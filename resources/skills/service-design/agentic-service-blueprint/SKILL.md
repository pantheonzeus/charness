---
id: agentic-service-blueprint
aliases: [agentic-service-blueprint]
name: "Agentic Service Blueprint — Human–Agent Work Design"
category: service-design
description: Redesigns a service with AI agents as actors, frontstage and backstage. The method decomposes blueprint steps into tasks, scores agent fit with hard vetoes, and sets an autonomy level per task (operator → observer). It keeps a named human accountable for every agent task and designs the handoffs, the oversight checkpoints (AI Act Art. 14 as checklist), the failure modes and the degraded mode, staff role changes, and the cost per resolved case for human versus agent.
triggers: [AI agents in the service, agentic service, agentic blueprint, where can agents help, automate the service with AI, AI agent customer service, human in the loop, human-agent handoff, escalation to human, autonomy level, agent oversight, AI Act human oversight, agentic workflow design, digital workforce, replace the chatbot, agent and caseworker]
tags: [service-design, agentic, ai-agents, blueprint, human-in-the-loop, oversight]
related: ["[[service-blueprint]]", "[[agentic-service-evaluation]]", "[[agent-ready-service]]", "[[service-performance-measurement]]", "[[operating-model-design]]", "[[risk-and-mitigation]]", "[[cloud-architecture]]", "[[ai-opportunity-portfolio]]", "[[agent-architecture]]", "[[multi-agent-platform]]"]
modules: [file-backed-state, evidence-backed-answering, verifier-separation]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
requires:
  tools: [web_search]
environment: "Runs anywhere. Regulatory dates in the reference are a 2026-10-10 snapshot — re-verify before client use."
references: [references/agentic-patterns.md]
---

# Agentic Service Blueprint — Human–Agent Work Design

## Contract
- **Input:** a current-state service blueprint (build one first with `service-blueprint` if none exists), plus volumes, cost rates, systems and the risk context (regulation, customer vulnerability).
- **Output:** `output/<YYYYMMDD>-<slug>-agentic-blueprint.md` containing (a) the task decomposition with fit scores, (b) the **autonomy register** (task · level · accountable human · rationale), (c) the future-state blueprint with agent lanes, handoff markers and oversight checkpoints, (d) the handoff specs, (e) the failure-mode and degraded-mode table, (f) the workforce impact, (g) the economics per task.
- **Allowed tools/artifacts:** conversation, blueprint and data, [agentic-patterns.md](references/agentic-patterns.md), web search for current regulation.
- **Done when:** every agent task has an autonomy level with a rationale **and** a named accountable human role; every veto is applied or its exception justified; every handoff has trigger conditions and a context-packet spec; a degraded mode exists for agent outage; the economics include review and error cost; the verifier pass records PASS.

## Upstream
For a portfolio-level question ("where across the function should we use agents?"), rank candidates first with business-design's AI opportunity portfolio. This skill designs **one service** in depth.

## Operating principles (enforceable)
1. **Agents are actors in lanes, not features.** The blueprint gets explicit lanes: *Agent — frontstage*, *Agent — backstage*, *Human oversight*. Every agent cell shows its autonomy level (L1–L5).
2. **Accountability never moves to the agent.** In the RACI, an agent can be **R** (responsible for doing the work), never **A** (accountable for the result). Every agent task names the accountable human role.
3. **Autonomy is chosen, then earned.** Set the level by harm, reversibility and verifiability, not by what the model can do. House ceiling: L3 for irreversible customer-impacting tasks until `agentic-service-evaluation` promotion criteria are met.
4. **Vetoes are hard.** Keep the task human (or at L1–L2) if a legally required human decision is involved, if it's a decision with significant effect made solely by automated processing (GDPR Art. 22) without a lawful exception and safeguards, if it's a vulnerability determination, or if errors can't be detected before harm.
5. **Design the handoff before the happy path.** The customer never repeats themselves. The receiving human gets a context packet. The escalation should feel like progress.
6. **Oversight is a designed role.** Use Art. 14(4) as the checklist (understand, monitor, automation-bias countermeasures, interpret, override, interrupt). The overseer has training, authority and a time budget (Art. 26(2)).
7. **Count the whole cost.** Agent cost per resolved case = inference + tooling + human review time + error remediation + oversight overhead. Compare it with the human cost per resolved case, not per contact.
8. **Say it's an AI.** Customer-facing agents disclose that they are AI (AI Act Art. 50, from Aug 2026). Verify the current requirement.

