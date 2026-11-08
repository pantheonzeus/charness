#!/usr/bin/env bash
# Regression test for .claude/hooks/path-hint.py. Fixture tree in a throwaway repo.
# Run: bash .claude/hooks/tests/path-hint.test.sh   (exit 0 = all pass)
set -uo pipefail
HOOK="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/path-hint.py"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
R="$T/repo"
mkdir -p "$R/output/.runs/20261102-0900-mail-triage" "$R/cbrain/notes" "$T/outside/secretdir"
touch "$R/output/.runs/20261102-0900-mail-triage/RESPONSE.md" "$R/cbrain/notes/20261101-Alice.md" "$R/cbrain/notes/20261030-Bob.md"
touch "$T/outside/secret-file.txt"

pass=0; fail=0
run() {   # $1 tool, $2 file_path, $3 error → hook stdout
  jq -cn --arg t "$1" --arg p "$2" --arg e "$3" --arg c "$R" \
    '{hook_event_name:"PostToolUseFailure", tool_name:$t, tool_input:{file_path:$p}, error:$e, cwd:$c}' \
    | CLAUDE_PROJECT_DIR="$R" python3 "$HOOK"
}
check() {   # $1 name, $2 expect (has|lacks|empty), $3 needle, $4 output
  local ok=0
  case "$2" in
    has)   printf '%s' "$4" | grep -qF -- "$3" && ok=1 ;;
    lacks) printf '%s' "$4" | grep -qF -- "$3" || ok=1 ;;
    empty) [ -z "$4" ] && ok=1 ;;
  esac
  if [ "$ok" = 1 ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: $1 — expected $2 '$3', got: $4"; fi
}
MISS="File does not exist. Note: your current working directory is $R."

out="$(run Read "$R/output/.runs/20261102-0900-mail-triag/RESPONSE.md" "$MISS")"
check "run-dir miss names the real sibling"      has   "20261102-0900-mail-triage/" "$out"
check "run-dir miss names the nearest dir"       has   "Nearest existing dir: output/.runs/" "$out"
check "hint is PostToolUseFailure context"       has   '"hookEventName": "PostToolUseFailure"' "$out"

out="$(run Edit "output/.runs/20261102-0900-mail-triage/RESPONS.md" "$MISS")"
check "relative Edit path resolves against cwd"  has   "RESPONSE.md" "$out"

out="$(run Read "$T/outside/secret.txt" "$MISS")"
check "path outside the repo gets no output"     empty "" "$out"

out="$(run Read "$R/../outside/secret.txt" "$MISS")"
check "dot-dot escape gets no output"            empty "" "$out"

out="$(run Read "$R/output/.runs/20261102-0900-mail-triage/RESPONSE.md" "File is too large to read")"
check "non-path error gets no output"            empty "" "$out"

out="$(run Bash "$R/output/.runs/nope" "$MISS")"
check "other tool gets no output"                empty "" "$out"

out="$(run Read "$R/cbrain/notes/20261101-Alic.md" "$MISS")"
check "vault miss names the closest match"       has   "20261101-Alice.md" "$out"
check "vault miss gets no directory listing"     lacks "Entries:" "$out"
check "vault miss omits non-matching notes"      lacks "Bob" "$out"

out="$(printf 'not json' | CLAUDE_PROJECT_DIR="$R" python3 "$HOOK")"; rc=$?
check "bad input fails open"                     empty "" "$out"
[ "$rc" -eq 0 ] && pass=$((pass+1)) || { fail=$((fail+1)); echo "FAIL: bad input exit $rc"; }

echo "path-hint: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
