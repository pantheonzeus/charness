# Landscape snapshot — agents, protocols, platforms, regulation (retrieved 2026-10-10)

**Dated snapshot. Re-verify every item before it lands in a client deliverable.** Tags:
- **[D]** read in the primary source on retrieval;
- **[S]** secondary source only (trade press or aggregator);
- **[I]** inference.

## 1. Design guidance
- **Workflow vs agent is the first fork.** Start with the simplest solution; agents trade latency and cost for task performance. The pattern ladder: prompt chaining → routing → parallelization → orchestrator-workers → evaluator-optimizer → autonomous agent. Tool (ACI) design matters as much as prompts. [D] https://www.anthropic.com/research/building-effective-agents
- **Cost multiples:** agents ≈ 4× the tokens of chat; multi-agent ≈ 15×. A multi-agent setup (lead + sub-agents) beat a single agent by 90.2% on an internal research eval. It is a poor fit when agents share context or have many interdependencies. Failure modes: over-spawning, endless search, vague delegation. Fixes: explicit delegation, effort-scaling rules, parallel tool calls. [D] https://www.anthropic.com/engineering/multi-agent-research-system
- **Counter-position:** share full context and traces, because "actions carry implicit decisions". Default to a single-threaded agent. [D] https://cognition.com/blog/dont-build-multi-agents
- **Read-heavy multi-agent is easier than write-heavy.** [D] https://blog.langchain.com/how-and-when-to-build-multi-agent-systems
- **Context engineering:** context rot; compaction; external notes; sub-agents with clean contexts; just-in-time retrieval. [D] https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents — long-running agents use an initializer plus a progress file and incremental sessions. [D-snippet] https://anthropic.com/engineering/effective-harnesses-for-long-running-agents
- **OpenAI practical guide:** start with one agent and split on eval evidence. The two shapes are manager (agents-as-tools) and decentralized handoff. [S] via https://agentic-ai.readthedocs.io/en/latest/DesignPatterns/openai-patterns/

## 2. Frameworks (a platform choice, not the architecture)
- Microsoft Agent Framework 1.0 GA (Apr 2026) unifies Semantic Kernel and AutoGen; AutoGen is in maintenance. [S] https://devblogs.microsoft.com/agent-framework/
- Google ADK: LLM agents plus Sequential/Parallel/Loop workflow agents, and MCP tools. [S] https://cloud.google.com/blog/products/ai-machine-learning/build-multi-agentic-systems-using-google-adk
- [I] All major SDKs ship the same primitives. Choose by cloud, identity and skills stack.

## 3. Protocols
- **MCP** is under the Agentic AI Foundation (Linux Foundation) since Dec 2025, alongside goose and AGENTS.md. [D-snippet] https://blog.modelcontextprotocol.io/posts/2025-12-09-mcp-joins-agentic-ai-foundation/
- **MCP spec 2026-07-28.** [D] https://aaif.io/blog/mcp-2026-07-28-whats-changing-and-how-to-migrate
  - Stateless: no init handshake, `server/discover`, load-balancer friendly.
  - New extensions: MCP Apps and Tasks (async, durable IDs).
  - Auth: OAuth 2.1/OIDC plus Enterprise-Managed Authorization.
  - **Deprecated** (removal ≥ 2027-07-28): Roots, Sampling, Logging (→ OpenTelemetry), Dynamic Client Registration, HTTP+SSE.
  - Servers act as OAuth resource servers (RFC 9728); clients send RFC 8707 resource indicators. [S] https://workos.com/blog/mcp-2026-spec-agent-authentication
- **A2A** for agent↔agent: Linux Foundation, with a TSC spanning AWS, Cisco, Google, IBM, Microsoft, Salesforce, SAP and ServiceNow. [D] https://a2a-protocol.org/latest/ — v1.0 with signed Agent Cards; IBM's ACP merged into A2A. [S] https://zuplo.com/blog/agent-protocol-stack-mcp-a2a-acp-2026
- **Gateways:** agentgateway (Linux Foundation) proxies LLM, MCP and A2A traffic with authz, rate limits and observability. [S] https://linuxfoundation.org/press/linux-foundation-welcomes-agentgateway-project-to-accelerate-ai-agent-adoption-while-maintaining-security-observability-and-governance
- **AGNTCY:** not verified. Treat as unknown.

