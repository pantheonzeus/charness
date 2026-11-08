---
id: client-follow-through
aliases: [client-follow-through, meeting-follow-up, client-brief, follow-up-draft]
name: "Client Follow-Through — Post-Meeting Follow-Up Draft & Client-Shareable Brief"
category: sales
description: Makes the prep visible to the client. (A) After a meeting, it drafts the follow-up email with what was agreed, who owes what by when, and one fresh, public, cited finding from the vault-frontier loop that moves their problem forward. (B) Before or after a meeting, it builds a one-page brief the client can keep, made only from public sources and client-safe findings. Both pass a deterministic confidentiality gate and are drafts only. Nothing is ever sent.
triggers: [follow-up email, follow up on the meeting, draft the follow-up, recap email, after the meeting, send them a summary, client brief, one-pager for the client, something to leave behind, leave-behind, share with the client, expand the client discussion]
tags: [sales, client, follow-up, meeting, confidentiality, email-draft]
related: ["[[meeting-prep-loop]]", "[[vault-frontier-loop]]", "[[communication-architecture]]", "[[pursuit-deal-tracking]]", "[[executive-dialogue-planner]]"]
status: active
version: 1
created: 2026-10-11
updated: 2026-10-11
modules: [evidence-backed-answering, verifier-separation]
scripts: [scripts/client_gate.py]
---

# Client Follow-Through

**Contract**
- **Input:** a meeting (uid or title from `output/meetings/meetings.json`) plus, for a follow-up, **what was agreed**, in the user's words. Read the meeting's prep (`output/meetings/prep/<uid>.json`), the vault meeting note, the account and person notes, and `output/frontier/*.json` from the last 14 days.
- **Output:**
  - (A) `output/client/followups/<YYYYMMDD>-<meeting-slug>.md`: subject line plus email body, in the language of the meeting (German if the client writes German).
  - (B) `output/client/briefs/<YYYYMMDD>-<account-slug>.md`: a one-page brief.
  - Both as files only. **Never send, never create a mail draft in a connected account unless the user asks in this turn.**
- **Allowed tools/artifacts:** Read/Grep/Glob over the vault and `output/`; WebFetch only to re-open a source you cite; Write for the two folders above; `python3 resources/skills/sales/client-follow-through/scripts/client_gate.py`.
- **Done when:** `client_gate.py check <file> --account "<their company>"` prints `OK` (with `--allow-email` for the recipients, `--allow-money` only if the user put a price in on purpose), and the user has been told the path plus the one line most worth reading twice.

**Triggers/Context**
- From the console: **Draft follow-up** on a meeting that ended today, or **Client brief** on any meeting with external participants. In conversation: "draft the follow-up for …", "give them something to keep".
- Who the client is comes from the meeting's external participants (`internal: false`) and their notes' `company:`.

**Core Blueprint**
- **A. Follow-up draft** (what made the meeting worth it, in their inbox within 24h)
  1. **Facts only from the user and the record.** What was agreed comes from the user's line and the meeting note. If the user gave nothing, ask **one** question: "What was agreed, and who owes what?" Don't invent outcomes from the prep's goal.
  2. **Shape** (≤ 180 words; `content/communication-architecture` answer-first):
     - one line of thanks that names the actual topic;
     - **Agreed**: 2–4 bullets;
     - **Next steps**: owner · action · date, theirs and ours;
     - **One new thing**: a finding from the frontier digests with `client_safe: true` that fits their problem. Give the fact, one sentence on what it means for them, and the public link. Use the prep's `new_insight` if there is one. If none fits, leave the section out; a forced insight reads as filler.
     - a close with the next meeting or decision date.
  3. Run the gate. Fix and re-run until it prints `OK`. Then tell the user the path, and name the next step most likely to slip.
- **B. Client-shareable brief** (the leave-behind that makes them remember the meeting)
  1. **Their problem, in their words.** Take it from the meeting note and mails, but **paraphrase, never quote** internal material, and never mention other clients, prices, our pipeline or what we think of their people.
  2. **Shape** (one page):
     - title naming their question;
     - **What's changing**: 3–5 client-safe findings, each with a public source and date;
     - **What it means for you**: 2–3 implications, marked as our view;
     - **Questions worth deciding**: 2–3;
     - **Sources**: the links.

     No logos, no claims about our track record unless public, and no numbers you didn't read in the source.
  3. Run the evidence gate (`_shared/evidence-gate.md`). Every factual line has a public source. Then run `client_gate.py`. Both must pass.
  4. Tell the user it is a draft for them to read before sharing, and name the one line most likely to need their judgment.

**Optimizations/Gotchas**
- **The gate is necessary, not sufficient.** It catches other accounts, other companies' people, money, internal markers, emails and missing sources. It can't catch a paraphrased secret. Read your own draft once as the client's competitor would, before you run it.
- **"3 million users" trips the money check** (it errs on the safe side). Rephrase, or pass `--allow-money` if the number is public and sourced.
- **Confidential stays confidential** (Soul, inviolable): a finding marked `client_safe: false` never reaches a client document, however useful it looks.
- **Follow-ups decay fast.** Offer the draft on the day of the meeting. After 48 hours, lead with the next step, not the recap.
