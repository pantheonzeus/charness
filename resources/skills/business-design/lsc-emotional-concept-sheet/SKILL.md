---
id: lsc-emotional-concept-sheet
aliases: [lsc-emotional-concept-sheet]
name: "LSC 09 — Concept Sheet (Emotional Value Proposition & Fake Ad)"
category: business-design
description: Run the Lean Service Creation "Concept Sheet" — negative and positive emotions, the value gap, how the concept answers each, the emotional value proposition, the combined rational-plus-emotional proposition, the mental reward, and a fake advertisement as the first prototype.
triggers: [emotional value proposition, concept sheet emotional, LSC concept sheet, fake advertisement, fake ad prototype, value gap, mental reward, positive and negative emotions of the customer, emotions and values concept, first prototype ad]
tags: [lean-service-creation, lsc, canvas, concept, emotion, prototype]
related: ["[[lean-service-creation]]", "[[lsc-rational-concept-sheet]]", "[[lsc-insight]]", "[[lsc-validation]]", "[[lsc-experimenting]]", "[[value-proposition-design]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 09 — Concept Sheet (emotional level)

## Contract
- **Input:** `canvases/08-rational-concept-sheet.md`, `canvases/05-insight.md` (emotions and values with quotes).
- **Output:** `canvases/09-emotional-concept-sheet.md`, including the fake ad (text and a layout description or image file under `assets/`).
- **Allowed tools/artifacts:** upstream canvases, an image or layout tool, blank-paper ad template.
- **Done when:** the emotions come from interview quotes, the combined proposition is written, and the fake ad is ready to put in front of the main group in 15 or 21.

## Canvas (v3.0.5) — "Adding the emotional and value level to the concept"
Top row: **Negative emotions?** (related to the needs of the customer) → *How is the concept helping with the negative emotions?* · **Positive emotions** → *How is the concept making the most out of the positive emotions?* · **Value gap** (gap between the customer's values and current actions) → *How is this concept helping to fill the value gap?*
Middle: **Emotional value proposition:** END USER / EMOTIONAL NEED / SOLUTION · **Combine both value propositions here:**
Bottom: **What is the mental reward for the customer?** · **Fake advertisement — The first prototype:** build fake ads to test the value proposition; use blank paper; template: PICTURE, CAPTION, HEADLINE, COPY.

## Core Blueprint
1. **Collect emotions from 05 only.** List negative and positive emotions with quote ids. A new emotion without a quote is `[I]` and marked for the next interview round.
2. **Value gap.** For each value the customers hold (from 05), write what they do today that contradicts it ("values sustainability, still orders express"). Gap = the tension the concept can resolve.
3. **Answer each:** how the concept reduces a negative emotion, amplifies a positive one, closes a gap. One sentence each, concrete in the service's behaviour, not slogans.
4. **Emotional value proposition:** END USER (from 03) · EMOTIONAL NEED (e.g. "to feel in control when production stops") · SOLUTION (what the service does to give it).
5. **Combine** with the rational proposition from 08 into one statement that carries both. Test by reading it to a person in the main group; if they would not repeat it in their words, rewrite.
6. **Mental reward.** The feeling or recognition the customer gets after using the service, in the customer's language.
7. **Fake ad.** Create a one-page ad: PICTURE (what the customer sees), CAPTION, HEADLINE (the promise), COPY (3–4 lines of benefit and a call to action). It states only what the concept would truly deliver. Prepare two variants that differ in one element (headline or promise) for testing. **[house]**
8. **Test plan.** Write what response counts as success (comprehension, interest, request for more) and put it in `lsc-experimenting` (21) as an experiment; success criteria are set before showing the ad.

## Quality tests
- Every emotion is traceable to a quote id or labelled `[I]`.
- Each value gap names a value and a contradicting current behaviour.
- Combined proposition mentions both a rational outcome and an emotional one.
- Ad contains no claim the concept cannot keep.
- Success criteria for the ad test exist before any customer sees it.

## Agent-augmented variant
An agent may draft ad variants and rewrite copy (`[S]`). Reactions of synthetic personas to the ad are not evidence; only real people in the main group count (`agent-augmented-discovery`).

## Handbook 2.0 guidance (book, Futurice 2018, paraphrased)
Handbook guidance on the fake ad:
- It is the first prototype you take to customers and tests the value proposition. Design it as a print ad for a newspaper or bus stop.
- Most people look only at the picture. Choose one that carries the feeling and relationship. Brainstorm a headline that attracts the right reader.
- Write the copy as a letter to another person. Try a few approaches and watch how customers understand each.
- If the solution is hard to explain in a fake ad or landing page, the concept may be too complicated.
- Helen case: the ad was turned into a commitment test for solar panels and gathered about 2,000 potentially interested buyers. The team stated openly that the product did not yet exist and would be built only with enough interest. Adopt the same honesty rule.

## Gotchas
- **Emotions as decoration.** If nothing in the service changes because of an emotion, drop the row.
- **Promise the service cannot deliver.** The ad is a prototype of the value proposition, not marketing copy; a fake door that takes money needs a refund path and legal check (see `business-experiment-design`).
- **Testing too many things** in one ad. Change one element per variant.

## Hand-offs
Next: `lsc-impact-optimizer` (10) and `lsc-customer-engagement` (11). Ad test goes to `lsc-experimenting` (21) and verdict to `lsc-validation` (15).
