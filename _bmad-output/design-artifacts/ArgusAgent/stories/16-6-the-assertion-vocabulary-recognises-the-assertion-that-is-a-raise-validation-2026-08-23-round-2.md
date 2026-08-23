# Story 16.6 — READINESS VALIDATION, ROUND 2 (independent)

**Story:** `16-6-the-assertion-vocabulary-recognises-the-assertion-that-is-a-raise`
**Story file:** `stories/16-6-the-assertion-vocabulary-recognises-the-assertion-that-is-a-raise.md`
**Round-1 report:** `…-validation-2026-08-23.md` (same directory)
**Sprint status on disk:** `ready-for-dev` — **UNCHANGED by this validation**
**Validated:** 2026-08-23 at HEAD `6d48c15`, branch `epic-16/discharge-df-15-2-d`
**Validator:** independent reader, iteration 2. Did **not** write the story and did **not** write the
2026-08-23 amendment.
**Mode:** READ-ONLY. Nothing under `argus/`, `tests/`, `scripts/`, the story file or
`deferred-work.md` was created, edited or deleted. This report is the only file written.
Verified by execution: `git diff --stat HEAD -- tests/ argus/ scripts/` is empty and
`git status --porcelain -- tests/ argus/ scripts/` is empty.

No detector was run over a sealed bench member; no ratification; no third-party fetch; no
disposition; no `V1.4` row; no protocol edit. Re-derivation was read-only measurement over the
repository's own artifacts.

> ⚠️ **Why this report never puts a disposition verb on a line with an open id.**
> `story_closure_claims` globs **every** `*.md` under `stories/`, including this file. That is
> `DF-16-6-D`'s subject and it has now recurred eight times. Every line below is wrapped so the
> rule holds. **The guard was re-run over this report after writing it: green.**

---

## VERDICT: **CONCERNS** — all six round-1 findings resolved; five further divergences found

**All three round-1 BLOCKING defects are genuinely FIXED, not relocated, and I confirmed each by
execution rather than by reading the amendment's claim.** The suite is green with everything on
disk. The two new ledger entries are well-formed and dispose of nothing. The byte integrity of the
append is exact at the byte level, not merely at the line level.

**But my own AC/Task sweep found five more divergences the amendment's sweep missed** — four of the
same AC/Task-twin class it named as the reusable lesson, plus one factually false path sentence
inside the very block written to prevent path errors. None is blocking: none turns the suite red,
none is unsatisfiable, and none forces a wrong action the way round-1's B2 did. Each is an
**omission** or a **stale figure**, and in every case the AC — the authoritative side — is correct.

The story is close to dev-ready. Fixing items C1–C5 below is small and confined to the story file.

---

## PART 1 — THE SIX ROUND-1 FINDINGS, RE-CHECKED BY EXECUTION

| # | Round-1 finding | Status | How I confirmed it |
|---|---|---|---|
| **B1** | §0.0's GREEN baseline was FALSE; the story file made the suite RED | ✅ **FIXED** | Full suite re-run by me with the amended story file, the round-1 report and both new ledger entries on disk: **1,688 passed, 0 failed, exit 0** |
| **B2** | Task 3.6 ordered an assertion AC3.3 forbids | ✅ **FIXED** | Task 3.6 now enumerates AC1.3/3.1/3.2/3.4 only and carries an explicit prohibition; AC3.3 and Task 7.1 both name the existing gate guards as the whole discharge |
| **B3** | Task 0.5 demanded an empty porcelain on corpus members | ✅ **FIXED** | Task 0.5 now orders before/after byte-identical captures and says "do NOT expect them empty" |
| **M4** | AC5.1 / §2.5 / Task 4.3 repeated B3 on this repo | ✅ **FIXED** | All three restated as invariance; Task 4.1 now takes the pre-mutation capture. A grep for `porcelain` returns no surviving emptiness requirement except Task 7.2's `git diff --stat` (a legitimate diff-emptiness check) |
| **M5** | AC1.5's census figures unreproducible; wrong in-source columns | ✅ **FIXED, and the replacement is checkable** | AC1.5 now requires stated inclusion rules and a **labelled** row, explicitly forbids the existing columns, and demotes the figures to an expectation. I verified the premise it rests on: `argus/detectors/vacuous_vocabulary.py` line 290 does carry `name / py collisions / js/ts benefit / benefit/cost / decision` over a stated **4,046**-file population — so the AC's prohibition names a real thing, and a reviewer can check compliance by looking for the labelled row and the stated rule. **Not vaguer.** |
| **L6/L8** | `minions` 13 vs 14; the `-133` register moved | ✅ **FIXED** | §0.7 now records three disagreeing same-day columns; AC5.2 requires a bounded two-way cross-reference and AC6.1 carries the matching bounded write-set exception. I verified `tests/test_vacuous_cross_language.py:617-621` really is a hand-listed **five-name** loop, so `AssertionError` really would be a sixth admitted name registered elsewhere |
| **L7** | §0.1's `except AssertionError:` row shows `[]` | ⚠️ **NOT fixed** (round 1 called it optional) — story line 174 unchanged |

