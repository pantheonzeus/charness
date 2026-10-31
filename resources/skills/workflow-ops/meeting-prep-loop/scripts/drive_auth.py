# /// script
# requires-python = ">=3.10"
# dependencies = ["google-auth-oauthlib", "google-api-python-client"]
# ///
"""One-time Google consent for read-only Drive access, used by sync.py to find and read
the documents a meeting's participants worked on. Run it once, in a terminal:

  uv run resources/skills/workflow-ops/meeting-prep-loop/scripts/drive_auth.py

Prerequisite: the Google Drive API is enabled in the Google Cloud project that owns
~/.config/calendar-to-contacts/credentials.json (the same OAuth client the calendar and
mail skills use). The browser opens once; the token is stored at
~/.config/meeting-prep-loop/drive-token.json (0600) and refreshes itself afterwards.
"""
import os
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

CREDENTIALS = Path.home() / ".config/calendar-to-contacts/credentials.json"
TOKEN = Path.home() / ".config/meeting-prep-loop/drive-token.json"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

creds = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS), SCOPES).run_local_server(
    port=0, open_browser=True, authorization_prompt_message="Opening browser for Google consent (Drive, read-only)...\n")
TOKEN.parent.mkdir(parents=True, exist_ok=True)
TOKEN.write_text(creds.to_json())
os.chmod(TOKEN, 0o600)

# Prove it works end to end — this is where a disabled Drive API shows up.
files = build("drive", "v3", credentials=creds, cache_discovery=False).files().list(
    pageSize=3, orderBy="modifiedTime desc", fields="files(name,modifiedTime)").execute().get("files", [])
print(f"Drive connected. Token: {TOKEN}")
for f in files:
    print(f"  {f['modifiedTime'][:10]}  {f['name']}")
