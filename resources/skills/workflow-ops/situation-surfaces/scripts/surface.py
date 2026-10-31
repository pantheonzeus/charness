#!/usr/bin/env python3
"""Validator for situation surfaces — JSON that the console renders from its own component catalog.

  surface.py check <file.json>...    prints OK or the problems per file (exit 1 if any fails)

The desk renders only what passes here: known component types, bounded sizes, a confidence level
and sources on every block (verified needs at least one), no markup in any string.
"""
import json
import re
import sys
from pathlib import Path

CONF = {"verified", "likely", "unsure"}
STANCES = {"champion", "supporter", "neutral", "skeptic", "blocker", "unknown"}
TONES = {"info", "risk", "good"}
KINDS = {"past", "next", "deadline"}


def strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from strings(v)


def need(errs, where, cond, msg):
    if not cond:
        errs.append(f"{where}: {msg}")


def unit(v):
    return isinstance(v, (int, float)) and 0 <= v <= 1


def check_block(b, i, errs):
    w = f"block {i} ({b.get('type', '?')})"
    t = b.get("type")
    need(errs, w, b.get("confidence") in CONF, f"confidence must be one of {sorted(CONF)}")
    need(errs, w, isinstance(b.get("sources", []), list), "sources must be a list")
    if b.get("confidence") == "verified":
        need(errs, w, bool(b.get("sources")), "a verified block needs at least one source")
    if t == "Callout":
        need(errs, w, bool(str(b.get("text", "")).strip()), "needs text")
        need(errs, w, b.get("tone", "info") in TONES, f"tone must be one of {sorted(TONES)}")
    elif t == "MetricRow":
        items = b.get("items") or []
        need(errs, w, 1 <= len(items) <= 6, "1–6 items")
        for it in items:
            need(errs, w, it.get("label") and str(it.get("value", "")).strip(), "each item needs label and value")
    elif t == "RiskSheet":
        items = b.get("items") or []
        need(errs, w, 1 <= len(items) <= 8, "1–8 items")
        for it in items:
            need(errs, w, it.get("label") and unit(it.get("level")), "each item needs label and level 0–1")
    elif t == "StakeholderMap":
        ppl = b.get("people") or []
        need(errs, w, 1 <= len(ppl) <= 10, "1–10 people")
        for p in ppl:
            need(errs, w, p.get("name") and p.get("stance") in STANCES and unit(p.get("influence")),
                 f"each person needs name, stance ({'/'.join(sorted(STANCES))}) and influence 0–1")
    elif t == "Timeline":
        ev = b.get("events") or []
        need(errs, w, 1 <= len(ev) <= 10, "1–10 events")
        for e in ev:
            need(errs, w, re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(e.get("date", ""))) and e.get("label")
                 and e.get("kind", "past") in KINDS, "each event needs date YYYY-MM-DD, label, kind past/next/deadline")
    elif t == "DecisionCard":
        need(errs, w, bool(str(b.get("question", "")).strip()), "needs a question")
        need(errs, w, 2 <= len(b.get("options") or []) <= 4, "2–4 options")
        for o in b.get("options") or []:
            need(errs, w, bool(o.get("label")), "each option needs a label")
    elif t == "PersonCard":
        need(errs, w, bool(b.get("name")), "needs name")
    elif t == "DocList":
        docs = b.get("docs") or []
        need(errs, w, 1 <= len(docs) <= 6, "1–6 docs")
        for d in docs:
            need(errs, w, bool(d.get("name")), "each doc needs a name")
            if d.get("link"):
                need(errs, w, str(d["link"]).startswith("https://"), "links must be https://")
    else:
        errs.append(f"{w}: unknown type; allowed: Callout, MetricRow, RiskSheet, StakeholderMap, Timeline, DecisionCard, PersonCard, DocList")


def check(path):
    try:
        s = json.loads(Path(path).read_text())
    except (OSError, ValueError) as e:
        return [f"cannot read JSON: {e}"]
    errs = []
    need(errs, "surface", s.get("version") == 1, "version must be 1")
    need(errs, "surface", s.get("kind") in ("meeting", "answer"), "kind must be meeting or answer")
    need(errs, "surface", bool(str(s.get("title", "")).strip()), "needs a title")
    if s.get("kind") == "meeting":
        need(errs, "surface", s.get("uid") and s.get("fingerprint"), "a meeting surface needs uid and fingerprint (copy from TASK.json)")
        need(errs, "surface", Path(path).stem == s.get("uid"), "a meeting surface's filename must be <uid>.json")
    blocks = s.get("blocks") or []
    need(errs, "surface", 1 <= len(blocks) <= 6, f"{len(blocks)} blocks; keep 1–6 (2–4 is the target)")
    for i, b in enumerate(blocks, 1):
        check_block(b, i, errs)
    for b in s.get("basis") or []:
        need(errs, "basis", b.get("label") and b.get("ref"), "each entry needs label and ref")
    if any(re.search(r"<[a-zA-Z/!]", x) for x in strings(s)):
        errs.append("surface: no markup in strings (found '<tag')")
    return errs


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] != "check":
        print(__doc__)
        sys.exit(64)
    bad = 0
    for f in sys.argv[2:]:
        errs = check(f)
        bad += bool(errs)
        print(f"{f}: " + ("OK" if not errs else "\n".join("FAIL: " + e for e in errs)))
    sys.exit(1 if bad else 0)
