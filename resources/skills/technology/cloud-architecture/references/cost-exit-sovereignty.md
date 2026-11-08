# Cost, Exit & Sovereignty — cloud-architecture reference

*Snapshot retrieved 2026-10-10. [F] = sourced fact · [I] = inference/derivation · [U] = not confirmed as current. **Re-verify prices and regulatory status against the primary source before a client-facing number.** Raw research: `output/.runs/20261010-cloud-architecture-skill/children/b-cost-sovereignty/RESPONSE.md`.*

## 1. FinOps & billing data
- **FinOps Framework (2025 revision)** [F, secondary]:
  - Phases: Inform → Optimize → Operate.
  - 4 domains and 22 capabilities; *Quantify Business Value* includes **unit economics**.
  - New **Scopes**: Public Cloud, SaaS, Data Center, AI. Treat SaaS licences and AI tokens like cloud spend[^finops].
- **FOCUS** [F]:
  - 1.2 GA was 3 Jun 2025 (SaaS/PaaS, invoice reconciliation).
  - **1.3 (Dec 2025)** adds shared-cost **allocation columns** (K8s pods, shared DBs) and a contract-commitment dataset[^focus].
  - **1.4 (ratified 4 Jun 2026) is current**. It adds **Invoice Detail** and **Billing Period** datasets for invoice reconciliation, and 1.5 is in development [F][^focus].
  - **Rule** [I]: require FOCUS exports from every provider. A provider that can't deliver one is an allocation and portability risk.
- **Unit cost is mandatory** [I]: cost per transaction, tenant, GB or inference, matched to the revenue driver, at 1× and 10× scale, plus the share of COGS. A total without a denominator is rejected.
- **Tagging** [I]: owner, cost-center, env, service and tenant, enforced at provisioning via policy-as-code. Untaggable spend (transfer, shared NAT) gets an explicit allocation rule.

## 2. Price anchors (list, first paid tier — re-verify)
| Item | AWS | Azure | GCP | EU IaaS reference |
|---|---|---|---|---|
| Internet egress | $0.09/GB (first 10 TB; 100 GB free)[^aws-vpc] | $0.087/GB next 10 TB after 100 GB free, NA/EU origin[^az-bw] | $0.12/GB 0–1 TiB, $0.11 to 10 TiB (Premium)[^gcp-net] | Hetzner: 20 TB included on CX/CAX, then **€1/TB**[^hetzner] |
| NAT processing | **+$0.045/GB** + hourly, so private→internet = $0.135/GB[^aws-vpc] | **$0.045/GB** + $0.045/h (Standard = StandardV2)[^az-nat] | **$0.045/GiB** + gateway hourly (≤ $0.044/h)[^gcp-nat] | — |
| Cross-AZ / inter-zone | **$0.01/GB each way**[^xaz] | **Free** since May 2024 (legacy $0.01 meters still listed but not billed)[^az-xaz] | **$0.01/GiB** VM-to-VM, same region[^gcp-xaz] | — |
| Compute commitments | Compute Savings Plan up to 66% (flexible); EC2 Instance SP up to 72% (family + region locked); 1 or 3 yr[^sp] | — | — | — |
| Spot | up to 90% off, **2-min** reclaim notice[^spot] | — | — | — |

- Hyperscaler egress is **~70–100×** Hetzner-class overage ($90/TB vs ~€1/TB) [I]. For media, downloads, data products or API fan-out, egress is a first-order design input.
- **Transfer traps** [I]:
  - image and S3 pulls through NAT instead of free gateway endpoints;
  - chatty services spread over 3 AZs;
  - cross-AZ Kafka or DB replication;
  - a mesh without topology-aware routing.
- **Rule** [I]: annotate every data-flow edge with GB/month × $/GB. If transfer exceeds ~15% of the bill, redesign (CDN, endpoints, co-location, or moving the egress-heavy tier).
- **Commitments** [I]: use the flexible instrument, sized to the **12-month usage floor**, not the average. Log every commitment's end date in an ADR as an **exit constraint**, and never let a term outrun the exit-plan horizon. 37signals' exit date was set by a 4-year S3 contract, not by technology [F][^37s].
- **Spot** [I]: stateless or checkpointed work only (CI, batch, stateless pools with disruption budgets). Never single-replica state or quorum members.
- **Unpriced drivers** — checklist items only, no quoted figures [I]:
  - observability ingestion per GB (mitigate with sampling, retention tiers and an OpenTelemetry neutral layer);
  - idle non-prod (dev/test runs 24/7 but is used ~40–50 h/week; AWS puts the stop-schedule saving at ~75%[^aws-cost]);
  - managed-service markups.
