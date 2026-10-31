# /// script
# requires-python = ">=3.10"
# ///
"""Role scout: find open roles that fit the principal's search profile, ping through Jarvis, push until applied.

  run                 launch the role-scout agent on the profile, merge the verified roles it found, notify
  check <STATE_ROOT>  validate the RESULT.json one run wrote
  mark <id> <status>  applied | skipped | new (by hand; Jarvis "done" = applied, "drop"/"noise" = skipped)
  status              JSON for the console

The profile (what fits) is output/role-scout/profile.md, private and git-ignored, edited by hand.
Roles live in output/role-scout/roles.json. A role stays in Jarvis for NAG_DAYS days: each day it is
not applied to or skipped it comes back as a new item (the push), then it goes stale.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
REPO = SKILL.parents[3]
OUT = REPO / "output" / "role-scout"
PROFILE = OUT / "profile.md"
ROLES = OUT / "roles.json"
STATE = OUT / "state.json"
LOCK = OUT / ".lock"
RATINGS = REPO / "output" / ".webapp" / "jarvis-ratings.jsonl"
RUN_AGENT = REPO / "scripts" / "run_agent.sh"
NAG_DAYS, MIN_FIT, MAX_NEW, MIN_QUERIES = 3, 70, 5, 8   # first live run stopped at 5 queries: too thin to trust a "nothing found"
STATUSES = ("new", "applied", "skipped", "stale")
FIELDS = ("title", "company", "location", "url", "posted", "fit", "why", "gaps", "cv_base")
CLI_ENV = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")}
REL = lambda p: str(Path(p).relative_to(REPO))
TOOLS = ["Read", "Glob", "Grep", "Write", "WebSearch", "WebFetch", "Bash(date:*)",
         f"Bash(uv run {REL(__file__)}:*)", f"Bash(uv run {__file__}:*)"]


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


def rid(url):
    """One id per posting: the URL without query, fragment or trailing slash."""
    return hashlib.sha1(re.sub(r"[?#].*$", "", url.strip()).rstrip("/").lower().encode()).hexdigest()[:10]


def check(root):
    root = Path(root)
    if not (root / "TASK.json").is_file():
        return [f"no TASK.json in {root}"]
    result = load(root / "RESULT.json", None)
    if not isinstance(result, dict) or not isinstance(result.get("roles"), list):
        return ['no RESULT.json: write {"roles": [...], "searched": [queries], "rejected": n}']
    errs = []
    if len(result.get("searched") or []) < MIN_QUERIES:
        errs.append(f"searched: run and list at least {MIN_QUERIES} queries across the profile's role types")
    if len(result["roles"]) > MAX_NEW:
        errs.append(f"at most {MAX_NEW} roles per run, found {len(result['roles'])}")
    for i, r in enumerate(result["roles"]):
        miss = [k for k in FIELDS if not r.get(k)]
        if miss:
            errs.append(f"roles[{i}]: missing {', '.join(miss)}")
        if not str(r.get("url", "")).startswith("http"):
            errs.append(f"roles[{i}]: url must be the posting itself")
        if not isinstance(r.get("fit"), int) or r["fit"] < MIN_FIT:
            errs.append(f"roles[{i}]: fit must be an integer >= {MIN_FIT} (drop weaker ones)")
        if r.get("verified") is not True:
            errs.append(f"roles[{i}]: verified must be true (you opened the posting and it is live)")
    return errs


def notify(title, message):
    subprocess.run(["osascript", "-e", f'display notification {json.dumps(message)} with title {json.dumps(title)}'],
                   capture_output=True)


def alive():
    try:
        os.kill(int(LOCK.read_text()), 0)
        return True
    except (OSError, ValueError):
        return False


def run():
    if alive():
        return log("previous run still alive; skipping")
    if not PROFILE.is_file():
        return log(f"no profile at {REL(PROFILE)}; nothing to search for")
    OUT.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(str(os.getpid()))
    try:
        stamp = time.strftime("%Y%m%d-%H%M%S")
        root = REPO / "output" / ".runs" / f"{stamp}-role-scout"
        root.mkdir(parents=True)
        known = load(ROLES, {"roles": {}})["roles"]
        save(root / "TASK.json", {"run": stamp, "profile": REL(PROFILE), "min_fit": MIN_FIT, "max_new": MAX_NEW,
                                  "known": [{"url": r["url"], "title": r["title"], "company": r["company"]} for r in known.values()]})
        (root / "RESPONSE.md").write_text(f"# role-scout {stamp}\n- [ ] read the profile\n- [ ] searched (queries listed)\n"
            "- [ ] opened every candidate posting and checked it is live\n- [ ] RESULT.json written\n"
            "- [ ] role_scout.py check prints OK\n")
        prompt = (f"Read and follow resources/skills/workflow-ops/role-scout/SKILL.md (a repo skill: open it with Read, "
                  f"not the Skill tool) for the task packet {REL(root)}/TASK.json. Your STATE_ROOT is {REL(root)}/. "
                  f"Finish with `uv run {REL(__file__)} check {REL(root)}` printing OK.")
        subprocess.run(["bash", str(RUN_AGENT), "role-scout", str(root / "RESPONSE.md"), prompt,
                        "--permission-mode", "acceptEdits", "--allowedTools", *TOOLS],
                       cwd=REPO, env=CLI_ENV, stdin=subprocess.DEVNULL)
        errs = check(root)
        added = merge(load(root / "RESULT.json", {}).get("roles") or []) if not errs else []
        log(f"{len(added)} new role(s); check {'OK' if not errs else 'FAILED: ' + '; '.join(errs[:3])}")
        if added:
            notify("Jarvis", f"{len(added)} role{'s' if len(added) > 1 else ''} that fit. Apply while they're fresh.")
        state = load(STATE, {"runs": []})
        state["runs"] = (state["runs"] + [{"at": stamp, "ok": not errs, "errors": errs[:5], "added": len(added)}])[-300:]
        save(STATE, state)
    finally:
        LOCK.unlink(missing_ok=True)


def merge(found):
    data = load(ROLES, {"roles": {}})
    added = []
    for r in found:
        i = rid(r["url"])
        if i in data["roles"]:
            continue
        data["roles"][i] = {**{k: r[k] for k in FIELDS}, "id": i, "status": "new", "found": time.time()}
        added.append(i)
    save(ROLES, data)
    return added


def sync():
    """Your calls in Jarvis close a role: done = applied, drop or noise = skipped. Old untouched ones go stale."""
    data = load(ROLES, {"roles": {}})
    calls = {}
    try:
        for line in RATINGS.read_text().splitlines():
            r = json.loads(line)
            if r.get("id", "").startswith("role:"):
                calls[r["id"].split(":")[1]] = r.get("rated")
    except (OSError, ValueError):
        pass
    changed = False
    for i, r in data["roles"].items():
        if r["status"] != "new":
            continue
        new = {"done": "applied", "drop": "skipped", "noise": "skipped"}.get(calls.get(i))
        if not new and time.time() - r["found"] > NAG_DAYS * 86400:
            new = "stale"
        if new:
            r["status"], r["closed"], changed = new, time.time(), True
    if changed:
        save(ROLES, data)
    return data


def open_roles():
    """Jarvis items: one per open role per day, so a role you haven't acted on comes back the next day."""
    out = []
    for r in sync()["roles"].values():
        if r["status"] != "new":
            continue
        day = int((time.time() - r["found"]) // 86400)
        lead = (f"A role that fits: {r['title']} at {r['company']}." if day == 0 else
                f"Day {day + 1}: you haven't applied to {r['title']} at {r['company']} yet. The CV base is ready.")
        out.append({"id": f"role:{r['id']}:{day}", "kind": "role", "title": f"{r['title']} — {r['company']} ({r['location']})",
                    "lead": lead, "summary": f"Fit {r['fit']}: {r['why']} Gaps: {r['gaps']} CV base: {r['cv_base']}.",
                    "ts": r["found"], "open": {"href": r["url"]}})
    return out


def mark(i, status):
    if status not in STATUSES:
        sys.exit(f"status must be one of {STATUSES}")
    data = load(ROLES, {"roles": {}})
    if i not in data["roles"]:
        sys.exit(f"unknown role {i}")
    data["roles"][i].update(status=status, closed=time.time())
    save(ROLES, data)


def status():
    roles = sync()["roles"].values()
    return {"running": alive(), "last_run": (load(STATE, {"runs": []})["runs"] or [None])[-1],
            "by_status": {s: sum(r["status"] == s for r in roles) for s in STATUSES},
            "open": [{k: r[k] for k in ("id", "title", "company", "location", "fit", "url")} for r in roles if r["status"] == "new"]}


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["run"]:
        run()
    elif a[:1] == ["check"] and len(a) == 2:
        e = check(a[1])
        print("OK" if not e else "\n".join(e))
        sys.exit(1 if e else 0)
    elif a[:1] == ["mark"] and len(a) == 3:
        mark(a[1], a[2])
    elif a[:1] == ["status"]:
        print(json.dumps(status(), indent=1, ensure_ascii=False))
    else:
        sys.exit(__doc__)
