---
id: daily-report-synthesis
aliases: [daily-report-synthesis]
name: "Daily Report Synthesis — End-of-Day Narrative"
category: workflow-ops
description: Turn today's honest daily-report stub into a real narrative — what actually happened and was decided — synthesized only from what's genuinely in the vault (meeting notes, mail, enrichments, deliverables), never fabricated.
triggers: [synthesize today's daily report, write up today, close out the day, end of day summary, daily report is just a stub, what happened today, log today's decisions]
tags: [workflow-ops, daily-report, synthesis, vault-hygiene]
related: ["[[morning-briefing]]", "[[vault-maintenance]]", "[[calendar-to-contacts]]", "[[mail-to-conversations]]"]
status: active
version: 1
created: 2026-07-25
updated: 2026-07-25
vault_writes: ["cbrain/daily reports/*"]
---

# Daily Report Synthesis — End-of-Day Narrative

## Contract
- **Input:** a date (default today) whose `daily reports/<YYYYMMDD>.md` note exists — as a real note or, more commonly, the honest stub `gen_daily.py` (`[[vault-maintenance]]`) produces.
- **Output:** the same `daily reports/<YYYYMMDD>.md`, with `## Summary` replaced by 2–4 sentences of genuine narrative and a `## Knowledge Graph` section listing what changed in the vault that day — never a new file, always the existing daily note.
- **Allowed tools/artifacts:** read-only over the day's meeting notes, mail imports, `Clients/` edits, and `output/` deliverables; write only to the one daily-report file.
- **Done when:** `## Summary` no longer reads `_Stub — backfilled during vault clean-up._`, every sentence in it traces to a note that actually exists (no invented decisions), and thin days are reported as thin rather than padded.

**Triggers/Context**
- On demand, end of day: "synthesize today's daily report", "close out the day".
- The gap this exists to close: `gen_daily.py` intentionally writes **honest scaffolding, never a fabricated summary** — which means a day's real narrative only ever gets written if a human (or this skill) does it deliberately afterward. Left undone, the stub is permanent — which is exactly what happened vault-wide from 2026-07-12 onward despite meetings continuing to log through October.

## Core Blueprint
1. **Resolve the date** (default today; accept an explicit `YYYY-MM-DD`). Open `daily reports/<YYYYMMDD>.md` — if it doesn't exist yet, that's `gen_daily.py`'s job first, not this skill's.
2. **Gather the day's real inputs** — read, don't infer:
   - Every `notes/<YYYYMMDD>-*.md` meeting note linked under `## Meetings` — specifically their body content (`## My Notes`, prep blocks, outcomes), not just the title.
   - Mail imported that day (`Mail/msgs/` dated today, via `[[mail-to-conversations]]`) and any conversation threads it touched.
   - `Clients/` notes created or meaningfully enriched that day (new contacts, status changes, enrichment passes).
   - `output/` deliverables generated that day (cross-reference `notes/Deliverables/` dates) and any topic anchors (`projects/`) updated.
   - LinkedIn posts published or content ideas logged that day, if any.
3. **Write the Summary** — 2–4 sentences on what actually happened or was decided, not a restatement of the meeting list (that's already under `## Meetings`). Name the decision, the open question it resolved or raised, or the concrete next step it produced. If a meeting note has no real content beyond its title, say so ("no notes captured for X") rather than manufacture a plausible-sounding line — this is the same honesty rule `gen_daily.py` already applies to the stub itself, just carried into the narrative step.
4. **Write/refresh `## Knowledge Graph`** — one bullet per genuinely new/changed vault artifact that day (new contact, enrichment batch, new topic link, deliverable shipped), following the existing convention already visible in well-formed daily reports (e.g. `daily reports/20260709.md`).
5. **Thin day → thin report.** A day with routine internal standups and no decisions gets a one-line honest Summary ("Routine internal cadence — Lasers4MaaS WP5/WP6, no new decisions") — don't inflate it to look substantive. Padding a quiet day is the same failure mode as fabricating one.
6. **Idempotent.** If `## Summary` already holds real narrative (i.e., it's not the literal stub string), treat the day as already synthesized and stop — don't overwrite a human-written entry.

## Optimizations/Gotchas
- **Never fabricate.** This skill's entire reason to exist is that `gen_daily.py` deliberately refuses to guess — it would be a direct regression to have this skill guess instead. Every Summary sentence must trace to a note, mail thread, or deliverable that actually exists; if nothing did, the honest output is "nothing notable" not an invented narrative.
- **This is retrospective, not prep.** Don't confuse this with `[[morning-briefing]]`, which prepares for *upcoming* meetings each morning; this skill closes out the day that already happened. They're complementary, not overlapping — morning-briefing's per-meeting prep blocks are one of the inputs this skill reads back at end of day.
- **Manual-first by design.** Unlike `[[morning-briefing]]`, this skill ships without a launchd schedule or a deterministic Python half yet — the synthesis step is 100% judgment (reading notes and writing prose), so there's no mechanical/judgment split to make script-backed the way `build_briefing_html.py` is. Automate it (a `run_daily_synthesis.sh` wrapper, an evening `launchd` slot) once the manual shape has run for a couple of weeks and proven itself — building the scheduler before the content pattern is validated would be scaffolding nobody's checked yet.
- **Backfilling the existing 80+ stubs is a separate, larger job**, not something this skill does automatically — most of those days' *real* narrative content (what was actually decided in a WP5/WP6 standup last September) may no longer be reconstructable from notes alone. Run this skill going forward; treat historical backfill as its own explicit, scoped pass if wanted.

**Feedback & Skill Verification**
- Would you like to provide feedback to optimize this workflow or execution?
- Should we update this skill (or add a new one) based on how this went?
