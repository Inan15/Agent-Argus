# Sprint Change Proposal — 2026-08-22

**Project:** ArgusAgent (formerly APAA — AI Project Assurance Audit)
**Author:** Technical research + measurement session, acting on the detector-category research of 2026-08-21/22
**Requested by:** XAgent007
**Trigger type:** Measurement. The detector-category research asked why the gate returns an empty
verdict-eligible population. Measuring the shipped predicate against the recorded 1,032-finding
flagged population identified **one shipped precision defect** and **one candidate verdict-eligible
class carrying 36 members**, and **falsified the research's own first estimate** of a cheap widening.
**Change scope classification:** **MODERATE** — two stories added to Epic 16. **No** gate amendment,
**no** protocol amendment, **no** threshold movement, **no** bench expansion, **no** ratification.
**Status:** ✅ **APPROVED by XAgent007, 2026-08-22.** The document was authored and committed
(`b4b9b92`) in the `AWAITING OPERATOR APPROVAL` state, and approval was taken as a **separate, later
act** — recorded here in place, on the §4.3 precedent of the 2026-08-20 proposal, so that authoring
and approving are not collapsed into one motion by the party proposing.

> **Nothing under `argus/` or `tests/` was modified to produce this document.** No detector was run
> over any corpus member; no adjudication set, finding, verdict, disposition or gate artifact was
> produced or modified; no working tree was read or mutated; nothing under `validation-corpus/` was
> written; no sealed candidate was fetched or ratified. `git diff` over `validation-corpus/` is
> empty. **`DF-13-5-A`'s round is UNSPENT.** Every figure below was obtained by calling the
> **shipped** `provenance_evidence()` over blobs materialised from each member's pinned git object
> into a scratch tree. Harness and figures: [`research/revalidate-fact-b-widening.py`](research/revalidate-fact-b-widening.py),
> [`research/measure-vacuous-population-split.py`](research/measure-vacuous-population-split.py),
> [`research/technical-argusagent-detector-categories-research-2026-08-21.md`](research/technical-argusagent-detector-categories-research-2026-08-21.md).

---

## 0. What this document is for, in one paragraph

The corrected detector emits **0 blocking findings of 4,284** over the ratified corpus, and Epic 16
exists to strengthen the gate before spending `DF-13-5-A`'s single round. This proposal does not
spend the round, does not expand the bench, and does not touch a threshold. It records what
measurement established about **why** the population is empty — that the binding clause is
`consumed == 0` evaluated over the whole test function, and that one clause of fact (b) is provably
dead over the entire corpus — identifies a **shipped precision defect** in the assertion vocabulary
that inflates the advisory population, and proposes **two stories**: fix the defect, then
**adjudicate** a measured 36-member candidate class **as a measurement**, not as a promotion.
Promotion is deliberately *not* proposed, because the spot-check found a false-accusation class the
data cannot rule out.

---

## 1. Issue Summary

### 1.1 What was measured, and how the harness earned trust

All 1,032 `vacuous_test_heuristic` findings recorded in `validation-corpus/adjudication-set-13-5.json`
were re-evaluated through the **shipped** `argus.detectors.provenance_scan.provenance_evidence()` —
the exact function `ast_corroborated` calls — with span edges from a real `build_ast_index` over
pinned blobs. **The harness was validated in both directions before any figure was believed:**

| Direction | Check | Result |
|---|---|---|
| Negative | shipped fact (b) must reproduce the recorded **0** blocking findings | **0** ✅ |
| Positive | the project's own `_CORROBORATED_FIXTURE` control must still promote | `disc=2 cons=0 mref=1` → corroborated **True** ✅ |

The positive control was not optional. `mock_referencing_assertions` measures **0 across all 1,032**
findings, which would make the negative check pass trivially if the harness could not compute that
field at all. It can. The zero is real.

### 1.2 Clause-by-clause, against the shipped predicate

| Clause | of 1,032 |
|---|---:|
| no SUT call at all (`disc=0 ∧ cons=0`) | 8 |
| at least one **discarded** SUT call | **676** |
| **zero consumed** SUT calls | **14** |
| at least one **mock-referencing assertion** | **0** |
| `sut_result_is_discarded` (`disc≥1 ∧ cons=0`) | 6 |
| full shipped fact (b) | **0** |

**Two findings follow, and neither was previously on the record.**

**(a) The mock-referencing clause is provably dead over the ratified corpus — 0 of 1,032.** Not one
flagged test carries an assertion referencing a mock-bound name. The clause blocks exactly the 6
findings that satisfy everything else.

