# Run Workflow — extract mail into conversations

Assumes [gmail-auth.md](gmail-auth.md) is done (Gmail API enabled + gmail.readonly consented).

```bash
SKILL=resources/skills/workflow-ops/mail-to-conversations
VAULT=cbrain   # run from the repo root
```

## Step 1: Fetch (read-only)

```bash
uv run --with google-api-python-client --with google-auth-oauthlib --with google-auth \
  python3 $SKILL/scripts/fetch_gmail.py --count 100 > /tmp/mail.json
```
- Default domains are the keys of your local `schema/domain_map.yaml` (gitignored; start from `domain_map.example.yaml`); override with `--domains a.com,b.com`.
- Prints `Fetched N messages across T threads` to stderr.

## Step 2: Peek (optional)

```bash
python3 -c "import json;d=json.load(open('/tmp/mail.json'));print(d['count'],'msgs,',d['thread_count'],'threads');[print(' ',m['date'][:10],m['from_email'],'—',m['subject'][:60]) for m in d['messages'][:15]]"
```

## Step 3: Dry run (writes nothing)

```bash
python3 $SKILL/scripts/build_conversations.py --sources /tmp/mail.json --vault "$VAULT" \
  --domain-map "$(python3 scripts/employer.py path mail-to-conversations/domain_map.yaml)" --dry-run
```

## Step 4: Build

```bash
python3 $SKILL/scripts/build_conversations.py --sources /tmp/mail.json --vault "$VAULT" \
  --domain-map "$(python3 scripts/employer.py path mail-to-conversations/domain_map.yaml)"
```

## Step 5: Verify in Obsidian

- **`Mail/Conversations.md`** — the master view: each conversation (thread) with its messages newest-first and participants linked. Start here to see what belongs to which conversation.
- **`Mail/msgs/<…>.md`** — one note per email; `[[open]]` links from the index land here; each links back to its conversation + sender.
- **`Clients/<Name>.md`** — sender contacts gained a `## Mail` section listing their conversations. Existing contacts were appended to, not overwritten.

Re-running is idempotent: existing message notes are skipped; contacts get only new conversation links.
