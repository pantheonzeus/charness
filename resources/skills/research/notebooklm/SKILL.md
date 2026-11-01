---
id: notebooklm
aliases: [notebooklm]
name: "NotebookLM — Expert Knowledge to Action"
category: research
description: Turn any expert's podcast/YouTube content into a personalized, cited protocol with experiments — bulk-load 300 episodes into NotebookLM from the terminal, run an expert-informed interview, and create tracked experiments in your Obsidian daily note.
triggers: [notebooklm, notebook lm, podcast of the research, video overview, research podcast, load channel, expert interview, notebooklm ask, health protocol, youtube channel, bulk load videos, import youtube, add source, add to notebook, import to notebooklm, studio artifacts, infographic, quiz, flashcards, download artifacts]
tags: [research, notebooklm, citations, obsidian, youtube, podcasts, experiments, automation]
related: ["[[source-distillation-topic-note]]", "[[notebooklm-daily-audio]]", "[[linkedin-authentic-storytelling]]"]
requires:
  tools: [bash, python]
  cli: ["nlm (notebooklm-mcp-cli)", "notebooklm-py[browser]", playwright]
  obsidian-plugins: [Dataview]
environment: "Terminal + Google auth (nlm + notebooklm-py cookies); Obsidian with Dataview. Scripts run from the vault root (Path.cwd())."
scripts: [scripts/load_channel.py, scripts/resolve_citations.py, scripts/import_sources.py, scripts/extract_passages.py, scripts/backfill_fulltext.py, scripts/link_audit.sh, scripts/task_media.py]
workflows: [workflows/add-source.md, workflows/youtube-channel.md, workflows/ask.md, workflows/import.md, workflows/auth.md]
status: active
version: 8
created: 2026-07-05
updated: 2026-11-01
# Original upstream frontmatter was {name, description}; preserved as id/name/description above. License: MIT (see body).
vault_writes: ["cbrain/notes/NotebookLM/*", "cbrain/notes/Dashboards/*", "cbrain/notes/Experiments/*", "cbrain/notes/[0-9]*", "cbrain/projects/*", "cbrain/Clients/*"]
---

# NotebookLM - Expert Knowledge to Action

Turn any expert's content into a personalized protocol with experiments you actually run. Load 300 YouTube episodes into NotebookLM from terminal, run a cited interview about your goal, create experiments in your Obsidian daily note.

