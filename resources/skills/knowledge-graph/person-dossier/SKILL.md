---
id: person-dossier
aliases: [person-dossier]
name: "Person Dossier — Recall, Research & Cross-Reference"
category: knowledge-graph
description: Look up (or create) a person, harvest their meetings/mail/topics/peers, add a light cited web pass, produce a re-engagement + content hook, and wire bi-directional cross-references.
triggers: [who is, brief me on, catch me up on, dossier on, pull up, remind me about, prep me for, new contact with role, name company role]
tags: [people, recall, dossier, linking, hook]
related: ["[[contact-meeting-capture]]", "[[topic-based-linking]]", "[[relationship-intro-pattern]]", "[[recall]]", "[[contact-enrichment-dedupe]]"]
status: active
version: 1
created: 2026-07-06
updated: 2026-07-06
# --- optional keys ---
requires:
  optional: [web_search, web_fetch]   # light web pass; skill degrades to vault-only without them
environment: "Runs against the live vault under cbrain/cbrain/. Web pass is optional — omit it and the dossier is vault-only, flagged as such."
vault_writes: ["cbrain/Clients/*", "cbrain/notes/[0-9]*", "cbrain/projects/*", "cbrain/daily reports/*"]
---

# Person Dossier — Recall, Research & Cross-Reference

**Triggers/Context**
- User gives a **name only** → *Recall mode*: find them, synthesize who they are / relevant topics / last interactions, produce hooks, wire missing links, enrich the note.
- User gives **name + company + role** for someone not yet in the vault → *Create mode*: create the person note, do the light research, wire links from the start.
- Fires on "who is X", "brief/catch me up on X", "prep me for X", "dossier on X", or a bare `Name / Company / Role` triple.
- Purpose: traverse the second brain like a first brain — pull every thread touching a person and leave the graph better-connected than you found it.

**Core Blueprint**
1. **Detect mode & resolve the person.** Name-only → search `cbrain/Clients/`. Name+company+role for someone absent → *Create mode*. Resolve name variants before concluding "new": two filename styles (`First Last.md` and `Last, First (Nick).md`), lowercase email-handle files (`jane.doe.md`), and `aliases:` frontmatter. If more than one candidate matches, list them and ask.
2. **(Create mode) Stand up the person note** per `[[contact-meeting-capture]]` conventions → `cbrain/Clients/<Name>.md`: `type: person`, **`status:` present** (required or `People.base` won't surface them), bold body fields (`**Company:** **Role:** **Email:** **Status:** **Headline:** **First logged:**`), then empty `## Notes`, `## Meetings`, `## Links`. Lives under `Clients/` only.
3. **Vault harvest (the recall core).** Gather everything touching them — read, don't guess: `## Meetings` links + matching `notes/YYYYMMDD-*.md`; the `Mail/Conversations.md` digest (`[[Conversations#subject]]`); their account note (`type: account`) and its `## TL;DR`; topic anchors in `projects/` that reference them; peers / co-attendees on shared meetings.
4. **Last interactions.** Order meetings + mail by date (filename `YYYYMMDD`, frontmatter ISO `YYYY-MM-DD`) into a short "most-recent-first" timeline, each with its one-line takeaway.
5. **Relevant topics.** Which `projects/` anchors touch them, plus themes recurring across their meetings. If a theme has 3+ people and no anchor yet, defer to `[[topic-based-linking]]` to create or point at one.
6. **Light web pass (optional, cited).** Quick pass for recent news / role / company context. **Cite every external claim** (Academic Rigor); label fact vs. inference; never fabricate. If web tools are absent, skip cleanly and flag the dossier as vault-only. A source worth keeping → hand to `[[source-distillation-topic-note]]`.
7. **Dual hook.**
   - **Re-engagement angle** — a sharp door-opener for the next conversation, tied to their current focus + your last interaction. State it as a *bet* with its risk; never oversell.
   - **Content/talk angle** — how this person or their theme becomes a talk/post for the audience.
8. **Cross-reference wiring (use the 2nd brain like the 1st).** Make every relevant link **bi-directional with a one-line reason** — person ↔ meetings ↔ account ↔ topics ↔ peers. Use the labeled `## Links` idiom (`Account:`, `Topic:`, `Peer on this topic:`, `Strategy:`, `Meeting:` — each followed by ` — reason`). Add the reciprocal link on the account/topic/peer note. Peers/intros → `[[relationship-intro-pattern]]`.
9. **Enrich the person note (append, never overwrite).** Refresh `**Status:**`/`**Headline:**`, add harvested links under `## Links`, add web findings as sourced `## Notes` bullets. Preserve any `## TL;DR` heading (MOC transclusion). Log a one-line touchpoint in `cbrain/daily reports/<YYYYMMDD>.md`.
10. **Present in chat** per Communication Architecture: **Executive TL;DR** (who they are · last touch · the hook) → `---` → dossier (Who / Topics / Last interactions / Dual hook / Links wired), then the Feedback & Skill Verification block.

**Optimizations/Gotchas**
- **Name resolution is the #1 failure mode** — check `aliases:` and both filename styles before concluding "new person"; a false-negative spawns a duplicate. When unsure, ask.
- **Append, never overwrite.** Auto-generated notes use `**First seen:**`; enriched ones use `**First logged:**` — keep whichever exists.
- People **and** accounts share `Clients/` (`type: person` vs `type: account`); a new person needs a `status:` field or `People.base` won't show them.
- `tags:` belong on **topic notes only** — never add them to a person or meeting note.
- Preserve exact `## TL;DR` headings — MOCs transclude them via `![[Note#TL;DR]]`.
- Web pass is lossy and optional: cite sources, separate fact from inference, flag vault-only when skipped. Distillation-worthy sources → `[[source-distillation-topic-note]]`.
- Every link carries its **reason** and its **reciprocal** — a bare `[[wikilink]]` loses the "why", a one-sided link gets lost.
- Don't oversell the re-engagement hook — it's a bet; price its risk.
