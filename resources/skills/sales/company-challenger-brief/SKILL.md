---
id: company-challenger-brief
aliases: [company-challenger-brief]
name: "Company & Market Meeting Brief (Challenger)"
category: sales
description: Research a company (vision, mission, core numbers) and its industry from website + news, then build a Challenger-method commercial insight so you walk into a meeting as a value-adding peer.
triggers: [research this company, prep for a meeting with, company brief, what do they do, meeting prep, know enough for a meeting, market research, industry landscape, challenger insight, before I meet]
tags: [sales, meeting-prep, company-research, competitive-intelligence, challenger-sales, industry]
related: ["[[audience-of-one-report]]", "[[proposal-challenger]]", "[[competitive-porter-teardown]]", "[[account-priority-map]]", "[[executive-dialogue-planner]]"]
requires:
  tools: [web_search, web_fetch]
status: active
version: 2
created: 2026-07-06
updated: 2026-10-01
vault_writes: ["cbrain/Clients/*", "cbrain/projects/*"]
---

# Company & Market Meeting Brief (Challenger)

## What this skill is for

You have a meeting with someone at a company you don't yet know well, and you want to walk in as a *peer who adds value* — not a vendor who read the About page an hour ago. This skill researches the **company** (vision, mission, what they actually do, core numbers), maps its **industry** to the depth a good conversation needs, and then does the thing that separates a memorable meeting from a forgettable one: it builds a **Challenger-method commercial insight** — a defensible, data-backed reframe that teaches them something about their own business they under-appreciate, and points toward where you can help.

The output is a **concise, cited meeting brief** saved to `output/`. You should be able to read it in five minutes and hold your own for an hour.

**Not for:** deep psychological profiling of the individual you're meeting (→ `[[audience-of-one-report]]`, which is person-centric and produces a branded PDF), red-teaming an existing bid against an RFP (→ `[[proposal-challenger]]`), a full strategic teardown with multi-business-unit fan-out and a Porter 5 Forces structure (→ `[[competitive-porter-teardown]]`, for when the ask is a goal-driven strategy dossier, not a meeting brief), or a durable Mission→Strategy→Initiative→Project account tree (→ `[[account-priority-map]]`, which this brief's research feeds). This skill is company + market + insight, with only a *light* read on the person.

## The input you need

At minimum: **the company** (name or, better, website URL). Ideally also **who you're meeting** (name + role) and the **meeting context** (why you're talking, what you want out of it). More context sharpens the Challenger insight — a generic company brief is a commodity; a brief aimed at *this person's mandate and this meeting's goal* is not.

If any of that is missing, ask before researching — a short prompt works:

> "To prep this properly, tell me: (1) the company — name or website; (2) who you're meeting and their role, if you know; (3) what the meeting is about and what you want out of it. I can run on just the company name, but the sharper insight comes from knowing the person and the goal."

If the user only has the company, proceed — but flag that the Challenger insight will be aimed at the company's likely priorities rather than a specific person's mandate.

## Sources — website and news are primary

Research in this order, and **cite every non-obvious claim** (Academic Rigor rule — source name + link, or an Obsidian callout in vault notes):

1. **Official website** — the source of truth for what *they* say they are. Hit: `/about`, `/mission` or `/vision`, `/products` or `/solutions`, `/customers`, and the `/investors` or `/press` / `/newsroom` pages. This is where vision, mission, positioning, and self-described strategy live.
2. **Recent news articles** — the source of truth for what they're *actually doing*. Search the last 6–12 months: funding, launches, M&A, leadership changes, earnings, layoffs, partnerships, regulatory run-ins. News is where the narrative-vs-reality gap shows up — and that gap is often the insight.
3. **Financials / filings** — annual reports, investor decks, 10-K/press releases (public co.), Crunchbase/PitchBook-style summaries (private). This is where the core numbers come from.
4. **Industry & competitor sources** — analyst notes, market-size reports, trade press, and the top competitors' own sites. Enough to place this company in its market, not a full sector study.

**Flag public vs. estimated.** A revenue figure from a 10-K is a fact; a third-party estimate for a private company is a bet — label it as such (Soul.md: never dress a guess as a fact).

## What to extract

Three buckets. Keep each tight — you're building a brief, not a dossier.

**Company**
- Vision & mission — in their own words (quote them).
- What they sell and to whom — the business model in one or two lines.
- **Core numbers** — revenue and growth, headcount, funding/valuation or market cap, margins (if public), key markets/geographies, customer count or logos. Get the 3–5 that matter; skip the vanity metrics.
- Recent moves — the last 12 months of news that a peer would know about (launches, M&A, leadership, earnings, layoffs).
- Stated strategic priorities — what leadership says they're betting on.

