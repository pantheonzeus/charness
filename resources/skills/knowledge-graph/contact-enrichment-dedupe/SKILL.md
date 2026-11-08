---
id: contact-enrichment-dedupe
aliases: [contact-enrichment-dedupe, contact-cleanup, dedupe-contacts, enrich-contacts]
name: "Contact Enrichment & Dedupe — Clients/ Hygiene"
category: knowledge-graph
description: "Repeatable pass over Clients/ to purge non-person notes (lists/rooms/system senders), merge duplicate & split-series contacts via aliases, and enrich unenriched `status: new` people from vault evidence + a light cited web pass — without fighting the generators."
triggers: [enrich contacts, clean up contacts, dedupe contacts, merge duplicate contacts, junk people, status new contacts, contact hygiene, who are these contacts, upgrade contact status, split contact series]
tags: [knowledge-graph, contacts, people, dedupe, enrichment, hygiene, obsidian]
related: ["[[person-dossier]]", "[[contact-meeting-capture]]", "[[vault-maintenance]]", "[[calendar-to-contacts]]", "[[mail-to-conversations]]"]
status: active
version: 1
created: 2026-07-11
updated: 2026-07-11
vault_writes: ["cbrain/*"]
---

# Contact Enrichment & Dedupe — Clients/ Hygiene

The `Clients/` folder is fed by two append-only generators (`[[calendar-to-contacts]]`, `[[mail-to-conversations]]`). They cannot judge *who is a person*, *who is the same person twice*, or *which relationship is real* — so `Clients/` accumulates three debts this skill clears: **junk non-persons**, **duplicates/split series**, and **unenriched `status: new` stubs**. It is the person-side twin of `[[vault-maintenance]]` (which does whole-vault links) and the batch companion to `[[person-dossier]]` (single-person deep dive).

**Triggers/Context**
- "clean up / enrich the contacts", "dedupe contacts", "who are these people", "upgrade the new contacts", "why do I have a contact called Team Acme".
- After any bulk import (calendar or mail run) — those generators are the source of the debt.
- Pairs with `[[vault-maintenance]]`: run this first (fewer junk people ⇒ fewer junk links), then the whole-vault sweep.

**Core Blueprint**
1. **Purge non-persons — reuse the generator filter, don't eyeball.** A contact is not a person if its `**Email:**` local-part hits `build_contacts.py`'s `_FUNCTIONAL_LOCAL_RE` (functional tokens: `purchase-orders`, `team-`, `-calendar`, `info`, `events`, `supervisors`, …) **or** `_is_list_domain()` (`*.onmicrosoft.com`) **or** contains `group.calendar.google.com` / `calendar-invite@`. Import those checks:
   `python3 -c "import sys; sys.path.insert(0,'resources/skills/workflow-ops/calendar-to-contacts/scripts'); import build_contacts as bc; …"` and scan every `Clients/*.md`. For each hit: delink inbound `[[Name]]`/`[[Name|alias]]` → plain text across the vault (table-pipe- and code-span-aware, per `[[vault-maintenance]]`), then delete the note. Regenerate `MOCs/*-Index.md` (they self-heal). **Confirm the list with the user before deleting** (Clarify Before Action).
2. **Dedupe by alias, never by rename.**
   - **True duplicate** (same person/meeting, two files): keep the canonical (the one hubs already link), merge unique body, add the other's name form to the canonical's `aliases:`, repoint hand-authored inbound links, delete the dupe. Safe only when the note is **not** regenerated (past-dated meetings, hand-made contacts).
   - **Name-variant person** (`Last, First` / ALLCAPS / dept-suffix / title): add a `aliases: ["First Last"]` line — one line resolves every reference. **Never rename** a calendar/mail-sourced note: the generator recreates it under the old slug on the next run and inbound links break. Verify first/last order against the `**Email:**` local-part.
   - **Split recurring series** (`X-Christoph` vs `X-Christoph-1-1`): this is source-driven (inconsistent calendar event titles). Do **not** rename to unify — the generator will recreate the old slug. Leave it; fix the calendar event title upstream if it matters.
3. **Enrich `status: new` — evidence first, judgment always.**
   - **Harvest vault evidence** (Charter §6, no external calls): the person's `## Meetings`, `## Mail`, `company`, linked topics/accounts. Write a one-line context and wire bi-directional links to their account + topic anchors.
   - **Light cited web pass** for genuinely key *external* stakeholders only (delegate to `[[person-dossier]]`): role, org, one public hook. Tag every added fact per the evidence gate (`_shared/evidence-gate.md`) — observed/inferred/assumed, with a source. Never web-profile internal colleagues or one-off attendees en masse.
   - **Flip `status`** on real evidence: `new → active` (ongoing relationship), `reconnect` (dormant), or leave `new`. **Meeting count is not evidence** — see Gotchas.
4. **Close bi-directionally + log.** Every enriched/merged person links to their account and topic anchors and back; note the touch in the day's `daily reports/` entry.

**Optimizations/Gotchas**
- **Meeting count ≠ relationship strength.** `## Meetings` is inflated by *future-dated recurring-series stubs* — a weekly standup shows as 16 "meetings," and a one-off recurring invite gives 3. Never flip `status: new → active` on raw count; judge distinct real interactions. This is why bulk mechanical status-flips are wrong.
- **The generator is the root cause — fix it before the output.** If a junk pattern recurs, extend `_FUNCTIONAL_LOCAL_RE`/`_is_list_domain` in `build_contacts.py` (and `_AUTO_LOCAL` in `build_conversations.py`) and bump the skill version, rather than deleting the same note every import.
- **Aliases > mass edits** (`[[vault-maintenance]]`): one `aliases:` line beats editing dozens of referencing files. `First Last.md` is the target filename convention (`[[contact-meeting-capture]]`).
- **Accounts live in `Clients/` too** (`type: account`) — don't treat them as people to enrich; `People.base` filters on `status`, so both coexist. Self-references (`[[Your Name]]`, the vault owner) → plain text, never a contact.
- **Mail bodies** land empty until a fetch carries `body_text` (`[[mail-to-conversations]]` v4 `msg_body()`); backfilling them needs the Google Workspace MCP, not this skill.
- **Don't over-purge:** a functional-*looking* local-part on a boundary (`steam`, `christoph`) is a real person — the regex is word-boundary-anchored for exactly this reason. When unsure, keep and flag.
