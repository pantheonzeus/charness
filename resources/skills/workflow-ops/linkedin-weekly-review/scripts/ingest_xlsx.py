#!/usr/bin/env python3
"""
ingest_xlsx.py — parse a LinkedIn analytics .xlsx export and write it into
this skill's canonical data stores: account-metrics.tsv (weekly, account-
level) or a per-post vault note's ## Performance / ## Audience snapshot
sections (cbrain/notes/LinkedIn-Posts/YYYYMMDD-slug.md).

STATUS: the field-label mapping below (LABELS/DEMO_CATEGORIES) is a
best-effort match against LinkedIn's known export vocabulary — it has not
yet been verified against a real export from this account. Run --inspect on
your actual file FIRST; the script prints every label it finds, so a mapping
miss is visible immediately rather than silently wrong. Confirm the printed
field->value mapping against the source file before trusting a write.

Design: locate every value by HEADER LABEL, matched exactly (case/whitespace
-insensitive) against a small alias list -- never by fixed cell coordinates,
which would silently break the moment LinkedIn reshuffles a sheet layout.
A label that isn't found is left blank and reported under DATA QUALITY,
never guessed or defaulted to 0 (same posture as viral_metrics.py /
build_dataset.py).

Modes:
  ingest_xlsx.py --inspect FILE.xlsx
      Dump every sheet name + every non-empty label-like cell found. Use
      this first, always, to calibrate against your real export.

  ingest_xlsx.py --account FILE.xlsx --week-start YYYY-MM-DD --week-end YYYY-MM-DD
      Parse an account-level (Analytics > Content, date-ranged) export.
      Appends one row to account-metrics.tsv. Run account_metrics.py
      afterward to compute the derived axis columns.

  ingest_xlsx.py --post FILE.xlsx --date YYYYMMDD --slug some-post-slug
      Parse a single-post analytics export. Updates the ## Performance and
      ## Audience snapshot sections of the EXISTING vault note
      cbrain/notes/LinkedIn-Posts/YYYYMMDD-some-post-slug.md in place --
      refuses to fabricate a new post note from scratch (a post note is
      created when the post is drafted/published, not by this script).

Requires openpyxl (present at build time: 3.1.5). Degrades to the stdlib
`csv` module for a .csv export -- single-sheet only, so demographics
(which need a labelled sub-table) cannot be parsed from csv; account/post
totals still can.
"""

import argparse
import csv
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
CALIB_DIR = os.path.normpath(
    os.path.join(HERE, "..", "..", "linkedin-scoring-calibration", "scripts")
)
if CALIB_DIR not in sys.path:
    sys.path.insert(0, CALIB_DIR)
try:
    import build_dataset as bd  # reuse senior_share/industry_fit_share -- never re-forked
except ImportError:
    sys.exit(f"error: cannot import build_dataset from {CALIB_DIR}")

VAULT_POSTS_DIR = os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "..", "..", "cbrain", "notes", "LinkedIn-Posts")
)
DEFAULT_ACCOUNT_TSV = os.path.join(HERE, "..", "account-metrics.tsv")

# --- Header-label aliases -> canonical field name. Matched after
# lowercasing + collapsing whitespace. PROVISIONAL -- extend/correct once
# validated against a real export via --inspect. ---
LABELS = {
    "impressions": "impressions",
    "members reached": "members_reached",
    "reactions": "reactions",
    "comments": "comments",
    "reposts": "reposts",
    "shares": "reposts",
    "saves": "saves",
    "sends": "sends",
    "sends on linkedin": "sends",
    "engagement rate": "engagement_rate",
    "engagements": "engagements",
    "social engagements": "engagements",
    "new followers": "followers_gained",
    "followers gained": "followers_gained",
    "followers gained from this post": "followers_gained",
    "profile viewers": "profile_viewers",
    "profile viewers from post": "profile_viewers",
    "profile viewers from this post": "profile_viewers",
    "profile views": "profile_viewers",
    "search appearances": "search_appearances",
    "number of posts": "n_posts",
}

# Row-category labels (col A of LinkedIn's flat "category | value | pct"
# demographics table) -> the (label, pct) bucket build_dataset.py / the note
# renderer expect. Verified 2026-07-24 against this account's own
# SinglePostAnalytics/AggregateAnalytics exports -- one row per item, the
# category repeated down column A (e.g. ['Seniority', 'Senior', '36%'],
# ['Job title', 'Founder', '5%']), not a header-then-rows-below layout.
DEMO_ROW_CATEGORIES = {
    "seniority": "seniority",
    "job title": "top job titles",
    "industry": "top industries",
    "location": "top locations",
    "company size": "company size",
    "company": "notable companies",
}

