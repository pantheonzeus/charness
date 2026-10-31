---
id: morning-briefing
aliases: [morning-briefing, daily-briefing, meeting-prep-briefing]
name: "Morning Briefing — Daily Meeting Prep + Interactive HTML"
category: workflow-ops
description: Every weekday morning, import today's calendar meetings and new relevant mail into the vault, write a vault-only prep guide onto each meeting note, assemble the briefing as a reading page (`briefing` template, with the two latest NotebookLM podcasts embedded and playable), and auto-open it in the browser. Idempotent, scheduled via launchd.
triggers: [morning briefing, daily briefing, meeting prep for today, today's meetings, prep my day, briefing html, what's on today, daily meeting prep]
tags: [workflow-ops, calendar, mail, meeting-prep, briefing, html, podcast, automation, launchd]
related: ["[[calendar-to-contacts]]", "[[mail-to-conversations]]", "[[notebooklm-daily-audio]]", "[[person-dossier]]", "[[communication-architecture]]"]
modules: [file-backed-handoff]
requires:
  tools: [bash, python, claude]
  mcp: ["workspace-mcp (Gmail + Calendar)"]
environment: "Local terminal + Google auth for the workspace-mcp server (Gmail + Calendar). Scheduled via a macOS launchd agent that runs the wrapper directly — a cloud agent would lack the local MCP auth, vault access, and the GUI session needed to open the browser."
scripts: [scripts/run_morning_briefing.sh, scripts/build_briefing_html.py]
workflows: [workflows/build-briefing.md]
status: superseded
superseded_by: meeting-prep-loop
version: 4
created: 2026-07-11
updated: 2026-10-23
vault_writes: ["cbrain/Clients/*", "cbrain/notes/[0-9]*", "cbrain/Mail/*", "cbrain/daily reports/*"]
---

# Morning Briefing — Daily Meeting Prep + Interactive HTML

> [!warning] Superseded 2026-10-11 by [[meeting-prep-loop]]
> Meeting prep now runs continuously (15-min sync + change-driven enrichment) and shows in the web console's Today view. This skill never had a live schedule here; it stays for its podcast-embedding HTML builder until that moves into the console.

Once every weekday morning, produce a briefing that's waiting on screen when the laptop
unlocks: **today's** calendar meetings and any **new relevant mail** imported into the
vault, a **prep guide per meeting** (participants, title, description, the themes those
people share, talking points, smart questions), assembled into the reading page
`output/morning-briefing/<YYYYMMDD>.html` (content in the same-stem `.md`, `briefing` template
from [[reading-pages]]) with the **two latest NotebookLM podcasts**
embedded and playable — then auto-opened in the browser.

Two halves, split by what they need — the same shape as [[notebooklm-daily-audio]]:
- **Mechanical (Python, launchd-safe):** `build_briefing_html.py` reads today's meeting
  notes + the newest podcasts, writes the page content (`<date>.md`, `template: briefing`)
  and renders it with `reading-pages/scripts/page.py` to the self-contained HTML. Deterministic,
  no judgment, and no styling of its own: the look comes from `webapp/design/`.
- **Judgment (headless Claude):** [`workflows/build-briefing.md`](workflows/build-briefing.md) — a file-backed headless handoff (Charter §5, [`_shared/delegation-handoff.md`](../../_shared/delegation-handoff.md)) — the workflow file is the task packet, context mode **fresh**; the child writes its result to `output/.runs/<YYYYMMDD>-morning-briefing/children/build/RESPONSE.md`, which `run_morning_briefing.sh` reopens into the job log —
  imports today's calendar + new mail (reusing the [[calendar-to-contacts]] and
  [[mail-to-conversations]] builders) and writes the vault-only prep onto each meeting
  note. Semantic matching never lives in Python.

**Triggers/Context**
- On demand: "build my morning briefing", "prep my day", "what's on today".
- Automatically: a bundled `launchd` agent fires every weekday at ~06:33 → runs the
  wrapper → builds + opens the HTML.

**Core Blueprint** (full detail in [`workflows/build-briefing.md`](workflows/build-briefing.md))
1. **Import today's calendar.** MCP `list_calendar_events` for today's local-day window →
   `calendar-to-contacts` adapter + `build_contacts.py` → `notes/<date>-*.md` + attendees.
2. **Import new mail.** MCP `search_gmail_messages` (partner domains, `newer_than:2d`) →
   `mail-to-conversations` adapter + `build_conversations.py --exclude-noise`. Filename
   dedup = the "not yet imported" check.
3. **Per-meeting prep (vault-only).** For each of today's meeting notes, harvest attendees'
   `Clients/` notes + topic anchors + mail history (person-dossier recall), synthesise
   shared themes + prep guide + smart questions, and **append** an `mb-prep` JSON block
   (+ readable markdown) to `## My Notes`.
