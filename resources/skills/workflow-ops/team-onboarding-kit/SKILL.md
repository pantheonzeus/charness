---
id: team-onboarding-kit
aliases: [team-onboarding-kit, onboarding-kit]
name: "Team Onboarding Kit — Role-Tailored NotebookLM Media → Personal Learning Pages"
category: workflow-ops
description: Turn an engagement's sources into a private, role-tailored onboarding package for each team member. Person profiles feed a scoped NotebookLM notebook; studio artifacts are prompted per role (podcasts, videos, infographics, quizzes, flashcards), checked visually, then built into one offline HTML page per person. Each page leads with a short core path (about 30 minutes of media a week for anyone but the lead, one priority task a day, a plain-language glossary of the terms outside their craft), their job on each sprint day, a short quiz and readiness check; everything else sits in an optional Go deeper tab.
triggers: [onboarding kit, onboard my team, team onboarding, get the team up to speed, up to speed, learning package, onboarding material, onboarding package, podcasts for the team, personal learning path, ramp-up plan, enablement pack, notebooklm for the team, quiz for the team, tailored onboarding]
tags: [workflow-ops, onboarding, notebooklm, learning, team, podcasts, html]
related: ["[[notebooklm]]", "[[engagement-kickoff]]", "[[service-design-engagement]]", "[[reading-pages]]"]
status: active
version: 2
created: 2026-11-01
updated: 2026-11-02
modules: [file-backed-state, verifier-separation]
requires:
  cli: ["nlm (notebooklm-mcp-cli)"]
  optional: ["playwright (browser test; the notebooklm-py tool venv has it)", "afinfo (macOS, media durations)"]
scripts: [scripts/create_artifacts.py, scripts/fetch_media.py, scripts/build_kit.py, scripts/template.html, scripts/kit.example.py]
references: [references/prompt-library.md]
---

# Team Onboarding Kit

> Everyone starts from their own craft. The material meets them there, not at the technology. Make the minimum that gets them ahead of expectations on day 1, not everything you could make.

**Contract**
- **Input:** the team (name, role, craft, what they already know, what they own, minutes per day), the engagement plan or proposal, the concepts to learn, the prep-week and sprint dates. Client and person names come from the prompt, never from this skill.
- **Output:**
  - a NotebookLM notebook on the **work** account;
  - `output/<YYYYMMDD>-<slug>-onboarding-kit/` with `onboarding-<person>.html` per person, `media/`, `README.txt`, and the shared playbook if there is one;
  - a kit guide `output/<YYYYMMDD>-<slug>-team-onboarding-kit.md` (paths per person, media table, how the prompts were built, known limitations), indexed per Charter §4.

  Run state lives at `output/.runs/<YYYYMMDD>-<slug>-nlm-onboarding/`: `RESPONSE.md`, `sources/`, `jobs.json`, `artifacts.json`, `kit.py`.
- **Allowed tools/artifacts:** `nlm` CLI, the engagement's own documents, public research URLs, Playwright for the browser test. Sending notebook invites or sharing the kit needs the principal's explicit yes.
- **Done when:**
  - every artifact a path names is downloaded;
  - every infographic has been looked at;
  - each page passes the browser test: all tabs, every quiz type on that page, state persists after reload, no console errors;
  - every page except the lead's holds the core-path caps (step 7) and has passed the plain-language read (step 8);
  - the kit guide lists the known limitations.

**Triggers/Context**
- Ramping a team onto a new engagement, client, domain or method within days, especially mixed teams where one size fits nobody.
- Upstream: `engagement-kickoff` (the plan the team onboards to). The notebook mechanics live in `research/notebooklm`.

