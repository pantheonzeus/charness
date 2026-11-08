---
id: lsc-impact-optimizer
aliases: [lsc-impact-optimizer]
name: "LSC 10 — Impact Optimizer Canvas"
category: business-design
description: Run the Lean Service Creation "Impact Optimizer" — list the concept's positive and negative social and environmental impacts, tweak the concept to raise the good and cut the bad, and decide whether the net impact on the world is positive.
triggers: [impact optimizer, LSC impact, social and environmental impact, net positive impact, sustainability of the concept, negative impact reduction, impact assessment of the concept, is our impact net positive, societal impact canvas, ESG of the service]
tags: [lean-service-creation, lsc, canvas, impact, sustainability, social]
related: ["[[lean-service-creation]]", "[[lsc-business-objective-context]]", "[[lsc-idea-accelerator]]", "[[lsc-concept-evaluation]]", "[[lsc-pitch-creator]]", "[[servitization-model-design]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 10 — Impact Optimizer

## Contract
- **Input:** `canvases/08-…` and `09-…` (concept), `canvases/01-…` (impact goals), `canvases/07-…` lane 4.
- **Output:** `canvases/10-impact-optimizer.md`: four impact lists, the tweak lists, a verdict with reasons, and the list of impacts still unquantified.
- **Allowed tools/artifacts:** conversation, standards and published factors for quantification (cited), web search.
- **Done when:** each quadrant has entries with a tag, every negative impact has at least one mitigation idea or an accepted-risk note, and the net-impact verdict is recorded with its evidence.

## Canvas (v3.0.5) — "Enhance the good impact and minimise the bad. Ideation continues!"
Four quadrants around a ring of icons: **1. Current concept's positive social impact** · **1. positive environmental impact** · **1. negative social impact** · **1. negative environmental impact**. For each: **2. Tweak the concept to maximise the positive societal / environmental impact** and **2. Ideas to reduce the negative social / environmental impact**. Bottom slider: **Is our impact net positive to the world?** NO! — Hard to say — YES!

## Core Blueprint
1. **Walk the concept's life.** Production or build, use, support, end of life, plus rebound effects (does cheaper use cause more use?). For each stage ask what it does to people (jobs, access, safety, privacy, fairness, health) and to environment (energy, materials, emissions, water, waste).
2. **Fill the four "1." quadrants.** Each entry: who or what, how, direction, rough magnitude, tag. If magnitude is unknown, write "unknown" and add it to the unquantified list; no invented numbers.
3. **Include AI-specific impacts when agents are part of the service:** work displacement, bias, privacy, energy of inference. **[house]**
4. **Tweak.** For each positive quadrant write the change to the concept that would amplify it; for each negative, the change that would avoid, reduce or compensate it. Mark changes that affect cost or feasibility; feed them back to 07 or 12 and 13.
5. **Quantify the biggest two** impacts where feasible, with a cited method or factor. Keep ranges, not point values. **[house]**
6. **Verdict.** NO (net negative or unacceptable harm), Hard to say (material unknowns), YES (net positive with evidence). State the reason in one sentence and the top uncertainty.
7. **Gate line.** NO → back to 07 or kill; Hard to say → name the data needed (candidate experiment for 21); YES → continue. Record in `RESPONSE.md`.

## Quality tests
- All four quadrants filled, or "none identified" with the method used to look.
- At least one entry covers a stage other than "use".
- Each negative impact has a tweak or an explicit accepted-risk note with owner.
- Quantities cite a method; unquantified items listed.
- Verdict sentence names the main uncertainty.

## Agent-augmented variant
An agent may brainstorm stakeholders affected, lifecycle stages and rebound effects (`[S]`), and search for published impact factors; every factor used is verified at the source and logged `[O]`. No agent assigns the verdict.

## Gotchas
- **Greenwashing.** Claiming benefits without numbers or ignoring rebound effects breaks the Soul line against overselling. Say "unknown" when it is unknown.
- **Only environmental or only social.** The canvas has both halves; fill both.
- **Offsetting as design.** Compensation is a last tweak, after avoiding and reducing.
- **Manufacturing and as-a-service:** include utilisation and lifetime of the physical asset; servitization can raise or lower material use depending on the model (`servitization-model-design`).

## Hand-offs
Result flows into `lsc-concept-evaluation` (14, "positive impact to the society") and `lsc-pitch-creator` (17, "Social impact"). Open items go to `lsc-experimenting` (21).
