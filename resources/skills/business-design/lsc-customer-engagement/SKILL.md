---
id: lsc-customer-engagement
aliases: [lsc-customer-engagement]
name: "LSC 11 — Customer Engagement Canvas"
category: business-design
description: Run the Lean Service Creation "Customer Engagement" canvas — walk the six stages from awareness to advocacy around the value proposition, name what prevents and what enables each transition, and derive key activities, resources and partners.
triggers: [customer engagement canvas, LSC customer engagement, awareness interest purchase first use continued use advocate, customer lifecycle canvas, what prevents what enables, go to market canvas, how do customers become advocates, adoption journey, key activities resources partners]
tags: [lean-service-creation, lsc, canvas, engagement, go-to-market, adoption]
related: ["[[lean-service-creation]]", "[[lsc-rational-concept-sheet]]", "[[lsc-business-model-market-size]]", "[[lsc-feasibility-study]]", "[[service-ecosystem-mapping]]", "[[business-model-design]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 11 — Customer Engagement

## Contract
- **Input:** `canvases/08-…`, `09-…` (value propositions), `canvases/03-…`, interview evidence in 05.
- **Output:** `canvases/11-customer-engagement.md`: six stages each with "prevents / enables", the weakest transition, and the three bottom lists.
- **Allowed tools/artifacts:** conversation, upstream canvases, web research on channels and competitors, `service-ecosystem-mapping`.
- **Done when:** all six stages have a prevents and an enables entry tied to evidence, the weakest transition is named, and activities, resources and partners derive from the stage entries.

## Canvas (v3.0.5) — "How do we get people to become our advocates? Ideation continues!"
Ring around **VALUE PROPOSITION**: **Awareness → Interest → Purchase → First use → Continued use → Advocate**. On each link: **What prevents?** and **What enables?** Bottom: **Key activities** (what the value propositions, distribution channels, customer relationships and revenue streams require) · **Key resources** (same lens) · **Key partners** (key partners and suppliers; resources acquired from partners; activities partners perform).

## Core Blueprint
1. **Place the value proposition** (combined, from 09) at the centre in one sentence.
2. **Walk stage by stage from the customer's side.** Awareness: how do they learn it exists? Interest: why look closer? Purchase: who decides, what must be true to sign? First use: what must work in the first session? Continued use: what makes it a habit or a contract renewal? Advocate: what makes them tell others, in which situation?
3. **Per transition write prevents and enables.** Evidence tag each. In B2B, add the buying committee (user, economic buyer, technical gatekeeper, legal) at Interest and Purchase. In public sector add procurement route and threshold values. **[house]**
4. **Find the weakest transition:** the one with the strongest blocker and the least enabler. This becomes an experiment (21) and a design target.
5. **Derive activities.** For each blocker you want to remove and each enabler you want to use, write the activity the organisation must do (content, sales, onboarding, support, community).
6. **Derive resources** needed to carry those activities (people, data, platform, assets, brand) and **partners** who hold what you do not (channels, integrators, certifications).
7. **Check against 12.** Each activity, resource and partner must show up as cost or constraint in the business model; otherwise the model is incomplete.

## Quality tests
- Six stages, each with prevents and enables, each tied to an interview quote, data point, or labelled `[I]`.
- At least one stage-specific metric proposed (e.g. awareness → interest conversion).
- Weakest transition named with reason.
- Every partner states what it brings and what it gets.
- B2B/public: decision-makers named by role.

## Agent-augmented variant
Agents can draft channel options and competitor engagement patterns (`[S]`). Real customer path data (analytics, CRM funnels) overrides any agent view. Agent-facing channels (customers' AI agents as evaluators or buyers) are a stage to consider under `service-design/agent-ready-service`.

## Handbook 2.0 guidance (book, Futurice 2018, paraphrased)
Handbook version of the stages: **Awareness, Engagement, Purchase, Use, Use more, Advocate**. This skill's stage names map: Interest = Engagement, First use = Use, Continued use = Use more. Prompts from the book:
- Awareness: where do customers go when the problem arises (niece, search, manual, friends)? Be there at that moment. Write the two or three most important ways.
- Engagement: brochure, landing page, free trial, coupon, personal visit.
- Purchase: includes the decision to acquire when no money moves.
- Use: describe the very first use; first impressions matter. Use more: most apps are used once, so plan how it becomes part of life or work.
- Advocate: how to turn a customer into a sales person and make it viral.
- Separate activities that keep the service running from activities that build it.

## Gotchas
- **Skipping to Awareness marketing.** The failure is usually at First use or Continued use.
- **Advocacy assumed.** Write the concrete trigger and channel for recommendation or it is empty.
- **Partners as logos.** Without defined exchange, a partner is a hope.

## Hand-offs
Next: `lsc-business-model-market-size` (12). Dependency risks go to `lsc-feasibility-study` (13). Ecosystem-heavy concepts: `ecosystem-platform-design`.
