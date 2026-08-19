# Sprint Change Proposal — 2026-08-19

**Project:** ArgusAgent (formerly APAA — AI Project Assurance Audit)
**Author:** Correct Course workflow (`bmad-correct-course`), batch mode
**Requested by:** XAgent007
**Trigger type:** Defect found by a post-hoc vacuity sweep of a CLOSED epic's guards — the sweep
Epic 14's `AI-E14-2` and Epic 13 FINAL's `SD-1` both named as Epic 15's highest-leverage
precondition. The sweep found what it was looking for, and in doing so found a live defect in the
shipped detector underneath it.
**Change scope classification:** **MODERATE** — one story added to an open backlog epic; no epic
created, no threshold moved, no corpus changed, no locked decision amended
**Status:** ✅ **APPROVED by XAgent007, 2026-08-19.**

> **Nothing under `argus/` or `tests/` was modified to produce this document.** Every number below
> was produced by out-of-tree probes that import the **shipped** `argus.index.ast_index.build_ast_index`,
> `argus.detectors.vacuous_test.VacuousTestDetector._score` and
> `argus.detectors.secret_scan.SecretScanDetector._scan` read-only, over synthetic fixtures in a
> `TemporaryDirectory`. `git status --porcelain argus tests` is unchanged from the start of the
> session. **This proposal fixes nothing. It decides what gets fixed, by whom, and in what order.**

---

## 0. What this document is for, in one paragraph

Epic 14 closed on 2026-08-18 having shipped **35** new guards. Eleven had been swept for vacuity
during Story 14.3's review, which found two vacuous. The remaining **24 had never been asked the
question**, and two consecutive retrospectives recorded that as the single highest-leverage item on
Epic 15's critical path — because Epic 15 is `DF-13-5-A`'s **ONE** round, and a round measured with
an instrument whose moat has unknown depth is a round spent either way. Those 24 have now been
swept, by mutation rather than by reading. The sweep's own verdicts are §1.2. What makes this a
change proposal rather than a report is §1.3: while establishing that one of those guards is a
tautology, the probe that would have made it real **flagged a genuine, fully-asserted, mock-free
test as heuristically vacuous.** That is the false-accusation class Epic 14 spent three stories
closing, arriving by a third route, in the instrument Epic 15 is about to run its one round on.

---

## 1. Issue Summary

### 1.1 What triggered this

`AI-E14-2` (Epic 14 retrospective, 2026-08-18) and `AI-E13F-1` / `SD-1` (Epic 13 FINAL
retrospective, 2026-08-19) both required the 24 unswept Epic-14 guards to be swept **before** Epic
15's candidate list is frozen, on the reasoning that Story 15.1 is selection-only and therefore does
not contend with the sweep. The sweep ran on 2026-08-19 at HEAD `57946a8`, in a detached worktree,
by applying **25 named mutations** one at a time to `argus/detectors/vacuous_test.py` and
`argus/detectors/provenance_scan.py` and observing which guards went red. The live tree was never
written to and every mutation was reverted immediately.

### 1.2 What the sweep returned

**24 swept: 22 REAL · 1 VACUOUS · 1 WEAK.** Combined with the 11 swept during Story 14.3's review
(which found `-131` and `-132` vacuous and floored both), Epic 14's record is **4 of 35** guards
that did not hold what their titles claimed.

| Guard | Verdict | Why |
|---|---|---|
| `DETECT-001-101`..`-106`, `-108`..`-117`, `-119`..`-122`, `VERDICT-001-116`/`-117` | **REAL** (22) | Each is killed by a *targeted* mutation of the mechanism its docstring names, not merely by a broad one. Every guard asserting an absence was separately checked for a precondition floor, and each has one that is load-bearing. |
| `DETECT-001-107` | **VACUOUS** | §1.4 |
| `DETECT-001-118` | **WEAK** | §1.5 |

**No unfloored negative was found among the 24.** The `-131` / `-132` failure shape — asserting a
conclusion about a mechanism the fixture never reaches — does **not** recur in `-101`..`-122`.

⚠️ **`AI-E14-2` is not discharged by this document.** Its DoD is *"each of the 24 ids carries a
recorded verdict"*, and a verdict recorded only in a session-scoped scratch file is not a record
this repository can read. Filed as `DF-15-2-C`.

### 1.3 The defect the sweep surfaced — measured, not inferred

**`argus/detectors/vacuous_test.py:958` scores over `source.splitlines()`. The Story 1.4 tree-sitter
index numbers lines by newline. Those are different functions.**

`str.splitlines()` splits on **eleven** things. `\n` is one of them. The others are `\r`, `\r\n`,
`\x0b` (VT), `\x0c` (FF), `\x1c` (FS), `\x1d` (GS), `\x1e` (RS), `\x85` (NEL), `\u2028` (LS) and
`\u2029` (PS). None of the last eight is a line break to Python's tokenizer or to tree-sitter. Each
occurrence therefore shifts the detector's view of the file **forward by one line relative to the
span the index handed it**, and the scored window silently loses its last line — which, in a
conventionally-written test, is where the assertions are.

Measured on a genuine, fully-asserted test **with no mocks at all**, through the REAL index
(`build_ast_index` + `VacuousTestDetector()._score`), varying only the number of form feeds:

