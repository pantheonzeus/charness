---
id: lsc-success-is-a-process
aliases: [lsc-success-is-a-process]
name: "LSC 26 — Success Is a Process Canvas (Management Track)"
category: business-design
description: Run the Lean Service Creation "Success is a Process" canvas — phase-specific success criteria, weekly current status, learnings and assumptions, and actions — so management does not judge an early release by revenue alone and the metrics change as the service matures.
triggers: [success is a process, LSC success criteria, phase specific metrics, stage gate metrics for a new service, management metrics for an MVP, why is the MVP not making revenue, metrics per phase, management dashboard for lean, steering group canvas, current status against criteria]
tags: [lean-service-creation, lsc, canvas, management-track, metrics, governance]
related: ["[[lean-service-creation]]", "[[lsc-strategic-business-objectives]]", "[[lsc-what-to-measure]]", "[[lsc-weekly-board]]", "[[kpi-architect]]", "[[business-experiment-design]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 26 — Success Is a Process (Management Track)

## Contract
- **Input:** `canvases/01-…` success goals, the phase plan of the project, stakeholders.
- **Output:** `canvases/26-success-is-a-process.md`: a table of phases × (criteria for success, current status, learnings and assumptions, actions), refreshed weekly in the current phase's column only.
- **Allowed tools/artifacts:** workshop with the relevant stakeholders, metrics from analytics and experiments, `kpi-architect` for metric design.
- **Done when:** the current and next phase have criteria with a metric, threshold and reason; the current status cites data; and the steering group has agreed that the criteria differ per phase.

## Source and scope
From the Handbook 2.0 (Futurice, 2018), Management Track. The book's problem statement: when the MVP is out, management looks at revenue and declares failure; the service is never finished with version one and its key metrics change over its life. Fields: **Criteria for success** · **Current status** · **Learnings and assumptions** · **Actions**, per phase.

## Core Blueprint
1. **Fill with the relevant stakeholders** in one session, including whoever will judge the project.
2. **List the phases** the service will pass through (e.g. concept validation, MLP pilot, early adoption, scale). In an environment that does not accept iteration, fill only the current and next phase (the book's advice).
3. **Criteria per phase.** For each: what we are aiming at, the best metric to guide the work, why this metric, how it differs from the next phase. Examples of the shift: early phases measure learning (validated assumptions, interview-to-pilot conversion); later phases measure adoption, retention, unit economics. **[house]**
4. **Weekly status.** Fill only the current phase column: where we are against the criteria, with numbers and dates.
5. **Learnings and assumptions.** What the metrics tell us; what changed in our beliefs. Link hypothesis ids from 21.
6. **Actions.** Concrete decisions made because of the learnings, with owner and date.
7. **Redo as the project advances.** When a phase gate passes, rewrite the next phase's criteria with what you learned.
8. **Guard against vanity metrics.** Each metric must connect to a decision or money (persona rule).

## Quality tests
- Criteria have metric, threshold, reason, and differ between phases.
- Status shows data with date, not adjectives.
- Every action has owner and date.
- Management has explicitly agreed that the first release is judged on the phase-1 criteria.

## Agent-augmented variant
An agent can draft the weekly status from analytics and the experiment register (`[S]`) and flag when a metric is a vanity metric. Thresholds and phase gates are set by people.

## Gotchas
- **Revenue as the only yardstick for an MVP.** The failure the book calls out.
- **Moving thresholds after seeing numbers.** Log changes with reason.
- **Filling all columns every week.** One column at a time.

## Hand-offs
Metrics detail: `lsc-what-to-measure` (28). Weekly use: `lsc-weekly-board` (19). Phase gates: `lsc-validation` (15).
