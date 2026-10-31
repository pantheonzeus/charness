---
id: audience-of-one-report
aliases: [audience-of-one-report]
name: "Audience-of-One Intelligence Brief"
category: sales
description: Generate a tailored "audience of one" intelligence brief (PDF, your firm's house style) to support sales outreach to a named individual — an implicit, cross-read intelligence product that earns a first conversation.
triggers: ["reaching out to [name] at [company]", "help me open a conversation with", "build an outreach brief", "research this stakeholder", "I'm pitching to", "audience of one", "LinkedIn PDF export", door-opener, prep before a meeting]
tags: [sales, outreach, intelligence-brief, business-development, competitive-intelligence, pdf]
related: ["[[proposal-challenger]]", "[[company-challenger-brief]]", "[[executive-dialogue-planner]]"]
modules: [file-backed-state, evidence-backed-answering, verifier-separation, self-evolution]  # see ../../MODULES.md
requires:
  tools: [web_search, web_fetch]
  optional: [apify, firecrawl, the employer's internal knowledge base (pack brand.internal_kb)]
  bundled-skills: [pdf, the employer's brand skills (pack brand.bundled_skills)]
environment: "Best in Cowork / Claude Desktop (your org's local MCP plugins — branding skill, internal knowledge base — are only visible there). Core workflow runs in web chat; plugin-dependent extras degrade to fallbacks with a method note."
assets: []
status: active
version: "7.9"
created: 2026-07-05
updated: 2026-10-23
---

# Audience-of-One Intelligence Brief

> **Brand comes from the active employer pack.** Palette, font, house style, CTA heading, brand bundled skills, internal knowledge base and reference briefs live in `employers/<active>/brand/` (`palette.json`, `fonts/`, `house-style.md`, `examples/`) and the pack profile's `brand.*` keys (`python3 scripts/employer.py get brand`). The persona engine, gates and registries here are employer-agnostic. **No pack or no `brand/`** → neutral fallback: greyscale palette, a system sans, CTA heading "How we can help", no internal-KB query; record the fallback in the audit log.

## What this skill does

This skill helps a salesperson reach out to a specific named individual at a target company — earning a first conversation through a genuinely useful intelligence artefact rather than a cold ask. It also works as prep ahead of an early meeting. The output is a **PDF intelligence brief** in the narrative-vs-data genre — a cross-read across 3–5 narrow subjects (companies, programmes, or sectors) the stakeholder cares about, styled in your firm's house brand. Once the meeting is actually on the calendar, `[[executive-dialogue-planner]]` turns this brief's findings into the dialogue plan and hook for that specific conversation.

**Genre matters.** The stakeholder is the *audience*, not the subject. The brief reads like a competitive-intelligence product or an investor research note — what selected companies / programmes are saying publicly, what data shows them actually doing, where the two diverge. The brief is *for* this person; it is not *about* this person.

**HARD RULE — Stakeholder name placement, conditional on delivery mode.** The user picks mode at the start (see "Required inputs to start"). Default is (a) implicit.

- **Mode (a) implicit (default).** The stakeholder's name, direct quotes, LinkedIn posts, interview soundbites, personal biography, and any "Prepared for [Name]" header line **do not appear anywhere in the brief** — not the body, not the header, not the metadata. Audience-of-one targeting is fully implicit: subject narrowing, finding selection, forward call direction, structural choice, visual choice, and "[Reader's business unit] read." paragraphs.
- **Mode (b) explicit.** The stakeholder's name + role + employer may appear in **two places only**: (1) the header line ("Prepared for [Name], [Role] at [Company]"), and (2) optionally a single short opening framing paragraph. **Nowhere else.** The body continues to use the business-unit name and never the person's name. Direct quotes from the stakeholder still do not appear. The implicit mechanisms are still required — explicit name is additive cover-surface signal, not a replacement for personalisation work.

**The v5/v6 personalisation floor (applies under BOTH modes).** "[Business unit] read." paragraphs are required, **minimum 2–4 across the brief** — a load-bearing element of implicit targeting alongside subject narrowing, finding selection, and forward calls. See Step 6 for placement rules.

**Two artefact streams — buyer-facing brief vs Claude-internal audit log.**
- **The brief (PDF) — buyer-facing.** Its Methodology covers only what the *buyer* needs to evaluate the claims: data sources, time window, classification approach, and limits that genuinely affect conclusions. No audit-gate documentation, persona-derivation notes, or mode-selection records — exposing internal QA reads as the artefact showing its own homework.
- **The internal audit log (`/home/claude/audit_log.md`) — Claude-facing.** Everything that exists for QA: which gates ran, what they returned, remediation, persona decisions, mode-selection record, source-fetch log. This is what the *salesperson* uses to defend the brief if challenged. Create it at the start of Step 1 and append throughout.

**User-facing prompts use plain language — no skill jargon.** The user is a salesperson, not a skill author. Every chat question uses ordinary words: no "audience-of-one targeting", no "persona §4", no "DD7", no "Reference A/B". Internal vocabulary stays in the skill text Claude reads.

**Skill constraints prevent laziness; they don't substitute for judgement.** The mandatory registries (`programmes.json`, `subject_metrics.json`, `dd10_visuals.json`, `quotes.json`), mechanical checks, MANDATORY reads, and audit gates exist only to prevent specific observed failures (skipping the visual-render step, fabricating programme names, self-passing gates, shipping subject deep dives without stat blocks). Where the skill says "deep", "rich", "well-attributed" — the judgement of what that means is Claude's. Encode observed failures as mechanical gates; encode aspirations as reference patterns plus soft guidance; trust judgement to thread the path.

**Persona is the thinking engine.** Steps 1–3 build a detailed persona. The persona does not appear in the brief — it drives every content, structural, and visual choice. In Step 4A you translate the persona into **10 explicit design decisions** (8 content + 2 form). The reference briefs in `assets/` show three configurations — examples of the genre, not templates.

**Why order matters.** Persona (Steps 1–3) → design decisions (Step 4A) → source plan (Step 4B) → collection (Step 5) → drafting (Step 6). Each step depends on the previous; skipping ahead poisons everything downstream.

## Operating doctrine — read first, steer by this

Everything below is downstream of six invariants. **Steer by these.** The gates and registries are mechanical backstops for when one lapses under pressure — they catch slips; they are not the thing you optimise for.

1. **It is an intelligence product, not sales material.** Reads like an investor research note, not a pitch. A senior buyer extends trust to analysis that stands on its own and withdraws it from anything that smells like selling.
2. **The reader is the audience, never the subject.** The brief is *for* this person and *about* selected companies/programmes — their name and biography never appear in the body.
3. **Narrative vs. numbers is the engine — find the tension.** Each subject gets a says / shows / align / diverge cross-read; the value is the *gap* between the public story and what the data does.
4. **Every claim traces to something fetched; if you can't source it, it does not exist.** A name, number, or quote with no fetched source is out. **#4 also runs in reverse (v7.4):** a sourced low / zero / absent value in one proxy measures that lens, not reality — it bites hardest on small-base cells, the reference entity, and negative/gap claims. See `references/data_render_doctrine.md` items 1–3.
5. **Confirm the read before you build on it.** Validate persona / company / spine with the user *before* it cascades into ten design decisions and a rendered brief.
6. **Internal QA stays internal.** Gate output, persona derivation, design-decision reasoning, mode records go to the audit log — never the buyer-facing brief or the chat hand-off.

**On adding to this skill (the anti-bloat rule).** Before adding a new gate or rule, check whether the failure is a fresh instance of one of the six invariants; if so, sharpen the invariant or existing gate rather than minting a new one. Put new mechanical-gate *implementations* in `references/gates.md`, not here.

**Data-integrity & render doctrine (v7.4).** `references/data_render_doctrine.md` collects the interpretation, comparability, second-source, alternatives, external-data and render rules. Read it at Step 4A, again at the Step 5 → Step 6 boundary, and before render.

---

## How this skill is organised

Read the bundled reference files only when you hit the matching situation:

- `references/brief_style.md` — genre, the 4 canonical structural variants, writing rules, how the persona drives writing, implicit audience-targeting, the visual lexicon. **Read before Step 6 (every time).**
- `references/edge_cases.md` — skip-questions, low-footprint stakeholder, vague pushback, wrong data-layer file, sales-content requests, reputational signals, failure-modes checklist. Read the matching section.
- `references/gates.md` — **the verification machinery.** Full implementations of the seven gates, the §8 completeness audit, the §9 render-inspection, and the §10 data-integrity sub-checks. **Read at the Step 5 → Step 6 boundary and before render.**
- `references/data_render_doctrine.md` — data-integrity & render doctrine (v7.4+).
- `references/regression_cases.md` — concrete shipped failures as eval anchors. A change that lets any regress is a regression.
- `employers/<active>/brand/``examples/reference_brief_example.md` — three condensed reference briefs (A theme-first, B company-first, C capability-first). **Read all three before Step 6.** Absent → work from `references/brief_style.md` alone and say so in the method note.

## Where this skill runs

Best output is in Cowork or Claude Desktop — the employer's internal plugins (pack `brand.internal_kb` and `brand.bundled_skills`) are local plugins visible only there. In every environment the core workflow (LinkedIn scraping, web search, deep reads, data analysis, PDF generation) works; plugin-dependent extras degrade to fallbacks and the method note flags what was missing. Don't refuse to run in web chat — run it and note the limits.

## Required inputs to start

At least one of: the **stakeholder's name** ("Alex Renner at Meridian Power Systems"), their **LinkedIn URL**, or a **PDF export** of their LinkedIn profile. The **company** is also needed (usually inferable). Industry/sector is inferred from the company. Anything else volunteered up front (what the outreach is about, relationship stage, internal notes) improves Step 4A — don't demand it.

### Delivery mode — implicit vs explicit name (ask up front)

Before Step 1, ask which mode. Use plain language. Verbatim text to send:

> "Quick choice before I build the brief — two ways it can address [reader's name]:
>
> **(a) No name on the brief (recommended default).** [Reader's name] never appears. The brief looks like a market intelligence report that happens to cover exactly the companies, angle, and questions that matter to them. Reads like serious analysis, not sales material.
>
> **(b) Name on the cover.** The cover says 'Prepared for [Name], [Role] at [Company]', and an opening line may address them directly. The body still doesn't use their name. Reads like a consultant memo written for them.
>
> Most leaders and outreach contexts prefer (a). In cold or warm outreach especially, a prospect who hasn't met you can find their name on the cover off-putting — so (a) is the safer default the colder the relationship. Pick (b) only when the relationship is warm enough that an openly personal artefact will land.
>
> Which one — (a) or (b)?"

Capture the choice in the audit log (not the Methodology). Default to (a) if silent/ambiguous.

### Brief scope — quick / standard / deep (infer, do NOT add a question)

Calibrate **breadth of collection only — never the quality bar.** Infer from the ask; default to standard.
- **Quick** — "quick prep", "cold call in an hour". Narrow to **3 subjects** and Recommended DD3 dimensions only; fewer visuals. *Smaller, not sloppier.*
- **Standard (default)** — 3–5 subjects, Recommended + strongest Optional dimensions.
- **Deep** — "major pitch", "board-level", "go wide". Up to 5 subjects, all confirmed dimensions, per-subject visuals.

**HARD RULE — scope never relaxes a gate.** Quick mode reduces how *many* subjects/dimensions are in scope; it does not lower the floor for the ones that ARE. Every in-scope cell still reaches `collected`/`exhausted`/justified `n/a` and passes Gate 7, quote-verify, comparability, provenance, and the stakeholder-absence rule across all scopes. Record the inferred scope + signal phrase in the audit log.

## Tools this skill expects

**Always available:** `web_search`, `web_fetch` (the default deep-read tool for Step 5), filesystem (`view`, `bash_tool`, `str_replace`, `create_file`).

**Cloud connectors (use if available):** **Apify** (strongly recommended for Step 1 LinkedIn scraping — LinkedIn's self-described keywords make the persona materially better; fall back to web search if absent), **Firecrawl** (optional cleaner page reads).

**Local plugins (Cowork/Desktop only):** the employer's internal knowledge base for prior engagements, named in pack `brand.internal_kb` (skip when null).

**Bundled skills (filesystem — required):** the pack's `brand.bundled_skills` under `/mnt/skills/user/<name>/` (**mandatory** when listed: brand palette, typography, PDF/chart refs, tone of voice; see the pack's `brand/house-style.md`), and `/mnt/skills/public/pdf/`.

### How to find tools at runtime

`web_search`/`web_fetch` are always available. All other MCP tools are **deferred** — load with `tool_search` before assuming absent: `tool_search("apify linkedin")`, `tool_search("firecrawl scrape")`, `tool_search("<internal_kb> lessons")`. The pack's brand bundled skills are filesystem skills read directly with `view`. **The single most common silent failure is not bothering to run `tool_search` and degrading unnecessarily.**

### Graceful fallbacks
- **No Apify** → web search for Step 1 (persona thinner; note it).
- **No internal knowledge base** (pack `brand.internal_kb` null or plugin absent) → skip internal query; note it.
- **Brand bundled skill missing** → flag; render from `employers/<active>/brand/``palette.json` + `fonts/`; with no pack brand at all, use the neutral fallback; record it in the audit log.
- **No data-layer file** → narrative-only is a *full-strength path* (Variant A), not a degradation.

---

## Step 1 — Three parallel research streams

Collect on three dimensions in parallel: the **stakeholder** (1A, basis for persona), their **employer/target account** (1B, basis for subject selection + reader's-employer narrowing), and the **industry/sector** (1C, basis for cross-read angle, frontier focus, industry-peer candidates). Run concurrently; weight by case (high-footprint stakeholder at a low-profile private company → weight 1A; mid-public stakeholder at a name-brand listed company in a fast-moving regulatory environment → weight 1B+1C). All three are **research input, not brief body content.** The HARD RULE on stakeholder placement applies from now on.

### First action — create the audit log

**Before any web search, create `/home/claude/audit_log.md` and write the header.** Hard sequence requirement — Gate 5 verifies it exists. Read the skill version from this file's frontmatter (don't hardcode). Header records: Reader, Mode, Started, Skill version; a note that the log is internal QA (NOT in the PDF); a Step 1 heading to append findings under.

### Second action — create the named-programme registry

Immediately after, `echo '[]' > /home/claude/programmes.json` — the **anti-fabrication mechanism** (added after "AiRR"/"President of Power Systems" fabrications). Every named programme in persona / company brief / brief body must trace to a fetched URL recorded here, with `confidence: high|medium|low`. Programmes at `low` may not be stated as fact ("reportedly" only). If a programme has no entry, it does not exist for the brief. Gate 6 sub-check D verifies before render.

### Third action — create the run-state ledger

`/home/claude/run_state.md` — the tiny control spine (CP0–CP10). Delivery is hard-blocked until every box is `[x]`. Advance it as you go; detailed findings go in `audit_log.md`. **CP8/CP9 are ticked only by `completeness_gate.sh`** (which re-runs the §10 data suite against on-disk artifacts), not by hand.

### Fourth action — create the hand-off spine (`handoff.md`)

A third, deliberately small file — the *content* spine. At each step's close, **overwrite** a short block carrying only what the next step consumes (locked persona spine, confirmed DDs, cells collected, open needs). It changes *what a step reads* (this plus named files, not the whole growing audit_log), keeping context from ballooning. Not gated. Also record the audience in `run_meta.json` (`stakeholder` + `exclude_from_subjects`) so §10-E can enforce that the stakeholder is never plotted as an unflagged sixth subject.

### Step 1A — Stakeholder material (research input for the persona, not brief body)

LinkedIn data is the **foundation** — the person's own self-description, career trajectory, publications, colleague recommendations. If the user hasn't provided it, ask (PDF export > URL > name + company). Decide input, then scrape:

- **Scraping path A: URL** → Apify (`tool_search("apify linkedin")` first). Don't hardcode actor/field names — find a working actor (99%+ success, 4+ stars, no account-level auth), look up its input schema before calling (most failures are silent 0-item returns from wrong field names), then call and re-verify field names on empty returns.
- **Scraping path B: Name search** → run a quick `web_search` for name + company first (spelling check + identity disambiguation), then the name-search actor.
- **If Apify fails** → `web_search` public sources or ask the user to paste visible LinkedIn content. Note thinner persona; continue exactly as other paths do.

**Sanity check before parallel streams** — verify current company matches what the user said and role matches approximately (catches wrong URL / same-name mismatch / stale cached profile). A wrong profile poisons everything downstream.

**Universal parallel launch** (after identity confirmed): Stream W (public web persona — how others frame them, said aloud, recent signal LinkedIn won't show), Stream 1B (company), Stream 1C (industry) all concurrently.

**What to extract — the quotable signals.** Step 4A requires *quoting* persona language, so Step 2's persona must contain **verbatim phrases and directly observed evidence**, not generic descriptors. Flag and copy verbatim: phrases from their own posts; named programmes they're publicly accountable for; specific peers/companies they've named; public talk titles; self-keyworded vocabulary (headline + About); phrases from colleague recommendations. **Not** quotable: generic About-section descriptors ("passionate about transformation"), role-implied claims, your own characterisations. Rough guide for a senior exec with normal activity: 4–8 quotable phrases, 2–3 named programmes, 1–2 named peers, 1–2 talk titles.

**Speaker-network signal — the Stream W query list.** General presence (`"[Name]" "[Company]"`, interview/podcast/keynote, "spoke at", co-authored, "in conversation with", site:youtube.com) + stage-sharing (panel, alongside "[sector keyword]" — stronger signal than passive mentions: paid fees, agreed billing, joint authorship). `web_fetch` the 2–3 most substantive URLs. Capture event/date/co-panellists (→ §4a benchmarks) / topic framing / vocabulary.

### Step 1B — Company / target-account intelligence

Research input for DD1 subject selection + DD7 narrowing, not brief body. Six things (be selective): (1) recent strategic moves 12–18mo; (2) current stated priorities (quote 2–3 verbatim); (3) reader's business unit specifically (numbers/scope/named programmes/peer set — **never fabricate a programme name**); (4) recent investor/analyst questions and concerns (externally-visible pain points); (5) tech/digital posture signals; (6) internal context via the employer's internal knowledge base (pack `brand.internal_kb`; skip + note if unavailable). Output: 4–6 paragraphs of working notes tagged by DD.

### Step 1C — Industry / sector context

Research input for DD2 angle, DD4 frontier, DD1 industry-peer slot — not an "industry overview" section. Five things (lightest of the three): (1) the 1–2 dominant strategic questions in the sector *specifically*; (2) technology/capability frontier (what peers are publicly hiring/investing in); (3) regulatory/policy/standards environment; (4) recent peer-set movements (raw material for DD1 — **subject-selection input only, NOT per-subject collection**); (5) what's NOT on the agenda but should be (creative-judgment candidates). Output: 3–5 paragraphs tagged by DD.

### Cross-stream synthesis (light touch)

Before Step 2, write one 2–3 sentence note: *"The most interesting thing here is X, surfaced by the intersection of stakeholder signal Y and industry condition Z."* The spine seed (not yet DD2). If you can't write it, the streams aren't rich enough — collect more. This is where creative latitude does load-bearing work.

## Step 2 — Build the persona + company brief + industry brief (design briefs)

Three internal working briefs, none appears in the brief body. Persona is deepest; company + industry lighter unless the case weights them. Don't fill all three to equal depth out of symmetry.

### 2A — Persona (role archetype header + 9 sections)

**Role archetype header (one line).** Place the reader against a sales role archetype — a default register for DD2/DD5/DD6/DD8 that the individual §1–§9 sharpens. Four common enterprise tech-buyer archetypes (reference points, not a closed set): **CDO** (digital product/CX/revenue; "product thinking", "time to market"; avoids "governance/frameworks"), **CIO** (estate/infra/security; "architecture", "resilience", "TCO"; avoids "ship it/sprint"), **CTO** (tech vision/eng culture; "developer experience", "platform", "engineering excellence"; avoids "transformation programme/business case"), **SVP/VP Eng or Product** (delivery; "sprint", "velocity", "capacity"; avoids "board narrative"). Hybrids common (Group CDIO = CDO+CIO). **When the reader doesn't fit** (CFO/COO/CMO/GC/…), build a header from first principles using the same five columns (owns / pressures / vocab-leans-to / vocab-avoids / engagement-levers). The archetype is never a substitute for the individual persona.

Nine sections: (1) role and remit; (2) stated focus areas (their own words, quoted internally); (3) career trajectory + pattern; (4) **who they benchmark against — two distinct lists**: §4a stakeholder-direct (peers/partners *they* personally named) vs §4b direct competitive peer set (who their *company* compares to — **industry-pure** for well-defined-peer industries; a platform vendor named by the person goes in §4a, never §4b); (5) technical depth + vocabulary register; (6) decision style + evidence type; (7) likely pain points on their desk now (specific, not generic); (8) what they already know vs what's new (information ceiling); (9) what makes them engage. Every claim traces to something read; label thin sections.

**Self-check before Step 3 — persona depth.** Signals must be **stakeholder-direct** (they said/wrote/named it, or a named colleague did), not stakeholder-adjacent (true of employer/role/industry, inferred onto them). Audit §4 (≥1 stakeholder-direct benchmark), §6 (≥1 quoted phrase or observed pattern), §7 (≥1 pain point from a stakeholder-direct signal). Test: *would this signal change if the same person moved employer next month?* If no, it's company-adjacent. A persona where §4/§6/§7 are all generic or all stakeholder-adjacent is the single biggest predictor the brief reads generic — dig further or mark the section weak.

### 2B — Company brief (5 fields)

One decision-ready paragraph each: (1) strategic posture in one sentence (specific, quantified); (2) 2–3 live priorities quoted verbatim; (3) reader's BU specifically; (4) 2–3 live concerns from analyst questions/news; (5) posture on the axis the angle turns on.

### 2C — Industry brief (3 fields)

Bullets fine: (1) the 1–2 dominant sector questions, named specifically; (2) industry frontier — 3–5 capability areas at peer-investment level (not abstract themes); (3) one regulatory/policy inflection currently changing peer behaviour.

### Cross-brief seed: the spine sentence

Refine the Step-1 synthesis in light of 2A/2B/2C: *"The brief's spine is X — driven by stakeholder signal Y, company context Z, industry inflection W."* Step 4A translates this into DD1 + DD2.

## Step 3 — Confirm with the user

Present persona + company brief + industry brief + spine, ask targeted questions on the highest-cost-to-be-wrong points. Six questions (focus areas / benchmarks / pain points / company pressure / sector framing / spine sentence) — *"answer any or all, then say 'go'."*

**HARD anti-regression rules:** Ask all six — do not compress to three (that removes the user's chance to flag suppressed questions). **Never include a "subjects" or "peer set" question in Step 3** — DD1 subject selection is a *separate* Step 4A chooser. Persona §4 benchmarks (who they cite) and DD1 subjects (what the brief covers) are different objects validated in different steps. **Never substitute a Step 4A question into the Step 3 slot.**

Handle: edits → apply + re-present briefly; confirm / ambiguous ("looks fine, go") → proceed; vague pushback → the multiple-choice clarifier in `references/edge_cases.md` §3.

**Leave a trace:** append the user's actual response text (or `treated as confirm`) to the audit log — §8 greps for it.

**HARD LINE — showing the DD1 chooser does NOT satisfy Step 3.** Step 3 (six-question persona/company/spine confirmation) and Step 4A's DD1 chooser are two different user turns; Step 3 comes first. Most dangerous on a low-footprint reader — the thinner the persona, the more Step 3 is the *one* place the user can correct it before it cascades. This is the most important quality gate in the skill.

## Step 4A — Translate persona + company + industry into 10 design decisions

The **core mechanic.** 8 content decisions + 2 form decisions.

**Creative latitude — what's fixed and what's open.** Fixed: 10 DDs, 4 canonical structural variants as vocabulary, the audit gates, the HARD RULE. Everything else is judgment. Mechanically picking Variant B every time because it was in the reference is the failure this skill exists to prevent.

**Reasoning before lookup.** Before naming any DD, write (for yourself): (1) what kind of brief this persona + angle actually wants — describe the *experience*, not "a Variant D brief"; (2) which specific signals point this way — **quote the exact phrase** in quotation marks; (3) what alternative you considered and rejected — structurally different, with the specific reader reaction that signals "not for me". Only then name the 10 DDs.

**The 10 DDs cascade, they are not independent lookups.** If a downstream DD doesn't trace cleanly to upstream signals across all three briefs, the upstream is incomplete — go back. Name the specific upstream section(s) each DD traces to.

- **DD1 — Subjects (3–5 named).** Do NOT silently infer one set. Synthesise three sources — §4a stakeholder-direct, §4b direct competitive (industry-pure), industry/capability peers — and present a **chooser** (Option A / B / C), not a single recommendation. **Default: the reader's own employer is NOT a subject** (they already know it; it enters implicitly). For well-defined-peer industries (aerospace, defence, pharma, banking, oil & gas, auto, telecoms, utilities, insurance, FMCG, big-tech — see the industry table in the reference), **Option B (direct competitors) is the recommended default**; A/C only when the angle demands cross-industry. Subject discipline: no thin subjects — a candidate earns its slot only if it yields comparable signal across the confirmed DD3 dimensions.
- **DD2 — Cross-read angle.** Narrative on *what* vs data on *what*. **Preferred default: lead with an AI/digital angle** (your firm's wheelhouse — swap for whichever domain is actually yours) *if* it survives the generic-angle test; otherwise run the honest non-AI angle properly. **Generic-angle failure test (HARD):** would this angle fit the most senior *different* exec at the same companies (group CEO vs Group CDIO)? If yes, it's too generic.
- **DD3 — Data dimensions.** **Claude-derived, never solicited as an open question.** Walk the full standard signal menu item-by-item (earnings-call commitment, hiring, patents/R&D, M&A, content/data assets, partnerships, model/infra strategy, shipping cadence, deployment metrics, regulatory posture, capex, geography, pricing), score each Recommended/Optional with a one-line rationale, and **let the user confirm the set** (wide net → confirm, so a load-bearing dimension isn't silently dropped). Optional weights default equal.
- **DD4 — Frontier focus.** **Reader-programme anchoring (HARD when applicable):** centre on capabilities the reader's *named* programmes are building/competing for — generic industry frontier is secondary context only.
- **DD5 — Forward calls direction.** Balance personal-implicit with industry-context: of 4–5 calls, ≥1–2 carry implicit implications for the reader's org (no "you should" framing); the rest are industry-context forecasts (a peer-set view they aren't running internally — not filler).
- **DD6 — Vocabulary register + evidence selection.** In-register vs out-of-register terms; which evidence persuades this reader.
- **DD7 — Subject narrowing.** For each subject, the specific slice that matters (not "Lockheed Martin" — *Astris AI Factory + Genesis*). **The single most load-bearing element of audience-of-one targeting.** When DD1 explicitly includes the reader's employer, its deep dive MUST be BU-narrowed.
- **DD8 — Reader-question mapping.** For each subject, which specific §7 pain point its deep dive answers. Internal; if a paragraph doesn't land on it, cut it. Second most load-bearing after DD7.
- **DD9 — Structural arrangement.** Pick the canonical variant (theme-first A / company-first B / quadrant-first C / capability-first D) or a named hybrid that fits reader × angle. **Reason, don't lookup** — what axis carries most value? The angle leads; reader processing style is a tie-breaker.
- **DD10 — Visual lexicon.** Pick devices the angle *needs to show* (a shift-over-time angle needs a time-series; a positioning angle a matrix; a capability angle a heatmap). **HARD floor:** every brief renders stat blocks + ≥1 non-table primary visual + ≥1 secondary device. Richness scales to content, no upper cap; cut only for duplication / decoration / unsupportable-by-data.

**Present to user for confirmation** as a single consolidated block: reasoning pass (3–5 sentences) → TL;DR of the 10 → full set (each with choice + specific-signal rationale + upstream trace). DD1 chooser (three labelled options), DD2, and the DD3 scored menu are all confirmed *here, in one turn*. If the user says "just go," proceed on the recommended DD1 option + Recommended DD3 dimensions at equal weight. Leave DD1-choice + DD3-set traces in the audit log. A weak reasoning pass is the single biggest predictor the brief reads generic — if it feels thin, the persona is underspecified; go back.

## Step 4B — Source plan (narrative layer + data layer)

**Narrative layer (Claude collects autonomously):** per subject — 2–3 recent earnings/disclosures, 1–2 named exec interviews on the angle, 1–2 outside-framing features, regulatory/programme/partnership announcements, internal knowledge-base search (pack `brand.internal_kb`, if any). **The narrative layer is NOT the stakeholder's interviews/posts** — those went into the persona; the brief body never quotes the stakeholder.

**Data layer — anti-laziness HARD RULE.** Exhaust autonomous fetch (`web_search` + `web_fetch`) before asking the user for anything. If the data is publicly fetchable, Claude fetches it. If the signal exists publicly but is conventionally accessed via a credentialed tool (Lightcast/Revelio/Bloomberg/PitchBook/Gartner/PatSnap), Claude reconstructs from public sources (careers pages, filings, Yahoo Finance/Stooq, Espacenet/Google Patents, Crunchbase, analyst 1-pagers). Before asking the user, **state explicitly what was tried and failed** with specific tool calls. Apify/third-party scrapers are a **last resort only** — the hiring/job-listing dimension is collected web-first (careers-site counts, aggregator result-page counts, announcement reconstruction). Genuinely user-required: internal CRM/account history, NDA-bound material, the user's own data.

Present the source plan (built from work already done, not asked of the user); ask three quick questions (narrative edits / internal-only sources / URLs already on radar). **Schema inference is mandatory** for any data source (CSV/XLSX/PDF/HTML/JSON/paste/joins) — never ask the user what a column means; print a 5-line schema summary as a notification, not a question. ETL pipeline (ETL-1 inspect → ETL-2 relevance check → ETL-3 analyse tied to DD2/DD3/DD4 → ETL-4 map outputs to sections → ETL-5 cite dataset) runs identically regardless of how data arrived.

## Step 5 — Collect data

**HARD GATE — Step 5 is mandatory and cannot be absorbed into Step 1**, no matter how much Step 1 surfaced. Step 1 collected research input to *choose* subjects and angle; Step 5 collects a structured, per-DD1-subject quantitative profile keyed to the *confirmed* subjects and DD2/DD3/DD4. Build `/home/claude/subject_metrics.json` (a **JSON list**, one object per subject with a `subject` field — a dict keyed by subject name silently defeats Gate 7's substance-check) and `/home/claude/coverage_matrix.json` (the close-out). Drafting cannot begin until both exist and Gate 7 passes. Leave a visible coverage trace in the audit log.

Execute the confirmed source plan (don't re-derive). Depth over breadth: **5–8 strong specific sources per subject beats 20 shallow ones.**

**Per-subject quantitative profile (build deep).** The biggest quality gap vs the leader reference is quantitative density (a numerical claim ~every other sentence). **Collection is direction-driven, not template-driven** — derive 4–6 brief-direction categories from DD2/DD3/DD4 *before* searching; each subject needs multiple targeted searches across them, plus one generic-context financial search. Single-query collection is laziness. Carry `source_tier` (primary/secondary/inferred), `as_of`, and `source_url` on every number; `stat_block_candidates` carry the same provenance as programme metrics.

**Every DD3 dimension is found web-first, exhaustively, and the dimension set changes every brief.** For each (subject × target) cell run the web-first ladder (search → primary source → aggregator → announcement reconstruction → user/internal only after documented exhaustion; third-party scraper optional last resort). **No dimension ships as a bare qualitative posture (Deep/Strong/Light) when a real figure was reachable.** **Comparability is the discipline (HARD):** same source/method, same reporting window, same units/currency across subjects; carry `as_of` into comparisons; flag approximations. **Triangulate headline numbers** (second independent source in `second_source`). Scraper guardrails: verify input schema first (silent-filter trap), set a bounded limit + timeout, read-and-extract immediately (accounts can lock between write and read).

**Step 5 close-out — coverage checkpoint.** Anti-fixation check (each confirmed dimension produced evidence across most subjects, not one mined deep while the rest coast). Build `coverage_matrix.json` — one entry per (subject × target) with `status` ∈ `collected` (evidence + source_urls) / `partial` / `exhausted` (both need `rungs_tried` ≥2) / `n/a` (with reason). `missing` with no `rungs_tried` is not an allowed end-state. **Run Gate 7 here** (Step 5 → 6 boundary) — a FAIL sends you back to Step 5, not forward. Then print a short plain-language **user-facing data audit** (what was found / data quality / what's genuinely unobtainable), organised by dimension across subjects. Proceed to drafting; don't block on a reply unless a gap is flagged.

## Step 6 — Draft, render, and audit the brief

Produce a **PDF intelligence brief** in your firm's house style; section ordering follows the DD9 variant (see `references/brief_style.md` §2). Use the bundled `pdf` skill to render.

**Required reading before drafting (in order):** (1) the pack's brand bundled skill(s) (`brand.bundled_skills`: SKILL.md, then its `references/pdf.md` and `references/charts.md` where present); (2) `employers/<active>/brand/house-style.md`; (3) `references/brief_style.md`; (4) `employers/<active>/brand/examples/reference_brief_example.md` (all three references). **Branding is integrated, not optional** — generate `brand.css` with the brand skill's `brand.py css` where it exists; load the pack font (`brand/palette.json` → `font.file`, e.g. `employers/<active>/brand/fonts/…`) via `@font-face` (weasyprint) and `font_manager.addfont` (matplotlib); use the pack palette (`brand/palette.json`: `text`, `accent`, `cycle`, `grid`, `fills`, `heatmap`, `headings`). A palette entry with `hex: null` is read from the brand skill, never guessed. No pack brand → the neutral fallback above. The pack's tone-of-voice brand skill (e.g. a `*-tov` entry in `brand.bundled_skills`) is mandatory reading before Stage 3 (applies to cover/framing/section-openers/[BU]-read/transitions/closers; the analytical body stays neutral).

**Brief title — substance-led, never journalistic.** Default to Economist-Special-Report register over TechCrunch. Anti-patterns (documented failures): alliteration/rhetorical pairs ("Five Primes, One Promise"), magazine hooks ("The AI Gap"), slogans, question titles, colon-twists. Good: topic-led ("Operating-Model Maturity in Enterprise AI"), method-led ("Narrative vs Evidence Across Five Aerospace Primes"), subject-led. The subtitle does the explaining. Log the title test to the audit log.

**Apply the persona-driven DDs as you write** — DD9 structure, DD10 visuals, DD7 narrowing, DD8 reader-question mapping, DD6 register/evidence, DD4 frontier, DD5 forward calls (implicit ones carry unmistakable-but-unstated implications, no "you should"), and **"[BU] read." paragraphs — required minimum 2–4**, inline (not callouts), lowercase "[Business unit] read." lead-in, situational contrast (never directive translation), distributed across the brief.

### Step 6 sequence — Stages (order matters)

- **Stage 1** — read the pack's brand bundled skills (tone of voice first) and `brand/house-style.md` before drafting prose; confirm in the audit log.
- **Stage 2** — commit DD10 visuals to `/home/claude/dd10_visuals.json` BEFORE drafting (the anti-skip mechanism). Each entry carries `claim` (the one defensible analytic point — if you can't write it, the visual is decoration), `data_provenance`, and render-state fields. Three-question check per visual: meaningful? verified (values trace to `subject_metrics.json` source_urls)? honestly encoded (same source/window/units inside the chart; no truncated baseline)?
- **Stage 3** — draft prose per DD9; maintain `quotes.json` incrementally. Lean on `subject_metrics.json` for density (a number ~every 2–3 analytical sentences). **Use numbers TO MAKE CLAIMS, not as standalone facts** — a sentence listing 3 numbers with no comparative/pattern/divergence claim is a press-release rewrite. Some sentences carry zero numbers — that's where the analytical inference lives.
- **Stage 4** — render every visual to PNG (matplotlib + the pack font + the pack palette); update `file_path`/`rendered_at`.
- **Stage 5** — HARD VERIFICATION: run the bash check that fails on any `file_path: null` or missing file; show the output explicitly. Do NOT proceed with unrendered visuals.
- **Stage 6** — embed each visual; primary structural visuals cannot degrade to tables; log any degradation to the audit log.
- **Stage 6.5** — **skeptical critic pass (CP7)**, generative not a grep: re-read twice (as a senior reviewer from your own firm, then as the buyer's skeptical analyst) and score five questions — specificity (name three things that make it unmistakably *this* seat), tension (sharpest say/show gap), numbers earning their place (each of the five most prominent figures supports a claim), title/framing (substance-led?), the "so what" (forward calls give something to act on). Write the critique, then revise. Record in the audit log; tick CP7.
- **Stage 7** — run the audit gates (see `references/gates.md`). **Gate 7 already ran at the Step 5→6 boundary.** The other six run here on the finished embedded draft in order **Gate 2 → 1 → 3 → 4 → 5 → 6**. For Gate 6 sub-A show the actual `IMG_COUNT=$(grep -o '<img ' "$DRAFT" | wc -l)` output. Append each gate's pass/fail to the audit log.
- **Stage 8** — render the final PDF (weasyprint) only after gates pass and §8 confirms every pre-render trace. Then **render-inspection (CP9)** — view *every* rasterised page for layout integrity + brand fidelity (the pack font actually embedded, palette correct, no clipped/overflowing/colliding/stranded content, "[BU] read." rendered inline not as a box). Run from `references/gates.md` §9. Fix at source, re-render, tick CP9.

### Buyer-facing Methodology page

Short, dignified, one page. **Contains:** named sources (per subject/category), time window, classification approach, a single subjects line ("Subjects selected as the direct peer set on [angle]"), acknowledged limits phrased as data-quality. **Never contains:** the gates, mode selection, DD reasoning, persona quotes, "[BU] read." counts, "audience-of-one/wrong-reader/stakeholder-placement" vocabulary, "we considered three options" trails, render-degradation notes. If it runs long, internal QA has leaked in — move it to the audit log.

### Delivery

**(0) At the finish line — default to finishing, don't stall.** A re-sent selection matching what was built is "proceed", not a change. A signal the data can't support like-for-like, already disclosed with a Methodology note, is disclosed-and-finished. The one case that interrupts: the user explicitly asks for a *change* (different subject/angle/signal, or "swap/redo X") — name the rebuild cost once, then proceed. Vague dissatisfaction routes to the `edge_cases.md` §3 clarifier, applied narrowly.

**(I) Delivery fallback chain:** `present_files` to `/mnt/user-data/outputs/` → Cowork sidebar HTML artifact → save to `/home/claude/` with the path. Don't narrate the attempts. Log path + method to the audit log.

**(II) Delivery message — one or two sentences.** Draft it to `/home/claude/delivery_message.txt` first so §8 can check it (≤ ~40 words; none of the build-narration markers). **Not** a place to coach, narrate mechanism, or explain design. Acceptable: *"PDF attached — 14 pages, three subjects with cross-read and forward calls. Want me to revise any section?"* The build narrative belongs in the audit log (handed over alongside the PDF), never the chat. Test: if a salesperson could tell an AI wrote the brief by reading the hand-off, it's over-narrated.
