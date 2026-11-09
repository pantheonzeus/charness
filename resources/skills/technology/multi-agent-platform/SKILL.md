---
id: multi-agent-platform
aliases: [multi-agent-platform]
name: "Multi-Agent Platform & Orchestration — Lanes, Research Firewall, Three Clocks & Control Plane"
category: technology
description: Architect a multi-agent system or an enterprise agent estate. Decide single vs multi-agent on price and task shape (agents ~4x, multi-agent ~15x chat tokens; parallelize reads, serialize writes). Classify each agent into a lane (gated process / bounded loop / research) and put a research firewall in code so outside-sourced claims can never fire a decision. Pick the topology and delegation packet against the known multi-agent failure modes. Separate the three clocks of orchestration (model gateway / agent runtime / process engine, with a two-of-four trigger rule for Temporal/Camunda). Specify the shared control plane (registry, policy repo, ledger, audit chain, evals/shadow, gateway, agent identity, ingest screening) on MCP/A2A/OTel seams, and a placement procedure plus conformance levels so the estate stays governable at agent twenty.
triggers: [multi-agent, multi agent system, multi-agent platform, agent platform, agent orchestration, orchestrate agents, orchestration layer, agent estate, agent landscape, many agents, 20 agents, orchestrator worker, supervisor agent, agent handoff, agent swarm, subagents, agent to agent, A2A, MCP gateway, agent gateway, agent registry, agent control plane, agent governance platform, agent identity, agent observability, OpenTelemetry agents, Temporal or Camunda, workflow engine for agents, research agent, deep research agent, agent monorepo, agent reference architecture, which orchestration framework, AI Act agents, harness as a service, scale my harness, team harness, company harness, explain orchestration to the client, plug-in standard, policy as harness, trust levels]
tags: [technology, architecture, ai-agents, multi-agent, orchestration, platform, governance]
related: ["[[agent-architecture]]", "[[agentic-service-blueprint]]", "[[agentic-service-evaluation]]", "[[agent-ready-service]]", "[[ai-opportunity-portfolio]]", "[[ecosystem-platform-design]]", "[[cloud-architecture]]", "[[operating-model-design]]", "[[decision-memo]]"]
modules: [file-backed-state, evidence-backed-answering, verifier-separation]
status: active
version: 3
created: 2026-10-10
updated: 2026-11-09
requires:
  tools: [web_search, web_fetch]
  optional: [python3 (scripts/research_firewall.py reference implementation + selftest)]
environment: "Runs anywhere. references/landscape-2026-10.md is a dated snapshot (protocols, frameworks, EU AI Act Omnibus dates, industrial vendors); several items are secondary-source only and marked so — re-verify before client use."
references: [references/landscape-2026-10.md, references/decision-questions.md, references/harness-scaling.md, references/enterprise-orchestration-primer.md, references/worked-example-registry.md, ../agent-architecture/references/harness-patterns.md]
---

# Multi-Agent Platform & Orchestration — Lanes, Research Firewall, Three Clocks & Control Plane

> Twenty agents built on a shared framework are still a collection, not an estate. The difference is a registry, a firewall and a control plane, and none of those comes from a framework vendor.

## Contract
- **Input:** one of three modes.
  - **Design:** a multi-agent system for one problem, or a platform for an agent program (N planned agents).
  - **Review:** an existing estate, orchestration-layer proposal or framework decision to red-team.
  - **Counter:** a peer team's or vendor's architecture to answer in a meeting.

  Also collect the agent list (or the use cases), the systems of record, the cloud/identity stack, the regulation and the team topology.
- **Output:** `output/<YYYYMMDD>-<slug>-agent-platform.md` containing:
  - (a) the 3–5 decisions to take, up front;
  - (b) the single-vs-multi verdict with a token/cost estimate;
  - (c) the lane register (agent · lane · level · owner · identity mode · budget);
  - (d) the research-firewall spec;
  - (e) the topology and delegation-packet spec;
  - (f) the three-clocks table with the workflow-engine trigger check;
  - (g) the control-plane table with build/buy per service;
  - (h) protocol and identity seams;
  - (i) the repo and registry shape;
  - (j) a trigger-based sequencing plan;
  - (k) the risk register.

  Counter mode instead produces a question set and a one-page counter ([decision-questions.md](references/decision-questions.md)). Index the output into `cbrain/notes/Deliverables/` per Charter §4.
