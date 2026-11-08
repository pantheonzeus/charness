#!/usr/bin/env python3
"""Outbound confidentiality gate (G1b): deterministic, no model.

Confidentiality used to be prose only. Research on agent privacy leakage found that letting the model
judge its own disclosures fails structurally, while an out-of-model check took leak rates to ~0
(arXiv:2609.14003). This is that check, for the two ways text leaves the harness:

  send mode    a mail to known recipients. Flags another client's name (an account note other than the
               recipient's company and ours), a person from a third company, and internal chat channel
               names unless the recipient works at that employer. Called by .claude/hooks/send-gate.sh.
  public mode  a draft meant for everyone (LinkedIn, a talk, a blog). Flags every account and every
               vault contact with a company, unless allowed with --allow, plus internal channel names
               and the employer-internal tag.

Names come from the vault (cbrain/Clients: type account / type person + company); "ours" and the
recipient's company come from the employer packs (company_names, mail-triage companies, domain maps),
current and former. A finding is a reason to stop and look, not proof of a leak: the human decides.

  python3 scripts/outbound_gate.py check <file> --to a@b.com[,c@d.com]   send mode
  python3 scripts/outbound_gate.py check <file> --public [--allow NAME ...]
Exit 0 = clean, 1 = findings (one per line).
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CLIENTS = REPO / "cbrain" / "Clients"
sys.path.insert(0, str(REPO / "scripts"))
import employer  # noqa: E402


def fm(text):
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    return dict(re.findall(r"^(\w+):[ \t]*\"?(.*?)\"?[ \t]*$", m.group(1), re.M)) if m else {}


def vault_names():
    accounts, people = [], []
    for note in CLIENTS.glob("*.md") if CLIENTS.is_dir() else []:
        meta = fm(note.read_text(errors="ignore")[:2000])
        if meta.get("type") == "account":
            accounts.append(note.stem)
        elif meta.get("type") == "person" and meta.get("company") and " " in note.stem:
            people.append((note.stem, meta["company"]))
    return accounts, people


def domain_companies():
    """domain → company, from every employer pack (current and former)."""
    out = {}
    for slug in employer.packs():
        name = employer.get("employer.name", slug, slug)
        for d in employer.get("employer.domains", [], slug):
            out[d.lower()] = name
        try:
            for c in json.loads(employer.path("mail-triage/companies.json", slug).read_text()).get("companies", []):
                for d in c.get("domains", []):
                    out[d.lower()] = c["name"]
        except (OSError, ValueError):
            pass
        for rel in ("mail-to-conversations/domain_map.yaml", "calendar-to-contacts/domain_map.yaml"):
            try:
                for line in employer.path(rel, slug).read_text().splitlines():
                    line = line.split("#", 1)[0]
                    if ":" in line:
                        d, c = line.split(":", 1)
                        if c.strip():
                            out.setdefault(d.strip().strip('"').lower(), c.strip().strip('"'))
            except OSError:
                pass
    return out


def channels():
    """internal chat channel name → employer name, from every pack."""
    out = {}
    for slug in employer.packs():
        try:
            for c in json.loads(employer.path("slack-intel/channels.json", slug).read_text()).get("channels", []):
                out[c["name"].lower()] = employer.get("employer.name", slug, slug)
        except (OSError, ValueError, KeyError):
            pass
    return out


def mentions(name, text):
    if len(name) <= 4:   # short names (e.g. a three-letter acronym) only as the exact word, case-sensitive
        return re.search(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", text) is not None
    return re.search(r"(?<![\w-])" + re.escape(name.lower()) + r"(?![\w-])", text.lower()) is not None


def related(a, b):
    a, b = a.lower().strip(), b.lower().strip()
    return bool(a and b) and (a in b or b in a)


def scan(text, recipients=(), public=False, allow=()):
    accounts, people = vault_names()
    ours = set(employer.company_names()) | {n.lower() for n in employer.company_names()}
    allowed = {a.lower() for a in allow}
    dmap = domain_companies()
    rcpt_companies = {dmap.get(r.split("@")[-1].lower(), "") for r in recipients} - {""}
    rcpt_domains = {r.split("@")[-1].lower() for r in recipients}
    findings = []
    own_domains = {d.lower() for d in employer.get("employer.domains", [])}
    internal = not public and bool(rcpt_domains) and rcpt_domains <= own_domains   # a mail to colleagues only

    def exempt(company):
        return company.lower() in allowed or any(related(company, o) for o in ours) \
            or (not public and any(related(company, rc) for rc in rcpt_companies))

    for a in accounts if not internal else []:
        if mentions(a, text) and not exempt(a):
            findings.append(f"names an account: {a}" + ("" if public else " (not the recipient's company, not ours)"))
    for person, company in people if not internal else []:
        if person.lower() in allowed or not mentions(person, text):
            continue
        if public or not exempt(company):
            findings.append(f"names a contact from {company}: {person}")
    for ch, emp in channels().items():
        prefix = "#?" if "-" in ch else "#"   # a one-word name ("design") counts only as #design
        if re.search(r"(?<![\w-])" + prefix + re.escape(ch) + r"(?![\w-])", text, re.I):
            emp_domains = {d.lower() for s in employer.packs() if employer.get("employer.name", s, s) == emp
                           for d in employer.get("employer.domains", [], s)}
            if public or not (rcpt_domains & emp_domains):
                findings.append(f"names an internal {emp} chat channel: #{ch}")
    if public and re.search(r"employer-internal|confidential:\s*\S+-internal", text, re.I):
        findings.append("carries an employer-internal tag")
    return findings


def main(argv):
    if len(argv) < 2 or argv[0] != "check":
        print(__doc__)
        return 64
    text = Path(argv[1]).read_text(errors="ignore")
    to, allow, public = [], [], "--public" in argv
    for i, a in enumerate(argv):
        if a == "--to" and i + 1 < len(argv):
            to += [x.strip() for x in argv[i + 1].split(",") if x.strip()]
        if a == "--allow" and i + 1 < len(argv):
            allow.append(argv[i + 1])
    if not public and not to:
        print("send mode needs --to (or use --public)")
        return 64
    findings = scan(text, to, public, allow)
    for f in findings:
        print(f)
    print("OK" if not findings else f"FAIL: {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
