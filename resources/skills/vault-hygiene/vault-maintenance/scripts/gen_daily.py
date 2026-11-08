#!/usr/bin/env python3
"""
Backfill honest daily-note stubs for every [[YYYYMMDD]] link that has no note yet.

Reads audit.json (produced by link_audit.py) for the set of referenced-but-missing
daily dates, then writes daily reports/YYYYMMDD.md listing that day's REAL meetings
(notes/YYYYMMDD-*.md) and weather (weather data/YYYYMMDD-*.md). No fabricated summaries —
a stub is honest scaffolding, not invented content. Idempotent: never overwrites an
existing daily note.

Usage:  python3 link_audit.py        # first, to refresh audit.json
        python3 gen_daily.py [/path/to/vault]
"""
import os, re, json, glob, sys

HERE = os.path.dirname(__file__)
VAULT = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath(
    os.path.join(HERE, "..", "..", "..", "..", "..", "cbrain"))
NOTES = os.path.join(VAULT, "notes")
DAILY = os.path.join(VAULT, "daily reports")
WEATHER = os.path.join(VAULT, "weather data")
STUB = "_Stub — backfilled during vault clean-up. Meetings for the day are listed below._"

audit = json.load(open(os.path.join(HERE, "audit.json")))
dates = sorted(t for t in audit["missing_targets"] if re.fullmatch(r'\d{8}', t))

created = 0
for ymd in dates:
    out = os.path.join(DAILY, f"{ymd}.md")
    if os.path.exists(out):
        continue
    iso = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}"
    meetings = [f"- [[{os.path.splitext(os.path.basename(m))[0]}]]"
                for m in sorted(glob.glob(os.path.join(NOTES, f"{ymd}-*.md")))]
    weather = [f"- [[{os.path.splitext(os.path.basename(w))[0]}]]"
               for w in sorted(glob.glob(os.path.join(WEATHER, f"{ymd}-*.md")))]
    body = ["---", "type: daily", f"date: {iso}", "---", f"# Daily Report — {iso}", "",
            "## Summary", STUB, "", "## Meetings"]
    body += meetings or ["_No meeting notes recorded for this day._"]
    if weather:
        body += ["", "## Weather"] + weather
    open(out, "w", encoding="utf-8").write("\n".join(body) + "\n")
    created += 1

print(f"created {created} daily stubs of {len(dates)} referenced dates "
      f"(existing left untouched)")
