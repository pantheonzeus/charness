# /// script
# requires-python = ">=3.10"
# ///
"""Harness upgrade scout: each weekday, check what is new against this setup and stage at most 3
improvement proposals as plans in the console, each waiting for your Go. Go builds it on its own branch.

  run                    launch the scout agent, validate its RESULT.json, stage the proposals as plans
  check <STATE_ROOT>     validate the RESULT.json one scout run wrote
  stage <STATE_ROOT>     turn a checked RESULT.json into console plans (run does this)
  prepare <task-id>      create the task's worktree + branch upgrade/<task-id> from the checkout as it is now
                         (HEAD + a snapshot commit of uncommitted work), idempotent; print its path
  stage-claude <task-id> copy the builder's drafts from output/.runs/upgrade-<task-id>/claude/ into the worktree's .claude/
  verify <task-id>       syntax and test checks on the files the branch changed
  commit <task-id> <msg> commit everything in the worktree to the branch
  finish <task-id>       write the review page, pause the task on your Apply or Discard (needs a commit and verify OK)
  apply <task-id>        lay the built change onto your checkout as uncommitted edits (you commit)
  close <task-id> [--force]  remove the worktree and branch once applied (--force: discard it unapplied)
  pause-built            one-off: give builds finished before the review pause their Apply and Discard
  decide <task-id> <rejected|deferred|approved> [note]   record your call (the console does this)
  status                 JSON: proposals by decision, worktrees still open

Nothing here merges or commits to your branch. The built change waits for you: Apply in the console's Plans
tab (or `apply <task-id>`, then `close <task-id>`), review `git diff`, commit when you like.
Decisions live in output/harness-upgrades/decisions.jsonl; the scout reads them so a rejected idea
never comes back and a deferred one waits its week.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
REPO = SKILL.parents[3]
OUT = REPO / "output" / "harness-upgrades"
DECISIONS = OUT / "decisions.jsonl"
STATE = OUT / "state.json"
LOCK = OUT / ".lock"
TASKS = REPO / "output" / "tasks"
PLANS = REPO / "output" / "plans"
BRIEFINGS = REPO / "output" / "briefings"
FORENSICS = REPO / "output" / "run-forensics"
SESSIONS_PY = "resources/skills/workflow-ops/run-forensics/scripts/sessions.py"   # lessons ledger (run-forensics §E)
WORKTREES = Path.home() / "GitHub" / "cbrain-upgrades"
RUN_AGENT = REPO / "scripts" / "run_agent.sh"
MAX_NEW, MAX_OPEN, MIN_SEARCHED, DEFER_DAYS = 3, 5, 4, 7
SCOPES = ("cc-releases", "harness-research", "console-ux", "run-failures", "session-lessons")
FIELDS = ("title", "scope", "source", "finding", "current", "change", "files", "steps",
          "predicted_effect", "refuted_if", "effort", "risk", "confidence")
FORBIDDEN = ("IDENTITY.md", "employers/", "cbrain/", "output/", ".mcp.json")   # private or generated: never a proposal's target
SETUP = ["HARNESSCARD.md", "Charter.md", "resources/skills/_shared/CHANGE_LOG.md", "resources/skills/INDEX.md",
         "webapp/README.md", ".claude/settings.json"]
CLI_ENV = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")}
REL = lambda p: str(Path(p).relative_to(REPO))
TOOLS = ["Read", "Glob", "Grep", "Write", "WebSearch", "WebFetch", "Bash(date:*)",
         "Bash(python3 scripts/session_archive.py show:*)", "Bash(python3 scripts/session_archive.py find:*)",
         f"Bash(python3 {SESSIONS_PY} lesson:*)", f"Bash(python3 {SESSIONS_PY} lessons:*)",
         f"Bash(uv run {REL(__file__)}:*)", f"Bash(uv run {__file__}:*)"]
TRAILER = "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"


def load(path, default):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    tmp.replace(path)


def log(msg):
    print(f"[{time.strftime('%F %T')}] {msg}", flush=True)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def slug(text, n=40):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:n].strip("-") or "upgrade"


def git(*args, cwd=REPO, check=True):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode:
        sys.exit(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout.strip()


# ---------- decisions ----------

def decisions():
    out = []
    try:
        for line in DECISIONS.read_text().splitlines():
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    except OSError:
        pass
    return out


def latest():
    """The last decision per task id."""
    last = {}
    for d in decisions():
        last[d["id"]] = {**last.get(d["id"], {}), **d}
    return last


def decide(tid, decision, note=""):
    if decision not in ("proposed", "approved", "rejected", "deferred", "built", "applied", "closed", "discarded"):
        sys.exit(f"unknown decision {decision}")
    entry = {"ts": now(), "id": tid, "decision": decision}
    if note:
        entry["note"] = note[:500]
    if decision == "deferred":
        entry["until"] = time.strftime("%Y-%m-%d", time.localtime(time.time() + DEFER_DAYS * 86400))
    OUT.mkdir(parents=True, exist_ok=True)
    with DECISIONS.open("a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    d = TASKS / tid
    if decision in ("rejected", "deferred") and (d / "TASK.md").exists():
        summary = ("Rejected. Logged, so the scout won't propose it again." if decision == "rejected"
                   else f"Deferred to {entry['until']}. The scout may bring it back after that.")
        save(d / "STATUS.json", {"state": "done", "stage": "decided", "summary": summary, "updated": now()})
    return entry


def open_ids():
    return [i for i, d in latest().items() if d["decision"] in ("proposed", "approved")]


# ---------- scout ----------

def check(root):
    root = Path(root)
    if not (root / "TASK.json").is_file():
        return [f"no TASK.json in {root}"]
    result = load(root / "RESULT.json", None)
    if not isinstance(result, dict) or not isinstance(result.get("proposals"), list):
        return ['no RESULT.json: write {"searched": [...], "considered": n, "proposals": [...]}']
    task = load(root / "TASK.json", {})
    errs = []
    if len(result.get("searched") or []) < MIN_SEARCHED:
        errs.append(f"searched: list at least {MIN_SEARCHED} queries or pages you checked, across the scopes")
    cap = task.get("max_new", MAX_NEW)
    if len(result["proposals"]) > cap:
        errs.append(f"at most {cap} proposals this run, found {len(result['proposals'])}")
    seen = {slug(t) for t in task.get("closed_titles", [])}
    ready = {l["id"] for l in task.get("ready_lessons", [])}
    for i, p in enumerate(result["proposals"]):
        miss = [k for k in FIELDS if not p.get(k)]
        if miss:
            errs.append(f"proposals[{i}]: missing {', '.join(miss)}")
            continue
        if p["scope"] not in SCOPES:
            errs.append(f"proposals[{i}]: scope must be one of {SCOPES}")
        if p["effort"] not in ("S", "M", "L"):
            errs.append(f"proposals[{i}]: effort must be S, M or L")
        if p["confidence"] not in ("verified", "likely", "unsure"):
            errs.append(f"proposals[{i}]: confidence must be verified, likely or unsure")
        src = p["source"] if isinstance(p["source"], dict) else {}
        url = str(src.get("url", ""))
        if not src.get("title") or not (url.startswith("http") or (REPO / url).is_file()):
            errs.append(f"proposals[{i}]: source needs a title and a url you opened (or a repo path for run-failures)")
        if not isinstance(p["steps"], list) or not 1 <= len(p["steps"]) <= 6:
            errs.append(f"proposals[{i}]: steps is a list of 1-6 build steps")
        for f in p["files"] if isinstance(p["files"], list) else ["(files must be a list)"]:
            f = str(f)
            if f.startswith(FORBIDDEN) or ".." in f or f.startswith("/"):
                errs.append(f"proposals[{i}]: {f} is off limits (private, generated or outside the repo)")
            elif not (REPO / f).exists() and not (REPO / f).parent.is_dir() and not (
                    re.fullmatch(r"resources/skills/[a-z-]+/[a-z0-9-]+/SKILL\.md", f) and (REPO / f).parent.parent.is_dir()):
                errs.append(f"proposals[{i}]: {f} neither exists nor sits in an existing folder")
        if p["scope"] == "session-lessons" and not (
                isinstance(p.get("lessons"), list) and p["lessons"] and set(p["lessons"]) <= set(ready)):
            errs.append(f"proposals[{i}]: a session-lessons proposal lists the ready lesson ids it acts on in 'lessons'")
        if slug(p["title"]) in seen:
            errs.append(f"proposals[{i}]: '{p['title']}' was already proposed and decided; drop it")
    return errs


def scout_context():
    """What the scout reads: new briefings, current run failures, the setup, and every past decision."""
    state = load(STATE, {})
    last = state.get("last_run_date", "")
    briefings = sorted(p for p in BRIEFINGS.glob("????-??-??.json") if p.stem > last)[-3:] if BRIEFINGS.exists() else []
    if not briefings and BRIEFINGS.exists():
        briefings = sorted(BRIEFINGS.glob("????-??-??.json"))[-1:]
    reports = sorted(FORENSICS.glob("report-*.md"))[-1:] if FORENSICS.exists() else []
    issues = load(FORENSICS / "issues.json", {})
    failing = [{"code": c, "state": v.get("state"), "jobs": v.get("jobs"), "examples": (v.get("examples") or [])[:2]}
               for c, v in issues.items() if isinstance(v, dict) and v.get("state") not in ("verified", "closed")]
    titles = {}
    for d in TASKS.glob("*-upgrade-*/TASK.md") if TASKS.exists() else []:
        m = re.search(r"^title:\s*(.+)$", d.read_text(), re.M)
        titles[d.parent.name] = m.group(1).strip() if m else d.parent.name
    today = time.strftime("%Y-%m-%d")
    past = [{"title": titles.get(i, i), "decision": d["decision"], "note": d.get("note", ""), "until": d.get("until")}
            for i, d in latest().items()]
    closed = [p["title"] for p in past if p["decision"] in ("rejected", "built", "applied", "closed", "discarded", "proposed", "approved")
              or (p["decision"] == "deferred" and (p.get("until") or "") > today)]
    sessions = sorted(FORENSICS.glob("sessions-*.md"))[-1:] if FORENSICS.exists() else []
    lessons = load(FORENSICS / "lessons.json", {})
    ready = [{"id": i, "text": l["text"], "target": l["target"], "sessions": l["sessions"][:5],
              "helpful": l["helpful"], "harmful": l["harmful"], "provenance": l["provenance"]}
             for i, l in lessons.items() if l["status"] == "candidate" and len(set(l["sessions"])) >= 2
             and l["helpful"] - l["harmful"] >= 2]
    return {"briefings": [REL(p) for p in briefings], "forensics_report": [REL(p) for p in reports],
            "failing_codes": failing, "sessions_report": [REL(p) for p in sessions], "ready_lessons": ready, "setup": [f for f in SETUP if (REPO / f).exists()],
            "past_proposals": past, "closed_titles": closed}


def alive():
    try:
        os.kill(int(LOCK.read_text()), 0)
        return True
    except (OSError, ValueError):
        return False


def run():
    if alive():
        return log("previous run still alive; skipping")
    waiting = open_ids()
    if len(waiting) >= MAX_OPEN:
        return log(f"{len(waiting)} proposals still wait for your call; no new scan until you decide some")
    OUT.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(str(os.getpid()))
    try:
        stamp = time.strftime("%Y%m%d-%H%M%S")
        root = REPO / "output" / ".runs" / f"{stamp}-harness-upgrade-scout"
        root.mkdir(parents=True)
        save(root / "TASK.json", {"run": stamp, "date": time.strftime("%Y-%m-%d"), "scopes": list(SCOPES),
                                  "max_new": min(MAX_NEW, MAX_OPEN - len(waiting)), **scout_context()})
        (root / "RESPONSE.md").write_text(
            f"# harness-upgrade-scout {stamp}\n- [ ] context read (briefings, failing codes, setup, past proposals)\n"
            "- [ ] scanned the four scopes (queries listed in RESULT.json searched)\n"
            "- [ ] every candidate checked against the setup files it would change\n"
            "- [ ] RESULT.json written (0-3 proposals)\n- [ ] upgrades.py check prints OK\n")
        prompt = (f"Read and follow resources/skills/workflow-ops/harness-upgrade-scout/SKILL.md, section Scout (a repo skill: "
                  f"open it with Read, not the Skill tool) for the task packet {REL(root)}/TASK.json. Your STATE_ROOT is "
                  f"{REL(root)}/. Finish with `uv run {REL(__file__)} check {REL(root)}` printing OK.")
        subprocess.run(["bash", str(RUN_AGENT), "harness-upgrade-scout", str(root / "RESPONSE.md"), prompt,
                        "--permission-mode", "acceptEdits", "--allowedTools", *TOOLS],
                       cwd=REPO, env=CLI_ENV, stdin=subprocess.DEVNULL)
        errs = check(root)
        staged = stage(root) if not errs else []
        log(f"{len(staged)} proposal(s) staged; check {'OK' if not errs else 'FAILED: ' + '; '.join(errs[:3])}")
        state = load(STATE, {"runs": []})
        state["runs"] = (state.get("runs", []) + [{"at": stamp, "ok": not errs, "errors": errs[:5], "staged": staged}])[-300:]
        if not errs:
            state["last_run_date"] = time.strftime("%Y-%m-%d")
        save(STATE, state)
    finally:
        LOCK.unlink(missing_ok=True)


def stage(root):
    """Each proposal becomes a console plan, already paused on "Build it?": the case is in the done steps,
    the build is in the pending ones. tasks.py holds it until you answer."""
    root = Path(root)
    staged = []
    for n, p in enumerate(load(root / "RESULT.json", {}).get("proposals") or [], 1):
        tid = f"{time.strftime('%Y%m%d-%H%M')}-upgrade-{n}-{slug(p['title'], 30)}"
        d = TASKS / tid
        if d.exists():
            continue
        d.mkdir(parents=True)
        src, branch = p["source"], f"upgrade/{tid}"
        (d / "TASK.md").write_text(
            f"---\ntitle: {p['title'][:80]}\nkind: plan\nrunner: upgrade\ninterrogate: no\nrequested: {now()}\n---\n"
            f"## Outcome\n{p['change']}\n\n## Context\n- What's new: {p['finding']} ({src['title']}, {src['url']})\n"
            f"- Today: {p['current']}\n- Predicted effect: {p['predicted_effect']}\n- Refuted if: {p['refuted_if']}\n"
            f"- Effort {p['effort']} · risk: {p['risk']}\n\n## Constraints\nBuild on branch `{branch}` in its own worktree "
            f"(`upgrades.py prepare {tid}`). Never merge, never touch the main checkout. Files in scope: "
            f"{', '.join(p['files'])}.\n\n## Proposal\n```json\n{json.dumps(p, indent=1, ensure_ascii=False)}\n```\n")
        build = [{"id": f"s{i}", "title": str(t)[:200], "owner": "cos", "status": "pending", "checkpoint": None,
                  "note": "", "findings": []} for i, t in enumerate(p["steps"], 3)]
        k = len(build) + 3
        build += [{"id": f"s{k}", "title": "Verify, commit to the branch, write the review page", "owner": "cos",
                   "status": "pending", "checkpoint": None, "note": "", "findings": []},
                  {"id": f"s{k + 1}", "title": "Review the diff, then apply or discard it", "owner": "you",
                   "status": "pending", "checkpoint": None, "note": f"upgrades.py apply {tid} · upgrades.py close {tid}", "findings": []}]
        url = str(src["url"])
        save(d / "PLAN.json", {
            "outcome": p["change"],
            "deliverable": {"shape": f"The change on branch {branch}, verified, with a review page (diff, checks, merge and discard commands)",
                            "path": f"output/plans/{tid}.md"},
            "estimate": {"minutes": {"S": 10, "M": 25, "L": 60}[p["effort"]], "web_calls": 2},
            "sources_planned": [f"{'web' if url.startswith('http') else 'repo'}: {src['title']}", *[f"repo: {f}" for f in p["files"]]],
            "steps": [
                {"id": "s1", "title": f"What's new: {src['title']}"[:200], "owner": "researcher", "status": "done", "checkpoint": None,
                 "note": f"Today: {p['current']}"[:600],
                 "findings": [{"text": p["finding"], "confidence": p["confidence"], "sources": [url]}]},
                {"id": "s2", "title": "Why it pays off here, and how it could fail", "owner": "analyst", "status": "done", "checkpoint": None,
                 "note": f"Effort {p['effort']}. Risk: {p['risk']}"[:600],
                 "findings": [{"text": f"Predicted: {p['predicted_effect']}", "confidence": "likely", "sources": []},
                              {"text": f"Refuted if: {p['refuted_if']}", "confidence": "likely", "sources": []}]},
                *build],
            "receipts": [{"kind": "web" if url.startswith("http") else "repo", "ref": url, "label": src["title"][:80], "used_in": ["s1"]}],
            "interrogation": [],
            "updated": now()})
        save(d / "STATUS.json", {"state": "needs_input", "stage": "plan", "updated": now(),
                                 "question": f"Build it on branch {branch}? {p['predicted_effect']}"[:400],
                                 "options": ["Go", "Reject", "Defer a week"]})
        decide(tid, "proposed", p["title"])
        for lid in p.get("lessons") or []:
            subprocess.run([sys.executable, str(REPO / SESSIONS_PY), "lesson", "mark", lid, "proposed", "--ref", tid], cwd=REPO)
        staged.append(tid)
    return staged


# ---------- build ----------

def meta(tid):
    d = TASKS / tid
    if not re.fullmatch(r"[0-9]{8}-[0-9]{4}-upgrade-[a-z0-9-]+", tid) or not (d / "TASK.md").exists():
        sys.exit(f"no upgrade task {tid}")
    return d, load(d / "upgrade.json", {})


def prepare(tid):
    """Worktree on branch upgrade/<tid>, based on the checkout as it is now: HEAD plus a snapshot commit of
    your uncommitted and untracked (not ignored) files, so the builder sees the setup you actually run."""
    d, m = meta(tid)
    wt = WORKTREES / tid
    if not wt.is_dir():
        WORKTREES.mkdir(parents=True, exist_ok=True)
        head = git("rev-parse", "HEAD")
        git("worktree", "add", "-q", "-b", f"upgrade/{tid}", str(wt), head)
        for f in git("ls-files", "-m", "-o", "--exclude-standard").splitlines():
            src, dst = REPO / f, wt / f
            if src.is_file():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        for f in git("ls-files", "-d").splitlines():
            (wt / f).unlink(missing_ok=True)
        git("add", "-A", cwd=wt)
        if git("diff", "--cached", "--name-only", cwd=wt):
            git("commit", "-q", "--no-verify", "-m", f"base: working-tree snapshot {now()}", cwd=wt)
        m = {"branch": f"upgrade/{tid}", "worktree": str(wt), "head": head, "base": git("rev-parse", "HEAD", cwd=wt),
             "base_branch": git("branch", "--show-current"), "created": now()}
        save(d / "upgrade.json", m)
    return str(wt)


def apply(tid):
    """Lay the branch's change (snapshot → tip) onto the main checkout as uncommitted edits. Never commits."""
    d, m = meta(tid)
    if latest().get(tid, {}).get("decision") != "built":
        sys.exit("only a built upgrade can be applied")
    patch = subprocess.run(["git", "diff", "--binary", m["base"], m["branch"]], cwd=REPO, capture_output=True).stdout
    r = subprocess.run(["git", "apply", "--check", "-"], cwd=REPO, input=patch, capture_output=True)
    if r.returncode:
        sys.exit(f"does not apply cleanly (the files changed since the snapshot):\n{r.stderr.decode().strip()}\n"
                 f"Look at it with: git diff {m['base'][:10]} {m['branch']}\n"
                 f"Discard it with: uv run {REL(__file__)} close {tid} --force")
    subprocess.run(["git", "apply", "-"], cwd=REPO, input=patch, check=True)
    decide(tid, "applied")
    return git("diff", "--stat", m["base"], m["branch"])


