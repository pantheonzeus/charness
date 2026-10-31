# /// script
# requires-python = ">=3.10"
# dependencies = ["google-api-python-client", "google-auth", "google-auth-oauthlib"]
# ///
"""mail-triage: the deterministic half. launchd runs `poll` every minute.

1. Pull new mail from the companies in the active employer pack's mail-triage/companies.json
   (employers/README.md; template: schema/companies.example.json) through the Gmail API with the
   stored read-only token (no LLM, no browser). Calendar/automated mail is parked as noise.
2. Each kept message lands as output/mail-triage/messages/<id>.json (headers + body text).
3. If untriaged messages are waiting and no run is alive, launch one headless triage run
   (claude -p via run_agent.sh, agent `mail-triage`) on a batch. The agent writes
   output/mail-triage/triage/<id>.json: know | action | answer, a summary, and a reply draft.
4. Every few polls, open items whose thread you already answered in Gmail are marked replied.

Sending is separate and only ever on your click in the console (`send`), with its own
gmail.send token. Files and writers: index.json + state.json (this poller only),
decisions.json (the console only), triage/ (the agent only).

  uv run triage.py poll                              one poll (what launchd runs)
  uv run triage.py poll --no-launch                  ingest only
  uv run triage.py backfill <Company> [--count 100]  queue the last N kept mails of one company
  uv run triage.py check <id> [<id> ...]             validate triage files (the agent's done-gate)
  uv run triage.py auth-send                         one-time browser consent for gmail.send
  uv run triage.py send <id> --body-file F [--all]   send the approved reply in-thread
"""
import argparse
import base64
import contextlib
import datetime as dt
import fcntl
import html
import json
import os
import re
import subprocess
import sys
import time
from email.message import EmailMessage
from email.utils import getaddresses, parseaddr
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO / "scripts"))
import employer  # noqa: E402  employer pack (employers/README.md): company list + the mail binding
CONFIG = employer.path("mail-triage/companies.json")
OUT = REPO / "output" / "mail-triage"
MSGS = OUT / "messages"
TRIAGE = OUT / "triage"
INDEX = OUT / "index.json"
STATE = OUT / "state.json"
DECISIONS = OUT / "decisions.json"
LOG = REPO / "output" / "mail-triage.log"
LOCK = OUT / ".lock"
READ_TOKEN = Path.home() / ".config/mail-to-conversations/token.json"   # shared with mail-to-conversations + meeting-prep-loop
SEND_TOKEN = Path.home() / ".config/mail-triage/send-token.json"
CLIENT = Path.home() / ".config/calendar-to-contacts/credentials.json"
READ_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"
SELF = subprocess.run(["git", "config", "--get", "charness.selfEmail"], cwd=REPO,
                      capture_output=True, text=True).stdout.strip().lower()

POLL_DAYS = 2        # the minute poll looks this far back; the index makes it idempotent
BATCH = 12           # messages per triage run
DAILY_CAP = 40       # triage runs per day — runaway guard for the subscription
MAX_ATTEMPTS = 3     # a message that fails this often is parked as "failed"
RUN_TIMEOUT = 1800   # a run older than this is treated as dead
REPLY_CHECK_EVERY = 5
BODY_CHARS = 6000
CATEGORIES = {"know", "action", "answer"}

# Noise rules, same as mail-to-conversations/build_conversations.py (calendar + automated senders).
_CAL = re.compile(r"^(invitation|accepted|declined|tentative|tentatively accepted|updated invitation|cancell?ed|"
                  r"canceled|new event|reminder|proposed new time|new updates|automatic reply|out of office)\b", re.I)
_AUTO_LOCAL = re.compile(
    r"^(no-?reply|noreply|do-?not-?reply|invoicing|invoice|billing|notifications?|mailer|mailer-daemon|postmaster|"
    r"bounce|purchase-?orders?|accounts-?payable|calendar|calendar-notification|newsletter|marketing)([._-]|$)", re.I)


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
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as f:
        f.write(f"{dt.datetime.now():%Y-%m-%d %H:%M:%S} {msg}\n")


@contextlib.contextmanager
def locked(wait):
    """One writer of index.json at a time: a poll skips while a backfill holds the lock."""
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    with LOCK.open("w") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | (0 if wait else fcntl.LOCK_NB))
        except BlockingIOError:
            yield False
            return
        yield True


def creds(token_path, scope):
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    if not token_path.exists():
        raise RuntimeError(f"No Google login at {token_path}")
    c = Credentials.from_authorized_user_file(str(token_path), [scope])
    if not c.valid:
        if not (c.expired and c.refresh_token):
            raise RuntimeError(f"Google login at {token_path} is invalid — re-consent once in a terminal")
        c.refresh(Request())
        token_path.write_text(c.to_json())
    return c


