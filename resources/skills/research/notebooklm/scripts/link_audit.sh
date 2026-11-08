#!/usr/bin/env bash
# link_audit.sh — enforcement gate for the "sync a notebook → wire it into the graph"
# behavior shared by the notebooklm (import) and notebooklm-daily-audio (distill) skills.
#
# For a synced notebook <slug>, asserts the STRUCTURAL backbone that prevents islands
# and enables forward/backward traversal through topic anchors:
#   A) every notebook-source note links to at least one type:topic anchor in projects/
#   B) each such anchor reciprocates a link back to this notebook's dashboard
# People-linking is semantic (can't be mechanically judged "relevant"), so it is printed
# as an ADVISORY, never a hard failure.
#
# Usage:  link_audit.sh <slug> [<slug> ...]
# Run from the vault dir (cbrain/) or the repo root; auto-detects either.
# Exit: 0 = all checks pass · 1 = violations · 2 = usage/vault error.
# No `set -e`: grep -q no-match (exit 1) is normal control flow throughout this script.
set -uo pipefail

if [ "$#" -lt 1 ]; then
  echo "usage: link_audit.sh <slug> [<slug> ...]" >&2; exit 2
fi

# Locate the vault (holds notes/NotebookLM). Honor $VAULT, else try cwd then cwd/cbrain.
VAULT="${VAULT:-}"
if [ -z "$VAULT" ]; then
  if   [ -d "notes/NotebookLM" ];       then VAULT="."
  elif [ -d "cbrain/notes/NotebookLM" ]; then VAULT="cbrain"
  else echo "link_audit: cannot find notes/NotebookLM under cwd or cwd/cbrain" >&2; exit 2; fi
fi
PROJ_DIR="$VAULT/notes/../projects"          # cbrain/projects
DASH_DIR="$VAULT/notes/Dashboards"

# Emit each [[wikilink]] target in a file, normalized: drop alias (|...), heading (#...),
# and any path prefix → bare note name. HTML comments are stripped first so example/placeholder
# links inside <!-- ... --> never count as real links.
wikilinks() {
  perl -0777 -pe 's/<!--.*?-->//gs' "$1" 2>/dev/null \
    | grep -oE '\[\[[^]]+\]\]' \
    | sed -E 's/^\[\[//; s/\]\]$//; s/\|.*$//; s/#.*$//; s@^.*/@@' \
    | sed -E 's/[[:space:]]+$//'
}

# Is note <name> a type:topic anchor in projects/ ? echo its path if so.
topic_path() {
  local f="$PROJ_DIR/$1.md"
  [ -f "$f" ] && grep -qE '^type:[[:space:]]*topic' "$f" && echo "$f"
}

fails=0
for SLUG in "$@"; do
  SRC_DIR="$VAULT/notes/NotebookLM/$SLUG/Sources"
  echo "── notebook: $SLUG ──────────────────────────────"
  if [ ! -d "$SRC_DIR" ]; then
    echo "  FAIL: no Sources/ dir at $SRC_DIR"; fails=$((fails+1)); continue
  fi

  # Dashboard basename for this slug (reciprocity target).
  DASH_NAME=""
  if [ -d "$DASH_DIR" ]; then
    while IFS= read -r d; do
      if grep -qE "^slug:[[:space:]]*\"?$SLUG\"?[[:space:]]*$" "$d"; then
        DASH_NAME="$(basename "$d" .md)"; break
      fi
    done < <(find "$DASH_DIR" -maxdepth 1 -name '*.md')
  fi

  shopt -s nullglob
  src_count=$(find "$SRC_DIR" -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')
  if [ "$src_count" -eq 0 ]; then
    echo "  FAIL: no source notes in $SRC_DIR (import produced nothing to wire)"; fails=$((fails+1)); continue
  fi
  for src in "$SRC_DIR"/*.md; do
    name="$(basename "$src")"
    anchors=()
    while IFS= read -r link; do
      [ -z "$link" ] && continue
      tp="$(topic_path "$link")" || true
      [ -n "$tp" ] && anchors+=("$link|$tp")
    done < <(wikilinks "$src")

    if [ "${#anchors[@]}" -eq 0 ]; then
      echo "  FAIL [A] no topic-anchor link: $name"; fails=$((fails+1)); continue
    fi

    # B) reciprocity: at least one linked anchor must link back to this dashboard.
    recip=0
    for a in "${anchors[@]}"; do
      apath="${a#*|}"; aname="${a%%|*}"
      if [ -n "$DASH_NAME" ] && grep -qF "[[" "$apath" && grep -qF "$DASH_NAME" "$apath"; then
        recip=1
      fi
    done
    if [ "$recip" -eq 0 ]; then
      echo "  FAIL [B] anchor(s) don't link back to dashboard '${DASH_NAME:-<none>}': $name"
      fails=$((fails+1)); continue
    fi
    names="$(for a in "${anchors[@]}"; do echo "${a%%|*}"; done | sort -u | paste -sd, -)"
    echo "  ok: $name → $names"
  done

  # People advisory: which people already sit on the linked anchors.
  for src in "$SRC_DIR"/*.md; do
    while IFS= read -r link; do
      tp="$(topic_path "$link")" || true
      [ -z "$tp" ] && continue
      ppl="$(wikilinks "$tp" | while read -r n; do
               [ -f "$VAULT/Clients/$n.md" ] && grep -qE '^type:[[:space:]]*person' "$VAULT/Clients/$n.md" && echo "$n"
             done | sort -u | paste -sd, -)"
      [ -n "$ppl" ] && echo "  advisory: anchor [[$link]] carries people: $ppl (confirm they're linked to this notebook)"
    done < <(wikilinks "$src")
  done | sort -u
done

echo "────────────────────────────────────────────────"
if [ "$fails" -gt 0 ]; then echo "link_audit: $fails violation(s)"; exit 1; fi
echo "link_audit: PASS — all source notes reach a reciprocating topic anchor"; exit 0
