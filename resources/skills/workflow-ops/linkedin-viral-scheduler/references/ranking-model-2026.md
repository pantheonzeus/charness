# How LinkedIn Actually Ranks a Post (2026) — mechanism, and what it changes about the craft

*Added 2026-08-18. Until now the skill library encoded **heuristics** (≤3 hashtags, no links in body,
one idea per line) with no model of the machine underneath, so there was no way to tell a real mechanism
from folklore. This file is that model, built only on LinkedIn's own engineering publications, and it
states the craft consequence of each mechanism. Read it with
[`engagement-learnings.md`](engagement-learnings.md): this file is **why the platform behaves that way**,
that file is **what this account's own data has actually measured.** Where they disagree, the account's
own data wins — it is evidence about this author, not about LinkedIn in general.*

**Evidence tiering used throughout:** **T1** = LinkedIn engineering blog / LinkedIn-authored research ·
**T2** = reputable secondary write-up of a T1 source · **T3** = marketing blog / creator video. Charter §2
forbids a T3 claim outranking a T1 one. Full source list and verbatim quotes:
`output/.runs/20260818-linkedin-360brew-deepdive/EVIDENCE.md`.

---

## 1. The stack, as LinkedIn describes it

LinkedIn rebuilt the feed in two halves (T1: ["Engineering the next generation of LinkedIn's
Feed"](https://www.linkedin.com/blog/engineering/feed/engineering-the-next-generation-of-linkedins-feed),
2026-03-12; T1: [arXiv 2602.12354](https://arxiv.org/html/2602.12354v1), "An Industrial-Scale Sequential
Recommender for LinkedIn Feed Ranking"):

**Retrieval — a shared-LLM dual encoder.** One LLM embeds *members* and *posts* into the same vector
space; candidates are fetched by nearest-neighbour search (<50 ms). This replaced the old bundle of
separate chronological / collaborative-filtering / embedding / trending retrieval paths. It is explicitly
semantic rather than lexical — LinkedIn's own illustration: a member interested in *"electrical
engineering"* who engages heavily with *"small modular reactors"* gets connected, where
*"traditional keyword-based systems might miss the connection."*

**Ranking — Feed-SR, a transformer Generative Recommender.** Replaces the previous DCNv2 ranker and is
"currently the primary member experience on LinkedIn's Feed." It reads the viewer's **most recent
T=1000 impressions** as a *chronological sequence* with causal attention (posts interleaved with action
embeddings), late-fuses count/affinity features, and heads into an MMoE. Online A/B: **+2.10% time
spent.**

**What the ranker is trained to predict — the actual label set, verbatim (T1, arXiv 2602.12354):**
- **Passive:** `click`, `skip`, `long-dwell`
- **Active:** `like`, `comment`, `share`
- `Long Dwell` = "dwelling on a post longer than a specified threshold" (threshold unpublished).
- `Contribution` = "a like, comment, or share."

**360Brew is not this.** 360Brew (150B decoder-only, >30 consolidated predictive tasks) is the
foundation-model research line, and **its arXiv paper was withdrawn by arXiv administrators over
licensing issues.** Treat "360Brew ranks your feed" as an imprecise shorthand: the *published,
in-production* Feed ranker is Feed-SR/GR. Anything a T3 blog asserts as a "360Brew rule" is that author's
extrapolation from a withdrawn paper.

---

## 2. Six mechanisms, and what each one changes about writing

### M1 — Two different things read your post, and they read different parts
The **human** decides `skip` vs `long-dwell` from what renders above the "…see more" fold. The
**retrieval model** embeds the **whole post text** to place it in vector space. These are separate levers
and the library used to conflate them.

> **Craft consequence.** The **hook's** job is to beat the skip threshold — tension, specificity, a real
> moment. The **body's** job is to be semantically unmistakable about *which* territory and *whose*
> problem this is. A hook optimised for tension with a body that stays vague is a post that survives the
> fold and then fails retrieval next time.

### M2 — `skip` is a trained label, and being shown-and-ignored is a *hard negative*
`skip` is modelled directly (T1). In retrieval training, "posts shown but not engaged with" are used as
**hard negatives**, and adding just two of them improved recall@10 by 3.6% (T2, ByteByteGo on T1).

> **Craft consequence — the most important line in this file.** Reach to the wrong audience is not
> neutral, it is **negative**. A post served to 2,000 people who scroll past it teaches the model to
> separate the author from those people. This upgrades `engagement-learnings.md` **Rule 4** from a
> commercial preference ("the right audience matters more than impressions") to a **mechanism**: broad
> imprecise reach actively degrades future retrieval. Narrow and resonant beats wide and ignored.

### M3 — Only *positively engaged* posts enter the viewer's sequence
The historical sequence feeding the ranker contains "only posts that received **positive** engagement" —
scrolled-past content is excluded (T1).

> **Craft consequence.** You do not accumulate presence in someone's feed by being shown to them; you
> accumulate it by being *engaged with*. Consecutive posts inside the same 2–3 territories compound —
> each earned engagement makes the next post more retrievable for that member. Territory-hopping resets
> the compounding. Consistency is a distribution mechanism, not a branding preference.

### M4 — The viewer's vector is built from their profile, skills, work history, and engaged posts
The member sequence "incorporates profile information, skills, work history, and a chronologically
ordered sequence of posts they've previously engaged with," rendered through a prompt library that
templates structured features into text (T2 on T1).

> **Craft consequence — the lexicon lever.** Retrieval matches your post against text that reads like the
> target buyer's *own professional record*. A post about the same underlying problem written in
> consultant vocabulary ("servitization enablement", "digital transformation") lands near consultants;
> written in plant vocabulary ("changeover", "unplanned downtime", "spare-parts lead time") it lands near
> plant leaders. **This is the mechanistic answer to `engagement-learnings.md` Rule 5** — the observed
> gap between on-theme message and off-target audience is partly *lexical*, which means the writing craft
> can move it. Rule 5's "distribution problem the writing craft alone can't fully solve" was too
> pessimistic. See the **Buyer Lexicon** in
> [`icp-positioning.md`](../../../content/linkedin-authentic-storytelling/references/icp-positioning.md).

### M5 — `long-dwell` is a threshold, not an accumulator
The label fires on dwelling "longer than a specified threshold" — not on total seconds. LinkedIn's stated
philosophy across its dwell-time work is "**time well spent is better than more time spent**" (T1, 2020
and 2024).

> **Craft consequence.** "Write longer to farm dwell" is the **wrong** inference from a real mechanism.
> The lever is **crossing the threshold**: hook that stops the scroll, then a genuine payoff *above the
> fold* so the reader commits instead of bouncing. A long post that is boring at line 4 loses to a short
> one that pays off at line 2. This is why Mobile Readability's 60–220-word band is not in tension with
> dwell — it never was.

### M6 — Affinity features are a ranking input
Count and affinity features are late-fused into the ranker alongside the sequence (T1).

> **Craft consequence.** Sustained, substantive interaction with a target segment is an *input to
> ranking*, not merely networking. This is the mechanistic basis for
> [[linkedin-comment-engagement]] — commenting on the ICP's posts is distribution work, not
> just relationship work.

### M7 — Cold start runs on profile text
Member profile embeddings are "particularly valuable for members with short or sparse histories":
**+2% AUC for members with <10 historical actions** (T1, arXiv 2602.12354).

> **Craft consequence — a cross-skill one.** Profile text is a ranking input, so the **profile and the
> posts must share one lexicon.** [[linkedin-profile-headhunter]] currently optimises the profile purely
> for *recruiter keyword search*; nothing in the library optimises it for *feed retrieval semantics*.
> Those two objectives mostly agree (both want the buyer's vocabulary) but nobody was checking.

---

## 3. What the T3 layer claims, and what to do with it

These circulate everywhere and several are directionally consistent with T1 — but **none of the numbers
traces to a LinkedIn source.** Do not quote them as fact and do not set a scorer weight from them.

| T3 claim | Status |
|---|---|
| "A save ≈ 5× a like, ≈ 2× a comment" | **No T1 support.** Feed-SR's published labels are click/skip/long-dwell/like/comment/share — **saves and sends are absent; `share` is present.** This does not prove saves are ignored platform-wide (other surfaces and objectives exist, and a "send" is arguably a share), but no primary source licenses a *multiplier*. See §4. |
| "Comments ≈ 15× a like" | No T1 support. `comment` and `like` are both trained labels; **no published relative weight.** Comments being *worth more* is plausible (a comment is rarer and correlates with dwell); the number is invented. |
| "70% of reach is decided in the first 60–90 minutes" | No T1 support. Sequence-based ranking is recency-ordered, so early signal plausibly matters, but the figure is uncited and the sources contradict each other on the window. |
| "Reach down ~50% YoY" | Unverifiable from outside. Irrelevant as guidance either way. |
| "Links in the body cut reach by more than half" | Direction plausible and already encoded as a hard hygiene rule (0 links). The magnitude is uncited. **Keep the rule, drop the number.** |
| "Put the link in the first comment to restore reach" | Unverified workaround. Do not build a rule on it. |
| "Engagement bait is downranked" | **Directionally consistent** with LinkedIn's own anti-bait posture and with this account's own data (`has_question` r=+0.157 ≈ noise). Already encoded via `CTA_BAIT`. |
| "Posts pass a human editorial review before wide distribution" | **Folklore.** Nothing in LinkedIn's engineering material describes human review in the ranking path. Recorded so a future run doesn't rediscover it. |
| "≤3 hashtags" | No T1 support either way. Harmless, long-standing, cheap to keep. Keep as convention, not as physics. |

## 4. The saves question — stated honestly

Three T3 blogs are currently cited in [`viral-metrics.md`](viral-metrics.md) to justify the Save Rate
benchmark and the "saves are the strongest distribution signal" framing. The T1 label set does not
include saves. The honest position, and the one the library should hold:

- **Keep measuring Save Rate.** It is a real, informative *reader-behaviour* metric — "this was worth
  keeping" — regardless of whether it is a ranking label.
- **Stop asserting it is the strongest distribution signal**, and delete the 5×/2× multipliers. They are
  Tier-3 arithmetic contradicted by omission in Tier-1.
- **Keep Save-Worthiness (Family B) non-gating.** The case for promoting it to a gate rested largely on
  those multipliers. It must be earned on this account's own corpus via
  [[linkedin-scoring-calibration]], not on blog authority.
- **Craft point that survives all of this:** writing something worth *keeping* — a reusable frame, a
  number worth returning to — is good practice independent of the ranking question, and none of the
  current scorecards reward re-usability. That gap is real; the justification for closing it is craft,
  not algorithm.

## 5. What this model does *not* license

- **No engineering the embedding.** Keyword-stuffing buyer vocabulary into a post that has no real
  content is exactly what a semantic model is built to see through, and it violates the persona's own
  no-fluff line. The lexicon lever means *write about the buyer's actual problem in their actual words* —
  it is a reason to know the domain, not a reason to salt the text.
- **No number-quoting from §3.** If a draft ever cites "saves are 5× likes" or "70% in the first hour"
  as fact, that is an evidence-gate failure.
- **No new gate.** Nothing in this file changes a ship gate on its own authority. Mechanisms inform the
  craft and generate labelled hypotheses for the calibration skill; only this account's measured data
  moves a threshold.
