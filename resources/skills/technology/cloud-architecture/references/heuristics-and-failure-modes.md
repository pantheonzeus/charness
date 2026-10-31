# Heuristics & Failure Modes — cloud-architecture reference

*Snapshot retrieved 2026-10-10; prior-knowledge citations re-verified the same day. [F] = sourced fact · [F*] = cited from prior knowledge, not re-fetched · [I] = inference/judgment. Raw research: `output/.runs/20261010-cloud-architecture-skill/children/c-heuristics-failures/RESPONSE.md`.*

## 1. The default stack and what it takes to deviate
Every deviation needs an ADR naming the requirement that the default **measurably** fails. The thresholds are judgment [I] unless cited, so tune them per client and record the reason.

| Layer | Default | Deviate only when |
|---|---|---|
| Shape | Modular monolith with enforced boundaries (Packwerk/ArchUnit-style) | A split maps to a **different team owner**, a **different scaling/availability profile**, or a **different compliance/residency regime**. Independently deployable services ≤ stream-aligned teams [I] |
| Compute | Managed containers (Cloud Run / ECS Fargate / Azure Container Apps), or VMs for stateful/licensed/legacy | **Kubernetes:** a platform team of ≥ 2 FTE exists **and** there are > ~20–30 services or a hard multi-cloud/on-prem portability need [I]. **Functions:** event glue or spiky, low-duty-cycle load |
| Data | Managed **wire-compatible open Postgres** (+ JSONB, full-text, pgvector, queue table via SKIP LOCKED) | **NoSQL:** known narrow access patterns at very high scale with single-digit-ms needs. Proprietary Postgres-likes (Aurora-specific features, Spanner, Cosmos APIs) count as lock-in and need justification [I] |
| Messaging | Managed queue (SQS / Pub/Sub / Service Bus) or a Postgres queue | **Kafka:** a replayable durable log, multiple independent consumers, CDC/event-sourcing fan-out, or ordered throughput ≥ tens of MB/s [I; no primary source found] |
| Tenancy | **Pool** + Postgres RLS + tenant_id in every key, log and metric | **Silo** as a priced premium tier for regulated/enterprise tenants. **Bridge** per tier [F][^saas] |
| Regions | Single region, multi-AZ, in an EU region (not us-east-1 as primary) | Multi-region only when the RTO/RPO math or a regulation demands it. Pick the DR tier from [frameworks-and-method.md §3](frameworks-and-method.md) |
| IaC | OpenTofu (open license, Linux Foundation fork of Terraform 1.5) with portable HCL. CI plan/apply with mandatory plan review | Terraform when the client is already standardized on it (BSL mainly bites competing vendors, and the remaining risk is IBM stewardship) [F][^iac]. Pulumi (Apache 2.0 engine, self-managed state backends incl. S3/Blob/GCS/Postgres) for teams that want real code [F][^pulumi] |
| Delivery | CI/CD with staged rollout, bake time, auto-rollback, feature flags, **config validation** | GitOps (Argo CD / Flux, both CNCF-graduated 2022) once on Kubernetes [F][^gitops] |
| Platform | A shared IaC module repo plus managed services *is* the platform | An IDP or product-managed platform team at ≥ ~5 stream-aligned teams repeatedly solving the same infra problems [I] |
| AI | Managed model API behind a **gateway** (routing, quotas, PII redaction, logging, fallback model) using EU data-zone deployment types. pgvector for RAG | Self-hosted GPU (see §4) |

## 2. Evidence behind the defaults
- **Kubernetes waste is measured** [F]:
  - Average provisioned-CPU utilization is ~8% and memory ~20%, and getting worse (Cast AI 2026 report; vendor data)[^cast26].
  - CPU was ~69% over-provisioned and memory ~79% in 2024[^nextplat].
  - In a CNCF FinOps microsurvey (2023), K8s raised spend for nearly half of respondents, mainly through over-provisioning (70%)[^cncf].
