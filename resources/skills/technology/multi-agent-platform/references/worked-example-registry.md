# Worked example — registry entries and ledger-set budget caps for a 19-job estate

Use this when someone asks what "register before code" (principle 10) and "budget per agent" look like in practice, or as a pattern for their own registry. It's from this harness on 2026-11-09: one person, 19 headless jobs started by launchd through one runner, every run logged to a per-job JSONL ledger. Code: `scripts/agent_registry.py` (check + budgets report), wired into `scripts/check.sh`. The figures are direct observations from that ledger; re-derive them for any other estate.

## The registry entry is the agent file

Each job's `.claude/agents/<job>.md` frontmatter already held what it runs on, what it may spend and where it may write. Five keys turned it into a registry entry:

```yaml
model: claude-sonnet-5-5
budget_usd: 1            # runaway guard per run, not a target (formula below)
write_scopes:            # hook-enforced: the job writes nowhere else
  - "output/mail-triage/triage/*.json"
lane: B                  # A gated process · B bounded loop · C research
level: L1                # L0 sandbox · L1 advisory · L2 decision-supporting
owner: principal         # the human who answers for its output
stop_when: "the mail stops reaching this inbox, or drafts are rewritten more often than sent as written"
evals: ["triage.py check", "scripts/spotcheck.py"]
```

`agent_registry.py check` fails CI when a key is missing, a lane or level is outside its set, `evals` is empty, or a lane-C job claims L2. A job built in a parallel session at the same time has no entry yet, so the check will fail it at merge until it gets one. That's the point: agent twenty can't arrive unregistered.

## What placement produced

| Lane | Jobs | Shape |
|---|---|---|
| A | 0 | — |
| B | 7 | deterministic wrapper (poll/sync) → one headless agent run under a budget → a `check` script re-verifies the output (mail triage, meeting prep, briefing podcast, distill-to-vault, idea engine, …) |
| C | 12 | open-ended research against outside sources (daily intel, vault frontier, client news, newsletter watchers, console researchers, upgrade scout) |

- **Lane A is empty, and that is correct for a one-person estate.** No job commits money or excludes a counterparty on its own. The human gate sits at the boundary instead: a send gate allows a mail out only after an explicit yes, and only the principal can mark a note `confirmed:`. In a company estate the same jobs often move to A, because the output is defended externally.
- **Every job is L1.** L2 needs a passing golden-run suite per job, and none had one. Writing L2 anyway is the drift the level exists to stop. Promotion is a reviewed diff with a named approver.
- **`stop_when` is the owner's call.** The agent drafted all 19 for the owner to correct. A kill criterion the owner never read is not one.

## The caps formula

```
cap = round_up_to_0.50( max( p95 × 1.5,  largest run × 1.25,  $1 ) )
```

- **Count only runs on the job's pinned model.** Mixing models skews p95 badly: mail triage's p95 was $0.63 over all history and $0.29 on the current model.
- **Wait for at least 6 runs on that model.** With fewer, keep the guess and say so.
- **Report, never auto-apply.** A cap the owner set by hand stays theirs. In this estate, one job's $3 cap was the owner's explicit call.
- **Only tighten.** If the formula comes out above the current cap and nothing has hit that cap, keep the current one.
- **Why the max floor.** p95 by definition leaves 1 run in 20 above it. The floor guarantees no past run would have been cut, which makes the change safe to ship without a trial period.

Result (9 of 19 caps changed; the others had < 6 runs on their model, an owner-set cap, or a formula above the current cap):

| Job | Before | After | Runs | p95 | Largest |
|---|---|---|---|---|---|
| daily intel | $15 | $4 | 12 | $2.55 | $2.55 |
| client news | $6 | $2.50 | 61 | $1.62 | $1.91 |
| console researcher | $5 | $2.50 | 165 | $1.31 | $1.88 |
| harness upgrader | $6 | $3.50 | 10 | $2.19 | $2.19 |
| briefing podcast | $4 | $2 | 12 | $1.06 | $1.06 |
| meeting prep | $3 | $2 | 156 | $1.09 | $1.39 |
| idea engine | $2 | $1 | 102 | $0.59 | $0.66 |
| mail triage | $2 | $1 | 49 | $0.29 | $0.32 |

The guesses were 2–4× too loose. A runaway loop was therefore caught at 2–4× the cost it should have been.

## Gotchas met on the way

- **Find every reader of the file before adding keys.** Here a shell hook (awk), a Python writer (regex) and the CLI all parse the same frontmatter. New keys went after the `write_scopes:` list, behind a comment line, so no parser could take them for scope entries. Check that the new keys parse as YAML on their own. One description line in this estate was already invalid strict YAML and was left alone.
- **The research firewall in the same estate.** Meeting prep's `check` refuses a web-sourced participant note that isn't labelled `External (<source>, <date>):`, and a `new_insight` whose URL the harvest never offered.
  - Run against all 105 existing preps, it flagged 5 notes, all genuinely web-derived, and 0 of 26 insights.
  - The first version measured the 7-day window from today rather than from the prep's `enriched_at`, and flagged 15 valid insights. Anchor any time window to when the output was made.
- **Measure the human gate too.** Approvals are recorded with the seconds on screen and whether a draft was edited, and a weekly blind sheet re-asks five decisions. An L1 estate is only as good as the reading its owner actually does.
