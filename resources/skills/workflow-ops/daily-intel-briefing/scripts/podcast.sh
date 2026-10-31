#!/usr/bin/env bash
# Briefing podcast for one date: a headless `claude -p` writes the two-host script
# (workflows/podcast-script.md), then podcast.py voices it on-device into output/briefings/<date>.mp3.
# Called by run.sh after each briefing and by the console's "Make podcast" button.
#
#   ./podcast.sh [YYYY-MM-DD]        default: today
#   ./podcast.sh --render-only DATE  re-voice an existing script, no LLM
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
unset ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN

RENDER_ONLY=0
[[ "${1:-}" == "--render-only" ]] && { RENDER_ONLY=1; shift; }
DAY="${1:-$(date +%Y-%m-%d)}"
cd "$REPO_ROOT"
[[ -f "output/briefings/$DAY.json" ]] || { echo "no briefing for $DAY"; exit 1; }

HELPER="resources/skills/workflow-ops/daily-intel-briefing/scripts/podcast.py"
if [[ $RENDER_ONLY == 0 ]]; then
  STAMP="${DAY//-/}"
  SPINE="$REPO_ROOT/output/.runs/$STAMP-briefing-podcast/RESPONSE.md"
  PROMPT="Follow resources/skills/workflow-ops/daily-intel-briefing/workflows/podcast-script.md for $DAY. Write output/briefings/$DAY.podcast.json, make 'uv run $HELPER check output/briefings/$DAY.podcast.json' print OK, and tick every checkpoint in output/.runs/$STAMP-briefing-podcast/RESPONSE.md before stopping."
  echo "[$(date '+%F %T')] briefing-podcast script start ($DAY)"
  bash "$REPO_ROOT/scripts/run_agent.sh" briefing-podcast "$SPINE" "$PROMPT" \
    --permission-mode acceptEdits --allowedTools Glob Grep WebFetch "Bash(uv run $HELPER:*)" "Bash(uv run $REPO_ROOT/$HELPER:*)"
fi
echo "[$(date '+%F %T')] briefing-podcast render ($DAY)"
uv run "$HELPER" render "$DAY"
# Refresh the reading page so it carries the new episode (reading-pages skill; mechanical).
python3 "$REPO_ROOT/resources/skills/workflow-ops/daily-intel-briefing/scripts/briefing.py" page "$DAY"
