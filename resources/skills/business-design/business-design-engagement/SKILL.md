---
id: business-design-engagement
aliases: [business-design-engagement]
name: "Business Design Engagement — Viability Lead, Frame → Test → Launch"
category: business-design
description: The business designer's end-to-end engagement router — owns the viability lens of a design team, runs a phased frame → understand → design → test → launch-plan arc with explicit continue/pivot/kill gates, and dispatches each phase to the business-design, strategy and service-design skills that own it (classic and agent-augmented).
triggers: [business design, business designer, act as business designer, business design engagement, new offering, new business, venture building, innovation project, desirability feasibility viability, DVF, is this viable, design a new service business, lean service creation, LSC, from idea to launch]
tags: [business-design, router, viability, lean-service-creation, innovation]
related: ["[[opportunity-framing]]", "[[value-proposition-design]]", "[[business-model-design]]", "[[viability-model]]", "[[business-experiment-design]]", "[[ecosystem-platform-design]]", "[[servitization-model-design]]", "[[ai-native-business-model]]", "[[ai-opportunity-portfolio]]", "[[agent-augmented-discovery]]", "[[lean-service-creation]]", "[[assumption-audit]]", "[[business-case-builder]]", "[[narrative-builder]]", "[[service-design-engagement]]", "[[service-discovery-research]]", "[[service-codesign-facilitation]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
---

# Business Design Engagement — Viability Lead, Frame → Test → Launch

## Contract
- **Input:** an idea, a growth ambition, a client brief, or a stuck initiative — plus whatever exists already (research, numbers, canvases, constraints).
- **Output:** a STATE_ROOT at `output/.runs/<YYYYMMDD>-<slug>-bd/` holding `RESPONSE.md` (the phase spine below), `EVIDENCE.md` (every claim tagged `observed` / `synthetic` / `inferred` with source), and one artifact per phase from the dispatched skill; a final **Gate Memo** at `output/<YYYYMMDD>-<slug>-business-design.md`, indexed into `cbrain/notes/Deliverables/` (Charter §4).
- **Allowed tools/artifacts:** the dispatched skills, web search, vault notes, user-supplied data, child agents per Charter §5.
- **Done when:** every phase in the spine is `[x]` **or** explicitly skipped with a reason, every gate has a recorded verdict (continue / pivot / kill) with the evidence that drove it, and the Gate Memo names the single riskiest open assumption.

## Triggers/Context
The business designer is the **viability owner** in a multidisciplinary team: the person who makes sure a desirable, buildable concept also makes money, fits the client's strategy, and can be taken to market (IDEO, Fjord and Futurice role definitions — see Sources). Use this skill when the ask is "design / shape / validate a new offering or business", not when it is a single analytical question — for those, go straight to the specific skill.

## Core Blueprint
Open the STATE_ROOT first and copy this spine into `RESPONSE.md`. Each phase lists the owning skill; open its `SKILL.md` and follow it.

| # | Phase | Question it answers | Owning skill(s) | Gate |
|---|---|---|---|---|
| 1 | Frame | What problem, for whom, worth how much to the client? | `opportunity-framing` | Is the opportunity big enough and strategically ours? |
| 2 | Understand | What do customers actually do, need, pay for today? | `service-design/service-discovery-research` (real people) + `agent-augmented-discovery` (desk + synthetic pre-work) + `strategy/market-mapping`, `strategy/customer-segmentation` | Is the problem real and painful in a reachable segment? |
| 3 | Design value | What do we offer and why would they switch? | `value-proposition-design` | Problem–solution fit on paper |
| 4 | Design the business | How do we create, deliver, capture value? | `business-model-design`; branch: `servitization-model-design` (physical assets), `ecosystem-platform-design` (multi-sided), `ai-native-business-model` (agents in the value chain) | ≥3 alternatives compared, one chosen with reasons |
| 5 | Prove the math | Does it make money, under which assumptions? | `viability-model` → `strategy/pricing-strategy` | Break-even reachable inside the client's horizon? |
| 6 | Test | Which assumption kills us first, and what's the cheapest evidence? | `strategy/assumption-audit` → `business-experiment-design` | Riskiest assumption supported by ≥ medium evidence |
| 7 | Plan the launch | What's the pilot, the KPIs, the investment ask? | `strategy/kpi-architect`, `strategy/business-case-builder`, `strategy/narrative-builder` | Sponsor commits budget for the next stage |

**Gate rule.** At each gate write one line into `RESPONSE.md`: `Gate n: CONTINUE | PIVOT (what changes) | KILL — evidence: <EVIDENCE.md ids>`. A gate with only `synthetic` or `inferred` evidence may CONTINUE only to a test phase, never to Plan the launch. This mirrors Futurice Lean Service Creation's continue/pivot/kill checkpoints.

**Agentic variant (when the user asks for speed or scale).** Run phases 2, 4 and 5 as file-backed child agents (Charter §5): one research child per segment, one child per business-model alternative, one red-team child that attacks the chosen model. The parent keeps every gate decision; children never decide a gate.

**Workshop variant.** When the work happens with a client in the room, produce each phase's canvas as a fill-in template plus a pre-filled "strawman" from desk research, so the session edits rather than starts blank. Co-design facilitation itself belongs to `service-design/service-codesign-facilitation`.

## Output Format (Gate Memo)
```markdown
# <Concept> — Business Design Gate Memo (<date>)
**Recommendation:** CONTINUE / PIVOT / KILL — one sentence why.
**Riskiest open assumption:** <assumption> — next test: <experiment>, cost <€>, decision date <date>.

| Lens | Verdict | Strongest evidence (tag) | Biggest gap |
|---|---|---|---|
| Desirability | | | |
| Viability | | | |
| Feasibility | | | |

## Business model (one paragraph + canvas link)
## Numbers that matter (3–5, each with source or assumption id)
## Gate log (phase · verdict · evidence ids)
## Ask (budget, people, decision needed, by when)
```

## Optimizations/Gotchas
- **Viability is your job; don't let the team defer it to "later".** A concept that reaches phase 6 without a `viability-model` is not ready to test; you'd be testing desirability of something nobody can sell at a profit.
- **Never let synthetic evidence pass a launch gate.** Synthetic persona output and LLM desk summaries are tagged `synthetic`; they shape hypotheses, they don't validate them (see `agent-augmented-discovery`).
- **Kill is a success outcome.** Report a killed concept with the evidence and the money saved; never quietly re-scope to avoid saying it.
- **Don't duplicate strategy skills.** Board-grade ROI/NPV is `business-case-builder`; this skill's own numbers stay at concept-stage ranges (`viability-model`).
- **Persona lens holds:** lead every artifact with the business outcome, then product, then technology.

## Sources
IDEO Senior Business Designer posting (viability of concepts, growth opportunities, get offers to market); Fjord/Accenture Business Design Director posting (design + strategy fused at strategic, operational and organizational level); Futurice "Meet Tuomas, Senior Business Designer" (bridges business, technology and design); Futurice Lean Service Creation (canvases with continue/pivot/kill checkpoints). Full citations: [business-design/_category.md → Sources](../_category.md).
