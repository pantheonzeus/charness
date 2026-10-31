---
id: calendar-to-contacts
aliases: [calendar-to-contacts]
name: "Weekly Calendar → Contacts & Meeting Notes"
category: workflow-ops
description: Read this week's Google Calendar (via the Google Workspace MCP server; EventKit/OAuth-script fallback) and create a contact note per attendee + a meeting note per event in the vault, each with an empty Notes section to fill afterwards.
triggers: [meetings of the week, this week's meetings, calendar contacts, create contacts from calendar, log my week, weekly meetings, calendar to contacts, who did I meet]
tags: [workflow-ops, calendar, contacts, meetings, mcp, google-calendar, eventkit, obsidian, automation]
related: ["[[contact-meeting-capture]]", "[[relationship-intro-pattern]]"]
requires:
  tools: [bash, python]
  mcp: ["workspace-mcp (google_workspace_mcp) — Gmail+Calendar; see resources/mcp/google-workspace.md"]
  python: [pyobjc-framework-EventKit, google-api-python-client, google-auth-oauthlib, google-auth]  # fallback path only
  obsidian-plugins: [Dataview]
environment: "Primary: Google Workspace MCP server (`list_calendar_events` → adapter → build_contacts.py); any OS, one shared local server, see resources/mcp/google-workspace.md. Fallback (offline/degraded): the OAuth script (`fetch_gcal_oauth.py`, needs a Google Cloud desktop client) or macOS EventKit (`fetch_week_events.py`, Calendar.app + TCC permission). All three feed the same JSON contract; writes to the vault (Clients/, notes/)."
scripts: [scripts/mcp_events_to_sources.py, scripts/build_contacts.py, scripts/fetch_gcal_oauth.py, scripts/fetch_week_events.py]
workflows: [workflows/mcp-run.md, workflows/setup.md, workflows/gcal-api-auth.md, workflows/weekly-run.md]
schema: [schema/domain_map.example.yaml]
status: active
version: 8
created: 2026-07-05
updated: 2026-10-23
vault_writes: ["cbrain/Clients/*", "cbrain/notes/[0-9]*"]
---

# Weekly Calendar → Contacts & Meeting Notes

Turn this week's calendar meetings into vault artefacts you can annotate: **one contact note per attendee** (name, email, an inferred headline) and **one meeting note per event**, bi-directionally linked. Reuses the `contact-meeting-capture` conventions and is **append-only** — it never rewrites notes you've already edited.

## What This Does

1. **Reads the week's events** from the Google Workspace MCP server (`list_calendar_events`); an OAuth script or macOS EventKit are drop-in fallbacks.
2. **Extracts attendees** (name + email), skipping meeting rooms/resources and yourself.
3. **Creates contact notes** → `Clients/<Name>.md` with `**Company:**` (inferred from the email domain), `**Email:**`, `**Headline:**` (`Met in "<title>" (<date>) · <Company>`), `**Status:** New (from calendar)`, an empty `## Notes`, and a `## Meetings` link. Everyone incl. colleagues.
4. **Creates meeting notes** → `notes/<YYYYMMDD>-<slug>.md` with the attendees as `[[wikilinks]]`. **A meeting is recorded whether or not it has a calendar description** (recorded if it has ≥1 attendee *or* a description; only pure solo blocks with no notes are skipped). When the event has a description, its **cleaned notes are folded into `## Notes`** (HTML stripped, dial-in/join boilerplate removed); `## My Notes` stays empty for you.
5. **Dedupes** — existing contacts (matched by email) get the new meeting appended, not duplicated; existing meeting notes are skipped. Re-running is idempotent.

## Reading the calendar — one contract, three sources

The read layer produces one JSON shape (`{events:[…]}`); `build_contacts.py` is identical downstream regardless of which produced it.

| Path | Source | Setup | Use when |
|------|--------|-------|----------|
| **MCP** (primary) | `list_calendar_events` → `scripts/mcp_events_to_sources.py` | Google Workspace MCP server running (once) — [resources/mcp/google-workspace.md](../../../mcp/google-workspace.md) | Default. Any OS, one shared server for Calendar + Mail |
| **OAuth script** (fallback) | `scripts/fetch_gcal_oauth.py` | Google Cloud OAuth desktop client (`credentials.json`) + browser consent | MCP server down, or a quick offline one-shot |
| **EventKit** (fallback) | `scripts/fetch_week_events.py` | Google account in Calendar.app + Calendar (TCC) permission | macOS + Calendar.app, no Google Cloud project |

## Prerequisites

- **Google Workspace MCP server** running and connected (`/mcp` shows `workspace-mcp` with Calendar tools). One-time setup + auth: [resources/mcp/google-workspace.md](../../../mcp/google-workspace.md).
- **`uv`** installed (`~/.local/bin/uv`) — for the launcher and the fallback scripts (their deps install on demand).

## Quick Start (MCP — primary)

```bash
SKILL=resources/skills/workflow-ops/calendar-to-contacts
VAULT=cbrain   # the live Obsidian vault root; run from the repo root

# 1. Ask the MCP server for this week's events (agent calls the `list_calendar_events`
#    tool for the Mon–Sun window) and save the raw tool JSON to /tmp/mcp-events.json.
# 2. Adapt it into the builder's contract:
python3 $SKILL/scripts/mcp_events_to_sources.py /tmp/mcp-events.json > /tmp/week-events.json

# 3. Preview (writes nothing), then build:
python3 $SKILL/scripts/build_contacts.py --sources /tmp/week-events.json --vault "$VAULT" \
  --domain-map "$(python3 scripts/employer.py path calendar-to-contacts/domain_map.yaml)" --self-email you@yourcompany.com --dry-run
python3 $SKILL/scripts/build_contacts.py --sources /tmp/week-events.json --vault "$VAULT" \
  --domain-map "$(python3 scripts/employer.py path calendar-to-contacts/domain_map.yaml)" --self-email you@yourcompany.com
```

`build_contacts.py` flags: `--dry-run` · `--self-email <you@domain>` (excluded from contacts) · `--domain-map <yaml>`.
Full call sequence + fallbacks: [workflows/mcp-run.md](workflows/mcp-run.md).

### Fallback (MCP unavailable)
Swap step 1–2 for one fetch script, then run `build_contacts.py` unchanged:
```bash
uv run --with google-api-python-client --with google-auth-oauthlib --with google-auth \
  python3 $SKILL/scripts/fetch_gcal_oauth.py --this-week > /tmp/week-events.json   # OAuth script
# or, macOS Calendar.app:
uv run --with pyobjc-framework-EventKit python3 $SKILL/scripts/fetch_week_events.py --this-week > /tmp/week-events.json
```
`fetch_*` flags: `--this-week` (default) · `--next-week` · `--start YYYY-MM-DD --end YYYY-MM-DD`.

## Workflow Routing

| Task | Workflow |
|------|----------|
| Run the weekly capture via MCP (primary) | [workflows/mcp-run.md](workflows/mcp-run.md) |
| MCP server setup + auth (shared with Mail) | [resources/mcp/google-workspace.md](../../../mcp/google-workspace.md) |
| Fallback setup — EventKit (Calendar.app + permission) | [workflows/setup.md](workflows/setup.md) |
| Fallback setup — Google Calendar API (OAuth client + consent) | [workflows/gcal-api-auth.md](workflows/gcal-api-auth.md) |
| Fallback run (fetch script → review → build) | [workflows/weekly-run.md](workflows/weekly-run.md) |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/mcp_events_to_sources.py` | **(primary)** MCP `list_calendar_events` JSON → the `{events:[…]}` builder contract |
| `scripts/build_contacts.py` | JSON → `Clients/` contacts + `notes/` meeting notes (dedup, domain→company, append-only, `--dry-run`) |
| `scripts/fetch_gcal_oauth.py` | *(fallback)* Google Calendar API (OAuth) read → same JSON, Calendar.app-free (read-only) |
| `scripts/fetch_week_events.py` | *(fallback)* EventKit read (macOS Calendar.app) → same JSON (read-only) |

## Notes & Gotchas

- **EventKit sees only synced calendars** — if the Google account isn't in Calendar.app, you get zero events.
- **Permission is per host process** — the prompt attaches to whatever runs the script; denial needs a manual toggle in System Settings.
- **Company inference** is heuristic (email domain → title-cased **org label**, *public-suffix aware*: `warwick.ac.uk`→Warwick, `acme.co.uk`→Acme — not "Ac"/"Co"). Override known domains in `schema/domain_map.yaml` (gitignored — start from `domain_map.example.yaml`); add any new multi-label ccTLD to `_MULTI_SUFFIX` in `build_contacts.py`. Personal providers (gmail, outlook, …) leave Company blank **regardless of ccTLD** — `outlook.es` and `gmail.co.uk` too (matched by org label in `_PERSONAL_LABELS`).
- **Attendee "names" that are really email local-parts** (`jane.doe`) are humanized to `Jane Doe` — never used verbatim as the note filename (`_LOCALPART_RE` guard in `display_name`).
- **Distribution lists / shared calendars / functional mailboxes are NOT people** (v6) — `kept()` drops any attendee whose local-part carries a functional token (`purchase-orders`, `team-`, `-calendar`, `info`, `events`, `supervisors`, …, via `_FUNCTIONAL_LOCAL_RE`, word-boundary-anchored so real names like `jane.doe`/`steam.roller` are safe) **or** whose domain is `*.onmicrosoft.com` (M365 tenant routing, e.g. `projectteam@…onmicrosoft.com`). This stops the junk contacts the earlier version minted (`Team Germany.md`, `Germany Calendar.md`, `Supervisors Global.md`).
- **Append-only** on existing contact notes — only a `## Meetings` link is added; your annotations are never touched.
- **Attendees without an email are skipped** (needed for dedup + company); solo blocks with no other humans produce no meeting note.
