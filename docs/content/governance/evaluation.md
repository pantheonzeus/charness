# Evaluation

A harness that can't show it still works after a change is a liability. charness measures harness behaviour, and it says plainly what it doesn't measure yet.

## What is measured

| Eval | What it checks | Where |
|---|---|---|
| **Regression suite** | One probe per recorded failure code or Charter rule: skill misroutes, capability check before denial, resistance to untrusted-ingest injection, permission blocks in headless Bash. Each probe is a headless run against the real harness with read-only tools, graded by code from the transcript. | [`regression.json`](gh:resources/skills/workflow-ops/run-forensics/evals/regression.json), runner `scripts/regression.py` |
| **Hook test suites** | Deterministic cases for every guard: allowed and denied writes, egress shapes, send approvals, provenance stamping. | [`.claude/hooks/tests/`](gh:.claude/hooks/tests/), run by `scripts/check.sh` in CI |
| **Routing recall** | Does the preselector put the right skill in its top five? | `scripts/skill_router.py eval` against your own golden set |
| **Quality floors** | Did a daily-intel or meeting-prep run meet the floors its own skill states (searches, sources, documents opened)? | `run-forensics/scripts/quality.py` |
| **Change manifest** | Each harness edit predicts its effect; the prediction is checked at the next real use. | [`_shared/change-manifest.md`](gh:resources/skills/_shared/change-manifest.md) |

## pass^3

A probe passes only if it passes in **all three of three runs**. A probe that passes once in three runs is a failing probe that sometimes gets lucky. The suite runs before and after every harness edit and on every model change.

## Model changes

A job's model changes only when the candidate model holds pass^3 on that job's probes (`regression.py --model`). Harness gains are model-specific, so the suite reruns on every model upgrade. A daily check runs the suite on any pinned model that has no passing run yet. The current results are on the [HarnessCard](harnesscard.md).

## What is not measured yet

There are no output-quality evals for the deliverables themselves (briefings, plans, drafts): nothing grades them mechanically yet. The suite tells you the harness behaves. It doesn't tell you the brief is good. That gap is stated on the [HarnessCard](harnesscard.md) too.

## Golden sets stay private

Routing and recall golden sets live in `resources/skills/_evals/`, which is git-ignored: real prompts carry real names. Build your own from your sessions.
