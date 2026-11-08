#!/usr/bin/env python3
"""Commit guard: nothing that must never be on GitHub enters a commit or leaves in a push.

Scans what a commit adds (staged mode) or every commit a push sends (push/range mode) and blocks on any of:
  path      a force-added gitignored file (vault, output/, IDENTITY.md, employer packs, eval sets …), a secret-bearing
            file type (.env, keys, keystores, credential/token JSON, databases, .netrc …), a file over 5 MB
  secret    provider tokens (AWS, GitHub, GitLab, Slack, Google, Anthropic, OpenAI, Stripe), private key blocks, JWTs,
            credentials in URLs, bearer tokens, password/secret/token assignments, high-entropy strings next to a key word
  personal  e-mail addresses (reserved example domains, GitHub noreply addresses and SECURITY.md's contact excepted),
            phone numbers, IBANs, home-directory paths
  names     client accounts, vault contacts with a company, internal chat channels, the employer-internal tag
            (scripts/outbound_gate.py, public mode)
  unicode   bidirectional controls and zero-width characters (Trojan Source)
  conflict  leftover merge-conflict markers
  identity  author or committer other than the principal (git config user.name, a GitHub noreply address), and any
            Co-Authored-By / On-behalf-of trailer or "Generated with Claude" line: the principal is the only person shown
  push      a force push (remote tip not an ancestor), a branch deletion, any archive/* ref

Only ADDED lines are scanned, so text already public does not block; a line that is touched is scanned again.
Matches are printed masked. There is no inline opt-out. The one exception channel is the local, never-pushed file
.git/commit-guard-allow, which only the principal edits: one entry per line, `name:<Account>` (the gate's allow) or
`fp:<fingerprint>` (one exact finding, fingerprint printed with it).

  python3 scripts/commit_guard.py staged                      pre-commit hook
  python3 scripts/commit_guard.py message <file>              commit-msg hook
  python3 scripts/commit_guard.py push <remote> [url] < refs  pre-push hook (git passes the ref lines on stdin)
  python3 scripts/commit_guard.py range <base>..<head>        any range by hand
  python3 scripts/commit_guard.py hook                        Claude PreToolUse on Bash (JSON on stdin)
Install the git hooks once per clone: git config core.hooksPath scripts/git-hooks
Exit 0 clean, 1 findings, 2 error (the hooks block on anything but 0). Stdlib only.
"""
import functools
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import outbound_gate as gate  # noqa: E402

MAX_BYTES = 5 * 1024 * 1024
ZERO = "0" * 40
NOREPLY = re.compile(r"@users\.noreply\.github\.com$", re.I)
SOLE = re.compile(r"(?im)^[ \t]*(co-authored-by|on-behalf-of)[ \t]*:.*$|^.*generated (with|by) \[?claude.*$")

SECRET_FILE = re.compile(
    r"(^|/)(\.env(\.(?!example$|sample$|template$)[^/]+)?|\.netrc|\.npmrc|\.pypirc|\.git-credentials|\.htpasswd|"
    r"id_(rsa|dsa|ecdsa|ed25519)(\.pub)?|settings\.local\.json|"
    r"[^/]*\.(pem|key|p12|pfx|jks|keystore|kdbx|ovpn|ppk|gpg|sqlite3?|db)|"
    r"(?![^/]*\.example\.)[^/]*(credential|client_secret|service[-_]account|secret|token)[^/]*\.(json|ya?ml|toml|ini|txt))$", re.I)

