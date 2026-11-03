---
id: run-forensics
aliases: [run-forensics, failure-taxonomy]
name: "Run Forensics — Failure Codes, Quality Floors, Recurrence, Verified Fixes & Regression Suite"
category: workflow-ops
description: Classify why every headless agent run failed or degraded (closed taxonomy, from the run's own transcript plus the hooks' logged decisions; for daily-intel and meeting-prep also whether the run did the work its skill requires), detect failure codes that recur across runs and jobs, and close the loop with a human-approved harness fix (diagnosed against a clean run of the same job, revised against what the harness can see and already does, designed from a precedent) that is verified automatically on the next runs — over a window scaled to how often the code hit, per model.
triggers: [why did the run fail, job quality, quality floor, is the briefing getting worse, did the model change hurt quality, run failed, recurring failure, failure mode, same failure again, fix the recurring failures, fix PERM_BLOCKED, fix SKILL_MISROUTE, run forensics, agent errors, ops failures, harness self-improvement, error analysis, flipping runs, compare a failing run with a clean one]
tags: [harness, ops, observability, self-improvement, error-analysis]
related: []
modules: [file-backed-state, decision-observability, self-evolution]
status: active
version: 8
created: 2026-10-20
updated: 2026-11-01
---

# Run Forensics — Failure Codes, Quality Floors, Recurrence, Verified Fixes & Regression Suite

**The problem it solves.** `run_agent.sh`'s ledger records exit codes, and nearly every run exits 0 with `subtype: success`. The transcript underneath tells a different story: on 2026-10-20, 113 of 186 ledgered runs were *degraded* — ~215 blocked shell commands, 46 repo skills called through the Skill tool, 38 guessed paths — and nothing grouped them or noticed they came back every day.

**Contract**
- **Input:** `output/.runs/_ledger/*.jsonl` (one line per run, incl. `models` and `git_sha`), each run's transcript `~/.claude/projects/*/<session_id>.jsonl`, and the hooks' decision log `output/.runs/_forensics/hooks.jsonl` (written by `.claude/hooks/write-boundary.sh` and `control-spine-gate.sh`).
- **Output:** `output/.runs/_forensics/runs.jsonl` (per-run outcome + codes + normalized signatures + `hooks` summary), `output/run-forensics/issues.json` (issue state machine), `output/run-forensics/report-<YYYYMMDD>.md` (daily), Jarvis Ops panel + island pill.
- **Allowed tools/artifacts:** `scripts/forensics.py` and `scripts/quality.py` (stdlib, deterministic — no LLM in the hot path); `references/handbook.md` (which harness behavior owns each code, and where its code lives); for the fix step, edits to `.claude/agents/*.md`, a job's `--allowedTools`, a skill's `SKILL.md`, a hook, or `schema/taxonomy.json`.
- **Done when:** (detection) every ledgered run is classified and the unclassified share is < 5%; (fix) the issue is `verified`: `needs` clean post-fix runs of the affected jobs on their current model, zero recurrences.

**Triggers/Context**
- The island shows *"Ops: N recurring failures"* or *"fix for X didn't hold"*; the principal says "fix <CODE>" / "why did <job> fail".
- After any new scheduled agent is added (its runs flow in automatically through `run_agent.sh`).

## The loop
```
run ends → run_agent.sh → forensics.py ingest      (per run: classify, never fails the job)
07:20 daily → launchd com.cbrain.run-forensics → forensics.py report
              → recurring code (≥ 2 runs / 7 d) opens an issue → Jarvis island pill
principal: "fix <CODE>" → this skill's fix step (below) → forensics.py fixed <CODE> --note …
              → judged every report on post-fix runs of the fixed jobs only (never the pre-fix runs still in the window),
                each job on its current model only (a model change restarts that job's count):
                `needs` clean, 0 hits → verified · hitting ≥ half the pre-fix share of runs → regressed (alarm pill)
                · anything else → `fixing` (slips below that bar, too few runs yet, or a code too rare to verify)
```
**`needs`** is the smallest n with (1 − pre-fix share)^n ≤ 10%, at least 5: the number of clean runs after which a fix that did nothing would have been caught at least 90% of the time. A code that hit 52% of runs needs 5; one that hit 18% needs 12; one that hit 6% needs 38. Above 30 the code is **too rare to verify by recurrence**: it stays `fixing`, and its verdict comes from reading post-fix traces (say so in the change log). *(Before v5 every fix needed 5 runs; BOUNDARY_BLOCKED went `verified` on 5 clean runs at a 6% pre-fix rate, which a do-nothing fix passes 73% of the time.)*

