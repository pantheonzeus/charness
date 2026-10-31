# Weekly Review — Three-Axis Spec & Intake Mapping

*Single source of truth for `scripts/account_metrics.py` (axis formulas) and
`scripts/ingest_xlsx.py` (intake mapping). Mirrors the sibling
`linkedin-viral-scheduler/references/viral-metrics.md` in spirit: honest
formulas, `n` always stated, nothing computed that the export doesn't
actually contain.*

## Why three axes, not one blended score

The account's own career goal ([[career-manufacturing-cto-content-rule]])
splits visibility into distinct audiences that pull in different directions:
a post that reaches recruiters (talent/HR titles) is not the same win as one
that reaches manufacturing buyers, and raw reach alone is neither — Soul.md's
own position is that vanity metrics are "lies with charts." Tracking three
separate axes, rather than one composite, keeps each goal legible and avoids
inventing a weighting scheme with no data to justify it.

## The three axes

| Axis | Formula | Provenance |
|---|---|---|
| **Buyer** | `engagement_rate × clamp(decision_maker_density / 15, 0.4, 2.0)`, `decision_maker_density = mean(senior_share, industry_fit_share)` | Reused verbatim from `linkedin-scoring-calibration/scripts/build_dataset.py::senior_share()` / `industry_fit_share()` / `clamp()` — the same classification and calibrated pivot (15%) already validated against the post-level corpus. Applied here to account-level weekly demographics instead of a single post's. |
| **Recruiter** | `recruiter_share` = job-title keyword share + industry keyword share (`ingest_xlsx.py::recruiter_share()`) | **New.** No invented multiplier — there is no historical corpus yet to calibrate a Buyer-Axis-style pivot for this axis. Reported as a direct, honest share until enough weekly data accumulates to justify one (same "report raw until validated" posture the repo already applies to the post-level Family B content predictors, which stayed non-gating until n≥40). **Revisit once ≥8 weeks of data exist.** |
| **Reach** | `impressions` (raw weekly total) | Deliberately the plainest number LinkedIn reports, not a manufactured composite. `followers_gained` and `engagement_rate` are tracked as separate columns for context — folding raw counts of different units into one invented weighted sum would be exactly the vanity-metric trap this account's content rejects. |

**Buyer-axis honesty note (inherited from `viral-metrics.md` #6):** LinkedIn's
exported demographics are independent marginal top-N lists (Seniority, Top
industries), never a cross-tab — `decision_maker_density` is a documented
*proxy* (mean of two marginal shares), not a measured joint percentage. Same
limitation applies here as at the post level.

**Recruiter-axis honesty note:** real data (calibrated 2026-07-24) shows
recruiter reach surfaces almost entirely as the **"Staffing and Recruiting"
industry share**, not a job-title match — recruiters' actual titles vary too
widely to catch by keyword, and job-title matching alone reads as a false
zero. `recruiter_share` therefore sums two independent signals: a job-title
keyword match (kept for when it does hit) plus the industry-keyword match.
This is a **sum of two different marginal breakdowns of the same audience**
(job title and industry are different dimensions of the same viewer pool),
not a joint measurement — a viewer counted under both signals would be
counted twice. Treat `recruiter_axis` as directional, not precise.

## Intake mapping — `ingest_xlsx.py`

Values are located by **header-label match** (case/whitespace-insensitive),
never by fixed cell coordinates — LinkedIn's export layout is not something
this skill controls, and a coordinate-based parser would silently break (or
silently misattribute a number) the moment it shifts. `LABELS` (scalar
fields) and `DEMO_ROW_CATEGORIES` (demographics) in `ingest_xlsx.py` are the
alias tables — **calibrated 2026-07-24** against this account's own real
exports (3 `AggregateAnalytics_*.xlsx` weekly exports, 3
`SinglePostAnalytics_*.xlsx` post exports), not just the LinkedIn export
vocabulary in general.

**Real export shape (both types):** scalar metrics are `label | value` rows
(e.g. `['Impressions', '1518']`), except one column-header case — a daily
`Date | Impressions | Engagements` (or `Date | New followers`) time-series,
where the *header* is matched and the column summed. **Demographics are a
flat 3-column table**, one row per item, with the category repeated in
column A: `['Seniority', 'Senior', '36%']`, `['Job title', 'Founder', '5%']`
— not a header-then-rows-below block. Entries at LinkedIn's `'< 1%'` floor
don't parse as a number and are dropped (documented as negligible, never
treated as a measured 0).

**Neither export carries a direct engagement-rate field** — `engagement_rate`
is *derived* as `engagements / impressions × 100` whenever both are present
(`derive_engagement_rate()`), and reported to you as computed, not read, in
the confirm-back output.

| Canonical field | Known LinkedIn export label(s) matched |
|---|---|
| `impressions` | Impressions |
| `members_reached` | Members reached |
| `reactions` / `comments` / `reposts` (or Shares) / `saves` | as labelled |
| `sends` | Sends, Sends on LinkedIn |
| `engagement_rate` | Engagement rate *(rare — usually derived, see above)* |
| `engagements` | Engagements, Social engagements |
| `followers_gained` | New followers, Followers gained, Followers gained from this post |
| `profile_viewers` | Profile viewers, Profile viewers from post, Profile viewers from this post |
| `search_appearances` | Search appearances *(not present in a Content/Post analytics export — it's a separate profile-analytics feature; consistently blank + flagged, never fabricated)* |
| Demographics buckets (`seniority`, `top industries`, `top job titles`, `top locations`, `company size`, `notable companies`) | matched by the row's category label in column A (`Seniority`, `Industry`, `Job title`, `Location`, `Company size`, `Company`), value in column B, percentage in column C |

A daily time-series column (e.g. the `ENGAGEMENT` sheet's per-day
Impressions/Engagements) is summed automatically once its header label is
matched — the parser doesn't need a fixed sheet name, only the label
LinkedIn already puts on the column. This also means a scalar found earlier
under a `label | value` form (e.g. `DISCOVERY`'s single `Impressions` total)
is not double-counted against the same label appearing later as a daily
column header — first match wins.

**First-run protocol:** run `ingest_xlsx.py --inspect <file>` on a real
export before trusting any parsed write. Both `--account` and `--post` print
every field they matched (and every one left blank) before writing, so a
label miss is visible immediately rather than silently wrong — confirm the
printed values against the source file. The mapping above is now calibrated
against real exports from this account; if LinkedIn changes its export
format, re-run `--inspect` and patch `LABELS`/`DEMO_ROW_CATEGORIES`
accordingly.

## Vault note schema this feeds (per-post)

`ingest_xlsx.py --post` updates the `## Performance` table and
`## Audience snapshot` section of an **existing**
`cbrain/notes/LinkedIn-Posts/YYYYMMDD-slug.md` note in place — it never
creates a new post note from scratch (that happens when the post is
drafted/published, per [[linkedin-viral-scheduler]]). The exact table/bullet
format is unchanged from the existing convention (see any current note for
a worked example) so `build_dataset.py::parse_post()` / `parse_demographics()`
keep working on it unmodified, and the folder-watch auto-refresh in
[[linkedin-viral-scheduler]] picks up the update with no changes on that
side.
