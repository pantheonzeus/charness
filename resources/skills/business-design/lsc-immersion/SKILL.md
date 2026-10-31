---
id: lsc-immersion
aliases: [lsc-immersion]
name: "LSC 02 — Immersion Canvas"
category: business-design
description: Run the Lean Service Creation "Immersion" canvas — best-guess customer problems, how customers cope today, inspiring analogues, hottest start-ups, the data we have, what it tells us, and the new data we need and how to get it — before any interview or ideation.
triggers: [immersion canvas, LSC immersion, know where you are, build on others work, desk research canvas, landscape scan, what do we already know, data inventory, start-up scan, analogues scan, inspiring services, how do customers solve it today]
tags: [lean-service-creation, lsc, canvas, research, discovery, desk-research]
related: ["[[lean-service-creation]]", "[[lsc-business-objective-context]]", "[[lsc-customer-groups]]", "[[agent-augmented-discovery]]", "[[opportunity-framing]]", "[[service-discovery-research]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 02 — Immersion

## Contract
- **Input:** `canvases/01-business-objective-context.md`; existing internal data, reports, tickets, analytics; web access.
- **Output:** `canvases/02-immersion.md` with the eight fields, plus `EVIDENCE.md` entries for every sourced claim.
- **Allowed tools/artifacts:** web search, internal data exports, vault notes, `agent-augmented-discovery` for swarm desk research.
- **Done when:** all eight fields pass the Quality tests and the "new data we need" list is ranked by the decision each item would change.

## Canvas (v3.0.5) — "To know where you are and to build on others' work."
**Your best guess of the customers problems/needs?** · **How is the customer solving the problem/handling the need now?** · **Inspiring products, services or organisations that have a positive impact on the world?** · **Hottest related start-ups & inspiring services?** · **What data do we have about the topic?** → **What does it tell us?** · **What new data do we need?** → **How are we going to access it?**

## Core Blueprint
1. **Best guess of problems/needs.** Write 3–7 hypotheses, each `[I]`, each solution-free. Date them. They are the baseline that interviews will confirm or kill.
2. **Today's solution.** For each guessed need list the current alternative, including "do nothing", spreadsheets, a competitor, an internal workaround, a human. Add what it costs the customer (money, time, risk) where known.
3. **Inspiring analogues.** Find 3–5 products, services or organisations with a positive impact, from **other** industries as well as the same one. Record why each inspires: the mechanism, not the brand. Source URL and date each.
4. **Hottest start-ups.** List 5–10 related start-ups or services with what they do, stage or funding if public, and the date checked. Mark what they prove (demand, willingness to pay) versus what they only claim.
5. **Data inventory.** For each dataset: owner · access route · period · quality · legal constraint. "What does it tell us": one claim per dataset with a number, tagged `[O]` if read from the data, `[I]` if reasoned.
6. **New data needed.** For each gap write the question it answers and the decision that changes if the answer changes. Rank by decision impact. **[house]** Drop items that change no decision.
7. **Access plan.** Per item: method (interview, survey, scrape, partner export, purchase), owner, date, legal basis (GDPR, contracts, confidentiality). Interviews hand over to `lsc-script-creator`.

## Quality tests
- Every guess is labelled `[I]` and solution-free.
- At least one alternative per need, including do-nothing.
- Analogues include at least one outside the client's industry.
- Every start-up and analogue entry has URL and date; funding or traction claims cite the source.
- Every "tells us" is a claim with a number or a quote, not "interesting trends".
- Every new-data item names the decision it would change and how to access it lawfully.

## Agent-augmented variant
Run a desk-research swarm per question (market, competitors, analogues, trends) as file-backed children per Charter §5 and `agent-augmented-discovery`. Children return sourced findings to `children/<id>/RESPONSE.md`. Parent reopens, spot-checks 3 sources per child, tags results `[O]` only for facts read at a cited primary source; summaries are `[S]`. Prefer primary sources (filings, papers, official docs) over content farms (Charter §2).

## Handbook 2.0 guidance (book, Futurice 2018, paraphrased)
- Stop before hands-on design. Background work saves weeks later. Copying and learning from the best solutions on the market is legitimate.
- Competition includes the customer's friends, a good bottle of wine, and doing nothing. Doing nothing is a real competitor.
- Add the **public debate** field: what press, social media and conferences say, and what the service could add to that debate.
- Knowing how customers use your existing service is not the same as understanding their daily life.
- Unused data is an advantage. If data sits in another division or a queue, get ahead of the queue or learn to run the analysis yourself. Use `lsc-growth-hacking` (29) to map an existing conversion funnel.

## Gotchas
- **Solution-shopping.** Scanning start-ups only for features to copy. Record the *need* each proves.
- **"Data we have" is vague** ("CRM data"). Name the table, period and who can export it.
- **Stale start-up lists.** Re-date at gate 14; funded start-ups pivot or die within months.

## Hand-offs
Next: `lsc-customer-groups` (03). Findings feed `lsc-business-model-market-size` (12) for price anchors and `lsc-concept-evaluation` (14) for competition and novelty.
