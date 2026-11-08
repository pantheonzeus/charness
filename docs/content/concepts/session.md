# Anatomy of a session

Here is what happens around one prompt, in order. Each step is a Claude Code hook declared in [`.claude/settings.json`](gh:.claude/settings.json).

```text
SessionStart ──► UserPromptSubmit ──► model works ──► PreToolUse ──► tool ──► PostToolUse ──► … ──► Stop
  inject           preselect skills     opens SKILL.md    guard            runs    label         gate
```

## 1. SessionStart: four blocks of context

Before the first prompt, four blocks are injected:

1. **Skill registry.** A compact list of every skill slug by category (`scripts/skill_router.py compact`). The full `INDEX.md` is longer than the hook-context cap, so the agent gets the short form here and reads the full rows on demand.
2. **Memory index.** `MEMORY.md`: one line per learned fact or correction, plus a stale-fact warning from `scripts/memory_sweep.py`.
3. **Persona.** `IDENTITY.md`, or the public `IDENTITY.example.md` if you have none.
4. **Employer pack.** Role, provider bindings and the confidentiality class, from `scripts/employer.py context`.

## 2. UserPromptSubmit: skill preselection

[`scripts/skill_router.py`](gh:scripts/skill_router.py) scores the prompt against every skill's triggers, name, description and body (BM25, deterministic) and injects the best-matching rows. It stays quiet unless at least two prompt words or a whole trigger phrase back the match. A prompt that names a skill gets only that skill.

The preselection is a hint. If nothing listed fits, the Charter requires a search of `INDEX.md` before the agent concludes that no skill exists, and before it tells you anything can't be done.

## 3. The model works

The agent opens the matched `SKILL.md` and follows its contract (input, output, allowed tools, done-when). For substantive work it shows the blueprint first and asks before it executes. Multi-step runs keep their state in a STATE_ROOT under `output/.runs/`. [State →](state-and-memory.md)

## 4. PreToolUse: the guards

| Tool call | Guard |
|---|---|
| Write, Edit, MultiEdit, NotebookEdit | `write-boundary.sh`: allowed zones, or the job's write scopes · `ingest_lint.py hook`: asks before a memory write in a session that took in outside text |
| WebFetch, WebSearch | `egress-guard.sh`: no email address, encoded blob or oversized query leaves |
| Any MCP send tool | `send-gate.sh` → `send_gate.py`: your explicit yes plus a clean outbound scan; fails closed |
| Bash | `commit_guard.py hook`: no `--no-verify`, no redirected git hooks, no force push |

## 5. PostToolUse: provenance

After a write to a vault note, `ingest_lint.py hook` reads the session transcript. If outside text came in during the session (web, mail, chat, pasted content, an untrusted note), the note is stamped `provenance: derived-untrusted`. The decision comes from the transcript; the writer can't opt out. [Untrusted ingest →](../governance/untrusted-ingest.md)

If a Read or Edit fails on a missing path, `path-hint.py` answers with what does exist nearby, so the agent stops guessing paths.

## 6. Stop: two gates

- **Control-spine gate.** The run can't end while a `RESPONSE.md` this session touched still has unchecked `[ ]` checkpoints. Another session's open run never blocks yours.
- **Memory nudge.** In interactive sessions, once every 30 tool calls, the agent is asked to propose up to three memory candidates. Nothing is saved without your yes.

## 7. After the task

The Charter ends every task with two questions: any feedback on the workflow, and should a skill be added or updated. Approved changes land in the skill's `SKILL.md`. Edits to the Charter or to shared modules also get a change-manifest entry: a falsifiable prediction of their effect, checked at the next real use.
