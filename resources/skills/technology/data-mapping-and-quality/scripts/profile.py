#!/usr/bin/env python3
"""Profile a migration source (or target) with DuckDB and print a Markdown report.

Run:  uv run --with duckdb resources/skills/technology/data-mapping-and-quality/scripts/profile.py SOURCE [options]

SOURCE is anything DuckDB can select from:
  - a file path: customers.csv, orders.parquet, events.json
  - a table in an attached database: src.public.customers  (with --attach)
  - a parenthesised subquery: "(SELECT * FROM src.orders WHERE year = 2025)"

--attach takes DuckDB ATTACH syntax, e.g.
  --attach "postgresql://user@host/db AS src (TYPE postgres, READ_ONLY)"
  --attach "legacy.sqlite AS src (TYPE sqlite, READ_ONLY)"

Reports per column: type, nulls, distinct, min/max, string length range, blank and
whitespace-padded strings, top values. With --key: null and duplicate keys.
Read-only: it never writes to the source.
"""
import argparse
import os
import sys

import duckdb


def rel(source):
    if os.path.exists(source):
        return "'" + source.replace("'", "''") + "'"
    return source


def q(con, sql):
    return con.execute(sql).fetchall()


def ident(name):
    return '"' + name.replace('"', '""') + '"'


def fmt(v, width=40):
    s = "NULL" if v is None else str(v)
    s = s.replace("|", "\\|").replace("\n", " ")
    return s if len(s) <= width else s[: width - 1] + "…"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source")
    p.add_argument("--attach", action="append", default=[], help="DuckDB ATTACH clause (repeatable)")
    p.add_argument("--key", help="comma-separated business/primary key columns")
    p.add_argument("--top", type=int, default=5, help="top-N values per column (default 5)")
    p.add_argument("--sample", type=int, help="profile a random sample of N rows (large tables)")
    p.add_argument("--out", help="write the Markdown report here instead of stdout")
    a = p.parse_args()

    con = duckdb.connect()
    for clause in a.attach:
        con.execute(f"ATTACH {clause}")
    sample = f" USING SAMPLE {a.sample} ROWS" if a.sample else ""
    con.execute(f"CREATE TEMP VIEW src AS SELECT * FROM {rel(a.source)}{sample}")

    cols = q(con, "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'src' ORDER BY ordinal_position")
    total = q(con, "SELECT count(*) FROM src")[0][0]

    out = [f"# Profile — `{a.source}`", "", f"- Rows: **{total:,}**" + (f" (sample of {a.sample})" if a.sample else ""),
           f"- Columns: **{len(cols)}**", ""]

    out += ["| Column | Type | Nulls | Null % | Distinct | Min | Max | Len min–max | Blank | Padded |",
            "|---|---|---:|---:|---:|---|---|---|---:|---:|"]
    candidate_keys, tops = [], []
    for name, dtype in cols:
        c = ident(name)
        is_str = dtype.upper().startswith("VARCHAR")
        str_sql = (f", min(length({c})), max(length({c})), count(*) FILTER (WHERE trim({c}) = ''),"
                   f" count(*) FILTER (WHERE {c} <> trim({c}))") if is_str else ", NULL, NULL, NULL, NULL"
        nn, dist, mn, mx, lmin, lmax, blank, padded = q(
            con, f"SELECT count({c}), count(DISTINCT {c}), min({c})::VARCHAR, max({c})::VARCHAR{str_sql} FROM src")[0]
        nulls = total - nn
        pct = f"{100 * nulls / total:.1f}" if total else "–"
        lens = f"{lmin}–{lmax}" if is_str and lmin is not None else ""
        out.append(f"| {fmt(name)} | {dtype} | {nulls:,} | {pct} | {dist:,} | {fmt(mn, 24)} | {fmt(mx, 24)} | {lens} | "
                   f"{'' if blank is None else f'{blank:,}'} | {'' if padded is None else f'{padded:,}'} |")
        if total and nulls == 0 and dist == total:
            candidate_keys.append(name)
        top = q(con, f"SELECT {c}::VARCHAR, count(*) n FROM src GROUP BY 1 ORDER BY n DESC, 1 LIMIT {a.top}")
        tops.append((name, top))

    out += ["", "**Candidate single-column keys** (no nulls, all distinct): "
            + (", ".join(f"`{k}`" for k in candidate_keys) if candidate_keys else "none"), ""]

    if a.key:
        keys = [k.strip() for k in a.key.split(",")]
        kc = ", ".join(ident(k) for k in keys)
        null_keys = q(con, "SELECT count(*) FROM src WHERE " + " OR ".join(f"{ident(k)} IS NULL" for k in keys))[0][0]
        dup_groups, dup_rows = q(con, f"SELECT count(*), coalesce(sum(n), 0) FROM (SELECT count(*) n FROM src GROUP BY {kc} HAVING n > 1)")[0]
        out += [f"## Key check — ({', '.join(keys)})", "", f"- Rows with a NULL key part: **{null_keys:,}**",
                f"- Duplicate key groups: **{dup_groups:,}** covering **{dup_rows:,}** rows"]
        if dup_groups:
            out += ["", "Sample duplicate keys:", ""]
            for row in q(con, f"SELECT {kc}, count(*) n FROM src GROUP BY {kc} HAVING n > 1 ORDER BY n DESC LIMIT 10"):
                out.append(f"- {', '.join(fmt(v) for v in row[:-1])} × {row[-1]}")
        out.append("")

    out += ["## Top values", ""]
    for name, top in tops:
        out.append(f"- **{fmt(name)}**: " + "; ".join(f"{fmt(v, 30)} ({n:,})" for v, n in top))

    report = "\n".join(out) + "\n"
    if a.out:
        with open(a.out, "w") as f:
            f.write(report)
        print(f"wrote {a.out}", file=sys.stderr)
    else:
        sys.stdout.write(report)


if __name__ == "__main__":
    main()
