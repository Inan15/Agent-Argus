# Story 14.2: The density scorer counts statements, and knows the assertions the ecosystem writes

Status: done

<!-- Contexted 2026-08-18 on HEAD 966ceba. Every premise below was RE-DERIVED BY EXECUTION at
     contexting time against the POST-14.1 tree. Where a figure carried by
     sprint-change-proposal-2026-08-17.md did not reproduce, the measured value is used and the
     divergence is stated. Nothing is inherited. -->

## Story

As the Argus maintainer,
I want the assertion-density score computed over real **statements** and real **assertions**,
So that the advisory signal stops flagging half of every test suite for reasons that are arithmetic
rather than evidence.

### What this story IS

Two measured defects in the **heuristic half** of `argus/detectors/vacuous_test.py`:

1. **The denominator counts LINES.** `_count_statements` counts every non-blank, non-comment line in
   the span. A multi-line call, a dict literal, a closing bracket and **every line of a docstring**
   each count as a statement. Re-measured 2026-08-18: **1.907×** inflation over the 1,848 flagged
   minions tests (§0.2 — *not* the 2.04× the proposal records).
2. **The assertion table knows no pytest.** `_ASSERTION_CALLEES` is documented as *"unittest family
   + pytest helpers"* and every one of its 23 names is `unittest`. Re-measured: an assertion it
   cannot see is present in **13 of the 31** adjudicated spans (§0.3).

### What it is NOT

- **It does NOT move a threshold.** `ASSERTION_DENSITY_FLOOR = 1/4` and `MOCK_RATIO_CEILING = 1/2`
  are byte-unchanged. A failed measurement is not a reason to move a threshold (protocol §5, Story
  13.3 / AC5).
- **It does NOT touch fact (b).** Story 14.1 owns the corroboration predicate. ⛔ **This is not
  automatic any more — see §0.4, which is the most important section in this file.**
- **It does NOT do 14.3's work.** The cross-language vocabulary (`expect`/`toBe`/`assertEquals`/Go/
  Java) is Story 14.3's and runs strictly after this one. §0.6 draws the line.
- **It does NOT re-measure the gate.** That is Story 13.5, which does not begin until Epic 14 closes.
- **It does NOT re-adjudicate.** `validation-corpus/**` is not written by this story.

---

## ⛔ §0 — Premise re-measurement (this project's create-story control)

**Measured 2026-08-18 on `966ceba`, by execution**, through the SHIPPED `build_ast_index` and the
SHIPPED `VacuousTestDetector`, over both contributing corpus members staged at their **unchanged**
pinned shas via `git show <sha>:<path>` into a temp tree. Per `AI-E12-10`, confirmations are recorded
as well as divergences. **Re-measure on your own baseline (Task 0) — inherit nothing, including this.**

### §0.1 — Baselines, verbatim

```
pytest                 -> 1611 collected / 1611 passed / 0 failed / 0 skipped, exit 0
mypy argus             -> Success: no issues found in 87 source files
bandit -r argus        -> 19 Low / 0 Medium / 0 High; confidence 0 / 0 / 6 / 13
```

| Premise | Re-measured on `966ceba` | Consequence |
|---|---|---|
| `_count_statements` counts non-blank/non-comment **LINES** | ✅ **CONFIRMED**, `vacuous_test.py:496-513` | Defect 1 |
| `_ASSERTION_CALLEES` is documented "unittest family + pytest helpers" and holds **23** names, all `unittest` | ✅ **CONFIRMED**, `vacuous_test.py:178-206` | Defect 2 |
| Thresholds `1/4` / `1/2` | ✅ **CONFIRMED** unchanged, `vacuous_test.py:175-176` | AC3 — must stay byte-identical |
| minions test functions / flagged | **3,551 / 1,848 = 52.0%** | Matches 14.1's baseline exactly |
| agent-smith test functions / flagged | **1,122 / 681 = 60.7%** | AC4's before-number |
| corroborated (`vacuous_test_ast`) anywhere in either member | **0 / 4,673** | 14.1's AC3 re-confirmed independently |
| the 31 adjudicated locators | **31/31 resolve, 31/31 still FLAGGED, 0/31 verdict-eligible** | Harness validated against ground truth |
| `argus/detectors/vacuous_test.py` | **697 lines**, headroom **503** | Room here |
| `argus/detectors/provenance_scan.py` (NEW, 14.1) | **610 lines**, headroom **590** | Room here |
| ⚠️ `tests/test_vacuous_detector.py` | **1,084 lines, headroom 116** — was **324** before 14.1 | **The real size constraint of this story.** See §0.7 |
| ⚠️ `argus/pipeline.py` | **1,111 lines, headroom 89**, NOT exempt | **Do not add to it** |
| minions@`ec63b729`, agent-smith@`9ab774d7…` | ✅ **BOTH REACHABLE** (`git cat-file -t` → `commit`) | AC5 re-scoring is against true pinned trees |
| A `project-context.md` exists | ❌ **NONE.** `architecture.md`, `deferred-work.md`, the retrospectives, `stories/14-1-*.md` and this file **are** the context | — |
| Working tree is clean | ❌ **NO — and that is expected.** See §0.8 | Your diff will contain other people's work |

### §0.2 — Defect 1, RE-MEASURED. The proposal's 2.04× does NOT reproduce

Ground truth = CPython's own `ast` module, counting every `ast.stmt` node in the function body
(recursively). Denominator candidates measured against it:

| Population | shipped LINE count | ÷ CPython statements | **inflation** |
|---|---|---|---|
| minions, flagged by the shipped detector (n=1,848) | 29,093 | 15,255 | **1.907×** |
| both members, flagged (n=2,529) | 42,241 | 21,855 | **1.933×** |
| all test functions, both members (n=4,673) | 60,027 | 35,810 | **1.676×** |

⚠️ **DIVERGENCE, stated plainly rather than carried forward (this is the `DF-8-5-C` class).**
`sprint-change-proposal-2026-08-17.md` §1.3 and the Story 1.5 amendment both record **2.04×** "over
the 1,812 flagged tests". On the population that best corresponds — minions, flagged, n=**1,848** —
the measured figure is **1.907×**. It is not a definitional difference either: counting only
TOP-LEVEL body statements gives **2.664×**, so 2.04 is neither. **The defect is real and large; the
specific multiplier is stale.** Use 1.907× and say so. Do not restate 2.04× anywhere, and do not
silently "correct" the Story 1.5 amendment's number — see AC1.3.

**The two candidate denominators, measured:**

| Candidate | ÷ CPython (minions flagged) | exact match | flags GAINED |
|---|---|---|---|
| **v1** — reuse `provenance_scan.logical_statement_starts`, `;`-compounds counted via `_simple_statement_breaks` | 1.134× | 1,266/1,848 = 68.5% | ⚠️ **2** |
| **v2** — v1 **plus cross-line triple-quoted-string state** | **1.005×** | **1,784/1,848 = 96.5%** | **0** |

⛔ **v1 is not good enough, and the reason is a measured defect you must design around.**
`logical_statement_starts` reads **one physical line at a time and carries no cross-line string
state**, so every line of a docstring looks like its own statement — and a `;` *inside docstring
prose* is read as a statement separator. Both flag GAINS are exactly that:

```
agent-smith/agentsmith-core/tests/test_sim_real_boundary.py:405   8 -> 9 statements
    419|     manifest object; the sim path never enforces the KMS key gate (presence-only)."""
agent-smith/agentsmith-plugin/tests/test_plugin_fail_closed.py:376  12 -> 13 statements
    379|     "No parseable envelope on stdout" is the rule; a framework argument error also
```

Under **v2** both disappear: **0 flags gained, 1,268 lost** across both members. A change advertised
as flag-*reducing* that quietly manufactures two new accusations is the defect class this epic
exists to close.

### §0.3 — Defect 2, RE-MEASURED. "4 of 31" reproduces only WITH the naming convention

Two widening shapes were measured separately, because they are not the same decision:

- **TABLE** — add the names: pytest (`raises`, `warns`, `deprecated_call`), the `unittest.mock`
  assertion methods (`assert_called_once_with`, `assert_not_called`, `assert_has_calls`, …) and the
  `unittest` gaps the 23 names miss (`assertIsInstance`, `assertWarns`, `assertLogs`,
  `assertSequenceEqual`, …).
- **CONVENTION** — additionally admit a callee matching the project-helper naming convention
  (`assert*` / `_assert*`), which is what reaches `_assert_one_rejection`.

| Measured over the 31 adjudicated locators | TABLE only | TABLE + CONVENTION | proposal says |
|---|---|---|---|
| spans where `assertion_sites` rises | 11/31 | **13/31** | 13/31 ✅ |
| lifted above the floor by the **names alone** | 3/31 | **4/31** | 4/31 ✅ |
| lifted by the **v2 denominator alone** | **14/31** | **14/31** | 14/31 ✅ |
| lifted by **both together** | 22/31 | **23/31** | 23/31 ✅ |
| **still flagged after both** | 9/31 | **8/31** | 8/31 ✅ |

**This is the useful result and it is prescriptive.** The proposal's attribution table reproduces
**exactly** — but only for the design that (i) tracks multi-line strings in the denominator and
(ii) includes the project-helper naming convention. Every weaker design misses. The numbers pin the
design; they are not decoration.

