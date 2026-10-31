---
id: strangler-fig-program
aliases: [strangler-fig-program]
name: "Strangler Fig Program — Legacy Modernization Orchestrator"
category: technology
description: Run a legacy modernization as a Strangler Fig program at CTO level — decide strangle vs rewrite vs retain, tie every slice to a business outcome, sequence the phases (seam map → transitional architecture → slice cutovers → decommission), and track the program on one register whose headline metric is legacy cost and traffic actually retired.
triggers: [strangler fig, strangler pattern, strangle the monolith, legacy modernization, legacy modernisation, replace the legacy system, mainframe exit, modernize the monolith, big bang rewrite, rewrite vs refactor, incremental migration, legacy displacement, application modernization]
tags: [technology, architecture, modernization, legacy, migration, strangler-fig]
related: ["[[legacy-seam-mapping]]", "[[strangler-transition-architecture]]", "[[strangler-slice-cutover]]", "[[cloud-architecture]]", "[[business-case-builder]]", "[[transformation-roadmap]]", "[[risk-and-mitigation]]", "[[decision-memo]]", "[[value-realization]]"]
modules: [file-backed-state, evidence-backed-answering, verifier-separation]
status: active
version: 2
created: 2026-10-10
updated: 2026-10-10
environment: "Runs anywhere. Works from conversation, architecture docs, code/repo access and telemetry when available; degrades to an assumption-tagged plan without them."
references: [references/pattern-catalog.md, references/templates.md]
---

# Strangler Fig Program — Legacy Modernization Orchestrator

## Contract
- **Input:** a legacy system (name, what it does for the business, rough size, who runs it), the trigger for modernizing (cost, risk, speed, end-of-support, talent), and constraints (budget, deadline, regulation, team).
- **Output:** a program plan at `output/<YYYYMMDD>-<slug>-strangler-program.md` (sections per [templates.md](references/templates.md) §1) plus a living **slice register** at `output/<YYYYMMDD>-<slug>-strangler-register.md` (§2). Index both into `cbrain/notes/Deliverables/` per Charter §4 and link the client's account note.
- **Allowed tools/artifacts:** conversation, client docs, read-only repo/telemetry access, the three phase skills, the strategy skills named under hand-offs. No production changes.
- **Done when:** the strangle/rewrite/retain decision is written with its rejected alternatives; every slice in the register names a business outcome, an owner, and a decommission criterion; the dual-run cost and a strangling deadline are stated; and the verifier pass (step 7) records PASS.

## Triggers/Context
- Anyone asks how to replace, modernize, or escape a legacy system without a big-bang rewrite — or proposes a big-bang rewrite. Also: a strangler effort that is stalled (new system live, old one still running).
- This skill owns the **program**. It routes the detailed work: seam discovery → `legacy-seam-mapping`; facade, anti-corruption layer and data sync → `strangler-transition-architecture`; per-slice go-live and legacy retirement → `strangler-slice-cutover`; target platform design → `cloud-architecture`.
- Business hand-offs: funding → `business-case-builder`; phase plan and PMO → `transformation-roadmap`; risk register → `risk-and-mitigation`; executive go/no-go → `decision-memo`; benefits tracking → `value-realization`.

## Operating principles (enforceable)
1. **Outcome before architecture.** No slice enters the register without a named business outcome (cost removed, lead time cut, risk retired, revenue enabled). "Modernize the stack" is not an outcome.
2. **Strangling is a choice, not a default.** Decide it explicitly against **rewrite** (only for small, well-understood systems) and **retain/encapsulate** (stable, cheap, no change pressure). Write the rejected options down.
3. **No feature parity.** Replicating every legacy feature is the classic program killer. Each slice ships what the business needs today, with an explicit "dropped" list signed off by the business owner.
4. **The target is the simplest thing that works.** A modular monolith is a valid end state. Microservices need the burden of proof that `cloud-architecture` applies.
5. **Dual-run is a tax, so set a deadline.** Running two systems costs real money and attention. State the monthly dual-run cost and a date by which the legacy is switched off. A program with no decommission dates is a migration that never ends.
6. **Progress is measured on the legacy side.** The headline metric is legacy retired (% traffic routed away, capabilities decommissioned, legacy run cost removed). Lines of new code and services launched don't count.
7. **Claims are evidenced.** Dependency, volume and cost figures go through `_shared/evidence-gate.md`: sourced from code, telemetry or invoices, or tagged as inference.
8. **Change the organization, not just the code.** Fowler's 2024 revision makes this one of the four core activities. Build the new system the way it should be run from now on ("Build as You Mean to Continue": CI/CD, tests, observability, teams owning capabilities). If you don't, Conway's law rebuilds the legacy in a new stack. The plan names the practice and team changes, not only the slices.
9. **Use AI to understand the legacy, not to translate it.** AI-assisted reverse engineering (code graph + LLM → capability maps, business rules, specs) is the most proven AI use in modernization. Line-by-line AI translation is weak (non-idiomatic code, legacy design carried over), and it's feature parity by machine. AI output stays tagged as inference until a domain expert or runtime evidence confirms it. Detail is in `legacy-seam-mapping` step 4.

