# Sprint Change Proposal — 2026-08-17b

**Project:** ArgusAgent (formerly APAA — AI Project Assurance Audit)
**Author:** Correct Course workflow (`bmad-correct-course`), batch mode
**Requested by:** XAgent007
**Trigger type:** Newly discovered defect in scope already open — found while scoping a multi-language validation bench, in the epic that is currently open to fix the same failure class
**Change scope classification:** **MINOR-to-MODERATE** — one story added to an open epic; no epic created, no threshold moved, no corpus changed
**Status:** ✅ **APPROVED by XAgent007, 2026-08-17 — all §4 edits APPLIED.**

> **Nothing in `argus/` was modified to produce this document.** Every number in §1.3 was produced
> by an out-of-tree probe that imports the **shipped** `argus.index.ast_index.build_ast_index` and
> `argus.detectors.vacuous_test.VacuousTestDetector._score` read-only, over six synthetic fixture
> files. `git status` for `argus/` is unchanged from the start of the session.

---

## 1. Issue Summary

### 1.1 What triggered this

The operator proposed expanding the precision-validation bench with **public GitHub repositories
across several languages** — the route to a non-empty precision denominator recorded as option (a)
of the §2.5 decision in `sprint-change-proposal-2026-08-17.md`.

Before that bench could be scoped, one premise had to be checked rather than assumed: **does the
vacuous-test detector actually work on non-Python code?** It was probed by execution. It does not,
and one of the four ways it fails is a **false accusation** — the precise failure class Epic 14 was
opened to close.

### 1.2 Problem statement

`argus/index/` is genuinely multi-language: ten tree-sitter grammars ship in the **default** install
(`pyproject.toml:47-69`, Story 12.5), and `argus/detectors/vacuous_test.py:201-216` already carries
the test-file naming conventions of Go, JavaScript, TypeScript, Rust, Ruby, C++ and Java.

**The scorer behind that surface is Python-shaped in four independent places.** The result is not a
graceful degradation. On one measured path Argus **flags a JavaScript test that contains a real,
passing assertion as vacuous**, because it cannot see the assertion.

### 1.3 Evidence — measured, not inferred

Six fixture files, one per idiom, through the shipped index and the shipped scorer:

| Fixture | test file? | definitions | `_is_test_function`? | assertion visible? | scored | outcome |
|---|---|---|---|---|---|---|
| `test_control.py` — `unittest` + `MagicMock` | ✅ | class + function | ✅ | ✅ `assertEqual` | ✅ | `assertions=2 density=1/2` **not flagged — correct** |
| `plainfn.test.js` — `expect(r).toBe(5)` | ✅ | function | ✅ | ❌ | ✅ | `assertions=0 density=0` **FLAGGED — false** |
| `calc.test.js` — `describe`/`it` arrow blocks | ✅ | **none** | — | — | ❌ | silent |
| `parser_test.go` — `t.Fatalf` / `t.Errorf` | ✅ | function | ❌ | ❌ | ❌ | silent |
| `testify_test.go` — `assert.Equal` / `require.NoError` | ✅ | function | ❌ | ❌ | ❌ | silent |
| `CalcTest.java` — JUnit `@Test`, `assertEquals` | ✅ | class + function | ❌ | ✅ `assertEquals` | ❌ | silent |

Four **independent** defects, each isolated to its own mechanism:

**D1 — the assertion vocabulary is unittest-only.** `_ASSERTION_CALLEES` (`vacuous_test.py:117`)
holds **23 names, every one of them `unittest`**. `expect`, `toBe` and `assertEquals` all appear in
the edge set — the index *sees* them — and none is in the table. Measured consequence: a JS/TS test
whose assertion is real scores `assertion_sites=0`, `assertion_density=0`, falls below
`ASSERTION_DENSITY_FLOOR = 1/4`, and is **flagged heuristically vacuous**. **This is a false
accusation.**

**D2 — the test-function predicate is Python-shaped.** `_is_test_function` (`vacuous_test.py:409`)
is `definition.name.startswith("test")` — case-**sensitive**. Go's `TestParseReturnsTokens` misses
on the capital `T`; JUnit marks tests by the `@Test` **annotation** and its method names carry no
prefix at all. Measured consequence: **no Go or Java test is ever scored.**

**D3 — Go selector calls never reach the edge set.** In `parser_test.go`, `NewParser` and `len`
appear as edges while `t.Fatalf` and `t.Errorf` **do not**; in `testify_test.go`, `Compute` appears
while `assert.Equal` and `require.NoError` do not. Python's `self.assertEqual` **is** captured, so
this is Go-specific extraction, not a general receiver-call limit. Measured consequence: **even with
D1 and D2 fixed, every Go test would still score `assertion_sites=0`.**

