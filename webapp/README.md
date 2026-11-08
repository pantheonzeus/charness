# cbrain console

A local web UI for running the harness from the browser. The conversation is one long-lived `claude -p` process (stream-json in and out) started from the repo root, so it gets the full harness: Charter, Soul, the SessionStart hooks, the write-boundary and control-spine hooks, memory and the skill index. It runs on your claude.ai subscription, not the API, because the server strips `ANTHROPIC_API_KEY` from the child's environment.

```bash
uv run webapp/server.py        # → http://127.0.0.1:8765   (CBRAIN_WEB_PORT to change)
```

Always on: `webapp/com.cbrain.webapp.plist` runs it under launchd (starts at login, restarts on exit, logs to `output/webapp.log`). Install it with `cp webapp/com.cbrain.webapp.plist ~/Library/LaunchAgents/ && launchctl load ~/Library/LaunchAgents/com.cbrain.webapp.plist`. To restart after a code change, run `scripts/jarvis.sh restart`; `scripts/jarvis.sh stop|start|status` for the rest (killing the process does nothing: KeepAlive restarts it).

## What it does: one page, Jarvis and the work
**One voice page.** On the left is Jarvis: her rings carry the voice state, with what she just said or heard, *what needs you* in her order, and the conversation. On the right is **the stage**: the one thing you two are looking at.
- **Who fills the stage.** Jarvis fills it when nobody else has chosen. A meeting starting within 30 min comes first, then the most pressing worthwhile item from her urgency × importance queue, else **today** (the next meeting, today's reading, your tasks). The head line says whose pick it is and why.
- **You move it by voice.** The Chief of Staff routes every request and moves the stage with a `[[stage: …]]` directive in its reply. The directive is stripped before anything is shown or spoken. You can also click an item in Jarvis's list. Your choice (or the Chief of Staff's) holds for 20 min after the last turn, then Jarvis takes over again.
- **"Bring me to …" also brings the console up.** "Bring me to the app" / "the start screen" puts today on stage and brings the Chrome tab to the front (or opens one), via `[[open: today]]`. "Bring me to <topic>" first looks for a vault topic (`cbrain/projects/`, stage ref `topic:<name>`), then for a deliverable (`doc:<library id>`). If neither exists, the Chief of Staff starts a `kind: topic` task (`workflow-ops/topic-build`, no questions). When it's done, Jarvis says it's ready; this knock doesn't count against her budget. "Go there" then opens it. On stage, a topic's `[[links]]` to other topics, its deliverables and its "Linked from" list are all clickable.
- **Overruling her teaches her.** Moving the stage off her pick is logged as a correction (`via: redirect` in the ratings ledger), and she learns your bar from it. Opening a view or today isn't: that's logged as `via: navigate` and never taught, and her scorecard counts only your explicit calls. There's no rating ceremony. On a staged item, **Done · Later · Noise** close it and she picks the next one.
- **Plan is the default.** Research, search, "find out", an outcome, or anything that commits you to a number, a position or a client message becomes a living plan. Before starting one, the Chief of Staff challenges you live by voice: up to three hard questions, one at a time (the decision and who makes it, the number you'd defend today, what would prove you wrong). A dodge gets one sharper follow-up; "skip" plans anyway with the gaps named as assumptions. The answers go into the plan's `TASK.md` under `## Interrogation`, so the background team goes straight to the plan preview.
- **Questions about your day or a meeting** get answered first, with the thing on stage, then one hard question back (what you want out of it, who says no). Pure logistics get no question.
- **Everything else only on purpose.** Plans, Mail, Library, Ideas, Situation and earlier conversations sit behind **⋯** (top right), or you say "open mail". `?view=plans|mail|library|ideas|situation` and `?p=<plan id>` open a place directly.

One calm stage instead of a dashboard. It's designed from the research in `output/20261011-future-ui-concepts.html` (direction A, "the room"). Every motion encodes real state and has a static version under reduced motion or reduced transparency.

- **Edge light: the voice channel.** The screen border shows the voice state:
  - a faint hairline during the 5 s follow-up window
  - brighter with your actual mic level as you talk
  - a travelling shimmer while it's thinking
  - following the actual playback signal while it speaks
  - a hard cool flash when you barge in
- **Today.** The idle stage: the next meeting (the countdown, the one point to raise, who's in it, and Join / 🎙 Prep me / Everything on it), later meetings, today's reading (the Analyst's briefing, the latest Slack digest) and your tasks.
- **Conversation** (left column, under Jarvis). One live Claude session with the full harness, speaking as the Chief of Staff. Older exchanges fade. An answer with shape (a surface) goes on stage. A **karaoke caption** lights up each word as it's spoken. **Hold Right ⌥ (anywhere) or the 🎙 button to talk**, or type and press Enter. Spoken turns get spoken replies; typed turns stay on screen. **▶ Brief me** gives a spoken rundown, Space interrupts, and **history** (top right) lists earlier conversations. `?s=<session id>` reopens one directly.
- **Constellation: the team.** Four lights. Each rhythm is a real loop state, and clicking a light opens its panel.
  - **Chief of Staff** flares on every 15-minute sync and pulses while it's preparing.
  - **Analyst** is lit when today's briefing exists and dim when it doesn't.
  - **Researcher** pulses while working and gets a ring when it needs you.
  - **Ops** beats like a heart, and a stopped beat in red is the alarm.
- **Island.** At most two decision pills at the top: a Researcher question, a stopped loop, a failing calendar sync, recurring run failures.
- **Run forensics** (`workflow-ops/run-forensics`). Every agent run is classified as clean / degraded / failed with failure codes read from its transcript (`run_agent.sh` → `forensics.py ingest`). A code that recurs (≥ 2 runs in 7 days) becomes an issue in the Ops panel's **Recurring failures** table and an island pill. Say "fix <CODE>": the fix is a small harness edit, then `forensics.py fixed`, and the next runs verify it. A fix that doesn't hold turns the pill red. Daily report at 07:20: `output/run-forensics/report-<date>.md`.
- **Glance line.** The day in one sentence across the top.
- **Interruption budget.** From five minutes before a meeting until it ends, no toasts or browser notifications pop up. The island and the lights still show what's waiting.
- **Living plans** (`workflow-ops/living-plan`). Say it in the conversation (the default: the Chief of Staff challenges you by voice, then starts the plan), or use **⋯ → Plans → + New plan**. A quick answer from the vault is just done inline.
  - **Hard questions first.** Started by voice, the Chief of Staff has already asked them (see above). Started from the form, the team reads your vault before any research and asks 3–5 questions specific to this outcome: the decision and who makes it, the number you'd commit to today, what would prove you wrong, and who says no. Each question says why it matters. If you dodge a load-bearing one, you get at most one sharper follow-up. **Skip the questions** (or tick "skip the hard questions" on the form) plans anyway and names the gaps as assumptions. Your answers stay visible in the plan under "What you told the team".
  - **Plan preview next.** The team drafts a plan before any work starts, showing the deliverable shape, the steps and who owns each one, planned sources, an estimate, and the riskiest assumption up front. It opens in **Plans** or from the island pill. Edit it in place: rename, click an owner chip to reassign, ↑ to reorder, × to remove, + to add, ◆ for a checkpoint. Then **Go**.
  - **The run.** It works step by step in the shared `PLAN.json`. The light of whichever role owns the running step pulses. It pauses only at checkpoints it placed itself, each with its stakes stated, and at steps you own.
  - **Findings show confidence.** Verified has a solid green underline, likely is dotted, and unsure is wavy and visibly rougher.
  - **Built from:** every source it read, each with **stale / wrong** buttons. A flag makes the team stop trusting that source and appends a dated warning to the vault note. The deliverable lands in `output/plans/`.
  - **Harness upgrades** (`workflow-ops/harness-upgrade-scout`). A built upgrade pauses in Plans with **Open the review page**, **Apply** and **Discard**. No agent runs either one. Apply lays the change onto your checkout as uncommitted edits, so `git diff` stays your review, then removes the worktree and branch. Discard removes them unapplied. A patch that no longer applies stops the task with git's message, which also gives the terminal command to discard it. Typed text at this pause goes to the builder as a question and changes nothing.
- **The situation** (`workflow-ops/situation-surfaces`). Answers become interfaces, built from the desk's own catalog: Callout, MetricRow, RiskSheet, StakeholderMap, Timeline, DecisionCard, PersonCard, DocList. Agents write JSON that picks components; the desk renders it; no generated code runs. Every block shows its confidence (solid / dotted / dashed and faded) with its sources, plus "Built from" underneath.
  - **New for them:** each morning at 05:45 the vault-frontier loop (`research/vault-frontier-loop`) searches the web for what changed on the topic notes linked to the people you meet. It appends dated, cited entries to the vault. The meeting prep then picks at most one finding per meeting, client-safe only when someone external is present. That finding shows in the focus slot as **New for them** and becomes the first talking point.
  - **Slack intel** (`workflow-ops/slack-intel`): weekdays 08–20 at :05, the Chief of Staff reads the channels in the active employer pack's `slack-intel/channels.json`. The read goes through the claude.ai Slack connector, with read-only tools. It judges each new post against the vault and keeps only new knowledge, then researches it from 2–4 sources. Each run with something new writes one cited digest (`output/slack-intel/briefings/`, a briefing page indexed into the vault). The Chief of Staff light pulses while it reads and flares when a digest lands. Its panel lists the digests.
  - **Follow-through** (`sales/client-follow-through`): a meeting with external participants that ended in the last 10 hours shows **✉ Draft follow-up**. Type what was agreed, and the conversation drafts the email to `output/client/followups/`. Upcoming external meetings get **Client brief**, a one-page leave-behind from public sources only, in `output/client/briefs/`. Both pass a confidentiality gate and are never sent.
  - **Send email**: ask the conversation to mail someone. It looks up the address in the vault, reads the mail back, and sends via the workspace-mcp Gmail tools only after you say "send" ("draft" leaves it in Gmail Drafts). Needs workspace-mcp running and authorized with Gmail send scope.
  - **Meetings:** the meeting-prep loop composes each meeting's surface ahead of time, together with the prep. A meeting that's already prepped gets a cheaper surface-only run. It appears in the focus slot and at the top of the meeting panel.
  - **Answers:** when an answer has shape (stakeholders, risks, a timeline, a decision), the conversation writes `output/surfaces/…json` and the desk renders it under the answer.
  - **Canvas:** **situation** (top right, or `?view=situation`) lays out meetings across time, their people around them, documents beneath and open plans aside. Drag anything onto anything:
    - a person onto a meeting asks what to raise;
    - a document onto a meeting asks what matters;
    - a person onto a person asks how they're connected;
    - anything onto a plan feeds it;
    - anything onto the Researcher's light starts research.

    The answer arrives in the conversation.
- **Library** (`webapp/library.py`, `?view=library`). Every deliverable in `output/`, newest first by month. The catalog is the vault's deliverable index (`cbrain/notes/Deliverables/`, kept by `vault-hygiene/deliverable-index`), so a file shows up once that index has run. The console runs it when a plan or research task finishes.
  - **Filter** by type (Documents is the default, which hides LinkedIn drafts and image bundles) and by the vault entities the deliverables link to.
  - **Find by words:** type, and an in-memory SQLite FTS5 index over the full text answers instantly with highlighted snippets.
  - **Ask by meaning:** press Enter, and one `claude -p --model haiku` call ranks the whole catalog (titles and TL;DRs) against your question, with a reason line per hit. It takes ~15 s on your seat. It runs outside the repo with no tools, so no hooks load and nothing is written.
  - **Read:** a click opens it in the panel. Markdown renders in place; HTML opens in a sandboxed frame; PDFs open inline. You also get **Open as page** (templated docs), **Open full**, **Open in app** (Word, Keynote, Preview) and **Ask about it** (prefills the conversation).
  - **Plan from these:** tick several, from any search; the selection persists. Then state the outcome in the tray. The plan's `TASK.md` gets a `## Sources` list. `living-plan` reads those first, asks its questions against them, and lists them as receipts.
- **Ideas** (`workflow-ops/idea-engine`, `?view=ideas`). Like Mail, but for ideas. Weekdays at :35, the idea engine turns what changed in the vault into four kinds of idea: LinkedIn post topic, learning, research, status-quo challenge. The view groups them by type; the badge counts new ones. Each idea offers:
  - **Acknowledge:** seen, off the list.
  - **Dive deeper:** a Researcher task on the idea; its progress and then **Open report** show on the card.
  - **Ask a question:** answered on the card in ~30 s from the idea, its vault sources and the web, and saved to the idea note.
  - **Twist & dive deeper:** your reframe leads the research.
  - **🎧 Podcasts:** a NotebookLM notebook on the idea, then an in-depth and a short episode on the central idea. Both play on the card when ready (10–30 min). Only gated text and public URLs go up (`idea-engine` skill).
- **Mail** (`workflow-ops/mail-triage`, `?view=mail`). A launchd poll checks Gmail every minute for mail from the companies in the active employer pack's `mail-triage/companies.json` (employers/README.md). A headless agent triages each new mail. The view groups mail by company, then into **To know** (summary), **Action needed** (summary and the action) and **Answer needed** (summary and an editable reply draft in your voice).
  - **Approve & send** sends the reply in the original thread, from your account. It asks you to confirm first, and it refuses while a `[confirm: …]` placeholder remains.
  - Mail you answer directly in Gmail drops off the list on its own.
  - The badge on **Mail** counts the open answers.
  - Sending needs a one-time `gmail.send` consent: run `uv run resources/skills/workflow-ops/mail-triage/scripts/triage.py auth-send` in a terminal.
- **Panels.** Solid "paper" slides in from the right with everything in full: meeting prep and people notes, the briefing with 👍/👎, Ask and Save, Researcher tasks with answer boxes and reports, Ops loops and cost.

### Pages: what people read, in five fixed templates
Content and design never mix. An agent writes only **content**: an `output/**.md` with `template: briefing | report | decision | plan | dossier` in its frontmatter, `## ` sections and optional typed blocks (```` ```metrics ````, ```` ```options ````, ```` ```audio ````, …, JSON inside). `resources/skills/workflow-ops/reading-pages/scripts/page.py` (skill `reading-pages`) maps each section to its template slot by heading and fills the template. The **design** lives only in `webapp/design/`: `theme.css`, `templates/*.html` and the slot registry `templates.json`. Change the look there once, and every page follows.
- `uv run …/reading-pages/scripts/page.py spec` prints the contract; `check <file.md>` shows which heading went to which slot; `render <file.md>` writes a self-contained same-stem `.html`, which `scripts/render.py pdf` then prints.
- The console renders live at `/page/<path under output/>`, and `/pages` lists every templated page, newest first. A research or plan report with a template gets **Open as page** in its panel.
- Pages never run script (CSP `default-src 'none'`), and raw HTML in content is shown as text.

### The look: JARVIS skin (`webapp/static/hud.css`)
A cinematic HUD laid over the same page, in three layers:
- **Ambient chrome** (decorative, `aria-hidden`): a grid, corner brackets, and a slow scan sweep. Jarvis's core rings (top of the left column) change speed and colour with the voice state.
- **Instruments:** the mode readout, the segmented rail, diamond crew glyphs, and the reticle you hold to talk.
- **Reading plates:** opaque, ≥ 10:1 contrast for body text, no motion under text.

**Colour:** cyan for instruments, amber only for *you* (needs-you, the shield), red for broken. **Type:** Antonio / Barlow Condensed / IBM Plex Sans and Mono, vendored in `static/vendor/fonts/`, so nothing loads from the internet. The skin is dark-only. In a meeting the chrome freezes (0 fps) and turns amber. With reduced motion the animations stop; with reduced transparency the chrome is hidden.

### JARVIS: audio by default, quiet only when you say so (`webapp/presence.py`)
**Audio is the default. Nothing goes quiet on its own.** A native helper (`webapp/native/presence.swift`) still reports which processes use the mic, the output device, sleep/wake and the Right ⌥ hotkey. `webapp/presence.py` combines that with the calendar and an open Meet tab, but only to *show* what it sees on the chip (ON AIR · IN A CALL, ON AIR · MEETING ON THE CALENDAR). It never mutes, closes the mic, blanks the screen or stops a knock by itself.
- **Quiet is your call.** Say "be quiet" / "mute" / "stop talking for an hour" (60 min if you give no time, at most 10 h), or use **Shield** in the Voice & presence panel. Replies then stay on screen and Jarvis doesn't knock. The mic stays yours, so you can say "talk again" to end it.
- **The tradeoff:** if you start a turn during a call, the answer is spoken into the room. A knock never comes during a call: it waits and tells you after.
- **The mic is native**, owned by the server and fixed to the built-in mic (never AirPods, which would drop to call quality), so the shield can tell the console's own mic from a call. The phone, or a lid-closed Mac, falls back to browser push-to-talk.
- **Voice only, as a conversation.** Every reply is said aloud in full, names and amounts included, typed turns too. On this Mac the server plays it (streamed to the speaker), so Chrome's autoplay rules don't matter and the server knows when the last sentence ends. Then the mic opens for 8 s for your verified voice, so you just answer. Hold Right ⌥ or press Space to cut in. On the phone the browser still plays it.
- **"What's on your mind?"** gets a spoken rundown in under 45 s: what's waiting on you, what the team is working on and how far it got, what finished today, and Jarvis's top item. It ends by asking which to take first.
- **Voiceprint:** **Voice & presence** (the chip at the top left) → *Teach it your voice*, 3 phrases while holding ⌥. It stays in `~/.config/cbrain/voiceprint.npy` (0600) and identifies no one else. With a voiceprint, a 5 s follow-up window opens after a spoken reply, and only your voice counts.
- **Permissions, once:** Accessibility (Right ⌥ hotkey), Microphone, and Automation → Google Chrome (Meet detection). The panel shows what's missing.

### One conversation, one console
- The page remembers its conversation: a reload or a new console tab continues it ("New conversation" in Conversations starts fresh). A newer console tab takes over and older ones step aside; push-to-talk brings forward the live one (title ●) and never opens a second tab.
- **No page needed.** Right ⌥, the knock and the follow-up window use the console page on this Mac if one is open. With none open, the server runs the same conversation itself (the newest one, resumed) and speaks through the Mac; opening a console page hands the conversation back to it.

### Jarvis: the queue, the stage and the knock (`webapp/jarvis.py`)
- **What she watches:** mail waiting for your answer, plans and research waiting on you, a meeting that ended in the last 45 min, today's briefing, and new ideas.
- **She sorts it first.** A background `claude -p --model haiku` call (no tools, run outside the repo) rates every new item on **urgency** and **importance** (0–1), flags **noise**, and gives one spoken reason. Your past calls and redirects are its examples, so she learns your bar.
- **She picks the stage** (see above). The queue, with her ids, is also in the Chief of Staff's context, so "what's next" and "do the Acme mail first" route straight to the item.
- **The knock tells you what it is.** When something urgent or important arrives and presence allows proactive speech (no turn running), the Chief of Staff tells you out loud, unprompted, through the Mac: who, what they want and by when, most pressing first, then asks what you want done. You don't need the page open; just answer (the follow-up window is open, or hold Right ⌥). Names and amounts are said in full, on speakers too: your call (2026-10-19).
- **Never into a call.** While a call is detected (Meet, Zoom, a huddle…; a calendar entry alone doesn't count) she holds the news and tells you once the call ends.
- **Budget:** 2 an hour and 8 a day. Putting a knocked item off ("later", "noise", "not important") within 10 minutes counts as "not now" and halves the day; two calls where she matched you take one halving back. Noise never knocks. It's also an island pill and a macOS notification (with the title). Away from the Mac (keyboard and mouse idle ≥ 10 min), the knock also goes to your phone as an iMessage to yourself, count and kind only, never a title (`webapp/push.py`; put your phone number or Apple ID in `~/.config/cbrain/imessage-to`, then test with `uv run webapp/push.py test`).
- **Research from the phone, with media.** Text yourself (or send a voice memo) "research X, make a podcast and a video" (`webapp/inbox.py`). The turn reaches the model tagged `<via-phone/>`, so Jarvis skips the challenge questions you couldn't see and starts the plan at once with `media:` and `media_account:` in TASK.md; the plan's own OK still pauses and knocks. When it's done, `tasks.py` runs `resources/skills/research/notebooklm/scripts/task_media.py`: NotebookLM podcast and/or video, downloaded beside the report, played in the report panel (on the phone via `tailscale serve`). Work topics use the employer's NotebookLM account, everything else a personal profile (`nlm login --profile personal`, once).
- **Nothing is sent by voice from a knock.** A mail reply goes out only on your tap on **Approve & send** (spec §5).
- **The ledger:** `output/.webapp/jarvis-ratings.jsonl` holds her guess, your call or your redirect, and agree yes/no. State is in `output/.webapp/jarvis.json`. Both are git-ignored, because titles carry client names.
- **Voice:** Qwen3-TTS `serena` with a British accent instruction (`voice.py`), the same voice for the whole console. The Chief of Staff has a personality (British, composed, one dry line at most, never at anyone's expense) and picks a tone per sentence with `[[tone: …]]`: calm, warm, dry, pleased, concerned, urgent, gentle.
- **Not built yet (spec §4):** activity breakpoints (app switch, unlock, return from away), the external-deadline budget bypass, and "hey Jarvis".

### Voice: everything on-device except Claude itself
`voice.py` runs Whisper large-v3-turbo (speech → text, ~0.5–0.7s) and Qwen3-TTS 1.7B CustomVoice, 6-bit (text → speech, voice `serena`, an emotion instruction per sentence) through MLX on Apple Silicon. Your audio never leaves the Mac; only the transcript goes to Claude. Replies are spoken sentence by sentence while still streaming. The page sends Claude a digest of today's meetings, prep and briefing up front, so most answers need no file reads. Measured from the end of your question to the first spoken word: **2.4–4.3s** with the earlier Kokoro voice; On this Mac the new voice is streamed: generated ~0.3 s at a time and played as it comes, so the first audio starts ~0.2 s after the first sentence arrives and sentences follow each other with no gaps (Qwen3-TTS runs at 0.4–0.7× real time on an M5). Not yet measured end to end. The phone still gets whole sentences. The first server start downloads the models (~3.6 GB) once.

## Permissions
A headless run can't show permission prompts. Runs use `--permission-mode acceptEdits` plus the `ALLOWED_TOOLS` list in `server.py`:
- File edits are allowed, and the write-boundary hook still guards them.
- Bash is limited to read-only commands and `resources/skills/**` scripts.
- Everything else is denied, and the denial is shown in the UI. To widen it, edit `ALLOWED_TOOLS`.

The CLI also auto-approves commands it classifies as read-only, such as `whoami` and `pwd`.

## Security
The server binds to `127.0.0.1` only. It rejects any `Host` header other than `127.0.0.1`/`localhost` (against DNS rebinding) and any POST or WebSocket whose `Origin` is a different site (against CSRF and cross-site WebSocket hijacking from other browser tabs). There's no login, so any process on this machine can use it. That's the same trust level as the `claude` CLI itself.
