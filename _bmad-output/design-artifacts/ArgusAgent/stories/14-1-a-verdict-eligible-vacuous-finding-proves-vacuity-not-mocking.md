# Story 14.1: A verdict-eligible vacuous finding proves vacuity, not mocking

Status: review

<!-- Created 2026-08-17 by create-story on HEAD 47b6dbe. Every premise below was re-measured BY
     EXECUTION before this file was written; see §0. The feasibility of the replacement predicate
     was measured OUT OF TREE and its numbers are in §0.2 — the approach is not a guess. §0.3
     carries a MEASURED ESCALATION the dev must read before writing a line of code. Validation is
     optional — run bmad-create-story:validate for a second pass before dev-story. -->

## Story

As the Argus maintainer,
I want the AST corroboration step to be evidence that the asserted values do not derive from the SUT,
So that a 🔴 rests on the fact cross-cutting concern #6 requires rather than on the presence of a mock.

This is **Epic 14's first story** and it is the one that repairs the false-accusation moat. It was
authorised by `sprint-change-proposal-2026-08-17.md`, **APPROVED by XAgent007 on 2026-08-17**, which
is the source document for every measurement quoted here.

### What this story IS

A **conformance fix**. Cross-cutting concern #6 (`architecture.md`) has required *"`audited_deep` AST
corroboration AND Prosecutor sign-off"* since the architecture was written. The shipped detector
grants `AUDITED_SHALLOW` with no sign-off, and its fact (b) reduces to *"the test constructs a
mock"*. This story makes fact (b) mean what the invariant already says it must.

### What it is NOT

- **NOT a threshold change.** `ASSERTION_DENSITY_FLOOR = Fraction(1, 4)` and
  `MOCK_RATIO_CEILING = Fraction(1, 2)` are **byte-unchanged**. A failed precision measurement is
  never a reason to move a threshold — protocol §5 and Story 13.3 / AC5 forbid it by name.
- **NOT Story 14.2's work.** `_count_statements` and `_ASSERTION_CALLEES` are **not touched here**.
  See the tension recorded at DN-4 — it is real and the dev must respect it.
- **NOT a claim of dataflow.** The V1 signal is name-level and a proxy. `DF-14-1-A` in
  `deferred-work.md` already records that limit and names Story 6.2 as the owner of real assertion
  provenance. **Cite it; do not re-file it.**
- **NOT the re-measurement.** This story does not re-audit the corpus or re-adjudicate anything.
  That is Story 13.5, and it does not begin until Epic 14 closes.
- **NOT a fix for `TC-ArgusAgent-VERDICT-001-30`'s fixture.** §0.3 is an **escalation**, recorded
  with two named options and a decision that is not the dev's alone to take.

---

## ⛔ WHY THIS STORY EXISTS — a moat that measured 0/26

Over the ratified 5-repository validation corpus the `vacuous_test_ast` rule class emitted **31
blocking findings** and the named human adjudicated **0** of them true: **26 FP / 5 BORDERLINE**.
All 31 are one rule class, and that rule class is the **only** verdict-eligible finding Argus ships
— the only thing that can take a user's build to 🔴.

The cause is `_ast_corroborated`'s fact (b):

```python
vacuity_signal = assertion_sites >= 1 and mock_sites >= 1
```

That is *"the test constructs a mock"*. It is **not** *"the asserted values do not derive from the
SUT output"*, which is what the docstring above it claims and what CC#6 requires. Measured across
**1,836** heuristically-flagged tests in the two contributing corpus members, `ast_corroborated` is
**equivalent to `mock_sites >= 1` in 1,835 cases** — facts (a) and (`assertion_sites >= 1`) never
independently excluded anything. The corroboration step adds no evidence the heuristic did not
already have; it re-reads one input and treats the agreement as confirmation.

---

## Acceptance Criteria

### AC1 — Fact (b) becomes evidence of vacuity, and the old equivalence is BROKEN, measured

1. `_ast_corroborated`'s fact (b) is replaced by a signal that **discriminates real vacuity from
   mock-using-but-valid tests**. The two facts stay two facts: fact (a) (reachability) is
   **unchanged**.
2. **The equivalence is re-measured on the same population and no longer holds.** Today
   `ast_corroborated == (mock_sites >= 1)` in 1,835 of 1,836 flagged tests. After this story, that
   number is measured again over the same two corpus members at their **unchanged pinned shas** and
   **recorded as a number in the Dev Agent Record**. A story that does not report this number has
   not demonstrated the fix.
3. **A test whose assertions constrain the real SUT result is NOT corroborated**, however many
   mocks it constructs.
4. **A SUT call inside a `pytest.raises` / `assertRaises` / `pytest.warns` context counts as
   result-CONSUMED**, because raising *is* the observation. This is a **known defect in the §0.2
   feasibility probe**, specified here so it is designed in rather than inherited.
5. **The conservative default is preserved and is the moat.** Where the unresolved 1.4 edge set
   (`DF-1-4-A`) cannot establish fact (b), corroboration is **NOT granted** and the finding stays
   `vacuous_test_heuristic` / advisory. It must never fabricate corroboration.

### AC2 — Recall on the planted defects is PRESERVED and MEASURED, not assumed

1. Cartridges **`vacuous_basic`**, **`holdout_vacuous`** and **`nonascii_unicode`** each still emit
   `vacuous_test_ast` and still BLOCK (`max_blocking=1`, `expected_exit=2`). `holdout_vacuous` is
   the **anti-overfitting control** (DN-HOLDOUT) and `nonascii_unicode` carries a Cyrillic `тесты/`
   directory — both must pass for the same reason as `vacuous_basic`, not by special-casing.
2. **The measured recall is recorded as a number** (`N/3`), not asserted. §0.2 measured 3/3 with the
   candidate predicate; the dev re-measures against the real implementation.
3. **No cartridge, golden key or `CartridgeSpec` is edited to make this pass.** Changing the corpus
   to fit the detector is the move `tests/test_module_size_ceiling.py:35-39` files as a defect and
   Story 13.3 / AC5 forbids. If a cartridge legitimately must change, that is an **escalation**, not
   a task.

### AC3 — Precision on the adjudicated locators is MEASURED

1. The **31 adjudicated locators** are re-scored at their pinned shas (`minions` `ec63b729`,
   `agent-smith` `9ab774d7` — reachable, see §0.4) and the count that **remain verdict-eligible** is
   recorded. §0.2 measured 1 of 31 surviving with the candidate predicate.
2. **The surviving finding(s) are named and characterised**, not just counted. §0.2's single
   survivor is `agentsmith-core/tests/test_ir_copilot.py:128`, which the named human adjudicated
   **BORDERLINE — not FP** — for the same reason the predicate keeps it. A survivor that the human
   also could not call clean is a different result from a survivor the human called wrong, and the
   record must be able to tell them apart.
3. **The promotion rate over the whole minions test tree is recorded** (3,509 test functions; 24
   promotions today).

### AC4 — `TC-ArgusAgent-DETECT-001-86` is RE-AUTHORED as an intended behaviour change

1. That test currently pins corroboration on a test that asserts on the **real SUT result**
   (`assert sut`, where `sut = widget_under_test(m, dep)`). Under a correct fact (b) it **must not
   corroborate**.
2. It is **re-authored with the reason recorded in the story** — never silently adjusted until it
   matches the new output. The re-authored test must pin the **new** contract: a mock-heavy test
   that asserts on the SUT result is **advisory**, and a test that asserts on a mock-derived value
   while discarding the SUT result is **corroborated**.
3. `TC-ArgusAgent-DETECT-001-87` (advisory-only when no mock signal) and `-88` (the MANDATORY
   false-accusation guard: a genuine test is not flagged) **must still pass unchanged**. `-88` is
   the moat's own test and it is not this story's to weaken.

### AC5 — Purity, determinism and the contract surface are untouched

1. **AR8** — the scorer stays PURE: no I/O, no clock, no LLM, no `uuid4`/`random`, no network. The
   new predicate reads only the source text already passed in and the pre-built 1.4 `AstIndexEntry`.
2. **AR4** — ratios stay exact `Fraction`, never `float`. No new `float` field enters
   `VacuousTestScore`, and the emitted finding still round-trips the float-rejecting serializer
   (`TC-ArgusAgent-DETECT-001-92`).
3. **NFR-D2 / determinism** — no iteration-order, `set`-ordering or dict-ordering dependence in
   anything reaching a `.argus/`-bound output. Any set rendered into a message is `sorted()`.
4. **`VacuousTestScore` is a frozen `extra="forbid"` model.** If the new predicate needs new evidence
   counts, adding a field is a **schema change to a finding-borne model** — state whether one was
   added, and if so that the round-trip test still passes.
5. **`RULE_AST` / `RULE_HEURISTIC` vocabulary is unchanged**, and the eligibility surface read by
   Story 1.6 is unchanged: heuristic → `advisory=True` + `depth_supported=None`; corroborated →
   `advisory=True` + `depth_supported=AUDITED_SHALLOW` + `rule_id="vacuous_test_ast"`.

### AC6 — Nothing 14.2 owns is touched

1. `_count_statements`, `_ASSERTION_CALLEES`, `_MOCK_CALLEES`, `ASSERTION_DENSITY_FLOOR` and
   `MOCK_RATIO_CEILING` are **byte-unchanged by this story**. Confirm with `git diff` and say so.
2. **The heuristic flag rate does not change.** It is 51.6% of test functions on the minions tree
   today (1,812 of 3,509); after this story it must be **identical**, because this story changes
   only which flagged tests are PROMOTED. Re-measure and report — a changed flag rate means fact
   (b)'s replacement leaked into the flag path.

### AC7 — Gates, blast radius, and hand-off

1. **All three gates run locally with ACTUAL numbers, as deltas against the §0.1 baselines** — never
   "all green". `pytest` **1597 collected**, `mypy argus` **Success, 86 source files**,
   `bandit -r argus` **19 Low / 0 Medium / 0 High** (confidence 0/0/6/13). Label them **LOCAL** and
   record that **CI evidence is NOT ESTABLISHED**. A skip appearing is a regression signal.
2. **The full suite is the gate, and the blast radius is wider than the detector's own tests.** §0.5
   enumerates **10 test modules that run the detector end-to-end** over a staged cartridge. Run the
   FULL suite; do not run the detector's own file and call it done.
3. **`test_dogfood_artifact_currency.py` may fire.** Committed dogfood artifacts are
   detector-output-dependent. If it goes red, regenerate **through the existing renderers**
   (`scripts/regenerate_dogfood_artifacts.py`) — never by hand-editing an artifact.
4. **HAND OFF GREEN**, and run the full suite **after** the last prose edit (`AI-E13-1`:
   `stories/*.md`, `architecture.md` and `deferred-work.md` are TESTED ARTIFACTS here).
5. **Nothing outward-facing.** `git tag -l` is empty and stays empty. Nothing is committed.

---

## Developer Context & Guardrails

### §0 — Premise re-measurement (this project's create-story control)

Measured **2026-08-17 on `47b6dbe`**, **by execution**. Per `AI-E12-10`, confirmations are recorded
as well as divergences. **Re-measure on your own baseline (Task 0) — inherit nothing.**

