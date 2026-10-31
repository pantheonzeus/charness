#!/usr/bin/env python3
"""
viral_metrics.py — score every published LinkedIn post on the 10 post-hoc
viral & quality metrics (see references/viral-metrics.md, the authoritative
spec this script implements).

Family A (1-7): measured outcomes, computed from each post's `## Performance`
table and `## Audience snapshot` demographics.
Family B (8-10): leading content predictors, imported — never re-implemented —
from the sibling `prepublish_audit.py` (score_sovereignty/score_saveworthiness/
score_conversation_trigger/score_buyer_dialect), same reuse convention build_dataset.py already
uses for the ship-gate scorer.

Usage:
  viral_metrics.py [--posts DIR] [--out FILE]

Writes viral-metrics.tsv (machine-readable, one row per post) and prints a
ranked human summary to stdout. Never fabricates a value it can't measure —
a post missing demographics gets a blank #6/#7, listed under DATA QUALITY,
not silently scored 0.
"""

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUDIT_DIR = os.path.normpath(
    os.path.join(HERE, "..", "..", "linkedin-viral-scheduler", "scripts")
)
CALIB_DIR = os.path.normpath(
    os.path.join(HERE, "..", "..", "linkedin-scoring-calibration", "scripts")
)
for p in (AUDIT_DIR, CALIB_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    import prepublish_audit as audit
except ImportError:
    sys.exit(f"error: cannot import prepublish_audit from {AUDIT_DIR}")

try:
    import build_dataset as bd  # reuse parse_post()/num(), never re-forked
except ImportError:
    sys.exit(f"error: cannot import build_dataset from {CALIB_DIR}")

DEFAULT_POSTS = os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "..", "..", "cbrain", "notes", "LinkedIn-Posts")
)

# Decision-maker density / Buyer-Weighted Engagement (#6-7) are computed by
# build_dataset.buyer_metrics() — the single source of truth, also used by
# the calibration skill's dataset.tsv. Not re-implemented here; see that
# module's docstring for the demographics-parsing rationale.


def rate_per_k(numer, denom):
    if denom in ("", None) or denom == 0:
        return ""
    return round(numer / denom * 1000, 2)


def safe_div(numer, denom):
    if denom in ("", None) or denom == 0:
        return ""
    return round(numer / denom, 3)


COLUMNS = [
    "file", "date", "impressions", "engagement_rate",
    # Family A
    "save_rate", "conversation_density", "amplification_rate",
    "follower_conversion", "profile_pull_rate", "decision_maker_density",
    "buyer_weighted_engagement",
    # Family B
    "sovereignty", "saveworthiness", "conversation_trigger", "buyer_dialect",
    # flags
    "has_demographics",
]


