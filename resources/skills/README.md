# Skill Library

The agent's evolved capabilities, one folder per skill. This replaces the old flat `skills.md` ledger so every skill can be optimized in isolation and the library can scale.

## How lookup works (progressive disclosure)
Never load the whole library. Three tiers:
1. **Scan [`INDEX.md`](INDEX.md) first** — a compact registry (name · category · trigger keywords · description · path). Cheap to read every task.
2. **Open the matched `SKILL.md`** — full instructions for the one skill that fits.
3. **Load `reference.md` / `examples/`** inside that skill's folder only if the task needs the deep material.

This mirrors the Agent Skills pattern: lightweight metadata at startup, full instructions on match, deep material on demand.

## Layout
```
skills/
├── README.md            # this file — the contract
├── INDEX.md             # registry, scanned first
├── MODULES.md           # the module vocabulary (values for the modules: frontmatter key)
├── _template/SKILL.md   # copy this to add a skill
├── _shared/             # cross-skill modules invoked by the Charter (evidence gate, handoff, self-evolution, verifier separation, change-manifest + CHANGE_LOG.md, autoresearch-loop)
└── <category>/
    ├── _category.md     # scope of the category
    └── <skill-slug>/
        ├── SKILL.md      # the skill (frontmatter + body)
        ├── references/   # optional deep prose (or a single reference.md)
        ├── assets/       # optional bundled files: fonts, reference examples, templates, data
        ├── scripts/      # optional executable code the skill runs (Python, bash, …)
        ├── workflows/    # optional routed sub-procedures (SKILL.md dispatches to these by intent)
        └── schema/       # optional validation schemas / controlled vocabularies (e.g. tags.yaml)
```

## Taxonomy (canonical categories)
| Category | Holds |
|---|---|
| `knowledge-graph` | People, linking, relationships, vault graph structure |
| `research` | Sourcing, citations, distillation, competitive analysis |
| `sales` | Proposals, bids, tenders, pitches, competitive positioning |
| `content` | Talks, drafts, tutorials, hooks, angles |
| `workflow-ops` | Automation, productivity processes, recurring pipelines |
| `technology` | Hands-on technical architecture and engineering method — cloud/system design and review, AI agent and multi-agent platform architecture, migration, infrastructure cost and exit modelling |
| `strategy` | Strategy-consulting analytical frameworks — diagnosis, market/competitive intelligence, strategic choice & economics, operating model & execution, risk/value governance, executive alignment |
| `service-design` | Principal-level service design method — framing, discovery research, journeys, blueprints, ecosystem maps, prototyping/pilots, co-design, service measurement, plus the agentic layer (human–agent blueprints, agent-ready services, agentic evaluation) |
| `business-design` | Business designer method — the viability lens: opportunity framing, value propositions, business models (incl. servitization, platform/ecosystem, AI-native), concept-stage viability models and business experiments, plus agent-augmented discovery and AI opportunity portfolios |
| `vault-hygiene` | Obsidian structure, tagging, naming, maintenance |

A new category gets a folder + `_category.md` when its first skill lands. Reserved categories may be empty.

