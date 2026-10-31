---
id: linkedin-viral-scheduler
aliases: [linkedin-viral-scheduler]
name: "LinkedIn Viral Post — Timeliness Pick + Judge-Optimized (Tue/Thu)"
category: workflow-ops
description: "Twice-weekly (Tue/Thu 9am, launchd), pick the **joint** the recency guard permits from the ladder spine (`ladder-joints.md` — four stall points in the climb tool→website→portal→platform→ecosystem; the seven standing topics are now evidence *under* joints, and the rung sequence is prior art that is never claimed in public), confirm a real lived moment exists — **no moment, no post** — then draft a scroll-stopping LinkedIn post in the house voice, then self-optimize it against three complementary gates — a blind-judged Substance score (Topic-DNA + Depth, >=9/10), a blind-judged Audience Pull score (Manufacturing-Buyer Resonance + Story-over-Pitch, >=8/10), and a deterministic Pre-Publish Audit (Hook/Readability/Spacing/AI-Fluff, composite >=85 \"Viral Potential\" band) — until all three pass or a **4-iteration budget** is spent (cut from 12 on 2026-08-22: a draft that cannot pass in four has a material problem, not a wording problem), plus a non-negotiable **methodology check** that fails any draft reading as a framework presentation rather than an operating story. Draft-only — no publishing API exists here; keeps the best version as output/linkedin/latest.md for manual review and posting. Also scores **published** posts post-hoc on 11 viral/quality metrics (`scripts/viral_metrics.py`, auto-recomputed via a launchd watcher) — 7 measured-outcome metrics incl. a buyer-quality-weighted Buyer-Weighted Engagement north-star (formalized as retrospective-only **Scorecard D** in `rubric.md`, and now the calibration skill's tuning target), plus 4 content predictors (Sovereignty/EU-Framing, Save-Worthiness, Conversation-Trigger, and Buyer-Dialect Density added 2026-08-18) reported non-gating inside the Pre-Publish Audit. Grounded since 2026-08-18 in `references/ranking-model-2026.md` — a Tier-1 model of LinkedIn's 2026 feed ranking that also retired several marketing-blog claims the library had been carrying as fact."
triggers: [scheduled linkedin post, tuesday thursday post, viral linkedin post, weekly linkedin, auto linkedin post, optimize linkedin post score, linkedin post loop, linkedin content engine, judge my linkedin post, pre-publish audit, score this post for virality, score published posts, viral metrics, analyze post performance, buyer-weighted engagement, decision-maker density]
tags: [workflow-ops, linkedin, content, automation, launchd, scheduled, optimization, blind-judge, deterministic-scoring, self-evolution]
related: ["[[linkedin-authentic-storytelling]]", "[[linkedin-profile-headhunter]]", "[[linkedin-scoring-calibration]]", "[[linkedin-comment-engagement]]", "[[linkedin-repost-evaluator]]", "[[campaign-week]]", "[[career-campaign-review]]"]
references: [references/rubric.md, references/topics-and-proof-bank.md, references/engagement-learnings.md, references/viral-metrics.md, references/ranking-model-2026.md, "../../content/linkedin-authentic-storytelling/references/ladder-joints.md"]
scripts: [scripts/run.sh, scripts/hygiene_check.sh, scripts/prepublish_audit.py, scripts/viral_metrics.py, scripts/watch_refresh.sh, scripts/ingest_single_post.py]
requires:
  tools: [web_search, web_fetch]
  cli: ["claude", "python3"]
modules: [file-backed-state, evidence-backed-answering, file-backed-handoff, self-evolution, verifier-separation]
environment: "Local terminal, scheduled via launchd (`com.cbrain.linkedin-viral-scheduler`, Tue/Thu 09:00 — cron is documented but blocked by macOS TCC on this machine). Needs vault access (cbrain/), a local `claude` binary for the substance judges, and `python3` (stdlib only) for the deterministic audit — a cloud routine would lack the first two, same rationale as morning-briefing/notebooklm-daily-audio."
status: active
version: 10
created: 2026-07-11
updated: 2026-10-23
vault_writes: ["cbrain/projects/*", "cbrain/notes/[0-9]*"]
---

