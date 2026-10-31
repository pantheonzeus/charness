# Workflow — Propose skills from heavy sessions

Hermes Agent writes a skill on its own after a complex task. We take the trigger, not the autonomy: the agent drafts a **proposal**, and nothing enters `resources/skills/` without the principal's yes (Charter §7).

**Budget:** one scan, at most 3 proposals per pass, no web calls.

1. **Scan.** `python3 resources/skills/vault-hygiene/skill-library-maintenance/scripts/skill_candidates.py --days 7` lists sessions with ≥ 15 tool calls that no repo skill covered (the prompt names no skill slug, and no tool call touched `resources/skills/`).
2. **Judge each row** by opening its transcript (`~/.claude/projects/<repo-dir>/<session>.jsonl`). Keep a row only if the task **will recur** and the session found a **procedure** worth keeping: an ordered set of steps, a gotcha, a script. Drop one-offs, debugging and pure Q&A. Before proposing, check the closest existing skill in INDEX.md: if one nearly fits, propose a **trigger or Blueprint change to that skill** instead of a new one.
3. **Write the proposal** to `output/skill-proposals/<YYYYMMDD>.md` (git-ignored, because prompts carry client names). For each kept row:
   - the session id and the one-line task;
   - **new skill or edit to `<slug>`**, with category and slug;
   - the drafted triggers and description (the INDEX row);
   - a 3–7 step Core Blueprint lifted from what the session actually did, and its gotchas;
   - **why it recurs:** the evidence, such as other sessions with the same shape.
4. **Ask.** Show the proposals and ask which to build. Build only the approved ones, through this skill's normal add path (steps 3–7 of the Core Blueprint, lint and INDEX in the same change).

**Gotcha:** the console (`webapp/server.py`) runs one long session for many tasks, so its first prompt rarely names what the heavy work was. Read the whole transcript before judging it.
