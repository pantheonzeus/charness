# /// script
# requires-python = ">=3.10"
# dependencies = ["fastapi>=0.110", "uvicorn[standard]>=0.29"]
# ///
"""Frame-shift demo: an autonomous discovery loop on synthetic demand-space data, in the browser.

Two arms run on the same hypothesis budget. The control arm proposes hypotheses inside the
original frame. The frame-shift arm first rewrites the question (outer loop), then proposes
hypotheses inside the new frame (inner loop). Claude proposes through headless `claude -p`,
with no tools, no hooks and no repo context, on the claude.ai subscription. engine.py
compiles, tests and gates every proposal. The browser is the blind review panel (G4).

Run:  uv run demos/frameshift/server.py      → http://127.0.0.1:8770
"""
import asyncio
import json
import os
import random
import tempfile
import time
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

import engine as E

PORT = int(os.environ.get("FRAMESHIFT_PORT", "8770"))
HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
RUNS = REPO / "output" / ".frameshift"      # git-ignored
# Run the CLI outside the repo so it doesn't pick up CLAUDE.md and the harness: the proposer
# should know only what each prompt hands it.
CLI_CWD = Path(tempfile.gettempdir()) / "frameshift-cwd"
CLI_ENV = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")}
ALLOWED_HOSTS = {f"127.0.0.1:{PORT}", f"localhost:{PORT}"}
OPERATORS = ["change the unit", "invert the outcome", "import a lens", "cross distant variables", "switch school of thought"]

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.middleware("http")
async def local_only(request: Request, call_next):
    if request.headers.get("host") not in ALLOWED_HOSTS:
        return JSONResponse({"error": "local only"}, status_code=403)
    origin = request.headers.get("origin")
    if request.method == "POST" and origin and origin not in {f"http://{h}" for h in ALLOWED_HOSTS}:
        return JSONResponse({"error": "cross-site"}, status_code=403)
    return await call_next(request)


# ---------- proposer: Claude headless, or a scripted stand-in ----------
HYP_SCHEMA = {"type": "object", "required": ["hypotheses"], "properties": {"hypotheses": {"type": "array", "items": {
    "type": "object", "required": ["statement", "rationale", "direction", "segment"], "properties": {
        "statement": {"type": "string"}, "rationale": {"type": "string"},
        "direction": {"type": "string", "enum": ["higher", "lower"]},
        "segment": {"type": "array", "items": {"type": "object", "required": ["col"], "properties": {
            "col": {"type": "string"}, "values": {"type": "array", "items": {"type": "string"}},
            "op": {"type": "string", "enum": [">=", "<="]}, "value": {"type": "number"}}}}}}}}}
FRAME_SCHEMA = {"type": "object", "required": ["operator", "question", "unit", "outcome", "columns", "why"], "properties": {
    "operator": {"type": "string", "enum": OPERATORS}, "question": {"type": "string"},
    "unit": {"type": "string", "enum": ["occasion", "respondent"]},
    "outcome": {"type": "string", "enum": list(E.OUTCOMES)},
    "columns": {"type": "array", "items": {"type": "string"}}, "why": {"type": "string"}}}

HYP_SYSTEM = """You are the hypothesis proposer inside an autonomous discovery loop over consumer occasion data for a premium-spirits category.
You never see rows. Deterministic code compiles each hypothesis you write, tests it on a discovery split, and logs the result. You only ever see those logged results.
A hypothesis is a segment of 1-4 conditions on the allowed columns, plus a claim that the segment's outcome is higher or lower than everyone else's.
Rules: use only the allowed columns, with values spelled exactly as listed. Numeric columns take {"col", "op": ">=" or "<=", "value"}; categorical ones take {"col", "values": [...]}. Never repeat a segment already in the ledger. Build on what was kept and abandon what was killed. Prefer segments that would matter commercially, and make them specific enough to act on.
statement: one plain-English sentence. rationale: the human logic for why it might hold."""

