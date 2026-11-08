"""Per-job quality: did a run do the work its own skill says every run must do? (Plus, for every job, how much of
its research it repeated: efficiency().)

forensics.py sees failures (blocked calls, missing handoffs). A run can be clean by those measures and still
under-deliver: on Sonnet 5.5 the daily-intel runs got 75% cheaper by searching a third as much and shipping
1-3 items (2026-10-26..30). This module measures each run of a listed job from its transcript (subagents
included) and the files it wrote, and checks it against floors taken word for word from the job's SKILL.md.
A run below a floor gets the tracked code QUALITY_FLOOR in forensics, so recurrence, the console pill and
fix verification work as for any other code. Volume (items, domains) is reported per model, never a floor:
a quiet news day is allowed to be short ("Never pad").

Code only, no LLM judge (SKILL.md: rules before judges). Stdlib, Python 3.9.
"""
import fnmatch
import json
import re
import shlex
from pathlib import Path
from urllib.parse import urlsplit

REPO = Path(__file__).resolve().parents[5]
LONG_VALUE_FLAGS = ("--include", "--exclude", "--exclude-dir", "--regexp", "--file", "--max-count",
                    "--after-context", "--before-context")


def calls(path):
    """(tool, input) for every tool call of a run, in order, its subagents' calls after the main ones. A transcript
    can log the same call twice (seen on meeting-prep, 2026-10-30), so each call id counts once."""
    out, seen = [], set()
    for p in [path, *sorted(path.with_suffix("").glob("subagents/*.jsonl"))]:
        for line in p.read_text(errors="replace").splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            content = (e.get("message") or {}).get("content")
            for b in content if isinstance(content, list) else []:
                if b.get("type") == "tool_use" and b.get("id") not in seen:
                    seen.add(b.get("id"))
                    out.append((b.get("name", "?"), b.get("input") or {}))
    return out


def launch(path):
    """The launch prompt: the first user message, i.e. what the run was told to do."""
    for line in path.read_text(errors="replace").splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("type") == "user":
            c = (e.get("message") or {}).get("content")
            return c if isinstance(c, str) else " ".join(b.get("text", "") for b in c or [] if isinstance(b, dict))
    return ""


def written(cs, pattern):
    """Final text of every file the run wrote whose path matches, rebuilt from its own Write and Edit calls,
    so a later run overwriting the file doesn't change this run's measurement. A file the run only edited is
    read from disk."""
    files = {}
    for name, inp in cs:
        f = str(inp.get("file_path", ""))
        if not re.search(pattern, f):
            continue
        if name == "Write":
            files[f] = inp.get("content", "")
        elif name == "Edit" and files.get(f) is not None:
            old, new = inp.get("old_string", ""), inp.get("new_string", "")
            files[f] = files[f].replace(old, new) if inp.get("replace_all") else files[f].replace(old, new, 1)
        elif name == "Edit":
            files[f] = None
    for f, text in files.items():
        if text is None:
            try:
                files[f] = Path(f).read_text()
            except OSError:
                files[f] = ""
    return files


def loads(text):
    try:
        return json.loads(text)
    except ValueError:
        return None


def url_key(u):
    s = urlsplit(u.strip())
    return (s.netloc.lower().removeprefix("www.") + s.path.rstrip("/")).lower()


def count(cs, *tools):
    return sum(1 for name, _ in cs if name in tools)


def grepped(inp, doc):
    """Did this Grep search the document: its path is the file, or a directory holding it with no glob or a glob
    (one {a,b} brace level) that matches the file name."""
    p = str(inp.get("path", "")).rstrip("/").removeprefix(str(REPO) + "/")
    if p.endswith(doc):
        return True
    if not p or not doc.startswith(p + "/"):
        return False
    g = inp.get("glob")
    if not g:
        return True
    m = re.search(r"\{([^}]*)\}", g)
    alts = [g[:m.start()] + a + g[m.end():] for a in m.group(1).split(",")] if m else [g]
    return any(fnmatch.fnmatch(Path(doc).name, a) for a in alts)


