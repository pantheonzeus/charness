#!/usr/bin/env python3
"""Reconcile a migration target against its source with DuckDB. Exit 0 = PASS, 1 = FAIL, 2 = usage error.

Run:  uv run --with duckdb resources/skills/technology/migration-reconciliation/scripts/reconcile.py \
        --source legacy.csv --target "tgt.public.customers" --key customer_id \
        --attach "postgresql://user@host/db AS tgt (TYPE postgres, READ_ONLY)" \
        --map cust_no=customer_id,name=full_name --out recon.md

SOURCE/TARGET: a file path, an attached table (alias.schema.table) or a "(SELECT ...)" subquery.
Put source-side transformations (filters, derived columns, unit conversion) in a subquery so
both sides are compared in the target's terms.

Checks, in order:
  1. Row counts
  2. Key integrity on both sides (NULL keys, duplicate keys)
  3. Key diff: keys missing in target / unexpected in target
  4. Field-level diff on matched keys, per mapped column
  5. Control totals: sum of every numeric mapped column, both sides
The verdict is FAIL if any check exceeds its threshold (all thresholds default to 0).
Read-only on both sides.
"""
import argparse
import json
import os
import sys

import duckdb

NUMERIC = ("TINYINT", "SMALLINT", "INTEGER", "BIGINT", "HUGEINT", "UTINYINT", "USMALLINT", "UINTEGER",
           "UBIGINT", "FLOAT", "DOUBLE", "REAL", "DECIMAL")


def rel(source):
    if os.path.exists(source):
        return "'" + source.replace("'", "''") + "'"
    return source


def ident(name):
    return '"' + name.replace('"', '""') + '"'


def fmt(v, width=40):
    s = "NULL" if v is None else str(v)
    s = s.replace("|", "\\|").replace("\n", " ")
    return s if len(s) <= width else s[: width - 1] + "…"