FRAME_SYSTEM = """You run the outer loop of an autonomous discovery system over consumer occasion data for a premium-spirits category. Your job is to reformulate the question the data is asked, not to answer it.
Each turn, pick one reframing operator: change the unit (occasion vs respondent), invert the outcome (look at who backs out of premium, i.e. 'skipped'), import a lens (borrow a structure from another category), cross distant variables (pair context variables the original frame treats as background with the ones it treats as primary), or switch school of thought (jobs-to-be-done, behavioural economics, ritual anthropology, semiotics).
A frame declares a unit, an outcome, and the columns hypotheses may use. The columns must be legal for the unit. A good frame asks a question the original frame cannot express. Explore before you exploit: each new frame must differ from every earlier one in operator, unit or outcome, and an occasion-unit frame must include at least two columns the original frame doesn't have. Use the ledger: an operator that produced survivors deserves a variation, and one that produced none deserves a different direction. Never just zoom into the original frame's known hotspots."""


async def claude_json(system, prompt, schema, model, log):
    CLI_CWD.mkdir(exist_ok=True)
    cmd = ["claude", "-p", prompt, "--tools", "", "--setting-sources", "", "--no-session-persistence",
           "--system-prompt", system, "--output-format", "json", "--model", model, "--json-schema", json.dumps(schema)]
    t = time.time()
    proc = await asyncio.create_subprocess_exec(*cmd, cwd=CLI_CWD, env=CLI_ENV, stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.PIPE)
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=180)
    except asyncio.TimeoutError:
        proc.kill()
        raise RuntimeError("claude -p timed out after 180s")
    if proc.returncode != 0:
        raise RuntimeError(f"claude -p exited {proc.returncode}: {err.decode()[-400:]}")
    d = json.loads(out)
    if d.get("is_error") or d.get("structured_output") is None:
        raise RuntimeError(f"claude -p returned no structured output: {str(d.get('result'))[:300]}")
    log({"type": "llm_call", "secs": round(time.time() - t, 1), "cost_usd": d.get("total_cost_usd"),
         "in": d.get("usage", {}).get("input_tokens"), "out": d.get("usage", {}).get("output_tokens")})
    return d["structured_output"]


class Scripted:
    """Stand-in proposer for testing the pipeline without model calls. It is random, not clever."""

    def __init__(self, seed):
        self.rng = random.Random(seed)

    def frame(self, k):
        op = OPERATORS[k % len(OPERATORS)]
        unit = "respondent" if op == "change the unit" else "occasion"
        outcome = "skipped" if op == "invert the outcome" else self.rng.choice(["premium", "premium", "spend_eur"])
        cols = self.rng.sample(E.legal_columns(unit), min(5, len(E.legal_columns(unit))))
        return {"operator": op, "question": f"Scripted frame {k + 1}: {op}", "unit": unit, "outcome": outcome,
                "columns": cols, "why": "scripted"}

    def hyps(self, frame, n):
        out = []
        for _ in range(n):
            seg = []
            for c in self.rng.sample(frame["columns"], self.rng.randint(1, min(3, len(frame["columns"])))):
                if c in E.NUMERIC:
                    seg.append({"col": c, "op": ">=", "value": self.rng.choice([2, 3, 4, 6])})
                else:
                    seg.append({"col": c, "values": [self.rng.choice(E.CATS[c])]})
            out.append({"statement": "scripted", "rationale": "random draw", "segment": seg,
                        "direction": self.rng.choice(["higher", "higher", "lower"])})
        return out


def ledger_lines(tested, limit=30):
    lines = []
    for h in tested[-limit:]:
        r = h["resA"]
        stat = f"n={r['n']}" + (f", lift={r['lift']:.2f}, p={r['p']:.1e}" if r.get("lift") else "")
        lines.append(f"- [{h['verdict']}] {h['frame_id']} {h['spec_text'] if h['spec'] else h['statement']} ({stat}; {h['reason']})")
    return "\n".join(lines) or "(empty: nothing tested yet)"


