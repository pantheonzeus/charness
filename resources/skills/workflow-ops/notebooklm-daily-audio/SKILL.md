---
id: notebooklm-daily-audio
aliases: [notebooklm-daily-audio]
name: "NotebookLM — Daily Audio Overviews"
category: workflow-ops
description: Find every NotebookLM notebook touched today that has no audio overview yet, generate a deep-dive podcast for each, download the finished .m4a into output/podcasts/, and also fetch each notebook's text summary — then a second headless job distills those summaries into linked topic notes in the vault. Idempotent, scheduled daily via launchd.
triggers: [daily audio overview, notebooklm audio, new notebooks audio, generate podcasts, download podcast, save audio overview, audio overview today, daily notebook podcast, notebook summary to vault, distill notebook summary, link notebook to people]
tags: [workflow-ops, notebooklm, audio, podcast, download, summary, knowledge-graph, automation, launchd]
related: ["[[notebooklm]]", "[[source-distillation-topic-note]]", "[[topic-based-linking]]"]
modules: [file-backed-handoff]
requires:
  tools: [bash, python, claude]
  cli: ["nlm (notebooklm-mcp-cli)"]
environment: "Local terminal + Google auth for `nlm` (cookies). Scheduled via macOS launchd agents that run the bundled scripts directly — a cloud agent would lack the local auth and vault access."
scripts: [scripts/daily_audio.py, scripts/distill_to_vault.sh]
workflows: [workflows/distill-to-vault.md]
status: active
version: 5
created: 2026-07-07
updated: 2026-10-23
vault_writes: ["cbrain/projects/*", "cbrain/Clients/*", "cbrain/notes/[0-9]*", "cbrain/daily reports/*"]
---

# NotebookLM — Daily Audio Overviews

Extends the [[notebooklm]] skill. Once a day, sweep every notebook that was touched today and — if it has no audio overview yet — kick off a `deep_dive` podcast, **download the finished audio into `output/podcasts/`**, and **fetch each notebook's text summary** next to it. A **second headless job** then distills those summaries into linked topic notes in the vault (see the [Distill to vault](#distill-to-vault-second-job) section). Idempotent throughout — running repeatedly (or after a partial failure) never duplicates a generation, re-downloads a file on disk, re-writes a summary, or spawns a duplicate topic note.

Two halves, split by what they need:
- **Mechanical (Python, cron-safe):** `daily_audio.py` generates + downloads audio and writes each notebook's raw summary — deterministic, no judgment.
- **Judgment (headless Claude):** a file-backed handoff (Charter §5, [`_shared/delegation-handoff.md`](../../_shared/delegation-handoff.md)) — task packet = the versioned [`workflows/distill-to-vault.md`](workflows/distill-to-vault.md), context mode **fresh**; the child writes its result to `output/.runs/<YYYYMMDD>-nlm-distill/children/distill/RESPONSE.md`, and `distill_to_vault.sh` reopens that file into the job log (and warns if it is missing). `distill_to_vault.sh` reads those summaries and connects each to the *relevant* people and meetings in the knowledge graph — reusing [[source-distillation-topic-note]] and [[topic-based-linking]]. Semantic matching never lives in Python. Handoff is file-backed per Charter §5 ([`_shared/delegation-handoff.md`](../../_shared/delegation-handoff.md)) — the job reads its brief and writes results through files, not an inline reply.

**Triggers/Context**
- On demand: "generate audio overviews for today's notebooks", "notebooklm daily audio", "distill today's notebook summaries into the vault".
- Automatically: two `launchd` agents — `com.cbrain.notebooklm-daily-audio` (audio + summary, 18:00) and `com.cbrain.notebooklm-distill-vault` (distill to vault, 18:30, installed 2026-10-23; writes the vault unattended, held to `.claude/agents/nlm-distill.md` `write_scopes:`, each run committed to the vault history as `nlm-distill`).

**Core Blueprint**
1. `nlm notebook list --json` → all notebooks (`{id, title, source_count, updated_at}`).
2. Keep notebooks whose `updated_at` (UTC) converts to **today's local date** (override with `--date YYYY-MM-DD`). There is no `created_at` in the CLI — `updated_at == today` is the proxy for "new/touched today".
3. **Create phase.** For each candidate, `nlm studio status <id> --json` → **skip** if an audio artifact already exists (idempotency); otherwise `nlm audio create <id> -f deep_dive -l default --language en -y`.
4. **Download phase** (skip with `--no-download`). For each matched notebook, poll `studio status` until an audio artifact reports `completed` (bounded by `--wait-timeout`, default 900s; `0` = don't wait, grab only what's already done), then `nlm download audio <id> -o output/podcasts/<YYYYMMDD>-<slug>.m4a`. Skips any file already on disk.
5. **Summary phase** (skip with `--no-summary`). For each matched notebook, `nlm describe notebook <id> --json` → parse `summary` + `topics`, and write `output/podcasts/<YYYYMMDD>-<slug>.summary.md` (same stem as the audio). Idempotent by filename. The file carries frontmatter (`notebook_id`, `notebook_title`, `topics`, `audio`, `distilled: false`) — it is the **queue** the distiller consumes.
6. Print a summary: `matched N · created K · skipped M · downloaded D · on-disk O · pending P · summarized S · summary-on-disk SO · errors E`. Non-zero exit if any create, download, or summary fetch failed.

