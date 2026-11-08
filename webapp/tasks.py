"""Background team tasks: the conversation delegates, the Researcher works, the user gets notified.

Files are the interface (Charter §5), one folder per task under output/tasks/<id>/:
  TASK.md      written by the conversation (or anyone): frontmatter title/depth + the brief
  STATUS.json  written by the worker: working | needs_input | done | failed (+ question, summary…)
  answers/     the user's replies, one file each, from the console or relayed by the conversation
  meta.json    written only here: session id, launches, which answers were consumed, notifications

A watcher launches new tasks, resumes a paused one when an answer appears (`--resume` on the
session id assigned at launch, so it keeps everything it read), and fires a macOS notification
on every state change. A pause ends the worker's run cleanly: nothing hangs while you think.

A task with `runner: upgrade` (a harness-upgrade-scout proposal) arrives already paused on its plan
and launches nothing until you answer: Reject / Defer are recorded here, anything else starts the
builder fresh in the proposal's own git worktree. A finished build pauses again on your review:
Apply / Discard run here too, with no agent.
"""
import importlib.util
import asyncio
import json
import re
import subprocess
import time
import sys
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import employer  # noqa: E402  employer pack (employers/README.md): the mail binding
TASKS = REPO / "output" / "tasks"
RESEARCH = REPO / "output" / "research"
PLANS = REPO / "output" / "plans"
VAULT = REPO / "cbrain"
OWNERS = {"you", "cos", "analyst", "researcher"}
RUN_AGENT = REPO / "scripts" / "run_agent.sh"
LOG = REPO / "output" / "researcher.log"
MAX_RUNNING = 2
ID_RX = re.compile(r"[0-9]{8}-[0-9]{4}-[a-z0-9-]{1,60}")
TOOLS = ["WebSearch", "WebFetch", "Task", "Read", "Glob", "Grep", "Bash(date:*)", "Bash(ls:*)", "Bash(grep:*)",
         "Bash(uv run scripts/render.py:*)", f"Bash(uv run {REPO}/scripts/render.py:*)",  # PDF / MP3 of a deliverable
         "Bash(uv run resources/skills/workflow-ops/reading-pages/scripts/page.py:*)",  # check / render a reading page
         f"Bash(uv run {REPO}/resources/skills/workflow-ops/reading-pages/scripts/page.py:*)"]
INDEXER = REPO / "resources" / "skills" / "vault-hygiene" / "deliverable-index" / "scripts" / "index_deliverables.py"
MEDIA = REPO / "resources" / "skills" / "research" / "notebooklm" / "scripts" / "task_media.py"   # `media:` in TASK.md
MEDIA_TYPES = {".pdf": "application/pdf", ".mp3": "audio/mpeg", ".m4a": "audio/mp4", ".mp4": "video/mp4"}
RENDER = REPO / "scripts" / "render.py"
PLAN_CHECK = "resources/skills/workflow-ops/living-plan/scripts/plan.py"
PLAN_TOOLS = TOOLS + [f"Bash(python3 {PLAN_CHECK}:*)", f"Bash(python3 {REPO}/{PLAN_CHECK}:*)",
                      f"Bash(uv run {PLAN_CHECK}:*)", f"Bash(uv run {REPO}/{PLAN_CHECK}:*)",
                      ]
# A plan whose outcome is an email sends it through workspace-mcp, while the employer pack binds
# mail=google; the living-plan skill puts an approval checkpoint in front of every send.
if employer.provider("mail") == "google":
    PLAN_TOOLS += ["mcp__workspace-mcp__draft_gmail_message", "mcp__workspace-mcp__send_gmail_message"]
# kind → (agent, skill, STATE_ROOT prefix). A plan is the general case; research is the original one.
KINDS = {"research": ("researcher", "research/deep-research", "research"),
         "plan": ("plan-runner", "workflow-ops/living-plan", "plan"),
         "topic": ("topic-builder", "workflow-ops/topic-build", "topic")}   # "bring me to X" when X doesn't exist yet