| Premise | Re-measured on `47b6dbe` | Consequence |
|---|---|---|
| Fact (b) is `assertion_sites >= 1 and mock_sites >= 1` | ✅ **CONFIRMED**, `argus/detectors/vacuous_test.py:622` | The whole story |
| `ast_corroborated` ≡ `mock_sites >= 1` | ✅ **1,835 of 1,836** flagged tests, both contributing members | AC1.2 |
| The rule class measured 0 TP / 26 FP / 5 BORDERLINE | ✅ **CONFIRMED** from the committed adjudication record | Why this is P1 |
| CC#6 requires `audited_deep` corroboration **AND** Prosecutor sign-off | ✅ **CONFIRMED**, `architecture.md` §Cross-Cutting #6 | This is a CONFORMANCE fix |
| The detector ships `AUDITED_SHALLOW`, no sign-off | ✅ **CONFIRMED**, `vacuous_test.py:519` | The divergence |
| The Prosecutor does not gate this class | ✅ **CONFIRMED** — `prosecutor.py:56-57` leaves an ALREADY-eligible finding UNCHANGED, and `pipeline.py:535` passes **no `sign_offs`** | Do not "fix" it in the Prosecutor |
| `argus/detectors/vacuous_test.py` size | **623 lines**, headroom **577** to the 1200 ceiling | No 13-4-class deadlock here |
| `argus/pipeline.py` size | ⚠️ **1111 lines, headroom 89** | **Do not add to `pipeline.py`.** It is the nearest file to the ceiling and it is NOT exempt |
| `tests/test_vacuous_detector.py` size | 324 lines, headroom 876 | Room for the re-authored `-86` |
| Baseline gates | ✅ `pytest` **1597 collected / 1597 passed / 0 failed / 0 skipped** exit 0 · `mypy argus` **Success, 86 files** · `bandit` **19 Low / 0 Med / 0 High** (0/0/6/13) | AC7.1 deltas |
| Working tree is clean | ❌ **NO — and this is expected.** The approved correct-course change (6 governance artifacts + `sprint-change-proposal-2026-08-17.md`) and completed Story 13.4 are uncommitted | Your diff will contain them. **They are not yours** |
| `git tag -l` | ✅ **EMPTY** | AC7.5 |
| A `project-context.md` exists | ❌ **NONE.** `architecture.md`, `deferred-work.md`, the retrospectives and this file **are** the context | — |

### §0.1 — The three baselines, verbatim

```
pytest --collect-only  -> 1597 tests collected
pytest                 -> all passed, 0 failed, 0 skipped, exit 0
mypy argus             -> Success: no issues found in 86 source files
bandit -r argus        -> 19 Low / 0 Medium / 0 High; confidence 0 / 0 / 6 / 13
```

### §0.2 — FEASIBILITY, measured out of tree. The approach is NOT a guess

The planted-vacuous cartridges carry a signature the 31 false positives do not: **the SUT is called
with its result DISCARDED**, and **the assertion is on a value bound from a separately configured
mock**. `vacuous_basic` is the canonical shape:

```python
def test_compute_total_is_vacuous():
    compute_total([1, 2, 3])       # SUT reached, result THROWN AWAY
    fake = Mock()
    fake.calculate.return_value = 6
    pretended = fake.calculate()   # value bound from a MOCK-derived call
    assert pretended == 6          # ...and that is what is asserted
```

A probe implementing exactly that — bind mock names; classify a call whose receiver is a mock-bound
name as mock-derived rather than SUT; require that **no** SUT call's result is consumed; require
that an assertion references a mock-bound value — scored:

| Population | Requirement | Measured |
|---|---|---|
| 3 planted cartridges (incl. the **holdout** and the non-ASCII one) | keep corroboration | **3 / 3 kept** |
| 31 adjudicated findings | lose corroboration | **30 / 31 demoted** |
| Whole minions test tree (3,509 test functions) | — | promotions **24 → 0** |

The single survivor, `test_ir_copilot.py:128`, is the one finding the human adjudicated
**BORDERLINE** rather than FP, for the same reason the probe keeps it.

**The probe is at**
`C:\Users\varin\AppData\Local\Temp\claude\d--ProjectX-XAgents-XAgents-ArgusAgent\a0a156c9-4444-4213-b9e7-eb84768c5358\scratchpad\probe_predicate.py`.
**It is a FEASIBILITY MEASUREMENT, not a design, and not production quality** — it uses regexes over
source lines, it is not pure in the AR8 sense, and it has the raises-context defect AC1.4 names. You
own the real implementation. **Do not copy it; do not re-derive the approach from scratch either.**

### §0.3 — ⛔ MEASURED ESCALATION: the default blocking path may disappear. READ BEFORE CODING

`tests/test_default_path_blocking_verdict.py::test_TC_ArgusAgent_VERDICT_001_30` runs a **default
`run_audit_detailed`** — no flags, no deep pass, no LLM, no cartridge harness — and asserts the
verdict is `NOT_READY_FOR_RELEASE` with a blocking finding **from `RULE_AST` specifically**. Its own
failure message reads:

> *"Do NOT adjust a gate to make this pass — report it and escalate. The externalization guard's
> causal claim, and Story 12.4's statement about the default path, both depend on this answer."*

**Its planted test does NOT survive the candidate predicate. Measured:**

```python
def test_add_is_vacuous():
    first = MagicMock(); second = MagicMock()
    result = add(1, 2)             # SUT result is BOUND
    assert first is not None       # mock assertion
    assert second is not None      # mock assertion
    assert result is not None      # ...but this one CONSTRAINS THE SUT RESULT

probe -> flagged=True  OLD corrob=True  NEW corrob=False
         sut_calls=['add']  consumed_sut=['add']   <- fact (b) correctly fails
```

**The predicate is arguably RIGHT and the fixture is arguably not vacuous** — `assert result is not
None` is a real, if weak, constraint on the SUT output. But the consequence is product-level, not
cosmetic: **it is the test proving a zero-token, no-sign-off blocking path exists at all.** If it
cannot be satisfied, Argus can no longer block anything without LLM or sign-offs, which is the same
consequence `sprint-change-proposal-2026-08-17.md` §2.5 records for the precision gate.

**Two named options. This is an ESCALATION — do not simply pick one silently:**

- **(A) Strengthen the fixture** so the planted test is genuinely vacuous under the corrected
  definition (discard the SUT result; assert a mock-derived value), matching the cartridge shape.
  *Argument for:* the fixture was written against the old, wrong definition and is not actually a
  vacuous test. *Argument against:* editing a fixture so a test passes is the move this repository
  distrusts on sight, and `-30`'s message says escalate.
- **(B) Accept that the default path no longer blocks**, record it, and escalate to the operator —
  it changes what the tool claims about itself in `README`, `action.yml` and Story 12.4's statement.

**Whichever is taken, it is recorded with its reasoning in the Dev Agent Record and surfaced in the
hand-off. Do not resolve it by weakening the predicate.**

### §0.4 — `agent-smith`'s pinned sha IS reachable

`DF-13-3-A` records it as unreachable; that entry carries a dated **correction** (2026-08-17): the
repository is at `D:/ProjectX/XAgents/XAgents/XAgents/Agent-Smith` — depth **five**, one level past
the depth-4 scan that filed it — `origin` matches, and `9ab774d7bf5d61da552c61094b2d478f72dfbb6d`
is that checkout's `HEAD`. So AC3's re-scoring can use the **true pinned trees for both members**.
Read every file via `git show <sha>:<path>`; both checkouts have moved. **Pass the Windows path form
to `git -C` from Python — a Git-Bash `/d/...` path fails there with exit 128** (paid for already).

### §0.5 — BLAST RADIUS, measured: 10 modules run the detector end to end

21 test modules reference `vacuous_test_ast` / `RULE_AST`. **11 use it only as a synthetic
`rule_id` literal** and cannot be affected. **These 10 stage a cartridge or run the detector and
CAN be:**

```
test_cartridge_selfaudit.py          test_dogfood_proof.py
test_critical_eligibility_pipeline.py test_evidence_bundle.py
test_detector_base.py                 test_grammar_runtime_validation.py
test_dogfood_plan.py                  test_pipeline_signature_demo.py
test_precision_replay.py              test_vacuous_detector.py
```

Plus `test_default_path_blocking_verdict.py` (§0.3), which the classifier scored "synthetic" because
it builds its corpus inline — **the classifier was wrong about that one and it is the highest-risk
module of all**. Treat the enumeration as a floor, not a ceiling: **run the full suite**.

`test_pipeline_signature_demo.py` is the FR32 signature demo — the `🔴 tests *appear* vacuous`
line that the PRD calls *"the product"*. If it goes red, that is not a test failure to fix quietly;
it is the demo changing, and it belongs in the hand-off.

### Locked decisions this story must CITE rather than reopen

| Locked | Where | Consequence here |
|---|---|---|
| **CC#6 — a heuristic finding cannot move the verdict without AST corroboration AND sign-off** | `architecture.md` §Cross-Cutting #6 | The rule this story conforms to. **Do not re-derive it** |
| **Vacuity-corroboration enforcement** | `architecture.md` §Enforcement (added 2026-08-17) | The paragraph this story implements |
| **The conservative default IS the moat** | `vacuous_test.py` docstring, "the false-accusation moat" | AC1.5 |
| **A false 🔴 is the lethal failure; a real vacuous test left advisory is tolerable** | same | The asymmetry that decides every judgement call here |
| **A failed measurement is not a reason to amend a threshold** | protocol §5; Story 13.3 / AC5 | AC6.1 — thresholds are byte-unchanged |
| **Narrowing a population until it goes green is a defect** | `test_module_size_ceiling.py:35-39` | AC2.3 — do not edit a cartridge to pass |
| **AR7 / single implementation** | `architecture.md` §Enforcement | One predicate, one place. Do not fork a second scorer |
| **AR8 — the scorer is PURE** | `vacuous_test.py` module docstring | AC5.1 |
| **AR4 — `Fraction`, never `float`** | same | AC5.2 |
| **Full dataflow grounding is Story 6.2's** | `DF-14-1-A`; 1.5 module docstring | Cite the limit; do not attempt dataflow here |
| **`AI-E9-8`** — never leave an entry without a named owner | Epic-9 retro | Anything deferred gets an owner |

### Decisions taken by this story (record each with its rejected alternative)

- **DN-1 — fact (b) is replaced, not supplemented.** The predicate becomes a statement about
  *provenance shape* (is the SUT result discarded? is the asserted value mock-bound?) rather than
  about *mock presence*. *Rejected alternative:* keeping `mock_sites >= 1` and AND-ing a new
  condition onto it. That reads as safer and is not: it preserves the term that measured
  1,835/1,836 equivalent with the outcome, so the predicate would still be dominated by "a mock
  exists" and the story would be unable to show the equivalence broken (AC1.2).
- **DN-2 — the signal is derived from source text plus the 1.4 edge set, and stays NAME-LEVEL.**
  *Rejected alternative:* real dataflow/scope resolution. That is Story 6.2's scope, it needs a
  resolved call graph the 1.4 index does not provide (`DF-1-4-A`), and attempting it here would
  quietly widen a conformance fix into an epic.
