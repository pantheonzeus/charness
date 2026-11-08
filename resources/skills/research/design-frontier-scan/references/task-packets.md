# Task-packet templates: the three lanes

Copy each section into `STATE_ROOT/children/<lane>/TASK.md`. Replace `<…>` and append the shared **Context** and **Rules** blocks verbatim to every packet. The lanes are deliberately non-overlapping, so the synthesis gets three angles instead of three copies.

## Lane 1: products (`children/products/TASK.md`)
```
# Task: shipped interaction patterns for <surface>, <last 18 months>
Find the interaction patterns leading products actually ship now, beyond <the current default, e.g. chat boxes / dashboards>.
Cover at least: <6–10 pattern families relevant to the surface, e.g. generative UI, background agents with notify/approve,
voice/realtime multimodal, canvas/spatial workspaces, proactive surfacing, multi-agent mission control, memory/context visibility, wearables>.
For each: what it is (2 lines), who ships it, link+date, what's genuinely new about the interaction, how it applies to <surface>.
End with the 5 patterns most worth stealing for <surface>, ranked.
Output file: <STATE_ROOT>/children/products/RESPONSE.md
```

## Lane 2: research frontier (`children/research/TASK.md`)
```
# Task: the research frontier for <the interaction problem, e.g. humans working with agent teams>
Find the frontier (CHI, UIST, CSCW, IUI, FAccT <last 2 years>; arXiv; respected lab and researcher blogs).
Cover at least: <6–10 concepts, e.g. generative/malleable interfaces, mixed-initiative and interruption, oversight and checkpoints,
intent-based interaction and feedforward, shared representations, calm/ambient computing, turn-taking, trust calibration>.
For each: the idea in 2 lines, key source (authors, venue, year, URL), evidence of what works (effect sizes where they exist),
what it would look like in <surface>.
End with the 5 concepts most likely to make <surface> genuinely next-generation, ranked, and the 3 known failure modes to avoid.
Output file: <STATE_ROOT>/children/research/RESPONSE.md
```

## Lane 3: visual and experiential language (`children/visual/TASK.md`)
```
# Task: a design language for <surface> that reads as the future, not as a trend
Cover at least: current design-system directions, how leading products visualize <the key states, e.g. presence/listening/thinking/speaking>,
showing <parallel activity, e.g. multiple agents> without dashboards, speculative/sci-fi lessons (what aged well, what's cliché),
calm technology, typography and motion for live content, accessibility constraints (reduced motion/transparency, contrast),
and what's feasible in <the stack, e.g. vanilla HTML/CSS/JS without a build step> today.
For each: the principle, references with links and dates, a concrete motif for <surface>.
End with a proposed visual direction: 5 signature motifs and 5 things to avoid.
Output file: <STATE_ROOT>/children/visual/RESPONSE.md
```

## Shared Context block (fill once, append to all three)
```
## Context
<What the surface is and what it does today, column by column or flow by flow.>
<Who uses it, and what they care about (role, priority lens).>
<Stack and hard constraints: build tooling, privacy, local-only, platforms.>
The bar: "<the user's words, e.g. something completely new>" — not a nicer version of what exists.
```

## Shared Rules block (verbatim)
```
## Rules
- Primary sources first (official product pages/docs/changelogs, papers, author blogs). Cite every item with a URL and date. No content farms.
- Prefer the last 18–24 months; say when something is older but still the frontier.
- Tag every item SHIPPED (people use it today), DEMO/RESEARCH (prototype, paper) or SPECULATIVE.
- Mark any fact you could only reach through a secondary source.
- Budget: at most 25 web searches/fetches. Stop and write when you hit it.
- Write your result to the RESPONSE.md path above (max ~1500 words), then reply with one status line only.
```
