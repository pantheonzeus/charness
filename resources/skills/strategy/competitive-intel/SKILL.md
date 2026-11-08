---
id: competitive-intel
aliases: [competitive-intel]
name: "Competitive Intel"
category: strategy
description: Models likely competitor moves from incentives, capabilities, constraints, and market position. Use for competitive intelligence, competitor response planning, rival strategy, market defense, strategic threats, or "what will competitors do next?" questions.
triggers: [competitive intelligence, competitor response planning, rival strategy, market defense, strategic threats, what will competitors do next]
tags: [strategy, consulting, market-and-competitive-intelligence]
related: ["[[market-mapping]]", "[[war-gaming]]", "[[competitive-porter-teardown]]", "[[competitor-intelligence]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-07-26
updated: 2026-07-26
# imported verbatim (body unchanged) from aapersh/strategy-skills-for-claude, skills/02-market-and-competitive-intelligence/competitive-intel.md — original frontmatter used name: "competitive-intel" (slug-as-name convention); description preserved above.
# Note: overlaps in theme with sales/competitive-porter-teardown and sales/competitor-intelligence — this skill is the generic single-shot analytical method, those are vault-linked/deal-specific.
---

# Competitive Intel

## Contract
- **Input:** the strategic move or market question to pressure-test against likely competitor response.
- **Output:** the Competitive Intel structure below, delivered inline. For a live, named pursuit, use `[[competitive-porter-teardown]]` and `[[competitor-intelligence]]` instead (see this file's frontmatter note) — this skill is the generic, single-shot method, not the vault-linked/deal-specific one.
- **Allowed tools/artifacts:** conversation plus user-supplied data; web research for named-competitor facts, cited.
- **Done when:** every Likely Move states a trigger, impact, and Confidence rating, and the Response Plan gives at least one observable early-warning signal per scenario.

## When To Use

Use this skill when the user needs to anticipate competitor action before making a move. It is useful for market entry, pricing changes, product launches, channel conflict, M&A threats, and share-defense planning.

## Strategy-Consulting Approach

Do not stop at competitor facts. Infer competitor behavior from incentives, capabilities, constraints, and likely economics. Pre-commit responses before rivals move.

## Workflow

1. Define the strategic move or market question.
2. Identify relevant competitors and substitutes.
3. Map each competitor's goals, assets, constraints, and economics.
4. Infer likely moves under base, aggressive, and defensive scenarios.
5. Assess impact on the user's strategy.
6. Recommend pre-emptive or reactive moves.

## Output Format

```markdown
# Competitive Intel

## Competitor Map
| Competitor | Position | Incentives | Capabilities | Constraints |
|---|---|---|---|---|

## Likely Moves
| Competitor | Most Likely Move | Trigger | Impact | Confidence |
|---|---|---|---|---|

## Response Plan
| Scenario | Early Signal | Recommended Response |
|---|---|---|

## Strategic Implication
[What this means for the user's decision.]
```

## Quality Bar

- Explain why each competitor would act, not only what they may do.
- Distinguish likely moves from high-impact tail risks.
- Include early warning indicators.
- Tie responses to the user's economics and capabilities.
