# Post-Hoc Viral & Quality Metrics — the 11-metric spec

*Added 2026-07-19. These 11 metrics score **published** posts against their real
outcomes — a different job from the three ship gates in `rubric.md`, which score
**drafts before publishing**. Nothing here changes those gates. Single source of
truth for `scripts/viral_metrics.py`; that script is the authoritative
implementation, this file is the readable spec.*

## Why these and not others

Grounded in two inputs: (1) this account's own `engagement-learnings.md` — story
beats pitch, consortium/EU narrative is the workhorse, sovereignty over-indexes
and is under-used, reach ≠ audience quality, and (2) 2026 LinkedIn algorithm
research — saves and sends are the strongest distribution signals (a save ≈ 5×
a like), comments carry far more weight than reactions, and dwell time is the
biggest single driver of reach (sources: [Linkboost](https://www.linkboost.co/blog/linkedin-viral-posts-2026/),
[DigitalApplied](https://www.digitalapplied.com/blog/linkedin-algorithm-2026-engagement-strategy-guide),
[Teract](https://www.teract.ai/resources/linkedin-algorithm-2026)).

**Evidence correction, 2026-08-18.** The paragraph above cited three marketing blogs for "a save ≈ 5×
a like" and "dwell time is the biggest single driver of reach." A tiering pass against **LinkedIn's own
engineering publications** (see [`ranking-model-2026.md`](ranking-model-2026.md)) found:
- **Dwell is genuinely Tier-1.** LinkedIn's published Feed ranker trains on `long-dwell` directly, and
  `skip` as its negative. **But `long-dwell` is a threshold label** ("dwelling on a post longer than a
  specified threshold"), not accumulated time — so "longer posts farm more dwell" is the wrong inference
  from a real mechanism. The lever is crossing the threshold.
- **The save multiplier is not Tier-1 and should not be quoted.** The published label set is `click`,
  `skip`, `long-dwell`, `like`, `comment`, `share` — **saves and sends do not appear; `share` does.** The
  5×/2×/15× multipliers circulating in the marketing layer are those authors' own arithmetic.
- **Consequence for this file:** Save Rate (#1) stays — it is a real and informative *reader-behaviour*
  measure ("worth keeping"), independent of whether it is a ranking label. What changes is the
  **justification**: its benchmark is a convention, not a derived weight, and Save-Worthiness (#9) must
  **not** be promoted to a ship gate on the strength of the multiplier claim. Only this account's own
  corpus, via [[linkedin-scoring-calibration]], can earn that promotion.

**Not computable from this data, and not faked:** dwell time and first-hour /
"golden hour" engagement velocity. LinkedIn's per-post "Single Post Analytics"
PDF export has no time-series and no dwell field — only cumulative totals.
Spacing/Readability in `prepublish_audit.py` already proxy dwell mechanically;
golden-hour has no proxy without time-series data, so it is out of scope here.

## Family A — Measured outcomes (7)

Computed from each post's `## Performance` table (frontmatter/table fields) and
`## Audience snapshot` demographics. A post missing a field is left blank in
`viral-metrics.tsv` and flagged in the summary — never silently scored 0.

| # | Metric | Formula | Why | Benchmark |
|---|---|---|---|---|
| 1 | **Save Rate** | `saves / impressions × 1000` | The purest "this was worth keeping" reference-value proxy. *(Benchmark is a convention — the "5× a like" justification was retired 2026-08-18 as unsourced; see the evidence correction above.)* | ≥ 3 per 1k impr |
| 2 | **Conversation Density** | `comments / reactions` (blank if reactions = 0) | `comment` and `like` are both trained ranking labels; no published relative weight exists, so treat this as dialogue-per-approval rather than a weighted-signal proxy | ≥ 0.15 |
| 3 | **Amplification Rate** | `(reposts + sends) / impressions × 1000` | The closest measurable proxy for a virality coefficient — reach LinkedIn's own algorithm didn't originate | ≥ 2 per 1k impr |
| 4 | **Follower Conversion** | `followers_gained / members_reached × 1000` | Did the post convert a reader into an ongoing relationship, not just a scroll-by | ≥ 1 per 1k reached |
| 5 | **Profile-Pull Rate** | `profile_viewers / members_reached × 1000` | Did the post make readers curious who wrote it — a leading indicator of authority/inbound, distinct from following | ≥ 5 per 1k reached |
| 6 | **Decision-Maker Density** | `mean(senior_share, industry_fit_share)` — see below | Operationalizes Rule 4/5: reach is not the target, the *right audience* is | ≥ 20% |
| 7 | **Buyer-Weighted Engagement** *(north-star)* | `engagement_rate × clamp(decision_maker_density / 15, 0.4, 2.0)` | Fuses viral pull with buyer quality — a 1.98% post reaching real buyers should outrank a 2.75% post reaching the wrong crowd | top quartile of corpus |

### #6 — Decision-Maker Density: method and honest limitation

LinkedIn's exported demographics are **two independent marginal top-N lists**
(Seniority, Top industries) — never a cross-tab. There is no way to recover the
true joint "senior AND in a target industry" percentage from this export; a
product-of-marginals estimate would imply near-independence assumptions that
don't hold, and would also produce numbers so small (typically low single
digits) that they stop being legible against the rest of the corpus. This
metric is therefore a documented **proxy, not a measurement**: the mean of two
marginal shares.

- `senior_share` = sum of the % for Director + VP + CXO + Partner + Owner in the
  post's `Seniority` breakdown (Manager and below excluded — Manager is
  mid-level, not a decision-maker for this ICP).
- `industry_fit_share` = sum of the % for any `Top industries` entry matching a
  target-industry keyword: `manufactur, machinery, industrial, automotive,
  motor vehicle, aerospace, defense, semiconductor, appliances, electronics,
  energy`.
- Both lists are themselves **truncated "Top" exports** (LinkedIn only surfaces
  the top handful of categories, so the visible entries rarely sum to 100%) —
  treat this metric as *directional*, not a precise population percentage.

### #7 — Buyer-Weighted Engagement: the multiplier

`multiplier = clamp(decision_maker_density / 15, 0.4, 2.0)` — pivoted at 15%
(roughly this corpus's typical density) so the multiplier is neutral (1.0) near
that pivot, penalizes down to 0.4× for an IT-services-only audience with no
industry fit, and rewards up to 2.0× for a strongly senior + industrial-fit
audience. **This never inflates a zero** — a post with 0% engagement stays at 0
regardless of how good its audience was (see the "Buy capability" post: strong
buyer density, zero engagement, buyer-weighted score still 0 — the content
failed the audience it reached, which is itself a finding).

## Family B — Leading content predictors (4)

Computed from the post **text** (pre-publish-capable), each mapped to the
Family-A outcome it should predict. Implemented in `prepublish_audit.py` as
**reported, non-gating** sub-scores (§ below) — they do not affect the
`composite ≥ 85` ship gate.

| # | Metric | Detects | Predicts | Scale |
|---|---|---|---|---|
| 8 | **Sovereignty/EU-Framing Signal** | Presence across 4 keyword categories (EN + DE terms — see note below): *sovereignty* (sovereign, souverän\*, own the data, hyperscaler independence), *EU/institutional* (EU, Horizon, consortium/Konsortium, Brussels, GA review), *resilience/capacity* (resilience, Resilienz, capacity, Kapazität, supply chain/Lieferkette), *defense/security* (defense, security, Sicherheit, Verteidigung, Militär, GovTech, NATO). Score = `25 × distinct categories hit` (cap 100) `+ 15` if any hit lands in the first ~180 characters (the hook region) | overall engagement rate and #6 | 0–100 |
| 9 | **Save-Worthiness (Reference Value)** | A reusable, extractable artifact: an enumerated/numbered list (≥3 items), a named repeatable framework (a Title-Case term appearing ≥2×, e.g. "Manufacturing-as-a-Service", "Revenue Bridge"), and hard-number density (reuses the audit's digit-anchor count) | #1 Save Rate | 0–100 |
| 10 | **Conversation-Trigger Score** | A genuine open question **anywhere in the body** at strategic altitude (not just the last-line CTA the Spacing metric already checks) + a contrarian/stakeable claim (reuses `TENSION_MARKERS`) + a named specific tension (an explicit contrast: "X, not Y" / "instead of" / a direct second-person stake "what's *your*...") | #2 Conversation Density | 0–100 |
| 11 | **Buyer-Dialect Density** *(added 2026-08-18)* | Distinct **buyer-dialect** terms present (10pt each, cap 60) + 20pt if one lands in the first ~180 chars + 20pt when buyer terms outnumber **consultant-dialect** terms (10pt if tied). Two term banks in `prepublish_audit.py`: `BUYER_DIALECT_TERMS` (OEE, changeover, unplanned downtime, PLC, OPC UA, spare-parts lead time, shop floor, retrofit…) and `CONSULTANT_DIALECT_TERMS` (digital transformation, servitization, enablement, roadmap, operating model…). EN + DE. | **#6 Decision-Maker Density** — explicitly *not* engagement rate | 0–100 |

Full formulas (weights per sub-component) are implemented — not just described
— in `prepublish_audit.py`'s `score_sovereignty()`, `score_saveworthiness()`,
`score_conversation_trigger()`, `score_buyer_dialect()`; read those functions as
the authoritative spec, this table is the summary.

### #11 — Buyer-Dialect Density: why it exists, and what the corpus already says

**Why.** LinkedIn's 2026 retrieval layer embeds members and posts into one semantic space, and a member's
vector is built from their profile, skills, work history and the posts they have engaged with (Tier-1;
`ranking-model-2026.md` M4). Vocabulary is therefore part of what decides *which audience* a post is
retrieved to — which is a candidate mechanism for this account's standing Rule 5 gap (on-theme
manufacturing content, IT-services/consulting viewers).

**Measured on this account's own corpus, 2026-08-18** (not assumed — this is the one Family B metric with
an initial empirical check behind it):

| Correlation | r | n | \|r\| significance threshold (1.96/√n) | Read |
|---|---|---|---|---|
| Buyer-Dialect × **Decision-Maker Density** (#6) | **+0.444** | 23 | 0.409 | **Clears the bar** — the mapping this metric claims |
| Buyer-Dialect × **engagement rate** | −0.241 | 50 | 0.277 | **Correctly no relationship** — this is an audience lever, not a resonance lever |

The second row matters as much as the first: the metric is *supposed* to predict who sees the post, not
whether they like it. A signal that predicted both would be measuring something vaguer.

**Honest limits — read these before treating +0.444 as settled:**
- **n = 23, and 13 of those score 0.** The relationship rests on the 9 posts that use any buyer
  vocabulary at all. That is thin.
- **Its two components each fail individually.** Senior share r = +0.293 and industry-fit share r = +0.363
  are both *below* the 0.409 threshold; only their mean (#6) clears it.
- **Topic is an uncontrolled confound.** Buyer-dialect words plausibly co-occur with manufacturing
  *topics*, and the topic may be doing the work. The two topic-matched pairs available are only
  directionally supportive, not clean.
- **The strongest counter-example is instructive, not fatal:** `20260715-buy-capability-not-the-machine`
  has the corpus's **highest** dialect score (70) and a good decision-maker density (25.5) — and **0.00%
  engagement.** Right audience, wrong content. Exactly the separation the design predicts, and a reminder
  that this metric can never substitute for Scorecard C.
- **Structurally immune to the ingest bug**, unlike Hook/Spacing: it matches words and uses a
  character-prefix hook region, so a body whose line breaks were lost on ingest still scores correctly.
  (Mean dialect is nonetheless lower on damaged rows — 7.1 vs 14.8 — which is corpus composition, older
  posts on different topics, not a scoring artifact.)

**Status: reported, non-gating.** It informs drafting and it is now a labelled hypothesis for
[[linkedin-scoring-calibration]]. It does not move `composite` and does not affect the exit code.

## Data sources

- Per-post files: `cbrain/notes/LinkedIn-Posts/YYYYMMDD-*.md` — `## Performance`
  table (Family A #1–#5) and `## Audience snapshot` bullets (Family A #6–#7).
- Post body: the `## Post` section (Family B #8–#10, reused for Family A #7's
  multiplier only indirectly via #6).
- Script: `scripts/viral_metrics.py` — reuses `build_dataset.py`'s
  `parse_post`/`num` parsing and imports `prepublish_audit` for Family B,
  exactly as `build_dataset.py` already does (no forked text-analysis logic).

## Language coverage note (Family B, same caveat as the existing AI-Fluff detector)
`score_sovereignty` matches EN + DE keywords (mirroring `score_ai_fluff`'s existing
EN+DE personal-marker precedent) — without the German terms, the single
highest-converting post in the whole corpus (Finnish Independence Day, entirely
in German: "Technologie und *Sicherheit*", "*militärischen* Führungskräften")
would score 0 on this axis by omission, not because the framing is actually
absent. `score_saveworthiness` and `score_conversation_trigger` are
language-agnostic (digits, capitalization, punctuation) and need no DE variant.

## Known data-quality flags (surface, don't hide)

- **Saves and sends are ~0 across nearly the entire corpus** (one post has a
  single save; every other post has 0 for both). Metrics #1 and #3 will read
  near-zero almost everywhere. This is a **real finding**, not a broken metric —
  this account earns reactions, not saves/shares, which is exactly the gap
  metric #9 (Save-Worthiness) is designed to diagnose and close.
- **`20260715-buy-capability-not-the-machine`** carries an explicit anomaly flag
  in its own vault note: impressions (2,010) far exceed members reached (167),
  consistent with a document/carousel served repeatedly to a small pool, or a
  counting artifact. Rate-based metrics (#1, #3) that divide by impressions are
  therefore unusually generous to this post's denominator; metrics dividing by
  members reached (#4, #5) are the more trustworthy read for it.
- Any post missing a `## Audience snapshot` section scores blank (not 0) on
  #6/#7 and is listed explicitly in the report's data-quality section.
