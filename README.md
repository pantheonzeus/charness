# charness — Unified AI Agent Workspace

A configuration-as-code workspace for [Claude Code](https://claude.com/claude-code). It turns a general-purpose agent into a consistent, opinionated operator with a fixed identity, a set of operating rules, and a reusable **skill library** — tuned for research, high-signal content, and automated knowledge-work.

> **Note on scope.** The private knowledge vault (`cbrain/`), the `autoresearch/` scratch area, the `input/` artifacts folder, the `output/` deliverables folder, and your private `IDENTITY.md` persona are git-ignored and **not** part of this repository. What's tracked here is the *operating system* — the voice mechanics, rules, skills, and integration setup — not the data or the specific persona it operates with.

## Foundation

This workspace is a concrete implementation of the **Natural-Language Agent Harness (NLAH)** paradigm introduced in Pan, Zou, Guo, Ni & Zheng, *[Natural-Language Agent Harnesses](https://arxiv.org/abs/2603.25723)* (arXiv:2603.25723).

The paper's thesis: agent performance is shaped less by the model than by the *harness* around it, and that harness policy is best expressed as **editable natural-language documents** — not code or ad-hoc prompts — interpreted at run time by an **Intelligent Harness Runtime (IHR)**. Their result is that NL-expressed harnesses match code-realized ones on task outcomes while keeping the static policy far shorter and readable.

This repo maps onto that architecture directly, separating **policy from mechanism**:

| NLAH concept (paper) | Realization here |
|---|---|
| Run-level harness policy (editable docs) | [Charter.md](Charter.md) — universal physics for every run |
| Agent identity / voice | [Soul.md](Soul.md) — voice mechanics + inviolable lines; the persona itself is `IDENTITY.md` (private) / `IDENTITY.example.md` (public template) |
| Task-specific NL harness documents | `resources/skills/**/SKILL.md` — one editable policy doc per task type |
| Reusable, ablatable harness modules | `resources/skills/MODULES.md` (vocabulary) + `_shared/` (file-backed state, evidence gate, handoff, self-evolution) |
| Intelligent Harness Runtime (interprets docs → calls, handoffs, gates, artifacts) | Claude Code + `.claude/` hooks + the skill-dispatch protocol |
| File-backed run state / artifact separation | `STATE_ROOT` (`output/.runs/<slug>/` — control spine + evidence) kept distinct from `output/` deliverables (Charter §4) |
| Parent→child handoff discipline | file-backed task packets + reopened result files (Charter §5, `_shared/delegation-handoff.md`) |
| Validation gates & artifact contracts | PreToolUse write / egress / send gates, Stop-hook control-spine gate, `link_audit` graph gate, the evidence gate (Charter §4), `output/` deliverables |

The rest of this README describes that implementation.

---

## What's in the repo

```text
├── Charter.md           # Runtime physics: execution discipline, skill dispatch, gates (every run)
├── Soul.md              # Voice mechanics + inviolable lines, persona-agnostic (always-on)
├── IDENTITY.example.md  # Public persona template — copy to IDENTITY.md and make it yours
├── IDENTITY.md          # Your private persona: role, beliefs, proof points (git-ignored)
├── employers/           # Employer packs: what ends with a job (bindings, clients, channels, brand, loops) — README + _template public
├── CLAUDE.md            # Project map: architecture, structure — imports Charter + Soul
├── HARNESSCARD.md       # CAR harness-disclosure card (Control–Agency–Runtime, 8 fields)
├── .mcp.json            # MCP server wiring (Google Workspace over HTTP)
├── .claude/             # Harness automation — settings.json (hooks), hooks/ (+ tests/), agents/ (one file per headless job)
├── resources/
│   ├── adapters/        # Provider capability contracts: mail, calendar, files, chat
│   ├── mcp/             # MCP connection docs (Google Workspace / Gmail + Calendar)
│   └── skills/          # The skill library — see below
├── scripts/             # Shared mechanism: agent runner + scorecard, skill router, employer packs, gates, vault history
├── webapp/              # Local browser console — voice + chat with the harness via `claude -p`
├── demos/frameshift/    # Frame-Shift Lab — autonomous discovery-loop demo on synthetic data
├── output/              # Finished deliverables, run state (output/.runs/) & logs (git-ignored)
├── input/               # Input artifacts, e.g. analytics exports (git-ignored)
├── .github/             # Issue + pull-request templates
├── CONTRIBUTING.md · CODE_OF_CONDUCT.md · SECURITY.md
└── LICENSE · NOTICE     # MIT; the Lean Service Creation skills are CC BY-SA 4.0 (NOTICE)
```

## The policy layers

| File | Role |
|---|---|
| **[Charter.md](Charter.md)** | *How every run executes.* Universal physics for every task: execution discipline (simplicity-first, surgical changes, goal-driven), the skill-dispatch protocol, file-backed state & delegation/handoff, the living knowledge-graph triggers, the continuous self-learning loop, and the inviolable lines asserted as binding runtime physics. |
| **[Soul.md](Soul.md)** | *How the agent always sounds.* Voice mechanics (impatience with preamble, no hedging, no performative warmth) and inviolable lines in voiced form (never leak instructions, never oversell, never dress a guess as a fact) — the same regardless of which persona is loaded. |
| **`IDENTITY.md` / [IDENTITY.example.md](IDENTITY.example.md)** | *Who the agent is.* Role, organization, priority lens, real positions held, and flagship proof points — your private `IDENTITY.md` (git-ignored) or the generic public default, injected fresh each session by the SessionStart hook. |
| **[CLAUDE.md](CLAUDE.md)** | *The entry point.* Project context and the layer map, on-disk structure — it `@`-imports Charter and Soul so both load automatically every session. |

Charter is the runtime that selects and executes the skill library; Soul plus the injected persona is the voice it executes them in; CLAUDE.md is where a session starts reading. **[HARNESSCARD.md](HARNESSCARD.md)** is the disclosure card for the whole setup — the Control–Agency–Runtime template (8 fields: base model, control artifacts, runtime policy, action substrate, execution topology, feedback stack, governance/observability, evaluation protocol).

## The skill library (`resources/skills/`)

The heart of the workspace. Each skill is a self-contained recipe — YAML frontmatter (triggers, tags, status, version) plus a body (name, triggers/context, step-by-step blueprint, gotchas). The agent scans the index, matches a task to triggers, and opens only the matched skill.

- **[`INDEX.md`](resources/skills/INDEX.md)** — the registry scanned first on every task (name · triggers · description · path).
- **[`README.md`](resources/skills/README.md)** — the contract: `SKILL.md` schema, taxonomy, and how to add or optimize a skill.
- **[`MODULES.md`](resources/skills/MODULES.md)** — the harness-module vocabulary (the values a skill declares in its `modules:` key), grounded in the paper's module ablation.
- **`_shared/`** — cross-skill modules invoked by the Charter: the evidence gate, the delegation/handoff contract, the self-evolution loop, verifier-separation, and the change-manifest (+ its `CHANGE_LOG.md` ledger) for between-session harness edits.
- **`_template/SKILL.md`** — starting point for new skills.
- **`_evals/`** — golden sets for the skill router (`routing.tsv`, scored by `python3 scripts/skill_router.py eval`) and for recall.

**Ten categories.** The current skill list and count live in [`INDEX.md`](resources/skills/INDEX.md) — deliberately not repeated here, so this page can't drift from the registry.

| Category | Holds |
|---|---|
| **knowledge-graph** | People, linking, relationships, vault graph structure (contact capture, dossiers, intros, dedupe) |
| **research** | Sourcing, citations, distillation (source → topic note, NotebookLM), deep research, newsletter watches, vault-frontier expansion |
| **sales** | Proposals, pursuits, account and competitor intelligence, executive briefs, RFP clarification, client follow-through |
| **content** | Executive communication, LinkedIn storytelling / engagement / video, speaker submissions |
| **strategy** | Strategy-consulting frameworks — diagnosis, market/competitive intelligence, strategic choice & economics, operating model, risk/value governance, executive alignment |
| **technology** | Principal-engineer architecture method — application, cloud, agent and multi-agent platforms, data migration, strangler-fig modernisation |
| **service-design** | End-to-end service design — discovery, journey maps, blueprints, ecosystem maps, prototyping, measurement, plus agentic services |
| **business-design** | The viability owner's method — opportunity framing, value propositions, business models (as-a-service, platform, AI-native), experiments, the Lean Service Creation canvases |
| **workflow-ops** | Recurring pipelines — session sync & recall, calendar/mail → vault, mail triage, chat intel, morning and daily-intel briefings, meeting prep, living plans, idea engine, run forensics, LinkedIn scheduling & calibration, daily reports |
| **vault-hygiene** | Obsidian structure, progressive disclosure, link-integrity sweeps, skill-library maintenance, deliverable indexing |

Several skills are **script-backed** — Python/shell helpers under each skill folder, with `workflows/`, `references/`, and `schema/` bundles for the deeper ones (e.g. `research/notebooklm` ships `load_channel`, `resolve_citations`, `extract_passages`, `link_audit`). The `workflow-ops` and `research` skills also depend on the Google Workspace / NotebookLM connections.

## Automation & guardrails (`.claude/`)

The workspace enforces its own rules mechanically rather than trusting the agent to remember them. Configured in **[`.claude/settings.json`](.claude/settings.json)**:

| Mechanism | What it does |
|---|---|
| **SessionStart injection** | Every session opens with four blocks injected into context: the **skill registry** (a compact category → slug list from `scripts/skill_router.py compact`, since the full `INDEX.md` exceeds the hook-context cap), the **persistent memory index** (`MEMORY.md` — learned facts & corrections — plus a one-line stale-fact warning from `scripts/memory_sweep.py`), the **active persona** (`IDENTITY.md` if present, else `IDENTITY.example.md`), and the **active employer pack** (`scripts/employer.py context`). |
| **UserPromptSubmit skill preselector** | [`scripts/skill_router.py`](scripts/skill_router.py) injects the few `INDEX.md` rows that best match each prompt (deterministic BM25 over triggers, name, description and the `SKILL.md` body; stays quiet unless two prompt words or a whole trigger phrase back the match, and a prompt that names a skill gets only that skill). Recall is scored against `resources/skills/_evals/routing.tsv`. |
| **PreToolUse write-boundary guard** | [`hooks/write-boundary.sh`](.claude/hooks/write-boundary.sh) denies any `Write`/`Edit` whose target — resolved through `..` segments and symlinks — falls outside the repo, the session scratchpad, or `~/.claude`. For a headless job (`CBRAIN_JOB`, set by `scripts/run_agent.sh`) it allows only the `write_scopes:` in that job's `.claude/agents/<job>.md`, so a scheduled agent can't touch vault notes outside its lane. Fail-open by design — a parse hiccup never blocks real work. Bash-run writes never pass this hook, so they have their own two paths: [`scripts/vault_api.py`](scripts/vault_api.py), a typed batch writer (`find`, `apply`) that enforces the same scopes and provenance in its own code and is all-or-nothing, and `code_mode: true` in an agent file, which forces the sandbox with the vault and the harness denied for writing. |
| **PreToolUse egress guard** | [`hooks/egress-guard.sh`](.claude/hooks/egress-guard.sh) denies `WebFetch`/`WebSearch` calls whose URL or query carries an exfiltration shape: an email address (other than the principal's public one), an encoded blob, or an oversized query string. Fail-open. |
| **PreToolUse send gate** | [`hooks/send-gate.sh`](.claude/hooks/send-gate.sh) → `send_gate.py` stops any MCP send tool (mail, chat) unless the latest human message is an explicit "send" and the draft passes the deterministic outbound scan (`scripts/outbound_gate.py`: other clients' names, third-company contacts, internal channel names). **Fail-closed** — a send is irreversible. |
| **Provenance hook (Pre + PostToolUse)** | [`scripts/ingest_lint.py`](scripts/ingest_lint.py) `hook`: after a `Write`/`Edit` to a vault note, it reads the session transcript (and its subagents'). If outside text came in — web tools, mail/chat MCP tools, pasted content, a Read of an ingest or derived note, or a job whose agent file says `untrusted_ingest: true` — a note with no label gets `provenance: derived-untrusted` with `derived_from:` and `derived_by:`, so the label survives the agent's rewrite. In such a session it asks before any write to the memory dir. `backfill` replays past transcripts with the same rule (dry run by default). |
| **Private vault history** | [`scripts/vault_history.sh`](scripts/vault_history.sh) keeps a local-only git history of the vault (git dir outside the synced folder, pushes refused). `run_agent.sh` commits once per headless run, authored by the job and holding exactly the vault files that run wrote (read from its transcript), so any run's vault changes can be reviewed and reverted. |
| **Stop control-spine gate** | [`hooks/control-spine-gate.sh`](.claude/hooks/control-spine-gate.sh) blocks the run from stopping while a `output/.runs/*/RESPONSE.md` control spine **this session touched** still has unchecked `[ ]` checkpoints — the un-bypassable half of Charter §4's file-backed-state discipline. Another session's open run never blocks yours; fail-open on any error; never loops (respects `stop_hook_active`). |
| **Ingest provenance** | [`scripts/ingest_lint.py`](scripts/ingest_lint.py) stamps vault notes holding outside text (mail, newsletters, chat) as `provenance: untrusted-ingest` and flags instruction-shaped text in them, so untrusted data written by one agent isn't read as instructions by the next. Runs in the weekly vault ratchet. |
| **Persistent memory** | The self-learning loop's storage, and the model's path-addressable cross-session state. Learned facts live one-per-file under `~/.claude/projects/.../memory/`, indexed by `MEMORY.md` and recalled each session. Deliberately files, not an in-context summary — the paper's ablation shows path-addressable state beats aggressive compression, which measurably hurt. |
| **`link_audit` graph gate** | A blocking check (`research/notebooklm/scripts/link_audit.sh`) that fails a notebook import if the new source note doesn't reach a `type:topic` anchor — mechanically enforcing the bi-directional knowledge-graph rule. Also runs as a daily sweep. |

Hook tests: `bash .claude/hooks/tests/<hook>.test.sh` (write-boundary, egress-guard, send-gate, provenance, vault-api).

**Headless agent jobs.** Each scheduled or console-delegated agent has one definition in [`.claude/agents/`](.claude/agents/) — model, `budget_usd:` and `write_scopes:` — and runs through [`scripts/run_agent.sh`](scripts/run_agent.sh), which wraps one `claude -p` call: it applies the budget cap, exports `CBRAIN_JOB` for the write guard, snapshots the vault before and after, reopens the job's handoff file, appends cost/turns/outcome to `output/.runs/_ledger/<job>.jsonl`, and classifies the run (clean / degraded / failed) via `workflow-ops/run-forensics`. [`scripts/agent_scorecard.sh`](scripts/agent_scorecard.sh) summarises the ledger per job (success rate, yield, cost per productive run).

**Scheduled jobs (launchd).** The loops — mail triage, meeting prep, chat intel, daily-intel briefing, newsletter watches, vault frontier, idea engine, NotebookLM audio + distill, LinkedIn scheduling, run forensics, the weekly vault ratchet, plus the Workspace MCP service and the console — run as `com.cbrain.*` jobs in `~/Library/LaunchAgents/`. The installed plists are user-machine config; the reference plists ship in each skill's `schema/` (or `scripts/`) folder, and loops tied to an employer's systems are declared in its pack (`python3 scripts/employer.py loops`). Logs land in `output/`.

## The console (`webapp/`)

A local browser UI for running the harness by voice or chat. The conversation is one long-lived `claude -p` process started from the repo root, so it gets the full harness (Charter, Soul, hooks, memory, skill index), and it runs on your claude.ai subscription — the server strips `ANTHROPIC_API_KEY` from the child's environment.

```bash
uv run webapp/server.py        # → http://127.0.0.1:8765
```

One page: the assistant and the conversation on the left, a single "stage" on the right (today's meetings and reading, a topic, a deliverable, a plan). Research and anything that commits you to a number or a position becomes a **living plan** run in the background by the `plan-runner` / `researcher` agents; Mail, Library, Ideas and Situation views sit behind a menu. `webapp/com.cbrain.webapp.plist` keeps it running under launchd. Full feature tour: [`webapp/README.md`](webapp/README.md).

**Frame-Shift Lab** ([`demos/frameshift/`](demos/frameshift/README.md)) is a separate browser demo: an autonomous discovery loop on synthetic data that pits hypothesis search inside the original frame against a loop that first rewrites the question, with code-decided statistical gates and a blind human review. `uv run demos/frameshift/server.py` → `http://127.0.0.1:8770`.

## Employer packs and provider adapters

Everything that ends with an employment contract lives in one gitignored folder, `employers/<slug>/`: the current role, which provider serves each capability (mail, calendar, files, chat), that employer's clients and partner domains, its chat channels, its brand and the launchd loops its bindings feed. A new job is a new pack from `employers/_template/`, not a rebuild; leaving runs `python3 scripts/employer.py exit-report`. Skills ask for a capability, never a vendor; the contracts live in `resources/adapters/` (Google, Calendar.app and Slack implemented; Microsoft 365 and Teams documented stubs). Runbook: [`employers/README.md`](employers/README.md).

## Integrations — Google Workspace MCP

Gmail and Calendar access run through a self-hosted [Google Workspace MCP server](https://github.com/taylorwilsdon/google_workspace_mcp), scoped to `--tools gmail calendar` over HTTP.

```bash
# Start the server manually (or let the launchd service run it on login)
scripts/start-google-workspace-mcp.sh
```

`.mcp.json` points Claude Code at it on `localhost:8000`. First tool call opens a browser for OAuth consent. In practice the server runs as a **launchd standing service** (`com.cbrain.workspace-mcp.plist`, `RunAtLoad` + `KeepAlive`), so the manual command is only a fallback. Full setup, scope expansion, the launchd plist, and the offline fallback path are in **[resources/mcp/google-workspace.md](resources/mcp/google-workspace.md)**.

> Two additional connectors (`claude.ai Figma`, `claude.ai Slack`) are configured on the claude.ai side — not in this repo's `.mcp.json` — and require authorization via your claude.ai connector settings before use.

## Getting started

1. **Make it yours:** `cp IDENTITY.example.md IDENTITY.md`, then rewrite it — your role, organization, priority lens, real positions, flagship proof points. `IDENTITY.md` is git-ignored; it never leaves your machine.
2. (Optional) **Add your employer:** copy `employers/_template/` to `employers/<slug>/`, fill in `profile.json` and `role.md`, write the slug to `employers/ACTIVE`, then check it with `python3 scripts/employer.py validate`. Without a pack, mail/calendar/chat loops simply stay off.
3. Open the repo in Claude Code — `CLAUDE.md` loads automatically (it imports `Charter.md` and `Soul.md`), and the SessionStart hooks inject the skill registry, memory index, your `IDENTITY.md` and the active employer pack.
4. Browse **[resources/skills/INDEX.md](resources/skills/INDEX.md)** to see what the agent can do — several `workflow-ops`/`content` skills are personal-workflow examples (LinkedIn growth, sales outreach) built around the original author's persona; adapt or delete what doesn't fit yours.
5. (Optional) Start the Workspace MCP server for Gmail/Calendar-backed skills, the console (`uv run webapp/server.py`), and whichever launchd loops you want.
6. Give it a task — it scans the skill index, proposes a blueprint, then executes.

## License

MIT — see [LICENSE](LICENSE), with one exception: the Lean Service Creation skills (`resources/skills/business-design/lean-service-creation/` and `lsc-*/`) adapt canvas content from Futurice's Lean Service Creation Toolbox and are licensed **CC BY-SA 4.0**, not MIT. See [NOTICE](NOTICE).
