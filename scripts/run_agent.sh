#!/usr/bin/env bash
# Shared runner for scheduled headless agent jobs (agent-roles rollout, step 1).
# Wraps one `claude -p` run so every job is measurable the same way:
#   1. runs claude with --output-format json and prints the result text to the job log
#   2. reopens the job's handoff RESPONSE.md (Charter §5 — the file is the record)
#   3. appends one line to output/.runs/_ledger/<job>.jsonl (cost, duration, turns, outcome)
#      and classifies it (failure codes from the transcript) via workflow-ops/run-forensics
#   4. exits with claude's own exit code, so callers' `set -e` behaves as before
# If .claude/agents/<job>.md exists, the run uses it (--agent: model + scope), its
# `budget_usd:` frontmatter becomes --max-budget-usd and its `effort:` becomes --effort. The model
# family's addendum (resources/models/<family>.md) is appended to the system prompt. CBRAIN_JOB is exported so the
# write-boundary hook can hold the run to that file's `write_scopes:`.
# The vault is snapshotted into its private history (scripts/vault_history.sh) before the run
# (as "unattributed") and after it (as <job>), so every vault change is attributable and undoable.
#
# Usage: run_agent.sh <job> <handoff-path|-> <prompt> [extra claude args...]
#   <job>          ledger key, e.g. meeting-prep
#   <handoff-path> child RESPONSE.md to reopen, or "-" when the job has none
# Summarise the ledger with scripts/agent_scorecard.sh.
set -uo pipefail

if [ $# -lt 3 ]; then
  echo "usage: run_agent.sh <job> <handoff-path|-> <prompt> [extra claude args...]" >&2
  exit 64
fi
JOB="$1"; HANDOFF="$2"; PROMPT="$3"; shift 3

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LEDGER_DIR="$REPO_ROOT/output/.runs/_ledger"
mkdir -p "$LEDGER_DIR"

START="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
GIT_SHA="$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"
[ -n "$(git -C "$REPO_ROOT" status --porcelain 2>/dev/null)" ] && GIT_SHA="$GIT_SHA-dirty"

AGENT_ARGS=()
BUDGET=""
AGENT_FILE="$REPO_ROOT/.claude/agents/$JOB.md"
if [ -f "$AGENT_FILE" ]; then
  AGENT_ARGS=(--agent "$JOB")
  BUDGET="$(sed -n 's/^budget_usd:[[:space:]]*\([0-9.]*\).*/\1/p' "$AGENT_FILE" | head -1)"
  [ -n "$BUDGET" ] && AGENT_ARGS+=(--max-budget-usd "$BUDGET")
  # Effort is the main per-model control and its levels mean different amounts of thinking on each model
  # (Anthropic, Prompting Claude Sonnet 5.5 / Opus 5.5), so each job pins it next to its pinned model.
  EFFORT="$(sed -n 's/^effort:[[:space:]]*\([a-z]*\).*/\1/p' "$AGENT_FILE" | head -1)"
  [ -n "$EFFORT" ] && AGENT_ARGS+=(--effort "$EFFORT")
  # Bash sandbox (G4b), opt-in per job: `sandbox: true` in the agent file's frontmatter, plus an
  # optional `network:` list of extra domains. Bash and its children may then write only inside the
  # repo (and uv's cache) and reach only pypi + the listed domains; no unsandboxed fallback, and the
  # run fails instead of running unsandboxed. WebFetch/WebSearch are outside the sandbox: the
  # egress-guard hook covers them. Canary 2026-10-23: write outside the repo and curl to an unlisted
  # domain both denied, uv-run helpers unaffected.
  # Code Mode, opt-in per job: `code_mode: true` means the job may run code it wrote itself. Bash-run
  # code skips the Write/Edit hooks (write_scopes, provenance), so it implies the sandbox and also denies
  # Bash writes to the vault and the harness (denyWrite wins over allowWrite). Such code writes only
  # output/; vault notes still go through the hooked Write/Edit tools.
  SANDBOX_JSON="$(/usr/bin/python3 - "$AGENT_FILE" "$REPO_ROOT" <<'PY' 2>/dev/null
import json, os, re, sys
m = re.match(r"---\n(.*?)\n---", open(sys.argv[1]).read(), re.S)
fm = m.group(1) if m else ""
code = re.search(r"^code_mode:\s*true\s*$", fm, re.M)
if code or re.search(r"^sandbox:\s*true\s*$", fm, re.M):
    extra = re.search(r"^network:\s*\n((?:[ \t]+-.*\n?)*)", fm, re.M)
    domains = ["pypi.org", "files.pythonhosted.org"] + \
        ([d.strip().strip("\"'") for d in re.findall(r"-\s*(.+)", extra.group(1))] if extra else [])
    fs = {"allowWrite": ["~/.cache/uv", "~/.local/share/uv"]}
    if code:
        fs["denyWrite"] = [os.path.join(sys.argv[2], p) for p in (
            "cbrain", ".claude", "resources", "scripts", "employers", "webapp", ".git", ".vault-history.git",
            "CLAUDE.md", "Charter.md", "Soul.md", "IDENTITY.md", ".mcp.json")]
    print(json.dumps({"sandbox": {"enabled": True, "failIfUnavailable": True, "allowUnsandboxedCommands": False,
                                  "network": {"allowedDomains": domains}, "filesystem": fs}}))
PY
)"
  [ -n "$SANDBOX_JSON" ] && AGENT_ARGS+=(--settings "$SANDBOX_JSON")