| form feeds | assertion_sites | statements | density | `heuristically_vacuous` |
|---|---|---|---|---|
| 0 | 3 | 9 | 1/3 | `False` — correct |
| 1 | 2 | 8 | 1/4 | `False` — **exactly on the floor** |
| 2 | 1 | 7 | 1/7 | **`True` — FALSE ACCUSATION** |
| 3 | 0 | 6 | 0 | **`True` — FALSE ACCUSATION** |

`ASSERTION_DENSITY_FLOOR` is `1/4`, read from the shipped module. One form feed lands the test
*exactly* on the floor; two push it through.

**And it is not a form-feed defect.** The same fixture, with the separator placed inside a comment —
the one placement legal for all of them — measured through the real index, against a control:

| separator | survives the production read path? | detector's line count | index's line count | scored span | sites | stmts | density | flagged? |
|---|---|---|---|---|---|---|---|---|
| *(control — none)* | — | 10 | 10 | (1, 10) | 3 | 9 | 1/3 | no |
| `\x0b` VT | **yes** | 12 | 11 | (1, 11) | 2 | 9 | 2/9 | **YES** |
| `\x0c` FF | **yes** | 12 | 11 | (1, 11) | 2 | 9 | 2/9 | **YES** |
| `\x1c` FS | **yes** | 12 | 11 | (1, 11) | 2 | 9 | 2/9 | **YES** |
| `\x1d` GS | **yes** | 12 | 11 | (1, 11) | 2 | 9 | 2/9 | **YES** |
| `\x1e` RS | **yes** | 12 | 11 | (1, 11) | 2 | 9 | 2/9 | **YES** |
| `\x85` NEL | **yes** | 12 | 11 | (1, 11) | 2 | 9 | 2/9 | **YES** |
| `\u2028` LS | **yes** | 12 | 11 | (1, 11) | 2 | 9 | 2/9 | **YES** |
| `\u2029` PS | **yes** | 12 | 11 | (1, 11) | 2 | 9 | 2/9 | **YES** |
| `\r` CR | **no** | 12 | 11 | (1, 11) | 2 | 9 | 2/9 | (unreachable) |
| `\r\n` CRLF | **no** | 12 | 12 | (1, 8) | 0 | 6 | 0 | (unreachable) |

*"Survives the production read path"* was measured, not assumed: `argus/pipeline_stages.py:124` is
`(repo_root / rel_path).read_text(encoding="utf-8", errors="replace")` — universal newlines — so
`\r` and `\r\n` are normalised to `\n` before the detector ever sees them, and **the other eight
arrive intact.** That single fact explains both the defect and why the guards missed it: the CRLF
claim the guards test is true *by construction* in production, and the eight characters that are
**not** true by construction are the ones nothing tests.

**The root cause, stated as the thing it is:** there is an **unstated line-numbering contract**
between `argus/detectors/vacuous_test.py` and the Story 1.4 index. The detector consumes spans the
index numbered, and re-derives the lines those spans point into with a *different* function. A fix
that special-cases `\x0c` and leaves the contract unstated will be re-broken by the next exotic
separator on the list — there are seven more, and one of them is `\u2029`, which arrives in any file
that has passed through a word processor.

**Reproductions:** `ff4.py`, `ff5.py`, `sepscan3.py` (session scratchpad). They are **measurements,
not designs.** They must not be copied into the tree; the story writes its own guards.

### 1.4 `DETECT-001-107` — VACUOUS, and it is the guard whose entire subject this is

`tests/test_vacuous_detector.py:581`, `test_score_is_identical_on_CRLF_and_LF_source`. Headline
claim: *"the predicate reads SOURCE LINES, so line endings must not matter."*

```python
crlf = lf.replace("\n", "\r\n")
lf_score   = detector._score(lf.splitlines(),   edges, defn)
crlf_score = detector._score(crlf.splitlines(), edges, defn)
assert lf_score == crlf_score
```

**The test normalises both inputs itself, before the code under test runs.** Verified by execution:
`lf.splitlines() == crlf.splitlines()` is `True`; `edges` and `defn` are the same objects; `_score`
is a pure deterministic function (AR8, asserted in the module docstring). The headline assertion is
therefore `f(x) == f(x)` — a tautology **no line-ending defect can falsify.** No mutation in the
sweep's 25 could make it red on that arm.

Its only live assertion is the follow-up `assert lf_score.ast_corroborated is True`, which is a
**verbatim duplicate of `-104`**: byte-identical fixture, identical edge list, identical
expectation, reached through `_score` instead of `run`. `-107` is a strict subset of its neighbour.

### 1.5 `DETECT-001-118` — WEAK

`tests/test_vacuous_density.py:708`, `test_the_denominator_is_identical_on_CRLF_and_LF_source`.

Three of its four assertions are load-bearing (`statement_count == 4`, `assertion_sites == 1`,
`assertion_density == 1/4`) and mutations E, G and Q kill it through them. **The arm it is named
for cannot fail**, for two independently measured reasons:

1. `_score_one` (`tests/test_vacuous_density.py:119`) scores `source.splitlines()` of the
   **in-memory** string, so the denominator's input is byte-identical in both arms.
2. On Windows the on-disk bytes are not what the fixture says either. `write_text(source,
   encoding="utf-8")` uses `newline=None`. **Measured this session:** the "LF" arm is written with
   **11 CRLF / 0 bare CR** and the "CRLF" arm with **11 CRLF / 11 bare CR** (i.e. `\r\r\n`). Neither
   arm ever presents an LF file to the parser, and both produce an identical index.

