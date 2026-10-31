---
id: lsc-agile-board
aliases: [lsc-agile-board]
name: "LSC 20 — Agile Board Canvas"
category: business-design
description: Run the Lean Service Creation "Agile Board" — stories flowing across To do, In progress, Testing and Done with the team's own definition of done, seeded from the Minimum Lovable Product and linked to validation hypotheses.
triggers: [agile board, LSC agile board, kanban board canvas, stories to do in progress testing done, definition of done, build backlog, MVP backlog board, sprint board for the service, story board]
tags: [lean-service-creation, lsc, canvas, agile, kanban, delivery]
related: ["[[lean-service-creation]]", "[[lsc-minimum-lovable-product]]", "[[lsc-weekly-board]]", "[[lsc-team-weekly]]", "[[lsc-experimenting]]"]
modules: [file-backed-state]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 20 — Agile Board

## Contract
- **Input:** `canvases/16-minimum-lovable-product.md` (Musts and Later), `canvases/18-…` capacity.
- **Output:** `canvases/20-agile-board.md`: the board (stories × status) and the team's definition of done. State changes are appended with date.
- **Allowed tools/artifacts:** the team's existing tracker if there is one (the board mirrors it, never competes); markdown board otherwise.
- **Done when:** every Must from 16 has a story, each story carries a need id and a hypothesis id, the definition of done is written and agreed, and work in progress respects the limit.

## Canvas (v3.0.5) — "Use agile tools that best fit your project phase and team."
Columns: **STORIES** · **TO DO** · **IN PROGRESS** · **TESTING** · **DONE**. Box: **OUR DEFINITION OF DONE.**

## Core Blueprint
1. **Choose the tool for the phase.** The canvas says to use the agile tools that fit the project phase and team: if a tracker exists, mirror its state here weekly; do not run two boards.
2. **Stories from the MLP.** One story per Must in 16: "As <group from 03> I need a way to <need from 05> so that <consequence>". Add ids: need (N-xx), hypothesis (H-xx from 21).
3. **Definition of done.** Write it as a checklist the team agrees, including validation: "released to a real user", "instrumented to measure H-xx", "tested with the main group". **[house]** Done without learning is not done.
4. **Flow rules.** Limit work in progress (default 2 per person, 6 for the team). **[house]** Testing means tested against the definition and, where relevant, by a user.
5. **Weekly update** before 19: move cards, record cycle times and what blocked them.
6. **Feed from Later.** New items enter only through a decision on 16; unplanned items are marked as such.
7. **Review burn against the plan** at the retro (22): what moved, what stalled, why.

## Quality tests
- Every story links to a need and a hypothesis.
- Definition of done includes a learning or validation step.
- WIP within limit; items stuck > 1 week have a named blocker.
- No story exists that is not in 16 or flagged as decision-added.

## Agent-augmented variant
An agent can draft stories from 16, estimate effort ranges (`[S]`) and write test cases. It may update card status only from real tracker events. It does not mark a story done; the team does, against the definition.

## Handbook 2.0 guidance (book, Futurice 2018, paraphrased)
Handbook guidance:
- The canvas is a placeholder for the team's own board (Scrum, Kanban, whiteboard, or digital for multi-site teams). The product owner holds the prioritised backlog; the team pulls from the top.
- Stories are small and bring clear value to customer or business. Remember the KPIs. The team is not a feature factory.
- Break stories into tasks small enough for a couple of spare hours; small tangible goals motivate.
- Max two items in progress per person; context switching hurts velocity. Test as soon as possible, or you build on unvalidated work.
- Definition of done is relative; examples include integration, performance, stability, user acceptance, regression testing, refactoring, release notes, code review, documentation. Create shared rules visible to all.

## Gotchas
- **Board as theatre of busyness.** Count validated learnings, not moved cards.
- **Hidden work.** Operational and legal tasks need stories too.
- **Scope creep via the board.** New stories need a decision on 16.

## Hand-offs
Feeds `lsc-weekly-board` (19), `lsc-experimenting` (21) and `lsc-retrospective` (22).
