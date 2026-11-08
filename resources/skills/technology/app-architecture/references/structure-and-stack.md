# Structure & Stack — app-architecture reference

*Snapshot retrieved 2026-10-10. [F] = sourced fact · [W] = weak/practitioner or vendor source, never cite as fact in client work · [I] = inference/judgment. Raw research with full source table: `output/.runs/20261010-app-architecture-skill/children/structure/RESPONSE.md`.*

## 1. The default app stack and what it takes to deviate
Every deviation needs an ADR naming the scenario the default **measurably** fails. Thresholds are judgment [I] unless cited.

| Layer | Default | Deviate only when |
|---|---|---|
| Shape | **Modular monolith**: one deployable, enforced modules, each module the sole writer of its data. Separate worker *roles* from the same artifact for async/batch load | Extract a service when **≥2** hold: independent team cadence blocked by a shared pipeline · a distinct scaling/resource profile (GPU, memory-bound, bursty batch) a separate entrypoint can't absorb · a separate compliance perimeter · a separate availability tier that must fail independently [I, grounded in Fowler, DORA, Segment, Prime Video][^fowler][^dora-lc][^segment][^prime] |
| Internal code | **Vertical slices** (feature folders) inside each module. Ports-and-adapters only at real edges | Full clean/hexagonal layering for a module with a rich shared domain model or genuine adapter variability. No repository interface whose only implementation is the ORM[^vsa] |
| Language/framework | The team's strongest **mainstream, long-track-record** option (Rails, Django, Laravel, Spring Boot, ASP.NET, a Node/TS framework) | Only for a scenario the team's stack demonstrably can't meet. "Mainstream" ≠ "boring": a framework with a big server-side attack surface (RSC) needs a patch SLA [F][^r2s] |
| Data | **Postgres**: single primary + read replicas; JSONB for semi-structured attributes; FTS/pg_trgm/pgvector first | Carve out a *write-heavy, partition-friendly* stream to wide-column/distributed SQL on a **measured** write ceiling. Never shard everything [F][^openai][^discord] |
| Tenancy | **Pool**: shared tables + `tenant_id` + Postgres RLS (`FORCE ROW LEVEL SECURITY`, tested with a non-owner role) | **Silo** (DB/instance per tenant) as a priced tier for contractual isolation/residency/noisy neighbours. Avoid schema-per-tenant above ~500 tenants [F][^saas-pg][W][^tenancy-wall] |
| Jobs | Framework/DB-backed queue (Sidekiq, Oban, Solid Queue, SKIP LOCKED) for single-step idempotent jobs, ≲1k jobs/s, with dead-tuple/vacuum monitoring | Broker for fan-out, replay or measured throughput beyond that. **Durable execution** (Postgres-backed lib like DBOS → Temporal at scale/polyglot) for multi-step, long-wait, saga or human-approval flows [W][^pgq][^dbos] |
| Integration | **Transactional outbox** for every "write + publish" (polling relay or CDC) | — dual writes are never acceptable [F][^outbox] |
| API | **REST + OpenAPI** across any team/org boundary; additive-only changes + contract tests internally; date-pinned versions for long-lived public APIs | gRPC: internal high-volume/streaming/polyglot. GraphQL: many heterogeneous clients over many backends. tRPC: single TS monorepo, client+server deploy together, no external consumer [F][^trpc][^stripe] |
| Web client | **Server-rendered HTML + progressive enhancement** (htmx/Hotwire/islands) for forms, CRUD, content, back-office. Per-route JS budget in CI | **SPA** for long-session, heavy-client-state tools (editors, canvases, dense dashboards, offline). SPAs can beat MPAs on in-session INP, so the choice is about the surface, not dogma [F][^webdev-spa][^russell] |
| Mobile | **PWA** for internal/B2B tools without deep device APIs | React Native/Expo for a React/TS org (New Architecture only since 0.82). KMP + Compose MP when native teams exist or native UX differentiates. Flutter for pixel-identical branded UI with a dedicated team. Native when the app *is* the product [F][^rn][^cmp][I] |
| Offline | Online-first with optimistic UI | Local-first sync engine (ElectricSQL, Zero, PowerSync) only when offline or sub-50 ms perceived latency is a product requirement (field service, shop floor, collaborative editing). It adds conflict resolution, partial-replication authz and client schema migration [F][^localfirst][W] |
| Identity | **Buy** OIDC (Entra, Okta, Auth0, Keycloak, Zitadel); passkeys as the default login | Never build password storage or MFA flows. Passkeys: FIDO reports ~93% sign-in success and up to 81% fewer login tickets (advocacy body, treat accordingly) [F][^fido] |
| Authorization | **RBAC in one central authz module** with a test per policy from day 1 | **ReBAC** (OpenFGA, SpiceDB; Zanzibar model) at "role explosion" (roles encode resource IDs) or sharing/hierarchies. ABAC/policy engine (Cedar, OPA) for attribute rules. Broken access control is OWASP #1 [F][^fga][^zanzibar] |
| Feature flags | Buy or OSS; every flag typed (release/ops/experiment/permission) with owner and expiry; release flags deleted within a set window | — never repurpose a flag name (Knight Capital, ~$440M in ~45 min) [F][^hodgson][^knight] |
| Event sourcing / CQRS | Plain state tables + outbox events | CQRS when the read shape differs sharply from the write shape. Event sourcing for **one** bounded context where the log *is* the business truth (ledger, audit, temporal queries), with a written upcasting + snapshot + replay-time budget [F][^pryce][W] |

