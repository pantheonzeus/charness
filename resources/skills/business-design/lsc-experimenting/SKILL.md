---
id: lsc-experimenting
aliases: [lsc-experimenting]
name: "LSC 21 — Experimenting Canvas"
category: business-design
description: Run the Lean Service Creation "Experimenting" canvas — list the main assumptions, label each "think / know / checked", design the experiment and success criteria before running, record key findings, and name what will make the concept fail.
triggers: [experimenting canvas, LSC experimenting, assumption register, our main assumptions, how to experiment, success criteria for the experiment, do you think do you know did you check, validate assumptions before building, experiment log, riskiest assumptions, why will this fail]
tags: [lean-service-creation, lsc, canvas, experiments, assumptions, validation]
related: ["[[lean-service-creation]]", "[[lsc-validation]]", "[[lsc-emotional-concept-sheet]]", "[[lsc-business-model-market-size]]", "[[business-experiment-design]]", "[[assumption-audit]]", "[[lsc-weekly-board]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 21 — Experimenting

## Contract
- **Input:** all concept canvases (08–13), the 14 scorecard's weak spokes, the 15 conclusions.
- **Output:** `canvases/21-experimenting.md`: the assumption register with experiment, success criterion, key findings, status; plus the "will fail because of" list. Updated throughout the build phase.
- **Allowed tools/artifacts:** `business-experiment-design` (test cards, evidence ladder), `strategy/assumption-audit`, analytics and landing-page tools the user has.
- **Done when:** the top assumptions each have a success criterion written before the experiment, a status (think / know / checked), and findings that cite data; the "fails because of" statement is written.

## Canvas (v3.0.5) — "Validating your assumptions before building it."
Columns: **OUR MAIN ASSUMPTIONS** · **HOW TO EXPERIMENT** · **SUCCESS CRITERIA** · **KEY FINDINGS**, over seven rows. Vertical: **IF THE CONCEPT OR BUSINESS DOESN'T WORK, IT WILL FAIL BECAUSE OF:** Footer: **DO YOU THINK? DO YOU KNOW? DID YOU CHECK?**

## Core Blueprint
1. **Harvest assumptions** from every canvas: customer group exists (03), need real (05), would use (08/09), would pay (12), can be built (13), partners will act (11), impact claims (10). Write each as "We believe that…". Give ids H-01…
2. **Complete the sentence** "If the concept or business doesn't work, it will fail because of: …" with the top three. These are the riskiest assumptions.
3. **Status of each:** *think* (guess, `[I]`), *know* (we have `[O]` evidence), *checked* (a test with pre-set criterion passed or failed). Only *checked* items count at gates.
4. **Rank** by importance × uncertainty (`assumption-audit` method). Work the top three first.
5. **Design the cheapest experiment per assumption** (see the evidence ladder in `business-experiment-design`): interview probe, fake ad, landing page, concierge service, pre-sale, spike, pilot.
6. **Write the success criterion before running:** metric, threshold, sample, date. Not changed afterwards without a logged reason.
7. **Run, record key findings** as data (numbers, quotes), then the decision: assumption confirmed, killed, or needs a stronger test.
8. **Escalate evidence strength** on survivors; a passed weak test earns a stronger test, not a launch.
9. **Sync** with 15 (verdict) and 19 ("week's validation" cites H-ids).

## Quality tests
- Every assumption is falsifiable and has an id.
- "Think / know / checked" assigned honestly; "checked" requires a stored criterion and result.
- Criteria were written before data collection (timestamp or file history).
- Top three failure causes are explicit.
- Findings contain data, not opinion.

## Agent-augmented variant
Agents can derive assumption lists from canvases and build the experiment assets (`[S]`) and analyse results. Pre-testing with synthetic personas sharpens hypotheses only; results are not entered under "checked" (`agent-augmented-discovery`).

## Handbook 2.0 guidance (book, Futurice 2018, paraphrased)
Handbook guidance:
- Treat it like a moon landing: cut the problem into pieces and run step-by-step experiments instead of assuming the whole works.
- It is the antidote to following the official process step regardless of what is most critical (the example: building a prototype because the process says phase B3, when the canvas shows the value proposition is the thing to test).
- Method: each person writes one or two critical assumptions on sticky notes (wrong means the whole vision fails; technology, business, customer, project, organisation), the team discusses and votes.
- A good experiment is simple, fast and cheap. Example: instead of commissioning a market-research study on whether venues will install new wi-fi, phone three venue managers today.
- Set success criteria before the experiment because humans interpret results to show they were right. Key findings also cover what you learn about communicating the value proposition and recruiting participants.

## Gotchas
- **Confusing "know" with "checked".** Opinions of colleagues are not checks.
- **Moving thresholds.** The cardinal sin; log any change with the reason.
- **Testing the wrong thing.** A page with two changes cannot tell you which failed.
- **Ethics and law.** Fake-door tests that take money need a refund path and legal clearance.

## Hand-offs
Verdicts flow to `lsc-validation` (15). Depth: `business-experiment-design`, `strategy/assumption-audit`.
