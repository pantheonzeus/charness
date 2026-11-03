---
id: skill-library-maintenance
aliases: [skill-library-maintenance]
name: "Skill Library Maintenance"
category: vault-hygiene
description: Import external skills into resources/skills/ and keep the library consistent — copy-verbatim vs reproduce-and-clean, frontmatter mapping, INDEX/counts/category sync, when to extend the schema additively, and proposing new skills from heavy sessions no skill covered.
triggers: [import skill, add this skill, import a skill from, add to our schema, extend the schema, new skill folder, maintain the skill library, keep INDEX in sync, propose skills, skill candidates, which sessions should become skills, agent skills spec, export a skill, spec-compliant skill]
tags: [vault-hygiene, skills, meta, import, schema, maintenance]
related: []
scripts: [scripts/lint_frontmatter.py, scripts/routing_eval.py, scripts/lean_index.py, scripts/skill_candidates.py, scripts/spec_export.py, ../../../../scripts/skill_router.py]
workflows: [workflows/propose-from-sessions.md]
modules: [autoresearch-loop]
status: active
version: 7
created: 2026-07-05
updated: 2026-11-02
---

# Skill Library Maintenance

The meta-skill for `resources/skills/`. Governs importing external skills, keeping the registry consistent, and extending the schema without breaking what exists. Read `resources/skills/README.md` first — it holds the contract this skill operates.

**Triggers/Context**
- "import skill from `<folder>`", "add this skill", "add to our schema / extend our schema".
- Any add / rename / remove / recategorize of a skill (the INDEX and counts must stay in sync).
- Deciding whether a new skill's needs justify an additive schema change.
- Exporting or packaging a skill for a native loader (claude.ai upload, a Claude Code plugin, an org marketplace): run `scripts/spec_export.py export`. It never touches the source.
- "Propose skills" / "which sessions should become skills": run `workflows/propose-from-sessions.md`. It drafts proposals from heavy sessions no skill covered, and builds only the ones the principal approves.

**Core Blueprint**
1. **Locate + inspect the source.** `find <src> -type f | sort`; line counts; detect executables and shebangs (`head -1`, `file`). Know what you're importing before you touch it.
2. **Pick the import mode:**
   - **Copy-verbatim (default for real on-disk skills)** — `cp -R <src> <dest>`. Preserves code, the executable bit, and the SKILL.md's *internal* relative paths (`scripts/…`, `workflows/…`). **Never retype scripts.** Confirm with `diff -rq <src> <dest>` → byte-identical.
   - **Reproduce-and-clean (only when the source is provided as text)** — e.g. pasted documents. Reproduce faithfully and **normalise mojibake** to clean Markdown (Obsidian Hygiene). Common map: `â`→ `—`/`→`/quotes (by context), `Ã—`→`×`, `Â§`→`§`, `â¥`→`≥`, `â¤`→`≤`, `Â·`→`·`, `Â£`→`£`, `â¦`→`…`; fix accented names (`NestlÃ©`→`Nestlé`). Verify: `grep -rl 'â\|Ã\|Â§'` returns nothing.
3. **Categorise** into the taxonomy (`knowledge-graph` · `research` · `sales` · `content` · `workflow-ops` · `vault-hygiene`). If none fits, **add a category** (folder + `_category.md`) — richer taxonomy over forcing a bad fit. Pair related skills in the same category (e.g. `sync-claude-sessions` + `recall`).
4. **Convert ONLY the SKILL.md frontmatter** to the house schema (`id`, `aliases`, `name`, `category`, `description`, `triggers`, `tags`, `related`, `status`, `version`, `created`, `updated` + optional `requires`/`environment`/`assets`/`scripts`/`workflows`/`schema`). **Leave the body untouched** for copied skills. **Preserve** the original `{name, description}` (as a comment) and any functional fields — e.g. Claude Code slash-command `argument-hint` / `allowed-tools`. Set `aliases: [<slug>]` so `[[wikilinks]]` resolve despite every file being `SKILL.md`.
5. **Extend the schema only if needed, and only additively** (edit README): a new subfolder type or a new optional frontmatter key. Never lower or rename existing keys.
6. **Register:** add one INDEX.md row under the category; bump the header counts (skills · populated categories); update the category's `_category.md` skill list.
7. **Verify:** `SKILL.md files == INDEX skill rows` (rows under the category sections only — the trailing *Shared modules* table is excluded); every indexed path resolves; `aliases` present; (copied) byte-identical + exec bit intact (`ls -l`); frontmatter conforms; encoding clean.

