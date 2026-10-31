---
id: strategic-options
aliases: [strategic-options]
name: "Strategic Options"
category: strategy
description: Generates and compares strategic options with clear decision criteria, trade-offs, and recommendation logic. Use for strategy options, path selection, growth choices, market entry choices, build-buy-partner, or "what are our options?" questions.
triggers: [strategy options, path selection, growth choices, market entry choices, build-buy-partner, what are our options]
tags: [strategy, consulting, strategic-choice-and-economics]
related: ["[[business-case-builder]]", "[[portfolio-review]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-07-26
updated: 2026-07-26
# imported verbatim (body unchanged) from aapersh/strategy-skills-for-claude, skills/03-strategic-choice-and-economics/strategic-options.md — original frontmatter used name: "strategic-options" (slug-as-name convention); description preserved above.
---

# Strategic Options

## Contract
- **Input:** the strategic decision to be made and the constraints bounding it.
- **Output:** the Strategic Options structure below, delivered inline; save to `output/` for board-facing option reviews (Charter §4).
- **Allowed tools/artifacts:** conversation plus user-supplied data.
- **Done when:** at least two meaningfully distinct options are scored against the same criteria, the Recommendation states what must be true, and Next Tests names the evidence that would change the call.

## When To Use

Use this skill when the user needs alternatives before committing to a strategy. It helps avoid false binaries and creates a defensible path from options to recommendation.

## Strategy-Consulting Approach

Develop a small set of distinct, viable options. Compare them against decision criteria that matter. Recommend a path with trade-offs visible.

## Workflow

1. Clarify the strategic decision and constraints.
2. Generate mutually distinct options.
3. Define decision criteria.
4. Assess each option against attractiveness, feasibility, risk, economics, and strategic fit.
5. Identify hybrids or sequencing if useful.
6. Recommend the best path and what must be true.

## Output Format

```markdown
# Strategic Options

## Decision
[Decision being made.]

## Options
| Option | Description | Upside | Trade-Off | What Must Be True |
|---|---|---|---|---|

## Evaluation
| Criteria | Option A | Option B | Option C |
|---|---|---|---|

## Recommendation
[Preferred option and rationale.]

## Next Tests
[Evidence needed before committing.]
```

## Quality Bar

- Options must be meaningfully different.
- Criteria must reflect the user's decision, not generic attractiveness.
- Include trade-offs and risks.
- State what evidence would change the recommendation.