# LinkedIn Viral Post — Timeliness Pick + Judge-Optimized (Tue/Thu)

*Twice a week, turn a fresh industry moment into a scroll-stopping post anchored in real CV proof points, then grind it against three complementary gates — a blind-judged Substance score, a blind-judged Audience Pull score (manufacturing-buyer resonance + story-over-pitch, added 2026-07-19 from the analytics read), and a deterministic Pre-Publish Audit — until all three pass or the budget runs out. This is the **scheduling + optimization engine** around the craft — the actual writing voice is [[linkedin-authentic-storytelling]]'s, inherited, not restated.*

**Triggers/Context**
- Automatically: the launchd agent fires this Tue/Thu 09:00 local (§5). Expect Thursday to log "no moment, no post" often — that is the one-substantive-plus-one-light cadence enforcing itself, not a failure.
- On demand: "run the linkedin post loop", "run a pre-publish audit on this post", "pick today's linkedin topic".
- **Real-moment / event post (on demand).** A one-off post about a specific real moment (a talk, a launch, a win) normally goes to [[linkedin-authentic-storytelling]] directly. But when you want *this engine's three-gate rigor* on that real moment, run it here: inherit the craft (§0), pick the moment as the "topic" (recency guard is moot), anchor the event as the *reason* — never a "come see me speak" broadcast (the ICP scrolls past those, and P2/Story-over-Pitch will fail it) — and finalize to a **dedicated** `output/linkedin/<event-slug-YYYY-MM-DD>.md` (not just `latest.md`) so a scheduled Tue/Thu run doesn't overwrite the manual post. Worked example: `output/.runs/20260712-linkedin-techdays/`.
- **Not for:** editing the LinkedIn *profile* → [[linkedin-profile-headhunter]]. This skill is the recurring, metric-driven content engine; the other two are the craft and the profile.

**Core Blueprint**

### 0. Load the craft + the targets
- Read [[linkedin-authentic-storytelling]] §0–2 in full — ICP (**co-primary since 2026-07-19:** European Group CTOs / CTOs / NEDs / Board Members **and** manufacturing/industrial decision-makers), the executive-vulnerability voice, hook→arc→formatting, confidentiality rules. **Inherit this craft wholesale; do not re-derive it.**
- Read [`references/engagement-learnings.md`](references/engagement-learnings.md) — the empirical rules distilled from the real post archive (story beats pitch, consortium/EU narrative is the workhorse, sovereignty over-indexes, reach ≠ audience quality). This is the evidence behind Scorecard C below and behind the topic-pick weighting in §1.
- Read [`references/topics-and-proof-bank.md`](references/topics-and-proof-bank.md) — the 7 topics and their CV/vault proof points, now mapped onto joints.
- Read [`ladder-joints.md`](../../content/linkedin-authentic-storytelling/references/ladder-joints.md) (added 2026-08-22) — **the spine the pick now rotates on.** Four joints in the climb from tool to ecosystem, each with the reason companies stall there. The stall is the owned territory; the rung sequence is published prior art and is never claimed in public. Carries the **methodology check**, which this loop must respect: a draft that reads as a framework presentation fails regardless of its scores.
- Read [`references/ranking-model-2026.md`](references/ranking-model-2026.md) (added 2026-08-18) — **how LinkedIn's 2026 feed actually ranks**, built only on LinkedIn's own engineering publications, plus the evidence-tiering table that says which widely-repeated claims are folklore. Read it before changing any weight in the rubric: it is what separates a mechanism from a marketing-blog number, and it supplies the mutation levers §3 now names (buyer dialect, payoff-above-the-fold).
- Read [`references/rubric.md`](references/rubric.md) — Scorecard A (Substance: M1 Topic-DNA + M3 Depth, blind-judged), Scorecard C (Audience Pull: P1 Manufacturing-Buyer Resonance + P2 Story-over-Pitch, blind-judged, added 2026-07-19), and Scorecard B (the Pre-Publish Audit: Hook/Readability/Spacing/AI-Fluff, scripted), plus the combined-loop objective and all three gates.
- Create the run's STATE_ROOT: `output/.runs/<YYYYMMDD>-linkedin-viral/` with a `RESPONSE.md` control spine (checkpoints CP0–CP3 below) and an `EVIDENCE.md`.

