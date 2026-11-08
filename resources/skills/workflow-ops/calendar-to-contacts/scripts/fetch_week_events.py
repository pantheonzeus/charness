#!/usr/bin/env python3
"""Fetch a week's calendar events from macOS Calendar.app (EventKit) as JSON.

Run via uv so PyObjC + EventKit install on demand:

  uv run --with pyobjc-framework-EventKit python3 fetch_week_events.py --this-week \
    > /tmp/week-events.json

Reads whatever calendars Calendar.app has synced (add your Google account in
System Settings -> Internet Accounts first). On the first run macOS prompts for
Calendar access; if denied, grant it in System Settings -> Privacy & Security ->
Calendars and re-run.

Output: JSON {"range": {...}, "events": [{uid, title, start, end, all_day,
calendar, attendees: [{name, email, type, is_current_user, is_organizer}]}]}.
No writes.
"""
import argparse
import datetime
import json
import sys

try:
    from Foundation import NSDate, NSRunLoop
    import EventKit
    from EventKit import EKEventStore
except Exception as e:  # pragma: no cover
    sys.stderr.write(
        "ERROR: could not import EventKit/Foundation. Run this script via:\n"
        "  uv run --with pyobjc-framework-EventKit python3 %s\n(%s)\n" % (sys.argv[0], e)
    )
    sys.exit(2)

EK_ENTITY_EVENT = getattr(EventKit, "EKEntityTypeEvent", 0)
EK_ROOM = getattr(EventKit, "EKParticipantTypeRoom", 3)
EK_RESOURCE = getattr(EventKit, "EKParticipantTypeResource", 4)
PTYPE_NAME = {
    getattr(EventKit, "EKParticipantTypeUnknown", 0): "unknown",
    getattr(EventKit, "EKParticipantTypePerson", 1): "person",
    getattr(EventKit, "EKParticipantTypeGroup", 2): "group",
    EK_ROOM: "room",
    EK_RESOURCE: "resource",
}


def request_access(store):
    """Request Calendar access, spinning the runloop until the async handler fires."""
    state = {"granted": None}

    def handler(granted, err):
        state["granted"] = bool(granted)

    if hasattr(store, "requestFullAccessToEventsWithCompletion_"):
        store.requestFullAccessToEventsWithCompletion_(handler)  # macOS 14+
    else:
        store.requestAccessToEntityType_completion_(EK_ENTITY_EVENT, handler)

    rl = NSRunLoop.currentRunLoop()
    deadline = NSDate.dateWithTimeIntervalSinceNow_(30)
    while state["granted"] is None and NSDate.date().compare_(deadline) < 0:
        rl.runMode_beforeDate_(
            "NSDefaultRunLoopMode", NSDate.dateWithTimeIntervalSinceNow_(0.1)
        )
    return state["granted"]


def week_bounds(which, start, end):
    now = datetime.datetime.now()
    if start and end:
        s = datetime.datetime.fromisoformat(start)
        e = datetime.datetime.fromisoformat(end) + datetime.timedelta(days=1)
    else:
        monday = (now - datetime.timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        if which == "next-week":
            monday += datetime.timedelta(days=7)
        s = monday
        e = monday + datetime.timedelta(days=7)
    return s, e


def nsdate(dt):
    return NSDate.dateWithTimeIntervalSince1970_(dt.timestamp())


def to_iso(ns):
    if ns is None:
        return None
    return datetime.datetime.fromtimestamp(ns.timeIntervalSince1970()).isoformat()


def email_from(participant):
    url = participant.URL()
    if url is None:
        return None
    s = str(url)
    return s[7:] if s.lower().startswith("mailto:") else s


def participant_dict(p, is_organizer=False):
    if p is None:
        return None
    ptype = p.participantType()
    return {
        "name": (p.name() or None),
        "email": email_from(p),
        "type": PTYPE_NAME.get(ptype, str(ptype)),
        "is_current_user": bool(p.isCurrentUser()),
        "is_organizer": is_organizer,
    }


def main():
    ap = argparse.ArgumentParser(description="Fetch a week of macOS calendar events as JSON")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--this-week", action="store_true", help="current Mon-Sun (default)")
    g.add_argument("--next-week", action="store_true")
    ap.add_argument("--start", help="YYYY-MM-DD (with --end, overrides week selection)")
    ap.add_argument("--end", help="YYYY-MM-DD inclusive")
    args = ap.parse_args()

    which = "next-week" if args.next_week else "this-week"
    s, e = week_bounds(which, args.start, args.end)

    store = EKEventStore.alloc().init()
    granted = request_access(store)
    if not granted:
        sys.stderr.write(
            "ERROR: Calendar access not granted.\n"
            "Grant it in System Settings -> Privacy & Security -> Calendars\n"
            "(enable access for the terminal/app running this), then re-run.\n"
        )
        sys.exit(3)

    predicate = store.predicateForEventsWithStartDate_endDate_calendars_(
        nsdate(s), nsdate(e), None
    )
    ek_events = store.eventsMatchingPredicate_(predicate) or []

    events = []
    for ev in ek_events:
        attendees = []
        organizer = ev.organizer()
        org_email = email_from(organizer) if organizer else None
        if organizer is not None:
            attendees.append(participant_dict(organizer, is_organizer=True))
        for p in (ev.attendees() or []):
            # avoid duplicating the organizer if they also appear in attendees
            if org_email and email_from(p) and email_from(p).lower() == org_email.lower():
                continue
            attendees.append(participant_dict(p))
        cal = ev.calendar()
        events.append({
            "uid": ev.calendarItemIdentifier(),
            "title": (ev.title() or "(untitled)"),
            "start": to_iso(ev.startDate()),
            "end": to_iso(ev.endDate()),
            "all_day": bool(ev.isAllDay()),
            "calendar": (cal.title() if cal else None),
            "attendees": [a for a in attendees if a],
        })

    events.sort(key=lambda x: x["start"] or "")
    json.dump({
        "range": {"start": s.isoformat(), "end": e.isoformat(), "which": which},
        "count": len(events),
        "events": events,
    }, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    sys.stderr.write("Fetched %d event(s) for %s (%s .. %s)\n" % (len(events), which, s.date(), e.date()))


if __name__ == "__main__":
    main()
