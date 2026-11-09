#!/usr/bin/env bash
# Regression test for the research firewall in meeting-prep-loop's `sync.py check`: a web-sourced
# participant note must be labelled External, and new_insight must come from a finding the harvest offered.
# Fixtures in a throwaway dir; sync.py is imported with REPO pointed there.
# Run: bash .claude/hooks/tests/prep-firewall.test.sh   (exit 0 = all pass)
set -uo pipefail
SYNC="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/resources/skills/workflow-ops/meeting-prep-loop/scripts"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/output/frontier" "$T/output/client-news/findings"
jq -n '{topics: [{note: "projects/OPC UA.md", findings: [{id: 1, text: "x", sources: [{url: "https://ex.org/new"}]}]}]}' > "$T/output/frontier/2026-11-05.json"
jq -n '{topics: [{note: "projects/OPC UA.md", findings: [{id: 1, text: "x", sources: [{url: "https://ex.org/old"}]}]}]}' > "$T/output/frontier/2026-10-20.json"

prep() {   # $1 name, $2 participant note, $3 new_insight url ("" = none)
  jq -n --arg uid "$1" --arg note "$2" --arg url "$3" '{uid: $uid, fingerprint: "f", goal: "g", enriched_at: "2026-11-09T08:00:00+01:00",
    mail_ids: [], participants: [{name: "Jane", internal: false, notes: [$note]}], talking_points: ["t"], smart_questions: ["q"]}
    + (if $url == "" then {} else {new_insight: {text: "t", so_what: "s", source: {url: $url}, client_safe: true}} end)' > "$T/$1.json"
}
pass=0; fail=0
check() {   # $1 name, $2 expect OK|FAIL
  local out
  out="$(cd "$SYNC" && python3 -c 'import sys, pathlib; sys.path.insert(0, "."); import sync
sync.REPO = pathlib.Path(sys.argv[1]); sync.MEETINGS = sync.REPO / "none.json"
e = sync.check(sys.argv[2]); print("FAIL: " + "; ".join(e) if e else "OK")' "$T" "$T/$1.json" 2>&1)"
  if [[ "$out" == "$2"* ]]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: $1 — expected $2, got: $out"; fi
}
prep clean     "Asked for the outline per mail 2026-11-03." "";                      check clean     OK
prep web       "VP Ops at Acme (LinkedIn, Oct 2026)." "";                            check web       FAIL
prep url       "Profile at https://ex.org/jane says VP Ops." "";                     check url       FAIL
prep search    "Two web searches found no reliable profile." "";                     check search    FAIL
prep labelled  "External (LinkedIn, 2026-10-01): VP Ops at Acme." "";                check labelled  OK
prep offered   "Asked for the outline per mail 2026-11-03." "https://ex.org/new";    check offered   OK
prep invented  "Asked for the outline per mail 2026-11-03." "https://ex.org/made-up"; check invented FAIL
prep stale     "Asked for the outline per mail 2026-11-03." "https://ex.org/old";    check stale     FAIL

echo "prep-firewall: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