def gmail(token=READ_TOKEN, scope=READ_SCOPE):
    from googleapiclient.discovery import build
    return build("gmail", "v1", credentials=creds(token, scope), cache_discovery=False)


# ---------- companies ----------

def companies():
    return load(CONFIG, {}).get("companies", [])


def _dom_match(email, domains):
    d = email.rsplit("@", 1)[-1].lower()
    return any(d == x or d.endswith("." + x) for x in domains)


def company_of(from_email, rcpts):
    for c in companies():
        lists = {x.lower() for x in c.get("lists", [])}
        if lists & ({from_email} | set(rcpts)) or _dom_match(from_email, c.get("domains", [])):
            return c["name"]
    return None


def query(only=None, days=None):
    terms = []
    for c in companies():
        if only and c["name"].lower() != only.lower():
            continue
        terms += [f"from:{d}" for d in c.get("domains", [])]
        terms += [f"{h}:{l}" for l in c.get("lists", []) for h in ("from", "to", "cc")]
    if not terms:
        raise SystemExit(f"No company matches {only!r} in {CONFIG}")
    return ("{" + " ".join(terms) + "} -from:me" + (f" newer_than:{days}d" if days else "")).strip()


# ---------- ingest ----------

def body_text(payload):
    """Prefer text/plain anywhere in the MIME tree; fall back to stripped text/html."""
    found = {}

    def walk(p):
        mt, data = p.get("mimeType", ""), p.get("body", {}).get("data")
        if data and mt in ("text/plain", "text/html") and mt not in found:
            found[mt] = base64.urlsafe_b64decode(data + "===").decode("utf-8", "replace")
        for c in p.get("parts", []) or []:
            walk(c)
    walk(payload)
    if "text/plain" in found:
        return found["text/plain"]
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", found.get("text/html", ""))
    h = re.sub(r"(?i)<br\s*/?>|</p>|</div>", "\n", h)
    return html.unescape(re.sub(r"<[^>]+>", " ", h))


def thread_replied(svc, thread_id, after_ms):
    """True if a message you sent sits in the thread after `after_ms`."""
    t = svc.users().threads().get(userId="me", id=thread_id, format="minimal").execute()
    return any("SENT" in m.get("labelIds", []) and int(m.get("internalDate", 0)) > after_ms
               for m in t.get("messages", []))


def ingest(svc, mid, index):
    m = svc.users().messages().get(userId="me", id=mid, format="full").execute()
    h = {x["name"].lower(): x["value"] for x in m["payload"].get("headers", [])}
    name, frm = parseaddr(h.get("from", ""))
    # A Google Group relays outside mail as "'Sender' via group" <group@yourdomain>; classify on the real sender.
    name = re.sub(r"^'?(.*?)'? via .*$", r"\1", name)
    frm = (parseaddr(h.get("x-original-sender", ""))[1] or frm).lower()
    rcpts = [a.lower() for _, a in getaddresses([h.get("to", ""), h.get("cc", "")]) if a]
    ms = int(m.get("internalDate", 0))
    comp = company_of(frm, rcpts)
    if frm == SELF or "SENT" in m.get("labelIds", []) or not comp:
        index[mid] = {"state": "skip", "ms": ms}
        return None
    noise = bool(_CAL.match(h.get("subject", "")) or _AUTO_LOCAL.match(frm.split("@")[0]))
    entry = {"state": "noise" if noise else "new", "company": comp, "ms": ms, "thread_id": m["threadId"], "attempts": 0}
    if not noise:
        text = re.sub(r"\n{3,}", "\n\n", body_text(m["payload"])).strip()
        save(MSGS / f"{mid}.json", {
            "id": mid, "thread_id": m["threadId"], "company": comp,
            "date": dt.datetime.fromtimestamp(ms / 1000).isoformat(timespec="minutes"),
            "from_name": name or frm, "from_email": frm, "reply_to": h.get("reply-to", ""),
            "to": h.get("to", ""), "cc": h.get("cc", ""), "subject": h.get("subject", ""),
            "message_id": h.get("message-id", ""), "references": h.get("references", ""),
            "snippet": html.unescape(m.get("snippet", "")),
            "already_replied": thread_replied(svc, m["threadId"], ms),
            "body_text": text[:BODY_CHARS] + ("\n[…truncated]" if len(text) > BODY_CHARS else "")})
    index[mid] = entry
    return entry


