---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - argus/detectors/vacuous_test.py
  - argus/detectors/provenance_scan.py
  - _bmad-output/design-artifacts/ArgusAgent/research/technical-argusagent-detector-categories-research-2026-08-21.md
  - _bmad-output/design-artifacts/ArgusAgent/research/revalidate-fact-b-widening.py
  - _bmad-output/design-artifacts/ArgusAgent/research/investigate-per-call-scoping.py
  - _bmad-output/design-artifacts/ArgusAgent/validation-corpus/adjudication-set-13-5.json
  - _bmad-output/design-artifacts/ArgusAgent/deferred-work.md
workflowType: 'research'
lastStep: 4
research_type: 'technical'
research_topic: 'Why the vacuous-test verdict-eligible population is empty — a two-stage mismatch, measured'
research_goals: 'Answer the operator question of 2026-08-24: is the zero yield an implementation defect, or is the defect class simply rare in real repositories? Take the Epic 17 charter decision against measurement rather than assumption.'
user_name: 'XAgent007'
date: '2026-08-24'
web_research_enabled: false
source_verification: true
supersedes: 'nothing — this EXTENDS technical-argusagent-detector-categories-research-2026-08-21.md §6'
---

# The Two-Stage Mismatch: Why `vacuous_test` Cannot Promote Anything

**Date:** 2026-08-24
**Author:** XAgent007
**Research Type:** technical (measurement)
**Session:** operator-directed, no story — chartered to answer a question, not to change code

---

## 0. Provenance and honest scope

⛔ **This document changes no code, ratifies no member, spends no round and disposes of no ledger
entry.** It is a measurement record. Every number in it was produced on the operator's machine
against the **five pinned corpus shas** in `validation-corpus/adjudication-set-13-5.json`, by
harnesses committed beside this file, and every one is reproducible by running them.

⚠️ **It is NOT the first document to reach the central conclusion.**
[technical-argusagent-detector-categories-research-2026-08-21.md](technical-argusagent-detector-categories-research-2026-08-21.md)
§6 ("The Blindness Finding") already established, three days earlier, that fact (b) is structurally
blind to weakly-constrained results and that the round should not be spent before the predicate
changes. **This document corroborates that finding with an independent instrument and sharpens it in
two places where the earlier reading was too generous.** Where the two disagree, §4 says so
explicitly rather than quietly preferring the newer number.

**The operator's question, recorded verbatim so the answer can be checked against it:**

> *"I doubt more round of widening will bring in valid issues. May be these detectors are not
> implemented properly with best solution in mind based on design and coding best practices, or these
> detectors do not really could not found any issues in repos in general (because these are not very
> common issues in repos). What do you suggest after analyzing deep in current implementation?"*

Two hypotheses, with opposite consequences. **The measured answer is neither**, and §5 gives it.

---

## 1. Method, and why there are two instruments

The shipped detector is two stages, and this document measures each separately.

| Stage | Where | What it does |
|---|---|---|
| **1 — flagging** | `VacuousTestDetector._score` | FLAG iff `assertion_density < 1/4` **OR** `mock_ratio > 1/2` |
| **2 — corroboration** | `_ast_corroborated` → `provenance_evidence` | verdict-eligible iff ≥1 **discarded** SUT call, **zero consumed** SUT calls, **and** ≥1 assertion referencing a **mock-bound name** |

**Instrument A — the shipped code itself.** `revalidate-fact-b-widening.py` and
`measure-heuristic-arms.py` import and call `provenance_evidence` and `VacuousTestDetector._score`,
the real functions, over blobs read from each member's pinned sha into a scratch tree. No checkout is
touched and nothing is written outside that tree.

**Instrument B — CPython's own `ast` module.** `measure-mock-binding-idioms.py` re-derives mock
binding *without* argus's tree-sitter index, so the second reading is a genuine second opinion rather
than a re-read of the first. This matters: the question in §3 is precisely *"can the shipped resolver
see what is there?"*, and an instrument that shares the resolver cannot answer it.

