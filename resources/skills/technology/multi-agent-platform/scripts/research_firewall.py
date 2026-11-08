#!/usr/bin/env python3
"""Research firewall — reference implementation (stdlib only).

Claims sourced outside the client's systems of record are `external` and can
never fire a gate. Promotion to `observation` needs re-verification against a
named system and an owner, and is appended to a hash-chained audit log.

    python3 research_firewall.py --selftest
"""
import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone

CLASSES = {"observation", "inference", "external"}
SOURCE_TIERS = ("primary", "industry", "press", "unattributed")


class FirewallViolation(Exception):
    """A gated step tried to decide on a claim that is not gate-eligible."""


@dataclass
class Claim:
    id: str
    text: str
    cls: str
    source: str                      # system name (observation) or URL (external)
    retrieved: str = ""              # ISO date
    tier: str = ""                   # external only
    derived_from: list = field(default_factory=list)  # inference only

    def __post_init__(self):
        if self.cls not in CLASSES:
            raise ValueError(f"unknown claim class {self.cls!r}")
        if self.cls == "external" and (self.tier not in SOURCE_TIERS or not self.retrieved):
            raise ValueError("external claims need a source tier and a retrieval date")
        if self.cls == "inference" and not self.derived_from:
            raise ValueError("inference claims must list the observations they derive from")


class Ledger:
    def __init__(self):
        self.claims, self.audit = {}, []

    def _log(self, event: dict):
        prev = self.audit[-1]["hash"] if self.audit else "0" * 64
        body = json.dumps(event, sort_keys=True)
        self.audit.append({**event, "prev": prev,
                           "hash": hashlib.sha256((prev + body).encode()).hexdigest()})

    def add(self, claim: Claim):
        self.claims[claim.id] = claim
        self._log({"event": "add", "claim": claim.id, "cls": claim.cls})

    def gate_eligible(self, claim_id: str) -> bool:
        c = self.claims[claim_id]
        if c.cls == "observation":
            return True
        if c.cls == "inference":
            return all(self.gate_eligible(d) for d in c.derived_from)
        return False                 # external: never

    def gate(self, claim_id: str, decision: str):
        """Fire a hard gate. Raises (and the run must stop) on a non-eligible claim."""
        if not self.gate_eligible(claim_id):
            self._log({"event": "violation", "claim": claim_id, "decision": decision})
            raise FirewallViolation(f"{claim_id} is not gate-eligible; re-verify before deciding")
        self._log({"event": "gate", "claim": claim_id, "decision": decision})

    def promote(self, claim_id: str, system: str, owner: str):
        """External -> observation, only by re-verification against a named system, with an owner."""
        c = self.claims[claim_id]
        if c.cls != "external":
            raise ValueError("only external claims are promoted")
        if not system or not owner or owner.lower().startswith(("model", "llm", "agent")):
            raise ValueError("promotion needs a system of record and a human/process owner")
        c.cls, c.source = "observation", system
        c.retrieved = datetime.now(timezone.utc).date().isoformat()
        self._log({"event": "promote", "claim": claim_id, "system": system, "owner": owner})

    def verify_chain(self) -> bool:
        prev = "0" * 64
        for e in self.audit:
            body = json.dumps({k: v for k, v in e.items() if k not in ("prev", "hash")}, sort_keys=True)
            if e["prev"] != prev or e["hash"] != hashlib.sha256((prev + body).encode()).hexdigest():
                return False
            prev = e["hash"]
        return True

    def tier_mix(self) -> dict:
        ext = [c.tier for c in self.claims.values() if c.cls == "external"]
        return {t: ext.count(t) for t in SOURCE_TIERS if ext.count(t)}


def selftest():
    L = Ledger()
    L.add(Claim("o1", "Counterparty X holds certificate Y", "observation", "system-of-record", "2026-10-10"))
    L.add(Claim("e1", "Counterparty Z announced a new plant", "external",
                "https://example.com/news", "2026-10-10", tier="press"))
    L.add(Claim("i1", "X qualifies", "inference", "rule", derived_from=["o1"]))
    L.add(Claim("i2", "Z qualifies", "inference", "rule", derived_from=["o1", "e1"]))

    L.gate("o1", "shortlist X")
    L.gate("i1", "shortlist X")
    for bad in ("e1", "i2"):         # external, and inference tainted by external
        try:
            L.gate(bad, "exclude"); raise AssertionError(f"{bad} passed the firewall")
        except FirewallViolation:
            pass
    for owner in ("", "model:planner"):
        try:
            L.promote("e1", "system-of-record", owner); raise AssertionError("bad promotion accepted")
        except ValueError:
            pass
    L.promote("e1", "system-of-record", "buyer:jdoe")
    L.gate("i2", "shortlist Z")      # now eligible
    assert L.verify_chain()
    L.audit[1]["claim"] = "tampered"
    assert not L.verify_chain()
    print("research_firewall selftest: PASS (6 checks)")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        print(__doc__)
