# Templates

## Migration plan — `output/<YYYYMMDD>-<slug>-migration-plan.md`
```markdown
# <Source> → <Target> Data Migration Plan
Status · Tier T? · Strategy · Go-live target · Owner

## 1. Outcome
Business outcome · deadline + driver · cost of 1h downtime · cost of one wrong record

## 2. Scope decisions
| Data object | Source(s) | Rows | Decision (migrate/archive/retire) | History cut-off | Retention basis | Business owner |

## 3. Complexity scorecard
| Dimension | Score 1–4 | Evidence (source, given/assumed) |
**Tier = T? (driven by: <dimension>)**

## 4. Strategy (ADR)
Decision · Context · Rejected alternative(s) + why · Downtime figure · Point of no return · Rollback path

## 5. Minimum controls for this tier
(the row of the control table for T?, each with how/where it's satisfied)

## 6. Workstreams & calendar
Pipeline stages · mock-load calendar (entry/exit criteria per mock) · cleansing backlog · freeze dates · integration cutover sequence · archive/decommission

## 7. Acceptance criteria
Per object: counts · control totals · field-level threshold · business-rule tests · signer

## 8. Risks (ranked)
| # | Risk | Impact | Likelihood | Owner | Trigger | Mitigation |

## 9. RACI
| Activity | Responsible | Accountable | Consulted | Informed |

## 10. Open questions & assumptions
```

## Mock-load entry/exit card
```markdown
### Mock <n> — <date>
Entry: mapping spec v? frozen · reference data v? loaded · source extract taken at <ts>
Run: duration per stage (extract / transform / load / reconcile)
Exit: reconciliation verdict · open defects by severity · timing vs window · go/no-go for next mock
```
