# Skills

A skill is one Markdown file, `SKILL.md`, holding the policy for one type of task: what it takes in, what it delivers and where, which tools it may use, and when it is done. The library has {{ skills_count }} skills in {{ categories_count }} categories on this site. [Browse the catalog →](../reference/skills.md)

## Progressive disclosure

The agent never loads the whole library. It reads in three tiers:

1. **The index.** [`INDEX.md`](gh:resources/skills/INDEX.md) has one row per skill (name, triggers, description, path). It is scanned before every task, including small ones, and before the agent says anything can't be done.
2. **The skill.** Only the matched `SKILL.md` is opened.
3. **Deep material.** `references/`, `workflows/`, `scripts/` and `schema/` inside the skill's folder are loaded only when the task needs them.

The [UserPromptSubmit preselector](session.md#2-userpromptsubmit-skill-preselection) narrows tier 1 to a few rows for each prompt.

## Anatomy of a SKILL.md

```yaml
---
id: deep-research
name: "Deep Research — Background Task with Plan Check-in"
category: research
description: One line, used for index matching.
triggers: [research this, deep research, look into, dig into, investigate, …]
status: active            # active | draft | deprecated
version: 4
modules: [file-backed-state, file-backed-handoff, evidence-backed-answering]   # from MODULES.md
---
```

Optional keys add `requires:` (tools, CLIs, other skills), `environment:`, and `vault_writes:`, the vault paths the skill may write. A skill without `vault_writes:` writes nothing to the vault.

The body opens with a **Contract**:

- **Input**: what the skill receives.
- **Output**: the exact deliverable and where it lands.
- **Allowed tools/artifacts**: what it may use.
- **Done when**: an observable completion condition.

Then come the triggers and context, the step-by-step blueprint, and the gotchas learned from real runs. Full schema: [resources/skills/README.md](gh:resources/skills/README.md).

## Enforceable language

"Be careful", "think deeply" and "act like an expert" are not policy: nothing observable follows from them. Skills replace each one with a clause naming an artifact or a check:

| Weak | Enforceable |
|---|---|
| Be careful with sources. | Cite the source file for every numeric claim. |
| Verify thoroughly. | Run the verifier before finalizing and record its verdict. |
| Keep the user informed. | Write the plan to `RESPONSE.md` and ask before step 2. |

## Shared modules

Some procedures are used by many skills, so they live once in [`_shared/`](gh:resources/skills/_shared/):

| Module | What it does |
|---|---|
| Evidence gate | Before a client-facing deliverable ships, every release-critical claim is tagged as observed or inferred and carries a source. |
| Delegation handoff | A child agent gets its task as a file and writes its result to a file, which the parent reopens. |
| Verifier separation | A distinct checking step, run apart from the step that produced the work. |
| Self-evolution | Within one run: reflect, redesign, retry, capped at 5 attempts. |
| Change manifest | Every harness edit records a falsifiable prediction, checked at its next real use. |

A skill declares the modules it uses in `modules:`, so modules can be compared and ablated across the library ([`MODULES.md`](gh:resources/skills/MODULES.md)).

## Script-backed skills

Deterministic work belongs in code. Many skills ship `scripts/` (Python or shell), and the `SKILL.md` tells the agent when to run them. The pattern in the scheduled loops: a cheap, no-LLM script does the polling and diffing, and an agent wakes only when something changed.

[Write your own skill →](../guides/write-a-skill.md)
