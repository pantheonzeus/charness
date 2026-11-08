# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown"]
# ///
"""Fill one of the five fixed page templates with a content file. Content and design stay apart.

  page.py spec               the contract: templates, their slots, the block types
  page.py check  <file.md>   validate; prints which heading went to which slot, then OK
  page.py render <file.md>   write the same-stem .html beside it (self-contained)
  (page.py = uv run resources/skills/workflow-ops/reading-pages/scripts/page.py)

Content: a Markdown file with frontmatter `template: briefing|report|decision|plan|dossier`
(+ optional title, subtitle, date, author, status, confidence, lang). Every `## ` section is
matched to a slot of that template by its heading (webapp/design/templates.json); unmatched
sections become body sections. Structured parts are fenced blocks whose language is a block type
(```metrics, ```options, …) holding JSON. No HTML in content: raw HTML is shown as text.
Design: webapp/design/ (theme.css + templates/*.html). Never write CSS or HTML into output/.
The console serves the same render live at /page/<path under output/>; scripts/render.py pdf
prints the .html this writes.
"""
import html
import json
import re
import sys
from pathlib import Path

import markdown

REPO = Path(__file__).resolve().parents[5]
DESIGN = REPO / "webapp" / "design"
REG = json.loads((DESIGN / "templates.json").read_text())
BLOCKS = set(REG["blocks"])
AUDIO = re.compile(r"^(?!/)[\w./-]+\.(m4a|mp3)$")  # relative path to a local file: no scheme, no host, no leading /
FENCE = re.compile(r"^(```+|~~~+)\s*([\w-]*)")
OK_HREF = re.compile(r"^(https?:|mailto:|#|[^:]*$)", re.I)

_md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists"])
_md.preprocessors.deregister("html_block")  # raw HTML in content renders as text, never as markup
_md.inlinePatterns.deregister("html")
esc = html.escape


def md(text: str) -> str:
    _md.reset()
    out = _md.convert(re.sub(r"\n\s*(-{3,}|\*{3,})\s*$", "", text.strip()))  # a trailing --- separator is not content
    out = out.replace("<li>[ ] ", '<li class="todo">☐ ').replace("<li>[x] ", '<li class="todo done">☑ ').replace("<li>[X] ", '<li class="todo done">☑ ')
    return re.sub(r'(href|src)="([^"]*)"', lambda m: m.group(0) if OK_HREF.match(html.unescape(m.group(2))) else f'{m.group(1)}="#"', out)


def inline(text) -> str:
    text = re.sub(r"^(\d+)\.(\s)", r"\1\\.\2", str(text or "").strip())  # "0. The one thing" is a heading, not a list
    out = md(re.sub(r"^([-*+>#])(\s)", r"\\\1\2", text)).strip()
    return out[3:-4] if out.startswith("<p>") and out.endswith("</p>") and out.count("<p>") == 1 else out


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "s"


# ---------- parse ----------

def parse(text: str):
    """→ frontmatter dict, H1 title, preamble, [(heading, body)] split on ## outside code fences."""
    fm = {}
    if text.startswith("---\n") and (end := text.find("\n---", 3)) != -1:
        for line in text[4:end].splitlines():
            if (m := re.match(r"^([A-Za-z_]\w*):\s*(.*)$", line)) and m.group(2).strip():
                fm[m.group(1).lower()] = m.group(2).strip().strip("\"'")
        text = text[end + 4:].split("\n", 1)[1] if "\n" in text[end + 4:] else ""
    title, pre, secs, fence = "", [], [], None
    for line in text.splitlines():
        f = FENCE.match(line)
        if f and (fence is None or line.startswith(fence)):
            fence = f.group(1) if fence is None else None
        elif fence is None and line.startswith("# ") and not title and not secs:
            title = line[2:].strip()
            continue
        elif fence is None and line.startswith("## "):
            secs.append([line[3:].strip(), []])
            continue
        (secs[-1][1] if secs else pre).append(line)
    return fm, title, "\n".join(pre).strip(), [(h, "\n".join(b).strip()) for h, b in secs]