def changed(tid):
    _, m = meta(tid)
    wt = m.get("worktree")
    if not wt or not Path(wt).is_dir():
        sys.exit(f"no worktree for {tid}: run prepare first")
    files = set(git("diff", "--name-only", m["base"], cwd=wt).splitlines())
    files |= {line[3:].split(" -> ")[-1] for line in git("status", "--porcelain", "--untracked-files=all", cwd=wt).splitlines()}
    return Path(wt), m, sorted(f for f in files if f)


def stage_claude(tid):
    """Claude Code refuses Write/Edit under any .claude/ in a headless run, and allow rules don't lift that.
    So the builder drafts in STATE_ROOT/claude/<path under .claude> and this copies the drafts into the
    worktree only. All or nothing: a symlink or a target outside .claude/ refuses the whole batch."""
    wt, _, _ = changed(tid)
    src, dst = REPO / "output" / ".runs" / f"upgrade-{tid}" / "claude", (wt / ".claude").resolve()
    pairs = []
    for f in sorted(p for p in src.rglob("*") if p.is_file() or p.is_symlink()):
        target = (dst / f.relative_to(src)).resolve()
        if f.is_symlink() or not target.is_relative_to(dst):
            sys.exit(f"refused, nothing staged: {f.relative_to(src)} leaves the worktree's .claude/")
        pairs.append((f, target))
    if not pairs:
        sys.exit(f"nothing to stage in {src}")
    for f, target in pairs:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(f, target)   # not copy2: an existing hook keeps its mode
    return [str(t.relative_to(dst.parent)) for _, t in pairs]


