---
id: linkedin-post-discovery
aliases: [linkedin-post-discovery]
name: "LinkedIn Post Discovery — Search Queries for Share/Comment Candidates"
category: content
description: Generate boolean LinkedIn search queries mapped to the ICP positioning pillars so the user can source repost/comment candidates in their own logged-in browser — LinkedIn search requires an authenticated session this agent cannot reach.
triggers: [find posts to comment on, find posts to share, search linkedin for content, posts worth commenting, sourcing posts, discover posts to engage with, create a linkedin search, linkedin search queries]
tags: [content, linkedin, discovery, search, engagement, ssi]
related: ["[[linkedin-repost-evaluator]]", "[[linkedin-comment-engagement]]", "[[linkedin-authentic-storytelling]]"]
references: ["../linkedin-authentic-storytelling/references/icp-positioning.md", "../../workflow-ops/linkedin-viral-scheduler/references/ranking-model-2026.md"]
status: active
version: 2
created: 2026-07-25
updated: 2026-08-18
---

# LinkedIn Post Discovery — Search Queries for Share/Comment Candidates

**Contract**
- **Input:** none required — a standing reference table; optionally a specific pillar/theme to narrow the query set for one session.
- **Output:** a table of boolean search strings (EN + DE) per positioning pillar, a hashtag shortcut list, and a pre-filter checklist, saved to `output/linkedin/post-discovery-search-queries-<date>.md`.
- **Allowed tools/artifacts:** read [`icp-positioning.md`](../linkedin-authentic-storytelling/references/icp-positioning.md) for the pillar definitions. `WebFetch` cannot execute the actual search — LinkedIn's `/search/results/content/` endpoint hits an authenticated sign-in wall unconditionally (confirmed live 2026-07-25). This is a platform constraint, not a one-off bug — don't re-verify it every run.
- **Done when:** the query table is saved and the user has run at least one query in their own logged-in browser, pasting candidate post URLs back for [[linkedin-repost-evaluator]] / [[linkedin-comment-engagement]] to score and draft.

**Triggers/Context**
- Deploy when asked to find, source, or discover posts worth commenting on or resharing — or literally "create a linkedin search."
- This is the **sourcing step upstream** of [[linkedin-repost-evaluator]] and [[linkedin-comment-engagement]]: those two evaluate a specific URL already in hand; this skill produces the URLs to hand them. Not a replacement for either — it never scores or drafts anything itself.

**Core Blueprint**
1. Load the seven pillars + two ICP segments from `icp-positioning.md`.
2. Reuse the query table below — refresh it only when the pillars/positioning change, don't regenerate from scratch each run.
3. Hand the user the usage steps (below) — the search itself runs in *their* logged-in session, not this agent's.
4. Apply the pre-filter checklist before a candidate URL comes back for scoring, to keep obvious P1 losers out of the pipeline.
5. Save/refresh the table at `output/linkedin/post-discovery-search-queries-<date>.md`.

