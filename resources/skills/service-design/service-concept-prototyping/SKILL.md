---
id: service-concept-prototyping
aliases: [service-concept-prototyping]
name: "Service Concept & Prototyping — Concepts, Prototype Ladder & Pilots"
category: service-design
description: Turns ranked opportunities into 2–3 distinct service concepts, then tests them up a prototype ladder. The ladder runs from desirability (storyboards, concierge, Wizard of Oz) through usability to operability (role-play, bodystorming, live single-site pilot). Every test has pass/fail criteria written before it runs, and every pilot has a stop rule. For agent concepts, Wizard of Oz comes before any build, and its transcripts become the seed eval set.
triggers: [service concept, concept development, ideation, service prototype, prototyping a service, wizard of oz, concierge test, storyboard, bodystorming, role play service, desktop walkthrough, pilot design, service pilot, test the new service, MVP service, prototype an AI agent]
tags: [service-design, prototyping, concepts, pilot, iteration]
related: ["[[service-discovery-research]]", "[[service-codesign-facilitation]]", "[[agentic-service-evaluation]]", "[[assumption-audit]]", "[[service-performance-measurement]]", "[[business-experiment-design]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
---

# Service Concept & Prototyping — Concepts, Prototype Ladder & Pilots

## Contract
- **Input:** ranked opportunity areas (from research or journey work), constraints, and access to users and staff for testing.
- **Output:** `output/<YYYYMMDD>-<slug>-concepts-and-tests.md` containing concept cards, the riskiest-assumption list per concept, the test plan with pre-registered criteria, results, and (when ready) the pilot design.
- **Allowed tools/artifacts:** conversation, research outputs, low-fi prototype material (Markdown storyboards, scripts, mock screens), and for agent concepts a prompt-based mock run by a human operator.
- **Done when:** ≥2 concepts that differ in mechanism (not just UI) were considered; each test had pass/fail criteria written **before** it ran; each concept has a verdict (advance / iterate / kill) with evidence; any pilot has scope, duration, comparison, metrics and a stop rule.

## Boundary
This skill tests **desirability, usability and operability**: will people use it, can they, and can the organisation deliver it. Testing whether the business model is viable (pricing, willingness to pay, unit economics) belongs in `business-design` experiment design.

## Operating principles (enforceable)
1. **Diverge on mechanism.** Concepts must differ in *how* value is delivered (self-serve vs assisted vs proactive vs agent-delegated), not in colour or channel alone.
2. **Test the riskiest assumption first.** For each concept, list what has to be true. Pick the assumption that is most important and least evidenced, then choose the cheapest prototype that can kill it.
3. **Climb the ladder, don't skip rungs.** Desirability comes before usability, and usability before operability. Building software before a concierge test is how teams fund the wrong service.
4. **Pre-register criteria.** Write "advance if ≥X of N complete the task / choose it / don't call back" before the session. Criteria set afterwards are rationalisation.
5. **Prototype the backstage too.** An operability test (staff role-play with the new process, a desktop walkthrough with real case files) is mandatory before a pilot.

## Prototype ladder
| Rung | Question | Methods |
|---|---|---|
| Desirability | Do they want it, and does it solve the job? | storyboard, concept card test, fake door / landing page, concierge (do it by hand for 5 users) |
| Usability | Can they use it? | paper / clickable prototype, scripted role-play, **Wizard of Oz** (a human plays the system or agent) |
| Operability | Can we deliver it repeatedly? | desktop walkthrough with real cases, bodystorming in the real space, staff simulation, shadow run |
| Pilot | Does it move the metric in real operation? | single site / segment / time-box, with a comparison group and stop rules |

## Core Blueprint
1. **Concepts.** Write 2–3 concept cards: name, for whom, job solved, how it works (frontstage + backstage), what changes for staff, agent role if any, riskiest assumptions.
2. **Assumption ranking.** Score each assumption by importance × lack of evidence. Pick the top 1–2 per concept (use `assumption-audit` for heavy cases).
3. **Test plan.** For each test: assumption, rung, method, participants, script, **pre-registered pass/fail**, and the decision it unlocks.
4. **Run and record.** One note per session in STATE_ROOT. Results are recorded against the criteria, not against impressions.
5. **Verdict.** Advance / iterate / kill per concept. Killing a concept is a result, not a failure. Log why.
6. **Pilot design** for the survivor: scope, duration, comparison (before/after or control site), the primary metric from `service-performance-measurement`, guardrail metrics, stop rules (e.g. complaints > baseline + 20%), owner, and a decision date.

## Agent concepts (agentic rung)
- **Wizard of Oz first.** A trained person answers through the agent's interface using the intended policy and tools. You learn the real request mix, the edge cases and the handoff triggers before writing a line of code.
- **Transcripts become the eval seed.** Every WoZ session, labelled with correct outcome and handoff decision, goes to `agentic-service-evaluation` as golden cases.
- **Test the handoff, not just the conversation.** Include scenarios where the agent must hand off, and measure whether the customer had to repeat themselves.

## Optimizations/Gotchas
- **High-fidelity too early anchors stakeholders.** A polished mock reads as "decided". Keep prototypes visibly rough until the operability rung.
- **Five users find most usability problems, not most desirability truths.** Size desirability tests by the decision, and don't over-read n=5 on preference.
- **Pilots without stop rules never stop.** They drift into permanent half-services. The stop rule and decision date are part of the design.