**Re-measured flag rate over the same populations** (AC4's after-number to beat):

| Configuration | minions | agent-smith |
|---|---|---|
| shipped today | 1,848 / 3,551 = **52.0%** | 681 / 1,122 = **60.7%** |
| v2 denominator only | 868 = **24.4%** | 393 = **35.0%** |
| v2 + TABLE | 704 = **19.8%** | 308 = **27.5%** |
| **v2 + TABLE + CONVENTION** | **660 = 18.6%** | **297 = 26.5%** |

### §0.4 — ⛔⛔ THE PREMISE THAT DID NOT SURVIVE. Widening the table CAN manufacture a 🔴

**Read this before writing a line of code. It is the reason this story is contexted rather than
copied from the proposal, and the proposal predates the tree it now runs on.**

Story 14.1 extracted fact (b) into `argus/detectors/provenance_scan.py` and left the callee
vocabularies in `vacuous_test.py`, passed in as parameters. That module's docstring records the
intent (`provenance_scan.py:22-27`):

> *"`_ASSERTION_CALLEES` and `_MOCK_CALLEES` stay in `vacuous_test.py` and are PASSED IN, because
> Story 14.2 owns the assertion table and **fact (b) must not move when it is widened** (Story 14.1
> / DN-4). Parameters make that structural rather than promised: **nothing in this module can grow a
> dependency on a table it cannot see.**"*

⛔ **The last sentence is false as written, and the guarantee it claims does not hold.** The module
*can* see the table — it is a parameter, `assertion_callees`, and it is read in **two** places:

| Read site | Effect of widening | Direction |
|---|---|---|
| `provenance_evidence`, SUT loop (`provenance_scan.py:547-552`) — a widened callee is now SKIPPED | can drop `consumed_sut_calls` to 0 → `sut_result_is_discarded` flips **True** | ⚠️ **towards accusation** |
| …same site | can drop `discarded_sut_calls` to 0 | away from accusation |
| `_assertion_statement_lines` (`provenance_scan.py:502`) — more lines count as assertion statements | can raise `mock_referencing_assertions` 0 → ≥1 | ⚠️ **towards accusation** |
| `vacuous_test._sut_call_sites` — fact **(a)** also excludes `_ASSERTION_CALLEES` | can flip `reaches_sut` False | away from accusation |

**What DN-4 actually guarantees is that fact (b) does not depend on the assertion COUNT. It does not
guarantee independence from the assertion TABLE, and the two are different things.**
`TC-ArgusAgent-DETECT-001-102`'s comment (`tests/test_vacuous_detector.py:424-426`) is correct about
the SUT-classification half and is silent about the other half — that is the gap.

**Reproduced end to end through the REAL tree-sitter index and the REAL detector** (an ordinary
mock-interaction test — no bare `assert`, no assertion the shipped table can see):

```python
def test_compute_calls_the_dependency():
    compute([1, 2])                              # SUT reached, result DISCARDED
    fake = Mock()
    fake.calculate.return_value = 6
    fake.calculate()
    fake.calculate.assert_called_once_with()     # the only "assertion" in the test
```

```
SHIPPED table   : asserts=0 stmts=5 density=0   flagged=True  CORROBORATED=False   <- advisory
WIDENED table   : asserts=1 stmts=5 density=1/5 flagged=True  CORROBORATED=True    <- 🔴 VERDICT-ELIGIBLE
```

The mechanism is `_assertion_statement_lines`: with `assert_called_once_with` in the table that line
becomes an assertion statement, it references the mock-bound name `fake`, and
`mock_referencing_assertions` goes `0 → 1`. Density rises to `1/5`, which is **still below the 1/4
floor**, so the test stays flagged and is now promoted. **A perfectly ordinary mock-interaction test
becomes a build-blocking false accusation, produced by the fix for defect 2.**

⚠️ **The corpus measurement cannot see this, and you must not be reassured by it.** Over both
members, widening the table moved corroboration for **0** tests in every direction measured — but
only because **0 of 4,673 tests are corroborated at all** after 14.1. That is an **empty
denominator**: `UNEVALUABLE`, not a confirmation. It is the same shape `sprint-change-proposal-
2026-08-17.md` §2.5 records for the precision gate. **The mechanism above is the evidence; the
corpus figure is not.**

**Resolution — DN-14-2-1, taken here, not left to the dev** (see the Decisions section for the
rejected alternative). The locked asymmetry decides it: *a false 🔴 is the lethal failure; a real
vacuous test left advisory is tolerable.* **The corroboration path (fact (a) AND fact (b)) reads a
FROZEN assertion vocabulary pinned to 14.1's 23 names. Only the density NUMERATOR reads the widened
one.** This is what makes 14.1's promise true instead of merely written, and it is what lets 14.3
widen the table again — across four languages — without re-opening the moat.

### §0.5 — Guards: predict BEFORE you measure

Changing the denominator moves flag rates, so some of these are EXPECTED to move and some must not.
**Write your prediction in the Dev Agent Record before running the suite, then record the result
beside it.** A prediction produced after the measurement is not a prediction.

| Guard | Where | Expectation | Why |
|---|---|---|---|
| `TC-ArgusAgent-DETECT-001-87` | `test_vacuous_detector.py:194` | ⛔ **MUST NOT MOVE** | Fixture is 5 single-line statements; line count == statement count. If it moves, your denominator is wrong |
| `TC-ArgusAgent-DETECT-001-88` | `:221` | ⛔ **MUST NOT MOVE — the false-accusation guard, the moat's own test** | 2 single-line statements. A genuine test must stay unflagged |
| `TC-ArgusAgent-DETECT-001-89`/`-90`/`-91` | `:238`/`:254`/`:269` | must not move | degrade paths, no density involved |
| `TC-ArgusAgent-DETECT-001-93` | `:304` | ⛔ **MUST NOT MOVE** | it asserts `assertion_density == Fraction(1, 5)` exactly, and its fixture is 5 **single-line** statements — line count == statement count. A move here means your denominator is wrong on the trivial case. (If it ever does move, that is an intended behaviour change to be re-authored `-86`-style with its reason — **never** an expected number nudged to match output) |
| `TC-ArgusAgent-DETECT-001-101`..`-108` | `:348`-`:800` | must not move | 14.1's fact-(b) branch coverage; single-line fixtures |
| `TC-ArgusAgent-DETECT-001-109`/`-110` | `:653`/`:701` | ⚠️ **THE MOST LIKELY TO BREAK, and the failure will be misleading** | their fixtures are *about* line-wrapped statements, and they route through `_corroborated` (`:338-344`), which asserts `len(result.findings) == 1` — **the fixture must still be FLAGGED**. A wrapped statement now counts **once**, so `statement_count` falls and density RISES; a fixture can drop below the flag threshold and the test fails on *"the heuristic must still FLAG"* — which reads like a corroboration regression and is not one. If it happens, **strengthen the fixture so it is still flagged and still tests wrapping**; do not delete the case, do not touch the denominator to save it |
| `TC-ArgusAgent-DETECT-001-111`/`-112` | `:987`/`:1032` | ⚠️ lower risk, same mechanism | `;`-compound fixtures, also via `_corroborated`. A `;` compound now counts as **2** statements, so density FALLS and they stay flagged — the safe direction. Confirm rather than assume |
| `TC-ArgusAgent-VERDICT-001-30` (two-arm structure) | `test_default_path_blocking_verdict.py:243` | ⛔ **BOTH ARMS MUST SURVIVE** | 14.1 hardened it to measure the promoted new witness AND the demoted old fixture on one default path. Preserving *both* arms is the point; a single-arm `-30` is a regression of 14.1's escalation resolution |
| `TC-ArgusAgent-VERDICT-001-116`/`-117` | `:329`/`:415` | ⛔ **MUST NOT MOVE** | end-to-end proof that wrapping/semicolons alone cannot reach a blocking verdict. If either goes red you have re-opened 14.1 |
| `test_dogfood_plan.py` · `test_dogfood_proof.py` · `test_dogfood_artifact_currency.py` | — | ⚠️ **EXPECTED to fire** | detector-output-dependent. Discharge via AI-E12-11 (§0.9), never by editing an artifact |
| `test_pipeline_signature_demo.py` | — | ⚠️ **may fire** | the FR32 demo, the line the PRD calls *"the product"*. If it moves, that is not a test to fix quietly — it belongs in the hand-off |
| `test_module_size_ceiling.py` | — | ⚠️ | see §0.7 |

**Blast radius floor, inherited from 14.1 §0.5 and still current:** 21 modules reference the rule
id; **10 stage a cartridge or run the detector end to end** (`test_cartridge_selfaudit.py`,
`test_critical_eligibility_pipeline.py`, `test_detector_base.py`, `test_dogfood_plan.py`,
`test_dogfood_proof.py`, `test_evidence_bundle.py`, `test_grammar_runtime_validation.py`,
`test_pipeline_signature_demo.py`, `test_precision_replay.py`, `test_vacuous_detector.py`), plus
`test_default_path_blocking_verdict.py`. **Treat it as a floor. Run the full suite.**

### §0.6 — The line between this story and 14.3, drawn explicitly

`14-3-the-assertion-vocabulary-crosses-the-languages-the-installer-ships` **runs strictly after this
story and owns the same frozenset.** Leave it in a state 14.3 can extend without re-litigating your
decisions, and do not pre-empt its scope.

| | **14.2 — yours** | **14.3 — NOT yours** |
|---|---|---|
| Vocabulary | Python: pytest helpers, `unittest.mock` assertion methods, the `unittest` gaps, the project-helper naming convention | JS/TS (`expect`, `toBe`, `toEqual`, `toThrow`, `ok`, `deepStrictEqual`), Java/JUnit (`assertThat`, …), Go (`Fatal`, `Errorf`, `NoError`, …) |
| Denominator | ✅ yours entirely | ✗ untouched by 14.3 |
| Corpus members measured | minions, agent-smith (the two contributing members) | additionally `xagents-webapp`, `agent-smith` **as TypeScript** |
| `DF-14-3-A/B/C` | cite only | cite only — still not fixed there |

**What you owe 14.3 (AC7):**

- The set stays **FLAT and language-agnostic** — the `_UNAMBIGUOUS_TEST_SUFFIXES` precedent. **No
  language field, no per-language sub-table, no grouping key enters the detector** (NFR-P2 confines
  the language conditional to `argus/index/`). If you group your additions, group them with
  **comments**, which 14.3 can extend, never with structure it would have to unpick.
- If you introduce a naming-convention **predicate** (§0.3 says you should), it must be a separate,
  named, documented predicate — not entries smuggled into the frozenset — so 14.3 adds names to a
  set whose contract it can read in one place.
- The frozen fact-(b) vocabulary (DN-14-2-1) must be **named for its purpose, not for its
  contents**, so 14.3 inherits the moat protection by construction rather than by remembering to.

### §0.7 — ⚠️ `tests/test_vacuous_detector.py` has 116 lines of headroom

It went **324 → 1,084** during 14.1. NFR-M1's ceiling is 1,200 and
`tests/test_module_size_ceiling.py` sweeps **every tracked `.py`**, `tests/**` included. You are
adding cases; 14.3 adds more after you.

**Do not:** add a size exemption (the registry may only shrink, and `-04` enforces that), narrow the
sweep, or delete existing cases to make room. **Do:** if you cross the ceiling, split by **cohesion**
on the `provenance_scan.py` precedent — e.g. a `tests/test_vacuous_density.py` holding the density /
denominator / assertion-table cases, leaving the corroboration cases where they are. That split is
also the cleaner hand-off to 14.3. Record it if you take it.

### §0.8 — Working tree state you must NOT disturb

Pre-existing uncommitted changes, none of them yours:

```
 M _bmad-output/.../E-PRD/prd.md            M _bmad-output/.../architecture.md
 M _bmad-output/.../deferred-work.md        M _bmad-output/.../epics.md
 M _bmad-output/.../stories/1-5-*.md        M _bmad-output/.../stories/13-4-*.md
 M _bmad-output/.../stories/14-1-*.md
 M tests/test_evidence_citation.py          M tests/test_module_size_ceiling.py
 M tests/test_spec_claim_scope.py           M tests/test_v1_commitment_closure.py
?? argusdemo/  ?? .bmad-drift-audit/  ?? bmad-dev-loop-pack/
?? _bmad-output/audit-reports/*  ?? sprint-change-proposal-2026-08-17{,b}.md
?? _bmad-output/.../stories/15-1-*.md  ?? tests/test_status_document_registry.py
```

⚠️ **`stories/1-5-…md` is itself DIRTY**, and it is the file carrying the struck-not-deleted locked
decision this story amends (`:519-528`). **Read it as it stands on disk. Do NOT commit it**, and do
not treat its uncommitted state as an invitation to rewrite it — AC1.3 says exactly what you may
change there and it is one sentence.

### §0.9 — The dogfood close is pre-authorised (`AI-E12-11`)

`scripts/regenerate_dogfood_artifacts.py` re-renders all three artifacts
(`minions-dogfood-partition-plan.md`, `minions-dogfood-budget-plan.md`, `minions-dogfood-proof.md`)
through their **own** renderers and **refuses to run on a dirty `argus/` tree by design**. The
authorised sequence, already used by 13.2 and by 14.1 three times:

```
commit the argus/ delta  ->  python scripts/regenerate_dogfood_artifacts.py  ->  commit the artifacts SEPARATELY
```

⛔ **Never hand-edit a generated artifact. Never loosen, skip, xfail or narrow an assertion to make a
currency guard green** (`DF-8-5-B`). The provenance sha an artifact cites must be a real commit and
an ancestor of `HEAD`.

---

## Acceptance Criteria

### AC1 — The denominator counts STATEMENTS, and the record is amended at its source

1. `_count_statements` counts **logical statements**: a multi-line statement (bracket-wrapped or
   backslash-continued) counts **once**; a `;`-compound counts once per simple statement; a
   docstring or any other multi-line string literal counts **once**, not once per line.
2. The implementation **REUSES `provenance_scan.logical_statement_starts` and
   `_simple_statement_breaks`** rather than forking a second statement scanner (AR7 / §3.3). Two
   spellings of *"where does a statement start"* is the disagreement class this detector keeps
   closing elsewhere. Whatever cross-line string state you add (§0.2 v2) is added **once**, in
   `provenance_scan.py`, and both consumers read it.
3. The **Story 1.5 locked decision is amended at its source** —
   `stories/1-5-heuristic-vacuous-test-detector-tier-a-vacuous-path-ast-subset.md:519-528` — dated,
   struck, **never erased**. It already carries a 2026-08-17 amendment; **append a dated 2026-08-18
   correction to the `2.04×` figure**, recording the re-measured **1.907×** and *why* the earlier
   number is being corrected rather than overwritten. ⛔ Do not edit the struck text and do not
   commit anything else in that file (§0.8).
4. **Measured, not asserted:** the inflation ratio and the corrected ratio are re-derived on your own
   baseline against CPython's `ast` module as ground truth, and both are recorded as numbers.

### AC2 — Nothing GAINS a flag, and that is demonstrated by execution

1. Over both members at their unchanged pinned shas, the count of tests that **gain** a flag is
   recorded. §0.2 measures **0** for the v2 denominator and **2** for v1.
2. If your implementation gains any flag, each one is **named, its mechanism explained, and it is
   argued or fixed** — never rounded off. "A change that can only remove flags must be shown to have
   only removed them."
3. The docstring/`;` mechanism of §0.2 has a **direct regression test**: a test function whose
   docstring contains a `;` scores the same `statement_count` as the same function without it.

### AC3 — Thresholds and the contract surface are byte-unchanged

1. `ASSERTION_DENSITY_FLOOR = Fraction(1, 4)` and `MOCK_RATIO_CEILING = Fraction(1, 2)` — **proven
   byte-identical by diff**, not by inspection.
2. `VacuousTestScore` keeps its shape: frozen, `extra="forbid"`, same field names and types.
   `assertion_density` and `mock_ratio` remain exact `Fraction`, **never `float`** (AR4).
3. `RULE_HEURISTIC` / `RULE_AST` vocabulary unchanged, and the Story 1.6 verdict-eligibility surface
   (`advisory` + `depth_supported` + `rule_id`) unchanged.
4. The scorer stays **PURE** (AR8) and deterministic (NFR-D2): no clock, uuid, random, or
   iteration-order in any `.argus/`-bound output; any set that reaches a message is `sorted()`.
5. `argus/pipeline.py` is **untouched** (89 lines of headroom).

### AC4 — The flag rate is re-measured over the SAME population and recorded as a number

Before and after, both members, at the unchanged pinned shas. §0.3's table is the prediction to beat;
record your own figures and state any divergence from it as a finding.

### AC5 — The 31 adjudicated findings are re-scored, with the attribution separated

1. All 31 locators are re-scored **by execution** at the pinned shas (they resolve 31/31 today).
2. The attribution is reported **separately** for: denominator alone · assertion names alone · both ·
   neither — §0.3's `14 / 4 / 23 / 8` is the prediction.
3. ⛔ **`verdict-eligible` must remain 0/31.** It is 0/31 today (14.1). If any adjudicated locator
   becomes verdict-eligible again, **STOP and escalate** — that is a regression of 14.1's moat, not a
   number to record.

### AC6 — ⛔ Fact (b) does NOT move, and that is now something you must BUILD, not inherit

1. The **corroboration path — fact (a) `_sut_call_sites` AND fact (b) `provenance_evidence` — reads a
   FROZEN assertion vocabulary pinned to 14.1's 23 names.** Only the density numerator
   (`assertion_call_sites`) reads the widened vocabulary. (DN-14-2-1.)
2. The frozen table is **named for its purpose**, carries a comment explaining that it must not track
   `_ASSERTION_CALLEES`, and states the measured reason (§0.4). A reviewer must not be able to read it
   as an accidental duplicate — it is two different questions, not two spellings of one (see the AR7
   note in Dev Notes).
3. **A guard reproduces §0.4's mechanism**: the mock-interaction fixture must be RED (i.e.
   `ast_corroborated=True`) against a build in which the corroboration path reads the widened table,
   and GREEN (`False`) against the shipped design. **Demonstrate the RED first.** A guard written
   after the fix, over a defect never demonstrated, is `AI-E3-1`.
4. `ast_corroborated` is **byte-identical** for every test whose `heuristically_vacuous` value is
   unchanged, measured over both members.
5. `provenance_scan.py`'s docstring claim *"nothing in this module can grow a dependency on a table
   it cannot see"* is **corrected** — it is false as written (§0.4). Replace it with what DN-4
   actually guarantees (independence from the assertion **count**) and what now enforces the rest.
6. `TC-ArgusAgent-DETECT-001-102`'s comment (`tests/test_vacuous_detector.py:424-426`) is corrected
   in the same change, for the same reason.

### AC7 — 14.3 can extend this without re-litigating it

1. `_ASSERTION_CALLEES` stays **FLAT and language-agnostic**. **No language field, sub-table or
   grouping key enters the detector** (NFR-P2).
2. Any naming-convention admission is a **separate, named, documented predicate**, not entries hidden
   in the frozenset.
3. This story adds **no** cross-language vocabulary — no `expect`, `toBe`, `assertEquals`, `Fatalf`.
   That is 14.3's, measured against its own corpus members.
4. The accepted collision cost of each Python addition is recorded with its error direction (a
   widened table can only *raise* `assertion_sites`, and the floor fires from below — so the density
   half is strictly flag-reducing; the corroboration half is protected by AC6.1 instead).

### AC8 — "Not done on a Windows-only pass" is discharged concretely, not restated

Local gates here are Windows-only; CI runs an ubuntu matrix, and this repository **has already
shipped POSIX-only bugs out of a green Windows run** (`AI-E13-1`). This story reads source text, which
is the most exposed shape there is. "Done" requires **all** of:

1. **No line-terminator assumption.** Everything operates on the `source.splitlines()` list the
   detector already receives — `"a\r\nb".splitlines() == "a\nb".splitlines()`. No regex anchored with
   `$`, no reliance on `\s` spanning a terminator.
2. **No path-separator or encoding assumption** in changed code: `pathlib` only, explicit
   `encoding="utf-8"` on every read, no comparison of a path against a hand-built string.
3. **Unicode-safe name matching.** The naming-convention predicate and every identifier pattern use
   Unicode-aware classes (`[^\W\d]\w*`), so the `nonascii_unicode` cartridge's Cyrillic paths and
   `café_calc.py` keep working.
4. **A CRLF regression test for the DENOMINATOR specifically.** `-107` covers the predicate; nothing
   covers the statement count. Feed the scorer CRLF source and assert a byte-identical
   `VacuousTestScore`. Include a docstring and a wrapped statement in the fixture, since those are
   where the two representations could diverge.
5. ⛔ **`pytest.skip` is a FALSE GREEN here.** `audit-ci.yml` sets
   `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`. The correct pattern for an unavailable tool is a **named
   `Unevaluable` outcome**, never a skip. A skip appearing in the suite is itself the regression
   signal.
6. **An explicit statement of what could NOT be verified locally**, written in the Dev Agent Record:
   name the ubuntu-matrix behaviours you reasoned about but did not execute, and say so. Gates are
   reported as **LOCAL**, with *"CI evidence is NOT ESTABLISHED"* stated, exactly as 14.1 did.

### AC9 — Gates, artifacts and hand-off

1. `pytest` (full suite), `mypy argus`, `bandit -r argus` reported as **numbers**, with the Δ against
   §0.1's baseline (1611 / Success-87 / 19-0-0). **No new skip, xfail, or narrowed population.**
2. The three dogfood artifacts are regenerated **through their own renderers** via `AI-E12-11`'s
   sequence (§0.9) and `test_dogfood_artifact_currency.py` is green. Nothing hand-edited; no
   assertion loosened.
3. Anything deferred is filed in `deferred-work.md` (**append only**) with a **named owner**
   (`AI-E9-8`).
4. `git tag -l` stays empty; no push; nothing outward-facing changed beyond what the ACs require.

---

## Developer Context & Guardrails

### Locked decisions this story must CITE rather than reopen