- **Kubernetes TCO** = cluster compute (often 3–10× used capacity) + control-plane fee + 2–4 platform FTE + ~3 minor upgrades/yr [I].
- **Prime Video VQA (2023)** moved from Step Functions + S3 hand-offs to one process on ECS and cut infra cost by >90%. The lesson is that **granularity should follow data-movement cost**, not that Amazon abandoned microservices [F][^prime][F][^catchpoint].
- **Segment** went from 140+ per-destination microservices back to a monolith because operational overhead stalled product work [F][^segment].
- **Shopify** runs >1,000 developers on a modular Rails monolith, with boundaries enforced by Packwerk [F][^shopify].
- **Fowler**: MonolithFirst and the MicroservicePremium [F][^fowler]. Conway's law and Team Topologies: architecture mirrors the communication structure [F][^conway].
- **Postgres** was the most-used database in Stack Overflow 2025, at **58.2% of professional developers** (55.6% of all respondents). It is also the most admired (65.5%) and most desired (46.5%), and has ranked highest on both since 2023 [F][^pg].

## 3. Outages → design rules
Four of these five megaoutages were **change events** (config, content, automation), not hardware. Deployment safety buys more availability per euro than active-active multi-region [I].

| Event | What happened | Design rule |
|---|---|---|
| **AWS us-east-1, 19–20 Oct 2025** [F][^aws-oct25] | A race between DNS Enactors deleted all IPs for the DynamoDB regional endpoint. EC2 lease management depended on DynamoDB, so launches failed. Recovery hit congestive collapse, and NLB auto-failover removed healthy capacity. ~14.5 h end to end | **Static stability**: pre-provision N+1 AZ capacity, because existing-capacity data planes survived and anything needing to launch did not. Load-test recovery paths. Cap automatic failover velocity. Don't use us-east-1 as primary (global control-plane dependencies) [I] |
| **Google Cloud, 12 Jun 2025** [F][^gcp-jun25] | Service Control had new code with no feature flag and no error handling. A blank policy row replicated globally via Spanner in seconds, causing crash loops in every region. us-central1 took ~2h40m because of a herd with no jittered backoff | **Config is code**: staged regional rollout, validation and a kill switch. Global replication = global blast radius. Retries must use **randomized exponential backoff** |
| **Azure Front Door, 29–30 Oct 2025** [F][^afd] | A config change bypassed validation because of a defect in the deployment-safety system and propagated globally. ~8.5 h. The Portal and Entra-dependent services were hit too | A global edge/CDN is one global failure domain. Critical sites need a documented **bypass** (DNS to a secondary CDN or origin). Expect the provider's portal to be down when you need it [I] |
| **CrowdStrike, 19 Jul 2024** [F][^cs] | A content update read 21 fields where 20 were supplied, an out-of-bounds read in the kernel, and fleet-wide BSOD. Recovery was manual per host | Any **privileged, auto-updating vendor agent** is an unstaged global change channel into your estate. Demand staged rings (N-1) [I] |
| **OVH Strasbourg fire, 10 Mar 2021** [F][^ovh] | SBG2 was destroyed. Customers with backups on the same site lost data permanently. OVH then moved to 3-DC regions and default backups | **A backup in the same failure domain is not a backup.** Verify the physical separation of "AZs" at smaller providers [I] |

Cross-cutting patterns [F]:
- **Static stability**: the data plane never depends on the control plane, and the system survives losing one AZ without launching anything[^static].
- **Cells**: independent cells with no shared state behind a thin router bound the blast radius of bad deploys and poison tenants[^cells]. Propose cells for multi-tenant systems at scale.

