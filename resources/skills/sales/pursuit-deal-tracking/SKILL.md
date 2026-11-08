---
id: pursuit-deal-tracking
aliases: [pursuit-deal-tracking]
name: "Pursuit / Deal Tracking"
category: sales
description: Give every live, named, high-stakes pursuit — a sales deal or a personal career opportunity — a standing vault anchor the moment it generates its first deliverable, so it stays visible after the deliverable ages out of top-of-mind.
triggers: [live pursuit, active deal, deal tracking, pursuit status, bake-off, vendor decision, hearing round, interview round, is this deal tracked, where does this pursuit live, add to pursuits, pursuit dashboard]
tags: [sales, pursuit, deal-tracking, crm, career]
related: ["[[competitive-porter-teardown]]", "[[company-challenger-brief]]", "[[proposal-challenger]]", "[[audience-of-one-report]]", "[[competitor-intelligence]]", "[[account-priority-map]]", "[[rfp-clarification-reconciliation]]"]
modules: [file-backed-state]
scripts: [scripts/reaction_tally.py]
status: active
version: 3
created: 2026-07-25
updated: 2026-10-09
vault_writes: ["cbrain/Clients/*", "cbrain/projects/*"]
---

# Pursuit / Deal Tracking

## Contract
- **Input:** a named company + a live, high-stakes thread involving it — a sales bid (bake-off, RFP, expansion proposal) **or** a personal career pursuit (interview/hearing round, board seat, advisory offer). Both shapes hit the same failure mode: research/prep deliverables pile up in `output/` with no vault home.
- **Output:** a `Clients/<Company>.md` note (create if absent, extend if it exists) carrying `pursuit: true`, `pursuit_type: sales-deal | career-opportunity`, and `pursuit_stage`, plus a `## Pursuit` section — surfaced live via `Bases/Pursuits.base` and `MOCs/Pursuits.md`.
- **Allowed tools/artifacts:** vault file edits only; no external research (that's `[[competitive-porter-teardown]]` / `[[company-challenger-brief]]` / `[[proposal-challenger]]` upstream of this skill).
- **Done when:** the company has a `Clients/` note with the pursuit frontmatter set, the note appears in `Bases/Pursuits.base`, and it's bi-directionally linked to every deliverable, contact, and topic anchor the pursuit touches (career-track pursuits link to `[[career-manufacturing-cto-positioning]]`; sales-track pursuits link to the relevant account/topic anchor, e.g. `[[AI SDLC]]`).

**Triggers/Context**
- The moment a hearing-prep cheat sheet, Porter teardown, proposal red-team, or audience-of-one brief is generated **for a company that has no `Clients/` note yet** — this is the single most common way a pursuit goes untracked (it was the exact gap that left the Company A hearing reachable only by remembering the `output/` folder existed).
- A deal changes stage (bake-off → shortlist → decision) or a hearing moves to its next round — update `pursuit_stage`, don't create a second note.
- Explicit ask: "track this pursuit", "is X on the pursuit board".

## Core Blueprint
1. **Check for an existing anchor.** `Clients/<Company>.md` first (account notes already exist for some companies — e.g. `Globex`, `Acme` — extend, never duplicate).
2. **Set/extend frontmatter:**
   ```yaml
   type: account
   status: active
   pursuit: true
   pursuit_type: sales-deal        # or: career-opportunity
   pursuit_stage: "<short stage — e.g. '3-vendor bake-off, decision early Aug 2026' or '2nd hearing round'>"
   ```
3. **Write/extend the `## Pursuit` section** (or reuse the note's existing `## TL;DR`/`## Next steps` convention if the note predates this skill, per `Acme` — don't force a rewrite of a note that's already doing the job in prose): stage, decision date if known, key stakeholders/panel, what's actually being evaluated, the live deliverables trail (link every `output/` artifact generated for this pursuit). A `## Business Priority Framework` section from `[[account-priority-map]]` lives on this same note too — don't spin up a second file for it.
4. **Link bi-directionally, branching on `pursuit_type`:**
   - `sales-deal` → link the relevant topic anchor (e.g. `[[AI SDLC]]`) and your own team's contacts involved; reciprocate the link on the anchor's Business-relevance section.
   - `career-opportunity` → link `[[career-manufacturing-cto-positioning]]` (or whichever career anchor applies) under a dedicated subsection there — this is the single link most likely to be forgotten, because a personal pursuit doesn't route through the usual sales-account instinct. **Non-negotiable**, same standing as the topic-anchor step in `[[contact-meeting-capture]]`.
5. **Don't spin up person notes for one-off panel/stakeholder mentions** unless they become an ongoing contact — a hearing panelist named in a cheat sheet is not automatically a CRM contact; use judgment, and say so if you're deliberately skipping it (Simplicity First — don't force symmetry with the People graph).
6. **Confirm** with the file(s) touched and the `Bases/Pursuits.base` row it now produces.
7. **Log what the client actually reacted to (the outer loop).** Do this on every stage change and every client reply, under a `### Client reaction log` subsection of `## Pursuit`. Add one line per finding the client responded to, in exactly this shape, so `scripts/reaction_tally.py` can read it:
   ```
   - 2026-10-06 · corrected-us · proposal-challenger · offered inventory phase the client runs itself · "so you don't offer us consulting we don't need"
   ```
   The fields are: date · reaction (`landed` | `rejected` | `ignored` | `corrected-us`) · the skill that produced the finding (its `id`, or `none`) · the finding in a few words · the client's own words, quoted, when you have them. **Log only real reactions** (a reply, a meeting remark, a scoring sheet), never our guess at how a finding landed.
8. **On resolution, record the outcome** in frontmatter: `pursuit_outcome: won | lost | withdrawn | no-decision` and `outcome_date: YYYY-MM-DD`, alongside `pursuit: false`. Add one dated line in the stage history naming the decisive factor, if the client gave one.
   - **Across pursuits:** `python3 resources/skills/sales/pursuit-deal-tracking/scripts/reaction_tally.py` tallies the reaction log per skill. This is the evidence for the `CHANGE_LOG.md` verdicts on sales skills.
   - **Judge-scored loops don't replace it.** With n≈1 per pursuit, a judge only measures agreement with its own rubric.

## Optimizations/Gotchas
- **This is a frontmatter + linking pattern, not a new folder.** Pursuits live on the same `Clients/<Company>.md` notes the vault already uses for accounts — adding a parallel `Pursuits/` folder would just create a second place to look. The dashboard visibility comes from `Bases/Pursuits.base` filtering `pursuit == true`, not from file location.
- **A career-track pursuit is still an "account" note structurally** (same folder, same frontmatter shape) even though the buyer/seller relationship is inverted — don't invent a separate note type for it; `pursuit_type` carries the distinction.
- **Stage updates overwrite `pursuit_stage`, they don't append a new note** — the whole point is one durable place per company, not a new file per stage change. Log the stage history as dated lines inside the `## Pursuit` section body instead.
- **Set `pursuit: false` (don't delete) once resolved** (won/lost/hired/passed) — closed pursuits still answer "did we ever pursue this" without cluttering the live dashboard filter.
- **This skill is the safety net, not the trigger for new research** — it never initiates a Porter teardown or proposal red-team itself; it just makes sure whatever those skills already produced doesn't go untracked.

**Worked example:** Company A — a `career-opportunity` pursuit (Director Digital Business, 2nd hearing round) that generated four `output/` deliverables (hearing cheat sheet, deck, notes, competitive Porter dossier) before this skill existed to give it a `Clients/` anchor or a link back to `[[career-manufacturing-cto-positioning]]`. Acme is the `sales-deal` counterpart — already well-tracked in prose (`Clients/Acme.md`'s 🔥-flagged TL;DR); this skill just formalizes that into `pursuit_stage` so it surfaces on `Bases/Pursuits.base` alongside career-track pursuits instead of only being visible by opening the note.

**Feedback & Skill Verification**
- Would you like to provide feedback to optimize this workflow or execution?
- Should we update this skill (or add a new one) based on how this went?
