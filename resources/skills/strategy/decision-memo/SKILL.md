---
id: decision-memo
aliases: [decision-memo]
name: "Decision Memo"
category: strategy
description: Produces concise executive decision memos with recommendation, context, options, evidence, risks, and next steps. Use for decision memo, executive memo, board memo, investment recommendation, strategy approval, written recommendation, or "write this for leadership" requests.
triggers: [decision memo, executive memo, board memo, investment recommendation, strategy approval, written recommendation, write this for leadership]
tags: [strategy, consulting, alignment-and-executive-communication]
related: ["[[narrative-builder]]", "[[stakeholder-alignment]]", "[[communication-architecture]]"]
modules: [evidence-backed-answering]
status: active
version: 1
created: 2026-07-26
updated: 2026-07-26
# imported verbatim (body unchanged) from aapersh/strategy-skills-for-claude, skills/06-alignment-and-executive-communication/decision-memo.md — original frontmatter used name: "decision-memo" (slug-as-name convention); description preserved above.
# Note: overlaps in theme with content/communication-architecture (Executive TL;DR -> Strategic Narrative voice formatting) — apply that skill's voice/format rules when drafting the memo text this skill structures.
---

# Decision Memo

## Contract
- **Input:** a recommendation, its supporting evidence, and the decision the reader must make.
- **Output:** the Decision Memo structure below, delivered inline; save to `output/` and index into `cbrain/notes/Deliverables/` for board-facing memos (Charter §4).
- **Allowed tools/artifacts:** conversation plus user-supplied evidence; apply `[[communication-architecture]]`'s voice/format rules when drafting the memo text.
- **Done when:** the Recommendation is stated before any context, every entry in Options Considered has a stated trade-off and verdict, and Next Steps lists only actions that follow immediately from approval.

## When To Use

Use this skill when the user needs a written recommendation that helps executives make a decision without a long deck.

## Strategy-Consulting Approach

Write answer-first. Give the decision-maker the recommendation, why it is right, what alternatives were considered, what risks remain, and what decision is needed now.

## Workflow

1. Clarify the audience, decision, and required action.
2. Extract the recommendation and strongest evidence.
3. Summarize options considered.
4. State risks, mitigations, economics, and next steps.
5. Draft a concise memo.
6. Stress-test for executive objections.

## Output Format

```markdown
# Decision Memo

## Recommendation
[One paragraph.]

## Decision Required
[What the reader must approve or choose.]

## Context
[Why this decision matters now.]

## Options Considered
| Option | Upside | Trade-Off | Verdict |
|---|---|---|---|

## Evidence
[Key evidence supporting the recommendation.]

## Risks and Mitigations
[Material risks and responses.]

## Next Steps
[Immediate actions after approval.]
```

## Quality Bar

- Lead with the recommendation.
- Keep the memo concise.
- Include alternatives and why they lost.
- End with a clear decision request.