**(b) The binding constraint is the SCOPE of `consumed == 0`, not the word "discarded".** 676
findings have at least one discarded SUT call; only 14 have zero consumed ones. The clause is
evaluated over the **whole test function**, so a single observed call anywhere — including one
inside a `pytest.raises` block (CONSUMED by DN-3) or one that cannot be located in source
(CONSUMED because *unresolvable is not evidence*) — withholds corroboration from the entire test.

### 1.3 ⛔ A shipped precision defect: the assertion vocabulary cannot see `raise AssertionError`

Spot-checking candidates surfaced this, and it is independent of any widening.

`is_assertion_callee` recognises the `_ASSERTION_CALLEES` table **or** the naming convention
`\A_?assert\w*\Z`. That regex is **case-sensitive**, so `AssertionError` does not match, and a
`raise` is a statement rather than a call to an assertion callee. The idiom

```python
try:
    prosecute(verdict="not-a-verdict", ledger=ledger)
except ProsecutorError:
    pass
else:
    raise AssertionError("a non-AuditVerdict verdict must raise ProsecutorError")
```

is a **rigorous** contract assertion that the vocabulary scores as no assertion at all.

**Measured impact: 22 of 1,032 flagged findings contain `raise AssertionError`.** Because the
density scorer counts assertion statements, those tests are scored at a lower assertion density
than they truly have, which **inflates the flagged advisory population**. This is a false-flag
defect in the shipped advisory tier, in the accusation direction.

### 1.4 The candidate class, and why promotion is NOT proposed

Formulating the per-call question as *"reaches the SUT, discards the result, and asserts nothing at
all"* — using the **wide** vocabulary, because `DN-14-2-1` forbids routing this question through the
frozen corroboration table — yields:

| Variant | Definition | Count |
|---|---|---:|
| V0 shipped | `disc≥1 ∧ cons=0 ∧ mref≥1` | **0** |
| V1 drop dead clause | `disc≥1 ∧ cons=0` | **6** |
| **V2 silent** | `disc≥1 ∧ span asserts NOTHING` | **39** |
| V2 after the §1.3 fix | 3 of the 39 are false accusations from the vocabulary gap | **36** |
| V5 unrelated-assertions | `disc≥1 ∧ asserts, none about the SUT` | 122 |
| V4 upper bound | `disc≥1` alone | 676 |

⛔ **V2 must not be promoted on this evidence.** A three-case spot-check found that the class
contains a legitimate idiom the data cannot separate — the deliberate smoke test:

```python
def test_no_float_fields_serialize(self) -> None:
    led = CoverageLedger.build(_golden_entries())
    canonical.dumps(led.model_dump())  # must not raise
```

Here *"does not raise"* **is** the assertion, stated in a comment the analyser cannot read. `DN-3`
already carves out the explicit spelling (`pytest.raises`); this is the implicit one. **The
proportion of the 36 that are intentional smoke tests is unmeasured**, and promoting the class
blind would manufacture exactly the false 🔴 that cross-cutting #6 exists to prevent.

### 1.5 ⛔ What this proposal WITHDRAWS

The research addendum of 2026-08-22 estimated that widening *"discarded"* to *"unobserved"* would
reach **250** candidates. **That estimate is falsified and is withdrawn.** It was produced by a
hand-rolled classifier using a weaker notion of "consumed" than the shipped scan, which
additionally counts as consumed: a call inside `pytest.raises`/`assertRaises`/`pytest.warns`
(DN-3), an unlocatable call, an off-span edge, and treats mock-rooted calls as not-SUT at all. The
correct figure for that formulation is **6**. The falsification and the corrected figure are
recorded in place in the research document rather than restated quietly.

---

## 2. Impact Analysis

### 2.1 Epic impact

**Epic 16 — Spend the Round Well.** Stories 16.1–16.3 `done`; **16.4 `in-progress`, HALTED at Task 1**
awaiting HALT-1/HALT-2; 16.5 `backlog`. This proposal **adds 16.6 and 16.7** and touches no existing
story. It is squarely inside Epic 16's charter — *strengthen the gate, then measure once* — and is
the work `DF-13-5-A`'s own pre-registered fallback names: *"a materially better detector — NOT a
bigger bench."*

### 2.2 ⛔ Sequencing constraints — non-negotiable, and they gate everything

1. **Story 16.4's AC7.1 declares `argus/detectors/**` BYTE-UNCHANGED.** Neither new story may land
   while 16.4 is in flight. **16.6 and 16.7 are blocked on 16.4 reaching a terminal state** —
   whether that is the round spent or the round declined.
