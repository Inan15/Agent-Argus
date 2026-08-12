---
baseline_commit: 93adc94d0203eaaf4d1cb1d8bc7113e9b885beed
baseline_note: >-
  `HEAD` = `93adc94` on `master`, **6 commits unpushed**, `git tag -l` **empty**. Epic 10 is 5/5
  `done`; Story 11.1 is `done` and its delta is **in the tree, uncommitted**. **No CI run has ever
  seen a line of Epic 10 or Epic 11** — the last executed `audit-ci.yml` run (`31341363300`) is
  sha-scoped to `00c8d1b`, which contains none of it. Every baseline figure in this story is
  **LOCAL, Windows / CPython 3.11.15**, under the dated risk acceptance recorded in Story 11.1
  §0.1 (AI-E10-1, 2026-08-11, XAgent007). See §0.1 — it is carried forward, not re-taken.
  ⚠️ **The tree is NOT clean and you did not dirty it.** `git status --porcelain -- argus/`
  shows exactly **three ` M` lines** — `argus/cli.py`, `argus/reports/generator.py`,
  `argus/verdict/negative_assurance.py` — which are **Story 11.1's reviewed and `done` delta**.
  `tests/test_v1_commitment_closure.py` is staged (10.5). `_bmad/**` churn is AI-E10-9's.
  `bmad-dev-loop-pack/`, `.bmad-drift-audit/` and `_bmad-output/audit-reports/*` belong to the
  orchestrator/host. **Do not commit, revert, restage or "tidy" any of it.** THIS FILE is
  untracked and IS yours: `git add` it with your delta or you repeat AI-E8-1.
  ⚠️ **ONE TEST IS ALREADY RED AND IT IS NOT YOURS.** See §0.4 (`DF-11-1-A`). Do not fix it, do
  not register around it, and do not let it hide a regression you did cause.
  **Every figure, coordinate, count and classification result below was produced by EXECUTING
  code on THIS tree on 2026-08-11.** Locate every site by its **anchor text**; treat every line
  number as a hint you must re-verify (this project has produced six stale coordinates in five
  days).
story_key: 11-2-polyglot-repository-is-classified-correctly
epic: 11
---

# Story 11.2: A polyglot repository is classified correctly

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **ArgusAgent story — Argus repo, `argus/` tree only.** ArgusAgent (formerly APAA) is a
> self-contained headless audit tool extracted from the Minions monorepo into its own repository
> (`Agent-Argus`, distribution `argus-agent`, package `argus/`). **RS-1 is binding: all work lands in
> THIS repo. The `minions_core/apaa/` copy in the Minions repo is legacy — no modification, no
> back-port.** Planning artifacts live under `_bmad-output/design-artifacts/ArgusAgent/`; the tracker
> is that folder's `sprint-status.yaml`. Prose in older documents saying `design-artifacts/APAA/`,
> `minions_core/apaa/` or `tests/apaa/` should be read as `design-artifacts/ArgusAgent/`, `argus/`
> and `tests/`.

---

## Story

As a developer auditing a repository that is not Python,
I want file classification to use real word boundaries,
so that an ordinary source file is never mistaken for a test.

**Why this is one story, and what it is not.** Epic 11's charter is *"nothing unsafe or untrue can
be published."* This story closes exactly one defect class: **name-based test classification that
matches on a letter sequence instead of a word.** It changes three table entries, adds one
boundary rule, and closes the class with a guard that fails on the next separator-less entry
anybody adds. It ships **no new capability**, adds **no test convention that is not already
recognised**, and touches **no verdict, threshold or decision table**.

**What makes it release-blocking rather than the 🟢 the ledger filed it as.** §A.3 measures it
end-to-end: on a polyglot repository, an ordinary production Java file that Argus assesses
**CRITICAL** is excluded from the FR4 critical set with the reason **`test_file`**, the critical
set comes out **EMPTY**, and the FR16 clause *"all critical subsystems deep"* is therefore
satisfied **vacuously**. `RELEASE_READY` is reachable on a repository whose one critical
production file was never deep-graded and was reported to the operator as a test. That is a false
green in the **PRD-fatal direction (inversion F1)** — and it is exactly what the epic's charter
forbids being published.

⚠️ **Read §0 before anything else.** Four items gate this story; two of them constrain your
*design*, and one of them is a red test you must not touch.

---

## Story Context

### Method statement — everything in §0–§F was MEASURED on this tree on 2026-08-11

Every count, coordinate, classification result and partition id below was produced by running
`git`, `grep`, `wc`, `mypy`, `pytest`, `python -m argus.cli audit .`, by importing and calling
`argus.detectors.vacuous_test`'s predicates directly, by driving `argus.pipeline._detect_per_file`
over a staged polyglot fixture, and by calling
`argus.dogfood.partition_plan.build_full_repo_plan('.')` in this working tree. **§B additionally
records a REVERSIBLE EXPERIMENT**: the candidate fix was applied to
`argus/detectors/vacuous_test.py`, the full suite and the dogfood plan were run against it, and
the file was restored — verified by `sha256` round-trip
(`85af39dd98e4362df2e8dddaf9567ee3dd0a0cb3218124a99752be667b6364f0`, before **and** after). **Two
figures are ATTRIBUTED, not re-measured here**: `bandit` 0 High / 0 Medium (19 Low) and coverage
95.77%, both from Story 11.1's run at this tree. **Re-derive everything; transcribe nothing.**

---

### §0. The four gates on this story — read these first

#### 0.1 — 🔴 DATED RISK ACCEPTANCE, CARRIED FORWARD (AI-E10-1)

**Recorded by: XAgent007 (operator), 2026-08-11. Carried forward to this story, not re-taken.**

> **No CI run covers any Epic 10 or Epic 11 sha.** Re-verified this session: `HEAD` = `93adc94`, 6
> commits ahead of `origin/master`, `git tag -l` **empty**. Every gate figure this story cites —
> 1352 collected tests, `mypy` clean on 72 files, `RELEASE_READY`, the dogfood partition ids — is a
> **LOCAL run on a Windows host at CPython 3.11.15**. CI is ubuntu × 3.10/3.11/3.12, and this
> project has measured evidence that the difference matters (six of the twelve commits in
> `cd60dbb..00c8d1b` were host-portability defects invisible on exactly this machine).