def is_numeric(t):
    return t.upper().split("(")[0] in NUMERIC


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--source", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--key", required=True, help="comma-separated key columns, SOURCE names (mapped via --map)")
    p.add_argument("--map", default="", help="src=tgt column renames, comma-separated; unmapped columns match by name")
    p.add_argument("--columns", help="restrict the field diff to these SOURCE columns")
    p.add_argument("--ignore", default="", help="SOURCE columns to leave out of the field diff")
    p.add_argument("--attach", action="append", default=[], help="DuckDB ATTACH clause (repeatable)")
    p.add_argument("--trim", action="store_true", help="ignore leading/trailing whitespace in string compares")
    p.add_argument("--ci", action="store_true", help="case-insensitive string compares")
    p.add_argument("--tolerance", type=float, default=0.0, help="absolute tolerance for numeric field and total compares")
    p.add_argument("--max-missing", type=int, default=0, help="allowed keys missing in target (e.g. agreed exclusions)")
    p.add_argument("--max-extra", type=int, default=0, help="allowed unexpected keys in target")
    p.add_argument("--max-field-mismatch", type=int, default=0, help="allowed mismatching rows per column")
    p.add_argument("--samples", type=int, default=10, help="sample rows shown per finding")
    p.add_argument("--out", help="write the Markdown report here (also printed to stdout)")
    p.add_argument("--json", help="write machine-readable results here")
    a = p.parse_args()

    con = duckdb.connect()
    try:
        for clause in a.attach:
            con.execute(f"ATTACH {clause}")
        con.execute(f"CREATE TEMP VIEW s AS SELECT * FROM {rel(a.source)}")
        con.execute(f"CREATE TEMP VIEW t AS SELECT * FROM {rel(a.target)}")
    except duckdb.Error as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    def cols(view):
        return dict(con.execute("SELECT column_name, data_type FROM information_schema.columns "
                                "WHERE table_name = ? ORDER BY ordinal_position", [view]).fetchall())

    scols, tcols = cols("s"), cols("t")
    mapping = dict(pair.split("=", 1) for pair in a.map.split(",") if pair)
    tgt = lambda c: mapping.get(c, c)  # noqa: E731

    keys = [k.strip() for k in a.key.split(",")]
    for k in keys:
        if k not in scols or tgt(k) not in tcols:
            print(f"error: key {k!r} (target {tgt(k)!r}) not found on both sides", file=sys.stderr)
            return 2

    ignore = {c.strip() for c in a.ignore.split(",") if c.strip()}
    wanted = [c.strip() for c in a.columns.split(",")] if a.columns else list(scols)
    compare = [c for c in wanted if c not in keys and c not in ignore and tgt(c) in tcols]
    unmatched_src = [c for c in scols if c not in keys and c not in ignore and tgt(c) not in tcols]
    mapped_tgt = {tgt(c) for c in scols}
    unmatched_tgt = [c for c in tcols if c not in mapped_tgt]

    join = " AND ".join(f"s.{ident(k)} = TRY_CAST(t.{ident(tgt(k))} AS {scols[k]})" for k in keys)
    skey = ", ".join(f"s.{ident(k)}" for k in keys)
    tkey = ", ".join(f"t.{ident(tgt(k))}" for k in keys)

    results, fails, out = {"source": a.source, "target": a.target, "checks": []}, [], []

    def check(name, value, limit, detail=None):
        ok = value <= limit
        results["checks"].append({"check": name, "value": value, "limit": limit, "pass": ok})
        if not ok:
            fails.append(name)
        out.append(f"| {name} | {value:,} | {limit:,} | {'PASS' if ok else '**FAIL**'} |")
        return ok

    def one(sql):
        return con.execute(sql).fetchone()[0]

    s_n, t_n = one("SELECT count(*) FROM s"), one("SELECT count(*) FROM t")
    out += [f"# Reconciliation — `{a.source}` → `{a.target}`", "",
            f"- Key: {', '.join(f'`{k}`→`{tgt(k)}`' for k in keys)}",
            f"- Fields compared: {len(compare)}" + (f" (trim={a.trim}, ci={a.ci}, tolerance={a.tolerance})"),
            f"- Source columns with no target column (not compared): {', '.join(unmatched_src) or 'none'}",
            f"- Target columns with no source column: {', '.join(unmatched_tgt) or 'none'}", "",
            "| Check | Value | Allowed | Result |", "|---|---:|---:|---|"]

    results.update(source_rows=s_n, target_rows=t_n)
    out.append(f"| Row count source / target | {s_n:,} / {t_n:,} | – | {'match' if s_n == t_n else 'differs (see key diff)'} |")

    for side, view, kcols in (("source", "s", keys), ("target", "t", [tgt(k) for k in keys])):
        kc = ", ".join(ident(k) for k in kcols)
        check(f"NULL keys in {side}", one(f"SELECT count(*) FROM {view} WHERE " + " OR ".join(f"{ident(k)} IS NULL" for k in kcols)), 0)
        check(f"Duplicate keys in {side}", one(f"SELECT count(*) FROM (SELECT 1 FROM {view} GROUP BY {kc} HAVING count(*) > 1)"), 0)

    missing_sql = f"SELECT {skey} FROM s WHERE NOT EXISTS (SELECT 1 FROM t WHERE {join})"
    extra_sql = f"SELECT {tkey} FROM t WHERE NOT EXISTS (SELECT 1 FROM s WHERE {join})"
    missing, extra = one(f"SELECT count(*) FROM ({missing_sql})"), one(f"SELECT count(*) FROM ({extra_sql})")
    check("Keys missing in target", missing, a.max_missing)
    check("Unexpected keys in target", extra, a.max_extra)

    def norm(expr, dtype):
        if dtype.upper().startswith("VARCHAR"):
            if a.trim:
                expr = f"trim({expr})"
            if a.ci:
                expr = f"lower({expr})"
        return expr

    field_detail = []
    for c in compare:
        st, tt = scols[c], tcols[tgt(c)]
        sv, tv = f"s.{ident(c)}", f"TRY_CAST(t.{ident(tgt(c))} AS {st})"
        if is_numeric(st) and a.tolerance > 0:
            diff = f"(({sv} IS NULL) <> ({tv} IS NULL) OR abs({sv} - {tv}) > {a.tolerance})"
        else:
            diff = f"({norm(sv, st)} IS DISTINCT FROM {norm(tv, st)})"
        # A target value that fails to cast to the source type is a mismatch, not a silent NULL.
        diff = f"({diff} OR (t.{ident(tgt(c))} IS NOT NULL AND {tv} IS NULL))"
        n = one(f"SELECT count(*) FROM s JOIN t ON {join} WHERE {diff}")
        check(f"Field mismatches: {c}" + (f" → {tgt(c)}" if tgt(c) != c else ""), n, a.max_field_mismatch)
        if n:
            rows = con.execute(f"SELECT {skey}, {sv}::VARCHAR, t.{ident(tgt(c))}::VARCHAR FROM s JOIN t ON {join} "
                               f"WHERE {diff} LIMIT {a.samples}").fetchall()
            field_detail.append((c, st, tt, rows))

    totals = []
    for c in compare:
        if is_numeric(scols[c]) and is_numeric(tcols[tgt(c)]):
            ssum = one(f"SELECT sum({ident(c)}) FROM s")
            tsum = one(f"SELECT sum({ident(tgt(c))}) FROM t")
            delta = abs(float(ssum or 0) - float(tsum or 0))
            ok = delta <= a.tolerance
            totals.append((c, ssum, tsum, delta, ok))
            results["checks"].append({"check": f"Control total: {c}", "value": delta, "limit": a.tolerance, "pass": ok})
            if not ok:
                fails.append(f"Control total: {c}")

    if totals:
        out += ["", "## Control totals (sum over all rows, each side)", "",
                "| Column | Source | Target | Δ | Result |", "|---|---:|---:|---:|---|"]
        for c, ssum, tsum, delta, ok in totals:
            out.append(f"| {c} | {ssum} | {tsum} | {delta:g} | {'PASS' if ok else '**FAIL**'} |")

    for title, sql, n in (("Keys missing in target", missing_sql, missing), ("Unexpected keys in target", extra_sql, extra)):
        if n:
            out += ["", f"## {title} — first {a.samples}", ""]
            out += [f"- {', '.join(fmt(v) for v in r)}" for r in con.execute(f"{sql} LIMIT {a.samples}").fetchall()]

    for c, st, tt, rows in field_detail:
        out += ["", f"## Field mismatches: {c} ({st}) → {tgt(c)} ({tt}) — first {a.samples}", "",
                "| Key | Source | Target |", "|---|---|---|"]
        out += [f"| {', '.join(fmt(v) for v in r[:len(keys)])} | {fmt(r[-2])} | {fmt(r[-1])} |" for r in rows]

    if any(f.startswith("Duplicate keys") for f in fails):
        out += ["", "> Duplicate keys found: field mismatch counts above are inflated by the fan-out join. "
                "Fix key uniqueness first, then re-run."]

    verdict = "PASS" if not fails else "FAIL"
    results["verdict"] = verdict
    out += ["", f"## Verdict: **{verdict}**" + (f" — {len(fails)} check(s) failed: {', '.join(fails)}" if fails else "")]

    report = "\n".join(out) + "\n"
    sys.stdout.write(report)
    if a.out:
        with open(a.out, "w") as f:
            f.write(report)
    if a.json:
        with open(a.json, "w") as f:
            json.dump(results, f, indent=2, default=str)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
