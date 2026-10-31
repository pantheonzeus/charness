#!/usr/bin/env python3
"""Weekly vault ratchet — measure, trend, alarm (_shared/autoresearch-loop.md). Edits no notes.

1. Runs link_audit.py (refreshes audit.json).
2. Counts missing link targets per category (skill-ref / output-ref / memory-ref point outside the
   vault and are generator-fixable; person/org and concept/topic need a stub or a re-link).
3. Runs the recall benchmark (progressive-disclosure/scripts/recall_bench.py) as the guard.
4. Appends one row to the results TSV and compares with the previous row:
   RATCHET=HOLD     no category grew and recall PASS
   RATCHET=REGRESS  any category grew, or recall FAIL — the lines above say which

Why no auto-fix: the only add-only fix (adding `aliases:` to the target note) makes link_audit
count a link as resolved, but Obsidian's docs do not confirm a raw [[Alias]] resolves — that
would raise the score without repairing the graph. Stub creation needs the principal's approval.

Usage: python3 ratchet.py [--log PATH]   (default log: output/vault-ratchet/results.tsv)
Exit 0 on HOLD, 1 on REGRESS.
"""
import argparse, datetime, importlib.util, io, json, pathlib, subprocess, sys
from collections import Counter
from contextlib import redirect_stdout

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[4]
ap = argparse.ArgumentParser()
ap.add_argument("--log", default=str(REPO / "output" / "vault-ratchet" / "results.tsv"))
a = ap.parse_args()

spec = importlib.util.spec_from_file_location("link_audit", HERE / "link_audit.py")
la = importlib.util.module_from_spec(spec)
sys.argv = [str(HERE / "link_audit.py"), str(REPO / "cbrain")]
with redirect_stdout(io.StringIO()):
    spec.loader.exec_module(la)
audit = json.load(open(HERE / "audit.json"))

# Categorise by what the target actually is — link_audit's bucket() lumps ~all of them together.
SKILL_IDS = {q.parent.name for q in (REPO / "resources/skills").glob("*/*/SKILL.md")}
OUTPUT_STEMS = {q.stem for q in (REPO / "output").rglob("*") if q.is_file() and ".runs" not in q.parts}
MEMORY_STEMS = {q.stem for q in (pathlib.Path.home() / ".claude/projects" /
                str(REPO).replace("/", "-") / "memory").glob("*.md")}
import re
def category(t):
    if t in SKILL_IDS: return "skill-ref"
    if t in MEMORY_STEMS: return "memory-ref"
    if t in OUTPUT_STEMS: return "output-ref"
    if re.fullmatch(r"\d{8}.*", t): return "meeting/daily"
    if re.fullmatch(r"[A-ZÄÖÜ][\w'’.-]+(,)?( [A-ZÄÖÜ][\w'’.-]+){1,3}", t) and not t.isupper(): return "person/org"
    return "concept/topic"
cats = Counter(category(t) for t in audit["missing_targets"])
recall = subprocess.run([sys.executable, str(REPO / "resources/skills/vault-hygiene/progressive-disclosure/scripts/recall_bench.py")],
                        capture_output=True, text=True)
recall_line = recall.stdout.strip().splitlines()[-1] if recall.stdout.strip() else "recall: no output"
recall_ok = recall.returncode == 0

CATS = ["skill-ref", "output-ref", "memory-ref", "meeting/daily", "person/org", "concept/topic"]
row = {"date": datetime.date.today().isoformat(),
       "missing_total": len(audit["missing_targets"]),
       **{c: cats.get(c, 0) for c in CATS},
       "broken_files": len(audit["broken"]), "orphans": len(audit["orphans"]),
       "recall": "PASS" if recall_ok else "FAIL"}

log = pathlib.Path(a.log)
log.parent.mkdir(parents=True, exist_ok=True)
prev = None
if log.exists():
    lines = log.read_text().strip().splitlines()
    if len(lines) > 1:
        prev = dict(zip(lines[0].split("\t"), lines[-1].split("\t")))
with log.open("a") as f:
    if prev is None and not (log.exists() and log.stat().st_size):
        f.write("\t".join(row) + "\n")
    f.write("\t".join(str(v) for v in row.values()) + "\n")

grew = [c for c in ["missing_total", *CATS] if prev and int(row[c]) > int(prev.get(c, 0))]
for c in grew:
    print(f"GREW {c}: {prev[c]} -> {row[c]}")
if not recall_ok:
    print(f"RECALL FAIL: {recall_line}")
print("  ".join(f"{k}={v}" for k, v in row.items()))
# Ingest provenance sweep (G2, scripts/ingest_lint.py): stamp new ingest notes, list instruction-shaped
# lines for a person to look at. Best effort; it never moves the ratchet verdict.
try:
    sweep = subprocess.run([sys.executable, str(REPO / "scripts" / "ingest_lint.py"), "sweep"],
                           capture_output=True, text=True, timeout=300)
    print(sweep.stdout.strip())
except (OSError, subprocess.SubprocessError) as e:
    print(f"ingest sweep failed: {e}")
verdict = "REGRESS" if grew or not recall_ok else "HOLD"
print(f"RATCHET={verdict}")
sys.exit(0 if verdict == "HOLD" else 1)
