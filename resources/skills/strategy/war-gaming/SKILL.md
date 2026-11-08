---
id: war-gaming
aliases: [war-gaming]
name: "War Gaming"
category: strategy
description: Stress-tests strategy against competitor moves, market shifts, customer reactions, regulatory changes, and execution failure. Use for war gaming, scenario planning, strategy stress test, competitive response, risk scenarios, or "what could break this strategy?" questions.
triggers: [war gaming, scenario planning, strategy stress test, competitive response, risk scenarios, what could break this strategy]
tags: [strategy, consulting, risk-performance-and-value-governance]
related: ["[[risk-and-mitigation]]", "[[competitive-intel]]", "[[assumption-audit]]"]
status: active
version: 1
created: 2026-07-26
updated: 2026-07-26
# imported verbatim (body unchanged) from aapersh/strategy-skills-for-claude, skills/05-risk-performance-and-value-governance/war-gaming.md — original frontmatter used name: "war-gaming" (slug-as-name convention); description preserved above.
---

# War Gaming

## Contract
- **Input:** the strategy to stress-test and the scenario dimensions in scope (competitor, market, regulatory, operational, financial).
- **Output:** the Strategy War Game structure below, delivered inline; save to `output/` for board-facing risk review (Charter §4).
- **Allowed tools/artifacts:** conversation plus user-supplied data; web research for competitor/regulatory context, cited.
- **Done when:** scenarios span both likely and painful cases with a Likelihood and Severity each, every Vulnerability has a mitigation, and the Response Playbook names an owner per signal.

## When To Use

Use this skill before committing to a strategy that could be disrupted by rivals, market shifts, execution failure, regulation, customer response, or capital constraints.

## Strategy-Consulting Approach

Pressure-test the strategy before reality does. Simulate likely and high-impact scenarios, identify weak points, and pre-commit response moves.

## Workflow

1. Define the strategy to test.
2. Identify scenario dimensions: competitor, customer, market, regulatory, operational, financial.
3. Build base, adverse, and aggressive scenarios.
4. Assess impact on economics and strategic logic.
5. Identify early warning signals.
6. Recommend defensive and offensive responses.

## Output Format

```markdown
# Strategy War Game

## Strategy Under Test
[Strategy summary.]

## Scenarios
| Scenario | Trigger | Impact | Likelihood | Severity |
|---|---|---|---|---|

## Vulnerabilities
| Weak Point | Why It Matters | Mitigation |
|---|---|---|

## Response Playbook
| Signal | Response | Owner |
|---|---|---|
```

## Quality Bar

- Include likely scenarios and painful scenarios.
- Make early warning signals observable.
- Tie responses to owners and decisions.
- Do not turn the output into a generic risk list.