Generation is **asynchronous** — a freshly created overview is `in_progress` for a few minutes, which is why the download phase polls before pulling the file. Downloads land in `output/podcasts/` (repo root, resolved from the script's own path so launchd's cwd doesn't matter) and are **git-ignored** (`.gitignore` excludes `output/`; audio ~35–45 MB each). The `.summary.md` files sit alongside them — a transient handoff queue; the durable artifact is the vault topic note the distiller writes.

<a id="distill-to-vault-second-job"></a>
### Distill to vault (second job)
The summary phase only *fetches* the text. Connecting it to the *right* people and meetings is judgment, so it runs as a separate headless Claude job — [`scripts/distill_to_vault.sh`](scripts/distill_to_vault.sh) driving [`workflows/distill-to-vault.md`](workflows/distill-to-vault.md):
1. Read today's `output/podcasts/<YYYYMMDD>-*.summary.md` where `distilled: false` (exit cleanly if none).
2. Distill each into a `type: topic` note in `cbrain/projects/` modeled on `cbrain/projects/AI SDLC.md` — Primary-source callout (citing the `notebook_id`, the dedup key), TL;DR, frameworks, angles.
3. **Wire bi-directional links**: scan `cbrain/Clients/` (people/accounts) and `cbrain/notes/` (meetings) for genuine matches; add `Topic: [[<Topic>]] — <reason>` on each and reciprocate on the topic note.
4. Log a line in `cbrain/daily reports/<YYYYMMDD>.md` and flip the summary's `distilled: true`.

Guardrails (it edits the vault unattended): link only **existing** people/meetings (never invent a contact from a source), clear matches only, **append never overwrite**, one topic note per `notebook_id`. Everything is logged in the daily report, so a run is reviewable the next morning.

## Quick Start
```bash
cd resources/skills/workflow-ops/notebooklm-daily-audio

# Preview today's targets — creates/downloads nothing
python3 scripts/daily_audio.py --dry-run

# Live run (today): create missing overviews, wait, download to output/podcasts/
python3 scripts/daily_audio.py

# A specific date, or different format/length/language
python3 scripts/daily_audio.py --date 2026-07-07 --format brief --length short --language de

# Only create overviews, don't download; or download only what's already finished
python3 scripts/daily_audio.py --no-download
python3 scripts/daily_audio.py --wait-timeout 0

# Skip the summary phase (audio only)
python3 scripts/daily_audio.py --no-summary

# Save somewhere other than output/podcasts/
python3 scripts/daily_audio.py --podcast-dir ~/Music/notebooklm

# Distill today's fetched summaries into linked vault notes (headless Claude)
bash scripts/distill_to_vault.sh                 # today
bash scripts/distill_to_vault.sh 2026-07-07      # a specific date
```

## Scheduling (macOS launchd)
Runs the script daily at 18:00. Point `<REPO>` at the absolute path of this checkout (e.g. `/Users/<you>/GitHub/cbrain`).

`~/Library/LaunchAgents/com.cbrain.notebooklm-daily-audio.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>              <string>com.cbrain.notebooklm-daily-audio</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string><REPO>/resources/skills/workflow-ops/notebooklm-daily-audio/scripts/daily_audio.py</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key>     <string><REPO>/output/notebooklm-daily-audio.log</string>
  <key>StandardErrorPath</key>   <string><REPO>/output/notebooklm-daily-audio.log</string>
  <!-- `nlm` lives in ~/.local/bin; ensure it's on PATH for the agent -->
  <key>EnvironmentVariables</key>
  <dict><key>PATH</key><string>/Users/<you>/.local/bin:/usr/local/bin:/usr/bin:/bin</string></dict>
</dict>
</plist>
```
```bash
launchctl load  ~/Library/LaunchAgents/com.cbrain.notebooklm-daily-audio.plist   # register
launchctl start com.cbrain.notebooklm-daily-audio                                # fire once now
launchctl list | grep notebooklm                                                 # confirm registered
launchctl unload ~/Library/LaunchAgents/com.cbrain.notebooklm-daily-audio.plist  # remove
```
Alternative (crontab, daily 18:00):
```
0 18 * * * /usr/bin/python3 <REPO>/resources/skills/workflow-ops/notebooklm-daily-audio/scripts/daily_audio.py >> <REPO>/output/notebooklm-daily-audio.log 2>&1
```

### Second agent — distill to vault (daily 18:30, installed 2026-10-23)
Runs `distill_to_vault.sh` half an hour after the audio job, so the summaries exist. The wrapper resolves the repo root from its own path and exits early when there are no fresh summaries.

`~/Library/LaunchAgents/com.cbrain.notebooklm-distill-vault.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>              <string>com.cbrain.notebooklm-distill-vault</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string><REPO>/resources/skills/workflow-ops/notebooklm-daily-audio/scripts/distill_to_vault.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>30</integer></dict>
  <key>StandardOutPath</key>     <string><REPO>/output/notebooklm-distill-vault.log</string>
  <key>StandardErrorPath</key>   <string><REPO>/output/notebooklm-distill-vault.log</string>
  <!-- `claude` and `nlm` live in ~/.local/bin (and Homebrew); ensure both are on PATH -->
  <key>EnvironmentVariables</key>
  <dict><key>PATH</key><string>/Users/<you>/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string></dict>
</dict>
</plist>
```
```bash
launchctl load  ~/Library/LaunchAgents/com.cbrain.notebooklm-distill-vault.plist
launchctl start com.cbrain.notebooklm-distill-vault      # fire once now
```
Crontab alternative (daily 18:30):
```
30 18 * * * /bin/bash <REPO>/resources/skills/workflow-ops/notebooklm-daily-audio/scripts/distill_to_vault.sh >> <REPO>/output/notebooklm-distill-vault.log 2>&1
```

**Optimizations/Gotchas**
- **Prefixes it skips.** `Idea · ` (idea-engine) and `Daily Intel · ` (daily-intel-briefing learning podcasts) notebooks download their own audio and are never distilled here.
- **No `created_at`.** Only `updated_at` exists, so a notebook merely *edited* today also matches — acceptable, and the "no audio yet" check keeps it from generating twice.
- **UTC → local.** `updated_at` ends in `Z`; the script converts to the machine's local date before comparing, so a late-night notebook lands on the right day.
- **Idempotency.** Detection matches a `studio status` artifact whose `type`/`name`/`title` contains "audio" or "overview". Confirmed against the live shape `{"type": "audio", "status": "in_progress"}` — an in-progress overview counts, so a re-run won't re-trigger while generation is underway.
- **Auth expiry.** A launchd run fails silently if the `nlm` Google cookies expire — that's why output is logged to `output/notebooklm-daily-audio.log`. If audio stops appearing, re-auth per the [[notebooklm]] skill (`nlm login`) and check the log.
- **PATH in launchd.** launchd agents get a minimal environment; the plist sets `PATH` so `nlm` (in `~/.local/bin`) resolves.
- **Async wait blocks the run.** The download phase polls until each freshly-created overview finishes (up to `--wait-timeout`, default 900s), so a live run with new notebooks can take several minutes. Acceptable for an 18:00 launchd job. Overviews that don't complete in time are reported `PENDING` and picked up on the next run (their file still isn't on disk). Use `--wait-timeout 0` for a fast pass that downloads only already-completed audio.
- **Download idempotency & size.** Files are named `output/podcasts/<YYYYMMDD>-<slug>.m4a`; an existing file is never re-downloaded. Each is ~35–45 MB, so they're git-ignored — don't remove that `.gitignore` rule or you'll commit binaries daily.
- **Repo-root path.** The output dir resolves from the script's own location (`parents[5]` in Python, `../../../../..` in the shell wrapper), not cwd, so it works under launchd. If you move a script within the tree, fix that offset.
- **Summary source.** The text summary comes from `nlm describe notebook <id> --json` (`summary` + `topics`). It's fetched independent of audio completion, so `--no-download --wait-timeout 0` still produces summaries fast. Idempotent by filename — an existing `.summary.md` is never re-fetched.
- **The two jobs are ordered, not coupled.** Audio+summary at 18:00, distill at 18:30. The distiller only needs the `.summary.md` files, so if the audio job is still waiting on a slow generation the summaries are usually already written. The distiller exits cleanly when no fresh summaries exist, so an empty day is a no-op.
- **Headless edits the vault.** `distill_to_vault.sh` runs `claude -p … --permission-mode acceptEdits`, so it writes notes unattended. The workflow's guardrails (existing people/meetings only, append-only, one note per `notebook_id`) plus the daily-report log keep it bounded and reviewable. If `claude`'s cookies/auth or the `nlm` cookies expire, the run fails silently — check `output/notebooklm-distill-vault.log`.
