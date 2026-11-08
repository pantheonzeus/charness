---
id: vault-maintenance
aliases: [vault-maintenance, vault-cleanup, link-audit, vault-health-check]
name: "Vault Maintenance — Link Integrity & Hygiene Sweep"
category: vault-hygiene
description: Audit the whole Obsidian vault for broken links, orphans, missing frontmatter, empty/corrupt files, and name collisions — then fix by ROOT CAUSE (not raw count), separating content fixes from generator-script fixes. Alias-, table-pipe-, and code-span-aware so it doesn't over-report. Script-backed.
triggers: [clean up the vault, vault clean-up, vault maintenance, vault health check, audit the vault, check the second brain, fix broken links, broken links, dangling links, orphan notes, link integrity, is everything in order, entry by entry, make the vault perfect]
tags: [vault-hygiene, obsidian, links, orphans, frontmatter, audit, maintenance, integrity]
related: ["[[progressive-disclosure]]", "[[contact-meeting-capture]]", "[[skill-library-maintenance]]", "[[contact-enrichment-dedupe]]"]
scripts: [scripts/link_audit.py, scripts/gen_daily.py, scripts/ratchet.py]
modules: [autoresearch-loop]
status: active
version: 6
created: 2026-07-09
updated: 2026-10-23
vault_writes: ["cbrain/*"]
---

# Vault Maintenance — Link Integrity & Hygiene Sweep

Keeps `cbrain/cbrain/` in best shape: no dangling links, no islands, clean frontmatter, no
name collisions. The core discipline is **diagnose by root cause, not by raw count** — a naive
`[[link]]` scan over-reports by ~3× because of three Obsidian resolution rules it misses. Fix the
few real causes; don't hand-patch symptoms in files that a generator will just regenerate.