| Locked | Where | Consequence here |
|---|---|---|
| **A false 🔴 is the lethal failure; a real vacuous test left advisory is tolerable** | `vacuous_test.py` docstring | The asymmetry that decides §0.4 / DN-14-2-1 |
| **CC#6 — no 🔴 without AST corroboration AND sign-off** | `architecture.md` §Cross-Cutting #6 | Why AC6 is release-blocking, not cosmetic |
| **Vacuity-corroboration enforcement** | `architecture.md` §Enforcement (2026-08-17) | The paragraph 14.1 implemented and you must not undo |
| **A failed measurement is not a reason to amend a threshold** | protocol §5; Story 13.3 / AC5 | AC3.1 |
| **Narrowing a population until it goes green is a defect** | `test_module_size_ceiling.py:35-39` | AC2.2, §0.7 |
| **AR7 / §3.3 — one derivation, never a fork** | `architecture.md` §Enforcement | AC1.2 |
| **AR8 pure · AR4 `Fraction` never `float` · NFR-D2 deterministic** | `vacuous_test.py` docstring | AC3 |
| **NFR-P2 — the language conditional stays in `argus/index/`** | `architecture.md` | AC7.1 |
| **NFR-M1 — ≤1200 lines, every tracked `.py`** | `architecture.md` §Enforcement (Module-size) | §0.7 |
| **DN-4 (Story 14.1)** — fact (b) must not be tuned to today's `assertion_sites` | `stories/14-1-*.md` | **Holds for the COUNT. §0.4 shows it does NOT hold for the TABLE** |
| **DN-3 (Story 14.1)** — a raises-context SUT call is CONSUMED | same | `raises`/`warns` are already in `RESULT_OBSERVING_CONTEXT_CALLEES`; adding them to `_ASSERTION_CALLEES` must not disturb that |
| **Full dataflow grounding is Story 6.2's** (`DF-14-1-A`) | 1.5 / 14.1 docstrings | Cite the limit; attempt no dataflow |
| **`AI-E9-8`** — no deferred entry without a named owner | Epic-9 retro | AC9.3 |

### Decisions taken by this story (record each with its rejected alternative)

- **DN-14-2-1 — the corroboration path reads a FROZEN assertion vocabulary; only the density
  numerator reads the widened one.** *Rejected alternative:* one table for everything, with a guard
  asserting corroboration did not move on the corpus. Rejected **on measurement**: the corpus has
  **0** corroborated findings, so such a guard would be green over an empty denominator while §0.4's
  mechanism is live — a test that proves nothing, which is `AI-E3-1`. The frozen table makes the
  property structural instead of measured-against-nothing.
- **DN-14-2-2 — the denominator tracks multi-line string literals.** *Rejected alternative:* reuse
  `logical_statement_starts` as-is. Rejected **on measurement**: it manufactures 2 new flags on the
  corpus from `;` inside docstring prose (§0.2), and lands at 1.134× rather than 1.005× of ground
  truth.
- **DN-14-2-3 — the assertion widening includes a project-helper naming CONVENTION, not just a name
  table.** *Rejected alternative:* the table alone. Rejected **on measurement**: table-alone
  reproduces neither the *"4 of 31"* nor the *"13 of 31"* nor the *"23 / 8 of 31"* figures the change
  proposal and `epics.md` commit this story to (§0.3). Record the accepted collision cost: a
  production helper coincidentally named `assert_*` now counts as an assertion — error direction is
  **one fewer flag**, which is the safe direction for the density half and is neutralised for the
  corroboration half by DN-14-2-1.
- **DN-14-2-4 — the two assertion vocabularies are two QUESTIONS, not two spellings of one.** The
  heuristic asks *"does this test assert anything?"* and wants breadth; fact (a)/(b) ask *"which
  edges are not SUT calls?"* and want stability. State this where a reviewer will look, or it will be
  filed as an AR7 fork. *Rejected alternative:* deriving one from the other (e.g. frozen = widened
  minus a delta set), which re-couples them the moment 14.3 lands.

### Files to touch

| Path | Action |
|---|---|
| `argus/detectors/vacuous_test.py` | **UPDATE** — `_count_statements`, `_ASSERTION_CALLEES`, the frozen fact-(b) vocabulary, `_sut_call_sites`, module docstring. 697 lines, headroom 503 |
| `argus/detectors/provenance_scan.py` | **UPDATE** — cross-line string state (AC1.2), docstring correction (AC6.5). 610 lines, headroom 590 |
| `tests/test_vacuous_detector.py` | **UPDATE** — new cases, `-102`'s comment, any `-93`/`-109`..`-112` re-authoring. ⚠️ **1,084 lines, headroom 116** — see §0.7 |
| `tests/test_default_path_blocking_verdict.py` | **READ; update only if `-30`/`-116`/`-117` genuinely move**, and then as an intended behaviour change with its reason |
| `stories/1-5-…md` | **APPEND ONE DATED CORRECTION** to the amendment at `:519-528` (AC1.3). Nothing else. ⚠️ file is already dirty — do not commit it |
| `stories/14-2-…md` (this file) | **UPDATE** — Dev Agent Record, File List, Change Log |
| `sprint-status.yaml` | **UPDATE** — the `14-2` key only |
| `deferred-work.md` | **APPEND ONLY**, and only if something is deferred |
| Dogfood artifacts | **REGENERATE via `scripts/regenerate_dogfood_artifacts.py`** per §0.9 |
| **Everything else** | ⛔ **DO NOT TOUCH.** In particular `argus/pipeline.py`, `argus/verdict/**`, every cartridge under `tests/cartridges/`, `tests/corpus/_manifest.py`, `validation-corpus/**`, `epics.md`, `architecture.md`, `E-PRD/prd.md`, and every file listed in §0.8 |

### Previous story intelligence — traps already paid for

- **The tree moved under the change proposal.** 14.1 landed today in six commits and rewrote the file
  this story owns. Every figure in `sprint-change-proposal-2026-08-17.md` §1.3 predates it. §0.2/§0.3
  re-derive them; two do not reproduce. **Cite §0, never the proposal, for a number.**
- **`AI-E13-1` — hand off green.** Story 13.3's SM phase wrote a story file, nothing re-ran the
  suite, the commit was pushed, and `audit-ci` went red on ubuntu. Run the full suite **after** your
  last prose edit.
- **Line numbers in this repository drift constantly.** 13.4 found a cite already stale before it
  touched anything. **Locate every block by anchor text**, not by the line numbers in this file.
- **Guards going RED on a full run are usually guards WORKING.** 13.4 hit the `DOCS-001-22` closure
  and did not loosen it. 14.1 hit two dogfood guards and routed them to `AI-E12-11` instead of
  editing an artifact.
- **`story_closure_claims` is LINE-SCOPED** (`test_governance_record_integrity.py:58-72`). **Never
  put a `DF-*` id on the same line as `CLOSED`, `Closes` or `closes`** unless `deferred-work.md`
  really carries that closure. `DOCS-001-78` globs `stories/*.md`, so this file is inside it.
- **A new status document must be registered in the SAME change that creates it**
  (`architecture.md` §Enforcement, added by 13.4). This story creates none; if you produce one,
  register it in `tests/test_status_document_registry.py` immediately.
- **14.1 measured a population divergence and used its own numbers.** §0's figures agree with 14.1's
  exactly (3,551 / 1,848 / 1,122 / 681), which is the harness being right twice — but the §0 harness
  is still validated the only way that counts: it reproduces **all 31** adjudicated locators as
  flagged at the pinned shas.

### Testing requirements

- **RED-then-green at the real seam.** Every new behaviour is demonstrated from the **real detector
  over the real tree-sitter index**, not from a reconstruction — the denominator cases, the
  docstring/`;` case (AC2.3), and above all AC6.3's corroboration guard.
- **Every branch of the new denominator needs a test that reaches it:** wrapped statement,
  backslash continuation, `;`-compound, docstring (single- and triple-quoted, and one containing a
  `;`), comment-only line, blank line, nested block, a statement inside a `with`.
- **Both directions on the assertion table.** A test containing only a pytest/`unittest.mock`
  assertion is no longer flagged (recall of the fix), **and** a genuinely assertion-free test still
  is (the fix did not just delete the signal). A one-directional check would pass on a change that
  removed the flag by removing the capability.
- **Non-vacuity is mandatory.** If a new helper can return an answer for a reason that never occurs,
  it is decoration. Enumerations carry a `> 0` floor.
- **The full suite is the gate** (§0.5), plus `mypy argus` and `bandit -r argus`, reported as numbers.
- **CRLF and non-ASCII** per AC8.3/AC8.4.

### Project structure notes

- `argus/detectors/*` is a **leaf** package — the import-isolation gate keeps it so. Add no import
  edge out of it (`vacuous_test.py` imports `detectors.base`, `index.ast_index`,
  `ledger.coverage_ledger` and `detectors.provenance_scan`; that is the whole list).
- Modules are `snake_case.py`, ≤1200 lines (NFR-M1). Any split follows the
  `pipeline_stages.py` / `provenance_scan.py` precedent: a **cohesion** boundary, no function split
  across it, the caller imports back.
- Test ids are `TC-ArgusAgent-<AREA>-<NNN>-<nn>`; new density cases continue the `DETECT-001-` series
  (`-112` is the highest in use).

### References

- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Story 14.2`] — the AC set this story expands
- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Story 14.3`] — the boundary in §0.6
- [Source: `_bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-08-17.md#1.3, #4.1, #4.2`] — findings B/C and the 1.5 amendment (figures superseded by §0.2/§0.3)
- [Source: `_bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-08-17b.md`] — Story 14.3's scope
- [Source: `_bmad-output/design-artifacts/ArgusAgent/stories/1-5-…md:519-528`] — the locked denominator decision, struck-not-deleted
- [Source: `_bmad-output/design-artifacts/ArgusAgent/stories/14-1-…md#DN-3, #DN-4, #§0.5`] — the decisions and blast radius this story inherits
- [Source: `_bmad-output/design-artifacts/ArgusAgent/architecture.md#Cross-Cutting #6, #Enforcement`] — the moat, module-size, dogfood-currency and name-classification rules
- [Source: `_bmad-output/design-artifacts/ArgusAgent/epic-12-retro-2026-08-15.md#AI-E12-11`] — the pre-authorised dogfood close
- [Source: `argus/detectors/vacuous_test.py`, `argus/detectors/provenance_scan.py`] — read completely at contexting time; §0.4's finding comes from that reading and was then reproduced by execution

---

## Tasks & Subtasks

- [x] **Task 0 — Re-measure the premise on YOUR baseline (AC: 9.1)**
  - [x] Record `HEAD`. Re-run the three gates; report any divergence from §0.1 as a finding.
  - [x] Re-measure the flag rate and population, both members at the pinned shas (expect 1,848/3,551
        and 681/1,122), so AC4 has a before-number that is yours.
  - [x] Re-measure the denominator inflation against CPython `ast` (expect **1.907×**, *not* 2.04×).
  - [x] Confirm 0/4,673 corroborated and 31/31 flagged / 0/31 verdict-eligible, so AC5.3 has a floor.
  - [x] **Write your guard predictions (§0.5) into the Dev Agent Record NOW, before touching code.**
- [x] **Task 1 — Reproduce §0.4 before you fix it (AC: 6.3)**
  - [x] Stand up the mock-interaction fixture through the real index and show `CORROBORATED=False`
        today and `True` under a naively-widened table. **RED first.**
  - [x] Only then design DN-14-2-1's frozen vocabulary.
- [x] **Task 2 — The statement denominator (AC: 1, 2)**
  - [x] Add cross-line string state in `provenance_scan.py`; reuse `logical_statement_starts` +
        `_simple_statement_breaks`. **No second scanner.**
  - [x] Rewrite `_count_statements` over it. Keep it PURE and line-terminator-agnostic.
  - [x] Measure flags gained (target **0**) and lost, both members. Name any gain.
  - [x] Regression test for the `;`-in-docstring mechanism.
- [x] **Task 3 — The assertion vocabulary (AC: 3, 6, 7)**
  - [x] Widen `_ASSERTION_CALLEES`: pytest helpers, `unittest.mock` assertion methods, `unittest`
        gaps. Flat, language-agnostic, comment-grouped only.
  - [x] Add the naming-convention predicate, named and documented.
  - [x] Pin the frozen fact-(b)/(a) vocabulary; route `provenance_evidence` and `_sut_call_sites`
        to it; prove `ast_corroborated` byte-identical (AC6.4).
  - [x] Correct `provenance_scan.py`'s docstring and `-102`'s comment (AC6.5/6.6).
- [x] **Task 4 — Re-measure and attribute (AC: 4, 5)**
  - [x] Flag rate, both members, before/after. Record as numbers.
  - [x] The 31 locators: denominator alone / names alone / both / neither. Predict §0.3's
        `14 / 4 / 23 / 8`, then measure.
  - [x] ⛔ Verdict-eligible must be 0/31. If not, **STOP and escalate.**
- [x] **Task 5 — The record (AC: 1.3)**
  - [x] Append the dated 2026-08-18 correction to `stories/1-5-…md:519-528`. Struck, never erased.
        Nothing else in that file.
- [x] **Task 6 — Platform neutrality (AC: 8)**
  - [x] CRLF regression test for the denominator specifically; Unicode-safe matching; no `$`-anchored
        regex; `pathlib` + explicit `encoding="utf-8"`.
  - [x] Write the explicit "what could NOT be verified locally" statement.
- [x] **Task 7 — Gates, artifacts, hand-off (AC: 9)**
  - [x] Full suite + `mypy argus` + `bandit -r argus`, as numbers with Δ. No new skip.
  - [x] Check `tests/test_vacuous_detector.py` against the 1,200 ceiling; split by cohesion if needed
        (§0.7). **No exemption.**
  - [x] Run `AI-E12-11`'s commit → regenerate → commit-separately sequence (§0.9).
  - [x] File anything deferred with a named owner. Re-run the suite **after** your last prose edit.

### Review Findings

