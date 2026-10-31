#!/usr/bin/env python3
"""Skill candidates: heavy sessions that no repo skill covered — the raw list for a skill proposal.

Hermes Agent writes a skill on its own after a complex task. Here the agent only *proposes*: this script finds
the sessions worth turning into a skill, the propose-from-sessions workflow drafts the proposal, and nothing
enters resources/skills/ without the principal's yes (Charter §7).

A session is a candidate when it made at least --min-calls tool calls and no repo skill covered it: its prompt
names no skill slug and none of its tool calls touched a file under resources/skills/ (a session that ran a skill
feeds self-evolution of that skill instead, not a new one).

  python3 skill_candidates.py [--days 7] [--min-calls 15]     → a Markdown table on stdout
Prompts carry client names: write the result only under output/ (git-ignored).
"""
import argparse
import json
import time
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
SESSIONS = Path.home() / ".claude" / "projects" / str(REPO).replace("/", "-")
SLUGS = {p.parent.name for p in (REPO / "resources" / "skills").glob("*/*/SKILL.md")}


def human(entry):
    """The person's own words in a user entry ("" for tool results and harness-injected text)."""
    c = entry.get("message", {}).get("content")
    items = [{"type": "text", "text": c}] if isinstance(c, str) else (c or [])
    if any(isinstance(i, dict) and i.get("type") == "tool_result" for i in items):
        return ""
    text = " ".join(i.get("text", "") for i in items if isinstance(i, dict) and i.get("type") == "text").strip()
    return "" if text.startswith("<") else text


def scan(path):
    calls, covered, prompt = 0, False, ""
    with open(path) as f:
        for line in f:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("type") == "user" and not prompt:
                prompt = human(e)
            elif e.get("type") == "assistant":
                for c in e.get("message", {}).get("content") or []:
                    if isinstance(c, dict) and c.get("type") == "tool_use":
                        calls += 1
                        covered = covered or "resources/skills/" in json.dumps(c.get("input"))
    covered = covered or "resources/skills/" in prompt or any(s in prompt for s in SLUGS)
    return calls, covered, prompt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--min-calls", type=int, default=15)
    a = ap.parse_args()
    since = time.time() - a.days * 86400
    rows = []
    for p in SESSIONS.glob("*.jsonl"):
        if p.stat().st_mtime < since:
            continue
        calls, covered, prompt = scan(p)
        if calls >= a.min_calls and not covered and prompt:
            rows.append((p.stat().st_mtime, calls, p.stem, prompt))
    print(f"# Skill candidates — last {a.days} days, ≥ {a.min_calls} tool calls, no repo skill used\n")
    if not rows:
        print("None.")
        return
    print("| date | tool calls | session | first prompt |\n|---|---|---|---|")
    for mtime, calls, sid, prompt in sorted(rows, reverse=True):
        print(f"| {datetime.fromtimestamp(mtime):%Y-%m-%d} | {calls} | `{sid}` | {' '.join(prompt.split())[:160].replace('|', '/')} |")


if __name__ == "__main__":
    main()
