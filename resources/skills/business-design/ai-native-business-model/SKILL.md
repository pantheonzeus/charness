---
id: ai-native-business-model
aliases: [ai-native-business-model]
name: "AI-Native Business Model — Agents in Value Creation & Capture"
category: business-design
description: Design how AI agents change a business model — classify the offer (copilot, agent, AI-enabled service / service-as-software), pick the pricing unit (seat, consumption, workflow, outcome, hybrid) against value type and ROI clarity, model gross margin with inference and human-in-the-loop costs and cost variance, define the defensibility (data, workflow, distribution, trust), and set the liability and accountability terms that outcome pricing implies.
triggers: [AI-native business model, agentic business model, AI business model, monetize AI, price an AI agent, AI pricing, outcome-based pricing, per resolution pricing, usage-based AI pricing, seat-based pricing dying, service as software, AI-enabled service, agent economics, inference cost margin, AI gross margin, what is our moat with AI, AI disrupts our business model]
tags: [business-design, agentic, ai, pricing, business-model, unit-economics]
related: ["[[business-model-design]]", "[[viability-model]]", "[[pricing-strategy]]", "[[ai-opportunity-portfolio]]", "[[servitization-model-design]]", "[[business-experiment-design]]", "[[risk-and-mitigation]]", "[[cloud-architecture]]", "[[agentic-service-blueprint]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
---

# AI-Native Business Model — Agents in Value Creation & Capture

## Contract
- **Input:** an AI/agent-based offer (new, or AI added to an existing product/service), or an incumbent business threatened by one.
- **Output:** an AI Business Model pack (format below) at `output/<YYYYMMDD>-<slug>-ai-business-model.md`.
- **Allowed tools/artifacts:** conversation, client cost/volume data, web search for current pricing analogues and model prices (cite with date; prices move monthly), Python for margin math.
- **Done when:** the offer type is classified; the pricing unit is chosen against the decision table with a rejected alternative; gross margin per unit includes inference, tooling, and human review at low/base/high task complexity; the defensibility source is named (or its absence is admitted); and the accountability terms for agent errors are written.

## Triggers/Context
Use when agents do work that a customer would otherwise do or pay a person to do, when AI is the product, or when an incumbent's revenue is per seat or per hour and agents threaten it. Per-service agent lanes and oversight design belong to `service-design/agentic-service-blueprint`. Choosing *which* workflows to agentify belongs to `ai-opportunity-portfolio`.

## Core Blueprint
1. **Classify the offer.** *Copilot*: a human does the work faster, so ROI is soft. *Agent*: completes discrete units of work, so ROI is harder and countable. *AI-enabled service / service-as-software*: sells the outcome of a service (a resolved ticket, a processed invoice, a booked inspection) with agents plus humans behind it, which competes with labour and outsourcing budgets, not software budgets.
2. **Value type and ROI clarity.** Is the value revenue uplift or cost reduction? Is the ROI hard (measured per unit) or soft? Who is the buyer: technical, line-of-business, or CFO?
3. **Choose the pricing unit** (BVP framework):
   | Unit | Fits when | Watch out |
   |---|---|---|
   | Seat | Copilot, incremental productivity | Revenue shrinks as agents replace seats |
   | Consumption (tokens, calls) | Technical buyers who want control | Opaque to business buyers |
   | Workflow / task | Bounded tasks, customer can count time saved | Complexity variance per task |
   | Outcome | Measurable result, confident performance, you can absorb variance | Attribution disputes, maximum cost variance |
   | Hybrid (base + usage/outcome) | Early uncertainty | Complexity in billing and sales |
   Pick one, name the rejected runner-up and why.
4. **Unit margin with variance.** Per unit: model/inference cost, tool/API costs, retrieval and infra, human-in-the-loop review time × rate, error-remediation cost × error rate. Compute at low/base/high task complexity. AI gross margins have run ~50–60% vs SaaS 80–90% (BVP); show where this offer lands. Hand to `viability-model`.
5. **Cost curve and pricing durability.** Model prices fall over time while customer reference prices also reset. Decide whether to pass savings through, hold price and widen margin, or re-tier. Never let the price depend on today's token price.
6. **Defensibility.** Choose one honestly: proprietary data or feedback loop, workflow embedding and integration depth, distribution or installed base, trust, compliance, liability-bearing. "We use the best model" is not a moat.
7. **Accountability and liability.** When the agent errs: who detects it, who pays, which SLAs/credits apply, what is excluded. Outcome pricing implies outcome liability. Price it in or bound it in the contract. Check regulatory classification (e.g. EU AI Act risk class) via `strategy/risk-and-mitigation`.
8. **Incumbent cannibalization check** (if the client sells hours or seats today): model revenue under agent substitution and design the transition path (e.g. outcome tiers alongside seats).
9. **Test** the pricing unit and willingness to pay with `business-experiment-design`. Wizard-of-Oz or concierge delivery gives the cost-to-serve baseline before building the agent.

## Output Format
```markdown
# AI Business Model — <offer>
**Type:** copilot / agent / AI-enabled service · **Buyer:** <role> · **Value:** <uplift|saving>, ROI <hard|soft>
## Pricing unit: <unit> (rejected: <unit> — why)
## Unit margin (low / base / high complexity)
| Cost line | Low | Base | High | Source/assumption |
|---|---|---|---|---|
## Pricing durability vs. model cost curve
## Defensibility: <source> — evidence
## Accountability terms (detection · remedy · cap · exclusions · regulatory class)
## Cannibalization & transition (if incumbent)
## Hypotheses to test
```

## Optimizations/Gotchas
- **Seat pricing for agents caps your own revenue.** Agents don't log in; charging per seat for them is the parking-space-per-self-driving-car mistake.
- **Outcome pricing without an agreed meter is a dispute generator.** Define "resolved", "processed" and "correct" in the contract.
- **Human review is a cost line, not a footnote.** It often decides the margin, and it shrinks only as measured error rates fall.
- **Prices and adoption statistics in this space date fast.** Re-verify any analyst number (e.g. Gartner's 40%-of-enterprise-apps-with-agents projection) before it lands in a client deliverable.
- **Boring tech still wins.** Pick the cheapest model that meets the measured quality bar per task. Model choice is a cost decision, not a branding one.

## Sources
Bessemer Venture Partners, "The AI pricing and monetization playbook" (pricing units, offer types, margin ranges); Monetizely, "2026 Guide to SaaS, AI and Agentic Pricing Models" (outcome-pricing rationale; Gartner projection, secondary); Zuora, "Pricing Agentic AI". See [Sources](../_category.md).
