# Change Manifest — shared module

A falsifiable record for every edit to Charter.md, `MODULES.md`, `_shared/*`, or a skill's core Blueprint made under Charter §7's self-learning loop. Distinct from [[self-evolution]] (which retries *within* one run); this tracks edits *between* runs so "did that change actually help" is checkable, not anecdotal.

*Source: AHE's decision-observability pillar (Lin et al., arXiv:2604.25850, §3 / §4.4.2) — every harness edit paired with a self-declared prediction, verified against the next round's real outcome. Their evolve model's fix-precision (33.7%) and fix-recall (51.4%) ran ~5x above random-guessing baselines (6.5% / 10.6%) — the evidence that falsifiable prediction beats undirected trial-and-error. That number describes AHE's benchmark, not this repo; see `MODULES.md`'s "adopted, not yet internally measured" note.*

## The loop
1. **On edit.** When Charter §7 triggers a Charter/MODULES/`_shared`/skill-Blueprint optimization, append one entry to [`_shared/CHANGE_LOG.md`](CHANGE_LOG.md): the failure signal that motivated it, the file(s) touched, what the edit is expected to fix, and what it risks regressing. An edit to a harness mechanism (a hook, a launcher, an agent definition, a run-forensics fix) also gets two lines:
   - **Refuted if:** the observation that would show it failed.
   - **Fires on stable:** whether it triggers on runs that already succeed, and at what cost. *(RiseHarness, arXiv:2610.27435: every proposal states `refuted_if` and is checked against always-passing runs before it is built.)*
   - **Matched baseline:** what an unedited re-run at the same spend scores (same tries, same budget). Credit the edit only above that. *(arXiv:2607.12227: on Terminal-Bench 2.1, automatic harness evolution did not beat plain test-time scaling once budgets were matched.)*
   - **Judge competence (only when an LLM judge decides the verdict):** the judge's within-question AUC on a labelled set, measured once with the judge deciding nothing. Near chance, the judge is not a valid gate. *(arXiv:2608.18719: a reference-free judge's discrimination falls to chance below a competence floor.)*
2. **On next use.** The next time the edited mechanism is exercised for real, check the entry against what actually happened. Record one verdict: `confirmed`, `not confirmed`, or `regressed`.
3. **Weekly sweep, so step 2 actually happens.**
   - Run `python3 resources/skills/_shared/scripts/verdict_sweep.py --log output/verdict-sweep/results.tsv`. It lists every pending entry as READY (a later run names the touched skill in its spine header), MENTIONED (named only in a run's body, often an audit) or NO-USE-YET.
   - **Judge at most 5 READY entries per pass** from the evidence the sweep points at. Write a dated verdict with one line of proof per checked clause. Where the evidence can't test the prediction as worded, write `partial` or `pending — blocked`; never stretch it to `confirmed`.
   - **Metric:** `pending_over_14d`, lower is better. Baseline 2026-10-09: 12 → 9 after the first pass.
4. **Honest ledger.** Never delete a disconfirmed entry — a wrong prediction is itself signal about which edits are safe to make un-reviewed versus which need a second pair of eyes next time.

## When NOT to use it
Skip for one-off content edits with no reusable mechanism (a typo fix, a date update, a single SKILL.md's prose tightened without changing its Blueprint). Reserve for edits that change *behavior* future runs will inherit.
