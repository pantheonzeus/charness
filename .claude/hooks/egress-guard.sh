#!/usr/bin/env bash
# PreToolUse egress guard for WebFetch / WebSearch (G4b). The Bash sandbox does not cover these
# tools, and they are the exfiltration channel when a run that holds private data (mail, vault,
# client notes) also reads untrusted text that could instruct it to "fetch" a URL. Research URLs
# and search queries never need to carry the shapes below, so they are denied:
#   - an email address, except the principal's public one (`git config charness.publicEmail`, e.g. for
#     APIs such as Unpaywall that require it)
#   - an encoded blob: an unbroken run of >= 56 letters and digits with at least 4 of each (word slugs
#     break on _ - +, document ids are 44)
#   - a query string longer than 300 characters, or one parameter value longer than 150
# Denies are traced to output/.runs/_forensics/hooks.jsonl like write-boundary's.
# FAIL-OPEN like write-boundary: a parse problem never blocks a call.
# Test: bash .claude/hooks/tests/egress-guard.test.sh
set -uo pipefail

input="$(cat 2>/dev/null || true)"
tool="$(printf '%s' "$input" | jq -r '.tool_name // empty' 2>/dev/null || true)"
target="$(printf '%s' "$input" | jq -r '.tool_input.url // .tool_input.query // empty' 2>/dev/null || true)"
[ -z "$target" ] && exit 0

PUBLIC_EMAIL="$(git -C "${CLAUDE_PROJECT_DIR:-.}" config --get charness.publicEmail 2>/dev/null || true)"
reason="$(/usr/bin/python3 - "$target" "$PUBLIC_EMAIL" <<'PY' 2>/dev/null || true
import re, sys
from urllib.parse import urlsplit, parse_qsl, unquote
t = unquote(sys.argv[1])
public = sys.argv[2].lower() if len(sys.argv) > 2 else ""
if any(e.lower() != public for e in re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", t)):
    print("it contains an email address")
    sys.exit()
for blob in re.findall(r"[A-Za-z0-9]{56,}", t):
    if len(re.findall(r"[A-Za-z]", blob)) >= 4 and len(re.findall(r"\d", blob)) >= 4:
        print(f"it contains a {len(blob)}-character encoded blob")
        sys.exit()
q = urlsplit(sys.argv[1]).query if "://" in sys.argv[1] else ""
if len(q) > 300:
    print(f"its query string is {len(q)} characters")
elif any(len(v) > 150 for _, v in parse_qsl(q)):
    print("one query parameter is over 150 characters")
PY
)"
[ -z "$reason" ] && exit 0

REPO="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
msg="egress guard: $tool blocked because $reason — research never needs to send that out. If this URL is genuinely public and needed, fetch the page without the data in it, or ask the principal."
log="$REPO/output/.runs/_forensics/hooks.jsonl"
if mkdir -p "$(dirname "$log")" 2>/dev/null; then
  printf '%s' "$input" | jq -c --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg why "$reason" --arg job "${CBRAIN_JOB:-}" \
    '{ts: $ts, session_id: (.session_id // null), hook: "egress-guard", decision: "deny", tool: (.tool_name // null), why: $why, job: (if $job == "" then null else $job end)}' \
    >> "$log" 2>/dev/null || true
fi
jq -cn --arg r "$msg" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}'
