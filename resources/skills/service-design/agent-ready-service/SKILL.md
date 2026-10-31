---
id: agent-ready-service
aliases: [agent-ready-service]
name: "Agent-Ready Service — Designing for Customers' AI Agents"
category: service-design
description: Designs or audits a service so that customers' own AI agents can use it safely. It covers intent-first service descriptions, machine-readable discovery (structured catalogue, llms.txt, OpenAPI/MCP), delegated authority (scoped, revocable, step-up), composable resumable steps, legible receipts and action logs, and human escalation. The live test runs a real agent against the service and maps an agent journey of where it breaks.
triggers: [agent ready, agent-ready service, agent experience, AX, customers using AI agents, AI agents as customers, agentic commerce, agent can't use our site, MCP server for our service, llms.txt, machine-readable service, delegated access for agents, agent acting on behalf of customer, agentic interfaces, design for AI agents as users]
tags: [service-design, agentic, agent-experience, ax, delegation, interoperability]
related: ["[[agentic-service-blueprint]]", "[[journey-mapping]]", "[[service-ecosystem-mapping]]", "[[cloud-architecture]]", "[[agentic-service-evaluation]]"]
modules: [evidence-backed-answering, verifier-separation]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
requires:
  tools: [web_fetch]
  optional: [a browser/computer-use agent or Claude with web tools for the live agent test]
references: [../agentic-service-blueprint/references/agentic-patterns.md]
---

# Agent-Ready Service — Designing for Customers' AI Agents

## Contract
- **Input:** a service (URL, API docs, or journey/blueprint), its key customer intents, and the risk class of each intent.
- **Output:** `output/<YYYYMMDD>-<slug>-agent-readiness.md` containing (a) the intent inventory with agent suitability, (b) the agent journey map from the live test, (c) a readiness scorecard over six dimensions, (d) the prioritised design changes, (e) the delegation and accountability spec.
- **Allowed tools/artifacts:** conversation, web fetch of public pages and docs, a real agent run against **public or test** flows only. Never submit real transactions, applications or personal data in the live test.
- **Done when:** every key intent has a suitability verdict; at least one live agent test ran and is logged step by step (or the reason it couldn't run is stated); all six dimensions are scored with evidence; every high-risk intent has a step-up and escalation design.

## Operating principles (enforceable)
1. **Intents, not pages.** Describe the service by the jobs people delegate ("renew my contract", "report a fault"), each with its inputs, eligibility rules and outcome. Agents navigate intents; org-chart menus defeat them.
2. **Two front doors, one service.** The agent channel and the human channel share the same rules, prices and outcomes. Never degrade the human path, and never give agents worse terms without saying so.
3. **Delegation is scoped, revocable and visible.** The customer grants an agent specific permissions for specific intents, with an expiry. They can see and revoke the grant. High-risk actions (payment, cancellation, data change) need step-up confirmation from the human.
4. **Steps must survive interruption.** Every step is independently callable, idempotent and resumable. Session timeouts that discard half-done work are a defect for agents and for people.
5. **Receipts for the principal.** Every action by an agent produces a human-legible record: what was done, on whose authority, when, and how to undo or dispute it.
6. **Agent content is untrusted input.** Treat what agents send as data. Rate-limit, validate, and keep fraud and abuse controls on. Being agent-friendly is not the same as being agent-naïve.

## Readiness scorecard (0–3 each)
| Dimension | 0 | 3 |
|---|---|---|
| Discoverability | only marketing pages | structured catalogue, `llms.txt`, documented API/MCP per intent |
| Legibility | rules hidden in PDFs or flows | eligibility, prices and SLAs machine-readable and plain-language |
| Actionability | UI only, CAPTCHA walls | API/MCP for key intents; semantic, stable UI for computer-use agents |
| Delegation | shared passwords the only option | scoped, revocable, time-bound grants + step-up |
| Composability | long stateful session | idempotent, resumable steps with status endpoints |
| Accountability | no record of agent actions | action log + receipts to principal + dispute and escalation path |

## Core Blueprint
1. **Intent inventory.** List the top 10–20 intents by volume. For each, record inputs, rules, outcome, risk class, and suitability for agent delegation (yes / with step-up / human only).
2. **Live agent test.** Give a real agent 2–3 representative intents on public or test flows and log every step: what it found, where it guessed, where it got stuck, what it misread. This is the agent journey map. Use the `journey-mapping` lanes, with "agent reasoning" in place of thoughts and feelings.
3. **Score readiness** on the six dimensions, citing the test log and the docs reviewed.
4. **Design changes.** Map each gap to a change (content / rule / API / identity / process), rank by intent volume × gap severity, and give the first move. Rewriting service descriptions around intents needs no technology spend and comes first.
5. **Delegation and accountability spec.** Per intent: permission scope, expiry, step-up trigger, receipt content, dispute path, human escalation trigger.
6. **Ecosystem check.** Add customers' agents and agent platforms as actors in `service-ecosystem-mapping`. Note who carries the risk when an agent errs.
7. **Hand off.** API, MCP and identity architecture go to `cloud-architecture`. Monitoring of agent-channel quality goes to `agentic-service-evaluation`.
8. **Verifier pass.** Re-check the done-when list and record PASS/FAIL. At most 2 revisions.

## Optimizations/Gotchas
- **Blocking all bots is a business decision, not a security default.** Separate abusive automation from legitimate delegated agents, and decide per intent.
- **Agents expose bad content design brutally.** If an agent misreads the eligibility rule, many humans do too. These fixes pay off twice.
- **Don't promise "MCP everything".** Start with the 2–3 highest-volume, low-risk intents. A sprawling, poorly-scoped tool surface is a security and support liability.
- **Public-sector parallel:** life-event services (one intent across agencies) are the agent-ready pattern governments are moving toward. Use them as the reference model for multi-party services.