- **DN-3 — a raises-context SUT call is CONSUMED** (AC1.4). *Rejected alternative:* treating it as
  discarded, which is what the feasibility probe does. It is wrong: `with pytest.raises(X):
  sut(...)` observes the SUT's behaviour precisely, and treating it as vacuous would re-create the
  false-accusation class on fail-closed tests — a shape this corpus is full of.
- **DN-4 — the predicate must NOT be tuned to the current assertion-name undercount.** `_ASSERTION_CALLEES`
  misses `pytest.raises`, every `unittest.mock` assertion method and project helpers; **Story 14.2
  widens it.** Any threshold or branch in fact (b) that depends on today's `assertion_sites` value
  will silently change meaning when 14.2 lands. *Rejected alternative:* fixing the name list here to
  remove the tension — it is 14.2's AC and doing it here makes two stories un-reviewable
  independently.

### Files to touch

| Path | Action |
|---|---|
| `argus/detectors/vacuous_test.py` | **UPDATE** — `_ast_corroborated` and its helpers. 623 lines, headroom 577 |
| `tests/test_vacuous_detector.py` | **UPDATE** — re-author `-86` (AC4); add coverage for the new predicate |
| `_bmad-output/design-artifacts/ArgusAgent/stories/14-1-...md` | **UPDATE** — Dev Agent Record, File List, Change Log |
| `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` | **UPDATE** — `14-1` status only |
| `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` | **APPEND ONLY**, and only if something is deferred |
| Dogfood artifacts | **REGENERATE via `scripts/regenerate_dogfood_artifacts.py` only if `test_dogfood_artifact_currency.py` fires** |
| **Everything else** | **DO NOT TOUCH.** In particular: `argus/pipeline.py` (89 lines of headroom), `argus/verdict/prosecutor.py`, `argus/verdict/verdict_gate.py`, every cartridge under `tests/cartridges/`, `tests/corpus/_manifest.py`, `validation-corpus/**`, and the six governance artifacts carrying the uncommitted correct-course change |

### Previous story intelligence — traps already paid for

- **`AI-E13-1` — hand off green.** Story 13.3's SM phase wrote a story file, nothing re-ran the
  suite, the commit was pushed, and `audit-ci` went red on ubuntu. Run the full suite **after** your
  last prose edit.
- **Story 13.4 (immediately prior) paid for two things you inherit.** (a) **Line numbers in this
  repository drift constantly** — 13.4 found `test_module_size_ceiling.py:34`'s cite already stale
  before it touched anything. Locate every block by **anchor text**. (b) **Guards going RED on a
  full run are usually guards WORKING** — 13.4 hit the `DOCS-001-22` closure and did not loosen it.
- **`story_closure_claims` is LINE-SCOPED** (`test_governance_record_integrity.py:58-72`). **Never
  put a `DF-*` id on the same line as `CLOSED`, `Closes` or `closes`** unless `deferred-work.md`
  really carries that closure. `DOCS-001-78` globs `stories/*.md` and this file is inside it.
- **A new status document must be registered in the SAME change that creates it** — the rule added
  to `architecture.md` §Enforcement by Story 13.4. This story creates none, but if it produces a
  retrospective or proposal, register it in `tests/test_status_document_registry.py` immediately.
- **Windows-only local gates, ubuntu CI matrix.** This repo has shipped POSIX-only bugs out of a
  green Windows run. **Your predicate does source-text scanning**, which is the highest-risk shape
  for this: line splitting, `\r\n` vs `\n`, and any regex anchored with `$`. See Testing
  requirements.

### Testing requirements

- **Platform neutrality is not optional, and this story is the most exposed one in the epic.** The
  predicate reads source lines. Use `str.splitlines()` (already how the detector receives them) and
  never assume `\n`; never write a regex whose `$` or `\s` behaviour differs on CRLF input; never
  compare a path to a hand-built string; `pathlib` only; explicit `encoding="utf-8"` on every read.
  **Add at least one test that feeds the scorer CRLF source text and asserts an identical score** —
  that is the cheapest possible insurance against the `AI-E13-1` class and nothing today covers it.
- **Non-ASCII must keep working.** `nonascii_unicode` carries a Cyrillic `тесты/` directory and a
  `café_calc.py`. Any name-matching you add must be Unicode-safe.
- **RED-then-green at the real seam.** Demonstrate the new predicate RED on a genuinely vacuous test
  and GREEN on a genuine one, from the real detector — not from a reconstruction.
- **Non-vacuity travels with the assertions.** If a new helper can return "not corroborated" for a
  reason that never occurs, it is decoration. Every branch of fact (b) needs a test that reaches it.
- **The full suite is the gate** (§0.5), plus `mypy argus` and `bandit -r argus`, reported as
  numbers.

---

## Tasks & Subtasks

- [x] **Task 0 — Re-measure the premise on your own baseline (AC: 7.1)**
  - [x] Record HEAD. Re-run the three gates; report divergence from §0.1 as a finding.
  - [x] Re-measure `ast_corroborated ≡ mock_sites >= 1` over both corpus members — expect 1,835/1,836.
  - [x] Re-measure the flag rate (expect 1,812 / 3,509 = 51.6%) so AC6.2 has a before-number.
  - [x] Confirm §0.3 by execution: run `TC-ArgusAgent-VERDICT-001-30` and confirm it passes TODAY.
- [x] **Task 1 — Design and implement the new fact (b) (AC: 1, 5)**
  - [x] Write the predicate. Keep fact (a) unchanged. Keep it PURE (AR8) and `Fraction`-only (AR4).
  - [x] Implement DN-3: a raises-context SUT call is CONSUMED.
  - [x] Preserve the conservative default: cannot establish ⇒ not corroborated.
  - [x] Record in the Dev Agent Record whether `VacuousTestScore` gained a field, and if so that the
        float-rejecting round-trip still passes.
- [x] **Task 2 — Re-author `TC-ArgusAgent-DETECT-001-86` (AC: 4)**
  - [x] Re-author it against the NEW contract, with the reason written down.
  - [x] Confirm `-87` and `-88` pass **unchanged**; `-88` is the false-accusation guard.
  - [x] Add coverage for each branch of the new predicate, including the CRLF case.
- [x] **Task 3 — Measure recall on the planted defects (AC: 2)**
  - [x] Run the three vacuous cartridges. Record `N/3`.
  - [x] If any fails: **STOP and escalate.** Do not edit a cartridge.
- [x] **Task 4 — Measure precision on the adjudicated locators (AC: 3)**
  - [x] Re-score all 31 at their pinned shas (§0.4). Record how many remain verdict-eligible.
  - [x] Name and characterise every survivor; state its human disposition.
  - [x] Record the minions-wide promotion rate (24 today).
- [x] **Task 5 — Confirm 14.2's surface is untouched (AC: 6)**
  - [x] `git diff` proves `_count_statements`, `_ASSERTION_CALLEES`, `_MOCK_CALLEES`,
        `ASSERTION_DENSITY_FLOOR`, `MOCK_RATIO_CEILING` byte-unchanged.
  - [x] Re-measure the flag rate; it must equal Task 0's number.
- [x] **Task 6 — Work the blast radius and resolve §0.3 (AC: 7.2, 7.3)**
  - [x] Run the FULL suite. For each of the 10 end-to-end modules that fires, record which and why.
  - [x] **Resolve §0.3 explicitly**: take option (A) or (B), write the reasoning down, and surface it
        in the hand-off. Do NOT weaken the predicate to avoid the choice.
  - [x] If `test_dogfood_artifact_currency.py` fires, regenerate through the renderers only.
        (It did NOT fire. Two OTHER dogfood guards did — see the hand-off item in Completion Notes.)
  - [x] If `test_pipeline_signature_demo.py` fires, say so prominently — that is the product's demo.
        (It did NOT fire. The FR32 demo is intact.)
- [x] **Task 7 — Gates and hand-off (AC: 7)**
  - [x] Three gates, actual numbers, as deltas against §0.1. Label LOCAL; CI **NOT ESTABLISHED**.
  - [x] Full suite **after** the last prose edit.
  - [x] Dev Agent Record, File List, Change Log. Confirm `git tag -l` empty, nothing committed.

---

## Dev Agent Record

### Agent Model Used

`claude-opus-5[1m]` (Claude Opus 5, 1M context) via the BMAD `dev-story` worker, 2026-08-17.

### Debug Log

**HEAD at start: `47b6dbe`.** Nothing committed; `git tag -l` empty at start and at hand-off.

#### Task 0 — the baselines, MEASURED (and one divergence from §0.1)

| Gate | §0.1 | Measured here | Δ |
|---|---|---|---|
| `pytest` collected | 1597 | **1597** | 0 |
| `pytest` result | 1597 passed / 0 failed / 0 skipped, exit 0 | **1597 passed / 0 failed / 0 skipped, exit 0** | none |
| `mypy argus` | Success, 86 source files | **Success, 86 source files** | none |
| `bandit -r argus` | 19 Low / 0 Med / 0 High (conf 0/0/6/13) | **19 Low / 0 Med / 0 High (conf 0/0/6/13)** | none |

`TC-ArgusAgent-VERDICT-001-30` **passed today**, confirming §0.3 by execution before any code moved.

⚠️ **DIVERGENCE — the §0 corpus population numbers do not reproduce, and mine are used instead.**
Re-measured by execution through the SHIPPED detector and the SHIPPED 1.4 index, over both members
staged at their unchanged pinned shas (`git show <sha>:<path>` into a temp tree, Windows path form
passed to `git -C`):

| Population | §0 says | Measured here (before) |
|---|---|---|
| minions test functions | 3,509 | **3,551** |
| minions heuristically flagged | 1,812 (51.6%) | **1,848 (52.0%)** |
| minions promotions | 24 | **27** |
| agent-smith test functions | — | **1,122** |
| agent-smith heuristically flagged | — | **681** |
| both members, flagged | 1,836 | **2,529** |
| `ast_corroborated == (mock_sites >= 1)` | 1,835 / 1,836 | **2,527 / 2,529** |
| the 31 adjudicated locators, verdict-eligible | 31 | **31 / 31** |

The divergence is a POPULATION difference, not a behaviour difference, and it is not intake:
applying `argus.intake.ignore_rules.classify_path` with the members' own corroborated Tier-2 set
changes nothing (3,551 → 3,551; 1,122 → 1,122). §0's figures came from the out-of-tree probe;
these come from the shipped code. The harness is validated by the strongest check available: it
reproduces **all 31** adjudicated blocking findings as verdict-eligible at the pinned shas, which
is the ground truth the adjudication record was built from. Per §0 ("inherit nothing"), every
before/after comparison below is against MY baseline, over an identical population.

#### AC1.2 — the equivalence, re-measured on the SAME population

| | before | after |
|---|---|---|
| flagged tests, both members | 2,529 | **2,529 (identical)** |
| `ast_corroborated == (mock_sites >= 1)` | **2,527 / 2,529** | **2,493 / 2,529** |
| …on the sub-population where the two terms CAN differ (`mock_sites >= 1`, n=36) | **34 / 36** | **0 / 36** |
| promotions, both members | 34 | **0** |

