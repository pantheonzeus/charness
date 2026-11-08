---
id: campaign-week
aliases: [campaign-week]
name: "Campaign Week — the Ladder Campaign's Single Weekly Entry Point"
category: workflow-ops
description: One command that runs the Ladder Campaign's weekly rhythm in priority order — loop-integrity check, ledger sweep, then pursuit before content, then distribution — dispatching to the skills that already own each step and enforcing the order rather than reimplementing anything. Exists because a campaign spanning eight skills fails on the week someone forgets one, which is exactly how two weeks of August 2026 became unmeasurable.
triggers: [campaign week, weekly campaign, run my week, my week, weekly rhythm, what should i do this week, ladder campaign week, campaign standup, weekly run]
tags: [workflow-ops, campaign, career, orchestrator, router, weekly, adherence]
related: ["[[career-campaign-review]]", "[[linkedin-weekly-review]]", "[[linkedin-viral-scheduler]]", "[[linkedin-post-discovery]]", "[[linkedin-comment-engagement]]", "[[pursuit-deal-tracking]]", "[[account-priority-map]]", "[[linkedin-video-script]]", "[[speaker-submission]]"]
references: ["../../content/linkedin-authentic-storytelling/references/ladder-joints.md"]
modules: [file-backed-state]
environment: "Local terminal with vault access. Dispatches only — owns no scripts. Google Workspace MCP is optional; without it, moment-generating activity is scheduled by hand."
status: active
version: 1
created: 2026-08-22
updated: 2026-08-22
---

# Campaign Week — the Single Weekly Entry Point

*A **router with a checklist**. It owns no machinery and reimplements nothing — every step dispatches to the skill that already owns it. What this skill contributes is the **order**, and the order is the whole point: after the Company A finding, pursuit outranks content, and when a week compresses content is what gets cut.*

**Contract**
- **Input:** the trigger, plus whatever happened in the user's week.
- **Output:** the week's artifacts (wherever the dispatched skills put them) **plus** a five-line status back to the user — what moved, what didn't, the one thing next.
- **State:** `output/.runs/<YYYYMMDD>-campaign-week/RESPONSE.md` as the control spine, so a week interrupted mid-way can be reopened by path.
- **Done when:** steps 0–2 have run (they are not optional), every skipped step is named with a reason, and the status has been handed back.

