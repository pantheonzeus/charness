#!/usr/bin/env bash
# Regression test for scripts/packet_lint.py (delegation packets: constraints verbatim in, checked out).
# Run: bash .claude/hooks/tests/packet-lint.test.sh   (exit 0 = all pass)
set -uo pipefail
LINT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../scripts" && pwd)/packet_lint.py"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
pass=0; fail=0
expect() {   # $1 name, $2 expected exit code, $3 mode, $4 folder
  python3 "$LINT" "$3" "$4" >/dev/null 2>&1; local rc=$?
  if [ "$rc" = "$2" ]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL: $1 — expected exit $2, got $rc"; fi
}
task() { mkdir -p "$T/$1"; printf '# Task\n\n## Constraints\n- Write only children/%s/RESPONSE.md.\n- Never name a client in a web query.\n\n## Question\nx\n' "$1" > "$T/$1/TASK.md"; }

mkdir -p "$T/none"; printf '# Task\n\n## Question\nx\n' > "$T/none/TASK.md"
expect "packet without constraints"        1 task  "$T/none"
task ok;      expect "packet with constraints"   0 task  "$T/ok"
printf '## Findings\nx\n\n## Constraints checked\n- Write only children/ok/RESPONSE.md. — kept\n- Never name a client in a web query. — not applicable\n' > "$T/ok/RESPONSE.md"
expect "all echoed, none broken"           0 check "$T/ok"
task para;    printf '## Constraints checked\n- Only write my RESPONSE. — kept\n- Never name a client in a web query. — kept\n' > "$T/para/RESPONSE.md"
expect "paraphrased constraint"            1 check "$T/para"
task broke;   printf '## Constraints checked\n- Write only children/broke/RESPONSE.md. -- kept\n- Never name a client in a web query. — broken: one query named the account\n' > "$T/broke/RESPONSE.md"
expect "broken constraint reported"        2 check "$T/broke"
task noecho;  printf '## Findings\nx\n' > "$T/noecho/RESPONSE.md"
expect "no Constraints checked section"    1 check "$T/noecho"
task noresp;  expect "no RESPONSE.md"      1 check "$T/noresp"
echo "packet-lint: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
