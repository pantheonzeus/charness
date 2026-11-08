#!/usr/bin/env python3
"""Media for a finished console task: a NotebookLM podcast and/or video overview of its report, downloaded.

  task_media.py <task id>            notebook, sources, generate, wait, download (idempotent, resumes)
  task_media.py <task id> --dry-run  print account, sources and what is held back, change nothing

Started by webapp/tasks.py when a task whose TASK.md says `media: audio, video` reaches done. Reads the
report named in STATUS.json. Account (TASK.md `media_account:`, principal's call 2026-10-31):
  work      the nlm profile signed in to an address under the active employer's domains
  personal  (default) a profile signed in to an address under no employer's domains
A missing profile fails the media, never falls back to the other account. Sources: public URLs cited in
the report and the plan's receipts, plus the report text only if scripts/outbound_gate.py (public mode)
finds nothing in it. Files land beside the report as <stem>-podcast.m4a / <stem>-video.mp4; state in
output/tasks/<id>/media.json. When nothing is left generating, Jarvis iMessages "ready" (the title only for personal tasks and only
if the outbound gate passes it); playback is in the console, over Tailscale on the phone.
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[5]
TASKS = REPO / "output" / "tasks"
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "webapp"))
import employer  # noqa: E402
import outbound_gate  # noqa: E402
import push  # noqa: E402

TITLE_PREFIX = "Research · "
INTERNAL_HOSTS = ("slack.com", "mail.google.com", "docs.google.com", "drive.google.com", "calendar.google.com",
                  "meet.google.com", "zoom.us", "teams.microsoft.com", "localhost", "127.0.0.1", "notebooklm.google.com")
MAX_URLS = 25
KINDS = {"audio": ("podcast", ".m4a", ["audio", "create", "-f", "deep_dive", "-l", "default"]),
         "video": ("video", ".mp4", ["video", "create", "-f", "explainer"])}
WAIT = 3600        # seconds for all generations together; a video overview can take 20-30 minutes
POLL = 30
URL_RX = re.compile(r"https?://[^\s)\]>\"'`]+")


def nlm(profile, *args, timeout=900):
    r = subprocess.run(["nlm", *args], capture_output=True, text=True, timeout=timeout,
                       env={**os.environ, "NLM_PROFILE": profile})
    if r.returncode:
        raise RuntimeError(f"nlm {args[0]} {args[1] if len(args) > 1 else ''}: {(r.stderr or r.stdout).strip()[-400:]}")
    return r.stdout


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return dict(re.findall(r"^(\w+):\s*(.+?)\s*$", m.group(1), re.M)) if m else {}


def employer_domains(active_only):
    slugs = [employer.active()] if active_only else employer.packs()
    return {d.lower() for s in slugs if s for d in employer.get("employer.domains", [], s)}


def profile_for(account):
    """The nlm profile for this account, by the signed-in address's domain, or raise."""
    out = subprocess.run(["nlm", "login", "profile", "list"], capture_output=True, text=True, timeout=60).stdout
    profiles = re.findall(r"^\s+([\w.-]+):\s*(\S+@\S+)", out, re.M)
    work, every = employer_domains(True), employer_domains(False)
    for name, email in profiles:
        dom = email.split("@")[1].lower()
        if (account == "work" and dom in work) or (account == "personal" and dom not in every):
            return name
    hint = "" if account == "work" else " Sign one in once: nlm login --profile personal"
    raise RuntimeError(f"no {account} NotebookLM profile ({', '.join(e for _, e in profiles) or 'none'}).{hint}")


def public(urls):
    own = employer_domains(False)
    out = []
    for u in urls:
        u = u.rstrip(".,;:")
        host = (urlparse(u).hostname or "").lower()
        if host and not any(host == h or host.endswith("." + h) for h in (*INTERNAL_HOSTS, *own)) and u not in out:
            out.append(u)
    return out[:MAX_URLS]


def sources(tid, report):
    """(public urls, [(title, text)] that may leave the Mac, [held back])"""
    text = report.read_text()
    urls = URL_RX.findall(text)
    plan = TASKS / tid / "PLAN.json"
    if plan.exists():
        urls += URL_RX.findall(plan.read_text())
    body = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    findings = outbound_gate.scan(body, public=True)
    if findings:
        return public(urls), [], [f"report text: outbound gate ({'; '.join(findings[:3])})"]
    return public(urls), [(f"Report: {report.stem}"[:100], body)], []


def status(profile, nb, aid):
    for a in json.loads(nlm(profile, "studio", "status", nb, "--json") or "[]"):
        if aid in (a.get("artifact_id"), a.get("id")):
            return str(a.get("status", "")).lower()
    return ""


def notify(state, title):
    ready = [state["items"][k]["label"] for k in state["items"] if state["items"][k].get("status") == "ready"]
    failed = [state["items"][k]["label"] for k in state["items"] if state["items"][k].get("status") == "failed"]
    if state.get("notified"):
        return
    what = " and ".join(ready) or "nothing"
    msg = f"Jarvis: {what} ready: {title}. Play it in the console." + (f" {' and '.join(failed)} failed." if failed else "")
    if not ready:
        msg = f"Jarvis: {' and '.join(failed)} failed for {title}. Details on the Mac."
    if state.get("account") == "work" or outbound_gate.scan(msg, public=True):   # work titles never leave the Mac
        msg = re.sub(re.escape(f": {title}") if ready else re.escape(f" for {title}"), " for your research task", msg)
    if push.send(msg):
        state["notified"] = msg


