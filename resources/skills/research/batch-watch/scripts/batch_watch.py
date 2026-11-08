# /// script
# requires-python = ">=3.10"
# ///
"""The Batch watch: mirror every issue and article of deeplearning.ai's The Batch into the vault.

  sync [--all]     mirror what is not yet held (default: page 1 of each listing; --all walks every page)
  run              daily pass: sync (locked, logged, vault-history snapshot)
  page <slug>      print one page's converted Markdown (parser debugging; writes nothing)
  status           JSON summary

Listings: the main /the-batch archive (weekly issues, full newsletter) and the eight category tags
(letters, data-points, research, business, science, culture, hardware, ai-careers). The fetch is plain
HTTP, no LLM: each listing embeds card JSON (title, href, date) in its Next.js payload, and each page's
body is its `prose` div, converted to Markdown. One vault note per page:
  cbrain/notes/Sources/The-Batch/issues/<YYYY-MM-DD>-<slug>.md     type: newsletter-issue
  cbrain/notes/Sources/The-Batch/articles/<YYYY-MM-DD>-<slug>.md   type: batch-article
An article can sit under several tags; `sections:` lists them. The fetcher never rewrites a note's
body. The only later edit it makes is widening the one-line `sections:` when a held article shows up
under another tag.
"""
import hashlib
import html
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
BASE = "https://www.deeplearning.ai"
SECTIONS = ["letters", "data-points", "research", "business", "science", "culture", "hardware", "ai-careers"]
LISTINGS = [("issues", "/the-batch")] + [(s, f"/the-batch/tag/{s}") for s in SECTIONS]
VAULT = REPO / "cbrain"
FOLDER = VAULT / "notes" / "Sources" / "The-Batch"
HUB = FOLDER / "The Batch.md"
BASE_FILE = VAULT / "Bases" / "The-Batch.base"
OUT = REPO / "output" / "batch-watch"
STATE = OUT / "state.json"
LOCK = OUT / ".lock"
HISTORY = REPO / "scripts" / "vault_history.sh"
FULL = "## Full text"
REL = lambda p: str(p.relative_to(REPO))


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


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (cbrain batch-watch)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def cards(path, page):
    """Cards on one listing page → [(slug, title)], plus totalPages."""
    s = get(BASE + path + (f"/page/{page}" if page > 1 else "")).replace('\\"', '"')
    out = []
    # one card = {"title":…,"image":…,"href":…,"date":…}; never let a match run into the next card's title
    for m in re.finditer(r'\{"title":"(.*?)","image":(?:(?!\{"title":").)*?"href":"/the-batch/([^"/]+)/?","date":"', s):
        title, slug = m.groups()
        title = title.replace('\\\\"', '\\"')   # a quote inside a title arrives double-escaped
        if slug not in ("about", "search") and not slug.startswith("tag"):
            try:
                out.append((slug, html.unescape(json.loads(f'"{title}"'))))
            except ValueError:
                out.append((slug, title))
    total = re.search(r'"totalPages":(\d+)', s)
    return out, int(total.group(1)) if total else 1


