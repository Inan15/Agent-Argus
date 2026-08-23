---
baseline_commit: 6d48c15
---

# Story 16.6: The assertion vocabulary recognises the assertion that is a `raise`

Status: done

<!-- Contexted 2026-08-23 at HEAD `6d48c15` by the create-story workflow (Opus 5).

     ⛔ EVERY FIGURE IN §0 WAS READ OFF THE TREE BY EXECUTION, not copied from the epic or from
     the sprint-change proposal. Where the epic text and the tree disagree, §0 says so and THE
     TREE WINS. Story 16.5 failed its readiness validation on three defects — an AC that was
     unsatisfiable inside its own byte-unchanged fence, two ACs that contradicted each other,
     and a motivating premise that was factually FALSE — and all three were AC defects, not
     research defects. This file is written against that lesson: the fix shape, its blast
     radius, its collision cost and its exact before/after number were all MEASURED before a
     single AC was written, and the measurement commands are in Task 0 so the dev reproduces
     them rather than trusting them.

     ⛔ NO `argus/`, `tests/` or `scripts/` file was touched to produce this story. Every
     simulation of the change was performed by in-memory patching or by an out-of-tree pytest
     plugin; `git status --porcelain` carried ZERO entries under `argus/`, `tests/` and `scripts/`
     before and after — that INVARIANT, never emptiness (§0.0). No detector ran over any
     BENCH member; no third-party fetch; nothing ratified; no disposition written; no role
     filled; no `V1.4` row; `adjudication-record.json` byte-unchanged; `DF-13-5-A` OPEN and
     UNSPENT.

     ⛔ AMENDED 2026-08-23 (create-story, amendment mode) after this file FAILED an independent
     readiness validation. The validation confirmed the RESEARCH exact — the −7 re-derived to the
     `Fraction` on all seven named rows, AC5 proven non-vacuous, both collision sites confirmed —
     and found SIX defects, all in this file's own TEXT. All six are repaired here, plus four more
     AC/Task divergences found by sweeping the whole task list for the same shape. The status stays
     `ready-for-dev`. Nothing was re-researched and no figure in §0.3/§0.4 was disturbed.
     ⛔ Two ledger entries were filed by the same pass: `DF-16-6-C` (the CRLF/`.gitattributes` trap
     in `deferred-work.md`) and `DF-16-6-D` (the line-scoped closure-claim trap that made this very
     file's baseline RED). `DF-16-6-B` is deliberately NOT taken — AC6.5 reserves it for the dev.
     Nothing was disposed of; no `DN-*` reopened; sprint-status untouched.

     ⛔ AMENDED AGAIN 2026-08-23 (create-story, amendment mode, pass 2) after a SECOND independent
     readiness validation returned **CONCERNS** — non-blocking. Round 2 re-confirmed by EXECUTION
     that all six round-1 findings are genuinely repaired, that the suite is green with everything
     on disk, that the ledger append is prefix-byte-identical, and that every §0 invariant holds.
     None of that was disturbed. Six TEXT items were repaired: AC5.2 given a task (Task 3.4), AC6.4
     given a task (Task 3.6.1), §0.0's PATH ROOTS block corrected (its five mis-rooted artifacts, and TWO roots -> FOUR), AC4.5's
     dirty-count dropped for the invariance contract, AC4.4 widened to §0.3/§0.4/§0.5, AC5.5 bound to
     every Task 3 subtask, and four stale phrasings softened (§0.0's closed enumeration, Task 7.3's
     singular report, §0.1's `except` row, this block's own porcelain-emptiness sentence).
     **This is the LAST amendment. The next reader is a dev.** -->

## Story

As the **Engineering Lead**,
I want **`raise AssertionError` counted as an assertion**,
so that **the advisory population is not inflated by tests that assert rigorously in a spelling the
tool cannot read.**

### What this story IS

A **one-name widening of the WIDE assertion vocabulary**, in the **de-accusation** direction, with
its collision cost measured and made executable.

`is_assertion_callee` admits a callee that is in `_ASSERTION_CALLEES` **or** matches the
project-helper convention `\A_?assert\w*\Z`. That regex is **case-sensitive**, so `AssertionError`
does not match it, and the table does not carry the name. A test whose contract assertion is

```python
try:
    prosecute(verdict="not-a-verdict", ledger=ledger)
except ProsecutorError:
    pass
else:
    raise AssertionError("a non-AuditVerdict verdict must raise ProsecutorError")
```

therefore scores that line as **no assertion at all**, is scored below its true density, and is
**falsely flagged**. **22 of the 1,032 recorded `vacuous_test_heuristic` findings carry the idiom**
(re-derived here, §0.4), and the tool over-flags in the **accusation** direction.

### What it is NOT

- ⛔ **NOT a promotion.** No finding becomes verdict-eligible. `verdict_eligible` stays `False` for
  every affected row.
- ⛔ **NOT a threshold move.** `ASSERTION_DENSITY_FLOOR` stays `Fraction(1, 4)` and
  `MOCK_RATIO_CEILING` stays `Fraction(1, 2)`, byte-unchanged.
- ⛔ **NOT a change to the frozen table.** `_CORROBORATION_ASSERTION_CALLEES` stays **byte-unchanged
  at 23 names** (`DN-14-2-1`). Facts (a) and (b) are structurally unreachable from this change —
  §2.2 proves it rather than promising it.
- ⛔ **NOT an eighth §5 condition.** `SECTION_5_CONDITIONS` stays at **SEVEN** and
  `GateDecision.precision_evaluable` keeps **exactly four** conjuncts. This story adds neither.
- ⛔ **NOT a module split.** The split this story's PRECONDITION demanded is **ALREADY DONE** —
  §0.2. Re-planning it is pure waste.
- ⛔ **NOT a re-measurement of the corpus.** No detector runs over a bench member. The committed
  adjudication set and gate-decision record stay **byte-unchanged** — and §2.3 shows why they can,
  which is the single most likely thing for a dev to get wrong here.
- ⛔ **NOT a gate outcome change.** The gate stays `BLOCKED`. `DF-13-5-A` stays **OPEN and UNSPENT**.

---

## §0 — PREMISES RE-MEASURED BY EXECUTION at HEAD `6d48c15`

⛔ **Task 0 re-derives every row below before a line is written.** Every story in Epic 16 found a
stated premise false by executing it — 16.4 found three. Budget for it.

### §0.0 The tree, and the baseline — which is GREEN

Branch `epic-16/discharge-df-15-2-d`, HEAD **`6d48c15`** (`docs(16-5): record the iteration-2 review
that closed the story`), **tree clean at that commit**. create-story then wrote **this file** and
**`sprint-status.yaml`**; TWO independent readiness validations then wrote a report each, and the
2026-08-23 amendment pass appended two entries to `deferred-work.md`. None of them was committed,
so the working-tree entries when you open are **this story file**, **its validation reports —
TWO as this line is written**, **`sprint-status.yaml`** and **`deferred-work.md`**.
⛔ **That enumeration is OPEN, not closed.** A later governance pass may add another report under
`stories/`, and an extra artifact there is neither a defect nor a scope breach.
⛔ **Do not assert a COUNT of working-tree entries** (Task 0.1). The tree moves between sessions; the
invariant that actually holds is **zero entries under `argus/`, `tests/`, `scripts/` or
`_bmad-output/design-artifacts/ArgusAgent/validation-corpus/`**.

⛔ **PATH ROOTS — read this BEFORE Task 0's first command, because this file mixes FOUR of them.**
`argus/**`, `tests/**`, `scripts/**` and `pyproject.toml` are **repo-root-relative**. But
`validation-corpus/adjudication-set-13-5.json`, `validation-corpus/adjudication-record.json` and
`validation-corpus/gate-decision-record.json` are **NOT at the repo root**. ⛔ **And they are not
all one root: there are THREE roots here, and they are three DIFFERENT directories.**
1. The three JSON artifacts above live under
   **`_bmad-output/design-artifacts/ArgusAgent/validation-corpus/`** — which holds the corpus JSONs
   and the blocking worklists, and nothing you read at Task 6.
2. `epics.md`, `architecture.md`, **`deferred-work.md`** and `precision-validation-protocol.md` live
   one directory **UP**, directly under **`_bmad-output/design-artifacts/ArgusAgent/`**.
3. **This story file and its validation reports** live under
   **`_bmad-output/design-artifacts/ArgusAgent/stories/`**.
⛔ **`deferred-work.md` is NOT under `validation-corpus/`.** Task 6 ENOENTs on its first line if you
look for it there — which is the identical failure this block exists to prevent. AC6.1 writes the
correct path out in full; measure it, do not assume it.
Resolve the two builder artifacts through the builders' own path constants
(`scripts/build_gate_decision.py`, `scripts/build_adjudication_record.py`) rather than re-typing
either root. A command that takes the short form literally **ENOENTs on its first line**.

**THE BASELINE, MEASURED — and it is GREEN.** Story 16.5's dev found the baseline RED when the story
claimed green, and it cost a commit to repair. It was re-measured here by execution at `6d48c15`:

| Gate | Command | Measured | Exit |
|---|---|---|---|
| Full suite | `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 pytest` | **1,688 passed, 0 failed** across **122** test files — ⚠️ **re-measured 2026-08-23 WITH the amended story file and the two new ledger entries on disk** (see the note below; the first measurement of this row was taken before this file existed and was FALSE) | **0** ✅ |
| Coverage | `pytest --cov=argus --cov-fail-under=80` | **95.55%** (7,095 stmts, 316 missed) | **0** ✅ |
| Types | `mypy argus` (**the CI scope**) | Success, **94** source files | **0** ✅ |
| Security | `bandit -r argus --severity-level medium` | **No issues** (Medium 0, High 0) | **0** ✅ |
| Ceiling | `pytest tests/test_module_size_ceiling.py` | **6 passed** | **0** ✅ |
| Builder | `python scripts/build_adjudication_record.py --check` | *"the adjudication record is current (**31** row(s))"* | **0** ✅ |
| Builder | `python scripts/build_gate_decision.py --check` | *"CURRENT — **BLOCKED** (NOT COMPUTED BY THIS RUN)"* | **0** ✅ |

⛔ **THE FULL-SUITE ROW WAS RE-MEASURED 2026-08-23 WITH THIS FILE ITSELF ON DISK, AND THE FIRST
MEASUREMENT WAS WRONG.** As first contexted the row was taken *before* this file existed. With the
file present the suite was **1,687 passed / 1 failed / exit 1**, and this story file was the **sole**
cause: §References carried a closure verb and three ledger ids on ONE physical line, and
`story_closure_claims` (`tests/test_governance_record_integrity.py`) is **line-scoped by design**, so
it read that line as a claim about all three ids — including one the ledger does not back. **The
guard is right and was NOT amended; the record was wrong and was.** The References line is now
wrapped so a closure verb never shares a physical line with an open id, and the row above is the
re-measured result **with the amended story file and the 2026-08-23 ledger appends on disk**.
`DF-16-6-D` files the recurring authoring defect this belongs to.

⛔ **WRITING RULE FOR EVERY LINE YOU ADD TO THIS FILE, TO THE LEDGER, OR TO ANY `stories/*.md`:**
a closure verb (`CLOSED`, `Closes`, `closed by this story`) must never appear on the same **physical
line** as a ledger id that is still open. Wrap the line instead. `story_closure_claims` globs every
`*.md` in `stories/`, so a report *about* this defect reproduces it if quoted verbatim.

⚠️ **ONE MEASURED CAVEAT, recorded rather than smoothed.** `mypy argus scripts` — a **wider** scope
than CI's — reports **4 pre-existing errors in 3 files**: `scripts/candidate_selection.py:600`
(`"PinnedFile" has no attribute "definitions"`), `scripts/build_gate_decision.py:110`
(`Cannot find implementation or library stub for module named "_cartridge"`), and
`scripts/audit_validation_corpus.py:702` (`Value of type "object" is not indexable`). **CI runs
`mypy argus`** (`.github/workflows/audit-ci.yml`), which is clean. These are **NOT this story's
business** and **must not be fixed here** — but a dev who widens the mypy scope on a hunch will see
red that predates them, will believe they caused it, and will burn a cycle. They did not.

⛔ **Local gates are Windows-only; CI runs an ubuntu matrix.** A green local suite has already
shipped POSIX-only bugs to master from this repository (`AI-E13-1`). Nothing in this story is
platform-sensitive — it adds one ASCII name to a frozenset — but do not treat a green Windows run as
proof for the matrix.

### §0.1 The defect, measured at the real seam

```text
is_assertion_callee("AssertionError")                        -> False   ← the defect
_ASSERTION_NAMING_CONVENTION.match("AssertionError")         -> None    ← case-sensitive \A_?assert\w*\Z
"AssertionError" in _ASSERTION_CALLEES                       -> False
len(_ASSERTION_CALLEES)                                      == 88
len(_CORROBORATION_ASSERTION_CALLEES)                        == 23      ← FROZEN, DN-14-2-1
len(_MOCK_CALLEES)                                           == 10
```

**AND — the load-bearing fact the epic text does not state.** The index **DOES** emit a call edge for
the message-carrying spelling. Measured against a real `build_ast_index` over a scratch fixture:

| Source | Edges emitted in the span |
|---|---|
| `raise AssertionError("must raise")` | `['AssertionError']` ✅ **an edge exists** |
| `raise builtins.AssertionError("x")` | `['AssertionError']` ✅ (attribute form resolves to `.attr`) |
| `raise AssertionError` (bare, no parens) | `[]` ⛔ **no edge — it is not a call node** |
| `with pytest.raises(AssertionError):` | `['raises', 'check']` — **no `AssertionError` edge** |
| `except AssertionError:` | ⚠️ **no `AssertionError` edge** — not a call node. ⚠️ **Not literally `[]`**: the span still emits whatever else it calls (`try: f()` / `except AssertionError: pass` measures `['f']`). The row's point is the ABSENT `AssertionError` edge, and it holds. |
| `e = AssertionError("x")` | `['AssertionError']` — the collision shape (§0.5) |

⛔ **This is what decides the fix shape, and it is the single most important row in §0.** Because the
`raise AssertionError("msg")` form already reaches the edge set, **the entire measured population is
reachable by adding ONE NAME to the table.** No new scanner is required — and adding one would
**double-count** (§2.1).

### §0.2 ⛔ THE EPIC TEXT AND THE SPRINT-STATUS COMMENT ARE STALE ON THIS STORY'S PRECONDITION

The epic's Story 16.6 block, and §2.2/§5.2 of `sprint-change-proposal-2026-08-22.md`, both open with:

> ⛔ **Precondition: `argus/detectors/vacuous_test.py` sits at 1,196/1,200 with `DF-15-2-D` filed.
> The module SPLIT lands FIRST, alone, in its own commit, with no behaviour change.**

**That precondition is DISCHARGED. Do not re-plan it. Do not re-split anything.**

- The split landed in **`4123931`** — *alone and first*, in its own commit, before any behaviour
  change, exactly as the ledger trigger required.
- **`ba5e8df`** then repaired the four currency guards the split re-armed, in Story 16.4 §2.7's
  order (`argus/` first, regenerate, artifacts committed separately).
- **`DF-15-2-D` is CLOSED 2026-08-22**, and the closure carries a machine-readable `- status:` field
  appended by Story 16.5 so `TC-ArgusAgent-DOCS-001-78` can see it.

**AND THE TARGET FILE HAS MOVED.** Re-measured with the ceiling guard's own `_physical_line_count`
(`_CEILING = 1200`) at `6d48c15`:

| Module | Lines | Headroom | Note |
|---|---:|---:|---|
| **`argus/detectors/vacuous_vocabulary.py`** | **455** | **745** | ⬅ **THE TABLES LIVE HERE NOW.** This is where you edit. |
| `argus/detectors/vacuous_test.py` | **796** | 404 | was 1,196. The scorer, not the vocabulary. |
| `argus/detectors/provenance_scan.py` | 976 | 224 | fact (b). Untouched by this story. |

⛔ **An AC that names `argus/detectors/vacuous_test.py` as the home of the assertion table names a
file that no longer holds the code.** The epic text was written before `4123931`. This story's ACs
name `vacuous_vocabulary.py`, and every path an AC names below was confirmed to exist at that path
at `6d48c15`.

**What is unchanged by the split:** `vacuous_test.py` re-exports every moved name, so
`from argus.detectors.vacuous_test import _CORROBORATION_ASSERTION_CALLEES` still resolves and
`vacuous_test.__all__` is unchanged at **9**. `vacuous_vocabulary.__all__` is `['is_assertion_callee']`.
Existing tests import from **both** modules; neither import path may move in this story.

### §0.3 ⛔ THE EXPECTED MEASURED OUTCOME — direction and magnitude, stated up front

Measured by calling the **shipped** scorer components (`is_assertion_callee`,
`_matches_assertion_convention`, `_count_bare_asserts`, `_count_statements`, `index_aligned_lines`,
`_edges_in_span`, `_MOCK_CALLEES`, `ASSERTION_DENSITY_FLOOR`, `MOCK_RATIO_CEILING`) over blobs
materialised from each member's **pinned git object** into a scratch tree — the same read-only
method `sprint-change-proposal-2026-08-22.md` used and certified. **All 1,032 findings walked, 0
skipped, 0 unresolvable.**

| | Count |
|---|---:|
| Recorded `vacuous_test_heuristic` findings | **1,032** |
| …of which carry a `raise AssertionError` (any form) | **22** |
| **FLAGGED before** (shipped 88-name table) | **1,032** |
| **FLAGGED after** (89-name table) | **1,025** |
| **DELTA** | **−7** |
| Newly flagged (the forbidden direction) | **0** |

⛔ **THE NUMBER TO EXPECT IS −7, NOT −22, AND A DEV WHO EXPECTS −22 WILL BELIEVE THE FIX FAILED.**
22 findings are *affected* — their `assertion_sites` and `assertion_density` rise. Only **7** cross
the `1/4` floor and un-flag. The other **15** rise but stay below the floor, or are flagged on the
`mock_ratio > 1/2` limb which this change cannot reach at all. Both outcomes are correct.

The seven, with their measured density before → after:

| Member | Locator | Test | Before | After |
|---|---|---|---|---|
| minions | `tests/apaa/test_budget_exhaustion.py:329` | `test_exhaustion_module_is_pure_no_io_clock_random` | `1/6` | `1/4` |
| minions | `tests/apaa/test_critical_subsystems.py:268` | `test_module_is_pure_no_io_clock_random_via_ast_scan` | `1/6` | `1/4` |
| minions | `tests/apaa/test_insufficient_coverage_floor.py:435` | `test_exhaustion_module_floor_logic_is_pure` | `1/6` | `1/4` |
| minions | `tests/cost/test_preflight_variance.py:112` | `test_variance_point_is_frozen` | `1/7` | `2/7` |
| agent-smith | `agentsmith-core/tests/test_regression_alarm.py:493` | `test_detector_alarm_report_path_invokes_no_provider_builder` | `1/6` | `1/4` |
| agent-smith | `agentsmith-core/tests/test_surface_accept.py:165` | `test_ac14_2_the_accept_record_is_in_memory_only_and_is_never_persisted` | `6/25` | `7/25` |
| agent-smith | `agentsmith-core/tests/test_surface_envelope.py:223` | `test_an_outcome_outside_the_closed_set_has_no_exit_code_and_no_fallback` | `0` | `1/4` |

**By member:** the 22 are **minions 12** + **agent-smith 10**. The other three ratified members
(`agent-markovich`, `xagents-webapp`, `ai-body-runtime`) contribute **zero**, so any re-derivation
reporting a hit in those three has a bug, not a discovery.

**Direction:** strictly **de-accusation**. `assertion_sites` can only rise; `assertion_density` is
`assertion_sites / statement_count` and the floor **fires from below**; `mock_ratio`, `call_sites`
and `statement_count` are all computed from tables and scanners this change does not touch. **A
newly-flagged finding is structurally impossible, and `0` is the measured confirmation.**

### §0.4 The spelling census — ⛔ ALL 22 ARE THE CALL FORM. ZERO ARE BARE.

Re-derived read-only over pinned git objects, classifying every `ast.Raise` inside each flagged
span:

| Spelling | Findings |
|---|---:|
| `raise AssertionError("msg")` — a **Call** node, **emits an edge** | **22** |
| `raise AssertionError` — a bare **Name**, emits **no** edge | **0** |
| `raise <attr>.AssertionError(...)` | 0 (present in the shape probe, absent from the corpus) |

⛔ **This is why the fix is one table entry and not a second scanner.** The bare form is
**measured at 0 of 1,032**. Building a text-line scanner for it — the shape `_count_bare_asserts`
uses — would (a) buy zero on the measured population and (b) **double-count all 22**, because those
spans already contribute an edge. §2.1 and `DN-16-6-2` hold this decision.

### §0.5 The collision cost, under `DN-14-3-5`'s own arithmetic

`DN-14-3-5` is the standing rule for admitting a name: *a name is admitted when its MEASURED
non-assertion collision as a Python callee is materially smaller than its MEASURED assertion
benefit.* It was applied here, with its own method — **stdlib `ast`, deliberately NOT Argus's own
index, because deriving a collision argument from the thing under test is circular** — over
**5,085** Python files (Argus itself, all five pinned corpus checkouts, this environment's
`site-packages`, and the CPython 3.11 standard library):

| Shape of the `AssertionError(...)` call site | Sites |
|---|---:|
| **inside a `raise`** — i.e. an assertion | **183** |
| **not inside a `raise`** — i.e. a collision | **2** |

**Benefit/cost ≈ 91×.** `DN-14-3-5` admits it, by the same arithmetic that excluded `match` (0.7×)
and `Error` (0×) and admitted `expect` (237×) and `equal` (45×).

**The two collisions are named, not summarised.** One is `stevedore/tests/test_extension.py:118` in
`site-packages`; the other is Argus's own
`tests/test_open_llm_adapter.py:391` —
`post_error=AssertionError("must not POST")`, an `AssertionError` **constructed as a tripwire value**
for a fake to raise later. That is still an assertion device, and in any case the error direction is
**flag-reducing**. ⛔ **This cost is recorded because recording it in prose only was the previous
round's mistake** — AC5 makes it executable.

⛔ **`pytest.raises(AssertionError)` is NOT a collision and NOT a double count.** Measured: the span
emits `['raises', 'check']` and **no `AssertionError` edge**, because the class name there is a bare
`Name` argument, not a `Call`. `raises` already counts once, and it still counts exactly once.

### §0.6 Module headroom, and ⛔ WHERE THE GUARDS GO — `DF-15-2-E` will fire if you get this wrong

Measured with the ceiling guard's own `_physical_line_count` (`_CEILING = 1200`) at `6d48c15`:

| File | Lines | Headroom | Ledger |
|---|---:|---:|---|
| `argus/detectors/vacuous_vocabulary.py` | **455** | **745** | none — filed as a disposition under `DF-15-2-D`, deliberately not its own entry |
| `argus/detectors/vacuous_test.py` | 796 | 404 | `DF-15-2-D` **CLOSED** |
| **`tests/test_vacuous_density.py`** | **1,159** | **41** | ⛔ **`DF-15-2-E` OPEN — trigger at 1,180. 21 lines of margin.** |
| `tests/test_vacuous_cross_language.py` | 1,031 | 169 | none |
| `tests/test_vacuous_detector_index.py` | 1,065 | 135 | none |
| `tests/test_vacuous_detector.py` | 791 | 409 | `DF-14-3-H` |
| `argus/precision/gate_decision.py` | 1,132 | 68 | **`DF-16-5-A`** (filed 2026-08-23, **not split**) |
| `tests/test_gate_independence.py` | 1,127 | 73 | **`DF-16-5-B`** (filed 2026-08-23, **not split**) |
| `argus/precision/gate_independence.py` | 328 | 872 | none — new at Story 16.5 |

⛔ **`DF-15-2-E`'s trigger, verbatim:** *"the first change that would take this module past **1,180**
performs the cohesion split FIRST — by subject cohesion, never by arithmetic, with no function split
across the boundary."* The split-first rule means **a split lands ALONE and FIRST, in its own
commit, before any behaviour change** — the discipline `4123931` + `ba5e8df` just demonstrated.

**`tests/test_vacuous_density.py` is the subject-correct home for a density-numerator guard, and it
has 21 usable lines.** This story's guards are far more than 21 lines. So:

> ⛔ **DECISION `DN-16-6-3`: this story's guards go in a NEW module,
> `tests/test_vacuous_vocabulary.py`, and `tests/test_vacuous_density.py` is BYTE-UNCHANGED.**

Rationale, and the rejected alternatives, are in Dev Notes. The consequence stated plainly: **taking
the obvious route — putting the guards in `test_vacuous_density.py` — fires `DF-15-2-E`'s trigger
and drags a test-module split into a behaviour-change story, which is precisely what the split-first
rule forbids.** AC6.2 asserts the 1,180 line is not crossed, by execution.

⛔ **`DF-16-5-A` and `DF-16-5-B` were filed 2026-08-23 and are NOT in the epic text.** Neither is
this story's business. Put nothing in `gate_decision.py` or `test_gate_independence.py`.

### §0.7 ⛔ THREE OF THE FIVE CORPUS CHECKOUTS ARE ALREADY DIRTY — measure invariance, not cleanliness

Measured at `6d48c15` before this story touched anything — and then **twice more on the same day**,
which is the finding that matters far more than any single column:

| Member | Checkout | contexting | independent validation | amendment pass |
|---|---|---:|---:|---:|
| `agent-markovich` | `…/AgentMarkovich` | **0** | **0** | **0** |
| `minions` | `…/Minions` | **13** | **14** | **0** |
| `xagents-webapp` | `…/XAgents-WebApp` | **1** | **1** | **1** |
| `agent-smith` | `…/XAgents/XAgents/Agent-Smith` (⚠️ **depth 5**, not depth 4) | **16** | **16** | **18** |
| `ai-body-runtime` | `…/ai_body_runtime` | **0** | **0** | **0** |

⛔ **Three measurements on 2026-08-23 returned three different answers.** These are live working
trees that nobody in this story controls: `minions` went 13 → 14 → 0 while this story was being
written and validated, and `agent-smith` 16 → 16 → 18. **The counts above are a dated OBSERVATION,
not a premise — assert none of them.** Your own numbers will differ again, and that is not a
discovery. The one property that is stable, and the only one an AC may assert, is **invariance
across your own run** (AC4.5).

⛔ **An AC demanding `git status --porcelain` be EMPTY for these is unsatisfiable and would fail for
a reason nobody can fix** — this is the Story 16.5 defect class, caught here rather than by the dev.
**AC4.5 therefore asserts INVARIANCE:** capture the porcelain output **before and after** and assert
it is byte-identical. The dirt is pre-existing, is none of this story's business, and **must not be
cleaned** — cleaning a corpus member's working tree is a mutation of a ratified member.

This is also why the re-derivation reads through `git cat-file -p <pinned_sha>:<path>` into a
scratch tree: **the pinned bytes are reachable regardless of what the working tree currently holds**,
which is the property `sprint-change-proposal-2026-08-22.md`'s harness relies on. It resolved **all
1,032** locators with **0 unresolvable** against these same dirty checkouts.

### §0.8 Next free verification ids

Highest `TC-ArgusAgent-DETECT-001-NN` in the tree is **137** (`tests/test_vacuous_detector_index.py`).
**This story's ids start at `-138`.** Re-derive before writing — do not trust this line.

### §0.9 What is already true and must NOT be re-done

| Already true | Evidence |
|---|---|
| The `vacuous_test.py` cohesion split | `4123931` (alone, first) + `ba5e8df`. `DF-15-2-D` **CLOSED 2026-08-22**. |
| The QA Lead role is **FILLED** | Veer Pratap Singh, operator act 2026-08-22, a dated §2 block under **V1.3** with **NO `V1.4` row**. A **16.7** precondition, not this story's. |
| `SECTION_5_CONDITIONS` is at **SEVEN** | Story 16.5. `precision_evaluable` has exactly **four** conjuncts. This story adds neither. |
| `argus/precision/gate_independence.py` exists | New at Story 16.5, 328 lines. Untouched here. |
| The baseline is **GREEN** | §0.0 — ⚠️ **it was not, until this file's §References was wrapped on 2026-08-23**; the row there is the re-measurement with the amended file on disk. Re-verify anyway; that is Task 0. |
| **No existing guard detects the change** | Measured: the full suite run with an out-of-tree plugin that adds `"AssertionError"` to the wide table is **identical to baseline, with zero delta in any other test** — independently reproduced 2026-08-23 (both runs returned the same single governance failure and nothing else, before §References was repaired). **The load-bearing property is the ZERO DELTA, not the absolute count**; §0.0 carries the count. ⛔ **This is the point of AC5, not a reassurance:** a fix that no guard can see is a fix that can be silently reverted. |
| Both builders stay **CURRENT** under the widened table | Measured: `build(check_only=True)` → exit **0** for both, with the table patched in memory. §2.3. |

---

## §1 — WHY THIS STORY EXISTS

### §1.1 The failure mode, stated concretely

The density numerator asks one question — *"does this test assert anything?"* — and wants
**BREADTH**. A name it cannot see **invents a low density and accuses a real test**. That is exactly
what happens here: a `raise AssertionError("…")` is one of the most rigorous assertions a Python
test can make (it is what `pytest`'s own rewriting produces), and the vocabulary scores it as zero.

The error is in the **accusation** direction and is therefore the one the project's locked asymmetry
cares about — *a false 🔴 is the lethal failure; a real vacuous test left advisory is tolerable*.

### §1.2 Why it is contained, and why the severity is 🟠 and not 🔴

The defect lives entirely in the **advisory tier**. The advisory tier **cannot block**: the
corroboration path reads the **FROZEN** table by name and never `is_assertion_callee`
(`DN-14-2-1`), so no finding here is or becomes verdict-eligible. The gate remains correctly
`BLOCKED` before and after. The story fixes a **measured false-flag defect**, and nothing else.

### §1.3 What this story does NOT fix, named so it is not mistaken for fixed

- **The bare `raise AssertionError` spelling stays invisible.** Measured **0 of 1,032**. It is a
  **recorded, executable residual** (`DN-16-6-2`, AC5.4), filed as **`DF-16-6-B`** — not a
  half-finished fix, and not something to "tidy up" later into a double count.
- **`DF-16-6-A`** — the mock-referencing clause of fact (b) is provably dead over the ratified
  corpus (0 of 1,032). **OPEN. Untouched.** Removing it would promote 6 findings; this story
  promotes nothing.
- **The 15 findings that stay flagged.** Correct, not a shortfall (§0.3).
- **The committed corpus artifacts do not move.** §2.3. That is by design and is asserted.

---

## §2 — THE COUPLINGS THAT WILL BITE

### §2.1 ⛔ THE DOUBLE-COUNT TRAP — the single most consequential thing in this story

`assertion_sites = assertion_call_sites + bare_asserts` (`vacuous_test.py::_score`), where
`assertion_call_sites` counts **edges** through `is_assertion_callee` and `bare_asserts` counts
**source lines** through `_count_bare_asserts` / `opens_bare_assert`. **Two independent counters over
the same span.**

`raise AssertionError("msg")` **already produces an edge** (§0.1). So:

- Adding `"AssertionError"` to the table → each such statement counts **once**, through the edge
  path. ✅
- **ALSO** adding a `raise AssertionError`-matching line scanner → each such statement counts
  **TWICE**, inflating `assertion_sites` for all 22. ⛔

⛔ **Do exactly one of these, and it is the table entry.** AC5.3 asserts non-double-counting by
execution on a fixture carrying both spellings, so the trap is detectable rather than remembered.

### §2.2 ⛔ `DN-14-2-1` — and the inertness of facts (a) and (b) is STRUCTURAL, not a promise

There are TWO vocabularies because there are TWO QUESTIONS. This story widens the **WIDE** one only.
The corroboration path is unreachable from it, and this is provable by reading the code rather than
by measuring a corpus:

- `_score` uses `is_assertion_callee` for **`assertion_call_sites` only**.
- `_sut_call_sites` filters on **`_CORROBORATION_ASSERTION_CALLEES`** and `_MOCK_CALLEES` — never the
  wide table, never `is_assertion_callee`.
- `_ast_corroborated` passes **`assertion_callees=_CORROBORATION_ASSERTION_CALLEES`** into
  `provenance_evidence`.
- `mock_ratio` reads `_MOCK_CALLEES`; `call_sites` is `len(span_edges)`; `statement_count` is
  `body_statement_count`. **None of the four reads the wide table.**

⛔ **`_CORROBORATION_ASSERTION_CALLEES` stays byte-unchanged at 23 names. If the fix appears to
require changing it, STOP — that is an AC7.4 escalation, not a story decision.**

⚠️ **The measured false 🔴 that this separation prevents is written out beside the frozen table's
declaration in `vacuous_vocabulary.py`.** Read it before you touch anything in that file.

### §2.3 ⛔ THE COMMITTED ARTIFACTS DO NOT MOVE, AND MUST NOT BE MADE TO

A dev who reads §0.3's *"1,032 → 1,025"* will reach for `scripts/audit_validation_corpus.py` to
refresh the population. **DO NOT.** That would be a **new measurement over five corpus members**, an
act this story is not authorised to take, and it would rewrite the adjudication set that
`build_adjudication_record.py`'s exhaustiveness check compares the 31 rows against.

**It is also unnecessary, and that is measured rather than assumed.** `build_gate_decision.py`
reads the **committed** `adjudication-set-13-5.json`; `corpus_read_proof()` is documented as read
*"off the artifact rather than recomputed"*, because *"re-deriving it here — a day later, over
whatever the checkouts look like now — would be a second measurement wearing the first one's name."*
Neither builder invokes a detector. Confirmed by execution: with `"AssertionError"` patched into the
wide table in memory, **both** `build(check_only=True)` calls returned **exit 0**.

⛔ So: **`adjudication-record.json`, `adjudication-set-13-5.json` and `gate-decision-record.json` are
BYTE-UNCHANGED by this story** (AC6.3), the `−7` lives in **this story file and the ledger**, and no
disposition, verdict, finding or gate artifact is produced or modified.

### §2.4 The existing table invariants are OPEN, and the new name satisfies all of them

Every guard closing over the wide table was read. **None goes red**, and the reasons are structural:

| Guard | Assertion | Effect of `+AssertionError` |
|---|---|---|
| `test_vacuous_cross_language.py` | `len(_ASSERTION_CALLEES) >= 88` | still true (89) |
| `test_vacuous_cross_language.py` | `{"match","doesNotMatch","objectContaining","Error"} ∉ table` | unaffected |
| `test_vacuous_cross_language.py` `-133` | named-name arms (`ok`/`equal`/`Equal`/`throws`/`rejects`), `Error` excluded | unaffected — it is a named-name guard, **not** a whole-table sweep |
| `test_vacuous_density.py` | `_CORROBORATION_ASSERTION_CALLEES < _ASSERTION_CALLEES` (proper subset) | still true |
| `test_vacuous_density.py` | `len(_CORROBORATION_ASSERTION_CALLEES) == 23` | unaffected (frozen table untouched) |
| both | flatness: `isinstance(table, frozenset)`, all members non-empty `str` | satisfied — one plain ASCII string |

⚠️ **And that is the problem AC5 exists to solve:** the full suite is **identically green** with and
without the change (§0.9 — *not* §0.8, which is the verification-id section). **The new guards are the only thing that can make this fix visible.**

### §2.5 Guard vacuity — this project's signature defect

This project shipped **4 of 35 unreal guards in Epic 14**, and 16.3's own mutation run caught one of
its own. The **GUARD-ADEQUACY CLAUSE** (`architecture.md` §Enforcement) applies in all three parts,
discharged **in each guard's own docstring**: (i) name the **observable**; (ii) demonstrate the
defect **moves** it — RED **at the real seam**, not against a reconstruction; (iii) at least one
adversarial variant **generated** from the table the guard closes over, with its count.

⛔ **Run every mutation with `PYTHONDONTWRITEBYTECODE=1` and a cleared `__pycache__`.** 16.2 recorded
a false RED from a stale cache and had to re-run everything. **Restore the tree after each mutation
and confirm `git status --porcelain` is BYTE-IDENTICAL to a capture taken immediately before that
mutation.** ⛔ **Not "empty" — empty is unreachable for this story's whole duration** (AC5.1), and a
check nobody can satisfy is the Story 16.5 defect class.

⛔ **The lockstep trap has fired four times** (16.1, 16.2, 16.3, and once inside 16.5). Here it is
specific and named: **a fixture whose density changes because you added the `raise` line is a
fixture in which the numerator AND the denominator both moved** — `_count_statements` counts the
`raise` as a logical statement. A guard built that way tests the fixture, not the name. ⛔ **Vary
ONLY the callee name, with the statement count PINNED**: score the *same* fixture text against the
shipped table and against the widened table, or use a control whose statement count is asserted
equal — the shape `-133` already uses (`assert cost.statement_count == control.statement_count`).

### §2.6 ⛔ No operator acts. Contexting a story is not authorising its acts.

No `checkout`, `stash`, `clean`, `reset` or `worktree` on any ratified or candidate repository,
ever. **This story runs no detector over any bench member, fetches nothing third-party, ratifies
nothing (`N` stays 5), writes no disposition, fills no role, adds no `V1.4` row, leaves
`protocol_cleared` `False` and the seal closed.** `DF-13-5-A` stays **OPEN and UNSPENT**.

Re-deriving §0.3 and §0.4 is read-only over **pinned git objects** into a **scratch tree** and
writes nothing — the method `sprint-change-proposal-2026-08-22.md` used and certified. **A corpus
member's working tree is never mutated.**

---

## Acceptance Criteria

### AC1 — THE RECOGNITION IS ADDED TO THE WIDE VOCABULARY, AND ONLY THERE

**Given** two assertion vocabularies exist for two different questions (`DN-14-2-1`)
**When** the recognition for `raise AssertionError` is added
**Then** it is added to **`_ASSERTION_CALLEES` in `argus/detectors/vacuous_vocabulary.py`** — the
WIDE table, the density numerator — and nowhere else.

- **AC1.1** — `is_assertion_callee("AssertionError")` returns **`True`**.
- **AC1.2** — `len(_ASSERTION_CALLEES) == 89` (was 88), and `"AssertionError" in _ASSERTION_CALLEES`.
- **AC1.3** — ⛔ **`_CORROBORATION_ASSERTION_CALLEES` is BYTE-UNCHANGED at 23 names.** Asserted by
  `len(...) == 23` **and** by `"AssertionError" not in _CORROBORATION_ASSERTION_CALLEES`, **and** by
  the file diff carrying no change inside that frozenset's declaration.
- **AC1.4** — ⛔ **`_ASSERTION_NAMING_CONVENTION` is BYTE-UNCHANGED.** The regex stays
  `re.compile(r"\A_?assert\w*\Z")` — **case-sensitive**, `\A`/`\Z`-anchored. Making it
  case-insensitive is **rejected** (`DN-16-6-1`) and is an AC7.4 escalation.
- **AC1.5** — the addition carries an in-source `DN-14-3-5` block recording the benefit and cost
  **you re-derive at Task 0.6**, over a population whose **inclusion rules the block states
  explicitly**, and **naming both collision sites** (`site-packages/stevedore/tests/test_extension.py`
  and Argus's own `tests/test_open_llm_adapter.py`). Prose alone does not discharge this — AC5.2
  makes it executable.
  ⛔ **The figures are an EXPECTATION, not the contract (AC4.4 — the tree wins), because §0.5's do
  not independently reproduce.** An independent stdlib-`ast` re-derivation over the population §0.5
  *describes* measured **172 : 2 over 4,369 files** with nested `.venv` / `site-packages` under the
  corpus checkouts EXCLUDED, and **662 : 3 over 20,769** with them INCLUDED, against §0.5's claimed
  **183 : 2 over 5,085**. All three ratios — **86×**, **91×**, **221×** — clear `DN-14-3-5` by two
  orders of magnitude, and **both named collision sites reproduce exactly**. So the DECISION is
  robust and the NUMBER is not. **State the rule you used**: whether nested `.venv` /
  `site-packages` directories under a corpus checkout are walked, and whether a vendored duplicate
  of a third-party package is folded into one site or counted twice. Then record the figures that
  rule produced, and note any disagreement with §0.5 under AC4.4.
  ⛔ **Do NOT write the figures into the existing table's columns.** At
  `argus/detectors/vacuous_vocabulary.py:290` those columns are
  `name / py collisions / js/ts benefit / benefit/cost / decision` over a stated **4,046**-file
  population of three ratified members — a different population with different semantics.
  `js/ts benefit` for a **Python builtin** is **0**, so writing the benefit there records a false
  value; and `py collisions` in every existing row counts **ALL** Python call sites of the name
  (`match` 706, `Error` 164), which for `AssertionError` is roughly **185**, not the non-`raise`
  **2**. Write a **LABELLED row or an adjacent sub-note** naming its own population and its own two
  measurements — e.g. `python benefit (in-raise sites)` and `python collisions (non-raise sites)` —
  so no later reader treats it as commensurable with its neighbours.
- **AC1.6** — `_MOCK_CALLEES` (10), `ASSERTION_DENSITY_FLOOR` (`Fraction(1,4)`) and
  `MOCK_RATIO_CEILING` (`Fraction(1,2)`) are **byte-unchanged**, and asserted so.

### AC2 — NO SECOND SCANNER, AND NOTHING IS COUNTED TWICE

**Given** `raise AssertionError("msg")` **already emits a call edge** (§0.1)
**Then** the fix is a **table entry only**. ⛔ **No line scanner, no `_count_raise_asserts`, no
change to `_count_bare_asserts` or `opens_bare_assert`.**

- **AC2.1** — `argus/detectors/provenance_scan.py` is **byte-unchanged**.
- **AC2.2** — `_count_bare_asserts` and `opens_bare_assert` are **byte-unchanged**.
- **AC2.3** — a fixture containing exactly one `raise AssertionError("x")` and no other assertion
  scores `assertion_sites == 1` — ⛔ **not 2** — proving the statement is counted once.
  **Measured** (`def test_x(): compute(1); raise AssertionError("x")`):
  shipped `sites=0 stmts=2 density=0 flagged=True` → widened `sites=1 stmts=2 density=1/2
  flagged=False`.
- **AC2.4** — a fixture containing one `assert r` **and** one `raise AssertionError("x")` scores
  `assertion_sites == 2`, proving the two counters compose without overlapping.
  **Measured** (`r = compute(1); assert r; raise AssertionError("x")`): shipped `sites=1 stmts=3
  density=1/3 flagged=False` → widened `sites=2 stmts=3 density=2/3 flagged=False`.
  ⚠️ **`flagged` is `False` in BOTH columns here — assert on `assertion_sites`, not on the flag.**
  `1/3` already clears the `1/4` floor, so a guard written against a flag flip on this fixture is
  vacuous. This is §2.5's lockstep trap in its cheapest form.

### AC3 — FACTS (a) AND (b) DO NOT MOVE, AND NOTHING BECOMES VERDICT-ELIGIBLE

**Given** this story changes the advisory tier only
**Then** no finding becomes verdict-eligible, no threshold moves, and the gate outcome is unchanged.

- **AC3.1** — over a fixture set that includes **at least one** span where `_sut_call_sites`,
  `mock_referencing_assertions` and `sut_result_is_discarded` are each non-trivially exercised,
  `ast_corroborated` is **identical** under the shipped and widened tables. ⛔ **The population must
  be asserted non-empty and non-degenerate before this is asserted about it** (`AI-E11-1`) —
  a fixture set in which `ast_corroborated` is `False` everywhere for an unrelated reason proves
  nothing, and that is the shape this project files as `AI-E3-1`.
  💡 **Constructibility hint, so you do not burn a cycle discovering it:** a `True` here needs an
  assertion whose callee is in the **FROZEN 23** *and* which references a **mock-bound** name, with
  the SUT called and its result discarded — e.g. `compute([1, 2])` (discarded), a `Mock()` bound to
  `fake`, then `self.assertEqual(fake.calculate.call_count, 1)`. The worked example — including the
  false 🔴 that widening the **frozen** table would manufacture — is written out beside
  `_CORROBORATION_ASSERTION_CALLEES`'s declaration in `vacuous_vocabulary.py`. ⚠️ Note
  `mock_referencing_assertions` measures **0 across all 1,032** real findings, so a fixture is the
  only way to reach a non-degenerate population here — that is expected, not a defect.
- **AC3.2** — `mock_ratio`, `call_sites` and `statement_count` are **byte-identical** under both
  tables for every fixture, isolating `assertion_sites` as the only term that moved.
- **AC3.3** — `SECTION_5_CONDITIONS` stays at **SEVEN** and `precision_evaluable` keeps exactly
  **four** conjuncts. ⛔ **Discharged by the EXISTING `tests/test_gate_*.py` guards staying green —
  this story adds no assertion about `argus/precision/**` and imports nothing from it into the new
  test module.** Coupling a vocabulary test to the precision gate would fork a guard that already
  exists, which is the AR7 defect. Confirm by running those guards, not by writing new ones.
  ⛔ **Task 7.1 runs them and that is the whole discharge. Task 3.6 must NOT restate this**, because
  asserting `SECTION_5_CONDITIONS` inside `tests/test_vacuous_vocabulary.py` requires the
  `argus.precision.gate_decision` import this AC forbids.
- **AC3.4** — the direction is **one-way**: across the fixture set, `assertion_sites` under the
  widened table is `>=` its value under the shipped table for **every** span, and
  `heuristically_vacuous` never goes `False → True`.

### AC4 — THE BEFORE/AFTER FLAGGED COUNT IS RE-DERIVED AND RECORDED

**Given** §0.3 states a measured expectation
**When** the dev re-derives it
**Then** the numbers below are reproduced **by execution**, read-only over **pinned git objects**,
and recorded in the story's Completion Notes.

- **AC4.1** — **22 of 1,032** findings carry the idiom; **minions 12 + agent-smith 10**; the other
  three members contribute **0**.
- **AC4.2** — **all 22 are the `raise AssertionError("msg")` CALL form; 0 are bare.**
- **AC4.3** — **flagged before 1,032 → flagged after 1,025, delta −7, newly flagged 0**, with the
  seven named (§0.3's table reproduced or corrected).
- **AC4.4** — ⛔ **if a re-derived figure disagrees with §0.3, §0.4 or §0.5, the TREE WINS and the
  story file is corrected** — record what disagreed and why. Do **not** adjust the code to hit a
  number. (All three sections, not §0.3 alone: AC1.5 delegates §0.5's census to this AC and AC7.3
  lists all three, so a §0.3-only scope leaves those delegations landing nowhere.)
- **AC4.5** — ⛔ the re-derivation **writes nothing**: no finding, verdict, disposition,
  adjudication set or gate artifact, and **no corpus working tree is mutated**.
  ⛔ **The test is INVARIANCE, not cleanliness — SOME members are already dirty and the count MOVES
  between sessions (§0.7, whose own rule is to assert none of its columns), so "porcelain is empty"
  is a check that can never pass.** ⛔ **Assert invariance, never emptiness — and never a COUNT:**
  four measurements on 2026-08-23 returned four different answers, and that is the finding rather
  than noise. Capture
  `git -C <member> status --porcelain` **before and after** for every member read and assert the
  two are **byte-identical**. Read every file with `git cat-file -p <pinned_sha>:<path>` into a
  **scratch tree** — never `checkout`, `stash`, `clean`, `reset` or `worktree`.

### AC5 — GUARDS THAT CANNOT BE VACUOUS

**Given** a guard that cannot fail proves nothing — and the full suite is **identically green** with
and without this change (§0.9)
**Then** the new recognition is driven **RED by executed mutation**, with the tree restored
byte-exact.

- **AC5.1** — **the mutation is: remove `"AssertionError"` from `_ASSERTION_CALLEES`.** At least one
  new case goes **RED at the real seam** — i.e. against a real `build_ast_index` + the real scorer,
  not against a reconstruction. Record the observed RED, the command, and the restoration, run
  under `PYTHONDONTWRITEBYTECODE=1` with `__pycache__` cleared.
  ⛔ **The restoration test is INVARIANCE, not emptiness — AC4.5's defect class, on this repo.** By
  Task 4 the tree necessarily carries the Task 2 edit, the new test module, this story file,
  `sprint-status.yaml` and (by Task 6) `deferred-work.md`, so `git status --porcelain` **can never
  be empty**, and a check demanding it fails for a reason nobody can fix. **Capture
  `git status --porcelain` immediately BEFORE the mutation and assert it byte-identical after the
  restoration.** That is what AC5's own *"restored byte-exact"* means, and it is strictly stronger
  than emptiness — it also catches a stray `__pycache__`, backup or `.orig` file.
- **AC5.2** — the **accepted collision cost is executable, not prose**: a fixture in which
  `AssertionError("x")` appears **outside** a `raise` scores `assertion_sites == 1`, so the cost
  `DN-14-3-5` accepted is asserted rather than remembered, and cannot be re-discovered later as if
  it were news. (`-133`'s "accepted cost" arm is the precedent.)
  **Measured** (`compute(1); e = AssertionError("x"); use(e)`): shipped `sites=0 stmts=3 density=0
  flagged=True` → widened `sites=1 stmts=3 density=1/3 flagged=False`. **The collision DOES un-flag
  a synthetic Python shape** — that is the cost, and it is accepted at the ratio Task 0.6 re-derives
  (§0.5, AC1.5).
  ⛔ **AND CROSS-REFERENCE IT IN BOTH DIRECTIONS, because this AC moves the register.**
  `tests/test_vacuous_cross_language.py:617-621` is where this project registers each admitted
  name's accepted collision cost, as a **hand-listed five-name loop**. `AssertionError` becomes the
  **sixth** admitted name with its cost registered **somewhere else** (`DN-16-6-3` puts it in the
  new module, and that cohesion argument stands), so a later auditor reading `-133` as *the*
  register under-counts by one. **Add a one-line cross-reference to each docstring** — `-133`
  pointing at `tests/test_vacuous_vocabulary.py`, and the new case pointing back at `-133` — so
  neither reads as complete on its own. That is the **only** permitted edit to
  `tests/test_vacuous_cross_language.py` (AC6.1): at most two physical lines of docstring or
  comment, with **no assertion, no fixture and no loop member changed**.
- **AC5.3** — the **double-count trap** is closed by execution (AC2.3/AC2.4).
- **AC5.4** — the **bare-`raise` residual is executable**: a fixture whose only assertion is
  `raise AssertionError` (no parentheses) still scores `assertion_sites == 0` and stays flagged,
  with the guard's docstring stating this is `DN-16-6-2`'s **measured decision (0 of 1,032)** and
  **not** an oversight — so nobody "fixes" it into §2.1's double count.
  **Measured** (`compute(1); raise AssertionError`): shipped `sites=0 stmts=2 flagged=True` →
  widened `sites=0 stmts=2 flagged=True` — **identical in both columns**, which is the point.
  Pair it with a `pass`-bodied control scoring identically (`sites=0 stmts=2 flagged=True`) so the
  case cannot pass by measuring the fixture's shape instead of the name.
- **AC5.5** — ⛔ **non-vacuity, in the `-133` shape.** Every new case asserts its **population is
  non-empty and its seam reachable before** asserting anything about it: the index actually emitted
  the `AssertionError` callee for the fixture, `statement_count > 0`, and a **control** fixture
  isolates the NAME from the fixture's SHAPE with `statement_count` asserted **equal** (§2.5's
  lockstep trap).
- **AC5.6** — at least one adversarial variant is **generated** from `_ASSERTION_CALLEES` itself
  (not hand-listed), with its **count asserted**, per the guard-adequacy clause's third part.

### AC6 — SCOPE, PATHS, CEILINGS AND ARTIFACTS

- **AC6.1** — ⛔ **The write set is exactly:**
  `argus/detectors/vacuous_vocabulary.py` (the one name + its `DN-14-3-5` block) ·
  **NEW** `tests/test_vacuous_vocabulary.py` (the guards) ·
  `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (append `DF-16-6-B`) ·
  this story file · `sprint-status.yaml`.
  **Everything else is byte-unchanged**, in particular `argus/detectors/vacuous_test.py`,
  `argus/detectors/provenance_scan.py`, `tests/test_vacuous_density.py`,
  `tests/test_vacuous_detector.py`, `tests/test_vacuous_detector_index.py`, `argus/precision/**`,
  `scripts/**`, `pyproject.toml`.
  ⛔ **ONE bounded exception, and it is the ONLY one:** `tests/test_vacuous_cross_language.py` may
  receive the AC5.2 cross-reference — **at most two physical lines of docstring or comment inside
  `-133`**, pointing at `tests/test_vacuous_vocabulary.py`. **No assertion, no fixture, no loop
  member and no import may change**, the module stays well inside NFR-M1 (1,031 of 1,200), and if
  you find yourself editing anything else in it, you are out of scope (AC7.4).
- **AC6.2** — ⛔ **`tests/test_vacuous_density.py` stays at 1,159 lines** and in no case crosses
  **1,180**, so **`DF-15-2-E`'s trigger does not fire and no split is dragged into this story**.
  Measured with the ceiling guard's own `_physical_line_count`, and `tests/test_module_size_ceiling.py`
  is green. **No `_EXEMPT_BY_DESIGN` entry is added** — `MAINT-001-04` lets that registry **shrink
  only**, and the remedy is a cohesion split, never a shave and never an exemption.
- **AC6.3** — ⛔ **`validation-corpus/adjudication-record.json`,
  `validation-corpus/adjudication-set-13-5.json` and `validation-corpus/gate-decision-record.json`
  are BYTE-UNCHANGED**, and **both builders exit 0 under `--check`** at the end. `N` stays **5**,
  `protocol_cleared` stays **`False`**, the seal stays closed, no `V1.4` row is added, the
  change-log head is unmoved, and **`DF-13-5-A` stays OPEN and UNSPENT**.
- **AC6.4** — `argus/detectors/vacuous_vocabulary.py` ends the story **≤1,200** lines (it starts at
  455) and `vacuous_test.py`'s re-export surface is unchanged: `vacuous_test.__all__` still has
  **9** entries and
  `from argus.detectors.vacuous_test import _ASSERTION_CALLEES, _CORROBORATION_ASSERTION_CALLEES,
  is_assertion_callee` still resolves to the **same objects** as the direct import.
- **AC6.5** — **`DF-16-6-B`** is appended to `deferred-work.md` for the bare-`raise` residual,
  carrying the measurement (**0 of 1,032**), a severity, an owner and a target story.
  ⛔ **Append-only: no historical entry is edited, and no `DF-*` other than `DF-16-6-B` is created
  or disposed of.** In particular `DF-16-6-A`, `DF-16-6-C`, `DF-16-6-D`, `DF-15-2-E`, `DF-16-1-A`,
  `DF-16-5-A`, `DF-16-5-B` and `DF-13-5-A` are left exactly as they stand.
  ⛔ **`DF-16-6-B` IS RESERVED FOR YOU AND IS STILL FREE.** The 2026-08-23 amendment pass filed
  `DF-16-6-C` and `DF-16-6-D` and deliberately skipped `-B` so this AC keeps its id. Verify that on
  disk before you write, and take the next free letter if it has moved.
  ⛔ **APPEND IN BINARY, AND VERIFY THE BYTES — `DF-16-6-C` is filed for exactly this.**
  `deferred-work.md` contains **exactly one lone `CR`** byte (a literal carriage return quoted as
  prose inside the `DF-15-2-D` entry). That byte is the only reason git classifies the file as
  binary (`git ls-files --eol` reports `i/-text w/-text`, while every sibling `.md` reports
  `i/lf w/crlf`) and therefore leaves it alone under `core.autocrlf=true` with no `.gitattributes`.
  **Any editor that opens and re-saves this file destroys it, and git books that as a one-line
  DELETION of a historical entry — an append-only violation.** It has already happened once
  (`9aea1be`, repaired by `a4de7e7`). So: **count the lone `CR`s before and after your append and
  assert the count is exactly 1**, assert the file still ends with a newline, and assert
  `git diff --numstat` shows **`+n / -0`**. ⛔ **Do not implement `DF-16-6-C`'s `.gitattributes`
  remedy in this story** — that is a repo-wide change and is not this story's business.

### AC7 — GATES AND HAND-OFF

- **AC7.1** — all of §0.0's gates green at the end, at **or above** their baseline numbers: the
  full suite with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` (**≥1,688 passed, 0 failed**), coverage
  `--cov-fail-under=80` (**baseline 95.55%**), `mypy argus` (**CI scope**, clean), `bandit -r argus
  --severity-level medium` (**no issues**), `tests/test_module_size_ceiling.py`, and **both builders
  under `--check` at exit 0**. Record each exit code.
- **AC7.2** — the commit arc follows Epic 16's: **`chore`** (story file + `in-progress`) →
  **`feat`** (the one name + the guards) → **`docs`** (the ledger entry + this story's record).
  ⛔ **No split commit is needed and none is made** — the split already landed in `4123931`.
  A commit cannot cite itself, so a sha citation takes two commits.
- **AC7.3** — Completion Notes record: the re-derived §0.3/§0.4/§0.5 figures, the observed mutation
  RED with its restoration proof, every gate exit code, and **any premise in §0 found false**.
- **AC7.4** — ⛔ **ESCALATE, do not decide, if:** the fix appears to need
  `_CORROBORATION_ASSERTION_CALLEES` widened · or the convention regex made case-insensitive · or a
  finding becomes verdict-eligible · or a threshold must move · or an eighth §5 condition ·
  or a corpus artifact must be regenerated · or `DF-15-2-E`'s 1,180 line must be crossed · or any
  `DN-*` reopened. **A `DN-*` you disagree with is an escalation, not a story decision.**

---

## Dev Notes

### Decisions this story TAKES, each with its rejected alternative

**`DN-16-6-1` — the fix is ONE NAME IN THE TABLE, not a looser regex.**
*Rejected: make `_ASSERTION_NAMING_CONVENTION` case-insensitive.* It would admit `AssertionError`
— and also `Assertion`, `AssertionRegistry`, `Asserter`, `ASSERT_MODE`, `assertionCount` and every
other identifier beginning with those nine letters in any casing. The collision population is
**unbounded and unmeasured**, and `DN-14-3-5` admits a name on a **measured** benefit/cost ratio, not
on a pattern's convenience. A table entry is precise, is measurable (**183 : 2**), and is the shape
Story 14.3 used for every one of its 36 additions. The regex stays byte-unchanged (AC1.4).
*Also rejected: route it through `_CORROBORATION_ASSERTION_CALLEES`.* `DN-14-2-1` forbids it and
§2.2 shows the false 🔴 it would manufacture.

**`DN-16-6-2` — the BARE `raise AssertionError` spelling is left invisible, DELIBERATELY, and the
decision is made EXECUTABLE.**
Measured **0 of 1,032**. Closing it needs a source-line scanner, which on the measured population
buys **zero** and — combined with the table entry — **double-counts all 22** (§2.1). *Rejected:
build the scanner anyway "for completeness".* Completeness that changes no measured outcome and
introduces a live double-count is a regression wearing a fix's clothes. *Rejected: record it in
prose only.* That was the previous round's mistake — `-133`'s own docstring says so. AC5.4 pins it
by execution and `DF-16-6-B` files it, so a later reader finds a **decision**, not a gap.

**`DN-16-6-3` — the guards go in a NEW `tests/test_vacuous_vocabulary.py`.**
Three homes were considered.
*Rejected: `tests/test_vacuous_density.py`* — subject-correct, but **1,159/1,200 with `DF-15-2-E`'s
trigger at 1,180**: 21 usable lines against a guard set many times that. Using it fires the
split-first rule and drags a **test-module split into a behaviour-change story**, which is exactly
what that rule exists to prevent (AC6.2).
*Rejected: `tests/test_vacuous_cross_language.py`* — it owns `DN-14-3-5` and `-133`, and has 169
lines free, so it is the closest call. But its declared subject is the **cross-language** vocabulary,
and `AssertionError` is a **Python** builtin: filing a Python-only name under a cross-language
heading is how a module's subject dissolves, and NFR-M1's remedy is *cohesion*, not free space.
*Selected:* the production split created **`argus/detectors/vacuous_vocabulary.py`** with **no test
module mirroring it**. A new `tests/test_vacuous_vocabulary.py` mirrors the split, has zero ceiling
pressure, is swept by the ceiling guard the moment it is `git add`-ed, and puts *"which names count
as an assertion?"* in one readable place — the same argument the production split itself made.

**`DN-16-6-4` — the committed corpus artifacts are NOT regenerated, and the `−7` lives in the story
and the ledger.**
*Rejected: re-run `scripts/audit_validation_corpus.py` so the recorded population reflects the fix.*
That is a **new measurement over five corpus members** — not authorised by this story, and it would
rewrite the set that the adjudication record's exhaustiveness check compares against. §2.3 measured
that it is also **unnecessary**: neither builder invokes a detector, and both return exit 0 with the
widened table in memory. The number is evidence **about** the fix, not an artifact **of** the corpus
run, and recording it as the latter would be a second measurement wearing the first one's name —
the exact failure `corpus_read_proof()`'s docstring names.

### ⛔ AMENDMENT 2026-08-23 — what the independent readiness validation changed, and why

This file **FAILED an independent readiness validation** and was amended in place. The status did
not move. ⛔ **The research was NOT touched.** The validator re-derived §0.3 and §0.4 over pinned
git objects and reproduced the **−7**, all seven named rows to the exact `Fraction`, the
22-with-zero-bare spelling census, both collision sites, and all ten of §0.6's line counts — and
proved **AC5 non-vacuous** (three of its five cases flip under AC5.1's mutation). **Every defect was
in this file's own TEXT.**

| # | Where | Defect | Repair |
|---|---|---|---|
| **A1** | §References | A disposition verb and three ledger ids on ONE physical line turned the whole suite RED — the **sole** cause, proven by driving the guard's own analyzers over the 78-story corpus with and without this file. | Line wrapped so no verb shares a physical line with an open id; §0.0's full-suite row re-measured **with this file on disk**; a writing rule added to §0.0. ⛔ **The guard was NOT amended — the guard is right and the record was wrong.** `DF-16-6-D` filed. |
| **A2** | Task 3.6 vs AC3.3 | The task ordered an assertion that **requires** the `argus/precision/**` import the AC forbids — the **AR7** fork. | `SECTION_5_CONDITIONS` struck from Task 3.6; AC3.3 discharged solely by Task 7.1's existing `tests/test_gate_*.py` run. |
| **A3** | Task 0.5 vs AC4.5 / §0.7 | The task demanded an **EMPTY** porcelain on corpus members, which §0.7 itself proves unsatisfiable. | Restated as a before/after **byte-identical** capture. |
| **A4** | AC5.1, §2.5, Task 4.3 | The same cleanliness-where-invariance-is-meant defect, on **this** repo, where the tree necessarily carries the story's own edits. | All three restated as invariance against a capture taken immediately **before** the mutation; Task 4.1 now takes that capture. |
| **A5** | AC1.5 | The census did not independently reproduce (**172 : 2 / 4,369** and **662 : 3 / 20,769** against the claimed **183 : 2 / 5,085**) and reused in-source columns that mean something else. | Inclusion rules now required; a **labelled** row required instead of the existing columns; the figures demoted to an expectation under AC4.4. |
| **A6** | §0.7, AC5.2 | A stale dirty-count, and an accepted-cost register moved away from `-133` with no cross-reference. | §0.7 now carries three same-day measurements and forbids asserting any of them; AC5.2 requires a bounded two-way docstring cross-reference, and AC6.1 carries the single bounded exception permitting it. |

**Five further divergences of the same shape, found by sweeping the ENTIRE task list for it:**

- **Task 0.1** asserted *"exactly two"* working-tree entries — already false (four artifacts) and
  unstable by construction. Restated as an invariant: **zero** entries under `argus/`, `tests/`,
  `scripts/`, `…/validation-corpus/`.
- **Task 2.2** mirrored AC1.5's defect exactly, ordering the figures into the existing columns.
  Repaired alongside AC1.5 — the same AC/Task twin shape as A2 and A3.
- **Task 7.2** wrote `validation-corpus/` **bare** — the precise ENOENT §0.0's PATH ROOTS block warns
  about two hundred lines earlier in this same file. Full path written out.
- **Task 7.3** verified the write set with `git diff --name-only`, which **cannot see** the story's
  main deliverable: `tests/test_vacuous_vocabulary.py` is a NEW **untracked** file. A check that
  passes while blind. Switched to `git status --porcelain`.
- **§2.4** cited §0.8 for a fact that lives in §0.9 (§0.8 is the verification-id section).

⛔ **THE PATTERN, recorded because it is the reusable lesson.** The author **self-caught A2 and A3,
fixed them in the ACs, and left the mirrors live in the Tasks.** A2, A3, A4, A5 and Task 2.2 are all
one class — *an AC repaired on one side of the file while its executable twin kept the defect.*
**When you amend an AC in this project, grep the task list for its twin before you stop.** That is
Epic 16's own proposition about self-validation, demonstrated on Epic 16's own story file.

**Decisions the amendment pass TOOK, with their rationale — no user was present to ask:**

1. **The census figures are DEMOTED to an expectation rather than re-derived.** Sound practice says
   an AC should state a contract. This project's own AC4.4 says **the tree wins** and the story is
   corrected against it. Project context wins: `DN-14-3-5` consumes the **ratio**, every candidate
   population clears it by two orders of magnitude, and pinning an unreproducible integer would
   manufacture the exact unsatisfiable AC that failed Story 16.5.
2. **`tests/test_vacuous_cross_language.py` gains a BOUNDED write-set exception.** AC6.1's fence is
   this story's strongest guarantee and widening it has a real cost. Against that: `-133` silently
   becomes a five-of-six register the moment AC5.2 lands, and `AI-E12-3`'s rule is that a record
   which no longer records everything is the defect this project files rather than tolerates.
   Bounded to **two docstring lines, no assertion changed**, with AC7.4 catching anything wider.
3. **`DF-16-6-B` was NOT taken by the amendment pass.** AC6.5 names it and the dev files it; taking
   it would have forced an AC edit for no gain. The two new entries took `-C` and `-D`.
4. **§0.7's disagreeing counts were KEPT, not corrected to a single number.** Three disagreeing
   same-day measurements are far stronger evidence for the invariance rule than any one right
   number, and §3.4's *strike, never erase* is this project's standing habit.
5. **Nothing was disposed of, promoted, ratified or regenerated by the amendment pass**, and
   `sprint-status.yaml` was not modified: the story was `ready-for-dev` before it and is
   `ready-for-dev` after it.

### ⛔ AMENDMENT 2026-08-23, PASS 2 — what the SECOND validation changed

Round 2 returned **CONCERNS**, not a failure. It re-derived by execution — not by reading the
amendment's claims — that all six round-1 findings are repaired rather than relocated, that the full
suite is **1,688 passed / 0 failed / exit 0** with the amended file on disk, that the ledger append is
**prefix-byte-identical** with the lone `CR` and the trailing newline intact, and that the analyzer's
disposition set is 35 both before and after. ⛔ **None of that was touched by this pass, and no
research figure moved.** Six items, all TEXT:

| # | Where | Divergence | Repair |
|---|---|---|---|
| **B1** | AC5.2 vs the task list | AC5.2's two-way docstring cross-reference — the whole point of A6's repair — was cited by **exactly one** task (3.4) that said nothing about it, and Task 7.3's expected porcelain omitted the file it edits. A dev would either skip it or trip its own scope check. | Task 3.4 now orders both directions with the two-line bound; Task 7.3 now names `tests/test_vacuous_cross_language.py` as EXPECTED. |
| **B2** | AC6.4 | Cited by **no task at all**. Nothing asked for `vacuous_test.__all__ == 9` or for the three re-exports being the SAME objects — the surface `4123931` created and `ba5e8df` had to repair, which fails silently. | New Task **3.6.1** names both assertions, with the AC3.3 boundary spelled out so it is not mistaken for the forbidden `argus/precision/**` import. |
| **B3** | §0.0 PATH ROOTS | The block written to prevent path errors **was itself wrong**: it placed `epics.md`, `architecture.md`, `deferred-work.md`, `precision-validation-protocol.md` and this story file under `validation-corpus/`. Measured, that directory holds only the corpus JSONs and the worklists. Task 6 ENOENTs. | Split into THREE explicit roots, with `deferred-work.md`'s real location called out. |
| **B4** | AC4.5 | Still asserted *"three of the five … are ALREADY DIRTY"* while §0.7 forbids asserting any such count, Task 0.5 says two, and round 2 measured a **fourth** answer the same day. A6's own honesty rule, unapplied to the AC A6 repaired. | The count is gone. The invariance contract — byte-identical before/after capture — is unchanged and remains the operative clause. |
| **B5** | AC4.4 / AC5.5 | AC1.5 delegates §0.5's census to AC4.4, whose text was scoped to §0.3 alone; AC5.5 binds *every* new case but only Tasks 3.2 and 3.5 carried the control. | AC4.4 widened to §0.3/§0.4/§0.5; a binding preamble added to Task 3 naming every subtask. |
| **B6** | Four stale phrasings | §0.0's *"and nothing else"* and Task 7.3's singular *"its validation report"* (there are two); §0.1's `except AssertionError:` row printed as a literal `[]` when a span still emits its other calls; this file's own header claiming the porcelain *"was empty before and after"*. | All four restated — open enumerations, and the ZERO-under-`argus/tests/scripts` invariant instead of emptiness. |

⛔ **THE MASKED EIGHTH INSTANCE, and why it is recorded rather than fixed here.** Round 2 found that
the round-1 validation report still carries the `DF-16-6-D` line shape — a disposition verb sharing a
physical line with an id the ledger does **not** genuinely back. It passes today only because
`ledger_closed_ids` reports that id as disposition-bearing from historical prose 962 lines above the
append, a **pre-existing analyzer false positive** confirmed identical against the HEAD blob. Pass 2
re-wrapped the offending line in that report (line breaks only — not one word, cite, figure or
verdict changed) and corrected `DF-16-6-D`'s evidence and its count of seven to **eight**. ⛔ **The
guard was NOT amended, and `ledger_closed_ids` was NOT repaired** — that repair is `DF-16-6-D`'s own
remedy (ii), it belongs to a future story, and the entry now warns in terms that whoever implements
it will **unmask** this instance and turn the suite RED unless the record is wrapped first.

**Decisions pass 2 TOOK — again, no user was present to ask:**

1. **`§0.7`'s heading and its three-column table were left alone.** Its own text already forbids
   asserting any column, and pass 1 decided (decision 4) that the disagreement IS the evidence.
   Only the **AC** — the operative side — was corrected, which is the narrowest edit that discharges
   the finding.
2. **AC6.4 got a TASK, not a rewrite.** Round 2 confirmed the property already holds on the tree, so
   the gap was executable coverage, not contract. Adding an assertion is cheaper and stricter than
   restating the AC.
3. **`§0.8`'s single named id (`-138`) was left as-is.** Round 2 rated it "not wrong; a dev will
   allocate", and inventing six more ids here would pin numbering the dev is better placed to choose.
4. **No new AC and no new §5 condition.** Every pass-2 repair lands in an existing AC or an existing
   task. `DN-14-2-1` stays LOCKED, `N` stays 5, the artifacts stay byte-unchanged, and
   `sprint-status.yaml` stays `ready-for-dev`.

### Locked decisions this story CITES rather than reopens

- **`DN-14-2-1`** — two assertion vocabularies, two questions; the frozen table is the moat. ⛔ **The
  single most load-bearing constraint in this story.**
- **`DN-14-2-3`** — the project-helper naming convention is a named predicate, not smuggled entries.
- **`DN-14-2-4`** — the tables are partitioned by QUESTION, never by LANGUAGE.
- **`DN-14-3-2` / `DN-14-3-3` / `DN-14-3-5`** — the collision rule and its measured applications.
  ⛔ **`Error` stays OUT** (164 : 0). Do not re-add it for symmetry while you are in this table.
- **`DN-3`** — one floor, resolved from the cartridge registry, never re-typed; `pytest.raises` is
  the **explicit** result-observing carve-out.
- **`DN-4`** — fact (b) depends on no assertion COUNT and no threshold. This story depends on that
  and does not extend it.
- **`DN-15-2-*`** — the detector's line decomposition IS the index's (`index_aligned_lines`).
- **§3.4** — amend by dated block; strike, never erase; append-only ledger.
- **§6 R2** — ratification, third-party fetch and role-filling are **operator acts**.

### Open ledger entries bearing on this story — verify against `deferred-work.md` on disk

| id | State | Bearing |
|---|---|---|
| `DF-13-5-A` | **OPEN, UNSPENT** | Untouched. Nothing spent, nothing expanded. Its re-review trigger is *16.6 + 16.7 done, or 2026-11-22*. |
| `DF-15-2-D` | **CLOSED 2026-08-22** by `4123931` + `ba5e8df` | ⛔ **Cited, NOT reopened. The split is DONE.** The vocabulary lives in `vacuous_vocabulary.py`. |
| `DF-15-2-E` | **OPEN, trigger NOT fired** | `tests/test_vacuous_density.py` **1,159/1,200**, trigger **1,180**. ⛔ **This story is the likeliest to move it — `DN-16-6-3` is how it does not.** Byte-unchanged. |
| `DF-16-6-A` | **OPEN** | Fact (b)'s mock-referencing clause dead over the corpus (0/1,032). Untouched — closing it promotes 6. |
| `DF-16-6-B` | **TO BE FILED by this story** | The bare-`raise` residual, 0/1,032. AC6.5. |
| `DF-16-5-A` | **OPEN** (filed 2026-08-23) | `argus/precision/gate_decision.py` 1,132/1,200. ⛔ **Not in the epic text. Put nothing there.** |
| `DF-16-5-B` | **OPEN** (filed 2026-08-23) | `tests/test_gate_independence.py` 1,127/1,200. ⛔ Same. |
| `DF-16-1-A` | **OPEN, unlanded** | Rule-class arm of §5 breadth. Untouched. |
| `DF-14-3-A/B/C` | **OPEN** | Go/TS tests largely unscored. Explains why this table's cross-language half is inert. Not this story's. |
| `DF-14-1-A` | **OPEN** | Fact (b) is a NAME-level proxy, not dataflow. Target story 6.2. Untouched. |
| `DF-14-3-H` | **OPEN** | `tests/test_vacuous_detector.py`. Byte-unchanged here. |
| `DF-16-6-C` | **OPEN** (filed 2026-08-23) | `deferred-work.md` is protected from CRLF normalisation by ONE lone `CR` byte rather than by a `.gitattributes` rule, and a re-save silently deletes a historical line. ⛔ **Read AC6.5's byte checks before Task 6.** The remedy is NOT implemented here. |
| `DF-16-6-D` | **OPEN** (filed 2026-08-23) | The line-scoped closure-claim trap — a disposition verb sharing a physical line with an open ledger id. ⛔ **It made THIS story's own baseline RED.** §0.0's writing rule is the interim remedy; the entry proposes the durable one. |

⛔ **Writing rule — `TC-ArgusAgent-DOCS-001-78`.** `deferred-work.md` is **append-only**, and a
closure must be machine-readable (the id on the closure line, or a trailing `- status:` field).
Edits to historical entries must be annotated, not silent — 16.1's review caught exactly that, and
the remedy was **restoration**, not annotation after the fact. This story **closes nothing**.

### Dependencies — none are added, and that is a requirement

No new package. No new import edge. `vacuous_vocabulary.py` imports **only** `re` and
`__future__.annotations` — **keep it that way**; it is a leaf module by design and the
import-isolation gate depends on it. No import from `argus/**` into `tests/**` (`DF-9-2-A`:
`tests/` is absent from the built distribution). The new test module imports the shipped detector,
never a reimplementation of it.

### Standing rules (non-negotiable)

- **AR7 / §3.3** — one arithmetic, one vocabulary, never forked. *"Two spellings of 'is this an
  assert line' is exactly the disagreement class this detector keeps closing elsewhere."*
- **AR8** — pure/impure separation; the detector path is pure, I/O lives in `scripts/`.
- **AR4** — ratios are exact `Fraction`s, never floats. `assertion_density` included.
- **NFR-P1** — no clock, randomness or network on any decision path; byte-stability of every surface
  this story does not intend to move.
- **NFR-P2** — the language conditional lives in `argus/index/`; the tables stay **FLAT** and
  language-agnostic. **No language field, sub-table or grouping key** may enter the detector — the
  groupings in the source are **comments**.
- **NFR-S1** — no source byte, no secret value, no absolute host path in any artifact. ⛔ The
  harness paths in §0.3/§0.5 are **absolute Windows paths**; they may appear in this story file and
  in a scratch script, and **must not** reach `deferred-work.md` or any committed artifact.
- **NFR-M1** — 1,200 physical lines per module. **Split, never shave, never exempt.**
- **`AI-E11-1`** — every guard asserts its population is non-empty **before** asserting anything
  about it.
- **`DF-10-4-E`** — an unregistered value RAISES; never defaulted, never tolerated.
- **`AI-E12-3` / `AI-E12-6`** — *a disposition recorded in prose and not in the ledger is not a
  disposition.*

### Previous-story intelligence — 16.1–16.4 (`done`), 16.5 (`done`, two review iterations)

1. **Every story in Epic 16 found a stated premise false by executing it**; 16.4 found three, one of
   which changed its plan. **This story already carries two: §0.2 (the precondition is discharged
   and the file has moved) and §0.3 (the number is −7, not −22). Expect a third.**
2. **⛔ Story 16.5 FAILED its readiness validation on three blocking defects** — an AC unsatisfiable
   inside its own byte-unchanged fence, two ACs that contradicted each other, and a motivating
   premise that was **factually false**. **All three were AC defects, not research defects.** This
   file's ACs were written after the measurement, against paths confirmed to exist at `6d48c15`.
   If you find a fourth, **the tree wins** — correct the story (AC4.4), never the code.
3. **The lockstep trap has fired four times.** §2.5 names this story's version: numerator and
   denominator both move when you add a `raise` line to a fixture.
4. **16.3's own mutation run caught one of its guards UNREAL.** **Expect to find one of yours.**
   AC5.1 and AC5.5 are written to make that specific failure detectable here.
5. **16.5's dev found the baseline RED when the story claimed GREEN**, costing a commit. §0.0 states
   the baseline as measured, with numbers. **Re-measure anyway — that is Task 0.**
6. **16.4 closed by DECISION, not by result** — HALT-1 declined, nothing ratified, `N` still 5, no
   detector run over a bench member. The live record is still the 2026-08-17 set of **31**.
7. **Two commits, not one, when a sha must be cited** — a commit cannot cite itself.
8. **`4123931` + `ba5e8df` are the current model for split-first discipline** — the split landed
   **alone and before** any behaviour change, and `52143eb` recorded the discharge afterwards.
   ⛔ **This story needs no split, so it makes no split commit.**

### Git intelligence

Epic 16's arc: `chore(story file + in-progress) → [refactor/test(split-first, ALONE)] → feat(the
change) → chore(regenerate artifacts) → docs(protocol/architecture/ledger) → docs(the review)`.
**This story's arc omits both bracketed steps**: no split is needed (§0.2) and no artifact is
regenerated (§2.3), so it is `chore → feat → docs`.

⛔ **Not one Epic 16 commit touches a `CANDIDATE_OUTPUT_PATHS` entry, and the epic's BINDING ORDERING
CONSTRAINT is intact.** This story adds no bench output, so it cannot break it — **verify that claim
with `tests/test_gate_ordering.py` rather than asserting it.**

### References

- [epics.md](../epics.md) — §Epic 16 (`## Epic 16` heading) and `### Story 16.6` heading. ⛔ **Its
  first Given is STALE — see §0.2.**
- [sprint-change-proposal-2026-08-22.md](../sprint-change-proposal-2026-08-22.md) — §1.3 (the
  defect), §1.4 (why nothing is promoted), §2.2 (sequencing — **precondition 2 is discharged**,
  precondition 1 is satisfied by 16.4 being terminal), §2.4 (what is not in scope), §3.2, §5.
  **APPROVED by XAgent007 2026-08-22.**
- [deferred-work.md](../deferred-work.md) — `DF-13-5-A`, `DF-15-2-E`, `DF-16-6-A`, `DF-16-6-C`,
  `DF-16-6-D`, `DF-16-5-A/B`, `DF-16-1-A`, `DF-14-1-A`, `DF-14-3-A/B/C/H`
  · `DF-15-2-D` — its disposition is recorded in the ledger, dated 2026-08-22 (§0.2).
  ⛔ **That last id sits on a line of its OWN, deliberately.** `story_closure_claims` is
  **line-scoped**, so a disposition word beside an open id reads as a claim about *every* id on
  that physical line. Before 2026-08-23 these were one line, and that one line was §0.0's RED.
  See `DF-16-6-D`, and §0.0's writing rule.
- [architecture.md](../architecture.md) — §Enforcement (**guard-adequacy clause**), NFR-M1, NFR-P1,
  NFR-P2, NFR-S1, AR4, AR7, AR8
- [precision-validation-protocol.md](../precision-validation-protocol.md) — §2 (roles; the
  **2026-08-22 dated block under V1.3** filling the QA Lead, **no `V1.4` row**), §5 (the seven
  conditions), §6 (R2 operator acts)
- Research (read-only harnesses, both validated in two directions):
  [`research/measure-vacuous-population-split.py`](../research/measure-vacuous-population-split.py),
  [`research/revalidate-fact-b-widening.py`](../research/revalidate-fact-b-widening.py),
  [`research/technical-argusagent-detector-categories-research-2026-08-21.md`](../research/technical-argusagent-detector-categories-research-2026-08-21.md)
- Stories [16.5](16-5-the-record-says-who-judged-and-whether-they-were-independent.md),
  [16.4](16-4-ratify-run-adjudicate-and-let-the-arithmetic-decide.md),
  [15.2](15-2-the-detector-and-the-index-agree-on-what-a-line-is.md),
  [14.3](14-3-the-assertion-vocabulary-crosses-the-languages-the-installer-ships.md),
  [14.2](14-2-the-density-scorer-counts-statements-and-knows-the-assertions.md),
  [14.1](14-1-a-verdict-eligible-vacuous-finding-proves-vacuity-not-mocking.md)
- Code: `argus/detectors/vacuous_vocabulary.py` (**the edit**) ·
  `argus/detectors/vacuous_test.py` (`_score`, `_sut_call_sites`, `_ast_corroborated`,
  `_count_bare_asserts`, `_count_statements`, `index_aligned_lines`) ·
  `argus/detectors/provenance_scan.py` (`opens_bare_assert`, `provenance_evidence`,
  `RESULT_OBSERVING_CONTEXT_CALLEES`) · `argus/index/ast_index.py` (`build_ast_index`) ·
  `tests/test_vacuous_{density,cross_language,detector,detector_index}.py` ·
  `tests/test_module_size_ceiling.py` (`_physical_line_count`, `_CEILING`, `_REMEDY`,
  `_EXEMPT_BY_DESIGN`) · `scripts/build_{gate_decision,adjudication_record}.py`

---

## Tasks & Subtasks

### ⛔ Task 0 — REPRODUCE §0 BEFORE WRITING ANYTHING

- [x] **0.1** Confirm HEAD, branch and working tree. Expected: branch
      `epic-16/discharge-df-15-2-d`, HEAD at or after **`6d48c15`**, and every
      `git status --porcelain` entry under `_bmad-output/design-artifacts/ArgusAgent/` — this story
      file, its validation report, `sprint-status.yaml`, `deferred-work.md`.
      ⛔ **Do NOT assert a COUNT of entries** (§0.0): they come and go between sessions, and the
      story was contexted, validated and amended in three separate passes. **Assert the invariant
      instead — ZERO entries under `argus/`, `tests/`, `scripts/` or `…/validation-corpus/`.**
      Anything under those four means the tree moved, and you re-read §0 against it before writing
      a line.
- [x] **0.2** Re-run **every** gate in §0.0's table and record each exit code and count. ⛔ **A
      `--check` exit `1` means an artifact was already stale before you touched anything, and that
      changes the plan — STOP and report.**
- [x] **0.3** Re-measure §0.2's line counts with the **ceiling guard's own** `_physical_line_count`
      (import it; do not re-implement it). Confirm `vacuous_vocabulary.py` **455**,
      `vacuous_test.py` **796**, `tests/test_vacuous_density.py` **1,159**.
- [x] **0.4** Re-derive §0.1's edge-emission table with a real `build_ast_index` over a scratch
      fixture. ⛔ **If `raise AssertionError("x")` does NOT emit an `AssertionError` edge on your
      machine, the whole fix shape is wrong — STOP and escalate (AC7.4).**
- [x] **0.5** Re-derive §0.4 (the **22**, spelling split) and §0.3 (the **−7**), read-only over
      **pinned git objects** into a **scratch tree**. Keep the harness out of the repo or under
      `_bmad-output/.../research/`; it writes nothing.
      ⛔ **INVARIANCE, NOT CLEANLINESS (AC4.5, §0.7).** Capture `git -C <member> status --porcelain`
      for every member **before** the re-derivation and again **after**, and assert the two captures
      are **byte-identical**. ⛔ **Do NOT expect them empty.** Two of the five were dirty when this
      amendment pass measured them and the counts moved three times in one day; an emptiness check
      fails for a reason nobody can fix, and a dev who "cleans" a member to satisfy it has mutated a
      ratified member (§2.6).
- [x] **0.6** Re-derive §0.5's collision census with **stdlib `ast`** (not Argus's index). ⛔ **State
      the population's INCLUSION RULES before you run it** — whether nested `.venv` /
      `site-packages` under a corpus checkout are walked, and whether a vendored duplicate of a
      third-party package folds into one site or counts twice — then record the population size and
      both counts **against that stated rule** (AC1.5). ⚠️ **Expect a number that is not 183.** An
      independent re-derivation measured **172 : 2 over 4,369** and **662 : 3 over 20,769** under
      the two obvious rules. `DN-14-3-5` consumes the **RATIO**, and 86× / 91× / 221× all clear it
      by two orders of magnitude; the absolute count is not the contract (AC4.4).
- [x] **0.7** Confirm §0.8's next free `TC-ArgusAgent-DETECT-001-NN`.
- [x] **0.8** Record every disagreement with §0 in Completion Notes. **The tree wins.**

### Task 1 — THE HEADROOM DECISION, TAKEN BEFORE THE FIRST LINE (AC6.2, `DN-16-6-3`)

- [x] **1.1** Confirm `tests/test_vacuous_density.py` is **1,159** and `DF-15-2-E`'s trigger is
      **1,180**. Confirm the guards are going into **new** `tests/test_vacuous_vocabulary.py`.
- [x] **1.2** ⛔ If you conclude the guards belong in `test_vacuous_density.py` after all, that
      **fires the split-first rule**: the split lands **ALONE and FIRST in its own commit** before
      any behaviour change. Do not do both in one commit. **Prefer `DN-16-6-3` and avoid the
      question.**
- [x] **1.3** ⛔ **No `_EXEMPT_BY_DESIGN` entry.** `MAINT-001-04` lets that registry shrink only.

### Task 2 — THE ONE NAME (AC1, AC2)

- [x] **2.1** Add `"AssertionError"` to `_ASSERTION_CALLEES` in
      `argus/detectors/vacuous_vocabulary.py`, in its own commented group.
- [x] **2.2** Write the `DN-14-3-5` block beside it: **your own** Task 0.6 benefit and cost, the
      population size **and the inclusion rules you stated**, both collision sites named, decision
      `✅ admitted` (AC1.5). ⛔ **A LABELLED row or an adjacent sub-note — do NOT reuse the existing
      `py collisions` / `js/ts benefit` columns.** Their population (4,046 files, three ratified
      members) and their semantics (all call sites; a JS/TS-only benefit, which for a Python builtin
      is 0) are both different, and reusing them records a false value in a table other people read
      as commensurable.
- [x] **2.3** ⛔ Touch **nothing else** in that file — the convention regex, the frozen table,
      `_MOCK_CALLEES` and both thresholds stay byte-unchanged (AC1.3/1.4/1.6).
- [x] **2.4** ⛔ **No scanner.** `provenance_scan.py`, `_count_bare_asserts` and `opens_bare_assert`
      stay byte-unchanged (AC2.1/2.2).
- [x] **2.5** Verify `is_assertion_callee("AssertionError") is True` and `len(...) == 89`.

### Task 3 — THE GUARDS (AC5, AC2.3/2.4, AC3)

⛔ **AC5.5 BINDS EVERY SUBTASK BELOW, not only 3.2 and 3.5.** Each new case states its non-vacuity
preamble **before** it asserts anything — the index really emitted the callee the case is about, and
`statement_count > 0` — and each carries the `statement_count`-pinned **control** that isolates the
NAME from the fixture's SHAPE (§2.5's lockstep trap). A case missing either half is not done
(AC5.5), and 3.3, 3.4, 3.6, 3.6.1 and 3.7 are in scope for it exactly as 3.2 and 3.5 are.

- [x] **3.1** Create `tests/test_vacuous_vocabulary.py` with a module docstring naming **why the
      module exists** (mirrors `argus/detectors/vacuous_vocabulary.py`; the split precedent) and the
      verification area.
- [x] **3.2** The **primary** case (`-138`): a Python test whose only assertion is
      `raise AssertionError("…")` scores `assertion_sites == 1`, density ≥ `1/4`, and is **NOT**
      flagged — with the `-133` non-vacuity preamble (the index emitted the `AssertionError` callee;
      `statement_count > 0`) and a **control** whose `statement_count` is asserted **equal**.
- [x] **3.3** The **double-count** cases (AC2.3, AC2.4).
- [x] **3.4** The **accepted collision cost** case (AC5.2): `AssertionError("x")` outside a `raise`
      scores `assertion_sites == 1` — the cost `DN-14-3-5` accepted, asserted rather than remembered.
      ⛔ **AND WRITE AC5.2's TWO-WAY CROSS-REFERENCE HERE — no other task orders it.** Add **at most
      two physical lines** of docstring or comment inside `-133`
      (`tests/test_vacuous_cross_language.py:617-621`) pointing at `tests/test_vacuous_vocabulary.py`,
      and **one line** in this new case pointing back at `-133`. ⛔ **No assertion, no fixture, no
      loop member and no import in that file may change** — that is AC6.1's single bounded exception,
      and anything wider is out of scope (AC7.4). Task 7.3 therefore EXPECTS
      `tests/test_vacuous_cross_language.py` in the porcelain. Skip this and `-133` silently becomes
      a five-of-six register the moment `AssertionError` is admitted (AC5.2, AC6.1, `DN-16-6-3`).
- [x] **3.5** The **bare-`raise` residual** case (AC5.4), docstring citing `DN-16-6-2` and the
      **0 of 1,032** measurement — **paired with the `pass`-bodied control AC5.4 requires**, scoring
      identically, so the case cannot pass by measuring the fixture's SHAPE instead of the NAME.
- [x] **3.6** The **containment** cases (**AC1.3, AC3.1, AC3.2, AC3.4** — note the range):
      frozen table 23, `ast_corroborated` unmoved on a **non-degenerate** population,
      `mock_ratio`/`call_sites`/`statement_count` byte-identical, direction one-way.
      ⛔ **AC3.3 IS NOT IN THIS TASK, AND `SECTION_5_CONDITIONS` MUST NOT BE ASSERTED HERE.**
      Asserting it inside `tests/test_vacuous_vocabulary.py` requires
      `from argus.precision.gate_decision import SECTION_5_CONDITIONS` — the exact import AC3.3
      forbids — and forks a guard `tests/test_gate_breadth.py:616` already owns, which is the
      **AR7** defect. **AC3.3 is discharged by Task 7.1 running the existing `tests/test_gate_*.py`,
      and by nothing else.**
- [x] **3.6.1** ⛔ **THE RE-EXPORT SURFACE (AC6.4) — the only task that covers it.** Assert
      `len(argus.detectors.vacuous_test.__all__) == 9`, and assert that importing
      `_ASSERTION_CALLEES`, `_CORROBORATION_ASSERTION_CALLEES` and `is_assertion_callee` **from
      `argus.detectors.vacuous_test`** yields the **SAME OBJECTS** (`is`, not `==`) as importing the
      same three names directly from `argus.detectors.vacuous_vocabulary`. ⛔ **This is the surface
      that breaks SILENTLY**: it is what `4123931`'s cohesion split created and what `ba5e8df` had to
      repair afterwards, and a shrunk `__all__` or a re-export rebound to a COPY would leave every
      other guard in this story green. Importing from `argus.detectors.**` is **not** the AC3.3
      prohibition, which is about `argus/precision/**` only (Task 3.6).
- [x] **3.7** The **generated adversarial variant** (AC5.6), closed over `_ASSERTION_CALLEES` itself,
      with its count asserted.

### Task 4 — DRIVE IT RED (AC5.1)

- [x] **4.1** `PYTHONDONTWRITEBYTECODE=1`, clear `__pycache__`. **Capture
      `git status --porcelain` NOW and keep it** — that capture, not emptiness, is 4.3's
      restoration contract (AC5.1).
- [x] **4.2** Remove `"AssertionError"` from the table. Run the new module. **Observe RED at the
      real seam.** Record the exact failure text.
- [x] **4.3** Restore. ⛔ **`git status --porcelain` BYTE-IDENTICAL to 4.1's capture — NOT empty**
      (AC5.1, §2.5). The tree already carries Task 2's edit, the new test module, this story file
      and `sprint-status.yaml`, so empty is unreachable for the whole story; byte-identical is both
      satisfiable and strictly stronger. Re-run **green**.
- [x] **4.4** Repeat for at least one more mutation of your choosing, and record it.

### Task 5 — RE-DERIVE AND RECORD THE NUMBER (AC4)

- [x] **5.1** Re-derive **22 / 12+10 / all-CALL-form / 1,032 → 1,025 / −7 / 0 newly flagged**, and
      the seven named rows.
- [x] **5.2** ⛔ **Write nothing.** No finding, verdict, disposition, adjudication set or gate
      artifact. No corpus working tree mutated — proven by Task 0.5's **before/after byte-identical
      porcelain captures**, re-taken around this re-derivation (AC4.5). ⛔ **Not by an emptiness
      check.**
- [x] **5.3** Record in Completion Notes. If a figure disagrees with §0.3, **correct the story**
      (AC4.4) — never the code.

### Task 6 — THE LEDGER (AC6.5)

- [x] **6.1** Append **`DF-16-6-B`** for the bare-`raise` residual: the measurement (**0 of 1,032**),
      why it is a decision and not a gap, severity, owner, target story. Machine-readable fields.
- [x] **6.2** ⛔ **Append only.** No historical entry edited. Nothing disposed of. No absolute host
      path (NFR-S1). ⛔ **Confirm `DF-16-6-B` is still the next free letter** — the amendment pass
      filed `DF-16-6-C` and `DF-16-6-D` and left `-B` for you.
- [x] **6.3** ⛔ **THE BYTE CHECKS (AC6.5, `DF-16-6-C`).** Append in **binary**, then assert: the
      count of **lone `CR`** bytes (a `\r` not followed by `\n`) in `deferred-work.md` is still
      **exactly 1**; the file still ends with a newline; and `git diff --numstat` reports
      **`+n / -0`**. A one-line deletion here is an append-only violation, and it has happened
      before (`9aea1be` → `a4de7e7`). ⛔ **Do NOT add `.gitattributes`** — that is `DF-16-6-C`'s
      proposed remedy and it is not this story's to implement.

### Task 7 — GATES AND HAND-OFF (AC6.3, AC7)

- [x] **7.1** Full suite with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`; coverage ≥80%; `mypy argus`
      (**CI scope — do NOT widen it to `scripts`, §0.0's caveat**); `bandit -r argus
      --severity-level medium`; `tests/test_module_size_ceiling.py`; `tests/test_gate_ordering.py`;
      and `tests/test_gate_*.py` for **AC3.3**. Record every exit code.
      ⛔ **`tests/test_gate_*.py` staying green IS AC3.3's whole discharge** — write no new assertion
      about `argus/precision/**` and import nothing from it into `tests/test_vacuous_vocabulary.py`
      (AC3.3, Task 3.6).
      ⛔ **`tests/test_governance_record_integrity.py` runs in this suite and it READS your story
      file and your ledger append.** Re-read §0.0's writing rule before you commit either: a
      disposition verb sharing a physical line with an open `DF-*` id turns this suite RED, and it
      is what made this story's own first baseline false (`DF-16-6-D`).
- [x] **7.2** ⛔ **Both builders `--check` → exit 0**, and confirm all three corpus artifacts are
      **byte-unchanged** — `git diff --stat` over
      **`_bmad-output/design-artifacts/ArgusAgent/validation-corpus/`** is **empty**. ⛔ **Use the
      full path**: `validation-corpus/` is NOT at the repo root, and the short form ENOENTs on its
      first line (§0.0's PATH ROOTS warning).
- [x] **7.3** Confirm the final write set equals AC6.1 exactly. ⛔ **Use `git status --porcelain`,
      NOT `git diff --name-only`** — `tests/test_vacuous_vocabulary.py` is a **NEW untracked** file
      that `git diff` cannot see, so that check would pass while blind to this story's main
      deliverable. Expect exactly AC6.1's set — ⛔ **including
      `tests/test_vacuous_cross_language.py`**, which carries AC5.2's bounded two-way cross-reference
      (Task 3.4) and is an EXPECTED entry rather than a scope breach — **plus** the pre-existing
      artifact entries §0.0 lists (this story file, **its validation reports: two or more, ⛔ do NOT
      assert a COUNT**, `sprint-status.yaml`, `deferred-work.md`), and **nothing** under
      `argus/precision/`, `scripts/` or `…/validation-corpus/`.
- [x] **7.4** Commit arc `chore → feat → docs`. **No split commit.**
- [x] **7.5** Completion Notes per AC7.3.

### Review Findings

#### Iteration 1 (2026-08-23) — as originally written, PRESERVED VERBATIM below

⚠️ **RECONCILIATION NOTE, added at iteration 2, 2026-08-23 — read this before the paragraph below.**
The sentence *"Verdict: pass"* immediately below is iteration 1's own text, unedited. It is
**inconsistent with the verdict iteration 1 actually enacted**: `sprint-status.yaml`'s
iteration-1 comment records `CONCERNS; review -> in-progress`, and this workflow's own
pass/concerns/fail mapping is unambiguous — an unresolved `[Review][Patch]` finding (the
`36`-vs-`58` miscount, unchecked at the moment iteration 1 finished writing findings) blocks `pass`
by definition, which is exactly why the story was sent back to `in-progress` for a fix round rather
than closed. So: the enacted, load-bearing verdict of iteration 1 was **CONCERNS**, not `pass`; the
word "pass" in the paragraph below is an iteration-1 authoring slip that was never corrected and is
left exactly as written, per the instruction to preserve iteration-1 history rather than silently
overwrite it. Iteration 2 (below the bullets) records the actual, current verdict.

Adversarial code review (Blind Hunter / Edge Case Hunter / Acceptance Auditor) against commits
`dd1e03a` · `6304552` · `6bb91ae`. Every claim below was checked by independent execution, not by
trusting the Completion Notes — full suite re-run (1,695 passed / 0 failed / exit 0), `mypy argus`
(94 files clean), `bandit -r argus --severity-level medium` (0 medium / 0 high), ceiling (6 passed),
`tests/test_gate_*.py` (58 passed — see Patch item below), governance-record integrity (green),
both builders `--check` (exit 0), the `-7` delta re-derived from scratch over the real 1,032
pinned findings (exact match, all seven rows to the `Fraction`), the `pytest.raises(AssertionError)`
non-edge claim reproduced live, the DOGFOOD regeneration re-run and confirmed renderer-produced, and
both mutations (remove the name; case-insensitive convention) driven RED and restored byte-exact.
**Verdict: pass.** No `decision-needed` or unresolved `patch` blocks acceptance; the two items below
are informational and do not gate `done`.

- [x] [Review][Patch] Completion Notes §7's gate table misreports `tests/test_gate_*.py` as "36
      passed" [stories/16-6-…-raise.md:§7 Gates table]. Independently re-run: `pytest
      tests/test_gate_*.py -v` collects and passes **58** tests across all nine
      `test_gate_*.py` files (breadth 5, condition_lookup 2, decision 8, decision_artifact 7,
      flip_path 7, independence 10, ordering 4, seal 9, yield 6 = 58), none of which were touched
      by this story and all of which predate its baseline commit `6d48c15`. AC3.3's discharge
      still holds (the suite is green either way), so this is a reporting-accuracy defect in the
      story's own record, not a functional one — the same shape as the already-known
      sprint-status "182 vs 109 keys" miscount. Fix: correct the figure to 58 in Completion Notes
      §7 (or state the narrower selection actually run, if one was intended) — trivial text-only
      patch, no re-test needed.
- [x] [Review][Defer] The `Evidence-partition: open` trailer citation for a `partition: pre-seal`
      corpus is a genuine, disclosed protocol gap, not a defect this story should fix
      [argus/detectors/vacuous_vocabulary.py commit `dd1e03a` trailer]. Confirmed by reading
      `argus/precision/gate_seal.py`: `SEAL_CITATION_VALUES = (sealed, open, none)` has no
      `pre-seal` member, `cites_partition` only regex-matches the commit body against those three
      literal strings, and `corpus_partition_counts` is computed independently of any commit
      trailer — so citing `open` cannot corrupt any downstream computed state, it only satisfies
      (truthfully, if awkwardly) a citation predicate that was never given a fourth option. The
      judgement is disclosed in the commit body rather than smoothed over, which is the correct
      behavior under AC7.4's escalation list (this exact gap is not one of the listed escalation
      triggers). Deferred rather than patched here because widening `SEAL_CITATION_VALUES` is a
      protocol-owner decision outside this story's scope (AC7.4) — deferred, pre-existing gap in
      the seal-citation vocabulary, surfaced for whoever owns `argus/precision/gate_seal.py`'s
      protocol.
- [x] [Review][Defer] `tests/test_gate_seal.py::_git` decodes git subprocess output with
      `text=True` and no `encoding=`, so it uses the locale codec (cp1252 on this Windows box);
      reproduced independently in an isolated scratch repo — a commit message containing a
      character outside cp1252 (e.g. `ā`, U+0101) makes the stdout-reader thread raise
      `UnicodeDecodeError`, `CompletedProcess.stdout` comes back `None`, and
      `cites_partition(None)` at `tests/test_gate_seal.py:1140` raises `TypeError` (not merely a
      theoretical claim — reproduced by execution) instead of reading the trailer. Confirmed
      Windows-only and invisible to the ubuntu CI leg (UTF-8 locale decodes cleanly). Confirmed no
      commit in this diff trips it: `dd1e03a`, `6304552` and `6bb91ae` are all pure ASCII by
      execution (`.decode('ascii')` succeeds on all three `git log --format=%B` outputs). Correctly
      left unfixed — amending the guard is out of this story's scope (AC7.4) and the orchestrator's
      brief records it will be filed to the ledger separately — deferred, pre-existing, real.

#### Iteration 2 (2026-08-23) — re-review of fix round 1 (`d6625b5`), against `dd1e03a` · `6304552`
      · `6bb91ae` · `d6625b5`, baseline `6d48c15`

**Every claim below was checked by independent execution against the tree as it stands now, not by
trusting the Completion Notes or iteration 1's write-up.**

- **The one iteration-1 `[Patch]` finding is CONFIRMED FIXED.** Independently re-ran
  `pytest tests/test_gate_breadth.py tests/test_gate_condition_lookup.py tests/test_gate_decision.py
  tests/test_gate_decision_artifact.py tests/test_gate_flip_path.py tests/test_gate_independence.py
  tests/test_gate_ordering.py tests/test_gate_seal.py tests/test_gate_yield.py -v` myself: **58
  passed, exit 0**, matching the corrected figure now in §7's table and the Change Log. Fix round 1's
  own diff (`d6625b5`) touches only the story record and `sprint-status.yaml` — confirmed by `git
  show --stat d6625b5`, no `argus/`, `tests/`, `scripts/` or `…/validation-corpus/` path in it. This
  was a record-accuracy fix, correctly scoped, correctly executed, and independently reproduces.
- **Both iteration-1 `[Defer]` findings were re-confirmed real by independent execution** (not
  re-trusted): `argus/precision/gate_seal.py`'s `SEAL_CITATION_VALUES` is read directly and contains
  exactly `(PARTITION_SEALED, PARTITION_OPEN, "none")` — no `pre-seal` member; and
  `tests/test_gate_seal.py::_git` is read directly and confirmed to call `subprocess.run(...,
  capture_output=True, text=True, timeout=120)` with no `encoding=` argument, at
  `tests/test_gate_seal.py:1012-1019`. Both remain correctly out of this story's fence under AC7.4:
  neither is caused by this story's diff, neither corrupts computed state or an AC's discharge, and
  fixing either here would be exactly the AR7/scope-creep shape this epic's guards exist to prevent.
- ⛔ **PROCESS GAP FOUND AND CLOSED BY THIS REVIEW ROUND.** Both `[Defer]` findings were correctly
  triaged by iteration 1 but **never filed to `deferred-work.md`** — fix round 1's own commit message
  discloses this explicitly ("both are being filed separately, outside this story's write-set fence")
  but no separate filing commit followed, and `grep` for their subject matter in `deferred-work.md`
  returned zero hits before this round. Filing a `defer` finding to the ledger is this review
  workflow's own step (not the dev's), so this iteration files them now: **`DF-16-6-E`** (the
  `SEAL_CITATION_VALUES` `pre-seal`-citation gap) and **`DF-16-6-F`** (the `tests/test_gate_seal.py`
  cp1252 decode bug) are appended to `deferred-work.md` under a new dated heading, filed with the
  same byte-invariant discipline `DF-16-6-C` requires (lone-`CR` count 1 → 1, `git diff --numstat`
  `+79/-0`, no CRLF introduced, trailing newline intact — verified by execution both before and
  after the append). No existing ledger entry is edited and no `DF-*` other than `-E`/`-F` is
  created.
- **Independent full re-verification, this round, by execution — not copied from any prior record:**

  | Gate | Command | Result | Exit |
  |---|---|---|---|
  | Table state | `is_assertion_callee("AssertionError")`, `len(_ASSERTION_CALLEES)`, `"AssertionError" in _CORROBORATION_ASSERTION_CALLEES`, `len(_MOCK_CALLEES)` | `True`, **89**, `False`, **10** | n/a ✅ |
  | Full suite | `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 pytest` | **1,695 passed**, 241.56s | **0** ✅ |
  | Types | `mypy argus` (CI scope) | *"Success: no issues found in **94** source files"* | **0** ✅ |
  | Security | `bandit -r argus --severity-level medium` | Low 20, **Medium 0, High 0** | **0** ✅ |
  | Ceiling | `pytest tests/test_module_size_ceiling.py` | **6 passed** | **0** ✅ |
  | AC3.3 | `pytest tests/test_gate_*.py` (all nine) | **58 passed** | **0** ✅ |
  | Governance | `pytest tests/test_governance_record_integrity.py` | **3 passed** | **0** ✅ |
  | New module | `pytest tests/test_vacuous_vocabulary.py` | **7 passed** | **0** ✅ |
  | Collateral | `pytest tests/test_vacuous_cross_language.py tests/test_vacuous_density.py tests/test_vacuous_detector.py tests/test_vacuous_detector_index.py` | **51 passed**, no regression | **0** ✅ |
  | Builder | `python scripts/build_adjudication_record.py --check` | *"current (**31** row(s))"* | **0** ✅ |
  | Builder | `python scripts/build_gate_decision.py --check` | *"CURRENT — BLOCKED"* | **0** ✅ |

- **AC-by-AC spot audit, by reading the shipped code and the shipped test module (not the prose
  describing them):** AC1.1–AC1.3/AC1.6 confirmed by direct interpreter execution (table above).
  AC1.4 confirmed unchanged (`_ASSERTION_NAMING_CONVENTION.pattern == r"\A_?assert\w*\Z"`, asserted
  by `-142`). AC1.5's `DN-14-3-5` block is a labelled sub-note naming its own population and axes
  (`python benefit (in-raise sites)` / `python collisions (non-raise sites)`) rather than a row of
  the existing table at `vacuous_vocabulary.py:290` — read directly, confirmed correctly separated.
  AC2 (`-139`) varies only the callee name with the denominator pinned via an explicit control
  fixture, and asserts `assertion_sites` (not the flag) exactly where AC2.4 requires — read the test
  body directly, confirmed non-vacuous. AC3.1 (`-142`) asserts `corroborated_seen >= 1` as an
  explicit non-vacuity floor before drawing any "unmoved" conclusion (the `AI-E3-1` shape this
  project has shipped before) — confirmed present and correct. AC3.2–AC3.4 read directly in the same
  case. AC5.1's mutation evidence (six of seven RED, full pre-existing vacuous suite green under the
  same mutation, `git status --porcelain` byte-identical before/after) is recorded with the actual
  failure text in Completion Notes §4 — this is real seam mutation via `monkeypatch.setattr` on the
  module global, not a reconstruction. AC6 module placement (`tests/test_vacuous_vocabulary.py`, new,
  per `DN-16-6-3`) confirmed to exist and pass; `tests/test_vacuous_density.py` confirmed
  byte-unchanged (not touched by this story's diff). No AC found unmet; no High/Medium-severity
  defect found in the implementation or the tests.
- **No new `decision-needed` or `patch` finding.** Nothing beyond the two now-filed `defer` items
  above.

**VERDICT: PASS.** All ACs independently verified met, tests/lint/build green by fresh execution,
no unresolved `decision-needed`/`patch`/High/Medium finding remains. The two `defer` items are
Low-severity, pre-existing, correctly out of this story's scope, and now properly filed to the
ledger. Story moves to `done`.

### Agent Model Used

Claude Opus 5 (1M context) — `claude-opus-5[1m]`, BMAD `dev-story`, `mode=implement`, 2026-08-23.

### Debug Log References

All measurement harnesses were kept **out of the repository**, under the session scratchpad, and
write nothing:

- `rederive.py` — walks all 1,032 recorded `vacuous_test_heuristic` findings from their PINNED git
  objects into a scratch tree, scores each span through a real `build_ast_index` + the real
  `VacuousTestDetector._score` under the 88-name and 89-name tables, and captures
  `git -C <member> status --porcelain` **before and after** for all five members.
- `census.py` — the `DN-14-3-5` collision census with stdlib `ast`, inclusion rules R1–R5 stated in
  its own docstring **before** it runs.

Mutation runs were driven under `PYTHONDONTWRITEBYTECODE=1` with every `__pycache__` outside
`.venv` removed first, against a `git status --porcelain` capture taken immediately before each
mutation.

### Completion Notes List

#### 1. What was implemented

**One name.** `"AssertionError"` joined `_ASSERTION_CALLEES` in
`argus/detectors/vacuous_vocabulary.py` — **88 → 89** — in its own commented group, carrying a
`DN-14-3-5` block written as a **LABELLED sub-note** rather than as a row of the existing table
(AC1.5: that table's `py collisions` / `js/ts benefit` columns are a different population with
different semantics, and a JS/TS benefit for a Python builtin is 0 by construction). The diff over
that file is **`+79 / -0`** — a pure insertion, which is what *proves*
`_CORROBORATION_ASSERTION_CALLEES`, `_ASSERTION_NAMING_CONVENTION`, `_MOCK_CALLEES`,
`ASSERTION_DENSITY_FLOOR` and `MOCK_RATIO_CEILING` byte-unchanged (AC1.3/1.4/1.6) rather than
merely asserting it.

**No second scanner.** `argus/detectors/provenance_scan.py`, `_count_bare_asserts` and
`opens_bare_assert` are byte-unchanged (AC2.1/2.2) — `git status --porcelain` carries no entry for
either file.

**Seven new guards** in a NEW `tests/test_vacuous_vocabulary.py`
(`TC-ArgusAgent-DETECT-001-138`..`-144`), per `DN-16-6-3`. `tests/test_vacuous_density.py` is
**byte-unchanged at 1,159 lines**, so `DF-15-2-E`'s 1,180 trigger does not fire and no split was
dragged into a behaviour-change story (AC6.2). No `_EXEMPT_BY_DESIGN` entry was added.

#### 2. §0 re-derived by execution — every figure reproduced, with THREE recorded disagreements

| Premise | §0 said | Measured here | Verdict |
|---|---|---|---|
| Baseline full suite | 1,688 passed / 0 failed / exit 0 | **1,688 passed, exit 0** | ✅ exact |
| `mypy argus` (CI scope) | clean, 94 files | **Success, 94 source files** | ✅ exact |
| `bandit -r argus --severity-level medium` | no issues | **Medium 0, High 0**, exit 0 | ✅ exact |
| Ceiling guard | 6 passed | **6 passed** | ✅ exact |
| Both builders `--check` | exit 0, 31 rows, `BLOCKED` | **exit 0 / 31 row(s) / BLOCKED** | ✅ exact |
| `vacuous_vocabulary.py` / `vacuous_test.py` / `test_vacuous_density.py` | 455 / 796 / 1,159 | **455 / 796 / 1,159** | ✅ exact |
| §0.1 edge emission | the call form emits an edge; the bare form does not | **reproduced row-for-row, all six** | ✅ exact |
| Findings walked | 1,032, 0 unresolvable | **1,032, 0 unresolvable** | ✅ exact |
| Carrying the idiom | 22; minions 12 + agent-smith 10; other three 0 | **22; 12 + 10; 0** | ✅ exact |
| Spelling census | all CALL form, 0 bare | **22 findings / 26 raise nodes, 0 bare, 0 attribute** | ⚠️ see (a) |
| Flagged before → after | 1,032 → 1,025, **-7**, newly flagged 0 | **1,032 → 1,025, -7, 0** | ✅ exact |
| The seven un-flagging rows | named, with `Fraction`s | **all seven, to the exact `Fraction`** | ✅ exact |
| Affected-but-still-flagged | 15 | **15** | ✅ exact |
| §0.5 collision census | 183 : 2 over 5,085 files, 91× | **182 : 2 over 5,086 files, 91×** | ⚠️ see (b) |
| Both collision sites | `stevedore/tests/test_extension.py:118`, `tests/test_open_llm_adapter.py:391` | **both reproduce exactly** | ✅ exact |
| Next free `TC-…-DETECT-001-NN` | 138 | **138** (highest in tree is 137) | ✅ exact |
| §0.7 corpus dirt | *"a dated OBSERVATION — assert none of it"* | **two more disagreeing answers, same day** | ⚠️ see (c) |
| §0.9 *"no existing guard detects the change"* | identically green | **confirmed by execution** | ✅ exact |

**(a) A UNIT nuance, not a disagreement.** §0.4's table is keyed *Findings* and reads 22 / 0 / 0.
That is correct as written. The finer count is that those 22 findings contain **26**
`raise AssertionError(...)` nodes between them — some spans raise more than once. Bare: **0**.
Attribute form: **0**. The 26 is recorded so a later re-derivation counting NODES rather than
FINDINGS does not read a discrepancy into §0.4.

**(b) §0.5's absolute figures do not independently reproduce, and AC4.4 says the tree wins.**
Under inclusion rules stated **before** the run — roots: the Argus tree + the five corpus checkouts
with `.venv` / `venv` / `site-packages` / `node_modules` pruned, plus this environment's
`site-packages` and the CPython 3.11 stdlib walked whole; de-duplicated by resolved absolute path;
0 unparseable — the census measures **182 in-`raise` : 2 non-`raise` over 5,086 unique `*.py`
paths**, against §0.5's **183 : 2 over 5,085**. The corpus checkouts are live working trees nobody
in this story controls and they moved between measurements. `DN-14-3-5` consumes the **RATIO**,
which is **91×** either way and clears the rule by two orders of magnitude, so the DECISION is
untouched. The **re-derived** figures — not §0.5's — are what went into the in-source block, with
their inclusion rules stated beside them, and the disagreement is written there too.

**(c) §0.7's dirty-count table now has more disagreeing same-day answers, which IS the finding.**
Measured here across two runs: minions **9 → 11**, agent-smith **0 → 1**, xagents-webapp **1**,
agent-markovich **0**, ai-body-runtime **0**. §0.7 already forbids asserting any of its columns and
this is further confirmation of why. **Invariance held on every run**: the before/after porcelain
captures were **byte-identical for all five members**, on both the Task 0.5 and the Task 5
re-derivations (AC4.5). No corpus working tree was mutated.

**A fourth item, and it is a divergence of the ORCHESTRATOR's brief rather than of §0:** the brief
states `sprint-status.yaml` carries **109** keys. Measured: `development_status` carries **182**
keys. All 182 are preserved, along with every comment and the STATUS DEFINITIONS block.

#### 3. THE NUMBER — re-derived twice, before and after the fix landed

```
recorded vacuous_test_heuristic findings walked : 1032      unresolvable: 0
...carrying a `raise AssertionError` (any form) : 22        minions 12 + agent-smith 10
spelling census                                 : 22 findings / 26 call-form nodes, 0 bare
FLAGGED before (88-name table)                  : 1032
FLAGGED after  (89-name table)                  : 1025
DELTA                                           : -7
NEWLY flagged (the forbidden direction)         : 0
assertion_sites fell anywhere                   : 0
affected-but-still-flagged                      : 15
```

The seven, measured to the exact `Fraction` and identical to §0.3:

| Member | Locator | Before | After |
|---|---|---|---|
| agent-smith | `agentsmith-core/tests/test_regression_alarm.py:493` | `1/6` | `1/4` |
| agent-smith | `agentsmith-core/tests/test_surface_accept.py:165` | `6/25` | `7/25` |
| agent-smith | `agentsmith-core/tests/test_surface_envelope.py:223` | `0` | `1/4` |
| minions | `tests/apaa/test_budget_exhaustion.py:329` | `1/6` | `1/4` |
| minions | `tests/apaa/test_critical_subsystems.py:268` | `1/6` | `1/4` |
| minions | `tests/apaa/test_insufficient_coverage_floor.py:435` | `1/6` | `1/4` |
| minions | `tests/cost/test_preflight_variance.py:112` | `1/7` | `2/7` |

#### 4. THE MUTATION — AC5.1's RED, observed, and the restoration proved by INVARIANCE

**Mutation 1 (AC5.1's own): remove `"AssertionError"` from `_ASSERTION_CALLEES`.**
**SIX of the seven new cases went RED at the real seam** — against a real `build_ast_index` and the
real scorer, never a reconstruction. `-138`'s observed failure text:

```
E  AssertionError: `AssertionError` no longer counts as an assertion. It was admitted under
   DN-14-3-5 on a measured 182 in-`raise` sites against 2 non-`raise` collisions (91x) over
   5,086 Python files, and it un-flags 7 of the 1,032 recorded findings. Removing it re-opens
   a false accusation against every test that asserts by raising.
E  assert False is True
E   +  where False = is_assertion_callee('AssertionError')
```

RED: `-138`, `-139`, `-140`, `-142`, `-143`, `-144`. GREEN by design: `-141`, the bare-`raise`
residual — that case is *supposed* to read identically under both tables, and its `pass`-bodied
control is what stops it passing by measuring the fixture's shape.

⛔ **And the whole point of AC5, confirmed by execution:** under the SAME mutation,
`tests/test_vacuous_density.py`, `tests/test_vacuous_cross_language.py`,
`tests/test_vacuous_detector.py`, `tests/test_vacuous_detector_index.py` and
`tests/test_module_size_ceiling.py` ran **55 passed, fully green**. §0.9's claim is exact: **no
pre-existing guard can see this fix.** The new module is the only thing standing between the fix
and a silent revert.

**Mutation 2 (Task 4.4, chosen): make `_ASSERTION_NAMING_CONVENTION` case-INSENSITIVE** — the
`DN-16-6-1` alternative this story REJECTED. Three cases went RED, including `-144`'s generated
sweep (230 surviving near-miss variants against a table-derived floor of 267) and `-138`'s live
pre-16.6 arm.

**Restoration, on both mutations:** `git status --porcelain` was captured immediately before each
mutation and compared byte-for-byte after each restore, with `__pycache__` cleared on both sides.
**BYTE-IDENTICAL both times** (AC5.1 — invariance, never emptiness; the tree necessarily carries
this story's own edits throughout, so "empty" was unreachable for the whole story). The module was
re-run green after each restore.

#### 5. A defect found in this story's OWN guards, before the gates saw it

Two of the seven cases were **written wrong and caught by execution**, which is the outcome
Previous-story-intelligence item 4 predicted:

1. `-143`'s negative control read `frozenset(x) is not x`. **`frozenset(x)` RETURNS `x` when `x` is
   already a frozenset** (a CPython interning optimisation), so the control asserted a falsehood,
   and the `is` checks it exists to justify would have been unfalsifiable. Rebuilt through an
   intermediate iterable so the copy is genuinely a second object, with the reason written into the
   comment beside it.
2. `-144`'s adversarial set required the guard to REJECT `assertionerror`. Measured: the SHIPPED
   case-sensitive convention `\A_?assert\w*\Z` **already admits** the all-lowercase spelling — it
   reads as a project helper. That spelling was never the defect; the **capitalised builtin** was,
   and it is the only thing this story moved. Recorded in the case rather than smoothed away, and
   it sharpens `DN-16-6-1`: it is `ASSERTIONERROR`, `MyAssertionError` and `AssertionErrorish` that
   a case-insensitive regex would wrongly admit.

`-144`'s non-vacuity floor was also re-derived from the table (`3 × len(_ASSERTION_CALLEES)` = 267,
measured 283) rather than left as a typed constant, so the sweep is required to grow with the
vocabulary.

#### 6. The ledger append, and its byte checks

`DF-16-6-B` was verified still free on disk (one mention only, in `DF-16-6-C`'s neighbouring prose
reserving it) and appended **in binary**. Measured before and after: lone-`CR` count **1 → 1**; the
file still ends with a newline; the HEAD blob is still a **strict prefix** of the working file and
the preceding bytes are **verbatim identical**; `git ls-files --eol` still reports
`i/-text w/-text`; `git diff --numstat` reports **`+207 / -0`** (the amendment pass's `-C`/`-D`
appends plus this one, zero deletions). No historical entry was edited, no `.gitattributes` was
added, and no `DF-*` other than `-B` was created or disposed of.

⛔ **The closure-claim trap (`DF-16-6-D`) was checked by eye AND by driving the guard's own pure
analyzer over everything this story wrote.** `story_closure_claims` extracts **zero** claims from
`tests/test_vacuous_vocabulary.py`, from `argus/detectors/vacuous_vocabulary.py` and from this
story's ledger append; the story file's single claim (`DF-15-2-D`) is pre-existing from the
create-story pass and the ledger backs it. No disposition verb was placed on a physical line with
an open id anywhere in this story's writing.

#### 7. Gates — every one run, every exit code recorded

| Gate | Command | Result | Exit |
|---|---|---|---|
| Full suite | `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 pytest` | **1,695 passed, 0 failed** (baseline 1,688 + the 7 new cases) | **0** ✅ |
| Coverage | `pytest --cov=argus --cov-fail-under=80` | **95.55%** (7,095 stmts, 316 missed) — the baseline figure, held | **0** ✅ |
| Types | `mypy argus` (**CI scope**, deliberately not widened) | Success, **94** source files | **0** ✅ |
| Security | `bandit -r argus --severity-level medium` | No issues (Medium 0, High 0) | **0** ✅ |
| Ceiling | `pytest tests/test_module_size_ceiling.py` | **6 passed**; no `_EXEMPT_BY_DESIGN` entry added | **0** ✅ |
| Ordering | `pytest tests/test_gate_ordering.py` | green — no `CANDIDATE_OUTPUT_PATHS` entry touched | **0** ✅ |
| **AC3.3** | `pytest tests/test_gate_*.py` — the selection is **all NINE** `tests/test_gate_*.py` files (`breadth`, `condition_lookup`, `decision`, `decision_artifact`, `flip_path`, `independence`, `ordering`, `seal`, `yield`) | **58 passed** — ⚠️ **CORRECTED in fix round 1 from a misreported "36 passed"** (§9 below; reviewer `[Patch]` item). Re-measured by execution 2026-08-23: **5 + 2 + 8 + 7 + 7 + 10 + 4 + 9 + 6 = 58**, `58 passed in 3.24s`. `SECTION_5_CONDITIONS` stays **7** and `precision_evaluable` keeps **4** conjuncts. **Discharged by these existing guards and by nothing this story wrote**: `argus.precision` is not imported by the new module (AR7). | **0** ✅ |
| Governance | `pytest tests/test_governance_record_integrity.py` | green with this story file and the ledger append on disk | **0** ✅ |
| Builder | `python scripts/build_adjudication_record.py --check` | *"the adjudication record is current (**31** row(s))"* | **0** ✅ |
| Builder | `python scripts/build_gate_decision.py --check` | *"CURRENT — **BLOCKED** (NOT COMPUTED BY THIS RUN)"* | **0** ✅ |

**Module sizes at the end**, measured with the ceiling guard's own `_physical_line_count`:
`argus/detectors/vacuous_vocabulary.py` **534** / 1,200 (was 455) ·
`tests/test_vacuous_cross_language.py` **1,033** / 1,200 (was 1,031; +2 comment lines) ·
`tests/test_vacuous_vocabulary.py` **NEW, 757** / 1,200 ·
**`tests/test_vacuous_density.py` 1,159 — BYTE-UNCHANGED**, so `DF-15-2-E`'s 1,180 trigger is 21
lines away and did not fire.

**Corpus artifacts:** `git status --porcelain` over
`_bmad-output/design-artifacts/ArgusAgent/validation-corpus/` is **EMPTY** —
`adjudication-record.json`, `adjudication-set-13-5.json` and `gate-decision-record.json` are all
**byte-unchanged** (AC6.3).

#### 7b. ⛔ THREE THINGS THE STORY DID NOT FORESEE — the "expect a third" that arrived

Previous-story-intelligence item 1 says *every story in Epic 16 found a stated premise false by
executing it* and *"expect a third"*. Three arrived, none of them in §0's research, all three in
what the ACs did **not** cover. All three were resolved inside domain authority and are recorded
here rather than smoothed.

**(i) `AC6.1`'s write-set fence is UNSATISFIABLE alongside `AC7.1`, and the tree wins.**
The `+79` lines took `argus/`'s total physical LOC from **32,555 → 32,634**, and the three
committed **dogfood** artifacts cite that number as the build-cost proxy every budget figure folds
from. `tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation`
and `tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run` went
**RED**. ⛔ **ANY line added to `argus/` moves that number, and this story's only possible
deliverable is a line added to `argus/`** — so AC6.1's *"everything else is byte-unchanged"* and
AC7.1's green suite cannot both hold as written. This is the Story 16.5 defect class (an AC
unsatisfiable inside its own fence), caught here by execution.

⚠️ **§2.3 and §Git-intelligence are NOT wrong — they are about a different artifact set.** *"No
artifact is regenerated"* is stated about the **CORPUS** artifacts (`adjudication-record.json`,
`adjudication-set-13-5.json`, `gate-decision-record.json`), and those are **byte-unchanged**, as
AC6.3 requires and as §7 above records. These are the **DOGFOOD** artifacts, a set the story never
considered — even though §0.2 itself records that `4123931` re-armed four currency guards and
`ba5e8df` had to repair them in a separate commit.

**Resolved by the project's own documented remedy**, which every one of those guards prints in its
own failure message: `python scripts/regenerate_dogfood_artifacts.py`. It renders each artifact
through its **OWN renderer** and re-reads it to assert byte-equality, so no `.md` was hand-edited
and no assertion was loosened (`DF-8-5-B`: *"Do not close it by loosening an assertion"*). It also
**refuses to run on a dirty `argus/` tree**, which forces exactly the ordering §0.2 describes: the
behaviour change lands **alone and first**, the artifacts follow in their **own** commit. The diff
is **3 lines per artifact** — the LOC figure and the provenance sha. **This adds a `chore` step to
AC7.2's commit arc that the story says it omits**, and the arc is therefore
`feat → chore(regenerate) → docs`.

**(ii) `TC-ArgusAgent-PRECISION-001-94` — this is the FIRST post-seal commit to touch a declared
detector-tuning path, and the trailer vocabulary has no value for the corpus we actually have.**
`argus/detectors` is a `DETECTOR_TUNING_PATHS` entry, so the `feat` commit must carry a whole-line
`Evidence-partition: sealed | open | none` trailer. Measured: **all five ratified members carry
`partition: pre-seal`**, and the counts are **0 sealed / 0 open / 5 pre-seal**. `pre-seal` is
**not** in `SEAL_CITATION_VALUES`.

- `none` — *"no corpus evidence informed it at all"* — is **false**: the corpus findings sized the
  `-7`, and the spelling census (22 call / 0 bare) is what decided the fix shape.
- `sealed` is **false and would corrupt the very record the rule exists to build**: it would
  disclose that a holdout was peeked at, and there is no holdout — `partition_meaning('pre-seal')`
  says Argus output over the member *"ALREADY EXISTED when the seal was taken"*, so the member is
  **excluded** from being one.
- `open` is the nearest true value: the non-holdout side, *"the partition tuning happens against"*.

**Decision, taken inside domain authority and disclosed in the commit body itself:**
`Evidence-partition: open`, cited **in that sense only and NOT as an assignment** — `DN-16-2-4`
keeps `pre-seal` a distinct partition precisely so an exclusion is never read as one. ⛔ **The rule
was NOT amended and no guard was touched** (*"amending the rule to make a red commit green is the
corpus-shopping failure mode with an extra step"*). **The gap between the partition registry and
the trailer vocabulary is a real one and belongs to whoever owns the protocol** — it is recorded
here rather than filed, because AC6.5 permits this story to create **no `DF-*` other than
`DF-16-6-B`**.

**(iii) A WINDOWS-ONLY guard fragility, found by tripping it — and the inverse of this repo's usual
failure direction.** `tests/test_gate_seal.py::_git` calls `subprocess.run(..., text=True)` with
**no `encoding=`**, so it decodes git output with the **locale** codec — `cp1252` on this machine.
A commit message carrying any character outside cp1252 (this project writes `⛔` and `⚠️`
constantly) makes the reader thread raise `UnicodeDecodeError`, `stdout` comes back **`None`**, and
`-94` dies with `TypeError: expected string or bytes-like object, got 'NoneType'` **before it ever
reads the trailer**. Reproduced deliberately, then confirmed by direct measurement
(`locale.getpreferredencoding(False)` → `cp1252`; the message failed to encode at `⚠`).

⚠️ **On the ubuntu CI leg the locale is UTF-8 and the identical commit passes**, so this is a
Windows-only failure that CI cannot see — the mirror image of `AI-E13-1`, where green Windows runs
shipped POSIX-only bugs. ⛔ **The guard was NOT amended** (the story forbids it, and it is out of
scope). The commit message was kept in **plain ASCII**, which is what every commit in this history
already does. Recorded so the next author does not lose the same cycle.

#### 8. What this story did NOT do — asserted rather than promised

`N` stays **5**. Nothing ratified. **No detector was run over any bench member** — the `-7` was
measured over the repository's OWN recorded findings, read from pinned git objects into a scratch
tree. No third-party fetch. No disposition written. No role filled. **No `V1.4` row.**
`adjudication-record.json` byte-unchanged. `protocol_cleared` stays `False` and the seal stays
closed. **`DF-13-5-A` stays OPEN and UNSPENT.** No threshold moved, nothing was promoted, and there
is no eighth §5 condition. No guard was amended or weakened — including `ledger_closed_ids` and
`story_closure_claims`, whose analyzer defect belongs to `DF-16-6-D` and to a future story. No
`DN-*` was reopened. No new dependency and no new import edge: `vacuous_vocabulary.py` still
imports only `re` and `__future__.annotations`.

**POSIX / ubuntu-matrix reasoning — local gates are Windows-only and this repository has shipped
POSIX-only bugs off a green Windows run.** The behaviour change is one ASCII string added to a
`frozenset`: no bytes read, no process spawned, no path joined, no platform call. The new test
module writes its fixtures with `write_text(..., newline="")` and reads line structure exclusively
through the shipped `index_aligned_lines`, which is the detector's own terminator-neutral
decomposition and is already guarded for CRLF/LF byte-identity by `-128`; every path it constructs
goes through `pathlib` under `tmp_path`. The one platform-sensitive artifact this story touches is
`deferred-work.md`, and it was appended **in binary** with the lone-`CR` count and the trailing
newline asserted on both sides precisely so `core.autocrlf` cannot differ between the two legs.

#### 9. FIX ROUND 1 (2026-08-23) — the one reviewer `[Patch]` finding, and nothing else

The 2026-08-23 adversarial code review returned **CONCERNS** with three findings: one `[Patch]` and
two `[Defer]`. **Exactly one was actionable inside this story, and exactly one was actioned.**

**THE DEFECT: a wrong number in this story's own record.** §7's gate table and the Change Log both
reported `pytest tests/test_gate_*.py` as **"36 passed"**. The real figure is **58**. The reviewer
re-ran it independently and got 58; the orchestrator re-ran it independently and got 58; this fix
round re-ran it a third time and got 58. **The "36" was never reproducible, and it is not a
narrower selection that someone forgot to name** — the story's own AC3.3 wording
(`pytest tests/test_gate_*.py`) is a whole-glob selection over all nine files. It was a
transcription error in the record. It is corrected to **58**, and the selection is now spelled out
in the table cell so the number and its scope cannot drift apart again.

**Re-measured here by execution, 2026-08-23** (`python -m pytest <the nine files> -v --tb=no` →
`58 passed in 3.24s`, exit **0**), with the per-file collection counted separately so the total is
checkable rather than asserted:

| File | Tests |
|---|---:|
| `tests/test_gate_breadth.py` | 5 |
| `tests/test_gate_condition_lookup.py` | 2 |
| `tests/test_gate_decision.py` | 8 |
| `tests/test_gate_decision_artifact.py` | 7 |
| `tests/test_gate_flip_path.py` | 7 |
| `tests/test_gate_independence.py` | 10 |
| `tests/test_gate_ordering.py` | 4 |
| `tests/test_gate_seal.py` | 9 |
| `tests/test_gate_yield.py` | 6 |
| **TOTAL** | **58** |

⚠️ **AC3.3's discharge is UNAFFECTED.** The selection is green either way — exit **0** whether
the record says 36 or 58 — and none of the nine files was touched by this story; all nine predate
its baseline commit `6d48c15`. `SECTION_5_CONDITIONS` stays at **SEVEN** and `precision_evaluable`
keeps exactly **FOUR** conjuncts, discharged by these pre-existing guards and by nothing this story
wrote. This was a **record-accuracy** defect, not a functional one — the same shape as the
already-known sprint-status "182 vs 109 keys" miscount, and the same shape this epic has been
bitten by repeatedly. That is precisely why it was worth a round.

**THE TWO `[Defer]` FINDINGS WERE DELIBERATELY NOT TOUCHED.** Both were confirmed real by the
reviewer and both were correctly ruled outside this story's fence (AC7.4):

1. **The `Evidence-partition: open` trailer on a 100%-pre-seal corpus.** `SEAL_CITATION_VALUES` in
   `argus/precision/gate_seal.py` carries no `pre-seal` member, so the citation predicate was never
   given a fourth option. Re-confirmed harmless: `cites_partition` regex-matches only the three
   literal strings, and `corpus_partition_counts` is computed independently of any commit trailer,
   so no computed state is corrupted. Widening that enum is the seal-protocol owner's decision, not
   this story's.
2. **`tests/test_gate_seal.py::_git` decodes git output with the Windows locale codec**
   (`subprocess.run(text=True)` with no `encoding=`), so a non-cp1252 commit message yields
   `stdout is None` and `cites_partition(None)` raises `TypeError` at `tests/test_gate_seal.py:1140`.
   Windows-only, invisible to the ubuntu CI leg. All three of this story's commits are pure ASCII
   and none trips it; **fix round 1's commit message was likewise kept pure ASCII for the same
   reason.**

⛔ **Neither was fixed, and neither was filed to the ledger by this round.** They are being filed
separately, outside this story's write-set fence. `deferred-work.md` is **BYTE-UNTOUCHED** by fix
round 1 — `git status --porcelain` carries no entry for it.

**THE WRITE SET OF FIX ROUND 1 IS THE RECORD ONLY.** No `argus/`, `tests/`, `scripts/` or
`…/validation-corpus/` file was opened for writing; `git status --porcelain` carried exactly the
two expected entries (this story file and `sprint-status.yaml` — both the reviewer's own findings
writes) before this round and exactly those two after. No guard was amended, weakened or exempted.
No `DN-*` was reopened. `_CORROBORATION_ASSERTION_CALLEES` is still **23** and `_ASSERTION_CALLEES`
is still **89**, both re-asserted by execution this round. `N` stays **5**, nothing was ratified, no
detector was run over a bench member, no third-party fetch, no disposition, no role filled, no
`V1.4` row, `adjudication-record.json` byte-unchanged, `protocol_cleared` still `False`.
**`DF-13-5-A` remains OPEN and UNSPENT.**

**Gates re-run in full for fix round 1** — every number below was measured this round, not copied:

| Gate | Command | Result | Exit |
|---|---|---|---|
| Full suite | `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 pytest` | **1,695 passed** in 205.42s | **0** ✅ |
| Types | `mypy argus` (CI scope, deliberately not widened) | *"Success: no issues found in **94** source files"* | **0** ✅ |
| Security | `bandit -r argus --severity-level medium` | Medium **0**, High **0** | **0** ✅ |
| Ceiling | `pytest tests/test_module_size_ceiling.py` | **6 passed**; the guard file is byte-unchanged, so **no `_EXEMPT_BY_DESIGN` entry was added** | **0** ✅ |
| **AC3.3** | `pytest tests/test_gate_*.py` (all nine) | **58 passed** — the corrected figure | **0** ✅ |
| Builder | `python scripts/build_adjudication_record.py --check` | *"the adjudication record is current (**31** row(s))"* | **0** ✅ |
| Builder | `python scripts/build_gate_decision.py --check` | *"CURRENT — **BLOCKED** (NOT COMPUTED BY THIS RUN)"* | **0** ✅ |

The suite figure is **1,695**, identical to the implementation round's — as it must be, since fix
round 1 changed no executable line.

### File List

| Path | Change |
|---|---|
| `argus/detectors/vacuous_vocabulary.py` | **modified** — `+79 / -0`; `"AssertionError"` added to `_ASSERTION_CALLEES` (88 → 89) with its labelled `DN-14-3-5` sub-note |
| `tests/test_vacuous_vocabulary.py` | **NEW** — the seven guards, `TC-ArgusAgent-DETECT-001-138`..`-144` |
| `tests/test_vacuous_cross_language.py` | **modified** — `+2 / -0`, AC6.1's single bounded exception: two comment lines inside `-133` cross-referencing the new register. No assertion, fixture, loop member or import changed. |
| `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` | **modified, append-only** — `DF-16-6-B` filed for the bare-`raise` residual |
| `_bmad-output/design-artifacts/ArgusAgent/stories/16-6-the-assertion-vocabulary-recognises-the-assertion-that-is-a-raise.md` | **modified** — `baseline_commit` frontmatter, Status, checkboxes, this record |
| `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` | **modified** — `16-6-…` `ready-for-dev` → `in-progress` → `review`; all 182 keys, every comment and the STATUS DEFINITIONS block preserved |
| `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md` | **modified, renderer-produced** — `+3 / -3`, the `argus/` LOC figure and the provenance sha (§7b(i)) |
| `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md` | **modified, renderer-produced** — `+3 / -3`, same reason |
| `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md` | **modified, renderer-produced** — `+3 / -3`, same reason |

⚠️ **The last three are OUTSIDE AC6.1's stated write set, and that is §7b(i)'s finding rather than
a scope breach:** the fence is unsatisfiable alongside AC7.1 for any change at all to `argus/`.
They were produced by `scripts/regenerate_dogfood_artifacts.py` through the artifacts' own
renderers, never hand-edited, and committed **separately** from the behaviour change.

⛔ **Byte-unchanged, and confirmed by `git status --porcelain` carrying no entry for any of them:**
`argus/detectors/vacuous_test.py` · `argus/detectors/provenance_scan.py` ·
`tests/test_vacuous_density.py` · `tests/test_vacuous_detector.py` ·
`tests/test_vacuous_detector_index.py` · `argus/precision/**` · `scripts/**` · `pyproject.toml` ·
`_bmad-output/design-artifacts/ArgusAgent/validation-corpus/**`.

### Change Log

| Date | Change |
|---|---|
| 2026-08-23 | Story opened. Baseline re-measured GREEN at HEAD `6d48c15` (1,688 passed / exit 0; both builders `--check` exit 0) before a line was written. `ready-for-dev` → `in-progress`. |
| 2026-08-23 | §0 re-derived by execution: the `-7` reproduced exactly (1,032 → 1,025, 22 findings, 0 newly flagged, all seven rows to the `Fraction`). Three disagreements recorded under AC4.4 — the §0.5 census (182 : 2 over 5,086 against 183 : 2 over 5,085; ratio 91× either way), §0.4's finding-vs-node unit, and further same-day corpus dirty-counts. |
| 2026-08-23 | `"AssertionError"` added to `_ASSERTION_CALLEES` (88 → 89) with a labelled `DN-14-3-5` sub-note carrying its own population and its stated inclusion rules. `+79 / -0`. |
| 2026-08-23 | NEW `tests/test_vacuous_vocabulary.py` — seven guards, `-138`..`-144`. Two were found defective by execution before the gates saw them, and repaired. |
| 2026-08-23 | AC5.1's mutation executed: six of the seven cases RED at the real seam, while the pre-existing vacuous suite stayed identically GREEN under the same mutation. Tree restored, porcelain byte-identical. A second mutation (case-insensitive convention regex) drove three cases RED. |
| 2026-08-23 | `DF-16-6-B` appended to `deferred-work.md` in binary; lone-`CR` count 1 → 1, trailing newline intact, HEAD blob still a strict prefix, `+207 / -0`. |
| 2026-08-23 | Three unforeseen items found by execution and resolved inside domain authority (§7b): AC6.1's fence is unsatisfiable alongside AC7.1 for any `argus/` change, so the three DOGFOOD artifacts were regenerated through their own renderers in a separate commit; the first-ever post-seal detector commit needed an `Evidence-partition:` trailer for which the corpus has no matching value (all five members are `pre-seal`); and `tests/test_gate_seal.py::_git` decodes git output with the Windows locale codec, so the commit message was kept ASCII. **No guard was amended, weakened or exempted.** |
| 2026-08-23 | Commit arc: `feat` (the one name + the guards, alone and first) → `chore` (the regenerated dogfood artifacts, separately, as the guard's own remedy and `ba5e8df`'s precedent require) → `docs` (this record + the ledger). **No split commit** — the split already landed in `4123931`. |
| 2026-08-23 | All gates green with their actual numbers recorded (§7 above): suite **1,695 passed / exit 0**, coverage **95.55%**, `mypy argus` clean over **94** files, bandit Medium 0 / High 0, ceiling **6 passed** with no `_EXEMPT_BY_DESIGN` entry added, `tests/test_gate_*.py` **~~36~~ 58 passed** (⚠️ the **36** was WRONG as written and is corrected here in fix round 1 — §9), both builders `--check` exit 0, corpus artifacts byte-unchanged. `in-progress` → `review`. |
| 2026-08-23 | **FIX ROUND 1** — code review returned **CONCERNS** with 1 `[Patch]` + 2 `[Defer]`. **1 of 1 actionable findings resolved.** §7's gate table and the Change Log misreported `pytest tests/test_gate_*.py` as **36 passed**; re-measured by execution as **58 passed / exit 0** (5+2+8+7+7+10+4+9+6 across all nine `test_gate_*.py` files) and corrected, with the selection now named in the table cell. AC3.3's discharge is unaffected — the selection is green at either figure and none of the nine files was touched by this story. **Record-accuracy fix only: no executable line changed.** The two `[Defer]` findings (the `SEAL_CITATION_VALUES` `pre-seal` gap; the `tests/test_gate_seal.py::_git` cp1252 decode) were deliberately left exactly as they are, were not fixed, and were not filed to the ledger by this round — `deferred-work.md` is byte-untouched. |
| 2026-08-23 | Fix round 1 gates re-run in full: suite **1,695 passed / exit 0**, `mypy argus` clean over **94** files, bandit Medium 0 / High 0, ceiling **6 passed** with no `_EXEMPT_BY_DESIGN` entry added, `tests/test_gate_*.py` **58 passed**, both builders `--check` exit 0. `_ASSERTION_CALLEES` re-asserted at **89** and `_CORROBORATION_ASSERTION_CALLEES` at **23**. `in-progress` → `review`. |
