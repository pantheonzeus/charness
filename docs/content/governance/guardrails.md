# Guardrails

The rules that must hold are enforced by hooks and git hooks, not by the prompt. Each guard has its own test suite under [`.claude/hooks/tests/`](gh:.claude/hooks/tests/), and `scripts/check.sh` runs all {{ hook_suites_count }} suites in CI on every push and pull request.

## Fail-open vs fail-closed

| Mode | Meaning | Used for |
|---|---|---|
| **Fail-open** | An error inside the guard lets the action through. | Guards on reversible actions: a hook bug never stalls real work. |
| **Fail-closed** | An error inside the guard blocks the action. | The send gate: a sent message can't be recalled. |

## The guards

### Write boundary

[`write-boundary.sh`](gh:.claude/hooks/write-boundary.sh) runs before Write, Edit, MultiEdit and NotebookEdit.

- **Interactive sessions** may write inside the repo, the session scratchpad and `~/.claude`. Targets are resolved through `..` segments and symlinks before the check.
- **Headless jobs** (`CBRAIN_JOB` set by the runner) may write only inside the `write_scopes:` of their agent file. A scheduled agent can't touch vault notes outside its lane.
- **Fail-open.**

### Egress guard

[`egress-guard.sh`](gh:.claude/hooks/egress-guard.sh) runs before WebFetch and WebSearch. It denies a call whose URL or query carries an exfiltration shape: an email address (other than the principal's public one), an encoded blob, or an oversized query string. Data doesn't leave the machine inside a search. **Fail-open.**

### Send gate

[`send-gate.sh`](gh:.claude/hooks/send-gate.sh) → `send_gate.py` runs before any MCP tool whose name contains `send`. It requires both:

1. The latest human message is an explicit "send", after a read-back that names every recipient.
2. The draft passes [`scripts/outbound_gate.py`](gh:scripts/outbound_gate.py), a deterministic scan for other clients' names, third-party contacts and internal channel names.

**Fail-closed.**

### Commit guard

[`scripts/commit_guard.py`](gh:scripts/commit_guard.py) runs as git hooks (`pre-commit`, `commit-msg`, `pre-push`), installed once per clone with `git config core.hooksPath scripts/git-hooks`. It blocks:

- secrets, personal data and client names in added lines and commit messages;
- force-added ignored files (the vault, `output/`, `IDENTITY.md`, employer packs);
- force pushes, branch deletions and co-author trailers.

A Claude Code Bash hook denies the ways around it: `--no-verify`, redirecting `core.hooksPath`, force pushes. CI runs the guard again over pushed commits, because local hooks can be skipped and CI can't.

### Provenance labels

`scripts/ingest_lint.py hook` runs after vault writes. It decides from the transcript whether outside text came in, and labels the note. [Untrusted ingest →](untrusted-ingest.md)

### Control-spine gate

[`control-spine-gate.sh`](gh:.claude/hooks/control-spine-gate.sh) runs at Stop. It blocks the end of a run while a `RESPONSE.md` that this session touched has open `[ ]` checkpoints. It respects `stop_hook_active`, so it never loops. **Fail-open.**

### Graph gate

`link_audit.sh` fails a NotebookLM import if the new source note doesn't reach a topic anchor. No islands in the knowledge graph. It also runs as a daily sweep.

## Headless-only controls

| Control | Where | Effect |
|---|---|---|
| Budget cap | `budget_usd:` in the agent file | `--max-budget-usd` on every run |
| Bash sandbox | `sandbox: true` | Writes only in the repo, network only to PyPI |
| Code mode | `code_mode: true` | Sandbox forced; Bash writes to the vault and the harness denied at OS level |
| Typed vault writer | `scripts/vault_api.py` | Bash-run vault writes keep the job's scopes and provenance; all-or-nothing |
| Circuit breaker | `run_agent.sh` | All jobs stop after three API-pressure failures |

## Run the tests

```bash
scripts/check.sh                                    # everything, as CI runs it
bash .claude/hooks/tests/write-boundary.test.sh     # one suite
```
