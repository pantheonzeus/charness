---
id: lsc-business-model-market-size
aliases: [lsc-business-model-market-size]
name: "LSC 12 — Business Model & Market Size Canvas"
category: business-design
description: Run the Lean Service Creation "Business Model & Market Size" canvas — who pays whom and how much, revenue model, today's payments and price anchoring, total addressable and potential target market, first-year and first-month sales, cost structure and key EBIT elements — as a high-level business case with ranges and evidence tags.
triggers: [business model and market size, LSC business model, who pays whom, revenue model, price anchoring, total addressable market, TAM, first year sales, cost structure, EBIT drivers, high level business case, concept business case, napkin business model]
tags: [lean-service-creation, lsc, canvas, business-model, market-size, pricing, viability]
related: ["[[lean-service-creation]]", "[[lsc-customer-engagement]]", "[[lsc-concept-evaluation]]", "[[business-model-design]]", "[[viability-model]]", "[[pricing-strategy]]", "[[business-case-builder]]", "[[servitization-model-design]]", "[[ai-native-business-model]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 12 — Business Model & Market Size

## Contract
- **Input:** `canvases/01-…` (success goals), `02-…` (current spend, alternatives), `03-…` (groups), `08-…`, `11-…` (activities, resources, partners).
- **Output:** `canvases/12-business-model-market-size.md` with ranges (low / base / high), each number tagged and sourced, plus the two drivers that decide viability.
- **Allowed tools/artifacts:** upstream canvases, market data (cited), the client's own price and cost data, `viability-model` for the money model, `pricing-strategy` for price levels.
- **Done when:** every field has a value or range with a tag, market size is built bottom-up, price is anchored to today's spend, the cost structure reflects the activities from 11, and the viability drivers are named.

## Canvas (v3.0.5) — "Thinking through the high level business case."
**Who pays whom? How much?** · **What is the revenue model?** · **How are customers paying today? How much?** · **Where and how do you anchor price perception?** · **Total addressable market** · **Potential target market** · **1st year sales** · **Plan for 1st month sales** · **Cost structure?** · **Key elements for EBIT?**

## Core Blueprint
1. **Money flow.** Draw who pays whom: customer, payer (may differ), partner shares, platform fees. Write amounts per unit and per year as ranges.
2. **Revenue model.** Choose one primary mechanism (one-off, subscription, usage, outcome, licence, transaction fee, hybrid) and justify against how customers buy and what value they perceive. For physical-asset concepts consult `servitization-model-design`; for agent-delivered services `ai-native-business-model`.
3. **Today's payment.** What do customers pay now for the alternative from 02 (money, time, risk)? Cite the source or label `[I]`.
4. **Price anchor.** State the reference the customer compares to and why our price looks fair against it (cost of the problem, price of the status quo, price of a peer). **[house]**
5. **Market size, bottom-up.** TAM = number of potential customers × annual value, from counted units, not "1% of a huge market". Potential target market = the main group from 03 that we can actually reach in the next 12–24 months. Show the multiplication and each factor's source.
6. **First-year sales and first-month plan.** First-year = target market × realistic conversion from 11's weakest transition. First-month = named leads, channels and activities, and the number expected. State ranges.
7. **Cost structure.** List the cost lines driven by the activities, resources and partners in 11, plus cost to serve per customer. Mark fixed vs variable.
8. **Key elements for EBIT.** Identify the two or three drivers that decide whether margin is positive (price, utilisation, conversion, cost per case, inference cost). Run a one-way sensitivity on each. These are the assumptions to test next (21).
9. **Hand to `viability-model`** when a break-even and scenario range is needed; hand to `business-case-builder` only for board-grade NPV.

## Quality tests
- Every number has a unit, period, tag and E-id; ranges, not single points, for `[I]` values.
- Market built from counted units; no unexplained percentage of a global figure.
- Price is anchored to today's spend or a named reference.
- First-month plan names real people or channels.
- Cost lines trace to activities in 11.
- Two viability drivers named with sensitivity.

## Agent-augmented variant
Agents may gather market data and run scenario arithmetic (`[S]`), always showing formulas. Market figures from reports are `[O]` only when read at the cited source; vendor-sourced TCO or market-hype figures are marked and discounted (Soul: trust cash-flow math over vendor decks).

## Handbook 2.0 guidance (book, Futurice 2018, paraphrased)
Handbook guidance:
- Do not calculate the business before you understand customers and what you should build. Start with best guesses, then dig deeper only on the most critical.
- Existing payment: if people pay nothing and spend no time, the problem may be too small. Time is money.
- Price anchoring: say whether the offer is like a smartphone but bigger, or like a laptop but lighter. Reference prices such as streaming subscriptions or app prices shape perception.
- Total addressable market is everyone who could buy. Potential target market is your educated guess of who you could really get. Estimate it anyway.
- First-month plan: who first, and does the season matter (a mood off-season differs from on-season).
- Separate development costs from running costs. Look for cost or revenue elements that swing EBIT, for example weather-dependent costs or better-margin revenue streams.

## Gotchas
- **TAM theatre.** A large total that no one can reach is not a market.
- **Price by cost-plus.** Price follows perceived value and the alternative, then check margin.
- **Payer ≠ user.** If the user does not pay, the buyer's incentives matter more than the user's delight.
- **No cost of acquisition.** Missing sales and support cost is the most common overstatement; the 11 activities show them.

## Hand-offs
Next: `lsc-feasibility-study` (13) and the acid test `lsc-concept-evaluation` (14). Drivers go to `lsc-experimenting` (21) and `lsc-validation` (15).
