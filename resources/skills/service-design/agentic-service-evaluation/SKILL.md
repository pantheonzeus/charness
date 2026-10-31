---
id: agentic-service-evaluation
aliases: [agentic-service-evaluation]
name: "Agentic Service Evaluation — Eval Suite, Staged Rollout & Operating Scorecard"
category: service-design
description: Proves that an agentic service is safe to scale, and keeps it that way. It builds an eval suite from journey scenarios, real cases and Wizard-of-Oz transcripts (including edge, adversarial and vulnerable-customer cases), grades outcome, policy, handoff and tone with calibrated human graders, and runs a staged rollout (offline → shadow → assisted → gated autonomy) with promotion criteria written before each stage. Live operation is covered by an operating scorecard, drift monitoring and an incident review.
triggers: [evaluate the AI agent, agent evals, eval set for agent, is the agent ready, shadow mode, staged rollout agent, promote autonomy, agent quality monitoring, agent incident, agent drift, golden dataset service, LLM judge, red team the agent, agent go-live criteria, agent KPIs]
tags: [service-design, agentic, evaluation, rollout, quality, governance]
related: ["[[agentic-service-blueprint]]", "[[service-concept-prototyping]]", "[[service-performance-measurement]]", "[[agent-ready-service]]", "[[risk-and-mitigation]]", "[[agent-architecture]]"]
modules: [file-backed-state, evidence-backed-answering, verifier-separation]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
references: [../agentic-service-blueprint/references/agentic-patterns.md]
---

# Agentic Service Evaluation — Eval Suite, Staged Rollout & Operating Scorecard

## Contract
- **Input:** the agentic blueprint (autonomy register, handoff specs, failure modes), real or Wizard-of-Oz cases, and access to the agent (or its spec, for design-time work).
- **Output:** `output/<YYYYMMDD>-<slug>-agent-eval-plan.md` containing (a) the eval suite spec and case mix, (b) the grading rubric and grader-calibration result, (c) rollout stages with pre-registered promotion and rollback criteria, (d) the operating scorecard, (e) the incident and change-control procedure. Eval cases live in `STATE_ROOT/evals/cases.tsv`, results in `STATE_ROOT/evals/results-<date>.tsv`.
- **Allowed tools/artifacts:** conversation, case data (pseudonymised), the agent under test in a non-production environment, scripted runs.
- **Done when:** the case mix covers every intent in the autonomy register, plus edge, adversarial and vulnerable-customer slices; each rollout stage has promotion **and** rollback criteria written before the stage starts; human graders agree with each other at or above a stated threshold before their grades are used; the scorecard uses resolution and re-contact, not containment; incident ownership is named.

## Operating principles (enforceable)
1. **Evals come from the service, not the model.** Cases are built from journey scenarios, blueprint fail points, real transcripts and WoZ sessions. Generic benchmarks say nothing about your refunds policy.
2. **Grade the outcome, not the prose.** The primary grade is whether the right thing happened (correct resolution, correct action, correct handoff). Tone and style are secondary.
3. **Humans set the truth; judges scale it.** An LLM judge may grade at scale only after it has been calibrated against human grades on a held-out sample. It is never the sole metric for a promotion decision (house rule, `_shared/autoresearch-loop.md`).
4. **Pre-register every gate.** Promotion, rollback and stop criteria are written before the stage starts. A gate moved after the data came in is a rationalised gate.
5. **Slice before you average.** Report results per intent, per risk class and per segment (language, vulnerability, channel). A 95% average can hide a 60% slice that harms a group.
6. **Autonomy is promoted one level at a time.** Each step up the autonomy register (L2→L3→L4) needs its own evidence. It never jumps.
7. **Any change re-runs the suite.** Model, prompt, tool or policy changes go through regression on the frozen suite before release.

## Core Blueprint
1. **Case mix.** Per intent: typical cases (from volume), edge cases (from fail points), handoff-required cases, adversarial cases (prompt injection, social engineering, out-of-scope), and vulnerable-customer cases. Freeze a **held-out** slice that's never used for tuning. Aim for ≥30 cases per high-volume intent at launch and grow the suite from production incidents.
2. **Rubric.** Score: outcome correct (pass/fail) · policy compliance (pass/fail, with the policy cited) · handoff decision correct (escalated when it should have, didn't when it shouldn't) · handoff packet complete · factual grounding · tone (1–3). Severity-weight the failures: one critical policy breach outweighs many tone points.
3. **Calibrate graders.** Two humans grade the same 30+ cases. Compute agreement and align on the disagreements. Calibrate any LLM judge against the aligned human grades and record its agreement rate.
4. **Offline eval.** Run the suite and report per slice. Fix and re-run, capped at the run's attempt budget (default 5, per `_shared/self-evolution.md`), then report honestly.
5. **Shadow mode.** The agent runs on live traffic without acting while humans handle the cases. Compare agent proposals with human outcomes. Promotion needs the pre-registered match rate on each slice.
6. **Assisted (L2–L3).** Humans see the agent's proposal and decide. Track override rate and reasons; overrides are the richest source of new cases.
7. **Gated autonomy (L4).** The agent acts and humans approve gated actions. Track the approval time distribution (watch for rubber-stamping), error-reversal rate and re-contact.
8. **Operating scorecard.** Verified resolution, re-contact within N days, handoff rate and handoff quality, critical policy breaches (target 0, with alerting), cost per resolved case including review, complaint themes, and slice parity. Review weekly with the accountable owner from the autonomy register.
9. **Incidents and change control.** Define severity levels, an owner, and a kill-switch decision right (who can stop the agent, and how fast). Run a post-incident review that adds the case to the suite. Every model or prompt change goes through regression first.

## Output structure
```markdown
## Scope                 (agentic blueprint ref · intents · autonomy targets)
## Case mix              | Intent | Typical | Edge | Handoff | Adversarial | Vulnerable | Held-out |
## Rubric & calibration  criteria · severity weights · human agreement % · judge agreement %
## Rollout gates         | Stage | Entry | Promotion criteria | Rollback trigger | Duration | Decider |
## Operating scorecard   | Measure | Definition | Target/threshold | Alert | Owner | Cadence |
## Incidents & change control
```

## Optimizations/Gotchas
- **Containment is the metric vendors love and customers hate.** It counts abandonment as success. Use verified resolution.
- **Shadow mode is cheap insurance.** Weeks of shadow data on real traffic beat months of synthetic eval tuning. Don't skip it to hit a launch date.
- **Your eval set rots.** The case mix shifts as the service, policies and customers change. Refresh it quarterly from production, and keep the frozen held-out slice for trend comparison.
- **Treat a 100% score as a smell.** It usually means the cases leaked into the prompt or the set is too easy. Add harder cases from recent overrides.
