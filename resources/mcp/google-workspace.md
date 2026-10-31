# Google Workspace MCP — Gmail + Calendar connection

Shared setup for the **self-hosted Google Workspace MCP server** that is now the
**primary** connection for both vault skills:

- `workflow-ops/calendar-to-contacts` — reads Calendar events
- `workflow-ops/mail-to-conversations` — reads Gmail messages

The old per-skill `fetch_*.py` scripts (and the macOS EventKit path) still work and
stay in place as an **offline / degraded-mode fallback** — see each skill's SKILL.md.

## Why this exists

Previously each skill re-implemented its own Google OAuth + REST plumbing. Both now
share **one** maintained MCP surface. The pure-stdlib vault builders
(`build_contacts.py`, `build_conversations.py`) are unchanged — their `--sources
<json>` input is the stable contract. We only swapped what produces that JSON:

```
Old:  fetch_*.py            → JSON → build_*.py → vault
New:  MCP tool call → adapter → JSON → build_*.py → vault
```

## Server

**[`taylorwilsdon/google_workspace_mcp`](https://github.com/taylorwilsdon/google_workspace_mcp)**
— run with `--permissions gmail:full calendar:full drive:readonly docs:readonly` (Drive + Docs read-only since 2026-10-11), HTTP transport, OAuth 2.1.

## One-time setup

### 1. Google Cloud project (reuse the existing one)
The desktop OAuth client already backing the fetch scripts lives at
`~/.config/calendar-to-contacts/credentials.json`. Reuse it. In that project:

- Confirm **Gmail API** and **Google Calendar API** are enabled.
- **Expand the OAuth consent-screen scopes to include write** (this migration chose
  write access): Gmail send/modify + Calendar events, alongside the existing
  `gmail.readonly` / `calendar.readonly`. Write is latent headroom — no skill sends
  mail or edits events yet.
- Add the redirect URI **`http://localhost:8000/oauth2callback`** to the OAuth client
  (or mint a dedicated client and point `GOOGLE_OAUTH_CREDENTIALS` at it).

### 2. Start the server
```bash
./scripts/start-google-workspace-mcp.sh
```
Leave it running in its own terminal. It reads the client id/secret from the existing
`credentials.json`, enables OAuth 2.1, and serves Gmail + Calendar tools on
`http://localhost:8000/mcp`. Tokens cache under `~/.google_workspace_mcp/credentials/`
(separate from the fetch scripts' `~/.config/**/token.json`).

> **Standing service (recommended — avoids "MCP path isn't live"):** the server is a
> launchd agent, `~/Library/LaunchAgents/com.cbrain.workspace-mcp.plist`
> (`RunAtLoad` + `KeepAlive`), so it auto-starts on login and self-restarts. It wraps
> this same script; logs go to `output/workspace-mcp.log`. Manage with
> `launchctl load|unload ~/Library/LaunchAgents/com.cbrain.workspace-mcp.plist`;
> check with `launchctl list | grep workspace-mcp`. No need to keep a terminal open.

### 3. Register with Claude Code
The repo-root `.mcp.json` already declares the server. Confirm/register:
```bash
claude mcp add --transport http workspace-mcp http://localhost:8000/mcp   # if not already picked up
```
**Verify:** `/mcp` shows `workspace-mcp` connected and lists Gmail + Calendar tools.
The first tool call opens a browser for consent, then caches a token.

## Tools used by the skills

| Skill | MCP tool | Adapter → builder |
|---|---|---|
| calendar-to-contacts | `list_calendar_events` (window = the target week) | `scripts/mcp_events_to_sources.py` → `build_contacts.py --sources` |
| mail-to-conversations | `search_gmail_messages` (query = `from:(domainA OR …)`) | `scripts/mcp_gmail_to_sources.py` → `build_conversations.py --sources` |

Each skill's `workflows/mcp-run.md` has the exact call sequence.

## Known caveat — Gmail metadata depth

`build_conversations.py` groups by `thread_id` and uses the RFC headers
`message_id` / `in_reply_to` / `references`. If `search_gmail_messages` returns
thinner results than the fetch script's `format=metadata` call, the adapter must
backfill those via a per-message `get_gmail_message`. **Confirm the tool's real
output shape when you first authorize** (capture one response) and finalize the
adapters against it — that is the one thing that can only be nailed with the live
server.

## Write access — guardrail

Write tools are enabled at the server for Gmail + Calendar (`gmail:full calendar:full`; Drive + Docs are `readonly`),
so an agent *could* send mail or modify the calendar. No skill does. The one sender is the
webapp console (`webapp/server.py`): its `ALLOWED_TOOLS` admits Gmail search/read/draft/send
only, and its prompt requires a full read-back plus an explicit "send" before each mail. Keep routine
workflows read-shaped; if you want a hard block, restart the server with
`--read-only` (drops the write tools and requests only read scopes).

## Lighter alternative — stdio

HTTP transport needs the standing process above. For a single-user local-only setup
you can instead run the server over **stdio** (Claude Code spawns/kills it
automatically, no separate terminal), at the cost of the OAuth 2.1 multi-user flow.
Swap the `.mcp.json` entry for a `command`/`args` stdio launch of `workspace-mcp` if
the standing process proves annoying.
