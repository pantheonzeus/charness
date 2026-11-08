#!/usr/bin/env bash
# Regression test for scripts/vault_api.py: the typed vault writer that holds Bash-run writes to the same
# write_scopes and provenance rules as the Write/Edit hooks.
# Hermetic: builds a throwaway repo with fixture notes; never touches the real vault.
# Run: bash .claude/hooks/tests/vault-api.test.sh   (exit 0 = all pass)
set -uo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/scripts"
FAKE="$(mktemp -d)"; trap 'rm -rf "$FAKE"' EXIT
FAKE="$(cd "$FAKE" && pwd -P)"
V="$FAKE/cbrain"
mkdir -p "$FAKE/scripts" "$V/notes" "$V/Clients" "$V/projects" "$FAKE/.claude/agents" "$FAKE/output" "$FAKE/outside"
cp "$SRC/vault_api.py" "$SRC/ingest_lint.py" "$FAKE/scripts/"
API="$FAKE/scripts/vault_api.py"
printf -- '---\nname: prep\nuntrusted_ingest: true\nwrite_scopes:\n  - "cbrain/notes/????????-*.md"\n  - "cbrain/Clients/*.md"\n---\n' > "$FAKE/.claude/agents/prep.md"
printf -- '---\nname: plain\n---\n' > "$FAKE/.claude/agents/plain.md"
printf -- '---\ntype: meeting\n---\n\n# Meeting\n\n## Notes\nagenda\n\n## My Notes\n\n## Next Steps\n- x\n' > "$V/notes/20261028-Kickoff.md"
printf -- '---\naliases: ["Doe, Jane", "J. Doe"]\ntype: person\n---\n# Jane Doe\n**Email:** jane@acme.com\n\n## Notes\n- old fact\n\n## Links\n' > "$V/Clients/Jane Doe.md"
printf -- '---\nprovenance: untrusted-ingest\n---\n# Topic\n' > "$V/projects/Topic.md"
printf 'secret\n' > "$FAKE/outside/x.md"
ln -s "$FAKE/outside/x.md" "$V/notes/20261028-Link.md"