def norm(h: str) -> str:
    h = re.sub(r"[*_`]", "", h).strip().lower()
    return re.sub(r"^(§?\d+[.)]?|[ivx]+\.)\s+", "", h)


def slot_of(heading: str, tpl: dict):
    n = norm(heading)
    for s in tpl["slots"]:
        for a in s["headings"]:
            rest = n[len(a):] if n.startswith(a) else None
            if rest is not None and (rest == "" or rest[0] in ":(" or rest.lstrip()[:1] in ("—", "–", "-")):
                return s["name"]
    return None


# ---------- blocks ----------

def unwrap(data, errs, kind):
    """List blocks take a bare list or {"items": [...], "confidence": ...}."""
    conf = None
    if isinstance(data, dict) and "items" in data:
        conf, data = data.get("confidence"), data["items"]
    if not isinstance(data, list) or not all(isinstance(x, dict) for x in data):
        errs.append(f"{kind}: expected a list of objects")
        return [], conf
    return data, conf


def need(item, keys, kind, errs):
    for k in keys:
        if not item.get(k) and item.get(k) != 0:
            errs.append(f"{kind}: every entry needs `{k}` ({json.dumps(item, ensure_ascii=False)[:80]})")


def src_html(sources) -> str:
    out = []
    for s in sources if isinstance(sources, list) else [sources] if sources else []:
        if isinstance(s, dict):
            label, url = esc(str(s.get("label") or s.get("url") or "")), str(s.get("url") or "")
            out.append(f'<a href="{esc(url)}">{label}</a>' if url.startswith(("http://", "https://")) else label)
        else:
            out.append(inline(s))
    return " · ".join(out)


