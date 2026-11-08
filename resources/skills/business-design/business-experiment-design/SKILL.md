---
id: business-experiment-design
aliases: [business-experiment-design]
name: "Business Experiment Design — Test Cards, Evidence Ladder & Innovation Accounting"
category: business-design
description: Turn the riskiest desirability, viability and feasibility hypotheses into a sequenced experiment plan — Test Cards with pass/fail thresholds set in advance, experiments chosen from a cheap-to-strong evidence ladder (Testing Business Ideas), Learning Cards after each run, and a hypothesis-level innovation-accounting board that drives continue/pivot/kill.
triggers: [test the idea, experiment design, business experiment, test card, learning card, testing business ideas, validate the business model, riskiest assumption test, fake door, landing page test, smoke test, pre-sale, letter of intent, MVP plan, innovation accounting, evidence strength]
tags: [business-design, experimentation, lean-startup, validation, innovation-accounting]
related: ["[[assumption-audit]]", "[[viability-model]]", "[[value-proposition-design]]", "[[business-model-design]]", "[[business-design-engagement]]", "[[agent-augmented-discovery]]", "[[kpi-architect]]", "[[service-concept-prototyping]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
references: [references/experiment-ladder.md]
---

# Business Experiment Design — Test Cards, Evidence Ladder & Innovation Accounting

## Contract
- **Input:** a ranked hypothesis list from `strategy/assumption-audit`, `viability-model` (sensitive drivers) or `value-proposition-design`.
- **Output:** an Experiment Plan plus a living Hypothesis Board at `output/<YYYYMMDD>-<slug>-experiments.md`. Each run appends a Learning Card to the same file. The board is the state file; reopen it by path, never from memory.
- **Allowed tools/artifacts:** conversation, the [experiment ladder](references/experiment-ladder.md), web/landing-page/ad tooling the user has, analytics exports.
- **Done when:** every top-3 hypothesis has a Test Card whose metric and pass threshold were written **before** the run; each card names cost, duration and evidence strength; the sequence moves from cheap/weak to costly/strong; and every completed run has a Learning Card with a decision.

## Triggers/Context
Use after assumptions are ranked and before building anything expensive. Business designers own the **viability** experiments (price, willingness to pay, channel economics, partner commitment). Desirability experiments are shared with the design team. Usability and operability prototypes belong to `service-design/service-concept-prototyping`.

## Core Blueprint
1. **Pick the hypotheses.** Take the top 3 by "importance × lack of evidence". Classify each D (desirability), V (viability) or F (feasibility). Write each as "We believe that <specific, falsifiable claim>."
2. **Choose the first experiment per hypothesis** from the [ladder](references/experiment-ladder.md): the cheapest one that can produce evidence relevant to *this* hypothesis. Start with discovery experiments, move to validation only after a pass.
3. **Write a Test Card before running anything:**
   `Hypothesis · Test (what we do) · Metric (what we measure) · Criteria (pass if ≥ X by <date>) · Cost · Duration · Evidence strength (weak / medium / strong) · Owner`.
   Thresholds are set now and not moved later. Moving them is the cardinal sin.
4. **Prefer what people do over what they say.** Evidence strength rises from opinions (interview statements) through behaviour (clicks, sign-ups) to commitment (pre-payment, signed LOI, pilot budget). Viability hypotheses need commitment-grade evidence before launch.
5. **Run, then write a Learning Card:** `We believed · We observed (data) · From that we learned · Therefore we will (continue / pivot / kill / re-test stronger)`.
6. **Update the Hypothesis Board** (innovation accounting): per hypothesis the strongest evidence so far, the trend, and the next test. This replaces revenue as the progress metric until there is revenue.
7. **Escalate evidence strength** on survivors. A passed weak test earns a medium test, not a launch.
8. **Report at the gate** via `business-design-engagement`: each D/V/F lens with its strongest evidence.

## Output Format
```markdown
# Experiment Plan — <concept>
## Hypothesis Board
| id | Hypothesis | D/V/F | Strongest evidence so far | Strength | Status | Next test |
|---|---|---|---|---|---|---|
## Test Cards
### T1 — <name>
Hypothesis · Test · Metric · Criteria (set <date>) · Cost · Duration · Strength · Owner
## Learning Cards (append per run)
### L1 — <date>
We believed · We observed · We learned · Therefore
```

## Optimizations/Gotchas
- **Agreement isn't evidence.** "Would you use this?" interviews produce weak evidence; anyone can say yes for free.
- **One hypothesis per test.** A landing page testing segment, price and message at once cannot tell you which one failed.
- **B2B viability = commitment.** In B2B, the strong signals are an LOI, a paid pilot, or a budget line, not survey intent.
- **Synthetic tests don't count.** Running a test on LLM personas is pre-work for the test card (sharpen the hypothesis and threshold), never a Learning Card. See `agent-augmented-discovery`.
- **Ethics and law.** Fake-door and pre-sale tests must not take money for something that won't be delivered without a refund path, and must respect consumer-protection and data rules. Check this before launch.

## Sources
Bland & Osterwalder, *Testing Business Ideas* (2019; 44 experiments by cost/time/evidence strength, Test and Learning Cards, D/V/F); Osterwalder et al., *The Invincible Company* (innovation metrics at hypothesis level); Futurice Lean Service Creation (build-measure-learn, kill checkpoints). See [Sources](../_category.md).