The whole-population figure is dominated by agreement on False/False (only 36 of 2,529 flagged
tests construct a mock inside the test span at all), which is why the sub-population row is the
one that answers AC1.2: **the two terms now disagree on every single test where they could
possibly differ.** The corroboration step is no longer a re-reading of one of its own inputs.

#### AC2 — cartridge recall, MEASURED through the real pipeline

`stage_cartridge` → default `run_audit_detailed`, no flags, no LLM:

```
vacuous_basic    : verdict=NOT_READY_FOR_RELEASE exit=2 (expected 2) blocking=1 (max 1) eligible vacuous_test_ast=1 -> PASS
holdout_vacuous  : verdict=NOT_READY_FOR_RELEASE exit=2 (expected 2) blocking=1 (max 1) eligible vacuous_test_ast=1 -> PASS
nonascii_unicode : verdict=NOT_READY_FOR_RELEASE exit=2 (expected 2) blocking=1 (max 1) eligible vacuous_test_ast=1 -> PASS
CARTRIDGE RECALL = 3/3
```

**RECALL = 3/3.** No cartridge, golden key or `CartridgeSpec` was read for edit, let alone edited
(`git status --porcelain -- tests/cartridges tests/corpus` is empty). The holdout
(`holdout_vacuous`, the anti-overfitting control) and the Cyrillic-pathed `nonascii_unicode` pass
for the same structural reason as `vacuous_basic` — the predicate keys on the shape all three
share, not on any of their names.

#### AC3 — precision on the 31 adjudicated locators, at their pinned shas

**Verdict-eligible survivors: 0 of 31.** All 24 minions FPs and all 7 agent-smith rows (2 FP,
5 BORDERLINE) are demoted to `vacuous_test_heuristic` / advisory. Minions-wide promotion rate:
**27 → 0** over 3,551 test functions; both members **34 → 0** over 4,673.

**The §0.2 probe's single survivor is named, and the reason it does not survive here is DN-3.**
That survivor was `agentsmith-core/tests/test_ir_copilot.py:128`
(`test_always_invalid_fails_closed_with_typed_error`), which the named human adjudicated
**BORDERLINE — not FP**. Its SUT call is:

```python
client = MagicMock(spec=LLMClientPort)
client.generate_structured_output.return_value = invalid
with pytest.raises(CopilotTranslationError):
    propose_commands(NL, client=client)                 # <- inside a raises context
assert client.generate_structured_output.call_count == MAX_RETRIES + 1
```

The probe scored `propose_commands(...)` as "result discarded" — the defect AC1.4 specified to
design in rather than inherit. Here it is CONSUMED, because raising IS the observation, so the
finding is demoted. So the surviving-count difference (1 → 0) is not a stricter predicate: it is
exactly DN-3 doing what the story asked for, on exactly the test the probe's defect was about.
There is therefore **no survivor to characterise as "the human also could not call it clean"**;
the record can still tell the two classes apart because every demoted row keeps its human
disposition in `adjudication-record.json`, which this story did not touch.

#### AC6.2 — the flag rate did NOT change

| | before | after |
|---|---|---|
| minions flagged / test functions | **1,848 / 3,551 = 52.0%** | **1,848 / 3,551 = 52.0%** |
| agent-smith flagged / test functions | **681 / 1,122** | **681 / 1,122** |

Byte-identical on both members: fact (b)'s replacement did not leak into the flag path. Only which
flagged tests are PROMOTED moved.

#### RED-then-green at the real seam

Both directions were driven from the REAL detector over the REAL tree-sitter index before any test
was rewritten (four fixtures staged to disk, `build_ast_index`, `VacuousTestDetector().run`):

```
test_cart.py   (cartridge shape: SUT discarded, mock-derived assertion)  -> vacuous_test_ast        AUDITED_SHALLOW
test_new30.py  (the new -30 witness)                                     -> vacuous_test_ast        AUDITED_SHALLOW
test_old30.py  (the old -30 fixture: SUT result bound and asserted)      -> vacuous_test_heuristic  None
test_raises.py (SUT call inside `with pytest.raises(...)`)               -> vacuous_test_heuristic  None
```

The last two are the RED half — they were `vacuous_test_ast` before this change and are advisory
after. `-88`, the false-accusation guard, is **byte-unchanged and passing**; so is `-87`.

#### AC7.1 — the three gates after the change (LOCAL; CI evidence is NOT ESTABLISHED)

| Gate | §0.1 baseline | After | Δ |
|---|---|---|---|
| `pytest` collected | 1597 | **1605** | **+8** (the eight new `-101`..`-108` cases; no test deleted) |
| `pytest` | 1597 passed / 0 failed / **0 skipped** | **1603 passed / 2 failed / 0 skipped** | **+2 failed** — both are the dogfood artifact-currency bootstrap; see the hand-off item |
| `mypy argus` | Success, 86 source files | **Success, 86 source files** | **0** |
| `bandit -r argus` | 19 Low / 0 Med / 0 High (0/0/6/13) | **19 Low / 0 Med / 0 High (0/0/6/13)** | **0** |

**No skip appeared** (a skip would itself be the regression signal AC7.1 names). These are LOCAL
Windows numbers; **CI evidence is NOT ESTABLISHED for this delta** — nothing was pushed and no
workflow ran over it, and this repository has shipped POSIX-only bugs out of a green Windows run
before (`AI-E13-1`), which is why `-107` (CRLF) and `-108` (non-ASCII identifiers) exist.

#### AC7.2 — the blast radius, worked

Of the 10 modules §0.5 enumerates as running the detector end to end, plus the highest-risk
eleventh, **four fired**:

| Module | Fired | Why, and what was done |
|---|---|---|
| `test_vacuous_detector.py` | ✅ | `-86` and `-94` pinned the OLD fact (b). RE-AUTHORED as an intended behaviour change with the reason committed beside them (AC4). |
| `test_default_path_blocking_verdict.py` | ✅ | §0.3, exactly as predicted. Resolved below. `-31` follows `-30`'s corpus and is green on the new witness. |
| `test_dogfood_plan.py` | ✅ | NOT a detector-behaviour failure — see the hand-off item. |
| `test_dogfood_proof.py` | ✅ | NOT a detector-behaviour failure — see the hand-off item. |
| `test_cartridge_selfaudit.py` · `test_precision_replay.py` · `test_critical_eligibility_pipeline.py` · `test_evidence_bundle.py` · `test_detector_base.py` · `test_grammar_runtime_validation.py` · `test_dogfood_artifact_currency.py` | ❌ | Green, unchanged. |
| **`test_pipeline_signature_demo.py`** | ❌ | **GREEN — the FR32 signature demo, the line the PRD calls "the product", is intact and unchanged.** Stated prominently because the story asked for it either way. |

### Completion Notes

#### The §0.3 escalation — RESOLVED as option (A), HARDENED

Escalated as the story required; **the operator delegated the call and ruled option (A), with a
mandatory hardening**. Recorded here with the reasoning, per AC and per §0.3's instruction:

1. **What `-30` asserts is a property of the TOOL, and it is still TRUE.** The question is whether
   a blocking verdict is reachable on a default, zero-token, no-sign-off run. Measured under the
   corrected predicate: **3/3 planted cartridges keep corroboration and still exit 2**. Option (B)
   would therefore have committed a FALSE claim to the README, `action.yml` and Story 12.4's
   statement. The default path still blocks; it merely no longer blocks THIS witness.
2. **`-30`'s failure message forbids adjusting A GATE, and (A) adjusts none.** No threshold and no
   predicate moved. What was replaced is a reachability WITNESS that was itself engineered against
   the old detector — the module's own note said so ("a naive one-mock/one-call fixture lands
   exactly ON the boundary and fires nothing"). It is a constructed existence proof, never an
   adjudicated sample, so it carries none of the evidentiary weight that makes fixture-editing
   suspect in this repository.
3. **AC4 already set the precedent** for `-86`: re-author as an INTENDED BEHAVIOUR CHANGE with the
   reason recorded, never silently adjusted until it matches new output. `-30` follows it.

**The hardening, delivered in full.** `-30` does not merely swap one fixture for another. It now
measures **both arms on the same default `run_audit_detailed` path**:

- **Arm 1** — the NEW witness (SUT called with its result DISCARDED, assertion on a mock-derived
  bound value, matching the `vacuous_basic` cartridge shape) still reaches `NOT_READY_FOR_RELEASE`
  with a `RULE_AST` finding carrying `depth_supported is AUDITED_SHALLOW`, exit 2,
  `blocking_finding_count >= 1`, no deep-pass record, thresholds imported not transcribed.
- **Arm 2** — the CURRENT fixture, kept verbatim as `_SUT_RESULT_ASSERTED_SOURCE`, now yields **no
  verdict-eligible `RULE_AST` finding** on that same default run, and is asserted to still emit the
  advisory `RULE_HEURISTIC` finding with `depth_supported is None` — demoted, not made invisible.

Arm 2 is the point: it regression-locks the discrimination Epic 14 exists to create and converts
the fixture edit into a measurement of the intended change. The module docstring was rewritten to
carry the 2026-08-17 re-authoring, the ruling and the two arms, in the spirit of its own "why this
is committed rather than recorded in prose".

#### DN-1..DN-4 — each confirmed, with the rejected alternative named

- **DN-1 — CONFIRMED. Fact (b) was replaced, not supplemented.** The predicate is now a statement
  about provenance SHAPE (is the SUT result discarded? is the asserted value mock-bound?).
  *Rejected alternative:* AND-ing a new condition onto `mock_sites >= 1`. Measured consequence of
  the rejection: the surviving term would still have dominated the outcome and the equivalence
  could not have been shown broken — with the replacement, agreement on the mock-bearing
  sub-population went 34/36 → **0/36**, which an AND could not have produced.
- **DN-2 — CONFIRMED. The signal is source text + the 1.4 edge set, and stays NAME-LEVEL.** No
  scope resolution, no call graph, no re-parse; the detector reads only what it was already handed.
  *Rejected alternative:* real dataflow — Story 6.2's scope, needing a resolved call graph the 1.4
  index does not provide, and doing it here would have widened a conformance fix into an epic. The
  limit is cited, not re-filed: `DF-14-1-A` already owns it and `deferred-work.md` was not touched.
- **DN-3 — CONFIRMED AND LOAD-BEARING. A raises-context SUT call is CONSUMED** (AC1.4). Its own
  table, `_RESULT_OBSERVING_CONTEXT_CALLEES`, deliberately separate from `_ASSERTION_CALLEES`.
  *Rejected alternative:* the probe's behaviour (treat it as discarded), which would have kept a
  BORDERLINE finding verdict-eligible on a fail-closed test — see AC3 above, where this is exactly
  the 1-vs-0 survivor difference. Pinned by `-101`, which also asserts the SAME test corroborates
  once the raises context is removed, so the clause cannot be satisfied by accident.
