#!/usr/bin/env bash
# One entry point for every repo check. CI (.github/workflows/ci.yml) runs exactly this, so a green
# local run means a green CI run. Exits non-zero if any check fails; runs them all before exiting.
#
#   hook tests   .claude/hooks/tests/*.test.sh (each exits non-zero on a failed case)
#   skills       frontmatter lint + Agent Skills spec export (errors block, warnings don't)
#   python       ruff, rules and exceptions in ruff.toml
#   shell        shellcheck, error severity
#
# Needs python3, jq and uv (ruff and shellcheck run pinned through uvx).
# Usage: scripts/check.sh
set -uo pipefail
cd "$(dirname "$0")/.."

RUFF=ruff@0.17.4
SHELLCHECK=shellcheck-py==0.11.0.1
failed=()

run() {   # run <label> <command...>
  local label=$1; shift
  printf '== %s\n' "$label"
  if "$@"; then printf -- '-- ok: %s\n\n' "$label"; else printf -- '-- FAILED: %s\n\n' "$label"; failed+=("$label"); fi
}

for t in .claude/hooks/tests/*.test.sh; do run "$(basename "$t" .test.sh)" bash "$t"; done
run "skill frontmatter" python3 resources/skills/vault-hygiene/skill-library-maintenance/scripts/lint_frontmatter.py
run "skill spec export" python3 resources/skills/vault-hygiene/skill-library-maintenance/scripts/spec_export.py check
run "ruff" bash -c "git ls-files -z '*.py' | xargs -0 uvx $RUFF check --quiet"
run "shellcheck" bash -c "git ls-files -z '*.sh' 'scripts/git-hooks/*' | xargs -0 uvx --from $SHELLCHECK shellcheck -S error"

if [ ${#failed[@]} -gt 0 ]; then
  printf 'check: %d failed: %s\n' "${#failed[@]}" "${failed[*]}"
  exit 1
fi
echo "check: all passed"