pass=0; fail=0
check() { if [ "$2" = "$3" ]; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL: $1 — expected [$3] got [$2]"; fi; }
batch() { printf '%s' "$1" > "$FAKE/b.json"; CBRAIN_JOB="${2:-}" CBRAIN_RUN="${3:-}" python3 "$API" apply "$FAKE/b.json"; }
ok() { python3 -c 'import json,sys; print(json.load(sys.stdin)["ok"])'; }
prov() { sed -n 's/^provenance: //p' "$1" | head -1; }

# 1. Append under a heading in the middle of the note: lands at the end of that section, next section kept
out="$(batch '{"ops":[{"op":"append","note":"notes/20261028-Kickoff.md","under":"## My Notes","text":"### Meeting Prep — {now}\n- goal"}]}' prep run-1)"
check "append ok" "$(printf '%s' "$out" | ok)" "True"
check "block under My Notes" "$(awk '/^## My Notes/{f=1;next} /^## /{f=0} f' "$V/notes/20261028-Kickoff.md" | grep -c '^### Meeting Prep — 20[0-9][0-9]-')" "1"
check "next section intact" "$(grep -A1 '^## Next Steps' "$V/notes/20261028-Kickoff.md" | tail -1)" "- x"
check "{now} filled" "$(grep -c '{now}' "$V/notes/20261028-Kickoff.md")" "0"
check "labelled job-input" "$(prov "$V/notes/20261028-Kickoff.md")" "derived-untrusted"
check "derived_from job-input" "$(sed -n 's/^derived_from: //p' "$V/notes/20261028-Kickoff.md")" "[job-input]"
check "attribution log" "$(grep -c '"run": "run-1", "path": "cbrain/notes/20261028-Kickoff.md"' "$FAKE/output/.runs/_forensics/vault_api.jsonl")" "1"

# 2. Same text again → skipped, not duplicated
batch '{"ops":[{"op":"append","note":"Clients/Jane Doe.md","under":"## Notes","text":"- 2026-10-27 · new fact"}]}' prep >/dev/null
out="$(batch '{"ops":[{"op":"append","note":"Clients/Jane Doe.md","under":"## Notes","text":"- 2026-10-27 · new fact"}]}' prep)"
check "idempotent" "$(grep -c 'new fact' "$V/Clients/Jane Doe.md")" "1"
check "skip reported" "$(printf '%s' "$out" | grep -c 'skipped')" "1"
check "bullet joins list" "$(awk '/^## Notes/{f=1;next} /^## /{f=0} f' "$V/Clients/Jane Doe.md" | grep -c '^- ')" "2"

# 3. Missing heading → added at the end
batch '{"ops":[{"op":"append","note":"Clients/Jane Doe.md","under":"## Meetings","text":"- [[20261028-Kickoff]]"}]}' prep >/dev/null
check "new heading at end" "$(tail -2 "$V/Clients/Jane Doe.md" | head -1)" "## Meetings"

# 4. Scope: a note outside the job's write_scopes refuses the WHOLE batch (all-or-nothing)
before="$(cat "$V/notes/20261028-Kickoff.md")"
out="$(batch '{"ops":[{"op":"append","note":"notes/20261028-Kickoff.md","text":"should not land"},{"op":"append","note":"projects/Topic.md","text":"x"}]}' prep)"; rc=$?
check "out of scope refused" "$(printf '%s' "$out" | ok)" "False"
check "exit 1 on refusal" "$rc" "1"
check "scope named" "$(printf '%s' "$out" | grep -c 'outside job')" "1"
check "nothing written" "$(cat "$V/notes/20261028-Kickoff.md")" "$before"

# 5. Job without write_scopes, and interactive: whole vault allowed; an existing label is kept
check "no-scope job ok" "$(batch '{"ops":[{"op":"append","note":"projects/Topic.md","text":"- a"}]}' plain | ok)" "True"
check "ingest label kept" "$(prov "$V/projects/Topic.md")" "untrusted-ingest"
check "interactive ok" "$(batch '{"ops":[{"op":"append","note":"Clients/Jane Doe.md","text":"- b"}]}' | ok)" "True"

# 6. Escapes and bad input
check "dotdot refused" "$(batch '{"ops":[{"op":"append","note":"../outside/x.md","text":"x"}]}' | ok)" "False"
check "symlink out refused" "$(batch '{"ops":[{"op":"append","note":"notes/20261028-Link.md","text":"x"}]}' | ok)" "False"
check "outside file intact" "$(cat "$FAKE/outside/x.md")" "secret"
check "missing note refused" "$(batch '{"ops":[{"op":"append","note":"notes/20261028-New.md","text":"x"}]}' | ok)" "False"
check "unknown op refused" "$(batch '{"ops":[{"op":"write","note":"projects/Topic.md","text":"x"}]}' | ok)" "False"
check "bad heading refused" "$(batch '{"ops":[{"op":"append","note":"projects/Topic.md","under":"Notes","text":"x"}]}' | ok)" "False"
check "empty batch refused" "$(batch '{"ops":[]}' | ok)" "False"
check "job confirmed: refused" "$(batch '{"ops":[{"op":"append","note":"projects/Topic.md","text":"confirmed: 2026-10-29"}]}' plain | ok)" "False"

# 7. find: by email, by alias, by file name; misses are empty
f="$(python3 "$API" find jane@acme.com 'doe, jane' 'Jane Doe' nobody@x.com)"
check "find email" "$(printf '%s' "$f" | python3 -c 'import json,sys; print(json.load(sys.stdin)["jane@acme.com"])')" "['Clients/Jane Doe.md']"
check "find alias" "$(printf '%s' "$f" | python3 -c 'import json,sys; print(json.load(sys.stdin)["doe, jane"])')" "['Clients/Jane Doe.md']"
check "find name" "$(printf '%s' "$f" | python3 -c 'import json,sys; print(json.load(sys.stdin)["Jane Doe"])')" "['Clients/Jane Doe.md']"
check "find miss" "$(printf '%s' "$f" | python3 -c 'import json,sys; print(json.load(sys.stdin)["nobody@x.com"])')" "[]"

echo "vault_api: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
