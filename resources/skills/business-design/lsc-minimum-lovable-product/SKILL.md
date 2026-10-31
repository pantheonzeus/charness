---
id: lsc-minimum-lovable-product
aliases: [lsc-minimum-lovable-product]
name: "LSC 16 — Minimum Lovable Product Canvas"
category: business-design
description: Run the Lean Service Creation "Minimum Lovable Product" canvas — the absolute minimum user needs, business requirements and implementation, ranked Must / Should / Could, with everything else parked in the MVP backlog.
triggers: [minimum lovable product, MLP, LSC minimum lovable product, MVP scope, what is the minimum, must should could, cut the scope, first release scope, MVP backlog, minimum implementation, what do we build first]
tags: [lean-service-creation, lsc, canvas, mvp, scope, prioritisation]
related: ["[[lean-service-creation]]", "[[lsc-insight]]", "[[lsc-validation]]", "[[lsc-feasibility-study]]", "[[lsc-agile-board]]", "[[service-concept-prototyping]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 16 — Minimum Lovable Product

## Contract
- **Input:** `canvases/05-insight.md` (selected needs), `12-…` (business minimum), `13-…` (simplified scope), `15-validation.md`.
- **Output:** `canvases/16-minimum-lovable-product.md`: a grid (rows Must / Should / Could × columns user needs, business requirements, minimum implementation) plus the "Later" backlog.
- **Allowed tools/artifacts:** upstream canvases, sponsor and team session, `service-concept-prototyping` for prototype choices.
- **Done when:** each Must item traces to a validated need or a business requirement, the cut line has been agreed with the sponsor, and the Later list is stored as the backlog for the agile board.

## Canvas (v3.0.5) — "Nothing but the essential."
Columns: **User needs** (*What is the absolute minimum needed for the user to love your solution?*) · **Business Requirements** (*What is the minimum value we have to achieve from the business point of view?*) · **Minimum implementation** (*What is the absolutely minimum that needs to happen to deliver a first solution?*). Rows: **Needs MVP must fulfil** (Must), **Should**, **Could**. **Later:** features, integrations, investments and requirements we don't yet need in the MVP → *To MVP backlog.* Callout: **ASK WHY.**

## Core Blueprint
1. **List candidates.** Pull needs from 05, requirements from 12 (revenue, cost, learning needed), constraints from 13 (simplification). One line each, solution-free for needs.
2. **Test each user need for "lovable".** "If this is missing, would the main group refuse or stop using it?" Must = yes. Should = they would complain. Could = they would barely notice. Evidence from interviews or tests, tagged. **[house]** The product must be lovable, not merely viable: a Must list that only works technically fails.
3. **Business minimum.** What must the first release prove or earn to justify going on: a conversion, a paid pilot, a retention figure, a cost-to-serve figure? State as numbers from 01 and 12.
4. **Minimum implementation.** For each Must, the least that delivers it: manual first, existing tool, partner, a narrow segment, one channel. Link to the simplification in 13.
5. **Ask why for every Must.** If the answer is not a user need or business requirement, move it to Later.
6. **Cut line.** Count the Musts against capacity (18, 20); if they do not fit, simplify further instead of extending the timeline.
7. **Later list.** Store with reason and trigger ("add when pilot has 10 users"). It becomes the backlog of 20.
8. **Link to hypotheses:** each Must states the validation (15, 21) it will produce when live.

## Quality tests
- Each Must has a "because" tied to an id from 05 or 12.
- "Lovable" justified by quotes or test data.
- Minimum implementation lists the cheapest route per Must, including manual routes.
- Later items each have a reason and a re-entry trigger.
- Musts fit the capacity in 18 within the agreed horizon.

## Agent-augmented variant
Agents can propose a Must/Should/Could split and flag candidates lacking evidence (`[S]`). Agents also lower implementation cost: draft a concierge or prototype plan. Cut-line decisions stay with the sponsor and team.

## Handbook 2.0 guidance (book, Futurice 2018, paraphrased)
Handbook guidance:
- The name replaces MVP to avoid fruitless debate: the MLP is the minimum customers will fall in love with, and it must also deliver enough for your own strategic goals.
- User needs form a numbered, prioritised list. There is only one way to prioritise.
- Business side: recall the 01 goals. Also account for regulation, brand and data protection. If you cut a corner, do it intentionally, not out of ignorance.
- Minimum means minimum. If a feature or investment can be left for later, leave it.
- The Later list feeds `lsc-mvp-backlog` (27); metrics come from `lsc-what-to-measure` (28).

## Gotchas
- **MVP = minimum only.** The "L" is the point: a loveless first release produces misleading negatives.
- **Feature creep via "should".** If it is not needed to learn or to love, it is Later.
- **Hidden Musts.** Legal, security and support obligations are Musts even when users do not ask.

## Hand-offs
Next: `lsc-pitch-creator` (17) and `lsc-agile-board` (20). Prototype choices: `service-design/service-concept-prototyping`.