**Video walkthrough:** [https://youtu.be/KRpZSvtMiTI](https://youtu.be/KRpZSvtMiTI)

## What This Does

1. **Load sources from terminal.** You can't just tell NotebookLM to add a YouTube channel. This skill does it. One command. 300 episodes.
2. **Cited answers traced to exact transcript lines.** Every recommendation links back to the exact episode and passage. Verifiable.
3. **Expert-informed interviews.** Claude queries NotebookLM with YOUR goal. Generates questions informed by the expert's research on your specific topic.
4. **Experiments in Obsidian.** Protocol becomes experiments in your daily note. Morning routine skill asks every day: how is this going?
5. **Any expert, any domain.** Huberman for health. Lenny for product. Onboarding docs for a new job. Same pattern.

## Prerequisites

### 1. Install nlm CLI

```bash
uv tool install notebooklm-mcp-cli
```

Gives you the `nlm` command. See [notebooklm-mcp-cli](https://github.com/jacob-bd/notebooklm-mcp-cli) for details.

### 2. Install notebooklm-py (for notebook creation and channel loading)

```bash
pip install "notebooklm-py[browser]"
playwright install chromium
```

### 3. Authenticate

```bash
# nlm CLI auth (for queries and source listing)
nlm login

# notebooklm-py auth (for notebook creation and loading)
notebooklm login
```

Both open a browser window for Google login. `nlm` saves to its own config, `notebooklm-py` saves cookies to `~/.notebooklm/storage_state.json`.

### 4. Obsidian Plugins

- **Dataview** (required) - for dashboard queries and citation tables

## Quick Start

```bash
# List your notebooks
nlm notebook list

# Ask a question with citations
nlm notebook query <notebook-id> "What does Huberman say about deep focus?" --json

# List sources
nlm source list <notebook-id> --json
```

## Workflow Routing

| User says | Workflow |
|-----------|----------|
| "add source", "import youtube", "add to notebook", "add a URL/PDF" | [workflows/add-source.md](workflows/add-source.md) |
| "load channel", "youtube channel", "bulk load videos" | [workflows/youtube-channel.md](workflows/youtube-channel.md) |
| "notebooklm ask", "ask notebook", "Q&A" | [workflows/ask.md](workflows/ask.md) |
| "import notebook", "import sources" | [workflows/import.md](workflows/import.md) |
| "notebooklm auth", "notebooklm login" | [workflows/auth.md](workflows/auth.md) |

## The Full Pipeline

This is the workflow shown in the video:

### 1. Pick your expert and goal

```
Goal: "I want to improve my health and focus"
Expert: Andrew Huberman (@hubaborhab on YouTube)
```

### 2. Load their content

```bash
# Scrape channel videos
python3 scripts/load_channel.py scrape \
  --channel "https://www.youtube.com/@hubaborhab" \
  --output /tmp/huberman-videos.json

# Create notebook
notebooklm create "Andrew Huberman - Health"

# Load 200 most recent health-related episodes
notebooklm use <notebook-id>
python3 scripts/load_channel.py load \
  --videos /tmp/huberman-videos.json \
  --notebook <notebook-id> \
  --count 200 \
  --concurrency 20
```

### 3. Ask expert-informed questions

```bash
nlm notebook query <notebook-id> \
  "What does Huberman recommend for sustaining deep focus for 4+ hours daily?" --json
```

Each answer comes with `[N]` citations back to the exact source and passage.

### 4. Run a cited interview

Claude uses the notebook to generate interview questions specific to YOUR goal. You answer honestly. Claude builds a personalized protocol where each recommendation is tied to an exact episode.

### 5. Create experiments

The protocol becomes experiments in your Obsidian vault:
- Each experiment has a hypothesis, protocol, success criteria, and timeframe
- They appear in your daily note every morning
- Your morning routine skill asks: "How is this experiment going? Any observations?"

### 6. Turn it into a reusable skill

Package the workflow as a `/huberman` or `/lenny` skill. Same pattern, different expert.

## Vault Structure

```
Your Vault/
├── Notes/NotebookLM/
│   ├── Huberman Health.md              # type: notebook (index)
│   └── huberman-health/
│       ├── Sources/                     # type: notebook-source (transcripts)
│       │   └── Episode Title.md
│       └── QA/                          # type: nlm-query (cited answers)
│           └── 2026-04-05 Focus Protocol.md
├── Notes/Experiments/
│   └── Morning Sunlight Protocol.md     # type: experiment
└── Notes/Dashboards/
    └── Health.md                        # Dashboard with embedded experiments
```

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/load_channel.py` | Scrape YouTube channel + bulk-load into NotebookLM |
| `scripts/resolve_citations.py` | Replace `[N]` with `[[Source#^anchor\|[N]]]` wikilinks |
| `scripts/import_sources.py` | Import sources as vault files with metadata |
| `scripts/extract_passages.py` | Extract cited passages from Q&A into source files |
| `scripts/backfill_fulltext.py` | Fetch full transcripts for source files |
| `scripts/link_audit.sh` | **Enforcement gate** — asserts every synced source note reaches a reciprocating `type:topic` anchor (no islands). Blocking post-condition of the import workflow. Exit 0 = wired into the graph. |
| `scripts/task_media.py` | Podcast and/or video overview of a finished console task's report (TASK.md `media:`), started by `webapp/tasks.py`. See *Media for console tasks* below. |

All Python scripts use `Path.cwd()` as vault root. Run them from your vault directory.
`link_audit.sh` auto-detects the vault (cwd or cwd/cbrain) and takes one or more notebook slugs.

## Media for console tasks

Text Jarvis from the phone (or say it): "research X, make a podcast and a video". The console writes the plan's TASK.md with `media: audio, video` and `media_account: work|personal`. When the task reaches done, `webapp/tasks.py` runs `scripts/task_media.py <task id>` once: a notebook "Research · <title>", the report's cited public URLs (plus the report text only if `scripts/outbound_gate.py`, public mode, passes it), a deep-dive podcast and an explainer video, downloaded beside the report as `<stem>-podcast.m4a` / `<stem>-video.mp4`. State: `output/tasks/<id>/media.json`; re-run the script to resume.

- **Account (principal's call, 2026-10-31):** `work` goes to the nlm profile signed in under the active employer's domains; `personal` (default) to a profile under no employer's domain. No fallback between them. Set up the personal one once: `nlm login --profile personal`.
- **Delivery:** players in the task's report panel in the console (phone: over `tailscale serve`). The iMessage says only what is ready; the title only for a personal task, and only if the outbound gate passes it.
- **Dry run:** `python3 resources/skills/research/notebooklm/scripts/task_media.py <task id> --dry-run` prints account, profile, URLs and what is held back.

## Studio Artifacts — Gotchas

- **`nlm download <kind>` takes no `--profile` flag.** With it, every download fails ("No such option"). It uses the default profile; `studio status` and `studio rename` do accept `--profile`.
- **Quiz JSON mixes four question types:** `multiple_choice`, `multiple_select` (several `isCorrect`), `fill_in_the_blank` (`bestAnswer`, `acceptableAnswers`) and `short_answer` (`grading.modelAnswer`). Parse all four (`--format json`).
- **Flashcard sides** are `{flashcardContentBlock: [{type: "text", content}]}`, not strings.
- **Infographics** still contain typos after a "spell-check twice" instruction, and may draw a company's logo unless told "no logos or brand marks". Icons-only layouts have fewer text errors.
- **`--focus` is the steering prompt** for audio, video, infographic, quiz and flashcards. `--source-ids` scopes each artifact; fewer sources means less drift.
- For role-tailored team onboarding built on this, see [[team-onboarding-kit]].

## Citation Resolution

The resolver turns `[N]` markers in NotebookLM answers into clickable `[[Source#^c-XXXXXXXX|[N]]]` wikilinks. Click to jump to the exact cited passage in the source transcript.

- Anchor IDs are stable (MD5 of cited text)
- Idempotent: re-running same question skips existing anchors
- Cross-source citation remap: handles collapsed source_ids
- ~96% resolution rate across tested queries

## Examples

- **Health:** 300 Huberman episodes -> personalized health protocol with sleep, supplements, exercise experiments
- **Product:** 200 Lenny's Podcast episodes -> product strategy playbook with cited frameworks
- **New job:** Onboarding docs + team wikis + architecture decisions -> ramp-up plan with daily experiments
- **Business:** Hormozi content -> offer audit with value equation scoring
- **Content:** a primary-source report (e.g. the EU competitiveness/Draghi report) -> cited answers cross-referenced against a live news trigger -> a data-grounded contrarian take for a board-register LinkedIn post (see [[linkedin-authentic-storytelling]])

## License

MIT
