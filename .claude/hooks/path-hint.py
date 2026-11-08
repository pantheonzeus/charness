#!/usr/bin/env python3
"""PostToolUseFailure hook: answer a missed Read/Edit path with what actually exists.

When a Read or Edit fails because the file does not exist, name the deepest existing
ancestor directory, its closest name matches (difflib) and up to 15 of its entries, as
additionalContext next to the error. Only paths inside $CLAUDE_PROJECT_DIR get a hint
(no listing of ~/ lands in a transcript). Under the vault (cbrain/) only the closest
matches are named, never a directory listing. Every other failure: silent exit 0.
Stdlib only; never blocks (PostToolUseFailure cannot block anyway).
"""
import difflib
import json
import os
import sys

MAX_ENTRIES = 15     # entries shown
MAX_SCAN = 2000      # entries read from one directory, bounds latency on huge dirs
MISS_MARKERS = ("does not exist", "no such file")
VAULT_DIR = "cbrain"
CUTOFF = 0.5         # difflib similarity for a closest-match outside the vault
VAULT_CUTOFF = 0.8   # inside it: near-identical names only


def hint(data):
    if data.get("tool_name") not in ("Read", "Edit"):
        return None
    err = str(data.get("error") or "").lower()
    if not any(m in err for m in MISS_MARKERS):
        return None
    path = (data.get("tool_input") or {}).get("file_path")
    root = os.environ.get("CLAUDE_PROJECT_DIR")
    if not path or not root:
        return None
    root = os.path.realpath(root)
    path = os.path.normpath(os.path.join(data.get("cwd") or root, path))

    # Deepest existing ancestor, and the first missing component below it.
    anc, missing = path, ""
    while not os.path.isdir(anc):
        parent = os.path.dirname(anc)
        if parent == anc:
            return None
        missing, anc = os.path.basename(anc), parent
    anc = os.path.realpath(anc)
    if anc != root and not anc.startswith(root + os.sep):
        return None
    if not missing:   # the path itself is an existing directory, not a miss we can help with
        return None

    names = []
    with os.scandir(anc) as it:
        for i, e in enumerate(it):
            if i >= MAX_SCAN:
                break
            names.append(e.name + ("/" if e.is_dir(follow_symlinks=False) else ""))
    names.sort()
    rel_anc = os.path.relpath(anc, root)
    rel_anc = "." if rel_anc == "." else rel_anc + "/"
    in_vault = rel_anc == VAULT_DIR + "/" or rel_anc.startswith(VAULT_DIR + "/")
    # Vault notes share date prefixes, so a loose cutoff would name unrelated people's notes.
    cutoff = VAULT_CUTOFF if in_vault else CUTOFF
    closest = difflib.get_close_matches(missing, names, n=5, cutoff=cutoff)
    closest += [n for n in difflib.get_close_matches(missing + "/", names, n=5, cutoff=cutoff) if n not in closest]
    closest = closest[:5]

    msg = f"Path not found. Nearest existing dir: {rel_anc} (missing: {missing})."
    msg += " Closest: " + (", ".join(closest) if closest else "none") + "."
    if not in_vault:
        rest = [n for n in names if n not in closest]
        shown = rest[:max(0, MAX_ENTRIES - len(closest))]
        more = f" (+{len(names) - len(closest) - len(shown)} more)" if len(names) > len(closest) + len(shown) else ""
        msg += " Entries: " + (", ".join(shown) if shown else "none") + more + "."
    msg += " List the directory before guessing again."
    return msg


def main():
    try:
        data = json.load(sys.stdin)
        msg = hint(data)
    except Exception:
        return 0
    if msg:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUseFailure",
                                                 "additionalContext": msg}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
