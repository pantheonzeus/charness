---
id: business-case-builder
aliases: [business-case-builder]
name: "Business Case Builder"
category: strategy
description: Builds evidence-backed business cases with economics, assumptions, sensitivities, risks, and decision logic. Use for investment cases, ROI, payback, NPV, board cases, initiative funding, product bets, or "does this business case work?" questions.
triggers: [investment case, ROI, payback, NPV, board case, initiative funding, product bet, does this business case work]
tags: [strategy, consulting, strategic-choice-and-economics]
related: ["[[strategic-options]]", "[[portfolio-review]]", "[[assumption-audit]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-07-26
updated: 2026-07-26
# imported verbatim (body unchanged) from aapersh/strategy-skills-for-claude, skills/03-strategic-choice-and-economics/business-case-builder.md — original frontmatter used name: "business-case-builder" (slug-as-name convention); description preserved above.
---

# Business Case Builder

## Contract
- **Input:** the investment decision/option under review, plus whatever cost/value data the user can supply.
- **Output:** the Business Case structure below, delivered inline; save to `output/` and index into `cbrain/notes/Deliverables/` for a board-facing case (Charter §4).
- **Allowed tools/artifacts:** conversation plus user-supplied data.
- **Done when:** every Value Driver carries an Evidence rating and a Sensitivity range (never a single point estimate), downside/base/upside are all populated, and the Recommendation states proceed/test/redesign/stop with rationale.

## When To Use

Use this skill when a strategic choice needs quantified economics and a clear investment decision. It fits new products, market entry, transformation programs, pricing moves, M&A screening, and major initiatives.

## Strategy-Consulting Approach

Build the case around decision logic, not spreadsheet detail. Make assumptions visible, size value and cost, test sensitivities, and state the decision threshold.

## Workflow

1. Define the decision and investment option.
2. Identify value drivers, cost drivers, timing, and risks.
3. Build base, downside, and upside cases.
4. Surface load-bearing assumptions.
5. Calculate relevant metrics such as ROI, payback, NPV, margin impact, or cash impact.
6. Recommend proceed, test, redesign, or stop.

## Output Format

```markdown
# Business Case

## Decision
[Decision and option under review.]

## Economics Summary
| Metric | Downside | Base | Upside |
|---|---|---|---|

## Value Drivers
| Driver | Assumption | Evidence | Sensitivity |
|---|---|---|---|

## Cost and Investment
[Major cost categories and timing.]

## Risks
[Key risks and mitigations.]

## Recommendation
[Decision and rationale.]
```

## Quality Bar

- Show assumptions and confidence levels.
- Include downside and sensitivity, not only base case.
- Tie metrics to the actual decision.
- Avoid false precision.
