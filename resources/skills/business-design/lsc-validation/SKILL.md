---
id: lsc-validation
aliases: [lsc-validation]
name: "LSC 15 — Validation Canvas"
category: business-design
description: Run the Lean Service Creation "Validation" canvas — define how to validate the value proposition, the customer group and the business model, record results and conclusions (segment size, price in euros), plot each on an evidence-versus-direction chart, and give a YES / ITERATE / NO verdict.
triggers: [validation canvas, LSC validation, validate the concept, don't assume validate, value proposition validated, customer group validated, business model validated, ready to pay, large enough user base, solid evidence, needs more validation, validation verdict]
tags: [lean-service-creation, lsc, canvas, validation, evidence, gate]
related: ["[[lean-service-creation]]", "[[lsc-concept-evaluation]]", "[[lsc-experimenting]]", "[[lsc-emotional-concept-sheet]]", "[[business-experiment-design]]", "[[assumption-audit]]", "[[lsc-minimum-lovable-product]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 15 — Validation

## Contract
- **Input:** `canvases/08-…`, `09-…` (fake ad), `12-…` (price, market), `14-…` (what is least proven), and the experiment register `canvases/21-experimenting.md`.
- **Output:** `canvases/15-validation.md`: three columns (how to validate · results · conclusion), three plotted positions, and the gate verdict.
- **Allowed tools/artifacts:** real customers and their behaviour, experiment results with raw data, `business-experiment-design`.
- **Done when:** each column has at least one run experiment with pre-set criteria, each conclusion cites `[O]` evidence, positions are plotted with reasons, and the gate line is written.

## Canvas (v3.0.5) — "Don't assume, validate. Do whatever it takes to question your concept."
**How might we validate our:** **VALUE PROPOSITION** · **CUSTOMER GROUP** · **BUSINESS MODEL**. For each: **RESULTS**, **CONCLUSION** (customer group: *What size?*; business model: *How much €?*). Each has a 2×2 chart: vertical SOLID EVIDENCE ↔ NEEDS MORE VALIDATION; horizontal VALUE PROPOSITION DOESN'T WORK ↔ GOOD VALUE PROPOSITION · TOO SMALL SEGMENT ↔ LARGE ENOUGH USER BASE · NOT READY TO PAY ↔ READY TO PAY. **Should we proceed?** NO! — WE HAVE TO ITERATE — YES!

## Core Blueprint
1. **Derive what to validate** from the weakest points in 14 and the assumptions in 21. One method per column minimum; stronger evidence preferred: behaviour and commitment over opinion.
2. **Value proposition.** Test with the main group: comprehension and wanting of the fake ad, a concierge pilot, a prototype used on a real task. Success criteria set first.
3. **Customer group.** Show that the group exists in the size claimed and can be reached: counted from data, screener pass-rates, response to outreach, pipeline conversion.
4. **Business model.** Show people will pay the planned amount: pre-orders, signed LOI, pilot budget, paid pilot, quote acceptance. State the euro figure.
5. **Record results** as raw numbers and quotes with dates, not impressions.
6. **Write conclusions.** Customer group: size with range. Business model: how much € per unit and per year, with n and conversion.
7. **Plot each position** on its chart: horizontal = direction (works vs not), vertical = evidence strength (solid vs needs more). Positions with `[S]`/`[I]` evidence cannot be plotted above the midline. **[house]**
8. **Verdict.** YES: all three upper-right (solid, positive). WE HAVE TO ITERATE: any column below the midline or mixed; name the next experiments in 21. NO: any column solidly negative and not fixable by pivot. Record the gate line; cap three iterations.

## Quality tests
- Each column has at least one executed test with a pre-written criterion.
- Results are numbers or quotes with dates and n.
- Conclusions give a size and a euro figure with range.
- Business-model evidence includes a commitment-grade signal for B2B, or an explicit "none yet, so not YES".
- Plot positions match the evidence tags.

## Agent-augmented variant
Agents may build landing pages, ad variants and analysis scripts and analyse the results (`[S]` for the interpretation, `[O]` for the underlying data). Synthetic respondents never count here (`agent-augmented-discovery`).

## Handbook 2.0 guidance (book, Futurice 2018, paraphrased)
Handbook guidance:
- Do not aim to prove the concept is great. Aim to prove it fails. Be honest with yourself.
- Do not ask for opinions. Measure effects with fake ads, interviews, live landing pages, prototypes, pilots. The best test is when customers give something of value: real money (ten euros, not "would"), a pilot agreement, or contact details for further interviews. Early on, understanding the offer at all can be enough.
- Three plans: value proposition, customer grouping size, willingness to pay. Do not guess willingness to pay; use fake selling and interviews.
- Voting has two dimensions: were the tests extensive enough, and did it validate. Conflicting votes need discussion. Then vote proceed, iterate or kill.
- The old model applies for funding now; in LSC you test your assumptions first.

## Gotchas
- **Polite yes.** Interview enthusiasm is not willingness to pay.
- **Convenience sample.** Test with the main group from 03, not friends.
- **Moving criteria after seeing results.** Criteria are set before the run; changes are logged as such.
- **One test, three conclusions.** Each column needs its own evidence.

## Hand-offs
YES → `lsc-minimum-lovable-product` (16) and `lsc-pitch-creator` (17). ITERATE → `lsc-experimenting` (21). NO → kill note. Method depth: `business-experiment-design`.
