#!/usr/bin/env bash
# Regression test for .claude/hooks/nesting-guard.sh. Hermetic: a throwaway CLAUDE_PROJECT_DIR.
# Run: bash .claude/hooks/tests/nesting-guard.test.sh   (exit 0 = all pass)
set -uo pipefail
HOOK="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/nesting-guard.sh"
FAKE="$(mktemp -d)"; trap 'rm -rf "$FAKE"' EXIT

pass=0; fail=0
check() {   # $1 name, $2 expect allow|deny, $3 agent_type ("" = none), $4 CBRAIN_JOB, [$5 raw input]
  local in out got
  if [ -n "${5:-}" ]; then in="$5"
  elif [ -n "$3" ]; then in="$(jq -cn --arg a "$3" '{tool_name:"Agent", session_id:"t", agent_type:$a, tool_input:{subagent_type:"Explore"}}')"
  else in='{"tool_name":"Agent","session_id":"t","tool_input":{"subagent_type":"web-fetch"}}'; fi
  out="$(printf '%s' "$in" | CLAUDE_PROJECT_DIR="$FAKE" CBRAIN_JOB="$4" bash "$HOOK")"
  if printf '%s' "$out" | grep -q '"permissionDecision":"deny"'; then got=deny; else got=allow; fi
  if [ "$got" = "$2" ]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL: $1 — expected $2, got $got ($out)"; fi
}
check "main session spawns"                allow ""                ""
check "headless job main spawns"           allow ""                role-scout
check "headless --agent top level spawns"  allow research          research
check "domain subagent in chat"            deny  research          ""
check "built-in subagent in chat"          deny  general-purpose   ""
check "job's child spawns"                 deny  general-purpose   researcher-deep
check "fork spawns"                        deny  fork              ""
check "garbage input fails open"           allow ""                ""   "not json"
grep -q '"hook":"nesting-guard"' "$FAKE/output/.runs/_forensics/hooks.jsonl" 2>/dev/null \
  && pass=$((pass + 1)) || { fail=$((fail + 1)); echo "FAIL: deny trace missing"; }
echo "nesting-guard: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
