---
id: contact-meeting-capture
aliases: [contact-meeting-capture]
name: "Contact & Meeting Capture → Vault Linking"
category: knowledge-graph
description: Capture a new person (name/email/date/notes) into client + meeting notes and wire up bi-directional links, branching on how you met.
triggers: [meeting someone, got to know, new contact, met today, business card, referral intro]
tags: [people, linking, crm, capture]
related: ["[[topic-based-linking]]", "[[relationship-intro-pattern]]", "[[person-dossier]]"]
status: active
version: 3
created: 2026-07-05
updated: 2026-10-29
vault_writes: ["cbrain/Clients/*", "cbrain/notes/[0-9]*", "cbrain/projects/*", "cbrain/daily reports/*"]
---

# Contact & Meeting Capture → Vault Linking

**Triggers/Context**
- User reports meeting/getting to know someone, or hands over raw notes about a person.
- Minimal input expected: **name, email, date, notes** (as a text dump or an attached file). Everything else is inferred.
- Branch on **how we met** (referral / event / inbound / cold) — this drives which links get created.

**Core Blueprint**
1. **Capture inputs.** Name, email, date (default = today), and the notes dump/file. Don't demand more; infer the rest from the notes.
2. **Resolve dates.** Convert relative dates ("Wednesday") to absolute `YYYY-MM-DD`; verify the weekday.
3. **Create client note** → `cbrain/Clients/<Name>.md`: company, email, status, interest, and a Links section. Keep it lean.
4. **Create meeting note** → `cbrain/notes/<YYYYMMDD>-<Name>.md`: `**Date:**`, `**Client:** [[Name]]`, notes body, `## Next Steps`, `## Links` (client, weather `[[YYYYMMDD-City]]`, daily report `[[YYYYMMDD]]`).
5. **Branch on how we met:**
   - *Referral* → add `**Referred by:** [[Referrer]]` and a `## Referrals` back-link on the referrer's client note (bi-directional).
   - *Event* → link the event/location note.
   - *Inbound/cold* → note the channel; no back-link needed.
6. **Attach to topic anchor(s) — MANDATORY (this is the forward link).** Identify the meeting's theme(s) and link the meeting note to the matching `type: topic` anchor(s) in `cbrain/projects/` under `## Links` (`Topic: [[<Anchor>]] — <reason>`); reciprocate on the anchor (`Meeting: [[<YYYYMMDD-Name>]] — <reason>`). Reuse an existing anchor; create one only per [[topic-based-linking]] (3+ converging, none fits). **Why it matters:** the anchor is the join point — attaching the meeting here wires it to every source/notebook already on that anchor, so past research surfaces at future meetings and this meeting is reachable from them. Skipping this leaves the meeting an island. No genuine theme match → say so; don't force one.
7. **Update daily report** → `cbrain/daily reports/<YYYYMMDD>.md`: add a touchpoint block + a next-step line. Adjust the summary count ("Two → Three touchpoints").
8. **Confirm** with a bulleted summary of files created/updated (clickable links).

**Optimizations/Gotchas**
- The live vault is under `cbrain/cbrain/` (CLAUDE.md's diagram matches this). Match the *actual* folders: `Clients/`, `notes/`, `daily reports/`, `projects/`, `Mail/`, `MOCs/`, `Bases/`.
- File-naming conventions observed: client = `Clients/Name.md`; meeting = `notes/YYYYMMDD-Name.md`; daily = `daily reports/YYYYMMDD.md`.
- **Contact filename convention = `First Last.md`.** When the source gives another form — `Last, First` (`Doe, Jane`), ALLCAPS surname (`SMITH John`), a dept suffix (`Muster Max (DC-ABC)`), or a title (`Mag. Stefan RENDL`) — keep the file (don't rename calendar/mail-sourced notes; the generators recreate them and inbound links break) but add a `aliases: ["First Last"]` line so a natural reference resolves and duplicates don't form. This is the name-resolution twin of the alias strategy in `[[vault-maintenance]]` and the dedup logic in `[[contact-enrichment-dedupe]]`.
- Bi-directional linking is mandatory (`[[wikilinks]]`) — referrals must link both ways.
- **Topic-anchor attachment (step 6) is non-negotiable** — it is the *only* way a meeting connects to research/notebooks synced before or after it. A meeting linked to no anchor is a dead-end node; prefer over-linking a plausible anchor (with a stated assumption) to leaving it orphaned.
- Existing client notes are minimal (e.g. just `female`/`male`); **append**, never overwrite existing content.
- Email is a capture field — store it on the client note even if the rest is sparse.
- **Typed records (the Commitments-Index reads these).** Each commitment under `## Next Steps` is one line `- [ ] **[Owner]** what — detail 📅 YYYY-MM-DD`: a named owner (a person note's name where one exists), the due date only when one was agreed. Each decision goes under `## Decisions` as `- **Decision** — why`. Tick `[x]` when done; never delete a line. A box without an owner shows up as `(no owner)` in `MOCs/Commitments-Index.md`.