## 2. Boundary enforcement: what actually works
- **Modularity and deployment units are separate decisions.** Shopify increased modularity without adding deployables [F][^shopify].
- **Violation counts lie.** Shopify's 2024 Packwerk retrospective [F][^packwerk]:
  - Privacy checks were removed in v3 because they produced "endless poorly-documented public code".
  - Static analysis misses autoloading and routes, so zero-violation packages still crashed.
  - Semantic names grouped code that had no runtime relationship.
  - **Acceptance test for a module: it boots and its tests run in isolation, enforced in CI.**
- **Wire the ecosystem's checker into CI from day 1** [I]:
  - JVM: Spring Modulith 2.0 `ApplicationModules.verify()` (GA 2025-11-21) [F][^modulith] or ArchUnit
  - Python: import-linter
  - JS/TS: dependency-cruiser or Nx module boundaries
  - Ruby: Packwerk
  - .NET: NetArchTest
- **Find boundaries with domain events and change coupling, not nouns** (event storming, bounded contexts). Git change coupling across a proposed boundary is the empirical test [I].

## 3. Named failure modes (each is a review finding)
1. **Distributed monolith / service per integration.** Segment ran ~140 per-destination services; ops cost grew linearly per destination and they consolidated to one service [F][^segment].
2. **Serverless orchestration of a hot loop.** Prime Video's monitoring pipeline hit Step Functions transition limits and S3 hand-off costs; one process cut cost >90%. This was one subsystem, not an abandonment of services [F][^prime].
3. **Microservices from scratch.** Fowler: almost all systems built that way "ended up in serious trouble" [F][^fowler].
4. **Boundary theatre.** Fake-public APIs, zero-violation modules that crash [F][^packwerk].
5. **Event-sourcing everywhere / hybrid writes.** Handlers writing events *and* relational state left state unrebuildable [F][^pryce].
6. **Dual write without outbox.** Lost or phantom events [F][^outbox].
7. **Postgres queue MVCC death spiral.** Long transactions stall vacuum; the queue slows ~10× while looking empty [W][^pgq].
8. **Schema-per-tenant sprawl** past hundreds of schemas [W][^tenancy-wall].
9. **RLS tested as table owner.** Owners bypass RLS unless it is forced, so tests pass while prod leaks [I].
10. **GraphQL for a single web client.** N+1 and per-field authz debt [W].
11. **JS-first frontend for low-end devices / public services** [F][^russell].
12. **Framework as attack surface.** CVE-2025-55182 "React2Shell": CVSS 10 unauthenticated RCE in RSC deserialization, exploited in the wild (Dec 2025) [F][^r2s].
13. **Flag reuse / dormant code** (Knight Capital) [F][^knight].
14. **Role explosion** [F][^fga].
15. **Headline-statistic architecture.** "42% of orgs returning to monoliths (CNCF 2025)" has no primary source, so don't cite it. The strong evidence is case-level [W].

## 4. Red-flag checklist — run on every design and every review
1. Stack named before the outcome, the expected change and the scenarios exist.
2. More deployables than stream-aligned teams; services sharing a database or deploying together.
3. Modules with no CI-enforced boundary check, or that can't boot/test in isolation.
4. A table written by more than one module.
5. "Write + publish" without an outbox.
6. Event sourcing across a whole system, or without a replay-time budget.
7. NoSQL or a broker chosen "for scale" without access-pattern or throughput numbers.
8. Pool tenancy without RLS + a cross-tenant leak test as a non-owner role.
9. SPA for a forms/content app, or no JS budget at all.
10. Self-built auth (password storage, MFA, sessions) instead of OIDC.
11. Authorization checks scattered across handlers with no central policy module or tests.
12. Feature flags without type, owner or expiry; reused flag names.
13. A server-side framework with no CVE patch SLA (≤72 h for criticals [I]).
14. A one-way-door decision (data model, tenancy, IdP, public API) with no ADR.