# Recruiter/talent-visibility axis -- new, not in build_dataset.py. Real data
# shows recruiter reach surfaces mostly as the "Staffing and Recruiting"
# INDUSTRY share, not a job-title match (recruiters' titles vary too widely
# to catch by keyword) -- so this axis sums two independent signals: a
# job-title keyword match (kept for when it does hit) plus the industry
# share. See references/axes-and-intake.md for the double-counting caveat
# (these are two different marginal breakdowns of the same audience, not a
# joint measurement).
RECRUITER_TITLE_KEYWORDS = [
    "recruit", "talent acquisition", "talent partner", "talent sourc",
    "headhunter", "executive search", "human resources", " hr ", "hr manager",
    "hr business partner", "people operations", "people partner",
]
RECRUITER_INDUSTRY_KEYWORDS = ["staffing and recruiting", "recruiting"]


def recruiter_share(demo):
    total = 0.0
    for label, pct in demo.get("top job titles", []):
        low = f" {label.lower()} "
        if any(kw in low for kw in RECRUITER_TITLE_KEYWORDS):
            total += pct
    for label, pct in demo.get("top industries", []):
        low = label.lower()
        if any(kw in low for kw in RECRUITER_INDUSTRY_KEYWORDS):
            total += pct
    return round(total, 1)


def derive_engagement_rate(fields):
    """Neither the Aggregate nor the Single-Post export carries a direct
    engagement-rate field (verified 2026-07-24) -- derive it as
    engagements/impressions*100 when both are present. Returns True if a
    value was derived, so the caller can print it as computed, not read."""
    if fields.get("engagement_rate") in (None, ""):
        impr, eng = fields.get("impressions"), fields.get("engagements")
        if impr not in (None, "", 0) and eng not in (None, ""):
            fields["engagement_rate"] = round(eng / impr * 100, 2)
            return True
    return False


def norm(s):
    return re.sub(r"\s+", " ", str(s).strip().lower()) if s is not None else ""


def num(v):
    if v is None:
        return None
    s = str(v).replace(",", "").replace("%", "").strip()
    if s == "":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def fmt_num(v):
    """Format a value for vault-note display: whole numbers with no trailing
    '.0', others to 2 decimals. Accepts a raw number or an already-formatted
    string (e.g. a value carried forward from the note's prior table)."""
    if v in (None, ""):
        return ""
    n = num(v) if isinstance(v, str) else v
    if n is None:
        return v  # not numeric -- pass through rather than mangle it
    return str(int(n)) if n == int(n) else f"{round(n, 2)}"


def fmt_pct(v):
    """Same as fmt_num but always renders a '%' suffix at 2 decimals,
    matching the existing vault-note convention (e.g. '3.10%')."""
    if v in (None, ""):
        return ""
    n = num(v) if isinstance(v, str) else v
    if n is None:
        return v
    return f"{n:.2f}%"


def load_workbook_cells(path):
    """Return {sheet_name: [[cell, cell, ...], ...]} of raw values."""
    try:
        import openpyxl
    except ImportError:
        sys.exit("error: openpyxl not installed (`pip install openpyxl`) -- required for .xlsx")
    wb = openpyxl.load_workbook(path, data_only=True)
    out = {}
    for ws in wb.worksheets:
        out[ws.title] = [list(row) for row in ws.iter_rows(values_only=True)]
    return out


