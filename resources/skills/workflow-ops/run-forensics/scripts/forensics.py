#!/usr/bin/env python3
"""Run forensics: why did a headless agent run fail, and does the same failure keep coming back?

The run ledger (output/.runs/_ledger/<job>.jsonl, written by scripts/run_agent.sh) only says whether a run
exited 0. Almost every run does, while the transcript underneath is full of blocked commands, misrouted
skills and stale edits. This script reads each run's transcript, files every failure under one code of a
closed taxonomy (../schema/taxonomy.json), and tracks recurring codes as issues with a fix → verify cycle.

  ingest              classify every ledgered run not yet classified (idempotent; run_agent.sh calls it)
  report [--days N]   recurrence + fix verification → output/run-forensics/report-<date>.md, issues.json
  fixed CODE --note   start a fix's verification window (after the harness edit is made)
  pair CODE [--job J] a failing run next to the nearest clean run of the same job and model (fix step 1)
  status              JSON summary for the console (open/regressed issues)
  models              each job's current model against the regression suite (report runs it too): a model no
                      finished suite covers gets one started in the background, and output/.runs/_forensics/
                      model-alarm.json raises the console's model pill until a suite passes on it
  quality             measure past runs of the jobs quality.py lists (backfill), then print their quality per
                      model; a run below its skill's floor carries QUALITY_FLOOR (ingest does this for new runs);
                      also backfills every job's repeated-research measure (quality.efficiency)

Files: output/.runs/_forensics/runs.jsonl (one line per classified run), output/run-forensics/issues.json,
output/.runs/_forensics/hooks.jsonl (block/deny decisions written by the .claude/hooks scripts),
output/.runs/_forensics/judge.jsonl (output-quality verdicts written by judge.py run; a flagged run gets QUALITY_JUDGE).
Stdlib only, Python 3.9 (launchd runs /usr/bin/python3).
"""
import argparse
import collections
import datetime as dt
import glob
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

import quality

REPO = Path(__file__).resolve().parents[5]
LEDGER = REPO / "output" / ".runs" / "_ledger"
RUNS = REPO / "output" / ".runs" / "_forensics" / "runs.jsonl"
HOOKS = REPO / "output" / ".runs" / "_forensics" / "hooks.jsonl"
JUDGE = REPO / "output" / ".runs" / "_forensics" / "judge.jsonl"
OUT = REPO / "output" / "run-forensics"
ISSUES = OUT / "issues.json"
TAXONOMY = json.loads((Path(__file__).resolve().parents[1] / "schema" / "taxonomy.json").read_text())
TRANSCRIPTS = Path.home() / ".claude" / "projects"

RECUR_RUNS = 2        # a tracked code in >= 2 runs inside the window is recurring
VERIFY_RUNS = 5       # floor: a fix needs at least 5 clean post-fix runs
MAX_VERIFY_RUNS = 30  # above this a code is too rare to verify by recurrence; judge it from the traces
FALSE_VERIFY = 0.10   # accept at most a 10% chance that the clean runs were luck, not the fix
WINDOW_DAYS = 7
REGRESSION = REPO / "output" / "regression"
SUITE = Path(__file__).resolve().parents[1] / "evals" / "regression.json"
MODEL_ALARM = REPO / "output" / ".runs" / "_forensics" / "model-alarm.json"
MODEL_DAYS = 14       # a job counts for the model check while it has run in the last 14 days


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_jsonl(path):
    out = []
    try:
        for line in path.read_text(errors="replace").splitlines():
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    except OSError:
        pass
    return out


def normalize(text):
    """Sentry-style signature: strip ids, paths, numbers so the same failure groups together."""
    t = text.strip().split("\n")[0]
    t = re.sub(r"<tool_use_error>|</tool_use_error>", "", t)
    t = re.sub(r"[0-9a-f]{8}-[0-9a-f-]{27,}", "<id>", t)
    t = re.sub(r"(~|\.{0,2})?/[\w.@~+-]+(/[\w.@~+-]*)+", "<path>", t)
    t = re.sub(r"\d+", "N", t)
    return t[:120]


def step_code(tool, text):
    for r in TAXONOMY["step_rules"]:
        if re.fullmatch(r["tool"], tool) and re.search(r["pattern"], text):
            return r["code"]
    return "UNCLASSIFIED"


