# /// script
# requires-python = ">=3.10"
# ///
"""Client news watch: every hour, find new public news about the active employer's clients and turn the
material items into meeting-ready briefs with a point of view.

The watch list is employer config: employers/<active>/client-news/clients.json (template:
schema/clients.example.json). Each client has Google News queries, locales, a must/exclude filter,
its vault account note and its key people.

  run [--init] [--only A,B]   one pass: poll → ingest → (if new items and under the daily cap) analyse → check → index
  check <STATE_ROOT>           validate the analyse agent's files for one run
  status                       JSON summary for the console

The poll is plain HTTP to Google News RSS, no LLM: a quiet hour costs nothing. Queries carry only
public company and people names from the config, never pursuit details. The analyse step is a
full-harness agent (`run_agent.sh client-news`) and runs only when something new arrived.
"""
import datetime as dt
import email.utils
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
REPO = SKILL.parents[3]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "webapp"))
import employer  # noqa: E402  employer pack (employers/README.md): the client watch list
import push  # noqa: E402  iMessage to the principal's own phone
CONFIG = employer.path("client-news/clients.json")
OUT = REPO / "output" / "client-news"
ITEMS, TRIAGE, BRIEFS, FINDINGS = OUT / "items", OUT / "triage", OUT / "briefs", OUT / "findings"
STATE = OUT / "state.json"
LOCK = OUT / ".lock"
LEDGER = REPO / "output" / ".runs" / "_ledger"
RUN_AGENT = REPO / "scripts" / "run_agent.sh"
PAGE = REPO / "resources/skills/workflow-ops/reading-pages/scripts/page.py"
INDEXER = REPO / "resources/skills/vault-hygiene/deliverable-index/scripts/index_deliverables.py"
VAULT = REPO / "cbrain"
DAILY_CAP_USD = 20      # set by the principal, 2026-10-31; the agent file's budget_usd caps each run
INIT_BUDGET = "10"
MAX_ITEMS = 15          # items handed to one run; the rest wait for the next hour
MAX_ATTEMPTS = 2        # an item whose analysis failed twice is dropped, not retried forever
CONFIDENCE = {"verified", "likely", "unsure"}
CLI_ENV = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")}
REL = lambda p: str(p.relative_to(REPO))
ANALYSE_TOOLS = ["Read", "Glob", "Grep", "Write", "Edit", "WebSearch", "WebFetch", "Bash(date:*)", "Bash(ls:*)",
                 f"Bash(uv run {REL(PAGE)}:*)", f"Bash(uv run {PAGE}:*)",
                 f"Bash(uv run {REL(Path(__file__))}:*)", f"Bash(uv run {Path(__file__)}:*)"]


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


def spent_today():
    """USD the analyse agent has spent today, from run_agent.sh's ledger."""
    today, total = time.strftime("%Y-%m-%d", time.gmtime()), 0.0
    try:
        for line in (LEDGER / "client-news.jsonl").read_text().splitlines():
            r = json.loads(line)
            if str(r.get("ts", "")).startswith(today):
                total += float(r.get("cost_usd") or 0)
    except (OSError, ValueError):
        pass
    return total


def norm_title(title):
    """Google News appends ' - <Source>'; the same story syndicated keeps the same headline."""
    t = re.sub(r"\s+-\s+[^-]{2,60}$", "", html.unescape(title))
    return re.sub(r"[^a-z0-9äöüß]+", " ", t.lower()).strip()


def poll(client, window):
    """Google News RSS for each query x locale → [{title, link, source, published, summary}]."""
    got = []
    for q in client["queries"]:
        for loc in client.get("locales", ["en-US"]):
            lang, country = loc.split("-")
            url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
                {"q": f"{q} when:{window}", "hl": loc, "gl": country, "ceid": f"{country}:{lang}"})
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (cbrain client-news-watch)"})
                root = ET.fromstring(urllib.request.urlopen(req, timeout=30).read())
            except Exception as e:   # one bad feed must not sink the pass
                log(f"{client['name']}: feed failed for {q!r} {loc}: {type(e).__name__}")
                continue
            for it in root.iter("item"):
                pub = it.findtext("pubDate") or ""
                try:
                    published = email.utils.parsedate_to_datetime(pub).astimezone().isoformat(timespec="minutes")
                except (TypeError, ValueError):
                    published = ""
                got.append({"title": html.unescape(it.findtext("title") or "").strip(),
                            "link": (it.findtext("link") or "").strip(),
                            "source": (it.findtext("source") or "").strip(),
                            "published": published,
                            "summary": re.sub(r"<[^>]+>", " ", html.unescape(it.findtext("description") or ""))[:600].strip(),
                            "query": q, "locale": loc})
        time.sleep(1)   # polite to the feed
    return got


