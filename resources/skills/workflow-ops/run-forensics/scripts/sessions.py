#!/usr/bin/env python3
"""Session forensics: what goes wrong in the principal's own sessions, and the lessons the harness keeps from it.

forensics.py reads headless runs; nothing read the interactive sessions, where corrections, interrupts and
repeated asks show what the harness gets wrong for the person using it. This reads the session archive
(scripts/session_archive.py, origin `human` only, so regression probes and jobs stay out) and writes a digest of
deterministic signals. Judging which signal is a real lesson is a language question for a model (the scout,
or a session on "learn from sessions"); keeping the lessons is this script's job, by delta only (ACE,
arXiv:2510.04618: whole-context rewrites collapsed 18,282 tokens to 122 and fell below baseline).

  scan [--days N]                         digest of the last N days (default 7) → output/run-forensics/sessions-<date>.md
  lesson add --text T --target P --session S [--session S2 …] [--replaces ID]
                                          a new lesson; P = a repo path (skill, hook, agent file) or new-skill:<category>/<slug>
  lesson vote ID helpful|harmful --session S [--note N]
                                          one more session for or against a lesson
  lesson mark ID proposed|applied|rejected|retired [--ref R]
  lessons [--ready]                       list; ready = candidate, ≥ 2 distinct sessions, helpful − harmful ≥ 2

A lesson's text never changes: a better wording is a new lesson with --replaces (the old one retires).
Provenance is set from the archive, not by the writer: a lesson drawn from any session that took in outside
text is `derived-untrusted` (arXiv:2607.29167: consolidation launders outside text into trusted history).
Lessons and the digest quote the principal's prompts and may name clients: they stay in output/ (git-ignored),
and nothing from them enters a skill except as a client-free procedure, on the principal's Go.
Stdlib only, Python 3.9.
"""
import argparse
import collections
import datetime as dt
import json
import re
import sys

import forensics

REPO = forensics.REPO
sys.path.insert(0, str(REPO / "scripts"))
import session_archive as archive  # noqa: E402

OUT = REPO / "output" / "run-forensics"
LESSONS = OUT / "lessons.json"
STATUSES = ("candidate", "proposed", "applied", "rejected", "retired")
REDIRECT = re.compile(
    r"^\s*(no\b|nope|nein|wrong|not (that|this|what)|don'?t\b|do not\b|stop (it|that|doing)\b|instead\b|actually\b|why did you|"
    r"i (said|told you|asked)|again\b|you (forgot|missed|didn'?t)|that'?s not|please don'?t|never\b)"
    r"|not what i|instead of|should have|you ignored|i already", re.I)
STOP = set("a an the to me my for of and in on at is it this that please can you could would i we".split())


def ask_key(text):
    words = [w for w in re.findall(r"[a-zäöüß]+", text.lower()) if w not in STOP]
    return " ".join(words[:4])


def human_sessions(days):
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%d")
    return [e for e in archive.current() if e["origin"] == "human" and (e.get("started") or "")[:10] >= since]


def signals(e):
    """Deterministic signals of one archived session."""
    s = {"codes": collections.Counter(), "examples": {}, "interrupts": 0, "rejections": 0, "hook_stops": 0,
         "redirects": [], "prompts": []}
    calls, first = {}, True
    for raw in archive.read_stored(e).splitlines():
        try:
            m = json.loads(raw)
        except ValueError:
            continue
        content, ts = (m.get("message") or {}).get("content"), (m.get("timestamp") or "")[:16]
        if m.get("type") == "assistant" and isinstance(content, list):
            for b in content:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    calls[b.get("id")] = b.get("name", "")
            continue
        if m.get("type") != "user":
            continue
        text = archive.text_of(content)
        if "[Request interrupted by user" in text:
            s["interrupts"] += 1
        if re.search(r"Stop hook feedback|hook blocking error", text):
            s["hook_stops"] += 1
        if (m.get("origin") or {}).get("kind") == "human" and text.strip() and not text.lstrip().startswith("<"):
            t = archive.flat(text.strip())
            s["prompts"].append(t)
            if not first and REDIRECT.search(t[:200]):
                s["redirects"].append((ts, t[:220]))
            first = False
        for b in content if isinstance(content, list) else []:
            if not (isinstance(b, dict) and b.get("type") == "tool_result" and b.get("is_error")):
                continue
            body = str(b.get("content"))
            if re.search(r"user doesn'?t want to proceed|rejected by the user|user rejected", body, re.I):
                s["rejections"] += 1
                continue
            code = forensics.step_code(calls.get(b.get("tool_use_id"), ""), body)
            s["codes"][code] += 1
            s["examples"].setdefault(code, forensics.normalize(body))
    return s


