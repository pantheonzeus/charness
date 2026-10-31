# Quality Foundations & EU Compliance — app-architecture reference

*Snapshot retrieved 2026-10-10. [F] = sourced fact · [F*] = canonical source cited from prior knowledge, not re-fetched · [W] = weak/vendor/survey · [I] = inference/judgment. Raw research: `output/.runs/20261010-app-architecture-skill/children/quality/RESPONSE.md`.*

## 0. Why this section is non-negotiable (the evidence)
- **Quality is speed** [F][^codered]. Unhealthy code has **15× more defects** and takes **124% longer** on average to change (up to 9× longer max). The data comes from 39 codebases (Tornhill & Borg 2022). "Time-to-market beats perfection" holds for *scope*, not for code health.
- **Debt has a measured tax** [F][^besker]. Developers lose ~23% of their time to technical debt (Besker/Martini/Bosch).
- **AI coding amplifies whatever system it lands in** [F][^dora24][^dora25][^metr][^veracode][^gitclear]:
  - DORA 2024: more AI adoption came with −1.5% throughput and −7.2% stability.
  - DORA 2025: throughput rises but instability still rises; only 2 of 7 team archetypes gain without losing stability.
  - METR RCT: experienced developers were 19% slower on mature repos while believing they were 20% faster.
  - Veracode: AI picked the insecure option in 45% of tasks.
  - GitClear: 8× more duplicated code blocks.

  **Implication:** fast CI, small batches, enforced boundaries and SAST gates are the *prerequisite* for getting value from AI coding agents [I].

## 1. Delivery baseline
| Item | Default | Source |
|---|---|---|
| Branching | Trunk-based: ≤3 active branches, everyone merges ≥1×/day, branches live hours | [F][^tbd] |
| Metrics | DORA **five**: deploy frequency, lead time, change failure rate, failed-deploy recovery time, **rework rate** (new 2025). No elite/low tiers: DORA 2025 replaced them with archetypes | [F][^dora5] |
| CI budget | ≤10 min to green on trunk. Rollback is one command. PR size capped | [I] |
| AI coding rollout gate | Only after the CI budget, one-command rollback and PR caps hold. Watch change-failure and rework rate monthly as adoption rises | [I] from DORA AI Capabilities Model[^dora-ai] |
| Priorities | Stable priorities are a measured capability; designs needing cross-team coordination for every priority shift are a smell | [F][^dora24] |

## 2. Test strategy — shape follows architecture
No rigorous study compares the ROI of pyramid, trophy and honeycomb, so pick by the system's failure locus [F: absence of evidence].

| Option | Choose when | Avoid when |
|---|---|---|
| Pyramid (many unit) | Logic-heavy core, libraries, calc engines | UI-heavy apps where bugs live in wiring |
| **Trophy** (static types/lint → unit → **integration-heavy** → few E2E) | **Default for server-rendered web apps and modular monoliths** | Pure algorithmic code |
| Honeycomb | Many services with real I/O boundaries | Monoliths |
| Consumer-driven contract tests (Pact) | Independently deployed services, public APIs | In-process modules: use boundary fitness functions instead |
| E2E browser tests | 3–10 revenue-critical journeys only | As the primary safety net |
| Mutation testing, diff-scoped | Critical modules | Whole-repo nightly runs |

Rules:
- **Flakiness scales with size** [F][^flaky]. At Google, 0.5% of small, 1.6% of medium and **14% of large** tests were flaky. Quarantine within 24h and keep a flake budget (<1% of runs) [I].
- **Coverage is a floor, not a target** [F][^coverage]. Once suite size is controlled, coverage correlates only weakly with fault detection. Gate on *changed-line* coverage, not a global 90%.
- **Diff-scoped mutation testing works** [F][^mutation]. Google surfaces mutants in code review, and 38% of them get resolved by code or test changes.
- **Real dependencies in integration tests** (Testcontainers, ephemeral Postgres) beat in-memory fakes for DB-bound logic [I].