`-118` misses the same class as `-107`, and it is the guard that owns the denominator — the half
Story 14.2 rewrote.

### 1.6 A SECOND live instance of the same contract breach, in a different detector

Recorded because it changes what the fix has to be. `argus/detectors/secret_scan.py:334` derives a
match's line as `source.count("\n", 0, match_start) + 1` — **newline-only, the index's convention** —
and `:434`/`:447` then index into `source.splitlines()` with that number to recover the line **text**
the suppression engine reads.

Measured against the shipped module, one separator inside a comment above the secret:

| separator | line the scanner reports | text the suppression engine is handed | text on that line |
|---|---|---|---|
| *(control)* | 2 | `AWS_KEY = "AKIA…"  # argus: ignore-secret` | same — **correct** |
| `\x0c` FF | 3 | `tail` | `AWS_KEY = "AKIA…"  # argus: ignore-secret` — **WRONG LINE** |
| `\x0b` VT | 3 | `tail` | — **WRONG LINE** |
| `\x1e` RS | 3 | `tail` | — **WRONG LINE** |
| `\u2028` LS | 3 | `tail` | — **WRONG LINE** |

**The measured direction is safe:** the operator's `argus: ignore-secret` is not seen, so the
suppression is dropped and the secret is **reported**. **The mirror direction — a suppression
comment on an unrelated line being applied to a real secret, silently — is NOT established here**
and this proposal does not assert it. Establishing it is the work of the ledger entry, not of a
sentence in this document.

The point for §2 is narrower and certain: **the contract is repository-wide, not detector-local.**
Two detectors, written by different stories, made the same mistake independently. A repair scoped to
one call site does not make the second one right, and does not stop the third.

---

## 2. Impact Analysis

### 2.1 Epic impact

**Epic 15** — one story added (**15.2**). The epic's charter — *"Make the Gate Evaluable — a bench
with the defect class in it"* — is **unchanged and needs no amendment**: a bench measured with a
known-broken instrument does not make the gate evaluable, so repairing the instrument is inside the
charter as written. The epic's **Covers:** line is extended to name it.

**Epics 13 and 14** — both `done`, both untouched. Epic 14 is not re-opened. This is deliberate: a
defect found after an epic closes is filed forward, not backfilled into a closed epic, and Epic 14's
retrospective is a record of what was true when it was written (§3.4 — records are superseded, never
erased). The `-107` / `-118` findings **supersede** Epic 14's guard count by adding verdicts to it;
they do not edit it.

### 2.2 Story impact — the id, the position, and why

**New story: `15.2` — key `15-2-the-detector-and-the-index-agree-on-what-a-line-is`.**
**Position: after `15-1` in both `epics.md` and `sprint-status.yaml`.**

**Why not renumber, giving the fix `15-1`?** Because in this repository an id is a **citation**, not
a schedule slot. `stories/15-1-a-bench-with-the-defect-class-in-it-chosen-before-anyone-looks.md`
exists on disk; `sprint-status.yaml:459` names it; the Epic-13 FINAL retrospective cites `15-1` by
id in §14, §14.3 (four times) and `SD-1`; `DF-13-5-A`'s pre-registered stopping rule names *"Epic 15
/ Story 15.1"* in the sentence that binds the operator. Renumbering to express an ordering would
invalidate all of them to encode information that a stated constraint carries better.

**The precedent is exact.** Story 14.3 was appended **after** 14.2 while carrying a *"strictly after
14.2"* ordering constraint on its own record and in `sprint-status.yaml` — order travelled as a
constraint, not as a number. `15.2` follows that form.

**The ordering constraint, stated:**

> **15.2 must reach `done` before any commit containing Argus output over any Epic-15 candidate.**
> **15.1 is selection-only** — its own AC states it does **NOT** ratify, does **NOT** run Argus over
> any candidate and does **NOT** adjudicate — so it is **NOT blocked by 15.2, and 15.2 is not
> blocked by it.** The two may proceed in either order, or concurrently. What must never happen is
> the third thing: **the bench being audited by the known-broken instrument.**

This is not a distinction without a difference. 15.1's AC1 requires its criteria to be frozen in a
commit that **precedes** every commit containing Argus output over any candidate. If 15.2 were made
a blocker of 15.1, that freeze would be delayed for no evidentiary gain — the freeze commit contains
no Argus output, so the instrument's state is irrelevant to it. Coupling them would cost schedule
and buy nothing.

| Story | Impact |
|---|---|
| **15.1** | **None.** Selection-only; no candidate is run. Its `DF-14-3-A`/`-B`/`-C` Python+TypeScript scoping rationale is untouched by 15.2 and must still be re-derived at create-story time as §14.3 of the Epic-13 FINAL retrospective requires. |
| **15.2** *(new)* | The whole of this proposal. |
| **`epic-15-retrospective`** | Key already exists at `backlog`. Unchanged. |

### 2.3 Severity — stated precisely, and one half of it deliberately left open

**What is established, at HEAD `57946a8`:** the defect produces a **false `heuristically_vacuous`
flag**, which is **ADVISORY**. It is emitted as a `RULE_HEURISTIC` finding and does **not** block a
build on its own.

