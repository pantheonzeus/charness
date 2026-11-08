#!/usr/bin/env bash
# Entrypoint for the vault-frontier-loop skill: launchd (com.cbrain.vault-frontier-loop, weekdays 05:45)
# or by hand. One headless `claude -p` run through scripts/run_agent.sh, so every run lands in
# output/.runs/_ledger/vault-frontier.jsonl.
#
# Dry run (prints the resolved command, launches nothing):  ./run.sh --dry-run
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# scripts/ -> vault-frontier-loop/ -> research/ -> skills/ -> resources/ -> repo root
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
# Subscription, not API: never let a stray key redirect billing.
unset ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN

DAY="$(date +%Y-%m-%d)"
SPINE="$REPO_ROOT/output/.runs/$(date +%Y%m%d)-vault-frontier/RESPONSE.md"
HELPER="resources/skills/research/vault-frontier-loop/scripts/frontier.py"
PROMPT="Read and follow resources/skills/research/vault-frontier-loop/SKILL.md (a repo skill: open it with Read, not the Skill tool) for $DAY. Start with python3 $HELPER pick. Write output/frontier/$DAY.json, make python3 $HELPER check print OK, and tick every checkpoint in output/.runs/$(date +%Y%m%d)-vault-frontier/RESPONSE.md before stopping."
TOOLS=(WebSearch WebFetch Read Glob Grep Write Edit "Bash(python3 $HELPER:*)" "Bash(python3 $REPO_ROOT/$HELPER:*)" "Bash(date:*)")

if [[ "${1:-}" == "--dry-run" ]]; then
  echo "repo root : $REPO_ROOT"
  echo "would run : scripts/run_agent.sh vault-frontier $SPINE \"$PROMPT\" --permission-mode acceptEdits --allowedTools ${TOOLS[*]}"
  python3 "$REPO_ROOT/$HELPER" pick
  exit 0
fi

cd "$REPO_ROOT"
mkdir -p output/frontier "$(dirname "$SPINE")"
echo "[$(date '+%F %T')] vault-frontier-loop start ($DAY)"
exec bash "$REPO_ROOT/scripts/run_agent.sh" vault-frontier "$SPINE" "$PROMPT" \
  --permission-mode acceptEdits --allowedTools "${TOOLS[@]}"