## 3. Observability by design
- **OpenTelemetry is the default** [F][^otel]. Traces are stable with LTS, the logs bridge is stable, metrics API/protocol are stable, and profiles are still in development. Keep your logging library and emit OTLP via the bridge.
- **Structured logs** carry trace/span IDs on every line. Redact PII in the OTel collector, because PII in telemetry becomes undeletable GDPR liability [I].
- **App SLOs per user journey**: 2–4 SLIs (availability, p95/p99 latency, correctness/freshness) with an error-budget policy. Set targets from measured performance, not aspiration [F*][^sre].
- **Budget the cost** [F][^grafana]. Observability runs a median 10% (mean 17%) of infra spend. Use tail sampling for errors, cardinality caps and retention tiers.
- **Logging is a security control** [F][^top10]. OWASP Top 10:2025 lists A09 Logging & *Alerting* and A10 Mishandling of Exceptional Conditions. Fail closed, and alert on authz failures.

## 4. Security by design
| Item | Default | Source |
|---|---|---|
| Requirements standard | **OWASP ASVS 5.0** (May 2025, ~350 reqs). **L1** for every internet-facing app, **L2** for personal/financial data, B2B SaaS or NIS2-customer suppliers, **L3** for payments core, health and critical infra | [F][^asvs] levels [I] |
| Awareness | OWASP Top 10:2025: A01 Broken Access Control · A02 Misconfiguration · **A03 Software Supply Chain (new, highest exploit/impact)** · … · **A10 Exceptional Conditions (new)** | [F][^top10] |
| Threat modeling | The four Manifesto questions, 30–60 min per epic/ADR, STRIDE as the prompt across the C4 L2 trust boundaries, output = tickets + an ADR section. Evidence of effectiveness is weak (multivocal), so keep it light | [F][^tmm] |
| Supply chain | SBOM per release (CycloneDX/SPDX). **SLSA Build L2** default; Build L3 + Source track for distributed products under the CRA (SLSA v1.2, Nov 2025). Pinned + verified deps, automated update PRs with a merge SLA | [F][^slsa] |
| Secrets | None in repo/images; secret scanning pre-commit + CI; short-lived workload identity over static keys | [I] |
| AI-generated code | Same SAST/DAST gates, no exemptions | [F][^veracode] |

## 5. Performance & accessibility budgets
- **Core Web Vitals at p75 field data** [F][^cwv]:
  - LCP ≤ 2.5 s
  - **INP ≤ 200 ms** (replaced FID in Mar 2024)
  - CLS ≤ 0.1

  Enforce with Lighthouse CI byte budgets plus RUM.
- **Accessibility: WCAG 2.2 AA now.**
  - EN 301 549 V4.1.1 (WCAG 2.2) was published 2 Sep 2026, with OJ citation targeted ~Dec 2026.
  - Until then, V3.2.1 (WCAG 2.1 AA) is the legal presumption basis [F][^en301].
  - Enforce with axe in CI, plus manual screen-reader passes on key journeys, plus a design system with accessibility built into the components.

## 6. EU regulation that changes app architecture (as of 2026-10-10)
| Date | Event |
|---|---|
| 28 Jun 2025 | **European Accessibility Act** applies to new products/services; existing services transition by 28 Jun 2030 [F][^eaa] |
| 6 Dec 2025 | German NIS2 implementing law in force (~29,500 entities) [F][^nis2de] |
| 2 Aug 2026 | **AI Act Art. 50 transparency** applies (disclose AI interaction, mark synthetic content) [F][^aiomni] |
| **11 Sep 2026** | **CRA reporting live**: exploited vulnerabilities and severe incidents → 24h early warning, 72h notification [F][^cra-rep] |
| ~Dec 2026 | EN 301 549 V4.1.1 (WCAG 2.2) cited in the OJ [F][^en301] |
| 2 Dec 2027 | AI Act high-risk (Annex III) obligations, delayed by the AI Omnibus (Reg. (EU) 2026/1744) [F][^aiomni] |
| **11 Dec 2027** | **CRA fully applies**: security by design, technical docs, conformity assessment, CE marking [F][^cra] |
| 2 Aug 2028 | AI Act high-risk embedded in Annex I products [F][^aiomni] |
| pending | GDPR Digital Omnibus (COM(2025) 837) is **not law**, so don't design on it [F][^omnibus] |