fi

# Model addendum: Anthropic's tested fixes for one model family (resources/models/README.md), appended to
# the system prompt. A --model passed by the caller wins over the agent file's, as it does in claude.
MODEL=""; prev=""
for a in "$@"; do [ "$prev" = "--model" ] && MODEL="$a"; prev="$a"; done
[ -z "$MODEL" ] && [ -f "$AGENT_FILE" ] && MODEL="$(sed -n 's/^model:[[:space:]]*\([^[:space:]]*\).*/\1/p' "$AGENT_FILE" | head -1)"
ADDENDUM=""
for fam in opus sonnet haiku fable; do
  case "$MODEL" in *"$fam"*) [ -f "$REPO_ROOT/resources/models/$fam.md" ] && ADDENDUM="resources/models/$fam.md"; break ;; esac
done
[ -n "$ADDENDUM" ] && AGENT_ARGS+=(--append-system-prompt-file "$REPO_ROOT/$ADDENDUM")

# Circuit breaker (G8): three runs in a row that end in API pressure (HTTP 429/529/5xx) open the
# circuit for every job, so a backlog loop stops hammering a rate-limited login (2026-10-23:
# substack-watch fired 20 runs into a 429 in four minutes). Open = exit 75 at once, no API call;
# the wait doubles per further failure (5 → 10 → 20 → 40 → 60 min cap); one good run closes it.
CIRCUIT="$LEDGER_DIR/_circuit.json"
NOW_EPOCH="$(date +%s)"
OPEN_UNTIL="$(jq -r '.open_until_epoch // 0' "$CIRCUIT" 2>/dev/null || echo 0)"
if [ "${OPEN_UNTIL:-0}" -gt "$NOW_EPOCH" ]; then
  echo "[$(date '+%F %T')] circuit open until $(date -r "$OPEN_UNTIL" '+%F %T') after repeated API-pressure failures; $JOB not started." >&2
  jq -cn --arg ts "$START" --arg job "$JOB" --arg sha "$GIT_SHA" \
    '{ts: $ts, job: $job, git_sha: $sha, exit_code: 75, is_error: true, subtype: "circuit_open", terminal_reason: "circuit_open"}' \
    >> "$LEDGER_DIR/$JOB.jsonl"
  exit 75
fi

export CBRAIN_JOB="$JOB"
export CBRAIN_RUN="$JOB-$START-$$"   # scripts/vault_api.py logs its writes under this id
VAULT_HISTORY="$REPO_ROOT/scripts/vault_history.sh"
bash "$VAULT_HISTORY" snapshot unattributed "before $JOB $START: vault changes since the last snapshot" >/dev/null 2>&1 \
  || echo "[$(date '+%F %T')] WARNING: pre-run vault snapshot failed" >&2

