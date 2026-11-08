# Engagement Learnings — distilled from the analytics (2026-07-19)

Empirical rules extracted from the vault's real LinkedIn post archive (`cbrain/notes/LinkedIn-Posts/LinkedIn-Posts-Index.md`, 19 posts, 20,482 impressions, 248 engagements as of 2026-07-19) and the career read at `cbrain/projects/career-manufacturing-cto-positioning.md`. Every rule below cites the evidence it's built on — read this before drafting or auditing a post; it is the "why" behind Scorecard C (`rubric.md`) and the pitch-opener penalty in `scripts/prepublish_audit.py`.

**Companion file (added 2026-08-18):** [`ranking-model-2026.md`](ranking-model-2026.md) describes how
LinkedIn's 2026 feed actually ranks, from LinkedIn's own engineering publications. This file is **what
this account measured**; that file is **why the platform behaves that way**. Where the two disagree, this
file wins — it is evidence about this author, not about LinkedIn in general. Two rules below (4 and 5)
were revised on 2026-08-18 once the mechanism was known.

## Rule 1 — Story beats pitch, decisively
The two worst-performing posts of the batch are both flat capability pitches with no lived moment: "Buy capability, not the machine" (2,010 impr, **0.00% engagement**, 0 comments) and the TechDays teaser "Most manufacturers own their capacity" (619 impr, **0.16%**, 1 reaction, ends on "come see me speak"). Compare the story-led posts covering the *same underlying thesis*: the TechDays keynote recap ("My S-Bahn broke down…") converted at 1.97%, and "18 months of no business case → EU says deploy" (a consortium narrative) converted at 1.98%. **Lead every post with a real, specific moment; let the take emerge from it. Never open on a generalising capability claim ("Most manufacturers…", "X-as-a-Service changes…") or an event/announcement.**

## Rule 2 — Consortium/EU narrative is the workhorse
Posts framed as a real institutional narrative (an EU review milestone, a consortium decision, a paper accepted) consistently outperform framework/opinion posts at similar reach: "18 months → EU says deploy" (1,867 impr, 1.98%) and "I-ESA 26 takeaways" (790 impr, 1.77%). This is a specific instance of Rule 1 — the institutional moment *is* the lived moment — but is worth calling out because Lasers4MaaS supplies a steady stream of these (GA reviews, workshops, deliverables, backlog milestones).