def verify(tid):
    wt, m, files = changed(tid)
    errs = [] if files else ["the branch changes nothing yet"]
    for f in files:
        p = wt / f
        if f.startswith(FORBIDDEN):
            errs.append(f"{f}: off limits for an upgrade")
        if not p.is_file():
            continue   # deleted
        if p.suffix == ".py":
            r = subprocess.run([sys.executable, "-m", "py_compile", str(p)], capture_output=True, text=True)
            errs += [f"{f}: {r.stderr.strip()[-300:]}"] if r.returncode else []
        elif p.suffix == ".sh":
            r = subprocess.run(["bash", "-n", str(p)], capture_output=True, text=True)
            errs += [f"{f}: {r.stderr.strip()[-300:]}"] if r.returncode else []
        elif p.suffix == ".json":
            try:
                json.loads(p.read_text())
            except ValueError as e:
                errs.append(f"{f}: invalid JSON ({e})")
        if p.name == "SKILL.md":
            sid = re.search(r"^id:\s*(\S+)", p.read_text(), re.M)
            if not sid:
                errs.append(f"{f}: frontmatter has no id")
            elif f"/{p.parent.name}/SKILL.md" not in (wt / "resources/skills/INDEX.md").read_text():
                errs.append(f"{f}: not in resources/skills/INDEX.md (a skill missing from the index is invisible)")
    tests = sorted({t for f in files if f.startswith(".claude/hooks/") for t in (wt / ".claude/hooks/tests").glob("*.test.sh")})
    for t in tests:
        r = subprocess.run(["bash", str(t)], cwd=wt, capture_output=True, text=True, timeout=300,
                           env={**os.environ, "CLAUDE_PROJECT_DIR": str(wt)})
        if r.returncode:
            errs.append(f"{t.relative_to(wt)} failed: {(r.stdout + r.stderr).strip()[-400:]}")
    d, m = meta(tid)
    m["verify"] = {"at": now(), "ok": not errs, "errors": errs[:20], "files": files, "tests": [str(t.relative_to(wt)) for t in tests]}
    save(d / "upgrade.json", m)
    return errs


