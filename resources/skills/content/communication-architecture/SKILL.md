---
id: communication-architecture
aliases: [communication-architecture]
name: "Communication Architecture — Executive TL;DR → Strategic Narrative"
category: content
description: Format comprehensive messages, reports, and strategic emails in the Soul.md executive voice — a top Executive TL;DR (3–4 bolded bullets) then a divider and a Strategic Narrative broken down by the Business → Product → Technology hierarchy.
triggers: [report, strategic email, comprehensive message, executive summary, executive tldr, strategic narrative, briefing, board update, decision memo, write a report, draft an email to leadership]
tags: [content, communication, formatting, executive, voice]
related: ["[[proposal-challenger]]", "[[audience-of-one-report]]", "[[company-challenger-brief]]"]
status: active
version: 1
created: 2026-07-07
updated: 2026-07-07
---

# Communication Architecture — Executive TL;DR → Strategic Narrative

*Operational procedure — how the Soul.md voice is formatted on the page. Identity lives in Soul.md; this is execution. Extracted from the always-on CLAUDE.md layer so it loads only when producing a comprehensive deliverable.*

**Triggers/Context**
- Producing a **comprehensive** message, report, strategic email, briefing, board update, or decision memo.
- **Not** for routine confirmations, quick vault edits, or short off-lane answers — those stay governed by **Density Over Volume** (keep them terse; do not inflate a small ask into a deck).

**Core Blueprint** — structure the deliverable in exactly two parts:

### 1. The Executive TL;DR
- **Positioning:** at the absolute top of the response.
- **Format:** maximum 3–4 high-impact, **bolded** bullet points.
- **Content:** the core conclusion, strategic recommendation, and bottom-line impact. A busy executive must grasp the entire narrative in 15 seconds.

### 2. Strategic Narrative (Long-Form Detail)
- **Positioning:** follows a clear divider (`---`) after the TL;DR.
- **Format:** clean Markdown headings (`##`, `###`), concise paragraphs, data-dense bulleted lists.
- **Content:** deep-dive analysis broken down by the Strategic Hierarchy — **Business impact → Product strategy → Technical execution**.
- **Close:** end with clear ownership lines, next steps, or decision gates.

**Optimizations/Gotchas**
- Lead with business impact, not the stack — the Soul.md lens is Business → Product → Technology. Redirect only if the user explicitly asks to start at architecture.
- The TL;DR is a *conclusion*, not a table of contents — state the recommendation and its bottom line, don't preview section titles.
- No hedging, no performative warmth, no corporate fluff (Soul.md voice). State risks as owned bets, not qualifiers.
- Cite sources for factual/research claims (Academic Rigor).
- Density Over Volume still applies *within* each section — crisp structural bullets over dense paragraphs.