def block(kind: str, raw: str, errs: list) -> str:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        errs.append(f"{kind}: invalid JSON ({e.msg}, line {e.lineno})")
        return ""
    conf = data.get("confidence") if isinstance(data, dict) else None
    if kind == "callout":
        if not isinstance(data, dict) or not data.get("text"):
            errs.append("callout: needs {\"text\": …}")
            return ""
        tone = data.get("tone") if data.get("tone") in ("info", "risk", "good") else "info"
        lbl = f'<span class="lbl">{esc(data["label"])}</span>' if data.get("label") else ""
        h = f'<div class="callout {tone}">{lbl}{inline(data["text"])}</div>'
    elif kind == "audio":
        items, conf = unwrap(data, errs, kind)
        h = ""
        for i in items:
            need(i, ["title", "src"], kind, errs)
            if not AUDIO.match(str(i.get("src", ""))):
                errs.append(f"audio: src must be a relative path to a .m4a/.mp3 file ({i.get('src')!r})")
                continue
            h += f'<div class="card audio"><div class="n">{inline(i.get("title"))}</div><audio controls preload="none" src="{esc(str(i["src"]))}"></audio></div>'
    elif kind == "options":
        opts = data.get("options") if isinstance(data, dict) else None
        if not isinstance(opts, list) or not 2 <= len(opts) <= 5:
            errs.append("options: needs {\"options\": [2–5 × {label, for?, against?}]}")
            return ""
        rec = str(data.get("recommendation") or "")
        cards = []
        for o in opts:
            need(o, ["label"], kind, errs)
            is_rec = rec and str(o.get("label")) == rec
            cards.append(f'<div class="card{" rec" if is_rec else ""}">' + ('<span class="chip rec">Recommended</span>' if is_rec else "")
                         + f'<h3>{inline(o.get("label"))}</h3>' + (f'<div>{inline(o["summary"])}</div>' if o.get("summary") else "")
                         + (f'<p class="pro"><b>For</b>{inline(o["for"])}</p>' if o.get("for") else "")
                         + (f'<p class="con"><b>Against</b>{inline(o["against"])}</p>' if o.get("against") else "") + "</div>")
        if rec and not any(str(o.get("label")) == rec for o in opts):
            errs.append(f"options: recommendation {rec!r} matches no option label")
        q = f'<p class="question">{inline(data["question"])}</p>' if data.get("question") else ""
        h = f'{q}<div class="options">{"".join(cards)}</div>'
    else:
        items, conf = unwrap(data, errs, kind)
        if kind == "metrics":
            for i in items: need(i, ["label", "value"], kind, errs)
            h = '<div class="tiles">' + "".join(
                f'<div class="tile"><div class="v">{esc(str(i.get("value", "")))}</div><div class="l">{inline(i.get("label"))}</div>'
                + (f'<div class="d">{inline(i["delta"])}</div>' if i.get("delta") else "")
                + (f'<div class="s">{src_html(i["source"])}</div>' if i.get("source") else "") + "</div>" for i in items) + "</div>"
        elif kind == "timeline":
            for i in items: need(i, ["date", "label"], kind, errs)
            h = '<ol class="timeline">' + "".join(
                f'<li class="{esc(str(i.get("kind") or "past"))}"><span class="dt">{esc(str(i.get("date", "")))}</span>{inline(i.get("label"))}</li>'
                for i in items) + "</ol>"
        elif kind == "risks":
            rows = []
            for i in items:
                need(i, ["label"], kind, errs)
                try:
                    lv = max(0.0, min(1.0, float(i.get("level", 0))))
                except (TypeError, ValueError):
                    errs.append(f"risks: level must be a number 0–1 ({i.get('label')})")
                    lv = 0.0
                word = "high" if lv >= .67 else "medium" if lv >= .34 else "low"
                rows.append(f'<li><span>{inline(i.get("label"))}</span><span><span class="bar"><i style="width:{lv * 100:.0f}%"></i></span>'
                            f'<span class="lv">{word} · {lv:.1f}</span></span>' + (f'<span class="note">{inline(i["note"])}</span>' if i.get("note") else "") + "</li>")
            h = '<ul class="risks">' + "".join(rows) + "</ul>"
        elif kind == "people":
            for i in items: need(i, ["name"], kind, errs)
            h = '<div class="people">' + "".join(
                f'<div class="card"><div class="n">{esc(str(i.get("name", "")))}</div>'
                + (f'<div class="r">{esc(str(i["role"]))}</div>' if i.get("role") else "")
                + (f'<span class="chip {esc(str(i["stance"]))}">{esc(str(i["stance"]))}</span>' if i.get("stance") else "")
                + (f'<p>{inline(i["note"])}</p>' if i.get("note") else "") + "</div>" for i in items) + "</div>"
        elif kind == "steps":
            marks = {"done": "☑", "doing": "◐", "blocked": "⊘"}
            for i in items: need(i, ["label"], kind, errs)
            h = '<ul class="steps">' + "".join(
                f'<li class="{esc(str(i.get("status") or "todo"))}"><span class="box">{marks.get(i.get("status"), "☐")}</span>'
                f'<span class="t">{inline(i.get("label"))}</span><span class="who">{esc(" · ".join(str(i[k]) for k in ("owner", "due") if i.get(k)))}</span></li>'
                for i in items) + "</ul>"
        else:  # items: news / findings cards
            for i in items: need(i, ["headline"], kind, errs)
            h = '<div class="grid-cards">' + "".join(
                f'<div class="card item"><h3>{inline(i.get("headline"))}</h3>' + (f'<div>{inline(i["summary"])}</div>' if i.get("summary") else "")
                + (f'<div class="why"><b>Why it matters</b> {inline(i["why"])}</div>' if i.get("why") else "")
                + (f'<div class="src">{src_html(i["sources"])}</div>' if i.get("sources") else "") + "</div>" for i in items) + "</div>"
    if conf in ("likely", "unsure"):
        h = f'<div class="conf-{conf}">{h}<p class="conf-tag">Confidence: {conf}</p></div>'
    return h


