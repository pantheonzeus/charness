---
id: app-architecture
aliases: [app-architecture]
name: "App Architecture — Boundaries, Stack Decisions & Fitness Functions"
category: technology
description: Design, review or evolve a software application's architecture at principal level — outcome and quality-attribute scenarios first, module boundaries and data ownership before services, a boring-by-default stack with a burden of proof on exotic choices, quality foundations (tests, CI, observability, security, accessibility) as non-negotiable, AI features on the simplest rung that works, and decisions locked in as ADRs plus executable fitness functions.
triggers: [app architecture, application architecture, architect this app, design the app, software architecture, system design, architecture for our product, tech stack, which stack, choose a framework, modular monolith, microservices or monolith, bounded contexts, domain-driven design, DDD, hexagonal, clean architecture, data model, multi-tenancy, SaaS architecture, API design, REST vs GraphQL, SPA vs server-rendered, htmx, react server components, mobile app architecture, native vs cross-platform, Flutter vs React Native, offline first, authentication, authorization, RBAC, event-driven, event sourcing, CQRS, architecture review, codebase review, tech debt, fitness functions, ADR, architect an AI app, LLM feature architecture, AI feature in our app, RAG app]
tags: [technology, architecture, software-design, application, ai-native, quality]
related: ["[[cloud-architecture]]", "[[agent-architecture]]", "[[multi-agent-platform]]", "[[strangler-fig-program]]", "[[legacy-seam-mapping]]", "[[agentic-service-blueprint]]", "[[agentic-service-evaluation]]", "[[business-case-builder]]", "[[decision-memo]]", "[[risk-and-mitigation]]"]
modules: [file-backed-state, evidence-backed-answering, verifier-separation]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
requires:
  tools: [web_search, web_fetch]
  optional: [git and read-only static analysis on a supplied repo (dependency-cruiser, madge, packwerk, ArchUnit, import-linter, osv-scanner, syft)]
environment: "Runs anywhere. Review mode is strongest with the codebase checked out locally — read-only commands only. Regulatory dates and framework/tool status in references/ are 2026-10-10 snapshots; re-verify anything that drives a client decision."
references: [references/method-and-decisions.md, references/structure-and-stack.md, references/quality-and-compliance.md, references/ai-native.md, references/templates.md]
---

# App Architecture — Boundaries, Stack Decisions & Fitness Functions

## Contract
- **Input:** one of three modes —
  - **Design:** a product or app to build, from an idea to a PRD.
  - **Review:** an existing app to red-team, from a repo, a diagram, a design doc or a pain statement ("releases take 3 weeks").
  - **Evolve:** a major change to a live app, such as adding multi-tenancy, a mobile client, an AI feature, splitting a service or killing a framework.

  Plus whatever constraints exist: team size and skills, deadline, users and load, regulation, budget.
- **Output:** a design doc at `output/<YYYYMMDD>-<slug>-app-architecture.md` with the sections in [templates.md](references/templates.md). It covers:
  - outcome and quality-attribute scenarios
  - module and data-ownership map
  - C4 L1/L2 views
  - stack decisions sized S/M/L, with ADRs for M/L (Confirmation on every L) and build or buy
  - the quality-foundations section
  - an AI section, when the app has AI features
  - a fitness-function register
  - a walking-skeleton delivery plan
  - ranked risks

  Review mode adds a findings table carrying evidence (file:line, dependency-graph output, git churn). Index the doc into `cbrain/notes/Deliverables/` per Charter §4.
- **Allowed tools/artifacts:** conversation, supplied docs/diagrams, read-only git and static analysis on a supplied repo, web search for current framework/regulatory status. Never push, never mutate the client's repo or infra.
- **Done when:**
  - every M/L decision has an ADR naming ≥1 rejected alternative and the scenario that forced it
  - every L decision's Confirmation names an automated check
  - every module has exactly one owner of its data
  - every quality-attribute scenario has a measure and is protected by ≥1 fitness function or an explicit "accepted risk"
  - the quality-foundations section names concrete tools and thresholds
  - any AI feature states its ladder rung, its eval pass bar and its cost per task
  - the verifier pass (step 10) records PASS

## Triggers/Context
- Any request to design, choose a stack for, review, or restructure a **software application**: web, mobile, SaaS, internal tool, API product, or AI-native app.
- **Boundary with siblings:**
  - **`cloud-architecture`** owns *where and how it runs*: hosting, compute, regions, DR, availability math, cloud cost, exit and sovereignty. This skill owns *what the software is made of*: modules, data ownership, APIs, clients, identity, async, AI components, quality foundations. A full-system ask runs this skill first, then hands the container view to `cloud-architecture`. Don't duplicate its cost or DR math.
  - **Legacy replacement** (strangling an old system) → `strangler-fig-program`. This skill designs the target architecture the slices migrate into.
  - **AI agents:** this skill decides *whether* the app needs an AI component and on which rung, then integrates it: gateway, evals in CI, cost per task, residency, UI disclosure, injection posture at the app boundary.
    - Designing the agent itself (harness, determinism boundary, conformance level) → `agent-architecture`.
    - Several agents or an agent estate → `multi-agent-platform`.
    - Human–agent work design in a service → `agentic-service-blueprint`; go-live evals → `agentic-service-evaluation`.
  - A funding question goes to `business-case-builder`; a one-page recommendation to `decision-memo`.

