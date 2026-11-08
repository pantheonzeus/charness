---
id: linkedin-scoring-calibration
aliases: [linkedin-scoring-calibration]
name: "LinkedIn Scoring Calibration — Backtest & Tune the Scorer on Real Data"
category: workflow-ops
description: "Turn the vault's real LinkedIn post statistics into a labelled dataset, then use autoresearch to calibrate the Pre-Publish Audit scorer (Scorecard B of the viral-scheduler's rubric — see `linkedin-viral-scheduler/references/rubric.md`) so its predicted performance matches actual Buyer-Weighted Engagement (Scorecard D — engagement rate discounted/rewarded by decision-maker audience density, retargeted 2026-07-19 from a raw reach×engagement blend per Rule 4 \"reach is not the target\") — with a train/test split, an overfit guard, evidence-cited baselines, and a \"what actually moves engagement\" analysis. Note: this calibrates the deterministic Scorecard B only; the blind-judged Scorecard A (Substance) and Scorecard C (Audience Pull, added 2026-07-19) are out of scope for this dataset-driven calibration."
triggers: [calibrate linkedin scoring, tune post rubric, validate scoring against real data, linkedin analytics calibration, why did my post underperform, what to improve linkedin, score accuracy, backtest linkedin scorer, does the scorer predict engagement, buyer-weighted engagement calibration]
tags: [linkedin, calibration, autoresearch, analytics, evidence, scoring, deterministic-scoring, headless]
related: ["[[linkedin-viral-scheduler]]", "[[linkedin-authentic-storytelling]]"]
status: active
version: 6
created: 2026-07-12
updated: 2026-10-23
modules: [file-backed-state, evidence-backed-answering, file-backed-handoff, verifier-separation, autoresearch-loop]
requires:
  bundled-skills: [autoresearch]
environment: "Runs where the vault's cbrain/notes/LinkedIn-Posts/ dir and the sibling linkedin-viral-scheduler/scripts/prepublish_audit.py are present (the latter is imported, not forked). Pure Python stdlib — no numpy/pandas. Headless mode (scripts/run.sh) needs a local `claude` binary + vault access; no MCP required, so it degrades cleanly on a scheduler. Scheduled weekly via launchd (a cloud routine would lack local claude auth + vault access)."
scripts: [scripts/build_dataset.py, scripts/calibrate.py, scripts/calibration.json, scripts/run.sh]
workflows: [workflows/headless-calibration.md]
references: [references/methodology.md]
vault_writes: ["cbrain/notes/LinkedIn-Posts/*"]
---

# LinkedIn Scoring Calibration

**Triggers/Context**
- The two-gate scorer in [[linkedin-viral-scheduler]] predicts "viral potential" from **hand-guessed thresholds that have never been checked against a single real engagement number.** This skill closes that loop: it grounds the scorer in the account's own post statistics.
- Fire it when: asked to calibrate/validate/backtest the LinkedIn scorer, to explain why posts under- or over-perform, to learn *what to actually improve*, or on a cadence as new posts accumulate (re-run to keep the scorer honest).
- **Data source:** `cbrain/notes/LinkedIn-Posts/YYYYMMDD-*.md` — one file per post, `## Post` body + `## Performance` metrics + frontmatter.

**The honest constraint — state it, never bury it.** With ~16 posts (12 train / 4 test) a *validated* 98% is arithmetically impossible: a 4-post test set only reads 0/25/50/75/100%, and feature correlations below |r|≈0.49 are noise. So the deliverable is a **genuine re-runnable engine** that reports honest agreement now and trends toward 98% as the corpus grows — not a faked number today. Every figure ships with its `n` and, for test figures, the `1/n` resolution caveat (Charter §4 evidence gate; Soul.md "never oversell the numbers"). Full statistics in [references/methodology.md](references/methodology.md).

## Core Blueprint

Run under a STATE_ROOT: `output/.runs/YYYYMMDD-linkedin-calibration/`. Point the scripts' `--out`/`--data`/`--train`/`--test` there so derived data stays out of the skill folder (only `calibration.json` is tracked — autoresearch git-loops it).

**1 — Build the labelled dataset.**
`python3 scripts/build_dataset.py --out $STATE_ROOT/dataset.tsv`
Parses every post, scores the body with the **imported** live scorer (never re-implemented), and writes features + actual outcomes, one post per row. This is the "real statistical data" deliverable.

