"""Deterministic half of the frame-shift demo: synthetic data, the hypothesis compiler, the
statistical test, and gates G1–G3. The model never touches anything in here; it only proposes
specs that this module validates and scores.

Synthetic world: occasions in a premium-spirits category. Five demand spaces are planted on the
"original frame" columns (need, setting, company…) and sealed as the known map. Four more
connections are planted on columns the original frame ignores (prior activity, weather, the
skip outcome, respondent-level repertoire). Only a reframed question can reach those.
"""
import math
import random

# ---------- schema ----------
CATS = {
    "age_band": ["18-24", "25-34", "35-44", "45-54", "55+"],
    "income_band": ["low", "mid", "high"],
    "region": ["urban", "suburban", "rural"],
    "household": ["single", "couple", "family"],
    "need_state": ["celebrate", "unwind", "socialize", "impress", "refresh", "ritual"],
    "setting": ["home", "bar", "restaurant", "friend_home", "outdoor"],
    "company": ["alone", "partner", "friends", "family", "colleagues"],
    "day_part": ["afternoon", "evening", "late_night"],
    "weekday": ["weekday", "weekend"],
    "channel": ["on_trade", "off_trade"],
    "weather": ["hot", "mild", "cold"],
    "trigger": ["planned", "spontaneous", "gift", "after_work", "sport_event", "meal"],
    "prior_activity": ["work", "sport", "cooking", "travel", "none"],
}
DESCRIBE = {
    "age_band": "respondent age band", "income_band": "household income band",
    "region": "where the respondent lives", "household": "household type",
    "need_state": "the need the respondent named for the occasion",
    "setting": "where the drink happened", "company": "who they were with",
    "day_part": "time of day", "weekday": "weekday or weekend", "channel": "bought in a venue (on_trade) or a shop (off_trade)",
    "weather": "weather that day", "trigger": "what prompted the occasion",
    "prior_activity": "what they did in the hour before",
    "n_occasions": "number of occasions the respondent logged (respondent unit only)",
    "repertoire_breadth": "number of distinct settings the respondent drank in (respondent unit only)",
}
OUTCOMES = {
    "premium": "share of occasions where a premium-tier bottle or serve was chosen",
    "spend_eur": "spend per occasion in EUR",
    "skipped": "share of occasions where premium was considered but the respondent bought standard instead",
}
OCC_COLS = list(CATS)
RESP_COLS = ["age_band", "income_band", "region", "household", "n_occasions", "repertoire_breadth"]
NUMERIC = {"n_occasions": (3, 9), "repertoire_breadth": (1, 5)}  # column → (min, max)

ORIGINAL_FRAME = {
    "id": "F0",
    "operator": "original",
    "question": "Which need states, settings and company drive premium choice on an occasion?",
    "unit": "occasion",
    "outcome": "premium",
    "columns": ["need_state", "setting", "company", "day_part", "age_band", "income_band", "channel"],
}

KNOWN_MAP = [  # the sealed map: what "your method" already found
    {"name": "Celebration night out", "unit": "occasion", "segment": [
        {"col": "need_state", "values": ["celebrate"]}, {"col": "setting", "values": ["bar"]}, {"col": "company", "values": ["friends"]}]},
    {"name": "Impress over dinner", "unit": "occasion", "segment": [
        {"col": "need_state", "values": ["impress"]}, {"col": "setting", "values": ["restaurant"]}]},
    {"name": "Solo wind-down", "unit": "occasion", "segment": [
        {"col": "need_state", "values": ["unwind"]}, {"col": "setting", "values": ["home"]}, {"col": "company", "values": ["alone"]}]},
    {"name": "Hosting friends at home", "unit": "occasion", "segment": [
        {"col": "need_state", "values": ["socialize"]}, {"col": "setting", "values": ["home"]}, {"col": "company", "values": ["friends"]}]},
    {"name": "Outdoor refresh", "unit": "occasion", "segment": [
        {"col": "need_state", "values": ["refresh"]}, {"col": "setting", "values": ["outdoor"]}]},
]