## 4. Identity and observability
- Microsoft Entra Agent ID: agent identity blueprints and OAuth OBO with agent impersonation. [D-snippet] https://learn.microsoft.com/en-us/entra/agent-id/agent-on-behalf-of-oauth-flow — the IETF OBO-for-agents draft is an individual draft, not adopted. [S] https://workos.com/blog/oauth-on-behalf-of-ai-agents
- OTel GenAI semantic conventions define agent spans (`create_agent`, `invoke_agent`, `execute_tool`) but are still at **Development** stability. Pin the version. [S] https://www.dash0.com/knowledge/opentelemetry-genai-semantic-conventions-explained

## 5. Research on harnesses and failures
- **MAST** (NeurIPS 2025): 1,642 traces, 14 failure modes. System design 43.7% (step repetition 15.7%, unaware of termination 12.4%, task-spec disobedience 11.8%). Inter-agent misalignment 45.3%. Verification 11.0%. Prompt and role fixes gained only +9–16%. [D] https://arxiv.org/html/2503.13657v3
- **NLAH** (arXiv 2603.25723) module ablation on SWE-bench Verified: self-evolution +4.8, file-backed state +1.6, evidence-backed answering +1.6, dynamic orchestration 0.0, verifier −0.8, multi-candidate search −2.4. [D] https://arxiv.org/html/2603.25723v1
- **AHE** (arXiv 2604.25850): observability-driven harness evolution took Terminal-Bench 2 from 69.7% to 77.0% in 10 iterations. [D] https://arxiv.org/abs/2604.25850
- **τ-bench:** pass^k consistency; gpt-4o scored under 25% pass^8 in retail. [D-snippet] https://arxiv.org/abs/2406.12045

## 6. EU AI Act after the Omnibus (Reg. (EU) 2026/1744 [S])
- Art. 50 transparency: **2 Aug 2026**. Watermarking has a grace period to 2 Dec 2026 for systems already on the market.
- Annex III high-risk: **2 Dec 2027**. Annex I (AI in regulated products): **2 Aug 2028**.
- AI embedded in products under the **Machinery Regulation** is largely exempted. Read the legal text before advising on scope.

Source: [D] https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/ (provisional agreement, May 2026); final adoption [S] https://secureprivacy.ai/blog/eu-ai-act-digital-omnibus-the-new-high-risk-ai-deadlines-after-council-approval

## 7. Sovereignty and industrial
- SAP + Mistral (Nov 2025): sovereign agents in SAP AI Foundation; Mistral's open weights are self-hostable. [D-snippet] https://news.sap.com/2025/11/sap-mistral-ai-new-alliance-european-sovereign-ai/
- Siemens (May 2025): an orchestrator over specialist agents including physical ones, Copilots across the value chain and a planned agent marketplace. "Up to 50%" productivity is a vision claim. [D] https://news.siemens.com/en-us/ai-agents-manufacturing
- Bosch Rexroth ctrlX: multiple agents plus an LLM running locally on edge hardware under ctrlX OS. The Data Layer is exposed through a central MCP server, and an embedded agent turns goals into engineering tasks. [S] https://www.computer-automation.de/industrial-computing/bosch-rexroth-and-amd--ai-agents-running-locally-on-ctrlx-os.htm (the primary page returned 403)
- [I] Industrial convergence: orchestrator + specialists, MCP as the OT data adapter, edge inference. No independent production metrics were found.

## Contested
- Whether to go multi-agent at all: Anthropic vs Cognition. It depends on task shape.
- Verifiers: MAST favours them, NLAH measured −0.8. Align any verifier with the real acceptance criterion.
- These are secondary-source only: the OpenAI guide's split criteria, A2A v1.0 details, the Microsoft Agent Framework GA date and the final Omnibus text.