### A1 is genuinely fixed, not relocated — proven independently

I drove the guard's **own** pure analyzers over the live corpus rather than trusting the amendment:

```
ledger_closed_ids(deferred-work.md)       -> 35 ids
story files globbed                       -> 79
total closure claims extracted            -> 60
NEW unbacked claims                       -> []      <- none
stale registry entries                    -> []      <- none
_UNBACKED_AT_LANDING                      -> 17      <- unchanged, not weakened
tests/test_governance_record_integrity.py -> 3 passed
```

`git diff --stat HEAD -- tests/` is **empty**, so neither `story_closure_claims` nor
`ledger_closed_ids` nor the historical registry was touched, shrunk or exempted. **The record was
repaired; the guard was not.**

**Then I hunted the recurring line-shape myself** — the guard's own `_CLOSURE_VERB` against the
guard's own `_DF_ID`, across the story file, the round-1 report and the two new ledger entries,
scoring each id against the ledger's disposition set:

| file | lines carrying a verb **and** an id | any carrying an id the ledger does not back |
|---|---:|---|
| story file | 4 (all `DF-15-2-D` alone, which the ledger backs) | **none** |
| ledger — appended region only (lines 5689-5815) | **0** | **none** |
| round-1 report | 2 | **one, masked — see C1** |

I re-ran the same scan with a **wider** verb set (`closure`, `disposed`, `discharged`, lowercase
`closed`) against the true open set. The story file's four hits and the ledger append's two hits are
all negations or non-verbs, and none matches the guard's predicate. **The story file and both new
ledger entries are clean of this defect.**

---

## PART 2 — THE TWO NEW LEDGER ENTRIES

| check | result |
|---|---|
| Id convention `DF-16-6-C` / `DF-16-6-D` | ✅ correct; `-B` deliberately skipped and still free, exactly as AC6.5 requires |
| Format matches neighbours | ✅ `- id:` / `- origin_story:` / `- owner:` / `- target_story:` / `- category:` / `- severity:`, same shape as the `DF-16-5-A` and `DF-16-5-B` entries immediately above |
| Remedies proposed, **not** implemented | ✅ both say so explicitly; no `.gitattributes` exists (`git check-attr` returns nothing for the path) and no pre-commit hook was added |
| Nothing disposed of | ✅ **the analyzer's disposition set is 35 before and 35 after, and the two sets are set-identical** — computed against `git show HEAD:…/deferred-work.md` and against the working tree; the symmetric difference is empty |
| `DF-13-5-A` open and unspent | ✅ ledger line 4766 — *"THE ENTRY STAYS OPEN … is UNSPENT"*; `- round_state: UNSPENT` at 4777 |
| Evidence accurate | ⚠️ **one inaccuracy — see C1** |

### Byte integrity — verified at the byte level, not the line level

```
HEAD blob                 433,506 bytes      working tree   444,253 bytes
prefix comparison         cur[:433506] == HEAD blob        -> TRUE
first differing offset    433,506  (== end of the HEAD blob, i.e. a PURE APPEND)
appended                  10,747 bytes / 127 lines
git diff --numstat        127   0   deferred-work.md
lone CR bytes  (\r not followed by \n)   HEAD 1   ->   working tree 1
CRLF pairs                               HEAD 0   ->   working tree 0
trailing newline                         present
```

