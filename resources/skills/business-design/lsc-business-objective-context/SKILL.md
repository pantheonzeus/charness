---
id: lsc-business-objective-context
aliases: [lsc-business-objective-context]
name: "LSC 01 — Business Objective and Context Canvas"
category: business-design
description: Run the Lean Service Creation "Business Objective and Context" canvas with the sponsor — stakeholders, success goals, business objective, ambition level, strategic purpose, social/environmental impact, risks and restrictions — so every later canvas has a funded, measurable why.
triggers: [business objective and context, LSC business objective, project context canvas, sponsor alignment canvas, why are we doing this, strategic purpose, option big bet no-regret, how far are we aiming, success goals for the project, kickoff canvas, LSC kickoff]
tags: [lean-service-creation, lsc, canvas, framing, sponsor, kickoff]
related: ["[[lean-service-creation]]", "[[opportunity-framing]]", "[[lsc-immersion]]", "[[lsc-pitch-creator]]", "[[kpi-architect]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
vault_writes: ["cbrain/Clients/*"]
---

# LSC 01 — Business Objective and Context

## Contract
- **Input:** the sponsor (the person funding the project), a brief or idea, any strategy documents. Conventions: [lsc-conventions](../lean-service-creation/references/lsc-conventions.md).
- **Output:** `canvases/01-business-objective-context.md` with the seven fields below, plus a one-line sponsor sign-off record.
- **Allowed tools/artifacts:** conversation with the sponsor, strategy docs, vault notes on people and company, web search for public strategy statements.
- **Done when:** all seven fields pass the Quality tests, the sponsor has seen and accepted the file (name and date recorded), and the kill/pivot criteria derived from the risks are written.

## Canvas (v3.0.5) — "Create this together with the person funding this project."
Centre, top to bottom: **What is our business objective?** (impact we aim to create; business challenge to solve) · **How far are we aiming?** (incremental, breakthrough, or disrupting the market; when a viable business is expected) · **What is our strategic purpose?** (an option to invest in if need be, the big bet that changes the company, or a no-regret move)
Around it: **Who needs to be involved?** (stakeholders, people from parallel or related projects) · **How will we know that we've succeeded?** (after a month, a year; concrete goals) · **Social & environmental impact** (positive impacts to boost, negative to reduce, based on strategy, mission and values) · **Risks, restrictions and things we need to take into account** (budget, schedule, organization, legal, current business). Callout: **ASK WHY.**

## Core Blueprint
1. **Name the sponsor.** One person with budget authority. No sponsor: stop and record "no funded objective" as the run's first gate failure.
2. **Objective, with five whys.** Write the sponsor's first statement, ask "why does that matter?" up to five times until the answer is a business consequence (revenue, cost, risk, position). Write the last answer as the objective.
3. **Success goals.** Convert each goal to metric · baseline · target · date · data source. Two horizons: one month, one year (the canvas's own prompts).
4. **How far.** Choose exactly one of incremental / breakthrough / disruptive and write the date by which a viable business is expected.
5. **Strategic purpose.** Choose exactly one of option / big bet / no-regret. Run the consistency check: a no-regret move with a disruptive ambition and a large budget contradicts itself. Resolve with the sponsor.
6. **Stakeholders.** List people with role and what they need from the project. Harvest the vault first (Charter §6) and link or create person notes.
7. **Impact.** Name up to three positive and three negative effects on society and environment that this kind of service could cause, tied to the company's stated mission or values. Quantify later in 10 and 14.
8. **Risks and restrictions.** Cover all five prompt areas (budget, schedule, organization, legal, current business). For each, record the point at which it would make us stop: a **kill trigger**. **[house]**
9. **Sign-off.** Show the sponsor the file. Record name and date. Unsigned = `status: draft`.

## Quality tests
- Objective names a business consequence, not a feature or technology.
- Every success goal has a number, a date and a data source.
- Exactly one ambition level and one strategic purpose, consistent with budget and timeline.
- At least one stakeholder from an adjacent or parallel project, or an explicit "none found, searched <where>".
- Risks cover all five areas; each has a kill trigger.
- Sponsor sign-off recorded.

## Agent-augmented variant
An agent may pre-read strategy documents and draft a strawman marked `[S]` for the sponsor to correct. It may not decide ambition or purpose. Public company strategy statements go into `EVIDENCE.md` as `[O]` with URL and date.

## Handbook 2.0 guidance (book, Futurice 2018, paraphrased)
- Create it together with the manager who came up with the need. A good objective can be solved in many ways and implies no solution.
- Ask "based on what facts?" Facts over opinions, to give team and management common ground. The handbook version also asks **What enables us?** (existing user pool, infrastructure, unique data or know-how). Add it as a field.
- Success: picture one year from now, then one month from now for the process. Ask whether the boss agrees.
- Strategic options come from `lsc-strategic-business-objectives` (25) and `lsc-trends` (24) when the project starts from management.

## Gotchas
- **Sponsor absent:** the most common failure. A canvas filled by the team alone is a hypothesis list, not an objective.
- **Objective written as a solution** ("build an app for…"). Re-ask why.
- **Vanity goals** ("increase engagement"). Tie to money or a decision.
- **Purpose drift:** re-read this canvas at gates 07, 14 and 17; if the sponsor's answer changed, update and log it.

## Hand-offs
Next: `lsc-immersion` (02). Gate 14 and Pitch (17) read this canvas for strategy fit and the "Why".
