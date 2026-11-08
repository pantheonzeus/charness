# Three-Gate Scoring — Substance + Audience Pull + Pre-Publish Audit

A post ships only when it clears **all three pre-publish gates**. They measure different things and are never merged into one number:

- **Scorecard A — Substance (blind-judged, subjective).** "Is this worth saying, and does it fit the persona?" Two metrics: M1 Topic-DNA, M3 Depth.
- **Scorecard C — Audience Pull (blind-judged, subjective).** "Will the *right* buyer stop, and is this a story or a pitch?" Two metrics: P1 Manufacturing-Buyer Resonance, P2 Story-over-Pitch. **Added 2026-07-19** — the earlier two-gate scorer measured "worth saying" and "will the algorithm carry it," but neither gate caught the failure mode the analytics exposed: a post can pass both and still be a flat capability pitch that a manufacturing buyer scrolls past (see `engagement-learnings.md`, evidence from `[[LinkedIn-Posts-Index]]`).
- **Scorecard B — Pre-Publish Audit (deterministic, scripted).** "Will the algorithm carry it?" Four metrics: Hook, Readability, Spacing, AI-Fluff.

A fourth scorecard exists but is **not a ship gate** — see below.

**Mechanism grounding (added 2026-08-18).** Until now these scorecards encoded heuristics with no model of
the ranking system underneath, so there was no way to tell a real mechanism from folklore.
[`ranking-model-2026.md`](ranking-model-2026.md) is now that model, built only on LinkedIn's own
engineering publications. Read it before changing any weight here. Two clarifications it forces:
- **"Spacing & Dwell Time" is named slightly wrong.** LinkedIn's published `long-dwell` label fires on
  crossing an *unpublished threshold*, not on accumulated seconds. So the Spacing metric is a proxy for
  **surviving the skip decision**, not for maximising time on post — and the Readability metric's
  60–220-word band was never in tension with dwell. Names kept for continuity; read them this way.
- **No gate weight may be set from a marketing-blog number.** §3 of that file lists the ones the library
  had been carrying (a save ≈ 5× a like, comments ≈ 15×, 70% of reach in the first hour) — all untraceable
  to LinkedIn.

The original M2 (Dwell Time) and M4 (Algo Hygiene) are **retired** — Scorecard B's Hook/Spacing metrics are the richer version of the same thing, so keeping both would double-count the same signal.

## Scorecard A — Substance (blind-judge protocol)

| Metric | Target | 5 | 3 | 1 |
|---|---|---|---|---|
| **M1: Topic DNA Match** | Semantic alignment with profile persona. | 100% niche authority | Broadly industrial but generic | Chasing mainstream/off-topic trends |
| **M3: Depth Score** | Utility yielding saves/shares. | Proprietary framework, raw data, or unique contrarian paradigm | Useful advice but forgettable/static | Basic corporate announcements ("Thrilled to share") |

`substance = M1 + M3` (max 10). **Gate: `substance ≥ 9`.**

