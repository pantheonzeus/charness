---
id: mail-to-conversations
aliases: [mail-to-conversations]
name: "Mail → Conversations & People"
category: workflow-ops
description: Extract recent Gmail from a set of sender domains (via the Google Workspace MCP server; OAuth-script fallback), group it into conversations (threads), write a per-email note + a conversation index, and link every sender to the people (contacts) — so you can see what belongs to which conversation.
triggers: [extract emails, last mails from, mail from domain, email conversations, thread emails, who emailed me, mail chains, link emails to people]
tags: [workflow-ops, email, gmail, mcp, conversations, threads, contacts, obsidian, automation]
related: ["[[calendar-to-contacts]]", "[[contact-meeting-capture]]"]
modules: [file-backed-handoff]
requires:
  tools: [bash, python]
  mcp: ["workspace-mcp (google_workspace_mcp) — Gmail+Calendar; see resources/mcp/google-workspace.md"]
  python: [google-api-python-client, google-auth-oauthlib, google-auth]  # fallback path only
  obsidian-plugins: [Dataview]
environment: "Primary: Google Workspace MCP server (`search_gmail_messages` → adapter → build_conversations.py), one shared local server — see resources/mcp/google-workspace.md. Fallback (offline/degraded): `fetch_gmail.py` (Gmail API, reuses the calendar skill's OAuth desktop client, gmail.readonly consent). Both feed the same JSON contract; writes to the vault (Mail/, Clients/)."
scripts: [scripts/mcp_gmail_to_sources.py, scripts/build_conversations.py, scripts/fetch_gmail.py]
workflows: [workflows/mcp-run.md, workflows/gmail-auth.md, workflows/run.md]
schema: [schema/domain_map.example.yaml]
status: active
version: 7
created: 2026-07-05
updated: 2026-10-23
vault_writes: ["cbrain/Mail/*", "cbrain/Clients/*"]
---

# Mail → Conversations & People

Pull recent email **sent from a set of domains**, group it by **conversation (thread)**, and link each sender to a **contact** — so the vault answers "what belongs to which conversation" and "who said what".

## What This Does

1. **Fetches** the most-recent N emails whose sender domain is in your list via the Google Workspace MCP server (`search_gmail_messages`, read-only), with thread IDs and headers; `fetch_gmail.py` is a drop-in fallback.
2. **One note per email** → `Mail/msgs/<YYYYMMDD>-<subject>-<id8>.md` (from/to/date/snippet, links to sender + conversation).
3. **A conversation index** → `Mail/Conversations.md` — grouped by thread, newest first, each thread listing its messages in order with participants linked. **This is the "what belongs to which conversation" view.**
4. **Links senders to people** → each sender gets/updates a `Clients/<Name>.md` with a `## Mail` section listing the conversations they're in (company inferred from domain). Append-only; deduped by email.

## Reading mail — one contract, two sources

The read layer produces one JSON shape (`{query,count,messages:[…]}`); `build_conversations.py` is identical downstream.

| Path | Source | Setup | Use when |
|------|--------|-------|----------|
| **MCP** (primary) | `search_gmail_messages` → `scripts/mcp_gmail_to_sources.py` | Google Workspace MCP server running (once) — [resources/mcp/google-workspace.md](../../../mcp/google-workspace.md) | Default. Shared server with the calendar skill |
| **OAuth script** (fallback) | `scripts/fetch_gmail.py` | Reuses the calendar OAuth client + `gmail.readonly` consent | MCP server down, or a quick offline one-shot |

## Prerequisites

- **Google Workspace MCP server** running and connected (`/mcp` shows `workspace-mcp` with Gmail tools). One-time setup + auth: [resources/mcp/google-workspace.md](../../../mcp/google-workspace.md).
- **`uv`** installed — for the launcher and the fallback fetch script (Google libs install on demand).

## Quick Start (MCP — primary)

