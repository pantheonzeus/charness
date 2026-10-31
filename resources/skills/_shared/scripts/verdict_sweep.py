#!/usr/bin/env python3
"""Verdict sweep — closes the change-manifest loop (_shared/change-manifest.md, autoresearch-loop.md).

For every CHANGE_LOG.md entry whose verdict is still `pending`:
  1. find what it touched — skill ids and `_shared/` module names named in its **Files touched** line;
  2. find later evidence in STATE_ROOTs under output/.runs/ dated after the entry:
       strong — the name appears in the first 8 lines of the run's RESPONSE.md (the spine header,
                where an executing run names its skill);
       weak   — the name appears only further down, or in EVIDENCE.md / children/* (often an audit
                or a planning run that merely talks about the skill);
  3. print a worklist: READY (strong evidence — judge it now), MENTIONED (weak only — read before
     judging, may be no real use), NO-USE-YET (nothing).
Read-only. The verdict itself is a judgement written by hand into CHANGE_LOG.md
(`confirmed` / `not confirmed` / `regressed` / `partial`, dated, with one line of proof).

Metric (lower is better): pending_over_14d. Last line:
  `entries=<n> pending=<p> pending_over_14d=<o> ready=<r> mentioned=<m>`
Usage: python3 verdict_sweep.py [--log RESULTS_TSV] [--max N]   (--max limits READY lines printed; default 5)
"""
import argparse, datetime, pathlib, re

SKILLS = pathlib.Path(__file__).resolve().parents[2]
REPO = SKILLS.parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--log")
ap.add_argument("--max", type=int, default=5)
a = ap.parse_args()

text = (SKILLS / "_shared" / "CHANGE_LOG.md").read_text(encoding="utf-8")
entries = re.split(r"^(?=## \d{4}-\d{2}-\d{2})", text, flags=re.M)[1:]
skill_ids = {p.parent.name for p in SKILLS.glob("*/*/SKILL.md") if not p.parts[-3].startswith("_")}
modules = {p.stem for p in (SKILLS / "_shared").glob("*.md") if p.stem != "CHANGE_LOG"}
runs = sorted(d for d in (REPO / "output" / ".runs").iterdir() if d.is_dir() and re.match(r"\d{8}", d.name))
today = datetime.date.today()


def run_text(d):
    """(header, full) text of a run: header = first 8 lines of RESPONSE.md."""
    files = [d / "RESPONSE.md", d / "EVIDENCE.md", *d.glob("children/*/TASK.md"), *d.glob("children/*/RESPONSE.md")]
    full = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in files if f.exists())
    resp = d / "RESPONSE.md"
    header = "\n".join(resp.read_text(encoding="utf-8", errors="replace").splitlines()[:8]) if resp.exists() else ""
    return header, full


def named(n, t):
    return re.search(rf"(?<![\w-]){re.escape(n)}(?![\w-])", t)


cache = {}
pending = over14 = ready = mentioned = 0
rows = []
for e in entries:
    head = e.splitlines()[0]
    date = datetime.date.fromisoformat(head[3:13])
    verdict = re.search(r"^- \*\*Verdict:\*\*\s*(.*)$", e, re.M)
    status = verdict.group(1).strip("* ").lower() if verdict else "missing"
    if not (status.startswith("pending") or status == "missing"):
        continue
    pending += 1
    age = (today - date).days
    over14 += age > 14
    touched_line = re.search(r"^- \*\*Files touched:\*\*(.*?)(?=^- \*\*|\Z)", e, re.M | re.S)
    touched_text = touched_line.group(1) if touched_line else e
    # a touched name counts only when written as a path, in backticks, or as a [[link]] —
    # so the skill id `recall` is not matched by the phrase "register recall"
    names = sorted({n for n in skill_ids | modules
                    if re.search(rf"(?:[/`]|\[\[){re.escape(n)}(?:[/`.]|\]\])", touched_text)})
    hits = []
    for d in runs:
        if datetime.date(int(d.name[:4]), int(d.name[4:6]), int(d.name[6:8])) <= date:
            continue
        header, full = cache.setdefault(d, run_text(d))
        strong = [n for n in names if named(n, header)]
        weak = [n for n in names if n not in strong and named(n, full)]
        if strong or weak:
            hits.append((d.name, strong, weak))
    if any(h[1] for h in hits):
        state = "READY"; ready += 1
        hits = [h for h in hits if h[1]] + [h for h in hits if not h[1]]
    elif hits:
        state = "MENTIONED"; mentioned += 1
    else:
        state = "NO-USE-YET"
    rows.append((state, age, head[3:], names, hits))

ORDER = {"READY": 0, "MENTIONED": 1, "NO-USE-YET": 2}
for state, age, title, names, hits in sorted(rows, key=lambda r: (ORDER[r[0]], -r[1])):
    print(f"{state:10} {age:3}d  {title[:90]}")
    print(f"           touched: {', '.join(names) or '(no skill/module named)'}")
    for name, strong, weak in hits[:a.max]:
        tag = f"strong: {', '.join(strong)}" if strong else f"weak: {', '.join(weak)}"
        print(f"           evidence: output/.runs/{name}  ({tag})")
    if len(hits) > a.max:
        print(f"           … {len(hits) - a.max} more runs")
line = f"entries={len(entries)} pending={pending} pending_over_14d={over14} ready={ready} mentioned={mentioned}"
print(line)
if a.log:
    log = pathlib.Path(a.log)
    new = not log.exists()
    with log.open("a") as f:
        if new:
            f.write("date\tentries\tpending\tpending_over_14d\tready\tmentioned\n")
        f.write(f"{today}\t{len(entries)}\t{pending}\t{over14}\t{ready}\t{mentioned}\n")
