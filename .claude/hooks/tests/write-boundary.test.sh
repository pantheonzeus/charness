#!/usr/bin/env bash
# Regression test for .claude/hooks/write-boundary.sh — repo zones + per-job write scopes.
# Hermetic: builds a throwaway repo with fixture agent files; never touches the real one.
# Run: bash .claude/hooks/tests/write-boundary.test.sh   (exit 0 = all pass)
set -uo pipefail

HOOK="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/write-boundary.sh"
FAKE="$(mktemp -d)"; trap 'rm -rf "$FAKE"' EXIT
FAKE="$(cd "$FAKE" && pwd -P)"
mkdir -p "$FAKE/.claude/agents"
cat > "$FAKE/.claude/agents/scoped.md" <<'EOF'
---
name: scoped
model: sonnet
write_scopes:
  - output/briefings/*.json
  - output/.runs/*-scoped/*
  - "cbrain/projects/*"
  - ~/.claude/scoped-test/*
budget_usd: 1
---
Body text with write_scopes:
  - cbrain/*
EOF
cat > "$FAKE/.claude/agents/unscoped.md" <<'EOF'
---
name: unscoped
budget_usd: 1
---
EOF

pass=0; fail=0
check() {   # $1 name, $2 expect allow|deny, $3 job ("" = interactive), $4 tool, $5 path, [$6 path key]
  local key="${6:-file_path}" out got
  out="$(jq -cn --arg t "$4" --arg p "$5" --arg k "$key" --arg cwd "$FAKE" \
          '{tool_name: $t, cwd: $cwd, session_id: "test", tool_input: {($k): $p}}' \
        | CLAUDE_PROJECT_DIR="$FAKE" CBRAIN_JOB="$3" bash "$HOOK")"
  if printf '%s' "$out" | grep -q '"permissionDecision":"deny"'; then got=deny; else got=allow; fi
  if [ "$got" = "$2" ]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL: $1 — expected $2, got $got ($out)"; fi
}

# Interactive (no job): the repo-zone rules, unchanged.
check "interactive vault write"          allow ""       Write "$FAKE/cbrain/Clients/A.md"
check "interactive outside zones"        deny  ""       Write "/etc/hosts"
# Scoped job: only its scopes.
check "scoped in-scope output"           allow scoped   Write "$FAKE/output/briefings/2026-10-23.json"
check "scoped in-scope state root"       allow scoped   Write "$FAKE/output/.runs/20261023-scoped/children/a/RESPONSE.md"
check "scoped in-scope vault (quoted)"   allow scoped   Edit  "$FAKE/cbrain/projects/Topic.md"
check "scoped relative in-scope"         allow scoped   Write "output/briefings/x.json"
check "scoped absolute ~/ scope"         allow scoped   Write "$HOME/.claude/scoped-test/x.md"
check "scoped vault out of scope"        deny  scoped   Edit  "$FAKE/cbrain/Clients/A.md"
check "scoped traversal into vault"      deny  scoped   Write "$FAKE/output/briefings/../../cbrain/Home.md"
check "scoped case variant, same folder" allow scoped   Write "$FAKE/CBRAIN/Projects/Topic.md"
check "scoped case variant, out of scope" deny scoped   Write "$FAKE/CBRAIN/Clients/A.md"
check "scoped own agent file"            deny  scoped   Edit  "$FAKE/.claude/agents/scoped.md"
check "scoped other run's state root"    deny  scoped   Write "$FAKE/output/.runs/20261023-other/RESPONSE.md"
check "scoped body list is ignored"      deny  scoped   Write "$FAKE/cbrain/Mail/x.md"
check "scoped NotebookEdit out of scope" deny  scoped   NotebookEdit "$FAKE/cbrain/x.ipynb" notebook_path
check "scoped MultiEdit out of scope"    deny  scoped   MultiEdit "$FAKE/resources/skills/x/SKILL.md"
check "scoped ~/.claude outside scope"   deny  scoped   Write "$HOME/.claude/settings.json"
# Job without declared scopes, or unknown job: falls back to the zone rules.
check "unscoped job in repo"             allow unscoped Write "$FAKE/cbrain/Clients/A.md"
check "unknown job in repo"              allow nosuch   Write "$FAKE/cbrain/Clients/A.md"
check "unscoped job outside zones"       deny  unscoped Write "/etc/hosts"
# Symlinks are resolved: a link inside the repo pointing outside it can't carry a write out.
mkdir -p "$FAKE/outside-target"; OUTSIDE="$(mktemp -d)"; ln -s "$OUTSIDE" "$FAKE/escape"
check "symlink in repo to outside"       deny  ""       Write "$FAKE/escape/payload.txt"
ln -s "$FAKE/outside-target" "$FAKE/inner-link"
check "symlink in repo to inside"        allow ""       Write "$FAKE/inner-link/ok.txt"
rm -rf "$OUTSIDE"
# Confirmation is human-only: a job may not add, change or remove a vault note's `confirmed:` line.
confirm() {   # $1 name, $2 expect, $3 job, $4 tool_input JSON (file_path is added)
  local out got
  out="$(jq -cn --argjson ti "$4" --arg p "$FAKE/cbrain/projects/Topic.md" --arg cwd "$FAKE" \
          '{tool_name: "Edit", cwd: $cwd, session_id: "test", tool_input: ($ti + {file_path: $p})}' \
        | CLAUDE_PROJECT_DIR="$FAKE" CBRAIN_JOB="$3" bash "$HOOK")"
  if printf '%s' "$out" | grep -q '"permissionDecision":"deny"'; then got=deny; else got=allow; fi
  if [ "$got" = "$2" ]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL: $1 — expected $2, got $got ($out)"; fi
}
confirm "job adds confirmed:"            deny  scoped   '{"old_string":"type: topic\n","new_string":"type: topic\nconfirmed: 2026-10-29\n"}'
confirm "job removes confirmed:"         deny  scoped   '{"old_string":"confirmed: 2026-10-29\n","new_string":""}'
confirm "job Writes a confirmed note"    deny  scoped   '{"content":"---\ntype: topic\nconfirmed: 2026-10-29\n---\nBody\n"}'
confirm "job MultiEdit confirmed:"       deny  unscoped '{"edits":[{"old_string":"a","new_string":"b"},{"old_string":"x","new_string":"  Confirmed: 2026-10-29"}]}'
confirm "job body edit, line untouched"  allow scoped   '{"old_string":"## Links\n","new_string":"## Links\n- [[X]] — reason\n"}'
confirm "job prose mentions confirmed"   allow scoped   '{"old_string":"a","new_string":"the client confirmed: yes"}'
confirm "interactive sets confirmed:"    allow ""       '{"old_string":"type: topic\n","new_string":"type: topic\nconfirmed: 2026-10-29\n"}'
# Every deny is traced for run-forensics, with the job.
grep -q '"job":"scoped"' "$FAKE/output/.runs/_forensics/hooks.jsonl" 2>/dev/null \
  && pass=$((pass + 1)) || { fail=$((fail + 1)); echo "FAIL: deny trace missing job field"; }

echo "write-boundary: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