# runner → (agent, skill, STATE_ROOT prefix): a plan the console shows like any other, run by a special agent.
UPGRADES = REPO / "resources" / "skills" / "workflow-ops" / "harness-upgrade-scout" / "scripts" / "upgrades.py"
RUNNERS = {"upgrade": ("harness-upgrader", "workflow-ops/harness-upgrade-scout", "upgrade")}
UPGRADE_TOOLS = ["Read", "Glob", "Grep", "Write", "Edit", "WebFetch", "Bash(date:*)",
                 f"Bash(uv run {UPGRADES.relative_to(REPO)}:*)", f"Bash(uv run {UPGRADES}:*)"]


def upgrades():
    spec = importlib.util.spec_from_file_location("upgrades", UPGRADES)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

router = APIRouter()


def load(path, default):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def save(path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    tmp.replace(path)


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return dict(re.findall(r"^(\w+):\s*(.+?)\s*$", m.group(1), re.M)) if m else {}


def processes():
    """Every process's command line: one `ps` per listing, not a `pgrep` per task (128 tasks took 3.5 s)."""
    return subprocess.run(["ps", "-axww", "-o", "command="], capture_output=True, text=True).stdout


def alive(meta, procs=None):
    sid = (meta or {}).get("session_id")
    return bool(sid) and sid in (processes() if procs is None else procs)


def notify(title, subtitle, message):
    # argv, not string interpolation: task text can't break out of the AppleScript.
    subprocess.Popen(["osascript", "-e", "on run argv", "-e",
                      'display notification (item 1 of argv) with title (item 2 of argv) subtitle (item 3 of argv) sound name "Glass"',
                      "-e", "end run", message[:200], title, subtitle[:80]],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def launch(d, meta, env, answer=None):
    tid, fm = d.name, frontmatter((d / "TASK.md").read_text())
    kind = fm.get("kind", "research").strip().lower()
    agent, skill, prefix = KINDS.get(kind, KINDS["research"])
    if kind == "research" and fm.get("depth", "").strip().lower() == "deep":
        agent = "researcher-deep"
    runner = fm.get("runner", "").strip().lower()
    if runner in RUNNERS:
        agent, skill, prefix = RUNNERS[runner]
    spine = REPO / "output" / ".runs" / f"{prefix}-{tid}" / "RESPONSE.md"
    if answer is None or not meta.get("launches"):   # a staged task's first launch already carries your answer
        prompt = (f"Read and follow resources/skills/{skill}/SKILL.md (a repo skill: open it with Read, not the Skill tool) for the task packet output/tasks/{tid}/TASK.md. "
                  f"Your STATE_ROOT is output/.runs/{prefix}-{tid}/. Keep output/tasks/{tid}/STATUS.json current exactly as the skill specifies."
                  + (f"\n\nThe user answered the staged plan:\n\n{answer}" if answer else ""))
        session = ["--session-id", meta["session_id"]]
    else:
        prompt = (f"The user answered your question on task {tid}:\n\n{answer}\n\n"
                  f"Continue the {skill} skill from where you paused: reopen output/.runs/{prefix}-{tid}/RESPONSE.md"
                  + (" and re-read output/tasks/{tid}/PLAN.json first (the user may have edited it)".format(tid=tid) if kind == "plan" else "")
                  + (" and re-read the skill's Build section (a retried build may find it changed)" if runner == "upgrade" else "")
                  + ", turn [~] back into [ ], set STATUS.json to working, then carry on.")
        session = ["--resume", meta["session_id"]]
    spine.parent.mkdir(parents=True, exist_ok=True)
    # Planning phase (interrogate + plan preview, before PLAN.json exists) runs on Opus — the
    # highest-leverage, hardest-reasoning part of a plan. CLI --model beats the plan-runner
    # agent file's Sonnet `model:`, which still governs once execution starts (PLAN.json exists).
    # opusplan's own Opus/Sonnet auto-switch never fires here: it triggers on interactive plan
    # mode, which headless `claude -p` runs never enter.
    model_args = ["--model", "claude-opus-5-5"] if kind == "plan" and not (d / "PLAN.json").exists() else []
    tools = PLAN_TOOLS if kind == "plan" else TOOLS
    if runner == "upgrade":   # the builder works in the proposal's worktree, outside the repo
        try:
            tools = UPGRADE_TOOLS + ["--add-dir", upgrades().prepare(tid)]
        except SystemExit as e:   # upgrades.py exits on a git error; that must not stop the watcher
            meta["error"] = f"could not create the worktree: {e}"
            return
    with LOG.open("a") as log:
        subprocess.Popen(["bash", str(RUN_AGENT), agent, str(spine), prompt, "--permission-mode", "acceptEdits",
                          *session, *model_args, "--allowedTools", *tools],
                         cwd=REPO, env=env, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                         start_new_session=True)
    meta.setdefault("launches", []).append(time.time())


def answerable(d, status):
    """An answer restarts the worker on a pause, and on a failed upgrade build (Go again retries it)."""
    st = status.get("state")
    return st == "needs_input" or (st == "failed" and frontmatter((d / "TASK.md").read_text()).get("runner") == "upgrade")


def state_of(d, meta, status, procs=None):
    if meta is None:
        return "queued"
    if meta.get("cancelled"):
        return "cancelled"
    if meta.get("error"):
        return "failed"
    if alive(meta, procs):  # a live process is working, even if STATUS still shows the question it just got answered
        return "working" if status.get("state") is None or answerable(d, status) else status["state"]
    if answerable(d, status) and unconsumed(d, meta):
        return "resuming"
    if status.get("state") in ("needs_input", "done", "failed"):
        return status["state"]
    return "lost" if meta.get("launches") and time.time() - meta["launches"][-1] > 30 else "working"


def unconsumed(d, meta):
    return [a for a in sorted((d / "answers").glob("*.md")) if a.name not in meta.get("answers_used", [])]


def settle_upgrade(d, call, status):
    """Your Apply or Discard from the review pause. upgrades.py exits on a git error, which must not
    stop the watcher: the message lands in STATUS."""
    mod, did = upgrades(), ""
    try:
        if call == "apply":
            mod.apply(d.name)
            did = "Applied to your checkout, but the cleanup failed: "
            mod.close(d.name)
        else:
            mod.close(d.name, force=True)
    except (SystemExit, Exception) as e:
        save(d / "STATUS.json", {**status, "state": "failed", "error": f"{did}{e}",
                                 "updated": time.strftime("%Y-%m-%dT%H:%M:%S%z")})


def tick(env):
    if not TASKS.exists():
        return
    dirs = sorted(x for x in TASKS.iterdir() if x.is_dir() and (x / "TASK.md").exists())
    procs = processes()
    running = sum(1 for d in dirs if alive(load(d / "meta.json", None), procs))
    for d in dirs:
        meta, status = load(d / "meta.json", None), load(d / "STATUS.json", {})
        fm = frontmatter((d / "TASK.md").read_text())
        title, who = fm.get("title", d.name), "Your team" if fm.get("kind") == "plan" else "Researcher"
        if meta is None:
            if not ID_RX.fullmatch(d.name):
                save(d / "meta.json", {"error": "task folder name must look like YYYYMMDD-HHMM-short-slug"})
                continue
            if fm.get("runner") in RUNNERS and status.get("state") == "needs_input":
                # Staged already paused (a scout proposal): nothing runs until you answer.
                save(d / "meta.json", {"session_id": str(uuid.uuid4()), "answers_used": [], "notified": None})
                continue
            if running >= MAX_RUNNING:
                continue  # stays queued until a slot frees up
            meta = {"session_id": str(uuid.uuid4()), "answers_used": [], "notified": None}
            launch(d, meta, env)
            running += 1
            save(d / "meta.json", meta)
            continue
        if meta.get("cancelled") or meta.get("error"):
            continue
        is_alive = alive(meta, procs)
        if answerable(d, status) and not is_alive and running < MAX_RUNNING:
            fresh = unconsumed(d, meta)
            if fresh:
                answer = "\n\n".join(a.read_text().strip() for a in fresh)
                call = re.match(r"\s*(reject|defer)", answer, re.I)
                review = fm.get("runner") == "upgrade" and status.get("stage") == "review"
                # Touches your checkout, so only a plain Apply / Discard counts; any other text goes to the builder.
                settle = re.fullmatch(r"\s*(apply|discard)(\s+it)?[.!]?\s*", answer.split("\n\n")[0], re.I) if review else None
                if settle or (fm.get("runner") == "upgrade" and call and not review):   # your call, recorded; no agent needed
                    if settle:
                        settle_upgrade(d, settle.group(1).lower(), status)
                    else:
                        upgrades().decide(d.name, "rejected" if call.group(1).lower() == "reject" else "deferred", answer)
                    meta["answers_used"] += [a.name for a in fresh]
                    meta["notified"] = f"done:{load(d / 'STATUS.json', {}).get('updated')}"   # you made the call; no knock about it
                    save(d / "meta.json", meta)
                    continue
                if fm.get("runner") == "upgrade" and re.match(r"\s*go\b", answer, re.I) and not meta.get("launches"):
                    upgrades().decide(d.name, "approved")
                launch(d, meta, env, answer=answer)
                meta["answers_used"] += [a.name for a in fresh]
                running += 1
                save(d / "meta.json", meta)
                continue
        st = state_of(d, meta, status, procs)
        key = f"{st}:{status.get('updated')}"
        if st in ("needs_input", "done", "failed", "lost") and meta.get("notified") != key:
            msg = {"needs_input": f"Needs your input: {status.get('question', '')}",
                   "done": f"Ready: {status.get('summary', '')}",
                   "failed": f"Stopped: {status.get('error', '')}",
                   "lost": "Stopped without reporting. Ops has the log."}
            built = st == "needs_input" and status.get("stage") == "review"   # paused, but its report is finished
            notify(f"cbrain · {who}", title, msg["done" if built else st])
            if st == "done" or built:  # the report now exists in output/: give it its vault index note
                with LOG.open("a") as log:
                    subprocess.Popen(["python3", str(INDEXER)], cwd=REPO, stdout=log, stderr=subprocess.STDOUT)
                    if fm.get("media") and not meta.get("media_started"):   # NotebookLM podcast / video of the report
                        subprocess.Popen(["python3", str(MEDIA), d.name], cwd=REPO, stdout=log, stderr=subprocess.STDOUT,
                                         stdin=subprocess.DEVNULL, start_new_session=True)
                        meta["media_started"] = time.time()
            meta["notified"] = key
            save(d / "meta.json", meta)


async def watch(env):
    while True:
        try:
            await asyncio.to_thread(tick, env)
        except Exception as e:  # never let one bad task folder kill the watcher
            print(f"task watcher: {type(e).__name__}: {e}", flush=True)
        await asyncio.sleep(3)


def task_dir(tid):
    if not ID_RX.fullmatch(tid) or not (TASKS / tid / "TASK.md").exists():
        raise HTTPException(404, "no such task")
    return TASKS / tid


@router.get("/api/tasks")
def list_tasks():
    out, procs = [], processes()
    for d in sorted(TASKS.glob("*/TASK.md"), reverse=True) if TASKS.exists() else []:
        d = d.parent
        meta, status = load(d / "meta.json", None), load(d / "STATUS.json", {})
        fm = frontmatter((d / "TASK.md").read_text())
        plan = None
        if fm.get("kind") == "plan":
            plan = load(d / "PLAN.json", None)
            if plan:
                flags = {}
                for line in (d / "flags.jsonl").read_text().splitlines() if (d / "flags.jsonl").exists() else []:
                    try:
                        f = json.loads(line)
                        flags[f["ref"]] = f["reason"]
                    except (ValueError, KeyError):
                        pass
                for r in plan.get("receipts") or []:
                    r["flag"] = flags.get(r.get("ref"))
        out.append({"id": d.name, "kind": fm.get("kind", "research"), "doc": plan, "runner": fm.get("runner"),
                    "title": fm.get("title", d.name), "depth": fm.get("depth", "standard"),
                    "requested": fm.get("requested"), "state": state_of(d, meta, status, procs),
                    **{k: status.get(k) for k in ("stage", "plan", "question", "options", "questions", "summary", "report", "topic", "updated", "error")},
                    "error": (meta or {}).get("error") or status.get("error")})
    return out


@router.post("/api/plans")
async def new_plan(request: Request):
    """A plan started from the console's Plans view instead of the conversation. Same packet the
    conversation writes; `interrogate: no` only when the user ticked "skip the hard questions"."""
    body = await request.json()
    outcome = str(body.get("outcome", "")).strip()[:2000]
    if not outcome:
        raise HTTPException(400, "state the outcome")
    title = " ".join(outcome.split()[:8])[:80].rstrip(":;,.-— ")
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40] or "plan"
    tid = f"{time.strftime('%Y%m%d-%H%M')}-{slug}"
    d = TASKS / tid
    if d.exists():
        raise HTTPException(409, "a plan with this name was just started; wait a minute")
    d.mkdir(parents=True)
    by, ctx = str(body.get("by", "")).strip()[:200], str(body.get("context", "")).strip()[:4000]
    # Deliverables or idea notes picked in the Library: the plan builds on them first (living-plan reads ## Sources).
    srcs = [p for p in (str(x) for x in (body.get("sources") or [])[:20])
            if p.startswith(("output/", "cbrain/")) and ".." not in p and (REPO / p).is_file()]
    (d / "TASK.md").write_text(
        f"---\ntitle: {title}\nkind: plan\ninterrogate: {'no' if body.get('skip_questions') else 'yes'}\n"
        f"requested: {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n---\n"
        f"## Outcome\n{outcome}\n\n## Context\n{ctx or '(none given: find it in the vault)'}\n\n"
        f"## Constraints\n{('Deadline: ' + by) if by else '(none given)'}\n"
        + ("\n## Sources\n" + "".join(f"- {p}\n" for p in srcs) if srcs else ""))
    return {"id": tid}


def new_research(title, question, decision, scope):
    """A research task written by the console (e.g. an idea's Dive deeper). The watcher launches it."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40] or "research"
    tid = f"{time.strftime('%Y%m%d-%H%M')}-{slug}"
    d = TASKS / tid
    if d.exists():
        raise HTTPException(409, "a task with this name was just started; wait a minute")
    d.mkdir(parents=True)
    (d / "TASK.md").write_text(f"---\ntitle: {title[:80]}\ndepth: standard\nrequested: {time.strftime('%Y-%m-%dT%H:%M:%S%z')}\n---\n\n"
                               f"## Question\n{question}\n\n## Decision it informs\n{decision}\n\n## Scope & constraints\n{scope}\n")
    return tid


@router.post("/api/tasks/{tid}/answer")
async def answer(tid: str, request: Request):
    d = task_dir(tid)
    text = str((await request.json()).get("text", "")).strip()
    if not text:
        raise HTTPException(400, "empty answer")
    (d / "answers").mkdir(exist_ok=True)
    (d / "answers" / f"{time.strftime('%Y%m%d-%H%M%S')}.md").write_text(text + "\n")
    return {"ok": True}


@router.post("/api/tasks/{tid}/cancel")
def cancel(tid: str):
    d = task_dir(tid)
    meta = load(d / "meta.json", {}) or {}
    if meta.get("session_id"):
        subprocess.run(["pkill", "-f", meta["session_id"]])
    meta["cancelled"] = True
    save(d / "meta.json", meta)
    return {"ok": True}


@router.get("/api/tasks/{tid}/report")
def report(tid: str):
    d = task_dir(tid)
    path = (REPO / str(load(d / "STATUS.json", {}).get("report") or "")).resolve()
    if not any(str(path).startswith(str(root.resolve())) for root in (RESEARCH, PLANS)) or not path.is_file():
        raise HTTPException(404, "no report yet")
    return {"markdown": path.read_text(), "path": str(path.relative_to(REPO)), "files": files_of(d), "media": media_of(d)}


def media_of(d):
    """The NotebookLM podcast / video task_media.py makes for a task with `media:`, with its state."""
    items = (load(d / "media.json", {}) or {}).get("items", {})
    return [{"kind": k, "label": it.get("label", k), "status": it.get("status", "waiting"), "error": it.get("error"),
             "path": it.get("file") if it.get("status") == "ready" and (REPO / it.get("file", "")).is_file() else None}
            for k, it in items.items()]


def deliverables(d):
    """The task's files in output/research|plans: they share its YYYYMMDD-HHMM prefix."""
    return sorted(f for root in (RESEARCH, PLANS) for f in root.glob(d.name[:13] + "-*") if f.is_file())


def rendering(path):
    return subprocess.run(["pgrep", "-f", f"render.py [a-z]+ {path}$"], capture_output=True).returncode == 0


def files_of(d):
    out = []
    for f in deliverables(d):
        if f.suffix not in (".md", ".html") or (f.suffix == ".html" and f.with_suffix(".md").exists()):
            continue  # one row per document; a same-stem .html is the .md's layout, printed by its PDF
        rel = str(f.relative_to(REPO))
        out.append({"path": rel, "name": f.stem[14:] or f.stem, "audio_ok": f.suffix == ".md",
                    "pdf": f.with_suffix(".pdf").exists(), "mp3": f.with_suffix(".mp3").exists(),
                    "rendering": rendering(rel)})
    return out


@router.post("/api/tasks/{tid}/render")
async def render(tid: str, request: Request):
    """PDF or MP3 of one of the task's deliverables, in the background (audio takes minutes)."""
    d = task_dir(tid)
    body = await request.json()
    kind, rel = body.get("kind"), str(body.get("path", ""))
    if kind not in ("pdf", "audio") or rel not in {f["path"] for f in files_of(d)}:
        raise HTTPException(400, "kind (pdf|audio) and one of the task's files required")
    if kind == "audio" and not rel.endswith(".md"):
        raise HTTPException(400, "audio needs a .md script")
    if rendering(rel):
        raise HTTPException(409, "already rendering")
    with LOG.open("a") as log:  # then index, so the PDF folds into the file's vault note
        subprocess.Popen(["bash", "-c", 'uv run -q "$0" "$1" "$2" && python3 "$3"', str(RENDER), kind, rel, str(INDEXER)],
                         cwd=REPO, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    return {"ok": True}


@router.get("/api/tasks/{tid}/file")
def task_file(tid: str, path: str):
    f = (REPO / path).resolve()
    if f.suffix not in MEDIA_TYPES or f not in deliverables(task_dir(tid)):
        raise HTTPException(404, "no such file")
    return FileResponse(f, media_type=MEDIA_TYPES[f.suffix], filename=f.name)


@router.post("/api/tasks/{tid}/plan")
async def edit_plan(tid: str, request: Request):
    """The user's edits to a paused plan, plus their answer. History (done/active steps) is immutable;
    every change is written into the answer so the agent knows exactly what moved."""
    d = task_dir(tid)
    meta, status, plan = load(d / "meta.json", {}) or {}, load(d / "STATUS.json", {}), load(d / "PLAN.json", None)
    if not plan:
        raise HTTPException(404, "no plan")
    if alive(meta) or not answerable(d, status):
        raise HTTPException(409, "the team is working; edit when it pauses")
    body = await request.json()
    old = {s["id"]: s for s in plan.get("steps", [])}
    fixed = [s for s in plan["steps"] if s.get("status") in ("done", "active", "skipped")]
    used = set(old)
    editable, changes = [], []
    for ns in body.get("steps") or []:
        sid = ns.get("id")
        if sid in old and old[sid] in fixed:
            continue
        if sid in old:
            s = dict(old[sid])
            title = str(ns.get("title", s["title"])).strip()[:200]
            if title and title != s["title"]:
                changes.append(f'{sid} reworded to "{title}"')
                s["title"] = title
            if ns.get("owner") in OWNERS and ns["owner"] != s.get("owner"):
                changes.append(f"{sid} reassigned from {s.get('owner')} to {ns['owner']}")
                s["owner"] = ns["owner"]
            if ns.get("checkpoint") and not s.get("checkpoint"):
                s["checkpoint"] = {"stakes": "Added by the user.", "question": f"Ready for: {s['title']}?", "options": ["Go", "Skip it"]}
                changes.append(f"{sid} checkpoint added by the user")
            elif not ns.get("checkpoint") and s.get("checkpoint"):
                s["checkpoint"] = None
                changes.append(f"{sid} checkpoint removed by the user")
            editable.append(s)
        else:
            title = str(ns.get("title", "")).strip()[:200]
            if not title:
                continue
            n = 1
            while f"s{n}" in used:
                n += 1
            used.add(f"s{n}")
            owner = ns.get("owner") if ns.get("owner") in OWNERS else "you"
            editable.append({"id": f"s{n}", "title": title, "owner": owner, "status": "pending",
                             "checkpoint": None, "note": "", "findings": []})
            changes.append(f's{n} added by the user ({owner}): "{title}"')
    old_order = [s["id"] for s in plan["steps"] if s not in fixed]
    new_order = [s["id"] for s in editable if s["id"] in old]
    if [x for x in old_order if x in new_order] != new_order:
        changes.append("the user reordered the remaining steps to: " + ", ".join(s["id"] for s in editable))
    kept = {s["id"] for s in editable}
    changes += [f'{sid} removed by the user ("{old[sid]["title"]}")' for sid in old if old[sid] not in fixed and sid not in kept]
    plan["steps"] = fixed + editable
    plan["updated"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    save(d / "PLAN.json", plan)
    answer = str(body.get("answer") or "Go").strip()
    text = answer + ("\n\nThe user edited the plan:\n- " + "\n- ".join(changes) if changes else "")
    (d / "answers").mkdir(exist_ok=True)
    (d / "answers" / f"{time.strftime('%Y%m%d-%H%M%S')}.md").write_text(text + "\n")
    return {"ok": True, "changes": changes}


@router.post("/api/tasks/{tid}/flag")
async def flag_receipt(tid: str, request: Request):
    """Mark a source the plan used as wrong or stale. The agent stops trusting it; a vault note
    also gets a dated warning, so the correction outlives this plan."""
    d = task_dir(tid)
    body = await request.json()
    ref, reason = str(body.get("ref", "")), body.get("reason")
    if reason not in ("wrong", "stale") or not ref:
        raise HTTPException(400, "ref and reason (wrong|stale) required")
    with (d / "flags.jsonl").open("a") as f:
        f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "ref": ref, "reason": reason}) + "\n")
    note = (REPO / ref).resolve()
    vault_note = str(note).startswith(str(VAULT.resolve()) + "/") and note.suffix == ".md" and note.is_file()
    if vault_note:
        with note.open("a") as f:
            f.write(f"\n> [!warning] Flagged as {reason} from the console on {time.strftime('%Y-%m-%d')} "
                    f"(plan {tid}). Verify before relying on it.\n")
    return {"ok": True, "vault_note_marked": vault_note}
