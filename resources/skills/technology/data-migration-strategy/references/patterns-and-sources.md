# Patterns & Sources

The named methods the four data-migration skills draw on, with primary sources. Cite these in client deliverables instead of paraphrasing them unattributed. Deliberately absent: the widely repeated "X% of data migrations fail" figures. Their original studies are old and hard to trace, so don't put them in a deliverable unless you have the primary source in hand.

| Method / tool | Used in | Primary source |
|---|---|---|
| Business-owned, data-quality-first migration method (PDMv2): data stakeholders, key data stakeholder sign-off, "migrate less" | strategy, mapping | Johny Morris, *Practical Data Migration*, 3rd ed., BCS, 2012 |
| Data quality dimensions (completeness, validity, accuracy, consistency, uniqueness, timeliness) | mapping | DAMA International, *DAMA-DMBOK: Data Management Body of Knowledge*, 2nd ed., 2017 |
| Parallel change (expand → migrate → contract) | cutover | Danilo Sato, "ParallelChange", martinfowler.com — https://martinfowler.com/bliki/ParallelChange.html |
| Strangler fig (incremental replacement of a legacy system) | strategy, cutover | Martin Fowler, "StranglerFigApplication" — https://martinfowler.com/bliki/StranglerFigApplication.html |
| Online migration via dual writes → move reads → move writes → remove old | cutover | Jacqueline Xu, "Online migrations at scale", Stripe engineering blog, 2017 — https://stripe.com/blog/online-migrations |
| Log-based change data capture | strategy, cutover | Debezium documentation — https://debezium.io/documentation/ |
| Managed bulk + CDC replication across engines | cutover | AWS Database Migration Service User Guide — https://docs.aws.amazon.com/dms/latest/userguide/Welcome.html |
| Native logical replication (Postgres → Postgres, version upgrades) | cutover | PostgreSQL docs, "Logical Replication" — https://www.postgresql.org/docs/current/logical-replication.html |
| Online schema change for MySQL without triggers | cutover | github/gh-ost — https://github.com/github/gh-ost |
| In-process engine for profiling/reconciliation across files and DBs (postgres/mysql/sqlite scanners) | mapping, reconciliation | DuckDB documentation — https://duckdb.org/docs/ |

Re-verify tool capabilities against the live docs before a client recommendation, because managed-service feature sets change.
