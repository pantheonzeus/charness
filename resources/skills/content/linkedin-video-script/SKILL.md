---
id: linkedin-video-script
aliases: [linkedin-video-script]
name: "LinkedIn Video Script — 60–90s Face-to-Camera"
category: content
description: "Write a 60–90 second face-to-camera LinkedIn video script in the spoken register — one argument, a hook that survives three seconds of muted autoplay, burned-in captions, shot where the work already is. Separate from the text skill because the failure modes are different: a strong written hook is frequently an unspeakable sentence, and the deterministic prose audit mis-scores speech."
triggers: [video script, linkedin video, face to camera, record a video, talking head, video post, shoot a video, reel, script for camera, video hook, plant floor video]
tags: [content, linkedin, video, script, spoken-register, personal-brand]
related: ["[[linkedin-authentic-storytelling]]", "[[linkedin-viral-scheduler]]", "[[speaker-submission]]", "[[career-campaign-review]]"]
references: ["../linkedin-authentic-storytelling/references/ladder-joints.md", "../linkedin-authentic-storytelling/references/icp-positioning.md", "../../workflow-ops/linkedin-viral-scheduler/references/ranking-model-2026.md"]
modules: [evidence-backed-answering]
environment: "No special tooling. Phone camera, natural light, whatever room the work is happening in. No studio, no editing suite — that constraint is deliberate (see Gotchas)."
status: active
version: 2
created: 2026-08-22
updated: 2026-10-23
vault_writes: ["cbrain/projects/*", "cbrain/notes/[0-9]*"]
---

# LinkedIn Video Script — 60–90s Face-to-Camera

*Inherits the ICP, the joint spine and the confidentiality rules from [[linkedin-authentic-storytelling]] wholesale — do not re-derive them. What this skill owns is the **spoken register**, which is a genuinely different craft: written hooks are often unsayable, and the deterministic audit that governs text posts cannot score speech.*

**Contract**
- **Input:** one lived moment, one joint (from [`ladder-joints.md`](../linkedin-authentic-storytelling/references/ladder-joints.md)), one dialect, and a location where the work is actually happening.
- **Output:** `output/linkedin/video-<slug>-<YYYY-MM-DD>.md` — the spoken script marked for delivery, a caption/description block, a one-line shot note, and the reel-reuse tag.
- **Done when:** the script reads aloud inside 90 seconds without stumbling, the first spoken sentence works with the sound off, and the methodology check passes.

**Triggers/Context**
- Deploy when: recording a face-to-camera video, turning a field visit into a video, or scripting a joint explanation for camera.
- **Two per month** is the standing cadence (charter §7) and they come out of activity that was happening anyway.
- **Not for:** a text post ([[linkedin-authentic-storytelling]]) · a conference abstract ([[speaker-submission]]) · scoring a draft ([[linkedin-viral-scheduler]] — its audit cannot score this, see below).

**Core Blueprint**

### 1. Load the target, pick the one thing
- Read `icp-positioning.md` §ICP + Buyer Lexicon, and the relevant joint row in `ladder-joints.md`.
- **One argument. Not two.** Ninety seconds holds a single claim with one piece of evidence. The most common failure is a script that is a good three-minute talk compressed until nothing lands.
- Name: the **joint** · the **dialect** · the **lived moment** the video opens on.

### 2. The muted-autoplay hook (first ~3 seconds)
The video starts silent in a scrolling feed. So the opening does two jobs at once:
- **Spoken:** a concrete first sentence — the thing that happened, the number, the objection someone actually made. Never "Hi, I'm…", never "Today I want to talk about…", never the topic announced before the point.
- **Visible:** the burned-in caption of that same sentence, and a frame that says where you are. A plant floor, a machine, a whiteboard mid-argument — location *is* the credibility signal in the first second, and it is the one thing a text post cannot do.

### 3. Write it to be said, not read
- **Say each line out loud while writing it.** If you stumble, rewrite it. Subordinate clauses, em-dashes and parenthetical asides are text devices; they collapse in speech.
- Short sentences. One idea each. Spoken register tolerates repetition that reads badly on the page — and needs it, because a listener cannot re-read.
- **No numbered structure spoken aloud.** "There are three reasons" is a slide leaking into speech, and it trips the methodology check.
- Keep the arc: moment → what broke → the take. Land on a judgment, not a summary.
- **German (D1):** write in German end to end, don't translate. A translated script sounds translated, and this audience hears it immediately.

### 4. Timing and structure
| Beat | Seconds | Job |
|---|---|---|
| Hook | 0–5 | The concrete thing. Works muted |
| Stakes | 5–25 | Why it mattered — money, downtime, a decision with a cost |
| The turn | 25–65 | What actually broke, or what changed the call. The substance |
| The take | 65–85 | The judgment. Stakeable — someone could disagree |
| Out | 85–90 | Stop. No sign-off, no "let me know in the comments" |

### 5. Ship checklist (this replaces the deterministic audit)
`prepublish_audit.py` **cannot score this** — its readability and spacing gates are meaningless on speech, and its fluff and tension-marker lists are English prose lists. Record the composite as **not applicable** rather than running it and reporting a number that means nothing. Instead:
- [ ] Reads aloud in ≤90s at normal pace, no stumbles.
- [ ] First spoken sentence is concrete and works with sound off.
- [ ] Exactly one argument.
- [ ] One joint named internally; **no model, no stages, no framework language spoken aloud** (methodology check — `ladder-joints.md` §3.5).
- [ ] Three Buyer-Lexicon terms from the chosen segment appear naturally.
- [ ] Every number has a source; nothing confidential; client/consortium specifics abstracted.
- [ ] Captions burned in (a large share of feed viewing is muted).
- [ ] Reel-reuse tag set: is this clip usable in a speaker reel, and for which argument?
- [ ] The blind Substance and Audience-Pull judges are language-agnostic and **still apply** — run them if the claim is contested.

### 6. After publishing
- Log the video as a vault note `cbrain/projects/content-idea-<slug>.md` tagged `#content-idea` with joint + dialect, cross-linked to the visit or project it came from (Charter §6).
- Export the post stats within 72h like any other post. **First video export also answers an open question:** whether LinkedIn's single-post `.xlsx` carries watch-through or view-duration fields at all. Nobody on this account has exported a video post — record what fields actually appear, and tell [[linkedin-weekly-review]] so it stops guessing.
- Judge it on watch-through and decision-maker density, **not on reactions**.

**Optimizations/Gotchas**
- **The no-studio rule is load-bearing.** A production setup turns two videos a month into a hobby with a budget, and polish is not what earns trust with this audience — being visibly at the work is. Phone, daylight, real location.
- **A great written hook is often unsayable.** The text skill's best openers frequently depend on line breaks and punctuation doing the work. Rewrite for the mouth; don't port.
- **Video's justification is narrower than it first looks.** It was originally adopted here as a stage audition for programme committees. The campaign then moved to closed-door rooms, which run on referral rather than reels, so that argument was withdrawn (charter T7 resolution). Video stays as a reach-and-trust format showing the work at plant altitude — a real but smaller claim. Do not re-inflate it.
- **Confidentiality is harder on camera.** A plant background can expose a client, a machine, a layout or a customer's process. Check the frame, not just the script. This is a Soul.md inviolable line and it beats the better shot every time.
- **Sound-off viewing is the default, not the exception.** A script whose value only arrives audibly is a script most viewers never hear.
- **No engagement bait.** "What do you think?" closes fail the audit for text posts and are no better here — they just also sound needy out loud.
