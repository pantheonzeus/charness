# /// script
# requires-python = ">=3.10"
# ///
"""Substack watch: mirror every issue of a Substack newsletter into the vault, brief on each new one.

  sync <pub> [--all]                         mirror issues not yet held (default: newest 25; --all walks the archive)
  run                                        daily pass over every publication: sync → briefing agent per new issue
  brief <pub> --since YYYY-MM-DD [--max N]   backfill: brief held issues on/after the date that have none (newest first, N=1)
  refresh <pub>                              after a parser fix: re-convert every held note's full text (briefings stay)
  check <ROOT>                              validate one briefing run
  status                                     JSON summary

Publications live in ../publications.json ({id, name, url, default_topic}). Any Substack works: they all serve
the same JSON API, /api/v1/archive (paged listing) and /api/v1/posts/<slug> (full body_html). The fetch is
plain HTTP, no LLM. Each issue becomes one vault note, cbrain/notes/Sources/<Name>/<YYYY-MM-DD>-<slug>.md:
frontmatter, an info callout, then `## Full text`. The fetcher never rewrites a note; the briefing agent
inserts its sections above `## Full text`, which must stay byte-identical (checked by hash).
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ME = Path(__file__).resolve()
SKILL = ME.parent.parent
REPO = SKILL.parents[3]
PUBS = SKILL / "publications.json"
VAULT = REPO / "cbrain"
SOURCES = VAULT / "notes" / "Sources"
BASE_FILE = VAULT / "Bases" / "Newsletters.base"
OUT = REPO / "output" / "substack"
LOCK = OUT / ".lock"
RUN_AGENT = REPO / "scripts" / "run_agent.sh"
CLI_ENV = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")}
REL = lambda p: str(p.relative_to(REPO))
TOOLS = ["Read", "Glob", "Grep", "Write", "Edit", "WebSearch", "WebFetch", "Bash(date:*)", "Bash(ls:*)",
         f"Bash(uv run {REL(ME)}:*)", f"Bash(uv run {ME}:*)"]
FULL = "## Full text"


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


def getjson(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (cbrain substack-watch)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def pubs():
    return {p["id"]: p for p in json.loads(PUBS.read_text())}


def folder(p):
    return SOURCES / re.sub(r"[^\w]+", "-", p["name"]).strip("-")


def state_path(p):
    return OUT / p["id"] / "state.json"


def sha(text):
    return hashlib.sha256(text.strip().encode()).hexdigest()


class Body(HTMLParser):
    """Substack body_html → Markdown. Headings drop to ###+ so they sit under `## Full text`."""
    HEAD = {"h1": "### ", "h2": "### ", "h3": "#### ", "h4": "##### ", "h5": "##### ", "h6": "##### "}
    VOID = {"img", "br", "hr", "input", "source", "wbr", "meta", "link"}
    SKIP_TAGS = {"svg", "button", "form", "script", "style"}
    SKIP_CLASS = ("subscription-widget", "button-wrapper", "image-link-expand")

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.skip, self.bufs, self.hrefs, self.lists = [], 0, [[]], [], []

    @property
    def buf(self):
        return self.bufs[-1]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.VOID:
            if not self.skip:
                self.void(tag, a)
            return
        self.stack.append(tag)
        if self.skip:
            return
        cls = a.get("class") or ""
        if tag in self.SKIP_TAGS or any(c in cls for c in self.SKIP_CLASS):
            self.skip = len(self.stack)
        elif tag == "p":
            self.buf.append(" " if self.lists else "\n\n")
        elif tag in self.HEAD:
            self.buf.append("\n\n" + self.HEAD[tag])
        elif tag == "blockquote":
            self.bufs.append([])
        elif tag in ("ul", "ol"):
            self.lists.append(tag)
        elif tag == "li":
            self.buf.append("\n" + "  " * (len(self.lists) - 1) + ("1. " if self.lists[-1:] == ["ol"] else "- "))
        elif tag == "a":
            image = "image-link" in cls   # wraps a picture: emit the image, not a link around it
            self.hrefs.append(None if image else a.get("href") or "")
            if not image:
                self.buf.append("[")
        elif tag in ("strong", "b"):
            self.buf.append("**")
        elif tag in ("em", "i"):
            self.buf.append("*")
        elif tag == "figcaption":
            self.buf.append("\n\n*")

    def void(self, tag, a):
        if tag == "br":
            self.buf.append("\n")
        elif tag == "hr":
            self.buf.append("\n\n---\n\n")
        elif tag == "img" and a.get("src"):
            self.buf.append(f"\n\n![{a.get('alt') or ''}]({a['src']})")

    def handle_endtag(self, tag):
        if tag in self.VOID or tag not in self.stack:
            return
        while True:   # pop to the matching tag, so an unclosed child can't derail the rest
            t = self.stack.pop()
            if self.skip:
                if len(self.stack) < self.skip:
                    self.skip = 0
            else:
                self.close(t)
            if t == tag:
                return

    def close(self, t):
        if t == "blockquote" and len(self.bufs) > 1:
            inner = "".join(self.bufs.pop()).strip()
            self.buf.append("\n\n" + "\n".join("> " + ln if ln.strip() else ">" for ln in inner.splitlines()))
        elif t in self.HEAD:   # a pull-quote follows its heading as bare text, not a <p>
            self.buf.append("\n\n")
        elif t in ("ul", "ol") and self.lists:
            self.lists.pop()
            self.buf.append("\n")
        elif t == "a":
            h = self.hrefs.pop() if self.hrefs else ""
            if h is not None:
                self.buf.append(f"]({h})" if h else "]")
        elif t in ("strong", "b"):
            self.buf.append("**")
        elif t in ("em", "i"):
            self.buf.append("*")
        elif t == "figcaption":
            self.buf.append("*")

    def handle_data(self, data):
        if not self.skip:
            self.buf.append(re.sub(r"\s+", " ", data))

    def text(self):
        t = "".join(self.bufs[0])
        t = re.sub(r"(?<!!)\[\s*\]\([^)]*\)", "", t)
        t = re.sub(r"\*\*[ \t]*\*\*", "", t)   # empty or back-to-back bold; never across a line break
        t = re.sub(r"[ \t]+\n", "\n", t)
        t = re.sub(r"(?m)^[ \t]+(?![-*] |\d+\. )", "", t)
        t = re.sub(r"(?m)^(\s*(?:-|\d+\.)) {2,}", r"\1 ", t)
        t = re.sub(r"(?m)^#(?!#{2,4} )", r"\\#", t)   # newsletter text never becomes a heading or tag
        t = re.sub(r"(?m)^```", r"\\`\\`\\`", t)
        return re.sub(r"\n{3,}", "\n\n", t).strip()