def ingest(client, got, state, cap):
    """Write each unseen, on-topic item once. Returns (new item ids newest first, at most cap; overflow count)."""
    seen = state.setdefault("seen", {})
    must = re.compile(client["must"], re.I) if client.get("must") else None
    excl = re.compile(client["exclude"], re.I) if client.get("exclude") else None
    new, over = [], 0
    for g in sorted(got, key=lambda g: g["published"], reverse=True):
        text = f"{g['title']} {g['summary']}"
        key = hashlib.sha1(f"{client['name']}|{norm_title(g['title'])}".encode()).hexdigest()[:12]
        if not g["title"] or key in seen or (must and not must.search(text)) or (excl and excl.search(text)):
            continue
        seen[key] = time.strftime("%Y-%m-%d")
        if len(new) >= cap:
            over += 1
            continue   # marked seen: an init backfill stays a backfill, not a flood next hour
        iid = f"{re.sub(r'[^a-z0-9]+', '-', client['name'].lower()).strip('-')}-{key}"
        save(ITEMS / f"{iid}.json", {"id": iid, "client": client["name"], "note": client["note"], **g})
        new.append(iid)
    return new, over


def pending(state):
    """Ingested items without a triage file that haven't failed too often, oldest first."""
    tries = state.setdefault("attempts", {})
    out = [f.stem for f in sorted(ITEMS.glob("*.json"), key=lambda f: f.stat().st_mtime)
           if not (TRIAGE / f.name).exists() and tries.get(f.stem, 0) < MAX_ATTEMPTS]
    return out[:MAX_ITEMS]


def check(root):
    root = Path(root)
    task = load(root / "TASK.json", None)
    if not task:
        return [f"no TASK.json in {root}"]
    errs, material = [], []
    for iid in task["items"]:
        t = load(TRIAGE / f"{iid}.json", None)
        if not t:
            errs.append(f"missing triage/{iid}.json")
            continue
        if t.get("id") != iid or not isinstance(t.get("material"), bool) or not t.get("why"):
            errs.append(f"triage/{iid}.json needs id, material (bool), why")
        if t.get("material") is True:
            material.append(iid)
    brief, findings = REPO / task["brief"], REPO / task["findings"]
    if not material:
        for p in (brief, findings):
            if p.exists():
                errs.append(f"{REL(p)} written although no item was material")
        return errs
    if not brief.is_file():
        errs.append(f"material items but no brief at {task['brief']}")
    else:
        head = brief.read_text()[:800]
        for pat, msg in ((r"^template:\s*briefing\s*$", "template: briefing"),
                         (r"^confidential:\s*employer-internal\s*$", "confidential: employer-internal")):
            if not re.search(pat, head, re.M):
                errs.append(f"brief frontmatter needs {msg}")
        r = subprocess.run(["uv", "run", "-q", str(PAGE), "check", str(brief)], capture_output=True, text=True, cwd=REPO)
        if r.returncode != 0:
            errs.append("page.py check failed: " + (r.stdout + r.stderr).strip()[-300:])
    d = load(findings, None)
    if not d:
        return errs + [f"material items but no readable findings at {task['findings']}"]
    for t in d.get("topics", []):
        name = t.get("note", "?")
        if not (VAULT / name).is_file():
            errs.append(f"findings: {name} is not a vault note (path relative to cbrain/)")
        for f in t.get("findings", []):
            fid = f.get("id", "?")
            for k in ("id", "text", "so_what"):
                if not str(f.get(k, "")).strip():
                    errs.append(f"findings {name} {fid}: missing {k}")
            if f.get("confidence") not in CONFIDENCE:
                errs.append(f"findings {name} {fid}: confidence must be one of {sorted(CONFIDENCE)}")
            if not f.get("sources") or not all(str(s.get("url", "")).startswith("http") for s in f["sources"]):
                errs.append(f"findings {name} {fid}: needs >=1 source with an http(s) url")
            if not isinstance(f.get("client_safe"), bool):
                errs.append(f"findings {name} {fid}: client_safe must be true or false")
            if not isinstance(f.get("people", []), list):
                errs.append(f"findings {name} {fid}: people must be a list")
    if not sum(len(t.get("findings", [])) for t in d.get("topics", [])):
        errs.append("findings: material items but no finding")
    return errs


def notify(n):
    msg = f"Jarvis: {n} client news brief{'s' if n != 1 else ''} ready. Details on the Mac."
    subprocess.run(["osascript", "-e", f'display notification {json.dumps(msg)} with title "Client news"'], capture_output=True)
    if 7 <= dt.datetime.now().hour < 22:   # no pings at night; the brief waits in the vault
        push.send(msg)   # count only: client names never leave the Mac (push.py, your call 2026-10-27)


def alive():
    try:
        os.kill(int(LOCK.read_text()), 0)
        return True
    except (OSError, ValueError):
        return False