## Core Blueprint
Substantive runs keep a STATE_ROOT at `output/.runs/<YYYYMMDD>-<slug>-agentic/` with a `RESPONSE.md` control spine (steps 1–10) and `EVIDENCE.md`.

1. **Import the blueprint.** Bring in the steps, owners, fail points, volumes and cost. Mark which fail points the redesign targets.
2. **Decompose.** Split each step into tasks and type each one: retrieve · classify · decide (rule) · decide (judgment) · communicate · transact · coordinate.
3. **Score fit.** Use the six-factor score from the reference (volume, repeatability, verifiability, reversibility, information availability, harm). Apply the vetoes. Shortlist tasks scoring ≥12 with no veto.
4. **Set autonomy.** Assign L1–L5 per shortlisted task with a one-line rationale and the evidence that would justify promoting it a level.
5. **Accountability.** Build the RACI with humans and agents. Name the accountable role per agent task, plus the overseer role and their capacity (cases or hours per day).
6. **Redraw the blueprint.** Add the agent lanes and oversight lane. Mark handoffs (**H→**), approval gates (**◆**) and kill-switch points (**■**). Agent-to-agent work has a named orchestrator.
7. **Specify the handoffs.** For each one: trigger conditions, context-packet fields, receiving queue, SLA, customer message, and what happens when the queue is full.
8. **Failure modes and degraded mode.** Use the reference table (confabulation, wrong action, scope creep, loop, prompt injection, silent degradation, bias) with prevent / detect / recover per agent task. Define the degraded mode: who takes the work when the agent is off, and how the customer is told.
9. **Workforce impact.** Role by role: tasks removed, tasks added (reviewing, exception handling, agent supervision, prompt/policy ownership), training needed, and how capacity is redeployed. In DE/AT/NL, flag works-council co-determination for monitoring or role changes.
10. **Economics and verifier.** Cost per resolved case, human vs agent, per task; break-even volume; the metrics handed to `service-performance-measurement`. Then the verifier pass: re-read against the done-when list and record PASS/FAIL. At most 2 revisions, and report anything still open.

## Output structure
```markdown
## Scope and baseline            (blueprint ref · volumes · target fail points)
## Task decomposition & fit      | Step | Task | Type | Vol | Rep | Verif | Rev | Info | Harm | Score | Veto |
## Autonomy register             | Task | Level | Accountable human | Overseer | Rationale | Promotion evidence |
## Future-state agentic blueprint lanes incl. Agent-front, Agent-back, Human oversight; markers H→ ◆ ■
## Handoff specs                 | Handoff | Trigger | Context packet | Receiver | SLA | Customer message | Overflow |
## Failure & degraded mode       | Task | Failure | Prevent | Detect | Recover |  + degraded-mode plan
## Workforce impact              | Role | Removed | Added | Training | Capacity |
## Economics                     | Task | Human €/resolved | Agent €/resolved (incl. review+errors) | Break-even |
## Open risks → risk-and-mitigation
```

## Optimizations/Gotchas
- **"Put an agent on the front door" is the most common bad design.** A frontstage agent on a broken backstage just answers status calls faster. Fix the fail points the blueprint found first, because many will remove the demand entirely.
- **Backstage agents usually pay first.** Document intake, case preparation and data reconciliation are high-volume, verifiable and invisible to the customer. That's lower risk and earlier value than customer-facing chat.
- **Approval gates rot into rubber stamps.** At L4, show the evidence with each approval, sample decisions for blind review, and track approval time. Approvals in under 3 seconds are a signal of automation bias.
- **Vendor demos run at L5 on curated data.** Your design runs at the level the evidence supports.
- **Technical architecture is a separate deliverable.** Model hosting, data residency and tool permissions go to `cloud-architecture`. This skill owns what the agent does and who answers for it.
