---
id: initiative-prioritizer
aliases: [initiative-prioritizer]
name: "Initiative Prioritizer"
category: strategy
description: Prioritizes initiatives by impact, feasibility, strategic fit, dependencies, and resource constraints. Use for initiative prioritization, roadmap focus, kill list, transformation portfolio, annual planning, resource allocation, or "which projects matter most?" questions.
triggers: [initiative prioritization, roadmap focus, kill list, transformation portfolio, annual planning, resource allocation, which projects matter most]
tags: [strategy, consulting, operating-model-and-execution]
related: ["[[portfolio-review]]", "[[transformation-roadmap]]", "[[operating-model-design]]"]
status: active
version: 1
created: 2026-07-26
updated: 2026-07-26
# imported verbatim (body unchanged) from aapersh/strategy-skills-for-claude, skills/04-operating-model-and-execution/initiative-prioritizer.md — original frontmatter used name: "initiative-prioritizer" (slug-as-name convention); description preserved above.
---

# Initiative Prioritizer

## Contract
- **Input:** the inventory of candidate initiatives and the decision criteria/constraints bounding them.
- **Output:** the Initiative Prioritization structure below, delivered inline; save to `output/` for annual-planning cycles (Charter §4).
- **Allowed tools/artifacts:** conversation plus user-supplied initiative data.
- **Done when:** the Priority Roadmap holds only the vital few (not everything scored "high"), every Kill List entry states a rationale and revisit trigger, and dependencies/sequencing are visible.

## When To Use

Use this skill when the user has too many initiatives and needs a focused roadmap. It is useful for annual planning, transformation programs, OKR planning, cost programs, and product or GTM roadmaps.

## Strategy-Consulting Approach

Force trade-offs. Compare initiatives by value, feasibility, urgency, dependencies, and strategic fit. Produce both a priority list and a defensible kill list.

## Workflow

1. Clarify strategy, constraints, and decision criteria.
2. Inventory initiatives.
3. Score initiatives by impact, feasibility, urgency, and fit.
4. Identify dependencies and sequencing.
5. Select the vital few.
6. Build the roadmap and kill list.

## Output Format

```markdown
# Initiative Prioritization

## Criteria
[Decision criteria and weights if useful.]

## Initiative Assessment
| Initiative | Impact | Feasibility | Fit | Priority | Rationale |
|---|---|---|---|---|---|

## Priority Roadmap
| Phase | Initiative | Owner | Milestone |
|---|---|---|---|

## Kill List
| Initiative | Reason | Revisit Trigger |
|---|---|---|
```

## Quality Bar

- Do not make everything high priority.
- Include a kill list with rationale.
- Show dependencies and sequencing.
- Tie prioritization to strategy and resource constraints.
