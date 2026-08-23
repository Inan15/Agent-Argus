# Story 16.6 — READINESS VALIDATION (independent)

**Story:** `16-6-the-assertion-vocabulary-recognises-the-assertion-that-is-a-raise`
**Story file:** `_bmad-output/design-artifacts/ArgusAgent/stories/16-6-the-assertion-vocabulary-recognises-the-assertion-that-is-a-raise.md`
**Sprint status on disk:** `ready-for-dev` (UNCHANGED by this validation)
**Validated:** 2026-08-23 at HEAD `6d48c15`, branch `epic-16/discharge-df-15-2-d`
**Validator:** independent reader (create-story `validate` action). Did NOT write the story.
**Mode:** READ-ONLY quality gate. Nothing under `argus/`, `tests/`, `scripts/` or the story
file was created, edited or deleted. `git status --porcelain` was, before and after, exactly:

```
 M _bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml
?? _bmad-output/design-artifacts/ArgusAgent/stories/16-6-...-is-a-raise.md
```

No detector was run over a sealed bench member; no ratification, no third-party fetch, no
disposition, no `V1.4` row. Re-derivation of the corpus figures was read-only over **pinned
git objects** into a scratch tree outside the repository.

---

## VERDICT: **FAIL** — 3 blocking defects, all in the story text, none in the research

The measurement underneath this story is **excellent and independently confirmed**: every
load-bearing number reproduces by execution, several of them to the exact `Fraction`. The
headline `−7` is right. AC5 is **not** vacuous. The fix shape is right.

But the story **as it stands on disk turns the repository's test suite RED**, and its own
`AC7.1` exit criterion is therefore unsatisfiable until the story file is edited. Two further
defects are self-contradictions of *precisely* the class that failed Story 16.5 — a task that
contradicts its own AC, and a cleanliness assertion where invariance is meant. The author
self-caught two instances of that class in the ACs; **the fix was applied to the ACs and not
to the Tasks that mirror them.** That is the concrete evidence for Epic 16's own proposition
that self-validation is weaker than independent validation.

Remediation is confined to the story file and is small. No re-research is required.

---

## BLOCKING DEFECTS

### B1 — §0.0's "GREEN baseline" is FALSE. The story file itself makes the suite RED.

