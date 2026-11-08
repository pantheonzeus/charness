# /// script
# requires-python = ">=3.10"
# ///
"""Idea engine: turn what's new in the vault into ideas worth the principal's time.

  run [--seed]       refresh the vault (new Claude sessions, deliverable/work index), then, if any
                     vault note changed since the last run, launch the idea-engine agent.
                     --seed mines the whole vault for 5 ideas of each type instead.
  check <STATE_ROOT> validate the ideas one run wrote
  status             JSON for the console

Four idea types: linkedin (a post topic, executive style, not a draft), learning, research, challenge
(a concept that challenges the status quo). An hourly run writes at most one per type, and only the
ones that add value. State lives in output/idea-engine/state.json; ideas live in cbrain/Ideas/.
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
REPO = SKILL.parents[3]
VAULT = REPO / "cbrain"
IDEAS = VAULT / "Ideas"
OUT = REPO / "output" / "idea-engine"
PODCASTS = REPO / "output" / "podcasts" / "ideas"   # podcast.py: two NotebookLM episodes per idea
STATE = OUT / "state.json"
LOCK = OUT / ".lock"
RUN_AGENT = REPO / "scripts" / "run_agent.sh"
INDEXER = REPO / "resources/skills/vault-hygiene/deliverable-index/scripts/index_deliverables.py"
SESSIONS = REPO / "resources/skills/workflow-ops/sync-claude-sessions/scripts/claude-sessions"
MOC_BUILDER = REPO / "resources/skills/vault-hygiene/progressive-disclosure/scripts/build_indexes.py"
PROJECTS = Path.home() / ".claude" / "projects"
TYPES = ("linkedin", "learning", "research", "challenge")
SKIP_PARTS = {"Ideas", "Bases", "MOCs", ".obsidian", ".trash"}   # own output and generated indexes never re-trigger it
MAX_CHANGED = 80
SEED_BUDGET = "6"   # the agent file's budget_usd (2) covers an hourly run; mining the whole vault needs more
CLI_ENV = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")}
REL = lambda p: str(Path(p).relative_to(REPO))
TOOLS = ["Read", "Glob", "Grep", "Write", "Edit", "WebSearch", "WebFetch", "Bash(date:*)", "Bash(ls:*)",
         f"Bash(uv run {REL(__file__)}:*)", f"Bash(uv run {__file__}:*)"]


def load(path, default):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    tmp.replace(path)


def log(msg):
    print(f"[{time.strftime('%F %T')}] {msg}", flush=True)


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return dict(re.findall(r"^(\w+):\s*\"?(.*?)\"?\s*$", m.group(1), re.M)) if m else {}


def refresh(since):
    """Bring the vault up to date before reading it: new interactive Claude sessions, then the index."""
    n = 0
    for d in PROJECTS.glob("-Users-*-GitHub-*"):
        for f in d.glob("*.jsonl"):
            if f.stat().st_mtime <= since or '"entrypoint":"claude-vscode"' not in f.read_text(errors="ignore")[:20000]:
                continue   # headless loop runs (sdk-cli) are not the principal's thinking
            r = subprocess.run(["uv", "run", "-q", "--python", "3.12", str(SESSIONS), "export", str(f)],
                               cwd=REPO, env={**CLI_ENV, "VAULT_DIR": str(VAULT)}, capture_output=True)
            n += r.returncode == 0
    subprocess.run([sys.executable, str(INDEXER)], cwd=REPO, capture_output=True)
    # People/Meetings MOCs: left un-run, they went stale for 3 months and every new person became an orphan.
    subprocess.run([sys.executable, str(MOC_BUILDER)], cwd=REPO, capture_output=True)
    return n


def changed_notes(since):
    out = []
    for f in VAULT.rglob("*.md"):
        if SKIP_PARTS & set(f.relative_to(VAULT).parts):
            continue
        m = f.stat().st_mtime
        if m > since:
            out.append((m, REL(f)))
    return [p for _, p in sorted(out, reverse=True)[:MAX_CHANGED]], len(out)


def check(root):
    root = Path(root)
    task, result = load(root / "TASK.json", None), load(root / "RESULT.json", None)
    if not task:
        return [f"no TASK.json in {root}"]
    if not result:
        return ["no RESULT.json: write {\"made\": [paths], \"skipped\": {type: reason}}"]
    errs, per = [], {t: 0 for t in TYPES}
    for f in IDEAS.glob("*.md"):
        text = f.read_text()
        fm = frontmatter(text)
        if fm.get("run") != task["run"]:
            continue
        t = fm.get("idea_type")
        if fm.get("type") != "idea" or t not in TYPES:
            errs.append(f"{f.name}: needs type: idea and idea_type one of {TYPES}")
            continue
        per[t] += 1
        for k in ("title", "value", "created"):
            if not fm.get(k):
                errs.append(f"{f.name}: frontmatter needs {k}")
        if fm.get("status") != "new":
            errs.append(f"{f.name}: status must start as new")
        for h in ("## The idea", "## Why now", "## Built from"):
            if h not in text:
                errs.append(f"{f.name}: missing section {h}")
        built = text.split("## Built from", 1)[-1]
        if "[[" not in built:
            errs.append(f"{f.name}: Built from needs ≥ 1 [[vault link]]")
        for link in re.findall(r"\[\[([^\]|#]+)", built):   # a path link must name an existing note
            if not ((VAULT / f"{link}.md").exists() or any(VAULT.rglob(f"{Path(link).name}.md"))):
                errs.append(f"{f.name}: Built from link [[{link}]] matches no vault note (paths start at the vault root)")
    for t in TYPES:
        if task["seed"] and per[t] != 5:
            errs.append(f"seed needs exactly 5 {t} ideas, found {per[t]}")
        if not task["seed"] and per[t] > 1:
            errs.append(f"an hourly run writes at most 1 {t} idea, found {per[t]}")
        if not task["seed"] and per[t] == 0 and not (result.get("skipped") or {}).get(t):
            errs.append(f"no {t} idea and no reason in RESULT.json skipped.{t}")
    return errs


def notify(title, message):
    subprocess.run(["osascript", "-e", f'display notification {json.dumps(message)} with title {json.dumps(title)}'],
                   capture_output=True)


def alive():
    try:
        os.kill(int(LOCK.read_text()), 0)
        return True
    except (OSError, ValueError):
        return False


def run(seed):
    if alive():
        return log("previous run still alive; skipping")
    OUT.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(str(os.getpid()))
    try:
        state = load(STATE, {"last_run": 0, "runs": []})
        started = time.time()
        sessions = refresh(state["last_run"] or started - 86400)
        changed, total = ([], 0) if seed else changed_notes(state["last_run"] or started - 3600)
        rec = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "seed": seed, "sessions_exported": sessions, "changed": total}
        if not seed and not changed:
            log("nothing changed in the vault; no run")
            state["last_run"] = started
            state["runs"] = (state["runs"] + [rec])[-300:]
            return save(STATE, state)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        root = REPO / "output" / ".runs" / f"{stamp}-idea-engine"
        root.mkdir(parents=True)
        recent = sorted(IDEAS.glob("*.md"), reverse=True)[:80]
        save(root / "TASK.json", {"run": stamp, "seed": seed, "changed": changed, "changed_total": total,
                                  "ideas_dir": REL(IDEAS), "earlier_ideas": [REL(f) for f in recent]})
        (root / "RESPONSE.md").write_text(f"# idea-engine {stamp}{' (seed)' if seed else ''}\n"
            "- [ ] read the changed notes (or mined the vault, on seed)\n- [ ] checked earlier ideas for repeats\n"
            "- [ ] ideas written (only the ones that add value)\n- [ ] RESULT.json written\n"
            "- [ ] ideas.py check prints OK\n")
        prompt = (f"Read and follow resources/skills/workflow-ops/idea-engine/SKILL.md (a repo skill: open it with Read, "
                  f"not the Skill tool) for the task packet {REL(root)}/TASK.json. Your STATE_ROOT is {REL(root)}/. "
                  f"Finish with `uv run {REL(__file__)} check {REL(root)}` printing OK.")
        extra = ["--max-budget-usd", SEED_BUDGET] if seed else []
        subprocess.run(["bash", str(RUN_AGENT), "idea-engine", str(root / "RESPONSE.md"), prompt,
                        "--permission-mode", "acceptEdits", *extra, "--allowedTools", *TOOLS],
                       cwd=REPO, env=CLI_ENV, stdin=subprocess.DEVNULL)
        errs = check(root)
        made = (load(root / "RESULT.json", {}) or {}).get("made") or []
        rec.update(ok=not errs, errors=errs[:5], made=len(made))
        log(f"{len(made)} idea(s); check {'OK' if not errs else 'FAILED: ' + '; '.join(errs[:3])}")
        if made:
            notify("Your team", f"{len(made)} new idea{'s' if len(made) > 1 else ''} worth a look")
        state = load(STATE, state)
        state["last_run"] = started    # changes during this run are picked up by the next one
        state["runs"] = (state["runs"] + [rec])[-300:]
        save(STATE, state)
    finally:
        LOCK.unlink(missing_ok=True)


def ideas():
    out = []
    for f in sorted(IDEAS.glob("*.md"), reverse=True):
        text = f.read_text(errors="ignore")
        fm = frontmatter(text)
        if fm.get("type") != "idea":
            continue
        body = re.search(r"^## The idea\n(.+?)(?:\n## |\Z)", text, re.M | re.S)
        qa = re.findall(r"^### Q \((.*?)\): (.+?)\n\n(.+?)(?=\n### |\n## |\Z)", text, re.M | re.S)
        out.append({"id": f.stem, "path": REL(f), "type": fm.get("idea_type", ""), "title": fm.get("title", f.stem),
                    "value": fm.get("value", ""), "status": fm.get("status", "new"), "created": fm.get("created", ""),
                    "idea": body.group(1).strip() if body else "", "tasks": [t for t in fm.get("tasks", "").strip("[]").replace(" ", "").split(",") if t],
                    "qa": [{"at": a, "q": q.strip(), "a": ans.strip()} for a, q, ans in qa],
                    "podcast": fm.get("podcast", ""),
                    "podcasts": [{"label": label, "url": f"/page/podcasts/ideas/{f.stem}-{kind}.m4a"}
                                 for kind, label in (("short", "Short: the central idea"), ("indepth", "In depth"))
                                 if (PODCASTS / f"{f.stem}-{kind}.m4a").is_file()],
                    "markdown": re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)})
    return out


def idea_file(iid):
    f = IDEAS / f"{iid}.md"
    if not re.fullmatch(r"[\w.-]+", iid) or not f.is_file():
        raise ValueError("unknown idea")
    return f


def set_status(iid, status):
    if status not in ("new", "acknowledged", "diving"):
        raise ValueError("unknown status")
    f = idea_file(iid)
    f.write_text(re.sub(r"^status:.*$", f"status: {status}", f.read_text(), count=1, flags=re.M))


def add_task(iid, tid):
    """Link a research task started from this idea (frontmatter `tasks: [..]`) and mark it diving."""
    f = idea_file(iid)
    text = f.read_text()
    fm = frontmatter(text)
    tasks = [t for t in fm.get("tasks", "").strip("[]").replace(" ", "").split(",") if t] + [tid]
    line = f"tasks: [{', '.join(tasks)}]"
    text = re.sub(r"^tasks:.*$", line, text, count=1, flags=re.M) if "tasks" in fm else text.replace("\ngenerated:", f"\n{line}\ngenerated:", 1)
    f.write_text(re.sub(r"^status:.*$", "status: diving", text, count=1, flags=re.M))


def set_field(iid, key, value):
    """Set one frontmatter field (added before `generated:` if missing): podcast state, notebook id."""
    f = idea_file(iid)
    text, line = f.read_text(), f"{key}: {value}"
    rx = re.compile(rf"^{key}:.*$", re.M)
    f.write_text(rx.sub(line, text, count=1) if key in frontmatter(text) else text.replace("\ngenerated:", f"\n{line}\ngenerated:", 1))


def append(iid, heading, entry):
    """Append an entry under a `## heading` section at the end of the note (created if missing)."""
    f = idea_file(iid)
    text = f.read_text().rstrip("\n")
    if f"\n## {heading}\n" not in text + "\n":
        text += f"\n\n## {heading}\n"
    parts = text.split(f"\n## {heading}\n", 1)
    rest = re.split(r"(?=\n## )", parts[1], maxsplit=1)
    f.write_text(parts[0] + f"\n## {heading}\n" + rest[0].rstrip("\n") + ("\n\n" if rest[0].strip() else "\n") + entry.strip() + "\n" + (rest[1] if len(rest) > 1 else ""))


def status():
    state = load(STATE, {"runs": []})
    return {"running": alive(), "last_run": (state["runs"] or [None])[-1], "ideas": ideas()}


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["run"]:
        run("--seed" in a)
    elif a[:1] == ["check"] and len(a) == 2:
        e = check(a[1])
        print("OK" if not e else "\n".join(e))
        sys.exit(1 if e else 0)
    elif a[:1] == ["status"]:
        print(json.dumps({k: v for k, v in status().items() if k != "ideas"} | {"ideas": len(ideas())}, indent=1))
    else:
        sys.exit(__doc__)
