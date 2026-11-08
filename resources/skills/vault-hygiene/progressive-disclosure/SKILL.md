---
id: progressive-disclosure
aliases: [progressive-disclosure]
name: "Progressive Disclosure — MOCs, Bases, Summaries, Transclusion"
category: vault-hygiene
description: Structure the vault so information is revealed on a need-to-know basis — a Home MOC drills into Bases and domain hubs, which surface transcluded TL;DRs, exposing raw notes only on a specific query.
triggers: [progressive disclosure, MOC, map of content, home note, dashboard, obsidian bases, .base, need-to-know, TL;DR layer, transclusion, foldable, navigate the vault, entry point]
tags: [vault-hygiene, obsidian, navigation, moc, bases, summarization]
related: ["[[topic-based-linking]]", "[[skill-library-maintenance]]", "[[source-distillation-topic-note]]"]
requires:
  obsidian-plugins: [bases]
  python: ["3"]
scripts: [scripts/build_indexes.py, scripts/recall_bench.py]
modules: [autoresearch-loop]
status: active
version: 4
created: 2026-07-06
updated: 2026-10-29
vault_writes: ["cbrain/Home.md", "cbrain/MOCs/*", "cbrain/Bases/*", "cbrain/projects/*", "cbrain/Clients/*"]
---

# Progressive Disclosure — MOCs, Bases, Summaries, Transclusion

## What this skill is for

A vault of a few hundred machine-generated notes is a wall of text — for you *and* for an
AI reading it through an MCP server. Progressive disclosure fixes that: information is
revealed on a **need-to-know basis**. You (or the agent) start at a map, drill into the one
branch that matters, read a one-line summary, and open the raw note only when a specific
question demands it. This protects attention and the model's context window, and it stops
the AI drowning in irrelevant files.

**The four mechanisms are one composed system, not four features:**

```
Home MOC  →  Base / domain MOC  →  transcluded child TL;DRs  →  foldable depth  →  raw note
 (map)         (filtered list)        (Layer-4 summaries)        (hidden detail)   (Layer-1)
```

**Not for:** deep note *content* work (that's the note-type skills like
`[[source-distillation-topic-note]]`) or the skill library's own index (that's
`[[skill-library-maintenance]]`). This skill is about how notes are *surfaced and
navigated*, not what goes in them.

## The four mechanisms — and when to use each

**1. MOC (Map of Content) — the navigational hub.** A single note that links out to many
related notes. Use it as the *entry point* for a domain. The vault has one top-level
`Home.md` and one MOC per domain (`People`, `Projects`, `Meetings`) under `MOCs/`. This
generalizes the existing **anchor pattern** (`[[topic-based-linking]]`, Claude.md): an
anchor note is a topic-scoped MOC. Rule: an MOC *links and transcludes*, it does not
duplicate content. When 3+ notes converge on a theme with no natural hub, make a MOC.

**1b. Generated index (the pragmatic MOC for un-migrated folders).** When a high-volume
folder's notes carry their essence as *inline* fields (not YAML), a Base can't read them —
so generate an **index note** instead: one row per note (name/title · key field · link),
built by a script that reads the notes themselves. This is the compressed retrieval layer,
and re-running the script after new notes land is the "auto-update after new knowledge"
mechanism. `scripts/build_indexes.py` produces `MOCs/People-Index.md`,
`MOCs/Meetings-Index.md` and `MOCs/Commitments-Index.md` (open commitments by owner, with a ⚠️ on
overdue or > 30 days open, a `(no owner)` group for untagged Next Steps boxes, and `## Decisions`
bullets newest first; stamped `derived-untrusted` since meeting notes carry outside text); it only
reads note bodies and writes the index files, never edits a note. Measured effect: answering a query from the index + 1–2 drilled notes cost a
**median ~0.32 token ratio vs a full-folder scan, at 100% fact retrieval** (benchmark in
`autoresearch/improve-*/`). Link the generated index from the hand-curated MOC — don't let
it become a competing hub.

**2. Bases — the queryable dashboard.** The `bases` core plugin turns notes with consistent
YAML frontmatter into filtered, Notion-style tables — offline. Use a Base when you want a
*live, self-updating* view (all active projects, recent mail) rather than a hand-maintained
link list. The AI reads the `.base` file's filter to grasp the high-level shape before
opening any note. **Bases only see YAML properties** — inline `**bold:**` body fields are
invisible to them. See `references/frontmatter-schema.md` for the property vocabulary and
copy-paste `.base` recipes. Embed a Base in a MOC with `![[Name.base]]`.