# ---------- one run ----------
class Run:
    def __init__(self, cfg):
        self.id = time.strftime("%Y%m%d-%H%M%S")
        self.cfg = cfg
        self.events, self.changed, self.done = [], asyncio.Event(), False
        self.dir = RUNS / self.id
        self.dir.mkdir(parents=True, exist_ok=True)
        self.world = E.World(seed=cfg["seed"])
        self.tested = {"control": [], "shift": []}
        self.frames = {"control": [dict(E.ORIGINAL_FRAME)], "shift": []}
        self.deck, self.labels, self.cands = [], {}, []
        self.scripted = Scripted(cfg["seed"]) if cfg["mock"] else None
        self.cost = 0.0

    def emit(self, ev):
        ev["t"] = round(time.time(), 2)
        self.events.append(ev)
        with (self.dir / "ledger.jsonl").open("a") as f:
            f.write(json.dumps(ev, default=str) + "\n")
        if ev["type"] == "llm_call" and ev.get("cost_usd"):
            self.cost += ev["cost_usd"]
        self.changed.set()
        self.changed = asyncio.Event()

    async def propose_hyps(self, arm, frame):
        n = self.cfg["per_round"]
        if self.scripted:
            await asyncio.sleep(0.3)
            return self.scripted.hyps(frame, n)
        prompt = (f"FRAME {frame['id']}: {frame['question']}\nUnit: {frame['unit']}. Outcome: {frame['outcome']} "
                  f"({E.OUTCOMES[frame['outcome']]}" + (", averaged per respondent" if frame["unit"] == "respondent" else "") + ").\n"
                  f"ALLOWED COLUMNS:\n{json.dumps(E.dictionary(frame['columns'], frame['unit']), indent=1)}\n\n"
                  f"LEDGER (this arm, most recent last):\n{ledger_lines(self.tested[arm])}\n\n"
                  + (f"RULE: the original frame (unit occasion, outcome premium, columns {E.ORIGINAL_FRAME['columns']}) must not be able "
                     "to ask any of your hypotheses. Code rejects any it could ask.\n\n" if arm == "shift" else "")
                  + f"Write exactly {n} new hypotheses inside this frame.")
        self.emit({"type": "thinking", "arm": arm, "role": "hypotheses", "frame_id": frame["id"]})
        d = await claude_json(HYP_SYSTEM, prompt, HYP_SCHEMA, self.cfg["model"], lambda e: self.emit({**e, "arm": arm}))
        return d["hypotheses"][:n]

    async def propose_frame(self, k):
        if self.scripted:
            await asyncio.sleep(0.3)
            return self.scripted.frame(k)
        tried = []
        for f in self.frames["shift"]:
            hs = [h for h in self.tested["shift"] if h["frame_id"] == f["id"]]
            kept = [h for h in hs if h["verdict"] == "kept"]
            best = max(kept, key=lambda h: abs((h["resA"]["lift"] or 1) - 1), default=None)
            tried.append(f"- {f['id']} [{f['operator']}] {f['question']} (unit={f['unit']}, outcome={f['outcome']}, "
                         f"columns={f['columns']}): {len(kept)}/{len(hs)} kept"
                         + (f"; strongest: {best['spec_text']} lift {best['resA']['lift']:.2f}" if best else ""))
        cols = {u: E.dictionary(E.legal_columns(u), u) for u in ("occasion", "respondent")}
        prompt = (f"ORIGINAL FRAME (what the existing method asks): {E.ORIGINAL_FRAME['question']} "
                  f"Unit occasion, outcome premium, columns {E.ORIGINAL_FRAME['columns']}.\n\n"
                  f"OUTCOMES: {json.dumps(E.OUTCOMES)}\n\nCOLUMNS BY UNIT:\n{json.dumps(cols, indent=1)}\n\n"
                  f"FRAMES TRIED SO FAR:\n" + ("\n".join(tried) or "(none yet)") + "\n\nPropose the next frame.")
        self.emit({"type": "thinking", "arm": "shift", "role": "frame"})
        return await claude_json(FRAME_SYSTEM, prompt, FRAME_SCHEMA, self.cfg["model"], lambda e: self.emit({**e, "arm": "shift"}))

    def test(self, arm, frame, raw):
        hid = f"{'C' if arm == 'control' else 'S'}{len(self.tested[arm]) + 1:02d}"
        spec, why = E.compile_spec(raw, frame)
        if spec and arm == "shift" and E.expressible_in_original(spec):
            spec, why = None, "expressible in the original frame (that's the control arm's job)"
        h = {"id": hid, "arm": arm, "frame_id": frame["id"], "statement": raw.get("statement", ""),
             "rationale": raw.get("rationale", ""), "spec": spec, "spec_text": E.describe(spec) if spec else None}
        if spec is None:
            h.update(verdict="invalid", reason=why, resA={"n": 0})
        elif any(t["spec"] and t["spec"]["segment"] == spec["segment"] and t["spec"]["outcome"] == spec["outcome"]
                 and t["spec"]["unit"] == spec["unit"] for t in self.tested[arm]):
            h.update(verdict="invalid", reason="duplicate of an earlier hypothesis", resA={"n": 0})
        else:
            res, kept, why = E.inner_test(self.world, spec)
            res = {k: v for k, v in res.items() if k != "rows"}
            h.update(verdict="kept" if kept else "killed", reason=why, resA=res, text=E.describe(spec, res))
        self.tested[arm].append(h)
        self.emit({"type": "hypothesis", **h})

    async def arm_control(self):
        frame = self.frames["control"][0]
        self.emit({"type": "frame", "arm": "control", "frame": frame})
        for r in range(self.cfg["rounds"]):
            for raw in await self.propose_hyps("control", frame):
                self.test("control", frame, raw)
            self.emit({"type": "round_done", "arm": "control", "round": r + 1})

    async def arm_shift(self):
        # Same hypothesis budget as the control arm: its rounds are shared out across the frames,
        # so every frame gets its own inner loop that learns between rounds.
        frames, rounds = self.cfg["frames"], self.cfg["rounds"]
        inner = [rounds // frames + (1 if k < rounds % frames else 0) for k in range(frames)]
        for k in range(frames):
            f = await self.propose_frame(k)
            legal = E.legal_columns(f["unit"])
            f["columns"] = [c for c in dict.fromkeys(f.get("columns", [])) if c in legal] or legal[:4]
            f["id"] = f"F{k + 1}"
            self.frames["shift"].append(f)
            self.emit({"type": "frame", "arm": "shift", "frame": f})
            for _ in range(inner[k]):
                for raw in await self.propose_hyps("shift", f):
                    self.test("shift", f, raw)
            hs = [h for h in self.tested["shift"] if h["frame_id"] == f["id"]]
            self.emit({"type": "frame_yield", "arm": "shift", "frame_id": f["id"],
                       "kept": sum(h["verdict"] == "kept" for h in hs), "tested": len(hs)})

    def gates(self):
        w = self.world
        cands = [h for arm in self.tested.values() for h in arm if h["verdict"] == "kept"]
        resB = [E.evaluate(w, h["spec"], "B") for h in cands]
        survive = E.bh([r["p"] for r in resB])
        known_ids = [(k["name"], E.occ_ids(w, k)) for k in E.KNOWN_MAP]
        for i, (h, rb) in enumerate(zip(cands, resB)):
            same_dir = rb["seg"] is not None and ((rb["z"] > 0) == (h["spec"]["direction"] == "higher"))
            h["resB"] = {k: v for k, v in rb.items() if k != "rows"}
            h["g1"] = i in survive and same_dir
            ids = E.occ_ids(w, h["spec"])
            j = max(((n, E.jaccard(ids, kid)) for n, kid in known_ids), key=lambda x: x[1])
            h["nearest_known"], h["overlap"] = j[0], round(j[1], 2)
            h["g2"] = h["g1"] and j[1] < 0.3
            m, why = E.money(w, h["spec"], rb) if h["g1"] else (None, "failed G1")
            h["money"], h["money_note"] = m, why
            h["g3"] = h["g2"] and m is not None and m["low"] >= E.G3_MIN_EUR
        self.cands = cands
        arms = {}
        for arm in ("control", "shift"):
            t = self.tested[arm]
            c = [h for h in cands if h["arm"] == arm]
            arms[arm] = {"tested": sum(h["verdict"] != "invalid" for h in t), "invalid": sum(h["verdict"] == "invalid" for h in t),
                         "kept": len(c), "g1": sum(h["g1"] for h in c), "g2": sum(h["g2"] for h in c), "g3": sum(h["g3"] for h in c)}
        self.emit({"type": "gates", "arms": arms, "candidates": [
            {k: h[k] for k in ("id", "arm", "frame_id", "spec_text", "g1", "g2", "g3", "overlap", "nearest_known", "money_note")}
            | {"pB": h["resB"]["p"], "money": h["money"] and {"low": h["money"]["low"], "high": h["money"]["high"]}}
            for h in cands]})

        # Blind deck: G3 survivors, the sealed map's "higher" spaces, and decoys (looked great on A, failed on B).
        # Every card is worded mechanically from its spec, so the model's prose can't give the source away.
        # Overlapping survivors are one finding: keep the strongest on B, drop the variants.
        picked = []
        for h in sorted((h for h in cands if h["g3"]), key=lambda h: h["resB"]["p"]):
            ids = E.occ_ids(w, h["spec"])
            if all(E.jaccard(ids, E.occ_ids(w, o["spec"])) < 0.4 for o in picked):
                picked.append(h)
        cards = [("loop", h["spec"], h) for h in picked]
        for k in E.KNOWN_MAP:
            spec = {**k, "outcome": "premium", "direction": "higher"}
            r = E.evaluate(w, spec, "A")
            if r["seg"] is not None and r["seg"] > r["rest"]:
                cards.append(("known", spec, {"name": k["name"]}))
        decoys = sorted([h for h in cands if not h["g1"]], key=lambda h: -abs((h["resA"]["lift"] or 1) - 1))[:2]
        cards += [("decoy", h["spec"], h) for h in decoys]
        random.Random(self.cfg["seed"]).shuffle(cards)
        for i, (kind, spec, src) in enumerate(cards):
            cid = f"card{i + 1}"
            r = E.evaluate(w, spec, "A")
            self.deck.append({"id": cid, "text": E.describe(spec, r)})
            self.labels[cid] = {"kind": kind, "src": src.get("id") or src.get("name")}
        self.emit({"type": "deck", "cards": self.deck})

    async def go(self):
        self.emit({"type": "start", "run_id": self.id, "cfg": self.cfg, "data": self.world.summary(),
                   "original_frame": E.ORIGINAL_FRAME})
        try:
            await asyncio.gather(self.arm_control(), self.arm_shift())
            self.gates()
            self.emit({"type": "done", "cost_usd": round(self.cost, 4)})
        except Exception as e:  # report, never hide
            self.emit({"type": "error", "message": str(e)})
        self.done = True
        self.changed.set()

    def reveal(self, ratings):
        (self.dir / "ratings.json").write_text(json.dumps(ratings, indent=1))
        w = self.world
        by_id = {h["id"]: h for h in self.cands}
        cards = []
        for c in self.deck:
            lab = self.labels[c["id"]]
            h = by_id.get(lab["src"]) if lab["kind"] != "known" else None
            frame = next((f for arm in self.frames.values() for f in arm if h and f["id"] == h["frame_id"]), None)
            cards.append({**c, **lab, "rating": ratings.get(c["id"]),
                          "arm": h and h["arm"], "statement": h and h["statement"], "rationale": h and h["rationale"],
                          "frame": frame and {k: frame[k] for k in ("id", "operator", "question")},
                          "resA": h and h["resA"], "resB": h and h["resB"], "money": h and h["money"],
                          "overlap": h and h["overlap"], "nearest_known": h and h["nearest_known"]})
        g1 = [h for h in self.cands if h["g1"]]
        recall = {}
        for arm in ("control", "shift"):
            recall[arm] = [k["name"] for k in E.KNOWN_MAP
                           if any(h["arm"] == arm and E.jaccard(E.occ_ids(w, h["spec"]), E.occ_ids(w, k)) >= 0.5 for h in g1)]
        found = []
        for p in E.PLANTED:
            pid = E.occ_ids(w, p)
            hits = [(h["id"], h["arm"], round(E.jaccard(E.occ_ids(w, h["spec"]), pid), 2)) for h in g1
                    if (h["spec"]["outcome"] == p["outcome"] or {h["spec"]["outcome"], p["outcome"]} == {"premium", "spend_eur"})
                    and E.jaccard(E.occ_ids(w, h["spec"]), pid) >= 0.4]
            found.append({"name": p["name"], "operator": p["operator"], "text": E.describe({**p, "direction": "higher"}),
                          "hits": hits})
        both = sorted(set(recall["control"]) | set(recall["shift"]))
        g3 = [h for h in self.cands if h["g3"]]
        shift_new = [c for c in cards if c["kind"] == "loop" and c["arm"] == "shift" and c["rating"] == "new"]
        if len(both) < 2:
            verdict, why = "VOID", f"The recall guard failed: only {len(both)} of {len(E.KNOWN_MAP)} known spaces were rediscovered, so 'new' can't be trusted."
        elif not g1:
            verdict, why = "KILL: no signal", "Nothing replicated on the sealed split."
        elif g3 and all(h["arm"] == "control" for h in g3):
            verdict, why = "KILL: thesis", "Every candidate that cleared G1–G3 came from the control arm. The loop finds patterns but doesn't reframe."
        elif shift_new:
            verdict, why = "PASS", f"{len(shift_new)} frame-shift card(s) cleared G1–G3 and you rated them new and plausible without knowing their source."
        elif not g3:
            verdict, why = "INCONCLUSIVE", "Candidates replicated, but none cleared both novelty and the money trace."
        else:
            verdict, why = "INCONCLUSIVE", "Frame-shift candidates cleared G1–G3, but you didn't rate any of them as new."
        out = {"cards": cards, "recall": recall, "recall_union": both, "planted": found, "verdict": verdict, "why": why,
               "cost_usd": round(self.cost, 4), "ledger": str(self.dir.relative_to(REPO) / "ledger.jsonl")}
        (self.dir / "reveal.json").write_text(json.dumps(out, indent=1, default=str))
        return out


RUN: dict = {"current": None}


@app.get("/")
async def index():
    return FileResponse(HERE / "static" / "index.html")


@app.post("/api/run")
async def start(req: Request):
    cur = RUN["current"]
    if cur and not cur.done:
        raise HTTPException(409, "a run is already going")
    b = await req.json()
    cfg = {"model": b.get("model") if b.get("model") in ("haiku", "sonnet", "opus") else "sonnet",
           "rounds": max(1, min(8, int(b.get("rounds", 6)))), "per_round": max(2, min(10, int(b.get("per_round", 6)))),
           "seed": int(b.get("seed", 7)), "mock": bool(b.get("mock"))}
    cfg["frames"] = max(1, min(cfg["rounds"], int(b.get("frames", 3))))
    run = Run(cfg)
    RUN["current"] = run
    asyncio.create_task(run.go())
    return {"run_id": run.id}


@app.get("/api/current")
async def current():
    cur = RUN["current"]
    return {"run_id": cur and cur.id, "done": cur and cur.done}


@app.get("/api/events/{run_id}")
async def events(run_id: str):
    run = RUN["current"]
    if not run or run.id != run_id:
        raise HTTPException(404, "unknown run")

    async def stream():
        i = 0
        while True:
            while i < len(run.events):
                yield f"data: {json.dumps(run.events[i], default=str)}\n\n"
                i += 1
            if run.done:
                yield "event: end\ndata: {}\n\n"
                return
            try:
                await asyncio.wait_for(run.changed.wait(), timeout=15)
            except asyncio.TimeoutError:
                yield ": keepalive\n\n"
    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})


@app.post("/api/reveal/{run_id}")
async def reveal(run_id: str, req: Request):
    run = RUN["current"]
    if not run or run.id != run_id or not run.deck:
        raise HTTPException(404, "no finished run with a deck")
    b = await req.json()
    return run.reveal({k: v for k, v in (b.get("ratings") or {}).items() if v in ("new", "known", "implausible")})


if __name__ == "__main__":
    print(f"frame-shift demo → http://127.0.0.1:{PORT}")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
