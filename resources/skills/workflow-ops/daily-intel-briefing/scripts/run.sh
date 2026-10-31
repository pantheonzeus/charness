#!/usr/bin/env bash
# Entrypoint for the daily-intel-briefing skill — launchd (com.cbrain.daily-intel-briefing,
# weekdays 06:30) and the web console's "Run now" button both call this.
# Resolves its own path, sets PATH, and drives one headless `claude -p` run through
# scripts/run_agent.sh, so every run lands in output/.runs/_ledger/daily-intel.jsonl.
# Then learn_podcasts.py (NotebookLM, one 5-10 min deep dive per topic) and podcast.sh
# (the two-host Kokoro episode) run side by side.
#
# Dry run (prints the resolved command, launches nothing):  ./run.sh --dry-run
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# scripts/ -> daily-intel-briefing/ -> workflow-ops/ -> skills/ -> resources/ -> repo root
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
# Subscription, not API: never let a stray key redirect billing.
unset ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN

DAY="$(date +%Y-%m-%d)"
SPINE="$REPO_ROOT/output/.runs/$(date +%Y%m%d)-daily-intel/RESPONSE.md"
PROMPT="Read and follow resources/skills/workflow-ops/daily-intel-briefing/SKILL.md (a repo skill: open it with Read, not the Skill tool) end-to-end for $DAY. Write output/briefings/$DAY.json and its deep-dive pages, make scripts/briefing.py check print OK, and tick every checkpoint in output/.runs/$(date +%Y%m%d)-daily-intel/RESPONSE.md before stopping."
HELPER="resources/skills/workflow-ops/daily-intel-briefing/scripts/briefing.py"
PAGE="resources/skills/workflow-ops/reading-pages/scripts/page.py"
TOOLS=(Glob Grep WebSearch WebFetch "Bash(python3 $HELPER:*)" "Bash(python3 $REPO_ROOT/$HELPER:*)" "Bash(uv run $PAGE check:*)")

if [[ "${1:-}" == "--dry-run" ]]; then
  echo "repo root : $REPO_ROOT"
  echo "would run : scripts/run_agent.sh daily-intel $SPINE \"$PROMPT\" --permission-mode acceptEdits --allowedTools ${TOOLS[*]}"
  exit 0
fi

cd "$REPO_ROOT"
mkdir -p output/briefings
echo "[$(date '+%F %T')] daily-intel-briefing start ($DAY)"
bash "$REPO_ROOT/scripts/run_agent.sh" daily-intel "$SPINE" "$PROMPT" \
  --permission-mode acceptEdits --allowedTools "${TOOLS[@]}"
# The podcast follows the briefing. Its failure never fails the briefing run.
# The reading page (reading-pages skill) from the JSON: mechanical, no agent. podcast.sh refreshes it with the episode.
[[ -f "output/briefings/$DAY.json" ]] && { python3 "$SCRIPT_DIR/briefing.py" page "$DAY" || echo "[$(date '+%F %T')] briefing page failed (briefing itself is fine)"; }
# NotebookLM generates server-side, so it runs alongside the local podcast. Neither failure fails the briefing.
python3 "$SCRIPT_DIR/learn_podcasts.py" "$DAY" &
LEARN=$!
bash "$SCRIPT_DIR/podcast.sh" "$DAY" || echo "[$(date '+%F %T')] briefing-podcast failed (briefing itself is fine)"
wait "$LEARN" || echo "[$(date '+%F %T')] learning podcasts incomplete (re-run: python3 $SCRIPT_DIR/learn_podcasts.py $DAY)"
[[ -f "output/briefings/$DAY.json" ]] && python3 "$SCRIPT_DIR/briefing.py" page "$DAY" || true