**What this obliges you to do.** Apply Story 10.1's evidence-citation rule (`architecture.md` §H +
§Enforcement, enforced by `tests/test_evidence_citation.py`) to **your own** gate run: label every
figure **LOCAL**, and either cite an `audit-ci.yml` run id **plus the sha it covers** for your own
HEAD, or record **`NOT ESTABLISHED`** and name the command a human runs. ⛔ **Do not push, tag or
`workflow_dispatch` to manufacture a citation** (10.1's DN-7).

⚠️ **Your fix is a `str.endswith` change that behaves identically on every platform, but the file
paths it reads do not.** `_lower_basename` splits on `/` after `replace("\\", "/")`. If your new
boundary rule reintroduces a `Path`, `os.sep` or a case-folding assumption, it will pass here and
fail on the runner nobody has run. Keep it pure string arithmetic on the already-normalised
basename.

#### 0.2 — ⛔ THE `DF-10-4-D` FENCE (AI-E10-2) — operator ruling for ALL of Epic 11

**NO Epic 11 story may create or stage a new `argus/**` source file.**

The mechanism, re-verified: `argus/dogfood/partition_plan.py::enumerate_minions_source_files`
enumerates via **`git ls-files argus`**, and `git ls-files` reports the **INDEX**, not `HEAD`. The
dogfood-audited population therefore moves the instant a new `argus/**` module is **staged** —
before any commit, at the exact moment `AI-E8-1` *requires* the `git add`. In Story 10.4 that
turned **five** committed-artifact staleness tests red mid-implementation and **halted the story**.
Its remedy is targeted at **Story 12.1 — after Epic 11**.

**Re-measured this session: `git ls-files -- argus` = 72. CONFIRMED SATISFIABLE.** Every line of
this story's production change lands inside **one file that already exists** —
`argus/detectors/vacuous_test.py`. No new module, no new package, no `argus/shared/` constant
module. `git ls-files -- argus` must still read **72** after you stage. This is **DN-4** and it is
not negotiable.

**⚠️ The second trigger is live and it is tighter than 11.1's was. §A.6 measures it: you have 133
physical lines.** `argus/detectors/vacuous_test.py` is in **dogfood unit 2**. Read §A.6 before you
write code.

#### 0.3 — 🔴 RE-MEASURED PREMISES (AI-E10-3)

Story 11.2's ACs were drafted **2026-08-10b**; its underlying ledger entry (`DF-8-2-B`) was written
**2026-08-04**. Stories 10.2 and 10.4 rebuilt the grammar loader in between. **Three premises were
re-measured. One held, one is materially stale, and one is wrong in the direction that makes the
story bigger, not smaller.**

| Premise as the epic / ledger writes it | Measured on this tree, 2026-08-11 | Verdict |
|---|---|---|
| *"`\"test.java\"` and `\"spec.rb\"` at `argus/detectors/vacuous_test.py:198` carry no word separator"* | **HELD, and the coordinate is exact.** Both literals are on **line 198**, inside `_UNAMBIGUOUS_TEST_SUFFIXES` (`:195-199`). `is_test_file("svc/latest.java")` → `True`, `is_test_file("svc/myspec.rb")` → `True`, both with `is_test_classification_content_dependent(...)` → `False`. | ✅ **holds** |
| *"…not a false green relative to what Argus can actually grade, because the GRADING stage misclassifies them identically"* (`DF-8-2-B`, 2026-08-04) | **THE PREMISE EXPIRED.** It was written when Java had no grammar. Measured now: `build_ast_index` over `svc/latest.java` returns `ast_eligible=True`, `parse_failed=False`, **2 definitions**. The file is deep-*gradable*. The two stages still agree — **AC7's invariant holds** — but what they agree on now costs real assurance coverage and produces a **vacuously satisfied FR16 critical clause** (§A.3). | ❌ **stale → this is why the story is release-blocking** |
| *"**Two** entries … are written without a word separator"* (every planning document, four times) | **THERE ARE THREE.** `_AMBIGUOUS_PYTHON_TEST_SUFFIXES` carries a bare **`"test.py"`** with the identical defect: `contest.py`, `attest.py`, `greatest.py`, `latest.py` and `mytest.py` all match it. **The sixth wrong hand-count in this project.** §A.4. | ❌ **stale → AC1.4, and it is why AC3 is a closure and not a list** |

#### 0.4 — ⛔ ONE TEST IS ALREADY RED. IT IS `DF-11-1-A` AND IT IS NOT YOURS

`tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed`
**FAILS on this tree, before you touch anything.** Re-run and confirmed this session:

```
AssertionError: status-asserting document(s) exist but are not registered:
['epic-10-retro-2026-08-11.md']
```

**Attribution is PROVEN, not assumed.** Story 11.1's review adjudicated it by a positive
git-stash isolation experiment (all nine of 11.1's touched files reverted, identical failure
reproduced from the untracked `epic-10-retro-2026-08-11.md` alone, stash popped content-identical).
It is Story 10.1's own citation guard working as designed on an Epic-10 artifact that was never
registered.

**Ruled for this story: `DF-11-1-A` STAYS DEFERRED. Do not close it here.** The reasoning, recorded
so it is not re-litigated (DN-7):

1. It is an **artifact-registration** item about an Epic-10 retrospective document. It has no
   relationship to file classification and shares no line of code with this story's write set.
2. Closing it means registering the retro in `_STATUS_DOCUMENTS`, which then requires **the retro
   itself** to satisfy the citation rule (a run id + the sha it covers, or a `NOT ESTABLISHED`
   marker). Editing a signed Epic-10 retrospective from inside an Epic-11 story to make a test go
   green is the *regenerate-the-artifact-to-pass-the-staleness-check* antipattern wearing a
   different hat. Story 10.4 refused the same move and was right to.
3. Precedent: **Story 8.1's AC18 carve-out**, cited by 11.1's reviewer for exactly this shape.

**What this obliges you to do (this is AC7.1, and it fixes a Low finding the 11.1 review raised
against 11.1's own wording):** your "full suite green" claim must **carve out this failure BY NAME
and by node id**, and must assert that it is the **only** failure. ⛔ A second red is yours, whatever
its file. Do not add `epic-10-retro-2026-08-11.md` to `_STATUS_DOCUMENTS`, do not `git add` it, and
do not delete it.

*(Surfaced to the operator as open question 2 — it is a two-minute human step that would remove a
standing red from every remaining Epic 11 story, and it is not this story's to take.)*

---

### §A. What was measured, and what it changes

#### A.1 — The defect, reproduced exactly

`argus/detectors/vacuous_test.py` classifies in **three tiers** (`_is_unambiguous_test_path`,
`is_test_classification_content_dependent`, `is_test_file` — anchors, not line numbers):

- **Tier 1 — location.** Any path with `tests`/`test`/`__tests__`/`spec`/`specs` in a parent
  segment, or rooted at `tests`/`test`/`spec`.
- **Tier 2 — reserved filename.** Lowercased basename starting `test_` or `test.`, **or ending
  with any member of `_UNAMBIGUOUS_TEST_SUFFIXES`**. ⚠️ **Tier 2 has no content check by design** —
  the module's own comment says *"the convention is reserved for tests and no production module
  adopts it."* A tier-2 answer is final.
- **Tier 3 — ambiguous Python suffix.** `_AMBIGUOUS_PYTHON_TEST_SUFFIXES`, resolved by CONTENT via
  `_exhibits_test_definitions(ast_entry)` when an entry is supplied, and defaulting to `True` when
  it is not.

Measured, by calling the real predicates (`is_test` / `content_dependent`):

| Path | `is_test_file` | content-dependent | Verdict |
|---|---|---|---|
| `svc/latest.java` | **True** | False | ❌ **false positive, tier 2, unfixable by content** |
| `svc/myspec.rb` | **True** | False | ❌ **false positive, tier 2** |
| `svc/respec.rb` | **True** | False | ❌ false positive, tier 2 |
| `svc/spec.rb` | **True** | False | ❌ false positive (bare literal), tier 2 |
| `svc/contest.py` · `attest.py` · `greatest.py` · `latest.py` · `mytest.py` | **True** *(no entry)* | **True** | ❌ **false positive, tier 3 — masked when content is readable** |
| `svc/UserServiceTest.java` | True | False | ✅ true positive — **must survive** |
| `svc/user_spec.rb` | True | False | ✅ true positive — **must survive** |
| `pkg/conftest.py` | True | **True** | ✅ true positive — **must survive AND stay tier 3** |
| `svc/x_test.go` · `web/button.test.tsx` · `crate/parser_test.rs` | True | False | ✅ unaffected (separators present) |

**Zero instances in THIS repository, re-verified.** `git ls-files` finds no `.java`, no `.rb`, no
`conftest.py` and no bare-suffix `*test.py` under any tracked path. That is what makes AC7.5
assertable: your change must not move `argus audit .` at all.

#### A.2 — 🚩 THE MEASUREMENT THAT DECIDES THE IMPLEMENTATION: Java's word separator is a CASE boundary

`DF-8-2-B`'s close condition offers *"`\"_test.java\"`/`\"Test.java\"`"*. **The first of those is
wrong and would silently delete a whole language's true positives.** Java has no `_` convention.
**Maven Surefire's default includes are `**/Test*.java`, `**/*Test.java`, `**/*Tests.java`,
`**/*TestCase.java`** — verified against the plugin's published *Inclusions and Exclusions* page,
2026-08-11 — all four **CamelCase**. The separator IS the capital letter.

And `_is_unambiguous_test_path` **lowercases the basename before matching**, which destroys exactly
that boundary. Measured:

| Candidate rule | `latest.java` | `UserServiceTest.java` |
|---|---|---|
| today — lowercase match on `"test.java"` | **True** ❌ | True ✅ |
| `"_test.java"`, lowercase match | False ✅ | **False** ❌ *(every Java test in the world)* |
| **`"Test.java"`, CASE-SENSITIVE, on the un-lowercased basename** | **False** ✅ | **True** ✅ |

**Locked as DN-1: the Java boundary is matched case-sensitively against the original-case basename.**
A file literally named `test.java` (all lowercase) is unaffected either way — **tier 2's
`startswith("test.")` prefix rule already claims it**, verified: `is_test_file("svc/test.java")` is
`True` today and stays `True`.

#### A.3 — 🚩🚩 THE MEASUREMENT THAT MAKES THIS RELEASE-BLOCKING: a vacuous FR16 critical clause

Driving the real pipeline (`build_ast_index` → `_detect_per_file` → `CoverageLedger.build` →
`identify_critical_subsystems`) over a staged four-file polyglot fixture, **at HEAD, defect live**:

```
svc/UserServiceTest.java   is_test=True   depth=audited_shallow  crit=normal    inelig=test_file
svc/contest.py             is_test=False  depth=audited_deep     crit=normal    inelig=None
svc/latest.java            is_test=True   depth=audited_shallow  crit=CRITICAL  inelig=test_file
svc/myspec.rb              is_test=True   depth=audited_shallow  crit=normal    inelig=test_file
critical set: ()
excluded    : {'svc/latest.java': 'test_file'}
```

**Read the third row.** `svc/latest.java` is ordinary production code carrying a credential-shaped
token. Argus assesses it **CRITICAL**. It is then removed from the FR4 critical set under the
reason **`test_file`** — a statement that is simply false — and **the critical set comes out
empty**. FR16's *"all critical subsystems deep"* clause is satisfied because there is nothing left
to satisfy it with.

Three consequences, each separately assertable, and each stated at the size it actually is:

1. **A false green in the fatal direction.** `RELEASE_READY` becomes reachable on a repository
   whose only critical production file was never examined. The PRD names this inversion (F1) as
   fatal for an assurance tool. *(This is the consequence `DF-8-2-B` explicitly reasoned away in
   2026-08-04 — on a premise that has since expired: Java grounds now.)*
2. **An untrue statement to the operator.** The file is counted in `held_out=` on the stdout wire
   line, and `argus/reports/generator.py` renders *"N test file(s), graded shallow by
   construction"* over a population that includes it. ⚠️ **Do not overclaim the third channel:**
   `heuristic_excluded_ineligible` — the map that carries the literal token `test_file` — was
   measured to have **no operator-facing consumer at all** (its only reader outside `ledger/` is
   `argus/dogfood/proof_run.py`, and it takes the `len()`). That is `DF-8-3-A`, it is not yours,
   and the story must not claim a disclosure surface that does not exist.
3. **AC7's invariant is NOT violated.** Both stages call the *same* predicate and reach the *same*
   wrong answer. That is why AC4 re-**proves** the invariant rather than repairing it — and why the
   re-proof is load-bearing, because your change is the first thing to alter that predicate since
   a second classification stage was added.

#### A.4 — 🚩 The enumeration was wrong for the fourth time: there are THREE separator-less entries

Every document names two. Measured, by reading both tables out of the module:

| Table | Entry | Separator? |
|---|---|---|
| `_UNAMBIGUOUS_TEST_SUFFIXES` | `_test.go`, `.test.js`, `.spec.js`, `.test.ts`, `.spec.ts`, `.test.jsx`, `.spec.jsx`, `.test.tsx`, `.spec.tsx`, `_test.rs`, `_spec.rb`, `_test.cpp`, `_test.cc` | ✅ 13 of 15 |
| `_UNAMBIGUOUS_TEST_SUFFIXES` | **`test.java`** | ❌ |
| `_UNAMBIGUOUS_TEST_SUFFIXES` | **`spec.rb`** | ❌ *(and redundant — `_spec.rb` sits beside it)* |
| `_AMBIGUOUS_PYTHON_TEST_SUFFIXES` | `_test.py` | ✅ |
| `_AMBIGUOUS_PYTHON_TEST_SUFFIXES` | **`test.py`** | ❌ **never named by any document** |

**Why the Python entry is fixed here even though it is NOT release-blocking, stated honestly.** Its
harm is largely masked: tier 3 resolves by content, and `_critical_ineligibility` already carves
out an unreadable tier-3 label (`if unreadable and is_test_classification_content_dependent(...):
return None`), so it costs neither eligibility nor, in the common case, grading. **It is fixed
because AC3's closure has to have a uniform contract.** Leaving it would force the guard to carry a
named exemption for a known-defective entry, which is a guard that documents the bug instead of
closing it. That reasoning, not a severity claim, is the justification — DN-3.

**And it is why AC3 is a closure, not a list.** AI-E10-5: *five hand-counted enumerations were
re-measured and all five were wrong.* This is the sixth.

#### A.5 — 🚩 `conftest.py` is what the bare `"test.py"` is really standing in for — do not delete it

The reversible experiment in §B **failed once**, and the failure is the most useful thing it
produced:

```
tests/test_vacuous_detector.py::test_test_classification_content_dependence_names_the_tier_that_answered
AssertionError: assert False
  where False = is_test_classification_content_dependent('pkg/conftest.py')
```

`conftest.py` ends with `test.py`. `TC-ArgusAgent-DETECT-001-95` **pins it as tier 3**, deliberately
— a `conftest.py` holding only fixtures should resolve to production by content, and one holding
test helpers should not. **The correct fix is therefore not "drop the bare entry" but "replace the
letter-sequence match with the whole-BASENAME rule it was standing in for":** `conftest.py` as an
exact basename, still routed through tier 3. Locked as **DN-2**.

⛔ **`TC-ArgusAgent-DETECT-001-95` must pass UNMODIFIED.** If you find yourself editing an existing
test to accommodate your change, stop — with the shape in §B, **zero existing tests need to
change**, and that is the proof that the fix is a repair and not a redefinition.

#### A.6 — 🚩🚩 THE BUDGET, RE-MEASURED THIS SESSION: you have 133 physical lines

`argus/detectors/vacuous_test.py` was measured into **dogfood unit 2**, the unit at the ceiling.
`build_full_repo_plan('.')`, run directly:

| unit | `partition_id` (prefix) | LOC | files |
|---|---|---|---|
| 1 | `477ef77d7b65…` | 1 330 | 21 |
| 2 | **`82a3d605e61e…`** | **14 867** | 39 ← **`argus/detectors/vacuous_test.py` is here** |
| 3 | `ed6d08f25ce3…` | 3 804 | 12 |
| — | total | 20 001 | 72 |

`DEFAULT_SOFT_LOC_LIMIT = 15_000` (`argus/index/partitioner.py`). **14 867 of 15 000 leaves a hard
budget of 133 ADDED PHYSICAL LINES inside `argus/**` files belonging to unit 2** before the
bin-packer re-flows and the `partition_id` sha256s move — which turns Story 10.4's five
committed-artifact staleness tests red with no file having been added.

*(Provenance of the figure: 11.1 consumed 74 of the 207 that were available to it. 14 867 is
re-measured here, not carried forward.)*

**Measured headroom for the actual change: the candidate fix in §B costs `+7` physical lines
(14 867 → 14 874, all three `partition_id`s byte-unchanged).** With docstrings written to this
project's standard, budget 25–45. **You have room, and you must still verify rather than assume
(AC7.4).** ⛔ **If it tips, HALT. Never regenerate a dogfood artifact to make a staleness test pass
— that remedy belongs to Story 12.1 and Story 10.4 already refused it once.**

#### A.7 — 8 of the 10 grounded languages have a name convention. Two have none

`argus/shared/source_languages.py::LANGUAGE_BY_SUFFIX` grounds **10** languages: `c`, `cpp`, `go`,
`java`, `javascript`, `php`, `python`, `ruby`, `rust`, `typescript`. Cross-referencing the suffix
tables: **`c` and `php` have no test-name convention at all** (PHPUnit's is `*Test.php`; C's is
`*_test.c`), and Ruby's minitest form `_test.rb` and Java's `*Tests.java` / `*TestCase.java` are
absent too.

⚠️ **A fourth Java gap, measured:** Surefire's `**/Test*.java` **prefix** form is not recognised
either — `TestUserService.java` lowercases to `testuserservice.java`, which does **not** match tier
2's `startswith("test.")`. Only the exact name `test.java` does.

⛔ **Those are ALL FALSE NEGATIVES — a different defect class, and they are OUT OF SCOPE.** Adding a
convention adds true positives and moves classification on real repositories; this story only
*removes* false ones. They are **filed** (AC6.2), and AC3.5 makes the gap **registered rather than
invisible**: a future language added to `LANGUAGE_BY_SUFFIX` without a convention or a
reason-carrying exemption turns the guard red. A closure that forces a decision is not the same as
a fix, and this story does the first only.

#### A.8 — Baseline, re-measured this session (LOCAL — see §0.1)

| Figure | Measured 2026-08-11 | How |
|---|---|---|
| Tests collected | **1352** — 1351 passed, **1 failed (`DF-11-1-A`, §0.4)**, 0 errors, **0 skipped** | `pytest tests/ --junit-xml`, `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` |
| `mypy` | **clean, 72 source files** | `python -m mypy argus` |
| `git ls-files -- argus` | **72** | — |
| `git status --porcelain -- argus/` | **exactly 3 ` M`** (11.1's `done` delta) | — |
| dogfood unit 2 | **14 867 / 15 000**; ids `477ef77d7b65…` / `82a3d605e61e…` / `ed6d08f25ce3…` | `build_full_repo_plan('.')` |
| `argus audit .` | `verdict=RELEASE_READY deep_ratio=61/165 blocking_findings=0 assessed_deep_ratio=61/77 scope=application held_out=88`, exit 0 | `python -m argus.cli audit .` |
| `vacuous_test.py` size | **533 lines** (NFR-M1 cap 1200 — ample) | `wc -l` |
| Next free test ids | `DETECT-001-96`+ · `PIPELINE-002-10`+ · `DOCS-001-53`+ | grep of both id spellings |
| Coverage / `bandit` | 95.77% · 0 High / 0 Medium (19 Low) | **ATTRIBUTED to 11.1 — re-measure yours** |

⚠️ **`deep_ratio=61/165` corrects the `61/164` that Story 10.5's tracker entry records** — 11.1 added
a test file and moved the denominator. Cite 61/165, and see AC7.5 for why your own new test file
will move it again by exactly +1.

---

### §B. The shape, PROVEN VIABLE by a reversible experiment — not a mandate

The candidate below was **applied to the real file, measured, and reverted** (`sha256` identical
before and after: `85af39dd98e4362df2e8dddaf9567ee3dd0a0cb3218124a99752be667b6364f0`). It is given
so you know the story is deliverable and what "no existing test changes" looks like. **The ACs pin
observable behaviour, not this code.** A better shape that satisfies §C and the ACs is welcome; a
shape that requires editing an existing test is not.

```python
_UNAMBIGUOUS_TEST_SUFFIXES = (
    "_test.go", ".test.js", ".spec.js",
    ".test.ts", ".spec.ts", ".test.jsx", ".spec.jsx", ".test.tsx", ".spec.tsx",
    "_test.rs", "_spec.rb", "_test.cpp", "_test.cc",
)                                        # "test.java" and "spec.rb" removed

_CASE_SENSITIVE_TEST_SUFFIXES = ("Test.java",)      # DN-1: the boundary IS the capital

_AMBIGUOUS_PYTHON_TEST_SUFFIXES = ("_test.py",)     # bare "test.py" removed
_AMBIGUOUS_PYTHON_TEST_BASENAMES = ("conftest.py",) # DN-2: what it was standing in for
```

with `_is_unambiguous_test_path` gaining, **before** the lowercasing:

```python
raw = file_path.replace("\\", "/").split("/")[-1]
if any(raw.endswith(s) for s in _CASE_SENSITIVE_TEST_SUFFIXES):
    return True
```

and `is_test_classification_content_dependent` checking the basename table beside the suffix table.

**Measured under that shape, on this tree:**

- every false positive in §A.1 → `False`; every true positive → `True`, **including
  `pkg/conftest.py` still content-dependent**;
- **full suite: 1352 collected, exactly ONE failure — `DF-11-1-A`. Zero new failures. Zero existing
  tests modified.**
- `mypy` clean, 72 source files;
- dogfood unit 2: 14 867 → **14 874 (+7)**, **all three `partition_id`s byte-unchanged.**

⛔ **This is a measurement, not permission to skip RED-first.** §E.1 is mandatory: your guards must
be demonstrated failing on the *unfixed* tree, with the *final* test code.

#### B.1 — Regression watchlist: the six existing assertions your change passes closest to

These already exist and already pass. **Run them individually first, and again at the end.** They
are how you find out you widened something.

| Assertion | File | Why it is close to your change |
|---|---|---|
| `is_test_file("lib/user_spec.rb")` is a test | `tests/test_pipeline_coverage_scope.py:102` (`PIPELINE-002-04`) | The **only** Ruby true positive in the suite. It survives on `_spec.rb`. Delete that entry by mistake and this is your first red. |
| `is_test_classification_content_dependent("pkg/conftest.py")` | `tests/test_vacuous_detector.py` (`DETECT-001-95`) | **DN-2.** The reason the bare `"test.py"` cannot simply be dropped (§A.5). |
| `is_test_file("src/vacuous_test.py")` True **without** an entry, **False** with one | `tests/test_report_surface_consistency.py:386-388` | Pins tier 3's two answers. Both must be preserved exactly. |
| `app/auth_test.py` is `audited_deep` **and** `ineligibility is None` | `tests/test_critical_eligibility_pipeline.py` (`PIPELINE-002-02`) | **This is the original AC7 test.** Your AC4 re-proof extends it; it must still pass untouched. |
| `svc/token_test.py` unreadable stays **eligible**; `tests/test_broken.py` stays `TEST_FILE` | same file (`PIPELINE-002-09`) | The tier-3 unreadable carve-out. ⛔ Do not "improve" the default direction (§C). |
| `is_test_file("web/button.test.tsx")`, `("crate/parser_test.rs")`, `("pkg/handler_test.go")` | `tests/test_test_file_classification.py:111-113` | The separator-carrying entries you must not disturb while editing the same tuple. |

---

### §C. Design constraints a reviewer will check

- **AR7 / §3.3 — no second mechanism where one exists.** The tier structure is declared **once**;
  `is_test_file` and `is_test_classification_content_dependent` both *read* it. ⛔ Do not add a
  parallel regex classifier, do not re-declare a suffix table in the guard, and do not fork a
  boundary rule into `pipeline.py` or `reports/`. If you add a fourth table, it must be **read by
  the same two predicates** and nothing else.
- **AR8 / pure-impure.** These predicates are **pure** — string arithmetic and an optional
  `AstIndexEntry`. No I/O, no `Path`, no clock, no `float`, no new import, no new dependency.
- **The tier ORDER is the contract, not an implementation detail.** Tier 1 (location) → tier 2
  (reserved name, final) → tier 3 (content). Your case-sensitive rule belongs **inside tier 2**,
  because a `*Test.java` is a test by convention with no content check available. ⛔ Do not route
  Java or Ruby through the Python content-resolution path — it is AST-backed and
  language-specific, and the epic's binding note says so explicitly.
- **The tier-3 unreadable default stays `True`.** `_exhibits_test_definitions` returns `True` for
  anything it cannot read, and its docstring explains why the two misclassifications are not
  symmetric. ⛔ Do not "improve" that direction; `_critical_ineligibility`'s carve-out and
  `TC-ArgusAgent-PIPELINE-002-09` both depend on it.
- **`is_test_classification_content_dependent` is a two-consumer contract.** Grading wants
  "assume test when unreadable"; FR4/DR-5 eligibility wants the opposite. Anything you move
  between tier 2 and tier 3 changes **both** consumers. That is why AC4 exists.
- **NFR-M1**: `argus/detectors/vacuous_test.py` is 533/1200. Not a constraint here; the **dogfood
  LOC budget (§A.6) is.**

---

### §D. ⛔ FENCES — what this story must NOT touch

| Fenced | Owner | Why, and where the line sits |
|---|---|---|
| **Creating or staging ANY new `argus/**` file** | **12.1** | §0.2 / `DF-10-4-D`, operator ruling for all of Epic 11. `git ls-files -- argus` stays **72**. DN-4. |
| **> 133 added physical lines in dogfood unit 2** | **12.1** | §A.6. Verify empirically (AC7.4). **HALT if it tips.** |
| **Regenerating `minions-dogfood-*.md`** | **12.1** | Verdict-adjacent, fenced by 10.4's DN-9. Their bytes must not move. |
| **ADDING a test-name convention** (`_test.rb`, `*Tests.java`, `*TestCase.java`, `*Test.php`, `_test.c`) | **filed, AC6.2** | §A.7. False negatives are a different class; adding one moves classification on real repos. **Remove false positives only.** |
| **The FR16 decision table, any threshold, any exit code, the verdict vocabulary** | — | ⛔ The epic AC for 11.1 is explicit and binds the epic: *"no verdict is reworded, upgraded or hedged."* FR37 governs explanation; FR16 governs classification. |
| **`argus/pipeline.py`** | **12.1** | 1331/1200 measured, byte-fenced. AC4.2 **reads** it with `ast`; it does not edit it. |
| **`argus/ledger/**`, `argus/reports/**`, `argus/cli.py`, `argus/verdict/**`** | — | Byte-unchanged. The three ` M` files are **11.1's**, already reviewed. Do not touch them. |
| **`DF-8-3-A`** (the vacuous-critical-set disclosure has no operator surface) | **the 12.1 extraction story** | §A.3 consequence 2. You may not add a report surface for `heuristic_excluded_ineligible`. |
| **`DF-8-3-C`** (the duplicated ast-index→application partition plumbing) | **the 12.1 extraction story** | Its close condition is *"the story that performs the `DF-8-2-A` `pipeline.py` extraction"* — **not** *"any story that edits `vacuous_test.py`"*. It does **not** fire here. Do not add `partition_application_files`. |
| **`DF-10-2-A`** (C/C++/Ruby/Rust ground but extract zero definitions) | **11.5 / AI-E10-4** | AC5.2 **observes** its effect on `myspec.rb`. It does not fix it. |
| **`DF-11-1-A`** / `tests/test_evidence_citation.py` / `epic-10-retro-2026-08-11.md` | **operator** | §0.4. Carve it out by name; do not close it. |
| **`E-PRD/prd.md`, `epics.md`, every Epic 1–9 artifact and retrospective, `_bmad/**`, `audit-ci.yml`, `release.yml`, `action.yml`, `README.md`, `pyproject.toml`** | — | ⛔ Byte-unchanged. *(One exception, additive only: `architecture.md` §Enforcement gains this story's guard registration — AC6.3.)* |
| **Publishing, tagging, `workflow_dispatch`, `git push`** | **12.9 / operator** | **NO STORY IN EPIC 11 PUBLISHES ANYTHING.** 10.1's DN-7: triggering a run to manufacture a citation is manufacturing evidence. |
| **The ≥80% precision gate** | **Epic 13** | NOT CLEARED. Nothing here clears it. |
| **H0 (who files the Minions handoff) · `DF-7-2-A` (the human TP/FP adjudication)** | UNOWNED / XAgent007, **OPEN** | `tests/test_v1_commitment_closure.py::-38` pins both. Do not let anything you write read as closing either. |
| **The uncommitted work already in the tree** | operator / AI-E10-9 | Not yours. Do not commit, revert or restage it. |

---

### §E. Traps previous stories already paid for — the six that apply

| # | Trap | What it costs you here |
|---|---|---|
| **E.1** | **AI-E3-1 — a keystone test that was green over its own keystone bug** (Story 3.4). | **RED-first is MANDATORY, with the FINAL test code.** Restore the three defective entries, run AC3's closure, and record it naming **exactly three** offenders. Then restore the fix and verify the file `sha256` round-trips. 10.5 found a real bug in its own guard doing precisely this. |
| **E.2** | **Six hand-counted enumerations, six wrong** (10.2 ×3, 10.3 4→6, 10.4 2→4, 10.5 1→3, 11.1 2→3, **this story 2→3**). | AC3's **closure over the tables** is load-bearing; §A.4's table is its *input*, never its contract. |
| **E.3** | **A guard that passes vacuously** (10.3's `-39`, 10.4's `-118`, 10.5's `-39`, 11.1's non-vacuity floors). | Assert non-zero floors: entries per table > 0, near-miss pairs generated > 0, languages enumerated > 0. **A rename or move of the constants, or an `ast.parse` failure, must turn this RED — not silently green.** |
| **E.4** | **Positive control, both directions.** | Every near-miss must be **False** *and* its true-positive twin **True**. A guard that made everything `False` would pass a one-directional check. |
| **E.5** | **AI-E8-1 — `git diff` cannot see an untracked path.** | `git add` this story file **and** the new test before you claim a write-set fence. Verify with `git status --porcelain` **and** `git diff --stat`. Then re-check `git ls-files -- argus` is still **72** (§0.2 — staging is what moves it). |
| **E.6** | **AI-E9-7 — never publish a prose copy of an enumerable fact.** | The near-miss corpus is declared in **one** place and imported by every consumer, including the `tests/test_vacuous_detector.py` pin. The suffix tables are read **out of the module**, never retyped into the guard. |

---

## Acceptance Criteria

### AC1 — Every name-based test convention carries a real word boundary

1. **`_UNAMBIGUOUS_TEST_SUFFIXES` no longer contains `"test.java"` or `"spec.rb"`.**
2. **Java's boundary is matched CASE-SENSITIVELY against the original-case basename** (DN-1, §A.2),
   inside **tier 2**. Measured requirement: `svc/latest.java` → `False`,
   `svc/UserServiceTest.java` → `True`, `svc/Test.java` → `True`, `svc/test.java` → `True` (the
   last via the existing `startswith("test.")` prefix rule, which is **unchanged**).
3. **Ruby's convention is carried by the existing `_spec.rb`.** The bare literal is removed. **State
   the loss rather than hide it:** a file named literally `spec.rb` outside a `spec/` directory is
   no longer a test by name. That is correct — RSpec's convention is `*_spec.rb` — and it is pinned
   as a decided answer, not left to be discovered.
4. **`_AMBIGUOUS_PYTHON_TEST_SUFFIXES` no longer contains the bare `"test.py"`; `conftest.py` is
   preserved as an explicit whole-BASENAME rule that stays in TIER 3** (DN-2, §A.5). ⛔
   `TC-ArgusAgent-DETECT-001-95` must pass **unmodified**.
5. **Tier 1 (location) and tier 2's `test_` / `test.` prefix rules are unchanged.** The tier ORDER
   is unchanged. `_exhibits_test_definitions`' unreadable-defaults-to-`True` direction is unchanged.
6. **No new `argus/**` file** (DN-4), no new import, no new dependency; the predicates stay **pure**
   (AR8) and the tier structure stays declared **once** (AR7/§3.3).
7. ⛔ **No existing test is modified, weakened, renamed or deleted.** §B measured this to be
   achievable. If an existing test goes red, your fix is wrong — do not adjust the test.

### AC2 — A pinned near-miss corpus asserts BOTH directions

1. A **single declared corpus** of `(path, expected_is_test, expected_content_dependent)` triples,
   covering at minimum: `latest.java`, `myspec.rb`, `respec.rb`, `spec.rb`, `contest.py`,
   `attest.py`, `greatest.py`, `latest.py`, `mytest.py` (all → **not a test**) and their true
   positives `UserServiceTest.java`, `Test.java`, `test.java`, `user_spec.rb`, `conftest.py`,
   `app/auth_test.py`, `svc/x_test.go`, `web/button.test.tsx`, `crate/parser_test.rs`,
   `tests/test_x.py` (all → **test**).
2. **Both source documents named different corpora and the union is used, recorded as such** —
   `DF-8-2-B` names `attest.py`/`greatest.py`; the epic names `contest.py`/`respec.rb`. Neither
   list is the contract (AC3 is); both are covered so neither reviewer finds a gap.
3. **`content_dependent` is asserted alongside `is_test` for every entry**, because *which tier
   answered* is a separate contract with a second consumer (§C).
4. **The corpus is declared ONCE** and imported by every consumer (E.6), including:
5. **`tests/test_vacuous_detector.py` gains a case beside `TC-ArgusAgent-DETECT-001-85`/`-95`
   pinning the two headline near-misses** — `DF-8-2-B`'s close condition names that file
   explicitly, and a reviewer will look there first. It **imports** the corpus; it does not restate
   it.

### AC3 — 🔑 THE CLOSURE: a separator-less entry FAILS CI

**This is the load-bearing AC** (AI-E10-5: *where an AC names a set of sites, the load-bearing AC is
a closure guard that fails on an unenumerated member; the list is a convenience, never the
contract*). A list closes today's three instances; a closure closes the class.

1. The guard **imports the tables out of `argus/detectors/vacuous_test.py`** — never transcribes
   them — and asserts **every** entry is one of: a suffix beginning with a registered word
   separator (`_` or `.`); a **registered case-sensitive** convention whose first character is an
   uppercase letter; or a **registered whole basename**. Any other entry **fails, naming itself**.
2. **Adversarial near-misses are SYNTHESIZED from the tables, not hand-listed.** For every suffix
   entry, the guard derives the separator-less form, prefixes an alphanumeric character, and
   asserts the result is **not** classified as a test; and asserts the separator-carrying form
   **is** (positive control, both directions — E.4).
3. **RED-first, with the final test code (E.1).** Demonstrated failing against the unfixed tables
   and naming **exactly three** offenders — `test.java`, `spec.rb`, `test.py`. Record the failure
   text in the Dev Agent Record.
4. **Non-vacuity is mandatory (E.3).** Floors: entries read per table > 0, near-miss pairs
   generated > 0. A rename or move of the constants, or a failure to resolve the module, must turn
   this **RED**, not green-by-finding-nothing.
5. **Language closure (§A.7).** Every language in
   `argus/shared/source_languages.py::LANGUAGE_BY_SUFFIX` either has ≥1 registered convention, or
   is a **registered exemption carrying its reason** — today exactly `c` and `php`. A new grounded
   language, or a new convention, turns this red until it is decided. ⛔ **This forces a decision;
   it does not authorise adding a convention** (§D).
6. The failure messages say **what to do**, in the 10.3/10.5 house style, and state that **a red
   here is the guard working**.

### AC4 — 🔑 The AC7 two-stages-cannot-disagree invariant is RE-PROVEN, across BOTH constants

The epic's binding note: *"the AC7 re-proof is now the load-bearing AC, not a formality — the
invariant must be re-proven across both constants and their interaction, since a second
classification stage now exists that did not when AC7 was written."* It is **re-proven, not
assumed to survive**.

1. **Behavioural, end-to-end.** Over a staged polyglot fixture exercising **both** constants and
   their interaction — tier-2 Java/Ruby (`latest.java`, `UserServiceTest.java`, `myspec.rb`,
   `user_spec.rb`) **and** tier-3 Python (`contest.py`, `app/auth_test.py`, `pkg/conftest.py`,
   plus an unreadable `svc/token_test.py`) — drive the real pipeline and assert **for every file**
   that the grading depth and the eligibility fact **agree**:
   - no file graded `audited_deep` carries `CriticalIneligibility.TEST_FILE`;
   - no file classified a test by **name** (tier 1 or 2) is graded `audited_deep`;
   - the tier-3 unreadable carve-out still holds — `svc/token_test.py` stays **eligible** and is
     never disclosed under the false reason `test_file` (`TC-ArgusAgent-PIPELINE-002-09`'s rule).
2. **Structural.** An `ast` walk of **`argus/pipeline.py`** (read-only — the file is byte-fenced)
   proving `is_test_file` is evaluated **once per file** and the **same value** is passed into
   `_critical_ineligibility` on **both** paths: the fresh path (`_detect_per_file`) and the resume
   path (`_critical_candidate`). **Measured: there are exactly two such construction sites today.**
   A **third** derivation of `is_test`, or a call to `_critical_ineligibility` with a
   separately-computed value, turns this red — that is the mechanism by which the two stages
   *could* come to disagree, and the only one.
3. **Non-vacuity + positive control.** Sites found > 0; a rename of either function or an
   `ast.parse` failure must turn it **RED**. A synthetic candidate whose two stages *do* disagree
   must make the behavioural assertion fire.

### AC5 — The measured consequence is pinned as a test, and the verdict machinery is untouched

1. **The §A.3 vacuous-critical-set result is pinned, in its corrected form**, not written as prose:
   on the polyglot fixture, `svc/latest.java` is assessed **CRITICAL**, and after this story it is
   **eligible** (`ineligibility is None`) and the critical set is **non-empty**. ⛔ Do **not** assert
   the pre-fix state as a live expectation; assert the post-fix invariant and record the measured
   before-state in the Dev Agent Record.
2. **`myspec.rb`'s exclusion reason changes from `test_file` to the TRUE reason.** Ruby grounds but
   extracts **zero definitions** (`DF-10-2-A`), so it becomes `ZERO_DEFINITION_MODULE` — still
   ineligible, now for a reason that is true. ⛔ Pin it; do **not** fix `DF-10-2-A` (§D).
3. **⛔ FR16's decision table, the verdict vocabulary, every threshold and every exit code are
   byte-unchanged**, asserted rather than claimed. FR37 governs explanation, FR16 governs
   classification, and this story changes neither.
4. **State the direction of the change rather than hedging it.** On a repository that *has* the
   affected files, the verdict may move — and it can only move **conservatively** (files return to
   the assessed population; an ungroundable one lowers the deep ratio). ⛔ It can never turn a
   blocking verdict into `RELEASE_READY`. Say this plainly in the CHANGELOG (AC6.4); do not
   describe the change as behaviour-preserving, because on the target audience's repositories it is
   not.

### AC6 — The ledger, the registration and the release note

1. **`DF-8-2-B` is CLOSED** in `deferred-work.md`, **append-only** (§3.4 — the original entry is not
   rewritten; verify `after.startswith(before)` programmatically, +n/-0). The closure records: the
   corrected count (**three**, not two), the **expired premise** (*"not a false green"* was true
   only while Java had no grammar — §0.3), and the measured vacuous-critical-set result.
2. **New filings, each with a NAMED OWNER and a target story** (AI-E9-8 convention): (a) the
   false-negative convention gaps — minitest `_test.rb`, Surefire's `*Tests.java` /
   `*TestCase.java` / `Test*.java`, PHPUnit `*Test.php`, `_test.c` — and (b) the registered
   `c` / `php` no-convention exemptions from AC3.5. ⛔ Filed, **not fixed** (§D).
3. **`architecture.md` §Enforcement gains this story's guard registration** — additive only,
   following the 10.4 / 10.5 / 11.1 form: the **rule** in one sentence (*a name-based classification
   convention matches a WORD, never a letter sequence; every entry carries a real boundary and an
   entry without one fails CI*), the guard file, the test-id range, what each closure closes, and
   the non-vacuity assertion. A test (`TC-ArgusAgent-DOCS-001-53`) asserts the registration text is
   still present — a rule that lives only in a test is not a rule.
4. **`CHANGELOG.md` gains ONE `###` section under `## Unreleased`**, consumer-facing: what was
   misclassified, what changes for a polyglot repository, and AC5.4's honest statement of
   direction. ⛔ Re-run `tests/test_release_note.py` and `tests/test_release_surface_honesty.py`;
   both must be green.
5. **⛔ `DF-11-1-A` is NOT closed and NOT touched** (§0.4, DN-7).
6. **Nothing open is closed by accident.** H0's unfiled Minions handoff, `DF-7-2-A`'s adjudication
   and the ≥80% precision gate all stay **OPEN** — `tests/test_v1_commitment_closure.py::-38` pins
   the first two and must stay green.

### AC7 — Gates, fences and the budget

1. **Full suite, `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`: 1352 baseline + exactly N new, 0 skipped, and
   EXACTLY ONE failure —**
   `tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed`,
   **carved out BY NODE ID as `DF-11-1-A` (§0.4)**. State N and what each new case is. ⛔ **Any
   second red is yours**, whatever file it is in.
2. **`mypy` clean on 72 source files** (the count must not move — no new module). **`bandit` 0 High
   / 0 Medium.** Coverage at or above the 80 gate, and its movement explained.
3. **`DF-10-4-D` fence, verified AFTER staging, not before:** `git ls-files -- argus` == **72**;
   `git status --porcelain -- argus/` shows **exactly four ` M` lines** (11.1's three, plus
   `argus/detectors/vacuous_test.py`) and **no `A` line**.
4. **LOC budget, re-run rather than assumed:** `build_full_repo_plan('.')` → unit 2 **≤ 15 000**
   (14 867 today ⇒ **133 available**), and **all three `partition_id`s byte-unchanged**
   (`477ef77d7b65…` / `82a3d605e61e…` / `ed6d08f25ce3…`). Record the consumed and remaining counts.
   ⛔ **If it tips: HALT and report. Never regenerate a dogfood artifact** (§A.6).
5. **`argus audit .` re-run and compared field by field.** `verdict=RELEASE_READY`,
   `blocking_findings=0`, `assessed_deep_ratio=61/77`, `scope=application`, exit `0` — all
   **unchanged**. `deep_ratio` / `held_out` denominators move by **exactly +1 per NEW TEST FILE you
   add** (baseline `61/165`, `held_out=88`), and the movement is **explained arithmetically, not
   observed**. ⛔ Any other movement means your change was not zero-instance in this repo and you
   must stop and explain it.
6. **The write set is exactly what §F declares** and everything else is **byte-unchanged**, proven
   with `git status --porcelain` **and** `git diff --stat` (E.5). **Nothing is pushed, tagged or
   dispatched.**
7. **Every figure is labelled LOCAL**, and CI evidence is recorded as **`NOT ESTABLISHED`** with
   the command a human runs (§0.1).

---

### §F. Write set — exactly this, nothing else

| Path | Action |
|---|---|
| `argus/detectors/vacuous_test.py` | **MODIFY** (existing — the only `argus/**` file; DN-4) |
| `tests/test_classification_word_boundary.py` | **NEW** (the corpus declaration + AC3 closure + AC4 re-proof + AC5 pins) |
| `tests/test_vacuous_detector.py` | **MODIFY** — one added case beside `-85`/`-95` importing the corpus (AC2.5). ⛔ Existing cases untouched. |
| `CHANGELOG.md` | **MODIFY** — one `###` section under `## Unreleased` |
| `_bmad-output/design-artifacts/ArgusAgent/architecture.md` | **MODIFY** — §Enforcement registration, **additive only** |
| `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` | **MODIFY** — **append-only**, +n/-0 |
| `_bmad-output/design-artifacts/ArgusAgent/stories/11-2-…md` | **MODIFY** (this file — `git add` it, E.5) |
| `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` | **MODIFY** — status transitions + your entry |

---

## Tasks / Subtasks

- [x] **T1 — Re-verify the premises before writing anything (AC7, §0.3).** (AC: 7)
  - [x] `git ls-files -- argus` (expect 72) · `git status --porcelain -- argus/` (expect 3 ` M`)
  - [x] `build_full_repo_plan('.')` — record unit 2 LOC and the three `partition_id`s
  - [x] Full suite; confirm **1352 / 1 failure / `DF-11-1-A` only** — this is your carve-out baseline
  - [x] Re-read `_UNAMBIGUOUS_TEST_SUFFIXES` and `_AMBIGUOUS_PYTHON_TEST_SUFFIXES` **by anchor**; if
        a coordinate in §A moved, record the drift and proceed on what you measured
- [x] **T2 — Declare the near-miss corpus, ONCE (AC2).** (AC: 2)
  - [x] `(path, expected_is_test, expected_content_dependent)` triples, union of both source lists
  - [x] Prove it **RED** against the unfixed tree for every false-positive row (E.1)
- [x] **T3 — Write AC3's closure guard, RED-first, with the final test code (AC3).** (AC: 3)
  - [x] Tables read out of the module; separator/registration rule; synthesized near-misses both
        directions; language closure with `c`/`php` exemptions; non-vacuity floors
  - [x] Record the RED naming **exactly three** offenders
- [x] **T4 — Write AC4's two-stage re-proof, RED-first (AC4).** (AC: 4)
  - [x] Behavioural polyglot fixture across **both** constants + the unreadable tier-3 case
  - [x] `ast` walk of `pipeline.py` (read-only) pinning the **two** construction sites
- [x] **T5 — Apply the fix in `argus/detectors/vacuous_test.py` (AC1).** (AC: 1)
  - [x] Remove the three separator-less entries; add the case-sensitive Java rule inside tier 2;
        add the `conftest.py` basename rule inside tier 3; document each with its reason
  - [x] ⛔ Re-run and confirm **zero existing tests changed** and `TC-…-DETECT-001-95` passes
        unmodified
- [x] **T6 — Pin the consequences (AC5).** (AC: 5)
  - [x] `latest.java` eligible + critical set non-empty; `myspec.rb` → `ZERO_DEFINITION_MODULE`
  - [x] Assert the FR16 table / vocabulary / exit codes unchanged
- [x] **T7 — Ledger, registration, release note (AC6).** (AC: 6)
  - [x] Close `DF-8-2-B` (append-only, verified programmatically) with the corrected count and the
        expired premise
  - [x] File the false-negative gaps and the `c`/`php` exemptions with named owners
  - [x] `architecture.md` §Enforcement registration + `TC-…-DOCS-001-53`
  - [x] `CHANGELOG.md` `###` section; re-run both release-note guards
- [x] **T8 — Gates, fences, budget, and the honest record (AC7).** (AC: 7)
  - [x] Full suite / `mypy` / `bandit` / coverage — all labelled **LOCAL**
  - [x] `git add` the new test **and** this story file, then re-check `git ls-files -- argus` == 72
  - [x] Re-run `build_full_repo_plan('.')`; record consumed/remaining; **HALT if unit 2 > 15 000**
  - [x] Re-run `argus audit .`; explain the denominator movement arithmetically
  - [x] Record CI evidence as **NOT ESTABLISHED**; **do not push, tag or dispatch**

### Review Findings

Code review, iteration 1 (Sonnet). Every hard-numeric claim in this story was independently
re-derived on disk, not read off the story: `git ls-files -- argus` = 72 with exactly four ` M`
lines and no `A` line under `argus/` (DF-10-4-D fence held); `build_full_repo_plan('.')` re-run
directly gives unit 2 = 14 900 LOC / 39 files with `partition_id`s `477ef77d7b65…` /
`82a3d605e61e…` / `ed6d08f25ce3…` byte-identical to the story's claim (33 of 133 consumed, matching
the `git diff --stat` net of the file: +42/-9 = +33 physical lines, 533 → 566); the full suite via
`--junit-xml` gives `tests="1362" failures="1" errors="0" skipped="0"`, and the one failure is
`tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed`
(`DF-11-1-A`) exactly as carved out — no second red; `mypy` clean on 72 source files; `bandit` 0
High / 0 Medium (19 Low); coverage re-measured at 95.82% exactly; `python -m argus.cli audit .`
reproduces `verdict=RELEASE_READY deep_ratio=61/166 blocking_findings=0 assessed_deep_ratio=61/77
scope=application held_out=89` exit 0, field-for-field; the current `argus/detectors/vacuous_test.py`
sha256 (`37c82e39003a1ad3074600d7754eee2749a59263b01125c67f85dcb603793e48`) matches the claimed
post-round-trip hash exactly, corroborating the RED-B restoration claim. `deferred-work.md`'s
Story-11.2 section is a clean append (lines 2259-2344, +86/-0) with `DF-8-2-B` closed and
`DF-11-2-A`/`DF-11-2-B` filed with named owners and target story 12.5, not fixed. `DN-1`
(`_CASE_SENSITIVE_TEST_SUFFIXES = ("Test.java",)` matched pre-lowering against the raw basename)
and `DN-2` (`conftest.py` as a whole-basename tier-3 rule, not dropped) are both implemented exactly
as locked, and `TC-ArgusAgent-DETECT-001-95` passes unmodified. `architecture.md` §Enforcement's new
paragraph and the `tests/test_release_surface_honesty.py` `_NOTE_SECTIONS` deviation (Completion
Note 7) are both legitimate, additive-only, and consistent with Story 11.1's precedent — not an
assertion bent to fit. AC4's structural walk correctly finds exactly two `_critical_ineligibility`
call sites (`_detect_per_file`, `_critical_candidate`), each deriving `is_test_file` once and
passing the same bound name — verified by reading `argus/pipeline.py` directly. The residual false
negatives left by `_CASE_SENSITIVE_TEST_SUFFIXES` (`*Tests.java`, `*TestCase.java`, prefix
`Test*.java`, minitest `_test.rb`, `_test.c`, PHPUnit `*Test.php`) are the safe direction (a test
file over-audited as production, never a production file wrongly excluded) and are transparently
filed as `DF-11-2-A`, not a hidden gap.

One inaccuracy found in the Dev Agent Record itself — the project's own recurring "hand-counted
enumeration was wrong" pattern (E.2), this time in a self-reported test measurement rather than in
the tables:

- [x] **[Review][Patch] Completion Note 3 claims "60 pairs generated" by
  `TC-ArgusAgent-DETECT-001-98`; the actual count is 32** [`tests/test_classification_word_boundary.py:328-358`]
  — independently computed: 16 registered table entries (13 + 1 + 1 + 1) × 2 synthesized prefixes
  (`"a"`, `"9"`) = 32 pairs, confirmed by reading the loop in `-98` and by direct execution against
  the live tables. The test's own `assert pairs >= 30` still holds (32 ≥ 30) and the guard is
  correct and non-vacuous as written — this is a prose inaccuracy in the narrative record this
  story itself introduced, not a code or test defect, and it does not affect any AC or gate figure.
  Fix: correct "60 pairs generated" to "32 pairs generated" in this story's Completion Notes List
  item 3, and in `sprint-status.yaml`'s matching `11-2-polyglot-repository-is-classified-correctly`
  last_updated comment (same wording was copied there).

  **✅ RESOLVED, fix iteration 1 (2026-08-12).** The count was **re-derived by execution, not copied
  from the finding** — required, because the finding is itself about asserting a number that was
  never measured. Method: `sys.settrace` over a run of the **real** `-98` test function, capturing
  its own `pairs` local at frame return (no re-implementation of the loop, no transcription).
  Result: **`pairs = 32`**, test passing, with `_all_registrations()` reporting
  `_UNAMBIGUOUS_TEST_SUFFIXES` 13 · `_AMBIGUOUS_PYTHON_TEST_SUFFIXES` 1 ·
  `_CASE_SENSITIVE_TEST_SUFFIXES` 1 · `_AMBIGUOUS_PYTHON_TEST_BASENAMES` 1 = **16 entries × 2
  prefixes = 32** — two independent routes to the same number. Corrected in Completion Note 3 and in
  both copied occurrences in `sprint-status.yaml`. ⛔ **Prose only:** `tests/test_classification_word_boundary.py`
  is byte-unchanged — the guard's `assert pairs >= 30` floor is correct and non-vacuous as written
  (32 ≥ 30) and was NOT touched, and no `argus/**` file was touched (DF-10-4-D fence, DN-4).

Severity: Low. No High/Medium findings. No `decision-needed` or unresolved `patch` items — every
AC, fence, gate and DN was independently verified to hold. Full suite, `mypy`, `bandit`, coverage
and `argus audit .` are all green/as-claimed on this LOCAL run; nothing pushed, tagged or
dispatched. Verdict: **concerns** (the one Low item does not block, but the pattern — an
un-re-derived count in a project whose own culture is "verify, do not transcribe" — is worth a
correction pass).

---

**Code review, iteration 2 (Sonnet) — NARROW CONFIRMATION of fix iteration 1's single Low
finding, not a full re-review.** Everything iteration 1 already independently re-derived (the
`DF-10-4-D` fence, the LOC budget, the test ledger, DN-1/DN-2, both closures, the deferred-work
append, the `test_release_surface_honesty.py` deviation) was **not re-litigated**, per instruction.

1. **The corrected count is RIGHT and was measured, twice, independently by this reviewer too.**
   `_all_registrations()` executed live: `_UNAMBIGUOUS_TEST_SUFFIXES` 13 ·
   `_AMBIGUOUS_PYTHON_TEST_SUFFIXES` 1 · `_CASE_SENSITIVE_TEST_SUFFIXES` 1 ·
   `_AMBIGUOUS_PYTHON_TEST_BASENAMES` 1 = **16 entries**, × the `-98` loop's **2** synthesized
   prefixes (`"a"`, `"9"`) = **32**. `TC-ArgusAgent-DETECT-001-98` re-run directly: **passes**. ✅
2. **The correction landed in BOTH places.** Story Completion Note 3 (line ~1115) now reads "32
   pairs generated"; `sprint-status.yaml` line 221 (`last_updated` comment) and line 390 (the
   `11-2-…` `development_status` comment) both read "32", not "60" — confirmed by direct grep. ✅
3. **The guard was NOT re-baselined.** `tests/test_classification_word_boundary.py` still reads
   `assert pairs >= 30` (32 ≥ 30, non-vacuous, unchanged). File mtime (2026-08-11 23:34) predates
   the fix-iteration-1 timestamp (2026-08-12); only the story file and `sprint-status.yaml` carry a
   2026-08-12 mtime — the write set really is "prose in two files," not a re-baseline. ✅
4. **Nothing else moved, all independently re-run:** `git ls-files -- argus` = **72**;
   `git status --porcelain -- argus/` = exactly **four ` M`** lines (`cli.py`,
   `detectors/vacuous_test.py`, `reports/generator.py`, `verdict/negative_assurance.py`), **no `A`**;
   `argus/detectors/vacuous_test.py` sha256 = `37c82e39003a1ad3074600d7754eee2749a59263b01125c67f85dcb603793e48`
   (matches claim exactly, mtime 2026-08-11, untouched by this round); dogfood
   `build_full_repo_plan('.')` re-run directly gives unit 2 = **14 900** LOC with all three
   `partition_id`s byte-identical (`477ef77d7b65…` / `82a3d605e61e…` / `ed6d08f25ce3…`); full suite
   via `--junit-xml` gives `tests="1362" failures="1" errors="0" skipped="0"`, and the one failure
   is `tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed`
   (`DF-11-1-A`) — no second red; `mypy` clean on 72 source files; `bandit` 0 High / 0 Medium (19
   Low). ✅
5. **`sprint-status.yaml` parses clean** (`yaml.safe_load` succeeds) with the `STATUS DEFINITIONS`
   block intact (line 186) and all history comments preserved. ✅
6. **Nothing published.** `origin/master` is still at `00c8d1b`; local `master` is 6 commits ahead;
   `git tag -l` is empty. No push, tag, release or dispatch. ✅

All six confirmation items hold. The single Low finding from iteration 1 is fully resolved, with
no new issues introduced by the fix. **Verdict: PASS.** Status → `done`.

---

## Dev Notes

### LOCKED decisions taken at story design — record these, do not re-litigate

- **DN-1 — Java's word separator is a CASE boundary, matched case-sensitively on the
  original-case basename.** `DF-8-2-B`'s alternative spelling `"_test.java"` is **wrong** and would
  delete every Java true positive (§A.2, measured). Java/Maven-Surefire convention is `*Test.java`
  in CamelCase; lowercasing destroys the only boundary the name has.
- **DN-2 — `conftest.py` is preserved as an explicit whole-BASENAME rule, still in TIER 3.** It is
  what the bare `"test.py"` was really standing in for, and `TC-ArgusAgent-DETECT-001-95` pins it
  as content-dependent (§A.5, discovered by the §B experiment failing).
- **DN-3 — the Python entry is fixed, and NOT because it is release-blocking.** Its harm is masked
  by tier-3 content resolution and by `_critical_ineligibility`'s unreadable carve-out. It is fixed
  so AC3's closure has a **uniform contract** rather than a named exemption for a known-defective
  entry (§A.4). Do not restate it as a severity claim.
- **DN-4 — ZERO new `argus/**` files.** Operator ruling for all of Epic 11 (`DF-10-4-D`, §0.2).
  Everything lands in `argus/detectors/vacuous_test.py`. `git ls-files -- argus` stays **72**.
- **DN-5 — false NEGATIVES are out of scope and are FILED, not fixed.** `_test.rb`, `*Tests.java`,
  `*TestCase.java`, `*Test.php`, `_test.c`, and the `c`/`php` gaps. This story only *removes* false
  positives; adding a convention moves classification on real repositories and belongs to a story
  that can measure that (§A.7, §D).
- **DN-6 — no new report surface for `heuristic_excluded_ineligible`.** The false `test_file` token
  reaches **no operator surface** (measured, §A.3); that is `DF-8-3-A` and it belongs to the 12.1
  extraction story. The operator-visible harm is the `held_out=` count and the *"N test file(s)"*
  report line, and stating more than that would be its own overclaim.
- **DN-7 — `DF-11-1-A` stays deferred and is carved out BY NAME** (§0.4). Three reasons recorded
  there; Story 8.1's AC18 is the precedent.
- **DN-8 — `DF-8-3-C` does NOT fire.** Its close condition is the `DF-8-2-A` `pipeline.py`
  extraction, not "any story that edits `vacuous_test.py`". Do not add
  `partition_application_files`; it lands in the byte-fenced `pipeline.py` and belongs to 12.1.

### Architecture patterns & constraints a reviewer will check

- **AR7 / §3.3** — no second mechanism; the tier structure is declared once and read by both public
  predicates. The guard reads the tables **out of the module**; it never restates them.
- **AR8** — `detectors/` may not be imported by `ledger/`; `pipeline.py` is the impure shell that
  owns `is_test_file` and passes the *fact* down. Your change must not invert that.
- **NFR-P2** — *"the language conditional remains confined to `argus/index/`."* ⚠️ Your
  case-sensitive Java rule is a language-specific **naming convention**, which lives in
  `detectors/` beside the conventions already there — it is **not** a grammar/parse conditional and
  does not breach NFR-P2. Say so in the code comment so a reviewer does not have to work it out.
- **FR4** (`prd.md`) — *"a file APAA can never grade `audited_deep` is ineligible for the
  heuristically-derived critical set."* The defect inverts this: it makes a file Argus **can** grade
  deep ineligible, under a false reason.
- **FR7 / NFR-P2** — multi-language AST grounding is **delivered in V1**, and
  `argus/shared/source_languages.py` is the **source of truth, deliberately not a hand-typed list**.
  AC3.5 derives its language set from that module for exactly that reason.
- **FR16 / FR37** — classification vs explanation. Untouched, asserted (AC5.3).

### Testing standards — the house form your new file matches

- Test ids `TC-ArgusAgent-<AREA>-<NNN>-<nn>`, one per test, in the docstring first line, with the
  AC it discharges. Next free: **`DETECT-001-96`+**, **`PIPELINE-002-10`+**, **`DOCS-001-53`**.
- The guard idiom established by 10.1→11.1 and expected here: **registry + closure + both-direction
  positive control + explicit non-vacuity assertion**, with failure messages that name the remedy
  and say *a red here is the guard working*.
- Fixtures are **staged into `tmp_path`** and driven through the real functions
  (`build_ast_index` → `_detect_per_file` → `CoverageLedger.build` →
  `identify_critical_subsystems`) — see `tests/test_critical_eligibility_pipeline.py::_stage`
  / `_request` / `_detect_per_file` for the exact shape to follow.
- Static walks use the **stdlib `ast` over source read as text**. The 10.5 DN-6 rule (*no
  `import argus` in a static guard*) applies to the `pipeline.py` walk in AC4.2; AC3's table read
  **does** import the module, which is correct — it is reading data, not tracing reachability.
- ⛔ **No new dependency. No network. No `float`. Deterministic ordering everywhere.**

### Previous story intelligence

- **11.1 (`done`, PASS on review iteration 1)** — the immediately preceding story, and its delta is
  live in your tree. It proved the DF-10-4-D fence holds when every line lands in existing files,
  and it consumed 74 of its 207-line budget. Its two Low review observations are **fixed by this
  story's design**: (a) the "full suite green" wording now carves out `DF-11-1-A` by node id
  (AC7.1); (b) the inherited-dirty file list is stated in the frontmatter rather than presented as
  this story's fence.
- **10.4** — HALTED on `DF-10-4-D` and was right to. Its ruling stands: **never regenerate a
  committed artifact to make a staleness test pass.**
- **10.5** — its RED-first re-demonstration with the *final* test code found a real bug in its own
  guard. Do the same (E.1).
- **10.2 / 10.3 / 10.4 / 10.5 / 11.1** — five consecutive stories whose hand-counted enumerations
  were wrong. This story's was too (§A.4). That is what AC3 is for.
- **8.2** — introduced the eligibility filter and `CriticalIneligibility`; **8.3** — reused the
  predicate rather than forking it (AC8) and fenced `vacuous_test.py`, which is why `DF-8-2-B` has
  waited three epics for a story that actually edits the file. **This is that story.**

### Runtime & toolchain, verified on this machine 2026-08-11

Windows · CPython **3.11.15** · `pytest` 9.1.1 · `mypy` clean on 72 sources ·
`ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` set for every suite run · `tree-sitter` grammars present for
all 10 languages (Java **grounds and extracts definitions**; Ruby grounds and extracts **zero** —
`DF-10-2-A`). **No CI run covers this tree** (§0.1).

### Project structure notes

`argus/detectors/vacuous_test.py` (533 lines) owns the tier structure and both public predicates.
`argus/pipeline.py` (1331 lines, byte-fenced to 12.1) is the impure shell that evaluates
`is_test_file` **once** and passes the fact to `_critical_ineligibility`; `argus/ledger/` consumes
the fact and never imports `detectors/` (AR8). `argus/reports/generator.py` re-derives the
application partition (`DF-8-3-C`, 12.1's). No file moves and no module is added.

### Open questions for the operator — saved for the end, as the workflow requires

1. **Should a later story ADD the missing conventions (`_test.rb`, `*Tests.java`, `*TestCase.java`,
   `Test*.java`, `*Test.php`, `_test.c`)?** This story files them (AC6.2) and deliberately does not add them —
   they are false *negatives*, they move classification on real repositories, and Epic 11 is the
   wrong epic for a widening. **Recommendation of record: schedule with Story 12.5** (which already
   owns *"a deliberately-excluded language states its absence AND reason at the point of
   downgrade"*), since the same disclosure surface answers both.
2. **`DF-11-1-A` — the standing red.** It will fail every remaining Epic 11 story's gate and cost
   each one a carve-out. It is a two-minute human step and it is not a story's to take:
   either **commit or remove** `epic-10-retro-2026-08-11.md`, or **register** it in
   `_STATUS_DOCUMENTS` **and** give the retro the citation the rule requires (a run id + the sha it
   covers, or a `NOT ESTABLISHED` marker). ⛔ Neither is done from inside a story.
3. **`DF-8-2-B`'s severity was 🟢 and the measurement says otherwise** (§A.3 — a vacuously satisfied
   FR16 critical clause and a reachable false green). The ledger entry is **append-only**, so the
   closure records the escalation rather than editing the original. Confirm that is the disposition
   you want, or rule that the original severity be annotated separately.

### References

- Epic + story ACs, and the binding *"the surrounding code has changed"* note:
  [epics.md](../epics.md) §Epic 11 / Story 11.2 (lines ~2018–2058)
- Ledger entry and its close condition: [deferred-work.md](../deferred-work.md) `DF-8-2-B`
  (~line 571); adjacent fences `DF-8-3-A` (~603), `DF-8-3-C` (~656), `DF-10-4-D`, `DF-10-2-A`,
  `DF-11-1-A`
- FR4 / FR7 / FR16 + decision table / FR37 / NFR-P2: [E-PRD/prd.md](../E-PRD/prd.md) lines
  485, 493, 510, 523–525, 601
- §Enforcement registrations to model yours on, and §Error/Degradation:
  [architecture.md](../architecture.md) lines ~694–760
- Retrospective action items AI-E10-1 / -2 / -3 / -5 / -7:
  [epic-10-retro-2026-08-11.md](../epic-10-retro-2026-08-11.md) §7–§8, and `sprint-status.yaml`
  `action_items:`
- Prior story: [11-1-tool-discloses-its-status-with-an-expiry.md](11-1-tool-discloses-its-status-with-an-expiry.md)
  §0.2 (the fence), §A.5 (the budget mechanism), §E (the traps)
- Code under change / read: `argus/detectors/vacuous_test.py`, `argus/pipeline.py`
  (`_critical_ineligibility`, `_critical_candidate`, `_detect_per_file`),
  `argus/ledger/critical_subsystems.py`, `argus/shared/source_languages.py`
- External convention sources checked 2026-08-11 (no dependency, no version risk — these are naming
  conventions, not APIs): Maven Surefire *Inclusions and Exclusions of Tests*
  (`**/Test*.java`, `**/*Test.java`, `**/*Tests.java`, `**/*TestCase.java` — the four defaults,
  all CamelCase) at <https://maven.apache.org/surefire/maven-surefire-plugin/examples/inclusion-exclusion.html>;
  `pytest`'s `python_files = test_*.py *_test.py` default (which is why `mytest.py` is correctly
  production and `conftest.py` is special-cased by `pytest` itself); RSpec's `*_spec.rb`.
  ⛔ **No library, framework or version changes in this story — nothing to upgrade, nothing to pin.**
- Tests that constrain you: `tests/test_vacuous_detector.py` (`-85`, `-95`),
  `tests/test_test_file_classification.py`, `tests/test_critical_eligibility_pipeline.py`
  (`PIPELINE-002-02`, `-09`), `tests/test_pipeline_coverage_scope.py`,
  `tests/test_multilanguage_audit.py`, `tests/test_report_surface_consistency.py`

---

## Dev Agent Record

### Context Reference

This story file (§0–§F), read in full before any write. Every figure below was **re-derived by
execution on this tree**, not transcribed from §A. Where a measurement differed from the story, the
drift is recorded rather than smoothed over (there was one, and it is in the Debug Log).

### Agent Model Used

`claude-opus-5[1m]` (BMAD `dev-story`, mode `implement`, single pass, no fix iteration).

### Debug Log References

**T1 — premises re-verified before writing anything. All held.**

| Premise | Re-measured 2026-08-11 | Verdict |
|---|---|---|
| `git ls-files -- argus` | **72** | ✅ |
| `git status --porcelain -- argus/` | exactly **3 ` M`** (11.1's delta) | ✅ |
| dogfood unit 2 | **14 867 / 15 000**, ids `477ef77d7b65…` / `82a3d605e61e…` / `ed6d08f25ce3…` | ✅ |
| Full suite | **1352 collected, 1351 passed, 1 failed, 0 skipped** — the failure is `DF-11-1-A` only | ✅ |
| `"test.java"` / `"spec.rb"` on line **198**, bare `"test.py"` on line **207** | exact, by anchor | ✅ |
| `vacuous_test.py` sha256 | `85af39dd98e4362df2e8dddaf9567ee3dd0a0cb3218124a99752be667b6364f0` — **identical to §B's** | ✅ |

**Only drift found:** none in §A. §0.3's three premises, §A.4's count of **three**, and §A.6's
14 867 all reproduced exactly. (One divergence appeared later, in the *write set* rather than in a
measurement — see Completion Note 7.)

---

**RED-first, run TWICE with the FINAL test code (E.1). Both are recorded because they prove
different things.**

**RED-A — the genuinely unfixed tree, before a single production byte moved.** Seven of the ten new
cases failed; `PIPELINE-002-11` (the structural `ast` walk) passed, which is *correct* — the defect
was never in the mechanism, it was in the tables, and that is exactly why AC4 re-**proves** the
invariant instead of repairing it. AC3's closure named **exactly three** offenders, as AC3.3
requires:

```
AssertionError: a name-based test convention must match a WORD, never a letter sequence — 3 entry/entries do not:
  - _UNAMBIGUOUS_TEST_SUFFIXES entry 'test.java' begins with no registered word separator ('_', '.'), so it
    matches a LETTER SEQUENCE: every basename merely ending in 'test.java' is claimed as a test
  - _UNAMBIGUOUS_TEST_SUFFIXES entry 'spec.rb' begins with no registered word separator ('_', '.'), …
  - _AMBIGUOUS_PYTHON_TEST_SUFFIXES entry 'test.py' begins with no registered word separator ('_', '.'), …
Add the real separator the convention actually uses (`_`, `.`, a CamelCase capital, or the whole basename),
or register the entry in the table whose boundary rule it satisfies. A red here is the guard working: …
```

and `PIPELINE-002-12` reproduced **the false green itself**, end-to-end, before the fix:

```
AssertionError: ordinary production Java is excluded from the FR4 critical set under the reason
`test_file` — the false statement that made FR16's critical clause vacuous
assert <CriticalIneligibility.TEST_FILE: 'test_file'> is None
  where … CriticalCandidate(file_path='svc/latest.java',
                            criticality=<Criticality.CRITICAL: 'critical'>,
                            ineligibility=<CriticalIneligibility.TEST_FILE: 'test_file'>)
… and depth_by_path['svc/latest.java'] was AUDITED_SHALLOW, not AUDITED_DEEP.
```

**Measured before-state, recorded here rather than asserted as a live expectation (AC5.1):**
`svc/latest.java  is_test=True  depth=audited_shallow  crit=CRITICAL  inelig=test_file` — matching
§A.3 exactly, on an independently authored fixture.

**RED-B — E.1's mandated re-demonstration against the FINAL module structure.** After the fix, the
three defective entries were restored into the *new* tables and both closures bit again: `-97` named
the same **three** offenders (so the red is attributable to the entries, not to a missing registry),
and `-98` fired on a **synthesized** case nobody hand-listed — `'svc/atest.java' is production code:
it merely ENDS with the letters of the _UNAMBIGUOUS_TEST_SUFFIXES convention 'test.java'`. The file
was then restored and the **sha256 round-tripped byte-identically**:
`37c82e39003a1ad3074600d7754eee2749a59263b01125c67f85dcb603793e48` before **and** after.

---

**Gate figures — every one LOCAL (Windows · CPython 3.11.15), re-run, none attributed.**

| Gate | Result |
|---|---|
| Full suite (`ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`) | **1362 = 1352 baseline + exactly 10 new**, 0 skipped, 0 errors, **exactly ONE failure** |
| The one failure | `tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed` — **`DF-11-1-A`**, carved out by node id (§0.4) |
| `mypy` | clean, **72 source files** — the count did not move |
| `bandit` | **0 High / 0 Medium** (19 Low) |
| Coverage | **95.82 %** (gate 80). Baseline 95.77 %; **+0.05** because the ~33 added production lines are fully exercised by the new guards |
| `git ls-files -- argus` **after staging** | **72** |
| `git status --porcelain -- argus/` | exactly **four ` M`** (11.1's three + `argus/detectors/vacuous_test.py`), **no `A`** |
| dogfood unit 2 | 14 867 → **14 900 = 33 consumed of 133, 100 remaining**; all three `partition_id`s **byte-unchanged** |
| `argus audit .` | `verdict=RELEASE_READY deep_ratio=61/166 blocking_findings=0 assessed_deep_ratio=61/77 scope=application held_out=89`, exit **0** |
| CI evidence | **NOT ESTABLISHED** |

**The audit movement, explained arithmetically rather than observed (AC7.5).** Four fields are
byte-identical to baseline: `verdict`, `blocking_findings`, `assessed_deep_ratio=61/77`, `scope`,
exit `0`. Two moved by exactly **+1**: `deep_ratio` 61/165 → **61/166** and `held_out` 88 → **89** —
one new test file, `tests/test_classification_word_boundary.py`, which enters the enumerated
population *and* is held out of application scope because tier 1 classifies it by LOCATION. The
arithmetic closes exactly: **166 − 89 = 77**, the unmoved application denominator, and the numerator
**61 is unchanged**, which is the direct evidence that no file changed grading class. Independently
re-verified: `git ls-files` finds **no** `.java`, **no** `.rb`, **no** `conftest.py` and **no**
bare-suffix `*test.py` under any tracked path, so the change is genuinely zero-instance here.

**CI evidence — `NOT ESTABLISHED` (§0.1, 10.1's rule applied to my own run).** No `audit-ci.yml`
run covers this `HEAD`; the last executed run (`31341363300`) is sha-scoped to `00c8d1b`, which
contains none of Epic 10 or 11. Every figure above is **LOCAL**. The command a human runs, after
pushing: `gh workflow run audit-ci.yml --ref master`, then cite the run id **plus the sha it
covers**. ⛔ Nothing was pushed, tagged or `workflow_dispatch`-ed to manufacture that citation
(10.1's DN-7; Epic 11 publishes nothing — that is 12.9).

---

**FIX ITERATION 1 — 2026-08-12. The re-derivation, and the gates re-run to prove nothing moved.**

*The measurement that IS the fix (Completion Note 12). Two independent routes, neither of them a
transcription of the review's number:*

| Route | Method | Result |
|---|---|---|
| **(a) the real test's own frame** | `sys.settrace` over a live call of `test_TC_ArgusAgent_DETECT_001_98_…`, capturing its `pairs` local at frame return — the loop is **executed, not re-implemented** | **`pairs = 32`**, test **passing** |
| **(b) the live tables** | `_all_registrations()`: `_UNAMBIGUOUS_TEST_SUFFIXES` **13** · `_AMBIGUOUS_PYTHON_TEST_SUFFIXES` **1** · `_CASE_SENSITIVE_TEST_SUFFIXES` **1** · `_AMBIGUOUS_PYTHON_TEST_BASENAMES` **1** = **16** entries × the loop's **2** prefixes (`"a"`, `"9"`) | **32** |

The guard's own floor `assert pairs >= 30` holds (**32 ≥ 30**) and is non-vacuous, so
`tests/test_classification_word_boundary.py` was **not edited** — re-baselining a threshold to
agree with a corrected count is the antipattern this project has refused twice (10.4, §A.6).

*Gates re-run after the prose correction — every figure LOCAL (Windows · CPython 3.11.15), and
every one identical to the pre-fix round:*

| Gate | Fix-round result | vs. implement round |
|---|---|---|
| Full suite (`--junit-xml`, `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`) | `tests="1362" failures="1" errors="0" skipped="0"` | **unmoved** |
| The one failure | `tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed` — **`DF-11-1-A`**, carved out by node id. **No second red** | **unmoved** |
| `mypy` | clean, **72 source files** | **unmoved** |
| `bandit` | **0 High / 0 Medium** (19 Low) | **unmoved** |
| `git ls-files -- argus` | **72** | **unmoved** (DF-10-4-D fence holds) |
| `git status --porcelain -- argus/` | exactly **four ` M`**, **no `A`** | **unmoved** |
| `argus/detectors/vacuous_test.py` sha256 | `37c82e39003a1ad3074600d7754eee2749a59263b01125c67f85dcb603793e48` | **byte-identical** — no `argus/**` byte moved |
| dogfood unit 2 | **14 900 / 15 000** — 33 consumed of 133, **100 remaining** | **unmoved** |
| `partition_id`s | `477ef77d7b65…` / `82a3d605e61e…` / `ed6d08f25ce3…` | **all three byte-unchanged** |
| `argus audit .` | `verdict=RELEASE_READY deep_ratio=61/166 blocking_findings=0 assessed_deep_ratio=61/77 scope=application held_out=89`, exit **0** | **field-for-field unmoved** |
| CI evidence | **NOT ESTABLISHED** — no `audit-ci.yml` run covers this `HEAD`; a human runs `gh workflow run audit-ci.yml --ref master` and cites the run id **plus the sha it covers** | unchanged |

**Nothing published** — no push, no tag, no `workflow_dispatch` (Epic 11 publishes nothing; that is
12.9). The round's entire write set is **prose in two files**: this story's Completion Note 3 (plus
this record) and the two copied occurrences in `sprint-status.yaml`. No test, no `argus/**` source,
no ledger, no `architecture.md`, no `CHANGELOG.md` byte was touched.

### Completion Notes List

1. **The fix is 33 physical lines in ONE existing file.** `_UNAMBIGUOUS_TEST_SUFFIXES` lost
   `"test.java"` and `"spec.rb"`; `_AMBIGUOUS_PYTHON_TEST_SUFFIXES` lost the bare `"test.py"`;
   `_CASE_SENSITIVE_TEST_SUFFIXES = ("Test.java",)` was added **inside tier 2**, matched against the
   **original-case** basename *before* the lowercasing (DN-1); `_AMBIGUOUS_PYTHON_TEST_BASENAMES =
   ("conftest.py",)` was added **inside tier 3** (DN-2). No new `argus/**` file (DN-4), no new
   import, no new dependency; the predicates stay pure (AR8), the tier structure stays declared once
   and read by both public predicates (AR7/§3.3), the tier ORDER is unchanged, and
   `_exhibits_test_definitions`' unreadable-defaults-to-`True` direction is untouched (§C).
2. **Zero existing test assertions changed, as §B measured.** The six-item §B.1 watchlist was run
   individually before and after and is green throughout; `TC-ArgusAgent-DETECT-001-95` passes
   **unmodified**. That is the evidence the change is a repair and not a redefinition.
3. **The load-bearing ACs shipped as closures, never lists (AI-E10-5).** `-97` reads both tables
   **out of the module** and fails on any entry carrying no registered boundary, naming itself;
   `-98` **synthesizes** every adversarial near-miss from those same tables (**32 pairs generated** —
   16 registered entries (13 + 1 + 1 + 1) × 2 synthesized prefixes (`"a"`, `"9"`); **re-derived by
   execution**, see Completion Note 12)
   and asserts **both** directions, so a fix that removed the false positives by deleting the
   conventions would fail here (E.4); `-99` closes over `LANGUAGE_BY_SUFFIX`, so all **10** grounded
   languages are decided — **8** carry a convention, `c` and `php` are **registered reason-carrying
   exemptions** — and it goes red in *both* directions (an 11th language with no decision, or an
   exemption that has quietly acquired a convention). Every closure carries an explicit `> 0`
   non-vacuity floor (E.3): tables resolved, registrations read, pairs synthesized, languages
   enumerated, functions parsed.
4. **AC4's re-proof is behavioural AND structural, and it proves itself.** `-10` drives the real
   pipeline over an 8-file polyglot fixture spanning **both** constants and their interaction, then
   runs its own invariant assertion against a **synthetic disagreement** and requires it to fire — a
   re-proof that cannot fail is not a proof. `-11` walks `argus/pipeline.py` with the stdlib `ast`
   over source read as **text** (10.5's DN-6; the file stays byte-fenced to 12.1) and pins the
   **two** construction sites measured in §A: each must evaluate `is_test_file` exactly once, bind
   it to one name, and hand *that* name to `_critical_ineligibility`. A third derivation turns it
   red — that is the only mechanism by which the two stages could come to disagree.
5. **The false green is proven closed end-to-end, not asserted (AC5).** On the same fixture that
   reproduced it, `svc/latest.java` is now CRITICAL **and** eligible **and** `audited_deep`, and the
   critical set is **non-empty**. `svc/myspec.rb` stays excluded — but its reason moved from the
   **false** `test_file` to the **true** `ZERO_DEFINITION_MODULE` (`DF-10-2-A` observed, **not**
   fixed, §D). FR16's decision table, the verdict vocabulary and all three exit codes are
   **asserted** unchanged by `-13` rather than described as unchanged in prose.
6. **False NEGATIVES were filed, not fixed (DN-5).** `DF-11-2-A` (minitest `_test.rb`, Surefire
   `*Tests.java` / `*TestCase.java` / `Test*.java`, PHPUnit `*Test.php`, `_test.c`) and `DF-11-2-B`
   (the `c`/`php` no-convention exemptions), each with a **named owner** (Delivery Orchestrator) and
   a **target story** (12.5, following the story's own recommendation of record). `DF-8-2-B` is
   CLOSED **append-only** — verified programmatically, `after.startswith(before)` is `True`, **+86 /
   −0** — recording the corrected count (**three**, not two), the **expired premise**, and the
   measured vacuous-critical-set result. The severity escalation is recorded in the closure note
   rather than by editing the original 🟢, since the entry is append-only (operator open question 3).
7. **⚠️ ONE DEVIATION FROM §F's WRITE SET, recorded rather than hidden.**
   `tests/test_release_surface_honesty.py` gained **one additive `_NOTE_SECTIONS` registry entry**.
   It is not in §F, and here is why it was unavoidable and why it is not a weakening: AC6.4 mandates
   a new `###` section under `## Unreleased`, and `TC-ArgusAgent-DOCS-001-16` is *designed* to go RED
   until such a section is **registered deliberately** — its own failure message says so, and Story
   11.1 registered its section exactly this way. No assertion was modified, weakened or removed; the
   pinned set only grew. **The two ACs are in tension and the project standard wins:** AC1.7's
   "do not adjust the test" governs the *classification* fix (which needed no test adjusted — note
   2), while a registration guard's entire purpose is to cost a deliberate edit. The section's
   PLACEMENT was a decision that registry's own comment demands rather than a default: 11.1's
   instrument disclosure stays **first**, because it bounds how a consumer should weigh every other
   claim in the note — including this one — and demoting it beneath a behavioural fix would be the
   wrong signal for an assurance tool.
8. **The CHANGELOG states the direction of the change instead of hedging it (AC5.4).** It says
   plainly that a polyglot repository's verdict **may move**, that it can only move
   **conservatively**, and that it can **never** turn a blocking verdict into `RELEASE_READY`. Both
   losses are stated rather than left to be discovered: a literal `spec.rb` outside a `spec/`
   directory, and a literal `test.py`. It does **not** describe the change as behaviour-preserving,
   because on the target audience's repositories it is not.
9. **Nothing open was closed by accident (AC6.6).** `tests/test_v1_commitment_closure.py::-38` is
   green — H0's unfiled Minions handoff and `DF-7-2-A`'s adjudication both stay OPEN — and the ≥80 %
   precision gate is untouched. **`DF-11-1-A` was not closed and not touched** (DN-7):
   `epic-10-retro-2026-08-11.md` was neither registered in `_STATUS_DOCUMENTS`, nor `git add`-ed,
   nor deleted. **No operator surface was added for `heuristic_excluded_ineligible`** (DN-6 —
   `DF-8-3-A` is 12.1's), **`partition_application_files` was not added** (DN-8 — `DF-8-3-C` does not
   fire here), and `argus/pipeline.py`, `argus/ledger/**`, `argus/reports/**`, `argus/cli.py` and
   `argus/verdict/**` are all **byte-unchanged** (the four ` M` lines under `argus/` are 11.1's three
   plus this story's one file).
10. **The budget was re-run, not assumed, and it did not tip.** 33 of 133 lines consumed, 100 left,
    all three `partition_id`s byte-unchanged — so no committed dogfood artifact was regenerated, and
    none needed to be. Had it tipped, the mandated response was HALT (§A.6, 10.4's ruling).
11. **Not committed.** The delta is **staged** (`git add` of the new test **and** this story file,
    E.5) and left for the review gate; no AC requires a commit and the operator did not ask for one.
    The inherited-dirty paths named in the frontmatter were not committed, reverted or restaged.
12. **⚠️ FIX ITERATION 1 (2026-08-12) — the one Low review finding: a count I asserted and never
    measured.** Completion Note 3 said `-98` generates **60** adversarial pairs. It generates **32**.
    This is the project's own E.2 pattern (six hand-counted enumerations, six wrong) reappearing in
    the *narrative record* rather than in a table — the worse place for it, because §A's whole
    method statement is *"re-derive everything; transcribe nothing."* **The correction was itself
    re-derived by execution, not copied from the review:** `sys.settrace` over a run of the real
    `-98` function, capturing its own `pairs` local at frame return — **32**, test passing —
    cross-checked against `_all_registrations()` (13 + 1 + 1 + 1 = **16** entries × the loop's **2**
    prefixes `"a"`/`"9"` = **32**). Two independent routes, one number. **The guard is untouched and
    was never the defect:** its `assert pairs >= 30` non-vacuity floor is correct and non-vacuous
    (32 ≥ 30), so `tests/test_classification_word_boundary.py` is **byte-unchanged**; lowering or
    re-baselining that threshold to "match" a corrected count would have been the antipattern, not
    the fix. Scope of the round is prose in two files (this note 3 + both copied occurrences in
    `sprint-status.yaml`). **No `argus/**` byte moved** — `git ls-files -- argus` still **72**, the
    module's `sha256` still `37c82e39003a…`, and all three `partition_id`s and the 33-of-133 LOC
    consumption are unmoved, all re-verified below.

### File List

| Path | Action |
|---|---|
| `argus/detectors/vacuous_test.py` | **MODIFY** — the only `argus/**` file (DN-4); +33 physical lines |
| `tests/test_classification_word_boundary.py` | **NEW** — corpus + AC3 closures + AC4 re-proof + AC5 pins + AC6.3 registration guard (9 cases) |
| `tests/test_vacuous_detector.py` | **MODIFY** — one added case (`TC-ArgusAgent-DETECT-001-100`) **importing** the corpus; existing cases untouched |
| `tests/test_release_surface_honesty.py` | **MODIFY** — one additive `_NOTE_SECTIONS` registry entry (**deviation from §F — see Completion Note 7**) |
| `CHANGELOG.md` | **MODIFY** — one `###` section under `## Unreleased` |
| `_bmad-output/design-artifacts/ArgusAgent/architecture.md` | **MODIFY** — §Enforcement registration, additive only |
| `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` | **MODIFY** — append-only, +86 / −0 (verified programmatically) |
| `_bmad-output/design-artifacts/ArgusAgent/stories/11-2-polyglot-repository-is-classified-correctly.md` | **MODIFY** — this file (`git add`-ed, E.5) |
| `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` | **MODIFY** — `ready-for-dev` → `in-progress` → `review` + record; all comments and STATUS DEFINITIONS preserved |

---

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-08-12 | 1.1 | **Fix iteration 1 — 1 of 1 review findings resolved (Low, prose only).** The review's single open item: Completion Note 3 claimed `TC-ArgusAgent-DETECT-001-98` generates **60** adversarial pairs; it generates **32**. **The corrected count was re-derived by execution, not copied from the review** — mandatory, since the finding is itself about asserting a number that was never measured: `sys.settrace` over a run of the **real** `-98` function captured its own `pairs` local at frame return (**32**, test passing), cross-checked against `_all_registrations()` (13 + 1 + 1 + 1 = **16** entries × **2** synthesized prefixes = **32**). Corrected in Completion Note 3 and in **both** copied occurrences in `sprint-status.yaml`; all comments and the STATUS DEFINITIONS block preserved. ⛔ **The guard was NOT touched** — its `assert pairs >= 30` floor is correct and non-vacuous (32 ≥ 30), and re-baselining a threshold to agree with a corrected count is the antipattern; `tests/test_classification_word_boundary.py` is byte-unchanged. ⛔ **No `argus/**` byte moved** — sha256 still `37c82e39003a…`. Gates re-run and **all unmoved**: 1362 tests / **exactly one failure** (`DF-11-1-A`, carved out by node id — no second red) / 0 errors / 0 skipped; `mypy` clean 72; `bandit` 0H/0M/19L; `git ls-files -- argus` **72** with four ` M` and no `A`; dogfood unit 2 **14 900** = 33 of 133 with all three `partition_id`s byte-unchanged; `argus audit .` field-for-field identical, exit 0. All figures **LOCAL** (Windows/CPython 3.11.15); CI **NOT ESTABLISHED**; nothing pushed, tagged or dispatched. Status → `review`. | Developer (bmad-dev-story, mode `fix`) |
| 2026-08-11 | 1.0 | **Implemented; `DF-8-2-B` CLOSED.** Three separator-less entries removed from the two classification tables; Java's boundary added as a CASE-SENSITIVE tier-2 rule against the original-case basename (DN-1) and `conftest.py` as a whole-BASENAME tier-3 rule (DN-2) — **33 physical lines in the one existing `argus/detectors/vacuous_test.py`**, zero new `argus/**` files, zero existing test assertions changed. RED-first run **twice** with the final test code (E.1): against the unfixed tree, where AC3's closure named **exactly three** offenders and the vacuous-critical-set false green reproduced end-to-end; and again with the defective entries restored into the final module structure, after which the file's `sha256` round-tripped byte-identically (`37c82e39003a`). AC3 shipped as three closures over both tables **and** the grounded language set; AC4's AC7 invariant re-proven behaviourally over an 8-file polyglot fixture **and** structurally by an `ast` walk pinning `pipeline.py`'s two construction sites; AC5 pins `latest.java` CRITICAL + eligible + deep with a non-empty critical set, and `myspec.rb`'s reason moved from the false `test_file` to the true `zero_definition_module`. LOCAL gates (Windows/3.11.15, **no CI covers this tree**): 1362 tests = 1352 + exactly 10 new, 0 skipped, **exactly one failure — `DF-11-1-A`, carved out by node id and NOT closed**; `mypy` clean 72; `bandit` 0H/0M/19L; coverage 95.82%. Dogfood unit 2 14 867 → **14 900 = 33 of 133**, all three `partition_id`s byte-unchanged, no artifact regenerated. `argus audit .` unchanged field-by-field; `deep_ratio`/`held_out` +1 each, explained arithmetically (166 − 89 = 77). False negatives **filed** as `DF-11-2-A`/`DF-11-2-B` with owners, not fixed. CI evidence **NOT ESTABLISHED**; nothing pushed, tagged or dispatched. One recorded write-set deviation (Note 7). Status → `review`. | Developer (bmad-dev-story) |
| 2026-08-11 | 0.1 | Story contexted from `epics.md` Epic 11 / Story 11.2 + `DF-8-2-B`. All premises re-measured on this tree (AI-E10-3): the separator-less entry count is **three**, not two; `DF-8-2-B`'s *"not a false green"* premise **expired** when Java gained a grammar; the fix's shape is decided by Java's CamelCase boundary and by `conftest.py`. Candidate fix validated by a reversible, `sha256`-round-tripped experiment (full suite green bar `DF-11-1-A`; +7 LOC; partition ids unchanged). Status → `ready-for-dev`. | Scrum Master (bmad-create-story) |
