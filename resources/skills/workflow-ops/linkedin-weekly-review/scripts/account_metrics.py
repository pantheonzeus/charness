#!/usr/bin/env python3
"""
account_metrics.py — recompute the three tracked account-level visibility
axes (Buyer / Recruiter / Reach) over account-metrics.tsv and print a
week-over-week trend summary.

Pure recompute, mirrors linkedin-viral-scheduler/scripts/viral_metrics.py's
design: `ingest_xlsx.py --account` is the only writer of new *raw* weekly
rows (measured fields ingested from a LinkedIn export); this script only
(re)computes the three *derived* axis columns from those raw fields and
reports — so retuning an axis formula never requires re-ingesting the
source export.

Axis definitions (full rationale in references/axes-and-intake.md):
  buyer_axis      = engagement_rate x clamp(decision_maker_density/15, 0.4, 2.0)
                    -- reuses build_dataset.py's senior/industry classification
                    + calibrated pivot (never re-forked); decision_maker_density
                    = mean(senior_share, industry_fit_share).
  recruiter_axis  = recruiter_share (%) -- direct measured share, no invented
                    multiplier (no historical corpus yet to calibrate one —
                    same "report raw until validated" posture the repo already
                    applies to Family B content predictors at low n).
  reach_axis      = impressions (raw weekly total) -- the plainest honest
                    reach number. followers_gained/engagement_rate are kept as
                    separate columns, not folded into one invented composite
                    (a manufactured weighted sum here would be exactly the
                    "vanity metric with a chart" this account's own voice
                    rejects).

Usage:
  account_metrics.py [--tsv FILE]

Never fabricates: a row missing a raw input for an axis leaves that axis
blank and is listed under DATA QUALITY, not silently scored 0.
"""

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CALIB_DIR = os.path.normpath(
    os.path.join(HERE, "..", "..", "linkedin-scoring-calibration", "scripts")
)
if CALIB_DIR not in sys.path:
    sys.path.insert(0, CALIB_DIR)
try:
    import build_dataset as bd  # reuse clamp() -- the calibrated buyer-axis pivot, never re-forked
except ImportError:
    sys.exit(f"error: cannot import build_dataset from {CALIB_DIR}")

DEFAULT_TSV = os.path.join(HERE, "..", "account-metrics.tsv")

RAW_COLUMNS = [
    "week", "week_start", "week_end", "impressions", "engagements",
    "engagement_rate", "followers_gained", "profile_views",
    "search_appearances", "senior_share", "industry_fit_share",
    "recruiter_share", "n_posts", "has_demographics",
]
DERIVED_COLUMNS = ["decision_maker_density", "buyer_axis", "recruiter_axis", "reach_axis"]
COLUMNS = RAW_COLUMNS + DERIVED_COLUMNS


def num(s):
    """Parse '1,252' / '3.10%' / '' -> float or ''. Mirrors build_dataset.num()."""
    if s in (None, ""):
        return ""
    s = str(s).replace(",", "").replace("%", "").strip()
    if s == "":
        return ""
    try:
        return float(s)
    except ValueError:
        return ""


def read_rows(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f if ln.strip()]
    if not lines:
        return []
    header = lines[0].split("\t")
    rows = []
    for line in lines[1:]:
        vals = line.split("\t")
        rows.append(dict(zip(header, vals)))
    return rows


def compute_row(row):
    senior = num(row.get("senior_share", ""))
    industry = num(row.get("industry_fit_share", ""))
    engagement_rate = num(row.get("engagement_rate", ""))
    recruiter = num(row.get("recruiter_share", ""))
    impressions = num(row.get("impressions", ""))

    density = round((senior + industry) / 2, 1) if senior != "" and industry != "" else ""

    if density != "" and engagement_rate != "":
        multiplier = bd.clamp(density / 15.0, 0.4, 2.0)
        buyer_axis = round(engagement_rate * multiplier, 3)
    else:
        buyer_axis = ""

    row["decision_maker_density"] = density
    row["buyer_axis"] = buyer_axis
    row["recruiter_axis"] = recruiter if recruiter != "" else ""
    row["reach_axis"] = impressions if impressions != "" else ""
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tsv", default=DEFAULT_TSV)
    args = ap.parse_args()

    tsv_path = os.path.normpath(args.tsv)
    if not os.path.isfile(tsv_path):
        sys.exit(f"error: {tsv_path} not found -- run ingest_xlsx.py --account first")

    rows = read_rows(tsv_path)
    if not rows:
        print(f"{tsv_path} has no data rows yet -- nothing to compute.")
        return

    rows = [compute_row(r) for r in rows]
    rows.sort(key=lambda r: r.get("week_end", ""))

    with open(tsv_path, "w", encoding="utf-8") as f:
        f.write("\t".join(COLUMNS) + "\n")
        for r in rows:
            f.write("\t".join(str(r.get(c, "")) for c in COLUMNS) + "\n")
    print(f"recomputed {len(rows)} weekly rows -> {tsv_path}\n")

    missing_buyer = [r["week"] for r in rows if r["buyer_axis"] == ""]
    missing_recruiter = [r["week"] for r in rows if r["recruiter_axis"] == ""]
    if missing_buyer:
        print(f"DATA QUALITY -- buyer_axis blank (missing demographics or "
              f"engagement_rate): {', '.join(missing_buyer)}")
    if missing_recruiter:
        print(f"DATA QUALITY -- recruiter_axis blank (missing recruiter_share): "
              f"{', '.join(missing_recruiter)}")

    def delta(key):
        if len(rows) < 2:
            return None
        a, b = num(rows[-2].get(key, "")), num(rows[-1].get(key, ""))
        if a == "" or b == "":
            return None
        return round(b - a, 3)

    print("\n=== Week-over-week (most recent vs prior) ===")
    for label, key in [
        ("Buyer axis", "buyer_axis"),
        ("Recruiter axis (%)", "recruiter_axis"),
        ("Reach axis (impressions)", "reach_axis"),
        ("Engagement rate (%)", "engagement_rate"),
        ("Followers gained", "followers_gained"),
    ]:
        d = delta(key)
        latest = rows[-1].get(key, "")
        if d is None:
            print(f"  {label:28s}  latest={latest}  (n<2 weeks or missing data, no delta)")
        else:
            arrow = "^" if d > 0 else ("v" if d < 0 else "=")
            print(f"  {label:28s}  latest={latest}  wow={d:+} {arrow}")

    if len(rows) < 4:
        print(f"\nNote: n={len(rows)} weeks in corpus -- trend is directional only, "
              f"not yet statistically meaningful (same small-n posture as the "
              f"post-level corpus in viral-metrics.md).")


if __name__ == "__main__":
    main()
