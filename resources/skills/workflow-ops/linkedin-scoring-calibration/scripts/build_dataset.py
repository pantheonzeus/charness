#!/usr/bin/env python3
"""
build_dataset.py — turn the vault's LinkedIn posts into one labelled table.

For each post in cbrain/notes/LinkedIn-Posts/YYYYMMDD-*.md it:
  1. extracts the verbatim `## Post` body + the `## Performance` metrics + frontmatter,
  2. scores the body with the LIVE deterministic scorer (imported, never
     re-implemented, from the sibling linkedin-viral-scheduler skill),
  3. writes one row of features + actual outcomes to dataset.tsv.

Substance (M1+M3) is a SUBJECTIVE feature — it is NOT computed here. It is
filled by a one-time file-backed judge pass (see SKILL.md §2) cached as a
2-column TSV (`file<TAB>substance`) passed via --substance. Absent, substance
defaults to a neutral 6 and the row is flagged so no one mistakes it for a
judged value.

This is the "real statistical data" deliverable: features on the left, the
outcomes they have to predict on the right, one post per row.

Also computes the buyer-quality outcome columns (added 2026-07-19, see the
sibling skill's `references/viral-metrics.md` #6-7): `decision_maker_density`
and `buyer_weighted_engagement` — parsed from each post's `## Audience
snapshot` demographics. This is the single source of truth for that formula;
`viral_metrics.py` imports it from here rather than recomputing it.

Usage:
  build_dataset.py [--posts DIR] [--substance FILE] [--out FILE]
"""

import argparse
import os
import re
import sys

# --- Reuse the live scorer's text-analysis functions verbatim. The tunable
# band/weight mapping lives in calibrate.py + calibration.json; the raw text
# analysis (word/sentence/hook/fluff detection) is the scorer's own code and
# we do not fork it. ---
HERE = os.path.dirname(os.path.abspath(__file__))
AUDIT_DIR = os.path.normpath(
    os.path.join(HERE, "..", "..", "linkedin-viral-scheduler", "scripts")
)
sys.path.insert(0, AUDIT_DIR)
try:
    import prepublish_audit as audit
except ImportError:
    sys.exit(
        f"error: cannot import prepublish_audit from {AUDIT_DIR}\n"
        "  the linkedin-viral-scheduler skill must sit beside this one."
    )

DEFAULT_POSTS = os.path.normpath(
    os.path.join(HERE, "..", "..", "..", "..", "..", "cbrain", "notes", "LinkedIn-Posts")
)

# Performance-table row label -> dataset column. Labels are matched
# case-insensitively after stripping markdown bold (**...**).
METRIC_MAP = {
    "impressions": "impressions",
    "members reached": "members_reached",
    "profile viewers from post": "profile_viewers",
    "followers gained": "followers_gained",
    "social engagements": "social_engagements",
    "reactions": "reactions",
    "comments": "comments",
    "reposts": "reposts",
    "saves": "saves",
    "sends": "sends",
}

FEATURE_COLS = [
    "hook", "readability", "spacing", "aifluff", "composite",  # live scorer sub-scores
    "hook_block_len", "wordcount", "avg_sentence_len", "sentence_len_stdev",
    "hashtags", "emoji_count", "personal_markers", "hard_anchors", "has_question",
    # 0 when the stored body lost its line breaks on ingest — see formatting_intact().
    # Rows with 0 must not train the scorer: half their composite is an artifact.
    "formatting_intact",
]
OUTCOME_COLS = [
    "impressions", "members_reached", "profile_viewers", "followers_gained",
    "social_engagements", "reactions", "comments", "reposts", "saves", "sends",
    "engagement_rate",
    # Buyer-quality outcomes (added 2026-07-19) — see buyer_metrics() below.
    "decision_maker_density", "buyer_weighted_engagement", "has_demographics",
]
COLUMNS = ["file", "date", "substance", "substance_source"] + FEATURE_COLS + OUTCOME_COLS

# --- Buyer-quality outcome (viral-metrics.md #6-7). Demographics are two
# independent marginal top-N lists (Seniority, Top industries) — never a
# cross-tab — so decision_maker_density is a documented proxy (mean of two
# marginal shares), not a true joint measurement. See viral-metrics.md for
# the full rationale. ---
DECISION_SENIORITY = {"director", "vp", "cxo", "partner", "owner"}
TARGET_INDUSTRY_KEYWORDS = [
    "manufactur", "machinery", "industrial", "automotive", "motor vehicle",
    "aerospace", "defense", "defence", "semiconductor", "appliances",
    "electronics", "energy",
]
DEMO_LABEL_RE = re.compile(r"^\*\*([^:]+):\*\*\s*(.+)$")
DEMO_ITEM_RE = re.compile(r"^(.*?)\s+(\d+(?:\.\d+)?)%$")


