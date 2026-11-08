#!/usr/bin/env python3
"""
Vault link-integrity + hygiene audit for the Obsidian vault (cbrain/ at the repo root).

Reports, by ROOT CAUSE (not raw count):
  - broken [[wikilinks]]  (alias-, table-pipe-, and code-span-aware)
  - orphan notes (0 inbound links)
  - empty files, files without frontmatter
Emits a machine-readable audit.json next to itself for follow-up scripts.

Why the awareness matters (these are the false-positive traps):
  * `[[note\\|Alias]]`  — the pipe is ESCAPED inside Markdown tables. Not a broken name.
  * `aliases:` frontmatter — Obsidian resolves [[Alias]] to the note that declares it.
  * `` `[[x]]` ``       — a wikilink inside inline code / a fenced block is NOT a link.
A naive scan over-reports by ~3x. This script strips all three before judging.

Usage:  python3 link_audit.py [/path/to/vault]   (default: the repo's cbrain/)
"""
import os, re, sys, json
from collections import defaultdict

VAULT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "..", "..", "cbrain")
VAULT = os.path.abspath(VAULT)
OUT = os.path.join(os.path.dirname(__file__), "audit.json")

def walk(ext):
    for root, dirs, files in os.walk(VAULT):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for f in files:
            if f.endswith(ext):
                yield os.path.join(root, f)

md_files = list(walk('.md'))
base_files = list(walk('.base'))
attach_files = list(walk(('.pdf', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')))

def read(p):
    with open(p, encoding='utf-8', errors='replace') as fh:
        return fh.read()

def frontmatter(text):
    if text.startswith('---'):
        end = text.find('\n---', 3)
        if end != -1:
            return text[3:end].strip()
    return None

def strip_code(text):
    """Remove fenced blocks, inline code, and HTML comments so links inside them
    aren't counted (mirrors link_audit.sh, which already strips comments — e.g.
    the notebooklm import template's `<!-- ... [[<Anchor>]] ... -->` usage example)."""
    text = re.sub(r'```.*?```', '', text, flags=re.S)
    text = re.sub(r'`[^`\n]*`', '', text)
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    return text

# name (and alias) -> file path
name_to_paths = defaultdict(list)
for p in md_files:
    name_to_paths[os.path.splitext(os.path.basename(p))[0].lower()].append(p)
    fm = frontmatter(read(p))
    if fm:
        am = re.search(r'^aliases:\s*(.+)$', fm, re.M)
        if am:
            line = am.group(1).strip()
            quoted = re.findall(r'"([^"]+)"|\'([^\']+)\'', line)
            aliases = [(q[0] or q[1]) for q in quoted] if quoted else \
                      [x.strip().strip('[]') for x in line.strip('[]').split(',')]
            for a in aliases:
                if a.strip():
                    name_to_paths[a.strip().lower()].append(p)
for p in base_files:
    name_to_paths[os.path.basename(p).lower()].append(p)
    name_to_paths[os.path.splitext(os.path.basename(p))[0].lower()].append(p)
for p in attach_files:
    name_to_paths[os.path.basename(p).lower()].append(p)
    name_to_paths[os.path.splitext(os.path.basename(p))[0].lower()].append(p)

relpaths = set()
for p in md_files + base_files + attach_files:
    rel = os.path.relpath(p, VAULT)
    relpaths.add(rel.lower()); relpaths.add(os.path.splitext(rel)[0].lower())

LINK = re.compile(r'!?\[\[([^\]]+)\]\]')
broken = defaultdict(list); inbound = defaultdict(set)
empty = []; no_fm = []; fm_type = {}
missing = defaultdict(int)

for p in md_files:
    text = read(p); rel = os.path.relpath(p, VAULT)
    if not text.strip():
        empty.append(rel); continue
    fm = frontmatter(text)
    if fm is None:
        no_fm.append(rel)
    else:
        m = re.search(r'^type:\s*(.+)$', fm, re.M)
        fm_type[rel] = m.group(1).strip() if m else '(no type)'
    for mt in LINK.finditer(strip_code(text)):
        raw = mt.group(1).replace('\\|', '|')
        target = raw.split('|')[0].split('#')[0].strip().rstrip('\\').strip()
        if not target:
            continue
        key = target.lower(); kb = os.path.splitext(key)[0]
        resolved = name_to_paths.get(key) or name_to_paths.get(kb)
        if resolved:
            inbound[os.path.relpath(resolved[0], VAULT)].add(rel)
        elif key in relpaths or kb in relpaths:
            pass  # path-based link, resolves
        else:
            broken[rel].append(target); missing[target] += 1

orphans = [os.path.relpath(p, VAULT) for p in md_files
           if os.path.relpath(p, VAULT) not in empty
           and not inbound.get(os.path.relpath(p, VAULT))]

def bucket(t):
    if re.fullmatch(r'\d{8}', t): return 'daily-note (YYYYMMDD)'
    if t.startswith('[') or t.endswith(']'): return 'MALFORMED syntax'
    if 'via ' in t or t.startswith("'"): return 'mail-sender artifact'
    if t.startswith('YYYYMMDD'): return 'template placeholder (usually code-span)'
    return 'person / org / topic'

buckets = defaultdict(lambda: defaultdict(int))
for t, c in missing.items():
    buckets[bucket(t)][t] += c

print(f"VAULT: {VAULT}")
print(f"md={len(md_files)} base={len(base_files)} | empty={len(empty)} "
      f"no-frontmatter={len(no_fm)} | broken-refs={sum(missing.values())} "
      f"in {len(broken)} files | orphans={len(orphans)}\n")
for b in sorted(buckets, key=lambda k: -sum(buckets[k].values())):
    tot = sum(buckets[b].values())
    print(f"### {b} — {len(buckets[b])} targets, {tot} refs")
    for t, c in sorted(buckets[b].items(), key=lambda x: -x[1]):
        print(f"   {c:3d}x  [[{t}]]")
    print()

json.dump({"empty": empty, "no_frontmatter": no_fm, "broken": dict(broken),
           "missing_targets": dict(missing), "orphans": orphans, "fm_type": fm_type},
          open(OUT, "w"), indent=1)
print(f"→ {OUT}")