def score_post(path):
    fm, body, perf = bd.parse_post(path)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    def num_perf(key, cast=int):
        return bd.num(perf.get(key, ""), cast)

    impressions = num_perf("impressions")
    members_reached = num_perf("members_reached")
    reactions = num_perf("reactions")
    saves = num_perf("saves")
    sends = num_perf("sends")
    reposts = num_perf("reposts")
    comments = num_perf("comments")
    followers_gained = num_perf("followers_gained")
    profile_viewers = num_perf("profile_viewers")
    engagement_rate = bd.num(perf.get("engagement_rate", fm.get("engagement_rate", "")), float)

    save_rate = rate_per_k(saves, impressions) if isinstance(saves, int) and isinstance(impressions, int) else ""
    conversation_density = safe_div(comments, reactions) if isinstance(comments, int) and isinstance(reactions, int) else ""
    amplification_rate = (
        rate_per_k(reposts + sends, impressions)
        if isinstance(reposts, int) and isinstance(sends, int) and isinstance(impressions, int)
        else ""
    )
    follower_conversion = (
        rate_per_k(followers_gained, members_reached)
        if isinstance(followers_gained, int) and isinstance(members_reached, int)
        else ""
    )
    profile_pull_rate = (
        rate_per_k(profile_viewers, members_reached)
        if isinstance(profile_viewers, int) and isinstance(members_reached, int)
        else ""
    )

    dmd, buyer_weighted, has_demo = bd.buyer_metrics(text, engagement_rate)

    sov_score, _ = audit.score_sovereignty(body)
    sav_score, _ = audit.score_saveworthiness(body)
    conv_score, _ = audit.score_conversation_trigger(body)
    dialect_score, _ = audit.score_buyer_dialect(body)

    return {
        "file": os.path.basename(path),
        "date": fm.get("date", os.path.basename(path)[:8]),
        "impressions": impressions,
        "engagement_rate": engagement_rate,
        "save_rate": save_rate,
        "conversation_density": conversation_density,
        "amplification_rate": amplification_rate,
        "follower_conversion": follower_conversion,
        "profile_pull_rate": profile_pull_rate,
        "decision_maker_density": dmd,
        "buyer_weighted_engagement": buyer_weighted,
        "sovereignty": sov_score,
        "saveworthiness": sav_score,
        "conversation_trigger": conv_score,
        "buyer_dialect": dialect_score,
        "has_demographics": 1 if has_demo else 0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--posts", default=DEFAULT_POSTS)
    ap.add_argument("--out", default=os.path.join(HERE, "..", "viral-metrics.tsv"))
    args = ap.parse_args()

    if not os.path.isdir(args.posts):
        sys.exit(f"error: posts dir not found: {args.posts}")

    files = sorted(
        f for f in os.listdir(args.posts)
        if re.match(r"\d{8}-.+\.md$", f) and f != "LinkedIn-Posts-Index.md"
    )
    if not files:
        sys.exit(f"error: no post files matched in {args.posts}")

    rows = [score_post(os.path.join(args.posts, f)) for f in files]

    out_path = os.path.normpath(args.out)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\t".join(COLUMNS) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in COLUMNS) + "\n")

    print(f"wrote {len(rows)} rows -> {out_path}\n")

    missing_demo = [r["file"] for r in rows if not r["has_demographics"]]
    if missing_demo:
        print(f"DATA QUALITY — no ## Audience snapshot section (metrics #6/#7 blank): "
              f"{', '.join(missing_demo)}\n")

    def top(key, n=5, reverse=True):
        scored = [r for r in rows if r[key] != ""]
        scored.sort(key=lambda r: r[key], reverse=reverse)
        return scored[:n]

    print("=== Buyer-Weighted Engagement (north-star) — top 5 ===")
    for r in top("buyer_weighted_engagement"):
        print(f"  {r['buyer_weighted_engagement']:>6}  {r['file']}  "
              f"(raw ER={r['engagement_rate']}%, decision-maker density={r['decision_maker_density']}%)")

    print("\n=== Save Rate (per 1k impr) — top 5 ===")
    for r in top("save_rate"):
        print(f"  {r['save_rate']:>6}  {r['file']}")

    print("\n=== Conversation Density (comments/reactions) — top 5 ===")
    for r in top("conversation_density"):
        print(f"  {r['conversation_density']:>6}  {r['file']}")

    print("\n=== Sovereignty/EU-Framing Signal — top 5 ===")
    for r in top("sovereignty"):
        print(f"  {r['sovereignty']:>6}  {r['file']}")

    print("\n=== Save-Worthiness — top 5 ===")
    for r in top("saveworthiness"):
        print(f"  {r['saveworthiness']:>6}  {r['file']}")

    print("\n=== Conversation-Trigger Score — top 5 ===")
    for r in top("conversation_trigger"):
        print(f"  {r['conversation_trigger']:>6}  {r['file']}")

    # Family B #11 — predicts Decision-Maker Density (#6), not engagement rate.
    print("\nTop Buyer-Dialect Density (audience lever, not a resonance lever):")
    for r in top("buyer_dialect"):
        print(f"  {r['buyer_dialect']:>6}  {r['file']}")


if __name__ == "__main__":
    main()