**Core Blueprint**
1. **Profile the people.** Per person: role, craft, prior knowledge of the engagement's topic (new / some / expert), what they own, time budget. Write `sources/00-team-and-learning-goals.md`: who the material is for, what each person needs from it, what "good" looks like, the working rules. Every artifact then knows its audience.
2. **Set the data boundary before uploading anything.** Into the notebook go the firm's own summaries (plan, concepts primer, proposal) and public primary research. Kept out: client internal documents, org charts and stakeholder names beyond the direct counterparts, until an NDA and the client's consent cover third-party AI tools. Use the work profile (`nlm login --check --profile <work>`). Any personal IP of the principal stays out until cleared.
3. **Load the sources.** Run `nlm notebook create`, then `nlm source add --file|--url --wait`. Prefer primary sources. Record the source IDs.
4. **Write `jobs.json`** with [the prompt library](references/prompt-library.md): the six rules, a format chosen by purpose, sources scoped per artifact. **Pass 1** is the shared core: a 2-minute video, the team briefing, the concepts deep dive, the talking-point countdown, a red-team critique, one short lens per role, a debate on the contested choice, 3–5 infographics. Queue it with `create_artifacts.py`, then run `fetch_media.py` in the background.
5. **QA pass 1.** Open every infographic (Read the PNG) and check for typos, logos and invented dates or names. Regenerate a failing one at most once with the visual guardrails, then accept and log what remains. Audio and video can't be checked here: put "check V1 and the first minutes of A1" at the top of the lead's path.
6. **Pass 2: fill the gaps per person.** A frontier brief for the lead, a rehearsal for whoever runs interviews or workshops, a craft video for the designer, one quiz per person at their difficulty, and glossary flashcards. Add the frontier sources these need first.
7. **Build the pages: core path first, the rest optional.** Copy `kit.example.py` to `<run-dir>/kit.py` and fill in ENGAGEMENT, MEDIA_DESC, ORDER, DATES and PEOPLE. Making more media than anyone needs is fine; putting all of it on a person's path is the failure. For everyone except the lead:
   - **`week`** is the core path: at most about 30–45 minutes of podcasts and video for the whole prep week, at most 3 media items a day, nothing longer than about 20 minutes. "Do" tasks come from their real prep work, listed in priority order: the page marks the first one "if you do one thing today".
   - **`deeper`** takes every other useful item. The page shows it in an optional Go deeper tab, next to at most 3 notebook questions, at most 2 reading links and the full library (collapsed).
   - **`glossary`**: at most 12 terms the material and the room will use that sit outside the person's craft, each with one plain sentence taken from the sources, anchored in their craft where possible ("like a persona card, for an agent"). The page shows it on Start here and uses it as their flashcards. For someone new to the topic, day 1 is meeting these words, not the theory.
   - **`quiz_pick`**: the 5 plainest questions, by index, mixing the types the quiz has. **`ready`**: 3 "I can…" statements.
   - **Sprint lines and tasks**: every term is in the glossary or rewritten in plain words.

   The lead's page may keep the full path; the lead checks the material for the team. Then run `build_kit.py --run-dir … --config … --out …`.
8. **Verify.**
   - **Browser test (Playwright):** open each page, click every tab, answer every quiz question, flip a card, rate one statement, reload, and check that state persisted and the console is clean.
   - **Plain-language read (verifier-separation):** a fresh-context agent reads each non-lead page's text as that person, from a packet in `children/<id>/TASK.md`. It lists every term not explained on the page, every unclear glossary line and anything that still overloads. Fix what it finds and rebuild.
   - Only then write the kit guide and index.
9. **Hand over and collect feedback in a fixed shape.** Ask before sharing the folder or zip on the firm's drive and before sending notebook invites (`nlm share invite`). The hand-over message asks each person for two things: "three statements you didn't understand" and "what you skipped". Unclear statements go into that person's glossary in the next version; skipped items move to `deeper`. Log the replies in `<run-dir>/FEEDBACK.md`.

**Optimizations/Gotchas**
- **`nlm download` takes no `--profile` flag.** With it, every download fails; it uses the default profile. `studio status` and `rename` do take `--profile`.
- **Quiz JSON mixes four types.** `multiple_choice`, `multiple_select` (several `isCorrect`), `fill_in_the_blank` (`bestAnswer`, `acceptableAnswers`) and `short_answer` (`grading.modelAnswer`). A choice-only parser silently drops 30–40% of questions. The template renders open questions as "write, then compare with the model answer, then self-grade", which teaches better anyway.
- **Flashcard sides** are `{flashcardContentBlock: [{type: "text", content}]}`, not strings.
- **The infographic image model makes typos** even when told to spell-check twice. Asking for icons only and no illustrations of people reduces them. Without "no logos" it may draw a client's logo. Regenerate once, then log the rest as a limitation.
- **Render times vary.** Infographics and audio take minutes; videos can take 30 or more. A 60-second poll is enough. `nlm download slide-deck` (slides) is wired in but untested.
- **Length:** `--length long` gives about an hour of audio, so put it in the path at 1.25–1.5×. A "short" lens comes out at 4–6 minutes: right for one sitting.
- **Delivery:** the pages need `media/` next to them, and Drive previews HTML as source code, so recipients download the folder. Ticks, ratings and answers live in each person's own browser, which keeps the package private.
- **Browser tests:** quiz clicks re-render the DOM, so re-query locators after each click instead of holding element handles. CSS `text-transform` changes `inner_text` case.
- **Persona lens:** the lead's path is also the quality gate. They check the material before the team relies on it.
- **Overload is the default failure (v1, 2026-11-01).** A v1 kit gave non-lead roles about 2.5 h of media, 10 quiz questions, 22 flashcards, 6 readiness statements, 6 notebook questions and a reading list. Recipients said "a lot of material: cut it to what's needed to exceed expectations" and, from someone new to the topic, "a lot of statements I still don't understand". v2 caps (step 7) brought the same roles to about 30 minutes. NotebookLM's shared flashcards and quizzes are written at team level; a person new to the topic needs their own glossary and a hand-picked short quiz.
- **Rebuild after feedback:** delivering changed pages only works when the media keys and filenames stay stable. Then recipients drop the new HTML into the folder they already have and don't download the media again. Checkbox state is keyed per engagement and person, so a restructured week starts with fresh ticks.
