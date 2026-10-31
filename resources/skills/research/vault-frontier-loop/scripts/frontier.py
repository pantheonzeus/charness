#!/usr/bin/env python3
"""Deterministic half of the vault-frontier-loop skill. No LLM, no network.

  frontier.py pick [--n 5]                 rank topic notes, print the day's picks as JSON
  frontier.py check <output/frontier/YYYY-MM-DD.json>   validate the digest (OK or FAIL lines, exit 1)

Ranking, per topic note in cbrain/projects/ (type: topic):
  +3  linked from the note of someone in a meeting today / next workday (output/meetings/meetings.json)
  +1  linked from an account note those people link to (one hop further)
  +0..3  staleness: days since the last "## What changed — YYYY-MM-DD" entry (or file mtime), /10, capped
  +0..1  how connected it is: backlinks across the vault, /20, capped
Skipped: content-idea-*, career-*, ladder-campaign, and any note with `frontier: skip` in its frontmatter.
`frontier: always` forces a note into the picks.
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
VAULT = REPO / "cbrain"
TOPICS = VAULT / "projects"
MEETINGS = REPO / "output" / "meetings" / "meetings.json"
SKIP = re.compile(r"^(content-idea-|career-|ladder-campaign)")
CHANGED = re.compile(r"^## What changed — (\d{4}-\d{2}-\d{2})", re.M)
LINK = re.compile(r"\[\[([^\]|#]+)")
CONFIDENCE = {"verified", "likely", "unsure"}
WEB_CAP = 30


def fm(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return dict(re.findall(r"^(\w+):\s*(.+?)\s*$", m.group(1), re.M)) if m else {}


def links(text):
    return {x.strip() for x in LINK.findall(text)}


def meeting_people():
    """{person note title: [meeting uids]} for meetings that haven't ended."""
    try:
        data = json.loads(MEETINGS.read_text())
    except (OSError, ValueError):
        return {}, []
    now = dt.datetime.now().astimezone()
    live = [m for m in data.get("meetings", []) if dt.datetime.fromisoformat(m["end"].replace("Z", "+00:00")) > now]
    by_email = {}
    for m in live:
        for a in m.get("attendees", []):
            if a.get("email"):
                by_email.setdefault(a["email"].lower(), []).append(m["uid"])
    people = {}
    for note in (VAULT / "Clients").glob("*.md"):
        text = note.read_text(errors="ignore")
        for email in re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text[:1500]):
            if email.lower() in by_email:
                people.setdefault(note.stem, set()).update(by_email[email.lower()])
    return {k: sorted(v) for k, v in people.items()}, live


def pick(n):
    people, live = meeting_people()
    direct, via_account, who = {}, {}, {}   # topic -> meeting uids; topic -> the people whose notes lead to it
    for person, uids in people.items():
        text = (VAULT / "Clients" / f"{person}.md").read_text(errors="ignore")
        for t in links(text):
            direct.setdefault(t, set()).update(uids)
            who.setdefault(t, set()).add(person)
            acc = VAULT / "Clients" / f"{t}.md"
            if acc.exists() and fm(acc.read_text(errors="ignore")).get("type") == "account":
                for t2 in links(acc.read_text(errors="ignore")):
                    via_account.setdefault(t2, set()).update(uids)
                    who.setdefault(t2, set()).add(person)
    backlinks = {}
    for f in VAULT.rglob("*.md"):
        for t in links(f.read_text(errors="ignore")):
            backlinks[t] = backlinks.get(t, 0) + 1
    today = dt.date.today()
    ranked = []
    for note in sorted(TOPICS.glob("*.md")):
        text = note.read_text(errors="ignore")
        meta = fm(text)
        if meta.get("type") != "topic" or SKIP.match(note.stem) or meta.get("frontier") == "skip":
            continue
        dates = CHANGED.findall(text)
        last = dt.date.fromisoformat(max(dates)) if dates else dt.date.fromtimestamp(note.stat().st_mtime)
        if last == today and meta.get("frontier") != "always":
            continue   # already expanded today
        age = (today - last).days
        uids = direct.get(note.stem, set()) | via_account.get(note.stem, set())
        score = 3 * bool(direct.get(note.stem)) + 1 * bool(via_account.get(note.stem)) \
            + min(age / 10, 3) + min(backlinks.get(note.stem, 0) / 20, 1) + (100 if meta.get("frontier") == "always" else 0)
        why = []
        if direct.get(note.stem):
            why.append("linked from someone you meet soon")
        elif via_account.get(note.stem):
            why.append("linked from an account you meet soon")
        why.append(f"last expanded {age} days ago" if dates else f"never expanded; file {age} days old")
        ranked.append({"note": str(note.relative_to(VAULT)), "title": note.stem, "score": round(score, 2),
                       "why": "; ".join(why), "meetings": sorted(uids),
                       "people": sorted(who.get(note.stem, ()))})
    ranked.sort(key=lambda x: -x["score"])
    return {"date": today.isoformat(), "meetings_considered": len(live), "picks": ranked[:n]}


