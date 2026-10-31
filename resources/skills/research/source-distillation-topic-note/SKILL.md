---
id: source-distillation-topic-note
aliases: [source-distillation-topic-note]
name: "Source Distillation → Topic Note"
category: research
description: Distill a source (PDF/article/video) into a cited topic anchor with reusable frameworks and talk/business angles, linked to relevant people.
triggers: [shared a source, PDF, article, paper, whitepaper, transcript, distill, use for talks, research this]
tags: [research, distillation, content-idea, sources]
related: ["[[topic-based-linking]]", "[[linkedin-comment-engagement]]", "[[linkedin-repost-evaluator]]"]
status: active
version: 1
created: 2026-07-05
updated: 2026-07-05
vault_writes: ["cbrain/projects/*", "cbrain/Clients/*", "cbrain/daily reports/*"]
---

# Source Distillation → Topic Note

**Triggers/Context**
- User shares a source (PDF, article, paper, video, transcript) and wants to keep/reuse its content — for talks, business, or research.
- Also fires when new knowledge should feed an existing theme rather than sit as a raw dump.

**Core Blueprint**
1. **Distill, don't dump.** Extract the reusable **frameworks, models, tables, and quotable lines** — not a page-by-page summary. Dense, structural bullets (Density Over Volume).
2. **Cite the source** up top (authors, title, publisher, date) in an Obsidian callout — Academic Rigor rule. Offer to archive the full raw source separately if exact quotes will be needed.
3. **Create/append the topic anchor** → `cbrain/projects/<Topic>.md` with frontmatter tags (e.g. `research`, `content-idea`). If the topic note exists, append and reconcile.
4. **Add an audience layer.** For a content creator: a **"Content & talk angles"** section (hooks pitched at the stated audience) and a **"Business relevance"** section tying the topic to active people/engagements.
5. **Bi-directional linking (mandatory):** link the topic note to every relevant person, and add `Topic: [[Topic]]` on each of their notes. Log a one-line entry in the day's `daily reports/` note.

**Optimizations/Gotchas**
- Distillation over transcription: the value is the *framework*, not the prose. Keep only what can be reused in a deliverable.
- Preserve one or two verbatim **quotable lines** — useful for talks/posts — but attribute them.
- If the source strengthens an existing anchor (e.g. [[AI SDLC]]), append there instead of spawning a duplicate hub.
- Always surface the option to store the full source verbatim; distillation is lossy by design.
