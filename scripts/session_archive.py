#!/usr/bin/env python3
"""Session archive: every Claude Code transcript kept past the cleanup, redacted, hash-chained and searchable.

Claude Code deletes transcripts after `cleanupPeriodDays` (90 here since 2026-11-08; the default is 30). They are
the only record of why a change was made and what a session actually did, and the raw input for learning from
sessions (run-forensics `scripts/sessions.py`). Raw traces, not summaries: a harness optimizer fed summaries
lost most of the signal (Meta-Harness, arXiv:2603.28052: 34.9 vs 50.0 median accuracy).

`sync` copies each finished transcript (main session and subagents) to output/.sessions/<project>/, gzipped, with
high-confidence secrets replaced by [REDACTED:<kind>], and appends one line per copy to output/.sessions/index.jsonl.
Index lines are hash-chained (each carries the hash of the line before it), and each stores the sha256 of the
original transcript and of the stored copy, so `verify` can show later that no archived session and no index
line was changed or removed. A session that grows after it was archived (resumed later) gets a new version;
nothing is overwritten.

  sync [--idle-min N] [--dry-run]   archive transcripts idle >= N minutes (default 120) that are new or changed
  verify                            recompute the chain and every stored file's hash; exit 1 on any mismatch
  find [--since D] [--until D] [--text T] [--file F] [--origin O] [--job J] [--grep RX] [--limit N]
                                    latest version of each session matching all filters (D = YYYY-MM-DD)
  show SESSION [--all] [--grep RX]  readable timeline of one archived session (an id prefix is enough)

Per session the index records origin (human: a person typed in it · job: a ledgered headless run · automated:
anything else, e.g. regression probes), job, title (first human prompt), started/ended, git sha, the active
employer pack, taint (outside text it took in, scripts/ingest_lint.py's rule), files written and skills used.
The archive holds client content: it is git-ignored, owner-only (0700/0600), never synced, and listed in
`employer.py exit-report`. Pattern redaction misses some secrets (CSA, 2026-10-28), so it is a floor, not a
guarantee. Stdlib only, Python 3.9 (launchd runs /usr/bin/python3).
"""
import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ingest_lint  # noqa: E402  (events(): taint and file writes, same rule as the vault provenance hook)

REPO = Path(__file__).resolve().parent.parent
PROJECTS = Path.home() / ".claude" / "projects"
ARCHIVE = Path(os.environ.get("CBRAIN_SESSIONS_ARCHIVE") or REPO / "output" / ".sessions")   # env: tests only
INDEX = ARCHIVE / "index.jsonl"
LEDGER = REPO / "output" / ".runs" / "_ledger"
GENESIS = "0" * 64

