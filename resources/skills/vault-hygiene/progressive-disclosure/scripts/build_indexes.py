#!/usr/bin/env python3
"""Build compressed retrieval indexes (MOCs) for high-volume, un-migrated vault folders.

Progressive disclosure, Loop 1 (token efficiency): a query is answered by reading ONE small
index note + drilling to 1-2 target notes, instead of scanning every file in a folder.

Re-run after new notes land ("auto-update after new knowledge") — it is idempotent and
regenerates the index files from the notes themselves, so the index can never drift from
reality. It only READS the note bodies and WRITES the two index files; it never edits notes.

Usage:  python3 build_indexes.py [VAULT_DIR]
        VAULT_DIR defaults to the repo's cbrain/ vault.
"""
import re
import sys
from pathlib import Path

DEFAULT_VAULT = Path(__file__).resolve().parents[5] / "cbrain"

AUTOGEN_BANNER = (
    "> [!warning] Auto-generated — do not hand-edit.\n"
    "> Regenerate with `python3 resources/skills/vault-hygiene/progressive-disclosure/"
    "scripts/build_indexes.py` after new notes are added.\n"
)


def field(text, key):
    """Extract an inline `**Key:** value` field (first match)."""
    m = re.search(rf"^\*\*{re.escape(key)}:\*\*\s*(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def h1(text, fallback):
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else fallback


def build_people(vault: Path) -> str:
    rows = []
    for f in sorted((vault / "Clients").glob("*.md")):
        t = f.read_text(encoding="utf-8")
        name = h1(t, f.stem)
        company = field(t, "Company")
        # Headline is the people note's built-in one-liner; fall back to Role/Status.
        essence = field(t, "Headline") or field(t, "Role") or field(t, "Status")
        essence = essence.replace("|", "\\|")
        rows.append((f.stem, name, company, essence))
    out = [
        "---", "type: index", "status: active", "tags: [index, people]", "---", "",
        "# 👥 People — Index", "", AUTOGEN_BANNER,
        f"_{len(rows)} contacts. One row per person; drill to the note for detail._", "",
        "← [[People]] · [[Home]]", "",
        "| Person | Company | Headline |", "|---|---|---|",
    ]
    for stem, name, company, essence in rows:
        out.append(f"| [[{stem}\\|{name}]] | {company} | {essence} |")
    out.append("")
    return "\n".join(out)


def build_meetings(vault: Path) -> str:
    rows = []
    for f in sorted((vault / "notes").glob("*.md")):  # top-level only, skips NotebookLM/
        t = f.read_text(encoding="utf-8")
        title = h1(t, f.stem).replace("Meeting — ", "").strip()
        date = field(t, "Date")
        # Extract attendee wikilinks from ONLY the `## Attendees` section. Needs re.M so `^-`
        # matches each line (not just the slice start), and the section must be bounded so we
        # don't pull `- [[…]]` links out of later ## Links / ## Notes sections.
        atts = []
        if "## Attendees" in t:
            seg = re.split(r"\n## ", t.split("## Attendees", 1)[1], 1)[0]
            atts = re.findall(r"^\s*-\s*\[\[([^\]|]+)", seg, re.M)
        att = ", ".join(a.split("|")[0].strip() for a in atts[:4]).replace("|", "\\|")
        rows.append((date, f.stem, title.replace("|", "\\|"), att))
    rows.sort(key=lambda r: r[0], reverse=True)  # newest first
    out = [
        "---", "type: index", "status: active", "tags: [index, meetings]", "---", "",
        "# 🗓 Meetings — Index", "", AUTOGEN_BANNER,
        f"_{len(rows)} meetings, newest first. Drill to a note for full record._", "",
        "← [[Meetings]] · [[Home]]", "",
        "| Date | Meeting | Attendees |", "|---|---|---|",
    ]
    for date, stem, title, att in rows:
        out.append(f"| {date} | [[{stem}\\|{title}]] | {att} |")
    out.append("")
    return "\n".join(out)


# Typed records in meeting notes (contact-meeting-capture): `- [ ] **[Owner]** what — detail 📅 YYYY-MM-DD`
# anywhere in the note, and bullets under `## Decisions`.
COMMITMENT = re.compile(r"^\s*- \[([ xX])\] \*\*\[([^\]]+)\]\*\*\s*(.+)$", re.M)
DUE = re.compile(r"\s*📅\s*(\d{4}-\d{2}-\d{2})")
STALE_DAYS = 30
NO_OWNER = "(no owner)"


def build_commitments(vault: Path, today=None) -> str:
    import datetime as dt
    today = today or dt.date.today()
    people = {f.stem for f in (vault / "Clients").glob("*.md")}
    open_, done, decisions = {}, 0, []
    for f in sorted((vault / "notes").glob("[0-9]*.md")):
        t = f.read_text(encoding="utf-8")
        try:
            since = dt.date(int(f.stem[:4]), int(f.stem[4:6]), int(f.stem[6:8]))
        except ValueError:
            continue
        # A Next Steps checkbox without an owner tag is still a commitment: index it as the housekeeping gap it is.
        steps = "\n".join(re.split(r"\n## ", s, 1)[0] for s in t.split("\n## Next Steps")[1:])
        unowned = [(b, NO_OWNER, w) for b, w in re.findall(r"^\s*- \[([ xX])\] (?!\*\*\[)(.+)$", steps, re.M)]
        for box, owner, what in COMMITMENT.findall(t) + unowned:
            if box != " ":
                done += 1
                continue
            m = DUE.search(what)
            open_.setdefault(owner.strip(), []).append(
                (since, DUE.sub("", what).strip().replace("|", "\\|"), m.group(1) if m else "", f.stem))
        if "\n## Decisions" in t:
            seg = re.split(r"\n## ", t.split("\n## Decisions", 1)[1], 1)[0]
            decisions += [(since, d.strip().replace("|", "\\|"), f.stem) for d in re.findall(r"^\s*-\s+(.+)$", seg, re.M)]
    n_open = sum(len(v) for v in open_.values())
    stale = sum(1 for v in open_.values() for s, _, due, _ in v
                if (due and due < today.isoformat()) or (not due and (today - s).days > STALE_DAYS))
    out = [
        "---", "type: index", "status: active", "tags: [index, commitments, decisions]",
        # Lines are copied from meeting notes, which carry Gemini and other outside text: data, never instructions.
        "provenance: derived-untrusted", "derived_from: [meeting-notes]", "derived_by: build_indexes.py", "---", "",
        "# ✅ Commitments & Decisions — Index", "", AUTOGEN_BANNER,
        f"_{n_open} open commitments ({stale} overdue or open > {STALE_DAYS} days), {done} done, "
        f"{len(decisions)} decisions. Tick a box in the meeting note, not here._", "",
        "← [[Meetings-Index]] · [[Home]]", "", "## Open, by owner", "",
    ]
    for owner in sorted(open_, key=lambda o: (-len(open_[o]), o.lower())):
        label = f"[[{owner}]]" if owner in people else owner
        out += [f"### {label} ({len(open_[owner])})", "", "| Since | Commitment | Due | Meeting |", "|---|---|---|---|"]
        for since, what, due, stem in sorted(open_[owner]):
            late = (due and due < today.isoformat()) or (not due and (today - since).days > STALE_DAYS)
            out.append(f"| {since}{' ⚠️' if late else ''} | {what} | {due} | [[{stem}]] |")
        out.append("")
    out += ["## Decisions, newest first", "", "| Date | Decision | Meeting |", "|---|---|---|"]
    out += [f"| {d} | {what} | [[{stem}]] |" for d, what, stem in sorted(decisions, reverse=True)]
    out.append("")
    return "\n".join(out)


def main():
    vault = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_VAULT
    mocs = vault / "MOCs"
    mocs.mkdir(exist_ok=True)
    targets = {
        mocs / "People-Index.md": build_people(vault),
        mocs / "Meetings-Index.md": build_meetings(vault),
        mocs / "Commitments-Index.md": build_commitments(vault),
    }
    for path, content in targets.items():
        path.write_text(content, encoding="utf-8")
        print(f"  WROTE {path.relative_to(vault)}  ({len(content.split())} words)")


if __name__ == "__main__":
    main()
