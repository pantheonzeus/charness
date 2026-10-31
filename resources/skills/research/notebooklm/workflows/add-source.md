# Add Source Workflow

Add one (or a few) sources — a YouTube video, a web URL, a local file, or pasted text —
**into** a NotebookLM notebook. This is the inbound direction: content → NotebookLM.
(For the reverse — pulling an existing notebook's sources *out* into the vault — use
[import.md](import.md). For bulk-loading a whole channel, use
[youtube-channel.md](youtube-channel.md).)

Uses the `nlm` CLI, which is on PATH and handles auth itself (`nlm login` if it errors).

## Inputs

- **url / youtube / file**: what to add
- **notebook-id**: an existing notebook (`nlm notebook list --json`), or create one first

## Step 1 (optional): Create the notebook

```bash
nlm notebook create "The Notebook Title" --json
```

**Gotcha — the id key is `notebook_id`, not `id`.** The JSON is
`{"notebook_id": "…", "title": "…", "url": "…", "message": "…"}`. Extracting `.id`
returns empty and every downstream `nlm` call then fails with `INVALID_ARGUMENT`.

```bash
NB_ID=$(nlm notebook create "The Notebook Title" --json | jq -r '.notebook_id')
```

## Step 2: Add the source

```bash
# YouTube (public videos with captions)
nlm source add "$NB_ID" --youtube "https://www.youtube.com/watch?v=VIDEO_ID" --wait

# Web page
nlm source add "$NB_ID" --url "https://example.com/article" --wait

# Local file (PDF, etc.)
nlm source add "$NB_ID" --file document.pdf --wait

# Multiple at once (flags repeat)
nlm source add "$NB_ID" --youtube "https://youtu.be/a" --youtube "https://youtu.be/b" --wait
```

- `--wait` blocks until NotebookLM finishes processing and prints the source id + `ready`.
  Omit it to fire-and-forget. Raise `--wait-timeout` (default 600s) for very long audio.
- YouTube requires a **public** video with captions; otherwise the add fails with a
  "Could not add url source" / `INVALID_ARGUMENT` hint.

## Step 3: Verify

```bash
nlm source list "$NB_ID" --json
```

Confirm the new source appears with the expected `title` and `type`.

## Notes

- Both `nlm` and `notebooklm` are on PATH — no `cd`/`uv run` wrapper is needed.
- One-liner for the common case (add a YouTube video to an existing notebook):
  `nlm source add <notebook-id> --youtube "<url>" --wait`