### 1. Pick the topic — timeliness-driven, story-first
- Scan the vault for recent signal on each of the 7 topics: `cbrain/daily reports/` (last ~14 days), `cbrain/notes/`, `cbrain/projects/`. **Look specifically for a lived moment** (a meeting, a decision, a real setback or win) behind each candidate topic, not just a clean angle — per `engagement-learnings.md` Rule 1, a topic with no real moment behind it drafts into a pitch.
- Run a light cited `web_search` pass — one query per candidate topic — for a genuinely fresh industry hook (a report, a stat, a public move by a peer OEM/vendor) published in the last ~30 days. Cite every source found.
- **Audience-question sourcing (added 2026-08-19, Tier-3 craft input).** Alongside the 7 standing topics, check what the ICP is actually *asking*: the best-performing posts of 2-3 ICP-adjacent authors over the last 90 days ([[linkedin-post-discovery]] supplies the queries), and recurring questions in the buyer's own forums. A topic that answers a question the buyer already has beats a topic that is merely fresh. Source: notebook `9338ba5c-…`; **craft input, never a scorer weight**.
- Read `output/linkedin/history.tsv` (create empty if absent) and apply the recency guard from `topics-and-proof-bank.md`. **Since 2026-08-22 the guard rotates *joints*, not topics** — deprioritize a joint used in the last 2 posts. Rotating across parallel topics was territory-hopping with extra steps (M3: consecutive posts inside the same territory compound); rotating joints keeps one territory while changing the problem. `history.tsv` columns are now `date  joint  dialect  topic  file`.
- Score each candidate on **freshness × proof-point availability × joint-not-recently-posted × story availability × manufacturing-buyer/sovereignty resonance** (the last two added 2026-07-19 — see `engagement-learnings.md` Rules 1, 3, 5). A candidate with a strong lived-moment angle and a sovereignty or manufacturing-buyer resonance beats a merely-fresher one with no story behind it. Pick the winner and **name its joint and its dialect explicitly** — one joint, never several. Write the pick + every source URL to `STATE_ROOT/topic-pick.md`. **CP0.**
- **Moment supply is the real constraint, not the topic list (added 2026-08-22).** This engine cannot manufacture a lived moment and must not pretend otherwise. If no candidate has a genuine moment behind it, **stop and report that** rather than drafting from a clean angle — that is exactly how five posts in August 2026 were abandoned mid-iteration. The standing cadence is **one substantive post + one light asset per week**, and fewer is the correct answer when fewer is honest.

### 2. Draft the baseline post
- Apply the inherited craft (§0) to the picked topic, anchored in its proof points from the bank. Hook (first ~3 lines) must pass the audience-fit test; arc is what-happened → what-it-felt-like → the take; human formatting (one thought per line, no walls of text).
- Write to `STATE_ROOT/post.md`; copy it to `STATE_ROOT/best.md`.
- Score it as **iteration 0**: run the Pre-Publish Audit (free) and the Substance + Audience Pull judges together (§3), log the row in `STATE_ROOT/results.tsv`. **CP1.**

### 3. The optimization loop — three gates, cheap-first
Full protocol in [`references/rubric.md`](references/rubric.md). Budget **4 iterations** (cut from 12 on 2026-08-22 — see the note below). **Stop when all three gates pass:** `substance = M1+M3 ≥ 9` **and** `pull = P1+P2 ≥ 8` **and** `composite ≥ 85` (Pre-Publish Audit "Viral Potential" band) — or when the budget is spent, whichever first.

> **Why 4 and not 12.** The only paired outcome on record is composite 98.5 → 288 impressions against an archive mean of 1,078 (n=1). Grinding twelve iterations toward a composite buys craft discipline, not reach, and the campaign charter retired reach as an objective anyway. **A draft that cannot pass in four iterations has a material problem, not a wording problem** — the correct response is a better moment or a different joint, not a ninth mutation. Freed effort belongs in pursuit and substance work (`output/20260822-ladder-campaign-charter.md` §7). If the budget is exhausted, report it and say what the material problem is.

