---
id: growth-barriers
aliases: [growth-barriers]
name: "Growth Barriers"
category: strategy
description: Identifies the true constraint blocking growth and separates root causes from symptoms. Use for stalled growth, revenue plateau, funnel issues, retention problems, sales productivity, market expansion blockers, or "why are we not growing?" questions.
triggers: [stalled growth, revenue plateau, funnel issues, retention problems, sales productivity, market expansion blockers, why are we not growing]
tags: [strategy, consulting, diagnosis-and-framing]
related: ["[[situation-assessment]]", "[[assumption-audit]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-07-26
updated: 2026-07-26
# imported verbatim (body unchanged) from aapersh/strategy-skills-for-claude, skills/01-diagnosis-and-framing/growth-barriers.md — original frontmatter used name: "growth-barriers" (slug-as-name convention); description preserved above.
---

# Growth Barriers

## Contract
- **Input:** a growth target/gap and whatever funnel, retention, or sales-productivity data the user can supply.
- **Output:** the Growth Barrier Diagnosis structure below, delivered inline; save to `output/` and index into the vault for a standing engagement (Charter §4).
- **Allowed tools/artifacts:** conversation plus user-supplied data.
- **Done when:** the Binding Constraint names one or two causes (never a long list), every Barrier Assessment row carries real evidence and a confidence level, and each Recommended Action traces directly to the diagnosed constraint.

## When To Use

Use this skill when growth is underperforming and leadership is debating symptoms. It helps identify the binding constraint across demand, conversion, retention, monetization, capacity, product, and execution.

## Strategy-Consulting Approach

Build a growth driver tree, quantify where momentum breaks, and isolate the constraint that matters most. Treat growth as a system, not a list of initiatives.

## Workflow

1. Define the growth target, baseline, and gap.
2. Build a driver tree for growth.
3. Gather signals across acquisition, activation, conversion, retention, expansion, pricing, and capacity.
4. Identify where the funnel or system breaks.
5. Distinguish symptoms from root causes.
6. Recommend the highest-leverage tests or actions.

## Output Format

```markdown
# Growth Barrier Diagnosis

## Growth Gap
[Target, current trajectory, size of gap.]

## Driver Tree
[MECE breakdown of growth drivers.]

## Barrier Assessment
| Driver | Evidence | Impact | Confidence | Root Cause |
|---|---|---|---|---|

## Binding Constraint
[The constraint most limiting growth.]

## Recommended Actions
1. [Action]
2. [Action]
3. [Action]
```

## Quality Bar

- Start from the growth equation.
- Identify one or two binding constraints, not a long issue list.
- Use evidence to separate cause from symptom.
- Link every action to the diagnosed constraint.