**Industry (to the depth the conversation needs)**
- Market size & growth trajectory.
- The 2–3 forces reshaping it — technology shifts, disruption, regulation, cost/margin pressure.
- Top competitors and how they're positioned.
- Where *this* company sits: leader, challenger, laggard, niche.

**Person (light)**
- Role, mandate, and the pressures someone in that seat likely feels this year.
- 2–3 talking hooks — recent posts, quotes, or moves you could open on.
- For anything deeper, hand off to `[[audience-of-one-report]]`.

## The Challenger layer

This is the point of the skill. Research alone makes you *informed*; the Challenger reframe makes you *valuable*. The method is **Teach → Tailor → Take Control**:

- **Teach** — lead with a commercial insight about *their* business they haven't fully priced in. Not a fact they already know, not a generic industry truism ("AI is changing everything") — a specific cost, risk, or missed opportunity, backed by data, that reframes how they see their situation.
- **Tailor** — aim it at this person's mandate and this company's numbers. A CFO hears payback and risk; an operations lead hears throughput and adoption; a CEO hears strategic exposure.
- **Take Control** — carry the insight toward a decision. Name the cost of standing still, and where the help lives — without pitching prematurely.

Build the insight along the classic reframe arc, and put the working version in the brief:

1. **Warm-up** — show you understand their world (a sharp, non-obvious observation about their business).
2. **Reframe** — "the real issue isn't X, it's Y." The pivot that surprises them.
3. **Rational drowning** — the data that makes Y undeniable (this is where the core numbers and industry trends earn their keep).
4. **Emotional impact** — make it *their* problem: "this is likely showing up as ___ in your business."
5. **A new way** — the better approach, described as a category, not your product.
6. **Where value lives** — where you specifically can help. Stated as a hypothesis, not a pitch.

Produce **1–2 defensible insights** — each with the reframe, the supporting data (cited), and **one opening question** that would surface it naturally in conversation. The bar: a smart person from the target company should hear it and think *"huh, I hadn't framed it that way"* — not *"tell me something I don't know."* If you can't support the reframe with data, it's a gimmick — cut it and say what input you'd need to make it real.

## Output structure

Save a markdown brief to `output/` (filename like `YYYYMMDD-<Company>-meeting-brief.md`). Lead with the TL;DR per the Communication Architecture; keep the whole thing scannable.

1. **Executive TL;DR** — 3–4 bolded bullets: what this company is, the one number that matters, and the single Challenger insight you'll open with. A busy reader gets the meeting in 15 seconds.
2. **Company snapshot** — vision/mission (quoted), what they sell, business model, recent moves.
3. **Core numbers** — the 3–5 that matter, each cited, public-vs-estimate flagged.
4. **Industry landscape** — market size/growth, the reshaping forces, competitors, where this company sits.
5. **Challenger insight(s) & reframe** — the 1–2 insights with the reframe arc, cited data, and opening question(s). *This is the centre of gravity.*
6. **Who you're meeting** — role, likely priorities, 2–3 talking hooks (light; defer depth to `[[audience-of-one-report]]`).
7. **Smart questions to ask** — 4–6 questions that make you look like a peer and surface where you can help.
8. **Sources** — every source used, linked.

## Operating principles

- **Business → Product → Technology.** Lead with the commercial outcome, not the tech stack. The insight is about *their business*, not architecture.
- **Name your confidence.** A filed number is a fact; an estimate is a bet with its risk stated. Never blur the two (Soul.md).
- **Density over volume.** Crisp bullets over paragraphs. If the brief runs long, cut — the value is in what you can act on, not what you gathered.
- **Don't oversell.** The "where value lives" line is a hypothesis, not a pitch. A meeting won on a hollow insight is lost on the follow-up.
- **Skip vanity metrics.** If a number doesn't tie to a decision or a dollar, it doesn't go in the brief.

## Gotchas / Optimizations

- **Verify numbers against a primary source.** News articles recycle each other's errors; trace a figure back to the filing or the company's own statement before you stake an insight on it.
- **Check recency.** A "current" headcount or revenue figure can be two years stale. Date every number.
- **Private companies = estimates.** Label them as bets, give the range, name the source. Don't manufacture precision.
- **Keep the insight defensible, not clever.** The failure mode is a reframe that sounds smart but collapses under one informed follow-up question. Pressure-test it: could the person you're meeting refute it in one sentence? If yes, it's not ready.
- **Wire it into the vault.** Create/update the company note and the person's contact note, link them bi-directionally, and connect to any relevant topic/anchor note (Living Knowledge Graph rule). A meeting-prepped company is a node, not a throwaway.

## After the brief

End by offering the next step, not assuming it: "Want me to go deeper on the person (audience-of-one brief), structure this into an account priority map, build a dialogue plan for the meeting, or turn the smart questions into a discovery flow?"

**Feedback & Skill Verification**
- Would you like to provide feedback to optimize this workflow or execution?
- Should we update this skill (or add a new one) based on how this went?
