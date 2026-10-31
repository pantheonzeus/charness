---
id: lsc-growth-hacking
aliases: [lsc-growth-hacking]
name: "LSC 29 — Growth Hacking Canvas"
category: business-design
description: Run the Lean Service Creation "Growth Hacking" canvas after launch — visualise the analytics funnel with conversion and volumes, find the reasons behind drop-offs, pick the single most critical blocker, and turn the fix into a measured experiment.
triggers: [growth hacking canvas, LSC growth hacking, conversion funnel, why are we losing users, most critical blocker, post launch iteration, grow it huge, analytics funnel review, funnel conversion experiment, build measure learn after launch]
tags: [lean-service-creation, lsc, canvas, growth, analytics, post-launch]
related: ["[[lean-service-creation]]", "[[lsc-what-to-measure]]", "[[lsc-customer-engagement]]", "[[lsc-experimenting]]", "[[lsc-immersion]]", "[[business-experiment-design]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 29 — Growth Hacking

## Contract
- **Input:** live analytics, the 11 engagement stages, the 28 metrics, user research channels.
- **Output:** `canvases/29-growth-hacking.md`: one dated section per release cycle with the funnel (A), the why (B), the chosen blocker and the experiment (C), appended, never overwritten.
- **Allowed tools/artifacts:** analytics exports, session recordings, user tests and interviews, `business-experiment-design`.
- **Done when:** the funnel shows percentages and absolute volumes per step, each large drop has a researched reason or a plan to research it, one blocker is chosen with an experiment and success criterion set before the change, and the previous cycle's result is recorded.

## Source and scope
From the Handbook 2.0 (Futurice, 2018), "Growing it huge". Not in the 23-page PDF. The book's frame: once live there is hard data, and the same Build, Measure, Learn workflow continues; if a change does not have the desired effect, roll back to the previous version; the frequency of use follows the release cycle. Parts: **A. Visualize your analytics** · **B. The why** · **C. Most critical blocker right now**.

## Core Blueprint
1. **Draw the funnel (A).** Use the stages of 11 (awareness through advocate) or the product's own events. For each step write the conversion percentage, the absolute number of users or usage, and the goal if one exists. Make the picture visible to stakeholders to build trust.
2. **Find the why (B).** Analytics show where users leave, not why. For each large drop plan research: user tests, interviews, recordings. Do not guess the reason.
3. **Choose the most critical blocker (C).** Prefer the earliest step where the funnel breaks badly. The book's example: if registration is broken, more marketing only produces many disappointed customers. Work upstream-to-downstream by cost of the leak. **[house]**
4. **Write the experiment:** change, hypothesis, metric, threshold, sample, duration. Success criterion before release.
5. **Release, measure, decide:** keep, adjust, or roll back. Record the result and what was learned.
6. **Repeat** per release cycle; carry open "why" questions forward.
7. **Link to economics.** Re-check unit economics in 12 when funnel numbers replace guesses; update the viability model.

## Quality tests
- Funnel has both rates and absolute volumes with dates.
- Every big drop has a reason backed by research or an open research task.
- One blocker per cycle, with a pre-set criterion.
- Rollback condition stated.

## Agent-augmented variant
An agent can compute funnel numbers from exports, cluster qualitative feedback, and draft experiment plans (`[S]` for interpretation). Causal claims from a single experiment need the sample size and the criterion that was set in advance.

## Gotchas
- **Spending on acquisition into a leaking funnel.**
- **Reading noise as signal** from small samples; state n.
- **Skipping the why.** Analytics alone propose fixes to the wrong problem.

## Hand-offs
Results update `lsc-what-to-measure` (28) and `lsc-success-is-a-process` (26). Larger feature changes: run the relevant Service Vision Sprint canvases again (book guidance) via `lean-service-creation`.
