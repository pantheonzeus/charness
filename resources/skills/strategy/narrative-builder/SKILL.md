---
id: narrative-builder
aliases: [narrative-builder]
name: "Narrative Builder"
category: strategy
description: "Builds executive strategy narratives using Pyramid Principle, SCQA, answer-first communication, and hostile-question prep. Use for strategy story, board deck storyline, executive narrative, recommendation story, presentation structure, or \"make this land\" requests. Not for pitch visuals, slide design, proposal reviews, or a talk track for an existing deck."
triggers: [strategy story, board deck storyline, executive narrative, recommendation story, presentation structure, make this land]
tags: [strategy, consulting, alignment-and-executive-communication]
related: ["[[decision-memo]]", "[[stakeholder-alignment]]", "[[communication-architecture]]"]
status: active
version: 2
created: 2026-07-26
updated: 2026-10-09
# imported verbatim (body unchanged) from aapersh/strategy-skills-for-claude, skills/06-alignment-and-executive-communication/narrative-builder.md — original frontmatter used name: "narrative-builder" (slug-as-name convention); description preserved above.
# Note: overlaps in theme with content/communication-architecture (Executive TL;DR -> Strategic Narrative) — that skill formats messages/reports in the Soul.md voice; this one builds the story structure (Pyramid/SCQA) for a strategy recommendation specifically.
---

# Narrative Builder

## Contract
- **Input:** an already-formed recommendation that needs to land with a specific audience.
- **Output:** the Executive Narrative structure below, delivered inline; feeds into `[[decision-memo]]` or a slide deck as the storyline backbone.
- **Allowed tools/artifacts:** conversation only — this skill structures an existing recommendation, it does not originate new analysis or evidence.
- **Done when:** the Core Message is one sentence, every Storyline headline could stand alone as the takeaway, and the Hostile Questions table has a real answer for each entry, not a placeholder.

## When To Use

Use this skill when the recommendation is mostly known but the story needs to land quickly with executives, boards, investors, or leadership teams.

## Strategy-Consulting Approach

Lead with the answer, structure support in a pyramid, and anticipate the questions a skeptical executive will ask. Use SCQA when the audience needs context and urgency.

## Workflow

1. Clarify audience, decision, tone, and desired action.
2. Extract the core recommendation and supporting logic.
3. Choose the story pattern: pyramid, SCQA, options, transformation, or roadmap.
4. Build a headline sequence.
5. Prepare hostile questions and answers.
6. Produce an executive-ready narrative outline.

## Output Format

```markdown
# Executive Narrative

## Audience and Decision
[Who must decide and what they must do.]

## Core Message
[One sentence.]

## Storyline
| Page or Section | Headline | Purpose |
|---|---|---|

## Pyramid Logic
[Recommendation, supporting arguments, evidence.]

## Hostile Questions
| Question | Answer |
|---|---|
```

## Quality Bar

- The first minute should reveal the recommendation.
- Headlines should tell the story by themselves.
- Include likely objections.
- Remove setup language that does not help the decision.
