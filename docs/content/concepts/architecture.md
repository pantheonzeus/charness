# Architecture

charness is a **Natural-Language Agent Harness** ([Pan et al., arXiv:2603.25723](https://arxiv.org/abs/2603.25723)). Harness policy is written as editable documents in plain language, and a runtime interprets them. Here the runtime is Claude Code plus the deterministic hooks around it.

The design rule is **policy separated from mechanism**. Documents say what should happen. Code makes sure the parts that must hold do hold.

## Four layers, one job each

| Layer | Files | Job | Changes |
|---|---|---|---|
| **Skill library** | `resources/skills/**/SKILL.md` + [`INDEX.md`](../reference/skills.md) | Task logic: one policy document per task type | often |
| **Identity** | [`Soul.md`](../reference/soul.md) + `IDENTITY.md` | Voice mechanics and inviolable lines; the persona | when you change |
| **Runtime Charter** | [`Charter.md`](../reference/charter.md) | Universal physics for every run: discipline, dispatch, state, delegation, the knowledge graph, self-learning | rarely |
| **Backend** | `.claude/` hooks, `scripts/`, per-skill `scripts/` | Mechanism: guards, injection, runners, ledgers | rarely |

`CLAUDE.md` is the entry point: Claude Code loads it automatically, and it imports the Charter and Soul.

## How the paper maps onto the repo

| NLAH concept | Realization here |
|---|---|
| Run-level harness policy | [Charter.md](../reference/charter.md) |
| Agent identity and voice | [Soul.md](../reference/soul.md) + `IDENTITY.md` |
| Task-specific harness documents | `resources/skills/**/SKILL.md` |
| Reusable, ablatable modules | [`MODULES.md`](gh:resources/skills/MODULES.md) (vocabulary) + [`_shared/`](gh:resources/skills/_shared/) (evidence gate, handoff, self-evolution, verifier separation, change manifest) |
| Intelligent Harness Runtime | Claude Code + `.claude/` hooks + the skill-dispatch protocol |
| File-backed run state | `output/.runs/<slug>/`: control spine + evidence, kept apart from deliverables |
| Parent → child handoff | File-backed task packets (`TASK.md` → `RESPONSE.md`), reopened by the parent |
| Validation gates | Write, egress and send gates, the control-spine stop gate, the link-audit graph gate, the evidence gate |

## Why documents and code both

A rule written only in a prompt holds until the model decides otherwise. A rule written only in code can't explain itself, and can't handle the cases nobody anticipated. charness uses each where it is strong:

- **Documents** carry judgment: how to research, when to ask, what a good brief contains, which skill fits.
- **Code** carries what must never depend on judgment: where a job may write, what may leave the machine, what needs your yes, when a run may stop.

Most guards **fail open**: a parse error lets the action through, so a hook bug never blocks real work. The send gate **fails closed**, because a sent message can't be recalled. [Guardrails →](../governance/guardrails.md)

## What's in the repo and what isn't

The repo holds the operating system, not the data:

| Tracked (public) | Git-ignored (yours) |
|---|---|
| Charter, Soul, `IDENTITY.example.md` | `IDENTITY.md` |
| Skills, hooks, scripts, the console | `cbrain/`, the Obsidian vault |
| `employers/README.md` + `_template/` | `employers/<slug>/`, `employers/ACTIVE` |
| Reference launchd plists | `output/` (deliverables, run state, ledgers), `input/` |
