---
id: linkedin-repost-evaluator
aliases: [linkedin-repost-evaluator]
name: "LinkedIn Repost Evaluator — Share vs Quote-Share vs Skip"
category: content
description: Decide whether someone else's LinkedIn post is worth reposting — reuse Scorecard C (Manufacturing-Buyer Resonance + Story-over-Pitch) from the viral-scheduler rubric to score it, then verdict naked-share / quote-share-with-commentary / skip, never a bare reshare of an announcement-shaped post.
triggers: [repost opportunity, should I repost, worth reposting, quote share, share this post, repost this, is this worth resharing]
tags: [content, linkedin, engagement, repost, resharing, ssi]
related: ["[[linkedin-viral-scheduler]]", "[[linkedin-comment-engagement]]", "[[linkedin-authentic-storytelling]]", "[[source-distillation-topic-note]]", "[[linkedin-post-discovery]]"]
references: ["../../workflow-ops/linkedin-viral-scheduler/references/rubric.md", "../../workflow-ops/linkedin-viral-scheduler/references/engagement-learnings.md", "../../workflow-ops/linkedin-viral-scheduler/references/ranking-model-2026.md"]
modules: [evidence-backed-answering]
status: active
version: 2
created: 2026-07-19
updated: 2026-08-18
vault_writes: ["cbrain/notes/Sources/External-LinkedIn/*", "cbrain/projects/*", "cbrain/daily reports/*"]
---

# LinkedIn Repost Evaluator — Share vs Quote-Share vs Skip

