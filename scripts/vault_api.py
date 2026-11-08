#!/usr/bin/env python3
"""Typed vault API for agent jobs: the model says what to write, this code does the writing.
The Code Mode pattern (Cloudflare 2025-09; Anthropic "Code execution with MCP" 2025-11) with the model
kept out of the code: one call carries a whole batch, so a job stops spending a turn per Read/Edit.

Writes made through Bash skip the Write/Edit hooks, so this script enforces the same rules itself:
  - only existing .md notes inside cbrain/, symlinks resolved;
  - a headless job (CBRAIN_JOB) only inside the `write_scopes:` of .claude/agents/<job>.md,
    matched like .claude/hooks/write-boundary.sh (case-insensitive, `*` crosses `/`);
  - a job never writes a `confirmed:` line: confirmation is the principal's (Charter §6 trust tier);
  - every note it writes keeps or gets a `provenance:` label (scripts/ingest_lint.py). It cannot see the
    session's transcript, so it labels whenever the note has none: over-labelling is the safe direction;
  - all-or-nothing: every op is checked before the first write;
  - each write is logged to output/.runs/_forensics/vault_api.jsonl with CBRAIN_RUN, so run_agent.sh
    files it under the job's vault-history commit.

  python3 scripts/vault_api.py find <email-or-name>...   person notes in cbrain/Clients, as JSON
  python3 scripts/vault_api.py apply <batch.json>        apply a batch; prints JSON, exit 1 when refused

batch.json: {"ops": [{"op": "append", "note": "notes/20261028-X.md", "under": "## My Notes",
                      "text": "### Meeting Prep — {now}\\n- goal: ..."}]}
  note   path relative to cbrain/ (an existing note; this API never creates notes)
  under  optional heading: the text goes at the end of that section, or the heading is added at the end
  text   markdown; {now} {date} {time} are replaced with local time. Text already in the note is skipped.
Stdlib only.
"""
import datetime as dt
import fnmatch
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = (REPO / "cbrain").resolve()
LOG = REPO / "output" / ".runs" / "_forensics" / "vault_api.jsonl"
sys.path.insert(0, str(REPO / "scripts"))
import ingest_lint  # noqa: E402  provenance labels, shared with the Write/Edit hook


def scopes(job):
    """The job's write_scopes, or None when it has none (then the vault as a whole is the boundary)."""
    f = REPO / ".claude" / "agents" / f"{job}.md"
    if not job or not f.is_file():
        return None
    head = ingest_lint.head_of(f.read_text(errors="ignore")) or ""
    m = re.search(r"^write_scopes:\s*\n((?:[ \t]+-.*\n?)*)", head, re.M)
    pats = [p.strip().strip("\"'") for p in re.findall(r"-\s*(.+)", m.group(1))] if m else []
    return pats or None


def in_scope(path, pats):
    rel = str(path.relative_to(REPO)).lower()
    for p in pats:
        if p.startswith("~/"):
            p = str(Path.home()) + p[1:]
        if fnmatch.fnmatchcase(str(path).lower() if p.startswith("/") else rel, p.lower()):
            return True
    return False


def resolve(note):
    path = (VAULT / note).resolve()
    if VAULT not in path.parents:
        return None, f"{note}: outside the vault"
    if path.suffix != ".md" or not path.is_file():
        return None, f"{note}: not an existing .md note (this API never creates notes)"
    return path, None


def fill(text, now):
    return (text.replace("{now}", now.strftime("%Y-%m-%d %H:%M"))
                .replace("{date}", now.strftime("%Y-%m-%d")).replace("{time}", now.strftime("%H:%M")))


def level(line):
    m = re.match(r"(#{1,6}) ", line)
    return len(m.group(1)) if m else 0


