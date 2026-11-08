# mail — capability contract

## Operations (used today)
| Operation | Used by | Notes |
|---|---|---|
| `search(senders \| participants \| lists, since, exclude_self, limit)` | mail-triage poll/backfill, meeting-prep sync, mail-to-conversations, morning-briefing, console | paginated; exclude own address |
| `get(ref) → Message` | mail-triage, mail-to-conversations, console | full headers + plain-text body |
| `thread_replied(thread_id, after) → bool` | mail-triage | did the principal answer in the thread |
| `draft(to, cc, subject, body, reply_to?)` | console, living-plan | |
| `send(...)` / `reply(ref, body, reply_all)` | mail-triage `send` (console click), console, living-plan | approval-gated; in-thread (In-Reply-To/References) |
| `web_link(thread_id) → url` | console Mail view | |
| `can_send() → bool` | console Mail view | send credential present |

## Normalized shape — `output/mail-triage/messages/<id>.json`
`id, thread_id, message_id, references, reply_to, from_name, from_email, to, cc, subject, date, snippet, body_text, company, already_replied`
(mail-to-conversations' builder input `{query, count, messages:[…]}` carries the same fields.)

## Implementations
| Adapter | Where | Auth |
|---|---|---|
| `google` | `mail-triage/scripts/triage.py` (REST: messages.list/get, threads.get, messages.send); `meeting-prep-loop/scripts/sync.py` (REST search); `mail-to-conversations/scripts/fetch_gmail.py` (REST) + `mcp_gmail_to_sources.py` (workspace-mcp → shape); console tools `mcp__workspace-mcp__*_gmail_*` | `~/.config/mail-to-conversations/token.json` (read), `~/.config/mail-triage/send-token.json` (send), OAuth client `~/.config/calendar-to-contacts/credentials.json`; server setup `resources/mcp/google-workspace.md` |
| `m365` | **stub — not built.** | |

### m365 notes (from memory, unverified: confirm against Microsoft Graph docs before building)
`search` → `GET /me/messages` with `$search` / `$filter` (KQL/OData, not Gmail syntax); `get` → `/me/messages/{id}`
(`internetMessageId`, `conversationId` ↔ thread); `reply` → `POST /me/messages/{id}/reply` or `createReply` + `send`;
`web_link` → the message's `webLink`. Delegated `Mail.Read` / `Mail.Send` consent; a tenant may require admin approval.