class Body(HTMLParser):
    """The first div whose class contains `prose` → Markdown. Headings drop to ###+ so they sit under `## Full text`."""
    HEAD = {"h1": "### ", "h2": "### ", "h3": "#### ", "h4": "##### ", "h5": "##### ", "h6": "##### "}
    VOID = {"img", "br", "hr", "input", "source", "wbr", "meta", "link"}
    SKIP_TAGS = {"svg", "button", "form", "script", "style", "noscript"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.skip, self.inside, self.done = [], 0, 0, False
        self.bufs, self.hrefs, self.lists = [[]], [], []

    @property
    def buf(self):
        return self.bufs[-1]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if self.done or (not self.inside and not (tag == "div" and "prose" in (a.get("class") or "").split())):
            return
        if tag in self.VOID:
            if not self.skip:
                self.void(tag, a)
            return
        self.stack.append(tag)
        if not self.inside:
            self.inside = len(self.stack)
            return
        if self.skip:
            return
        if tag in self.SKIP_TAGS or "elevenlabs" in (a.get("id") or "") + (a.get("class") or ""):
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
            h = a.get("href") or ""
            hidden = h.startswith("/cdn-cgi/l/email-protection")   # Cloudflare-masked address: plain text, no link
            self.hrefs.append(None if hidden else h)
            if not hidden:
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
        elif tag == "img" and (a.get("src") or "").startswith("http"):
            self.buf.append(f"\n\n![{(a.get('alt') or '').replace(']', '')}]({a['src']})\n\n")

    def handle_endtag(self, tag):
        if not self.inside or self.done or tag in self.VOID or tag not in self.stack:
            return
        while True:   # pop to the matching tag, so an unclosed child can't derail the rest
            t = self.stack.pop()
            if len(self.stack) < self.inside:
                self.done = True
                return
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
        elif t in self.HEAD:
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
        if self.inside and not self.skip and not self.done:
            self.buf.append(re.sub(r"\s+", " ", data))

    def text(self):
        t = "".join(self.bufs[0])
        t = re.sub(r"(?<!!)\[\s*\]\([^)]*\)", "", t)
        t = re.sub(r"\*\*[ \t]*\*\*", "", t)   # empty or back-to-back bold; never across a line break
        t = re.sub(r"[ \t]+\n", "\n", t)
        t = re.sub(r"(?m)^[ \t]+(?![-*] |\d+\. )", "", t)
        t = re.sub(r"(?m)^(\s*(?:-|\d+\.)) {2,}", r"\1 ", t)
        t = re.sub(r"(?m)^#(?!#{2,4} )", r"\\#", t)   # page text never becomes a heading or tag
        t = re.sub(r"(?m)^```", r"\\`\\`\\`", t)
        return re.sub(r"\n{3,}", "\n\n", t).strip()


def meta(s, prop):
    m = re.search(rf'<meta[^>]+(?:property|name)="{prop}"[^>]+content="([^"]*)"', s)
    return html.unescape(m.group(1)).strip() if m else ""


def fetch(slug):
    """One page → (title, subtitle, date, page tags, Markdown body)."""
    s = get(f"{BASE}/the-batch/{slug}")
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S)
    sub = re.search(r"<span[^>]*>(.*?)</span>", h1.group(1), re.S) if h1 else None
    strip = lambda x: html.unescape(re.sub(r"<[^>]+>", "", x)).replace("\xa0", " ").strip()
    title = strip(h1.group(1)[:sub.start()] if sub else h1.group(1)) if h1 else ""
    date = (meta(s, "article:published_time") or "")[:10]
    tags = sorted(set(re.findall(r'href="/the-batch/tag/([a-z0-9-]+)/?"', s)) - set(SECTIONS))
    b = Body()
    b.feed(s)
    return title or meta(s, "og:title"), strip(sub.group(1)) if sub else "", date, tags, b.text()


def sha(text):
    return hashlib.sha256(text.strip().encode()).hexdigest()


