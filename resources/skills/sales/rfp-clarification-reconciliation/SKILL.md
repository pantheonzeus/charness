---
id: rfp-clarification-reconciliation
aliases: [rfp-clarification-reconciliation]
name: "RFP Clarification Reconciliation — Client Answers vs. Drafted Bid"
category: sales
description: When the client answers the bidder clarification round after your bid answers were already drafted on named assumptions, reconcile every answer against every draft — confirms / contradicts / new obligation / deferred — and turn it into a superseded premise, a gate-register delta and a prioritised follow-up list.
triggers: [rückfragen beantwortet, antworten des auftraggebers, abgleich rückfragen, bieterfragen beantwortet, client answered our questions, bidder questions answered, clarification answers, clarification round, Q&A round, answers to our RFP questions, does this change our bid, the client replied to our questions, das hat der kunde geantwortet]
tags: [sales, rfp, bid, tender, reconciliation, assumptions, compliance]
related: ["[[proposal-challenger]]", "[[pursuit-deal-tracking]]", "[[company-challenger-brief]]", "[[deliverable-index]]"]
modules: [file-backed-state, evidence-backed-answering]
status: active
version: 1
created: 2026-09-16
updated: 2026-09-16
vault_writes: ["cbrain/Clients/*", "cbrain/projects/*"]
---

# RFP Clarification Reconciliation — Client Answers vs. Drafted Bid

## Contract
- **Input:** the client's written answers to the bidder clarification round — **as the source file** (xlsx / docx / pdf), never a screenshot — plus a live pursuit run whose drafted answers already exist under a `STATE_ROOT` (`output/.runs/<YYYYMMDD-slug>/`).
- **Output:** `output/<YYYYMMDD>-<client>-rueckfragen-abgleich.md` (or `-clarification-reconciliation.md`), carrying: a superseded-premise statement, the hard contradictions with both sides quoted, the structural tensions, an answer-by-answer classification table, a gate-register delta, a prioritised follow-up list, and the "what is not coming before submission" table. Plus: the run's `RESPONSE.md` premise block visibly superseded, and the pursuit's vault anchors extended.
- **Allowed tools/artifacts:** reads of the source file and the run state, writes to the reconciliation deliverable, the control spine, and the vault. **Not allowed in this pass:** rewriting the drafted bid answers, and any contact with the client.
- **Done when:** every client answer carries at least one classification and names the affected draft IDs; every claimed contradiction quotes the client's wording *and* the draft's wording; the control spine's superseded premise is struck in writing rather than deleted; and every deferred item is mapped to the bid's assumptions register.

**Triggers/Context**
- The client answers the clarification round **after** drafting started — the normal case, and the one that silently invalidates work. Also fires when answers arrive after your own run recorded the window as closed.
- An addendum, a Q&A appendix, or a "clarifications" sheet is issued to all bidders mid-drafting.
- Explicit ask: *"das hat der Kunde geantwortet"*, *"does this change our bid?"*, *"reconcile these answers"*.
- **Not for** a first read of an RFP with no drafts yet (that is ordinary bid work), and not for a red-team of a finished proposal (`[[proposal-challenger]]`).

## Core Blueprint

1. **Demand the source file. Never reconcile from an image.**
   A screenshot of a dense Q&A table is not a source of record — small rendered text cannot be quoted safely into a bid, and a bid is exactly where a 90%-legible quote becomes a fabricated claim. Say so plainly, ask for the file, and do the parts that don't depend on the text (theme-to-draft mapping) while waiting. Extract the file to text in the scratchpad and work from that.

2. **Read every sheet, tab and annex — not just the answer table.**
   Clarification packs routinely carry a **second sheet listing what you will *not* get before submission** and when it will arrive instead. That sheet is often more decision-relevant than the answers: it converts open questions into forced assumptions. Extract it in full.

3. **Find the premise the drafts were built on, and supersede it in writing.**
   Open the run's `RESPONSE.md`. Drafts written during a closed clarification window carry a standing assumption ("no further clarification is coming; every answer must stand on named assumptions"). When answers arrive, **strike that premise visibly in the spine — never delete it.** Everything downstream was written under it, and a silently removed premise makes the drafts unreadable to anyone auditing them later.

4. **Classify every answer into one or more of four buckets. Leave none unclassified.**
   | Mark | Meaning | What it obliges |
   |---|---|---|
   | ✅ **confirms** | The client states as their own position what a draft argued | Quote it back — your argument is now their requirement |
   | ⛔ **contradicts** | A draft says something the answer rules out | Hard rework; list under the contradictions section |
   | ➕ **new obligation** | A demand with no counterpart anywhere in the drafts | New scope, new price line, or a new annex |
   | 🔒 **deferred** | Answered with "you get that at shortlist / project start" | An assumption, not a wait — see step 7 |

5. **Verify before asserting a contradiction — quote both sides.**
   Never claim a draft is contradicted from memory of what the draft says. Open the fragment, grep the relevant clause, and put the client's wording and the draft's wording next to each other in the deliverable. A contradiction asserted without both quotes is the evidence-gate failure this skill exists to prevent (`_shared/evidence-gate.md`). Where the answer only half-lands, write **partial** — a partial answer is not an answer.

6. **Run the gate-register delta.**
   For every open gate in the run: closed · partially moved · still open. Record the answer number that closed it.

