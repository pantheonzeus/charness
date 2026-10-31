# Decision Questions — placement, triggers and the counter question set

Client-agnostic. Distilled from a 2026 industrial agent-estate engagement and checked against the 2026 public guidance in [landscape-2026-10.md](landscape-2026-10.md).

## Placement — five questions, in order; stop at the first that decides

1. **Can the output exclude a counterparty, commit money, or need to be defended externally?** → **Lane A, L2.** Fixed order, human gate, reproducible, no cross-run memory. Ask nothing further.
2. **Is there exactly one step whose tool sequence cannot be known in advance?** → **Lane A with one Lane-B node.** That node loops under a tool budget, its output is re-verified downstream, and the agent otherwise stays deterministic.
3. **Is the work open-ended, long-horizon, and read-only against sources the client doesn't own?** → **Lane C, L1.** Orchestrator-worker, declared research budget, source tiers, firewall on the way out.
4. **Must it be reachable by an agent outside this estate?** → Put an A2A Agent Card over the existing packet. The lane doesn't change.
5. **Does it take part in a transaction with two or more other agents, with state that outlives them all?** → Re-check the workflow-engine triggers before building.

Then **register it before writing code**: lane, level, owner, policy path, identity and mode, data scopes, budget, eval suite.

## Lanes at a glance

| | A — Gated process | B — Bounded loop | C — Research |
|---|---|---|---|
| Who decides "next" | the process, at design time | the model, inside one node, under a tool budget | the model, continuously, under a research budget |
| Reproducible | required | bounded; output re-verified | no, and never claimed |
| Human gate | named in policy, halts the run | inherited from the enclosing graph | review happens on the artifact |
| Evidence | traceable to a system of record | same | URL + retrieval date + source tier |
| May fire a hard gate | yes | yes, on re-verified claims only | **never** |
| Cross-run memory | defect | defect | feature |
| Failure to fear | silent rubric drift | burning budget without converging | confident synthesis from a content farm |

## Workflow-engine trigger (adopt Temporal/Camunda-class when ANY TWO hold)
- More than two agents share one business transaction whose state outlives all of them.
- A handoff must survive a multi-day human wait, with an SLA and an escalation path.
- A failed downstream step must **compensate** an upstream side effect.
- Process owners outside engineering must read and change the sequence.

One agent with a durable checkpointer needs none of this. Twenty agents with file handoffs and no engine last longer than instinct suggests, then fail suddenly when the compensation condition hits.

## Counter question set — for an orchestration-layer or framework proposal

**Opening move.** Concede what they got right, then separate out what they didn't answer: *"That box answers how you write agents — which slide answers what runs them?"* Ask, don't argue. The framework is the cheap, reversible decision; the control plane is the expensive one.

| # | Question | Good answer | Weak answer |
|---|---|---|---|
| 1 | When the process restarts halfway through a run, what happens? Which checkpointer, and where does that state persist? | a named durable store | "we'd re-run it" / in-memory |
| 2 | Where does the human gate live? | one stop primitive, the same in every agent, pause state persisted | "the agent asks the user in the chat" |
| 3 | Which component decides which model a call goes to, and who is charged for it? | a named gateway, mandatory from agent one | an API key in each repo's environment |
| 4 | What identity does the agent run as? | per-agent identity, scopes in a registry and enforced at the tool plane, read ≠ write | "it can write, but the prompt tells it not to" |
| 5 | How would you find out you had shipped a regression? | golden runs in CI per agent + shadow mode | "we test manually before release" |
| 6 | What happens to outside free text before it reaches the prompt? | screened and labelled at the tool plane; findings go to the data owner; score-neutral | silence (the usual answer) |

**Closing question, if you only get one:** *"Which conformance level is this agent at — and which layer owns durable state when the process runs for three days?"* "L0 sandbox" is a fine answer. "Decision-supporting, and the framework owns the state" doesn't survive the room. Let them hear it themselves.

**Don't make it a framework argument.** Graphs, agents and deep agents compose (a graph can be a sub-agent; an agent can be a graph node), so moving between them is a refactor, not a migration.

## Single vs multi-agent — quick test
- Is the work **read-heavy and breadth-first** (research, scanning, retrieval across independent branches)? → orchestrator-worker can pay off.
- Is it **write-heavy or tightly coupled** (one document, one codebase, one decision)? → a single agent, or one writer plus read-only helpers.
- Does the value per run cover **~15× chat tokens**? If not, stop.
- Is there an eval showing the single agent failing? If not, you haven't earned the split.

## Adoption questions (ask before any architecture)
- Who uses it on Monday, and what do they stop doing?
- What signal at 30 days proves value? (Repeat use, acceptance rate, override reasons, time saved, pull from adjacent teams.)
- What makes us kill it?
- Which steps are green / amber / red for autonomy in the user's own view? (This sets the human-in-the-loop points.)
