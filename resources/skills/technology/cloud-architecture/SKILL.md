---
id: cloud-architecture
aliases: [cloud-architecture]
name: "Cloud Architecture — Design, Review & Exit-Ready Cost Math"
category: technology
description: Design or red-team a cloud architecture at principal level — requirements and quality-attribute scenarios first, boring-by-default component choices with a burden of proof on exotic ones, availability/DR math, a unit-cost and egress model, an explicit exit/sovereignty plan, and ADRs plus a C4 design doc as output. Provider-agnostic (AWS/Azure/GCP + EU sovereign providers).
triggers: [cloud architecture, design the architecture, architecture review, well-architected review, AWS, Azure, GCP, landing zone, migrate to cloud, repatriation, leave the cloud, kubernetes or not, serverless vs containers, microservices or monolith, multi-region, disaster recovery, RTO RPO, cloud cost, FinOps, egress, vendor lock-in, exit strategy, sovereign cloud, Gaia-X, STACKIT, DORA exit plan, RAG architecture, GPU hosting, ADR]
tags: [technology, architecture, cloud, finops, sovereignty, reliability]
related: ["[[app-architecture]]", "[[business-case-builder]]", "[[risk-and-mitigation]]", "[[decision-memo]]", "[[assumption-audit]]", "[[operating-model-design]]", "[[data-migration-strategy]]"]
modules: [file-backed-state, evidence-backed-answering, verifier-separation]
status: active
version: 2
created: 2026-10-10
updated: 2026-10-10
requires:
  tools: [web_search, web_fetch]
  optional: [provider pricing calculators, cloud CLIs (aws/az/gcloud) for read-only inventory]
environment: "Runs anywhere. Pricing and regulatory dates in references/ are dated snapshots — re-verify any number that drives a decision against the provider's live price page before it lands in a client deliverable."
references: [references/frameworks-and-method.md, references/cost-exit-sovereignty.md, references/heuristics-and-failure-modes.md, references/templates.md, references/EVIDENCE.md]
scripts: [scripts/build_claims_register.py]
---

# Cloud Architecture — Design, Review & Exit-Ready Cost Math

## Contract
- **Input:** one of three modes — **Design** (a workload or product to build), **Review** (an existing architecture, diagram, IaC repo, or bill to red-team), **Move** (migrate-to / repatriate-from / switch-between clouds). Plus whatever constraints exist: load, data, team size, regulation, budget, deadline.
- **Output:** a design doc at `output/<YYYYMMDD>-<slug>-architecture.md` with the sections in [templates.md](references/templates.md): requirements + quality-attribute scenarios, C4 context/container view (Mermaid), component decisions as ADRs, availability and DR math, a cost model with unit cost, an exit and sovereignty plan, and a ranked risk list. Review mode adds a findings table (severity · evidence · fix · effort). Index into `cbrain/notes/Deliverables/` per Charter §4.
- **Allowed tools/artifacts:** conversation, user-supplied diagrams/IaC/bills, read-only cloud CLI inventory, web search for current prices and regulation. Never run mutating cloud commands.
- **Done when:** every component choice has an ADR with at least one rejected alternative; every SLO has the arithmetic behind it; the cost model shows a monthly figure **and** a unit cost with egress itemized; the exit plan names the target, the data-transfer path and the cost; and the verifier pass (step 9) records PASS.

## Triggers/Context
- Any request to design, review, cost, migrate, or de-risk a system that runs on cloud infrastructure, or to answer "should we use X" for an infrastructure component (Kubernetes, Kafka, serverless, multi-region, a sovereign provider).
- **Boundary:** the software's internal structure — modules, data model, APIs, client rendering, identity/authz, AI feature integration, quality foundations — belongs to `app-architecture`. A full-system ask runs that skill first and arrives here with its C4 container view.
- Hand-offs: when the question becomes a funding decision, pass the cost model to `business-case-builder`. A board-level risk register goes to `risk-and-mitigation`, and a one-page executive recommendation goes to `decision-memo`. This skill owns the technical truth those skills consume.

