---
id: ai-opportunity-portfolio
aliases: [ai-opportunity-portfolio]
name: "AI Opportunity Portfolio — Workflow Decomposition to Ranked Agent Bets"
category: business-design
description: Find and rank where AI agents create business value across a function or company — decompose workflows into tasks, classify each as automate / agent / copilot / human, score candidates on separable dimensions (value, workflow fit, data readiness, feasibility, risk, sponsor, measurability) instead of one blended impression, and produce a sequenced portfolio of quick wins, strategic bets and kills with a value hypothesis per bet.
triggers: [AI use cases, AI opportunities, where can we use AI, where should we use agents, agentic opportunities, AI use case prioritization, AI portfolio, AI roadmap, which processes to automate, agentify, redesign work with AI, human agent work allocation, AI strategy workshop, AI ideation, AI quick wins]
tags: [business-design, agentic, ai, use-cases, prioritization, work-redesign]
related: ["[[ai-native-business-model]]", "[[initiative-prioritizer]]", "[[portfolio-review]]", "[[operating-model-design]]", "[[business-case-builder]]", "[[kpi-architect]]", "[[opportunity-framing]]", "[[agentic-service-blueprint]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
---

# AI Opportunity Portfolio — Workflow Decomposition to Ranked Agent Bets

## Contract
- **Input:** a function, value stream or company in scope, plus the business outcome the sponsor cares about. Optional: process docs, volumes, FTE allocation, system landscape, data inventory.
- **Output:** an AI Opportunity Portfolio (format below) at `output/<YYYYMMDD>-<slug>-ai-portfolio.md`.
- **Allowed tools/artifacts:** conversation, client documents, interviews notes, vault account notes, web search for analogues (cite them).
- **Done when:** every in-scope workflow is decomposed into tasks with volume and effort; every candidate is scored on all seven dimensions separately with a one-line reason; the portfolio has a ranked top list, a sequence, **and** a kill list; and each top bet has a value hypothesis with a baseline metric and an owner.

## Triggers/Context
Use when a client asks "where should we use AI / agents?" or has a pile of disconnected pilots. Most organizations are stuck in fragmented use cases; McKinsey reports only ~11% have reached the "reinvention" horizon where work and value creation are redesigned. This skill moves from tool-hunting to workflow redesign. For one chosen service, hand off to `service-design/agentic-service-blueprint`. For monetizing an agent externally, use `ai-native-business-model`.

## Core Blueprint
1. **Anchor on outcomes.** List the 2–3 business metrics in scope (cost-to-serve, cycle time, revenue per FTE, quality/error rate, capacity). Candidates that move none of them go straight to the parking lot.
2. **Map workflows, then tasks.** For each workflow: trigger → steps → output. For each task, record volume per month, minutes per instance, people involved, systems touched, inputs (structured / unstructured), and decision type (rule-based, judgment, relationship).
3. **Classify each task:** *Automate* (deterministic rules, so use plain software or RPA and no LLM needed), *Agent* (multi-step, tool use, bounded judgment, verifiable output), *Copilot* (human decides, AI drafts/retrieves), *Human* (relationship, accountability, novel judgment). Boring first: if a rule engine does it, don't use an agent.
4. **Cluster into candidates.** A candidate is a coherent slice of a workflow that one team could own, not a single task and not an entire department.
5. **Score on separable dimensions** (1–5, each with a reason, never blended early):
   | Dimension | Question |
   |---|---|
   | Business value | € or metric impact per year (volume × time × rate, or revenue effect) |
   | Workflow fit | Can output be verified? Is there a clear handoff? Is the error cost tolerable? |
   | Data readiness | Is the data accessible, of good enough quality, legally usable? |
   | Technical feasibility | Integration depth, tool APIs, latency, known model capability |
   | Risk | Regulatory class, customer impact of errors, security, works-council/union implications |
   | Sponsorship | Named owner with budget and pain |
   | Measurability | Baseline exists? Can impact be attributed? |
6. **Portfolio, not a list.** Plot value × (feasibility + data readiness). Quadrants: *quick wins* (do now), *strategic bets* (fund foundations: data, integration), *fill-ins* (only if cheap), *kills* (say it). Add dependencies: shared data foundations often unlock several candidates.
7. **Value hypothesis per top bet:** "Agentifying <slice> reduces <metric> from <baseline> to <target> within <period>, measured by <method>; owner <name>." Feed into `strategy/kpi-architect` and, for funding, `strategy/business-case-builder`.
8. **Work redesign note.** For each top bet, state what changes for the people: roles freed, new oversight roles, skills needed. Agents change the constraints of human capacity, expertise and coordination (McKinsey), so the operating-model consequences go to `strategy/operating-model-design`.

## Output Format
```markdown
# AI Opportunity Portfolio — <scope>
**Outcomes in scope:** <metrics with baselines>
## Task inventory (workflow · task · volume · min/instance · class · reason)
## Candidates scored
| Candidate | Value | Fit | Data | Feas. | Risk | Sponsor | Measur. | Quadrant |
|---|---|---|---|---|---|---|---|---|
## Ranked portfolio & sequence (with dependencies)
## Kill list (and why)
## Value hypotheses for top bets
## Work-redesign implications
```

## Optimizations/Gotchas
- **Blended scores hide the killer.** A candidate scoring 5 on value and 1 on data readiness is a data project, not an AI quick win. Keep the dimensions separate until the quadrant step.
- **"Agent" is not the default class.** Most high-volume, rule-based tasks are cheaper and more reliable as plain automation.
- **Pilot purgatory comes from missing baselines.** No baseline means no measurable value, so the pilot can never "win". Measure the baseline before building.
- **Works councils and co-determination (DE/AT/Nordics) are a gating dependency** for anything touching employee monitoring or role changes. Put them in Risk early.
- **Use agents to do the inventory, not the scoring.** Agents can draft task inventories from process docs and tickets (`agent-augmented-discovery`); humans who own the work validate volumes and score risk and sponsorship.

## Sources
Umbrex, "AI Use Case Discovery & Prioritization Playbook" (separable dimensions; task-level automate/copilot/agent split); McKinsey, "AI is changing work — now it has to change the organization" and "Agentic organizations" (capacity/expertise/coordination constraints; 11% at reinvention horizon); Coursera "Identify and prioritize AI opportunities" (DVF for AI). See [Sources](../_category.md).