**Code review (Sonnet, iteration 1, 2026-08-18) — independent re-derivation by execution, not
inspection.** Both members re-staged fresh at their unchanged pinned shas (`ec63b729` minions,
`9ab774d7` agent-smith) into two isolated `git worktree`s of `966ceba`/`a9cf25d`, scored through
the SHIPPED `build_ast_index` + `VacuousTestDetector._score` with an independent harness (not the
dev's script). Every headline number reproduced EXACTLY: minions 1,848/3,551 (52.0%) → 660/3,551
(18.6%); agent-smith 681/1,122 (60.7%) → 297/1,122 (26.5%); flags **GAINED 0** in both members
independently (1,188 + 384 = 1,572 lost, matching "1,572 lost / 0 gained" precisely). CPython `ast`
ground truth re-derived independently for the full 1,848-function (minions) and 681-function
(agent-smith) before-flagged populations: LINE-count ratio 29,093/15,255 = **1.9071×** (exact),
statement-count ratio 15,334/15,255 = **1.0052×** (exact), exact match on **1,784/1,848 = 96.5%**
(exact) — every digit of AC1's completion-note claim reproduced independently, including the
agent-smith ground-truth divergence the Dev Agent Record itself flags (my own re-count: 6,608, not
§0's 6,600 — confirms the dev's own stated divergence is real, not smoothed over). The DN-14-2-1
load-bearing experiment was reproduced literally: `assertion_callees=_ASSERTION_CALLEES` was
substituted for `_CORROBORATION_ASSERTION_CALLEES` at `vacuous_test.py:916` in an isolated
worktree and the full suite re-run — `-115` is the ONLY failure (`vacuous_test_ast` where
`vacuous_test_heuristic` was expected), `test_default_path_blocking_verdict.py` (`-30`/`-116`/`-117`)
stays 100% green, and reverting restores byte-identical `git diff`. Gates independently
re-measured in ArgusAgent's OWN venv (not the one first tried, which turned out to be a sibling
project's): `pytest` — JUnit XML shows `tests="1619" errors="0" failures="1" skipped="0"`, and the
one failure is a verification-harness artifact (a `git worktree` literally named `after` trips a
project-name-leak assertion in `test_gate_decision.py`, unrelated to the diff — confirmed by
running the same test at `966ceba` with no patch applied, where it passes); `mypy argus` —
`Success: no issues found in 87 source files`; `bandit -r argus` — `19 Low / 0 Medium / 0 High`,
confidence `0/0/6/13`. Thresholds proven byte-identical by `git diff -U0` (empty). `argus/pipeline.py`
diff empty. Module sizes confirmed (919/815/1128/814, all ≤1200); `test_module_size_ceiling.py`
diff empty (no exemption added). Cartridge/critical-eligibility suites re-run clean. `DF-14-2-A`
confirmed a real, well-scoped, honestly-bounded deferral with a named owner (Story 14.3 dev) and a
real mechanism (`importorskip` ignoring `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`), not a parking space —
and the story's OWN new module (`test_vacuous_density.py`) is confirmed to use the correct
`Unevaluable`-failure pattern rather than the deferred `importorskip` one. `stories/1-5-…md`'s
2026-08-18 correction independently checked: struck text untouched, 2026-08-17 amendment left
standing (superseded, not overwritten), and every re-measured figure it carries (1,848 / 1.907× /
1.005× / 1,784-of-1,848) matches my own independent re-derivation exactly.

- [x] [Review][Patch] The AC1 docstring's claim about the residual error's DIRECTION is measurably
  wrong; the actual dominant mechanism is an OVER-count, not the claimed under-count
  [`argus/detectors/provenance_scan.py:359-380`, `argus/detectors/vacuous_test.py:701-721`] —
  `logical_statement_count`/`body_statement_count`'s docstrings (and AC1's Completion Notes) state
  the residual against CPython `ast` is "a bounded, deterministic under-count in the direction that
  RAISES density, i.e. away from a flag" (citing `with x: y()` as the mechanism). Independently
  measured: of the 64 (minions) / 28 (agent-smith) non-exact spans in the 1,784/1,848-exact
  population, **64/64 and 27/28 are OVER-counts** (scan > CPython ground truth), the opposite
  direction — which LOWERS density, i.e. biases TOWARDS a flag. Root cause, isolated with a minimal
  repro and confirmed against real corpus functions: every `except`/`else`/`finally` clause header
  on an `if`/`for`/`while`/`try`, and every `case` clause header in `match`/`case`, is counted by
  `_scan_span` as opening its own statement, but corresponds to NO additional `ast.stmt` node in
  CPython's ground truth (`ast.Try`/`ast.If`/`ast.Match` is ONE stmt regardless of how many
  handler/case clauses it carries). Minimal repro: `try: a() / except V: pass / else: b() /
  finally: c()` scores 8 via `body_statement_count` vs. 5 via CPython `ast.stmt` walk (diff +3,
  from the three continuation-clause headers). Real corpus instances, independently located:
  `tests/apaa/test_prosecutor.py::test_malformed_top_level_arguments_raise_typed_error` (two
  `try/except/else` blocks; scan 15 vs. ground truth 11) and
  `tests/conformance/cases/test_llm_provider_conformance.py::test_secret_not_in_exception_repr`
  (scan 39 vs. ground truth 35). This is a genuine, reproducible defect in the exact mechanism this
  story exists to fix ("stops flagging... for reasons that are arithmetic rather than evidence") —
  reintroduced in smaller, differently-shaped form — and the docstring's specific factual claim
  about the residual's direction should not stand uncorrected in a story whose stated method is
  "measured, not asserted." **Severity capped at Low per the fixture-gate calibration this review
  was scoped under**: the defect can only feed `heuristically_vacuous` (the advisory,
  non-verdict-eligible path) — `ast_corroborated`/`RULE_AST` is completely independent of density
  and reads the FROZEN vocabulary via a wholly separate code path (DN-14-2-1), so this cannot by
  itself manufacture a verdict-eligible false accusation; it is bounded to advisory noise. Suggested
  fix: either correct the docstring/Completion-Notes claim to describe both real mechanisms
  (dominant over-count from bare continuation-clause headers vs. minority under-count from inline
  one-line compounds), or — better — stop `_scan_span` from opening a new statement on a
  continuation-clause header line that carries no code of its own past the colon, which would also
  raise the 96.5%/95.9% exact-match rate.
- [x] [Review][Defer] `_ASSIGNMENT_RE` is `$`-anchored, contradicting the module's own "no pattern
  below is anchored with `$`" claim [`argus/detectors/provenance_scan.py:65,116-120`] — deferred,
  pre-existing. Byte-identical at `966ceba` (Story 14.1), not touched by this story. Not practically
  exploitable today: `_ASSIGNMENT_RE.match(code)` is always invoked on a single
  `splitlines()`-derived line with no embedded terminator, so `$` behaves like `\Z` in practice; the
  risk is purely that the docstring's blanket claim is not quite true. Out of this story's blast
  radius per the review's own scope rule (validate findings against the diff actually reviewed).

---

## Review iteration 1 — resolution (2026-08-18, dev pass 2)

**Both findings closed: 1 fixed, 1 confirmed-deferred. `2/2`.** Baseline for this pass: `HEAD` =
`a9cf25d`. Landed as `2eeaace` (code) → `e2e278c` (artifacts).

### Finding 1 — the residual's DIRECTION. FIXED at the mechanism, then the prose re-derived

The reviewer offered two remedies and preferred the real one. **(a) was clean, so (a) was taken
and the prose was then rewritten to match what was measured afterwards — not before.**

**The finding reproduced first, exactly.** Before touching anything, the review's minimal repro was
run through the shipped `body_statement_count`: `try/except/else/finally` scored **8** against
CPython's **5** (+3, one per continuation-clause header). Re-derived over the full pinned
populations at `a9cf25d`: of the non-exact spans, **64 of 64** (minions) and **27 of 28**
(agent-smith) were OVER-counts. Every digit of the finding reproduced independently.

**What was wrong, mechanically.** `_scan_span` opens a logical statement on every line that starts
one, and an `except` / `else` / `finally` / `case` header starts a **clause**, not a statement.
CPython builds ONE `ast.Try` however many handlers it carries, ONE `ast.If` however its `orelse` is
spelled and ONE `ast.Match` however many arms it has; `ast.ExceptHandler` and `ast.match_case` are
not `ast.stmt` subclasses at all.

**Two rules, not one — the second was found by measurement, not by guessing.** After the
clause-header rule the corpus still held exactly **one** over-count in 4,673 spans:
`test_quality_gate_default_on.py::test_unevaluable_toggle_resolves_to_enforcing`, whose body defines
a nested class carrying an `@property`. A decorator is an expression in `decorator_list`, not a
statement. `_is_decorator` closes it. **This was a deliberate scope extension and it is recorded as
one:** it is what makes the residual's direction *unambiguous*, which is the entire substance of a
finding about a safety-direction claim — leaving one over-count in would have meant writing the
corrected prose with a caveat instead of a fact.

**Where the rules are applied, and why it matters.** Both at the COUNT
(`_counted_statement_texts`), never inside `_scan_span`. `logical_statement_starts` — fact (b)'s
boundary map, which Story 14.1's moat rests on — is therefore **byte-identical**: a call on a
clause-header line is still attributed to that line. `-122` asserts the whole map for a fixture
containing a wrapped statement inside a `try`, two clause headers and an `else`. A denominator fix
must not reach into the corroboration path; that is DN-14-2-1's coupling class arriving through a
different door, and it is closed by construction rather than by hope.

**RED-first, confirmed before green (the reviewer checks this claim).**

| Guard | RED against | Observed RED | Now |
|---|---|---|---|
| `-121` clause rows | shipped `a9cf25d` code | `try/except/else/finally` **8 vs 5**; `if/else` 5 vs 4; `for/else` 5 vs 4; `while/else` 5 vs 4; `match/case` **6 vs 4**; wrapped `except(` header 5 vs 4 | green |
| `-121` decorator rows | shipped `a9cf25d` code, re-run from a worktree of it | `@property` **5 vs 4**; wrapped decorator **5 vs 4** | green |
| `-121` negative controls | — | `elif` 5 vs 5, inline `except V: b()` 4 vs 4, `case` as a NAME 2 vs 2, `a @ b` 2 vs 2 — **already correct before the fix**, so an over-reaching predicate fails here | green |
| `-122` fact-(b) map | shipped `a9cf25d` code | count 7 vs 5 RED **while `logical_statement_starts` already passed** — i.e. the RED was in the count only | green |

`elif` is excluded from the rule on purpose: `if/elif` IS a nested `ast.If`, a genuine extra
statement. Sweeping it in would have *under*-counted, and the negative control is there so a future
hand cannot.

**RE-MEASURED after the change** (both members re-staged fresh at their **unchanged** pinned shas
`ec63b729` / `9ab774d7`, scored through the SHIPPED `build_ast_index` + `VacuousTestDetector._score`;
ground truth = every `ast.stmt` in the body, recursively, from CPython itself):

| | shipped `966ceba` | iteration 1 `a9cf25d` | **this pass** |
|---|---|---|---|
| minions denominator ÷ ground truth (n=1,848 before-flagged) | 29,093 ÷ 15,255 = **1.9071×** | 15,334 = **1.0052×** | **15,255 = 1.0000×** |
| …exact-span count | — | 1,784 / 1,848 = 96.5% | **1,848 / 1,848 = 100.0%** |
| agent-smith ÷ ground truth (n=681) | 13,148 ÷ 6,608 = 1.9897× | 6,637 = 1.0044× | **6,606 = 0.9997×** |
| …exact-span count | — | 653 / 681 = 95.9% | **680 / 681 = 99.9%** |
| non-exact spans, by direction | — | **64 OVER / 0 UNDER** · **27 OVER / 1 UNDER** | **0 OVER / 0 UNDER** · **0 OVER / 1 UNDER** |
| whole population (n=4,673) | — | — | **4,672 exact, 0 over-counts, 1 under-count** |
| minions flag rate | 1,848 / 3,551 = 52.0% | 660 = 18.6% | **653 / 3,551 = 18.4%** |
| agent-smith flag rate | 681 / 1,122 = 60.7% | 297 = 26.5% | **295 / 1,122 = 26.3%** |
| flags **GAINED** | — | 0 | **0** vs `966ceba` **and** 0 vs `a9cf25d` |
| flags lost | — | 1,572 | **1,581** (1,195 + 386) |
| `ast_corroborated` on unchanged-heuristic spans | — | — | **identical, 4,664 / 4,664** |
| corroborated anywhere | 0 / 4,673 | 0 / 4,673 | **0 / 4,673** |
| the 31 adjudicated locators | 31 resolve / 31 flagged | 13 · **14 / 4 / 23 / 8** | **31 resolve · 13 · 14 / 4 / 23 / 8 — every cell unchanged** |
| ⛔ verdict-eligible of the 31 | 0 / 31 | 0 / 31 | **0 / 31** |
| cartridge recall | 4/4 | 4/4 | **4/4 unchanged** (`test_cartridge_selfaudit.py` green; every planted/holdout/trap cartridge hits its golden key, `clean_control` still unflagged) |

**The deltas, stated explicitly because a denominator change moves flag counts by design.** Nine
tests changed verdict — minions 660 → 653 (**−7**), agent-smith 297 → 295 (**−2**) — all in the
LOSE direction. **The number that must not move is flags GAINED, and it is 0 against both
baselines.** That is structural, not lucky: the denominator can only shrink, so
`assertion_density` can only rise; the `1/4` floor fires from **below**; and `mock_ratio` is taken
over `call_sites`, never over the statement count — so no arm of `heuristically_vacuous` can turn
on. The AC5 attribution and the 31 locators did not move at all: not one adjudicated span is
affected by the nine.

**The prose now matches the measurement, and says so.** `logical_statement_count`'s docstring
carries the corrected paragraph — the old claim quoted, marked wrong, with the 64/64 and 27/28
figures that falsified it, and the direction as it now measures. `_count_statements` carries the
same correction in short form. `-113`'s stale `1.005× / 1,784-of-1,848` is updated to
`1.0000× / 1,848-of-1,848` with the iteration-1 figures kept as the superseded record rather than
erased. **The original claim is now TRUE of the code as it stands** — the sole residual in 4,673
spans is the inline compound header (`def f(): return 0`, `with x(): y()`: two statements to
CPython, one line here), a bounded UNDER-count that raises density and moves away from a flag. It
was made true rather than merely asserted, which is the whole of the point.

### Finding 2 — `DF-14-2-B`. Confirmed deferred, code untouched

`_ASSIGNMENT_RE`'s `$` anchor is byte-identical to `966ceba` and was not touched. The ledger entry
was checked and is well-formed: `id` `DF-14-2-B`, `origin_story` (naming Story 14.1 as the true
origin), **named owner** *"next dev to open `argus/detectors/provenance_scan.py`"*, `target_story`
14.3, `category`, `severity` 🟢 with its bound. Nothing to complete.

⚠️ **One honest note, since this pass DID open that module.** The entry's own wording says the
defect *"should be corrected the next time that module is opened"*, and I opened it. It was left
alone deliberately, on instruction and on scope: fixing it would widen a two-line-finding diff into
an unrelated regex change on fact (b)'s assignment reader, which is exactly the blast radius this
story was told not to enter. The entry stands, unmodified, with its owner intact.

---

## Dev Agent Record

### Agent Model Used

claude-opus-5 (1M context), BMAD `dev-story` worker, 2026-08-18, baseline `HEAD` = `966ceba`.

### Task 0 — the premise, re-measured on MY baseline

Harness: both members staged from their **own** clones at the pinned shas via
`git -C <WINDOWS path> cat-file --batch` (`ec63b729…` in `D:\ProjectX\XAgents\XAgents\Minions`,
`9ab774d7…` in `D:\ProjectX\XAgents\XAgents\XAgents\Agent-Smith` — both `git cat-file -t` →
`commit`), scored through the SHIPPED `build_ast_index` + `VacuousTestDetector._score`. Ground
truth = CPython `ast`, every `ast.stmt` in the function body, recursively.

| Premise | §0 says | I measured | |
|---|---|---|---|
| gates | 1611 / Success-87 / 19-0-0 | **1611 passed, 0 failed, 0 skipped, exit 0** · **Success: no issues found in 87 source files** · **19 Low / 0 Med / 0 High, confidence 0/0/6/13** | ✅ identical |
| minions functions / flagged | 3,551 / 1,848 = 52.0% | **3,551 / 1,848 = 52.0%** | ✅ |
| agent-smith functions / flagged | 1,122 / 681 = 60.7% | **1,122 / 681 = 60.7%** | ✅ |
| inflation, minions flagged | 1.907× (29,093 ÷ 15,255) | **1.9071× (29,093 ÷ 15,255)** | ✅ — and 2.04× does NOT reproduce |
| inflation, both members flagged | 1.933× (42,241 ÷ 21,855) | **1.9321× (42,241 ÷ 21,863)** | ⚠️ ground truth differs by **8** stmts (0.04%) |
| inflation, all functions | 1.676× (60,027 ÷ 35,810) | **1.6759× (60,027 ÷ 35,818)** | ⚠️ same 8 |
| corroborated anywhere | 0 / 4,673 | **0 / 4,673** | ✅ AC5.3's floor |
| the 31 adjudicated locators | 31 resolve / 31 flagged / 0 verdict-eligible | **31 / 31 / 0** | ✅ harness validated against ground truth |

**Divergence recorded rather than smoothed (`DF-8-5-C`):** my CPython ground truth for
*agent-smith* is **6,608**, §0's is 6,600 — an 8-statement (0.12%) difference confined to that
member; minions is byte-identical at 15,255. It moves the reported ratio by 0.0004 and changes no
decision, so §0's ratio is confirmed, not corrected. It is stated because the story's own control
is to state divergences rather than carry them.

