# PRD Addendum — ArgusAgent (APAA)

Depth that belongs downstream (architecture, implementation, integrator migration) rather
than in the PRD's capability contract. The PRD states *what must be true*; this states
*how it lands* and *what it costs consumers*.

---

## A1 — FR16 / FR4 amendment mechanics (2026-08-03)

**Change signal:** [sprint-change-proposal-2026-08-03.md](../sprint-change-proposal-2026-08-03.md)
**Approved by:** XAgent007, at the contract gate (step 4 of the proposal's recommended sequence).

### Options considered for the verdict vocabulary

| Option | Shape | Why not chosen |
|---|---|---|
| **Widen `INSUFFICIENT_COVERAGE`** *(chosen)* | One value carries the whole not-assessed state: sub-20% floor **or** unmet gate with zero findings. | — |
| Add `COVERAGE_GATE_UNMET` | A third non-blocking value sharing exit `3`. More precise diagnostics. | Grows a frozen enum and widens the surface every downstream consumer must learn, to distinguish two cases that route identically (human review). The distinction is already recoverable from the disclosed ratio and assessed population. |
| Reject CR-1 | Leave the decision table as shipped. | The blocking verdict would keep asserting a defect the audit did not find — the false-accusation failure mode cross-cutting concern #6 exists to prevent. |

### Implementation consequences (not PRD contract)

- **`VERDICT_SCHEMA_VERSION` `"1"` → `"2"`.** An intentional content-hash change, permitted
  under the additive-only rule at `argus/verdict/verdict_gate.py:147-149`. Verdicts persisted
  under `.apaa/` before the amendment keep their original meaning and their original version
  stamp; they are not rewritten.
- **Touched modules:** `argus/verdict/verdict_gate.py` (decision table + version bump),
  `argus/ledger/critical_subsystems.py` (eligibility filter, glob-capable exclusion).
- **Exit codes are unchanged as values.** No new code is introduced; what changes is which
  runs map to `3` instead of `2`.

### Integrator migration note

**Behaviour change:** some runs that previously exited `2` now exit `3`. A CI step that
branches only on `0` vs non-zero is unaffected. A step that treats `2` as "defect found"
and `3` as "escalate to a human" now gets the correct one in the zero-findings case —
which is the point of the amendment, and requires no code change on the consumer side.

### Related: `--coverage-scope` default (CR-2, landed 2026-08-03, no contract change)

The default flipped from `repository` to `application`. A CI step that relied on the
whole-repository denominator must now pass `--coverage-scope repository` explicitly to
keep its previous ratio. Both ratios remain printed on every run and the assessed
population remains disclosed on the verdict artifact, so no consumer loses information.
The coverage floor continues to be applied *within* the scope — a narrowing changes what
is claimed, never the bar for claiming it.

### Rationale trail

The FR16 amendment is **conformance to the PRD, not a reversal of it**. "Never a default
block" was in FR16 from the original draft; what shipped was a decision table whose
`otherwise` row violated it. Journey 3 already specified "`INSUFFICIENT_COVERAGE` routing
to human review (never a silent pass *or a false block*)" — the amended table is the first
version that actually delivers the second half of that clause.
