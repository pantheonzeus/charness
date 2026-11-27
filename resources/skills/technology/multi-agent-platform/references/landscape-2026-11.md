# Landscape snapshot — agents, protocols, platforms, regulation (retrieved 2026-11-27)

**Dated snapshot; supersedes `landscape-2026-10.md`. Re-verify every item before it lands in a client deliverable**, and treat anything here older than a month as stale (red-flag list in SKILL.md). Tags:
- **[D]** read in the primary source on retrieval;
- **[S]** secondary source or search summary only;
- **[I]** inference.

Run of record: `output/.runs/20261127-multi-agent-frontier/` (four fresh research children, a claim register and a parent verification pass).

## 1. Design guidance
- **Split by context, not by role.** Anthropic: go multi-agent only for context protection, parallelisable work, or specialisation (20+ tools, conflicting behaviours). Budget 3–10x tokens. Role splits (planner/implementer/tester) cost more in coordination than they save. [D] https://claude.com/blog/building-multi-agent-systems-when-and-how-to-use-them (2026-01-23)
- **Five coordination patterns:** generator-verifier, orchestrator-subagent (the recommended start), agent teams, message bus, shared state. Shared state needs a designed termination condition; LLM routers on a message bus fail silently. [D] https://claude.com/resources/articles/multi-agent-coordination-patterns (2026-04-10)
- **A separate evaluator is the strongest lever in long-running harnesses, and scaffolding should shrink as models improve.** Anthropic dropped sprints and context resets moving from Opus 4.5 to 4.6. [D] https://anthropic.com/engineering/harness-design-long-running-apps (2026-03-24)
- **Cognition narrowed "Don't build multi-agents"** to: writes stay single-threaded; read-only context subagents and a no-shared-context reviewer work; parallel-writer swarms and unstructured agent networks still fail. [D] https://cognition.com/blog/multi-agents-working (2026-04-22)
- Baseline, still valid: the cost multiples (agents ≈ 4x, multi-agent ≈ 15x chat tokens) and the +90.2% internal research eval. [D] https://www.anthropic.com/engineering/multi-agent-research-system (2025)

## 2. Evidence on single vs multi (compute-matched)
- At equal thinking-token budgets, single agents match or beat MAS on multi-hop reasoning. [D] arXiv 2604.02460 (2026-04-02)
- BenchAgent: only 1 of 6 MAS workflows beat a single-agent reference across 10 benchmarks (GPT-4.1). [D] arXiv 2606.05670 (v2 2026-10-09)
- Google scaling study: centralised coordination helps parallelisable work and every MAS variant degrades sequential planning. Independent agents amplify errors far more than centralised ones. The blog's figures (180 configs, +81% / −39 to −70%, 17.2x vs 4.4x, R² 0.513) are v1. The revised paper reports 260 configs and R² 0.373. Quote the direction, and date any number. [D] blog https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/ (2026-01-28); [D-abstract] arXiv 2512.08296
- The one new positive result: many small parallel teams plus a verifier, on machine-checkable tasks. [D] arXiv 2611.09798 (2026-11-06, not replicated)

