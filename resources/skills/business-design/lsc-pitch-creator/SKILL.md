---
id: lsc-pitch-creator
aliases: [lsc-pitch-creator]
name: "LSC 17 — Pitch Creator Canvas"
category: business-design
description: Run the Lean Service Creation "Pitch Creator" — wrap the work into challenge-as-opportunity, why, how, validated target group and needs, what, validation, business/user/social impact and next steps, so that others commit; ends with an evidence-gated one-page pitch.
triggers: [pitch creator, LSC pitch, pitch the concept, get others to commit, wrapping it all up, concept pitch, internal pitch, investment pitch for the service, executive pitch, challenge equals opportunity, why how what pitch]
tags: [lean-service-creation, lsc, canvas, pitch, narrative, commitment]
related: ["[[lean-service-creation]]", "[[lsc-business-objective-context]]", "[[lsc-validation]]", "[[lsc-impact-optimizer]]", "[[narrative-builder]]", "[[business-case-builder]]", "[[kpi-architect]]"]
modules: [file-backed-state, evidence-backed-answering, verifier-separation]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
vault_writes: ["cbrain/Clients/*"]
---

# LSC 17 — Pitch Creator

## Contract
- **Input:** canvases 01, 05, 08–10, 12, 15, 16 and the evidence register.
- **Output:** `canvases/17-pitch-creator.md` (the canvas) and a one-page pitch at `output/<YYYYMMDD>-<slug>-pitch.md`, indexed into `cbrain/notes/Deliverables/`.
- **Allowed tools/artifacts:** upstream canvases, `narrative-builder`, `business-case-builder` for board numbers, `_shared/evidence-gate.md`.
- **Done when:** every canvas field pulls from a source canvas, the evidence gate passes with no uncited number, the ask is explicit (budget, people, decision, date), and the sponsor has seen the draft.

## Canvas (v3.0.5) — "For wrapping it all up and getting others to commit"
**Challenge = Opportunity** (what is happening in the world; trends, changes in the business landscape) · **Why** (why important to us; why now; relation to our mission statement) · **How** (the business objective for us as a company; the endeavour we want to drive and benefit from) · **Validated target group and their needs** (what group, what needs, motives and emotions from the interviews) · **What** (the concept and its emotional and rational value proposition) · **Validation** (how validated, what found out) · **Impact:** **Business impact** (what business; what strategic position) · **User impact** · **Social impact** (direct and indirect, society and environment) · **Next steps** (what happens next; what we validate next; what we need from the audience; how colleagues are kept informed).

## Core Blueprint
1. **Audience first.** Write who decides, what they care about, what they already believe, and what the "yes" is. Pitch to the decision, not to the topic.
2. **Fill from sources, not from memory:**
   - Challenge = Opportunity ← 02 trends and landscape (cited).
   - Why ← 01 strategic purpose and mission, "why now" with a dated reason.
   - How ← 01 objective, success goals, ambition.
   - Validated target group ← 03 and 05 with two real quotes.
   - What ← 08 and 09 combined proposition; one line how it works.
   - Validation ← 15 results: tests run, numbers, what failed too.
   - Business impact ← 12 ranges; User impact ← 05/08; Social impact ← 10.
   - Next steps ← 21 and 16: next validation, ask, cadence (19).
3. **Lead with the decision and the money.** First lines: the recommendation, the business outcome, the ask. Then product, then technology (persona lens).
4. **Show the evidence honestly.** State what is validated (`[O]`), what is assumed, what could kill the concept and how you will know. Include one result that did not go well.
5. **Compose the one-pager and a spoken version** (3 minutes). Same facts, same numbers.
6. **Run the evidence gate** (`_shared/evidence-gate.md`): list each numeric and factual claim with tag and source; remove or soften any release-critical claim not supported. Have a reader who did not write the pitch attempt to break it.
7. **Walk the sponsor through** the draft; record the objections as risks or experiments.
8. **Record the gate:** Gate 17: YES (commits) / ITERATE (what is missing) / NO (not now, why). Update the vault: people in the audience, their stated concerns.

## Quality tests
- Each field traces to a source canvas.
- Opening lines carry recommendation, outcome and ask.
- All numbers have tag, source, date; ranges where uncertain.
- One negative or unexpected result included.
- Social impact quantified or marked unknown, never inflated.
- Next steps contain a dated ask with an owner.

## Agent-augmented variant
An agent drafts the pitch from the canvases (`[S]`), with every claim linked to a source canvas line. A second agent or person attempts to find unsupported claims. The human owns tone and final numbers.

## Gotchas
- **Pitching the idea instead of the evidence.** The canvas has a Validation box for a reason.
- **Buzzwords.** Strip "leverage", "synergy", "innovative", "seamless".
- **Hiding risk.** Decision-makers punish surprises later; the persona rule is to state the risk and price it.
- **Confidential data in a shareable pitch.** Check audience rights before including client numbers (Soul: confidentiality).

## Hand-offs
YES → build phase: `lsc-team-weekly` (18), `lsc-weekly-board` (19), `lsc-agile-board` (20). Board-grade numbers: `strategy/business-case-builder`. Narrative polish: `strategy/narrative-builder`.
