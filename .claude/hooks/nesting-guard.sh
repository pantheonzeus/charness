#!/usr/bin/env bash
# PreToolUse nesting guard (Charter §5: delegation is one level deep).
# Claude Code lets subagents spawn subagents (three layers by default), so the one-level rule was prose
# only. This hook makes it mechanical: an Agent/Task call made from inside a subagent is denied.
#   - main session (no agent_type in the hook input)                  → allow
#   - headless job's own top level (agent_type == CBRAIN_JOB, --agent) → allow
#   - any other agent_type (a domain or built-in subagent, a job's child) → deny + trace
# Subagents keep WebFetch themselves, so they never need the web-fetch subagent.
# Test: bash .claude/hooks/tests/nesting-guard.test.sh
# FAIL-OPEN by design: a parse problem allows the call.
set -uo pipefail

input="$(cat 2>/dev/null || true)"
atype="$(printf '%s' "$input" | jq -r '.agent_type // empty' 2>/dev/null || true)"
[ -z "$atype" ] && exit 0
[ -n "${CBRAIN_JOB:-}" ] && [ "$atype" = "$CBRAIN_JOB" ] && exit 0

REPO="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
log="$REPO/output/.runs/_forensics/hooks.jsonl"
mkdir -p "$(dirname "$log")" 2>/dev/null
printf '%s' "$input" | jq -c --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg job "${CBRAIN_JOB:-}" \
  '{ts: $ts, session_id: (.session_id // null), hook: "nesting-guard", decision: "deny", tool: (.tool_name // null),
    agent: (.agent_type // null), requested: (.tool_input.subagent_type // null), job: (if $job == "" then null else $job end)}' \
  >> "$log" 2>/dev/null || true
jq -cn --arg a "$atype" '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny",
  permissionDecisionReason: ("nesting guard: delegation is one level deep (Charter §5), and \($a) is already a subagent. Do the work yourself (you have WebFetch and WebSearch), or write what needs delegating into your RESPONSE.md for the parent.")}}'
exit 0
