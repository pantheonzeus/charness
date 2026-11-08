#!/usr/bin/env bash
# Stop control-spine gate — the un-bypassable half of Charter §4 file-backed-state discipline.
# Blocks the run from stopping while any STATE_ROOT control spine (output/.runs/*/RESPONSE.md)
# still has unchecked `[ ]` checkpoints. Deterministic acceptance-gate enforcement: a declared
# checkpoint that was never cleared means the run is not actually done.
#
# Scope is deliberately narrow (paper F.1: don't add process that doesn't tighten acceptance).
# It only fires when a run explicitly opted into a control spine.
#
# FAIL-OPEN by design (like write-boundary.sh): no runs dir, no unchecked boxes, or any parse
# error → allow the stop (exit 0). Never loops: if this Stop was already triggered by our own
# block (stop_hook_active), we defer. Each block, and each release after one, is logged to
# output/.runs/_forensics/hooks.jsonl for workflow-ops/run-forensics.
set -uo pipefail

REPO="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
RUNS="$REPO/output/.runs"

# Nothing to police.
[ -d "$RUNS" ] || exit 0

input="$(cat 2>/dev/null || true)"
active="$(printf '%s' "$input" | jq -r '.stop_hook_active // false' 2>/dev/null || echo false)"

# Harness trace for run-forensics: one line per block, and per release of a stop that followed a
# block (did the block get the boxes cleared?), joined to the run by session_id. Best effort.
log_decision() {   # $1 = block|release, $2 = newline list of this session's run dirs still open
  local log="$REPO/output/.runs/_forensics/hooks.jsonl"
  mkdir -p "$(dirname "$log")" 2>/dev/null
  printf '%s' "$input" | jq -c --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg d "$1" --arg open "$2" \
    '{ts: $ts, session_id: (.session_id // null), hook: "control-spine-gate", decision: $d,
      runs: ($open | split("\n") | map(select(. != "")))}' >> "$log" 2>/dev/null || true
}

# Top-level control spines (not child handoff files) with at least one unchecked checkpoint.
incomplete="$(grep -lF '[ ]' "$RUNS"/*/RESPONSE.md 2>/dev/null || true)"

# Scope to this session's own runs: a spine counts only if this session's tool calls named
# its run dir. Without this, one open run blocks every other session — and a headless job
# under acceptEdits would tick (or delete) another run's checkpoints to get past the gate.
# No readable transcript → keep the old all-runs check rather than lose enforcement.
transcript="$(printf '%s' "$input" | jq -r '.transcript_path // empty' 2>/dev/null || true)"
if [ -n "$incomplete" ] && [ -n "$transcript" ] && [ -r "$transcript" ]; then
  calls="$(jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") | .input | tostring' \
    "$transcript" 2>/dev/null || true)"
  own=""
  while IFS= read -r spine; do
    [ -z "$spine" ] && continue
    run="$(basename "$(dirname "$spine")")"
    printf '%s' "$calls" | grep -qF "$run" && own="$own$spine"$'\n'
  done <<< "$incomplete"
  incomplete="$(printf '%s' "$own" | sed '/^$/d')"
fi
open="$(printf '%s\n' "$incomplete" | sed '/^$/d' | sed "s#$RUNS/##; s#/RESPONSE.md##")"

# Anti-loop: never block twice in the same stop cycle. This stop follows our own block.
if [ "$active" = "true" ]; then
  log_decision release "$open"
  exit 0
fi
[ -z "$incomplete" ] && exit 0

# Offending run dirs, relative to the runs root.
dirs="$(printf '%s\n' "$incomplete" | sed "s#$RUNS/##; s#/RESPONSE.md##" | paste -sd', ' - 2>/dev/null || true)"

reason="Control-spine gate (Charter §4): these runs still have unchecked [ ] checkpoints — ${dirs}. Clear them in RESPONSE.md before stopping. If a run is intentionally abandoned, mark its remaining boxes [x] with a note (or remove its dir under output/.runs/)."
log_decision block "$open"
jq -cn --arg r "$reason" '{decision:"block",reason:$r}'
exit 0