Per iteration:
1. **Read** `post.md` and the current scores (`M1, M3, substance, P1, P2, pull, hook, readability, spacing, aifluff, composite`) from `results.tsv`.
2. **Hypothesize** — name the single weakest metric **across all three scorecards** and one targeted mutation to fix it. Do not try to fix everything at once.
3. **Mutate** `post.md` accordingly. Authentic human tone; never introduce a phrase from the canonical AI-fluff list (`references/rubric.md` / `scripts/prepublish_audit.py`); if the weakest metric is P2 (Story-over-Pitch), the mutation must ground the post in a more specific lived moment, not just soften the pitch language.
   - **When the weakest metric is P1 (Manufacturing-Buyer Resonance), reach for the dialect lever first (added 2026-08-18).** The cheapest real fix is usually vocabulary, not more argument: rewrite the post's domain terms from consultant dialect into the buyer's own words (Buyer Lexicon in `../../content/linkedin-authentic-storytelling/references/icp-positioning.md`). The reported `buyer_dialect` sub-score in the audit output tells you mechanically whether the mutation landed — it correlates **+0.444** with real Decision-Maker Density on this account's corpus (n=23) while being correctly uncorrelated with engagement rate. **It is non-gating**: use it as a cheap read on whether the rewrite happened, never as evidence that P1 improved — that is still the blind judge's call.
   - **Never salt in lexicon terms to move the reported number.** That is Goodharting a non-gating diagnostic, it is what a semantic retrieval model exists to see through, and it violates the persona's own no-padding line. If the buyer's words don't fit, the post isn't about the buyer's problem — change the post, not the wordlist.
4. **Hygiene guard** — run `scripts/hygiene_check.sh STATE_ROOT/post.md` first (cheapest check). Fail → auto-reject: restore `post.md` from `best.md`, log `decision=discard, hygiene=fail`, skip straight to the next hypothesis (no audit run, no judge calls spent).
5. **Audit (always, free)** — run `scripts/prepublish_audit.py STATE_ROOT/post.md`; record `hook/readability/spacing/aifluff/composite/band`.
6. **Judge (conditionally)** — re-run the 3 fresh blind judges (`STATE_ROOT/children/judge-<n>/{TASK.md,RESPONSE.md}`, median per metric) for **both** Substance (M1/M3) and Audience Pull (P1/P2) together, in the same task packet — **only if this mutation changed the post's meaning, claims, or framing**; if it was a pure reformatting mutation (line breaks, hashtag/emoji count, word-order for scannability), carry the prior `M1`/`M3`/`substance`/`P1`/`P2`/`pull` forward unchanged and note `judged=carried-forward` in the row.
7. **Decide:** compute `combined = (substance/10*100 + pull/10*100 + composite) / 3`. `combined > best_combined` → **keep** (promote `post.md` → `best.md`, log `decision=keep`). Otherwise → **discard** (restore `post.md` from `best.md`, log `decision=discard`).
8. Stop when all three gates pass **or** 4 iterations spent. Log the stop reason (`all-gates-passed` / `budget-exhausted`).
9. **Methodology check before finalizing (added 2026-08-22, non-negotiable).** Independently of all three scorecards: does the draft read as an operator saying what broke, or as a consultant presenting a framework? Numbered stages, *maturity/journey/framework* language, a structure that would work as a slide, or more words about the model than about what happened → **fail and rewrite**, even at composite 98. Grounded in the Company A post-mortem, not in taste (`ladder-joints.md` §3.5).

**Keep/discard is a file-snapshot operation (copy `best.md` ↔ `post.md`), not a git operation** — `output/` is git-ignored in this repo, so there is nothing to commit or revert; the snapshot file is the only carrier of "the last good version." **CP2.**

`results.tsv` columns: `iteration  timestamp  M1  M3  substance  P1  P2  pull  hook  readability  spacing  aifluff  composite  band  gates_passed  hygiene  decision  hypothesis`.