**What is NOT established:** whether the corrupted line view can also carry a finding to
**verdict-eligibility** — i.e. whether the shifted span can make fact (b) (`ast_corroborated`)
read `True` on a test where it should read `False`. The mechanism makes it *conceivable* in both
directions, because fact (b) reads mock bindings and logical statement starts out of the same
shifted line list. **It was not measured**, for a stated reason: every reproduction above uses a
fixture with **no mock-bound assertions at all**, so the corroboration path was never exercised.
Running it would require a different fixture family, and building that fixture family is the
story's work, not a probe's.

**This proposal therefore asserts neither answer**, and makes determining it **AC1 of Story 15.2**.
The judgement recorded here is only this: *advisory* is the severity that is **measured**, and
`🔴-eligible` is a severity that is **unexcluded**. Recording it as advisory-and-settled would be the
inflation's mirror image, and this project has a name for closing a question by writing it down.

**Why it gates Epic 15 either way.** Epic 15's round produces a count of findings and asks whether
they are real. A detector that can flag a fully-asserted test on the strength of an invisible
character contributes findings to that count whose provenance nobody will reconstruct. Under
`DF-13-5-A` there is **one** round.

### 2.4 Blast radius — measured at HEAD `57946a8`, against NFR-M1's 1,200-line ceiling

`MAINT-001-03` pins the boundary by execution: **1,200 passes, 1,201 fails.**

| Module | Lines | Headroom | Note |
|---|---|---|---|
| `argus/detectors/vacuous_test.py` | **1,113** | 87 | The fix lands here. |
| `argus/detectors/provenance_scan.py` | **955** | 245 | Its docstrings at `:63-73`, `:132` and `:452` state *"line-terminator-agnostic by construction… every call site passes a `splitlines()`-derived line"* — **that prose becomes stale the moment 15.2 changes the decomposition**, and updating it is in scope. |
| `argus/pipeline.py` | **1,111** | 89 | ⛔ **Must not be added to.** Byte-fenced by Story 12.1; Story 10.3 already routed a field around it rather than through it. |
| `argus/detectors/secret_scan.py` | 583 | — | §1.6's second instance. **Not** touched by 15.2 — see §2.5. |
| `tests/test_vacuous_detector.py` | **1,161** | **39** | Where `-107` lives. `DF-14-3-H`. |
| `tests/test_vacuous_density.py` | **1,087** | 113 | Where `-118` lives. |
| `tests/test_vacuous_cross_language.py` | **1,027** | 173 | The cohesion module Story 14.3 opened. |

> **A correction, recorded rather than propagated.** This proposal was briefed with
> `argus/detectors/vacuous_test.py` at *"~1,041 lines"*. Re-measured with the ceiling guard's own
> method: **1,113**. The briefed figure is wrong by 72 lines and 87 lines of headroom is the number
> the story must plan against. `AI-E13F-*` records four occurrences of figures stated as measured
> and carried forward unmeasured; this is the fifth catch, and it is corrected here.

**⛔ The prescription, and it is not negotiable in a fix round:** `tests/test_vacuous_detector.py`
has **39 lines**. Making `-107` real needs a fixture through the real index, a control, and at least
eight rows. **That does not fit, and it must not be made to fit.**

- **Take the COHESION SPLIT** — the sanctioned remedy, on the `provenance_scan.py` /
  `test_vacuous_density.py` / `test_status_document_registry.py` precedent: a boundary chosen by
  what the cases are *about*, with no function split across it, and a docstring recording the
  rejected alternative.
- **⛔ No `_EXEMPT_BY_DESIGN` entry, and no shave.** `MAINT-001-04`'s registry may only **shrink**.
  `DF-14-3-H` forbids the exemption by name; `AI-E13-2` forbids it; `test_module_size_ceiling.py`'s
  `_REMEDY` forbids choosing whichever boundary helps the arithmetic most.
- **The split comes FIRST**, before the case that needs it — `DF-14-3-H`'s *"precondition, not
  afterthought"*.

⚠️ **`DF-14-3-H`'s `target_story` is now stale and is amended, not closed.** It points at `13-5`
as *"the next story on this detector; the split is its precondition"*. Story 13.5 is `done` and the
module is **still 1,161** — the split did not happen. The entry is re-pointed at `15-2` by an
append-only note. **It is not closed**, because it is not closed.

### 2.5 What is explicitly NOT in scope

Cited, not drifted into:

- **`DF-14-3-A`** — the test-function predicate is `startswith("test")`, case-**sensitive**, so Go's
  `TestXxx` and JUnit's annotation-marked methods are **never scored**.
- **`DF-14-3-B`** — Go selector-expression calls never reach the edge set, so a Go test's assertions
  are invisible.
- ⛔ **`-A` and `-B` are COUPLED and neither may be scheduled without the other.** The one-character
  fix to `-A` alone would score every Go test, find `assertion_sites=0` because `-B` hides the
  assertions, and **flag it** — converting Go's harmless silence into a **fresh false accusation
  across an entire language.** Restated here because 15.2 touches the same file and the temptation
  is adjacent.
- **`DF-14-3-C`** — callback test blocks (`describe`/`it` arrow functions) yield **zero**
  definitions, so idiomatic Jest / Mocha / Vitest suites are invisible.
- **`argus/detectors/secret_scan.py` (§1.6)** — a real, measured instance of the same contract
  breach, in a detector 15.2 does not own. Filed as `DF-15-2-B` with a named owner. **Reason for
  excluding it:** its measured direction is over-reporting, its dangerous mirror is unestablished,
  and folding a second detector into a story whose host test module has 39 lines of headroom is how
  a scoped repair becomes an unscoped one. **This is a deferral with a ledger entry, not an
  omission.**