SECRETS = [
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.{0,8000}?-----END [A-Z ]*PRIVATE KEY-----", re.S)),
    ("anthropic", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("openai", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}")),
    ("github", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})")),
    ("slack", re.compile(r"\bxox[abprse]-[A-Za-z0-9-]{10,}")),
    ("aws", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("google-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}")),
    # not inside base64 (attachments): a refresh token is never flanked by + or /, a base64 run usually is
    ("google-oauth", re.compile(r"(?<![A-Za-z0-9+/])(?:ya29\.[0-9A-Za-z_-]{20,}|1//0[0-9A-Za-z_-]{30,})(?![+/=])")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("bearer", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{20,}=*")),
]
ENV_SECRET = re.compile(r"\b([A-Z][A-Z0-9_]*(?:SECRET|TOKEN|PASSWORD|PASSWD|API_KEY|APIKEY)[A-Z0-9_]*)=([^\s\"'\\]{12,})")


def redact(text):
    counts = {}
    for kind, rx in SECRETS:
        text, n = rx.subn(f"[REDACTED:{kind}]", text)
        if n:
            counts[kind] = n

    def env(m):
        if m.group(2).isdigit() or m.group(2).startswith("[REDACTED"):
            return m.group(0)
        counts["env"] = counts.get("env", 0) + 1
        return f"{m.group(1)}=[REDACTED:env]"
    return ENV_SECRET.sub(env, text), counts


def sha(data):
    return hashlib.sha256(data).hexdigest()


def line_hash(entry):
    body = {k: v for k, v in entry.items() if k != "hash"}
    return sha(json.dumps(body, sort_keys=True, ensure_ascii=False).encode())


def load_index():
    if not INDEX.exists():
        return []
    return [json.loads(l) for l in INDEX.read_text().splitlines() if l.strip()]


def ledger_jobs():
    jobs = {}
    for f in LEDGER.glob("*.jsonl") if LEDGER.exists() else []:
        for l in f.read_text(errors="ignore").splitlines():
            try:
                r = json.loads(l)
            except ValueError:
                continue
            if r.get("session_id"):
                jobs[r["session_id"]] = {"job": r.get("job") or f.stem, "git_sha": r.get("git_sha")}
    return jobs


def active_employer():
    f = REPO / "employers" / "ACTIVE"
    slug = f.read_text().strip() if f.exists() else ""
    return None if slug in ("", "none") else slug


def git_sha_at(ts):
    try:
        out = subprocess.run(["git", "-C", str(REPO), "log", "-1", "--all", f"--before={ts}", "--format=%H"],
                             capture_output=True, text=True, timeout=10).stdout.strip()
        return out or None
    except (OSError, subprocess.SubprocessError):
        return None


def flat(text):
    return re.sub(r"\s+", " ", text)


def text_of(content):
    if isinstance(content, str):
        return content
    return " ".join(b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")


def describe(lines):
    """Metadata of one transcript: origin, times, title, counts, files written, skills used, taint."""
    d = {"human": False, "started": None, "ended": None, "title": None, "n_user": 0, "n_tools": 0, "n_errors": 0,
         "entrypoint": None, "cc_version": None, "git_branch": None, "files": [], "skills": []}
    files, skills = [], []
    for raw in lines:
        try:
            e = json.loads(raw)
        except ValueError:
            continue
        ts = e.get("timestamp")
        if ts:
            d["started"] = d["started"] or ts
            d["ended"] = ts
        d["entrypoint"] = d["entrypoint"] or e.get("entrypoint")
        d["cc_version"] = d["cc_version"] or e.get("version")
        d["git_branch"] = d["git_branch"] or e.get("gitBranch")
        if (e.get("origin") or {}).get("kind") == "human":
            d["human"] = True
            t = text_of((e.get("message") or {}).get("content")).strip()
            if t and not t.startswith("<"):
                d["n_user"] += 1
                d["title"] = d["title"] or re.sub(r"\s+", " ", t)[:140]
        content = (e.get("message") or {}).get("content")
        if e.get("type") == "assistant" and isinstance(content, list):
            for b in content:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    d["n_tools"] += 1
                    inp = b.get("input") or {}
                    if b.get("name") == "Skill" and inp.get("skill"):
                        skills.append(inp["skill"])
                    fp = str(inp.get("file_path", ""))
                    m = re.search(r"resources/skills/(.+?)/SKILL\.md$", fp)
                    if b.get("name") == "Read" and m:
                        skills.append(m.group(1))
        if e.get("type") == "user" and isinstance(content, list):
            d["n_errors"] += sum(1 for b in content if isinstance(b, dict) and b.get("is_error"))
    kinds = set()
    for k, v in ingest_lint.events(lines):
        if k == "taint":
            kinds.add(v)
        elif k == "write":
            p = str(v)
            files.append(p[len(str(REPO)) + 1:] if p.startswith(str(REPO) + "/") else p)
    d["files"] = list(dict.fromkeys(files))[:60]
    d["skills"] = list(dict.fromkeys(skills))[:30]
    d["taint"] = sorted(kinds)
    if not d["title"]:
        for raw in lines:   # headless runs: the launch prompt is the first user message
            try:
                e = json.loads(raw)
            except ValueError:
                continue
            if e.get("type") == "user" and not e.get("isMeta"):
                t = text_of((e.get("message") or {}).get("content")).strip()
                if t and not t.startswith("<"):
                    d["title"] = re.sub(r"\s+", " ", t)[:140]
                    break
    return d


def sync(args):
    index = load_index()
    latest = {}
    for e in index:
        latest[e["rel"]] = e
    jobs = ledger_jobs()
    employer = active_employer()
    cutoff = time.time() - args.idle_min * 60
    prev = index[-1]["hash"] if index else GENESIS
    seq = index[-1]["seq"] if index else 0
    added = skipped = 0
    redacted = {}
    out = None
    if not args.dry_run:
        ARCHIVE.mkdir(parents=True, exist_ok=True)
        os.chmod(ARCHIVE, 0o700)
        out = open(INDEX, "a")
    for path in sorted(PROJECTS.glob("*/*.jsonl")) + sorted(PROJECTS.glob("*/*/subagents/*.jsonl")):
        st = path.stat()
        rel = str(path.relative_to(PROJECTS))
        last = latest.get(rel)
        if st.st_mtime > cutoff:
            continue
        if last and last["bytes_raw"] == st.st_size and last.get("mtime") == int(st.st_mtime):
            continue
        raw = path.read_bytes()
        digest = sha(raw)
        if last and last["sha256_raw"] == digest:
            skipped += 1
            continue
        text, counts = redact(raw.decode("utf-8", errors="replace"))
        lines = text.splitlines()
        meta = describe(lines)
        sub = path.parent.name == "subagents"
        sid = path.parent.parent.name if sub else path.stem
        run = jobs.get(sid, {})
        version = (last["version"] + 1) if last else 1
        stored = Path(rel).with_suffix("").as_posix() + (f".v{version}" if version > 1 else "") + ".jsonl.gz"
        blob = gzip.compress(text.encode(), mtime=0)
        seq += 1
        entry = {
            "seq": seq, "archived_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "rel": rel, "project": rel.split("/", 1)[0], "session_id": sid,
            "agent": path.stem if sub else None, "version": version,
            "origin": "human" if meta["human"] else "job" if run else "automated", "job": run.get("job"),
            "title": redact(meta["title"] or "")[0] or None, "started": meta["started"], "ended": meta["ended"],
            "git_sha": run.get("git_sha") or (git_sha_at(meta["started"]) if meta["started"] else None),
            "git_branch": meta["git_branch"], "cc_version": meta["cc_version"], "entrypoint": meta["entrypoint"],
            "employer": employer, "taint": meta["taint"], "files_written": meta["files"], "skills_used": meta["skills"],
            "n_user": meta["n_user"], "n_tools": meta["n_tools"], "n_errors": meta["n_errors"],
            "redactions": counts, "bytes_raw": st.st_size, "mtime": int(st.st_mtime),
            "sha256_raw": digest, "stored": stored, "sha256_stored": sha(blob), "prev": prev,
        }
        entry["hash"] = line_hash(entry)
        for k, n in counts.items():
            redacted[k] = redacted.get(k, 0) + n
        added += 1
        if args.dry_run:
            seq -= 1
            continue
        dest = ARCHIVE / stored
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(blob)
        os.chmod(dest, 0o600)
        out.write(json.dumps(entry, ensure_ascii=False) + "\n")
        out.flush()
        prev = entry["hash"]
        latest[rel] = entry
    if out:
        out.close()
        os.chmod(INDEX, 0o600)
    print(f"{'would archive' if args.dry_run else 'archived'} {added} transcript(s), {skipped} unchanged by content; "
          f"redactions {redacted or 'none'}; chain head {prev[:16]}")


def verify(_args):
    index, prev, bad = load_index(), GENESIS, []
    for i, e in enumerate(index):
        if e.get("prev") != prev:
            bad.append(f"seq {e.get('seq')}: chain broken (a line before it was changed or removed)")
        if line_hash(e) != e.get("hash"):
            bad.append(f"seq {e.get('seq')}: index line altered")
        f = ARCHIVE / e["stored"]
        if not f.exists():
            bad.append(f"seq {e.get('seq')}: {e['stored']} missing")
        elif sha(f.read_bytes()) != e["sha256_stored"]:
            bad.append(f"seq {e.get('seq')}: {e['stored']} altered")
        if e.get("seq") != i + 1:
            bad.append(f"line {i + 1}: seq {e.get('seq')} out of order")
        prev = e.get("hash")
    for b in bad[:50]:
        print("FAIL", b)
    print(f"{'FAIL' if bad else 'OK'}: {len(index)} entries, {len(bad)} problem(s); chain head {prev[:16]}")
    return 1 if bad else 0


def current():
    """Latest version of each archived transcript, main sessions only."""
    latest = {}
    for e in load_index():
        if not e.get("agent"):
            latest[e["rel"]] = e
    return sorted(latest.values(), key=lambda e: e.get("started") or "")


def read_stored(e):
    with gzip.open(ARCHIVE / e["stored"], "rt", errors="replace") as f:
        return f.read()


def find(args):
    rows = []
    for e in current():
        day = (e.get("started") or "")[:10]
        if (args.since and day < args.since) or (args.until and day > args.until):
            continue
        if args.origin and e["origin"] != args.origin or args.job and e.get("job") != args.job:
            continue
        if args.text and args.text.lower() not in " ".join(
                [e.get("title") or ""] + e.get("skills_used", []) + e.get("files_written", [])).lower():
            continue
        if args.file and not any(args.file in f for f in e.get("files_written", [])):
            continue
        if args.grep and not re.search(args.grep, read_stored(e), re.I):
            continue
        rows.append(e)
    for e in rows[-args.limit:]:
        who = e["job"] if e["origin"] == "job" else e["origin"]
        print(f"{(e.get('started') or '')[:16]}  {e['session_id'][:8]}  {who:<14} {e['n_tools']:>4} tools  "
              f"{e.get('title') or '-'}")
    print(f"{len(rows)} session(s)" + (f", last {args.limit} shown" if len(rows) > args.limit else ""))


def show(args):
    hits = [e for e in current() if e["session_id"].startswith(args.session)]
    if len(hits) != 1:
        print(f"{len(hits)} archived sessions match '{args.session}'" + (": give more of the id" if hits else ""))
        return 1
    e = hits[0]
    cut = (lambda s, n: s) if args.all else (lambda s, n: s if len(s) <= n else s[:n] + " …")
    print(f"# {e['session_id']}  v{e['version']}  {e['origin']}{' / ' + e['job'] if e.get('job') else ''}")
    for k in ("started", "ended", "git_sha", "git_branch", "employer", "taint", "skills_used", "files_written",
              "redactions"):
        print(f"{k}: {e.get(k)}")
    print()
    calls = {}
    for raw in read_stored(e).splitlines():
        try:
            m = json.loads(raw)
        except ValueError:
            continue
        ts, content = (m.get("timestamp") or "")[11:16], (m.get("message") or {}).get("content")
        out = []
        if m.get("type") == "user":
            if isinstance(content, str) or (m.get("origin") or {}).get("kind") == "human":
                t = text_of(content).strip()
                if t and not m.get("isMeta"):
                    out.append(f"{ts} USER   {cut(flat(t), 600)}")
            for b in content if isinstance(content, list) else []:
                if isinstance(b, dict) and b.get("type") == "tool_result" and b.get("is_error"):
                    out.append(f"{ts} ERROR  {calls.get(b.get('tool_use_id'), '?')}: "
                               f"{cut(flat(str(b.get('content'))), 220)}")
        elif m.get("type") == "assistant" and isinstance(content, list):
            for b in content:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "text" and b.get("text", "").strip():
                    out.append(f"{ts} AGENT  {cut(flat(b['text']), 400)}")
                elif b.get("type") == "tool_use":
                    calls[b.get("id")] = b.get("name")
                    out.append(f"{ts} TOOL   {b.get('name')} {cut(json.dumps(b.get('input'), ensure_ascii=False), 200)}")
        for o in out:
            if not args.grep or re.search(args.grep, o, re.I):
                print(o)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("sync")
    p.add_argument("--idle-min", type=int, default=120)
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(fn=sync)
    sub.add_parser("verify").set_defaults(fn=verify)
    p = sub.add_parser("find")
    for a in ("--since", "--until", "--text", "--file", "--origin", "--job", "--grep"):
        p.add_argument(a)
    p.add_argument("--limit", type=int, default=40)
    p.set_defaults(fn=find)
    p = sub.add_parser("show")
    p.add_argument("session")
    p.add_argument("--all", action="store_true")
    p.add_argument("--grep")
    p.set_defaults(fn=show)
    a = ap.parse_args()
    return a.fn(a) or 0


if __name__ == "__main__":
    sys.exit(main())
