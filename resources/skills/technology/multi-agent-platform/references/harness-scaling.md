# Harness scaling — personal → team → company (and "harness as a service")

Use when someone has a harness that works for them personally and asks what it takes to make it work for a team or a company. Dated 2026-11-01. Re-verify vendor features before advising.

## Diagnose the single-user couplings first
A personal harness usually works because one person is the whole security model. Look for these:

| Coupling | Typical evidence |
|---|---|
| One persona, one memory, one knowledge vault | identity file, memory dir and vault all local and owned by one person |
| One machine is the runtime | scheduled jobs on a laptop (launchd/cron); closed lid = nothing runs |
| Personal subscription as the model account | the CLI is forced onto a consumer login; consumer plans are for individuals, not for serving others |
| No login on the UI | a local console that assumes its only user is the owner |
| Guardrails are local scripts | hooks anyone with the repo can edit or remove |
| Human judgment as the control | "the owner confirms", send approvals, memory-write prompts all assume one principal |

The policy layer (charter, skills, provenance labels, write scopes, regression suite, disclosure card) usually transfers as is. That layer is the asset; the couplings above are plumbing.

## Level 1 — team harness (3–15 people): package, don't host
1. **Split into three layers:**
   - **shared and versioned:** charter, voice, skills, hooks, agent definitions;
   - **per person:** identity, memory, own notes;
   - **shared state:** a team knowledge base with access control. An employer-pack or tenant-pack pattern generalises per person.
2. **Distribute as a plugin through a team marketplace**, not as forks. Forks drift.
3. **Use team seats or API keys** with a spend cap per person, replacing personal subscriptions.
4. **Name a skill owner.** Skill changes go through PRs, with the regression suite as a CI gate, and the change-manifest becomes a review step.
5. **Give shared knowledge permissions.** One vault for everyone breaks confidentiality between clients. Use per-person vaults plus a shared layer per engagement.

Scheduled jobs can stay on each person's machine at this level.

## Level 2 — company setup: a control plane, mostly bought
| Service | Why | Build/buy |
|---|---|---|
| SSO + one identity per agent | who did what: a person, or a job on their behalf | buy (corporate IdP) |
| Model gateway | cost per team and client, quotas, routing, model swap | buy / open source |
| Centrally managed policy | hooks and permissions users can't switch off (managed settings) | configure |
| Hosted runtime for scheduled jobs | team-serving jobs can't depend on one laptop | buy (managed agent runtime) |
| Audit log + telemetry | central OTel collector | buy |
| Eval and release pipeline | one skill or model change reaches everyone, so pass^k runs before rollout | build (exists) |
| Agent registry | owner, write scopes, risk class per agent | build, small |
| Research firewall in code | untrusted input never triggers a decision | build (exists) |

**Germany / Austria:** per-user telemetry (token ledgers, run forensics, files written per run) is a system suited to monitoring performance. In Germany that triggers works-council co-determination under BetrVG §87(1) No. 6; Austria has comparable rules under ArbVG. Plan the works agreement from the start, plus a DPIA for anything that ingests mail or chat.

## "Harness as a service" means two different things
- **Hosted runtime:** agents run server-side; people use them through a UI or chat. Needed **only for jobs that serve a team**. Interactive work stays in each person's agent client with the shared plugin. Buy it; don't build it.
- **Product:** selling the policy layer (policy as files, provenance, write scopes, evals, conformance card). The infrastructure is a commodity: *buy the commodity, build the differentiator.* Clear employment IP and side-job clauses before anyone outside sees it.

**One line:** personal = a repo · team = a plugin + seats + a shared knowledge layer with permissions · company = the same plugin governed by a control plane you mostly buy.
