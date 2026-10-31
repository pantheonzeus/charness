#!/usr/bin/env python3
"""Employer packs: everything that ends with an employment contract, in one swappable folder.

employers/ACTIVE names the active pack (one line: a slug, or "none"). employers/<slug>/ holds
profile.json, role.md, brand/ and the real config files skills used to keep in their own
schema/ folders, filed as <skill-id>/<same file name>. Everything under employers/ except
README.md and _template/ is gitignored. Stdlib only: launchd loops import this.

As a library (skills add REPO/scripts to sys.path):
  employer.path("mail-triage/companies.json")  file in the active pack; a path that does not
                                               exist when no pack is active, so callers keep
                                               their usual "missing file → empty" handling
  employer.get("employer.name")                dotted lookup in the active profile
  employer.require("mail", "google", "mail-triage")   exit unless that adapter is bound

  python3 scripts/employer.py get <dotted.key>      one profile value (JSON for non-strings)
  python3 scripts/employer.py path <rel>            absolute path of a pack file
  python3 scripts/employer.py context               the SessionStart block (role, bindings, rules)
  python3 scripts/employer.py validate              profile, files, loops, runtime login
  python3 scripts/employer.py loops [--load|--unload] [--apply]   declared launchd loops
  python3 scripts/employer.py exit-report [<slug>]  what a pack's employer still has on disk

CBRAIN_EMPLOYER overrides employers/ACTIVE for one process (tests, a dry look at another pack).
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ROOT = REPO / "employers"
ACTIVE = ROOT / "ACTIVE"
LAUNCH_AGENTS = Path.home() / "Library" / "LaunchAgents"
ADAPTERS = {"mail": {"google", "m365"}, "calendar": {"google", "m365", "eventkit"},
            "files": {"google", "m365"}, "chat": {"slack", "teams", "none"}}


def active():
    slug = os.environ.get("CBRAIN_EMPLOYER")
    if slug is None:
        try:
            slug = ACTIVE.read_text().strip()
        except OSError:
            return None
    slug = slug.strip()
    if not slug or slug == "none" or slug.startswith("_") or not (ROOT / slug).is_dir():
        return None
    return slug


def packs():
    """Every real pack on disk, active or former."""
    return sorted(p.name for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith((".", "_"))) \
        if ROOT.is_dir() else []


def profile(slug=None):
    slug = slug or active()
    if not slug:
        return {}
    try:
        return json.loads((ROOT / slug / "profile.json").read_text())
    except (OSError, ValueError):
        return {}


def get(key, default=None, slug=None):
    node = profile(slug)
    for part in key.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node


def path(rel, slug=None):
    return ROOT / (slug or active() or "_none") / rel


def provider(capability):
    return get(f"providers.{capability}.adapter")


def require(capability, adapter, what):
    bound = provider(capability)
    if bound != adapter:
        raise SystemExit(f"{what}: needs the {capability} adapter '{adapter}', but the active employer pack "
                         f"({active() or 'none'}) binds '{bound or 'nothing'}'. "
                         f"See resources/adapters/{capability}.md and employers/README.md.")


def company_names(slug=None):
    return [n.lower() for n in get("employer.company_names", [], slug)]


def former():
    """Packs other than the active one: their content stays employer-internal after the job ends."""
    a = active()
    return [s for s in packs() if s != a]


def context():
    slug = active()
    formers = ", ".join(get("employer.name", s, s) for s in former()) or "none"
    rule = ("Content from any employer's systems (mail, chat, documents, clients, internal channels) is class "
            "`employer-internal`, for the current employer and every former one. It may sit in the vault only where the "
            "pack records an approval, and never goes into public content (LinkedIn, talks, blog), another employer's "
            "work, or the venture.")
    if not slug:
        return ("### Active employer pack — none\n\nNo active employer pack (employers/ACTIVE is missing or `none`): "
                f"employer bindings and loops are off. Former employer packs: {formers}.\n{rule}\n"
                "Switch or exit: employers/README.md.\n")
    p = profile(slug)
    e = p.get("employer", {})
    role = ""
    try:
        role = (ROOT / slug / "role.md").read_text().strip()
    except OSError:
        pass
    binds = ", ".join(f"{cap}={v.get('adapter', '?')}" + (f" ({v['workspace']})" if v.get("workspace") else "")
                      for cap, v in p.get("providers", {}).items())
    approvals = ", ".join(f"{k} since {v}" for k, v in p.get("confidentiality", {}).get("vault_ok", {}).items()) or "none"
    return "\n".join([
        f"### Active employer pack — employers/{slug}/ ({e.get('name', slug)})", "",
        role, "",
        f"- **Bindings:** {binds}. Skills ask for a capability (resources/adapters/<capability>.md), never a vendor.",
        f"- **Work email:** {e.get('work_email', '?')} · domains: {', '.join(e.get('domains', []))}",
        f"- **Confidentiality:** {rule} Vault approvals for this employer: {approvals}. Former employer packs: {formers}.",
        f"- **Employer loops:** {', '.join(p.get('loops', [])) or 'none'}",
        "- Pack files: `python3 scripts/employer.py path <rel>`; switch or exit: employers/README.md.", ""])


def loaded_labels():
    out = subprocess.run(["launchctl", "list"], capture_output=True, text=True).stdout
    return {line.split()[-1] for line in out.splitlines()[1:] if line.split()}


def loops(action=None, apply=False, slug=None):
    labels = get("loops", [], slug)
    live = loaded_labels()
    uid = os.getuid()
    for label in labels:
        plist = LAUNCH_AGENTS / f"{label}.plist"
        state = f"{'installed' if plist.exists() else 'MISSING  '} {'loaded' if label in live else 'not loaded'}"
        print(f"{label:<34} {state}")
        if action and plist.exists():
            cmd = (["launchctl", "bootout", f"gui/{uid}", str(plist)] if action == "unload"
                   else ["launchctl", "bootstrap", f"gui/{uid}", str(plist)])
            if (action == "unload") != (label in live):
                continue
            if apply:
                r = subprocess.run(cmd, capture_output=True, text=True)
                print(f"  {action}ed" if r.returncode == 0 else f"  {action} failed: {r.stderr.strip()}")
            else:
                print("  would run:", " ".join(cmd))


def validate(slug=None):
    slug = slug or active()
    errors, warnings = [], []
    if not slug:
        print("no active pack (employers/ACTIVE)")
        return 0
    p = profile(slug)
    if not p:
        errors.append(f"employers/{slug}/profile.json missing or not valid JSON")
    for key in ("employer.name", "employer.company_names", "employer.domains", "confidentiality.class"):
        if get(key, slug=slug) in (None, "", []):
            errors.append(f"profile key missing: {key}")
    for cap, v in p.get("providers", {}).items():
        if cap in ADAPTERS and v.get("adapter") not in ADAPTERS[cap]:
            errors.append(f"providers.{cap}.adapter '{v.get('adapter')}' not one of {sorted(ADAPTERS[cap])}")
    if not (ROOT / slug / "role.md").is_file():
        errors.append("role.md missing")
    for rel in p.get("files", []):
        if not (ROOT / slug / rel).is_file():
            errors.append(f"pack file missing: {rel}")
    for label in p.get("loops", []):
        if not (LAUNCH_AGENTS / f"{label}.plist").exists():
            warnings.append(f"loop {label} declared but not installed")
    try:
        auth = json.loads(subprocess.run(["claude", "auth", "status"], capture_output=True, text=True, timeout=30).stdout)
        who = f"{auth.get('email', '')} {auth.get('orgName', '')}".lower()
        for s in packs():
            hits = [d for d in get("employer.domains", [], s) + company_names(s) if d.lower() in who]
            if hits:
                warnings.append(f"the Claude login ({auth.get('email')}, {auth.get('orgName')}) belongs to employer "
                                f"'{s}': every loop stops when that job ends")
    except (OSError, ValueError, subprocess.SubprocessError):
        warnings.append("could not read `claude auth status`")
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    if not errors:
        print(f"OK   employers/{slug}/ ({len(p.get('files', []))} files, {len(p.get('loops', []))} loops)")
    return 1 if errors else 0


def exit_report(slug=None):
    slug = slug or active()
    if not slug:
        raise SystemExit("usage: employer.py exit-report <slug>")
    p, name = profile(slug), get("employer.name", slug, slug)
    print(f"# Exit report — {name} (employers/{slug}/)\n")
    print("## Loops to unload\n")
    loops(slug=slug)
    print("\n## Content from this employer still on disk\n")
    tag = re.compile(rf"^(employer:\s*{re.escape(slug)}|confidential:\s*{re.escape(slug)}-internal)\s*$", re.M | re.I)
    markers = p.get("exit", {}).get("vault_markers", [])
    tagged, marked = [], []
    for f in (REPO / "cbrain").rglob("*.md"):
        try:
            text = f.read_text(errors="ignore")
        except OSError:
            continue
        if text.startswith("---") and tag.search(text.split("\n---", 1)[0]):
            tagged.append(f.relative_to(REPO))
        elif any(m in text for m in markers):
            marked.append(f.relative_to(REPO))
    print(f"- vault notes tagged for this employer: {len(tagged)}")
    for h in tagged[:20]:
        print(f"  - {h}")
    if markers:
        print(f"- vault notes holding untagged sections from this employer ({', '.join(markers)}): {len(marked)}")
        for h in marked[:20]:
            print(f"  - {h}")
    for d in p.get("exit", {}).get("output_dirs", []):
        root = REPO / d
        files = [x for x in root.rglob("*") if x.is_file()] if root.exists() else []
        print(f"- {d}: {len(files)} files, {sum(x.stat().st_size for x in files) // 1024} KB")
    print("- .vault-history.git: every headless run's vault commit, including the notes above; deleting a note "
          "does not remove it from history")
    print("\n## Credentials to revoke and delete\n")
    for c in p.get("exit", {}).get("credentials", []):
        print(f"- {c} ({'present' if Path(os.path.expanduser(c)).exists() else 'absent'})")
    for n in p.get("exit", {}).get("notes", []):
        print(f"- {n}")
    print("\nKeep or purge is a contract question, not a harness default: decide, then act.")


def main(argv):
    if not argv:
        print(__doc__)
        return 64
    cmd, rest = argv[0], argv[1:]
    if cmd == "get" and rest:
        v = get(rest[0])
        print(v if isinstance(v, str) else json.dumps(v))
    elif cmd == "path" and rest:
        print(path(rest[0]))
    elif cmd == "context":
        print(context())
    elif cmd == "validate":
        return validate(rest[0] if rest else None)
    elif cmd == "loops":
        action = "load" if "--load" in rest else "unload" if "--unload" in rest else None
        loops(action, apply="--apply" in rest)
    elif cmd == "exit-report":
        exit_report(rest[0] if rest else None)
    else:
        print(__doc__)
        return 64
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
