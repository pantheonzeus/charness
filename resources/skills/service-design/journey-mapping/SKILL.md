---
id: journey-mapping
aliases: [journey-mapping]
name: "Journey Mapping — Evidence-Backed Current & Future State"
category: service-design
description: Builds current-state or future-state journey maps for one actor and one scenario. Each map has stages, steps, touchpoints, channels, thoughts and feelings backed by verbatims, pain points, moments of truth, failure-demand points and stage metrics. It ends in prioritised opportunities and becomes the frontstage spine of the service blueprint.
triggers: [journey map, customer journey, user journey, experience map, current state journey, future state journey, moments of truth, pain points map, touchpoint map, cross-channel journey, employee journey, lifecycle journey, map the experience]
tags: [service-design, journey, experience, frontstage]
related: ["[[service-discovery-research]]", "[[service-blueprint]]", "[[service-design-engagement]]", "[[service-performance-measurement]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
---

# Journey Mapping — Evidence-Backed Current & Future State

## Contract
- **Input:** an actor (customer segment, employee role, or a customer's AI agent, for which see `agent-ready-service`), a scenario with a start trigger and an end outcome, and research evidence (insights file, transcripts, analytics, contact data).
- **Output:** `output/<YYYYMMDD>-<slug>-journey-<current|future>.md` containing the journey table, the moments-of-truth list and the opportunity list. Optionally a Mermaid `journey` diagram for the emotional curve.
- **Allowed tools/artifacts:** conversation, research outputs, analytics/contact data.
- **Done when:** every pain point and emotion cites evidence (observation ID or data source) or is tagged **assumed**; every stage carries at least one metric or a "no data" flag; moments of truth are marked; each future-state change is traceable to a current-state pain point.

## Operating principles (enforceable)
1. **One actor, one scenario, one map.** "All customers" produces an average journey nobody lives. Make separate maps per segment where behaviour really differs.
2. **Customer-language stages.** Name stages from the customer's side ("Find out if I'm covered"), not by department ("Claims intake").
3. **Evidence or label.** Emotions come from verbatims or observed behaviour, never from the designer's imagination. Unverified rows are tagged **assumed** and go into the next research round.
4. **Include the unhappy paths.** Map the drop-out, the re-contact and the escalation alongside the happy path. That's where the failure demand lives.
5. **Numbers per stage.** Volume, drop-off, elapsed time, contacts per case and cost where known. A journey map without numbers is a mood board.

## Core Blueprint
1. **Scope.** Actor, scenario, start trigger, end outcome, channels in scope, current vs future.
2. **Stages and steps.** List 4–8 stages, then the steps within each from the actor's point of view, including off-channel steps (asking a friend, searching, waiting).
3. **Fill the lanes per step:** touchpoint and channel · actor actions · thoughts (verbatim) · feeling (−2..+2, with source) · pain points · opportunity.
4. **Overlay data:** stage metrics, failure-demand points (where people contact you because something didn't happen or went wrong), handoffs between channels.
5. **Moments of truth.** Mark the 2–4 steps where the actor decides to trust, continue or leave. These carry the design priority.
6. **Opportunities.** Turn each top pain point into a "How might we", then rank them by impact on the moments of truth and the failure demand.
7. **Future state (if asked).** Redesign the journey only after the current state has been validated with frontline staff. Mark each step as removed / automated / changed / new, with the pain point it resolves. Then hand it to `service-blueprint` to check that the backstage can deliver it.

## Output structure
```markdown
## Scope   actor · scenario · trigger → outcome · current|future · evidence base
| Stage | Step | Touchpoint/channel | Actions | Thoughts (verbatim, ID) | Feeling (−2..+2, src) | Pain points | Metric | Opportunity |
## Moments of truth   (step · why it decides the relationship · evidence)
## Failure-demand points   (step · reason code · volume/share)
## Opportunities (ranked)
```

## Optimizations/Gotchas
- **The pretty-poster trap.** Visual polish gets mistaken for rigour. The table with evidence IDs is the deliverable. Visualise afterwards, if at all.
- **Waiting is a step.** Long silences between touchpoints are where anxiety and status calls come from. Map them, with durations.
- **Employee journeys are journeys too.** For a backstage-heavy service, map the caseworker's journey. It often explains the customer's pain better than the customer map does.
- **Future-state maps lie when nobody checks the backstage.** Every future step must survive the blueprint test before it is presented as a commitment.
