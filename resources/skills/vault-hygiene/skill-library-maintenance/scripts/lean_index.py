#!/usr/bin/env python3
"""Lean skill index: the always-on routing view of INDEX.md (Pi's "minimal core" lesson).

INDEX.md stays the source of truth (full descriptions, human-readable). This script derives a
compact candidate view: one line per skill with its path, name and triggers, plus the description
cut to its first clause. NOT wired into the SessionStart hook: trimmed views routed worse than the
full INDEX on 2026-10-11 (see skill-library-maintenance/SKILL.md), so the hook injects INDEX.md
as is. Kept for re-tests.

  python3 lean_index.py [--index PATH] [--desc-chars N] [--max-triggers N]     # prints the lean index
Validate any change with routing_eval.py --index <output>: it must not route worse than INDEX.md.
"""
import argparse
import pathlib
import re

SKILLS = pathlib.Path(__file__).resolve().parents[3]
ap = argparse.ArgumentParser()
ap.add_argument("--index", default=str(SKILLS / "INDEX.md"))
ap.add_argument("--desc-chars", type=int, default=110, help="0 drops descriptions entirely")
ap.add_argument("--max-triggers", type=int, default=0, help="keep only the first N trigger phrases (0 = all)")
a = ap.parse_args()

out = ["# Skill Index (lean)",
       "One line per skill: `path` · name — triggers ¦ what it does. Match the task against the triggers, then open "
       "`resources/skills/<path>/SKILL.md`. Full entries: `grep -A0 '<path>' resources/skills/INDEX.md`.", ""]
n = 0
for line in pathlib.Path(a.index).read_text(encoding="utf-8").splitlines():
    if line.startswith("## "):
        out.append(f"\n## {line[3:].strip()}")
        continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 4 or not cells[-1].startswith("`") or cells[0] in ("Skill", "---"):
        continue
    name, triggers, desc, path = cells[0], cells[1], cells[2], cells[-1].strip("`")
    if a.max_triggers:
        triggers = ", ".join([t.strip() for t in triggers.split(",") if t.strip()][:a.max_triggers])
    path = re.sub(r"/SKILL\.md$|\.md$", "", path)
    name = re.split(r" — | → ", re.sub(r"\*\(.*?\)\*|\*", "", name))[0].strip()
    desc = re.sub(r"\*\(.*?\)\*|\*\*|`", "", desc)
    if a.desc_chars:
        first = re.split(r"(?<=[.;:])\s|—", desc)[0].strip()
        desc = first if len(first) <= a.desc_chars else first[:a.desc_chars].rsplit(" ", 1)[0] + "…"
    out.append(f"- `{path}` · {name} — {triggers}" + (f" ¦ {desc}" if a.desc_chars and desc else ""))
    n += 1
out[0] += f" — {n} skills"
print("\n".join(out))
