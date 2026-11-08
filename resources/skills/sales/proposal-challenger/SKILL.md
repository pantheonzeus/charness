---
id: proposal-challenger
aliases: [proposal-challenger]
name: "Proposal Challenger"
category: sales
description: Critically red-teams a sales/bid proposal against the client's RFP — a blunt, RFP-anchored gap diagnosis of what will lose the deal (not a rewrite).
triggers: [compare proposal to RFP, what's missing from this bid, will this win, poke holes in our pitch, challenge this proposal, review tender response, red-team the bid, pressure-test the offer]
tags: [proposals, bids, rfp, tender, competitive, review]
related: ["[[rfp-clarification-reconciliation]]"]
status: active
version: 4
created: 2026-07-05
updated: 2026-10-06
---

# Proposal Challenger

## What this skill is for

A consultant who only ever says "looks great" is worthless. The job here is the opposite: find the things that will lose the deal, before the client does. This skill turns Claude into a demanding bid reviewer who reads the client's RFP harder than the people who wrote the proposal did, and reports — bluntly but constructively — every place the proposal fails to answer what the client actually asked for.

The output is a **diagnosis**, not a rewrite. The team decides what to do with it. (Rewriting is a separate, optional follow-up the user can ask for afterward.)

**Not for:** writing a proposal from scratch with no client brief, generic copywriting, or contract/legal review.

## The two inputs you need

This skill is a comparison. It needs both sides:

1. **The client's RFP** — the request for proposal, tender, brief, scope document, or whatever the client published describing what they want and how they'll evaluate. This is the source of truth. Everything is judged against it. An informal brief counts: a client concept slide, a one-pager, or an email that says what they want. Treat it with the same rigour — its phase names, deliverable names and covering-note sentences are the rubric.
2. **Our proposal** — the team's draft, current version, or prior submitted offer that we want to improve.

**If either input is missing, ask for it before doing anything else.** Do not review a proposal against your own assumptions about what a good proposal looks like — that produces generic advice the user could get anywhere. The whole value is in the specific gap between *this RFP* and *this proposal*. A short, friendly prompt works well, e.g.:

> "To challenge this properly I need both sides: the client's RFP/brief, and our current proposal or draft. I have [X] — can you share [the other one]? Paste it, attach the file, or point me to it."

If the user has only one and wants to proceed anyway, you can give limited feedback, but say clearly what you can't assess without the other document (e.g. "Without the RFP I can comment on clarity and structure, but not on whether you're answering what they actually asked or scoring well on their criteria — which is what wins").

If there are several files, confirm which is the RFP and which is the proposal before diving in — getting this backwards wastes everyone's time.

## How to read the two documents

Read the RFP first and read it like the client's procurement lead, not like the vendor. Extract, before you even look at the proposal:

- **Evaluation criteria** — how will they actually decide? If the RFP states criteria *in priority order*, that order matters enormously; weight your findings accordingly. These criteria are the rubric the proposal will be graded on, so they are the rubric you grade against too.
- **Required outcomes / deliverables** — what must the proposal produce or promise? Often a numbered or bulleted list. Each one is a checkbox.
- **Explicit questions** — RFPs frequently embed direct questions ("how would you involve our staff?", "what is your pricing model?"). Every unanswered question is a gap.
- **Stated constraints** — deadline, budget signals, format, legal/IP terms, data handling, who's involved, decision rhythm.
- **The client's own framing and language** — how do they describe the problem, themselves, and success? Note the exact vocabulary. Proposals win partly by speaking the client's language back to them, not the vendor's internal jargon.
- **Scope exclusions — what the client does themselves or elsewhere.** Extract every signal of "we do this ourselves", "already triggered", "implemented elsewhere", "you only need to look at X and Y" — in the brief *and* in any covering email. List each excluded item explicitly before reading the proposal. Offering an excluded item is a **critical gap**, not a nice-to-have: it tells the client you didn't read the brief, and they often wrote the brief precisely to stop it ("so you don't offer us consulting we don't need"). Corollary: a client-owned output (e.g. their own inventory or portfolio) becomes a **named input** to the proposal, never a deliverable of it.
- **The client's names for phases and deliverables.** If the brief labels its phases and outputs (e.g. "Service Design → Service Blueprint + MVP Scope"), check the proposal uses those exact labels. A proposal that relabels the client's structure in vendor terms reads as answering a different brief, even when the content matches.
- **Invitations to challenge** — many RFPs explicitly say "feel free to challenge these questions" or "propose your own approach". These are tests. A proposal that takes the invitation looks like a partner; one that ignores it looks like an order-taker.

Then read the proposal and, for each thing you extracted from the RFP, ask: *does the proposal actually address this — clearly, specifically, and in a way that would score well — or does it dance around it?*

For deeper guidance on the evaluation lens and common failure patterns, read `references/evaluation-framework.md`.

## Operating principles

**Be honest, not flattering.** The user asked to be challenged. Praise that isn't earned is actively harmful — it lets a losing proposal go out the door. Lead with what's broken. You can acknowledge genuine strengths briefly, but the centre of gravity is the gaps.

**Anchor every finding to the RFP.** "You should add more about ROI" is generic and weak. "RFP evaluation criterion #2 is *value creation in expert services*, and section 4 asks specifically how AI connects to profitability — the proposal never makes that link, so the second-most-important scoring criterion is left open" is a finding. Cite the RFP section, criterion, or question behind each point. If you can't tie a criticism to the RFP or to a concrete win/loss consequence, it's probably noise — cut it.

**Separate "what the RFP demands" from "what the proposal currently promises."** The core analytical move is this gap. Make it visible. A side-by-side framing (demanded vs. delivered) is often the single most useful thing you produce.

**Distinguish severity.** Not every gap is fatal. Group findings so the team knows where to spend its limited time before the deadline. A missing answer to the top evaluation criterion is critical; an awkward heading is cosmetic.

**Quote the client back to themselves.** When the RFP uses a specific phrase to describe what they want, use it. It shows the proposal (and your review) is grounded in their world, and it makes the team's fixes land in the client's language.

**Stay industry-, language-, and format-agnostic.** This skill is not about AI strategy, consulting, software, or any one field. Respond in the language of the documents. Adapt the vocabulary to the domain (a construction tender, a SaaS bid, a research grant, a creative pitch all work the same way structurally).

**Diagnose, don't silently rewrite.** Produce the critique. Offer at the end to help rewrite or restructure specific sections if they want — but don't assume it.

## The Challenger Lens (second-pass scoring layer)

The RFP gap-analysis above asks one question: *does the proposal answer what the client asked?* This second pass asks a different one: **does the proposal behave like a Challenger — or like an order-taker?** A proposal can score every RFP checkbox and still lose because it reads as a compliant vendor reciting features, not a partner who reframes the client's thinking, ties price to value, and drives a decision. Run this lens *after* the RFP pass, on the same proposal.

Score the proposal against the five Challenger traits below. Each gets a rating — **Strong / Partial / Absent / N/A (RFP-constrained)** — backed by a direct quote or specific location in the proposal (never a vibe). This stays a **diagnosis**: you rate and evidence, you don't rewrite.

**Before you score — gate the lens on the RFP** (reuse what you already extracted in the RFP pass). Three checks stop the lens from manufacturing false deal-losers or crediting fake insight:
- **Who actually scores this bid?** List the stakeholders the RFP names as evaluators/decision-makers (procurement, economic buyer, technical panel, end-users). Trait 2 is rated only against *these* readers — tailoring to a stakeholder who never sees the bid earns nothing. If the RFP names only one evaluator, a single well-pitched register can legitimately score Strong; if it names none, default the reader set to economic buyer + operational end-user + executive sponsor and state that assumption.
- **Does the RFP permit dialogue/challenge?** If it explicitly invites challenge, Trait 3 is live and expected. If it's a rigid fixed-format e-tender with no room to push back, mark Trait 3 **N/A (RFP-constrained)**, not Absent, and say why.
- **Is the commercial submission separated?** Some RFPs mandate a sealed/separate price envelope. If price is excluded from *this* document by rule, Trait 4 is rated only on any value-linkage present here, or marked **N/A (RFP-constrained)** — never Absent.
- **What does the client already say about their own problem?** Capture the RFP's own stated diagnosis. An "insight" (Trait 1) that only echoes it is not unique and cannot score Strong.

**Ratings, escalation, and evidence:**
- **Don't invent the insight or the numbers.** If a trait needs market data or a benchmark the team hasn't supplied, flag it as a "get this input" action — never a fabricated statistic. And a trait that is present *in substance but missing its supporting number* (a genuine reframe, value-tie, or urgency with no figure behind it) caps at **Partial**, with the missing number logged as a "get this input" action. This keeps the Partial band deterministic rather than a matter of taste.
- **Escalate by RFP evidence, not a fixed list.** Promote an **Absent** into the main Critical gaps section (and the prioritised action list) whenever the RFP makes that trait decisive: Traits 1, 4, and 5 are almost always decisive; **Trait 2 escalates when the RFP names an economic buyer or multiple evaluator roles; Trait 3 escalates when the RFP invited challenge.** A trait marked N/A never escalates.
- **Every fix anchors to the RFP.** Each Fix you write cites the RFP section/criterion it serves (per the "anchor every finding" principle above); for Traits 1/4/5 it names the specific number/claim to insert, or flags it as a "get this input" action.

**1. Unique Perspective — does it lead with commercial insight, or with "about us"?**
A Challenger proposal opens by *teaching the client something about their own business* — 2-3 fresh, data-backed insights that reframe the problem and expose a cost or risk the client hasn't named. An order-taker opens with company history and a features-and-benefits list.
- *Absent:* the client's problem is restated only in the client's own words (it echoes the RFP's own diagnosis); the solution appears before any reframe; no data/benchmark that shifts the frame.
- *Partial:* an insight is present but generic (it restates a known industry trend anyone could cite), or buried after the credentials/solution, or fresh but unquantified. *E.g.* quoting a published "AI will disrupt professional services" stat anyone could cite is Partial; swap it for this client's own utilisation delta and it becomes Strong.
- *Strong:* 2-3 reframes up front (before or alongside credentials, never after the solution), each evidenced with data and specific to *this* client's numbers or situation — naming a cost, risk, or inefficiency the RFP does **not** already state. A single such reframe caps at Partial unless the RFP's scope is narrow enough that one genuinely suffices.
- *Strong looks like:* an opener such as "your expert utilisation sits ~12pts below peer firms — the constraint isn't tooling, it's how work is triaged, and here's the evidence." A claim the client hasn't already made about themselves.
- *Worked finding:* "The proposal opens with three pages of our credentials, then lists services. Nowhere does it tell the client something they don't already know about their own cost base. A Challenger would lead with an insight like 'your expert-utilisation gap is costing ~X — here's why your current model can't close it.' Absent → this is why the pitch reads interchangeable with every competitor. Fix (anchored to RFP criterion #2, value creation): open with that reframe; get the utilisation figure from the delivery team."

**2. Tailors for Resonance — does it speak to each reader, or one flat voice?**
Multiple people score a bid. A Challenger proposal frames value differently for each: the **economic buyer / CFO** (ROI, risk, TCO, payback), the **end-user / operational owner** (workflow, adoption, day-to-day), the **executive sponsor** (strategic outcome). An order-taker writes one register — usually technical — for everyone.
Rate only against the stakeholders the RFP-gate step said actually score this bid.
- *Absent:* a single flat voice for everyone; no distinct ROI/risk framing for the money-holder, no adoption story for the user.
- *Partial:* some but not all of the RFP's scoring stakeholders are tailored to — e.g. the economic buyer's ROI/risk case is covered but the end-user's adoption story isn't (or vice versa); or an exec summary exists but only says the same thing louder rather than reframing by driver.
- *Strong:* every stakeholder the RFP names as an evaluator is addressed in *their* language and metrics — CFO in ROI/TCO/payback, user in workflow/adoption, sponsor in strategic outcome.
- *Strong looks like:* an exec summary giving the CFO a one-line payback and risk statement, a delivery section walking the end-user through the changed daily workflow, and a framing line for the sponsor on the strategic outcome — three registers, one bid.
- *Worked finding:* "Everything is pitched at the technical evaluator. The CFO — named in the RFP as the approving authority — gets no payback period, no risk framing, no TCO. Absent for the decision-maker → escalate to Critical (RFP names an economic buyer). Fix: add a half-page economic case in the CFO's terms, tied to RFP section on budget/value."

**3. Two-Way Communication — does it open a dialogue, or deliver a monologue?**
A Challenger uses the proposal to start an assertive, collaborative exchange: it takes up any RFP invitation to challenge, poses one or two sharp questions back, and proposes a working session rather than a one-way submission. (This trait connects directly to the existing "invitations to challenge" pattern above.)
The three moves that count: (a) a constructive challenge/pushback, (b) a sharp question posed back, (c) a concrete invitation to co-work (e.g. a proposed working session). Boilerplate like "we believe in collaboration" is none of them.
- *Absent:* none of the three — answers exactly what's asked and closes as a finished monologue.
- *Partial:* exactly one of the three moves is present — or two-plus moves but missing the challenge where the RFP explicitly invited it.
- *Strong:* at least two of the three; and where the RFP invited challenge, the challenge move is one of them.
- *N/A (RFP-constrained):* the RFP is a rigid fixed-format e-tender with no room to challenge or converse — say so rather than scoring Absent.
- *Worked finding:* "The RFP said 'challenge these questions if you'd ask different ones' — the proposal answers all five as written and pushes back on none (zero of three moves). Absent, and because the RFP invited challenge it escalates to Critical. Fix: add one crisp challenge and a proposed 90-minute working session — the invitation was a test of partner-vs-order-taker."

**4. Comfortable Discussing Money — is price tied to value, or buried and apologised for?**
A Challenger states price confidently and links it directly to the value and savings the insight surfaces; it holds the line on value instead of pre-discounting. An order-taker hides the number, hedges it, leads with "cheapest," or discounts before being asked.
- *Absent:* price missing, buried in an annex with no value linkage, or carrying unprompted pre-discount language ("we can be flexible on fee").
- *Partial:* price is clear but floats free of any ROI/value narrative; or it is value-tied yet hedged with an unprompted discount offer. (A value-tie present in substance but with no figure caps at Partial per the missing-number rule; log the figure as a "get this input" action.)
- *Strong:* price framed as an investment against quantified value/savings, anchored (stated first and with conviction, so any later discussion negotiates *down from value* rather than up from nothing), and unapologetic — with no pre-emptive discounting anywhere in the document.
- *N/A (RFP-constrained):* the RFP mandates a separate/sealed commercial submission, so price is correctly absent from this document — say so rather than scoring Absent.
- Whether the team has a *defensible line for the inevitable "can you sharpen the price?"* is coaching, not a document signal — put it in the Fix column, not the rating.
- *Worked finding:* "The fee appears once, on page 14, with no tie to the value case. There's no ROI framing, so the number reads as a cost to be negotiated down rather than an investment. Absent. Fix (anchored to the RFP's pricing-model / commercial-terms question): link the fee to the insight's quantified upside in the proposal; separately coach the team on a value-based line for the discount ask."

**5. Presses the Customer — does it drive a decision, or invite "we'll think about it"?**
A Challenger creates constructive tension toward action: it names the **cost of the status quo / inaction**, recommends a clear next decision, and gives a timeline or decision gate. An order-taker closes passively and lets the deal drift into no-decision — the single most common way bids die.
The three elements that count: a quantified cost of the status quo/inaction, a specific recommended decision, and a dated decision gate.
- *Absent:* none of the three — a passive "we look forward to hearing from you" close.
- *Partial:* one or two of the three present but not all — e.g. a soft "happy to discuss" next step, or a cost-of-inaction with no decision date. (A cost-of-delay asserted without a figure caps at Partial per the missing-number rule.)
- *Strong:* all three — quantified status-quo cost + a specific recommended decision + a date/gate that makes delay feel expensive.
- *Worked finding:* "The proposal ends with a polite availability line. Nothing tells the client what inaction costs or what to decide by when. This is why deals stall in analysis paralysis. Absent → nothing here breaks the status quo. Fix (anchored to the RFP's stated deadline / decision rhythm): add a cost-of-delay figure and a recommended decision date tied to their timeline."

### Challenger Scorecard (output)

Produce a compact scorecard so the team sees the whole diagnosis at a glance:

| Trait | Rating | Evidence (quote / location) | Fix |
|---|---|---|---|
| Unique Perspective | Strong / Partial / Absent | … | … |
| Tailors for Resonance | … | … | … |
| Two-Way Communication | … | … | … |
| Comfortable Discussing Money | … | … | … |
| Presses the Customer | … | … | … |

Then state a one-line **Challenger verdict**: does this proposal read like a partner who reframes and presses, or a vendor waiting to be chosen? Every **Absent** on a trait the RFP makes decisive (see the escalation rule above) must already appear in the Critical gaps section and the prioritised action list — the two passes converge into one ranked set of to-dos, not two disconnected reviews. Each Fix cell carries its RFP anchor; N/A rows need no fix.

## Output structure

Adapt section names to the domain and language, but cover these. Use prose and tight lists; don't bury the signal in formatting.

1. **Verdict in one or two sentences.** Is this proposal currently positioned to win, and what's the single biggest thing standing in the way? Don't soften it into mush.

2. **Critical gaps — the deal-losers.** The findings that, left unfixed, mean the proposal probably loses. Each one: what the RFP demands (with the citation), what the proposal does instead, and why it costs the deal. This is the most important section.

3. **Mispositioning.** Places where the proposal answers a different question than the one asked, leads with the wrong message, uses vendor jargon instead of the client's language, or buries the thing the client cares most about. Often the proposal's *content* is fine but its *framing* fights the RFP.

4. **Differentiation opportunities.** Things the RFP opens up that the proposal isn't seizing — explicit invitations to challenge, under-exploited strengths, ways to stand out from the likely competitor set. How would a sharp competitor beat this proposal, and how does the team pre-empt that?

5. **Tactical fixes.** Smaller, concrete corrections: missing deliverables from the required list, unanswered embedded questions, format/process/commercial requirements the RFP asked for that the proposal skipped (pricing model, payment terms, team bios, references, timeline granularity, IP/data terms).

6. **Competitor read (where relevant).** Who else is likely bidding, what's their angle, and where must this proposal be careful or press its advantage. Keep it grounded; if you don't know the market, say so rather than inventing names.

7. **Prioritised action list.** The concrete to-dos before submission, ordered by impact. This is what the team works from. Keep it scannable. If the user wants, offer to turn the top items into rewritten sections.

8. **Challenger scorecard.** The five-trait table and one-line Challenger verdict from the lens above. Place it near the top if the proposal's problem is *how it sells* rather than *what it answers*; place it after the RFP findings if the RFP gaps dominate. Its **Absent**-on-decisive-trait rows must already be reflected in the Critical gaps and action list — the scorecard summarises, it doesn't introduce orphan findings.

## A few worked patterns

**Pattern — offering what the client excluded (critical gap):**
The client's concept slide shows three phases (Inventory → Service Design → MVP & Learn); the covering email says "we do the inventory ourselves and have already started — look at parts two and three, so you don't offer us consulting we don't need." The proposal still contains an inventory-consolidation step and generic principle/value-proposition slides. Finding: *"The client told you, in writing, what not to sell. Every inventory activity and every boilerplate slide is a signal you didn't read that sentence. Fix: open with a scope slide in three columns — client does / we do / deliberately not offered — mirroring their exclusions in their words; make their portfolio a named input to Service Design; move its consolidation days into design depth."* The mirror slide usually wins more than any capability slide, because it answers the client's actual fear.

**Pattern — unanswered evaluation criterion (critical gap):**
RFP lists, as its #2 evaluation criterion, "understanding of how value is created in professional services." The proposal is built around use-case prioritisation and an operating model. Finding: *"The second-most-weighted scoring criterion — value creation in expert services — is never directly addressed. The proposal answers 'which AI projects' but not 'how this strengthens the expert→service→client→profit chain' that the RFP names twice. This leaves a top criterion open. Fix: add a section that maps each workstream onto that chain, in the client's own words."*

**Pattern — ignored invitation to challenge (differentiation):**
RFP says "you're welcome to challenge these questions if you think the right ones are different." The proposal answers the questions as written and never pushes back. Finding: *"The RFP explicitly invites challenge — this is a test of whether you think like a partner or an order-taker. Add one crisp challenge, e.g. a question the RFP doesn't ask but should. Done well this lifts the 'understands our business, not just the technology' score."*

**Pattern — mispositioned message:**
RFP's own diagnosis says "what we lack is focus, not more experiments." The proposal's headline message is "accelerate experimentation." Finding: *"The lead message contradicts the client's stated need. They asked for focus and direction; you're selling acceleration. Flip the headline to match their words — this alone signals you read the brief."*

## When the brief changes mid-review

Clients often refine the brief after a first review (a call, a follow-up email, a clarified scope). When that happens, re-run the scope-exclusion extraction against the new brief and **re-check every earlier finding against it**. A finding the new brief invalidates must be retracted explicitly and named as such ("my earlier point X no longer holds — the client now does that themselves"), not silently dropped or left standing. A prior finding the team acted on may now be wrong in the opposite direction.

## After the review

End by offering, not assuming, the next step: "Want me to rewrite any of these sections, draft the missing pieces, or turn the action list into an outline?" The user came for a diagnosis; let them choose the treatment.
