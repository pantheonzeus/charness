---
id: lsc-customer-groups
aliases: [lsc-customer-groups]
name: "LSC 03 — Customer Groups Canvas"
category: business-design
description: Run the Lean Service Creation "Customer Groups" canvas — up to three named customer groups, each with a description and an assumed need worth solving, one marked as the main group, plus the needs common to all segments.
triggers: [customer groups canvas, LSC customer groups, who do we aim to serve, target group, main customer group, user segments canvas, love the problem not the solution, segment by need, which customers first]
tags: [lean-service-creation, lsc, canvas, segmentation, customer, need]
related: ["[[lean-service-creation]]", "[[lsc-immersion]]", "[[lsc-script-creator]]", "[[lsc-insight]]", "[[customer-segmentation]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 03 — Customer Groups

## Contract
- **Input:** `canvases/01-…` and `canvases/02-immersion.md`.
- **Output:** `canvases/03-customer-groups.md`: up to three group blocks and the common-needs field.
- **Allowed tools/artifacts:** conversation, vault client and account notes, CRM exports, `customer-segmentation` for sizing.
- **Done when:** exactly one group is marked main, each group's need passes the solution-free test, and for the main group a recruiting route to five interviewees is written.

## Canvas (v3.0.5) — "Your best guess of who you aim to serve."
Three rows, each: **Group name** · **Description** · **Need (assumed) worth solving** · **Main group** ☐. Bottom: **Common in all user segments**. Callout: **LOVE THE PROBLEM NOT THE SOLUTION.**

## Core Blueprint
1. **Draft groups by need and situation**, not by demographics or industry code alone. Pattern: "<who>, when <situation>, struggling with <need>".
2. **Write each assumed need as a problem**, starting "needs a way to…". Delete any need that names a product, feature or technology.
3. **Describe each group** in 2–4 lines: context, size guess, how they are served today (from 02). Mark size as `[I]` until sized.
4. **Choose the main group** with the sponsor: highest combination of need intensity (guess), reachability this month, and fit with the 01 objective. Tick exactly one box and write the reason. **[house]**
5. **Common needs.** List needs that appear in all groups. These are the safest core of the later concept.
6. **Recruiting route.** For the main group write where five people can be found within two weeks (own customers, partners, community, panel). In B2B name both the user and the economic buyer; they may be different groups.

## Quality tests
- At most three groups; exactly one main.
- Group names are specific enough to find a person ("regional service managers in machine building"), not "SMEs".
- Every need is solution-free and starts from the customer's difficulty.
- Reachability recorded; no main group without a route to five interviews.
- All size and need claims tagged `[I]` with the evidence that would upgrade them.

## Agent-augmented variant
An agent may propose candidate groupings from desk data (`[S]`) and flag overlaps. Synthetic personas may be used only to prepare interview questions in 04, never to rank groups (see `agent-augmented-discovery`).

## Handbook 2.0 guidance (book, Futurice 2018, paraphrased)
- Start with one group unless two are obviously different. Splitting later is expected.
- Defining groups by basic demographics is lazy. Different groups have different problems.
- Describe each group by three bullets that let you decide whether a person walking up belongs to it. Name it, and draw or print a picture of it.
- If you have not talked to a real person in the group, write the problem as an assumption.
- Fill "common in all groups" first or last. Record why the main group is main and why the others are not. Decisions can be revisited.

## Gotchas
- **Demographic trap:** age and company size rarely predict need.
- **Everyone is main.** Refuse; the whole point is the first group to learn from.
- **Buyer ≠ user (B2B, public sector).** Create two groups, or the concept will win users and lose the budget holder.

## Hand-offs
Next: `lsc-script-creator` (04) for the main group. After insight (05), revisit this canvas if the interviews show the need sits in another group. Sizing continues in `lsc-business-model-market-size` (12).