def insert(body, under, text):
    """Body with text at the end of the `under` section (or a new section at the end)."""
    lines, add = body.rstrip("\n").split("\n"), text.strip("\n").split("\n")
    head = next((i for i, l in enumerate(lines) if under and l.strip() == under.strip()), None)
    if head is None:
        return "\n".join(lines + [""] + ([under] if under else []) + add) + "\n"
    end = next((i for i in range(head + 1, len(lines)) if 0 < level(lines[i]) <= level(under)), len(lines))
    last = end
    while last > head + 1 and not lines[last - 1].strip():
        last -= 1
    gap = [""] if level(add[0]) or (last > head + 1 and level(lines[last - 1])) else []
    tail = [""] if end < len(lines) else []
    return "\n".join(lines[:last] + gap + add + tail + lines[end:]) + "\n"


def apply(batch, job, run, now):
    ops = batch.get("ops") if isinstance(batch, dict) else None
    if not isinstance(ops, list) or not ops:
        return {"ok": False, "errors": ["batch needs a non-empty \"ops\" list"]}
    pats, errors, plan = scopes(job), [], []
    for n, op in enumerate(ops):
        where = f"ops[{n}]"
        if not isinstance(op, dict) or op.get("op") != "append":
            errors.append(f"{where}: unknown op (only \"append\")")
            continue
        text, under = str(op.get("text") or "").strip(), op.get("under")
        if not text:
            errors.append(f"{where}: empty text")
        if job and re.search(r"(?im)^[ \t]*confirmed:", text):
            errors.append(f"{where}: a job may not write a 'confirmed:' line; only the principal confirms a note")
        if under is not None and not level(str(under)):
            errors.append(f"{where}: under must be a markdown heading, e.g. \"## Notes\"")
        path, err = resolve(str(op.get("note") or ""))
        if err:
            errors.append(f"{where}: {err}")
        elif pats is not None and not in_scope(path, pats):
            errors.append(f"{where}: {path.relative_to(REPO)} is outside job '{job}' write_scopes ({' '.join(pats)})")
        else:
            plan.append((path, under, fill(text, now)))
    if errors:
        return {"ok": False, "errors": errors, "written": []}
    results, by = [], f"{job or 'interactive'} (vault_api)"
    for path, under, text in plan:
        body = path.read_text(errors="ignore")
        if text in body:
            results.append({"note": str(path.relative_to(VAULT)), "result": "skipped (already there)"})
            continue
        path.write_text(insert(body, under, text))
        labelled = ingest_lint.provenance(path) is None and ingest_lint.label(
            path, {"job-input"} if ingest_lint.agent_ingests(job) else {"unknown-session"}, by)
        results.append({"note": str(path.relative_to(VAULT)), "result": "appended" + (", labelled" if labelled else "")})
        try:
            LOG.parent.mkdir(parents=True, exist_ok=True)
            with LOG.open("a") as f:
                f.write(json.dumps({"ts": now.isoformat(timespec="seconds"), "job": job or None, "run": run or None,
                                    "path": str(path.relative_to(REPO))}) + "\n")
        except OSError:
            pass   # the log is for attribution; a failed log line never undoes a write
    return {"ok": True, "errors": [], "written": results}


def find(queries):
    notes = sorted((VAULT / "Clients").glob("*.md"))
    texts = {p: p.read_text(errors="ignore").lower() for p in notes}
    out = {}
    for q in queries:
        k = q.strip().lower()
        if "@" in k:
            hits = [p for p in notes if k in texts[p]]
        else:
            hits = [p for p in notes if p.stem.lower() == k or re.search(
                r"^aliases:.*[\"'\[, ]" + re.escape(k) + r"[\"'\], ]", ingest_lint.head_of(texts[p]) or "", re.M)]
        out[q] = [str(p.relative_to(VAULT)) for p in hits]
    return out


def main(argv):
    if len(argv) >= 2 and argv[0] == "find":
        print(json.dumps(find(argv[1:]), ensure_ascii=False, indent=1))
        return 0
    if len(argv) == 2 and argv[0] == "apply":
        try:
            batch = json.loads(Path(argv[1]).read_text())
        except (OSError, ValueError) as e:
            print(json.dumps({"ok": False, "errors": [f"cannot read batch: {e}"]}))
            return 1
        res = apply(batch, os.environ.get("CBRAIN_JOB", ""), os.environ.get("CBRAIN_RUN", ""), dt.datetime.now())
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return 0 if res["ok"] else 1
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
