#!/usr/bin/env python3
"""Vault recall benchmark — a STANDING GUARD, not an optimization target (_shared/autoresearch-loop.md).

Promoted from the July 2026 one-off (autoresearch/improve-260706-1528/bench_token_efficiency.py).
For each question it simulates progressive-disclosure retrieval:
  compressed path = read the index/MOC note, keep the lines containing the keyword, drill ONLY
                    into the [[wikilinks]] on those lines.
  naive path      = read every note in the question's folder.
A question passes when every expected fact (case-insensitive substring) appears in the compressed
path — i.e. the index still routes to the notes that hold the answer.

Optional `kind` column (empty = answer). All checks are deterministic: they test the vault, not a model.
  answer      every fact is on the compressed path (the default above).
  abstain     no note under `folder` holds any fact: a question the brain must answer "I don't know" to.
              Use folder `.` for the whole vault.
  permission  no note under `folder` holds any fact: confidential facts stay out of a folder that other
              readers see (e.g. client pricing out of notes/LinkedIn-Posts).
  conflict    facts = winner|loser. Both are on the compressed path (the contradiction stays visible) and
              the winner sits in a note with a `confirmed:` frontmatter line (the confirmed source wins).

Gate: PASS iff every row passes. Token ratio (words, compressed/naive) is reported for answer rows only.

Golden set (gitignored — facts are client data): resources/skills/_evals/recall.tsv
  columns: id  index  folder  keyword  facts(|-separated)  question  [kind]

Usage: python3 recall_bench.py [--vault cbrain] [--data PATH] [--log RESULTS_TSV] [--note TEXT]
Last line: `facts=<found>/<total> median_ratio=<r> VERDICT=PASS|FAIL`. Exit 0 iff PASS.
"""
import argparse, csv, datetime, pathlib, re, statistics, sys

SKILLS = pathlib.Path(__file__).resolve().parents[3]
ap = argparse.ArgumentParser()
ap.add_argument("--vault", default=str(SKILLS.parents[1] / "cbrain"))
ap.add_argument("--data", default=str(SKILLS / "_evals" / "recall.tsv"))
ap.add_argument("--log")
ap.add_argument("--note", default="")
a = ap.parse_args()
VAULT = pathlib.Path(a.vault)


def words(t): return len(t.split())


def compressed(index_rel, keyword):
    """Return (cost_words, evidence_text, drilled). Cost counts the whole index read; evidence is only the
    matched lines + drilled notes, so a fact sitting in some other index row cannot mask a broken route.
    drilled = [(note text)] for each note reached, so a conflict row can see which note holds which fact."""
    idx = (VAULT / index_rel).read_text(encoding="utf-8")
    text, seen, drilled = "", set(), []
    for line in idx.splitlines():
        if keyword.lower() not in line.lower():
            continue
        text += line + "\n"
        for tgt in re.findall(r"\[\[([^\]]+?)\]\]", line):
            stem = re.split(r"\\?[|#]", tgt)[0].strip()
            if stem in seen:
                continue
            seen.add(stem)
            hits = list(VAULT.rglob(f"{stem}.md"))
            if hits:
                drilled.append(hits[0].read_text(encoding="utf-8"))
                text += "\n" + drilled[-1]
    return words(idx) + words(text), text, drilled


def confirmed(note):
    return note.startswith("---\n") and re.search(r"^confirmed:\s*\S", note[:note.find("\n---", 4)], re.M)


rows = list(csv.DictReader(open(a.data, encoding="utf-8"), delimiter="\t"))
found_total = facts_total = 0
ratios = []
kinds = {}   # kind -> [passed, total]
for r in rows:
    kind = (r.get("kind") or "answer").strip()
    facts = r["facts"].split("|")
    kinds.setdefault(kind, [0, 0])[1] += 1
    if kind in ("abstain", "permission"):
        leaks = [f for f in facts for p in (VAULT / r["folder"]).rglob("*.md")
                 if f.lower() in p.read_text(encoding="utf-8", errors="ignore").lower()]
        if leaks:
            print(f"{'ANSWERABLE' if kind == 'abstain' else 'LEAK'} {r['id']} ({r['question']}): {sorted(set(leaks))}")
        kinds[kind][0] += not leaks
        continue
    cost, comp, drilled = compressed(r["index"], r["keyword"])
    miss = [f for f in facts if f.lower() not in comp.lower()]
    if miss:
        print(f"MISS {r['id']} ({r['question']}): {miss}")
    elif kind == "conflict" and not any(confirmed(n) and facts[0].lower() in n.lower() for n in drilled):
        print(f"UNCONFIRMED {r['id']} ({r['question']}): winner {facts[0]!r} is in no confirmed note on the path")
        miss = [facts[0]]
    if kind == "answer":
        naive = sum(words(p.read_text(encoding="utf-8")) for p in (VAULT / r["folder"]).rglob("*.md"))
        ratios.append(cost / naive if naive else 0)
    elif kind != "conflict":
        print(f"UNKNOWN KIND {r['id']}: {kind!r}")
        miss = miss or ["<unknown kind>"]
    found_total += len(facts) - len(miss)
    facts_total += len(facts)
    kinds[kind][0] += not miss

median = statistics.median(ratios) if ratios else 0
verdict = "PASS" if all(p == t for p, t in kinds.values()) else "FAIL"
print(" ".join(f"{k}={p}/{t}" for k, (p, t) in sorted(kinds.items())))
print(f"facts={found_total}/{facts_total} median_ratio={median:.3f} VERDICT={verdict}")
if a.log:
    log = pathlib.Path(a.log)
    new = not log.exists()
    with log.open("a") as f:
        if new:
            f.write("timestamp\tfacts\tmedian_ratio\tverdict\tnote\n")
        f.write(f"{datetime.datetime.now().isoformat(timespec='seconds')}\t{found_total}/{facts_total}\t"
                f"{median:.3f}\t{verdict}\t{a.note}\n")
sys.exit(0 if verdict == "PASS" else 1)
