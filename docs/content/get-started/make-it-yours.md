# Make it yours

charness keeps three kinds of content apart, so that when you swap one the others stay as they are:

| Kind | Where it lives | Public? | Changes when |
|---|---|---|---|
| **General**: policy, skills, hooks | the repo | yes | the harness improves |
| **Personal**: who you are, your knowledge | `IDENTITY.md`, the vault, the memory dir | no, git-ignored | you change |
| **Employer**: role, systems, clients | `employers/<slug>/` | no, git-ignored | you change jobs |

## 1. Write your persona

`IDENTITY.md` is injected fresh into every session. Copy the public template and rewrite each section:

| Section | What goes in it |
|---|---|
| Role & Organization | Who the agent speaks as, and for whom. |
| What I Believe | Your priority lens and the positions you actually hold. The agent argues from these. |
| Flagship Proof Points | The two or three pieces of work that content and profile skills may draw on. |
| Broader Background | Your expertise, audience and style preferences. |

The voice mechanics (no preamble, no hedging, no padding) and the inviolable lines live in [Soul.md](../reference/soul.md). They hold whichever persona is loaded, so you don't repeat them.

## 2. Add an employer pack (optional)

Everything that ends with an employment contract goes in one folder: your current title, which provider serves mail, calendar, files and chat, your employer's clients and partner domains, its chat channels, its brand and the loops those bindings feed.

```bash
cp -R employers/_template employers/acme
# fill in employers/acme/profile.json and role.md
echo acme > employers/ACTIVE
python3 scripts/employer.py validate
```

Without a pack, the mail, calendar and chat loops stay off. When you leave a job, `python3 scripts/employer.py exit-report <slug>` lists what to unload, revoke and keep. Content from a former employer keeps its confidentiality class after you leave. Full contract: [employers/README.md](gh:employers/README.md).

Skills ask for a **capability** (mail, calendar, files, chat), never a vendor. The contracts are in [resources/adapters/](gh:resources/adapters/). Google, Calendar.app and Slack are implemented; Microsoft 365 and Teams are documented stubs.

## 3. Prune the skill library

The library ships the original author's working set. Delete what you won't use, or move it to `status: deprecated`. When you remove a skill, remove its row from `resources/skills/INDEX.md` and its slug from the category's `_category.md` in the same change. The agent finds skills through the index, so a skill without a row is invisible, and an index row whose skill you deleted points at nothing.

## 4. Point the vault somewhere

Long-term knowledge lives in an Obsidian vault at `cbrain/`, which is git-ignored. Start empty, and the knowledge-graph skills will build it as you work. [State, memory and the vault →](../concepts/state-and-memory.md)
