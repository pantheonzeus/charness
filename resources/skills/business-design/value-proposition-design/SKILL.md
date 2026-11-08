---
id: value-proposition-design
aliases: [value-proposition-design]
name: "Value Proposition Design — Jobs, Pains, Gains & Fit"
category: business-design
description: Design and pressure-test a value proposition with the Value Proposition Canvas and Jobs-to-be-Done — evidence-ranked customer jobs, pains and gains, a value map that addresses the top ones, an explicit fit check, the switching-cost argument against today's alternative, and a one-line proposition statement.
triggers: [value proposition, value prop, value proposition canvas, VPC, jobs to be done, JTBD, customer jobs, pains and gains, problem solution fit, why would they buy, why would they switch, positioning statement, unique value, offer design]
tags: [business-design, value-proposition, jtbd, strategyzer, fit]
related: ["[[business-design-engagement]]", "[[opportunity-framing]]", "[[business-model-design]]", "[[customer-segmentation]]", "[[business-experiment-design]]", "[[agent-augmented-discovery]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
---

# Value Proposition Design — Jobs, Pains, Gains & Fit

## Contract
- **Input:** a segment (from `opportunity-framing` or `strategy/customer-segmentation`) plus research material: interviews, support tickets, sales notes, reviews, or desk research.
- **Output:** one Value Proposition Canvas per segment plus a fit check and a proposition statement (format below), inline or at `output/<YYYYMMDD>-<slug>-value-proposition.md`.
- **Allowed tools/artifacts:** conversation, research files, vault meeting notes, web search for competitor offers.
- **Done when:** every job, pain and gain carries an evidence tag and a rank; every pain reliever and gain creator points to a specific ranked pain/gain; the fit check states which top-3 pains are **not** addressed; and the switching argument names today's alternative and its cost.

## Triggers/Context
Use after the opportunity is framed and before choosing a business model. Re-run whenever interviews or experiments contradict the ranked pains: the canvas is a hypothesis register, not a poster.

## Core Blueprint
1. **One segment per canvas.** Two segments with different jobs = two canvases. Multi-sided businesses need one per side (hand off to `ecosystem-platform-design`).
2. **Customer profile.**
   - *Jobs*: functional, social, emotional; plus supporting jobs (buyer, co-creator, transferrer). Phrase as verb + object + context.
   - *Pains*: undesired outcomes, obstacles, risks. Make them concrete and measurable ("loses 2 days per quote", not "slow").
   - *Gains*: required, expected, desired, unexpected.
   - Rank each list by importance **to the customer**; tag evidence `observed` (interview, data), `synthetic`, or `inferred`.
3. **Today's alternative.** What do they do now (incl. "nothing" and spreadsheets)? What does it cost them in money, time and risk? This is the real competitor.
4. **Value map.** Products/services; pain relievers and gain creators, each linked to a ranked pain/gain by id. Anything that links to nothing is a feature to cut.
5. **Fit check.** Score coverage of the top-3 pains and top-3 gains. State fit level honestly: *problem–solution fit* (on paper, evidence of the problem), *product–market fit* (evidence customers want **this** offer), *business-model fit* (evidence it scales profitably; only after `viability-model`).
6. **Switching argument.** Benefit of switching − (switching cost + perceived risk) must be clearly positive for the buyer, and for B2B for the **economic buyer**, not only the user.
7. **Proposition statement.** "For <segment> who <job/pain>, <offer> is a <category> that <key benefit>; unlike <alternative>, it <differentiator>." Write three variants and pick one for testing.
8. **Hand off the riskiest links** (pain ranks with only `inferred` evidence, untested relievers) to `business-experiment-design`.

## Output Format
```markdown
# Value Proposition — <segment>
## Customer profile
| id | Type | Statement | Rank | Evidence tag · source |
|---|---|---|---|---|
| J1 | Job (functional) | | | |
| P1 | Pain | | | |
| G1 | Gain | | | |
## Today's alternative & its cost
## Value map
| Element | Type (product / reliever / creator) | Addresses (ids) |
|---|---|---|
## Fit check
Top pains covered: P1 ✓, P2 ✓, P3 ✗ (why) · Fit level: problem–solution / product–market / business-model
## Proposition statement (chosen + 2 alternatives)
## Hypotheses to test
```

## Optimizations/Gotchas
- **B2B has two profiles.** User and economic buyer have different pains; a proposition that delights users but saves the CFO nothing stalls in procurement.
- **Rank by customer importance, not by what we can solve.** Reordering pains to match our solution is the most common self-deception in this canvas.
- **Feature lists are not value maps.** Every reliever names the pain it kills.
- **Synthetic personas may generate candidate jobs/pains and objections, never ranks.** Ranks need real people.

## Sources
Strategyzer Value Proposition Canvas (jobs/pains/gains, fit); Osterwalder et al., *Value Proposition Design* (2014); Kromatic on synthetic personas (generate objections, don't validate). See [Sources](../_category.md).