**Triggers/Context**
- Weekly, on demand: "campaign week", "run my week", "campaign standup".
- **Not for:** the monthly indicator roll-up ([[career-campaign-review]]) · a single post ([[linkedin-viral-scheduler]]) · a single pursuit ([[pursuit-deal-tracking]]).
- **Governing documents:** `output/20260822-ladder-campaign-charter.md` (indicators, anti-goals, hour split) and `-90day-plan.md` (which block we're in). Read the charter's §9 falsification list if a week's evidence looks like it contradicts the strategy.

**Core Blueprint**

Run in order. **Steps 0–2 are mandatory**; 3–6 are cut in reverse order when the week is short.

### 0. Loop integrity — before anything else (~5 min)
- List posts published in the last ~10 days. For each: does a vault note exist, and a post-level export row, inside 72h?
- Dispatch the CP0 gate in [[linkedin-weekly-review]] for the real check and the backfill.
- **A gap blocks interpretation, never work.** You can still post today; you cannot conclude anything about last week. Say "this window is partial" and keep the flag raised in every subsequent week until it clears.
- This step exists because 2026-08-06→08-17 produced five posts with no demographics — a state strictly worse than bad numbers.

### 1. Ledger sweep (~10 min) — the primary indicator
- Who **replied, connected, reached out, invited, or took a call** this week? Append named rows to `output/campaign/contact-ledger.tsv`: date · person · company · target class · board state · action · direction · content-attributed · owns P&L · next step.
- Do it now, not at month end. Named-person memory decays inside a week and this is the charter's indicator #1.
- **Never invent a row.** An empty week is a real datum.

### 2. Pursuit — the largest slice (~6h)
Advance **exactly one** target. Not three shallowly.
- Pick from `output/campaign/target-list.md`. If rows 2–12 don't exist yet, this step *is* the research: screen candidates against the five board states with cited evidence.
- Then one of: board-state evidence gathered · joint diagnosis written ([`ladder-joints.md`](../../content/linkedin-authentic-storytelling/references/ladder-joints.md)) · decision-maker mapped · approach sent.
- Dispatch: [[account-priority-map]] · [[competitive-porter-teardown]] · [[audience-of-one-report]] · [[pursuit-deal-tracking]] for the anchor.
- **If a live process surfaced this week, run the qualify-out test** and record the verdict in `output/campaign/qualify-out-log.md` — entered *or* declined. A declined process is progress; log it as such.

### 3. Content — the substantive post (~2h)
- Read `output/linkedin/history.tsv`, take the joint the recency guard permits, name the dialect.
- **Confirm a real lived moment exists first.** If none does: **no post, stated plainly**, and note what moment-generating activity is booked next. This is the guard that August lacked.
- Dispatch [[linkedin-viral-scheduler]] (4-iteration budget, three gates, plus the methodology check).

### 4. Content — the light asset (~1h)
Field recap, a quote-share carrying a joint diagnosis ([[linkedin-repost-evaluator]]), or a video if a visit happened ([[linkedin-video-script]]). Optional by design — it is the *light* slot, not a second substantive post.

### 5. Distribution — five comments, person-first (~2h)
- Work `output/campaign/watchlist.md`, **not** whoever posted something good. Five comments a week scattered across strangers accumulates nothing; five under the same ~30 people builds the recognition the contrast-candidate slot lacks.
- Dispatch [[linkedin-post-discovery]] for the queries (you run them in your own browser — no authenticated session reaches here), then [[linkedin-comment-engagement]] per post.
- Warm connects only: comment substantively for a few weeks *before* connecting, and reference the exchange.
- Update `last touch` on each watchlist row.

### 6. Substance + rooms — monthly slot (~4h/month)
- One joint's economics from **listed-OEM annual reports** (service revenue share, recurring-revenue disclosure, margin bridges). Hard stop per joint — shipped beats complete.
- Any closed-room opportunity → [[speaker-submission]] §B. Warm doors before cold submissions.

### 7. Status back — five lines, not a report
1. Loop integrity: clean / partial (and what's missing).
2. Ledger: the named actions, or "none".
3. Pursuit: which target moved, and how.
4. Content: what shipped, or why nothing did.
5. The one thing to do next week.

Then tick the control spine. If a Charter §7 feedback block is appropriate, one line is enough — this is a recurring operational run, not a deliverable.

**Optimizations/Gotchas**
- **The order is the contribution.** Content is the pleasant part and pursuit is the part that ends in an offer. Running content first means pursuit absorbs every overrun, which is precisely the failure the T0 post-mortem diagnosed. **When the week compresses, cut from step 6 backwards and never touch 0–2.**
- **A quiet week is a legitimate output.** "No moment, so no post; one target advanced; two ledger rows" is a good week. Manufacturing a post to fill the slot reproduces the documented 0.00%/0.16% failure mode and now also fails the methodology check.
- **This skill routes; it does not do.** If it starts growing scoring logic, parsing, or its own state format, that logic belongs in the owning skill. Keep it thin enough to read in one screen.
- **Never fabricate.** No ledger rows, no board states, no numbers, no "probably reached" claims. Empty is a finding.
- **Don't let it become the campaign review.** Weekly is operational; the five indicators and the tier progress are monthly, in [[career-campaign-review]]. Reporting indicators weekly at this n produces noise that looks like signal.
- **The Tue/Thu cron is the drafting engine, not this rhythm.** Scheduled runs produce drafts (or an honest "no moment" log line); this skill is where the week is actually decided. Expect Thursday to be empty often — that is the cadence working.
- **The strategy rests on an unverified inference.** The whole priority order follows from the contrast-candidate read of Company A, which is the user's own and not the panel's. If the panel answers otherwise, stop applying this order and re-read charter §9.1.
