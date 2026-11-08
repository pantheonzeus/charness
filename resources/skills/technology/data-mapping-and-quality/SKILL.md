---
id: data-mapping-and-quality
aliases: [data-mapping-and-quality]
name: "Data Migration — Profiling, Mapping & Cleansing"
category: technology
description: Turn source data into a signed source-to-target mapping. Profile the real data (script-backed, DuckDB, any file or database), then write field-level mapping rules, value maps and a key crosswalk. Cleansing decisions are logged per defect class (fix at source / fix in flight / exclude / accept) with a business owner, and the transform is designed to be idempotent and re-runnable. Scales from a one-sheet mapping (T1) to change-controlled specs per business object (T4).
triggers: [data mapping, source to target mapping, mapping spec, field mapping, data profiling, profile this data, data quality, data cleansing, data cleanup before migration, dedupe, duplicates, key mapping, ID crosswalk, value mapping, reference data mapping, transformation rules, ETL design, data dictionary, orphan records, golden record, merge customer records]
tags: [technology, data-migration, data-quality, etl, mapping]
related: ["[[data-migration-strategy]]", "[[migration-reconciliation]]", "[[migration-cutover-runbook]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
requires:
  tools: []
  optional: [uv (runs scripts/profile.py with duckdb pulled on demand), read-only DB credentials]
  python: [duckdb]
environment: "Profiling runs locally via `uv run --with duckdb`. Attaching Postgres/MySQL/SQLite makes DuckDB download that extension on first use, which needs network. Offline, profile a CSV/Parquet extract instead."
scripts: [scripts/profile.py]
references: [references/mapping-template.md]
---

# Data Migration — Profiling, Mapping & Cleansing

## Contract
- **Input:** source access (read-only DB connection or extracts), the target data model, and the plan from [[data-migration-strategy]] (tier, scope table, owners). Without a plan, run a T1-sized version and state the tier you assumed.
- **Output:** per migrate-object, (1) a profile report `output/<YYYYMMDD>-<slug>/profile-<object>.md` produced by `scripts/profile.py`, (2) a mapping spec `output/<YYYYMMDD>-<slug>/mapping-<object>.md` per [mapping-template.md](references/mapping-template.md), and (3) a cleansing decision log in the same spec. Optionally the transformation code (SQL/dbt/Python) if asked.
- **Allowed tools/artifacts:** read-only queries and `profile.py` against sources, the target schema, and the conversation. Never write to a source system. Source-side cleansing is executed by the data owner's team, not by this skill.
- **Done when:** every target field of every in-scope object has a mapping row (a rule, a default, or an explicit "not populated" with a reason); every mandatory target field has a non-null source or default; every defect class from the profile has a decision and an owner; the key strategy (natural key, surrogate + crosswalk) is stated; and the spec carries the owner's sign-off status.

## Triggers/Context
- After the plan exists, or directly for "map this to that" / "how dirty is this data" questions.
- Run profiling **before** mapping workshops, so the workshop argues about real values instead of the data dictionary.

## Operating principles (enforceable)
1. **Profile, then map.** Every mapping rule that touches a value domain (codes, statuses, units) cites the profile's actual distinct values. A value map that doesn't cover every observed value is incomplete. Unmapped values need an explicit default or reject rule.
2. **Map target-backwards.** Start from every target field and find its source. Source-forwards mapping misses mandatory target fields and defaults, and those surface as load failures at mock 1.
3. **Every defect class gets one of four decisions:** *fix at source* (preferred, because it fixes the business process too), *fix in flight* (a deterministic transform rule), *exclude* (with a count and a reason, reconciled as an expected difference), or *accept* (load as-is, with the owner's explicit OK). "We'll clean it in the new system" is *accept* and must be recorded as such.
4. **Keys are designed, not inherited.** State the target key strategy. If keys are re-numbered or sources are merged, build a **crosswalk table** (source system, source key → target key) that persists after go-live. Reconciliation, integrations and audit all need it.
5. **Transforms are deterministic and idempotent.** The same extract produces the same output every run. No `now()`, random IDs or row-order dependence without a seed or rule. A re-run upserts instead of duplicating.
6. **Land raw first.** Extract into a staging area unchanged (plus load timestamp and source ID) before any transformation, so each mock can be diffed against the raw extract and defects traced to the source or the rule.

## Core Blueprint
1. **Profile each object:** `uv run --with duckdb resources/skills/technology/data-mapping-and-quality/scripts/profile.py <source> --key <business key> --out output/<run>/profile-<object>.md`. The source can be a file path, an attached table (`--attach "postgresql://… AS src (TYPE postgres, READ_ONLY)"` → `src.schema.table`) or a `"(SELECT …)"` subquery. For very large tables use `--sample N` for the shape, then run exact key checks on the full table.
2. **Read the profile for migration defects:** duplicate or NULL business keys; orphans (FKs with no parent, checked with an anti-join per relationship); mixed case or padding in codes; blank vs NULL; sentinel values (`1900-01-01`, `9999`, `N/A`); free text in coded fields; mixed units or currencies; encoding damage (`Ã¼` instead of `ü`); timezone-less timestamps. Log each defect class with its row count.
3. **Write the mapping spec** target-backwards per [mapping-template.md](references/mapping-template.md): target field, type/length, mandatory flag, source field(s), rule (direct / value map / lookup / derive / default / constant / not populated), the rule as executable pseudo-SQL, and test cases.
4. **Value maps and reference data:** one table per coded domain (source value → target value), covering 100% of profiled values, versioned, and owned by the business.
5. **Key strategy and crosswalk:** natural vs surrogate key; collision handling when merging sources (prefix, offset or a match-and-merge rule); survivorship rules for golden records (which source wins per field).
6. **Cleansing decision log:** defect class · count · decision (source / in-flight / exclude / accept) · owner · due by mock N.
7. **Review and sign-off:** walk the spec with the business owner, record their decision per open item, then freeze the spec version for the next mock. In T3+, changes after the freeze go through change control.

## Optimizations/Gotchas
- **The data dictionary lies.** A `status` documented as 4 values typically holds 11 in production. The profile's top values are the truth.
- **Length and type truncation fails silently.** Compare the source's max length (profile `Len min–max`) against target field lengths before mock 1, and do the same for numeric precision and scale.
- **Blank ≠ NULL ≠ sentinel.** Decide per field. DuckDB's CSV reader treats empty fields as NULL by default, so profile extracts with that in mind.
- **Timezones.** Decide whether timestamps are stored as UTC, and how local times across a DST change are converted. Write the rule into the spec.
- **Golden-record merges need business rules.** Survivorship ("CRM wins on email, ERP wins on billing address") is a business decision. Never let the engineer pick it silently.
- **Personal data in profiles.** Top-value lists can expose names and emails. Treat profile reports as confidential, or profile against a masked extract.
