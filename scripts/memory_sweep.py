#!/usr/bin/env python3
"""Stale-fact sweep for the memory dir (MEMORY.md index + one file per fact).

A memory is a claim that was true when written. This lists the ones to re-check:
  - expired:     metadata.valid_until is in the past
  - unverified:  no verification within the window (project 30 d; feedback, user, reference 180 d),
                 dated by metadata.last_verified, else metadata.modified, else the file's mtime
  - unindexed:   a memory file MEMORY.md does not list (it is never injected)
  - dangling:    a MEMORY.md line pointing at a file that does not exist
  - superseded:  a file with metadata.superseded_by that MEMORY.md still lists, or whose target is missing
  - unconsolidated: a body that still carries an inline revision (**Correction**, **Update**, **Outcome**,
                 **Resolved**, "supersedes"/"superseded") above its `## Superseded` section
  - unscoped:    a feedback memory with no `**How to apply:**` line saying which tasks the rule governs

Supersession convention (Memora, arXiv 2604.20006: agents keep reusing invalidated memories):
  - The body states only what is true now. A retired claim moves to a closing `## Superseded` section as
    `- YYYY-MM-DD: <old claim> → <what replaced it>`, so it stays auditable but never reads as current.
  - A whole memory replaced by another gets `superseded_by: <name>` under `metadata:` and leaves MEMORY.md.
  - A feedback rule names its scope in `**How to apply:**`. A preference given for one kind of task (skip a
    confirmation, relax a check) never widens to others. (The Memory Trap, arXiv 2611.07554: memories from
    benign low-stakes sessions led agents to skip confirmation and weaken tests on high-stakes tasks.)
  - The consolidation pass (resources/skills/vault-hygiene/memory-consolidation, scripts/memory_dream.py)
    clears both flags.

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
HOW_TO_APPLY = re.compile(r"^\*\*How to apply:?\*\*", re.M)
REVISION = re.compile(r"^[ \t]*\*\*(Correction|Update|Outcome|Resolved)\b|\bsupersed(es|ed)\b", re.I | re.M)


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    return dict(re.findall(r"^[ \t]*(\w+):[ \t]*\"?(.*?)\"?[ \t]*$", m.group(1), re.M)) if m else {}


def day(value):
    try:
        return dt.date.fromisoformat(value[:10])
    except (TypeError, ValueError):
        return None


def unconsolidated(text):
    """Inline revisions in the body above `## Superseded` (frontmatter and that section excluded)."""
    body = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    current = re.split(r"^## Superseded\b", body, maxsplit=1, flags=re.M)[0]
    return sorted({m.group(0).strip("* \t").lower() for m in REVISION.finditer(current)})


def sweep(today=None, memory=None):
    today, memory = today or dt.date.today(), memory or MEMORY
    index = (memory / "MEMORY.md").read_text() if (memory / "MEMORY.md").exists() else ""
    linked = set(re.findall(r"\]\(([^)]+\.md)\)", index))
    found = {"expired": [], "unverified": [], "unindexed": [], "dangling": sorted(l for l in linked if not (memory / l).exists()),
             "superseded": [], "unconsolidated": [], "unscoped": []}
    for f in sorted(memory.glob("*.md")):
        if f.name == "MEMORY.md":
            continue
        text = f.read_text()
        fm = frontmatter(text)
        by = fm.get("superseded_by", "")
        if by:
            if not (memory / f"{by.removesuffix('.md')}.md").exists():
                found["superseded"].append(f"{f.name} (superseded_by {by}: no such memory)")
            if f.name in linked:
                found["superseded"].append(f"{f.name} (superseded by {by}, still in MEMORY.md)")
            continue
        marks = unconsolidated(text)
        if marks:
            found["unconsolidated"].append(f"{f.name} ({', '.join(marks)})")
        if fm.get("type") == "feedback" and not HOW_TO_APPLY.search(text):
            found["unscoped"].append(f.name)
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
                  ". Re-check before relying on them: python3 scripts/memory_sweep.py" +
                  ("; consolidate: resources/skills/vault-hygiene/memory-consolidation"
                   if n["superseded"] or n["unconsolidated"] else ""))
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
