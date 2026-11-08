#!/usr/bin/env python3
"""Tally client reactions per skill across all pursuits — the outer-loop signal for sales skills.

Reads `### Client reaction log` lines in cbrain/Clients/*.md (format: SKILL.md step 7):
  - YYYY-MM-DD · landed|rejected|ignored|corrected-us · <skill-id|none> · <finding> · "<client words>"
and `pursuit_outcome:` from frontmatter. Read-only; prints a per-skill table and the outcomes.

Usage: python3 reaction_tally.py [vault]   (default: repo's cbrain/)
"""
import pathlib, re, sys
from collections import Counter, defaultdict

VAULT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[5] / "cbrain"
LINE = re.compile(r"^- (\d{4}-\d{2}-\d{2}) · (landed|rejected|ignored|corrected-us) · ([\w-]+) · (.+)$")
REACTIONS = ["landed", "rejected", "ignored", "corrected-us"]

per_skill, outcomes, bad = defaultdict(Counter), {}, []
for note in sorted((VAULT / "Clients").glob("*.md")):
    text = note.read_text(encoding="utf-8")
    m = re.search(r"^pursuit_outcome:\s*(\S+)", text, re.M)
    if m:
        outcomes[note.stem] = m.group(1)
    sec = re.search(r"^### Client reaction log\n(.*?)(?=^#|\Z)", text, re.M | re.S)
    if not sec:
        continue
    for line in sec.group(1).splitlines():
        if not line.startswith("- "):
            continue
        r = LINE.match(line.strip())
        if r:
            per_skill[r.group(3)][r.group(2)] += 1
        else:
            bad.append(f"{note.stem}: {line[:90]}")

print("skill\t" + "\t".join(REACTIONS) + "\ttotal")
for skill, c in sorted(per_skill.items()):
    print(f"{skill}\t" + "\t".join(str(c[k]) for k in REACTIONS) + f"\t{sum(c.values())}")
print("\noutcomes: " + (", ".join(f"{k}={v}" for k, v in outcomes.items()) or "none recorded"))
for b in bad:
    print(f"UNPARSED {b}")
