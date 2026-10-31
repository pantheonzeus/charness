# Strangler Fig — Templates

Output skeletons for the four Strangler Fig skills. Keep each section short, and leave a section out only with a written reason.

## §1 Program plan — `output/<YYYYMMDD>-<slug>-strangler-program.md`

```markdown
# <System> Modernization — Strangler Fig Program
## Executive summary        (3–4 bullets: outcome, strategy, first slice, deadline + dual-run cost)
## Why now                  (business role of the system, annual cost run+change+risk, trigger, cost of doing nothing)
## Strategy decision        (strangle / rewrite / retain / SaaS — chosen + rejected, with reasons; mixed per capability if applicable)
## Target end state         (modular monolith / services / SaaS mix — link the cloud-architecture doc)
## Slice sequence           (top slices from the seam map, each with its outcome — full detail in the register)
## Transitional architecture (summary + link; scaffolding total cost and removal dates)
## Phases & gates           (seam map approved → facade live at 0% → slice 1 live → slice 1 decommissioned → … → facade removed / kept as adapter by ADR)
## Economics                (dual-run cost / month, legacy cost by slice, strangling deadline, funding ask → business-case-builder)
## Team, practices & governance (owners, legacy team retention, target practices + team-per-capability changes, decision rights, cadence)
## Top risks                (≤7, each with owner + mitigation)
## Open questions / assumptions (tagged inference)
```

## §2 Slice register — `output/<YYYYMMDD>-<slug>-strangler-register.md`

Headline at top: **Legacy retired: X% of traffic · Y of Z capabilities decommissioned · €N/yr legacy run cost removed · deadline <date>.**

| # | Slice (capability) | Business outcome | Owner | Seam / interception | Data SoR phase | Status | % diverted | Decommission criterion | Legacy cost removed | Target date |
|---|---|---|---|---|---|---|---|---|---|---|

Status values: `planned` · `building` · `G1` · `G2 parity` · `G3 ramp` · `100% live` · `decommissioned` · `rolled back` · `dropped`.

## §3 Seam map — `output/<YYYYMMDD>-<slug>-seam-map.md`

```markdown
## Comprehension method (interviews / Event Storming / telemetry / AI-assisted code graph — and how AI output was validated)
## Capability map      (capability · business owner · code areas · entry points · volume/day · change freq — source per row)
## Seam inventory      (entry point · seam type (pattern-catalog §2) · interceptable Y/N · notes)
## Data ownership      (capability × table matrix R/W/RW; shared-write tables flagged; external DB readers listed)
## Slice scoring       (slice · value 1–5 · risk 1–5 · coupling 1–5 · priority · evidence)
## Recommended sequence (ordered list; slice 1 with the written reason)
## Unknowns            (item · owner · discovery task · due)
```

## §4 Transition design — `output/<YYYYMMDD>-<slug>-transition-architecture.md`

```markdown
## C4 container view   (Mermaid: legacy, new, facade, ACL, sync, reconciliation; trust boundaries)
## ADR — Interception  (mechanism per seam, rejected alternative, triggering requirement)
## ADR — Anti-corruption layer (new model, translations, legacy concepts deliberately dropped)
## ADR — Data sync     (approach per entity, latency tolerance, reconciliation, failure behaviour)
## Ownership by phase  (entity × phase → system of record)
## Rollback path       (per slice: routing change + back-sync of data written while live)
## Scaffolding register (component · purpose · run cost/month · owner · removal trigger)
```

## §5 Slice cutover runbook — `output/<YYYYMMDD>-<slug>-slice-<n>-cutover.md`

```markdown
## Slice summary       (outcome, owner, dropped features signed off by, decommission criterion)
## G1 Readiness        (checklist with evidence links; rollback rehearsal date)
## G2 Parity           (method shadow/parallel, threshold set in advance, run window, diff classification table)
## G3 Ramp             (steps · cohort · soak time · rollback triggers with numeric thresholds)
## G4 Decommission     (stability period; switch-off, back-sync stop, archive + retention, code/scaffold removal, licences/infra cancelled, docs) + cost actually removed
## Gate log            (gate · date · verdict · evidence · decided by)
## Lessons for next slice
```
