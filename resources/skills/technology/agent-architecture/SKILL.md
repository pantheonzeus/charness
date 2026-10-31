---
id: agent-architecture
aliases: [agent-architecture]
name: "Agent Architecture — Need-Gate, Determinism Boundary & Conformance Level"
category: technology
description: Architect one AI agent at principal level. Start with the use-case and need-gate (plain code → single call → workflow → agent, each rung justified by an eval). Draw the determinism boundary (the model answers narrow language questions; code scores, ranks and gates; the business owns policy as files), then design the harness — on-disk control spine, context degraded by reference, evidence ledger, ingest screening, identity, budget and human gate. Prove it with golden runs, pass^k and a model-swap test, and assign a conformance level (L0/L1/L2) against seven framework-independent invariants. Framework follows the client's stack, not its feature list.
triggers: [agent architecture, architect an agent, design an AI agent, build an agent, agent design review, do we need an agent, agent or workflow, which agent framework, LangGraph or, Agent SDK, agent harness, harness engineering, context engineering, agent tools design, MCP server design, agent state, agent memory, human in the loop gate, agent guardrails, prompt injection defense, agent identity, agent golden runs, model swap, deterministic agent, agent conformance, agent prototype to production]
tags: [technology, architecture, ai-agents, harness, governance, evals]
related: ["[[multi-agent-platform]]", "[[agentic-service-blueprint]]", "[[agentic-service-evaluation]]", "[[agent-ready-service]]", "[[ai-opportunity-portfolio]]", "[[cloud-architecture]]", "[[decision-memo]]"]
modules: [file-backed-state, evidence-backed-answering, verifier-separation]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
requires:
  tools: [web_search, web_fetch]
  optional: [python3 (for the reference firewall in multi-agent-platform/scripts), the client's agent framework for the swap test]
environment: "Runs anywhere. Framework, protocol and regulatory facts live in ../multi-agent-platform/references/landscape-2026-10.md as a dated snapshot — re-verify before any client-facing claim; this layer moves monthly."
references: [references/harness-patterns.md, ../multi-agent-platform/references/landscape-2026-10.md, ../multi-agent-platform/references/decision-questions.md]
---

# Agent Architecture — Need-Gate, Determinism Boundary & Conformance Level

> The model is about 10% of an agent. The harness around it is the other 90%, and the harness is the only part the client owns. Architect that.

## Contract
- **Input:** one of three modes. **Design** means a use case to build an agent for. **Review** means an existing agent (repo, prompt, diagram, framework config) to red-team. **Harden** means a prototype to bring to production. Also collect whatever exists: the users, the systems of record it reads or writes, the decision its output feeds, the regulation, the team and the cloud/identity stack.
- **Output:** `output/<YYYYMMDD>-<slug>-agent-architecture.md` containing:
  - (a) the use-case card and need-gate verdict;
  - (b) the layer map (policy / domain / mechanism / connectors / model) with owners and rate of change;
  - (c) the determinism boundary table (each step: model or code, and why);
  - (d) the harness spec (state, context, evidence, tools and identity, ingest, governance, budget);
  - (e) the eval plan (golden runs, pass^k, model-swap test, shadow);
  - (f) the invariant checklist with the target conformance level;
  - (g) a framework-fit ADR with ≥1 rejected alternative.

  Review mode adds a findings table (invariant · evidence · severity · fix · effort). Index the output into `cbrain/notes/Deliverables/` per Charter §4.
- **Allowed tools/artifacts:** conversation, the client's code/configs (read-only), web search for current framework and protocol facts, running the agent in a sandbox for the swap test. Never point a test at production systems of record.
- **Done when:**
  - the need-gate names the lowest rung that works and the eval evidence for climbing past it;
  - every step in the boundary table is assigned to model or code with a reason;
  - every one of the seven invariants is marked met / gap / n.a. with evidence;
  - the conformance level is stated and its promotion approver named;
  - the swap test has **run** — or is listed as the first open item, never claimed as passed;
  - the verifier pass (step 9) records PASS.

## Triggers/Context
- Any ask to design, review, harden or choose a framework for a single agent, or "do we even need an agent here?".
- **Hand-offs:**
  - More than one agent, a shared platform, orchestration across agents or an agent registry → `multi-agent-platform`. This skill architects one agent; that one architects the estate the agent lives in.
  - Who does what between humans and agents in a service, autonomy per task, staff impact → `agentic-service-blueprint`.
  - Service-level eval suite, staged rollout and operating scorecard → `agentic-service-evaluation`.
  - Where in the business agents pay off at all → `ai-opportunity-portfolio`.
  - Hosting, sovereignty, cost of the infrastructure under the agent → `cloud-architecture`.

## Operating principles (enforceable)
1. **Adoption before architecture.** No harness is designed until the use-case card exists: who uses it on Monday, what they stop doing, what signal at 30 days proves value (repeat use, acceptance rate, override reasons, time saved), and the kill criterion. An unused agent is a cost center with good test coverage.
2. **Climb the ladder, one justified rung at a time:** plain code → single model call (+ retrieval) → workflow (chaining / routing / parallel / evaluator-optimizer in fixed code paths) → one agent with tools. Each rung up needs an eval result showing the lower one failing, not taste. A fixed rule with no text understanding is plain code, every time. Agents cost roughly 4× the tokens of a chat (see the landscape reference), so price the climb.
3. **The determinism boundary is the architecture.** The model answers narrow language questions (extract, classify, summarize, draft, choose among listed options). Scoring, ranking, gating, arithmetic and anything that must be defended externally are deterministic code. A ranking a model produced cannot be defended to an auditor; one computed by code from cited inputs can.
4. **Policy is files the business owns.** Weights, thresholds, hard gates, escalation rules and scope live in versioned Markdown or YAML that a domain owner edits. Code parses them; the model receives them verbatim as a byte-stable, cacheable prefix. A rule change is a diff the business wrote, with no deployment and no ticket.
5. **Separate by rate of change.** Policy changes weekly (business-owned), domain logic monthly, mechanism almost never, connectors when a system of record is replaced. The model is a fifth, swappable part. Put a seam wherever rates differ; fuse nothing that changes at different speeds.
6. **A step may not return a value that matters — it writes one.** State lives on disk (a control spine of checkpoints plus artifacts), and each step rebuilds its state from disk. Resume is just "run" against a spine with boxes already ticked, so the two paths cannot drift.
7. **Context is degraded by reference, never summarized away.** Over budget, an artifact drops to digest + path + hash, then to a bare pointer. Pinned items (acceptance criteria, policy, open escalations) are never dropped. Write each step's context window to disk so a bad answer is debuggable.
8. **Untrusted input is data, by construction.** Every ingested text (web page, email, PDF, counterparty free text, tool output) is labelled as data before it reaches a prompt. Findings route to the data owner. A screening hit must move the output in **neither** direction; assert that with a poisoned-input test. Treat screening as a boundary plus a label, not as detection — regexes will miss things.
9. **Identity is least privilege at the tool plane.** The agent has its own identity, and read and write are separate identities. Scopes are declared up front and enforced at the tool/MCP server, never requested by the model at runtime. "It could write, but the prompt tells it not to" is one prompt away from writing.
10. **Stop rather than invent.** Distinguish hard stops (halt the run, write `DECISION_REQUIRED.md`, exit) from soft escalations (continue and flag on the deliverable). The rule: when the agent would otherwise have to invent something to continue, it stops and asks. Auto-approve flags are logged as themselves.

## Core Blueprint
Substantive runs keep a STATE_ROOT at `output/.runs/<YYYYMMDD>-<slug>-agent/` with `RESPONSE.md` (steps 1–9 as boxes) and `EVIDENCE.md` (every framework/protocol/regulatory fact with source and date).

1. **Frame mode and outcome.** Design / Review / Harden. Write the use-case card from principle 1. If nobody can name the user, the decision the output feeds, or the kill criterion, stop and ask. Placing that decision is the job of `ai-opportunity-portfolio`, not this skill.
2. **Run the need-gate.** Walk the ladder from principle 2 and record the verdict with evidence. Common correct answers are "plain code with one model call for extraction" and "a fixed workflow with one agentic node". Name the agentic step precisely: the one step whose tool sequence cannot be known in advance. Everything else stays deterministic.
3. **Map the layers.** A table of policy / domain / mechanism / connectors / model, with an owner, a rate of change and a file location for each. Flag any fused layers, such as weights hard-coded in prompts or scoring inside the model call.
4. **Draw the determinism boundary.** List every step. For each: model or code, the narrow question the model answers (if model), the deterministic check on its output, and what happens if the model is wrong. The number of distinct model questions should be small. A pipeline that asks the model to "decide" is a review finding.
5. **Specify the harness** using [harness-patterns.md](references/harness-patterns.md):
   - **State:** control spine + artifact store, and where durable state persists when the process dies (name the checkpointer and its backing store; in-memory is a prototype).
   - **Context:** byte-stable prefix (policy + instructions), pinned set, degradation ladder, per-step context dumps.
   - **Evidence:** claim classes `observation` (named system + extract date) / `inference` (from listed observation ids) / `external` (URL + retrieval date + source tier, never gate-eligible), with a release gate on uncited claims.
   - **Tools and identity:** tool allowlist with read/write split, poka-yoke parameters, MCP servers per system of record with attribution stamped at the server, the identity mode (on-behalf-of the user vs service identity).
   - **Ingest:** screening boundary and labelling; the routing of findings.
   - **Governance:** hash-chained audit log of every tool call, model call, escalation and decision; budget guard (tool calls, model calls, wall-clock, tokens) that stops and reports; hard-stop vs soft-escalation table; human gate as a file.
6. **Choose the framework last.** Write an ADR. Every major SDK now ships the same primitives (deterministic nodes, an LLM agent node, a checkpointer, an interrupt for humans, handoff or agent-as-tool), so pick by the client's cloud, identity and skills stack, not by feature list. Record what the framework covers (run loop, checkpointing, interrupt/resume) and what it does **not** — the invariants are code the client writes in any framework. Verify current framework facts against the landscape reference and re-check them live.
7. **Design the evals.**
   - **Golden runs:** fixed inputs with expected structured outputs, in CI.
   - **pass^k:** measure consistency across k trials, not pass@1.
   - **Poisoned-input test:** principle 8.
   - **Crash-resume test:** kill mid-run, resume, same answer.
   - **Model-swap test:** run with the production model and with a second model or a rule-based stub. If the runs are not structurally identical, the model choice *is* the architecture; fix the boundary before claiming it.
   - Shadow mode on live traffic before any autonomy. Service-level rollout gates go to `agentic-service-evaluation`.
8. **Score the invariants and set the level.** Mark each of the seven invariants (in [harness-patterns.md §Invariants](references/harness-patterns.md)) as met / gap / n.a. with evidence. Assign the conformance level:
   - **L0 — sandbox:** no output reaches a decision.
   - **L1 — advisory:** read and cited by humans, never fires a gate.
   - **L2 — decision-supporting:** golden runs pass plus a named human gate.

   Name who approves promotion. Review mode: list the gaps ranked by blast radius.
9. **Verifier pass (separate step).** Re-read the deliverable against the Contract's done-when list and the red-flag list below. Record each item PASS/FAIL in RESPONSE.md. On FAIL, fix and re-run, capped at 2 revision attempts; report anything still open rather than hiding it.

## Red flags (review checklist)
- The model produces a score, ranking or go/no-go that a human then defends.
- Weights or rules live inside a prompt string or in code that only engineers can change.
- "Memory" is the transcript, and there is no on-disk state or resume path.
- The checkpointer is in-memory, or nobody can say where state lives when the pod dies.
- One identity can both read and write, or a shared team service account is used.
- The agent asks the human for approval inside the chat instead of through a gate that halts the run and leaves a record.
- Free text from outside reaches the prompt unlabelled.
- No budget, or a budget that silently truncates.
- Evals are pass@1 on a handful of demo inputs, or there are no evals at all.
- The framework was chosen before the use-case card existed.

## Optimizations/Gotchas
- **"Which framework?" is usually the wrong first question.** Answer it with a runnable reference agent plus the invariant checklist, not a vendor comparison. Building the same agent framework-free and as a framework port shows exactly which ~200 lines of guardrails no framework gives you.
- **The swap test is the claim most often made and least often run.** Never write "model-agnostic" in a deliverable without its result.
- **Budget overrun is a symptom.** Before raising a budget, check whether the agent is looping.
- **Lead with the decisions, not the folders.** Reviews of this kind drift into many artifacts for few decisions. The deliverable opens with the 3–5 decisions the client must take.
- **Vendor and protocol facts go stale in weeks.** Keep them in the dated reference, never in the method.
- **Confidentiality:** client agent designs, policy weights and system names stay in `output/` and the vault, never in this skill or its references.