- **DN-4 — CONFIRMED. The predicate is not tuned to today's assertion-name undercount.** Fact (b)
  no longer receives `assertion_sites` or `mock_sites` at all: `_ast_corroborated`'s signature
  changed from `(span_edges, assertion_sites, mock_sites, heuristically_vacuous)` to
  `(source_lines, span_edges, start, end, heuristically_vacuous)`. There is no count and no
  threshold in fact (b) that Story 14.2 can move. `_ASSERTION_CALLEES` is READ (to locate assertion
  statements and to exclude assertion callees from the SUT set) but never counted against a bound;
  `-102` pins the mechanism that makes this safe, using `assert_called` / `reset_mock` — two names
  14.2 will add — and showing they are already excluded on their RECEIVER chain rather than on the
  table. *Rejected alternative:* widening the name list here to remove the tension, which is 14.2's
  AC and would make the two stories un-reviewable independently.

#### AC5 — purity, determinism, contract surface

- **AR8 (PURE) — held.** The new code performs no I/O, no clock, no LLM, no `uuid4`/`random`, no
  network. It reads only the `source.splitlines()` list and the pre-built `AstIndexEntry` the
  detector already receives. `import re` is the only new import; every pattern is compiled at
  module level.
- **AR4 (`Fraction`, never `float`) — held.** No arithmetic was added. Fact (b) returns a `bool`
  from integer counts; no ratio, no division, no `float` anywhere in the change.
- **NFR-D2 (determinism) — held.** The one mutable set (`_mock_bound_names`) is used for membership
  tests only and is never iterated into an output; `_result_observing_lines` returns a `frozenset`
  consumed by `in`; `_assertion_statement_lines` returns a `sorted()` tuple (AR11). The
  `_OBSERVING_CALL_RE` alternation is built from `sorted(...)` so even the compiled pattern is
  order-stable. Nothing new reaches a `.argus/`-bound output.
- **`VacuousTestScore` DID NOT gain a field.** It is byte-unchanged: same 11 fields, still frozen
  `extra="forbid"`. So this is **not** a schema change to a finding-borne model, no migration is
  owed, and the float-rejecting round-trip (`TC-ArgusAgent-DETECT-001-92`) passes **unchanged**.
  The evidence fact (b) computes is carried in a private `_ProvenanceEvidence` `NamedTuple` that
  never leaves the scorer. *Rejected alternative:* adding `sut_result_discarded` /
  `mock_referencing_assertions` fields for legibility — it would have been a schema change to a
  model that travels with findings, for evidence no consumer reads, which is the additive-only
  policy's cost with none of its benefit (YAGNI).
- **Vocabulary and eligibility surface — unchanged.** `RULE_HEURISTIC` / `RULE_AST` are byte-
  unchanged; heuristic → `advisory=True` + `depth_supported=None`; corroborated → `advisory=True` +
  `depth_supported=AUDITED_SHALLOW` + `rule_id="vacuous_test_ast"`. Story 1.6 reads exactly what it
  read before.

#### AC6.1 — 14.2's surface, proven byte-unchanged

Not asserted — **diffed**. `git show HEAD:argus/detectors/vacuous_test.py` against the working
file, comparing the extracted definition blocks byte for byte:

```
_ASSERTION_CALLEES : byte-identical = True (623 bytes)
_MOCK_CALLEES      : byte-identical = True (284 bytes)
_count_statements  : byte-identical = True (801 bytes)
ASSERTION_DENSITY_FLOOR = Fraction(1, 4)   present in both, unchanged
MOCK_RATIO_CEILING      = Fraction(1, 2)   present in both, unchanged
```

The only `+` lines mentioning those names are READS of them (a set-membership test) and one
comment. `argus/pipeline.py` is **untouched** and still 1111 lines — nothing was added to the file
with 89 lines of headroom, and nothing else under `argus/` was modified.

#### Sizes after the change

`argus/detectors/vacuous_test.py` **623 → 1072** lines (headroom **128** to the 1200 ceiling;
`tests/test_module_size_ceiling.py` is green). `tests/test_vacuous_detector.py` 324 → 676;
`tests/test_default_path_blocking_verdict.py` 180 → 268. Flagged for Story 14.2, which must also
edit this module: the headroom is now 128, not 577. 14.2's own change (widening a name table) is
small, but if it needs more room the module has a natural split line — the tier-based test-file
classification block (`_UNAMBIGUOUS_TEST_SUFFIXES` … `partition_application_files`) shares nothing
with the scorer.

#### ⛔ HAND-OFF ITEM — two dogfood guards are RED, and the remedy is a commit this story may not make

**`test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation`
and `test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run` fail.**

**They are guards WORKING, and the cause is not detector behaviour.** Both compare a committed
dogfood artifact against a LIVE re-derivation over the working tree. The committed proof records
`**28038**` total physical LOC; the live derivation reads `28487` — a delta of **+449**, which is
exactly this story's net line change to `argus/detectors/vacuous_test.py` (474 added, 25 removed).
The partition-plan failure is the same cause one level up: a partition unit id is a content hash,
so it moved too. Nothing about detector OUTPUT is involved — `test_dogfood_artifact_currency.py`
(`TC-ArgusAgent-DOGFOOD-001-49`..`-52`), the guard AC7.3 actually named, is **green**, because it
compares two COMMITS and this delta is uncommitted.

**The remedy is pre-authorised and it is not mine to run.** `scripts/regenerate_dogfood_artifacts.py`
**refuses to run on a dirty `argus/` tree** by design (the artifacts cite `git rev-parse HEAD` while
enumerating the git index; regenerating now would produce an artifact citing a commit that does not
contain the code it describes — the false-citation class Epic 10 exists to remove). Its
`--allow-dirty-argus` flag is documented "for diagnosis only" and was NOT used. So no green state
exists for this story while `argus/` is uncommitted, and AC7.4 ("hand off green") and AC7.5
("nothing is committed") cannot both be satisfied by this worker.

AC7.5 is this story's explicit, most specific instruction, so **nothing was committed** and no
assertion was loosened, skipped, xfailed or narrowed (`DF-8-5-B`: *"do not close it by loosening an
assertion"*). This is routed to the owner the Epic-12 retro already assigned it to —
**`AI-E12-11`, owner: the dev-loop orchestrator** — whose pre-authorised sequence is:

```
1. commit the `argus/` + `tests/` delta
2. python scripts/regenerate_dogfood_artifacts.py
3. commit the three regenerated artifacts as a SEPARATE commit
```

That is the identical sequence recorded as applied by Stories 13.1, 13.2 and 13.3 in
`deferred-work.md`, and the Epic-13 interim retro records it as `AI-E12-11`'s evidence of use.
Nothing new is filed in `deferred-work.md`: this is an existing item with a named owner
(`AI-E9-8` satisfied), not a new defect.

#### AC7.5 — nothing outward-facing

`git tag -l` is **empty** at hand-off, as it was at start. Nothing was committed, staged, pushed,
published or tagged. No cartridge, no golden key, no `CartridgeSpec`, no
`tests/corpus/_manifest.py`, no `validation-corpus/**` file and none of the six governance
artifacts carrying the uncommitted correct-course change were touched. `deferred-work.md` and
`architecture.md` were not modified — this story defers nothing new and re-derives no locked
decision.

---

## Dev Agent Record — ITERATION 2 (review findings, 2026-08-17)

Second `dev-story` pass, on HEAD `ae2fb28`, addressing the two findings recorded above.
Both are checked off with their resolution written beside them; this section carries the
numbers.

### Debug Log — iteration 2

#### The High finding: what was actually broken, measured twice

The recorded finding said the discard/consumed classification reads only the call's own
physical line. That is correct, and the consequence is wider than "backslash": **every**
continuation syntax puts the assignment target on an earlier line. Measured through the
shipped detector over the REAL tree-sitter index (not a hand-built edge set), five
spellings of one semantically identical test:

```
case                   disc cons mockref   BEFORE                        AFTER
plain-assign              0    1       1   advisory                      advisory
backslash                 1    0       1   vacuous_test_ast  🔴          advisory
backslash-tight           1    0       1   vacuous_test_ast  🔴          advisory
paren-wrap                1    0       1   vacuous_test_ast  🔴          advisory
list-wrap                 0    1       1   advisory (by ACCIDENT: `]`)   advisory
dict-wrap                 0    1       1   advisory (by accident)        advisory
call-arg-wrap             1    1       1   advisory (by accident)        advisory (cons=2)
TRUE-discard              1    0       1   vacuous_test_ast              vacuous_test_ast
TRUE-discard-wrapped      1    0       1   vacuous_test_ast              vacuous_test_ast
```

The three "by accident" rows are the reason this was fixed at the root rather than by the
suggested backslash special-case: they were advisory only because their statement text
happened not to end in `)`. A last-element list entry without a trailing comma
(`bracket-continuation` in `-109`) has no such luck, and would have stayed broken.

**And end to end, on the `-30` corpus shape, through a default `run_audit_detailed` —
no flags, no LLM, no harness:**

```
                       BEFORE                                    AFTER
plain      INSUFFICIENT_COVERAGE  exit 3  RULE_AST=0   ->  INSUFFICIENT_COVERAGE exit 3 RULE_AST=0
paren      NOT_READY_FOR_RELEASE  exit 2  RULE_AST=1   ->  INSUFFICIENT_COVERAGE exit 3 RULE_AST=0
backslash  NOT_READY_FOR_RELEASE  exit 2  RULE_AST=1   ->  INSUFFICIENT_COVERAGE exit 3 RULE_AST=0
```

Three spellings of one test; two of them took a build to 🔴 on where the author pressed
Enter. That is the lethal failure class and a direct AC1.3 violation.

⚠️ **A correction issued to this worker was itself wrong, and is recorded as such.** The
orchestrator's brief asserted that backslash continuation was ALREADY handled correctly
and that only the parenthesised form was defective. Re-measured here at both levels, the
backslash spelling was defective in exactly the same way and to exactly the same degree.
The reviewer's recorded mechanism needed WIDENING, not replacing. Nothing was implemented
from the incorrect claim.

#### The fix, and why it is the root cause rather than a patch

`provenance_scan.logical_statement_starts` maps every line of the span to the first line
of its LOGICAL statement — the mirror image of the `_logical_statement_end` the module
already had, which is what made this the missing half rather than a new mechanism. One
rule covers both syntaxes: *a line is a continuation iff the bracket depth before it is
positive OR the previous code line ended in a backslash.* `_logical_statement_end` gained
the same backslash awareness, so the two functions agree about what a statement is.
Fact (b) then judges the whole statement: the SUT call is DISCARDED only when everything
of the statement preceding it is empty (or a bare `await`) and the statement ends at the
call. A line whose statement cannot be resolved is CONSUMED — the module's existing
convention (`_locate_call` returning `None`), applied to the new branch: unresolvable is
not evidence, and the failure direction is always away from a false accusation.

#### The predicate was NOT weakened — re-measured, not assumed

| Population | Requirement | Iteration 1 | Iteration 2 |
|---|---|---|---|
| 3 planted cartridges (incl. `holdout_vacuous`, `nonascii_unicode`) | keep corroboration | 3/3 | **3/3** |
| 31 adjudicated locators at the unchanged pinned shas | not verdict-eligible | 0/31 eligible | **0/31 eligible** |
| minions test functions / heuristically flagged | flag rate unchanged | 3,551 / 1,848 (52.0%) | **3,551 / 1,848 (52.0%)** |
| agent-smith test functions / heuristically flagged | flag rate unchanged | 1,122 / 681 | **1,122 / 681** |
| minions promotions | — | 0 | **0** |
| agent-smith promotions | — | 0 | **0** |

