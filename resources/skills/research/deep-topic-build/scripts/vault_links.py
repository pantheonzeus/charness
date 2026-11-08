#!/usr/bin/env python3
"""Vault link helper for research/deep-topic-build. Stdlib only.

  check FILE...       Every [[wikilink]] in each FILE resolves to a file in the vault. Exit 1 on any miss.
  append SPEC.json    For each entry, insert `line` at the end of the first block under `heading` in `note`.
                      Idempotent: skipped when the line's key (text before " — ") is already in the note.
                      A missing heading is created at the end of the note.

SPEC.json: [{"note": "projects/X.md", "heading": "## Links", "line": "- Sibling: [[Y]] — added 2026-10-23; reason"}]
`note` is relative to --vault (default: <repo>/cbrain).
"""
import argparse, json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
LINK = re.compile(r"\[\[([^\]]+)\]\]")


def vault_names(vault: Path) -> set:
    names = set()
    for p in vault.rglob("*"):
        if p.is_file() and ".obsidian" not in p.parts:
            names.add(p.name)
            if p.suffix == ".md":
                names.add(p.stem)
    return names


def check(vault: Path, files: list) -> int:
    names, misses = vault_names(vault), 0
    for f in files:
        for raw in sorted(set(LINK.findall(Path(f).read_text(encoding="utf-8")))):
            target = Path(re.split(r"[|#]", raw)[0].strip()).name
            if target and target not in names:
                print(f"MISSING {f}: [[{raw}]]")
                misses += 1
    print("OK" if not misses else f"FAIL: {misses} unresolved link(s)")
    return 1 if misses else 0


def insert(note: Path, heading: str, line: str) -> str:
    lines = note.read_text(encoding="utf-8").split("\n")
    key = line.split(" — ")[0].strip()
    if any(key in l for l in lines):
        return "SKIP (already linked)"
    try:
        i = next(n for n, l in enumerate(lines) if l.strip() == heading) + 1
    except StopIteration:
        while lines and lines[-1].strip() == "":
            lines.pop()
        lines += ["", heading, line, ""]
        note.write_text("\n".join(lines), encoding="utf-8")
        return "OK (heading created)"
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    while i < len(lines) and lines[i].strip() and not lines[i].startswith("## "):
        i += 1
    lines.insert(i, line)
    note.write_text("\n".join(lines), encoding="utf-8")
    return f"OK @ line {i + 1}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vault", type=Path, default=REPO / "cbrain")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check").add_argument("files", nargs="+")
    sub.add_parser("append").add_argument("spec", type=Path)
    a = ap.parse_args()
    if a.cmd == "check":
        return check(a.vault, a.files)
    for e in json.loads(a.spec.read_text(encoding="utf-8")):
        note = a.vault / e["note"]
        print(f"{insert(note, e['heading'], e['line']) if note.exists() else 'NO NOTE'}  {e['note']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
