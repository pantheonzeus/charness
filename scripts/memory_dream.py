#!/usr/bin/env python3
"""Memory consolidation ("dreaming") for the memory dir: a proposed copy, a deterministic verifier, a reviewed apply.

Modelled on Anthropic's Managed Agents dreams: the live store is never edited in place. A consolidator rewrites a
copy, this script verifies it, the principal reads the diff and says yes, and only then does it replace the live
store. The verifier's three checks follow TrustMem (arXiv 2606.25161): coverage, preservation, faithfulness.

  stage [RUN]   copy the live memory dir to RUN/base/ and RUN/proposed/, hashes in RUN/base.sha256
                (RUN defaults to output/.runs/<YYYYMMDD>-memory-dream)
  check RUN     verify RUN/proposed against RUN/base. FAIL lines exit 1; WARN lines go to the reviewer
  diff RUN      unified diff base → proposed
  apply RUN     replace the live memory dir with RUN/proposed, old files kept in RUN/backup/. Refuses inside a
                headless job (CBRAIN_JOB), when check fails, or when the live dir changed since stage

Inside RUN/proposed: merge a file into another by deleting it and listing it in the survivor's
`merged_from: [a.md]` (under metadata:); retire a wrong memory by deleting it and adding a line
`<file> — <reason>` to RUN/retired.txt. Stdlib only.
"""
import datetime as dt
import difflib
import hashlib
import os
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ingest_lint import RX as INJECTION  # noqa: E402
from memory_sweep import MEMORY, frontmatter, unconsolidated  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
INDEX = "MEMORY.md"
INDEX_MAX_LINES = 200   # Claude Code loads only the first 200 lines of MEMORY.md
VOLATILE = re.compile(r"^[ \t]*(modified|originSessionId|node_type|last_verified|merged_from|superseded_by):.*$", re.M)
TOKEN = re.compile(r"https?://[^\s)>\]]+|\[\[[^\]]+\]\]|`[^`\n]+`|\d{4}-\d{2}-\d{2}|€\s?\d[\d.,]*\s?k?"
                   r"|\d[\d.,]*\s?%|\b(?=[0-9a-f]*\d)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b|\b\d[\d,.]*\d\b"
                   r"|(?<![\w.,/-])\d(?![\w%/-]|[.,]\d)")   # bare git hashes; single digits
LIST_MARKER = re.compile(r"^[ \t]*\d+[.)][ \t]", re.M)


def tokens(text):
    """The checkable facts of a memory: dates, numbers, money, URLs, paths/code, wikilinks."""
    return {t.rstrip(".,;:") for t in TOKEN.findall(LIST_MARKER.sub("", VOLATILE.sub("", text)))}


def files(d):
    return {f.name: f.read_text() for f in sorted(Path(d).glob("*.md"))}


def merged_from(text):
    m = re.search(r"^[ \t]*merged_from:(.*)$", text, re.M)
    return set(re.findall(r"[\w.-]+\.md", m.group(1))) if m else set()


def digest(d):
    return {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(Path(d).glob("*.md"))}


def stage(run):
    if run.exists():
        sys.exit(f"{run} exists; pass another RUN path")
    shutil.copytree(MEMORY, run / "base")
    shutil.copytree(MEMORY, run / "proposed")
    (run / "base.sha256").write_text("".join(f"{h}  {n}\n" for n, h in digest(run / "base").items()))
    print(f"staged {len(digest(run / 'base'))} files → {run}/proposed  (edit there, then: check {run})")


