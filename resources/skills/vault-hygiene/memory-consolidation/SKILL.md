---
id: memory-consolidation
aliases: [memory-consolidation, memory-dream, consolidate-memory]
name: "Memory Consolidation — Reviewed \"Dream\" Pass over the Memory Dir"
category: vault-hygiene
description: Consolidate the cross-session memory dir (MEMORY.md + one file per fact) the way the 2026 "dreaming" systems do, but reviewed. A proposed copy is rewritten so each memory states only what is true now, retired claims move to a dated `## Superseded` section, duplicates merge with `merged_from:`, and replaced memories get `superseded_by:`. A deterministic verifier (`scripts/memory_dream.py check`) checks coverage, preservation and faithfulness. Nothing reaches the live memory without the principal's yes. Triggered by the SessionStart sweep line "N unconsolidated / superseded".
triggers: [consolidate memory, memory consolidation, memory dream, run a memory dream, clean up memory, tidy memory, merge memories, memory is stale, superseded memory, unconsolidated memory, memory sweep says unconsolidated]
tags: [vault-hygiene, memory, consolidation, supersession, verifier, provenance]
related: ["[[vault-maintenance]]", "[[recall]]", "[[skill-library-maintenance]]"]
scripts: [scripts/memory_sweep.py, scripts/memory_dream.py]
modules: [file-backed-state, verifier-separation]
status: active
version: 1
created: 2026-11-08
updated: 2026-11-08
---

# Memory Consolidation — Reviewed "Dream" Pass

**Contract**
- **Input:** the live memory dir (`~/.claude/projects/<project>/memory/`, resolved by `scripts/memory_sweep.py`), plus what the repo and git can confirm. No web, no session transcripts: mining transcripts for new facts would launder outside text into trusted memory (Charter §2). New candidates come from the Stop-hook memory nudge, not from here.
- **Output:** a STATE_ROOT `output/.runs/<YYYYMMDD>-memory-dream/` with `base/`, `proposed/`, `base.sha256`, optional `retired.txt`, `RESPONSE.md` (spine) and `CHANGES.md` (one line per touched memory: what moved and why). After the principal's yes, the live memory dir equals `proposed/`, and `backup/` holds the old files.
- **Allowed tools/artifacts:** `scripts/memory_dream.py` (`stage`, `check`, `diff`, `apply`), `scripts/memory_sweep.py`, Read/Edit inside `proposed/`, and Read/Grep/git over the repo to confirm a fact. Never edit the live memory dir directly. Never run `apply` without an explicit yes in this session, and never from a headless job (the script refuses when `CBRAIN_JOB` is set).
- **Done when:** `memory_dream.py check` prints `OK`, the principal has seen the diff summary and every WARN, and either `apply` ran on their yes (then `memory_sweep.py` shows 0 superseded and 0 unconsolidated) or they declined and the run folder stays as the record.

**The convention (also in `scripts/memory_sweep.py`)**
- The body states only what is true now. A retired claim moves to a closing `## Superseded` section as `- YYYY-MM-DD: <old claim> → <what replaced it>`. It stays auditable, but it never reads as current. *(Memora, arXiv 2604.20006: memory agents keep reusing invalidated memories.)*
- A memory wholly replaced by another gets `superseded_by: <name>` under `metadata:` and leaves `MEMORY.md`.
- A merge deletes the absorbed file and lists it in the survivor's `merged_from: [a.md]`.
- A memory that is simply wrong is deleted and listed in `retired.txt` as `<file> — <reason>`, only on the principal's word.

**Core Blueprint**
1. **Stage.** `python3 scripts/memory_dream.py stage` → STATE_ROOT. Write the spine: stage, consolidate, check, review, apply. Run `python3 scripts/memory_sweep.py` and copy its findings into the spine: these are the work list.
2. **Consolidate in `proposed/` only.** For each flagged memory, and any whose `description:` contradicts its body:
   - Rewrite the body so the current state comes first. Move every inline **Correction / Update / Outcome / Resolved** and every "supersedes / was X" clause into `## Superseded`, with its date.
   - Keep every date, number, path, URL and `[[link]]`. The verifier fails a run that loses one. A stale fact goes to `## Superseded`; it is never deleted.
   - Fix the `description:` and the `MEMORY.md` line so both state the current truth in one line.
   - Merge true duplicates only. Don't merge memories that are merely related; link them with `[[name]]`.
   - Add no facts. A fact you confirmed in the repo or git may be added with its source in `CHANGES.md`. The verifier lists it as WARN, and the principal sees it.
   - Leave untouched memories byte-identical.
3. **Check (verifier separation).** `python3 scripts/memory_dream.py check <RUN>` until `OK`. The checks:
   - **Coverage:** every base memory is kept, merged or retired.
   - **Preservation:** no lost token.
   - **Faithfulness:** new tokens become WARN.
   - **Structure:** frontmatter, `MEMORY.md` complete and ≤ 200 lines, no inline revisions left, no instruction-shaped lines.
   The script is the judge here, not your reading of your own edit.
4. **Review.** Show the principal a short summary: per memory, one line on what moved, every WARN verbatim, any retirement. Offer the full diff (`python3 scripts/memory_dream.py diff <RUN>`). Ask once: apply or not.
5. **Apply on yes only.** Run `python3 scripts/memory_dream.py apply <RUN>`. It refuses if the live dir changed since stage; if so, stage again and carry the edits over. Then `python3 scripts/memory_sweep.py` must show 0 superseded and 0 unconsolidated. Tick the spine. On no, leave the run folder as the record and tick the spine with the decision.

**Optimizations/Gotchas**
- **"Confirmed" is a vault concept, not a memory one.** Memory files are the principal's word by construction. Consolidation may reorganise them, not re-judge them. When two memories contradict and the dates don't settle it, ask the principal; don't pick one.
- **Token preservation is strict on purpose.** If a reformatted date ("22 Oct 2026") fails the check, keep the ISO form. If a stale number seems pointless, it still goes to `## Superseded`: a superseded offer price, still read as current, is the case that motivated this.
- **Descriptions drift first.** The memory index shows the `MEMORY.md` line, but the file's `description:` is what decides relevance during recall. A body updated without its description still misleads (e.g. a status that was overtaken by a later outcome).
- **Scope is the memory dir.** Vault notes have their own trust tier (`confirmed:`) and hygiene skill ([[vault-maintenance]]). Supersession for vault notes is a separate decision.
- **Cadence.** Run it when the SessionStart sweep line shows `unconsolidated` or `superseded`, not on a timer. It needs the principal's review, so a scheduled run would only stage.
