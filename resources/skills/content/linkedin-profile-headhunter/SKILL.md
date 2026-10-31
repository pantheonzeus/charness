---
id: linkedin-profile-headhunter
aliases: [linkedin-profile-headhunter]
name: "LinkedIn Profile Optimizer → Headhunter Discoverability"
category: content
description: Interview the user in depth, then rebuild their LinkedIn profile to be FOUND by headhunters for a specific target role (default target — CTO / VP / Director driving digitalization & servitization at a manufacturing company). Engineers the recruiter keyword funnel (Headline → Skills → About → Certs), the 220-char headline formula, an AIDA/PAS About, metric-driven experience, and Open-to-Work-for-recruiters settings — grounded in an ex-recruiter playbook, with Lasers4MaaS (servitization) and the Bosch PT ecosystem as flagship proof points.
triggers: [linkedin profile, optimize my linkedin, get found by headhunters, recruiter search, open to work, profile rebuild, linkedin headline, about section, get a new job, job search profile, servitization, digitalization CTO, VP director role, linkedin SEO, profile optimization]
tags: [content, linkedin, profile, job-search, recruiter, seo, headhunter, servitization, digitalization, personal-brand]
related: ["[[linkedin-authentic-storytelling]]", "[[notebooklm]]", "[[audience-of-one-report]]", "[[linkedin-viral-scheduler]]"]
modules: [file-backed-handoff]
references: [references/playbook.md, "../linkedin-authentic-storytelling/references/icp-positioning.md", "../../workflow-ops/linkedin-viral-scheduler/references/ranking-model-2026.md"]
requires:
  optional: [nlm]
environment: "Fully self-contained via references/playbook.md. Optional live notebook refresh needs the `nlm` CLI authenticated (first run is an interactive `nlm login`); degrades gracefully to the embedded playbook."
status: active
version: 5
created: 2026-07-11
updated: 2026-10-01
vault_writes: ["cbrain/notes/[0-9]*", "cbrain/projects/*", "cbrain/Clients/*"]
---

# LinkedIn Profile Optimizer → Headhunter Discoverability

*Rebuild the **profile** — not a post — so the right headhunter **finds you** for the role you want. Recruiter search is keyword matching: this skill runs a deep, batched interview, engineers the keyword funnel (Headline → Skills → About → Certs), and outputs a paste-ready profile grounded in an ex-recruiter playbook. Default target: **CTO / VP / Director of digitalization & servitization at a manufacturing company**, with **Lasers4MaaS** (servitization) and the **Bosch PT professional-series ecosystem** (platform/ecosystem) as flagship proof points.*

**Triggers/Context**
- Deploy when: rebuilding or optimizing the LinkedIn *profile* for a job search, maximizing recruiter/headhunter discoverability, fixing the headline/About/skills, or configuring Open-to-Work.
- The lens stays Soul.md — Business → Product → Technology — but the *reader* here is a **headhunter running a keyword search**, not a peer audience. Every choice serves being found and then respected.
- **Not** for: writing LinkedIn *posts* / thought-leadership → use [[linkedin-authentic-storytelling]]. Not for an outreach brief on a *named* person → use [[audience-of-one-report]].
- **Read [`references/playbook.md`](references/playbook.md) first** — the recruiter-search mechanics, the headline formula, the AIDA/PAS About templates, the metric taxonomy, the settings, and the seed keyword bank. It is the canonical grounding.

**Core Blueprint**
Run in order. §1–§3 are the interview (batched AskUserQuestion rounds — never a single wall of questions); §4 builds; §5 delivers; §6 wires the vault. Confirm the target BEFORE building — a profile aimed at the wrong title is worse than no change.