## Operating principles (enforceable)
1. **Requirements before boxes.** No component appears in the design until steps 1–2 exist. A diagram drawn before the quality-attribute scenarios is a review finding, not a design.
2. **Burden of proof on the exotic choice.** The default stack is a modular monolith on managed containers or VMs, managed Postgres, object storage, a managed queue, a CDN, and IaC from day one. Every deviation (Kubernetes, microservices, NoSQL, Kafka, multi-region active-active, service mesh, multi-cloud) needs an ADR that names the requirement which the default *measurably* fails. The defaults and their thresholds are in [heuristics-and-failure-modes.md](references/heuristics-and-failure-modes.md).
3. **Every number shows its arithmetic.** Composite availability is the product of the serial components' SLAs. RTO/RPO come from a named DR tier. Cost is volume × list price × time, with the price source and its date. No "highly available", "scalable", or "cost-effective" without a figure.
4. **Exit is designed in, not promised.** Every design names its exit target and per-component portability (portable / rewrite / lock-in accepted, with reason). For EU-regulated clients, check this against the Data Act and DORA (see [cost-exit-sovereignty.md](references/cost-exit-sovereignty.md)).
5. **Failure domains are explicit.** For every critical dependency, state the failure domain (AZ / region / provider / control plane / identity / DNS / vendor agent) and what happens when it fails. Backups live in a separate failure domain, and a backup that has never been restored doesn't count.
6. **Team capacity is a hard constraint.** The ops load must fit the team that will run it. An architecture needing an on-call platform team that the client doesn't have is rejected, however elegant.
7. **Facts are dated and sourced.** Prices, regulatory dates and service availability go through the evidence gate (`_shared/evidence-gate.md`): source plus retrieval date, or tagged as inference.

## Core Blueprint
Substantive runs keep a STATE_ROOT at `output/.runs/<YYYYMMDD>-<slug>-arch/` with `RESPONSE.md` (steps 1–9 as boxes) and `EVIDENCE.md` (every price/date/claim plus source).