def run_codes(r):
    """The first (root) failure only: an API outage also loses the handoff, but the outage is the cause."""
    meta = r.get("terminal_reason") or ""
    sub = r.get("subtype") or ""
    if sub in ("error_max_turns", "error_max_budget_usd") or meta in ("max_turns", "budget_exhausted", "prompt_too_long"):
        return ["BUDGET"]
    if meta in ("hook_stopped", "stop_hook_prevented"):
        return ["GATE"]
    if r.get("auth_failed"):
        return ["AUTH_EXPIRED"]
    no_result = r.get("cost_usd") is None and r.get("num_turns") is None
    if no_result or r.get("exit_code") not in (0, None) or r.get("is_error") or meta == "api_error":
        return ["INFRA"]
    if r.get("handoff_present") is False:
        return ["NO_HANDOFF"]
    return []


def transcript(sid):
    hits = glob.glob(str(TRANSCRIPTS / "*" / f"{sid}.jsonl"))
    return Path(hits[0]) if hits else None


def hook_events():
    """Block/deny decisions the .claude/hooks scripts logged, by session: the harness side of the trace."""
    by = collections.defaultdict(list)
    for e in read_jsonl(HOOKS):
        if e.get("session_id"):
            by[e["session_id"]].append(e)
    return by


def hook_summary(events, tools):
    """What the hooks decided in one run, and what the agent did after its first Stop-gate block:
    'worked' (any call besides editing a control spine), 'tick-only' (only RESPONSE.md edits), 'none' (stopped again)."""
    blocks = sorted(e["ts"] for e in events if e.get("hook") == "control-spine-gate" and e.get("decision") == "block")
    out = {"gate_blocks": len(blocks),
           "released_open": sum(1 for e in events if e.get("decision") == "release" and e.get("runs")),
           "boundary_denials": sum(1 for e in events if e.get("hook") == "write-boundary")}
    if blocks and tools is not None:   # None = transcript gone (a reclassification): unknown, not "none"
        later = [(name, inp) for ts, name, inp in tools if ts > blocks[0]]
        spine = all(name in ("Edit", "MultiEdit", "Write") and str(inp.get("file_path", "")).endswith("RESPONSE.md")
                    for name, inp in later)
        out["after_block"] = "none" if not later else "tick-only" if spine else "worked"
    return out


def classify(r, hooks=None):
    steps, sigs = collections.Counter(), collections.Counter()
    path = transcript(r["session_id"]) if r.get("session_id") else None
    names, tools = {}, []
    for e in read_jsonl(path) if path else []:
        content = (e.get("message") or {}).get("content")
        for b in content if isinstance(content, list) else []:
            if b.get("type") == "tool_use":
                names[b.get("id")] = b.get("name", "?")
                tools.append((e.get("timestamp") or "", b.get("name", "?"), b.get("input") or {}))
            elif b.get("type") == "tool_result" and b.get("is_error"):
                c = b.get("content")
                text = c if isinstance(c, str) else json.dumps(c)
                tool = names.get(b.get("tool_use_id"), "?")
                code = step_code(tool, text)
                steps[code] += 1
                sigs[f"{code} · {tool} · {normalize(text)}"] += 1
    run = run_codes(r)
    # A clean run can still skip work its skill requires; a failed run is judged by its root failure instead.
    try:
        q = quality.measure(r.get("job"), path) if path and not run else None
    except Exception as e:   # a parser bug must never stop ingest, which runs after every job
        q = {"metrics": {"error": f"{type(e).__name__}: {e}"[:200]}, "below": []}
    try:
        eff = quality.efficiency(quality.calls(path)) if path else None
    except Exception:   # same rule: never stop ingest
        eff = None
    for miss in (q or {}).get("below", []):
        steps["QUALITY_FLOOR"] += 1
        sigs[f"QUALITY_FLOOR · {r.get('job')} · {normalize(miss)}"] += 1
    tracked = {x["code"] for x in TAXONOMY["step_rules"] if x["track"]} | {"UNCLASSIFIED"}
    outcome = "failed" if run else "degraded" if any(c in tracked for c in steps) else "clean"
    out = {"key": r.get("session_id") or f'{r.get("job")}@{r.get("ts")}', "ts": r.get("ts"), "job": r.get("job"),
           "session_id": r.get("session_id"), "transcript": bool(path), "outcome": outcome, "run_codes": run,
           "step_codes": dict(steps), "signatures": dict(sigs.most_common(12)), "cost_usd": r.get("cost_usd")}
    if q:
        out["quality"] = q["metrics"]
    if eff:
        out["efficiency"] = eff
    events = (hooks or {}).get(r.get("session_id"), [])
    if events:   # joined now: the transcript needed for after_block expires, the classification doesn't
        out["hooks"] = hook_summary(events, tools if path else None)
    return out


