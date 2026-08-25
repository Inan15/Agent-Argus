---
baseline_commit: 024d330
---

# Story 17.3: Grade what the assertion constrains

Status: review

<!-- Contexted 2026-08-25 at HEAD `024d330` (branch `docs/merge-strategy-decision`) by the
     create-story workflow (Opus 5).

     THE WORKING TREE IS CLEAN AT CONTEXTING (`git status --porcelain` empty). Unlike 17.2's
     contexting, the peer session's staged artifacts have landed: `024d330` is 17.2's review
     close-out. `origin/master` is `c2ce00f` and this branch is **8 ahead**.

     EVERY FIGURE IN SECTION 0 WAS READ OFF THIS TREE BY EXECUTION at `024d330`, not copied
     from `epics.md`, from `deferred-work.md`, from the 2026-08-24 research or from 17.2's
     story record. The vocabularies were IMPORTED and sized; the `-127` fence's own closure
     was re-walked; `DF-AUD-DETECT-D`'s divergence was RE-MEASURED with both implementations
     over the live tree; the five pinned corpus shas were probed with `git cat-file -e`; the
     1,032 was re-counted out of `adjudication-set-13-5.json`; every module's line count was
     re-derived from the git index.

     ⛔ THIS IS THE FIRST STORY OF EPIC 17 THAT WRITES `argus/**` BYTES. 17.1 shipped a
     frozen `scripts/` module; 17.2 shipped a document, three guards and one ledger note.
     17.3 spends ALL FOUR of the costs `DN-17-1-1` counted (§2.1), and it is the story the
     epic's two hardest traps were handed to.

     SIX PREMISES MOVED AGAINST WHAT `epics.md` ASSUMES, and each is load-bearing:

       (1) §0.4 — ⛔ **EVERY ONE OF THE NINE `RESULT_OBSERVING_CONTEXT_CALLEES` IS IN THE WIDE
           ASSERTION TABLE**, and only 2 of the 9 are in the FROZEN one. So a fail-closed test
           — `with pytest.raises(ValueError): parse(bad)` — DOES carry an assertion under the
           vocabulary (c′) must read, and a grader that scores it by *"what do this assertion
           call's arguments reference"* grades it at the WEAKEST band and hands `S1` a FALSE
           ACCUSATION on every fail-closed test in the corpus. **This is the single most
           expensive defect this story can ship** and `DN-3` already refused it once, one level
           down, in fact (b). AC2.4 and `TC-ArgusAgent-DETECT-001-149` exist for it alone.

       (2) §0.5 — ⛔ **ONLY THE BAND-0 BOUNDARY CARRIES VERDICT WEIGHT.** `S1`'s threshold is
           *EVERY assertion at the weakest band*, so grading something as `existence` or
           `value` REFUSES `S1`; only grading it `none` admits. The whole moat therefore sits
           on one boundary, and the conservative default is one sentence: ⛔ **when in doubt,
           NOT the weakest band.** The `existence`/`value` split carries **no** verdict weight
           in Epic 17 — it is 17.4's reporting axis and the thing 17.2 pre-refused widening
           into. Do not over-engineer it; do not let it eat the story.

       (3) §0.6 — ⛔ **`DF-AUD-DETECT-D` REPRODUCES AT HEAD AND ITS FIGURES HAVE MOVED**:
           re-measured here with both implementations over the live tree, **1,890 divergences
           of 31,845 statements across 232 files (5.93%)** against the entry's recorded
           1,844 / 30,941 / 228 (5.96%). The entry is TRUE, its numbers are STALE, and the
           story must re-derive rather than quote (`AI-E9-7`).

       (4) §0.7 — ⛔ **THE RESEARCH HARNESS'S `V5` RESOLVER IS NOT PORTABLE TO SHIPPED CODE.**
           `research/investigate-per-call-scoping.py::sut_unrelated_assertions` is built on
           CPython `ast.walk` over a re-parsed function body. The epic's own AC forbids that
           here — *"grading reads the source text and the index and nothing else — no re-parse,
           no second grammar call"*. So the resolver is not a port; it is a **new derivation in
           the `provenance_scan` idiom**, and `_mock_bound_names` is its working mirror image.

       (5) §0.8 — ⛔ **NFR-M1 HEADROOM IS THE REAL CONSTRAINT ON WHERE THIS CODE LANDS.**
           `provenance_scan.py` is at **976 / 1200** (224 free) and `vacuous_test.py` at
           **807 / 1200** (393 free), against a repository whose docstring density has put
           `DF-16-5-A` on the ledger at 68 lines of headroom. §1.2 takes the placement decision
           and §0.8 pre-registers the split trigger BEFORE a line is written, on Story 16.5's
           §0.5 precedent, so a split is never discovered at review.

       (6) §0.9 — ⛔ **ALL FIVE PINNED CORPUS SHAS ARE REACHABLE** (`git cat-file -e` on each,
           at the five checkout paths), and the 1,032 re-counts exactly out of
           `adjudication-set-13-5.json` — `minions` 648 · `agent-smith` 295 · `agent-markovich`
           72 · `xagents-webapp` 17 · `ai-body-runtime` 0. So the epic's *"re-run the
           1,032-finding harness and diff"* is RUNNABLE. ⛔ **It is runnable LOCALLY ONLY** —
           CI has no third-party checkouts — so it is a RECORDED MEASUREMENT with its command,
           never a committed test (a test that needs the checkouts reds every CI run).

     ⛔ NOTHING HERE RATIFIES A MEMBER, FETCHES A THIRD-PARTY SOURCE, ADJUDICATES A ROW, SPENDS
     `DF-13-5-A`'s ROUND, PUBLISHES A REACH FIGURE FOR `S1`, OR MAKES ANY FINDING
     VERDICT-ELIGIBLE. `scripts/precision_preregistration.py` stays FROZEN and
     `successor-vacuity-predicate-specification.md` is CITED, never re-specified. -->

## Story

As the **Engineering Lead**,
I want **each assertion in a flagged test graded on whether — and how strongly — it constrains a value derived from the code under test, and the successor predicate `S1` landed as code on top of that grading**,
so that **a test which runs the SUT and tolerates any result is distinguishable from one that checks it — and so that 17.4 has a shipped predicate to measure instead of a research script's own reasoning.**

### What this story IS

Story 17.1 froze the criterion. Story 17.2 wrote the specification and argued `S1` as a
genuinely different predicate. **This story builds what 17.2 specified.** Both prior stories
say so in terms: the specification's own header records *"⛔ **Predicate as code — DOES NOT
EXIST YET. Story 17.3 builds it.**"*, and §4.3 records *"The `V5` band's resolver does not
exist in `argus/`. Story 17.3 must build it. That is the single largest piece of unbuilt work
in Epic 17."*

It lands **five things and nothing else**:

1. **A committed assertion-strength SCALE** — a closed, ordered, named vocabulary with at
   minimum the three bands the epic names (*does not reference an SUT-derived value* /
   *constrains only its existence or type* / *constrains its value*), each carrying its
   meaning, refusing an unregistered member in the `DF-10-4-E` shape.
2. **A PURE grader and an SUT-derived-name resolver inside `argus/`** — reading the source
   lines and the Story 1.4 index and nothing else. No re-parse, no second grammar call, no
   clock/uuid/random.
3. **`S1` as code**, exactly as `successor-vacuity-predicate-specification.md` §2.1 defines
   it: (a) reachability UNCHANGED · (b′) `discarded_sut_calls >= 1` UNCHANGED · (c′) every
   assertion in the span at the weakest band, including the empty-assertion span. ⛔ **Landed
   ADVISORY: no finding's verdict-eligibility moves** (specification §6.5).
4. **The `DF-AUD-DETECT-D` collapse** — `_logical_statement_end` and `_scan_span` become ONE
   derivation, **before** grading is layered on it, proven output-neutral by re-running the
   1,032-finding harness and diffing byte-for-byte.
5. **The span-scan cost record**, before and after, so a regression is disclosed rather than
   discovered later.

Plus, because they are the price of an `argus/**` byte: the guard module, the dogfood-artifact
regeneration, the `Evidence-partition:` trailer on every commit touching `argus/detectors/**`,
this story's record and the `sprint-status.yaml` transitions.

### What it is NOT

- ⛔ **NOT a re-specification.** `successor-vacuity-predicate-specification.md` is the
  contract; this story implements it. If the code and the document disagree, **the document
  wins and the code is wrong** — unless the document is falsified by measurement, which is an
  **escalation** (AC10), never a quiet edit. ⛔ **The document is not rewritten by this story**
  (§3.4 evidence immutability).
- ⛔ **NOT a promotion, and not a proposal to promote.** `S1` gates nothing. ⛔ **No finding's
  `verdict_eligible` flips**, `_ast_corroborated`'s return expression is **byte-unchanged**,
  the externalization gate stays `BLOCKED`, `protocol_cleared` stays `False`, the ≥80%
  keystone stays **NOT CLEARED** and FR34's disclosure stands. Specification §6.5: *"17.3 must
  land `S1` such that no finding's `verdict_eligible` flips on it within Epic 17."*
- ⛔ **NOT a loosening of `consumed == 0`.** The clause is not deleted from, weakened in,
  widened within or re-scoped in the shipped predicate. `S1` is a **second, additional**
  predicate computed beside fact (b); fact (b) keeps its own arithmetic unchanged.
- ⛔ **NOT a measurement of `S1`'s reach.** ⛔ **No number for `S1`'s population is written in
  any committed artifact of this story** — not `36`, not `125`, not `161`, not a new one.
  17.2 refused to publish it (`DN-17-2-4`) and **17.4 measures it, once**, against a criterion
  frozen before any of this existed. The 1,032-harness run this story DOES perform is a
  **neutrality diff of a refactor**, and its output is *"byte-identical / not byte-identical"*.
- ⛔ **NOT a tuning of 17.1's criterion.** `scripts/precision_preregistration.py` is **FROZEN**
  and is **not in the write set**; `TC-ArgusAgent-PRECISION-001-140` must stay green and
  unedited.
- ⛔ **NOT a widening of the threshold.** `S1` requires **EVERY** assertion at the weakest
  band. Admitting the *existence or type* band **is a separate, future act requiring its own
  pre-registration** (specification §2.2). ⛔ **It is not a tuning knob and this story does not
  turn it.**
- ⛔ **NOT a unification of the two assertion tables.** `DN-14-2-1` holds: the FROZEN
  corroboration table answers *"does this corroborate the SUT result"*; the WIDE table answers
  *"does this assert anything at all"*. Two questions, opposite harm directions, two tables
  (§1.5).
- ⛔ **NOT a performance story.** `DF-AUD-DETECT-C` stays **OPEN and UNDISPOSITIONED**. The
  cost record is a disclosure, not an optimisation mandate, and ⛔ **no timing threshold enters
  the test suite** (§1.6).
- ⛔ **NOT a ledger sweep.** **Exactly ONE** entry is written: `DF-AUD-DETECT-D`.
  ⛔ `DF-INV-VACUOUS-A`, `DF-16-7-A`, `DF-16-7-B`, `DF-14-1-A`, `DF-12-2-D`, `DF-12-3-A` and
  every other `DF-AUD-DETECT-*` stay **untouched** — the six re-homings and the four Epic-18
  scheduling notes are **Story 17.5's**, by name (`DN-17-1-9`).
- ⛔ **NOT a spend of `DF-13-5-A`.** No member ratified, no third-party source fetched, no
  round consumed, branch (a) not executed, branch (b) not declared. Its 2026-08-24 trigger is
  **17.4's** to evaluate.
- ⛔ **NOT an FR10 evidence-plumbing repair.** `Recording` has no evidence field and
  `DN-18-4-6` recorded that widening one detector in isolation is the wrong shape of repair.
  The grading counts live on the detector's own score object and **reach no `.argus/`-bound
  output** (§1.4).
- ⛔ **NOT a reopening of Epics 1–16 or 18, of Story 6.2, or of any signed retrospective.**

---

## §0 — PREMISES MEASURED BY EXECUTION at HEAD `024d330`

⛔ **Task 0 re-derives every row below before a line is written.** Every figure here is cheap
to reproduce and none requires running a detector over a corpus member. **A row that does not
reproduce is an escalation (AC10), not a number to adjust.**

### §0.0 The tree, the paths, the baseline