### 0. Load baseline (do this first, silently)
- **Read the playbook** (`references/playbook.md`). *Optional refresh:* if the user wants the latest from source, delegate `nlm notebook query b29229f5-0c1c-4cab-b2d5-ac25eb6f2a3b "…" --json` to a cheap sub-agent (keeps large JSON out of context) via a file-backed handoff (Charter §5: [`_shared/delegation-handoff.md`](../../_shared/delegation-handoff.md)): packet at `output/.runs/<YYYYMMDD>-headhunter/children/playbook-refresh/TASK.md` (the query, the output path), context mode **fresh**; the child writes the answer to `RESPONSE.md` beside it, and the parent reopens that file before merging it into the playbook baseline. If `nlm` is unauthenticated (redirects to Google), skip it and use the embedded playbook — do not block on `nlm login`.
- **Harvest the vault** (`cbrain/cbrain/` → `Clients/`, `projects/`, `notes/`, `daily reports/`) for the user's real career context — existing roles, **Lasers4MaaS**, **Bosch PT**, metrics, scale, org-building history. Pre-fill what you already know so the interview asks for what's *missing*, not what's on record.

### 1. Target lock (interview round 1) — the single most important step
Ask, in one batched round:
- **The ONE cohesive target title story** — CTO / VP Technology / CDO / Director Digital Transformation (manufacturing). Enforce one coherent story; incompatible titles in one profile signal "doesn't know what they want" and dilute every keyword.
- **Target sectors & sub-domains** (discrete/process manufacturing, machine-building, industrial equipment…).
- **Geography** where headhunters should surface you (DACH / Europe / remote) — this seeds the Open-to-Work location filter.
- **3–5 example target companies + real job postings** — you will mine these for the exact keywords in §2.
- Reflect back the locked target in one line and get a yes before proceeding.

### 2. Keyword & SEO engineering
- Build the keyword set from the recruiter funnel (playbook §1): **exact target titles** + **industry/domain terms** (Industry 4.0, IIoT, servitization, X-as-a-Service, digital twin, MES/PLM, edge-to-cloud, platform/ecosystem, Gaia-X, agentic AI) + **hard skills/systems**. Start from the seed bank (playbook §8); refine against the real postings from §1.
- If the user can access them, run the **"Skills match" panel** on a target posting to harvest the exact algorithm-weighted skills; add only what they can legitimately claim.
- Map each keyword to its placement (**Headline → Skills → About → Certs**), highest-weight terms first. Every keyword must be a term the user can **defend in an interview** — no stuffing.
- **Second reader: the feed's retrieval model (added 2026-08-18).** This skill has always optimised for one reader — a headhunter running a keyword search. There is a second one. LinkedIn's 2026 feed embeds **members** and **posts** into a shared semantic space, and a member's vector is built from their **profile, skills and work history** plus the posts they engaged with; profile text carries measurably more weight for members with little engagement history (**+2% AUC below 10 historical actions** — Tier-1, [`ranking-model-2026.md`](../../workflow-ops/linkedin-viral-scheduler/references/ranking-model-2026.md) M7). So the profile is *also* an input to who the user's own posts get shown to.
  - **The practical rule: profile and posts must share one lexicon.** Cross-check the keyword set against the **Buyer Lexicon** in [`icp-positioning.md`](../linkedin-authentic-storytelling/references/icp-positioning.md). If the profile is written entirely in recruiter/consultant vocabulary while the posts aim at plant-floor buyers, the two objectives are pulling apart and nobody was checking.
  - **The two objectives mostly agree, and where they conflict, recruiter wins here.** A headhunter's boolean search needs the recognised title and domain terms ("CTO", "Industry 4.0", "servitization"); those stay non-negotiable in the Headline and Skills. The buyer dialect belongs in the **About** and **Experience** prose, where there is room for the real vocabulary of the work ("changeover", "unplanned downtime", "OPC UA", "spare-parts lead time") — which is also where it reads as someone who has actually stood on a shop floor. Put both in, in the right places, rather than trading one for the other.
  - **Honesty flag:** the recruiter-funnel half of this is grounded in the ex-recruiter playbook; the feed-retrieval half is a Tier-1 *mechanism* with no measurement for this account. Do not rewrite a working profile chasing it — treat it as a tiebreak when choosing between two defensible phrasings.