def ingest(_args):
    seen = {x["key"] for x in read_jsonl(RUNS)}
    hooks = hook_events()
    RUNS.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with RUNS.open("a") as f:
        for p in sorted(LEDGER.glob("*.jsonl")):
            for r in read_jsonl(p):
                key = r.get("session_id") or f'{r.get("job")}@{r.get("ts")}'
                if key in seen:
                    continue
                seen.add(key)
                f.write(json.dumps(classify(r, hooks)) + "\n")
                n += 1
    print(f"forensics: classified {n} new run(s)")


# ---------- recurrence, fixes, verification ----------

def load_issues():
    try:
        return json.loads(ISSUES.read_text())
    except (OSError, ValueError):
        return {}


def all_codes(run):
    return list(run["run_codes"]) + [c for c in run["step_codes"]]


def is_tracked(code):
    for x in TAXONOMY["step_rules"]:
        if x["code"] == code:
            return x["track"]
    return True   # run-level codes and UNCLASSIFIED


def fix_hint(code):
    for x in TAXONOMY["run_rules"] + TAXONOMY["step_rules"]:
        if x["code"] == code:
            return x["fix"]
    return "No code fits these signatures: read the examples, then add a rule or a new code to schema/taxonomy.json."


def owner_of(code):
    """The harness behavior a code belongs to and the files that implement it (references/handbook.md)."""
    for x in TAXONOMY["run_rules"] + TAXONOMY["step_rules"]:
        if x["code"] == code and x.get("behavior"):
            return f"{x['behavior']} → " + ", ".join(f"`{s}`" for s in x.get("sites", []))
    return None


def needed_runs(share):
    """Clean post-fix runs before a fix counts as verified: the smallest n with (1 - share)^n <= FALSE_VERIFY.
    A fix that did nothing still looks clean for n runs with probability (1 - share)^n, so a code that hit
    6% of runs needs 38 clean runs, not 5 (assumes independent runs at the pre-fix rate)."""
    if share >= 1:
        return VERIFY_RUNS
    if share <= 0:
        return MAX_VERIFY_RUNS + 1
    return max(VERIFY_RUNS, math.ceil(math.log(FALSE_VERIFY) / math.log(1 - share)))


def main_model(models):
    """The model a run was on. Haiku sub-calls ride along with most runs and are not the configuration."""
    main = sorted(m for m in models or [] if "haiku" not in m)
    return main[0] if main else (sorted(models)[0] if models else None)


def load_runs():
    """Classified runs, deduped (two jobs ending together may both ingest), with model and git_sha joined from
    the ledger: verification keys on configuration, and old runs.jsonl lines predate those fields."""
    ledger = {}
    for p in LEDGER.glob("*.jsonl"):
        for r in read_jsonl(p):
            ledger[r.get("session_id") or f'{r.get("job")}@{r.get("ts")}'] = r
    runs = list({r["key"]: r for r in read_jsonl(RUNS)}.values())
    # The judge (judge.py run) grades a run the morning after it was ingested, so its verdict is joined here,
    # not written into runs.jsonl. A flagged run carries QUALITY_JUDGE like any step code.
    judged = {j["key"]: j for j in read_jsonl(JUDGE)}
    for r in runs:
        line = ledger.get(r["key"], {})
        r["model"], r["git_sha"] = main_model(line.get("models")), line.get("git_sha")
        j = judged.get(r["key"])
        if j:
            r["judge"] = j
        if j and j.get("flag"):
            r["step_codes"]["QUALITY_JUDGE"] = j["fails"]
            for c, n in j["criteria"].items():
                r["signatures"][f"QUALITY_JUDGE · {r['job']} · {c}"] = n
            if r["outcome"] == "clean":
                r["outcome"] = "degraded"
    return runs


