# Changelog

Notable changes to charness. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow
[Semantic Versioning](https://semver.org/). Pushing a `v*` tag publishes that version's section below as the
GitHub release (`.github/workflows/release.yml`); the release fails if the section is missing.

## [Unreleased]

## [0.1.0] — 2026-11-08

First tagged release of the public harness.

### Added
- **Repo checks and CI.** `scripts/check.sh` runs every check: hook test suites, skill lints, ruff and
  shellcheck. GitHub Actions runs it on each push and pull request, and re-runs the commit guard over
  pushed commits. `main` is protected by `.github/rulesets/main.json`.
- **Commit guard.** Git hooks block secrets, personal data, client names, ignored files, force pushes and
  co-author trailers in commits and pushes (`scripts/commit_guard.py`).
- **Session archive.** Claude Code transcripts kept past the cleanup, secrets redacted, hash-chained index;
  `jarvis-control` skill for the console.
- **Memory consolidation.** Supersession convention and a reviewed "dream" pass (`scripts/memory_dream.py`).
- **Model-aware harness.** Pinned models and effort per headless job, per-model-family prompt addenda,
  quality floors.
- **Skill Library Maintenance v7.** Agent Skills spec export and an exportability lint.
- **Skills:** team-onboarding-kit (v2) and engagement-kickoff.
- **PostToolUseFailure path hint.** A missed Read/Edit path is answered with what exists.

### Changed
- Harness research applied: NLAH v2 numbers, the authority rule for ingested text, frozen safety text.
- 14 citations corrected against the papers (3 wrong, 11 simplified).
- README and harness card refreshed; Lean Service Creation skills carry their CC BY-SA 4.0 licence (`NOTICE`).
- `linkedin-viral-scheduler` description shortened to the Agent Skills spec limit.

### Fixed
- Vault links repaired at the scripts that generate them.
- The outbound gate catches short account names; the skill router counts skills only.
- 21 lint findings (unused code, bare excepts, a late import), with no behaviour change.

[Unreleased]: https://github.com/pantheonzeus/charness/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/pantheonzeus/charness/releases/tag/v0.1.0
