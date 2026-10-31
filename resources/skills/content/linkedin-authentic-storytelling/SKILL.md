---
id: linkedin-authentic-storytelling
aliases: [linkedin-authentic-storytelling]
name: "LinkedIn Authentic Storytelling → SSI Boost"
category: content
description: Write LinkedIn posts aimed at a defined ICP (European Group CTOs / CTOs / NEDs / Board Members) to advance a dual goal — peer authority and board/NED positioning — turning a real moment into a scroll-stopping post in an executive-vulnerability voice (hook, arc, formatting, photo); SSI is a lagging indicator, not the point. Also audits existing posts and harvests/logs ideas from the vault.
triggers: [linkedin post, write a linkedin post, linkedin, ssi, social selling index, authentic storytelling, personal brand, linkedin hook, post idea, content audit, boost engagement, target audience, reach CTOs, board positioning, NED, thought leadership]
tags: [content, linkedin, storytelling, personal-brand, ssi, social-selling, icp, board-positioning]
related: ["[[communication-architecture]]", "[[audience-of-one-report]]", "[[linkedin-viral-scheduler]]", "[[linkedin-comment-engagement]]", "[[linkedin-repost-evaluator]]", "[[notebooklm]]"]
references: [references/icp-positioning.md, references/ladder-joints.md, "../../workflow-ops/linkedin-viral-scheduler/references/engagement-learnings.md", "../../workflow-ops/linkedin-viral-scheduler/references/ranking-model-2026.md"]
status: active
version: 8
created: 2026-07-09
updated: 2026-10-23
vault_writes: ["cbrain/projects/*", "cbrain/notes/[0-9]*"]
---

# LinkedIn Authentic Storytelling → SSI Boost

*Write LinkedIn posts that stop the scroll of a **specific** audience — European Group CTOs, CTOs, NEDs, and Board Members — and advance a dual goal: **peer authority** and **board/NED positioning**. Real moments in an **executive-vulnerability** voice, aimed at that ICP. The audience is the target; SSI is the effect, not the point.*

**Triggers/Context**
- Deploy when: writing or ideating a LinkedIn post, sharpening reach to the target audience, auditing existing content, or turning a vault moment (meeting, win, failure) into public content.
- The voice is **executive vulnerability**: keep the CTO authority and Business → Product → Technology lens, but let a real moment and *what you got wrong and learned* carry the post. Vulnerability = honest lessons, not a confessional diary.
- **Not** for: exec reports, strategic emails, or board updates → use [[communication-architecture]]. Routine vault edits and quick confirmations stay governed by Density Over Volume.

**Core Blueprint**
Route by intent: *writing a post →* §0–2 · *scoring/planning for SSI →* §3 · *auditing existing posts →* §4 · *harvesting ideas / saving drafts →* §5.

### 0. Load the Target + Pick the Goal (do this first)
- **Read [`references/icp-positioning.md`](references/icp-positioning.md)** — the ICP definition (co-primary since 2026-07-19: Group CTO/NED/Board **and** manufacturing/industrial decision-makers), the two registers, and the positioning pillars. This is the target; the rest of the method aims at it.
- **Read [`engagement-learnings.md`](../../workflow-ops/linkedin-viral-scheduler/references/engagement-learnings.md)** — the empirical rules from the post archive (story beats pitch, sovereignty over-indexes, reach ≠ audience quality). Rule 1 in particular changes how §2 is written below.
- **Read [`ranking-model-2026.md`](../../workflow-ops/linkedin-viral-scheduler/references/ranking-model-2026.md)** (added 2026-08-18) — how LinkedIn's 2026 feed actually ranks, built only on LinkedIn's own engineering publications. Three things there change how §2 below is written: the **hook and the body are read by two different things** (M1), **reach to the wrong audience is mechanically negative, not merely wasted** (M2), and **word choice decides which audience a post is retrieved to** (M4). Everything in it is a mechanism or a labelled inference — it never moves a ship gate on its own.
- **Read [`references/ladder-joints.md`](references/ladder-joints.md)** (added 2026-08-22) — the internal diagnostic spine. Four joints in the climb from tool to ecosystem, and for each one **why companies stall there**. The stall is the owned territory; the rung sequence itself is published prior art and is never claimed. **The ladder is never presented in public as a named model** — see the methodology check in §2 and the reasoning in that file's opening note.
- **Name five things before writing a word:** (1) which **goal** this post serves — *peer authority* (Register A) or *board-readiness* (Register B); (2) which **joint** it sits on — one, not three (added 2026-08-22; `ladder-joints.md`); (3) which **positioning pillar** supplies the evidence; (4) **whose dialect it is written in** — pick the segment and name three terms from that segment's row in the **Buyer Lexicon** (`icp-positioning.md`) that this post will genuinely contain (added 2026-08-18; this is the retrieval lever, see M4); (5) the **audience-fit test** it must pass at the end (now six checks — see `icp-positioning.md`).
- Targeting is the first move, not a finishing filter. A post with no named goal is broadcast — and broadcast is not for this ICP.

