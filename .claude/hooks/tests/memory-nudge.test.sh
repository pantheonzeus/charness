#!/usr/bin/env bash
# Regression test for .claude/hooks/memory_nudge.py. Fixture transcripts and state in a throwaway repo.
# Run: bash .claude/hooks/tests/memory-nudge.test.sh   (exit 0 = all pass)
set -uo pipefail
HOOK="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/memory_nudge.py"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT

calls() {   # $1 = number of tool calls → transcript on stdout
  for _ in $(seq 1 "$1"); do
    jq -cn '{type:"assistant", message:{role:"assistant", content:[{type:"tool_use", id:"x", name:"Read", input:{}}]}}'
  done
}
pass=0; fail=0
check() {   # $1 name, $2 expect (block|allow), $3 transcript, $4 session, [$5 job], [$6 stop_hook_active]
  local out got
  out="$(jq -cn --arg tp "$3" --arg s "$4" --argjson a "${6:-false}" '{session_id:$s, transcript_path:$tp, stop_hook_active:$a}' \
        | CLAUDE_PROJECT_DIR="$T/repo" CBRAIN_JOB="${5:-}" python3 "$HOOK")"
  if printf '%s' "$out" | grep -q '"decision": *"block"'; then got=block; else got=allow; fi
  if [ "$got" = "$2" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: $1 — expected $2, got $got ($out)"; fi
}

calls 5  > "$T/short.jsonl"
calls 30 > "$T/long.jsonl"
calls 45 > "$T/longer.jsonl"
calls 60 > "$T/longest.jsonl"

check "short session"                    allow "$T/short.jsonl"   s1
check "30 calls nudges"                  block "$T/long.jsonl"    s2
check "same count, no repeat"            allow "$T/long.jsonl"    s2
check "15 more calls, still quiet"       allow "$T/longer.jsonl"  s2
check "30 more calls nudges again"       block "$T/longest.jsonl" s2
check "headless job never nudges"        allow "$T/long.jsonl"    s3 mail-triage
check "own block cycle releases"         allow "$T/long.jsonl"    s4 "" true
check "missing transcript fails open"    allow "$T/nope.jsonl"    s5

echo "memory-nudge: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
