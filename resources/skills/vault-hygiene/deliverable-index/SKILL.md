---
id: deliverable-index
aliases: [deliverable-index, output-to-vault, deliverables-in-vault, index-deliverables]
name: "Deliverable Index — Bridge output/ Artifacts into the Vault"
category: vault-hygiene
description: Give every finished deliverable in output/ a linked index note in the second brain (cbrain/notes/Deliverables/), and every input/ artifact one in cbrain/notes/Inputs/, so all outputs and inputs are discoverable from the vault without moving files or breaking scheduler paths. Idempotent, script-backed; auto-wikilinks to matching people/topics; surfaced via Deliverables.base + Inputs.base on Home.
triggers: [outputs in vault, deliverables in vault, index outputs, are my outputs in the second brain, all outputs land in vault, bridge output to vault, deliverable index, surface deliverables, output not in vault, inputs in vault, input artefacts in second brain]
tags: [vault-hygiene, obsidian, deliverables, output, index, bridge, base]
related: ["[[vault-maintenance]]", "[[progressive-disclosure]]", "[[source-distillation-topic-note]]"]
status: active
version: 4
created: 2026-07-25
updated: 2026-10-18
vault_writes: ["cbrain/notes/Deliverables/*", "cbrain/notes/Inputs/*", "cbrain/notes/Work/*", "cbrain/projects/*"]
---

# Deliverable Index — Bridge output/ Artifacts into the Vault

Charter §4 keeps two zones on purpose: finished deliverables live in `output/` (the working
artifact area, git-ignored), the knowledge graph lives in `cbrain/`. That split is right — but
it left deliverables invisible from the second brain. This skill closes the gap: one **linked
index note** per deliverable under `cbrain/notes/Deliverables/`, pointing back at the artifact.
The heavy file never moves, so no launchd/cron path breaks; the vault just gains a window onto it.

This is a **bridge, not a relocation**. If someone asks to physically move `output/` into the
vault, that's a different (larger) change — flag the scheduler-path fallout first.

**Contract**
- **Input:** the `output/` and `input/` trees.
- **Output:** `cbrain/notes/Deliverables/<slug>.md` (one per deliverable, `type: deliverable`),
  `cbrain/notes/Inputs/<slug>.md` (one per input file, `type: input`), and `cbrain/notes/Work/<slug>.md` (one per document in a sibling repo under `~/GitHub/`, or a loose file there, `type: work`, artifact `../<repo>/<path>`), surfaced by
  `cbrain/Bases/Deliverables.base` + `Inputs.base` (both embedded in `Home.md`).
- **Allowed tools/artifacts:** `scripts/index_deliverables.py` (stdlib only). No network, no artifact moves.
- **Done when:** every in-scope file in `output/` and every file in `input/` is referenced by a vault note; re-run reports `0 new/changed` on both passes.

**Triggers/Context**
- "are my outputs in the vault?", "all outputs should land in the second brain", "bridge output → vault".
- After producing a new report/deck/dossier/profile/LinkedIn draft, or as a periodic sweep (pairs with `[[vault-maintenance]]`).
- **Runs automatically** from the console (`webapp/tasks.py`): when a research/plan task reaches `done`, and after every PDF/MP3 render (`scripts/render.py`). Other producers still need a manual run.
- Rendered `.mp3` files are listed under *Other formats* on their same-stem document's note; a loose MP3 (e.g. `output/briefings/<date>.mp3`) is skipped, since briefings reach the vault only via the console's "Save to vault".

**Core Blueprint**
1. **Dry-run to see scope:** `python3 resources/skills/vault-hygiene/deliverable-index/scripts/index_deliverables.py --dry-run`. It prints the count and what it skips by policy.
2. **Run it:** drop `--dry-run`. Idempotent — fully-generated notes (`generated: deliverable-index`) are overwritten, and index notes whose artifact was deleted are pruned. Re-run must report `0 new/changed`.
3. **Confirm surfacing:** `Deliverables.base` filters `type == "deliverable"`; it's embedded under `### 📦 Deliverables` in `Home.md`. Open Home in Obsidian to eyeball the table.
4. **Wire the graph (Charter §6):** the script auto-links any existing person/topic note whose name token appears in the deliverable's path. For a marquee deliverable, add the missing `[[links]]` by hand to the *artifact* or the relevant topic note — the auto-match is deliberately conservative (first-token, len≥5) to avoid false links.

**Optimizations/Gotchas**
- **Work pass (v4, 2026-10-18).** Walks `~/GitHub/*` except this repo, keeping only `.md/.html/.pdf/.docx/.pptx/.xlsx` ≤ 50 MB. It skips hidden dirs (`.git`, `.venv`), `node_modules`, the env dirs (`venv`, `my_env`, `mlx-env`, …), `build`/`dist`, and `CLAUDE.md`/`AGENTS.md`/`LICENSE.md`. Keys (`.pem`), code, notebooks and media are never in scope. The scope lives in `WORK_SKIP_*`; say what you changed when you widen it.
- **Scope is opinionated on purpose.** Indexes `.md/.html` anywhere under `output/`; `.docx/.pptx/.pdf/.xlsx` fold into a same-stem md/html note as "Other formats" (case-insensitive stem) or get their own note; orphan `.png/.svg` collapse into one `<folder>-images` bundle note per directory; every `input/` file gets its own note. **Never** duplicates or overwrites a hand-authored note (`generated:` ≠ `deliverable-index`) — any `output/…` path in its `artifact:` field or a `../../../output/…` link counts as covered. **Skips** hidden files (`.build-*.html`), Office lock files (`~$*`), `*.bak*`, code/data (`.py .sh .json .jsonl .tsv`) — a code folder is indexed through its `README.md`; also skips `podcasts/` + `*.summary.md` (already bridged by `[[notebooklm-daily-audio]]` via `nlm-*.base` + NotebookLM sources — re-indexing would duplicate what the vault already records), `morning-briefing/` (ephemeral, regenerated daily), `.runs/` (run state), `*.log`, `*.m4a`, `.DS_Store`. Widen the `SKIP_DIRS` / `SKIP_NAME_RX` / `INCLUDE_EXT` constants to change it — and say what you changed (no silent scope drift).
- **Auto-links are whole-token** (since v2): `chris` no longer matches inside `christoph`. Entities with a short first token (`rsg`, `l4m` < 5 chars) never auto-link — wire those hubs by hand (one line on the topic note pointing at the index note).
- **TL;DR copies the artifact's first paragraph verbatim**, including any `[[wikilinks]]` it contains — a skill-id link in an artifact (e.g. `[[linkedin-weekly-review]]`) surfaces as a broken vault link. Known, not yet fixed.
- **Index notes are generated, not authored.** They carry `generated: deliverable-index` and are overwritten each run. Put durable commentary on the *artifact* or a real topic note, not here.
- **Relative artifact link points outside the vault** (`../../../output/...`). That's a valid filesystem path but Obsidian won't treat it as an internal link — the canonical pointer is the `artifact:` frontmatter field, which the Base shows.
- **`cbrain/` is git-ignored + Obsidian-synced.** Generated notes land in live personal data, exactly like `vault-maintenance`'s stubs — that's expected, not a boundary violation.
- **Schedule it** (optional) alongside the daily jobs so new deliverables self-index; it's cheap and safe to run repeatedly.