PLANTED = [  # ground truth for the demo's reveal; never shown to the model
    {"name": "Post-sport premium round", "operator": "cross distant variables", "unit": "occasion", "outcome": "premium",
     "segment": [{"col": "prior_activity", "values": ["sport"]}, {"col": "company", "values": ["friends"]}, {"col": "day_part", "values": ["evening"]}]},
    {"name": "Gift buyers who back out", "operator": "invert the outcome", "unit": "occasion", "outcome": "skipped",
     "segment": [{"col": "trigger", "values": ["gift"]}, {"col": "age_band", "values": ["25-34"]}, {"col": "channel", "values": ["off_trade"]}]},
    {"name": "Repertoire explorers", "operator": "change the unit", "unit": "respondent", "outcome": "premium",
     "segment": [{"col": "repertoire_breadth", "op": ">=", "value": 4}]},
    {"name": "Cold-night sipping ritual", "operator": "cross distant variables", "unit": "occasion", "outcome": "premium",
     "segment": [{"col": "weather", "values": ["cold"]}, {"col": "setting", "values": ["home"]}, {"col": "company", "values": ["partner"]}]},
]

OCCASIONS_PER_YEAR = 40_000_000  # synthetic market size the sample is scaled to (stated assumption)
CAPTURE = (0.05, 0.15)           # share of the gap a brand could plausibly close (stated assumption)
G3_MIN_EUR = 150_000             # low end of the € range must clear this (stated threshold)


def _pick(rng, xs, w=None):
    return rng.choices(xs, weights=w)[0]


def _sig(x):
    return 1 / (1 + math.exp(-x))


def generate(seed=7, n_resp=4000):
    rng = random.Random(seed)
    rows = []
    for r in range(n_resp):
        explorer = rng.random() < 0.18
        person = {
            "respondent_id": r,
            "age_band": _pick(rng, CATS["age_band"], [14, 24, 22, 20, 20]),
            "income_band": _pick(rng, CATS["income_band"], [30, 50, 20]),
            "region": _pick(rng, CATS["region"], [45, 35, 20]),
            "household": _pick(rng, CATS["household"], [35, 35, 30]),
        }
        settings_pool = CATS["setting"] if explorer else rng.sample(CATS["setting"], rng.choice([1, 2, 2, 3]))
        for _ in range(rng.randint(4, 9) if explorer else rng.randint(3, 7)):
            o = dict(person)
            o["setting"] = rng.choice(settings_pool)
            o["company"] = _pick(rng, CATS["company"], [15, 25, 35, 15, 10])
            o["day_part"] = _pick(rng, CATS["day_part"], [20, 55, 25])
            o["weekday"] = _pick(rng, CATS["weekday"], [55, 45])
            o["channel"] = "on_trade" if o["setting"] in ("bar", "restaurant") else "off_trade"
            o["weather"] = _pick(rng, CATS["weather"], [30, 40, 30])
            o["prior_activity"] = _pick(rng, CATS["prior_activity"], [30, 15, 15, 10, 30])
            o["trigger"] = _pick(rng, CATS["trigger"], [25, 20, 10, 20, 10, 15])
            if o["prior_activity"] == "sport":
                o["need_state"] = _pick(rng, CATS["need_state"], [10, 10, 15, 5, 55, 5])
            elif o["setting"] == "restaurant":
                o["need_state"] = _pick(rng, CATS["need_state"], [15, 10, 20, 40, 5, 10])
            else:
                o["need_state"] = _pick(rng, CATS["need_state"], [18, 22, 22, 8, 15, 15])

            z = -1.45 + (0.45 if o["income_band"] == "high" else 0) - (0.3 if o["income_band"] == "low" else 0)
            ns, st, co = o["need_state"], o["setting"], o["company"]
            z += 1.3 if (ns, st, co) == ("celebrate", "bar", "friends") else 0
            z += 1.4 if (ns, st) == ("impress", "restaurant") else 0
            z -= 0.9 if (ns, st, co) == ("unwind", "home", "alone") else 0
            z += 0.8 if (ns, st, co) == ("socialize", "home", "friends") else 0
            z -= 0.8 if (ns, st) == ("refresh", "outdoor") else 0
            z -= 0.35 if ns == "refresh" else 0
            # planted, outside the original frame
            z += 1.7 if (o["prior_activity"], co, o["day_part"]) == ("sport", "friends", "evening") else 0
            z += 1.3 if (o["weather"], st, co) == ("cold", "home", "partner") else 0
            z += 0.9 if explorer else 0
            o["premium"] = int(rng.random() < _sig(z))
            zs = -2.3 + (2.2 if (o["trigger"], o["age_band"], o["channel"]) == ("gift", "25-34", "off_trade") else 0)
            o["skipped"] = int(not o["premium"] and rng.random() < _sig(zs))
            o["spend_eur"] = round(max(4, rng.gauss(44, 9) if o["premium"] else rng.gauss(19, 5)), 2)
            rows.append(o)
    return rows