## Core Blueprint
STATE_ROOT: `output/.runs/<YYYYMMDD>-<slug>-strangler/`, with `RESPONSE.md` (steps 1–7 as boxes) and `EVIDENCE.md`. The slice register is the program's durable state across sessions, so reopen it by path at the start of every follow-up run.

1. **Frame the why.** One paragraph: what the legacy does for the business, what it costs per year (run + change + risk), what triggers action now, and what happens if nothing changes in 24 months. If nobody can name the trigger, stop and ask.
2. **Decide the strategy.** Score strangle vs rewrite vs retain/encapsulate vs replace-with-SaaS against size, change pressure, knowledge of the legacy, data entanglement and deadline ([pattern-catalog.md](references/pattern-catalog.md) §1). Record the decision with rejected alternatives. If the answer is not strangle, stop here and hand the decision to `decision-memo`.
3. **Map seams and sequence slices** → run `legacy-seam-mapping`. The program needs back from it: a capability map, a ranked list of slices, and the first slice chosen as a **thin, valuable, low-coupling** proof of the pattern.
4. **Design the transitional architecture** → run `strangler-transition-architecture`. The program needs back: the interception point (facade/proxy/events), the anti-corruption layer, the data-sync approach, and the cost and removal date of each piece of scaffolding.
5. **Build the program plan and register.** Phases with gates (seam map approved → facade live with 0% diverted → slice 1 live → slice 1 legacy decommissioned → repeat → **facade removed**, or kept on purpose as an adapter for legacy clients, with that decision recorded). Per slice: outcome, owner, effort band, target date, decommission criterion. Add the dual-run cost, the strangling deadline, the team and practice changes (principle 8), and the top risks (hand the register to `risk-and-mitigation` if it's board-level).
6. **Run slices** → each slice goes through `strangler-slice-cutover` and then updates the register: status, % traffic diverted, legacy cost removed. Review after every slice: did the outcome land, and is the next slice still the right one?
7. **Verifier pass (separate step).** Re-read the plan against the done-when list and the red flags in [pattern-catalog.md](references/pattern-catalog.md) §4. Record PASS/FAIL per item in RESPONSE.md. Fix and re-check, capped at 2 attempts, and report anything still open.

## Optimizations/Gotchas
- **The usual way this fails is the half-strangled zombie:** the new system is live, the legacy can't be switched off, and the run cost has doubled. Steps 5–6 exist to make decommissioning a tracked deliverable, not a hope.
- **The first slice proves the plumbing as well as the feature.** Pick one where the facade, data sync and rollback all get exercised, but the business impact of a bad day is small.
- **Data is the hard part, not code.** If the legacy database is the integration layer for other systems, say so up front. It sets the pace of the whole program.
- **Keep the legacy team in the program.** They hold the undocumented rules. Losing them mid-strangle is a top-3 risk on every register.
- **Treat vendor "years to months" AI claims as a bet to price.** Agentic platforms (e.g. AWS Transform for mainframe, Thoughtworks AI/works) speed up analysis and spec extraction. Both still keep human-in-the-loop validation and position themselves inside an incremental strangler approach, not instead of it. Use their output to speed up step 3. Don't use it to shorten the decommission plan.
- **Re-plan at every slice boundary.** The register is a living document. A slice ranked #4 at kickoff is often #1 or dead by slice 3.
