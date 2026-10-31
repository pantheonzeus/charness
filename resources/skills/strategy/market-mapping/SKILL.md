---
id: market-mapping
aliases: [market-mapping]
name: "Market Mapping"
category: strategy
description: Sizes and segments markets using top-down and bottom-up logic, then identifies white space and where-to-play choices. Use for market mapping, TAM/SAM/SOM, market entry, segmentation, white space, category strategy, or opportunity sizing.
triggers: [market mapping, TAM SAM SOM, market entry, segmentation, white space, category strategy, opportunity sizing]
tags: [strategy, consulting, market-and-competitive-intelligence]
related: ["[[profit-pool-analysis]]", "[[customer-segmentation]]", "[[competitive-intel]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-07-26
updated: 2026-07-26
# imported verbatim (body unchanged) from aapersh/strategy-skills-for-claude, skills/02-market-and-competitive-intelligence/market-mapping.md — original frontmatter used name: "market-mapping" (slug-as-name convention); description preserved above.
---

# Market Mapping

## Contract
- **Input:** the market/category to size and the decision the sizing must support.
- **Output:** the Market Map structure below, delivered inline; save to `output/` for a market-entry or investment-screening engagement (Charter §4).
- **Allowed tools/artifacts:** conversation plus user-supplied data; web research for external market-size figures, always cited and never presented as more precise than the source supports.
- **Done when:** at least two independent sizing methods appear with a stated Confidence rating each, and every segment in the Segment Map is MECE and mapped to a where-to-play option.

## When To Use

Use this skill when the user needs to understand a market's structure, size, segments, growth, economics, and white space. It fits market entry, expansion, category creation, and investment screening.

## Strategy-Consulting Approach

Build the market map from multiple angles. Segment MECE, cross-check top-down and bottom-up sizing, then link the map to where-to-play choices.

## Workflow

1. Define the market boundary and decision question.
2. Ask for geography, customer type, product scope, and time horizon.
3. Build top-down sizing logic.
4. Build bottom-up sizing logic.
5. Segment the market by needs, economics, channels, behavior, or use case.
6. Identify attractive spaces, contested spaces, and white space.
7. Recommend where further analysis should focus.

## Output Format

```markdown
# Market Map

## Market Definition
[Boundary, exclusions, geography, time horizon.]

## Size Estimate
| Method | Logic | Estimate | Confidence |
|---|---|---|---|

## Segment Map
| Segment | Size | Growth | Profitability | Competition | Attractiveness |
|---|---|---|---|---|---|

## White Space
[Where needs are unmet or competition is weak.]

## Where-To-Play Options
1. [Option]
2. [Option]
3. [Option]
```

## Quality Bar

- Define the market before sizing it.
- Use at least two sizing approaches when possible.
- Make segments MECE and decision-relevant.
- Separate market attractiveness from right to win.
