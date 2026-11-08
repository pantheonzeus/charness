# Gate implementations — `audience-of-one-report`

The **verification machinery**: full implementations of the seven pre-render gates, the §8 completeness audit, the §9 render-inspection, and the §10 data-integrity sub-checks. Split out of SKILL.md (v6.16) so the spine stays readable; SKILL.md carries the *loud trigger* for each gate, the *implementation* lives here.

**Read contract.** Read this at two points: **at the Step 5 → Step 6 boundary** run **§7** (data-completeness — a FAIL sends you back to Step 5); **before render on the finished embedded draft** run **§2 → §1 → §3 → §4 → §5 → §6** in that order, then **§8**. Paste each gate's actual output. For §6 sub-A you MUST paste the `IMG_COUNT` line. Each gate leaves a one-line trace in `/home/claude/audit_log.md`; §8 greps for every required trace and blocks render if one is missing — that is how the interaction-only checkpoints (mode / Step 3 / DD1 / delivery) are enforced. **Do not paraphrase the code** — it was hardened against specific observed failures (e.g. `grep -c` → `grep -o … | wc -l` for the visual-floor pass). Adapt only the marked per-brief variables.

---

## Gate 1 — Quote-verify (the rigour gate)

Every direct quote in the body must trace to a source Claude fetched and verified. Maintain `/home/claude/quotes.json` **incrementally during drafting** (append `{"quote","speaker","source_url","cited_date","source_date","outlet","draft_section","slot","subject","speaker_affiliation"}` per quote) — not end-of-draft regex extraction, which misses reverse-attribution, line-break-spanning quotes, and smart-quote mismatches.

**Four-check verification per quote (all four must pass):**
| Check | Verifies | Pass criterion | Catches |
|---|---|---|---|
| 1. Text | quote appears in source | full-quote substring (case-insensitive); first-8-words fuzzy = FUZZY not PASS | hallucinated / partially-fabricated quotes |
| 2. Speaker | source attributes it to the named speaker | "[Speaker] said/told/stated/…" within 200 chars, OR reverse, OR interview colon "Speaker:", OR institutional entity + corporate-comms marker | misattribution (right phrase, wrong/no speaker) |
| 3. Date | pub date matches citation | same month (YYYY-MM); year-only mismatch = HARD FAIL | wrong-date citation |
| 4. Speech-act | presented as direct speech, not paraphrase/marketing | speech verb within 100 chars (5 patterns: forward, reverse, interview-colon, multi-sentence guillemet, institutional) | marketing-copy re-presented as a CEO's words |

