---
id: linkedin-weekly-review
aliases: [linkedin-weekly-review]
name: "LinkedIn Weekly Performance Review → Strategy"
category: workflow-ops
description: Ingest a weekly LinkedIn analytics export (.xlsx, account-level + individual posts), refresh the per-post metrics corpus, track three visibility axes over time — Buyer, Recruiter, Reach — and turn the trend into 2-3 concrete next-post recommendations.
triggers: [upload linkedin stats, weekly linkedin review, linkedin performance, how did my posts do, weekly stats, post analytics, review my linkedin week, linkedin dashboard, buyer visibility, recruiter visibility, what should i post next, linkedin xlsx export, linkedin analytics export]
tags: [workflow-ops, linkedin, analytics, weekly-review, strategy, script-backed]
related: ["[[linkedin-viral-scheduler]]", "[[linkedin-scoring-calibration]]", "[[linkedin-profile-headhunter]]", "[[linkedin-authentic-storytelling]]", "[[career-campaign-review]]", "[[linkedin-video-script]]"]
modules: [file-backed-state, evidence-backed-answering]
requires:
  cli: [python3]
  optional: [openpyxl]
references: [references/axes-and-intake.md, "../linkedin-viral-scheduler/references/ranking-model-2026.md"]
scripts: [scripts/ingest_xlsx.py, scripts/account_metrics.py]
environment: "Local terminal or Claude Code with vault access (cbrain/). openpyxl parses the .xlsx export; degrades to stdlib csv if you export .csv instead (demographics parsing is then unavailable — only totals)."
status: active
version: 3
created: 2026-07-24
updated: 2026-08-22
vault_writes: ["cbrain/notes/LinkedIn-Posts/*", "cbrain/projects/ladder-campaign.md", "cbrain/projects/career-manufacturing-cto-positioning.md"]
---

# LinkedIn Weekly Performance Review → Strategy

