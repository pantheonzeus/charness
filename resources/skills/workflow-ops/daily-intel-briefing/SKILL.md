---
id: daily-intel-briefing
aliases: [daily-intel-briefing, daily-briefing, ai-briefing]
name: "Daily Intel Briefing — Eight AI Themes, Deep Dives, Emerging Tech & German Manufacturing Outlook"
category: workflow-ops
description: Every weekday 06:30, research what is new since the last briefing across eight AI themes (LLMs/enterprise AI/RAG, agentic ops, token economics, self-improvement, physical AI, enterprise value, cyber threats, sovereign AI and regulation), emerging tech and the German manufacturing outlook, flag hits on a ten-term trend radar, write up to 3 news-driven deep-dive pages, and turn every topic with news into a 5–10 minute NotebookLM learning podcast, downloaded. Each item gets a "why it matters to you" line drawn from the vault, and item selection learns from the reader's 👍/👎 in the web console. Writes structured JSON to output/briefings/ for the console, then turns it into a two-host discussion podcast (sourced script + on-device voices) playable on the phone.
triggers: [daily intel, daily briefing, ai news, what's new in ai, agentic news, harness news, daily deep dive, ai deep dive, token economics news, ai finops news, physical ai news, humanoid robots news, sovereign ai news, ai regulation news, ai security news, trend radar, learning podcast, learn podcast, notebooklm topic podcast, teach me the topics, emerging tech news, german manufacturing outlook, ifo, pmi germany, vdma orders, run the briefing, today's briefing, briefing podcast, podcast of the briefing, listen to the briefing, two voices, audio briefing]
tags: [briefing, podcast, audio, news, ai, agentic, deep-dive, radar, manufacturing, germany, scheduled, console]
related: ["[[morning-briefing]]", "[[notebooklm-daily-audio]]", "[[notebooklm]]", "[[source-distillation-topic-note]]", "[[linkedin-viral-scheduler]]"]
status: active
version: 5
created: 2026-10-11
updated: 2026-10-31
modules: [file-backed-state, evidence-backed-answering]
scripts: [scripts/briefing.py, scripts/learn_podcasts.py, scripts/run.sh, scripts/podcast.sh, scripts/podcast.py]
workflows: [workflows/podcast-script.md]
---

# Daily Intel Briefing

**Contract**
- **Input:** today's date; `output/briefings/` (past briefings + `feedback.jsonl`); the vault (`cbrain/MOCs/Pursuits.md`, `cbrain/projects/`); the injected persona and memory index.
- **Output:** `output/briefings/<YYYY-MM-DD>.json` in the schema below, plus up to 3 deep-dive pages `output/briefings/<YYYY-MM-DD>/dd-<n>.md` (`report` template, [[reading-pages]]) that the briefing links, and one NotebookLM learning podcast per topic with news at `output/briefings/<YYYY-MM-DD>/learn/<section-id>.m4a` (made by `learn_podcasts.py` from the `learn` packs the run writes), rendered by the web console (`webapp/`, Briefings tab). The run script then writes the reading page `output/briefings/<date>.md` (`briefing` template, [[reading-pages]]) from that JSON with `briefing.py page <date>`, mechanically and with no agent cost; `podcast.sh` refreshes it so the page carries the episode. The console opens it from the briefing panel (**Open as page**). Do not write the page yourself. STATE_ROOT `output/.runs/<YYYYMMDD>-daily-intel/RESPONSE.md` is the control spine.
- **Allowed tools/artifacts:** WebSearch, WebFetch, Read/Grep over the repo and vault, `scripts/briefing.py`, `uv run resources/skills/workflow-ops/reading-pages/scripts/page.py check`. Never writes to the vault. Vault capture happens only when the reader clicks "Save to vault" in the console.
- **Done when:** `python3 resources/skills/workflow-ops/daily-intel-briefing/scripts/briefing.py check output/briefings/<date>.json` prints `OK` (it also checks the deep-dive pages) and every spine checkpoint is `[x]`.

