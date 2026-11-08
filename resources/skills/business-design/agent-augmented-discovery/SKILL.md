---
id: agent-augmented-discovery
aliases: [agent-augmented-discovery]
name: "Agent-Augmented Discovery — Research Swarms, Synthetic Personas & Red Teams with Guardrails"
category: business-design
description: Run the business designer's discovery and pressure-testing with AI agents — a file-backed desk-research swarm (market, competitors, analogues, trends), synthetic personas used only for objection generation and interview-guide prep, and an adversarial red-team on the chosen business model — with every output tagged `synthetic` or `observed` so agent output sharpens hypotheses but never counts as validation.
triggers: [synthetic personas, synthetic users, AI personas, simulate customers, AI customer interviews, research agents, research swarm, agentic research, desk research with agents, red team the business model, devil's advocate, pressure test with AI, AI-assisted business design, use agents for discovery, speed up discovery with AI]
tags: [business-design, agentic, synthetic-research, desk-research, red-team, guardrails]
related: ["[[business-design-engagement]]", "[[opportunity-framing]]", "[[value-proposition-design]]", "[[business-experiment-design]]", "[[competitive-porter-teardown]]", "[[market-mapping]]", "[[assumption-audit]]", "[[service-discovery-research]]"]
modules: [file-backed-state, file-backed-handoff, evidence-backed-answering, verifier-separation]
status: active
version: 1
created: 2026-10-10
updated: 2026-10-10
requires:
  tools: [web_search, web_fetch]
---

# Agent-Augmented Discovery — Research Swarms, Synthetic Personas & Red Teams with Guardrails

## Contract
- **Input:** an opportunity frame or a business model to pressure-test, plus the questions discovery must answer.
- **Output:** a STATE_ROOT `output/.runs/<YYYYMMDD>-<slug>-discovery/` with one `children/<id>/TASK.md` + `RESPONSE.md` per agent, an `EVIDENCE.md` where every finding is tagged `observed` (cited primary/secondary source) or `synthetic` (persona or model-generated), and a synthesis at `output/<YYYYMMDD>-<slug>-discovery.md`.
- **Allowed tools/artifacts:** Agent tool / headless children per Charter §5, web search and fetch, vault notes. No real customer contact; that belongs to `service-design/service-discovery-research`.
- **Done when:** every child result was reopened from its file; every `observed` finding carries a source URL or document; every `synthetic` finding is labelled as such in the synthesis; the synthesis ends with a list of **hypotheses and interview questions for real people**, not conclusions; and the verifier pass has recorded PASS.

## Triggers/Context
Use to compress the desk-research and preparation part of discovery from weeks to hours, and to attack a business model before a client does. This is the "agentic work" half of the business designer's role: designers direct and validate while agents do the bulk gathering (Valtech's 20-agent sprint pattern). Don't use it to replace talking to customers, and don't use it at all for niche B2B segments where synthetic personas are known to be unreliable.

## Core Blueprint
1. **Write the question set** in the parent STATE_ROOT: 5–10 discovery questions, each tied to a hypothesis id from the opportunity frame or assumption audit.
2. **Desk-research swarm (observed evidence).** Spawn fresh-context children, each with a `TASK.md` naming its scope, the questions, the source-quality rule (primary sources, official data and papers before vendor blogs; no content farms, per Charter §2), and the output schema `finding · source URL · date · confidence`. Typical children: market & segment size; competitor and substitute offers with prices; analogous business models in other industries; regulatory and technology trends. Use `sales/competitive-porter-teardown` for a full competitive teardown instead of a light child.
3. **Synthetic personas (synthetic evidence, narrow use).** Allowed uses: generating objections to a value proposition, drafting and stress-testing interview guides and recruiting screeners, finding gaps in a hypothesis list, rough-sorting weak ideas to kill early. Build personas thin (role, industry, 1–2 pains). Rich invented backstories degrade accuracy. Run at least 5 personas with varied prompts and report the spread, not a consensus. **Forbidden uses:** ranking pains or gains, estimating willingness to pay or adoption rates, validating demand, standing in for B2B or specialized roles as primary research.
4. **Red team.** One fresh-context child receives only the chosen business model and viability model, and the brief "find the three ways this fails and the cheapest evidence that would show it". Its output becomes candidate hypotheses for `strategy/assumption-audit`.
5. **Reopen and integrate.** The parent reopens each `children/<id>/RESPONSE.md` (never the inline reply), merges findings into `EVIDENCE.md` with tags, and resolves contradictions explicitly.
6. **Verifier pass (separate step).** Sample at least 5 `observed` findings and re-fetch their sources: does the source say what the finding claims? Any mismatch downgrades the finding to `unverified` and is counted. Record `Verifier: PASS | FAIL (n mismatches)`.
7. **Synthesize to questions, not answers.** The synthesis lists what desk evidence supports, what synthetic runs suggest (labelled), and the interview questions and experiments that real people must answer next (handed to `service-design/service-discovery-research` and `business-experiment-design`).

## Output Format
```markdown
# Agent-Augmented Discovery — <scope> (<date>)
## Questions → hypotheses (ids)
## Observed findings (finding · source · date · confidence)
## Synthetic findings — NOT evidence (persona set · prompt variants · spread of responses)
## Red-team: three ways this fails
## Contradictions & how resolved
## Next: questions for real customers · experiments to run
Verifier: PASS — <n> findings re-checked
```

## Optimizations/Gotchas
- **Synthetic respondents skew positive, more homogeneous, and less varied than real people.** In a 2026 benchmark the best simulator covered under half of real consumer reactions (ConsumerSimBench, 47.8%). Treat agreement among personas as an artefact, not a signal.
- **Confirmation bias runs faster with agents.** Asking personas to validate your idea gets you validation. Prompt for objections and failure modes only.
- **B2B and niche segments: no synthetic primary research.** Training data on specialized roles is patchy (NN/g, Kromatic). Use personas for guide prep only.
- **Agents fabricate citations.** That's why the verifier re-fetches sources: a finding without a fetchable source is `unverified`, not `observed`.
- **Confidentiality.** Never put client-confidential data into third-party synthetic-persona tools. Run inside approved environments only (Soul.md inviolable).
- **Budget.** Declare the cap up front (default: ≤6 children, ≤20 searches per child, 1 red-team pass) and report when it's hit.

## Sources
Kromatic, "Can Synthetic Personas Replace Customer Discovery?" (allowed and forbidden uses; positivity and variance skew); personia.ai summary of 2026 validation studies (ConsumerSimBench 47.8%); AAAI AIES "Whose Personae? Synthetic Persona Experiments in LLM Research" (review of 63 studies); Valtech Design, "20 AI Agents, 1 Design Sprint" (humans direct and validate, agents execute). See [Sources](../_category.md).
