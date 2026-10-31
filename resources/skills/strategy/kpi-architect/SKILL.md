---
id: kpi-architect
aliases: [kpi-architect]
name: "KPI Architect"
category: strategy
description: Designs KPI systems with leading and lagging indicators tied to strategic decisions, ownership, and operating rhythms. Use for KPI design, metrics cleanup, performance management, dashboards, OKRs, vanity metrics, or "what should we measure?" questions.
triggers: [KPI design, metrics cleanup, performance management, dashboards, OKRs, vanity metrics, what should we measure]
tags: [strategy, consulting, risk-performance-and-value-governance]
related: ["[[value-realization]]", "[[transformation-roadmap]]"]
status: active
version: 1
created: 2026-07-26
updated: 2026-07-26
# imported verbatim (body unchanged) from aapersh/strategy-skills-for-claude, skills/05-risk-performance-and-value-governance/kpi-architect.md — original frontmatter used name: "kpi-architect" (slug-as-name convention); description preserved above.
---

# KPI Architect

## Contract
- **Input:** the strategic objective and the decisions the KPI system must serve.
- **Output:** the KPI Architecture structure below, delivered inline; save to `output/` for a transformation-governance engagement (Charter §4).
- **Allowed tools/artifacts:** conversation plus user-supplied current-metrics inventory.
- **Done when:** every KPI names the specific decision it supports and an owner/threshold, at least one vanity metric is flagged for removal, and the KPI set stays small enough to fit on one dashboard.

## When To Use

Use this skill when metrics are noisy, backward-looking, disconnected from decisions, or too numerous. It fits strategy execution, transformation governance, product performance, growth management, and operating reviews.

## Strategy-Consulting Approach

Start from the decisions leaders need to make. Build a small KPI system with outcome metrics, driver metrics, leading indicators, owners, thresholds, and review cadence.

## Workflow

1. Define the strategic objective and decisions.
2. Identify the value driver tree.
3. Separate outcome, driver, and activity metrics.
4. Remove vanity metrics.
5. Assign owners, thresholds, and review cadence.
6. Design the KPI dashboard and governance rhythm.

## Output Format

```markdown
# KPI Architecture

## Strategic Objective
[What the KPI system must manage.]

## KPI System
| KPI | Type | Decision It Supports | Owner | Threshold |
|---|---|---|---|---|

## Driver Tree
[How KPIs connect to value creation.]

## Metrics To Remove
| Metric | Why Remove |
|---|---|

## Review Cadence
[Meeting rhythm, escalation triggers, and owners.]
```

## Quality Bar

- Include leading and lagging indicators.
- Link each KPI to a decision.
- Assign ownership and thresholds.
- Keep the KPI set small enough to manage.
