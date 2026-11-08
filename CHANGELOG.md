# Changelog

Notable changes to charness. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow
[Semantic Versioning](https://semver.org/). Pushing a `v*` tag publishes that version's section below as the
GitHub release (`.github/workflows/release.yml`); the release fails if the section is missing.

## [Unreleased]

### Added
- **Console: a quick voice in front.** A warm Haiku session says in a few words what is being done with the
  question at about +1.3 s, while the main session thinks (`webapp/foreground.py`).
- **Output-quality judge.** `run-forensics/scripts/judge.py` grades daily-intel briefing items against rules
  quoted from that job's skill. It flags nothing until it agrees with the principal's own labels (TPR and
  TNR ≥ 0.8 on ≥ 10 pass and 10 fail labels); not yet calibrated.
- **Repeated-research report.** `quality.py` reports, per job and model, research a run repeated for nothing.
  Report-only.

### Fixed
- **Commit guard** accepts GitHub's merge button as committer, so UI merges no longer fail CI on `main`.

## [0.1.1] — 2026-11-08

The documentation site.

### Added
- **Documentation site** at `pantheonzeus.github.io/charness`: landing page, guides, concepts, governance and a
  skill catalog generated from `INDEX.md` at build time. Material for MkDocs, pinned and locked in `docs/`;
  `.github/workflows/pages.yml` builds it with `--strict` on pull requests and deploys it from `main`.

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
- README opens with what you get and a four-line quickstart.
- README and harness card refreshed; Lean Service Creation skills carry their CC BY-SA 4.0 licence (`NOTICE`).
- `linkedin-viral-scheduler` description shortened to the Agent Skills spec limit.

### Fixed
- Vault links repaired at the scripts that generate them.
- The outbound gate catches short account names; the skill router counts skills only.
- 21 lint findings (unused code, bare excepts, a late import), with no behaviour change.

[Unreleased]: https://github.com/pantheonzeus/charness/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/pantheonzeus/charness/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/pantheonzeus/charness/releases/tag/v0.1.0