def grep_inputs(cmd):
    """The {path, glob} entries grepped() reads for a Bash command that starts with grep, one per path argument; a
    --include or an unexpanded shell wildcard becomes the glob. [] for any other command, one shlex cannot parse, or
    grep -c "" (an empty pattern counts lines, it searches nothing). Flags may follow the paths (seen in transcripts)."""
    try:
        args = shlex.split(cmd)
    except ValueError:
        return []
    if args[:1] != ["grep"]:
        return []
    words, patterns, includes = [], [], []
    rest = iter(args[1:])
    for a in rest:
        if a == "--":
            words.extend(rest)
        elif a.startswith("--"):
            name, eq, value = a.partition("=")
            if name in LONG_VALUE_FLAGS and not eq:
                value = next(rest, "")
            if name == "--include":
                includes.append(value)
            elif name in ("--regexp", "--file"):
                patterns.append(value)
        elif a.startswith("-") and a != "-":
            m = re.search("[ABCDdefm]", a)   # the short flags that take a value, attached or as the next word
            if m:
                value = a[m.end():] or next(rest, "")
                if m.group() in "ef":
                    patterns.append(value)
        else:
            words.append(a)
    if not patterns and words:
        patterns.append(words.pop(0))
    if not any(patterns):
        return []
    out = []
    for p in words:
        p = p.removeprefix("./")
        folder, _, name = p.rpartition("/")
        if "*" in name or "?" in name:
            out.append({"path": folder, "glob": name})
        else:
            out.extend({"path": p, "glob": g} for g in includes or [None])
    return out


def daily_intel(cs, prompt):
    """workflow-ops/daily-intel-briefing SKILL.md step 3: "Each section gets ≥ 2 WebSearch calls with different
    angles and every item gets ≥ 1 WebFetch of its primary source before it is written." """
    briefs = [d for d in map(loads, written(cs, r"output/briefings/\d{4}-\d{2}-\d{2}\.json$").values()) if isinstance(d, dict)]
    searches, fetched = count(cs, "WebSearch"), {url_key(i.get("url", "")) for n, i in cs if n == "WebFetch"}
    if not briefs:
        return {"metrics": {"searches": searches, "fetches": len(fetched)}, "below": ["no briefing written"]}
    b = briefs[-1]
    sections = b.get("sections") or []
    items = [i for s in sections for i in s.get("items") or []]
    urls = lambda i: [s.get("url", "") for s in i.get("sources") or [] if isinstance(s, dict)]
    unfetched = [i for i in items if not any(url_key(u) in fetched for u in urls(i))]
    m = {"searches": searches, "fetches": count(cs, "WebFetch"), "sections": len(sections), "items": len(items),
         "items_fetched": len(items) - len(unfetched), "deep_dives": len(b.get("deep_dives") or []),
         "domains": len({urlsplit(u).netloc.removeprefix("www.") for i in items for u in urls(i) if u})}
    below = []
    if searches < 2 * len(sections):
        below.append(f"searches {searches} < 2 per section ({2 * len(sections)})")
    if unfetched:
        below.append(f"items without a fetched source {len(unfetched)} of {len(items)}")
    return {"metrics": m, "below": below}


