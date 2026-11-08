# Harness Patterns — the parts no framework ships

Distilled from a 2026 industrial agent engagement: a framework-free reference agent with eight gates, ported 1:1 to a graph framework. These are client-agnostic patterns. Research basis: NLAH (arXiv 2603.25723), where file-backed state and evidence-backed answering were the modules that reliably helped, and MAST (arXiv 2503.13657), where most failures came from system design and coordination rather than model capability. Sources are in [landscape-2026-10.md](../../multi-agent-platform/references/landscape-2026-10.md).

## The layer map

| Layer | Contents | Owner | Changes | Lives in |
|---|---|---|---|---|
| Policy | weights, thresholds, hard gates, escalation, scope | domain/business owner | weekly | `policy/*.md` (versioned, reviewed) |
| Domain | the steps, the rubric arithmetic, output schema | agent team | monthly | `agent/` |
| Mechanism | spine, state, context, evidence, governance | platform | almost never | shared library |
| Connectors | system-of-record adapters, MCP servers | integration | when a system is replaced | `connectors/` / MCP servers |
| Model | planner / language component | platform (via gateway) | swappable at will | gateway config |

## Pattern catalog

| Pattern | Rule | Test it holds |
|---|---|---|
| **Control spine on disk** | Gates are checkboxes in `SPINE.md` (+ machine-readable twin). Resume = run against a spine with ticks. | Kill mid-run, resume, same output |
| **Steps write, don't return** | Every step persists its result, and the next step reopens it by path. No load-bearing value only in memory or in the transcript. | Delete the in-memory state between steps; the run still completes |
| **Context by reference** | Byte-stable prefix (policy + instructions), pinned set, then degrade: full → digest + path + sha → pointer. Dump each step's context to disk. | Prompt-cache hit rate stays high; any answer is traceable to its context dump |
| **Evidence ledger** | Append-only JSONL. `observation` (system, extract date, tool call id) · `inference` (from observation ids) · `external` (URL, retrieval date, source tier). Release gate blocks uncited release-critical claims. | A number without lineage cannot be written |
| **Determinism boundary** | Model = narrow language questions (few per run). Code = score, rank, gate, arithmetic. | Model-swap test: production model vs second model or rule stub → structurally identical runs |
| **Ingest screening** | Untrusted text is labelled as data before any prompt sees it; findings go to the data owner; screening is score-neutral. | Poison all counterparty free text → ranking unchanged |
| **Governance kit** | Hash-chained audit log (each entry hashes its predecessor); budget guard that stops and reports; human gate writes `DECISION_REQUIRED.md` and exits; auto-approve logged verbatim. | Edit one audit line → chain verification fails (self-test does exactly this) |
| **Hard stop vs soft escalation** | Hard stops halt the run (missing mandatory input, gate conflict, would-have-to-invent). Soft escalations continue but are flagged on the deliverable. | Every escalation type is classified in `policy/escalation.md` |
| **Identity split** | Own identity per agent; read and write are separate identities; scopes enforced at the tool/MCP server; delegated (on-behalf-of) vs service mode chosen per lane. | The read identity physically lacks the write grant |
| **Framework-free core vs port** | Build the reference once without a framework (what a harness must do), then port it (what the framework covers: loop, checkpointer, interrupt/resume). The difference is your guardrail code. | Both versions produce the same output on the golden runs |

## Invariants

An implementation conforms if it satisfies these, whatever it imports. No mainstream framework ships them; they are code the client writes.

| # | Invariant | Test |
|---|---|---|
| 1 | **Policy as files the business owns**, given to the model verbatim as a stable prefix | A rule change is a business-authored diff, deployed without a code change |
| 2 | **Evidence ledger with three claim classes**; `external` never gate-eligible | `gate_eligible(external)` is False; uncited claims block release |
| 3 | **Audit hash chain** over every tool call, model call, escalation and decision | Tampering with one line fails verification |
| 4 | **Determinism boundary**; reasoning core swappable | Model-swap test passes |
| 5 | **Ingest screening**, score-neutral | Poisoned-input test passes |
| 6 | **File-backed handoff, fresh start** — the file is the carrier of record, never the inline reply | Crash-resume test passes |
| 7 | **Declared budget, reported on exhaustion** | A budget-hit run reports what it did not reach |

### Conformance levels (a registry field; promotion is a review with a named approver)

| Level | Requires | Typical use |
|---|---|---|
| **L0 — Sandbox** | 3, 5, 7 | Prototypes, shadow mode. No output reaches a business decision |
| **L1 — Advisory** | L0 + 2, 6 | Research agents. Humans read and cite; output never fires a gate |
| **L2 — Decision-supporting** | L1 + 1, 4 + passing golden-run suite + named human gate | Anything whose output someone must defend externally, or that commits money or excludes a counterparty |

Levels stop the most common estate failure: a prototype drifting into a real decision process without anyone deciding that it should.

## Need-gate table ("do I need an agent?")

| If the step… | Use |
|---|---|
| applies a fixed rule to structured data | plain code |
| needs text understanding but its path is fixed | code + one model call (extract/classify) |
| has several fixed steps, some needing language | workflow (chain / route / parallel / evaluator-optimizer) |
| has one step whose tool sequence cannot be known in advance | workflow with **one** agentic node under a tool budget, its output re-verified downstream |
| is open-ended, long-horizon and read-mostly | an agent (consider a research lane — see `multi-agent-platform`) |

## Known gaps to close in any real build
These were designed in the source engagement but not built. Do not repeat that.
- The model-swap test was specified but never executed, so the boundary was asserted rather than shown.
- The durable checkpointer was named (a Postgres-class store) but the template ran in memory.
- The `external` class and `gate_eligible` were design-only. A reference implementation now ships in `multi-agent-platform/scripts/research_firewall.py`.
- There was no sandbox boundary for code execution by research agents. Ingest screening covers prompts, not execution.
- There was no cost model per run and no handling of disagreement between models.
