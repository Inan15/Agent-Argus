---
baseline_commit: 762a73ecd54beb20ec61e66fe834a2727708945c
---

# Story 15.1: A bench with the defect class in it, chosen before anyone looks

Status: ready-for-dev

| | |
|---|---|
| **Epic** | 15 — Make the Gate Evaluable — a bench with the defect class in it |
| **Story key** | `15-1-a-bench-with-the-defect-class-in-it-chosen-before-anyone-looks` |
| **Source** | **Operator decision (XAgent007), 2026-08-17** — NOT a change proposal; admitted on the Story 13.4 precedent · [epics.md](../epics.md) §Story 15.1 (`epics.md:2852`, working copy) |
| **Contexted on** | HEAD `f2189c1` (`docs(15-2): code review iteration 2 — VERDICT pass, story -> done`), **equal to `origin/master`, 0 ahead / 0 behind** |
| **Round** | ⛔ this story is the first half of **`DF-13-5-A`'s ONE permitted round**. See §2. |
| **Ordering** | **NOT** coupled to Story 15.2 in either direction (15.2 is `done` as of 2026-08-19). |
| **Scope** | **SELECTION ONLY.** It does not ratify, does not run Argus over any candidate, does not adjudicate. |

<!-- REWRITTEN 2026-08-19 by create-story. The 2026-08-17 file was a BACKLOG premise list written
     from the authorising conversation; its own head comment required every §0 premise to be
     re-derived by execution before dev. That re-derivation is §0 below. Two epics and five stories
     landed in between, and the instrument moved three times. Premises that survived are marked
     SURVIVES with the measurement; premises that did not are CORRECTED or VOID, with the original
     named as wrong. Nothing that survived re-measurement was dropped. -->

---

## Story

As the Argus maintainer,
I want a candidate bench of repositories selected against written criteria that are **frozen in git
before Argus is run over any of them**,
So that whatever precision it eventually measures means something.

### What this story IS

**Selection, and nothing else.** It produces (a) a frozen, written criteria set; (b) a candidate
list justified against it, with recorded exclusions; and (c) manifest rows that **cannot** count
toward `N` until the operator ratifies them. It is the first half of protocol §6's **R2**, arranged
so the second half stays the operator act the protocol requires.

### What it is NOT

- **NOT ratification.** Protocol §6 R2, verbatim: *"choosing which repositories are legitimate
  members, and fetching third-party source, are not autonomous acts."* This story prepares the
  decision; it does not take it.
- **NOT a run.** Argus's **detector** is not executed over any candidate here. That ordering is the
  whole point, and AC2 makes the ban structural rather than promised.
- **NOT adjudication.** That is R3 — a named human, protocol §4.
- **NOT a threshold / corpus-membership / FR34 / `protocol_cleared` change.** None is touched.
- **NOT a schema change.** `MANIFEST_FIELDS` is closed and stays closed; candidates use fields that
  already exist. No field is added.
- **NOT a commitment to clear the gate**, and **NOT licence to expand until it passes.** See §2.

---

## §0 — PREMISE RE-MEASUREMENT, executed 2026-08-19 at HEAD `f2189c1`

> Every premise the 2026-08-17 file carried forward was re-derived **by execution**, out of tree,
> read-only. `git status --porcelain` over `argus/` and `tests/` was empty before and after.
> `AI-E13F-2` asks §0 to carry per-AC RED reproducibility as well; that is §0.4.

### §0.1 Premises that SURVIVE, with the measurement

| # | Premise as written 2026-08-17 | Measured 2026-08-19 | Verdict |
|---|---|---|---|
| 1 | `VALIDATION_CORPUS` holds **7** rows; **5** eligible, all `provenance: independent`; **3 python + 2 typescript** among the eligible five | rows **7**, eligible **5**, all five `independent`, `Counter({'python': 3, 'typescript': 2})` | **SURVIVES — exact** |
| 2 | `MANIFEST_FIELDS` is closed and includes `eligible_for_n` + `ineligible_reason` | closed at **9** fields: `member_id, repository_url, commit_sha, licence, primary_language, provenance, eligible_for_n, ineligible_reason, adjudication_caveat`; `-22` checks the dataclass in both directions | **SURVIVES** |
| 3 | `CorpusMemberSpec.__post_init__` raises when `eligible_for_n=False` carries no reason | constructed with no reason gives `ValueError`; with a whitespace-only reason gives `ValueError` | **SURVIVES** (but see §0.2 #6 for what it does **not** do) |
| 4 | `VALIDATION_SET_FLOOR_N = 5`, resolved not restated (DN-3) | `validation_floor_n()` returns **5**, resolved through `argus.precision.replay_harness.registry_module()`; `meets_validation_floor()` is `True` at N=5 | **SURVIVES** |
| 5 | The **ONE-round** stopping rule, pre-registered 2026-08-17 before any repository was chosen | present verbatim in the ledger, un-dispositioned, `target_story: NONE`, owner XAgent007 | **SURVIVES — cited in §2, never re-litigated** |
| 6 | `SOURCING_RULE` already permits sourcing from a public index | present in `_manifest.py`, asserted by `-22` (>=25 words plus the word *adjudicat*) | **SURVIVES** |

### §0.2 Premises that did NOT survive — corrected, with the original named as wrong

**⛔ 1. AC3's Python-AND-TypeScript scoping rests on a premise that is measured FALSE in the
direction that matters. This is the most important correction in this document.**

AC3 as written scoped the bench to Python **and TypeScript**, excluding Go and Java because
`DF-14-3-A`/`-B` leave them unscored, on the reasoning that admitting an unscorable language *"would
inflate the N that satisfies the floor while contributing nothing to the N that gates."* Measured
2026-08-19, **TypeScript is in the same position as Go and Java, not a different one.**

Re-derived independently this session, read from the **git object database at each pin** (never the
working tree), through the **real** `argus.index.ast_index.build_ast_index` and the shipped
`_is_test_function`:

| Member | Pin | `.ts`/`.tsx` files | of those, **test files** | definitions extracted | **SCORABLE test functions** |
|---|---|---|---|---|---|
| `xagents-webapp` | `33a86525` | 810 | **279** | 452 | **1** |
| `agent-smith` | `9ab774d7` | 226 | **88** | 169 | **0** |
| **TOTAL** | | 1,036 | **367** | 621 | **1** |

**367 TypeScript test files across the two ratified TypeScript members yield ONE scorable test
function.** 269 of `xagents-webapp`'s 279 and 87 of `agent-smith`'s 88 are callback-style.

Reproduced from first principles on fresh fixtures through the same real index — the mechanism, not
just the number:

| Idiom | `is_test_file` | `ast_eligible` | definitions | **scorable test fns** |
|---|---|---|---|---|
| Jest `describe(...)` / `it(...)` arrow | True | True | **0** | **0** |
| Vitest `test('...', () => {})` | True | True | **0** | **0** |
| Mocha `describe(function(){ it(function(){}) })` | True | True | **0** | **0** |
| `function testAddsNumbers()` (Allman) | True | True | 1 | **1** |
| `class CalcTest { testAdds() {} }` | True | True | 2 | **1** |
| Python `def test_adds_numbers()` (control) | True | True | 1 | **1** |

**Every idiomatic Jest / Vitest / Mocha suite yields zero.** Two independent causes, both open and
both cited rather than fixed here: `DF-14-3-C` (`_DEF_KIND_BY_NODE` has no entry for a test declared
as a callback passed to a call, so `describe`/`it` bodies extract **no definitions at all**) and
`_is_test_function`'s case-sensitive `definition.name.startswith("test")`.

**What this changes and what it does not.** It does **not** widen the scope — Go, Java, PHP, C, C++,
Ruby and Rust stay out, and nothing here reopens `DF-14-3-A`/`-B`. It changes what a **TypeScript
candidate must demonstrate before it is worth one of this round's slots**, and it is answered by
`DN-15-1-3` plus AC3, not by silently dropping the language: the scoping instruction and the R2
ratification are both the operator's, and this story hands them the measurement rather than
pre-empting it.

**⛔ 2. `prd.md:190`'s *"31 findings from 2 of 5 members"* is SUPERSEDED and must be cited as
history, not as current corpus state.** The 2026-08-17 file's AC3 cited it as if live. Those 31
findings were produced by the working-tree-reading instrument, so which bytes they describe is not
established (`DF-13-5-B`, open, owner XAgent007). The current pin-verified state is §1's zero. The
*concentration* point AC3 made from it survives — the `N` that satisfies the floor and the `N` that
contributes are genuinely different numbers — but it must be sourced to Story 13.5's measurement,
not to the superseded one.

**⛔ 3. *"A corrected detector is EXPECTED to emit zero blocking findings"* was a FORECAST when
written. It is now a MEASUREMENT.** Story 13.5 re-measured through the corrected instrument and the
pinned reader: **0 blocking findings across all five members, five-of-five pin-verified**, 1,960
staged files all proved against their pins by git blob hash. The premise is confirmed and its
*status* changed from prediction to fact — exactly the drift §0 exists to catch. §1 carries the
figures with their predicates.

**⛔ 4. AC1's stated blocker is RESOLVED for the code tree — but not completely.** The Epic-13 FINAL
retrospective §14.3 called AC1 *"a blocker, not a caveat"*, because *"Epic 15's central evidentiary
claim is a claim about git history, and it cannot be established while the tree is uncommitted."*
Measured now: HEAD `f2189c1` **equals `origin/master`, 0 ahead / 0 behind**; `argus/`, `tests/`,
`deferred-work.md`, `architecture.md` and `stories/15-2-*.md` are all committed and pushed. **The
ordering claim is establishable today in a way it was not on 2026-08-17.**

⚠️ **The residue, measured and named because it is easy to miss:** `epics.md` **at `HEAD` ends at
Epic 13.** Epic 14, Epic 15, Story 15.1 and Story 15.2 exist **only in the uncommitted working
copy** — `git show HEAD:.../epics.md` yields Epic 13 as its last epic heading and nothing after. A
reader of git history at `f2189c1` cannot see that this epic exists. This does **not** block AC1 —
AC1 is a claim about the ordering of *this story's criteria commit* relative to *Argus-output*
commits — but AC1's commit must not be the only place Epic 15 exists. Recorded as a precondition on
the AC1 commit in AC1.4. **`epics.md` is not this story's file to fix** and it is not in the write
set; the dev agent raises it rather than editing it.

**⛔ 5. AC7's guard range `TC-ArgusAgent-PRECISION-001-21..-30` is short by one, and by three more.**
`tests/test_validation_corpus.py` (859 lines) runs `-21` through **`-31`**, plus
`TC-ArgusAgent-DOGFOOD-001-53`, `-54` and `-55`. `-31` is the one that matters most here: it asserts
`set(adjudication-set members) == {eligible members}` and `len(members) == VALIDATION_SET_FLOOR_N ==
5`. **Verified: candidate rows do not disturb it**, because candidates are ineligible and `-31`
closes over `eligible_members()`.

**⛔ 6. *"The guard is STRUCTURAL"* is true of the claim AC4 makes and FALSE of three claims a
reader will assume it makes.** `__post_init__` **returns early** immediately after the
ineligible-reason check, so for a row with `eligible_for_n=False` the sha, provenance and
AST-eligibility validations **never run**. Measured, by construction:

| Row shape (`eligible_for_n=False`) | Result |
|---|---|
| no `ineligible_reason` / whitespace-only reason | **RAISES** — correct |
| valid candidate row (reason present) | constructs — correct |
| `commit_sha='deadbeef'` (8 chars) plus reason | ⚠️ **CONSTRUCTS — no raise** |
| `commit_sha='zzzz'` (non-hex) plus reason | ⚠️ **CONSTRUCTS — no raise** |
| `primary_language='go'` / `'ruby'` plus reason | ⚠️ **CONSTRUCTS — no raise** |
| `primary_language='cobol'` (unknown to `LANGUAGE_BY_SUFFIX`) | **RAISES** (this check precedes the early return) |
| `provenance='thirdparty'` | **RAISES** (precedes the early return) |
| `eligible_for_n=True`, `commit_sha='deadbeef'` | **RAISES** |

**AC4's actual claim survives and is stronger than it looks:** a candidate cannot be folded into `N`
by flipping one boolean, because flipping `eligible_for_n` to `True` while the `ineligible_reason`
is still present raises *"an ELIGIBLE member carries an ineligible_reason"*. Promotion therefore
takes **two** deliberate edits, both visible in a diff. **What is NOT structural** is criteria 1, 5
and 7 on a candidate row: a candidate with a malformed pin, an unscorable language or a missing
licence constructs happily. **AC4.3 adds those guards, and they are the ones most at risk of
vacuity.**

**⛔ 7. The `DF-13-3-A` citation in criterion 7 teaches the wrong lesson.** The old file cited it for
*"what an unreachable pin costs"*. That entry's premise was **withdrawn on 2026-08-17**: the pin was
never unreachable — the depth-4 scan that filed the entry stopped one level short. Re-confirmed by
execution today (§0.3). The correct lesson, and the one criterion 7 should carry, is: **a path
scanned at the wrong depth is indistinguishable from an unreachable pin, and it cost this project a
🟠 ledger entry and seven findings' worth of doubt.**

**⛔ 8. Premise 5 — *"Epic 14 must be `done` before any candidate is run; selection MAY proceed in
parallel"* — is MOOT.** `epic-14: done` (dev-loop roll-up 2026-08-18; 14-1, 14-2, 14-3 and
`epic-14-retrospective` all `done`). The parallelism dispensation is no longer needed and should not
be carried forward as if it were live. `15-2` is also `done` (2026-08-19), so the Epic-15 ordering
constraint on any future *run* is already satisfied.

