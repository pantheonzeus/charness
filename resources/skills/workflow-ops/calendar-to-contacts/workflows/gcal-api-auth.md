# Google Calendar API auth (Calendar.app-free path)

Use this when you'd rather read Google Calendar **directly via the API** (no macOS Calendar.app, no TCC permission) — the `fetch_gcal_oauth.py` path. One-time: create a Google Cloud OAuth client, then a browser consent. Mirrors the notebooklm login model.

## Step 1: Create a Google Cloud OAuth client (one-time, ~5 min)

1. Go to **https://console.cloud.google.com/** → create (or pick) a project.
2. **APIs & Services → Library →** search **"Google Calendar API" → Enable**.
3. **APIs & Services → OAuth consent screen →** User type **External** (or Internal if Workspace) → fill app name + your email → add yourself under **Test users** (External apps in "testing" only allow test users, which is fine for personal use).
4. **APIs & Services → Credentials → Create Credentials → OAuth client ID →** Application type **Desktop app** → Create → **Download JSON**.
5. Save it as:
   ```bash
   mkdir -p ~/.config/calendar-to-contacts
   mv ~/Downloads/client_secret_*.json ~/.config/calendar-to-contacts/credentials.json
   chmod 600 ~/.config/calendar-to-contacts/credentials.json
   ```

## Step 2: First fetch = browser consent

```bash
SKILL=resources/skills/workflow-ops/calendar-to-contacts
uv run --with google-api-python-client --with google-auth-oauthlib --with google-auth \
  python3 $SKILL/scripts/fetch_gcal_oauth.py --start 2026-07-06 --end 2026-07-10 \
  > /tmp/workweek-events.json
```
A browser window opens → sign in → **Allow** the read-only Calendar access. The script caches a token at `~/.config/calendar-to-contacts/token.json` (chmod 600); later runs are non-interactive until the token expires.

- If you see "Google hasn't verified this app", that's expected for a personal test app — proceed (Advanced → continue), since it's your own client and read-only scope.
- Scope requested: `calendar.readonly` only.

## Step 3: Build (same as the EventKit path)

The JSON is identical in shape, so:
```bash
python3 $SKILL/scripts/build_contacts.py --sources /tmp/workweek-events.json \
  --vault cbrain --domain-map "$(python3 scripts/employer.py path calendar-to-contacts/domain_map.yaml)" --dry-run
```

## Flags
`fetch_gcal_oauth.py`: `--this-week` (default) · `--next-week` · `--start/--end YYYY-MM-DD` · `--calendar <id>` (default `primary`) · `--credentials <path>` · `--token <path>`.

## Troubleshooting
- **`OAuth client not found`** → credentials.json isn't at `~/.config/calendar-to-contacts/credentials.json` (or pass `--credentials`).
- **`access_denied` / test-user error** → add your Google address as a Test user on the consent screen.
- **Wrong account** → delete `~/.config/calendar-to-contacts/token.json` and re-run to re-consent.
- **Multiple calendars** → default is `primary`; pass `--calendar <calendarId>` (find IDs with the Calendar API `calendarList`).
