# Mapping Spec Template — `output/<YYYYMMDD>-<slug>/mapping-<object>.md`

```markdown
# Mapping — <Object> (<source system> → <target system>)
Spec version v? · frozen for mock <n> · business owner <name> · sign-off: pending/approved <date>

## Scope & key
Rows in scope: <n> (filter: <rule>) · excluded: <n> (reason) · history cut-off: <date>
Target key: <natural|surrogate> · crosswalk table: <name> (source_system, source_key → target_key)
Merge/survivorship: <rule per field, or n/a>

## Field mapping (target-backwards)
| # | Target field | Type/len | Mand. | Source field(s) | Rule type | Rule (pseudo-SQL) | Test case |
|---|---|---|---|---|---|---|---|
| 1 | customer_id | bigint | Y | CUST.CUST_NO | lookup | xwalk(src='LEG', key=CUST_NO) | 1001 → 50001 |
| 2 | country_code | char(2) | Y | CUST.LAND | value map | vm_country(upper(trim(LAND))) ; unmapped → reject | 'de ' → 'DE' |
| 3 | created_at | timestamptz | Y | CUST.ERF_DAT + ERF_ZEIT | derive | (ERF_DAT + ERF_ZEIT) AT TIME ZONE 'Europe/Berlin' | … |
| 4 | segment | varchar(20) | N | — | not populated | reason: no source; set in target post go-live | — |

## Value maps
### vm_country (v?, owner <name>) — covers <k>/<k> profiled values
| Source value | Count | Target value | Note |

## Cleansing decision log
| Defect class | Rows | Decision (source/in-flight/exclude/accept) | Rule or action | Owner | Due by |

## Expected differences (feed to reconciliation)
| Check | Expected Δ | Reason |
```
