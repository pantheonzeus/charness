---
id: service-design-engagement
aliases: [service-design-engagement]
name: "Service Design Engagement — Principal Framing & Router"
category: service-design
description: Entry point for any service design work. Frames the outcome and the money at stake, draws the service boundary, decides where AI agents fit, and produces a phased engagement plan with decision gates. It then routes each phase to the right service-design skill. This is how a principal service designer shapes the work before anyone opens a whiteboard.
triggers: [service design, service designer, redesign the service, end-to-end service, customer service redesign, service transformation, design a new service, service design project, service design engagement, double diamond, principal service designer, service innovation, improve the customer experience end to end, where should we use AI agents in our service]
tags: [service-design, engagement, framing, principal, router]
related: ["[[service-discovery-research]]", "[[journey-mapping]]", "[[service-blueprint]]", "[[service-ecosystem-mapping]]", "[[service-concept-prototyping]]", "[[service-codesign-facilitation]]", "[[service-performance-measurement]]", "[[agentic-service-blueprint]]", "[[agent-ready-service]]", "[[agentic-service-evaluation]]", "[[situation-assessment]]", "[[stakeholder-alignment]]", "[[transformation-roadmap]]", "[[business-design-engagement]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
references: [references/role-and-competencies.md]
vault_writes: ["cbrain/Clients/*", "cbrain/projects/*"]
---

# Service Design Engagement — Principal Framing & Router

## Contract
- **Input:** a brief, from one sentence ("our claims process is a mess") to an RFP. Plus whatever exists: org chart, contact data, complaints, prior research, cost figures.
- **Output:** `output/<YYYYMMDD>-<slug>-sd-engagement-plan.md` using the structure below, indexed into `cbrain/notes/Deliverables/` (Charter §4). The client account and stakeholders are wired into the vault per Charter §6.
- **Allowed tools/artifacts:** conversation, user-supplied material, the vault (harvest prior meetings and account notes first), web search for sector context.
- **Done when:** (1) the outcome is a named metric with a baseline or a tagged estimate; (2) the service boundary says what is in and what is out; (3) every phase has a decision gate, an owner and a named deliverable; (4) the agentic stance is explicit (per-step candidates, or "not yet" with the reason); (5) the operational owner who must change their process is named.

## Triggers/Context
Use this skill when a request concerns a whole service, or when it isn't clear which service-design skill applies. For a single, clearly scoped artifact ("blueprint this onboarding flow"), go straight to that skill. This skill is the principal's job: deciding **what to redesign, for what outcome, with whose commitment**. The method work comes after.

## Operating principles (enforceable)
1. **Outcome before method.** No phase plan until the plan names the business outcome (cost-to-serve, conversion, retention, risk or compliance) and the users' outcome. If nobody can name either, the first deliverable is a 1-page problem frame, not a project.
2. **Draw the boundary.** A service is defined by where it starts (the trigger or need) and where it ends (the outcome achieved), not by an org unit. Write both down. Scope creep and "boil the ocean" research both start with a missing boundary.
3. **The backstage is the job.** Most cost and most failure live backstage. Every plan includes a blueprint phase and puts frontline staff and the systems owners in the research sample.
4. **Find the money early.** Commission a demand sample (`service-performance-measurement` step 2) in week 1–2. A failure-demand share, even a rough one, is the strongest business case a service designer can bring.
5. **Agents are a per-step design decision, not a strategy.** Never plan "an AI agent for the service". Plan to assess each blueprint step for agent fit (`agentic-service-blueprint`). If customers already arrive via their own AI agents, add `agent-ready-service`.
6. **Pilot over deck.** Every plan ends in something that runs in the real operation (a pilot, a changed process, a live agent in shadow mode), with a stop rule. A future-state map with no pilot is a finding against the plan.
7. **Design with the operation, not at it.** The person who owns the process that must change signs off the boundary and the gates. Without that person the plan carries a named risk.

## Core Blueprint
Substantive runs keep a STATE_ROOT at `output/.runs/<YYYYMMDD>-<slug>-sd/` with `RESPONSE.md` (the phase gates as boxes) and `EVIDENCE.md`.

1. **Harvest.** Search the vault for the account, people and prior work. Load the brief and the data. List what is known, assumed and missing.
2. **Frame.** Write the problem frame: who, what need, current outcome, cost of the status quo (tagged fact or estimate), and the constraints (regulation, systems, union/works council, budget, deadline).
3. **Boundary and ambition.** Set the start trigger and end outcome, what's in and out, and the ambition level: *fix* (remove failure in the existing service), *redesign* (new end-to-end flow on the same proposition) or *new service* (new proposition — pull in business-design).
4. **Hypotheses.** Write 3–5 falsifiable hypotheses about where value is lost, e.g. "≥40% of inbound contacts are failure demand caused by status uncertainty". Research is planned to kill or confirm them.
5. **Phase plan.** Use the routing table and pick only the phases the ambition needs. A *fix* rarely needs ecosystem mapping. A *new service* rarely skips it.
6. **Governance.** Name the sponsor, the operational owner, the decision forum and cadence, and the participation of frontline staff and customers, plus any works council or DPO touchpoints (EU).
7. **Risks.** List the top 5 risks with owner and mitigation. Always include "the redesign stalls at handover to delivery" and "insight without an operational owner".
8. **Gate.** Before releasing the plan to the client, run the evidence gate on every numeric claim and check the done-when list.

## Routing table
| Need | Skill | Typical deliverable |
|---|---|---|
| Understand users, staff, demand | `service-discovery-research` | research plan, insight report |
| See the experience end to end | `journey-mapping` | current/future-state journey |
| See the operation that delivers it | `service-blueprint` | blueprint + fail-point register |
| Many organisations or actors involved | `service-ecosystem-mapping` | actor map + value-exchange table |
| Generate and test the new service | `service-concept-prototyping` | concept cards, test plan, pilot design |
| Run workshops that end in decisions | `service-codesign-facilitation` | session plans + decision log |
| Prove value, baseline and track | `service-performance-measurement` | measurement framework + baseline |
| Put AI agents into the service | `agentic-service-blueprint` | agentic blueprint + autonomy register |
| Customers' agents use the service | `agent-ready-service` | agent journey + readiness scorecard |
| Prove the agentic service is safe to scale | `agentic-service-evaluation` | eval suite + rollout gates |
| Exec buy-in / pre-wire | `stakeholder-alignment` (strategy) | |
| Business case / roadmap / operating model | `business-case-builder`, `transformation-roadmap`, `operating-model-design` (strategy) | |

## Output structure
```markdown
# <Service> — Service Design Engagement Plan
## 1. Outcome and money at stake   (business outcome · user outcome · baseline [fact|estimate, source])
## 2. Problem frame                 (who · need · today's outcome · constraints)
## 3. Service boundary              (start trigger → end outcome · in / out · ambition: fix|redesign|new)
## 4. Hypotheses to test            (3–5, each with the evidence that would kill it)
## 5. Phases and gates              | Phase | Skill | Deliverable | Gate decision | Owner | Weeks |
## 6. Agentic stance                (candidate steps / customer-agent channel / "not yet" + reason)
## 7. Governance and participation  (sponsor · operational owner · forum · staff & customer involvement)
## 8. Risks                         | Risk | Likelihood | Impact | Mitigation | Owner |
## 9. Open questions
```

## Optimizations/Gotchas
- **"Map the customer journey" is not a goal.** If the brief asks for an artifact, ask which decision it will inform. Reframe around that decision.
- **Org-chart boundaries are the most common framing error.** "The contact centre" is not a service. "Getting a claim paid" is.
- **Research participants are not vault contacts.** Stakeholders and client staff get vault notes (Charter §6). Interviewed customers stay pseudonymised in the research file, never in `Clients/`.
- **A principal kills scope.** If the timeline can't fit discovery and a pilot, cut the breadth of research, never the pilot.
- **Persona lens:** lead every readout with outcome and cost, then experience, then technology. A beautiful journey map with no number on it gets no budget.