class World:
    """One synthetic dataset plus its frozen split. Split is by respondent so no person leaks across."""

    def __init__(self, seed=7, n_resp=4000):
        self.seed = seed
        self.rows = generate(seed, n_resp)
        rng = random.Random(seed + 1)
        ids = sorted({r["respondent_id"] for r in self.rows})
        rng.shuffle(ids)
        self.split_b = set(ids[: int(len(ids) * 0.4)])
        for i, r in enumerate(self.rows):
            r["_i"] = i
        self.occ = {"A": [r for r in self.rows if r["respondent_id"] not in self.split_b],
                    "B": [r for r in self.rows if r["respondent_id"] in self.split_b]}
        self.resp = {k: _respondents(v) for k, v in self.occ.items()}
        self.prem_eur = _mean([r["spend_eur"] for r in self.rows if r["premium"]])
        self.std_eur = _mean([r["spend_eur"] for r in self.rows if not r["premium"]])

    def summary(self):
        return {"rows": len(self.rows), "respondents": len({r["respondent_id"] for r in self.rows}),
                "rows_a": len(self.occ["A"]), "rows_b": len(self.occ["B"]),
                "columns": len(OCC_COLS), "outcomes": list(OUTCOMES),
                "premium_rate": round(_mean([r["premium"] for r in self.rows]), 3),
                "known_spaces": len(KNOWN_MAP), "seed": self.seed}


def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def _respondents(occ):
    by = {}
    for r in occ:
        by.setdefault(r["respondent_id"], []).append(r)
    out = []
    for rid, os_ in by.items():
        p = {c: os_[0][c] for c in ("age_band", "income_band", "region", "household")}
        p.update(respondent_id=rid, n_occasions=len(os_), repertoire_breadth=len({o["setting"] for o in os_}),
                 premium=_mean([o["premium"] for o in os_]), skipped=_mean([o["skipped"] for o in os_]),
                 spend_eur=_mean([o["spend_eur"] for o in os_]), _occ=[o["_i"] for o in os_])
        out.append(p)
    return out


# ---------- compile: the model's spec → a validated predicate ----------
def dictionary(columns, unit):
    """What the model is allowed to see about the data: names, meanings, legal values. Never rows."""
    out = {}
    for c in columns:
        if c in NUMERIC:
            out[c] = {"meaning": DESCRIBE[c], "type": "integer", "min": NUMERIC[c][0], "max": NUMERIC[c][1]}
        else:
            out[c] = {"meaning": DESCRIBE[c], "values": CATS[c]}
    return out


def legal_columns(unit):
    return RESP_COLS if unit == "respondent" else OCC_COLS


def compile_spec(h, frame):
    """Return (normalised spec, None) or (None, reason). This is the 'compile' step: anything the
    frame doesn't allow is rejected here, before a single row is touched."""
    unit, outcome = frame["unit"], frame["outcome"]
    seg = h.get("segment") or []
    if not 1 <= len(seg) <= 4:
        return None, "segment needs 1–4 conditions"
    clean = []
    for c in seg:
        col = c.get("col")
        if col not in frame["columns"]:
            return None, f"column '{col}' is outside this frame"
        if col in NUMERIC:
            op, v = c.get("op"), c.get("value")
            if op not in (">=", "<=") or not isinstance(v, (int, float)):
                return None, f"'{col}' needs op >= or <= and a number"
            clean.append({"col": col, "op": op, "value": v})
        else:
            vals = [v for v in (c.get("values") or []) if v in CATS[col]]
            if not vals or len(vals) == len(CATS[col]):
                return None, f"'{col}' values must be a proper subset of {CATS[col]}"
            clean.append({"col": col, "values": sorted(set(vals))})
    if h.get("direction") not in ("higher", "lower"):
        return None, "direction must be higher or lower"
    return {"unit": unit, "outcome": outcome, "segment": clean, "direction": h["direction"]}, None


def expressible_in_original(spec):
    """True if the original frame could already ask this. The frame-shift arm only gets credit for questions it can't."""
    f = ORIGINAL_FRAME
    return (spec["unit"] == f["unit"] and spec["outcome"] == f["outcome"]
            and all(c["col"] in f["columns"] for c in spec["segment"]))


def _match(row, seg):
    for c in seg:
        v = row[c["col"]]
        if "values" in c:
            if v not in c["values"]:
                return False
        elif (c["op"] == ">=" and v < c["value"]) or (c["op"] == "<=" and v > c["value"]):
            return False
    return True