def run(init, only):
    if alive():
        return log("previous run still alive; skipping")
    OUT.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(str(os.getpid()))
    try:
        cfg = load(CONFIG, {})
        clients = [c for c in cfg.get("clients", []) if not only or c["name"] in only.split(",")]
        if not clients:
            return log(f"no clients configured in {CONFIG}")
        state = load(STATE, {"seen": {}, "attempts": {}, "runs": []})
        cutoff = (dt.date.today() - dt.timedelta(days=60)).isoformat()
        state["seen"] = {k: v for k, v in state.get("seen", {}).items() if v >= cutoff}
        fetched = new = dropped = 0
        for c in clients:
            got = poll(c, "7d" if init else cfg.get("window", "2d"))
            ids, over = ingest(c, got, state, cfg.get("items_per_init", 6) if init else cfg.get("items_per_run", 8))
            fetched, new, dropped = fetched + len(got), new + len(ids), dropped + over
            if over:
                log(f"{c['name']}: {over} more new item(s) over the per-run cap, marked seen unanalysed")
        save(STATE, state)   # items are on disk now; a failed analysis must not re-ingest them
        todo = pending(state)
        rec = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "init": init, "fetched": fetched, "new": new, "dropped": dropped, "analysed": len(todo)}
        log(f"fetched {fetched} items, {new} new, {len(todo)} to analyse")
        spent = spent_today()
        if todo and spent >= DAILY_CAP_USD - 1 and not init:
            rec["capped"] = f"daily cap ${DAILY_CAP_USD} reached (${spent:.2f}); {len(todo)} item(s) wait"
            log(rec["capped"])
            todo = []
        if not todo:
            state["runs"] = (state["runs"] + [rec])[-300:]
            return save(STATE, state)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        root = REPO / "output" / ".runs" / f"{stamp}-client-news"
        root.mkdir(parents=True)
        brief = BRIEFS / f"{stamp[:13]}-client-news.md"
        findings = FINDINGS / f"{time.strftime('%Y-%m-%d-%H%M')}.json"
        save(root / "TASK.json", {"items": todo, "item_dir": REL(ITEMS), "triage_dir": REL(TRIAGE),
                                  "brief": REL(brief), "findings": REL(findings), "clients": REL(CONFIG),
                                  "brief_note": f"client-news-briefs-{brief.stem.lower()}",
                                  "init": init, "max_briefs": 6 if init else 3, "max_web_calls": 50 if init else 30})
        (root / "RESPONSE.md").write_text(f"# client-news {stamp}{' (init)' if init else ''}\n"
            "- [ ] every item triaged (triage/<id>.json)\n- [ ] material items researched deep (primary sources first)\n"
            "- [ ] brief written + page.py check OK (only if something was material)\n"
            "- [ ] findings JSON written (frontier shape)\n- [ ] account notes appended\n"
            "- [ ] client_news.py check prints OK\n")
        tries = state.setdefault("attempts", {})
        for iid in todo:
            tries[iid] = tries.get(iid, 0) + 1
        save(STATE, state)
        prompt = (f"Read and follow resources/skills/workflow-ops/client-news-watch/SKILL.md (a repo skill: open it with Read, not the Skill tool) for the task packet {REL(root)}/TASK.json. "
                  f"Your STATE_ROOT is {REL(root)}/. Finish with `uv run {REL(Path(__file__))} check {REL(root)}` printing OK.")
        extra = ["--max-budget-usd", INIT_BUDGET] if init else []
        subprocess.run(["bash", str(RUN_AGENT), "client-news", str(root / "RESPONSE.md"), prompt,
                        "--permission-mode", "acceptEdits", *extra, "--allowedTools", *ANALYSE_TOOLS],
                       cwd=REPO, env=CLI_ENV, stdin=subprocess.DEVNULL)
        errs = check(root)
        n = sum(1 for i in todo if load(TRIAGE / f"{i}.json", {}).get("material"))
        rec.update(ok=not errs, errors=errs[:5], material=n)
        if brief.exists():
            rec["brief"] = REL(brief)
            subprocess.run(["uv", "run", "-q", str(PAGE), "render", str(brief)], cwd=REPO, capture_output=True)
            subprocess.run([sys.executable, str(INDEXER)], cwd=REPO, capture_output=True)   # into the vault
            notify(n)
        log(f"analysis {'OK' if not errs else 'FAILED: ' + '; '.join(errs[:3])}")
        state = load(STATE, state)
        state["runs"] = (state["runs"] + [rec])[-300:]
        save(STATE, state)
    finally:
        LOCK.unlink(missing_ok=True)


def status():
    state = load(STATE, {"runs": []})
    briefs = []
    for f in sorted(BRIEFS.glob("*-client-news.md"), reverse=True)[:30]:
        head = re.search(r"^title:\s*(.+)$", f.read_text()[:800], re.M)
        briefs.append({"path": REL(f), "title": head.group(1).strip().strip('"') if head else f.stem, "html": f.with_suffix(".html").exists()})
    return {"running": alive(), "last_run": (state["runs"] or [None])[-1], "briefs": briefs,
            "spent_today_usd": round(spent_today(), 2), "daily_cap_usd": DAILY_CAP_USD,
            "items": len(list(ITEMS.glob("*.json"))), "material": sum(1 for f in TRIAGE.glob("*.json") if load(f, {}).get("material"))}


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["run"]:
        run("--init" in a, a[a.index("--only") + 1] if "--only" in a else None)
    elif a[:1] == ["check"] and len(a) == 2:
        e = check(a[1])
        print("OK" if not e else "\n".join(e))
        sys.exit(1 if e else 0)
    elif a[:1] == ["status"]:
        print(json.dumps(status(), indent=1))
    else:
        sys.exit(__doc__)
