#!/usr/bin/env bash
# Cron entrypoint for the linkedin-viral-scheduler skill.
# Cron-safe: resolves its own path (cron's cwd/env is minimal), sets PATH, cd's to
# the repo root, and drives a headless `claude -p` run through the skill end-to-end.
#
# Install (crontab -e), Tue/Thu 09:00 local:
#   0 9 * * 2,4 <REPO>/resources/skills/workflow-ops/linkedin-viral-scheduler/scripts/run.sh >> <REPO>/output/linkedin-viral-scheduler.log 2>&1
#
# Dry run (prints the resolved command, launches nothing):
#   ./run.sh --dry-run

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# scripts/ -> linkedin-viral-scheduler/ -> workflow-ops/ -> skills/ -> resources/ -> repo root
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

# Prompt refreshed 2026-08-22: the previous text still named "the 7 topics", a
# 12-iteration budget and the retired M1-M4 `total_score >= 18` rubric — none of
# which the skill has used since the joint spine and the three-gate rubric landed.
# A stale prompt here silently drafts against retired rules, so keep it in sync
# with SKILL.md §1/§3 whenever either changes.
PROMPT='Read and follow resources/skills/workflow-ops/linkedin-viral-scheduler/SKILL.md (a repo skill: open it with Read, not the Skill tool) end-to-end. Pick the joint the recency guard permits (references/ladder-joints.md via the storytelling skill; history.tsv carries joint+dialect) and name its dialect. CRITICAL: confirm a real lived moment exists behind the pick — if none does, write no post, log "no moment, no post" with what moment-generating activity is next, tick the control spine and stop. That is a correct outcome, not a failure. Otherwise draft, then run the three-gate loop on a 4-iteration budget: blind-judged Substance (M1+M3 >= 9), blind-judged Audience Pull (P1+P2 >= 8), deterministic Pre-Publish Audit (composite >= 85). Then apply the methodology check: if the draft reads as a framework presentation rather than an operating story, rewrite it regardless of score. Finalize output/linkedin/latest.md and append the history.tsv row. Tick every control-spine checkpoint before stopping.'
# run-forensics PERM_BLOCKED, flagged 2026-10-22 (CHANGE_LOG "Harness-side trace" entry,
# risk (d)): this launcher set no --allowedTools, unlike daily-intel-briefing/vault-frontier-loop —
# 30 PERM_BLOCKED hits in 4 runs, headless mode can't grant the approval. The skill's own prose
# (SKILL.md "Hygiene guard" / "Audit" steps) tells the agent to run exactly these two helpers;
# pre-approve them the same way daily-intel's run.sh does, so the common case never needs approval.
HYGIENE="resources/skills/workflow-ops/linkedin-viral-scheduler/scripts/hygiene_check.sh"
AUDIT="resources/skills/workflow-ops/linkedin-viral-scheduler/scripts/prepublish_audit.py"
# The outbound gate (public mode) is the Finalize step's confidentiality check (G1b, 2026-10-23).
GATE="scripts/outbound_gate.py"
TOOLS=("Bash($HYGIENE:*)" "Bash($REPO_ROOT/$HYGIENE:*)" "Bash(python3 $AUDIT:*)" "Bash(python3 $REPO_ROOT/$AUDIT:*)"
       "Bash(python3 $GATE:*)" "Bash(python3 $REPO_ROOT/$GATE:*)")

if [[ "${1:-}" == "--dry-run" ]]; then
  echo "repo root : $REPO_ROOT"
  echo "would run : cd '$REPO_ROOT' && scripts/run_agent.sh linkedin-viral - \"$PROMPT\" --permission-mode acceptEdits --allowedTools ${TOOLS[*]}"
  exit 0
fi

cd "$REPO_ROOT"
# scripts/run_agent.sh runs claude and appends the run to the job ledger (cost, turns, outcome).
exec bash "$REPO_ROOT/scripts/run_agent.sh" linkedin-viral - "$PROMPT" --permission-mode acceptEdits --allowedTools "${TOOLS[@]}"
