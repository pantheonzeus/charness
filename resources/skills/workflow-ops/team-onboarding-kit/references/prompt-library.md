# Prompt library — NotebookLM studio prompts for team onboarding

Placeholders: `<ENGAGEMENT>` (client + project in one phrase), `<DATES>`, `<PERSON>` / `<ROLE>`, `<EXAMPLE>` (the one running example), `<CONCEPTS>` (numbered list from the concepts source). Fill them in the jobs file and never in this library.

## The six rules (apply to every prompt)
1. **Name the listener and what they already know.** "For <PERSON>, <ROLE>, who knows X and not Y." The lead gets no basics; non-specialists get every term defined at first use.
2. **State the goal as an ability.** "Afterwards they can explain each concept to a service owner." Not "cover topic X".
3. **Fix the structure.** A numbered outline in the sprint's or the concept source's order. NotebookLM follows numbered outlines closely.
4. **One running example everywhere.** Pick one case from the engagement and land every concept on it.
5. **Scope the sources.** Pass `--source-ids` per artifact: visuals get only the firm's own docs; debates get only the studies that disagree.
6. **Guardrails, appended verbatim:**
   - text: *"Stick to the sources. Do not invent client names, figures or dates. Say when a figure is a forecast or vendor claim rather than research. Plain English for non-native speakers; no hype words."*
   - visuals add: *"Spell every word correctly and check all text twice. Use only names and dates exactly as in the sources. No logos or brand marks of any company."*

## Format by purpose
| Purpose | Kind · format | Notes |
|---|---|---|
| Whole-team briefing | audio · deep_dive · default | Address each person by name in the "who owns what" part |
| Concepts | audio · deep_dive · long | Running example; end with the forcing questions |
| Talking points | audio · deep_dive · default | Countdown, one segment each: fact + source + "so for them…" + when used |
| Objections | audio · **critique** | The only format that argues against your plan; ask for 2 weaknesses to fix |
| Role lens | audio · deep_dive · short | One per person, in their craft's language |
| Contested choice | audio · **debate** · short | Close on "it depends on the task shape" |
| Frontier brief (lead) | audio · deep_dive · default | Evidence strength, what's contested, "claims not to make" |
| Rehearsal | audio · deep_dive · short | For the people who run interviews or workshops |
| Process explained | video · explainer · whiteboard | One flow, one example |
| Management topic | video · explainer · `--style-prompt` editorial | Calm business register |
| Two-minute overview | video · brief · classic | Shareable |
| Flows, timelines | infographic · landscape · professional | Icons only, no people illustrations (fewer text errors) |
| Checklists | infographic · portrait · bento_grid / editorial | One tile per item |
| Cheat sheet | infographic · portrait · sketch_note · concise | Exact numbers only |
| Self-check | quiz · `--count 10` · difficulty 2 (non-specialists) / 4 (lead) | Scenario questions; "explain each answer" |
| Vocabulary | flashcards · medium | Front: term. Back: one sentence + "at <client> this means…" |

## Archetype prompts

**Team briefing (audio).** "Audience: <names and roles> who start <ENGAGEMENT> on <DATES>. Goal: afterwards each knows why the client wants this, what we must deliver, how the days run and exactly what their own role is. Structure: 1) situation and our bet; 2) success criteria; 3) rhythm; 4) the days, highlighting the wow moments; 5) what each person owns, by name; 6) working rules. End with what each person does in prep week." + rules

**Concepts deep dive (audio, long).** "Audience: <non-specialist roles>; <lead> listens for sharpness. Goal: each can explain every concept to a client stakeholder and knows the question to ask. Use one running example throughout: <EXAMPLE>. Cover in order: <CONCEPTS>. Explain every technical term the first time. Where sources disagree, present both and say what it depends on. End with the forcing questions." + rules

**Red team (audio, critique).** "Review our plan and concept as a sceptical but fair senior <client function> manager would. Find the five strongest objections, e.g. <3–6 likely ones>. For each: why it's reasonable, what in our plan answers it, the one-sentence reply. Then name two genuine weaknesses to fix before day 1." + rules

**Role lens (audio, short).** "For <PERSON>, <ROLE>, who owns <their part>. Translate the concept into <their craft's language>: <4–6 specific topics>. Skip detail that doesn't change their work; define any term in one sentence. End with <a checklist / five interview questions>." + rules

**Frontier brief (audio).** "For <lead>, who knows the basics. What changed recently in <field>: <topics>. For each finding: what exactly was measured, how strong the evidence is, what is contested, and one implication for <ENGAGEMENT>. End with three claims NOT to make to the client because the evidence is too thin." + rules

**Quiz.** "Questions for a <ROLE>: <topic list>. Scenario-style ('a stakeholder says X — which concept answers it?'). Explain each answer."
