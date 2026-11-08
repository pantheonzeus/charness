# Self-Evolution Loop — shared module

An optional *within-run* retry loop for hard skills (proposals, intelligence briefs, competitive analysis). Invoked by a skill that declares `modules: [self-evolution]`.

*Source: the NLAH `self-evolution` module (Pan et al., arXiv:2603.25723, App. F). The strongest single module on the solve loop itself (+5.8 / +8.4 on the paper's two benchmarks). Distinct from Charter §7's cross-session library learning — that improves the SKILL.md between runs; this improves the answer within one run.*

## The loop
1. **Baseline first.** Produce a real attempt before optimizing — no premature meta-work. Record it in the control spine.
2. **Trigger.** After any attempt that is unsuccessful, partial, unstable, or stalled, stop and **reflect on the concrete failure signals** (a failed gate, a missing source, a weak argument, a contradicted claim) before planning the next attempt. Reflection names *what* failed and *why*, not "try harder."
3. **Redesign along three axes.** Make the next attempt materially different, not a cosmetic retouch — change the **prompt/framing**, the **tools/sources** used, or the **workflow/decomposition**. Attempt 2 must visibly reflect attempt 1's reflection.
4. **Cap.** Default cap of **5** attempts unless the skill sets its own. Track the count in the control spine.
5. **Honest stop.** Continue until judged success or the cap. If the cap is hit without success, **report incomplete** — never dress the last attempt as passing. (Soul.md: never oversell; Charter §4 evidence gate still applies.)

## When NOT to use it
Skip on straightforward tasks — the loop adds cost and only pays off where the first attempt genuinely risks failing an acceptance gate. The related NLAH result: *multi-candidate search* (running K parallel candidates) rarely justified its cost — prefer this sequential reflect-and-redesign loop over parallel branching unless a skill has a specific reason.