**Applicability check — run in Blueprint step 1:**
| Regime | Applies when | Not when | Architecture consequence [I] |
|---|---|---|---|
| **CRA** | Software product placed on the EU market (apps, installables, firmware) + its essential remote data processing | Pure SaaS not tied to a marketed product (Commission RDPS test, 27 Jul 2026) | Update channel from day 1. Versioned, signed releases. SBOM in CI. Vuln intake → 24h reporting runbook. Secure-by-default config. **≥5-year support period**, which argues for few, long-lived release trains and boring dependencies [F][^cra] |
| **EAA** | Consumer-facing in listed sectors (e-commerce, banking, transport ticketing, e-comms, e-books, AV) | Micro-enterprise *service* providers; B2B-internal tools | Semantic server-rendered HTML first, accessible design system, accessibility statement as a product artifact |
| **GDPR** | Any personal data | Truly anonymous data | See the privacy patterns below |
| **AI Act Art. 50** | Any user-facing AI interaction or generated content | Purely internal, non-interactive ML | Disclosure and content-labelling built into UI components |
| **AI Act high-risk** | Annex III use cases (employment, credit, education, essential services…) | Others | Risk file, input/output/version logging, a human-override path |
| **NIS2** | You are, or sell to, an essential/important entity | Small entities generally | Expect SDLC-evidence questionnaires. ASVS + SLSA + CRA artifacts double as NIS2 supplier evidence, so build them once and reuse them three times |

**GDPR privacy-by-design patterns** [I unless tagged]:
- Minimize at the schema level, with no "just in case" columns.
- Tag every field with a classification.
- Make retention code: TTL jobs and tables partitioned by retention class.
- Deletion must reach backups, search indexes and analytics. Use crypto-shredding with per-subject keys where backups can't be edited.
- Hold pseudonymization keys in a separate service. Pseudonymized data **stays personal data for the controller** (EDPB 01/2025) and may be non-personal only for a recipient who can't re-identify it (CJEU *EDPS v SRB*, C-413/23 P) [F][^pseudo].
- Keep logs and traces PII-free.
- Design the DSAR export endpoint early.

## 7. Failure modes (each is a review finding)
1. The **AI amplifier**: throughput up, change failures and rework up [F][^dora25].
2. Self-reported AI productivity accepted as evidence [F][^metr].
3. A copy-paste codebase, where duplication overtakes refactoring [F][^gitclear].
4. An **ice-cream-cone suite**: E2E-first, flaky, red builds ignored [F][^flaky].
5. **Coverage theatre**: 90% gates producing assertion-free tests [F][^coverage].
6. Long-lived feature branches [F][^tbd].
7. Observability bill shock from unbounded logs and high-cardinality metrics [F][^grafana].
8. PII in telemetry [I].
9. "Pseudonymized = anonymous" [F][^pseudo].
10. Fail-open error handling [F][^top10].
11. Accessibility retrofitted after launch [I].
12. "We're SaaS so the CRA doesn't apply", which is false when the backend is essential remote processing for an app you market [F][^cra].
13. CRA reporting with no pipeline behind it: the 24h warning is impossible without vuln intake, SBOM-to-CVE matching and on-call ownership [I].

