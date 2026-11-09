#!/usr/bin/env bash
# Regression test for scripts/spotcheck.py on a throwaway repo: report counts, blind sheet, score.
# Run: bash .claude/hooks/tests/spotcheck.test.sh   (exit 0 = all pass)
set -uo pipefail
SC="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/scripts/spotcheck.py"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
M="$T/output/mail-triage"; mkdir -p "$M/messages" "$M/triage" "$T/output/.runs/_forensics"
NOW="$(date +%Y-%m-%dT%H:%M:%S)"; NOWZ="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
jq -n --arg at "$NOW" '{
  "aaaaaaaa01": {action: "read", dwell_s: 1.1, at: $at},
  "aaaaaaaa02": {action: "done", dwell_s: 40, at: $at},
  "aaaaaaaa03": {action: "sent", dwell_s: 2, edited: false, at: $at},
  "aaaaaaaa04": {action: "read", bulk: true, dwell_s: 0.5, at: $at},
  "aaaaaaaa05": {action: "done", at: "2020-01-01T00:00:00"}}' > "$M/decisions.json"
for id in aaaaaaaa01 aaaaaaaa02 aaaaaaaa03 aaaaaaaa04; do
  jq -n --arg id "$id" '{from_name: "Mark", subject: ("Re " + $id), body: "Can you send the outline?"}' > "$M/messages/$id.json"
  jq -n '{category: "answer", summary: "Wants the outline.", reply: "Hi Mark,\nFriday."}' > "$M/triage/$id.json"
done
jq -cn --arg ts "$NOWZ" '{ts: $ts, hook: "send-gate", decision: "allow", approval_s: 1.2}' > "$T/output/.runs/_forensics/hooks.jsonl"
jq -cn --arg ts "$NOWZ" '{ts: $ts, hook: "send-gate", decision: "deny", approval_s: 0.4}' >> "$T/output/.runs/_forensics/hooks.jsonl"

pass=0; fail=0
ok() { if eval "$2"; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: $1"; fi; }
R="$(CLAUDE_PROJECT_DIR="$T" python3 "$SC" report)"
ok "old decisions fall outside the window"  'grep -q "mail decisions: 4 " <<<"$R"'
ok "bulk counted on its own"                'grep -q "bulk .mark all read.: 1" <<<"$R"'
ok "fast decisions exclude bulk"            'grep -q "under 3 s on screen: 2 of 3 timed" <<<"$R"'
ok "unedited sends counted"                 'grep -q "sent unedited: 1 of 1 sent" <<<"$R"'
ok "only allowed sends are timed"           'grep -q "read-back: 1 of 1 timed (1 sends)" <<<"$R"'
S="$(CLAUDE_PROJECT_DIR="$T" python3 "$SC" sample --n 3)"
ok "sheet written"                          '[ -f "$S" ]'
ok "sheet prefers non-bulk decisions"       '! grep -q aaaaaaaa04 "$S"'
ok "sheet opens with the week's signals"     'grep -q "under 3 s on screen: 2 of 3 timed" "$S"'
ok "sheet hides each mail's original call"  '! sed -n "/^## 1 /,\$p" "$S" | grep -qiE "dwell|action|unedited"'
# Tick "done" everywhere: agrees only with aaaaaaaa02.
sed -i.bak 's/^- \[ \] done$/- [x] done/; s/^- \[ \] triage right$/- [x] triage right/' "$S"
C="$(CLAUDE_PROJECT_DIR="$T" python3 "$SC" score "$S")"
ok "agreement scored"                       'grep -q "agreement: 1 of 3" <<<"$C"'
ok "disagreement names the original call"   'grep -q "aaaaaaaa03: now done, then reply" <<<"$C"'
ok "score appended to the ledger"           '[ "$(jq .agree "$T/output/spotcheck/scores.jsonl")" = 1 ]'

echo "spotcheck: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
