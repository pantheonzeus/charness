#!/usr/bin/env python3
"""Confidentiality gate for anything the client-follow-through skill drafts for a client to read.

  client_gate.py check <draft.md> --account "<Account or company>" [--allow-money] [--allow-email a@b.c ...]

Deterministic, no LLM. Fails (exit 1) on anything that must never reach a client by accident:
  - another account's name (cbrain/Clients notes with type: account, other than --account)
  - a person from the vault whose company is neither the client's nor ours (the active employer pack's
    employer.company_names; no pack → nobody counts as ours, so the gate flags more, never less)
  - money amounts (€, EUR, k€, Mio) unless --allow-money: prices go out only on purpose
  - internal markers: vault links, repo paths, pursuit/Baustein language, "confidential", "do not distribute"
  - email addresses not explicitly allowed
  - a brief (file under output/client/briefs/) with no http(s) source
A pass is necessary, not sufficient: the human still reads the draft before it goes anywhere.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
CLIENTS = REPO / "cbrain" / "Clients"
sys.path.insert(0, str(REPO / "scripts"))
import employer  # noqa: E402  employer pack (employers/README.md)
OURS = set(employer.company_names())
INTERNAL = [r"\[\[", r"cbrain/", r"output/", r"\bBaustein\b", r"\bpursuit\b", r"\bpipeline value\b", r"\bmargin\b",
            r"confidential", r"vertraulich", r"do not distribute", r"nicht weitergeben", r"internal only", r"\bintern\b"]
MONEY = r"(€\s?\d|\d[\d.,]*\s?(k€|T€|€|EUR\b|Mio\b|million\b|bn\b))"


def fm(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    return dict(re.findall(r"^(\w+):\s*(.+?)\s*$", m.group(1), re.M)) if m else {}


def check(path, account, allow_money=False, allow_email=()):
    text = Path(path).read_text()
    low, acc = text.lower(), account.lower().strip()
    errs = []
    for note in CLIENTS.glob("*.md"):
        meta = fm(note.read_text(errors="ignore"))
        name = note.stem
        if len(name) < 4 or name.lower() == acc or acc in name.lower():
            continue
        hit = re.search(r"\b" + re.escape(name.lower()) + r"\b", low)
        if not hit:
            continue
        company = meta.get("company", "").lower()
        if meta.get("type") == "account":
            errs.append(f"names another account: {name}")
        elif meta.get("type") == "person" and company and acc not in company and company not in acc \
                and not any(o in company for o in OURS):
            errs.append(f"names a person from another company: {name} ({meta.get('company')})")
    if not allow_money and re.search(MONEY, text, re.I):
        errs.append("contains a money amount; pass --allow-money only if this price is meant for them")
    for rx in INTERNAL:
        m = re.search(rx, text, re.I)
        if m:
            errs.append(f"internal marker: {m.group(0)!r}")
    for e in set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)):
        if e.lower() not in {x.lower() for x in allow_email}:
            errs.append(f"email address not allowed: {e}")
    if "/client/briefs/" in str(Path(path).resolve()) and not re.search(r"https?://", text):
        errs.append("a client brief needs at least one public http(s) source")
    return errs


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 4 or a[0] != "check" or "--account" not in a:
        print(__doc__)
        sys.exit(64)
    account = a[a.index("--account") + 1]
    emails = a[a.index("--allow-email") + 1:] if "--allow-email" in a else []
    emails = [e for e in emails if not e.startswith("--")]
    errs = check(a[1], account, "--allow-money" in a, emails)
    print("OK" if not errs else "\n".join("FAIL: " + e for e in errs))
    sys.exit(1 if errs else 0)
