#!/usr/bin/env bash
# M4 mechanical guard — Algo Hygiene floor.
# Usage: hygiene_check.sh <path-to-post.md>
# Exit 0 = clean (0 outbound links, <=3 hashtags). Exit 1 = violation. Exit 2 = usage error.
# Prints: "links=<n> hashtags=<n> verdict=<pass|fail>"

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: hygiene_check.sh <path-to-post.md>" >&2
  exit 2
fi

post_file="$1"
if [[ ! -f "$post_file" ]]; then
  echo "error: file not found: $post_file" >&2
  exit 2
fi

# Count outbound links: http://, https://, or bare www.
# grep exits 1 on "no match", which is a valid zero-count result, not an error —
# guard each pipeline with `|| true` so `set -e` doesn't abort the script on a clean post.
link_count=$(grep -oE '(https?://|www\.)[^[:space:])"'"'"']+' "$post_file" | wc -l | tr -d ' ' || true)
link_count=${link_count:-0}

# Count hashtags: a '#' immediately followed by a word character, not preceded by one
# (avoids matching markdown headings like "# Heading" or "## Section").
hashtag_count=$(grep -oE '(^|[^[:alnum:]#])#[A-Za-z][A-Za-z0-9_]*' "$post_file" | wc -l | tr -d ' ' || true)
hashtag_count=${hashtag_count:-0}

verdict="pass"
status=0

if [[ "$link_count" -gt 0 ]]; then
  verdict="fail"
  status=1
fi

if [[ "$hashtag_count" -gt 3 ]]; then
  verdict="fail"
  status=1
fi

echo "links=${link_count} hashtags=${hashtag_count} verdict=${verdict}"
exit "$status"
