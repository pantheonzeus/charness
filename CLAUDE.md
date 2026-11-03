# Project Context
This is my unified AI agent workspace optimized for advanced research, high-quality content creation, and automated productivity workflows. This environment acts as an extension of my digital mind, combining automated processing with a structured long-term knowledge repository.

# About Me (the principal)
Who the principal is — role, organization, beliefs, flagship proof points, content style — lives in `IDENTITY.md` (private, gitignored) or the generic public default `IDENTITY.example.md` if you haven't set one up yet. It's injected fresh each session by the SessionStart hook; edit that file, not this one, to make this workspace yours. Everything that ends with an employment contract (current title, mail/calendar/files/chat bindings, that employer's clients, Slack channels, brand, confidentiality approvals, its launchd loops) lives in the active **employer pack**, `employers/<slug>/` (private, gitignored; contract and switch/exit runbook in `employers/README.md`), injected right after the persona.

# Workspace Architecture — a Natural-Language Agent Harness
This workspace is a layered agent harness that keeps **policy separate from mechanism**. Four layers, each with one job:

- **Backend (mechanism / code)** — `.claude/` hooks (SessionStart injects a compact skill registry + memory index (with a stale-fact line) + active persona + active employer pack; UserPromptSubmit preselects the likely skills per prompt; PreToolUse guards writes, web egress and sends; PostToolUse keeps the untrusted label on vault notes written from outside text; a PreToolUse write-guard that also holds each headless job to its declared `write_scopes:`; Stop hooks enforcing the control spine and, in interactive sessions, proposing memory candidates every ~30 tool calls) and per-skill `scripts/`/`workflows/`/`schema/`. Deterministic; changes rarely.
- **Runtime Charter (universal physics)** — [Charter.md](Charter.md): fixed run-level policy that applies to *every* task and dispatches the skill library. Changes rarely.
- **Identity (voice + persona)** — [Soul.md](Soul.md): the voice mechanics and inviolable lines that apply no matter who's loaded, always imported here. The persona itself — role, organization, beliefs, priority lens — lives in `IDENTITY.md` (private, gitignored) or `IDENTITY.example.md` (public default), injected fresh each session by the SessionStart hook. Embody whichever persona is loaded in every interaction.
- **NLAH library (task logic)** — `resources/skills/`: one editable policy document per task type. Scan `INDEX.md`, match on triggers, open the matched `SKILL.md`. Changes often.

The Charter is the runtime that selects and executes the skills (the NLAHs); the Soul plus the injected persona is the voice it executes them in. Load the always-on layer:

@Charter.md

@Soul.md

# Project Structure
*(Actual on-disk layout. The repo root holds the tooling; the live Obsidian vault is `cbrain/` below.)*
```text
├── CLAUDE.md           # Entry point — loads Charter + Soul, describes this layout
├── Charter.md          # Runtime Charter — universal physics (every run)
├── Soul.md             # Identity mechanism — voice mechanics + inviolable lines (persona-agnostic)
├── IDENTITY.example.md # Public persona template — copy to IDENTITY.md and make it yours
├── IDENTITY.md          # Your private persona (gitignored, not tracked)
├── employers/          # Employer packs: README.md + _template/ public; <slug>/ + ACTIVE gitignored (role, provider bindings, clients, channels, brand, loops, exit list)
├── HARNESSCARD.md      # Harness disclosure card — Control/Agency/Runtime/Governance/Eval (CAR template)
├── README.md · LICENSE · CONTRIBUTING.md · CODE_OF_CONDUCT.md · SECURITY.md  # repo docs
├── .github/            # issue templates + pull_request_template.md
├── .mcp.json           # project MCP server config
├── scripts/            # Operational scripts (e.g. start the Workspace MCP server; employer.py = active employer pack: resolver, validate, loops, exit report; skill_router.py = compact registry + per-prompt skill preselection; outbound_gate.py = confidentiality scan for sends and public drafts; ingest_lint.py = provenance stamp + derived-note hook + injection lint; memory_sweep.py = stale-memory check; run_agent.sh = shared runner for scheduled agent jobs → output/.runs/_ledger/<job>.jsonl; agent_scorecard.sh; vault_history.sh = private local git history of the vault, one commit per headless run, in the gitignored .vault-history.git/; vault_api.py = typed batch writer for Bash-run vault appends, holding the job's write_scopes + provenance)
├── webapp/             # Local browser console — chat with the harness via `claude -p` (subscription, not API) + read-only loops panel; `uv run webapp/server.py`
├── demos/frameshift/  # Frame-Shift Lab — browser demo of an autonomous discovery loop (control vs frame-shift arm) on synthetic data via headless `claude -p`; `uv run demos/frameshift/server.py`
├── output/             # Finished deliverables (reports, drafts, data analysis, final assets) — git-ignored
│   └── .runs/          #   STATE_ROOTs: <YYYYMMDD-slug>/RESPONSE.md (control spine) + EVIDENCE.md + children/<id>/
├── input/              # Input artifacts (e.g. LinkedIn analytics exports) — git-ignored
├── autoresearch/       # Third-party autoresearch scratch area — git-ignored
├── resources/
│   ├── models/         # Per-model-family prompt addenda (Anthropic's tested fixes), appended to headless jobs by run_agent.sh; README.md has the rule
│   ├── adapters/       # Provider capability contracts (mail, calendar, files, chat): operations, normalized shapes, implementations (google/eventkit/slack; m365/teams stubs)
│   ├── mcp/            # MCP connection docs (Google Workspace / Gmail + Calendar) — the google implementation's setup
│   └── skills/         # NLAH library — one policy doc per task; scan INDEX.md first
│       ├── INDEX.md    #   registry (name · triggers · description · path), scanned every task
│       ├── README.md   #   the contract: SKILL.md schema, taxonomy, how to add/optimize
│       ├── MODULES.md  #   harness-module vocabulary (the `modules:` key values)
│       ├── _shared/    #   cross-skill modules: evidence gate, delegation-handoff, self-evolution, verifier-separation, change-manifest (+ CHANGE_LOG.md ledger), autoresearch-loop
│       ├── _template/  #   starting point for new skills (SKILL.md)
│       └── <category>/ #   knowledge-graph · research · content · sales · strategy · technology · business-design · vault-hygiene · workflow-ops
│           ├── _category.md       # scope + the category's **Skills:** list
│           └── <skill-slug>/SKILL.md  # the skill (frontmatter + body [+ scripts/ workflows/ references/])
├── .claude/            # Backend — settings.json (hooks: SessionStart injects INDEX + memory + persona; PreToolUse write-guard; Stop control-spine gate, scoped to the session's own runs), hooks/, agents/ (one file per scheduled agent job: model, budget_usd, write_scopes — hook-enforced), settings.local.json
└── cbrain/             # Obsidian Knowledge Vault (the semantic brain) — git-ignored, Obsidian-synced
    ├── Home.md         #   root MOC (progressive-disclosure entry point)
    ├── MOCs/           #   maps of content + generated indexes (e.g. People-Index, Meetings-Index, Pursuits)
    ├── Bases/          #   *.base dashboards (e.g. People, Projects, Sources, Mail, Deliverables, Inputs, Pursuits, Competitors, nlm-*)
    ├── Clients/        #   people (type: person) + accounts (type: account)
    ├── Competitors/    #   standing competitor notes (competitor-intelligence skill)
    ├── notes/          #   meeting notes (YYYYMMDD-Name.md) + Deliverables/ + Inputs/ (generated index notes) + NotebookLM/ + Sources/ + Transcripts/ (Gemini notes, untrusted ingest) + LinkedIn-Posts/ + Dashboards/
    ├── projects/       #   topic/anchor notes (the graph hubs, type: topic)
    ├── Mail/           #   Conversations.md + msgs/ (per-email notes)
    └── daily reports/  #   daily logs (YYYYMMDD.md)
```
