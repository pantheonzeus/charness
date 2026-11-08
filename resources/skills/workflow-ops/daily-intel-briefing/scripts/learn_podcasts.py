#!/usr/bin/env python3
"""Learning podcasts: one NotebookLM deep dive per briefing topic, 5-10 minutes, downloaded.

  learn_podcasts.py <YYYY-MM-DD>            notebooks, sources, generate, wait, download (idempotent)
  learn_podcasts.py <YYYY-MM-DD> --dry-run  print what each notebook would get, change nothing

Reads the `learn` packs the daily-intel run wrote into output/briefings/<date>.json (one per section
with items: a focus brief plus the public URLs the run researched). Per pack: a notebook
"Daily Intel · <date> · <title>", the URLs plus the section's items and its deep-dive page as text
(each text only if scripts/outbound_gate.py, public mode, finds nothing), then
`nlm audio create -f deep_dive -l short --focus <brief>`. All generations start before any wait.
Audio lands in output/briefings/<date>/learn/<section>.m4a; state.json beside it makes re-runs resume.
daily_audio.py skips the "Daily Intel · " prefix: these notebooks are downloaded here, not distilled.
When nothing is left generating, Jarvis iMessages you the list of episodes (topic: title) once per day via
webapp/push.py. These titles come from public web research, so they may go out (your call, 2026-10-31); the list
still passes outbound_gate first, and a flagged list goes out as a count only.
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[5]
BRIEFINGS = REPO / "output" / "briefings"
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "webapp"))
import employer  # noqa: E402
import outbound_gate  # noqa: E402
import push  # noqa: E402

TITLE_PREFIX = "Daily Intel · "   # daily_audio.py skips notebooks with this prefix
INTERNAL_HOSTS = ("slack.com", "mail.google.com", "docs.google.com", "drive.google.com", "calendar.google.com",
                  "meet.google.com", "zoom.us", "teams.microsoft.com", "localhost", "127.0.0.1", "notebooklm.google.com")
MAX_URLS = 15
WAIT = 1800        # seconds for all generations together; a short deep dive takes ~5-10 minutes
POLL = 20


def nlm(*args, timeout=900):
    r = subprocess.run(["nlm", *args], capture_output=True, text=True, timeout=timeout)
    if r.returncode:
        raise RuntimeError(f"nlm {args[0]} {args[1] if len(args) > 1 else ''}: {(r.stderr or r.stdout).strip()[-400:]}")
    return r.stdout


def public(urls):
    own = {d.lower() for s in employer.packs() for d in employer.get("employer.domains", [], s)}
    out = []
    for u in urls:
        host = (urlparse(str(u)).hostname or "").lower()
        if host and not any(host == h or host.endswith("." + h) for h in (*INTERNAL_HOSTS, *own)) and u not in out:
            out.append(u)
    return out[:MAX_URLS]


def texts(date, b, section):
    """The day's items for this section, and its deep-dive pages, as text sources."""
    s = next(x for x in b["sections"] if x["id"] == section)
    docs = [(f"Briefing {date}: {s['title']}", "\n\n".join(
        f"{it['headline']}\n{it['summary']}\nWhy it matters: {it['why_it_matters']}" for it in s["items"]))]
    ids = {it["id"] for it in s["items"]}
    for d in b.get("deep_dives") or []:
        page = BRIEFINGS / date / f"{d['id']}.md"
        if d.get("item_id") in ids and page.is_file():
            docs.append((f"Deep dive: {d['title']}"[:100], re.sub(r"\A---\n.*?\n---\n", "", page.read_text(), flags=re.S)))
    kept, held = [], []
    for title, text in docs:
        findings = outbound_gate.scan(text, public=True)
        if findings:
            held.append(f"{title}: outbound gate ({'; '.join(findings[:3])})")
        else:
            kept.append((title, text))
    return kept, held


def status(nb, aid):
    for a in json.loads(nlm("studio", "status", nb, "--json") or "[]"):
        if aid in (a.get("artifact_id"), a.get("id")):
            return str(a.get("status", "")).lower()
    return ""


