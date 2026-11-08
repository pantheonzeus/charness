#!/usr/bin/env bash
# Regression test for scripts/session_archive.py: redaction, origin, versioning, and tamper detection by `verify`.
# Fixture transcripts under a throwaway HOME. Run: bash .claude/hooks/tests/session-archive.test.sh   (exit 0 = all pass)
set -uo pipefail
SCRIPTS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/scripts"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
export HOME="$T/home" CBRAIN_SESSIONS_ARCHIVE="$T/archive"
P="$HOME/.claude/projects/-fixture"; mkdir -p "$P/s1/subagents"

pass=0; fail=0
ok() { if [ "$2" = "$3" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: $1 — expected $2, got $3"; fi; }
has() { if printf '%s' "$3" | grep -q -- "$2"; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: $1 — no '$2' in: $3"; fi; }
arc() { python3 "$SCRIPTS/session_archive.py" "$@" 2>&1; }
old() { touch -t 202601010000 "$@"; }
idx() { python3 -c "import json,sys;print(json.loads(open('$T/archive/index.jsonl').read().splitlines()[$1])['$2'])"; }

KEY="sk-ant-api03-$(printf 'A%.0s' {1..40})"
cat > "$P/s1.jsonl" <<EOF
{"type":"user","origin":{"kind":"human"},"timestamp":"2026-01-01T10:00:00Z","sessionId":"s1","message":{"role":"user","content":"stop the jarvis app"}}
{"type":"assistant","timestamp":"2026-01-01T10:00:05Z","message":{"content":[{"type":"tool_use","id":"t1","name":"Bash","input":{"command":"export ANTHROPIC_API_KEY=$KEY"}}]}}
{"type":"user","timestamp":"2026-01-01T10:00:06Z","message":{"content":[{"type":"tool_result","tool_use_id":"t1","is_error":true,"content":"ghp_$(printf 'b%.0s' {1..36}) leaked"}]}}
{"type":"assistant","timestamp":"2026-01-01T10:00:07Z","message":{"content":[{"type":"tool_use","id":"t2","name":"WebFetch","input":{"url":"https://example.com"}}]}}
EOF
printf '%s\n' '{"type":"user","timestamp":"2026-01-01T10:00:01Z","message":{"content":"probe prompt"}}' > "$P/s2.jsonl"
printf '%s\n' '{"type":"user","timestamp":"2026-01-01T10:00:02Z","message":{"content":"sub task"}}' > "$P/s1/subagents/agent-a.jsonl"
old "$P/s1.jsonl" "$P/s2.jsonl" "$P/s1/subagents/agent-a.jsonl"

# --- sync: three transcripts, secrets gone, origin + taint recorded
out="$(arc sync)"
has "sync archives all three"          "archived 3 transcript" "$out"
stored="$(gzip -dc "$T/archive/-fixture/s1.jsonl.gz")"
ok  "anthropic key redacted"           "0" "$(printf '%s' "$stored" | grep -c "$KEY")"
has "redaction marker present"         "REDACTED:anthropic" "$stored"
has "github token redacted"            "REDACTED:github" "$stored"
ok  "human origin"                     "human" "$(idx 0 origin)"
ok  "probe is automated"               "automated" "$(idx 1 origin)"
has "taint web recorded"               "web" "$(idx 0 taint)"
ok  "title from first human prompt"    "stop the jarvis app" "$(idx 0 title)"
ok  "subagent keyed to parent"         "s1" "$(idx 2 session_id)"
ok  "archive is owner-only"            "700" "$(stat -f %Lp "$T/archive")"

# --- base64 attachments are not tokens; a quoted refresh token is
TOK="1//0$(printf 'c%.0s' {1..40})"
B64="iVBORw0K1//0$(printf 'd%.0s' {1..40})+/xyz"
printf '%s\n' "{\"type\":\"user\",\"timestamp\":\"2026-01-01T10:00:00Z\",\"message\":{\"content\":\"tok \\\"$TOK\\\" img $B64\"}}" > "$P/s3.jsonl"; old "$P/s3.jsonl"
arc sync >/dev/null
s3="$(gzip -dc "$T/archive/-fixture/s3.jsonl.gz")"
ok  "quoted refresh token redacted"    "0" "$(printf '%s' "$s3" | grep -c "$TOK")"
has "base64 run left intact"           "$B64" "$s3"

# --- idempotent; a resumed session becomes version 2, never an overwrite
has "second sync is a no-op"           "archived 0 transcript" "$(arc sync)"
echo '{"type":"user","origin":{"kind":"human"},"timestamp":"2026-01-02T09:00:00Z","message":{"content":"again"}}' >> "$P/s1.jsonl"; old "$P/s1.jsonl"
has "grown session archived again"     "archived 1 transcript" "$(arc sync)"
ok  "new version number"               "2" "$(idx 4 version)"
ok  "version 1 file kept"              "yes" "$([ -f "$T/archive/-fixture/s1.jsonl.gz" ] && echo yes)"
has "verify clean"                     "OK: 5 entries" "$(arc verify)"

# --- find / show
has "find by text"                     "stop the jarvis app" "$(arc find --text jarvis)"
has "find by origin filters"           "2 session" "$(arc find --origin automated)"
has "show prints the error"            "ERROR  Bash" "$(arc show s1)"

# --- tamper detection
cp "$T/archive/index.jsonl" "$T/index.bak"
python3 - "$T/archive/index.jsonl" <<'PY'
import sys; p = sys.argv[1]; L = open(p).read().splitlines(); L[1] = L[1].replace('"automated"', '"human"'); open(p, "w").write("\n".join(L) + "\n")
PY
has "edited index line caught"         "index line altered" "$(arc verify)"
cp "$T/index.bak" "$T/archive/index.jsonl"
sed -i '' '2d' "$T/archive/index.jsonl"
has "removed index line caught"        "chain broken" "$(arc verify)"
cp "$T/index.bak" "$T/archive/index.jsonl"
echo x | gzip >> "$T/archive/-fixture/s2.jsonl.gz"
has "altered stored file caught"       "s2.jsonl.gz altered" "$(arc verify)"
arc verify >/dev/null; ok "verify exits 1 on tamper" "1" "$?"

echo "session-archive: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
