#!/usr/bin/env python3
"""Skill-routing eval — the metric for the INDEX trigger loop (_shared/autoresearch-loop.md).

Gives a headless model ONLY the INDEX.md text plus a frozen golden set of real past prompts and
asks it to dispatch each one to a Path (or `none`). Scores exact membership in the row's
acceptable set (`expected` column, `|`-separated). The model is the dispatcher being measured,
not a judge: labels are fixed, the score is mechanical.

Golden set (gitignored — real prompts carry client names): resources/skills/_evals/routing.tsv
  columns: id  split(train|heldout)  expected  prompt

Usage:
  python3 routing_eval.py [--index PATH] [--data PATH] [--model opus] [--log RESULTS_TSV] [--note TEXT]
Prints per-miss lines, then `train=<a>/<n> heldout=<b>/<m> index_chars=<c>` as the last line.
One headless call per run (all prompts batched). Runs from a temp dir with no tools, so project
hooks and CLAUDE.md never reach the dispatcher.
"""
import argparse, csv, datetime, json, pathlib, re, subprocess, sys, tempfile

SKILLS = pathlib.Path(__file__).resolve().parents[3]
ap = argparse.ArgumentParser()
ap.add_argument("--index", default=str(SKILLS / "INDEX.md"))
ap.add_argument("--data", default=str(SKILLS / "_evals" / "routing.tsv"))
ap.add_argument("--model", default="opus")
ap.add_argument("--log", help="append one result row to this TSV")
ap.add_argument("--note", default="", help="hypothesis/description for the log row")
a = ap.parse_args()

index = pathlib.Path(a.index).read_text(encoding="utf-8")
rows = list(csv.DictReader(open(a.data, encoding="utf-8"), delimiter="\t"))

numbered = "\n".join(f"{i}. {r['prompt']}" for i, r in enumerate(rows, 1))
prompt = f"""You are the skill dispatcher for an agent workspace. Below is the registry INDEX.md.
For each numbered user request, choose the single best entry from the registry's Path column
(write it without the trailing `/SKILL.md` or `.md`, e.g. `sales/proposal-challenger` or
`_shared/autoresearch-loop`), or `none` if no registry entry should be opened for it.
Answer with ONLY a JSON object mapping each request number (as a string) to its choice.

<registry>
{index}
</registry>

<requests>
{numbered}
</requests>"""

with tempfile.TemporaryDirectory() as tmp:
    out = subprocess.run(
        ["claude", "-p", "--setting-sources", "user", "--tools", "", "--no-session-persistence",
         "--model", a.model],
        input=prompt, capture_output=True, text=True, cwd=tmp, timeout=600)
m = re.search(r"\{.*\}", out.stdout, re.S)
if not m:
    sys.exit(f"no JSON in dispatcher output:\n{out.stdout[:500]}\n{out.stderr[:500]}")
picks = json.loads(m.group(0))

def norm(p):
    p = str(p).strip().strip("`").removesuffix("/SKILL.md").removesuffix(".md")
    return p.removeprefix("resources/skills/")

score = {"train": [0, 0], "heldout": [0, 0]}
for i, r in enumerate(rows, 1):
    got = norm(picks.get(str(i), "none"))
    ok = got in r["expected"].split("|")
    score[r["split"]][0] += ok
    score[r["split"]][1] += 1
    if not ok:
        print(f"MISS {r['id']} [{r['split']}] expected={r['expected']} got={got}")

line = (f"train={score['train'][0]}/{score['train'][1]} "
        f"heldout={score['heldout'][0]}/{score['heldout'][1]} index_chars={len(index)}")
print(line)
if a.log:
    log = pathlib.Path(a.log)
    new = not log.exists()
    with log.open("a") as f:
        if new:
            f.write("timestamp\ttrain\theldout\tindex_chars\tmodel\tnote\n")
        f.write(f"{datetime.datetime.now().isoformat(timespec='seconds')}\t{score['train'][0]}/{score['train'][1]}\t"
                f"{score['heldout'][0]}/{score['heldout'][1]}\t{len(index)}\t{a.model}\t{a.note}\n")