Both members re-staged from `git show <sha>:<path>` at `minions@ec63b729` /
`agent-smith@9ab774d7` (Windows path form passed to `git -C`, per §0.4) and re-scored
through the shipped index and the shipped detector. AC6.2 therefore still holds after the
extraction as well as after the fix: nothing leaked into the flag path.

#### RED-then-green, at BOTH levels

Each new guard was confirmed RED against the pre-fix predicate before being made green —
by reverting the classification to the physical-line spelling in place, running, and
restoring it:

```
pre-fix: -109 FAILED  ("'backslash-continuation': expected ast_corroborated=False, got True")
pre-fix: -116 FAILED  (default run_audit_detailed promoted the backslash-wrapped test)
post-fix: -109, -110, -116 all pass
```

`-116` is the arm iteration 1 was missing: predicate-level tests could not have shown that
a **verdict** moved.

#### The Medium finding: the extraction, measured

| File | Before | After |
|---|---|---|
| `argus/detectors/vacuous_test.py` | 1072 (headroom 128) | **697 (headroom 503)** |
| `argus/detectors/provenance_scan.py` | — | **541** |
| `argus/pipeline.py` | 1111 | **1111 (untouched)** |
| `tests/test_vacuous_detector.py` | 676 | 872 |
| `tests/test_default_path_blocking_verdict.py` | 268 | 390 |

`tests/test_module_size_ceiling.py` is green and was **not edited** — no exemption was
added, and the working tree's pre-existing modification to that file is not this story's.

### Completion Notes — iteration 2

- **AC6 still holds, proven by diff not by assertion.** `_ASSERTION_CALLEES` (623 bytes),
  `_MOCK_CALLEES` (284 bytes) and `_count_statements` compared byte-for-byte against
  `git show HEAD:argus/detectors/vacuous_test.py`: **identical**. Both thresholds present
  and unchanged. Fact (b) still receives neither `assertion_sites` nor `mock_sites`
  (DN-4) — and the extraction hardens that: the two tables are now **parameters** of
  `provenance_evidence`, so the scan module cannot reference the table Story 14.2 widens.
- **AC5 still holds.** No arithmetic was added (fact (b) returns a `bool` from integer
  counts — no ratio, no `float`). `VacuousTestScore` is byte-unchanged: same 11 fields,
  frozen `extra="forbid"`, no schema change to a finding-borne model, `-92` passes.
  `RULE_AST`/`RULE_HEURISTIC` and the Story 1.6 eligibility surface are byte-unchanged.
  Determinism: the new `logical_statement_starts` returns a `dict` keyed by line number
  and is consumed only by `.get()`; nothing new is iterated into an output. The scorer
  stays PURE — the new module performs no I/O, no clock, no LLM, no `uuid4`/`random`.
- **`-87` and `-88` pass UNCHANGED**, as does the whole of `-101`..`-108`. `-30`'s two-arm
  structure (the §0.3 ruling) is intact and untouched; `-116` is a NEW sibling beside it,
  not a modification of it.
- **`README.md` and `CHANGELOG.md` were edited, and only because a guard demanded it.**
  `TC-ArgusAgent-DOCS-001-54` compares published distribution figures against a freshly
  built wheel and went red on the new module: *"README.md publishes a stale figure for
  'importable_modules': it says 86, the freshly built artifact measures 87. Fix the
  document — the artifact is the fact."* Both documents now read 87/87 (and 95 wheel
  entries / 94 sdist files), each carrying the dated note the surrounding rolling record
  uses. This is a guard WORKING (the Story 13.4 lesson), and the remedy it names.
  `mypy argus` moves 86 → **87 source files** for the same reason — that delta is the new
  module, not a new error.
- **Nothing else outward-facing.** `git tag -l` empty at start and at hand-off. No
  cartridge, golden key, `CartridgeSpec`, `tests/corpus/_manifest.py`,
  `validation-corpus/**` file, `deferred-work.md`, `architecture.md` or governance
  artifact was touched, and none of the working tree's pre-existing uncommitted changes
  (six governance artifacts, four test modules, the untracked directories) was staged.

#### AC7.1 — the three gates, iteration 2 (LOCAL; CI evidence is NOT ESTABLISHED)

| Gate | §0.1 baseline | Iteration 1 | Iteration 2 | Δ vs §0.1 |
|---|---|---|---|---|
| `pytest` collected | 1597 | 1605 | **1608** | **+11** (`-109`, `-110`, `-116` added here; no test deleted) |
| `pytest` | 1597 passed / 0 failed / 0 skipped | 1603 passed / 2 failed | **1608 passed / 0 failed / 0 skipped, exit 0** | **green** |
| `mypy argus` | Success, 86 source files | Success, 86 | **Success, 87 source files** | +1 file, 0 issues |
| `bandit -r argus` | 19 Low / 0 Med / 0 High (0/0/6/13) | same | **19 Low / 0 Med / 0 High (0/0/6/13)** | 0 |

**No skip appeared.** These are LOCAL Windows numbers and **CI evidence is NOT
ESTABLISHED** for this delta. The two dogfood-currency failures iteration 1 handed off
under `AI-E12-11` were closed by running that item's own pre-authorised sequence (commit
the code delta → `python scripts/regenerate_dogfood_artifacts.py` → commit the three
regenerated artifacts separately); no artifact was hand-edited and no assertion was
loosened, skipped, xfailed or narrowed (`DF-8-5-B`).

### File List

| Path | Action |
|---|---|
| `argus/detectors/provenance_scan.py` | **ADDED** (iteration 2) — the line-oriented provenance scan extracted from the detector, carrying the logical-statement fix (`logical_statement_starts`, backslash-aware `_logical_statement_end`). 541 lines |
| `argus/detectors/vacuous_test.py` | **MODIFIED** — iteration 1: new fact (b) (`_RESULT_OBSERVING_CONTEXT_CALLEES`, the source-text scanning primitives, `_provenance_evidence`, a rewritten `_ast_corroborated` + module docstring). Iteration 2: the scan moved to `provenance_scan.py` and is imported back, the callee tables passed in as parameters (DN-4 made structural), docstring re-stated around "logical statement, not physical line". 623 → 1072 → **697** lines (headroom 503) |
| `tests/test_vacuous_detector.py` | **MODIFIED** — iteration 1: `-86` re-authored as a two-arm intended behaviour change, `-94` re-authored to a three-way discrimination over the real index, new `-101`..`-108`. Iteration 2: **new** `-109` (the five-shape continuation closure, both directions, driven from `_CONTINUATION_SHAPES`) and `-110` (a genuinely discarded call stays corroborated across three wrappings — the fix does not buy safety with recall). 324 → 676 → **872** lines |
| `tests/test_default_path_blocking_verdict.py` | **MODIFIED** — iteration 1: §0.3 option (A) hardened (new witness + the old fixture verbatim as arm 2). Iteration 2: **new** `TC-ArgusAgent-VERDICT-001-116` — the same default `run_audit_detailed`, the same corpus, both continuation spellings, asserted EQUIVALENT to the unwrapped control. `-30` itself is untouched. 180 → 268 → **390** lines |
| `README.md` | **MODIFIED** (iteration 2) — the published distribution figures, because `TC-ArgusAgent-DOCS-001-54` compares them against a freshly built wheel and the new module moved them: 86/86 → **87/87** importable modules, 94 → **95** wheel entries, 93 → **94** sdist files, with the dated provenance note the surrounding rolling record uses |
| `CHANGELOG.md` | **MODIFIED** (iteration 2) — the same two figures in the packaging section, for the same guard and the same reason |
| `_bmad-output/design-artifacts/ArgusAgent/stories/14-1-a-verdict-eligible-vacuous-finding-proves-vacuity-not-mocking.md` | **MODIFIED** — Tasks, Dev Agent Record (iterations 1 and 2), Completion Notes, Review Findings (both checked off, with a dated correction to the High finding's recorded mechanism), File List, Change Log, Status |
| `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` | **MODIFIED** — `14-1` status only (`ready-for-dev` → `in-progress` → `review`), `last_updated` |
| `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-{proof,partition-plan,budget-plan}.md` | **REGENERATED** through `scripts/regenerate_dogfood_artifacts.py` only, as a separate commit (`AI-E12-11`). Never hand-edited |

**Not touched, deliberately:** `argus/pipeline.py`, `argus/verdict/prosecutor.py`,
`argus/verdict/verdict_gate.py`, every file under `tests/cartridges/`, `tests/corpus/_manifest.py`,
`_bmad-output/design-artifacts/ArgusAgent/validation-corpus/**`, `deferred-work.md`,
`architecture.md`, and the six governance artifacts carrying the uncommitted correct-course change.
The measurement harness used for AC1.2 / AC3 / AC6.2 lives OUT OF TREE in the session scratchpad
and is not part of the delta.

### Review Findings

_Code review (Sonnet), 2026-08-17, iteration 1. Scope: `git diff 47b6dbe..ae2fb28`
(`b315bcd` + `ae2fb28`). All claims below were RE-VERIFIED BY EXECUTION, not read back
from the Dev Agent Record — full suite (1605 collected, exit 0), `mypy argus`
(Success, 86 files), `bandit -r argus` (19 Low/0 Med/0 High, conf 0/0/6/13), cartridge
recall (7 passed via `test_cartridge_selfaudit.py -k "vacuous_basic or holdout_vacuous
or nonascii_unicode"`), and an INDEPENDENT re-scoring script run against both pinned
shas (`minions@ec63b729`, `agent-smith@9ab774d7`) over all 31 adjudicated locators —
confirms **0/31 verdict-eligible**, matching the story's claim exactly. The two-commit
close was verified by re-running `scripts/regenerate_dogfood_artifacts.py` against the
current clean tree and diffing output against the committed artifacts: the only delta
is the (expected) `git rev-parse HEAD` descriptor line — content, LOC (28487) and
partition figures are byte-identical, confirming the artifacts were genuinely
script-generated, not hand-edited (AI-E12-11 verified). §0.3's hardening (both arms on
`-30`) is present exactly as required: arm 2 asserts the OLD fixture yields **no**
verdict-eligible `RULE_AST` finding and still emits an advisory `RULE_HEURISTIC`
finding — confirmed by reading `tests/test_default_path_blocking_verdict.py:216-236`.
AC6 boundary (`_count_statements`, `_ASSERTION_CALLEES`, `_MOCK_CALLEES`, both
thresholds) confirmed byte-unchanged by diff — only new READS of those names appear.
DN-3 (raises-context = CONSUMED) is implemented and tested (`-101`, plus the
independent `test_ir_copilot.py:128` demotion). `-87`/`-88` are unchanged in the diff.