**3. Progressive summarization — the TL;DR layer.** Tiago Forte's layered compression, applied
at the top of a note: **Layer 4** = a `## TL;DR` (3–5 bullets) directly under the H1;
Layer 1 = the raw body below. An AI doing RAG reads only the TL;DR to judge relevance, and
descends into the body only on a hyper-specific question. Use a `## TL;DR` **heading** (not
just a callout) on any note worth summarizing — the heading is what makes it transcludable.
Don't retrofit the whole back-catalogue; summarize hubs and high-traffic notes, and let
templates give new notes one automatically.

**4. Transclusion + foldable headers — composition and hiding.**
- **Transclusion** `![[Note#TL;DR]]` embeds one note's TL;DR section into a MOC, so the hub
  shows summaries without you copy-pasting. This is how mechanism 3 feeds mechanism 1. The
  target heading must exist or the embed renders empty — always point at a real `## TL;DR`
  (or `## Key takeaway`).
- **Foldable headings** are *native Obsidian* — nothing to build. Every `##` section
  collapses. For detail you want hidden by default, use a **collapsed callout**
  `> [!note]- Title` (the `-` starts it folded). Push deeply technical detail into its own
  atomic note and transclude a snippet, keeping the parent clean.

## How to apply it (the bootstrap recipe)

1. **Define the schema first.** Decide the YAML properties Bases will query (`type`,
   `status`, `tags`, `date`) — see `references/frontmatter-schema.md`. Without consistent
   frontmatter, Bases are useless.
2. **Build the Home MOC** as the single entry point: a short intro, links to the domain
   MOCs, and embedded Bases for the live dashboards.
3. **Build domain MOCs** that link out and transclude child `## TL;DR`s for the notes that
   have them.
4. **Add `## TL;DR` to hub notes** and bake a `## TL;DR` stub into note-generator templates
   so new notes are born with one (see the generator scripts under
   `resources/skills/workflow-ops/*/scripts/`).
5. **Create `.base` files** over the layers whose frontmatter is already clean; scope
   honestly and flag any Base that is empty pending a frontmatter migration.

## Recall benchmark — the standing guard
`python3 resources/skills/vault-hygiene/progressive-disclosure/scripts/recall_bench.py` runs 20 frozen questions (29 facts) through the index-then-drill path. The golden set is at `resources/skills/_evals/recall.tsv` (gitignored: the facts are client data).
- **PASS iff 100% of facts are found** in the matched index lines plus the drilled notes. A fact elsewhere in the index does not count, so a deleted route fails (probed 2026-10-09).
- **It is a guard, not a target.** Run it before and after any change to `build_indexes.py`, `index_deliverables.py`, a MOC, or a generator template, and revert the change if it flips to FAIL.
- The token ratio it reports is informational only.
- Baseline 2026-10-09: 29/29, median ratio 0.056.
- **Row kinds** (optional `kind` column, empty = `answer`), all deterministic checks on the vault, not on a model:
  - `abstain`: no note under `folder` (`.` = whole vault) holds any fact. The expected answer is "I don't know"; a hit means the row is outdated or the vault learned something.
  - `permission`: no note under `folder` holds any fact, e.g. pursuit pricing out of `notes/LinkedIn-Posts`.
  - `conflict`: facts `winner|loser` are both on the path (the contradiction stays visible) and the winner sits in a `confirmed:` note (Charter §6 trust tier).
- Baseline 2026-10-29: answer 20/20, abstain 1/1, permission 1/1; no conflict row yet (it needs a first confirmed note).

## Optimizations / Gotchas

- **Bases are blind to inline fields.** If `Status:`/`Type:`/`Date:` live as `**bold**` body
  text (as most auto-generated people/meeting notes do), a Base cannot filter them. Either
  migrate those to YAML (a scripted pass + fixing the generator templates) or scope the Base
  to the layers that are already clean (Mail, NotebookLM, topic notes). **Never ship a Base
  that looks populated but silently drops most notes** — state what it excludes and why.
- **Transclusion fails silently.** A typo'd heading in `![[Note#TL;DR]]` renders nothing, no
  error. Verify the target heading exists.
- **Don't boil the ocean on summaries.** Retrofitting a TL;DR onto 185 machine-generated
  notes is waste. Hubs + templates give ~90% of the benefit for ~10% of the effort.
- **One entry point.** Resist a second competing Home/index — orphan hubs defeat the purpose
  (same rule as the anchor pattern: prefer an existing hub over inventing a new one).
- **Foldable is free — don't overbuild it.** It's native UI. The only authoring move is
  choosing collapsed callouts for detail you want hidden by default.

## After applying

Offer, don't assume, the next step: "Want me to migrate the ~120 inline-field notes to YAML
so the People/Meetings Bases populate, or add TL;DRs to a specific set of notes?"

**Feedback & Skill Verification**
- Would you like to provide feedback to optimize this workflow or execution?
- Should we update this skill (or add a new one) based on how this went?
