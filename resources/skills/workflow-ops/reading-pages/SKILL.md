---
id: reading-pages
aliases: [reading-pages, page-templates, html-pages, pages]
name: "Reading Pages — Five Fixed Templates, Content Only"
category: workflow-ops
description: Turn any document people should read (briefing, research report, decision memo, plan, brief/dossier) into an HTML page by writing content only, a Markdown file with `template:` frontmatter, `## ` sections and optional typed JSON blocks, and letting `page.py` slot it into one of five fixed templates. The design lives once in `webapp/design/`; agents never write HTML or CSS. The console renders pages live at `/page/<path>` and lists them at `/pages`.
triggers: [html page, make it a page, readable page, html report, render as html, page template, briefing page, report page, decision memo, one-pager, nice html, open as page]
tags: [workflow-ops, console, html, templates, content-design-separation]
related: ["[[situation-surfaces]]", "[[deep-research]]", "[[living-plan]]", "[[daily-intel-briefing]]", "[[morning-briefing]]", "[[deliverable-index]]"]
status: active
version: 1
created: 2026-10-18
updated: 2026-10-18
scripts: [scripts/page.py]
---

# Reading Pages

**Contract**
- **Input:** a finished document's content.
- **Output:** `output/<…>/<name>.md` with `template:` frontmatter, plus the same-stem `.html` written by `page.py render` when the file has to work outside the console (opened from Finder, printed, attached).
- **Allowed:** Markdown, the typed blocks below and nothing else. Never write HTML, CSS or a `<style>` into `output/`, and never hand-build a page. If a document doesn't fit a template, use the nearest one and let the extra sections fall into the body. A sixth template needs the user's approval and a change in `webapp/design/`.
- **Done when:** `uv run resources/skills/workflow-ops/reading-pages/scripts/page.py check <file.md>` prints `OK`.

**Why.** Every hand-built HTML deliverable in `output/` carried its own CSS, so the look was recreated, and drifted, on every run. Content and design are now separate. The agent fills slots; `webapp/design/` (`theme.css`, `templates/*.html`, `templates.json`) owns the look, and one change there updates every page.

**Pick the template by the reader's job**

| template | the reader wants to | required `##` | other slots |
|---|---|---|---|
| `briefing` | scan what's new today | Headline (or the text before the first `##`) | At a glance · Watchlist / Listen · Sources |
| `report` | understand an answer and trust it | Bottom line | Confidence and gaps · Sources |
| `decision` | make one call | Recommendation · Options | Risks · Next steps · Sources |
| `plan` | execute in phases | Goal (or the text before the first `##`) | Risks · Next steps · Sources |
| `dossier` | walk into a room prepared | The one thing | Profile · Talking points · Unknowns · Sources |

Any `##` heading that matches no slot becomes a body section (and a contents entry in `report`). `page.py spec` prints every accepted heading and block field; `check` prints where each heading went.

**Frontmatter:** `template` (required), `title` (or a `# ` heading), and optionally `subtitle`, `date`, `author`, `status`, `confidence`, `lang`.

**Blocks** (a fenced block whose language is the type and whose body is JSON):
`callout` · `metrics` · `timeline` · `options` · `risks` · `people` · `steps` · `items` · `audio`. The fields match `situation-surfaces`. A list block also takes `{"items": [...], "confidence": "likely|unsure"}`, and the page then frames it as less certain.

**Core Blueprint**
1. Pick the template from the table. Write the lead first: the answer, the call, the goal or the one thing.
2. Write the sections in Markdown. Use a block only where the shape matters: real numbers → `metrics` (each with a source), a choice → `options` with `recommendation` equal to one option's label, dated sequence → `timeline`, owned actions → `steps`.
3. Run `page.py check`. On `FAIL`, fix the named slot or block and run it again.
4. Run `page.py render` when the file must stand alone. `scripts/render.py pdf <file.md>` then prints that `.html`.
5. In the console, the page is at `/page/<path under output/>` and appears in `/pages`.

**Optimizations/Gotchas**
- **Never invent a number to fill a `metrics` tile.** A page looks more credible than its evidence; that is exactly why unsure blocks render rougher.
- **Untrusted text** (web, mail, calendar) going into a page must not start a line with `#` or a code fence. The producers' scripts escape it; do the same in new producers.
- Pages never run script (CSP `default-src 'none'`). Audio is allowed only from relative local paths (`../podcasts/x.m4a`).
- Producers on this contract: `research/deep-research` (report), `workflow-ops/living-plan` (by deliverable shape), `workflow-ops/daily-intel-briefing` (`briefing.py page`, mechanical), `workflow-ops/morning-briefing` (`build_briefing_html.py`, mechanical).