⛔ **Harness validation, in the house form.** `revalidate-fact-b-widening.py` refuses to be trusted
unless the full shipped fact (b) reproduces **ZERO** promotions over the population, because the
2026-08-18 run recorded 0 blocking findings. It printed `harness trustworthy : YES`. A harness that
cannot reproduce the known result is a harness whose other numbers mean nothing.

---

## 2. The shipped predicate returns zero, and the "ceiling of six" is not what it sounds like

Over all **1,032** `vacuous_test_heuristic` findings, evaluated, 0 skipped as unresolvable:

| clause of fact (b) | count | share |
|---|---:|---:|
| no SUT call at all (`disc=0, cons=0`) | 8 | 0.8% |
| ≥1 **discarded** SUT call | 676 | 65.5% |
| **zero consumed** SUT calls | 14 | 1.4% |
| ≥1 **mock-referencing assertion** | **0** | **0.0%** |
| **shipped fact (b) — all three** | **0** | **0.0%** |

⛔ **The number the project has been quoting as "the corroborable ceiling is six" is `W1` — fact (b)
with its mock-referencing clause DELETED.** The shipped predicate's output is **0**, not 6, and has
been 0 on every run. Six is the count of findings that satisfy `discarded ≥1 AND consumed == 0`; the
third clause then removes all six. This is stated because a ceiling of six reads as *"nearly enough"*
and a floor of zero reads as *"structurally shut"*, and the second is the true one.

Distribution of `(discarded, consumed, mock_ref)` shapes, capped at 3 — **`mock_ref` is 0 in every
row that occurs**:

```
disc=0 cons=3 mref=0 -> 308      disc=0 cons=2 mref=0 -> 27
disc=1 cons=3 mref=0 -> 273      disc=1 cons=2 mref=0 -> 19
disc=2 cons=3 mref=0 -> 174      disc=1 cons=1 mref=0 -> 18
disc=3 cons=3 mref=0 -> 162      disc=0 cons=1 mref=0 -> 13
```

**917 of 1,032 (88.9%) carry three or more CONSUMED SUT calls.** The `consumed == 0` clause is
evaluated at **whole-function scope**, so one observed call anywhere in a test withholds corroboration
from the entire test.

**Per member.** ⚠️ Note the concentration, which bears on any claim of corpus breadth:

| member | flagged findings | share | `W1` | shipped |
|---|---:|---:|---:|---:|
| minions | 648 | 62.8% | 1 | 0 |
| agent-smith | 295 | 28.6% | 5 | 0 |
| agent-markovich | 72 | 7.0% | 0 | 0 |
| xagents-webapp | 17 | 1.6% | 0 | 0 |
| **ai-body-runtime** | **0** | **0.0%** | 0 | 0 |

⛔ **One of the five ratified members contributes NOTHING to this rule class**, and a single member
contributes **63%**. This is recorded as a fact about the denominator, not as an argument for a bigger
bench — §5 explains why a bigger bench is the wrong response.

---

## 3. The resolver gap is real, is NOT the cause, and must not be proposed as the fix

`_mock_bound_names` (`argus/detectors/provenance_scan.py:794`) recognises a name as mock-bound by
exactly two routes: an in-span assignment whose value is mock-derived, and `with … as m`. It
additionally rejects any dotted assignment target (`if name and "." not in name`).

**Three of the four dominant real-world Python mock idioms are therefore invisible to it:**

| idiom | example | visible? | why not |
|---|---|---|---|
| local assignment | `fake = Mock()` | ✅ | the one route implemented |
| `@patch` decorator injection | `@patch("m.dep")` → `def test(self, mock_dep)` | ❌ | bound by the signature, not by an in-span assignment |
| fixture / `mocker` injection | `def test(mocker)` | ❌ | bound in another function entirely |
| `setUp` + `self` attribute | `self.svc = Mock()` → `self.svc.assert_called()` | ❌ | binding is outside the span **and** the dotted target is rejected |

This looks like the obvious explanation for `mock_ref = 0`, and it is **wrong**. Instrument B
implements an extended resolver covering all four idioms and re-runs the question over the same 1,032:

