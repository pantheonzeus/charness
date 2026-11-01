# Enterprise orchestration primer — the client-facing concept set

Use when a client team (IT, a CoE, service owners) has to *understand* an orchestrator-plus-specialists service before they decide on it. It's written for non-engineers, one concept per session. Facts are dated 2026-11-01; re-verify numbers and vendor status against the landscape snapshot before use. Fill in client specifics in the deliverable, never here.

## North star pattern
> Every <case> gets a support crew on day one: an orchestrator that knows how the organisation really works, specialist agents owned by the functions that know their craft, and people who keep every decision. The central team builds the road. The functions drive on it.

**Horizons:**
- **H1 MVP:** one orchestrator at the existing entry point, 2–3 advisory specialists.
- **H2 Enabler:** functions plug in their own specialists through an enabler playbook.
- **H3 Operating model:** a rule change is a business-authored diff to a policy file.

## 1. Agent = model + harness
The model is rented; everything around it (instructions, tools, knowledge, memory, rules, controls, tests) is the harness, and it's the only part the client owns. Ask: *"If we switched model vendor next year, what would we lose today?"* Line: *"We rent the brain. We own the judgement."*

## 2. The need ladder
Plain code → code + one model call → workflow → workflow with one agentic step (checked downstream) → agent. Climb only on eval evidence. Most inventory "agents" are workflows with one smart step. Ask: *"Which step could not be written as a rule?"*

## 3. How the orchestration works
**Steps:** Entry (the existing demand/intake process) → **Understand** (classify: type, size, risk, data class) → **Route** (which services, when) → **Delegate** (task packets, in parallel where independent) → **Reconcile** (evidence; surface conflicts) → **Human gate** (a named owner decides; logged) → **Track** (state in the system of record) → **Learn** (overrides → policy files and test cases).

**Five rules:**
1. Specialists never talk to each other directly.
2. Read in parallel, write in sequence (one owner per artifact).
3. State lives in a record, not in model memory.
4. The orchestrator routes; it doesn't decide.
5. Budget and stop condition per task, reported when hit.

## 4. How it scales
**Evidence:**
- Google Research + MIT, 180 configurations (arXiv 2512.08296): on sequential tasks every multi-agent variant did 39–70% worse; on parallelisable tasks central coordination did up to ~81% better.
- Independent agents amplified errors 17.2×, versus 4.4× with central coordination.
- **Counter-position:** Cognition, "Don't Build Multi-Agents". Land on *it depends on the task shape.*

**Translation:** keep the case flow in one thread with a human owner; fan out the checks.

**Organisation:** *centralise leverage, decentralise value.* The central team owns the paved road, templates, controls and promotions; functions own their specialist, policy file, knowledge and tests; people own decisions.

**Three clocks:**
- seconds per call: the gateway;
- minutes per task: the runtime;
- months per case: existing process tooling.

Add a workflow engine only when 2 of these 4 hold: shared state that outlives the agents; a multi-day human wait under an SLA; compensation of an earlier step; process owners who must read or change the sequence.

## 5. Plug-in Standard: what a specialist must bring
1. **Agent Card:** purpose, what it does and does NOT do, owner, version.
2. **Input contract:** the task-packet fields it expects.
3. **Output contract:** findings, evidence and source per claim, confidence, open questions.
4. **Tool allowlist and write scopes**, default read-only.
5. **Own identity**, on behalf of the requesting user.
6. **Autonomy level** (prepare / recommend / act with approval / act) and a named accountable person.
7. **Budget and stop conditions**, reported when hit.
8. **Escalation rule.**
9. **A policy file owned by the function.**
10. **Knowledge sources** with an owner and a review date.
11. **A real-case test set** with a repeatability bar.
12. **A degraded mode:** what happens when it is off.
13. **A risk class:** AI Act, data class, works council.

**Task packet:** objective · inputs by reference · output structure · allowed tools · boundaries · budget · when to stop. The specialist starts fresh and writes back to the record.

