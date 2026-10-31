---
id: account-priority-map
aliases: [account-priority-map]
name: "Account Priority Map (Business Priority Framework)"
category: sales
description: Build and maintain a customer's Mission → Strategy → Initiative → Tactic → Project tree from public sources, tag CXO ownership and KPIs, and flag competitive gaps and opportunity nodes — the account-planning backbone before a pitch or pursuit.
triggers: [business priority framework, BPF, account priority map, customer's mission goals strategies, map their initiatives, account planning tree, who sponsors this initiative, where are the gaps in their strategy, opportunity map for this account]
tags: [sales, account-planning, business-priority-framework, strategy-mapping, executive-sponsorship]
related: ["[[company-challenger-brief]]", "[[pursuit-deal-tracking]]", "[[executive-dialogue-planner]]", "[[competitive-porter-teardown]]"]
modules: [file-backed-state, evidence-backed-answering]
requires:
  tools: [web_search, web_fetch]
status: active
version: 1
created: 2026-07-26
updated: 2026-07-26
vault_writes: ["cbrain/Clients/*", "cbrain/projects/*"]
---

# Account Priority Map (Business Priority Framework)

**Contract**
- **Input:** a named account (company) you're pursuing or account-planning, ideally with a known industry/sector. Optional: an existing `company-challenger-brief` or prior research to reuse instead of re-fetching.
- **Output:** a `## Business Priority Framework` section written into the account's `Clients/<Company>.md` note (create the note if it doesn't exist, per `pursuit-deal-tracking`'s account convention) — the Mission→Strategy→Initiative→Tactic→Project tree, each node in the company's own terminology, with CXO owner + KPI tags on Strategy nodes, and a gaps/opportunity line on every Initiative and Project node. If the account note doesn't yet exist, also save a copy to `output/YYYYMMDD-<Company>-BPF.md` so the deliverable isn't lost while the note is being created.
- **Allowed tools/artifacts:** `web_search`/`web_fetch` against public sources only (annual report, investor site, newsroom/PR, industry commentary); vault file edits.
- **Done when:** the tree covers Mission through at least one full Strategy→Initiative→Tactic→Project chain (ideally all disclosed strategies), every claim is sourced or flagged as inference, and the note is bi-directionally linked per the Living Knowledge Graph rule.

**Triggers/Context**
- Before a pitch, pursuit, or account plan for a company you don't yet have a structural read on — "map their strategy," "where does this initiative sit," "who owns this."
- A `[[company-challenger-brief]]` surfaced good research but the account has no durable Mission→Strategy structure yet captured — this skill is the structural layer on top of that raw research, not a replacement for it.
- An existing account's BPF tree needs a refresh (new annual report, reorg, strategy pivot) — extend the existing section, don't duplicate.

**Core Blueprint**
1. **Reuse before you refetch.** Check for `[[company-challenger-brief]]` output or a `## Business Priority Framework` section already in `Clients/<Company>.md`. Pull the mission/strategy/numbers already gathered rather than re-researching from scratch.
2. **Gather from public sources only, most authoritative first:** annual report / investor deck → official website (`/about`, `/strategy`, `/investors`) → newsroom/PR → industry/analyst commentary. Same source hierarchy as `company-challenger-brief`.
3. **Build the five-level tree, using their words, not a generic template:**
   - **Mission** — one statement or small set of principal goals, quoted or closely paraphrased from their own materials.
   - **Strategy** (2–5 branches) — the approaches to the mission, each tagged with the sponsoring **CXO** (name + title if known, else "unconfirmed — infer from org chart / press") and the **KPI** they're likely measured against (if publicly stated; else flag as inferred).
   - **Initiative** (1–3 per strategy) — measurable steps executing the strategy.
   - **Tactic** (1–2 per initiative) — the tool/method/approach.
   - **Project** (1–2 per tactic) — the concrete piece of work or spend.
   Not every branch will have public detail this deep — stop at whatever level the sources support, and say so rather than inventing lower levels to fill the shape.
4. **On every Initiative and Project node, answer the deck's four questions in one line each:** who sponsors/leads it; how they're doing relative to competitors (if visible); what gap exists; what the opportunity is for us specifically — stated as a hypothesis, not a pitch (Soul.md: never oversell).
5. **Tag confidence per node.** A quoted mission statement or a disclosed KPI is a fact (cite it); an inferred sponsor or an assumed KPI is a bet — label it, per the evidence gate.
6. **Write the tree into the vault**, per `pursuit-deal-tracking`'s account-note convention (extend `Clients/<Company>.md`, don't create a parallel file), and link it to any relevant topic anchor and to the `company-challenger-brief`/`competitive-porter-teardown` deliverables that fed it.
7. **Render the tree as nested markdown** (Mission as H3, Strategy as H4 with a `CXO: … · KPI: …` line, Initiative/Tactic/Project as nested bullets) — legible without needing the original boxes-and-arrows PowerPoint layout.

**Optimizations/Gotchas**
- **This is structural scaffolding, not a fresh research pass.** If `company-challenger-brief` already ran for this account, this skill organizes and extends that research into the Mission→Project shape — don't duplicate the source-gathering step.
- **Use their terminology.** The deck's own instruction: every company names strategy/initiatives differently — force-fitting generic labels (e.g. always calling something a "Strategy" when the company calls it a "Pillar") makes the map harder to recognize in their own room. Keep a parenthetical of their actual term where it differs.
- **Don't force full-depth on every branch.** A strategy with no public initiative-level detail stays a stub with a note on what's missing — inventing plausible-sounding initiatives to fill the tree is a guess dressed as a fact.
- **The "opportunity for us" line is the entire commercial point of the exercise** — an accurate tree with no opportunity annotations is just an org chart. Don't skip it even when the gap is unclear; say "opportunity unclear from public sources, needs a discovery question" rather than leaving it blank.
- **Keep it current.** Reorgs, new annual reports, and strategy pivots date this fast — when the account resurfaces for a new pursuit, check the note's `updated` line before assuming the tree is still accurate.

**Feedback & Skill Verification**
- Would you like to provide feedback to optimize this workflow or execution?
- Should we update this skill (or add a new one) based on how this went?