- **Any threshold.** `ASSERTION_DENSITY_FLOOR`, `MOCK_RATIO_CEILING`, the ≥80% gate, FR34,
  `MANIFEST_FIELDS`, corpus membership and the adjudication record are all untouched. A defect in a
  line count is not a reason to move a floor (protocol §5, Story 13.3 / AC5).

---

## 3. Recommended Approach

### 3.1 Options evaluated

| # | Option | Verdict |
|---|---|---|
| 1 | **One story in Epic 15, ordered before any candidate is audited: repair the line-numbering contract in the vacuous-test detector, make `-107` real, strengthen `-118`; file the rest** | ✅ **Selected.** Puts the repair in the epic whose one round depends on it, at the only point where "before" is still available. |
| 2 | Re-open Epic 14 and fix it there | ❌ Epic 14 is `done` and its retrospective is written and registered. Re-opening a closed epic to backfill a later finding makes "done" mean "done unless something turns up", which is the state the three-outcome vocabulary exists to prevent. The finding is filed forward instead. |
| 3 | Special-case `\x0c` in `_score` and move on | ❌ **The trap, and it is named here so it cannot be chosen quietly.** It is one line, it makes the reproduction pass, and it leaves seven measured characters live plus an unstated contract for the next author to break. `DF-14-3-A`'s ⛔ is the same shape: the cheap fix that converts one defect into a wider one. |
| 4 | Fix both detectors (§1.6) in one story | ❌ Considered seriously, and rejected on blast radius rather than on principle. `secret_scan`'s defect is real and it is filed with an owner. Its measured direction is safe; the vacuous-test defect's is a false accusation; and the host test module has 39 lines. Two detectors and a cohesion split in one story is how a scoped repair loses its scope. |
| 5 | Ship Epic 15's round on the current instrument and disclose the residual | ❌ Available and honest, and it is `SD-1`'s stated alternative. Rejected because the defect is now **measured** rather than suspected: disclosing a known false-accusation path is not the same act as disclosing an unverified one, and `DF-13-5-A` allows **no second round** in which to correct for it. |

### 3.2 Selected — Option 1

```
Epic 15 (make the gate evaluable)

  15.1  a bench with the defect class in it        ─┐  selection only; NOT blocked by 15.2
        (criteria frozen in a commit)               │  and does not block it
                                                    │
  15.2  the detector and the index agree on         ─┤  ⛔ MUST be `done` before ANY commit
        what a line is                               │     containing Argus output over ANY
        (cohesion split FIRST, then the fix)         │     Epic-15 candidate
                                                    │
  ────────────────────────────────────────────────  ┴──>  the round, on a repaired instrument
```

### 3.3 Effort, risk, timeline

| | Assessment |
|---|---|
| **Effort** | **Medium**, and almost all of it is the cohesion split of `tests/test_vacuous_detector.py`. The production change is small; the guards it needs are not, and they cannot go where `-107` currently lives. |
| **Technical risk** | **Medium.** The fix changes what `_score` reads for **every** file, not only pathological ones. It must be shown by execution that the corrected decomposition is **identical** to the current one on all-`\n` source — which is every file in the corpus and every fixture in the suite — so the change is inert on the population that exists and corrective only on the population that does not yet. |
| **Regression risk of the split** | **Medium, and it is the real one.** Splitting the module that holds the moat's own false-accusation guards risks silently dropping a case (`AI-E3-1`). Mitigation: the id inventory before and after must be compared **by execution**, not by eye, and the count must be equal. |
| **Governance risk** | **Low.** No locked decision is amended, no threshold moves, no epic charter changes, nothing is closed that is not closed. |
| **Measurement risk** | **Medium — and it is scoped into AC1.** The verdict-eligibility question of §2.3 is genuinely open. If AC1 finds the answer is *yes*, the severity of this entire document changes from advisory to blocking-path, and the story must say so rather than keep the framing it was written with. |
| **Timeline** | Adds one story to a `backlog` epic. Blocks nothing that is currently `ready-for-dev`. |

---

## 4. Detailed Change Proposals

### 4.1 `epics.md` — 2 edits

**(a)** Epic 15's **Covers:** line gains *"· the line-numbering contract between the detector and the
1.4 index"*.

**(b)** Insert after Story 15.1:

