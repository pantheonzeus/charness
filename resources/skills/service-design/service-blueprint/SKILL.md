---
id: service-blueprint
aliases: [service-blueprint]
name: "Service Blueprint — Operational Truth, Fail Points & Ownership"
category: service-design
description: Builds current- or future-state service blueprints. Lanes cover evidence, customer actions, human and digital frontstage, backstage, support systems and policies, separated by the lines of interaction, visibility and internal interaction. Every step carries an owner, a time and a KPI. Fail, wait and decision points are marked and costed. Orphan steps and cross-team handoffs are surfaced, and the result converts into a change list for operations and IT.
triggers: [service blueprint, blueprint the service, frontstage backstage, line of visibility, line of interaction, support processes, fail points, wait points, handoffs between teams, process and experience, operational redesign, who owns this step, backstage process, future state blueprint]
tags: [service-design, blueprint, operations, backstage, fail-points]
related: ["[[journey-mapping]]", "[[agentic-service-blueprint]]", "[[service-performance-measurement]]", "[[operating-model-design]]", "[[transformation-roadmap]]", "[[cloud-architecture]]"]
modules: [file-backed-state, evidence-backed-answering, verifier-separation]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
---

# Service Blueprint — Operational Truth, Fail Points & Ownership

## Contract
- **Input:** a journey (current or future), plus access to the people and systems behind it: process docs, system lists, staff, case data.
- **Output:** `output/<YYYYMMDD>-<slug>-blueprint-<current|future>.md` with (a) the blueprint table (steps as columns, lanes as rows, or the transposed table for long services), (b) the fail-point register, (c) the handoff and ownership analysis, and (d) for future state, the change list.
- **Allowed tools/artifacts:** conversation, process docs, system inventories, case/ticket data, staff walkthroughs.
- **Done when:** every step has a named owning role; every fail point has a frequency (data or tagged estimate) and a cost or impact; cross-team handoffs are counted; the current state was walked through with at least one frontline and one backstage person (or the gap is flagged); the verifier pass records PASS.

## Lanes (house standard)
| Lane | Holds |
|---|---|
| Physical / digital evidence | what the customer sees or receives: letter, screen, email, SMS, invoice |
| Customer actions | from the journey map |
| — line of interaction — | |
| Frontstage — human | staff the customer meets: agent, advisor, technician |
| Frontstage — digital | app, portal, chatbot, IVR, the provider's customer-facing AI agent |
| — line of visibility — | |
| Backstage | staff work the customer doesn't see: case handling, approvals, scheduling |
| — line of internal interaction — | |
| Support systems & partners | CRM, ERP, core systems, data, third parties, the provider's backstage AI agents |
| Policies & rules | the rule, SLA or regulation that governs the step |
| Owner · time · KPI | owning role, elapsed and touch time, step measure |

Markers: **F** fail point · **W** wait point (with duration) · **D** decision point · **H** handoff between teams · **?** unknown, to verify.

## Operating principles (enforceable)
1. **Blueprint the real process, not the documented one.** The process manual is a hypothesis. Staff walkthroughs and case data are the evidence, and workarounds go on the blueprint.
2. **Every step has an owner.** A step without an owning role is an **orphan** and a top finding. Orphans are where cases go to die.
3. **Count the handoffs.** Each cross-team handoff is a queue, a context loss and a likely fail point. Report the handoff count end to end.
4. **Cost the failure.** Fail points carry frequency × consequence (rework time, re-contact, refund, churn, compliance exposure). That figure ranks the redesign.
5. **Policies are design material.** Many fail points are caused by a rule, not a person or a system. Name the rule and its owner, because a rule is often the cheapest thing to change.

## Core Blueprint
1. **Import the journey** as the customer-actions lane. Keep its step IDs.
2. **Walk each step backstage.** Ask: who does what, in which system, triggered by what, under which rule, and how long does it take? Fill the lanes and mark F/W/D/H/?.
3. **Fail-point register.** For each F, record the failure mode, cause (people / process / system / policy / data), frequency, consequence, current detection, and a fix idea (prevent > detect > recover).
4. **Ownership and handoffs.** List the owning role per step, the orphans, the handoff count, and the longest wait chain.
5. **Validate.** Run a walkthrough with frontline and backstage staff. Update the blueprint and record who validated it.
6. **Future state (if asked).** Redesign from the top-ranked fail points and the journey opportunities. Mark each change as process / policy / system / role / agent. For agent candidates, hand off to `agentic-service-blueprint`.
7. **Change list.** Record each change with the affected step IDs, the owner, a size (S/M/L), dependencies, and the metric it moves. Hand it to `transformation-roadmap` and system changes to `cloud-architecture` where relevant.
8. **Verifier pass.** Re-check against the done-when list. Record PASS/FAIL in the STATE_ROOT `RESPONSE.md`. At most 2 revisions; anything still open is reported.

## Output structure
```markdown
## Scope and sources            (journey ref · who validated · data used)
## Blueprint                    lanes × steps table with F/W/D/H/? markers
## Fail-point register          | ID | Step | Failure mode | Cause | Frequency | Consequence (€/time) | Detection | Fix (prevent/detect/recover) |
## Ownership & handoffs         orphans · handoff count · longest wait chain
## Change list (future state)   | Change | Type | Steps | Owner | Size | Depends on | Moves metric |
```

## Optimizations/Gotchas
- **Long services break the table.** Past ~25 steps, transpose the table (steps as rows, lanes as columns) or split it by stage. Never shrink the content to fit.
- **"The system does it" is not a lane entry.** Name the system and the trigger. If nobody knows, mark **?**, which is a finding in itself.
- **Don't blueprint everything.** Blueprint the stages where the journey shows moments of truth or failure demand. Breadth without depth wastes the walkthroughs.
- **AI agents are actors, not systems.** If an agent already runs a step, put it in a lane with its autonomy level. A chatbot buried under "support systems" hides who decided what.