- **Allowed tools/artifacts:** conversation, client architecture docs and repos (read-only), web search for current protocol, framework and regulatory facts, `scripts/research_firewall.py` for demos.
- **Done when:**
  - every agent has a lane and a conformance level;
  - the firewall is specified as a code boundary with a test;
  - the multi-agent choice carries a cost multiple and the task-shape reason;
  - the workflow-engine decision cites which of the four triggers fire;
  - every control-plane service has an owner and a build/buy line;
  - protocol and regulatory facts carry source + date (secondary-only marked);
  - the verifier pass (step 10) records PASS.

## Triggers/Context
- Any ask about several cooperating agents, an agent platform or program, orchestration, an agent registry or gateway, agent-to-agent protocols, or "which orchestration framework for our N agents?".
- **Hand-offs:**
  - Each individual agent's internals (need-gate, determinism boundary, harness, evals, level) → `agent-architecture`. Run it per agent, or at least for the reference agent.
  - Human–agent work division inside a service → `agentic-service-blueprint`.
  - Service-level rollout and scorecard → `agentic-service-evaluation`.
  - Where agents pay off → `ai-opportunity-portfolio`.
  - An agent *marketplace* or ecosystem business → `ecosystem-platform-design`.
  - Infrastructure, hosting and sovereignty cost → `cloud-architecture`.
  - The platform team's operating model → `operating-model-design`.

## Operating principles (enforceable)
1. **Multi-agent must earn its 15×.** Default to one agent, or a workflow. Go multi-agent only when the task is breadth-first and parallelizable, high-value enough to pay ~15× chat tokens (single agent ~4×), and evals show the single agent failing. A multi-agent system fits badly when agents must share context or have dense interdependencies. State the Anthropic-vs-Cognition disagreement honestly: this is task-shape dependent, not settled.
2. **Parallelize reads, serialize writes.** Sub-agents may explore in parallel and return condensed, cited findings. Exactly one writer owns each artifact or side effect. Parallel writers make conflicting implicit decisions.
3. **Lanes before frameworks.** Classify every agent by what it is trusted for, not by the library it uses:
   - **A — gated process:** fixed order, reproducible, human gate, no cross-run memory.
   - **B — bounded loop:** a deterministic graph with exactly one agentic node under a tool budget, whose output is re-verified downstream.
   - **C — research:** orchestrator-worker, non-reproducible by design, budgeted, cross-run memory allowed.

   Never standardize on one agent shape. Cross-run memory is a feature in C and a defect in A.
4. **The research firewall is code, not convention.** Claims sourced outside the client's systems of record are `external` (URL, retrieval date, run id, source tier). `gate_eligible()` returns False for them, and a gated step that tries to use one raises an error and stops. Promotion to `observation` happens only by re-verification against a named system, as an audited event with an owner — never automatic, never by a model. This is what lets research agents run unattended next to decision agents: **autonomy is cheap where the blast radius is bounded.** Reference implementation: `scripts/research_firewall.py`.
5. **Lane B must pass a rejection test.** Teams will claim B for everything. Before granting it, name the single step whose tool sequence is genuinely unknowable in advance, show that the rest is fixed, and show the downstream re-verification. If you can't name it, the agent is lane A. If there are several such steps, it's a lane-C problem or a redesign.
6. **Delegation is a file packet, not a chat message.** The packet holds objective, inputs by path, output schema, tool allowlist, boundaries, budget (sub-agents, tool calls, wall-clock, tokens) and termination condition. The receiving agent starts **fresh** from it and writes its result back to a path. These fields target the MAST failure modes directly: step repetition, unawareness of termination, task-spec disobedience, derailment, and verification that is missing or superficial.
7. **Three clocks, three owners.** The **model gateway** (per call: routing, quota, cost attribution, logging, model swap) is mandatory from agent one. The **agent runtime** (seconds to hours: steps, state, resume, gate) is per agent team. **Process orchestration** (weeks to months: sequence, SLA, escalation, compensation) is introduced only when **any two** of these fire:
   - more than two agents share one transaction whose state outlives them all;
   - a handoff must survive a multi-day human wait with an SLA;
   - a failed downstream step must compensate an upstream side effect;
   - process owners outside engineering must read or change the sequence.