2. **`argus/detectors/vacuous_test.py` is at 1,196 lines against the 1,200 ceiling — 4 lines of
   headroom**, with `DF-15-2-D` filed and requiring it stay byte-unchanged until split. The §1.3 fix
   touches the assertion vocabulary, which lives there. **A module split is a PRECONDITION of 16.6,
   in its own commit, before any behaviour change.** Sibling headroom, measured at HEAD:
   `provenance_scan.py` 976 (224 free) · `test_vacuous_density.py` 1,159 (41 free, `DF-15-2-E`) ·
   `test_vacuous_detector_index.py` 1,065 (135 free).
3. **Protocol §2's QA Lead role is UNFILLED**, and §4's borderline ladder terminates there. 16.7
   produces adjudications and can produce borderlines. **The role must be filled before 16.7 runs**,
   not during it.

### 2.3 Severity

🟠 **Moderate.** Nothing is failing and no guard is loose. The §1.3 defect makes the tool
**over-flag** in the advisory tier — it does not produce a false blocking verdict, because the
advisory tier cannot block. The gate remains correctly `BLOCKED`.

### 2.4 What is explicitly NOT in scope

- ⛔ **No bench expansion, no ratification, no third-party fetch, no round spent.** Story 16.4's
  AC5.3 forbids this proposal from proposing expansion, and it does not: every figure here comes
  from the corpus already ratified and already audited.
- ⛔ **No gate or protocol amendment.** `VALIDATION_SET_FLOOR_N`, the ≥80% `Fraction`, the breadth /
  seal / yield floors, `SECTION_5_CONDITIONS`, `GATE_OUTCOMES`, `CONDITION_VERDICTS` and
  `MANIFEST_FIELDS` are all untouched.
- ⛔ **No promotion of any finding to verdict-eligible.** 16.7 measures; it does not promote.
- ⛔ **No loosening of fact (b).** Its asymmetry is correct and stays.
- **Per-call observation analysis (V5, 122 findings) is NOT proposed here.** It requires real
  dataflow and scope resolution — Story 6.2 / `DF-14-1-A` — and is recorded as a deferred entry.

---

## 3. Recommended Approach

### 3.1 Options evaluated

| # | Option | Verdict |
|---|---|---|
| 1 | Do nothing; carry the findings as research only | ❌ The §1.3 defect is shipped and inflates the advisory population. Leaving a measured false-flag defect unfiled is how it becomes permanent. |
| 2 | Drop the dead mock-referencing clause; promote the resulting 6 | ❌ Six findings, from five repositories, against a base rate of 0 TP / 26 FP. A precision measurement resting on six is fragile even if all six adjudicate true. |
| 3 | Promote V2 (36) to verdict-eligible | ⛔ **Rejected.** The smoke-test class is real, unmeasured, and promoting blind manufactures false 🔴. |
| 4 | **Fix the vocabulary defect; then ADJUDICATE the 36 as a measurement** | ✅ **Selected.** Fixes a shipped defect in the safe direction, and converts an unmeasured class into a measured one before anything is promoted. |

### 3.2 Selected — Option 4, in two stories, strictly ordered

**16.6 fixes the defect. 16.7 measures the class. Neither promotes anything.** If 16.7's
adjudication shows the class is predominantly real, a *later* story may propose promotion, carrying
16.7's number as its evidence. That is the same author-then-approve separation §4.3 of the
2026-08-20 proposal established for the gate amendment.

### 3.3 Effort, risk, timeline

| | 16.6 | 16.7 |
|---|---|---|
| Effort | Small — a module split, then a vocabulary addition + guards | Small in code; **human adjudication of ≤36 rows is the cost** |
| Risk | Low — changes the advisory tier only, in the de-accusation direction | Low in code; the risk is the QA Lead role |
| Blocked on | 16.4 terminal + `vacuous_test.py` split | 16.6, and the QA Lead role filled |

---

## 4. Detailed Change Proposals

### 4.1 `epics.md` — 2 story entries appended to Epic 16

**Story 16.6 — The assertion vocabulary recognises the assertion that is a `raise`.**
*As the Engineering Lead, I want `raise AssertionError` counted as an assertion, so that the advisory
population is not inflated by tests that assert rigorously in a spelling the tool cannot read.*
Acceptance shape: a `vacuous_test.py` module split lands **first, in its own commit**, with no
behaviour change and `DF-15-2-D` discharged or re-filed against the new sizes · the wide vocabulary
(never the frozen corroboration table — `DN-14-2-1`) recognises a `raise` whose exception is
`AssertionError` · driven RED by executed mutation · the 22 affected findings are re-derived and the
before/after flagged count recorded · `_CORROBORATION_ASSERTION_CALLEES` stays **byte-unchanged at
23 names**, because widening it moves fact (b) toward an accusation.

