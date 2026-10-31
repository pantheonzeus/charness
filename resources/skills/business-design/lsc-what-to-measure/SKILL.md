---
id: lsc-what-to-measure
aliases: [lsc-what-to-measure]
name: "LSC 28 — What to Measure Canvas"
category: business-design
description: Run the Lean Service Creation "What to Measure" canvas — define value-proposition metrics, service metrics and business metrics for the MVP so each ties to the problem worth solving, the engagement cycle, and the original business objective.
triggers: [what to measure, LSC metrics, value proposition metrics, service metrics, business metrics, MVP metrics, which KPIs for the new service, measure the MLP, net promoter score for a new service, define metrics before launch]
tags: [lean-service-creation, lsc, canvas, metrics, kpi, mvp]
related: ["[[lean-service-creation]]", "[[lsc-minimum-lovable-product]]", "[[lsc-customer-engagement]]", "[[lsc-business-objective-context]]", "[[lsc-success-is-a-process]]", "[[lsc-growth-hacking]]", "[[kpi-architect]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 28 — What to Measure

## Contract
- **Input:** `canvases/05-…` (problem worth solving), `11-…` (engagement stages), `16-…` (MLP), `01-…` (business goals).
- **Output:** `canvases/28-what-to-measure.md`: three metric blocks, each with definition, source, baseline, target, review cadence, and the decision it informs.
- **Allowed tools/artifacts:** analytics tools the project has, surveys and interview plans, `kpi-architect` for a fuller KPI tree.
- **Done when:** each of the three blocks has at least one metric that is measurable at the MVP stage, has an instrument in place or planned in 27, and connects to a decision.

## Source and scope
From the Handbook 2.0 (Futurice, 2018). Not in the 23-page PDF. The book says it can be used at the very beginning or at the end of the build set-up: the point is to define the metrics, giving clarity and focus. Fields: **Value proposition metrics** · **Service metrics** · **Business metrics**.

## Core Blueprint
1. **Value proposition metrics.** Restate the problem worth solving. Choose what shows that the value proposition is understood, speaks to customers, and ideally is accepted or bought: for example recommendation score, a weekly survey, regular interviews with a handful of customers, share of trials that become paid use. Behaviour and commitment beat opinion (`business-experiment-design`).
2. **Service metrics.** Look at 11 and 16: what is the most important element of the service at this stage and how is it measured? Examples from the book: awareness and clicks on ads, downloads, purchase decisions, use of a built recommendation tool. Pick the metric for the weakest transition in the engagement cycle.
3. **Business metrics.** Return to the 01 goals: revenue, profit, cost, new customers, margin of the core service. Choose what tells you the business objective is being met in this phase, consistent with 26.
4. **For each metric write** name, exact definition, data source, baseline, target and date, owner, cadence, and the decision a change in it would trigger.
5. **Vanity check.** Drop any metric that cannot change a decision or tie to money (persona rule).
6. **Instrument.** Add the set-up work (events, surveys, dashboards) to 27 so data exists at launch.
7. **Review** in 19 and 26; revise per phase.

## Quality tests
- Three blocks filled; each metric has definition, source, baseline, target.
- Every metric has the decision it informs.
- No metric without an instrument or a task to create one.
- Value proposition metrics include at least one behaviour or commitment measure.

## Agent-augmented variant
An agent can propose a metric tree and instrumentation tasks and compute baselines from exports (`[S]` for proposals, `[O]` for computed numbers with the formula shown).

## Gotchas
- **Vanity metrics** (downloads without use). The book's modern-company theme.
- **Revenue only at MVP stage.** See 26.
- **Metrics without owners** are never read.

## Hand-offs
Phase criteria: `lsc-success-is-a-process` (26). After launch: `lsc-growth-hacking` (29).
