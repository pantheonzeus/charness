# Method & Decisions — app-architecture reference

*Snapshot retrieved 2026-10-10. [F] = sourced fact · [F*] = canonical text, not re-fetched this run · [W] = secondary/doctrine without measured outcomes · [I] = inference/judgment. Raw research: `output/.runs/20261010-app-architecture-skill/children/methods/RESPONSE.md`.*

## 1. Size every decision before choosing its process
A decision is architectural if reversing it later is expensive [F*][^booch]. Classify each one by door type and blast radius [I, from Bezos[^bezos] and Wirfs-Brock[^wb]]:

| Size | Test | Record | Process |
|---|---|---|---|
| **S** | Two-way door, one team, < 1 sprint to reverse | PR description | Decide at ~70% of the information you'd like [F][^bezos] |
| **M** | Two-way door but cross-team, **or** 1 sprint–1 quarter to reverse | **Y-statement** ADR | Advice from affected teams |
| **L** | One-way door: data model of record, tenancy, public API/contract, persistence engine, identity provider, vendor lock-in, security boundary, team split | **MADR 4** ADR with a **Confirmation** section | Quality-attribute scenarios + risk-storm + ≥1 fitness function |

**Timing:**
- Use the **most responsible moment**, not the last [F][^wb]. Decisions ripple and take time to disseminate.
- **If ≥2 teams depend on an answer, its deadline is their start date** [I].
- Defer only one-way doors where an option-preserving seam is cheap.

## 2. Decision records that survive
- **Y-statement** (M decisions, and the one-line summary of every L decision) [F][^ystmt]:
  > In the context of ‹use case/component›, facing ‹concern›, we decided for ‹option› and against ‹alternatives›, to achieve ‹quality›, accepting that ‹downside›.
- **MADR 4.0** (2024-09-17) for L decisions [F][^madr].
  - **Front matter:** `status, date, decision-makers, consulted, informed`.
  - **Sections:** Context and Problem Statement · Decision Drivers · Considered Options · Decision Outcome → Consequences → **Confirmation** · Pros and Cons of the Options.
  - **House rule [I]:** an L-ADR with no automated or manual check in Confirmation is not accepted.
  - The ADR template shared with `cloud-architecture` (MADR-lite plus "Revisit when") is acceptable for M decisions.
- **YADR** (Zimmermann, Jun 2026) is MADR in schema-validatable YAML. It's useful when agents generate or check ADRs, but there's no adoption evidence yet [F][^yadr].
- **Store ADRs in the repo, next to the code** [F][^tw-adr][^adr-ar]. Wiki-stored docs are perceived as less useful.
- **Expect decay** [F][^adr-msr]. ~50% of GitHub repos that use ADRs hold only 1–5 of them. Review the ADR log quarterly; a log with no supersessions in 12 months is presumed stale [I].
- **Record advice received**, not just the decision (the consulted/informed fields) [F][^hl].

## 3. Governance: advice process over approval boards
- **One rule** [F][^hl][^hl-book]: anyone may make an architectural decision after seeking advice from everyone meaningfully affected and from people with relevant expertise. Consensus is not the goal.
- **Four supports:** ADRs, a weekly 1-hour Architecture Advisory Forum, team-sourced principles, and an internal tech radar.
- **Fits DORA** [F][^dora-lc]. The first loose-coupling predictor is that teams change their design "without the permission of somebody outside the team".
- **Preconditions:** trust and psychological safety. The named failure is **shadow architecture**: architects deciding behind the scenes [F][^hl].
- **Principles must be testable.** A principle with no example of what it forbids gets deleted [F][^hl][I].
- **When to use a review board instead:** an architecture review board is fine only where a regulator needs a named approver. A single architect deciding is fine below ~1 team or in the founding phase [I].

| Governance | Choose when | Avoid when |
|---|---|---|
| Advice process + forum + ADRs | Multiple autonomous teams, trust exists | Low psychological safety |
| Review board (approval) | Hard regulatory gate | As the default: it blocks teams |
| Single architect decides | Founding phase, ≤1 team | >2 teams: the architect becomes the bottleneck |

