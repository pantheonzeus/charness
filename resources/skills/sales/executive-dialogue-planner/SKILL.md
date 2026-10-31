---
id: executive-dialogue-planner
aliases: [executive-dialogue-planner]
name: "Executive Dialogue Planner (Business Value Proposition & Role-Play Prep)"
category: sales
description: Turn a prepped company/insight into a 4-quadrant Business Value Proposition answering the four executive questions, then a dialogue plan (objective, emotional shift, objection handling, hook, pitch, message) — a role-play-ready script for a short executive conversation.
triggers: [dialogue plan, business value proposition, prep for an executive conversation, role play this pitch, what's my hook, emotional shift, objection handling for this pitch, prep the exec meeting, executive dialogue, dialogue planning template]
tags: [sales, executive-meeting-prep, pitch-structure, objection-handling, role-play]
related: ["[[company-challenger-brief]]", "[[audience-of-one-report]]", "[[account-priority-map]]", "[[proposal-challenger]]"]
status: active
version: 1
created: 2026-07-26
updated: 2026-07-26
---

# Executive Dialogue Planner (Business Value Proposition & Role-Play Prep)

**Contract**
- **Input:** an upcoming short (5–10 min) conversation or meeting with a named executive, plus whatever prep already exists — a `[[company-challenger-brief]]`, an `[[account-priority-map]]`, an `[[audience-of-one-report]]`, or just a proposition the user believes will land.
- **Output:** a markdown dialogue plan saved to `output/YYYYMMDD-<Company>-<Exec>-dialogue-plan.md` — the 4-quadrant Business Value Proposition, the Design-Funnel dialogue plan (Objective / Emotional Shift / Thoughts & Objections / Hook / Pitch / Message), and a role-play opening script.
- **Allowed tools/artifacts:** reuses existing research/briefs; only fetches new public sources if no prior brief exists for this account.
- **Done when:** all four Business Value Proposition quadrants are filled with account-specific content (no generic placeholder answers), the dialogue plan names a single measurable objective and a named emotional shift (from-state → to-state), and a role-play opening (hook + first 60 seconds) is drafted verbatim.

**Triggers/Context**
- A pitch, proposal walkthrough, or discovery meeting with a named executive is imminent and the user wants to structure *what to say*, not just *what to know* — downstream of the research skills (`company-challenger-brief`, `account-priority-map`, `audience-of-one-report`), which build the insight this skill turns into a spoken plan.
- Explicit ask: "help me prep for this exec conversation," "what's my hook," "build the dialogue plan," "role-play this."

**Core Blueprint**
1. **Pull in existing prep first.** Ask for or locate the relevant `company-challenger-brief` / `account-priority-map` / `audience-of-one-report` output for this account and executive. Don't re-research if it exists — this skill structures a conversation from research that's already been done.
2. **Set the Objective.** One sentence: the single action you want this executive to take as a direct result of the meeting (not "have a good conversation" — a next step: approve a pilot, introduce you to X, agree to a follow-up with finance).
3. **Build the 4-quadrant Business Value Proposition**, each quadrant answering one of the deck's four executive questions with account-specific content (generic answers defeat the point of the exercise):
   - **The Business Problem/Opportunity** — answers *"Do you understand my business and what I need to achieve?"* Pull directly from the account-priority-map's gaps/opportunities if available.
   - **Our Proposition vs others** — answers *"Can you help me? What are you able to do for me?"* — the solution, how it fits their existing tech/skills, and how it differs from likely alternatives.
   - **Our Experience** — answers *"Why should I choose you? Can I trust you to deliver?"* — relevant reference cases, sector experience, and whether they're independently checkable. Never invent a reference case that doesn't exist.
   - **The Case for Change** — answers *"Can you help me build a business case? Are you a true partner?"* — internal approval hurdles, likely sponsor, tangible/intangible benefits and how they'd be measured, and what an ongoing partnership (not a one-off engagement) would look like.
4. **Map the Emotional Shift.** Name the executive's likely starting emotional state (e.g. skeptical, overloaded, cautious) and the state you need them in to take the Objective's action (e.g. confident, energized, reassured) — one sentence each, plus the 1–2 moves in the conversation that create the shift.
5. **Draft Thoughts & Objection Handling.** What does the executive need to be thinking, after the meeting, to take the action? List the 3–5 most likely objections and a one-line response to each — grounded in the Business Value Proposition quadrants, not generic sales rebuttals.
6. **Write the Hook.** One memorable opening line or question — "what if…" framing preferred — that earns attention in the first 15 seconds. Test it against the account-priority-map's opportunity line; a hook disconnected from a real, sourced gap is a gimmick.
7. **Draft the Pitch and the Message.** Pitch = the value proposition delivered as a short narrative (problem → your read → what you'd do → outcome), citing a real story/case where possible. Message = the one sentence that should be "ringing in their ears" when they leave — the "so, given…" close.
8. **Assemble the role-play opening.** Write out, verbatim, the Hook + first ~60 seconds of the Pitch as spoken words — this is what actually gets rehearsed, not just an outline.

**Optimizations/Gotchas**
- **This is a script, not a slide deck.** Keep every section in language you'd actually say out loud — a value proposition that only reads as a bullet list has failed the exercise.
- **Don't invent reference cases or experience.** The "Experience" quadrant is a Soul.md never-oversell line in miniature — if there's no genuinely comparable case, say the honest sector-adjacent equivalent instead of manufacturing false familiarity.
- **One objective, not three.** A dialogue plan chasing multiple outcomes dilutes the hook and the close — force a single next action; if the user names several, ask which one this specific conversation should drive.
- **Reuse the emotional-shift map even for a written pitch** (proposal, email) — the deck's insight (the audience needs to *think* something specific before they'll *act*) generalizes past live meetings.
- **Short meetings need a shorter hook, not a shorter proposition.** For a 5–10 min slot, the Hook + Pitch opening is what gets rehearsed; the full 4-quadrant proposition is reference material for objection handling, not something to recite in order.

**After the plan**
Offer the natural next step: "Want me to run this as a role-play — I'll play the executive and push back on the objections we listed?"

**Feedback & Skill Verification**
- Would you like to provide feedback to optimize this workflow or execution?
- Should we update this skill (or add a new one) based on how this went?