SECRETS = [
    ("aws-access-key", r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("github-token", r"\b(gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,})"),
    ("gitlab-token", r"\bglpat-[A-Za-z0-9_-]{20,}"),
    ("slack-token", r"\bxox[abposr]-[A-Za-z0-9-]{10,}"),
    ("slack-webhook", r"hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[A-Za-z0-9]+"),
    ("google-api-key", r"\bAIza[0-9A-Za-z_-]{35}"),
    ("google-oauth-secret", r"\bGOCSPX-[A-Za-z0-9_-]{20,}"),
    ("google-token", r"\b(ya29\.[A-Za-z0-9_-]{20,}|1//0[A-Za-z0-9_-]{30,})"),
    ("anthropic-key", r"\bsk-ant-[A-Za-z0-9_-]{20,}"),
    ("openai-key", r"\bsk-(proj-|svcacct-)?[A-Za-z0-9_-]{32,}"),
    ("stripe-key", r"\b[rs]k_live_[A-Za-z0-9]{20,}"),
    ("private-key", r"-{5}BEGIN [A-Z ]*PRIVATE KEY( BLOCK)?-{5}"),
    ("jwt", r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    ("url-credentials", r"\b[a-z][a-z0-9+.-]*://[^/\s:@'\"]+:[^/\s@'\"]{3,}@[A-Za-z0-9.-]+"),
    ("bearer-token", r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{20,}=*"),
    ("secret-assignment", r"(?i)\b[A-Za-z0-9_]*(password|passwd|pwd|secret|api[_-]?key|access[_-]?key|auth[_-]?token|"
                          r"token|client[_-]?secret|private[_-]?key)[A-Za-z0-9_]*\b(?:['\"]?\s*=\s*|['\"]\s*:\s*|\s*:\s+)['\"]?([^\s'\",;)}]{8,})"),
]
SECRETS = [(n, re.compile(p)) for n, p in SECRETS]
PLACEHOLDER = re.compile(r"[<>{}$*]|\.\.\.|example|sample|changeme|change_me|dummy|placeholder|your[_-]|xxxx|redacted|"
                         r"os\.environ|getenv|process\.env|env\[|none|null|true|false|\(|^[a-z_]+\.[a-z_]+$", re.I)
KEYWORD = re.compile(r"(?i)key|token|secret|password|passwd|auth|credential|bearer|cookie|session")
ENTROPY_TOKEN = re.compile(r"[A-Za-z0-9+/=_-]{32,}")

EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
RESERVED = re.compile(r"@([A-Za-z0-9-]+\.)*(example\.(com|org|net)|[A-Za-z0-9-]+\.(example|test|invalid|localhost|local))$"
                      r"|@users\.noreply\.github\.com$", re.I)
PHONE = re.compile(r"(?<![\w.+-])\+\d{1,3}[ -]?\(?\d{2,5}\)?(?:[ -]?\d{2,5}){2,4}(?![\w-])")
IBAN = re.compile(r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}(?: ?[A-Z0-9]{1,3})?\b")
HOME = re.compile(r"(/Users|/home)/(?!(<|\$|you\b|me\b|user\b|username\b|example|runner\b|shared\b))[A-Za-z0-9._-]+/")
UNICODE = re.compile("[\u202a-\u202e\u2066-\u2069\u200b-\u200d\u2060\ufeff]")
CONFLICT = re.compile(r"^(<{7}|>{7}) ")
TAG = re.compile(r"(?im)^\s*(confidential|class|classification):\s*\S*-internal\b")


def git(*args, check=True):
    r = subprocess.run(["git", *args], capture_output=True, text=True, errors="replace")
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def allow_list():
    try:
        p = Path(git("rev-parse", "--git-common-dir").strip()) / "commit-guard-allow"
        lines = [l.strip() for l in p.read_text().splitlines() if l.strip() and not l.startswith("#")]
    except (OSError, RuntimeError):
        lines = []
    return {l[5:] for l in lines if l.startswith("name:")}, {l[3:] for l in lines if l.startswith("fp:")}


@functools.lru_cache(None)
def public_contacts():
    try:
        text = git("show", "HEAD:SECURITY.md", check=False)
    except RuntimeError:
        text = ""
    return {e.lower() for e in EMAIL.findall(text)}


def mask(s):
    s = s.strip()
    return s if len(s) <= 8 else s[:4] + "*" * min(len(s) - 6, 12) + s[-2:]


def entropy(s):
    return -sum(c / len(s) * math.log2(c / len(s)) for c in (s.count(ch) for ch in set(s)))


class Scan:
    def __init__(self):
        self.findings, (self.allowed_names, self.allowed_fp) = [], allow_list()
        gate.vault_names = functools.lru_cache(None)(gate.vault_names)
        gate.channels = functools.lru_cache(None)(gate.channels)

    def add(self, where, rule, match=""):
        fp = hashlib.sha256(f"{where.split(':')[0]}|{rule}|{match}".encode()).hexdigest()[:12]
        if fp not in self.allowed_fp:
            self.findings.append(f"{where}  [{rule}]  {mask(match) if match else ''}  (fp:{fp})")

    def path(self, where, path, size):
        if subprocess.run(["git", "check-ignore", "-q", "--no-index", path]).returncode == 0:
            self.add(where, "path:gitignored", path)
        if SECRET_FILE.search(path):
            self.add(where, "path:secret-file", path)
        if size and size > MAX_BYTES:
            self.add(where, "path:over-5MB", f"{size} bytes")

    def line(self, where, text):
        for name, rx in SECRETS:
            for m in rx.finditer(text):
                value = m.group(m.lastindex) if name == "secret-assignment" else m.group(0)
                if name in ("secret-assignment", "url-credentials", "bearer-token") and PLACEHOLDER.search(value):
                    continue
                self.add(where, f"secret:{name}", m.group(0))
        if KEYWORD.search(text):
            for t in ENTROPY_TOKEN.findall(text):
                # mixed case + digit, judged per path segment: run paths like output/.runs/2026…-slug/ are not keys
                for seg in [s for s in t.split("/") if len(s) >= 20] if "/" in t else [t]:
                    if entropy(seg) >= 4.3 and re.search(r"\d", seg) and re.search(r"[a-z]", seg) \
                            and re.search(r"[A-Z]", seg) and not PLACEHOLDER.search(seg):
                        self.add(where, "secret:high-entropy", t)
                        break
        for e in EMAIL.findall(text):
            if not RESERVED.search(e) and e.lower() not in public_contacts():
                self.add(where, "personal:email", e)
        for rule, rx in (("personal:phone", PHONE), ("personal:iban", IBAN), ("personal:home-path", HOME)):
            for m in rx.finditer(text):
                self.add(where, rule, m.group(0))
        if UNICODE.search(text):
            self.add(where, "unicode:hidden-or-bidi", repr(UNICODE.search(text).group(0)))
        if CONFLICT.match(text):
            self.add(where, "conflict-marker", text[:12])

    def names(self, where, text):
        for f in gate.scan(text, public=True, allow=tuple(self.allowed_names)):
            if f != "carries an employer-internal tag":   # the gate's bare-word rule fires on policy prose
                self.add(where, "names", f)
        if TAG.search(text):
            self.add(where, "names", "employer-internal classification tag")

    def identity(self, where, email, name=None):
        if not NOREPLY.search(email.strip()):
            self.add(where, "identity:not-noreply", email.strip())
        expected = git("config", "user.name", check=False).strip()
        if name is not None and expected and name.strip() != expected:
            self.add(where, "identity:not-the-principal", name.strip())

    def message(self, where, msg):
        """The principal is the only person on a commit: no co-author or tool trailers; plus every content rule."""
        for m in SOLE.finditer(msg):
            self.add(where, "identity:co-author-or-tool-trailer", m.group(0))
        for i, l in enumerate(msg.splitlines(), 1):
            self.line(f"{where}:{i}", l)
        self.names(where, msg)

    def diff(self, label, patch, sizes):
        """Unified diff with -U0: scan every added line, file by file."""
        path, lineno, added = None, 0, []
        for raw in patch.splitlines() + ["diff --git END"]:
            if raw.startswith("diff --git "):
                if path and added:
                    self.names(f"{label}{path}", "\n".join(t for _, t in added))
                path, added = None, []
            elif raw.startswith("+++ "):
                path = None if raw[4:] == "/dev/null" else raw[6:] if raw.startswith("+++ b/") else raw[4:]
                if path:
                    self.path(f"{label}{path}", path, sizes.get(path))
            elif raw.startswith("@@"):
                m = re.search(r"\+(\d+)", raw)
                lineno = int(m.group(1)) if m else 0
            elif raw.startswith("Binary files") and " and b/" in raw:
                p = raw.split(" and b/", 1)[1].rsplit(" differ", 1)[0]
                self.path(f"{label}{p}", p, sizes.get(p))
            elif raw.startswith("+") and path:
                self.line(f"{label}{path}:{lineno}", raw[1:])
                added.append((lineno, raw[1:]))
                lineno += 1

    def commit(self, sha):
        meta = git("show", "-s", "--format=%ae%n%ce%n%an%n%cn%n%B", sha).split("\n", 4)
        short = sha[:9]
        self.identity(f"{short} author", meta[0], meta[2])
        self.identity(f"{short} committer", meta[1], meta[3])
        self.message(f"{short} message", meta[4] if len(meta) > 4 else "")
        sizes = {}
        for l in git("ls-tree", "-r", "-l", sha).splitlines():
            meta_, p = l.split("\t", 1)
            s = meta_.split()[3]
            sizes[p] = int(s) if s.isdigit() else 0
        changed = git("diff-tree", "--no-commit-id", "-r", "--root", "--diff-filter=ACMRT", "--name-only", sha).split("\n")
        self.diff(f"{short} ", git("diff-tree", "--no-commit-id", "-r", "--root", "-p", "-U0", "--no-color",
                                   "--no-ext-diff", "--diff-filter=ACMRT", sha), {p: sizes.get(p, 0) for p in changed if p})

    def report(self):
        for f in self.findings:
            print(f"BLOCK {f}", file=sys.stderr)
        if self.findings:
            print(f"commit-guard: {len(self.findings)} finding(s). Remove the content (rotate any real secret: treat it as "
                  "leaked). Never bypass with --no-verify. A true false positive goes to .git/commit-guard-allow, by the "
                  "principal only.", file=sys.stderr)
        else:
            print("commit-guard: clean", file=sys.stderr)
        return 1 if self.findings else 0


def staged():
    s = Scan()
    for var in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT"):
        m = re.match(r"(.*?) <([^>]*)>", git("var", var))
        s.identity(f"staged {var[4:-6].lower()}", m.group(2), m.group(1))
    sizes = {}
    for p in git("diff", "--cached", "--name-only", "--diff-filter=ACMRT").splitlines():
        out = git("cat-file", "-s", f":{p}", check=False).strip()
        sizes[p] = int(out) if out.isdigit() else 0
    s.diff("", git("diff", "--cached", "-U0", "--no-color", "--no-ext-diff", "--diff-filter=ACMRT"), sizes)
    return s.report()


def message(path):
    """commit-msg hook: the message as git will store it (comment lines dropped)."""
    s = Scan()
    s.message("message", "\n".join(l for l in Path(path).read_text(errors="replace").splitlines() if not l.startswith("#")))
    return s.report()


def commits(rng):
    return [c for c in git("rev-list", "--reverse", *rng).split() if c]


def push(argv):
    remote = argv[0] if argv else "origin"
    s = Scan()
    for line in sys.stdin.read().splitlines():
        parts = line.split()
        if len(parts) != 4:
            continue
        lref, lsha, rref, rsha = parts
        if "archive/" in lref or "archive/" in rref:
            s.add(rref, "push:archive-ref", lref)
            continue
        if lsha == ZERO:
            s.add(rref, "push:branch-deletion", rref)
            continue
        if rsha != ZERO:
            if subprocess.run(["git", "merge-base", "--is-ancestor", rsha, lsha]).returncode != 0:
                s.add(rref, "push:force (remote tip is not an ancestor)", rsha[:9])
                continue
            rng = [f"{rsha}..{lsha}"]
        else:
            rng = [lsha, "--not", f"--remotes={remote}"]
        for c in commits(rng):
            s.commit(c)
    return s.report()


def rng(spec):
    s = Scan()
    for c in commits([spec]):
        s.commit(c)
    return s.report()


GIT_CMD = re.compile(r"(?:^|[;&|(]\s*|\b(?:then|do|xargs)\s+)git\b(?P<rest>[^;&|]*)")


def hook():
    """Claude PreToolUse on Bash: refuse ways around the git hooks."""
    try:
        cmd = json.loads(sys.stdin.read() or "{}").get("tool_input", {}).get("command", "")
    except ValueError:
        cmd = None
    reason = None
    if cmd is None:
        reason = "unreadable hook input"
    else:
        for m in GIT_CMD.finditer(cmd):
            rest = m.group("rest")
            if re.search(r"(^|\s)--no-verify\b", rest) or re.search(r"\bcommit\b.*\s-[a-zA-Z]*n[a-zA-Z]*\b", rest):
                reason = "--no-verify skips the commit guard"
            elif re.search(r"(\bconfig\b[^;&|]*?|(^|\s)-c\s*)core\.hookspath", rest, re.I) and not re.search(r"--get\b", rest) \
                    and not re.search(r"\bconfig\s+(--local\s+)?core\.hookspath\s+scripts/git-hooks/?(?=[\s`'\");]|$)", rest, re.I):
                reason = "changing core.hooksPath disables the commit guard"
            elif re.search(r"\bpush\b", rest) and (re.search(r"\s(--force\b|--force-with-lease\b|-[a-zA-Z]*f\b|\+\S)", rest)
                                                 or re.search(r"\s--delete\b|\s:\S", rest)):
                reason = "force push or remote deletion: the principal runs it by hand, after reading what it overwrites"
            elif re.search(r"\bpush\b.*\barchive/", rest):
                reason = "archive/* refs never leave this machine"
    if not reason:
        return 0
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": f"commit-guard: {reason}."}}))
    return 0


def main(argv):
    try:
        if argv[:1] == ["staged"]:
            return staged()
        if argv[:1] == ["message"] and len(argv) == 2:
            return message(argv[1])
        if argv[:1] == ["push"]:
            return push(argv[1:])
        if argv[:1] == ["range"] and len(argv) == 2:
            return rng(argv[1])
        if argv[:1] == ["hook"]:
            return hook()
    except Exception as e:   # fail closed
        print(f"commit-guard: error, blocking: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
