---
id: lean-service-creation
aliases: [lean-service-creation, lsc]
name: "Lean Service Creation — Futurice's 29-Canvas Method, Idea to Pitch to Build to Growth"
category: business-design
description: Run Futurice's Lean Service Creation (LSC) end to end or canvas by canvas — trends, strategic objectives, business objective, immersion, customer groups, interviews, insight, ideation, concepting, impact, engagement, business model, feasibility, evaluation, validation, minimum lovable product, pitch, MVP backlog, metrics, growth hacking and the build-phase rituals — with file-backed canvases, evidence tags and explicit YES / ITERATE / NO gates. Router for the 29 `lsc-*` canvas skills, informed by the Handbook 2.0.
triggers: [lean service creation, LSC handbook, service vision sprint, growth hacking canvas, management track, LSC, LSC canvas, futurice canvases, lean service creation toolbox, run LSC, service creation workshop, new service from scratch, idea to pitch, business objective and context, concept evaluation, minimum lovable product, MLP, pitch creator, audit my canvases, fill the canvases, canvas workshop kit]
tags: [lean-service-creation, futurice, canvases, innovation, service-design, business-design, router]
related: ["[[business-design-engagement]]", "[[opportunity-framing]]", "[[value-proposition-design]]", "[[business-model-design]]", "[[viability-model]]", "[[business-experiment-design]]", "[[agent-augmented-discovery]]", "[[service-discovery-research]]", "[[service-codesign-facilitation]]", "[[assumption-audit]]", "[[narrative-builder]]", "[[business-case-builder]]", "[[kpi-architect]]", "[[lsc-business-objective-context]]", "[[lsc-immersion]]", "[[lsc-customer-groups]]", "[[lsc-script-creator]]", "[[lsc-insight]]", "[[lsc-ideation-sandbox]]", "[[lsc-idea-accelerator]]", "[[lsc-rational-concept-sheet]]", "[[lsc-emotional-concept-sheet]]", "[[lsc-impact-optimizer]]", "[[lsc-customer-engagement]]", "[[lsc-business-model-market-size]]", "[[lsc-feasibility-study]]", "[[lsc-concept-evaluation]]", "[[lsc-validation]]", "[[lsc-minimum-lovable-product]]", "[[lsc-pitch-creator]]", "[[lsc-team-weekly]]", "[[lsc-weekly-board]]", "[[lsc-agile-board]]", "[[lsc-experimenting]]", "[[lsc-retrospective]]", "[[lsc-retro-diamond]]", "[[lsc-trends]]", "[[lsc-strategic-business-objectives]]", "[[lsc-success-is-a-process]]", "[[lsc-mvp-backlog]]", "[[lsc-what-to-measure]]", "[[lsc-growth-hacking]]"]
modules: [file-backed-state, evidence-backed-answering, file-backed-handoff]
references: [references/lsc-conventions.md, references/handbook-2.md]
status: active
version: 2
created: 2026-10-22
updated: 2026-10-22
vault_writes: ["cbrain/Clients/*", "cbrain/projects/*"]
---

# Lean Service Creation — Futurice's 29-Canvas Method

## Contract
- **Input:** an idea, a brief, a sponsor ambition, a half-filled canvas set, or a stuck initiative. Optional: interview notes, data, existing canvases (PDF, photo, text).
- **Output:** a STATE_ROOT `output/.runs/<YYYYMMDD>-<slug>-lsc/` with `RESPONSE.md` (spine and gate log), `EVIDENCE.md`, and one `canvases/NN-<slug>.md` per canvas run. Final **LSC Dossier** at `output/<YYYYMMDD>-<slug>-lsc.md`, indexed into `cbrain/notes/Deliverables/` (Charter §4). Conventions: [lsc-conventions.md](references/lsc-conventions.md). Book-derived mindset, structure and lessons: [handbook-2.md](references/handbook-2.md).
- **Allowed tools/artifacts:** the `lsc-*` skills, the business-design and service-design skills named below, web search, vault notes, user data, child agents per Charter §5.
- **Done when:** every canvas in the chosen route is `[x]` or skipped with a reason; every gate has a YES/ITERATE/NO line with evidence ids; the Dossier lists the riskiest open assumption with its next test; no gate toward build or pitch rests on `[S]`/`[I]` evidence alone.

## Triggers/Context
LSC is Futurice's canvas toolbox for taking a service from a funded objective to a validated, pitched, built-and-learning concept. The 23-page toolbox PDF (v3.0.5) groups the canvases in phases: **business objective → users needs → ideation → concepting → business model → validation → wrapping it all up**, followed by build-phase team tools. The Handbook 2.0 book adds a management track before them (trends, strategic objectives, phase metrics) and measurement and growth canvases after launch. It is non-linear: gates send you backwards, and per the book "there is no orthodox order". The mindset counts more than the paper: the book calls LSC a movement and warns it is no silver bullet. Read [handbook-2.md](references/handbook-2.md) before coaching a team or a sponsor.