**Triggers/Context**
- Scheduled: launchd `com.cbrain.daily-intel-briefing`, weekdays 06:30 → `scripts/run.sh` → `scripts/run_agent.sh daily-intel` (logged to the ledger and shown in the console's Loops tab).
- On demand: the console's **Run now** button, or "run today's briefing" in any session.
- Replaces the retired user-level `daily-briefing` (German) and `ai-weekly-briefing` agents (renamed `*.md.retired` in `~/.claude/agents/`). Their archives live outside the repo, so headless runs cannot read them. Do not try.

**Core Blueprint**
1. **Open the spine.** Create `output/.runs/<YYYYMMDD>-daily-intel/RESPONSE.md` with these boxes: `[ ] context loaded`, one `[ ] research: <section-id>` per section (ten), `[ ] radar swept`, `[ ] delta applied`, `[ ] deep dives picked`, one `[ ] deep dive: dd-<n>` per pick, `[ ] learning packs`, `[ ] briefing written + check OK`. Tick each one as it clears.
2. **Load context (reader first).**
   - Run `briefing.py prefs`. It prints the learned preferences (sections, tags, source domains and the items the reader saved or voted on). Bias selection toward 👍 tags and domains and away from 👎 ones. Never drop a section because of votes. A major release or indicator print always makes the cut.
   - Read the last 5 briefings in `output/briefings/`, excluding today's if this is a re-run. That is "already covered".
   - Read `cbrain/MOCs/Pursuits.md` and skim the persona. The reader is a Regional CTO hunting a PE digital-lab or manufacturing CTO role. They care about manufacturing buyers, sovereignty, agentic delivery and buy-vs-build economics.
3. **Research the window.** The window runs from the last briefing's date to now; on Monday that covers the weekend. Prefer primary sources (lab and vendor posts, papers, regulators, filings, official statistics).
   - **Floor, not just a ceiling.** Each section gets **≥ 2 WebSearch calls with different angles** and every item gets **≥ 1 WebFetch of its primary source** before it is written. A section's "Nothing material" note is valid only after its floor searches ran; log each query in `EVIDENCE.md`. *(Added 2026-10-31: runs from 2026-10-26 stopped after 7 searches and 0 fetches and shipped a 1-item briefing.)*
   - **Ceiling:** ≤ 60 WebSearch/WebFetch calls for the scan, ≤ 4 items per section, ≤ 18 items in total. On hitting a cap, write what you have and say so in `headline`.
   - **Theme sections** (the principal's eight AI themes; each item belongs in exactly one, the closest):
     - `llm-enterprise` — **LLMs, enterprise AI, RAG and knowledge architectures, AI agents, workflow automation:** lab releases (anthropic.com/news, openai.com/news, deepmind.google, Mistral, Meta, Qwen/DeepSeek), Hugging Face trending, retrieval/knowledge-graph/context-engineering work, enterprise platform launches (Microsoft, Google, AWS, SAP, ServiceNow, Salesforce), practitioner analysis (simonwillison.net, Latent Space, Import AI, The Batch).
     - `agentic-ops` — **Agentic AI & autonomous operations:** agent harness and framework releases (Claude Code, Agent SDK, MCP/A2A spec changes, LangGraph, OpenAI Agents SDK, open-source harnesses), agent papers getting real attention on arXiv, production deployments that run operations without a human in each loop, and their failures.
     - `token-finops` — **Token economics & AI FinOps:** API price changes, inference cost curves, caching/batching economics, GPU and capacity pricing, FinOps Foundation work on AI spend, lab revenue and margin disclosures.
     - `self-improvement` — **Recursive self-improvement & model evolution:** automated AI research, self-play and self-training results, harness/prompt self-evolution, eval saturation, frontier capability evals (METR, AISI, Epoch AI).
     - `physical-ai` — **Humanoid robots & physical AI:** humanoid makers (Figure, Agility, Apptronik, 1X, Unitree, Tesla Optimus, Neura), robot foundation models (NVIDIA GR00T, Physical Intelligence, Gemini Robotics), factory pilots. Industrial robotics lives here, not in `emerging`.
     - `enterprise-value` — **Enterprise value, consolidation & specialized AI:** measured ROI studies, M&A and funding rounds in AI (≥ $100M or strategically telling), vertical and domain-specific models, vendor consolidation, IPOs.
     - `cyber-security` — **Automated cyber threats & data security:** AI-driven attacks and exploits, agent and prompt-injection incidents, AI used in defence, data leakage, CISA/ENISA/BSI advisories.
     - `sovereign-regulation` — **Geopolitics, sovereign AI & regulation:** EU AI Act milestones and guidance, US/China export controls, sovereign-cloud and sovereign-model programmes (Gaia-X, EuroHPC AI factories, national LLMs), chip geopolitics.
   - **Standing sections:**
     - `emerging` — **emerging tech outside AI:** quantum, semis, energy tech, space, biotech platforms. Sources: MIT Technology Review, IEEE Spectrum, Gartner newsroom, CB Insights, heise.de. Skip consumer gadgets.
     - `de-manufacturing` — **German manufacturing business outlook:** ifo (Geschäftsklima, Produktions-/Exporterwartungen), HCOB Germany Manufacturing PMI, Destatis (Auftragseingang, Produktion, Exporte, Insolvenzen), VDMA (Auftragseingang Maschinenbau), ZVEI, VDA, Bundesbank, IW Köln, Handelsblatt / Reuters Germany. Every new indicator print goes into `indicators`, with its value, period, change and source.
   - **Radar sweep** (part of the scan budget, ≤ 5 searches, batch several terms per query): Large quantitative models · Speech reasoning models · World models · AI context platforms · AI coding agent harness · AI agent identity · Autonomous exposure remediation · SovereignTech · Disposable applications · Wetware as a service. A radar hit is a real item: it goes into the closest theme section and gets a `radar` entry pointing at it. No hit, no entry.
4. **Apply the delta.** Drop anything already covered unless it materially changed (a new figure, a new step in a running story). Say what changed. A section with nothing new gets `items: []` plus a `note` such as "Nothing material since <date>." Never pad.
5. **Write "why it matters to you"** for every item. Make it 1–2 sentences, specific to the reader, and name the pursuit, topic note or role it touches. Put the matching `[[wikilinks]]` in `vault_links` only after confirming each note exists (Glob/Grep). If nothing in the vault connects, say what the item means for a manufacturing CTO or PE operator. Do not invent a link. This field is **inference** and the console labels it so.
6. **Pick the deep dives (0–3, news-driven).** From today's items, pick the developments that most change what a manufacturing CTO or PE operator should believe or do: a frontier release, a regulation with a date, a price shift, a deal that reshapes a market, a first production deployment. Weigh reader preferences and pursuits, never section balance. A quiet day gets fewer, or none, with a one-line `deep_dive_note`. Never pick an item the last 5 briefings already deep-dived unless it materially moved.
7. **Write each deep dive** to `output/briefings/<date>/dd-<n>.md`. Budget: **≤ 12 WebSearch/WebFetch calls per dive, ≥ 4 distinct sources actually fetched**, at least one primary and one independent or critical. Content only, `report` template:
   - frontmatter `template: report`, `title`, `date`, `confidence: high|medium|low`;
   - `## Bottom line`: what is new, and the call, in 3–4 sentences;
   - `## What happened`: facts and numbers, each with its source inline;
   - `## How it works and why now`: mechanism, context, prior state;
   - `## What it means for you`: inference, labelled as such; name the pursuit, theme or buy-vs-build decision it touches;
   - `## What to watch`: dated next steps or the signal that would change the call;
   - `## Confidence and gaps`: what is direct observation vs inference, and what you could not verify;
   - `## Sources`: one `- [title](url)` per source.
   Run `uv run resources/skills/workflow-ops/reading-pages/scripts/page.py check <file>` and fix until it passes. Evidence gate as below: a number without a fetched source is dropped.
8. **Write a learning pack per topic.** Every section with ≥ 1 item today gets one entry in `learn`; NotebookLM turns it into a 5–10 minute deep-dive podcast meant to **teach**, not just report. Budget: **≤ 20 extra WebSearch/WebFetch calls across all packs.**
   - `sources`: 5–15 public URLs NotebookLM can read: every item source of that section, the fetched sources of its deep dive if it has one, plus 2–4 **background sources that teach the concept underneath the news** (the original paper, official docs or spec, a regulator's explainer, a respected primer). Fetch each background source once to confirm it loads and is not paywalled. No internal or employer hosts.
   - `focus` (≤ 800 characters, written to the hosts): who listens (a CTO who wants to understand, not skim), the one or two concepts to explain from first principles, today's news to walk through, the open question or counterargument to test, and what it means for a manufacturing buyer or PE operator. Ask them to define each term the first time.
   - `title`: the section title, or a sharper name for today's thread.
9. **Write the JSON** in the schema below, then run `briefing.py check`. Fix every error it prints and re-run until it says `OK`. Tick the last box.

**Learning podcasts (after the briefing, mechanical, NotebookLM)**
`run.sh` starts `scripts/learn_podcasts.py <date>` in the background next to the two-host podcast. No agent cost; a failure never fails the briefing.
1. Per `learn` pack: a notebook `Daily Intel · <date> · <title>`; sources = the pack's URLs (internal and employer hosts dropped, max 15) plus the section's items and its deep-dive page as text, each text uploaded only if `scripts/outbound_gate.py` (public mode) finds nothing.
2. `nlm audio create -f deep_dive -l short --language en --focus <focus>` for every notebook before any waiting, so they generate in parallel (~5–10 min each).
3. Poll, then download to `output/briefings/<date>/learn/<section-id>.m4a`. `state.json` beside them records notebook, artifact, refused sources and errors. Re-running the same command resumes and never duplicates a notebook or download.
4. **iMessage.** Once nothing is left generating, Jarvis texts you the numbered list of ready episodes (`<n>. <topic>: <title>`, plus a failed count) through `webapp/push.py`, once per day (`learn/notified` marker). This is the one place push sends titles: they come from public research (principal's call, 2026-10-31), and the list still passes `outbound_gate` (public mode). A flagged list goes out as a count only. **Reply to play:** `2`, `play 2` or `play humanoids` plays that episode on the Mac speakers (`webapp/listen.py`, caught in `server.py` `texted()` before the model, so it is instant and costs nothing); `stop` ends it. Not while the meeting shield has speech off.
5. `briefing.py page` re-runs afterwards, so the reading page's **Listen** block carries every episode; the console shows **▶ Learn** next to each section that has one (phone included).
`notebooklm-daily-audio` (18:00) skips the `Daily Intel · ` prefix, so these notebooks are not distilled into the vault. **Quota:** NotebookLM caps audio overviews per day by plan; up to 10 here plus idea-engine and the 18:00 sweep share it. A refused generation shows as `failed` in `state.json`.

**Podcast phase (after the briefing, separate job)**
`run.sh` calls `scripts/podcast.sh <date>` once the briefing run ends. A podcast failure never fails the briefing.
1. **Script (judgment).** This is a fresh headless job, `briefing-podcast` (`.claude/agents/briefing-podcast.md`, ledgered by `run_agent.sh`). Its task packet is [`workflows/podcast-script.md`](workflows/podcast-script.md). The job re-reads every item's primary sources (≤ 14 fetches) and logs each usable fact to its STATE_ROOT `EVIDENCE.md`. It then writes a Maya (anchor) and Ben (skeptical operator) discussion, one segment per item, to `output/briefings/<date>.podcast.json`, and does a fact pass against the evidence log.
2. **Gate (mechanism).** `uv run scripts/podcast.py check` fails the script if:
   - a briefing item has no segment;
   - a turn states a digit without a `src` URL drawn from the briefing sources, indicator sources or declared `extra_sources`;
   - a spoken turn contains a URL or markdown;
   - the length falls outside 1,500–4,000 words.
3. **Voice (mechanism).** `uv run scripts/podcast.py render <date>` voices the script on-device with Kokoro-82M (MLX, the same model as the console voice). Maya is `af_heart` and Ben is `am_michael`. The output is `output/briefings/<date>.mp3`, 96 kbps mono, roughly 12–18 minutes.
4. **Phone.** The console serves it at `/api/briefings/<date>/podcast` (HTTP range requests, so seeking works). On the Pixel, go through `tailscale serve`, then **Analyst → ▶ Listen**. The player is docked at the bottom, survives closing the panel and shows on the lock screen. **Make podcast** builds one for a briefing that has none.
Re-voice without the LLM: `podcast.sh --render-only <date>`.

**Schema** (`output/briefings/<YYYY-MM-DD>.json`)
```json
{
  "date": "2026-11-02",
  "window": "2026-10-30 → 2026-11-02",
  "headline": "One sentence: the single thing the reader should know today.",
  "sections": [
    {"id": "llm-enterprise", "title": "LLMs, enterprise AI, RAG & workflow automation", "note": "", "items": [
      {"id": "llm-enterprise-1", "headline": "…", "summary": "What the source says — facts and numbers from the linked source only.",
       "why_it_matters": "…", "vault_links": ["[[Pursuits]]"], "tags": ["rag", "anthropic"],
       "sources": [{"title": "Anthropic news, 2026-11-01", "url": "https://…"}]}
    ]},
    {"id": "agentic-ops", "title": "Agentic AI & autonomous operations", "note": "", "items": []},
    {"id": "token-finops", "title": "Token economics & AI FinOps", "note": "", "items": []},
    {"id": "self-improvement", "title": "Recursive self-improvement & model evolution", "note": "", "items": []},
    {"id": "physical-ai", "title": "Humanoid robots & physical AI", "note": "", "items": []},
    {"id": "enterprise-value", "title": "Enterprise value, consolidation & specialized AI", "note": "", "items": []},
    {"id": "cyber-security", "title": "Automated cyber threats & data security", "note": "", "items": []},
    {"id": "sovereign-regulation", "title": "Geopolitics, sovereign AI & regulation", "note": "", "items": []},
    {"id": "emerging", "title": "Emerging tech", "note": "", "items": []},
    {"id": "de-manufacturing", "title": "German manufacturing outlook", "note": "", "items": [],
     "indicators": [{"name": "ifo Geschäftsklima (Industrie)", "value": "-12.4", "period": "Oct 2026",
                     "change": "+1.1 vs Sep", "source": "https://www.ifo.de/…"}]}
  ],
  "radar": [{"term": "World models", "item_id": "physical-ai-2"}],
  "deep_dives": [{"id": "dd-1", "item_id": "llm-enterprise-1", "title": "…", "bottom_line": "One or two sentences: what is new and the call."}],
  "deep_dive_note": "",
  "learn": [{"section": "llm-enterprise", "title": "Context engineering after RAG",
             "focus": "For a CTO who wants to understand it: explain … from first principles, then walk through today's news …, test it against …, and close on what it means for a manufacturing buyer. Define each term the first time.",
             "sources": ["https://…", "https://…", "https://…", "https://…", "https://…"]}],
  "watchlist": ["Scheduled release or running story to check next time, with its date."]
}
```
Section ids and order are fixed (the check enforces them). `radar` terms must be spelled exactly as in the radar list. `deep_dives` ids run `dd-1…dd-3` and each needs its page; with no deep dives, `deep_dive_note` says why. `learn` has exactly one pack per section with items.

**Optimizations/Gotchas**
- **Evidence gate:** `summary` carries only what the linked source states. A number without a source URL is dropped, not softened. `why_it_matters` is the only place for inference.
- **Tags drive learning.** Use short, stable, lowercase tags (`agentic`, `mcp`, `open-weights`, `rag`, `finops`, `humanoids`, `world-models`, `ai-act`, `export-controls`, `ifo`, `pmi`, `machine-building`, `sovereign-cloud`). Inventing a new synonym each day breaks the preference signal.
- **Section ids changed 2026-10-31** (`ai` split into the eight themes). Older briefings keep `ai`; `prefs` still counts their votes.
- **Item ids** are `<section-id>-<n>` and must be unique. The console keys votes on `date` + `id`.
- **English throughout.** German sources are summarized in English. Keep the official German indicator name in `name`.
- The 👍/👎 votes live in `output/briefings/feedback.jsonl` and are written only by the console. Read them, never edit them.