The script (`/home/claude/quote_verify.py`) runs all four against fetched content, handling five real-world attribution patterns (forward, reverse, interview-colon, multi-sentence direct quote, institutional source); a single-pattern regex false-FAILs on patterns 2–5. Decision rules: **PASS (4/4)** stays; **FUZZY** rewrite to source's exact wording, re-run; **FAIL on any check** remove or convert to paraphrase without quotation marks (Text FAIL → remove; Speaker FAIL → find right attribution or present as institutional without quotes; Date FAIL → correct the date or remove; Speech-act FAIL → paraphrase, attribute to the company not the executive). Source preference: primary (newsroom/press release/transcript/filing) → interview/talk transcript → news article. **Special cases:** paywalled → don't quote (find a public reproduction or paraphrase); translated → verify against original-language source, note "(translated)"; stakeholder quotes never appear (Gate 2's job if one slipped in). Trace: `Gate 1: N quotes, all 4-check verified` (name any removed/rewritten).

## Gate 2 — Stakeholder-placement audit (HARD RULE enforcement)

Grep the draft (format-agnostic — point at `.html`/`.md`/`.tex`) for the stakeholder's surname + first name.
```bash
SURNAME="Renner"; FIRST_NAME="Alex"; DRAFT="/home/claude/brief_draft.html"; MODE="a"
grep -c -i "$SURNAME" "$DRAFT"; grep -c -i "$FIRST_NAME" "$DRAFT"
grep -n -i "$SURNAME\|$FIRST_NAME" "$DRAFT"
```
**Pass — mode (a):** zero matches (body, header, metadata all clean). **Mode (b):** matches confined to the header region + at most one short opening framing paragraph (first ~30 lines); any name in deep dives / findings / forward calls / methodology / callouts = fail (convert to business-unit references or remove). Direct stakeholder quotes never appear in any mode. Most common bleed-through: "[Name]'s framework/programme" → rewrite to the programme name without the stakeholder's name, and only if the programme is publicly disclosed by the company. Trace: `Gate 2 (mode a|b): N matches, all in [location]`.

## Gate 3 — Self-run audience-of-one test (the "wrong reader" simulation)

Pick the most plausible alternative reader at the same company; read the first two pages *as that wrong reader* (does the exec-summary framing fit their decision space? do headline findings name programmes they care about? does the angle speak to their pain points? is the vocabulary in their dialect?). Score: **PASS** (wrong reader thinks "this isn't for me"), **AMBIGUOUS** (could plausibly be for them — too generic; tighten DD7 + DD8), **FAIL** (wrong reader is a more natural audience — DD1 subjects or DD2 angle wrong, back to Step 4A). Must pass on subject narrowing + finding selection + forward calls alone, without relying on [BU] read paragraphs. Trace: `Gate 3: wrong-reader [role] would [pass]; carried by [narrowing/findings/forward calls]`.

## Gate 4 — Reader-org-fit test (the personalisation floor)

```bash
DRAFT="/home/claude/brief_draft.html"; BU_NAME="Power Systems"; BU_READ_MARKER="$BU_NAME read."
PROGRAMME_1="Signature Analyzer"; PROGRAMME_2="MCSS"
grep -c -i "$BU_READ_MARKER" "$DRAFT"      # target ≥2, ideally 2–4
grep -c -i "$BU_NAME" "$DRAFT"             # target ≥3 distinct sections
grep -c -i "$PROGRAMME_1" "$DRAFT"         # target ≥2
grep -n -i "$BU_NAME" "$DRAFT" | head -20  # distribution check
```
**Pass (all four):** (1) ≥2 "[BU] read." paragraphs; (2) BU name across ≥3 distinct sections (not clustered); (3) each reader-named public programme appears ≥2×; (4) reader's-employer subject deep dive BU-narrowed (group-level content only as ≤1 paragraph of context). Failure handling per floor (add paragraphs / spread / surface the programme in Frontier + a deep dive / rewrite to BU-narrow, usually cutting 50–70% of group material). Gate 3 passes without [BU] read paragraphs; Gate 4 enforces the v5 floor *on top*. A brief that passes 3 but fails 4 is "implicitly targeted but reads insufficiently customised." Trace: `Gate 4: N [BU] read. paras; BU across X sections; programmes Y; deep dive BU-narrowed`.

## Gate 5 — Artefact separation audit (Methodology cleanliness + audit-log presence)

Sub-checks (A, B, D must PASS; C is a warning): **A** — `audit_log.md` exists and is ≥800 bytes; **A2** — it carries a Step 5 coverage trace (catches "Step 5 skipped, Gate 7 self-passed"); **B** — the Methodology section (regex-extracted from the `<h2>…Methodology…</h2>` block) contains **zero** forbidden vocabulary; **C** — Methodology ≤ ~900 words (warn if over — QA leaked in; warn if <100 — too thin); **D** — a Methodology section exists (empty regex = FAIL, not a free pass).

The forbidden list (FIXED — **do NOT modify in-session**): `Gate 1..7`, `coverage matrix/coverage_matrix`, `rungs_tried`, `data-completeness`, ` PASS`/` FAIL`, `audit gate`, `audit log`, `wrong-reader`, `stakeholder-placement`, `stakeholder-absence`, `audience-of-one test`, `personalisation floor`, `implicit targeting`, `design decision`, `DD1..DD10`, `v5/v6 convention`, `four-check verification`, `wrong-reader archetype`. Never silently expand it mid-session (that self-modifies the audit). If a phrase fires that you think is legitimate, it isn't — move the sentence to the audit log and rewrite the Methodology in buyer-facing language. Trace: `Gate 5: audit_log present (N bytes); Methodology clean (0 matches), N words`.

## Gate 6 — Content integrity audit (visual floor + frontier anchoring + quote attribution + programme provenance)

```bash
DRAFT="/home/claude/brief_draft.html"
IMG_COUNT=$(grep -o '<img ' "$DRAFT" 2>/dev/null | wc -l)   # sub-A — PASTE THIS LINE
```
**A — visual floor:** ≥1 `<img>` pointing to a non-table primary visual (a brief whose only visuals are stat blocks + styled tables fails). **B — frontier programme anchoring:** the Frontier section references ≥1 of the reader's named (public) programmes — abstract "AI governance" without naming the actual programmes is a DD4 regression. **C — quote attribution:** each subject's "saying"-slot quote is from a person whose affiliation includes that subject's own org (not a partner/customer/analyst — the documented failure was Safran's saying-slot quote attributed to an AWS MD); verified via `quotes.json` `subject`/`speaker_affiliation`. **D — programme provenance (anti-fabrication, v6.8):** every named programme in persona/company-brief/body exists in `programmes.json` at `high|medium` confidence with a source URL; a heuristic flags capitalised programme-like phrases with no registry entry (triage: real → add with URL+quote; common-noun → extend SAFELIST; fabrication → remove). Auto-FAIL if any flagged candidate is asserted as a real programme attributed to a specific employer without a URL. Trace: `Gate 6: N visuals; Frontier names N programme(s); saying-slots clean; programmes provenance OK`.

