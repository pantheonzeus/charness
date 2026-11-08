---
id: lsc-mvp-backlog
aliases: [lsc-mvp-backlog]
name: "LSC 27 — MVP Backlog Canvas"
category: business-design
description: Run the Lean Service Creation "MVP Backlog" canvas — transfer the burning technical issue, business question and end-user verification from the experiment board, then list every action needed to get the MVP out (not only tech tasks) as an owned, limited-WIP backlog.
triggers: [MVP backlog, LSC MVP backlog, from planning to executing, first backlog, actions to launch the MVP, technical issue business question end user verification, antidote for endless planning, launch checklist for the first version, who does what for the MVP]
tags: [lean-service-creation, lsc, canvas, mvp, backlog, execution]
related: ["[[lean-service-creation]]", "[[lsc-minimum-lovable-product]]", "[[lsc-experimenting]]", "[[lsc-agile-board]]", "[[lsc-weekly-board]]"]
modules: [file-backed-state]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 27 — MVP Backlog

## Contract
- **Input:** `canvases/21-experimenting.md` (assumptions), `canvases/16-minimum-lovable-product.md` (scope), team capacity (18).
- **Output:** `canvases/27-mvp-backlog.md`: the three transferred issues and the backlog table (task · owner · status To do / In progress / Done).
- **Allowed tools/artifacts:** team session; the team's tracker if one exists (mirror it, do not duplicate).
- **Done when:** the three top issues are copied from the experiment board with their hypothesis ids, every MLP Must and every non-technical launch action has an owned task, and WIP limits are written.

## Source and scope
From the Handbook 2.0 (Futurice, 2018), "Defining and building the MVP". Not in the 23-page PDF. The book calls it the antidote for endless planning and stresses it is **not** a technical backlog: it lists all required actions, including asking for budget and contacting partners. Fields: **Technical issue?** · **Business question?** · **End user verification?** · **The backlog** (To do with owner name, In progress, Done).

## Core Blueprint
1. **Transfer the technical issue:** the most burning technical assumption on the experiment board, the one that is both important and likely trickiest. Cite the H-id.
2. **Transfer the business question:** the most burning business assumption (funding, willingness to pay, competitor move). Cite the H-id.
3. **End-user verification:** do we have the right segment first, is the value proposition validated enough, are we speaking the customer's language? State the open check and who does it.
4. **Build the list** from three sources: each Must in 16; each experiment needed to settle the three issues above; each non-technical enabler (budget approval, partner contact, legal review, support set-up, data-protection check).
5. **Assign an owner per task** and put the name in To do. Move to In progress only when work starts and to Done when finished.
6. **Limit WIP per person** (the book: a limit is good practice; the Agile board canvas says max two per person). Keep one backlog; when it outgrows the canvas, move to the team's tracker.
7. **Review weekly** in 19. A task idle for a week gets a blocker note or is removed.

## Quality tests
- Three transferred issues carry hypothesis ids.
- At least one non-technical action in the list.
- Every task has an owner and a size small enough to finish in days.
- WIP limit stated.

## Agent-augmented variant
An agent can draft tasks from 16 and 21 and flag Musts without tasks (`[S]`). It does not assign owners or mark tasks done.

## Gotchas
- **Tech-only backlog.** Launches fail on missing approvals and partners as often as on code.
- **Backlog as wish list.** The point is that it is followed and things get done.
- **Duplicate tracking.** Two boards, two truths.

## Hand-offs
Day-to-day work: `lsc-agile-board` (20). Measurement set-up: `lsc-what-to-measure` (28).