**This is the Story 16.5 defect reproduced verbatim** ("16.5's dev found the baseline RED when
the story claimed green, and it cost a commit to repair" — §0.0, this story's own words).

Measured at `6d48c15` with the story file on disk:

```
ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 pytest   ->  1 failed, 1687 passed   exit 1
FAILED tests/test_governance_record_integrity.py::
       test_TC_ArgusAgent_DOCS_001_78_a_claimed_ledger_closure_is_checked_against_the_ledger
E  a story record claims a ledger closure that `deferred-work.md` never received:
E      16-6-...-is-a-raise.md claims DF-15-2-E
       ^ the guard's real message appends the literal closure verb after that id.
         It is shown on a separate line throughout this report for the reason given
         in the box below.
```

> ⚠️ **Why this report never puts that verb and an OPEN id on one line.**
> `story_closure_claims` globs **every** `*.md` in this directory, including this file.
> Reproducing the offending line verbatim would make this report a *second* false claimant
> and keep the suite RED after the story is fixed. Every quotation below is therefore
> line-wrapped so the verb and `DF-15-2-E` never share a physical line. **That wrapping is
> itself the fix B1 asks for.**

**The story file is the SOLE cause**, proven by driving the guard's own pure analyzers over the
78-story corpus with and without it:

| population | new unbacked closure claims |
|---|---|
| all 78 stories | one unbacked claim, from `16-6-...-is-a-raise.md`, against `DF-15-2-E` |
| the 77 excluding 16.6 | `[]` — none |

**The offending text is ONE line — story line 830**, in §References:

```markdown
- [deferred-work.md](../deferred-work.md) — `DF-13-5-A`,
  `DF-15-2-D` (**CLOSED**),
  `DF-15-2-E`,
```

⛔ **In the story these are ONE physical line.** They are wrapped here per the note above —
and wrapping them exactly like this is a valid fix, because the first line then carries only
ids the ledger *does* back.

`story_closure_claims` is **line-scoped by design** (`tests/test_governance_record_integrity.py:58-72`,
and the docstring says so: *"widening the window to a paragraph swept unrelated ids into the
claim"*). That single line carries a `_CLOSURE_VERB` match (`CLOSED`) and three `_DF_ID`
matches, so it reads as a claim that **all three** are closed. `DF-15-2-D` and `DF-13-5-A` are
backed by the ledger; `DF-15-2-E` is not — and must not be, because this story's own AC6.5
requires `DF-15-2-E` be "left exactly as [it] stand[s]".

So the story **contradicts itself at the extractor level**: its prose says `DF-15-2-E` is OPEN
(§0.6, §2.6, Dev Notes) while its References line asserts the closure. It also trips the very
guard its Dev Notes cite by name (*"Writing rule — `TC-ArgusAgent-DOCS-001-78`… This story
closes nothing"*).

**Consequences if shipped as-is.** §0.0 states "1,688 passed, 0 failed"; the truth with the file
present is 1,687 passed / 1 failed. `AC7.1` demands "**≥1,688 passed, 0 failed**" at the end —
unsatisfiable. Task 0.2 tells the dev to re-run every gate first, so the dev opens the story,
goes RED on line one of the work, and is in exactly the confusion this story was written to
prevent.

**Suggested fix (story file only; it is already in AC6.1's write set).** Break the shared line
so no closure verb shares a line with an OPEN id — e.g.

```markdown
- [deferred-work.md](../deferred-work.md) — `DF-13-5-A`, `DF-15-2-E`, `DF-16-6-A`,
  `DF-16-5-A/B`, `DF-16-1-A`, `DF-14-1-A`, `DF-14-3-A/B/C/H`
  · `DF-15-2-D` (closure recorded in the ledger 2026-08-22)
```

Then re-run the guard and confirm `story_closure_claims` no longer returns `DF-15-2-E`.
⚠️ Check the same property across the whole file after editing — line 830 is the only current
offender, but §0.6 and the Dev Notes ledger table both put ids and `CLOSED` near each other.

---

### B2 — Task 3.6 directly contradicts AC3.3 (the AR7 coupling the story says it removed)

This is one of the two defects the author reports self-catching. **It was fixed in the AC and
left live in the Task.**

- **AC3.3** (story line ~555): *"⛔ Discharged by the EXISTING `tests/test_gate_*.py` guards
  staying green — this story adds no assertion about `argus/precision/**` and **imports nothing
  from it into the new test module**. Coupling a vocabulary test to the precision gate would
  fork a guard that already exists, which is the AR7 defect. **Confirm by running those guards,
  not by writing new ones.**"*
- **Task 3.6** (story line ~962): *"The **containment** cases (AC1.3, AC3.1–3.4): frozen table
  23, `ast_corroborated` unmoved …, direction one-way, **`SECTION_5_CONDITIONS` still SEVEN**."*

Task 3.6 places the cases in `tests/test_vacuous_vocabulary.py` (Task 3.1). Asserting
`SECTION_5_CONDITIONS` there **requires** `from argus.precision.gate_decision import
SECTION_5_CONDITIONS` — the exact import AC3.3 forbids. A dev working the task list will write
the forbidden import; a dev working the ACs will not. This is the "two ACs that contradicted
each other" class that failed 16.5.

**AC3.3's discharge route is real and was verified**, so the AC is the correct side:

| existing guard | assertion |
|---|---|
| `tests/test_gate_breadth.py:616` | `len(decision.conditions) == len(SECTION_5_CONDITIONS) == 7` |
| `tests/test_gate_flip_path.py`, `test_gate_independence.py`, `test_gate_yield.py` | close over `precision_evaluable` |

**Suggested fix.** Strike `SECTION_5_CONDITIONS still SEVEN` from Task 3.6 and add to Task 7.1:
*"run `tests/test_gate_*.py` — this discharges AC3.3; write no new assertion about
`argus/precision/**`."* (Task 7.1 already names `tests/test_gate_*.py` "for **AC3.3**", so the
two tasks currently discharge the same AC two incompatible ways.)

---

### B3 — Task 0.5 demands an empty porcelain on corpus members, which §0.7 and AC4.5 both prove impossible

The second self-caught defect. **Again fixed in the AC, left live in the Task.**

- **§0.7:** *"⛔ An AC demanding `git status --porcelain` be EMPTY for these is unsatisfiable and
  would fail for a reason nobody can fix."*
- **AC4.5:** correctly asserts **INVARIANCE** — capture porcelain before and after, assert
  byte-identical. ✅ This AC is right.
- **Task 0.5** (story line ~876): *"Confirm `git -C <member> status --porcelain` **empty** for
  every member."* ⛔

Measured by me at `6d48c15`, before and after a full 1,032-finding read-only re-derivation:

| member | dirty entries | porcelain invariant across my run |
|---|---:|---|
| `agent-markovich` | 0 | ✅ byte-identical |
| `minions` | **14** | ✅ byte-identical |
| `xagents-webapp` | **1** | ✅ byte-identical |
| `agent-smith` | **16** | ✅ byte-identical |
| `ai-body-runtime` | 0 | ✅ byte-identical |

Task 0.5 can never pass. A dev who follows it either stops on an unfixable failure or "cleans"
a ratified member's working tree — which §0.7 explicitly calls a mutation of a ratified member.

**Suggested fix.** Restate Task 0.5 in AC4.5's terms: *"capture `git -C <member> status
--porcelain` before and after and assert the two are byte-identical; do NOT expect it empty —
three of the five are already dirty (§0.7)."*

---

## HIGH / MEDIUM

### M4 — AC5.1, §2.5 and Task 4.3 repeat B3's defect class on the Argus repo itself

Three places require `git status --porcelain` be **empty** after restoring a mutation:

- **AC5.1**: *"Record the observed RED, the command, and the restoration (`git status
  --porcelain` empty)"*
- **§2.5**: *"Restore the tree after each mutation and confirm `git status --porcelain` is empty."*
- **Task 4.3**: *"Restore. `git status --porcelain` **empty**. Re-run **green**."*

At Task 4 the working tree **necessarily** carries the Task 2 edit to
`vacuous_vocabulary.py`, the new untracked `tests/test_vacuous_vocabulary.py`, the story file
and `sprint-status.yaml` (and by Task 6, `deferred-work.md`). It is already non-empty today.
Empty is unreachable for the whole duration of the story.

**Suggested fix.** Same remedy as B3: capture porcelain immediately before the mutation and
assert byte-identical after restoration. That is what "restored byte-exact" (AC5's own Then
clause) actually means, and it is a strictly stronger check than emptiness.

### M5 — AC1.5's `183 / 2 / 5,085` are not independently reproducible, and the in-source columns they go into mean something else

AC1.5 requires the source carry *"the **measured** benefit (**183** in-`raise` sites) and
**cost** (**2** non-`raise` sites) over the **5,085**-file population"*. Two problems.

**(a) The population is underspecified, so the figures do not reproduce.** Re-derived with
stdlib `ast` (the story's own stated method) over the population §0.5 describes — Argus, the
five pinned checkouts, this environment's `site-packages`, the CPython 3.11 stdlib:

| population construction | files | in-`raise` | not in `raise` | ratio |
|---|---:|---:|---:|---:|
| story's claim | 5,085 | 183 | 2 | ~91× |
| nested `.venv`/`site-packages` **excluded** from repo walks | 4,369 | 172 | 2 | 86× |
| nested `.venv` **included** | 20,769 | 662 | 3 | 221× |

**The conclusion is robust — 86×, 91× and 221× all clear `DN-14-3-5`'s bar by two orders of
magnitude — and both named collision sites are CONFIRMED exactly:**
`…/site-packages/stevedore/tests/test_extension.py:118` and Argus's own
`tests/test_open_llm_adapter.py:391`. (The third hit in the wide run is a duplicate vendored
copy of stevedore inside Minions' own `.venv`, i.e. the story's "2" is right once vendored
duplicates are folded.) But a dev running Task 0.6 will get a number that is not 183, and
AC1.5 as literally written then cannot be satisfied.

**(b) The live in-source table's columns mean something different.** At
`argus/detectors/vacuous_vocabulary.py:290` the table is

```
#     name        py collisions   js/ts benefit   benefit/cost   decision
```

over a stated **4,046**-file population. For `AssertionError`: the `js/ts benefit` is **0** (it
is a Python builtin), so writing `183` there records a false value; and `py collisions` in every
existing row counts **all** Python call sites of the name (`match` 706, `Error` 164), not the
non-`raise` subset — so `2` in that column is a different measurement from its neighbours
(all sites would be ~185).

**Suggested fix.** AC1.5 should (i) state the population's inclusion rules — in particular
whether nested `.venv`/`site-packages` under corpus checkouts are walked — so the figure is
reproducible; and (ii) require a **labelled** row or adjacent sub-note rather than reusing
columns whose semantics differ, e.g. a `python benefit (in-raise)` column or a footnoted row.
Alternatively, re-word AC1.5 to require "the re-derived benefit and cost over a population the
block states", with §0.5's numbers as the expectation rather than the contract, and let
Task 0.8/AC4.4's "the tree wins" carry it.

---

## LOW

- **L6 — §0.7 says `minions` has 13 dirty entries; measured **14**.** Not load-bearing (AC4.5
  asserts invariance, not a count) but it is a §0 figure and Task 0.8 requires disagreements be
  recorded. If anything it reinforces §0.7's own argument.
- **L7 — §0.1's `except AssertionError:` row shows `[]`.** A span containing any call emits that
  call's edge; I measured `['f']` for `try: f() / except AssertionError: pass`. The row's actual
  point — **no `AssertionError` edge** — holds. Cosmetic.
- **L8 — AC5.2 moves the "accepted collision cost" register away from `-133`.**
  `tests/test_vacuous_cross_language.py:617-621` is where the project records each admitted
  name's accepted cost, as a hand-listed five-name loop. `AssertionError` becomes the sixth
  admitted name with its cost recorded **elsewhere**, so a future auditor reading `-133` as the
  register under-counts. `DN-16-6-3`'s cohesion argument for the new module is sound; add a
  cross-reference in both docstrings so neither reads as complete on its own.

---

## WHAT I VERIFIED AND FOUND **CORRECT**

### ✅ 1. The headline number is RIGHT — exactly, including all seven rows

Re-derived independently over **pinned git objects** (`git cat-file -p <sha>:<path>`) into a
scratch tree, scoring each span with the **real** `build_ast_index` + the **real**
`VacuousTestDetector._score`, once against the shipped 88-name table and once against a
89-name table patched in memory:

| | story | **measured** |
|---|---:|---:|
| recorded `vacuous_test_heuristic` findings | 1,032 | **1,032** ✅ |
| unresolvable locators | 0 | **0** ✅ |
| carry a `raise AssertionError` (any form) | 22 | **22** ✅ |
| FLAGGED before | 1,032 | **1,032** ✅ |
| FLAGGED after | 1,025 | **1,025** ✅ |
| **DELTA** | **−7** | **−7** ✅ |
| newly flagged | 0 | **0** ✅ |
| affected but still flagged | 15 | **15** ✅ |
| by member | minions 12 + agent-smith 10, other three 0 | **identical** ✅ |

**All seven un-flagged rows reproduce with their exact before→after densities**, including the
awkward ones (`1/7 → 2/7`, `6/25 → 7/25`, `0 → 1/4`). §0.3's table needs no correction.

**The `−7` vs `−22` warning is correct and is the most valuable line in the story.**

### ✅ 2. The fix shape — all four sub-claims confirmed

Probed with a real `build_ast_index` over a scratch fixture:

| source | edges in span | story | verdict |
|---|---|---|---|
| `raise AssertionError("must raise")` | `['AssertionError']` | edge exists | ✅ |
| `raise builtins.AssertionError("x")` | `['AssertionError']` | resolves to `.attr` | ✅ |
| `raise AssertionError` (bare) | `[]` | no edge | ✅ |
| `with pytest.raises(AssertionError):` | `['raises', 'check']` | **no** `AssertionError` edge | ✅ |
| `e = AssertionError("x")` | `['AssertionError']` | the collision shape | ✅ |

Spelling census over the 22: **call 22, bare 0, attribute 0** ✅ exactly as §0.4 claims. So the
"no second scanner / adding one double-counts all 22" argument (§2.1, `DN-16-6-2`) is sound,
and the bare form's "0 of 1,032" residual is a measured decision, not a gap.

### ✅ 3. The change itself, and the frozen table's unreachability

```
len(_ASSERTION_CALLEES)                == 88     ✅  (-> 89)
len(_CORROBORATION_ASSERTION_CALLEES)  == 23     ✅  FROZEN, DN-14-2-1
len(_MOCK_CALLEES)                     == 10     ✅
is_assertion_callee("AssertionError")  is False  ✅
_ASSERTION_NAMING_CONVENTION           == r"\A_?assert\w*\Z"  case-sensitive, no match  ✅
ASSERTION_DENSITY_FLOOR == Fraction(1,4)   MOCK_RATIO_CEILING == Fraction(1,2)  ✅
vacuous_test.__all__ == 9    vacuous_vocabulary.__all__ == ['is_assertion_callee']  ✅
"Error" not in _ASSERTION_CALLEES  ✅
```

§2.2's structural argument was verified **by reading the code**, not by trusting the prose:
`_score` uses `is_assertion_callee` for `assertion_call_sites` only; `_sut_call_sites` filters
on `_CORROBORATION_ASSERTION_CALLEES`/`_MOCK_CALLEES`; `_ast_corroborated` passes
`assertion_callees=_CORROBORATION_ASSERTION_CALLEES`; `mock_ratio` reads `_MOCK_CALLEES`;
`call_sites = len(span_edges)`; `statement_count = _count_statements`. **None reads the wide
table.**

**And confirmed empirically across all 1,032 spans:** `mock_ratio`, `call_sites` and
`statement_count` are byte-identical under both tables, and `assertion_sites` is monotone
non-decreasing. **The ACs cannot be satisfied by touching the frozen table**, and a
newly-flagged finding is structurally impossible — `0` is the measured confirmation.

### ✅ 4. `DN-14-3-5` census — direction sound, both collision sites confirmed

See **M5**: the conclusion and both named sites are confirmed; only the exact figures and the
population definition need tightening. The risk argument ("widening does not over-flag
elsewhere") **stands**.

### ✅ 5. `DF-15-2-E`'s trigger does NOT fire, and `DN-16-6-3` is the right call

Measured with the ceiling guard's **own** `_physical_line_count` (`_CEILING = 1200`).
**All ten of §0.6's line counts reproduce exactly:**

| file | measured |
|---|---:|
| `argus/detectors/vacuous_vocabulary.py` | **455** ✅ |
| `argus/detectors/vacuous_test.py` | **796** ✅ |
| `argus/detectors/provenance_scan.py` | **976** ✅ |
| **`tests/test_vacuous_density.py`** | **1,159** ✅ (trigger **1,180**, 21 lines margin) |
| `tests/test_vacuous_cross_language.py` | **1,031** ✅ |
| `tests/test_vacuous_detector.py` | **791** ✅ |
| `tests/test_vacuous_detector_index.py` | **1,065** ✅ |
| `argus/precision/gate_decision.py` | **1,132** ✅ |
| `tests/test_gate_independence.py` | **1,127** ✅ |
| `argus/precision/gate_independence.py` | **328** ✅ |

`DF-15-2-E`'s trigger text in `deferred-work.md:5357-5361` matches the story's verbatim quote.
The entry is **OPEN** and the trigger has **not** fired.

**Could the story's own guards cross a trigger in the new module?** No. `tests/test_vacuous_vocabulary.py`
does not exist today, starts at 0 against a 1,200 ceiling, and carries no ledger entry. The
ceiling guard's population is `git ls-files -- '*.py'` — the **index** — so the new module is
swept "the moment it is `git add`-ed, before any commit" (its docstring, lines 19-26). Story's
claim ✅. `_EXEMPT_BY_DESIGN` holds 3 entries, none of them these files.

### ✅ 6. "Identically green with the name added" — CONFIRMED, and **AC5 IS NOT VACUOUS**

Full suite re-run with an **out-of-tree** pytest plugin adding `"AssertionError"` to the wide
table in memory (no repo file touched):

| run | result |
|---|---|
| baseline (shipped 88) | `1 failed, 1687 passed` — the B1 governance guard |
| widened (89, in memory) | `1 failed, 1687 passed` — **the same single failure, no other delta** |

**No existing guard can see the fix.** AC5's mutation-driven RED is therefore *necessary*, and
the story is right to say so.

**And AC5 actually specifies a mutation that goes RED.** Every measured before/after row the
ACs assert was reproduced exactly, at the real seam:

| AC | fixture | SHIPPED (88) | WIDENED (89) | distinguishes? |
|---|---|---|---|---|
| **AC2.3** | one `raise AssertionError("x")` | `sites=0 stmts=2 dens=0 flag=True` | `sites=1 stmts=2 dens=1/2 flag=False` | **YES** |
| **AC2.4** | `assert r` + `raise AssertionError("x")` | `sites=1 stmts=3 dens=1/3 flag=False` | `sites=2 stmts=3 dens=2/3 flag=False` | **YES** |
| **AC5.2** | `AssertionError("x")` outside a `raise` | `sites=0 stmts=3 dens=0 flag=True` | `sites=1 stmts=3 dens=1/3 flag=False` | **YES** |
| **AC5.4** | bare `raise AssertionError` | `sites=0 stmts=2 flag=True` | `sites=0 stmts=2 flag=True` | no — **by design** |
| **AC5.4** control | `pass`-bodied | `sites=0 stmts=2 flag=True` | identical | no — **by design** |

Every figure the story states for these five is **exactly** right, including AC2.4's warning
that `flagged` is `False` in **both** columns (so a guard written against a flag flip there
would be vacuous — the story caught its own lockstep trap) and AC5.4's "identical in both
columns, which is the point" plus its control scoring identically.

**Three of the five cases flip under AC5.1's mutation (remove `"AssertionError"`).** AC5.1
requires "at least one". **AC5 can distinguish the fix from its absence. Not vacuous.**

### ✅ 7. Neither builder invokes a detector; the corpus artifacts stay put

```
python scripts/build_adjudication_record.py --check
  -> "OK - the adjudication record is current (31 row(s))."         exit 0  ✅
python scripts/build_gate_decision.py --check
  -> "CURRENT - BLOCKED (NOT COMPUTED BY THIS RUN)"                 exit 0  ✅
git status --porcelain after both  -> unchanged (they write nothing)        ✅
```

`gate-decision-record.json`: `ratified_member_count = 5`, `outcome = BLOCKED`, `seal_holds = False`.
`adjudication-set-13-5.json`: 5 members. `N` stays **5**. §2.3 / `DN-16-6-4` stand.

### ✅ 8. Both self-caught AC defects WERE fixed in the ACs

- **AC4.5** asserts **invariance**, not cleanliness ✅ — correct, and matches the measured
  reality (3 of 5 checkouts dirty). *But Task 0.5 still says "empty" → **B3**.*
- **AC3.3** is discharged by **existing** gate guards, adds no `argus/precision/**` assertion ✅
  — and the route is real (`tests/test_gate_breadth.py:616`). *But Task 3.6 re-couples it → **B2**.*

**The same class searched for elsewhere** produced **M4** (AC5.1 / §2.5 / Task 4.3, cleanliness
where invariance is meant). I found no further instance in the ACs themselves — the AC set is
clean of this class; the **Tasks** are not.

---

## BASELINE, INDEPENDENTLY RE-MEASURED at `6d48c15`

| gate | command | story claims | **I measured** | verdict |
|---|---|---|---|---|
| Full suite | `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 pytest` | 1,688 passed / 0 failed, exit 0 | **1 failed, 1687 passed**, **exit 1** | ⛔ **B1** |
| Test files | — | 122 | **122** | ✅ |
| Coverage | `pytest --cov=argus --cov-fail-under=80` | 95.55% (7,095 stmts, 316 missed) | **95.55%, 7,095 stmts, 316 missed** | ✅ exact |
| Types (CI scope) | `mypy argus` | Success, 94 files | **Success, 94 source files** | ✅ |
| Types (wider) | `mypy argus scripts` | 4 pre-existing errors in 3 files | **4 errors in 3 files, 102 checked** | ✅ exact |
| Security | `bandit -r argus --severity-level medium` | Medium 0 / High 0 | **Medium 0 / High 0** | ✅ |
| Ceiling | `pytest tests/test_module_size_ceiling.py` | 6 passed | **6 passed** | ✅ |
| Builder | `build_adjudication_record.py --check` | current, 31 rows, exit 0 | **current, 31 row(s), exit 0** | ✅ |
| Builder | `build_gate_decision.py --check` | CURRENT — BLOCKED, exit 0 | **CURRENT — BLOCKED, exit 0** | ✅ |

The recorded `mypy argus scripts` caveat is **exactly right**, including all three named files
(`candidate_selection.py`, `build_gate_decision.py:110` `_cartridge`,
`audit_validation_corpus.py:702`); the fourth error is `candidate_selection.py:599`, the
sibling of the named `:600`. CI runs `mypy argus` (clean), so the caveat's conclusion holds.

**Every one of §0.0's rows is correct EXCEPT the full-suite row — and that row is wrong only
because the story file was written after the measurement and never re-measured with itself
present.**

---

## OTHER CHECKS

| check | result |
|---|---|
| Every file path an AC names exists at that path today | ✅ all 25 checked; `tests/test_vacuous_vocabulary.py` correctly ABSENT (it is NEW) |
| Promotes nothing | ✅ advisory tier only; corroboration path unreachable (§2.2 verified in code) |
| Moves no threshold | ✅ `ASSERTION_DENSITY_FLOOR` 1/4, `MOCK_RATIO_CEILING` 1/2 |
| No eighth §5 condition | ✅ `len(SECTION_5_CONDITIONS) == 7` |
| `precision_evaluable` conjuncts | ✅ exactly **four** |
| Nothing ratified | ✅ `N = 5` |
| No detector over a bench member in the story's plan | ✅ Task 5 reads pinned blobs into a scratch tree |
| No fetch, no disposition, no `V1.4` row | ✅ |
| `DF-13-5-A` OPEN and UNSPENT | ✅ ledger `:4766` — *"THE ENTRY STAYS OPEN. `DF-13-5-A` is UNSPENT."* |
| Story single-purpose | ✅ one name, one table, one direction |
| ACs individually testable | ✅ every AC names an executable observable |
| ACs collectively sufficient | ✅ subject to B1–B3 / M4–M5 |
| §0.2's "precondition discharged, file has moved" | ✅ the tables are in `vacuous_vocabulary.py`; no AC names the stale home |
| `-133` is a named-name guard, not a whole-table sweep | ✅ `test_vacuous_cross_language.py:617-621` |
| §2.4's six table invariants survive 89 | ✅ confirmed structurally **and** by the widened suite run |

---

## REQUIRED BEFORE THIS GOES TO A DEV

All edits are to the **story file only**; it is already inside AC6.1's write set.

1. **B1** — split story line 830 so no closure verb shares a line with an OPEN `DF-*` id; re-run
   `tests/test_governance_record_integrity.py` and confirm GREEN. Then re-state §0.0's
   full-suite row from a run **with the story file present**.
2. **B2** — remove `SECTION_5_CONDITIONS still SEVEN` from Task 3.6; point it at Task 7.1's
   existing `tests/test_gate_*.py` run, per AC3.3.
3. **B3** — restate Task 0.5 as invariance, matching AC4.5 and §0.7.
4. **M4** — restate AC5.1 / §2.5 / Task 4.3 as porcelain **invariance** across each mutation,
   not emptiness.
5. **M5** — tighten AC1.5: state the census population's inclusion rules, and require a labelled
   row rather than reusing the `js/ts benefit` / `py collisions` columns.
6. **L6/L7/L8** — optional; correct `minions` 13 → 14, soften the `except` row, cross-reference
   `-133`.

Once B1–B3 are fixed the story is, on the evidence, **genuinely dev-ready**: the research is
the strongest I have validated in this epic and the `−7` figure — the one a dev would most
likely misread as a failed fix — is exactly right.

---

## REPRODUCTION

All harnesses were written **outside the repository**, under the session scratchpad, and are
read-only. None is committed; none writes into `argus/`, `tests/`, `scripts/`, any corpus
member, or any validation-corpus artifact.

| harness | what it establishes |
|---|---|
| `probe_edges.py` | §0.1's edge-emission table (real `build_ast_index`) |
| `rederive.py` | §0.3/§0.4 — 1,032 → 1,025, the 22, the spelling split, porcelain invariance |
| `census.py` / `census2.py` | §0.5's collision census under two population constructions |
| `fixtures.py` | every AC before/after row (AC2.3, AC2.4, AC5.2, AC5.4 + control) |
| `widen_plugin.py` | the in-memory 89-name suite run ("identically green") |

**Sprint status was NOT modified. The story file was NOT modified. This report is the only
file written.**
