# Brief Style Guide

Read this file in full before drafting the PDF in Step 6. It encodes the genre, the four canonical structural variants, the writing rules, how the persona drives writing, the rules for implicit audience-targeting, and the visual lexicon with rendering guidance.

**Contents:**
1. Genre — what this is and what it isn't, plus the HARD RULES
2. The four canonical structural variants — pick one per design decision 9
3. Writing rules
4. Reference examples — see `assets/reference_brief_example.md`
5. How the persona drives writing
6. Implicit audience-targeting — the most important rule
7. Visual lexicon — devices, when to use, rendering guidance

---

## 1. Genre — read this carefully

This is an **intelligence brief** in the active employer's house style (pack `brand.house_style`; its CTA section is the pack's `brand.cta_heading`, written below as "How <employer> can help"). It reads like a competitive-intelligence product or an investor research note — what selected companies / programmes are saying publicly, what data shows them actually doing, where the two diverge. It is *for* one specific reader but it is not *about* them.

**Negative space — what this brief is *not*:**
- **Not a stakeholder profile.** No "About [Name]" section. No "What [Name] is saying." The reader's name, biography, and direct quotes do not appear in the body.
- **Not a sales pitch.** "Lead with X" / "Avoid Y" framings appear only in the dedicated "How <employer> can help" section, and even there, restrained — three paragraphs maximum, no quoted talking-point scripts.
- **Not generic exec-profile content.** "Visionary leader with extensive experience" type sentences are forbidden. Every adjective must trace to a source.
- **Not a wall of bullets.** Prose-first. Bullets only when content is genuinely a list.
- **Not bound to one structure.** The brief admits multiple canonical structural arrangements (section 2). Persona drives the choice.

**HARD RULES — the two non-negotiable constraints:**
1. **Stakeholder absence from the brief, entirely.** The stakeholder's name, direct quotes, LinkedIn posts, personal biography, and any "Prepared for [Name]" header line do not appear *anywhere* in the brief. The audience-of-one targeting is *fully implicit*, achieved through subject narrowing, finding selection, forward call direction, structural choice, and visual choice — never through naming the reader.
2. **"[Reader's business unit] read." paragraphs — required floor (v5).** Use the *business unit name* ("Power Systems read.", "Group Digital read.") — never the person's name. Inline paragraphs, not callout boxes. **Minimum 2–4 per brief.**

---

## 2. The four canonical structural variants

Design decision 9 picks one. Each variant has a fixed section ordering; content is persona-driven, order/shape follows the variant. The variants are well-tested patterns, not exhaustive — if the persona genuinely fits none, escalate at Step 3 / 4A rather than forcing a fit.

### Variant A — Theme-first (Reference A, Earnings Narrative Tracker)
**When:** narrative-only data, angle is *narrative shift over time*, time-pressed senior reader tracking how the field changes in CEO commentary.
**Structure:** title/subtitle → Key Findings at a Glance (3–5 stat blocks) → Narrative Direction Heatmap (subjects × themes × direction) → Headline Findings (3–5 numbered) → per-theme deep dives (time-series chart + trajectory prose + Vocabulary Evolution stage table + optional "[BU] read." paragraph) → Competitor Narrative Scorecards → Forward Signals (double table) → Methodology.
**Native visuals:** stat blocks, narrative direction heatmap, time-series line charts, vocabulary stage table, competitor scorecards, forward-signals double table.

### Variant B — Company-first deep dives (Reference B, Industrial Quartet)
**When:** narrative AND behavioural data both available; M&A / partnership / deep competitor analysis; value is in pairing what each subject says with what they're building.
**Structure:** title/subtitle → Executive summary (dense framing + 3–5 numbered findings + italicised "Headline view") → Dataset overview → company-by-company deep dives (fixed 4-part substructure per subject: **What management is saying / What the data shows / Where it aligns / Where it diverges**, + italicised "in one line" closer, + optional "[BU] read.") → narrative-vs-data quadrant matrix → functional themes → geographic strategy → frontier roles → cross-company synthesis → 12–18-month forward calls (+ watch list) → How <employer> can help (3 paragraphs) → Methodology.
**Native visuals:** stat blocks, hiring/data-composition table, 4-quadrant matrix, functional-themes table, geographic table, 4-part deep-dive prose blocks, frontier-roles list.

### Variant C — Quadrant-first
**When:** positioning / portfolio / strategic-bet decisions; "where does our organisation sit relative to the field." The 4-quadrant matrix is the centerpiece.
**Structure:** exec summary (matrix as anchor + one stat block + 3 findings) → the matrix (large) → one section per quadrant → forward calls → How <employer> can help → Methodology.
**Native visuals:** the 4-quadrant matrix (large), stat blocks, small per-quadrant sparklines.