def to_markdown(body_html):
    b = Body()
    b.feed(body_html)
    return b.text()


def write_issue(p, slug):
    d = getjson(f"{p['url']}/api/v1/posts/{slug}")
    text = to_markdown(d.get("body_html") or "")
    if len(text) < 200:
        raise RuntimeError(f"body too short ({len(text)} chars)")
    date = d["post_date"][:10]
    url = d.get("canonical_url") or f"{p['url']}/p/{slug}"
    fm = {"type": "newsletter-issue", "provenance": "untrusted-ingest", "publication": f"[[{p['name']}]]", "title": d["title"],
          "subtitle": d.get("subtitle") or "", "date": date, "url": url,
          "authors": [b["name"] for b in d.get("publishedBylines") or []], "words": d.get("wordcount"),
          "status": "unread", "briefed": "", "topics": [], "tags": ["newsletter", p["id"]]}
    head = "".join(f"{k}: {v}\n" if k == "date" else f"{k}: {json.dumps(v, ensure_ascii=False)}\n" for k, v in fm.items())
    sub = f"\n> {fm['subtitle']}" if fm["subtitle"] else ""
    path = folder(p) / f"{date}-{slug[:90]}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{head}---\n\n# {d['title']}\n\n> [!info] {p['name']} · {date} · [Read on Substack]({url}){sub}\n\n"
                    f"{FULL}\n\n{text}\n")
    return path, sha(text)


def ensure_hub(p):
    """Write the publication's hub note and the shared Newsletters base once; never overwrite either."""
    hub = folder(p) / f"{p['name']}.md"
    if not hub.exists():
        hub.parent.mkdir(parents=True, exist_ok=True)
        hub.write_text(
            f"---\ntype: moc\nsource_url: {json.dumps(p['url'])}\ntags: [moc, newsletter, {p['id']}]\n"
            f"related:\n  - \"[[Home]]\"\n  - \"[[{p['default_topic']}]]\"\n---\n\n# {p['name']}\n\n"
            f"Every issue of [{p['name']}]({p['url']}), mirrored by the `substack-watch` skill. One note per issue: "
            f"the researched briefing on top (once `briefed` is set), the full text below. Set `status: read` when "
            f"you have read one.\n\n> [!warning] Evidence status\n> The full text is the newsletter's own reporting, "
            f"unverified by this vault. Briefing sections tag each claim verified / likely / unverified with a "
            f"source; quote only those.\n\n## Issues\n![[Newsletters.base]]\n")
    if not BASE_FILE.exists():
        cols = "    order:\n      - date\n      - title\n      - publication\n      - briefed\n      - status\n" \
               "    sort:\n      - property: date\n        direction: DESC\n"
        BASE_FILE.write_text(
            "# Newsletter issues (type: newsletter-issue), one note per issue, written by the `substack-watch` skill.\n"
            "# status is yours: unread → read. `briefed` is set when the researched briefing lands on top of the note.\n"
            "filters:\n  and:\n    - type == \"newsletter-issue\"\nviews:\n"
            "  - type: table\n    name: Unread (newest first)\n    filters:\n      and:\n        - status != \"read\"\n" + cols +
            "  - type: table\n    name: All issues\n" + cols)