def parse_demographics(text):
    """Parse the '## Audience snapshot' bullet block into
    {section_label_lower: [(entry_label, pct), ...]}. Returns {} if the
    section is absent (caller must flag this, never treat as 0)."""
    m = re.search(r"^## Audience snapshot.*?\n(.*?)(?=^## |\Z)", text, flags=re.DOTALL | re.MULTILINE)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        line = line.lstrip("- ").strip()
        lm = DEMO_LABEL_RE.match(line)
        if not lm:
            continue
        label, rest = lm.group(1).strip().lower(), lm.group(2)
        items = []
        for chunk in rest.split("·"):
            chunk = chunk.strip().rstrip(".")
            im = DEMO_ITEM_RE.match(chunk)
            if im:
                items.append((im.group(1).strip(), float(im.group(2))))
        out[label] = items
    return out


def senior_share(demo):
    rows = demo.get("seniority", [])
    return sum(pct for label, pct in rows if label.strip().lower() in DECISION_SENIORITY)


def industry_fit_share(demo):
    rows = demo.get("top industries", [])
    total = 0.0
    for label, pct in rows:
        low = label.lower()
        if any(kw in low for kw in TARGET_INDUSTRY_KEYWORDS):
            total += pct
    return total


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def buyer_metrics(text, engagement_rate):
    """Return (decision_maker_density, buyer_weighted_engagement,
    has_demographics) for a post's raw file text (not just the ## Post body —
    demographics live in a later section). density/bwe are '' (not 0) when
    demographics are absent, so a missing section is never mistaken for a
    measured zero."""
    demo = parse_demographics(text)
    if not demo:
        return "", "", 0
    density = round((senior_share(demo) + industry_fit_share(demo)) / 2, 1)
    if isinstance(engagement_rate, float):
        multiplier = clamp(density / 15.0, 0.4, 2.0)
        bwe = round(engagement_rate * multiplier, 3)
    else:
        bwe = ""
    return density, bwe, 1