```
MOCK-BINDING IDIOM (a test may use more than one)
  A_local_assign                 5  (  0.5%)   <- the only idiom the shipped resolver sees
  A_with_as                      2  (  0.2%)   <- the only idiom the shipped resolver sees
  Z_no_mock_binding_found     1025  ( 99.3%)

ASSERTION REFERENCES A MOCK-BOUND NAME
  shipped-equivalent resolver          :     1
  extended resolver (all four idioms)  :     1
  findings the RESOLVER GAP hides      :     0
```

⛔ **1,025 of 1,032 flagged tests bind no mock at all, by any idiom.** Teaching the resolver every
binding idiom in Python moves the count from 0 to 1. **The gap is a real latent defect and should be
filed, but it is not the cause of the empty population and fixing it would return the round to zero.**
It is recorded here specifically so that it is not rediscovered in six months and mistaken for the
remedy.

*(Instrument B reports 1 where the shipped code reports 0; the difference is B's deliberately looser
assertion vocabulary. Both round to "empty" and neither supports a promotion.)*

**Control — is this simply a corpus that never mocks?** No:

| member | test files | using mocks | share |
|---|---:|---:|---:|
| agent-smith | 95 | 22 | 23.2% |
| minions | 315 | 72 | 22.9% |
| agent-markovich | 26 | 3 | 11.5% |
| xagents-webapp | 6 | 0 | 0.0% |
| ai-body-runtime | 4 | 0 | 0.0% |

The corpus mocks. The **flagged population** does not.

---

## 4. The finding: the two stages target different defects

`measure-heuristic-arms.py`, attributing each flag to the arm that fired:

```
density floor = 1/4    mock ceiling = 1/2
  density_only   1025  (100.0%)
  mock_only         0  (  0.0%)
  both              0  (  0.0%)
```

⛔ **Stage 1's mock arm has never fired on the ratified corpus. Selection is 100% assertion-density.**
Stage 2 asks an exclusively mock-provenance question. **The population Stage 1 produces and the
population Stage 2 can judge are disjoint on this corpus — measured, not inferred.**

This is not a threshold that needs tuning and not a corpus that needs enlarging. It is two stages
built to different definitions of "vacuous":

- **Stage 1's definition:** *few assertions per statement* — a density property, and a proxy for
  test **style**.
- **Stage 2's definition:** *the asserted values derive from a mock rather than the SUT* — a
  provenance property, and a proxy for test **wiring**.

Within the flagged population, 54.5% carry exactly one assertion and 41.1% carry two or more; only
4.4% assert nothing at all. These are mostly *thin* tests, not *mock-wired* ones.

**Where this sharpens the 2026-08-21 research.** That document's §6 table marks *"result ignored,
assertions on a mock"* as ✅ verdict-eligible, and treats fact (b) as blind to the *most frequent*
instance of the defect while still able to catch its canonical one. **Measurement does not support the
second half:** that row is also empty, 0 of 1,032. Fact (b) is blind not to the most frequent
instance but to **every instance present in this corpus**. The practical consequence is a
re-weighting of that research's own recommendation #1 — of Story 6.2's two halves, **the provenance
half is worth approximately nothing here and the assertion-strength half is worth everything.**

⛔ **The reading error underneath all of this, stated plainly because both `DF-13-5-A` branches rest
on it.** *"0 blocking findings"* has been read as a fact about the world — either *the detector is too
conservative* (branch b) or *the corpus is too small* (branch a). **It is a fact about the
instrument.** No conclusion about how common vacuous tests are in real repositories is available from
this evidence, because the instrument has never been able to see the class it targets. The honest
statement is not *"the defect is rare"* — it is *"this measurement is silent on the base rate."*

---

## 5. Answer to the operator's question, and the recommendation

**Neither hypothesis, and the truth is more fixable than both.**

- **NOT "implemented without best practice."** The module is pure (`AR8`), deterministic (`NFR-D2`),
  exhaustively documented, and the Story 14.1 conformance repair — replacing a corroborator that
  agreed with its own input in 2,527 of 2,529 cases — was a correct and unusually honest call. The
  `consumed == 0` asymmetry is deliberate and is what keeps the false-accusation moat closed. ⛔
  **Nothing in this document argues for loosening it.**
- **NOT "the class is rare in repos."** Unavailable from this evidence (§4), and the external
  literature in the 2026-08-21 research points the other way: weak assertions are reported as the
  single most frequent defect in machine-written tests, and machine-written tests are a growing share.