def write_note(slug, kind, sections, title, issue_of, status):
    t, sub, date, tags, text = fetch(slug)
    if len(text) < 200:
        raise RuntimeError(f"body too short ({len(text)} chars)")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise RuntimeError(f"no publish date on the page ({date!r})")
    issue = kind == "issues"
    url = f"{BASE}/the-batch/{slug}/"
    # an issue's h1 is just "News"; its listing card carries the real title
    fm = {"type": "newsletter-issue" if issue else "batch-article", "provenance": "untrusted-ingest", "publication": "[[The Batch]]",
          "title": title if issue else t or title, "subtitle": sub, "date": date, "url": url}
    if not issue:
        fm["sections"] = sections
        fm["issue"] = f"[[{issue_of[date]}]]" if date in issue_of else ""
    fm.update({"words": len(text.split()), "status": status, "tags": ["newsletter", "the-batch"],
               "batch_tags": [x for x in tags if not re.fullmatch(r"[a-z]{3}-\d{1,2}-\d{4}", x)]})
    head = "".join(f"{k}: {v}\n" if k == "date" else f"{k}: {json.dumps(v, ensure_ascii=False)}\n" for k, v in fm.items())
    where = f"{' · '.join(sections)} · " if sections else ""
    up = f" · issue {fm['issue']}" if fm.get("issue") else ""
    path = FOLDER / ("issues" if issue else "articles") / f"{date}-{slug[:90]}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{head}---\n\n# {fm['title']}\n\n> [!info] The Batch · {where}{date} · [Read on deeplearning.ai]({url}){up}"
                    + (f"\n> {sub}" if sub else "") + f"\n\n{FULL}\n\n{text}\n")
    return path, date, sha(text)


def widen(note, sections):
    """A held article showed up under another tag: rewrite only its one-line `sections:`."""
    if not note.exists():
        return
    text = note.read_text()
    new = re.sub(r"^sections: .*$", "sections: " + json.dumps(sections), text, count=1, flags=re.M)
    if new != text:
        note.write_text(new)


def ensure_hub():
    """Write the hub note and the base once; never overwrite either."""
    if not HUB.exists():
        HUB.parent.mkdir(parents=True, exist_ok=True)
        HUB.write_text(
            "---\ntype: moc\nsource_url: \"https://www.deeplearning.ai/the-batch/\"\ntags: [moc, newsletter, the-batch]\n"
            "related:\n  - \"[[Home]]\"\n  - \"[[Andrew Ng - Thinking]]\"\n---\n\n# The Batch\n\n"
            "Every weekly issue and every article of [The Batch](https://www.deeplearning.ai/the-batch/) "
            "(DeepLearning.AI), mirrored by the `batch-watch` skill: `issues/` holds each newsletter as sent, "
            "`articles/` each story on its own page, with `sections:` naming the categories it is filed under "
            "(letters, data-points, research, business, science, culture, hardware, ai-careers). Andrew Ng's letters "
            "also get a researched briefing from `ng-letters-watch`; see [[Andrew Ng - Thinking]].\n\n"
            "Set `status: read` when you have read one. The back catalogue came in as `status: backlog`, so "
            "*New* shows only what arrived since.\n\n> [!warning] Evidence status\n> The full text is The Batch's own "
            "reporting, unverified by this vault. Verify at the primary source before quoting a claim as fact.\n\n"
            "## Notes\n![[The-Batch.base]]\n")
    if not BASE_FILE.exists():
        cols = "    order:\n      - date\n      - title\n      - sections\n      - status\n" \
               "    sort:\n      - property: date\n        direction: DESC\n"
        BASE_FILE.write_text(
            "# The Batch (deeplearning.ai), one note per issue and per article, written by the `batch-watch` skill.\n"
            "# status is yours: unread → read. The back catalogue is `backlog`.\n"
            "filters:\n  and:\n    - file.inFolder(\"notes/Sources/The-Batch\")\n    - type != \"moc\"\nviews:\n"
            "  - type: table\n    name: New (unread)\n    filters:\n      and:\n        - status == \"unread\"\n" + cols +
            "  - type: table\n    name: Articles\n    filters:\n      and:\n        - type == \"batch-article\"\n" + cols +
            "  - type: table\n    name: Issues\n    filters:\n      and:\n        - type == \"newsletter-issue\"\n" + cols)


