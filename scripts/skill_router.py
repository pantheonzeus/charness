#!/usr/bin/env python3
"""Skill preselector: the top few INDEX.md rows for one prompt, by keyword match (G5).

Why: with 143+ skills, letting the model pick from the whole registry loses recall (implicit routing
53% at +100 skills, 27% of prompts load nothing; explicit preselection of <= 5 holds up:
arXiv:2610.18522). And the full INDEX (95 KB) exceeds the 10,000-character cap on hook context, so
SessionStart gets a compact slug list (`compact`) and every prompt gets the likely rows (`hook`).

Deterministic, no model, stdlib only: BM25 over each row's triggers (weight 3), name and slug (2),
description (1) and the SKILL.md body (2: bodies carry routing cues descriptions miss, arXiv:2603.22455),
plus a bonus when a whole trigger phrase or the skill's slug appears in the prompt.
Stays quiet unless something backs the match: a prompt that names a skill gets that skill only; otherwise
the top row must share >= MIN_TERMS distinct prompt words with its INDEX row (the body never counts) or
match a whole trigger phrase, and so must every row shown. One generic word ("proposal", "post") is
noise, not a route; on 938 real prompts the old rule injected on 97% at 4.4 rows each.

The same match also delivers memory bodies (`memories`): the memory files' name and description go
through the same BM25 and floor, and the top 2 bodies follow the skill rows. SessionStart injects only
the MEMORY.md index, and models rarely open a file on their own (arXiv:2607.20972). Interactive prompts
only: a headless launch prompt ("Read and follow resources/skills/…, a repo skill") clears the floor on
its boilerplate words, so jobs (CBRAIN_JOB set by run_agent.sh) get no bodies.

  python3 scripts/skill_router.py hook                 UserPromptSubmit hook (JSON on stdin)
  python3 scripts/skill_router.py compact              SessionStart: category → slugs, < 10 K chars
  python3 scripts/skill_router.py route "<prompt>"     print the top rows with scores
  python3 scripts/skill_router.py eval [routing.tsv]   recall@5 on the golden set + quiet rate on `none`
  python3 scripts/skill_router.py memory-eval [memory.tsv]   right body on topic prompts + quiet rate on `none`
"""
import csv
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "resources" / "skills"
INDEX = SKILLS / "INDEX.md"
GOLDEN = SKILLS / "_evals" / "routing.tsv"
MEMORY_GOLDEN = SKILLS / "_evals" / "memory.tsv"
# The dir the SessionStart hook reads (.claude/settings.json).
MEMORY_DIR = Path.home() / ".claude" / "projects" / (os.environ.get("CLAUDE_PROJECT_DIR") or str(REPO)).replace("/", "-") / "memory"
MEMORY_K = 2
MEMORY_CAP = 1500    # characters per body
TOP_K = 5
MIN_SCORE = 6.0      # below this the best match is noise: inject nothing
KEEP_RATIO = 0.35    # rows scoring under this share of the best one are dropped
MIN_TERMS = 2        # distinct prompt words a row's INDEX fields must share, absent a phrase or slug hit
WEIGHTS = {"triggers": 3.0, "name": 2.0, "slug": 2.0, "description": 1.0, "body": 2.0}
# Harness text wrapped around the person's words: reminders, and the console's meeting context block.
SYSTEM_TEXT = re.compile(r"<system-reminder>.*?</system-reminder>|<context refreshed[^>]*>.*?</context>", re.S)
STOP = set("""a an and are as at be by can do for from have how i if in into is it its me my of on or our please
should so that the their them then there these this to us we what when where which who why will with you your
der die das und ist ein eine einen einem einer zu mit für von auf im in den dem des ich du er sie es wir ihr
mir mich dir dich bitte auch noch nur nicht wie was wo wer""".split())
# Conversational control words: a reply like "yes go ahead" or "skip" is steering, not a task.
CONTROL = set("""yes yeah yep ok okay go ahead sure thanks thank skip continue next done proceed fine good great cool
perfect right correct no nope ja nein weiter mach danke gut genau passt los""".split())


def tokens(text):
    out = []
    for t in re.findall(r"[0-9a-zäöüß]+", text.lower()):
        if t in STOP or t in CONTROL or len(t) < 2:
            continue
        out.append(t[:-1] if len(t) > 4 and t.endswith("s") else t)
    return out


def load_index():
    rows, category = [], ""
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            category = line[3:].strip()
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or not cells[-1].startswith("`") or cells[0] in ("Skill", "---"):
            continue
        path = cells[-1].strip("`")
        rows.append({"name": cells[0], "triggers": cells[1], "description": " | ".join(cells[2:-1]),
                     "path": path, "category": category,
                     "slug": path.rsplit("/SKILL.md", 1)[0].split("/")[-1], "body": body(path)})
    return rows


