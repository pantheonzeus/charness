#!/usr/bin/env bash
# Headless entrypoint for the linkedin-scoring-calibration skill.
# Runs the whole calibration end-to-end unattended: build dataset -> judge
# substance (incremental) -> label/split -> autoresearch tuning loop ->
# deterministic report + history + (gated) live-scorer update.
#
# launchd-safe / cron-safe: resolves its own path (the scheduler's cwd/env is
# minimal), sets PATH, cd's to the repo root, and drives one headless
# `claude -p` session through the skill's workflow.
#
# Install (weekly, launchd) — see SKILL.md §Headless for the full .plist.
# Crontab alternative (Mondays 08:00 local):
#   0 8 * * 1 <REPO>/resources/skills/workflow-ops/linkedin-scoring-calibration/scripts/run.sh >> <REPO>/output/linkedin-scoring-calibration.log 2>&1
#
# Dry run (prints the resolved command, launches nothing):
#   ./run.sh --dry-run

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# scripts/ -> linkedin-scoring-calibration/ -> workflow-ops/ -> skills/ -> resources/ -> repo root
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

DATE="${1:-$(date +%Y-%m-%d)}"
[[ "$DATE" == "--dry-run" ]] && DATE="$(date +%Y-%m-%d)"

PROMPT="Run the workflow-ops/linkedin-scoring-calibration headless-calibration workflow for ${DATE}. Follow resources/skills/workflow-ops/linkedin-scoring-calibration/workflows/headless-calibration.md exactly. Tick every control-spine checkpoint before stopping."

# --dangerously-skip-permissions is REQUIRED for a genuinely unattended run:
# a launchd/cron job cannot answer permission prompts, and --permission-mode
# acceptEdits auto-approves file edits but NOT `python3`/`cp`/`printf` execution
# — this whole pipeline is Python-driven, so acceptEdits alone stalls it at CP0.
# Scope stays bounded: the workflow only runs the skill's own scripts inside the
# repo, appends to output/, and performs NO git operations.
if [[ "${1:-}" == "--dry-run" ]]; then
  echo "repo root : $REPO_ROOT"
  echo "date      : $DATE"
  echo "would run : cd '$REPO_ROOT' && claude -p \"$PROMPT\" --dangerously-skip-permissions"
  exit 0
fi

echo "[$(date '+%F %T')] linkedin-scoring-calibration: starting headless run for $DATE"
cd "$REPO_ROOT"
exec claude -p "$PROMPT" --dangerously-skip-permissions
