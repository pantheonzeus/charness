---
id: customer-segmentation
aliases: [customer-segmentation]
name: "Customer Segmentation"
category: strategy
description: Creates MECE customer segments based on needs, economics, behavior, and strategic value. Use for customer segmentation, ICP work, go-to-market focus, retention strategy, pricing segmentation, product strategy, or "which customers should we prioritize?" questions.
triggers: [customer segmentation, ICP work, go-to-market focus, retention strategy, pricing segmentation, product strategy, which customers should we prioritize]
tags: [strategy, consulting, market-and-competitive-intelligence]
related: ["[[market-mapping]]", "[[pricing-strategy]]"]
status: active
version: 1
created: 2026-07-26
updated: 2026-07-26
# imported verbatim (body unchanged) from aapersh/strategy-skills-for-claude, skills/02-market-and-competitive-intelligence/customer-segmentation.md — original frontmatter used name: "customer-segmentation" (slug-as-name convention); description preserved above.
---

# Customer Segmentation

## Contract
- **Input:** the decision the segmentation must support, plus whatever customer/usage data the user can supply.
- **Output:** the Customer Segmentation structure below, delivered inline; save to `output/` for a durable GTM or product engagement (Charter §4).
- **Allowed tools/artifacts:** conversation plus user-supplied data.
- **Done when:** segments are MECE, each carries a stated Priority in the Segment Prioritization table, and every priority segment has a named implication (targeting, pricing, product, or coverage) — not just a ranking.

## When To Use

Use this skill when the user needs sharper customer groups for strategy decisions. It supports targeting, positioning, pricing, retention, product roadmap, account coverage, and investment allocation.

## Strategy-Consulting Approach

Segment customers by decision-relevant differences. Avoid demographic labels unless they predict needs, economics, behavior, or strategic value.

## Workflow

1. Define the decision the segmentation must support.
2. Ask for customer data, performance metrics, usage patterns, needs, and constraints.
3. Identify segmentation dimensions.
4. Build MECE segment options.
5. Score segments by attractiveness and right to win.
6. Recommend priority segments and implications.

## Output Format

```markdown
# Customer Segmentation

## Segmentation Objective
[Decision the segmentation supports.]

## Segment Definitions
| Segment | Defining Traits | Needs | Economics | Behavior |
|---|---|---|---|---|

## Segment Prioritization
| Segment | Size | Growth | Profitability | Fit | Priority |
|---|---|---|---|---|---|

## Strategic Implications
[Targeting, offer, pricing, product, coverage, or retention implications.]
```

## Quality Bar

- Segments must be MECE enough to guide decisions.
- Segment definitions should be observable or testable.
- Prioritize segments with criteria, not preference.
- Explain what changes for each priority segment.