## 5. Where the evidence refines the house positions
- **Postgres until it breaks** holds remarkably far: OpenAI serves ~800M ChatGPT users from one primary + ~50 replicas. But OpenAI puts *new write-heavy* workloads on sharded Cosmos DB [F][^openai]. Refinement: Postgres for relational truth, with write-heavy streams carved out on measured evidence.
- **Server-rendered before SPA** is right for documents and forms. SPAs can win INP within a session, and the htmx port evidence is selection-biased toward content apps [F][^webdev-spa][^htmx]. Refinement: SSR for documents and forms, SPA for long-session tools, and a JS budget either way.
- **Modular monolith** only counts with *executable* enforcement. Otherwise it's a monolith with folders [F][^packwerk].
- **Boring technology:** mainstream isn't the same as boring. Boring means a small attack surface and a long track record [I].

## Sources
[^fowler]: https://martinfowler.com/bliki/MonolithFirst.html · https://martinfowler.com/bliki/MicroservicePremium.html
[^dora-lc]: https://dora.dev/capabilities/loosely-coupled-teams/
[^segment]: https://segment.com/blog/goodbye-microservices/ · https://www.infoq.com/news/2020/04/microservices-back-again/
[^prime]: https://devclass.com/2023/05/05/reduce-costs-by-90-by-moving-from-microservices-to-monolith-amazon-internal-case-study-raises-eyebrows/
[^vsa]: https://milanjovanovic.tech/blog/vertical-slice-vs-clean-architecture · https://codeopinion.com/is-vertical-slice-architecture-better-than-clean-architecture-or-ports-and-adapters/
[^r2s]: https://security.utoronto.ca/advisories/react-server-next-js-critical-vulnerability/
[^openai]: https://www.infoq.com/news/2026/02/openai-runs-chatgpt-postgres
[^discord]: https://www.infoq.com/news/2023/06/discord-cassandra-scylladb/
[^saas-pg]: https://docs.aws.amazon.com/prescriptive-guidance/latest/saas-multitenant-managed-postgresql/welcome.html
[^tenancy-wall]: https://www.postgresql.eu/events/pgconfpl2026/schedule/session/8462-multi-tenant-postgres-where-each-design-hits-a-wall/
[^pgq]: https://dbos.dev/blog/making-postgres-queues-scale · https://www.prisma.io/blog/you-dont-need-a-job-queue-postgres-already-has-skip-locked (canonical primary not re-fetched: brandur.org on Postgres job queues and MVCC)
[^dbos]: https://dbos.dev/compare/dbos-vs-temporal (vendor)
[^outbox]: https://microservices.io/patterns/data/transactional-outbox.html · https://www.conduktor.io/glossary/outbox-pattern-for-reliable-event-publishing
[^trpc]: https://catalins.tech/public-api-trpc/ · https://infoq.com/news/2025/12/orpc-v1-typesafe/
[^stripe]: https://stripe.com/blog/api-versioning
[^webdev-spa]: https://web.dev/articles/vitals-spa-faq
[^russell]: https://infrequently.org/2024/11/if-not-react-then-what/
[^htmx]: https://htmx.org/essays/a-real-world-react-to-htmx-port/
[^rn]: https://reactnative.dev/blog/2025/10/08/react-native-0.82 · https://reactnative.dev/blog/2026/02/11/react-native-0.84
[^cmp]: https://www.neowin.net/news/jetbrains-brings-compose-for-ios-to-stable-with-compose-multiplatform-180-release/
[^localfirst]: https://www.inkandswitch.com/local-first/
[^fido]: https://fidoalliance.org/biometric-update-state-of-passkeys-2025-passkeys-move-to-mainstream/
[^fga]: https://guptadeepak.com/ciam-compass/guides/fine-grained-authorization-fga/
[^zanzibar]: https://www.usenix.org/conference/atc19/presentation/pang
[^hodgson]: https://martinfowler.com/articles/feature-toggles.html
[^knight]: https://en.wikipedia.org/wiki/Knight_Capital_Group
[^pryce]: https://www.infoq.com/news/2019/07/mistakes-recovery-event-sourcing/
[^shopify]: https://shopify.engineering/deconstructing-monolith-designing-software-maximizes-developer-productivity
[^packwerk]: https://shopify.engineering/a-packwerk-retrospective
[^modulith]: https://spring.io/blog/2025/11/21/spring-modulith-2-0-ga-1-4-5-and-1-3-11-released/
