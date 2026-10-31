#!/usr/bin/env bash
# Headless driver for the morning-briefing `build-briefing` workflow.
# Scheduled by launchd on weekday mornings (~06:33), or run by hand.
# Imports today's calendar + new mail, preps each meeting, builds the HTML,
# then opens it in the default browser so it's waiting when the laptop unlocks.
# Idempotent: re-running the same day never duplicates notes/contacts/mail.
set -euo pipefail

# Retired 2026-10-23: superseded by meeting-prep-loop on 2026-10-11, never scheduled since, and its
# headless agent definition (.claude/agents/morning-briefing.md) was removed. Kept as the record.
echo "morning-briefing is retired (superseded by workflow-ops/meeting-prep-loop); nothing was run." >&2
exit 1

# Repo root, resolved from this script's own location so launchd's cwd doesn't matter:
# <repo>/resources/skills/workflow-ops/morning-briefing/scripts/run_morning_briefing.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"

DATE="${1:-$(date +%Y-%m-%d)}"
DATE_COMPACT="${DATE//-/}"
HTML="$REPO_ROOT/output/morning-briefing/${DATE_COMPACT}.html"

cd "$REPO_ROOT"

echo "[$(date '+%F %T')] Building morning briefing for $DATE …"

# --permission-mode acceptEdits: unattended vault edits. Scope stays inside the repo
# (cwd) and the workflow's guardrails keep it append-only / existing-entities-only.
# scripts/run_agent.sh runs claude, reopens the child's result file (Charter §5 — the
# file, not the inline reply, is the record) and appends the run to the job ledger.
HANDOFF="$REPO_ROOT/output/.runs/${DATE_COMPACT}-morning-briefing/children/build/RESPONSE.md"
bash "$REPO_ROOT/scripts/run_agent.sh" morning-briefing "$HANDOFF" \
  "Run the morning-briefing build-briefing workflow for $DATE. \
Follow resources/skills/workflow-ops/morning-briefing/workflows/build-briefing.md exactly." \
  --permission-mode acceptEdits

# The workflow's final step builds the HTML; if the headless run couldn't (e.g. no
# meetings / MCP down), build a page anyway from whatever is on disk so something opens.
if [ ! -f "$HTML" ]; then
  echo "[$(date '+%F %T')] HTML missing — building from on-disk notes as a fallback."
  python3 "$REPO_ROOT/resources/skills/workflow-ops/morning-briefing/scripts/build_briefing_html.py" \
    --date "$DATE_COMPACT" || true
fi

if [ -f "$HTML" ]; then
  echo "[$(date '+%F %T')] Opening $HTML"
  open "$HTML"
else
  echo "[$(date '+%F %T')] No HTML to open."
fi
echo "[$(date '+%F %T')] Morning briefing run complete."
