#!/usr/bin/env bash
# Regression test for scripts/commit_guard.py and scripts/git-hooks/{pre-commit,pre-push}. A throwaway repo with a bare
# remote; every fake secret is assembled at run time so this tracked file carries none.
# Run: bash .claude/hooks/tests/commit-guard.test.sh   (exit 0 = all pass)
set -uo pipefail
REAL="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
GUARD="$REAL/scripts/commit_guard.py"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
export GIT_CONFIG_GLOBAL="$T/gitconfig" GIT_CONFIG_NOSYSTEM=1
git config --global user.name tester; git config --global user.email tester@users.noreply.github.com
git config --global init.defaultBranch main
git init -q --bare "$T/remote.git"; git init -q "$T/w"; cd "$T/w" || exit 2
git config core.hooksPath "$REAL/scripts/git-hooks"; git remote add origin "$T/remote.git"
printf 'ignored/\n' > .gitignore; printf '# Security\nReport to security-contact@example.com\n' > SECURITY.md
git add -A; git commit -qm init && git push -q origin main 2>/dev/null

pass=0; fail=0
ok() { if [ "$2" = "$3" ]; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL: $1 — expected $2, got $3"; fi; }
try() {   # $1 name, $2 expect pass|block, $3 file, $4 content
  mkdir -p "$(dirname "$3")"; printf '%s\n' "$4" > "$3"; git add -f "$3"
  if git diff --cached --quiet; then fail=$((fail+1)); echo "FAIL: $1 — nothing staged, test is vacuous"; return; fi
  if git commit -qm "test: $1" >/dev/null 2>"$T/err"; then ok "$1" "$2" pass; git reset -q --soft HEAD~1; else ok "$1" "$2" block; fi
  git reset -q; rm -f "$3"
}
AWS="AKIA""ABCDEFGHIJKLMNOP"; GH="ghp_""aB3dE5gH7jK9""mN1pQ3sT5v""X7zA9cE1gI3kM5"
PK="-----BEGIN ""RSA PRIVATE KEY-----"; SLK="xoxb-""123456789012-abcdefghijkl"
GKEY="AIza""SyA1b2C3d4E5f6G7""h8I9j0KlMnOpQrStUvW"; ANT="sk-ant-""api03-abcdefghijklm""nopqrstuvwxyz012345"
JWT="eyJhbGciOiJIUzI1NiJ9"".eyJzdWIiOiIxMjM0NTY3ODkwIn0"".dozjgNryP4J3jVmN""Hl0w5N_XgL0n3I9PlFUP0THsR8U"
RP="real.person""@gmail.com"; ME="someone.real""@gmail.com"; TEL="+49 171"" 2345678"; HP="/Users/""jdoe/projects/x"
UC="https://admin:"; UC="${UC}s3cr3tpass""@db.internal.io/x"

try "clean text"                       pass a.md   "Plain prose about agent harnesses."
try "aws access key"                   block a.py  "key = '$AWS'"
try "github token"                     block a.py  "TOKEN = '$GH'"
try "private key block"                block a.txt "$PK"
try "slack token"                      block a.py  "s = '$SLK'"
try "google api key"                   block a.js  "const k = '$GKEY';"
try "anthropic key"                    block a.sh  "export X=$ANT"
try "jwt"                              block a.md  "Authorization: $JWT"
try "password assignment"              block a.py  "db_password = \"hunter2hunter2\""
try "password placeholder passes"      pass a.py   "db_password = \"<your-password>\""
try "env lookup passes"                pass a.py   "token = os.environ[\"API_TOKEN\"]"
try "run path next to a key word passes" pass a.md "token log: output/.runs/upgrade-20261104-0837-upgrade-3-deliver-a-memory-s-body/"
try "url with credentials"             block a.cfg "url = $UC"
try "personal email"                   block a.md  "Mail me at $ME"
try "example email passes"             pass a.md   "Mail jane@example.com"
try "SECURITY.md contact passes"       pass a.md   "Report to security-contact@example.com"
try "phone number"                     block a.md  "Call $TEL today"
try "home path"                        block a.md  "see $HP"
try "placeholder home path passes"     pass a.md   "see /Users/<you>/projects/x"
try "bidi control"                     block a.py  "$(printf 'x = 1 \xe2\x80\xae # hidden')"
try "conflict marker"                  block a.md  "<<<<<<< HEAD"
try ".env file"                        block .env  "A=1"
try ".env.example passes"              pass .env.example "A=<value>"
try "credentials json"                 block credentials.json "{}"
try "force-added ignored file"         block ignored/n.md "note"
dd if=/dev/zero of=big.bin bs=1048576 count=6 2>/dev/null; git add big.bin
git commit -qm big >/dev/null 2>&1 && { ok "file over 5 MB" block pass; git reset -q --soft HEAD~1; } || ok "file over 5 MB" block block
git reset -q; rm -f big.bin
grep -q "$AWS" "$T/err" 2>/dev/null; ok "secret is masked in output" 1 $?
try "aws key" block a.py "key = '$AWS'"; grep -q "AKIA\*" "$T/err"; ok "masked form shown" 0 $?

# Names: an account from the real vault, read at run time (no client name in this file).
ACC="$(grep -l "^type: account" "$REAL"/cbrain/Clients/*.md 2>/dev/null | head -1 | xargs -I{} basename {} .md)"
if [ -n "$ACC" ]; then try "client account name" block a.md "We built this for $ACC last year."; fi

# Identity
git -c user.email=$RP commit -q --allow-empty -m x >/dev/null 2>&1 && { ok "non-noreply author" block pass; git reset -q --soft HEAD~1; } || ok "non-noreply author" block block

# Push: clean fast-forward passes; a secret committed past the hook is caught; force push and archive refs blocked.
printf 'ok\n' > b.md; git add b.md; git commit -qm clean; git push -q origin main 2>/dev/null; ok "clean push" 0 $?
printf "k = '%s'\n" "$AWS" > c.py; git add c.py; git commit -q --no-verify -m sneaky
git push -q origin main 2>/dev/null; ok "secret in outgoing commit blocks push" 1 $?
git reset -q --hard HEAD~1
git commit -q --no-verify -m "Co-Authored-By: someone <$RP>" --allow-empty
git push -q origin main 2>/dev/null; ok "personal email in commit message blocks push" 1 $?
git reset -q --hard HEAD~1
git commit -q --amend -m "rewritten" --no-verify; git push -q --force origin main 2>/dev/null; ok "force push blocked" 1 $?
git reset -q --hard origin/main; git branch -q archive/x; git push -q origin archive/x 2>/dev/null; ok "archive ref blocked" 1 $?
git push -q origin :main 2>/dev/null; ok "remote branch deletion blocked" 1 $?

# Claude PreToolUse hook
h() { jq -cn --arg c "$1" '{tool_name:"Bash", tool_input:{command:$c}}' | python3 "$GUARD" hook | grep -q '"deny"' && echo deny || echo allow; }
ok "hook: --no-verify"            deny  "$(h 'git commit --no-verify -m x')"
ok "hook: commit -n"              deny  "$(h 'git commit -n -m x')"
ok "hook: push --force"           deny  "$(h 'git push --force origin main')"
ok "hook: push -f via -C"         deny  "$(h 'git -C /tmp/x push -f origin main')"
ok "hook: +refspec"               deny  "$(h 'git push origin +main')"
ok "hook: unset hooksPath"        deny  "$(h 'git config --unset core.hooksPath')"
ok "hook: -c hooksPath"           deny  "$(h 'git -c core.hooksPath=/dev/null commit -m x')"
ok "hook: push archive"           deny  "$(h 'git push origin archive/2026-07')"
ok "hook: plain push"             allow "$(h 'git push origin public:main')"
ok "hook: plain commit"           allow "$(h 'git add -A && git commit -m "Fix -- docs"')"
ok "hook: install hooksPath"      allow "$(h 'git config core.hooksPath scripts/git-hooks')"
ok "hook: install, quoted in text" allow "$(h "echo \"(git hooks in scripts/git-hooks/, \`git config core.hooksPath scripts/git-hooks\`);\"")"
ok "hook: escaped path suffix"    deny  "$(h 'git config core.hooksPath scripts/git-hooks\x')"
ok "hook: install then unset"     deny  "$(h 'git config core.hooksPath scripts/git-hooks && git config --unset core.hooksPath')"
ok "hook: hooksPath elsewhere"    deny  "$(h 'git config core.hooksPath /tmp/nohooks')"
ok "hook: hooksPath prefix trick" deny  "$(h 'git config core.hooksPath scripts/git-hooks-off')"
ok "hook: non-git command"        allow "$(h 'ls -la')"

echo "commit-guard: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
