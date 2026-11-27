#!/usr/bin/env python3
"""Delegation packet lint: constraints travel verbatim and come back checked.

Handoff summaries keep facts and drop rules: in arXiv 2608.24569 (2026-08) summarised handoffs
switched off workflow blockers in 76.7-97.2% of cases, and restoring the full blocker text took
forbidden actions from 85.2% to 0.0%. So a TASK.md carries its constraints as a `## Constraints`
list, copied verbatim from their source, and the child's RESPONSE.md answers each one under
`## Constraints checked`, line for line:

    - <the constraint, copied verbatim> — kept | not applicable | broken: <why>

Usage:
  packet_lint.py task <children/<id>>...   before launch: the packet has a Constraints block
  packet_lint.py check <children/<id>>...  before integrating: every constraint echoed, none broken
Exit 0 = clean, 1 = missing or malformed, 2 = a child reports a broken constraint.
Contract: resources/skills/_shared/delegation-handoff.md.
"""
import re
import sys
from pathlib import Path

VERDICT = re.compile(r"\s+(?:—|--)\s+(kept|not applicable|broken)\b(.*)$", re.I)


def section(text, heading):
    """Bullet lines (without '- ') under '## <heading>' up to the next '## '."""
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    if not m:
        return None
    return [re.sub(r"\s+", " ", ln.strip()[2:]).strip()
            for ln in m.group(1).splitlines() if ln.strip().startswith("- ")]


def lint(folder, mode):
    d = Path(folder)
    task = d / "TASK.md"
    if not task.is_file():
        return 1, [f"{task}: missing"]
    cons = section(task.read_text(encoding="utf-8"), "Constraints")
    if not cons:
        return 1, [f"{task}: no '## Constraints' list (copy write scopes, the confidentiality deny-list, budget and never-do lines verbatim)"]
    if mode == "task":
        return 0, [f"{task}: {len(cons)} constraints"]
    resp = d / "RESPONSE.md"
    if not resp.is_file():
        return 1, [f"{resp}: missing"]
    echoed = section(resp.read_text(encoding="utf-8"), "Constraints checked")
    if echoed is None:
        return 1, [f"{resp}: no '## Constraints checked' section"]
    verdicts = {}
    for line in echoed:
        m = VERDICT.search(line)
        if m:
            verdicts[line[:m.start()].strip()] = (m.group(1).lower(), m.group(2).strip(" :"))
    problems, rc = [], 0
    for c in cons:
        if c not in verdicts:
            problems.append(f"{resp}: constraint not echoed verbatim with a verdict: {c}")
            rc = max(rc, 1)
        elif verdicts[c][0] == "broken":
            problems.append(f"{resp}: BROKEN: {c} ({verdicts[c][1] or 'no reason given'})")
            rc = 2
    return rc, problems or [f"{resp}: {len(cons)} constraints echoed, none broken"]


def main(argv):
    if len(argv) < 3 or argv[1] not in ("task", "check"):
        print(__doc__.strip().split("\n\n")[-1], file=sys.stderr)
        return 1
    rc = 0
    for folder in argv[2:]:
        r, msgs = lint(folder, argv[1])
        print("\n".join(msgs))
        rc = max(rc, r)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
