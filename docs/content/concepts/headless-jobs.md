# Headless jobs

The scheduled agents (briefings, mail triage, meeting prep, research loops) run without anyone watching. Every one of the {{ jobs_count }} jobs goes through the same runner, under the same rules.

## One agent file per job

Each job is defined once in [`.claude/agents/<job>.md`](gh:.claude/agents/):

```yaml
---
name: vault-frontier
description: Scheduled weekday vault-expansion agent…
model: claude-sonnet-5-5   # pinned; changes only after the regression suite passes on the candidate
effort: high
budget_usd: 3              # hard cap per run
untrusted_ingest: true     # its input is outside text: every vault note it writes gets labelled
write_scopes:              # hook-enforced: Write/Edit only inside these
  - "output/frontier/????-??-??.json"
  - "cbrain/projects/*.md"
  - "output/.runs/????????-vault-frontier/*"
---
You are the scheduled vault-frontier agent. …
```

The body says what the job owns, what it writes, what it never touches, and what success looks like.

## One runner for every job

[`scripts/run_agent.sh`](gh:scripts/run_agent.sh) wraps a single `claude -p` call, so every job is measured the same way:

1. Applies the agent file: model, effort, `--max-budget-usd`.
2. Appends the model family's prompt addendum from [`resources/models/`](gh:resources/models/README.md). These are Anthropic's tested fixes for that model, copied word for word.
3. Exports `CBRAIN_JOB`, so the write guard holds the run to its `write_scopes`.
4. Snapshots the vault before and after, into the private vault history.
5. Reopens the job's handoff `RESPONSE.md`. The file is the record, not the reply.
6. Appends cost, turns, duration and outcome to `output/.runs/_ledger/<job>.jsonl`, and classifies the run as clean, degraded or failed, with a failure code read from the transcript.

A circuit breaker stops all jobs after three API-pressure failures. `scripts/agent_scorecard.sh` summarizes the ledger per job: success rate, yield, cost per productive run.

## Scheduling

Jobs run as `com.cbrain.*` launchd agents. Each loop ships a reference plist in its skill's `schema/` folder. Replace the placeholder home-directory paths with your own and load it with `launchctl`. Loops tied to an employer's systems are declared in its pack and loaded together: `python3 scripts/employer.py loops --load --apply`.

Most loops are split into a cheap trigger and a costly agent. A deterministic poll runs often and costs nothing; the agent wakes only when there is something new.

## Code-mode and sandboxing

Bash-run writes never pass the write hook, so they get the vault by one of two paths only:

- **`scripts/vault_api.py`**, a typed, all-or-nothing batch writer that enforces the same scopes and provenance rules in its own code;
- **none at all.** A job whose agent file says `code_mode: true` (it runs code it wrote) is sandboxed at OS level, with the vault and the harness denied for writing.

## Failure forensics

`workflow-ops/run-forensics` classifies each failed or degraded run against a closed taxonomy, opens an issue when a failure code recurs, and closes the loop with a human-approved fix. The fix is verified over a window scaled to the code's pre-fix rate. [Evaluation →](../governance/evaluation.md)

[Add your own job →](../guides/add-a-headless-job.md)
