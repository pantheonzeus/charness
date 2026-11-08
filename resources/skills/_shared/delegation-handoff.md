# Delegation & Handoff — shared module

Cross-skill procedure invoked by Charter §5. Any skill that hands work to a child agent (the Agent/Task tools, or a headless `claude -p` job) follows this contract.

*Source: the NLAH research (Pan et al., arXiv:2603.25723, Tables 4 & E.1). Parent→child handoff is the single documented failure point of natural-language orchestration — Information Handoff Recall fell to 0.32–0.55 under naive delegation. Files, not inline replies, are the fix.*

## Why file-backed
An inline reply from a child is lossy and unauditable: the parent paraphrases it back into its own context and detail is dropped. A file on disk is the durable carrier of record — the parent reopens exactly what the child wrote.

## The contract
1. **Task packet as a file.** Write the child's brief to `STATE_ROOT/children/<id>/TASK.md` — goal, inputs, the exact output file it must write, and the completion condition. The launch prompt points the child at this file; it reads its packet by path.
2. **Declare the context mode.**
   - **fresh** (default for independent branches) — child starts clean and sees *only* its packet. Keeps boundaries clean; prevents unrelated context leaking in and skewing the work.
   - **forked** — child inherits the parent's accumulated context. Use only when the child genuinely needs the running history.
3. **Result written back.** The child writes its deliverable/answer to `STATE_ROOT/children/<id>/RESPONSE.md` (plus any artifacts it was told to produce). Its inline reply is a status line, not the payload.
4. **Parent reopens before integrating.** The parent reads `RESPONSE.md` from disk — never trusts the inline reply as the source of truth — then integrates.
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
