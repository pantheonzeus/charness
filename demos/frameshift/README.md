# Frame-Shift Lab

A browser demo of the frame-shift experiment architecture. An autonomous discovery loop runs on synthetic demand-space data. It tests whether *rewriting the question* finds connections that pattern-finding inside the original frame can't.

```bash
uv run demos/frameshift/server.py     # → http://127.0.0.1:8770   (FRAMESHIFT_PORT to change)
```

It is separate from the cbrain console (`webapp/`). It shares nothing with it except the pattern of calling the Claude Code CLI headless. It runs on your claude.ai subscription, because the server strips `ANTHROPIC_API_KEY` from the child environment.

## What happens in a run
1. **Data.** About 21k synthetic occasions from 4,000 respondents, split once by respondent into A (60%, which the loop tests on) and B (40%, sealed). The data has two kinds of planted pattern:
   - five demand spaces on the original-frame columns, sealed as "your map"
   - four connections on columns the original frame ignores
2. **Two arms, same hypothesis budget, in parallel.**
   - *Control:* Claude proposes hypotheses inside the original frame (need × setting × company → premium) and learns from its own ledger between rounds.
   - *Frame-shift:* an outer loop has Claude rewrite the question using one of five operators: change the unit, invert the outcome, import a lens, cross distant variables, switch school of thought. An inner loop then proposes and tests hypotheses inside each new frame. Code rejects any frame-shift hypothesis that the original frame could already ask.
3. **Code decides.** Each hypothesis is a JSON segment spec (never SQL, never rows). `engine.py` compiles it against the frame, then tests it on A with a Welch z-test, a minimum cell size of 30, p < 0.01 and a lift of at least ±15%. It then runs four gates:
   - **G1:** replicates on sealed B, with Benjamini–Hochberg FDR at q = 0.05.
   - **G2:** less than 30% occasion overlap with the sealed map.
   - **G3:** the low end of the € range is at least €150k/yr.
   - **G4 (you):** a blind deck in the browser. It mixes G1–G3 survivors with known-map spaces and decoys (strong on A, failed on B), and every card is worded by code.
4. **Reveal.** You see the source of every card, a verdict (PASS / KILL: thesis / KILL: no signal / VOID / INCONCLUSIVE), the recall guard, and the planted ground truth.

The model sees only the column dictionary, the frame and its own logged results. The sealed map, split B and the planted truth never reach a prompt.

## Files
- `engine.py`: synthetic world, compiler, test, gates and € trace (deterministic, stdlib only)
- `server.py`: orchestration, the `claude -p` proposer, SSE event stream and reveal
- `static/index.html`: the page
- Run state goes to `output/.frameshift/<run-id>/`: `ledger.jsonl` (every event), `ratings.json` and `reveal.json`. It is git-ignored.

## How Claude is called
`claude -p <prompt> --tools "" --setting-sources "" --no-session-persistence --system-prompt … --output-format json --json-schema …`, run from a temp dir outside the repo. That means no tools, no hooks, no CLAUDE.md and no memory: about 600 input tokens of overhead per call. The proposer knows only what each prompt hands it. Expect roughly 15 calls and 4–5 minutes per default run (6 rounds × 6 hypotheses per arm, 3 frames), at about $0.6 API-equivalent. The cost is shown, not charged, because the calls go through your subscription.

**Scripted (no Claude)** swaps in a random proposer, for testing the pipeline offline. Expect VOID, because random proposals don't pass the recall guard.

## Limits (what this demo does not prove)
- The data is synthetic, and its planted effects are clean by construction. Real demand-space data is noisier and has messier columns.
- Novelty (G2) is mechanical. A sub-segment of a known space with less than 30% overlap counts as "new", so control-arm refinements can pass it. G4 exists for exactly that.
- With n = 1 run per seed, any single verdict is an anecdote. Run several seeds before reading anything into control versus frame-shift.
- Spend counts as evidence for a premium-planted pattern, because in this world spend is driven mechanically by the premium choice.