| fact | value |
|---|---|
| HEAD | `024d33089a1ff25f22c8eae7db9e30b5aa1f6d3e` (`024d330`) |
| branch | `docs/merge-strategy-decision`, **8 ahead of `origin/master` (`c2ce00f`)** |
| `git status --porcelain` | **EMPTY** — clean at contexting |
| 17.2's arc | `5999624` chore → `126f502` docs (specification + guards) → `579a342` docs (ledger + record) → `024d330` docs (review close) |
| artifact root | `_bmad-output/design-artifacts/ArgusAgent/` |
| story location | `…/stories/` (`sprint-status.yaml:6`) |
| next free `DETECT-001` id | **`-147`** (`-146` is Story 18.4's); this story allocates `-147`..`-153` |
| next free `PRECISION-001` id | **`-145`** (`-142`..`-144` are Story 17.2's); this story allocates `-145`..`-146` |
| CI gates | `mypy argus` · `bandit -r argus --severity-level medium` · `pytest --cov=argus --cov-fail-under=80` (`.github/workflows/audit-ci.yml`) — matrix **ubuntu-latest × 3.10/3.11/3.12**, triggers on `master`/`main` only, `fetch-depth: 0` |
| NFR-M1 | ≤1200 physical lines, population `git ls-files -- '*.py'`, swept by `tests/test_module_size_ceiling.py` over the **INDEX** (a file is swept the moment it is `git add`-ed) |
| `deferred-work.md` byte invariants | **593,897 bytes · exactly 1 CR byte · 7,534 LF · 0 CRLF.** ⛔ Edit in **binary** mode; a text-mode round-trip eats the lone CR. |
| `sprint-status.yaml` byte invariants | **1,264 lines · 1,264 CR bytes.** Both identical after every edit. |
| `last_updated` | already `2026-08-25` at `sprint-status.yaml:236` — ⛔ **do not touch it unless the date changes** |

### §0.1 What is FROZEN coming in, and what may not move

| frozen thing | where | what it means here |
|---|---|---|
| `scripts/precision_preregistration.py` | pinned at `PREREGISTRATION_COMMIT_SHA = f906d04…` | ⛔ **not in the write set.** `TC-ArgusAgent-PRECISION-001-140` enforces the strengthening-only asymmetry directionally; it must stay green **and unedited**. |
| `SUCCESSOR_OUTPUT_PATHS` | `precision_preregistration.py` — two prefixes, **both ABSENT on disk** | ⛔ This story creates neither and writes nothing under either. That absence is what makes 17.4's ancestry guard provable. |
| `_CORROBORATION_ASSERTION_CALLEES` | `argus/detectors/vacuous_vocabulary.py`, **23 names** | FROZEN at Story 14.1's set. ⛔ Not widened, not narrowed, not read for the *"asserts anything"* question. |
| `successor-vacuity-predicate-specification.md` | 2026-08-25, Story 17.2 | The contract `S1` must satisfy. ⛔ **Cited, never rewritten** (§3.4). |
| `precision-validation-protocol.md` | `PROTOCOL_VERSION` V1.3 | ⛔ Byte-unchanged. No §5 condition created, no terminal state invented. |
| the 31 adjudicated rows + `silent-class-record.json` | `validation-corpus/` | ⛔ Byte-unchanged. **No row is adjudicated by this story** (protocol §2: the TP/FP/BORDERLINE judgement is an operator act). |

### §0.2 The shipped predicate, read at HEAD — and the ONE line that must not move

`argus/detectors/vacuous_test.py:754`–`:796`, `VacuousTestDetector._ast_corroborated`:

- **fact (a), reachability** — `len(self._sut_call_sites(span_edges)) >= 1`, where
  `_sut_call_sites` (`:737`–`:752`) filters the span edges against the **FROZEN** table and
  `_MOCK_CALLEES`.
- **fact (b), vacuity** — `evidence.sut_result_is_discarded and evidence.mock_referencing_assertions >= 1`
  (`:796`), where `evidence = provenance_evidence(..., assertion_callees=_CORROBORATION_ASSERTION_CALLEES, mock_callees=_MOCK_CALLEES)`
  and `sut_result_is_discarded` is `discarded_sut_calls >= 1 and consumed_sut_calls == 0`
  (`provenance_scan.py:843`–`:846`).

⛔ **`vacuous_test.py:796` IS THE ONE LINE THIS STORY MAY NOT CHANGE.** It is the only
verdict-eligibility decision in the whole rule class, and `TC-ArgusAgent-PRECISION-001-146`
compares it **as an AST expression**, not as a string, so a reformat is allowed and a
semantic change is not.

The three vocabularies, **sized by import at HEAD**:

| table | size | question it answers | direction of harm if widened |
|---|---:|---|---|
| `_CORROBORATION_ASSERTION_CALLEES` **FROZEN** | **23** | *"does this span corroborate the SUT result?"* — facts (a) and (b) | widening moves a test **towards** an accusation |
| `_ASSERTION_CALLEES` **WIDE** + `\A_?assert\w*\Z` | **89** + convention | *"does this span assert anything at all?"* — (c′)'s population | **narrowing** would score an asserting test as silent — harm **REVERSED** |
| `_MOCK_CALLEES` | **10** | mock recognition on both paths | — |
| `RESULT_OBSERVING_CONTEXT_CALLEES` | **9** | *"is raising / warning / logging the observation?"* (`DN-3`) | see §0.4 |

### §0.3 ⛔ `TC-ArgusAgent-PRECISION-001-127` FENCES `argus/detectors/**` OUT OF `silent_class.py`

Re-walked at HEAD: `tests/test_silent_class.py:525` parses **every** `argus/**` module
(**95** today), resolves the import graph **transitively**, and asserts that nothing in the
fenced set reaches `argus/precision/silent_class.py`.

```
fenced = argus/detectors/**  ∪  argus/precision/gate_*.py
         ∪ {adjudication.py, replay_harness.py, argus/precision/__init__.py}      → 20 today
non-vacuity asserted FIRST: ≥60 modules parsed, ≥12 fenced, the target's own
                            known outbound edge (adjudication.py) resolved
```

⛔ **THE CONSEQUENCE, AND IT IS THIS STORY'S SINGLE MOST EXPENSIVE STRUCTURAL TRAP** — 17.2
handed it over by name: **the `S1` scorer cannot be assembled by importing `silent_class` from
the detector package. One import line turns `-127` RED**, and ⛔ **the correct response is
NEVER to widen the fence** (`DF-8-5-B`: a guard is never weakened to go green).

⛔ **The direction that IS legal is the one that already exists**: `silent_class` imports
`provenance_evidence`, `body_statement_count`, `opens_bare_assert` and `is_assertion_callee`
**from the detector package**, one way. So everything `S1` needs is already on the detector
side of the fence, and the new code goes there too — which also leaves `silent_class` free to
compose the new grader later, still one-way, without touching `-127`. Adding
`argus/detectors/assertion_strength.py` moves the walk to **96 modules / 21 fenced**, both
above their floors.

### §0.4 ⛔ THE FAIL-CLOSED-TEST TRAP — measured, and it is the defect this story most likely ships

**Measured at HEAD by import.** All **nine** `RESULT_OBSERVING_CONTEXT_CALLEES` are members of
the **WIDE** assertion table and all nine satisfy `is_assertion_callee`; only **two** —
`assertRaises`, `assertRaisesRegex` — are in the FROZEN table:

| callee | in WIDE | in FROZEN |
|---|---|---|
| `raises`, `warns`, `deprecated_call`, `assertWarns`, `assertWarnsRegex`, `assertLogs`, `assertNoLogs` | ✅ | ❌ |
| `assertRaises`, `assertRaisesRegex` | ✅ | ✅ |

⛔ **THEREFORE**: a fail-closed test —

```python
def test_rejects_bad_input():
    with pytest.raises(ValueError):
        parse("nonsense")          # the SUT call, and its result IS discarded
```

— **carries an assertion under the vocabulary (c′) must read**, and a grader that scores an
assertion by *"what do this call's arguments reference"* sees `raises(ValueError)`, finds no
SUT-derived name in the arguments, grades it at the **weakest band**, and `S1` corroborates.
That is a **false accusation on every fail-closed test in the corpus** — a shape the ratified
corpus is full of, and precisely the class `DN-3` refused once already, one level down, when
it made a SUT call inside such a block **CONSUMED by construction** (`provenance_scan.py:112`–
`:131`, `_result_observing_lines` at `:760`).

⛔ **THE RULE, AND IT IS NOT NEGOTIABLE (AC2.4):** an assertion that is a
`RESULT_OBSERVING_CONTEXT_CALLEES` call whose block covers a SUT call grades at the
**STRONGEST** band — *raising IS the observation*. `_result_observing_lines` already computes
the covered line set; ⛔ **read it, do not re-derive it.**

⚠️ **Fact (b) does NOT protect you here.** `S1` deliberately drops `consumed == 0`, which is
the clause that made `DN-3`'s CONSUMED verdict bite. Under `S1` a fail-closed test can carry
`discarded_sut_calls >= 1` from a second, genuinely discarded call and still reach (c′). **The
protection has to be rebuilt at the band level, in this story, or it does not exist.**

### §0.5 ⛔ ONLY THE BAND-0 BOUNDARY CARRIES VERDICT WEIGHT

`S1`'s threshold is *EVERY assertion at the weakest band* (specification §2.2). So:

| grading a real constraint as… | effect on `S1` | direction |
|---|---|---|
| **`none`** (weakest) when it is not | `S1` **ADMITS** the span | ⛔ **towards an accusation — the lethal direction** |
| `existence` or `value` when it is `none` | `S1` **REFUSES** the span | under-claiming — the safe direction |

⛔ **THE CONSERVATIVE DEFAULT, IN ONE SENTENCE: when in doubt, NOT the weakest band.** That is
cross-cutting concern #6's moat restated at the band level, and it is the whole safety story.

⚠️ **A consequence worth taking, because it stops this story sprawling:** the
`existence` ↔ `value` boundary carries **no verdict weight in Epic 17**. It is 17.4's
reporting axis and it is the boundary 17.2 **pre-refused** widening `S1` into. So it must be
**stated, committed and testable** (AC1), and it does **not** need to be exhaustive over every
assertion idiom in Python. ⛔ **Do not spend this story building a complete assertion
taxonomy.**

### §0.6 ⛔ `DF-AUD-DETECT-D` REPRODUCES AT HEAD, AND ITS FIGURES HAVE MOVED

Re-measured here by running **both** implementations over every logical statement of every
tracked `argus/**` + `tests/**` Python file at `024d330`:

| source | files | statements | divergences | rate |
|---|---:|---:|---:|---:|
| `deferred-work.md` entry (2026-08-24) | 228 | 30,941 | 1,844 | 5.96% |
| **re-measured at `024d330`** | **232** | **31,845** | **1,890** | **5.93%** |

**Reproduce** (pure, no corpus, ~2 s):

```python
from argus.detectors import provenance_scan as ps
from argus.detectors.vacuous_test import index_aligned_lines
lines = index_aligned_lines(pathlib.Path(f).read_text(encoding="utf-8"))
ends  = {sl.opens: sl.line_no for sl in ps._scan_span(lines, 1, len(lines)) if sl.opens is not None}
#          ↑ last line whose `opens == s`, because _scan_span is walked in order
diverge = [s for s, e in ends.items() if ps._logical_statement_end(lines, s, len(lines)) != e]
```

**The mechanism, confirmed by reading both functions at HEAD:** `_scan_span` (`:377`) tracks
brackets **and** backslash **and** an open triple-quoted literal, threading `pending` through
`_continued_code_prefix`. `_logical_statement_end` (`:345`) calls `_code_prefix`, which hard-codes
`pending=None` (`:253`) and therefore **cannot carry the cross-line string state**. Every
sampled divergence is a multi-line docstring: the old function returns the OPENING line where
the scan spans the whole literal.

⛔ **THE ENTRY'S OWN SUGGESTED REPAIR IS A DELETION, NOT AN ADDITION**, and it is quoted here
because the dev must not invent a third thing: *"the end of the statement opening at `s` is the
last line whose `opens == s` in the `_scan_span` result, which inherits the string state
instead of restating the rule."*

**The blast radius is exactly two call sites**, both inside `provenance_evidence`:
`provenance_scan.py:941` (the SUT-call statement extent) and `:971` (the assertion statement
extent). ⛔ **Both are on the corroboration path**, which is why the epic requires the collapse
to be proven output-neutral before any grading is layered on it.

⚠️ **The entry is filed 🟢 and explicitly NOT as a correctness defect.** Its own words: *"It is
NOT filed as a correctness defect and must not be quoted as one."* Its stages (ii) and (iii)
— 1,543 test functions re-scored with the `_scan_span` extent, **0 evidence differences and 0
corroboration flips**, and a purpose-built synthetic trigger that produced **identical**
`ProvenanceEvidence` — are what make the collapse safe to take **first**. ⛔ Re-derive them;
do not quote them (AC4.2).

### §0.7 ⛔ THE SUT-DERIVED-NAME RESOLVER DOES NOT EXIST, AND THE RESEARCH VERSION IS NOT PORTABLE

`research/investigate-per-call-scoping.py::sut_unrelated_assertions` (`:79`–`:137`) is the only
existing implementation of *"does this assertion reference a name bound from a SUT call"*. It is
built on `ast.walk` over a re-parsed function body, and the harness says so in its own docstring:
*"V5 additionally needs SUT-derived name binding, **which no shipped helper provides**; it is
computed with Python `ast` and is therefore THIS SCRIPT'S OWN reasoning, not the shipped
predicate."*

⛔ **IT CANNOT BE PORTED.** The epic's own AC forbids it — *"grading reads the source text and
the index and nothing else — no re-parse, no second grammar call"* — and `AR8`/`NFR-D2` are the
standing reasons: the detector runs over an index the pipeline already built, and a second
parse is a second grammar with its own failure modes.

⛔ **BUT ITS MIRROR IMAGE ALREADY SHIPS, AND IT IS THE TEMPLATE.**
`provenance_scan._mock_bound_names` (`:794`–`:829`) answers the identical question for mocks,
name-level, over source lines, in one forward pass in source order, using `_ASSIGNMENT_RE`,
`_AS_BINDING_RE`, `_leading_chain` and `_is_mock_derived`. ⛔ **The SUT-derived resolver is that
function's sibling and must be built in that idiom** — one forward pass, transitive
(`r = sut(); doubled = r * 2` binds both), `with … as name` handled, and everything it cannot
read left **unbound** (which pushes away from the weakest band, i.e. away from an accusation).

### §0.8 ⛔ NFR-M1 HEADROOM, AND THE SPLIT TRIGGER PRE-REGISTERED BEFORE A LINE IS WRITTEN

Measured from the git index at HEAD:

| module | lines | headroom to 1200 |
|---|---:|---:|
| `argus/detectors/provenance_scan.py` | **976** | 224 |
| `argus/detectors/vacuous_test.py` | **807** | 393 |
| `argus/detectors/vacuous_vocabulary.py` | 534 | 666 |
| `argus/precision/silent_class.py` | 944 | 256 |
| `tests/test_vacuous_density.py` | **1,159** | **41** |
| `tests/test_vacuous_detector_index.py` | 1,065 | 135 |
| `tests/test_vacuous_cross_language.py` | 1,033 | 167 |
| `tests/test_vacuous_detector.py` | 791 | 409 |
| `tests/test_silent_class.py` | 698 | 502 |

⛔ **`tests/test_vacuous_density.py` HAS 41 LINES OF HEADROOM.** It is the natural-looking home
for a statement-boundary guard and it is **not available**. New guards go in a **new module**
(§1.2). Adding to it is how the last five stories each inherited an unfiled split-first trigger
at the worst moment (`DF-15-2-D`, `-E`, `DF-16-3-A`, `DF-16-5-A`).

⛔ **PRE-REGISTERED SPLIT TRIGGER (Story 16.5 §0.5's shape, set here BEFORE any code):** at
Task 1, project each touched module's final line count. **Split first** if any projection
exceeds **1,150**; **file a `deferred-work.md` entry** if it lands between **1,100 and 1,150**;
below 1,100 do neither. ⛔ **`_EXEMPT_BY_DESIGN` is not an option** — the registry is a
shrinking allow-list and an entry added here would be the first source-module entry ever.

### §0.9 The corpus, the harness, and the 1,032 — RUNNABLE, and locally only

**Re-counted at HEAD** out of `validation-corpus/adjudication-set-13-5.json` (4,284 findings
total across five rule classes):

| member | pinned sha | `vacuous_test_heuristic` findings | pin reachable? |
|---|---|---:|---|
| `minions` | `ec63b7293b70…` | **648** | ✅ `git cat-file -e` |
| `agent-smith` | `9ab774d7bf5d…` | **295** | ✅ |
| `agent-markovich` | `a561668636d8…` | **72** | ✅ |
| `xagents-webapp` | `33a86525a498…` | **17** | ✅ |
| `ai-body-runtime` | `4480ffdeb4c5…` | **0** | ✅ |
| **total** | | **1,032** | 5 of 5 |

All five checkout directories exist, and **all five pinned shas resolve in their checkouts** —
including `agent-smith` at the depth-5 path `D:/…/XAgents/XAgents/XAgents/Agent-Smith`.

⛔ **THE HARNESS IS `scripts/build_silent_class_record.py --check --checkout-root <root>`.** It
reads every byte from the **git OBJECT DATABASE at the pinned commit** through `pinned_tree` /
`materialize_pinned_bytes` / `verify_pinned_bytes`, re-hashes each blob with git's own identity,
and routes every git call through `read_only_git`, whose allow-list excludes `checkout`,
`stash`, `clean`, `reset`, `worktree`, `add`, `commit`, `fetch` and `pull`. **A member's working
tree cannot reach the measurement**, so a drifted or dirty checkout is not a hazard here (13.5's
lesson, already mechanised).

⛔ **IT IS A LOCAL, RECORDED MEASUREMENT — NEVER A COMMITTED TEST.** A clean CI machine has no
third-party checkouts; `--check` without `--checkout-root` deliberately prints its own
limitation rather than implying a measurement it never made. ⛔ **Do not add a test that needs
the checkouts** — it would red every CI run, which is the `DF-16-6-F` / `AI-E13-1` class.

⛔ **AND IT RATIFIES NOTHING.** Running it produces no adjudication, no successor output, no
new member and no reach figure. Its answer to this story is one bit: *byte-identical, or not*.

### §0.10 The detector surface, the trailer, and the artifacts an `argus/**` byte moves

| obligation | measured at HEAD | bearing on 17.3 |
|---|---|---|
| `Detector` Protocol — `rule_id -> str` + `run -> Callable[..., DetectorResult]`, read-only properties, `@runtime_checkable` **deliberately absent** | `argus/detectors/base.py:147`–`:190` | ⛔ **No Epic-17 guard may decide conformance by `isinstance`/`issubclass`** |
| `TC-ArgusAgent-DETECT-001-145` — every class defining `run() -> DetectorResult` carries an `if TYPE_CHECKING:` pin **inside `argus/`** | `tests/test_detector_base.py:224`; **four** pins today | ⛔ Goes RED the moment a fifth such class is written. §1.2 decides: **this story adds no detector class**, so it stays green — and if that decision is reversed, the pin lands in the same commit. |
| `TC-ArgusAgent-DETECT-001-146` — the Protocol's shape is a FENCE | `tests/test_detector_base.py:257` | ⛔ `base.py` is not edited |
| `Evidence-partition:` trailer over `DETECTOR_TUNING_PATHS = ("argus/detectors", "argus/precision/replay_harness.py")` | `argus/precision/gate_seal.py:280`; enforced over **real post-seal history** by `TC-ArgusAgent-PRECISION-001-94`'s tail loop | ⛔ **EVERY commit touching `argus/detectors/**` needs it.** 18.1 lost a sha to a forgotten one. §1.7 decides the value. |
| dogfood-artifact currency — *"CURRENT iff the cited provenance sha is an ancestor of HEAD **and** `git diff <sha> HEAD -- argus/` is empty"* | `tests/test_dogfood_artifact_currency.py` (`-49`..`-52`) | ⛔ **Any `argus/**` byte forces `python scripts/regenerate_dogfood_artifacts.py` and its OWN commit** |
| `--cov=argus --cov-fail-under=80` | `audit-ci.yml`; 95.69% at the 17.2 round | a new `argus/` module drags it |
| `mypy argus` (95 files) · `bandit -r argus --severity-level medium` | blocking | over a module that ships in the wheel |

### §0.11 What is already true and must NOT be re-done

- ⛔ **Do not register anything in `_STATUS_DOCUMENTS`.** `TC-ArgusAgent-DOCS-001-22` closes in
  **both** directions and its globs are `sprint-change-proposal-*.md` and `epic-*-retro-*.md`;
  a story file matches neither and registering one turns `-22` RED (`DN-17-1-8`).
- ⛔ **`TC-ArgusAgent-DOCS-001-78` is the ledger cross-check and it is already AC7's guard.** It
  extracts every `DF-*` a story file claims to have CLOSED (line-scoped, closure-verb anchored,
  negation-aware) and requires a matching disposition in `deferred-work.md`. ⛔ **Do not write a
  second, id-scoped copy** — that is an `AR7` fork of a working guard (`DN-17-2-9`'s precedent).
- Guard-RED observations are recorded **automatically** by `tests/conftest.py` into
  `.argus/guard-fires.jsonl` (gitignored). ⛔ **Do not hand-write a fires ledger.**
- The **ruling index** (`architecture.md:1150`) does not exist as a document. ⛔ Do not create
  it; `DN-17-3-*` rulings live in this story record.
- `scripts/check_meta_drift.py` is **advisory** — not in CI, not in `tests/`.
- ⛔ **`argus/detectors/__init__.py` is a docstring-only shell with `__all__: list[str] = []`
  and it says in terms *"do NOT add them here"*.** A new module is imported by path, not
  re-exported.

---

## §1 — THE DECISIONS THIS STORY MAKES, AND WHY

### §1.1 The scale — three bands, closed, ordered, and each carrying its meaning

The epic requires *"a stated, committed scale — at minimum *does not reference an SUT-derived
value* / *constrains only its existence or type* / *constrains its value*"*. This story commits
**exactly those three**, in that order, as a closed vocabulary in the house form
(`gate_seal.PARTITION_VALUES` / `silent_class.IDIOMS` / `adjudication.DISPOSITIONS`):

| band | ordinal | meaning | admits `S1`? |
|---|---:|---|---|
| `none` | 0 | the assertion does not reference a value derived from the code under test | ✅ (weakest) |
| `existence` | 1 | it constrains only that the value exists, is truthy, or has a type | ❌ |
| `value` | 2 | it constrains what the value **is** | ❌ |

Plus **one condition that is NOT a band**:

- **`unestablished`** — the assertion's statement could not be read, its extent could not be
  resolved, or the scale cannot assign it. ⛔ **It is a recorded condition (`NFR-R1`), not a
  fourth band**, it is carried as its own count, and **`S1` refuses any span with
  `unestablished >= 1`**. Specification §6.3 already states this as part of (c′) — *"a grading
  the scale cannot assign … the answer is NOT corroborated"* — so it is **not** a fourth
  conjunct and **not** a re-specification.

⛔ **An unregistered band raises** (`UnregisteredStrength(ValueError)`, the `DF-10-4-E` shape
`silent_class.UnregisteredIdiom` and `gate_seal.UnregisteredPartition` already use). ⛔ **Never
defaulted, never tolerated.**

### §1.2 Where the code lives — and what is NOT created

| thing | lands in | why |
|---|---|---|
| the scale, the SUT-derived-name resolver, the per-assertion grader, and `S1` | **NEW `argus/detectors/assertion_strength.py`** | on the **detector side** of the `-127` fence (§0.3), so `S1` is reachable by the detector **and** later composable one-way by `silent_class`; and `provenance_scan.py` has only 224 lines of headroom (§0.8) |
| the statement-extent **projection** that replaces `_logical_statement_end` | `argus/detectors/provenance_scan.py` | it is a deletion plus a projection of `_scan_span`, which lives there (`DF-AUD-DETECT-D`'s own instruction) |
| the SUT-call classification both fact (b) and the grader read | `argus/detectors/provenance_scan.py` | fact (b) already computes it and throws it away (§1.3) |
| the grading counts on the detector's score | `argus/detectors/vacuous_test.py` | composition only; `:796` untouched |
| the guards | **NEW `tests/test_assertion_strength.py`** | `tests/test_vacuous_density.py` has 41 lines of headroom (§0.8) |

⛔ **NO NEW DETECTOR CLASS.** The grader is module-level pure functions composed by the existing
`VacuousTestDetector`, so no class defines `run() -> DetectorResult` and
`TC-ArgusAgent-DETECT-001-145` stays green with its four pins. *Rejected:* an
`AssertionStrengthDetector`. It would buy nothing — there is no new finding, no new rule id and
no new pipeline stage in this story — and it would spend the fifth conformance pin, a new
`rule_id` in the vocabulary and a pipeline wiring decision on a story that emits nothing new.
⛔ **If a reviewer or the dev concludes a class IS required, its `if TYPE_CHECKING:` pin lands in
the SAME commit** (`-145` is RED in between).

⛔ **NOTHING IS ADDED TO `argus/detectors/__init__.py`** (§0.11).

### §1.3 ⛔ ONE DERIVATION FOR THREE QUESTIONS — the AR7 spine of this story

Three questions must each have exactly one derivation in `argus/detectors/**` when this story
lands. **Two of them have two today.**

| question | ONE derivation, after this story | today |
|---|---|---|
| *"where does the logical statement opening at line `s` end?"* | the `_scan_span` result — the last line whose `opens == s` | ⛔ **TWO**: `_scan_span` and `_logical_statement_end`, diverging on 5.93% (§0.6). `DF-AUD-DETECT-D`. |
| *"is this span edge a SUT call?"* | ONE classification, read by fact (b) **and** by the grader | ⛔ **ONE today, but it is PRIVATE and thrown away** inside `provenance_evidence`'s loop (`:912`–`:965`) — and the grader needs the same answer. Writing a second `is_sut` is `DF-AUD-DETECT-D`'s defect class, one story later, in the same module. |
| *"is this line an assertion statement?"* | `_assertion_statement_lines` (`:849`), called with the vocabulary the question needs (§1.5) | ONE — ⛔ **reuse it; do not fork it for the grader** |

⛔ **THE REQUIREMENT IS THE INVARIANT, NOT THE DIFF.** How the SUT-call classification is shared
— a projection function beside `logical_statement_starts`, a richer internal record type that
`provenance_evidence` folds into its counts, or a classification passed in — is the dev's call.
⛔ **What is not the dev's call: a second predicate anywhere in `argus/**` that decides "is this
a SUT call".** `TC-ArgusAgent-DETECT-001-151` sweeps for it.

⛔ **AND THE ORDER IS FIXED BY THE EPIC:** the collapse lands and is proven output-neutral
**BEFORE** grading is layered on it (AC4). A single commit that does both cannot show which
change moved the bytes.

### §1.4 ⛔ `S1` LANDS, AND NOTHING FLIPS

Specification §6.5: *"`S1` landing in Story 17.3 makes **nothing** verdict-eligible … 17.3 must
land `S1` such that no finding's `verdict_eligible` flips on it within Epic 17."*

Mechanically, that means:

1. `_ast_corroborated`'s **return expression at `vacuous_test.py:796` is unchanged**, compared
   as an AST expression by `TC-ArgusAgent-PRECISION-001-146`.
2. `S1` is computed **beside** fact (b), never instead of it, and its value **decides nothing**
   in `run()`: the `rule_id` chosen at `:661` and the `depth_supported` at `:665` stay driven by
   `score.ast_corroborated` alone.
3. The grading counts and the `S1` verdict are carried as **evidence counts** on the detector's
   own score object (`VacuousTestScore`, or a sibling frozen model beside it — the dev's call).
   ⛔ **Counts, never rendered sets** (`NFR-D2` / `AR4`), and ⛔ **no `float`** — the model's
   serializer rejects it.
4. ⛔ **Nothing reaches a `.argus/`-bound output.** `FindingDraft`, `DetectorResult` and
   `Recording` are **not** widened: `DN-18-4-6` measured that `Recording` has no field that could
   hold a count and concluded that widening one detector in isolation is the wrong shape of
   repair. ⛔ **The FR10 evidence-plumbing gap stays OPEN and this story does not touch it.**
5. ⚠️ **Whether `S1` is computed for EVERY scored span or only for heuristically-vacuous ones is
   the dev's call, and it has two consequences worth weighing rather than discovering.** The
   shipped `_ast_corroborated` short-circuits on `heuristically_vacuous` (`:780`), and the 1,032
   are all heuristic findings, so **17.4's measurement is unaffected either way**. Computing it
   for every span costs span-scan work on the majority path (AC7's record will show it);
   computing it only for flagged spans keeps the cost where it already is. ⛔ **Whichever is
   chosen, record it and record why** — a later reader must not have to infer it from a
   short-circuit.
6. ⚠️ **`VacuousTestScore` is `frozen`, `extra="forbid"`, and is constructed by four test
   modules** (`test_vacuous_density.py:105`, `test_vacuous_detector_index.py:476`,
   `test_vacuous_vocabulary.py:137`, `test_vacuous_cross_language.py:656`). A **required** new
   field breaks all four; a field with a default does not. Measure before choosing, and record
   the choice.

### §1.5 ⛔ WHICH TABLE ANSWERS WHICH QUESTION — the two-table split, applied a third time

`DN-14-2-1` is not a style rule; it is the reason a false 🔴 was reproduced end to end in Story
14.2. Applied to this story:

| question | vocabulary | why, and the harm if it is the other one |
|---|---|---|
| fact (a) — *"does the span reach a candidate SUT?"* | **FROZEN** (23) | UNCHANGED. Widening shrinks the candidate SUT set, moving towards an accusation. |
| fact (b′) — *"how many SUT results are discarded?"* | **FROZEN** (23), passed to `provenance_evidence` | UNCHANGED — fact (b)'s own arithmetic. Passing the WIDE one forks it (`silent_class.span_provenance` writes the reasoning out in full). |
| (c′) — *"which statements in this span are assertions?"* | ⛔ **WIDE** (89 + `\A_?assert\w*\Z`), via `is_assertion_callee` | ⛔ **An assertion through a name the FROZEN table never heard of would be invisible, the span would grade "all assertions at the weakest band" VACUOUSLY, and `S1` would accuse a well-asserting test.** This is `span_asserts_anything`'s reasoning, and it is why `S1 ⊇` the V2 silent band exactly. |
| (c′) — *"is raising the observation?"* | `RESULT_OBSERVING_CONTEXT_CALLEES` (9) + `_result_observing_lines` | §0.4 |

⛔ **The two tables are NOT unified and the FROZEN one is NOT widened.** Specification §3.2
records the measurement: widening the frozen table takes the population 36 → 84 — *"48 false
accusations is what the moat is worth here"*.

### §1.6 The cost record — a disclosure, and deliberately not a gate

The epic requires span-scan cost **before and after**, *"so a regression is disclosed rather than
discovered later"*, and states in terms: ⛔ *"This is not a performance story — `-C` stays OPEN
and is not dispositioned here."*

**The decision:** the primary measure is a **deterministic call count**, not a clock.

- Instrument `_scan_span`, `_code_prefix` / `_continued_code_prefix` and `_blank_strings` with a
  counting wrapper **in the measurement harness only** (never in shipped code), and report
  invocations per scored test function over a fixed, in-repo population.
- Wall-clock is reported **beside** it, labelled advisory, with the host and Python version
  named — a Windows developer machine is not the ubuntu matrix.
- ⛔ **No timing assertion, no invocation-count threshold and no benchmark enters the test
  suite.** A flaky gate is a defect this repository has not yet acquired, and `DF-AUD-DETECT-C`
  is filed 🟡 *"no output changes; this is cost, not correctness."*
- ⛔ **`DF-AUD-DETECT-C` is not dispositioned, not closed and not edited.** If the record shows a
  regression the dev states it plainly in the story record and escalates (AC10); it does not
  optimise under load.

*Rejected:* `pytest-benchmark` or a wall-clock ceiling. It would make CI's variance a build
failure and would convert an explicitly-not-a-performance-story into one.

### §1.7 The `Evidence-partition:` trailer value — `open`, and the reason is a disclosure

**Measured:** the trailer vocabulary is closed at `('sealed', 'open', 'none')`
(`gate_seal.SEAL_CITATION_VALUES`), and **all five ratified members are partitioned `pre-seal`**
— a value the trailer vocabulary does not carry, because `pre-seal` means *"Argus output over
this member already existed when the seal was taken"*.

The two most recent detector commits (`9e3fdc2`, `0ba6a98`, both Epic 18) wrote
`Evidence-partition: none`, and for them that was true — no corpus evidence informed them.

⛔ **For 17.3 it would be FALSE.** The grading scale, `S1`'s shape and the whole reason this epic
exists rest on measurements taken over those five members (`DF-INV-VACUOUS-A`, the 2026-08-24
research, the V2 band). **The decision: write `Evidence-partition: open` on every commit touching
`argus/detectors/**`**, and state in the commit body that the members are `pre-seal`, which the
vocabulary does not distinguish.

- *Rejected:* `none` — false, and the trailer exists precisely to make contamination visible.
- *Rejected:* `sealed` — false in the other direction; no sealed member's findings informed this.
- *Rejected:* ⛔ **amending `SEAL_CITATION_VALUES` to add `pre-seal`.** `SEAL_CITATION_RULE` names
  that move by name: *"Amending the rule to make a red commit green is the corpus-shopping
  failure mode with an extra step; the remedy is always to write the trailer."*
- The vocabulary gap is **recorded in this story record** as an observation. ⛔ **No new ledger id
  is filed for it without an operator act** (`AI-E9-8`: recording is the story's, filing is the
  operator's) — and grep the ledger first, because it may already know.

### §1.8 What this story does NOT fix, named so it is not mistaken for fixed

- `DF-INV-VACUOUS-A` — **OPEN.** Landing `S1` advisory does not close the stage mismatch;
  **17.4 measures whether it did.**
- `DF-16-7-A`, `DF-16-7-B`, `DF-14-1-A`, `DF-12-2-D`, `DF-12-3-A` — **OPEN and untouched.**
  Re-homing is **17.5's**.
- `DF-AUD-DETECT-C` — **OPEN, unscheduled, undispositioned** (§1.6).
- `DF-13-5-A` — **OPEN and UNSPENT.**
- `AI-E16-7` — **UNFILLED.** Not needed here (nothing is adjudicated); **17.4's** precondition.
- The `V2` band's 36 rows — **UNADJUDICATED**, and an operator act.
- The FR10 *"carrying their evidence counts"* plumbing gap — **OPEN, repository-wide**
  (`DN-18-4-6`).
- `DF-14-3-A`/`-B`/`-C` — Go/JUnit/Jest test discovery. **Untouched**; `S1` inherits the same
  blindness and that is not this story's to fix.

---

## §2 — THE COUPLINGS THAT WILL BITE

### §2.1 ⛔ ALL FOUR COSTS OF AN `argus/**` BYTE ARE SPENT HERE

`DN-17-1-1` counted them and 17.1 and 17.2 both avoided all four. **17.3 pays every one:**

1. **Dogfood-artifact currency** — *"CURRENT iff the cited provenance sha is an ancestor of HEAD
   **and** `git diff <sha> HEAD -- argus/` is empty."* ⛔ `python scripts/regenerate_dogfood_artifacts.py`
   **in its own commit**, after the last `argus/**` byte lands. ⚠️ `DF-INV-MERGE-A`: a squashed
   PR reddens `master` afterwards — record it, do not fix it here.
2. **`Evidence-partition:` trailer** — every commit touching `argus/detectors/**` (§1.7). Enforced
   over real history by `TC-ArgusAgent-PRECISION-001-94`'s tail loop. **18.1 lost a sha to a
   forgotten one.**
3. **`--cov=argus --cov-fail-under=80`** — a new `argus/` module drags the gate; the new guard
   module must cover it.
4. **`mypy argus` / `bandit -r argus --severity-level medium`** — blocking, over a module that
   ships in the wheel. ⛔ `mypy` runs on **95 files** today; strict typing, no `Any` leakage, no
   `# type: ignore` without a reason on the line.

### §2.2 The commit arc — FIVE commits, and the order is load-bearing

⛔ **`TC-ArgusAgent-DOCS-001-78` closes in both directions**, so the story record's closure claim
for `DF-AUD-DETECT-D` and the ledger's disposition **must land in the SAME commit**.
⛔ **The collapse must be a SEPARATE, EARLIER commit than the grading** (AC4.1) — a single commit
that does both cannot show which change moved the bytes.

- **Commit O — `chore(17-3): open the assertion-strength grading story`**
  this story file + `sprint-status.yaml` `ready-for-dev` → `in-progress`. *(No `argus/**` byte;
  no trailer needed.)*
- **Commit A — `refactor(17-3): one derivation for where a logical statement ends`**
  the `DF-AUD-DETECT-D` collapse in `provenance_scan.py`, its guard, and **nothing else**.
  ⛔ Carries `Evidence-partition: open`. ⛔ The neutrality evidence is recorded against **this**
  commit.
- **Commit B — `feat(17-3): grade what each assertion constrains, and land S1 advisory`**
  `argus/detectors/assertion_strength.py` + the `vacuous_test.py` composition + the SUT-call
  classification projection + `tests/test_assertion_strength.py`.
  ⛔ Carries `Evidence-partition: open`.
- **Commit C — `chore(17-3): regenerate the dogfood artifacts at <sha>`**
  the regeneration only, citing a provenance sha that is an ancestor of HEAD. *(No `argus/**`
  byte; the artifacts are not under `DETECTOR_TUNING_PATHS`, so no trailer — verify before
  committing.)*
- **Commit D — `docs(17-3): close DF-AUD-DETECT-D; record the 17.3 dev round`**
  the `deferred-work.md` note **and** this story's record **and** the `sprint-status.yaml`
  transition — **together, in one commit** (`-78`).

### §2.3 ⛔ THE GUARDS, AND THE ONES THAT WOULD GO GREEN BY FINDING NOTHING

Per the **GUARD-ADEQUACY CLAUSE** (`architecture.md:1132`, Story 13.2 / AC8.4) every guard states
(i) its observable, (ii) a demonstration that the defect **moves** that observable — **RED at the
REAL SEAM**, not against a reconstruction — and (iii) at least one adversarial variant
**GENERATED** from the table, record or tree it closes over, **with its count**.

Four of this story's guards assert a negative or sweep a population, and each has a specific way
of going quietly dead:

- a **sweep for a second `is_sut` predicate** that parses zero modules, or whose matcher matches
  nothing, reports *"one derivation"* forever → ⛔ **assert the module count and assert the KNOWN
  derivation is FOUND, before asserting any absence**;
- a **fail-closed fixture** hand-written for `pytest.raises` alone tests one of nine callees →
  ⛔ **generate one fixture per member of `RESULT_OBSERVING_CONTEXT_CALLEES` and assert the count
  is 9**, so a name entering or leaving the table re-runs the adversary automatically;
- a **band-assignment guard** over an empty assertion population is measuring nothing →
  ⛔ **assert the graded assertion count ≥ a stated floor FIRST** (`AI-E11-1`);
- an **`_ast_corroborated`-unchanged guard** that compares source **strings** goes red on a
  reformat and green on a semantic change with the same text → ⛔ **compare the parsed
  expression**.

⛔ **A guard is never weakened to go green** (`DF-8-5-B`). If a guard is RED because the code is
wrong, the code is fixed.

### §2.4 ⛔ THE LEDGER'S BYTE INVARIANTS AND ITS CLOSURE VOCABULARY

`deferred-work.md` carries **exactly one CR byte** in 593,897 (§0.0). ⛔ **Read and write it in
BINARY mode**; a text-mode round-trip normalises that byte away and produces a one-byte diff
across a 594 KB file that no reviewer will see. **Count before and after.**

The ledger writes a closure two ways, both recognised by `ledger_closed_ids`: inline on the
entry's own line, and as a trailing `- status: **CLOSED …**` field under the entry's id.
⛔ **`DF-AUD-DETECT-E`'s and `DF-AUD-DETECT-F`'s 2026-08-25 notes are the shape to copy** — a
dated, append-only note that leaves every byte above it unchanged (§3.4 evidence immutability).

⛔ **Grep the ledger before writing.** It already knows a great deal; cite prior art rather than
re-filing it.

### §2.5 ⛔ THE CLOSURE-VERB RULE, AND THE HAND-OFF TO 17.5

`story_closure_claims` is **line-scoped**, anchored to a closure verb
(`CLOSED|Closes|closes|Closed by this story`) and negation-aware on the same line.

- ⛔ **`DF-AUD-DETECT-D` is the ONLY id this story may write a closure verb next to**, and only
  in the same commit as its ledger disposition (§2.2 D).
- ⛔ **No line of this story record may write a closure verb next to any other `DF-*` id.**
- ⚠️ **HAND-OFF TO 17.5, and it is a real one.** Story 17.5's AC says it will point
  `DF-AUD-DETECT-D` *"at this epic's Story 17.3 — scheduling notes only"*. Once this story lands
  a terminal disposition for it, that scheduling note would point at completed work — which is,
  precisely, the defect class 17.5 exists to end (*"nothing points at a closed story"*).
  ⛔ **Record the hand-off explicitly in the Completion Notes** so 17.5 writes a disposition
  pointer naming this story's sha instead of a schedule.

⚠️ **AND THAT IS WHY THIS STORY SPEC NEVER WRITES A CLOSURE VERB BESIDE `DF-AUD-DETECT-D`.**
Measured at contexting by running `-78`'s own exported analyzers over this very file — and the
first draft of this spec **was RED**, caught by `story_closure_claims` before it was written to
disk. One line carrying the entry's id **and** a closure verb is enough: the analyzer extracts
the id, the ledger holds no disposition for it yet, and **`TC-ArgusAgent-DOCS-001-78` goes RED
the moment commit O lands and stays RED until commit D**.
⛔ **Do not "tidy" this spec by adding the verb** — and note that this paragraph is written so
that no single line of it carries both, which is the same discipline. The claim belongs in the
**Dev Agent Record**, written in commit D beside the ledger note.

### §2.6 ⛔ THE TREE IS SHARED

A peer session commits to this same branch. ⛔ **Never `git add -A`.** Stage by **explicit path**
and verify the write set with `git status --porcelain` against AC8.1 before every commit.

⛔ **`sprint-status.yaml` is edited SURGICALLY** — one status value per transition, and
`last_updated` **only if its value is not already today's date** (it already reads `2026-08-25`).
It must stay at **1,264 lines / 1,264 CR bytes**, and its comment blocks and **STATUS
DEFINITIONS** block must survive byte-for-byte. ⛔ **Do not use `sed -i` on it or on any artifact
file** — GNU sed on this host flattens CRLF across the whole file.

### §2.7 ⛔ LOCAL GATES ARE WINDOWS-ONLY; CI IS AN UBUNTU MATRIX

Every gate the dev can run is **local and Windows**; `audit-ci.yml` triggers on `master`/`main`
only and this branch is unpushed, so **no CI evidence exists at any sha in this arc**
(`AI-E13-1`; epic-18 retro SD-4). ⛔ **Label every gate figure LOCAL (Windows).**

⛔ **And this story is in the class where that bites.** It ships line-oriented text scanning over
third-party source: encodings, exotic line separators, Unicode identifiers and `pathlib`
behaviour all differ. Concretely, for this story:

- ⛔ **No `str.splitlines()`.** Use `index_aligned_lines` — the line-numbering contract
  (`vacuous_test.py:530`). `splitlines()` splits on eleven things where the index counts one, and
  Story 15.2 measured a false accusation caused by two form feeds.
- ⛔ **No `^`/`$` regex anchors** anywhere in `provenance_scan.py` or the new module — `\A`/`\Z`
  only. `$` also matches immediately BEFORE a trailing `\n`, so a pattern that ever meets a line
  carrying its terminator behaves differently on CRLF and LF input (`DF-14-2-B`).
  ⚠️ **MEASURED GAP, and it is this story's to close.** The existing sweep —
  `tests/test_vacuous_cross_language.py:724`,
  `test_provenance_scan_anchors_no_pattern_with_caret_or_dollar` — is scoped to
  **`provenance_scan.py` alone**, and it carries no `TC-ArgusAgent-…` id. A new module under
  `argus/detectors/` carrying regexes would be **unswept**. ⛔ **Extend that guard's POPULATION to
  `argus/detectors/**`** — its `_anchors_on_caret_or_dollar` predicate is already pure and
  exported for exactly this, and widening a population is the direction
  `test_module_size_ceiling._REMEDY` demands (*"do NOT narrow this guard's population"*). ⛔ **Do
  not fork a second sweep** (AC9.11).
- ⛔ **Every identifier pattern Unicode-aware by construction** (`_IDENT = r"[^\W\d]\w*"`), and
  every file read/write names `encoding="utf-8"`.
- ⛔ **No platform path separator and no `os.sep`** on any locator path; POSIX forward slashes,
  built from what the index gave you.
- ⛔ **Nothing may depend on `isinstance` verdicts that differ across 3.10–3.13** — Story 18.4
  measured a decoy whose verdict flips between 3.11 and 3.12.

### §2.8 The idioms you need, so you do not go looking for them

| need | take it from |
|---|---|
| a name-binding resolver over source lines, one forward pass, transitive | `provenance_scan._mock_bound_names` (`:794`) — ⛔ **the direct mirror image of what you are building** |
| a closed vocabulary that refuses an unregistered member | `silent_class.IDIOMS` + `UnregisteredIdiom` (`:126`) · `gate_seal.PARTITION_VALUES` + `UnregisteredPartition` (`:143`) |
| a per-member meaning function beside the vocabulary | `silent_class.idiom_meaning` (`:191`) · `gate_seal.partition_meaning` |
| a projection of one scan, never a second walk | `provenance_scan.logical_statement_starts` (`:606`) — *"A PROJECTION of `_scan_span`, never a second walk (AR7/§3.3)"* |
| a frozen counts-only evidence model | `provenance_scan.ProvenanceEvidence` (`:832`) · `silent_class.SpanScore` (`:217`) |
| a predicate composed from shipped helpers, re-implementing none | `silent_class.score_span` (`:309`) |
| an AST sweep that CLASSIFIES references rather than counting strings | `tests/test_silent_class.py:457` (`-126`), `:525` (`-127`) |
| adversarial variants **generated** from a live table with a count | `tests/test_silent_class.py:601` (`-128`) · `tests/test_governance_record_integrity.py:198` (`-78`) |
| a static conformance pin under `if TYPE_CHECKING:` | `vacuous_test.py:799` (should §1.2's decision ever be reversed) |
| a rule written down where the next author reads it | `gate_seal.SEAL_CITATION_RULE` · `test_module_size_ceiling._REMEDY` |
| a source sweep with a pure, exported predicate and positive controls both ways | `tests/test_vacuous_cross_language.py:169` (`_anchors_on_caret_or_dollar`), `:724` (the sweep AC9.11 widens) |
| a dated, append-only ledger disposition | `deferred-work.md` — the `DF-AUD-DETECT-E` / `-F` 2026-08-25 notes |
| the 1,032-finding harness, read-only over pinned blobs | `scripts/build_silent_class_record.py --check --checkout-root <root>` |

---

## §3 — AC ↔ TASK MAP

| AC | what it fixes | tasks | guards |
|---|---|---|---|
| AC1 | the scale is committed, closed, ordered and meaningful | 0, 2 | `-147` |
| AC2 | grading is correct where it is dangerous — the fail-closed trap and the conservative default | 2, 3 | `-149`, `-150` |
| AC3 | the scorer is PURE and does not re-parse | 2 | `-148` |
| AC4 | the `DF-AUD-DETECT-D` collapse, first and output-neutral | 0, 1 | `-151`, `-152` |
| AC5 | `S1` is the specified predicate, and its threshold did not move | 2 | `PRECISION-001-145` |
| AC6 | nothing flips: no verdict-eligibility, no reach figure, no successor output | 3, 4 | `PRECISION-001-146` |
| AC7 | the span-scan cost record; `-C` stays open | 4 | — (deliberately none) |
| AC8 | scope, gates, the commit arc and the byte invariants | 5 | — |
| AC9 | guards, each with an observable and an executed mutation; the anchor sweep widened | 3 | all, `-153` |
| AC10 | escalate, do not decide | all | — |

---

## Acceptance Criteria

### AC1 — A COMMITTED, CLOSED, ORDERED ASSERTION-STRENGTH SCALE

**Given** the epic requires *"a stated, committed scale — at minimum *does not reference an
SUT-derived value* / *constrains only its existence or type* / *constrains its value*"*,
**When** this story completes,
**Then** `argus/detectors/assertion_strength.py` declares that scale, and:

- **AC1.1** — the scale is a **closed, ORDERED** vocabulary of at least the three named bands
  (§1.1), declared **exactly once** in the repository, with `none` at ordinal 0.
- **AC1.2** — **every band carries a MEANING** in the `idiom_meaning` / `partition_meaning` house
  form, written *"in the words a promotion proposal would have to defend"*.
- **AC1.3** — an **unregistered band RAISES** a named error (`UnregisteredStrength`, the
  `DF-10-4-E` shape). ⛔ **Never defaulted, never tolerated**, and the refusal is proven by
  driving it, not by reading the list.
- **AC1.4** — **`unestablished` is carried as its own count and is NOT a band** (§1.1), and the
  reason is stated in the module: it is `NFR-R1`'s recorded condition, and `S1` refuses on it.
- **AC1.5** — per-span results are **COUNTS** (`NFR-D2` / `AR4`): a count per band plus the
  `unestablished` count. ⛔ **No rendered set, no iteration-order-dependent value, no `float`.**
- **AC1.6** — the scale's **direction of harm is written down beside it**: only the `none`
  boundary admits `S1`, so ⛔ **when in doubt, NOT the weakest band** (§0.5).

### AC2 — THE GRADING IS RIGHT WHERE IT IS DANGEROUS

**Given** the moat is *"a false 🔴 is the lethal failure; a real vacuous test left advisory is
tolerable"*,
**Then** each assertion in a flagged span is graded, and:

- **AC2.1** — the assertion **population** for grading is the **WIDE** vocabulary — bare `assert`
  plus `is_assertion_callee` — read through the shipped helpers, ⛔ **never the FROZEN table**
  (§1.5).
- **AC2.2** — an assertion referencing a name bound, transitively, from a SUT call grades at
  `existence` or `value`, never `none`; the resolver is a **name-level forward pass in
  `_mock_bound_names`' idiom** (§0.7).
- **AC2.3** — ⛔ **AMBIGUITY RESOLVES AWAY FROM THE WEAKEST BAND.** A name that could be either
  mock-derived or SUT-derived is treated as **SUT-derived**; an expression whose chain cannot be
  read is **not** graded `none`.
- **AC2.4** — ⛔ **THE FAIL-CLOSED RULE.** An assertion that is a
  `RESULT_OBSERVING_CONTEXT_CALLEES` call whose block covers a SUT call grades at the
  **STRONGEST** band — *raising IS the observation* (`DN-3`). The covered line set is **read from
  `_result_observing_lines`**, never re-derived. ⛔ **Proven over all nine members of the table,
  GENERATED with the count asserted** (`TC-ArgusAgent-DETECT-001-149`).
- **AC2.5** — a span with **no assertions at all** grades (c′) **TRUE** (the empty-assertion case
  the specification names explicitly), so `S1 ⊇` the V2 silent band exactly.
- **AC2.6** — ⛔ **the threshold is EVERY assertion at the weakest band and it is NOT widened.**
  Admitting `existence` is a separate, future act requiring its own pre-registration
  (specification §2.2). ⛔ **Not a tuning knob.**

### AC3 — THE SCORER IS PURE (AR8) AND DOES NOT RE-PARSE

**Given** the epic: *"grading reads the source text and the index and nothing else — no re-parse,
no second grammar call, no clock/uuid/random"*,
**Then**:

- **AC3.1** — the new module imports **no** parser: no `ast`, no `tree_sitter`, no
  `argus.index` grammar entry point. ⛔ Proven by an **AST sweep of the module's own source**
  (`tests/test_silent_class.py:457`'s idiom), not by a promise in a docstring.
- **AC3.2** — no I/O, no network, no clock, no `uuid4`, no `random`, no environment read, no
  module-level path resolution (`DF-9-2-A` — the wheel-import guard imports every shipped module
  out of a built distribution with this repository off `sys.path`).
- **AC3.3** — **determinism driven, not asserted**: the same `(source_lines, edges, span)` yields
  an equal result across repeated calls and across shuffled edge input, since the index's edge
  order is not source order (`provenance_evidence`'s own note).
- **AC3.4** — ⛔ **`NFR-R1`: a parse or resolution failure degrades to a recorded condition,
  never an uncaught raise**, and the failure path is **driven** over generated malformed spans —
  truncated, unterminated-literal, off-span edge, empty line list, `start > end`
  (`TC-ArgusAgent-DETECT-001-150`).
- **AC3.5** — ⛔ **when strength cannot be established the finding does NOT gain
  verdict-eligibility** and `S1` **refuses**. The conservative default IS the moat.

### AC4 — THE `DF-AUD-DETECT-D` COLLAPSE, TAKEN FIRST AND PROVEN OUTPUT-NEUTRAL

**Given** `DF-AUD-DETECT-D` records that `_logical_statement_end` and `_scan_span` are two
derivations of the same statement-boundary question (AR7 §3.3),
**When** this story extends the span scanner,
**Then**:

- **AC4.1** — ⛔ **the two collapse to ONE derivation in a commit that PRECEDES the grading
  commit** (§2.2 A before B). The end of the statement opening at `s` is the last line whose
  `opens == s` in the `_scan_span` result. ⛔ **It is a DELETION plus a projection, not a third
  function.**
- **AC4.2** — the divergence is **RE-MEASURED at HEAD before the change** (§0.6 reproduces:
  232 files / 31,845 statements / 1,890 divergences) and the entry's stages (ii) and (iii) are
  **re-derived, not quoted**: fact (b) re-scored over the repository's own test functions with
  the new extent → **0 evidence differences, 0 corroboration flips**; and a synthetic trigger
  built to exploit the string-state gap → **identical `ProvenanceEvidence` from both**.
- **AC4.3** — ⛔ **output-neutrality over the 1,032, byte-identical or it is not a collapse.**
  `scripts/build_silent_class_record.py --check --checkout-root <root>` is run **before and
  after** the collapse and the committed `silent-class-record.json` and
  `silent-class-worklist.md` are **byte-unchanged**. ⛔ The command, its exit code and the
  byte comparison are recorded in the Dev Agent Record. ⛔ **It ratifies nothing, adjudicates
  nothing and writes nothing to any corpus member.**
- **AC4.4** — ⛔ **it is a LOCAL measurement and is labelled so**; **no committed test may
  require the five checkouts** (§0.9).
- **AC4.5** — the in-repo half **is** a committed guard: the statement-extent property is pinned
  over a generated population with its count, **including the multi-line-docstring case the old
  implementation got wrong**, so the string state cannot be lost again
  (`TC-ArgusAgent-DETECT-001-152`).
- **AC4.6** — ⛔ **ONE derivation for "is this span edge a SUT call"** — fact (b) and the grader
  read the same classification, and no second `is_sut`-shaped predicate exists anywhere in
  `argus/**` (§1.3, `TC-ArgusAgent-DETECT-001-151`).
- **AC4.7** — `DF-AUD-DETECT-D` receives a **dated, append-only** disposition in
  `deferred-work.md`, in the same commit as this story's closure claim (§2.2 D, `-78`). ⛔ The
  entry above it is **byte-unchanged** and the file's **1-CR invariant** holds.

### AC5 — `S1` IS THE PREDICATE 17.2 SPECIFIED, AND NOTHING ELSE

**Given** `successor-vacuity-predicate-specification.md` §2.1 defines `S1` as three conjuncts,
**Then** the shipped `S1`:

- **AC5.1** — is **(a) reachability UNCHANGED** — the shipped fact (a), reading the **FROZEN**
  table — **AND (b′) `discarded_sut_calls >= 1` UNCHANGED** — fact (b)'s own arithmetic through
  `provenance_evidence` with the FROZEN table — **AND (c′)** every assertion at the weakest band,
  including the empty-assertion span.
- **AC5.2** — ⛔ **carries NO mock-binding input.** `_mock_bound_names`,
  `mock_referencing_assertions` and the `mref` clause play **no part** in (a), (b′) or (c′)
  (specification §7.3). `mock_referencing_assertions` still has **exactly one decision site** in
  `argus/**` after this story, and `TC-ArgusAgent-PRECISION-001-143` must stay green.
- **AC5.3** — ⛔ **`consumed == 0` is not deleted from, weakened in, widened within or re-scoped
  in the shipped predicate.** `S1` is computed **beside** fact (b); fact (b) is untouched.
- **AC5.4** — the predicate's declaration **names the specification document and its section**,
  and ⛔ **does not re-argue it**. A prose copy of the specification's argument inside the module
  is the `DF-8-5-C` / `AI-E9-7` defect; cite it.
- **AC5.5** — ⛔ **the specification document is NOT edited by this story** (§3.4). If code and
  document disagree, that is **AC10**.
- **AC5.6** — ⛔ **`S1`, the scale and the grader are PUBLIC and listed in the module's `__all__`.**
  **Story 17.4 must be able to MEASURE the shipped predicate**, from `scripts/` or from
  `argus/precision/**`, **without re-deriving it** — and that import direction is legal
  (`silent_class` already imports the detector package one-way; `-127` fences only the reverse).
  ⛔ **A private `_s1(...)` buried in `vacuous_test.py` would force 17.4 to fork the predicate,
  which is the `AR7` defect this epic exists to close.**

### AC6 — NOTHING FLIPS, NOTHING IS MEASURED, NOTHING IS PUBLISHED

- **AC6.1** — ⛔ **`vacuous_test.py:796`'s return expression is UNCHANGED**, compared as a parsed
  AST expression (`TC-ArgusAgent-PRECISION-001-146`).
- **AC6.2** — ⛔ **no finding's `verdict_eligible` / `rule_id` / `depth_supported` changes.**
  Proven by measurement over the 1,032 (AC4.3's same run): `vacuous_test_ast` stays **0**, and
  the flagged population is unchanged.
- **AC6.3** — ⛔ **NO REACH FIGURE FOR `S1` IS WRITTEN IN ANY COMMITTED ARTIFACT OF THIS STORY** —
  not in the module, not in a docstring, not in the ledger note, not in this story record.
  17.2 refused it (`DN-17-2-4`); **17.4 measures it.** ⚠️ Counts that appear as *guard fixtures*
  are not reach figures; a sentence of the form *"`S1` reaches N over the corpus"* is.
- **AC6.4** — ⛔ **neither `SUCCESSOR_OUTPUT_PATHS` prefix is created and nothing is written under
  either**; both are asserted **ABSENT** after the arc. ⚠️ **What the epic's BINDING ORDERING
  CONSTRAINT does and does not say about this story:** it orders 17.1's commit before every commit
  carrying a successor predicate's **OUTPUT over a corpus member** — `f906d04` is already an
  ancestor of HEAD, and this story commits **the predicate's CODE, never its output**. So 17.4's
  ancestry guard has nothing to find here, **provided AC6.4 holds**. ⛔ Committing so much as one
  scored row would make that guard argue about a commit nobody planned.
- **AC6.5** — ⛔ **no member ratified, no third-party source fetched, no round spent, no row
  adjudicated.** `DF-13-5-A` stays **OPEN and UNSPENT**; `validation-corpus/**` is
  byte-unchanged; the externalization gate stays `BLOCKED` and `protocol_cleared` stays `False`.
- **AC6.6** — `scripts/precision_preregistration.py` is **byte-unchanged** and
  `TC-ArgusAgent-PRECISION-001-140` is green **and unedited**.
- **AC6.7** — `TC-ArgusAgent-PRECISION-001-127` is **green and unedited** — nothing in
  `argus/detectors/**` reaches `argus/precision/silent_class.py`, directly or transitively
  (§0.3). ⛔ **The fence is not widened.**

### AC7 — THE SPAN-SCAN COST IS RECORDED, AND `DF-AUD-DETECT-C` STAYS OPEN

**Given** `DF-AUD-DETECT-C` measures the detector layer's hot path in the density denominator,
**Then**:

- **AC7.1** — span-scan cost is recorded **before and after** this story's addition, over a
  **fixed in-repo population**, as a **deterministic call count** (`_scan_span` /
  `_code_prefix` / `_blank_strings` invocations per scored test function), with wall-clock
  reported **beside** it and labelled advisory, naming the host OS and Python version (§1.6).
- **AC7.2** — ⛔ **no timing assertion, no invocation-count threshold and no benchmark enters the
  test suite.**
- **AC7.3** — ⛔ **`DF-AUD-DETECT-C` is NOT dispositioned, closed or edited.** ⛔ **This is not a
  performance story**; if the record shows a regression, state it and escalate (AC10) rather
  than optimise under load.

### AC8 — SCOPE, GATES AND THE COMMIT ARC

- **AC8.1 — the write set is EXACTLY:** `argus/detectors/provenance_scan.py` ·
  **NEW** `argus/detectors/assertion_strength.py` · `argus/detectors/vacuous_test.py` ·
  **NEW** `tests/test_assertion_strength.py` · `tests/test_vacuous_cross_language.py` (**AC9.11's
  population widening ONLY**) · the regenerated dogfood artifacts · the `DF-AUD-DETECT-D` note in
  `deferred-work.md` · this story file · `sprint-status.yaml`.
  ⛔ **Nothing else**, verified by `git status --porcelain` and `git diff --stat` before each
  commit. ⛔ Any other touched file is an escalation, not a decision.
- **AC8.2 — proved, not asserted:** `git diff <base> HEAD --` over
  `scripts/` · `_bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md` ·
  `…/successor-vacuity-predicate-specification.md` · `…/successor-predicate-precision-preregistration.md` ·
  `…/E-PRD/` · `…/architecture.md` · `…/epics.md` · `…/validation-corpus/` ·
  `argus/precision/` · `argus/detectors/base.py`
  is **EMPTY**, with the output recorded.
- **AC8.3 — every existing guard in the blast radius is green AND unedited**: `-127` · `-140` ·
  `-142`..`-144` · `-145`/`-146` (DETECT) · `-22` · `-78` · `-93`/`-94` · the NFR-M1 sweep ·
  `tests/test_vacuous_*.py` · `tests/test_silent_class*.py`. ⛔ **No existing test deleted,
  skipped, xfailed or weakened**; test-function names are a population that may grow and may not
  shrink. ⚠️ **ONE carve-out, and it goes only one way:** AC9.11 **widens** the anchor sweep's
  population in `tests/test_vacuous_cross_language.py` and gives it an id. ⛔ **No assertion in
  that file may be removed, relaxed or narrowed**, and its existing positive controls must still
  drive the predicate to both outcomes. Record the diff explicitly — a *"guard edited"* line in a
  story that touches detectors is exactly what a reviewer must be able to check in one look.
- **AC8.4 — NFR-M1**: every touched module ≤1200 lines, with §0.8's pre-registered split trigger
  applied **at Task 1** and its projection recorded. ⛔ **No `_EXEMPT_BY_DESIGN` entry.**
- **AC8.5 — every gate, every exit code, recorded and labelled LOCAL (Windows):** full `pytest`
  (exit 0, collected/passed counts, no `F`/`E` markers) · `mypy argus` · `bandit -r argus
  --severity-level medium` · `pytest --cov=argus --cov-fail-under=80` with the percentage ·
  the NFR-M1 sweep · `tests/test_dogfood_artifact_currency.py`.
- **AC8.6 — the five-commit arc of §2.2**, with the trailer on both `argus/detectors/**` commits,
  the regeneration in its own commit, and the ledger note + story record + `sprint-status.yaml`
  transition **together in commit D** (`-78`).
- **AC8.7 — byte invariants verified after every artifact write:** `deferred-work.md` **1 CR**;
  `sprint-status.yaml` **1,264 lines / 1,264 CR**.
- **AC8.8 — no `git add -A`.** Explicit paths only; the tree is shared.

### AC9 — THE GUARDS, EACH WITH AN OBSERVABLE AND AN EXECUTED MUTATION

**Given** the **GUARD-ADEQUACY CLAUSE** (`architecture.md:1132`),
**Then** `tests/test_assertion_strength.py` commits the guards below, each discharging (i)
observable, (ii) RED **at the real seam** by an **executed** mutation, (iii) an adversarial
variant **GENERATED** from a live table or tree **with its count**, in its own docstring:

- **AC9.1 — `TC-ArgusAgent-DETECT-001-147` — the scale is closed, ordered and meaningful.**
  *Observable:* the vocabulary, its order, each band's meaning, and the refusal of an
  unregistered band **driven**. *Generated:* every band is round-tripped through the meaning
  function with the count asserted; a generated unregistered value must raise.
- **AC9.2 — `TC-ArgusAgent-DETECT-001-148` — the grader is PURE and does not re-parse.**
  *Observable:* an AST walk over the new module's own source — imports, call names,
  module-level statements. *Non-vacuity FIRST:* the walk must parse the module and resolve a
  **known-present** import, or every absence is a broken walk. ⛔ **Classify AST nodes, never
  count substrings.** *Mutation:* add `import ast` → RED; restore byte-exact, sha256-verified.
- **AC9.3 — ⛔ `TC-ArgusAgent-DETECT-001-149` — THE FAIL-CLOSED TEST IS NOT ACCUSED.**
  *Observable:* the graded band of the sole assertion, and `S1`'s verdict, for a span whose only
  assertion is a result-observing context wrapping a discarded SUT call. *Generated with its
  count:* **one fixture per member of `RESULT_OBSERVING_CONTEXT_CALLEES`, count asserted == 9**,
  scored **at the real seam** through the shipped grader. *Non-vacuity FIRST:* each fixture is
  asserted to reach `discarded_sut_calls >= 1` and to carry ≥1 assertion, or the refusal is
  measured over an empty span. *Mutation:* remove the observing-context rule → RED, with the
  false accusation visible.
- **AC9.4 — `TC-ArgusAgent-DETECT-001-150` — the unestablished path refuses, and never raises.**
  *Observable:* the `unestablished` count and `S1`'s verdict over **generated** malformed spans
  (truncated line list, unterminated literal, off-span edge, `start > end`, empty edges), with
  the generated count asserted. ⛔ **No uncaught exception on any variant** (`NFR-R1`).
- **AC9.5 — `TC-ArgusAgent-DETECT-001-151` — ONE derivation, swept over `argus/**`.**
  *Observable:* an AST sweep for a second statement-extent walk and a second `is_sut`-shaped
  predicate. *Non-vacuity FIRST:* the sweep parses ≥60 modules **and resolves the ONE known
  derivation of each question**, or *"there is only one"* is a broken sweep. *Mutation:* plant a
  second predicate in a real module → RED; restore byte-exact.
- **AC9.6 — `TC-ArgusAgent-DETECT-001-152` — the statement extent carries the string state.**
  *Observable:* the extent of a statement opening a multi-line docstring, over a **generated**
  population drawn from the repository's own tracked files with its count asserted. *Mutation:*
  restore the `pending=None` behaviour → RED.
- **AC9.7 — `TC-ArgusAgent-PRECISION-001-145` — `S1` is the SPECIFIED predicate.** *Observable:*
  the three conjuncts driven independently — each falsified alone must refuse — plus the
  threshold: a span carrying exactly one `existence`-band assertion must be **REFUSED**.
  *Generated with a count:* one widening variant per band above `none`, each asserted to change
  the verdict. *Non-vacuity FIRST:* a span that `S1` **accepts** is exhibited, or every refusal
  is trivially green.
- **AC9.8 — `TC-ArgusAgent-PRECISION-001-146` — nothing flipped.** *Observable, three halves:*
  (1) `_ast_corroborated`'s return expression compared as a **parsed AST expression** to the
  pinned form; (2) both `SUCCESSOR_OUTPUT_PATHS` prefixes asserted **ABSENT** on disk; (3)
  `git diff <base> HEAD --` over `argus/precision/`, `scripts/` and the specification document
  is **EMPTY**. *Non-vacuity FIRST:* a **control path known to carry commits in the same range**
  is asserted non-empty — a misspelled pathspec returns empty and reads exactly like a clean
  tree (`-75`/`-94`/`-139`'s answer, reused). *Mutation:* alter the return expression → RED.
- **AC9.9** — every guard is **PURE** except read-only `git` verbs, carries its
  `TC-ArgusAgent-…` id in its name and first docstring line, and runs in the default suite.
  ⛔ **No new area id is opened** — `DETECT-001` continues at `-147`, `PRECISION-001` at `-145`.
  ⛔ **No guard may decide conformance by `isinstance`/`issubclass` against a Protocol.**
- **AC9.10** — ⛔ **a guard is never weakened to go green** (`DF-8-5-B`).
- **AC9.11** — ⛔ **the `^`/`$` anchor sweep's POPULATION is widened to `argus/detectors/**`**
  (§2.7) so the new module's patterns are covered, reusing the existing exported
  `_anchors_on_caret_or_dollar` predicate and its positive controls. ⛔ **Widened, never forked**;
  and while it is being touched, give it its `TC-ArgusAgent-DETECT-001-153` id — it has none
  today.

### AC10 — ESCALATE, DO NOT DECIDE

**Given** this story's whole value is that the grading is conservative where it is dangerous,
**Then** the dev **STOPS and escalates in the story record** — it does not adjust a band, a
threshold, a table or a claim — if any of the following is observed:

- **AC10.1** — any §0 row fails to reproduce at HEAD.
- **AC10.2** — the collapse is **not** byte-neutral over the 1,032 (AC4.3), or over the
  repository's own test functions (AC4.2). ⛔ **A divergence is a finding, not a rounding.**
- **AC10.3** — `S1` as specified cannot be built without re-parsing, without widening the FROZEN
  table, without unifying the two vocabularies, or without importing `silent_class` from the
  detector package.
- **AC10.4** — the specification (`successor-vacuity-predicate-specification.md`) is **falsified
  by measurement** — the three conjuncts do not compose, or (c′) is not computable at
  name level. ⛔ **The document is not edited; the disagreement is escalated.**
- **AC10.5** — any finding's `verdict_eligible`, `rule_id` or `depth_supported` moves (AC6.2).
- **AC10.6** — `mypy argus`, `bandit`, coverage or the NFR-M1 sweep cannot be satisfied without
  weakening a guard, adding an `_EXEMPT_BY_DESIGN` entry, or narrowing a population.
- **AC10.7** — a corpus member's pinned sha becomes unreachable, or the harness refuses (exit 2).
  ⛔ **Record which member and why; do not re-pin, do not substitute a member, do not skip.**
- **AC10.8** — a `sprint-status.yaml` or `deferred-work.md` byte invariant cannot be preserved.
- **AC10.9** — the story cannot be completed without touching a file outside AC8.1's write set.

---

## Dev Notes

### Decisions this story TAKES, each with its rejected alternative

- **`DN-17-3-1` — the grader ships in a NEW `argus/detectors/assertion_strength.py`.**
  *Rejected:* (a) `argus/precision/` — one import line from the detector turns `-127` RED and
  the correct answer is never to widen the fence; (b) growing `provenance_scan.py`, which has
  224 lines of headroom against a repository that has filed `DF-16-5-A` at 68; (c) growing
  `vacuous_test.py`, whose subject is *scoring a test function*, not answering *"what does this
  assertion constrain"* — the same cohesion boundary that produced `provenance_scan.py` in
  Story 14.1.
- **`DN-17-3-2` — NO new detector class, so `TC-ArgusAgent-DETECT-001-145` stays green.**
  *Rejected:* an `AssertionStrengthDetector`. It emits no finding, has no `rule_id` and needs no
  pipeline stage in this story; it would spend a fifth conformance pin, a new rule-id vocabulary
  entry and a wiring decision for nothing. ⛔ If reversed, the pin lands in the same commit.
- **`DN-17-3-3` — the collapse is taken FIRST, in its own commit, and is a DELETION.**
  *Rejected:* one commit doing both, and a third `statement_extent()` helper. `DF-AUD-DETECT-D`'s
  own suggested repair is *"a deletion, not an addition"*, and a combined commit cannot show
  which change moved the bytes.
- **`DN-17-3-4` — `unestablished` is a COUNT, not a fourth band, and `S1` refuses on it.**
  *Rejected:* a fourth band `unknown` on the scale, which would make the scale's order meaningless
  (where does *unknown* sit between *none* and *value*?) and would invite a future widening to
  admit it. The specification already places this inside (c′) (§6.3), so it is not a
  re-specification.
- **`DN-17-3-5` — ⛔ the fail-closed rule (AC2.4) is part of the GRADER, not of `S1`.** *Rejected:*
  re-adding a `consumed == 0`-shaped clause to `S1` to catch fail-closed tests. That would be the
  loosening-in-reverse the epic forbids and would collapse `S1` back onto the clause-removal
  lattice. The right place is the band: *raising IS the observation*, so the assertion constrains
  the value, so the band is the strongest. **Same `DN-3` reasoning, one level up.**
- **`DN-17-3-6` — ambiguity resolves AWAY from the weakest band.** *Rejected:* the symmetric
  *"unknown ⇒ none"*, which is the accusation direction. The asymmetry is cross-cutting concern
  #6 and it is the only reason a name-level proxy is admissible at all.
- **`DN-17-3-7` — the `existence` ↔ `value` boundary is stated and testable but NOT exhaustive.**
  *Rejected:* a complete Python assertion taxonomy. It carries **no verdict weight in Epic 17**
  (§0.5), it is the boundary 17.2 pre-refused widening into, and building it would consume the
  story that has to get the band-0 boundary right.
- **`DN-17-3-8` — the SUT-call classification gets ONE derivation, shared by fact (b) and the
  grader.** *Rejected:* a second `is_sut` in the new module, however small. That is
  `DF-AUD-DETECT-D`'s defect class, one story later, in the same module, filed by the same
  audit — and this story exists partly to close it.
- **`DN-17-3-9` — the cost record is a deterministic CALL COUNT; no timing enters the suite.**
  *Rejected:* `pytest-benchmark` / a wall-clock ceiling. It converts CI variance into build
  failure and turns an explicitly-not-a-performance-story into one.
- **`DN-17-3-10` — `Evidence-partition: open`, with `pre-seal` disclosed in the commit body.**
  *Rejected:* `none` (false — the design rests on measurements over those five members),
  `sealed` (false the other way), and amending `SEAL_CITATION_VALUES` (named by
  `SEAL_CITATION_RULE` as the corpus-shopping failure mode with an extra step).
- **`DN-17-3-11` — `DF-AUD-DETECT-D` receives its terminal disposition here, and the hand-off to
  17.5 is recorded.** *Rejected:* leaving it open for 17.5's scheduling note, which would leave a
  pointer at completed work — the exact defect class 17.5 exists to end. ⚠️ The closure **verb**
  is written only in the Dev Agent Record, in the same commit as the ledger note (§2.5).
- **`DN-17-3-12` — the guards go in a NEW `tests/test_assertion_strength.py`.** *Rejected:*
  `tests/test_vacuous_density.py` (41 lines of headroom) and `tests/test_vacuous_detector.py`
  (409, but its subject is the detector's scoring contract, not a new module's).
- **`DN-17-3-13` — no `_STATUS_DOCUMENTS` registration, no ruling-index document, no fires
  ledger.** *Rejected:* each, for the reasons already established (§0.11).

### Locked decisions this story CITES rather than reopens

`DN-3` (a SUT call inside a result-observing context is CONSUMED — raising IS the observation) ·
`DN-4` (fact (b) does not depend on the assertion COUNT) · **`DN-14-2-1` / `DN-14-2-4`** (the
two-table split; FROZEN for corroboration, WIDE for breadth) · `DN-14-2-2` (the cross-line string
state lives in the scan) · `DN-15-2-2` (`_score` takes a line list, not a source string) ·
**`DN-16-7-1`** (the silent-class record lives at its own address) · `DN-16-7-2` (the idiom axis
is orthogonal to the disposition) · **`DN-17-1-1`** (the four costs of an `argus/**` byte) ·
`DN-17-1-2` (no protocol amendment) · `DN-17-1-8` (`_STATUS_DOCUMENTS`) · **`DN-17-1-9`**
(`deferred-work.md` writes belong to the story the epic assigns them to) · **`DN-17-2-1`** (the
definition-as-code is 17.3's, and there is exactly ONE authoritative declaration) ·
**`DN-17-2-4`** (`S1`'s reach is not a number until 17.4 measures it) · **`DN-17-2-5`** (the
threshold is pre-refused from widening) · `DN-18-4-2` (the Protocol's read-only-property shape) ·
**`DN-18-4-6`** (the FR10 evidence gap is repository-wide; do not widen one detector) ·
§3.4 evidence immutability · cross-cutting #6 (advisory-by-contract; the conservative default IS
the moat) · `AR4` (no floats; counts, never rendered sets) · `AR7`/§3.3 (one derivation per
question) · `AR8` (pure) · `AR10` (typed/recorded failure) · `AR11` (deterministic ordering) ·
`NFR-D2` · `NFR-R1` · `NFR-M1` · `NFR-P2` (the language conditional stays in `argus/index/`) ·
`NFR-S1` · `DF-8-5-B` (a guard is never weakened to go green) · `AI-E9-7` (constants cited, never
re-typed) · `AI-E9-8` (recording is the story's, filing is the operator's) · `AI-E11-1` (an
absence is evidence only over a population proved non-empty) · `AI-E12-6` (a claimed closure the
ledger never received fails CI) · `AI-E13-1` (a green Windows suite does not predict the ubuntu
matrix).

### Open ledger entries bearing on this story — verify against `deferred-work.md` on disk

| entry | state at contexting | bearing |
|---|---|---|
| `DF-AUD-DETECT-D` | **OPEN**, 🟢 latent, `target_story` **NONE** — *"it rides with whatever story next reworks `provenance_scan`"* | ⛔ **THE ONE ENTRY THIS STORY WRITES.** AC4; a dated, append-only terminal disposition. Re-measured at HEAD (§0.6). |
| `DF-AUD-DETECT-C` | **OPEN**, unscheduled (`AI-E18-10`), 🟡 | AC7 records cost. ⛔ **Not dispositioned, not closed, not edited.** Its folded-in items (`_edges_in_span`'s O(D×E) filter, `secret_scan._line_span`) are **out of scope**. |
| `DF-INV-VACUOUS-A` | **OPEN**, 🟠 | The measured reason Epic 17 exists — *"the assertion-strength half is worth everything"*. ⛔ Landing `S1` advisory does not close it; **17.4** measures. Untouched. |
| `DF-INV-VACUOUS-B` | **dispositioned 2026-08-25 by 17.2** (moot-by-replacement, residual attached) | ⛔ **Do not re-write it.** AC5.2 is what keeps its disposition true: `S1` takes no mock-binding input. |
| `DF-16-7-A` | **OPEN** | *"per-call observation analysis needs real dataflow"* — the resolver §0.7 says must be built here, in the shipped idiom rather than the research script's `ast`. ⛔ Untouched; re-homing is 17.5's. |
| `DF-16-7-B` | **OPEN**, 🟠 | Source of *"a genuinely DIFFERENT predicate … must be argued as one"* and of the 36 → 84 / **48 false accusations** figure that forbids widening the FROZEN table. ⛔ Cited, not written. |
| `DF-14-1-A` | **OPEN** | The signal stays NAME-LEVEL and is a proxy, not dataflow. ⛔ `S1` does not change that and must not claim to. Untouched. |
| `DF-12-2-D`, `DF-12-3-A` | **OPEN** | Re-homing is **17.5's**. ⛔ Untouched. |
| `DF-13-5-A` | **OPEN, UNSPENT**; trigger *"shipped promotions rise above ZERO"*, backstop 2026-11-22 | ⛔ Neither spent nor evaluated here. `S1` promotes **nothing**, so the trigger does not fire on this story. **17.4** evaluates it. |
| `DF-14-3-A`/`-B`/`-C` | **OPEN** | Go/JUnit/Jest test discovery. ⛔ Out of scope; `S1` inherits the blindness. |
| `DF-15-2-B` | **OPEN** | `secret_scan`'s line-decomposition breach. ⛔ Different detector, out of scope. |
| `DF-16-5-A`, `DF-15-2-D`, `DF-15-2-E`, `DF-16-3-A` | **OPEN** | The NFR-M1 headroom class §0.8's pre-registered trigger exists to stop repeating. |
| `DF-8-5-C` | historical | The defect class AC5.4 and AC6.3 exist to prevent: a prose copy of a pinned fact drifting. |
| `DF-INV-MERGE-A` | **OPEN** | A squashed PR reddens `master` after a dogfood regeneration. Record, do not fix. |
| `AI-E16-7` | **UNFILLED** | Not needed here (nothing is adjudicated); **17.4's** precondition. |

### Dependencies — none are added, and that is a requirement

No new third-party dependency, no `pyproject.toml` edit, no lockfile change, no new packaging
extra. The new `argus/` module must import **only** from `argus.detectors.*`, `argus.index.*` and
the standard library (`re`, `typing`, `dataclasses`/`NamedTuple`). ⛔ **No `ast`, no
`tree_sitter`, no `pathlib`, no `os`, no `subprocess`** in the shipped module. The guard module
adds `ast`, `re`, `subprocess`, `pathlib`, `hashlib`, `textwrap` — all already used by
`tests/test_silent_class.py`, `tests/test_vacuous_density.py` and
`tests/test_governance_record_integrity.py`.

⚠️ **No web research is warranted for this story and none was performed. Recorded as
considered-and-declined rather than skipped.** Nothing here depends on a library version, an
external API or a framework release: the stack is CPython 3.10–3.13 with `pytest`, `mypy` and
`bandit`, all pinned by `pyproject.toml`, and the shipped module imports **no third-party code at
all** — it is standard library plus this repository's own helpers. The one place a version fact
would matter is the `isinstance`/`issubclass` behaviour Story 18.4 measured differing between
3.11 and 3.12+, and this story is forbidden from deciding anything by `isinstance` (AC9.9), so
the question does not arise. 17.1 and 17.2 recorded the same, for the same reason.

### Standing rules (non-negotiable)

1. **The shipped module is PURE (AR8).** The guards may shell out to `git` for read-only verbs;
   nothing else does I/O beyond reading committed files.
2. **Counts, never rendered sets** (`NFR-D2` / `AR4`). **No floats**; exact `Fraction` if a ratio
   is ever written.
3. **No source bytes, no secret values, no exception text, no host paths** in any committed
   artifact (`NFR-S1`). ⚠️ §0.9 names the corpus checkout paths **in this story record only**,
   for reproduction; ⛔ they do not go into `argus/**` or the ledger note.
4. **A negative is only evidence if the population was proved non-empty first** (`AI-E11-1`).
5. **§3.4:** nothing already committed is rewritten. Corrections are dated additions.
6. **`DF-8-5-B`:** a guard is never weakened to go green, and a fence is never widened.
7. **A figure is cited with the instrument that produced it and the HEAD it was produced at**, or
   it is not written down.
8. **The tree is shared.** Stage by explicit path; never `git add -A`.

### Project Structure Notes

**Alignment.** Every path this story writes already has a precedent in this tree, and none is a
new kind of thing:

- `argus/detectors/assertion_strength.py` — a **cohesion-boundary sibling** in the
  `argus/pipeline_stages.py` / `argus/pipeline_persist.py` / `argus/detectors/provenance_scan.py`
  lineage: a module docstring naming why the module exists, `__all__` declared, no function split
  across the boundary, and the consumer importing back. `snake_case.py`, ≤1200 lines (NFR-M1).
- `tests/test_assertion_strength.py` — one test module per subject, TC ids in the function names,
  each guard's id on its first docstring line.
- Verification-area continuity: **no new area id.** `DETECT-001` continues at `-147` and
  `PRECISION-001` at `-145`; both are re-derived in §0.0 rather than assumed.

**Variances, each with its rationale:**

- ⛔ **The grader ships in the DETECTOR package even though its consumer-to-be
  (`argus/precision/silent_class.py`) is in `precision/`.** That is not a layering slip — it is
  what `TC-ArgusAgent-PRECISION-001-127` requires: the edge runs `precision → detectors`, one way,
  and putting the predicate the other side of that fence turns the guard RED (§0.3).
- ⛔ **The new module is NOT re-exported from `argus/detectors/__init__.py`.** That file is a
  docstring-only shell whose own text says *"do NOT add them here"*; `secret_scan`, `tool_runner`
  and `orphan_code` are all absent from it too.
- ⚠️ **A guard file is edited (`tests/test_vacuous_cross_language.py`), which this project
  normally forbids.** It is a **population widening plus an id**, never a relaxation, and AC8.3
  carves it out explicitly and requires the diff to be recorded.

### Previous-story intelligence

**Story 17.2 is the immediate predecessor and it is `done`** (arc `5999624` → `126f502` →
`579a342` → `024d330`; code review iteration 1, VERDICT **pass**, Sonnet 5). What carries forward:

- ⛔ **17.2 handed this story FOUR constraints by name** (specification §8.1), and all four are
  reproduced above as §0.3, §0.10, §2.1 and §0.7. **They were written down there precisely
  because here is where they are expensive.** Read §8.1 before Task 1.
- **The §0-before-a-line-is-written discipline.** 17.1's §0 moved three premises; 17.2's moved
  four; this one moved six. ⛔ **Task 0 is not a formality.**
- ⛔ **17.1's one review finding was an unanchored whole-document regex**, fixed **by deletion**
  through the one existing derivation (`DN-17-1-15`, `AR7`). ⚠️ **This story's `-151` and `-152`
  sweep source and generate populations. Anchor every extraction and drive a decoy through it** —
  the same defect class has now appeared twice in this area id.
- **17.2's `-142` planted a decoy OUTSIDE its anchors on every run.** Reuse that shape.
- **17.2 wrote EXACTLY ONE ledger entry** and left the other six for 17.5, *"because splitting a
  re-homing across two stories is how an append-only ledger acquires two half-notes"*. ⛔ **This
  story writes exactly one too.**
- **From 18.1** — a `feat` commit lost a sha to a **forgotten `Evidence-partition:` trailer**.
  17.1 and 17.2 answered by staying out of `DETECTOR_TUNING_PATHS`. ⛔ **17.3 cannot**, and §1.7
  takes the decision instead of discovering it.
- **From 18.4** — the Detector Protocol is load-bearing, decided by `mypy` and a static pin,
  **never by `isinstance`**; and a decoy's `isinstance` verdict differs inside the CI matrix.
- **From 18.3** — a two-token regex repair still needed a full re-measurement of both defects
  before a line was written, and **3 of 4 audit entries were partly wrong on their own premises**.
  ⛔ **`DF-AUD-DETECT-D`'s numbers were already stale at contexting** (§0.6). Re-derive.
- **From 16.7** — `silent_class` is the working model of *"compose the shipped helpers,
  re-implement nothing"*, and `-126`/`-127` are the guards that keep it honest.
- **From 14.1 / 14.2** — every one of this module's past defects was a **second spelling of one
  question**: the assertion table read in two places, the denominator's own line scan, the
  statement-start rule. ⛔ **This story's whole AR7 spine (§1.3) is that history refusing to
  repeat.**

### Git intelligence

```
024d330 docs(17-2): code review iteration 1 (Sonnet 5) - VERDICT PASS; review -> done   <- base
579a342 docs(17-2): disposition DF-INV-VACUOUS-B moot-by-replacement; record the dev round
126f502 docs(17-2): specify the successor vacuity predicate and argue it as a different predicate
5999624 chore(17-2): open the successor-predicate specification story
52ae0e5 fix(17-1): resolve the change-log head through the one existing derivation
f906d04 feat(17-1): pre-register the successor-predicate precision criterion            <- the pin
c2ce00f Merge origin/master into docs/merge-strategy-decision                           <- origin/master
```

Read off that arc and applied above: the epic's **`chore` open → land → `docs` record**
convention is kept and **extended to five commits** (§2.2), because this is the first Epic-17
story writing `argus/**` and it owes both a separate refactor commit (AC4.1) and a separate
dogfood regeneration (AC8.6). The last two commits touching `argus/detectors/**` — `9e3fdc2`
(18.3) and `0ba6a98` (18.4) — both carried `Evidence-partition: none`; §1.7 explains why this
story's value differs.
⚠️ The branch is **8 ahead of `origin/master`** and `audit-ci.yml` triggers on `master`/`main`
only, so **no CI evidence is available for this work at its own sha** (`AI-E13-1`; epic-18 retro
SD-4). ⚠️ **CI runs an ubuntu matrix on 3.10/3.11/3.12 and a green Windows suite has previously
shipped POSIX-only defects** (§2.7).

### References

- `…/epics.md:3400`–`3489` — Epic 17 charter, the `consumed == 0` constraint, the BINDING
  ORDERING CONSTRAINT, the operator approval; **Story 17.3's five ACs at `:3510`–`:3545`**
- `…/successor-vacuity-predicate-specification.md` — **§2.1** (`S1`'s three conjuncts), **§2.2**
  (the threshold, pre-refused from widening), §2.3 (the defect shape), §2.4 (`S1` is not a `V`),
  §3 (the two-directional differential), **§3.2** (the rejected successors, incl. the 36 → 84
  measurement), **§4** (the two instruments; the resolver does not exist), §5 (what 17.2 did not
  do), **§6.3** (the moat is preserved by shape — the NFR-R1 refusal), **§6.5** (advisory until
  an operator says otherwise), §7.3 (mock binding is not an input), **§8.1** (⛔ the four
  constraints handed to this story by name)
- `…/successor-predicate-precision-preregistration.md` — §2 (the criterion), §3.5 (`AI-E16-7`),
  §5 (hand-off to 17.4); `SUCCESSOR_OUTPUT_PATHS`
- `…/stories/17-2-a-different-predicate-argued-as-one.md` — §0.2 (the two tables), §0.3 (the V2
  half already ships), **§0.4** (the `-127` fence), §0.5 (the two instruments), §0.6 (the one
  `mref` decision site), §2.1 (the four costs), `DN-17-2-1`..`-10`
- `…/deferred-work.md` — **`DF-AUD-DETECT-D`** (`:6630`, with the *"suggested repair is a
  deletion"* sentence), `DF-AUD-DETECT-C` (`:6600`), `DF-INV-VACUOUS-A` (`:6191`),
  `DF-INV-VACUOUS-B` (`:6240`), `DF-16-7-A` (`:5721`), `DF-16-7-B` (`:6140`), `DF-14-1-A`
  (`:4481`), `DF-13-5-A` (`:4717`); the `DF-AUD-DETECT-E`/`-F` closure-note shape
- `…/research/technical-argusagent-stage-mismatch-measurement-2026-08-24.md` §2, §4 (the two
  stages; `density_only` 1,025 of 1,032), §5 (the `V0`..`V5` table and the two charter
  constraints)
- `…/research/investigate-per-call-scoping.py:9`–`:24` (the variant definitions), **`:79`–`:137`**
  (`sut_unrelated_assertions` — ⛔ the `ast`-based resolver that may NOT be ported), `:55`
  (`CHECKOUTS`)
- `…/precision-validation-protocol.md` §2 (roles; `UNADJUDICATED` is the only member an automated
  producer may write), §4 (the ladder; step 3 unfilled), §5, §7 (OI1)
- `…/epic-18-retro-2026-08-25.md` **SD-1** (the detector-contract obligation), **SD-2** (Epic 17's
  premise survived 18.3/18.4), **SD-4** (evidence is local/unpushed)
- `…/architecture.md:1132` **GUARD-ADEQUACY CLAUSE** · `:1140` **Ledger-claim cross-check** ·
  the **Vacuity-corroboration enforcement** rule · `:1150` **Ruling-index** (do not create it)
- `argus/detectors/vacuous_test.py` — the module docstring's *"Why fact (b) is not
  `mock_sites >= 1`"* and *"Why there are TWO assertion vocabularies"* sections · `:464`
  (`_edges_in_span`) · `:530` (`index_aligned_lines`, the line-numbering contract) · `:689`
  (`_score`) · `:737` (`_sut_call_sites`) · **`:754`–`:796`** (`_ast_corroborated`, and `:796`
  is the line that must not move) · `:799` (the conformance pin)
- `argus/detectors/provenance_scan.py` — the platform-neutrality contract in the docstring ·
  `:119` (`RESULT_OBSERVING_CONTEXT_CALLEES`) · `:155`/`:169`/`:172`/`:176` (the anchored
  patterns) · `:206` (`opens_bare_assert`) · `:247`/`:256` (`_code_prefix` /
  `_continued_code_prefix` — ⛔ `pending=None` is the divergence's mechanism) · **`:345`**
  (`_logical_statement_end` — the deletion) · **`:377`** (`_scan_span` — the one derivation) ·
  `:606` (`logical_statement_starts` — the projection idiom) · `:653` (`_locate_call`) · `:760`
  (`_result_observing_lines`) · **`:794`** (`_mock_bound_names` — the resolver's mirror) ·
  `:832` (`ProvenanceEvidence`) · `:849` (`_assertion_statement_lines`) · **`:872`**
  (`provenance_evidence`, whose loop at `:912`–`:965` is where the SUT classification is
  computed and discarded)
- `argus/detectors/vacuous_vocabulary.py` — `_ASSERTION_CALLEES` (89), `_CORROBORATION_ASSERTION_CALLEES`
  (23), `_MOCK_CALLEES` (10), `_ASSERTION_NAMING_CONVENTION` (`\A_?assert\w*\Z`),
  `is_assertion_callee`
- `argus/detectors/base.py:147`–`:190` (the `Detector` Protocol) · `argus/detectors/__init__.py`
  (⛔ the *"do NOT add them here"* shell)
- `argus/precision/silent_class.py:106` (`SILENT_CLASS_DEFINITION`), `:217`–`:333` (`SpanScore`,
  `span_asserts_anything`, `span_provenance`, `score_span`), `:126` (`UnregisteredIdiom`), `:191`
  (`idiom_meaning`)
- `argus/precision/gate_seal.py:280` (`DETECTOR_TUNING_PATHS`), `SEAL_CITATION_RULE`,
  `SEAL_CITATION_VALUES`, `member_partitions`
- `scripts/build_silent_class_record.py` (the 1,032 harness; `--check --checkout-root`) ·
  `scripts/regenerate_dogfood_artifacts.py` · `scripts/precision_preregistration.py`
- `tests/test_silent_class.py:457` (`-126`), **`:525` (`-127`)**, `:601` (`-128`) ·
  `tests/test_detector_base.py:224` (`-145`), `:257` (`-146`) ·
  `tests/test_gate_seal.py:916` (`-93`), **`:1035` (`-94`, the trailer's real-history loop)** ·
  `tests/test_dogfood_artifact_currency.py` (`-49`..`-52`) ·
  `tests/test_module_size_ceiling.py` (`_EXEMPT_BY_DESIGN`, `_REMEDY`) ·
  `tests/test_governance_record_integrity.py:198` (`-78`) ·
  `tests/test_vacuous_density.py` (⛔ 41 lines of headroom) · `tests/test_vacuous_cross_language.py`
  (the `^`/`$` anchor sweep) · `tests/test_precision_preregistration.py` (`-139`, `-140`)
- `…/validation-corpus/adjudication-set-13-5.json` (the 1,032 and the five pins) ·
  `…/validation-corpus/silent-class-record.json`
- `…/E-PRD/prd.md:507` (FR7), `:527` (FR10 — *"advisory findings carrying their evidence
  counts"*), FR34, the ≥80% keystone

---

## Tasks & Subtasks

### ⛔ Task 0 — RE-MEASURE §0 BEFORE WRITING ANYTHING (AC1, AC4.2, AC10.1)

0.1 Confirm HEAD, branch, clean tree, and the `origin/master` distance.
0.2 Re-size the three vocabularies **by import**; re-confirm all nine
`RESULT_OBSERVING_CONTEXT_CALLEES` are in the WIDE table and only two in the FROZEN one (§0.4).
⛔ **If that has changed, the fail-closed trap has changed shape — escalate.**
0.3 Re-walk `-127`'s closure: module count, fenced count, and that it is green today.
0.4 ⛔ **Re-measure `DF-AUD-DETECT-D`'s divergence with both implementations** over the tracked
`argus/**` + `tests/**` files; record files / statements / divergences / rate (§0.6). ⛔ **Do not
quote the ledger's figures.**
0.5 Re-derive every module and test-module line count from the git index; **project each touched
module's final size** and apply §0.8's pre-registered split trigger.
0.6 Re-count the 1,032 out of `adjudication-set-13-5.json` per member; probe all five pinned shas
with `git cat-file -e`. ⛔ Any unreachable pin is **AC10.7**.
0.7 Re-verify both `SUCCESSOR_OUTPUT_PATHS` prefixes are **ABSENT**; re-verify
`scripts/precision_preregistration.py` matches its `f906d04` pin in every frozen field.
0.8 Re-count `deferred-work.md`'s CR byte and `sprint-status.yaml`'s 1,264/1,264.
0.9 Read **specification §8.1** in full and restate its four constraints in the Dev Agent Record.
0.10 Record the full-suite baseline (collected / passed / failed / skipped, exit code) **before**
any edit.

### Task 1 — THE COLLAPSE, ALONE AND FIRST (AC4, AC9.5, AC9.6)

1.1 Capture the **pre-change** 1,032-harness output: `scripts/build_silent_class_record.py --check
--checkout-root <root>`; record exit code and the sha256 of both committed artifacts.
1.2 Replace `_logical_statement_end` with a **projection of `_scan_span`** — the last line whose
`opens == s` — and delete the old function. Update both call sites (`:941`, `:971`).
⛔ **No third function.**
1.3 Re-derive the entry's stage (ii): re-score fact (b) over the repository's own test functions
with the new extent; record **evidence differences** and **corroboration flips** (expected 0 / 0).
1.4 Re-derive stage (iii): build the synthetic trigger — a SUT call whose logical statement opens
an unterminated triple-quote at depth 0 — and record that both extents yield identical
`ProvenanceEvidence`.
1.5 Re-run the 1,032 harness; ⛔ **assert both artifacts byte-identical** (AC4.3). A difference is
**AC10.2**.
1.6 Write `TC-ArgusAgent-DETECT-001-152` (the string-state property, generated population with its
count) and `TC-ArgusAgent-DETECT-001-151`'s statement-extent half.
1.7 Full suite + `mypy argus` + `bandit`; **commit A** with `Evidence-partition: open`.

### Task 2 — THE SCALE, THE RESOLVER AND THE GRADER (AC1, AC2, AC3, AC5)

2.1 Create `argus/detectors/assertion_strength.py` with the closed ordered scale, its meanings,
`UnregisteredStrength`, and the direction-of-harm paragraph (§0.5) written where the next author
reads it.
2.2 Build the **SUT-derived name resolver** in `_mock_bound_names`' idiom (§0.7) — one forward
pass, transitive, `with … as` handled, unreadable ⇒ **unbound**.
2.3 Expose the **ONE** SUT-call classification so fact (b) and the grader read the same answer
(§1.3, AC4.6). ⛔ `ProvenanceEvidence`'s three counts must be **byte-identical** afterwards —
re-run Task 1.5's comparison.
2.4 Grade each assertion statement, reading the **WIDE** vocabulary for the population (§1.5) and
`_result_observing_lines` for the fail-closed rule (AC2.4). Return **counts** plus `unestablished`.
2.5 Implement `S1` as the three conjuncts, citing the specification's section rather than
re-arguing it (AC5.4).
2.6 Compose it into `vacuous_test.py` as **evidence only** — ⛔ `:796` unchanged, `rule_id` and
`depth_supported` still driven by `score.ast_corroborated` alone (§1.4). Measure whether the score
model's new field needs a default before adding it (§1.4.6), and record the §1.4.5 decision.
2.7 Re-project module sizes against §0.8's trigger; record.

### Task 3 — THE GUARDS (AC9)

3.1 `tests/test_assertion_strength.py` with `-147`, `-148`, `-149`, `-150`, the `is_sut` half of
`-151`, `PRECISION-001-145` and `PRECISION-001-146`.
3.2 ⛔ **Each guard is driven RED at its REAL seam by an EXECUTED mutation**, and the mutated file
is restored **byte-exact, verified by sha256**. Record each observation.
3.3 ⛔ **`-149` generates one fixture per member of `RESULT_OBSERVING_CONTEXT_CALLEES` and asserts
the count is 9**, with each fixture's non-vacuity floor asserted first.
3.4 ⛔ Every guard asserting an absence states its non-vacuity floor **first** (`AI-E11-1`).
3.5 ⛔ **Widen the `^`/`$` anchor sweep's population to `argus/detectors/**`** and give it
`TC-ArgusAgent-DETECT-001-153` (AC9.11, §2.7). ⛔ **Widen, never fork; remove no assertion.**
Record the diff of `tests/test_vacuous_cross_language.py` explicitly (AC8.3).

### Task 4 — THE COST RECORD, AND PROVE NOTHING MOVED (AC6, AC7, AC8.2)

4.1 Measure span-scan cost **before and after** as a deterministic call count over a fixed in-repo
population; report wall-clock beside it, labelled advisory, with host OS and Python version
(§1.6). ⛔ **No assertion, no threshold, no benchmark in the suite.** ⛔ `DF-AUD-DETECT-C` untouched.
4.2 Re-run the 1,032 harness a final time; record `vacuous_test_ast` still **0** and the flagged
population unchanged (AC6.2).
4.3 Record the AC8.2 empty diffs verbatim; assert both `SUCCESSOR_OUTPUT_PATHS` still absent;
confirm `-127`, `-140`, `-142`..`-144`, `-145`/`-146`, `-22`, `-78`, `-93`/`-94` green **and
unedited**.
4.4 ⛔ **Sweep this story's own committed text for a reach figure** (AC6.3) before writing the
record.
4.5 Every gate with its exit code, labelled **LOCAL (Windows)**; **commit B** with
`Evidence-partition: open`.

### Task 5 — REGENERATION, LEDGER, RECORD (AC4.7, AC8)

5.1 `python scripts/regenerate_dogfood_artifacts.py`; verify `tests/test_dogfood_artifact_currency.py`
green; **commit C** alone, citing a provenance sha that is an ancestor of HEAD.
5.2 Grep `deferred-work.md` for prior art; append the **dated, append-only** `DF-AUD-DETECT-D`
disposition in **binary** mode; verify the 1-CR invariant and that the entry above is
byte-unchanged.
5.3 Write this story's record: Task 0's re-measured §0, the guard-RED observations, the
neutrality evidence, the cost record, the gate table, the write set, the §2.5 hand-off note to
17.5, and the §1.7 trailer-vocabulary observation.
5.4 `sprint-status.yaml`: `in-progress` → `review`, surgically; verify 1,264/1,264.
5.5 **Commit D** — ledger note + story record + sprint-status **together** (`-78`).
5.6 ⛔ **Post-write check:** re-run the full suite **after** the story record is written; confirm
`TC-ArgusAgent-DOCS-001-78` and `-22` are green.

---

## Dev Agent Record

### Agent Model Used

`bmad-dev-story` (Opus 5, 1M context), round 1 — `mode: implement`. LOCAL, Windows 10 /
CPython 3.11.15. Baseline `024d330`; the arc landed `4336d48` (O) → `2db5ce0` (A) →
`90b5235` (B) → `8516297` (C) → this record (D).

### Debug Log References

⛔ **§0 RE-MEASURED BY EXECUTION AT `024d330` BEFORE A LINE WAS WRITTEN (Task 0).** Every row
reproduced. Nothing was adjusted.

| §0 row | story says | re-measured | verdict |
|---|---|---|---|
| HEAD / branch / distance | `024d330`, `docs/merge-strategy-decision`, 8 ahead | identical | ✅ |
| tree at contexting | clean | the 17-3 story file + the `sprint-status.yaml` edit were the only uncommitted paths | ✅ |
| FROZEN / WIDE / MOCK / observing tables | 23 / 89 / 10 / 9 | 23 / 89 / 10 / 9, by import | ✅ |
| §0.4 the fail-closed trap | 9 of 9 observing callees in WIDE, 2 of 9 in FROZEN | 9 of 9 WIDE and `is_assertion_callee`-true; `assertRaises`, `assertRaisesRegex` the only two FROZEN | ✅ |
| §0.3 `-127`'s fence | 95 `argus/**` modules, ≥12 fenced, green | green; the walk parses 95 and the fenced set is 20 | ✅ |
| §0.6 `DF-AUD-DETECT-D` | 232 files / 31,845 statements / 1,890 divergences / 5.93% | **232 / 31,845 / 1,890 / 5.93%** | ✅ |
| §0.8 module sizes | `provenance_scan` 976 · `vacuous_test` 807 · `vacuous_vocabulary` 534 · `silent_class` 944 · `test_vacuous_density` 1,159 · `test_vacuous_detector_index` 1,065 · `test_vacuous_cross_language` 1,033 · `test_vacuous_detector` 791 · `test_silent_class` 698 | identical, from the git index | ✅ |
| §0.9 the 1,032 | minions 648 · agent-smith 295 · agent-markovich 72 · xagents-webapp 17 · ai-body-runtime 0; 4,284 total | identical, re-counted out of `adjudication-set-13-5.json` | ✅ |
| §0.9 pinned shas | 5 of 5 reachable | 5 of 5 by `git cat-file -e`, including `agent-smith` at the depth-5 path | ✅ |
| §0.0 `SUCCESSOR_OUTPUT_PATHS` | both ABSENT | both absent; `PREREGISTRATION_COMMIT_SHA` = `f906d04…`, `precision_preregistration.py` byte-unchanged | ✅ |
| §0.0 byte invariants | `deferred-work.md` 1 CR · `sprint-status.yaml` 1,264/1,264 | `deferred-work.md` 593,897 B / 1 CR / 7,534 LF / 0 CRLF; `sprint-status.yaml` 1,264 lines / 1,264 CR | ✅ |
| §0.10 full-suite baseline | — | **1,741 passed, 0 failed, exit 0**, 251 s | recorded |

**Specification §8.1's four constraints, restated (Task 0.9):** (1) `-127` fences the detector
package and `argus/precision/gate_*.py` out of `silent_class.py` transitively — the `S1` scorer
cannot import `silent_class`, and the fence is never widened; (2) `-145` reddens the moment a
fifth class defining `run() -> DetectorResult` is written until its `if TYPE_CHECKING:` pin
lands, and no Epic-17 guard may decide conformance by `isinstance`/`issubclass`; (3) the
`Evidence-partition:` trailer is owed by every commit touching `argus/detectors/**`; (4) the
SUT-derived name-binding resolver does not exist and 17.3 must build it, plus the three other
costs of an `argus/**` byte. All four were honoured — (1) by placing the module on the detector
side of the fence, (2) by adding no detector class, (3) on both `argus/detectors/**` commits,
(4) built in `_mock_bound_names`' idiom.

⛔ **THE `DF-AUD-DETECT-D` NEUTRALITY EVIDENCE, re-derived and never quoted (AC4.2/AC4.3).**

| stage | instrument | result |
|---|---|---|
| (i) divergence, at HEAD | both implementations over every tracked `argus/**` + `tests/**` file | 232 files / 31,845 statements / **1,890 divergences (5.93%)** |
| (ii) reachability through the shipped scorer | fact (b) re-scored over the repository's own test functions with both extents, through the real 1.4 index | **1,568 test functions · 0 evidence differences · 0 corroboration flips** |
| (iii) synthetic triggers | three purpose-built for the string-state gap: a SUT call opening a multi-line literal, an assertion statement opening one, docstring prose carrying an unbalanced bracket | **identical `ProvenanceEvidence` from both, 3 of 3.** ⚠️ A fourth — an unterminated literal at span end — is refused by the 1.4 index itself (`parse_failed`) and can never reach a detector; recorded because it BOUNDS the exploit attempt |
| the 1,032 | `scripts/build_silent_class_record.py --check --checkout-root <root>`, **before** and **after** | exit **0** both; `silent-class-record.json` sha256 `f784df6305c23aef…` and `silent-class-worklist.md` sha256 `cd3cb2933bfe7321…` **BYTE-IDENTICAL**; class=36, by member `{agent-smith: 22, minions: 14}`, all UNADJUDICATED |

⛔ **LOCAL (Windows) measurement.** No committed test requires the five checkouts (AC4.4).
⛔ It ratified nothing, adjudicated nothing and wrote nothing to any corpus member (AC6.5).

⛔ **GUARD-RED OBSERVATIONS — every guard driven RED at its REAL seam by an EXECUTED mutation.**
⚠️ **No mutation touches disk**, because the tree is shared with a peer session (§2.6); each one
mutates the REAL module's committed source TEXT or a live module attribute, drives the SAME
predicate over it, and re-asserts the file's on-disk sha256 afterwards.

| guard | observable | executed mutation | RED? |
|---|---|---|---|
| `-147` | the vocabulary, its order, each meaning, the refusal | an offender GENERATED from the live vocabulary (its members concatenated) driven through both accessors | ✅ raises `UnregisteredStrength` |
| `-148` | AST walk over the grader's own source: imports, call targets, module-level statements | `import ast` planted into the real module's text | ✅ the walk sees it |
| `-149` | the graded band and `S1`'s verdict for a fail-closed span, **one fixture per member, count asserted == 9** | `_OBSERVING_CALL_RE` replaced by a never-matching pattern | ✅ false accusations appear |
| `-150` | `unestablished` and `S1` over **100 GENERATED malformed spans** (5 line lists × 4 edge lists × 5 bounds) | — (the population IS the adversary; every variant refused, none raised) | n/a |
| `-151` | `_bracket_delta`'s callers, and the `is_sut`-shaped filter, swept over `argus/**` | the deleted `_logical_statement_end` planted back; a second `is_sut` planted into `assertion_strength.py`'s text | ✅ both seen |
| `-152` | the extent of a statement opening a multi-line literal, over 95 modules / 8,285 statements / 2,212 multi-line / 728 literal-opening | `_continued_code_prefix` replaced by a string-state-blind version | ✅ the extent moves |
| `PRECISION-001-145` | the three conjuncts falsified ONE AT A TIME | one widening variant per band above `none`, count asserted == 2 | ✅ each changes the verdict |
| `PRECISION-001-146` | the return expression as a PARSED AST expression; both output prefixes; this story's commits over the fenced paths | the expression mutated (`>= 1` → `>= 0`) and compared | ✅ distinguished |

⛔ **NON-VACUITY IS ASSERTED FIRST IN EVERY ONE** (`AI-E11-1`): the sweeps assert a module floor
AND resolve their KNOWN derivation before asserting an absence; `-149`'s fixtures assert
`discarded_sut_calls >= 1` and ≥1 graded assertion first; `-145` exhibits a span `S1` ACCEPTS
before asserting any refusal; `-146` asserts a control pathspec is NON-empty before asserting the
fenced ones are empty.

⛔ **SPAN-SCAN COST RECORD (AC7) — a deterministic CALL COUNT, wall clock ADVISORY beside it.**
Fixed in-repo population: 4 files, 47 scored test functions, 8 heuristically flagged.
Instrumentation lives in the measurement harness only and never in shipped code.

| counter | before (`024d330`) | after | per scored function |
|---|---:|---:|---|
| `_scan_span` | 55 | 63 | 1.2 → 1.3 |
| `_code_prefix` | 1,470 | 1,167 | 31.3 → 24.8 |
| `_continued_code_prefix` | 4,123 | 4,085 | 87.7 → 86.9 |
| `_blank_strings` | 4,408 | 4,365 | 93.8 → 92.9 |
| **TOTAL** | **10,056** | **9,680** | **214.0 → 206.0** |

**A 3.7% REDUCTION, and no regression to escalate.** It comes from the collapse: the deleted
function walked `_code_prefix` per line per call site. The grading contributes **nothing** to
`run()`'s path, because `S1` is off it (§1.4.5's decision, below). Wall clock 0.07 s before and
after — ⚠️ **ADVISORY only**, LOCAL Windows 10 / CPython 3.11.15, and not the ubuntu matrix.
⛔ **No timing assertion, no invocation-count threshold and no benchmark entered the suite, and
`DF-AUD-DETECT-C` is NOT dispositioned, closed or edited** (AC7.2/AC7.3).

⛔ **THE GATE TABLE — every figure LOCAL (Windows).** `audit-ci.yml` triggers on `master`/`main`
only and this branch is unpushed, so **no CI evidence exists at any sha in this arc**
(`AI-E13-1`).

| gate | command | result at commit D |
|---|---|---|
| full suite | `pytest` | see below |
| types | `mypy argus` | **Success, 96 source files** |
| security | `bandit -r argus --severity-level medium` | clean, exit 0 |
| coverage | `pytest --cov=argus --cov-fail-under=80` | **95.84%** — `assertion_strength.py` 94%, `provenance_scan.py` 99%, `vacuous_test.py` 98% |
| module size | `tests/test_module_size_ceiling.py` | green |
| dogfood currency | `tests/test_dogfood_artifact_currency.py` (`-49`..`-52`) | green after commit C |
| ledger cross-check | `tests/test_governance_record_integrity.py` (`-78`, `-22`) | green |
| the 1,032 | `scripts/build_silent_class_record.py --check --checkout-root <root>` | exit 0, artifacts byte-identical |

⚠️ **RECORDED HONESTLY: commits `4336d48`, `2db5ce0` and `90b5235` each carry a RED local suite**
— `tests/test_dogfood_plan.py`, `tests/test_dogfood_proof.py` and (from `90b5235`)
`tests/test_dogfood_artifact_currency.py::…-50`. That is not a defect; it is what §2.1's *"its
OWN commit, after the last `argus/**` byte lands"* costs. Commit `8516297` regenerates and all
four go green. A reviewer checking any intermediate sha will see it, so it is disclosed here
rather than discovered there.

### Completion Notes List

⛔ **`DF-AUD-DETECT-D` is CLOSED by this story**, at fix sha `2db5ce0`, and its dated,
append-only disposition lands in `deferred-work.md` in this same commit
(`TC-ArgusAgent-DOCS-001-78` closes in both directions, so the claim and the disposition cannot
be separated). The entry above it is byte-unchanged and the file's **1-CR invariant holds**
(597,097 → 602,265 bytes, 1 CR before and after, 0 CRLF, pure append: 54 insertions, 0 deletions).

⛔ **THE HAND-OFF TO STORY 17.5, RECORDED EXPLICITLY (§2.5).** Story 17.5's AC says it will point
`DF-AUD-DETECT-D` *"at this epic's Story 17.3 — scheduling notes only"*. That entry now holds a
TERMINAL disposition, so a scheduling note would point at completed work — precisely the defect
class 17.5 exists to end. ⛔ **17.5 must write a DISPOSITION POINTER naming this note's sha
instead of a schedule.** The ledger note says so in its own words too.

⛔ **EXACTLY ONE LEDGER ENTRY WAS WRITTEN.** `DF-AUD-DETECT-C`, `DF-INV-VACUOUS-A`,
`DF-INV-VACUOUS-B`, `DF-16-7-A`, `DF-16-7-B`, `DF-14-1-A`, `DF-12-2-D`, `DF-12-3-A`,
`DF-13-5-A`, `DF-14-3-A`/`-B`/`-C`, `DF-15-2-B`, `DF-16-5-A`, `DF-15-2-D`/`-E`, `DF-16-3-A` and
`DF-INV-MERGE-A` all keep the status they had; the six re-homings and the four Epic-18 scheduling
notes remain Story 17.5's (`DN-17-1-9`). ⚠️ `DF-INV-MERGE-A` was closed at `8715b7f` by the PEER
session sharing this branch, not by this story.

⛔ **NOTHING FLIPPED, AND NOTHING WAS PUBLISHED.** `vacuous_test.py`'s `_ast_corroborated` return
expression is unchanged as a parsed AST expression; no finding's `verdict_eligible`, `rule_id` or
`depth_supported` moves; neither `SUCCESSOR_OUTPUT_PATHS` prefix exists; `validation-corpus/**`,
`scripts/`, `argus/precision/`, `argus/detectors/base.py`, the specification document, the
protocol, `epics.md`, `architecture.md` and `E-PRD/` are byte-unchanged across all four commits
(proved by `git show --name-only` per commit over those pathspecs, with `argus/detectors` as a
control asserted NON-empty). ⛔ **No reach figure for `S1` is written anywhere in this story's
committed text** (swept before writing this record): the guard counts here — 9, 2, 3, 100, 47 —
are guard fixtures and population sizes, not a sentence of the form *"`S1` reaches N over the
corpus"*. **17.4 measures it, once.**

⛔ **`DF-13-5-A` NOT SPENT.** No member ratified, no third-party source fetched, no round
consumed, branch (a) not executed, branch (b) not declared. The externalization gate stays
`BLOCKED`, `protocol_cleared` stays `False`, FR34's disclosure stands.

#### §1.7 — the `Evidence-partition:` trailer, and the vocabulary gap (an OBSERVATION, not a filing)

Both `argus/detectors/**` commits (`2db5ce0`, `90b5235`) carry **`Evidence-partition: open`**, and
each commit body states that the five ratified members are partitioned **`pre-seal`**. ⚠️ **The
trailer vocabulary `SEAL_CITATION_VALUES` is closed at (`sealed`, `open`, `none`) and carries no
`pre-seal`.** `none` would be false — the grading scale, `S1`'s shape and the epic's premise all
rest on measurements taken over those members. `sealed` would be false the other way. ⛔ Amending
`SEAL_CITATION_VALUES` was refused: `SEAL_CITATION_RULE` names that move by name as *"the
corpus-shopping failure mode with an extra step"*. The gap is **recorded here as an observation**;
⛔ **no new ledger id is filed for it without an operator act** (`AI-E9-8`). `deferred-work.md`
was grepped first and holds no entry for it.

#### §1.4.5 — computed for which spans, ANSWERED rather than left to a short-circuit

⛔ **`S1` is computed for NEITHER *"every scored span"* NOR *"only the flagged ones"*: it is
computed ON DEMAND, off `run()` entirely**, through `VacuousTestDetector.successor_evidence(...)`.
The reason is measured, not stylistic: §1.4.4 forbids widening `FindingDraft`, `DetectorResult`
or `Recording`, so the evidence has **nowhere to travel to** — wiring it into `_score` would buy
a second full span scan on the flagged path to produce a value that is then discarded. Story
17.4's measurement is unaffected either way (the 1,032 are all heuristic findings and the method
scores any span it is given), and `run()`'s behaviour AND cost are provably unchanged, which is
what AC6.2 actually wants. The FR10 evidence-plumbing gap stays **OPEN** and repository-wide
(`DN-18-4-6`).

#### ⛔ THREE DIVERGENCES FROM THE STORY SPEC, each measured and none silent

- **`DN-17-3-14` — the evidence lands on a SIBLING model, not on `VacuousTestScore`.** §1.4.3
  offered both and §1.4.6 asked for a measurement before choosing; §1.4.6 measured only the four
  modules that CONSTRUCT the score. ⛔ **The binding constraint is different and was found by
  execution: `TC-ArgusAgent-DETECT-001-119` (`tests/test_vacuous_density.py:860`) pins
  `set(VacuousTestScore.model_fields)` EXACTLY**, so a field with a default reddens it just as a
  required one does. Widening the score therefore means editing a GREEN guard, in a file outside
  AC8.1's write set, to keep it green — `DF-8-5-B` outright. `SuccessorVacuityEvidence` lands
  beside `VacuousTestScore`, frozen, `extra="forbid"`, counts only, no `float`. ⚠️ The same shape
  of pin was hit a second time: `TC-ArgusAgent-DETECT-001-143` pins `vacuous_test.__all__` at
  NINE entries, so the new class is imported by path and is not re-exported. *Rejected:* editing
  either guard; *rejected:* dropping the composition, which Task 2.6 requires.
- **`DN-17-3-15` — the `^`/`$` anchor sweep keeps `TC-ArgusAgent-DETECT-001-130`; `-153` is NOT
  minted.** AC9.11 says the sweep *"has none today"*. ⛔ **Measured: false.**
  `test_provenance_scan_anchors_no_pattern_with_caret_or_dollar` carries
  `TC-ArgusAgent-DETECT-001-130` on its FIRST docstring line (what it lacks is the id in its
  function NAME, and renaming it would SHRINK the test-name population AC8.3 forbids shrinking).
  Its POPULATION is widened to `argus/detectors/**` exactly as required — ⛔ never forked, no
  assertion removed, relaxed or narrowed, both positive controls still driving
  `_anchors_on_caret_or_dollar` to BOTH outcomes, and a `provenance_scan.py`-specific
  non-vacuity floor kept beside a new package-wide one. Diff recorded per AC8.3: **+45 / −12,
  one hunk, one function**. ⛔ Giving one guard two ids is how a verification area acquires an
  untraceable duplicate, so `-153` stays unallocated for the next detector guard.
- **`DN-17-3-16` — AC10.9 ESCALATION, RECORDED AND THEN DISCHARGED MECHANICALLY: a FIFTH cost of
  an `argus/**` byte that §0.10 did not count.** `TC-ArgusAgent-DOCS-001-54` closes in BOTH
  directions over `README.md` and `CHANGELOG.md` against a **freshly built wheel**, and a new
  `argus/` module moves three published figures. ⛔ The story cannot be completed without touching
  two files outside AC8.1's write set — which is AC10.9 by its own terms, so it is stated here
  rather than absorbed. It was discharged rather than halted on because the guard names its own
  remedy in its own failure message (*"Fix the document — the artifact is the fact"*), the only
  alternative is weakening a green guard (`DF-8-5-B`), and the change decides nothing about the
  predicate: **95 → 96 importable/shipped modules, 103 → 104 wheel entries, 102 → 103 sdist
  files**, plus the one-paragraph module note in `README.md`'s established form. ⛔ **Both files
  are an ADDITION to AC8.1's write set and a reviewer should treat them as such.** Byte
  invariants: both are CRLF files and stayed so (`README.md` 449 → 455 CRLF; `CHANGELOG.md`
  1,181 CRLF unchanged).

#### Decisions taken as specified, confirmed by execution

`DN-17-3-1` (new module on the detector side of the `-127` fence — the fence is green and
UNEDITED, and the walk now covers 96 modules / 21 fenced, both above their floors) ·
`DN-17-3-2` (no new detector class; `-145`'s four `if TYPE_CHECKING:` pins are untouched) ·
`DN-17-3-3` (the collapse first, alone, in `2db5ce0`, and it is a DELETION plus a projection) ·
`DN-17-3-4` (`unestablished` is a COUNT, and `S1` refuses on it — driven by `-150`) ·
`DN-17-3-5` (the fail-closed rule is in the GRADER, not in `S1`; no `consumed == 0`-shaped clause
was re-added) · `DN-17-3-6` (ambiguity resolves AWAY from the weakest band — the grader asks the
SUT-call classification with an EMPTY mock-name set, which is both §7.3's requirement and the
conservative direction) · `DN-17-3-7` (the `existence` ↔ `value` boundary is stated and testable,
not exhaustive) · `DN-17-3-8` (ONE `is_sut` derivation, `candidate_sut_edges`, and `-151` asserts
all THREE consumers read it) · `DN-17-3-9` (a deterministic call count; no timing in the suite) ·
`DN-17-3-10` (`Evidence-partition: open`, `pre-seal` disclosed in the body) · `DN-17-3-11`
(terminal disposition here, hand-off to 17.5 recorded) · `DN-17-3-12` (guards in a new module —
and then SPLIT, below) · `DN-17-3-13` (no `_STATUS_DOCUMENTS` registration, no ruling-index
document, no hand-written fires ledger).

#### NFR-M1 — §0.8's PRE-REGISTERED trigger applied at Task 1 and again at Task 2.7

| module | before | projected/after | trigger |
|---|---:|---:|---|
| `argus/detectors/provenance_scan.py` | 976 | **1,086** | none (<1,100) — an intermediate draft projected **1,166**, above the 1,150 line, and was brought under 1,100 by tightening the ADDED docstrings and merging a redundant wrapper. ⛔ No committed measurement or prose was deleted; the `DF-AUD-DETECT-D` figures moved into the projection's own docstring and this record |
| `argus/detectors/vacuous_test.py` | 807 | **897** | none |
| `argus/detectors/assertion_strength.py` | — | **480** | none |
| `tests/test_assertion_strength.py` | — | **1,212 projected** | ⛔ **ABOVE 1,150 → SPLIT FIRST**, per §0.8, before review could discover it |
| ↳ after the split | — | **1,002** + `tests/test_successor_predicate_s1.py` **269** | none |
| `tests/test_vacuous_cross_language.py` | 1,033 | **1,066** | none |

⛔ **The split is along the seam the story is built on** — the SCALE and the GRADER in one module,
the PREDICATE and the *"nothing flipped"* evidence in the other — and the second module **IMPORTS
the first's fixture plumbing rather than copying it**, which is exactly the
`tests/test_silent_class.py` / `tests/test_silent_class_record.py` pair's shape. ⛔ **No
`_EXEMPT_BY_DESIGN` entry was added** and shaving was refused as a remedy.

#### The write set, verified by `git status --porcelain` before every commit

`argus/detectors/provenance_scan.py` · **NEW** `argus/detectors/assertion_strength.py` ·
`argus/detectors/vacuous_test.py` · **NEW** `tests/test_assertion_strength.py` · **NEW**
`tests/test_successor_predicate_s1.py` (the NFR-M1 split) ·
`tests/test_vacuous_cross_language.py` (AC9.11's population widening ONLY) · the three
regenerated dogfood artifacts · the `DF-AUD-DETECT-D` note in `deferred-work.md` · this story
file · `sprint-status.yaml` · **plus `README.md` and `CHANGELOG.md`** (`DN-17-3-16`).
⛔ **Nothing else.** ⛔ **`git add -A` was never used**; every commit staged explicit paths, and
the peer session's `deferred-work.md` work was left unstaged until that session committed it
itself at `8715b7f`.

### File List

- `argus/detectors/provenance_scan.py` — modified (the `DF-AUD-DETECT-D` collapse; `LogicalStatement` / `logical_statements`; `_SpanLine.pending`; `candidate_sut_edges`; `SutCallSite` / `sut_call_classification`; `result_observing_lines` and `assertion_statement_lines` made public)
- `argus/detectors/assertion_strength.py` — **NEW** (the scale, `UnregisteredStrength`, the SUT-derived-name resolver, the grader, `S1`)
- `argus/detectors/vacuous_test.py` — modified (`SuccessorVacuityEvidence`, `VacuousTestDetector.successor_evidence`, `_sut_call_sites` delegating to the ONE derivation)
- `tests/test_assertion_strength.py` — **NEW** (`-147`, `-148`, `-149`, `-150`, `-151`, `-152`)
- `tests/test_successor_predicate_s1.py` — **NEW** (`PRECISION-001-145`, `-146`; the NFR-M1 split half)
- `tests/test_vacuous_cross_language.py` — modified (AC9.11: `-130`'s population widened to `argus/detectors/**`; no assertion removed)
- `README.md` — modified (`DN-17-3-16`: published wheel figures)
- `CHANGELOG.md` — modified (`DN-17-3-16`: published wheel figures)
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md` — regenerated
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md` — regenerated
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md` — regenerated
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — modified (the `DF-AUD-DETECT-D` disposition ONLY; append-only, 1-CR invariant held)
- `_bmad-output/design-artifacts/ArgusAgent/stories/17-3-grade-what-the-assertion-constrains.md` — this record
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — `ready-for-dev` → `in-progress` → `review` (1,264 lines / 1,264 CR throughout)

---

## Change Log

| date | who | what |
|---|---|---|
| 2026-08-25 | create-story (Opus 5) | Story contexted at HEAD `024d330`. §0 measured by execution; six premises moved against `epics.md` — the fail-closed-test trap (all nine result-observing callees are WIDE assertions), the band-0-only verdict weight, `DF-AUD-DETECT-D`'s stale figures (re-measured 1,890 / 31,845 / 232 files), the non-portability of the research `ast` resolver, the NFR-M1 headroom and its pre-registered split trigger, and the five pinned shas all reachable. Status → `ready-for-dev`. |
| 2026-08-25 | bmad-dev-story (Opus 5) | Round 1 implement. Five commits: `4336d48` open → `2db5ce0` the `DF-AUD-DETECT-D` collapse ALONE and FIRST → `90b5235` the scale, the resolver, the grader and `S1` advisory → `8516297` dogfood regeneration → this record. §0 re-measured by execution before a line was written and every row reproduced. Collapse proven output-neutral three ways: 1,568 test functions re-scored with 0 evidence differences and 0 corroboration flips, three purpose-built string-state triggers all yielding identical `ProvenanceEvidence`, and the 1,032-finding harness byte-identical before and after. `S1` landed ADVISORY — `:796` unchanged as a parsed AST expression, nothing verdict-eligible moves, no reach figure published, both `SUCCESSOR_OUTPUT_PATHS` still absent. Span-scan cost 10,056 → 9,680 calls (−3.7%), a reduction, recorded as a disclosure with `DF-AUD-DETECT-C` untouched. Nine guards `-147`..`-152`, `PRECISION-001-145`/`-146` and `-130`'s widened population, each driven RED at its real seam without touching disk. Three divergences recorded with evidence: `DN-17-3-14` (the sibling evidence model, because `-119` pins the score's field set exactly), `DN-17-3-15` (the anchor sweep already carries `-130`, so `-153` was not minted) and `DN-17-3-16` (an AC10.9 escalation — a FIFTH cost of an `argus/**` byte moves README/CHANGELOG wheel figures). `tests/test_assertion_strength.py` projected above §0.8's 1,150 trigger and was SPLIT FIRST. ONE ledger entry written: `DF-AUD-DETECT-D`, with the 17.5 hand-off recorded. Status → `review`. |