**D4 — callback test blocks yield no definitions.** `describe('add', () => { it('sums', () => …) })`
extracts **zero** definitions; the same file rewritten as a plain `function testAddsNumbers()`
extracts correctly. Measured consequence: **idiomatic Jest / Mocha / Vitest suites are invisible** —
which is nearly all of them.

### 1.4 Why one of these belongs to Epic 14 and three do not

Epic 14's charter is *"the blocking rule proves what it claims"* — the false-accusation moat. The
four defects split cleanly on **failure direction**:

- **D1 makes Argus say something false about code that is fine.** It is the same failure as the one
  that produced 0 TP / 26 FP, arriving by a different route. It is Epic 14's business by definition.
- **D2, D3 and D4 make Argus say nothing at all.** That is a coverage gap. It is a real defect and
  it is why a multi-language bench cannot be assembled yet, but silence is not a false accusation
  and does not belong in the epic chartered to stop them.

---

## 2. Impact Analysis

### 2.1 Epic impact

**Epic 14** — one story added (14.3). Charter **unchanged**: D1 is a false accusation and the
existing epic statement already covers it without amendment.
**Epic 13** — unchanged. **Epic 15** — **not created.** The bench work stays unfiled pending the
§2.5 decision it depends on (`DF-13-5-A`).

### 2.2 Story impact

| Story | Impact |
|---|---|
| **14.1** | **None.** Fact (b) is about mock-derivation, not assertion naming. `_ASSERTION_CALLEES` is not on its Files-to-touch list. |
| **14.2** | ⚠️ **Direct collision — sequencing required.** 14.2 owns `_ASSERTION_CALLEES` and adds the missing **pytest** helpers to it. 14.3 adds the **non-Python** entries to the same frozenset. **14.3 runs after 14.2 and must not re-open 14.2's Python entries** — the same discipline DN-4 already imposes between 14.1 and 14.2. |
| **13.5** | ⚠️ **Numbers move — see §2.3.** |

### 2.3 The corpus impact, derived and NOT yet measured

**Two of the five ratified members are TypeScript** — `xagents-webapp` and `agent-smith`
(`tests/corpus/_manifest.py`). D1's mechanism therefore applies to real corpus members, not only to
fixtures.

**Stated as a derivation, because it has not been measured:** the mechanism in §1.3 predicts that
TypeScript tests in those two members are being scored `assertion_sites=0` and flagged
heuristically vacuous today. That prediction is **not** established here — the members are not
staged in this session, and staging them is an operator act. **Verifying it is a task of Story 14.3,
before the fix, so the delta is measured rather than claimed.**

Two things this does **not** disturb:

- **The 31 blocking findings are unaffected.** Blocking requires `ast_corroborated`, which requires
  `mock_sites >= 1`, and `_MOCK_CALLEES` is likewise Python-only — so a TS test cannot currently
  reach verdict-eligibility by any path. The `agent-smith` findings were emitted on that member's
  **Python** files (`test_trace_emitter.py`, named in the 2026-08-17 proposal §2.6), despite its
  `primary_language: typescript`.
- **The advisory counts DO move**, which is why 13.5 must run after this story rather than beside it.

### 2.4 Technical impact

The fix direction is **strictly flag-reducing**. `assertion_sites` appears only as the numerator of
`assertion_density`, and a flag fires when density is **below** the floor. Adding names can only
raise the numerator, so it can only **remove** flags, never add one. **No test that passes today can
start failing because of this change** — which is the conservative direction the module docstring's
*"the conservative default is the moat"* requires.

**Architectural note — NFR-P2 is respected, on existing precedent.** NFR-P2 confines the *language
conditional* to `argus/index/`. `_ASSERTION_CALLEES` stays a **flat, language-agnostic** set of
names, exactly as `_UNAMBIGUOUS_TEST_SUFFIXES` and `_CASE_SENSITIVE_TEST_SUFFIXES` already do in the
same module, under the justification recorded at `vacuous_test.py:212-215`: *a naming convention is
not a grammar/parse conditional.* **14.3 must not add a language field to the detector.**

**The accepted cost of a flat set:** a Python function named `expect` would now count as an
assertion. The error direction is one fewer flag, which is safe, and the alternative — a per-language
table — is the NFR-P2 breach. Recorded as a decision with its rejected alternative, not discovered
later.

---

## 3. Recommended Approach

### 3.1 Options evaluated

