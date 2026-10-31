# Security Policy

charness is an agent harness: it runs hooks, executes skill scripts, and mediates tool
access for an autonomous agent. Its security surface is therefore about **containment and
trust boundaries**, not a shipped binary. Reports about the following are in scope:

- **A hook that fails to enforce its boundary** — e.g. `write-boundary.sh` allowing a write
  outside the permitted zones, or `control-spine-gate.sh` letting a run stop with unmet gates.
- **Command / path injection in a skill script** — untrusted input reaching a shell, an
  unbounded file write, or an escape from the intended directory.
- **Prompt-injection surface** — a place where ingested content (email, web page, calendar
  entry, PDF, tool output) could be executed as instructions rather than treated as data.
- **Accidental exposure of private data** — a code path that could commit or transmit
  `cbrain/`, `output/`, `input/`, or `IDENTITY.md` contents.

Out of scope: issues in Claude Code itself (report those to Anthropic), and behavior that
requires the user to have already granted the agent unrestricted permissions on purpose.

## Reporting a vulnerability

**Do not open a public issue for a security problem.** Use one of:

1. **GitHub private advisory** (preferred) — the repo's
   **Security → Report a vulnerability** page:
   https://github.com/pantheonzeus/charness/security/advisories/new
2. **Email** — `christoph.nuetzel@gmail.com` with `SECURITY` in the subject.

Please include: the file or hook involved, a minimal reproduction, and the impact
(what boundary is crossed). If you have a fix in mind, say so — but a clear report is
enough.

## What to expect

This is a personal project maintained on a best-effort basis, not a product with an SLA.
That said:

- **Acknowledgement** within a few days.
- **An assessment** (accepted / needs-info / out-of-scope) once reproduced.
- **A fix on `main`** for accepted issues, with credit in the commit unless you prefer to
  stay anonymous. There are no versioned releases — `main` is the supported line.

Thanks for reporting responsibly.
