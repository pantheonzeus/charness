# /// script
# requires-python = ">=3.10"
# ///
"""Andrew Ng letters watch: mirror every letter from The Batch's `letters` tag, brief on each new one.

  sync [--all]     fetch letters not yet on disk (default: listing page 1 only; --all walks every page)
  run              daily pass: sync → (if new letters) briefing agent → check → render + index
  check <ROOT>     validate the briefing agent's files for one run
  status           JSON summary

The fetch is plain HTTP, no LLM: the tag listing embeds card JSON (title, href, date, excerpt),
and each letter's body is the page's `prose` div, converted to Markdown. Letters land in
output/ng-letters/letters/<YYYY-MM-DD>-<slug>.md and are never rewritten.
"""
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
REPO = SKILL.parents[3]
BASE = "https://www.deeplearning.ai"
TAG = BASE + "/the-batch/tag/letters"
OUT = REPO / "output" / "ng-letters"
LETTERS, BRIEFINGS = OUT / "letters", OUT / "briefings"
STATE = OUT / "state.json"
LOCK = OUT / ".lock"
RUN_AGENT = REPO / "scripts" / "run_agent.sh"
PAGE = REPO / "resources/skills/workflow-ops/reading-pages/scripts/page.py"
INDEXER = REPO / "resources/skills/vault-hygiene/deliverable-index/scripts/index_deliverables.py"
CLI_ENV = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")}
REL = lambda p: str(p.relative_to(REPO))
TOOLS = ["Read", "Glob", "Grep", "Write", "Edit", "WebSearch", "WebFetch", "Bash(date:*)", "Bash(ls:*)",
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


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (cbrain ng-letters-watch)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def cards(page):
    """Cards on one listing page → [{title, slug, date, excerpt}], plus totalPages."""
    s = get(TAG + (f"/page/{page}" if page > 1 else ""))
    s = s.replace('\\"', '"')   # card JSON sits escaped inside a Next.js flight string
    out = []
    for m in re.finditer(r'"title":"((?:[^"\\]|\\.)*)","image":.*?"excerpt":"((?:[^"\\]|\\.)*)","href":"/the-batch/([^"/]+)/?","date":"([^"]+)"', s):
        title, excerpt, slug, date = m.groups()
        try:
            iso = datetime.strptime(date, "%B %d, %Y").strftime("%Y-%m-%d")
        except ValueError:
            continue
        dec = lambda t: html.unescape(json.loads(f'"{t}"')) if t else ""
        out.append({"title": dec(title), "slug": slug, "date": iso, "excerpt": dec(excerpt)})
    total = re.search(r'"totalPages":(\d+)', s)
    return out, int(total.group(1)) if total else 1


class Prose(HTMLParser):
    """The letter body: the first div whose class contains `prose`, as light Markdown."""
    BLOCK = {"p": "\n\n", "h1": "\n\n# ", "h2": "\n\n## ", "h3": "\n\n### ", "h4": "\n\n#### ", "blockquote": "\n\n> ",
             "figcaption": "\n\n*"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth, self.skip, self.buf, self.href, self.lists = 0, 0, [], None, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if not self.depth:
            if tag == "div" and "prose" in (a.get("class") or "").split():
                self.depth = 1
            return
        if tag == "div":
            self.depth += 1
            if "elevenlabs" in (a.get("id") or ""):
                self.skip = self.depth
        if self.skip:
            return
        if tag in self.BLOCK:
            self.buf.append(self.BLOCK[tag])
        elif tag in ("ul", "ol"):
            self.lists.append(tag)
        elif tag == "li":
            self.buf.append("\n" + "  " * (len(self.lists) - 1) + ("1. " if self.lists[-1:] == ["ol"] else "- "))
        elif tag == "a":
            self.href = a.get("href")
            self.buf.append("[")
        elif tag in ("strong", "b"):
            self.buf.append("**")
        elif tag in ("em", "i"):
            self.buf.append("*")
        elif tag == "br":
            self.buf.append("\n")

    def handle_endtag(self, tag):
        if not self.depth:
            return
        if tag == "div":
            if self.skip == self.depth:
                self.skip = 0
            self.depth -= 1
            return
        if self.skip:
            return
        if tag in ("ul", "ol") and self.lists:
            self.lists.pop()
            self.buf.append("\n")
        elif tag == "a":
            self.buf.append(f"]({self.href})" if self.href else "]")
            self.href = None
        elif tag in ("strong", "b"):
            self.buf.append("**")
        elif tag in ("em", "i"):
            self.buf.append("*")
        elif tag == "figcaption":
            self.buf.append("*")

    def handle_data(self, data):
        if self.depth and not self.skip:
            self.buf.append(re.sub(r"\s+", " ", data))

    def text(self):
        t = "".join(self.buf)
        t = re.sub(r"\[\s*\]\([^)]*\)", "", t)
        t = re.sub(r"[ \t]+\n", "\n", t)
        return re.sub(r"\n{3,}", "\n\n", t).strip()


def body(slug):
    p = Prose()
    p.feed(get(f"{BASE}/the-batch/{slug}"))
    return p.text()


def write_letter(c):
    path = LETTERS / f"{c['date']}-{c['slug'][:90]}.md"
    text = body(c["slug"])
    if len(text) < 200:
        raise RuntimeError(f"body too short ({len(text)} chars)")
    fm = {"provenance": "untrusted-ingest", "title": c["title"], "date": c["date"], "url": f"{BASE}/the-batch/{c['slug']}", "author": "Andrew Ng",
          "source": "The Batch — letters", "excerpt": c["excerpt"]}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + "".join(f"{k}: {json.dumps(v, ensure_ascii=False)}\n" for k, v in fm.items()) + "---\n\n" + text + "\n")
    return path


def sync(all_pages):
    state = load(STATE, {"seen": {}, "runs": []})
    new, errors, page, total = [], [], 1, 1
    while page <= total:
        got, total = cards(page)
        fresh = [c for c in got if c["slug"] not in state["seen"]]
        for c in fresh:
            try:
                p = write_letter(c)
                state["seen"][c["slug"]] = REL(p)
                new.append(REL(p))
            except Exception as e:   # one bad page must not stop the sweep; it is retried next sync
                errors.append(f"{c['slug']}: {type(e).__name__}: {e}")
            time.sleep(0.5)
        if not all_pages:   # daily: page 1 holds the last ~15 letters
            break
        page += 1
        time.sleep(0.5)
    save(STATE, state)
    log(f"sync: {len(new)} new letter(s), {len(errors)} error(s), {len(state['seen'])} held")
    for e in errors:
        log("  " + e)
    return sorted(new), errors


def check(root):
    task = load(Path(root) / "TASK.json", None)
    if not task:
        return [f"no TASK.json in {root}"]
    errs = []
    brief = REPO / task["briefing"]
    if not brief.is_file():
        return [f"no briefing at {task['briefing']}"]
    text = brief.read_text()
    if not re.search(r"^template:\s*briefing\s*$", text[:600], re.M):
        errs.append("briefing frontmatter needs template: briefing")
    for need in ("## Headline", "## Sources"):
        if need not in text:
            errs.append(f"briefing lacks a '{need}' section")
    r = subprocess.run(["uv", "run", "-q", str(PAGE), "check", str(brief)], capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0:
        errs.append("page.py check failed: " + (r.stdout + r.stderr).strip()[-300:])
    ledger = REPO / "cbrain" / "projects" / "Andrew Ng - Letters Ledger.md"
    held = ledger.read_text() if ledger.exists() else ""
    for letter in task["letters"]:
        if f"`{Path(letter).stem}`" not in held:
            errs.append(f"{Path(letter).name} not logged in Andrew Ng - Letters Ledger")
    return errs


def notify(title, message):
    subprocess.run(["osascript", "-e", f'display notification {json.dumps(message)} with title {json.dumps(title)}'],
                   capture_output=True)


def alive():
    try:
        os.kill(int(LOCK.read_text()), 0)
        return True
    except (OSError, ValueError):
        return False


def run():
    if alive():
        return log("previous run still alive; skipping")
    OUT.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(str(os.getpid()))
    try:
        new, errors = sync(False)
        rec = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "new": len(new), "fetch_errors": errors[:5]}
        if new:
            stamp = time.strftime("%Y%m%d-%H%M%S")
            root = REPO / "output" / ".runs" / f"{stamp}-ng-letters"
            root.mkdir(parents=True)
            brief = BRIEFINGS / f"{Path(new[-1]).stem}-briefing.md"
            save(root / "TASK.json", {"letters": new, "briefing": REL(brief), "max_web_calls": 12})
            (root / "RESPONSE.md").write_text(f"# ng-letters {stamp}\n- [ ] letter(s) read in full\n"
                "- [ ] claims researched (primary sources first)\n- [ ] briefing written + page.py check OK\n"
                "- [ ] thinking anchor updated (ledger line + any shifted thesis)\n- [ ] ng_letters.py check prints OK\n")
            prompt = (f"Read and follow resources/skills/research/ng-letters-watch/SKILL.md (a repo skill: open it with Read, "
                      f"not the Skill tool) for the task packet {REL(root)}/TASK.json. Your STATE_ROOT is {REL(root)}/. "
                      f"Finish with `uv run {REL(Path(__file__))} check {REL(root)}` printing OK.")
            subprocess.run(["bash", str(RUN_AGENT), "ng-letters", str(root / "RESPONSE.md"), prompt,
                            "--permission-mode", "acceptEdits", "--allowedTools", *TOOLS],
                           cwd=REPO, env=CLI_ENV, stdin=subprocess.DEVNULL)
            errs = check(root)
            rec.update(ok=not errs, errors=errs[:5], briefing=REL(brief))
            if brief.exists():
                subprocess.run(["uv", "run", "-q", str(PAGE), "render", str(brief)], cwd=REPO, capture_output=True)
                subprocess.run([sys.executable, str(INDEXER)], cwd=REPO, capture_output=True)
                notify("Andrew Ng letter", f"New briefing: {Path(new[-1]).stem[11:]}")
            log(f"briefing {'OK' if not errs else 'FAILED: ' + '; '.join(errs[:3])}")
        state = load(STATE, {"seen": {}, "runs": []})
        state["runs"] = (state["runs"] + [rec])[-200:]
        save(STATE, state)
    finally:
        LOCK.unlink(missing_ok=True)


def status():
    state = load(STATE, {"seen": {}, "runs": []})
    return {"running": alive(), "letters": len(state["seen"]), "last_run": (state["runs"] or [None])[-1],
            "briefings": [REL(f) for f in sorted(BRIEFINGS.glob("*-briefing.md"), reverse=True)[:20]]}


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["sync"]:
        sync("--all" in a)
    elif a[:1] == ["run"]:
        run()
    elif a[:1] == ["check"] and len(a) == 2:
        e = check(a[1])
        print("OK" if not e else "\n".join(e))
        sys.exit(1 if e else 0)
    elif a[:1] == ["status"]:
        print(json.dumps(status(), indent=1))
    else:
        sys.exit(__doc__)