Use this skill when the ask is the LSC method, any named canvas, or "take this idea through a structured service-creation process". For a generic viability engagement with Osterwalder tooling, `business-design-engagement` is the sibling router. Both can run on one project: LSC canvases are the working artifacts, the business-design skills are the depth engines (table below).

## Canvas map (route table)
| # | Skill | Phase | Core question | Gate |
|---|---|---|---|---|
| 01 | `lsc-business-objective-context` | Business objective | Why are we doing this, for whom funding it, how will we know? | Sponsor signs |
| 02 | `lsc-immersion` | Users needs | What do we know, what is out there, what data is missing? | — |
| 03 | `lsc-customer-groups` | Users needs | Who do we aim to serve, with which assumed needs? | Main group chosen |
| 04 | `lsc-script-creator` | Users needs | How do we find the deeper need in an interview? | Script piloted |
| 05 | `lsc-insight` | Users needs | Which needs, backed by what people said, serve our objective? | Needs selected |
| 06 | `lsc-ideation-sandbox` | Ideation | Which ideas fill need, business objective and society? | Seed idea chosen |
| 07 | `lsc-idea-accelerator` | Ideation | How do we make the seed idea better on four fronts? | YES / NO (loop) |
| 08 | `lsc-rational-concept-sheet` | Concepting | What is the concept and its rational value proposition? | — |
| 09 | `lsc-emotional-concept-sheet` | Concepting | What is the emotional value proposition, and what does the fake ad say? | — |
| 10 | `lsc-impact-optimizer` | Concepting | Is our social and environmental impact net positive? | NO / Hard to say / YES |
| 11 | `lsc-customer-engagement` | Concepting | How do customers get from awareness to advocacy? | — |
| 12 | `lsc-business-model-market-size` | Business model | Does the high-level business case hold? | — |
| 13 | `lsc-feasibility-study` | Validation | What can stop us building it, and how do we simplify? | — |
| 14 | `lsc-concept-evaluation` | Validation | The acid test: proceed, iterate or stop? | YES / ITERATE / NO |
| 15 | `lsc-validation` | Validation | Is value proposition, customer group and business model proven? | YES / ITERATE / NO |
| 16 | `lsc-minimum-lovable-product` | Wrapping up | What is the minimum the user would love? | Cut line agreed |
| 17 | `lsc-pitch-creator` | Wrapping up | How do we get others to commit? | Sponsor commits |
| 18 | `lsc-team-weekly` | Build | Is the team's capacity and mood sustainable? | — |
| 19 | `lsc-weekly-board` | Build | What is most critical this week and what did we validate? | — |
| 20 | `lsc-agile-board` | Build | What is in flight and what does "done" mean? | — |
| 21 | `lsc-experimenting` | Build / Validation | Which assumptions do we test, with what success criteria? | — |
| 22 | `lsc-retrospective` | Build | What do we keep, start, stop? | — |
| 23 | `lsc-retro-diamond` | Build | What did we learn that other teams should reuse? | — |
| 24 | `lsc-trends` | Management track | Which megatrends change this business, and where do they show up? | — |
| 25 | `lsc-strategic-business-objectives` | Management track | Which of several objectives does the data support, and why not the others? | Objective chosen |
| 26 | `lsc-success-is-a-process` | Management track / Build | What does success mean in this phase, and in the next? | Steering agrees phase criteria |
| 27 | `lsc-mvp-backlog` | Build | What exact actions get the MVP out, who owns each? | — |
| 28 | `lsc-what-to-measure` | Build | Which value-proposition, service and business metrics do we track? | — |
| 29 | `lsc-growth-hacking` | After launch | Where does the funnel leak, why, and what is the one blocker to fix? | — |

Canvases 24–26 come from the Handbook 2.0 management track and 27–29 from its MVP and growth sections. Suggested order for a management-initiated project: 24 → 25 → 01 → … → 26 alongside 15 → 16 → 27 → 28 → build rituals 18–23 → 29 after launch. Canvas 01 maps to the book's Business Objective & Context, 03 to Customer Grouping, 06 to Ideation Kick Off, 08+09 to Concept and Value Proposition, 14 to Profiling the Concept ("Death Star"), 12 to Business Model & Market Size; 04, 07, 10, 13 and 17 exist only in the newer toolbox.