def evaluate(runs, issues, days):
    """Advance every issue's state from the classified runs. Returns the issues dict (mutated)."""
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    window = [r for r in runs if (r["ts"] or "") >= since]
    by_code = collections.defaultdict(list)
    for r in window:
        for c in set(all_codes(r)):
            by_code[c].append(r)

    for code, hit in by_code.items():
        if not is_tracked(code) or len(hit) < RECUR_RUNS:
            continue
        issues.setdefault(code, {"code": code, "state": "open", "opened": now(), "history": []})

    for code, i in issues.items():
        hit = by_code.get(code, [])
        sigs = collections.Counter()
        for r in hit:
            for s, n in r["signatures"].items():
                if s.startswith(code + " "):
                    sigs[s] += n
        i.update({"window_days": days, "runs": len(hit), "jobs": sorted({r["job"] for r in hit}),
                  "occurrences": sum(r["step_codes"].get(code, 0) or (code in r["run_codes"]) for r in hit),
                  "examples": [s for s, _ in sigs.most_common(3)],
                  "sessions": [r["session_id"] for r in hit if r["session_id"]][-3:], "fix_hint": fix_hint(code)})
        # A fixed issue is judged on post-fix runs only, every report: the 7-day window still holds pre-fix runs,
        # so counting it would flag every verified fix as regressed the day after.
        if i["state"] in ("fixing", "regressed", "verified") and i.get("fix"):
            f = i["fix"]
            jobs, at = set(f["jobs"]), f["ts"]
            prior = [r for r in runs if (r["ts"] or "") <= at and r["job"] in jobs]
            if "share_before" not in f:   # frozen at the first evaluation after `fixed`
                last = prior[-50:]
                f["share_before"] = round(sum(code in all_codes(r) for r in last) / len(last), 2) if last else 1.0
            if "models" not in f:         # frozen too: the configuration the fix was made for
                f["models"] = {j: next((r["model"] for r in reversed(prior) if r["job"] == j and r["model"]), None)
                               for j in sorted(jobs)}
            # A fix is verified per configuration (RiseHarness: harness changes are model-specific). Each job is
            # judged only on post-fix runs on its current model, so a model change restarts its count. Runs with
            # no model crashed before any result; they count, or an INFRA fix could never regress.
            current = {j: next((r["model"] for r in reversed(runs) if r["job"] == j and r["model"]), None) for j in jobs}
            after = [r for r in runs if (r["ts"] or "") > at and r["job"] in jobs and r["model"] in (None, current[r["job"]])]
            bad = [r for r in after if code in all_codes(r)]
            f.update({"runs_after": len(after), "bad_after": len(bad), "needs": needed_runs(f["share_before"]),
                      "model_changed": {j: f"{f['models'][j]} → {current[j]}" for j in sorted(jobs)
                                        if f["models"].get(j) and current[j] and current[j] != f["models"][j]}})
            # Did not hold = still hitting at least half as many runs as before (a slip on a 10-job fix is not a regression).
            # Verified = `needs` clean runs and no hit. Anything else is fixing: slips below the bar, too few runs
            # yet (a model change included), or a code too rare to verify by recurrence at all.
            if len(bad) >= RECUR_RUNS and len(bad) / len(after) >= f["share_before"] / 2:
                new = "regressed"
            elif not bad and f["needs"] <= MAX_VERIFY_RUNS and len(after) >= f["needs"]:
                new = "verified"
            else:
                new = "fixing"
            if new != i["state"]:
                i["state"] = new
                i["history"].append({"ts": now(), "event": new,
                                     "detail": f"{len(bad)}/{len(after)} runs after the fix, needs {f['needs']} clean"})
        elif i["state"] == "open" and not hit:
            i["state"] = "dormant"
            i["history"].append({"ts": now(), "event": "dormant", "detail": f"no occurrence in {days} days"})
        elif i["state"] == "dormant" and len(hit) >= RECUR_RUNS:
            i["state"] = "open"
            i["history"].append({"ts": now(), "event": "reopened", "detail": f"{len(hit)} runs"})
    return issues


def job_health(runs, days=14):
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = collections.defaultdict(collections.Counter)
    for r in runs:
        if (r["ts"] or "") >= since:
            out[r["job"]][r["outcome"]] += 1
    return out


def harness_decisions(runs, days=14):
    """Report section from the hook log: how often the harness blocked a run, and what the agent did next."""
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    per = collections.defaultdict(collections.Counter)
    for r in runs:
        h = r.get("hooks")
        if h and (r["ts"] or "") >= since:
            c = per[r["job"]]
            c["blocks"] += h["gate_blocks"]
            c[h.get("after_block", "-")] += 1
            c["released_open"] += h["released_open"]
            c["denials"] += h["boundary_denials"]
    ledgered = {r["session_id"] for r in runs if r.get("session_id")}
    other = sum(len(v) for s, v in hook_events().items() if s not in ledgered)
    L = [f"\n## Harness decisions ({days} days, hook log)\n"]
    if not per:
        L.append(f"_No block or deny logged in headless runs yet (log: `{HOOKS.relative_to(REPO)}`)._")
    else:
        L += ["| Job | Stop-gate blocks | After block: worked · tick-only · stopped | Released with boxes open | Write-boundary denials |",
              "|---|---|---|---|---|"]
        for job, c in sorted(per.items()):
            L.append(f"| {job} | {c['blocks']} | {c['worked']} · {c['tick-only']} · {c['none']} | {c['released_open']} | {c['denials']} |")
    L.append(f"_{other} decision(s) in sessions with no ledgered run (interactive or console)._")
    return L