## SKILL.md contract (frontmatter schema)
```yaml
---
id: skill-slug                    # kebab-case, matches folder name
aliases: [skill-slug]             # so [[wikilinks]] resolve (every file is SKILL.md)
name: "Human-Readable Skill Name"
category: knowledge-graph
description: One line — used for INDEX matching and relevance.
triggers: [keyword, phrase, "another phrase"]
tags: [tag1, tag2]
related: ["[[other-skill-slug]]"]
status: active                    # active | draft | deprecated
version: 1                        # integer, or a semver string like "7.7" for heavily-iterated skills
created: YYYY-MM-DD
updated: YYYY-MM-DD
# --- optional keys (only when the skill needs them) ---
modules: [file-backed-state, evidence-backed-answering]  # harness modules the skill uses; values from MODULES.md
requires:                         # external dependencies; omit for self-contained skills
  tools: [web_search, web_fetch]  #   always-needed tools
  optional: [apify, firecrawl]    #   nice-to-have; skill must degrade gracefully without them
  bundled-skills: [pdf]           #   other skills/plugins it loads
environment: "Where it runs best; note graceful-degradation path"
assets: [assets/fonts/BrandFont.ttf]    # bundled files shipped in the skill's assets/ folder
references: [references/reference.md]  # deep-prose files under references/, listed for discoverability
vault_writes: [cbrain/Clients/*, cbrain/projects/*]  # vault paths the skill creates/edits (Charter §6); omit = writes nothing to the vault
---
```
Body: every skill opens with a **Contract** block — input, output (+ where it lands), allowed tools/artifacts, and the observable done-when condition (NLAH research §3.2 principle #1: this prevents later sections from becoming vague advice). After the Contract, simple skills use the three-section format (**Triggers/Context**, **Core Blueprint**, **Optimizations/Gotchas**). Richer skills may use a fuller structure (e.g. *What this is for*, *Inputs*, *Operating principles*, *Output structure*, *Worked patterns*) and push deep material into `reference.md`, a `references/` subfolder, and bundled `assets/` — see `sales/audience-of-one-report/` for the maximal example (multi-file references, bundled font, external-tool dependencies, semver version). This is forward-facing: new and re-optimized skills adopt the Contract block; existing skills gain one the next time they're touched, not via a blanket retrofit.

### Optional keys — when to use them
- **`version` as semver** — heavily-iterated skills (many observed-failure fixes) may outgrow integer versions; a string like `"7.7"` is allowed. Bump on every optimization.
- **`requires`** — declare tools/plugins/bundled-skills the skill calls. Split `tools` (mandatory) from `optional` (must degrade gracefully). This lets a reader know upfront whether the environment can run the skill. Sub-keys are open and additive as needs arise: `cli` (external CLIs), `bundled-skills`, `obsidian-plugins`, `python` (packages pulled on demand, e.g. `pyobjc-framework-EventKit` via `uv run --with`).
- **`environment`** — one line on where the skill runs best and how it degrades elsewhere (e.g. local-MCP skills that only see plugins in Cowork/Desktop).
- **`assets`** — list bundled files under the skill's `assets/` folder (fonts, reference examples, templates). Deep reference *prose* goes in `references/`; binary/example *files* go in `assets/`.
- **`references`** — list deep-prose files under the skill's `references/` folder (or a cross-skill reference path) so they're discoverable from frontmatter without opening the body.
- **`scripts` / `workflows` / `schema`** — script-backed skills list their executable files (`scripts/`), routed sub-procedure docs (`workflows/`), and validation schemas / controlled vocabularies (`schema/`, e.g. a `tags.yaml`). Import these by **copying the folder verbatim** (`cp -R`, which preserves the executable bit) so the code and the SKILL.md's internal relative paths stay intact — never retype scripts. Keep the upstream folder structure; convert only the SKILL.md frontmatter.
- **`vault_writes`** — the vault (`cbrain/`) paths the skill creates, edits or appends to, as repo-relative globs (`*` crosses `/`), including what its scripts write. Per Charter §6 a skill **without** this key writes nothing to the vault and ends with a *Proposed vault links* list instead. Declare the narrowest globs that cover the skill. A headless agent's hook-enforced `write_scopes:` (in `.claude/agents/<job>.md`) must stay inside the `vault_writes:` of the skill it runs.
- **`modules`** — the named harness modules the skill relies on (e.g. `file-backed-state`, `evidence-backed-answering`, `self-evolution`), drawn from [`MODULES.md`](MODULES.md). This is analysis metadata, not an import: it makes explicit which reusable mechanisms a skill uses so they can be compared and ablated. Declare only what the skill genuinely uses. The reusable procedures live in `_shared/` and the Charter.

## Adding a skill
1. Copy `_template/SKILL.md` to `<category>/<skill-slug>/SKILL.md`; fill frontmatter + body.
2. Add one row to `INDEX.md` under the right category, and add the skill's slug to that category's `_category.md` **Skills:** line.
3. Cross-link via `related:` (use the other skill's `id`).

## Writing NLAHs (enforceable language)
Prefer short clauses, concrete conditions, and explicit artifacts over vague exhortations. Phrases like "be careful," "think deeply," or "act like an expert" are weak policy — they don't define observable behavior (NLAH research §3.2 principle #5). Replace each with a clause naming the artifact or check: not "be careful with sources" but "cite the source file for every numeric claim"; not "verify thoroughly" but "run the verifier before finalizing and record its verdict."

## Optimizing a skill
Edit its `SKILL.md` in isolation; bump `version` and `updated`. Move overflow detail into a `reference.md` beside it rather than bloating the body.

## Index-maintenance rule
`INDEX.md` is the source of truth for lookup. **Any** add / rename / remove / recategorize MUST update `INDEX.md` in the same change — a skill missing from the index is invisible. Update the category's `_category.md` **Skills:** line too — every existing category file maintains one, and a skill absent from it is invisible to anyone reading the category scope directly instead of the root index.

## Path to 1M skills (grow into, don't pre-build)
- **>~200 skills in a category** → split into subcategories and give the category its own `INDEX.md`; the root `INDEX.md` becomes an index-of-indexes.
- **Beyond that** → shard a subcategory into prefix/hash buckets (`a-f/ g-m/ …` or `00/ 01/ …`) so no directory holds thousands of entries.
- **Programmatic scale** → generate a machine-readable `index.json` (or SQLite) from frontmatter. Same structure — no migration required.