### 2b. Third reader: the panel that already has a doubt (added 2026-08-22)
The profile's first job is not keyword coverage — it is **defusing a category prior above the fold**. Evidence, not theory: the Company A panel had written *"kein Guru"* and *"Umsetzungsverantwortung"* into its briefing and one member's recorded test was *"Umsetzer oder Berater?"* — **before the hearing** (`output/20260822-company-a-postmortem.md`). They had read the profile and formed a view from it. Operating depth was then probed and handled; the loss was a category test.

- **⚠️ The category prior is PANEL-SPECIFIC. Never inherit it from the last loss (added 2026-08-24).** This is the correction that matters most in this section, and it was learned by getting it wrong. A profile was rebuilt on 2026-08-24 to defuse the Company A advisor prior — hours before a live process surfaced whose panel **inverts** it: Company B's two Managing Partners are both ex-McKinsey (turnaround, DD, PMI), so analytical depth is their *native register*, not a red flag. Their stated test was a different axis entirely — *"keinen Verwalter, sondern einen 'Pragmatic Architect' für eine unfertige, unperfekte Realität"*: **architect vs. administrator.** The rebuild had generalised a single loss into a law and mis-aimed the whole profile (`output/linkedin-profile-20260824.md`, superseded by `-v4`).
  - **The rule:** derive the prior from **the target panel's own words** — the search brief, the briefing language, the panel's biographies. If no live target exists, optimise for the *class* of target and say that is what you did. Never carry a prior forward as settled.
  - **The corollary:** a profile aimed at a class of buyer is a *default*, not a commitment. When a named process goes live, re-derive.
