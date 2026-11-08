# Setup Workflow — one-time

Reading Google Calendar here goes through **macOS Calendar.app** (EventKit), so the "Google login" is a one-time account-add in System Settings, not an OAuth flow in a script.

## Step 1: Add the Google account to Calendar.app

1. **System Settings → Internet Accounts → Add Account → Google.**
2. Sign in (browser + 2FA). **Enable Calendars** for the account.
3. Open **Calendar.app** and confirm your Google events appear. EventKit only sees what Calendar.app has synced.

Verify a local calendar store now exists:
```bash
ls ~/Library/Calendars    # should exist / be non-empty after syncing
```

## Step 2: Grant Calendar permission to the host process

The first `fetch_week_events.py` run triggers a macOS Calendar-access prompt for whatever process runs it (Terminal, iTerm, or the app hosting Claude Code). **Allow it.**

If you dismissed/denied it:
- **System Settings → Privacy & Security → Calendars** → enable the terminal/app.
- Full Access is preferred (macOS 14+); Calendar.app data is read-only here.

## Step 3: Confirm `uv`

```bash
~/.local/bin/uv --version    # any recent version; PyObjC/EventKit install on demand
```

## Step 4: Smoke test

```bash
uv run --with pyobjc-framework-EventKit python3 \
  resources/skills/workflow-ops/calendar-to-contacts/scripts/fetch_week_events.py --this-week | head -30
```
Expect JSON with a `count` and `events`. If it exits with "Calendar access not granted", redo Step 2. If `count` is 0 but you have meetings, the account isn't synced into Calendar.app (redo Step 1) or the week is genuinely empty.