**This is a genuine prefix-byte-identical append**, not merely `+127 / -0` by line count. The lone
`CR` that `DF-16-6-C` is filed about survived, and the trailing newline survived.

---

## PART 3 — MY OWN AC/TASK SWEEP (independent, over the WHOLE task list)

I cross-checked all 32 acceptance criteria against all 33 subtasks in both directions, rather than
confirming the five the amendment names. **The amendment's five are real and are repaired.** I found
**five more**, four of them the same AC/Task-twin class the amendment itself calls the reusable
lesson.

### C1 — [med] The round-1 report still carries the recurring line-shape, masked by the known analyzer false positive — and `DF-16-6-D`'s evidence says it does not

Round-1 report, **line 78**, has a disposition verb on the same physical line as `DF-13-5-A`, which
is **open**. It passes today **only** because `ledger_closed_ids` reports `DF-13-5-A` as
disposition-bearing from historical ledger prose (the known pre-existing `low` item 2). I verified
that false positive is genuinely pre-existing: the analyzer returns the identical 35-id set over
`git show HEAD:…/deferred-work.md`, and `DF-13-5-A` is in **both** sets. Its source is ledger line
4727, far above the append.

Two consequences the amendment did not record:

1. **A latent RED coupled to the obvious repair.** The moment anyone fixes that false positive —
   which is the correct fix, and `DF-16-6-D`'s own remedy (ii) would surface it — the round-1 report
   makes the suite red. The rule `DF-16-6-D` states positively is *"a disposition verb and a ledger
   id may share a physical line only when this ledger already backs that id"*; here the backing is
   an artefact of a known extractor bug, not a real disposition.
2. **`DF-16-6-D`'s evidence is inaccurate on this point.** Ledger lines 5778-5780 assert that the
   round-1 report's author *"caught it in their own draft, wrapped **every** quotation."* Line 78 of
   that report is not wrapped. The entry's recurrence count of seven should be **eight**, and the
   round-1 report belongs on the list as a **surviving** instance, not a caught one.

**Suggested fix.** Wrap round-1 report line 78 the way the story's §References is now wrapped (leave
the verb alone with the id the ledger genuinely backs), and correct `DF-16-6-D`'s evidence sentence.
Neither edit is this story's dev work — but leaving them is how the entry's own count goes stale,
which is the failure mode `DF-14-3-H`'s target-story drift is filed under.

### C2 — [med] AC5.2's two-way cross-reference has **no task** — the amendment's own A6 repair is unmirrored

AC5.2 now requires, in bold, an edit to **two** docstrings: `-133` in
`tests/test_vacuous_cross_language.py` pointing at the new module, and the new case pointing back.
AC6.1 carries the matching bounded write-set exception permitting it, and Dev Notes decision 2
justifies it at length.

**No task orders it.** `AC5.2` appears exactly once in the whole Tasks section — Task 3.4, which
reads in full: *"The **accepted collision cost** case (AC5.2): `AssertionError("x")` outside a
`raise`."* Nothing about the cross-reference, the two directions, the two-line bound, or the other
file.

Worse, **Task 7.3 works against it**: it says *"Confirm the final write set equals AC6.1 exactly …
Expect exactly AC6.1's set **plus** the pre-existing artifact entries"* and enumerates those
artifacts without naming `tests/test_vacuous_cross_language.py`. A dev who **does** write the
cross-reference then sees a file in the porcelain that Task 7.3's expectation list does not mention.

This is precisely the class the amendment's own Dev Notes describe — *"an AC repaired on one side of
the file while its executable twin kept the defect"* — reproduced by the repair for A6.

**Suggested fix.** Add to Task 3.4: *"and add the AC5.2 two-way cross-reference — at most two
docstring lines in `-133` pointing at `tests/test_vacuous_vocabulary.py`, and one line in the new
case pointing back at `-133`; no assertion, fixture, loop member or import changes (AC6.1's single
bounded exception)."* Add `tests/test_vacuous_cross_language.py` to Task 7.3's expected porcelain.