7. **"You'll get it after the deadline" closes the gate — as an assumption, not as a wait.**
   The most costly misreading in this whole procedure is treating a deferred answer as still pending. If the client says the data arrives at shortlisting or project start and the bid is due before that, the gate is **answered**: the answer is *decide it yourself and name the assumption*. Any deliverable blocked on that input must now be unblocked with a stated assumption plus an option path. Write that as an explicit instruction in the follow-up list, because the default behaviour is to keep waiting.

8. **Name the structural tensions in the client's own answers.**
   Look for pairs where one answer makes something mandatory and another withholds what it depends on, or puts its remedy outside the priced scope. These are real and they are priced risk. Put them in the bid as **named assumptions with an option path** — never as a silent caveat, never as a complaint. Two recurring shapes:
   - *Mandatory function, unavailable input:* feature X is launch-critical, the survey that sizes it arrives after award, and the fix for a bad result is out of scope.
   - *Mandatory scope, unavailable specification:* deliverable Y is a must-have, its specification is released only to the shortlist. The counterweight is usually a **right to refine** granted elsewhere in the same pack — find it and invoke it explicitly in the first offer.

9. **Sweep for money in both directions.** Two checks, both easy to miss because nothing in the drafts looks wrong:
   - **Work the client just took back in-house** — if an answer says they will build or operate something themselves, any draft pricing it is now over-priced against the competition. Grep the fragments for it.
   - **Work the client just handed you** that appears in no draft — a proposal they now expect, a mechanism they ask you to design, a proof they want evidenced. These arrive as ordinary prose inside a long answer and are the most-missed category.

10. **Extract literal compliance mechanics verbatim.**
    Answers often contain pass/fail mechanics stated in passing: exact cell coordinates, how many copies of a form, which value goes where, what wording a zero-value carries. Transcribe them literally into the follow-up list. These cost nothing to satisfy and everything to miss.

11. **Write the deliverable, then the spine, then the vault.**
    Deliverable to `output/` per Charter §4. Superseded-premise block plus the prioritised follow-up list into `RESPONSE.md`. Then the pursuit's vault anchors (`[[pursuit-deal-tracking]]`): the account note, the project/topic note, and the client contact's note — an answer pack usually confirms or corrects something about *who decides what* on the client side, which belongs on the person note. Run the deliverable indexer last.

12. **Prioritise the follow-up list by what disqualifies, not by what is biggest.**
    Order: (1) KO / pass-fail criteria, (2) contradictions that would read as non-compliance, (3) mechanics of the mandatory forms, (4) new obligations with no draft, (5) everything else. A scoring-point improvement below a failed KO criterion is worth nothing.

13. **Stop before rewriting the drafts.** Classification and rewriting are different jobs with different risk. Hand over the follow-up list and let the principal choose what gets pulled — drafts often carry deliberate positions that a well-meaning rewrite would flatten.

## Optimizations/Gotchas
- **Confirmations are not filler — they are the strongest material in the bid.** When the client states your architectural argument as their own requirement, that sentence is quotable back at them and it neutralises a competitor who assumed otherwise. Give confirmations their own section; do not bury them under the contradictions.
- **An answer can settle an open question against you.** The instinct is to keep presenting it as a live choice with a preferred branch. Resist it: once decided, the draft must carry the decision and price its consequences, or the bid reads as not having read the answers.
- **Watch the ones that quietly narrow scope.** When the client says "no further differences are defined" about something a draft argued for richly, that draft is not wrong — but it must be relabelled as *proposal*, not *requirement*, or the bid invents scope and gets marked for it.
- **Answers that arrive after your own recorded deadline are the whole point of this skill.** A run that recorded "the window is closed" will not go looking. The reconciliation must therefore start from the source file the principal hands over, never from the run's own belief about what is possible.
- **Deadline arithmetic beats stage labels.** A staged plan that reads sensibly ("stage 2: Q2–Q3, stage 3: Q4 and later") can still fall past a hard contractual cut-off. Convert every stage label to a date and compare it to the binding date before declaring the staging sound.
- **Do not reconcile against the built `.docx` files — reconcile against the run fragments.** The fragments are the working copies with the checklists and the open-gate annotations; the documents are their render.
- **Budget:** one pass over the answer pack, one targeted grep per suspected contradiction. If a suspected contradiction cannot be confirmed by opening the draft in two greps, record it as *unverified, needs a read* rather than asserting it.

**Worked example:** Client C, RFP for four native member apps (16.09.2026) — 24 answers issued 14.09. after the run had recorded the clarification window as closed on 13.09. and built ~60 drafts on named assumptions. Result: 4 hard contradictions (a staging plan whose stages 2 and 3 fell past the binding shut-off date; a pricing-sheet mechanism replaced by two separate copies of the sheet with specified zero-value cells; an open store-migration question decided against the favourable branch; a conditional caveat on a now-unconditional MVP function), 2 structural tensions, 11 gates closed — one of them by *"you get the data at project start"*, which unblocked a mandatory annex that had been waiting for it — 14 prioritised follow-ups led by a KO criterion on group-company staffing, and 11 documents confirmed as not arriving before submission. Deliverable: `output/20260916-client-c-rueckfragen-abgleich.md`.

**Feedback & Skill Verification**
- Would you like to provide feedback to optimize this workflow or execution?
- Should we update this skill (or add a new one) based on how this went?