| # | Option | Verdict |
|---|---|---|
| 1 | **Fix D1 only, in Epic 14; file D2/D3/D4 as measured deferred work** | ✅ **Selected.** Closes the false accusation inside the epic chartered for it; leaves the three coverage gaps to the multi-language roadmap where they belong. |
| 2 | Fix all four in Epic 14 | ❌ Epic 14 becomes a multi-language capability epic. D3 and D4 are extractor work in `argus/index/`, are not false accusations, and would delay 13.5 behind work the gate does not need. |
| 3 | Do nothing until the bench is scoped | ❌ Leaves a measured false accusation shipping in the beta, in the exact class Epic 14 is open to close. A known false 🔴-adjacent flag is not deferrable on grounds of tidiness. |
| 4 | Suppress the vacuous detector on non-Python files entirely | ❌ Considered seriously — it also removes the false flag. Rejected: it removes the capability rather than repairing it, forecloses the multi-language bench, and D4 already delivers most of that silence by accident. Silence is what D2–D4 are; adding more is not a fix. |

### 3.2 Selected: Option 1

```
Epic 14 (build)                              Epic 13 (measure, re-opened)
  14.1  corroboration -> CC#6 conformance  ─┐
  14.2  density scorer + assertion names   ─┤
  14.3  the vocabulary crosses languages   ─┴─>  13.5  re-audit, re-adjudicate, re-decide
        (strictly after 14.2)
```

### 3.3 Effort, risk, timeline

| | Assessment |
|---|---|
| **Effort** | **Low.** One frozenset, its docstring, and the measurement that proves the delta. Smaller than 14.2. |
| **Technical risk** | **Low.** Strictly flag-reducing (§2.4); no threshold, no predicate, no schema. |
| **Governance risk** | **Low.** No amendment to any locked decision. The flat-set choice is a new decision, recorded with its rejected alternative. |
| **Measurement risk** | **Medium — the only real one.** §2.3's corpus prediction is unmeasured. If TS members are *not* flagged as derived, 14.3's rationale narrows to fixtures and the story must say so rather than quietly keeping its framing. |
| **Timeline** | Adds one story between 14.2 and 13.5. Does not block 14.1, which is `ready-for-dev` now. |

---

## 4. Detailed Change Proposals

### 4.1 `epics.md` — 1 edit

Insert after Story 14.2, and amend the Epic 14 **Covers:** line to add *"· the cross-language
assertion vocabulary"*.

> ### Story 14.3: The assertion vocabulary crosses the languages the installer ships
>
> As the Argus maintainer,
> I want an assertion to be recognised in every language the default install can parse,
> So that a test with a real assertion is never flagged vacuous for being written in TypeScript.
>
> **Acceptance Criteria:**
>
> **Given** `_ASSERTION_CALLEES` holds 23 names and every one is `unittest`, while the index emits
> `expect`, `toBe` and `assertEquals` as ordinary edges
> **When** this story completes
> **Then** the table recognises the assertion vocabulary of the languages `pyproject.toml` ships a
> grammar for and DN-6 admits — at minimum JS/TS (`expect`, `toBe`, `toEqual`, `toThrow`, `assert`,
> `ok`, `deepStrictEqual`), Java/JUnit (`assertEquals`, `assertThat`, `assertTrue`, `fail`) and Go
> (`Fatal`, `Fatalf`, `Error`, `Errorf`, `NoError`, `Equal`) — **and the fixture measured at
> `assertions=0 density=0 FLAGGED` in the source proposal is measured again and is NOT flagged.**
>
> **Given** the change can only raise `assertion_sites`, the numerator of a ratio whose floor fires
> from below
> **Then** it is demonstrated by execution that **no test flagged before is unflagged into a
> BLOCKING finding**, and that the total flag count **falls or holds** — never rises.
>
> **Given** two ratified corpus members are TypeScript (`xagents-webapp`, `agent-smith`) and the
> source proposal's §2.3 prediction about them is explicitly UNMEASURED
> **Then** the flag delta over those members is **measured before and after**, and recorded as a
> number. If the prediction is wrong, the story **records that it was wrong** and does not retro-fit
> its rationale.
>
> **Given** NFR-P2 confines the language conditional to `argus/index/`
> **Then** `_ASSERTION_CALLEES` stays a FLAT, language-agnostic name set on the
> `_UNAMBIGUOUS_TEST_SUFFIXES` precedent (`vacuous_test.py:212-215`); **no language field enters the
> detector**, and the accepted cross-language collision cost is recorded with its rejected
> alternative.
>
> **Given** Story 14.2 owns the same frozenset and adds the pytest helpers to it
> **Then** 14.3 runs **strictly after** 14.2 and does not re-open, re-order or re-litigate 14.2's
> Python entries — the DN-4 discipline, applied to a second pair.
>
> **Given** `D2` (the `startswith("test")` predicate), `D3` (Go selector calls absent from the edge
> set) and `D4` (callback test blocks yielding no definitions) are measured in the source proposal
> **Then** they are **cited, not fixed here**, and the story states plainly that Go and Java tests
> remain unscored after it lands.
>
> **Given** AR8 (PURE scorer), AR4 (`Fraction`, never `float`) and NFR-D2 (deterministic, zero-token)
> **Then** all three hold unchanged.
>
> **Given** local gates are Windows-only while CI runs an ubuntu matrix
> **Then** this story is **not marked done on a local pass alone.**