## Rule 3 — Sovereignty/defense framing over-indexes
The single highest engagement rate of all 19 posts is the Finnish Independence Day post (2.75%) — a personal moment at a diplomatic event, explicitly noting "technology and security must intertwine." Sovereignty content elsewhere (Gaia-X, sovereign edge, digital sovereignty) also scores well when story-led (the keynote's "physics, scored" framing). **This axis is under-used relative to how well it converts — lean into it, especially for the manufacturing co-primary audience, where sovereignty is a capacity/resilience argument, not a policy abstraction.**

## Rule 4 — Reach to the wrong audience is not merely wasted, it is *negative*
The widest-reach post ("Buy capability, not the machine," 2,010 impr) had the worst engagement and audience quality of the batch. The TechDays keynote's own maturation is a live demonstration: growing from 804 to 1,117 impressions **diluted** its decision-maker mix (CXO 6%→4%, VP 5%→4%) rather than adding senior buyers. **Optimize for the right audience stopping and engaging, not raw impressions.**

**Revised 2026-08-18 — this rule now has a mechanism, and it is stronger than the original wording.**
LinkedIn's published ranker trains on `skip` as an explicit label, and its retrieval model uses "posts
shown but not engaged with" as **hard negatives** (`ranking-model-2026.md` M2, Tier-1 sources). So a post
served to 2,000 uninterested people does not just fail to help — it teaches the model to separate this
author from those members. The original rule said reach is *not the target*; the correct statement is
that **imprecise reach carries a cost**. Narrow and resonant beats wide and ignored, and the
Buyer-Weighted Engagement north-star (Scorecard D) is the right shape for exactly this reason.

## Rule 5 — The audience gap: on-theme message, off-target distribution — and it is partly *lexical*
Despite ~10 of 19 posts being manufacturing/Industry-4.0-5.0/MaaS/servitization content, viewers still skew IT-services/consulting + software + Munich + Futurice's own network on nearly every post. Manufacturing/industrial-machinery viewers stay single-digit %; defense/GovTech/sovereignty audiences don't appear at all.

**Revised 2026-08-18 — the original "the writing craft alone can't fully solve this" was too
pessimistic.** LinkedIn's 2026 retrieval layer embeds members and posts into one semantic space, and the
member vector is built from their **profile, skills, work history, and the posts they've engaged with**
(`ranking-model-2026.md` M4, Tier-1). A post written in consultant dialect ("servitization enablement",
"digital transformation") is semantically nearest to consultants — which is an exact description of the
observed audience. The same problem written in plant dialect ("changeover", "unplanned downtime",
"spare-parts lead time") sits in a different neighbourhood. **The craft lever is the
[Buyer Lexicon](../../../content/linkedin-authentic-storytelling/references/icp-positioning.md#the-buyer-lexicon--the-words-that-decide-who-the-post-reaches)
and the lexicon check in the storytelling skill §2.** Outreach-side levers still matter (see
`career-manufacturing-cto-positioning.md`), and Scorecard C's P1 still judges resonance-if-reached — but
"we can't write our way to a different audience" is no longer the right conclusion.

**Status: hypothesis, not result.** The mechanism is Tier-1; that *this account's* manufacturing-viewer
share moves when the dialect changes is unmeasured. The test is the manufacturing share in
[[linkedin-weekly-review]] across the next several dialect-corrected posts. If it doesn't move, say so
here and downgrade the lever.

## Rule 6 — Several beliefs the library held were folklore; they are now listed and dated *(added 2026-08-18)*
A tiering pass against LinkedIn's own engineering publications found the library carrying Tier-3
marketing-blog numbers as if they were facts. Full table in
[`ranking-model-2026.md`](ranking-model-2026.md) §3–4. The ones that mattered:
- **"A save is ~5× a like and ~2× a comment"** — cited from three marketing blogs in `viral-metrics.md`
  to justify the Save Rate benchmark. **No Tier-1 support:** the published Feed ranker's labels are
  `click`, `skip`, `long-dwell`, `like`, `comment`, `share` — saves and sends are absent, `share` is
  present. Keep measuring Save Rate as reader behaviour; stop calling it the strongest distribution
  signal; do not promote Save-Worthiness to a gate on this basis.
- **"Comments are ~15× a like"** — both are trained labels, no published relative weight. The direction
  is plausible; the number is invented.
- **"70% of reach is decided in the first 60–90 minutes"** — uncited, and the Tier-3 sources contradict
  each other on the window.
- **"Human editorial review before wide distribution"** — folklore. Nothing in LinkedIn's engineering
  material describes a human in the ranking path.
- **"≤3 hashtags", "no links in body"** — no Tier-1 support either way, but cheap, long-standing, and
  already enforced. Keep as convention; stop implying they are physics.

**The standing rule this produces:** a number without a traceable Tier-1 or own-corpus source does not
enter a skill, a scorer weight, or a post. Directional mechanisms may be adopted; borrowed arithmetic
may not.

## Rule 7 — Audience mix and reach move independently; the north-star currently only sees one of them *(added 2026-08-19, measured, n=1)*

First single-post analytics for a deliberately dialect-corrected post
(`SinglePostAnalytics_…_7495797662907273216`, published 2026-08-19 13:03, the
"Third Condition" post). Measured, not inferred:

| | This post | 19-post archive baseline |
|---|---|---|
| Impressions | **288** | mean 1,078 (20,482/19) → **27% of mean** |
| Members reached | 126 | — |
| Engagement rate | **0.69%** (2 of 288) | mean 1.21% → **0.57x mean** |
| Manufacturing-family industry share | **32%** (motor vehicle 8, industrial machinery 6, machinery 6, appliances/electrical/electronics 6, manufacturing 6) | "single digits even on the most on-theme posts" (Rule 5) |
| Consulting/IT/software share | 26% (IT services 13, business consulting 7, software 6) | historically dominant |
| Decision-maker seniority share | 39% (director 16, CXO 6, VP 6, partner 6, owner 5) | — |
| Company size 10,001+ | 22% | — |
| Decision-Maker Density | **35.5** → BWE multiplier **capped at 2.0** | — |
| Buyer-Weighted Engagement | 1.388 | — |
| Saves / sends / reposts | **0 / 0 / 0** | — |

**Two findings, opposite in sign.**

**7a — the first evidence for H1, and it is the good kind.** For the first time in the archive the
manufacturing family (32%) **outweighs consulting/IT/software (26%)**, on a post written deliberately in
buyer dialect. Rule 5 predicted this axis was the movable one. It moved. Status stays **directional, n=1**
— the register in [[linkedin-scoring-calibration]] governs promotion, not this file — and the confounds are
real: off-cadence publish (Wednesday 13:03 vs the Tue/Thu 09:00 cadence), two named companies, and a
topic that is intrinsically closer to manufacturing than the archive average.

**7b — mix improved while reach collapsed, and Scorecard D cannot see the difference.** BWE is
`engagement_rate x buyer_fit_multiplier(density)` — a **rate times a mix**, with **no volume term**. At
density 35.5 the multiplier pins to its 2.0 ceiling, so this post scores 1.388 while having been served to
126 people. A post read by the right 126 and a post read by the right 2,000 are indistinguishable to the
north-star. Rule 4 ("imprecise reach carries a cost") is still correct and is **not** the counter-argument
here: narrow-and-resonant beats wide-and-ignored, but *invisible* is not a win either. **Scorecard D must
never be reported without impressions against the account median beside it** — see `rubric.md`, Scorecard D.

**What this does not license.** The engagement count (2) cannot support a claim about *why* readers stayed
silent. 288 impressions is a distribution outcome, not an audience verdict; with n=1 and a two-event
denominator, "senior readers read it and chose not to engage" and "almost nobody was served it" are
observationally identical here. The measurable failure is reach. Do not encode a reader-psychology story
into the library on this evidence.

**7c — Save-Worthiness scored 100 and the post earned 0 saves.** The pre-publish predictor was at its
ceiling; the measured outcome was zero. n=1 against a corpus that is nearly all zeros, so this neither
refutes the metric nor rescues it — it is logged because H2 in the register turns on save *variance*
existing at all, and this data point says it still does not.

## How these rules are enforced
- **Scorecard C (Audience Pull)** in `rubric.md` — P1 (manufacturing-buyer resonance) and P2 (story-over-pitch), blind-judged, gate ≥ 8. This is where Rules 1, 4, and 5 get tested per-post.
- **Pitch-opener penalty** in `scripts/prepublish_audit.py`'s Hook metric — a cheap mechanical pre-signal for Rule 1's most obvious failure mode (no first-person + generalising-claim opener).
- **Topic pick (§1 of the SKILL.md)** — weighted toward story availability and the sovereignty angle (Rules 1 and 3), not just topical freshness.
- **Lexicon check + Buyer Lexicon** (`linkedin-authentic-storytelling` §2 and `icp-positioning.md`) — where the revised Rule 5 gets applied per-post. Unmeasured for this account; tracked via the manufacturing share in [[linkedin-weekly-review]].
- **Rule 7's volume floor** — `rubric.md` Scorecard D now requires impressions-vs-median beside every BWE figure, and [[linkedin-weekly-review]] carries the same pairing into the weekly scorecard.
- **Evidence tiering** (`ranking-model-2026.md` §3) — where Rule 6 is enforced: a number with no Tier-1 or own-corpus source doesn't enter a skill, a weight, or a post.
