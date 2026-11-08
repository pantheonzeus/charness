---
id: service-performance-measurement
aliases: [service-performance-measurement]
name: "Service Performance Measurement — Demand, Capability & Cost-to-Serve"
category: service-design
description: Builds the measurement framework that proves a service redesign pays off. The steps are purpose from the customer's view, then a demand analysis (value vs failure demand), capability measures (end-to-end time, first-time-right, cost-to-serve), experience and outcome measures, a baseline, and the money bridge to a business case. Agentic services get honest metrics (resolution and re-contact, not containment).
triggers: [service metrics, measure the service, failure demand, value demand, cost to serve, cost-to-serve, first contact resolution, end-to-end time, service KPIs, baseline the service, service design ROI, prove the value of service design, containment rate, deflection rate, CSAT CES NPS service]
tags: [service-design, measurement, failure-demand, cost-to-serve, roi]
related: ["[[kpi-architect]]", "[[business-case-builder]]", "[[value-realization]]", "[[service-blueprint]]", "[[agentic-service-evaluation]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
---

# Service Performance Measurement — Demand, Capability & Cost-to-Serve

## Contract
- **Input:** the service boundary, any operational data (contact volumes, reason codes, handling times, cost rates, case durations, CSAT), and a demand sample (from `service-discovery-research` step 2, or done here).
- **Output:** `output/<YYYYMMDD>-<slug>-service-measures.md` containing purpose, the demand analysis, the measures table with baselines, the money bridge, and the review cadence.
- **Allowed tools/artifacts:** conversation, user data (CSV/XLSX via the xlsx skill if needed), the evidence gate.
- **Done when:** the failure-demand share is calculated from a stated sample (n, period, method), or flagged as not yet measured; every measure has a baseline value with source, or "no baseline — collect from <date>"; the money bridge shows its arithmetic; every number in the deliverable passed the evidence gate.

## Operating principles (enforceable)
1. **Measure against purpose, from the customer's side.** First write the service's purpose as the customer would ("get my claim paid correctly, once"). Every measure must tell you whether that purpose is being achieved.
2. **Failure demand is the first number.** Demand caused by a failure to do something, or to do it right (Seddon). It is typically 40–75% in service organisations. Reducing it is the cheapest capacity a client will ever buy.
3. **End-to-end over functional.** Measure from the customer's trigger to the outcome. Departmental SLAs that are all green while the end-to-end time is weeks are the classic finding.
4. **No arbitrary targets on capability measures.** Show variation over time (a run chart with the median and the range). A target on handling time produces short calls and more re-contacts.
5. **Containment is a vanity metric.** For chatbots and agents, "conversations not handed to a human" counts customers who gave up. Use **resolution**, verified by no re-contact on the same issue within N days.
6. **The money bridge is arithmetic.** Benefit = volume × change × unit cost, with each input sourced. Then hand to `business-case-builder` for the investment case.

## Core Blueprint
1. **Purpose.** One sentence from the customer's side, plus what "done right" means.
2. **Demand analysis.** Take a sample of 100–300 contacts across channels. Classify each as value or failure demand with a reason code, and show the top reasons with their share. Name the period and method.
3. **Capability measures.** End-to-end time (median and spread), first-time-right / first-contact resolution, re-contact rate within N days, handoffs per case, cost-to-serve per case (handling time × loaded rate + system and partner cost).
4. **Experience measures.** Customer effort (CES) at the moments of truth, task success, and complaint themes. Use NPS only if the client already tracks it, and never as the primary measure.
5. **Outcome measures.** The business outcome from the engagement frame (retention, conversion, loss ratio, compliance breaches, revenue per customer).
6. **Agentic measures** (if agents are in the service): verified resolution rate, handoff rate and handoff quality (did the human get full context; did the customer repeat themselves), re-contact after agent interaction, policy-violation rate from eval sampling, cost per resolved case **including** human review and error remediation, and escalations on high-risk intents.
7. **Baseline.** Record the current value per measure, with source and date. Where no data exists, design the collection and set the date the baseline will exist.
8. **Money bridge.** Failure demand removed × cost per contact, plus capacity released, plus outcome uplift. Show it as a table with inputs, source and confidence.
9. **Cadence.** Who reviews which measure, how often, and which decision each one triggers. Hand KPI-system design to `kpi-architect` and benefit tracking to `value-realization`.

## Output structure
```markdown
## Purpose (customer's view)
## Demand analysis        sample n · period · method | Reason | Type (value/failure) | Share |
## Measures               | Measure | Type (capability/experience/outcome/agentic) | Definition | Baseline (src, date) | Decision it informs |
## Money bridge           | Driver | Volume | Change | Unit € | Annual € | Source | Confidence |
## Review cadence
```

## Optimizations/Gotchas
- **Clients often have reason codes that describe the department, not the customer** ("Billing – general"). Re-code a sample in customer language. The client's codes will understate failure demand.
- **Cost-to-serve hides in other departments.** Rework done by finance or field service after a frontstage error belongs to the case cost.
- **Agent dashboards from vendors report containment and CSAT on surveyed users only.** Ask for the re-contact data or build it yourself.