> ### Story 15.2: The detector and the index agree on what a line is
>
> As the Argus maintainer,
> I want the detector to read the same lines the index numbered,
> So that an invisible character in a file cannot make Argus say a fully-asserted test asserts
> nothing.
>
> **Acceptance Criteria:**
>
> **Given** the false flag reproduced in `sprint-change-proposal-2026-08-19.md` §1.3 uses a fixture
> with **no mock-bound assertions**, so the fact-(b) corroboration path was **never exercised**, and
> the source proposal explicitly declines to assert an answer
> **When** this story completes
> **Then** it is **DETERMINED BY EXECUTION** whether the shifted line view can carry a finding to
> **verdict-eligibility** — i.e. whether the corrupted span can make `ast_corroborated` read `True`
> where a correct span reads `False`, or the reverse. The answer is **recorded as a measurement in
> either direction**, and if it is *yes* the story records that the severity is higher than the
> proposal that created it assumed. **Neither answer may be assumed, and "no reproduction found" is
> recorded as exactly that rather than as "cannot happen".**
>
> **Given** `str.splitlines()` splits on eleven things and the Story 1.4 index numbers lines by
> newline alone
> **Then** the fix is stated and implemented as a **LINE-NUMBERING CONTRACT** — the detector's line
> decomposition is the index's line decomposition — and **not** as a special case for any one
> character. A patch that names `\x0c` and no other character does **not** satisfy this AC.
>
> **Given** eight characters were measured to survive the production read path
> (`argus/pipeline_stages.py:124`, universal newlines) and to desynchronise the two views
> **Then** the fix is **MEASURED, not assumed, against every one of them**: `\x0b` (VT), `\x0c`
> (FF), `\x1c` (FS), `\x1d` (GS), `\x1e` (RS), `\x85` (NEL), `\u2028` (LS), `\u2029` (PS) — and
> `\r` and `\r\n` are measured **too**, with their normalisation at the read path re-verified rather
> than inherited from this list. A guard covers each, through the **real index**, and each is shown
> to go RED before the fix.
>
> **Given** the corrected decomposition changes what `_score` reads for every file
> **Then** it is demonstrated **by execution** that on all-`\n` source the corrected and current
> decompositions are **identical**, so the change is inert on the existing corpus and every existing
> fixture, and corrective only where the two views currently disagree. Any flag-count delta over the
> ratified corpus members is **measured and recorded as a number**, in both directions.
>
> **Given** `TC-ArgusAgent-DETECT-001-107` is **VACUOUS** — `lf.splitlines() == crlf.splitlines()`
> is `True`, so its headline assertion is `f(x) == f(x)` on a pure function, and its only live
> assertion duplicates `-104` verbatim
> **Then** `-107` is **REBUILT around the split rather than deleted** — the split is genuinely
> unguarded and deleting the guard would remove the id that names the subject — and it is
> demonstrated by a **mutation that makes it RED**, recorded in the story.
>
> **Given** `TC-ArgusAgent-DETECT-001-118` is **WEAK** — `_score_one` scores the in-memory string,
> and on Windows `write_text(newline=None)` writes the "LF" arm as CRLF (measured: 11 CRLF / 0 bare
> CR) and the "CRLF" arm as `\r\r\n` (11 CRLF / 11 bare CR)
> **Then** its terminator arm is made able to fail: the fixtures are written with the terminators
> they claim (`newline=""` or `write_bytes`), and the scored source is derived from **the file that
> was written** through the same read path production uses — **and its three load-bearing
> assertions are preserved unchanged.**
>
> **Given** `tests/test_vacuous_detector.py` is at **1,161 of NFR-M1's 1,200** — 39 lines — and
> `DF-14-3-H` requires the split **first**
> **Then** the **COHESION SPLIT** happens **before** any case is added, on the `provenance_scan.py`
> / `test_vacuous_density.py` / `test_status_document_registry.py` precedent, with **no function
> split across the boundary**, the rejected boundary recorded in the new module's docstring, and
> **NO `_EXEMPT_BY_DESIGN` entry and no shave** — `MAINT-001-04`'s registry may only shrink.
> **Given** splitting the module holding the moat's own guards risks silently dropping a case
> (`AI-E3-1`)
> **Then** the `TC-ArgusAgent-*` id inventory is compared **by execution** before and after, and the
> counts are shown equal.
>
> **Given** `argus/pipeline.py` is at **1,111** and byte-fenced by Story 12.1
> **Then** **no line is added to it.**
>
> **Given** `argus/detectors/provenance_scan.py:63-73`, `:132` and `:452` document themselves as
> *"line-terminator-agnostic by construction"* over a `splitlines()`-derived list
> **Then** that prose is **re-derived against the corrected decomposition** and corrected if it has
> become false. A stale docstring asserting an invariant that no longer holds is how the next author
> reintroduces this defect.
>
> **Given** `DF-14-3-A` and `DF-14-3-B` are **COUPLED**, and the one-character fix to `-A` alone
> converts Go's silence into a language-wide false accusation
> **Then** this story does **NOT** touch `_is_test_function`, the edge extractor, or
> `_ASSERTION_CALLEES`, and states plainly that Go and Java remain unscored and callback-style
> JS/TS suites remain invisible after it lands (`DF-14-3-C`).
>
> **Given** `argus/detectors/secret_scan.py` carries the **same** contract breach (`:334` counts
> newlines, `:447` indexes `splitlines()`), measured in the source proposal §1.6
> **Then** it is **cited and NOT fixed here** (`DF-15-2-B`), and the story records that the repair
> is scoped to one detector while the contract is repository-wide.
>
> **Given** AR8 (PURE scorer), AR4 (`Fraction`, never `float`), NFR-D2 (deterministic, zero-token)
> and NFR-P2 (the language conditional lives in `argus/index/`)
> **Then** all four hold unchanged, and **no threshold moves** — not
> `ASSERTION_DENSITY_FLOOR`, not `MOCK_RATIO_CEILING`, not the ≥80% gate.
>
> **Given** Story 15.1 is selection-only and does not run Argus over any candidate
> **Then** this story does **NOT** block it and is **NOT** blocked by it; but this story must be
> `done` **before any commit containing Argus output over any Epic-15 candidate.**
>
> **Given** local gates are Windows-only while CI runs an ubuntu matrix, and `\r\n` handling is
> exactly the class that differs across platforms
> **Then** this story is **not marked done on a local pass alone.**

