# AI-Native Apps — app-architecture reference

*Snapshot retrieved 2026-10-10. [F] = sourced fact · [W] = vendor/secondary/contested · [I] = inference/judgment. Raw research: `output/.runs/20261010-app-architecture-skill/children/ai-native/RESPONSE.md`. Scope: an AI component **inside an app**. The internals of a single agent (harness, determinism boundary, conformance level) belong to [agent-architecture](../../agent-architecture/SKILL.md), and agent estates to [multi-agent-platform](../../multi-agent-platform/SKILL.md). Infra-level AI hosting (self-host GPUs vs API, residency endpoints by cloud) lives in [cloud-architecture heuristics §4](../../cloud-architecture/references/heuristics-and-failure-modes.md); this file owns the app-level design.*

## 1. The complexity ladder — climb one rung at a time
"Find the simplest solution possible, and only increase complexity when needed" [F][^bea]. Each step up needs eval evidence that the lower rung fails [I].

| Rung | Choose when | Avoid when |
|---|---|---|
| Plain code / rules | Deterministic logic, structured input | NL input, fuzzy classification |
| Single LLM call (+ retrieval, few-shot) | Classify, extract, summarize, draft | Multi-step with side effects |
| **Workflow** (chain / route / parallel / orchestrator-workers / evaluator-optimizer), written in code | Steps known in advance: **if you can draw the flowchart, it's a workflow** | Step count unknowable |
| Single agent (tool loop) | Open-ended, unpredictable step count, trusted environment, eval coverage exists | Any lethal-trifecta combination, no evals, prod write access |
| Multi-agent | Breadth-first, parallelizable, high-value work: ~+90% on Anthropic's research eval at **~15× chat tokens** | Shared-context or interdependent work, most coding [F][^multi] |

