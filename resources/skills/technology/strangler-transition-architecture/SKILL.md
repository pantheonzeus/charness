---
id: strangler-transition-architecture
aliases: [strangler-transition-architecture]
name: "Strangler Transitional Architecture — Facade, ACL & Data Sync"
category: technology
description: Design the temporary scaffolding a Strangler Fig program needs — the interception layer (routing facade, event interception or branch by abstraction), the anti-corruption layer between new and legacy models, and the data-synchronization approach — each with its cost, its failure mode, and the date it gets removed.
triggers: [strangler facade, routing facade, interception layer, anti-corruption layer, ACL, transitional architecture, branch by abstraction, event interception, change data capture, CDC, data synchronization legacy, dual write, legacy mimic, API gateway for migration]
tags: [technology, architecture, modernization, legacy, strangler-fig, integration]
related: ["[[strangler-fig-program]]", "[[legacy-seam-mapping]]", "[[strangler-slice-cutover]]", "[[cloud-architecture]]"]
modules: [verifier-separation]
status: active
version: 2
created: 2026-10-10
updated: 2026-10-10
environment: "Runs anywhere. Component choices follow cloud-architecture's boring-by-default rule; check product-specific claims (gateway/CDC tool capabilities) against current docs before they land in a client deliverable."
references: [../strangler-fig-program/references/pattern-catalog.md, ../strangler-fig-program/references/templates.md]
---

# Strangler Transitional Architecture — Facade, ACL & Data Sync

## Contract
- **Input:** the seam map from `legacy-seam-mapping` (or an equivalent description of entry points and data ownership), plus the target platform.
- **Output:** a transition design at `output/<YYYYMMDD>-<slug>-transition-architecture.md` (sections per [templates.md](../strangler-fig-program/references/templates.md) §4): a C4 container view (Mermaid) showing legacy, new and scaffolding; one ADR each for interception, anti-corruption layer and data sync; and a scaffolding register (component · purpose · run cost · owner · removal trigger).
- **Allowed tools/artifacts:** conversation, seam map, architecture docs; hand target-platform design to `cloud-architecture`.
- **Done when:** every seam in scope has an interception mechanism; every data entity the first slices touch has exactly one system of record per phase; every scaffolding component has a removal trigger; and the verifier pass (step 6) records PASS.

## Triggers/Context
- Step 4 of `strangler-fig-program`, after the seam map exists. Revisit when a slice needs a seam type the current design doesn't cover.

## Operating principles (enforceable)
1. **Scaffolding is temporary — and costs money.** Every piece gets a removal trigger ("removed when slice N decommissions"), or it becomes permanent legacy of its own.
2. **One system of record per entity, per phase.** At any moment, exactly one system owns the writes for each entity. The others get a synced copy. Write this down as a phase-by-entity table.
3. **No application-level dual writes.** Writing to both systems from the application without a transaction gives silent divergence. Use CDC/outbox or write-through-one-system-plus-sync instead.
4. **The new model doesn't inherit the legacy model.** The anti-corruption layer translates at the boundary. If legacy field names and codes appear in the new domain, the ACL has leaked.
5. **The facade stays dumb.** Routing and translation only, with no business logic, and it ships at 0% diverted before any slice goes live. The facade is scaffolding too. It's removed once the last slice decommissions, or kept on purpose as an adapter for legacy clients, with that recorded in an ADR.
6. **Build the new system to be strangled later.** Clear seams between its own capabilities, so the next migration doesn't start from a monolith again (Azure Architecture Center, 2026 revision).

## Core Blueprint
1. **Pick the interception mechanism per seam** ([pattern-catalog.md](../strangler-fig-program/references/pattern-catalog.md) §2): an HTTP routing facade (reverse proxy/gateway) for web and API traffic; UI composition for screens; event interception for message- and file-driven flows; branch by abstraction for in-process calls with no external seam. Prefer the infrastructure the client already runs (an existing gateway or proxy) over introducing a new product. **Database-centric legacy** (logic in stored procedures, no editable app layer): intercept at the database. Use log-based CDC, or a trigger/outbox that emits events to the new services, so the legacy application code doesn't change.
2. **Design the anti-corruption layer.** For each slice boundary: the new domain model, the translation to and from legacy (codes, IDs, status machines), and where it runs — in the new service's adapter, not in the facade. Name the legacy concepts that are deliberately *not* carried over.
3. **Choose the data-sync approach per entity** and fill in the phase-by-entity ownership table:
   - **Legacy stays the system of record, new reads a copy:** CDC or replication from legacy → new. This is the default for early slices.
   - **Ownership flips to the new system:** the new system writes, and CDC/outbox carries changes back to legacy for consumers that haven't moved yet ("legacy mimic").
   - **Retire:** consumers are moved, back-sync is switched off, and the data is archived.
   For each, state the latency tolerance, the reconciliation check (counts and checksums per day) and what happens on sync failure.
4. **Design for rollback.** For each slice, routing back to legacy must be one configuration change, and the data written by the new system while it was live must reach legacy (the back-sync path). If rollback needs a data migration, it isn't a rollback, and the slice needs redesign.
5. **Put the scaffolding in the register.** Facade, ACL adapters, sync jobs and reconciliation jobs, each with run cost, owner and removal trigger. Add the total to the program's dual-run cost.
6. **Verifier pass (separate step).** Check the design against the done-when list and the six principles. Record PASS/FAIL per item, fix and re-check (capped at 2 attempts), and report anything still open.

## Optimizations/Gotchas
- **The facade is a new single point of failure.** It sits on the hot path for 100% of traffic from day one. Give it the availability treatment in `cloud-architecture` (HA, latency budget, observability) before slice 1.
- **IDs are where sync breaks.** Decide the ID mapping strategy (keep legacy IDs, map table, or new IDs with a cross-reference) before writing any sync code.
- **Reconciliation is not optional.** Without a daily reconciliation report, data drift goes undetected until the month-end close finds it.
- **Batch jobs are seams too.** A nightly legacy job that reads tables now owned by the new system will break quietly. List every batch consumer in the ownership table.
