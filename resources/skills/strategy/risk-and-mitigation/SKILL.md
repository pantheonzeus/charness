---
id: risk-and-mitigation
aliases: [risk-and-mitigation]
name: "Risk and Mitigation"
category: strategy
description: Builds a strategic risk register with likelihood, impact, mitigations, triggers, owners, and contingency moves. Use for strategy risk, mitigation planning, risk register, board risk review, launch risk, execution risk, or "what could go wrong?" questions.
triggers: [strategy risk, mitigation planning, risk register, board risk review, launch risk, execution risk, what could go wrong]
tags: [strategy, consulting, risk-performance-and-value-governance]
related: ["[[war-gaming]]", "[[value-realization]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-07-26
updated: 2026-07-26
# imported verbatim (body unchanged) from aapersh/strategy-skills-for-claude, skills/05-risk-performance-and-value-governance/risk-and-mitigation.md — original frontmatter used name: "risk-and-mitigation" (slug-as-name convention); description preserved above.
---

# Risk and Mitigation

## Contract
- **Input:** the strategy or initiative under review and its risk categories in scope.
- **Output:** the Strategic Risk Register structure below, delivered inline; save to `output/` for board risk reviews (Charter §4).
- **Allowed tools/artifacts:** conversation plus user-supplied data.
- **Done when:** every Risk Register row has a likelihood, impact, mitigation, owner, and trigger, Highest-Risk Assumptions names what still needs testing, and the recommendation states go/no-go/redesign/gated approval.

## When To Use

Use this skill when a strategy or initiative needs a serious risk view before approval or execution. It fits board materials, launch planning, transformation governance, and investment decisions.

## Strategy-Consulting Approach

Treat risk as part of the strategy, not a compliance appendix. Prioritize risks that could change the decision, economics, timing, or feasibility.

## Workflow

1. Define the strategy or initiative under review.
2. Identify risk categories: market, customer, competitor, financial, operational, regulatory, organizational.
3. Score likelihood and impact.
4. Define mitigations, triggers, owners, and contingency actions.
5. Identify residual risk after mitigation.
6. Recommend go, no-go, redesign, or gated approval.

## Output Format

```markdown
# Strategic Risk Register

## Strategy Under Review
[Brief summary.]

## Risk Register
| Risk | Likelihood | Impact | Mitigation | Owner | Trigger |
|---|---|---|---|---|---|

## Highest-Risk Assumptions
[Assumptions that need testing.]

## Contingency Moves
[Actions to take if triggers occur.]
```

## Quality Bar

- Focus on risks that change decisions.
- Include triggers and owners.
- Show residual risk after mitigation.
- Avoid generic risk language.
