---
id: lsc-feasibility-study
aliases: [lsc-feasibility-study]
name: "LSC 13 — Feasibility Study Canvas"
category: business-design
description: Run the Lean Service Creation "Feasibility Study" — find the biggest implementation issues, define how to validate each and record findings, look ahead with "Back to the future", and cut project risk by simplifying the service while checking the effect on the value proposition.
triggers: [feasibility study canvas, LSC feasibility, can we build this, biggest implementation issues, risky tech dependency, simplify the service, back to the future canvas, technical feasibility of the concept, implementation risks, organisational blockers, spike before build]
tags: [lean-service-creation, lsc, canvas, feasibility, risk, technology]
related: ["[[lean-service-creation]]", "[[lsc-customer-engagement]]", "[[lsc-business-model-market-size]]", "[[lsc-concept-evaluation]]", "[[lsc-minimum-lovable-product]]", "[[cloud-architecture]]", "[[assumption-audit]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 13 — Feasibility Study

## Contract
- **Input:** `canvases/08-…`, `11-…` (activities, resources, partners), `12-…` (cost drivers).
- **Output:** `canvases/13-feasibility-study.md`: up to four issue columns (issue · how to validate · findings & solution), the future outlook, the simplified service and its value-proposition impact.
- **Allowed tools/artifacts:** conversation with engineering and operations, spikes and prototypes, `technology/cloud-architecture`, vendor documentation (cited).
- **Done when:** each issue has a validation with an owner and date, at least the top issue has findings from a real spike or test, and the simplification option is written with its effect on the value proposition.

## Canvas (v3.0.5) — "To make sure we can make this happen"
**Biggest implementation issues?** Four columns, each: **Potential issue** (What is the most risky tech dependency? What in our organisation is preventing this from happening? What is risky in building it?) → **How to validate** (How can we test this and eliminate the risk?) → **Findings & solution** (What did we learn and change?).
**Back to the future:** *What will this concept look like in the future?* · *How to take advantage of it? How to keep an eye on it?*
**Reduce project risks by simplifying the service:** *How could we simplify the service to make it easier to build:* · *How would this change affect the value proposition?*

## Core Blueprint
1. **Scan three risk sources** for each step of "how it works" in 08 and each activity in 11: technology dependencies, organisational blockers (people, politics, process, legal, security), build risk (effort, skills, integration).
2. **Pick the four most dangerous** by impact × uncertainty. Write each as a falsifiable statement: "We cannot <do X> at <acceptable cost/time> because <Y>".
3. **Define validation.** The cheapest test that could prove the statement false: a technical spike, a data access request, a conversation with legal or security, a vendor proof-of-concept. Name owner, date, pass criterion.
4. **Run, then record findings and solution.** What happened, what changes in the concept or the plan. Evidence tagged; a spike result is `[O]`, an engineer's opinion `[I]`.
5. **Back to the future.** Name the technologies, regulations and market shifts that will change the concept in 2–5 years, how to benefit (design hooks) and the watchlist with a review date. **[house]** For AI-based concepts name the model-capability and cost curve assumption explicitly.
6. **Simplify.** List what could be removed or replaced by a simpler, proven approach: boring technology first, buy before build, manual back-end ("concierge") before automation. Then state what this does to the value proposition: unchanged, reduced (how much), or still lovable.
7. **Decision.** If the top issue remains unresolved, the verdict feeds 14 as "Implementation: complex" and the simplification becomes the working scope for 16.

## Quality tests
- Each issue is falsifiable, not a theme ("security").
- Each validation has owner, date, pass criterion, and cost.
- Top issue has an `[O]` result or a dated plan.
- Simplification states what is cut, and what it costs in value.
- Future outlook has a review date.

## Agent-augmented variant
Agents can map dependency risks from architecture notes and prepare spike plans (`[S]`). For agent-based services, run a capability spike: a small eval set drawn from real cases, with a pass threshold set before running (`agentic-service-evaluation`). Reported accuracy without the eval set is not evidence.

## Gotchas
- **Technology-only view.** Organisation and legal blockers kill more concepts than code.
- **Spike scope creep.** A spike answers one question in days, not weeks.
- **Resume-driven choices.** The burden of proof is on the exotic option (persona rule: boring technology wins).
- **Vendor demo as proof.** Test on your own data and constraints.

## Hand-offs
Next: `lsc-concept-evaluation` (14). Simplified scope feeds `lsc-minimum-lovable-product` (16). Technical depth: `technology/cloud-architecture`.