## Gate 7 — Data-completeness audit (the anti-laziness gate)

Reads `coverage_matrix.json` at the Step 5 → 6 boundary. A Python script verifies: (1) the file exists (else Step 5 close-out skipped — HARD FAIL); (2) every (subject × target) cell is in an allowed end-state — `collected` (with evidence + source_urls), `partial`/`exhausted` (with `rungs_tried` ≥2), or `n/a` (with reason); a `missing`/blank cell or a `partial`/`exhausted` with no `rungs_tried` is HARD FAIL (ladder skipped); (3) no `collected` cell without evidence; (4) **substance check** — the gate builds a provenance substrate from every URL in `sources.json` **and** `subject_metrics.json`; when non-empty, every `collected` cell's `source_urls` must match something in it (a tidy matrix that corresponds to nothing fetched is HARD FAIL), and a `collected` subject missing from `subject_metrics.json` is a WARN. **Structural guard:** `subject_metrics.json` must be a LIST of `{subject:...}` objects — a dict keyed by subject name makes the subject-backing check vacuous, so it FAILs loudly. With no provenance anywhere, the gate degrades to form-only mode and says so. **Do not "remediate" by downgrading a cell to `n/a`** without a genuine reason. Trace: `Gate 7: N collected, M partial/exhausted (ladder), K n/a, across [dimensions]`.

---

## §8 — Completeness audit (trace verification + delivery-message check)

Run **last**, after the six pre-render gates left their traces and after drafting the hand-off to `delivery_message.txt`. A bash script (`check_trace`) greps `audit_log.md` for each required checkpoint: **Mode** recorded; **Step 3 persona confirmation** (with the user's actual response text — showing the DD1 chooser does NOT satisfy this; near-empty trace <40 bytes FAILs); **DD1 subject set chosen**; **Step 5 coverage trace**; **Gate 1–7** results; **critic pass** (Stage 6.5 / CP7, generative — a trace with no critique + no edits hasn't happened); **render-inspection** (CP9); **delivery message checked**.

