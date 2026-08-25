---
baseline_commit: bd110c6
---

# Story 18.4: The `Detector` Protocol is load-bearing or it is deleted

Status: in-progress

<!-- Contexted 2026-08-25 at HEAD `bd110c6` (branch `docs/merge-strategy-decision`) by the
     create-story workflow (Opus 5).

     EVERY FIGURE IN SECTION 0 WAS READ OFF THIS TREE BY EXECUTION, not copied from `epics.md`,
     from `sprint-change-proposal-2026-08-24.md`, from `DF-AUD-DETECT-F` or from Stories
     18.1/18.2/18.3. The Protocol was type-checked against all four shipped detectors with the
     repo's own `mypy`; the lone test's assertion was driven against five decoy classes; the
     runtime check was executed on CPython 3.11, 3.12 AND 3.13; and the whole candidate change was
     applied to a THROWAWAY COPY of `argus/` outside the repository and `mypy argus` re-run over it
     before a word of this file was written.

     THE EITHER/OR IN THE TITLE IS DECIDED BY THAT MEASUREMENT, AND IT IS DECIDED AGAINST DELETION.
     Four premises moved:
       (1) SECTION 0.2 - the entry says "the widened signature is what makes them all satisfy it".
           MEASURED FALSE. `mypy` REJECTS all four detectors against the shipped Protocol. The
           Protocol is not merely unused - it is UNUSABLE as a type, and nobody could ever have
           typed against it.
       (2) SECTION 0.3 - the lone test is vacuous, not merely lonely: `isinstance` passes for a
           class whose `run` is the integer `42` and for one whose `run` returns `str`, on 3.11,
           3.12 and 3.13 alike.
       (3) SECTION 0.4 - there is a Protocol SHAPE that all four detectors satisfy today, with no
           signature unification and no detector edit, and it REJECTS five decoys. The entry's own
           "honest counter-argument" - `rule_id` + `DetectorResult` is the real shared contract -
           is exactly that shape. Deleting the Protocol would throw away a real, enforceable
           invariant on the strength of an argument the measurement answers.
       (4) SECTION 0.1 - "the five concrete detectors" is FOUR. Five is the count of `rule_id`s in
           `FROZEN_DETECTOR_SET`, not of detector classes.

     NO `argus/`, `tests/`, `scripts/` OR ARTIFACT FILE WAS TOUCHED TO PRODUCE THIS STORY. Every
     probe ran in a scratch directory outside the repository, and the scratch copy of `argus/` was
     deleted after it was measured.

     THE WORKING TREE WAS ALREADY DIRTY AT CONTEXTING, AND NOT WITH THIS STORY'S WORK: five files
     carrying Stories 18.1/18.2/18.3's records are modified-but-uncommitted at `bd110c6`. See
     SECTION 0.0 and SECTION 2.6 - they are NOT this story's to commit, and `git add -A` would
     swallow them.

     NOTHING HERE SPENDS `DF-13-5-A`. No member is ratified, no protocol row is added, no FR is
     amended, no third-party source is fetched. -->

## Story

As the **Engineering Lead**,
I want **the `Detector` Protocol to state the contract the detectors actually have, and every detector statically pinned to it inside `argus/` where the blocking `mypy` gate can see it**,
so that **a contract that reads as load-bearing is one the type checker enforces — and the next person who adds a detector cannot skip it.**

### What this story IS

The discharge of **`DF-AUD-DETECT-F`**, both of its items, plus the one item Story 18.2 measured in
this module and handed over by name.

`argus/detectors/base.py` makes three contract claims. **All three are measurably unenforced**, and
each is unenforced in a different way:

- **Item A — the `Detector` Protocol (`:126`–`:139`).** Declared `runtime_checkable` with
  `run(self, *args: object, **kwargs: object) -> DetectorResult`. Imported by exactly one test and
  no production module (§0.1). ⛔ **And `mypy` rejects all four shipped detectors against it**
  (§0.2) — so it could never have been used as a type even by someone who tried.
- **Item B — the erased type at `build_recording` (`:166`, `:200`).** `depth_supported: object | None`
  passed to `Recording` under `# type: ignore[arg-type]`, at *the single construction point every
  finding in the system passes through*. ⛔ **Measured: `mypy` is SILENT on
  `build_recording(draft, depth_supported="not-a-depth")`; `pydantic` raises at RUNTIME** (§0.5).
  A compile-time error was converted into an audit-time crash.
- **Item C — `FindingDraft`'s docstring (`:63`–`:72`).** It says the draft carries *"the supported
  coverage depth (the verdict-fold input), and the evidence the finding carries WITH it"*. ⛔
  **Measured: `FindingDraft` has neither field** (§0.6). Story 18.2 measured this, recorded it
  un-filed under `AI-E9-8`, and left it because *"`base.py` is another story's module"* — **this
  story's module**.

The story lands: **one narrowed Protocol**, **four static conformance pins** inside `argus/`, **one
restored parameter type and one deleted `# type: ignore`**, **one corrected docstring**, and **the
structural guard that makes an unpinned detector impossible**.

### What it is NOT

- ⛔ **NOT the deletion arm.** The epic's AC offers *"either the detectors are typed against it … or
  it is deleted and its lone test with it"*. §0.4 measured a Protocol shape the four detectors
  satisfy **today**, with **no** signature unification and **no** detector-body edit, which
  **rejects five decoy classes** the shipped one accepts. `DN-18-4-1` takes the first arm and
  records why. **If Task 0 cannot reproduce §0.4, this story STOPS — it does not fall back to
  deleting** (AC9).
- ⛔ **NOT a unification of `run` signatures.** The entry's honest counter-argument is right that
  forcing a common `run(...)` would be a worse design. **Nothing in this story touches any
  detector's `run` signature, body, or call sites.** The Protocol stops describing `run`'s
  parameters at all; it constrains `run`'s **existence, callability and return type**, which is the
  part that is actually shared.
- ⛔ **NOT a new dispatch site, registry, base class or `for detector in …` loop.** ⛔ **Inventing a
  consumer to justify the contract is the same defect wearing a different hat.** §2.2. The
  detectors keep being constructed and called concretely in `argus/pipeline_stages.py`, which stays
  **byte-unchanged**.
- ⛔ **NOT a behaviour change.** No detector output moves. This story is the INVERSE of 18.3 and the
  same shape as 18.2: the obligation is **neutrality**, proven, not a directional improvement
  (`DN-18-4-7`).
- ⛔ **NOT a `code_identity` bump.** `FROZEN_DETECTOR_SET` carries five descriptors and **none of
  them is `base.py`**; nothing here changes any detector's logic (§0.8). ⛔ This is the deliberate
  inverse of `DN-18-3-6` and the same arm as `DN-18-2-5`.
- ⛔ **NOT a touch of `architecture.md`.** Under the arm taken, `architecture.md:1174` — *"base.py
  # detector Protocol + Finding builder"* — **stays true**. Had the deletion arm been taken it
  would have gone stale; that is one of the costs `DN-18-4-1` weighs.
- ⛔ **NOT a relitigation of `ToolRunnerDetector`'s impurity.** `tool_runner.py:27` cites the
  Protocol docstring's *"`run` MUST be pure"* sentence and then discloses that this detector's core
  is impure by design. That disclosure is Story 2.6's, it is reasoned, and it stays. ⛔ **The purity
  paragraph therefore STAYS IN THE PROTOCOL DOCSTRING** or that citation goes stale (§2.4).
- ⛔ **NOT a repository-wide `# type: ignore` purge.** `argus/` carries **31**; this story removes
  the **one** in `base.py` and touches no other (§0.5).
- ⛔ **NOT a disposition of `DF-10-4-B`.** *"`DetectorResult.degraded` has ZERO production readers"*
  is the same defect class, in the same module, and it stays **OPEN and untouched** (§1.3).
- ⛔ **NOT a repair of the FR10 evidence-carrying gap.** Story 18.2 measured it as
  *"repository-wide and older than this entry"* — `Recording`'s ten fields include none that could
  hold a count. Item C corrects a **docstring** to match the models; it does not add a field
  (`DN-18-4-6`).
- ⛔ **NOT a verdict move.** No finding becomes verdict-eligible. The ≥80% precision keystone stays
  **NOT CLEARED** and the gate stays `BLOCKED`.
- ⛔ **NOT an epic-16-or-earlier reopening.** Epics 1–16 are `done`. Story 1.5's, 2.5's, 2.6's and
  10.4's records are cited, never edited.
- ⛔ **NOT anything under `minions_core/apaa/`.** That tree is dead; `argus/` is the only live one.

---

## §0 — PREMISES RE-MEASURED BY EXECUTION at HEAD `bd110c6`

⛔ **Task 0 re-derives every row below before a line is written.** Six consecutive epics in this
repository found a stated premise false by executing it; 18.1 found two, 18.2 found three, 18.3
found three, and this contexting pass found **four** (§0.1, §0.2, §0.3, §0.4). The figures here were
true on 2026-08-25 on a Windows host; **they are a baseline to re-measure, not a fact to cite.**

### §0.0 The tree, the paths and the baseline