def timeline(path):
    """[tool, short argument, error text or None] for every tool call in a transcript, in order."""
    calls, at = [], {}
    for e in read_jsonl(path):
        content = (e.get("message") or {}).get("content")
        for b in content if isinstance(content, list) else []:
            if b.get("type") == "tool_use":
                inp = b.get("input") or {}
                arg = next((str(inp[k]) for k in ("command", "file_path", "path", "pattern", "skill", "url", "query") if inp.get(k)), "")
                at[b.get("id")] = len(calls)
                calls.append([b.get("name", "?"), " ".join(arg.split())[:90], None])
            elif b.get("type") == "tool_result" and b.get("is_error") and b.get("tool_use_id") in at:
                c = b.get("content")
                calls[at[b["tool_use_id"]]][2] = c if isinstance(c, str) else json.dumps(c)
    return calls


def pair(args):
    """Fix step 1 (RiseHarness §3.3): a failing run is read next to a success of the same job and configuration.
    The latest run with CODE whose transcript survives, against the run of the same job and model without CODE
    that is closest (same git_sha first, a clean run first, then nearest in time)."""
    runs = load_runs()
    alive = lambda r: r.get("session_id") and transcript(r["session_id"])
    hits = [r for r in runs if args.code in all_codes(r) and (not args.job or r["job"] == args.job) and alive(r)]
    if not hits:
        sys.exit(f"no run with {args.code}{' on ' + args.job if args.job else ''} still has a transcript")
    bad = max(hits, key=lambda r: r["ts"] or "")
    epoch = lambda r: dt.datetime.strptime(r["ts"], "%Y-%m-%dT%H:%M:%SZ").timestamp()
    refs = sorted((r for r in runs if r["job"] == bad["job"] and r["model"] == bad["model"]
                   and args.code not in all_codes(r) and r["ts"] and alive(r)),
                  key=lambda r: (r["git_sha"] != bad["git_sha"], r["outcome"] != "clean", abs(epoch(r) - epoch(bad))))
    ref = refs[0] if refs else None

    def head(label, r):
        print(f"{label:9} {r['ts']} · {r['job']} · {r['model']} · {r['git_sha']} · {r['outcome']} "
              f"{','.join(all_codes(r)) or '-'}\n          {transcript(r['session_id'])}")

    head("FAILING", bad)
    if ref:
        head("REFERENCE", ref)
    else:
        print(f"REFERENCE none: no run of {bad['job']} on {bad['model']} without {args.code} has a transcript left. "
              f"Read 2-3 failing runs instead (issues.json → sessions).")
    tb = timeline(transcript(bad["session_id"]))
    tr = timeline(transcript(ref["session_id"])) if ref else []
    first = next((n for n, (tool, _, err) in enumerate(tb) if err and step_code(tool, err) == args.code), max(len(tb) - 8, 0))
    split = next((n for n, (a, b) in enumerate(zip(tb, tr)) if a[0] != b[0]), None)
    if ref:
        print(f"\nTool sequences diverge at call {split}." if split is not None else "\nSame tool sequence up to the shorter run.")
    print(f"First {args.code} in the failing run: call {first}.")
    lo, hi = max(first - 6, 0), first + 3
    for label, calls in (("failing", tb), ("reference", tr)):
        if label == "reference" and not ref:
            continue
        print(f"\n-- {label}, calls {lo}-{min(hi, len(calls)) - 1} of {len(calls)} --")
        for n in range(lo, min(hi, len(calls))):
            tool, arg, err = calls[n]
            mark = f"   ✗ {step_code(tool, err)}: {normalize(err)}" if err else ""
            print(f"{n:>4}  {tool:<9} {arg}{mark}")


def addendum_name(model):
    """The addendum file run_agent.sh appends for this model's family, as regression.py records it."""
    fam = next((f for f in ("opus", "sonnet", "haiku", "fable") if f in (model or "")), None)
    return f"{fam}.md" if fam and (REPO / "resources" / "models" / f"{fam}.md").exists() else "none"


