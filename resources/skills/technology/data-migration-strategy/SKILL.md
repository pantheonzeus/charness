---
id: data-migration-strategy
aliases: [data-migration-strategy]
name: "Data Migration — Assess, Tier & Plan (entry point)"
category: technology
description: Entry point for any data migration, from a spreadsheet import to an ERP or mainframe replacement. Scopes what moves and what gets archived or retired, scores complexity on nine dimensions into tiers T1–T4 (the worst dimension sets the tier), picks the strategy (big bang / phased / trickle-CDC / parallel run) from the downtime budget, and writes the migration plan. Routes to mapping, reconciliation and cutover skills with the rigour the tier requires.
triggers: [data migration, migrate data, migrate the database, database migration, move data to, legacy data migration, ERP data migration, SAP data migration, S/4HANA data migration, mainframe data migration, CRM data migration, data conversion, import data into, consolidate databases, platform switch, Oracle to Postgres, schema migration plan, migration strategy, big bang or phased, zero downtime migration, how hard is this migration, migration estimate]
tags: [technology, data-migration, data-engineering, planning, risk]
related: ["[[data-mapping-and-quality]]", "[[migration-reconciliation]]", "[[migration-cutover-runbook]]", "[[cloud-architecture]]", "[[strangler-fig-program]]", "[[strangler-transition-architecture]]", "[[risk-and-mitigation]]", "[[business-case-builder]]", "[[decision-memo]]"]
modules: [file-backed-state, evidence-backed-answering, verifier-separation]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
requires:
  tools: []
  optional: [web_search, uv + duckdb (profiling via data-mapping-and-quality/scripts/profile.py), read-only DB clients]
environment: "Runs anywhere. Read-only access to the source (or an extract) makes the assessment evidence-based. Without it, every volume and quality figure stays tagged as assumed."
references: [references/tiering-and-strategies.md, references/templates.md, references/patterns-and-sources.md]
---

# Data Migration — Assess, Tier & Plan

## Contract
- **Input:** a migration intent (source system(s), target, why, deadline) plus whatever exists: schemas, extracts, volumes, integration lists, downtime constraints, regulation.
- **Output:** a migration plan at `output/<YYYYMMDD>-<slug>-migration-plan.md` following [templates.md](references/templates.md). It contains the business outcome, the scope decision table (migrate / archive / retire per data object), the tier scorecard, the chosen strategy with its rejected alternative, the workstream plan with mock-load count, the RACI with named data owners, a ranked risk list, and the skills to run next. Indexed into `cbrain/notes/Deliverables/` per Charter §4.
- **Allowed tools/artifacts:** conversation, user-supplied schemas and extracts, read-only queries and profiling against the source. Never run writes against a source or production target from this skill.
- **Done when:** every data object in scope has a scope decision and a named business owner; the tier scorecard shows a score with evidence for all nine dimensions; the strategy has a downtime figure and a rollback statement; the tier's minimum controls (table in step 6) are all in the plan; and the verifier pass (step 9) records PASS.

## Triggers/Context
- Any request to move, convert, consolidate or import data between systems, from a one-off CSV import to a multi-wave ERP replacement. Also "how hard / how long is this migration?"
- Infra-only moves (same database, new host or cloud) start in `cloud-architecture` Move mode. Replacing the *application* incrementally (facade, slices, legacy shrinking over months) is a `strangler-fig-program`. That skill owns the program and the per-slice data sync design (`strangler-transition-architecture`). These four skills own each slice's data movement and proof: mapping, reconciliation, bulk load and switchover.
- Load this skill as soon as data has to be transformed, merged, cleansed or verified.
- This skill decides *how much process* the migration needs. A T1 job gets a one-page plan and a reconciliation run. It does not get a programme office.

## Operating principles (enforceable)
1. **The business owns the data. IT owns the pipes.** Every in-scope data object has a named business owner who signs its mapping and its reconciliation result. If no owner can be named, the object is not ready to migrate. Record it as a blocker.
2. **Migrate less.** Default every object to *archive* or *retire*, and promote it to *migrate* only when a live process in the target needs it. History older than the target's operational need goes to a queryable archive. Every row not migrated is a row you don't have to map, cleanse or reconcile.
3. **Profile real data in week 1.** Specifications and data dictionaries describe what the data was meant to be. Volume, quality and complexity scores come from profiling the actual source ([[data-mapping-and-quality]] `profile.py`). Anything not yet profiled is tagged *assumed*.
4. **The worst dimension sets the tier.** Tier = the maximum dimension score, not the average. One hard constraint (zero downtime, regulated audit trail, 40 integrations) makes the whole migration hard.
5. **Every load is repeatable.** The migration is a pipeline that can be re-run from extract to reconciliation without manual steps. Hand-fixing data in the target during a mock load counts as a defect in the pipeline.
6. **Reconciliation defines done.** Acceptance criteria (counts, control totals, field-level match, business-rule tests) and their thresholds are agreed with the data owners *before* the first mock load ([[migration-reconciliation]]). A migration with no reconciliation evidence is not finished.
7. **Rollback is a design input.** The strategy names the point of no return and what reverses each step before it. If there is no rollback, the plan says so explicitly and the go/no-go bar rises accordingly.