| fact | value at contexting |
|---|---|
| repo root | `d:/ProjectX/XAgents/XAgents/ArgusAgent` |
| HEAD | `bd110c6` — Story 18.3's `docs` commit |
| branch | `docs/merge-strategy-decision` |
| last commit touching `argus/` | `9e3fdc2` — Story 18.3's `feat` |
| `git status --porcelain` | ⚠️ **NOT empty** — five Story-18.1/18.2/18.3 record files (below) |
| python (local) | **3.11.15** |
| CI python matrix | ⛔ **3.10, 3.11, 3.12** (`.github/workflows/audit-ci.yml:15`) — §2.3 |
| tests collected under `tests/` | **1,729** (`python -m pytest --collect-only`) |
| full suite | **exit 0** (`python -m pytest -q`, run at this HEAD) |
| `python -m mypy argus` | **Success: no issues found in 95 source files** |
| `python -m bandit -r argus --severity-level medium` | **No issues identified** |
| mypy version / config | **2.3.0**; ⛔ **NO `[tool.mypy]` section anywhere and no `mypy.ini`** — defaults, and CI runs **`mypy argus`** only (`audit-ci.yml:70`). §2.1 |
| tracked `*.py` (`git ls-files -- '*.py'`) | **253** |
| tracked `argus/*.py` | **95** |
| `argus/detectors/base.py` | **204** lines (NFR-M1 ceiling 1,200) — the module under change |
| `argus/detectors/vacuous_test.py` | 796 lines — pin only |
| `argus/detectors/secret_scan.py` | 630 lines — pin only ⛔ (18.3's module; **its regexes are not reopened**) |
| `argus/detectors/tool_runner.py` | 455 lines — pin only |
| `argus/detectors/orphan_code.py` | 306 lines — pin only |
| `tests/test_detector_base.py` | **89** lines — the only importer of `Detector` |
| `deferred-work.md` (worktree) | **573,091** bytes, **0** CRLF, **exactly one** lone `\r` at offset **410,341**, **7,305** LF |
| `deferred-work.md` (committed blob at `bd110c6`) | **571,142** bytes, **0** CRLF, **one** `\r` |
| `sprint-status.yaml` | **1,017,662** bytes, **1,187** CRLF, **0** lone `\r` |
| `minions-dogfood-proof.md` | total physical LOC **33,703**; `hardcoded_secret` **39** |
| next free `TC-ArgusAgent-DETECT-001` id | **-145** (max is **-144**, in `tests/test_vacuous_vocabulary.py`) |
| `# type: ignore` in `argus/` | **31** total; **exactly one** in `base.py` (`:200`) |

⚠️ **THE TREE IS DIRTY AND IT IS NOT YOURS.** At contexting `git status --porcelain` lists exactly:

```
 M _bmad-output/design-artifacts/ArgusAgent/deferred-work.md
 M _bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml
 M .../stories/18-1-the-sentinel-table-matches-values-not-substrings-of-them.md
 M .../stories/18-2-the-redaction-call-keeps-the-evidence-it-computes.md
 M .../stories/18-3-two-regex-precision-defects.md
```

The `deferred-work.md` modification is a **19-line, +19/−0 pure append** (`DF-AUD-DETECT-A`'s
closure note) written by a peer session and deliberately left unstaged. ⛔ **Stage by explicit path,
and stage `deferred-work.md` HUNK-SELECTIVELY** — Story 18.3 did exactly this and its review
verified the peer's 19 lines were still uncaptured afterwards (§2.6).

⛔ **`AI-E13-1` — the local suite is Windows-only and CI runs an ubuntu matrix.** A green local run
is recorded as **LOCAL** and never on its own discharges a cross-platform claim. ⛔ **This story has
a REAL cross-version exposure and it is not hypothetical** — see §2.3.

### §0.1 THE ENTRY'S CENSUS REPRODUCES — except the count of detectors

`DF-AUD-DETECT-F` says the Protocol is *"asserted by exactly one test and used by nothing"*.
**MEASURED TRUE.** A whole-tree grep for the bare name `Detector` (excluding `DetectorResult` and
the five concrete class names) resolves to:

| site | what it is |
|---|---|
| `argus/detectors/base.py:58` | the `__all__` entry |
| `argus/detectors/base.py:127` | the declaration |
| `argus/detectors/orphan_code.py:174`, `secret_scan.py:389`, `tool_runner.py:291`, `vacuous_test.py:602` | **docstring prose** — *"satisfies the `detectors.base.Detector` protocol structurally"* |
| `argus/detectors/tool_runner.py:27` | prose citing the Protocol docstring's purity sentence |
| `tests/test_detector_base.py:15` | ⛔ **the only `import`** |
| `tests/test_detector_base.py:89` | ⛔ **the only use**: `assert isinstance(VacuousTestDetector(), Detector)` |

⛔ **NO PRODUCTION MODULE IMPORTS THE NAME.** Confirmed.

⛔ **AND THE FOUR DOCSTRINGS ARE FALSE AS WRITTEN.** They claim their classes *satisfy* the
Protocol. Under `mypy` they do not (§0.2). Four shipped modules assert a conformance the type
checker denies.

⚠️ **PREMISE MOVED — "the five concrete detectors" is FOUR.** An AST walk of `argus/**` finds
exactly **six** classes defining `run`, of which:

- **four are detectors**: `VacuousTestDetector` (`vacuous_test.py:611`), `SecretScanDetector`
  (`secret_scan.py:437`), `ToolRunnerDetector` (`tool_runner.py:300`), `OrphanCodeDetector`
  (`orphan_code.py:187`) — all `-> DetectorResult`;
- one is the Protocol itself (`base.py:138`);
- one is **`DeepAuditSeam.run` (`argus/audit/deep_audit.py:110`) → `LLMRecording`** — not a
  detector, not in scope.

`argus/detectors/provenance_scan.py` defines **no** detector class. **Five is the number of
`rule_id`s in `FROZEN_DETECTOR_SET`** (`vacuous_test` contributes two), not the number of classes.
⚠️ Note also that `OrphanCodeDetector.rule_id == "orphan_code"` is **not** in that frozen set — a
separate observation, **recorded, not filed, not fixed here** (§1.3).

The three signature shapes the entry names DO reproduce exactly:

```
VacuousTestDetector.run(self, *, file_path: str, source: str, ast_entry: AstIndexEntry, coverage_envelope_slice: str | None = None)
SecretScanDetector.run (self, *, file_path: str, source: str, ast_entry: AstIndexEntry, coverage_envelope_slice: str | None = None, ignore_paths: Sequence[str] = (), ignore_patterns: Sequence[str] = ())
ToolRunnerDetector.run (self, *, targets: Sequence[tuple[str, str]], already_graded_paths: Sequence[str] = ())
OrphanCodeDetector.run (self, *, index: AstIndex, coverage_envelope_slice: str | None = None)
```

All four carry a **class-level** `rule_id: str` — `vacuous_test_heuristic`, `hardcoded_secret`,
`tool_failure`, `orphan_code`.

### §0.2 ⛔ THE ENTRY'S CENTRAL MECHANISM IS FALSE. THE PROTOCOL IS NOT UNUSED — IT IS UNUSABLE.

The entry says: *"The five concrete detectors take mutually incompatible keyword-only signatures …
**so the widened signature is what makes them all "satisfy" it**."*

⛔ **MEASURED FALSE.** A probe assigning each detector to a `Detector`-typed variable and running
the repo's own `mypy`:

```
error: Incompatible types in assignment (expression has type "VacuousTestDetector", variable has type "Detector")
note:   Expected: def run(self, *args: object, **kwargs: object) -> DetectorResult
note:   Got:      def run(self, *, file_path: str, source: str, ast_entry: AstIndexEntry, coverage_envelope_slice: str | None = ...) -> DetectorResult
… and the same for SecretScanDetector, ToolRunnerDetector, OrphanCodeDetector
Found 4 errors in 1 file (checked 1 source file)
```

**4 of 4 rejected.** `*args: object, **kwargs: object` does not *widen* the protocol member — it
**narrows what can implement it**, because an implementation must accept everything the protocol
permits, and a keyword-only signature does not accept positional arguments.

⛔ **This changes the story's premise.** The Protocol is not a harmless decoration that nobody
happened to use. **It is a contract that would have failed the moment anyone used it.** The middle
position the entry describes is not *"`run` is decoration"* — it is *"`run` is an active
falsehood"*, and the four docstrings in §0.1 are its downstream repetitions.

Also measured, and a trap for whoever touches it: **`issubclass(VacuousTestDetector, Detector)`
raises `TypeError: Protocols with non-method members don't support issubclass()`**, because
`rule_id: str` is a data member.

### §0.3 ⛔ THE LONE ASSERTION IS VACUOUS, ON EVERY PYTHON IN THE CI MATRIX

`tests/test_detector_base.py:89` is `assert isinstance(VacuousTestDetector(), Detector)`. A
`runtime_checkable` protocol's `isinstance` checks **member presence only** — never callability,
never signature, never return type. Driven against five decoys:

| decoy | shipped `isinstance` |
|---|---|
| `run` returns `str` instead of `DetectorResult` | ⛔ **True** |
| `run(self, banana: int)` — incompatible signature | ⛔ **True** |
| `run = 42` — **not callable at all** | ⛔ **True** |
| no `rule_id` | False |
| empty class | False |

⛔ **A class whose `run` is the integer `42` passes the only test the Protocol has.** The assertion
detects exactly two things: *has an attribute named `run`* and *has an attribute named `rule_id`*.

⚠️ **AND ITS RESULT IS NOT STABLE ACROSS THE CI MATRIX.** The same probe on three interpreters:

| decoy | 3.11.15 | 3.12.10 | 3.13.14 |
|---|---|---|---|
| `run = 42` | True | True | True |
| wrong signature | True | True | True |
| `rule_id` supplied by `__getattr__` | ⛔ **True** | ⛔ **False** | ⛔ **False** |

Python 3.12 changed `runtime_checkable` to use `inspect.getattr_static` instead of `hasattr`. **CI
runs 3.10, 3.11 and 3.12.** A guard whose verdict depends on the interpreter is not a guard (§2.3).

### §0.4 ⛔ THE SHAPE THE FOUR DETECTORS ALREADY SATISFY — MEASURED, AND IT REJECTS FIVE DECOYS

Four candidate Protocol shapes were type-checked against all four shipped detectors:

| shape | all four accepted by `mypy`? |
|---|---|
| **shipped**: `rule_id: str` + `def run(self, *args: object, **kwargs: object) -> DetectorResult` | ⛔ **NO — 4 errors** |
| `rule_id: str` only (no `run`) | yes — but constrains nothing about the result |
| `rule_id: str` + `run: Callable[..., DetectorResult]` (settable attribute) | ⛔ **NO** — *"expected settable variable, got read-only attribute"* |
| `rule_id: str` + `def run(self, **kwargs: Any) -> DetectorResult` | ⛔ **NO — 4 errors** |
| ⛔ **`rule_id` and `run` BOTH as read-only properties**, `run: Callable[..., DetectorResult]` | ✅ **YES — `Success: no issues found`** |

The accepted shape, verbatim as measured:

```python
class Detector(Protocol):
    @property
    def rule_id(self) -> str: ...  # pragma: no cover - structural declaration

    @property
    def run(self) -> Callable[..., DetectorResult]: ...  # pragma: no cover - structural
```

⛔ **And it is not permissive.** Against five decoys, with the pins written inside
`if TYPE_CHECKING:`:

| decoy | shipped `isinstance` | this shape under `mypy` |
|---|---|---|
| no `rule_id` | False | **error** |
| `rule_id = 7` (not `str`) | True | **error** |
| `run` returns `str` | ⛔ True | **error** |
| no `run` | False | **error** |
| `run = 42` | ⛔ True | **error** — *`run: expected "Callable[..., DetectorResult]", got "int"`* |

**5 of 5 rejected. `Found 5 errors in 1 file`.**

⛔ **THE IDIOM IS ALREADY THIS REPOSITORY'S.** `argus/detectors/vacuous_test.py:404` declares
`_HasFilePath(Protocol)` with exactly this spelling —
`@property def file_path(self) -> str: ...  # pragma: no cover - structural declaration` — and it
**is** load-bearing: it bounds the `_EntryT` TypeVar that `partition_application_files` is generic
over. `argus/audit/ports.py`'s `LLMDispatchPort` is the second one, and it appears in production
**type positions** (`def __init__(self, *, port: LLMDispatchPort)`, `port: LLMDispatchPort | None`).
⛔ **`Detector` is the only Protocol in this tree that constrains nothing** — and the spelling that
fixes it is already in the same package.

### §0.5 ⛔ ITEM B IS TRUE AND WORSE THAN THE ENTRY STATES

`build_recording(draft, *, depth_supported: object | None = None, …)` passes that value to
`Recording(depth_supported=…)  # type: ignore[arg-type]`. `Recording.depth_supported` is
`CoverageDepth | None` (`argus/ledger/recording.py:118`).

**Measured against the SHIPPED body:**

```
build_recording(d, depth_supported="not-a-depth")   ->  mypy: Success: no issues found
build_recording(d, depth_supported=object())        ->  mypy: Success: no issues found
   … and at runtime:  pydantic.ValidationError: Input should be 'audited_deep', 'audited_shallow', …
```

⛔ **The `# type: ignore` converts a compile-time error into an audit-time crash**, at the one
function every finding in the system is built by. **7 production call sites** pass
`depth_supported=` (`orphan_code:272`, `secret_scan:535`, `secret_scan:572`, `tool_runner:455`,
`deep_pass:353`, plus tests), and none of them is type-checked on that argument today.

⛔ **THE REPAIR IS FREE AND WAS MEASURED END-TO-END.** A throwaway copy of the whole `argus/` tree
outside the repository, with the parameter changed to `CoverageDepth | None` and the ignore
**deleted** — `CoverageDepth` comes from `argus.ledger.coverage_ledger`, which `base.py` **already**
imports for `CoverageLedgerEntry`, so **no new import edge** is created and the import-isolation
gate is unaffected:

```
python -m mypy argus   ->   Success: no issues found in 95 source files
```

and the same probe that was silent before is now **`error`**.

### §0.6 ITEM C — THE DOCSTRING NAMES TWO FIELDS THE MODEL DOES NOT HAVE

Read off the live models by execution:

```
FindingDraft fields : advisory, ast_span, cartridge_id, coverage_envelope_slice, end_line, file_path, rule_id, start_line
Recording    fields : advisory, cartridge_id, claim_present, coverage_envelope_slice, depth_supported,
                      locators, partition_id, recording_id, rule_id, schema_version
DetectorResult      : degraded, entries, findings
```

`base.py:63`–`:72` claims `FindingDraft` carries *"the supported coverage depth (the verdict-fold
input), and the evidence the finding carries WITH it (FR10 …)"*. ⛔ **Neither exists.**
`depth_supported` is a **parameter of `build_recording`**, not a draft field; and no evidence field
exists anywhere on the three models. Story 18.2's disposition measured this at its own fix sha,
recorded it **un-filed** under `AI-E9-8`, and left `base.py` byte-unchanged because it belongs to
this story.