def load_csv_cells(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return {"csv": list(csv.reader(f))}


def load_cells(path):
    if path.lower().endswith(".csv"):
        return load_csv_cells(path)
    return load_workbook_cells(path)


def inspect(path):
    sheets = load_cells(path)
    print(f"=== {path} ===")
    for name, rows in sheets.items():
        print(f"\n--- sheet: {name} ({len(rows)} rows) ---")
        for r in rows:
            cells = [c for c in r if c not in (None, "")]
            if cells:
                print("  ", cells)


def find_scalar_labels(sheets):
    """Scan every sheet for a label cell (matches LABELS) and take the
    nearest value: cell to the right, else sum of numeric cells below in
    the same column (handles a daily time-series column under one header).
    Returns {canonical_field: value_or_None}."""
    found = {}
    for rows in sheets.values():
        for r_idx, row in enumerate(rows):
            for c_idx, cell in enumerate(row):
                key = LABELS.get(norm(cell))
                if not key or key in found:
                    continue
                # try same-row, next column
                if c_idx + 1 < len(row):
                    v = num(row[c_idx + 1])
                    if v is not None:
                        found[key] = v
                        continue
                # try summing the column below (time-series under this header)
                col_vals = []
                for below in rows[r_idx + 1:]:
                    if c_idx < len(below):
                        v = num(below[c_idx])
                        if v is not None:
                            col_vals.append(v)
                        elif col_vals:
                            break  # stop at first blank after a run of numbers
                if col_vals:
                    found[key] = round(sum(col_vals), 3)
    return found


def find_demographics(sheets):
    """Scan every sheet for LinkedIn's flat demographics table -- one row per
    item, category repeated in column A (e.g. ['Seniority', 'Senior', '36%'],
    ['Job title', 'Founder', '5%']). Returns a `demo` dict in
    build_dataset.py's shape ({"seniority": [(label, pct), ...], ...}).
    Entries whose percentage doesn't parse (LinkedIn's '< 1%' floor) are
    dropped, not guessed at -- documented as negligible, never fabricated
    as 0."""
    demo = {}
    for rows in sheets.values():
        for row in rows:
            if len(row) < 3:
                continue
            bucket = DEMO_ROW_CATEGORIES.get(norm(row[0]))
            if not bucket:
                continue
            label, pct_cell = row[1], row[2]
            if label in (None, ""):
                continue
            pct = num(pct_cell)
            if pct is None:
                continue  # e.g. LinkedIn's '< 1%' floor -- negligible, not 0
            demo.setdefault(bucket, []).append((str(label).strip(), pct))
    return demo


def iso_week(d):
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


ACCOUNT_RAW_HEADER = [
    "week", "week_start", "week_end", "impressions", "engagements",
    "engagement_rate", "followers_gained", "profile_views",
    "search_appearances", "senior_share", "industry_fit_share",
    "recruiter_share", "n_posts", "has_demographics",
]


def read_tsv_rows(path):
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        return [], ACCOUNT_RAW_HEADER
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.rstrip("\n") for ln in f if ln.strip()]
    if not lines:
        return [], ACCOUNT_RAW_HEADER
    header = lines[0].split("\t")
    rows = [dict(zip(header, ln.split("\t"))) for ln in lines[1:]]
    return rows, header


def ingest_account(xlsx_path, week_start, week_end, tsv_path):
    sheets = load_cells(xlsx_path)
    fields = find_scalar_labels(sheets)
    demo = find_demographics(sheets)
    er_derived = derive_engagement_rate(fields)

    senior = bd.senior_share(demo) if demo else ""
    industry = bd.industry_fit_share(demo) if demo else ""
    recruiter = recruiter_share(demo) if demo else ""
    has_demo = 1 if demo else 0
    week = iso_week(week_end)

    new_row = {
        "week": week,
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "impressions": fields.get("impressions", ""),
        "engagements": fields.get("engagements", ""),
        "engagement_rate": fields.get("engagement_rate", ""),
        "followers_gained": fields.get("followers_gained", ""),
        "profile_views": fields.get("profile_viewers", ""),
        "search_appearances": fields.get("search_appearances", ""),
        "senior_share": senior,
        "industry_fit_share": industry,
        "recruiter_share": recruiter,
        "n_posts": fields.get("n_posts", ""),
        "has_demographics": has_demo,
    }

    rows, _ = read_tsv_rows(tsv_path)
    existing = next((r for r in rows if r.get("week") == week), None)
    if existing:
        # Re-ingest of an already-recorded week (e.g. a corrected export) --
        # update in place rather than duplicate the row. Any field this
        # export didn't carry falls back to what was already recorded,
        # never blanked.
        merged = dict(existing)
        for k, v in new_row.items():
            if v not in ("", None):
                merged[k] = v
        rows = [merged if r.get("week") == week else r for r in rows]
        action = "updated existing"
    else:
        rows.append(new_row)
        action = "appended new"

    print("Parsed fields (confirm against the source file before trusting this write):")
    for k, v in new_row.items():
        suffix = "  (DERIVED: engagements/impressions*100, not in export)" \
            if k == "engagement_rate" and er_derived else ""
        print(f"  {k:20s} = {v}{suffix}")

    missing = [k for k, v in new_row.items() if v == "" and k not in ("n_posts",)]
    if missing:
        print(f"\nDATA QUALITY -- label not found in this export: {', '.join(missing)}"
              + (" (kept prior value where one existed)" if existing else " (left blank)"))

    rows.sort(key=lambda r: r.get("week_end", ""))
    with open(tsv_path, "w", encoding="utf-8") as f:
        f.write("\t".join(ACCOUNT_RAW_HEADER) + "\n")
        for r in rows:
            f.write("\t".join(str(r.get(c, "")) for c in ACCOUNT_RAW_HEADER) + "\n")
    print(f"\n{action} row for {week} -> {tsv_path}\n"
          f"run account_metrics.py next to compute the derived axis columns.")