## 3. Handoffs and verification (the 2026 research that changes packet design)
- **Handoffs lose rules, not facts.** Summarised handoffs deactivated blockers in 76.7–97.2% of cases; the full blocker text took forbidden actions from 85.2% to 0.0%. [D] arXiv 2608.24569 (2026-08-25). Boundary metadata collapses under compression while facts survive; typed constraints fix it. [D] arXiv 2608.29028 (2026-08-29). Good packets mainly buy efficiency (20–59% fewer successor events). [D] arXiv 2606.02875
- **Self-verification is biased.** Self-authored errors were approved 11.9 pp more often; judge panels fail together without an executable check. [D] NeurIPS 2026 workshop https://neurips.cc/virtual/2026/178251
- **NLAH v2** (2026-05-18, Table 5; supersedes v1's −0.8/−8.4 verifier figures): file-backed state +2.6 SWE / +13.9 OSWorld, self-evolution +5.8 / +8.4, verifier +0.2 / +8.4, evidence-backed answering +2.8 / +2.8, multi-candidate search −1.6 / +2.8, context compression −1.0 / −8.3, markdown memory −2.8 / +5.6. [D] https://arxiv.org/html/2603.25723v2
- **AHE:** Terminal-Bench 2 went from 69.7% to 77.0%; the gains came from tools, middleware and memory, not the system prompt, and transferred across model families. [D] arXiv 2604.25850 (v5 2026-11-22)
- Debate adds little over voting. [S] arXiv 2508.17536 (2025)

## 4. Frameworks and runtimes
- **Claude Code** subagent frontmatter: `tools`, `disallowedTools`, `maxTurns`, `skills` (full content preloaded), `isolation: worktree`, `omitClaudeMd`, `effort`, `memory`, `background`, `hooks`. Subagents nest by default (depth var [S]). Combined descriptions over 15k tokens warn at startup. [D] https://code.claude.com/docs/en/sub-agents. Agent teams are experimental and **not spawned in `-p`**. [D] https://code.claude.com/docs/en/agent-teams. Dynamic workflows have been a research preview since 2026-05-25. [D] what's-new wk22. In CLI 2.1.319, `-p` main contexts have no WebFetch and use the `web-fetch` subagent instead (local canary, 2026-11-27).
- **Managed Agents:** session log / harness / sandbox separated (2026-04-08); multiagent (beta), outcomes (separate grader) and dreaming (2026-05). Vendor numbers are unreplicated. [D]
- **OpenAI:** the Agents SDK (2026-04-15) externalises state and separates the sandbox. Codex subagents (Mar 2026) gained agent-tree suspend/resume and a mailbox (CLI 0.171–0.172, Nov 2026). [D]
- **Microsoft Agent Framework orchestration 1.0** (2026-07-08): five patterns; magentic guards with round/stall/reset counters. [D]
- **Google ADK 2.0** (Python GA 2026-05-19): a graph workflow runtime replaces the Sequential/Parallel/Loop agents. [S]
- **LangChain Deep Agents** has async subagents (v0.5, 2026-04). [S]
- [I] Every vendor is shipping the file-backed pattern: an append-only log, resumable workers, and a mailbox or packet.

## 5. Skills and routing
- **Agent Skills** went to the Agentic AI Foundation (Linux Foundation) on 2026-10-22; Anthropic reports 70+ platforms (vendor count). [D]
- **Routing needs the skill body:** hiding it costs 37–44 points of routing accuracy. [D] arXiv 2603.22455. On-demand, agent-written skill queries beat static preselection on multi-step work. [D] arXiv 2610.23554
- **Skill gains** shrink toward the no-skill baseline under realistic retrieval. [D] arXiv 2604.04323. Single agent plus skills holds until confusable skills collide. [D] arXiv 2601.04748
- **Expert personas** don't raise accuracy. [D] arXiv 2512.05858, 2603.18507

## 6. Protocols
- **MCP 2026-07-28** (fifth spec): stateless core (`server/discover`, no sessions); Tasks became an extension (poll/update); server-initiated requests were replaced by `input_required` round trips; Roots, Sampling, Logging, HTTP+SSE and DCR are deprecated with a ≥ 12-month window; clients must validate `iss` (RFC 9207); OTel `traceparent` travels in `_meta`. [D] https://modelcontextprotocol.io/specification/2026-07-28/changelog
- **A2A** v1.0 (Mar 2026, signed agent cards) joined the AAIF on 2026-08-17. [D] https://aaif.io/blog/a2a-joins-aaif
- **ACP:** IBM's ACP folded into A2A (2025); AGNTCY's "Agent Connect Protocol" is a different thing. Name the owner whenever you write "ACP". [D/S]

## 7. Control plane, identity, security, observability
- **Registry + identity + gateway** is the trio all three hyperscalers ship: Microsoft Agent 365 / Entra Agent ID [D]; AWS Agent Registry (GA Aug 2026) [D]; Google Gemini Enterprise Agent Platform (Apr 2026) [D].
- **Out-of-band deterministic defences hold** (CaMeL, FIDES, Progent class); 12 in-band defences were broken above 90% by adaptive attacks. Only one weak adaptive reproduction exists. [D] arXiv 2606.26479. Typed-field admission: arXiv 2611.07222 (SPILLWAY). Taints propagated through the delegation graph: arXiv 2607.25255 (SafeFlow). Provenance plus per-role privilege: −91% inter-agent injection (workshop). [D] arXiv 2609.22949
- **Memory poisoning** is a separate surface, and more aggressive memory is more exploitable. [D] arXiv 2606.04329
- **The Claude Code sandbox covers Bash only;** built-in tools, hooks and local MCP run outside it. `Bash(curl *)`-style allow rules auto-approve the escape. [D] https://code.claude.com/docs/en/sandboxing
- **OTel GenAI agent spans** (`invoke_agent`, `execute_tool`, `gen_ai.agent.name`, `gen_ai.conversation.id`) are still Development. Don't sum parent and child usage. [D] semantic-conventions-genai repo
- **OWASP Top 10 for Agentic Applications** (ASI01–10, "least agency"). [S] https://genai.owasp.org (2025-12-09). NIST CAISI agent initiative: no final guidance (page updated 2026-11-09). [D]. IETF agent-auth work: individual drafts only. [S]

## 8. EU AI Act after the Digital Omnibus
- In force 27 Jul 2026 (OJ 24 Jul 2026). Annex III high-risk moves to **2 Dec 2027**; Annex I to **2 Aug 2028**. Art. 50 transparency has applied since **2 Aug 2026**; content marking for systems already on the market by 2 Dec 2026. AI literacy was relaxed to "support and document". [S] Lewis Silkin (2026-07-27), Gibson Dunn (2026-05-27). **EUR-Lex not read: read the legal text before advising.** The Machinery-Regulation carve-out (Oct snapshot) is still unverified.

## 9. Sovereignty and industrial
- Unchanged since the Oct snapshot (`landscape-2026-10.md` §7: sovereign model hosting, orchestrator + specialist agents, MCP as the OT data layer, edge inference). Not re-verified in this run.

## Contested
- Single vs multi: Anthropic, Cognition and the compute-matched papers agree on "bounded, clean context, one writer"; agent teams and dynamic workflows push toward more agents. Most compute-matched studies use older or open models.
- Verifiers: positive with an executable anchor or on OSWorld-like tasks (NLAH v2 +8.4); near zero on SWE (+0.2); biased when self-judging.
- Handoff format ranking (raw trace vs structured notes) depends on the model; nothing yet for Claude-family receivers.
- CaMeL/FIDES under adaptive attack: no independent numbers.
