---
template: home.html
title: The governed agent harness for Claude Code
hide: [navigation, toc]
---

<div class="cx-section" markdown>

<p class="cx-kicker">Why a harness</p>

## The model is one field out of eight.

A harness disclosure card ([He et al.](governance/harnesscard.md)) asks eight questions about an agent system, and the base model answers only one of them. The other seven are the harness: the control documents, the runtime policy, the tools, the topology, the feedback loops, the governance and the evaluation. Those seven decide whether an agent can be trusted with your mail, your knowledge base and your clients' names.

charness answers all eight in the open, and enforces the answers in code.

</div>

<div class="cx-section" markdown>

<p class="cx-kicker">How it is built</p>

## Policy separated from mechanism

<div class="cx-stack" markdown>

<div class="cx-layer" markdown>
**Skill library** <span>changes often</span>

{{ skills_count }} task policies, one Markdown file each. The agent matches the task, opens one skill and follows its contract. [Skills →](concepts/skills.md)
</div>

<div class="cx-layer" markdown>
**Identity** <span>yours</span>

Voice mechanics and inviolable lines in `Soul.md`. Your role and beliefs go in a private `IDENTITY.md`. [Make it yours →](get-started/make-it-yours.md)
</div>

<div class="cx-layer" markdown>
**Runtime Charter** <span>changes rarely</span>

How every run executes: verify before you deny, file-backed state, evidence gates, delegation by file. [Charter →](reference/charter.md)
</div>

<div class="cx-layer cx-layer--code" markdown>
**Backend** <span>deterministic code</span>

Hooks and scripts that enforce the documents above, whatever the model decides. [Guardrails →](governance/guardrails.md)
</div>

</div>

The documents carry the policy. The code makes sure the policy holds. [Architecture →](concepts/architecture.md)

</div>

<div class="cx-section" markdown>

<p class="cx-kicker">What it stops</p>

## Guardrails in code, not in prompts

<div class="cx-grid" markdown>

<div class="cx-card" markdown>
:material-folder-lock-outline:{ .cx-icon }
### Writes outside the lane
A scheduled job may write only inside the `write_scopes` its agent file declares. A hook denies everything else, with symlinks resolved.
</div>

<div class="cx-card" markdown>
:material-earth-off:{ .cx-icon }
### Data leaving in a web call
A web search or fetch is denied if it carries an email address, an encoded blob or an oversized query.
</div>

<div class="cx-card" markdown>
:material-send-lock-outline:{ .cx-icon }
### Sends you didn't approve
No mail or chat message leaves without your explicit yes and a clean confidentiality scan. This gate fails closed.
</div>

<div class="cx-card" markdown>
:material-shield-alert-outline:{ .cx-icon }
### Injected instructions
Text from outside the system is labelled untrusted, and the label stays on when an agent rewrites it. It stays data, never an instruction.
</div>

<div class="cx-card" markdown>
:material-source-commit:{ .cx-icon }
### Secrets in git
Git hooks block secrets, personal data, client names, ignored files and force pushes. CI runs the same scan again.
</div>

<div class="cx-card" markdown>
:material-checkbox-marked-circle-outline:{ .cx-icon }
### Runs that quit early
A run cannot stop while its control spine still has open checkpoints.
</div>

</div>

[See every guardrail, what it checks and how it is tested →](governance/guardrails.md)

</div>

<div class="cx-section" markdown>

<div class="cx-stats" markdown>
<div><strong>{{ skills_count }}</strong><span>skills in {{ categories_count }} categories</span></div>
<div><strong>{{ jobs_count }}</strong><span>headless jobs, each with a pinned model, a budget and write scopes</span></div>
<div><strong>{{ hook_suites_count }}</strong><span>hook test suites run in CI on every push</span></div>
<div><strong>8 / 8</strong><span>HarnessCard fields answered in the repo</span></div>
</div>

</div>

<div class="cx-section" markdown>

<p class="cx-kicker">Built on research</p>

## Credit where it is due

- **Natural-Language Agent Harnesses.** Pan, Zou, Guo, Ni & Zheng, [arXiv:2603.25723](https://arxiv.org/abs/2603.25723). It is the source of the idea that harness policy belongs in editable natural-language documents run by an intelligent runtime. charness is a working implementation of that idea.
- **Harness Engineering for Language Agents.** He et al., the Control–Agency–Runtime disclosure card. charness publishes [its own card](governance/harnesscard.md).
- **Agent Skills.** Progressive disclosure: the agent reads a cheap index first, opens the full skill only on a match and loads deep material only when needed.

Where a Charter rule comes from a paper, the Charter cites it next to the rule. [Read the Charter →](reference/charter.md)

</div>

<div class="cx-section" markdown>

<p class="cx-kicker">Honest scope</p>

## What it is, and what it isn't yet

- **It is** a working harness, used every day. It runs scheduled briefings, mail triage, meeting prep and research loops under launchd.
- **It runs on macOS** (launchd, Calendar.app) with [Claude Code](https://claude.com/claude-code), on your Claude subscription.
- **It measures harness behaviour**: a regression suite at pass^3, routing recall and hook tests. It does not yet grade the quality of what it writes. [Evaluation →](governance/evaluation.md)
- **It isn't a product.** It is a configuration you fork and make your own.

</div>

<div class="cx-section cx-final" markdown>

## Four lines to a governed agent

```bash
git clone https://github.com/pantheonzeus/charness.git && cd charness
cp IDENTITY.example.md IDENTITY.md   # make the persona yours
scripts/check.sh                     # every test and lint, under a minute
claude                               # CLAUDE.md loads the harness
```

[Get started](get-started/quickstart.md){ .md-button .md-button--primary } [Browse the skills](reference/skills.md){ .md-button }

</div>
