<!-- Lead with the outcome, not the code. Keep the diff surgical — every changed line should trace to this change. -->

## What & why
<!-- The problem this solves and the observable result. One or two lines. -->

## Layer
<!-- Tick the layer(s) this touches (see CONTRIBUTING.md). -->
- [ ] Backend / mechanism (`.claude/` hooks, per-skill `scripts/`)
- [ ] Runtime Charter (`Charter.md`)
- [ ] Identity / voice (`Soul.md`, `IDENTITY.example.md`)
- [ ] Skill library (`resources/skills/**`)
- [ ] Docs / repo meta

## How I verified
<!-- No CI yet — say what you ran and what you observed. E.g. hook fed sample JSON, script --dry-run + idempotency re-run, INDEX count check. -->

## Checklist
- [ ] Diff is surgical — every changed line traces to the stated change.
- [ ] **Skill change:** `INDEX.md` updated in the same commit (row + `Skills: N` count).
- [ ] **Skill change:** `version` + `updated` bumped; body opens with a Contract block.
- [ ] **Charter / Soul / `_shared/` / core Blueprint edit:** a change-manifest entry added to `resources/skills/_shared/CHANGE_LOG.md` (trigger · files · expected fix · risk · `Verdict: pending`).
- [ ] **Hook change:** fails open (`exit 0`) on any parse/shape error; both allow and deny paths tested.
- [ ] No private/vault data in the diff (nothing from `cbrain/`, `output/`, `input/`, or `IDENTITY.md`); `git status` is clean of them.
- [ ] Commit subject is a conventional-commit (`feat(skills): …`, `fix: …`, `docs: …`), one logical change per commit.
