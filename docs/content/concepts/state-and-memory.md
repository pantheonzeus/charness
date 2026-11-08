# State, memory and the vault

The Charter's rule is to **prefer a file on disk over a summary in context**. The NLAH module ablation backs it: file-backed state was the strongest positive module, and context compression was the one that clearly hurt ([Charter §4](../reference/charter.md#4-file-backed-state-evidence-discipline)). charness keeps four kinds of durable state, each with its own job.

| State | Where | Lifetime | Holds |
|---|---|---|---|
| **Deliverables** | `output/` | permanent | Finished reports, drafts, analyses |
| **Run state** | `output/.runs/<YYYYMMDD-slug>/` | one run | The control spine, evidence, child task packets |
| **Memory** | `~/.claude/projects/…/memory/` | across sessions | One file per learned fact or correction |
| **Vault** | `cbrain/` (Obsidian) | long-term | People, topics, meetings, sources: the knowledge graph |

## Run state: the STATE_ROOT

Every substantive multi-step run gets a folder:

```text
output/.runs/20261108-market-scan/
├── RESPONSE.md        # control spine: the checkpoints the run must clear, as [ ] / [x]
├── EVIDENCE.md        # the source behind each release-critical claim
└── children/<id>/     # delegated work: TASK.md in, RESPONSE.md out
```

The agent reopens these files by path after each step and after context compaction, so critical state never lives only in the conversation. A Stop hook won't let the run end while its control spine has open boxes.

## Memory: facts that stay true

The memory dir holds one Markdown file per fact, indexed by `MEMORY.md`, which is injected at session start. Memories go stale, and agents keep reusing invalidated ones, so charness manages their lifecycle:

- A retired claim moves to a dated `## Superseded` section. A replaced memory carries `superseded_by:`.
- `scripts/memory_sweep.py` flags drift at session start.
- `vault-hygiene/memory-consolidation` is a reviewed "dream" pass. It works on a copy and reaches the live memory only on your yes.

## The vault: a living knowledge graph

The Obsidian vault is the long-term brain. Two rules keep it trustworthy while many agents write to it:

- **Writing is declared.** A skill may write vault notes only if its frontmatter declares `vault_writes:`, and only inside those paths. Any other task ends with a list of *proposed* links and writes nothing until you agree. Headless jobs are held to their scopes by a hook.
- **Linking is bi-directional.** A new person is never an island: they get linked to the topics, people and engagements they touch, with a one-line reason on each side.

Two more mechanisms:

- **Trust tier.** `confirmed: YYYY-MM-DD` means you vouched for a note on that date. Only you can set it; headless jobs can't add, change or remove it. When a confirmed and an unconfirmed note disagree, the confirmed one wins and the contradiction is named.
- **Private history.** `scripts/vault_history.sh` keeps a local-only git history of the vault, outside the synced folder, and refuses pushes. Each headless run becomes one commit holding exactly the files it wrote, so you can review or revert any run.