## Core Blueprint
1. **Intake (ask, don't assume).** Establish: starting point (idea, brief, existing canvases, nothing), sponsor, time box, available evidence, mode. Ask only what changes the route; state assumptions for the rest.
2. **Pick the mode.**
   - **Full run:** 01 → 23 in order, with loops.
   - **Single canvas:** open that `lsc-*` skill; read upstream canvases if they exist, otherwise run it standalone with `[I]` entries labelled as guesses.
   - **Workshop kit:** for each canvas on the agenda, emit the blank "Canvas template" block from its skill plus a pre-filled strawman from desk research (all `[S]`/`[I]`), so the room edits instead of starting blank.
   - **Audit:** read the user's filled canvases, run each skill's **Quality tests**, report fails per canvas, propose the fix, and name the weakest gate.
3. **Open the STATE_ROOT.** Write the spine to `RESPONSE.md`, one line per canvas in the route, one Gate line per gate. Create an empty `EVIDENCE.md`. Reopen both by path after any compaction.
4. **Run canvases in route order.** For each: open its `SKILL.md`, follow its Blueprint, write `canvases/NN-<slug>.md`, run its Quality tests, tick the spine.
5. **Gates.** At 03, 07, 10, 14 and 15 write a Gate line in the format of conventions §3b. ITERATE names which canvases re-run. Cap 3 loops per gate; then decide and record why.
6. **Standard loops** (the paper canvases point back on purpose):
   - 07 NO → back to 06 with a new seed idea.
   - 14 ITERATE → back to the canvases whose spokes scored lowest (08/09 value, 12 money, 13 build).
   - 15 ITERATE → 21 (more experiments), then 15 again.
   - After launch: 29 findings that change the value proposition or segment re-open the relevant Service Vision Sprint canvases (book guidance).
   - 05 shows an unmet objective-need link → back to 01 (re-ask why) or 03 (wrong group).
7. **Assemble the Dossier.** One file: Gate memo on top (recommendation, riskiest assumption + next test + cost + date, ask), then the canvases in order, then the evidence register. Run `_shared/evidence-gate.md` before release.
8. **Wire the vault.** People and organisations found become or link to vault notes, both directions, with a one-line reason (Charter §6).

## Handoffs: LSC canvas → depth engine
| LSC canvas | Deeper skill when the canvas is not enough |
|---|---|
| 01, 02 | `opportunity-framing`, `strategy/market-mapping`, `agent-augmented-discovery` |
| 03 | `strategy/customer-segmentation` |
| 04, 05 | `service-design/service-discovery-research` |
| 06, 07 | `service-design/service-codesign-facilitation` |
| 08, 09 | `value-proposition-design` |
| 10 | `service-design/service-performance-measurement` for measurable impact KPIs |
| 11 | `service-design/service-ecosystem-mapping`, `ecosystem-platform-design` |
| 12 | `business-model-design`, `viability-model`, `strategy/pricing-strategy`, `servitization-model-design`, `ai-native-business-model` |
| 13 | `technology/cloud-architecture` |
| 14, 15, 21 | `strategy/assumption-audit`, `business-experiment-design` |
| 16, 20 | `service-design/service-concept-prototyping` |
| 17 | `strategy/narrative-builder`, `strategy/business-case-builder`, `strategy/kpi-architect` |
| 24, 25 | `opportunity-framing`, `strategy/market-mapping`, `strategy/assumption-audit` |
| 26, 28, 29 | `strategy/kpi-architect`, `business-experiment-design` |

## Optimizations/Gotchas
- **Do not skip 01.** A concept with no funded objective has no gate to pass. The sponsor co-creates 01; a canvas the sponsor never saw does not count as signed.
- **Needs before ideas.** If the user opens with "here is my idea", write it to the 06 idea pool and run 01–05 anyway, or mark the run "solution-first, high risk" in the spine. Do not silently reorder the method.
- **Guesses are legal early, fatal late.** 02 and 03 hold `[I]` guesses. By 14, the problem, the group and the willingness to pay need `[O]` evidence or the verdict is ITERATE.
- **The paper canvas is a prompt, not the work.** A filled box with one adjective fails. Each skill states a Quality test that a box must pass.
- **Impact is not decoration.** 01, 06, 07, 08, 10, 14 and 17 each carry a social/environmental field. Quantify or mark unknown. No claim the numbers do not support (Soul: never oversell).
- **Speed with agents is allowed, validation by agents is not** (conventions §6).
- **Management first.** The book finds the most successful LSC projects start by coaching management on the process, the tools and the values of autonomy and transparency, and that managers must state the what, not the how. If the sponsor has not been coached, run a one-hour briefing before canvas 01.
- **Protect the calendar.** The Helen and Wärtsilä cases both name time as the first blocker: people with calendars booked for months cannot run lean. Get dedicated time written into 01's risks and the 18 capacity plan.
- **Plan the handover to build.** The Telia case: after the canvases, the team had to slice each major finding into a separate development item. That is what 16, 27 and 20 now do; do not end a run at 15 or 17.
- **Persona lens:** every artifact leads with the business outcome, then product, then technology. For manufacturing and as-a-service concepts, route 12 through `servitization-model-design`.
- **Confidential client data stays in `output/` and the vault.** Interviewee names and client numbers never go into this skill folder or a public repo.

## Sources
Lean Service Creation Toolbox v3.0.5, Futurice Ltd, CC BY-SA 4.0 (the 23-page canvas PDF supplied by the principal). Public overview: https://futurice.com/lean-service-creation. Method additions marked **[house]** in each skill. Tools licensed and attributed per [lsc-conventions.md](references/lsc-conventions.md).