def scan(args):
    rows = [(e, signals(e)) for e in human_sessions(args.days)]
    codes, examples, asks = collections.Counter(), {}, collections.defaultdict(set)
    for e, s in rows:
        for c, n in s["codes"].items():
            if forensics.is_tracked(c):
                codes[c] += n
                examples.setdefault(c, s["examples"][c])
        for p in s["prompts"]:
            k = ask_key(p)
            if len(k.split()) >= 2:
                asks[k].add(e["session_id"])
    today = dt.date.today().strftime("%Y%m%d")
    L = [f"# Session forensics — {len(rows)} human sessions, last {args.days} days ({dt.date.today()})", "",
         "Source: output/.sessions (scripts/session_archive.py). Signals are deterministic; whether one is a lesson is "
         "a judgement (run-forensics SKILL.md, section E). Open a session with "
         "`python3 scripts/session_archive.py show <id> [--grep RX]`.", "",
         f"- interrupts {sum(s['interrupts'] for _, s in rows)} · tool calls you rejected "
         f"{sum(s['rejections'] for _, s in rows)} · Stop-hook blocks {sum(s['hook_stops'] for _, s in rows)} · "
         f"redirect candidates {sum(len(s['redirects']) for _, s in rows)}", "",
         "## Failure codes in your sessions (tracked codes, same taxonomy as headless runs)", ""]
    L += [f"- {c} ×{n} — {examples[c]}" for c, n in codes.most_common(10)] or ["- none"]
    L += ["", "## Repeated asks (same opening words in ≥ 3 sessions: a candidate for a skill or a script)", ""]
    rep = sorted(((k, v) for k, v in asks.items() if len(v) >= 3), key=lambda kv: -len(kv[1]))
    L += [f"- \"{k}\" in {len(v)} sessions: {', '.join(sorted(x[:8] for x in v)[:6])}" for k, v in rep[:12]] or ["- none"]
    L += ["", "## Redirect candidates (a later prompt that may correct the agent; read the turn before it)", ""]
    for e, s in rows:
        for ts, t in s["redirects"]:
            L.append(f"- {e['session_id'][:8]} {ts} {'(tainted) ' if e.get('taint') else ''}\"{t}\"")
    if not any(s["redirects"] for _, s in rows):
        L.append("- none")
    L += ["", "## Sessions", "", "| started | id | tools | errors | interrupts | redirects | skills | title |",
          "|---|---|---|---|---|---|---|---|"]
    for e, s in rows:
        L.append(f"| {(e.get('started') or '')[:16]} | {e['session_id'][:8]} | {e['n_tools']} | {sum(s['codes'].values())} "
                 f"| {s['interrupts']} | {len(s['redirects'])} | {', '.join(e.get('skills_used', [])[:3]) or '-'} "
                 f"| {(e.get('title') or '-').replace('|', '/')[:80]} |")
    ready = [l for l in load().values() if is_ready(l)]
    L += ["", f"## Lessons ready to propose: {len(ready)} (`sessions.py lessons --ready`)"]
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"sessions-{today}.md"
    path.write_text("\n".join(L) + "\n")
    print(f"{path.relative_to(REPO)}: {len(rows)} sessions, {len(rep)} repeated asks, "
          f"{sum(len(s['redirects']) for _, s in rows)} redirect candidates, {len(ready)} lessons ready")


def load():
    return json.loads(LESSONS.read_text()) if LESSONS.exists() else {}


