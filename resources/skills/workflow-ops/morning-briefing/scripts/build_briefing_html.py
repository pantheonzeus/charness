#!/usr/bin/env python3
"""Build the morning-briefing page for a given day.

Reads today's meeting notes (their per-meeting prep blocks) plus the two newest
NotebookLM podcasts, writes the page content to
    output/morning-briefing/<YYYYMMDD>.md     (template: briefing — content only)
and renders it through the reading-pages skill to the self-contained
    output/morning-briefing/<YYYYMMDD>.html   (design from webapp/design/, never from here)

Deterministic, pure stdlib, no judgment — the prep text is authored upstream by
the headless `build-briefing` workflow and embedded in each meeting note as an
`mb-prep` JSON comment. If that block is absent (e.g. running this generator
standalone), it falls back to the note's raw sections so the page still renders.

Repo root is resolved from this script's own path so launchd's cwd doesn't
matter (mirrors daily_audio.py / distill_to_vault.sh).
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]
VAULT = REPO_ROOT / "cbrain"
NOTES_DIR = VAULT / "notes"
PODCAST_DIR = REPO_ROOT / "output" / "podcasts"
OUT_DIR = REPO_ROOT / "output" / "morning-briefing"
PAGE = REPO_ROOT / "resources" / "skills" / "workflow-ops" / "reading-pages" / "scripts" / "page.py"

PREP_RE = re.compile(r"<!--mb-prep\s*(.*?)\s*mb-prep-->", re.DOTALL)


def read_frontmatter_and_body(text):
    """Split a note into (frontmatter dict-ish lines, body). Minimal parser."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm = text[3:end]
            body = text[end + 4:]
            return fm, body
    return "", text


def section(body, header):
    """Return the text under a `## header` up to the next `## `."""
    m = re.search(rf"^##\s+{re.escape(header)}\s*$", body, re.MULTILINE)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^##\s+", body[start:], re.MULTILINE)
    return body[start: start + nxt.start()].strip() if nxt else body[start:].strip()


def field(body, label):
    m = re.search(rf"^\*\*{re.escape(label)}:\*\*\s*(.+)$", body, re.MULTILINE)
    return m.group(1).strip() if m else ""


def parse_meeting(path):
    text = path.read_text(encoding="utf-8")
    _, body = read_frontmatter_and_body(text)

    # Structured prep authored by the workflow wins; fall back to raw sections.
    prep = {}
    pm = PREP_RE.search(text)
    if pm:
        try:
            prep = json.loads(pm.group(1))
        except json.JSONDecodeError:
            prep = {}

    title = prep.get("title") or ""
    if not title:
        tm = re.search(r"^#\s+Meeting\s+—\s+(.+)$", body, re.MULTILINE)
        title = tm.group(1).strip() if tm else path.stem

    time = prep.get("time") or field(body, "Time") or ""

    if prep.get("participants"):
        participants = prep["participants"]
    else:
        participants = [
            {"name": n.strip()}
            for n in re.findall(r"^-\s*\[\[([^\]]+)\]\]", section(body, "Attendees"), re.MULTILINE)
        ]

    description = prep.get("description")
    if not description:
        desc = section(body, "Notes")
        description = desc if desc else ""

    return {
        "time": time,
        "title": title,
        "description": description,
        "participants": participants,
        "shared_themes": prep.get("shared_themes", []),
        "prep_guide": prep.get("prep_guide", []),
        "open_threads": prep.get("open_threads", []),
        "smart_questions": prep.get("smart_questions", []),
        "has_prep": bool(prep),
    }


def latest_podcasts(n=2):
    """The n newest podcasts by filename (names lead with YYYYMMDD)."""
    m4as = sorted(PODCAST_DIR.glob("*.m4a"), key=lambda p: p.name, reverse=True)
    out = []
    for p in m4as[:n]:
        # <stem>.m4a -> <stem>.summary.md
        summ = p.parent / (p.stem + ".summary.md")
        title = p.stem
        if summ.exists():
            fm, _ = read_frontmatter_and_body(summ.read_text(encoding="utf-8"))
            tm = re.search(r"^notebook_title:\s*(.+)$", fm, re.MULTILINE)
            if tm:
                title = tm.group(1).strip()
        out.append({"file": p.name, "title": title})
    return out


