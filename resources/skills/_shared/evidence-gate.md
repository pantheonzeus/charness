# Evidence Gate — shared module

Cross-skill procedure invoked by Charter §4. Any skill that ships a client-facing deliverable with factual or numeric claims runs this before finalizing. It is the mechanical form of Soul.md's *"never dress a guess as a fact / never oversell the numbers."*

*Source: the NLAH `evidence-backed answering` module (Pan et al., arXiv:2603.25723, App. F). Consistently positive across benchmarks; strongest when the check stays close to the actual acceptance criterion.*

## When it fires
Any deliverable to `output/` that a reader could act on — proposals, briefs, reports, LinkedIn copy with claimed metrics, competitive analysis. **Exempt:** trivial/off-lane asks, pure-format edits, and internal scratch.

## Before you draft: register recall

The gate above is **outbound** — it checks what you are about to claim. It has no inbound step, and that is a real failure mode in multi-part runs: *a fact you already established and filed can sit unread in your own `EVIDENCE.md` while you write a deliverable that contradicts it.*

So before drafting any deliverable in a run that already has an `EVIDENCE.md`:

- **List the entities this deliverable touches** — systems, vendors, products, apps, people, environments, named numbers. Not the sibling deliverables it references: the *things* it talks about.
- **Grep the register for each one**, and for the obvious synonyms. Cheap (`grep -i`), and it is the whole cost of the step.
- **Scope answers get this unconditionally.** Anything that defines a boundary — MVP contents, migration scope, inventories, "what exists today", counts, priorisation — is exactly where an unread register entry does the most damage, because the omission is invisible in the finished text.
- **A hit that contradicts your draft is a finding, not a nuisance.** Surface it, correct the draft, and record it — the same way a refuted assumption is recorded.

*(This is the failure that prompted the rule: a register line reading "the current app is from vendor A, vendor B's payment provider is used in the brand-C app" sat filed for a day while an MVP-scope and a priorisation answer were written on the premise of a single existing app. The register was right; nobody asked it. Reading only the referenced sibling answers would not have caught it — the fact lived under a different question.)*

## The gate
Before release, produce an evidence pass (inline for small deliverables, `STATE_ROOT/EVIDENCE.md` for substantive ones):

1. **List release-critical claims.** Every claim whose falsity would embarrass the deliverable or mislead the reader. Numbers, named facts, attributions, "will win / will save X" assertions.
2. **Tag each claim's provenance:**
   - `observed` — pulled directly from a named source (URL, file, tool output). Cite it.
   - `inferred` — reasoned from observations. Name the inputs and say it's inference.
   - `assumed` — neither. **Not shippable as fact** — either source it, mark it explicitly as an assumption in the deliverable, or cut it.
   - A vault note as source: cite whether it is `confirmed:` (Charter §6 trust tier). Where a confirmed and an unconfirmed note disagree, the confirmed one wins and the register records the contradiction.
3. **Anti-fabrication.** A number without a source is `assumed`, not `observed`. Do not round, extrapolate, or "tidy" a figure into looking more precise than its source. Ranges and dates carry their `as_of`.
4. **Gate.** The deliverable does not ship while any release-critical claim is `assumed`-as-fact, uncited, contradicted by a source, or materially incomplete — **or while it contradicts an entry already in the register** (see register recall above).

## Fix-loop: blockers to zero (substantive deliverables)
Step 4 is mechanical once the register is a table, so run it as an `autoresearch:fix` loop under [`autoresearch-loop.md`](autoresearch-loop.md):

- **Metric:** `python3 resources/skills/_shared/scripts/evidence_lint.py STATE_ROOT/EVIDENCE.md` → `blockers=` (target 0). It counts three things:
  - `uncited`: observed or inferred with an empty source;
  - `assumed`: an assumption not yet labelled as such in the deliverable;
  - `untagged`: anything outside `observed` / `inferred` / `assumed`.
- **Per iteration:** fix one blocker: cite it, re-tag it, label the assumption in the deliverable, or cut the claim from the deliverable. Then re-run. Once the deliverable states an assumption, tag it `assumed (stated)`.
- **Register format the lint reads:** one table per section, with a claim column (`Claim` / `Aussage`), a tag column (`Type` / `Tag` / `Prov.`) holding exactly one of the three tags, and a source column. Retire a claim with `~~strikethrough~~` rather than deleting it.
- **Guard:** don't fix a blocker by deleting the register row while the claim stays in the deliverable. The lint can't see the deliverable, so the reviewer checks this.
- **Cap:** 5 passes. If blockers remain, report them by line; don't ship them as passing.
- **Judges are not this metric.** No judge-scored ≥95 loops on client deliverables (see `sales/_category.md`).

## Cheapest sufficient form
Do not build the full JSON-registry machinery for every task. Scale the evidence artifact to the deliverable:
- **Small** (a LinkedIn post, a short email) — a 3–5 line provenance note in the run, or inline citations.
- **Substantive** (a proposal, an intelligence brief) — a structured `EVIDENCE.md` per claim, or the provenance registries in `sales/audience-of-one-report` (`programmes.json` etc.), which is the maximal worked example.
