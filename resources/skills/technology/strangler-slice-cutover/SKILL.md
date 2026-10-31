---
id: strangler-slice-cutover
aliases: [strangler-slice-cutover]
name: "Strangler Slice Cutover & Legacy Decommission"
category: technology
description: Take one Strangler Fig slice from built to legacy-retired — readiness gate, shadow/parallel run with a parity threshold, canary ramp with rollback triggers, full cutover, then the decommission checklist (switch off, archive, remove scaffolding, cut the cost) so the legacy actually shrinks.
triggers: [slice cutover, go-live slice, parallel run, shadow traffic, dark launch, canary release, traffic ramp, rollback plan, cutover plan, decommission legacy, switch off legacy, retire legacy module, legacy sunset]
tags: [technology, modernization, legacy, strangler-fig, release, decommission]
related: ["[[strangler-fig-program]]", "[[strangler-transition-architecture]]", "[[legacy-seam-mapping]]", "[[value-realization]]"]
modules: [file-backed-state, verifier-separation]
status: active
version: 2
created: 2026-10-10
updated: 2026-10-10
environment: "Produces the plan and the gate verdicts; the client's teams execute the traffic changes. Runs anywhere, and works best with access to the facade's routing config and production telemetry for the parity and ramp gates."
references: [../strangler-fig-program/references/templates.md]
---

# Strangler Slice Cutover & Legacy Decommission

## Contract
- **Input:** one slice from the program register (its outcome, owner and decommission criterion) and the transition design for its seam and data.
- **Output:** a cutover runbook at `output/<YYYYMMDD>-<slug>-slice-<n>-cutover.md` (sections per [templates.md](../strangler-fig-program/references/templates.md) §5), the gate verdicts recorded in the STATE_ROOT, and an updated row in the slice register.
- **Allowed tools/artifacts:** runbook, telemetry and reconciliation reports, the facade's routing config (read). Traffic changes are made by the client's operators, never by this skill.
- **Done when:** all four gates are recorded PASS (or the slice is rolled back with the reason logged), the legacy path for the slice is switched off, its scaffolding is removed or re-dated, and the register shows legacy cost removed.

## Triggers/Context
- Step 6 of `strangler-fig-program`, once per slice. Also for a stalled slice: new system live, legacy still running.

## Core Blueprint
STATE_ROOT: `output/.runs/<YYYYMMDD>-<slug>-slice-<n>/`, with `RESPONSE.md` holding gates G1–G4 as boxes and `EVIDENCE.md` holding the metrics behind each verdict.

1. **G1 — Readiness.** The slice outcome and dropped-features list are signed off by the business owner. Observability for both paths is live (rate, errors, latency, business KPIs). Rollback is one routing change and has been rehearsed. Reconciliation runs daily. The on-call owner is named. Every item needs evidence, not a "yes".
2. **G2 — Parity (shadow / parallel run).** Mirror real traffic to the new path, or run both on the same inputs, and compare the outputs. Set the parity threshold *before* the run (e.g. ≥99.9% identical results on N days of traffic, with every difference explained). Classify each difference: new-system bug, legacy bug being fixed deliberately, or accepted change. Unexplained differences block the gate.
3. **G3 — Canary ramp.** Divert traffic in steps (e.g. 1% → 10% → 50% → 100%, or by tenant/region/user cohort). Each step has a minimum soak time and **pre-agreed rollback triggers** (error rate, latency p95, a business KPI drop, reconciliation drift). Hitting a trigger means rolling back first and discussing afterwards.
4. **G4 — Decommission.** After a stability period at 100% (agree it up front — typically one full business cycle, including a month-end if finance-relevant), run the checklist: switch off the legacy entry points, stop the back-sync, archive the data with its retention rules, remove the code paths and scaffolding, cancel the licences and infrastructure, and update the documentation and runbooks. Record the run cost actually removed. **Order matters:** until the legacy tables, stored procedures and sync jobs are dropped, rollback is still a routing change plus back-sync. Once they're dropped, rollback means restoring objects and replaying changes. So dropping legacy data objects is the deliberate last step, after the stability period and a final reconciliation PASS (Azure Architecture Center, 2026 revision).
5. **Update the register.** Status, % diverted, legacy cost removed, and lessons for the next slice. Hand outcome tracking to `value-realization` when the program reports benefits upward.

## Optimizations/Gotchas
- **Skipping G4 is the most expensive mistake in the pattern.** "We'll switch it off later" produces the zombie legacy that doubles run cost. The slice is not done until G4 passes.
- **Side-effecting calls can't be naively shadowed.** For payments, emails and external postings, shadow in compare-only mode with the new path's side effects stubbed, or the customer gets charged twice.
- **Legacy bugs show up as parity failures.** Decide case by case whether to replicate the bug (rarely) or fix it with the business owner's sign-off. Never decide this silently.
- **Business cycles hide edge cases.** Month-end, year-end and seasonal peaks exercise logic that two weeks of traffic never touch. Time the stability period accordingly.
- **Rollback rehearsed means actually executed in a non-prod or low-risk window**, not described in a document.
