---
id: relationship-intro-pattern
aliases: [relationship-intro-pattern]
name: "Relationship / Intro Pattern"
category: knowledge-graph
description: Map who-knows-who and set up introductions — mirrored intro TODOs and shared-contact links, distinct from referrals.
triggers: [should meet, introduce, they know each other, shared contact, connect two people, knows]
tags: [people, relationships, intros]
related: ["[[contact-meeting-capture]]", "[[topic-based-linking]]", "[[person-dossier]]"]
status: active
version: 1
created: 2026-07-05
updated: 2026-07-06
vault_writes: ["cbrain/Clients/*", "cbrain/daily reports/*"]
---

# Relationship / Intro Pattern

**Triggers/Context**
- User says two people **should meet / be introduced**, or notes that people **know each other** or **share a contact**.
- Distinct from a *referral* (past-tense: X sent Y). This is present/future relationship mapping and open action items.

**Core Blueprint**
1. **Capture the shared contact** as its own client note if new (email, org, role, status = `Contact (referenced)`) — even if never met directly.
2. **`## Connections` section** on each involved person's note:
   - `Knows [[Person]] (org — role).` for existing relationships.
   - `**TODO:** introduce / meet [[Person]].` for the intro action — mirror it on **both** notes.
3. **Shared-contact linking.** On the shared contact's note, list `Known by: [[A]], [[B]]`; on A and B, link back to the shared contact.
4. **Daily report action.** Add an `**Intro:**` line — `Connect [[A]] ↔ [[B]]`, plus the shared contact and why it matters.

**Optimizations/Gotchas**
- Intro TODOs must be **mirrored on both people** — a one-sided TODO gets lost.
- Keep referral vs. relationship distinct: referral → `## Referrals` (directional, past); intro/knows → `## Connections` (mutual, open).
- People who are collaborators/contacts (not paying clients) still land in `Clients/` under current convention — flag to the user if a split (`type:` tag or separate folder) is wanted rather than silently reorganizing.