def check(run):
    base, prop = files(run / "base"), files(run / "proposed")
    retired = {l.split()[0]: l for l in (run / "retired.txt").read_text().splitlines() if l.strip()} \
        if (run / "retired.txt").exists() else {}
    fail, warn = [], []
    corpus = set().union(*(tokens(t) for t in base.values())) | {dt.date.today().isoformat()}
    for name, text in base.items():
        if name == INDEX:
            continue
        dest = name if name in prop else next((n for n, t in prop.items() if name in merged_from(t)), None)
        if dest is None:
            (warn if name in retired else fail).append(
                f"{name}: " + (f"retired ({retired[name]})" if name in retired else "dropped without merged_from or retired.txt"))
            continue
        lost = tokens(text) - tokens(prop[dest])
        if lost:
            fail.append(f"{name} → {dest}: lost {sorted(lost)}")
    live = set()
    for name, text in prop.items():
        if name == INDEX:
            continue
        fm = frontmatter(text)
        missing = [k for k in ("name", "description", "type") if not fm.get(k)]
        if missing:
            fail.append(f"{name}: frontmatter lacks {missing}")
        if fm.get("superseded_by"):
            if f"{fm['superseded_by'].removesuffix('.md')}.md" not in prop:
                fail.append(f"{name}: superseded_by {fm['superseded_by']} does not exist")
        else:
            live.add(name)
            marks = unconsolidated(text)
            if marks:
                fail.append(f"{name}: inline revision above ## Superseded ({', '.join(marks)})")
        new = tokens(text) - corpus
        if new:
            warn.append(f"{name}: not in any base memory, verify or remove {sorted(new)}")
        for line in text.splitlines():
            if INJECTION.search(line):
                fail.append(f"{name}: instruction-shaped line: {line.strip()[:120]}")
    index = prop.get(INDEX, "")
    linked = set(re.findall(r"\]\(([^)]+\.md)\)", index))
    for problem, names in (("not in MEMORY.md", live - linked), ("superseded or missing but in MEMORY.md", linked - live)):
        if names:
            fail.append(f"{INDEX}: {problem}: {sorted(names)}")
    if len(index.splitlines()) > INDEX_MAX_LINES:
        fail.append(f"{INDEX}: {len(index.splitlines())} lines, only the first {INDEX_MAX_LINES} load")
    for line in fail:
        print(f"FAIL {line}")
    for line in warn:
        print(f"WARN {line}")
    print("OK" if not fail else f"{len(fail)} failure(s)", f"· {len(warn)} warning(s)" if warn else "")
    return not fail


def diff(run):
    base, prop = files(run / "base"), files(run / "proposed")
    for name in sorted(base.keys() | prop.keys()):
        sys.stdout.writelines(difflib.unified_diff(
            base.get(name, "").splitlines(True), prop.get(name, "").splitlines(True),
            f"base/{name}" if name in base else "/dev/null", f"proposed/{name}" if name in prop else "/dev/null"))


def apply(run):
    if os.environ.get("CBRAIN_JOB"):
        sys.exit("apply refused: headless job. Only the principal applies a consolidation.")
    if not check(run):
        sys.exit("apply refused: check failed")
    staged = dict(l.split("  ", 1)[::-1] for l in (run / "base.sha256").read_text().split("\n") if l)
    if digest(MEMORY) != staged:
        sys.exit("apply refused: the live memory dir changed since stage; stage again")
    shutil.copytree(MEMORY, run / "backup")
    prop = files(run / "proposed")
    for name in staged.keys() - prop.keys():
        (MEMORY / name).unlink()
    for name, text in prop.items():
        (MEMORY / name).write_text(text)
    print(f"applied: {len(prop)} files, {len(staged.keys() - prop.keys())} removed; backup in {run}/backup")


def main(argv):
    if not argv or argv[0] not in ("stage", "check", "diff", "apply") or (argv[0] != "stage" and len(argv) < 2):
        sys.exit(__doc__)
    run = Path(argv[1]) if len(argv) > 1 else REPO / "output" / ".runs" / f"{dt.date.today():%Y%m%d}-memory-dream"
    if argv[0] == "check":
        return 0 if check(run) else 1
    {"stage": stage, "diff": diff, "apply": apply}[argv[0]](run)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
