#!/usr/bin/env python3
"""Adapt Google Workspace MCP `list_calendar_events` output → build_contacts.py JSON.

The MCP server (taylorwilsdon/google_workspace_mcp) is the primary connection now;
this adapter maps its calendar tool output into the exact `{range,count,events:[...]}`
shape build_contacts.py consumes — the same contract fetch_gcal_oauth.py emits, so
the builder is unchanged. See ../../../../mcp/google-workspace.md.

Flow:
  1. Ask the MCP tool for the window, save its JSON:  … > /tmp/mcp-events.json
  2. python3 mcp_events_to_sources.py /tmp/mcp-events.json > /tmp/week-events.json
  3. build_contacts.py --sources /tmp/week-events.json …

Input: the raw MCP tool result — a JSON list of event objects, or an object with an
`events`/`items` array. Events are assumed Google-Calendar-API shaped (`start`,`end`,
`organizer`,`attendees`,`summary`,…) because the server is a thin wrapper. VALIDATE
this assumption against a captured live response the first time you authorize — if the
tool returns a flatter/renamed shape, adjust `norm_event` accordingly (that is the one
thing that can only be pinned down with the live server).

Reads a file arg or stdin; writes builder JSON to stdout.
"""
import argparse
import json
import sys


def norm_event(ev):
    """Google-Calendar-API event → build_contacts.py event. Mirrors fetch_gcal_oauth.py."""
    def dt(node):
        return (node or {}).get("dateTime") or (node or {}).get("date")
    start_node = ev.get("start", {}) or {}
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
        "calendar": ev.get("organizer", {}).get("email") or "primary",
        "location": ev.get("location") or "",
        "description": ev.get("description") or "",
        "attendees": attendees,
    }


def extract_items(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("events", "items", "results"):
            if isinstance(data.get(key), list):
                return data[key]
    sys.stderr.write("ERROR: could not find an events array in the MCP output "
                     "(expected a list, or an object with events/items/results).\n")
    sys.exit(2)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", nargs="?", help="MCP tool JSON (default: stdin)")
    args = ap.parse_args()

    raw = open(args.input).read() if args.input else sys.stdin.read()
    events = [norm_event(ev) for ev in extract_items(json.loads(raw))]
    events.sort(key=lambda x: x["start"] or "")

    json.dump({"range": {}, "count": len(events), "events": events},
              sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    sys.stderr.write("Adapted %d event(s) → build_contacts.py schema\n" % len(events))


if __name__ == "__main__":
    main()