**Standing evals (run after any skill add/rename/trigger change)**
- **Frontmatter lint (fix-loop to 0):** `python3 resources/skills/vault-hygiene/skill-library-maintenance/scripts/lint_frontmatter.py` checks YAML parse, required keys, id/category vs folder, `modules:` against MODULES.md, and `related:` resolution. Exit 0 iff `errors=0`. A non-zero result blocks the change.
- **Routing eval (autoresearch loop on INDEX triggers):** `python3 resources/skills/vault-hygiene/skill-library-maintenance/scripts/routing_eval.py --log <STATE_ROOT>/routing-results.tsv`.
- **Spec exportability (lint rule):** `python3 resources/skills/vault-hygiene/skill-library-maintenance/scripts/spec_export.py check` converts every skill to Agent Skills spec frontmatter in memory and runs the checks of Anthropic's `quick_validate.py` and the `skills-ref` validator on the rendered file. It checks: only the six spec keys at the top level; `name` a slug equal to the folder; description 1–1,024 characters with no `<`/`>`; `compatibility` ≤500. Triggers that don't fit in the description are a warning, not an error. Baseline 2026-11-02: errors=1 (`linkedin-viral-scheduler`'s description, 1,933 chars), warnings=7. New or edited skills must not add errors.
  - Mapping: `id`→`name`; triggers folded into the description ("Use when: …") while it fits; `environment`→`compatibility` when ≤500 chars; `allowed-tools` stays top level; the display `name` becomes `metadata.title`; every other key moves under `metadata` with its name and YAML type unchanged. Common angle forms are rewritten (`>=`→`≥`, `<path>`→`{path}`).
  - `export SLUG… --out DIR` writes a complete skill folder per slug: the converted SKILL.md, the body and all bundled files byte-identical.
  - **In-place migration is not decided.** Pilot run on 5 skills (`output/.runs/20261102-skill-spec-export/`): export only, sources unchanged, awaiting the principal's decision.
- **Preselector eval (in-session routing hint):** `python3 scripts/skill_router.py eval` prints recall@5 per split. Baseline 2026-10-23: train 17/25, held-out 11/17. Trigger edits (German and email vocabulary are the main misses) are judged on **both** evals: `routing_eval.py` measures an explicit dispatcher reading the whole INDEX, which arXiv:2610.18522 shows stays robust at scale; the preselector measures what an in-session prompt actually gets shown.
  - One headless dispatcher call reads only INDEX.md and routes 42 real past prompts. The golden set lives at `resources/skills/_evals/routing.tsv` (gitignored: real prompts carry client names), split 28 train / 14 held-out.
  - **Loop card** (per `_shared/autoresearch-loop.md`): mutate one trigger or description cell per candidate and keep the SKILL.md `triggers:` in sync. Guards: held-out mean must not drop, and INDEX may grow at most +5%.
  - **Noise is ±3 train prompts between identical runs**, so score each candidate on the mean of 2 runs or more. Never tune toward a held-out miss.
  - Baseline 2026-10-09: train 23.5/28, held-out 12/14. After the narrative-builder scope fix: train 26.5, held-out 13. Log: `output/.runs/20261009-loops-build/`.
  - **Extend the set only with real prompts,** never invented ones, and re-baseline after any change to the set.

**Optimizations/Gotchas**
- **Superseded 2026-10-23 for the session context:** the full INDEX no longer fits the 10,000-character hook cap, so sessions get a compact slug list plus a per-prompt preselection (`scripts/skill_router.py`); the rule below still holds for INDEX.md itself.
- **Don't slim the always-on INDEX by cutting triggers or descriptions: tested and failed on 2026-10-11.** The idea came from Pi 1.0's "minimal core" (system prompt plus tools under 1k tokens). `scripts/lean_index.py` generates trimmed views of INDEX.md; `routing_eval.py --index <view>` scored them against the full INDEX on opus.
  - Full INDEX (64 KB): 40/50 and 38/50 on two runs, so noise is about ±2.
  - All triggers + 110-char descriptions (36 KB): 36/50. All triggers + 200 chars: 35/50. 8 triggers + 80 chars (28 KB): 35/50. 12 triggers, no description: 33/50. 6 triggers, no description (18 KB): 28/50.
  - Why it fails: the long descriptions are what separate near-twin skills (`deliverable-index` vs `vault-maintenance`, `skill-library-maintenance` vs `vault-maintenance`, `agent-architecture` vs `agentic-service-evaluation`).
  - Re-test only after the near-twins have sharper boundaries; the full log is in `output/.runs/20261011-lean-index/routing-results.tsv`.
  - The always-on cost is smaller than the 16k tokens suggest, because the index is the same at every session start and comes from the prompt cache.
- **INDEX.md is the source of truth for lookup** — a skill missing from it is invisible. Update it *in the same change* as any add/rename/remove.
- **Alias collision** — because every skill file is `SKILL.md`, bare `[[SKILL]]` is ambiguous; the `aliases: [<slug>]` key is what makes cross-skill links resolve.
- **External tool deps are declared, not installed** — record CLIs/plugins under `requires` (`tools` mandatory · `optional`/`cli`/`bundled-skills`/`obsidian-plugins`); the user installs them (e.g. `nlm`, `notebooklm`, `qmd`). Note the correct install path (`uv tool install …` sidesteps fragile system Python) and that docs may name stale commands (`nlm login`, not `nlm auth login`).
- **Format-compatibility at *use* time (not import)** — a copied script may expect a different JSON shape than the CLI emits (e.g. NotebookLM's flat array vs the `{notebook_id, sources[]}` the import script wants); wrap/map before calling. This is a usage note, not an import fix — never edit the script.
- **Schema extensions accumulated so far** (all additive): subfolders `references/` (deep prose), `assets/` (binaries/examples/fonts), `scripts/` (executable code), `workflows/` (routed sub-procedures), `schema/` (validation vocab, e.g. `tags.yaml`); frontmatter `version` may be semver (`"7.7"`), plus `requires` / `environment` / `assets` / `scripts` / `workflows` / `schema` manifests.
- **Scale (documented in README, not pre-built)** — when a category exceeds ~200 skills, split into sub-indexes; then shard into prefix/hash buckets; optionally generate `index.json`. Same structure, no migration.
- **Spec export, known losses (pilot 2026-11-02):** YAML comments in the frontmatter are dropped. `metadata` values keep their lists and maps, although the spec text says string→string. Both reference validators accept that today; a stricter loader may not (a bet). Source quirks pass through unchanged, e.g. `recall`'s `argument-hint: [a|b]` is a YAML list, not a string.
- **Reproduce-and-clean is lossy** — prefer copy-verbatim whenever the files exist on disk. Only distil/condense when reproducing pasted text, and preserve every hard rule, gate, and example.
