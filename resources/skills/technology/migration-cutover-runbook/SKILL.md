---
id: migration-cutover-runbook
aliases: [migration-cutover-runbook]
name: "Data Migration — Mock Loads, Cutover & Rollback"
category: technology
description: Take a migration from rehearsal to go-live. Run timed mock loads with entry and exit criteria, write a minute-level cutover runbook with a single point of no return, a measurable go/no-go and a rehearsed rollback, and choose the zero-downtime mechanics (CDC with a short switchover, expand/contract, dual-write with shadow reads) when the downtime budget requires them. Then hypercare and decommission. Scales from a T1 checklist to a T4 war-room cutover.
triggers: [data migration cutover, migration cutover plan, migration go-live, migration runbook, mock load, dress rehearsal, go no-go migration, migration rollback, point of no return, zero downtime migration, online migration, CDC migration switchover, expand and contract, schema migration live database, backfill, shadow reads, data switchover, hypercare, freeze period, delta load, migration weekend]
tags: [technology, data-migration, operations, release, reliability]
related: ["[[data-migration-strategy]]", "[[data-mapping-and-quality]]", "[[migration-reconciliation]]", "[[cloud-architecture]]", "[[strangler-slice-cutover]]", "[[strangler-transition-architecture]]"]
modules: [file-backed-state, verifier-separation]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
requires:
  tools: []
  optional: [CDC tooling (Debezium, AWS DMS, native logical replication), online schema-change tools (gh-ost, pg logical replication)]
environment: "Planning runs anywhere. Execution happens in the client's environment under their change management, and this skill never runs production commands itself."
references: [references/runbook-and-zero-downtime.md]
---

# Data Migration — Mock Loads, Cutover & Rollback

## Contract
- **Input:** the plan and strategy ([[data-migration-strategy]]), the frozen mapping specs, the reconciliation acceptance criteria ([[migration-reconciliation]]), and timings from mock loads.
- **Output:** `output/<YYYYMMDD>-<slug>/cutover-runbook.md` per [runbook-and-zero-downtime.md](references/runbook-and-zero-downtime.md): pre-cutover checklist, timed step table (owner · start · duration · verification · rollback step), point of no return, go/no-go criteria, comms plan, hypercare plan, and decommission checklist. For each mock, an entry/exit card in `output/<YYYYMMDD>-<slug>/mock<n>.md`.
- **Allowed tools/artifacts:** planning documents, mock-load logs and timings, and the conversation. Never execute steps against production. The runbook is executed by named owners.
- **Done when:** every runbook step has an owner, a duration measured in a mock (not estimated), a verification and a rollback action (or "past PNR"); the total duration plus a ≥30% buffer fits the downtime budget; go/no-go criteria are measurable; the rollback has been rehearsed at least once (T3+); and hypercare exit criteria are defined.

## Triggers/Context
- From the first mock-load plan through go-live and decommission.
- When the downtime budget is minutes or zero, this skill owns the online-migration mechanics (CDC bulk-plus-catch-up, expand/contract) and their switchover.
- Boundary: a Strangler Fig *slice* go-live (traffic ramp, canary, retiring a legacy module) is `strangler-slice-cutover`. That skill calls this one when the slice moves data in bulk.