def save(lessons):
    OUT.mkdir(parents=True, exist_ok=True)
    LESSONS.write_text(json.dumps(lessons, indent=1, ensure_ascii=False) + "\n")


def is_ready(l):
    return l["status"] == "candidate" and len(set(l["sessions"])) >= 2 and l["helpful"] - l["harmful"] >= 2


def taint_of(sids):
    by_id = {e["session_id"]: e for e in archive.current()}
    missing = [s for s in sids if not any(k.startswith(s) for k in by_id)]
    if missing:
        raise SystemExit(f"not in the session archive: {', '.join(missing)} (run scripts/session_archive.py sync)")
    full = [next(k for k in by_id if k.startswith(s)) for s in sids]
    return full, sorted({t for k in full for t in by_id[k].get("taint", [])})


def stamp(l, kinds):
    l["taint"] = sorted(set(l.get("taint", [])) | set(kinds))
    l["provenance"] = "derived-untrusted" if l["taint"] else "principal-sessions"


def lesson(args):
    lessons, today = load(), dt.date.today().isoformat()
    if args.op == "add":
        t = args.target
        if not (t.startswith("new-skill:") and re.fullmatch(r"new-skill:[a-z-]+/[a-z0-9-]+", t) or (REPO / t).exists()):
            raise SystemExit(f"target {t}: give an existing repo path or new-skill:<category>/<slug>")
        sids, kinds = taint_of(args.session)
        lid = f"L{len(lessons) + 1}"
        lessons[lid] = {"text": args.text, "target": t, "sessions": sids, "helpful": len(set(sids)), "harmful": 0,
                        "status": "candidate", "created": today, "updated": today, "log": [f"{today} add"]}
        stamp(lessons[lid], kinds)
        if args.replaces:
            old = lessons[args.replaces]
            old["status"], old["updated"] = "retired", today
            old["log"].append(f"{today} retired, replaced by {lid}")
            lessons[lid]["replaces"] = args.replaces
        print(f"{lid} added ({lessons[lid]['provenance']})")
    elif args.op == "vote":
        l = lessons[args.id]
        sids, kinds = taint_of(args.session)
        l[args.vote] += 1
        l["sessions"] = list(dict.fromkeys(l["sessions"] + sids))
        l["updated"] = today
        l["log"].append(f"{today} {args.vote} {sids[0][:8]}" + (f": {args.note}" if args.note else ""))
        stamp(l, kinds)
        print(f"{args.id}: helpful {l['helpful']}, harmful {l['harmful']}, {len(set(l['sessions']))} sessions"
              + (" — ready" if is_ready(l) else ""))
    else:
        l = lessons[args.id]
        l["status"], l["updated"] = args.status, today
        l["log"].append(f"{today} {args.status}" + (f" ({args.ref})" if args.ref else ""))
        print(f"{args.id} → {args.status}")
    save(lessons)


def list_lessons(args):
    for lid, l in load().items():
        if args.ready and not is_ready(l):
            continue
        print(f"{lid} [{l['status']}{', ready' if is_ready(l) else ''}] +{l['helpful']}/−{l['harmful']} "
              f"{len(set(l['sessions']))} sessions, {l['provenance']} → {l['target']}\n    {l['text']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("scan")
    p.add_argument("--days", type=int, default=7)
    p.set_defaults(fn=scan)
    p = sub.add_parser("lesson")
    ops = p.add_subparsers(dest="op", required=True)
    q = ops.add_parser("add")
    q.add_argument("--text", required=True)
    q.add_argument("--target", required=True)
    q.add_argument("--session", action="append", required=True)
    q.add_argument("--replaces")
    q = ops.add_parser("vote")
    q.add_argument("id")
    q.add_argument("vote", choices=("helpful", "harmful"))
    q.add_argument("--session", action="append", required=True)
    q.add_argument("--note")
    q = ops.add_parser("mark")
    q.add_argument("id")
    q.add_argument("status", choices=STATUSES[1:])
    q.add_argument("--ref")
    p.set_defaults(fn=lesson)
    p = sub.add_parser("lessons")
    p.add_argument("--ready", action="store_true")
    p.set_defaults(fn=list_lessons)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