## Operating principles (enforceable)
1. **Outcome before architecture.** Write one sentence naming the business outcome, the user's job, and the change you expect most often in the next 12 months. Modifiability is judged against that change, not in the abstract. If nobody can name the outcome, stop and ask.
2. **Boundaries before services.** Draw modules (bounded contexts) with sole data ownership first. Deployment units come last and are a separate decision. The default is **one deployable, many enforced modules**. A split needs an ADR showing a *different team owner*, a *different scaling or availability profile*, or a *different compliance regime*. See [structure-and-stack.md](references/structure-and-stack.md).
3. **Burden of proof on the exotic choice.** The default stack is in [structure-and-stack.md §1](references/structure-and-stack.md). Every deviation needs an ADR naming the scenario the default *measurably* fails. "Scalable", "modern" and "flexible" are not scenarios.
4. **Size every decision before choosing its process** ([method-and-decisions.md §1](references/method-and-decisions.md)):
   - **S** (two-way door, one team) goes in a PR note, decided at ~70% of the information.
   - **M** (two-way but cross-team, or a quarter to reverse) gets a Y-statement plus advice from affected teams.
   - **L** (one-way door: data model, tenancy, identity provider, public API/contract, persistence engine, vendor lock-in, security boundary, team split) gets a MADR 4 ADR whose **Confirmation** names an automated check, plus a risk-storm.
   - Decide at the *most* responsible moment: if ≥2 teams depend on the answer, its deadline is their start date.
5. **Buy the commodity, build the differentiator.** Identity, payments, email, search, feature flags, observability and forms are bought or open-source by default. Build only what is on the product's differentiation path, and state the arithmetic (licence vs FTE-months) in the ADR.
6. **Quality foundations are part of the architecture, not a phase.** Every design specifies the items below with tools and thresholds. A design without them FAILs the verifier, whatever the elegance. Details are in [quality-and-compliance.md](references/quality-and-compliance.md).
   - test strategy and CI time budget
   - trunk-based delivery with feature flags
   - OpenTelemetry tracing plus app SLIs
   - threat model plus OWASP ASVS level
   - SBOM and dependency policy
   - accessibility target
   - performance budget
7. **Architecture is enforced by code, not by diagrams.** Each top-ranked scenario and every L decision gets a **fitness function**, an automated check in CI or production. Module boundaries need a static dependency checker **and** a test that boots each module in isolation; Shopify found zero-violation packages that still crashed alone. Fitness functions also keep AI coding agents on a leash; agents accelerate drift otherwise.
8. **AI on the lowest rung that works.** Use plain code, then a single LLM call, then a fixed workflow, then an agent. Each step up needs an ADR showing the lower rung failing on the eval set. Every LLM feature ships with:
   - a frozen eval set with a pass bar
   - a model gateway
   - an injection posture (no "lethal trifecta" without a break)
   - a cost per task
   - a human checkpoint before irreversible actions

   See [ai-native.md](references/ai-native.md).
9. **Team capacity is a hard constraint.** Cognitive load per team and the on-call reality must fit the people who exist. Conway's law runs whether you plan for it or not, so design the module map and the team map together.
10. **Facts are dated and sourced.** Framework status, regulatory dates and benchmark numbers go through the evidence gate (`_shared/evidence-gate.md`), with source plus retrieval date or an inference tag.

## Core Blueprint
Substantive runs keep a STATE_ROOT at `output/.runs/<YYYYMMDD>-<slug>-app-arch/` with `RESPONSE.md` (steps 1–10 as boxes) and `EVIDENCE.md` (every claim, number and repo measurement with its source).

1. **Frame the mode and outcome.** Design, Review or Evolve. Name:
   - the business outcome and the user's job
   - the change you expect most often
   - the team (size, skills, team count in 12 months)
   - the deadline
   - the regulatory class: is it a CRA "product with digital elements"? Is the EAA in scope? Which AI Act tier? Does GDPR special-category data apply?
2. **Quality-attribute scenarios** (stimulus · response · measure), ≤8, ranked, each marked given or assumed. Always cover modifiability against the expected change, time-to-market, key-journey p95, security/privacy, accessibility and operability by this team. Assumed scenarios go to open questions.
3. **Review mode only — gather evidence before opinions.** Run the read-only commands in [templates.md §3](references/templates.md):
   - churn hot spots
   - change coupling across module lines
   - dependency cycles
   - test-to-code ratio and CI duration
   - dependency/CVE age
   - delivery cadence

   Record the numbers in EVIDENCE.md. Every later finding cites one of them or a file:line.
