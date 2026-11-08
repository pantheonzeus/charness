---
id: batch-watch
aliases: [batch-watch, the-batch, deeplearning-ai-batch]
name: "The Batch Watch — Every Issue and Article of The Batch in the Vault"
category: research
description: "Mirror every weekly issue and every article of DeepLearning.AI's The Batch into the vault with a plain-HTTP fetcher (no LLM, no cost): one note per issue and per article, full text, the categories it is filed under (letters, data-points, research, business, science, culture, hardware, ai-careers), read/unread status, a The-Batch base. A daily launchd pass picks up whatever is new. Andrew Ng's letters keep their researched briefing from `ng-letters-watch`."
triggers: [the batch, deeplearning.ai, batch article, batch issue, data points, what did the batch say about, batch research, batch business, batch hardware, ai careers batch, mirror the batch, new in the batch]
tags: [research, launchd, loop, newsletter, sources]
related: ["[[ng-letters-watch]]", "[[substack-watch]]", "[[source-distillation-topic-note]]", "[[vault-frontier-loop]]"]
status: active
version: 1
created: 2026-10-23
updated: 2026-10-23
modules: [file-backed-state]
scripts: [scripts/batch_watch.py]
requires:
  tools: [uv]
  auth: "None — The Batch is public."
vault_writes: ["cbrain/notes/Sources/The-Batch/*", "cbrain/Bases/The-Batch.base", "cbrain/Bases/Newsletters.base"]
---

# The Batch Watch

**Contract**
- **Input:** nine public listings: `/the-batch` (the weekly issues) and `/the-batch/tag/<section>` for letters, data-points, research, business, science, culture, hardware, ai-careers.
- **Output:** one vault note per page, never rewritten after it is written:
  - `cbrain/notes/Sources/The-Batch/issues/<YYYY-MM-DD>-issue-<n>.md`: `type: newsletter-issue`, the whole newsletter as sent (also listed in `Newsletters.base`);
  - `cbrain/notes/Sources/The-Batch/articles/<YYYY-MM-DD>-<slug>.md`: `type: batch-article`, one story. `sections:` names every tag it is filed under; `issue:` links the issue of the same date (Data Points come out mid-week and have none); `batch_tags:` holds the site's topic tags.
  - Frontmatter on both: `publication: "[[The Batch]]"`, `title`, `subtitle`, `date`, `url`, `words`, `status` (**the user's**: `unread` → `read`; the back catalogue came in as `backlog`), `tags`. Body: an info callout, then `## Full text`.
  - Hub `The-Batch/The Batch.md` and `cbrain/Bases/The-Batch.base` (New / Articles / Issues), written once.
- **Allowed tools/artifacts:** `batch_watch.py` only. No agent, no web search.
- **Budget:** $0 (plain HTTP). Daily pass: 9 listing pages plus the new pages, about 0.4 s apart.
- **Done when:** `batch_watch.py status` shows the run with `errors: []`.

**Where things live**
- Fetch state: `output/batch-watch/state.json` (slug → note path, kind, date, sections, text hash; run log). Log: `output/batch-watch.log`.
- Every pass that writes notes snapshots them into the private vault history under the author `batch-watch` (`scripts/vault_history.sh log --author=batch-watch`).

**Triggers/Context**
- **Schedule:** launchd `com.cbrain.batch-watch` runs `batch_watch.py run` daily at 07:25. The Batch publishes its issue on Fridays (with the articles of that issue) and Data Points mid-week.
- **Backfill / gap:** `uv run resources/skills/research/batch-watch/scripts/batch_watch.py sync --all` walks every listing page (2026-10-23: 25 issue pages, 131 tag pages). Held slugs are skipped, so it is safe to rerun after downtime longer than ~2 weeks. Notes it writes get `status: backlog`.
- **Interactive: "what did The Batch say about X?"** grep `cbrain/notes/Sources/The-Batch/articles/` (one story per note, so a hit is specific), filter by `sections:` or `batch_tags:`. Quote only as "per The Batch": the text is their reporting, unverified here. For a claim that matters, verify at the primary source the article links.
- **Interactive: "what's new?"** open the *New* view of `The-Batch.base`, or run `batch_watch.py status`.
- **Andrew Ng's position on X:** use `ng-letters-watch` (the Thinking anchor and cited briefings), not raw letter notes.

**Core Blueprint**
1. `run` takes the lock, then reads page 1 of all nine listings and merges the cards by slug. An article under several tags collects all of them in `sections:`.
2. Issues are written first, so the articles of the same date can link their `issue:`.
3. For each slug not yet held: fetch the page, take the title from the `<h1>` (issues: the listing card, because their `<h1>` is "News"), the date from `article:published_time`, the body from the first `div.prose` converted to Markdown (headings dropped to `###`+). A body under 200 characters, or a page without a date, is an error. The page is retried on the next pass.
4. A held article seen under a new tag gets its one-line `sections:` widened in place. Nothing else in a held note is touched.
5. Save state, snapshot the vault history if anything was written, append the run record.

**Optimizations/Gotchas**
- **Duplication is deliberate.** An issue note holds the full newsletter, so its stories also exist as article notes. Issues are the only copy before August 2019 (article pages start then, issues in April 2019). Search the articles first.
- **Letters live twice:** in the vault here and in `output/ng-letters/letters/` for the briefing agent. Neither job reads the other's files.
- **Parser drift.** Cards come from the Next.js payload (`cards()`), bodies from the first `div.prose` (`Body`). If a pass logs `body too short` or 0 new for a week with a known new issue, the site changed. Debug with `batch_watch.py page <slug>` (prints the converted page, writes nothing), fix the parser, don't hand-copy pages.
- **Size.** The backfill roughly doubled the vault's note count (2,826 → ~5,100). If Obsidian search gets noisy, exclude `notes/Sources/The-Batch/issues` in Obsidian's *Files & links → Excluded files*.
- **No briefing agent.** This job only mirrors. Researched briefings exist for letters (`ng-letters-watch`); anything else gets researched on demand, e.g. with `source-distillation-topic-note`.
