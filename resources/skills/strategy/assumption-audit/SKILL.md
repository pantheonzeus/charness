---
id: assumption-audit
aliases: [assumption-audit]
name: "Assumption Audit"
category: strategy
description: Surfaces load-bearing assumptions behind a strategy, grades evidence strength, and turns weak beliefs into tests. Use for assumption audits, strategy pressure tests, investment cases, board prep, business plans, or "what has to be true?" questions.
triggers: [assumption audit, strategy pressure test, investment case, board prep, business plan, what has to be true]
tags: [strategy, consulting, diagnosis-and-framing]
related: ["[[situation-assessment]]", "[[growth-barriers]]", "[[war-gaming]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-07-26
updated: 2026-07-26
# imported verbatim (body unchanged) from aapersh/strategy-skills-for-claude, skills/01-diagnosis-and-framing/assumption-audit.md — original frontmatter used name: "assumption-audit" (slug-as-name convention); description preserved above.
---

# Assumption Audit

## Contract
- **Input:** a strategy, plan, or decision whose underlying assumptions need pressure-testing.
- **Output:** the Assumption Audit structure below, delivered inline; save to `output/` for board-prep or investment-case engagements (Charter §4).
- **Allowed tools/artifacts:** conversation plus whatever plan/strategy detail the user supplies.
- **Done when:** every load-bearing assumption in the register carries an Evidence Strength grade, and every weak load-bearing assumption has a Test Plan row with a data need, owner, and decision trigger — none left as a bare, untested belief.

## When To Use

Use this skill when a plan sounds plausible but rests on beliefs that have not been tested. It is especially useful before board reviews, major investments, launches, acquisitions, and expansion decisions.

## Strategy-Consulting Approach

Find the beliefs that carry the weight of the strategy. Grade each belief by evidence strength, importance, and testability. Convert weak assumptions into specific validation work.

## Workflow

1. Identify the strategy, decision, or plan being audited.
2. Extract explicit and implicit assumptions.
3. Separate assumptions into market, customer, economic, operational, competitive, and organizational categories.
4. Score each assumption by importance and evidence strength.
5. Identify load-bearing assumptions.
6. Convert weak load-bearing assumptions into tests.

## Output Format

```markdown
# Assumption Audit

## Strategy Being Tested
[Brief description.]

## Assumption Register
| Assumption | Category | Importance | Evidence Strength | Risk |
|---|---|---|---|---|

## Load-Bearing Assumptions
1. [Assumption and why it matters]
2. [Assumption and why it matters]

## Test Plan
| Assumption | Test | Data Needed | Owner | Decision Trigger |
|---|---|---|---|---|

## Recommendation
[Proceed, pause, test first, or redesign.]
```

## Quality Bar

- Include implicit assumptions, not only stated ones.
- Prioritize assumptions that could change the decision.
- Avoid vague tests. Each test needs evidence, owner, and trigger.
- Show what action follows if an assumption fails.
