#!/usr/bin/env python3
"""Deterministic gate for the living-plan skill.

  plan.py check <output/tasks/<id>/PLAN.json>   prints OK or the problems (exit 1)

The console renders PLAN.json live and lets the user edit it while the agent is paused, so a
malformed file breaks the shared document for both. Checked: shape, owners, step states,
checkpoints with stated stakes, findings with a confidence level and sources, receipts.
"""
import json
import re
import sys
from pathlib import Path

OWNERS = {"you", "cos", "analyst", "researcher"}
STATES = {"pending", "active", "done", "skipped", "waiting"}
CONFIDENCE = {"verified", "likely", "unsure"}


def check(path):
    try:
        p = json.loads(Path(path).read_text())
    except (OSError, ValueError) as e:
        return [f"cannot read JSON: {e}"]
    errs = []
    if not str(p.get("outcome", "")).strip():
        errs.append("missing outcome")
    d = p.get("deliverable") or {}
    if not d.get("shape") or not str(d.get("path", "")).startswith("output/plans/"):
        errs.append("deliverable needs shape and a path under output/plans/")
    if not isinstance((p.get("estimate") or {}).get("minutes"), (int, float)):
        errs.append("estimate.minutes must be a number")
    steps = p.get("steps") or []
    if not 1 <= len(steps) <= 12:
        errs.append(f"{len(steps)} steps; keep 1–12")
    ids, active = set(), 0
    for s in steps:
        sid = s.get("id", "?")
        if not re.fullmatch(r"s\d+", str(sid)) or sid in ids:
            errs.append(f"step id {sid!r} must be unique and look like s<n>")
        ids.add(sid)
        if not str(s.get("title", "")).strip():
            errs.append(f"{sid}: missing title")
        if s.get("owner") not in OWNERS:
            errs.append(f"{sid}: owner must be one of {sorted(OWNERS)}")
        if s.get("status") not in STATES:
            errs.append(f"{sid}: status must be one of {sorted(STATES)}")
        active += s.get("status") == "active"
        cp = s.get("checkpoint")
        if cp is not None and not (isinstance(cp, dict) and cp.get("stakes") and cp.get("question")):
            errs.append(f"{sid}: a checkpoint needs stakes and a question (or null)")
        for f in s.get("findings") or []:
            if f.get("confidence") not in CONFIDENCE:
                errs.append(f"{sid}: finding confidence must be one of {sorted(CONFIDENCE)}")
            elif f["confidence"] == "verified" and not f.get("sources"):
                errs.append(f"{sid}: a verified finding needs at least one source")
            if not str(f.get("text", "")).strip():
                errs.append(f"{sid}: empty finding")
    if active > 1:
        errs.append(f"{active} steps are active; at most one")
    for x in p.get("interrogation") or []:
        if not (isinstance(x, dict) and str(x.get("q", "")).strip() and isinstance(x.get("a", ""), str)):
            errs.append(f"interrogation entry {x!r} needs q and a (a may be empty if skipped)")
    for r in p.get("receipts") or []:
        if not (r.get("kind") and r.get("ref") and r.get("label")):
            errs.append(f"receipt {r!r} needs kind, ref and label")
    return errs


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "check":
        print(__doc__)
        sys.exit(64)
    errs = check(sys.argv[2])
    print("OK" if not errs else "\n".join("FAIL: " + e for e in errs))
    sys.exit(1 if errs else 0)