### 4. Finalize
- **Outbound gate (public mode, deterministic):** `python3 scripts/outbound_gate.py check STATE_ROOT/best.md --public [--allow <name> ...]`. It flags every account, every vault contact with a company, internal chat channels and the employer-internal tag. Each finding is either cut from the post, or it is public: then record its public source in `EVIDENCE.md` and pass the name with `--allow`. Re-run until it prints `OK`. Never ship with an unexplained finding (confidentiality is enforced here, not trusted to the drafting model; arXiv:2609.14003).
- Copy the winning `best.md` to `output/linkedin/latest.md` (overwrite — this is "the last version," not an archive).
- Append one row to `output/linkedin/history.tsv`: `date  joint  dialect  topic  file` (columns extended 2026-08-22 — the recency guard reads `joint`).
- Run the evidence gate ([`_shared/evidence-gate.md`](../../_shared/evidence-gate.md)) — a LinkedIn post is a **small** deliverable: a 3–5 line provenance note in `EVIDENCE.md` is enough, covering the topic-pick web sources and any stat quoted in the post. No stat ships without a cited source; if the loop's mutations introduced an unsourced number, cut it or mark it as illustrative.
- Report the final substance score, the audience-pull score, the audit composite + band, iterations spent, and whether all three gates were hit or the budget was exhausted. **CP3** — tick every control-spine box before stopping (the Stop-hook `control-spine-gate.sh` blocks an unattended cron run from exiting otherwise).

### 5. Scheduling — **launchd as installed (2026-08-22); cron documented but blocked on this machine**

> **What is actually installed:** `~/Library/LaunchAgents/com.cbrain.linkedin-viral-scheduler.plist`, Tue/Thu 09:00 via `StartCalendarInterval` (Weekday 2 and 4), loaded and validated 2026-08-22. **Cron was attempted first and failed**: `crontab` returns `Operation not permitted` under macOS TCC, and granting Full Disk Access is a user-side system change this harness cannot make. launchd needs no such grant, is already the mechanism behind `com.cbrain.notebooklm-daily-audio` and `com.cbrain.workspace-mcp`, and is proven to drive `claude -p` unattended on this machine — so the stated cron preference is overridden **by environment, not by taste**. To revert: grant the terminal Full Disk Access, install the cron line below, then `launchctl unload` the plist.
>
> `run.sh` is unchanged and serves both mechanisms. **Its prompt was stale until 2026-08-22** — it still named "the 7 topics", a 12-iteration budget and the retired M1–M4 `total_score >= 18` rubric. A scheduled job drafting against retired rules is worse than no scheduled job; **re-check the prompt against §1/§3 whenever either changes**, and use `--dry-run` to read it.

```xml
<key>StartCalendarInterval</key><array>
  <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
  <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>
</array>
```

**Cron alternative (documented, needs Full Disk Access).** `scripts/run.sh` is also cron-safe — it resolves its own path, sets `PATH`, `cd`s to the repo root and runs headless.

```
crontab -e
# add:
0 9 * * 2,4 <REPO>/resources/skills/workflow-ops/linkedin-viral-scheduler/scripts/run.sh >> <REPO>/output/linkedin-viral-scheduler.log 2>&1
```
Verify: `crontab -l`. Dry-run without installing: `scripts/run.sh --dry-run` (prints the resolved command, launches nothing).

**Gotchas:**
- **Timezone.** `cron` fires in the machine's local timezone with no explicit tz field — `0 9 * * 2,4` is 9am CEST only while the Mac's clock is on CET/CEST. If the system moves timezone, adjust the hour.
- **macOS permissions.** `cron`/the invoking shell may need Full Disk Access to read the vault and write `output/`.
- **Token cost.** Worst case is 4 iterations × 3 judge agents (budget cut from 12 on 2026-08-22), but the Pre-Publish Audit runs free every iteration and the judges (now scoring both Substance and Audience Pull per call, not two separate rounds) are skipped whenever a mutation is pure reformatting — typically far fewer than the 12-call ceiling. Exits early on hitting all three gates. Runs unattended twice a week — check the log after the first few fires.
- **No publishing.** There is no LinkedIn API/MCP available in this environment — this skill only ever produces `output/linkedin/latest.md`. Posting is manual.


### 5c. Close the loop on a published post (added 2026-08-19) — **this is the step the loop was missing**
The three pre-publish gates score a **draft**. Until now nothing carried a **published** post's real
numbers back to the run that predicted them, so the loop could iterate 12 times toward composite 98.5 and
never learn that the post reached 288 people.

