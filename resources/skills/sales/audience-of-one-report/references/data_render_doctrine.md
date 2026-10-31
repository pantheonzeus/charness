# Data-integrity & render doctrine — `audience-of-one-report` (v7.4+)

`gates.md` catches fabrication and structural slips. This file catches the **interpretation, comparability, external-data and render** failures that surfaced in the RC-1 fictionalized composite run (a filtered-dataset `0 senior / 0 MLOps` read as a capability gap, mis-framed twice, resolved only by an independent same-basis census). Per the anti-bloat rule, most of this **sharpens an existing invariant or gate**; only items 4, 5, 6 are genuinely new, and none is a counting threshold.

**Where this binds.** Read at **Step 4A** (DD reasoning + chart-basis choice), again at the **Step 5 → Step 6 boundary** (with Gate 7), and **before render** (with §9). Mechanical sub-checks live in `gates.md §10`.

## 1. Proxy reading — absence is not absence  *(sharpens invariant #4, inverse direction)*
Invariant #4 runs both ways. Stated: *if you can't source it, it doesn't exist.* Inverse: **a sourced low/zero/absent value in one proxy is not a claim about reality** — a filtered dataset, hiring postings, a transcript each measure *visibility through that lens*, not capability. Bites hardest on **small-base cells** (a `0` on n=38 is noise), **the reference entity** (its comparison carries the brief's thrust), and **negative/gap claims** (the reader *is* the company described). *Prevents:* reading Meridian's filtered "0 senior/0 MLOps" as a hollow core when its live job board carries senior ML/DS, software, FPGA, cyber roles.

## 2. Second source is mandatory for headline / centerpiece / reference-negative claims  *(sharpens the provenance gate + `subject_metrics.json` schema)*
`second_source` is **mandatory** for (1) any value anchoring the spine, an exec headline stat, or a centerpiece visual, and (2) any "lowest/only-one-without/absent/0/weakest" claim about the reference entity. It must be a **comparable-basis corroboration** (a different lens reaching the same read — a live job-board census behind a filtered-dataset number), not a restatement. If none exists, the value appears **only as a flagged directional observation**. Log each in `headline_claims.json`. **Tier discipline (v7.5):** every figure carries `source_tier` (primary = IR/filing/transcript/official newsroom/own careers count; secondary = analyst/trade-press/aggregator; inferred = reconstructed from announcements). A headline number may be single-sourced only if primary; where it leans on a `second_source`, the basis + second source may not **both** be secondary/inferred. (§10-A.)

## 3. One axis, one basis  *(sharpens the comparability gate)*
Every quantity on a **single chart axis** shares one basis (source/window/denominator/universe). An off-basis entity is brought onto the common basis or shown in a separately-labelled panel — never a directly-comparable point. A sub-floor small-base value may not be plotted as an unflagged comparable point. Record each chart's per-entity basis in `chart_basis.json`. Fix pattern: the two-panel `c2` (filtered cores left; live-census shares right). **Subject-set integrity (v7.5):** every entity in a subject-positioning figure is a developed subject **or** the stakeholder flagged `"role":"stakeholder"`; plotting the stakeholder as an unmarked peer contradicts the subject count. (§10-B, §10-E.)

## 4. An alternative is only real if its data is  *(NEW hard rule)*
Wherever the skill offers a choice (the DD "alternative considered and rejected", a chart-option A/B, an interpretation fork, the subject chooser), each option must be backed by data of **comparable basis and quality**. Never offer an expedient option that yields a known-misleading artifact as if equivalent ("keep the filtered chart + a caveat" when that chart plots the reference at a near-zero the caveat can't un-see). If the honest version needs data you don't have, say so and get it. When a finding is contested (flips depending on the source), pull comparable data for every entity *before* committing either framing. *Prevents:* the Meridian framing flip-flopping hollow-core → hidden-internally → built-and-visible across three revisions.

## 5. Read-and-extract immediately after any external scrape  *(NEW)*
The account can lock (quota/rate) between write and read. On every external scrape: pull in small chunks (≤30 items, only the fields you need), classify/extract the signal in-run, persist the extracted result locally (the tally, not just the dataset ID). Before a multi-entity batch, check remaining quota; cap each run (`maxTotalChargeUsd`); scrape only what the confirmed DD set needs.

## 6. Imported findings are leads, not sources  *(NEW)*
Findings from outside the current run (pasted transcripts, prior-session summaries, "I already checked X", a parallel session) are **leads to re-verify in-run, not fetched sources** — they don't satisfy invariant #4 until re-fetched/re-derived in this run.

## 7. "Present but thin/zero on a small base" gets the same skepticism as "absent"  *(sharpens comparability + critic)*
The skill already handles a fully-absent entity correctly (a named peer not in the dataset → labelled qualitative, kept off main charts). Apply the same skepticism to an entity present but thin/zero on a small base in a filtered source (Meridian at 38/0). Both are lens artifacts.

## 8. Render sharpenings  *(sharpens §9)*
(1) **Page-fill floor** — flag non-terminal non-section-break pages below ~70% body-fill. (2) **Break-inside discipline** — deep-dive prose flows across page breaks; only charts/stat-blocks/callouts/closers carry `break-inside:avoid`; never wrap a whole section in avoid. (3) **Reference entity, one encoding everywhere** (the palette's `text` colour, labelled "reference"). (4) **Mixed basis → separate panel.** (5) **Chart render self-check** — confirm the brand font registered (`fm.fontManager.addfont`), titles not clipped, `annotation_clip=False` + bottom-margin headroom. (6) **§9 means actually viewing the pages**, not checking they exist.

## 9. Critic (CP7) probe  *(sharpens the critic checklist)*
The critic must explicitly ask: is any headline stat / spine claim / centerpiece visual resting on a small-base or single-proxy reading — especially for the reference entity? If yes and no comparable second source, demote to a flagged directional note or get the source.

## 10. Render-path pre-flight
Before promising a rendered artifact, probe the render path once (a trivial file/render check) rather than asserting presence/absence. Don't narrate tool availability as an excuse — test, then deliver or state plainly what's missing.

## 11. Comparative claims carry their denominator and peer baseline  *(v7.6, from job-postings-insight)*
Never "Firm X bets on Y"; say "X names Y in 32% of postings, 3.1× the peer rate." Distinctiveness — lift over a peer baseline — is the signal, not raw prevalence. Every comparative/reference-negative/superlative carries a `comparison` block `{subject_value, peer_baseline, n}` in `headline_claims.json`: "Meridian senior-IC 0/38 vs peer median 14%", not "the thinnest". Distinctiveness on a thin base is fragile — state the n, frame directional. (§10-F.)

## 12. Convergence vs divergence — don't headline a subject with a table stake  *(v7.6, soft guidance, NOT a gate)*
**Convergence** (what every subject does — table stakes) is the *backdrop*; **divergence** (what one does that others don't) is the *story*. Never headline a subject with something table-stakes across the field ("they license to AI" is not a tell if everyone does). The field-level read leads with the shared backdrop, then each subject's divergence. Aspiration, not an observed failure — stays soft guidance.

---
*Meta:* none of the above is a "≥ N of X" threshold. Items 1, 8(2,3) sharpen existing invariants/§9; 2, 3, 7, 9, 11 tighten existing gates; 4, 5, 6, 10 are new *principles*, not counts; 12 is soft guidance — all consistent with the anti-bloat rule.