8. **Standards at the seams, files inside.** MCP for agent↔tool: one server per system of record, read/write split and attribution enforced at the server. A2A for agent↔agent **across a boundary** (another unit, another vendor, a counterparty's agent), designed as a thin adapter over the internal file packet. Inside one estate with one audit chain, a file packet is simpler and more auditable than RPC. Route LLM, MCP and A2A traffic through a gateway.
9. **Identity cannot be deferred past agent two.** Every agent gets its own identity. Use delegated (on-behalf-of the user) mode for lanes A and B, and service identity for lane C and scheduled work. Read and write are separate identities, scopes are declared in the registry and enforced at the tool plane, and autonomous actions are logged as themselves.
10. **Register before code.** No agent is built before its registry entry exists: lane, level, owner, policy path, identity and mode, data scopes, budget, eval suite. Promotion between levels is a review with a named approver. This is what stops prototype drift.

## Core Blueprint
Substantive runs keep a STATE_ROOT at `output/.runs/<YYYYMMDD>-<slug>-agent-platform/` with `RESPONSE.md` (steps 1–10 as boxes) and `EVIDENCE.md`.

1. **Frame mode, outcome and the decisions.** Design / Review / Counter. Name the business outcome of the program and the 3–5 decisions the client must take, and put them first in the deliverable. Check that each agent has a use-case card with a kill criterion (`agent-architecture` principle 1). Use cases without one are parked, not architected.
2. **Single vs multi.** For each problem, apply principles 1–2. Estimate tokens per run × runs per month × the multiple. Record the task-shape reason (read-heavy breadth vs write-heavy coupling).
3. **Lane every agent.** Build the lane register. Apply the placement procedure in [decision-questions.md §Placement](references/decision-questions.md) and the lane-B rejection test (principle 5). Assign each agent a target conformance level (L0/L1/L2, defined in `agent-architecture/references/harness-patterns.md`).
4. **Specify the firewall.** Claim classes, source tiers (primary/official · industry-authoritative · press · unattributed), the promotion path with its owner and systems of record, and the code boundary with its test. Put the source-tier distribution on the face of every research deliverable. Demo it with `python3 scripts/research_firewall.py --selftest`.
5. **Choose topologies.** Per multi-agent problem: manager / agents-as-tools (one agent owns the user and the synthesis), handoff (control truly transfers), or a deterministic graph (anything predictable). Use orchestrator-worker for research, with no peer-to-peer channel between workers. Specify the delegation packet (principle 6) and the effort-scaling rule, i.e. how many workers for how hard a question, so the orchestrator doesn't spawn 50 sub-agents for a simple query.
6. **Three clocks.** Fill the table: gateway product and owner, runtime(s) per lane, and the process engine (record which of the four triggers fire; "none yet" is a valid answer). If two fire, schedule a Temporal-vs-Camunda spike: engineering ergonomics vs legibility for process owners.
7. **Control plane.** Per service, give owner, build/buy and the trigger to have it by:
   - agent registry;
   - policy repository;
   - evidence ledger (shared, three classes);
   - audit hash chain (shared);
   - eval + shadow environment (golden runs in CI, pass^k);
   - model gateway;
   - agent identity (IdP-issued, OBO);
   - ingest screening (shared module);
   - observability: OTel GenAI spans `invoke_agent`, `execute_tool`, with the version pinned (still Development stability);
   - a sandbox for code-executing agents (a gap in most designs).

   No vendor sells this plane whole. Say so.
8. **Repo and registry shape.** Agent-as-folder monorepo: one folder = one package = one deployable. `agent.yaml` is the registry entry (lane, level, owner, tool allowlist, write scopes `[]` by default, budget, eval suite). Evals are a required check; add CODEOWNERS per agent and per policy folder, release automation per package, and shared mechanism as an internal library. The registry and allowlist then change only through a reviewed PR diff. Worked example, with the registry keys in each agent file, the CI check, and per-agent caps set from the run ledger by formula: [worked-example-registry.md](references/worked-example-registry.md).
9. **Sequence by trigger and place regulation.**
   - Before agent two: gateway, registry, identity, named policy owners.
   - Before agent three: shared ledger, audit chain, screening, CI evals.
   - Before the first research agent: firewall code, source tiers, budget reporting, shadow.
   - When an agent must be reachable from outside: an A2A adapter.

   Place each agent against the EU AI Act snapshot in the landscape reference: Art. 50 transparency applies now; the high-risk dates moved under the Omnibus; check the scope of the Machinery-Regulation carve-out. Re-verify the legal text before advising. Treat sovereignty as a model-hosting and identity choice behind model-agnostic protocols, not as a rewrite.
10. **Verifier pass (separate step).** Check the deliverable against the done-when list, the red flags below and the question set in [decision-questions.md](references/decision-questions.md). Mark each PASS/FAIL in RESPONSE.md, fix, and allow at most 2 revision attempts. Report anything still open.

## Red flags (review checklist)
- "Orchestration layer" is one box naming a framework, a code host and a language.
- Every agent has the same shape, or research agents can feed gates directly.
- Sub-agents write to the same artifact, or talk peer-to-peer without a packet.
- A2A or another RPC is used as the internal bus inside one estate on one runtime.
- Each repo holds its own model API key: no gateway, no cost attribution, no model swap.
- A shared service account for "the agents"; write access granted "but the prompt says don't".
- No registry, so agent twelve will be discovered through an incident.
- A workflow engine bought "for agent four" with zero of the four triggers firing — or twenty agents and a compensation requirement with no engine.
- OTel GenAI conventions treated as stable, or MCP features relied on that the 2026-07-28 spec deprecates (sampling, roots, logging, HTTP+SSE).
- Framework facts in the deliverable older than a month and not re-verified.

## Optimizations/Gotchas
- **Two client-ready references.** [harness-scaling.md](references/harness-scaling.md) answers "it works for me, what does a team or company need?": the single-user couplings, the team layer (plugin + seats + permissioned shared knowledge), the company control plane, works-council co-determination, and "harness as a service" as hosted runtime vs product. [enterprise-orchestration-primer.md](references/enterprise-orchestration-primer.md) is the concept set a client team needs before deciding: the orchestrator's steps and five rules, the scaling evidence, the 13-item Plug-in Standard and task packet, trust levels L0–L2, the governance pyramid made executable, and the control plane by agent count. Fill in client specifics in the deliverable, never in the reference.
- **Answer a framework debate by asking, not arguing.** Concede what the other side got right, isolate the question they didn't answer (where does state persist when the pod dies? where is the human gate? who pays for which model call? what identity does the agent run as? how would you notice a regression? what happens to outside free text before the prompt?), and hand over the checklist. Full set in [decision-questions.md](references/decision-questions.md).
- **The long pole is rarely technical.** Real policy weights from domain owners take weeks of the right people's time; the platform pieces take days. Put it on the plan.
- **These services get much more expensive once production agents predate them.** That is the honest pitch for building the control plane early.
- **Industrial pattern (2025–26):** vendors are converging on an orchestrator plus specialist agents, MCP as the shop-floor data adapter and local/edge inference (see the landscape reference). Design so OT-side MCP servers plug into the same gateway and identity model.
- **Verifiers help only when aligned with the real acceptance criterion.** Misaligned verifiers showed negative gains in NLAH. Check against the gate the business actually applies, not against an LLM-judge vibe.
- **Confidentiality:** client agent lists, system names and internal politics stay in `output/` and the vault, never in this skill.
