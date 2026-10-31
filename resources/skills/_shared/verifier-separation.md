# Verifier Separation — shared module

A distinct checking step that judges one candidate answer against the acceptance criterion, separate from the agent that produced it. Invoked by a skill that declares `modules: [verifier-separation]`.

*Source: the NLAH `verifier separation` module (Pan et al., arXiv:2603.25723, App. F + F.1). Measured positive on both audited benchmarks, but unevenly — +0.2 on SWE-bench Verified vs +8.4 on OSWorld. The finding: an explicit checking stage helps only when its object of judgment stays close to the benchmark's own acceptance criterion.*

## The contract
1. **Role.** The verifier inspects one candidate answer against the original problem and the lightest sufficient task materials needed to check it — not the whole workspace, not a re-derivation from scratch.
2. **Procedure.**
   - Identify the candidate's claim.
   - Break it into checkable subclaims.
   - Audit completeness, factual correctness, and logical correctness.
   - Run at least one central independent check when feasible (re-run a test, re-fetch a source, recompute a number).
3. **Output.** Return exactly one primary verdict label (e.g. pass/fail, or a named status), plus a report naming which checks ran and which were blocked and why. **The verifier never repairs the candidate on its behalf** — a fail is a fail, reported back for the producing step to fix, not silently patched.

## Where it pays off
Per F.1: keep the verifier's judgment object as close as possible to the actual acceptance criterion the deliverable will be judged against. A verifier checking something adjacent-but-not-quite (style instead of correctness, a proxy instead of the real gate) adds cost without adding control. When designing a verifier step, name the exact acceptance criterion it checks before writing the procedure.

## Existing users
`sales/audience-of-one-report` (ordered audit gates against its provenance registries), `workflow-ops/linkedin-viral-scheduler` (`scripts/prepublish_audit.py` as the deterministic verifier). New verifier steps should follow this contract rather than reinventing the shape per skill.