def section_html(body: str, errs: list) -> str:
    """Markdown with typed fenced blocks swapped out, rendered, and swapped back in."""
    parts, out, buf, kind, fence = [], [], [], None, None
    for line in body.splitlines():
        f = FENCE.match(line)
        if kind is None and fence is None and f and f.group(2) in BLOCKS:
            kind, fence = f.group(2), f.group(1)
        elif kind and line.strip() == fence:
            parts.append(block(kind, "\n".join(buf), errs))
            out.append(f"\n\n@@BLOCK{len(parts) - 1}@@\n\n")
            kind, fence, buf = None, None, []
        elif kind:
            buf.append(line)
        else:
            if f:  # an ordinary code fence: track it so a ``` inside stays code
                fence = None if fence and line.startswith(fence) else (fence or f.group(1))
            out.append(line)
    if kind:
        errs.append(f"{kind}: fence never closed")
    rendered = md("\n".join(out))
    return re.sub(r"<p>@@BLOCK(\d+)@@</p>", lambda m: parts[int(m.group(1))], rendered)


# ---------- build ----------

def build(path: Path):
    """→ (filled html or None, errors, mapping lines)."""
    fm, h1, pre, secs = parse(path.read_text(encoding="utf-8"))
    name = fm.get("template", "")
    if name not in REG["templates"]:
        return None, [f"frontmatter `template:` must be one of {', '.join(REG['templates'])} (got {name!r})"], []
    tpl, errs, mapping = REG["templates"][name], [], []
    slots, body, toc = {}, [], []
    if pre and not any(slot_of(h, tpl) == "lead" for h, _ in secs):
        slots["lead"] = [section_html(pre, errs)]
        mapping.append("lead     ← text before the first ## (no lead heading)")
    elif pre:
        body.append(f'<section class="sec">{section_html(pre, errs)}</section>')
    for heading, text in secs:
        s = slot_of(heading, tpl)
        inner = f"<h2>{inline(heading)}</h2>{section_html(text, errs)}"
        if s:
            slots.setdefault(s, []).append(inner)
            mapping.append(f"{s:<8} ← {heading}")
        else:
            sid = slug(heading)
            body.append(f'<section class="sec" id="{sid}">{inner}</section>')
            toc.append(f'<li><a href="#{sid}">{inline(heading)}</a></li>')
            mapping.append(f"body     ← {heading}")
    for s in tpl["slots"]:
        if s.get("required") and s["name"] not in slots:
            errs.append(f"missing required slot `{s['name']}`: add a section headed one of: {', '.join(s['headings'][:5])}")
    title = fm.get("title") or h1
    if not title:
        errs.append("no title: add `title:` to the frontmatter or a `# ` heading")
    meta = " · ".join(x for x in (fm.get("date"), fm.get("author"), fm.get("status"),
                                  f"confidence: {fm['confidence']}" if fm.get("confidence") else "") if x)
    ctx = {"lang": esc(fm.get("lang", "en")), "title": esc(title), "label": esc(tpl["label"]), "meta": esc(meta),
           "subtitle": f'<p class="sub">{inline(fm["subtitle"])}</p>' if fm.get("subtitle") else "",
           "css": (DESIGN / "theme.css").read_text(), "body": "".join(body),
           "toc": f"<ol>{''.join(toc)}</ol>" if len(toc) > 1 else ""}
    for s, inners in slots.items():
        cls = "slot lead" if s == "lead" else f"slot slot-{s}"
        ctx[f"slot:{s}"] = f'<section class="{cls}" id="{s}">{"".join(inners)}</section>'
    skeleton = (DESIGN / "templates" / f"{name}.html").read_text()
    for s in slots:
        if "{{slot:%s}}" % s not in skeleton:
            errs.append(f"design bug: templates/{name}.html has no {{{{slot:{s}}}}}")
    filled = re.sub(r"\{\{([a-z:]+)\}\}", lambda m: ctx.get(m.group(1), ""), skeleton)  # one pass: content is never re-read
    return filled, errs, mapping