def sync(all_pages):
    st = load(STATE, {"seen": {}, "runs": []})
    ensure_hub()
    status = "backlog" if all_pages or not st["seen"] else "unread"
    found = {}   # slug → {kind, sections, title}, merged across listings
    listing_errors = []
    for kind, path in LISTINGS:
        page, total = 1, 1
        while page <= total:
            try:
                got, total = cards(path, page)
            except Exception as e:   # one bad listing page must not stop the sweep
                listing_errors.append(f"{path} p{page}: {type(e).__name__}: {e}")
                got = []
            for slug, title in got:
                k = "issues" if kind == "issues" and slug.startswith("issue-") else "articles"   # also issue-119-2
                f = found.setdefault(slug, {"kind": k, "sections": [], "title": title})
                if kind != "issues" and kind not in f["sections"]:
                    f["sections"].append(kind)
            if not all_pages:   # daily: page 1 holds the last 15 of each listing
                break
            page += 1
            time.sleep(0.3)
    issue_of = {v["date"]: Path(v["path"]).stem for v in st["seen"].values() if v["kind"] == "issues"}
    new, errors, widened = [], [], 0
    for slug, f in sorted(found.items(), key=lambda kv: kv[1]["kind"] != "issues"):   # issues first, so articles link up
        held = st["seen"].get(slug)
        if held:
            merged = sorted(set(held.get("sections", [])) | set(f["sections"]), key=SECTIONS.index)
            if merged != held.get("sections", []):
                held["sections"] = merged
                widen(REPO / held["path"], merged)
                widened += 1
            continue
        try:
            p, date, digest = write_note(slug, f["kind"], sorted(f["sections"], key=SECTIONS.index), f["title"], issue_of, status)
            st["seen"][slug] = {"path": REL(p), "kind": f["kind"], "date": date, "sections": f["sections"], "sha": digest}
            if f["kind"] == "issues":
                issue_of[date] = p.stem
            new.append(REL(p))
        except Exception as e:   # one bad page must not stop the sweep; it is retried next sync
            errors.append(f"{slug}: {type(e).__name__}: {e}")
        if len(new) % 50 == 0:
            save(STATE, st)
        time.sleep(0.4)
    save(STATE, st)
    errors = listing_errors + errors
    log(f"sync: {len(new)} new, {widened} widened, {len(errors)} error(s), {len(st['seen'])} held")
    for e in errors:
        log("  " + e)
    return sorted(new), errors


def alive():
    try:
        os.kill(int(LOCK.read_text()), 0)
        return True
    except (OSError, ValueError):
        return False


def locked(fn):
    if alive():
        return log("another batch-watch pass is still running; skipping")
    OUT.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(str(os.getpid()))
    try:
        fn()
    finally:
        LOCK.unlink(missing_ok=True)


def run(all_pages=False):
    new, errors = sync(all_pages)
    if new:
        subprocess.run(["bash", str(HISTORY), "snapshot", "batch-watch", f"batch-watch: {len(new)} new note(s)",
                        "notes/Sources/The-Batch", "Bases/The-Batch.base"], cwd=REPO, capture_output=True)
    st = load(STATE, {"seen": {}, "runs": []})
    st["runs"] = (st["runs"] + [{"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "new": len(new), "errors": errors[:5]}])[-200:]
    save(STATE, st)


def status():
    st = load(STATE, {"seen": {}, "runs": []})
    v = st["seen"].values()
    per = {s: sum(1 for x in v if s in x.get("sections", [])) for s in SECTIONS}
    return {"running": alive(), "issues": sum(1 for x in v if x["kind"] == "issues"),
            "articles": sum(1 for x in v if x["kind"] == "articles"), "per_section": per,
            "last_run": (st["runs"] or [None])[-1]}


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["sync"]:
        locked(lambda: run("--all" in a))
    elif a[:1] == ["run"]:
        locked(run)
    elif a[:1] == ["page"] and len(a) == 2:
        t, sub, date, tags, text = fetch(a[1])
        print(json.dumps({"title": t, "subtitle": sub, "date": date, "tags": tags, "words": len(text.split())}), text, sep="\n\n")
    elif a[:1] == ["status"]:
        print(json.dumps(status(), indent=1))
    else:
        sys.exit(__doc__)
