#!/usr/bin/env python3
"""Harness regression suite runner (G6): probes from ../evals/regression.json, k runs each, pass^k.

Each probe is one headless `claude -p` in the repo, so the real harness is under test: CLAUDE.md,
Charter, the SessionStart and UserPromptSubmit hooks, the write/egress/send gates. Tools are read-only
(or a single allowlisted helper), so a probe never writes to the vault or sends anything. Grading is
code over the run's JSON result and transcript, never a model:

  read_any        the session Read one of these paths (suffix match)
  read_or_names   {"read": [paths], "names": [strings]}: Read one of the paths, or the answer names one string
                  (the preselector puts skill rows in context, so a grounded answer may need no Read)
  tools_only      every tool call used one of these tools
  result_lacks    no regex (case-insensitive) matches the final answer
  result_has      every string appears in the final answer
  result_has_pack every listed employer-pack value (scripts/employer.py get) appears in the answer
  max_denials     permission denials <= N
  file_absent     this repo path does not exist afterwards

  python3 regression.py [--only P1,P4] [--k 3] [--model sonnet] [--dry-run]
  python3 regression.py --regrade output/regression/<stamp>.tsv   re-score finished runs from their
                  transcripts with the current graders (after a logged grader change; no reruns)
Writes output/regression/<YYYYMMDD-HHMMSS>.tsv (one row per run) and prints pass^k per probe.
Runs are sequential with a pause, and the suite stops early if the circuit breaker is open.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SUITE = HERE.parent / "evals" / "regression.json"
OUT = REPO / "output" / "regression"
TRANSCRIPTS = Path.home() / ".claude" / "projects" / str(REPO).replace("/", "-")
CIRCUIT = REPO / "output" / ".runs" / "_ledger" / "_circuit.json"
CLI_ENV = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")}


def tool_uses(session):
    t = TRANSCRIPTS / f"{session}.jsonl"
    uses = []
    if t.exists():
        for line in t.read_text(errors="ignore").splitlines():
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("type") == "assistant":
                uses += [c for c in e.get("message", {}).get("content") or []
                         if isinstance(c, dict) and c.get("type") == "tool_use"]
    return uses


def pack_value(key):
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "employer.py"), "get", key],
                       capture_output=True, text=True, cwd=REPO)
    return r.stdout.strip()


def grade(spec, result, uses, denials):
    fails = []
    reads = [u.get("input", {}).get("file_path", "") for u in uses if u.get("name") == "Read"]
    if "read_any" in spec and not any(r.endswith(p) for r in reads for p in spec["read_any"]):
        fails.append(f"read none of {spec['read_any']} (read: {[Path(r).name for r in reads][:5]})")
    if "read_or_names" in spec:
        ro = spec["read_or_names"]
        if not (any(r.endswith(p) for r in reads for p in ro["read"])
                or any(n.lower() in result.lower() for n in ro["names"])):
            fails.append(f"neither read {ro['read']} nor named {ro['names']}")
    if "tools_only" in spec:
        other = sorted({u.get("name") for u in uses} - set(spec["tools_only"]))
        if other:
            fails.append(f"used tools outside {spec['tools_only']}: {other}")
    for rx in spec.get("result_lacks", []):
        if re.search(rx, result, re.I):
            fails.append(f"answer matches /{rx}/")
    for s in spec.get("result_has", []):
        if s.lower() not in result.lower():
            fails.append(f"answer lacks {s!r}")
    for key in spec.get("result_has_pack", []):
        v = pack_value(key)
        if not v or v.lower() not in result.lower():
            fails.append(f"answer lacks the pack's {key}")
    if "max_denials" in spec and denials > spec["max_denials"]:
        fails.append(f"{denials} permission denial(s)")
    if "file_absent" in spec and (REPO / spec["file_absent"]).exists():
        fails.append(f"{spec['file_absent']} exists")
    return fails


def run_probe(p, model, dry):
    if "fixture" in p:
        f = REPO / p["fixture"]["path"]
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(p["fixture"]["text"])
    if "file_absent" in p["pass"]:
        (REPO / p["pass"]["file_absent"]).unlink(missing_ok=True)
    cmd = ["claude", "-p", p["prompt"], "--model", model, "--output-format", "json",
           "--max-turns", str(p.get("max_turns", 8)), "--allowedTools", *p["tools"]]
    if p.get("agent"):
        cmd[3:3] = ["--agent", p["agent"]]
    if dry:
        print("would run:", " ".join(cmd[:3]), "…", " ".join(cmd[4:]))
        return None
    started = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO, env=CLI_ENV, stdin=subprocess.DEVNULL, timeout=900)
    try:
        out = json.loads(r.stdout)
    except ValueError:
        out = {"result": r.stdout[-500:], "is_error": True}
    uses = tool_uses(out.get("session_id", ""))
    fails = grade(p["pass"], out.get("result") or "", uses, len(out.get("permission_denials") or []))
    if out.get("is_error"):
        fails.append(f"run error: {out.get('subtype') or out.get('terminal_reason') or r.returncode}")
    return {"ok": not fails, "fails": fails, "secs": round(time.time() - started), "session": out.get("session_id"),
            "cost": out.get("total_cost_usd"), "tools": len(uses)}


def regrade(tsv, suite):
    specs = {p["id"]: p for p in suite["probes"]}
    rows = [dict(zip(tsv.read_text().splitlines()[0].split("\t"), l.split("\t"))) for l in tsv.read_text().splitlines()[1:]]
    summary = {}
    for r in rows:
        p = specs[r["probe"]]
        t = TRANSCRIPTS / f"{r['session']}.jsonl"
        result, denials = "", 0
        for line in t.read_text(errors="ignore").splitlines() if t.exists() else []:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("type") == "assistant":
                texts = [c.get("text", "") for c in e.get("message", {}).get("content") or [] if isinstance(c, dict) and c.get("type") == "text"]
                if texts:
                    result = "\n".join(texts)
        fails = grade({k: v for k, v in p["pass"].items() if k not in ("file_absent", "max_denials")}, result, tool_uses(r["session"]), denials)
        if "file_absent" in p["pass"] and r["fails"] and p["pass"]["file_absent"] in r["fails"]:
            fails.append(f"{p['pass']['file_absent']} existed at run time")
        if "max_denials" in p["pass"] and "denial" in r["fails"]:
            fails.append("permission denial(s) at run time")
        summary.setdefault(r["probe"], []).append(not fails)
        print(f"{r['probe']:<22} run {r['run']}  {'PASS' if not fails else 'FAIL'}" + ("" if not fails else "  — " + "; ".join(fails)))
    k = suite["k"]
    total = sum(all(o) and len(o) == k for o in summary.values())
    print(f"regraded suite: {total}/{len(summary)} probes pass^{k} ({tsv.name})")
    return 0 if total == len(summary) else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only")
    ap.add_argument("--k", type=int)
    ap.add_argument("--model")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--regrade")
    a = ap.parse_args()
    suite = json.loads(SUITE.read_text())
    if a.regrade:
        return regrade(Path(a.regrade), suite)
    k, model = a.k or suite["k"], a.model or suite["model"]
    probes = [p for p in suite["probes"] if not a.only or p["id"].split("-")[0] in a.only.split(",") or p["id"] in a.only.split(",")]
    OUT.mkdir(parents=True, exist_ok=True)
    tsv = OUT / f"{time.strftime('%Y%m%d-%H%M%S')}.tsv"
    if not a.dry_run:
        tsv.write_text("probe\tguards\trun\tok\tsecs\tcost_usd\ttools\tsession\tfails\n")
    summary = {}
    for p in probes:
        for i in range(1, k + 1):
            try:
                if json.loads(CIRCUIT.read_text()).get("open_until_epoch", 0) > time.time():
                    print("circuit breaker open: stopping the suite (rerun later)")
                    return 75
            except (OSError, ValueError):
                pass
            res = run_probe(p, model, a.dry_run)
            if res is None:
                break
            summary.setdefault(p["id"], []).append(res["ok"])
            print(f"{p['id']:<22} run {i}/{k}  {'PASS' if res['ok'] else 'FAIL'}  {res['secs']}s"
                  + ("" if res["ok"] else "  — " + "; ".join(res["fails"])), flush=True)
            with tsv.open("a") as f:
                f.write(f"{p['id']}\t{p['guards']}\t{i}\t{int(res['ok'])}\t{res['secs']}\t{res['cost']}\t{res['tools']}\t"
                        f"{res['session']}\t{'; '.join(res['fails'])}\n")
            time.sleep(5)
    if a.dry_run:
        return 0
    print(f"\npass^{k} per probe (all {k} runs pass):")
    for pid, oks in summary.items():
        print(f"  {pid:<22} {'PASS' if all(oks) and len(oks) == k else 'FAIL'}  ({sum(oks)}/{len(oks)} runs)")
    total = sum(all(o) and len(o) == k for o in summary.values())
    print(f"suite: {total}/{len(summary)} probes pass^{k} · results {tsv.relative_to(REPO)}")
    return 0 if total == len(summary) else 1


if __name__ == "__main__":
    sys.exit(main())
