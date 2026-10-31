# Autoresearch Loop — shared module

The design contract for any *between-run* optimization loop on the harness: `modify → verify (one number) → keep if better, else revert → log a row → repeat, bounded`. Driven by the bundled `autoresearch` skill (or a hand-rolled equivalent). Invoked by a skill that declares `modules: [autoresearch-loop]`.

*Distinct from [[self-evolution]] (reflect-and-redesign **within one run** on one deliverable) and from [[change-manifest]] (the prediction ledger that checks an edit against reality). This module governs the loop that optimizes a **skill, script, config, or vault structure** against a metric — and it exits into the change-manifest.*

*Source: an internal post-mortem, not an ablation (`output/20261009-autoresearch-loop-map.md`). The four July 2026 autoresearch runs converged on judge or self-designed rubrics (Soul.md 96.3, proposal-challenger 95.3), and a LinkedIn draft optimized to composite 98.5 reached 288 impressions against an archive mean of 1,078. The skill's most valuable fix that period (proposal-challenger v4) came from one client sentence, not from a judge. The common cause is NLAH F.1 ([[verifier-separation]]): a check helps only when it stays close to the real acceptance criterion. A loop is only as good as its verify command.*

## Before iteration 0 — the loop card
Write this to `STATE_ROOT/RESPONSE.md` before the first mutation. If you can't fill a field, don't start the loop.

| Field | Content |
|---|---|
| **Target** | The one file or config the loop may mutate (scope). |
| **Metric** | One number, its direction, and the exact command that prints it. |
| **Acceptance criterion** | The real-world test the metric stands in for, and why the metric is close to it. |
| **Eval set** | The frozen inputs the metric runs on (path), with its size *n*. |
| **Guard** | A second metric that must not regress, plus its command. |
| **Matched baseline** | The metric for the unedited target re-run with the same tries and spend, measured before iteration 0. A keep must beat it, not just the single baseline run. *(arXiv:2607.12227)* |
| **Judge probe** | Only if an LLM judge serves as metric or guard: its within-question AUC on a labelled set, logged for one cycle while it decides nothing. Near chance, no judge. *(arXiv:2608.18719)* |
| **Budget** | Iteration cap and stop rule (target hit / plateau / cap). |
| **Revert** | git for tracked files; file snapshot (`best.*` ↔ working copy) for gitignored `output/` and `cbrain/`. |

## The rules
1. **The metric must be mechanical and close to the acceptance criterion.** Good metrics include test or parse pass counts, citation resolution, link integrity, recall against a golden set, and agreement with real outcomes. If an LLM judge is the only available metric, the loop is a **guard**, not an optimizer: run it once to check, and don't iterate against it.
2. **Freeze the eval set before iteration 0.** The loop never edits its own metric, rubric, eval set, or scoring script. A change to any of those is a separate, logged decision, and it resets the baseline.
3. **Always carry a guard metric** that blocks a keep when it regresses. Examples: the recall benchmark for vault work, total length for INDEX trigger edits, and the held-out split for calibration. A metric with no guard will be Goodharted.
4. **Respect small n.** Below roughly 40 labelled outcomes, don't tune weights against outcomes: report agreement and stop. Correlations below |r|≈0.49 at n≈16 are noise (`linkedin-scoring-calibration`).
5. **Bounded and sequential.** Cap at 5–25 iterations. Mutate one thing per iteration and name the hypothesis. Don't run parallel K-candidate search, which is measured neutral-to-harmful in [`MODULES.md`](../MODULES.md). Log every iteration (kept or discarded) to `STATE_ROOT/results.tsv` in the shape `autoresearch:evals` reads.
6. **Revert by the right mechanism.** Use git for tracked files. Use file snapshots for gitignored `output/` and `cbrain/`. Take a full snapshot before any loop that edits vault notes. An unattended loop never changes git state.
7. **Run inside a STATE_ROOT,** `output/.runs/<YYYYMMDD>-<slug>/`, not only in `autoresearch/` scratch. When you drive the bundled skill, its own log dir is fine as scratch, but the final `results.tsv` and `handoff.json` must land in (or be referenced from) the STATE_ROOT. That keeps the run indexed, reopenable and covered by the control-spine gate.
8. **Exit into the change log.** A loop that keeps a change appends a [`CHANGE_LOG.md`](CHANGE_LOG.md) entry with the baseline → final metric, the guard result, and a **falsifiable prediction about real-world use**. The metric gain is not the verdict; the next real use is.
9. **Honest stop.** Report `CONVERGED`, `PLATEAU`, `CAP` or `BLOCKED` exactly as they happened. A cap hit below target is reported as incomplete, never as passing.

## Where it fits — and where it doesn't
- **Fits:** targets with a deterministic or ground-truth metric.
  - Frontmatter or lint errors → 0.
  - Skill-routing accuracy on a golden prompt set.
  - Vault link integrity, with recall as the guard.
  - Citation resolution.
  - Uncited release-critical claims → 0 (the [[evidence-gate]] as a fix-loop).
  - Scorer calibration against real outcomes once n is large enough.
- **Doesn't fit:**
  - Client deliverables judged by a rubric the same model wrote. With n≈1 per pursuit, use [[self-evolution]] in-run, and log the client's actual reaction as the outer signal.
  - Anything whose real bottleneck is human input (capture, publish/kill decisions). There a loop can measure the queue and surface its oldest item, but it can't optimize.
- **Not for one-off edits:** a single fix with an obvious check needs a test, not a loop.

## Users
- **Declared:**
  - `vault-hygiene/skill-library-maintenance`: frontmatter lint (fix-loop) and the routing eval (optimizer, with held-out and length guards).
  - `vault-hygiene/progressive-disclosure`: recall benchmark (guard only).
  - `vault-hygiene/vault-maintenance`: weekly ratchet (measure and alarm).
  - `workflow-ops/linkedin-scoring-calibration`: scorer calibration. Train-agreement metric, held-out overfit guard (gap ≤ 0.20), ~20-iteration cap, file-snapshot revert. Rule 4 applies: report agreement but don't tune weights below n≈40.
- **Uses the fix-loop:** `_shared/evidence-gate.md`, on `scripts/evidence_lint.py` blockers → 0.
- **First worked example:** `output/.runs/20261009-loops-build/RESPONSE.md`. Its loop card, noise measurement, one candidate discarded by rule and one kept are the reference shape.
