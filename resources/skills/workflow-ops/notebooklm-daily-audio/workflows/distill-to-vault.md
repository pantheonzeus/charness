# Distill NotebookLM Summaries → Vault (autonomous)

Turn today's raw NotebookLM notebook summaries into **distilled topic notes** in the
Obsidian second brain and **wire them bi-directionally to the relevant people and
meetings**. This is the judgment half of the daily audio pipeline: `daily_audio.py`
has already fetched each notebook's summary into `output/podcasts/<YYYYMMDD>-<slug>.summary.md`;
this workflow reads that queue and connects the material into the knowledge graph.

Runs headless (launchd, ~18:30) via [`scripts/distill_to_vault.sh`](../scripts/distill_to_vault.sh),
or on demand. Reuses the [[source-distillation-topic-note]], [[topic-based-linking]] and
living-knowledge-graph skills — do not invent new linking mechanics here.

## Inputs
- **date** (default: today, local) → `YYYYMMDD`. The prompt passes it explicitly to avoid
  midnight ambiguity.
- Queue files: `output/podcasts/<YYYYMMDD>-*.summary.md`.
- Run from the **repo root** (the checkout root, e.g. `/Users/<you>/GitHub/cbrain`). The vault is `cbrain/`:
  topic notes → `cbrain/projects/`, people/accounts → `cbrain/Clients/`,
  meetings → `cbrain/notes/`, daily reports → `cbrain/daily reports/`.

## Step 1 — Read the queue
List `output/podcasts/<date>-*.summary.md`. For each, read its frontmatter
(`notebook_id`, `notebook_title`, `topics`, `audio`, `distilled`) and body (the summary).
**Skip any with `distilled: true`** — already processed. If none remain, exit cleanly
(nothing to do; this is the normal case on quiet days).

## Step 2 — Distill into a topic note
For each fresh summary, create or update `cbrain/projects/<Topic>.md`, modeled exactly on
`cbrain/projects/AI SDLC.md`:
- Frontmatter: `type: topic`, `status: active`, `tags: [research, content-idea, <topic-tags>]`.
- A `> [!info] Primary source` callout citing the NotebookLM notebook **and including its
  `notebook_id`** — this is the idempotency key.
- `## TL;DR` (3–5 bullets), `## Key frameworks` (distilled tables/lists — **distill, don't
  dump** the raw summary), `## Content & talk angles`, `## Business relevance`, `## Links`.
- **Link only notes that exist.** Cite a notebook (or a companion notebook) by its title in plain
  text, inside the Primary-source callout. Write `[[X]]` only after confirming `X.md` exists in the
  vault; a link to a note that doesn't exist is a broken link, not a placeholder.
- **Idempotency:** if a topic note in `cbrain/projects/` already cites this `notebook_id`,
  **update that note in place** — never spawn a duplicate hub. Pick the topic name from the
  summary's `topics`/title; reuse an existing anchor if the theme already has one.

## Step 3 — Connect to the network (the point of this workflow)
The distilled `type: topic` note **is a topic anchor** — the join point for the whole graph.
Wiring it correctly is what makes the notebook reachable **both backward** (existing people/meetings)
**and forward** (a *future* meeting that links this same anchor inherits the notebook automatically —
that is the only mechanism for "link to future meetings"; see [[contact-meeting-capture]], which now
attaches every new meeting to its topic anchors).

Scan `cbrain/Clients/` (people + accounts) and `cbrain/notes/` (meetings) for **genuine**
matches to the topic and its `topics`. For each match:
- On the person/account/meeting note, append under its `## Links` section:
  `Topic: [[<Topic>]] — <one-line reason>`.
- Reciprocally, list that person/account/meeting under the topic note's `## Links`
  (e.g. `- Person: [[Jane Doe]] — reactivating on this exact theme`).
Links are **always bi-directional and always carry a reason** — a bare wikilink loses the why.
If this notebook also has imported source notes under `notes/NotebookLM/<slug>/Sources/`, run the
enforcement gate `resources/skills/research/notebooklm/scripts/link_audit.sh <slug>` and fix any island
it reports before closing out.

## Step 4 — Log + close out
- Append one line to `cbrain/daily reports/<date>.md` under `## Knowledge / Research`
  (create the daily file with `type: daily` frontmatter if it doesn't exist):
  `- Distilled [[<Topic>]] from NotebookLM ("<notebook_title>") and linked to <people/meetings>`.
- Flip the summary file's frontmatter `distilled: false` → `distilled: true`.
- **Write the handoff result (Charter §5) — last action of the run.** Write
  `output/.runs/<YYYYMMDD>-nlm-distill/children/distill/RESPONSE.md`: one line per summary file —
  topic note created/updated, people/meetings linked, or skipped + why — plus any failure. Write it
  even when nothing was distilled. Use only `[x]` boxes or none — never `[ ]`. The wrapper reopens this file.

## Guardrails (this runs unattended — stay conservative)
- **Only link EXISTING people and meetings.** Never create a new person/account/meeting note
  from a summary — a source is not a contact.
- **Link clear matches only.** When a connection is a stretch, don't make it. Precision over recall.
- **Append, never overwrite.** These notes are often sparse and hand-authored; add sections/lines,
  never replace existing content.
- **One topic note per notebook theme.** The `notebook_id` in the Primary-source callout is the
  dedup key — check for it before creating.
- Everything you touch is logged in the daily report and left append-only, so the run is
  reviewable the next morning.