When LinkedIn's per-post export is available (post → *Show stats* → *Export*), run:

```
scripts/ingest_single_post.py <SinglePostAnalytics_*.xlsx> --slug <post-slug> --composite <predicted>
```

It parses the export by **header label** (never position), computes Decision-Maker Density and
Buyer-Weighted Engagement by importing the constants from
`linkedin-scoring-calibration/scripts/build_dataset.py` (single source of truth — never re-implemented
here), appends one row to `output/linkedin/post-outcomes.tsv`, and enforces the Scorecard D
**volume floor**: impressions as a share of the rolling median, with `verdict=distribution_failure`
below 50% no matter how good the mix is.

**Read the pair, don't tune on it.** `composite_predicted` next to `bwe` and `impr_vs_median_pct` is a
prediction-vs-outcome record. A single row moves nothing: weight changes remain
[[linkedin-scoring-calibration]]'s decision on the accumulated ledger, per the same
mechanism-vs-measurement separation as the hypothesis register. First row logged 2026-08-19:
predicted composite 98.5 → 288 impressions, density 35.5, BWE 1.388 (see `engagement-learnings.md`
Rule 7).

### 5b. Post-hoc viral & quality metrics (added 2026-07-19)
Separate from the three pre-publish ship gates (Scorecards A/B/C, which score
**drafts**), 10 metrics score **published outcomes** — see
[`references/viral-metrics.md`](references/viral-metrics.md) for the full spec
and [`references/rubric.md`](references/rubric.md)'s **Scorecard D** for the
formal (non-gating) retrospective definition. Family A (7 metrics: Save Rate,
Conversation Density, Amplification Rate, Follower Conversion, Profile-Pull
Rate, Decision-Maker Density, and the buyer-quality-weighted **Buyer-Weighted
Engagement** north-star) is computed from the vault archive's Performance +
Audience snapshot data via `linkedin-scoring-calibration/scripts/build_dataset.py::buyer_metrics()`
(single source of truth — `viral_metrics.py` imports it rather than
recomputing). Family B (3 metrics: Sovereignty/EU-Framing, Save-Worthiness,
Conversation-Trigger) are content predictors implemented in
`prepublish_audit.py` as **reported, non-gating** fields — they never affect
the `composite ≥ 85` exit code. **[[linkedin-scoring-calibration]] now
calibrates Scorecard B against Buyer-Weighted Engagement** (retargeted
2026-07-19 from a raw reach×engagement blend — see that skill's
`references/methodology.md` §1). First full analysis:
`output/linkedin/viral-metrics-analysis-2026-07-19.md`.

