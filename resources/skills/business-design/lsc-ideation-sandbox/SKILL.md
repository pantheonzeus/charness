---
id: lsc-ideation-sandbox
aliases: [lsc-ideation-sandbox]
name: "LSC 06 — Ideation Sandbox Canvas"
category: business-design
description: Run the Lean Service Creation "Ideation Sandbox" — frame the sandbox with the user need, emotions and values, purpose for the user, business objective, company and team mission and purpose for society, then generate ideas that fill need, objective and/or society and choose a seed idea.
triggers: [ideation sandbox, LSC ideation, ideation workshop canvas, generate ideas from needs, seed idea, ideas that fill the user need, kickstart ideation, how might we ideate, idea generation with constraints, ideation canvas]
tags: [lean-service-creation, lsc, canvas, ideation, workshop]
related: ["[[lean-service-creation]]", "[[lsc-insight]]", "[[lsc-business-objective-context]]", "[[lsc-idea-accelerator]]", "[[service-codesign-facilitation]]"]
modules: [file-backed-state]
status: active
version: 1
created: 2026-10-22
updated: 2026-10-22
---

# LSC 06 — Ideation Sandbox

## Contract
- **Input:** `canvases/05-insight.md` (selected needs, emotions, values), `canvases/01-…` (objective, impact).
- **Output:** `canvases/06-ideation-sandbox.md`: the framed sandbox, the idea pool with origin tags, and one chosen **seed idea** with the reason.
- **Allowed tools/artifacts:** conversation or workshop, `service-codesign-facilitation` for facilitation, an agent for added divergence after humans have finished.
- **Done when:** the sandbox sides are filled from upstream canvases, the pool has at least 20 ideas, each idea is tagged with what it fills, and a seed idea is chosen with a recorded reason.

## Canvas (v3.0.5) — "To kickstart the first round of ideation"
Frame: **User need/problem** (write it at a high enough level that your idea is not the only solution) · **Emotions and values** (from the interviews) · **Purpose of the service for the user** (what job does the service do for the user? from needs, emotions and values) · **Business Objective** · **Company Mission** · **Team Mission** (ambition of the team) · **Purpose of the service for the society?** (how should it help society and environment?).
Centre: **Ideas that fill the user need, business objective and/or society purpose.**

## Core Blueprint
1. **Fill the sandbox sides from files, not memory:** need and emotions from 05, objective and mission from 01. Company and team mission are asked of the sponsor and team if absent.
2. **Lift the need.** Restate the need one level up so several solutions fit. Test: could a competitor's idea also answer this sentence? If not, it is too narrow.
3. **Write the purpose for the user** as a job sentence: "Helps <user> to <job> so that <outcome>".
4. **Diverge, humans first.** Silent writing, one idea per card, quantity over polish, at least three people. Target 20+ ideas in 15–20 minutes. **[house]** Defer judgement.
5. **Agents second.** Optionally ask an agent for ideas that fill *gaps*: needs or purposes with few ideas. Tag these `[S]` origin. Never show agent ideas before humans have written theirs (anchoring).
6. **Tag each idea** U (fills user need), B (business objective), S (society), any combination.
7. **Pick the seed idea.** Cluster, then choose by dot-vote followed by a stated reason against the sandbox: which idea fills the most sides with the least assumed behaviour change. One seed only; keep two runners-up in the pool.

## Quality tests
- Sandbox text matches upstream canvases; no new facts invented.
- Need statement is solution-free and not solved by one idea only.
- Pool ≥ 20 ideas, each tagged U/B/S, origin human or `[S]`.
- Seed idea has a written reason that cites at least two sandbox sides.
- Ideas that fill only B are visibly labelled; they need a user reason before concepting.

## Agent-augmented variant
Allowed: agent-generated gap-filling ideas, analogies from the 02 analogues, and "what would break this idea" prompts. Not allowed: an agent choosing the seed.

## Handbook 2.0 guidance (book, Futurice 2018, paraphrased)
Handbook "Ideation Kick Off" structure: fill the inner circle from the interviews (selected need, negative emotions, positive emotions), then brainstorm three idea groups around it:
1. ideas that solve the customer's problem, even partial ones or single features;
2. ideas that fix, eliminate or reduce the pain behind the negative emotions;
3. ideas that take the best out of the positive emotions.
- Negative emotions exist independent of your service. When people cannot name them, ask about concrete steps: what did you do next, why, how could it have been better.
- Use How Might We statements and other methods to break mental logjams.

## Gotchas
- **Solutioning in the need box.** Re-lift.
- **Idea pool full of features.** Ask each author: which need does this serve, and what job does the user hire it for?
- **Skipping society.** Even one honest sentence changes later impact work in 10.

## Hand-offs
Next: `lsc-idea-accelerator` (07) with the seed idea. Alternative: drop into `service-design/service-codesign-facilitation` if the session is run with customers.
