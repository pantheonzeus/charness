#!/usr/bin/env bash
# launchd WatchPaths entrypoint — recomputes the 10 post-hoc viral metrics
# whenever cbrain/notes/LinkedIn-Posts/ changes (a new post, an analytics
# refresh done by hand in Obsidian, or an edit made from Claude). Unlike
# run.sh/the calibration skill's run.sh, this is a pure deterministic
# recompute (viral_metrics.py) — no `claude -p` call, no LLM cost, cheap
# enough to fire on every filesystem event.
#
# Install (see linkedin-viral-scheduler/SKILL.md for the full plist + a
# WatchPaths reliability caveat — it is NOT auto-installed by this script):
#   launchctl load ~/Library/LaunchAgents/com.cbrain.linkedin-viral-metrics-watch.plist
#   (installed 2026-08-22; every launchd label in this library is com.cbrain.*)
#
# Dry run (prints the resolved command, launches nothing):
#   ./watch_refresh.sh --dry-run

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# scripts/ -> linkedin-viral-scheduler/ -> workflow-ops/ -> skills/ -> resources/ -> repo root
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

if [[ "${1:-}" == "--dry-run" ]]; then
  echo "repo root : $REPO_ROOT"
  echo "would run : python3 '$SCRIPT_DIR/viral_metrics.py'"
  exit 0
fi

cd "$REPO_ROOT"
python3 "$SCRIPT_DIR/viral_metrics.py"

# Family B correlation revisit reminder (Charter §4 — no silent caps).
# viral-metrics.md documents that Save-Worthiness/Conversation-Trigger did NOT
# validate against their targets at n=19 and should be re-checked once the
# corpus grows past ~40 posts. Surface that as a standing log line instead of
# relying on anyone remembering a promise made in a report.
POSTS_DIR="$REPO_ROOT/cbrain/notes/LinkedIn-Posts"
N=$(find "$POSTS_DIR" -maxdepth 1 -name '[0-9]*.md' | wc -l | tr -d ' ')
if [[ "$N" -ge 40 ]]; then
  echo "REVISIT: corpus at $N posts (>=40) — re-run the Family B correlation check (references/viral-metrics.md, 'Family B did not validate' section)."
fi