def sync(p, all_pages):
    st = load(state_path(p), {"seen": {}, "runs": []})
    ensure_hub(p)
    new, errors, paid, offset = [], [], 0, 0
    while True:
        page = getjson(f"{p['url']}/api/v1/archive?sort=new&limit=25&offset={offset}")
        if not page:
            break
        for post in page:
            slug = post["slug"]
            if slug in st["seen"] or post.get("type") != "newsletter":
                continue
            if post.get("audience") != "everyone":   # paid: the API serves only a preview
                paid += 1
                continue
            try:
                path, digest = write_issue(p, slug)
                st["seen"][slug] = {"path": REL(path), "sha": digest}
                new.append(REL(path))
            except Exception as e:   # one bad post must not stop the sweep; it is retried next sync
                errors.append(f"{slug}: {type(e).__name__}: {e}")
            time.sleep(0.5)
        if not all_pages:   # daily: the newest 25 cover any realistic gap
            break
        offset += len(page)
        time.sleep(0.5)
    save(state_path(p), st)
    log(f"{p['id']} sync: {len(new)} new, {len(errors)} error(s), {paid} paid skipped, {len(st['seen'])} held")
    for e in errors:
        log("  " + e)
    return sorted(new), errors


def refresh(p):
    """After a `Body` fix: re-convert the full text of every held note in place. Briefings above it stay."""
    st = load(state_path(p), {"seen": {}, "runs": []})
    done, errors = 0, []
    for slug, s in st["seen"].items():
        note = REPO / s["path"]
        head, sep, _ = note.read_text().partition(f"\n{FULL}\n") if note.exists() else ("", "", "")
        if not sep:
            errors.append(f"{slug}: note or '{FULL}' missing")
            continue
        try:
            text = to_markdown(getjson(f"{p['url']}/api/v1/posts/{slug}").get("body_html") or "")
            if len(text) < 200:
                raise RuntimeError(f"body too short ({len(text)} chars)")
        except Exception as e:
            errors.append(f"{slug}: {type(e).__name__}: {e}")
            continue
        note.write_text(f"{head}{sep}\n{text}\n")
        s["sha"] = sha(text)
        done += 1
        time.sleep(0.5)
    save(state_path(p), st)
    log(f"{p['id']} refresh: {done} re-converted, {len(errors)} error(s)")
    for e in errors:
        log("  " + e)


def frontmatter(text):
    return text[4:text.find("\n---\n", 4)] if text.startswith("---\n") else ""


def briefed(path):
    return bool(re.search(r"^briefed:\s*\"?\d{4}-\d{2}-\d{2}", frontmatter(path.read_text()), re.M))


def check(root):
    task = load(Path(root) / "TASK.json", None)
    if not task:
        return [f"no TASK.json in {root}"]
    note = REPO / task["issue"]
    if not note.is_file():
        return [f"issue note missing: {task['issue']}"]
    text = note.read_text()
    fm, errs = frontmatter(text), []
    if not briefed(note):
        errs.append("frontmatter `briefed:` is not set to a date")
    head, sep, full = text.partition(f"\n{FULL}\n")
    if not sep:
        return errs + [f"'{FULL}' section is gone"]
    if sha(full) != task["sha"]:
        errs.append(f"the text under '{FULL}' changed; it must stay verbatim")
    for need in ("## Headline", "## What the research adds", "## So what for you", "## Sources"):
        if need not in head:
            errs.append(f"briefing lacks '{need}' above '{FULL}'")
    block = re.search(r"^topics:(.*(?:\n[ \t]+-.*)*)", fm, re.M)
    topics = re.findall(r"\[\[([^\]|#]+)", block.group(1)) if block else []
    if not topics:
        errs.append("frontmatter `topics:` links no topic note")
    for t in topics:
        hits = [f for f in VAULT.rglob(f"{t}.md") if f != note]
        if not hits:
            errs.append(f"topic [[{t}]] has no note in the vault")
        elif not any(f"[[{note.stem}" in f.read_text() for f in hits):
            errs.append(f"[[{t}]] does not link back to [[{note.stem}]]")
    return errs