def render_page(path: Path) -> str:
    """For the console: the filled page, or ValueError listing what's wrong."""
    filled, errs, _ = build(path)
    if errs:
        raise ValueError("; ".join(errs))
    return filled


def is_page(path: Path) -> bool:
    with path.open(encoding="utf-8", errors="replace") as f:
        head = f.read(600)
    return head.startswith("---\n") and re.search(r"^template:\s*\w", head.split("\n---", 1)[0], re.M) is not None


def index_html(root: Path) -> str:
    """The console's /pages: every templated deliverable under output/, newest first. Navigation, not a template."""
    rows = []
    files = [f for f in root.rglob("*.md") if ".runs" not in f.parts and is_page(f)]
    for f in sorted(files, key=lambda f: f.stat().st_mtime, reverse=True):
        fm, h1, _, _ = parse(f.read_text(encoding="utf-8"))
        t = REG["templates"].get(fm.get("template", ""), {})
        rel = f.relative_to(root).as_posix()
        rows.append(f'<li><span class="chip">{esc(t.get("label", "?"))}</span> <a href="/page/{esc(rel)}">{esc(fm.get("title") or h1 or f.stem)}</a>'
                    f' <span class="meta">{esc(fm.get("date", ""))} · {esc(rel)}</span></li>')
    body = f'<ul class="pagelist">{"".join(rows)}</ul>' if rows else '<p class="meta">No templated pages yet. A page is an output/**.md with `template:` in its frontmatter.</p>'
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>Pages</title><style>{(DESIGN / "theme.css").read_text()}</style></head><body><main class="page">'
            f'<header class="mast"><div class="kicker">cbrain</div><h1>Pages</h1></header>{body}</main></body></html>')


def spec() -> str:
    lines = ["Templates (frontmatter `template:`) and their slots (## heading → slot; * = required; anything else → body):"]
    for n, t in REG["templates"].items():
        lines.append(f"\n{n} — {t['label']}: {t['use_for']}")
        for s in t["slots"]:
            lines.append(f"  {'*' if s.get('required') else ' '}{s['name']:<9} {' | '.join(s['headings'])}")
    lines.append("\nBlocks (fenced, language = type, body = JSON; list blocks also take {\"items\": [...], \"confidence\": \"likely|unsure\"}):")
    lines += ['  callout  {"text", "tone": "info|risk|good", "label"?}',
              '  metrics  [{"label", "value", "delta"?, "source"?}]   real numbers only, each with a source',
              '  timeline [{"date", "label", "kind": "past|next|deadline"}]',
              '  options  {"question"?, "options": [{"label", "summary"?, "for"?, "against"?}], "recommendation"?: <an option label>}',
              '  risks    [{"label", "level": 0..1, "note"?}]',
              '  people   [{"name", "role"?, "stance"?: "champion|supporter|neutral|skeptic|blocker|unknown", "note"?}]',
              '  steps    [{"label", "owner"?, "due"?, "status"?: "todo|doing|done|blocked"}]',
              '  items    [{"headline", "summary"?, "why"?, "sources"?: ["text" | {"label", "url"}]}]',
              '  audio    [{"title", "src": <path relative to the page, .m4a or .mp3, e.g. "../podcasts/x.m4a">}]']
    return "\n".join(lines)


def main(argv):
    if argv[:1] == ["spec"]:
        return print(spec())
    if len(argv) != 2 or argv[0] not in ("check", "render"):
        sys.exit(__doc__)
    path = Path(argv[1]).resolve()
    if path.suffix != ".md" or not path.is_file():
        sys.exit(f"not a .md file: {argv[1]}")
    filled, errs, mapping = build(path)
    print("\n".join(mapping))
    if errs:
        sys.exit("FAIL\n- " + "\n- ".join(errs))
    if argv[0] == "render":
        out = path.with_suffix(".html")
        out.write_text(filled, encoding="utf-8")
        print(f"OK → {out.relative_to(REPO) if out.is_relative_to(REPO) else out}")
    else:
        print("OK")


if __name__ == "__main__":
    main(sys.argv[1:])