def list_ids(svc, q, limit):
    ids, token = [], None
    while len(ids) < limit:
        r = svc.users().messages().list(userId="me", q=q, maxResults=min(100, limit - len(ids)), pageToken=token).execute()
        ids += [x["id"] for x in r.get("messages", [])]
        token = r.get("nextPageToken")
        if not token:
            break
    return ids


# ---------- runs ----------

def alive(run):
    if not run or time.time() - run.get("started", 0) > RUN_TIMEOUT:
        return False
    try:
        os.kill(run["pid"], 0)
        return True
    except (OSError, KeyError):
        return False


def valid(mid):
    """Errors in triage/<id>.json, [] if it is good."""
    t = load(TRIAGE / f"{mid}.json", None)
    if not isinstance(t, dict):
        return ["missing or not JSON"]
    errs = []
    if t.get("id") != mid:
        errs.append("id must equal the message id")
    if t.get("category") not in CATEGORIES:
        errs.append(f"category must be one of {sorted(CATEGORIES)}")
    if not str(t.get("summary", "")).strip():
        errs.append("summary is empty")
    if t.get("category") in ("action", "answer") and not str(t.get("action", "")).strip():
        errs.append("action is empty")
    if t.get("category") == "answer" and not str(t.get("reply", "")).strip():
        errs.append("reply is empty")
    return errs


def launch(batch):
    now = dt.datetime.now()
    run = f"{now:%Y%m%d-%H%M%S}-mail-triage"
    root = REPO / "output/.runs" / run
    save(root / "TASK.json", {"created": now.isoformat(timespec="seconds"),
                              "messages": [f"output/mail-triage/messages/{m}.json" for m in batch]})
    (root / "RESPONSE.md").write_text(
        f"# {run}\n\n- [ ] Read every message file in TASK.json\n"
        "- [ ] Wrote output/mail-triage/triage/<id>.json for each, per the mail-triage skill\n"
        "- [ ] `triage.py check` prints OK for every id\n")
    helper = "resources/skills/workflow-ops/mail-triage/scripts/triage.py"
    prompt = (f"Read and follow resources/skills/workflow-ops/mail-triage/SKILL.md (a repo skill: open it with Read, not the Skill tool). Triage the {len(batch)} message(s) listed in "
              f"output/.runs/{run}/TASK.json: write output/mail-triage/triage/<id>.json for each, then run "
              f"`uv run {helper} check {' '.join(batch)}` until it prints OK. Tick every checkpoint in "
              f"output/.runs/{run}/RESPONSE.md before stopping.")
    tools = ["Read", "Glob", "Grep", "Write", f"Bash(uv run {helper} check:*)", f"Bash(uv run {REPO}/{helper} check:*)",
             "Bash(date:*)"]
    env = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")}
    with LOG.open("a") as f:
        p = subprocess.Popen(["bash", str(REPO / "scripts/run_agent.sh"), "mail-triage", str(root / "RESPONSE.md"),
                              prompt, "--permission-mode", "acceptEdits", "--allowedTools", *tools],
                             cwd=REPO, env=env, stdout=f, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                             start_new_session=True)
    log(f"launched {run} ({len(batch)} messages, pid {p.pid})")
    return {"id": run, "pid": p.pid, "started": time.time(), "messages": batch}


def reconcile(index, state):
    """Move queued → triaged as files land; a finished run's leftovers go back to new (or failed)."""
    run = state.get("run")
    done = not alive(run)
    for mid, e in index.items():
        if e.get("state") != "queued":
            continue
        if not valid(mid):
            e["state"] = "triaged"
        elif done:
            e["attempts"] = e.get("attempts", 0) + 1
            e["state"] = "failed" if e["attempts"] >= MAX_ATTEMPTS else "new"
    if done:
        state["run"] = None


