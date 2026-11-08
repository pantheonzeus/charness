---
id: speaker-submission
aliases: [speaker-submission]
name: "Speaker Submission — CFP Abstract & Closed-Room Pitch"
category: content
description: Turn a real body of work into a speaking submission — a CFP abstract, speaker bio and programme-fit argument for association/consortium programmes, or the shorter warm pitch for a closed decision-maker room (working group, roundtable, consortium workshop). Optimizes for decision-maker concentration in the room, not audience size, and attaches whatever proof exists (reel, paper, prior stage).
triggers: [speaker submission, cfp, call for papers, conference abstract, submit a talk, speaking proposal, speaker bio, panel pitch, workshop pitch, roundtable, get on stage, speaking opportunity, keynote proposal]
tags: [content, speaking, cfp, conference, abstract, positioning, career]
related: ["[[linkedin-authentic-storytelling]]", "[[linkedin-video-script]]", "[[career-campaign-review]]", "[[communication-architecture]]", "[[audience-of-one-report]]"]
references: ["../linkedin-authentic-storytelling/references/ladder-joints.md", "../linkedin-authentic-storytelling/references/icp-positioning.md"]
modules: [evidence-backed-answering, file-backed-state]
environment: "Self-contained. Optional web_search to check a programme's theme, past speakers and deadline before writing to it."
status: active
version: 2
created: 2026-08-22
updated: 2026-10-23
vault_writes: ["cbrain/projects/*"]
---

# Speaker Submission — CFP Abstract & Closed-Room Pitch

*Encodes what was previously done ad hoc (`output/brains-on-silicon-2026-speaker-submission.md`). Two routes, and the second is the one the Ladder Campaign actually prioritises: **§A open CFP** for association/consortium programmes, **§B the warm closed-room pitch** for a working group, roundtable or workshop.*

**Contract**
- **Input:** the programme (or the room) · the joint and dialect the talk sits in · the lived work behind it · whatever proof exists (paper, prior stage, video clip, consortium role).
- **Output:** `output/<programme-slug>-speaker-submission-<YYYY-MM-DD>.md` — title, abstract at the requested length, speaker bio, programme-fit argument, attachments list, and the submission deadline/decision date.
- **Done when:** the fit argument names something specific about *this* programme, every claim in the bio is verifiable, and the deadline plus decision date are recorded for the campaign review.

**Triggers/Context**
- Deploy when: submitting to a CFP, pitching a workshop or roundtable slot, refreshing a speaker bio, or converting a past-stage contact into a new invitation.
- **Warm doors go first.** Existing speaking history and programme-committee contacts are approached before any cold submission — a known name skips the pile.
- **Not for:** a LinkedIn post ([[linkedin-authentic-storytelling]]) · a video script ([[linkedin-video-script]]) · an outreach brief on one named person ([[audience-of-one-report]], which is the better tool for pitching a specific programme chair).

**Core Blueprint**

### 0. Qualify the room before writing a word
Decision-maker concentration is the axis, **not audience size** (charter T7). Ask:
- **Who is actually in the room, and how many own a P&L?** Twenty operators beat three hundred attendees.
- **Is this reachable?** Check the deadline honestly — large trade-fair and conference programmes run 6–12 month cycles, so a submission today may pay off in 2028. Say so rather than logging it as pipeline.
- **Is there a warm door?** A past co-speaker, a programme-committee contact, a consortium partner. If yes, route through them.
- Record the answer. A room that fails this is not submitted to.

### 1. Load the substance
- Read the relevant joint row in [`ladder-joints.md`](../linkedin-authentic-storytelling/references/ladder-joints.md) and the segment in [`icp-positioning.md`](../linkedin-authentic-storytelling/references/icp-positioning.md).
- Optional `web_search`: the programme's stated theme this cycle, last year's speakers and titles, and who chairs it. **A submission that could have been sent to any programme reads exactly like one.**

### 2. §A — The open CFP submission
1. **Title** — concrete and slightly uncomfortable. Name the thing that breaks, not the topic. *"Why the data has been in that cabinet since commissioning"* over *"Digital Transformation in Manufacturing"*. No colon-subtitle consultancy constructions.
2. **Abstract** (to the requested length, never over): the specific problem in the audience's own dialect → what you actually did → what you'd tell the room to do differently → what they leave with. **One claim, evidenced.** Programme committees read hundreds; the concrete one survives.
3. **Programme-fit paragraph** — one paragraph naming *this* programme's theme, gap or prior session that this follows on from. This is the paragraph most submissions skip and the one that decides borderline cases.
4. **Speaker bio** (usually 80–150 words) — the credential that matters to *this* room, not the full CV. For consortium and association audiences: the EU Horizon role and the first-author paper. For industrial audiences: the delivered programme and its outcome. Every claim verifiable.
5. **Attachments** — first-author paper, consortium record, a prior stage, a video clip if one exists. **Never fabricate a reel that doesn't exist**; attach what is real and say what isn't.
6. **Log** the deadline and the expected decision date.

### 3. §B — The closed-room pitch (the campaign's priority route)
Shorter, warmer, and a different argument. It is a favour-shaped ask between peers, not a submission.
- **Six to ten sentences, not an abstract.** What you'd bring, why it's relevant *to that group's current agenda*, and what you want in return (usually nothing — the room is the return).
- **Lead with the specific thing you'd contribute**, not with your title. Working groups are allergic to positioning.
- **Name the concrete artifact:** joint economics from audited filings, a consortium finding, a failure you can describe honestly. Groups invite people who bring something to the table, not people who present.
- **No slide deck offered up front.** The Company A post-mortem's open hypothesis is that a 29-slide deck itself signalled consultant to a panel asking "implementer or advisor" — unresolved, and enough reason not to volunteer a deck into a room of operators. Offer to talk, bring one page if asked.
- These rooms are sourced from the watchlist's association/programme figures and from target companies' PE owners — see [[career-campaign-review]].

### 4. Record it for the campaign
- Append to `output/campaign/contact-ledger.tsv`: the person, the room, headcount if known, how many own a P&L, and the outcome. Closed rooms are **indicator 4** in the charter.
- Log a vault note in `cbrain/projects/` linked to `[[ladder-campaign]]` and the relevant topic anchor (Charter §6).
- End with the standard Feedback & Skill-Verification block (Charter §7).

**Optimizations/Gotchas**
- **Warm before cold, always.** A submission from a name the committee recognises is a different object from one in the pile. Exhaust the existing speaking history first — and record every past contact as either approached or explicitly ruled out, so "we have contacts" stops being a comfortable abstraction.
- **The fit paragraph is the whole game on borderline calls.** Generic abstracts lose to specific ones of lower quality.
- **Don't claim a reel you haven't built.** The speaker reel is conditional in the campaign plan; if it doesn't exist, attach the paper and the consortium record and move on.
- **Deadline honesty.** Logging a submission whose decision lands in eighteen months as near-term pipeline is the kind of self-deception the charter's anti-goals exist to block. Record the real date.
- **Concentration over prestige.** A prestigious stage full of vendors and consultants is worth less to this campaign than a working group of twenty plant and portfolio leaders. Prestige is pleasant; it is not the indicator.
- **A talk is a credibility artifact for the pursuit, not an end.** Nobody hands over a mandate because of a keynote; they take the call because of one. Every accepted slot should have a follow-up plan into the ledger before it is delivered.
- **Confidentiality is absolute** — abstracts and bios go through the same abstraction rules as posts. A submission is a public document.