### 4.2 `sprint-status.yaml` — 1 entry

`14-3-the-assertion-vocabulary-crosses-the-languages-the-installer-ships: backlog`, with a
`last_updated` note recording this proposal and the **after-14.2** ordering constraint.

### 4.3 `deferred-work.md` — 3 entries

`DF-14-3-A` (**D2** — the test-function predicate is Python-shaped; Go `TestXxx` and JUnit
`@Test` never score), `DF-14-3-B` (**D3** — Go selector calls absent from the edge set;
`argus/index/ast_index.py`), `DF-14-3-C` (**D4** — callback test blocks yield no definitions;
idiomatic Jest/Mocha/Vitest invisible). Each carries the six CC-3 fields, the measured mechanism
from §1.3, and `target_story: NONE` pending a multi-language capability decision.

### 4.4 What this proposal does NOT touch

`ASSERTION_DENSITY_FLOOR` · `MOCK_RATIO_CEILING` · the ≥80% threshold · corpus membership · FR34 ·
`_MOCK_CALLEES` · the adjudication record · `MANIFEST_FIELDS` · Epic 13's scope · Story 13.5's
charter. **No epic is created and the §2.5 decision is neither taken nor scheduled.**

---

## 5. Implementation Handoff

| Role | Action |
|---|---|
| **PM / Architect (XAgent007)** | Approve or reject. The one judgement call is §2.4's flat-set collision cost — a Python `expect()` would count as an assertion. Alternative is an NFR-P2 breach. |
| **SM** | On approval, apply §4.1–§4.3, then `create-story` for 14.3 **after 14.2 reaches done** — not before, or it will context against a `_ASSERTION_CALLEES` that is about to change under it. |
| **Dev** | 14.1 first (`ready-for-dev` now), then 14.2, then 14.3. |

**Sequencing invariant:** 14.3 after 14.2 · 13.5 after all of Epic 14 · nothing here reorders 14.1.

---

## 6. Approval

✅ **APPROVED** by **XAgent007** on **2026-08-17** — §4.1–§4.3 as written, **including the flat-set
decision** of §2.4 and its recorded collision cost.

**Applied 2026-08-17.** All three §4 edits landed:

| § | Artifact | Applied |
|---|---|---|
| 4.1 | `epics.md` — Epic 14 **Covers:**/**Source:** amended; Story 14.3 inserted after 14.2 | ✅ |
| 4.2 | `sprint-status.yaml` — `14-3-…: backlog` + the after-14.2 ordering constraint + `last_updated` | ✅ |
| 4.3 | `deferred-work.md` — `DF-14-3-A`, `DF-14-3-B`, `DF-14-3-C` filed with their measured mechanisms | ✅ |

**`argus/` is byte-unchanged by this proposal.** No detector, threshold, predicate or test was
modified — that is Story 14.3's work, and it has not started.

**Two things landed alongside this approval and are NOT part of it**, recorded here so the boundary
is legible rather than inferred:

- **Epic 15 + Story 15.1 were created by OPERATOR DECISION**, not by this proposal. §4.4 above says
  *"no epic is created"* and that remains true **of this document**. The epic was admitted by direct
  authorisation on the Story 13.4 precedent, and `epics.md` records the distinction at its header.
- **`DF-13-5-A` was ANSWERED** — as a **pre-registered rule**, decided before Story 13.5 ran and
  before any bench repository was chosen. One round; a zero-finding or sub-80% outcome means the
  FR34 disclosure stands for V1.5 and the next attempt requires a better **detector**, not a bigger
  bench.

**Author's note, retained unchanged from the draft.** The honest weak point is §2.3: the
corpus-impact claim is a derivation from a measured mechanism, not a measurement. It is labelled as
such in three places rather than smoothed into the evidence, and Story 14.3 carries an AC that
measures it and records a wrong prediction as wrong. **This approval therefore approves a story
whose first task may disprove part of its own rationale** — which is the intended shape, not an
oversight in it.
