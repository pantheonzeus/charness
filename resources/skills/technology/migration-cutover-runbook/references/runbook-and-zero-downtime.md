# Runbook Template & Zero-Downtime Patterns

## Cutover runbook — `output/<YYYYMMDD>-<slug>/cutover-runbook.md`
```markdown
# Cutover Runbook — <Source> → <Target>
Window: <start> – <end> (<h> h budget) · PNR at T+<hh:mm> · Rollback owner <name> · Decision-makers <names>
Mock basis: dress rehearsal <date>, total <h:mm> measured, buffer <x>% → fits/doesn't fit window

## Pre-cutover checklist
| T- | Item | Owner | Done |
| T-14d | Code/schema/reference-data freeze in force | | |
| T-7d  | Backup taken AND test-restored (time: __) | | |
| T-2d  | Integration owners confirmed on call | | |
| T-1d  | Comms sent (users, support desk, partners) | | |

## Step table
| # | T+ | Step | Owner | Duration (mock) | Verification | Rollback |
| 1 | 00:00 | Stop inbound interfaces A, B | | 0:10 | queues drained = 0 | restart interfaces |
| 2 | 00:10 | Source to read-only | | 0:05 | write test fails | revert grant |
| … |
| n | 06:30 | GO / NO-GO (criteria below) | decision-makers | 0:15 | recorded | — |
| n+1 | 06:45 | ▶ POINT OF NO RETURN: open target for writes | | | | forward-fix / reverse CDC |

## Go/no-go criteria
| Criterion | Threshold | Actual | OK |
| Reconciliation per object | PASS | | |
| Business-rule tests | all green | | |
| Elapsed vs plan | ≤ plan + buffer | | |
| Open Sev-1 defects | 0 | | |
| Smoke tests (top user journeys) | pass | | |

## Comms · Hypercare (duration, triage cadence, exit criteria) · Decommission (dates per item)
```

## Zero-downtime patterns

### 1. CDC trickle with short switchover (cross-system)
1. Enable log-based CDC on the source (WAL/binlog/redo; Debezium, AWS DMS or native logical replication for same-engine moves). Record the start position.
2. Bulk-load a consistent snapshot as of that position.
3. Stream changes and monitor lag (seconds behind and events/s) for days. Keep transformation logic in the stream identical to the bulk path, using the same code.
4. Reconcile at a recorded position: pause apply, reconcile, resume.
5. Switchover: freeze source writes → drain lag to 0 → final reconcile (fast checks: counts, key diff, totals) → re-point the applications → open the target.
6. Rollback within the window: optionally set up reverse replication target → source *before* opening the target, so the source stays current and re-pointing back is a minutes-long job.

### 2. Expand / contract (schema change inside one live database)
1. **Expand:** add the new columns/tables, nullable, with no reads yet. Backwards-compatible deploy.
2. **Sync:** the app writes old + new in the same transaction, or a trigger keeps the new structure in sync.
3. **Backfill:** idempotent batches by key range, throttled, resumable from a checkpoint. Reconcile old vs new.
4. **Shadow reads:** read both and compare in production, logging mismatches without serving the new values. Proceed only when mismatches are at zero over an agreed period.
5. **Move reads,** then **move writes,** to the new structure only.
6. **Contract:** drop the old structure after a soak period. This is the PNR for the schema change.
For large MySQL tables use an online schema-change tool (e.g. gh-ost) instead of blocking `ALTER TABLE`.

### 3. Strangler / per-entity migration (system replacement)
When the application is replaced incrementally behind a facade, the program, facade and slice ramp belong to `strangler-fig-program` → `strangler-transition-architecture` → `strangler-slice-cutover`. Use patterns 1–2 above for each slice's data movement, and `migration-reconciliation` for its parity proof.

### Backfill rules (all patterns)
- Batch by key range, not OFFSET. Commit per batch and store a checkpoint so the job resumes after a crash.
- Throttle on replica lag or DB load. A backfill that degrades production is an incident.
- Every write is an upsert keyed on the business key, so re-running a batch is safe.