### Guard predictions (written BEFORE measuring — §0.5)

Written after reading each fixture and hand-computing its new denominator/numerator, and
**before** a single line of `argus/` was edited. Where I disagree with §0.5 I say so here, so the
disagreement is a prediction and not a post-hoc excuse.

| Guard | §0.5 expects | **My prediction** | Mechanism I reasoned from |
|---|---|---|---|
| `DETECT-001-87` | must not move | **unchanged** | 5 single-line body statements, no widened callee among `do_a/do_b/do_c/compute`; 1/5 either way |
| `DETECT-001-88` | must not move | **unchanged** | 2 single-line statements, 1/2 ≥ 1/4 both ways |
| `-89`/`-90`/`-91` | must not move | **unchanged** | degrade paths, denominator never reached |
| `-93` | must not move | **unchanged** | 5 single-line statements; `a/b/c/d/z` are not assertion names; exactly 1/5 |
| `-101` | must not move | ⚠️ **I PREDICT IT BREAKS** | its fixture has 6 statements and **`raises` on line 4**. `raises` enters the *density* vocabulary, so `assertion_sites` 1 → 2 and density 1/6 → **2/6 = 1/3 ≥ 1/4** → NOT flagged → `_corroborated`'s `len(findings) == 1` fails. This is the widened TABLE, not the denominator, and the fixture becomes genuinely well-asserting — so the fix is to strengthen the fixture, never the table |
| `-102` | must not move | ⚠️ **I PREDICT IT BREAKS** | 9 statements, 2 bare asserts = 2/9 today. **`assert_called` matches the naming convention**, so 3/9 = **1/3 ≥ 1/4** → NOT flagged → same `len(findings) == 1` failure, same remedy |
| `-103`..`-106`, `-108` | must not move | **unchanged** | `configure`/`calculate`/`ping`/`dispatch`/`calculer` match neither the table nor the convention; `-106` moves 6 → 5 statements (the wrapped call) and stays under 1/4 at 1/5 |
| `-107` | must not move | **unchanged** | CRLF vs LF over `_score`; both representations feed the same `splitlines()` list |
| `-109` | ⚠️ most likely to break | **unchanged** — I disagree with §0.5 | hand-computed all five rows: the four bound spellings land at 5 statements (from 5/6/7/7/8 lines) and the discarded control at 6, all with 1 assert → 1/5 or 1/6, both **still under** 1/4. Density rises but not far enough to clear the floor |
| `-110` | ⚠️ same mechanism | **unchanged** — same reasoning | the three spellings collapse 5/8/8 lines → 5/5/5 statements, 1 assert → exactly 1/5 each |
| `-111`/`-112` | ⚠️ lower risk | **unchanged** | `;` compounds now count as **2**, so density FALLS (1/6 → 1/7) — the safe direction, as §0.5 predicts |
| `VERDICT-001-30` (both arms) | both must survive | **unchanged** | arm 1's witness is 5 single-line statements / 1 assert; arm 2 is flagged by the **mock ceiling** (2/3 > 1/2), which this story does not touch |
| `VERDICT-001-116`/`-117` | must not move | **unchanged** | `-116`'s wrapped sources collapse 8/7 lines → 6 statements but keep flagging on the mock ceiling; `-117`'s three arms move 6 → 7 statements (the `;`) and stay at 1/7 |
| cartridge recall (`vacuous_basic`, `holdout_vacuous`, `nonascii_unicode`, `vacuous_heuristic_basic`) | — | **unchanged, 4/4** | all four are single-line-statement bodies whose callees (`compute_total`/`tally`/`calculer`/`total_amount`…) match neither vocabulary |
| `test_dogfood_*` | expected to fire | **will fire** | detector-output-dependent; discharged via `AI-E12-11`, never by editing an artifact |
| `test_pipeline_signature_demo` | may fire | **will not fire** | it asserts the demo's shape, not a flag count |
| `test_module_size_ceiling` | ⚠️ | **will fire unless I split** | `test_vacuous_detector.py` is at 1,084/1,200 and this story adds cases — so I split by cohesion up front (§0.7), no exemption |

**Predicted corpus outcome** (§0.3's table is the number to beat): minions **660 = 18.6%**,
agent-smith **297 = 26.5%**; attribution over the 31 **14 / 4 / 23 / 8**; flags GAINED **0**.

### Debug Log

**Guard predictions vs. what happened — including the one I got right and the one §0.5 got wrong.**

| Guard | §0.5 | My prediction | **MEASURED** | |
|---|---|---|---|---|
| `-87`, `-88`, `-89`..`-91`, `-93` | must not move | unchanged | **unchanged** | ✅ both right |
| `-101` | must not move | ⚠️ **breaks** | **BROKE** — `len(result.findings) == 0`, "the heuristic must still FLAG" | ✅ my prediction, ❌ §0.5's |
| `-102` | must not move | ⚠️ **breaks** | **BROKE** — same assertion, same mechanism | ✅ my prediction, ❌ §0.5's |
| `-103`..`-108` | must not move | unchanged | **unchanged** | ✅ |
| `-109` | ⚠️ **most likely to break** | unchanged | **unchanged** | ❌ §0.5's prediction was **WRONG**, recorded as wrong |
| `-110` | ⚠️ same mechanism | unchanged | **unchanged** | ❌ §0.5 wrong, ✅ mine |
| `-111`/`-112` | ⚠️ lower risk | unchanged | **unchanged** | ✅ both |
| `VERDICT-001-30` (both arms), `-116`, `-117` | must not move | unchanged | **unchanged, both arms intact** | ✅ |
| cartridge recall | — | 4/4 unchanged | **unchanged** — every planted/holdout/trap cartridge hits its golden key, `clean_control` still unflagged | ✅ |
| `test_dogfood_plan` / `_proof` | expected to fire | will fire | **FIRED** (3 cases) — discharged via `AI-E12-11` | ✅ |
| `test_pipeline_signature_demo` | may fire | will not | **did not fire** | ✅ |
| `test_module_size_ceiling` | ⚠️ | fires unless I split | **did not fire — I split first** | ✅ |

⚠️ **§0.5's headline prediction was wrong, and it is worth saying why rather than just that.** It
expected `-109`/`-110` to be *"the most likely to break"* because a wrapped statement now counts
once, so `statement_count` falls and density RISES. The mechanism is right; the magnitude was not
checked. Hand-computed before running: those fixtures collapse from 5–8 lines to 5–6 statements
against **1** assertion, i.e. from 1/6–1/8 up to 1/5–1/6 — a real rise that lands nowhere near the
1/4 floor. Nothing in `-109`/`-110` moved.

The two that DID break broke on the **assertion table**, which §0.5 did not consider a source of
movement for the `-101`..`-108` block at all (it lists them as "single-line fixtures", reasoning
only about the denominator). `-101` carries `pytest.raises` and `-102` carries `assert_called`;
both are assertions the widened vocabulary now sees, and both fixtures had only 6 and 9 statements,
so each crossed the floor on the numerator alone (1/6 → 2/6; 2/9 → 3/9). §0.5's diagnosis
instruction still applied verbatim — the failure reads as a corroboration regression and is not one
— so the remedy was §0.5's: **strengthen the fixture, do not touch the predicate or the
vocabulary**. Five and four mock-configuration lines respectively (they emit no call edge and no SUT
call, so they move the denominator and nothing else) put them back at 2/10 and 3/13. Recorded in
each docstring `-86`-style, as an intended behaviour change with its reason, never a number nudged
to match output.

**Task 1 — the §0.4 RED, reproduced before the fix was designed.** Through the real
`build_ast_index` and the real detector, on the §0.4 fixture verbatim:

```
edges: [('compute', 7), ('Mock', 8), ('calculate', 10), ('assert_called_once_with', 11)]
SHIPPED : asserts=0 stmts=5 density=0   flagged=True  discarded=1 consumed=0 mock_ref=0  CORROBORATED=False
WIDENED : asserts=1 stmts=5 density=1/5 flagged=True  discarded=1 consumed=0 mock_ref=1  CORROBORATED=True
```

**RED-first proof at the seam, after the guard was written** (`-115`): `argus/detectors/vacuous_test.py`
was temporarily patched so the corroboration path read `_ASSERTION_CALLEES` — the one-table design
this story rejected — and the guard went **RED** with *"an ordinary mock-interaction test was
promoted to verdict-eligible"* (`vacuous_test_ast != vacuous_test_heuristic`). The patch was
reverted and `git diff` confirmed the file restored byte-for-byte. **The most important part of that
run: `tests/test_default_path_blocking_verdict.py` stayed 4/4 GREEN under the broken design.** So
nothing already in the suite — not `-30`, not `-116`, not `-117` — would have caught this. That is
the measured justification for AC6.3 existing as its own guard.

**AC2.2 — flags gained.** `0`. Nothing to name, argue or fix. (v1 — reusing the pre-existing line
scan — gains 2, both from a `;` in docstring prose; that is why `_scan_span` carries cross-line
string state, and `-114` pins the mechanism.)

**AC6.4 — `ast_corroborated` byte-identity.** Identical on **all 3,101** spans whose
`heuristically_vacuous` value is unchanged, and `corroborated` is 0/4,673 before and after. ⚠️
Stated with its limit, per §0.4: that is a measurement over an **empty denominator** and is
`UNEVALUABLE` as evidence, not a confirmation. The structural argument (DN-14-2-1 + `-115`) is what
carries AC6, not this figure.

### Completion Notes

**Every AC discharged, with the number rather than the claim.**

**AC1 — the denominator counts statements.** `_count_statements` now delegates to
`provenance_scan.body_statement_count`. A wrapped statement counts once, a `;`-compound once per
simple statement, a docstring once. It **REUSES** `logical_statement_starts` /
`_simple_statement_breaks` rather than forking a scanner: both are now projections of one
`_scan_span`, and the cross-line string state was added there, once (AC1.2). Measured against
CPython `ast` on my own baseline: **1.9071× → 1.0052×** over the 1,848 flagged minions tests
(29,093 → 15,334 against 15,255), **exact on 1,784/1,848 = 96.5%** of spans; 1.0032× over all 4,673.
AC1.3's dated correction is appended to `stories/1-5-…md` — struck text untouched, the 2026-08-17
amendment left standing and superseded rather than overwritten, `2.04×`/`1,812` corrected to
`1.907×`/`1,848` with the reason and with the note that the "14 of 31" attribution *does* reproduce.

**AC2 — nothing gains a flag.** `0` gained, `1,572` lost, both members at the unchanged pinned shas.
AC2.3's regression test is `-114`, asserted as an equivalence (same function ± the semicolon) plus
the opposite direction (a `;` in real code still separates statements), so it cannot pass by going
blind to semicolons.

**AC3 — thresholds and contract surface byte-unchanged.** Proven by diff, not inspection:
`git diff -U0 argus/detectors/vacuous_test.py | grep -E '^[-+].*(ASSERTION_DENSITY_FLOOR|MOCK_RATIO_CEILING) *='`
returns **nothing**. `VacuousTestScore` still frozen / `extra="forbid"` / same eleven fields, ratios
exact `Fraction` (`-119`). `RULE_AST`/`RULE_HEURISTIC` and the 1.6 eligibility surface unchanged.
Scorer still PURE and deterministic. **`argus/pipeline.py` is untouched** — absent from
`git status`.

**AC4 — flag rate, same population, as numbers.**

| | before | after |
|---|---|---|
| minions | 1,848 / 3,551 = **52.0%** | **660 / 3,551 = 18.6%** |
| agent-smith | 681 / 1,122 = **60.7%** | **297 / 1,122 = 26.5%** |

§0.3's prediction was **660 = 18.6%** and **297 = 26.5%**. No divergence.

**AC5 — the 31 adjudicated findings, re-scored by execution and attributed separately.**
31/31 resolve; spans where `assertion_sites` rises **13/31**; lifted by the **denominator alone
14/31**, by the **names alone 4/31**, by **both 23/31**, **still flagged 8/31**. §0.3's prediction
was 13 · 14 / 4 / 23 / 8. Exact, every cell. ⛔ **verdict-eligible 0/31** — unchanged, no escalation.

**AC6 — fact (b) does not move, and it is now BUILT.** `_CORROBORATION_ASSERTION_CALLEES` is a
second, independently-declared frozenset pinned at 14.1's 23 names, named for its purpose, carrying
the measured reason inline. Neither table is derived from the other (DN-14-2-4's rejected
alternative). `_sut_call_sites` and the `provenance_evidence` call both read it; only
`assertion_call_sites` reads the widened one. `-115` reproduces the mechanism in both directions and
goes red against the one-table build; `-116` pins the frozen set at exactly 23 names, asserts it is
a strict subset of the widened one, and asserts no cross-language name has reached either.
`provenance_scan`'s false docstring claim and `-102`'s comment are both corrected in this change,
each stating what DN-4 *actually* guarantees.

**AC7 — 14.3 can extend this.** Both sets stay flat `frozenset[str]`; the groupings are **comments**;
the naming convention is a separate named predicate (`is_assertion_callee` /
`_matches_assertion_convention`) with its collision cost and error direction recorded; **no**
`expect`/`toBe`/`assertEquals`/`Fatalf` anywhere, asserted by `-116`. The frozen table is named for
its purpose, so 14.3 inherits the moat by construction.

**AC8 — platform neutrality, discharged and bounded.** (1) Everything operates on the
`source.splitlines()` list; no new `$`-anchored pattern (the one regex I added is `\A…\Z`-anchored).
(2) No path or encoding assumption in changed code — the scan is pure string work; the new test
module uses `pathlib` and explicit `encoding="utf-8"` on every read and write. (3) The convention
predicate is `\A_?assert\w*\Z` — `\w` is a Unicode class on `str` patterns — and `-117` asserts
`assert_café_vide` / `assert_тесты_passed` match while `проверить` does not. (4) `-118` is the CRLF
regression for the **denominator specifically**, comparing the whole `VacuousTestScore` field by
field over a fixture containing both a docstring and a wrapped statement. (5) **No skip**:
`tests/test_vacuous_density.py` reports a named `UNEVALUABLE` **failure** rather than calling
`pytest.importorskip`, because `tree-sitter`/`tree-sitter-python` are BASE dependencies and
`audit-ci.yml` sets `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`; the suite reports **0 skipped**.

⚠️ **(6) WHAT I COULD NOT VERIFY LOCALLY — gates are LOCAL, and CI evidence is NOT ESTABLISHED.**
Every figure above was produced on **Windows 11 / CPython 3.11** only. Nothing was pushed and no
CI run exists for this change, so the ubuntu matrix is reasoned about and **not executed**.
Specifically unverified: (a) that `splitlines()` on a file checked out under a `core.autocrlf`
setting other than mine yields the identical list — `-118` proves the SCORER is indifferent given
both representations, which is not the same as proving the checkout produces them; (b) the
case-sensitive path behaviour of `is_test_file` on a case-sensitive filesystem, unchanged by this
story but on its blast radius; (c) the `nonascii_unicode` cartridge under a `C`/`POSIX` locale leg,
which is a CI-only leg here; (d) tree-sitter grammar wheels on linux/macOS, where a different build
could in principle emit a different edge set and move the counts; (e) Python versions other than
3.11 — the CPython `ast` ground truth in `-113` is version-dependent in principle, though no
statement-node change is known across the supported range. The mitigations are structural rather
than measured: no line terminator, path separator, locale or encoding is observed anywhere in the
changed code.

**AC9 — gates as numbers, with Δ.**

| Gate | §0.1 baseline | after | Δ |
|---|---|---|---|
| `pytest` (full) | 1611 passed / 0 failed / 0 skipped, exit 0 | **1619 passed / 0 failed / 0 skipped, exit 0** | **+8** (the new module), no new skip/xfail, no narrowed population |
| `mypy argus` | Success, 87 source files | **Success, 87 source files** | **0** |
| `bandit -r argus` | 19 Low / 0 Med / 0 High; confidence 0/0/6/13 | **19 Low / 0 Med / 0 High; confidence 0/0/6/13** | **0** |

Dogfood artifacts regenerated through their own renderers via `AI-E12-11`'s sequence (code commit
`26e6fb6` → `scripts/regenerate_dogfood_artifacts.py` → artifact commit `a9cf25d`); the provenance
sha the three artifacts cite is `26e6fb6`, confirmed an ancestor of `HEAD`. Nothing hand-edited, no
assertion loosened. `git tag -l` is empty; nothing pushed. One item deferred with a named owner
(`DF-14-2-A`, owner: Story 14.3 dev).