def suite_verdicts():
    """(model, addendum) -> pass | fail, from finished regression TSVs that record their model; newest wins.
    A TSV that lacks a probe or a run (--only, interrupted, still running) decides nothing."""
    suite = json.loads(SUITE.read_text())
    ids, k, out = {p["id"] for p in suite["probes"]}, suite["k"], {}
    for tsv in sorted(REGRESSION.glob("*.tsv")):
        lines = tsv.read_text(errors="replace").splitlines()
        head = lines[0].split("\t") if lines else []
        if "model" not in head:
            continue
        rows = [dict(zip(head, l.split("\t"))) for l in lines[1:]]
        runs = collections.defaultdict(list)
        for r in rows:
            runs[r.get("probe")].append(r.get("ok") == "1")
        if not rows or set(runs) != ids or any(len(v) < k for v in runs.values()):
            continue
        key = (rows[0]["model"], rows[0].get("addendum", "none"))
        out[key] = ("pass" if all(all(v) for v in runs.values()) else "fail", str(tsv.relative_to(REPO)))
    return out


def agent_field(job, key):
    f = REPO / ".claude" / "agents" / f"{job}.md"
    m = re.search(rf"^{key}:\s*(\S+)", f.read_text(), re.M) if f.exists() else None
    return m.group(1) if m else None


def check_models():
    """The model-swap test, run when it is due rather than when someone remembers (SKILL.md, Regression suite).
    Returns report lines; at most one automatic suite per model and addendum, ever: a failed one waits for you."""
    cutoff = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=MODEL_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    current = collections.defaultdict(list)
    for p in sorted(LEDGER.glob("*.jsonl")):
        # Harness runs only (run_agent.sh stamps git_sha); bare `claude -p` calls outside the harness don't count.
        rows = [r for r in read_jsonl(p) if r.get("models") and r.get("git_sha") and r.get("ts", "") >= cutoff]
        if rows:
            # A pinned model is what the next run uses; the last run's model covers jobs without a pin.
            pin = agent_field(p.stem, "model")
            current[pin if pin and pin.startswith("claude-") else main_model(rows[-1]["models"])].append(p.stem)
    verdicts, alarm = suite_verdicts(), {}
    for model, jobs in sorted(current.items()):
        add = addendum_name(model)
        verdict, tsv = verdicts.get((model, add), (None, None))
        if verdict == "pass":
            continue
        running = subprocess.run(["pgrep", "-f", f"regression.py --model {re.escape(model)}( |$)"],
                                 capture_output=True).returncode == 0
        state = "failed" if verdict == "fail" else "running" if running else "started"
        if state == "started":
            effort = next((e for e in (agent_field(j, "effort") for j in jobs) if e), None)
            env = dict(os.environ, PATH=f"{Path.home()}/.local/bin:/opt/homebrew/bin:/usr/local/bin:" + os.environ.get("PATH", ""))
            REGRESSION.mkdir(parents=True, exist_ok=True)
            log = open(REGRESSION / f"auto-{model}.log", "a")
            subprocess.Popen([sys.executable, str(Path(__file__).with_name("regression.py")), "--model", model]
                             + (["--effort", effort] if effort else []),
                             cwd=REPO, env=env, stdout=log, stderr=log, stdin=subprocess.DEVNULL, start_new_session=True)
        alarm[model] = {"jobs": jobs, "addendum": add, "suite": state, "tsv": tsv}
    if alarm:
        old = json.loads(MODEL_ALARM.read_text()) if MODEL_ALARM.exists() else {}
        MODEL_ALARM.parent.mkdir(parents=True, exist_ok=True)
        MODEL_ALARM.write_text(json.dumps({"since": old.get("since") or now(), "models": alarm}, indent=2))
    elif MODEL_ALARM.exists():
        MODEL_ALARM.unlink()
    L = ["\n## Models (regression suite per job model)\n"]
    for model, jobs in sorted(current.items()):
        a = alarm.get(model)
        L.append(f"- {model} ({addendum_name(model)}): {'suite ' + a['suite'] + (' · ' + a['tsv'] if a['tsv'] else '') if a else 'suite passed'}"
                 f" · jobs: {', '.join(jobs)}")
    return L


def models(_args):
    print("\n".join(check_models()).strip())


