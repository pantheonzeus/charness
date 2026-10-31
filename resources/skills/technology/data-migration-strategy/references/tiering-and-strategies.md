# Tiering & Strategy Selection

## The nine complexity dimensions
Score each 1–4 and cite the evidence (profiling output, interview, document). **Tier = the highest score.** If two or more dimensions score 4, write that into the risk list as a compounding risk.

| # | Dimension | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| 1 | **Volume** (largest object / total) | < 1M rows, < 10 GB | < 100M rows, < 500 GB | < 5B rows, < 10 TB | larger, or load window < full-copy time |
| 2 | **Source count** | 1 | 2–3, same tech | several, mixed tech | many incl. files/manual/mainframe |
| 3 | **Schema distance** | identical | renames, type changes | restructure (split/merge entities) | different data model (e.g. custom → ERP standard) |
| 4 | **Transformation logic** | none / 1:1 | lookups, value maps | derivations, dedupe, key re-numbering | business-rule recalculation (balances, pricing, open items) |
| 5 | **Data quality** (from profiling) | clean | minor issues, fix in flight | material dupes/orphans/invalid values | unknown, or quality so poor that business decisions are needed |
| 6 | **Downtime budget** | days | a weekend | hours | minutes / zero |
| 7 | **Integrations** to cut over | 0 | 1–3 | 4–15 | > 15, or undocumented |
| 8 | **Regulatory / audit** | none | GDPR personal data | audit trail required (SOX, GoBD, HGB/AO retention) | validated system (GxP), banking/insurance (DORA, BAIT/VAIT), KRITIS |
| 9 | **Business criticality** | internal convenience | department process | revenue or customer-facing | safety-, money- or licence-to-operate |

*Thresholds are heuristics, not standards. Adjust them for the client and record the adjustment in EVIDENCE.md.*

### Tier archetypes
- **T1 Simple:** a spreadsheet or CSV into a SaaS tool, a SQLite → Postgres move, a small CRM import. One person, days.
- **T2 Standard:** one database to one database with modest schema change, or a version upgrade or platform move with a weekend window. A small team, weeks.
- **T3 Complex:** heterogeneous engines (e.g. Oracle → Postgres), schema redesign, merging sources, real quality debt, hours of downtime. A dedicated team, months.
- **T4 Critical:** ERP, core banking, policy admin, MES/PLM or mainframe replacement; many integrations; regulated; minutes of downtime. A programme with multiple waves.

## Strategy patterns

| Strategy | How it works | Choose when | Avoid when | Rollback |
|---|---|---|---|---|
| **Big bang (offline)** | Freeze source → full extract/transform/load → reconcile → switch | Timed full mock + reconciliation + rollback buffer fits the downtime budget; few integrations | Window too short; T4 criticality with no fallback | Re-point to source; source unchanged until the point of no return |
| **Phased / waves** | Migrate by object, site, country, tenant or customer cohort | Data partitions cleanly; you want an early, low-risk pilot wave | Heavy cross-partition references (orders across all sites) | Per wave; earlier waves stay live |
| **Trickle / CDC (online)** | Initial bulk load + continuous change capture (log-based CDC) until switchover; short final cut | Downtime budget of minutes; large volume | Transformations so heavy that CDC replay can't keep up; no access to the source log | Reverse replication (target → source) set up before switching, or a re-point within the lag window |
| **Parallel run** | Both systems live; the same inputs go to both; outputs are compared for N cycles (e.g. a month-end) | T4 calculation-heavy domains (payroll, billing, ledgers) where "correct" means the *outputs* match | Teams can't double-key, or there is no automated output comparison | Stay on the old system; it remains the system of record until sign-off |
| **Expand / contract (in-place schema)** | Add the new structure, dual-write or backfill, move reads, move writes, drop the old | Schema change inside a live application database, zero downtime | Cross-system moves (use CDC instead) | Each step is reversible until "contract" |

### Decision rules
1. Downtime budget ≥ timed full mock × 1.5 + reconciliation time + rollback time → **big bang** is allowed. Prefer it, because it is the simplest to reason about.
2. Otherwise, if the data partitions cleanly → **phased**, with the smallest and least critical wave first as the pilot.
3. Otherwise → **trickle/CDC**, which needs log access and lag monitoring. Rehearse the final switchover.
4. T4 with calculated outputs (balances, payroll, invoices) → add a **parallel run** over at least one full business cycle on top of whichever strategy you chose.
5. The schema change stays inside one live application → **expand/contract**, see [[migration-cutover-runbook]].

## Archive vs migrate vs retire
- **Migrate:** a live target process reads or writes it.
- **Archive:** a retention obligation exists, or the history is occasionally needed. Store it read-only and queryable (Parquet + catalog, a read-only DB, or the vendor's archive), with its retention end date.
- **Retire:** no process needs it and no obligation exists. Delete it with a documented decision. This is also a GDPR storage-limitation win.