```bash
SKILL=resources/skills/workflow-ops/mail-to-conversations
VAULT=cbrain   # run from the repo root
Q="from:(yourcompany.com OR client-a.com OR client-b.com OR partner-university.edu)"  # swap in your own employer + active client/partner domains

# 1. Call the MCP `search_gmail_messages` tool with query $Q (newest ~100); save the raw
#    tool JSON to /tmp/mcp-mail.json. See the note below on thread/header depth.
# 2. Adapt into the builder's contract (records the query for the index header):
python3 $SKILL/scripts/mcp_gmail_to_sources.py /tmp/mcp-mail.json --query "$Q" > /tmp/mail.json

# 3. Preview (writes nothing) — --exclude-noise drops calendar-invite + automated mail
python3 $SKILL/scripts/build_conversations.py --sources /tmp/mail.json --vault "$VAULT" \
  --domain-map "$(python3 scripts/employer.py path mail-to-conversations/domain_map.yaml)" --exclude-noise --dry-run

# 4. Build
python3 $SKILL/scripts/build_conversations.py --sources /tmp/mail.json --vault "$VAULT" \
  --domain-map "$(python3 scripts/employer.py path mail-to-conversations/domain_map.yaml)" --exclude-noise
```

`mcp_gmail_to_sources.py` flags: `--query "<the query used>"` (recorded in output) · `--domains a.com,b.com` (sender double-check, default = the 8 partner domains).
`build_conversations.py` flags: `--exclude-noise` (drop calendar-notification subjects + automated/no-reply senders — **recommended**) · `--exclude-senders a@x,b@y` · `--self-email` (kept in threads, never made a contact — renders as *you*) · `--dry-run`.
Full call sequence + fallback: [workflows/mcp-run.md](workflows/mcp-run.md).

> **Thread/header depth (validate on first auth):** `build_conversations.py` groups by `thread_id` and uses the RFC headers. If `search_gmail_messages` returns thinner data than the old `format=metadata` fetch, backfill via a per-message `get_gmail_message` before the adapter — see the caveat in [resources/mcp/google-workspace.md](../../../mcp/google-workspace.md).

### Fallback (MCP unavailable)
Swap steps 1–2 for the fetch script, then run `build_conversations.py` unchanged:
```bash
uv run --with google-api-python-client --with google-auth-oauthlib --with google-auth \
  python3 $SKILL/scripts/fetch_gmail.py --count 100 > /tmp/mail.json
```
`fetch_gmail.py` flags: `--domains` · `--count N` · `--query "<raw Gmail query>"` · `--credentials`/`--token`.

## Workflow Routing

| Task | Workflow |
|------|----------|
| Run the extraction via MCP (primary) | [workflows/mcp-run.md](workflows/mcp-run.md) |
| MCP server setup + auth (shared with Calendar) | [resources/mcp/google-workspace.md](../../../mcp/google-workspace.md) |
| Fallback Gmail auth (enable API + gmail.readonly consent) | [workflows/gmail-auth.md](workflows/gmail-auth.md) |
| Fallback run (fetch script → preview → build) | [workflows/run.md](workflows/run.md) |

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/mcp_gmail_to_sources.py` | **(primary)** MCP `search_gmail_messages` JSON → the `{messages:[…]}` builder contract |
| `scripts/build_conversations.py` | JSON → `Mail/msgs/` per-email notes + `Mail/Conversations.md` index + `## Mail` links on sender contacts (dedup, append-only, `--dry-run`) |
| `scripts/fetch_gmail.py` | *(fallback)* Gmail API (OAuth) → same JSON, with thread IDs (read-only) |

## Notes & Gotchas

