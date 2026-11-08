# Contributing to charness

Thanks for your interest. charness is a **natural-language agent harness** for Claude Code:
it keeps **policy separate from mechanism** across four layers. Before contributing, know
which layer you're touching — that decides the rules that apply.

| Layer | Where | What it is | Changes |
|---|---|---|---|
| **Backend (mechanism)** | `.claude/` hooks, per-skill `scripts/` | Deterministic code | Rarely |
| **Runtime Charter** | [`Charter.md`](Charter.md) | Universal run-level physics | Rarely |
| **Identity (voice)** | [`Soul.md`](Soul.md) + `IDENTITY.example.md` | Voice mechanics + persona | Rarely |
| **Skill library (task logic)** | `resources/skills/` | One editable policy doc per task | Often |

Most contributions are **skills**. Start there.

## Ground rules (read once)

- **Never commit personal data.** `cbrain/` (the Obsidian vault), `output/`, `input/`, and
  `IDENTITY.md` are gitignored and stay that way. Put your persona in a local `IDENTITY.md`
  (copied from `IDENTITY.example.md`); only ever edit and commit the **`.example`** template.
  If you add real operational data, add its path to `.gitignore` and ship a `*.example` instead.
- **Policy is prose, mechanism is code.** Don't encode task logic in a hook, and don't put
  deterministic mechanism in a skill body. Keep the boundary clean.
- **Match the surrounding style.** Surgical diffs — every changed line should trace to the
  change you're making. Don't refactor adjacent code you didn't need to touch.
- **Be a good citizen.** By participating you agree to the [Code of Conduct](CODE_OF_CONDUCT.md).

## Adding or changing a skill

The full contract is [`resources/skills/README.md`](resources/skills/README.md). In short:

1. **Copy the template.** `resources/skills/_template/SKILL.md` → `<category>/<skill-slug>/SKILL.md`
   (kebab-case slug = folder name). Categories: `knowledge-graph`, `research`, `sales`,
   `content`, `workflow-ops`, `vault-hygiene`.
2. **Fill the frontmatter** per the schema (`id`, `name`, `category`, `description`, `triggers`,
   `status`, `version`, `created`, `updated`, plus optional keys only when the skill needs them).
3. **Open the body with a Contract block** — input · output (+ where it lands) · allowed
   tools/artifacts · the observable *done-when* condition. Then `Triggers/Context`,
   `Core Blueprint`, `Optimizations/Gotchas` for simple skills.
4. **Update `INDEX.md` in the same change.** This is non-negotiable: `INDEX.md` is the lookup
   source of truth, and a skill missing from it is invisible. Add the row **and** bump the
   `Skills: N` count in the header.
5. **Cross-link** related skills via the `related:` frontmatter key (use the other skill's `id`).
6. **Bump `version` + `updated`** on every optimization of an existing skill. Push overflow
   detail into a `references/` file rather than bloating the body.

### Write enforceable language, not exhortations

Skills are policy that an agent executes literally. Prefer concrete clauses naming an artifact
or check over vague advice:

- ✗ "be careful with sources" → ✓ "cite the source file for every numeric claim"
- ✗ "verify thoroughly" → ✓ "run the verifier before finalizing and record its verdict"

Phrases like "think deeply" or "act like an expert" define no observable behavior — replace them.

### Script-backed skills

Import scripts by **copying the folder verbatim** (`cp -R`, preserves the executable bit) so the
code and the SKILL.md's relative paths stay intact — never retype scripts. Scripts should be
stdlib-first, idempotent, and print a clear one-line summary of what they did (and what they
skipped, so scope drift is visible).

## Changing the Charter, Soul, `_shared/`, or a skill's core Blueprint

These are harness-level edits. In addition to the change itself, **log a change-manifest entry**
in [`resources/skills/_shared/CHANGE_LOG.md`](resources/skills/_shared/CHANGE_LOG.md): the trigger,
files touched, what you expect it to fix, the risk you're flagging, and a `Verdict: pending`. The
prediction is checked against the edit's next real use — that's how we tell whether a harness
change actually helped instead of just felt better.

## Changing hooks (`.claude/`)

Hooks are the un-bypassable mechanism, so treat them conservatively:

- **Fail open.** Any parse error, missing input, or unexpected shape must `exit 0` (allow) — a
  hook must never block real work because its own parsing choked. Follow the pattern in the
  existing `write-boundary.sh` / `control-spine-gate.sh`.
- **Test both paths** before committing (see below).

## Verifying your change

Run `scripts/check.sh` before you push: hook tests, skill lints, ruff and shellcheck. CI runs the same
script on every push to `main` and every pull request; a red check blocks the merge.

- **Hooks:** feed them sample JSON and check the decision, e.g.
  ```bash
  echo '{"tool_input":{"file_path":"/etc/passwd"}}' | bash .claude/hooks/write-boundary.sh   # expect: deny
  echo '{"tool_input":{"file_path":"./output/x.md"}}' | bash .claude/hooks/write-boundary.sh  # expect: empty (allow)
  ```
- **Skill scripts:** run with `--dry-run` first where supported; confirm idempotency (a second
  run reports zero changes).
- **INDEX integrity:** the `Skills: N` header must equal the number of `SKILL.md` files under
  `resources/skills/` excluding `_template/`.

## Commits & pull requests

- **Conventional-commit subjects** (`feat(skills): …`, `fix: …`, `docs: …`), imperative mood.
- **One logical change per commit.** A bugfix and a new skill are two commits, not one.
- **PRs** state what changed, which layer, and how you verified it. Link the skill path.
- Keep gitignored personal artifacts out of the diff — check `git status` before you commit.
- **`main` is protected** by [`.github/rulesets/main.json`](.github/rulesets/main.json): no deletion, no force
  push, and the CI `check` job must pass. Repository admins can bypass it; GitHub logs each bypass.

Questions or a design you're unsure about? Open an issue first and describe the outcome you want,
not just the code — this repo leads with the problem, then the mechanism.
