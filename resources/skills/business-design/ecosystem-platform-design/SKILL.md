---
id: ecosystem-platform-design
aliases: [ecosystem-platform-design]
name: "Ecosystem & Platform Design — Actors, Transactions, Network Effects, Governance"
category: business-design
description: Design a platform or ecosystem business — map the actors and their motivations, the transactions the platform makes cheaper and faster (Transactions Board), the learning engine and network effects, the chicken-and-egg launch sequence, orchestrator economics, and governance rules — and decide honestly whether the client should orchestrate, join, or stay a pipeline.
triggers: [platform business, ecosystem, ecosystem strategy, platform strategy, marketplace, multi-sided, two-sided market, orchestrator, network effects, chicken and egg, platform design toolkit, transactions board, open ecosystem, data sharing platform, dataspace, should we build a platform]
tags: [business-design, platform, ecosystem, network-effects, orchestration]
related: ["[[business-model-design]]", "[[value-proposition-design]]", "[[viability-model]]", "[[servitization-model-design]]", "[[stakeholder-alignment]]", "[[competitive-intel]]", "[[business-design-engagement]]", "[[service-ecosystem-mapping]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
---

# Ecosystem & Platform Design — Actors, Transactions, Network Effects, Governance

## Contract
- **Input:** a platform/ecosystem ambition, or a pipeline business considering one, plus the known actors.
- **Output:** an Ecosystem Design pack (format below) at `output/<YYYYMMDD>-<slug>-ecosystem.md`.
- **Allowed tools/artifacts:** conversation, vault account and competitor notes, web search for analogous platforms and their take rates (cite every one).
- **Done when:** the role decision (orchestrate / join / pipeline) is made with reasons; every actor has a stated motivation and the transaction they gain from; at least one network effect is described as a loop with its unit; a launch sequence solves the cold-start side explicitly; and orchestrator revenue and cost are passed to `viability-model`.

## Triggers/Context
Use when value depends on more than two parties interacting: marketplaces, partner/app ecosystems around a product line, industrial data-sharing (dataspaces, Gaia-X-style federations), service networks. The operational actor map for **one service** is `service-design/service-ecosystem-mapping`. This skill covers the strategy and business model of the whole ecosystem.

## Core Blueprint
1. **Role decision first.** Orchestrate, join someone else's, or stay a pipeline? Orchestrating requires a gravity asset (installed base, data, brand, standards position) **and** willingness to let others make money. Without both, recommend joining. Most companies that "want a platform" should join one.
2. **Ecosystem canvas.** List actors: platform owner, producers/providers, consumers, partners, peers, regulators. For each: what they want, what they bring, what they fear (lock-in, data loss, disintermediation).
3. **Transactions Board.** For each actor pair, what value is exchanged today (goods, money, data, reputation, attention) and through which channel, and what makes it slow, costly or risky. The platform's value proposition is making selected transactions **easier, cheaper, faster or safer**. Name those transactions.
4. **Learning engine.** What does each actor get better at by participating (data, tools, reputation, skills)? This is what keeps them beyond the first transaction.
5. **Network effects.** Describe each as a loop: "more A → more value for B → more B → more value for A". Same-side or cross-side, positive or negative (congestion, quality dilution). Name the metric that shows the loop is turning (liquidity, match rate, repeat transactions).
6. **Cold start.** Which side do you subsidize or seed first, and how: single-player utility, own supply, an anchor partner, or an existing installed base. Write the first-100-participants plan.
7. **Orchestrator economics.** Monetization point (take rate, subscription, data/service fees, premium tools), plus who must **not** be charged so the loop keeps running. Costs: trust & safety, onboarding, partner management, governance. Hand to `viability-model`.
8. **Governance.** Who sets the rules, curation and quality rules, data ownership and portability, dispute resolution, and how rules change. For industrial and sovereign contexts, data sovereignty and neutrality rules are often the adoption decider.
9. **Defensibility and threats.** Multi-homing cost, disintermediation risk (parties transacting off-platform after meeting), and competitor platform moves (`strategy/competitive-intel`).

## Output Format
```markdown
# Ecosystem Design — <name>
**Role decision:** orchestrate / join <whom> / pipeline — because <reasons>
## Actors (who · wants · brings · fears)
## Transactions Board (pair · value exchanged · today's friction · platform improvement)
## Learning engine
## Network effect loops (loop · type · health metric)
## Cold-start plan (seed side · tactic · first-100 plan)
## Orchestrator economics (monetization point · subsidized side · cost lines)
## Governance rules
## Threats (multi-homing · disintermediation · competitor moves)
```

## Optimizations/Gotchas
- **"Platform" is often a vanity word.** If there is no cross-side interaction, it is a product with an API. Call it that.
- **Charge the side that values the other side more**, and subsidize the scarce side. Charging both early kills liquidity.
- **Disintermediation kills B2B marketplaces.** Once a buyer and a supplier have met, why come back? The learning engine (payments, guarantees, tooling) must answer that.
- **Industrial ecosystems move at the speed of trust.** Neutral governance and data sovereignty usually decide adoption before features do. The persona's sovereignty experience applies here.

## Sources
Platform Design Toolkit (Ecosystem Canvas → Transactions Board → Learning Engine → Platform Experience → business model); St. Gallen patterns Two-sided Market and Orchestrator; Strategyzer shift pattern sales → platform. See [Sources](../_category.md).
