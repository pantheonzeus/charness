---
id: competitive-porter-teardown
aliases: [competitive-porter-teardown]
name: "Competitive & Market Teardown → Porter 5 Forces"
category: sales
description: Given a company and a goal, tear down its business units, their competitors and those competitors' digital businesses, then synthesize a Porter 5 Forces analysis and a goal-driven strategic reframe.
triggers: [porter 5 forces, competitive analysis, market teardown, analyse this company, analyze this company, wettbewerbsanalyse, konkurrenzanalyse, where are competitors ahead, digital competitor teardown, strategische marktanalyse, company + goal analysis, tear down this company, competitive intelligence deep dive]
tags: [sales, competitive-intelligence, porter-five-forces, market-research, strategy, digital-business]
related: ["[[company-challenger-brief]]", "[[audience-of-one-report]]", "[[proposal-challenger]]"]
modules: [file-backed-state, file-backed-handoff, evidence-backed-answering]  # see ../../MODULES.md
requires:
  tools: [web_search, web_fetch]
  optional: [agent-fan-out]
status: active
version: 1
created: 2026-07-25
updated: 2026-07-25
vault_writes: ["cbrain/Clients/*", "cbrain/projects/*"]
---

# Competitive & Market Teardown → Porter 5 Forces

## Contract

- **Input:** a **company** (name or website) and a **goal/task** — what the analysis is *for* (a hearing, a pitch, an investment thesis, a board deck). The goal is not optional context, it is the steering variable — without it this degrades into a generic report instead of a usable piece of advice.
- **Output:** a cited strategy dossier at `output/YYYYMMDD-<company-slug>-competitive-porter-dossier.md`, plus durable run state under `output/.runs/YYYYMMDD-<company-slug>-competitive-porter/` (control spine + evidence registry, per Charter §4).
- **Tools:** `web_search`/`web_fetch` for research; the Agent tool for parallel per-unit research when the company has multiple business units (see Step 1).
- **Done-when:** every Porter force is rated with evidence; every business unit in scope has ≥2 named competitors **with a digital-business assessment each**; the evidence gate has run; the synthesis names 2–3 reframes that answer the stated goal, not generic industry commentary.

**Not for:** a single meeting-prep brief on one company with no BU fan-out and no Porter requirement — that's the lighter `[[company-challenger-brief]]` (still the right tool for "I have a meeting Tuesday, brief me"). Not for a named-individual outreach brief — that's `[[audience-of-one-report]]`. This skill is for when the ask is a genuine strategic teardown: multiple competitors, their digital businesses, and a structured five-forces view, in service of a stated goal.

## Required inputs — clarify before researching

At minimum: the **company** and the **goal**. If the goal is missing, ask for it before starting — a short prompt works:

> "To make this a piece of advice rather than a report, tell me what it's *for* — a pitch, a hearing, an investment call, a board decision. That's what tells me which findings matter and how to frame the synthesis."

Also useful, not required: scope (whole company vs. named business units only), depth (quick/standard/deep — same calibration logic as `company-challenger-brief`), and language.

## Step 1 — Structure scan: decide the fan-out shape first

Before researching competitors, establish the company's actual shape. This determines everything downstream — don't skip it or default to a fan-out out of habit.

- **Multi-BU / multi-division / multi-subsidiary company** (e.g. a group with named divisions, each with its own P&L or market): fan out — one parallel research agent per unit, file-backed (see Step 2).
- **Single-business company** (one product line, one market): run the whole teardown in one pass, no fan-out. Forcing a fan-out here is manufactured busywork, not thoroughness — Simplicity First applies.
- **Ambiguous** (a company with product lines that aren't really separate businesses): use judgment; when in doubt, fewer, richer units beat many thin slices. State the decision and why in the run's control spine so it's auditable, not silent.

## Step 2 — Per-unit competitive & digital research

For each unit in scope (or the single business, if no fan-out), the research protocol is the same — this reuses the sourcing discipline from `[[company-challenger-brief]]`:

1. **Identify 2–5 named competitors** — real, verifiable ones. If a candidate name was hypothesized up front (by the user or a prior brief) and cannot be verified, say so explicitly and drop it — never invent a competitor to fill a slot. Correcting a wrong starting hypothesis is a quality signal, not a failure to flag quietly.
2. **What is their digital business** — platform, IoT/connectivity, software, service/subscription model, app, cloud analytics. Cite the source. Absence of a public digital offering is *absence of evidence*, not evidence of absence — say which one it is.
3. **Where are they ahead of the target company, concretely** — not "they're more digital," but the specific capability, live vs. roadmap, or business-model difference.
4. **Where do they apply pressure** — price, niche, digital maturity, servitization, consolidation, regulation.
5. **Market frame** — size/growth (flag commercial market-research estimates as directional, not fact — they routinely disagree by an order of magnitude across providers), the 2–3 structural forces reshaping it.

**Multi-unit fan-out mechanics** (when Step 1 said fan out): follow `_shared/delegation-handoff.md` exactly — write one `TASK.md` packet per unit under `output/.runs/<run>/children/<unit>/TASK.md` containing this protocol plus unit-specific context (candidate competitor names to verify, known company facts). Launch one Agent call per unit, fresh context, in a single parallel batch. Each writes `children/<unit>/RESPONSE.md`. **Reopen every RESPONSE.md file yourself before synthesizing** — never trust an inline agent summary as the carrier of record. The parent stays the orchestrator; it does not also do the per-unit web research redundantly.

## Step 3 — Porter 5 Forces (the fixed backbone)

Full worksheet and per-force guidance: `references/frameworks.md`. In brief: rate each of the five forces (rivalry, supplier power, buyer power, threat of new entrants, threat of substitutes) at group/company level, then flag where a force materially diverges by business unit. Every rating carries evidence and a **goal-relevant implication** — a force rated "high" with no bearing on the stated goal is noise, cut it or subordinate it.

**Honesty rule:** if a force genuinely wasn't researched (commonly supplier power — it's rarely covered by the same sources as competitor/digital research), tag it `[VIEW] — not researched`, don't manufacture a rating to complete the grid. An incomplete-but-honest Porter grid beats a complete-but-fabricated one.