## Taxonomy (closed; `schema/taxonomy.json`)
**Run level → `failed`** (first/root failure only — an API outage also loses the handoff, the outage is the cause): `AUTH_EXPIRED` · `INFRA` · `BUDGET` · `GATE` · `NO_HANDOFF`.
**Auth alarm:** `AUTH_EXPIRED` does not wait for the daily report or a second run. `run_agent.sh` matches the auth error on the first failed run, writes `output/.runs/_forensics/auth-alarm.json`, sends one macOS notification and Jarvis shows a red pill until the next good run removes the file. The fix is always the same: run `claude` and log in.
**Step level → `degraded`:** `PERM_BLOCKED` · `BOUNDARY_BLOCKED` · `SKILL_MISROUTE` · `STALE_EDIT` · `PATH_MISS` · `ENV_MISSING` · `BAD_INPUT` · `QUALITY_FLOOR` (no tool error: the run skipped work its skill requires, section D). Recorded but never an issue (`track: false`): `NET_FAIL`, `CMD_FAIL` (exploration noise). Anything else → `UNCLASSIFIED`, which *is* tracked — a recurring unclassified signature means the taxonomy needs a rule.
Each code carries its MAST and TRAIL mapping and a fix hint.

## Core Blueprint

### A. Detection (automatic — nothing to do)
`ingest` and the daily `report` keep it current. To refresh by hand: `python3 resources/skills/workflow-ops/run-forensics/scripts/forensics.py report`.

