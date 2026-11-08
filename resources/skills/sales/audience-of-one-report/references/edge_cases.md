# Edge Cases and Failure Modes

Read the section that matches your situation. Skip the rest.

**Contents:**
1. When the user wants to skip all questions
2. When the stakeholder has a low public footprint
3. When the user vaguely pushes back on the persona or design decisions
4. When a data-layer file the user uploaded isn't right
5. When the user requests sales content
6. Handling reputational signals
7. Common failure modes — checklist

---

## 1. When the user wants to skip all questions

If the user says *"just generate it, don't ask questions"* up front, apply the **default-and-announce protocol**:
- Build the persona in Step 2 from LinkedIn + a quick web pass.
- **Do not skip Step 3 silently** — present the persona in one compact block (4 bullets: focus areas, benchmarks, pain points, vocabulary register) and say: *"Building from the persona below. Speak up now if any of this is off — otherwise I'll proceed to design decisions."* Wait one exchange; if no pushback, proceed.
- Build the 10 DDs, present TL;DR + full set in one block, same announce pattern.
- Default narrative-layer source plan; data layer defaults to narrative-only (flag in method note if they'd rather wait for a file).
- In the Methodology, note: *"Persona and design decisions auto-derived; not user-confirmed."*

**Do not skip the persona-and-DDs step entirely** — the "skip" the user wants is the back-and-forth, not the thinking.

---

## 2. When the stakeholder has a low public footprint

Low footprint = thin LinkedIn About + no interviews + no analyst coverage + no talks + no writing. Common with private-company execs, mid-level roles, or highly-regulated-industry execs who avoid a public profile.

**The cost is high** — a thin persona means Step 4A leans on inference, risking a generic brief with a name on top. **Before Step 4A, tell the user** and offer three options: (a) *you fill the gaps* (their top 2–3 priorities, who they benchmark against, vocabulary they use/avoid — capture tagged "from user, not public source"; these improve the brief disproportionately); (b) *proceed with a thin persona*, flagged prominently in Methodology; (c) *I draft 2–3 candidate DD sets each on a different plausible reading of the role, you pick*.

---

## 3. When the user vaguely pushes back

If a Step 3 response is *"doesn't feel right"* / *"not quite them"* without specifics — don't ask "what's wrong?" (that puts the work on them). Offer a **multiple-choice clarifier**: (a) focus areas — wrong/weighted wrong; (b) benchmark set; (c) pain points — not on their desk; (d) vocabulary register — too technical / not enough; (e) something else. Same pattern at Step 4A on DDs (subjects / angle / narrowing / register / reader-question mapping / other). Apply the answer narrowly to the named axis — don't re-do everything.

---

## 4. When a data-layer file isn't right

Run the ETL-2 relevance check before analysis. Three failure modes: **wrong subjects** (file covers different companies than DD1), **wrong type** (employer-internal data, not evidence about subjects), **wrong granularity** (summary deck where row-level was needed). Don't silently push through — push back with a specific assessment and three options: (a) skip data layer, narrative-only (flagged); (b) point me at the relevant part; (c) upload a different file (I can wait). **Internal employer data** can feed the Methodology as "internal context" rather than being rejected outright.

---

## 5. When the user requests sales content

The brief stays restrained. If the user wants outreach copy / talking points / a one-pager, use the **companion-doc pattern**: *"The brief is a quiet intelligence product; I can produce a separate companion doc with ready-to-send content — (a) outreach message, (b) talking-points doc tied to findings, (c) both. The brief stays clean; the companion carries the sales motion."* Anchor each talking point to a specific named finding in the brief ("Open on Astris's 16,000 deployed agents, Section 2..."). Don't write talking points that aren't traceable to the brief.

---

## 6. Handling reputational signals

**(a) About the stakeholder personally** (regulatory action, controversy, criticism) — because of the HARD RULE these **do not appear in the brief body**. One flagged sentence in Methodology; also tell the user in chat separately.
**(b) About a subject** (material regulatory action, restatement, scandal, exec departures affecting the angle) — *can* appear in the body if it materially shapes what the subject says vs does. Include only if named in ≥2 reputable sources, directly affecting the angle, recent enough to matter. Frame neutrally and source explicitly ("the SEC notified the company in March 2026...") not "another scandal."

---

## 7. Common failure modes — checklist

### Stakeholder bleed-through (#1, most common)
Any of these in the body is a cut: quoting the stakeholder directly; biographising them; invoking their prior public statements ("connects to [Name]'s December 2025 framework"); addressing them obliquely ("for someone in [Name]'s position"). Find-on-page for surname + first name before generating the PDF — **zero matches anywhere**.

### Brief reads as generic — fails the "another exec at the same company" test (#2)
Four diagnostics: subjects aren't narrowed (DD7); findings don't trace to a pain point (DD8); forward calls are all generic industry forecasts (DD5 — need ≥1–2 implicit-reader); vocabulary is generic press-release register (DD6). The fix is almost never adding more "[BU] read." paragraphs.

### "[BU] read." as directive translation (#3)
Telling the reader what findings mean for them ("X is the reference for your Y programme") breaks implicit targeting. Use *situational contrast* (EU vs US manufacturer tariff exposure) and let the reader draw the implication.

### Too many "[BU] read." paragraphs (#4)
Reference uses it twice in eleven sections. More than 2 usually means the rest of the brief isn't doing the audience-of-one work — fix by re-narrowing subjects and re-selecting findings, not by adding callouts.

### Genre and tone failures
Reads like a sales memo ("we recommend", "lead with") outside Section 9 → cut. Talking-point scripts in quotes → cut, offer companion doc. Adjectives without evidence → numbers and named programmes beat adjectives. Wall of bullets → prose-first.

### Structural arrangement wrong for data type or reader (#5)
Forced company-first on narrative-only data (B's "what data shows"/"where diverges" collapse); forced theme-first on a deep-comparison reader; quadrant-first with no genuine 2-axis question; capability-first without a CIO/COO/capability-build reader. If caught mid-draft, name the issue and offer a switch rather than pushing through.

### Visual overload or under-investment (#6)
Overload: 10+ visuals reads as a deck. Under-investment: only 1–2 (or none beyond stat blocks) — particularly damaging for visual-scanner readers. Wrong device for processing style. Match DD9/DD10 to persona §6 explicitly. If a render library fails, degrade (matplotlib → styled table → prose) and flag in Methodology; never invent data to fill a chart.

### Sourcing failures
Persona quotes leaking into body (research input, not body content). Snippet-only sources (use `web_fetch` for the full page). Single-source claims for material assertions (2+ named sources). Fabricated/misquoted attributions (Gate 1 quote-verify is non-negotiable — a single misquote, once spotted, costs the brief's credibility). **Stakeholder bleed-through past the surface** — *invocations without naming* ("the December framework", "the internal AI factory") when those are programmes only the stakeholder has publicly described; if genuinely public (press release, news), naming is fine, otherwise it's bleed-through in spirit.