**2 — Judge substance once (file-backed, verifier-separation).**
Substance (M1 Topic-DNA + M3 Depth, 2–10) is subjective, so it is scored **once** and frozen — the loop tunes its *weight*, never the judgment (see methodology §3). Use **one consistent rater over all posts** (not the ship-gate's 3-blind-judges-per-post — a relative ranking needs a consistent rater). Per `_shared/delegation-handoff.md`: write the brief + the M1/M3 table from [[linkedin-viral-scheduler]]'s `rubric.md` to `$STATE_ROOT/children/substance/TASK.md`, the child writes a `file<TAB>substance` TSV to `RESPONSE.md`, **reopen it from disk**, then rebuild: `python3 scripts/build_dataset.py --substance $STATE_ROOT/substance.tsv --out $STATE_ROOT/dataset.tsv`. **Skipping this leaves substance at a flat neutral 6 — half the signal becomes a constant and calibration cannot climb far. It is a prerequisite, not an extra.**

**3 — Label & split.**
`python3 scripts/calibrate.py label --data $STATE_ROOT/dataset.tsv` → per-post Buyer-Weighted Engagement tercile (Under/On/Over — retargeted 2026-07-19 from a raw reach×engagement blend, see `references/methodology.md` §1 for why and the resulting discontinuity in `calibration-history.tsv`) + **evidence-cited account baselines** (median impressions/post, top-quartile line, blended engagement rate, reach-per-follower @ your follower base).
`python3 scripts/calibrate.py split --data $STATE_ROOT/dataset.tsv --train $STATE_ROOT/train.txt --test $STATE_ROOT/test.txt` → deterministic, stratified 12/4.

**4 — Calibrate with autoresearch (the engine — do not hand-roll a loop).**
Drive [[autoresearch]]. Keep/discard is a **file-snapshot** on `$STATE_ROOT/{calibration.working.json,best.json}` — **not** git; an unattended run must never mutate the repo's git state, and the sibling skill uses file-snapshots for the same reason. Only the final winning config is copied to `scripts/calibration.json` at finalize, and only if the gate passes.
- **Scope:** `$STATE_ROOT/calibration.working.json` (a copy of `scripts/calibration.json`; the durable calibrated config is written back only on a clean gate).
- **Metric:** train-set tier agreement · **Direction:** `higher_is_better`.
- **Verify:** `python3 scripts/calibrate.py verify --data $STATE_ROOT/dataset.tsv --config $STATE_ROOT/calibration.working.json --split train` — prints one number.
- **Guard (overfit tripwire):** `python3 scripts/calibrate.py evaluate ...` — reject a mutation where train rises but test falls (gap > 0.20).
- **Iterations:** bounded (~20). Each iteration mutates ONE knob (a composite weight, `substance_weight`, or a tier cutoff — the small surface is deliberate; see methodology §2). Log an autoresearch:evals-compatible row to `$STATE_ROOT/results.tsv` with the reasoning in `description`.
Then `autoresearch:evals` on the run's `results.tsv` for trend / plateau / stop.

**5 — Evaluate on held-out + find what to improve.**
`python3 scripts/calibrate.py evaluate --data $STATE_ROOT/dataset.tsv --config $STATE_ROOT/best.json` → train + test agreement + overfit gap (with the small-n caveat auto-printed).
`python3 scripts/calibrate.py correlate --data $STATE_ROOT/dataset.tsv` → ranks which features actually move the outcome + the engagement-shape lens (do comments/reactions precede reach?). This is the **"know what to improve"** deliverable.

**6 — Report (deterministic — one command).**
`python3 scripts/calibrate.py report --data $STATE_ROOT/dataset.tsv --baseline-config $STATE_ROOT/baseline.json --config $STATE_ROOT/best.json --results $STATE_ROOT/results.tsv --train $STATE_ROOT/train.txt --test $STATE_ROOT/test.txt --out output/linkedin/calibration-report-<date>.md --history output/linkedin/calibration-history.tsv --date <date>` → renders the writeup (run summary, cited baselines, before→after knob diff, per-iteration narrative, train vs test each with n + caveat, correlation findings, honest ceiling) and appends the run-over-run history row. Run the evidence gate before release.

**7 — Auto-update the live scorer (user chose this).**
When test agreement validates the new config *and* the overfit gap is clean, apply the calibrated weights/cutoffs into [[linkedin-viral-scheduler]]'s `references/rubric.md` and `scripts/prepublish_audit.py`, and bump that skill's `version`/`updated` **in the same change**. Record the exact diff in the report as evidence. If the gap is not clean, do **not** ship — report the honest ceiling and recommend more posts.

## Headless / Automated run (the loop takes all the work on its own)

The steps above are the interactive path. For unattended runs, everything is wrapped so **one command runs the whole calibration end-to-end with no human in the loop** — mirroring [[linkedin-viral-scheduler]]'s cron entrypoint and output shape.

- **Entrypoint:** `scripts/run.sh [YYYY-MM-DD]` — resolves its own path, sets PATH, `cd`s to the repo root, and `exec`s one headless `claude -p "<packet>" --dangerously-skip-permissions`. That flag is required, not optional: a scheduler can't answer prompts, and `--permission-mode acceptEdits` auto-approves edits but NOT `python3` execution, so this Python-driven pipeline stalls at CP0 under `acceptEdits`. Scope stays bounded (skill scripts only, appends to `output/`, no git ops). `./run.sh --dry-run` prints the resolved command and launches nothing.
- **The autonomous procedure** the session follows is [workflows/headless-calibration.md](workflows/headless-calibration.md), keyed to a `RESPONSE.md` **control spine** (CP0 dataset · CP1 substance · CP2 label/split · CP3 tuning loop · CP4 finalize). The Stop-hook (`.claude/hooks/control-spine-gate.sh`) refuses to let the run exit while any `[ ]` remains — so completing the spine *is* the completion condition, and a half-done calibration can't silently pass.
- **Mechanical / judgment split:** every measurement (dataset, verify, evaluate, correlate, report) is deterministic Python; the LLM does only judgment — rating substance once (consistently, incrementally cached), choosing which knob to move each iteration, and the gated update decision. The report always renders (pure Python) even if the model stalls.
- **Keep/discard is file-snapshot, never git** (`STATE_ROOT/{calibration.working.json,best.json}`) — an unattended job must never mutate the repo's git state. Only the final winning config is copied back to `scripts/calibration.json`, and only if the gate passes.
- **Output/results/reasoning** land where you'd expect them from the sibling skill: `output/linkedin/calibration-report-<date>.md` (the writeup), `output/linkedin/calibration-history.tsv` (run-over-run progress toward 98%), and `STATE_ROOT/{results.tsv,RESPONSE.md,EVIDENCE.md}` (the ledger, control spine, provenance).
- **Schedule (launchd, weekly).** Cadence is low — calibration only needs re-running as new posts accumulate. Install a weekly agent, e.g. `com.cbrain.linkedin-scoring-calibration`, Monday 08:00:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.cbrain.linkedin-scoring-calibration</string>
  <key>ProgramArguments</key><array>
    <string>/bin/bash</string>
    <string><REPO>/resources/skills/workflow-ops/linkedin-scoring-calibration/scripts/run.sh</string>
  </array>
  <key>StartCalendarInterval</key><dict>
    <key>Weekday</key><integer>1</integer><key>Hour</key><integer>8</integer><key>Minute</key><integer>7</integer>
  </dict>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>/Users/<you>/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
  </dict>
  <key>StandardOutPath</key><string><REPO>/output/linkedin-scoring-calibration.log</string>
  <key>StandardErrorPath</key><string><REPO>/output/linkedin-scoring-calibration.log</string>
</dict></plist>
```
Install: `launchctl load ~/Library/LaunchAgents/com.cbrain.linkedin-scoring-calibration.plist`. **Crontab alternative:** `7 8 * * 1 <REPO>/resources/skills/workflow-ops/linkedin-scoring-calibration/scripts/run.sh >> <REPO>/output/linkedin-scoring-calibration.log 2>&1`.

## Optimizations/Gotchas
- **Reuse, don't fork.** `build_dataset.py` imports `prepublish_audit.py`'s text-analysis functions. Keep the two skills adjacent; if the scorer's functions move, fix the import path, don't copy the logic.
- **Chance is 33%, not 0%.** Three balanced terciles → a random scorer scores ~33%. Iteration-0 (today's live scorer) currently sits there — the honest starting point, and the reason the loop has room.
- **Small tunable surface on purpose.** Do not add internal-band knobs (hook length, word count) until test n ≳ 30–40; on 12 posts they overfit. Widen only when the data earns it.
- **Re-runnable is the point.** Log each run's test agreement over time (in the report's history line). The 98% target is an asymptote reached as the corpus grows, tracked run-over-run — not a one-shot claim.

## Feedback & Skill Verification
1. Would you like to provide feedback to optimize this workflow or execution?
2. Should we add a new skill (or update an existing one) for this task in `resources/skills/`?