### 1. Start With the Why + Mine the Real Moment
- Write the one-line **why** first — the problem you love solving. It colors everything in the post; if you skip it, the post drifts into broadcast.
- Harvest the raw moment from the vault (`cbrain/cbrain/` → `daily reports/`, `notes/`, `projects/`): a decision you got wrong, a project win, a hard client conversation, a "seek discomfort" truth. Specific beats generic — real details, real dialogue, real stakes.
- **Primary-source + live-trigger pattern (Register B):** when a live news event (a funding call, a regulation, a ruling) intersects a pillar, pull a NotebookLM-loaded primary source (see [[notebooklm]]) that already diagnosed the underlying problem — an EU report, a whitepaper — and query it for the report's own numbers. The sharpest take is usually *the announcement doesn't fix what the source already measured*. A real vault moment still anchors the hook (Rule 1/2) — this sources the data spine, not the story. Worked example: `output/linkedin/battery-booster-sovereignty-2026-07-29.md` (Draghi competitiveness report + the EU's Battery Booster Facility call).
- **The moment must map to a positioning pillar and be legible to the ICP** — a decision / scale / risk / governance moment a Group CTO or board member would recognise as *their* kind of problem. Abstract client, programme, and defense/GovTech specifics (confidentiality is absolute).
- **Calibrate the vulnerability:** the stakes and the lesson are real; the exposure is *what I got wrong and what it taught me*, not oversharing. Keep the business lens visible — the story should still show how you think about value, product, and tech.

### 2. Build the Post (Hook → Arc → Human Formatting → Photo)

**First, the two levers (added 2026-08-18 — see `ranking-model-2026.md` M1/M5).** A post is read by two
different things, and they read different parts:
- **The human decides `skip` vs `long-dwell`** from what renders above the "…see more" fold. That is the
  **hook's** job — and `long-dwell` is a *threshold* label, not an accumulator, so the lever is a real
  **payoff above the fold**, never length. "Write longer to farm dwell" is the wrong inference from a real
  mechanism.
- **The retrieval model embeds the whole post text** to decide whose feed it belongs in next time. That is
  the **body's** job — be semantically unmistakable about which territory this is and whose problem it
  solves, in that buyer's own vocabulary.
A tension-perfect hook on a vague body survives the fold and then fails retrieval. Both levers, every post.

- **Hook (first ~3 lines):** ~90% read on a phone and scan the opening. Run the scroll-stop test *and* the **audience-fit test** — *would a European Group CTO or a sitting board member stop, respect this, and think "this person belongs at my level"?* Lead with the real, slightly uncomfortable line — never "Reflecting on my journey this quarter…". Give a pinch of intrigue. **Never open on a capability announcement or a generalising claim** ("Most manufacturers…", "X-as-a-Service changes…") — that's a pitch, not a hook, and it's the exact shape of the two worst-performing posts in the archive (`engagement-learnings.md`, Rule 1). The lived moment *is* the hook.
- **Arc — three skeletons, pick one (expanded 2026-08-18).** The default remains the story arc; the other two were missing from the library entirely, which is why every post came out the same shape. All three are subject to the same executive-vulnerability voice and the same no-pitch rule.
  - **Story → Lesson → Application** *(the default, and what this skill has always used)*: *what happened → what it felt like → the take.* Tell, don't teach — the lesson lands because the story earned it, not because you lectured. Best for a lived moment with a real cost.
  - **Problem → Agitate → Reframe**: open on a **specific** pain the buyer is living this quarter (named in their dialect), make its real cost concrete — money, downtime, a missed window — then reframe rather than sell. **The pain must still be one I have actually stood in front of**, introduced through that moment; a generalised pain ("Most manufacturers struggle with…") is the exact pitch shape Rule 1 kills. Best when the buyer's problem is sharper than my story.
  - **Decision → Before/After → What Actually Changed**: a decision I owned, the state before, the state after, and the *one* thing that turned it — with the cost priced in. Best for a Register-B judgment post. **Not** a delivery brag: if it lands on "look what we shipped" instead of "here is the call and what it cost," it fails the table test.
  - Whichever skeleton: never open on the conclusion, and never let the shape become visible as a template.
- **The take carries the register.** *Register A (peer):* land on an owned architectural trade-off only someone who's shipped-and-killed would make. *Register B (board):* land on a judgment about value, risk, or capital — the Business → Product → Technology lens, top-down. If the take could be written by a senior engineer, it isn't board-register yet.
- **Human formatting:** one thought = one line; bullets for lists, stats, and lessons; no walls of text. If it looks like a textbook, people assume it's homework.
- **Payoff above the fold (added 2026-08-18):** give the reader one real thing — the number, the tension, the turn — before the "…see more" cut, not after it. The reader's commit-or-skip decision is made there, and `skip` is a label the model trains on. A post that back-loads its entire value is optimising for a reader who already decided to leave.
- **Lexicon check (added 2026-08-18):** name the segment this post is written for and confirm **three terms from its Buyer Lexicon row** (`icp-positioning.md`) appear naturally in the text. If the three terms that actually appear are all consultant dialect ("servitization enablement", "digital transformation"), the post will be retrieved to consultants — which is precisely the measured Rule 5 gap. **Rewrite in the buyer's words, never salt them in:** a semantic model exists to see through keyword-stuffing, and padding is a Soul.md line anyway. If the honest answer is "I don't know their words for this," that is a domain gap to close, not a wording problem.
- **The body owes the reader three things, in order (added 2026-08-19).** From the "Mastering the Art of Viral LinkedIn Growth" notebook (`9338ba5c-…`, single YouTube source — **Tier-3, craft guidance only, never a scorer weight** per `engagement-learnings.md` Rule 6): **(1) agitate a specific pain the *reader* is living**, "not generically but in a way that makes them feel like you're describing their exact situation"; **(2) offer a reframe or solution**; **(3) close with a takeaway they can act on**. The failure this catches is a post that agitates *somebody else's* pain — a case study the reader watches rather than a problem the reader has. Diagnosed on the 2026-08-19 post: four-fifths analysis of another company's model, with the reader's own situation appearing once, late. **Check: by the second block, has the reader met their own problem?**
- **Polarity check — the take must be pushable-back-on (added 2026-08-19, same Tier-3 source).** The source's "prolific zone": mainstream takes are noise, and a take is in the zone when "people who agree love it and the people who don't actually push back." An analytically airtight post nobody can disagree with generates respect and no conversation. This is a **craft prompt, not a licence to manufacture controversy** — the claim must still be one you'd defend in a room, and it never overrides the confidentiality or no-overselling lines. Where a real stakeable claim doesn't exist, don't invent one.
- **Methodology check — the hardest gate added since the pitch test (added 2026-08-22).** Ask: does this read as an **operator telling you what broke**, or as a **consultant presenting a framework**? If a reader could reconstruct a stage model from the post, rewrite it. Symptoms: numbered stages in the body, the words *maturity / journey / framework*, a diagram that would work as a slide, more paragraphs about the model than about what happened. **This is not stylistic.** The Company A hearing loss turned on a panel that had already written "kein Guru / Umsetzungsverantwortung" in its briefing and was explicitly testing *"Umsetzer oder Berater?"* (`output/20260822-company-a-postmortem.md`). A signature framework is the artifact class of the reading that lost the role. The joint supplies the frame *internally*; the post shows the stall.
- **Named disagreement is allowed, and gated (added 2026-08-22).** Disagreeing publicly with a named vendor, consultancy or platform strategy is permitted **only on first-party or Tier-1 evidence** — something you measured, delivered, or can cite from a primary source. This register produced the account's strongest authority result (a Siemens division CEO conceding the sovereignty wedge publicly, 2026-07-30). Without the evidence it is just a swipe, and the no-overselling and no-guess-as-fact lines bind harder here than anywhere else: a contested claim about a named company is the one place an unsupported number ends the credibility permanently.
- **Photo:** real, with people, joy over polish. No stock images, no perfect headshots. The team selfie, the laughing shot, the "don't build alone" moment outperforms the posed portrait.
- **Document / carousel card (added 2026-08-22).** When the asset is a diagnostic rather than a story, render it as a document/carousel via the verified headless-Chrome path (`--force-device-scale-factor=2 --window-size=1080,1350 --screenshot`). This is the save-worthy format by construction — a reader keeps a frame they can apply to their own company. **The methodology check still applies**, and it is *harder* to pass here: a card is one step from a slide. A card that lays out stages fails; a card that lays out *what breaks and how you'd know* passes.

### 3. SSI Is the Lagging Signal, Not the Target
**Resonance with the ICP is the goal; SSI is how you know it's working.** LinkedIn's Social Selling Index has four components (~25 pts each). Don't optimise the number — optimise the story and the conversation for the target audience, and the number follows.

| SSI Pillar (~25 pts) | The move that moves it — aimed at the ICP |
|---|---|
| **Establish your professional brand** | Publish story-driven posts in one of the two registers; profile reflects the same real voice, positioned for peer + board standing. |
| **Find the right people** | *This is the ICP, explicitly* — European Group CTOs / CTOs / NEDs / Board Members. Tag and engage the right peers; a resonant story pulls inbound from exactly them. |
| **Engage with insights** | Share hot takes and lessons from the positioning pillars; comment substantively on the ICP's posts, not just react. |
| **Build relationships** | Photos-with-people, tag peers/mentors, reply to *every* comment — the conversation with the target audience builds the standing. |

### 4. Audit Existing Content (ICP + Storytelling Lens)
Run each recent post through:
- **Does it pass the audience-fit test** — would a European Group CTO / board member stop and respect it?
- **Pitch-not-story?** — does it open on a capability announcement, framework, or event promotion instead of a lived moment? (Added 2026-07-19 — this single failure mode explains the two worst posts in the archive: 0.00% and 0.16% engagement, both pitch-opened.)
- **Would a manufacturing buyer claim this problem?** — would a Head of Digital/Industry 4.0, VP Ops/Manufacturing, plant leader, or industrial-PE operating partner recognise it as *their* problem, at their altitude? (Added 2026-07-19, co-primary ICP.)
- **Whose dialect is it in?** — list the domain terms the post actually uses and sort them into consultant vs buyer dialect (`icp-positioning.md`, Buyer Lexicon). A post that is on-theme but entirely in consultant dialect explains the Rule 5 audience gap on its own, and is the single most fixable defect in the archive. (Added 2026-08-18.)
- **Does it read as methodology?** — could a reader reconstruct a stage model from it? Does it name a framework, number its stages, or spend more words on the model than on what happened? (Added 2026-08-22 — see §2. The archive has never been run against this check, and the framework-shaped posts are the likely failures.)
- **Which joint is it on, and is it only one?** — a post spanning several joints is a maturity model in disguise. (Added 2026-08-22.)
- **Is there a payoff above the fold?** — does the first ~200 characters contain a real thing, or does the post ask for a click on trust alone? (Added 2026-08-18.)
- **Which goal does it advance** — peer authority, board positioning, or is it just broadcast?
- Is the **authentic voice** coming through, or is it corporate autopilot?
- Where is **jargon standing in for a story of real impact**? ("Leveraged synergies" → the actual thing that happened.)
- Does it **add value to the ICP's story** (educate or entertain), or just broadcast?

Output a blunt verdict: **rewrite these · kill these · keep these** — with one line on why each, and the goal/pillar each keeper serves.

### 5. Vault Integration
- **Harvest:** pull post material from the vault per §1 — the graph is your idea backlog.
- **Save drafts:** finished/near-final posts go to `output/` (e.g. `output/linkedin-<slug>.md`).
- **Log ideas back:** capture reusable post ideas as a vault note `cbrain/projects/content-idea-<slug>.md` tagged `#content-idea`, tagged by **pillar + register**, cross-linked to the source meeting/project (Living Knowledge Graph rule) so the idea doesn't die with the moment.

**Optimizations/Gotchas**
- **No credential-parading:** this ICP smells insecurity from the first line. Peer status is earned by a judgment only you could make, never by a trophy case of titles and logos. Relatability + hard-won judgment beats the résumé every time.
- **Board register ≠ delivery brag:** "look what I shipped" is not governance judgment. Register B must carry a view on value, risk, capital, or oversight — the thing a board actually decides. If it's a feature story, it's Register A at best.
- **The flinch test:** "Is this too real — should I delete it?" is usually the signal to *post* — but only within executive-vulnerability bounds. It never overrides confidentiality.
- **Confidentiality is absolute:** real moments from client, GovTech/defense, consortium, or ministry work must be abstracted/anonymized. Never expose client data, protected programmes, or internal strategy — this is a Soul.md inviolable line, and it wins over the flinch test *and* the audience-fit instinct every time.
  - **Checked in code before it ships:** run `python3 scripts/outbound_gate.py check <draft> --public [--allow <name> ...]`. Every account, vault contact, internal channel or employer-internal tag it flags is cut or proven public (source in the evidence note, then `--allow`).
- **Length is not a dwell strategy** (added 2026-08-18): `long-dwell` fires on crossing an unpublished *threshold*, and LinkedIn's own stated philosophy is "time well spent is better than more time spent." A short post that pays off at line 2 beats a long one that is boring at line 4. The 60–220-word band in the audit was never in tension with dwell.
- **Wrong-audience reach has a cost, not just an opportunity cost** (added 2026-08-18): posts shown and scrolled past are used as *hard negatives* in retrieval training (`ranking-model-2026.md` M2). A wide, ignored post actively teaches the platform to stop showing you to those people. This is why the north-star is buyer-weighted, not impressions — and now it has a mechanism behind it, not just a preference.
- **Don't quote the folklore numbers** (added 2026-08-18): "saves are 5× a like", "comments are 15× a like", "70% of reach in the first hour" — all Tier-3 arithmetic with no LinkedIn source (`ranking-model-2026.md` §3). Using one as a fact in a post is an evidence-gate failure, and this ICP is exactly the audience that will know.
- **AI-perfect ≠ real:** don't ship grammatically flawless, heartless prose. If you don't feel it writing it, no one feels it reading it. Care first, edit second.
- **No vanity framing:** don't perform credentials or highlight-reel wins. Relatability beats a trophy case — people connect with the person figuring it out, not the guru.
- **No hedging, no corporate fluff** (Soul.md) — but *blunt is not callous*; storytelling adds human warmth without performative "Great question!" enthusiasm.
- **SSI is a lagging indicator:** the score follows consistent human storytelling plus real engagement. Don't optimize the metric directly — that's a vanity chart. Optimize the story and the conversation; the number follows.