def commit(tid, msg):
    wt, m, files = changed(tid)
    if not files:
        sys.exit("nothing to commit")
    git("add", "-A", cwd=wt)
    if git("diff", "--cached", "--name-only", cwd=wt):
        git("commit", "-q", "-m", f"{msg.strip()}\n\n{TRAILER}", cwd=wt)
    return git("rev-parse", "--short", "HEAD", cwd=wt)


def review_status(m, report):
    """The pause after a build. tasks.py carries out your Apply or Discard, with no agent."""
    return {"state": "needs_input", "stage": "review", "updated": now(), "report": report,
            "question": f"Built on {m['branch']}, checks OK. Read the review page, then Apply or Discard.",
            "summary": f"Built on {m['branch']}, checks OK. Review the diff, then apply or discard.",
            "options": ["Apply", "Discard"]}


def finish(tid):
    wt, m, _ = changed(tid)
    if git("status", "--porcelain", cwd=wt):
        sys.exit("uncommitted changes in the worktree: commit them first")
    if git("rev-parse", "HEAD", cwd=wt) == m["base"]:
        sys.exit("no commit on the branch yet")
    errs = verify(tid)
    if errs:
        sys.exit("verify failed:\n" + "\n".join(errs))
    d, m = meta(tid)
    notes = REPO / "output" / ".runs" / f"upgrade-{tid}" / "NOTES.md"
    title = re.search(r"^title:\s*(.+)$", (d / "TASK.md").read_text(), re.M).group(1).strip()
    stat = git("diff", "--stat", m["base"], "HEAD", cwd=wt)
    diff = git("diff", m["base"], "HEAD", cwd=wt).splitlines()
    cut = len(diff) > 600
    v = m["verify"]
    page = PLANS / f"{tid}.md"
    PLANS.mkdir(parents=True, exist_ok=True)
    page.write_text(
        f"---\ntype: upgrade-review\ndate: {time.strftime('%Y-%m-%d')}\nbranch: {m['branch']}\n---\n\n# {title}\n\n"
        f"Built on `{m['branch']}` from a snapshot of your checkout ({m.get('base_branch') or 'detached'} at "
        f"`{m.get('head', m['base'])[:10]}` plus uncommitted work). Nothing is applied yet.\n\n"
        f"## What changed and why\n{notes.read_text().strip() if notes.is_file() else '(no notes)'}\n\n"
        f"## Checks\n{'OK' if v['ok'] else 'FAILED'}: {len(v['files'])} file(s) checked"
        + (f"; tests run: {', '.join(v['tests'])}" if v["tests"] else "; no hook tests touched") + "\n\n"
        f"## Your call\n**Apply** or **Discard** on this plan in the console's Plans tab, or in a terminal:\n\n"
        f"- Apply: `uv run {REL(__file__)} apply {tid}` (uncommitted edits in your checkout; review with `git diff`, "
        f"commit when you like), then `uv run {REL(__file__)} close {tid}`\n"
        f"- Discard: `uv run {REL(__file__)} close {tid} --force`\n"
        f"- Look first: `git diff {m['base'][:10]} {m['branch']}` or `cd {wt}`\n\n"
        f"## Diff\n```\n{stat}\n```\n\n```diff\n" + "\n".join(diff[:600]) + ("\n… (cut at 600 lines)" if cut else "") + "\n```\n")
    save(d / "STATUS.json", review_status(m, REL(page)))
    decide(tid, "built")
    return REL(page)


