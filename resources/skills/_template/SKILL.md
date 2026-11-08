---
id: skill-slug
aliases: [skill-slug]
name: "Human-Readable Skill Name"
category: knowledge-graph
description: One line — what this skill does; used for INDEX matching and relevance.
triggers: [keyword, phrase, "another phrase"]
tags: [tag1, tag2]
related: ["[[other-skill-slug]]"]
status: draft
version: 1
created: YYYY-MM-DD
updated: YYYY-MM-DD
# vault_writes: [cbrain/projects/*]   # only if the skill writes the vault (Charter §6); omit otherwise
---

# Human-Readable Skill Name

**Contract**
- **Input:** what the skill receives.
- **Output:** the exact deliverable + where it lands (e.g. `output/…`).
- **Allowed tools/artifacts:** what it may use.
- **Done when:** the observable completion condition.

**Triggers/Context**
- When this skill should be deployed.

**Core Blueprint**
1. Step-by-step tactical execution protocol.

**Optimizations/Gotchas**
- Specific failure modes avoided or user preferences learned during execution.