**Decisions, each with its rejected alternative.** All four of the story's decisions were
implemented as specified and none was re-litigated. DN-14-2-1 (frozen corroboration vocabulary) was
additionally *re-derived* rather than accepted: the RED was reproduced before the design was
written, and the one-table alternative was measured to leave the entire existing suite green — which
is the strongest available argument that a corpus-based guard would have proved nothing.

**Two divergences recorded rather than smoothed.** (1) My CPython ground truth for agent-smith is
6,608 against §0's 6,600 — 8 statements, 0.12%, confined to that member, moving the ratio by 0.0004
and no decision. (2) §0.5's `-109`/`-110` prediction did not hold, and the two guards that did move
moved for a reason §0.5 did not consider; both are written up above as wrong predictions rather than
quietly absorbed.

**Not done, deliberately.** `deferred-work.md` and `stories/1-5-…md` are **appended to but NOT
committed** — both were already dirty with other people's work before this story began (§0.8), and
committing either would carry that work in. Same treatment for this story file and
`sprint-status.yaml`. The staged delta was verified to be exactly four files before committing.

### Review iteration 2 (Sonnet, 2026-08-18) — independent re-derivation, fix round only

**Scope: the fix round only** (`2eeaace` code, `e2e278c` dogfood artifacts, against `a9cf25d`).
Iteration 1's own re-derivation stands and was not repeated; this pass verified the fix round
by fresh execution, using a harness written from scratch (not the dev's script, not
iteration 1's script).

**CPython grounding, independently re-derived.** `ast.walk` over minimal repros for every one
of the five cases named in the fix confirms exactly what the fix's docstrings claim:
`ast.ExceptHandler` and `ast.match_case` are not `ast.stmt` subclasses (`issubclass(...,
ast.stmt) == False` for both); `try/except/else/finally` is ONE `ast.Try` regardless of clause
count; `if/else` is one `ast.If`; `if/elif` produces a NESTED `ast.If` (two `stmt` nodes) —
confirming `elif` is correctly excluded from the exclusion; a decorated `FunctionDef` carries
exactly one `stmt` node regardless of the decorator, with or without arguments.

**DN-14-2-5 verified on all three of its claims.** (a) `git diff a9cf25d..e2e278c --
argus/detectors/provenance_scan.py` shows `_scan_span`, `_statement_texts` and
`logical_statement_starts` **outside every changed hunk** — the exclusion is applied solely in
the new `_counted_statement_texts`, consumed only by `logical_statement_count` /
`body_statement_count`. (b) Confirmed byte-identical by direct call: `logical_statement_starts`
on `-122`'s own fixture returns the exact map the guard asserts, `{1:1,2:2,3:3,4:3,5:3,6:6,
7:7,8:8,9:9,10:10}`. (c) Built a deliberately WRONG alternative `_scan_span` that applies the
same exclusion inside the scan (never opens a new statement on a clause-header line) and ran
it over `-122`'s fixture: the resulting map is `{...,6:3,...,8:7,...}` — line 6 (`except
ValueError:`) and line 8 (`else:`) get mis-attributed to the preceding statement — which
diverges from `-122`'s expected map and would fail it. `-122` does catch the regression it is
built to catch.

**RED-first, independently reproduced against the actual shipped `a9cf25d` code** (via a
disposable, safely-named worktree — not named after any project). Every row of `-121` and
`-122` reproduced exactly as claimed: `try/except/else/finally` **8 vs 5**; `if/else`,
`for/else`, `while/else`, wrapped-except-header **5 vs 4** each; `match/case` **6 vs 4**;
decorator and wrapped-decorator **5 vs 4** each; the four negative controls (`elif`, inline
clause body, `case` as a name, `a @ b`) already green pre-fix. `-122`'s fixture: **7 vs 5**
RED on the count while `logical_statement_starts` already matched its expected map — exactly
"RED in the count only," as claimed.

**The structural GAINED=0 argument, adjudicated: it holds.** `_counted_statement_texts` is a
pure filter over `_statement_texts` (`opens: text for ... if not
_is_continuation_clause_header(text) and not _is_decorator(text)`) — strictly a subset, so the
denominator cannot increase. `mock_ratio = Fraction(mock_sites, call_sites) if call_sites else
Fraction(0)` (`vacuous_test.py`) — never reads the statement count at all, so the mock-ratio
arm of `heuristically_vacuous` is provably unaffected by this change, not merely unaffected in
the corpus measured. `heuristically_vacuous` fires on `assertion_density < FLOOR`; a
non-increasing denominator with an unchanged numerator (this pass does not touch the assertion
vocabulary) can only raise or hold density, never lower it. The measurement is not required to
carry this argument; it independently would hold even over an unmeasured corpus.

**Corpus-wide re-derivation, from a fresh harness (own line-matched ground truth, not the
dev's script, not `-113`'s cited numbers).** Both pinned trees staged via `git archive` into
disposable directories, indexed through the SHIPPED `build_ast_index`, scored through the
SHIPPED `body_statement_count`, ground truth from `ast.walk` matched by **name AND line
number** (the corpus contains files with several same-named test methods across different
`unittest.TestCase` subclasses — e.g.
`tests/security/test_a2a_missing_token_audits.py` defines
`test_missing_token_returns_401_and_writes_audit` **eleven times** across eleven classes — and
matching by name alone silently mismatches ten of them against the wrong function's ground
truth; this was caught and fixed in my own harness before trusting its output). Result, over
**all** 4,673 pinned test functions (a superset of the "flagged" populations §0/AC1 cite):
**minions 3,551/3,551 exact (100%)**; **agent-smith 1,121/1,122 exact**, the sole residual
being `agentsmith-core/tests/test_compiler.py::test_structural_conformance_set_verification`
(scan 33 vs CPython 35, an UNDER-count — the safe direction); **corpus-wide: n=4,673,
exact=4,672, over=0, under=1.** This reproduces the story's headline claim — "4,672/4,673
exact, 0 over-counts, 1 under-count" — **exactly**, digit for digit, via a completely
independent methodology.

**Gates, independently re-run.** `pytest` (full suite, via JUnit XML, not a dot-count):
`tests="1621" errors="0" failures="0" skipped="0"`, exit 0. `mypy argus`: `Success: no issues
found in 87 source files`. `bandit -r argus`: `19 Low / 0 Medium / 0 High`, confidence
`0/0/6/13`. All match the Dev Agent Record exactly. (⚠️ Iteration 1's spurious `after`-worktree
failure was avoided this pass by never naming a worktree or temp directory anything that could
leak into audited output.)

**Adversarial hunting against the new predicate, end to end through the real detector.** Fifteen
hand-built shapes not in the fixture set — `except*` with a tuple and `as`, a wrapped
`except (...) as e:`, `else` inside a conditional expression, a class pattern and a guarded
`case`, `case` as a dict-key identifier, a string literal containing `"except: ..."`, a comment
containing `# case: ...`, a decorator with an f-string argument containing a colon, an
annotation-only `case: int` with no value, CRLF line endings around a clause header, and a
non-ASCII identifier around an `except` block — every one matched CPython ground truth exactly
through `body_statement_count`. No defect found in the predicate itself.

**Finding 1 (residual direction): CLOSED, confirmed by independent re-derivation.** Finding 2 is
CLOSED **as a review item only, and that is explicitly not a ledger closure** — the entry
`DF-14-2-B` remains **OPEN and deferred**, which is its correct disposition.
⚠️ *Wording corrected 2026-08-18 by dev pass 3: this sentence originally put the ledger id and a
closure verb on one line, which reads to `TC-ArgusAgent-DOCS-001-78` as a claim the ledger never
received — the trap this story's own "previous story intelligence" names. It tripped that guard on
disk. Only the wording moved; the verification underneath is unchanged and stands.*
`_ASSIGNMENT_RE` is byte-identical to `966ceba`
(`git diff 966ceba..e2e278c -- argus/detectors/provenance_scan.py | grep _ASSIGNMENT_RE` is
empty) and the ledger entry (`deferred-work.md:4824-4831`) is well-formed with a named owner.
`argus/pipeline.py` and `tests/test_vacuous_detector.py` are both absent from the fix round's
diff, confirming the claimed scope exactly.

**One new finding, Low.**

- [x] [Review][Patch] The Dev Agent Record's own module-size numbers (AC9 table and File List,
  "this pass") do not match the files as committed — a factual-accuracy miss in a story whose
  stated method is "measured, not asserted"
  [`_bmad-output/design-artifacts/ArgusAgent/stories/14-2-...md` — the "AC9 — gates as numbers,
  this pass" table and the review-iteration-1 File List entries]. Claimed: `provenance_scan.py`
  903, `vacuous_test.py` 919, `test_vacuous_density.py` 1,053, `test_vacuous_detector.py` 1,128.
  Measured (`len(Path(p).read_text().splitlines())`, the same method
  `test_module_size_ceiling.py` uses, against `git show 2eeaace:<path>` and confirmed identical
  at current `HEAD`): `provenance_scan.py` **926** (+23), `vacuous_test.py` **929** (+10 — the
  claimed "919" is in fact this file's line count **before** this pass's own docstring edit, at
  `a9cf25d`, carried forward unchanged rather than re-measured), `test_vacuous_density.py`
  **1,060** (+7), `test_vacuous_detector.py` **1,128** (exact — this file is genuinely untouched
  this pass). Every file is still comfortably under the 1,200 ceiling either way, no exemption
  is implicated, and `test_module_size_ceiling.py` itself is green and independent of this
  prose — so this changes no conclusion. It is reported at Low severity, on the ADVISORY
  (documentation) path only, precisely because the project's own convention (§0.2's
  `DF-8-5-C` class, the 2.04×/1.907× correction this very story made to a different document)
  is to record a measured divergence rather than let a stale number stand once caught. Suggested
  fix: re-run `len(Path(p).read_text(encoding="utf-8").splitlines())` over the four files at
  current `HEAD` and correct the AC9 table and File List entries to match.

### Review-iteration-1 addendum to the Completion Notes (dev pass 2, 2026-08-18)

**AC1 / AC1.4 — the numbers above supersede the pass-1 figures.** `1.9071× → 1.0000×` over the
1,848 flagged minions tests, exact on **1,848/1,848**; `0.9997×` on agent-smith, exact on 680/681;
**4,672 of 4,673 spans exact corpus-wide, 0 over-counts**. AC1.3's dated correction in
`stories/1-5-…md` cites `1.907×` as the LINE-count inflation, which is unchanged and still correct —
it is a statement about the denominator that was REPLACED, not about the replacement — so that
file was not re-opened.

