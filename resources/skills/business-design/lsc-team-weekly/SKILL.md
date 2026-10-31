---
id: lsc-team-weekly
aliases: [lsc-team-weekly]
name: "LSC 18 — Weekly :) Team Capacity & Wellbeing Canvas"
category: business-design
description: Run the Lean Service Creation "Weekly :)" canvas — a four-week view per team member with holidays, used to plan capacity and keep the team happy and motivated through the build phase.
triggers: [weekly team canvas, LSC weekly smiley, team capacity plan, four week plan per person, holidays and availability, team happiness check, team is all you've got, who is available when, build phase staffing, team wellbeing canvas]
tags: [lean-service-creation, lsc, canvas, team, capacity, wellbeing]
related: ["[[lean-service-creation]]", "[[lsc-weekly-board]]", "[[lsc-agile-board]]", "[[lsc-minimum-lovable-product]]", "[[lsc-retrospective]]"]
modules: [file-backed-state]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 18 — Weekly :)

## Contract
- **Input:** team list, role and availability, the MLP scope (16), planned events (demos, user tests).
- **Output:** `canvases/18-team-weekly.md`: a rolling four-week table (name · week 1–4 · holidays) with allocation and a mood note, refreshed weekly.
- **Allowed tools/artifacts:** calendars (read-only, only with user consent), team conversation.
- **Done when:** every person has an allocation and a holiday entry for all four weeks, total allocation is checked against the MLP scope, and anyone above 100% or flagged low-mood has an action.

## Canvas (v3.0.5) — "The team is all you've got. Make sure they're happy and motivated!"
Table: **NAME** · **WEEK 1** · **WEEK 2** · **WEEK 3** · **WEEK 4** · **HOLIDAYS**.

## Core Blueprint
1. **List the team**, including part-time and external people, with role and capacity (days per week).
2. **Fill holidays first,** then public holidays and known absences.
3. **Allocate each person per week:** focus (what they work on, linked to 20 stories), percentage, and personal learning goal if any. **[house]**
4. **Add a mood marker per person per week** (self-reported: 🙂 / 😐 / 🙁) and, if not 🙂, one sentence on what would help. Self-report only; no inference by the agent.
5. **Check capacity against scope.** Sum available days versus estimated effort for Musts in 16. If short, reduce scope or add people before the sprint starts, not during.
6. **Rotate the view weekly:** drop the past week, add the next.
7. **Raise items** into 22 (retro) when a pattern repeats.

## Quality tests
- Four weeks filled for every member; holidays explicit.
- No one above 100% without a named reason and an end date.
- Mood markers are self-reported and dated.
- Capacity compared to 16 scope with the result stated.

## Agent-augmented variant
An agent can compute capacity sums and flag conflicts from a calendar the user explicitly allows it to read. It does not score people or guess mood. Personnel data stays out of any shareable deliverable and out of public repos.

## Handbook 2.0 guidance (book, Futurice 2018, paraphrased)
Handbook "Weekly :)" guidance:
- Each person draws a smiley on a sticky note per week and says how they are and why. Stay on moods and reasons, not on the to-do list. Share both private and professional context, and respond with support where it helps.
- A single sleepless night is fine; several in a row is an alarm.
- Photograph new teammates if they agree. Holidays go on the canvas so absences are planned.

## Gotchas
- **Hours without humans.** Wellbeing signals are inputs to the plan, not a nice-to-have.
- **Hidden second jobs.** Team members in shared projects: record actual availability, not nominal.
- **Personal data.** Mood and absences are sensitive; keep the file local and confined to the team.

## Hand-offs
Feeds `lsc-weekly-board` (19) "time team shared personal goals" and `lsc-agile-board` (20) capacity.
