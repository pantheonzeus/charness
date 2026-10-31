# Build Morning Briefing — headless workflow

Runs once every weekday morning (via `scripts/run_morning_briefing.sh` under launchd),
or by hand. Imports today's calendar + new mail into the vault, writes a prep block onto
each of today's meeting notes, and builds the interactive HTML the wrapper then opens.

This is the **judgment half** — it reuses the deterministic builders from the calendar
and mail skills and adds the semantic prep. Vault-only: **no web calls.**

Set once per run:
```bash
DATE=$(date +%Y-%m-%d)          # or pass an explicit YYYY-MM-DD
DATE_COMPACT=${DATE//-/}
REPO="$(git rev-parse --show-toplevel)"
VAULT=$REPO/cbrain
CAL=$REPO/resources/skills/workflow-ops/calendar-to-contacts
MAIL=$REPO/resources/skills/workflow-ops/mail-to-conversations
MB=$REPO/resources/skills/workflow-ops/morning-briefing
SELF=${CHARNESS_SELF_EMAIL:-$(git -C "$REPO" config --get charness.selfEmail)}   # set once: git config charness.selfEmail you@yourcompany.com
```

Guardrails (this edits the vault unattended): **append never overwrite** · link only
**existing** people/meetings · vault-only, no web · idempotent — safe to re-run the same day.

## Step 1 — Import today's calendar

Call the MCP **`list_calendar_events`** tool for **today's local-day window**
(`timeMin` = today 00:00, `timeMax` = today 23:59, local tz) and save the raw tool JSON to
`/tmp/mb-events.json`. Then adapt + build (see
[calendar-to-contacts/workflows/mcp-run.md](../../calendar-to-contacts/workflows/mcp-run.md)
for the contract and the MCP-unavailable fallback):
```bash
python3 $CAL/scripts/mcp_events_to_sources.py /tmp/mb-events.json > /tmp/mb-day.json
python3 $CAL/scripts/build_contacts.py --sources /tmp/mb-day.json --vault "$VAULT" \
  --domain-map "$(python3 $REPO/scripts/employer.py path calendar-to-contacts/domain_map.yaml)" --self-email "$SELF"
```
This creates/updates `notes/$DATE_COMPACT-*.md` (`type: meeting`) + attendee contacts.
Existing notes are skipped, existing contacts appended — never overwritten.

## Step 2 — Import new relevant mail

Call the MCP **`search_gmail_messages`** tool with the partner-domain query (mirror
the employer pack's `mail-to-conversations/domain_map.yaml`) restricted to the last couple of days
(`newer_than:2d`), save to `/tmp/mb-mail.json`, then:
```bash
python3 $MAIL/scripts/mcp_gmail_to_sources.py /tmp/mb-mail.json --query "$Q" > /tmp/mb-mail-src.json
python3 $MAIL/scripts/build_conversations.py --sources /tmp/mb-mail-src.json --vault "$VAULT" \
  --domain-map "$(python3 $REPO/scripts/employer.py path mail-to-conversations/domain_map.yaml)" --exclude-noise --self-email "$SELF"
```
Only mail with no existing `Mail/msgs/<…>.md` note is written — that filename dedup **is**
the "not yet imported" check. See
[mail-to-conversations/workflows/mcp-run.md](../../mail-to-conversations/workflows/mcp-run.md).

## Step 3 — Per-meeting prep (vault-only)

For **each** `notes/$DATE_COMPACT-*.md`:
1. Read its title (`# Meeting — <title>`), time (`**Time:**`), description (`## Notes`),
   and attendees (`## Attendees` wikilinks).
2. For each attendee, harvest from the vault (person-dossier **recall** mode — no web):
   their `Clients/<Name>.md` (company, role/headline, status), the topic anchors in
   `projects/` they link to, and recent `## Mail` threads. Note who is internal
   (your own company domain) vs external.
3. Synthesise the prep. **Shared themes** = topic anchors / accounts the attendees
   converge on (the reason to link them). **Prep guide** = concrete talking points and
   open threads pulled from their mail/meeting history. **Smart questions** = 2–3 sharp
   openers.
4. **Append** to that note's `## My Notes` section (never overwrite existing content) a
   block in exactly this shape — the HTML generator parses the JSON, the rendered markdown
   below it is for reading in Obsidian:

   ```
   ### Morning Briefing Prep — <DATE>
   <!--mb-prep
   {
     "time": "13:00",
     "title": "GER Leadership Meeting",
     "description": "one-paragraph cleaned description",
     "participants": [
       {"name": "Jane Doe", "role": "Head of X", "company": "Your Company"}
     ],
     "shared_themes": ["AI SDLC", "Team Germany"],
     "prep_guide": ["talking point", "open thread from mail"],
     "open_threads": ["RE: <subject> — awaiting reply since <date>"],
     "smart_questions": ["question one", "question two"]
   }
   mb-prep-->

   **Participants:** …
   **Shared themes:** …
   **Prep guide:**
   - …
   **Smart questions:**
   - …
   ```
   Keep the JSON valid (double quotes, no trailing commas). Omit a key's array if empty.
   If a meeting note already contains an `mb-prep` block for today, skip it (idempotent).

## Step 4 — Build the HTML

```bash
python3 $MB/scripts/build_briefing_html.py --date "$DATE_COMPACT"
```
Reads today's meeting notes' prep blocks + the two newest `output/podcasts/*.m4a`
(title from each sibling `.summary.md`), writes the page content
`output/morning-briefing/$DATE_COMPACT.md` (`template: briefing`) and renders it through the
reading-pages skill to `output/morning-briefing/$DATE_COMPACT.html`. The wrapper opens it.
Never hand-edit or hand-build the HTML: content goes in the meeting notes' `mb-prep` blocks.

## Step 5 — Log to the daily report

Append one line under `## Knowledge Graph` in `cbrain/daily reports/$DATE_COMPACT.md`
(create the file with the standard `type: daily` frontmatter + `## Summary` / `## Meetings`
/ `## Knowledge Graph` sections if it doesn't exist — match the format of an existing
daily report). E.g.:
```
- Morning briefing built: imported N meetings + M new mails, prepped each meeting, HTML at output/morning-briefing/<DATE>.html.
```

## Step 6 — Write the handoff result (Charter §5)

Last action of the run. Write `output/.runs/$DATE_COMPACT-morning-briefing/children/build/RESPONSE.md`
(relative to the repo root): meetings imported, mails imported, each meeting prepped or skipped + why,
HTML path, and any failure (e.g. MCP down). Write it even on a no-meeting day. Use only `[x]` boxes
or none — never `[ ]`. The wrapper reopens this file; your inline reply is not the record.
