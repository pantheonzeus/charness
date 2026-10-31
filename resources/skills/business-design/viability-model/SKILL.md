---
id: viability-model
aliases: [viability-model]
name: "Viability Model — Concept-Stage Unit Economics & Break-Even"
category: business-design
description: Build the concept-stage money model a business designer owns — a driver tree from the chosen business model to revenue, unit economics (contribution margin, CAC, payback, LTV), break-even and a three-scenario range, with every input tagged by evidence and the one or two drivers that decide viability made explicit for testing. Precedes, and is lighter than, a board business case.
triggers: [viability, is it viable, does it make money, unit economics, revenue model numbers, back of the envelope, napkin math, break even, contribution margin, CAC payback, LTV CAC, concept financials, ROI model for concept, cost to serve, viability check]
tags: [business-design, viability, unit-economics, financial-model, driver-tree]
related: ["[[business-model-design]]", "[[business-experiment-design]]", "[[business-case-builder]]", "[[pricing-strategy]]", "[[ai-native-business-model]]", "[[servitization-model-design]]", "[[business-design-engagement]]"]
modules: [evidence-backed-answering, verifier-separation]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
requires:
  optional: [xlsx]
---

# Viability Model — Concept-Stage Unit Economics & Break-Even

## Contract
- **Input:** a chosen business model (revenue streams, cost structure, segments) and whatever numbers exist: prices, volumes, costs, benchmarks.
- **Output:** a viability model as a markdown table set at `output/<YYYYMMDD>-<slug>-viability.md`, plus an `.xlsx` (via the `xlsx` skill) when the user will edit numbers. Format below.
- **Allowed tools/artifacts:** conversation, user data, web search for benchmarks (cite every one), Python for arithmetic.
- **Done when:** every input carries a tag (`observed` / `benchmark` + source / `assumption`); unit economics and break-even are computed by code, not by mental arithmetic; a low/base/high range exists; the two most sensitive drivers are named with the value at which the model breaks; and the verifier step has recorded PASS.

## Triggers/Context
Use as soon as a business model is chosen, before any experiment budget is spent. It answers "under which assumptions does this make money, and which assumption should we test first?" Board-grade NPV, financing and multi-year P&L belong to `strategy/business-case-builder`, which consumes this model's output.

## Core Blueprint
1. **Pick the unit.** The unit of value is the customer, contract, asset, transaction or agent-task. Everything is modelled per unit first, then scaled.
2. **Driver tree.** Revenue = units × adoption × price (or usage × rate, or outcomes × fee). Costs = variable cost per unit (incl. cost-to-serve, and for AI products inference + human-in-the-loop) + fixed costs (team, platform, compliance) + acquisition cost. Draw it as an indented list; each leaf is an input.
3. **Tag every leaf.** No untagged numbers. Benchmarks need a source and date; assumptions get an id (A1, A2…) that flows into `strategy/assumption-audit`.
4. **Unit economics.** Contribution margin per unit, CAC, CAC payback in months, LTV (contribution margin × expected lifetime) and LTV/CAC. For asset-backed models (`servitization-model-design`), add capital tied up per unit and asset utilization.
5. **Break-even.** Units, or months, to cover fixed costs. Compare against the client's investment horizon from the opportunity frame.
6. **Scenarios.** Low/base/high on the 3–5 most uncertain inputs, not on all inputs. Show the result spread.
7. **Sensitivity.** Move each driver ±20% (or along its plausible range). Rank by impact on break-even. Name the **break point**: the value at which the model stops working (e.g. "adoption < 6% → never breaks even in 36 months").
8. **Verifier pass (separate step).** Recompute totals in Python from the leaf inputs, check units (€/month vs €/year, per user vs per account), and confirm every number in the narrative matches the table. Record `Verifier: PASS | FAIL (what)` at the bottom.
9. **Hand off** the top-2 sensitive drivers to `business-experiment-design` as viability hypotheses.

## Output Format
```markdown
# Viability Model — <concept> (<date>)
**Verdict:** viable if <driver> ≥ <value> and <driver> ≤ <value>; break-even in <n> months (base).
## Driver tree (indented, leaf = input id)
## Inputs
| id | Input | Low | Base | High | Unit | Tag · source |
|---|---|---|---|---|---|---|
## Unit economics (base)
| Metric | Value | Formula |
|---|---|---|
## Break-even & scenarios
## Sensitivity (ranked) & break points
## Hypotheses handed to experiments
Verifier: PASS — recomputed <date>
```

## Optimizations/Gotchas
- **Never massage the numbers.** If base case doesn't break even, the verdict says so. This is an inviolable line (Soul.md), not a style choice.
- **Cost-to-serve is the most-forgotten line.** Support, onboarding, field service, and (for AI) inference and human review. Recurring-revenue models live or die on it.
- **AI margins aren't SaaS margins.** AI products have run around 50–60% gross margin versus 80–90% for classic SaaS (BVP). Don't import SaaS benchmarks into an agent business.
- **"If the math doesn't work at 10 customers it won't at 1,000"** (BVP). Model the first 10 customers explicitly before the scaled case.
- **Ranges beat false precision.** Concept-stage numbers have no business carrying two decimal places.

## Sources
Bessemer Venture Partners, "The AI pricing and monetization playbook" (gross-margin ranges, 10-customer rule); Fjord/IDEO postings (ROI modelling as a core business-design activity). See [Sources](../_category.md).
