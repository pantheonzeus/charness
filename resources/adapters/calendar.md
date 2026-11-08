# calendar — capability contract

## Operations (used today)
| Operation | Used by | Notes |
|---|---|---|
| `list_events(start, end) → [Event]` | meeting-prep sync (today + next workday), calendar-to-contacts (week), morning-briefing (today) | single instances, ordered by start |

No skill writes to a calendar.

## Normalized shape — `output/meetings/events.json` `{events:[…]}`
`uid, title, start, end, all_day, calendar, location, description, link (video join), declined, attachments[file_ref], attendees[{name, email, type, is_organizer, is_current_user}]`

## Implementations
| Adapter | Where | Auth |
|---|---|---|
| `google` | `meeting-prep-loop/scripts/sync.py` (REST events.list, `hangoutLink` / `conferenceData` → `link`); `calendar-to-contacts/scripts/fetch_gcal_oauth.py` (REST) + `mcp_events_to_sources.py` (workspace-mcp → shape) | `~/.config/calendar-to-contacts/token.json` |
| `eventkit` | `calendar-to-contacts/scripts/fetch_week_events.py` (macOS Calendar.app) | none: reads any account added to Calendar.app, Exchange/M365 included. The day-one fallback at a new employer |
| `m365` | **stub — not built.** Notes (unverified): `GET /me/calendarView?startDateTime&endDateTime`, `onlineMeeting.joinUrl` → `link`, `attendees[].status.response` → `declined`. | |