### Variant D — Capability-first
**When:** CIO/COO/capability-build readers deciding where to invest in talent/platforms/capabilities. Organised by capability, showing where each subject sits on each.
**Structure:** exec summary (capability-gap/lead stat blocks + findings) → capability map (heatmap capability × subject) → per-capability cross-subject deep dives → capability gap analysis (implicit reader positioning) → forward calls on capability evolution → How <employer> can help → Methodology.
**Native visuals:** capability heatmap (centerpiece), role-cluster bars, frontier-roles list, capability trajectory sparklines.

### Choosing between variants — starting priors, not lookup answers
| Reader posture (persona §6) | Data layer | Recommended start |
|---|---|---|
| Scanner / time-pressed / numbers-first | Narrative-only | Variant A |
| Deep reader / comparison-driven | Narrative + behavioural | Variant B |
| Strategist / portfolio-thinker | Either | Variant C (or B+C hybrid) |
| CIO / COO / capability-builder | Either | D+B hybrid |

**The cross-read angle (DD2) overrides reader posture when they conflict.** The angle is what the brief *answers*; the posture is how it's *delivered*. Answer first.

### Reusable substructures across variants
- The 4-part deep-dive substructure (saying/shows/aligns/diverges) is native to B, reusable in A (per theme) or D (per capability).
- The 4-quadrant matrix is C's centerpiece, appears as Section 3 in B.
- Competitor scorecards are native to A, can append to B/C/D.
- Stat blocks are used in all four.

### Hybrid variants — the most common real-world shape
Outer frame + inner substructure. Common: **D+B** (capability outer, B 4-part inner — best for CIO/COO who also want per-subject visibility); **B+A** (company outer, theme appendix — Industrial Quartet is effectively this); **C+B** (matrix centerpiece, B deep-dive appendices); **A+B** (theme outer, scorecards close). Name the hybrid explicitly in DD9 ("Variant D outer frame, Variant B 4-part substructure per capability"). The audience-of-one test applies to the *outer frame*.

### Note on variant maturity
A and B have shipped reference briefs. **Variant D** has a working template (Reference C, defence/aerospace CIO test case). **Variant C has no shipped reference yet** — treat the template as a starting point, expect to iterate; if strained, fall back to a B+C hybrid.

---

## 3. Writing rules
- **Specifics or silence.** Every claim needs a number, date, named source, or named programme. "They care about AI" is forbidden; *"Lockheed has built 16,000 AI Agents via Genesis since the start of 2025"* is the bar. If a section can't meet it, write "Limited public signal" rather than fill.
- **Absence as a finding.** A signal *consistently* missing across the whole set (none discloses production-deployment numbers) is itself a cross-read finding, often sharper than any positive one. **Guard:** distinguish a *true* absence (ladder run, cell `exhausted`) from a *gap in your own collection* (cell `partial`, stopped early). Only the former is a finding.
- **Numbers, not adjectives.** "111 Staff Enterprise Architect listings" beats "extensive enterprise architecture hiring." Round only when sources do.
- **Quote density and source.** 4–8 direct quotes across the brief, attributed inline (speaker + outlet + date). **Quotes come exclusively from the subjects' executives, analysts, or publications — never the stakeholder.**
- **Quiet authority.** Don't sell. State what is true, with sources. Let the reader draw the conclusion.
- **Opinionated but earned.** Strong calls welcome when the data supports them; hedge when honest, never to play safe.
- **"In one line" closers.** Each major deep dive and the Executive Summary end with a single italicised summary sentence.
- **Three-pattern reveals.** "Three things stand out" / "Two patterns" is compact and scannable — don't force it.
- **Restrained "How <employer> can help" voice.** Three paragraphs max, no bullets, no quoted talking-point scripts, no "we recommend."
- **"[BU] read." paragraphs — required minimum 2–4** (v5). Inline, lowercase "[Business unit] read.", situational contrast — **NOT directive translation** ("X is your benchmark"). If a subject yields no sharp contrast, write a thinner one rather than skip.
- **Length target.** 1,500–2,500 words of body across 5–8 dense PDF pages.
- **Pagination and density (v7.3).** Do **not** force a page break before every section — the brand default `h2 { break-before: page }` produces sparse pages with many short sections and balloons a 5–8-page brief to 12–14. Reserve hard breaks for genuinely major sections; let short sections flow or combine. A numbered section stranded on a largely blank page is a density failure (§9 flags it). Fix by consolidation, not more breaks.
- **British English.** organisation, behaviour, programme, analyse, recognise.

---

