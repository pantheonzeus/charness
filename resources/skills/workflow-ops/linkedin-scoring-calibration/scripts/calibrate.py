#!/usr/bin/env python3
"""
calibrate.py — the calibration engine for the LinkedIn two-gate scorer.

Ground truth per post = a BUYER-WEIGHTED ENGAGEMENT tercile computed on the
account's OWN history (buyer_weighted_engagement = engagement_rate x a
decision-maker-density multiplier; percentile-ranked, then split into
terciles Under / On / Over). The scorer's job is to predict that tercile from
the post's features. Calibration tunes the scorer config so predicted tier ==
actual tier.

Retargeted 2026-07-19 (was: a 50/50 reach x engagement blend). Raw reach is
deliberately NOT part of the label anymore — engagement-learnings.md Rule 4
("reach and audience quality are decoupled; reach is not the target") showed
the account's widest-reach post had its worst audience quality, so ranking
posts by impressions was rewarding exactly the wrong thing. See
linkedin-viral-scheduler/references/viral-metrics.md #6-7 for the
decision_maker_density / buyer_weighted_engagement formulas, and
references/methodology.md §1 here for the discontinuity this causes in
calibration-history.tsv (pre-2026-07-19 rows are not comparable to later ones).

Subcommands:
  label     show each post's blended outcome + tercile, and account baselines
  split     deterministic, stratified 75/25 train/test split -> train.txt/test.txt
  verify    THE autoresearch Verify command: print ONE number = train agreement
  evaluate  train + held-out test agreement + the train-vs-test overfit gap
  correlate which features actually move the outcome (what to improve), with caveats

Only `verify` prints a bare number to stdout (autoresearch parses stdout);
every other subcommand prints a human report. All diagnostics go to stderr.

Usage:
  calibrate.py label    [--data FILE] [--follower-base N]
  calibrate.py split    [--data FILE] [--train FILE] [--test FILE]
  calibrate.py verify   [--data FILE] --config FILE [--split train|test|all]
  calibrate.py evaluate [--data FILE] --config FILE
  calibrate.py correlate[--data FILE]
"""

import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA = os.path.join(HERE, "..", "dataset.tsv")
DEFAULT_CONFIG = os.path.join(HERE, "calibration.json")
DEFAULT_TRAIN = os.path.join(HERE, "..", "train.txt")
DEFAULT_TEST = os.path.join(HERE, "..", "test.txt")

TIERS = ["Under", "On", "Over"]
FEATURE_COLS = [
    "hook", "readability", "spacing", "aifluff", "composite", "substance",
    "hook_block_len", "wordcount", "avg_sentence_len", "sentence_len_stdev",
    "hashtags", "emoji_count", "personal_markers", "hard_anchors", "has_question",
]


