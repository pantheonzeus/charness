# Employer packs

Everything in this harness that ends with an employment contract lives in one folder per employer:
the role, the mail/calendar/files/chat bindings, that employer's clients and partner domains, its
Slack channels, its brand, its confidentiality approvals and the launchd loops its bindings feed.
The rest of the harness is **general** (public, charness) or **personal** (`IDENTITY.md`, the vault,
the LinkedIn and newsletter loops), and neither changes when the job does.

```
employers/
  README.md         this contract (public)
  _template/        an empty pack, every field commented (public)
  ACTIVE            one line: the active slug, or "none"            (gitignored)
  <slug>/           a real pack                                     (gitignored)
    profile.json    identity, provider bindings, runtime, confidentiality, files, loops, brand, exit
    role.md         role overlay: SessionStart injects it right after IDENTITY.md
    brand/          palette, fonts, house style, reference examples (audience-of-one-report)
    <skill-id>/     the skill's real config, same file name as its schema/*.example.*
```

Mechanism: [`scripts/employer.py`](../scripts/employer.py) (stdlib; skills import it). The SessionStart hook
runs `employer.py context`, so every session knows the active employer, its bindings, and the rule
that content from any employer, current **or former**, is class `employer-internal`.

## profile.json

| Key | Meaning | Read by |
|---|---|---|
| `employer.name`, `company_names`, `domains`, `work_email`, `start`, `end` | who "us" is | client-follow-through gate, console + living-plan send address, SessionStart |
| `providers.<mail\|calendar\|files\|chat>.adapter` | bound implementation, see [resources/adapters/](../resources/adapters/README.md) | provider guards in triage.py, sync.py, slack_intel.py, console tools |
| `runtime.claude_login` | which Claude login runs the loops (keep it `personal`) | `employer.py validate` warns when the login belongs to an employer |
| `confidentiality.class`, `vault_ok` | the class rules key on; dated approvals for this employer's content in the vault | skills (via SessionStart), slack-intel vault lines |
| `files` | the real config files in this pack | `employer.py validate` |
| `loops` | launchd labels this employer's bindings feed | `employer.py loops` |
| `brand` | house style name, CTA heading, bundled brand skills, internal knowledge-base plugin | audience-of-one-report |
| `exit.notes`, `credentials`, `output_dirs`, `vault_markers` | what to revoke and what content stays behind | `employer.py exit-report` |

Pack files today: `mail-triage/companies.json`, `slack-intel/channels.json`, `mail-to-conversations/domain_map.yaml`,
`calendar-to-contacts/domain_map.yaml`, `brand/`. Resolve one with `python3 scripts/employer.py path <rel>`.

## Start at a new employer

1. `cp -R employers/_template employers/<slug>`. Fill in `profile.json` and `role.md`.
2. Pick adapters per capability. If the employer runs Microsoft 365, the `m365` / `teams` implementations are
   stubs: build them against the contract in `resources/adapters/` first. Calendar works on day one through
   `eventkit` (add the work account to Calendar.app).
3. Copy each skill's `schema/*.example.*` into `employers/<slug>/<skill-id>/` and fill in the real lists.
4. `echo <slug> > employers/ACTIVE`, then `python3 scripts/employer.py validate` until it prints OK.
5. Set up each provider's credentials (for Google: `resources/mcp/google-workspace.md`), then
   `python3 scripts/employer.py loops --load --apply`.
6. Record any vault approval the principal gives in `confidentiality.vault_ok`, dated.

## Leave an employer

1. `python3 scripts/employer.py exit-report <slug>`: loops, content still on disk (tagged vault notes, notes
   holding marked sections, output folders, the private vault history), credentials, notes.
2. `python3 scripts/employer.py loops --unload --apply`, then `echo none > employers/ACTIVE`.
3. Revoke and delete the listed credentials; disconnect employer connectors in claude.ai.
4. Keep or purge the content: a contract question, not a harness default. The pack folder stays on disk
   (gitignored) so its content keeps counting as a former employer's `employer-internal` material.
