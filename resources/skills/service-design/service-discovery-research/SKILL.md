---
id: service-discovery-research
aliases: [service-discovery-research]
name: "Service Discovery Research — Plan, Fieldwork & Synthesis"
category: service-design
description: Plans and synthesises discovery research for a service. Research is tied to the decision it informs and to falsifiable hypotheses. The method mix covers customers, frontline staff, backstage and demand data, with a sample that covers extremes and accessibility. Synthesis traces every insight to raw observations and ends in scored opportunity areas. AI-assisted synthesis is allowed, but synthetic users never count as evidence.
triggers: [user research, discovery research, research plan, interview guide, contextual inquiry, shadowing, service safari, diary study, research synthesis, affinity mapping, insights, jobs to be done, JTBD, how might we, opportunity areas, user needs, pain points research, synthetic users, synthetic personas]
tags: [service-design, research, discovery, synthesis, evidence]
related: ["[[service-design-engagement]]", "[[journey-mapping]]", "[[service-performance-measurement]]", "[[customer-segmentation]]", "[[assumption-audit]]", "[[agent-augmented-discovery]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
---

# Service Discovery Research — Plan, Fieldwork & Synthesis

## Contract
- **Input:** the engagement frame (or a brief): the decision to inform, the hypotheses, and access to users, staff and data.
- **Output:** two files. (a) `output/<YYYYMMDD>-<slug>-research-plan.md`: the decision, hypotheses, methods, sample, guide, ethics. (b) `output/<YYYYMMDD>-<slug>-insights.md`: insights, evidence counts, needs/JTBD, opportunity areas. Raw notes stay in `STATE_ROOT/raw/` with pseudonymised IDs (P01, S01 for staff).
- **Allowed tools/artifacts:** conversation, user-supplied transcripts/notes/data, LLM-assisted clustering, web/desk research.
- **Done when:** every insight cites ≥3 independent observations by ID, or is tagged **weak signal**; each hypothesis is marked confirmed / refuted / open; frontline staff and at least one extreme or accessibility case are in the sample; every opportunity area carries a score and links to the insights behind it.

## Operating principles (enforceable)
1. **Research serves a decision.** The plan's first line names the decision. Any method that can't move that decision is cut.
2. **Three lenses, always.** Customers (what they try to do), frontline staff (what they work around), and the demand data (what actually arrives). Customer interviews alone describe the frontstage and miss the backstage.
3. **Observe over ask.** Prefer contextual inquiry, shadowing and service safaris. Use interviews for motive and history. Treat stated preferences as weak evidence.
4. **Sample the edges.** Include extremes (heaviest users, people who dropped out, people who complained) and accessibility or vulnerability cases. Designing for the edges usually fixes the middle (*Designing for everyone*).
5. **Traceability.** Every insight points to observation IDs. No ID, no insight.
6. **Synthetic users generate hypotheses, never evidence.** LLM personas may help draft an interview guide or anticipate objections. They never appear in an evidence count.

## Core Blueprint
1. **Plan.** Write down the decision, the hypotheses (from the engagement), the research questions (≤6), and the methods matrix (method × question × lens). Sample: 6–12 customers per meaningful segment, 4–8 staff across front and back office, plus extremes. Set the timeline.
2. **Demand sample (in parallel).** Pull 100–300 recent contacts (calls, emails, tickets) and classify each as value demand or failure demand, with a reason code. This is the input to `service-performance-measurement`.
3. **Ethics and data.** Consent text, GDPR basis, recording policy, retention, pseudonymisation. In the EU, check works-council rules before shadowing staff.
4. **Guides.** One interview/observation guide per lens. Open with a recent real episode ("tell me about the last time…"). Avoid leading questions and solution pitches.
5. **Fieldwork capture.** One note per session in `STATE_ROOT/raw/<ID>.md`: context, verbatims, observed behaviour, workarounds, artefacts.
6. **Synthesis.** Cluster observations into **observation → insight → implication**. An insight states a non-obvious truth with tension ("Customers call to check status, not because the status is wrong but because silence reads as failure"). Then write needs as JTBD statements and "How might we" questions.
7. **Opportunity areas.** Score each 1–5 on user value, business value (link to demand data), feasibility and evidence strength. Rank them.
8. **Readout.** Answer-first, in this order: hypotheses verdicts, top 5 insights, opportunity ranking, and what changes in the plan.

## Output structure (insights file)
```markdown
## Hypotheses   | # | Hypothesis | Verdict | Evidence (IDs) |
## Insights     | # | Insight | Implication | Evidence (IDs, n) | Strength |
## Needs (JTBD) When <situation>, I want to <motivation>, so I can <outcome>.
## Opportunity areas | Area | HMW | User | Business | Feasibility | Evidence | Rank |
## Gaps         what we could not observe and why
```

## Optimizations/Gotchas
- **"Users want X" is a finding about a solution, not a need.** Rewrite it as the job and the obstacle.
- **The loudest stakeholder's anecdote is n=1.** Log it as a hypothesis, not an insight.
- **LLM clustering over-merges.** It smooths contradictions into one tidy theme. Check every machine-made cluster for a dissenting observation and keep the tension visible.
- **Staff workarounds are gold.** Every sticky note on a monitor, shadow spreadsheet or "I just call Petra" is an unmet backstage need and a likely fail point for the blueprint.
- **Never put participants into the vault as people.** Pseudonymised IDs only; the key stays outside the repo (Charter §8, confidentiality).