⚠️ **The evidence half is repository-wide and is NOT repaired here** (`DN-18-4-6`). 18.2 measured
that `Recording`'s ten fields include none that could hold a count, so *"one detector widened in
isolation"* is the wrong shape of repair. **The docstring is corrected to describe what the model
is; no field is added.**

### §0.7 WHAT THE WHOLE CHANGE MOVES — measured on a throwaway copy of `argus/`

The complete candidate change (narrowed Protocol, four pins, item B, item C) applied to a scratch
copy:

| file | lines before → after | `hardcoded_secret` self-scan before → after |
|---|---|---|
| `argus/detectors/base.py` | **204 → 199** | 0 → 0 |
| `argus/detectors/vacuous_test.py` | 796 → 803 | 0 → 0 |
| `argus/detectors/secret_scan.py` | 630 → 637 | **7 → 7** |
| `argus/detectors/tool_runner.py` | 455 → 462 | 0 → 0 |
| `argus/detectors/orphan_code.py` | 306 → 313 | 0 → 0 |
| **total** | **+23 physical lines** | **7 → 7 (unchanged)** |

- ⛔ **`mypy argus` over the modified copy: `Success: no issues found in 95 source files`.**
- ⛔ **The detector's own output over the five changed files does not move** — which is what makes
  §0.8's dogfood prediction *"LOC moves, finding counts do not"*.
- ⚠️ The line deltas are the shape of one candidate spelling, **not a requirement**. What is
  required is AC1–AC4; the arithmetic is a sanity check.

### §0.8 THE GUARDS THAT WILL FIRE, AND THE ONES THAT WILL NOT

- ⛔ **The dogfood derivation guards WILL fire.** `minions-dogfood-budget-plan.md` records
  *"Build-cost proxy (total physical LOC): 33703"*, derived live. **+23 lines moves it to ~33,726**
  and `tests/test_dogfood_plan.py` / `tests/test_dogfood_proof.py` redden until the three artifacts
  are regenerated — exactly what Stories 18.2 and 18.3 each hit and each fixed by regeneration with
  **no assertion loosened**. ⛔ `scripts/regenerate_dogfood_artifacts.py` exits **2** on a dirty
  `argus/`, which is why the commit arc has four commits and the regeneration is the third.
- ⛔ **`tests/test_detector_base.py:89` WILL fail** the moment `@runtime_checkable` is dropped:
  `TypeError: Instance and class checks can only be used with @runtime_checkable protocols`
  (measured). **This is the story's own test and AC5 rewrites it.** It is the ONLY test in the tree
  that can be reddened by the Protocol change, because it is the only importer.
- **Expected NOT to move:** `tests/test_cache_key.py` and `tests/test_cache_invalidation.py` (no
  `code_identity` bump — §0.9), `tests/test_no_web_imports.py` (no new import edge — §0.5),
  `tests/test_module_size_ceiling.py` (199 and 803 are far below 1,200),
  `tests/test_v1_commitment_closure.py` (its FR13 row pins the string `"def build_recording("` in
  `argus/detectors/base.py`, which is unchanged), `tests/test_governance_record_integrity.py`,
  every secret-domain module, and the whole `precision/**` family.
- ⚠️ **Predictions, not facts.** Record every one that comes out different (Task 0, Task 6).

### §0.9 NO `code_identity` BUMP — measured, and the inverse of 18.3

`FROZEN_DETECTOR_SET` (`argus/cache/key.py:186`) is five hand-declared descriptors —
`hardcoded_secret`/`secret_scan.v2`, `tool_failure` and `traceability_not_establishable`/
`tool_runner.v1`, `vacuous_test_heuristic`/`vacuous_test.heuristic.v1`,
`vacuous_test_ast`/`vacuous_test.ast.v1`. ⛔ **`base.py` has no descriptor and the set is not
derived from any file's content.** The descriptor contract says a token is *"bumped when its logic
materially changes"*; **no detector's logic changes here** (§0.7). ⛔ **Nothing under
`argus/cache/` is touched.** This is `DN-18-2-5`'s arm, taken for `DN-18-2-5`'s reason, and the
deliberate inverse of `DN-18-3-6`.

### §0.10 What is already true and must NOT be re-done

- Story 18.1 (`done`) — the length-gated sentinel table and the repaired Live-Key Safeguard.
  `argus/detectors/secret_suppression.py` and `TC-ArgusAgent-SECRET-001-23`..`-27` are **not
  touched**.
- Story 18.2 (`done`) — the deleted redaction call, the replaced banner, `-28`..`-30`. **Not
  reopened.** Its RECORDED-NOT-FILED item (a) is this story's item C; item (b) stays recorded.
- Story 18.3 (`done`) — the anchored key alternation, the three paired delimiters, the
  `secret_scan.v2` bump, `TC-ArgusAgent-SECRET-002-08`..`-12`. ⛔ **`secret_scan.py`'s regexes and
  `argus/cache/key.py` are NOT reopened**; `secret_scan.py` is edited for **one appended
  conformance pin and nothing else**.
- The four detector docstrings that claim conformance already exist. **They become TRUE under this
  change; they are not rewritten** (§2.5).

---

## §1 — WHY THIS STORY EXISTS

### §1.1 The whole epic is about documents and code that assert what they do not do

18.1 repaired a sentinel table that claimed to match values and matched substrings. 18.2 deleted a
call that computed evidence and dropped it, and replaced a banner that described a guarantee the
code no longer provided. 18.3 corrected two regexes whose docstring claimed a precision they did
not have. ⛔ **`base.py` is the same defect three more times, in the module every finding in the
system is built by** — and unlike the first three, **nothing here is wrong at runtime today**. That
is precisely why it is 🟢 and why it is last.

### §1.2 "Used by nothing" and "unusable" are different findings, and only one of them argues for deletion

If the Protocol merely lacked a consumer, the ledger's counter-argument would be strong: heterogeneous
detectors, a fake common signature, delete it. **§0.2 measured something else.** The Protocol
lacks a consumer *because it cannot have one*. The contract underneath — a `rule_id` and a callable
`run` returning a `DetectorResult` — **is real, is shared by all four detectors, and is asserted in
four shipped docstrings today**. ⛔ **Deleting the Protocol deletes the wrong thing: it removes the
name and keeps the four unenforced claims.**

### §1.3 What this story does NOT fix, named so it is not mistaken for fixed

- **`DF-10-4-B`** — `DetectorResult.degraded` has zero production readers. Same class, same module,
  **OPEN and untouched**. ⚠️ Its `target_story` is `10-5-…`, which is `done`; ⛔ **that is Story
  17.5's guard to build, not this story's to re-home.**
- **The FR10 evidence-carrying gap** — repository-wide, older than `DF-AUD-DETECT-F`, recorded by
  18.2. Untouched.
- **`OrphanCodeDetector.rule_id` is absent from `FROZEN_DETECTOR_SET`** — measured in §0.1.
  ⛔ **RECORDED, NOT FILED, NOT FIXED** (`AI-E9-8`). It is a cache-key question, not a typing one,
  and `argus/cache/` is fenced.
- **`FROZEN_DETECTOR_SET`'s comment claims its `rule_id`s "mirror the live detector constants" and
  nothing enforces it.** ⛔ **RECORDED, NOT FILED.** Binding it would require `argus/cache/key.py`
  to import `argus.detectors.*`, dragging the AST/tree-sitter import surface into the determinism
  module. **That is a design decision with a real cost and it is the Engineering Lead's.**
- **`ToolRunnerDetector.run` is impure** while the Protocol docstring says `run` MUST be pure.
  Disclosed by Story 2.6 at `tool_runner.py:27`; **left exactly as it is** (§2.4).

---

## §2 — THE COUPLINGS THAT WILL BITE

### §2.1 ⛔ A CONFORMANCE PIN OUTSIDE `argus/` IS NOT A GUARD

There is **no `[tool.mypy]` section, no `mypy.ini`, no `setup.cfg`** in this repository, and CI runs
**`mypy argus`** — `tests/` **is not type-checked by any gate** (§0.0). ⛔ **Therefore a
`Detector`-typed assertion written in `tests/` is enforced by NOTHING.** It would look like a guard,
pass forever, and be exactly the vacuity this epic exists to remove (`AI-E14-1`).

