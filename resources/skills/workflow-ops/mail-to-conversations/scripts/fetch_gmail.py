#!/usr/bin/env python3
"""Fetch recent Gmail messages sent from a set of domains, grouped into threads → JSON.

Reuses the OAuth desktop client created for the calendar skill; needs the Gmail API
enabled in the same Google Cloud project and one browser re-consent for the
gmail.readonly scope. See workflows/gmail-auth.md.

  uv run --with google-api-python-client --with google-auth-oauthlib --with google-auth \
    python3 fetch_gmail.py --count 100 > /tmp/mail.json

Output: {"query": "...", "count": N, "messages": [{id, thread_id, date, internal_ms,
from_name, from_email, from_domain, to, cc, subject, snippet, message_id, in_reply_to,
references}]}  (sorted newest first). No writes.
"""
import argparse
import datetime
import json
import os
import sys
from email.utils import parseaddr, parsedate_to_datetime
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CRED_DIR = Path(os.path.expanduser("~/.config/calendar-to-contacts"))   # reuse the calendar OAuth client
TOKEN_DIR = Path(os.path.expanduser("~/.config/mail-to-conversations"))
# Default sender domains = the keys of the active employer pack's mail-to-conversations/domain_map.yaml
# (employers/README.md; it is that employer's partner list; copy schema/domain_map.example.yaml to start one).
sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "scripts"))
import employer  # noqa: E402  employer pack (employers/README.md)
DOMAIN_MAP = employer.path("mail-to-conversations/domain_map.yaml")
DEFAULT_DOMAINS = [
    line.split("#", 1)[0].split(":", 1)[0].strip().strip('"').lower()
    for line in (DOMAIN_MAP.read_text().splitlines() if DOMAIN_MAP.exists() else [])
    if ":" in line.split("#", 1)[0]
]
HEADERS = ["From", "To", "Cc", "Subject", "Date", "Message-ID", "In-Reply-To", "References"]


def _imports():
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        return Credentials, Request, InstalledAppFlow, build
    except Exception as e:
        sys.stderr.write(
            "ERROR: Google libs missing. Run via:\n  uv run --with google-api-python-client "
            "--with google-auth-oauthlib --with google-auth python3 %s ...\n(%s)\n" % (sys.argv[0], e))
        sys.exit(2)


def get_credentials(cred_path, token_path):
    Credentials, Request, InstalledAppFlow, _ = _imports()
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not cred_path.exists():
                sys.stderr.write("ERROR: OAuth client not found at %s (see workflows/gmail-auth.md).\n" % cred_path)
                sys.exit(4)
            flow = InstalledAppFlow.from_client_secrets_file(str(cred_path), SCOPES)
            sys.stderr.write("Opening browser for Google consent (gmail.readonly)...\n")
            creds = flow.run_local_server(port=0, open_browser=True, authorization_prompt_message="")
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())
        try:
            os.chmod(str(token_path), 0o600)
        except OSError:
            pass
    return creds


def hdr(headers, name):
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


def iso_date(headers, internal_ms):
    raw = hdr(headers, "Date")
    try:
        return parsedate_to_datetime(raw).astimezone().isoformat()
    except Exception:
        try:
            return datetime.datetime.fromtimestamp(int(internal_ms) / 1000).isoformat()
        except Exception:
            return ""


def main():
    ap = argparse.ArgumentParser(description="Fetch recent Gmail from a set of domains as JSON")
    ap.add_argument("--domains", default=",".join(DEFAULT_DOMAINS),
                    help="comma-separated sender domains")
    ap.add_argument("--count", type=int, default=100, help="max messages (newest first)")
    ap.add_argument("--query", help="override the Gmail search query entirely")
    ap.add_argument("--credentials", default=str(CRED_DIR / "credentials.json"))
    ap.add_argument("--token", default=str(TOKEN_DIR / "token.json"))
    args = ap.parse_args()

    domains = [d.strip().lower() for d in args.domains.split(",") if d.strip()]
    if not domains and not args.query:
        sys.stderr.write("ERROR: no sender domains — pass --domains, or create %s "
                         "(see domain_map.example.yaml).\n" % DOMAIN_MAP)
        sys.exit(2)
    query = args.query or ("from:(" + " OR ".join(domains) + ")")

    _, _, _, build = _imports()
    creds = get_credentials(Path(os.path.expanduser(args.credentials)),
                            Path(os.path.expanduser(args.token)))
    svc = build("gmail", "v1", credentials=creds, cache_discovery=False)

    # list ids (paginate up to count)
    ids, page = [], None
    while len(ids) < args.count:
        resp = svc.users().messages().list(
            userId="me", q=query, maxResults=min(100, args.count - len(ids)), pageToken=page).execute()
        ids += [m["id"] for m in resp.get("messages", [])]
        page = resp.get("nextPageToken")
        if not page:
            break

    messages = []
    for mid in ids[:args.count]:
        m = svc.users().messages().get(
            userId="me", id=mid, format="metadata", metadataHeaders=HEADERS).execute()
        headers = m.get("payload", {}).get("headers", [])
        from_name, from_email = parseaddr(hdr(headers, "From"))
        from_domain = from_email.split("@")[-1].lower() if "@" in from_email else ""
        # double-check the sender domain is actually one we asked for
        if from_domain not in domains:
            continue
        messages.append({
            "id": mid,
            "thread_id": m.get("threadId", ""),
            "internal_ms": int(m.get("internalDate", "0")),
            "date": iso_date(headers, m.get("internalDate", "0")),
            "from_name": from_name or from_email,
            "from_email": from_email,
            "from_domain": from_domain,
            "to": hdr(headers, "To"),
            "cc": hdr(headers, "Cc"),
            "subject": hdr(headers, "Subject") or "(no subject)",
            "snippet": m.get("snippet", ""),
            "message_id": hdr(headers, "Message-ID"),
            "in_reply_to": hdr(headers, "In-Reply-To"),
            "references": hdr(headers, "References"),
        })

    messages.sort(key=lambda x: x["internal_ms"], reverse=True)
    threads = {}
    for m in messages:
        threads.setdefault(m["thread_id"], 0)
        threads[m["thread_id"]] += 1
    json.dump({"query": query, "count": len(messages), "thread_count": len(threads),
               "messages": messages}, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    sys.stderr.write("Fetched %d messages across %d threads (query: %s)\n"
                     % (len(messages), len(threads), query))


if __name__ == "__main__":
    main()