def quality_table(runs):
    """Each measured job's quality per model, all runs: a model change shows up as a step in these medians.
    Volume (items, domains) is context, not a floor: a quiet day may be short."""
    rows = collections.defaultdict(list)
    for r in runs:
        if r.get("quality") and "error" not in r["quality"]:
            rows[(r["job"], r["model"] or "none")].append(r)
    L = ["\n## Quality (per job and model, all measured runs)\n"]
    if not rows:
        return L + ["_No measured runs yet (`forensics.py quality` backfills them)._"]
    L += ["| Job | Model | Runs | Below a floor | Median per run |", "|---|---|---|---|---|"]
    for (job, model), rs in sorted(rows.items(), key=lambda kv: (kv[0][0], min(r["ts"] or "" for r in kv[1]))):
        below = sum("QUALITY_FLOOR" in r["step_codes"] for r in rs)
        keys = list(dict.fromkeys(k for r in rs for k in r["quality"]))
        med = lambda k: sorted(r["quality"].get(k, 0) for r in rs)[len(rs) // 2]
        L.append(f"| {job} | {model} | {len(rs)} | {below} ({below / len(rs):.0%}) | " + " · ".join(f"{k} {med(k)}" for k in keys) + " |")
    return L


def efficiency_table(runs):
    """Repeated research per job and model (quality.efficiency): report-only, a step between models is the signal."""
    rows = collections.defaultdict(list)
    for r in runs:
        e = r.get("efficiency")
        if e and e["research"]:
            rows[(r["job"], r["model"] or "none")].append(e["repeated"] / e["research"])
    L = ["\n## Repeated research (per job and model, all measured runs)\n"]
    if not rows:
        return L + ["_No measured runs yet (`forensics.py quality` backfills them)._"]
    L += ["| Job | Model | Runs | Median repeated | p90 | Max |", "|---|---|---|---|---|---|"]
    for (job, model), s in sorted(rows.items()):
        s = sorted(s)
        L.append(f"| {job} | {model} | {len(s)} | {s[len(s) // 2]:.0%} | {s[int(0.9 * len(s))]:.0%} | {s[-1]:.0%} |")
    return L


def judge_table(runs):
    """The output-quality judge's verdicts per job and model (judge.py): items failed, corrected for the judge's
    measured error rates, and runs flagged QUALITY_JUDGE."""
    rows = collections.defaultdict(list)
    for r in runs:
        if r.get("judge"):
            rows[(r["job"], r["model"] or "none")].append(r["judge"])
    if not rows:
        return []
    L = ["\n## Judged output quality (judge.py, calibrated against the principal's labels)\n",
         "| Job | Model | Runs | Items | Median failed (corrected) | Flagged |", "|---|---|---|---|---|---|"]
    for (job, model), js in sorted(rows.items()):
        c = sorted(j["fail_share"] for j in js)
        L.append(f"| {job} | {model} | {len(js)} | {sum(j['items'] for j in js)} | {c[len(c) // 2]:.0%} | "
                 f"{sum(1 for j in js if j['flag'])} |")
    return L


def quality_cmd(_args):
    """Backfill: re-classify runs that predate quality.py (measured jobs) or efficiency (every job), while their
    transcripts last."""
    ledger = {}
    for p in LEDGER.glob("*.jsonl"):
        for r in read_jsonl(p):
            ledger[r.get("session_id") or f'{r.get("job")}@{r.get("ts")}'] = r
    hooks, lines, n = hook_events(), read_jsonl(RUNS), 0
    for i, x in enumerate(lines):
        path = x["key"] in ledger and x.get("session_id") and transcript(x["session_id"])
        if path and x.get("job") in quality.JOBS and "quality" not in x:
            lines[i] = classify(ledger[x["key"]], hooks)
            n += 1
        elif path and "efficiency" not in x:   # measure only: re-classifying would apply today's rules to old runs
            x["efficiency"] = quality.efficiency(quality.calls(path))
            n += 1
    if n:
        tmp = RUNS.with_suffix(".tmp")
        tmp.write_text("".join(json.dumps(x) + "\n" for x in lines))
        os.replace(tmp, RUNS)
    print(f"forensics: measured {n} earlier run(s)")
    print("\n".join(quality_table(load_runs())).strip())


def report(args):
    ingest(args)
    runs = load_runs()
    issues = evaluate(runs, load_issues(), args.days)
    OUT.mkdir(parents=True, exist_ok=True)
    ISSUES.write_text(json.dumps(issues, indent=2))

    order = {"regressed": 0, "open": 1, "fixing": 2, "dormant": 3, "verified": 4}
    live = sorted(issues.values(), key=lambda i: (order.get(i["state"], 9), -i.get("runs", 0)))
    today = dt.date.today().isoformat()
    L = [f"---\ntype: report\ndate: {today}\ntags: [run-forensics, harness]\n---\n",
         f"# Run forensics — {today}\n",
         f"Window: last {args.days} days · {len(runs)} runs classified in total · recurring = a tracked code in ≥ {RECUR_RUNS} runs.\n",
         "## Job health (14 days)\n", "| Job | Runs | Clean | Degraded | Failed | Not clean |", "|---|---|---|---|---|---|"]
    for job, c in sorted(job_health(runs).items()):
        tot = sum(c.values())
        rate = (c["degraded"] + c["failed"]) / tot if tot else 0
        flag = " ⚠ over budget (> 10%)" if c["failed"] / tot > 0.1 else ""
        L.append(f"| {job} | {tot} | {c['clean']} | {c['degraded']} | {c['failed']} | {rate:.0%}{flag} |")
    L.extend(harness_decisions(runs))
    L.extend(check_models())
    L.extend(quality_table(runs))
    L.extend(judge_table(runs))
    L.extend(efficiency_table(runs))
    L.append("\n## Issues\n")
    for i in live:
        L.append(f"### {i['code']} — {i['state']}")
        L.append(f"- {i.get('runs', 0)} runs, {i.get('occurrences', 0)} occurrences, jobs: {', '.join(i.get('jobs', [])) or '—'}")
        for e in i.get("examples", []):
            L.append(f"  - `{e}`")
        if i.get("fix"):
            f = i["fix"]
            L.append(f"- Fix {f['ts'][:10]}: {f['note']} · after the fix: {f.get('bad_after', 0)}/{f.get('runs_after', 0)} runs still hit it")
            if f.get("needs", 0) > MAX_VERIFY_RUNS:
                L.append(f"- Verification: too rare to verify by recurrence (hit {f['share_before']:.0%} of runs before; "
                         f"{f['needs']} clean runs needed). Judge it by reading post-fix traces.")
            elif i["state"] != "verified" and "needs" in f:
                L.append(f"- Verification: needs {f['needs']} clean runs on the current model "
                         f"(hit {f['share_before']:.0%} of runs before), has {f.get('runs_after', 0)}")
            for job, change in f.get("model_changed", {}).items():
                L.append(f"- Model changed on {job}: {change}. Re-verifying on the new model; runs on the old one no longer count.")
        owner = owner_of(i["code"])
        if owner:
            L.append(f"- Owner: {owner}")
        L.append(f"- Fix hint: {i['fix_hint']}\n")
    unc = sum(r["step_codes"].get("UNCLASSIFIED", 0) for r in runs)
    allsteps = sum(sum(r["step_codes"].values()) for r in runs) or 1
    L.append(f"_Unclassified share: {unc}/{allsteps} step failures ({unc / allsteps:.1%}). Above 5% → open-code the examples and extend the taxonomy._")
    path = OUT / f"report-{today.replace('-', '')}.md"
    path.write_text("\n".join(L) + "\n")
    print(f"forensics: {sum(1 for i in live if i['state'] in ('open', 'regressed'))} open/regressed issue(s) → {path.relative_to(REPO)}")


def fixed(args):
    issues = load_issues()
    i = issues.get(args.code)
    if not i:
        sys.exit(f"no issue {args.code}; known: {', '.join(issues) or 'none'}")
    jobs = args.jobs.split(",") if args.jobs else i.get("jobs", [])
    i["fix"] = {"ts": now(), "note": args.note, "jobs": jobs, "runs_after": 0, "bad_after": 0}
    i["state"] = "fixing"
    i["history"].append({"ts": i["fix"]["ts"], "event": "fixed", "detail": args.note})
    ISSUES.write_text(json.dumps(issues, indent=2))
    print(f"{args.code}: verifying over the next {VERIFY_RUNS} runs of {', '.join(jobs)}")


def status(_args):
    issues = load_issues()
    hot = [i for i in issues.values() if i["state"] in ("open", "regressed")]
    print(json.dumps({"open": len([i for i in hot if i["state"] == "open"]),
                      "regressed": [i["code"] for i in hot if i["state"] == "regressed"],
                      "top": max(hot, key=lambda i: i.get("runs", 0))["code"] if hot else None}))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ingest").set_defaults(fn=ingest)
    p = sub.add_parser("report")
    p.add_argument("--days", type=int, default=WINDOW_DAYS)
    p.set_defaults(fn=report)
    p = sub.add_parser("fixed")
    p.add_argument("code")
    p.add_argument("--note", required=True)
    p.add_argument("--jobs", help="comma list; default = the jobs that had it")
    p.set_defaults(fn=fixed)
    p = sub.add_parser("pair")
    p.add_argument("code")
    p.add_argument("--job")
    p.set_defaults(fn=pair)
    sub.add_parser("status").set_defaults(fn=status)
    sub.add_parser("models").set_defaults(fn=models)
    sub.add_parser("quality").set_defaults(fn=quality_cmd)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