def notify(date, b, packs, state, out):
    """One iMessage per day, once nothing is left generating: the list of ready episodes, topic and title."""
    marker = out / "notified"
    ready = [p for p in packs if state.get(p["section"], {}).get("status") == "ready"]
    if marker.exists() or not ready:
        return
    titles = {s["id"]: s["title"] for s in b["sections"]}
    failed = len(packs) - len(ready)
    msg = "\n".join([f"Jarvis: {len(ready)} learning podcast{'s' if len(ready) != 1 else ''} ready ({date})",
                     *(f"{n}. {titles.get(p['section'], p['section'])}: {p['title']}" for n, p in enumerate(ready, 1)),
                     *([f"{failed} failed, see learn/state.json"] if failed else []),
                     "Reply with a number to play it on the Mac, stop to end it."])
    if outbound_gate.scan(msg, public=True):
        msg = f"Jarvis: {len(ready)} learning podcasts ready ({date}). Titles held back by the outbound gate."
    if push.send(msg):
        marker.write_text(msg)


def main(date, dry):
    b = json.loads((BRIEFINGS / f"{date}.json").read_text())
    packs = b.get("learn") or []
    out = BRIEFINGS / date / "learn"
    state_file = out / "state.json"
    state = json.loads(state_file.read_text()) if state_file.exists() else {}

    def save():
        out.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps(state, indent=1))

    if dry:
        for p in packs:
            kept, held = texts(date, b, p["section"])
            print(json.dumps({"section": p["section"], "urls": public(p["sources"]), "texts": [t for t, _ in kept],
                              "held_back": held, "focus": p["focus"]}, indent=1))
        return 0

    # Phase 1: notebook + sources + start generation, for every pack before waiting on any.
    for p in packs:
        sid, st = p["section"], state.setdefault(p["section"], {})
        if (out / f"{sid}.m4a").exists() or st.get("artifact"):
            continue
        try:
            if not st.get("notebook"):
                st["notebook"] = json.loads(nlm("notebook", "create", f"{TITLE_PREFIX}{date} · {p['title']}"[:100], "--json"))["notebook_id"]
                save()
                kept, held = texts(date, b, sid)
                st["held_back"], st["refused"] = held, []
                for title, text in kept:
                    nlm("source", "add", st["notebook"], "--text", text[:400_000], "--title", title, "--wait", "--wait-timeout", "300")
                for u in public(p["sources"]):
                    try:
                        nlm("source", "add", st["notebook"], "--url", u, "--wait", "--wait-timeout", "300")
                    except (RuntimeError, subprocess.TimeoutExpired) as e:
                        st["refused"].append(f"{u}: {str(e)[-120:]}")
            st["artifact"] = json.loads(nlm("audio", "create", st["notebook"], "-f", "deep_dive", "-l", "short",
                                            "--language", "en", "--focus", p["focus"], "-y", "--json"))["artifact_id"]
            st["status"] = "generating"
            print(f"  + generating: {sid}", file=sys.stderr)
        except (RuntimeError, subprocess.TimeoutExpired, KeyError, ValueError) as e:
            st["status"], st["error"] = "failed", str(e)[-300:]
            print(f"  ! {sid}: {st['error']}", file=sys.stderr)
        save()

    # Phase 2: wait for all, download each as it completes.
    deadline = time.monotonic() + WAIT
    while True:
        waiting = [s for s, st in state.items() if st.get("status") == "generating"]
        for sid in waiting:
            st = state[sid]
            try:
                now = status(st["notebook"], st["artifact"])
                if now == "completed":
                    nlm("download", "audio", st["notebook"], "--id", st["artifact"], "-o", str(out / f"{sid}.m4a"), "--no-progress")
                    st["status"] = "ready"
                    print(f"  ↓ {sid}.m4a", file=sys.stderr)
                elif now in ("failed", "error"):
                    st["status"], st["error"] = "failed", f"NotebookLM reports audio {now}"
            except (RuntimeError, subprocess.TimeoutExpired, ValueError) as e:
                st["error"] = str(e)[-300:]   # transient: keep polling until the deadline
            save()
        if not [s for s, st in state.items() if st.get("status") == "generating"] or time.monotonic() > deadline:
            break
        time.sleep(POLL)

    counts = {k: sum(st.get("status") == k for st in state.values()) for k in ("ready", "generating", "failed")}
    if not counts["generating"]:
        notify(date, b, packs, state, out)
    print(f"Learning podcasts {date}: {len(packs)} topics · ready {counts['ready']} · still generating "
          f"{counts['generating']} (re-run to resume) · failed {counts['failed']}", file=sys.stderr)
    return 1 if counts["failed"] or counts["generating"] else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a[0]):
        sys.exit(__doc__)
    sys.exit(main(a[0], "--dry-run" in a))
