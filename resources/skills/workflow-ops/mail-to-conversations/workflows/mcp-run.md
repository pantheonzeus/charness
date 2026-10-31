# Mail Extraction — via the Google Workspace MCP server (primary)

Pull recent mail from a set of domains into per-email notes + a conversation index,
reading Gmail through the shared MCP server. One-time server setup + auth:
[resources/mcp/google-workspace.md](../../../../mcp/google-workspace.md).

Set once per run:
```bash
SKILL=resources/skills/workflow-ops/mail-to-conversations
VAULT=cbrain   # run from the repo root
Q="from:($(sed 's/#.*//' "$(python3 scripts/employer.py path mail-to-conversations/domain_map.yaml)" | cut -d: -f1 | tr -d ' "' | grep . | paste -sd' ' - | sed 's/ / OR /g'))"
```
(Domains are read from your local `schema/domain_map.yaml` — gitignored; start from `domain_map.example.yaml`.)

## Step 1: Search from MCP

Confirm the server is connected (`/mcp` lists `workspace-mcp` with Gmail tools), then call
the **`search_gmail_messages`** tool with query `$Q` for the newest ~100 messages, and
**save the raw tool JSON** to `/tmp/mcp-mail.json`. Read-only.

> **Thread/header depth — the one thing to verify live.** `build_conversations.py`
> groups by `thread_id` and uses `message_id` / `in_reply_to` / `references`. If
> `search_gmail_messages` returns thinner results than the old `format=metadata` fetch
> (no threadId, no RFC headers), backfill them: for each hit call `get_gmail_message`
> and merge, *or* extend the adapter to do so. Missing headers degrade threading, not
> the run. Capture one response on first auth and confirm before trusting the output.

## Step 2: Adapt to the builder contract

```bash
python3 $SKILL/scripts/mcp_gmail_to_sources.py /tmp/mcp-mail.json --query "$Q" > /tmp/mail.json
```
Maps the tool output into the `{query,count,thread_count,messages:[…]}` shape
`build_conversations.py` expects (same contract `fetch_gmail.py` emits) and re-applies the
sender-domain double-check. Adapted message/thread counts print to stderr.

## Step 3: Dry run (writes nothing)

```bash
python3 $SKILL/scripts/build_conversations.py --sources /tmp/mail.json --vault "$VAULT" \
  --domain-map "$(python3 scripts/employer.py path mail-to-conversations/domain_map.yaml)" --exclude-noise --dry-run
```
`--exclude-noise` drops calendar-invite + automated senders. Add `--exclude-senders a@x,b@y`
to cut a specific alias; `--self-email you@yourcompany.com` renders you as *you*.

## Step 4: Build

```bash
python3 $SKILL/scripts/build_conversations.py --sources /tmp/mail.json --vault "$VAULT" \
  --domain-map "$(python3 scripts/employer.py path mail-to-conversations/domain_map.yaml)" --exclude-noise
```

## Step 5: Verify in Obsidian

Same as the fallback run — see [run.md](run.md). `Mail/Conversations.md` groups by thread;
each sender's `Clients/<Name>.md` gained a `## Mail` section. Idempotent on re-run.

## Step 1b: Fallback (MCP unavailable)

Replace Steps 1–2 with the fetch script (emits the same `/tmp/mail.json`), then continue at
Step 3:
```bash
uv run --with google-api-python-client --with google-auth-oauthlib --with google-auth \
  python3 $SKILL/scripts/fetch_gmail.py --count 100 > /tmp/mail.json
```
Fallback auth: [gmail-auth.md](gmail-auth.md).

## Parity check (do once, after first live auth)

```bash
python3 $SKILL/scripts/mcp_gmail_to_sources.py /tmp/mcp-mail.json --query "$Q" > /tmp/mcp-mail-out.json
uv run --with google-api-python-client --with google-auth-oauthlib --with google-auth \
  python3 $SKILL/scripts/fetch_gmail.py --count 100 > /tmp/oauth-mail-out.json
diff <(jq -S '.messages|sort_by(.id)' /tmp/mcp-mail-out.json) \
     <(jq -S '.messages|sort_by(.id)' /tmp/oauth-mail-out.json)
```
Field-equivalent messages (esp. `thread_id` + the RFC headers) ⇒ the migration is correct.
