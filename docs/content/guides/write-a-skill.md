# Write a skill

A good skill turns a task you keep explaining into a policy the agent follows the same way every time. The skill is finished when someone else's agent could run it from the file alone.

## 1. Check it doesn't exist

Search the index first. The library is large, and a near-match you can extend beats a duplicate.

```bash
grep -i "your keyword" resources/skills/INDEX.md
```

Or ask in a session: *"Is there a skill for X?"* The agent runs the same check.

## 2. Copy the template

```bash
mkdir -p resources/skills/<category>/<skill-slug>
cp resources/skills/_template/SKILL.md resources/skills/<category>/<skill-slug>/SKILL.md
```

Pick an existing category ([catalog](../reference/skills.md)). `id` must match the folder name.

## 3. Write the contract first

```markdown
**Contract**
- **Input:** a company name and the meeting date.
- **Output:** `output/briefs/<YYYYMMDD>-<company>.md`, max two pages.
- **Allowed tools/artifacts:** WebSearch, WebFetch, the vault (read-only).
- **Done when:** every claim in the brief carries a source and the brief passes the evidence gate.
```

If you can't write *Done when* as something observable, the skill isn't ready. A vague contract turns the rest of the document into advice.

## 4. Write the blueprint in enforceable language

Numbered steps, each one naming an artifact, a check or a decision. Replace every "be careful" with the check that would show care. Keep the body short: deep material goes into `references/`, and deterministic work goes into `scripts/`.

## 5. Declare what it touches

| Key | When |
|---|---|
| `vault_writes:` | The skill creates or edits vault notes. Use the narrowest globs that cover them. |
| `requires:` | It needs tools, CLIs or other skills. Split mandatory from `optional`. |
| `modules:` | It uses shared modules (evidence gate, handoff, …). Values come from [`MODULES.md`](gh:resources/skills/MODULES.md). |

## 6. Register it, in the same change

1. Add one row to `resources/skills/INDEX.md` under the category: name · triggers · description · path.
2. Add the slug to the category's `_category.md` **Skills:** line.
3. Run `scripts/check.sh`. The frontmatter lint and the Agent Skills spec export must pass.

A skill missing from the index is invisible to the agent.

## 7. Let real runs improve it

At the end of every task the agent asks whether the skill should change. Accept, and it edits the `SKILL.md`, bumps `version` and `updated`, and logs the failure mode under **Optimizations/Gotchas**. Ten skills in the library are on version 7 or later. Each version fixed a failure that actually happened.