def main(tid, dry):
    d = TASKS / tid
    fm, st_json = frontmatter((d / "TASK.md").read_text()), json.loads((d / "STATUS.json").read_text())
    kinds = [k for k in re.split(r"[,\s]+", fm.get("media", "").lower()) if k in KINDS]
    report = REPO / str(st_json.get("report") or "")
    if not kinds or not report.is_file():
        sys.exit(f"{tid}: nothing to make (media: {fm.get('media')!r}, report: {st_json.get('report')!r})")
    title = fm.get("title", tid)
    account = "work" if fm.get("media_account", "").strip().lower() == "work" else "personal"
    state_file = d / "media.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {}
    state.setdefault("items", {})

    def save():
        state_file.write_text(json.dumps(state, indent=1, ensure_ascii=False))

    if dry:
        urls, texts, held = sources(tid, report)
        try:
            prof = profile_for(account)
        except RuntimeError as e:
            prof = f"(none: {e})"
        print(json.dumps({"account": account, "profile": prof, "media": kinds, "urls": urls,
                          "texts": [t for t, _ in texts], "held_back": held}, indent=1))
        return 0

    try:
        profile = state.get("profile") or profile_for(account)
        state["profile"], state["account"] = profile, account
        if not state.get("notebook"):
            state["notebook"] = json.loads(nlm(profile, "notebook", "create", f"{TITLE_PREFIX}{title}"[:100], "--json"))["notebook_id"]
            save()
            urls, texts, held = sources(tid, report)
            state["held_back"], state["refused"] = held, []
            for t, text in texts:
                nlm(profile, "source", "add", state["notebook"], "--text", text[:400_000], "--title", t, "--wait", "--wait-timeout", "300")
            for u in urls:
                try:
                    nlm(profile, "source", "add", state["notebook"], "--url", u, "--wait", "--wait-timeout", "300")
                except (RuntimeError, subprocess.TimeoutExpired) as e:
                    state["refused"].append(f"{u}: {str(e)[-120:]}")
            save()
    except (RuntimeError, subprocess.TimeoutExpired, KeyError, ValueError) as e:
        for k in kinds:
            state["items"][k] = {"label": KINDS[k][0], "status": "failed", "error": str(e)[-300:]}
        save()
        notify(state, title)
        save()
        print(f"  ! {tid}: {str(e)[-300:]}", file=sys.stderr)
        return 1

    # Phase 1: start every generation before waiting on any.
    focus = f"{title}. {st_json.get('summary', '')}"[:500]
    for k in kinds:
        label, ext, cmd = KINDS[k]
        it = state["items"].setdefault(k, {"label": label})
        it["file"] = str(report.with_name(f"{report.stem}-{label}{ext}").relative_to(REPO))
        if it.get("artifact") or (REPO / it["file"]).exists():
            continue
        try:
            it["artifact"] = json.loads(nlm(profile, *cmd, state["notebook"], "--language", "en", "--focus", focus,
                                            "-y", "--json"))["artifact_id"]
            it["status"] = "generating"
        except (RuntimeError, subprocess.TimeoutExpired, KeyError, ValueError) as e:
            it["status"], it["error"] = "failed", str(e)[-300:]
        save()

    # Phase 2: wait for all, download each as it completes.
    deadline = time.monotonic() + WAIT
    while True:
        for k, it in state["items"].items():
            if it.get("status") != "generating":
                continue
            try:
                now = status(profile, state["notebook"], it["artifact"])
                if now == "completed":
                    nlm(profile, "download", k, state["notebook"], "--id", it["artifact"], "-o", str(REPO / it["file"]), "--no-progress")
                    it["status"] = "ready"
                elif now in ("failed", "error"):
                    it["status"], it["error"] = "failed", f"NotebookLM reports {k} {now}"
            except (RuntimeError, subprocess.TimeoutExpired, ValueError) as e:
                it["error"] = str(e)[-300:]   # transient: keep polling until the deadline
            save()
        if not any(it.get("status") == "generating" for it in state["items"].values()) or time.monotonic() > deadline:
            break
        time.sleep(POLL)

    counts = {s: sum(it.get("status") == s for it in state["items"].values()) for s in ("ready", "generating", "failed")}
    if not counts["generating"]:
        notify(state, title)
        save()
    print(f"Task media {tid}: ready {counts['ready']} · still generating {counts['generating']} (re-run to resume) "
          f"· failed {counts['failed']}", file=sys.stderr)
    return 1 if counts["failed"] or counts["generating"] else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or not re.fullmatch(r"[0-9]{8}-[0-9]{4}-[a-z0-9-]{1,60}", a[0]):
        sys.exit(__doc__)
    sys.exit(main(a[0], "--dry-run" in a))