def meeting_prep(cs, prompt):
    """workflow-ops/meeting-prep-loop SKILL.md: write output/meetings/prep/<uid>.json unless needs is "surface",
    and a surface for every meeting (steps 5-6); "For each entry in the meeting's docs with a text path, read the
    file" (step 3); "Stay within ≤ 4 web calls per run in total" (step 4). The document floor is looser than the
    sentence: a document only searched (the Grep tool or a Bash grep), or carried into the prep from the last one,
    passes; a document the run neither opened nor listed fails."""
    root = re.search(r"output/\.runs/\d{8}-\d{4}-meeting-prep", prompt)
    root = root and root.group(0)
    task = loads((REPO / root / "TASK.json").read_text()) if root and (REPO / root / "TASK.json").exists() else None
    if not task:
        return None
    meetings = task.get("meetings") or []
    due = [x for x in meetings if x.get("needs") != "surface"]
    preps = {Path(f).stem: loads(t) for f, t in written(cs, r"output/meetings/prep/[^/]+\.json$").items()}
    surfaces = {Path(f).stem for f in written(cs, r"output/meetings/surfaces/[^/]+\.json$")}
    reads = [str(i.get("file_path", "")) for n, i in cs if n == "Read"]
    # A prep or surface the run read and left as it was counts: the agent judged it current (seen 2026-10-27/28).
    kept = lambda kind: {Path(r).stem for r in reads if f"output/meetings/{kind}/" in r}
    greps = [i for n, i in cs if n == "Grep"]
    greps += [e for n, i in cs if n == "Bash" for e in grep_inputs(str(i.get("command", "")))]
    docs = sorted({d["text"].removeprefix("./") for x in due for d in x.get("docs") or [] if d.get("text")})
    read = [d for d in docs if any(r.endswith(d) for r in reads)]
    # Searching a document for this meeting's names and terms finds what matters in it; never opening it does not.
    unopened = [d for d in docs if d not in read and not any(grepped(g, d) for g in greps)]
    # A re-prep may carry a document's insight over from the last prep instead of reopening it: that is not ignoring it.
    def listed(x):
        prep, f = preps.get(x.get("uid")), REPO / "output" / "meetings" / "prep" / f"{x.get('uid')}.json"
        if prep is None and x.get("uid") in kept("prep") and f.exists():   # kept, not rewritten: read it from disk
            prep = loads(f.read_text())
        return json.dumps(prep.get("documents") or []) if isinstance(prep, dict) else "[]"

    ignored = {d["text"].removeprefix("./") for x in due for d in x.get("docs") or []
               if d.get("text") and d["text"].removeprefix("./") in unopened and d.get("id", "\0") not in listed(x)}
    web = count(cs, "WebSearch", "WebFetch")
    good = [p for p in preps.values() if isinstance(p, dict)]
    m = {"meetings": len(meetings), "preps": len(good), "docs": len(docs), "docs_read": len(read),
         "docs_grepped_only": len(docs) - len(read) - len(unopened), "docs_ignored": len(ignored), "web": web,
         "participants": sum(len(p.get("participants") or []) for p in good),
         "talking_points": sum(len(p.get("talking_points") or []) for p in good),
         "new_insight": sum(1 for p in good if p.get("new_insight"))}
    below = []
    missing = [x for x in due if x.get("uid") not in set(preps) | kept("prep")]
    if missing:
        below.append(f"meetings without a prep {len(missing)} of {len(due)}")
    if "surfaces/" in prompt:   # surfaces are owed since the launch prompt asks for them (2026-10-28)
        lacking = [x for x in meetings if x.get("uid") not in surfaces | kept("surfaces")]
        if lacking:
            below.append(f"meetings without a surface {len(lacking)} of {len(meetings)}")
    if ignored:
        below.append(f"documents neither opened nor in the prep {len(ignored)} of {len(docs)}")
    if web > 4:
        below.append(f"web calls {web} > 4")
    return {"metrics": m, "below": below}


JOBS = {"daily-intel": daily_intel, "meeting-prep": meeting_prep}


def measure(job, path):
    """{"metrics": {...}, "below": [floor misses]} for a listed job's run, else None."""
    fn = JOBS.get(job)
    return fn(calls(path), launch(path)) if fn and path else None


def efficiency(cs):
    """Research a run repeated for nothing, for every job (path/convergence evals; report-only, never a floor or a
    code): a WebSearch whose words an earlier search already used, a WebFetch of the same URL with the same prompt
    (a new prompt asks a new question), a Read of the same file range with no Write or Edit to it in between.
    Exact repeats of any call are not counted: on 2026-11-08 (~860 runs) they were mostly `date` stamps and checks
    re-run after a fix, while this measure had a median of 0% in every job and a p90 of at most 21%. A model that
    starts looping shows up as a step in its job's per-model numbers."""
    seen, research, repeated = set(), 0, 0
    for name, inp in cs:
        if name == "WebSearch":
            key = ("q", frozenset(re.findall(r"\w+", str(inp.get("query", "")).lower())))
        elif name == "WebFetch":
            key = ("u", url_key(str(inp.get("url", ""))), inp.get("prompt"))
        elif name == "Read":
            key = ("r", inp.get("file_path"), inp.get("offset"), inp.get("limit"))
        else:
            if name in ("Write", "Edit", "MultiEdit"):
                seen = {k for k in seen if k[:2] != ("r", inp.get("file_path"))}
            continue
        research += 1
        repeated += key in seen
        seen.add(key)
    return {"research": research, "repeated": repeated}
