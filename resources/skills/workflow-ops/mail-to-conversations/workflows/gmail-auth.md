# Gmail auth (one-time)

Reuses the OAuth desktop client you already created for the calendar skill
(`~/.config/calendar-to-contacts/credentials.json`). You only need to enable the Gmail
API and consent to the read-only mail scope once.

## Step 1: Enable the Gmail API

In **https://console.cloud.google.com/** → the same project you used for Calendar →
**APIs & Services → Library** → search **"Gmail API"** → **Enable**.

(The OAuth consent screen is already configured from the calendar setup, and you're
already a Test user, so no changes there. A "testing" app can request the sensitive
`gmail.readonly` scope for test users — you'll just see the unverified-app screen.)

## Step 2: First fetch = browser consent

```bash
SKILL=resources/skills/workflow-ops/mail-to-conversations
uv run --with google-api-python-client --with google-auth-oauthlib --with google-auth \
  python3 $SKILL/scripts/fetch_gmail.py --count 100 > /tmp/mail.json
```
A browser opens → sign in → **Advanced → continue** past the unverified-app warning →
**Allow** read-only Gmail access. The token is cached at
`~/.config/mail-to-conversations/token.json` (chmod 600); later runs are non-interactive.

- Scope requested: `gmail.readonly` **only**.
- The calendar token is separate and untouched (this skill stores its own token).

## Troubleshooting

- **`OAuth client not found`** → credentials.json isn't at `~/.config/calendar-to-contacts/credentials.json` (or pass `--credentials`).
- **`Gmail API has not been used in project … or it is disabled`** → do Step 1, wait a minute, re-run.
- **`accessNotConfigured` / 403** → Gmail API not enabled on *that* project, or wrong Google account — delete `~/.config/mail-to-conversations/token.json` and re-consent with the right account.
- **Wrong scope cached** (was calendar-only) → the token here is gmail-specific; if you ever see a scope error, delete `~/.config/mail-to-conversations/token.json` and re-run.
