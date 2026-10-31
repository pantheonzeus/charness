# Frameworks & Method — cloud-architecture reference

*Snapshot retrieved 2026-10-10. [F] = sourced fact · [I] = inference/arithmetic. Re-verify anything decision-critical. Raw research: `output/.runs/20261010-cloud-architecture-skill/children/a-frameworks/RESPONSE.md`.*

## 1. Well-Architected frameworks — use as a review checklist, not as gospel
| | AWS | Azure | Google Cloud |
|---|---|---|---|
| Pillars | 6: Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability [F][^aws-pillars] | 5: Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency. Explicit **Tradeoffs** pages per pillar [F][^az-waf] | 6: Operational Excellence; Security, Privacy & Compliance; Reliability; Cost Optimization; Performance Optimization; Sustainability. Last updated 2026-01-28 [F][^gcp-waf] |
| Extensions | Lenses: GenAI (Apr 2025, updated Nov 2025 with agentic-AI preamble), ML, **Responsible AI** (Nov 2025), SaaS, Serverless [F][^aws-ai-lens] | Advisor Score per pillar, online WA Review [F][^az-waf] | Perspectives: AI/ML, Financial Services [F][^gcp-waf] |
| Review format | Numbered questions per pillar (REL 9…) → best practices → HRI/MRI risks → improvement plan [I] | Checklist codes RE:/SE:/CO:/OE:/PE: [I] | Principle-based |

- **Where they agree** [I]: identity is the primary security boundary; automate change (IaC); test recovery instead of assuming it; attribute cost to owners; horizontal scale; prefer managed services.
- **Bias to correct for** [I]: all three equate "simplify" with "use our managed services". That cuts ops toil and raises switching cost, and none of them prices lock-in. The skill does (principle 4).
- Useful AWS specifics [F]: dev/test runs only 40 of 168 h/week, so stopping it saves ~75%[^aws-cost]. Eliminate long-term static credentials[^aws-sec]. Reliability: "stop guessing capacity", "manage change through automation"[^aws-rel].

## 2. Method artifacts — the composition that works
**Utility tree → 6-part scenarios → fitness functions/SLOs → ADRs → C4 views** [I].
- **Quality-attribute scenario** (SEI): source · stimulus · environment · artifact · response · **response measure**. Without the measure, the scenario isn't a requirement [F][^qas].
- **ATAM** (SEI): 9 steps in two phases (business drivers → utility tree → analyze approaches → stakeholder scenarios → risks, non-risks, sensitivity points, tradeoff points) [F, secondary source][^atam]. Use the outputs (sensitivity/tradeoff points) even when not running the full ceremony.
- **ADR**: Nygard 2011 — Title, Status, Context, Decision, Consequences; numbered, immutable, superseded rather than edited, kept in the repo [F][^nygard]. **MADR 4.0.0** (Sep 2024) adds Decision Drivers, Considered Options, Pros/Cons and **Confirmation** (how compliance is verified, i.e. the fitness function) [F][^madr].
- **Fitness function**: "an objective integrity assessment of some architectural characteristic(s)", run continually in CI or monitoring [F][^fitness].
- **C4**: Context → Container → Component → Code, plus Deployment/Dynamic/Landscape [F][^c4]. Default to Context + Container (+ Deployment). Component and Code diagrams rot [I].
- **arc42**: 12 sections incl. quality requirements, risks & technical debt, and architectural decisions. A good skeleton for long-lived design docs [F][^arc42].

## 3. Reliability math
- **Error budget** = 1 − SLO. Releases continue while budget remains; when it's exhausted they halt and effort shifts to reliability. 99.99% ≈ 52.56 min/yr [F][^sre-risk].
- **SLI** = good events / valid events. **SLO** = target over a window. **SLA** = contractual and looser than the internal SLO [I][^sre-slo].
- **Nines → downtime** [I, arithmetic]:

| SLO | per year | per 30-day month |
|---|---|---|
| 99% | 87.6 h | 7.2 h |
| 99.9% | 8.76 h | 43.2 min |
| 99.95% | 4.38 h | 21.6 min |
| 99.99% | 52.6 min | 4.3 min |
| 99.999% | 5.3 min | 26 s |

- **Serial**: A = Π Aᵢ. Three 99.9% hard dependencies give 99.70%, ten 99.95% give ≈99.50% [I].
- **Parallel**: A = 1 − Π(1 − Aᵢ) **only if failures are independent**. A shared region, control plane, deploy pipeline or config push voids it, and most multi-AZ math is over-optimistic for exactly this reason [I].
- **"Rule of the extra 9"** (Treynor, Dahlin, Rau, Beyer, ACM Queue 2017) [F][^calculus] — "A service cannot be more available than the intersection of all its critical dependencies … critical dependencies must offer one additional 9 relative to your service." For a 99.99% service, that means 99.999% dependencies.

### DR tiers (pick the cheapest that meets RTO/RPO) [F][^aws-dr-tiers]
| Tier | RPO | RTO | Cost |
|---|---|---|---|
| Backup & restore | hours | < 24 h | Low |
| Pilot light | tens of min | tens of min | Medium |
| Warm standby | minutes | minutes | High |
| Multi-site active/active | ~0 | ~0 | Highest |

