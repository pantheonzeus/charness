---
id: legacy-seam-mapping
aliases: [legacy-seam-mapping]
name: "Legacy Seam Mapping & Slice Sequencing"
category: technology
description: Decompose a legacy system for a Strangler Fig program — map business capabilities onto the code and data, find the seams where traffic can be intercepted, score each candidate slice on value × risk × coupling, and return a ranked slice sequence with a thin, low-risk first slice.
triggers: [seam mapping, find the seams, decompose the monolith, legacy assessment, capability map, slice the legacy, which part first, migration sequencing, dependency map, bounded contexts, legacy discovery, domain decomposition, AI reverse engineering, legacy code comprehension, business rule extraction, Event Storming]
tags: [technology, architecture, modernization, legacy, strangler-fig, domain-driven-design]
related: ["[[strangler-fig-program]]", "[[strangler-transition-architecture]]", "[[strangler-slice-cutover]]", "[[initiative-prioritizer]]"]
modules: [evidence-backed-answering]
status: active
version: 2
created: 2026-10-10
updated: 2026-10-10
requires:
  optional: [code-graph / static-analysis tooling, LLM-assisted code comprehension (e.g. CodeConcise-style AST graph + LLM, AWS Transform, AI/works)]
environment: "Best with read-only repo access and production telemetry (request logs, DB query stats). Without them, it runs as stakeholder interviews plus docs, and every dependency is tagged as inference."
references: [../strangler-fig-program/references/pattern-catalog.md, ../strangler-fig-program/references/templates.md]
---

# Legacy Seam Mapping & Slice Sequencing

## Contract
- **Input:** the legacy system plus whatever exists — code/repo, architecture docs, DB schema, API/request logs, batch job lists, interfaces to other systems, and access to the people who run it.
- **Output:** a seam map at `output/<YYYYMMDD>-<slug>-seam-map.md` (sections per [templates.md](../strangler-fig-program/references/templates.md) §3): a capability map, a seam inventory, a data-ownership matrix, a scored slice list, and the recommended sequence. It feeds the slice register owned by `strangler-fig-program`.
- **Allowed tools/artifacts:** read-only code and schema reading, telemetry queries, interview notes. No production changes.
- **Done when:** every capability is mapped to its code areas and the tables it reads or writes; every candidate slice has a score with the evidence behind it; and slice 1 is chosen with a written reason.

## Triggers/Context
- Step 3 of `strangler-fig-program`, or standalone when someone asks "where do we start with this monolith?"
- Re-run at slice boundaries when the program re-plans.

## Core Blueprint
1. **Map capabilities, not modules.** List the 8–20 business capabilities the system serves (e.g. pricing, order capture, invoicing, reporting), in business language and confirmed with a business owner. Get them from the business side with Event Storming or a value stream map, not from the code's package structure. Code shows how the legacy is built, not what the business needs from it. Then map each one to its code areas, entry points (UI screens, APIs, batch jobs, file drops) and data.
2. **Inventory the seams.** For each capability, record where its requests could be intercepted: HTTP routes, UI pages, API operations, message queues, batch triggers, file interfaces. Pick the seam type from [pattern-catalog.md](../strangler-fig-program/references/pattern-catalog.md) §2. A capability with no interceptable entry point needs branch by abstraction inside the code. Note that explicitly, because it costs more.
3. **Map data ownership.** Build a capability × table matrix (R / W / RW). Shared tables written by several capabilities are the real coupling. Mark them, and also mark external systems that read the legacy database directly.
4. **Speed up comprehension with AI, then verify.** When the codebase is large or nobody understands it any more, build a code graph (AST/call graph) and let an LLM draft capability summaries, business rules and specs over it. Thoughtworks' CodeConcise is the reference approach: at one COBOL/IDMS client it cut reverse engineering from ~6 to ~2 weeks per 10k-line module. That's one engagement, so plan with it as a bet, not a benchmark. Every AI-derived rule or dependency stays tagged as inference until a domain expert or runtime evidence (step 5) confirms it. Find dead code with static analysis plus traffic data, not with the LLM. Compare the AI capability map against the one from step 1. The places where they disagree are the findings.
5. **Measure, don't guess.** Pull the volumes (requests/day per entry point, rows/day written, batch runtimes) and change frequency (commits or tickets per area in the last 12 months). Tag any figure without telemetry as inference in the evidence register.
6. **Score candidate slices** (1–5 each, with the evidence written next to the score):
   - **Value:** business outcome unlocked, change pressure, legacy cost removed.
   - **Risk:** revenue or compliance exposure if it goes wrong, and how much of the logic is undocumented.
   - **Coupling:** shared-write tables, synchronous calls into other capabilities, and external consumers.
   Priority ≈ value ÷ (risk × coupling). Don't trust the formula blindly. Sanity-check the top 5 by hand.
7. **Choose slice 1 and the sequence.** Slice 1 is thin, valuable, low-coupling, and **exercises the full plumbing** (interception, data sync, rollback). Usual good first slices are read-heavy capabilities, a new product line, or an edge capability with its own data. Usual bad ones are core transaction posting and anything that owns the master data. Order the rest so each slice removes coupling for the next.
8. **List the unknowns.** Logic nobody can explain, dead code that might not be dead, and batch jobs with no owner. Each one gets an owner and a discovery task, because these are where the program schedule goes wrong.

## Optimizations/Gotchas
- **Decomposing by technical layer is the most common mistake.** "Migrate the UI first, then the DB" is a rewrite in slow motion. Slice vertically by capability.
- **Telemetry beats interviews.** People remember the features they use and forget the batch job that runs at 03:00 and feeds the regulator. Check request logs and the job scheduler.
- **Dead code is a gift.** Capabilities with zero traffic in 90 days can often just be switched off — the cheapest slice there is. Confirm with the business owner first, and archive the data.
- **Don't let AI comprehension turn into AI translation.** Once the specs exist, the temptation is to have the agent transpile the module. That carries the legacy design into a new language. Rebuild from the confirmed spec, scoped by the slice's outcome.
- **Shared-write tables decide the sequence.** If two capabilities write the same table, either move them together or put a single owner plus sync in front of the table first.