## Core Blueprint
Substantive runs (T2+) keep a STATE_ROOT at `output/.runs/<YYYYMMDD>-<slug>-migration/` with `RESPONSE.md` (steps 1–9 as boxes) and `EVIDENCE.md` (every volume, quality figure and constraint, with its source). T1 runs may skip the STATE_ROOT.

1. **Frame the outcome.** One sentence on the business outcome, the hard deadline and its driver (licence expiry, contract end, regulation), and the cost of one hour of downtime and of one wrong record (e.g. a wrong invoice or a wrong dosage). If nobody can name these, stop and ask.
2. **Inventory.** List the sources, data objects (customer, order, asset…), volumes, the inbound and outbound integrations of the source system, and the consumers of the data (reports, downstream systems, regulators). Find the integrations that nobody documented: scheduled jobs, DB links, file drops. Each one is a cutover dependency.
3. **Scope decision table.** For each data object: migrate / archive / retire, with the retention rule and legal basis (GDPR erasure, statutory retention such as German HGB/AO periods), the history cut-off, and the business owner.
4. **Profile and score.** Profile each migrate-object, then score the nine dimensions in [tiering-and-strategies.md](references/tiering-and-strategies.md) (volume, source count, schema distance, transformation logic, data quality, downtime budget, integrations, regulatory/audit, criticality) from 1 to 4. Cite the evidence for each score. Tier = max score.
5. **Choose the strategy.** Use the downtime budget and the tier to choose big bang (offline window), phased by object/site/tenant (waves), trickle with CDC (online sync, short switchover), or parallel run (both systems live, outputs compared). Write it as an ADR with ≥1 rejected alternative, the downtime figure, the point of no return and the rollback path. The decision rules are in [tiering-and-strategies.md](references/tiering-and-strategies.md).
6. **Apply the tier's minimum controls.**

   | Control | T1 Simple | T2 Standard | T3 Complex | T4 Critical |
   |---|---|---|---|---|
   | Mapping spec | inline in plan | spec per table | signed spec per object | signed spec + change control |
   | Profiling | once | once + after cleanse | per mock | per mock, trended |
   | Mock loads before go-live | 1 dry run | ≥1 full | ≥2 full, last one timed | ≥3 full, last = dress rehearsal |
   | Reconciliation | counts + totals | + key diff | + field diff + business rules | + independent verifier + audit evidence pack |
   | Cutover runbook | checklist | timed runbook | timed runbook + go/no-go | + war room, comms, hypercare SLA |
   | Rollback | backup restore | tested restore | rehearsed rollback | rehearsed rollback + parallel-run fallback |
   | Sign-off | requester | data owner | data owners per object | owners + QA/compliance |

7. **Plan the workstreams.** Extract → stage (land raw) → cleanse → transform → load → reconcile, run as one repeatable pipeline. Add the mock-load calendar (each mock gets an entry and exit criterion), the cleansing backlog (source-side fixes before target-side fixes), the source freeze dates (schema and reference data), the integration cutover sequence, and archive/decommission. Effort estimates show their basis (object count × complexity), and every one not derived from profiling is tagged as a bet.
8. **Risks and RACI.** Rank the risks by impact × likelihood, each with an owner and a trigger. Standing risks to check every time: undocumented integrations, key collisions on merge, encoding/collation differences, timezone and DST handling, reference-data drift between mocks, source changes during the project, the load window being too short at production volume, and personal data in non-prod copies. Hand a board-level register to `risk-and-mitigation`.
9. **Verifier pass (separate step).** Re-read the plan against the Contract's done-when list and the tier's control table. Record each item PASS/FAIL in RESPONSE.md. On FAIL, fix and re-check, capped at 2 attempts. Report what stays open instead of hiding it.

**Then route:** mapping and cleansing → [[data-mapping-and-quality]]; acceptance and evidence → [[migration-reconciliation]]; mock loads, cutover, rollback and zero-downtime mechanics → [[migration-cutover-runbook]].

## Optimizations/Gotchas
- **"It's just a copy" is how T3 migrations get scoped as T1.** Merging two sources, or any key re-numbering, is a transformation, so score it as one.
- **Undocumented integrations surface in production.** Before you finish the inventory, check DB links, cron/scheduler jobs, file shares, and the source's access logs for clients nobody mentioned.
- **Reference data drifts.** Country codes, product hierarchies and GL accounts in the target change between mocks. Freeze them and version-stamp each mock load.
- **Non-prod copies leak personal data.** Mock loads with production data need the same access controls as production, or masking. Plan this, don't discover it in an audit.
- **The load window is set by the full production volume, not the mock subset.** Time the last mock at full volume. Extrapolating from 10% misses index rebuilds, log growth and lock contention.
- **Big-bang optimism.** If the downtime budget is shorter than a timed full mock plus reconciliation plus a rollback buffer, big bang is not an option, whatever the plan says.
