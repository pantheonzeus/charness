# Workflow: headless-calibration

The exact end-to-end procedure a headless `claude -p` run follows (launched by
`scripts/run.sh`). Runs unattended — no questions, no human in the loop. Do the
steps in order, tick each control-spine checkpoint as you clear it. The Stop-hook
(`control-spine-gate.sh`) will refuse to let the run exit while any `[ ]` remains,
so finishing the spine IS the completion condition.

Paths are relative to the repo root (run.sh `cd`s there). Shorthands:
- `SKILL = resources/skills/workflow-ops/linkedin-scoring-calibration`
- `STATE_ROOT = output/.runs/<YYYYMMDD>-linkedin-calibration` (use the run date)
- `SCORER = resources/skills/workflow-ops/linkedin-viral-scheduler`

## Step 0 — Open the run & write the control spine

Create `STATE_ROOT/` and write `STATE_ROOT/RESPONSE.md` with these unchecked boxes verbatim:

```markdown
# Control Spine — LinkedIn Scoring Calibration (<YYYYMMDD>)

Run: <YYYYMMDD>-linkedin-calibration · headless.

## Checkpoints
- [ ] **CP0** Dataset built from the vault posts
- [ ] **CP1** Substance judged (incremental) and dataset rebuilt
- [ ] **CP2** Labelled & split (12/4), baselines captured
- [ ] **CP3** autoresearch tuning loop converged (results.tsv written)
- [ ] **CP4** Report + history written; live-scorer update decided; evidence gate run
```

## CP0 — Build the dataset

```
python3 SKILL/scripts/build_dataset.py --out STATE_ROOT/dataset.tsv
```
Confirm 16 rows. Tick **CP0**.

## CP1 — Judge substance (incremental, one consistent rater)

Substance = M1 Topic-DNA + M3 Depth (2–10), the ONE subjective feature (methodology §3).
Rate it once, consistently, and cache it.

1. Read `STATE_ROOT/substance.tsv` if it exists; note which post files are already rated.
2. For every post file **not** already cached: read its `## Post` body from
   `cbrain/notes/LinkedIn-Posts/<file>` and score M1 (0/1/3/5 scaled → contribution)
   and M3 using the M1/M3 table in `SCORER/references/rubric.md`. **You are the single
   consistent rater across all posts** — do not spawn 3 blind judges (that protocol is
   for the ship gate; a relative ranking needs one consistent rater).
3. Append `file<TAB>substance` rows (substance = M1+M3, 2–10) to `STATE_ROOT/substance.tsv`
   (header `file\tsubstance`).
4. Rebuild the dataset with the cache:
```
python3 SKILL/scripts/build_dataset.py --substance STATE_ROOT/substance.tsv --out STATE_ROOT/dataset.tsv
```
Confirm the run prints `substance: 16 judged`. Tick **CP1**.

## CP2 — Label & split

```
python3 SKILL/scripts/calibrate.py label --data STATE_ROOT/dataset.tsv 2> STATE_ROOT/baselines.txt
python3 SKILL/scripts/calibrate.py split --data STATE_ROOT/dataset.tsv \
    --train STATE_ROOT/train.txt --test STATE_ROOT/test.txt
```
Tick **CP2**.

## CP3 — The autoresearch tuning loop (file-snapshot keep/discard — NEVER git)

Snapshot the starting config; the loop only ever edits the working copy:
```
cp SKILL/scripts/calibration.json STATE_ROOT/baseline.json
cp SKILL/scripts/calibration.json STATE_ROOT/calibration.working.json
cp SKILL/scripts/calibration.json STATE_ROOT/best.json
```
Write the results ledger header (autoresearch:evals-compatible):
```
printf '# metric_direction: higher_is_better\n' > STATE_ROOT/results.tsv
printf 'iteration\ttimestamp\tcommit\tmetric\tdelta\tguard\tguard-metric\tstatus\tdescription\n' >> STATE_ROOT/results.tsv
```
Record the baseline row (iteration 0) using the current train/test agreement (run
`verify --split train` and `--split test` on `best.json`).