## Operating principles (enforceable)
1. **Rehearse until it's boring.** The cutover is the last mock with the business watching. The number of full mocks follows the tier (≥1 T2, ≥2 T3, ≥3 T4). The final one is a dress rehearsal at production volume, timed end-to-end, run from the runbook as written by the people who will run it.
2. **Durations are measured, not estimated.** Every runbook duration comes from a mock log. Unmeasured steps are flagged in red and block the go/no-go.
3. **One point of no return, stated in minutes.** Before the PNR, rollback means "re-point to source" and is cheap. After it (the target takes writes that the source doesn't have), rollback means reverse migration or forward-fix. The runbook says which one, and the go/no-go happens immediately before the PNR.
4. **Go/no-go is a measurement, not a mood.** Criteria are thresholds: reconciliation verdict PASS per object, business-rule tests green, elapsed time ≤ plan + buffer, no open Sev-1 defects, smoke tests passed. Anyone on the decision list can call no-go and that call stands.
5. **Freeze before you cut.** Source schema, reference data and code freeze dates come before the dress rehearsal and hold through cutover. A change during the freeze resets the rehearsal clock.
6. **Rollback is rehearsed, not written.** In T3+ the rollback path is executed at least once in a mock and timed. An untested rollback counts as no rollback, and the plan must say so.

## Core Blueprint
1. **Mock calendar.** For each mock: entry criteria (spec version, reference data version, extract time), the run (timed per stage), exit criteria (reconciliation verdicts, defect counts, timing vs window). Each mock produces a timing table, and the runbook gets updated from it.
2. **Pick the switchover mechanics** from the strategy (see [runbook-and-zero-downtime.md](references/runbook-and-zero-downtime.md)):
   - **Offline (big bang / wave):** freeze → final extract → load → reconcile → go/no-go → switch.
   - **CDC trickle:** initial load → CDC catch-up with lag monitored → reconcile at a recorded position → brief write-freeze → drain lag to zero → final reconcile → switch → optionally reverse CDC (target → source) as the rollback path.
   - **In-place schema change:** expand (add new structure) → dual-write or trigger/CDC sync → backfill in idempotent batches → verify with shadow reads → move reads → move writes → contract (drop old) after a soak period.
3. **Write the timed runbook:** pre-cutover T-14d…T-0 checklist (freeze, backups verified by test restore, access, comms, integration owners on call), then the step table with a T+hh:mm start, owner, duration from the mock, verification and rollback per step. Include the integration cutover order (stop inbound feeds first, re-point outbound last) and the DNS/connection-string changes.
4. **Go/no-go gate** right before the PNR: run the criteria, record each value, and record the decision with the names of the decision-makers.
5. **Comms plan:** who is told what at freeze, start, go/no-go, completion and rollback, including the user-facing message and the support desk script.
6. **Hypercare:** duration (T1 days → T4 ≥1 business cycle, e.g. a month-end close), daily defect triage, delta-load procedure for stragglers, and exit criteria (no Sev-1/2 for N days, business-cycle outputs accepted).
7. **Decommission:** source made read-only on day 1, archive extracted per the scope table, integrations removed, licences and infra cancelled on a date, and the crosswalk tables retained. Without a date, legacy systems keep running and keep costing.
8. **Verifier pass:** check the runbook against the Contract's done-when list (owners, measured durations, buffer, PNR, rollback rehearsal, hypercare exit). Record PASS/FAIL per item, fix and re-check up to 2 times, and report what stays open.

## Optimizations/Gotchas
- **The final extract is slower than mocks.** Production has more data, more locks and live users until the freeze. Budget against the dress-rehearsal timing at full volume, plus the buffer.
- **Sequences and identity columns.** After a load with explicit IDs, reset sequences above the max key, or the first insert in production collides.
- **Triggers, constraints and indexes.** Disabling them for load speed is fine. Re-enabling them (and validating constraints) takes time, so measure it in the mock. Forgetting it is a silent integrity hole.
- **Dual writes.** Across two systems, never write to both from the application: a partial failure diverges silently. Use CDC/outbox from the system of record (same rule as `strangler-transition-architecture`). Within one database (expand/contract), write old and new structures in the same transaction, and keep reconciling until the contract step.
- **CDC lag at switchover.** The write-freeze has to last as long as draining the lag to zero, so monitor lag for days before cutover and rehearse the drain.
- **Caches and search indexes** downstream of the target need a rebuild or warm-up step in the runbook.
- **Time zones and the clock.** Schedule the cutover away from DST changes, month-end and batch windows, and confirm with finance and operations calendars.