**Family B is now four metrics (added 2026-08-18).** `buyer_dialect` (#11) joins
Sovereignty/EU-Framing, Save-Worthiness and Conversation-Trigger as a reported,
non-gating content predictor, and is also a column in `viral-metrics.tsv`. It
maps to Family A **#6 Decision-Maker Density**, explicitly not to engagement
rate. Same pass retired the "a save ≈ 5× a like" justification behind #1's
benchmark as untraceable to any LinkedIn source — see
[`references/viral-metrics.md`](references/viral-metrics.md)'s evidence
correction and [`references/ranking-model-2026.md`](references/ranking-model-2026.md) §4.

**Auto-recompute (added 2026-07-19).** `scripts/watch_refresh.sh` re-runs
`viral_metrics.py` (pure Python, no LLM call — cheap enough for every
filesystem event) and logs a `REVISIT` reminder once the corpus reaches ~40
posts (tracking the "Family B did not yet validate at n=19" follow-up from
`viral-metrics.md`). Install as a launchd `WatchPaths` agent so it fires
whenever `cbrain/notes/LinkedIn-Posts/` changes — whether the analytics were
refreshed by hand in Obsidian or by an agent in Claude (there is no
`.claude` post-edit hook that would catch the Obsidian case). **Installed 2026-08-22** as `com.cbrain.linkedin-viral-metrics-watch` (loaded, plist validated). The label was corrected from `com.charness.*` to match this machine's existing agents. Historically it shipped **not
auto-installed** — same convention as this skill's own scheduler entry and the
calibration skill's launchd agent, which ship as documented instructions, not
files silently loaded on your behalf:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.cbrain.linkedin-viral-metrics-watch</string>
  <key>ProgramArguments</key><array>
    <string>/bin/bash</string>
    <string><REPO>/resources/skills/workflow-ops/linkedin-viral-scheduler/scripts/watch_refresh.sh</string>
  </array>
  <key>WatchPaths</key><array>
    <string><REPO>/cbrain/notes/LinkedIn-Posts</string>
  </array>
  <key>ThrottleInterval</key><integer>15</integer>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>/Users/<you>/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
  </dict>
  <key>StandardOutPath</key><string><REPO>/output/linkedin-viral-metrics-watch.log</string>
  <key>StandardErrorPath</key><string><REPO>/output/linkedin-viral-metrics-watch.log</string>
</dict></plist>
```
Save as `~/Library/LaunchAgents/com.cbrain.linkedin-viral-metrics-watch.plist`,
install: `launchctl load ~/Library/LaunchAgents/com.cbrain.linkedin-viral-metrics-watch.plist`.
`ThrottleInterval: 15` debounces a burst of saves (e.g. editing several post
notes in one sitting) into one recompute. Dry-run: `scripts/watch_refresh.sh --dry-run`.

**Verified 2026-07-19 (throwaway test agent, unloaded/deleted after):**
`WatchPaths` fired reliably for all three write patterns tested against a
scratch directory — creating a new file, an in-place append to an existing
file's content (no rename), and an atomic write-via-temp-file-then-rename
(the pattern most editors, likely including Obsidian, use for a "safe save").
So this is not a documentation-only claim — it was tested, not assumed. The
one gap: I tested shell writes (`echo`, `mv`), not literally Obsidian's own
save path on this machine, so if a refresh ever doesn't show up in the log,
the fallback is still `scripts/viral_metrics.py` run by hand — kept documented
above for exactly that case.

### 6. Living Knowledge Graph + Self-Learning
- Log the finalized post idea as a vault note `cbrain/projects/content-idea-<slug>.md` tagged `#content-idea`, tagged by **pillar (topic) + register**, cross-linked to whatever meeting/project the proof points came from (Charter §6).
- End with the standard Feedback & Skill-Verification block (Charter §7).

**Optimizations/Gotchas**
- **Judges must be genuinely blind** — a judge agent that has seen the current hypothesis, the prior score, or the loop's history will anchor to it. Fresh context per delegation-handoff, whenever they're actually re-run.
- **Audit-first ordering saves real money** — the Pre-Publish Audit is free and instant; running it before spending a judge call means a purely-cosmetic mutation (fixing Hook or Spacing) never needs to touch the judges at all. Only re-judge when the mutation changed what the post *claims or how it's framed* (this now covers Audience Pull too — a mutation that changes generic language to a manufacturing-specific framing, or a pitch line into a story beat, changed the framing and must be re-judged).
- **The hygiene guard is still the cheapest check of all** — a real outbound link or a 4th hashtag auto-rejects before the audit script even runs, exactly as before.
- **One hypothesis per iteration** — resist mutating multiple metrics at once, and resist mutating across scorecards at once; it makes keep/discard causally uninterpretable (you won't know which change moved which score).
- **Recency guard beats raw freshness** — a very fresh angle on a topic posted 3 days ago should still lose to a slightly-less-fresh angle on an unused topic; repetition reads as broadcast to the ICP.
- **Confidentiality is absolute** (Soul.md inviolable line) — the proof-point bank is deliberately built only from what's already public on the profile; never let a mutation pull in a non-public client detail chasing a better M3 "depth" or AI-Fluff "hard anchor" score.
- **Non-English posts (e.g. German).** `prepublish_audit.py` detects first-person markers and AI-fluff phrases in EN + DE (`ich/mich/mir, mein*, wir, uns, unser*`); its fluff-phrase and tension-marker lists remain English-only, so a non-English post won't be *penalised* for foreign fluff but also won't be *caught* for native-language fluff — lean harder on the human read and the blind Substance judges (which are language-agnostic) for those posts. Curiosity/CTA detection is language-agnostic (digits, `?`, length).