def pause_built():
    """One-off: builds finished while finish() still ended on done get the review pause."""
    moved = []
    for tid, x in latest().items():
        d = TASKS / tid
        st = load(d / "STATUS.json", {})
        if x["decision"] == "built" and st.get("state") == "done" and st.get("stage") == "built":
            save(d / "STATUS.json", review_status(load(d / "upgrade.json", {}), st.get("report")))
            moved.append(tid)
    return moved


def close(tid, force=False):
    d, m = meta(tid)
    wt = m.get("worktree")
    if wt and Path(wt).is_dir():
        git("worktree", "remove", *(["--force"] if force else []), wt)
    applied = any(x["id"] == tid and x["decision"] == "applied" for x in decisions())
    if m.get("branch") and git("branch", "--list", m["branch"]):
        if not (applied or force):
            sys.exit(f"worktree removed; branch {m['branch']} kept because it was never applied. apply it, or close --force to discard.")
        git("branch", "-D", m["branch"])
    decide(tid, "closed" if applied else "discarded")
    st = load(d / "STATUS.json", {})
    if st.get("stage") == "review":   # the pause ends here, from the console or a terminal alike
        save(d / "STATUS.json", {"state": "done", "stage": "applied" if applied else "discarded", "updated": now(),
                                 "report": st.get("report"),
                                 "summary": "Applied to your checkout as uncommitted edits. Review with git diff, commit when you like."
                                 if applied else "Discarded. Worktree and branch removed, nothing applied."})


