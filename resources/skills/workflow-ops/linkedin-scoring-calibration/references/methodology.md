# Methodology — how the calibration works and what it can honestly claim

This is the deep spec behind `SKILL.md`. Read it before touching the scripts or
quoting a number from a run.

## 1. The ground-truth label — Buyer-Weighted Engagement

**Retargeted 2026-07-19.** The scorer predicts **how a post performs relative
to this account's own history** — not an absolute number. Per post:

- **buyer_weighted_engagement** = `engagement_rate × buyer_fit_multiplier(decision_maker_density)`, computed in `build_dataset.py::buyer_metrics()` (single source of truth, shared with `linkedin-viral-scheduler/scripts/viral_metrics.py` — see that skill's `references/viral-metrics.md` #6-7 for the full formula and the demographics-parsing caveats).
- That value is turned into a **percentile rank** in `[0,1]` across the whole corpus (ties get midrank).
- The corpus is split into **terciles** on that rank → **Under / On / Over** performed.

Terciles (not fixed cutoffs) guarantee roughly balanced classes, so a 3-tier
random baseline is ~33%. This matters: **iteration-0 currently scores ~33% —
i.e. the live hand-guessed scorer predicts real engagement no better than
chance.** That is the finding the whole skill exists to fix, and the loop's job
is to climb off that floor.

**Why the label dropped raw reach (was: `0.5·pct(impressions) + 0.5·pct(engagement_rate)`).**
The original blend rewarded a post for merely spreading wide, on the theory
that LinkedIn's algorithm couples early engagement to reach. The account's own
archive falsified that as a *target*, not just a mechanism:
`engagement-learnings.md` Rule 4 found the single widest-reach post in the
corpus ("Buy capability, not the machine," 2,010 impressions) had the **worst**
audience quality and zero engagement, while narrower-reach posts converted a
denser manufacturing-buyer audience. Ranking posts by impressions was
rewarding exactly the outcome the account's own data says to avoid. The label
now ranks by engagement discounted/rewarded by *who* was actually reached
(`decision_maker_density`), not by how many people were reached.

**Discontinuity — read before comparing across this date.** Every row in
`calibration-history.tsv` **before 2026-07-19** was scored against the old
reach×engagement blend; every row **from 2026-07-19 on** is scored against
Buyer-Weighted Engagement. These are not the same measurement — a run-over-run
"agreement improved from X% to Y%" comparison that straddles this date is
comparing two different questions, not tracking progress on one. Treat the
first post-retarget run as a new iteration-0 baseline, not a regression against
the old numbers.

## 1b. Standing hypothesis register (added 2026-08-18)

The evidence pass in [`ranking-model-2026.md`](../../linkedin-viral-scheduler/references/ranking-model-2026.md)
produced three claims that are **plausible, mechanistically grounded in LinkedIn's own publications, and
not yet earned on this account's corpus.** They are recorded here rather than encoded as gates, because
this skill — not a blog and not a mechanism argument — is what promotes a signal. Each names the
measurement that would settle it.

| # | Hypothesis | Current status | What would promote it |
|---|---|---|---|
| **H1** | **Buyer-Dialect Density (Family B #11) predicts audience composition.** Writing in the buyer's own vocabulary moves *who* the post reaches, because 2026 retrieval matches a post against the member's profile-and-history text. | **Initial support, below promotion bar.** r = **+0.444** with Decision-Maker Density (n=23, threshold 0.409) and r = **−0.241** with engagement rate (n=50, threshold 0.277) — correct sign on the axis it claims, correctly null on the axis it doesn't. But 13 of 23 rows score 0, its two sub-shares each fail individually (senior +0.293, industry-fit +0.363), and topic is an uncontrolled confound. | The correlation holding at **n ≥ 40** with more nonzero rows, **and** a topic-matched comparison — same territory, different dialect — moving the manufacturing-viewer share. Then, and only then, consider it as a Scorecard-B input. **First outcome-side datapoint logged 2026-08-19** (`engagement-learnings.md` Rule 7a): on a deliberately dialect-corrected post the manufacturing family reached **32%** vs consulting/IT/software **26%** — the first time in the archive that ordering inverts. n=1, confounded by an off-cadence publish time and an intrinsically manufacturing-adjacent topic. It is the *right sign on the claimed axis*, and it is nowhere near the promotion bar. |
| **H2** | **Save-Worthiness (Family B #9) should become a ship gate.** | **Not supported, and its original justification is now retired.** The case rested on "a save ≈ 5× a like," which has **no Tier-1 source** (LinkedIn's published label set is click/skip/long-dwell/like/comment/share — saves absent). Independently, saves are ~0 across nearly the whole corpus, so there is almost no variance to fit. | Real save variance in the corpus first (i.e. the account starts earning saves at all), then a correlation against Save Rate. Until then this stays non-gating, and `viral-metrics.md`'s note that it "did not yet validate at n=19" stands. **2026-08-19:** a post scoring Save-Worthiness **100** earned **0 saves, 0 sends, 0 reposts** — one more zero row, so the variance problem is unchanged and H2 stays where it is. |
| **H3** | **Payoff-above-the-fold predicts engagement better than total length.** `long-dwell` is a *threshold* label, not an accumulator, so what matters is surviving the skip decision — not word count. | **Unmeasured.** No feature currently isolates "is there a hard anchor or tension marker in the first ~180 characters," separately from the existing Hook length band. | Implement it as a Family B reported sub-score, then test against engagement rate. Cheap to add; deliberately **not** added in the same pass that added #11, so the two don't confound each other's first validation. |

**Discipline this register enforces:** a mechanism from LinkedIn's engineering blog earns a *hypothesis
row here*, never a weight in `calibration.json`. Only this account's measured outcomes move a weight —
that is the same separation Charter §4's evidence gate demands, applied to the scorer itself.

## 2. The scorer being calibrated

`predicted_score` is computed from features already extracted by the live
scorer, re-weighted by `calibration.json`:

```
comp   = Σ wᵢ·subscoreᵢ / Σ wᵢ      over {hook, readability, spacing, aifluff}
pred   = (1 − substance_weight)·comp + substance_weight·(substance·10)
tier   = Under  if pred < cutoffs[0]
         On     if pred < cutoffs[1]
         Over   otherwise
```

**Tunable surface (7 effective knobs):** the 4 composite weights, `substance_weight`, and the 2 tier cutoffs. That is *deliberately small*. With 12 training posts, tuning the live scorer's internal bands (hook 70–140, word count 60–220, …) would be textbook overfitting — 20+ knobs against 12 points. Those bands stay frozen until the corpus is large enough to justify moving them (see §5). The high-leverage, low-overfit surface is re-weighting the gates and re-drawing the tier boundaries against real outcomes.

**Iteration 0 reproduces the live scorer:** weights = `rubric.md` Scorecard B (0.30/0.20/0.20/0.30), `substance_weight` = 0.5 (the combined-loop objective `0.5·substance + 0.5·composite`), cutoffs = the rubric's own Standard(50)/Viral(85) boundaries. So every gain the loop finds is attributable to a specific knob move.

## 3. Substance is a frozen feature, not a tuned one (verifier-separation)

Substance (M1 Topic-DNA + M3 Depth, 2–10) is **subjective** — it cannot be
recomputed deterministically inside a tight loop, and the loop must never be
able to "tune" the judgment of quality. So it is scored **once**, cached, and
treated as a fixed input feature. The loop tunes only how much weight substance
carries (`substance_weight`), never the substance values themselves.

Until the judge pass runs, `build_dataset.py` writes `substance = 6`
(`neutral-default`). A constant feature carries no signal — half of `pred`
becomes a flat 60 for every post, which is a large part of why the untuned
baseline sits at chance. **The judge pass is a prerequisite for a meaningful
calibration**, not an optional extra.

Calibration deliberately uses **one consistent rater across all posts** (a
single judge pass scoring all N), not the ship-gate's 3-blind-judges-per-post
protocol. For a relative ranking you want a *consistent* rater, not three fresh
ones per item — inter-post consistency beats per-post blindness here. This is a
documented divergence from `rubric.md`, correct for its purpose.

## 4. Train / test split and the overfit guard

- **75/25, deterministic, stratified.** Posts are sorted by `(tier, date, file)` and every 4th is assigned to test — so the 4-post test set spreads across terciles and the split is identical on every run (no RNG).
- **Overfit guard = train − test agreement gap.** `evaluate` reports it. A gap > 0.20 means the config learned the 12 training posts, not the pattern — the autoresearch loop should treat rising train + falling test as a **discard**, not a keep. Wire this as the loop's Guard.

## 5. What the numbers can and cannot claim (the honest ceiling)

**n = 16 (12 train / 4 test) is tiny. State this every time a number ships.**

- A 4-post test set has resolution **1/4** — it can only read 0/25/50/75/100%. One post flipping moves it 25 points. **There is no route to a *validated* 98% on 4 posts; the arithmetic forbids it.**
- Feature correlations below **|r| ≈ 1.96/√n ≈ 0.49** (at n=16) are indistinguishable from noise. `correlate` flags these `(noise)`. Report them as *direction*, never proof.
- Therefore **98% is a north-star, reached as the corpus grows — not a claim about today.** The deliverable is a *re-runnable engine*: re-run `build_dataset` → judge pass → autoresearch loop → `evaluate` after each new batch of posts. Track test agreement over successive runs; it should trend up as n grows. When test n crosses ~30–40 and internal-band tuning becomes statistically defensible, widen the tunable surface (§2).

Every number in the calibration report carries its `n` and, for test figures,
the `1/n` resolution caveat. This is the evidence gate
(`_shared/evidence-gate.md`) and Soul.md's "never oversell the numbers" made
mechanical: a coarse number labelled coarse is honest; the same number sold as
98% is a lie with a chart.

## 6. Output, ledger, and keep/discard (headless shape)

The run's results and reasoning mirror the `linkedin-viral-scheduler` loop so they read as siblings:

- **`results.tsv`** — the per-iteration ledger, in **autoresearch:evals-compatible schema**: line 1 `# metric_direction: higher_is_better`, then `iteration timestamp commit metric delta guard guard-metric status description`. `metric` = train agreement, `guard` = overfit-ok pass/fail, `guard-metric` = test agreement, `status` = keep/discard/converged, `description` = the reasoning (`knob X: old→new; weakest=…`). Because it's evals-schema, `autoresearch:evals` reads it directly for trend/plateau.
- **`RESPONSE.md`** — the control spine (CP0–CP4). The Stop-hook `control-spine-gate.sh` blocks an unattended exit while any `[ ]` remains, so a half-done calibration can't silently pass.
- **`calibration-report-<date>.md`** — the deterministic writeup (`calibrate.py report`): run summary, cited baselines, before→after knob diff, iteration narrative, train vs test (each with n + caveat, never merged), correlations, honest ceiling. Pure Python — always renders even if the LLM stalls.
- **`calibration-history.tsv`** — one row per run (`date iterations train_agreement test_agreement overfit_gap scorer_updated`), so progress toward the 98% north-star is visible run-over-run.

**Keep/discard is a file-snapshot, never git.** The loop edits `STATE_ROOT/calibration.working.json`, promotes to `STATE_ROOT/best.json` on a keep, restores from it on a discard. An unattended job must never `git commit`/`git revert` the repo (it would fight the user's working tree and branch). Only the final `best.json` is copied to `scripts/calibration.json`, and only when the finalize gate passes (clean overfit gap AND test improved).

## 7. What "know what to improve" means here

`correlate` answers it directly: it ranks every pre-publish feature by its
correlation with the outcome label (Buyer-Weighted Engagement since
2026-07-19; see §1), and adds an engagement-shape lens (do comments / reactions
/ reposts / saves precede reach?) — that second lens is unaffected by the
retarget since it always compared against raw impressions, not the label. On
the current corpus the honest signal is that **comments and reactions precede
reach** (early engagement drives distribution) while the current `composite`
score barely moves with the buyer-weighted outcome (noise at this n) — so the
lever to pull is *provoking early comment-worthy engagement from the right
audience*, and the scorer's weights should shift toward whatever features
actually correlate. Every coefficient carries the noise flag; treat the ranking
as a hypothesis generator that firms up as the corpus grows.