DEMO_LINE_TEMPLATES = {
    "seniority": "Seniority",
    "top industries": "Top industries",
    "top job titles": "Top job titles",
    "top locations": "Top locations",
    "company size": "Company size",
    "notable companies": "Notable companies",
}

# A clean auto-generated item is "<label> <pct>%" (optional trailing '.'),
# with a required whitespace directly before the trailing number -- this is
# what rules out swallowing appended prose ending in its own '...N%.' (a
# trend note can itself contain percentages, so merely "ends in a percent"
# is not a sufficient check; requiring the match to reach end-of-chunk via
# a *whitespace-adjacent* trailing number is what catches it).
ITEM_RE = re.compile(r"^.+?\s\d+(?:\.\d+)?%\.?$")


def audience_section_has_annotations(text):
    """Detect hand-written commentary in the note's existing Audience
    snapshot beyond the standard 'label pct% · label pct%' pattern (e.g. a
    trend note appended to a bucket line: '... — Company A's viewer share has
    risen every snapshot: 4%->6%->7%.'). A mechanical re-render has no way to
    merge free text like that without risking a stale claim re-presented as
    current -- so the caller skips overwriting instead, and this returns the
    offending bucket titles to flag in the confirm-back."""
    m = re.search(r"^## Audience snapshot.*?\n(.*?)(?=^## |\Z)", text,
                  flags=re.DOTALL | re.MULTILINE)
    if not m:
        return []
    flagged = []
    for line in m.group(1).splitlines():
        lm = re.match(r"-\s*\*\*([^:]+):\*\*\s*(.*)", line.strip())
        if not lm:
            continue
        title, rest = lm.group(1).strip(), lm.group(2).strip()
        if not rest:
            continue
        chunks = [c.strip() for c in rest.split(" · ")]
        if any(not ITEM_RE.match(c) for c in chunks):
            flagged.append(title)
    return flagged


def render_audience_snapshot(demo):
    lines = ["## Audience snapshot (viewer demographics)", ""]
    for bucket, title in DEMO_LINE_TEMPLATES.items():
        items = demo.get(bucket)
        if not items:
            continue
        parts = " · ".join(f"{label} {fmt_num(pct)}%" for label, pct in items)
        lines.append(f"- **{title}:** {parts}")
    return "\n".join(lines) + "\n"


# (display label, our-fields-key, old-vault-note-key, formatter, bold)
# The old-vault-note-key differs from ours in exactly one place:
# build_dataset.py's parse_post() names the bolded row "social_engagements";
# we name the same field "engagements" (matching LABELS/find_scalar_labels).
POST_PERF_FIELDS = [
    ("Impressions", "impressions", "impressions", fmt_num, False),
    ("Members reached", "members_reached", "members_reached", fmt_num, False),
    ("Profile viewers from post", "profile_viewers", "profile_viewers", fmt_num, False),
    ("Followers gained", "followers_gained", "followers_gained", fmt_num, False),
    ("Social engagements", "engagements", "social_engagements", fmt_num, True),
    ("Reactions", "reactions", "reactions", fmt_num, False),
    ("Comments", "comments", "comments", fmt_num, False),
    ("Reposts", "reposts", "reposts", fmt_num, False),
    ("Saves", "saves", "saves", fmt_num, False),
    ("Sends", "sends", "sends", fmt_num, False),
    ("Engagement rate (eng/impr)", "engagement_rate", "engagement_rate", fmt_pct, False),
]

PERF_TABLE_RE = re.compile(r"\| Metric \| Value \|\n\|---\|---\|\n(?:\|.*\|\n?)*")


def render_table_only(fields):
    """Just the markdown table (no '## Performance' heading) -- so a
    re-ingest can replace the table in place while leaving any hand-written
    prose before/after it inside the section untouched."""
    lines = ["| Metric | Value |", "|---|---|"]
    for label, key, _old_key, fmt, bold in POST_PERF_FIELDS:
        val = fmt(fields.get(key, ""))
        cell_label, cell_val = (f"**{label}**", f"**{val}**") if bold else (label, val)
        lines.append(f"| {cell_label} | {cell_val} |")
    return "\n".join(lines) + "\n"