1. **Frame the mode and the outcome.** Design, Review, or Move. One sentence on the business outcome the system serves and the cost of it being down for an hour. If nobody can name either, stop and ask.
2. **Capture requirements as quality-attribute scenarios** (source · stimulus · environment · response · measure), at most 8, ranked. Always cover availability, latency, scale (steady **and** peak, with growth), data residency/sovereignty, security/compliance, cost ceiling, time-to-market and team size/skills. Mark each as given or assumed. Assumed ones go in the open-questions list.
3. **Classify the workload:** steady vs spiky load, stateful vs stateless, data gravity (where the data lives, where it flows, egress volume/month), regulatory class (GDPR, NIS2, DORA, KRITIS, export control), and any AI/GPU component. This determines the compute and hosting shortlist.
4. **Choose components default-first.** For each layer (edge/CDN, compute, data, messaging, identity, observability, CI/CD/IaC, AI if any), start from the default in principle 2 and write an ADR ([templates.md](references/templates.md)) with ≥1 rejected alternative and the triggering requirement. Run the red-flag checklist in [heuristics-and-failure-modes.md](references/heuristics-and-failure-modes.md) against your own choices.
5. **Draw it.** C4 Level 1 (context) and Level 2 (containers) in Mermaid, marking trust boundaries, regions/AZs and data-residency boundaries. Level 3 only for the one container that carries the risk.
6. **Do the reliability math.** Write down the SLO per user journey and the composite availability from the serial components, then check whether the SLO is achievable. Pick a DR tier (backup-restore / pilot light / warm standby / active-active) that meets the RTO/RPO and state its cost multiple. List the control-plane dependencies (IAM, DNS, KMS, the provider's global services) that the data path must not need in order to keep serving (static stability). Specify **change safety** for code *and* config/policy/content: staged rollout, bake time, auto-rollback, feature flags, validation, and jittered backoff on retries. Four of the five megaoutages in the reference (2021–2025) were change events, so this buys more availability per euro than going multi-region.
7. **Do the cost model.** Monthly run cost broken down by compute / storage / data transfer (egress, cross-AZ, NAT) / managed-service premium / observability / non-prod, at the steady **and** peak scenarios. Annotate every data-flow edge with GB/month × $/GB. If transfer exceeds ~15% of the bill, redesign before shipping. Then the unit cost (per tenant, transaction or user) at 1× and 10× scale, and the commitment strategy: the flexible instrument, sized to the 12-month usage floor, with each commitment's end date logged in an ADR as an exit constraint. In Move mode, run the repatriation test (steady spend ≥ ~$1M/yr or ≥ 20–25% of COGS, **and** baseline ≥ 60–70% of peak). Below ~$250k/yr, optimize in place. Otherwise add a 3-year TCO including ops FTE, migration effort and open commitments, the break-even point, and the *selective* move (storage, egress-heavy and steady tiers first). Pull price anchors from [cost-exit-sovereignty.md](references/cost-exit-sovereignty.md) and re-verify any figure that swings the decision.
8. **Write the exit and sovereignty plan.** Classify each data set (public / internal / confidential-personal / regulated-critical) and map it to an acceptable jurisdiction using the table in [cost-exit-sovereignty.md §5](references/cost-exit-sovereignty.md). Name the exit target (one EU-owned option where sovereignty matters), the per-component portability table, and the data-export path with volume × egress price (switching egress becomes free under the Data Act from 12 Jan 2027, but parallel multi-cloud egress doesn't). Add the regulatory hooks: a **tested** DORA exit plan for critical functions, NIS2 supply-chain records, and C5/SecNumCloud evidence. State CLOUD Act exposure honestly; residency is not sovereignty.
9. **Verifier pass (separate step).** Re-read the deliverable against the Contract's done-when list and the red-flag checklist. Record each item PASS/FAIL in RESPONSE.md. On FAIL, fix and re-run, capped at 2 revision attempts, and report anything still open instead of hiding it. Review mode: every finding carries evidence (file/line, bill line, diagram element), severity, fix and effort.

## Optimizations/Gotchas
- **Diagram-first is the most common failure.** Elegant boxes, no load numbers. Step 2 exists to block it.
- **Egress and NAT are where cloud bills surprise people.** Never ship a cost model that leaves data transfer out or folds it into "networking".
- **Composite SLA always comes out lower than the weakest link.** Five 99.9% serial services give ≈99.5%. Showing the arithmetic ends most "we need multi-region" debates — in either direction.
- **Multi-cloud for resilience rarely pays off.** Prefer single-provider multi-AZ with a tested, cheap exit path. Recommend active multi-cloud only when a regulation or a concentration-risk mandate requires it, and price it.
- **"Sovereign" is not one thing.** Separate data residency, operational sovereignty (who can access, under which jurisdiction) and technological sovereignty (could you run it without the vendor). State which one the client actually needs.
- **Prices and regulation go stale.** References are dated snapshots (last verified 2026-10-10), so re-verify before any client-facing number.
- **Maintaining the references:** every factual line carries [F]/[F*]/[I]/[U] plus a footnote. After any edit, run `python3 scripts/build_claims_register.py`, then `python3 ../../_shared/scripts/evidence_lint.py references/EVIDENCE.md`. Don't ship a reference change unless both report `blockers=0`. Never put a footnote directly before a colon mid-line (`[^x]:`), because it parses as a definition and the claim reads as uncited.
- **The frameworks are vendor-biased.** AWS, Azure and Google Well-Architected all equate "simplify" with "use our managed services" and never price lock-in. Use them as a review checklist and add the exit column yourself.
- **AI quick-starts default to "Global" deployment types**, which process EU personal data outside the EU. Check that the Bedrock `eu.` profile or the Azure Data Zone EU deployment is actually used.
- **Repatriation is a cost model, not a mood.** It wins on steady, predictable, large compute and storage with an ops-capable team, and loses on spiky load, small teams and fast-moving products. Show the break-even.
