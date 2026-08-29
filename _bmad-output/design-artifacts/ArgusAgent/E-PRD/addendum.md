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

---

## A2 — Post-V1 Capabilities: why FR38–FR40 read as they do (2026-08-28)

**Change signal:** [sprint-change-proposal-2026-08-28.md](../sprint-change-proposal-2026-08-28.md)
**Approved by:** XAgent007 — scope 2026-08-28; promotion and dispositions 2026-08-29.

**The FR text is not in this file.** FR38, FR39 and FR40 live in `prd.md` §Functional Requirements, topically placed. What follows is only the reasoning behind that placement and their dispositions.

### Why they moved out of the addendum

The 2026-08-28 proposal (§4) routed FR38–FR40 here. That is the wrong destination for a functional requirement: the addendum carries downstream depth — rejected alternatives, mechanism decisions, options matrices — while the **binding capability contract is `prd.md`**, whose own preamble states that a capability not listed there will not exist. Left here, three *built* capabilities would have been invisible to every downstream skill that reads `prd.md` alone, and the PRD would have carried no record that Epic 20 happened at all. The 2026-08-10b amendment set the precedent: FR34–FR37 went into the PRD body, and only their rationale stayed behind.

### Why all three are disposed `library-seam`

Measured 2026-08-29, not inferred: nothing outside `argus/remediation`, `argus/adapters` and `argus/parsers` imports any of them; `argus/cli.py` names none of them; `[project.scripts]` gained no entry point. `tests/test_post_v1_integration.py` — the story's "E2E" suite — reaches the packages by direct import, which pins library behaviour rather than an invocable path. Story 10.5 met this exact shape in FR23/FR24/FR26/FR29, and its ruling governs here: the sharpest case is an FR whose text names an operator when no operator can reach the capability.

### Options considered for FR40, and why the narrow wording won

| Option | Outcome |
|---|---|
| Keep the drafted wording | **Rejected** — contradicts both the 2026-08-10 amendment and the on-disk baseline. |
| Restate as "adds definition extraction" | **Rejected on measurement** — `argus/index/ast_index.py::_DEF_KIND_BY_NODE` already carries the TS/JS, Go and Java vocabulary, byte-unchanged by Epic 20. |
| Keep FR40 out of the contract entirely | **Rejected** — an unrecorded promise leaves no trace that anything was committed; the same under-counting Story 10.5 refused. |
| **Admit it with the full disposition** | **Chosen** — records what exists, that it duplicates the indexer, that it is unreachable, and that `DF-10-2-A` is still open. |

### What was deliberately not done

No code shipped, no schema version moved, `argus/**` is byte-unchanged, and the ≥80% precision gate is untouched. The duplication between `argus/parsers/extended.py` and `argus/index/ast_index.py` is **recorded, not resolved**: wiring it in and removing it are both still open, and neither was decided under a PRD amendment.