## 4. AI / LLM workloads
- **Frameworks** [F]: AWS GenAI Lens (Apr 2025; agentic preamble Nov 2025)[^genai-lens]. Azure WAF AI workloads and the GCP AI/ML perspective exist [F*][^ai-waf] (not re-fetched).
- **API vs self-host** [F, secondary — order of magnitude only][^llm-cost] —
  - API list prices run ~$0.20–$10 per M input tokens and ~$1.20–$50 per M output tokens.
  - Cloud H100s cost ~$2.85–3.50/h after a 64–75% drop from peak.
  - Break-even vs frontier APIs is cited at ~100–256 M tokens/month.
  - Production GPU clusters often run below 60% utilization.
- **Rule** [I]: default to the managed API. Self-host only for sustained volume at > ~50% *achieved* GPU utilization with a good-enough open model, or a hard no-US-parent sovereignty requirement, or airgap/latency constraints. Count ML-ops on-call headcount in the math.
- **Residency** [F]:
  - Bedrock `eu.` cross-Region inference profiles route only to EU Regions and aren't compatible with Provisioned Throughput[^bedrock-eu].
  - Azure OpenAI offers Global, **Data Zone EU** (processed within the EU Data Boundary) and Regional deployments[^aoai].
- **Red flag** [I]: "Global" deployment types are the quick-start default and process EU personal data outside the EU. EU-processing ≠ sovereignty, because US-parent providers stay subject to the CLOUD Act. Say so.
- **RAG reference** [I]:
  1. Ingest: parse → chunk → embed, **carrying document ACLs as metadata**.
  2. Index in pgvector in the existing Postgres. Move to a dedicated vector store only with a measured recall/latency gap.
  3. Filter by **permissions at query time**.
  4. Generate through the gateway.
  5. Evaluate with a harness (golden set, groundedness, retrieval recall) plus tracing.
- **Agents** [I]: durable workflows (queue + idempotent steps + state store), least-privilege credentials per tool, human approval for irreversible actions, per-tenant token budgets, and **all tool output treated as untrusted input**.

## 5. Red-flag checklist — run on every design and every review
Each hit is a finding: Critical/High where it threatens data, security or SLO, Med for cost or ops burden.
1. Boxes drawn before load, data and SLO numbers exist.
2. Kubernetes for fewer than ~10 services, or with no platform team. A service mesh before mTLS or observability need is proven.
3. **Distributed monolith**: services that share a database or must deploy together[^segment].
4. Chatty fine-grained orchestration passing large payloads via object storage[^prime].
5. NoSQL or Kafka chosen "for scale" without access-pattern or throughput numbers.
6. Global config, policy or content push without staged rollout, validation or a kill switch.
7. Retries without jittered exponential backoff.
8. Recovery that depends on control-plane actions (launch, scale, DNS change) during a regional event.
9. Unbounded automatic failover.
10. Backups in the same building, region or account as the primary, or restores never drilled. RTO/RPO claims with no drill date get marked *unverified*.
11. A single global edge/CDN with no documented bypass.
12. us-east-1 as the default primary region. EU data with no policy-as-code region allow-list.
13. Active-active multi-cloud "for resilience". Prefer portability plus a tested exit.
14. No unit-cost metric, no tagging, FinOps by monthly surprise. Egress/NAT missing from the cost model.
15. Prod and non-prod in one account/subscription/project. Long-lived or shared admin keys.
16. LLM calls hard-wired to one vendor SDK with no gateway. "Global" AI deployments with EU personal data. RAG without permission-aware retrieval or an eval set.
17. A privileged auto-updating vendor agent with no staged rings.
18. Pool tenancy without RLS and cross-tenant leak tests.

