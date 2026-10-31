# Frameworks Reference — Porter Worksheet & Adaptive Lens Menu

Read this at Step 3 (Porter) and Step 4 (adaptive lens) of `SKILL.md`. This file holds the mechanical templates; the judgment calls (when to add a lens, how to weight a force) stay in the main skill body.

## Porter 5 Forces — per-force worksheet

Fill one row per force. A force with no evidence is `[VIEW] — not researched`, never a silent guess.

| Force | Guiding questions | Rating | Evidence (cited) | Goal-relevant implication |
|---|---|---|---|---|
| **Rivalry among existing competitors** | How many real competitors, how concentrated, how do they compete (price/features/digital)? Is rivalry rising (new entrants, PE consolidation) or falling (consolidation into fewer players)? | high / medium / low | | |
| **Bargaining power of suppliers** | Are inputs commoditized or specialized/scarce? Can the company switch suppliers cheaply? Is there supplier concentration? *(Most often un-researched — see Gotchas in SKILL.md.)* | high / medium / low / **not researched** | | |
| **Bargaining power of buyers/customers** | Are customers concentrated or fragmented? Are they consolidating (chains, M&A)? Can large customers insource the value the company sells (the single most common cross-case finding — see below)? | high / medium / low | | |
| **Threat of new entrants** | What's the actual barrier — capital/manufacturing, or something thinner (a software/data layer that doesn't require building the core product at all)? Where do entrants actually show up — hardware, or an adjacent digital layer? | high / medium / low | | |
| **Threat of substitutes** | Is there a different way to get the same outcome the customer wants — not a rival product, but a different method entirely (e.g. a customer's own in-house capability, a different data-capture approach, a free/subsidized public alternative)? | high / medium / low | | |

**Cross-case pattern worth actively checking for (from the Company A precedent):** buyer power and new-entrant threat are frequently underrated when the analyst looks only for competitor firms. The two sharpest findings in the reference run were (a) large customers building their own digital layer in-house while still buying the target's hardware — a buyer-power finding, not a rivalry finding — and (b) pure software/digital entrants attaching to the installed base without ever building the core hardware product — a new-entrant finding from an unexpected direction. Actively look in both places before finalizing ratings.

**BU deltas.** When a fan-out ran (Step 1), don't just average the units into one grid — name where a force is materially different for one unit than for the group as a whole, and say why. A force rated "medium" at group level that is actually "high" for one exposed unit is more useful to the goal-holder than a flattened average.

## Adaptive supplementary lens — selection rule

Porter is always the backbone (Step 3). Add **one** supplementary lens only when the stated goal specifically calls for the dimension Porter doesn't cover well. Do not add a lens by default, and do not stack more than one unless the goal genuinely has two distinct unanswered questions.

| Lens | Add it when the goal is about... | Not when... |
|---|---|---|
| **Digital-maturity matrix** (company vs. each named competitor, scored across a small set of capability axes — e.g. connectivity, data monetization, service/subscription model) | ...positioning the company's own digital roadmap or investment case against named rivals, capability by capability | Porter's rivalry/entrant rows already answer "who's ahead and where" well enough — don't re-derive the same finding in matrix form for its own sake |
| **Value chain** | ...deciding where in the company's own value chain to invest or divest (make vs. buy, which activity captures margin) | the goal is external-facing (a pitch, a hearing) rather than an internal resource-allocation decision |
| **SWOT** | ...a short internal-facing summary is explicitly requested alongside the deeper analysis (e.g. an exec wants a one-page cover in addition to the dossier) | it would just restate the Porter findings under different headers — SWOT is a bad default, only use it when literally asked for or when the audience expects that specific format |
| **Wardley mapping** | ...the goal concerns evolution/commoditization timing of a specific capability (e.g. "when does condition monitoring become table stakes vs. a differentiator") | the goal doesn't hinge on *timing* of commoditization — most goals don't need this |

## Per-unit research template (for Step 2 / fan-out TASK.md packets)

Use this as the body of each unit's `TASK.md` when Step 1 triggers a fan-out:

```
# Task — Unit <NAME>: Competitive & Digital Teardown

Context: <one paragraph — what this unit does, its market position, any candidate
competitor names to verify (mark clearly as hypotheses to check, not facts)>

## Assignment
1. Identify 2-5 named, verifiable competitors in <unit>'s core market.
2. For each: what is their digital business (platform/IoT/software/service model)? Cite source.
3. Where are they concretely ahead of <company>'s <unit> — not "more digital," the specific capability.
4. Where do they apply pressure — price/niche/digital maturity/servitization/consolidation.
5. Market frame: size/growth (flag estimates as directional), 2-3 structural forces.

## Output
Write to `children/<unit>/RESPONSE.md`:
- Competitor table: Name | Core business | Digital offering | Comparison vs <company> | Source
- Pressure points (3-5 bullets, sourced)
- Market frame (short, sourced)
- Open questions / unresolved (say plainly what you couldn't verify — don't guess)

Every claim needs a source. If you can't find a solid one, say so instead of guessing.
Target 5-8 strong sources, depth over breadth.
```
