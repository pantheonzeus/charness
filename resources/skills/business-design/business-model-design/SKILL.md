---
id: business-model-design
aliases: [business-model-design]
name: "Business Model Design — Canvas, Patterns & Alternatives"
category: business-design
description: Design or innovate a business model — map the current or proposed model on the Business Model Canvas and St. Gallen magic triangle, generate at least three genuinely different alternatives from proven patterns (St. Gallen 55, Strategyzer Invincible Company), stress-test each against the environment map, and choose one with the assumptions it rests on.
triggers: [business model, business model canvas, BMC, business model innovation, new business model, how will we make money, revenue model, monetization model, business model patterns, st gallen navigator, magic triangle, invincible company, disrupt our own model, reinvent the business model]
tags: [business-design, business-model, canvas, patterns, innovation]
related: ["[[business-design-engagement]]", "[[value-proposition-design]]", "[[viability-model]]", "[[servitization-model-design]]", "[[ecosystem-platform-design]]", "[[ai-native-business-model]]", "[[strategic-options]]", "[[profit-pool-analysis]]", "[[pricing-strategy]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
references: [references/pattern-library.md]
---

# Business Model Design — Canvas, Patterns & Alternatives

## Contract
- **Input:** a value proposition (from `value-proposition-design`) or an existing business to innovate, plus its environment map (from `opportunity-framing`).
- **Output:** a Business Model Design pack (format below): as-is canvas (if one exists), ≥3 alternative to-be canvases, a comparison table, and a chosen model with its assumption list. Inline, or at `output/<YYYYMMDD>-<slug>-business-model.md`.
- **Allowed tools/artifacts:** conversation, [pattern library](references/pattern-library.md), web search for analogues, vault notes.
- **Done when:** the alternatives differ in **at least two** of Who/What/How/Value (otherwise they are variants, not alternatives); each names its source pattern and a real-world analogue; the choice is justified against explicit criteria; and the top-5 assumptions of the chosen model are listed for `strategy/assumption-audit`.

## Triggers/Context
Use once value is understood and the question becomes "how do we create, deliver and capture it?" Branch to a specialist skill when the model is: physical-asset-as-a-service → `servitization-model-design`; multi-sided/orchestrator → `ecosystem-platform-design`; agents doing the work or being the product → `ai-native-business-model`.

## Core Blueprint
1. **As-is first (if an existing business).** Fill the nine blocks: customer segments, value propositions, channels, customer relationships, revenue streams, key resources, key activities, key partners, cost structure. Mark the block that carries the profit and the block under most pressure from the environment map.
2. **Magic triangle summary.** Who (customer), What (value proposition), How (value chain: resources, activities, partners), Value (revenue mechanics + cost drivers). An innovation changes at least two corners.
3. **Generate alternatives with patterns.** Pick 5–8 candidate patterns from the [pattern library](references/pattern-library.md) by asking each pattern's trigger question. Combine and adapt; for each, write a one-line "what if we were <analogue> for <our segment>?".
4. **Select ≥3 alternatives** that are mutually distinct. Include one deliberately bold option (the one that would cannibalize today's business) and one low-risk adjacent option.
5. **Canvas each alternative** at headline level. Don't over-detail; the canvas is a thinking tool, not a deliverable to admire.
6. **Stress-test against the environment.** For each alternative, how does each of the two decisive environment forces hit it? Add one "what has to be true" line per alternative.
7. **Compare and choose.** Criteria: customer value (fit strength), revenue potential, margin structure, capital intensity, time to first revenue, capability gap, strategic fit, defensibility. Score 1–5 with a one-line reason, then **decide**; never present a tie.
8. **Write the assumption list** for the chosen model, ordered by "if wrong, the model dies", and hand off to `strategy/assumption-audit` → `business-experiment-design`. Hand the revenue/cost blocks to `viability-model`.

## Output Format
```markdown
# Business Model Design — <name>
## As-is (if applicable): canvas table + profit block + pressured block
## Alternatives
| | A: <name> | B: <name> | C: <name> |
|---|---|---|---|
| Source pattern(s) · analogue | | | |
| Who | | | |
| What | | | |
| How | | | |
| Value (revenue · cost drivers) | | | |
| What has to be true | | | |
## Comparison (criteria × alternatives, 1–5 with reasons)
## Decision: <alternative> — because <two sentences>
## Chosen canvas (9 blocks)
## Top assumptions (ranked, with kill impact)
```

## Optimizations/Gotchas
- **Product thinking in disguise.** Three alternatives that differ only in features are one business model. Enforce the two-corner rule.
- **Patterns are prompts, not answers.** Copying "subscription" without the switching-cost logic behind it fails.
- **Cost structure gets forgotten.** The as-a-service, platform and AI-native patterns shift cost and risk onto the provider; every alternative names its new cost and risk.
- **Boring wins.** When two alternatives score similarly, prefer the one that needs fewer new capabilities. That's the persona's burden-of-proof rule applied to business models.

## Sources
Osterwalder & Pigneur, *Business Model Generation* (2010); Gassmann, Frankenberger & Csik, *The Business Model Navigator* (55 patterns, magic triangle Who/What/How/Value); Osterwalder et al., *The Invincible Company* (2020; pattern library, portfolio map). See [Sources](../_category.md).
