# Quickstart

You get a working, governed Claude Code session in about five minutes. The scheduled loops, mail and calendar come later and are all optional.

## What you need

| Requirement | Why |
|---|---|
| macOS | The scheduled jobs run under launchd, and calendar access goes through Calendar.app. The core harness (policy, skills, hooks) runs wherever Claude Code runs; only the loops are tied to macOS. |
| [Claude Code](https://claude.com/claude-code) | The runtime that reads the policy documents and calls the tools. |
| Python 3.9+, [`uv`](https://docs.astral.sh/uv/), `jq` | The hooks and scripts. `uv` pins every third-party tool, so you install nothing else globally. |

## Install

```bash
git clone https://github.com/pantheonzeus/charness.git && cd charness
cp IDENTITY.example.md IDENTITY.md        # your persona; git-ignored, never leaves your machine
git config core.hooksPath scripts/git-hooks   # the commit guard: secrets and client names stay out of git
scripts/check.sh                          # hook tests, skill lints, ruff, shellcheck
```

`scripts/check.sh` is the same command CI runs. If it ends with `check: all passed` locally, CI passes too.

## First session

```bash
claude
```

`CLAUDE.md` loads automatically and imports the [Charter](../reference/charter.md) and [Soul](../reference/soul.md). Before your first prompt, the SessionStart hook adds four more blocks to the context: the skill registry, the memory index, your persona and the active employer pack (none yet). [What happens next →](../concepts/session.md)

Try these to see the harness at work:

| Prompt | What to watch |
|---|---|
| `What can you do for a market analysis?` | The skill preselector names the matching strategy skills; the agent opens one and shows its blueprint before it starts. |
| `Research the current state of EU AI Act enforcement` | `research/deep-research` runs with a plan check-in, a STATE_ROOT under `output/.runs/` and cited sources. |
| `Write a file to /tmp/test.txt` | `write-boundary.sh` denies it: the target is outside the repo and the session scratchpad. |

## Optional next steps

- **Make it yours.** Rewrite `IDENTITY.md`, add an employer pack, remove skills you don't need. [Make it yours →](make-it-yours.md)
- **The console.** `uv run webapp/server.py` opens a local browser UI for voice and chat at `http://127.0.0.1:8765`. It runs on your Claude subscription. ([webapp/README.md](gh:webapp/README.md))
- **Mail and calendar.** Start the self-hosted Google Workspace MCP server: [resources/mcp/google-workspace.md](gh:resources/mcp/google-workspace.md).
- **Scheduled loops.** Every loop ships a reference launchd plist in its skill's `schema/` folder. [Headless jobs →](../concepts/headless-jobs.md)

## If something fails

- **A hook test fails in `check.sh`.** Check that `jq` is on your `PATH`; the shell hooks parse their input with it.
- **The skill lints fail.** Run the lint on its own to see the offending file: `uv run --no-project --with pyyaml==6.0.2 python3 resources/skills/vault-hygiene/skill-library-maintenance/scripts/lint_frontmatter.py`.
- **A write is denied that you expected to work.** The deny message names the rule. Interactive sessions may write in the repo, the session scratchpad and `~/.claude`. Headless jobs may write only inside their `write_scopes`. [Guardrails →](../governance/guardrails.md)