- IDC: close to half of buyers overspent their 2023 cloud budget [F][^idc-over].

## 3. Repatriation — evidence, counter-evidence, break-even
**For** [F]:
- **a16z (2021)**[^a16z]:
  - committed cloud spend ≈ **50% of cost of revenue** across benchmarked public software companies;
  - repatriation costs **⅓–½** of the cloud equivalent;
  - Dropbox saved $75M in 2 years, and its gross margin went from 33% to 67%;
  - "You're crazy if you don't start in the cloud; you're crazy if you stay on it."
- **37signals**[^37s]:
  - Cloud bill fell from $3.2M/yr to $1.3M/yr after moving compute out (2024).
  - A dual-DC Pure Storage setup (18 PB combined) replaced S3. DHH puts the hardware cost at about one year of S3 spend (S3 ≈ $1.5M/yr per secondary reporting).
  - Projected 5-year saving is >$10M.
  - AWS waived exit egress, about $250k (secondary only: The Stack; not in DHH's post).
  - Primary: DHH's post (17 Oct 2024) confirms $3.2M → $1.3M/yr, the 18 PB and "well over ten million dollars over five years".
- **Ahrefs**: ~850 colocated servers vs an AWS-equivalent estimate of ~$400M+ over 2020–22, more than its ~$257M revenue. Per server, ~$1.5k/mo vs ~$17.6k/mo[^ahrefs].

**Against** [F]:
- Only **~8–9%** of companies plan *full* repatriation (IDC). Most move specific components[^idc-rep].
- a16z itself says start in the cloud[^a16z].
- Every success case had large, **steady** load and in-house ops. 37signals already ran hardware before the cloud era [I].

**Cloud is clearly cheaper when** [I]:
- infra spend is below ~1–2 ops engineers' fully loaded cost;
- peak-to-average is above ~3–4×;
- the product is pre-PMF and the architecture changes monthly;
- global reach is needed fast;
- the managed service replaces scarce skills;
- the workload needs short-lived specialised hardware (GPU bursts).

**Break-even heuristic** [I, derived — present as a model, not a fact]:
- Run the repatriation test when **all** hold:
  1. Steady spend is at least ~$1M/yr or ≥20–25% of COGS.
  2. Baseline is ≥60–70% of peak.
  3. The workload uses commodity primitives (VMs/K8s, Postgres/MySQL, object storage, queues).
  4. 24/7 ops can be staffed.
  5. Egress is material.
- Model: ⅓–½ of the cloud bill, **+** ops FTE, **+** a 6–18 month migration, **−** open commitments. Break-even typically lands at **1–3 years**; the 37signals storage case is ≈2 years.
- **Below ~$250k/yr, optimize in place.**
- The default outcome is **selective**: move storage, the egress-heavy tier and steady batch; keep the elastic and managed parts.

## 4. Lock-in & exit — regulation
- **EU Data Act** (Reg. 2023/2854, Ch. VI) [F]:
  - The switching rules have applied since **12 Sep 2025**.
  - Until 12 Jan 2027, only reduced, cost-linked switching charges are allowed.
  - **From 12 Jan 2027, no switching charges, including egress for the switch.**
  - Egress for **parallel (in-parallel) multi-cloud use** stays chargeable, but only at cost (Art. 34(2)) [F][^dataact].
  - **Contract mechanics (Art. 25)** [F][^dataact]:
    - **maximum notice of 2 months** to initiate switching;
    - a **mandatory maximum transition of 30 calendar days**;
    - if that is technically unfeasible, the provider must justify it within **14 working days** and may set an alternative transition of **at most 7 months**;
    - the customer can extend the transition **once**;
    - data retrieval is available for **at least 30 days** after the transition;
    - the provider must **support the customer's exit strategy**.
- **Hyperscaler exit waivers (2024)** [F]: Google (11 Jan), AWS (5 Mar; via support, **60-day** window, data deleted afterwards), Microsoft (13 Mar). They cover **full exits only**[^waiver].
  - So the real exit cost is re-platforming proprietary services, people and parallel running, not egress [I].
- **DORA** (Reg. 2022/2554, applies from 17 Jan 2025) [F]:
  - Art. 28(8): ICT services supporting **critical or important functions** need an exit strategy that is documented, realistic, periodically reviewed and **tested**.
  - Art. 30(3): contracts must include exit clauses with an adequate transition period[^dora].
  - **For financial-sector clients, a missing tested exit plan is a compliance finding** [I].
- **EBA**: final *Guidelines on the management of third-party risk* were published **18 Sep 2026** [F][^eba]. They replace the 2019 Outsourcing Guidelines, cover ICT and non-ICT arrangements supporting critical or important functions, and align with DORA, with a **two-year transition**. The reference EBA/GL/2026/09 comes from law-firm summaries, and the exact application date waits on translations.
- **Portability — what it really buys** [I]:

| Pattern | Portable | Not portable / real cost |
|---|---|---|
| Kubernetes | Workloads | Control plane, IAM, ingress/LB, storage classes, add-ons; 2+ platform FTE |
| Open Postgres | Data and engine | Some managed niceties; self-run needs proven PITR + HA (Patroni/operator) |
| OpenTofu/Terraform | The *inventory* (a reproducible, documented estate, which is what a DORA exit plan needs) | Provider resources; an AWS module doesn't deploy on STACKIT |
| S3-compatible API | PUT/GET | Lifecycle, events, Object Lock semantics; test the features you use |

  - **Lock-in lives in the glue** (IAM, queues, serverless triggers, managed AI APIs), not in VMs.
  - Put that glue behind a thin internal interface where it's cheap to do so. Where it isn't, accept it in an ADR with an exit estimate in person-weeks.

## 5. EU sovereignty
**Three kinds of sovereignty — always ask which one the client needs** [I]:
1. **Data residency** — where bits sit and get processed.
2. **Operational/legal sovereignty** — who can be compelled, and under which jurisdiction.
3. **Technological sovereignty** — whether you could run it without the vendor.

**Residency is not sovereignty.** Microsoft France's legal director testified under oath to the French Senate (10 Jun 2025) that he could not guarantee French citizens' data would never be handed to US authorities without French approval ("Non, je ne peux pas le garantir") [F][^cloudact]. Only three things change the CLOUD Act position [I]:
- a legally separated non-US operator (the SecNumCloud model);
- an EU-owned provider;
- customer-held keys with external KMS, **plus** an operating model with no provider access to plaintext. This still doesn't stop compelled service disruption.

**Data-class → acceptable jurisdiction** [I, default mapping; adjust per client]:
| Data class | Acceptable hosting |
|---|---|
| Public / internal | Any hyperscaler EU region |
| Confidential / personal | Hyperscaler EU region with EU data-zone processing + CMEK; name the CLOUD Act risk |
| Regulated / critical (KRITIS, defense, health, state) | EU-owned provider, or a SecNumCloud-qualified legally separated operator; HYOK if a hyperscaler is unavoidable |

**Certifications** [F]:
- **BSI C5:2026** (the final catalogue, published end of March 2026 and announced 7 Apr 2026, with 168 criteria in 17 areas, up from 121; "C5:2025" was only the community draft) adds container management, post-quantum crypto and confidential computing. It aligns with EUCS, ISO 27001:2022, NIS2 and CSA CCM and adds supply-chain and AI criteria. Transition rules (secondary — the BSI press release gives no dates) [F][^c5] —
  - attestation periods ending before 28 Feb 2027 may still use C5:2020;
  - periods ending 28 Feb – 31 May 2027 may use C5:2020 but must document the C5:2026 delta;
  - **from 1 Jun 2027 only C5:2026 applies**.
  - Ask DACH providers for C5 **Type 2**.
- **SecNumCloud 3.2** (FR) is the only scheme with explicit immunity from extraterritorial law.
  - **S3NS** (Thales+Google) was qualified **17 Dec 2025**.
  - **Bleu** (Orange+Capgemini, Microsoft tech) passed the J0 milestone for SecNumCloud 3.2 without reservations, targeting H1 2026. Final qualification couldn't be confirmed from a primary source as of 2026-10-10, so check the ANSSI list (cyber.gouv.fr) before relying on it [U][^snc].
- **EUCS** (ENISA) stalled over sovereignty requirements, and no adoption by implementing act was found as of 2026-10-10. Don't design against it, and treat it as not adopted until an implementing act is cited [F][^eucs].
- **Gaia-X**: Trust Framework 3.0 "Danube" (Nov 2025) is a **trust/labelling framework for data spaces, not a cloud**. Treat it as a weak signal for hosting choice [F/I][^gaiax].

**Offerings** [F]:
- **AWS European Sovereign Cloud** went GA in **Jan 2026** (Brandenburg, DE). It is physically and logically separate and EU-operated, with a €7.8B investment. First compliance milestone: **SOC 2 and BSI C5 Type 1** reports plus 7 ISO certifications covering 69 services[^esc].
  - It's still a US-parent structure, so CLOUD Act risk is reduced, not eliminated, and service parity is partial [I].
- **Microsoft**: the **EU Data Boundary** is complete, including AI processing. Microsoft Sovereign Cloud (Jun 2025) covers Sovereign Public Cloud, Sovereign Private Cloud on Azure Local (disconnected possible) and M365 Local[^ms-sov].
- **Google**: T-Systems Sovereign Cloud (DE, T-Systems-held keys), GDC air-gapped hosted by T-Systems, and S3NS (FR)[^gcp-sov].
- **EU-owned**: OVHcloud, Scaleway, **STACKIT** (C5, ISAE 3000/3402, OpenStack), Open Telekom Cloud, **IONOS** (C5 for compute and S3), Exoscale, Clever Cloud, Hetzner[^eu-prov].
  - **OVHcloud** holds SecNumCloud qualification for three offerings: **SNC Cloud Platform** (public cloud, 1 Sep 2026), **Bare Metal Pod** and **VMware on OVHcloud** [F][^ovh-snc]. The press release doesn't state the référentiel version (3.2 is the current one) [U].
  - Mature for IaaS, managed K8s, Postgres and S3. Thin on managed AI, global edge and long-tail PaaS. Design on commodity primitives and they become a credible primary **or exit target** [I].

**NIS2** [F]: Germany's NIS2UmsuCG has been in force since **6 Dec 2025** with no transition period. Scope grew from ~4.5k to ~29.5k entities, including cloud and DC providers, and registration was due by 6 Mar 2026[^nis2]. Art. 21 supply-chain security makes provider choice part of the client's own risk management. Many manufacturers are in scope as "important" entities [I]. Reviews record provider jurisdiction, certifications and the incident-reporting chain.

## Sources
[^finops]: https://www.nops.io/blog/new-finops-framework-changes-for-2025-6-key-takeaways/ · https://www.hyperglance.com/blog/cloud-finops/ (secondary; primary finops.org/framework)
[^focus]: https://focus.finops.org/focus-specification/ (lists 1.4 as current, checked 2026-10-10) · https://focus.finops.org/wp-content/uploads/2025/12/FOCUS_spec-v1_3.pdf
[^aws-vpc]: https://aws.amazon.com/vpc/pricing/
[^az-bw]: https://azure.microsoft.com/en-us/pricing/details/bandwidth/
[^gcp-net]: https://cloud.google.com/vpc/pricing-announce
[^hetzner]: https://docs.hetzner.com/robot/general/traffic/
[^xaz]: https://aws.amazon.com/blogs/architecture/exploring-data-transfer-costs-for-aws-managed-databases (AWS-owned; EC2 pricing table is JS-rendered)
[^az-nat]: https://prices.azure.com/api/retail/prices (Retail Prices API, productName 'NAT Gateway') · https://azure.microsoft.com/en-us/pricing/details/azure-nat-gateway/
[^gcp-nat]: https://cloud.google.com/nat/pricing
[^az-xaz]: https://azure.microsoft.com/updates/update-on-interavailability-zone-data-transfer-pricing (21 May 2024)
[^gcp-xaz]: https://cloud.google.com/vpc/network-pricing
[^sp]: https://docs.aws.amazon.com/savingsplans/latest/userguide/plan-types.html
[^spot]: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-instance-termination-notices.html · https://aws.amazon.com/ec2/spot/
[^aws-cost]: https://docs.aws.amazon.com/wellarchitected/latest/framework/cost-dp.html
[^idc-over]: https://idc.com/resource-center/blog/storm-clouds-ahead-missed-expectations-in-cloud-computing
[^a16z]: https://a16z.com/the-cost-of-cloud-a-trillion-dollar-paradox/
[^37s]: https://world.hey.com/dhh/our-cloud-exit-savings-will-now-top-ten-million-over-five-years-c7d9b5bd (primary, 17 Oct 2024) · https://www.thestack.technology/dhh-aws-egress-s3-pure/ · https://www.theregister.com/2025/05/09/37signals_cloud_repatriation_storage_savings · https://www.datacenterdynamics.com/en/news/37signals-begins-exiting-aws-storage-service/
[^ahrefs]: https://tech.ahrefs.com/how-ahrefs-saved-us-400m-in-3-years-by-not-going-to-the-cloud-8939dd930af8
[^idc-rep]: https://www.theregister.com/2024/10/30/cloud_repatriation_about_specific_workloads/
[^dataact]: https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32023R2854 (Arts. 25, 29, 34, 50 read verbatim 2026-10-10) · https://www.springlex.eu/en/packages/data-act/data-act-regulation/article-29/ · https://www.stephensonharwood.com/insights/the-eu-data-act-switching-interoperability-and-prevention-of-unauthorised-access-to-non-personal-data/
[^waiver]: https://www.infoq.com/news/2024/03/aws-egress-fees/ · https://assets.publishing.service.gov.uk/media/688b8169fc784fa12a089071/Appendix_N_-_Egress_fees___free_switching_programmes.pdf
[^dora]: https://presencis.com/regulations/dora/article-28 · https://www.afm.nl/en/sector/themas/belangrijke-europese-wet--en-regelgeving/dora/derde-aanbieders
[^eba]: https://www.eba.europa.eu/publications-and-media/press-releases/eba-publishes-its-final-guidelines-management-third-party-risk-delivering-more-proportionate-and
[^cloudact]: https://www.sdxcentral.com/news/microsoft-tells-french-lawmakers-it-cant-protect-user-data-from-us-demands/
[^c5]: https://www.bsi.bund.de/DE/Service-Navi/Presse/Pressemitteilungen/Presse2026/260407_C5_Cloud_Computing.html (7 Apr 2026) · https://www.bsi.bund.de/SharedDocs/Downloads/EN/BSI/CloudComputing/ComplianceControlsCatalogue/2026/C5_2026.html · transition dates: https://www.roedl.com/insights/der-neue-c5-katalog-ist-da-was-sie-jetzt-beachten-muessen/ (29 Apr 2026, secondary) · https://coalfire.com/the-coalfire-blog/c52025-community-draft
[^snc]: https://www.thalesgroup.com/en/news-centre/insights/group/s3ns-receives-secnumcloud-qualification-turning-point-trusted-cloud · https://next.ink/181303/bleu-valide-a-son-tour-le-jalon-j0-de-la-qualification-secnumcloud/
[^eucs]: https://www.amchameu.eu/position-papers/cybersecurity-certification-scheme-cloud-services-eucs
[^gaiax]: https://gaia-x.eu/gaia-x-summit-2025-showcases-the-next-phase-of-trusted-digital-ecosystems/ · https://en.ilsole24ore.com/art/europes-big-bet-on-the-cloud-remains-without-a-data-centre-AInU9xxD
[^esc]: https://press.aboutamazon.com/aws/2026/1/aws-launches-aws-european-sovereign-cloud-and-announces-expansion-across-europe · https://aws.amazon.com/blogs/security/aws-european-sovereign-cloud-achieves-first-compliance-milestone-soc-2-and-c5-reports-plus-seven-iso-certifications
[^ms-sov]: https://azure.microsoft.com/en-us/blog/microsoft-strengthens-sovereign-cloud-capabilities-with-new-services/
[^gcp-sov]: https://www.t-systems.com/gb/en/sovereign-cloud/solutions/sovereign-cloud-powered-by-google-cloud
[^ovh-snc]: https://corporate.ovhcloud.com/en/newsroom/news/ovhcloud-obtains-secnumcloud-qualification-snc-cloud-platform/
[^eu-prov]: https://www.softwareseni.com/the-european-sovereign-cloud-provider-landscape-in-2026-who-exists-and-what-they-offer/ · https://schwarz-digits.de/en/presse/archive/2024/sovereign-stackit-cloud-with-bsi-s-c5-isae-3000-soc-2-and-isae-3402-certified · https://www.ionos.co.uk/newsroom/news/ionos-gains-new-cloud-security-attestation-for-compute-engine-cloud-cubes-and-s3-object-storage/
[^nis2]: https://www.reedsmith.com/our-insights/blogs/technology-law-dispatch/102lxfr/finally-germany-enacts-its-nis2-law/