# Telemetry (G12). The ledger is the record: it keeps API time, time to first token, tokens and
# subagent counts from claude's own JSON result. OpenTelemetry export is opt-in: set
# CBRAIN_OTEL_ENDPOINT (an OTLP collector, e.g. http://localhost:4318) and every run exports
# metrics + events there. Prompts and tool content stay redacted (Claude Code's default).
if [ -n "${CBRAIN_OTEL_ENDPOINT:-}" ]; then
  export CLAUDE_CODE_ENABLE_TELEMETRY=1 OTEL_METRICS_EXPORTER=otlp OTEL_LOGS_EXPORTER=otlp \
         OTEL_EXPORTER_OTLP_PROTOCOL="${OTEL_EXPORTER_OTLP_PROTOCOL:-http/protobuf}" \
         OTEL_EXPORTER_OTLP_ENDPOINT="$CBRAIN_OTEL_ENDPOINT" OTEL_RESOURCE_ATTRIBUTES="cbrain.job=$JOB"
fi

ERRF="$(mktemp -t run_agent)"
# caffeinate -i: both recorded INFRA failures (2026-10-20 idea-engine, 2026-10-22 daily-intel)
# were the Mac going to sleep mid-run ("Your computer went to sleep mid-response"), not a
# broken launchd environment. Hold off idle sleep for the life of this one claude process.
# Claude Code 2.1.x has no Glob/Grep tools and points agents at Bash find/grep instead (BAD_INPUT,
# 2026-10-31). Every job may list and search read-only; repeated --allowedTools flags merge.
OUT="$(caffeinate -i claude -p "$PROMPT" --output-format json ${AGENT_ARGS[@]+"${AGENT_ARGS[@]}"} "$@" \
  --allowedTools "Bash(grep:*)" "Bash(ls:*)" 2>"$ERRF")"
RC=$?
cat "$ERRF" >&2

