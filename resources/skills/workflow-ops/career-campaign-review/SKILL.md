---
id: career-campaign-review
aliases: [career-campaign-review]
name: "Career Campaign Review — the Seat Funnel, Monthly"
category: workflow-ops
description: Monthly roll-up of the Ladder Campaign's five leading indicators across all three funnels — content, pursuit, closed rooms — against the charter's success tiers. The only place the *seat* funnel is measured; the weekly LinkedIn review measures only the content funnel. Reads the contact ledger, target list and qualify-out log, reports entered-vs-qualified-out honestly, and revisits the charter's own falsification list.
triggers: [campaign review, monthly campaign review, how is the job search going, seat funnel, am i making progress, career campaign, ladder campaign, contact ledger, qualify out, target list review, pursuit review, monthly review job search]
tags: [workflow-ops, career, campaign, pursuit, measurement, monthly-review, job-search]
related: ["[[linkedin-weekly-review]]", "[[pursuit-deal-tracking]]", "[[linkedin-authentic-storytelling]]", "[[account-priority-map]]", "[[speaker-submission]]"]
references: ["../../content/linkedin-authentic-storytelling/references/ladder-joints.md"]
modules: [file-backed-state, evidence-backed-answering]
requires:
  cli: [python3]
environment: "Local terminal with vault access. Reads plain text/TSV under output/campaign/; no external services. Runs fine with Google Workspace MCP unauthorized — calendar-sourced items are then entered by hand."
status: active
version: 1
created: 2026-08-22
updated: 2026-08-22
vault_writes: ["cbrain/projects/ladder-campaign.md", "cbrain/projects/career-manufacturing-cto-positioning.md", "cbrain/Clients/*"]
---

# Career Campaign Review — the Seat Funnel, Monthly

*The Ladder Campaign's instrument. [[linkedin-weekly-review]] answers "how did the content do"; this answers **"am I closer to the seat"** — which is a different question with different data, and until 2026-08-22 nothing measured it.*

**Contract**
- **Input:** `output/campaign/contact-ledger.tsv`, `target-list.md`, `qualify-out-log.md`, the month's weekly LinkedIn reviews, and the charter (`output/20260822-ladder-campaign-charter.md`).
- **Output:** `output/campaign/review-<YYYY-MM>.md` — the five indicators with sources, progress against the three success tiers, and the month's single decision.
- **Allowed tools/artifacts:** read the campaign files and the vault; write the review; update `pursuit_stage` on `Clients/` notes via [[pursuit-deal-tracking]].
- **Done when:** all five indicators are reported **with their source**, the entered-vs-qualified-out count is stated, the charter's falsification list has been revisited, and exactly one decision is named for next month.

**Triggers/Context**
- Monthly, on demand: "campaign review", "how is the search going", "monthly review".
- Also whenever a **tier boundary** is crossed — a process reaches final round, an offer arrives, or the month-9 floor date approaches.
- **Not for:** weekly content performance ([[linkedin-weekly-review]]) · scoring a draft ([[linkedin-viral-scheduler]]) · tracking one named pursuit ([[pursuit-deal-tracking]], which this skill reads rather than replaces).

**Core Blueprint**

### 0. Load the charter, not your memory of it
- Read `output/20260822-ladder-campaign-charter.md` — north star, three tiers, five indicators, anti-goals, falsification list. The charter is the standard; this review does not invent its own.
- Create STATE_ROOT `output/.runs/<YYYYMM>-campaign-review/` with `RESPONSE.md` (CP0–CP4) and `EVIDENCE.md`.

### 1. The five indicators (CP1) — each with its source or it doesn't ship
1. **Ledger actions by named people** — count from `contact-ledger.tsv`, split inbound vs. outbound, content-attributed vs. not, and by target class. Report the **named** people, not just the count: this is a small-n instrument and the names are the signal.
2. **Qualifying-state targets** — of the 12, how many carry cited board-state evidence, and how many have a written joint diagnosis.
3. **Processes entered vs. qualified out** — both counts from `qualify-out-log.md`. **A rising qualified-out count is reported as progress**, with the reason for each decline. Zero qualified-out in a month with live opportunities is a finding, not a neutral fact.
4. **Closed-room count** — rooms entered, headcount, and how many attendees own a P&L. Not audience size.
5. **Loop integrity** — % of the month's published posts with a note and an export inside 72h, carried from the weekly reviews. **If it is below 100%, say so before anything else** and mark that month's content conclusions as partial.

### 2. Tier progress (CP2)
State plainly where the campaign sits against Floor / Target / Ceiling, with the date each is due. For the Floor, count only processes that **passed the qualify-out test before being entered** — front-door processes reaching final round do not count toward it, by design.

### 3. Supporting evidence, clearly subordinate (CP3)
Decision-maker density (vs. the 32.0% high-water mark), Buyer/Recruiter/Reach axes, buyer-weighted engagement, post-outcome pairs. One short block. **Never lead with these** — they are proxies, and the charter demoted them on purpose.

### 4. Revisit the falsification list (CP4)
Walk charter §9 explicitly:
1. Has the panel answered on Company A? If the answer contradicts the contrast-candidate read, **say that the campaign's priority order is now in question** — do not quietly carry on.
2. German dialect test — any density lift?
3. Twelve-month ledger trend — is named-executive engagement growing?
4. Create-the-role motion — any live conversation yet?

### 5. One decision (CP5)
End with **exactly one** decision for next month — a reallocation, a target added or dropped, a motion changed, a hypothesis retired. Not a list of five intentions. Then the evidence gate: every number traces to a file and a field in `EVIDENCE.md`.

### 6. Knowledge graph + self-learning
- Link the review into `[[ladder-campaign]]` and `[[career-manufacturing-cto-positioning]]`; update `pursuit_stage` on any `Clients/` note whose stage moved (Charter §6).
- End with the standard Feedback & Skill-Verification block (Charter §7).

**Optimizations/Gotchas**
- **Names beat counts at this n.** "Four ledger actions" is nearly meaningless; "an operating partner at a portfolio company replied and took a call" is the whole month's signal. Report both, lead with the names.
- **Qualified-out is not inaction.** The instinct is to read a declined process as a month wasted. The Company A post-mortem is the argument otherwise: entering an unwinnable process cost weeks of preparation and produced one data point. Say the count out loud so the discipline stays visible.
- **Never substitute LinkedIn analytics for campaign progress.** A good content month with no ledger movement is a good content month, not progress toward the seat. Conflating the two is the exact failure this skill exists to prevent.
- **Small n, stated every time.** One month is not a trend. Report the count of months alongside every direction claim.
- **A missing panel answer is a standing open item**, not a closed one. It stays at the top of the review until it resolves — the entire priority order rests on an inference until then.
- **This skill does not create pursuits or do research.** It reads what the pursuit and research skills produced. If a target has no diagnosis, that is a reported gap, not something to fix inside the review.