**Delivery-message check:** `delivery_message.txt` exists, ≤ ~40 words (hard-fail >60 — it's narrating, not handing off), and free of build-narration markers. The seven markers: `the angle`, `the spine`, `how it was built`, `i dropped`, `i swapped`, `makes the punchline`, `the centerpiece`. **Deliberately excluded:** `page`/`read.`/`implicit` — they false-fire on a clean hand-off ("15 pages", "cross-read"); page-count over-talk is caught by the length check, not a keyword. **Failure handling:** a missing trace is remediated by *running the step that should have produced it*, not by writing the trace (that re-opens the drift). 

**Then hand CP8 to the completeness gate (v7.7):** after §8 PASS, run `bash completeness_gate.sh pre`. It re-extracts §10-A/B/E/F, re-runs each against live `headline_claims.json`/`chart_basis.json` (ignoring any logged verdict), requires each input artifact to exist and each gate to pass, and only then ticks **CP8** itself. Non-zero exit = a §10 gate was skipped, its artifact is missing, or it FAILs — fix it; do not tick CP8 by hand. (Guard against RC-6, the healthcare-sector run where §10-A/C/F never executed yet CP8 was self-ticked.)

## §9 — Render-inspection (per-page layout + brand QA; pre-delivery hard gate; CP9)

Brackets the render: **Step 0 before render (prevention), Steps 1–4 after (detection + inspection + final clear).** None of the gates or §8 looks at the *rendered pages*.

**Step 0 — font readiness (BEFORE rendering, v7.2).** The pack font silently falling back to a system sans is the single most common brand-fidelity failure (how the Verda brief shipped entirely in Liberation-Sans). Do both: (1) install the pack font into fontconfig (`cp` the TTF to `~/.fonts`, `fc-cache -f`) so any renderer finds it; (2) for WeasyPrint, instance the variable font to **static Regular(400)/Bold(700)** (its default instance is ExtraLight — too light for body, and single-VF weight selection is unreliable) and `@font-face` each weight. Register the same static TTFs for charts (`font_manager.addfont` + `rcParams["font.family"]=<palette font.family>`) so figure text matches the body. Then the render embeds the pack font on the first pass; Step 1's `pdffonts` confirms it.

**Step 1 — mechanical adjuncts:** `pdffonts "$PDF"` (expect the pack font embedded, no serif fallback); `pdftoppm -png -r 120 "$PDF" /tmp/pg/page` (rasterise every page).

**Step 2 — view EVERY page image** (`view` tool, not spot-check) against the checklist. **Layout integrity:** no clipped/cut-off/overflowing text, charts, tables; in every visual no colliding/overlapping labels, legend not on data, axis labels legible; no blank/half-blank pages, no orphaned headings; **no under-filled pages** (a numbered section alone on a >40%-blank page is a density failure — relax the per-section page break, hit the 5–8 dense-page target); tables fit column width; **subject-set integrity** (subject dots == subject rows == the declared subject count; if the stakeholder is shown it's a distinct marked "you are here" point, not a silent sixth peer); headers/footers intact. **Brand fidelity:** type is the pack font (not fallback); colours are the pack palette (no default matplotlib C0/C1, no stray pure-black where brand ink is specified); charts carry `charts.md` styling; margins/grid/heading-scale correct; wordmark correct asset, not distorted; **"[BU] read." renders as an inline paragraph, NOT a tinted/bordered callout box**.

**Step 3 — fix and re-inspect:** fix at source, re-render, re-rasterise, re-view. Trace to the audit log; tick CP9. **When compressing to kill a stranded page, cut by usefulness, not by what's easiest to delete (v7.7)** — merge prose and drop decorative/restating visuals first; a *load-bearing* chart (timeline cadence, matrix position, distribution shape, cross-read pattern) must survive; if the real choice is keep-the-figure vs add-a-page, keep the figure and add the page (only the terminal page may run short).

**Step 4 — final clear (run_state all-ticked):** every checkpoint `[x]`; any unticked `- [ ]` line FAILs and blocks delivery. **Then hand CP9 to `bash completeness_gate.sh post`** — it requires the rasterised pages, re-runs §10-C against them, blocks on any stranded non-terminal page, confirms the render-inspection trace + every earlier box ticked, and only then ticks CP9 and clears delivery. A FAIL here blocks *delivery*, not render — fix and re-render as needed.

---

## §10 — Data-integrity & render sub-checks (v7.4+)

Mechanical backstops for `references/data_render_doctrine.md`. Run **§10-A/B/E/F** at the Step 5 → 6 boundary (with Gate 7) and **§10-C** after render (with §9). `completeness_gate.sh` re-runs each against the live on-disk artifact and is the only thing that ticks CP8/CP9 — a skipped or hand-asserted §10 gate cannot reach delivery; an absent input artifact is itself a CP8 FAIL. Build `headline_claims.json` and `chart_basis.json` as you draft.

- **§10-A — second_source + source_tier on headline / centerpiece / reference-negative claims.** Each such value needs a **comparable-basis** `second_source` (a different lens reaching the same read, not a restatement) **and** at least one `primary`-tier source of the basis + second_source (they may not both be `secondary`/`inferred`). Untagged tiers = FAIL. Maintain `headline_claims.json` (`{claim, kind, basis, basis_tier, second_source, second_source_tier}`). Trace: `§10-A: N claims; all carry comparable second_source + ≥1 primary-tier source`. *(The gate that would have stopped Meridian's filtered `0/38` anchoring the exec stat strip.)*
- **§10-B — one axis, one basis.** Every entity on a shared chart axis shares one basis (source/window/denominator/universe); an off-basis entity goes in a separately-labelled panel (`panel_separated:true` in `chart_basis.json`), never as a comparable bar. Trace: `§10-B: N charts; all single-basis or panel-separated`.
- **§10-C — page-fill floor.** Rasterise every page (`pdftoppm -png -r 100`), measure body-fill %; flag any non-terminal, non-section-break page below ~70% (usually a whole section wrapped in `break-inside:avoid` instead of just its charts/boxes/closers). Trace with page list.
- **§10-D — critic probe (CP7) + render-path pre-flight.** The critic must ask: is any headline stat / spine claim / centerpiece visual resting on a small-base or single-proxy reading, especially for the reference entity? And: does every superlative/comparative carry its peer baseline + base n? **Prose-superlative vs own-chart consistency** — for every "the most/only/-est/than any/leading/benchmark" in prose, check the matrix/heatmap coding; if two+ subjects share the top band, a *singular* superlative is false against your own figure (reword to "among the most…", name the tie, or drop it). Probe the render path once before promising an artifact. External scrapes: read-and-extract immediately (≤30-item chunks, persist the tally), check quota, cap each run. Imported/pasted findings are leads to re-verify in-run, not fetched sources.
- **§10-E — subject-set integrity.** Every entity plotted in a subject-positioning figure is **either** a developed subject (profile in `subject_metrics.json`) **or** the stakeholder explicitly flagged `"role":"stakeholder"`. An unflagged entity matching `run_meta.json`'s `exclude_from_subjects` (the stakeholder/employer) = FAIL (unmarked-peer masquerade); the same entity flagged `role:stakeholder` PASSes. Register the positioning matrix + posture heatmap in `chart_basis.json` with `"subject_figure":true`. Trace: `§10-E: N subject-figures; every plotted entity is a developed subject or a flagged stakeholder`. *(The gate that would have caught the Owned-Audience brief (RC-3) plotting the stakeholder's employer as an unmarked sixth dot.)*
- **§10-F — comparative-claim grounding (v7.6).** Any claim tagged `comparative:true`, any `kind==reference_negative`, and any unambiguous magnitude superlative (largest/smallest/thinnest/highest/benchmark/"more than any") carries a `comparison` block `{subject_value, peer_baseline, n}` in `headline_claims.json` — "Meridian senior-IC 0/38 vs peer median 14%", not "the thinnest"; "13.08M, next-largest materially smaller", not "the largest". Untagged-but-superlative wording = WARN; a comparative on n<~8 = NOTE (frame directional, not headline). The soft regex deliberately excludes ordinal/vague words (first/only/most/leading) — they fire constantly on legitimate news prose; a genuinely comparative use of those is caught by tagging `comparative:true`, not the regex. Trace: `§10-F: N comparative/reference-negative claims; all carry subject value + peer baseline + n`.