### B. Fix step (on the principal's word — Charter §7)
1. **Read a failing run next to a clean one** (RiseHarness: a success under the same configuration is the reference; Meta-Harness: raw traces beat summaries). `forensics.py pair <CODE> [--job <job>]` picks the latest run with the code whose transcript survives, and the run of the same job and model without it (same git_sha first, a clean run first, then nearest in time). It prints both transcript paths and both tool timelines around the first failing call. The "diverge at call N" line compares tool names only: treat it as a pointer, not a diagnosis. Read both transcripts around that point. Name the *first* failure, why the agent made that call, and what the clean run did instead. No reference left (`REFERENCE none`) → read 2–3 failing transcripts from `issues.json` → `sessions`, and say the diagnosis has no reference.
2. **Write the wish, then revise it against the harness.** State what the harness should do, and under which observable condition. Then answer two questions from the traces, the hook log (`output/.runs/_forensics/hooks.jsonl`, or the run's `hooks` summary) and the code at the issue's `Owner` sites (`references/handbook.md`):
   - **can**: does the harness hold the information this needs, at that moment? If not, the fix must produce that signal itself (e.g. the agent runs its own check), or there is no fix. Say so; don't invent one.
   - **already**: does the harness already do this, *including as prose* in a skill or agent definition? If it does and the agent ignored the prose, the fix is a mechanism (a hook, a script, `--allowedTools`, a seeded file or path), not another sentence. *(2026-10-20 STALE_EDIT: living-plan already said "rewrite the whole file", and the agent ignored it. The [[AI SDLC]] evidence: prompt-only harness optimisation regressed −2.3pp.)*
3. **Look for a precedent before designing.** Run 2–4 web searches on two scopes. *Framework*: how Claude Code, OpenHands, SWE-agent or Aider handle the same behavior. *Transfer*: a non-agent system with the same problem; RiseHarness turned pytest's `--lf` into an unresolved-failure ledger. Record the precedent, how its signals map onto ours, and its status: `direct`, `needs extension`, or `none found → local design, labelled`. A failed search is not evidence that no precedent exists. *(In the RiseHarness ablation, dropping external research cost 5.5 points of Pass@1.)*
4. **Pick the smallest harness edit at the right layer** — fix the system, not the run (SRE postmortem rule):
   - a behavior many agents repeat (`SKILL_MISROUTE`, `BOUNDARY_BLOCKED`, `PATH_MISS`) → one line in each affected `.claude/agents/<job>.md` or the shared Charter/skill text;
   - a command a job legitimately needs (`PERM_BLOCKED`) → that job's `--allowedTools` in its launcher script, **never** a blanket allow; otherwise tell the agent to use Read/Grep/Glob and single plain commands;
   - a missing dependency (`ENV_MISSING`) → install once or remove the step;
   - `UNCLASSIFIED` → add a rule (or, rarely, a code) to `schema/taxonomy.json`, then delete `output/.runs/_forensics/runs.jsonl` and re-run `report` to reclassify. Reclassifying empties the issue's `jobs`, so step 6 must name them: `fixed UNCLASSIFIED --jobs <the jobs that had it>`.
5. **Show the edit + its prediction, get a yes.** Three parts:
   - **Predicts**, falsifiably: *"<CODE> on <jobs> drops to 0 over its verification window"* (the issue's `needs`, from the pre-fix share).
   - **Refuted if**: the observation that would show the fix failed or did harm.
   - **Fires on stable**: read one transcript of an always-clean job that passes through the same site, and say whether the change would trigger there and at what cost (turns, money, a wrong refusal).
6. **Apply, then open the verification window:** `forensics.py fixed <CODE> --note "<what changed>" [--jobs a,b]`. If the edit adds or moves a mechanism, update its row in `references/handbook.md` and the code's `sites` in `schema/taxonomy.json` in the same change.
7. **Log a change-manifest entry** in `_shared/CHANGE_LOG.md` with all three lines (`Verdict: pending — run-forensics`). The daily report settles it:
   - `verified` → write the verdict.
   - `regressed` → the fix didn't hold: revert or redesign (a materially different edit, per `self-evolution`), never re-apply the same one.
   - Too rare to verify by recurrence → judge it from post-fix traces, and write that it was judged that way.
   - "Model changed on <job>" → the earlier verdict no longer holds for that job. It is being re-verified on the new model; say so in the entry.

### C. Regression suite (harness evals, added 2026-10-23)
Forensics reacts to failures in production runs; the suite tests the harness on purpose. `evals/regression.json` holds one probe per recorded failure code or Charter rule (SKILL_MISROUTE, PERM_BLOCKED, capability check, untrusted ingest). Each probe is a headless `claude -p` in the repo with read-only tools, graded by code from the transcript, run k = 3 times and reported as **pass^3** (Anthropic, "Demystifying evals for AI agents", 2026-01: start from real failures, code graders, consistency over pass@1).
- Run: `python3 resources/skills/workflow-ops/run-forensics/scripts/regression.py [--only P1,P4] [--model claude-sonnet-5-5] [--effort high] [--addendum FILE | --no-addendum]`; results in `output/regression/<stamp>.tsv`, each row with its model, effort and addendum. A probe runs with its model family's addendum (`resources/models/<family>.md`), as the jobs do.
- **When:** before and after any harness edit (hook, Charter, `_shared`, agent file, model addendum), and on every model change: `--model <candidate>` is the model-swap test, and a job's `model:` changes only when the candidate holds pass^3 on that job's probes.
- **Models are pinned, and the check is automatic (2026-11-01).** Agent files carry full model IDs and an `effort:`, never an alias, so no model changes under a job unannounced (the `sonnet` alias moved Sonnet 5 → 5.5 on 2026-10-25 and no suite ran). `forensics.py models`, run by the daily report, maps each harness job to its pinned model (else its last run's). A model and addendum with no finished pass^3 suite gets one suite started in the background, and `output/.runs/_forensics/model-alarm.json` shows an Ops pill in the console until a suite passes. A failed suite is never retried on its own: read the TSV, fix or roll back the pin, rerun by hand.
- **Addenda change like hooks.** A new or edited `resources/models/<family>.md` runs the suite with `--addendum <candidate>` before it goes into `resources/models/`, where every job on that family picks it up at its next run.
- **Grow it from failures:** when a code recurs (step B), add a probe that reproduces it before fixing; the fix is verified when the probe passes pass^3 and stays green.
- Probes never write to the vault or send: keep their tools read-only or one allowlisted helper, and put fixtures under `output/regression/fixtures/`, never in a run's STATE_ROOT (the Stop gate would claim it).

### D. Quality floors (per job, added 2026-11-01)
A run can be clean by every code above and still under-deliver. On Sonnet 5.5, daily-intel got 75% cheaper by searching a third as much and shipping 1–3 items (2026-10-26..30); a person noticed, nothing measured it. `scripts/quality.py` measures each run of a listed job from its transcript (subagents included, each call id once) and the files that run wrote, against floors quoted from that job's own SKILL.md. A run below one gets `QUALITY_FLOOR` (tracked, degraded), so recurrence, the island pill, `pair` and fix verification work as for any code. A failed run is judged by its root failure, not its floors.

| Job | Floors (from its SKILL.md) | Reported per model, never a floor |
|---|---|---|
| daily-intel | a briefing JSON written; WebSearch ≥ 2 × sections; every item has ≥ 1 source fetched (WebFetch URL = a source URL) | searches, fetches, items, source domains, deep dives |
| meeting-prep | a prep per meeting unless `needs` is `surface`, a surface per meeting once the launch prompt asks for one (an existing file the run read and kept counts); every task document opened (Read or Grep) or listed in the prep; ≤ 4 web calls | docs read vs only grepped, participants, talking points, `new_insight` |

- **Volume is never a floor.** A quiet news day may be short ("Never pad"). The report's **Quality** table shows each job's medians per model, so a model change shows up as a step in them; read it next to the model-swap test.
- **Run:** ingest measures new runs automatically. `forensics.py quality` backfills earlier runs while their transcripts last and prints the table.
- **Add a job:** one function in `quality.py` (`JOBS`), each floor quoted from the job's SKILL.md in its docstring. A floor the skill doesn't state is not a floor. Change the skill first, with the principal.
- **A floor that fires on most runs** is either prose the agent ignores (fix: a mechanism, step B) or a rule the skill should drop. That decision belongs to the principal, never to the measurement. *(meeting-prep 2026-11-01: 59 of 80 Sonnet 5.5 runs left task documents neither opened nor listed; strict "read the file" would flag 65.)*

## Optimizations/Gotchas
- **Rules before judges.** All codes are assigned by regex/fields. TRAIL found the best model locates only ~11% of trace errors — an LLM label is a hypothesis, not a classification. Output quality is first measured as effort floors and counts (section D). An LLM judge of the content itself comes only when those floors hold and quality still slips.
- **Degraded ≠ broken.** A degraded run usually still delivered; the cost is wasted turns and money and the risk of a silent workaround. The Job-health table flags only *failed* > 10% (14 d) as an error-budget breach (Google SRE error-budget policy).
- **Transcripts expire** (Claude Code cleans old sessions). Classification is persisted at run end for that reason; never rely on re-reading old transcripts.
- **The ledger stays append-only.** Forensics writes its own sidecar keyed by `session_id`; `run_agent.sh` additionally records `api_error_status`, `error` and `startup_failure_reason` for root-causing `INFRA`.
- `slack-fetch` writes its own ledger lines without `subtype`/`session_id` — classified on fields only (no transcript), which is why "no result" means no cost *and* no turns, not a missing `subtype`.
- **Verification is statistical, not proof.** `needs` assumes runs are independent at the pre-fix rate. Failures that cluster by input (one malformed mail, one meeting with a broken note) break that assumption: a fix can look verified while the next bad input is still coming. Read `after fix N/M` together with the traces, not instead of them.
- **A model change is a new configuration.** RiseHarness found that a harness evolved for one model scored below the untouched seed on another, so a verdict does not carry across models. When the `sonnet` alias moves (the fleet is on `claude-sonnet-5` as of 2026-10-22), every fixed issue on those jobs drops back to `fixing` until it is re-verified. That is intended.
- **The hook log starts 2026-10-22.** Older runs have no `hooks` summary. `after_block` (worked · tick-only · none) is computed at ingest because it needs the transcript, so a reclassification after the transcript has expired keeps the counts but leaves `after_block` unknown.

## Sources
- Cemri et al., *Why Do Multi-Agent LLM Systems Fail?* (MAST), arXiv:2503.13657 · Deshpande et al., *TRAIL*, arXiv:2505.08638 · *Where LLM Agents Fail and How They Can Learn from Failures* (AgentDebug), arXiv:2509.25370.
- *Agentic Harness Engineering* (falsifiable edit predictions), arXiv:2604.25850 · *Meta-Harness* (raw traces as feedback), arXiv:2603.28052 · ACE, arXiv:2510.04618.
- Wang et al., *Harness Self-Evolution for Long-Horizon Terminal Agents* (RiseHarness: flipping-run pairs, wish → revise against harness traces, precedent research, per-model adaptation, adoption only on a complete grid against a declared baseline), arXiv:2610.27435 · *Harness Handbook*, arXiv:2607.13285. Applied here: `output/20261022-riseharness-jarvis.md`.
- Hamel Husain, evals FAQ — error analysis (open → axial coding, first failure per trace): hamel.dev/blog/posts/evals-faq/ · Sentry event grouping: docs.sentry.io/concepts/data-management/event-grouping/ · Google SRE: postmortem culture, error budget policy (sre.google).
- Andrew Ng, *Improve Agentic Performance with Evals and Error Analysis* Parts 1–2, The Batch 2025-10-15/22 (vault: `output/ng-letters/letters/`).
- Claude Code headless output (`permission_denials`, `subtype`, `terminal_reason`): code.claude.com/docs/en/agent-sdk/typescript, code.claude.com/docs/en/headless.
