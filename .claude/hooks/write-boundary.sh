#!/usr/bin/env bash
# PreToolUse write-boundary guard (Core Rule #4 safety net).
# Denies file-writing tools whose target is an ABSOLUTE path OUTSIDE the allowed zones:
#   - the repo tree            ($CLAUDE_PROJECT_DIR)
#   - the session scratchpad   (/private/tmp/claude-* , /tmp/claude-*)
#   - the Claude home          (~/.claude/…)
#   - sibling project          ../case-study (PE interview prototype, allowed by the user 2026-10-21)
# Everything in-repo (vault cbrain/, resources/, output/, .claude/) is allowed. Relative
# paths are resolved against the session cwd, and `.`/`..` segments are collapsed before the
# check, so `../../.zshrc` or `$REPO/../x` can't slip past it. This catches stray/accidental
# writes to $HOME or the system without blocking real work. Symlinks are then resolved
# (os.path.realpath: existing components only, a not-yet-created tail stays as is), so a link
# inside the repo that points outside it can't carry a write out (Anthropic, "How we contain
# Claude", 2026-05: resolve symlinks before path validation).
#
# Per-job write scopes (headless runs). scripts/run_agent.sh exports CBRAIN_JOB; when
# .claude/agents/<job>.md declares `write_scopes:` (repo-relative bash patterns, `*` crosses `/`;
# a pattern starting with / or ~/ is absolute), that job may write ONLY inside them — the vault
# included. No CBRAIN_JOB (interactive sessions) or no `write_scopes:` → the zones above apply.
# Test: bash .claude/hooks/tests/write-boundary.test.sh
#
# FAIL-OPEN by design: any parse problem, missing path, or non-file tool → allow (exit 0,
# no output). We never block a write because our own parsing choked.
set -uo pipefail

input="$(cat 2>/dev/null || true)"
path="$(printf '%s' "$input" | jq -r '.tool_input.file_path // .tool_input.notebook_path // .tool_input.path // empty' 2>/dev/null || true)"

# No path (non-file tool, or parse failure) → defer to the normal permission flow.
[ -z "$path" ] && exit 0

# Relative path → anchor it at the session cwd (from the hook input, else our own cwd).
case "$path" in
  /*) : ;;
  *) cwd="$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null || true)"
     path="${cwd:-$PWD}/$path" ;;
esac

# Collapse `.` and `..` segments lexically.
set -f
parts=()
IFS=/
for seg in $path; do
  case "$seg" in
    ''|.) : ;;
    ..) [ ${#parts[@]} -gt 0 ] && unset "parts[$((${#parts[@]} - 1))]" ;;
    *) parts+=("$seg") ;;
  esac
done
unset IFS
set +f
path="/"
[ ${#parts[@]} -gt 0 ] && path="$(printf '/%s' "${parts[@]}")"

realpath_of() { /usr/bin/python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$1" 2>/dev/null || printf '%s' "$1"; }
path="$(realpath_of "$path")"

REPO="$(realpath_of "${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}")"
HOME_CLAUDE="$(realpath_of "$HOME/.claude")"
CASE_STUDY="$(dirname "$REPO")/case-study"
JOB="${CBRAIN_JOB:-}"

deny() {   # $1 = reason. Deny the write, and leave one line for run-forensics (best effort).
  jq -cn --arg r "$1" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}'
  local log="$REPO/output/.runs/_forensics/hooks.jsonl"
  mkdir -p "$(dirname "$log")" 2>/dev/null
  printf '%s' "$input" | jq -c --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --arg path "$path" --arg job "$JOB" \
    '{ts: $ts, session_id: (.session_id // null), hook: "write-boundary", decision: "deny", tool: (.tool_name // null), path: $path, job: (if $job == "" then null else $job end)}' \
    >> "$log" 2>/dev/null || true
  exit 0
}

# Confirmation is a human act (Charter §6 trust tier): a headless job may not add, change or remove
# a vault note's `confirmed:` line, so it can't Write a confirmed note whole either. Its Edits that
# leave that line alone still pass. Interactive sessions are held to this by policy alone.
shopt -s nocasematch
if [ -n "$JOB" ] && [[ "$path" == "$REPO"/cbrain/* ]] && printf '%s' "$input" | jq -e \
     '[.tool_input | (.content, .new_string, .old_string, ((.edits // [])[] | .new_string, .old_string)) | strings
       | test("(^|\n)[ \t]*confirmed:"; "i")] | any' >/dev/null 2>&1; then
  deny "write-boundary guard: job '$JOB' touched a 'confirmed:' line in ${path#"$REPO"/}. Only the principal confirms a note; leave that line as it is, append via Edit or scripts/vault_api.py, and list the note as 'needs confirmation' in your RESPONSE.md."
fi
shopt -u nocasematch

# Headless job with declared scopes → its scopes are the whole allow-list.
if [ -n "$JOB" ] && [ -f "$REPO/.claude/agents/$JOB.md" ]; then
  scopes="$(awk '
    /^---[[:space:]]*$/ { fm++; next }
    fm == 1 && /^write_scopes:/ { on = 1; next }
    fm == 1 && on && /^[[:space:]]+-[[:space:]]/ { sub(/^[[:space:]]+-[[:space:]]+/, ""); gsub(/^["'\'']|["'\''][[:space:]]*$/, ""); print; next }
    { on = 0 }' "$REPO/.claude/agents/$JOB.md" 2>/dev/null || true)"
  if [ -n "$scopes" ]; then
    # APFS is case-insensitive: cbrain/Notes/ and cbrain/notes/ are one folder, so match that way.
    shopt -s nocasematch
    rel="${path#"$REPO"/}"
    while IFS= read -r pat; do
      case "$pat" in
        "~/"*) [[ "$path" == $HOME/${pat#"~/"} ]] && exit 0 ;;
        /*)    [[ "$path" == $pat ]] && exit 0 ;;
        *)     [ "$rel" != "$path" ] && [[ "$rel" == $pat ]] && exit 0 ;;
      esac
    done <<< "$scopes"
    deny "write-boundary guard: job '$JOB' may write only inside its write_scopes ($(printf '%s' "$scopes" | paste -sd' ' -)); '$rel' is outside them. Write inside your scopes, or report the gap in your RESPONSE.md. A wrong scope is fixed by a human in .claude/agents/$JOB.md, never by this run."
  fi
fi

case "$path" in
  "$REPO"|"$REPO"/*)              exit 0 ;;
  "$CASE_STUDY"|"$CASE_STUDY"/*)  exit 0 ;;
  /private/tmp/claude-*|/tmp/claude-*) exit 0 ;;
  "$HOME_CLAUDE"|"$HOME_CLAUDE"/*) exit 0 ;;
esac

# Out of bounds → deny with a clear, actionable reason.
deny "write-boundary guard: '$path' is outside the allowed zones (repo tree, session scratchpad, ~/.claude). If this is intentional, widen the allow-list in .claude/hooks/write-boundary.sh or bypass the hook."