- **One title story — and when a live process exists, the live target title wins.** The 2026-08 campaign default is **"Digital & Service Business" leadership** — owning the digital/service P&L of an industrial business; recruiter-legible for Director/VP/CDO searches and workable as a create-the-role pitch. But **a named live mandate overrides the campaign default**: with a Group CTO / Chief Digital & AI Officer search live, slot 1 carries *that* title, not a Director-class story one rung below the seat. **Dialects live in content; the headline carries one story — the story of the seat actually in play.**
- **Slot 1 vs slot 2, the standing resolution (added 2026-08-24).** §2 says the recruiter-recognised title is non-negotiable in the Headline; this section installs a business-title story. These collide, and the answer is **not** a trade-off: 220 characters carries both. Put the story of the seat in play in slot 1 and the recognised search token in slot 2 — measured twice at 203/220 and 212/220 with room left. Do not spend a run rediscovering this.
- **Subordinate the services-firm signal.** A services-firm title is the biographical fact a manufacturing panel reads as "advisor." Headline and About lead with **industrial outcomes and owned programmes**; the employer appears in Experience, not as identity. This is emphasis, not fiction — Lasers4MaaS was a real operating role and is described as one. **Never restate a title inaccurately**; the Gotchas' "keep actual titles exact" rule wins over any framing gain.
- **Ladder vocabulary, joint-level.** Draw the domain terms from [`ladder-joints.md`](../linkedin-authentic-storytelling/references/ladder-joints.md) — the stall language, not the stage names. *"who owns the spindle hours", "the data sat in a cabinet since commissioning", "pay-per-part"* belongs in About and Experience; **the ladder is never named as a model anywhere on the profile**, for the same reason it is never named in a post.
- **Three-dialect placement rule** (extends §2's existing split): recruiter terms and target titles in **Headline + Skills** · D1 German plant vocabulary and D2 capital vocabulary in **About + Experience prose** · D3 standards/sovereignty terms wherever the consortium work is described.

### 3. Batched interview — evidence & current state
Run as focused rounds (not one dump). Use the playbook's **metric-type menu** (absolute · ratio · time-to-result · ranking · growth · savings) as the prompt scaffold so answers come back quantified:
- **Quantified achievements** across the career — org scaled 0→N FTE, budgets, recurring-revenue shifts, time-to-market, ROI.
- **Lasers4MaaS deep-dive** (the servitization flagship) — the as-a-Service model built on physical assets: business outcome, scale, revenue model, ROI, your specific role.
- **Bosch PT professional-series ecosystem deep-dive** (the platform/ecosystem flagship) — what the ecosystem was, the platform play, adoption/partner/connected-device metrics, your specific role.
- **Current state** — paste of the existing headline, About, custom URL, and Open-to-Work status, so the rebuild is a clean diff and nothing real is lost.

### 4. Build the sections
Produce each, ready to paste, using the playbook templates:
- **Headline (≤220 chars)** — `Target Title | Years in sector | 3 high-priority keywords | "helped…" + metric`. No "Title at Company", no buzzwords.
- **About (≤2,000 chars)** — **AIDA** by default (Attention metric-hook → Interest roles/systems, keyword-dense → Desire differentiators+metrics → Action CTA + contact); offer **PAS** as an alternative framing. Framed around the employer's problem, not "me".
- **Experience** — each role led with **company context** (size/industry/function), then metric bullets; make **Lasers4MaaS** and **Bosch PT** the standout entries. Diversify metric types.
- **Skills** — up to 50, ordered by target relevance; **pin the top 5** hard skills (the highest-priority keywords).
- **Settings** — **Open to Work → recruiters-only** with target titles/locations/role types; clean **custom URL**; **Featured** proof pins; photo/banner guidance.

### 5. Output — paste-ready + safe rollout
Write `output/linkedin-profile-YYYYMMDD.md` containing:
- Each section, labeled, with **character counts** vs. the limits.
- A **"where each keyword lands"** map (keyword → section) so discoverability is auditable.
- A **step-by-step change checklist** in rollout order.
- **⚠️ Privacy warning FIRST in the checklist:** turn **OFF** "Share profile updates" *before* editing (or the whole network — including the current employer — gets notified), and use the **recruiters-only** Open-to-Work, never the public green banner.

### 6. Vault integration
- Log the rebuild as a vault note (tag `#job-search`, `#linkedin`), cross-linked to the **Lasers4MaaS** and **Bosch PT** topic/project notes and any relevant people (Living Knowledge Graph — bi-directional links, one-line reason each).
- If a recurring "target companies / headhunter" theme emerges, maintain a topic anchor note as the hub.

**Optimizations/Gotchas**
- **One cohesive title story, always.** Mixing incompatible target titles is the fastest way to fall off every shortlist — the search story must be singular.
- **Keyword you can't defend = liability.** The algorithm rewards the term; the interview punishes the bluff. Only place what's real.
- **Privacy broadcast is the classic own-goal** — editing a live profile with broadcast ON tells your current employer you're leaving. Kill it before touching anything.
- **Recruiters-only, never the green banner** at senior level — the public banner reads as "why hasn't anyone snapped them up?"
- **Discretion is a communication plan, not a toggle (added 2026-08-22).** Open-to-Work controls a banner; it does not control inference. A full profile rebuild plus a visible jump in posting cadence is legible to current colleagues regardless of the setting. Decide the answer to "are you looking?" *before* editing — thought leadership at this altitude is a defensible part of a CTO role, and that is the honest answer, not a cover story. Broadcast still goes off first.
- **Proof every AI-written line** — AI hallucinates/alters real titles and context; keep the user's actual titles exact, and cut anything that reads as generated.
- **Achievements over duties, every bullet a metric** — a duty list is invisible; a quantified outcome (especially time-to-result) is the "hit the ground running" signal recruiters buy.
- **The headline does the heaviest SEO lifting** — it is the #1 place the algorithm looks. If a keyword only fits one place, it goes here.
- **This is the profile, not a post** — if the user actually wants to publish content, hand off to [[linkedin-authentic-storytelling]].