### C3 — [med] AC6.4 is referenced by **no task at all**

Grepping every `ACn.m` citation in the Tasks section returns AC1.3, AC1.5, AC2.1, AC2.3, AC2.4,
AC3.1, AC3.2, AC3.3, AC3.4, AC4.4, AC4.5, AC5.1, AC5.2, AC5.4, AC5.6, AC6.1, AC6.2, AC6.3, AC6.5,
AC7.3, AC7.4 — and the un-cited ones are all covered by task prose except one. **AC6.4 is orphaned.**

AC6.4 requires two things nothing in the task list asks for:

- `vacuous_test.__all__` still has **9** entries, and
- `from argus.detectors.vacuous_test import _ASSERTION_CALLEES, _CORROBORATION_ASSERTION_CALLEES,
  is_assertion_callee` resolves to the **same objects** as the direct import.

Task 2.5 verifies the predicate and the length via the direct import only. Task 3.6's containment
list stops at AC1.3/3.1/3.2/3.4. Task 7.1's ceiling run covers the ≤1,200 half and nothing else.
This matters because the re-export shim is exactly what `4123931`'s split created and exactly what
`ba5e8df` had to repair afterwards — it is the story's own named precedent for a surface that breaks
quietly. (I confirmed the property holds today: all three re-exports are the identical objects and
`vacuous_test.__all__` is 9.)

**Suggested fix.** Add a subtask under Task 3.6 (or a new Task 2.6) naming AC6.4's two assertions.

### C4 — [med] §0.0's PATH ROOTS block states a **false** path for five artifacts — inside the block written to prevent exactly that

Story lines 103-106 read: *"`validation-corpus/adjudication-set-13-5.json`,
`validation-corpus/adjudication-record.json` and `validation-corpus/gate-decision-record.json` … live
under `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/`, **as do** `epics.md`,
`architecture.md`, `deferred-work.md`, `precision-validation-protocol.md` and this story file."*

Measured on disk:

```
_bmad-output/design-artifacts/ArgusAgent/validation-corpus/
    adjudication-record.json   adjudication-set-13-5.json   adjudication-set.json
    blocking-worklist-13-5.md  blocking-worklist.md         gate-decision-record.json
```

`epics.md`, `architecture.md`, `deferred-work.md` and `precision-validation-protocol.md` live one
directory **up**; the story file lives in `stories/`. The "as do" clause binds to the full path
including `validation-corpus/`, so a dev following it literally ENOENTs on `deferred-work.md` at
Task 6 — **the identical failure this block warns about, and the identical failure the amendment's
own sweep repaired in Task 7.2 two hundred lines later.**

Not blocking, because AC6.1 line 710 gives the correct path
(`_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`) and the §References links resolve
correctly from `stories/`. But the one block a dev is told to read *before Task 0's first command*
should not be the one that is wrong.

**Suggested fix.** Split the sentence: the three JSON artifacts are under
`…/ArgusAgent/validation-corpus/`; `epics.md`, `architecture.md`, `deferred-work.md` and
`precision-validation-protocol.md` are under `…/ArgusAgent/`; this story file is under
`…/ArgusAgent/stories/`.

### C5 — [low] A6's honesty rule is not applied to AC4.5 — three sources give three different dirty counts

§0.7 now says, correctly: *"The counts above are a dated OBSERVATION, not a premise — **assert none
of them**."* But:

| where | what it says |
|---|---|
| §0.7, amendment-pass column | agent-markovich 0 · minions **0** · xagents-webapp 1 · agent-smith 18 → **two** dirty |
| Task 0.5 | *"**Two** of the five were dirty when this amendment pass measured them"* |
| **AC4.5** | *"**three of the five** member checkouts are ALREADY DIRTY (§0.7)"* |
| **my own measurement, same day** | 0 · **2** · 1 · **28** · 0 → **three** dirty |

So AC4.5 states a count, cites §0.7 as its authority, and §0.7 forbids the assertion. My fourth
same-day measurement is a fourth different answer — which strengthens §0.7's argument and weakens
AC4.5's clause further. The clause is rationale, not the operative contract (AC4.5's contract is the
byte-identical capture, which is correct), so this is `low` — but it is the rule A6 installed,
unapplied to the AC A6 was repairing.