def safe(s):
    """Calendar and mail text is untrusted: it may not open a heading or a code fence of its own."""
    return re.sub(r"^(\s*)(#|```|~~~)", r"\1\\\2", str(s or "").strip(), flags=re.MULTILINE)


def one_line(s):
    return safe(" ".join(str(s or "").split()))


def fenced(kind, data):
    return f"```{kind}\n{json.dumps(data, ensure_ascii=False, indent=1)}\n```"


def build_md(date_compact, meetings, pods):
    try:
        pretty = dt.datetime.strptime(date_compact, "%Y%m%d").strftime("%A, %d %B %Y")
    except ValueError:
        pretty = date_compact
    n = len(meetings)
    first = next((m for m in meetings if m["time"]), meetings[0] if meetings else None)
    lead = (f"{n} meeting{'' if n == 1 else 's'} today. First up: {one_line(first['time'])} {one_line(first['title'])}."
            if first else "No meetings today.")
    out = ["---", "template: briefing", f"title: Morning briefing — {pretty}",
           f"date: {date_compact}", "---", "", lead, ""]
    if meetings:
        out += ["## At a glance", "", fenced("timeline", [
            {"date": m["time"] or "—", "label": " ".join(str(m["title"]).split()), **({"kind": "next"} if i == 0 else {})}
            for i, m in enumerate(meetings)]), ""]
    for m in meetings:
        out += [f"## {one_line(m['time']) + ' · ' if m['time'] else ''}{one_line(m['title'])}", ""]
        people = [{"name": p.get("name", ""), "role": " · ".join(x for x in (p.get("role"), p.get("company")) if x)}
                  for p in m["participants"] if p.get("name")]
        if people:
            out += [fenced("people", people), ""]
        if m["description"]:
            out += [safe(m["description"]), ""]
        for label, key in (("Shared themes", "shared_themes"), ("Prep guide", "prep_guide"),
                           ("Open threads (mail)", "open_threads"), ("Smart questions", "smart_questions")):
            if m[key]:
                out += [f"### {label}", ""] + [f"- {one_line(x)}" for x in m[key]] + [""]
        if not m["has_prep"]:
            out += ["_No prep block yet — showing the raw note._", ""]
    if pods:
        out += ["## Listen", "", fenced("audio", [{"title": p["title"], "src": "../podcasts/" + p["file"]} for p in pods]), ""]
    return "\n".join(out)


def uv():
    """launchd's PATH lacks ~/.local/bin and Homebrew, so look there too."""
    for c in (shutil.which("uv"), os.path.expanduser("~/.local/bin/uv"), "/opt/homebrew/bin/uv"):
        if c and os.path.exists(c):
            return c
    sys.exit("uv not found: needed to render the page (reading-pages skill)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="YYYYMMDD or YYYY-MM-DD (default: today)")
    ap.add_argument("--vault", help="override vault root (default <repo>/cbrain)")
    args = ap.parse_args()

    date_compact = (args.date or dt.date.today().strftime("%Y%m%d")).replace("-", "")
    notes_dir = (Path(args.vault) / "notes") if args.vault else NOTES_DIR
    meeting_files = sorted(notes_dir.glob(f"{date_compact}-*.md"))
    meetings = [parse_meeting(p) for p in meeting_files]
    meetings.sort(key=lambda m: (m["time"] or "99:99"))
    pods = latest_podcasts(2)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    md_path = OUT_DIR / f"{date_compact}.md"
    md_path.write_text(build_md(date_compact, meetings, pods), encoding="utf-8")
    r = subprocess.run([uv(), "run", "--quiet", str(PAGE), "render", str(md_path)], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"page render failed for {md_path}:\n{r.stdout}{r.stderr}")
    print(f"Wrote {md_path.with_suffix('.html')}  ({len(meetings)} meetings, {len(pods)} podcasts)")


if __name__ == "__main__":
    main()
