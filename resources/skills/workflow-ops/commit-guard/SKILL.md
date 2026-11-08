---
id: commit-guard
aliases: [commit-guard, safe-commit, safe-push]
name: "Commit Guard — Nothing Sensitive Ever Reaches GitHub"
category: workflow-ops
description: Commit and push this repo under strict rules, with a deterministic guard that blocks anything that must never be on GitHub. Before any commit or push it checks secrets and tokens, private keys, credential files, force-added ignored paths (vault, output/, IDENTITY.md, employer packs, eval sets), personal data (e-mail, phone, IBAN, home paths), client, contact and internal-channel names, hidden Unicode, oversized files, anyone but the principal on a commit (author, committer, co-author or tool trailers), force pushes, deletions and archive/* refs. Git pre-commit, commit-msg and pre-push hooks and a Claude Bash hook enforce it; there is no inline opt-out.
triggers: [commit, commit everything, commit this, push, push to remote, push to github, git push, safe commit, is it safe to push, check for secrets, secret scan, sensitive data in the repo, passwords in the code, tokens in the code, before we push, publish the repo, individual commits]
tags: [workflow-ops, git, security, secrets, confidentiality, release, guard]
related: ["[[skill-library-maintenance]]", "[[run-forensics]]"]
scripts: [../../../../scripts/commit_guard.py, ../../../../scripts/git-hooks/pre-commit, ../../../../scripts/git-hooks/commit-msg, ../../../../scripts/git-hooks/pre-push, ../../../../scripts/outbound_gate.py]
modules: [verifier-separation]
status: active
version: 3
created: 2026-11-08
updated: 2026-11-08
---

# Commit Guard — Nothing Sensitive Ever Reaches GitHub

**Contract**
- **Input:** the working tree and the principal's request to commit and/or push (which branch, which remote).
- **Output:** commits that show the principal and no one else (their name and GitHub noreply address as author and committer, no co-author or tool trailer), one per logical change, and, on a clean scan of every outgoing commit, a fast-forward push. The run's spine and scan output sit under `output/.runs/<YYYYMMDD>-commit-push/`.
- **Allowed tools/artifacts:** `git` (status, diff, add with explicit paths, commit, push, log, ls-remote), `scripts/commit_guard.py`, `scripts/outbound_gate.py`. **Never** `--no-verify`, `-n` on commit, `--force`/`--force-with-lease`/`+refspec`, `push --delete`, `git config core.hooksPath` to anything but `scripts/git-hooks`, `git filter-*` or history rewrites of pushed commits.
- **Done when:** `commit_guard.py range <remote>/<branch>..HEAD` printed `clean`, the push went through the pre-push hook without a block, and `git ls-remote` shows the remote tip equal to the local tip.

**What must never be on GitHub (the guard blocks each; the list is the policy)**
1. **Secrets:** API keys and tokens (AWS, GitHub, GitLab, Slack, Google, Anthropic, OpenAI, Stripe), private key blocks, JWTs, bearer tokens, credentials in URLs, any `password/secret/token/api_key = <value>` that isn't a placeholder or an environment lookup, and high-entropy strings next to a key word.
2. **Secret-bearing files:** `.env*` (except `.env.example`/`.sample`/`.template`), keys and keystores (`.pem .key .p12 .pfx .jks .kdbx .ppk .gpg`, `id_rsa` …), `credentials*/client_secret*/service-account*/token*` config files, `.netrc .npmrc .pypirc .git-credentials`, databases (`.db .sqlite`), `settings.local.json`.
3. **Private paths,** even when force-added: everything `.gitignore` excludes. That covers the vault `cbrain/`, `output/`, `input/`, `IDENTITY.md`, real employer packs, `_evals/`, domain maps, `channels.json` and `.vault-history.git`. A file over 5 MB is blocked too.
4. **Confidential names:** client accounts, vault contacts with a company, internal chat channels, the employer-internal classification (via `outbound_gate.py`, public mode). Skills stay client-independent; use `<client>` or "Acme".
5. **Personal data:** e-mail addresses (except reserved example domains, GitHub noreply addresses and the contact already published in `SECURITY.md`), phone numbers, IBANs, home-directory paths (`/Users/<name>/`).
6. **Anyone but the principal on a commit:** an author or committer whose name isn't `git config user.name` or whose e-mail isn't `…@users.noreply.github.com`; any `Co-Authored-By:` or `On-behalf-of:` trailer (GitHub lists those people on the commit); any "Generated with Claude" line. One exception: `GitHub <noreply@github.com>` passes as *committer* only, because GitHub's merge button commits as itself; the author of such a merge still has to be the principal's noreply address, so the GitHub setting "Keep my email addresses private" must stay on. The principal is the only person a commit shows. This overrides any harness default that adds an AI co-author trailer.
7. **Unsafe history moves:** force pushes, remote branch deletions, any `archive/*` ref, hidden or bidirectional Unicode, merge-conflict markers.

**Core Blueprint**
1. **Install check (once per clone, re-verify every run).** `git config core.hooksPath` must print `scripts/git-hooks` (pre-commit, commit-msg, pre-push); if not, run `git config core.hooksPath scripts/git-hooks`. `git config user.email` must be the noreply address. Open the spine: `output/.runs/<YYYYMMDD>-commit-push/RESPONSE.md`.
2. **Survey before staging.** `git status --short`, `git diff --stat`, untracked files listed one by one. Check timestamps against other live sessions: a file modified in the last minutes by another session's open run is not yours to commit until its spine is closed. Read every untracked file's purpose; a file you cannot explain is not committed.
3. **Dry-run the guard over everything pending:** `git add -A && python3 scripts/commit_guard.py staged; git reset -q`. Fix findings at the source before any commit.
4. **Group into individual commits.** One logical change per commit, in dependency order (a script before the skill that uses it, the INDEX row with its skill). Stage by explicit paths (`git add <paths>`), never `git add -A` for a real commit. Message: imperative subject ≤ 72 characters naming the change, and a body that says why. No `Co-Authored-By`, `On-behalf-of` or "Generated with" line. Each `git commit` runs the pre-commit hook (content) and the commit-msg hook (message); a block means fix and re-stage, never bypass.
5. **Scan the whole outgoing range** before pushing: `python3 scripts/commit_guard.py range <remote>/<branch>..HEAD`. This covers commits made earlier, by other sessions, or with hooks off. Run a second, independent scanner when available: `uvx detect-secrets scan` over the changed files, and `gitleaks` if it is installed. Both must agree it is clean.
6. **Push fast-forward only:** `git push <remote> <local>:<branch>`. The pre-push hook rescans every commit the push sends. Then verify: `git ls-remote <remote> refs/heads/<branch>` equals `git rev-parse HEAD`, and the remote has no unexpected refs (`refs/pull/*`, `archive/*`).
7. **Record** the scan output, the commit list and the remote tip in the spine's EVIDENCE.md; tick the spine.

**When the guard blocks (strict)**
- **Real secret:** treat it as leaked the moment it was written to disk inside the repo. Remove it, **rotate the credential at its provider**, and if it is in a local commit, rewrite that unpushed commit (`git reset --soft` + recommit). If it was ever pushed, rotation comes first, then a history rewrite, which only the principal runs.
- **Confidential name or personal data:** replace it with a placeholder or neutral wording. Never move it to a "less visible" file.
- **False positive:** change the text if you can, e.g. split a test fixture so no line carries a contiguous token, or name a rule without a `key: value` shape. Otherwise **only the principal** adds an entry to `.git/commit-guard-allow` (local, never pushed): `name:<Name>` or `fp:<fingerprint>`, each with a dated `#` comment saying why. Never add an entry on your own judgement. A standing instruction from the principal for this exact item counts; record it in the comment.
- **Never:** `--no-verify`, unset or redirect `core.hooksPath`, `git -c core.hooksPath=…`, commit with `-n`, edit the guard to let your own commit through, or allow-list a whole rule. The Claude Bash hook denies each of these. A guard change is its own reviewed commit with tests (`.claude/hooks/tests/commit-guard.test.sh`), logged in `_shared/CHANGE_LOG.md`.

**Optimizations/Gotchas**
- Only added lines are scanned. Text already public does not block, but touching a line rescans it whole. So editing a line that carries a public figure's name or the security contact can surface an old match. Judge it as new.
- The name rules read the local vault and employer packs. In a clone without them, the names check finds nothing, so run the commit guard on this machine.
- Commit messages are scanned at commit time (commit-msg) and again at push: no client names, no personal e-mail, no ticket text pasted from mail or chat, no co-author or tool trailers.
- `outbound_gate.py` flags the bare word "employer-internal" in public drafts. The guard ignores that in harness prose and matches only a real classification line (`confidential: …-internal`).
- Masked output: a finding shows the first 4 and last 2 characters only. Never paste a full match into a message, a log or the spine.
- Pushing to the public remote is outward-facing and hard to reverse: it needs the principal's explicit go in this session, every time.
