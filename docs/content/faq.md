# FAQ

### Is this a product?

No. It's a working configuration for Claude Code that you fork and make your own. The policy, skills and guards are general; your persona, vault and employer data stay on your machine and out of git.

### Does it need an API key?

No. Interactive sessions and the console run on your Claude subscription through Claude Code; the console strips `ANTHROPIC_API_KEY` from the agent's environment. The headless jobs call `claude -p` with the same login.

### Does it run on Linux or Windows?

The core does: the Charter, the skills and the hooks run wherever Claude Code runs. The scheduled loops use launchd, and calendar access uses Calendar.app, so those are macOS-only today. CI runs on macOS for the same reason.

### Why Markdown policies instead of code?

Because most of what makes an agent useful is judgment, and judgment reads better as prose: you can review it, diff it and edit it in one place. The research the harness is built on found natural-language harnesses competitive with code-realized ones while keeping the policy short and readable. The parts that must never depend on judgment are in code anyway. [Architecture →](concepts/architecture.md)

### Can the agent switch off its own guardrails?

Not through the paths it has. The guards are Claude Code hooks, outside the model's control. The Bash hook denies the known ways around the commit guard. CI repeats the commit scan on everything pushed. Headless jobs that run their own code are sandboxed at OS level. Most guards fail open on an internal error, so that a hook bug doesn't stall real work; the send gate fails closed. [Guardrails →](governance/guardrails.md)

### What happens to my data?

Your vault, memory, deliverables, persona and employer packs are git-ignored and never leave your machine through the repo. The commit guard blocks them if you try to add them by force. Web calls that would carry data out are denied, and nothing is sent without your explicit yes. This site makes no third-party requests and sets no cookies: fonts are bundled at build time.

### Why are some skills missing from the catalog?

A few personal-workflow skills are in the repo but not listed on this site. Everything else in [`INDEX.md`](gh:resources/skills/INDEX.md) is generated into the [catalog](reference/skills.md) at build time.

### How do I contribute?

Read [CONTRIBUTING.md](gh:CONTRIBUTING.md). Open an issue with the *skill or enhancement* template, keep changes surgical, and run `scripts/check.sh` before you push. Never put a real client, colleague or account name in a skill: skills stay client-independent, and the commit guard checks.

### What's the licence?

MIT, with one exception: the Lean Service Creation skills adapt canvas content from the Lean Service Creation Toolbox and are licensed CC BY-SA 4.0. See [NOTICE](gh:NOTICE).