**Story 16.7 — Adjudicate the silent-test class before anyone proposes promoting it.**
*As the Engineering Lead, I want the 36-member silent class adjudicated by a named human under §4, so
that a promotion proposal can carry a measurement instead of an estimate.*
Acceptance shape: the class is re-derived after 16.6 and its exact membership recorded · every member
carries a TP/FP/BORDERLINE disposition from a named `<who> (<role>)` under protocol §4 · the
**intentional smoke test** is adjudicated explicitly as its own outcome, not folded into FP without
comment · `expert_hours` recorded as an exact `Fraction` and reported against the §3 ≤4-hour ceiling
as a **report, never a gate** · ⛔ **no finding is promoted to verdict-eligible by this story, and no
threshold moves** · if the ladder reaches an unfilled role, the story **STOPS** and reports the rows.

### 4.2 `sprint-status.yaml` — 2 entries

```yaml
  16-6-the-assertion-vocabulary-recognises-the-assertion-that-is-a-raise: backlog
  16-7-adjudicate-the-silent-test-class-before-proposing-promotion: backlog
```

Both **blocked on 16.4 reaching a terminal state** (AC7.1). Recorded in the entry comment, since
`sprint-status.yaml` carries no dependency field.

### 4.3 `deferred-work.md` — 2 new entries

- **`DF-16-6-A` — the mock-referencing clause of fact (b) is provably dead over the ratified
  corpus (0 of 1,032).** Not proposed for removal here: removing it promotes 6 findings, and this
  proposal declines to promote anything without adjudication. Owner: XAgent007. Target story: the
  promotion story that 16.7's outcome may justify. Severity 🟡.
- **`DF-16-7-A` — per-call observation analysis (V5, 122 findings measured) requires real dataflow.**
  The `consumed == 0` clause is whole-function scoped; making the judgement per call needs scope
  resolution. Target story: **6.2** (`DF-14-1-A`). Severity 🟠 — it is the largest measured reachable
  population and the only one that addresses the ~40% suspect class.

### 4.4 `tests/test_status_document_registry.py` — 1 entry

This document registered in `_STATUS_DOCUMENTS` **in the same commit**, per
`TC-ArgusAgent-DOCS-001-22`, which closes in both directions.

---

## 5. Implementation Handoff

1. ⛔ **Do not start either story until 16.4 is terminal.** AC7.1 holds `argus/detectors/**`
   byte-unchanged; starting earlier breaches a live story's declared write set.
2. **16.6 opens with the `vacuous_test.py` split**, alone, in its own commit, no behaviour change.
   4 lines of headroom is not enough for the fix and the guards.
3. **Fill the QA Lead role before 16.7 runs.**
4. Re-derive every figure in §1 before relying on it. The harnesses are committed under `research/`
   and both validate in two directions; **re-run them rather than reading the tables above** — this
   proposal's own predecessor estimate was falsified by exactly that discipline.

---

## 6. Approval

| Act | Party | Date | Status |
|---|---|---|---|
| Authored | research + measurement session | 2026-08-22 | ✅ |
| Approved | XAgent007 (Engineering Lead) | 2026-08-22 | ✅ **APPROVED** |
| §4 edits applied | research session, on approval | 2026-08-22 | ✅ |

**Applied on approval**, per §4: `epics.md` (Stories 16.6 + 16.7 appended to Epic 16) ·
`sprint-status.yaml` (2 entries, `backlog`, with preconditions recorded inline) ·
`deferred-work.md` (`DF-16-6-A`, `DF-16-7-A`) · `tests/test_status_document_registry.py`
(registered at authoring time in `b4b9b92`, because `-22` closes in both directions).

⛔ **What approval does NOT do.** It spends no round, ratifies no member, moves no threshold, and
promotes no finding. `DF-13-5-A` remains **OPEN and UNSPENT** with its 2026-08-22 deferral and
re-review trigger intact. The gate outcome is **unchanged** — still `BLOCKED`. Approving the
proposal authorises the two stories to be *scheduled*; §2.2's preconditions still gate them, and
**Story 16.7 additionally requires protocol §2's QA Lead role to be filled**, which remains an
operator act nobody has taken.