def body(path):
    """The skill file without its frontmatter (triggers and description are scored from INDEX already)."""
    try:
        text = (SKILLS / path).read_text(encoding="utf-8")
    except OSError:
        return ""
    return re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)


def build(rows):
    fields = {}
    for f in WEIGHTS:
        docs = [tokens(r[f] if f != "slug" else r["slug"].replace("-", " ")) for r in rows]
        df = Counter(t for d in docs for t in set(d))
        avg = sum(map(len, docs)) / max(len(docs), 1) or 1
        fields[f] = (docs, df, avg)
    return fields


def score(prompt, rows, fields):
    q = tokens(prompt)
    low = prompt.lower()
    n = len(rows)
    scores = []
    for i, r in enumerate(rows):
        s = 0.0
        for f, w in WEIGHTS.items():
            docs, df, avg = fields[f]
            tf = Counter(docs[i])
            dl = len(docs[i])
            for t in set(q):
                if t in tf:
                    idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
                    s += w * idf * tf[t] * 2.2 / (tf[t] + 1.2 * (0.25 + 0.75 * dl / avg))
        phrases = [p.strip().lower() for p in r["triggers"].split(",") if " " in p.strip()]
        s += 4.0 * sum(1 for p in phrases if p in low)
        if r["slug"] in low or r["path"].rsplit("/SKILL.md", 1)[0] in low:
            s += 25.0
        scores.append(s)
    return scores


def backing(prompt, i, rows, fields):
    """What backs row i: distinct prompt words its INDEX fields share (not the body), a whole trigger
    phrase in the prompt, and whether the prompt names the skill outright."""
    r, low = rows[i], prompt.lower()
    shared = set(tokens(prompt)) & {t for f in WEIGHTS if f != "body" for t in fields[f][0][i]}
    phrase = any(" " in p and p.strip().lower() in low for p in r["triggers"].split(","))
    named = r["slug"] in low or r["path"].rsplit("/SKILL.md", 1)[0] in low
    return len(shared), phrase, named


def route(prompt, k=TOP_K, rows=None, fields=None):
    rows = rows or load_index()
    fields = fields or build(rows)
    prompt = SYSTEM_TEXT.sub("", prompt)
    scores = score(prompt, rows, fields)
    ranked = sorted(range(len(rows)), key=lambda i: -scores[i])[:k]
    if not ranked or scores[ranked[0]] < MIN_SCORE:
        return []
    shown = {i: backing(prompt, i, rows, fields) for i in ranked if scores[i] >= KEEP_RATIO * scores[ranked[0]]}
    named = [i for i, b in shown.items() if b[2]]
    if named:   # the prompt names its skill (headless jobs, "run slack-intel"): that one, nothing else
        return [(scores[i], rows[i]) for i in named]
    terms, phrase, _ = shown[ranked[0]]
    if len(tokens(prompt)) < 2 or (terms < MIN_TERMS and not phrase):
        return []
    return [(scores[i], rows[i]) for i, b in shown.items() if b[0] >= MIN_TERMS or b[1]]


def render(hits):
    lines = ["### Likely skills for this prompt — preselected from resources/skills/INDEX.md by keyword match",
             "Open the matching SKILL.md before acting. None fits? Grep INDEX.md before saying a skill doesn't exist.", ""]
    for _, r in hits:
        trig = r["triggers"] if len(r["triggers"]) <= 220 else r["triggers"][:217] + "…"
        desc = r["description"] if len(r["description"]) <= 420 else r["description"][:417] + "…"
        lines.append(f"- **{r['name']}** — `resources/skills/{r['path']}`\n  triggers: {trig}\n  {desc}")
    return "\n".join(lines)


def front(head, key):
    m = re.search(rf"^{key}:\s*(.+)$", head, re.M)
    return m.group(1).strip().strip('"') if m else ""


def load_memories():
    """Memory files as rows route() can score: name and description only, `text` is what gets delivered."""
    rows = []
    for p in sorted(MEMORY_DIR.glob("*.md")):
        if p.name == "MEMORY.md":
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, ValueError):
            continue
        m = re.match(r"---\n(.*?)\n---\n", text, re.S)
        head, rest = (m.group(1), text[m.end():]) if m else ("", text)
        rows.append({"name": front(head, "name") or p.stem, "triggers": "", "description": front(head, "description"),
                     "path": p.stem, "slug": p.stem, "body": "", "text": rest.strip()})
    return rows


