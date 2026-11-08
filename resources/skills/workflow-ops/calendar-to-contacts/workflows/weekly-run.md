# Weekly Run Workflow

Run this to capture a week of meetings into contacts + meeting notes. Assumes [setup.md](setup.md) is done.

Set once per run:
```bash
SKILL=resources/skills/workflow-ops/calendar-to-contacts
VAULT=cbrain   # run from the repo root
```

## Step 1: Fetch the week (read-only)

```bash
uv run --with pyobjc-framework-EventKit python3 $SKILL/scripts/fetch_week_events.py --this-week \
  > /tmp/week-events.json
```
Week range flags: `--this-week` (default) · `--next-week` · `--start YYYY-MM-DD --end YYYY-MM-DD`.
The script prints the event count to stderr. If access is denied, see setup.md Step 2.

## Step 2: Review (optional but recommended on first run)

Skim the JSON to sanity-check attendees/emails before writing:
```bash
python3 -c "import json;d=json.load(open('/tmp/week-events.json'));[print(e['start'][:16], '|', e['title'], '|', ', '.join(a.get('email') or a.get('name','?') for a in e['attendees'])) for e in d['events']]"
```

## Step 3: Dry run (writes nothing)

```bash
python3 $SKILL/scripts/build_contacts.py --sources /tmp/week-events.json --vault "$VAULT" \
  --domain-map "$(python3 scripts/employer.py path calendar-to-contacts/domain_map.yaml)" --dry-run
```
Shows every planned CREATE/APPEND and a summary (new vs existing contacts, meeting notes). Adjust the employer pack's `calendar-to-contacts/domain_map.yaml` if a company is mis-inferred, or `--self-email` if your address differs.

## Step 4: Build

```bash
python3 $SKILL/scripts/build_contacts.py --sources /tmp/week-events.json --vault "$VAULT" \
  --domain-map "$(python3 scripts/employer.py path calendar-to-contacts/domain_map.yaml)"
```

## Step 5: Verify in Obsidian

- `Clients/<Name>.md` — new people have `**Email:**`, `**Company:**`, `**Headline:**`, an empty `## Notes`, and a `## Meetings` link. Existing contacts gained a `## Meetings` link only (annotations untouched).
- `notes/<YYYYMMDD>-<slug>.md` — one per meeting, attendees as `[[wikilinks]]` back to the contacts, empty `## Notes` + `## Next Steps` for you to fill.
- Re-running the same week is idempotent (no duplicates).

## Then: add your notes

Open each meeting/contact note and fill the `## Notes` sections. To weave people into the wider graph (referrals, intros, topics), hand off to `contact-meeting-capture` / `relationship-intro-pattern` / `topic-based-linking`.