def status():
    last = latest()
    by = {}
    for i, d in last.items():
        by.setdefault(d["decision"], []).append(i)
    open_wt = [p.name for p in WORKTREES.iterdir() if p.is_dir()] if WORKTREES.exists() else []
    return {"running": alive(), "last_run": (load(STATE, {"runs": []}).get("runs") or [None])[-1],
            "by_decision": by, "worktrees": open_wt}


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["run"]:
        run()
    elif a[:1] == ["check"] and len(a) == 2:
        e = check(a[1])
        print("OK" if not e else "\n".join(e))
        sys.exit(1 if e else 0)
    elif a[:1] == ["stage"] and len(a) == 2:
        e = check(a[1])
        print("\n".join(stage(a[1])) if not e else "\n".join(e))
        sys.exit(1 if e else 0)
    elif a[:1] == ["prepare"] and len(a) == 2:
        print(prepare(a[1]))
    elif a[:1] == ["stage-claude"] and len(a) == 2:
        print("\n".join(stage_claude(a[1])))
    elif a[:1] == ["verify"] and len(a) == 2:
        e = verify(a[1])
        print("OK" if not e else "\n".join(e))
        sys.exit(1 if e else 0)
    elif a[:1] == ["commit"] and len(a) == 3:
        print(commit(a[1], a[2]))
    elif a[:1] == ["finish"] and len(a) == 2:
        print(finish(a[1]))
    elif a[:1] == ["apply"] and len(a) == 2:
        print(apply(a[1]))
    elif a[:1] == ["close"] and len(a) in (2, 3):
        close(a[1], force=a[2:] == ["--force"])
    elif a[:1] == ["pause-built"]:
        print("\n".join(pause_built()) or "nothing to move")
    elif a[:1] == ["decide"] and len(a) in (3, 4):
        print(json.dumps(decide(a[1], a[2], a[3] if len(a) == 4 else "")))
    elif a[:1] == ["status"]:
        print(json.dumps(status(), indent=1, ensure_ascii=False))
    else:
        sys.exit(__doc__)