⛔ **The pins MUST live inside `argus/`**, and AC2 requires it. `if TYPE_CHECKING:` is the spelling
that gets them checked without executing them — **measured**: mypy reports the error inside a
`TYPE_CHECKING` block, and the block never runs, so there is no import-time instantiation and no
runtime cost.

### §2.2 ⛔ DO NOT INVENT A CONSUMER

The tempting "make it load-bearing" move is to add a registry, a `Sequence[Detector]`, or a
dispatch loop. ⛔ **Do not.** `argus/pipeline_stages.py:249`–`:251` and `:348` construct and call the
detectors **concretely and directly**, and annotating those locals as `Detector` would make the
call sites **less** checked, not more — `Callable[..., DetectorResult]` accepts any arguments, so
`run(file_path=…, source=…)`'s keywords would stop being validated. **A typing story that weakens
type checking at its only use site is a regression.** `argus/pipeline_stages.py` is **byte-unchanged**
(AC8.1).

### §2.3 ⛔ THE CROSS-VERSION HAZARD IS REAL AND IS THIS STORY'S TO AVOID, NOT TO INHERIT

§0.3: `runtime_checkable`'s `isinstance` behaves **differently on 3.11 vs 3.12/3.13**, and CI runs
3.10, 3.11 **and** 3.12. ⛔ **Do not write a guard whose verdict is `isinstance` against a
Protocol.** Every guard this story lands must be decided by structure (`ast`) or by static typing,
both of which are version-stable. This is `AI-E13-1` with a measured mechanism attached rather than
a slogan.

### §2.4 ⛔ THE PROTOCOL DOCSTRING'S PURITY PARAGRAPH IS CITED FROM ANOTHER MODULE

`argus/detectors/tool_runner.py:27` reads *"The 1.5 `Detector` protocol docstring says `run` 'MUST
be pure'"* and builds Story 2.6's whole pure/impure argument on it. ⛔ **Keep that sentence in the
Protocol docstring.** Dropping it silently breaks a citation in a `done` story's shipped module —
the `DF-INV-REFS-A` defect class, committed on purpose.

### §2.5 ⛔ GUARD VACUITY — THIS STORY'S VERSION

`AI-E14-1`. **This story's version:** a guard that asserts *"`Detector` has a `run` member"* or
*"the pins exist"* by reading the same text it was written from, and would pass against **any**
spelling including the shipped one. ⛔ **Every guard must be driven RED against the SHIPPED body
first, with its exact failure text recorded** (AC5.6). Two of this story's guards can be RED that
way and **must** be; one is a fence that is GREEN before and after **by design** and must be
labelled a fence, not a caught defect — the `DN-18-2-1`/`-30` and `DN-18-3-8`/`-09` precedent.

⚠️ **A second, subtler vacuity:** asserting the four detectors conform by *importing them and
checking `rule_id`/`run` exist at runtime* re-implements the shipped `isinstance` and inherits
§0.3's blindness. ⛔ **Structural (`ast`) or nothing.**

### §2.6 ⛔ THE WORKING TREE IS SHARED, ALREADY DIRTY, AND ONE FILE HAS A BYTE INVARIANT

- **A concurrent session commits to this same branch and five of its files are uncommitted right
  now** (§0.0). ⛔ **Stage by EXPLICIT PATH. Never `git add -A`, never `git add .`.** Verify with
  `git status --porcelain` — **not** `git diff --name-only`.
- **`deferred-work.md` carries a peer's uncommitted +19/−0 append.** ⛔ **Stage it
  HUNK-SELECTIVELY** so your note is committed and the peer's 19 lines stay uncaptured in the
  worktree. Story 18.3 did this and its review verified it afterwards; copy that.
- **`deferred-work.md` is LF-only with exactly one content `\r`** at offset 410,341. ⛔
  **Binary-mode edits only**, invariants re-verified after writing (bytes, `CRLF == 0`, lone
  `CR == 1`).
- ⛔ **`minions_core/apaa/` is DEAD.** Nothing here goes near it.

### §2.7 The idioms you need, so you do not go looking for them

- The house Protocol spelling is `argus/detectors/vacuous_test.py:404` (`_HasFilePath`) — copy its
  `@property … ...  # pragma: no cover - structural declaration` form exactly.
- `Callable` is imported **`from collections.abc`** in this tree (`tool_runner.py:102`), not from
  `typing`.
- `CoverageDepth` is `argus.ledger.coverage_ledger:60`; `base.py:46` already imports
  `CoverageLedgerEntry` from that module — extend the existing import, do not add a line.
- The structural-guard precedent is `TC-ArgusAgent-PRECISION-001-74`, which enforces
  `scripts/candidate_selection.py`'s import ban with an `ast` walk — *"which is what converts 'we
  did not look' from a promise into a property"*. **That is the shape AC5.1 wants.**
- Test function names carry the id: `def test_TC_ArgusAgent_DETECT_001_145_<snake_case_claim>() -> None:`
  — `tests/conftest.py`'s guard-fire recorder attributes REDs by that name.
- ⛔ Clear `__pycache__` and export `PYTHONDONTWRITEBYTECODE=1`. Story 16.5 lost a commit to a false
  RED from stale bytecode.

---

## §3 — AC ↔ TASK MAP

*(There to be checked, not trusted. Every AC is named by at least one task; every task cites the AC
it discharges.)*

| AC | discharged by |
|---|---|
| AC1 — the Protocol states the contract the code has | Task 2 |
| AC2 — every detector is pinned to it, inside `argus/` | Task 2 |
| AC3 — the erased type at the single construction point is restored | Task 3 |
| AC4 — `base.py` stops naming fields the models lack | Task 3 |
| AC5 — three guards, each RED against the shipped body where it can be | Task 1, Task 2, Task 4 |
| AC6 — no detector output changes, proven three ways | Task 0, Task 1, Task 5 |
| AC7 — the disposition is recorded append-only, and what stays open is named | Task 6, Task 8 |
| AC8 — scope, gates, dogfood regeneration, the commit arc | Task 0, Task 7, Task 8 |
| AC9 — escalate, do not decide | all tasks |

---

## Acceptance Criteria

### AC1 — THE `Detector` PROTOCOL STATES THE CONTRACT THE CODE ACTUALLY HAS

- **AC1.1 — the arm is TAKEN, not deferred.** `argus/detectors/base.py` keeps a `Detector` Protocol
  and it is **narrowed to the members all four shipped detectors satisfy**: a `rule_id` readable as
  `str`, and a `run` readable as a callable returning `DetectorResult`. ⛔ **The Protocol MUST NOT
  describe `run`'s parameters.** `Callable[..., DetectorResult]` is the measured-correct spelling
  (§0.4); `def run(self, *args: object, **kwargs: object)`, `**kwargs: Any`, and a settable
  `run: Callable[...]` attribute are **forbidden by measurement** — each rejects all four detectors.
- **AC1.2 — the four shipped detectors are accepted, unedited.** With the new Protocol in place and
  **no change to any `run` signature, body, decorator or call site**, all four are statically
  assignable to `Detector`. ⛔ Proven by `mypy argus` being clean **with AC2's pins present** — the
  pins ARE the proof.
- **AC1.3 — `@runtime_checkable` is REMOVED**, and `Detector` is no longer usable with
  `isinstance`/`issubclass`. Reason recorded in the module (one sentence) and in the ledger note:
  the runtime check is measurably vacuous on 3.11/3.12/3.13 alike (§0.3) and its verdict is not
  stable across the CI matrix. ⛔ **If a future reader wants `isinstance` back, that is a decision,
  not an omission** — say so in the docstring.
- **AC1.4 — the AR8 purity paragraph SURVIVES** in the Protocol docstring, because
  `tool_runner.py:27` cites it (§2.4). ⛔ Its wording may be tightened; its claim may not be dropped.
- **AC1.5 — `"Detector"` stays in `__all__`** and the name is not renamed. This story makes the
  symbol mean something; it does not remove or move it.
- **AC1.6 — the module's "Contract decisions locked here" block (`:19`–`:36`) is updated** so the
  bullet describing the Protocol says what the Protocol now is. ⛔ **Correct it; do not delete it.**

### AC2 — EVERY DETECTOR IS STATICALLY PINNED TO IT, INSIDE `argus/`

- **AC2.1 — four pins, one per detector module.** `vacuous_test.py`, `secret_scan.py`,
  `tool_runner.py` and `orphan_code.py` each carry a static conformance pin binding their detector
  class to `Detector`, **inside `argus/`** so `mypy argus` — the blocking CI gate — checks it.
