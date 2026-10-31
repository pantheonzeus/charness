#!/usr/bin/env bash
# Headless driver for the notebooklm-daily-audio `distill-to-vault` workflow.
# Runs AFTER daily_audio.py (which writes output/podcasts/<date>-*.summary.md).
# Reads today's fresh summaries and, via a headless `claude` run, distills each
# into a linked topic note in the vault. Scheduled by launchd at 18:30
# (com.cbrain.notebooklm-distill-vault), or run by hand. Idempotent: skips distillation when there's nothing new — but the
# link_audit enforcement sweep at the tail runs every invocation regardless, so
# link islands are caught daily even on days with no new notebooks.
set -euo pipefail

# Repo root, resolved from this script's own location so launchd's cwd doesn't matter:
# <repo>/resources/skills/workflow-ops/notebooklm-daily-audio/scripts/distill_to_vault.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"

DATE="${1:-$(date +%Y-%m-%d)}"
DATE_COMPACT="${DATE//-/}"
PODCAST_DIR="$REPO_ROOT/output/podcasts"

cd "$REPO_ROOT"

# Only proceed if there is at least one summary file for the date. `distilled: true`
# filtering is the workflow's job; this is just the cheap "any work at all?" gate.
shopt -s nullglob
summaries=("$PODCAST_DIR/${DATE_COMPACT}-"*.summary.md)
if [ ${#summaries[@]} -eq 0 ]; then
  echo "[$(date '+%F %T')] No summary files for $DATE — nothing to distill (link_audit sweep still runs below)."
else
  echo "[$(date '+%F %T')] Distilling ${#summaries[@]} summary file(s) for $DATE …"
  # --permission-mode acceptEdits: unattended file edits, held to the write_scopes in
  # .claude/agents/nlm-distill.md by the write-boundary hook; the workflow's guardrails keep
  # it append-only. Bash is allowed only for the workflow's link_audit gate (Step 3).
  # scripts/run_agent.sh runs claude, reopens the child's result file (Charter §5 — the
  # file, not the inline reply, is the record) and appends the run to the job ledger.
  HANDOFF="$REPO_ROOT/output/.runs/${DATE_COMPACT}-nlm-distill/children/distill/RESPONSE.md"
  LINK_AUDIT="resources/skills/research/notebooklm/scripts/link_audit.sh"
  bash "$REPO_ROOT/scripts/run_agent.sh" nlm-distill "$HANDOFF" \
    "Run the notebooklm-daily-audio distill-to-vault workflow for $DATE. \
Follow resources/skills/workflow-ops/notebooklm-daily-audio/workflows/distill-to-vault.md exactly." \
    --permission-mode acceptEdits --allowedTools "Bash($LINK_AUDIT:*)" "Bash(bash $LINK_AUDIT:*)"
  echo "[$(date '+%F %T')] Distill run complete."
fi

# --- Knowledge-graph enforcement sweep --------------------------------------
# The vault is git-ignored, so no pre-commit hook can guard it. This scheduled
# sweep is the daily backstop: link_audit over every synced notebook catches link
# islands introduced anywhere (manual imports, hand edits) that the write-time
# workflow gates missed. Advisory only — it never edits notes, just logs + flags
# in the daily report so drift is reviewable the next morning. (bash 3.2-safe.)
AUDIT="$REPO_ROOT/resources/skills/research/notebooklm/scripts/link_audit.sh"
DAILY="$REPO_ROOT/cbrain/daily reports/${DATE_COMPACT}.md"
SWEEP_SLUGS="$(find "$REPO_ROOT/cbrain/notes/NotebookLM" -maxdepth 2 -type d -name Sources 2>/dev/null \
  | sed -E 's@.*/notes/NotebookLM/([^/]+)/Sources@\1@' | sort -u)"

if [ -n "$SWEEP_SLUGS" ]; then
  sweep_fail=0; audited=0
  # Per-slug loop via here-string — no dependence on unquoted word-splitting (differs bash/zsh).
  while IFS= read -r slug; do
    [ -z "$slug" ] && continue
    audited=$((audited + 1))
    bash "$AUDIT" "$slug" || sweep_fail=1
  done <<< "$SWEEP_SLUGS"
  if [ "$sweep_fail" -eq 0 ]; then
    echo "[$(date '+%F %T')] link_audit sweep: $audited notebook(s) — all wired (no islands)."
  else
    echo "[$(date '+%F %T')] link_audit sweep: $audited notebook(s) — ISLANDS FOUND (see output above)."
    if [ -f "$DAILY" ]; then
      printf '\n> [!warning] link_audit found unlinked notebook source note(s) at %s. Wire them to a topic anchor (see notebooklm/workflows/import.md Step 7), then re-run `link_audit.sh <slug>`.\n' "$(date '+%F %T')" >> "$DAILY"
    fi
  fi
fi