def poll(launch_runs=True):
    index, state = load(INDEX, {}), load(STATE, {})
    state["last_poll"] = dt.datetime.now().isoformat(timespec="seconds")
    try:
        svc = gmail()
        added = [m for m in list_ids(svc, query(days=POLL_DAYS), 50) if m not in index]
        for mid in added:
            ingest(svc, mid, index)
        state["error"] = None
        state["polls"] = state.get("polls", 0) + 1
        if state["polls"] % REPLY_CHECK_EVERY == 0:
            decided = load(DECISIONS, {})
            cutoff = (time.time() - 30 * 86400) * 1000
            for mid, e in index.items():
                if e.get("state") == "triaged" and mid not in decided and not e.get("replied") and e["ms"] > cutoff:
                    if load(TRIAGE / f"{mid}.json", {}).get("category") in ("action", "answer") \
                            and thread_replied(svc, e["thread_id"], e["ms"]):
                        e["replied"] = True
        if added:
            log(f"poll: {len(added)} new")
    except Exception as ex:  # an expired login must show up in the console, not kill the loop
        state["error"] = f"{type(ex).__name__}: {ex}"
        log(f"poll error: {state['error']}")
    reconcile(index, state)
    today = f"{dt.date.today()}"
    if state.get("runs_day") != today:
        state["runs_day"], state["runs_today"] = today, 0
    waiting = sorted((m for m, e in index.items() if e.get("state") == "new"), key=lambda m: -index[m]["ms"])
    if launch_runs and waiting and not alive(state.get("run")) and state["runs_today"] < DAILY_CAP:
        batch = waiting[:BATCH]
        for m in batch:
            index[m]["state"] = "queued"
        state["run"] = launch(batch)
        state["runs_today"] += 1
    state["waiting"] = sum(1 for e in index.values() if e.get("state") == "new")
    save(INDEX, index)
    save(STATE, state)


def backfill(company, count):
    index = load(INDEX, {})
    svc = gmail()
    kept = scanned = 0
    for mid in list_ids(svc, query(only=company), count * 8):
        scanned += 1
        e = index.get(mid) or ingest(svc, mid, index)
        if e and e.get("state") not in ("noise", "skip"):
            kept += 1
        if kept >= count:
            break
    save(INDEX, index)
    print(f"{company}: {kept} kept of {scanned} scanned; untriaged ones go to the next poll's runs")


# ---------- send ----------

def auth_send():
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT), [SEND_SCOPE])
    c = flow.run_local_server(port=0, open_browser=True)
    SEND_TOKEN.parent.mkdir(parents=True, exist_ok=True)
    SEND_TOKEN.write_text(c.to_json())
    os.chmod(SEND_TOKEN, 0o600)
    print(f"OK: gmail.send token saved to {SEND_TOKEN}")


def send(mid, body, reply_all):
    m = load(MSGS / f"{mid}.json", None)
    if not m:
        raise SystemExit(f"unknown message {mid}")
    to = parseaddr(m["reply_to"])[1] or m["from_email"]
    cc = []
    if reply_all:
        seen = {to.lower(), SELF}
        for _, a in getaddresses([m["to"], m["cc"]]):
            if a and a.lower() not in seen:
                seen.add(a.lower())
                cc.append(a)
    msg = EmailMessage()
    msg["To"] = to
    if cc:
        msg["Cc"] = ", ".join(cc)
    subj = m["subject"]
    msg["Subject"] = subj if re.match(r"(?i)^(re|aw|antw):", subj) else f"Re: {subj}"
    if m["message_id"]:
        msg["In-Reply-To"] = m["message_id"]
        msg["References"] = f"{m['references']} {m['message_id']}".strip()
    msg.set_content(body)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    r = gmail(SEND_TOKEN, SEND_SCOPE).users().messages().send(
        userId="me", body={"raw": raw, "threadId": m["thread_id"]}).execute()
    log(f"sent reply to {mid} → {to}{' +cc ' + str(len(cc)) if cc else ''} (gmail id {r.get('id')})")
    print(json.dumps({"ok": True, "gmail_id": r.get("id"), "to": to, "cc": cc}))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("poll"); p.add_argument("--no-launch", action="store_true")
    p = sub.add_parser("backfill"); p.add_argument("company"); p.add_argument("--count", type=int, default=100)
    p = sub.add_parser("check"); p.add_argument("ids", nargs="+")
    sub.add_parser("auth-send")
    p = sub.add_parser("send"); p.add_argument("id"); p.add_argument("--body-file", required=True)
    p.add_argument("--all", action="store_true", help="reply all (minus you)")
    a = ap.parse_args()
    if a.cmd != "check":
        employer.require("mail", "google", "mail-triage")
    if a.cmd == "poll":
        with locked(wait=False) as ok:
            if ok:
                poll(not a.no_launch)
    elif a.cmd == "backfill":
        with locked(wait=True):
            backfill(a.company, a.count)
    elif a.cmd == "check":
        bad = {m: valid(m) for m in a.ids if valid(m)}
        for m, errs in bad.items():
            print(f"{m}: {'; '.join(errs)}")
        print("OK" if not bad else f"FAIL: {len(bad)} of {len(a.ids)}")
        sys.exit(1 if bad else 0)
    elif a.cmd == "auth-send":
        auth_send()
    elif a.cmd == "send":
        send(a.id, Path(a.body_file).read_text(), a.all)


if __name__ == "__main__":
    main()
