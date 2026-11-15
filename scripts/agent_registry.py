#!/usr/bin/env python3
"""The agent registry: every .claude/agents/<name>.md is its registry entry (headless jobs and domain agents).

A job is not run before its entry says what it is trusted for and who answers for it
(technology/multi-agent-platform, principle 10: register before code). Required keys:
  model, budget_usd, write_scopes   what it runs on, what it may spend, where it may write
  lane       A gated process · B bounded loop (one agentic step, re-checked downstream) · C research
  level      L0 sandbox · L1 advisory (a human reads it; it never fires a gate) · L2 decision-supporting
             (technology/agent-architecture/references/harness-patterns.md, conformance levels)
  owner      the human who answers for its output
  stop_when  the condition under which the job is retired or paused (its kill criterion)
  evals      the checks that test its output (done-gates, probes), as a list
Lane C is never L2: research output does not support a decision until it is re-verified.

Domain agents and `extends:` (2026-11-15). A domain agent declares `categories: [<skill category>, ...]`
and is used both as a chat subagent (Agent tool) and headless. A job may declare `extends: <domain>`:
it then inherits the domain's model, effort and categories when it doesn't set them itself, and
run_agent.sh appends the domain's body to its system prompt. One level deep: a domain never extends.
Never inherited, always explicit per file: write_scopes, budget_usd, sandbox, code_mode,
untrusted_ingest and the registry keys. A category belongs to at most one domain.

  python3 scripts/agent_registry.py check                every entry complete; exit 1 otherwise (scripts/check.sh)
  python3 scripts/agent_registry.py budgets              cost per run from the ledger vs each job's budget_usd
  python3 scripts/agent_registry.py get <agent> <key>    one resolved key (extends applied); empty if unset
  python3 scripts/agent_registry.py body <agent>         the text below an agent file's frontmatter

budgets: runs on the job's pinned model only (a model change resets the history). Suggested cap =
p95 x 1.5, never below the largest past run + 25 % or $1, rounded up to $0.50; shown once a job
has >= 6 runs. It reports and changes nothing: a cap the principal set stays theirs.
Stdlib only.
"""
import json
import math
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
AGENTS = REPO / ".claude" / "agents"
LEDGER = REPO / "output" / ".runs" / "_ledger"
SKILLS = REPO / "resources" / "skills"
REQUIRED = ("model", "budget_usd", "write_scopes", "lane", "level", "owner", "stop_when", "evals")
INHERITED = ("model", "effort", "categories")
LANES, LEVELS = ("A", "B", "C"), ("L0", "L1", "L2")
NAME = re.compile(r"[a-z0-9][a-z0-9-]*")
MIN_RUNS = 6


def entry(path):
    """The frontmatter keys of one agent file, values as raw strings (comments stripped)."""
    text = path.read_text(errors="ignore")
    head = text[4:text.find("\n---\n", 4)] if text.startswith("---\n") else ""
    out = {}
    for line in head.split("\n"):
        m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if m:
            out[m.group(1)] = re.sub(r"\s+#.*$", "", m.group(2)).strip().strip("\"'")
    return out


def path_of(name):
    """The agent file for a name, or None (names come from hook input and env: no paths, no dots)."""
    f = AGENTS / f"{name}.md"
    return f if NAME.fullmatch(name or "") and f.is_file() else None


def listed(value):
    """`[a, b]` → ['a', 'b']."""
    return [v.strip().strip("\"'") for v in (value or "").strip("[] ").split(",") if v.strip()]


def resolved(name):
    """One agent's keys with `extends:` applied (the domain fills INHERITED keys the job leaves unset)."""
    f = path_of(name)
    if not f:
        return {}
    e = entry(f)
    parent = path_of(e.get("extends", ""))
    if parent:
        d = entry(parent)
        for k in INHERITED:
            if not e.get(k) and d.get(k):
                e[k] = d[k]
    return e


def body(name):
    f = path_of(name)
    text = f.read_text(errors="ignore") if f else ""
    end = text.find("\n---\n", 4) if text.startswith("---\n") else -1
    return text[end + 5:].strip() + "\n" if end >= 0 else ""


def problems(path):
    e, errs = resolved(path.stem), []
    own = entry(path)
    if "extends" in own:
        parent = path_of(own["extends"])
        if not parent:
            errs.append(f"extends '{own['extends']}': no such agent file")
        elif not entry(parent).get("categories"):
            errs.append(f"extends '{own['extends']}': not a domain agent (no categories)")
        elif "extends" in entry(parent):
            errs.append(f"extends '{own['extends']}': a domain agent cannot extend another")
        if own.get("categories"):
            errs.append("a job takes its categories from its domain; drop categories or extends")
    for c in listed(own.get("categories")):
        if c.startswith("_") or not (SKILLS / c).is_dir():
            errs.append(f"category '{c}' is not a folder in resources/skills/")
    for k in REQUIRED:
        if k not in e or (k != "write_scopes" and not e[k]):
            errs.append(f"missing {k}")
    if e.get("lane") and e["lane"] not in LANES:
        errs.append(f"lane must be one of {', '.join(LANES)}")
    if e.get("level") and e["level"] not in LEVELS:
        errs.append(f"level must be one of {', '.join(LEVELS)}")
    if e.get("lane") == "C" and e.get("level") == "L2":
        errs.append("a lane-C (research) job cannot be L2")
    if e.get("evals") and not re.fullmatch(r"\[.*\S.*\]", e["evals"]):
        errs.append("evals must be a non-empty list")
    return errs


def check():
    bad, owner = 0, {}
    for f in sorted(AGENTS.glob("*.md")):
        errs = problems(f)
        for c in listed(entry(f).get("categories")):
            if c in owner:
                errs.append(f"category '{c}' already belongs to {owner[c]}")
            owner.setdefault(c, f.stem)
        bad += bool(errs)
        print(f"{f.name}: " + ("OK" if not errs else "; ".join(errs)))
    return 1 if bad else 0


def budgets():
    print(f"{'job':22} {'runs':>4} {'p95':>6} {'max':>6} {'cap':>6} {'suggest':>8}")
    for f in sorted(AGENTS.glob("*.md")):
        e, job = resolved(f.stem), f.stem
        led = LEDGER / f"{job}.jsonl"
        rows = []
        if led.is_file():
            for line in led.read_text().splitlines():
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    continue
        cost = sorted(r["cost_usd"] for r in rows
                      if isinstance(r.get("cost_usd"), (int, float)) and r["cost_usd"] > 0 and e.get("model") in (r.get("models") or []))
        if len(cost) < MIN_RUNS:
            print(f"{job:22} {len(cost):>4} {'':>6} {'':>6} {e.get('budget_usd', '?'):>6} {'(< 6 runs)':>8}")
            continue
        p95 = cost[min(len(cost) - 1, math.floor(len(cost) * 0.95))]
        suggest = math.ceil(max(p95 * 1.5, cost[-1] * 1.25, 1.0) * 2) / 2
        print(f"{job:22} {len(cost):>4} {p95:>6.2f} {cost[-1]:>6.2f} {e.get('budget_usd', '?'):>6} {suggest:>8.2f}")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "check":
        sys.exit(check())
    if cmd == "budgets":
        sys.exit(budgets())
    if cmd == "get" and len(sys.argv) == 4:
        print(resolved(sys.argv[2]).get(sys.argv[3], ""))
        sys.exit(0)
    if cmd == "body" and len(sys.argv) == 3:
        sys.stdout.write(body(sys.argv[2]))
        sys.exit(0)
    sys.exit(__doc__)