- **The actual defect is architectural and sits BETWEEN the stages:** a selector graded on assertion
  *density* feeding a corroborator graded on mock *provenance*.

**Recommendation — Epic 17 is the assertion-strength epic.** Complete Story 6.2's dataflow /
scope-resolved grounding and extend it to grade **what an assertion actually constrains about the SUT
result**, *replacing* the mock-provenance vacuity signal rather than relaxing its clauses. This
aligns the two stages on one definition of vacuity: *the test runs the code and does not meaningfully
constrain what it returned*. Per the 2026-08-21 research it needs no new architecture, no execution
sandbox, no egress seam, and no additional adjudicator role.

**A cheap mock-free interim signal already exists in the project's own harness.**
`investigate-per-call-scoping.py`, re-run 2026-08-24:

| variant | definition | reach | share |
|---|---|---:|---:|
| `V0` shipped | `disc≥1 ∧ cons==0 ∧ mref≥1` | **0** | 0.0% |
| `V1` drop-mref | `disc≥1 ∧ cons==0` | 6 | 0.6% |
| `V2` silent | `disc≥1 ∧ the span asserts NOTHING` | 36 | 3.5% |
| `V5` unrelated | `disc≥1 ∧ asserts, none about the SUT` | **125** | **12.1%** |
| `V4` per-call | `disc≥1` alone | 676 | 65.5% — too loose |

`V5` depends on no mock, is computable from the same pure inputs, and is the shape closest to the
assertion-strength question. ⚠️ `DF-16-7-B` already records that `V2` is a **genuinely different
predicate** rather than a loosening of fact (b) and must be argued as one; **the same applies with
more force to `V5`**, and this document does not propose promoting either.

**Two constraints that belong in the Epic 17 charter, not in its aftermath:**

1. ⛔ **Yield and precision move in opposite directions.** Going from 0 to ~12% eligible mechanically
   increases exposure to false accusation, and precision at ≥80% is the entire gate. The precision
   guard must be **pre-registered before the widening lands**, in the discipline of the 2026-08-17
   rule — not measured afterwards against a number already in view.
2. ⛔ **This is a scope change to Story 6.2, not an absorption.** 6.2 is scoped as provenance
   grounding; assertion **strength** is a different question about the same dataflow. It goes through
   `bmad-correct-course` and is argued, per `DF-16-7-B`'s precedent.

**What this does NOT recommend:** spending `DF-13-5-A`'s round (§4 — a larger corpus of the same
blindness returns the same zero); taking branch (b) (its trigger conditions were never observed);
fixing the mock-binding resolver as a yield measure (§3 — worth 0→1).

---

## 6. Reproduction

From the repository root, with the five member checkouts present at the paths each harness names:

```
python _bmad-output/design-artifacts/ArgusAgent/research/revalidate-fact-b-widening.py
python _bmad-output/design-artifacts/ArgusAgent/research/investigate-per-call-scoping.py
python _bmad-output/design-artifacts/ArgusAgent/research/measure-mock-binding-idioms.py
python _bmad-output/design-artifacts/ArgusAgent/research/measure-heuristic-arms.py
python _bmad-output/design-artifacts/ArgusAgent/research/measure-flag-rate-inversion.py
```

The first four read **pinned blobs** and are reproducible from the object database alone. ⚠️
`measure-flag-rate-inversion.py` reads the live checkouts at **HEAD**, not the pins — it answers a
structural question about the instrument rather than a corpus question, and its numbers will drift as
those repositories move. It is labelled as such in its own docstring. Its result at time of writing:
among mock-using test files, flag rate 17.5% for mock-binding tests and 21.6% for mock-free ones, with
**`ast_corroborated` = 0 in every cell** — the same emptiness, reached from a different direction.

**Ledger entries filed from this document:** `DF-INV-VACUOUS-A` (the stage mismatch),
`DF-INV-VACUOUS-B` (the resolver gap, filed as a latent defect and explicitly NOT as the remedy).
`DF-13-5-A` carries a same-day append-only note sharpening its re-review trigger, whose metric this
document showed to be under-specified against a predicate replacement.