def check(path):
    try:
        d = json.loads(Path(path).read_text())
    except (OSError, ValueError) as e:
        return [f"cannot read JSON: {e}"]
    errs = []
    if Path(path).stem != d.get("date"):
        errs.append("date must match the filename (YYYY-MM-DD)")
    if not d.get("created"):
        errs.append("missing created (date -Iseconds)")
    calls = (d.get("budget") or {}).get("web_calls")
    if not isinstance(calls, int):
        errs.append("budget.web_calls must be the true count (int); never round it to pass this check")
    elif calls > WEB_CAP and (d.get("budget") or {}).get("capped") is not True:
        errs.append(f"budget.web_calls {calls} is over the cap of {WEB_CAP}: set budget.capped true and say why in the spine")
    topics = d.get("topics")
    if not isinstance(topics, list) or not 1 <= len(topics) <= 5:
        errs.append("topics: 1–5 entries")
        topics = []
    for t in topics:
        name = t.get("note", "?")
        if not (VAULT / name).is_file():
            errs.append(f"{name}: not a vault note (path relative to cbrain/)")
        if not isinstance(t.get("findings"), list):
            errs.append(f"{name}: findings must be a list (empty if nothing new: say so in `nothing_new`)")
            continue
        if not t["findings"] and not t.get("nothing_new"):
            errs.append(f"{name}: no findings, so nothing_new must say what was checked")
        for f in t["findings"]:
            fid = f.get("id", "?")
            for k in ("id", "text", "so_what"):
                if not str(f.get(k, "")).strip():
                    errs.append(f"{name} {fid}: missing {k}")
            if f.get("confidence") not in CONFIDENCE:
                errs.append(f"{name} {fid}: confidence must be one of {sorted(CONFIDENCE)}")
            srcs = f.get("sources") or []
            if not srcs or not all(str(s.get("url", "")).startswith("http") for s in srcs):
                errs.append(f"{name} {fid}: needs >=1 source with an http(s) url")
            if not isinstance(f.get("client_safe"), bool):
                errs.append(f"{name} {fid}: client_safe must be true or false")
            for k in ("people", "meetings"):
                if not isinstance(f.get(k, []), list):
                    errs.append(f"{name} {fid}: {k} must be a list")
    return errs


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["pick"]:
        n = int(a[a.index("--n") + 1]) if "--n" in a else 5
        print(json.dumps(pick(min(n, 5)), indent=1, ensure_ascii=False))
    elif len(a) == 2 and a[0] == "check":
        errs = check(a[1])
        print("OK" if not errs else "\n".join("FAIL: " + e for e in errs))
        sys.exit(1 if errs else 0)
    else:
        print(__doc__)
        sys.exit(64)