**Triggers/Context**
- "clean up / audit the vault", "check the second brain is in order", "fix broken links", "entry by entry", "make it perfect".
- After a bulk import (calendar → contacts, mail → conversations, NotebookLM distill) — those generators are the usual source of breakage.
- Periodic health check (pairs with the notebooklm skill's narrower `link_audit.sh` orphan gate).

**Core Blueprint**
1. **Survey scale first.** `find cbrain -name '*.md' | wc -l`; counts per top dir. Know if it's 50 or 600 files before choosing eyeball vs script.
2. **Run the alias-aware auditor — never eyeball a large vault.**
   `python3 resources/skills/vault-hygiene/vault-maintenance/scripts/link_audit.py`
   It reports broken refs, orphans, empty/no-frontmatter files, and buckets missing targets by root cause. It writes `audit.json` for follow-up scripts.
3. **Trust the buckets, not the headline number.** The script already strips the three false-positive traps (see Gotchas). If you wrote your own check, subtract them by hand or you'll "fix" links that already work.
4. **Triage every bucket into CONTENT vs GENERATOR:**
   - **Content** (hand-fix now): malformed syntax (`[[[x]]`), empty/corrupt files, one-off typos, genuinely-missing notes, name collisions.
   - **Generator** (fix upstream, don't whack-a-mole): anything in an auto-generated file (`Conversations.md`, `*-Index.md`, calendar/mail contact stubs, `notebook-source` frontmatter). Hand-edits there evaporate on the next regen — log the root cause and fix the skill's script instead.
5. **Fix the deterministic buckets directly** (surgical, reversible):
   - **Name-variant links → existing note:** add `aliases: ["Variant One", "Variant Two"]` to the note's frontmatter. One line repairs *every* reference at once — always prefer this over editing each source. (`[[Roe, Richard]]`, `[[R Roe]]` → the `Richard Roe.md` aliases.)
   - **Name collision** (two files, same basename → ambiguous `[[link]]`): confirm with `find cbrain -iname 'name.md'`; delete the junk one or rename to disambiguate.
   - **Empty / corrupt files:** investigate purpose before deleting; populate or remove.
   - **Missing frontmatter:** add the minimal `type:` + identity keys matching siblings.
6. **Confirm the high-volume / destructive buckets before executing** (Clarify Before Action):
   - **Daily-note links `[[YYYYMMDD]]`** (usually the biggest bucket): generate honest stubs in `daily reports/` listing that day's real meetings + weather (`scripts/gen_daily.py` pattern) — no fabricated summaries.
   - **Missing people / orgs:** create per the Living Knowledge Graph rule, harvesting company/role from the linking meeting/mail, wired bi-directionally (person↔meeting, person↔account, person↔topic roster). Filenames must match the exact `[[link]]` form; add aliases for the other order.
   - **Auto-minted topic links** (NotebookLM concepts with casing dupes): redirect to the existing anchor (`[[AI SDLC]]`) that the note already carries in `related:`, and delink the granular ones to plain strings — don't spawn dozens of stub anchors.
7. **Re-run the auditor and confirm** broken-refs → the irreducible by-design set (external skill refs in logs, code-span placeholders). State the before/after and what remains on purpose.

**Weekly ratchet (measure → trend → alarm; edits no notes except the provenance stamp)**
- `python3 resources/skills/vault-hygiene/vault-maintenance/scripts/ratchet.py` runs `link_audit.py` and counts missing link targets per category. It then runs the recall benchmark (`progressive-disclosure`) as the guard and appends a row to `output/vault-ratchet/results.tsv`.
- **Categories:**
  - `skill-ref`, `output-ref` and `memory-ref` targets live outside the vault and are fixed in the generator that wrote the link.
  - `person/org` and `concept/topic` need a stub (principal's approval) or a re-link.
  - `meeting/daily` counts links to `YYYYMMDD…` notes.
- **Verdicts:**
  - `RATCHET=REGRESS` (exit 1) when any category grew since the last row, or recall FAILs.
  - `HOLD` otherwise.
- **Ingest provenance (since 2026-10-23):** the ratchet also runs `python3 scripts/ingest_lint.py sweep`. It stamps `provenance: untrusted-ingest` on new notes under the ingest paths (newsletters, mail, NotebookLM sources) and lists instruction-shaped lines for a person to review. It checks ingest notes, `provenance: derived-untrusted` notes (stamped by the provenance hook since 2026-10-24), and `## … signals` and `## What changed — <date>` sections. The sweep never changes the ratchet verdict.
- **Any fix pass is add-only and recall-gated:** run the ratchet before and after, and revert if recall drops.
- **Never add `aliases:` just to clear a missing target.** link_audit counts an alias as resolving, but Obsidian's docs (obsidian.md/help/aliases) only show alias links written as `[[Note|Alias]]`, so a raw `[[Alias]]` may stay broken in Obsidian while the metric improves.
- **Schedule:** `scripts/com.cbrain.vault-ratchet.plist` (Mondays 07:15). **Installed and loaded 2026-10-09** as `~/Library/LaunchAgents/com.cbrain.vault-ratchet.plist`; a test fire via `launchctl start` returned HOLD. Install steps are in the plist header comment. Log: `output/vault-ratchet/ratchet.log`.
- Baseline 2026-10-09: 143 missing (5 skill-ref, 3 output-ref, 1 memory-ref, 78 person/org, 56 concept/topic), 52 files with broken refs, 752 orphans, recall PASS.

**Optimizations/Gotchas**
- **The four false-positive traps (why naive scans over-report):**
  1. `[[note\|Alias]]` — inside Markdown **tables** the alias pipe is `\|`-escaped; a naive split leaves a trailing `\` on the filename. Unescape first.
  2. `aliases:` **frontmatter** — Obsidian resolves `[[Alias]]` to the note declaring it. Load aliases into the resolver or every aliased link reads as broken.
  3. `` `[[x]]` `` — a wikilink inside inline code or a fenced block is **not** a link. Strip code spans before matching. (This is why `[[YYYYMMDD-City]]` in `Home.md` is fine — it's in backticks.)
  4. **Attachments** (`.pdf`, images) — `[[notes/attachments/foo.pdf]]` is a real, resolving link, not a broken one. `link_audit.py` v3+ indexes attachment basenames/paths alongside `.md`/`.base` so these no longer read as broken (fixed 2026-07-18 after a TechDays-deck PDF link false-positive).
- **Generator root causes seen in this vault (fix the script, not the output):** calendar→contacts names files after email local-parts (`jane.doe`) and derives junk `company:` from the domain suffix (`Ac`, `Fft`, `Onmicrosoft`), and captures **mailing lists / rooms as people** (`projectteam@…onmicrosoft.com` → a bogus `Clients/ProjectTeam.md` that then *collides* with the topic anchor). mail→conversations keeps raw `'X' via christoph` sender strings. NotebookLM distill mints uncanonicalised `[[Concept]]` links with casing duplicates.
- **Multi-part-TLD junk companies (named bug, fixed in calendar→contacts v4).** `company:` derived as `domain.split(".")[-2]` grabs the TLD tier on ccSLDs: `warwick.ac.uk`→"Ac", `tuwien.ac.at`→"Ac", `acme.co.uk`→"Co", and personal `outlook.es`→"Outlook" (only `.com` providers were blocked). **The email domain is the ground truth for the fix** — read the person note's `**Email:**` line and derive the real employer (org label before the public suffix), or blank it for personal/vanity domains (`outlook.es`, `pap.pm`) rather than guessing. One generator bug = many junk rows; fix `_MULTI_SUFFIX`/`_PERSONAL_LABELS` in `build_contacts.py`, don't just scrub the output. Same generator also produced **casing/variant company splits** (`Acme` vs `ACME`, `Initech` vs `Initech Optics`) — canonicalize via the `company:` field (one value per org) so People.base groups cleanly.
- **Orphans that are fine:** NotebookLM `Sources/*` and `Mail/msgs/*` are leaf nodes surfaced via `.base` queries, not wikilinks — 0 inbound is expected. Don't force-link them. Chase orphans only for hubs (topics, people) that *should* be linked.
- **Don't rewrite historical records** (`daily reports/`, past meeting notes) to clean a cosmetic link — an intentional skill cross-ref like `[[contact-meeting-capture]]` in a log is acceptable.
- **Aliases > mass edits.** Adding one `aliases:` line fixed 18+ references at once here. Reach for it before touching many files.
- **Self-references** (`[[Your Name]]` — the vault owner) should be delinked to plain text, not turned into a contact note.