Then run the autoresearch loop, **budget 20 iterations**. Each iteration:
1. **Read** the last rows of `STATE_ROOT/results.tsv` as memory.
2. **Hypothesize** the single weakest knob and ONE targeted change. Tunable knobs only
   (methodology §2): a `composite_weights` entry, `substance_weight`, or a `tier_cutoffs`
   boundary. One knob per iteration — never several.
3. **Mutate** `STATE_ROOT/calibration.working.json` (that one knob).
4. **Metric:** `python3 SKILL/scripts/calibrate.py verify --data STATE_ROOT/dataset.tsv --config STATE_ROOT/calibration.working.json --split train` → the printed number.
5. **Overfit guard:** `python3 SKILL/scripts/calibrate.py evaluate --data STATE_ROOT/dataset.tsv --config STATE_ROOT/calibration.working.json --train STATE_ROOT/train.txt --test STATE_ROOT/test.txt` → note test agreement + gap.
6. **Decide:**
   - **keep** if train improved AND the guard is clean (test did not fall while train rose; gap ≤ 0.20): `cp STATE_ROOT/calibration.working.json STATE_ROOT/best.json`.
   - **discard** otherwise: `cp STATE_ROOT/best.json STATE_ROOT/calibration.working.json`.
7. **Log** one row to `results.tsv`: `iteration`, ISO timestamp, `-`, train metric, delta,
   guard `pass`/`fail`, test agreement, status (`keep`/`discard`), and a `description`
   naming the knob move + why (`substance_weight 0.50->0.60; weakest=flat-substance pull`).
8. **Stop** when: both no single-knob move improves train for a full sweep (`status=converged`),
   or a 3-iteration plateau, or 20 iterations spent (`status=budget-exhausted`). Log the stop reason.

Tick **CP3**.

## CP4 — Finalize: report, history, gated update, evidence gate

1. Generate the deterministic report + history append:
```
python3 SKILL/scripts/calibrate.py report --data STATE_ROOT/dataset.tsv \
    --baseline-config STATE_ROOT/baseline.json --config STATE_ROOT/best.json \
    --results STATE_ROOT/results.tsv --train STATE_ROOT/train.txt --test STATE_ROOT/test.txt \
    --out output/linkedin/calibration-report-<YYYY-MM-DD>.md \
    --history output/linkedin/calibration-history.tsv --date <YYYY-MM-DD>
```
   (Add `--scorer-updated` only in step 3 if you actually update the scorer.)

2. **Decide the live-scorer update (gated).** Read the final train/test agreement + gap.
   Update the live scorer **only if** the overfit gap is clean (|gap| ≤ 0.20) AND test
   agreement improved over the baseline row. Otherwise change nothing — this is the honest
   default at small n; say so in the report.

3. **If (and only if) the gate passed:**
   - `cp STATE_ROOT/best.json SKILL/scripts/calibration.json`
   - Apply the calibrated `composite_weights` into `SCORER/scripts/prepublish_audit.py`
     (the `0.30·hook + 0.20·readability + 0.20·spacing + 0.30·aifluff` line in `main()`)
     and into `SCORER/references/rubric.md` (the composite formula + combined-objective
     weights). Bump `SCORER/SKILL.md` `version` + `updated`.
   - Re-run `python3 SCORER/scripts/prepublish_audit.py <any post>` to confirm it still runs.
   - Re-run `report ... --scorer-updated` so the report + history record the change, and
     append the exact diff to `STATE_ROOT/EVIDENCE.md`.

4. **Evidence gate** (`resources/skills/_shared/evidence-gate.md`): every release-critical
   number in the report is tagged observed/inferred and carries its `n`. Write
   `STATE_ROOT/EVIDENCE.md`. The report must not claim a validated accuracy it cannot support.

Tick **CP4**. All boxes checked → the run may exit.

## Idempotency & failure
- Re-running the same day reuses `STATE_ROOT` and the cached `substance.tsv`; only new posts get re-judged and the loop re-optimizes. Safe to re-run.
- No MCP needed (pure local vault + `python3` + `claude`). No git operations at any point.
- If a step fails, leave its checkbox unticked — the Stop-hook will keep the run from silently exiting on a half-done calibration.