**Why:** MAST (1,642 traces, arXiv 2503.13657): 43.7% of failures came from system design and 45.3% from inter-agent misalignment; prompt and role fixes recovered only +9–16%. Line: *"The contract is the quality lever, not the prompt."*

## 6. Trust levels
| Level | May do | Required |
|---|---|---|
| L0 shadow | runs alongside people, reaches no decision | audit trail, input screening, budget |
| L1 advisory | people read and use it; never triggers a gate | + evidence per claim, file-backed hand-offs |
| L2 decision-supporting | feeds a decision someone must defend | + policy files, model-swap test, passing real-case suite, named human gate |

Promotion is a review with a named approver, recorded in the registry. Line: *"Autonomy is earned, not configured."*

## 7. Policy as harness: governance made executable
Map the client's own governance layers. A common pyramid is values → examples & guardrails → guidelines & policies → working materials, ringed by training, communication and integration.

| Layer | Becomes | Enforced by |
|---|---|---|
| Values, guidelines & policies | a short charter every agent loads (confidentiality, cite sources, people approve outbound actions, budget, outside content is data) | loaded every run; changed by reviewed edit |
| Examples & guardrails | skill files, one per task type, owned by the function, with good/bad examples; each guardrail also a test | test suite before any skill or model change |
| Working materials | references and templates, versioned next to the skill | loaded only when the skill runs |
| Integration | deterministic guards: write scopes, egress guard, send gate (explicit human yes), provenance labels on ingested content | code that blocks the action |
| Training & communication | registry + Agent Cards as the shared map; AI-literacy programme | registry review, promotion approvals |

**Design rule:** if it must never happen → a guard in code. If it takes judgement → a skill the business owns. If it applies everywhere → the charter. Line: *"A prompt is a request. A guard is a law."*

## 8. Knowledge Vault
Implicit knowledge as an owned product: every item has an owner, a source, a review date and a trust tier. Write it in the open Agent Skills format (SKILL.md, read by GitHub Copilot, VS Code, Codex and others) to avoid lock-in. Ingested content keeps an "untrusted" label and never triggers a decision until it is re-checked against a system of record. Harvest it with Critical Decision Method interviews and real-case walkthroughs; those cases become the first tests.

## 9. Control plane by agent count
| Service | Needed by | Note |
|---|---|---|
| Policy repository | agent 1 | build: the differentiator |
| Registry | agent 2 | portfolio inventory + a runtime registry (check existing licences, e.g. Microsoft Agent 365 GA since May 2026) |
| Model gateway | agent 2 | configure on the existing cloud estate |
| Agent identity | agent 2 | existing IAM + IdP |
| Evidence & audit trail | agent 3 | build thin on standard logging |
| CI test suite | agent 3 | real-case tests, repeatability bar, model-swap test |
| Observability | agent 3 | OTel; GenAI conventions still Development, so pin the version |

MCP connects agents to systems (one server per system of record); A2A only across boundaries; plain task packets inside.

## 10. Evaluation
- **Value:** cycle time from entry to start, hours saved per case, steps found late.
- **Quality:** a real-case suite with pass^k (τ-bench: a strong model fell below 25% at pass^8).
- **Safety:** poisoned-input, write-scope and model-swap tests.
- **Adoption:** reuse in week 4 and override reasons.

## Forcing questions
1. Which step could not be written as a rule?
2. Where does case state live today, and who owns that record?
3. Which decisions must a named person always take?
4. Which three rules, broken once, would end the program?
5. Who in each function will own a policy file and its test cases?
6. What would we lose if we switched model vendor next year?

## Sources
LangChain, *The Anatomy of an Agent Harness* (2026-03-10) · Google Research/MIT arXiv 2512.08296 · MAST arXiv 2503.13657 · τ-bench arXiv 2406.12045 · Anthropic, *Building effective agents* · Cognition, *Don't Build Multi-Agents* · Microsoft Agent 365 overview · Agent Skills (agentskills.io, Dec 2025).