def load_data(path):
    with open(os.path.normpath(path), "r", encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")
        rows = []
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            rows.append(dict(zip(header, line.split("\t"))))
    if not rows:
        sys.exit(f"error: no data rows in {path}")

    # Drop ingest-damaged rows (added 2026-08-18). Posts whose stored body lost its
    # line breaks score hook + spacing — 50% of the composite — off an artifact, so
    # training on them fits the paste, not the writing. See build_dataset.py's
    # formatting_intact(). Older dataset.tsv files predate the column; those are
    # passed through unfiltered rather than silently emptied, with a warning.
    if rows and "formatting_intact" in rows[0]:
        intact = [r for r in rows if r.get("formatting_intact") == "1"]
        dropped = len(rows) - len(intact)
        if dropped:
            print(f"note: dropped {dropped}/{len(rows)} ingest-damaged rows "
                  f"(formatting_intact=0); calibrating on n={len(intact)}.", file=sys.stderr)
        if not intact:
            sys.exit("error: every row is ingest-damaged — repair the post bodies "
                     "before calibrating (see build_dataset.py formatting_intact()).")
        rows = intact
    else:
        print("warn: dataset has no formatting_intact column — rebuild it with "
              "build_dataset.py; ingest-damaged posts may be inflating n.", file=sys.stderr)
    return rows


def fnum(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def pct_rank(values):
    """Map each value to its percentile rank in [0,1] (ties get midrank)."""
    n = len(values)
    out = []
    for v in values:
        lo = sum(1 for x in values if x < v)
        eq = sum(1 for x in values if x == v)
        out.append((lo + 0.5 * eq) / n)
    return out


def blended_outcome(rows):
    """Return list of buyer-weighted-engagement percentile ranks in [0,1],
    aligned to rows. Retargeted 2026-07-19 (was a 50/50 reach+engagement
    blend) — see the module docstring for why raw reach was dropped."""
    bwe = [fnum(r.get("buyer_weighted_engagement")) or 0.0 for r in rows]
    return pct_rank(bwe)


def terciles(blend):
    """Assign each blended score a tercile label over the full corpus."""
    n = len(blend)
    order = sorted(range(n), key=lambda i: blend[i])
    rank = {idx: pos for pos, idx in enumerate(order)}
    labels = []
    for i in range(n):
        p = rank[i]
        if p < n / 3:
            labels.append("Under")
        elif p < 2 * n / 3:
            labels.append("On")
        else:
            labels.append("Over")
    return labels


def predicted_tier(row, config):
    w = config["composite_weights"]
    wsum = sum(w.values()) or 1.0
    comp = sum(w[k] * (fnum(row.get(k)) or 0.0)
               for k in ("hook", "readability", "spacing", "aifluff")) / wsum
    sw = config["substance_weight"]
    substance = fnum(row.get("substance")) or 0.0
    pred = (1 - sw) * comp + sw * (substance * 10.0)
    c0, c1 = sorted(config["tier_cutoffs"])
    if pred < c0:
        return "Under", pred
    if pred < c1:
        return "On", pred
    return "Over", pred


def load_config(path):
    with open(os.path.normpath(path), "r", encoding="utf-8") as f:
        cfg = json.load(f)
    for k in ("composite_weights", "substance_weight", "tier_cutoffs"):
        if k not in cfg:
            sys.exit(f"error: config missing '{k}'")
    return cfg


def read_list(path):
    p = os.path.normpath(path)
    if not os.path.isfile(p):
        sys.exit(f"error: split file not found: {p} (run `calibrate.py split` first)")
    with open(p, "r", encoding="utf-8") as f:
        return {l.strip() for l in f if l.strip()}


def agreement(rows, config, keep_files=None):
    """Fraction of rows whose predicted tier == actual tercile."""
    truth = terciles(blended_outcome(rows))
    hit = tot = 0
    for i, r in enumerate(rows):
        if keep_files is not None and r["file"] not in keep_files:
            continue
        tot += 1
        pred, _ = predicted_tier(r, config)
        if pred == truth[i]:
            hit += 1
    return (hit / tot if tot else 0.0), hit, tot


# --- subcommands ---------------------------------------------------------

def cmd_label(args):
    rows = load_data(args.data)
    blend = blended_outcome(rows)
    truth = terciles(blend)
    impr = [fnum(r.get("impressions")) or 0 for r in rows]
    eng = [fnum(r.get("engagement_rate")) or 0 for r in rows]
    dmd = [fnum(r.get("decision_maker_density")) for r in rows]
    bwe = [fnum(r.get("buyer_weighted_engagement")) for r in rows]
    n = len(rows)

    def median(xs):
        s = sorted(xs)
        m = len(s) // 2
        return s[m] if len(s) % 2 else (s[m - 1] + s[m]) / 2

    print(f"# Buyer-weighted-engagement tercile per post (n={n})", file=sys.stderr)
    print(f"{'file':<44} {'impr':>6} {'eng%':>6} {'buyer%':>7} {'bwe':>6}  tier", file=sys.stderr)
    for i in sorted(range(n), key=lambda i: -blend[i]):
        dmd_s = f"{dmd[i]:>7.1f}" if dmd[i] is not None else "     n/a"
        bwe_s = f"{bwe[i]:>6.3f}" if bwe[i] is not None else "   n/a"
        print(f"{rows[i]['file']:<44} {int(impr[i]):>6} {eng[i]:>6.2f} "
              f"{dmd_s} {bwe_s}  {truth[i]}", file=sys.stderr)

    counts = {t: truth.count(t) for t in TIERS}
    fb = args.follower_base
    print("\n# Account baselines (evidence: the corpus itself)", file=sys.stderr)
    print(f"  posts: {n}", file=sys.stderr)
    print(f"  total impressions: {int(sum(impr))}", file=sys.stderr)
    print(f"  median impressions/post: {median(impr):.0f}", file=sys.stderr)
    print(f"  top-quartile impressions: {sorted(impr)[int(0.75*(n-1))]:.0f}", file=sys.stderr)
    print(f"  blended engagement rate: {100*sum(fnum(r.get('social_engagements')) or 0 for r in rows)/max(1,sum(impr)):.2f}%",
          file=sys.stderr)
    print(f"  reach-per-follower @ {fb} followers: median {median(impr)/fb:.2f}x, "
          f"top {max(impr)/fb:.2f}x", file=sys.stderr)
    print(f"  tercile counts: {counts}", file=sys.stderr)
    print("label: OK", file=sys.stderr)


def cmd_split(args):
    rows = load_data(args.data)
    truth = terciles(blended_outcome(rows))
    idx = list(range(len(rows)))
    # Stratified + deterministic: sort by (tier, date), take every 4th as test.
    tier_rank = {t: i for i, t in enumerate(TIERS)}
    idx.sort(key=lambda i: (tier_rank[truth[i]], rows[i]["date"], rows[i]["file"]))
    test, train = [], []
    for pos, i in enumerate(idx):
        (test if pos % 4 == 3 else train).append(rows[i]["file"])
    with open(os.path.normpath(args.train), "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(train)) + "\n")
    with open(os.path.normpath(args.test), "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(test)) + "\n")
    print(f"train: {len(train)} posts -> {os.path.normpath(args.train)}", file=sys.stderr)
    print(f"test:  {len(test)} posts -> {os.path.normpath(args.test)}", file=sys.stderr)
    if len(test) < 3:
        print("warn: test set < 3 posts — accuracy on it is coarse; treat as directional.",
              file=sys.stderr)
    print("split: OK", file=sys.stderr)


def cmd_verify(args):
    rows = load_data(args.data)
    config = load_config(args.config)
    keep = None
    if args.split == "train":
        keep = read_list(args.train)
    elif args.split == "test":
        keep = read_list(args.test)
    acc, hit, tot = agreement(rows, config, keep)
    print(f"[verify] split={args.split} agreement={acc:.4f} ({hit}/{tot})", file=sys.stderr)
    print(f"{acc:.4f}")  # the ONLY stdout line — autoresearch reads this


def cmd_evaluate(args):
    rows = load_data(args.data)
    config = load_config(args.config)
    tr, trh, trt = agreement(rows, config, read_list(args.train))
    te, teh, tet = agreement(rows, config, read_list(args.test))
    gap = tr - te
    print(f"train agreement: {tr:.4f} ({trh}/{trt})", file=sys.stderr)
    print(f"test  agreement: {te:.4f} ({teh}/{tet})", file=sys.stderr)
    print(f"overfit gap (train - test): {gap:+.4f}", file=sys.stderr)
    if tet < 3:
        print(f"CAVEAT: test n={tet}. Resolution is 1/{tet}; a single post flips it "
              f"{100/tet:.0f} points. This is DIRECTIONAL, not a validated 98%.", file=sys.stderr)
    if gap > 0.20:
        print("WARN: gap > 0.20 — the config is overfitting the train set.", file=sys.stderr)
    print(f"{te:.4f}")


def pearson(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pairs)
    if n < 3:
        return None
    mx = sum(p[0] for p in pairs) / n
    my = sum(p[1] for p in pairs) / n
    sxx = sum((p[0] - mx) ** 2 for p in pairs)
    syy = sum((p[1] - my) ** 2 for p in pairs)
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pairs)
    if sxx == 0 or syy == 0:
        return 0.0
    return sxy / math.sqrt(sxx * syy)


def cmd_correlate(args):
    rows = load_data(args.data)
    blend = blended_outcome(rows)
    n = len(rows)
    print(f"# Feature -> blended-outcome correlation (Pearson r), n={n}", file=sys.stderr)
    print(f"# CAVEAT: n={n} is tiny. |r| below ~{1.96/math.sqrt(n):.2f} is not "
          f"distinguishable from noise. Read as DIRECTION, not proof.", file=sys.stderr)
    scored = []
    for col in FEATURE_COLS:
        r = pearson([fnum(rw.get(col)) for rw in rows], blend)
        if r is not None:
            scored.append((col, r))
    for col, r in sorted(scored, key=lambda t: -abs(t[1])):
        flag = "" if abs(r) >= 1.96 / math.sqrt(n) else "  (noise)"
        print(f"  {col:<20} r={r:+.3f}{flag}", file=sys.stderr)
    # A second lens: what within-post signal precedes reach?
    print("\n# Engagement-shape lens (do comments/saves precede reach?)", file=sys.stderr)
    impr = [fnum(rw.get("impressions")) for rw in rows]
    for col in ("comments", "reactions", "reposts", "saves"):
        r = pearson([fnum(rw.get(col)) for rw in rows], impr)
        if r is not None:
            print(f"  {col:<20} r(vs impressions)={r:+.3f}", file=sys.stderr)
    print("correlate: OK", file=sys.stderr)


def read_results(path):
    """Parse an autoresearch-schema results.tsv -> (direction, list-of-row-dicts)."""
    p = os.path.normpath(path)
    if not os.path.isfile(p):
        return None, []
    direction = "higher_is_better"
    header, rows = None, []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            if line.startswith("#"):
                if "metric_direction:" in line:
                    direction = line.split("metric_direction:", 1)[1].strip()
                continue
            cells = line.split("\t")
            if header is None:
                header = cells
                continue
            rows.append(dict(zip(header, cells)))
    return direction, rows


def cmd_report(args):
    rows = load_data(args.data)
    n = len(rows)
    blend = blended_outcome(rows)
    truth = terciles(blend)
    base_cfg = load_config(args.baseline_config)
    final_cfg = load_config(args.config)
    train_files = read_list(args.train) if os.path.isfile(os.path.normpath(args.train)) else None
    test_files = read_list(args.test) if os.path.isfile(os.path.normpath(args.test)) else None

    tr0, _, trt = agreement(rows, base_cfg, train_files)
    te0, _, tet = agreement(rows, base_cfg, test_files)
    tr1, trh, _ = agreement(rows, final_cfg, train_files)
    te1, teh, _ = agreement(rows, final_cfg, test_files)
    gap = tr1 - te1
    _, res_rows = read_results(args.results)
    iters = max((int(r.get("iteration", 0)) for r in res_rows), default=0)
    stop = next((r.get("description", "") for r in reversed(res_rows)
                 if r.get("status") in ("converged", "budget-exhausted", "plateau")), "n/a")
    judged = sum(1 for r in rows if r.get("substance_source") == "judged")

    impr = [fnum(r.get("impressions")) or 0 for r in rows]

    def median(xs):
        s = sorted(xs); m = len(s) // 2
        return s[m] if len(s) % 2 else (s[m - 1] + s[m]) / 2

    L = []
    L.append(f"# LinkedIn Scoring Calibration — Report ({args.date})\n")
    updated = "yes" if args.scorer_updated else "no (gate not met — see the gate note below)"
    L.append(f"**Run summary** · iterations: {iters} · stop: {stop or 'n/a'} · "
             f"train agreement {tr0:.0%}→**{tr1:.0%}** · test {te0:.0%}→**{te1:.0%}** · "
             f"overfit gap {gap:+.0%} · live scorer updated: {updated}\n")
    if judged < n:
        L.append(f"> ⚠️ Substance judged for {judged}/{n} posts (rest neutral-default). "
                 f"Run the substance pass for a meaningful calibration.\n")

    L.append("## The honest ceiling — read this first\n")
    L.append(f"n = {n} posts ({trt} train / {tet} test). A {tet}-post test set has "
             f"resolution 1/{tet} — one post flips it {100//max(1,tet)} points. **There is no "
             f"*validated* 98% at this n; the arithmetic forbids it.** 98% is the north-star "
             f"reached as the corpus grows — tracked run-over-run in "
             f"`calibration-history.tsv`. Chance for 3 balanced terciles is ~33%.\n")

    L.append("## Account baselines (evidence: the corpus itself)\n")
    L.append(f"- posts: {n} · total impressions: {int(sum(impr))}")
    L.append(f"- median impressions/post: {median(impr):.0f} · top-quartile: "
             f"{sorted(impr)[int(0.75*(n-1))]:.0f}")
    eng_tot = sum(fnum(r.get('social_engagements')) or 0 for r in rows)
    L.append(f"- blended engagement rate: {100*eng_tot/max(1,sum(impr)):.2f}%\n")

    L.append("## Before → after (what the loop changed)\n")
    L.append("| Knob | Baseline (live scorer) | Calibrated |")
    L.append("|---|---|---|")
    for k in ("hook", "readability", "spacing", "aifluff"):
        L.append(f"| composite_weights.{k} | {base_cfg['composite_weights'][k]} | "
                 f"{final_cfg['composite_weights'][k]} |")
    L.append(f"| substance_weight | {base_cfg['substance_weight']} | {final_cfg['substance_weight']} |")
    L.append(f"| tier_cutoffs | {base_cfg['tier_cutoffs']} | {final_cfg['tier_cutoffs']} |\n")

    L.append("## Iteration narrative (the loop's reasoning)\n")
    if res_rows:
        L.append("| # | metric | Δ | decision | reasoning |")
        L.append("|---|---|---|---|---|")
        for r in res_rows:
            L.append(f"| {r.get('iteration','')} | {r.get('metric','')} | "
                     f"{r.get('delta','')} | {r.get('status','')} | "
                     f"{r.get('description','').replace('|','/')} |")
        L.append("")
    else:
        L.append("_No results.tsv rows yet (loop not run)._\n")

    L.append("## Train vs test — reported separately, never merged\n")
    L.append(f"- **train**: {tr1:.1%} ({trh}/{trt})")
    L.append(f"- **test (held-out)**: {te1:.1%} ({teh}/{tet}) — resolution 1/{tet}")
    gap_note = "clean" if abs(gap) <= 0.20 else "OVERFIT (gap > 0.20 — do not ship)"
    L.append(f"- **overfit gap**: {gap:+.1%} — {gap_note}")
    gate_ok = abs(gap) <= 0.20 and te1 > te0 + 1e-9
    if args.scorer_updated:
        gate = "live scorer UPDATED — gap clean and held-out test improved."
    elif gate_ok:
        gate = "gate met but scorer left unchanged this run (see run notes)."
    elif abs(gap) > 0.20:
        gate = "live scorer NOT updated — overfit gap exceeds 0.20."
    else:
        gate = (f"live scorer NOT updated — overfit gap is clean but held-out test "
                f"did not improve over baseline ({te0:.0%}→{te1:.0%}). The conservative, "
                f"honest call at n={n}: train gains that the held-out set can't confirm don't ship.")
    L.append(f"- **gate decision**: {gate}\n")

    L.append("## What to improve (feature → outcome correlation)\n")
    thr = 1.96 / math.sqrt(n)
    scored = []
    for col in FEATURE_COLS:
        r = pearson([fnum(rw.get(col)) for rw in rows], blend)
        if r is not None:
            scored.append((col, r))
    L.append(f"_n={n}; |r| below ~{thr:.2f} is noise — read as direction, not proof._\n")
    L.append("| feature | r | |")
    L.append("|---|---|---|")
    for col, r in sorted(scored, key=lambda t: -abs(t[1]))[:8]:
        L.append(f"| {col} | {r:+.3f} | {'' if abs(r) >= thr else 'noise'} |")
    L.append("")
    for col in ("comments", "reactions"):
        r = pearson([fnum(rw.get(col)) for rw in rows], impr)
        if r is not None:
            L.append(f"- {col} vs impressions: r={r:+.3f} (does early engagement precede reach?)")
    L.append("")

    out = os.path.normpath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(L))

    # Append the run-over-run history row (create with header if absent).
    hist = os.path.normpath(args.history)
    os.makedirs(os.path.dirname(hist), exist_ok=True)
    new = not os.path.isfile(hist)
    with open(hist, "a", encoding="utf-8") as f:
        if new:
            f.write("date\titerations\ttrain_agreement\ttest_agreement\toverfit_gap\tscorer_updated\n")
        f.write(f"{args.date}\t{iters}\t{tr1:.4f}\t{te1:.4f}\t{gap:+.4f}\t"
                f"{'yes' if args.scorer_updated else 'no'}\n")

    print(f"report -> {out}", file=sys.stderr)
    print(f"history append -> {hist}", file=sys.stderr)
    print("report: OK", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("label", "split", "verify", "evaluate", "correlate", "report"):
        p = sub.add_parser(name)
        p.add_argument("--data", default=DEFAULT_DATA)
        if name in ("verify", "evaluate"):
            p.add_argument("--config", default=DEFAULT_CONFIG)
        if name in ("split", "verify", "evaluate", "report"):
            p.add_argument("--train", default=DEFAULT_TRAIN)
            p.add_argument("--test", default=DEFAULT_TEST)
        if name == "verify":
            p.add_argument("--split", choices=["train", "test", "all"], default="train")
        if name == "label":
            p.add_argument("--follower-base", type=float, default=2650.0)
        if name == "report":
            p.add_argument("--config", default=DEFAULT_CONFIG,
                           help="the final (calibrated) config")
            p.add_argument("--baseline-config", default=DEFAULT_CONFIG,
                           help="the iteration-0 snapshot to diff against")
            p.add_argument("--results", default=os.path.join(HERE, "..", "results.tsv"))
            p.add_argument("--out", default=os.path.join(HERE, "..", "..", "..", "..",
                           "..", "output", "linkedin", "calibration-report.md"))
            p.add_argument("--history", default=os.path.join(HERE, "..", "..", "..", "..",
                           "..", "output", "linkedin", "calibration-history.tsv"))
            p.add_argument("--date", default="")
            p.add_argument("--scorer-updated", action="store_true")
    args = ap.parse_args()
    {"label": cmd_label, "split": cmd_split, "verify": cmd_verify,
     "evaluate": cmd_evaluate, "correlate": cmd_correlate, "report": cmd_report}[args.cmd](args)


if __name__ == "__main__":
    main()
