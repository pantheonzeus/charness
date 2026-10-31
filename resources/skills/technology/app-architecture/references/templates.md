# Templates — app-architecture

ADR format: **L decisions use MADR 4** (with a Confirmation section naming the fitness function) and **M decisions a Y-statement** — see [method-and-decisions.md §2](method-and-decisions.md). The MADR-lite ADR and the C4 Mermaid starter in [cloud-architecture/references/templates.md §2 and §4](../../cloud-architecture/references/templates.md) are reused as-is; don't fork them.

## 1. Design doc skeleton (`output/<YYYYMMDD>-<slug>-app-architecture.md`)

```markdown
# <App> — Application Architecture (<Design|Review|Evolve>) · <date>

## TL;DR
- Recommendation in one line · shape (e.g. modular monolith, 6 modules) · the one decision that is expensive to reverse
- Time to first production release · team that runs it
- Top 3 risks

## 1. Outcome & constraints
Business outcome · primary user + the job they hire the app for · success metric tied to money or a decision
Team: size, skills, number of teams in 12 months · deadline · budget · regulatory class (CRA product? EAA in scope? AI Act tier? GDPR special categories?)

## 2. Quality-attribute scenarios (ranked, ≤8)
| # | Attribute | Stimulus → Response | Measure | Given/Assumed |
|---|---|---|---|---|
Always cover: modifiability (the change you expect most), time-to-market, performance (p95 on the key journey), security/privacy, accessibility, operability by this team. Add availability only at app level (graceful degradation); infra SLOs belong to cloud-architecture.

## 3. Domain & boundaries
Capability list → modules (bounded contexts). For each module: owner, data it owns (sole writer), public interface, events it publishes.
| Module | Owns data | Public API | Depends on | Team owner | Volatility (H/M/L) |
|---|---|---|---|---|---|
Dependency rule + the tool enforcing it (e.g. Packwerk, Spring Modulith, ArchUnit, import-linter, dependency-cruiser).

## 4. Architecture views
### C4 L1 — Context (mermaid)
### C4 L2 — Containers (mermaid)
### C4 L3 — Components of the riskiest container only

## 5. Stack & decisions (ADRs) — summary table; full ADRs in appendix
| ADR | Size (S/M/L) | Layer | Decision | Rejected alternative | Triggering scenario | Confirmation (fitness fn) | Build/Buy |
|---|---|---|---|---|---|---|
Layers to cover: shape · language/framework · data store + tenancy · API style · client (web rendering, mobile) · identity + authz · async/jobs/workflows · integration · AI (if any) · feature flags · observability · testing.

## 6. Data
Core entities + system of record per entity · tenancy model + isolation test · retention/deletion per data class · migration strategy (expand/contract)

## 7. Quality foundations (non-negotiable section)
Test strategy (shape + what runs on every commit, target pipeline time) · CI/CD + trunk-based flow · observability (OTel traces, structured logs, the 3–5 app SLIs) · security (threat model summary, ASVS level, SBOM, secrets) · accessibility target · performance budget

## 8. AI components (only if present)
Pattern ladder rung chosen (single call → workflow → agent) and why · model gateway · eval set + pass bar · guardrails / injection posture · cost per task at 1× and 10× · human-in-the-loop points

## 9. Fitness functions
| # | Protects scenario | Check | Where it runs (CI/prod) | Threshold | Fails build? |
|---|---|---|---|---|---|

## 10. Delivery plan
Walking skeleton (thinnest end-to-end slice in prod) · first 3 increments · which decisions stay open until when (most responsible moment: the date dependent teams need the answer)

## 11. Risks (ranked)
| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|

## 12. Open questions (every Assumed scenario lands here)

## Appendix — full ADRs · Evidence (sources + retrieval dates) · Handoffs (to cloud-architecture: hosting/DR/cost)
```

## 2. Review-mode findings table

```markdown
| # | Severity | Finding | Evidence (file:line / dependency graph / metric) | Fix | Effort (S/M/L) | Area |
|---|---|---|---|---|---|---|
```
Severity anchors: **Critical** = data leak across tenants/users, security hole, or unmet legal obligation (CRA, EAA, GDPR, AI Act) is plausible · **High** = the expected change (scenario #1) or the release cadence is blocked · **Med** = avoidable complexity or ops burden · **Low** = hygiene.
Area: boundaries · data · API · client · identity · async · AI · tests/CI · observability · security · accessibility.

## 3. Codebase review evidence commands (Review mode — read-only)

Run the ones that fit the stack and paste the numbers into EVIDENCE.md:
- Size and churn hot spots: `git log --since=12.months --name-only --format= | sort | uniq -c | sort -rn | head -30`
- Change coupling (files that always change together across module lines): same log, grouped per commit.
- Lead-time proxy: `git log --since=3.months --format=%cs | uniq -c` (deploy/merge frequency).
- Dependency graph and cycles: `npx dependency-cruiser`, `madge --circular`, `import-linter`, `packwerk check`, `jdeps`, ArchUnit tests.
- Test signal: test file count vs source file count, CI duration, flaky-test list.
- Dependency risk: lockfile age, `npm audit` / `pip-audit` / `osv-scanner`, SBOM generation (`syft`).

## 4. Fitness-function starter set

| Check | Tooling examples | Protects |
|---|---|---|
| No module imports another module's internals | Packwerk, Spring Modulith `verify()`, ArchUnit, import-linter, dependency-cruiser | Modifiability |
| No dependency cycles between modules | same | Modifiability |
| Each table written by one module only | SQL grants per module schema, or a CI grep on write paths | Boundaries / future extraction |
| Every query on tenant data carries tenant scope | Postgres RLS + a cross-tenant leak test in CI | Security |
| p95 of key journey ≤ budget | k6 / Lighthouse CI / Core Web Vitals RUM | Performance |
| Accessibility: zero axe violations on key pages | axe-core / Playwright | EAA compliance |
| No critical CVEs in shipped dependencies; SBOM produced | osv-scanner, syft, Dependabot/Renovate | CRA, supply chain |
| CI pipeline ≤ 10 min (judgment threshold) | CI metrics | Delivery speed |
| LLM feature eval score ≥ pass bar on frozen set | eval harness in CI | AI quality |