## 8. Outdated — correct on sight
- DORA elite/high/medium/low tiers → archetypes (2025)
- Four key metrics → five (rework rate)
- FID → INP
- OWASP Top 10:2021 → 2025
- ASVS 4.0.3 → 5.0.0 (requirement IDs changed, so remap control mappings)
- EN 301 549 V3.2.1 → V4.1.1
- AI Act high-risk "Aug 2026" → Dec 2027 / Aug 2028
- SLSA v1.0 → v1.2

## Sources
[^codered]: https://arxiv.org/abs/2203.04374
[^besker]: https://research.chalmers.se/en/publication/507477
[^dora24]: https://cloud.google.com/blog/products/devops-sre/announcing-the-2024-dora-report
[^dora25]: https://services.google.com/fh/files/misc/2025_state_of_ai_assisted_software_development.pdf · https://www.infoq.com/news/2025/09/dora-state-of-ai-in-dev-2025 (effect sizes: pull from the PDF before quoting)
[^dora-ai]: https://cloud.google.com/blog/products/ai-machine-learning/introducing-doras-inaugural-ai-capabilities-model
[^dora5]: https://cd.foundation/blog/2025/10/16/dora-5-metrics/ · https://redmonk.com/rstephens/2025/12/18/dora2025/
[^metr]: https://metr.org (primary) · https://eweek.com/news/news-ai-tools-slow-developer-productivity-study
[^veracode]: https://www.veracode.com/resources/genai-code-security-report/
[^gitclear]: https://devclass.com/2025/02/20/ai-is-eroding-code-quality-states-new-in-depth-report/
[^tbd]: https://dora.dev/capabilities/trunk-based-development/
[^flaky]: https://testing.googleblog.com/2017/04/where-do-our-flaky-tests-come-from.html
[^coverage]: https://neverworkintheory.org/2021/09/24/coverage-is-not-strongly-correlated-with-test-suite-effectiveness.html
[^mutation]: https://research.google/pubs/practical-mutation-testing-at-scale-a-view-from-google/
[^otel]: https://opentelemetry.io/docs/specs/status/
[^sre]: https://sre.google/workbook/implementing-slos/
[^grafana]: https://bigdatawire.com/2025/03/27/grafanas-annual-report-uncovers-key-insights-into-the-future-of-observability
[^top10]: https://top10.owasp.org/2025/0x00_2025-Introduction
[^asvs]: https://softwaremill.com/whats-new-in-asvs-5-0/ (official: owasp.org/www-project-application-security-verification-standard)
[^tmm]: https://threatmodelingmanifesto.org/
[^slsa]: https://slsa.dev/blog/2025/11/announce-slsa-v1.2
[^cwv]: https://web.dev/articles/defining-core-web-vitals-thresholds
[^en301]: https://www.deque.com/blog/en-301-549-v4-1-1-is-final-what-changed-what-it-means-and-what-you-should-do/ · https://www.dwt.com/insights/2026/09/european-accessibility-act-ict-standards-update
[^eaa]: https://e-include.eu/web-accessibility/european-accessibility-act/
[^nis2de]: https://www.mayerbrown.com/en/insights/publications/2025/12/cyber-rules-for-essential-and-important-entities-take-effect-in-germany-nis2-implementing-law
[^aiomni]: https://www.addleshawgoddard.com/en/insights/insights-briefings/2026/technology/eu-ai-act-ai-omnibus-formally-adopted/ · https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/
[^cra-rep]: https://privacymatters.dlapiper.com/2026/08/eu-preparing-for-the-cyber-resilience-acts-september-2026-reporting-obligations/
[^cra]: https://bootlin.com/blog/cyber-resilience-act-cra-obligations-for-manufacturers/ · https://www.cyberresilienceact.eu/news/commission-cra-application-guidance-published-27-july-2026.html
[^omnibus]: https://www.bakertilly.de/en/post/the-digital-omnibus-is-rolling-these-changes-are-planned
[^pseudo]: https://www.cliffordchance.com/insights/resources/blogs/talking-tech/en/articles/2025/09/pseudonymized-data-after-edps-v-srb.html
