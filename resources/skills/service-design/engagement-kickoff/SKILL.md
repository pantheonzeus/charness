---
id: engagement-kickoff
aliases: [engagement-kickoff, sprint-kickoff, kickoff-week]
name: "Engagement Kick-off — Prep Week, Decision Rhythm, Sponsor Timeline & Nugget Library"
category: service-design
description: Turn a won proposal into a delivery start that shows momentum from day one. Settle the contradictions before day 1, define "amazed" as observable criteria for the final decision, run a week-0 team onboarding, and plan a day-by-day first week on a Mon/Wed/Fri decision rhythm with planned wow moments. Write a 2–3-day timeline the sponsor can forward, map stakeholders from the org chart, and build a library of cited insights (one per session, each tied to a decision), plus a team playbook HTML.
triggers: [kick-off plan, kickoff plan, kickoff week, onboarding week, plan the first week, prep week, sprint plan for the client, timeline for the sponsor, update for senior management, rough timeline, every 2-3 days, we start the project, project start, wow the client, impress the client, first two weeks, plan the sprint, sprint kickoff, nuggets to inspire]
tags: [service-design, kickoff, delivery, sprint, facilitation, stakeholders, sponsor]
related: ["[[service-design-engagement]]", "[[service-codesign-facilitation]]", "[[stakeholder-alignment]]", "[[team-onboarding-kit]]", "[[agentic-service-blueprint]]", "[[client-follow-through]]"]
status: active
version: 1
created: 2026-11-01
updated: 2026-11-01
modules: [file-backed-state, evidence-backed-answering]
---

# Engagement Kick-off

> The client decides in the first 48 hours whether they bought a partner or a vendor. Plan those hours.

**Contract**
- **Input:** the signed or agreed proposal, the client's brief and mails, meeting notes, staffing, dates, and, if available, the client's org chart and intranet pages on the scope area. The client name comes from the prompt.
- **Output:**
  - `output/<YYYYMMDD>-<slug>-kickoff-plan.md`;
  - an interactive team playbook `output/<YYYYMMDD>-<slug>-sprint-playbook.html` (local file, not a hosted page);
  - both indexed per Charter §4.

  Run state goes in `output/.runs/<YYYYMMDD>-<slug>-kickoff/`, with `RESPONSE.md` and `EVIDENCE.md`.
- **Allowed tools/artifacts:** the vault (harvest the account, people and prior streams first), the client material provided, web search for the nugget library, the evidence gate.
- **Done when:**
  - every contradiction between proposal, mails and staffing is listed as a decision with an owner and date;
  - the final decision has observable success criteria;
  - every decision session names the written decision it ends with;
  - the sponsor timeline carries no uncited number;
  - every nugget has a source, an evidence tag and a session.

**Triggers/Context**
- A proposal was accepted and the first days of delivery need planning. The sponsor asks for "a rough timeline I can share upward". The team wants to "shine" and "drive" the client.
- Before the sale use `service-design-engagement` (framing, phases, gates). Use `service-codesign-facilitation` for the design of a single session. Use `team-onboarding-kit` to get the own team up to speed.

**Core Blueprint**
1. **Harvest and list the contradictions.** Read the proposal versions, the client's latest mail, meeting notes, staffing and calendar. Look for duration, team line-up, scope (what the client does itself), NDA status, and tool and data rules (the client's AI or IT policy). Each conflict goes into §0 of the plan, "Settle before day 1", with an owner and a date. Staffing changes after the sale are a named risk, because the client was sold specific people.
2. **Define "amazed" as observable criteria for the final decision**, 5–6 of them. For example:
   - a decision-maker says go/no-go in the room;
   - every session ended with a written decision;
   - the concept was tested on a real case;
   - the sponsor forwarded our update unedited;
   - one baseline number exists.
3. **Week 0 (own team).** Pre-read; drafts for the client to react to on day 1 (never a blank page: success criteria, hypothesis, a lifecycle or process frame, templates); an access list; NDA; interview guides; a kick-off dry run with timings.
4. **Week 1, day by day.** A Mon focus / Wed co-create / Fri decide rhythm, 90 minutes each, each ending with a written decision in a live decision log in the client's tenant. Plan three wow moments:
   - **speed:** the client's own material consolidated onto one page within 48 hours;
   - **reality:** walkthroughs of 2 real, recent cases from intake to delivery;
   - **communication:** a Friday one-pager the sponsor can forward.

   Ask early for one baseline number from the client's process data.
5. **Week 2 (or the rest of the sprint):** design, a zero-build test (Wizard-of-Oz or role-play on a real request), then decide. Book the decision-maker for the final session on day 1.
6. **Sponsor timeline.** Four blocks of 2–3 days, each with a plain-language goal and a dated output, marked provisional and adjusted after the checkpoint. Paste-ready, no numbers that need citing.
7. **Stakeholder map** from the org chart. Group people by sprint role: sponsor, likely decision-maker, product owner, operational owner of the process that must change, specialist owners to interview, foundation and guardrail owners, baseline data owner, users for walkthroughs. Mark every role "inferred from title — confirm with the PO".
8. **Nugget library.** 8–10 insights, each with a fact, its source and an evidence tag ([D] primary, [S] secondary, [I] inference); a "so for <client> this means…" line; and the session where it's used. At most one per session and three minutes. Run the evidence gate on every number, then add risks (NDA, tool policy, unfinished client inputs, interviewees not booked, scope pull, decision-maker absent, staffing churn).
9. **Build the playbook HTML.** Tabs: Plan (decisions to settle, success criteria, wow moves, rhythm) · Day by day (click a day to see goal, tasks with owners, written decision, nugget) · Sponsor timeline (copy button) · People (filter + search) · Nuggets (cards that reveal the so-what) · Concepts (optional) · Risks. Checkboxes persist in localStorage; light/dark theme. Single file, no external dependencies.

**Optimizations/Gotchas**
- **Client data is confidential by default.** Org charts, intranet pages and inventory lists stay in `output/` and local files. No hosted pages; no third-party AI tools unless the client's own policy and an NDA allow them. If the client's AI policy limits tools to approved ones, the team works in the client's tenant with sample data.
- **Don't pitch the principal's own IP inside client work** (a personal harness, a venture's design) until the IP and side-job questions are cleared. Use neutral wording or the client's own test as proof.
- **Scope creep in both directions:** the pull toward building the MVP, and the pull toward pure architecture. Point back to the client's own phase slide.
- **The sponsor's "senior management is interested" means they need forwardable material, not more meetings.** The Friday one-pager does more than any extra session.
- **Nuggets are judged by the decision they make easier, not by how novel they are.** A forecast stays labelled as one; vendor GA dates come from vendor docs.
- **Persona lens:** open with why it matters and the outcome, then the experience, then the technology. Every session ends in a decision, or it was a meeting.
