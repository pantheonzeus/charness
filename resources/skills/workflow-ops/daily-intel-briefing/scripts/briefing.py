#!/usr/bin/env python3
"""Deterministic half of the daily-intel-briefing skill.

  briefing.py check <output/briefings/YYYY-MM-DD.json>   validate briefing + its deep-dive pages; OK or the errors (exit 1)
  briefing.py prefs                                      learned reader preferences from feedback.jsonl
  briefing.py page <YYYY-MM-DD>                          write output/briefings/<date>.md, the reading page
                                                         (template: briefing, reading-pages skill) the console shows at /page/

feedback.jsonl is written by the web console (webapp/server.py), one line per click:
  {"ts": ..., "date": "YYYY-MM-DD", "item_id": "ai-1", "vote": 1 | -1 | 0}   (last vote per item wins)
  {"ts": ..., "date": "YYYY-MM-DD", "item_id": "ai-1", "action": "saved"}    (saved to vault: strongest signal)
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[5]
BRIEFINGS = REPO / "output" / "briefings"
FEEDBACK = BRIEFINGS / "feedback.jsonl"
# Theme sections first (the principal's eight AI themes, 2026-10-31), then the two standing ones.
SECTIONS = ["llm-enterprise", "agentic-ops", "token-finops", "self-improvement", "physical-ai",
            "enterprise-value", "cyber-security", "sovereign-regulation", "emerging", "de-manufacturing"]
MAX_ITEMS = 4
MAX_TOTAL = 18        # keeps the podcast (one segment per item) inside its word cap
MAX_DEEP_DIVES = 3
MIN_DEEP_SOURCES = 4
MIN_LEARN_SOURCES, MAX_FOCUS = 5, 800   # NotebookLM learning podcast per topic (learn_podcasts.py)
RADAR_TERMS = ["Large quantitative models", "Speech reasoning models", "World models", "AI context platforms",
               "AI coding agent harness", "AI agent identity", "Autonomous exposure remediation", "SovereignTech",
               "Disposable applications", "Wetware as a service"]


def check(path):
    errors = []
    try:
        b = json.loads(Path(path).read_text())
    except (OSError, ValueError) as e:
        return ["cannot read JSON: %s" % e]
    if b.get("date") != Path(path).stem:
        errors.append("date %r does not match filename %s" % (b.get("date"), Path(path).name))
    for key in ("window", "headline"):
        if not str(b.get(key, "")).strip():
            errors.append("missing %s" % key)
    sections = b.get("sections") or []
    if [s.get("id") for s in sections] != SECTIONS:
        errors.append("sections must be exactly %s in that order" % SECTIONS)
    seen = set()
    for s in sections:
        sid, items = s.get("id"), s.get("items") or []
        if not items and not str(s.get("note", "")).strip():
            errors.append("%s: no items and no note — say 'Nothing material since …' instead" % sid)
        if len(items) > MAX_ITEMS:
            errors.append("%s: %d items, max %d" % (sid, len(items), MAX_ITEMS))
        for it in items:
            iid = it.get("id", "?")
            if not re.fullmatch(r"%s-\d+" % re.escape(str(sid)), str(iid)):
                errors.append("%s: id %r must look like %s-<n>" % (sid, iid, sid))
            if iid in seen:
                errors.append("duplicate item id %s" % iid)
            seen.add(iid)
            for key in ("headline", "summary", "why_it_matters"):
                if not str(it.get(key, "")).strip():
                    errors.append("%s: missing %s" % (iid, key))
            srcs = it.get("sources") or []
            if not srcs or not all(str(x.get("url", "")).startswith(("http://", "https://")) for x in srcs):
                errors.append("%s: every item needs >=1 source with an http(s) url" % iid)
            if not it.get("tags"):
                errors.append("%s: needs tags (they drive preference learning)" % iid)
            for link in it.get("vault_links") or []:
                if not re.fullmatch(r"\[\[[^\]]+\]\]", link):
                    errors.append("%s: vault link %r must be [[Note Name]]" % (iid, link))
        for ind in s.get("indicators") or []:
            if not all(str(ind.get(k, "")).strip() for k in ("name", "value", "period")):
                errors.append("%s: indicator needs name, value, period" % sid)
            if not str(ind.get("source", "")).startswith(("http://", "https://")):
                errors.append("%s: indicator %r needs a source url" % (sid, ind.get("name")))
    if len(seen) > MAX_TOTAL:
        errors.append("%d items in total, max %d: keep the strongest" % (len(seen), MAX_TOTAL))
    for hit in b.get("radar") or []:
        if hit.get("term") not in RADAR_TERMS:
            errors.append("radar term %r is not one of %s" % (hit.get("term"), RADAR_TERMS))
        if hit.get("item_id") not in seen:
            errors.append("radar hit %r points at item %r, which is not in the briefing" % (hit.get("term"), hit.get("item_id")))
    dives = b.get("deep_dives") or []
    if len(dives) > MAX_DEEP_DIVES:
        errors.append("%d deep dives, max %d" % (len(dives), MAX_DEEP_DIVES))
    if not dives and not str(b.get("deep_dive_note", "")).strip():
        errors.append("no deep dives and no deep_dive_note: say why today has none")
    for n, d in enumerate(dives, 1):
        did = "dd-%d" % n
        if d.get("id") != did:
            errors.append("deep dive %d: id must be %s" % (n, did))
        if d.get("item_id") not in seen:
            errors.append("%s: item_id %r is not in the briefing" % (did, d.get("item_id")))
        for key in ("title", "bottom_line"):
            if not str(d.get(key, "")).strip():
                errors.append("%s: missing %s" % (did, key))
        errors += ["%s: %s" % (did, e) for e in check_deep_page(BRIEFINGS / str(b.get("date")) / ("%s.md" % did))]
    with_items = [s.get("id") for s in sections if s.get("items")]
    packs = {p.get("section"): p for p in b.get("learn") or []}
    for sid in with_items:
        p = packs.get(sid)
        if not p:
            errors.append("learn: section %s has items but no learning pack" % sid)
            continue
        if not str(p.get("title", "")).strip():
            errors.append("learn %s: missing title" % sid)
        if not 0 < len(str(p.get("focus", "")).strip()) <= MAX_FOCUS:
            errors.append("learn %s: focus must be 1-%d characters" % (sid, MAX_FOCUS))
        urls = {u for u in p.get("sources") or [] if str(u).startswith(("http://", "https://"))}
        if len(urls) < MIN_LEARN_SOURCES:
            errors.append("learn %s: %d distinct http(s) sources, min %d" % (sid, len(urls), MIN_LEARN_SOURCES))
    for sid in set(packs) - set(with_items):
        errors.append("learn: pack for %r, which is not a section with items today" % sid)
    return errors


def check_deep_page(path):
    """The page itself is rendered by reading-pages (template: report); this checks what the briefing relies on."""
    try:
        text = path.read_text()
    except OSError:
        return ["page %s missing" % path.relative_to(REPO)]
    errors = []
    if not re.match(r"---\n(.*\n)*?template: report\n", text):
        errors.append("page needs frontmatter with template: report")
    heads = [h.strip().lower() for h in re.findall(r"^## (.+)$", text, re.M)]
    for need in ("bottom line", "confidence and gaps", "sources"):
        if need not in heads:
            errors.append("page needs a '## %s' section" % need.capitalize())
    urls = set(re.findall(r"https?://[^\s)\]>\"]+", text))
    if len(urls) < MIN_DEEP_SOURCES:
        errors.append("page cites %d distinct sources, min %d" % (len(urls), MIN_DEEP_SOURCES))
    return errors


def one_line(s):
    """Briefing text is web-derived: it may not open a heading or fence of its own on the page."""
    return re.sub(r"^(#|```|~~~)", r"\\\1", " ".join(str(s or "").split()))


def fenced(kind, data):
    return "```%s\n%s\n```" % (kind, json.dumps(data, ensure_ascii=False, indent=1))


def page(date):
    """Content only: the reading-pages templates own the look. Mechanical, so no agent cost."""
    b = json.loads((BRIEFINGS / ("%s.json" % date)).read_text())
    out = ["---", "template: briefing", "title: Daily intel — %s" % b["date"], "date: %s" % one_line(b.get("window")),
           "---", "", "## Headline", "", one_line(b.get("headline")), ""]
    for s in b.get("sections") or []:
        out += ["## " + one_line(s.get("title") or s.get("id")), ""]
        if str(s.get("note", "")).strip():
            out += [one_line(s["note"]), ""]
        if s.get("indicators"):
            out += [fenced("metrics", [{"label": "%s (%s)" % (i.get("name"), i.get("period")), "value": i.get("value"),
                                        "delta": i.get("change") or "", "source": {"label": "source", "url": i.get("source")}}
                                       for i in s["indicators"]]), ""]
        if s.get("items"):
            out += [fenced("items", [{"headline": it.get("headline"), "summary": it.get("summary"), "why": it.get("why_it_matters"),
                                      "sources": [{"label": x.get("title") or x.get("url"), "url": x.get("url")} for x in it.get("sources") or []]}
                                     for it in s["items"]]), ""]
    if b.get("deep_dives"):
        out += ["## Deep dives", ""] + ["- [%s](%s/%s.md): %s" % (one_line(d.get("title")).replace("[", "(").replace("]", ")"), b["date"], d.get("id"),
                                                                  one_line(d.get("bottom_line"))) for d in b["deep_dives"]] + [""]
    if b.get("radar"):
        heads = {it.get("id"): it.get("headline") for s in b.get("sections") or [] for it in s.get("items") or []}
        out += ["## Radar hits", ""] + ["- **%s**: %s" % (one_line(r.get("term")), one_line(heads.get(r.get("item_id"))))
                                        for r in b["radar"]] + [""]
    if b.get("watchlist"):
        out += ["## Watchlist", ""] + ["- " + one_line(w) for w in b["watchlist"]] + [""]
    titles = {s.get("id"): s.get("title") for s in b.get("sections") or []}
    audio = [{"title": "Briefing podcast — %s" % date, "src": "%s.mp3" % date}] if (BRIEFINGS / ("%s.mp3" % date)).exists() else []
    audio += [{"title": "Learn · %s" % titles.get(f.stem, f.stem), "src": "%s/learn/%s" % (date, f.name)}
              for f in sorted((BRIEFINGS / date / "learn").glob("*.m4a"))]
    if audio:
        out += ["## Listen", "", fenced("audio", audio), ""]
    path = BRIEFINGS / ("%s.md" % date)
    path.write_text("\n".join(out), encoding="utf-8")
    print("Wrote %s" % path.relative_to(REPO))


def prefs():
    if not FEEDBACK.exists():
        print("No reader feedback yet — select on relevance to the persona alone.")
        return
    votes, saved = {}, set()
    for line in FEEDBACK.read_text().splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        key = (e.get("date"), e.get("item_id"))
        if e.get("action") == "saved":
            saved.add(key)
        elif "vote" in e:
            votes[key] = e["vote"]

    items, cache = {}, {}
    for date, iid in set(votes) | saved:
        if date not in cache:
            try:
                cache[date] = json.loads((BRIEFINGS / ("%s.json" % date)).read_text())
            except (OSError, ValueError):
                cache[date] = {"sections": []}
        for s in cache[date].get("sections", []):
            for it in s.get("items", []):
                if it.get("id") == iid:
                    items[(date, iid)] = dict(it, section=s.get("id"))

    tags, domains, sections = Counter(), Counter(), Counter()
    for key, it in items.items():
        w = votes.get(key, 0) + (2 if key in saved else 0)
        if not w:
            continue
        sections[it["section"]] += w
        for t in it.get("tags", []):
            tags[t] += w
        for src in it.get("sources", []):
            domains[urlparse(src.get("url", "")).netloc.replace("www.", "")] += w

    def fmt(counter, positive):
        picked = [(k, v) for k, v in counter.most_common() if (v > 0) == positive and v != 0]
        if not positive:
            picked = sorted(picked, key=lambda kv: kv[1])
        return ", ".join("%s (%+d)" % kv for kv in picked[:10]) or "—"

    print("Reader preferences from %d votes and %d vault saves:" % (len(votes), len(saved)))
    print("- sections: " + (", ".join("%s (%+d)" % kv for kv in sections.most_common()) or "—"))
    print("- more of (tags): " + fmt(tags, True))
    print("- less of (tags): " + fmt(tags, False))
    print("- trusted sources: " + fmt(domains, True))
    print("- disliked sources: " + fmt(domains, False))
    recent = sorted(items.items(), key=lambda kv: kv[0][0], reverse=True)[:8]
    for (date, iid), it in recent:
        mark = "saved" if (date, iid) in saved else {1: "👍", -1: "👎"}.get(votes.get((date, iid)), "")
        if mark:
            print("  %s %s: %s" % (mark, date, it.get("headline", "")))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "check":
        errs = check(sys.argv[2])
        print("OK" if not errs else "\n".join("FAIL: " + e for e in errs))
        sys.exit(1 if errs else 0)
    if len(sys.argv) == 3 and sys.argv[1] == "page":
        page(sys.argv[2])
        sys.exit(0)
    if len(sys.argv) == 2 and sys.argv[1] == "prefs":
        prefs()
        sys.exit(0)
    print(__doc__)
    sys.exit(64)