## Step 4 — Adaptive supplementary lens (only if the goal demands it)

Porter is always the backbone. Reach for a second lens only when the stated goal genuinely needs it — selection rule and short templates in `references/frameworks.md` (digital-maturity matrix, value chain, SWOT, Wardley mapping). Adding a lens because it's available, not because the goal requires it, is the framework-zoo failure mode this skill is built to avoid.

## Step 5 — Goal-driven synthesis (the point of the skill)

Research makes you informed; this step makes the analysis *usable*. Write 2–3 reframes — each a specific, defensible insight that connects a researched competitive/Porter finding directly to the stated goal. Test: could you say this reframe out loud in the room the goal is about (the hearing, the pitch, the board meeting) and have it land as *this specific analysis*, not generic industry commentary that would fit any company in the sector? If a reframe fails that test, cut it or sharpen it.

Do not skip counter-findings that complicate the narrative — a reframe that says "actually, on this dimension we're already ahead, we're just quiet about it" is often the most valuable one in the set (see the Company A / Competitor X-vs-Competitor Y precedent below), because it changes the goal-holder's action, not just their awareness.

## Step 6 — Evidence gate

Run the pass in `_shared/evidence-gate.md` before shipping: every release-critical claim tagged `[CITED]`/`[MODEL]`/`[VIEW]`; market-size figures from commercial research aggregators flagged as directional; "no public digital offering found" claims explicitly marked as absence-of-evidence; DNT/do-not-cite names (if any apply to the run, e.g. carried over from a linked hearing-prep run) respected; no fabricated competitor or capability ships to survive a first informed follow-up question.

## Output structure

Mirrors the reference dossier (see Worked Example below):

1. **Executive TL;DR** — 3-4 bolded bullets: the company in one sentence, the competitive force that actually matters, the one digital vulnerability/opportunity everything hangs on, and (when found) a counter-finding worth a beat of surprise.
2. **Company/BU structure** — the units in scope and what each does, one line each.
3. **Unit teardown** — one section per unit (or one section total if no fan-out): named competitors, their digital business, where ahead, where pressure comes from, market frame.
4. **Porter 5 Forces** — group-level table with per-force rating, evidence, goal-relevant implication, and BU deltas where they diverge.
5. **Synthesis** — the 2-3 goal-driven reframes (Step 5).
6. **Sources & evidence** — every claim traceable; link to per-unit RESPONSE.md files if a fan-out ran, rather than re-pasting every citation into the main dossier (keep it scannable).

## Living Knowledge Graph

Create/update the company's vault note and link it bidirectionally to relevant people/topics (Charter §6) — a competitor teardown on a company is exactly the kind of new knowledge that shouldn't stay an island.

## Operating principles

- **Business → Product → Technology.** The synthesis is a commercial/strategic argument first; the technology detail (which platform, which sensor) is evidence for the argument, not the point.
- **Name your confidence.** A filed number or a live-product page is a fact; a market-research aggregator figure or a privately-held company's revenue is an estimate — label it (Soul.md).
- **Correcting a wrong hypothesis beats confirming it.** If the user's or a prior brief's assumption about a competitor doesn't survive research, say so plainly and explain the correction — this is the single most valuable thing the research step can surface, not a defect to bury.
- **Don't force symmetry.** Not every unit needs equal depth; not every force needs equal weight; not every goal needs a second lens. Match effort to what the goal actually needs.

## Worked example

The reference run: Company A (5 divisions, multi-BU fan-out), goal = prep for a "Director Digital Business" hearing round. Produced `output/20260724-company-a-competitive-porter-dossier.md` from `output/.runs/20260724-company-a-competitive-porter/`. Notable precedent worth re-reading before a first run of this skill: the research **corrected two starting hypotheses** ("Competitor Y is clearly ahead of Competitor X digitally" turned out to be a positioning gap, not a technology gap; "Product E = a sales/logistics tool" was actually a cloud rebuild of the existing rental software) and **dropped two unverifiable competitor candidates** (two candidates) rather than forcing them into the tables. Both are exactly the behavior Step 2 and Step 5 above are written to reproduce.

## Gotchas

- **Supplier power is the force most often silently skipped** — it rarely surfaces in the same competitor/digital searches as the other four. Budget an explicit check or tag it `[VIEW] — not researched` rather than let it quietly default to "medium."
- **Market-size figures disagree wildly across commercial aggregators** (an order of magnitude apart is common) — cite a range with the caveat, never a single confident number from a single paid-report snippet.
- **A fan-out that returns thin per-unit findings is a sign to widen the search, not to pad the synthesis** — a unit with genuinely little public digital footprint (e.g. a small or newly-spun-off division) should say so honestly rather than manufacture competitors or capabilities to match the other units' depth.

**Feedback & Skill Verification**
- Would you like to provide feedback to optimize this workflow or execution?
- Should we update this skill (or add a new one) based on how this went?
