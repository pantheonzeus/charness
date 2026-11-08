# Add a headless job

A headless job is a skill that runs on a schedule with nobody watching. Because nobody can approve a prompt mid-run, the job's boundaries are fixed in advance and enforced by the harness.

## 1. Write the skill first

The job runs a skill. Write it ([guide](write-a-skill.md)) and run it interactively until its *Done when* holds reliably. A job only automates a skill that already works.

## 2. Create the agent file

`.claude/agents/<job>.md`:

```yaml
---
name: weekly-digest
description: Scheduled Friday digest agent. Runs the research/weekly-digest skill. Launched headless by scripts/run_agent.sh — not for interactive delegation.
model: claude-sonnet-5-5
effort: high
budget_usd: 2
untrusted_ingest: true          # set if it reads web, mail or chat
write_scopes:
  - "output/digest/????-??-??.md"
  - "output/.runs/????????-weekly-digest/*"
---
You are the scheduled weekly-digest agent. The Charter, Soul and skill library apply as in any session; this file only fixes your scope.

- **Owns:** one run of `resources/skills/research/weekly-digest/SKILL.md` for the date in the launch prompt.
- **Writes:** …
- **Never touches:** …
- **Success:** every checkpoint in the run's `RESPONSE.md` is `[x]`.
```

Rules of thumb:

- **Narrowest scopes that work.** Date-shaped globs (`????-??-??`) beat `*`. The job's scopes must stay inside the skill's `vault_writes:`.
- **Budget from observed runs.** Start tight, read the ledger, then adjust.
- **One plain Bash command per call.** A headless run can't answer a permission prompt, so a command outside the launch allowlist wastes the turn. The existing agent files spell out the headless shell rule; copy it.

## 3. Write the launcher

A small `scripts/run.sh` in the skill folder that calls the shared runner:

```bash
exec bash "$REPO_ROOT/scripts/run_agent.sh" weekly-digest "$SPINE" "$PROMPT" \
  --permission-mode acceptEdits --allowedTools "Read Write Edit WebSearch WebFetch"
```

`run_agent.sh` applies the model, budget and addendum, holds the writes to the scopes, snapshots the vault, and writes the ledger line.

## 4. Schedule it

Copy a reference plist from another skill's `schema/` folder, rename the label to `com.cbrain.<job>`, set the times and your paths, then:

```bash
cp resources/skills/research/weekly-digest/schema/com.cbrain.weekly-digest.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.cbrain.weekly-digest.plist
```

If the job depends on an employer's systems, list its label under `loops` in that employer pack instead, so it unloads when you leave.

## 5. Watch the ledger

```bash
tail -n 3 output/.runs/_ledger/weekly-digest.jsonl
scripts/agent_scorecard.sh
```

Run forensics classifies every degraded or failed run. If a failure code recurs, you get an issue with a proposed fix to approve.
