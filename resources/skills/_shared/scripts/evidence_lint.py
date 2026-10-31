#!/usr/bin/env python3
"""Evidence lint — the metric for the evidence-gate fix-loop (_shared/evidence-gate.md, autoresearch-loop.md).

Reads every Markdown table in an EVIDENCE.md that has a claim column, and counts release blockers:
  uncited    — tag observed/inferred but the source cell is empty or a placeholder
  assumed    — tag assumed, not marked as disclosed in the deliverable
               (write `assumed (stated)` / `assumed (flagged)` once the deliverable labels it)
  untagged   — no recognisable provenance tag, or the table has no tag column at all
Tables without a claim column (source lists, gate lists) are ignored; struck-through (~~retired~~)
claims are skipped.

Usage: python3 evidence_lint.py EVIDENCE.md [--quiet]
Last line: `claims=<n> uncited=<a> assumed=<b> untagged=<c> blockers=<a+b+c>`. Exit 0 iff blockers == 0.
"""
import re, sys

CLAIM = re.compile(r"claim|aussage|behauptung", re.I)
TAG = re.compile(r"^(type|tag|class|prov\.?|provenance|direct observation.*|reliability|typ|status|einordnung)$", re.I)
SOURCE = re.compile(r"source|beleg|quelle|how verified|evidence", re.I)
OBSERVED = re.compile(r"observ|\bobs\b|direct|external|vendor|verified|fact|cited|beobacht", re.I)
INFERRED = re.compile(r"infer|\binf\b|recommend|estimate|derived|ableitung", re.I)
ASSUMED = re.compile(r"assum|annahme", re.I)
DISCLOSED = re.compile(r"stated|flagged|disclosed|marked|explicitly|placeholder|gate [a-z]?\d|gekennzeichnet|benannt|platzhalter|ausdrücklich|geführt", re.I)
EMPTY = re.compile(r"^(|—|–|-|n/?a|\?|tbd|todo|none|offen|missing)$", re.I)


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def lint(text):
    claims = uncited = assumed = untagged = 0
    issues, header = [], None
    for n, line in enumerate(text.splitlines(), 1):
        if not line.lstrip().startswith("|"):
            header = None
            continue
        row = cells(line)
        if all(re.fullmatch(r":?-{2,}:?", c) for c in row if c):
            continue
        if header is None:
            header = row
            ci = next((i for i, h in enumerate(header) if CLAIM.search(h)), None)
            tags = [i for i, h in enumerate(header) if TAG.match(h.strip("* "))]
            exact = [i for i in tags if header[i].strip("* ").lower() in ("tag", "type", "class", "typ")]
            ti = (exact or tags or [None])[0]
            si = next((i for i, h in enumerate(header) if SOURCE.search(h) and i != ci), None)
            if si is None:  # "Provenance" used as the source column when a separate Tag column exists
                si = next((i for i in tags if i != ti), None)
            continue
        if ci is None or ci >= len(row) or not row[ci]:
            continue
        if row[ci].startswith("~~"):
            continue  # struck through = retired claim, not shipped
        claims += 1
        tag = row[ti] if ti is not None and ti < len(row) else ""
        src = row[si].strip("`* ") if si is not None and si < len(row) else ""
        if not (ASSUMED.search(tag) or OBSERVED.search(tag) or INFERRED.search(tag)):
            # no usable tag column: accept a provenance word in any other non-source cell
            tag = " ".join(c for i, c in enumerate(row) if i not in (ci, si))
        where = f"L{n}: {row[ci][:70]}"
        if ASSUMED.search(tag):
            if not DISCLOSED.search(tag + " " + src):
                assumed += 1
                issues.append(f"ASSUMED  {where}")
        elif OBSERVED.search(tag) or INFERRED.search(tag):
            if EMPTY.match(src):
                uncited += 1
                issues.append(f"UNCITED  {where}")
        else:
            untagged += 1
            issues.append(f"UNTAGGED {where} (tag cell: {tag[:30]!r})")
    return claims, uncited, assumed, untagged, issues


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    c, u, a, t, issues = lint(open(sys.argv[1], encoding="utf-8").read())
    if "--quiet" not in sys.argv:
        print("\n".join(issues))
    print(f"claims={c} uncited={u} assumed={a} untagged={t} blockers={u + a + t}")
    sys.exit(0 if u + a + t == 0 else 1)
