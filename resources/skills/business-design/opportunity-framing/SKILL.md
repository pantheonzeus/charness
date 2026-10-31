---
id: opportunity-framing
aliases: [opportunity-framing]
name: "Opportunity Framing — Problem, Prize & Business Model Environment"
category: business-design
description: Turn a vague ambition or client brief into a sharp opportunity frame — problem statement, target segment, how-might-we, the size of the prize, strategic fit, the business-model environment map (market, industry, macro forces, key trends), and explicit success and kill criteria — before any solutioning.
triggers: [frame the opportunity, opportunity framing, problem framing, how might we, HMW, what problem are we solving, design challenge, opportunity statement, innovation brief, size of the prize, where is the opportunity, trend scan, environment map, reframe the brief]
tags: [business-design, framing, opportunity, trends, environment-map]
related: ["[[business-design-engagement]]", "[[value-proposition-design]]", "[[situation-assessment]]", "[[market-mapping]]", "[[growth-barriers]]", "[[agent-augmented-discovery]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
---

# Opportunity Framing — Problem, Prize & Business Model Environment

## Contract
- **Input:** a brief, an ambition ("we need a digital business"), a technology looking for a use, or a pain someone reported.
- **Output:** an Opportunity Frame (format below), inline or at `output/<YYYYMMDD>-<slug>-opportunity-frame.md` when it feeds an engagement.
- **Allowed tools/artifacts:** conversation, client documents, vault notes on the account (`cbrain/Clients/`), web search for trends and market size.
- **Done when:** the frame names one primary segment, one problem in the customer's words, a prize estimate with its arithmetic, at least three environment forces with sources, and success **and** kill criteria a sponsor has agreed to (or that are marked `unconfirmed`).

## Triggers/Context
Use at the start of any business design effort, and whenever a team is debating solutions without agreeing on the problem. Also use to **reframe** a brief that arrives as a solution ("build us an app", "we want AI agents"): the frame recovers the problem the solution was meant to solve.

## Core Blueprint
1. **Unpack the brief.** Write the brief verbatim, then list what is a goal, what is a constraint, and what is a pre-chosen solution. Pre-chosen solutions become hypotheses, not scope.
2. **Name the business outcome first.** Which number does the sponsor need to move (revenue, margin, retention, cost-to-serve, share of wallet)? No named outcome → stop and ask; this is the persona's first rule.
3. **Pick the segment and the job.** One primary customer segment and the job they are trying to get done. Secondary segments go to a parking lot.
4. **Write the problem in the customer's words**, then one How-Might-We that is neither too narrow (a feature) nor too broad (world peace). Test: three distinct solution ideas fit inside it.
5. **Size the prize.** Bottom-up whenever possible: reachable customers × adoption × price or value per customer per year. Show the arithmetic and tag each input `observed` / `inferred`. For full TAM/SAM/SOM use `strategy/market-mapping`.
6. **Map the environment.** Fill the four-zone business-model environment map: market forces (segments, needs, switching costs), industry forces (competitors, new entrants, substitutes, suppliers), key trends (technology, regulation, society, culture), macro forces (economy, capital, commodities). Cite each force. Mark the two forces that most threaten or enable the opportunity.
7. **Check strategic fit.** Why this company? Name the unfair advantage (asset, channel, data, brand, relationships) or state plainly that there is none.
8. **Set success and kill criteria.** What evidence by which date makes us continue, and what makes us stop. Get the sponsor to agree before work starts.

## Output Format
```markdown
# Opportunity Frame — <name>
**Business outcome:** <metric, baseline → target, by when>
**Segment & job:** <who> trying to <job> when <situation>
**Problem (their words):** "<quote or paraphrase, source>"
**How might we:** <HMW>
**Prize:** <€/yr> = <inputs with tags>
**Why us:** <advantage> | none (risk)

## Environment map
| Zone | Force | Direction (+/−) | Source |
|---|---|---|---|

## Out of scope / parking lot
## Success criteria (by <date>)
## Kill criteria
## Open questions for discovery
```

## Optimizations/Gotchas
- **Solution-shaped briefs are the default, not the exception.** "We want an AI agent for X" is framed as "the cost/speed/quality problem in X"; the agent is one hypothesis among several.
- **A prize without arithmetic is a wish.** No top-down "1% of a €40bn market" without a bottom-up cross-check.
- **Trends are cited or dropped.** A trend from an LLM summary without a primary source is tagged `synthetic` and cannot be one of the two decisive forces.
- **Kill criteria up front** are what make a later kill politically survivable.

## Sources
Strategyzer "Your business model environment" (four zones); IDEO/Fjord business designer postings (define growth opportunities, trend research); Futurice Lean Service Creation (problem validation first). See [Sources](../_category.md).