- **AC2.2 — the pin costs nothing at runtime.** It lives under `if TYPE_CHECKING:` (or an
  equivalent construct that is provably never executed). ⛔ **No module-level detector instance is
  constructed at import time**, no `__init__` side effect is introduced, and
  `argus/detectors/__init__.py` is **not** touched (its Story 1.5 note *"`secret_scan` is Story 2.5
  … do NOT add them here"* is a locked decision).
- **AC2.3 — the pin is non-vacuous, proven by execution.** Mutating any pinned detector so it
  regresses the contract — `rule_id` removed, `rule_id` non-`str`, `run` removed, `run` returning
  something other than `DetectorResult`, `run` non-callable — makes **`mypy argus` FAIL**. ⛔ **At
  least three of those five mutations are executed and their exact `mypy` output recorded.**
- **AC2.4 — no new import edge.** The pins import `Detector` from `argus.detectors.base`, which all
  four modules already import from. ⛔ `tests/test_no_web_imports.py`'s import-isolation gate stays
  green and `argus.detectors.*` stays a leaf.

### AC3 — THE ERASED TYPE AT THE SINGLE CONSTRUCTION POINT IS RESTORED

- **AC3.1** — `build_recording`'s `depth_supported` parameter is annotated
  **`CoverageDepth | None`**, and the `# type: ignore[arg-type]` at the `Recording(...)` construction
  is **DELETED**.
- **AC3.2** — ⛔ **`argus/detectors/base.py` contains ZERO `# type: ignore` comments** afterwards.
  The other 30 in `argus/` are **not** touched.
- **AC3.3** — proven RED-before / GREEN-after by execution: a probe calling
  `build_recording(draft, depth_supported="not-a-depth")` is **silent** under the shipped body and
  **an error** under the changed one, with both `mypy` outputs recorded. ⛔ The **runtime**
  behaviour is unchanged — `pydantic` still raises `ValidationError` — and that is asserted, not
  assumed.
- **AC3.4** — `mypy argus` stays **`Success … 95 source files`**. All seven existing
  `depth_supported=` call sites keep type-checking unedited; ⛔ **if any call site must change, STOP**
  (AC9).
- **AC3.5** — `argus/ledger/recording.py` is **byte-unchanged**. No model field moves; NFR-M2
  (frozen, additive-only contracts) is not exercised.

### AC4 — `base.py` STOPS NAMING FIELDS THE MODELS DO NOT HAVE

- **AC4.1** — `FindingDraft`'s docstring (`:63`–`:72`) is corrected to describe the fields the model
  **actually** has, measured from `FindingDraft.model_fields` rather than transcribed (§0.6).
- **AC4.2** — the correction **states the two absences rather than deleting the sentence**:
  `depth_supported` is a **parameter of `build_recording`**, not a draft field; and **no evidence
  field exists on any of the three models** — a repository-wide gap Story 18.2 measured and left
  open. ⛔ **No field is added and no FR is amended** (`DN-18-4-6`).
- **AC4.3** — the module docstring's own summary of these contracts is checked against the same
  measurement and corrected wherever it repeats the claim. ⛔ **Every remaining sentence in
  `base.py` must be true of the code as it stands after this story.**

### AC5 — THREE GUARDS, EACH RED AGAINST THE SHIPPED BODY WHERE IT CAN BE

⛔ All three live in **`tests/test_detector_base.py`**, continuing `TC-ArgusAgent-DETECT-001` at
**`-145`** (`DN-18-4-4`). That file is Story 1.5's, and editing it is **chartered by the epic**,
which offers *"or it is deleted and its lone test with it"*.

- **AC5.1 — `-145`, THE STRUCTURAL PIN GUARD (RED against the shipped tree).** An `ast` walk over
  every module in `argus/detectors/` asserts: **every class that defines a `run` method annotated
  `-> DetectorResult` also carries, in its own module, a static conformance pin against `Detector`.**
  ⛔ Non-vacuity first (`AI-E11-1`): the walk must assert it **found at least four such classes**
  before asserting anything about pins — an empty population passes forever. ⛔ **Proven RED against
  the shipped tree, where the count is 4 classes / 0 pins**, with the failure text recorded.
  ⛔ **This is the guard that makes a fifth, unpinned detector impossible**, and it is the reason
  this story is not decoration.
- **AC5.2 — `-146`, THE PROTOCOL-SHAPE FENCE (GREEN before and after, BY DESIGN).** Asserts, by
  reading `base.py`'s AST: `Detector` is **not** decorated `runtime_checkable`; its members are
  exactly `rule_id` and `run`; and `run`'s declared return type is `Callable[..., DetectorResult]`.
  ⛔ **Label it a FENCE, not a caught defect** (`DN-18-4-5`, the `-30`/`-09` precedent). Its
  non-vacuity is proven by executing it against the **shipped** Protocol text, where it is RED —
  record that output.
- **AC5.3 — `-84` IS REWRITTEN, NOT DELETED.** `test_vacuous_detector_satisfies_protocol` currently
  reads `assert isinstance(VacuousTestDetector(), Detector)` and would raise `TypeError` after
  AC1.3. It is rewritten to assert **structurally** — no `isinstance`, no `issubclass` (§2.3) —
  that **all four** detector classes expose a `str` `rule_id` and a callable `run` whose declared
  return type is `DetectorResult`. ⛔ **The id `-84` is KEPT** so Story 1.5's record
  (*"Detector satisfies the `Detector` Protocol (TC-84)"*) stays true, and the assertion is
  **strengthened from one detector to four**.
- **AC5.4** — ⛔ **NO guard in this story uses `isinstance` or `issubclass` against a Protocol**
  (§2.3, §0.3).
- **AC5.5** — `tests/test_detector_base.py` stays ≤ 1,200 lines (NFR-M1) and its four existing
  `build_recording` cases (`-80`..`-83`) are **left exactly as they are**.
- **AC5.6** — ⛔ **Every RED is observed and its exact text recorded in the completion notes before
  the change is made.** `AI-E14-1`: an author-driven RED is vacuity evidence, not *"this guard
  caught a defect"* — say which is which.

### AC6 — NO DETECTOR OUTPUT CHANGES, PROVEN THREE WAYS

The epic's second AC: *"this story changes no detector output, proven by re-running the suite and
the 1,032-finding harness."*

- **AC6.1 — BY CONSTRUCTION.** A docstring-stripped AST comparison of each of the five changed
  `argus/` modules shows the **only** executable differences are: the Protocol's member declarations,
  the removed decorator, the four `if TYPE_CHECKING:` blocks, the added imports, and the parameter
  annotation. ⛔ **`from __future__ import annotations` is in force in `base.py`, so annotations are
  strings at runtime and the `depth_supported` change is provably inert.** ⛔ `TYPE_CHECKING` is
  `False` at runtime — assert it, do not assume it.
- **AC6.2 — ENGINE-VS-ENGINE, over ONE identical population.** The shipped engine and the changed
  engine are both run over the **same** set of all tracked `*.py` files (**253** at contexting,
  **including this story's own edits**, the disclosure gap 18.1's review raised and 18.2 closed).
  ⛔ **The differing set must be EMPTY** — same finding count, same files, same per-file
  `DetectorResult`. Record both totals and the population size.
- **AC6.3 — THE SUITE AND THE HARNESS.** Full suite green (**1,729** collected at contexting, plus
  this story's two new cases). The **1,032-finding harness runs inside the suite** —
  `tests/test_silent_class.py` asserts `population_walked == 1032` over the committed
  `silent-class-record.json`, derived from `adjudication-set-13-5.json`. ⛔ **In addition, run
  `python scripts/build_silent_class_record.py --check`** and record its output (at contexting: OK,
  36 rows, round-trip clean, and it says in terms that it did **not** re-derive).
- **AC6.4 — THE FULL RE-DERIVATION IS ATTEMPTED, AND ITS OUTCOME RECORDED EITHER WAY.** All five
  pinned shas were measured **reachable** in their ratified checkouts at contexting
  (`ai-body-runtime 4480ffde`, `agent-markovich a5616686`, `minions ec63b729`,
  `xagents-webapp 33a86525`, `agent-smith 9ab774d7` — the last under `XAgents/Agent-Smith`), and
  Story 13.5's reader takes bytes from the **object database**, so a dirty checkout is not a
  blocker. Run `build_silent_class_record.py --checkout-root … --map …` with a **short**
  `--snapshot-root` (Windows `MAX_PATH`) and prove the committed artifacts unchanged. ⛔ **If a
  member raises `PinUnreachable` or `PinnedBytesRefusal`, record it BY NAME as a partial run** —
  ⛔ **never silently substitute working-tree bytes, and never soften the claim to hide the gap.**
- **AC6.5 — DOGFOOD.** `hardcoded_secret` over `argus/**` is expected to stay **39** and total LOC
  to move **33,703 → ~33,726** (§0.7, §0.8). ⛔ **Regenerate the three artifacts with their own
  renderer on a clean `argus/` tree; loosen no assertion.** Any count that moves is **disclosed with
  its measured cause**, exactly as 18.3 disclosed its 40 → 39.

### AC7 — THE DISPOSITION IS RECORDED, APPEND-ONLY, AND WHAT STAYS OPEN IS NAMED

- **AC7.1** — `DF-AUD-DETECT-F` is **CLOSED** in `deferred-work.md` by a **dated, append-only**
  note. ⛔ **The entry above it is NOT rewritten** (§3.4). The note records: the arm taken and its
  reason; that **`mypy` rejects all four detectors against the shipped Protocol**, which falsifies
  the entry's *"the widened signature is what makes them all satisfy it"*; that the lone test passes
  for `run = 42` on 3.11/3.12/3.13; that **"five concrete detectors" is four**; the measured shape
  that all four satisfy and the five decoys it rejects; and item B's before/after `mypy` outputs.
- **AC7.2** — ⛔ **The entry's own "honest counter-argument" is answered in terms, not ignored.**
  It says the repair may be *"delete the Protocol and the test"* because forcing a common signature
  would be worse. The note records that **no signature is forced**, and that its own sentence —
  *"`rule_id` + `DetectorResult` is the real shared contract and `run` is decoration"* — is exactly
  what the new Protocol encodes.
- **AC7.3** — the **status transition** on the entry is stated explicitly (`OPEN → CLOSED`, with the
  fix sha), and its `id`, `owner`, `category` and `severity` fields are **left unedited**.
- **AC7.4** — ⛔ **WHAT THE NOTE DOES NOT DISPOSITION, listed:** `DF-10-4-B`, `DF-10-3-B`,
  `DF-10-3-C`, `DF-AUD-DETECT-C`, `DF-AUD-DETECT-D`, `DF-INV-MERGE-A`, `DF-INV-WHEEL-A`,
  `DF-INV-REFS-A` — all stay **OPEN and untouched** — and **`DF-13-5-A` stays OPEN and UNSPENT**.
  No FR is amended, no model field is added, no threshold moves, no finding becomes verdict-eligible,
  the ≥80% precision keystone stays **NOT CLEARED**, the gate stays `BLOCKED`, and `architecture.md`,
  `E-PRD/prd.md`, `epics.md` and every `done` story's record are **unedited**.
- **AC7.5** — the three §1.3 observations (`OrphanCodeDetector.rule_id` outside
  `FROZEN_DETECTOR_SET`; the unenforced `FROZEN_DETECTOR_SET` mirror comment; the FR10 evidence gap)
  are **RECORDED in the note and in the completion notes, and NOT FILED** (`AI-E9-8` — filing and
  scheduling are the Engineering Lead's).
- **AC7.6** — ⛔ **grep `deferred-work.md` by id before writing anything** (`DF-INV-LEDGER-A`); line
  numbers drift. Re-verify the byte invariants after the edit (§2.6).

### AC8 — SCOPE, GATES, DOGFOOD REGENERATION AND THE COMMIT ARC

- **AC8.1 — ⛔ THE WRITE SET IS EXACTLY:**
  1. `argus/detectors/base.py` — UPDATE (AC1, AC3, AC4)
  2. `argus/detectors/vacuous_test.py` — UPDATE, **pin + imports only**
  3. `argus/detectors/secret_scan.py` — UPDATE, **pin + imports only**
  4. `argus/detectors/tool_runner.py` — UPDATE, **pin + imports only**
  5. `argus/detectors/orphan_code.py` — UPDATE, **pin + imports only**
  6. `tests/test_detector_base.py` — UPDATE (AC5)
  7. `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — APPEND-ONLY
  8. the three regenerated dogfood artifacts — **by their own renderer only**
  9. this story file
  10. `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — status transitions only

  ⛔ **NOT in it:** `argus/pipeline.py`, `argus/pipeline_stages.py`, `argus/ledger/**`,
  `argus/cache/**`, `argus/detectors/__init__.py`, `argus/detectors/provenance_scan.py`,
  `argus/detectors/secret_suppression.py`, `argus/audit/**`, `argus/precision/**`, `argus/reports/**`,
  `scripts/**`, any other test module, `architecture.md`, `E-PRD/prd.md`, `epics.md`, any `done`
  story's record, and **anything under `minions_core/apaa/`**.
- **AC8.2** — the commit arc is **four** commits, in this order: **`chore`** (this story file +
  `sprint-status` → `in-progress`) → **`feat`** (`argus/` + `tests/`) → **`chore`** (regenerate the
  three dogfood artifacts on a **clean** `argus/`) → **`docs`** (ledger + this story's record,
  **ledger first in the diff**). ⛔ Commit messages **pure ASCII** (`DF-16-6-F`), and the **`feat`**
  commit carries the whole-line trailer **`Evidence-partition: none`** — ⛔ **write it the FIRST
  time**; Story 18.1 lost a sha to it.
- **AC8.3** — ⛔ `DF-INV-MERGE-A`: if the PR lands squashed or rebased, re-run
  `python scripts/regenerate_dogfood_artifacts.py` on `master` and commit, or
  `TC-ArgusAgent-DOGFOOD-001-49` reddens `master` after the fact.
- **AC8.4** — green at the end, **every exit code recorded**: the full suite (`python -m pytest -q`,
  and again with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`), coverage `--cov-fail-under=80`,
  `mypy argus`, `bandit -r argus --severity-level medium`, `tests/test_module_size_ceiling.py`,
  `tests/test_no_web_imports.py`, `tests/test_v1_commitment_closure.py`,
  `tests/test_governance_record_integrity.py`, `tests/test_dogfood_plan.py`,
  `tests/test_dogfood_proof.py`, `tests/test_dogfood_artifact_currency.py`,
  `tests/test_silent_class.py`, `tests/test_cache_key.py`, `tests/test_cache_invalidation.py`,
  `tests/test_release_preflight.py`, `tests/test_gate_*.py`. ⛔ Run with
  `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared.
- **AC8.5** — NFR-M1: every touched module stays ≤ **1,200** physical lines. **Split, never shave,
  never exempt.**
- **AC8.6** — `AI-E13-1`: the local run is Windows-only and is recorded as **LOCAL**. ⛔ **This
  story's cross-version claim (§0.3/§2.3) is the one place where that matters most** — the CI
  ubuntu matrix on 3.10/3.11/3.12 owns it, and it is claimed only after it is green at the pushed
  sha.
- **AC8.7** — ⛔ stage by **explicit path**, `deferred-work.md` **hunk-selectively** (§2.6); verify
  the final write set equals AC8.1 exactly with `git status --porcelain`, and confirm none of the
  five §0.0 files rode along unless its own session had already committed it.

### AC9 — ESCALATE, DO NOT DECIDE

⛔ **STOP and escalate — do not decide — if any of these becomes necessary:**

- ⛔ **§0.4 does not reproduce** — i.e. some Protocol shape that all four detectors satisfy cannot
  be found. **The fallback is NOT deletion.** Deleting the Protocol removes a public symbol, a
  `done` story's contract and a test id, and makes `architecture.md:1174` stale; that is the
  Engineering Lead's call, not a dev-loop fallback. **Report the measurement and STOP.**
- any detector's **`run` signature, body, decorator or call site** must change to make it conform;
- `argus/pipeline_stages.py`, `argus/pipeline.py` or any file under `argus/cache/`,
  `argus/ledger/`, `argus/audit/` or `argus/precision/` must be edited;
- a **new dispatch site, registry, base class or `Sequence[Detector]`** looks necessary (§2.2);
- a model field must be added, removed or retyped, or `CACHE_KEY_SCHEMA_VERSION` /
  any `code_identity` must move;
- **any** detector output moves — a single finding appearing, disappearing or changing span (AC6.2);
- a **guard must be loosened, skipped or deleted** to go green (`DF-8-5-B`);
- `architecture.md`, `E-PRD/prd.md`, `epics.md` or any `done` story's record must be edited;
- a **new `DF-*` entry** looks necessary (§1.3) — `AI-E9-8`: recording is this story's job, filing
  is the Engineering Lead's;
- `DF-13-5-A` must be spent, a member ratified, a protocol row added, or an FR amended;
- a finding must become **verdict-eligible**, or the precision gate must move;
- any `DN-*` must be reopened. ⛔ **A `DN-*` you disagree with is an escalation, not a story
  decision.**

---

## Dev Notes

### Decisions this story TAKES, each with its rejected alternative

- **`DN-18-4-1` — THE PROTOCOL IS MADE LOAD-BEARING; IT IS NOT DELETED.** The either/or is decided
  by §0.2 and §0.4. The entry's counter-argument assumes the only way to make it constrain something
  is to force a common `run` signature; **measured, there is a shape that constrains `rule_id`'s
  type and `run`'s callability and return type, that all four detectors satisfy unedited, and that
  rejects five decoys the shipped one accepts.** The entry's own words — *"`rule_id` +
  `DetectorResult` is the real shared contract"* — describe that shape exactly. **Deletion would
  remove the name and leave four shipped docstrings asserting a conformance nothing checks.**
  *Rejected: delete the Protocol and its lone test (the entry's counter-argument).* It throws away a
  real, enforceable invariant; it makes `architecture.md:1174` stale, which would force this epic's
  first architecture edit for a cosmetic reason; it deletes a public `__all__` symbol from a shipped
  distribution and a test id a `done` story's record names; and it leaves `argus/` carrying four
  false conformance claims with nothing to check them against. ⛔ **It is also the irreversible arm
  of the two: a narrowed Protocol can be deleted later by anyone; a deleted one has to be
  re-litigated.**
  *Rejected: leave it alone and close the entry as "won't fix".* §0.2 shows the middle position is
  worse than the entry knew — the contract is not decoration, it is unusable — and the epic's AC
  requires a choice.
- **`DN-18-4-2` — BOTH MEMBERS ARE READ-ONLY PROPERTIES.** Measured (§0.4): `rule_id: str` as a
  settable data member forces `issubclass` to raise `TypeError` and makes the member invariant;
  `run: Callable[...]` as a settable attribute is rejected for all four with *"expected settable
  variable, got read-only attribute"*. The property spelling is the only one that passes, **and it
  is already the house idiom** at `vacuous_test.py:404`.
  *Rejected: dropping `run` from the Protocol entirely* (`rule_id: str` alone also type-checks). It
  constrains nothing about the result and would make the Protocol nearly content-free — the
  deletion arm with extra steps.
- **`DN-18-4-3` — `@runtime_checkable` IS DROPPED.** §0.3: `isinstance` is measurably vacuous on
  every interpreter CI runs, and its verdict **differs** between 3.11 and 3.12/3.13. A Protocol
  whose enforcement is static should not also offer a weaker runtime check a future reader will
  mistake for enforcement.
  *Rejected: keeping it so `isinstance` still works.* Nothing in the tree calls it except the test
  this story rewrites; keeping it preserves the exact assertion that accepts `run = 42`. **Re-adding
  a decorator is a one-line, reversible change if a real need appears.**
- **`DN-18-4-4` — THE GUARDS EXTEND `tests/test_detector_base.py`; NO NEW MODULE.** One module, one
  subject (`DN-18-1-4`/`DN-18-2-4`/`DN-18-3-4`): that file's subject **is** `argus/detectors/base.py`,
  it is 89 lines against a 1,200 ceiling, and it holds the one test that must change anyway.
  *Rejected: a new `tests/test_detector_protocol.py`.* Splits one module's guards across two files
  and leaves the vacuous `-84` behind in the old one.
  *Rejected: leaving `test_detector_base.py` untouched as a `done` story's module.* Impossible —
  `-84` raises `TypeError` after AC1.3 — and **the epic's AC explicitly authorises touching it**.
- **`DN-18-4-5` — `-146` IS A FENCE, NOT A WITNESS, AND IS LABELLED AS ONE.** It is GREEN before and
  after the *behaviour* it protects, and is RED only against the shipped Protocol *text*. `AI-E14-1`
  makes an author-driven RED vacuity evidence; this is a **contract pin**, and calling it a caught
  defect is the over-claim this repository keeps withdrawing. `-30` (18.2) and `-09` (18.3) are the
  precedent.
  *Rejected: omitting it.* It is the only thing that stops `@runtime_checkable` and the `*args`
  signature being reinstated by a future well-meaning edit.
- **`DN-18-4-6` — ITEM C CORRECTS PROSE ONLY; NO FIELD IS ADDED.** 18.2 measured the evidence gap as
  repository-wide (`Recording`'s ten fields include none that could hold a count) and concluded
  *"one detector widened in isolation is the wrong shape of repair"*. This story states the absence
  accurately and leaves the gap OPEN.
  *Rejected: adding an `evidence` field to `FindingDraft`/`Recording`.* NFR-M2 contract change, FR10
  scope, verdict-surface implications — a different story and an escalation (AC9).
  *Rejected: deleting the false sentence without saying what is true.* A silent deletion loses the
  measurement; `AI-E12-3` — a disposition in prose that is not recorded is not a disposition.
- **`DN-18-4-7` — THIS STORY IS OUTPUT-NEUTRAL AND MUST PROVE IT.** The inverse of `DN-18-3-3`.
  18.2's AC2.1 shape — *"the differing set must be EMPTY"* — **is** the right shape here, and AC6.2
  takes it, including 18.2's improvement of running both engines over ONE identical population that
  includes the story's own edits.
  *Rejected: proving neutrality by the suite alone.* The suite does not scan `argus/**` with the
  detectors; the dogfood artifacts and the sweep do.
- **`DN-18-4-8` — NO `code_identity` BUMP.** §0.9: `base.py` has no descriptor, no detector logic
  changes, and the output is proven identical. `DN-18-2-5`'s arm for `DN-18-2-5`'s reason.
  *Rejected: bumping anyway "to be safe".* It would invalidate every cached closure for a change
  proven to have no output — the exact desync `DN-18-3-6` exists to avoid in the other direction,
  and it would drag `argus/cache/**` into a fenced write set.

### Locked decisions this story CITES rather than reopens

- **Story 1.5** — `DetectorResult` / `FindingDraft` / `DegradedCondition` frozen `extra="forbid"`;
  the content-derived recording id; the FR13 locator-or-reject rule enforced at the DATA layer.
  ⛔ All unchanged. The Protocol's **existence** is Story 1.5's; its **shape** is what this story
  repairs.
- **Story 1.5 / `argus/detectors/__init__.py`** — *"`secret_scan` is Story 2.5, `tool_runner` Story
  2.6, `orphan_code` Epic 6 — do NOT add them here"*. ⛔ The pins therefore live in the detector
  modules, never in the package `__init__`.
- **Story 2.6** — the pure/impure split and the disclosure at `tool_runner.py:27` that this
  detector's core is impure. ⛔ Cited, kept, not relitigated (§2.4).
- **Story 5.1 / `DN-DETECTORSET`** — the detector-set hash is over the declared frozen descriptor
  tuple. `DN-18-4-8` rests on it.
- **Story 10.4 / `DF-10-4-B`** — `DetectorResult.degraded` has zero production readers. OPEN;
  ⛔ **prior art for this story's argument, not its subject.**
- **Story 13.5** — a corpus member is audited from the bytes of its PINNED GIT OBJECT, and a
  deviation is a NAMED refusal. AC6.4 rests on it.
- **Stories 18.1 / 18.2 / 18.3 (`DN-18-1-*`, `DN-18-2-*`, `DN-18-3-*`)** — `done`; not reopened.
- **architecture §Guard-fire ledger (2026-08-23)** — an author-driven RED is vacuity evidence.
  `DN-18-4-5` rests on it.

### Open ledger entries bearing on this story — verify against `deferred-work.md` on disk

| entry | bearing |
|---|---|
| **`DF-AUD-DETECT-F`** | **THE SUBJECT.** Items A and B are discharged (AC1–AC3, AC7). Its central mechanism claim and its detector count are falsified append-only (§0.1, §0.2). |
| **`DF-10-4-B`** | ⛔ OPEN. Same class, same module, **untouched**. Its `target_story` names a `done` story — **Story 17.5's guard, not this story's re-homing** (§1.3). |
| **`DF-AUD-DETECT-C`** | ⛔ OPEN. Detector cost. **No timing figure is taken here.** |
| **`DF-AUD-DETECT-D`** | Story 17.3. Not this story. |
| **`DF-AUD-DETECT-A` / `-B` / `-E`** | CLOSED by 18.1 / 18.2 / 18.3. ⛔ Their notes are the FORM for yours; **none is edited**. |
| **`DF-10-3-B` / `DF-10-3-C`** | ⛔ OPEN, untouched, out of scope. |
| **`DF-INV-MERGE-A`** | OPEN, DECIDED-NOT-YET-APPLIED. Governs how this PR may land (AC8.3). |
| **`DF-INV-WHEEL-A`** | OPEN. Running Argus inside its own repo reddens `TC-ArgusAgent-DOCS-001-54` for an unrelated reason. If you hit that red, it is **not yours**. |
| **`DF-INV-REFS-A`** | OPEN. Six referenced ids do not resolve. Do not "fix" one in passing — and §2.4 is about not creating a seventh. |
| **`DF-13-5-A`** | ⛔ **OPEN and UNSPENT.** Nothing here spends it. |
| **`DF-8-5-B`** | *"Do not close it by loosening an assertion."* The standing rule over AC5 and AC9. |
| **`DF-INV-LEDGER-A`** | Why AC7.6 says grep before writing. |
| **`DF-16-6-F`** | Commit messages are pure ASCII (AC8.2). |

### Dependencies — none are added, and that is a requirement

`base.py` imports `hashlib`, `typing`, `pydantic`, and three first-party modules. **This story adds
`collections.abc.Callable` (stdlib), `typing.TYPE_CHECKING` (stdlib), and `CoverageDepth` from a
module `base.py` already imports from.** ⛔ **No third-party dependency is added, removed or
version-moved**, and no new inter-package import edge is created (AC2.4, §0.5).

⛔ **Nothing here requires web research.** The constructs are `typing`/`collections.abc` primitives
whose semantics are pinned by CPython, and every behavioural claim in §0 was obtained by running
them. ⚠️ **Two CPython details are load-bearing and were verified by execution on 3.11.15, 3.12.10
and 3.13.14 rather than assumed:**

1. `runtime_checkable`'s `isinstance` switched from `hasattr` to `inspect.getattr_static` in **3.12**
   — a `__getattr__`-provided member satisfies on 3.11 and does **not** on 3.12/3.13 (§0.3).
   ⛔ **CI runs 3.10, 3.11 and 3.12**, so this is a live matrix difference, not trivia.
2. `runtime_checkable` `isinstance` **never** checks callability or signature on any of the three —
   `run = 42` passes everywhere.

### Standing rules (non-negotiable)

- **AR7** — one arithmetic, one vocabulary, never forked. ⛔ A runtime re-implementation of the type
  checker's conformance rule would be that fork (§2.5).
- **AR8** — pure/impure separation. `base.py` is PURE and stays PURE; the pins execute nothing.
- **AR10** — typed failure; no bare `except: pass`, no `print()`.
- **NFR-P1** — no clock, randomness, network or host-dependent comparison on any decision path.
- **NFR-S1 / NFR-S2** — no source byte, no secret value, no absolute host path in any artifact,
  message or test assertion.
- **NFR-M1** — 1,200 physical lines per module. **Split, never shave, never exempt.**
- **NFR-M2** — frozen, additive-only contracts. ⛔ No model field moves here.
- **`AI-E11-1`** — every guard asserts its population is non-empty before asserting an absence.
  ⛔ AC5.1's *"found at least four detector classes"* is this rule.
- **`AI-E13-1`** — the local suite is Windows-only; CI runs an ubuntu matrix.
- **`AI-E12-3` / `AI-E12-6`** — *a disposition recorded in prose and not in the ledger is not a
  disposition.*
- **`AI-E14-1`** — an author-driven RED is vacuity evidence, not "this guard caught a defect".
- **`AI-E9-7`** — do not re-derive an argument from a stale figure.
- **`AI-E9-8`** — do not assert a new finding onto an existing story to give it a home.

### Previous-story intelligence

**Story 18.3 (`done`, this epic, immediately before) — what it hands you:**

1. ⛔ **It fenced `argus/detectors/base.py` OUT of its write set by name**, calling it *"Story 18.4's
   fence"*. The module is untouched since Story 1.5's era and is **yours**.
2. ⛔ **It bumped `code_identity` to `secret_scan.v2` and moved the detector-set hash to
   `fbec7912…`.** Your story does **not** bump (`DN-18-4-8`) — read `DN-18-3-6` and `DN-18-2-5`
   together before you assume either way.
3. **Its `secret_scan.py` is 630 lines and its two repaired regex source lines self-match as
   `high_entropy_string`.** Your pin appends **7 lines with no quoted literal**; §0.7 measured the
   self-scan at **7 → 7**. ⛔ **Re-measure it; do not assume.**
4. **Its ledger-staging discipline is the one to copy:** hunk-selective staging that left the peer's
   19-line append uncaptured, verified afterwards by its review.
5. **Its disclosure discipline is the one to copy:** the dogfood count came out 39, not the predicted
   37, and it **measured the cause and disclosed it** rather than re-spelling the source to hide it.

**Story 18.2 (`done`)** is the closest structural precedent: an output-NEUTRAL change proven
engine-vs-engine over one identical population, with the disposition recorded append-only and the
things it does not disposition listed. ⛔ **Its RECORDED-NOT-FILED item (a) is your item C** — it
named `base.py` as *"Story 18.4's module"* and left it byte-unchanged for you.

**Story 18.1 (`done`)** lost a sha to a missing `Evidence-partition:` trailer and took a review
finding for a sweep computed over a population that excluded its own new test file. ⛔ **Both are
solved problems; do not re-open either** (AC6.2, AC8.2).

**Story 1.5** created this Protocol, this builder and these models. ⛔ **Read its record; edit it
never.** Its line *"Detector satisfies the `Detector` Protocol (TC-84)"* is why AC5.3 keeps the id
alive rather than deleting it.

### Git intelligence

Recent arc (last 8 commits): `57a278f → 2cc5128 → 25ff87f → 62fd1b9` is Story 18.2's four-commit arc;
`e9e649e → 9e3fdc2 → 93a7502 → bd110c6` is Story 18.3's, in the same shape. ⛔ **Yours is the third
in that shape and the last of the epic.**

- **`argus/` is quiet again.** The last change to it is `9e3fdc2` (18.3's `feat`), and the three
  dogfood artifacts were regenerated for exactly that sha at `93a7502`. **Your `feat` moves past it,
  so those artifacts go stale and must be regenerated** (§0.8, AC6.5).
- **All three prior stories in this epic were reviewed by re-execution rather than by reading**, and
  all three reviews independently reproduced the story's headline measurement — 18.3's review
  re-derived the regex censuses and the byte invariants from scratch. ⛔ **Expect yours to be
  re-executed. Every figure you write down should be one you can hand someone a command for.**
- **The culture this week is: measure, then withdraw what the measurement does not support.** 18.1
  falsified `DF-10-3-B`'s safety claim; 18.2 falsified `DF-AUD-DETECT-B`'s Story-2.5 reasoning; 18.3
  falsified three of `DF-AUD-DETECT-E`'s premises. **§0.1–§0.4 do it again to `DF-AUD-DETECT-F`.**
  Do it once more in your completion notes if Task 0 disagrees with any row of §0.

### References

- [epics.md](../epics.md) — `## Epic 18` (~line 3609) and `### Story 18.4` (~3703). ⛔ Its *"AWAITING
  OPERATOR APPROVAL"* paragraph and the append-only approval note beneath it are **left as written**
  (§3.4). **Not a blocker; not to be edited.**
- [sprint-change-proposal-2026-08-24.md](../sprint-change-proposal-2026-08-24.md) — §1 (the audit),
  §2 (impact: `prd.md` **None**, `architecture.md` **None**), §4 (Epic 18's four stories).
  **APPROVED 2026-08-24 by XAgent007 (Engineering Lead).**
- [deferred-work.md](../deferred-work.md) — **`DF-AUD-DETECT-F`** (~line 6813, with its `id` block at
  ~6821 and its two ⚠️ paragraphs at ~6828/~6834), `DF-10-4-B` (~1930), the `DF-AUD-DETECT-A`/`-B`/
  `-E` closure notes (the FORM for yours), the Epic 17/18 scheduling table (~6890). ⛔ **Line numbers
  drift; grep by id.**
- [18-2-the-redaction-call-keeps-the-evidence-it-computes.md](18-2-the-redaction-call-keeps-the-evidence-it-computes.md)
  and [18-3-two-regex-precision-defects.md](18-3-two-regex-precision-defects.md) — ⛔ **Read; never
  edit** (both `done`). 18.2 for the neutrality proof shape; 18.3 for the staging and disclosure
  discipline.
- [1-5-heuristic-vacuous-test-detector-tier-a-vacuous-path-ast-subset.md](1-5-heuristic-vacuous-test-detector-tier-a-vacuous-path-ast-subset.md)
  — the Protocol's origin, its scope fence and `TC-84`. ⛔ **Read; never edit.**
- [architecture.md](../architecture.md) — `:1174` (this module in the directory tree — ⛔ **stays
  true under the arm taken**), `:1148` (the guard-fire rule `DN-18-4-5` rests on), `:1138` (Story
  13.5's corpus-pin provenance rule AC6.4 rests on). ⛔ **Read, do not edit** (AC7.4).
- `argus/detectors/base.py` — the module under change. ⛔ **Read all 204 lines before touching one**:
  the docstring's "Contract decisions locked here" block (`:19`–`:36`), `FindingDraft` (`:63`),
  `Detector` (`:126`), `_recording_id` (`:142`), `build_recording` (`:163`).
- `argus/detectors/vacuous_test.py:404` — **`_HasFilePath`**, the house Protocol idiom to copy.
- `argus/audit/ports.py:47` + `argus/audit/deep_pass.py:405` — **`LLMDispatchPort`**, this
  repository's example of a Protocol in a real production type position.
- `argus/pipeline_stages.py:249`–`:251`, `:348` — the four concrete construction sites. ⛔ **Read;
  do not edit** (§2.2).
- `argus/ledger/recording.py:111`–`:120` — `Recording.rule_id` / `depth_supported`. ⛔ **Read; do not
  edit.**
- `argus/cache/key.py:186` — `FROZEN_DETECTOR_SET` and the comment §1.3 records. ⛔ **Read; do not
  edit.**
- `tests/test_detector_base.py` — the one file this story edits under `tests/`.
- `scripts/candidate_selection.py` + `TC-ArgusAgent-PRECISION-001-74` — the `ast`-walk guard shape
  AC5.1 copies.
- `scripts/build_silent_class_record.py` — the 1,032-finding harness (AC6.3, AC6.4).
- `.github/workflows/audit-ci.yml:15` (the 3.10/3.11/3.12 matrix) and `:70` (`mypy argus`) — the two
  facts §2.1 and §2.3 rest on.

---

## Tasks & Subtasks

### ⛔ Task 0 — RE-MEASURE §0 BEFORE WRITING ANYTHING (AC6.1, AC8.4)

- [x] `git status --porcelain` — record it. ⚠️ **Expect it to be non-empty** (§0.0: five
      Story-18.1/18.2/18.3 files, one of them a +19/−0 peer append in `deferred-work.md`). Record
      which files are not yours **before** you stage anything.
- [x] Clear `__pycache__`; export `PYTHONDONTWRITEBYTECODE=1`.
- [x] Re-run §0.1's reference census. **Expect: `Detector` imported by exactly one file
      (`tests/test_detector_base.py`), used at one line, and FOUR detector classes** — not five. If
      a fifth detector has appeared, **STOP and report** (AC5.1's population changes).
- [x] Re-run §0.2's `mypy` probe. **Expect 4 of 4 REJECTED**, with the `Expected:`/`Got:` notes.
      ⛔ **This is the premise the whole arm rests on. If it does not reproduce, STOP** (AC9).
- [x] Re-run §0.3's decoy matrix on the local interpreter **and** on 3.12 if available. **Expect
      `run = 42` → True on every version** and the `__getattr__` row to differ between 3.11 and
      3.12+.
- [x] Re-run §0.4's five shape probes. **Expect exactly one shape accepted by all four**, and that
      shape to reject **five of five** decoys.
- [x] Re-run §0.5's item-B probe against the shipped body. **Expect `mypy` SILENT and `pydantic`
      raising at runtime.**
- [x] Re-read `FindingDraft.model_fields` / `Recording.model_fields` (§0.6). **Expect eight and ten
      fields, with no `depth_supported` on the draft and no evidence field anywhere.**
- [x] Full suite (**expect 1,729 collected, exit 0**), `mypy argus` (**95 files, clean**), `bandit`
      (**clean**), coverage. Record all four.
- [x] Re-measure §0.0's byte invariants for `deferred-work.md` and `sprint-status.yaml`, and the
      next free `TC-ArgusAgent-DETECT-001` id (**expect -145**).
- [x] Read the committed dogfood numbers (**expect total LOC 33,703, `hardcoded_secret` 39**).
- [x] `python scripts/build_silent_class_record.py --check` — **expect OK / 36 rows / not
      re-derived** (AC6.3).
- [x] Record every figure that came out different. **Expect at least one.**

### Task 1 — THE NEUTRALITY INSTRUMENT, BUILT BEFORE THE CHANGE (AC6.1, AC6.2)

- [x] Write the engine-vs-engine sweep as a throwaway script **outside the repository** that runs
      the shipped and changed detector bodies over the SAME tracked `*.py` population (**253 at
      contexting, including the files this story edits**) and diffs per-file `DetectorResult`s.
- [x] Take the **before** baseline now, with the shipped engine. Record counts and population size.
- [x] Write the docstring-stripped AST comparator for the five changed modules (AC6.1) — 18.2's
      instrument; re-derive it, do not copy a number from its record.

### Task 2 — THE PROTOCOL, THE PINS AND THEIR GUARDS (AC1, AC2, AC5.1, AC5.2)

- [ ] Write `-146` (the shape fence) and `-145` (the structural pin guard) **against the SHIPPED
      body first**. Observe **both RED**; record the exact failure text (AC5.6).
- [ ] ⛔ Confirm `-145`'s non-vacuity: it must report **4 classes found / 0 pinned** against the
      shipped tree, not pass over an empty population (`AI-E11-1`).
- [ ] Narrow `Detector` (AC1.1–AC1.6): read-only `rule_id` and `run`, `@runtime_checkable` removed,
      purity paragraph kept, locked-decisions bullet corrected, `__all__` unchanged.
- [ ] Add the four `if TYPE_CHECKING:` pins (AC2.1, AC2.2). ⛔ **No module-level instance is
      constructed at import time**; assert `TYPE_CHECKING is False` at runtime somewhere in `-145`
      or `-146`.
- [ ] `python -m mypy argus` — **expect `Success … 95 source files`**.
- [ ] AC2.3: mutate at least three pinned detectors (drop `rule_id`; retype `rule_id`; regress
      `run`'s return type) **in a scratch copy** and record each `mypy` failure.

### Task 3 — ITEM B AND ITEM C (AC3, AC4)

- [ ] Extend `base.py`'s existing `argus.ledger.coverage_ledger` import with `CoverageDepth`; retype
      `depth_supported`; **delete the `# type: ignore[arg-type]`**.
- [ ] Re-run §0.5's probe: **expect it to become an error**, and the runtime `ValidationError` to be
      unchanged (AC3.3).
- [ ] `grep -c "type: ignore" argus/detectors/base.py` — **expect 0** (AC3.2). ⛔ Do not touch the
      other 30 in `argus/`.
- [ ] Correct `FindingDraft`'s docstring and any module-docstring sentence that repeats the claim,
      **from the measured `model_fields`** (AC4). ⛔ **State the two absences; add no field.**

### Task 4 — REWRITE `-84` (AC5.3, AC5.4, AC5.5)

- [ ] Replace the `isinstance` assertion with a **structural** one covering **all four** detector
      classes. ⛔ **No `isinstance`, no `issubclass`** (§2.3).
- [ ] Keep the id `-84` and keep `-80`..`-83` byte-unchanged.
- [ ] Run the three guards; **expect all GREEN**. Re-run `-145`/`-146` against the shipped body one
      last time to confirm the recorded REDs are reproducible.

### Task 5 — PROVE NOTHING MOVED (AC6)

- [ ] Run the engine-vs-engine sweep **after**. ⛔ **The differing set must be EMPTY.** Record both
      totals, the population size, and that the population included this story's own edits.
- [ ] Run the AST comparator (AC6.1) and record the exact list of executable differences.
- [ ] Full suite; `tests/test_silent_class.py` explicitly (the 1,032-finding harness, AC6.3);
      `build_silent_class_record.py --check`.
- [ ] AC6.4: attempt the full re-derivation with `--checkout-root` and a **short**
      `--snapshot-root`. ⛔ Record the outcome either way, **by name** if a member refuses.
- [ ] Regenerate the three dogfood artifacts on a **clean** `argus/` tree (AC6.5). Compare
      `hardcoded_secret` (**expect 39**) and total LOC (**expect ~33,726**). ⛔ **Disclose any count
      that moves with its measured cause; loosen nothing.**

### Task 6 — THE LEDGER (AC7)

- [ ] ⛔ `grep` `deferred-work.md` by id first (`DF-INV-LEDGER-A`).
- [ ] Append the dated `DF-AUD-DETECT-F` closure note (AC7.1–AC7.3): the arm, the reason, the four
      falsified premises with their measurements, item B's before/after, item C.
- [ ] Answer the entry's own counter-argument in terms (AC7.2).
- [ ] List what is **not** dispositioned (AC7.4) and record the three un-filed observations (AC7.5).
- [ ] Re-verify the byte invariants: bytes, `CRLF == 0`, lone `CR == 1`, and that the edit is a pure
      insertion. ⛔ **Binary-mode edit; hunk-selective staging** (§2.6).

### Task 7 — GATES, DOGFOOD AND THE COMMIT ARC (AC8)

- [ ] Run every gate in AC8.4 and record every exit code. ⛔ `PYTHONDONTWRITEBYTECODE=1`,
      `__pycache__` cleared.
- [ ] Four commits in AC8.2's order; **`Evidence-partition: none`** on the `feat`, **written the
      first time**; pure-ASCII messages.
- [ ] ⛔ Verify the final write set equals AC8.1 **exactly** with `git status --porcelain`, and that
      none of the five §0.0 peer files rode along.

### Task 8 — HAND-OFF (AC7, AC8.6)

- [ ] Completion notes: every §0 row that moved, every RED's exact text, which guards are witnesses
      and which are fences, the AC6.4 outcome, and every deviation disclosed rather than smoothed.
- [ ] Mark the local evidence **LOCAL / Windows-only** (`AI-E13-1`) and say plainly that the
      3.10/3.11/3.12 claim belongs to CI at the pushed sha (AC8.6).
- [ ] ⛔ **This is the last story of Epic 18.** State whether `epic-18` is ready for its
      retrospective, and leave `epic-18-retrospective` at `backlog` — ⛔ **do not transition it.**

---

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

---

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-08-25 | 0.1.0 | Story contexted at HEAD `bd110c6`. Every §0 figure measured by execution: the `Detector` Protocol type-checked against all four shipped detectors (4 of 4 REJECTED by `mypy`, falsifying the entry's central mechanism), the lone `isinstance` assertion driven against five decoys on CPython 3.11/3.12/3.13 (`run = 42` passes on all three), five candidate Protocol shapes probed (exactly one accepted by all four detectors, rejecting five of five decoys), item B's silent `mypy` hole reproduced, and the whole candidate change applied to a throwaway copy of `argus/` with `mypy argus` clean over 95 files. Arm taken: **load-bearing, not deleted** (`DN-18-4-1`). Status → ready-for-dev. | bmad-create-story (Opus 5) |