- **Threads are the source of truth** for "which conversation" — grouping is by Gmail `threadId`, not by subject (so `Re:`/`Fwd:` and renamed subjects still group correctly). The subject shown is the latest message's, cleaned of `Re:`/`Fwd:` prefixes.
- **Senders only** become contacts (people who sent *from* the listed domains). Recipients aren't auto-created (would flood the vault); they appear in each mail's `To:` line.
- **Read-only; body-aware builder (v4).** The builder renders each note from `msg_body()`, which prefers a parsed `body_text`/`body` field and falls back to Gmail's `snippet`. Today the fetchers emit `snippet` only (`format=full` needed for a real body — see the bulk-pull note); the day a fetcher carries `body_text`, existing notes fill in on the next regen with no builder change. Empty-body notes (snippet was blank) are expected until then.
- **Company inference** from the sender domain; override in the employer pack's `mail-to-conversations/domain_map.yaml` (employers/README.md).
- **Append-only** on existing contacts — only a `## Mail` link is added; your annotations are untouched. Re-running is idempotent (existing msg notes skipped).
- **Noise is real.** Raw mailboxes are full of calendar invitations (`Invitation:`/`Accepted:`), automated senders (`invoicing@`, `no-reply@`, `*-admin-group`), and marketing aliases. `--exclude-noise` drops these so the conversation index shows actual back-and-forth. Tune via `--exclude-senders`.
- **Links resolve to the *canonical* contact.** A sender is matched to any existing contact by email first, so a person already in `Clients/` (e.g. from the calendar skill under a different name form) is reused rather than duplicated — every `[[person]]` in the Mail notes points at a real file. Your own address renders as *you*, never a self-contact.
- To regenerate cleanly (e.g. after changing filters), delete `Mail/` and re-run; contact `## Mail` links are deduped so they aren't doubled.
- **Shared/list addresses defeat email-based contact attribution.** Newsletters and forwards arrive as `'Real Name' via <group>` but with `from_email` collapsed to the *list* address (`you@`, `info-de@`, `purchase-orders.germany@`, `<partner>-admin-group@`, `<project>-platform@`, `hc@`/`hc-germany@`, `support@`, a client's `servicemanagement@…`). They'd spawn junk contacts named after the "via" string (e.g. `'Some Newsletter' via you` ×55). **Now handled at the root (v4):** `disp()` strips the ` via <handle>` annotation + surrounding quotes back to the real display name, and `_functional()` (functional local-part tokens + any `*.onmicrosoft.com` tenant address) keeps list senders out of `Clients/` and renders them as plain text, not `[[wikilinks]]` — always-on, no flag needed. `--exclude-senders` / `--exclude-noise` remain for dropping their *messages* entirely. Real individuals mail from their own address, so their threads survive. This is the mail-side twin of the mailing-list-as-person trap in `[[vault-maintenance]]`.
- **Subdomain senders:** partner mail often comes from subdomains (`j.doe@dept.partner-uni.example`, `a.smith@lab.partner-uni.example`). The exact-domain sender check drops them — match by **suffix** (`endswith('.'+domain)`) and normalise `from_domain` to the parent so `domain_map` company inference works.
- **Bulk pulls (100s–1000s):** the MCP tools are chatty (IDs-only search, 25-msg metadata batches). For a large pull, delegate the fetch to a subagent so the ~40+ round-trips don't flood the main context (file-backed handoff per Charter §5 — [`_shared/delegation-handoff.md`](../../_shared/delegation-handoff.md)): write its packet to `output/.runs/<YYYYMMDD>-mail-import/children/fetch/TASK.md` (query, date window, output path), context mode **fresh**; the child writes the builder JSON beside it plus a `RESPONSE.md` (message count, gaps, errors); the parent reopens `RESPONSE.md` and the JSON from disk before running the builder. Snippets need `format=full`; `metadata` (lighter) yields empty note previews.
- **`disp()` now strips `/`,`\` from display names** (v3) — a slash breaks `[[wikilink]]` resolution (read as a path separator) and can't be aliased around. `Conversations.md` now carries `type: index` frontmatter (v3). Both were post-import audit catches via `[[vault-maintenance]]`.
