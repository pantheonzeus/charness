---
id: lsc-weekly-board
aliases: [lsc-weekly-board]
name: "LSC 19 — Weekly LSC Board"
category: business-design
description: "Run the Lean Service Creation \"Weekly LSC Board\" — the weekly rhythm for the build phase: most critical technical, business and end-user issue, the week's biggest fear, what the work validates, last and next retro / user test / demo / shared goals, and a stakeholder-visibility score trend."
triggers: [weekly LSC board, weekly board, weekly build ritual, most critical issue this week, week's validation, biggest fear this week, next demo and user test, stakeholder visibility, build phase momentum, keep up momentum, weekly status for the team]
tags: [lean-service-creation, lsc, canvas, weekly, build-phase, visibility]
related: ["[[lean-service-creation]]", "[[lsc-team-weekly]]", "[[lsc-agile-board]]", "[[lsc-experimenting]]", "[[lsc-retrospective]]", "[[kpi-architect]]"]
modules: [file-backed-state]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 19 — Weekly LSC Board

## Contract
- **Input:** last week's board, `canvases/20-agile-board.md`, `canvases/21-experimenting.md`, `canvases/18-team-weekly.md`.
- **Output:** one appended section per week in `canvases/19-weekly-board.md` (never overwrite past weeks), plus a visibility score series.
- **Allowed tools/artifacts:** the team's weekly meeting, board files, stakeholder feedback.
- **Done when:** the week's section has all fields, the "validated" field names a specific hypothesis id and a result, next-week events have dates, and the visibility score is justified.

## Canvas (v3.0.5) — "Keeping up momentum through the build phase"
**Right now what's the most critical:** Technical issue · Business issue · End user issue. **Week's biggest:** Fear/Limitation. **Week's validation:** *What is validated by the work we are now doing?* Table **Last / Next** for **RETRO · USER TEST · DEMO · TIME TEAM SHARED PERSONAL GOALS**. Chart: **How well are we making our work visible to the relevant stakeholders?** EXEMPLARY ↔ NEED TO DO BETTER, by **WEEK**.

## Core Blueprint
1. **Reopen last week's section** by path; note what was promised.
2. **Critical triple.** One issue per lens (technical, business, end user), each with owner and "unblocked by" date. If a lens has none, write "none, checked <how>".
3. **Biggest fear or limitation.** One sentence from the team, named by the person who holds it. Fears are surfaced, not solved on the spot.
4. **Week's validation.** Link to a hypothesis in 21: what the work done this week will prove or disprove, and when you will read the result. If the answer is "nothing", rethink the week.
5. **Rhythm table.** Fill Last and Next for retro, user test, demo and the time the team shares for personal goals. Next entries have dates. No user test in the last three weeks is a flag.
6. **Visibility score** (1–5, your honest rating of how well stakeholders see the work). Write what was shown, to whom, and by which channel. A falling score triggers a demo or update this week.
7. **Close the loop.** Items not resolved roll over visibly; a fear or issue present three weeks in a row escalates to the sponsor.

## Quality tests
- Each lens has an issue or a verified "none".
- Validation field names a hypothesis id.
- Next retro, user test, demo have dates.
- Visibility score has a stated basis.
- Previous week's open items are carried or closed explicitly.

## Agent-augmented variant
An agent can prepare the draft board from the agile board, commit logs and experiment data (`[S]`) for the team to correct. It cannot fill the "fear" field; that is human. Weekly sections are appended; the file is the state of record.

## Handbook 2.0 guidance (book, Futurice 2018, paraphrased)
Handbook guidance:
- Keep it short and standing. Keep the dialogue open with business owners.
- Business question: think like a venture capitalist. Would you bet your grandmother's savings on the project?
- End-user issue: biggest fear about need, usability and value proposition.
- If you stand in the weekly with nothing to validate, you are doing something wrong; check for hidden assumptions about users.
- Transparency: others see you spending money and changing direction; share what you do and why, with validated justification, at regular intervals.
- You are never too busy for a retro. Postponing user tests risks cementing features without user value. Demos create deadlines and trust. Personal goal sharing helps others support your growth.

## Gotchas
- **Status theatre.** The board exists to decide the week, not to report.
- **Fear skipped.** The one field teams skip is usually the most useful.
- **Invisible work.** Stakeholders who learn at the end will reject at the end.

## Hand-offs
Updates feed `lsc-agile-board` (20), `lsc-experimenting` (21) and `lsc-retrospective` (22).
