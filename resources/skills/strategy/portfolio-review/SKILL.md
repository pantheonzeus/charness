---
id: portfolio-review
aliases: [portfolio-review]
name: "Portfolio Review"
category: strategy
description: Reviews a portfolio of markets, products, initiatives, customers, or bets and recommends allocation choices. Use for portfolio review, product portfolio, market portfolio, initiative portfolio, capital allocation, resource allocation, or "where should we invest?" questions.
triggers: [portfolio review, product portfolio, market portfolio, initiative portfolio, capital allocation, resource allocation, where should we invest]
tags: [strategy, consulting, strategic-choice-and-economics]
related: ["[[business-case-builder]]", "[[initiative-prioritizer]]", "[[strategic-options]]"]
status: active
version: 1
created: 2026-07-26
updated: 2026-07-26
# imported verbatim (body unchanged) from aapersh/strategy-skills-for-claude, skills/03-strategic-choice-and-economics/portfolio-review.md — original frontmatter used name: "portfolio-review" (slug-as-name convention); description preserved above.
---

# Portfolio Review

## Contract
- **Input:** the portfolio (products, markets, initiatives, or bets) and the allocation decision at stake.
- **Output:** the Portfolio Review structure below, delivered inline; save to `output/` for an annual-planning or capital-allocation cycle (Charter §4).
- **Allowed tools/artifacts:** conversation plus user-supplied performance data.
- **Done when:** every portfolio item is scored on the same criteria set, each carries an invest/maintain/fix/harvest/exit recommendation, and every Allocation Move names its resource trade-off.

## When To Use

Use this skill when the user needs to assess a set of businesses, products, markets, initiatives, or strategic bets and decide where to invest, hold, fix, or exit.

## Strategy-Consulting Approach

Compare portfolio elements on attractiveness, performance, strategic fit, right to win, and resource needs. Recommend allocation choices, not just rankings.

## Workflow

1. Define the portfolio and decision question.
2. Select evaluation criteria.
3. Score each portfolio element.
4. Identify invest, maintain, fix, harvest, and exit candidates.
5. Assess resource reallocation implications.
6. Recommend portfolio moves and next decisions.

## Output Format

```markdown
# Portfolio Review

## Portfolio Scope
[What is included and excluded.]

## Evaluation Matrix
| Item | Attractiveness | Performance | Fit | Right To Win | Recommendation |
|---|---|---|---|---|---|

## Allocation Moves
| Move | Rationale | Resource Implication |
|---|---|---|

## Decisions Required
1. [Decision]
2. [Decision]
3. [Decision]
```

## Quality Bar

- Use consistent criteria across the portfolio.
- Separate performance from attractiveness.
- Recommend allocation actions.
- Name the trade-offs created by reallocating resources.