### 4.2 `sprint-status.yaml` — 1 entry

`15-2-the-detector-and-the-index-agree-on-what-a-line-is: backlog`, inserted **after** the `15-1-…`
line and **before** `epic-15-retrospective`, carrying the ordering constraint (before any commit
containing Argus output over any candidate; not coupled to 15.1 in either direction) and the
split-first precondition. Every existing comment and the STATUS DEFINITIONS block are preserved
byte-for-byte; the file is edited surgically, never rewritten.

### 4.3 `deferred-work.md` — 3 new entries + 1 append-only amendment

| Id | Subject | Owner |
|---|---|---|
| **`DF-15-2-A`** | A vacuity sweep is in **no** definition of done. 4 of Epic 14's 35 guards did not hold what their titles claimed, and nothing in the loop asks the question — both times it was asked, it was asked by hand, after the fact. | **dev-loop orchestrator** (the phase rule) + **XAgent007** |
| **`DF-15-2-B`** | `argus/detectors/secret_scan.py` carries the same line-numbering contract breach (§1.6), measured. The safe direction is established; **the dangerous mirror is not**, and establishing it is part of the entry. | **XAgent007** (Engineering Lead) |
| **`DF-15-2-C`** | The 24-guard sweep's per-id verdict table has **no durable home in the repository**. `AI-E14-2`'s DoD requires each of the 24 to carry a recorded verdict; a scratch file is not a record. **`AI-E14-2` is therefore NOT discharged.** | **XAgent007** (Engineering Lead) |
| **`DF-14-3-H`** | **Append-only amendment, not a closure.** Its `target_story: 13-5` is stale — 13.5 is `done` and `tests/test_vacuous_detector.py` is **still 1,161**. Re-pointed at `15-2`. **The entry stays OPEN.** | unchanged |

⛔ **Nothing is closed by this proposal.** No `DF-*` id in this document sits beside a closure verb,
and `deferred-work.md` is **not** to be edited to make any guard quiet — that is `AI-E12-3`'s defect
inside the guard built to stop it.

### 4.4 `tests/test_status_document_registry.py` — 1 entry

This document is a status document. `TC-ArgusAgent-DOCS-001-22`'s glob closure resolves
`sprint-change-proposal-*.md` against the artifact tree and fails on anything unregistered, in
**both** directions. It is registered in `_STATUS_DOCUMENTS` as part of writing it — `AI-E12-1`'s
second half — with the registration verified in the established form: **`-22` observed RED against
this document before the line was added, and GREEN after, on the live tree.**

⚠️ **This file and this registry line must land in ONE commit.** `-22` closes in both directions:
the document without the entry and the entry without the document red `master` equally.

### 4.5 What this proposal does NOT touch

`ASSERTION_DENSITY_FLOOR` · `MOCK_RATIO_CEILING` · the ≥80% threshold · FR34 · corpus membership ·
`MANIFEST_FIELDS` · the adjudication record · `DF-13-5-A`'s pre-registered stopping rule · Story
15.1's scope, criteria or acceptance criteria · Epic 14's retrospective · Epic 13's retrospective ·
`E-PRD/prd.md` · `architecture.md` · any file under `argus/` or `tests/` other than the one registry
line in §4.4. **No epic is created and no epic charter is amended.**

---

## 5. The process lesson, recorded as a lesson

### 5.1 The number

