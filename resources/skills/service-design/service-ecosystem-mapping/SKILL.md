---
id: service-ecosystem-mapping
aliases: [service-ecosystem-mapping]
name: "Service Ecosystem Mapping — Actors, Value Exchanges & Dependencies"
category: service-design
description: "Maps the actors needed to deliver one service: customers, staff, partners, regulators, systems, and AI agents on either side. For each actor it records the value exchanges between them (money, data, service, trust, risk), their incentives and power, and the dependencies and data flows the service relies on. It surfaces misaligned incentives, single points of failure and the actors a redesign must win over."
triggers: [ecosystem map, stakeholder map, actor map, service ecosystem, value exchange, value network, multi-party service, partner ecosystem service, who is involved in delivering, incentives map, data flows between parties, public sector multi-agency service]
tags: [service-design, ecosystem, actors, value-exchange, systems-thinking]
related: ["[[service-design-engagement]]", "[[service-blueprint]]", "[[stakeholder-alignment]]", "[[agent-ready-service]]", "[[ecosystem-platform-design]]", "[[servitization-model-design]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
---

# Service Ecosystem Mapping — Actors, Value Exchanges & Dependencies

## Contract
- **Input:** a service boundary (from `service-design-engagement`) and what is known about the parties involved: org charts, contracts, partner lists, system inventories, research.
- **Output:** `output/<YYYYMMDD>-<slug>-ecosystem.md` containing (a) the actor map as a Mermaid flowchart (core / direct / indirect rings as subgraphs), (b) the value-exchange table, (c) the actor table with incentives and power, (d) the dependency and risk list.
- **Allowed tools/artifacts:** conversation, user-supplied docs, vault account and people notes, web search for public parties (regulators, vendors).
- **Done when:** every exchange is typed and two-directional (what flows each way, or "nothing back", which is itself a finding); every actor has a stated incentive and an influence rating; at least one misaligned incentive or single point of failure is named, or the map states that none was found and why.

## Boundary with business-design
This skill maps the **operational ecosystem that delivers one service**. Designing the business model, platform or ecosystem strategy, or an as-a-Service / servitization model belongs in the `business-design` category. Hand off to it when the question becomes "who pays whom, and how do we monetise".

## Operating principles (enforceable)
1. **Value is co-created, so map exchanges, not boxes.** Following service-dominant logic, an actor matters because of what it gives and gets. An actor with no exchanges is decoration and gets removed.
2. **Type every flow:** € money · D data · S service/work · T trust/reputation · R risk/liability. Risk transfers (who carries the cost of failure) explain most of the dysfunction.
3. **Incentives over intentions.** For each actor, record what they're measured or paid on. A partner paid per ticket closed won't help reduce tickets.
4. **Agents are actors.** The provider's AI agents, vendors' agents and **customers' own AI agents** each appear with their principal (on whose behalf they act) and their permissions.
5. **Data flows carry obligations.** For each D flow, note the legal basis and the residency or contract constraint (GDPR, Data Act data-sharing, sector rules). Tag these as **inference** unless they're confirmed by the client's DPO or a contract.

## Core Blueprint
1. **List the actors** in three rings: core (customer and provider unit), direct (partners, other departments, systems, agents), indirect (regulators, funders, communities, competitors' substitutes).
2. **Exchanges.** For each pair that interacts, record what flows each way and the flow type. Mark broken or one-way exchanges.
3. **Actor table.** For each actor: role in the service, incentive / KPI, influence (H/M/L), stance on change (champion / neutral / blocker / unknown), pain in today's service.
4. **Dependencies.** Name the single points of failure, the critical third parties and contracts, and the shared data sources. For each, say what happens if it fails.
5. **Findings.** Misaligned incentives, missing exchanges (someone does work and gets nothing), risk sitting with the party least able to carry it, and the actors the redesign must win over. Hand the last group to `stakeholder-alignment`.

## Output structure
```markdown
## Actor map            ```mermaid flowchart LR  (subgraph Core / Direct / Indirect; edges labelled €/D/S/T/R)```
## Value exchanges      | From | To | Gives (type) | Gets back (type) | Healthy? |
## Actors               | Actor | Role | Incentive/KPI | Influence | Stance | Pain |
## Dependencies & risks | Dependency | Failure effect | Owner | Mitigation |
## Findings             misaligned incentives · missing exchanges · risk misallocation · actors to win
```

## Optimizations/Gotchas
- **Mermaid gets unreadable past ~20 nodes.** Group the indirect ring into one node per type and keep the detail in the tables.
- **"IT" is not an actor.** Name the system owner and the vendor separately. They have different incentives.
- **The regulator is often the hidden designer.** A rule set outside the organisation can explain a fail point that no internal redesign will fix. Name it and route it to policy engagement.
