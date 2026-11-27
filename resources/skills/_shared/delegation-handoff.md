# Delegation & Handoff — shared module

Cross-skill procedure invoked by Charter §5. Any skill that hands work to a child agent (the Agent/Task tools, or a headless `claude -p` job) follows this contract.

*Source: the NLAH research (Pan et al., arXiv:2603.25723 v2, Table 4 and §5.2). Handoff is the paper's named main mechanism weakness: Information Handoff Recall fell from 1.00 under direct-context prompting to 0.32 (Live-SWE) and 0.55 (MHTBA) under the runtime's parent-child handoff. Files, not inline replies, are the fix.*

## Why file-backed
An inline reply from a child is lossy and unauditable: the parent paraphrases it back into its own context and detail is dropped. A file on disk is the durable carrier of record — the parent reopens exactly what the child wrote.

## The contract
1. **Task packet as a file.** Write the child's brief to `STATE_ROOT/children/<id>/TASK.md` — goal, inputs, the exact output file it must write, and the completion condition. The launch prompt points the child at this file; it reads its packet by path.
   - **Constraints travel verbatim.** The packet carries a `## Constraints` list: the child's write paths, the confidentiality deny-list (the client, account and person names or classes that must not leave, by name, never "keep it confidential"), the budget, and every never-do line that binds the work. Copy each from its source (skill, Charter, agent file, the principal's words), never paraphrase. *Why: handoffs keep facts and drop rules. In arXiv 2608.24569 (2026-08) summarised handoffs switched off workflow blockers in 76.7–97.2% of cases, and restoring the full blocker text took forbidden actions from 85.2% to 0.0%; arXiv 2608.29028 found boundary metadata collapses under compression while facts survive.* Check the packet with `python3 scripts/packet_lint.py task <children/<id>>` before launch.
2. **Declare the context mode.**
   - **fresh** (default for independent branches) — child starts clean and sees *only* its packet. Keeps boundaries clean; prevents unrelated context leaking in and skewing the work.
   - **forked** — child inherits the parent's accumulated context. Use only when the child genuinely needs the running history.
3. **Result written back.** The child writes its deliverable/answer to `STATE_ROOT/children/<id>/RESPONSE.md` (plus any artifacts it was told to produce). Its inline reply is a status line, not the payload. The file ends with `## Constraints checked`: every packet constraint copied verbatim, then ` — kept`, ` — not applicable` or ` — broken: <why>`.
4. **Parent reopens before integrating.** The parent reads `RESPONSE.md` from disk — never trusts the inline reply as the source of truth — runs `python3 scripts/packet_lint.py check <children/<id>>` (exit 1: a constraint not echoed, resume the child to answer it; exit 2: a constraint broken, act on it before integrating), then integrates. A clean final answer can hide a damaged handoff, so the echo is checked, not assumed.
   - **One level deep is mechanical** (`.claude/hooks/nesting-guard.sh`, 2026-11-27): a child cannot start its own subagents. **Unscoped children don't write shared state** (`write-boundary.sh`): a subagent type without `write_scopes:` (general-purpose, Explore, a fork) may not write the vault, `.claude/`, the core docs, `employers/` or the memory dir. Hand such work to the domain agent whose scopes cover it, or have the child return it in `RESPONSE.md`.
5. **Parent stays orchestrator.** Once delegated, the parent narrates launches / waits / integration and leaves substantive work in the child. Add child agents only when delegation genuinely improves coverage, latency, specialist focus, or keeps large intermediate data (big JSON, transcripts) out of the main context.

## Existing users
All declare `modules: [file-backed-handoff]`; each names its packet and result path in its SKILL.md.
- `workflow-ops/notebooklm-daily-audio` — headless distill job. Packet = `workflows/distill-to-vault.md`; result `output/.runs/<YYYYMMDD>-nlm-distill/children/distill/RESPONSE.md`, reopened by `distill_to_vault.sh`.
- `workflow-ops/meeting-prep-loop` — change-driven enrichment job. Packet = `TASK.json` + seeded `RESPONSE.md` spine written by `scripts/sync.py`; result `output/.runs/<YYYYMMDD-HHMM>-meeting-prep/RESPONSE.md`, reopened by `scripts/run_agent.sh`. (Replaced `workflow-ops/morning-briefing`, retired 2026-10-23.)
- `workflow-ops/mail-to-conversations` — bulk-fetch subagent, `output/.runs/<YYYYMMDD>-mail-import/children/fetch/`.
- `content/linkedin-profile-headhunter` — cheap playbook-query sub-agent, `output/.runs/<YYYYMMDD>-headhunter/children/playbook-refresh/`.
- `sales/competitive-porter-teardown` — per-BU fan-out via task-packet files.
- `workflow-ops/linkedin-viral-scheduler` — 3 fresh blind judges via `STATE_ROOT/children/judge-<n>/{TASK.md,RESPONSE.md}`.
- `workflow-ops/linkedin-scoring-calibration` — headless `claude -p` run; packet = `workflows/headless-calibration.md`.

For a **headless `claude -p` job** the versioned workflow file *is* the task packet (fixed, reviewable in git) and the shell wrapper is the parent: it reopens the child's `RESPONSE.md` into the job log and warns when it is missing. Child result files sit under `children/`, so the Stop control-spine gate (which reads only top-level `RESPONSE.md`) never blocks on them.
