#!/usr/bin/env bash
# Per-job scorecard over the run ledger written by scripts/run_agent.sh.
# Usage: agent_scorecard.sh [days]   (default 30)
# A run counts as ok when claude exited 0, reported no error, and — if the job has a
# handoff — the handoff file exists. Yield = share of runs that wrote a file outside their run state
# (files_written > 0, logged since 2026-10-23); $/yield = cost of those measured runs per productive run.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LEDGER_DIR="$REPO_ROOT/output/.runs/_ledger"
DAYS="${1:-30}"
SINCE="$(date -u -v-"${DAYS}"d +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d "-${DAYS} days" +%Y-%m-%dT%H:%M:%SZ)"

shopt -s nullglob
files=("$LEDGER_DIR"/*.jsonl)
[ ${#files[@]} -eq 0 ] && { echo "No ledger yet ($LEDGER_DIR)."; exit 0; }

echo "Scorecard — last $DAYS days (since $SINCE)"
cat "${files[@]}" | jq -rs --arg since "$SINCE" '
  def ok: .exit_code == 0 and (.is_error != true) and (.handoff_present != false);
  def r2: . * 100 | round / 100;
  map(select(.ts >= $since)) | group_by(.job) | map({
    job: .[0].job, runs: length, ok: (map(select(ok)) | length),
    cost: (map(.cost_usd // 0) | add | r2),
    cost_run: ((map(.cost_usd // 0) | add) / length | r2),
    min_run: ((map(.duration_ms // 0) | add) / length / 60000 | r2),
    turns_run: ((map(.num_turns // 0) | add) / length | round),
    measured: (map(select(.files_written != null))),
    last: (max_by(.ts) | .ts)
  } | . + {
    yield: (if (.measured | length) == 0 then "–" else ((.measured | map(select(.files_written > 0)) | length) * 100 / (.measured | length) | round | tostring + "%") end),
    cost_yield: ((.measured | map(select(.files_written > 0)) | length) as $p | if $p == 0 then "–" else ((.measured | map(.cost_usd // 0) | add) / $p | r2 | tostring) end)
  })
  | (["job","runs","ok","cost$","$/run","min/run","turns/run","yield","$/yield","last run"] | @tsv),
    (.[] | [.job, .runs, .ok, .cost, .cost_run, .min_run, .turns_run, .yield, .cost_yield, .last] | @tsv)
' | column -t -s $'\t'
