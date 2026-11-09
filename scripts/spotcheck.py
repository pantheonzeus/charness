#!/usr/bin/env python3
"""Rubber-stamp check on the principal's approvals of agent output (agentic-service-blueprint: "approval
gates rot into rubber stamps"; approvals under 3 seconds are the automation-bias signal).

Two sources, both written as the decisions happen:
  output/mail-triage/decisions.json      console mail decisions: action, dwell_s (seconds on screen),
                                          bulk ("mark all read"), edited (a sent draft was changed)
  output/.runs/_forensics/hooks.jsonl    send-gate allows: approval_s (seconds from read-back to yes)

  python3 scripts/spotcheck.py report [--days 7]          the signals for the window
  python3 scripts/spotcheck.py sample [--n 5] [--days 7]  the report, then a blind sheet: re-decide n mails without
                                                          the original call -> output/spotcheck/<YYYY>-W<ww>.md
                                                          (launchd, Sundays 08:00: scripts/com.cbrain.spotcheck.plist)
  python3 scripts/spotcheck.py score <sheet.md>           agreement with the original calls, appended to
                                                          output/spotcheck/scores.jsonl

Low agreement on the blind sheet means the original calls were not really made; ticks of "triage right?"
are labels for a future mail-triage quality judge. The sheet holds mail text, so it stays in output/.
Stdlib only.
"""
import argparse
import contextlib
import datetime as dt
import io
import json
import os
import random
import re
import sys
from pathlib import Path

REPO = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parent.parent)
MAIL = REPO / "output" / "mail-triage"
HOOKS = REPO / "output" / ".runs" / "_forensics" / "hooks.jsonl"
OUT = REPO / "output" / "spotcheck"
FAST = 3.0
CALLS = {"read": "read", "done": "done", "sent": "reply", "dismissed": "dismiss"}   # original action -> sheet call


def load(path, default):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def decisions(days):
    since = (dt.datetime.now() - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
    return {k: v for k, v in load(MAIL / "decisions.json", {}).items() if v.get("at", "") >= since}


def report(days):
    d = decisions(days)
    timed = [v for v in d.values() if "dwell_s" in v and not v.get("bulk")]
    sent = [v for v in d.values() if v.get("action") == "sent" and "edited" in v]
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    gate = []
    if HOOKS.is_file():
        for line in HOOKS.read_text(errors="ignore").splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("hook") == "send-gate" and e.get("decision") == "allow" and e.get("ts", "") >= since:
                gate.append(e)
    gate_timed = [e for e in gate if isinstance(e.get("approval_s"), (int, float))]
    by = {}
    for v in d.values():
        by[v.get("action", "?")] = by.get(v.get("action", "?"), 0) + 1
    print(f"Approvals, last {days} days")
    print(f"  mail decisions: {len(d)} ({', '.join(f'{k} {n}' for k, n in sorted(by.items())) or 'none'})")
    print(f"  bulk 'mark all read': {sum(1 for v in d.values() if v.get('bulk'))}")
    print(f"  decided under {FAST:g} s on screen: {sum(1 for v in timed if v['dwell_s'] < FAST)} of {len(timed)} timed")
    print(f"  drafts sent unedited: {sum(1 for v in sent if not v['edited'])} of {len(sent)} sent")
    print(f"  send-gate yes under {FAST:g} s after the read-back: "
          f"{sum(1 for e in gate_timed if e['approval_s'] < FAST)} of {len(gate_timed)} timed ({len(gate)} sends)")
    return 0


def sample(n, days):
    d = decisions(days)
    picked = [k for k in d if not d[k].get("bulk")]
    random.shuffle(picked)
    rest = [k for k in d if d[k].get("bulk")]
    random.shuffle(rest)
    picked = (picked + rest)[:n]
    if not picked:
        print(f"no mail decisions in the last {days} days")
        return 1
    year, week, _ = dt.date.today().isocalendar()
    sheet = OUT / f"{year}-W{week:02d}.md"
    signals = io.StringIO()
    with contextlib.redirect_stdout(signals):
        report(days)
    out = [f"# Blind spot-check — {year}-W{week:02d}", "", "```", signals.getvalue().rstrip(), "```", "",
           "Decide each mail again without looking up what you did. Tick one call and say whether the triage was right,",
           f"then: python3 scripts/spotcheck.py score {sheet.relative_to(REPO)}", ""]
    for i, mid in enumerate(picked, 1):
        m, t = load(MAIL / "messages" / f"{mid}.json", {}), load(MAIL / "triage" / f"{mid}.json", {})
        body = re.sub(r"\s+", " ", m.get("body", ""))[:600]
        out += [f"## {i} · {mid}", f"From: {m.get('from_name', '?')} · Subject: {m.get('subject', '?')} · "
                f"Triage said: {t.get('category', '?')}", f"Summary: {t.get('summary', '')}", f"> {body}"]
        if t.get("reply"):
            out += ["Draft:", *[f"> {line}" for line in t["reply"].splitlines()]]
        out += [f"- [ ] {c}" for c in CALLS.values()] + ["- [ ] triage right", "- [ ] triage wrong", ""]
    OUT.mkdir(parents=True, exist_ok=True)
    sheet.write_text("\n".join(out))
    print(sheet)
    return 0


def score(path):
    sheet = Path(path)
    original = load(MAIL / "decisions.json", {})
    rows, agree = [], 0
    for sec in re.split(r"^## \d+ · ", sheet.read_text(), flags=re.M)[1:]:
        mid = sec.split("\n", 1)[0].strip()
        ticked = re.findall(r"^- \[[xX]\] (.+)$", sec, re.M)
        call = next((c for c in ticked if c in CALLS.values()), None)
        then = CALLS.get(original.get(mid, {}).get("action"))
        right = "right" if "triage right" in ticked else "wrong" if "triage wrong" in ticked else None
        if call is None:
            print(f"{mid}: no call ticked")
            continue
        agree += call == then
        rows.append({"id": mid, "now": call, "then": then, "dwell_s": original.get(mid, {}).get("dwell_s"), "triage": right})
        if call != then:
            print(f"{mid}: now {call}, then {then} (dwell {original.get(mid, {}).get('dwell_s', '?')} s)")
    if not rows:
        return 1
    print(f"agreement: {agree} of {len(rows)}")
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "scores.jsonl").open("a") as f:
        f.write(json.dumps({"sheet": sheet.name, "scored": dt.datetime.now().isoformat(timespec="seconds"),
                            "agree": agree, "n": len(rows), "items": rows}) + "\n")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Rubber-stamp check on approvals of agent output.")
    ap.add_argument("cmd", choices=["report", "sample", "score"])
    ap.add_argument("sheet", nargs="?")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--n", type=int, default=5)
    a = ap.parse_args()
    if a.cmd == "score" and not a.sheet:
        ap.error("score needs the sheet path")
    sys.exit({"report": lambda: report(a.days), "sample": lambda: sample(a.n, a.days), "score": lambda: score(a.sheet)}[a.cmd]())
