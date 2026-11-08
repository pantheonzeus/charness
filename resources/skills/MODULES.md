# Module Vocabulary

Named, reusable harness modules a `SKILL.md` can declare via the optional `modules:` frontmatter key. Naming modules explicitly is what turns the library from a pile of prose into an *analyzable* harness — you can see which skills use which mechanism, turn one on or off, and judge its contribution.

*Grounded in the module ablation of the NLAH research (Pan et al., [arXiv:2603.25723](https://arxiv.org/abs/2603.25723), RQ3 / App. F). The one durable lesson: a module helps only when it **shortens the path from intermediate work to auditable evidence and final acceptance**. Modules that add branching, process layers, or lossy summaries do not — and several measurably hurt.*

## How to use
Add to a skill's frontmatter the modules it actually relies on:
```yaml
modules: [file-backed-state, evidence-backed-answering, verifier-separation]
```
This is documentation and analysis metadata, not an import — the behavior lives in the skill body and the `_shared/` docs. Declare only what the skill genuinely uses.

## The modules (use — measured positive)
| Module | What it means | Where the mechanism lives |
|---|---|---|
| `file-backed-state` | Durable path-addressable run state (`STATE_ROOT`, control spine, reopened by path). The most reliable module. | Charter §4 |
| `evidence-backed-answering` | Provenance-tagged claims + a release gate on unsupported ones, **plus an inbound register-recall step before drafting** (grep the run register for every entity the deliverable touches — mandatory for scope answers). | [`_shared/evidence-gate.md`](_shared/evidence-gate.md) |
| `verifier-separation` | A distinct checking step that judges a candidate against the acceptance criterion (best when it stays *close* to that criterion — e.g. `link_audit`, `completeness_gate`). | [`_shared/verifier-separation.md`](_shared/verifier-separation.md) + skill `scripts/` |
| `self-evolution` | Within-run reflect → redesign → retry loop with a cap and honest stop. Strongest on the solve loop. | [`_shared/self-evolution.md`](_shared/self-evolution.md) |
| `file-backed-handoff` | Delegation via task-packet files and reopened result files, not inline replies. | Charter §5, [`_shared/delegation-handoff.md`](_shared/delegation-handoff.md) |
| `dynamic-orchestration` | Add child agents only when delegation materially helps; smallest adequate topology. Real but modest gains. | Charter §5 |

## Anti-patterns (the research measured these as neutral-to-harmful)
| Anti-pattern | Finding | Guidance |
|---|---|---|
| `context-compression` | Hurt both benchmarks (worst: −8.3). Aggressive summarization drops action-critical detail. | Externalize to a file *before* compacting; recover by path. Never compress away acceptance criteria, error signatures, or handoff state. |
| `multi-candidate-search` | ~5× the agent calls for a *drop* on one benchmark. | Prefer the sequential `self-evolution` loop over parallel K-candidate branching unless a skill has a specific reason. |
| free-form markdown memory | Mixed results; a transcript-style dumping ground drifts from truth. | Keep memory one-fact-per-file and source-grounded (as the memory dir already is), not a running log. |

## Adopted from other harness research — not yet internally measured
Distinct from the table above: this mechanism was adopted on the strength of *another* team's published ablation, not (yet) validated by a before/after read on this repo. Treat the cited number as evidence about their system, not a claim about ours, until we have our own.

| Module | What it means | Where the mechanism lives | Source |
|---|---|---|---|
| `decision-observability` | Change-manifest: every Charter/`_shared`/skill-Blueprint edit gets a logged prediction (what it fixes, what it risks), checked against the next real use. A weekly verdict sweep turns pending entries into a READY worklist. | [`_shared/change-manifest.md`](_shared/change-manifest.md) + `_shared/scripts/verdict_sweep.py` | AHE (Lin et al., arXiv:2604.25850) — self-attributed fix-precision 33.7%, fix-recall 51.4%, ~5x random-guessing baselines. |

## Derived from internal post-mortem — not measured
Distinct from both tables above: this contract was written from this repo's own failures, not from a published ablation, and no before/after read exists yet.

| Module | What it means | Where the mechanism lives | Source |
|---|---|---|---|
| `autoresearch-loop` | Between-run optimization loop on a skill, script, config, or vault structure (modify → verify → keep/discard, bounded). Requires a loop card before iteration 0: a mechanical metric close to the acceptance criterion, a frozen eval set, and a guard metric. Exits into `CHANGE_LOG.md`. An LLM judge may serve as a guard, never as the sole metric. | [`_shared/autoresearch-loop.md`](_shared/autoresearch-loop.md) + the bundled `autoresearch` skill | Post-mortem `output/20261009-autoresearch-loop-map.md`: four July runs converged on judge or self-designed rubrics (95–96), and a composite-98.5 draft reached 288 impressions vs. a 1,078 archive mean. Rule basis: NLAH F.1. |

## Currently declared
- `vault-hygiene/skill-library-maintenance` — `autoresearch-loop` (frontmatter lint fix-loop; routing eval on INDEX triggers, 42 real prompts, train/held-out split).
- `vault-hygiene/progressive-disclosure` — `autoresearch-loop` (recall benchmark as the standing guard, not a target).
- `vault-hygiene/vault-maintenance` — `autoresearch-loop` (weekly ratchet: missing targets by category, recall-gated, no auto-fix).
- `vault-hygiene/memory-consolidation` — `file-backed-state` (base/proposed/backup copies in a STATE_ROOT, hash-checked before apply), `verifier-separation` (`memory_dream.py check` judges coverage, preservation and faithfulness, not the consolidator).
- `sales/audience-of-one-report` — `file-backed-state`, `evidence-backed-answering`, `verifier-separation`, `self-evolution` (the maximal worked example of the full stack).
- `sales/competitive-porter-teardown` — `file-backed-state`, `file-backed-handoff`, `evidence-backed-answering` (per-BU fan-out via task-packet files, evidence-gated synthesis).
- `content/linkedin-comment-engagement` — `evidence-backed-answering`.
- `content/linkedin-repost-evaluator` — `evidence-backed-answering`.
- `workflow-ops/linkedin-viral-scheduler` — `file-backed-state`, `evidence-backed-answering`, `file-backed-handoff`, `self-evolution`, `verifier-separation`.
- `workflow-ops/linkedin-scoring-calibration` — `file-backed-state`, `evidence-backed-answering`, `file-backed-handoff`, `verifier-separation`, `autoresearch-loop` (one-knob calibration on train agreement, held-out overfit guard, file-snapshot revert; no weight tuning below n≈40).
- `sales/pursuit-deal-tracking` — `file-backed-state` (one durable `Clients/` anchor per pursuit, reopened on every stage change rather than re-created).
- `sales/competitor-intelligence` — `evidence-backed-answering` (every promoted claim keeps its source dossier's provenance tag).
- `sales/account-priority-map` — `file-backed-state` (the BPF tree lives as a durable section on the account's `Clients/` note, reopened and extended on refresh), `evidence-backed-answering` (every Mission/Strategy/KPI node is cited or flagged as inferred).
- `content/linkedin-video-script` — `evidence-backed-answering`.
- `content/speaker-submission` — `evidence-backed-answering`, `file-backed-state`.
- `content/linkedin-profile-headhunter` — `file-backed-handoff` (playbook-query sub-agent via `children/playbook-refresh/`).
- `sales/rfp-clarification-reconciliation` — `file-backed-state`, `evidence-backed-answering`.
- `workflow-ops/campaign-week` — `file-backed-state`.
- `workflow-ops/career-campaign-review` — `file-backed-state`, `evidence-backed-answering`.
- `workflow-ops/linkedin-weekly-review` — `file-backed-state`, `evidence-backed-answering`.
- `workflow-ops/notebooklm-daily-audio` — `file-backed-handoff` (headless distill; wrapper reopens `children/distill/RESPONSE.md`).
- `workflow-ops/morning-briefing` — `file-backed-handoff` (headless build; wrapper reopens `children/build/RESPONSE.md`).
- `workflow-ops/mail-to-conversations` — `file-backed-handoff` (bulk-fetch subagent via `children/fetch/`).
- `business-design/{business-design-engagement}` — `file-backed-state`, `evidence-backed-answering` (phase spine with gate verdicts in a STATE_ROOT); `business-design/{viability-model}` — `evidence-backed-answering`, `verifier-separation` (Python recompute pass); `business-design/{business-experiment-design}` — `file-backed-state`, `evidence-backed-answering` (hypothesis board reopened by path); `business-design/{agent-augmented-discovery}` — `file-backed-state`, `file-backed-handoff`, `evidence-backed-answering`, `verifier-separation` (child research packets, observed/synthetic tags, source re-fetch); the other 7 business-design skills — `evidence-backed-answering`.
- `strategy/{situation-assessment, growth-barriers, assumption-audit, market-mapping, competitive-intel, pricing-strategy, business-case-builder, decision-memo, risk-and-mitigation, strategic-options}` — `evidence-backed-answering` (each has a structural Evidence/Confidence/Assumption-Strength column in its Output Format table; the other 11 strategy skills are pure structuring/design frameworks with no such column and were left undeclared rather than force-tagged).
- `service-design/{service-design-engagement, service-discovery-research, service-concept-prototyping}` — `file-backed-state`, `evidence-backed-answering`; `service-blueprint`, `agentic-service-blueprint`, `agentic-service-evaluation` add `verifier-separation` (done-when re-check with ≤2 revisions); `agent-ready-service` — `evidence-backed-answering`, `verifier-separation`; `journey-mapping`, `service-ecosystem-mapping`, `service-performance-measurement` — `evidence-backed-answering` (every pain point, exchange or number is cited or tagged assumed); `service-codesign-facilitation` undeclared.
- `technology/{data-migration-strategy, migration-reconciliation}` — `file-backed-state`, `evidence-backed-answering`, `verifier-separation` (tier scorecard cites evidence per dimension; `reconcile.py` is an exit-code verifier, re-run by a non-builder in T3+); `data-mapping-and-quality` — `file-backed-state`, `evidence-backed-answering` (value maps must cite profiled values); `migration-cutover-runbook` — `file-backed-state`, `verifier-separation` (runbook checked against measured mock timings).
- `technology/app-architecture` — `file-backed-state`, `evidence-backed-answering`, `verifier-separation` (STATE_ROOT spine over the 10 Blueprint steps, every repo measurement and framework/regulatory claim cited or tagged [I], done-when re-check with ≤2 revisions).
