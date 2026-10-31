#!/usr/bin/env python3
"""Stale-fact sweep for the memory dir (MEMORY.md index + one file per fact).

A memory is a claim that was true when written. This lists the ones to re-check:
  - expired:     metadata.valid_until is in the past
  - unverified:  no verification within the window (project 30 d; feedback, user, reference 180 d),
                 dated by metadata.last_verified, else metadata.modified, else the file's mtime
  - unindexed:   a memory file MEMORY.md does not list (it is never injected)
  - dangling:    a MEMORY.md line pointing at a file that does not exist

  python3 scripts/memory_sweep.py           full report
  python3 scripts/memory_sweep.py --brief   one line, or nothing when clean (the SessionStart hook)

Verifying a memory = re-checking the fact, then setting `last_verified: YYYY-MM-DD` under `metadata:`.
Stdlib only.
"""
import datetime as dt
import os
import re
import sys
from pathlib import Path

PROJECT = os.environ.get("CLAUDE_PROJECT_DIR") or str(Path(__file__).resolve().parent.parent)
MEMORY = Path.home() / ".claude" / "projects" / PROJECT.replace("/", "-") / "memory"
WINDOW = {"project": 30}
DEFAULT_WINDOW = 180


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    return dict(re.findall(r"^[ \t]*(\w+):[ \t]*\"?(.*?)\"?[ \t]*$", m.group(1), re.M)) if m else {}


def day(value):
    try:
        return dt.date.fromisoformat(value[:10])
    except (TypeError, ValueError):
        return None


def sweep(today=None):
    today = today or dt.date.today()
    index = (MEMORY / "MEMORY.md").read_text() if (MEMORY / "MEMORY.md").exists() else ""
    linked = set(re.findall(r"\]\(([^)]+\.md)\)", index))
    found = {"expired": [], "unverified": [], "unindexed": [], "dangling": sorted(l for l in linked if not (MEMORY / l).exists())}
    for f in sorted(MEMORY.glob("*.md")):
        if f.name == "MEMORY.md":
            continue
        fm = frontmatter(f.read_text())
        until = day(fm.get("valid_until", ""))
        if until and until < today:
            found["expired"].append(f"{f.name} (valid until {until})")
        checked = day(fm.get("last_verified", "")) or day(fm.get("modified", "")) or \
            dt.date.fromtimestamp(f.stat().st_mtime)
        window = WINDOW.get(fm.get("type", ""), DEFAULT_WINDOW)
        if (today - checked).days > window:
            found["unverified"].append(f"{f.name} ({fm.get('type', '?')}, last checked {checked}, window {window} d)")
        if f.name not in linked:
            found["unindexed"].append(f.name)
    return found


def main(argv):
    found = sweep()
    n = {k: len(v) for k, v in found.items()}
    if "--brief" in argv:
        if any(n.values()):
            print("Memory sweep: " + ", ".join(f"{v} {k}" for k, v in n.items() if v) +
                  ". Re-check before relying on them: python3 scripts/memory_sweep.py")
        return 0
    print(f"# Memory sweep — {MEMORY}\n")
    for k, items in found.items():
        print(f"## {k} ({len(items)})")
        for i in items:
            print(f"- {i}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
