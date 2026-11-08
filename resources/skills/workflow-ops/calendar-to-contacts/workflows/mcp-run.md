# Weekly Run — via the Google Workspace MCP server (primary)

Capture a week of meetings into contacts + meeting notes, reading Calendar through the
shared MCP server. One-time server setup + auth: [resources/mcp/google-workspace.md](../../../../mcp/google-workspace.md).

Set once per run:
```bash
SKILL=resources/skills/workflow-ops/calendar-to-contacts
VAULT=cbrain   # run from the repo root
```

## Step 1: Read the week from MCP

Confirm the server is connected (`/mcp` lists `workspace-mcp` with Calendar tools), then
call the **`list_calendar_events`** tool for the target window (default: this week,
Mon–Sun) and **save the raw tool JSON** to `/tmp/mcp-events.json`.

> **Single-day window (morning briefing).** For a one-day pull (used by the
> [[morning-briefing]] skill), scope the window to today: set the MCP call's `timeMin` to
> today 00:00 and `timeMax` to today 23:59 (local tz). The adapter + `build_contacts.py`
> are day/week-agnostic — they process whatever events the JSON contains — so no builder
> change is needed. The OAuth fallback takes an explicit range: `--start <YYYY-MM-DD>
> --end <YYYY-MM-DD>` with both set to today.

- The tool result is read-only.
- If `/mcp` doesn't list the server, start it (`./scripts/start-google-workspace-mcp.sh`)
  or use the fallback in Step 1b.

## Step 2: Adapt to the builder contract

```bash
python3 $SKILL/scripts/mcp_events_to_sources.py /tmp/mcp-events.json > /tmp/week-events.json
```
This maps the tool output into the exact `{events:[…]}` shape `build_contacts.py` expects
(same contract the fetch scripts emit). Adapted event count prints to stderr.

> **First-run validation:** the adapter assumes `list_calendar_events` returns
> Google-Calendar-API-shaped events. Skim `/tmp/week-events.json` once — if titles /
> attendees / start times look wrong, the tool's real shape differs; adjust
> `norm_event` in the adapter. This is the one thing only the live server can confirm.

## Step 3: Dry run (writes nothing)

```bash
python3 $SKILL/scripts/build_contacts.py --sources /tmp/week-events.json --vault "$VAULT" \
  --domain-map "$(python3 scripts/employer.py path calendar-to-contacts/domain_map.yaml)" --self-email you@yourcompany.com --dry-run
```
Shows every planned CREATE/APPEND. Tune the employer pack's `calendar-to-contacts/domain_map.yaml` if a company is
mis-inferred, or `--self-email` if your address differs.

## Step 4: Build

```bash
python3 $SKILL/scripts/build_contacts.py --sources /tmp/week-events.json --vault "$VAULT" \
  --domain-map "$(python3 scripts/employer.py path calendar-to-contacts/domain_map.yaml)" --self-email you@yourcompany.com
```

## Step 5: Verify in Obsidian

Same as the fallback run — see [weekly-run.md](weekly-run.md) Step 5. Re-running the same
week is idempotent.

## Step 1b: Fallback (MCP unavailable)

Replace Steps 1–2 with either fetch script (both emit the same `/tmp/week-events.json`),
then continue at Step 3:
```bash
uv run --with google-api-python-client --with google-auth-oauthlib --with google-auth \
  python3 $SKILL/scripts/fetch_gcal_oauth.py --this-week > /tmp/week-events.json   # OAuth
# or macOS Calendar.app:
uv run --with pyobjc-framework-EventKit python3 $SKILL/scripts/fetch_week_events.py --this-week > /tmp/week-events.json
```
Fallback setup: [gcal-api-auth.md](gcal-api-auth.md) (OAuth) · [setup.md](setup.md) (EventKit).

## Parity check (do once, after first live auth)

Prove the MCP path matches the old path for the same window:
```bash
# same week, both sources → diff the builder inputs
python3 $SKILL/scripts/mcp_events_to_sources.py /tmp/mcp-events.json > /tmp/mcp-week.json
uv run --with google-api-python-client --with google-auth-oauthlib --with google-auth \
  python3 $SKILL/scripts/fetch_gcal_oauth.py --this-week > /tmp/oauth-week.json
diff <(jq -S '.events' /tmp/mcp-week.json) <(jq -S '.events' /tmp/oauth-week.json)
```
Field-equivalent events ⇒ the migration is correct.
