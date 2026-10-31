---
id: competitor-intelligence
aliases: [competitor-intelligence]
name: "Competitor Intelligence — Standing Notes from Teardown Output"
category: sales
description: Promote named competitors and their digital-business assessments out of one-off Porter/teardown deliverables into standing, cross-engagement vault notes, so competitive knowledge compounds across pursuits instead of resetting every time.
triggers: [competitor note, track this competitor, competitor profile, competitive intelligence archive, has this competitor come up before, competitor dashboard, who competes with]
tags: [sales, competitive-intelligence, knowledge-graph]
related: ["[[competitive-porter-teardown]]", "[[company-challenger-brief]]", "[[pursuit-deal-tracking]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-07-25
updated: 2026-07-25
vault_writes: ["cbrain/Competitors/*", "cbrain/Clients/*"]
---

# Competitor Intelligence — Standing Notes from Teardown Output

## Contract
- **Input:** a named, verified competitor surfaced by `[[competitive-porter-teardown]]` (or `[[company-challenger-brief]]`) — real, evidence-backed, never a hypothesized-but-unverified name (that's the producer skill's job to have already dropped).
- **Output:** `cbrain/Competitors/<Competitor>.md` — created or updated — carrying its digital-business assessment, evidence citations, and every pursuit/engagement it's been relevant to. Surfaced via `Bases/Competitors.base`.
- **Allowed tools/artifacts:** vault file edits only. No new research — this skill promotes findings a teardown already produced and evidence-gated; it never originates a competitive claim itself.
- **Done when:** every named competitor from a completed teardown with a genuine digital-business finding (not a `[VIEW] — not researched` placeholder) has a `Competitors/` note, cited, linked back to the pursuit that produced the finding, and appears in `Bases/Competitors.base`.

**Triggers/Context**
- Automatically, as the last step of `[[competitive-porter-teardown]]`'s Step 6 (evidence gate) — promotion is part of that skill's done-when, not a separate ask.
- On demand: "have we looked at this competitor before", "what do we know about X".

## Core Blueprint
1. **Check for an existing note first.** `cbrain/Competitors/<Competitor>.md` — a competitor seen across two engagements (e.g. a supplier competing in two client pursuits) gets **one** compounding note, not a duplicate per pursuit. Grep the folder before creating.
2. **Create/extend the note:**
   ```yaml
   ---
   type: competitor
   status: active
   sector: "<one line — the market/division it competes in>"
   ---
   # <Competitor Name>

   ## Digital-business assessment
   - <capability/product, cited>
   - <where they're ahead / behind, concretely — not "more digital"; the specific capability, live vs. roadmap>

   ## Seen in
   - [[<Company>]] — <pursuit/engagement context, one line, dated>

   ## Sources
   - <citation per claim, carried over from the teardown dossier>
   ```
3. **Carry the citation, not just the conclusion.** Every claim on the competitor note keeps the same `[CITED]`/`[MODEL]`/`[VIEW]` provenance tag it had in the source dossier (per `_shared/evidence-gate.md`) — a promoted note is not an excuse to launder an estimate into an unqualified fact.
4. **Link back bi-directionally.** The pursuit's `Clients/<Company>.md` note gets a `Competitors: [[X]], [[Y]]` line; each competitor note's "Seen in" section links back. This is what makes the second teardown against the same competitor start from prior knowledge instead of re-researching from zero.
5. **On a repeat sighting, add a dated line, don't overwrite.** A competitor's digital posture is a moving target — append `**2026-XX-XX (via [[Company]]):** <what changed or reconfirmed>` rather than replacing the assessment, so drift over time is visible.

## Optimizations/Gotchas
- **This skill has no research authority of its own.** If a claim wasn't evidence-gated by the producing teardown, this skill does not promote it — "we should track this competitor" is not the same as "we have a cited finding about them." An under-researched competitor gets a thin note that says so, not a padded one.
- **Folder is `cbrain/Competitors/`, not `cbrain/Clients/Competitors/`** — deliberately outside `Clients/` so it never pollutes `Bases/People.base` (that Base's filter is folder + `status != null` only, with no `type` check, so anything dropped inside `Clients/` leaks into the people dashboard).
- **A competitor with a digital offering genuinely equal to or behind the target company** is exactly as valuable to record as one that's ahead — the Company A Porter dossier's most useful finding was a counter-finding ("Competitor X is probably ahead of Competitor Y, that's a narrative gap not a technology gap"). Don't only promote the scary competitors.
- **Market-size figures stay flagged as directional** on the standing note too, not just in the original dossier — the caveat doesn't expire when the finding gets promoted.

**Worked example:** the Company A competitive Porter dossier (`output/20260724-company-a-competitive-porter-dossier.md`) named competitors across five divisions (a dozen-plus named competitors) with per-division digital-maturity findings — exactly the shape this skill promotes into standing notes instead of letting them live only inside that one dossier.

**Feedback & Skill Verification**
- Would you like to provide feedback to optimize this workflow or execution?
- Should we update this skill (or add a new one) based on how this went?