def notify(title, message):
    subprocess.run(["osascript", "-e", f'display notification {json.dumps(message)} with title {json.dumps(title)}'],
                   capture_output=True)


def brief_one(p, issue, announce):
    s = next(v for v in load(state_path(p), {"seen": {}})["seen"].values() if v["path"] == issue)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    root = REPO / "output" / ".runs" / f"{stamp}-substack-{p['id']}"
    root.mkdir(parents=True)
    save(root / "TASK.json", {"publication": p["name"], "issue": issue, "sha": s["sha"], "max_web_calls": 10,
                              "signals_heading": f"## {p['name']} signals", "default_topic": p["default_topic"]})
    (root / "RESPONSE.md").write_text(
        f"# substack-watch {stamp} — {p['name']}: {Path(issue).stem}\n- [ ] issue read in full\n"
        "- [ ] claims researched (primary sources first)\n- [ ] briefing written above ## Full text, `briefed:` set\n"
        "- [ ] topic notes linked both ways (`topics:` + signals lines)\n- [ ] substack_watch.py check prints OK\n")
    prompt = (f"Read and follow resources/skills/research/substack-watch/SKILL.md (a repo skill: open it with Read, "
              f"not the Skill tool) for the task packet {REL(root)}/TASK.json. Your STATE_ROOT is {REL(root)}/. "
              f"Finish with `uv run {REL(ME)} check {REL(root)}` printing OK.")
    subprocess.run(["bash", str(RUN_AGENT), "substack-watch", str(root / "RESPONSE.md"), prompt,
                    "--permission-mode", "acceptEdits", "--allowedTools", *TOOLS],
                   cwd=REPO, env=CLI_ENV, stdin=subprocess.DEVNULL)
    errs = check(root)
    log(f"briefing {Path(issue).stem}: {'OK' if not errs else 'FAILED: ' + '; '.join(errs[:3])}")
    if announce and not errs:
        notify(p["name"], f"New issue briefed: {Path(issue).stem[11:]}")
    return {"issue": issue, "run": REL(root), "ok": not errs, "errors": errs[:5]}


def alive():
    try:
        os.kill(int(LOCK.read_text()), 0)
        return True
    except (OSError, ValueError):
        return False


def locked(fn):
    if alive():
        return log("another substack-watch pass is still running; skipping")
    OUT.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(str(os.getpid()))
    try:
        fn()
    finally:
        LOCK.unlink(missing_ok=True)


def run():
    for p in pubs().values():
        try:
            new, errors = sync(p, False)
        except Exception as e:   # one unreachable publication must not stop the others
            new, errors = [], [f"listing: {type(e).__name__}: {e}"]
            log(f"{p['id']} sync failed: {errors[0]}")
        rec = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "new": len(new), "fetch_errors": errors[:5],
               "briefs": [brief_one(p, issue, True) for issue in new]}
        st = load(state_path(p), {"seen": {}, "runs": []})
        st["runs"] = (st.get("runs", []) + [rec])[-200:]
        save(state_path(p), st)


def backfill(pid, since, n):
    p = pubs()[pid]
    held = [v["path"] for v in load(state_path(p), {"seen": {}})["seen"].values()]
    todo = sorted((i for i in held if Path(i).name[:10] >= since and (REPO / i).exists() and not briefed(REPO / i)),
                  reverse=True)
    for issue in todo[:n]:
        brief_one(p, issue, False)
    log(f"{pid} backfill: {min(n, len(todo))} briefed this pass, {max(0, len(todo) - n)} still unbriefed since {since}")


def status():
    out = {"running": alive()}
    for p in pubs().values():
        st = load(state_path(p), {"seen": {}, "runs": []})
        paths = [REPO / v["path"] for v in st["seen"].values()]
        out[p["id"]] = {"held": len(paths), "briefed": sum(1 for f in paths if f.exists() and briefed(f)),
                        "last_run": (st["runs"] or [None])[-1]}
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["sync"] and len(a) >= 2:
        sync(pubs()[a[1]], "--all" in a)
    elif a[:1] == ["refresh"] and len(a) == 2:
        locked(lambda: refresh(pubs()[a[1]]))
    elif a[:1] == ["run"]:
        locked(run)
    elif a[:1] == ["brief"] and len(a) >= 4 and a[2] == "--since":
        n = int(a[a.index("--max") + 1]) if "--max" in a else 1
        locked(lambda: backfill(a[1], a[3], n))
    elif a[:1] == ["check"] and len(a) == 2:
        e = check(a[1])
        print("OK" if not e else "\n".join(e))
        sys.exit(1 if e else 0)
    elif a[:1] == ["status"]:
        print(json.dumps(status(), indent=1))
    else:
        sys.exit(__doc__)
