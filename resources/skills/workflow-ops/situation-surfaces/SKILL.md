---
id: situation-surfaces
aliases: [situation-surfaces, surfaces, generative-ui, component-catalog]
name: "Situation Surfaces — Answers as Interfaces from the Desk's Own Catalog"
category: workflow-ops
description: Compose a meeting or an answer as a structured surface (a stakeholder map, risk sheet, metrics, timeline, decision card, person card, document list or callout) by writing JSON that picks only from the console's component catalog. The desk renders it; no generated code runs. Every block carries a confidence level and sources, and the renderer makes unsure blocks visibly rougher. Used ahead of time by the meeting-prep loop and on demand by the conversation.
triggers: [show me the situation, map the stakeholders, risk sheet, show it as a, visualize this, surface, situation view, stakeholder map, decision card, compose a view, what does the picture look like]
tags: [workflow-ops, console, generative-ui, a2ui, evidence]
related: ["[[meeting-prep-loop]]", "[[living-plan]]"]
status: active
version: 2
created: 2026-10-11
updated: 2026-11-08
modules: [evidence-backed-answering]
scripts: [scripts/surface.py]
---

# Situation Surfaces

**Contract**
- **Input:** a meeting (from the meeting-prep loop's TASK.json and its prep) or a question in the conversation.
- **Output:** one JSON file, validated by `uv run resources/skills/workflow-ops/situation-surfaces/scripts/surface.py check <file>`:
  - meetings go to `output/meetings/surfaces/<uid>.json`;
  - answers go to `output/surfaces/<YYYYMMDD-HHMMSS>-<slug>.json`.
- **Allowed:** only the component types below. No HTML, no markup and no code in any string; the desk escapes everything anyway.
- **Done when:** `surface.py check` prints `OK`.

**Why a catalog and not generated code.** This follows Google's A2UI pattern (agent JSON rendered from a client-owned catalog of pre-approved components). The desk owns the look and what each component can do; the agent only chooses and fills. It's safe, consistent and local. Polished layouts read as more credible, and not only because of the content (Chen et al., arXiv 2508.19227: 86.5% of credibility-related comments favoured the generative UI, §4.3, Table 4), so **every block declares its confidence, and the renderer makes `unsure` look rougher**.

**Envelope**
```json
{"version": 1, "kind": "meeting | answer", "title": "GER Alignment — where RSG stands",
 "uid": "<meeting uid, meetings only>", "fingerprint": "<from TASK.json, meetings only>",
 "generated_at": "<date -Iseconds>",
 "basis": [{"label": "RSG Team-Workbench 29.09", "ref": "cbrain/projects/RSG Mitglieder-Apps RFP.md"}],
 "blocks": [ … 1 to 6 blocks … ]}
```
Every block has `type`, an optional `title`, a `confidence` of `verified`, `likely` or `unsure`, and `sources` (a list of strings). A `verified` block needs at least one source.

**Catalog**

| type | fields | use it for |
|---|---|---|
| `Callout` | `text`, `tone`: info · risk · good | the one thing; a warning |
| `MetricRow` | `items`: [{`label`, `value`, `delta`?, `source`?}] (≤ 6) | real numbers only, each from a source |
| `RiskSheet` | `items`: [{`label`, `level` 0–1, `note`?}] (≤ 8) | how close each risk is to biting (a judgment, so usually `likely`) |
| `StakeholderMap` | `people`: [{`name`, `role`?, `stance`: champion · supporter · neutral · skeptic · blocker · unknown, `influence` 0–1, `note`?}] (≤ 10) | who matters and where they stand |
| `Timeline` | `events`: [{`date` YYYY-MM-DD, `label`, `kind`: past · next · deadline}] (≤ 10) | history and what's coming |
| `DecisionCard` | `question`, `options`: [{`label`, `for`?, `against`?}] (2–4), `recommendation`? | a decision the meeting or answer has to make |
| `PersonCard` | `name`, `role`?, `company`?, `note`?, `ask`? | a 1:1: who they are now and what to ask |
| `DocList` | `docs`: [{`name`, `link`?, `by`?, `when`?, `insight`?}] (≤ 6) | documents that matter, each with why |

**Composing**
1. Pick **2–4 blocks** that show the *shape* of the situation. Don't restate the prep text.
   - **Client or sales call:** StakeholderMap + DecisionCard (what you need from the call) + Timeline.
   - **Internal leadership sync:** RiskSheet and/or MetricRow + Callout.
   - **1:1:** PersonCard + Callout (the ask) + Timeline when there's history.
   - **Strategy question in the conversation:** DecisionCard + MetricRow or RiskSheet.
2. **Never invent a number.** `MetricRow` values come from sources. `RiskSheet` levels and `StakeholderMap` stances are judgments, so mark them `likely` or `unsure` and say so in `note`.
3. **List the notes, mails and documents you used in `basis`.** The desk shows them under the surface.
4. Run `surface.py check` and fix until it prints `OK`.

**Optimizations/Gotchas**
- **One stance per person.** If you don't know someone's stance, use `unknown`; don't guess "neutral".
- **Keep it small.** A surface with 6 dense blocks is a dashboard again; 2–4 is the target.
- The conversation should only compose a surface when the answer genuinely has shape (people with stances, several risks, a dated sequence, a decision with options). A plain answer stays text.
