# Frontmatter schema & Base recipes

The reference layer for `[[progressive-disclosure]]`. Bases can only filter/sort on **YAML
frontmatter properties** — this file defines the canonical vocabulary and gives copy-paste
`.base` recipes.

## Canonical YAML properties

Target this shape on every note that should be Base-queryable. Auto-generated layers (Mail,
NotebookLM) already emit YAML; the human layers (Clients, meetings, dailies) currently use
inline `**bold:**` fields and need migration before they populate a Base.

| Property | Applies to | Values | Notes |
|---|---|---|---|
| `type` | all | `mail` · `notebook-source` · `topic` · `meeting` · `person` · `account` · `daily` · `nlm-query` | The primary Base discriminator. Mail/NLM/topic set it today. |
| `status` | people, accounts, projects, tasks | `active` · `new` · `reconnect` · `won` · `lost` · `done` · `archived` | Replace the placeholder `New (from calendar)` with a real enum on migration. |
| `date` | dated notes | `YYYY-MM-DD` | Meetings, mail, dailies. Enables time sorting. |
| `tags` | any | list, e.g. `[research, ai-sdlc]` | Cross-cutting themes; the tag taxonomy is currently near-empty. |
| `company` | people, accounts | string | Currently inline `**Company:**` on people notes. |
| `aliases` | people | list | Already used on hand-edited notes for `[[wikilink]]` resolution. |

**Migration status — DONE (2026-07-06; counts refreshed 2026-07-11):** the human-layer
notes (Clients/, notes/, daily reports/) were backfilled to YAML `type`/`status`/`company`/`date`,
and both generators (`build_contacts.py`, `mail-to-conversations/build_conversations.py`) now
emit YAML so new notes stay correct. Current live counts: `Clients/` = **137** (132 `type: person`
+ 5 `type: account`, all carrying `status`, so all populate `People.base`); `type: meeting` = **303**.
Re-backfill after any bulk import with the migration script in
`autoresearch/improve-260706-1537/migrate_frontmatter.py` (additive, idempotent).

## Base file syntax

A `.base` file is YAML with `filters` (expressions) and `views` (tables/cards). Property
references use bare names (`status`), file metadata uses `file.*` (`file.name`,
`file.inFolder("...")`, `file.hasTag("...")`). Filters combine under `and:` / `or:` / `not:`.

### Mail.base — works today (uniform YAML)
```yaml
filters:
  and:
    - file.inFolder("Mail/msgs")
views:
  - type: table
    name: Recent mail
    order:
      - file.name
      - date
      - from
      - subject
    sort:
      - property: date
        direction: DESC
```

### Sources.base — works today (NotebookLM)
```yaml
filters:
  and:
    - type == "notebook-source"
views:
  - type: table
    name: NotebookLM sources
    order:
      - file.name
      - source_type
      - status
      - date
    sort:
      - property: date
        direction: DESC
```

### Projects.base — works today (topic notes)
```yaml
filters:
  and:
    - type == "topic"
views:
  - type: table
    name: Topics / projects
    order:
      - file.name
      - status
      - tags
    sort:
      - property: file.name
        direction: ASC
```

### People.base — near-empty until migration (honest scope)
Filters to Clients notes that carry a real YAML `status`. Today that is ~0–2 notes; it
populates once the migration adds `status`/`company`/`type` YAML to person notes.
```yaml
filters:
  and:
    - file.inFolder("Clients")
    - status != null
views:
  - type: table
    name: People (structured)
    order:
      - file.name
      - status
      - company
    sort:
      - property: file.name
        direction: ASC
```

## Embedding a Base in a MOC
```
![[Mail.base]]
```
Or inline a one-off view directly in a note with a ` ```base ` code block containing the
same YAML. Standalone `.base` files are preferred for reuse.