## 4. Quality attributes and evaluation
- **Quality-attribute scenarios** (SEI): source · stimulus · environment · artifact · response · response measure [F*][^atam]. No number, no requirement [I].
- **Risk-storming is the default review** [F][^risk]. Draw C4 diagrams, have each person mark risks *independently* on a likelihood × impact grid, then converge. Budget ~2 h.
- **Lightweight ATAM (½ day)** for L decisions with 3+ competing quality attributes [I from F[^atam]]:
  1. Build a utility tree of the top 5 scenarios.
  2. Walk the C4 container view.
  3. List risks, sensitivity points and tradeoffs.
  4. Write the ADRs.
- **Full ATAM/QAW** (multi-day workshops) only for safety-critical, public-sector or large procurement work [F][^atam].
- **Residuality** (Barry O'Reilly) is optional for high-uncertainty one-way doors [F][^resid]. List stressors (failure, user behaviour, regulation, vendor), check which parts of the design survive, and redesign until more of it survives. **No peer-reviewed validation exists**, so use it as a structured brainstorm, not as science.

## 5. Views and docs
- **C4 Context + Container are mandatory** [F][^c4]. Component diagrams only where they add value, and automated when long-lived. Never hand-draw code diagrams.
- **arc42** as the doc skeleton only for long-lived or audited systems [F*][^arc42]. Its section 9 links the ADRs and section 10 holds the quality scenarios. Otherwise use README + C4 + ADR log [I].

## 6. Fitness functions — how architecture is enforced
- **A fitness function** is "an objective integrity assessment of some architectural characteristic". It can be a test, a metric or a monitor [F][^tw-ff][^bea2].
  - Categories: atomic/holistic, triggered/continual, static/dynamic, automated/manual [F*].
- **Every L-ADR and every principle maps to ≥1 fitness function** [I][^madr]. The starter set is in [templates.md §4](templates.md).
- **Static boundary checks are necessary but not sufficient** [F][^packwerk]. Shopify had zero-violation packages that crashed when run alone. Pair dependency rules with a test that **boots each module in isolation**.
- **In 2026, fitness functions are the leash for AI coding agents** [F][^tw34]. Thoughtworks Radar Vol 34 (Apr 2026) themed "putting coding agents on a leash" with fitness functions as invariants. It also notes that agents *accelerate* architecture drift: "poor code begets poorer code".

## 7. Socio-technical inputs
- **Design for independent change and deploy, not for service count** [F][^dora-lc]. DORA's loose-coupling items:
  1. Change design without outside permission.
  2. Finish work without fine-grained coordination.
  3. Deploy independently.
  4. Test on demand without an integrated environment.
  5. Deploy in business hours with negligible downtime.

  As DORA puts it: "possible… with mainframe technologies… possible to fail… with the latest, most trendy technologies."
- **Team cognitive load is a first-class input** [F][^tt][I]. Team Topologies 2e (Sep 2025) keeps fast flow and cognitive load at its core. If one stream-aligned team owns more than one complex subdomain plus its platform plumbing, split the boundary or buy the plumbing.
- **Org structure predicts defects** [F][^vista]. On Windows Vista, organizational metrics beat churn, complexity and coverage as failure predictors. Review ownership seams alongside module seams.
- **Conway mirroring is common, not law** [F][^mirror]. It held in ~69% of 142 studies but was weak in open, collaborative software. Don't reorg purely to force an architecture; allow knowledge overlap across module owners.

## 8. Build vs buy
- **Place each component on the Wardley evolution axis** (Genesis → Custom → Product → Commodity) [W][^wardley]:

  | Stage | Source it by |
  |---|---|
  | Genesis | Build, as an experiment |
  | Custom | Build only if it differentiates |
  | Product | Buy or OSS |
  | Commodity | Consume as a utility |

  This is doctrine, not measured outcomes.
- **Build-vs-buy is itself an ADR**, usually an L decision because data lock-in is one-way. Its "accepting that" clause states the exit cost: data export, contract term, API lock-in [I]. Do the cost arithmetic as licence vs FTE-months.

## 9. Positions the evidence challenges — carry them honestly
- **Monolith-first is contested** [F][^tilkov]. Tilkov argues that retrofitting boundaries is hard, so build subsystems independently from day one. The answer is a modular monolith **with enforced module fitness functions from commit 1** [I].
- **The cases are anecdotes.** Segment and Prime Video are n=1 each and self-reported. DORA is style-neutral and supports *loose coupling*, not "monolith" [F][^dora-lc].
- **DORA is cross-sectional survey data**: "predicts" means associated, not caused [I].
- **Thoughtworks' ADR and fitness-function blips date from 2017–18** and are off the radar because they are mainstream, not outdated [F][^tw-adr][^tw-ff]. The 2026 radar re-invokes fitness functions for AI agents.

## 10. Anti-patterns (each is a review finding)
1. **Microservice envy** / distributed by default [F][^tw-modulith].
2. **Fake SOA**: services that can't be tested or deployed independently [F][^dora-lc].
3. **Imposed semantic boundaries** that don't match how the code runs [F][^packwerk].
4. **Shadow architecture**, or an ivory-tower review board [F][^hl].
5. **ADR graveyard** [F][^adr-msr], and **unverifiable decisions** (no Confirmation, no fitness function) [F][^madr].
6. **Last-moment paralysis**: the "last responsible moment" used as an excuse [F][^wb].
7. **AI throughput illusion**: local speed up, delivery stability down [F][^dora-lc].
8. **Reorg-to-force-architecture** [F][^mirror].
9. **Diagram overproduction**: hand-maintained component/code diagrams that rot [F][^c4].

## Sources
[^booch]: Grady Booch, "architecture represents the significant design decisions… where significant is measured by cost of change" (canonical quote, not re-fetched)
[^bezos]: https://www.aboutamazon.com/news/company-news/2016-letter-to-shareholders
[^wb]: https://wirfs-brock.com/rebecca/blog/2011/01/18/agile-architecture-myths-2-architecture-decisions-should-be-made-at-the-last-responsible-moment/
[^ystmt]: https://medium.com/@docsoc/y-statements-10eb07b5a177
[^madr]: https://github.com/adr/madr (template: https://raw.githubusercontent.com/adr/madr/main/template/adr-template.md)
[^yadr]: https://ozimmer.ch/practices/2026/06/19/YADRTemplateIntroduction.html
[^tw-adr]: https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records
[^adr-ar]: https://conf.researchr.org/details/ecsa-2024/ecsa-2024-research-papers/9/Introducing-Architecture-Decision-Records-in-Practice-An-Action-Research-Study
[^adr-msr]: https://research.jku.at/en/publications/using-architecture-decision-records-in-open-source-projects-an-ms/
[^hl]: https://martinfowler.com/articles/scaling-architecture-conversationally.html
[^hl-book]: https://www.thoughtworks.com/insights/books/facilitating-software-architecture
[^dora-lc]: https://dora.dev/capabilities/loosely-coupled-teams/ · AI numbers: https://www.infoq.com/news/2024/11/2024-dora-report/
[^atam]: https://apps.dtic.mil/sti/pdfs/ADA413696.pdf
[^risk]: https://riskstorming.com (via https://icepanel.io/blog/risk-storming)
[^resid]: https://gotopia.tech/books/120/residues-time-change-and-uncertainty-in-software-architecture
[^c4]: https://c4model.com/ · https://c4model.com/diagrams/component
[^arc42]: https://arc42.org (not re-fetched)
[^tw-ff]: https://www.thoughtworks.com/radar/techniques/architectural-fitness-function
[^bea2]: https://www.thoughtworks.com/insights/books/building-evolutionaryarchitectures-second-edition
[^packwerk]: https://railsatscale.com/2024-01-26-a-packwerk-retrospective/
[^tw34]: https://www.thoughtworks.com/radar/techniques/architecture-drift-reduction-with-llms · https://www.thoughtworks.com/insights/podcasts/technology-podcasts/themes-technology-radar-34
[^tt]: https://itrevolution.com/book/team-topologies/
[^vista]: https://api.crossref.org/works/10.1145%2F1368088.1368160
[^mirror]: https://dash.harvard.edu/bitstream/1/33785675/1/colfer,baldwin_mirroring-hypothesis.pdf
[^wardley]: https://www.barkingiguana.com/writing/wardley-mapping (secondary; primary: Simon Wardley, *Wardley Maps*)
[^tilkov]: https://martinfowler.com/articles/dont-start-monolith.html
[^tw-modulith]: https://www.thoughtworks.com/radar/languages-and-frameworks/spring-modulith