def memories(prompt):
    rows = load_memories()
    return [r for _, r in route(prompt, k=MEMORY_K, rows=rows)] if rows else []


def render_memories(mems):
    lines = ["### Memories for this prompt — matched by keyword from the memory dir",
             "Point-in-time notes, not live state: verify before asserting anything in them as fact.", ""]
    for r in mems:
        t = r["text"] if len(r["text"]) <= MEMORY_CAP else r["text"][:MEMORY_CAP - 1] + "…"
        lines.append(f"#### {r['slug']}\n{t}\n")
    return "\n".join(lines).rstrip()


def compact():
    rows = load_index()
    by_cat = {}
    for r in rows:
        by_cat.setdefault(r["category"], []).append(r["slug"])
    out = [f"### Repo skill registry — {sum(r['path'].endswith('/SKILL.md') for r in rows)} skills, compact. Full rows (triggers, descriptions): "
           "resources/skills/INDEX.md. Each prompt also gets its likely skills preselected (UserPromptSubmit). "
           "Before acting on OR declining a task, open the matching resources/skills/<category>/<slug>/SKILL.md; "
           "Grep INDEX.md when nothing listed fits. This is separate from the harness skill list.", ""]
    for cat, slugs in by_cat.items():
        out.append(f"**{cat}:** " + ", ".join(slugs))
    return "\n".join(out)


def hook():
    try:
        prompt = json.loads(sys.stdin.read() or "{}").get("prompt", "")
    except ValueError:
        return 0
    # System events arrive through the same hook (task notifications, reminders): they are not the
    # person's prompt, so stay quiet on notifications; route() strips reminder and context blocks.
    if "<task-notification>" in prompt or "SYSTEM NOTIFICATION" in prompt:
        return 0
    hits = route(prompt) if prompt.strip() else []
    mems = memories(prompt) if prompt.strip() and not os.environ.get("CBRAIN_JOB") else []
    parts = ([render(hits)] if hits else []) + ([render_memories(mems)] if mems else [])
    if parts:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                                                 "additionalContext": "\n\n".join(parts)[:9500]}}))
    return 0


def evaluate(path):
    rows, golden = load_index(), list(csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"))
    fields = build(rows)
    res = {}
    for g in golden:
        exp = {e.strip().removesuffix("/SKILL.md").removesuffix(".md") for e in g["expected"].split("|")}
        got = [r["path"].removesuffix("/SKILL.md").removesuffix(".md") for _, r in route(g["prompt"], rows=rows, fields=fields)]
        split = g.get("split", "all")
        bucket = res.setdefault(split, {"hit": 0, "n": 0, "quiet": 0, "none": 0})
        if exp == {"none"}:
            bucket["none"] += 1
            bucket["quiet"] += not got
        else:
            bucket["n"] += 1
            ok = bool(exp & set(got)) or ("none" in exp and not got)   # "none" acceptable: silence is a hit
            bucket["hit"] += ok
            if not ok:
                print(f"MISS {g['id']} expected {'|'.join(sorted(exp))} got {got[:3]}  — {g['prompt'][:70]}")
    print("  ".join(f"{s}: recall@{TOP_K}={b['hit']}/{b['n']} quiet-on-none={b['quiet']}/{b['none']}"
                    for s, b in sorted(res.items())))
    return 0


def evaluate_memory(path):
    hit = n = quiet = none = peak = 0
    for g in csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"):
        mems = memories(g["prompt"])
        got = [r["slug"] for r in mems]
        peak = max(peak, len(render_memories(mems)) if mems else 0)
        if g["expected"] == "none":
            none += 1
            quiet += not got
            if got:
                print(f"NOISE {g['id']} got {got}  — {g['prompt'][:70]}")
        else:
            n += 1
            hit += g["expected"] in got
            if g["expected"] not in got:
                print(f"MISS {g['id']} expected {g['expected']} got {got}  — {g['prompt'][:70]}")
    print(f"right body={hit}/{n} quiet-on-none={quiet}/{none} peak-added={peak} chars")
    return 0


def main(argv):
    cmd = argv[0] if argv else ""
    if cmd == "hook":
        return hook()
    if cmd == "compact":
        print(compact())
        return 0
    if cmd == "route" and len(argv) > 1:
        for s, r in route(" ".join(argv[1:])):
            print(f"{s:6.1f}  {r['path']}")
        return 0
    if cmd == "eval":
        return evaluate(argv[1] if len(argv) > 1 else GOLDEN)
    if cmd == "memory-eval":
        return evaluate_memory(argv[1] if len(argv) > 1 else MEMORY_GOLDEN)
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
