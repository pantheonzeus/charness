---
id: migration-reconciliation
aliases: [migration-reconciliation]
name: "Data Migration — Reconciliation & Acceptance"
category: technology
description: Prove a migration is correct. Agree acceptance thresholds with data owners before mock 1, then run a layered reconciliation (row counts → key integrity → key diff → field-level diff → control totals → business-rule tests) with a script-backed DuckDB verifier that compares any file or database to any other and exits non-zero on FAIL. Explain every difference as a defect or an approved exclusion, and package the signed result as audit evidence. T1 needs counts and totals; T4 needs an independent verifier and an evidence pack.
triggers: [reconciliation, reconcile, data reconciliation, migration validation, validate the migration, verify migrated data, data diff, compare source and target, row counts match, control totals, checksum, migration testing, acceptance criteria migration, mock load results, did everything migrate, missing records, audit evidence migration, sign-off data migration]
tags: [technology, data-migration, testing, verification, audit]
related: ["[[data-migration-strategy]]", "[[data-mapping-and-quality]]", "[[migration-cutover-runbook]]"]
modules: [file-backed-state, evidence-backed-answering, verifier-separation]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
requires:
  tools: []
  optional: [uv (runs scripts/reconcile.py with duckdb pulled on demand), read-only DB credentials on both sides]
  python: [duckdb]
environment: "Runs locally via `uv run --with duckdb`. Attaching Postgres/MySQL/SQLite downloads a DuckDB extension on first use, which needs network. Offline, reconcile extracts (CSV/Parquet) or a DuckDB file instead. Both sides are pulled into DuckDB, so for tables beyond a few hundred million rows reconcile per partition (date, tenant) via subqueries."
scripts: [scripts/reconcile.py]
---

# Data Migration — Reconciliation & Acceptance

## Contract
- **Input:** source and target access (or extracts taken at the same cut-off), the mapping spec's key strategy and expected differences ([[data-mapping-and-quality]]), and the tier from [[data-migration-strategy]].
- **Output:** per object per mock, a reconciliation report `output/<YYYYMMDD>-<slug>/recon-<object>-mock<n>.md` (+ `.json`) from `scripts/reconcile.py`, a business-rule test result, and a one-page acceptance summary `output/<YYYYMMDD>-<slug>/acceptance-mock<n>.md` (object · verdict · open differences · explained differences · signer). For T4, an evidence pack folder containing the reports, extract timestamps, script version and sign-offs.
- **Allowed tools/artifacts:** read-only queries on both sides, `reconcile.py`, and the conversation. Never "fix" target data to make a check pass. A fix is a pipeline change followed by a re-run.
- **Done when:** every in-scope object has a reconciliation verdict for the mock; every non-zero difference is either a logged defect or matches a pre-approved expected difference with a count; business-rule tests have run; and the acceptance summary records the owner's decision.

## Triggers/Context
- Defining acceptance criteria (before mock 1), after every mock load, at cutover before the go/no-go, and post go-live for delta loads.
- Also on its own: "do these two tables match?" when any two datasets need comparing.

## Operating principles (enforceable)
1. **Thresholds are agreed before data exists.** Acceptance criteria per object (allowed missing / extra / field mismatches, numeric tolerance, mandatory business rules) are written and signed before mock 1. Setting thresholds after seeing the results is not acceptance.
2. **Layered, cheapest first.** Counts → key integrity → key diff → field diff → control totals → business rules. A failure in an earlier layer is fixed before a later layer is interpreted (e.g. duplicate keys inflate field-diff counts).
3. **Compare in target terms.** Express the source-side transformation (filters, value maps, unit conversion, dedupe) as a subquery passed to `--source`, so the diff measures *defects*, not intended changes. Each `--max-*` allowance traces to a line in the mapping spec's expected-differences table.
4. **Every difference is explained.** A difference is either a defect (with an owner and a fix by mock N) or an approved exclusion (with a count that matches the spec exactly). "Close enough" is not a verdict.
5. **Business rules prove meaning, not just bytes.** Field equality doesn't prove that open-item balances, stock valuations or the number of active contracts per customer still hold. Per object, write 3–10 business-rule queries that run on both sides with the owner's expected result (e.g. AR open balance per company code equals the trial balance).
6. **The verifier is separate from the builder.** In T3+, the reconciliation is run (or at least re-run) by someone who did not build the pipeline, and the script version and extract timestamps are recorded with the result.

## Core Blueprint
1. **Write the acceptance criteria** per object: key, compared columns, ignore list (technical columns such as load timestamps), numeric tolerance, string normalization (`--trim`, `--ci`) and why, allowed missing/extra counts from the expected-differences table, the business-rule list, and the signer.
2. **Take consistent snapshots.** Extract both sides at a known cut-off (source frozen, or a CDC position/LSN recorded). Reconciling a moving source against a target produces noise, not findings.
3. **Run the verifier per object:**
   ```bash
   uv run --with duckdb resources/skills/technology/migration-reconciliation/scripts/reconcile.py \
     --source "(SELECT … FROM src.legacy.customers WHERE active = 'Y')" \
     --target tgt.public.customer \
     --attach "postgresql://ro@legacy/erp AS src (TYPE postgres, READ_ONLY)" \
     --attach "postgresql://ro@new/app AS tgt (TYPE postgres, READ_ONLY)" \
     --key cust_no --map cust_no=customer_id,name=full_name --ignore load_ts \
     --tolerance 0.005 --out output/<run>/recon-customer-mock2.md --json output/<run>/recon-customer-mock2.json
   ```
   Exit codes: `0` PASS, `1` FAIL, `2` usage/connection error, so it can gate a CI job or a cutover script.
4. **Triage every FAIL** into defect classes (mapping rule wrong, source data defect, load failure, expected-but-unlisted exclusion). Attach the sample keys and route each to its owner. Re-run after the pipeline fix, never after manual edits to the target.
5. **Run the business-rule tests** on both sides and record actual vs expected per rule.
6. **Write the acceptance summary** and get the owner's decision per object: accept / accept with listed defects / reject.
7. **Trend across mocks.** Track defect counts per object per mock. Defects should converge to zero before the dress rehearsal. A count that doesn't fall is a pipeline or source-process problem, so escalate it.

## Optimizations/Gotchas
- **Matching row counts prove almost nothing.** One missing record plus one duplicate still gives equal counts. Always run the key diff.
- **Type drift creates false mismatches.** `1.50` vs `1.5`, `DATE` vs `VARCHAR`, `CHAR(10)` padding. The script casts the target to the source type and counts uncastable values as mismatches. Use `--trim` and `--tolerance` deliberately and record why.
- **Floating-point sums rarely match exactly.** Use a tolerance on control totals for float columns, or sum DECIMALs instead.
- **Large tables:** split by partition with subqueries (`WHERE created >= '2024-01-01' AND created < '2025-01-01'`) and run per slice. Hash-bucket diffing (compare per-bucket counts and checksums, then drill into mismatching buckets) is the technique for billions of rows, but it isn't built into this script. Add it only when a slice-by-slice run is too slow.
- **Production credentials:** use read-only accounts on both sides. The script only issues SELECTs, but credentials are a blast radius.
- **Confidential output.** Mismatch samples contain real records, so store reports with the same access controls as the data.
