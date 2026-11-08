# LSC Conventions — shared by every `lsc-*` skill

Every canvas skill points here instead of repeating these rules. Read once per run.

## 1. Provenance and license
- Source: **Lean Service Creation Toolbox, v3.0.5, by Futurice Ltd**, licensed CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). Canvas titles, field questions and the callouts ("ASK WHY", "LOVE THE PROBLEM, NOT THE SOLUTION") are quoted from that PDF.
- ShareAlike: the `lsc-*` skills and `lean-service-creation` reproduce and adapt canvas content (the book paraphrase follows the same rule as a precaution). Any copy or fork of them carries the same CC BY-SA 4.0 license and this attribution line.
- Second source: *Lean Service Creation* (Handbook 2.0), Futurice Oy, 2018, supplied by the principal. Its guidance is paraphrased in a "Handbook 2.0 guidance" section per skill and in [handbook-2.md](handbook-2.md). The book states no separate license, so it is paraphrased, not copied. Canvases 24-29 come only from the book.
- Method guidance in neither source is marked **[house]** and is this workspace's addition, not Futurice's. Where the two sources differ in stage names or fields (for example the Customer Engagement stages), each skill says so.

## 2. The run's file-backed state
One run = one STATE_ROOT: `output/.runs/<YYYYMMDD>-<slug>-lsc/`.
```
RESPONSE.md           control spine: one [ ]/[x] line per canvas + one Gate line per gate
EVIDENCE.md           claim register: id · claim · tag · source · date
canvases/NN-<slug>.md one file per canvas (NN = canvas number from the router table)
```
A canvas skill reads its upstream canvases **by path**, never from conversation memory. Standalone use (no STATE_ROOT): write to `output/<YYYYMMDD>-<slug>-lsc-<canvas>.md`.

## 3. Canvas file format
```markdown
---
canvas: 05-insight
phase: users-needs
status: draft | reviewed | signed-off
upstream: [canvases/01-business-objective-context.md, canvases/04-script-creator.md]
evidence-mix: {observed: 14, synthetic: 0, inferred: 3}
updated: YYYY-MM-DD
---
### <field title, verbatim from the canvas>
- <entry> `[O|S|I]` `E-12`
```
- One `###` heading per canvas field, wording unchanged, so a filled file maps 1:1 to the paper canvas.
- Every entry carries a tag and an EVIDENCE.md id, except fields that are pure decisions (checkboxes, verdicts).

## 4. Evidence tags (same vocabulary as `business-design-engagement`)
| Tag | Means | Examples |
|---|---|---|
| `[O]` observed | seen or heard from a real person or system, with source and date | interview quote, analytics export, signed LOI, pilot result |
| `[S]` synthetic | produced by an AI agent or simulation | synthetic persona answer, LLM desk summary, agent-generated idea |
| `[I]` inferred | our own reasoning from other entries | "so they probably also…" |

Rules:
1. `[S]` and `[I]` shape hypotheses. They never count as validation. A gate that moves toward build or launch needs `[O]` evidence.
2. The canvases ask for "best guesses" in early phases (Immersion, Customer Groups). Guesses are written as `[I]` hypotheses and are expected, not hidden.
3. A numeric claim carries its unit, date and source. No number without an id.

## 3b. Gate lines (in RESPONSE.md)
`Gate <canvas>: YES|ITERATE|NO — <one-line reason> — evidence: E-ids — next: <canvas or action>`
Mapping from the paper sliders: YES → continue. "WE HAVE TO ITERATE" → re-run the named canvases (cap: 3 loops per gate, then decide YES or NO and record why). NO → kill or park, with the money and time saved.

## 5. Principles quoted from the canvases (apply everywhere)
- **Ask why.** Every objective, need and requirement gets a "why" until the answer is a business or human consequence.
- **Love the problem, not the solution.** Needs are written solution-free ("a way to…").
- **Deeper level.** "Don't ask what the user wants, try to find out what she needs on the deeper level."
- **Don't assume, validate.** "Do whatever it takes to question your concept."
- **Do you think? Do you know? Did you check?** Label each assumption honestly with one of the three.
- **Make work visible.** Stakeholders see progress weekly, not at the end.
- **The team is all you've got.** Capacity and morale are inputs, not afterthoughts.

## 6. Agent-augmented practice (house rule)
Agents may: scan desks, code transcripts, generate divergent ideas, draft canvas strawmen, red-team a choice, summarize a retro. Agents may not: interview-substitute, provide evidence for a gate, sign a canvas, or pick the winner. Every agent output is tagged `[S]`. Humans diverge first, agents add second, to avoid anchoring. Quote-backed claims are verified against the source transcript before they become `[O]` (see `_shared/verifier-separation.md`).

## 7. Vault wiring (Charter §6)
People, companies and sources surfaced in any canvas get a vault note or a link to an existing one, with a one-line reason, in both directions. Interview participants are personal data: keep them in the vault only with a lawful basis, never in a public repo or a shared deliverable by name.

## 8. Evidence gate before release (Charter §4)
Before a canvas set or pitch leaves the building, run `_shared/evidence-gate.md`: every numeric or factual claim is tagged and sourced, and nothing uncited ships.
