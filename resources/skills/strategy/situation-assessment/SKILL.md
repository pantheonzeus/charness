---
id: situation-assessment
aliases: [situation-assessment]
name: "Situation Assessment"
category: strategy
description: Establishes a fact-based baseline for a business, market, product, or function. Use when the user asks for a situation assessment, current-state diagnosis, business health check, momentum review, strategic baseline, or "where are we really?" analysis.
triggers: [situation assessment, current-state diagnosis, business health check, momentum review, strategic baseline, where are we really]
tags: [strategy, consulting, diagnosis-and-framing]
related: ["[[growth-barriers]]", "[[assumption-audit]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-07-26
updated: 2026-07-26
# imported verbatim (body unchanged) from aapersh/strategy-skills-for-claude, skills/01-diagnosis-and-framing/situation-assessment.md — original frontmatter used name: "situation-assessment" (slug-as-name convention); description preserved above.
---

# Situation Assessment

## Contract
- **Input:** a business, market, product, or function to assess, plus whatever financials, KPIs, or qualitative signals the user can supply.
- **Output:** the Situation Assessment structure below, delivered inline in the response; for a standing engagement or pursuit, save as `output/<topic>-situation-assessment.md` and index into `cbrain/notes/Deliverables/` per this workspace's file-backed-state convention (Charter §4).
- **Allowed tools/artifacts:** conversation plus user-supplied data; web research only if the user asks for external market context, and only when cited.
- **Done when:** every Fact Base row is tagged confirmed-fact, interpretation, or open-question, and the Strategic Issues list holds no more than the 3-5 items that actually matter for the decision.

## When To Use

Use this skill when the user needs a defensible read of the current situation before choosing a strategy. Typical cases include business reviews, turnaround diagnosis, market position checks, operating performance reviews, and board preparation.

## Strategy-Consulting Approach

Build the fact base before debating solutions. Separate facts, interpretations, and open questions. Look across financial performance, market position, customer momentum, competitive posture, operating health, and organizational constraints.

## Workflow

1. Frame the assessment question and decision context.
2. Ask for available facts: financials, KPIs, market data, customer signals, competitive context, and recent changes.
3. Build a MECE current-state view across performance, market, customers, operations, and organization.
4. Identify the few facts that matter most for the decision.
5. Separate confirmed facts from hypotheses and unknowns.
6. Produce a situation read with implications and next diagnostic questions.

## Output Format

```markdown
# Situation Assessment

## Executive Read
[One paragraph on where the business is and why it matters.]

## Fact Base
| Area | Evidence | Interpretation | Confidence |
|---|---|---|---|

## Momentum Signals
| Signal | Direction | Why It Matters |
|---|---|---|

## Strategic Issues
1. [Issue]
2. [Issue]
3. [Issue]

## Open Questions
[Questions that must be answered before committing to a strategy.]
```

## Quality Bar

- Do not recommend before establishing the baseline.
- Label facts, interpretations, and assumptions separately.
- Highlight trend and momentum, not only point-in-time performance.
- End with implications for the decision.