**Contract**
- **Input:** a URL (or pasted text/screenshot) of someone else's LinkedIn post.
- **Output:** a scored verdict — **skip / naked share / quote-share with commentary** — plus rationale, saved to `output/linkedin/<slug>-repost-analysis-<date>.md`.
- **Allowed tools/artifacts:** `WebFetch` (follow LinkedIn's redirect to the canonical activity URL), a primary-source fetch for factual/news posts, vault read/write for source capture.
- **Done when:** a verdict is reached with P1/P2 scores recorded, and — if quote-share — a next step is named (draft via [[linkedin-comment-engagement]] for a short commentary, or via [[linkedin-viral-scheduler]] for a full standalone post).

**Triggers/Context**
- Deploy when asked whether a specific external post is "worth reposting," a "repost opportunity," or should be quote-shared/reshared.
- **Not** for drafting your own original post (→ [[linkedin-authentic-storytelling]] / [[linkedin-viral-scheduler]]) or for commenting without resharing (→ [[linkedin-comment-engagement]]). The two are often evaluated together on the same post — run the comment skill for the immediate low-cost engagement, this skill for the resharing decision; keep their angles distinct (see Optimizations).

**Core Blueprint**

### 1. Fetch and fact-verify
- Same as [[linkedin-comment-engagement]] §1: follow the redirect to the canonical URL, extract author/org/body/hashtags/engagement stats, and — for any factual/news claim — verify against the primary/official source before scoring or drafting commentary.

### 2. Score with Scorecard C (reused, not reinvented)
Apply the **existing** P1/P2 table from `linkedin-viral-scheduler/references/rubric.md` verbatim — do not invent a new rubric:

| Metric | 5 | 3 | 1 |
|---|---|---|---|
| **P1: Manufacturing-Buyer Resonance** | Unmistakably a manufacturing/industrial decision-maker's problem, at their altitude (capacity, capital, sovereignty, resilience) | Recognisable but generic-consulting-flavoured | Reads as written for IT/software peers |
| **P2: Story-over-Pitch** | A concrete lived moment carries the take, no announcement framing | Some narrative but the pitch shows through | Pure capability announcement or event promotion |

Score each 1–5 (single-judge is fine for a repost call — this is a lighter-weight decision than an original-post ship gate, which requires the full 3-judge blind protocol).

### 3. Verdict table
| P1 | P2 | Verdict |
|---|---|---|
| ≤3 (wrong audience) | any | **Skip.** Doesn't matter how well-told it is — it's not your ICP's problem. |
| ≥4 | ≥4 | **Naked share is defensible** — the source itself already tells a story, not a pitch; a bare reshare doesn't inherit the announcement failure mode. |
| ≥4 | ≤3 (the common case — institutional/news announcements) | **Quote-share with commentary only, never naked.** A bare reshare inherits the flat-announcement shape that scored 0.00%/0.16% in the archive (`engagement-learnings.md` Rule 1). The commentary is what makes it yours. |
| ≥4 | ≤3, but no owned wedge available | **Skip.** Don't force a quote-share without a genuine angle — a weak "interesting read" caption is broadcast, not engagement. |

### 4. If quote-share: hand off, don't draft in place
- **Short commentary** (comment-length, one wedge) → run [[linkedin-comment-engagement]]'s wedge-finding method (§2 of that skill) to produce the added text.
- **Full standalone post** (the institutional moment as the peg for a lived-moment story) → hand off to [[linkedin-viral-scheduler]] for drafting and the full three-gate scoring (substance ≥9, pull ≥8, composite ≥85) before publishing.
- Record which path was chosen and why in the output file.

### 5. Vault capture
- Same as [[linkedin-comment-engagement]] §4 — capture durable reference posts via [[source-distillation-topic-note]] under `cbrain/notes/Sources/External-LinkedIn/` (`type: source`, `source_type: linkedin-post`), bi-directionally linked to the topic anchor(s) it reinforces, logged in the day's daily report. Skip for posts not worth citing again.

**Optimizations/Gotchas**
- **Never recommend a naked reshare of an announcement-shaped post.** This is the single highest-value rule here — institutional press-release-style posts (P2 ≤3) are the exact shape that underperforms; commentary is mandatory, not optional polish.
- **A naked reshare carries someone else's semantics, not yours (added 2026-08-18).** LinkedIn's 2026 retrieval layer places content by embedding the **post text**, and a member's future retrieval is shaped by the posts they engaged with (Tier-1; [`ranking-model-2026.md`](../../workflow-ops/linkedin-viral-scheduler/references/ranking-model-2026.md) M1/M3/M4). A bare reshare puts the *original author's* text into circulation — so whatever semantic position it earns accrues to their vocabulary, not yours. **Quote-share commentary is the part that is semantically yours**, which turns the existing "commentary is mandatory" rule from a resonance argument into a positioning one as well.
- **Off-territory reposts cost more than they look (added 2026-08-18).** Resharing outside the seven pillars doesn't just read as generic — it puts off-territory text in front of your audience, and only *positively engaged* posts enter a viewer's sequence (M3). A reshare that gets ignored is a wide, unengaged impression, which retrieval training treats as a hard negative (M2). "Harmless filler repost" is not a neutral act.
- **Reach ≠ audience quality.** A post with a huge follower count and P1 ≤3 is still a skip — score the buyer fit, not the source's popularity (`engagement-learnings.md` Rule 4).
- **Don't cannibalize your own comment with the quote-share.** If both [[linkedin-comment-engagement]] and this skill run on the same post, give them distinct angles — e.g. the comment makes a tight technical wedge in the original thread, the quote-share tells a full lived-moment story that only references the institutional post as the peg. Reusing the identical line in both reads as low-effort to anyone who sees both.
- **Institutional/consortium/EU-milestone posts are the workhorse raw material** (`engagement-learnings.md` Rule 2) — score them generously on P1 even when P2 is low; that's precisely the pattern this skill exists to convert (low P2 source + your own story-first commentary = high combined result), not to filter out.
- **A single-judge P1/P2 score is a lighter bar than the ship-gate protocol** — if the repost verdict is close (P1/P2 near the ≥4 threshold) or the stakes are high (e.g. deciding whether to lead a week's content around this), escalate to the full 3-judge blind protocol from `rubric.md` rather than trusting one pass.