Rules:
- **No agent framework in v1** [F][^bea][^12f]. Use the provider SDK directly. Own your prompts, context window and control flow (12-Factor Agents #2, #3, #8).
- **An agent is a stateless reducer over persisted state** [F][^12f][I]. Unify execution state with business state, with pause and resume via simple APIs. Human contact is a tool call (#5–#7, #12). The event log lives in Postgres, not in framework memory.
- **Keep agents small and focused** [F][^12f][^ctx]. Sub-agents return condensed summaries of 1–2k tokens.
- **Multi-agent is the microservices of LLM apps** [I]. Require value per task > 15× the single-call cost before approving it.

## 2. Context and knowledge access
| Option | Choose when | Avoid when |
|---|---|---|
| Full context + prompt caching | Corpus < ~200k tokens, stable, no per-user ACLs [F][^cr] | Large or distractor-heavy corpora |
| **Hybrid RAG** (BM25 + embeddings + reranker) | Corpus > ~200k, changing, proprietary, ACL'd | Tiny corpus |
| Agentic / just-in-time retrieval (tools, grep, SQL) | Structured sources, code, agent tasks [F][^ctx] | Latency-critical single shot |
| Fine-tuning | Behaviour only: format, tone, consistency, ≥50 good examples [F][^oai-acc] | Injecting facts or fast-changing knowledge |

- **Long context is not free accuracy** [F][^rot][^ctx]. Chroma tested 18 models: reliability drops with input length well below window limits. Aim for the smallest set of high-signal tokens.
- **Hybrid retrieval beats vector-only** [F][^cr]. Anthropic measured retrieval-failure cuts of −35% (contextual embeddings), −49% (+ contextual BM25) and **−67%** (+ reranking). Pure-vector RAG is an anti-pattern.
- **pgvector until a measured ceiling** [W][^pgv]. The ceiling is roughly ≥ tens of millions of vectors, heavy metadata-filtered ANN, or index builds blocking deploys. Keep embeddings next to the rows they describe for ACL joins and consistency, and **filter by permission at query time**.
- **Pre-fetch what is certain; fetch just-in-time what is speculative** [I, reconciling 12-Factor #13 and Anthropic's context engineering].

## 3. Tools, and apps usable *by* agents
- **Design tools for agents, not as API mirrors** [F][^tools]. Consolidate (`schedule_event`, not list+list+create), namespace, return semantic names rather than UUIDs, and paginate or truncate by default. If an engineer can't choose between two tools, neither can the model.
- **Poka-yoke the interface** [F][^bea]. Give examples in parameter descriptions, and make misuse structurally impossible (absolute paths, enums).
- **Expose your app to agents through a narrow, task-shaped MCP server** over existing domain services, not a CRUD dump.
  - Use OAuth 2.1 + PKCE with per-session least-privilege tokens [F][^mcp-auth][^ghmcp].
  - The API stays the source of truth; MCP is an adapter [I].
  - OAuth grants delegated access, but per-tool-call authorization is still your job.
- **Protocols** [F][^lf][^a2a]:
  - **MCP** is the de facto tool protocol. It moved to the Linux Foundation's Agentic AI Foundation in Dec 2025; the current spec revision is 2026-07-28.
  - **A2A** is only for cross-org or cross-vendor agent interop. Inside one codebase, agents talking A2A is distributed-monolith cosplay; use function calls [I].

## 4. Evals are the test suite
- **Error analysis before metrics** [F][^evals]. Review ≥100 diverse traces, the first ≥30 yourself. One domain-expert "benevolent dictator" owns quality. Practitioners report 60–80% of dev time going to error analysis and evals.
- **Binary pass/fail per failure mode** [F][^evals]. No Likert scales, and no ROUGE/BERTScore-style generic metrics.
- **Validate every LLM judge** against held-out human labels and report TPR/TNR [F][^evals][^judge]. Judges show position, verbosity and self-preference bias. Use a different model family than the generator, and randomize order.
- **Run two loops** [F][^evals][^multi]:
  - CI evals gate every prompt, model or tool change.
  - Production monitoring catches drift.

  Start with ~20 real queries; early effect sizes are large enough to see.
- **Trace everything in prod**: every LLM call and tool call, with tokens, cost and latency [F][^multi].
- **Build eval tooling first, buy a platform later** [F][^evals]. This is the rare build-first exception to buy-the-commodity.
- **The eval suite is the real portability asset** [I]. Switching models means re-running the evals.

## 5. Security — injection is an architecture problem
- **Never ship the lethal trifecta in one context** [F][^trifecta]: private data + untrusted content + external communication. Remove one leg per agent or session; that is the only reliable defense.
- **Guardrail classifiers are not a security boundary** [F][^trifecta]. "95% blocked" is a failing grade. Use them for UX and abuse telemetry.
- **Isolate untrusted input architecturally** [F][^patterns][^camel][^dual]. Once an agent has read untrusted input, it must be unable to trigger consequential actions. Patterns:
  - action-selector
  - plan-then-execute
  - map-reduce
  - **dual-LLM** (the privileged model sees only `$VAR` references)
  - code-then-execute
  - context-minimization

  CaMeL gives provable security at a ~7-point utility cost (77% vs 84% on AgentDojo).
- **Model output is untrusted input** [F][^owasp-llm]: escape it, parameterize it, never `eval` it (OWASP LLM05). **Unbounded consumption is a security bug**: cap tokens, steps, iterations and time per user and per task (LLM10).
- **Map controls** to the OWASP LLM Top 10 2025 and the OWASP Top 10 for Agentic Applications 2026 (published Dec 2025; verify item names on the official page before quoting) [F][^owasp-llm][^owasp-ag].
- **Agents never get prod write credentials by default.** Destructive operations go behind human approval. "Instructions as access control" is the anti-pattern [F][^replit].

## 6. Cost, latency, durability
- **Prompt caching is architecture** [F][^cache]:
  - A cache read costs ~0.1× base; a 5-min write 1.25×, a 1-h write 2×. It breaks even after one read.
  - Order prompts tools → system → static docs → varying suffix.
  - No timestamps or request IDs in the cached prefix.
  - Any tool-definition change invalidates everything downstream.

  Verify multipliers per model on the live pricing page.
- **Batch API for async work** (~50% off, stacks with caching) [W][^batch]. **Tier models by route**: static routing first (task type → model); learned routers only once eval data exists [F][^routellm] (2024 benchmark: keep the ratio, not the numbers).
- **Unit cost per completed task**, including retries and agent loops, at 1× and 10× volume [I]. Multi-agent can reach 15× a chat [F][^multi].
- **Durable execution** [F][^multi][^temporal][I]:
  - Request/response for <~30 s with no side effects.
  - A Postgres job/state table with idempotent steps for minutes-scale work.
  - Temporal (or equivalent) for hours- or days-long runs and human-approval signals.

  Deploy gradually so in-flight agents survive releases. HITL is a tool call plus a durable wait.

## 7. Provider abstraction and residency
- **Thin, owned adapter by default** [I][^litellm]. Use a ~1-file interface over the provider SDK, not a mega-gateway by reflex. If you adopt a gateway, pin versions, verify hashes and isolate its secrets: LiteLLM 1.82.7/1.82.8 were trojaned on PyPI on 2026-03-24 with a credential-stealing payload.
- **Provider-specific features are worth the lock-in** when they cut cost or latency by >50% (caching, batch, citations). A lowest-common-denominator abstraction forfeits them [I].
- **Residency is a day-1 routing decision per data class** [F][^anth-res][^oai-eu]:
  - Anthropic's first-party API offers `inference_geo` of only `us` or `global`, with at-rest storage in the US only (as of 2026-10). EU-resident Claude means Bedrock EU profiles or Vertex EU regions.
  - OpenAI EU residency requires new EU projects; existing ones can't be converted.

  Classify each data class (personal / confidential / public), route it to a compliant endpoint, and decide before the first project or workspace is created.
- **AI Act Art. 50** has applied since 2 Aug 2026. Build AI disclosure and content labelling into UI components, and log model, prompt version, inputs and outputs for traceability. See [quality-and-compliance.md §6](quality-and-compliance.md).

## 8. Failure modes (real cases → design rule)
| Case | Rule |
|---|---|
| *Moffatt v. Air Canada* (2024): the airline was held liable for a policy its chatbot invented [F][^aircanada] | Policy and price answers are grounded and cited, or deflected |
| Cursor support bot "Sam" (Apr 2025) invented a login policy [F][^cursor] | Label AI, ground in docs, escalate unknowns |
| Replit agent (Jul 2025) wiped a production DB during a freeze [F][^replit] | No prod write credentials; dev/prod separation; HITL for destructive actions |
| EchoLeak CVE-2025-32711 (M365 Copilot, CVSS 9.3): zero-click exfiltration via email [F][^echoleak] | Break the trifecta |
| GitHub MCP (May 2025): a public issue made an agent leak private-repo data [F][^ghmcp] | Per-session scoped tokens; the fix is architectural, not a patch |
| LiteLLM PyPI compromise (Mar 2026) [F][^litellm] | A gateway concentrates credentials: pin, verify, isolate |
| Klarna (2024–25): automated most chats, then rehired humans [W][^klarna] | Always keep a human escape hatch |
| MIT NANDA (2025): ~95% of pilots showed no P&L impact (contested) [W][^nanda] | Integration and learning loops matter more than model choice; cite as directional only |
| Framework-first agents, vibes-based evals, context stuffing, cache-busting prompt layouts, multi-agent for coupled work [F][^bea][^evals][^rot][^cache][^multi] | See §1–§6 |

## 9. AI red-flag checklist (add to the structure-and-stack checklist)
1. An agent where a workflow would do; multi-agent without a 15× value case.
2. An agent framework in v1, with prompts and control flow not owned in code.
3. No frozen eval set with a pass bar; unvalidated LLM judges; Likert scores.
4. Private data + untrusted content + outbound channel in one context.
5. Guardrail classifier presented as the security control.
6. Agent credentials with prod write access; no human approval on irreversible actions.
7. No token/step/time caps per user and per task.
8. Vector-only RAG; no permission filter at query time.
9. Cache-busting prompt layout; no cost per completed task.
10. Residency not decided before creating the provider project or workspace.
11. No AI disclosure in the UI (AI Act Art. 50).

## Sources
[^bea]: https://www.anthropic.com/engineering/building-effective-agents
[^multi]: https://www.anthropic.com/engineering/multi-agent-research-system
[^ctx]: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
[^tools]: https://www.anthropic.com/engineering/writing-tools-for-agents
[^12f]: https://github.com/humanlayer/12-factor-agents
[^trifecta]: https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/
[^patterns]: https://arxiv.org/abs/2506.08837
[^camel]: https://arxiv.org/abs/2503.18813
[^dual]: https://simonwillison.net/2023/Apr/25/dual-llm-pattern/
[^cr]: https://www.anthropic.com/engineering/contextual-retrieval
[^rot]: https://research.trychroma.com/context-rot
[^oai-acc]: https://developers.openai.com/api/docs/guides/optimizing-llm-accuracy
[^pgv]: https://www.tigerdata.com/blog/pgvector-is-now-as-fast-as-pinecone-at-75-less-cost (vendor) · https://ecorpit.com/pgvector-vs-dedicated-vector-database-rag-decision-2026/ (secondary)
[^mcp-auth]: https://modelcontextprotocol.io (spec 2026-07-28) · https://www.permit.io/blog/mcp-auth-vs-tool-call-authorization-2026-07-28
[^ghmcp]: https://invariantlabs.ai/blog/mcp-github-vulnerability
[^lf]: https://redmondmag.com/articles/2025/12/09/linux-foundation-launches-agentic-ai-foundation.aspx
[^a2a]: https://linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year
[^evals]: https://hamel.dev/blog/posts/evals-faq/
[^judge]: https://arxiv.org/abs/2306.05685
[^owasp-llm]: https://genai.owasp.org/llm-top-10/
[^owasp-ag]: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
[^replit]: https://www.thestack.technology/vibe-coding-ceo-deletes-production-database/
[^cache]: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
[^batch]: https://www.eesel.ai/blog/anthropic-api-pricing (secondary; verify on official pricing page)
[^routellm]: https://lmsys.org/blog/2024-07-01-routellm/
[^temporal]: https://temporal.io/blog/announcing-openai-agents-sdk-integration (vendor)
[^litellm]: https://securitylabs.datadoghq.com/articles/litellm-compromised-pypi-teampcp-supply-chain-campaign/
[^anth-res]: https://platform.claude.com/docs/en/manage-claude/data-residency
[^oai-eu]: https://openai.com/index/introducing-data-residency-in-europe/
[^aircanada]: https://www.law360.ca/ca/articles/1804075
[^cursor]: https://incidentdatabase.ai/entities/cursor-ai-support-bot-(%22sam%22)/
[^echoleak]: https://socprime.com/blog/cve-2025-32711-zero-click-ai-vulnerability/
[^klarna]: https://tech.co/news/klarna-reverses-ai-overhaul
[^nanda]: https://fortune.com/2025/08/18/mit-report-95-percent-generative-ai-pilots-at-companies-failing-cfo/
