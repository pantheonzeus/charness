"""Mail view: triaged mail by company → to know / action needed / answer needed.

Reads what workflow-ops/mail-triage writes (output/mail-triage/: index.json, messages/, triage/,
state.json). The only file written here is decisions.json (done / dismissed / sent). Sending
shells out to `triage.py send`, which holds the gmail.send token, and only on an explicit click.
"""
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "output" / "mail-triage"
DECISIONS = OUT / "decisions.json"
HELPER = REPO / "resources/skills/workflow-ops/mail-triage/scripts/triage.py"
sys.path.insert(0, str(REPO / "scripts"))
import employer  # noqa: E402  employer pack (employers/README.md): the company list
CONFIG = employer.path("mail-triage/companies.json")
SEND_TOKEN = Path.home() / ".config/mail-triage/send-token.json"
ID_RX = re.compile(r"[0-9a-f]{8,24}")
PLACEHOLDER = re.compile(r"\[confirm:", re.I)
WINDOW_DAYS = 45

router = APIRouter()


def load(path, default):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return default


def decide(mid, **fields):
    d = load(DECISIONS, {})
    d[mid] = {**fields, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    tmp = DECISIONS.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, indent=1, ensure_ascii=False))
    tmp.replace(DECISIONS)


@router.get("/api/mail")
def mail():
    index, state, decided = load(OUT / "index.json", {}), load(OUT / "state.json", {}), load(DECISIONS, {})
    order = [c["name"] for c in load(CONFIG, {}).get("companies", [])]
    groups = {n: {"name": n, "know": [], "action": [], "answer": [], "pending": 0} for n in order}
    cutoff = (time.time() - WINDOW_DAYS * 86400) * 1000
    for mid, e in index.items():
        comp = e.get("company")
        if comp not in groups or e.get("state") in ("skip", "noise") or mid in decided or e.get("replied") or e["ms"] < cutoff:
            continue
        if e["state"] in ("new", "queued"):
            groups[comp]["pending"] += 1
            continue
        m, t = load(OUT / "messages" / f"{mid}.json", None), load(OUT / "triage" / f"{mid}.json", None)
        if not m or not t or t.get("category") not in ("know", "action", "answer"):
            continue
        groups[comp][t["category"]].append({
            "id": mid, "ms": e["ms"], "from": m["from_name"], "from_email": m["from_email"], "subject": m["subject"],
            "to": m["to"], "cc": m["cc"], "thread_id": m["thread_id"], "summary": t["summary"],
            "action": t.get("action", ""), "reply": t.get("reply", ""), "reply_all": bool(t.get("reply_all")),
            "already_replied": m.get("already_replied", False)})
    for g in groups.values():
        for k in ("know", "action", "answer"):
            g[k].sort(key=lambda x: -x["ms"])
    run = state.get("run")
    return {"last_poll": state.get("last_poll"), "error": state.get("error"), "waiting": state.get("waiting", 0),
            "running": bool(run), "failed": sum(1 for e in index.values() if e.get("state") == "failed"),
            "send_ready": SEND_TOKEN.exists(), "companies": list(groups.values())}


def _id(mid):
    if not ID_RX.fullmatch(mid):
        raise HTTPException(400, "bad id")
    return mid


@router.post("/api/mail/{mid}/done")
async def done(mid: str, request: Request):
    body = await request.json()
    decide(_id(mid), action=body.get("action", "done"))
    return {"ok": True}


@router.post("/api/mail/{mid}/send")
async def send(mid: str, request: Request):
    _id(mid)
    body = await request.json()
    text = str(body.get("body", "")).strip()
    if not text:
        raise HTTPException(400, "The reply is empty.")
    if PLACEHOLDER.search(text):
        raise HTTPException(400, "The reply still has a [confirm: …] placeholder. Fill it in first.")
    if not SEND_TOKEN.exists():
        raise HTTPException(409, f"Sending isn't set up. Run once in a terminal: uv run {HELPER.relative_to(REPO)} auth-send")
    if mid in load(DECISIONS, {}):
        raise HTTPException(409, "Already handled.")
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(text + "\n")
    cmd = ["uv", "run", "-q", str(HELPER), "send", mid, "--body-file", f.name] + (["--all"] if body.get("reply_all") else [])
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=120)
    Path(f.name).unlink(missing_ok=True)
    if r.returncode != 0:
        raise HTTPException(502, (r.stderr or r.stdout).strip().splitlines()[-1] if (r.stderr or r.stdout).strip() else "Send failed.")
    res = json.loads(r.stdout.strip().splitlines()[-1])
    decide(mid, action="sent", to=res.get("to"), cc=res.get("cc"), gmail_id=res.get("gmail_id"), body=text)
    return res
