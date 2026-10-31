#!/usr/bin/env python3
"""Adapt Google Workspace MCP `search_gmail_messages` output → build_conversations.py JSON.

The MCP server (taylorwilsdon/google_workspace_mcp) is the primary connection now;
this adapter maps its Gmail tool output into the exact `{query,count,thread_count,
messages:[...]}` shape build_conversations.py consumes — the same contract
fetch_gmail.py emits, so the builder is unchanged. See ../../../../mcp/google-workspace.md.

Flow:
  1. Query the MCP tool (query = `from:(domainA OR …)`), save its JSON: … > /tmp/mcp-mail.json
  2. python3 mcp_gmail_to_sources.py /tmp/mcp-mail.json --query "from:(…)" > /tmp/mail.json
  3. build_conversations.py --sources /tmp/mail.json …

Input: the raw MCP tool result — a JSON list of message objects, or an object with a
`messages`/`results` array. Each message is read tolerantly:
  - Google-API shape: headers under `payload.headers`, `threadId`, `internalDate`, `snippet`
  - flat shape: top-level `from`/`to`/`cc`/`subject`/`date`/`thread_id`/`snippet` keys
VALIDATE against a captured live response the first time you authorize.

KNOWN RISK (see the shared doc): build_conversations.py groups by `thread_id` and uses
the RFC headers Message-ID / In-Reply-To / References. If the search tool omits these,
back them off a per-message `get_gmail_message` call before feeding this adapter, or
extend the adapter to make that call. Missing headers degrade threading, not the run.

Reads a file arg or stdin; writes builder JSON to stdout.
"""
import argparse
import datetime
import json
import sys
from email.utils import parseaddr, parsedate_to_datetime
from pathlib import Path

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


def hdr(m, name):
    """Read a header from either the Google `payload.headers` list or flat top-level keys."""
    headers = (m.get("payload", {}) or {}).get("headers")
    if isinstance(headers, list):
        for h in headers:
            if h.get("name", "").lower() == name.lower():
                return h.get("value", "")
    # flat fallback: `Message-ID` → message_id / messageId / message-id
    for cand in (name, name.lower(), name.replace("-", "_").lower(),
                 name.replace("-", "").lower()):
        if cand in m:
            return m.get(cand) or ""
    return ""


def internal_ms(m):
    v = m.get("internalDate") or m.get("internal_ms") or "0"
    try:
        return int(v)
    except (TypeError, ValueError):
        return 0


def iso_date(m, ms):
    raw = hdr(m, "Date")
    try:
        return parsedate_to_datetime(raw).astimezone().isoformat()
    except Exception:
        try:
            return datetime.datetime.fromtimestamp(ms / 1000).isoformat()
        except Exception:
            return ""


def extract_items(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("messages", "results", "items"):
            if isinstance(data.get(key), list):
                return data[key]
    sys.stderr.write("ERROR: could not find a messages array in the MCP output "
                     "(expected a list, or an object with messages/results/items).\n")
    sys.exit(2)


def norm_message(m, domains):
    from_name, from_email = parseaddr(hdr(m, "From"))
    from_domain = from_email.split("@")[-1].lower() if "@" in from_email else ""
    if domains and from_domain not in domains:
        return None  # double-check the sender domain, mirroring fetch_gmail.py
    ms = internal_ms(m)
    return {
        "id": m.get("id") or m.get("message_id") or "",
        "thread_id": m.get("threadId") or m.get("thread_id") or "",
        "internal_ms": ms,
        "date": iso_date(m, ms),
        "from_name": from_name or from_email,
        "from_email": from_email,
        "from_domain": from_domain,
        "to": hdr(m, "To"),
        "cc": hdr(m, "Cc"),
        "subject": hdr(m, "Subject") or "(no subject)",
        "snippet": m.get("snippet", ""),
        "message_id": hdr(m, "Message-ID"),
        "in_reply_to": hdr(m, "In-Reply-To"),
        "references": hdr(m, "References"),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", nargs="?", help="MCP tool JSON (default: stdin)")
    ap.add_argument("--query", default="", help="the Gmail query used (recorded in output for the index header)")
    ap.add_argument("--domains", default=",".join(DEFAULT_DOMAINS),
                    help="comma-separated sender domains to keep (blank = keep all)")
    args = ap.parse_args()

    domains = [d.strip().lower() for d in args.domains.split(",") if d.strip()]
    raw = open(args.input).read() if args.input else sys.stdin.read()
    messages = [x for x in (norm_message(m, domains) for m in extract_items(json.loads(raw))) if x]
    messages.sort(key=lambda x: x["internal_ms"], reverse=True)

    threads = {m["thread_id"] for m in messages}
    json.dump({"query": args.query, "count": len(messages),
               "thread_count": len(threads), "messages": messages},
              sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    sys.stderr.write("Adapted %d message(s) across %d thread(s) → build_conversations.py schema\n"
                     % (len(messages), len(threads)))


if __name__ == "__main__":
    main()