**Suggested fix.** Replace AC4.5's *"three of the five … are ALREADY DIRTY"* with *"some members are
already dirty and the count moves between sessions (§0.7) — assert invariance, never emptiness."*

### Lesser items (record; fixing is optional)

- **[low]** §0.0 line 96 closes its enumeration with *"and nothing else"* while listing one
  validation report. There are now two, and this report makes three artifacts under `stories/`.
  Immediately softened by the "do NOT assert a COUNT" rule below it and by Task 0.1's restated
  invariant, so it is inert — but the same closed-enumeration shape is what Task 0.1's *"exactly
  two"* was repaired for. Task 7.3 has the same singular *"its validation report"*.
- **[low]** AC1.5 delegates §0.5's census to *"AC4.4 — the tree wins"*, but AC4.4's own text is
  scoped to §0.3 only (*"if a re-derived figure disagrees with **§0.3**"*). AC7.3 does list
  §0.3/§0.4/§0.5. Widen AC4.4 to "§0.3, §0.4 or §0.5" so the delegation lands.
- **[low]** AC5.5 requires the non-vacuity preamble and the statement-count-pinned control of
  **every** new case. Task 3.2 applies it to the primary case and Task 3.5 to the bare-`raise` case;
  Tasks 3.3, 3.4, 3.6 and 3.7 are silent. Add "per AC5.5" to Task 3.
- **[low]** §0.8 allocates verification ids from `-138`, but only `-138` is named across seven guard
  groups (Tasks 3.2-3.7). Not wrong; a dev will allocate. Worth one line.
- **[low]** Round-1's **L7** is unrepaired: §0.1 line 174 still shows `except AssertionError:` →
  `[]`. Round 1 called it cosmetic and the row's actual point holds.
- **[low]** The story's own header comment (line 19) still says *"`git status --porcelain` was empty
  before and after"*, describing the contexting pass. Harmless history, but it is the cleanliness
  phrasing the amendment removed everywhere else.

---

## PART 4 — INVARIANTS, RE-MEASURED BY EXECUTION

| invariant | measured | verdict |
|---|---|---|
| Full suite, `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`, everything on disk | **1,688 passed, 0 failed, exit 0** (1,688 dots, zero `F`/`E`/`s`) | ✅ §0.0's row is now TRUE |
| Test files | **122** | ✅ |
| `TC-ArgusAgent-DOCS-001-78` | passes; the module is 3 passed | ✅ |
| `len(SECTION_5_CONDITIONS)` | **7** | ✅ no eighth condition |
| `precision_evaluable` conjuncts | **4** (read from source) | ✅ |
| `len(_CORROBORATION_ASSERTION_CALLEES)` | **23**, file byte-unchanged vs HEAD | ✅ `DN-14-2-1` |
| `len(_ASSERTION_CALLEES)` | **88** (→ 89) | ✅ |
| `len(_MOCK_CALLEES)` | **10** | ✅ |
| `is_assertion_callee("AssertionError")` | **False** — the defect is real | ✅ |
| `_ASSERTION_NAMING_CONVENTION` | `\A_?assert\w*\Z`, case-sensitive | ✅ |
| `ASSERTION_DENSITY_FLOOR` / `MOCK_RATIO_CEILING` | `1/4` / `1/2` | ✅ no threshold moves |
| `vacuous_test.__all__` / `vacuous_vocabulary.__all__` | **9** / `['is_assertion_callee']` | ✅ |
| Re-export identity (AC6.4) | all three names are the **same objects** | ✅ (but see **C3**) |
| `"Error" in _ASSERTION_CALLEES` | **False** | ✅ stays out |
| All ten of §0.6's line counts, via the ceiling guard's own `_physical_line_count` | 455 · 796 · **1,159** · 1,031 · 1,065 · 791 · 1,132 · 1,127 · 328 · 976 | ✅ **all ten exact** |
| `_CEILING` / `_EXEMPT_BY_DESIGN` | 1,200 / **3** | ✅ |
| Ratified member count / adjudication rows / gate outcome | **5** / **31** / **BLOCKED** | ✅ `N` stays 5 |
| Both builders `--check` | exit **0** / exit **0** | ✅ |
| `V1.4` row in the protocol | **none** — all five mentions are explicit refusals | ✅ |
| `DF-13-5-A` open and unspent | ✅ ledger 4766 / 4777 | ✅ |
| Every AC-named path exists | ✅ 19 checked; `tests/test_vacuous_vocabulary.py` correctly absent (it is NEW) | ✅ |
| Story promotes nothing / moves no threshold | ✅ advisory tier only | ✅ |
| ACs individually testable | ✅ every AC names an executable observable | ✅ |
| ACs collectively sufficient | ✅ subject to C2 and C3 being omissions in the **tasks**, not in the ACs | ✅ |
| Story single-purpose | ✅ one name, one table, one direction | ✅ |