## 4. Reference examples
`assets/reference_brief_example.md` contains three: **Reference A** (Earnings Narrative Shift Tracker, theme-first, narrative-only, uses "Power Systems read." twice), **Reference B** (Industrial Quartet, company-first, narrative + hiring, uses "[BU] read." zero times and writes the reader's employer at group level — **the v5 cautionary example, not the standard**; read for structure, not for its handling of the reader's-employer subject), **Reference C** (Variant D capability-first working template, test-case-grade). They are examples, not templates.

---

## 5. How the persona drives writing
The persona is invisible to the reader but visible in every paragraph via the 10 DDs. Eight places to keep it in working memory: (1) structural arrangement (DD9); (2) visual lexicon (DD10); (3) subject narrowing (DD7 — the narrow slice); (4) finding selection (DD8 — which true thing to surface); (5) vocabulary register (DD6 — reader's terms, avoid abstractions they roll their eyes at); (6) evidence selection (DD6 — lead with what persuades them); (7) frontier focus (DD4 — surface the non-obvious, suppress the obvious-to-them); (8) forward calls direction (DD5 — ≥1–2 implicit-reader-targeted). If a paragraph traces to none of these, cut it — even if true and well-sourced.

---

## 6. Implicit audience-targeting (the most important rule)
The brief must be implicitly audience-targeted from the first sentence — through every subject choice, finding selection, forward call, structural and visual choice — **not** through a callout telling the reader what each section means for them.

**The test.** If a different senior exec at the reader's company picked it up, they should be able to tell within the first two pages that it was *not* written for them — the structure, subjects, angle, visuals, questions implicitly answered, and vocabulary would all feel slightly off-target. **The wrong-reader test (Gate 3) should pass on paths 1–4 below alone — without relying on [BU] read paragraphs.** Paths 1–4 are load-bearing; the [BU] read paragraphs are a *separate* required reinforcement floor (path 5, Gate 4).

**Five ways implicit targeting shows up:** (1) structural arrangement (DD9); (2) subject narrowing (DD7 — *the single most load-bearing element*); (3) finding selection inside each subject (DD8); (4) forward calls direction (DD5 — balance implicit-reader with industry-context; the implicit ones don't use "you should"); (5) "[BU] read." paragraphs (required 2–4, v5 — situational contrast, distributed, never directive translation).

**Correct use** (Reference A): *"Power Systems read. The reader's business manufactures primarily outside the US. Its tariff exposure is chiefly retaliatory risk on US-bound exports, not the import-cost inflation US-headquartered competitors absorb..."* **Incorrect** (directive translation): *"Read for [reader's company]: [Subject]'s programme is the public reference point for what [your programme] could look like, so [reader's company] should treat this as the benchmark."* Don't do the second.

**What "implicit" means:** the targeting is built into content/structural/visual choices, not bolted on as commentary. Every paragraph and visual passes: *"why this fact / chart / arrangement, for this reader, in this seat, at this company?"* If it survives, it's in; if not — even if true and well-sourced — it's out.

---

## 7. Visual lexicon
**Rendering stack (brand styling mandatory).** matplotlib with the pack colour cycle (`employers/<active>/brand/palette.json`: `cycle` in order, `grid` for grid/spines with top+right removed, `text` for axis labels; PNG at 300 DPI, `bbox_inches='tight'`). Heatmaps: `imshow` with the palette's sequential `heatmap` ramp. Tables: styled HTML via `brand.css`. Stat blocks: HTML typography, no chart library. PDF: WeasyPrint + `brand.css` + `print.css`. **Never substitute non-brand colours to "look professional"** — degrade to the palette's greyscale (`text` / `grid` / `fills`).

**Render priority when time is tight:** (1) stat blocks; (2) the variant's native primary visual; (3) time-series if the angle is shift-over-time; (4) secondary tables; (5) tertiary devices (can degrade to prose lists).

**Device catalogue:** stat blocks · narrative direction heatmap · time-series line chart · 4-quadrant matrix · vocabulary evolution stage table · competitor scorecards · geographic table/heatmap · 4-part deep-dive prose block · forward signals double table · capability heatmap · role-cluster bar chart · partnership stack diagram · forward-calls timeline · per-subject deep-dive chart. Each has a persona signal and a render note (matplotlib device or styled table).

**Visual richness — scale to needs, no upper cap** (v6.1 retired the "4–6 devices" cap). Drivers of higher count: more DD1 subjects, more DD2 dimensions, per-subject deep dives that benefit from local visuals (typical for Variant B), 4+ forward calls, a visual-scanner reader. **HARD floor:** stat blocks + ≥1 non-table primary visual + ≥1 secondary device — a brief whose only visuals are stat blocks + styled tables fails the floor. **Cut a visual ONLY when** it duplicates another, decorates without analytic load, or can't be honestly supported by data. Reference points: Reference A ~7 charts/tables + 4 scorecards; Reference B ~5; a 3-subject × 5-capability Variant B brief may legitimately want 8–12.