### §0.3 Corpus paths and pins, RE-DERIVED — every one of them, because a measurement over an empty or unreachable corpus reports 0 and looks identical to a real 0

Measured 2026-08-19 with `git -C <windows-path> cat-file -t <pin>` and `git rev-parse HEAD`, both
pure reads. **No checkout, stash, clean, reset, commit or worktree. Nothing was mutated.**

| Member | **Real path (measured)** | Pin | `cat-file -t` | Checkout `HEAD` today |
|---|---|---|---|---|
| `ai-body-runtime` | `D:/ProjectX/XAgents/XAgents/ai_body_runtime` | `4480ffde` | `commit` | `4480ffde` — on pin |
| `agent-markovich` | `D:/ProjectX/XAgents/XAgents/AgentMarkovich` | `a5616686` | `commit` | `a5616686` — on pin |
| `minions` | `D:/ProjectX/XAgents/XAgents/Minions` | `ec63b729` | `commit` | **`c2940d2f` — DRIFTED off pin** |
| `xagents-webapp` | `D:/ProjectX/XAgents/XAgents/XAgents-WebApp` | `33a86525` | `commit` | `33a86525` — on pin |
| `agent-smith` | `D:/ProjectX/XAgents/XAgents/XAgents/Agent-Smith` | `9ab774d7` | `commit` | `9ab774d7` — on pin |

**Five of five pins reachable.** Three findings the dev agent must carry:

1. **The two members sit at DIFFERENT nesting depths, and `DF-14-3-F` says otherwise.** That entry
   corrects `xagents-webapp` to `.../XAgents/XAgents-WebApp` — **correct, verified** — but describes
   it as *"the same extra nesting the ledger already records for `agent-smith`"*. It is **not the
   same**: `agent-smith` is at `.../XAgents/XAgents/XAgents/Agent-Smith` (tripled segment, depth
   five) and `xagents-webapp` at `.../XAgents/XAgents/XAgents-WebApp` (doubled, depth four). *"One
   level deeper"* is not a rule; each path must be resolved individually. **`agent-markovich` is at
   `AgentMarkovich` — no hyphen — while its `member_id` and its repository are both
   `Agent-Markovich`.**
2. **THREE DECOY TREES exist beside the real ones, carrying the SAME `origin` URL and the WRONG
   bytes:** `.../XAgents/Minions - Copy` (origin `varinderpratap/minions`, HEAD `1468536f`, pin
   **NOT** reachable, exit 128), `.../XAgents/XAgents-WebApp - Temp (Bulild & run Working)` (origin
   `varinderpratap/XAgents-WebApp`, HEAD `54e09cc5`, pin **NOT** reachable), and
   `.../XAgents/AgentMarkovich-old` (no origin, pin **NOT** reachable). **Matching the remote is not
   matching the tree.** Resolve a checkout by `cat-file -t <pin>` returning `commit`, never by name
   and never by remote.
3. **A Git-Bash path form fails.** `git -C /d/ProjectX/... rev-parse HEAD` returns **exit 128**
   (*"cannot change to ...: No such file"*). Both `D:/...` and `D:\...` succeed. Pass the **Windows**
   form from Python.

### §0.4 Per-AC RED reproducibility on the current tree (`AI-E13F-2` / `AI-E14-8`)

