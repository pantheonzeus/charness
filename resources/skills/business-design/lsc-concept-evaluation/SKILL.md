---
id: lsc-concept-evaluation
aliases: [lsc-concept-evaluation]
name: "LSC 14 — Evaluating the Concept (The Acid Test)"
category: business-design
description: Run the Lean Service Creation "Evaluating the Concept" radar — score twelve criteria from societal impact to financing with evidence tags, compare concepts, and give a gate verdict of NO, WE HAVE TO ITERATE or YES with the canvases to revisit.
triggers: [evaluating the concept, LSC concept evaluation, acid test, should we proceed, concept radar, score the concept, go no go concept, compare concepts, fits our strategy vision brand promise, worth solving, concept gate]
tags: [lean-service-creation, lsc, canvas, evaluation, gate, decision]
related: ["[[lean-service-creation]]", "[[lsc-business-model-market-size]]", "[[lsc-feasibility-study]]", "[[lsc-impact-optimizer]]", "[[lsc-validation]]", "[[assumption-audit]]"]
modules: [file-backed-state, evidence-backed-answering, verifier-separation]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 14 — Evaluating the Concept

## Contract
- **Input:** canvases 01, 02, 05, 08–13 for each concept in the comparison.
- **Output:** `canvases/14-concept-evaluation.md`: a 12-row scorecard (score 1–5, evidence tag, source ids, one-line reason), a radar description, the gate verdict and the canvases to revisit.
- **Allowed tools/artifacts:** upstream canvases; a reviewer who did not fill the canvases (verifier separation).
- **Done when:** all 12 criteria are scored with evidence tags, a second reader has challenged any score above 3 resting only on `[I]`, and the gate line is written in `RESPONSE.md`.

## Canvas (v3.0.5) — "Time for the acid test."
Concept name at the centre. Twelve spokes, each with two poles:
| Criterion | Best pole | Worst pole |
|---|---|---|
| Positive impact to the society? | Best ever! | Sorry to say, but nope! |
| How new an idea? | Fresh and unique | Conservative |
| Easy to copy? | Very hard | Easy |
| Competition | None | Hard |
| Return on investment | High | Low |
| Financing | No problem | Too big/risky |
| Implementation | Straight forward | Complex |
| Fits our vision | Perfect fit | Doesn't fit |
| Fits our brand promise | Perfect fit | Doesn't fit |
| Fits our strategy? | Perfect fit | Doesn't fit |
| Right segment? | Perfect fit | Doesn't fit |
| Problem worth solving? | Insight driven | Process driven |
**Should we proceed?** NO! — WE HAVE TO ITERATE — YES!

## Core Blueprint
1. **Score from files.** For each criterion open the source canvas: society ← 10; novelty ← 02 analogues and start-ups; copy-ability and competition ← 02 and 08 differentiation; ROI and financing ← 12; implementation ← 13; vision, brand, strategy ← 01; segment ← 03 and 05; problem worth solving ← 05 (insight-driven = backed by interviews, process-driven = we assumed it). Score 1 (worst pole) to 5 (best pole).
2. **Tag every score** `[O]`, `[S]` or `[I]` and cite E-ids. A score with no cited canvas entry is invalid.
3. **Second reader.** A person or a fresh agent who did not write the canvases challenges every 4–5 and every score based on `[I]` only. Record changes.
4. **Compare concepts** side by side if more than one (including variants from 07 loops). Do not average spokes; look at the weakest.
5. **Verdict rule [house].**
   - **NO** if "Problem worth solving" ≤ 2, or "Positive impact" ≤ 1 with no mitigation, or "Fits our strategy" ≤ 1.
   - **YES** only if: no spoke ≤ 2 without a written mitigation; "Problem worth solving" ≥ 4 with `[O]` evidence; ROI and Implementation ≥ 3 with sources; and no gate-critical spoke supported by `[S]`/`[I]` alone.
   - Otherwise **WE HAVE TO ITERATE**: name the lowest spokes and the canvases to re-run (e.g. ROI → 12, Implementation → 13, Right segment → 03, Problem → 05/04).
   A different rule may be agreed with the sponsor in 01; record it there.
6. **Write the gate line** and the iteration list. Cap three iterations, then YES or NO with the reason.

## Quality tests
- All 12 scored, none left blank or "n/a" without a reason.
- Every score cites canvas entries and a tag.
- Evidence mix reported at the top (count of `[O]`/`[S]`/`[I]`).
- Verdict follows the stated rule; any override is written with its reason.
- Iteration list names canvases, not feelings.

## Agent-augmented variant
An agent may pre-fill scores and reasons as a strawman (`[S]`). Scores enter the file only after a human or independent verifier confirms each against the cited canvas. The agent does not set the verdict.

## Handbook 2.0 guidance (book, Futurice 2018, paraphrased)
Handbook version, "Profiling the Concept" (the Death Star): restate the value proposition (A) and how it works (B), then profile the concept (C), then vote (D).
- Start with silent individual estimates on the scale, forget rank and status, then discuss and justify each opinion.
- Outer ring is generally positive and the centre negative, but the team sets the convention. Thresholds can be agreed in advance when goals are set.
- Vote, or let the leader or product owner decide after discussion. Iterating is a sign of courage: admit you are smarter than before.

## Gotchas
- **Radar as decoration.** The value is in the reason line per spoke and in the weakest spoke.
- **Averaging.** One failed spoke (no willingness to pay, impossible build) sinks the concept regardless of the others.
- **Same author scores their own concept.** Always separate the reader.
- **Scoring novelty high because we have not searched.** Cite the search that supports "fresh and unique".

## Hand-offs
YES → `lsc-validation` (15) and `lsc-experimenting` (21) for the evidence still missing. ITERATE → named canvases. NO → write the kill note: what we learned, money and time saved, what would change the verdict.
