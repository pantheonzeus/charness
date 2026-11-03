# Model addenda

One file per model family (`opus.md`, `sonnet.md`, `haiku.md`, `fable.md`). `scripts/run_agent.sh` appends the file for the job's model to its system prompt (`--append-system-prompt-file`), and the regression suite (`run-forensics/scripts/regression.py`) does the same, so the suite tests what the jobs run. A family without a file gets nothing.

**What goes in:** only fixes Anthropic's prompting page for that model gives and says it tested, copied word for word, for a behaviour that matters to unattended jobs. Everything that holds for every model belongs in the Charter, a skill or an agent file, not here. Anthropic: "Where a technique names a specific model, treat it as measured on that model and re-check it against your own evals before applying it to another" ([Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)).

**How it changes:** a new or edited file passes `regression.py --model <id> --addendum <candidate>` at pass^3 before it lands here; it goes live for every job on that family at their next run. When a job's pinned model moves to a new version, re-read the new model's prompting page and drop what it no longer lists (`workflow-ops/harness-upgrade-scout`).

| File | Source (accessed 2026-11-01) | Why |
|---|---|---|
| `opus.md` | [Prompting Claude Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5), "Unattended agentic runs" | Opus 5.5 can end a turn on a progress note, which ends a headless run with work still owed. The Opus jobs (client-news, linkedin-viral, harness-upgrade-scout, harness-upgrader, plan drafting) run unattended. |
| `sonnet.md` | [Prompting Claude Sonnet 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5-5), "Tool use in chat and knowledge work" | Sonnet 5.5 sometimes answers from training knowledge where a search would catch a changed detail. The Sonnet jobs research, brief and triage, and all have web search. |