**Protocol** (unchanged from the original design): spawn 3 independent judge agents via the Agent tool, `subagent_type: general-purpose`, **fresh context** each (per `_shared/delegation-handoff.md` — a judge that has seen the hypothesis or a prior score isn't blind). Each judge's task packet (`STATE_ROOT/children/judge-<n>/TASK.md`) contains the current `post.md`, this M1/M3 table verbatim, and an instruction to write **only** `{"M1": int, "M3": int, "rationale": {"M1": "...", "M3": "..."}}` to `STATE_ROOT/children/judge-<n>/RESPONSE.md`. Reopen all 3 `RESPONSE.md` files from disk (never trust the inline reply) and take the **median** per metric.

**Judge cost discipline:** re-run the substance judges only when a mutation changed the post's *meaning or claims*. A mutation that only reformats (line breaks, hashtag count, emoji) carries the prior substance score forward — Scorecard A doesn't move when the words didn't change what they say.

## Scorecard C — Audience Pull (blind-judge protocol)

| Metric | Target | 5 | 3 | 1 |
|---|---|---|---|---|
| **P1: Manufacturing-Buyer Resonance** | Would a manufacturing/industrial digital-leadership decision-maker — Head of Digital / Industry 4.0 / Smart Factory lead, VP Ops/Manufacturing, plant/OT leader, industrial-PE operating partner, manufacturing CTO/CDO — stop, recognise *their* problem, and respect it? | Unmistakably their problem, at their altitude (capacity, capital, sovereignty, resilience) | Recognisable but generic-consulting-flavoured | Reads as written for IT/software peers, not a factory-floor or industrial-PE buyer |
| **P2: Story-over-Pitch** | Does it open on a real, specific lived moment/tension and let the take emerge, or does it announce a capability / "come see me speak"? | A concrete moment carries the take; no announcement framing | Some narrative but the pitch shows through | Pure capability announcement or event promotion |

`pull = P1 + P2` (max 10). **Gate: `pull ≥ 8`.**

**Protocol:** judged by the **same 3 blind judges** as Scorecard A, in the same delegation round — their task packet gains this P1/P2 table alongside M1/M3, and their `RESPONSE.md` gains `{"P1": int, "P2": int, "rationale": {"P1": "...", "P2": "..."}}`. Take the median per metric, same as Substance. **Judge cost discipline:** identical carry-forward rule — re-judge only when a mutation changed the post's meaning or framing (a moment swapped for a different moment, a pitch reframed as a story); a pure reformatting mutation carries P1/P2 forward unchanged.

**Why judged, not scripted:** manufacturing-buyer resonance and story-vs-pitch are semantic judgments a regex can't reliably make — a mechanical pre-filter for pitch-shaped openers exists in `scripts/prepublish_audit.py` (see below) as a cheap, deliberately modest pre-signal, but it is *not* the enforcement; P1/P2 are.

## Scorecard B — Pre-Publish Audit (deterministic script)

Run `scripts/prepublish_audit.py <post.md>` — no judge calls, instant, free, reproducible. Prints one JSON line + a human summary; exits 0 iff `composite ≥ 85`.

| Metric | Weight | What it measures | Viral (≥85 equiv.) | Standard (50–84) | Suppressed (≤49) |
|---|---|---|---|---|---|
| **Hook Efficiency** | 30% | Length of the opening hook **block** (first line, or first two lines combined if the hook is split by a single line break — a paragraph break/blank line ends the block), 70–140 chars optimal; fluff-opener detection; **pitch-opener detection** (a capability-announcement hook with no first-person marker — added 2026-07-19, see below); curiosity-gap proxy. | Counter-intuitive/tension hook in the 70–140 char band | Soft opener, hook buried | Wall of text, gives away the conclusion, or opens as a capability pitch |
| **Mobile Readability** | 20% | Word count (60–220 optimal), avg sentence length (<15 words optimal), sentence-length variation. | Short, scannable, varied rhythm | Sentences >25 words, 3+ sentence paragraphs | Academic-paper-length blocks |
| **Spacing & Dwell Time** | 20% | One-idea-per-line ratio, blank-line density, emoji count (≤5), non-bait close, 0 links / ≤3 hashtags. | Strict one-idea-per-line, substantive close (question **or** statement), no links | Generous formatting but a thin one-line sign-off | No line breaks, >3 hashtags, a link in body, or an engagement-bait close |
| **AI-Fluff Detection** | 30% | Transition-phrase density, personal-marker presence, hard-anchor count (digits/named specifics), sentence-uniformity. | Personal markers + hard anchors, zero transition phrases | Clean but generic 3-bullet-takeaway structure | Corporate abstractions, uniform paragraphing |

`composite = 0.30·hook + 0.20·readability + 0.20·spacing + 0.30·aifluff`. **Gate: `composite ≥ 85`** ("Viral Potential" band; 50–84 = "Standard Reach"; 0–49 = "Fluffed / Suppressed").

The exact scoring formulas (length bands, word-count bands, weight breakdowns per sub-metric, and the documented heuristics standing in for "curiosity-gap quality" and "CTA genuineness") are implemented — not just described — in `scripts/prepublish_audit.py`; read the script's docstring and function comments as the authoritative spec, this table is the summary.

## Combined loop objective

Per iteration, once all three scorecards are available: `combined = (substance/10·100 + pull/10·100 + composite) / 3`. **Keep** the mutation if `combined` improved over `best`; else **discard** (restore from `best.md`). **Stop** when **all three** gates pass (`substance ≥ 9` AND `pull ≥ 8` AND `composite ≥ 85`) or the 12-iteration budget is spent — whichever comes first.

## M4's mechanical floor is now inside the audit
The former standalone `hygiene_check.sh` guard (0 links, ≤3 hashtags) is still run as a **cheap pre-filter** before anything else — a hygiene violation auto-rejects the mutation without even running the audit script or spending a judge call. `prepublish_audit.py` independently re-detects the same violations inside its Spacing metric (same regexes, verified to agree) — the two are consistent, not contradictory; the shell guard is just the fast first check.

## Close scoring — questions are not privileged (changed 2026-08-18)

The Spacing metric used to award a **full** CTA score only to a post ending in a question (>4 words,
avoiding the three literal strings `agree?` / `thoughts?` / `right?`), and capped every declarative
close at 70. That structurally pushed every draft toward "What do you think?" — and let
*"What's your take?"* and *"Let's continue the conversation in the comments"* score a perfect CTA.

Three independent lines of evidence say that was backwards:
- **LinkedIn's own 2026 feed release** names "engagement bait" and "comment to agree" prompts among the
  content it downranks.
- **Both notebook sources** independently call generic closes momentum-killers ("kills whatever momentum
  the post had built").
- **This account's own corpus**: `has_question` correlates with the blended outcome at r=+0.157 on the
  intact rows — indistinguishable from noise.

Current behaviour in `scripts/prepublish_audit.py`:

| Close | CTA score |
|---|---|
| Matches the expanded `CTA_BAIT` list | **35** (real penalty) |
| Substantive close, >4 words — question **or** statement | **90** (neither shape is privileged) |
| Thin one-line sign-off / fragment | 65 |

Regression-tested across all 51 scorable archive posts: 38 rows changed CTA, exactly one bait true
positive (`20260427-iesa-takeaways`, ending "Let me know your thoughts below! 👇"), no false positives.
Composite moved by at most ±1.8 (mean +0.44) and the count of posts clearing the >=85 gate was unchanged
at 6/51 — **this fix corrects the guidance the scorer gives, it does not meaningfully move the gate.**
CTA is 25% of Spacing, which is 20% of composite: a 5% lever. Do not oversell it.

## Banned / AI-fluff phrases (single canonical list — used by both the mutator and the audit script)
`AI_FLUFF_PHRASES` in `scripts/prepublish_audit.py`: moreover, furthermore, in conclusion, delve, testament, thrilled to share, excited to announce, game-changer, unlock the power of, ever-evolving, leverage, synergy, seamless, cutting-edge, paradigm shift, landscape, in today's fast-paced. The mutator (SKILL.md §3) must never introduce any of these — the audit script enforces the same list mechanically, so a mutation that violates it is caught even if the mutator slips.

## Non-gating reported signals (Family B) — now four
`prepublish_audit.py` also prints four content predictors that **never enter `composite` and never affect
the exit code**: Sovereignty/EU-Framing (#8), Save-Worthiness (#9), Conversation-Trigger (#10), and
**Buyer-Dialect Density (#11, added 2026-08-18)**. Full spec:
[`viral-metrics.md`](viral-metrics.md).

#11 is the one with an empirical check behind it. It counts buyer-dialect terms (OEE, changeover,
unplanned downtime, PLC, spare-parts lead time…) against consultant-dialect terms (digital
transformation, servitization, enablement, roadmap…), because LinkedIn's 2026 retrieval layer places a
post by semantic proximity to the target member's own profile-and-history text
(`ranking-model-2026.md` M4). Measured on this account's corpus: **r = +0.444 with Decision-Maker Density
(n=23, threshold 0.409)** and **r = −0.241 with engagement rate (n=50, threshold 0.277)** — i.e. it
predicts *who sees the post*, not *whether they engage*, which is exactly the mapping it claims.

**It is deliberately not a gate.** n=23 with 14 zeros, topic is an uncontrolled confound, and the
corpus's highest-dialect post (`20260715-buy-capability`, 70) had 0.00% engagement — right audience, wrong
content. Buyer resonance stays enforced by Scorecard C's P1 judge; the lexical count is a cheap
pre-signal, the same relationship the pitch-opener regex has to P2. Promotion to a gate is
[[linkedin-scoring-calibration]]'s decision on a larger corpus, not this file's.

## Scorecard D — Post-Publish Retrospective (measured, not judged; added 2026-07-19)

**Not a ship gate — cannot be one.** Its inputs (impressions, viewer
demographics, saves, sends) don't exist until LinkedIn has actually served the
post to a real audience, so there is nothing for a draft to be scored against.
This is the standing retrospective measurement every **published** post
receives, once its analytics come in.

| Metric | Formula | Why |
|---|---|---|
| **Buyer-Weighted Engagement** (north-star) | `engagement_rate × buyer_fit_multiplier(decision_maker_density)` | Directly operationalizes Rule 4 (`engagement-learnings.md`) — "reach and audience quality are decoupled; reach is not the target." Discounts a high raw engagement rate earned from the wrong audience, rewards a lower rate earned from real manufacturing/industrial decision-makers. |



### Volume floor — BWE is never reported alone *(added 2026-08-19, from `engagement-learnings.md` Rule 7b)*

BWE is a **rate times a mix**. It contains **no volume term**, and its multiplier is clamped at 2.0, so a
post served to 126 people with an excellent audience mix scores the same as one served to 2,000 with the
same mix. Measured instance: the 2026-08-19 post scored BWE **1.388** on 288 impressions — 27% of the
account's mean reach — with Decision-Maker Density 35.5 pinning the multiplier to its ceiling.

Therefore, whenever Scorecard D is reported — in `viral_metrics.py` output, in the weekly review, or in
any run's final report — **BWE must be accompanied by impressions as a percentage of the account's rolling
median**, and a post below **50% of median reach** is labelled a **distribution failure** regardless of its
BWE. This does not reverse Rule 4: wide-and-ignored is still worse than narrow-and-resonant. It states the
missing half — *invisible* is not a win, and a north-star that cannot tell 126 from 2,000 will happily
optimise the account into silence.

**This is a reporting rule, not a new gate.** Scorecard D remains retrospective and non-gating; the floor
changes what must be shown next to the number, never a ship decision.

Full formula, the other 6 measured metrics, and the 3 content-predictor
metrics are specified in
[`references/viral-metrics.md`](viral-metrics.md) and computed by
`scripts/viral_metrics.py`. **This is what `linkedin-scoring-calibration` now
calibrates Scorecard B against** — retargeted 2026-07-19 from a raw
reach×engagement blend to Buyer-Weighted Engagement (see that skill's
`references/methodology.md` §1 for the discontinuity this causes in its
run history). Scorecard D is where the loop's pre-publish predictions get
checked against reality — it closes the loop A/B/C open, it doesn't replace
them.

## Pitch-opener penalty (mechanical pre-signal, added 2026-07-19)
`PITCH_OPENER_SUBJECTS_RE` / `PITCH_ANNOUNCEMENT_RE` / `PERSONAL_MARKER_RE` in `scripts/prepublish_audit.py` dock the Hook score when the hook block reads as a **capability announcement rather than a lived moment**: no first-person marker (`I/my/we/our/ich/wir/…`) present, combined with a generalising-claim shape (`most/every/nobody/manufacturers/factories/companies …`, or an "X-as-a-Service changes/flips/means…" pattern). This is the evidence-backed failure mode from both 2026-07 flops (`20260715-buy-capability-not-the-machine`, `20260713-manufacturing-as-a-service`) — both opened this way and both cleared the old Hook metric while landing 0.00%/0.16% engagement. **This penalty is deliberately modest** — regex pitch-detection is fragile and will miss or misfire; the real enforcement is Scorecard C's P2 judge above. Verify it does not fire on posts that open with a genuine first-person moment (e.g. the TechDays keynote's "My S-Bahn broke down…").
