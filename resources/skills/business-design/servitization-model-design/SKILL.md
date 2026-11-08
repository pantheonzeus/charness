---
id: servitization-model-design
aliases: [servitization-model-design]
name: "Servitization Model Design — Product-Service Systems & As-a-Service"
category: business-design
description: Design an as-a-service or product-service-system business for a physical-asset company — position the offer on the PSS spectrum (product-, use-, result-oriented; Tukker's 8 types) and on the ownership × results × smartness continua, model the risk and capital shifted onto the provider, choose the pricing metric (subscription, pay-per-use, pay-per-outcome), and test the capability and channel gaps that cause the servitization paradox.
triggers: [servitization, as a service, as-a-service, machine as a service, equipment as a service, MaaS, product service system, PSS, pay per use, pay per part, pay per outcome, outcome-based contract, performance-based contracting, uptime guarantee, availability contract, subscription for machines, from product to service, service business for manufacturer, servitization paradox, Tukker]
tags: [business-design, servitization, pss, manufacturing, as-a-service, outcome-based]
related: ["[[business-model-design]]", "[[viability-model]]", "[[ecosystem-platform-design]]", "[[ai-native-business-model]]", "[[pricing-strategy]]", "[[risk-and-mitigation]]", "[[operating-model-design]]", "[[cloud-architecture]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
---

# Servitization Model Design — Product-Service Systems & As-a-Service

## Contract
- **Input:** a manufacturer or asset owner, its product line, installed base, customers, and the ambition (recurring revenue, differentiation, sustainability, lock-in).
- **Output:** a Servitization Design pack (format below) at `output/<YYYYMMDD>-<slug>-servitization.md`.
- **Allowed tools/artifacts:** conversation, client data on installed base, failure rates, service revenue; vault notes (the Lasers4MaaS project material is a first-party reference case); web search for analogues and research.
- **Done when:** the offer is placed on the PSS spectrum with a reason; the risk-transfer table shows what the provider now carries and how it is priced; the pricing metric is chosen against the customer's value driver; capital tied up per contract is quantified (handed to `viability-model`); and the capability/channel gaps list has an owner per gap.

## Triggers/Context
Use when a product company wants to sell use or outcomes instead of (or alongside) products: machine-as-a-service, pay-per-part, uptime contracts, power-by-the-hour. Platform effects across many customers → also `ecosystem-platform-design`. AI agents delivering or optimizing the service → also `ai-native-business-model`. The connected-asset data architecture is `technology/cloud-architecture`.

## Core Blueprint
1. **Place the offer on the PSS spectrum** (Tukker 2004, three groups, eight types):
   - *Product-oriented:* product-related services (maintenance, spare parts, take-back); advice and consultancy.
   - *Use-oriented:* product lease; product renting/sharing; product pooling.
   - *Result-oriented:* activity management/outsourcing; pay per service unit; functional result.
   Then rate the offer on three continua: **ownership retention** (who owns the asset), **results orientation** (input → availability → output → outcome), and **smartness** (none → monitoring → optimization → autonomy).
2. **Name the customer's value driver.** Capex avoidance, uptime, output volume, quality, flexibility, sustainability reporting. The pricing metric must move with it.
3. **Risk-transfer table.** For each risk the provider takes on (asset utilization, failure, performance, obsolescence, customer credit, residual value, energy/consumables price): who carried it before, who now, how it's priced (premium, cap, floor, index), and what data is needed to price it.
4. **Pricing metric.** Subscription (flat, predictable, weakest value link), pay-per-use (hours, cycles, parts), pay-per-outcome (good parts, availability %, energy saved). Hybrid base + variable is the usual answer. Define measurement, metering trust, and dispute rules. Use `strategy/pricing-strategy` for levels.
5. **Capital and financing.** Assets stay on the provider's (or a financing partner's) balance sheet: capital per contract, payback per contract, residual-value assumption, financing partner options. Hand to `viability-model`.
6. **Smartness requirement.** What telemetry, remote monitoring and predictive maintenance does the risk table need to be priceable? Without data the provider is underwriting blind.
7. **Capability & channel gaps** (the servitization paradox: service revenue rises, profit doesn't). Check service delivery capacity, field service, sales incentives (dealers and salespeople paid on product sales will block it), contract/legal templates, accounting (revenue recognition), and customer procurement (capex vs opex budgets). Each gap gets an owner.
8. **Pilot design.** One segment, one asset type, a small set of contracts with explicit success KPIs, as a business experiment (`business-experiment-design`).

## Output Format
```markdown
# Servitization Design — <offer>
**Position:** <PSS group/type> · ownership <x> · results <x> · smartness <x> — because <value driver>
## Customer value driver & pricing metric (with measurement rule)
## Risk-transfer table (risk · before · after · pricing mechanism · data needed)
## Capital & financing per contract
## Smartness requirements
## Capability & channel gaps (gap · impact · owner)
## Pilot (segment · asset · contracts · KPIs · decision date)
```

## Optimizations/Gotchas
- **Result-oriented isn't automatically better.** It maximizes value alignment and provider risk. Move along the spectrum as data and capabilities mature, not in one jump.
- **Channel conflict kills more servitization programs than technology does.** Dealer and sales-incentive redesign is part of the business model.
- **Customers may want opex for accounting reasons and not for the service.** Validate the real driver; a financing product may be enough.
- **Outcome metering must be trusted by both sides.** Define the meter, the data owner and the dispute process in the contract before pricing.
- **Reference case:** Lasers4MaaS (EU Horizon, laser manufacturing as-a-service). Pull lessons from the vault and the Zenodo community `lasers4maas`. Respect client confidentiality; cite only public outputs.

## Sources
Tukker (2004), "Eight types of product–service system", *Business Strategy and the Environment*; "Product-Service Systems in the Digital Era: Deconstructing Servitisation Business Model Typologies" (ownership retention × results orientation × smartness); St. Gallen patterns Rent Instead of Buy, Pay per Use, Performance-based Contracting, Guaranteed Availability. See [Sources](../_category.md).