4. **Domain and boundaries.** List the capabilities, then group them into modules by language and data cohesion (event storming or a capability map). Per module, record the data it solely owns, its public interface, the events it publishes, its volatility and its owning team. Write the dependency rule and name the tool that will enforce it.
5. **Stack decisions, default-first.** Walk the layers in [structure-and-stack.md](references/structure-and-stack.md):
   - shape
   - language and framework (the team's strongest mainstream option wins ties)
   - data and tenancy
   - API style
   - web rendering and mobile
   - identity and authorization
   - async, jobs and workflows
   - integration
   - feature flags

   Size each decision S/M/L and record M (Y-statement) and L (MADR 4 with Confirmation) decisions, with build/buy arithmetic (licence vs FTE-months, exit cost) where relevant. Then run the red-flag checklist in [structure-and-stack.md](references/structure-and-stack.md) against your own choices.
6. **AI components (if any).** If the rung reached is *agent* or above, hand the agent's internals to `agent-architecture` (or `multi-agent-platform`) and keep only the integration contract here. Pick the ladder rung, gateway, context/RAG design, tool permissions and injection posture. Then the eval set and pass bar, human checkpoints, and cost and latency per task at 1× and 10×. Follow [ai-native.md](references/ai-native.md).
7. **Quality foundations and compliance.** Fill section 7 of the template with:
   - test shape and pipeline budget
   - observability (OTel, SLIs)
   - threat model (STRIDE on the C4 L2 trust boundaries), ASVS level, SBOM/SLSA target and secrets handling
   - accessibility (WCAG 2.2 AA)
   - performance budget (Core Web Vitals)
   - the regulatory hooks from [quality-and-compliance.md](references/quality-and-compliance.md): CRA vulnerability handling and reporting, EAA, GDPR deletion/retention by design, AI Act transparency
8. **Draw and lock in.**
   - C4 L1 and L2 in Mermaid, with L3 only for the riskiest container.
   - Fitness-function register: one check per top scenario, starting from [templates.md §4](references/templates.md).
   - A risk-storm on the C4 container view: each person marks risks independently, then the group converges.
   - Walking skeleton: the thinnest end-to-end slice through every layer in production.
   - First three increments, each with the decisions they keep open.
   - Hand the container view to `cloud-architecture` for hosting, DR and cost.
9. **Risks and open questions.** Rank the risks with an owner each. Every assumed scenario and every one-way door decided on thin evidence appears here.
10. **Verifier pass (separate step).** Re-read the deliverable against the Contract's done-when list and the red-flag checklist, and record each item PASS/FAIL in RESPONSE.md. On FAIL, fix and re-run, capped at 2 revision attempts, and report what stays open instead of hiding it. In Review mode, every finding carries evidence, severity, fix and effort.

## Optimizations/Gotchas
- **Stack-first is the most common failure.** "Next.js + microservices + Kafka" before anyone has named the expected change. Steps 1–2 exist to block it.
- **Distributed monolith is worse than either option.** Services that share a database, deploy together or call each other synchronously in chains carry the costs of both shapes and the benefits of neither. In review, it's the first thing to look for.
- **Module boundaries rot silently** without a CI checker, and violation counts lie. Group by how code runs and changes together (git change coupling), not by nouns.
- **Monolith-first has a serious critic.** Tilkov's case is that boundaries are hard to retrofit. The answer is enforced modules from commit 1, not "we'll modularize later". Segment and Prime Video are n=1 anecdotes, and DORA supports *loose coupling*, not a style.
- **ADR logs die young.** ~50% of repos that use ADRs stop at 1–5 of them. Keep ADRs in the repo, size them S/M/L so small decisions stay cheap, and recommend the advice process (anyone decides after seeking advice, plus a weekly forum) over an approval board ([method-and-decisions.md §3](references/method-and-decisions.md)).
- **AI coding without guardrails lowers delivery stability.** DORA 2024: more AI adoption came with −7.2% stability. METR: experienced developers were 19% slower while feeling faster. Recommend AI coding agents only alongside fast CI, small batches and fitness functions.
- **The SPA default is a cost, not a neutral choice.** Content- and form-heavy apps ship faster and lighter server-rendered (with htmx, Hotwire or islands). Reserve SPAs and rich clients for genuinely app-like, offline or highly interactive surfaces, and say which one this is.
- **Tenancy is a one-way door.** Decide shared-schema + RLS vs schema/DB-per-tenant before the first customer, and prove isolation with a cross-tenant leak test in CI.
- **Agents are the new microservices.** Teams reach for multi-agent orchestration before a single prompt with good context has been tried. Demand the eval evidence that the lower rung fails.
- **Compliance changes architecture now, not later.**
  - EAA accessibility obligations have applied since 28 Jun 2025.
  - CRA vulnerability reporting applies from 11 Sep 2026, with full obligations from 11 Dec 2027. That means an SBOM and a vulnerability-handling process for anything sold in the EU.
  - Retrofitting either one costs multiples of designing for it.
- **The frameworks and blogs are biased.** Vendor reference architectures sell their platform, and conference talks overrepresent FAANG scale. Weight evidence from teams of the client's size.
