---
id: pricing-strategy
aliases: [pricing-strategy]
name: "Pricing Strategy"
category: strategy
description: Diagnoses pricing power, willingness to pay, discounting, packaging, and monetization opportunities. Use for pricing strategy, discount leakage, monetization, packaging, price increase, value pricing, renewal pricing, or margin improvement.
triggers: [pricing strategy, discount leakage, monetization, packaging, price increase, value pricing, renewal pricing, margin improvement]
tags: [strategy, consulting, strategic-choice-and-economics]
related: ["[[customer-segmentation]]", "[[business-case-builder]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-07-26
updated: 2026-07-26
# imported verbatim (body unchanged) from aapersh/strategy-skills-for-claude, skills/03-strategic-choice-and-economics/pricing-strategy.md — original frontmatter used name: "pricing-strategy" (slug-as-name convention); description preserved above.
---

# Pricing Strategy

## Contract
- **Input:** the pricing question, plus whatever price, discount, win-loss, or margin data the user can supply.
- **Output:** the Pricing Strategy structure below, delivered inline; save to `output/` for a monetization program (Charter §4).
- **Allowed tools/artifacts:** conversation plus user-supplied pricing/margin data; web research for competitor pricing context, cited.
- **Done when:** every Diagnosis row cites real evidence rather than assumed leakage, each Recommended Move carries a segment-level rationale, and Risks and Tests names a pilot or rollout sequence.

## When To Use

Use this skill when the user needs to improve monetization, diagnose discounting, raise prices, redesign packaging, or understand willingness to pay.

## Strategy-Consulting Approach

Connect price to value, customer segments, competitive alternatives, and sales behavior. Separate list price, realized price, discounting, mix, and packaging.

## Workflow

1. Define the pricing question and economic objective.
2. Gather price architecture, discount data, win-loss, churn, margin, and competitor context.
3. Diagnose leakage across list price, discounting, mix, packaging, and governance.
4. Assess willingness to pay by segment or use case.
5. Generate pricing moves and risks.
6. Recommend a pricing action plan and test design.

## Output Format

```markdown
# Pricing Strategy

## Pricing Objective
[Growth, margin, retention, adoption, or simplification.]

## Diagnosis
| Area | Evidence | Issue | Impact |
|---|---|---|---|

## Segment Price Logic
| Segment | Value Driver | WTP Signal | Pricing Move |
|---|---|---|---|

## Recommended Moves
1. [Move]
2. [Move]
3. [Move]

## Risks and Tests
[Risks, mitigations, and pilot design.]
```

## Quality Bar

- Do not recommend a price move without segment logic.
- Separate price realization from list pricing.
- Include customer risk and sales execution risk.
- Recommend a test or rollout sequence.
