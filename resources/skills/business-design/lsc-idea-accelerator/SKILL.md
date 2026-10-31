---
id: lsc-idea-accelerator
aliases: [lsc-idea-accelerator]
name: "LSC 07 — Idea Accelerator Canvas"
category: business-design
description: Run the Lean Service Creation "Idea Accelerator" — take the seed idea and generate three best improvements each for user-need fit, the behavioural gap, the business objective and social purpose, write the accelerated holistic concept, and decide whether to loop with it as the new seed.
triggers: [idea accelerator, LSC idea accelerator, improve the seed idea, behavioural gap, accelerated idea, strengthen the concept draft, seed idea improvement, change the core of the idea, concept draft too weak]
tags: [lean-service-creation, lsc, canvas, ideation, concept, behaviour-change]
related: ["[[lean-service-creation]]", "[[lsc-ideation-sandbox]]", "[[lsc-rational-concept-sheet]]", "[[lsc-business-objective-context]]", "[[lsc-impact-optimizer]]"]
modules: [file-backed-state, self-evolution]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 07 — Idea Accelerator

## Contract
- **Input:** `canvases/06-ideation-sandbox.md` (seed idea), `canvases/05-insight.md`, `canvases/01-…`.
- **Output:** `canvases/07-idea-accelerator.md`: four lanes with three ideas each, the accelerated idea, and a loop decision (round count and verdict).
- **Allowed tools/artifacts:** workshop or conversation; `self-evolution` loop cap; an agent for additional options after humans.
- **Done when:** every lane has three ideas, the accelerated idea integrates at least one idea from each lane, the loop verdict is recorded, and loops did not exceed three rounds.

## Canvas (v3.0.5) — "To make the most out of the selected seed idea"
**Seed idea** (best idea from the Ideation Sandbox). Four lanes, three boxes each:
1. *Three best ideas to make the concept draft (seed idea) better fulfil the user need.*
2. **Behavioural gap** — *What is the behavioural change the user needs to adapt to use the service?* → *Three best ideas to help the user over the gap. Try to change the core of the idea. Don't just add a manual…*
3. **Business objective** — *Regarding the business objective where does the concept draft fall shortest?* → *Three best ideas to match the business objective better.*
4. **Social purpose** — *What is the social and environmental impact of this idea? How is it compared to your goal?* → *How could the concept have a bigger and better social impact or be more sustainable?*
**Accelerated idea** — the holistic concept built from the new ideas. **Are you ready to proceed? Or should we redo this canvas by using the accelerated concept as a seed idea?** NO! ↔ YES!

## Core Blueprint
1. **State the seed** in two sentences, with who and what job, from 06.
2. **Lane 1, need fit.** Re-read the selected needs in 05. Generate three changes that make the seed meet the need more completely or with less effort.
3. **Lane 2, behavioural gap.** Name the change in behaviour the seed demands (new tool, new habit, new trust, new process). Rate its size: small / medium / large, with the interview evidence. Generate three ideas that remove or shrink the change by altering the core of the service. Reject "write a manual", "train them", "send a reminder" unless nothing else works. **[house]**
4. **Lane 3, business objective.** Compare against the 01 goals; name the one where the seed falls shortest and by how much, then three ideas to close it.
5. **Lane 4, social purpose.** Estimate impact against the 01 impact goals. Three ideas to raise the positive or reduce the negative.
6. **Write the accelerated idea:** one paragraph, plus a "what changed vs seed" list tied to the 12 chosen ideas.
7. **Loop decision.** YES: proceed to 08. NO: rerun with the accelerated idea as seed. Cap at three rounds; after round three decide YES or send back to 06 for a different seed, and log why.
8. **Log the round** in `RESPONSE.md`: round number, what changed, verdict.

## Quality tests
- Lane 2 names a concrete behaviour change, and its three ideas alter the service, not add instructions.
- Lane 3 names the specific shortfall metric from 01.
- Accelerated idea uses at least one idea per lane and traces each.
- Round count ≤ 3; NO loops end in YES or a new seed, not drift.

## Agent-augmented variant
After humans fill the lanes, an agent can propose additional options per lane and name behaviour-change precedents from the 02 analogues (`[S]`). It can also red-team the accelerated idea ("what makes a user abandon this in week two?"). Selection stays human.

## Gotchas
- **Feature stacking.** Twelve ideas bolted on create a monster. Integrate or drop.
- **Ignoring the gap.** Services fail on behaviour change more than on features; spend the longest time on lane 2.
- **Society lane as greenwash.** Quantify or label unknown; real analysis follows in 10.

## Hand-offs
Next: `lsc-rational-concept-sheet` (08) and `lsc-emotional-concept-sheet` (09). Behavioural-gap findings are also experiment candidates for `lsc-experimenting` (21).