def evaluate(world, spec, split):
    pop = world.resp[split] if spec["unit"] == "respondent" else world.occ[split]
    seg = [r for r in pop if _match(r, spec["segment"])]
    rest = [r for r in pop if not _match(r, spec["segment"])]
    y = spec["outcome"]
    a, b = [r[y] for r in seg], [r[y] for r in rest]
    if len(a) < 30 or len(b) < 30:
        return {"n": len(a), "seg": None, "rest": None, "lift": None, "p": 1.0, "rows": seg}
    ma, mb = _mean(a), _mean(b)
    va = sum((x - ma) ** 2 for x in a) / (len(a) - 1)
    vb = sum((x - mb) ** 2 for x in b) / (len(b) - 1)
    se = math.sqrt(va / len(a) + vb / len(b)) or 1e-9
    z = (ma - mb) / se
    p = math.erfc(abs(z) / math.sqrt(2))
    return {"n": len(a), "seg": ma, "rest": mb, "lift": (ma / mb) if mb else None, "p": p, "z": z, "rows": seg}


MIN_CELL, P_A, MIN_LIFT = 30, 0.01, 0.15


def inner_test(world, spec):
    """Step 5–6 of the inner loop, on split A only."""
    r = evaluate(world, spec, "A")
    if r["seg"] is None:
        return r, False, f"cell too small (n={r['n']} < {MIN_CELL})"
    up = r["z"] > 0
    if (spec["direction"] == "higher") != up:
        return r, False, "effect goes the other way"
    if r["p"] >= P_A:
        return r, False, f"not significant on A (p={r['p']:.3f})"
    if r["lift"] is None or abs(r["lift"] - 1) < MIN_LIFT:
        return r, False, "effect too small to matter"
    return r, True, "kept"


def occ_ids(world, spec, split="A"):
    """Occasion row ids a spec covers, so respondent- and occasion-unit specs compare on one footing."""
    if spec["unit"] == "respondent":
        return {i for p in world.resp[split] if _match(p, spec["segment"]) for i in p["_occ"]}
    return {r["_i"] for r in world.occ[split] if _match(r, spec["segment"])}


def jaccard(a, b):
    return len(a & b) / len(a | b) if a or b else 0.0


def bh(pvals, q=0.05):
    """Benjamini–Hochberg: which indices survive at FDR q."""
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    cut = -1
    for rank, i in enumerate(order, 1):
        if pvals[i] <= q * rank / m:
            cut = rank
    return {order[k] for k in range(cut)} if cut > 0 else set()


def money(world, spec, res_b):
    """G3: a € range traced to data columns plus the two stated assumptions above."""
    occ = len(occ_ids(world, spec, "B")) / len(world.occ["B"]) * OCCASIONS_PER_YEAR
    uplift = world.prem_eur - world.std_eur
    if spec["direction"] != "higher":
        return None, "a 'lower' effect has no direct money path"
    unit_eur = 1.0 if spec["outcome"] == "spend_eur" else uplift
    base = occ * max(0.0, res_b["seg"] - res_b["rest"]) * unit_eur
    how = {"premium": "segment occasions/yr × excess premium rate vs rest × (premium − standard €)",
           "skipped": "segment occasions/yr × excess skip rate vs rest × (premium − standard €)",
           "spend_eur": "segment occasions/yr × (segment − rest €/occasion)"}[spec["outcome"]]
    lo, hi = base * CAPTURE[0], base * CAPTURE[1]
    return {"low": lo, "high": hi, "occasions_per_year": occ, "uplift_eur": uplift, "how": how,
            "assumptions": [f"market = {OCCASIONS_PER_YEAR/1e6:.0f}M occasions/yr (synthetic)",
                            f"a brand closes {int(CAPTURE[0]*100)}–{int(CAPTURE[1]*100)}% of the gap"]}, None


def describe(spec, res=None):
    """Mechanical wording, used for every card in the blind deck, so prose quality can't give a source away."""
    parts = []
    for c in spec["segment"]:
        if "values" in c:
            parts.append(f"{c['col']} = {' / '.join(c['values'])}")
        else:
            parts.append(f"{c['col']} {c['op']} {c['value']}")
    unit = "Respondents" if spec["unit"] == "respondent" else "Occasions"
    s = f"{unit} where {', '.join(parts)}"
    if res and res.get("seg") is not None:
        fmt = (lambda x: f"€{x:.0f}") if spec["outcome"] == "spend_eur" else (lambda x: f"{x*100:.0f}%")
        s += f": {spec['outcome']} {fmt(res['seg'])} vs {fmt(res['rest'])} for everyone else"
    return s