- [x] [Review][Patch] Fact (b)'s discard/consumed classification can be fooled by a
  backslash line continuation between an assignment's `=` and the SUT call, causing a
  test that genuinely constrains the real SUT result to be misclassified as
  "discarded" and promoted to verdict-eligible — violating AC1.3 ("A test whose
  assertions constrain the real SUT result is NOT corroborated") and the moat's own
  stated risk model ("a false 🔴 is the lethal failure"). [`argus/detectors/vacuous_test.py`,
  `_provenance_evidence`'s discard/consumed branch, ~lines 940-965 (the `preceding`
  check against only the call's own physical line)]. Root cause: `preceding =
  _code_prefix(source_lines[index])[:chain_start].strip()` only looks at text on the
  SAME physical line as the call; when the assignment's target and `=` sit on the
  PREVIOUS physical line via `\` continuation (`result = \` / `    sut(1, 2)`), nothing
  precedes the call on its own line, so it is scored "discarded" even though it is
  bound to `result`. Reproduced and confirmed by direct execution against the shipped
  detector:
  ```python
  def test_genuine_but_backslash():
      fake = Mock()
      fake.other.return_value = 1
      result = \
          sut(1, 2)
      assert result == fake.other()
  ```
  scores `vacuous_test_ast` / `AUDITED_SHALLOW` (verdict-eligible) even though the
  assertion genuinely constrains the real SUT result via `result`. This is the exact
  false-accusation class Story 14.1 exists to close, reached through a narrow but valid
  Python idiom (target repos audited by Argus are not bound by this repo's own lint
  rules against backslash continuation). Suggested fix: before crediting a call as
  discarded, check whether the physical line immediately preceding `edge.line`
  (comment-stripped, right-stripped) ends with a bare `\`; if so, fall back to the
  conservative default and count it as CONSUMED (mirroring the existing
  "unresolvable is not evidence → consumed" rule for `_locate_call` returning `None`).
  No test in `-101`..`-108` reaches this branch. Severity: High — a proven,
  reproducible violation of a core, explicitly-tested AC in the exact risk direction
  (false 🔴) the story is meant to eliminate.

  > **CORRECTION — 2026-08-17, dev-story iteration 2, MEASURED not argued.** The
  > finding's verdict is upheld and its mechanism is upheld, but it was **wider than
  > recorded**, and one intermediate correction issued to this worker was itself wrong.
  >
  > **(1) The trigger is not backslash continuation. It is CONTINUATION.** The recorded
  > root cause — `preceding = _code_prefix(source_lines[index])[:chain_start].strip()`
  > reads only the call's own physical line — is exactly right, and every syntax that
  > puts the assignment target on an earlier line hits it. Measured through the shipped
  > detector over the real tree-sitter index, on five spellings of one test:
  >
  > | shape | before | after |
  > |---|---|---|
  > | `result = sut(1, 2)` | advisory | advisory |
  > | `result = \` / `    sut(1, 2)` | **`vacuous_test_ast`** | advisory |
  > | `result = (` / `    sut(1, 2)` / `)` | **`vacuous_test_ast`** | advisory |
  > | `results = [` / `    sut(1, 2)` / `]` | advisory *(only because the `]` kept the statement from ending in `)`)* | advisory |
  > | genuinely discarded, wrapped | `vacuous_test_ast` | `vacuous_test_ast` (kept) |
  >
  > The **parenthesised** form is the one that matters most in the wild, because PEP 8
  > explicitly prefers it over the backslash: *"long lines can be broken over multiple
  > lines by wrapping expressions in parentheses… these should be used in preference to
  > using a backslash."* So the reachable-in-the-wild spelling was broken too, and the
  > bracket row shows the survivor was surviving by accident rather than by the
  > predicate.
  >
  > **(2) An orchestrator correction handed to this worker claimed backslash
  > continuation was ALREADY handled correctly and only the parenthesised form was
  > defective. That claim does not reproduce and was not acted on.** Re-measured here
  > twice — once at predicate level through `provenance_evidence`, once end to end
  > through a default `run_audit_detailed` over the `-30` corpus shape — the backslash
  > spelling produced `discarded=1 / consumed=0` and `NOT_READY_FOR_RELEASE` with
  > `RULE_AST=1`, identically to the parenthesised one. **The reviewer's mechanism was
  > correct as written.** This is recorded because a wrong mechanism left in the record
  > misleads the next reader, and that cuts both ways.
  >
  > **(3) It was reproduced END TO END, which is the part that makes it a product
  > defect rather than a helper bug.** On the default zero-token, no-sign-off path over
  > the `-30` corpus: `plain` → `INSUFFICIENT_COVERAGE`, `RULE_AST=0`; `paren-wrap` and
  > `backslash` → `NOT_READY_FOR_RELEASE`, exit 2, one verdict-eligible finding. Three
  > spellings of one test, one of them taking a build to 🔴 on layout alone.
  >
  > **Fix:** the classification is now made about the whole **logical statement**
  > containing the call (`provenance_scan.logical_statement_starts`, the mirror of the
  > existing `_logical_statement_end`), with both continuation syntaxes handled by one
  > rule and no special case for either. A line whose statement cannot be resolved
  > follows the module's existing convention — unresolvable is not evidence → CONSUMED.
  > **The predicate was not weakened to achieve it:** cartridge recall re-measured
  > **3/3** and the 31 adjudicated locators re-measured **0/31 verdict-eligible** at the
  > unchanged pinned shas, with the flag rate byte-identical. Regression-locked at both
  > levels: `TC-ArgusAgent-DETECT-001-109` (the five-shape closure, both directions) and
  > `-110` (recall is not traded away), plus `TC-ArgusAgent-VERDICT-001-116` — the
  > end-to-end arm, and the one that would have caught this. Both were confirmed RED
  > against the pre-fix predicate before being made green.

- [x] [Review][Patch] Cohesion/module-size: `argus/detectors/vacuous_test.py` grew
  623 → 1072 lines (headroom to the 1200 ceiling dropped from 577 to 128), and the
  growth is a self-contained ~15-function source-text micro-parser (`_skip_string`,
  `_code_prefix`, `_blank_strings`, `_bracket_delta`, `_logical_statement_end`,
  `_statement_code`, `_locate_call`, `_leading_chain`, `_is_mock_derived`,
  `_structural_colon`, `_result_observing_lines`, `_mock_bound_names`,
  `_ProvenanceEvidence`, `_assertion_statement_lines`, `_provenance_evidence`) bolted
  onto a module whose stated job is "detect vacuous tests via the scorer +
  corroboration." This is a real SRP/cohesion question, not a nit: the new code is a
  distinct concern (line-oriented provenance scanning) from the detector's scoring
  logic, and the Dev Agent Record itself flags that "Story 14.2, which must also edit
  this module... the module has a natural split line" without acting on it. With only
  128 lines of headroom left and both Story 14.2 and 14.3 still to land in this same
  file, this risks a 13-4-class module-size deadlock. Suggested fix: extract the
  provenance-scanning primitives (everything from `_skip_string` through
  `_provenance_evidence`) into a dedicated module (e.g.
  `argus/detectors/_provenance_scan.py`) before 14.2 lands, importing them back into
  `vacuous_test.py`. Severity: Medium — not a correctness defect, but a forward-looking
  architectural risk explicitly invited by the review brief and already anticipated
  (but not resolved) by this story's own Dev Agent Record.

  > **RESOLVED — 2026-08-17, dev-story iteration 2.** Done in this round rather than
  > deferred, for the reason the finding gives: the High fix ADDS lines to the same
  > module, and deferring the split into a file with 128 lines of headroom is how a
  > 13-4-class deadlock is built. `argus/detectors/provenance_scan.py` now owns the
  > line-oriented scan (`opens_bare_assert`, the string/comment/bracket primitives,
  > `logical_statement_starts`, `_logical_statement_end`, `_locate_call`,
  > `_leading_chain`, `_is_mock_derived`, `_structural_colon`, `_result_observing_lines`,
  > `_mock_bound_names`, `_assertion_statement_lines`, `ProvenanceEvidence`,
  > `provenance_evidence`, and fact (b)'s own `RESULT_OBSERVING_CONTEXT_CALLEES`).
  > Measured: `vacuous_test.py` **1072 → 697** lines, headroom **128 → 503**;
  > `provenance_scan.py` 541; `argus/pipeline.py` untouched at 1111.
  >
  > Two deliberate departures from the suggested shape, both recorded rather than
  > silently taken. **(a) The module is `provenance_scan.py`, not `_provenance_scan.py`.**
  > NFR-M1 states modules are `snake_case.py` and no module under `argus/` carries a
  > leading underscore; `argus/detectors/secret_suppression.py` and
  > `argus/dogfood/proof_types.py` are the precedent for an internal helper module.
  > Where a suggestion and a project standard conflict, the project standard wins.
  > **(b) `_ASSERTION_CALLEES` and `_MOCK_CALLEES` did NOT move** — they stay in
  > `vacuous_test.py` and are passed in as parameters. Moving them would have put Story
  > 14.2's table inside fact (b)'s own module, and DN-4 requires fact (b) not to move
  > when 14.2 widens it. As parameters that is structural rather than promised: nothing
  > in the scan module can grow a dependency on a table it cannot see. Extraction was
  > behaviour-preserving — re-measured after the move: recall **3/3**, adjudicated
  > locators **0/31**, flag rate **1,848/3,551** and **681/1,122**, all identical.

No other High/Medium findings. Determinism (AR4/AR8/NFR-D2), `VacuousTestScore`
byte-unchanged/frozen/`extra=forbid`, RULE_AST/RULE_HEURISTIC vocabulary, and CRLF/non-
ASCII handling were all spot-checked and hold as claimed.

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-08-17 | v1.1 | **Addressed code review findings — 2 of 2 items resolved (iteration 1, Sonnet).** **HIGH (false accusation) — FIXED AT THE ROOT, and the finding's scope was WIDER than recorded.** Fact (b) classified a SUT call's result as discarded by reading only the call's own PHYSICAL line, so every continuation syntax defeated it, not just the backslash the finding named: measured through the shipped detector, `result = \` / `sut(1, 2)` AND the parenthesised `result = (` / `sut(1, 2)` / `)` — the form PEP 8 explicitly PREFERS — both scored `vacuous_test_ast` / `AUDITED_SHALLOW` while the byte-equivalent single-line spelling stayed advisory. Reproduced **end to end** on the `-30` corpus shape through a default zero-token `run_audit_detailed`: `plain` → `INSUFFICIENT_COVERAGE` exit 3, `paren` and `backslash` → **`NOT_READY_FOR_RELEASE` exit 2 with one verdict-eligible finding** — a build taken to 🔴 by where the author pressed Enter, the lethal failure class and a direct AC1.3 violation. Two list/dict rows were advisory only BY ACCIDENT (their statement text did not end in `)`), which is why the suggested backslash special-case was rejected in favour of the root fix: the classification is now made about the whole **LOGICAL STATEMENT** containing the call, via `provenance_scan.logical_statement_starts` — the mirror of the `_logical_statement_end` the module already had — with ONE rule covering brackets and backslashes and no special case for either; an unresolvable statement follows the module's existing convention and counts CONSUMED (unresolvable is not evidence). ⚠️ **An orchestrator correction claiming backslash continuation was already handled and only the parenthesised form was broken does NOT reproduce**; re-measured twice, at predicate level and end to end, the backslash spelling was defective identically. The reviewer's mechanism needed widening, not replacing, and the incorrect claim was not implemented — recorded beside the finding so the record is not left misleading. **The predicate was NOT weakened to achieve it, re-measured not assumed:** cartridge recall **3/3** (`vacuous_basic`, the `holdout_vacuous` anti-overfitting control, the Cyrillic-pathed `nonascii_unicode`), the 31 adjudicated locators **0/31 verdict-eligible** at the unchanged pinned shas, promotions 0 on both members, flag rate byte-identical (1,848/3,551 = 52.0% minions, 681/1,122 agent-smith). Regression-locked at BOTH levels and both confirmed RED against the pre-fix predicate first: `TC-ArgusAgent-DETECT-001-109` (a five-shape closure asserting both directions, including a genuinely-discarded control that must STAY vacuous) and `-110` (recall is not traded for safety), plus **`TC-ArgusAgent-VERDICT-001-116`** — the end-to-end arm, at the same altitude as `-30`, asserting every wrapping of one test reaches the SAME verdict as the unwrapped one; it is the arm that would have caught this. **MEDIUM (cohesion / module size) — DONE THIS ROUND rather than deferred**, since the High fix adds lines to the same module: `argus/detectors/provenance_scan.py` now owns the line-oriented scan and `vacuous_test.py` goes **1072 → 697** (headroom **128 → 503**); `argus/pipeline.py` untouched at 1111 and `tests/test_module_size_ceiling.py` green with no exemption added. Two departures from the suggested shape, both recorded: the module is `provenance_scan.py`, not `_provenance_scan.py` (NFR-M1 says `snake_case.py` and no `argus/` module carries a leading underscore — the project standard wins over the suggestion), and `_ASSERTION_CALLEES` / `_MOCK_CALLEES` did NOT move — they are passed in as parameters, which makes DN-4 structural: the scan module cannot depend on the table Story 14.2 widens. Extraction proven behaviour-preserving by re-measuring recall, the 31 locators and both flag rates after the move. **AC6 re-proven by diff:** `_ASSERTION_CALLEES` (623 bytes), `_MOCK_CALLEES` (284 bytes) and `_count_statements` byte-identical to `HEAD`; both thresholds unchanged. **AC5 holds:** no arithmetic added (fact (b) returns a `bool` from integer counts — no ratio, no `float`), `VacuousTestScore` byte-unchanged and still frozen `extra="forbid"`, `RULE_AST`/`RULE_HEURISTIC` and the Story 1.6 surface unchanged, scorer still PURE. `-87`, `-88` (the false-accusation guard), `-101`..`-108` and `-30`'s two-arm structure all pass **unchanged**. `README.md` and `CHANGELOG.md` were edited ONLY because `TC-ArgusAgent-DOCS-001-54` went red on the new module and names that remedy in its own message (*"the artifact is the fact"*): 86/86 → 87/87 importable modules, 94 → 95 wheel entries, 93 → 94 sdist files. **Gates (LOCAL; CI evidence NOT ESTABLISHED):** `pytest` **1608 collected / 1608 passed / 0 failed / 0 skipped, exit 0**; `mypy argus` **Success, 87 source files** (the +1 is the new module, not a new error); `bandit -r argus` **19 Low / 0 Med / 0 High** (0/0/6/13), Δ0. Iteration 1's two dogfood-currency failures were closed by running `AI-E12-11`'s own pre-authorised sequence — commit the code delta, `python scripts/regenerate_dogfood_artifacts.py`, commit the three regenerated artifacts separately. No artifact hand-edited; no assertion loosened, skipped, xfailed or narrowed (`DF-8-5-B`); `deferred-work.md` and `architecture.md` untouched; `git tag -l` empty; none of the working tree's pre-existing uncommitted changes staged. | Dev Agent (dev-story, iteration 2) |
| 2026-08-17 | v1.0 | **Implemented on HEAD `47b6dbe`.** Fact (b) REPLACED (DN-1): `assertion_sites >= 1 and mock_sites >= 1` — *"the test constructs a mock"* — becomes a provenance-shape statement over the same PURE inputs: at least one SUT call's result is DISCARDED, **no** SUT call's result is consumed, and at least one assertion references a mock-bound name. Fact (a) is unchanged. **AC1.2, re-measured on MY baseline over an identical population:** agreement with the bare `mock_sites >= 1` term went 2,527/2,529 → 2,493/2,529 overall and **34/36 → 0/36** on the only sub-population where the two terms can differ — the corroboration step no longer re-reads one of its own inputs. **AC2: recall 3/3** (`vacuous_basic`, the `holdout_vacuous` anti-overfitting control and the Cyrillic-pathed `nonascii_unicode` all still exit 2 with one verdict-eligible `vacuous_test_ast`); no cartridge, golden key or `CartridgeSpec` edited. **AC3: 0 of 31** adjudicated locators remain verdict-eligible at the unchanged pinned shas; minions-wide promotions 27 → 0 over 3,551 test functions. The §0.2 probe's single survivor, `agentsmith-core/tests/test_ir_copilot.py:128` (human disposition BORDERLINE), is demoted **by DN-3 specifically** — its SUT call sits inside `with pytest.raises(...)`, and raising IS the observation; that is the probe defect AC1.4 required to be designed in rather than inherited. **AC6: flag rate IDENTICAL** (1,848/3,551 = 52.0% minions, 681/1,122 agent-smith), and `_count_statements` / `_ASSERTION_CALLEES` / `_MOCK_CALLEES` / both thresholds proven **byte-identical by diff**, not asserted. **AC5: `VacuousTestScore` did not change shape** — no field added, still frozen `extra="forbid"`, so no finding-borne schema change and `-92` passes unchanged; the scorer stays PURE and `float`-free. `argus/pipeline.py` untouched. **§0.3 RESOLVED as option (A), HARDENED, on the operator's ruling after escalation:** `-30` asks whether the TOOL can block on a default zero-token no-sign-off run and the answer is still YES (3/3 cartridges), so option (B) would have committed a false claim to README / `action.yml` / Story 12.4; and the fixture is a constructed existence proof engineered against the old detector, not an adjudicated sample, so replacing it adjusts no gate. `-30` now measures **both arms on the same default path** — the new witness is promoted, and the OLD fixture (kept verbatim) is demoted to advisory — which regression-locks the discrimination and turns the fixture edit into a measurement of the intended change. `-86` and `-94` re-authored the same way, with the reason committed beside them; `-87` and `-88` (the false-accusation guard) pass **unchanged**. Eight new cases `-101`..`-108` reach every branch of fact (b), including CRLF-identity and non-ASCII identifiers (the Windows-local / ubuntu-CI exposure `AI-E13-1` names). **Gates (LOCAL; CI evidence NOT ESTABLISHED):** `pytest` 1605 collected / **1603 passed / 2 failed / 0 skipped**; `mypy argus` Success, 86 source files (Δ0); `bandit -r argus` 19 Low / 0 Med / 0 High, confidence 0/0/6/13 (Δ0). ⛔ **The two failures are `test_dogfood_plan.py` and `test_dogfood_proof.py`, and they are guards WORKING, not detector behaviour**: the committed proof records 28038 total LOC, the live derivation reads 28487, a delta of exactly this story's +449 lines under `argus/`. The named remedy refuses to run on a dirty `argus/` tree by design, so no green state exists while the delta is uncommitted; AC7.5 forbids committing, so this is routed to `AI-E12-11`'s recorded owner (the dev-loop orchestrator) with the pre-authorised commit → regenerate → commit sequence Stories 13.1/13.2/13.3 applied. `test_dogfood_artifact_currency.py` — the guard AC7.3 named — is GREEN, as is `test_pipeline_signature_demo.py`, the FR32 demo the PRD calls *"the product"*. No assertion was loosened, skipped, xfailed or narrowed. Nothing committed; `git tag -l` empty. `deferred-work.md` unmodified — `DF-14-1-A` is cited, not re-filed. **Divergence recorded, not inherited:** §0's corpus population figures (3,509 / 1,812 / 24 / 1,836) do not reproduce through the shipped detector at the pinned shas; the measured population is 3,551 / 1,848 / 27 / 2,529, it is not an intake-exclusion artefact, and the harness is validated by reproducing all 31 adjudicated findings as verdict-eligible before the change. | Dev Agent (dev-story) |
| 2026-08-17 | v0.1 | Story contexted on HEAD `47b6dbe`. Source: `sprint-change-proposal-2026-08-17.md`, APPROVED by XAgent007 2026-08-17. **The defect was re-measured, not inherited:** fact (b) is `assertion_sites >= 1 and mock_sites >= 1`, and `ast_corroborated` is equivalent to `mock_sites >= 1` in **1,835 of 1,836** heuristically-flagged tests across both contributing corpus members — so the corroboration step adds no evidence the heuristic did not already have. The rule class emitted 31 blocking findings over the ratified corpus and the named human adjudicated **0** true (26 FP / 5 BORDERLINE). **This is a CONFORMANCE fix, not a new decision:** cross-cutting concern #6 has required `audited_deep` corroboration AND Prosecutor sign-off since the architecture was written, and the detector ships `AUDITED_SHALLOW` with no sign-off; the Epic-6 Prosecutor does not close it because `prosecutor.py:56-57` leaves an ALREADY-eligible finding UNCHANGED and `pipeline.py:535` passes no sign-offs. **Feasibility was MEASURED out of tree before this file was written** (§0.2): a predicate keyed on "SUT result discarded + assertion references a mock-bound value" kept **3/3** planted cartridges corroborated — including the `holdout_vacuous` anti-overfitting control and the Cyrillic-pathed `nonascii_unicode` — demoted **30/31** adjudicated findings, and took minions-wide promotions **24 → 0**; the single survivor is the one finding the human adjudicated BORDERLINE rather than FP. One probe defect is specified rather than inherited (DN-3: a `pytest.raises`-context SUT call is CONSUMED, because raising is the observation). ⛔ **A MEASURED ESCALATION is recorded at §0.3 and the dev must read it before coding:** `TC-ArgusAgent-VERDICT-001-30` — the test proving a zero-token, no-sign-off blocking path exists at all — plants a test whose SUT result is bound and asserted, so it does **not** survive the corrected predicate; its own message says *"Do NOT adjust a gate to make this pass — report it and escalate."* Two named options are recorded with arguments both ways and neither is the dev's to take silently. **Blast radius measured** (§0.5): 21 modules reference the rule id, **10 run the detector end to end**, and the classifier's one miss — `test_default_path_blocking_verdict.py` — is the highest-risk module of all; `test_pipeline_signature_demo.py` is the FR32 demo the PRD calls *"the product"*. Sizes measured so no 13-4-class deadlock is walked into: `vacuous_test.py` **623/1200**, but ⚠️ `argus/pipeline.py` is **1111/1200 with 89 lines of headroom** and is NOT exempt — do not add to it. `agent-smith`'s pinned sha confirmed **reachable** (§0.4), so both members can be re-scored against their true pinned trees. Baselines: `pytest` **1597 collected / 1597 passed / 0 failed / 0 skipped**, `mypy argus` **Success, 86 source files**, `bandit -r argus` **19 Low / 0 Med / 0 High**. `git tag -l` empty; nothing committed; nothing outward-facing. | Scrum Master (create-story) |
