#!/usr/bin/env python3
"""Frontmatter lint for the skill library — the metric for the frontmatter fix-loop.

Checks every <category>/<slug>/SKILL.md (skips _template/) against the README schema:
  - frontmatter block present and YAML-parseable
  - required keys present (README "SKILL.md contract")
  - id == folder name, category == parent folder
  - every `modules:` value is a module named in MODULES.md
  - every `related:` [[link]] resolves to an existing skill id
Prints one line per error, then `errors=<n>` as the last line. Exit 0 iff n == 0.

Usage: python3 lint_frontmatter.py [skills_root]   (default: resources/skills next to this script)
"""
import pathlib, re, sys
import yaml

ROOT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[3]
REQUIRED = ["id", "aliases", "name", "category", "description", "triggers", "tags",
            "related", "status", "version", "created", "updated"]

modules_md = (ROOT / "MODULES.md").read_text(encoding="utf-8")
KNOWN_MODULES = set(re.findall(r"^\| `([a-z-]+)` \|", modules_md, re.M))

skills, errors = {}, []
for p in sorted(ROOT.glob("*/*/SKILL.md")):
    if p.parts[-3].startswith("_"):
        continue
    rel = p.relative_to(ROOT)
    m = re.match(r"^---\n(.*?)\n---\n", p.read_text(encoding="utf-8"), re.S)
    if not m:
        errors.append(f"{rel}: no frontmatter block")
        continue
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        errors.append(f"{rel}: YAML parse error: {str(e).splitlines()[0]}")
        continue
    skills[rel] = fm

ids = {fm.get("id") for fm in skills.values()}
for rel, fm in skills.items():
    for k in REQUIRED:
        if k not in fm:
            errors.append(f"{rel}: missing required key `{k}`")
    if fm.get("id") != rel.parts[1]:
        errors.append(f"{rel}: id `{fm.get('id')}` != folder `{rel.parts[1]}`")
    if fm.get("category") != rel.parts[0]:
        errors.append(f"{rel}: category `{fm.get('category')}` != folder `{rel.parts[0]}`")
    for mod in fm.get("modules") or []:
        if mod not in KNOWN_MODULES:
            errors.append(f"{rel}: unknown module `{mod}` (not in MODULES.md)")
    for link in fm.get("related") or []:
        target = str(link).strip("[]")
        if target not in ids:
            errors.append(f"{rel}: related `{link}` does not resolve to a skill id")

for e in errors:
    print(e)
print(f"skills={len(skills)} errors={len(errors)}")
sys.exit(0 if not errors else 1)