---

## PART 5 — THE TWO KNOWN `low` ITEMS, CONFIRMED

**1. `sprint-status.yaml`'s 16-6 comment is stale; the story file is correct.** Confirmed by reading
both. The comment still carries `183 : 2 over 5,085 python files, ~91x` (which AC1.5 has now demoted
to an expectation), `minions 13, xagents-webapp 1, agent-smith 16` (which §0.7 has now superseded
with three disagreeing columns), and the pre-repair *"FULL SUITE identically green (1,688 passed)"*
provenance. **The story file is authoritative and is correct on all three.** The amendment was
forbidden from touching sprint-status and did not: the value on disk is `ready-for-dev`, unchanged.
Not a defect.

**2. `ledger_closed_ids` reports `DF-13-5-A` from historical prose.** Confirmed **genuinely
pre-existing**, not introduced by the append. Proof: the analyzer returns the identical 35-id set
over the HEAD blob and over the working tree, and the symmetric difference of the two sets is empty.
The source is ledger line 4727, 962 lines above the append. The entry's own text at 4766/4777 reads
open and unspent, so the analyzer and the entry disagree — a real latent defect in the analyzer, but
one that predates this story. **See C1 for the consequence nobody has recorded.**

---

## WHAT MUST CHANGE BEFORE A DEV STARTS

All edits are to the **story file**, which is already inside AC6.1's write set. Two more are outside
this story (C1's second half).

1. **C2** — give AC5.2's two-way cross-reference a task (Task 3.4), and add
   `tests/test_vacuous_cross_language.py` to Task 7.3's expected porcelain.
2. **C3** — give AC6.4 a task: `vacuous_test.__all__` is 9, and the three re-exports are the same
   objects as the direct import.
3. **C4** — split §0.0's PATH ROOTS sentence so it stops placing `deferred-work.md`, `epics.md`,
   `architecture.md`, `precision-validation-protocol.md` and the story file under
   `validation-corpus/`.
4. **C5** — drop AC4.5's *"three of the five"* count, per §0.7's own rule.
5. **C1** — wrap round-1 report line 78, and correct `DF-16-6-D`'s *"wrapped every quotation"*
   sentence and its recurrence count. Not the dev's work; the next governance pass owns it.

Once C2–C5 land the story is, on the evidence, **dev-ready**. The research remains the strongest in
this epic, the ACs are internally consistent, and the baseline the story states is now the baseline
a dev will actually measure.

---

## REPRODUCTION

Every harness was written **outside the repository**, under the session scratchpad, and is
read-only. None is committed; none writes into `argus/`, `tests/`, `scripts/`, any corpus member, or
any validation-corpus artifact.

| harness | what it establishes |
|---|---|
| `scan.py` | drives `story_closure_claims` / `ledger_closed_ids` / the registry over the live 79-story corpus |
| `bytes.py` | the prefix-byte-identical append, the lone-`CR` count, the trailing newline, the 35 → 35 disposition set |
| `verbscan.py` | the guard's own predicate against the guard's own id pattern, per file, per line |
| `wide.py` | the same scan with a widened verb set against the true open-id set |

**Sprint status was NOT modified — it reads `ready-for-dev` on disk. The story file was NOT
modified. `deferred-work.md` was NOT modified. This report is the only file written.**