## Sources
[^saas]: https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/silo-pool-and-bridge-models.html · https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/pool-isolation.html
[^iac]: https://www.softwareseni.com/hashicorp-terraform-opentofu-and-the-ibm-acquisition-wild-card-for-infrastructure-as-code/ · https://www.cloudmagazin.com/en/2026/03/22/opentofu-vs-terraform-what-the-ibm-acquisition-means-for-your-infrastructure/ · https://www.cncf.io/projects/opentofu/ (CNCF Sandbox since 23 Apr 2025)
[^cast26]: https://cast.ai/blog/2026-state-of-kubernetes-resource-optimization-cpu-at-8-memory-at-20-and-getting-worse/
[^nextplat]: https://www.nextplatform.com/2024/03/04/kubernetes-clusters-have-massive-overprovisioning-of-compute-and-memory/
[^cncf]: https://leaddev.com/technical-direction/ai-and-kubernetes-are-pushing-cloud-costs-out-control (secondary; CNCF PDF not fetched)
[^prime]: https://web.archive.org/web/20231230202019/https://www.primevideotech.com/video-streaming/scaling-up-the-prime-video-audio-video-monitoring-service-and-reducing-costs-by-90 (Marcin Kolny, 22 Mar 2023: "reduced our infrastructure cost by over 90%"; original URL now redirects away) · https://www.networkworld.com/article/3697737/6-lessons-from-the-amazon-prime-video-serverless-vs-monolith-flap.html
[^catchpoint]: https://www.catchpoint.com/blog/debunking-misconceptions-amazon-prime-videos-approach-to-microservices-and-serverless
[^segment]: https://www.infoq.com/news/2018/07/segment-microservices · https://www.infoq.com/presentations/microservices-monolith-antipatterns · https://www.twilio.com/en-us/blog/developers/best-practices/goodbye-microservices (Alexandra Noonan, 10 Jul 2018; "over 140 services")
[^shopify]: https://shopify.engineering/deconstructing-monolith-designing-software-maximizes-developer-productivity · https://shopify.engineering/enforcing-modularity-rails-apps-packwerk
[^fowler]: https://martinfowler.com/bliki/MonolithFirst.html (3 Jun 2015) · https://martinfowler.com/bliki/MicroservicePremium.html (13 May 2015)
[^gitops]: https://www.cncf.io/projects/argo/ (graduated 6 Dec 2022) · https://www.cncf.io/projects/flux/ (graduated 30 Nov 2022)
[^pulumi]: https://github.com/pulumi/pulumi/blob/master/LICENSE · https://www.pulumi.com/docs/iac/concepts/state-and-backends/
[^conway]: https://www.thoughtworks.com/insights/articles/demystifying-conways-law
[^pg]: https://survey.stackoverflow.co/2025/technology
[^aws-oct25]: https://aws.amazon.com/message/101925
[^gcp-jun25]: https://status.cloud.google.com/incidents/ow5i3PPK96RduMcb1SsW
[^afd]: https://azure.status.microsoft/status/history/?trackingId=YKYN-BWZ
[^cs]: https://crowdstrike.com/wp-content/uploads/2024/08/Executive-Summary_Root-Cause-Analysis_Channel-File-291.pdf
[^ovh]: https://www.techzine.eu/news/infrastructure/59799/ovh-has-98-percent-of-services-back-online-and-now-improves-backups/ · https://www.datacenterknowledge.com/outages/ovh-founder-data-center-fire-incident-shows-all-backup-should-be-free
[^static]: https://aws.amazon.com/builders-library/static-stability-using-availability-zones · https://docs.aws.amazon.com/whitepapers/latest/aws-fault-isolation-boundaries/static-stability.html
[^cells]: https://docs.aws.amazon.com/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/what-is-a-cell-based-architecture.html
[^genai-lens]: https://docs.aws.amazon.com/wellarchitected/latest/generative-ai-lens/generative-ai-lens.html
[^ai-waf]: https://learn.microsoft.com/azure/well-architected/ai/ · https://cloud.google.com/architecture/framework/perspectives/ai-ml (F*)
[^llm-cost]: https://introl.com/blog/inference-unit-economics-true-cost-per-million-tokens-guide · https://intuitionlabs.ai/articles/hosted-ai-api-vs-self-hosted-llm-cost
[^bedrock-eu]: https://docs.aws.eu/bedrock/latest/userguide/geographic-cross-region-inference.html
[^aoai]: https://learn.microsoft.com/azure/ai-services/openai/how-to/deployment-types
