---
id: design-frontier-scan
aliases: [design-frontier-scan, future-ui-research, interaction-frontier]
name: "Design Frontier Scan — Three Researchers → Concept Directions → Recommendation"
category: research
description: Find out what "next generation" really means for an interface, product surface or interaction model. Three parallel researchers each cover one lane (shipped products, the research frontier, the visual/experiential language). A synthesis then produces 2–3 distinct concept directions with animated mockups on a local page, ending in one recommendation, a phased build order and non-negotiables.
triggers: [look like it is from the future, next gen interaction, next-gen UI, cutting edge interaction patterns, future interface, reimagine the UI, completely new interface, design frontier, interaction design research, what should this UI become, ai interaction patterns, redesign the app, futuristic ui]
tags: [research, design, ux, ui, interaction, frontier, delegation, mockup]
related: ["[[deep-research]]", "[[service-concept-prototyping]]", "[[app-architecture]]", "[[agentic-service-blueprint]]"]
status: active
version: 1
created: 2026-10-11
updated: 2026-10-11
modules: [file-backed-state, file-backed-handoff, evidence-backed-answering]
references: [references/task-packets.md]
---

# Design Frontier Scan

**Contract**
- **Input:** the surface to reimagine (an app, a console, a product flow), what it does today, its users, and hard constraints (stack, privacy, build tooling).
- **Output:**
  - `output/<YYYYMMDD>-<slug>-concepts.html`: a local page with the thesis, 2–3 concept directions each with an animated mockup ("what's new / grounding / risk"), one recommendation, a phased build table and non-negotiables. Open it with `open`.
  - A vault index note through `vault-hygiene/deliverable-index`.
  - The STATE_ROOT `output/.runs/<YYYYMMDD>-<slug>/` with the spine and `children/{products,research,visual}/{TASK,RESPONSE}.md`.
- **Allowed tools/artifacts:** the Agent tool (3 fresh children in parallel), WebSearch/WebFetch inside the children, Write for the STATE_ROOT and the concepts page. **No hosted Artifact page.** Deliverables stay in `output/` and the vault (memory: no-claude-web-artifacts).
- **Budget:** at most 25 web lookups per child, so about 75 in total. One synthesis pass.
- **Done when:** all three child `RESPONSE.md` files have been reopened from disk, the concepts page exists and opens, it's indexed in the vault, and every spine box is `[x]`.

**Triggers/Context**
- The user wants something "from the future", "completely new" or "next-gen", not a polish pass. A polish or usability fix is a normal design task; don't fan out for that.
- Precedes a build. Its output is a decision (which direction), not code.

**Core Blueprint**
1. **Spine first.** Write `RESPONSE.md` with four boxes: `products`, `research`, `visual`, `synthesis`.
2. **Three task packets, one per lane, context mode fresh** (Charter §5). Use the templates in [`references/task-packets.md`](references/task-packets.md). Every packet carries the same context block: what the surface is, its users, the stack and its constraints, and the "completely new, not a nicer X" bar. Every packet also carries the same rules:
   - primary sources first, each item with a URL and date
   - tag each item SHIPPED, DEMO/RESEARCH or SPECULATIVE
   - flag secondary-only sources
   - a 25-lookup cap
   - result written to `RESPONSE.md`, with a one-line status as the inline reply
   - each lane ends in a ranked top 5
3. **Launch all three in one message**, `run_in_background`. While they run, mark the open boxes `[~]` and add a pause line. **The pause line must not contain the literal unchecked-box text**, because the Stop gate greps for that exact string (learned 2026-10-11).
4. **As each child reports, reopen its `RESPONSE.md` from disk** and tick its box. The hand-back message is a status line, not the record.
5. **Synthesize into 2–3 directions that are genuinely distinct.** Distinct means they differ in *what you can do*, not in skin. For each direction:
   - **What's new:** 4–5 concrete mechanics.
   - **Grounding:** each mechanic tied to a lane finding with its tag; carry the effect sizes over from the research lane.
   - **Risk:** the honest one.
   - **Mockup:** an inline HTML/CSS/JS mockup on real (local) data. Motion must encode state, and every motion needs a `prefers-reduced-motion` version.
6. **Recommend one combination and say why.** Weigh evidence of value (research lane) against felt novelty (visual lane) against cost and risk. Give a phase table (phase · what you get · built on) and 3–5 non-negotiables. Then ask the user which phase to build.
7. Open the page, run the deliverable index, tick the synthesis box.

**Optimizations/Gotchas**
- **Polish raises trust more than it should.** Generative or polished UI raised perceived credibility in 86.5% of comments, even when the content was no better (Chen et al., arXiv 2508.19227). Longer explanations raise confidence without raising accuracy (Steyvers et al., 2025). Any direction that adds polish must also add visible confidence (rougher when unsure).
- **Clichés to name and reject up front:** the central pulsing orb, HUD wireframes, gesture-flinging, glass under body text, and "a dashboard dressed up as agents" (kanban, KPI tiles).
- **Mockups on real data persuade more than lorem ipsum.** They stay local (`output/` is git-ignored). Never publish them.
- **The visual lane's citations rest most often on secondary sources** (design-system critiques, platform guidelines behind digests). Carry those flags into the page's grounding notes.
- First run, 2026-10-11 (cbrain desk): 3 children took about 2.5 minutes each, about 75 lookups in total. The synthesis recommended direction B's substance inside direction A's room and was built as "the room" the same day. Run log: `output/.runs/20261011-future-ui/`.