DR rules [F][^aws-dr-wp] —
- Fail over using **data-plane** operations, because control planes have lower availability goals.
- Replication doesn't protect against corruption or malicious deletion, so point-in-time backups are needed at every tier. Data-corruption RPO is never zero.
- Prefer *manually initiated, fully automated* failover over health-check auto-failover.
- Use a separate account per Region.
- Restore-test your backups.

## 4. Migration & landing zones
- **7 Rs** (AWS): Retire, Retain, Rehost, Relocate, Repurchase, Replatform, Refactor. AWS itself advises rehost/relocate/replatform first and modernizing after, because refactor is "the most complex and costly". Retire anything below 5% average utilization (zombie) or at 5–20% over 90 days (idle). Retain explicitly covers data-residency and **manufacturing-plant hardware dependencies** [F][^7rs].
- **Azure CAF landing-zone design areas**: billing & tenant · identity & access (the "primary security boundary") · resource organization · network topology · security · management · governance · platform automation & DevOps [F][^caf-lz].
- **Minimal landing zone before the first workload** [I, cross-vendor synthesis]:
  1. Account structure: prod / non-prod / security & log-archive / shared network, in an OU or management-group hierarchy.
  2. Identity: federated SSO with MFA, no long-lived keys, break-glass accounts, group-based RBAC.
  3. Network: IP plan, hub-spoke, private connectivity, egress control, DNS.
  4. Logging: immutable org-wide audit logs in a separate account.
  5. Guardrails: an EU region allow-list, deny public storage, require encryption, enforce tags.
  6. Budgets and cost-allocation tags.
  7. All of it in IaC.

## 5. Security baseline
- **Shared responsibility**: the provider secures *of* the cloud, the customer secures *in* it. On IaaS the customer patches the guest OS; on abstracted services the customer owns data, encryption choices and IAM [F][^shared].
- **Zero trust** (NIST SP 800-207): no implicit trust from network location, and authentication plus authorization before each resource access [F][^nist-zt]. Identity is the perimeter.
- **Keys** [F][^gcp-kms] — CMEK = customer-managed key in the provider KMS · BYOK = you import the key material · HYOK/EKM = keys stay outside the provider.
  - Only HYOK or confidential computing technically limits provider-side access [I].
  - HYOK adds the external KMS to the serial availability product [I].
- **Hardening**: CIS Foundations Benchmarks, Level 1 (low friction) vs Level 2 (defense in depth). Current versions [F][^cis] —
  - **AWS v7.0.0** (Apr 2026);
  - **Azure v6.0.0** (May 2026; Entra ID recommendations moved to the M365 benchmark);
  - **GCP v5.0.0** (Jun 2026).
- **Secrets**: a managed secret store, workload identity federation over static secrets, auto-rotation, and never in IaC state or repos [I].

## Sources
[^aws-pillars]: https://docs.aws.amazon.com/wellarchitected/latest/framework/the-pillars-of-the-framework.html · https://docs.aws.amazon.com/wellarchitected/latest/framework/document-revisions.html (latest major update 6 Nov 2024, checked 2026-10-10)
[^aws-ai-lens]: https://aws.amazon.com/about-aws/whats-new/2025/11/new-aws-well-architected-lenses-ai-ml-workloads · https://aws.amazon.com/blogs/architecture/announcing-the-updated-aws-well-architected-generative-ai-lens
[^aws-cost]: https://docs.aws.amazon.com/wellarchitected/latest/framework/cost-dp.html
[^aws-sec]: https://docs.aws.amazon.com/wellarchitected/latest/framework/sec-design.html
[^aws-rel]: https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/design-principles.html
[^az-waf]: https://learn.microsoft.com/en-us/azure/well-architected/pillars
[^gcp-waf]: https://docs.cloud.google.com/architecture/framework
[^qas]: https://people.ece.ubc.ca/matei/EECE417/BASS/ch04lev1sec5.html · https://quality.arc42.org/articles/specify-quality-requirements
[^atam]: https://en.wikipedia.org/wiki/Architecture_tradeoff_analysis_method (secondary; SEI primary not fetched)
[^nygard]: https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions
[^madr]: https://adr.github.io/madr/
[^fitness]: https://www.thoughtworks.com/en-gb/radar/techniques/architectural-fitness-function
[^c4]: https://c4model.com/
[^arc42]: https://arc42.org/overview
[^sre-risk]: https://sre.google/sre-book/embracing-risk/
[^sre-slo]: https://sre.google/sre-book/service-level-objectives/ (not fetched this run)
[^calculus]: https://sre.google/static/pdf/calculus_of.pdf (ACM Queue 15(2), Mar–Apr 2017 reprint; queue.acm.org returns 403)
[^aws-dr-tiers]: https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-database-disaster-recovery/defining.html
[^aws-dr-wp]: https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html
[^7rs]: https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-guide/migration-strategies.html
[^caf-lz]: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/design-areas
[^shared]: https://aws.amazon.com/compliance/shared-responsibility-model/
[^nist-zt]: https://csrc.nist.gov/pubs/sp/800/207/final
[^gcp-kms]: https://docs.cloud.google.com/security/key-management-deep-dive
[^cis]: https://www.cisecurity.org/insights/blog/cis-benchmarks-april-2026-update · https://www.cisecurity.org/insights/blog/cis-benchmarks-may-2026-update · https://www.cisecurity.org/insights/blog/cis-benchmarks-june-2026-update
