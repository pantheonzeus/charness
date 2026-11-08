#!/usr/bin/env bash
# Start the self-hosted Google Workspace MCP server (Gmail + Calendar) for the vault.
#
# One long-running local process is the operational cost of HTTP transport (the
# transport Claude Code's OAuth 2.1 flow needs). Leave this running in its own
# terminal; the `.mcp.json` at the repo root points Claude Code at it on :8000.
#
# Reuses the *existing* Google Cloud OAuth desktop client that already backs the
# fetch_*.py fallback scripts (~/.config/calendar-to-contacts/credentials.json) —
# no second client to create. First tool call opens a browser for consent; the
# token is cached under ~/.google_workspace_mcp/credentials/.
#
# Setup, scope expansion (for write access) and the stdio alternative are in
# resources/mcp/google-workspace.md.
set -euo pipefail

CRED="${GOOGLE_OAUTH_CREDENTIALS:-$HOME/.config/calendar-to-contacts/credentials.json}"
if [ ! -f "$CRED" ]; then
  echo "OAuth client JSON not found at $CRED" >&2
  echo "See resources/mcp/google-workspace.md for how to create/point at it." >&2
  exit 1
fi

# Pull client_id / client_secret out of the existing desktop client JSON.
eval "$(python3 - "$CRED" <<'PY'
import json, shlex, sys
c = json.load(open(sys.argv[1]))
c = c.get("installed") or c.get("web") or c
print("export GOOGLE_OAUTH_CLIENT_ID=%s" % shlex.quote(c["client_id"]))
print("export GOOGLE_OAUTH_CLIENT_SECRET=%s" % shlex.quote(c["client_secret"]))
PY
)"

export MCP_ENABLE_OAUTH21=true
export WORKSPACE_MCP_PORT="${WORKSPACE_MCP_PORT:-8000}"
# IPv4 first: IPv6 here resolves but doesn't route, and httplib2 hangs instead of falling back.
export PYTHONPATH="$(cd "$(dirname "$0")" && pwd)/ipv4${PYTHONPATH:+:$PYTHONPATH}"

# Gmail + Calendar only. Write tools are ENABLED (no --read-only) per the migration
# decision — send/modify is latent headroom; no skill uses it yet.
# Drive + Docs added 2026-10-11, READ-ONLY (ask about documents in chat; the meeting-prep loop
# reads Drive through its own token, not this server). Gmail/Calendar keep full as before.
exec uvx workspace-mcp@latest --permissions gmail:full calendar:full drive:readonly docs:readonly \
  --transport streamable-http
