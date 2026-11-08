---
id: topic-based-linking
aliases: [topic-based-linking]
name: "Topic-Based Linking"
category: knowledge-graph
description: Weave people and notes around a shared theme via an anchor/topic note when there's no referral or meeting between them.
triggers: [shared topic, common theme, connect around subject, anchor note, same area, converge on theme]
tags: [linking, topics, knowledge-graph]
related: ["[[contact-meeting-capture]]", "[[source-distillation-topic-note]]", "[[person-dossier]]"]
status: active
version: 1
created: 2026-07-05
updated: 2026-07-06
vault_writes: ["cbrain/Clients/*", "cbrain/projects/*", "cbrain/daily reports/*"]
---

# Topic-Based Linking

**Triggers/Context**
- Two or more people/notes share a theme (e.g. "AI SDLC") but there's **no referral or direct meeting** between them.
- Use to weave the knowledge graph around *subjects*, not just people — so a topic can be traversed across everyone touching it.

**Core Blueprint**
1. **Identify the shared topic** from the notes (an engagement, research area, or theme).
2. **Link each person to the anchor.** If a canonical note for the topic/engagement exists (e.g. the lead's client note like `[[Peter]]`), link everyone to it under a `## Links` → `Related engagement:` line. Consider creating a dedicated topic note if 3+ people converge and none is the natural anchor.
3. **Cross-link the people** to each other via the topic, with a short reason ("supporting AI SDLC", "funding").
4. **Reflect in the daily report** so the day's entry shows the topic cluster forming.

**Optimizations/Gotchas**
- Prefer an existing anchor note over inventing a new topic note — avoid orphan/duplicate hubs.
- Always state the *reason* for the link inline; a bare `[[wikilink]]` loses the "why" over time.
- Topic links are still bi-directional — add the back-link on the anchor (e.g. `Research support: [[Phil]]`).