def parse_post(path):
    """Return (frontmatter dict, post_body str, performance dict)."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    fm = {}
    m = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip()

    # Post body = everything between the `## Post` heading and the next `## `.
    body = ""
    bm = re.search(r"^## Post\s*\n(.*?)(?=^## )", text, flags=re.DOTALL | re.MULTILINE)
    if bm:
        body = bm.group(1).strip()

    # Performance table.
    perf = {}
    pm = re.search(r"^## Performance\s*\n(.*?)(?=^## |\Z)", text, flags=re.DOTALL | re.MULTILINE)
    if pm:
        for row in re.findall(r"^\|(.+?)\|(.+?)\|\s*$", pm.group(1), flags=re.MULTILINE):
            label = re.sub(r"\*\*", "", row[0]).strip().lower()
            value = re.sub(r"\*\*", "", row[1]).strip()
            if label in ("metric", "---") or label.startswith("---"):
                continue
            if label in METRIC_MAP:
                perf[METRIC_MAP[label]] = value
            elif "engagement rate" in label:
                perf["engagement_rate"] = value
    return fm, body, perf


def num(s, cast=int):
    """Parse '1,252' / '2.24%' / '' -> number or ''."""
    if s is None:
        return ""
    s = s.replace(",", "").replace("%", "").strip()
    if s == "":
        return ""
    try:
        return cast(float(s)) if cast is int else cast(s)
    except ValueError:
        return ""


def formatting_intact(body):
    """False when the stored body lost its line breaks on ingest.

    Added 2026-08-18. 34 of 57 archived posts store the `## Post` body as one
    unbroken paragraph. A real LinkedIn post always carries line breaks, so a
    single-line body is an ingest artifact, not an authorial choice — and it
    silently corrupts the two heaviest-weighted scorer features: the hook block
    becomes the whole post (measured at 1051 chars on one sample, against a
    70-140 optimal band) and one-idea-per-line collapses. Hook is 30% of the
    composite and Spacing 20%, so half the composite is wrong for those rows.

    Measured on the 51 scorable posts: blob rows averaged hook 43.2 / composite
    70.8 with 0/28 clearing the >=85 gate; intact rows averaged hook 55.4 /
    composite 74.4 with 6/23 clearing it. Every post that passes the gate is one
    whose formatting survived. Training on the blob rows fits an ingest artifact.
    """
    return len([l for l in body.split("\n") if l.strip()]) > 2


def features_for(body):
    """Run the live scorer over the post body; return the calibration features."""
    lines = body.split("\n")
    sents = audit.sentences_of(body)
    hook, hook_detail = audit.score_hook(lines)
    read, read_detail, sent_lens = audit.score_readability(body)
    spacing, spacing_detail = audit.score_spacing(body, lines, max(1, len(sents)))
    aifluff, aifluff_detail = audit.score_ai_fluff(body, sent_lens)
    composite = round(0.30 * hook + 0.20 * read + 0.20 * spacing + 0.30 * aifluff, 1)

    # hook_block_len is embedded in the hook detail string "hook_block_len=NN ..."
    hbl = re.search(r"hook_block_len=(\d+)", hook_detail)
    return {
        "hook": hook, "readability": read, "spacing": spacing, "aifluff": aifluff,
        "composite": composite,
        "hook_block_len": int(hbl.group(1)) if hbl else "",
        "wordcount": read_detail["wordcount"],
        "avg_sentence_len": read_detail["avg_sentence_len"],
        "sentence_len_stdev": read_detail["sentence_len_stdev"],
        "hashtags": spacing_detail.get("hashtags", ""),
        "emoji_count": spacing_detail.get("emoji_count", ""),
        "personal_markers": aifluff_detail["personal_markers"],
        "hard_anchors": aifluff_detail["hard_anchors"],
        "has_question": 1 if "?" in body else 0,
        "formatting_intact": 1 if formatting_intact(body) else 0,
    }


def load_substance(path):
    cache = {}
    if not path:
        return cache
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#") or line.lower().startswith("file\t"):
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                cache[parts[0].strip()] = num(parts[1], float)
    return cache


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--posts", default=DEFAULT_POSTS)
    ap.add_argument("--substance", default=None,
                    help="TSV cache: file<TAB>substance (M1+M3, 2..10). Absent => neutral 6.")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "dataset.tsv"))
    args = ap.parse_args()

    if not os.path.isdir(args.posts):
        sys.exit(f"error: posts dir not found: {args.posts}")

    substance_cache = load_substance(args.substance)
    files = sorted(
        f for f in os.listdir(args.posts)
        if re.match(r"\d{8}-.+\.md$", f) and f != "LinkedIn-Posts-Index.md"
    )
    if not files:
        sys.exit(f"error: no post files matched in {args.posts}")

    rows = []
    for fname in files:
        fm, body, perf = parse_post(os.path.join(args.posts, fname))
        if not body:
            print(f"warn: no ## Post body in {fname}, skipping", file=sys.stderr)
            continue
        feats = features_for(body)
        base = os.path.basename(fname)
        if base in substance_cache:
            substance, src = substance_cache[base], "judged"
        else:
            substance, src = 6.0, "neutral-default"

        row = {c: "" for c in COLUMNS}
        row["file"] = base
        row["date"] = fm.get("date", base[:8])
        row["substance"] = substance
        row["substance_source"] = src
        row.update(feats)
        for c in OUTCOME_COLS:
            if c in ("decision_maker_density", "buyer_weighted_engagement", "has_demographics"):
                continue  # filled below, once engagement_rate is known
            if c == "engagement_rate":
                row[c] = num(perf.get(c, fm.get("engagement_rate", "")), float)
            else:
                row[c] = num(perf.get(c, ""))

        # Buyer-quality outcomes need the full file text (demographics live
        # past `## Post`/`## Performance`), not just the parsed body.
        with open(os.path.join(args.posts, fname), "r", encoding="utf-8") as f:
            full_text = f.read()
        density, bwe, has_demo = buyer_metrics(full_text, row["engagement_rate"])
        row["decision_maker_density"] = density
        row["buyer_weighted_engagement"] = bwe
        row["has_demographics"] = has_demo

        rows.append(row)

    out_path = os.path.normpath(args.out)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\t".join(COLUMNS) + "\n")
        for r in rows:
            f.write("\t".join(str(r[c]) for c in COLUMNS) + "\n")

    judged = sum(1 for r in rows if r["substance_source"] == "judged")
    print(f"wrote {len(rows)} rows -> {out_path}")
    print(f"substance: {judged} judged, {len(rows) - judged} neutral-default "
          f"({'OK' if judged == len(rows) else 'run the judge pass to fill the rest'})")
    missing_demo = [r["file"] for r in rows if not r["has_demographics"]]
    if missing_demo:
        print(f"demographics: {len(rows) - len(missing_demo)}/{len(rows)} have an "
              f"## Audience snapshot section — missing on: {', '.join(missing_demo)}")

    # Loud, never-silent report of the ingest-damaged rows (Charter §2: no silent
    # truncation). These rows are still written to the TSV — excluding them here
    # would hide the problem — but calibrate.py must filter on formatting_intact.
    broken = [r["file"] for r in rows if not r["formatting_intact"]]
    if broken:
        print(f"\n!! FORMATTING: {len(broken)}/{len(rows)} posts lost their line breaks on "
              f"ingest and are NOT valid training rows (hook + spacing = 50% of the "
              f"composite are artifacts on these).")
        print(f"!! Calibrate on the {len(rows) - len(broken)} intact rows only, and repair "
              f"the damaged bodies from each note's `url:` frontmatter.")
        print(f"!! damaged: {', '.join(broken)}")


if __name__ == "__main__":
    main()