Epic 14 shipped **35** guards. **4 did not hold what their titles claimed** — `-131` and `-132`
(found during Story 14.3's review, both floored), `-107` (vacuous) and `-118` (weak). That is
**11%**, in the epic chartered to stop a detector from asserting things it had not established,
inside that detector's own suite. Both sweeps were run **by hand, after the fact, by someone who
decided to ask.** Nothing in the loop asks.

### 5.2 Recommendation 1 — the standing rule: **YES, and it is already twice-resolved**

> *A guard that asserts an absence must first assert the precondition state that makes the absence
> meaningful, and must assert the mechanism directly rather than infer it from a `False`.*

This is `AI-E14-1`, carried forward as `AI-E13F-1`. Both retrospectives already answered **yes**.
This proposal adds two things rather than re-deciding:

1. **A fifth independent invention.** The rule has now been reinvented by `AI-E11-1`'s non-vacuity
   floor, `-115`'s floor in Epic 14, `corpus_read_proof` in Story 13.5, `-68`'s *"a detector that
   never ran produces zero of both"* — and, this session, by the sweep's own §4 check for
   precondition floors on the nine absence-asserting guards among the 24. **Five independent
   inventions is not a pattern; it is a missing standard.**
2. **A widening the four instances above do not cover, and it is what `-107` proves.** Every prior
   instance is about a guard asserting an **absence**. `-107` asserts a **presence** — an equality —
   and is vacuous anyway, because it computes both sides from an input it normalised itself. The
   rule as drafted would not have caught it. **The widening: a guard must assert that the input it
   varies actually differs at the seam it varies it across.** `-107` varies line terminators across
   a seam (`splitlines()`) that erases them; `-118` varies them across a `write_text` that rewrites
   them. Both are the same defect: **the variable under test was constant.**

⛔ **Register it, do not write it as prose.** `AI-E12-5` waited four retrospectives for exactly that
reason, and `AI-E13F-1` says so in its own text. The registered form is rule text + enforcing module
+ test ids in `architecture.md` §Enforcement, asserted present by its own guard as `-77` does.

**On mechanising it:** a general "is this guard vacuous?" check is not decidable and this proposal
does not pretend otherwise. What **is** mechanisable, and what this proposal recommends, is the
narrow, checkable half: **a guard that asserts `f(a) == f(b)` must first assert `a != b`.** That is
a two-line addition to a test, it is machine-checkable over the corpus of comparison assertions, and
it would have failed `-107` and `-118` on the day each was written. **Scoped into `DF-15-2-A`.**

### 5.3 Recommendation 2 — sweep in the definition of done: **YES, with the scope narrowed so it can actually run**

**A blanket "sweep every guard" DoD would not survive contact with a real story** — mutation
sweeping 35 guards is a session's work, and a DoD nobody can afford is a DoD that gets waived, which
is worse than not having one because it also teaches that DoD items are negotiable.

**The proposed shape, narrowed to what a story can carry:**

- **Any story that adds a guard asserting an absence, an equality, or an invariance** must, for each
  such guard, record **one mutation that was executed and observed to make it RED.** Not a claim
  that one exists — the mutation, named, and the observation.
- **Not** a blanket sweep of the module, the epic, or anything the story did not write.
- The **epic**-level sweep of everything the epic shipped stays where it already is: an action item
  with a named owner (`AI-E14-2`), run once per epic, not per story.

**Why this is affordable:** the sweep just run needed 25 mutations for 24 guards because it was
retrospective and had to rediscover each guard's intent from its docstring. **An author already
knows which mutation their guard is aimed at** — writing it down costs a line, and the two vacuous
guards in this epic would each have failed that line immediately.

**Both recommendations are filed as `DF-15-2-A` with named owners. Neither is implemented by this
proposal**, because a change to the loop's phase rules is not a change to this repository and
asserting it here would be a closure the ledger never received.

---

## 6. Implementation Handoff

**Scope classification: MODERATE** — backlog reorganisation within an existing epic, requiring
PO/DEV coordination but no replan.

| Role | Action |
|---|---|
| **PM / Architect (XAgent007)** | ✅ Approved. The judgement calls were: (a) filing forward rather than re-opening Epic 14; (b) `15.2` after `15-1` with order carried as a constraint rather than as a number; (c) leaving verdict-eligibility open as AC1 instead of settling it here; (d) excluding `secret_scan` with a ledger entry rather than folding it in. |
| **SM** | Apply §4.1–§4.4, then `create-story` for 15.2. **§0 must re-derive, at that moment:** all six line counts in §2.4; whether `-107` and `-118` are still at the lines cited; whether `DF-14-3-A` is still unfixed; and, per `AI-E13F-2` / `AI-E14-8`, **whether each AC's RED is reproducible on the tree as it then stands.** |
| **Dev** | **Split first, then fix, then guard.** `tests/test_vacuous_detector.py` has 39 lines and the split is a precondition, not an afterthought. |
| **Review gate** | The two things most likely to be got wrong: a fix that special-cases `\x0c` and satisfies the reproduction while leaving the contract unstated (§3.1 option 3), and a split that silently drops a case (§4.1's by-execution id inventory). |

**Sequencing invariant:** the cohesion split precedes the fix · the fix precedes the new guards ·
**15.2 precedes any commit containing Argus output over any Epic-15 candidate** · 15.1 and 15.2 are
independent of each other in both directions · nothing here reorders anything in Epics 13 or 14,
both of which are `done` and stay `done`.

---

## 7. Approval

✅ **APPROVED** by **XAgent007** on **2026-08-19** — §4.1 through §4.4 as written, **including**:

- the **id and position decision** of §2.2 — `15.2`, after `15-1`, order carried as a stated
  constraint because an id in this repository is a citation;
- the **open severity** of §2.3 — verdict-eligibility is **not established in either direction** and
  is determined by AC1 of the story rather than by a sentence here;
- the **cohesion split over any exemption** of §2.4, and the correction of the briefed 1,041 to the
  measured **1,113**;
- the **exclusion** of `secret_scan.py` from 15.2 with `DF-15-2-B` filed against it, and of
  `DF-14-3-A`/`-B`/`-C` with their coupling restated.

**No code was written and no defect was fixed by this document.** `argus/` and `tests/` are
byte-unchanged apart from the single `_STATUS_DOCUMENTS` registration line of §4.4, which exists
because this file exists. **Nothing was committed, staged or pushed.**

**Author's note, and it is the honest weak point.** §2.3 is the load-bearing uncertainty: this
document argues that a defect gating Epic 15's one round must be repaired first, while declining to
say whether that defect can reach a blocking verdict. Both halves are deliberate. The measurement
that would settle it needs a fixture family that does not exist yet, and building it is the story's
first acceptance criterion rather than a probe's afterthought. **This approval therefore approves a
story whose first task may raise the severity of the proposal that created it** — which is the
intended shape, and it is the same shape `sprint-change-proposal-2026-08-17b.md` was approved in.

**A second, smaller one, recorded rather than smoothed over.** The trigger for this whole document
was a housekeeping action item — sweep some guards nobody had asked about. It found a live
false-accusation path in the shipped detector. The lesson in §5 is not that the sweep was clever; it
is that **the sweep was optional**, ran once, ran late, and ran only because two retrospectives in a
row wrote it down and someone eventually did it.