### How to use (hand to the user)
1. Paste the **keyword string** (not a full URL — LinkedIn's own search box parses the boolean syntax more reliably than a raw query param) into LinkedIn's search bar.
2. Click the **"Posts"** filter tab (the default search returns people/companies, not content).
3. Sort by **"Latest"** to comment early on a fresh thread, or **"Top"** for already-proven engagement.
4. Optional: add the **"Past week"** date filter to match a Tue/Thu posting cadence.
5. Shortlist 2–3 candidates whose **author** fits the ICP and whose **post** reads as substance, not a pure product/event pitch.
6. Paste the post URL back for `linkedin-repost-evaluator` (P1/P2 score + verdict) and, if warranted, `linkedin-comment-engagement` (draft).

### Query table by pillar

| Pillar | EN query | DE query |
|---|---|---|
| **Sovereign infrastructure / Gaia-X / digital sovereignty** (board) | `("digital sovereignty" OR "Gaia-X" OR "sovereign cloud" OR "sovereign AI") AND (Europe OR EU)` | `("digitale Souveränität" OR "Gaia-X" OR "europäische Cloud") AND (Europa OR EU)` |
| **Manufacturing/industrial competitiveness** (manufacturing buyer + board) | `(manufacturing OR industrial OR factory) AND (competitiveness OR "labor cost" OR "energy cost" OR bureaucracy) AND (Germany OR Europe)` | `(Industrie OR Fertigung OR "Standort Deutschland") AND (Wettbewerbsfähigkeit OR Arbeitskosten OR Energiekosten OR Bürokratie)` |
| **EU AI Act / AI regulation & enforcement** | `("AI Act" OR "AI regulation") AND (enforcement OR compliance OR sovereignty)` | `("KI-Verordnung" OR "AI Act") AND (Durchsetzung OR Regulierung)` |
| **Agentic AI in the enterprise / production reality** (peer) | `("agentic AI" OR "AI agents") AND (production OR enterprise OR manufacturing)` | — |
| **GovTech & European defense tech** (board) | `(GovTech OR "defense tech" OR "defence tech") AND (Europe OR EU OR sovereignty OR procurement)` | — |
| **EU Horizon consortium / industrial R&D funding** (board) | `("Horizon Europe" OR "EU Horizon" OR consortium) AND (manufacturing OR industrial OR AI)` | — |
| **Servitization / Industry 4.0 / Smart Factory** (manufacturing buyer) | `(servitization OR "as-a-service" OR "Industry 4.0" OR "smart factory") AND (manufacturing OR machinery OR OEM)` | `("Industrie 4.0" OR "Smart Factory" OR Maschinenbau) AND (Wettbewerbsfähigkeit OR Digitalisierung)` |

### Buyer-dialect query set (added 2026-08-18) — the queries that actually surface plant-floor authors

The table above is written in **pillar/policy vocabulary**, which reliably surfaces consultants,
policy people and vendors talking *about* manufacturing. It rarely surfaces the operators themselves.
That is the sourcing-side face of this account's standing Rule 5 audience gap: searching in consultant
dialect finds consultant authors. These queries search in the **buyer's own dialect** instead
(see the Buyer Lexicon in [`icp-positioning.md`](../linkedin-authentic-storytelling/references/icp-positioning.md)).

| Segment / angle | EN query | DE query |
|---|---|---|
| **Downtime & line reality** (VP Ops, plant manager) | `(OEE OR "unplanned downtime" OR changeover OR retooling) AND (plant OR line OR shift)` | `(OEE OR Rüstzeit OR Umrüstung OR "ungeplanter Stillstand") AND (Werk OR Linie OR Schicht)` |
| **Shop-floor connectivity** (Head of Digital, Industry 4.0, smart-factory lead) | `("OPC UA" OR PLC OR SCADA OR MES OR brownfield OR retrofit) AND (plant OR factory OR "shop floor")` | `("OPC UA" OR SPS OR SCADA OR MES OR Bestandsanlagen OR Nachrüstung) AND (Werk OR Fertigung OR Produktion)` |
| **Capacity & supply resilience** (plant + procurement + board) | `("spare parts" OR "lead time" OR "second source" OR "supply chain") AND (machinery OR manufacturing OR OEM)` | `(Ersatzteile OR Lieferzeit OR Zweitquelle OR Lieferkette) AND (Maschinenbau OR Fertigung OR OEM)` |
| **OT security & regulation** (plant IT / OT leader) | `("IEC 62443" OR NIS2 OR "network segmentation" OR "vendor remote access") AND (OT OR plant OR industrial)` | `("IEC 62443" OR NIS2 OR Netzsegmentierung OR Fernzugriff) AND (OT OR Werk OR Industrie)` |
| **Asset economics** (industrial-PE operating partner, manufacturing CFO/CTO) | `("asset utilisation" OR "asset utilization" OR "machine hours" OR "pay-per-part" OR capex) AND (manufacturing OR industrial OR "operating partner")` | `(Anlagennutzung OR Maschinenstunden OR "Pay-per-Part" OR Investitionen) AND (Fertigung OR Industrie)` |

**Two reasons this set earns its place, beyond finding better candidates:**
1. **Author selection is a distribution lever.** LinkedIn's 2026 ranker late-fuses affinity features
   (Tier-1; [`ranking-model-2026.md`](../../workflow-ops/linkedin-viral-scheduler/references/ranking-model-2026.md) M6), so *whose* threads you show up in feeds back into ranking.
   These queries surface the authors whose affinity is actually worth building.
2. **This is where the Buyer Lexicon gets refreshed.** Every post these queries return is a free sample of
   the buyer's real vocabulary. When a term recurs that isn't yet in the lexicon, **add it** — the lexicon
   file explicitly asks to be harvested rather than invented, and this is the harvesting step.

**Hashtag shortcuts** (feed-scroll, faster than the search box for a daily skim): `#DigitalSovereignty #GaiaX #Industry40 #SmartFactory #AIAct #AgenticAI #GovTech #HorizonEurope #Servitization`

**Pre-filter checklist** — skip a candidate before sending it over if:
- The author is IT/software-vendor-flavoured with no manufacturing/board angle (fails P1 before it's even scored — cf. the Tom Whitehead MCMC/HMC post, P1=1).
- The post is a pure capability announcement or "come see me speak" **and** P1 also reads weak — still send it if P1 looks ≥4 (that's exactly the quote-share pattern), but a P1≤3 pitch post is a pure skip.
- It's outside the seven pillars **and** has no obvious owned-judgment wedge — borrowed territory reads as generic (cf. the pillar-fit caveat on the Aumovio 40h-week post).

**Optimizations/Gotchas**
- **LinkedIn search requires auth — confirmed, not assumed.** A live `WebFetch` against `/search/results/content/` returned LinkedIn's sign-in wall, not results. Don't spend a tool call re-confirming this each run.
- **Repost yield will run lower than comment yield.** Across the 5 posts sourced/evaluated the week this skill was built, the repost verdict was skip on all 5 (P1 gate or negligible reach), but 4 of 5 produced a usable comment. These queries are tuned to surface *pillar-relevant* content, not necessarily *manufacturing-buyer-shaped* content that clears repost's P1≥4 bar — treat comment as the default outcome, repost as the occasional bonus.
- **Pacing discipline across a sourcing run.** If one session surfaces several pillar-adjacent posts on the same theme (e.g., multiple sovereignty hits), track how many same-theme comments have already gone out that week before drafting another — see the Giorgio Alverà/Ipazia post (2026-07-25), flagged as the fourth sovereignty-themed comment that week, risking a single-topic-campaign read. `linkedin-comment-engagement` doesn't track this on its own; this skill's discovery step is where the pacing check belongs, since it's the point where multiple candidates are seen together.
- **Run the buyer-dialect set first when the goal is audience, not volume.** The pillar table yields more hits; the buyer-dialect table yields more *ICP authors*. If a sourcing session is meant to move the manufacturing-viewer share, the second table is the one that matters — and expect fewer, better candidates from it.
- **Refresh the table** when `icp-positioning.md`'s pillars change, or when a query set surfaces nothing but P1≤3 posts for 2+ sessions running — don't let it go stale silently.