**AC2 — flags GAINED remain `0`**, now against two baselines: `966ceba` (the shipped line count)
and `a9cf25d` (this story's first pass). Nothing to name, argue or fix. Lost rises 1,572 → **1,581**.

**AC5 — the 31 adjudicated locators did not move**: 31/31 resolve, 13 gain assertion sites,
attribution **14 / 4 / 23 / 8**, ⛔ **verdict-eligible 0/31**. No escalation.

**AC6 — fact (b) did not move, and this pass had to build that too.** The clause/decorator rules
are applied at the count and not in `_scan_span`, so `logical_statement_starts` is byte-identical;
`-122` pins the whole boundary map. `ast_corroborated` identical on all 4,664 unchanged-heuristic
spans, corroborated 0/4,673 before and after — stated again with its limit: an empty denominator is
`UNEVALUABLE` as evidence. `-115`, `-116`, `-30`'s two arms, `VERDICT-001-116`/`-117` and
`-87`/`-88`/`-109`/`-110`/`-111`/`-112` are all green.

**AC8 — platform neutrality, re-discharged for the NEW code.** The two predicates are pure string
work over the existing `splitlines()` list: no terminator, path, locale or encoding is observed.
`_CONTINUATION_CLAUSE_RE` is anchored `\A…\Z` and **never** `^…$` — deliberately, since `DF-14-2-B`
is open against exactly that mistake next door. `\w`/`[^\W\d]` are Unicode classes on `str`
patterns, so a Cyrillic or accented name is unaffected; the predicates key on Python keywords and
`@`, neither of which is locale-dependent. **No skip added; the suite reports 0 skipped.**

⚠️ **What I could NOT verify locally, this pass — gates are LOCAL and CI evidence is NOT
ESTABLISHED.** Windows 11 / CPython 3.11 only; nothing pushed, so the ubuntu matrix is reasoned
about and not executed. Specifically unverified: (a) the ubuntu/macOS legs at all, including the
`C`/`POSIX` locale leg for the `nonascii_unicode` cartridge; (b) **CPython 3.10 and 3.12**, which
the matrix runs and I did not — relevant here because the ground truth in `-113`/`-121`/`-122` is
CPython's own `ast`, and `match`/`case` requires 3.10+. No `ast.stmt` classification change is known
for `Try`/`If`/`Match`/`ExceptHandler`/`match_case` across 3.10–3.12, and the detector's own
predicates are text-only and version-independent, but the ground-truth side of those assertions is
the part a version change could in principle move; (c) tree-sitter grammar wheels on linux/macOS,
where a different build could emit a different edge set; (d) `core.autocrlf` checkout behaviour, as
before. The mitigations are structural rather than measured.

**AC9 — gates as numbers, this pass.** Full suite **1621 passed / 0 failed / 0 skipped / 0 errors**
(Δ **+2** vs pass 1's 1619, Δ **+10** vs §0.1's 1611 — the two new guards, no new skip/xfail, no
narrowed population). `mypy argus` **Success: no issues found in 87 source files** (Δ 0). `bandit -r
argus` **19 Low / 0 Medium / 0 High**, confidence **0/0/6/13** (Δ 0). Thresholds byte-identical by
`git diff -U0 … | grep`, empty. `argus/pipeline.py` absent from the diff. Module sizes
**926 / 929 / 1,060 / 1,128**, all ≤ 1,200; `test_module_size_ceiling.py` **not touched** and no
exemption added. ⚠️ **Corrected 2026-08-18 (dev pass 3) — these four figures were first written as
903 / 919 / 1,053 / 1,128, three of them wrong. See the correction addendum below; the numbers
above are the re-measured ones and the ceiling conclusion is unchanged.** Dogfood artifacts regenerated through their own renderers via `AI-E12-11`
(`2eeaace` → `e2e278c`), provenance sha `2eeaace`, an ancestor of `HEAD`; the two currency guards
fired before regeneration and are green after. Nothing hand-edited, no assertion loosened.
`git tag -l` empty; nothing pushed.

**Decision taken this pass, with its rejected alternative.**

- **DN-14-2-5 — a bare continuation-clause header and a decorator are excluded from the density
  denominator, and the exclusion lives at the COUNT rather than in `_scan_span`.** *Rejected
  alternative 1:* the reviewer's option (b), correcting only the docstring to describe both
  mechanisms. Rejected because option (a) proved clean and strictly better — it makes the claim true
  instead of accurately pessimistic, raises exactness from 96.5% to 100.0% on the minions
  population, and gains **0** flags. *Rejected alternative 2:* implementing it inside `_scan_span`
  by not opening a statement on those lines, which is where the reviewer's wording pointed. Rejected
  on **risk, and it is the load-bearing choice here**: `_scan_span` also produces
  `logical_statement_starts`, fact (b)'s boundary map, so that spelling would have moved the
  corroboration path as a side effect of a density fix — the exact coupling `-115` exists to
  prevent. Applying it at the count leaves fact (b) byte-identical, and `-122` proves it rather than
  claiming it.

### Review-iteration-2 correction (dev pass 3, 2026-08-18) — the record's own numbers, re-measured

**Documentation only. No file under `argus/` or `tests/` was opened, no test was added or changed,
nothing was committed.** Baseline `HEAD` = `e2e278c`, unchanged by this pass.

**The finding, restated as what it actually is.** Review iteration 2 confirmed the substance of this
story by independent re-derivation and left exactly one item open: the Dev Agent Record's own
module-size figures were carried forward from an earlier commit instead of re-measured, and three of
the four were therefore wrong. That is `DF-8-5-C`'s class — the very class §0.2 exists to police, and
the class this story's own AC1.3 correction to `stories/1-5-…md` was written to close in someone
else's document. **Applied here to this document.** The finding was reproduced before it was
accepted: each figure was re-measured with the reviewer's own expression rather than read from the
reviewer's table.

**Re-measured**, `len(Path(p).read_text(encoding="utf-8").splitlines())` — byte-for-byte the method
`test_module_size_ceiling.py` itself uses — at `HEAD` = `e2e278c`, then cross-checked at every
commit this story produced via `git show <sha>:<path>`:

| file | `966ceba` | `26e6fb6`/`a9cf25d` (pass 1) | `2eeaace`/`e2e278c` (fix pass) | **claimed "this pass"** | **TRUE** | ceiling |
|---|---|---|---|---|---|---|
| `argus/detectors/provenance_scan.py` | 610 | 815 | **926** | 903 | **926** (+23) | ≤1,200 ✅ |
| `argus/detectors/vacuous_test.py` | 697 | 919 | **929** | 919 | **929** (+10) | ≤1,200 ✅ |
| `tests/test_vacuous_density.py` | — | 814 | **1,060** | 1,053 | **1,060** (+7) | ≤1,200 ✅ |
| `tests/test_vacuous_detector.py` | 1,084 | 1,128 | **1,128** | 1,128 | **1,128** (exact) | ≤1,200 ✅ |
| `argus/pipeline.py` | 1,111 | 1,111 | **1,111** | — | **1,111** unchanged | ≤1,200 ✅ |

**The mechanism of the error, named rather than rounded off.** The `919` was not a mistyped
measurement; it was `vacuous_test.py`'s count **before** the fix pass's own docstring edit, at
`a9cf25d`, transcribed forward as though it were a post-pass number. The other two moved for the
same reason — the fix-pass table was assembled from the pass-1 table rather than from the files. The
one figure that was right, `1,128`, was right by accident of the file genuinely not being touched.
**Every "919" now carries its baseline explicitly**, and the fix-pass File List entries read
`815 → 926`, `919 → 929`, `814 → 1,060` so no reader can take a pre-pass count for a post-pass one.

**Sweep for the same defect class elsewhere in the record** (this is the actual finding; the four
line counts are only where it surfaced). Every figure in the permitted sections that is stated as
measured and is cheaply re-derivable was re-derived:

| Claim | Where | Re-measured | |
|---|---|---|---|
| module sizes, fix pass | AC9 "this pass", File List | 926 / 929 / 1,060 / 1,128 | ❌ **3 of 4 wrong — corrected above** |
| module sizes, pass 1 (`697 → 919`, `610 → 815`, `814` new, `1,084 → 1,128`) | File List, pass 1 | all four exact at `26e6fb6`/`a9cf25d` | ✅ correct for their baseline; now annotated with it |
| `deferred-work.md` "269 insertions, 0 deletions across the whole working diff" | File List | `git diff --numstat` → **287 / 0** | ❌ **stale — corrected.** Append-only (0 deletions) holds |
| `argus/pipeline.py` untouched, 1,111 lines | AC3.5, AC9 | 1,111 at all five commits and on disk; absent from `git diff --stat 966ceba..e2e278c` | ✅ |
| thresholds byte-identical | AC3.1 | `git diff -U0 966ceba..e2e278c -- vacuous_test.py \| grep -E '(ASSERTION_DENSITY_FLOOR\|MOCK_RATIO_CEILING) *='` → **empty** | ✅ |
| dogfood provenance sha `2eeaace`, ancestor of `HEAD` | AC9.2 | `minions-dogfood-proof.md:13` cites `2eeaace06a3…`; `git merge-base --is-ancestor 2eeaace HEAD` → true | ✅ |
| `git tag -l` empty | AC9.4 | empty | ✅ |
| finding 2's disposition sentence, which named the ledger id beside a closure verb | review-iteration-2 prose, this file | the ledger carries **no** closure for `DF-14-2-B`, and correctly so — it is deferred and OPEN | ❌ **a closure claimed in prose the ledger never received — corrected in the prose, NOT in the ledger** |
| `pytest` 1621 / 0 / 0 / 0 | AC9 "this pass" | re-run this pass: **1621 passed, 0 failed, 0 skipped, exit 0** | ✅ after the correction above; ⚠️ **1 failed before it** |
| `mypy` Success-87 · `bandit` 19L/0M/0H | AC9 "this pass" | not re-run this pass; independently re-run and confirmed exact by review iteration 2 against the same `e2e278c` | ✅ corroborated |
| corpus figures (1,581 lost / 0 gained · 4,672-of-4,673 exact · 14/4/23/8 · 0/31 verdict-eligible · `ast_corroborated` on 4,664 spans) | AC2/4/5/6 | **not re-run** — out of this pass's scope by instruction; all independently reproduced digit-for-digit by review iteration 2's from-scratch harness | ✅ corroborated |

**No ceiling implication, and it is confirmed rather than assumed.** All four files remain under
NFR-M1's 1,200 (largest headroom consumed: `test_vacuous_detector.py` at 1,128, 72 lines spare).
`tests/test_module_size_ceiling.py` is green in this pass's full run and its own diff is unrelated to
this story (§0.8). No exemption exists or was added; the registry did not move.

**No currency-guard implication, and that is confirmed rather than assumed.** `git status --porcelain
-- argus/` is **empty** at `e2e278c` — this pass changed no `argus/` line, so the dogfood artifacts'
inputs cannot have moved and `test_dogfood_artifact_currency.py` cannot fire. It is green in the full
run below. `scripts/regenerate_dogfood_artifacts.py` was **not** run, correctly: re-rendering with no
input change would rewrite a provenance sha for nothing.

**⛔ The sweep found a second live defect, and this one was RED on disk — a guard working, exactly as
this story's own "previous story intelligence" warns.** The first full-suite run of this pass came
back **1620 passed / 1 FAILED**:
`TC-ArgusAgent-DOCS-001-78` (`test_governance_record_integrity.py`) — *"a story record claims a
ledger closure that `deferred-work.md` never received."* The claimant was **this file**: review
iteration 2's own prose wrote a ledger id on the same line as a closure verb, which
`story_closure_claims` reads — deliberately, line-scoped — as a claim that the ENTRY was closed. It
was not, and must not be: the entry in question is **deferred and OPEN**, with a named owner, which
both prior passes verified.

**This is the same defect class as the finding I was sent to fix** — the record asserting something
that is not true of the world — arriving through a different door, and it is the exact trap this
story's *"never put a `DF-*` id on the same line as `CLOSED`"* note names. It is also why iteration
2's own gate report (`1621 / 0 / 0 / 0`) did not catch it: **those gates were run before the review's
findings were written into this file**, so the red was created by the hand-off prose itself and
nothing re-ran afterwards. That is `AI-E13-1` in miniature.

**Fixed in the PROSE, deliberately not in the ledger.** The honest repair is to stop the record
claiming a closure it never made — the sentence now says *closed as a review item, explicitly not a
ledger closure, the entry remains OPEN* — and it is annotated with what was changed and why.
`deferred-work.md` was **not** opened: appending a closure to make a guard green would be `AI-E12-3`'s
defect (closing an entry in prose rather than against evidence) committed inside the guard written to
stop it, and that entry is genuinely unfixed.

⚠️ **My own correction re-tripped the guard twice before it held, and that is recorded rather than
tidied away.** Attempt 1 quoted the offending sentence verbatim, which reproduced the exact pattern
inside the annotation explaining it. Attempt 2 fixed the quote but then *described* the defect in
three new places — a sweep-table row, the paragraph above, and the Change Log — each of which named
the ledger id beside the word it must not sit next to. The rule is narrower than it reads: it is not
enough for the surrounding prose to be true, because the analyzer is **line-scoped by design** and
cannot see the sentence's meaning. The stable spelling is to never put the id and a closure verb on
one line at all — so the id is now named only on lines that say it is **OPEN**, and every line that
carries a closure verb refers to it obliquely. **This is a small, real lesson about writing in a
repository that machine-checks its own records, and it belongs to Story 14.3's dev as much as to
me.**

**Gate re-run after the last prose edit** (`AI-E13-1`'s lesson, honoured a third time): full suite
**1621 passed / 0 failed / 0 skipped / 0 errors, exit 0** — Δ **0** against the fix pass, which is the
expected result for a change that touches no executable line. ⚠️ **LOCAL only; CI evidence is NOT
ESTABLISHED** — Windows 11 / CPython 3.11, nothing pushed, the ubuntu matrix and the 3.10/3.12 legs
reasoned about and not executed, exactly as the two prior passes recorded.

**What this correction deliberately did NOT do.** It changed no code, added no test, moved no
threshold, re-ran no corpus measurement, regenerated no artifact, re-opened no closed finding, and
touched none of §0.8's files. The story's substance — confirmed correct by two independent review
passes — is byte-unchanged; only the record's own arithmetic about itself was repaired.

### Review iteration 3 (Sonnet, 2026-08-18) — narrow confirmation pass, VERDICT pass

**Scope, by instruction: confirm dev pass 3's documentation-accuracy correction is closed, and
nothing else.** `HEAD` = `e2e278c`, unchanged since iteration 2 — `git diff e2e278c -- argus/` is
**empty**; `git diff e2e278c -- tests/` shows only the four files already catalogued in §0.8 as
pre-existing unrelated dirty work (`test_evidence_citation.py`, `test_module_size_ceiling.py`,
`test_spec_claim_scope.py`, `test_v1_commitment_closure.py`), plus the untracked, also-pre-existing
`tests/test_status_document_registry.py`. Iteration 1 and 2's own substance re-derivations are not
repeated; this pass only re-checks what dev pass 3 changed.

**The four module-size figures, independently re-measured** with
`len(Path(p).read_text(encoding="utf-8").splitlines())` (the ceiling test's own method), at
current `HEAD`: `argus/detectors/provenance_scan.py` **926**, `argus/detectors/vacuous_test.py`
**929**, `tests/test_vacuous_density.py` **1,060**, `tests/test_vacuous_detector.py` **1,128** —
all four match the AC9 table and File List as corrected by dev pass 3, exactly. Every surviving
`919` in the record (File List, "Committed by this story's first pass") is explicitly annotated as
the count *before* the fix pass's own docstring edit, at `a9cf25d`, and is nowhere presented as a
current or post-fix-pass number. Confirmed correct.

**The sweep's two further findings, both re-verified.** (1) `deferred-work.md`'s working diff:
`git diff --numstat -- deferred-work.md` → **287 0**, matching the corrected claim exactly; the
load-bearing `0` deletions (append-only) holds. (2) `DF-14-2-B`: the ledger entry
(`deferred-work.md:4824-4831`) is well-formed — `id`, `origin_story`, a **named owner** ("next dev
to open `argus/detectors/provenance_scan.py`, naturally Story 14.3's"), `target_story`, `category`,
`severity` — and carries **no** closure disposition; it is genuinely `OPEN`. **Adjudicating dev pass
3's reasoning: it is sound.** Appending a closure to `deferred-work.md` for a defect that was, by
the dev's own account, deliberately left unfixed (the `$`-anchored `_ASSIGNMENT_RE`, byte-identical
since `966ceba`) would itself be a false closure — exactly `AI-E12-3`'s defect, committed *inside*
the governance guard (`TC-ArgusAgent-DOCS-001-78`) built to catch that defect class. Declining to
"fix the guard by lying to the ledger" and instead correcting only the prose that falsely implied a
closure is the correct call, not a corner cut. Independently confirmed no `DF-14-2-B` occurrence in
this file now sits on a line matching `story_closure_claims`' closure-verb pattern
(`CLOSED`/`Closes`/`closes`/`Closed by this story`/`closed by this story`, case-sensitive,
line-scoped) — every line naming the id says `OPEN`, `deferred`, or similar, and every line
carrying a closure verb (e.g. "Finding 2 is CLOSED **as a review item only**") refers to the id
obliquely rather than on the same line. The story now describes `DF-14-2-B`'s status truthfully.

**Nothing else moved.** `git status --porcelain -- argus/` is empty. No test was added or altered
by dev pass 3 (`tests/test_vacuous_detector.py` and `tests/test_vacuous_density.py` are absent from
`git diff e2e278c -- tests/`). No dogfood artifact was regenerated (correctly — `argus/`'s inputs
did not move). Nothing was committed. `sprint-status.yaml` was checked before this review's own
edit: only the `14-2` key and `last_updated` differed from committed `HEAD`, with every comment and
the `STATUS DEFINITIONS` block intact.

**The process hazard this round was warned about, handled.** Iteration 2's own hand-off prose put
`DF-14-2-B` on the same line as a closure verb and tripped `TC-ArgusAgent-DOCS-001-78`; dev pass 3
fixed the wording (not the ledger). After writing this iteration's findings into this file, the
full suite was re-run: **1621 passed, 0 failed, 0 skipped, exit 0** (JUnit XML confirms
`tests="1621" errors="0" failures="0" skipped="0"`) — exact match to baseline, and
`tests/test_governance_record_integrity.py`'s 3 tests (including `DOCS-001-78`) are green.

**Verdict: PASS.** The figures are correct, `DF-14-2-B`'s disposition is honest and its non-closure
is the right call, the tree is green after this review's own write, and no new finding is warranted
— manufacturing one to justify a further round would itself be the `AI-E3-1`/`DF-8-5-C` class this
story exists to police. Status `review` → `done`.

### File List

**Committed by review iteration 1's fix pass** (`2eeaace`, then `e2e278c`):

- `argus/detectors/provenance_scan.py` — MODIFIED. `_CONTINUATION_CLAUSE_RE`,
  `_is_continuation_clause_header`, `_is_decorator`, `_counted_statement_texts`;
  `logical_statement_count` / `body_statement_count` routed through it;
  `logical_statement_count`'s residual-direction paragraph corrected. `_scan_span` and
  `logical_statement_starts` **unchanged**. 815 → **926** lines.
- `argus/detectors/vacuous_test.py` — MODIFIED. `_count_statements`'s docstring only: the corrected
  ratio and the corrected residual direction. No behavioural change in this file. 919 → **929** lines
  (the docstring correction is +10; `919` is the PRE-pass count at `a9cf25d`).
- `tests/test_vacuous_density.py` — MODIFIED. New `TC-ArgusAgent-DETECT-001-121` (nine ground-truth
  rows: six clause/decorator shapes, four negative controls) and `-122` (fact (b)'s boundary map
  unmoved); `-113`'s stale ratio updated; module docstring extended to `-122`. 814 → **1,060** lines.
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md` — REGENERATED.
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md` — REGENERATED.
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md` — REGENERATED.

**Committed by this story's first pass** (`26e6fb6`, then `a9cf25d`):

- `argus/detectors/vacuous_test.py` — MODIFIED. Two assertion vocabularies (widened
  `_ASSERTION_CALLEES`, frozen `_CORROBORATION_ASSERTION_CALLEES`), the
  `_ASSERTION_NAMING_CONVENTION` predicate + `is_assertion_callee`, `_count_statements` re-authored
  over `body_statement_count`, `_sut_call_sites` and the `provenance_evidence` call routed to the
  frozen table, module docstring updated. 697 → 919 lines (ceiling 1,200). ⚠️ **`919` is this pass's
  figure, measured at `26e6fb6`/`a9cf25d` and re-confirmed correct there; the fix pass took it to
  929. Do not read it as a current count.**
- `argus/detectors/provenance_scan.py` — MODIFIED. `_consume_string` / `_continued_code_prefix`
  (cross-line string state), `_scan_span` + `_SpanLine` (the one scan), `logical_statement_count`,
  `body_statement_count`, `_statement_texts`, `_simple_statement_segments`;
  `logical_statement_starts` reduced to a projection; the false docstring claim corrected.
  610 → 815 lines.
- `tests/test_vacuous_density.py` — **NEW**, 814 lines. `TC-ArgusAgent-DETECT-001-113`..`-120`.
- `tests/test_vacuous_detector.py` — MODIFIED. `-101`/`-102` fixtures strengthened with their
  reason, `-102`'s comment corrected (AC6.6), `-112` routed to the frozen vocabulary.
  1,084 → 1,128 lines.
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md` — REGENERATED.
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md` — REGENERATED.
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md` — REGENERATED.

**Written but deliberately NOT committed** (each was already dirty with unrelated work — §0.8):

- `_bmad-output/design-artifacts/ArgusAgent/stories/1-5-…md` — one dated 2026-08-18 correction
  appended to the existing amendment (AC1.3). Nothing else in the file touched.
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — APPEND ONLY (**287** insertions,
  **0** deletions across the whole working diff, re-measured at `e2e278c`), one entry `DF-14-2-A`
  with a named owner. ⚠️ **Corrected 2026-08-18 (dev pass 3): this read `269` insertions, a figure
  that was true when pass 1 wrote it and was carried forward unre-measured afterwards. The
  load-bearing half — `0` deletions, i.e. genuinely append-only — is re-measured and holds.**
- `_bmad-output/design-artifacts/ArgusAgent/stories/14-2-…md` — this file.
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — the `14-2` key and
  `last_updated` only.

⚠️ **Unchanged by the fix pass, deliberately:** `stories/1-5-…md` (its correction cites the LINE
count's `1.907×`, which this pass does not move), `deferred-work.md` (`DF-14-2-B` verified
well-formed and left byte-identical; `DF-14-2-A` untouched), and every file on §0.8's list.

**Touched by dev pass 3 (the review-iteration-2 correction) — two files, neither committed:**

- `_bmad-output/design-artifacts/ArgusAgent/stories/14-2-…md` — this file. Dev Agent Record
  correction addendum, the AC9 "this pass" module-size figures, four File List figures, Change Log,
  Status.
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — the `14-2` key and `last_updated`
  only.

⚠️ **Unchanged by dev pass 3:** every file under `argus/` and `tests/` (`git status --porcelain --
argus/` is empty; `tests/`'s four modified files and one untracked file are §0.8's pre-existing
work, none of it this story's), all three dogfood artifacts, `deferred-work.md`, `stories/1-5-…md`,
and every other file on §0.8's list.

---

## Change Log

| Date | Change |
|---|---|
| 2026-08-18 | **Review iteration 3 — PASS.** Narrow, by instruction: confirmed dev pass 3's documentation-accuracy correction only. `HEAD` = `e2e278c`, unchanged since iteration 2 (`git diff e2e278c -- argus/` empty; `tests/`'s diff is exactly §0.8's pre-existing unrelated dirty work). Independently re-measured all four module sizes with the ceiling test's own method: `provenance_scan.py` **926**, `vacuous_test.py` **929**, `test_vacuous_density.py` **1,060**, `test_vacuous_detector.py` **1,128** — exact match to the corrected AC9/File-List figures; every surviving `919` confirmed explicitly labelled as the pre-fix-pass baseline at `a9cf25d`, never presented as current. `deferred-work.md`'s working diff re-measured at **287 / 0** (`git diff --numstat`), matching the correction; append-only holds. `DF-14-2-B` confirmed genuinely **OPEN** in the ledger with a named owner; **adjudicated the dev's non-closure as correct** — appending a closure to green `TC-ArgusAgent-DOCS-001-78` over a defect left deliberately unfixed would itself be `AI-E12-3`'s defect, committed inside the guard built to stop it. Confirmed no `DF-14-2-B` occurrence now sits on a line matching the closure-verb pattern. Full suite independently re-run **after** this review's own findings were written into this file (the exact hazard iteration 2's own prose tripped): **1621 passed, 0 failed, 0 skipped, exit 0**, `test_governance_record_integrity.py` green including `DOCS-001-78`. Nothing else moved — no `argus/`/`tests/` file opened by this review, nothing committed, `sprint-status.yaml`'s only changes are the `14-2` key and `last_updated`, all comments and `STATUS DEFINITIONS` preserved. Status `review` → `done`. |
| 2026-08-18 | **Review iteration 2 addressed — 1 of 1 finding closed. Documentation only; no code, no test, no artifact, nothing committed.** *Reason for the correction, stated because this is a correction to the record and not a silent edit:* the Dev Agent Record's own module-size figures were carried forward from an earlier commit rather than re-measured, which is exactly the `DF-8-5-C` defect class this story polices in §0.2 and corrected in someone else's document at AC1.3 — so it is corrected here, in this one, by the same rule. Each figure was **re-derived first** with `len(Path(p).read_text(encoding="utf-8").splitlines())` (the method `test_module_size_ceiling.py` itself uses) at `HEAD` = `e2e278c` and cross-checked at every commit this story produced, rather than copied from the reviewer's table. Corrected: `provenance_scan.py` 903 → **926**, `vacuous_test.py` 919 → **929**, `test_vacuous_density.py` 1,053 → **1,060**; `test_vacuous_detector.py` **1,128** confirmed already exact. The `919` is identified as `vacuous_test.py`'s **pre**-fix-pass count at `a9cf25d` transcribed forward as a post-pass number, and every remaining `919` in the record now carries its baseline explicitly. **Sweep of the same defect class across the whole record** (the finding's real subject) found **two further live defects**, one of them RED on disk. (i) `deferred-work.md`'s working diff, claimed `269` insertions, re-measured **287**, with the load-bearing `0` deletions (append-only) confirmed to hold. (ii) ⛔ **The first full-suite run of this pass came back 1620 passed / 1 FAILED** — `TC-ArgusAgent-DOCS-001-78`, *"a story record claims a ledger closure that `deferred-work.md` never received"* — and the claimant was **this file**: review iteration 2's own hand-off prose put a ledger id on the same line as a closure verb, which the line-scoped `story_closure_claims` analyzer reads as a claim the ENTRY was closed. It was not and must not be — that entry is deferred and **OPEN** with a named owner, as both prior passes verified. Same defect class as the finding I was sent to fix (the record asserting what is not true of the world), through a different door, and it is the exact trap this story's own intelligence names. It went unseen because iteration 2's gates ran **before** its findings were written into this file, so the red was created by the hand-off itself and nothing re-ran — `AI-E13-1` in miniature. **Fixed in the PROSE, deliberately NOT in the ledger**: appending a closure to green a guard would be `AI-E12-3`'s defect committed inside the guard built to stop it, so `deferred-work.md` was not opened and the sentence now reads *closed as a review item, explicitly not a ledger closure, the entry remains OPEN*, annotated with what changed and why. (⚠️ My own correction re-tripped the guard **twice** before it held — attempt 1 quoted the offending sentence verbatim, attempt 2 described the defect in three new places, each naming the ledger id beside the word it must not sit next to. Recorded rather than tidied away: the analyzer is line-scoped by design and cannot see that the surrounding sentence is true, so the only stable spelling is to name the id **only** on lines that say it is OPEN. A fix that had to be fixed is part of the record, and the lesson belongs to 14.3's dev as much as to me.) The rest of the sweep re-derived as correct: pass-1's four module sizes exact for their baseline, `argus/pipeline.py` 1,111 and absent from the diff, thresholds byte-identical by `git diff -U0 … | grep` (empty), dogfood provenance sha `2eeaace` confirmed an ancestor of `HEAD`, `git tag -l` empty. **No ceiling implication** — all four files ≤ 1,200 (tightest: 1,128, 72 spare), `test_module_size_ceiling.py` green and no exemption added. **No currency-guard implication, confirmed rather than assumed** — `git status --porcelain -- argus/` is empty, so the artifacts' inputs cannot have moved; the regenerator was deliberately NOT run. Gates re-run after the last prose edit (`AI-E13-1`): full suite **1621 passed / 0 failed / 0 skipped / 0 errors, exit 0**, Δ **0** — **LOCAL only; CI evidence is NOT ESTABLISHED**. Files touched: this story file and `sprint-status.yaml`, both left **uncommitted** per §0.8; `argus/`, `tests/`, `deferred-work.md`, `stories/1-5-…md` and all three dogfood artifacts untouched. The story's substance, confirmed by two independent review passes, is byte-unchanged. Status `in-progress` → `review`. |
| 2026-08-18 | **Review iteration 2 — CONCERNS.** Independent re-derivation (fresh harness, not the dev's script) confirms the fix round exactly: CPython grounding for all five excluded/carried-negative cases; DN-14-2-5's three claims (`_scan_span`/`logical_statement_starts` outside every changed diff hunk, byte-identical boundary map, and a hand-built "wrong" in-scan implementation demonstrated to fail `-122`); RED-first reproduced row-for-row against `a9cf25d` (8-vs-5, 5-vs-4 ×4, 6-vs-4, 5-vs-4 ×2, `-122`'s 7-vs-5); the structural GAINED=0 argument adjudicated sound by source (`_counted_statement_texts` strictly subsets, `mock_ratio` never reads the statement count); corpus-wide **n=4,673, exact=4,672, over=0, under=1** reproduced exactly via an independent line-matched-ground-truth harness; 15 hand-built adversarial predicate shapes (except\*/tuple/as, wrapped except-as, conditional-expression else, match class pattern + guard, case-as-identifier, string/comment containing except:/case:, decorator with f-string colon, annotation-only case, CRLF, non-ASCII) all matched CPython exactly — no predicate defect found. Gates re-run independently: 1621/0/0/0 pytest, mypy Success-87, bandit 19L/0M/0H — all exact. Both iteration-1 findings confirmed CLOSED. **One new Low finding**: the Dev Agent Record's own AC9 module-size table and File List numbers ("this pass") do not match the files as committed (`provenance_scan.py` claimed 903 vs measured 926; `vacuous_test.py` 919 vs 929 — the claimed figure is this pass's PRE-edit count, not re-measured; `test_vacuous_density.py` 1,053 vs 1,060; `test_vacuous_detector.py` exact at 1,128). No ceiling implication, no functional impact — flagged because the story's own stated method is "measured, not asserted." Status `review` → `in-progress` pending this cleanup. |
| 2026-08-18 | **Review iteration 1 addressed — 2 of 2 findings closed (1 fixed, 1 confirmed-deferred).** Finding 1 fixed at the MECHANISM, not the prose: a bare `except`/`else`/`finally`/`case` clause header and a decorator no longer open a statement in the density denominator, because CPython builds no `ast.stmt` for either. The docstring claim the review falsified — a residual "under-count away from a flag" that measured as **64/64** and **27/28** OVER-counts, biasing TOWARDS a flag — is corrected to what was measured AFTER the fix. Denominator vs CPython ground truth **1.0052× → 1.0000×** on the 1,848 flagged minions tests, exact **1,784/1,848 → 1,848/1,848**; agent-smith **0.9997×**, exact 680/681; corpus-wide **4,672/4,673 exact, 0 over-counts, 1 under-count** (the inline compound header — so the original direction claim is now true of the code). Flag rate minions **660 → 653 = 18.4%**, agent-smith **297 → 295 = 26.3%**; flags **GAINED 0** against both `966ceba` and `a9cf25d`, lost 1,572 → **1,581**. The 31 adjudicated locators **did not move** — 13 · **14/4/23/8**, **verdict-eligible 0/31**; cartridge recall 4/4; `ast_corroborated` identical on all 4,664 unchanged-heuristic spans. Applied at the COUNT and not in `_scan_span`, so fact (b)'s `logical_statement_starts` is **byte-identical** (DN-14-2-5) — `-122` proves it. New guards `-121`/`-122` confirmed **RED first** against `a9cf25d` (8-vs-5, 6-vs-4, 5-vs-4) with four negative controls (`elif`, inline clause body, `case` as a name, `a @ b`) that were already green. Finding 2 (`DF-14-2-B`, `$`-anchored `_ASSIGNMENT_RE`) left untouched as deferred; ledger entry verified well-formed with a named owner. Gates: **1621 passed / 0 failed / 0 skipped** (Δ +2), mypy **Success 87** (Δ 0), bandit **19L/0M/0H** (Δ 0) — **LOCAL only; CI evidence is NOT ESTABLISHED** (3.10/3.12 legs unexecuted). Thresholds byte-identical, `argus/pipeline.py` untouched, no size exemption. Dogfood artifacts regenerated via `AI-E12-11` (`2eeaace` → `e2e278c`). Status stays `review`. |
| 2026-08-18 | **Implemented.** Denominator re-authored over logical statements (1.9071× → **1.0052×** of CPython ground truth, exact on 1,784/1,848); assertion vocabulary widened with a separate naming-convention predicate; **DN-14-2-1 built** — the corroboration path reads a FROZEN 23-name vocabulary, the density numerator reads the widened one. Flag rate minions **1,848 → 660** (52.0% → 18.6%), agent-smith **681 → 297** (60.7% → 26.5%); flags **GAINED 0**, lost 1,572. The 31 adjudicated locators re-scored by execution: 13 spans gain assertion sites, **14 / 4 / 23 / 8** attribution, **verdict-eligible 0/31**. §0.3's every predicted cell reproduced exactly. §0.4's false accusation reproduced RED first and pinned by `-115`, which goes red against the one-table design **while the whole existing suite stays green** — the measured justification for the guard. §0.5's `-109`/`-110` prediction was **WRONG and is recorded as wrong**; `-101`/`-102` moved instead, on the assertion TABLE, and their fixtures were strengthened with the reason. New `tests/test_vacuous_density.py` (cohesion split, no size exemption). Gates: **1619 passed / 0 failed / 0 skipped** (Δ +8), mypy **Success 87** (Δ 0), bandit **19L/0M/0H** (Δ 0) — **LOCAL only; CI evidence is NOT ESTABLISHED**. Story 1.5's `2.04×` corrected on the record to `1.907×`. Dogfood artifacts regenerated via `AI-E12-11` (`26e6fb6` → `a9cf25d`). One item deferred with a named owner. Status `in-progress` → `review`. |
| 2026-08-18 | Story contexted on HEAD `966ceba` (post-14.1). All premises re-derived by execution. **Two proposal figures did not reproduce and are superseded**: the 2.04× denominator inflation (measured **1.907×**, §0.2) and the "4 of 31 / 13 of 31" assertion attribution (reproduces only with the naming convention, §0.3). **One premise was falsified**: widening `_ASSERTION_CALLEES` CAN manufacture a verdict-eligible false accusation through fact (b)'s `_assertion_statement_lines` path — reproduced end to end (§0.4), resolved as DN-14-2-1, and made AC6. Status `backlog` → `ready-for-dev`. |
