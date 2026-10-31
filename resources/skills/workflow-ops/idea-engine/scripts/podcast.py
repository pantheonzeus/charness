# /// script
# requires-python = ">=3.10"
# ///
"""Turn one idea into two NotebookLM podcasts: an in-depth one and a short one on the central idea.

  podcast.py <idea id>            new notebook, upload sources, generate both, download, link in the note
  podcast.py <idea id> --dry-run  print the sources it would upload (and what it holds back), change nothing

Sources (what may leave the vault for Google):
  - the idea note and its Dive-deeper reports, as text, each only if scripts/outbound_gate.py (public mode)
    finds nothing in it;
  - public web URLs cited in the idea, its reports and its Built-from notes. Notes under Mail/ or Clients/
    and Slack material are never read for URLs, and internal hosts (employer domains, Slack, Google Docs/Drive,
    meeting links) are dropped.
Audio lands in output/podcasts/ideas/<id>-indepth.m4a and -short.m4a; the idea note gets `podcast:` in its
frontmatter (generating → ready | failed) and a `## Podcasts` section. Started from the console's Ideas view.
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ideas  # noqa: E402

REPO = ideas.REPO
sys.path.insert(0, str(REPO / "scripts"))
import employer  # noqa: E402
import outbound_gate  # noqa: E402

OUT = REPO / "output" / "podcasts" / "ideas"
TITLE_PREFIX = "Idea · "   # daily_audio.py skips notebooks with this prefix: these are downloaded here
PRIVATE_PARTS = ("Mail/", "Clients/")
INTERNAL_HOSTS = ("slack.com", "mail.google.com", "docs.google.com", "drive.google.com", "calendar.google.com",
                  "meet.google.com", "zoom.us", "teams.microsoft.com", "localhost", "127.0.0.1", "notebooklm.google.com")
MAX_URLS = 20
WAIT = 2400        # seconds per audio: a long deep dive can take 20+ minutes
POLL = 20
URL_RX = re.compile(r"https?://[^\s)\]>\"'`|]+")


def nlm(*args, timeout=900):
    r = subprocess.run(["nlm", *args], capture_output=True, text=True, timeout=timeout)
    if r.returncode:
        raise RuntimeError(f"nlm {args[0]} {args[1] if len(args) > 1 else ''}: {(r.stderr or r.stdout).strip()[-400:]}")
    return r.stdout


def body(text):
    """Note text without frontmatter, wiki links flattened to their names."""
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    return re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", lambda m: m.group(2) or m.group(1).split("/")[-1], text)


def built_from(text):
    sec = re.search(r"^## Built from\n(.+?)(?:\n## |\Z)", text, re.M | re.S)
    out = []
    for link in re.findall(r"\[\[([^\]|#]+)", sec.group(1) if sec else ""):
        f = ideas.VAULT / f"{link}.md"
        f = f if f.is_file() else next(ideas.VAULT.rglob(f"{Path(link).name}.md"), None)
        if f:
            out.append(f)
    return out


def private(rel):
    return rel.startswith(PRIVATE_PARTS) or "slack" in rel.lower()


def public_urls(texts):
    own = {d.lower() for s in employer.packs() for d in employer.get("employer.domains", [], s)}
    seen = []
    for t in texts:
        for u in URL_RX.findall(t):
            u = u.rstrip(".,;:!?*_")
            host = (urlparse(u).hostname or "").lower()
            if not host or any(host == h or host.endswith("." + h) for h in (*INTERNAL_HOSTS, *own)):
                continue
            if u not in seen:
                seen.append(u)
    return seen[:MAX_URLS]


def gather(it):
    """→ (texts [(title, text)], urls, held_back [reason])."""
    note = (REPO / it["path"]).read_text()
    texts, held, url_from = [], [], [note]
    docs = [(f"Idea: {it['title']}", body(note))]
    for tid in it["tasks"]:
        status = ideas.load(REPO / "output" / "tasks" / tid / "STATUS.json", {})
        rep = REPO / str(status.get("report") or "-")
        if status.get("state") == "done" and rep.is_file():
            raw = rep.read_text(errors="ignore")
            url_from.append(raw)
            docs.append((f"Research: {status.get('summary', tid)[:80]}",
                         re.sub(r"<[^>]+>", " ", raw) if rep.suffix == ".html" else body(raw)))
    for title, text in docs:
        findings = outbound_gate.scan(text, public=True)
        if findings:
            held.append(f"{title}: not uploaded, the outbound gate flagged it ({'; '.join(findings[:3])})")
        else:
            texts.append((title, text[:400_000]))
    for f in built_from(note):
        rel = str(f.relative_to(ideas.VAULT))
        if private(rel):
            held.append(f"{rel}: private folder, its links stay in the vault")
        else:
            url_from.append(f.read_text(errors="ignore"))
    return texts, public_urls(url_from), held


def artifact(nb, aid):
    for a in json.loads(nlm("studio", "status", nb, "--json") or "[]"):
        if aid in (a.get("artifact_id"), a.get("id")):
            return str(a.get("status", "")).lower()
    return ""


def wait(nb, aid):
    deadline = time.monotonic() + WAIT
    while time.monotonic() < deadline:
        st = artifact(nb, aid)
        if st == "completed":
            return
        if st in ("failed", "error"):
            raise RuntimeError(f"NotebookLM reports audio {aid} {st}")
        time.sleep(POLL)
    raise RuntimeError(f"audio {aid} not ready after {WAIT // 60} min")


def create_audio(nb, length, focus):
    return json.loads(nlm("audio", "create", nb, "-f", "deep_dive", "-l", length, "--language", "en",
                          "--focus", focus, "-y", "--json"))["artifact_id"]


def main(iid, dry):
    it = next((i for i in ideas.ideas() if i["id"] == iid), None)
    if not it:
        sys.exit(f"no such idea: {iid}")
    texts, urls, held = gather(it)
    if dry:
        print(json.dumps({"texts": [t for t, _ in texts], "urls": urls, "held_back": held}, indent=2))
        return
    if not texts and not urls:
        raise RuntimeError("nothing public to upload: " + "; ".join(held))

    ideas.log(f"{iid}: notebook with {len(texts)} text + {len(urls)} url sources")
    nb = json.loads(nlm("notebook", "create", f"{TITLE_PREFIX}{it['title']}"[:100], "--json"))["notebook_id"]
    ideas.set_field(iid, "notebook", nb)
    added, failed = [], []
    for title, text in texts:
        nlm("source", "add", nb, "--text", text, "--title", title, "--wait", "--wait-timeout", "300")
        added.append(title)
    for u in urls:
        try:
            nlm("source", "add", nb, "--url", u, "--wait", "--wait-timeout", "300")
            added.append(u)
        except (RuntimeError, subprocess.TimeoutExpired) as e:
            failed.append(f"{u}: {str(e)[-120:]}")

    deep_focus = (f"An in-depth episode on: {it['title']}. Why it matters now: {it['value']} Cover the evidence, "
                  "the strongest counterarguments, and what it would take to act on it.")
    short_focus = (f"Keep the whole episode on one central idea: {it['title']}. {it['value']} Open with it, say why "
                   "it matters now, and end on the one action it implies.")
    deep = create_audio(nb, "long", deep_focus)
    try:
        short = create_audio(nb, "short", short_focus)
    except RuntimeError:   # NotebookLM may allow one generation at a time per notebook
        wait(nb, deep)
        short = create_audio(nb, "short", short_focus)

    OUT.mkdir(parents=True, exist_ok=True)
    files = []
    for label, aid in (("indepth", deep), ("short", short)):
        wait(nb, aid)
        dest = OUT / f"{iid}-{label}.m4a"
        nlm("download", "audio", nb, "--id", aid, "-o", str(dest), "--no-progress")
        files.append(dest)

    ideas.append(iid, "Podcasts", "\n".join([
        f"### {time.strftime('%Y-%m-%d %H:%M')}",
        f"- In depth: `{ideas.REL(files[0])}`",
        f"- Short, the central idea: `{ideas.REL(files[1])}`",
        f"- Notebook: https://notebooklm.google.com/notebook/{nb}",
        "- Sources uploaded: " + "; ".join(added),
        *([f"- Sources NotebookLM refused: {'; '.join(failed)}"] if failed else []),
        *([f"- Held back: {'; '.join(held)}"] if held else [])]))
    ideas.set_field(iid, "podcast", "ready")
    ideas.notify("Podcasts ready", it["title"])
    ideas.log(f"{iid}: ready")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    try:
        main(a[0], "--dry-run" in a)
    except Exception as e:  # the card must leave "generating" whatever broke
        ideas.log(f"{a[0]}: failed: {e}")
        if "--dry-run" not in a:
            ideas.set_field(a[0], "podcast", "failed")
            ideas.append(a[0], "Podcasts", f"- {time.strftime('%Y-%m-%d %H:%M')}: failed: {str(e)[:300]}")
        sys.exit(1)
