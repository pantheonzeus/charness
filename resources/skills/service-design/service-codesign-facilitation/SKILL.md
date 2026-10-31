---
id: service-codesign-facilitation
aliases: [service-codesign-facilitation]
name: "Co-Design Facilitation — Workshops That End in Decisions"
category: service-design
description: Designs and runs co-design sessions with customers, frontline staff and decision-makers. Each session has one named decision and one artifact, the right participants (including those who do the work), pre-work, a timeboxed agenda with methods, a decision protocol that handles power dynamics, and a decision log written within 24 hours.
triggers: [workshop, co-design, co-creation, design sprint, facilitation, facilitate a session, stakeholder workshop, journey mapping workshop, blueprint workshop, ideation workshop, alignment workshop, workshop agenda, kick-off workshop, prioritisation workshop]
tags: [service-design, facilitation, co-design, workshops, alignment]
related: ["[[service-design-engagement]]", "[[service-concept-prototyping]]", "[[stakeholder-alignment]]", "[[contact-meeting-capture]]"]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
vault_writes: ["cbrain/Clients/*", "cbrain/notes/[0-9]*", "cbrain/projects/*", "cbrain/daily reports/*"]
---

# Co-Design Facilitation — Workshops That End in Decisions

## Contract
- **Input:** the purpose of the session(s), the participants available, the time available, and the inputs (research, maps, blueprints).
- **Output:** `output/<YYYYMMDD>-<slug>-workshop-plan.md` (session design: decision, participants, pre-work, agenda, methods, materials, decision protocol), and after the session `output/<YYYYMMDD>-<slug>-workshop-outcomes.md` (decisions, actions with owners and dates, open questions, artifacts).
- **Allowed tools/artifacts:** conversation, prior deliverables, the vault for participant context, the calendar/mail connectors to draft invites (drafts only; never sent without approval).
- **Done when:** every session names its decision and its artifact; the participant list includes someone who does the work being redesigned; the decision protocol is stated before the session; outcomes are written within 24 hours, with every action carrying an owner and a date.

## Operating principles (enforceable)
1. **One decision per session.** "Align on the future state" is not a decision. "Choose 2 of 5 concepts to prototype" is. If a session has no decision, it's a briefing. Send an email instead.
2. **The people who do the work are in the room.** Frontline and backstage staff, and customers where possible. A redesign signed off only by managers fails on contact with the operation.
3. **Diverge alone, converge together.** Individual silent writing before group discussion. This neutralises the HiPPO (the highest-paid person's opinion) and the loudest voice.
4. **The decision protocol is announced up front.** Dot vote + owner decides, consent ("any reasoned objection?"), or sponsor decides after hearing the room. Pick one and say it before the session starts.
5. **Workshops are paid for with outputs.** The outcomes file is due within 24 hours, or the session's value decays.

## Core Blueprint
1. **Purpose → decision → artifact.** Write one line each.
2. **Participants.** Up to 8–12 per breakout. Map them by role (decider / doer / customer / expert / blocker) and invite at least one doer. Check the vault for each stakeholder's context and history.
3. **Pre-work.** Send a 1-page pre-read and one question each participant answers in writing beforehand. Facilitation starts before the session.
4. **Agenda.** Open (purpose, decision, protocol, 10%) → ground in evidence (research/maps, 15–20%) → diverge (silent individual work, 20–25%) → cluster and discuss (20%) → converge and decide (15–20%) → commit (actions and owners, 10%). Timebox every block.
5. **Methods by purpose.** Journey or blueprint walk-through (validate), "How might we" + crazy 8s (ideate), 2×2 impact/effort (prioritise), concept speed-dating (choose), pre-mortem (de-risk), role-play (test operability).
6. **Run.** Facilitator, note-taker and timekeeper are separate roles. Park off-topic items visibly. Record decisions verbatim as they're made.
7. **Outcomes.** Within 24 hours: decisions, actions (owner, date), parked items with a destination, and photos/exports of the artifacts. Wire stakeholders into the vault per `contact-meeting-capture` and Charter §6.
8. **Exec pre-wire.** If the session needs a senior decision, pre-wire it via `stakeholder-alignment`. Never surprise a decider in the room.

## Remote / hybrid
- Shorten to 2–3 hours per session, with breaks every 50 minutes.
- Share one board; prepare the frames before the session.
- Remote participants contribute first in each round, so the room doesn't dominate.

## Optimizations/Gotchas
- **Sticky-note theatre.** Lots of output, no decision. The fix is principle 1.
- **Works councils (DE/AT/NL).** Workshops that redesign staff roles or monitoring can trigger co-determination rights. Check before the session, not after.
- **AI as a participant.** An LLM may generate the long list of ideas or a pre-mortem. Present its output as "machine prompts", after the humans have contributed, so it doesn't anchor the room.
