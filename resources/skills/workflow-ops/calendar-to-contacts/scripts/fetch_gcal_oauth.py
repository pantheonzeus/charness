#!/usr/bin/env python3
"""Fetch a week's Google Calendar events via the Calendar API (OAuth) → JSON.

Calendar.app-free alternative to fetch_week_events.py. Same JSON output shape, so
build_contacts.py consumes it unchanged. Browser-consent OAuth like the notebooklm login.

Run via uv (deps install on demand):

  uv run --with google-api-python-client --with google-auth-oauthlib --with google-auth \
    python3 fetch_gcal_oauth.py --start 2026-07-06 --end 2026-07-10 \
    --credentials ~/.config/calendar-to-contacts/credentials.json \
    > /tmp/workweek-events.json

First run opens a browser for Google consent (readonly scope) and caches a token;
later runs are non-interactive. Needs a Google Cloud OAuth *desktop* client
(credentials.json) — see workflows/gcal-api-auth.md.

Output: {"range":{...},"count":N,"events":[{uid,title,start,end,all_day,calendar,
attendees:[{name,email,type,is_current_user,is_organizer}]}]}
"""
import argparse
import datetime
import json
import os
import sys
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
DEFAULT_DIR = Path(os.path.expanduser("~/.config/calendar-to-contacts"))


def _imports():
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        return Credentials, Request, InstalledAppFlow, build
    except Exception as e:
        sys.stderr.write(
            "ERROR: Google libs missing. Run via:\n"
            "  uv run --with google-api-python-client --with google-auth-oauthlib "
            "--with google-auth python3 %s ...\n(%s)\n" % (sys.argv[0], e)
        )
        sys.exit(2)


def week_bounds(which, start, end):
    now = datetime.datetime.now()
    if start and end:
        s = datetime.datetime.fromisoformat(start)
        e = datetime.datetime.fromisoformat(end) + datetime.timedelta(days=1)
    else:
        monday = (now - datetime.timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0)
        if which == "next-week":
            monday += datetime.timedelta(days=7)
        s, e = monday, monday + datetime.timedelta(days=7)
    return s, e


def get_credentials(credentials_path, token_path):
    Credentials, Request, InstalledAppFlow, _ = _imports()
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                sys.stderr.write(
                    "ERROR: OAuth client not found at %s\n"
                    "Create a Google Cloud OAuth 'desktop' client and save its JSON there.\n"
                    "See workflows/gcal-api-auth.md.\n" % credentials_path)
                sys.exit(4)
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            sys.stderr.write("Opening browser for Google consent (readonly calendar)...\n")
            # authorization_prompt_message="" keeps stdout clean (JSON only); the library
            # otherwise prints "Please visit this URL..." to stdout and corrupts the output.
            creds = flow.run_local_server(port=0, open_browser=True,
                                          authorization_prompt_message="")
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())
        try:
            os.chmod(str(token_path), 0o600)
        except OSError:
            pass
    return creds


def norm_event(ev, cal_id):
    def dt(node):
        return node.get("dateTime") or node.get("date")
    start_node = ev.get("start", {})
    all_day = "date" in start_node and "dateTime" not in start_node
    org = ev.get("organizer", {}) or {}
    org_email = (org.get("email") or "").lower()
    attendees = []
    if org.get("email"):
        attendees.append({
            "name": org.get("displayName"),
            "email": org.get("email"),
            "type": "person",
            "is_current_user": bool(org.get("self")),
            "is_organizer": True,
        })
    for a in ev.get("attendees", []) or []:
        em = (a.get("email") or "")
        if em.lower() == org_email and org.get("email"):
            continue  # already added as organizer
        attendees.append({
            "name": a.get("displayName"),
            "email": a.get("email"),
            "type": "resource" if a.get("resource") else "person",
            "is_current_user": bool(a.get("self")),
            "is_organizer": bool(a.get("organizer")),
        })
    return {
        "uid": ev.get("id"),
        "title": ev.get("summary") or "(untitled)",
        "start": dt(start_node),
        "end": dt(ev.get("end", {})),
        "all_day": all_day,
        "calendar": cal_id,
        "location": ev.get("location") or "",
        "description": ev.get("description") or "",   # the event "notes" field
        "attendees": attendees,
    }


def main():
    ap = argparse.ArgumentParser(description="Fetch a week of Google Calendar events via API")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--this-week", action="store_true", help="current Mon-Sun (default)")
    g.add_argument("--next-week", action="store_true")
    ap.add_argument("--start", help="YYYY-MM-DD (with --end, overrides week selection)")
    ap.add_argument("--end", help="YYYY-MM-DD inclusive")
    ap.add_argument("--calendar", default="primary", help="calendarId (default: primary)")
    ap.add_argument("--credentials", default=str(DEFAULT_DIR / "credentials.json"))
    ap.add_argument("--token", default=str(DEFAULT_DIR / "token.json"))
    args = ap.parse_args()

    _, _, _, build = _imports()
    which = "next-week" if args.next_week else "this-week"
    s, e = week_bounds(which, args.start, args.end)

    creds = get_credentials(Path(os.path.expanduser(args.credentials)),
                            Path(os.path.expanduser(args.token)))
    service = build("calendar", "v3", credentials=creds, cache_discovery=False)

    time_min = s.astimezone().isoformat()
    time_max = e.astimezone().isoformat()
    events, page_token = [], None
    while True:
        resp = service.events().list(
            calendarId=args.calendar, timeMin=time_min, timeMax=time_max,
            singleEvents=True, orderBy="startTime", maxResults=250,
            pageToken=page_token).execute()
        for ev in resp.get("items", []):
            events.append(norm_event(ev, args.calendar))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    events.sort(key=lambda x: x["start"] or "")
    json.dump({
        "range": {"start": s.isoformat(), "end": e.isoformat(), "which": which},
        "count": len(events),
        "events": events,
    }, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    sys.stderr.write("Fetched %d event(s) from '%s' (%s .. %s)\n"
                     % (len(events), args.calendar, s.date(), e.date()))


if __name__ == "__main__":
    main()