# The run's commit holds exactly the vault files this run's own Write/Edit calls touched (its transcript,
# subagents included), plus the ones scripts/vault_api.py logged under this run's CBRAIN_RUN, so
# concurrent jobs and your own edits never land under this job's name. Writes made by other helper
# scripts, and anything else, go into the next "unattributed" snapshot.
SESSION="$(printf '%s' "$OUT" | jq -r '.session_id // "unknown"' 2>/dev/null || echo unknown)"
TDIR="$HOME/.claude/projects/$(printf '%s' "$REPO_ROOT" | tr '/' '-')"
WRITTEN="$({
  for t in "$TDIR/$SESSION.jsonl" "$TDIR/$SESSION"/subagents/*.jsonl; do
    [ -f "$t" ] && jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use" and (.name|test("^(Write|Edit|MultiEdit|NotebookEdit)$"))) | (.input.file_path // .input.notebook_path // empty)' "$t" 2>/dev/null
  done
  jq -r --arg run "$CBRAIN_RUN" 'select(.run == $run) | .path' "$REPO_ROOT/output/.runs/_forensics/vault_api.jsonl" 2>/dev/null
  } | sed "s|^$REPO_ROOT/||" | sort -u)"
# Yield (G8): files the run wrote outside its own run state — deliverables, vault notes, triage files.
FILES_WRITTEN="$(printf '%s\n' "$WRITTEN" | grep -v '^output/\.runs/' | grep -c . || true)"
SPECS=()
while IFS= read -r p; do
  [ -f "$REPO_ROOT/cbrain/$p" ] && SPECS+=(":(literal)$p")
done < <(printf '%s\n' "$WRITTEN" | sed -n 's|^cbrain/||p')
if [ ${#SPECS[@]} -gt 0 ]; then
  bash "$VAULT_HISTORY" snapshot "$JOB" "$JOB $START session $SESSION exit $RC" "${SPECS[@]}" >/dev/null 2>&1 \
    || echo "[$(date '+%F %T')] WARNING: post-run vault snapshot failed" >&2
fi

# Auth alarm (run-forensics AUTH_EXPIRED): an expired `claude` login fails every job silently
# until someone logs in again. Raise it on the first failed run, clear it on the next good one.
AUTH_RE='Failed to authenticate|OAuth session expired|authentication_error|Invalid API key|Not logged in|Please run /login'
ALARM="$REPO_ROOT/output/.runs/_forensics/auth-alarm.json"
auth_failed=false
if [ "$RC" -ne 0 ] && { printf '%s' "$OUT"; cat "$ERRF"; } | grep -qE "$AUTH_RE"; then
  auth_failed=true
  mkdir -p "$(dirname "$ALARM")"
  NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  if [ -f "$ALARM" ]; then
    jq -c --arg now "$NOW" --arg job "$JOB" '.last = $now | .runs += 1 | .jobs = (.jobs + [$job] | unique)' "$ALARM" > "$ALARM.tmp" && mv "$ALARM.tmp" "$ALARM"
  else
    jq -cn --arg now "$NOW" --arg job "$JOB" '{since: $now, last: $now, runs: 1, jobs: [$job]}' > "$ALARM"
    osascript -e 'display notification "Headless agent jobs are failing. Run claude in a terminal and log in." with title "Claude login expired" sound name "Basso"' >/dev/null 2>&1 || true
  fi
elif [ "$RC" -eq 0 ]; then
  rm -f "$ALARM"
fi
rm -f "$ERRF"

# The result text is what the plain-text run used to print — keep the job log readable.
printf '%s\n' "$OUT" | jq -r '.result // empty' 2>/dev/null || printf '%s\n' "$OUT"

handoff_present=null
if [ "$HANDOFF" != "-" ]; then
  if [ -f "$HANDOFF" ]; then
    handoff_present=true
    echo "[$(date '+%F %T')] Handoff result ($HANDOFF):"; cat "$HANDOFF"
  else
    handoff_present=false
    echo "[$(date '+%F %T')] WARNING: handoff result missing — $HANDOFF (child did not report back)."
  fi
fi

# One ledger line per run. If claude produced no JSON (crash, auth failure), the
# metric fields stay null but the line is still written — a failed run must be visible.
META="$(printf '%s' "$OUT" | jq -c '{is_error, subtype, terminal_reason,
  cost_usd: .total_cost_usd, duration_ms, num_turns,
  permission_denials: ((.permission_denials // []) | length),
  api_error_status, error: ((.errors // [])[0]), startup_failure_reason,
  models: ((.modelUsage // {}) | keys), session_id,
  duration_api_ms, ttft_ms,
  tokens: (if .usage then {in: .usage.input_tokens, out: .usage.output_tokens,
           cache_read: .usage.cache_read_input_tokens, cache_write: .usage.cache_creation_input_tokens,
           web_search: .usage.server_tool_use.web_search_requests, web_fetch: .usage.server_tool_use.web_fetch_requests}
          else null end),
  subagents: .subagent_stats.spawned, credential_expires_at}' 2>/dev/null || true)"
[ -n "$META" ] || META='{}'
jq -cn --arg ts "$START" --arg job "$JOB" --arg sha "$GIT_SHA" --argjson rc "$RC" \
  --argjson handoff "$handoff_present" --arg budget "$BUDGET" --argjson meta "$META" --argjson auth "$auth_failed" \
  --argjson files "${FILES_WRITTEN:-0}" --arg effort "${EFFORT:-}" --arg addendum "$ADDENDUM" \
  '{ts: $ts, job: $job, git_sha: $sha, exit_code: $rc, handoff_present: $handoff, auth_failed: $auth,
    budget_usd: (if $budget == "" then null else ($budget | tonumber) end), files_written: $files,
    effort: (if $effort == "" then null else $effort end), addendum: (if $addendum == "" then null else $addendum end)} + $meta' \
  >> "$LEDGER_DIR/$JOB.jsonl"

# Login expiry warning: Claude Code 2.1.318+ reports the sign-in's end in the JSON result. Under 7 days
# left, write auth-expiry.json and notify once per expiry date; a date past the window removes the file.
# A run without the field (older CLI, crash, API key) leaves the file alone. The value's format is not
# documented, so ISO strings and epoch seconds or milliseconds are all read.
EXPIRY="$REPO_ROOT/output/.runs/_forensics/auth-expiry.json"
EXP_RAW="$(printf '%s' "$META" | jq -r '.credential_expires_at // empty' 2>/dev/null)"
if [ -n "$EXP_RAW" ]; then
  EXP_EPOCH="$(/usr/bin/python3 - "$EXP_RAW" <<'PY' 2>/dev/null
import sys
from datetime import datetime, timezone
v = sys.argv[1]
try:
    n = float(v)
    print(int(n / 1000 if n > 1e11 else n))
except ValueError:
    d = datetime.fromisoformat(v.replace("Z", "+00:00"))
    print(int((d if d.tzinfo else d.replace(tzinfo=timezone.utc)).timestamp()))
PY
)"
  if [ -z "$EXP_EPOCH" ]; then
    echo "[$(date '+%F %T')] WARNING: unreadable credential_expires_at: $EXP_RAW" >&2
  elif [ $(( EXP_EPOCH - $(date +%s) )) -lt 604800 ]; then
    EXP_DATE="$(date -r "$EXP_EPOCH" +%F)"
    if [ "$(jq -r '.expires_date // empty' "$EXPIRY" 2>/dev/null)" != "$EXP_DATE" ]; then
      mkdir -p "$(dirname "$EXPIRY")"
      jq -cn --arg raw "$EXP_RAW" --arg d "$EXP_DATE" --argjson e "$EXP_EPOCH" --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        '{expires_at: $raw, expires_date: $d, expires_epoch: $e, since: $now}' > "$EXPIRY.tmp" && mv "$EXPIRY.tmp" "$EXPIRY"
      osascript -e "display notification \"Run claude auth login in a terminal before then.\" with title \"Claude login ends $EXP_DATE\" sound name \"Basso\"" >/dev/null 2>&1 || true
    fi
  else
    rm -f "$EXPIRY"
  fi
fi

# Circuit bookkeeping: API pressure counts toward opening; any other outcome closes it.
STATUS="$(printf '%s' "$META" | jq -r '.api_error_status // empty' 2>/dev/null)"
if [ -n "$STATUS" ] && { [ "$STATUS" = 429 ] || [ "$STATUS" = 529 ] || [ "$STATUS" -ge 500 ] 2>/dev/null; }; then
  FAILS=$(( $(jq -r '.failures // 0' "$CIRCUIT" 2>/dev/null || echo 0) + 1 ))
  UNTIL=0
  if [ "$FAILS" -ge 3 ]; then
    WAIT=$(( 300 * (1 << (FAILS - 3)) )); [ "$WAIT" -gt 3600 ] && WAIT=3600
    UNTIL=$(( $(date +%s) + WAIT ))
    echo "[$(date '+%F %T')] circuit opened for $(( WAIT / 60 )) min after $FAILS API-pressure failures (last: $JOB, HTTP $STATUS)." >&2
  fi
  jq -cn --argjson f "$FAILS" --argjson u "$UNTIL" --arg job "$JOB" --arg st "$STATUS" \
    '{failures: $f, open_until_epoch: $u, last_job: $job, last_status: $st}' > "$CIRCUIT.tmp" && mv "$CIRCUIT.tmp" "$CIRCUIT"
elif [ "$RC" -eq 0 ]; then
  rm -f "$CIRCUIT"
fi

# Classify the run (why it failed, which failure codes it hit) — workflow-ops/run-forensics.
# Best effort: forensics must never change the job's outcome.
/usr/bin/python3 "$REPO_ROOT/resources/skills/workflow-ops/run-forensics/scripts/forensics.py" ingest >/dev/null 2>&1 || true

exit "$RC"
