---
id: lsc-retro-diamond
aliases: [lsc-retro-diamond]
name: "LSC 23 — Retro Diamond Canvas"
category: business-design
description: Run the Lean Service Creation "Retro Diamond" — a running record of the team changes that worked, written as reusable learnings and shared with other teams and into the vault.
triggers: [retro diamond, LSC retro diamond, track team learnings, share what the team learned, what changes worked, team playbook, lessons learned register, share retro results with other teams, learning library]
tags: [lean-service-creation, lsc, canvas, learning, knowledge-sharing, retrospective]
related: ["[[lean-service-creation]]", "[[lsc-retrospective]]", "[[topic-based-linking]]"]
modules: [file-backed-state]
status: active
version: 2
created: 2026-10-22
updated: 2026-10-23
vault_writes: ["cbrain/projects/*", "cbrain/Clients/*"]
---

# LSC 23 — Retro Diamond

## Contract
- **Input:** `canvases/22-retrospective.md` changes marked "worked", the evidence of effect.
- **Output:** `canvases/23-retro-diamond.md`: one facet per worked change (change · context · result · evidence · who can reuse it), plus a vault note per facet that other teams can find.
- **Allowed tools/artifacts:** retro records, team channels, vault notes.
- **Done when:** every facet cites the retro it came from and a measured or observed effect, and each has been shared with at least one other team or is stored in the vault with links.

## Canvas (v3.0.5) — "Track and share what your team has learned."
A diamond drawn with facets; each facet holds one proven learning. Linked from the Retrospective canvas: *What change did you make based on the last retro that worked well? Add it to the Retro Diamond canvas and remember to share with other teams as well!*

## Core Blueprint
1. **Admit only changes that worked,** with evidence: before/after number, a quote, or an observed change repeated at least twice. "Felt better" is `[I]`; mark it so.
2. **Write the facet** in five lines: *Change* (what we did) · *Context* (team size, phase, constraint) · *Result* (what improved, by how much) · *Evidence* (source retro and data) · *Use when* / *Don't use when*.
3. **Name it** with a short verb phrase ("Demo every Thursday to the sponsor").
4. **Share:** post to other teams' channel or session, and write a vault note in `cbrain/projects/` linking the facet to the project, the people involved and related topic notes with a one-line reason each, both directions (Charter §6).
5. **Review facets quarterly.** Retire those that stopped working.
6. **For LSC itself:** if a facet improves a canvas procedure, propose a skill update to the matching `lsc-*` skill through the library's change process (confirm, bump version, log).

## Quality tests
- Each facet has change, context, result, evidence and use/don't-use.
- Each links to its source retro.
- At least one share action recorded per facet.
- No facet without an observed effect.

## Agent-augmented variant
An agent can draft facet text from retro and board records (`[S]`) and write the vault note links. Effect claims need the underlying numbers; the team confirms before publishing.

## Handbook 2.0 guidance (book, Futurice 2018, paraphrased)
Handbook guidance: publicly visible diamonds show that the team keeps developing its core. Sharing proven improvements is the point: "sharing is caring". If several changes were really good, add them all.

## Gotchas
- **Hoarding.** A diamond nobody else sees helps one team.
- **Anecdote as law.** Context matters; include when it does not apply.
- **Confidentiality.** Strip client names and numbers before sharing outside the project.

## Hand-offs
Feeds the next project's `lsc-retrospective` (22) and, via the self-learning loop, the `lsc-*` skills themselves.