def ingest_post(xlsx_path, date_str, slug, posts_dir):
    note_path = os.path.join(posts_dir, f"{date_str}-{slug}.md")
    if not os.path.isfile(note_path):
        candidates = [f for f in os.listdir(posts_dir) if f.startswith(date_str)] \
            if os.path.isdir(posts_dir) else []
        hint = f" candidates for this date: {candidates}" if candidates else ""
        sys.exit(f"error: {note_path} does not exist.\n"
                  f"This script updates an EXISTING post note's Performance/Audience "
                  f"sections -- it never creates a new post note from scratch.{hint}")

    sheets = load_cells(xlsx_path)
    fields = find_scalar_labels(sheets)
    demo = find_demographics(sheets)
    er_derived = derive_engagement_rate(fields)

    # Merge forward: any field this export didn't carry keeps the note's
    # existing value rather than being blanked -- a partial re-ingest must
    # never destroy previously-known data.
    _, _, old_perf = bd.parse_post(note_path)
    carried = []
    for _, key, old_key, _fmt, _bold in POST_PERF_FIELDS:
        if fields.get(key) in (None, "") and old_perf.get(old_key, "") != "":
            fields[key] = old_perf[old_key]
            carried.append(key)

    print("Parsed fields (confirm against the source file before trusting this write):")
    for _, key, _old_key, fmt, _bold in POST_PERF_FIELDS:
        suffix = "  (DERIVED: engagements/impressions*100, not in export)" \
            if key == "engagement_rate" and er_derived else ""
        print(f"  {key:20s} = {fmt(fields.get(key, ''))}{suffix}")
    if carried:
        print(f"  (kept from existing note, not in this export: {', '.join(carried)})")
    if demo:
        print("Parsed demographics buckets:", list(demo.keys()))
    else:
        print("DATA QUALITY -- no demographics buckets found, Audience snapshot left unchanged")

    with open(note_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Replace only the TABLE inside ## Performance, not the whole section --
    # a note can carry hand-written prose before/after the table (e.g. a
    # "snapshot updated, Nth capture" note), which a whole-section overwrite
    # would silently delete.
    new_table = render_table_only(fields)
    if re.search(r"^## Performance\b", text, flags=re.MULTILINE):
        if PERF_TABLE_RE.search(text):
            text = PERF_TABLE_RE.sub(lambda _m: new_table, text, count=1)
        else:
            text = re.sub(r"(^## Performance\s*\n)",
                           lambda m: m.group(1) + "\n" + new_table + "\n",
                           text, count=1, flags=re.MULTILINE)
    else:
        text = text.rstrip("\n") + "\n\n## Performance\n\n" + new_table + "\n"

    if demo:
        annotated = audience_section_has_annotations(text)
        if annotated:
            print(f"DATA QUALITY -- Audience snapshot has hand-written commentary on: "
                  f"{', '.join(annotated)} -- left UNCHANGED to avoid destroying it. "
                  f"Update those lines by hand if the underlying numbers moved.")
        else:
            new_demo = render_audience_snapshot(demo)
            if re.search(r"^## Audience snapshot.*?\n.*?(?=^## |\Z)", text, flags=re.DOTALL | re.MULTILINE):
                text = re.sub(r"^## Audience snapshot.*?\n.*?(?=^## |\Z)",
                               lambda _m: new_demo + "\n",
                               text, flags=re.DOTALL | re.MULTILINE)
            else:
                text = text.rstrip("\n") + "\n\n" + new_demo

    with open(note_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"\nupdated -> {note_path}\n"
          f"run linkedin-viral-scheduler/scripts/viral_metrics.py next to refresh "
          f"viral-metrics.tsv with this post.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inspect", metavar="FILE")
    ap.add_argument("--account", metavar="FILE")
    ap.add_argument("--week-start", type=lambda s: date.fromisoformat(s))
    ap.add_argument("--week-end", type=lambda s: date.fromisoformat(s))
    ap.add_argument("--account-tsv", default=DEFAULT_ACCOUNT_TSV)
    ap.add_argument("--post", metavar="FILE")
    ap.add_argument("--date", help="YYYYMMDD, matches the vault note filename prefix")
    ap.add_argument("--slug", help="matches the vault note filename suffix")
    ap.add_argument("--posts-dir", default=VAULT_POSTS_DIR)
    args = ap.parse_args()

    if args.inspect:
        inspect(args.inspect)
    elif args.account:
        if not (args.week_start and args.week_end):
            sys.exit("error: --account requires --week-start and --week-end (YYYY-MM-DD)")
        ingest_account(args.account, args.week_start, args.week_end,
                        os.path.normpath(args.account_tsv))
    elif args.post:
        if not (args.date and args.slug):
            sys.exit("error: --post requires --date YYYYMMDD and --slug")
        ingest_post(args.post, args.date, args.slug, args.posts_dir)
    else:
        ap.error("one of --inspect, --account, --post is required")


if __name__ == "__main__":
    main()