*Each week, ingest LinkedIn's own analytics exports — the account/overall view and each individual post — refresh the existing per-post metrics corpus, track three visibility axes over time, and end with a small set of concrete next-post recommendations. This is the **review + strategy layer**; it does not draft or score draft posts (that's [[linkedin-viral-scheduler]]) and does not tune the scorer (that's [[linkedin-scoring-calibration]]) — it reuses both, on real published/measured data.*

**Contract**
- **Input:** one weekly account-level `.xlsx` export + one `.xlsx` export per post published/measured that week, supplied by you.
- **Output:** updated vault post notes (`## Performance` / `## Audience snapshot`), a new row in `account-metrics.tsv`, and `output/linkedin/weekly-review-<YYYY-Www>.md` — the scorecard + next-post plan.
- **Bootstrap:** `account-metrics.tsv` holds your real weekly numbers and is gitignored — it never leaves your machine. First run: `cp account-metrics.tsv.example account-metrics.tsv`.
- **Allowed tools/artifacts:** `Read`/`Bash` for running the scripts, `Edit`/`Write` for vault notes and the review deliverable.
- **Done when:** the loop-integrity gate has been reported **first**, all three axes carry a week-over-week delta and a source, and 2-3 next-post recommendations are written, each mapped to the lagging axis.

**Scope note (added 2026-08-22).** This skill measures the **content** funnel. It does **not** measure progress toward the seat — that is [[career-campaign-review]], monthly, reading the contact ledger. A good content week with no ledger movement is a good content week, not progress; conflating the two is the specific error the campaign charter demoted these axes to prevent.

**Triggers/Context**
- On demand, weekly: "here are this week's LinkedIn stats", "upload weekly stats", "how did my posts do this week".
- **Not for:** drafting a new post ([[linkedin-viral-scheduler]]), tuning the Pre-Publish Audit scorer ([[linkedin-scoring-calibration]]), or editing the profile itself ([[linkedin-profile-headhunter]]).

**Core Blueprint**

### 0. First-time setup (once, or whenever a field mapping looks wrong)
- Read [`references/axes-and-intake.md`](references/axes-and-intake.md) — the three axis formulas and the intake label mapping.
- Run `scripts/ingest_xlsx.py --inspect <your export>.xlsx` on a real export and eyeball the dumped sheet/label structure against the mapping table. The label aliases in `ingest_xlsx.py` (`LABELS`, `DEMO_CATEGORIES`) are marked provisional until confirmed this way — a mismatch here means a wrong number downstream, so don't skip it on the first real run.

### 1. Intake + the loop-integrity gate (CP0)
- Create the run's STATE_ROOT: `output/.runs/<YYYYMMDD>-linkedin-weekly-review/` with `RESPONSE.md` (control spine, checkpoints below) and `EVIDENCE.md`.
- **Loop-integrity gate — run this before anything else (added 2026-08-22).** List every post published in the window. For each, confirm a vault note exists **and** a post-level export row exists, inside 72 hours of publishing. Then:
  - **Backfill what's possible** — a reach-only stub for any missed post, explicitly labelled demographics-free so the corpus stays continuous with honest holes.
  - **And block the conclusions** — if integrity is below 100%, the review **opens** with the gap and states that this window's content conclusions are partial. Do not report "reach down, buyer down" as a finding when the demographics for half the window don't exist; that is the difference between an unfavourable week and an *unknown* one, and it is the mistake that cost two weeks in August 2026 (`career-manufacturing-cto-positioning` 2026-08-18 update).
  - The gap stays at the top of every subsequent review until it is closed. This is a gate, not a metric.
- Place the week's `.xlsx` files (account export + each post export) somewhere accessible; note their paths.
- Run `scripts/ingest_xlsx.py --account <file> --week-start YYYY-MM-DD --week-end YYYY-MM-DD`. It prints every field it parsed (and every one left blank) — **confirm the printed values against the source file** before trusting the appended row. Record the file + confirmed fields in `EVIDENCE.md`.
- For each post measured this week: run `scripts/ingest_xlsx.py --post <file> --date YYYYMMDD --slug <slug>` (the note must already exist — this updates it in place, never fabricates one). Same confirm-back discipline. **CP0.**

### 2. Per-post refresh (CP1)
- Run `linkedin-viral-scheduler/scripts/viral_metrics.py` (reused, unmodified) to refresh `viral-metrics.tsv` with the updated/new post notes. **CP1.**

### 3. Account axes (CP2)
- Run `scripts/account_metrics.py` — recomputes `decision_maker_density`, `buyer_axis`, `recruiter_axis`, `reach_axis` over every row in `account-metrics.tsv` and prints the week-over-week deltas. **CP2.**

### 4. Review + next-post plan (CP3)
Write `output/linkedin/weekly-review-<YYYY-Www>.md`:
- **Three-axis scorecard** — Buyer / Recruiter / Reach: this week's value, WoW delta, and the trend direction (from step 3's output). State `n` (weeks of history) plainly — flag as directional-only below n=4 per the script's own note.
- **Per-post table** — this week's posts, their `buyer_weighted_engagement` / other Family A-B metrics (from `viral-metrics.tsv`), and which axis each mainly served.
- **H1 dialect check (added 2026-08-18) — this is the standing test of the lexicon hypothesis.** For each post this week, put `buyer_dialect` (Family B #11, now a column in `viral-metrics.tsv`) next to its `decision_maker_density` and its raw manufacturing/industrial industry share. Then answer one question in one line: **did the higher-dialect posts actually reach a more industrial audience than the lower-dialect ones?** Baseline to beat, measured 2026-08-18 across the 23 posts with demographics: **r = +0.444** (threshold 0.409), with 13 of 23 posts scoring 0 dialect. Append the running result to the review; when the corpus reaches n ≥ 40, recompute and record the verdict in [[linkedin-scoring-calibration]]'s hypothesis register (H1). **If the relationship does not hold, say so and downgrade the lever in `engagement-learnings.md` Rule 5** — that file's own instruction. This is the only place the hypothesis can be falsified, so do not skip it because the sample is small; report it small.
- **What moved the needle** — tie back to the standing content rule ([[career-manufacturing-cto-content-rule]]: story-led, not pitch-led; manufacturing-buyer co-primary; sovereignty angle over-indexes).
- **Reach is not a win on its own (added 2026-08-18).** When the Reach axis rises while Buyer falls, that is a **regression**, not a mixed result — posts shown and scrolled past are used as hard negatives in LinkedIn's retrieval training (`linkedin-viral-scheduler/references/ranking-model-2026.md` M2), so wide-and-ignored reach has a cost. Write it up that way rather than reporting "reach up, buyer down" neutrally.
- **Next-post recommendations (2-3)** — each targeted at whichever axis is currently lagging your stated goal, naming the **joint** it sits on (`ladder-joints.md`) and the **dialect** it should be written in, with the supporting proof point from [[linkedin-viral-scheduler]]'s `references/topics-and-proof-bank.md`. Recommend a joint that the recency guard permits.
- **Followers are telemetry, not an axis (added 2026-08-22).** Report follower growth as a single line without interpretation. The campaign charter retired follower count as an objective; a recommendation that would trade decision-maker density for follower growth is an anti-goal, not a trade-off to weigh.
- **Video posts (added 2026-08-22).** If the window contains a face-to-camera video ([[linkedin-video-script]]), record which fields the single-post export actually carries — whether watch-through or view-duration data exists at all is **unverified on this account**, since no video post has ever been exported. Establish it from the real file and write the answer into `references/axes-and-intake.md`; until then do not report a video metric this skill cannot source. A video's composite is `n/a` by design — the deterministic audit cannot score speech.

### 5. Evidence gate + knowledge graph (CP4)
- Run the evidence gate ([`_shared/evidence-gate.md`](../../_shared/evidence-gate.md)) — every number in the review traces to a source `.xlsx` (file + sheet + label) recorded in `EVIDENCE.md`.
- Link the review into [[career-manufacturing-cto-positioning]] and [[ladder-campaign]], and update `cbrain/notes/LinkedIn-Posts/LinkedIn-Posts-Index.md` if new posts were ingested (Charter §6).
- **Feed the contact ledger.** Any named person who replied, connected, or reached out this week goes into `output/campaign/contact-ledger.tsv` — that ledger, not these axes, is the campaign's primary indicator, and this review is one of the places its rows are noticed.
- Tick every control-spine box before stopping. **CP4.**
- End with the standard Feedback & Skill-Verification block (Charter §7).

**Optimizations/Gotchas**
- **Confirm-back is not optional on early runs.** The intake label mapping is unverified against this account's actual export format — a silent mismatch would misattribute a number, which the evidence gate exists to catch. Once a few weeks confirm clean, this step can move faster.
- **`search_appearances` may not be exportable** depending on LinkedIn account tier (it's a separate profile-analytics feature, not part of Content/Post analytics). If it's consistently blank, the Recruiter axis leans more on `recruiter_share` and `profile_views` growth — say so in the review rather than silently carrying a gap.
- **Small n, every week.** Both the account-level and post-level corpora are small; state the count and flag axes as directional until the data supports more (mirrors the post-level corpus's own posture in `viral-metrics.md`).
- **A post note must already exist to ingest its stats.** This skill never creates a post note from scratch — that happens at draft/publish time via [[linkedin-viral-scheduler]] or manual entry.
