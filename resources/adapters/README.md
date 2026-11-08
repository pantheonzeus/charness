# Provider adapters — capability contracts

Skills ask for a **capability** (mail, calendar, files, chat), never a vendor. The active employer pack
(`employers/<slug>/profile.json` → `providers.<capability>.adapter`) says which implementation is bound.
Each contract below lists the operations skills actually use today and the normalized shape they write;
downstream code (vault builders, the console, agents) reads only that shape, never provider objects.

| Capability | Contract | Implemented | Stub |
|---|---|---|---|
| mail | [mail.md](mail.md) | `google` (Gmail REST + workspace-mcp) | `m365` |
| calendar | [calendar.md](calendar.md) | `google` (Calendar REST + workspace-mcp), `eventkit` (macOS Calendar.app, any account) | `m365` |
| files | [files.md](files.md) | `google` (Drive REST, read-only) | `m365` |
| chat | [chat.md](chat.md) | `slack` (claude.ai connector, read-only) | `teams` |

**Rules**
- A provider-specific script calls `employer.require("<capability>", "<adapter>", "<what>")` at its entry
  point (not at import), so a loop refuses to run against an unbound provider instead of failing on a dead
  token. Today: `mail-triage/scripts/triage.py`, `meeting-prep-loop/scripts/sync.py`, `slack-intel/scripts/slack_intel.py`.
  The console (`webapp/server.py`, `webapp/tasks.py`) adds its Gmail tools only while `mail=google`.
- Google code stays where it lives today, in each skill's `scripts/`, registered in the contract's
  implementation table. It moves behind a shared module when a second implementation exists to test
  against; a one-implementation abstraction would be untested design.
- A new implementation writes the same normalized shape, so builders and the console need no change.
  Query syntax (Gmail `from:… newer_than:` vs. Graph KQL/OData) lives inside the implementation.
- Credentials live outside the repo (`~/.config/<skill>/…`); the pack's `exit.credentials` lists them.
