---
id: lsc-insight
aliases: [lsc-insight]
name: "LSC 05 — Insight Canvas"
category: business-design
description: Run the Lean Service Creation "Insight" canvas — per interviewee needs and key findings, what they think and feel, what surprised us — then select the needs worth meeting for the business objective as "the user needs a way to / it's important because / related emotions and values".
triggers: [insight canvas, LSC insight, interview synthesis, customer insight, synthesize interviews, user needs selection, needs and findings, thinks and feels, surprised us, the user needs a way to, affinity from interviews]
tags: [lean-service-creation, lsc, canvas, insight, synthesis, needs]
related: ["[[lean-service-creation]]", "[[lsc-script-creator]]", "[[lsc-business-objective-context]]", "[[lsc-ideation-sandbox]]", "[[service-discovery-research]]", "[[value-proposition-design]]"]
modules: [file-backed-state, evidence-backed-answering, verifier-separation]
status: active
version: 2
created: 2026-10-22
updated: 2026-10-23
---

# LSC 05 — Insight

## Contract
- **Input:** interview notes or transcripts (consented), `canvases/04-…`, `canvases/01-…`.
- **Output:** `canvases/05-insight.md`: one row per interviewee and the selected-needs table. Every row cites a source file and quote id.
- **Allowed tools/artifacts:** transcripts, notes, vault person notes, an agent for coding with the verifier step below.
- **Done when:** each interviewee has a filled row, every selected need is backed by quotes from at least two interviewees, and each selected need links to the 01 objective in one sentence.

## Canvas (v3.0.5) — "Our understanding of customer motivations that will unlock a business opportunity."
Five rows, each with a **NAME**, three columns: **Needs + other key findings** · **Thinks and feels** · **Surprised us**.
Below: **Select the needs we want to meet to fulfil the business objective:** three columns: **The user needs a way to:** · **It's important because:** · **Related emotions and values:**

## Core Blueprint
1. **Fill a row within 24 hours** of each interview, while memory is fresh. Use a pseudonym in the file; keep the key outside the repo and the vault (as in service-discovery-research). Verbatim quotes get ids (`Q-07-03` = interview 07, quote 3).
2. **Needs + key findings:** what the person did, tried, paid for, avoided, plus the underlying need in solution-free words. Separate observation from interpretation, tag `[O]` and `[I]`.
3. **Thinks and feels:** emotions and beliefs the person expressed, with the quote that shows it.
4. **Surprised us:** copy from the interview's Surprise log. A row with an empty cell here is a flag, not a pass.
5. **Cluster across rows.** Group similar needs; count how many interviewees support each. Keep minority needs visible with their count.
6. **Select needs for the objective.** For each candidate need ask: does meeting it move a 01 success goal? Write the link. Reject needs that are real but off-objective and park them in a "later" list.
7. **Write the selected table.** *The user needs a way to* (verb phrase, no solution) · *It's important because* (the consequence for the person) · *Related emotions and values* (named, with quotes).
8. **Verify (separate step).** A second pass, human or a fresh agent that has not seen the synthesis, checks every quote id against the transcript: does it exist, does it support the claim? Unsupported claims drop to `[I]` or are removed.
9. **Check against 03.** If the strongest needs sit in a different group, update 03 and note the pivot in `RESPONSE.md`.

## Quality tests
- All rows are real interviewees. No synthetic-persona rows.
- Each selected need has ≥ 2 interviewees and ≥ 2 quote ids; singletons are labelled "single signal".
- "A way to…" statements contain no solution, product or technology.
- Each selected need has an objective link sentence.
- Emotions and values are specific words ("fear of blame when a machine stops"), not "frustrated".
- Verification pass recorded with date and result.

## Agent-augmented variant
An agent may code transcripts into candidate needs and draft clusters (`[S]`), always with quote ids. It may not count support for a need without citing the quotes. Counts are computed from ids, not asserted. The synthesis decision stays human.

## Handbook 2.0 guidance (book, Futurice 2018, paraphrased)
- Write the three most important findings right after each interview.
- Take a photo of the interviewee with permission, so the team and sponsor see the insights come from real people. In this workspace keep photos and names outside the repo and the vault, like the pseudonym key.
- If you forgot to ask how they felt, call them back and ask in the next interview.
- Needs example from the handbook: they say coffee, you conclude they need something to wake them up. Write the real quote next to the conclusion.
- "It's important because" should check whether the problem is real and whether your company has a unique advantage in it.

## Gotchas
- **Averaging away the surprise.** The outlier row often holds the opportunity; keep it visible.
- **Writing the solution as a need** ("needs a dashboard"). Ask why until it is a job.
- **Cherry-picking quotes** that fit the favourite idea. Verification pass exists to catch this.
- **N too small.** Fewer than five interviews in the main group: label every need "early signal".

## Hand-offs
Next: `lsc-ideation-sandbox` (06) takes the selected needs and emotions. `lsc-minimum-lovable-product` (16) later reads the same table.
