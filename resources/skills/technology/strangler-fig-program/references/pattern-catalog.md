# Strangler Fig — Pattern Catalog

Shared reference for `strangler-fig-program`, `legacy-seam-mapping`, `strangler-transition-architecture` and `strangler-slice-cutover`.

**Sources:** Martin Fowler, *StranglerFigApplication* (bliki, 2004, revised since) — https://martinfowler.com/bliki/StranglerFigApplication.html · Ian Cartwright, Rob Horn & James Lewis, *Patterns of Legacy Displacement* — https://martinfowler.com/articles/patterns-legacy-displacement/ · Sam Newman, *Monolith to Microservices* (O'Reilly, 2019) · Eric Evans, *Domain-Driven Design* (2003) — anti-corruption layer · Microsoft Azure Architecture Center, *Strangler Fig pattern* — https://learn.microsoft.com/en-us/azure/architecture/patterns/strangler-fig · Martin Fowler, *BranchByAbstraction* — https://martinfowler.com/bliki/BranchByAbstraction.html · Ferri, Coggrave & Sheth, *Legacy Modernization meets GenAI* (martinfowler.com, 2024-09-24) — https://martinfowler.com/articles/legacy-modernization-gen-ai.html · Thoughtworks Technology Radar Vol. 34 (April 2026) — https://www.thoughtworks.com/content/dam/thoughtworks/documents/radar/2026/04/tr_technology_radar_vol_34_en_1.pdf

*Source dates checked 2026-10-10: Fowler bliki last revised 2024-08-22; Legacy Displacement catalog last addition 2024-03-05 (Event Interception); Azure pattern page ms.date 2026-05-29.*

## §1 Strategy choice — strangle, rewrite, retain or replace

| Option | Choose when | Reject when |
|---|---|---|
| **Strangle** (incremental) | Large or critical system, change pressure continues during the migration, the legacy is only partly understood, and traffic can be intercepted | No interceptable seams and no budget for branch by abstraction; or the system is small enough to rewrite in one quarter |
| **Rewrite** (big bang) | Small, well-understood, low-criticality system; a short freeze is acceptable | Anything where the rewrite runs > ~6 months while the legacy keeps changing — the target keeps moving |
| **Retain / encapsulate** | Stable, cheap to run, little change pressure; wrap it in an API and leave it | Run cost, end-of-support or talent risk is the trigger |
| **Replace with SaaS / package** | The capability is a commodity (HR, finance, CRM) — buy the commodity | It's the differentiator; or the package needs heavy customization to fit (that's a rewrite with a licence fee) |

Mixed answers are normal: retain the stable core, buy the commodity capabilities, strangle the differentiating ones.

**Strangling doesn't fit** (Azure Architecture Center) when requests can't be intercepted, when you have no access to the legacy source code (you need it to disable migrated features and redirect internal calls), when the system is small enough to replace in one go, or when the legacy must be gone quickly. For the last case, a planned **Stop the World Cutover** is the honest option. Price its downtime and rehearse it.

## §2 Interception mechanisms (seam types)

| Mechanism | Seam | Notes |
|---|---|---|
| **Routing facade** (reverse proxy / API gateway) | HTTP/API traffic | The default. Route by path, operation, tenant or header. It becomes a hot-path SPOF, so engineer it accordingly. |
| **UI composition** | Screens / pages | Route pages or embed new fragments. Works when the UI is web-based and page-addressable. |
| **Event interception** | Messages, queues, file drops | Put a router in front of the queue or file interface and divert per message type. |
| **Branch by abstraction** | In-process calls, no external seam | Introduce an abstraction inside the legacy code, put both implementations behind it, and switch with a toggle. Needs changes to the legacy code — budget for it. |
| **Change data capture (CDC)** | The database itself | For syncing data, not for intercepting behaviour. Prefer an outbox where you control the writer. |

## §3 Supporting patterns

| Pattern | Use |
|---|---|
| **Anti-corruption layer** | Translate between the legacy and new models so legacy concepts don't leak into the new domain. |
| **Legacy mimic** | The new system feeds data back in the legacy's format so consumers that haven't moved yet keep working. |
| **Extract product lines / value streams** | Slice by what the business sells or delivers, not by technical layer. |
| **Dark launching / shadow traffic** | Run the new path on real traffic without serving its results; compare outputs (parity gate). |
| **Parallel run** | Both systems process the same inputs, and the outputs are reconciled. The strongest evidence of parity. |
| **Canary release** | Divert a small, controlled share of real traffic and ramp up with rollback triggers. |
| **Archive** | Retire data the new system doesn't need, with retention rules, instead of migrating it. |
| **Critical aggregator** | Build the new reporting/decision view early by aggregating from both systems — a frequent high-value first slice. |
| **Revert to source** | Go back to the original data source instead of the legacy's copy of it, which lets you skip migrating legacy data. |
| **Divert the flow** | Move activities that span the organization (e.g. a shared upstream process) off the legacy first, so later slices don't depend on it. |
| **Stop the world cutover** | Planned downtime and a one-shot switch. Legitimate for small slices or hard deadlines, but priced and rehearsed. |
| **Event Storming / value stream map / identify business capabilities** | The *understanding* patterns: derive capabilities from how the business works, not from the code. |
| **Build as you mean to continue** | The new system is built with the target practices and team model from day one, or it becomes the next legacy. |
| **Protected pilot** | Shield the first slice's team from standard governance so it can prove the new way of working. |
| **AI-assisted reverse engineering** | Code graph + LLM to draft capability maps, business rules and specs. Human-validated; for comprehension, not translation (Thoughtworks, 2024; Radar Vol. 34, 2026). |

## §4 Red flags (verifier checklist)

- [ ] **Feature-parity scope** — "rebuild everything it does" with no dropped list.
- [ ] **No decommission dates** — slices go live but nothing gets switched off.
- [ ] **Application-level dual writes** without a transaction or reconciliation.
- [ ] **Two systems of record** for the same entity in the same phase.
- [ ] **Business logic in the facade.**
- [ ] **Horizontal slicing** (UI first, then DB) instead of vertical capabilities.
- [ ] **First slice is the core** (posting, master data, billing) instead of a thin, low-coupling one.
- [ ] **Microservices as the goal** with no requirement that a modular monolith fails.
- [ ] **No dual-run cost** stated, or no strangling deadline.
- [ ] **Rollback requires a data migration.**
- [ ] **Progress reported as new-system output** (services, sprints, LOC) instead of legacy retired.
- [ ] **Legacy team not involved**, or not retained through the program.
- [ ] **No organizational change** — the new system is built with the same practices and team structure that produced the legacy.
- [ ] **AI transpilation as the strategy** — line-by-line machine translation of legacy code, or AI-extracted rules shipped without SME/runtime confirmation.
- [ ] **Legacy data objects dropped before validation** — the rollback window closed early.
- [ ] **Facade has no end state** — neither a removal date nor a recorded decision to keep it as an adapter.