| AC | Is its RED reproducible on the tree as it stands today? |
|---|---|
| **AC1** (ordering, git) | **YES, in both directions.** `git merge-base --is-ancestor` and `git log <sha> -- <path>` both run against a real history at `f2189c1`. The negative control is available: paths under `validation-corpus/` already carry commits, so the predicate can be watched returning non-empty. |
| **AC2** (import ban) | **YES.** An `ast` walk of the harness module currently finds no `argus.detectors` import; adding one makes it RED. Directly modelled on `TC-ArgusAgent-PRECISION-001-28`, which already does this for network imports. |
| **AC3** (language scope) | **YES.** `AST_INELIGIBLE_LANGUAGES` and `LANGUAGE_BY_SUFFIX` are live, and the TS-visibility floor is reproducible now — §0.2 #1 **is** that reproduction. |
| **AC4** (candidate rows) | **PARTIAL, and this is the one to watch.** AC4.1/4.2 reproduce RED today (§0.2 #6 table). **AC4.3's new guards have no RED until they are written**, because the shapes they forbid currently construct silently. Each must be observed RED by a real executed mutation before it is trusted (`DF-15-2-A` arm (a)). |
| **AC5** (no source bytes) | **YES.** `-28`'s `rglob` over `tests/corpus/` is live; dropping any non-`.py`/`.md` file there makes it RED. |
| **AC6** (reasons and exclusions) | **YES**, by the `-24` >=8-word reason floor pattern, extended to candidates. |
| **AC7** (gates and CI) | **YES.** Suite and CI are both currently green and both observable. |

---

## §1 — WHY THIS STORY EXISTS: an empty denominator is not a score, and the reason is now MEASURED

Story 13.5 re-measured the gate through the corrected instrument and the pin-verified reader and
returned **`outcome = BLOCKED`, precision `UNEVALUABLE`**. The figures, **each with its predicate
stated**, because this project has had a figure stated-as-measured turn out wrong **five separate
times this week** (Epic-13 FINAL retrospective §5.3 — four in-session plus a fifth at the epic
boundary; the create-story pass for 15.2 corrected four more):

> **1,960** in-scope source files read (= 15 + 65 + 583 + 862 + 435, reconciling exactly) ·
> **828** test **files** · **5,129** test **functions** scored · **1,249** **files** flagged ·
> **4,284** advisory **findings** · **0** blocking findings · **1,960/1,960** files proved against
> their pins by git blob hash · byte-reproducible across two runs for all five members.

⚠️ **The 1,249 is an ALL-DETECTOR flagged-FILE count, not a test-function count** — set beside
*"5,129 test functions scored"* it invites exactly the wrong reading. Story 13.5 records the
distinction explicitly (D-4): the **vacuous-test** flagged population is **269 files**, and
`vacuous_test_heuristic` totals **1,032** over 1,960 files; `vacuous_test_ast` is **0**.

**An empty precision denominator is `UNEVALUABLE` by construction** (`architecture.md`,
*Adjudication-record enforcement*, property (b) — the alternative was the `Fraction(1, 1)`
convention that read as *"cleared"*). Clearing needs findings that are **REAL**, which needs a bench
that **CONTAINS THE DEFECT CLASS**.

### §1.1 ⛔ THE NEW MEASUREMENT — why the corpus returned zero, established without running the detector

Executed 2026-08-19 over the three ratified **Python** members, reading each file from its **pinned
git object**, using **text patterns only — the detector was not imported**:

- `MOCK_BIND` = `\b(?:MagicMock|AsyncMock|Mock|patch|mocker\.patch|create_autospec|NonCallableMock)\s*\(`
- `MOCK_ASSERT` (strict) = `\.(?:assert_called(?:_once|_with|_once_with)?|assert_any_call|assert_has_calls|assert_not_called|assert_awaited\w*)\s*\(|\.call_count\b|\.called\b`
- test-file predicate = `test_*.py` or `*_test.py`

| Member | Python test files | files binding a mock | files with a mock assertion | **BOTH (co-occurrence)** |
|---|---|---|---|---|
| `minions` @ `ec63b729` | 286 | 21 (7%) | 3 (1%) | **1** |
| `agent-markovich` @ `a5616686` | 26 | 0 | 0 | **0** |
| `ai-body-runtime` @ `4480ffde` | 3 | 0 | 0 | **0** |
| **TOTAL** | **315** | **21** | **3** | **1 (0.3%)** |

**Predicate sensitivity, stated rather than hidden**, because an unnamed predicate is how a figure
becomes folklore: under a **looser** mock-assertion pattern (`assert_called|assert_any_call|
assert_has_calls|assert_not_called|assert_awaited|call_count|\.called\b|\.call_args`, unanchored)
the co-occurrence count on `minions` rises **1 to 6** (2.1% of 286). **Both figures are reported.
The conclusion is invariant to the choice.**

**This is the single most useful fact in this story.** The gate returned zero not because the
detector is mysteriously silent, but because **the bench does not contain the defect class at all** —
across 315 Python test files at five pinned trees, between **one and six** files carry even the
*co-occurrence* of a mock binding and a mock assertion, before any question of whether the SUT
result is discarded. And it is established **without running Argus over anything**, which is
precisely the discipline the rest of this story is built on.

### §1.2 What the defect class IS, since Epic 14 — narrow and specific

`Vacuity-corroboration enforcement` (`architecture.md`, added 2026-08-17, implemented by Story
14.1): *"a `vacuous_test_ast` finding is verdict-eligible ONLY on evidence that the asserted values
do not derive from the SUT — NEVER on the mere presence of a mock."* Fact (b), from the detector's
own contract, holds **iff all three**:

1. at least one **SUT call is DISCARDED** (its whole logical statement is that call and nothing
   else), **and**
2. **NO** SUT call is **CONSUMED** (bound, nested, asserted on, compared, chained — or inside
   `pytest.raises`/`assertRaises`/`pytest.warns`, which is CONSUMED **by construction**, because
   raising IS the observation), **and**
3. at least one assertion references a **mock-bound name**.

**"A test that constructs a mock" is the OLD, WRONG definition** — the one that measured **0 TP /
26 FP** over the ratified corpus, and under which `ast_corroborated` was equivalent to
`mock_sites >= 1` in **1,835 of 1,836** flagged tests. **A criterion built on "uses mocking" is a
criterion built on the refuted definition.** `DN-15-1-1` is the answer.

Epic 14 also widened the **density** vocabulary to **88** names against a **frozen 23-name**
corroboration table (`DN-14-2-1` — corroboration and density read **different** vocabularies;
re-measured this session: `_ASSERTION_CALLEES` = 88, `_CORROBORATION_ASSERTION_CALLEES` = 23,
`_MOCK_CALLEES` = 10), replaced fact (b) with a provenance-shape predicate, and corrected a
**1.907x** inflated denominator to **1.0000x** exact. **Neither table is touched by this story.**

### §1.3 The failure mode this story is built to prevent

Not *"too few repositories."* It is **choosing repositories after seeing what Argus says about
them** — which the Story 13.1 amendment already rejected by name, refusing *"an externalization gate
clearable by a corpus the team authored, planted, and wrote the answers for."* Selecting on the
tool's **output** is that same fallacy wearing public repositories as a disguise.

**The line, stated exactly, because the whole story turns on it:**

> A criterion may reference the **defect's DEFINITION**. A criterion may never reference the
> **tool's VERDICT**.

Selecting repositories likely to contain the defect is ordinary benchmark design — a bench for a
null-pointer analyser is chosen from code that dereferences pointers. Selecting repositories the
detector already flagged is criterion-shopping. AC2 makes the difference **mechanically checkable**
instead of assertable.

---

## §2 — ⛔ THE PRE-REGISTERED STOPPING RULE. Cite it. Do not re-litigate it. Do not execute its branch.

`DF-13-5-A` was answered **2026-08-17 by XAgent007**, *"before Story 13.5 ran, before Epic 15's
bench was chosen, and before any number existed."* Quoted **verbatim** from the ledger:

> **PRE-REGISTERED, 2026-08-17.** If Story 13.5 returns `UNEVALUABLE`, we pursue option **(a)**:
> **ONE** bench-expansion round of 12–20 independently selected repositories (Epic 15 / Story
> 15.1). If that round produces adjudicable findings and precision lands **≥80%**, the gate
> clears. If it produces **ZERO** blocking findings, **or** precision lands **below 80%**, we take
> option **(b)**: the FR34 disclosure **stands for V1.5**, attested externalization is **not
> pursued in this phase**, and the next attempt requires a **materially better detector — NOT a
> bigger bench.**
>
> **ONE round is the load-bearing word.** Without a stopping rule, *"expand the bench"* becomes
> *"keep expanding until it passes"*, which is corpus-shopping with extra steps. A pre-committed
> single round cannot drift into it.
>
> **What a zero-finding round MEANS, named in advance so it cannot be re-read later:** not *"we
> need 40 repositories"* — it means the detector is too conservative to be a product, and the
> answer moves to promoting a more reliably detectable rule to verdict-eligible, or to the
> coverage ledger as the product. Neither is scheduled here.

**Binding consequences for the dev agent, stated so this story cannot be read as licence:**

- This story **selects once**. It does not contain an *"if the yield looks thin, add more"* branch,
  and the dev agent must not add one. A second round requires a **new operator decision**, taken
  outside this story.
- The **branch is not this story's to take**. The rule *"resolves by execution of the rule, never by
  re-opening it"*, and the entry stays open and un-dispositioned. Story 15.1 does not even reach the
  branch point: it selects, and the operator ratifies.
- **`DF-13-5-A` is CITED here. This story disposes of nothing.**
  (`TC-ArgusAgent-DOCS-001-78` has gone RED three times this week from prose that put a ledger id
  beside a closure verb — see §Writing rule below.)
- **Epic 15 does not clear the gate. It makes the gate evaluable.** The ≥80% threshold, the corpus
  floor, FR34 and `protocol_cleared` are **unchanged by this story**.

---

## Acceptance Criteria

### AC1 — The criteria are frozen in a commit that PRECEDES every commit containing Argus output over any candidate, and the check is MECHANICAL

**Given** an intention to pick-before-looking is not evidence of having done so, and **git history
is the evidence, while an asserted intention is not**:

**AC1.1** The selection criteria (`DN-15-1-1`..`-3` resolved) and the **full candidate list** land in
**their own commit**, containing no Argus output over any candidate. That commit's **40-hex sha is
recorded in this story file** (§Dev Agent Record and §Change Log).

**AC1.2** A guard in `tests/test_validation_corpus.py` asserts, over real git history:
- the recorded criteria sha **resolves** (`git cat-file -t` returns `commit`) — *the precondition
  without which every assertion below is vacuous*;
- it is an **ancestor of `HEAD`** (`git merge-base --is-ancestor`);
- **no commit reachable from the criteria sha touches any declared candidate-output path.**

**AC1.3 — the non-vacuity floor, and it is not optional.** This guard asserts an **absence**, which
is this project's signature defect (§Guard vacuity). It must pin the preconditions that make the
absence meaningful, each asserted **before** the absence:
- the declared candidate-output path set is **non-empty**;
- `git log` over a **control path known to have commits** returns **non-empty**, proving the
  invocation is capable of finding something (a misspelled path returns empty and reads identical to
  a clean ordering);
- the ancestry predicate is driven to **both** outcomes — an ancestor sha and a non-ancestor sha —
  so it is watched **failing**, not only passing.

**AC1.4 — precondition on the AC1 commit.** Per §0.2 #4, `epics.md` at `f2189c1` **ends at Epic 13**,
so Epic 14 and Epic 15 exist only in an uncommitted working copy. The dev agent **records this on the
AC1 commit** and **raises it**; it does **not** edit `epics.md`, which is outside this story's write
set and carries unrelated uncommitted work.

*Guard ids: allocate the next actually-free ids in the `PRECISION-001` range and record them. Never
renumber an existing id — an id in this repository is a citation.*

### AC2 — Every criterion is decidable WITHOUT the detector, and the ban is STRUCTURAL

**AC2.1** Each criterion is observable from the repository alone, **before** Argus's detector is run
over it. The criteria are exactly these:

| # | Criterion | Decided by | Why |
|---|---|---|---|
| 1 | Primary language **Python**; **TypeScript only** if it clears the visibility floor of AC3.2 | file-suffix fold through `LANGUAGE_BY_SUFFIX` | §0.2 #1 |
| 2 | **>= 50** test files by the language's naming convention, **AND >= 10** files satisfying the `DN-15-1-1` co-occurrence predicate | text patterns over the pinned tree | `DN-15-1-2` — a suite-size floor alone is measured to be uninformative |
| 3 | **Mock-assertion CO-OCCURRENCE** (`DN-15-1-1`), never "uses mocking" | text patterns | §1.2 — "constructs a mock" is the refuted definition |
| 4 | **>= 2 years** of commit history | `git log --reverse --format=%cI` first entry | tests need time to rot; a new repo's tests have not had it |
| 5 | **Permissive licence**, recorded **verbatim** from the tracked licence file | tracked `LICENSE`/`COPYING` at the pin | the schema requires it, and ratification must be informed |
| 6 | **Independent provenance** — nothing Argus was developed against, and (see AC2.3) **third-party** | operator-verifiable metadata | the `argus-self-audit` row is excluded for exactly this |
| 7 | **Resolvable pin** — a 40-char lowercase-hex sha reachable at a path resolved **individually** | `git -C <windows-path> cat-file -t <sha>` returns `commit` | protocol §4's determinism precondition; §0.3's decoys and depths |

**AC2.2 — THE IMPORT BAN, and it is the strongest guard in this story.** The selection harness may
import `argus.index.*` (which measures whether a test is **visible** — the instrument's *reach*) and
must **NEVER** import `argus.detectors.*` (which measures whether a test is **guilty** — the
instrument's *output*). Enforced by an `ast` walk over the harness module, on the
`TC-ArgusAgent-PRECISION-001-28` pattern already used for network imports, with `-28`'s own
non-vacuity floor copied: **the walk must find imports at all**, or the closure is broken rather than
clean. This is what converts *"we did not look"* from a promise into a property.

**AC2.3 — a recorded limitation, not a gap.** `provenance` is a **closed** three-value vocabulary
(`independent | self | superseded`), and `_manifest.py`'s own comment states plainly that
`independent` *"means what it has always meant in this project's record — NOT the tool auditing
itself ... It does NOT mean third-party."* Criterion 6 is **stricter than the field can express**,
and `MANIFEST_FIELDS` stays closed, so **the third-party property is carried in the candidate's
`ineligible_reason` / `adjudication_caveat` prose and enforced by selection, not by the schema.**
Recorded here because a reader who assumes `provenance: independent` means arms-length would misread
the bench. **No field is added.**

**AC2.4** The story records **why criterion 3 is legitimate and criterion-shopping is not**, in the
§1.3 form: a criterion may reference the defect's **definition**; never the tool's **verdict**.

### AC3 — Scoped Python and TypeScript, with TypeScript carrying a MEASURED visibility floor

**AC3.1** Go, Java, PHP and the four `AST_INELIGIBLE_LANGUAGES` (`c`, `cpp`, `ruby`, `rust`) are
**excluded**, with `DF-14-3-A`/`-B` cited and **not reopened** — they are ⛔ **coupled**, and fixing
`-A` alone would convert Go's silence into a language-wide false accusation.

**AC3.2** A **TypeScript** candidate is admitted only if it clears an **extractor-visibility floor**,
because §0.2 #1 measured 367 TS test files yielding **one** scorable test function. The floor is
stated as a number and measured **through the index only** (permitted by AC2.2), never through the
detector: **>= 25 scorable test functions** — definitions of `kind == "function"` whose name starts
with lowercase `test`, or class methods of that shape — at the candidate's pin.

**AC3.3** Every TypeScript candidate records its **measured scorable-test-function count** beside its
raw test-file count, so the operator sees at R2 what it would actually contribute. If **no**
TypeScript candidate clears AC3.2, the story records **that outcome as a measurement** and the bench
is Python-only **for this round** — recorded as a finding, never as a scope change taken by this
story. **The decision to collapse the bench to Python-only is the operator's at R2; this story does
not pre-empt it and does not widen the scope to compensate.**

**AC3.4** The concentration point is preserved and **re-sourced**: the `N` that satisfies the floor
and the `N` that contributes are different numbers. Cited to **Story 13.5's pin-verified
measurement**; `prd.md:190`'s *"31 findings from 2 of 5"* cited as **history** under `DF-13-5-B`,
never as current corpus state (§0.2 #2).

### AC4 — A candidate cannot silently become a member, and the parts that are NOT structural get guards

**AC4.1** Every candidate enters `tests/corpus/_manifest.py` with `eligible_for_n=False` and
`ineligible_reason="candidate — awaiting operator ratification (protocol §6 R2)"`.

**AC4.2** The promotion path stays **structural** and is asserted in **both directions**: the row
validates at construction, and flipping `eligible_for_n` to `True` while the reason remains **raises**
(*"an ELIGIBLE member carries an ineligible_reason"*). Promotion therefore takes **two** deliberate
edits, both visible in a diff. **`MANIFEST_FIELDS` stays closed; no field is added**, and
`TC-ArgusAgent-PRECISION-001-22` stays green **without amendment**.

**AC4.3 — the three checks `__post_init__` does NOT perform on a candidate row** (§0.2 #6) are added
as guards over `VALIDATION_CORPUS`, **not** as new `__post_init__` branches — a new branch would
change behaviour for the five ratified rows, which is outside this story:
- every candidate's `commit_sha` is **40 lowercase hex** — measured today, an 8-char or non-hex sha
  constructs silently;
- every candidate's `primary_language` is **not** in `AST_INELIGIBLE_LANGUAGES` and is within AC3's
  scope — measured today, `go` and `ruby` construct silently;
- every candidate carries a **non-empty licence**, recorded verbatim.

**AC4.4 — non-vacuity for each AC4.3 guard.** Each asserts a **negative** and must therefore pin its
precondition: the candidate population is asserted **non-empty first**, and each guard is driven RED
by an **executed** mutation of a real row — not a claim that one exists. This is `DF-15-2-A`'s arm
(a), and the reason it exists is that **4 of Epic 14's 35 guards** did not hold what their titles
claimed.

**AC4.5** `-31` is re-verified green: `set(adjudication-set members) == {eligible members}` and
`len(members) == VALIDATION_SET_FLOOR_N == 5` — i.e. **`N` is unchanged at 5** and the adjudication
set is undisturbed. `eligible_member_count()` is asserted **still 5** after the candidates land.

### AC5 — Metadata and a pin, never source

**Given** NFR-S1 forbids third-party source bytes in this repository and in every artifact
**Then** a candidate is **metadata and a pin**, exactly as the five ratified members are. Nothing in
this story fetches, vendors or commits third-party source; `DN-5` holds (nothing in the module
fetches) and `TC-ArgusAgent-PRECISION-001-28`'s `rglob` over `tests/corpus/` stays green.

**Both corpus checkouts and every candidate tree are live third-party trees — strictly read-only:**
no `checkout`, `stash`, `clean`, `reset`, `commit` or leftover worktree, per *Corpus-pin provenance
enforcement*, which records that **no corpus member's working tree is ever mutated** and that
`ls-tree` plus `cat-file` are pure reads.

### AC6 — Rejections are recorded, not silent

**AC6.1** The target is **12–20 candidates** for **>= 10 ratified** — `DF-13-5-A`'s own number.
**AC6.2** The story records **why each candidate was chosen**, against each of the seven criteria,
with its measured figures.
**AC6.3** The story records **every repository considered and rejected**, naming **the criterion that
rejected it**. *An exclusion without a reason is an oversight wearing a decision's clothes* — the
DN-4 rule applied to candidates, and the same >=8-word substance floor `-24` already enforces on the
two recorded exclusions.
**AC6.4** Criterion 2's floor is read against `DF-14-3-C` for any TypeScript candidate, per AC3.2 —
never against a raw test count.

### AC7 — Gates, CI, and hand-off

**AC7.1** `tests/test_validation_corpus.py` (`TC-ArgusAgent-PRECISION-001-21`..**`-31`** plus
`TC-ArgusAgent-DOGFOOD-001-53`..`-55` — §0.2 #5) are green.
**AC7.2** `argus/` is **byte-unchanged** — asserted by `git diff --stat argus/` being empty, not by
inspection.
**AC7.3** Full suite green: **baseline 1,645 collected**, exit 0, **0 skipped**, with
`ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`. A `pytest.skip` is a **FALSE GREEN**; a **named `Unevaluable`
failure** is the correct pattern (`tests/test_vacuous_density.py` is the model).
**AC7.4 — the CI obligation, CONCRETE rather than a disclaimer.** Local gates are Windows-only and
this repository has shipped POSIX-only bugs out of a green Windows run. **CI is real now**: HEAD
`f2189c1` is green on run **`32225333417`** (*ArgusAgent Repository Audit & Assurance CI*,
ubuntu-latest × **3.10 / 3.11 / 3.12**, all three legs `success`) and run **`32225333384`**
(*Security Shield*). **This story is not marked done until a CI run id is recorded together with the
sha it covers**, in the `_executed_gate_citations` run-id-plus-sha form, for the commit carrying its
delta. **A local pass alone does not discharge AC7.**
**AC7.5** The story hands the operator **one reviewable list** for the R2 ratification act: per
candidate, the seven criteria with measured values, the pin, the resolved path, the licence verbatim,
and (for TypeScript) the AC3.2 count.

---

## Dev Notes

### Decisions this story TAKES, each with its rejected alternative

**`DN-15-1-1` — criterion 3 is MOCK-ASSERTION CO-OCCURRENCE, not "uses mocking."**
A candidate qualifies on a **per-repository rate** of test files that contain **both** a
mock-primitive binding **and** an assertion on a mock-derived value. The predicates are declared **in
code**, as named module-level constants beside the harness, never retyped into prose (`AI-E9-7`; and
§1.1's 1-versus-6 sensitivity is exactly why).

- *Rejected — "declares a mock dependency in `pyproject.toml` / `package.json`":* this is the
  **refuted definition** (§1.2). It selects the population that measured **0 TP / 26 FP**, and it is
  satisfied by 21 of `minions`' 286 test files while only **1** carries the co-occurrence.
- *Rejected — "imports `unittest.mock`":* the same defect, one notch weaker.
- *Recorded limitation:* co-occurrence is a **text proxy** for facts (a)+(b); it cannot see whether
  the SUT result is **discarded** versus **consumed**, which is what actually decides eligibility. It
  is deliberately **broader** than the detector — a bench must be able to contain true negatives, or
  precision is unmeasurable. It is a proxy for the **DEFINITION**, never for the verdict (§1.3).

**`DN-15-1-2` — the size floor is a PAIR of numbers, and the second one is the real floor.**
**>= 50** test files by naming convention **AND >= 10** co-occurrence files.

- *Why 10:* the current five-member corpus carries **1** co-occurrence file across 315 Python test
  files (§1.1) and returned **0** blocking findings. Twelve to twenty candidates at >= 10 each puts
  the bench between **120 and 200** such files against today's **1** — an **order-of-magnitude**
  argument, stated as such and **explicitly not a prediction** that the detector will flag any of
  them. It cannot be: predicting the yield would be looking.
- *Rejected — a raw test-count floor ("a large suite"):* measured uninformative. `minions` has
  **286** Python test files, the largest in the corpus, and contributes **one** co-occurrence file.
  Suite size does not carry the defect class.
- *Rejected — deriving the floor from the ≥80% gate arithmetic:* that reasons backwards from the
  number the round is supposed to measure, which is corpus-shopping in a spreadsheet.

**`DN-15-1-3` — TypeScript is kept in scope and carries an extractor-visibility floor (AC3.2).**

- *Rejected — keeping TypeScript on the epic's wording alone:* §0.2 #1 measures it doing the exact
  thing AC3 forbids — inflating the `N` that satisfies the floor while contributing nothing to the
  `N` that gates. Carrying it silently would be propagating a premise measured false.
- *Rejected — dropping TypeScript from the bench unilaterally:* the language scoping and the R2
  ratification are both the **operator's**, and narrowing inside a create-story pass would take a
  decision the protocol assigns elsewhere. Kept in scope, gated by a measured floor, with the
  measured reality on the record — so the operator decides at R2 against a number rather than an
  impression.
- *Rejected — filtering TypeScript candidates for non-callback style as a bare preference:* that
  would be a selection criterion derived from a **defect** (`DF-14-3-C`) presented as a design
  choice. AC3.2 is the same filter **recorded as what it is**, with the ledger entry named.
- *Recorded — is running `build_ast_index` over a candidate "looking"?* **No, and the line is
  AC2.2's.** The index measures whether a test is **visible**; the detector measures whether it is
  **guilty**. Using the index to size a candidate's scorable population is measuring the
  instrument's *reach*, not reading its *output* — and the ban on the latter is enforced by an `ast`
  walk, not by this paragraph.

### External prior art — checked so this story does not reinvent a wheel, and rejected with reasons

Searched 2026-08-19. **Titles, venues and artifact locators were verified; the papers themselves
were NOT read, and nothing below is cited as a measurement.** Recorded because `SOURCING_RULE`
permits sourcing *"from a maintainer's own reading"* and because the dev agent should not spend the
round rediscovering that these exist.

| Prior art | What it is | Why it is NOT the bench |
|---|---|---|
| **Zhu et al., *Understanding and Characterizing Mock Assertions in Unit Tests*** ([arXiv 2503.19284](https://arxiv.org/pdf/2503.19284)), dataset at [zenodo.14695509](https://doi.org/10.5281/zenodo.14695509) | A released dataset of method calls verified by developers with **mock assertions**, collected via an instrumented **Mockito** | **Java, and Mockito-specific.** Java is precisely the language `DF-14-3-A`/`-B` leave **unscored**, so admitting it is the failure AC3 exists to prevent. Also a *dataset of call sites*, not a set of pinned repositories — it cannot become `CorpusMemberSpec` rows, which are metadata plus a pin (DN-4). |
| **ATLAS** — ~9,000 projects, ~2.5M developer-written assertion statements | An assertion-generation training corpus | Java; and a corpus of **extracted methods**, not auditable repositories at pins. Vendoring any of it would breach NFR-S1. |
| **Defects4J** | The standard Java test-generation defect benchmark | Java; and its defects are **planted/curated program bugs**, i.e. a **recall** instrument — the role this project already assigns to `tests/cartridges/` under DN-2. It measures the wrong quantity. |

**What this prior art DOES contribute, and it is worth having:** it is external corroboration that
**"an assertion made against a mock rather than against the SUT result"** is a recognised, separately
studied phenomenon with its own literature — not a proxy this story invented to make its own bench
convenient. `DN-15-1-1` is therefore an instance of an established characterisation, narrowed to what
this repository's detector can score. ⚠️ It is **corroboration of the CONCEPT, never of any number
here**; every figure in §0 and §1 is this session's own execution.

*Rejected — "use an existing benchmark instead of selecting one":* all three are Java, all three
measure recall or supply extracted snippets rather than pinned repositories, and adopting one would
either widen the scope into an unscored language or replace the precision instrument with a recall
one. Recorded rather than left unasked, because *"why didn't you just use Defects4J"* is the first
question a reviewer will ask.

### Locked decisions this story CITES rather than reopens

| Decision | Where | What it forbids here |
|---|---|---|
| **DN-1** — the PRD governs; the gate is measured over the REPOSITORY corpus | `_manifest.py` | using cartridges to clear the gate |
| **DN-2** — cartridges are a different corpus (recall, not precision) | `_manifest.py`, `-24` | a cartridge id appearing in the manifest |
| **DN-3** — one floor constant, two populations | `_manifest.py`, `-25` | a second `N`, or restating `5` |
| **DN-4** — a member is metadata plus a pin | `_manifest.py` | vendoring source |
| **DN-5** — nothing in the module fetches | `_manifest.py`, `-28` | an automated fetch step |
| **DN-6** — AST-ineligible languages cannot count | `_manifest.py`, `-30` | admitting `c` / `cpp` / `ruby` / `rust` |
| **DN-14-2-1** — two assertion vocabularies; corroboration FROZEN at 23 names | `vacuous_test.py` | touching either table |
| **R2 is an operator act** | protocol §6 | ratifying inside this story |
| **The pre-registered stopping rule** | `DF-13-5-A` | a second round without a new operator decision |
| **`SOURCING_RULE`** | `_manifest.py` | recording *where* a candidate came from as evidence |
| **`NEVER_ELIGIBLE_FIELDS`** | `_manifest.py`, `-22` | stars / forks / downloads as a selection signal |

> **`SOURCING_RULE` already permits this story's premise** and should be cited rather than
> re-argued: *"A candidate repository may be sourced from anywhere — including from public users of
> the tool, from a maintainer's own reading, or from a public index."* **Sourcing is unrestricted;
> ADMISSION is what is restricted.** Public GitHub was always an allowed source. What is banned is
> using **adoption** as evidence (`prd.md:159`; and `NEVER_ELIGIBLE_FIELDS` makes adding a `stars`
> field a failure rather than a silent extension) — so *"popular repository"* is **not** a criterion.

### Open ledger entries bearing on this story — verified against `deferred-work.md` on disk, 2026-08-19

**All entries below are OPEN and are CITED. This story disposes of NONE of them.**

| Entry | State on disk | Bearing here |
|---|---|---|
| `DF-13-5-A` | OPEN, owner XAgent007, `target_story: NONE`; answered as a **rule**, branch not executed | §2 — the ONE round |
| `DF-13-5-B` | OPEN, owner XAgent007, `target_story: NONE` | §0.2 #2 — why `prd.md:190` is history, not current state |
| `DF-14-3-A` / `-B` | OPEN, **unassigned**, ⛔ **COUPLED** — neither may be scheduled without the other | AC3.1 — Go and Java excluded |
| `DF-14-3-C` | OPEN, unassigned; the entry itself states it **bounds Epic 15** | §0.2 #1, AC3.2, AC6.4 — the mechanism behind the TS measurement |
| `DF-14-3-F` | OPEN, owner XAgent007 | §0.3 — path correction, and its *"same extra nesting"* wording is itself wrong |
| `DF-13-3-A` | OPEN; premise **withdrawn 2026-08-17**, residual is the missing `evidence_deviation` header field | §0.2 #7 — criterion 7's real lesson |
| `DF-15-2-A` | OPEN; a vacuity sweep is in no definition of done; **4 of Epic 14's 35 guards** did not hold what their titles claimed | AC1.3, AC4.4 |
| `DF-15-2-B` | OPEN | not in scope — `secret_scan.py` is untouched |
| `DF-15-2-C` | OPEN | `AI-E14-2` is **NOT** discharged; do not cite *"22 of 24 REAL"* as established |
| `DF-15-2-D` | OPEN | §Module headroom below |

#### ⛔ Writing rule — `TC-ArgusAgent-DOCS-001-78`

That guard goes RED when a ledger id sits **on the same line** as a closure verb for an entry the
ledger never received, and **it has gone RED three times this week**. Its analyzer is line-scoped:
`_CLOSURE_VERB` matches `CLOSED | Closes | closes | Closed by this story` unless preceded by
`not` / `NOT` / `never`. **Rule for the dev agent: never put a `DF-` id on the same line as a closure
verb.** And **never append a closure to `deferred-work.md` to green a guard** — the remedy is to
correct the prose, always.

### Module headroom — MEASURED with the ceiling guard's own `_physical_line_count`, `_CEILING = 1200`

| Module | Lines | Headroom | Note |
|---|---|---|---|
| `argus/detectors/vacuous_test.py` | **1,196** | **4** | `DF-15-2-D`. ⛔ **Not on this story's write set — no split is triggered.** |
| `argus/pipeline.py` | 1,111 | 89 | must not be added to |
| `tests/test_vacuous_density.py` | 1,159 | **41** | the **tightest test module in the repository** today |
| `tests/test_vacuous_detector_index.py` | 1,065 | 135 | created by Story 15.2 |
| `tests/test_vacuous_detector.py` | 791 | 409 | split by 15.2, 1,161 to 791 |
| **`tests/corpus/_manifest.py`** | **546** | **654** | **this story's main write target — comfortable** |
| **`tests/test_validation_corpus.py`** | **859** | **341** | **this story's guard target — comfortable** |
| `argus/index/ast_index.py` | 635 | 565 | read-only here |

**`DF-15-2-D`'s trigger is NOT fired by this story.** Its condition is *"the next change of any size
to `argus/detectors/vacuous_test.py` performs the cohesion split FIRST."* This story does not touch
that module — `argus/` is byte-unchanged (AC7.2). If any dev pass finds itself needing to edit it,
**the split comes first**, by subject cohesion, never by arithmetic, with no function split across
the boundary, and with **no `_EXEMPT_BY_DESIGN` entry and no shave** (`MAINT-001-04`'s registry may
only shrink; `MAINT-001-03` pins **1,201** as the failure). At four lines that is a certainty rather
than a risk — so **plan not to open it.**

### Guard vacuity — this project's signature defect, and the specific obligation on this story

Epic 14 shipped **35** guards and **4** were not real (`-131` and `-132`, given floors in review;
`-107` **VACUOUS** — `lf.splitlines() == crlf.splitlines()` is `True`, so its headline assertion was
`f(x) == f(x)` on a pure function; `-118` **WEAK**). The 2026-08-19 sweep of the other 24 returned
**22 REAL / 1 VACUOUS / 1 WEAK**. ⛔ **That sweep's per-id table has no durable home in this
repository** (`DF-15-2-C`), so do **not** cite *"22 of 24 REAL"* as an established property of the
suite.

**Every guard this story adds asserts a NEGATIVE** — no output commit precedes, no detector import,
no malformed pin, no unscorable language. **Each must pin the precondition that makes the absence
meaningful, asserted FIRST**, and each must be **observed RED by an executed mutation** before it is
trusted (`DF-15-2-A` arm (a); `AI-E13F-1`). Model them on the guards this repository already trusts:
`-28`'s *"the ast walk found no imports at all — the closure is broken, not clean"*, `-24`'s >=8-word
reason floor, and `-78`'s *"the ledger extractor found ZERO closed entries"* floor. Also honour
`DF-15-2-A` arm (b): **a guard asserting `f(a) == f(b)` must first assert `a != b`.**

### Standing rules (non-negotiable)

- **AR8 / Pure-Impure separation** — any analyzer added here is pure: no I/O, no clock, no LLM, no
  network. The impure shell (git subprocess reads) stays at the edge, in the harness, never inside
  `_manifest.py` (`DN-5`, asserted by `-28`).
- **AR4** — exact `Fraction`, **never** `float`, in any recorded figure. Rates in this story's
  records are a `Fraction` or a plain integer pair, never a decimal.
- **Determinism (NFR-P1/D1)** — no wall-clock, no `uuid4`, no `random`, no dict/set-iteration-order
  reliance; **every set rendered `sorted()`**. Candidate rows are written in a stable, declared order.
- **AR7 / reuse-never-fork** — the language vocabulary is **imported** from
  `argus/shared/source_languages.py` (`_known_languages()`), never hand-listed; the floor is
  **resolved** through `validation_floor_n()`, never restated.
- **NFR-M1** — <= 1,200 lines per module, measured by `_physical_line_count`.
- **`pytest.skip` is a FALSE GREEN.** `audit-ci.yml` sets `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`
  precisely so a missing grammar cannot be answered with a skip. A **named `Unevaluable` failure** is
  the correct pattern (`tests/test_vacuous_density.py`).

### Files to touch — and the ones that must not move

**Write set:**
- `tests/corpus/_manifest.py` — **candidate rows only.** No schema change, no new field, no new
  function, no fetch.
- `tests/test_validation_corpus.py` — the AC1 / AC2.2 / AC4.3 guards, with newly allocated ids
  recorded.
- The AC2.2 selection harness — a small script under `scripts/`, on the
  `scripts/pinned_corpus_snapshot.py` precedent: pure functions plus a thin impure git edge, reading
  from the **object database at the pin**, never the working tree.
- **this story file** — criteria, per-candidate reasons, all exclusions, the AC1 sha, the CI run id.
- `sprint-status.yaml` — status transitions.

**Not touched:** `argus/**` (byte-unchanged, AC7.2) · `argus/detectors/vacuous_test.py` (four lines
of headroom) · `argus/pipeline.py` · `precision-validation-protocol.md` · the adjudication record and
`validation-corpus/*.json` · `prd.md` · `architecture.md` · `epics.md` (AC1.4) · `deferred-work.md`
(nothing is disposed of, and nothing is appended to green a guard).

**Also not yours, and uncommitted in the tree today:** `E-PRD/prd.md`, `epics.md`,
`stories/1-5-*.md`, `argusdemo/`, `.bmad-drift-audit/`, `bmad-dev-loop-pack/`,
`_bmad-output/audit-reports/*`. Leave all of them alone.

### Previous-story intelligence — Story 15.2 (`done`, 2026-08-19)

- **It fixed a line-numbering CONTRACT defect**: the detector scored over `source.splitlines()`
  (which splits on eleven things) while the Story 1.4 index numbers lines by **newline alone**. Eight
  characters survive the production read path at `argus/pipeline_stages.py:124` and desynchronise the
  two views, silently dropping assertions and producing **false flags**. **Consequence for this
  story: every flag rate and `assertion_sites` figure that predates `3acb028` is void.** §0.2 #3 and
  §1's figures are re-derived at or after it.
- **Its pattern to copy:** the fix landed as a **contract** (`index_aligned_lines`, newline-based *by
  construction*), not as a special case for any one character. Prefer a stated contract over an
  enumeration of cases.
- **Its precondition to copy:** the **cohesion split came FIRST**, before any case was added, with no
  exemption and no shave.
- **Its review found the real lesson:** *"a disposition recorded in prose and not in the ledger is
  not a disposition."* Story 15.2's own completion notes wrote *"recommend a ledger entry"* and filed
  none, which is why `DF-15-2-D` exists.

### Git intelligence

`f2189c1` `docs(15-2): code review iteration 2 — VERDICT pass, story -> done` · `79a78cf` review
iteration 1 · `bc4bce9` dogfood regeneration · `be3ff0a` `DN-15-2-2` moved into the code it governs
and `DF-15-2-D` filed · `c66a065` CI matrix result recorded so its AC was discharged **by
observation**.

Three habits worth copying exactly: **(i)** code delta, dogfood-artifact regeneration and story
record land in **separate commits** — which is precisely what AC1 needs, since the criteria commit
must contain no Argus output; **(ii)** a CI result is recorded as a **run id plus the sha it
covers**, discharging its AC by observation rather than by assertion; **(iii)**
`git status --porcelain argus tests` is checked **empty before and after** any out-of-tree
measurement.

### References

- [epics.md](../epics.md) §Epic 15 (`:2827`), §Story 15.1 (`:2852`) — **working copy only; see §0.2 #4**
- [deferred-work.md](../deferred-work.md) — `DF-13-5-A` (`:4692`), `DF-13-5-B` (`:5079`),
  `DF-14-3-A` / `-B` / `-C` (`:4740`+), `DF-14-3-F` (`:4969`), `DF-13-3-A` (`:4394`),
  `DF-15-2-A` (`:5098`), `DF-15-2-B` (`:5132`), `DF-15-2-C` (`:5160`), `DF-15-2-D` (`:5188`)
- [precision-validation-protocol.md](../precision-validation-protocol.md) §6 R1–R4, §4, §5, §7
- [architecture.md](../architecture.md) §Enforcement — *Vacuity-corroboration*, *Adjudication-record*,
  *Corpus-pin provenance*, *Ledger-claim cross-check*, *GUARD-ADEQUACY CLAUSE*
- [epic-13-retro-2026-08-19.md](../epic-13-retro-2026-08-19.md) §5.3, §9 SD-1, §14.1–§14.4
- [epic-14-retro-2026-08-18.md](../epic-14-retro-2026-08-18.md) §3.1, §3.5, §3.6, §3.7
- [13-5-re-measure-the-gate-against-the-corrected-instrument.md](13-5-re-measure-the-gate-against-the-corrected-instrument.md)
- [15-2-the-detector-and-the-index-agree-on-what-a-line-is.md](15-2-the-detector-and-the-index-agree-on-what-a-line-is.md)
- `tests/corpus/_manifest.py` · `tests/test_validation_corpus.py` ·
  `argus/detectors/vacuous_test.py` (contract docstring) · `scripts/pinned_corpus_snapshot.py`

---

## Tasks & Subtasks

- [ ] **Read §0 first.** The premises are re-derived; do not re-derive them again, but do **not**
      inherit any figure §0 marks CORRECTED or VOID. (AC: all)
- [ ] Resolve `DN-15-1-1` / `-2` / `-3` into declared **code constants** beside the harness (AC2.1,
      AC2.2)
- [ ] Build the selection harness: pure analyzers plus a thin git edge, reading from the **pinned
      object database**; `argus.index.*` permitted, `argus.detectors.*` **banned** (AC2.2)
- [ ] Write the AC2.2 import-ban guard **with `-28`'s non-vacuity floor**, and observe it RED by
      adding a detector import, then remove it (AC2.2, AC4.4)
- [ ] **Freeze the criteria plus the full candidate list in their OWN commit**, containing no Argus
      output over any candidate; record its 40-hex sha here (AC1.1)
- [ ] Write the AC1 ordering guard: sha resolves, ancestor of HEAD, no output path touched; **pin all
      three non-vacuity preconditions and drive the ancestry predicate to BOTH outcomes** (AC1.2,
      AC1.3)
- [ ] Record the `epics.md`-uncommitted precondition on the AC1 commit; **do not edit `epics.md`**
      (AC1.4)
- [ ] Assemble **12–20** candidates against the frozen criteria; resolve **each** path individually by
      `cat-file -t <pin>` and beware the §0.3 decoys (AC6.1, criterion 7)
- [ ] For every TypeScript candidate, measure and record its **scorable test function count** through
      the index; apply the AC3.2 floor; if none clears it, record that as a **measurement** (AC3.2,
      AC3.3)
- [ ] Record per-candidate reasons **and every rejection with the criterion that rejected it** (AC6.2,
      AC6.3)
- [ ] Add candidate rows: `eligible_for_n=False` plus the R2 reason; **no field added** (AC4.1, AC4.2)
- [ ] Add the AC4.3 guards for pin shape, language scope and licence, **each with a non-empty
      candidate-population floor asserted first and each observed RED by an executed mutation**
      (AC4.3, AC4.4)
- [ ] Verify `eligible_member_count() == 5` and `-31` green — **`N` is unchanged** (AC4.5)
- [ ] Verify `git diff --stat argus/` is **empty** (AC7.2)
- [ ] Full suite green at **1,645+**, exit 0, **0 skipped**, with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`
      (AC7.3)
- [ ] Commit, push, and **record the CI run id together with the sha it covers** (AC7.4)
- [ ] Hand the operator **one reviewable list** for the R2 ratification act (AC7.5)

---

## Dev Agent Record

### Agent Model Used

claude-opus-5[1m] (BMAD dev-story worker)

### D0 - WHAT THIS PASS DELIVERED, AND THE ONE THING IT COULD NOT

**SELECTION IS BLOCKED ON AN OPERATOR ACT, AND THE BLOCK IS MEASURED RATHER THAN ASSERTED.**

AC6.1 asks for **12-20 candidates**. Criterion 7 requires each candidate's pin to resolve at a
path on this machine (`git -C <windows-path> cat-file -t <sha>` returning `commit`), and criteria
2, 3 and 5 are all reads **of the pinned tree**. So a repository that is not already on this
machine cannot be measured. AC5 says, and this pass honoured, that **nothing in this story
fetches**.

The whole locally-resolvable universe was swept (D3). **Eleven repositories, and ZERO of them
qualify.** Every one fails criterion 2. The highest co-occurrence count anywhere on this machine
is **3**, and that is the Argus repository itself, which is permanently ineligible. Exactly
**two** genuinely third-party repositories exist locally, and both fail:

| Third-party repository | Test files | Co-occurrence | Rejected by |
|---|---|---|---|
| `microsoft/qlib` @ `79633dd9` | 36 | **0** | criteria 2, 3 |
| `Microsoft/Windows-universal-samples` @ `0db108e9` | 0 (Python) | **0** | criteria 2, 3 |

Assembling the bench therefore requires **fetching third-party source**, and protocol section 6
R2 names that act verbatim:

> *"Choosing which repositories are legitimate members, and fetching third-party source, are not
> autonomous acts."*

That is the operator act this pass **HALTS on rather than performs**, which is the same reason
`tests/corpus/_manifest.py` is byte-unchanged: with no candidate clearing the criteria, writing a
candidate row would be fabricating a bench, and this is the story whose entire purpose is that
the bench be chosen honestly.

**What DID land, and it is the half that had to come first:** the criteria are now **frozen in
git as executable code** with the candidate sweep recorded against them, and the ban on reading
the detector's output is **structural**. Per AC1 that ordering is the point - the criteria commit
precedes any Argus output over any candidate, and now provably so.

### D1 - AC1: the criteria-freezing commit

| | |
|---|---|
| **Criteria commit sha** | `CRITERIA_SHA_PLACEHOLDER` |
| **Guard id** | `TC-ArgusAgent-PRECISION-001-75` |
| **Ancestor of HEAD** | yes - asserted mechanically, and the predicate is driven to **both** outcomes |
| **Argus output over a candidate in it?** | none - asserted over real git history, not by inspection |

**AC1.4 - the `epics.md` precondition, RE-MEASURED and RESOLVED.** Section 0.2 #4 recorded that at
`f2189c1` `epics.md` ended at Epic 13, so Epic 14 and Epic 15 existed only in an uncommitted
working copy. **That is no longer true.** Commit `762a73e` (*"docs(epics): the plan of record
catches up with epics 14 and 15"*, the current HEAD and this story's `baseline_commit`) committed
it: `git show HEAD:.../epics.md` now carries `## Epic 14` at line 2668, `## Epic 15` at 2827 and
`### Story 15.1` at 2852. **A reader of git history can now see that this epic exists**, and the
AC1 commit is no longer the only place it does. `epics.md` was **not edited by this pass**, as
AC1.4 requires - it was already committed by the operator.

### D2 - the frozen criteria, resolved into code (AC2.1, AC2.2)

`DN-15-1-1`, `-2` and `-3` are resolved as **named module-level constants** in
`scripts/candidate_selection.py`, never retyped into prose (`AI-E9-7`):

| Criterion | Constant / function | Value |
|---|---|---|
| 1 - language scope | `IN_SCOPE_LANGUAGES` | `python`, `typescript` |
| 2 - suite floor | `TEST_FILE_FLOOR` | 50 |
| 2 - the REAL floor | `COOCCURRENCE_FILE_FLOOR` | 10 |
| 3 - co-occurrence | `MOCK_BINDING_PATTERN` + `MOCK_ASSERTION_PATTERN` (+ `_LOOSE`) | see module |
| 4 - history | `HISTORY_SPAN_DAYS_FLOOR` | 730 |
| 5 - licence | `_LICENCE_NAMES`, read from the tracked blob at the pin | verbatim first line |
| 6 - provenance | not machine-decidable - recorded as `CriterionOutcome(6, False, ...)` | operator act |
| 7 - pin | `pin_is_reachable` via `cat-file -t` | reused, never forked (AR7) |
| AC3.2 - TS floor | `TYPESCRIPT_SCORABLE_FLOOR` | 25 |

**Criterion 4 is measured first-commit-to-pin, NOT first-commit-to-now.** NFR-P1/D1 forbid a
wall-clock read, and a criterion whose value changes every day it is re-run is not a *frozen*
criterion. This is a decision this pass took; it is recorded rather than assumed.

**AC2.4 - why criterion 3 is legitimate and criterion-shopping is not.** Carried in the module
docstring in section 1.3's exact form: a criterion may reference the defect's **definition**; it
may never reference the tool's **verdict**. AC2.2 makes the difference mechanical rather than
promised - `argus.index.*` (reach) is permitted, `argus.detectors.*` (output) is banned by an
`ast` walk.

**A visible cost of the ban, recorded rather than hidden.** `is_scorable_test_definition`
**restates** the detector's test-function rule instead of importing `_is_test_function`, because
that function lives in `argus/detectors/vacuous_test.py` - the banned module. This is a
deliberate duplication: the rule is a three-line predicate quoted from the detector's own
contract, and the import ban is worth more than the de-duplication. Recorded because AR7 says
reuse-never-fork, and this is the one place this pass did not.

**AC2.3 holds unchanged and no field was added.** `MANIFEST_FIELDS` is untouched at 9.

### D3 - THE SWEEP: every repository considered, with the criterion that rejected it (AC6.2, AC6.3)

**How the universe was established, because a scan at the wrong depth is indistinguishable from
an absence** (`DF-13-3-A`'s real lesson, section 0.2 #7). `find` for `.git` to **depth 9** under
`D:/ProjectX` (16 hits, 6 of them `XAgents-WebApp` agent worktrees), plus depth-5 scans of
`D:/AI Study`, `D:/t`, `D:/tmp`, `D:/_gs`, `C:/Users/varin/source`, `C:/Users/varin/Documents`.
`agent-smith` at depth 5 was found, which is the specific miss that filed a ledger entry last
time. Every pin was resolved **individually** by `cat-file -t`, never by name and never by remote.

All figures below are read from the **pinned object database** (`ls-tree` + `cat-file`), never the
working tree. Both corpus checkouts and every tree inspected were treated as **strictly
read-only**: no checkout, stash, clean, reset, commit or worktree. `git status --porcelain` over
`argus/` and `tests/` was empty before and after the sweep.

| # | Repository | Class | Pin | Test files | bind | assert | **co-occur** | loose | days | licence | **REJECTED BY** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `microsoft/qlib` | **third-party** | `79633dd9` | 36 | 0 | 0 | **0** | 0 | 2168 | MIT | **2** (36 < 50; 0 < 10), **3** |
| 2 | `Microsoft/Windows-universal-samples` | **third-party** | `0db108e9` | 0 | 0 | 0 | **0** | 0 | 3213 | present | **2**, **3** (C++/C#/XAML) |
| 3 | `minions` | same-org, ratified | `c2940d2f` | 237 | 19 | 3 | **1** | 6 | 135 | none | **6** (Argus was developed against it), 2, 4, 5 |
| 4 | `agent-markovich` | same-org, ratified | `a5616686` | 26 | 0 | 0 | **0** | 0 | 5 | none | **6**, 2, 3, 4, 5 |
| 5 | `ai-body-runtime` | same-org, ratified | `4480ffde` | 3 | 0 | 0 | **0** | 0 | 0 | none | **6**, 2, 3, 4, 5 |
| 6 | `xagents-webapp` | same-org, ratified | `33a86525` | 265 | 12 | 0 | **0** | 0 | 91 | none | **6**, 1 (AC3.2), 2, 3, 4, 5 |
| 7 | `agent-smith` | same-org, ratified | `9ab774d7` | 86 | 0 | 0 | **0** | 0 | 63 | none | **6**, 1 (AC3.2), 2, 3, 4, 5 |
| 8 | `ArgusAgent` (self) | **self** | `762a73ec` | 115 | 7 | 3 | **3** | 3 | 20 | present | **6** - a tool cannot clear an externalization gate by auditing itself |
| 9 | `Minions - Copy` | **DECOY** | `1468536f` | 33 | 4 | 0 | **0** | 0 | 20 | none | **6**, and the ratified pin is NOT reachable in it |
| 10 | `XAgents-WebApp - Temp (...)` | **DECOY** | `54e09cc5` | 32 | 1 | 0 | **0** | 0 | 20 | none | **6**, and the ratified pin is NOT reachable in it |
| 11 | `AgentMarkovich-old` | **DECOY** | `465b305e` | 47 | 0 | 0 | **0** | 0 | 0 | none | **6**, no origin, ratified pin NOT reachable |

**Every rejection above names the criterion that rejected it** - AC6.3, and *an exclusion without
a reason is an oversight wearing a decision's clothes*.

**The measured headline: not one repository on this machine reaches `COOCCURRENCE_FILE_FLOOR`.**
The best third-party candidate scores **0 of 10**. The best score of any kind is **3**, by the
self-audit row that can never be eligible.

**Section 1.1 REPRODUCED EXACTLY - the sweep's non-vacuity proof.** The harness, run over
`minions` at the ratified pin `ec63b729`, returns **286 test files, 21 binding, 3 assertion, 1
strict co-occurrence, 6 loose** - every figure matching section 1.1's independent measurement,
which was taken by a different method with the detector not imported. *A measurement over an
empty, unreachable or decoy corpus reports 0 and looks identical to a real 0*, so this
reproduction is what establishes that the zeroes above are **real zeroes** and not an empty read.
(Row 3 reads `c2940d2f`, the checkout's drifted current HEAD, and 237 files; the ratified pin
reads 286. Both are recorded - the drift is `minions`' own, it is a live third-party tree, and
nothing here touched it.)

### D4 - AC3.2 / AC3.3: the TypeScript outcome, recorded as a MEASUREMENT

**No TypeScript candidate clears the AC3.2 visibility floor, because no TypeScript candidate
exists to test.** Neither third-party repository is TypeScript. The two ratified TypeScript
members are not candidates (criterion 6) and, per section 0.2 #1, would fail the floor anyway:
367 TS test files between them yield **one** scorable test function.

Per AC3.3 this is recorded as a **measurement and as a finding - never as a scope change taken by
this story**. TypeScript **stays in scope**, behind the floor, exactly as `DN-15-1-3` decided.
**Collapsing the bench to Python-only is the operator's call at R2**, where the protocol already
puts it, and this pass does not pre-empt it and did not widen the scope to compensate.

**AC3.4** - the concentration point is preserved and re-sourced to **Story 13.5's pin-verified
measurement** (1,960 files, 0 blocking findings, five-of-five pin-verified). `prd.md:190`'s *"31
findings from 2 of 5 members"* is cited as **history only**, under `DF-13-5-B`, and never as
current corpus state.

### D5 - the guards added, each RED-observed by an EXECUTED mutation

Ids allocated as the next **actually-free** ids in the `PRECISION-001` range. **Section 0.2 #5's
range is itself short:** `-21..-31` is the range *within `tests/test_validation_corpus.py`*, but
the `PRECISION-001` area runs to **`-73`** across `test_gate_flip_path.py` (`-32..-38`),
`test_adjudication_record.py` (`-39..-52`, `-71`), `test_gate_decision.py` (`-53..-70`) and
`test_pinned_corpus_snapshot.py` (`-65..-68`, `-72`, `-73`). The next free id is **`-74`**. No
existing id was renumbered - an id in this repository is a citation.

| Guard | Asserts | Its non-vacuity precondition, asserted FIRST | Driven to both outcomes? |
|---|---|---|---|
| `-74` | AC2.2 - the harness never imports `argus.detectors.*` | the walk found imports **at all**, **and** it can SEE `argus.index` - proving dotted-name extraction works, so the absence of `argus.detectors` is meaningful rather than a parsing artifact | **YES** - the same pure analyzer is re-run over source with a detector import injected, and must catch it |
| `-75` | AC1 - the criteria sha resolves, is an ancestor of HEAD, and no commit reachable from it touches a candidate-output path | the output-path set is **non-empty**; `git log` over a **control path known to carry commits** returns **non-empty**, proving the invocation can find something | **YES** - ancestry is asserted True for criteria-to-HEAD and False for HEAD-to-criteria |
| `-76` | AC4.3 - a candidate row's pin shape, language scope and licence | the checker is proved able to REPORT defects before it is trusted to report none | **YES** - five executed mutations |

**`-76` also pins the measured premise that makes it necessary:** it asserts that
`CorpusMemberSpec(eligible_for_n=False, commit_sha='deadbeef', ...)` **constructs silently**. If
`__post_init__` ever stops returning early, `-76` says so instead of quietly becoming redundant.

**`-76` carries a deliberate TRIPWIRE, and it is the honest answer to AC4.4.** AC4.4 requires the
candidate population be asserted **non-empty first**. There are **zero** candidate rows, so that
assertion cannot be made truthfully today. Rather than fold over an empty tuple and pass forever
- *this project's signature defect*, and the reason 4 of Epic 14's 35 guards were not real -
`-76` asserts the population is **exactly empty** and names why. **It goes RED the moment the
first candidate row lands**, forcing whoever adds it to complete the AC4.4 population arm. That
is the `-25`/`-27` precedent: a guard written to fail loudly on a corpus change rather than
absorb one silently.

**AC4.5 - `N` is unchanged at 5.** `eligible_member_count() == 5`, `-31` and `-25` green,
`tests/corpus/_manifest.py` **byte-unchanged**. `MANIFEST_FIELDS` stays closed at 9 fields and
`-22` is green without amendment.

### D6 - a deviation from the story's write set, with its rationale

The story's write set puts the new guards in `tests/test_validation_corpus.py` (859 lines, 341
headroom). They went into a **new `tests/test_candidate_selection.py`** instead. Two reasons, and
the second is the governing one:

1. **Cohesion.** These guards are about `scripts/candidate_selection.py`, not about the manifest.
   The repository already pairs `scripts/pinned_corpus_snapshot.py` with
   `tests/test_pinned_corpus_snapshot.py`; this follows that precedent exactly.
2. **NFR-M1 headroom.** The three guards are ~300 lines. In `test_validation_corpus.py` that
   lands near 1,160 of the 1,200 ceiling, making it the tightest test module in the repository
   and pushing the *next* change into a split. **Cohesion split over a shave**, which is the rule
   Story 15.2 established and `MAINT-001-04` enforces. No `_EXEMPT_BY_DESIGN` entry was added.

`tests/test_validation_corpus.py` is therefore **unchanged**, and so is every guard in it.

### D7 - Debug Log

- Suite baseline confirmed at HEAD `762a73e` before any edit: **1,645 passed, 0 failed, 0
  skipped**, exit 0, with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`.
- Harness validated by **reproducing section 1.1's independent figures exactly** over
  `minions@ec63b729`.
- `-74`, `-75`, `-76` each observed RED before green, by executed mutation - see D5.
- `git status --porcelain argus tests` checked empty before and after every out-of-tree read.
- `git diff --stat argus/` **empty** (AC7.2) - `argus/` is byte-unchanged, so no `argus/` LOC
  changed and the dogfood artifacts are **not** regenerated. Confirmed rather than assumed: the
  currency guards track `argus/` LOC, and this delta contains none.

### D8 - THE HALT, with options, for the operator

**Selection cannot be completed autonomously.** It needs one operator act, and protocol section 6
R2 already assigns it. Stated with options rather than performed:

- **Option A - authorise the fetch (the protocol's own path).** Name 12-20 third-party
  repositories, or authorise cloning against the frozen criteria. The criteria are now executable:
  `python scripts/candidate_selection.py <checkout> <sha> <id> <language> [url]` prints all seven
  verdicts with measured values. This is R2's *"fetching third-party source"* half, and it is
  explicitly **not autonomous**.
- **Option B - relax criterion 2 for this round.** `COOCCURRENCE_FILE_FLOOR = 10` is the binding
  constraint; `microsoft/qlib` fails it **0 to 10**, so relaxing it does not rescue the one
  third-party repository available. Recorded for completeness and **not recommended**: tuning a
  frozen criterion after seeing what it rejects is the failure section 1.3 exists to prevent.
- **Option C - take the `DF-13-5-A` branch instead.** The pre-registered rule already covers a
  round that cannot produce adjudicable findings. **That branch is NOT this story's to take**, it
  is not executed here, and nothing in this pass disposes of that entry - it stays open and
  un-dispositioned, cited only.

**What is NOT blocked and is ready now:** the criteria are frozen in git, the ordering claim is
mechanically checkable, and the ban on reading the detector's output is structural. When the
operator authorises Option A, the measuring half runs against criteria that were **provably
written first** - which is the entire property this story exists to establish.

### File List

- `scripts/candidate_selection.py` - **new.** The selection harness: `DN-15-1-1`/`-2`/`-3` as
  named constants, pure analyzers, a thin read-only git edge over the pinned object database.
- `tests/test_candidate_selection.py` - **new.** `TC-ArgusAgent-PRECISION-001-74`, `-75`, `-76`.
- `_bmad-output/design-artifacts/ArgusAgent/stories/15-1-a-bench-with-the-defect-class-in-it-chosen-before-anyone-looks.md`
  - this record.
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` - status transitions.

**Byte-unchanged, and asserted rather than claimed:** `argus/**`, `tests/corpus/_manifest.py`,
`tests/test_validation_corpus.py`, `epics.md`, `prd.md`, `architecture.md`, `deferred-work.md`,
`precision-validation-protocol.md`, `validation-corpus/*.json`.

### CI evidence (AC7.4)

| | |
|---|---|
| **Run id** | `CI_RUN_PLACEHOLDER` |
| **Sha covered** | `CI_SHA_PLACEHOLDER` |
| **Legs** | ubuntu-latest x 3.10 / 3.11 / 3.12 |

### Completion Notes

**Status: `review`, with an explicit HALT recorded in D8.** Delivered: the criteria frozen in git
as executable code (AC1.1, AC2.1), the structural import ban (AC2.2), the mechanical ordering
guard (AC1.2, AC1.3), the AC4.3 candidate-row checker with a tripwire in place of a vacuous fold,
the complete 11-repository sweep with every rejection reasoned (AC6.2, AC6.3), and the TypeScript
outcome recorded as a measurement (AC3.3).

**Not delivered, because it requires an operator act:** the 12-20 candidate list (AC6.1) and the
candidate rows (AC4.1, AC4.2). Zero of the eleven locally-resolvable repositories clear the
criteria, and fetching more is protocol section 6 R2's *"not autonomous"* half.

**Nothing was ratified, no Argus detector was run over any candidate, nothing was adjudicated,
and no threshold, corpus floor, FR34 or `protocol_cleared` value moved.** `DF-13-5-A`'s ONE
permitted round is not consumed by this pass: no bench was expanded, because none could be
selected. Every ledger entry this story cites remains open and un-dispositioned.

### Review Findings


## Change Log

| Date | Change | By |
|---|---|---|
| 2026-08-17 | Created as `backlog` under Epic 15, by operator decision. §0 written as a premise list explicitly requiring re-derivation at create-story time. | XAgent007 |
| 2026-08-19 | **Contexted by create-story on HEAD `f2189c1`.** Every §0 premise re-derived by execution. **Six premises survived exactly** (manifest shape, closed schema, construction-time refusal, resolved floor, the stopping rule, the sourcing rule). **Eight did not, and are corrected with the original named as wrong:** the TypeScript scoping premise (measured — 367 TS test files across the two ratified TS members yield **1** scorable test function); `prd.md:190` cited as current state (superseded); *"expected zero"* as a forecast (now a measurement); AC1's uncommitted-tree blocker (resolved for the code tree, with the `epics.md` residue named); the `-21..-30` guard range (runs to `-31` plus three DOGFOOD ids); *"the guard is structural"* (`__post_init__` returns early, so pin, language and provenance are unchecked on a candidate row); the `DF-13-3-A` lesson (the pin was never unreachable); and premise 5 (`epic-14` is `done`, so the parallelism dispensation is moot). **New measurement added:** across 315 Python test files at three pins, between **1 and 6** carry a mock-binding / mock-assertion co-occurrence — establishing *why* the corpus returned zero, without running the detector. Status `backlog` to `ready-for-dev`. | Scrum Master (create-story) |
