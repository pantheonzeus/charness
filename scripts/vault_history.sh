#!/usr/bin/env bash
# Private local history of the Obsidian vault (cbrain/). scripts/run_agent.sh snapshots before and
# after every headless run, so each vault change has an author (the job, or "unattributed" for
# you / Obsidian Sync / interactive sessions) and one bad run can be undone with a single revert.
#
# The git dir lives OUTSIDE the synced vault (.vault-history.git at the repo root, gitignored), so
# Obsidian Sync never sees it and git writes nothing into cbrain/ except on a revert/restore.
# It has no remote, and its pre-push hook refuses every push: this history holds client data.
#
# Usage:
#   vault_history.sh snapshot <author> <message> [pathspec...]
#                                                  commit vault changes since the last snapshot, only
#                                                  those under the pathspecs when given (no-op if none)
#   vault_history.sh <git args...>                 any git command against the vault history, e.g.
#       vault_history.sh log --oneline -20                  what changed, by whom
#       vault_history.sh log --author=slack-intel --stat    one job's footprint
#       vault_history.sh show <sha> --stat                  one run's diff
#       vault_history.sh revert --no-edit <sha>             undo one run (writes into cbrain/)
#
# run_agent.sh passes the vault files the run's own Write/Edit calls touched (from its transcript) as
# pathspecs, so a run's commit holds exactly what that run wrote. Everything else that changed in the
# meantime (you, Obsidian, a concurrent job, a job's helper scripts) goes into the next "unattributed"
# snapshot. Only two runs editing the same file at the same moment can still share one commit.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export GIT_DIR="${VAULT_HISTORY_GIT_DIR:-$REPO_ROOT/.vault-history.git}"
export GIT_WORK_TREE="${VAULT_HISTORY_VAULT:-$REPO_ROOT/cbrain}"

[ -d "$GIT_WORK_TREE" ] || { echo "vault_history: no vault at $GIT_WORK_TREE" >&2; exit 1; }

if [ ! -d "$GIT_DIR" ]; then
  git init -q || exit 1
  git config user.name "vault-history"
  git config user.email "vault-history@cbrain.local"
  git config core.quotepath false
  printf '%s\n' '.obsidian/workspace*.json' '.trash/' '.DS_Store' >> "$GIT_DIR/info/exclude"
  printf '%s\n' '#!/bin/sh' 'echo "vault history is local-only (it holds client data): push refused" >&2' 'exit 1' \
    > "$GIT_DIR/hooks/pre-push"
  chmod +x "$GIT_DIR/hooks/pre-push"
fi

if [ "${1:-}" != "snapshot" ]; then
  exec git "$@"
fi

[ $# -ge 3 ] || { echo "usage: vault_history.sh snapshot <author> <message> [pathspec...]" >&2; exit 64; }
# Concurrent jobs snapshot through one OS lock (released if the holder dies).
if [ -z "${VAULT_HISTORY_LOCKED:-}" ] && [ -x /usr/bin/lockf ]; then
  VAULT_HISTORY_LOCKED=1 exec /usr/bin/lockf -k -t 120 "$GIT_DIR/snapshot.lock" bash "${BASH_SOURCE[0]}" "$@"
fi
git add -A -- "${@:4}" || exit 1
git diff --cached --quiet && exit 0
git -c user.name="$2" commit -q -m "$3"