4. **Build the page.** `build_briefing_html.py --date <date>` →
   `output/morning-briefing/<date>.md` (content) → `<date>.html` (rendered), with the 2 newest
   `output/podcasts/*.m4a` as an `audio` block. Also readable in the console at
   `/page/morning-briefing/<date>.md`.
5. **Log** a line under `## Knowledge Graph` in the daily report.

The wrapper `run_morning_briefing.sh` runs the headless workflow, then `open`s the HTML
(building a fallback page from on-disk notes first if the workflow couldn't).

## Quick Start
```bash
# Build just the HTML for a day (deterministic, reads existing notes + podcasts)
python3 resources/skills/workflow-ops/morning-briefing/scripts/build_briefing_html.py --date 2026-07-09

# Full run for today (headless import + prep + HTML + open browser)
bash resources/skills/workflow-ops/morning-briefing/scripts/run_morning_briefing.sh
bash resources/skills/workflow-ops/morning-briefing/scripts/run_morning_briefing.sh 2026-07-09   # a specific day
```

## Scheduling (macOS launchd) — weekday mornings
Runs the wrapper Mon–Fri at ~06:33 (off-minute so it isn't on the hour). `StartCalendarInterval`
is an **array** of five dicts (`Weekday` 1–5 = Mon–Fri). Point `<REPO>`/`<you>` at your paths.
On a sleeping Mac, launchd fires the missed job on wake — so the tab is there shortly after unlock.

`~/Library/LaunchAgents/com.cbrain.morning-briefing.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>              <string>com.cbrain.morning-briefing</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string><REPO>/resources/skills/workflow-ops/morning-briefing/scripts/run_morning_briefing.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>6</integer><key>Minute</key><integer>33</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>6</integer><key>Minute</key><integer>33</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>6</integer><key>Minute</key><integer>33</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>6</integer><key>Minute</key><integer>33</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>6</integer><key>Minute</key><integer>33</integer></dict>
  </array>
  <key>StandardOutPath</key>     <string><REPO>/output/morning-briefing.log</string>
  <key>StandardErrorPath</key>   <string><REPO>/output/morning-briefing.log</string>
  <!-- `claude` and `python3` live in ~/.local/bin / Homebrew; ensure both are on PATH -->
  <key>EnvironmentVariables</key>
  <dict><key>PATH</key><string>/Users/<you>/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string></dict>
</dict>
</plist>
```
```bash
launchctl load  ~/Library/LaunchAgents/com.cbrain.morning-briefing.plist   # register
launchctl start com.cbrain.morning-briefing                                # fire once now
launchctl list | grep morning-briefing                                     # confirm registered
launchctl unload ~/Library/LaunchAgents/com.cbrain.morning-briefing.plist  # remove
```

**Optimizations/Gotchas**
- **MCP auth is the single point of failure.** The live calendar/mail pull needs the
  `workspace-mcp` server running (kept alive by `com.cbrain.workspace-mcp`) and Google
  OAuth consented (tokens at `~/.google_workspace_mcp/credentials/`). If it lapses the
  import silently no-ops — check `output/morning-briefing.log`. The HTML still builds from
  whatever notes are already on disk (the wrapper's fallback), so a page always opens.
- **"Latest 2 podcasts" is by filename desc** (names lead with `YYYYMMDD`), so it's
  deterministic even when several share a date. `.m4a`/AAC plays natively in Safari &
  Chrome; the `src` is relative (`../podcasts/…`) so the file opens fine via `file://`.
- **Prep block is the contract.** The generator parses the `mb-prep` JSON comment in each
  meeting note's `## My Notes`; if it's absent it falls back to the note's raw sections, so
  running `build_briefing_html.py` standalone still renders. Keep the JSON valid.
- **Idempotent throughout.** Meeting notes / contacts / mail dedup by filename; the prep
  step skips a note that already has today's `mb-prep` block. Safe to re-run the same day.
- **PATH in launchd.** launchd agents get a minimal env; the plist sets `PATH` so `claude`
  and `python3` resolve. `open` runs in the user's GUI (Aqua) session, so the browser
  launches even while the screen is locked.
- **Repo-root path.** Both scripts resolve the repo root from their own location
  (`parents[5]` in Python, `../../../../..` in the wrapper), not cwd, so launchd's minimal
  cwd doesn't matter. If you move a script in the tree, fix that offset.
- **Vault-only by design.** Prep uses only the knowledge graph — no web calls — so the
  daily run is fast, free, and reliable unattended. For a genuinely high-stakes external
  meeting, run [[company-challenger-brief]] by hand for the deeper, cited version.
