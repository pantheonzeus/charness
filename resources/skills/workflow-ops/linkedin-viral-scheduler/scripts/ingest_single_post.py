#!/usr/bin/env python3
"""
Ingest a LinkedIn **SinglePostAnalytics_*.xlsx** export and close the loop on one
published post: pre-publish prediction (Scorecard B composite) vs measured outcome
(Scorecard D).

Why this exists: until 2026-08-19 the loop could score a *draft* three ways and had
no mechanical path back from a *published* post's analytics. The 2026-08-19 post
scored composite 98.5 pre-publish and was served to 288 people — a gap the library
could describe but not record. See references/engagement-learnings.md Rule 7.

Usage:
  ingest_single_post.py <SinglePostAnalytics_*.xlsx> [--slug NAME] [--composite N]

Prints one JSON line + a human summary, and appends a row to
output/linkedin/post-outcomes.tsv (created with a header if absent).

Enforces the Scorecard D **volume floor** (rubric.md): Buyer-Weighted Engagement is
never emitted without impressions as a share of the account's rolling median, and a
post under 50% of median is flagged `distribution_failure` regardless of BWE.

Density/BWE reuse linkedin-scoring-calibration/scripts/build_dataset.py as the single
source of truth for DECISION_SENIORITY, TARGET_INDUSTRY_KEYWORDS and clamp() — this
script must never re-implement them (same rule viral_metrics.py already follows).
"""

import json
import os
import statistics
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
CALIB = os.path.join(REPO, "resources", "skills", "workflow-ops",
                     "linkedin-scoring-calibration", "scripts")
sys.path.insert(0, CALIB)

try:
    from build_dataset import DECISION_SENIORITY, TARGET_INDUSTRY_KEYWORDS, clamp
except ImportError:  # pragma: no cover - surfaced, never silently re-implemented
    sys.exit("cannot import build_dataset.py — density constants live there, "
             f"expected at {CALIB}")

OUTCOMES = os.path.join(REPO, "output", "linkedin", "post-outcomes.tsv")
COLUMNS = [
    "date", "slug", "post_url", "impressions", "members_reached", "engagements",
    "reactions", "comments", "reposts", "saves", "sends", "profile_viewers",
    "followers_gained", "engagement_rate", "senior_share", "industry_share",
    "decision_maker_density", "bwe", "impr_vs_median_pct", "verdict",
    "composite_predicted",
]

# Metric labels as LinkedIn writes them in the single-post export. Matched
# case-insensitively on the row's first cell, same header-label discipline as
# linkedin-weekly-review's parser (never positional).
METRIC_LABELS = {
    "impressions": "impressions",
    "members reached": "members_reached",
    "social engagements": "engagements",
    "reactions": "reactions",
    "comments": "comments",
    "reposts": "reposts",
    "saves": "saves",
    "sends on linkedin": "sends",
    "profile viewers from this post": "profile_viewers",
    "followers gained from this post": "followers_gained",
}


def parse_workbook(path):
    try:
        import openpyxl
    except ImportError:
        sys.exit("openpyxl required: python3 -m pip install --user openpyxl")

    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.worksheets[0]

    post = {k: 0 for k in METRIC_LABELS.values()}
    post["post_url"] = ""
    post["date"] = ""
    demo = {"seniority": [], "industry": [], "company size": [], "location": []}
    section = None

    for row in ws.iter_rows(values_only=True):
        cells = [("" if c is None else str(c).strip()) for c in row]
        if not any(cells):
            continue
        head = cells[0].lower()
        val = cells[1] if len(cells) > 1 else ""

        if head == "post url":
            post["post_url"] = val
        elif head == "post date":
            post["date"] = val
        elif head in METRIC_LABELS:
            try:
                post[METRIC_LABELS[head]] = int(float(str(val).replace(",", "")))
            except (ValueError, TypeError):
                pass
        elif head in ("location", "seniority", "industry", "company size"):
            # demographic rows are: Category | Value | NN%
            pct = cells[2] if len(cells) > 2 else ""
            if pct.endswith("%"):
                try:
                    demo[head].append((val, float(pct.rstrip("%"))))
                except ValueError:
                    pass
        elif head in ("discovery", "engagement", "profile activity",
                      "post viewer demographics"):
            section = head

    return post, demo


def main():
    args = [a for a in sys.argv[1:]]
    if not args:
        sys.exit(__doc__)

    path = args[0]
    slug = ""
    composite = ""
    if "--slug" in args:
        slug = args[args.index("--slug") + 1]
    if "--composite" in args:
        composite = args[args.index("--composite") + 1]

    post, demo = parse_workbook(path)

    impressions = post["impressions"]
    if not impressions:
        sys.exit("no impressions found — is this a SinglePostAnalytics export?")

    er = round(100.0 * post["engagements"] / impressions, 3)

    senior = sum(p for label, p in demo["seniority"]
                 if label.strip().lower() in DECISION_SENIORITY)
    industry = sum(p for label, p in demo["industry"]
                   if any(kw in label.lower() for kw in TARGET_INDUSTRY_KEYWORDS))
    density = round((senior + industry) / 2, 1)
    bwe = round(er * clamp(density / 15.0, 0.4, 2.0), 3)

    # --- volume floor (rubric.md, Scorecard D) -------------------------------
    prior = []
    if os.path.exists(OUTCOMES):
        with open(OUTCOMES, encoding="utf-8") as f:
            rows = [l.rstrip("\n").split("\t") for l in f][1:]
            idx = COLUMNS.index("impressions")
            for r in rows:
                if len(r) > idx:
                    try:
                        prior.append(int(r[idx]))
                    except ValueError:
                        pass
    median = statistics.median(prior) if prior else None
    if median:
        share = round(100.0 * impressions / median)
        verdict = "distribution_failure" if share < 50 else "ok"
    else:
        share, verdict = "", "no_baseline"

    rec = {
        "date": post["date"], "slug": slug, "post_url": post["post_url"],
        "impressions": impressions, "members_reached": post["members_reached"],
        "engagements": post["engagements"], "reactions": post["reactions"],
        "comments": post["comments"], "reposts": post["reposts"],
        "saves": post["saves"], "sends": post["sends"],
        "profile_viewers": post["profile_viewers"],
        "followers_gained": post["followers_gained"],
        "engagement_rate": er, "senior_share": senior, "industry_share": industry,
        "decision_maker_density": density, "bwe": bwe,
        "impr_vs_median_pct": share, "verdict": verdict,
        "composite_predicted": composite,
    }

    os.makedirs(os.path.dirname(OUTCOMES), exist_ok=True)
    new = not os.path.exists(OUTCOMES)
    with open(OUTCOMES, "a", encoding="utf-8") as f:
        if new:
            f.write("\t".join(COLUMNS) + "\n")
        f.write("\t".join(str(rec[c]) for c in COLUMNS) + "\n")

    print(json.dumps(rec))
    floor = f" | impressions {share}% of median -> {verdict}" if median else \
            " | no median yet (first row)"
    print(f"impr={impressions} reached={post['members_reached']} er={er}% "
          f"density={density} BWE={bwe}{floor}")
    if composite:
        print(f"predicted composite {composite} -> measured BWE {bwe} "
              f"({verdict}) — the pre-publish gates do not predict reach; "
              f"log the pair, do not tune a weight on n=1.")


if __name__ == "__main__":
    main()
