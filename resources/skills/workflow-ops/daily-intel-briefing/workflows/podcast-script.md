# Briefing podcast — two-host script (task packet)

Context mode: **fresh**. You get a date. Turn that day's briefing into a two-host discussion script the reader listens to on the phone, about 12–18 minutes long. Accuracy beats polish. A fact that is wrong in someone's ear is worse than one left out.

**Input:** `output/briefings/<date>.json` (already source-checked) and the primary sources it links.
**Output:** `output/briefings/<date>.podcast.json`. STATE_ROOT: `output/.runs/<YYYYMMDD>-briefing-podcast/` with a `RESPONSE.md` spine and an `EVIDENCE.md`.
**Done when:** `uv run resources/skills/workflow-ops/daily-intel-briefing/scripts/podcast.py check output/briefings/<date>.podcast.json` prints `OK` and every box is `[x]`. Rendering the audio is not your job; `podcast.sh` runs it after you stop.

## The hosts
- **Maya (speaker `A`)**: the anchor. She has read the sources closely. She explains what happened, with the numbers, and how it works.
- **Ben (speaker `B`)**: the operator. He thinks like a manufacturing CTO who is moving into a PE Digital Lab role. He asks the questions the listener would ask: "what's the catch", "who pays", "what would I do with this on Monday". He pushes back when a claim is thin.

They disagree where the evidence leaves room for it. Neither one flatters the listener or the news.

## Steps (tick each in RESPONSE.md)
1. `[ ] briefing read`: read the briefing JSON in full, including `why_it_matters`, the indicators and the watchlist.
2. `[ ] sources read`: WebFetch the primary source of every item, plus a second source where the item has one. Budget: **≤ 14 fetches**. If a fetch fails, work from the briefing `summary` alone for that item and say so on air ("the report itself was thin on detail"). In `EVIDENCE.md`, log every fact you might use, one line each: `fact | url | quote or figure as printed`. To add depth, you may follow at most 2 links from a primary source. List each such URL in `extra_sources`.
3. `[ ] script drafted`:
   - **Cold open (item `null`):** Maya gives the day's headline in two sentences, and Ben says why he cares.
   - **One segment per briefing item, ordered by weight for the listener** (not section order). Items with a deep dive (`deep_dives[].item_id`) lead and get the longest segments: read their page `output/briefings/<date>/dd-<n>.md` first and list any of its sources you cite in `extra_sources`. Other items get two or three turns each. Each segment covers what happened (facts, numbers, who), how it works or why it happened, Ben's challenge, and the implication. The implication is inference. Voice it as such: "my read is", "the bet here is", "if that holds". `why_it_matters` is your starting point for the implication. Say the pursuit or topic in plain words and never read out a note name.
   - **Indicators** go inside the manufacturing segment as numbers with their period and change.
   - **Close (item `null`):** the watchlist dates that matter in the next two weeks, and one question to think about. No sign-off fluff.
4. `[ ] fact pass`: go through the script turn by turn. Every factual statement must appear in `EVIDENCE.md` with a matching figure. Delete or soften any statement that does not. Every turn that contains a digit needs `src` URLs taken from the briefing sources, the indicator sources or `extra_sources`. Never round a number in a way that changes its claim, and never state an inference as fact.
5. `[ ] check OK`: run `podcast.py check` and fix every error it reports until it prints `OK`.

## Writing for the ear
- Use short sentences and one idea per turn. Most turns are 1–4 sentences, and the hosts interrupt and react ("Wait, employee-level?").
- Write numbers and versions the way a person says them: "three point five trillion dollars", "Claude Code version two point one, three hundred", "Q3" → "the third quarter". Write abbreviations as spoken ("V-D-M-A", "P-M-I", "ifo" is said as one word). Leave out URLs, markdown, brackets and emoji. The check rejects them.
- German names stay German: say the official name once, then use the English gloss ("the ifo business climate index").
- No ad-read energy, no "great question", no "stay tuned". Dry wit is allowed, at most one line per segment.
- Total length: 1,800–3,000 words. The check enforces 1,500–4,000.

## Schema
```json
{
  "date": "2026-10-16",
  "title": "Briefing, 16 October: METR inside Anthropic, the AI capex hangover",
  "extra_sources": ["https://…"],
  "segments": [
    {"item": null, "turns": [{"speaker": "A", "text": "…", "src": []}]},
    {"item": "ai-1", "turns": [
      {"speaker": "A", "text": "…three point five trillion dollars…", "src": ["https://…"]},
      {"speaker": "B", "text": "…", "src": []}
    ]}
  ]
}
```
Every briefing item must have its own segment. The check fails if one is missing.

## Never
- Never add a fact that is not in `EVIDENCE.md`, including background "everyone knows". If it matters, fetch it and log it.
- Never write to the vault or to any file outside the output and STATE_ROOT paths above.
- Never put confidential client numbers or internal pursuit figures on air. Name the pursuit or topic only.
