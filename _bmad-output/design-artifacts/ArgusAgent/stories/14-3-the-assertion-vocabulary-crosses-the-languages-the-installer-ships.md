# Story 14.3: The assertion vocabulary crosses the languages the installer ships

Status: done

<!-- Contexted 2026-08-18 on HEAD e2e278c (post-14.1, post-14.2). Every premise below was
     RE-DERIVED BY EXECUTION at contexting time against the tree as it stands, through the
     SHIPPED `build_ast_index` and the SHIPPED `VacuousTestDetector`. `argus/` was not modified
     to produce any number in this file. TWO of the premises this story was written on DID NOT
     SURVIVE; both are recorded as failures in §0.2 and §0.4 rather than smoothed over. Nothing
     is inherited from sprint-change-proposal-2026-08-17b.md — cite §0, never the proposal, for
     a number. -->

## Story

As the Argus maintainer,
I want an assertion to be recognised in every language the default install can parse,
So that a test with a real assertion is never flagged vacuous for being written in TypeScript.

### What this story IS

**One frozenset widened: `_ASSERTION_CALLEES`, the density NUMERATOR's vocabulary.** It holds 53
names today and every one of them is Python. The shipped index emits `expect`, `toBe`, `ok`,
`equal` and `deepEqual` as ordinary edges — the index *sees* them; the table does not know them —
so a JS/TS test whose assertion is real can score `assertion_sites=0`, fall below
`ASSERTION_DENSITY_FLOOR = 1/4`, and be flagged heuristically vacuous. That is a **false
accusation**, the failure class Epic 14 exists to close, arriving by a different route.

### What it is NOT

- **It does NOT touch `_CORROBORATION_ASSERTION_CALLEES`.** That table is the moat (DN-14-2-1) and
  stays at exactly 23 names. §0.7 proves by execution why widening it is neither needed nor safe.
- **It does NOT move a threshold.** `ASSERTION_DENSITY_FLOOR` and `MOCK_RATIO_CEILING` are
  byte-unchanged. §0.8 is the guard list, not a menu.
- **It does NOT touch the denominator.** Story 14.2 owns `_count_statements` and
  `provenance_scan.logical_statement_count`. Do not re-open them — but §0.2 and §0.3 are about
  what 14.2's denominator did to *this* story's premise, and you must read both.
- **It does NOT fix `DF-14-3-A` / `-B` / `-C`.** Go and Java stay unscored after it lands and
  callback-style JS/TS suites stay invisible. §0.12 carries the coupling warning.
- **It does NOT re-measure the gate.** That is Story 13.5, after Epic 14.
- **It does NOT re-adjudicate.** `validation-corpus/**` is not written by this story.

---

## ⛔ §0 — Premise re-measurement (this project's create-story control)

**Measured 2026-08-18 on `e2e278c` by execution.** The two TypeScript corpus members and the two
Python ones were staged at their **unchanged pinned shas** via `git show <sha>:<path>` into temp
trees and put through the shipped index and the shipped scorer. Per `AI-E12-10`, confirmations
are recorded as well as divergences. **Re-measure on your own baseline (Task 0) — inherit
nothing, including this.**

### §0.1 — Baselines, verbatim

```
pytest                 -> 1621 collected / 1621 passed / 0 failed / 0 skipped, exit 0
mypy argus             -> Success: no issues found in 87 source files
bandit -r argus        -> 19 Low / 0 Medium / 0 High; confidence 0 / 0 / 6 / 13
```

| Premise | Re-measured on `e2e278c` | Consequence |
|---|---|---|
| `_ASSERTION_CALLEES` holds **23** names, all `unittest` | ❌ **STALE — it holds 53.** Story 14.2 widened it (23 unittest + 13 unittest gaps + 3 pytest + 14 `unittest.mock`) | The story's own headline premise is a pre-14.2 figure. Say **53**, never 23 |
| `_CORROBORATION_ASSERTION_CALLEES` is FROZEN at 23 | ✅ **CONFIRMED**, `vacuous_test.py:361-387`, pinned by `-116` | §0.7 — you must not widen it |
| `ASSERTION_DENSITY_FLOOR = 1/4`, `MOCK_RATIO_CEILING = 1/2` | ✅ **CONFIRMED** unchanged, `vacuous_test.py:202-203` | AC4 — must stay byte-identical |
| The naming-convention predicate exists (14.2 / DN-14-2-3) | ✅ **CONFIRMED**, `_ASSERTION_NAMING_CONVENTION = \A_?assert\w*\Z`, `vacuous_test.py:325` | §0.6 — it already admits three of the four Java names |
| minions test functions / flagged | **3,551 / 653 = 18.4%** | Reproduces 14.2's post-fix figure exactly. The proposal-era 52.0% is void |
| agent-smith test functions / flagged | **1,122 / 295 = 26.3%** | Reproduces 14.2's post-fix figure exactly. The proposal-era 60.7% is void |
| xagents-webapp test functions / flagged | **73 / 17 = 23.3%** — of which **72 are `.py` and 1 is `.ts`** | §0.4. This member had never been measured before |
| corroborated anywhere in any member | **0** | 14.1's property still holds |
| `argus/detectors/vacuous_test.py` | **929 lines**, headroom **271** | Room here |
| `argus/detectors/provenance_scan.py` | **926 lines**, headroom **274** | Room here |
| ⚠️ `tests/test_vacuous_detector.py` | **1,128 lines, headroom 72** | ⛔ **Do not add cases here.** §0.9 |
| ⚠️ `tests/test_vacuous_density.py` | **1,060 lines, headroom 140** | `-116` lives here and must be re-authored **in place**. §0.9 |
| ⚠️ `argus/pipeline.py` | **1,111 lines, headroom 89**, NOT exempt | **Do not add to it** |
| minions@`ec63b729` · agent-smith@`9ab774d7` · xagents-webapp@`33a86525` | ✅ **ALL THREE REACHABLE** (`git cat-file -t` → `commit`) | The TS prediction is measurable, and §0.4 measures it |
| A `project-context.md` exists | ❌ **NONE.** `architecture.md`, `deferred-work.md`, `stories/14-1-*.md`, `stories/14-2-*.md` and this file **are** the context | — |
| Working tree is clean | ❌ **NO — and that is expected.** §0.11 | Your diff will contain other people's work |

**Local clone paths for the pinned members** (pass the **Windows** path form to `git -C` from
Python; a Git-Bash `/d/...` path fails with exit 128):

```
minions          D:/ProjectX/XAgents/XAgents/Minions              @ ec63b7293b7036bf910a0d1b5e61aba7dc551526
agent-smith      D:/ProjectX/XAgents/XAgents/XAgents/Agent-Smith  @ 9ab774d7bf5d61da552c61094b2d478f72dfbb6d
xagents-webapp   D:/ProjectX/XAgents/XAgents/XAgents-WebApp       @ 33a86525a4981c2725133c3f297ce003c1ef8a2b
```

### §0.2 — ⛔⛔ THE PREMISE THAT DID NOT SURVIVE #1. The named fixture is no longer flagged

**Read this before writing a line of code.** The proposal's §1.3 six fixtures, re-measured through
the same shipped surfaces on the post-14.2 tree:

| Fixture | test file? | definitions | `_is_test_function`? | scored | **outcome on `e2e278c`** | proposal said |
|---|---|---|---|---|---|---|
| `test_control.py` | ✅ | class + function | ✅ | ✅ | `assertions=2 stmts=3 density=2/3` **not flagged** | not flagged ✅ |
| `plainfn.test.js` — `expect(r).toBe(5)` | ✅ | function | ✅ | ✅ | `assertions=0 **stmts=0** density=0` **NOT FLAGGED** | **FLAGGED — false** ❌ |
| `calc.test.js` — `describe`/`it` | ✅ | **none** | — | ❌ | silent (`no_test_functions`) | silent ✅ |
| `parser_test.go` | ✅ | function | ❌ | ❌ | silent | silent ✅ |
| `testify_test.go` | ✅ | function | ❌ | ❌ | silent | silent ✅ |
| `CalcTest.java` | ✅ | class + function | ❌ | ❌ | silent | silent ✅ |

⚠️ **The one row this story exists for is the one that changed.** Story 14.2 replaced the
LINE-counting denominator with `provenance_scan.body_statement_count`, a **Python-shaped logical
statement scanner**. On `function testAddsNumbers() {` the trailing `{` is an unclosed bracket, so
the scanner treats the entire function as ONE continued logical statement — the `def` header — and
the **body counts ZERO**. `heuristically_vacuous` requires `statement_count > 0`, so the test is
not flagged. **The false accusation was not repaired by 14.2; it was replaced by silence.**

⛔ **Therefore `epics.md`'s Story 14.3 AC — *"the JS fixture measured at `assertions=0 density=0
FLAGGED` is re-measured and is NOT flagged"* — is now VACUOUSLY TRUE. It passes with zero code
change.** Discharging it as written would be `AI-E3-1` in its purest form: a criterion satisfied by
a defect that moved rather than by a fix. AC1 re-states the target on measurement (DN-14-3-4) and
still requires that fixture to be measured — for the record that it is unflagged **for a different
reason**.

### §0.3 — …BUT THE FALSE ACCUSATION IS ALIVE, in a narrower and precisely-bounded shape

Eight JS/TS/Go function shapes, measured through the same surfaces:

| Shape | `stmts` | `asserts` | **FLAGGED** |
|---|---|---|---|
| `function testOneLiner() { … }` — whole body on the `function` line | 0 | 0 | ❌ no |
| `function testNested() {` … K&R, nested object literal | 0 | 0 | ❌ no |
| `function testTyped(): void {` — TS | 0 | 0 | ❌ no |
| `async function testAsync(): Promise<void> {` — TS | 0 | 0 | ❌ no |
| `function testMocky() {` — `jest.fn()` mock interaction | 0 | 0 | ❌ no |
| **`function testAllman()` + `{` on its OWN line** | **1** | **0** | ⛔ **YES — the surviving false accusation** |
| `func testGo(t *testing.T)` + `{` on its own line | 0 | 0 | ❌ no |
| `function testNothing()` Allman, genuinely assertion-free | 1 | 0 | ✅ yes — **correctly** flagged |

**The mechanism, stated exactly:** when the opening brace is NOT on the `function` line, the header
closes as its own logical statement and the body scores ≥1. Density is then `0/n`, below the floor,
and the test is flagged **even though `expect(r).toBe(5)` is right there in the edge set.**

**And the widening closes it — measured, not assumed.** With the candidate vocabulary applied to
`_ASSERTION_CALLEES` only:

```
allman.test.js:testAllman            asserts 0 -> 2   FLAGGED True  -> False   ✅ closed
empty.test.js:testNothing            asserts 0 -> 0   FLAGGED True  -> True    ✅ signal preserved
```

Both arms matter. A one-directional check would pass on a change that removed the flag by removing
the capability (`-117`'s lesson, applied to a second vocabulary).

### §0.4 — ⛔⛔ THE PREMISE THAT DID NOT SURVIVE #2. The corpus prediction is REFUTED, not unmeasured

The source proposal §2.3 derived — and labelled UNMEASURED — that *"TypeScript tests in those two
members are being scored `assertion_sites=0` and flagged heuristically vacuous today."* Its §3.3
pre-registered the branch: *"If TS members are not flagged as derived, 14.3's rationale narrows to
fixtures and the story must say so rather than quietly keeping its framing."*

**That branch is taken. Measured over all three members at their pinned shas, before and after the
candidate widening:**

| Member | test functions scored | by extension | flagged BEFORE | flagged AFTER | **GAINED** | **LOST** | corroborated |
|---|---|---|---|---|---|---|---|
| minions | 3,551 | 3,551 `.py` | 653 (18.4%) | 653 (18.4%) | **0** | **0** | 0 → 0 |
| agent-smith | 1,122 | **1,122 `.py`, 0 `.ts`** | 295 (26.3%) | 295 (26.3%) | **0** | **0** | 0 → 0 |
| xagents-webapp | 73 | **72 `.py`, 1 `.ts`** | 17 (23.3%) | 17 (23.3%) | **0** | **0** | 0 → 0 |

**The prediction is WRONG, and this story records it as wrong rather than retro-fitting its
rationale.** The flag delta of this change over the entire ratified corpus is **zero**.

**Why — the funnel, measured:**

| | agent-smith | xagents-webapp |
|---|---|---|
| TS/JS test files staged | 88 | 279 |
| AST-eligible | 88 | 277 (2 `syntax_error`) |
| `function` definitions extracted | 169 | 410 |
| …whose name `startswith("test")`, case-sensitive | **0** | **1** (`testDbConnection`) |
| …case-INsensitive | **0** | **1** |
| TS test functions actually scored | **0** | **1**, and it is **not flagged** |

`DF-14-3-A` (the case-sensitive `startswith("test")` predicate) and `DF-14-3-C` (callback test
blocks yield no definitions) keep essentially **every real TypeScript test out of the scorer
entirely**. Both members write `describe`/`it`/`test(…)` callback suites; neither writes
`function test*`. **D1's blast radius is gated by D2 and D4** — which is the same coupling the
ledger already records from the other direction.

**What this means for this story, stated plainly and NOT smoothed:**

1. The defect is **real and reproducible** (§0.3) — it is a live mechanism in shipped code, and a
   user writing Allman-brace JS gets a false accusation today.
2. Its **incidence on the ratified corpus is zero**, so this story cannot claim a corpus benefit
   and must not. Its rationale is the **mechanism** and the **fixture**, exactly as §3.3 predicted.
3. The change is therefore also **zero-risk on the corpus**, which is the other half of the same
   measurement and is the strongest thing that can honestly be said for it.
4. It is a **prerequisite for Epic 15**: a multi-language bench cannot be assembled on a detector
   that cannot see a JS assertion, whatever the current corpus does.

### §0.5 — The vocabulary the ratified corpus ACTUALLY writes (a correction to the epic's minimum list)

Top call edges measured over the staged TS/JS test files:

| Member | harness | measured assertion vocabulary (with counts) |
|---|---|---|
| xagents-webapp | Jest / Vitest | `expect` **6876** · `toBe` **2560** · `toHaveBeenCalledWith` **696** · `toHaveBeenCalled` **569** · `objectContaining` 376 |
| agent-smith | `node:test` + `node:assert` | `equal` **1548** · `ok` **758** · `deepEqual` **506** · `match` 469 · `doesNotMatch` 76 |

⚠️ **`epics.md`'s minimum JS/TS list — `expect`, `toBe`, `toEqual`, `toThrow`, `assert`, `ok`,
`deepStrictEqual` — covers only three of the names the two ratified TypeScript members actually
write.** It misses `toHaveBeenCalled` / `toHaveBeenCalledWith` (Jest's dominant idiom) and the
whole `node:assert` core (`equal`, `deepEqual`, `strictEqual`, `notEqual`, `throws`, `rejects`).
The minimum is a **floor**, not a specification. DN-14-3-2 sets the shipped set.

⛔ **`match` and `doesNotMatch` are the dangerous pair and are EXCLUDED.** `re.match` in Python and
`String.prototype.match` in JavaScript are pervasive **non-assertions**. Their error direction is
flag-*reducing*, so they cannot manufacture an accusation — but they would silently suppress
**real** flags on Python code, which is a recall regression wearing a precision fix's clothes. The
accepted-collision-cost argument that carries `expect` does **not** carry `match`: `expect` has no
common non-assertion meaning; `match` does, in both languages. Recorded with its reason so it is a
decision rather than an omission.

### §0.6 — The naming-convention predicate ALREADY covers Java/JUnit — measured

`_ASSERTION_NAMING_CONVENTION` (`\A_?assert\w*\Z`, Story 14.2 / DN-14-2-3) admits any callee whose
name begins `assert` / `_assert`. Measured against `epics.md`'s Java/JUnit minimum:

| Name | in `_ASSERTION_CALLEES` today | matches the convention | in the FROZEN table |
|---|---|---|---|
| `assertEquals` | no | ✅ **already admitted** | no |
| `assertThat` | no | ✅ **already admitted** | no |
| `assertTrue` | ✅ **already present** | ✅ | ✅ |
| `fail` | ✅ **already present** | no | ✅ |
| `assert` (node) | no | ✅ **already admitted** | no |

**All four of the epic's Java/JUnit names are already recognised by the density numerator today**,
and adding them changes no behaviour. AC2 still adds `assertEquals` and `assertThat` to the table
**explicitly**, for the same reason 14.2 enumerated the `unittest.mock` methods that also match the
convention: *"the convention is a fallback for names this project cannot know, and the ecosystem's
own vocabulary should be readable in one place."* **The behaviour delta of those two names is ZERO
and the story must say so** rather than claiming credit for it.

⛔ `assertTrue` and `fail` are already in **both** tables. Do not add them again, and do not touch
the frozen table to "align" it.

Java is moot regardless: `CalcTest.java`'s `computesSum` is never scored (`DF-14-3-A`).

### §0.7 — ONE table or two? And can JS/TS ever be verdict-eligible? Both answered by execution

**This is the section 14.2's review asked for, and it is the one you must not get wrong.**

**(a) 14.3 widens exactly ONE table.** `_ASSERTION_CALLEES` — the density numerator.
`_CORROBORATION_ASSERTION_CALLEES` stays at exactly 23 names, pinned by
`TC-ArgusAgent-DETECT-001-116`.

**(b) That does not breach NFR-P2, and here is why in one sentence:** NFR-P2 confines the
*language conditional* to `argus/index/`, and there is none here — both tables are **flat
frozensets of plain strings**, partitioned by **QUESTION** (*"does this test assert anything?"* vs
*"which edges are not SUT calls?"*, DN-14-2-4), never by **LANGUAGE**. That is the same shape
`_UNAMBIGUOUS_TEST_SUFFIXES` and `_CASE_SENSITIVE_TEST_SUFFIXES` already have in this module: two
tables for two matching **rules**, not two languages. No language field, no per-language
sub-table, no grouping key enters the detector. Groupings are **comments**.

**(c) Can a JS/TS test become corroborated / verdict-eligible after this story? NO — and NOT
because of DN-14-2-1.** Measured: the *most favourable* JS fixture that could exist — Allman
braces so the denominator is non-zero, an explicit `Mock()` constructor by its Python name, a
discarded SUT call, and a JS assertion referencing the mock — put through `provenance_evidence`
under **both** vocabularies:

```
⚠️ AS CONTEXTED — the second row's sut=3 does NOT reproduce. Kept visible, corrected below.
FROZEN 23 (shipped)                     fact(a) sut=4  discarded=False  mock_ref_asserts=0  -> CORROBORATED=False
ONE-TABLE hypothetical (widened + 14.3) fact(a) sut=3  discarded=False  mock_ref_asserts=0  -> CORROBORATED=False
```

⚠️ **CORRECTED 2026-08-18 by review iteration 2** (the only edit this section has taken, and it
is a factual correction rather than a re-scoping). `sut=` was never defined; it is
`ProvenanceEvidence.consumed_sut_calls`. Against the fixture `TC-ArgusAgent-DETECT-001-131`
**actually pins** — which iteration 2 also had to reshape, because the fixture it shipped cleared
the density floor and so never reached `provenance_evidence` at all:

```
FROZEN 23 (shipped)                     consumed_sut=3  discarded=False  mock_ref_asserts=0  -> CORROBORATED=False
ONE-TABLE hypothetical (widened + 14.3) consumed_sut=1  discarded=False  mock_ref_asserts=0  -> CORROBORATED=False
heuristically_vacuous=True (mock_ratio 4/7 > 1/2), fact (a) holds -> fact (b) IS asked.
```

The iteration-1 fixture's own real figures were `consumed_sut=4` / `consumed_sut=2`: `sut=4` was
right, `sut=3` was wrong by one. **The conclusion is unchanged under every fixture measured** —
`mock_referencing_assertions` is 0 under both vocabularies because `_mock_bound_names` binds
nothing in `const fake = Mock();`, which is the "Python-syntax-shaped" claim, now asserted
directly instead of inferred from a `False`. The ledger entry carries the same correction.

…and the same for the idiomatic `jest.fn()` variant. **Both fact-(b) clauses measure False on JS
input under a one-table design carrying the full 14.3 vocabulary.** The barriers are elsewhere and
they are structural: `_MOCK_CALLEES` carries **no** JS mock constructor (`fn`, `spyOn`, `stub`,
`vi`, `sinon` are all absent; only `Mock` overlaps, by coincidence of spelling), and fact (b)'s
assignment/statement machinery is Python-syntax-shaped.

**Conclusions the dev must carry, in order:**

1. **DN-14-2-1 is the OUTER of two independent barriers, not the cause of the limitation.** It is
   therefore **not an unrecorded trap that 14.2 laid for 14.3** — the answer to the question 14.2's
   review raised is *no*, and it is answered by measurement rather than by argument.
2. This story's widening is **structurally incapable** of manufacturing a verdict-eligible false
   accusation, on any language. AC3 still proves it by execution rather than resting on this.
3. **The limitation is ACCEPTABLE for this story's scope**, on the locked asymmetry: *a false 🔴 is
   the lethal failure; a real vacuous test left advisory is tolerable.* A blocking rule that cannot
   fire on JS/TS cannot make a false claim about JS/TS, and Epic 14's charter is that the
   **blocking** rule proves what it claims.
4. ⛔ **But it must not pass unrecorded, because it BOUNDS EPIC 15.** A TypeScript bench member can
   contribute **advisory findings only** — never a verdict-eligible one, therefore never a data
   point for the ≥80% precision gate. **AC6 requires a new ledger entry with a named owner
   carrying the measurement above.** Nothing in the ledger states this today: the source proposal
   §2.3 notes `_MOCK_CALLEES` is Python-only in passing, and it was never filed.

### §0.8 — Guards: predict BEFORE you measure

**Write your prediction into the Dev Agent Record before running the suite, then record the result
beside it.** A prediction produced after the measurement is not a prediction. Measured basis for
the "must not move" rows: **none of the candidate names appears in any fixture** in
`test_vacuous_detector.py`, `test_vacuous_density.py`, `test_default_path_blocking_verdict.py` or
`tests/cartridges/` — the single occurrence of each is the `-116` literal itself.

| Guard | Where | Expectation | Why |
|---|---|---|---|
| **`TC-ArgusAgent-DETECT-001-116`** | `test_vacuous_density.py:544`, assertion at **`:582-587`** | ⚠️ **WILL GO RED — and it is the ONLY guard that will** | It asserts `not (cross_language & _ASSERTION_CALLEES)` over exactly `{expect, toBe, toEqual, toThrow, deepStrictEqual, assertEquals, assertThat, Fatal, Fatalf, Errorf, NoError, ok}`. That is 14.2's *"Story 14.3 has not happened yet"* assertion, and this story is what makes it false. **Re-author it as an INTENDED behaviour change, `-86`-style, with its reason recorded** — never delete the case, never nudge the literal to dodge the intersection. Its other three arms (**frozen == 23** · **frozen ⊂ widened** · **both flat frozensets of `str`**) must stay green **untouched**, and the re-authored case must still assert them |
| **`TC-ArgusAgent-DETECT-001-115`** | `test_vacuous_density.py:437` | ⛔ **MUST STAY GREEN — the moat guard (DN-14-2-1)** | Its RED arm feeds `_ASSERTION_CALLEES` to `provenance_evidence`; widening must not break the RED (the mechanism must still reproduce) **and** must not break the GREEN (`frozen_evidence.mock_referencing_assertions == 0`). Verify **both arms** by execution. If the RED arm stops reproducing, repair the FIXTURE — do not delete the arm |
| `TC-ArgusAgent-DETECT-001-87` | `test_vacuous_detector.py:198` | ⛔ must not move | Python fixture, no candidate name |
| `TC-ArgusAgent-DETECT-001-88` | `:225` | ⛔ **MUST NOT MOVE — the moat's own false-accusation guard** | A genuine test must stay unflagged. This is the one whose movement means the fix broke the thing it was protecting |
| `-89`/`-90`/`-91`/`-92`/`-93` | `:242`/`:257`/`:272`/`:283`/`:307` | ⛔ must not move | degrade paths and the exact `Fraction(1, 5)` density case |
| `-101`..`-108` | `:351`-`:808` | ⛔ must not move | 14.1's fact-(b) branch coverage. `-102`'s comment (`:424`) was corrected by 14.2 — **do not re-open it** |
| `-109`/`-110`/`-111`/`-112` | `:697`/`:745`/`:1031`/`:1076` | ⛔ must not move | 14.1's wrapping / `;`-compound corroboration cases |
| `-113`..`-114`, `-117`..`-122` | `test_vacuous_density.py` | ⛔ must not move | 14.2's denominator and vocabulary guards. **`-117` is the both-directions vocabulary guard** — if it moves, your widening changed Python behaviour and you must explain why |
| `TC-ArgusAgent-VERDICT-001-30` | `test_default_path_blocking_verdict.py:246` | ⛔ **BOTH ARMS MUST SURVIVE** | A single-arm `-30` is a regression of 14.1's escalation resolution |
| `TC-ArgusAgent-VERDICT-001-116`/`-117` | `:332`/`:418` | ⛔ **MUST NOT MOVE** | End-to-end proof that wrapping/semicolons alone cannot reach a blocking verdict. If either goes red you have re-opened 14.1 |
| `test_dogfood_plan.py` · `test_dogfood_proof.py` · `test_dogfood_artifact_currency.py` | — | ⚠️ **PREDICTED NOT TO FIRE — this REVERSES the usual expectation** | Measured: over Argus's own tracked test tree the candidate widening moves **0 flags gained / 0 lost across 1,777 test functions, corroborated 0 → 0**; over minions, **0 / 0**. No artifact should change and **`AI-E12-11` should not be needed.** ⛔ **If a currency guard DOES fire, that is a FINDING** — stop, explain the mechanism, and only then regenerate through the renderers |
| `test_pipeline_signature_demo.py` · `test_cartridge_selfaudit.py` · `test_precision_replay.py` | — | ⚠️ must not move | Detector-output-dependent; predicted unchanged for the same measured reason |
| `test_module_size_ceiling.py` | — | ⚠️ | §0.9 — headroom is 72 lines in the obvious place |
| `TC-ArgusAgent-DOCS-001-78` | `test_governance_record_integrity.py:186` | ⚠️ **lints THIS file** | Never write a `DF-*` id on the same line as a closure verb unless the ledger really carries that disposition. It went red twice on 2026-08-17 for exactly that |

**Blast-radius floor, inherited from 14.1/14.2 and still current:** 21 modules reference the rule
id; **10 stage a cartridge or run the detector end to end**, plus
`test_default_path_blocking_verdict.py`. **Treat it as a floor. Run the full suite.**

### §0.9 — Where the new tests go. Decide before you write, not after

| Module | lines | headroom | verdict |
|---|---|---|---|
| `tests/test_vacuous_detector.py` | **1,128** | **72** | ⛔ **Do not add cases here** |
| `tests/test_vacuous_density.py` | **1,060** | **140** | `-116` lives here and is re-authored **in place** — an edit, not growth |

**PRESCRIBED: a new cohesion module `tests/test_vacuous_cross_language.py`** for this story's new
cases, on the `provenance_scan.py` / `test_vacuous_density.py` precedent — a cohesion boundary, no
function split across it, the module owns the cross-language vocabulary question end to end.

⛔ **Do not** add a size exemption (the registry may only **shrink**, and `-04` enforces that),
narrow the sweep, or delete existing cases to make room. A test module is not a status document,
so no `tests/test_status_document_registry.py` registration is required — and `:268` asserts story
files are *absent* from that registry, so do not add this file either.

### §0.10 — TWO open ledger entries name THIS story as their target. They are in scope

Both were filed by Story 14.2 and both carry a named owner pointing here. Discharge them, record
the disposition in the ledger, and do **not** re-open their analysis.

- **`DF-14-2-A`** — `tests/test_vacuous_detector.py:836-837` calls `pytest.importorskip("tree_sitter")`
  / `("tree_sitter_python")` at module level. `audit-ci.yml:100` sets
  `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` precisely so a missing grammar cannot be answered with a
  skip, and `importorskip` **ignores that variable** — so if either package went missing in CI,
  roughly forty fact-(b) guards including the moat's own `-88` would report SKIPPED and the run
  would read green. `owner: Story 14.3 dev`. **The pattern to copy already exists** in
  `tests/test_vacuous_density.py:72-93` — a named `UNEVALUABLE` **failure**, never a skip. This is
  also exactly what AC7.5 demands of your own new module, so the two are one piece of work.
- **`DF-14-2-B`** — `_ASSIGNMENT_RE` (`argus/detectors/provenance_scan.py:116-120`) is `$`-anchored,
  contradicting that module's own platform-neutrality docstring claim at `:65` that *"no pattern
  below is anchored with `$`"*. Not exploitable under current call sites (always invoked on a
  single `splitlines()`-derived line), but the claim is not true as written. `target_story: 14.3`.
  Re-anchor to `\Z` **and demonstrate behaviour-identical** on the corpus rather than asserting it,
  or correct the docstring — prefer the re-anchor.

### §0.11 — Working tree state you must NOT disturb

Pre-existing uncommitted work, none of it yours. This run has deliberately left it uncommitted.

```
 M _bmad-output/.../E-PRD/prd.md           M _bmad-output/.../architecture.md
 M _bmad-output/.../deferred-work.md       M _bmad-output/.../epics.md
 M _bmad-output/.../sprint-status.yaml     M _bmad-output/.../stories/1-5-*.md
 M _bmad-output/.../stories/13-4-*.md      M _bmad-output/.../stories/14-1-*.md
 M tests/test_evidence_citation.py         M tests/test_module_size_ceiling.py
 M tests/test_spec_claim_scope.py          M tests/test_v1_commitment_closure.py
?? argusdemo/  ?? .bmad-drift-audit/  ?? bmad-dev-loop-pack/  ?? _bmad-output/audit-reports/*
?? sprint-change-proposal-2026-08-17{,b}.md  ?? stories/14-2-*.md  ?? stories/15-1-*.md
?? tests/test_status_document_registry.py
```

⛔ **Commit only what this story changes.** `deferred-work.md` is **append-only** and is already
dirty — append your entries and do not rewrite a line of what is there. Do not commit
`stories/1-5-*.md`, `stories/13-4-*.md`, `stories/14-1-*.md`, `epics.md`, `architecture.md`,
`E-PRD/prd.md`, or any of the four `tests/*.py` above.

### §0.12 — Out of scope: cited, not fixed

`DF-14-3-A` (the `startswith("test")` predicate is case-sensitive), `DF-14-3-B` (Go
selector-expression calls never reach the edge set) and `DF-14-3-C` (callback test blocks yield no
definitions) are **cited here and fixed nowhere here**. After this story lands, **Go and Java tests
remain unscored and idiomatic Jest/Mocha/Vitest suites remain invisible.**

⛔ **`DF-14-3-A` MUST NOT be fixed alone, and the one-character fix is the trap.** Go tests are
silent *because* of it. Lowering the predicate's case-sensitivity while `DF-14-3-B` stands would
score every Go test, find `assertion_sites=0` because B hides the assertions, and FLAG it —
converting harmless silence into a **fresh false accusation across an entire language**, inside the
epic opened to stop false accusations. **A and B move together or not at all.** Do not drift into
them; do not "just try" the predicate to see what happens on the corpus.

---

## Acceptance Criteria

### AC1 — The false accusation that ACTUALLY EXISTS is reproduced RED, then closed

1. The **Allman-brace JS fixture of §0.3** — a test containing a real `expect(r).toBe(5)` whose
   opening brace is on its own line — is demonstrated **FLAGGED before the change** and **NOT
   flagged after**, through the real tree-sitter index and the real detector. **Demonstrate the
   RED first.** A guard written after the fix over a defect never demonstrated is `AI-E3-1`.
2. Its **byte-identical assertion-free counterpart stays FLAGGED**, in the same case. A
   one-directional check would pass on a change that removed the flag by removing the capability.
3. The proposal's original K&R fixture (`plainfn.test.js`) is **also measured**, and the record
   states that it is unflagged **because its statement count is zero** (§0.2) — not because this
   story fixed it. ⛔ Do not report the epic's AC as discharged by that fixture.
4. The same pair is measured for **TypeScript** (`.test.ts`), not JavaScript alone. Two ratified
   corpus members are TypeScript and the epic's claim is about TypeScript.

### AC2 — The vocabulary is measured, not copied, and every name has a recorded reason

1. `_ASSERTION_CALLEES` gains, at minimum, the epic's list: JS/TS `expect`, `toBe`, `toEqual`,
   `toThrow`, `assert`, `ok`, `deepStrictEqual`; Java/JUnit `assertEquals`, `assertThat`; Go
   `Fatal`, `Fatalf`, `Error`, `Errorf`, `NoError`, `Equal`.
2. It **additionally** gains the names the ratified TypeScript members actually write, re-measured
   on your own baseline (§0.5 is the prediction): the Jest `toHaveBeenCalled` family and the
   `node:assert` core. **Each addition is justified by a measured count or by an ecosystem
   citation** — never by taste.
3. ⛔ **`match` and `doesNotMatch` are EXCLUDED**, with the reason recorded (§0.5). If you disagree
   after measuring, you may include them **only** with a measured statement of how many Python
   flags they remove across all three members — and that number must be **0**.
4. `assertTrue` and `fail` are **already present**; they are not added again. The **zero behaviour
   delta** of `assertEquals`/`assertThat` (already admitted by the naming convention, §0.6) is
   **stated as zero**, not claimed as a fix.
5. The set stays **FLAT and language-agnostic** (NFR-P2, AC7 of 14.2): **no language field, no
   per-language sub-table, no grouping key enters the detector.** Groupings are **comments**.
6. The accepted cross-language collision cost is recorded with its **error direction** and its
   **rejected alternative** — a Python function named `expect` or `ok` now counts as an assertion;
   the direction is one *fewer* flag; the alternative is the NFR-P2 breach.

### AC3 — Nothing GAINS a flag, and the corroboration path does not move at all

1. Over **all three** members at their unchanged pinned shas, flags **GAINED = 0** — recorded as a
   number, per member, before and after. §0.4 measures 0/0/0. *A change that can only remove flags
   must be shown to have only removed them.*
2. Flags **LOST** is recorded per member as well. §0.4 measures **0** on all three; if yours
   differs, that is a finding to explain, not a number to round off.
3. `ast_corroborated` is **byte-identical** for every scored test function in all three members.
4. ⛔ **`_CORROBORATION_ASSERTION_CALLEES` is byte-unchanged at 23 names**, proven by diff.
5. **`TC-ArgusAgent-DETECT-001-115` is green on both arms** — the RED arm still reproduces the
   mechanism and the GREEN arm still measures `mock_referencing_assertions == 0`.

### AC4 — Thresholds and the contract surface are byte-unchanged

1. `ASSERTION_DENSITY_FLOOR = Fraction(1, 4)` and `MOCK_RATIO_CEILING = Fraction(1, 2)` — **proven
   byte-identical by diff**, not by inspection.
2. `VacuousTestScore` keeps its shape: frozen, `extra="forbid"`, same field names and types.
   `assertion_density` and `mock_ratio` remain exact `Fraction`, **never `float`** (AR4).
3. `RULE_HEURISTIC` / `RULE_AST` vocabulary unchanged, and the Story 1.6 verdict-eligibility
   surface (`advisory` + `depth_supported` + `rule_id`) unchanged.
4. The scorer stays **PURE** (AR8) and deterministic (NFR-D2): no clock, uuid, random or
   iteration-order in any `.argus/`-bound output; any set that reaches a message is `sorted()`.
5. `argus/pipeline.py` is **untouched** (89 lines of headroom). `_count_statements`,
   `logical_statement_count` and `body_statement_count` are **untouched** — 14.2 owns them.
6. `_is_test_function` is **untouched** (`DF-14-3-A`, §0.12).

### AC5 — `TC-ArgusAgent-DETECT-001-116` is re-authored as an intended behaviour change

1. The guard is predicted RED **before** the suite is run (§0.8) and the prediction is in the Dev
   Agent Record.
2. It is **re-authored, never deleted and never nudged**: the `cross_language` literal becomes a
   statement about what Story 14.3 *did*, with the reason and the date, in the `-86` style Story
   14.1 established for an intended behaviour change.
3. Its **other three arms survive unchanged and still assert**: frozen table is exactly 23 · frozen
   is a strict subset of widened · both are flat `frozenset`s of `str`.
4. ⛔ If any **other** guard moves, it is named, its mechanism explained, and it is argued or
   fixed — never adjusted to match output.

### AC6 — The corroboration limitation is RECORDED, with a named owner

1. A **new `deferred-work.md` entry** is appended (append-only) carrying the six CC-3 fields and
   the §0.7 measurement: **no non-Python test can reach verdict-eligibility**, because
   `_MOCK_CALLEES` carries no non-Python mock constructor and fact (b)'s assignment/statement
   machinery is Python-syntax-shaped — **demonstrated to hold even under a hypothetical one-table
   design carrying this story's full vocabulary**, so it is not caused by DN-14-2-1.
2. The entry states the consequence for **Epic 15**: a TypeScript bench member can contribute
   **advisory findings only**, never a data point for the ≥80% precision gate.
3. It carries a **named owner** (`AI-E9-8`) and a `target_story`.
4. The entry is filed as a **new** id. `DF-14-3-A`/`-B`/`-C` are **cited**, not re-opened — none of
   them states this property.

### AC7 — "Not done on a Windows-only pass" is discharged concretely, not restated

Local gates here are Windows-only; CI runs an ubuntu matrix, and this repository **has already
shipped POSIX-only bugs out of a green Windows run** (`AI-E13-1`). "Done" requires **all** of:

1. **No line-terminator assumption.** Everything operates on the `source.splitlines()` list the
   detector already receives. No regex anchored with `$`; use `\Z`.
2. **No path-separator or encoding assumption** in changed code: `pathlib` only, explicit
   `encoding="utf-8"` on every read, no comparison of a path against a hand-built string. Any
   corpus harness you write passes `git -C` the **Windows** path form — a Git-Bash `/d/...` path
   fails with exit 128 on this machine.
3. **Unicode-safe name matching** for every identifier pattern, so the `nonascii_unicode`
   cartridge's Cyrillic paths keep working.
4. **A CRLF regression test for the cross-language path**: feed the scorer CRLF `.test.ts` source
   and assert a byte-identical `VacuousTestScore`.
5. ⛔ **`pytest.skip` is a FALSE GREEN here.** `audit-ci.yml:100` sets
   `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`. The correct pattern for an unavailable tool is a **named
   `Unevaluable` outcome**, never a skip — copy `tests/test_vacuous_density.py:72-93`. **A skip
   appearing anywhere in the suite is itself the regression signal.** Your new module needs
   `tree-sitter-javascript` / `tree-sitter-typescript`, which are **optional** `[languages]`
   extras — so this is a live requirement here, not a formality.
6. `DF-14-2-A` is discharged as described in §0.10, using that same pattern.
7. `DF-14-2-B` is discharged as described in §0.10, with the equivalence demonstrated rather than
   asserted.
8. **An explicit statement of what could NOT be verified locally**, in the Dev Agent Record: name
   the ubuntu-matrix behaviours you reasoned about but did not execute. Gates are reported as
   **LOCAL**, with *"CI evidence is NOT ESTABLISHED"* stated, exactly as 14.1 and 14.2 did.

### AC8 — Gates, artifacts and hand-off

1. `pytest` (full suite), `mypy argus`, `bandit -r argus` reported as **numbers**, with the Δ
   against §0.1's baseline (**1621 / Success-87 / 19-0-0**). **No new skip, xfail or narrowed
   population.**
2. Module sizes re-measured with the ceiling test's own method
   (`len(Path(p).read_text(encoding="utf-8").splitlines())`) and reported. **No size exemption.**
3. Dogfood artifacts: **predicted unchanged** (§0.8). Run the currency guard; if it is green, say
   so and regenerate nothing. If it fires, explain the mechanism first, then discharge through
   `AI-E12-11`'s commit → regenerate → commit-separately sequence. ⛔ Never hand-edit a generated
   artifact; never loosen an assertion to make a currency guard green (`DF-8-5-B`).
4. Anything deferred is filed in `deferred-work.md` (**append only**) with a **named owner**
   (`AI-E9-8`).
5. `git tag -l` stays empty; no push; nothing outward-facing changed beyond what the ACs require.
6. **Re-run the full suite after your last prose edit** — `TC-ArgusAgent-DOCS-001-78` and the other
   governance guards lint this very file, and `AI-E13-1` is the story of a hand-off that skipped
   exactly this step.

---

## Developer Context & Guardrails

### Locked decisions this story must CITE rather than reopen

| Locked | Where | Consequence here |
|---|---|---|
| **A false 🔴 is the lethal failure; a real vacuous test left advisory is tolerable** | `vacuous_test.py` module docstring | The asymmetry that makes §0.7's limitation acceptable |
| **CC#6 — no 🔴 without AST corroboration AND sign-off** | `architecture.md` §Cross-Cutting #6 | Why AC3.3/3.4 are release-blocking |
| **DN-14-2-1 — the corroboration path reads a FROZEN vocabulary; only the density numerator reads the widened one** | `stories/14-2-*.md`; `vacuous_test.py:327-360` | **The single most important inherited decision.** It is what lets you widen four languages without re-opening the moat |
| **DN-14-2-4 — the two vocabularies are two QUESTIONS, not two spellings of one** | same | Neither is derived from the other. Do not "tidy" them together |
| **DN-14-2-3 — the project-helper naming convention is a separate named predicate** | `vacuous_test.py:303-325` | §0.6 — it already admits the `assert*` half of the Java list |
| **DN-4 (Story 14.1)** — fact (b) must not be tuned to today's `assertion_sites` | `stories/14-1-*.md` | Holds for the COUNT; DN-14-2-1 supplies the TABLE half |
| **DN-3 (Story 14.1)** — a raises-context SUT call is CONSUMED | same | `RESULT_OBSERVING_CONTEXT_CALLEES` is fact (b)'s OWN table, read by name. Adding names to `_ASSERTION_CALLEES` must not disturb it |
| **NFR-P2 — the language conditional stays in `argus/index/`** | `architecture.md` | AC2.5, and §0.7(b) is the argument |
| **AR7 / §3.3 — one derivation, never a fork** | `architecture.md` §Enforcement | One `is_assertion_callee`, one convention predicate. No second answer to "is this an assertion?" |
| **AR8 pure · AR4 `Fraction` never `float` · NFR-D2 deterministic** | `vacuous_test.py` docstring | AC4 |
| **NFR-M1 — ≤1200 lines, every tracked `.py`** | `architecture.md` §Enforcement | §0.9 |
| **A failed measurement is not a reason to amend a threshold** | protocol §5; Story 13.3 / AC5 | AC4.1 |
| **Narrowing a population until it goes green is a defect** | `test_module_size_ceiling.py:35-39` | AC3.1, §0.9 |
| **Full dataflow grounding is Story 6.2's** (`DF-14-1-A`) | 1.5 / 14.1 docstrings | Cite the limit; attempt no dataflow |
| **`AI-E9-8`** — no deferred entry without a named owner | Epic-9 retro | AC6.3, AC8.4 |
| **`AI-E12-10`** — record confirmations, not only divergences | Epic-12 retro | §0's shape, and yours |

### Decisions taken by this story (record each with its rejected alternative)

- **DN-14-3-1 — this story widens ONE table.** `_ASSERTION_CALLEES` only;
  `_CORROBORATION_ASSERTION_CALLEES` is untouched at 23. *Rejected alternative:* widening both, so
  a JS/TS test could reach verdict-eligibility. Rejected **on measurement and on the locked
  asymmetry**: §0.7 shows a JS test cannot reach fact (b) anyway (`_MOCK_CALLEES` is Python-only),
  so the widening would buy no capability while re-opening the exact false-🔴 channel `-115`
  reproduces. Two flat tables partitioned by QUESTION is not a language conditional, so NFR-P2 is
  satisfied by construction rather than by promise.
- **DN-14-3-2 — the shipped vocabulary is the epic's minimum PLUS the names the ratified corpus
  measurably writes, MINUS `match`/`doesNotMatch`.** *Rejected alternative A:* the epic's minimum
  alone — rejected on measurement, it misses the dominant idiom of **both** TypeScript members
  (`toHaveBeenCalled*` in xagents-webapp, `equal`/`deepEqual` in agent-smith; §0.5).
  *Rejected alternative B:* including `match` — rejected because `re.match` and
  `String.prototype.match` are pervasive **non**-assertions in the two languages that matter, and
  while the error direction is flag-reducing (so it cannot accuse anyone falsely), it would
  suppress **real** Python flags. The accepted-collision argument that carries `expect` does not
  carry `match`, and the difference is that `expect` has no common non-assertion meaning.
- **DN-14-3-3 — the Go names ship even though no Go test can be scored today.** `Fatal`, `Fatalf`,
  `Error`, `Errorf`, `NoError`, `Equal` are added and are **measurably inert** (§0.4: 0 flag delta
  on all three members; no Go file is scored at all, `DF-14-3-A`/`-B`). *Rejected alternative:*
  omit them until A and B move together. Rejected because `epics.md` names them, they cost nothing,
  and having them already present removes one reason to re-open this table when A and B eventually
  move — which is precisely the coupling the ledger warns about. **Record them as inert and say
  why**, rather than letting a future reader believe Go was made to work here.
- **DN-14-3-4 — the story's closing target is RE-STATED from the proposal's K&R fixture to the
  Allman-brace fixture.** *Rejected alternative:* discharge `epics.md`'s AC as written against
  `plainfn.test.js`. Rejected **on measurement**: that fixture is no longer flagged (§0.2), so the
  criterion is now **vacuously true** and would be satisfied by a no-op. The epic's intent — *a
  test with a real assertion is never flagged vacuous for being written in TypeScript* — is
  preserved exactly and is now pointed at the shape where it still fails. The original fixture is
  still measured, and its silence is recorded with its real cause.
- **DN-14-3-5 — the collision test is a RULE applied to every name, not a judgement made about
  two.** *(Added by review iteration 2; the full measurement and the per-name reasoning are in
  "Review resolution — iteration 2" and in `vacuous_test.py` beside the table.)* A name is
  admitted when its **measured** Python non-assertion collision is materially below its
  **measured** JS/TS assertion benefit. *Rejected alternative A:* leave DN-14-3-2 as a judgement
  about `match`/`doesNotMatch` — rejected because an exclusion principle applied to one name and
  not to its neighbours is a preference, and it shipped six undecided names. *Rejected
  alternative B:* exclude everything that could conceivably collide — rejected on measurement:
  it would drop `ok` and `equal`, which carry the entire harness of a ratified corpus member
  (2,312 edges), to prevent a recall loss that measures **0** across all three members. The rule
  drops exactly one name, **`Error`**, and reproduces both previously-ratified decisions.

### Files to touch

| Path | Action |
|---|---|
| `argus/detectors/vacuous_test.py` | **UPDATE** — `_ASSERTION_CALLEES` and its comment block only. Do **not** touch `_CORROBORATION_ASSERTION_CALLEES`, `_count_statements`, `_is_test_function`, `_MOCK_CALLEES`, the thresholds or `VacuousTestScore`. 929 lines, headroom 271 |
| `argus/detectors/provenance_scan.py` | **UPDATE, narrowly** — `_ASSIGNMENT_RE` re-anchor + the docstring claim at `:65` (§0.10, `DF-14-2-B`). Nothing else; 14.2 owns this module's logic. 926 lines, headroom 274 |
| `tests/test_vacuous_cross_language.py` | **NEW** — this story's cases (§0.9). Named `UNEVALUABLE` failure for missing grammars, never a skip |
| `tests/test_vacuous_density.py` | **UPDATE** — `-116` re-authored in place (AC5). Nothing else. 1,060 lines, headroom 140 |
| `tests/test_vacuous_detector.py` | **UPDATE, narrowly** — the two `importorskip` lines at `:836-837` only (§0.10, `DF-14-2-A`). ⚠️ **1,128 lines, headroom 72 — add no cases here** |
| `deferred-work.md` | **APPEND ONLY** — the AC6 entry, plus dispositions for the two entries in §0.10. Do not rewrite a line of what is there |
| `stories/14-3-…md` (this file) | **UPDATE** — Dev Agent Record, File List, Change Log |
| `sprint-status.yaml` | **UPDATE** — the `14-3` key only |
| **Everything else** | ⛔ **DO NOT TOUCH.** In particular `argus/pipeline.py`, `argus/index/**`, `argus/verdict/**`, every cartridge under `tests/cartridges/`, `tests/corpus/_manifest.py`, `validation-corpus/**`, `epics.md`, `architecture.md`, `E-PRD/prd.md`, and every file listed in §0.11 |

### Previous story intelligence — traps already paid for

- **The tree has moved TWICE today, and this story's premises were written against neither
  version.** 14.1 and 14.2 both landed on 2026-08-18 and both changed the exact machinery this
  story touches. Two of the premises did not survive (§0.2, §0.4). **Cite §0, never the proposal,
  for any number.** Carrying a proposal figure forward untested is the `DF-8-5-C` defect class.
- **14.2's dev predicted `-109`/`-110` would move; they did not, and `-101`/`-102` moved instead.
  The wrong prediction was recorded AS WRONG and it caught a real misunderstanding.** Do the same:
  §0.8 is your prediction sheet, and being wrong on it is worth more than being silent.
- **`AI-E13-1` — hand off green.** Story 13.3's SM phase wrote a story file, nothing re-ran the
  suite, the commit was pushed, and `audit-ci` went red on ubuntu. Run the full suite **after** your
  last prose edit (AC8.6).
- **Line numbers in this repository drift constantly.** 13.4 found a cite already stale before it
  touched anything, and 14.2's own record shipped four stale line counts that review caught.
  **Locate every block by anchor text**, not by the line numbers in this file, and **re-measure**
  any number you restate.
- **Guards going RED on a full run are usually guards WORKING.** 13.4 hit the `DOCS-001-22` closure
  and did not loosen it. 14.1 hit two dogfood guards and routed them to `AI-E12-11` instead of
  editing an artifact. `-116` going red here is the single expected exception, and it is expected
  because it was *designed* to go red when this story happened.
- **`story_closure_claims` is LINE-SCOPED** (`test_governance_record_integrity.py:58-72`). **Never
  put a `DF-*` id on the same line as `CLOSED`, `Closes` or `closes`** unless `deferred-work.md`
  really carries that disposition. `DOCS-001-78` globs `stories/*.md`, so this file is inside it,
  and it went red twice on 2026-08-17 for exactly this.
- **An empty denominator is `UNEVALUABLE`, never a confirmation** (§0.4 of Story 14.2). Your corpus
  measurement showing "0 corroborated moved" says nothing on its own; the mechanism is the evidence.

### Testing requirements

- **RED-then-green at the real seam.** Every new behaviour is demonstrated from the **real detector
  over the real tree-sitter index**, never from a reconstruction. AC1.1's RED is the keystone.
- **Both directions on every vocabulary row**, on the `-117` pattern: a test whose only assertion is
  a newly-admitted name is no longer flagged, **and** the byte-identical test with that assertion
  removed still is. A one-directional check passes on a change that deleted the capability.
- **Non-vacuity is mandatory.** If a new helper or fixture can return an answer for a reason that
  never occurs, it is decoration. Enumerations carry a `> 0` floor.
- **Brace style is a variable, not an accident.** §0.3 shows the flag depends on it. Cover both K&R
  and Allman explicitly, and assert the K&R case's `statement_count == 0` so the §0.2 mechanism is
  pinned rather than remembered.
- **TypeScript, not only JavaScript** — `.test.ts` and `.spec.ts` fixtures (AC1.4).
- **CRLF and non-ASCII** per AC7.3/AC7.4.
- **Missing optional grammars produce a named `UNEVALUABLE` failure**, never a skip (AC7.5).
- **The full suite is the gate** (§0.8), plus `mypy argus` and `bandit -r argus`, as numbers.

### Project structure notes

- `argus/detectors/*` is a **leaf** package — the import-isolation gate keeps it so. Add no import
  edge out of it (`vacuous_test.py` imports `detectors.base`, `index.ast_index`,
  `ledger.coverage_ledger` and `detectors.provenance_scan`; that is the whole list).
- Modules are `snake_case.py`, ≤1200 lines (NFR-M1). Any split follows the
  `pipeline_stages.py` / `provenance_scan.py` / `test_vacuous_density.py` precedent: a **cohesion**
  boundary, no function split across it, the caller imports back.
- Test ids are `TC-ArgusAgent-<AREA>-<NNN>-<nn>`; new cross-language cases continue the
  `DETECT-001-` series (**`-122` is the highest in use**, `tests/test_vacuous_density.py:1026`).

### References

- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Story 14.3`] — the AC set this story expands; §0.2 and §0.5 record where it is now stale
- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Epic 14`] — the charter, and the ⚠️ note that this epic cannot clear the gate
- [Source: `_bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-08-17b.md#1.3, #2.3, #2.4, #3.3`] — this story's origin. **§1.3's row 2 and §2.3's derivation are both superseded by §0.2 / §0.4**; §3.3's measurement-risk row pre-registered exactly that outcome
- [Source: `_bmad-output/design-artifacts/ArgusAgent/stories/14-2-…md#§0.4, #§0.6, #DN-14-2-1..4, #AC7`] — the split vocabulary, and the hand-off §0.6 wrote for this story
- [Source: `_bmad-output/design-artifacts/ArgusAgent/stories/14-1-…md#DN-3, #DN-4, #§0.5`] — the corroboration decisions and the blast-radius floor
- [Source: `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md#DF-14-3-A, #DF-14-3-B, #DF-14-3-C`] — cited, not fixed (§0.12)
- [Source: `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md#DF-14-2-A, #DF-14-2-B`] — both name this story as their target (§0.10)
- [Source: `_bmad-output/design-artifacts/ArgusAgent/architecture.md#Cross-Cutting #6, #Enforcement`] — the moat, NFR-P2, module-size and dogfood-currency rules
- [Source: `_bmad-output/design-artifacts/ArgusAgent/epic-12-retro-2026-08-15.md#AI-E12-11`] — the pre-authorised dogfood close, predicted unnecessary here
- [Source: `argus/detectors/vacuous_test.py`, `argus/detectors/provenance_scan.py`, `tests/test_vacuous_density.py`] — read at contexting time; every §0 finding was then reproduced by execution

---

## Tasks & Subtasks

- [x] **Task 0 — Re-measure the premise on YOUR baseline (AC: 8.1)**
  - [x] Record `HEAD`. Re-run the three gates; report any divergence from §0.1 as a finding.
  - [x] Confirm `_ASSERTION_CALLEES` is **53** and `_CORROBORATION_ASSERTION_CALLEES` is **23**.
  - [x] Re-measure the flag rate and population for **all three** members at the pinned shas
        (expect 653/3,551 · 295/1,122 · 17/73), so AC3 has before-numbers that are yours.
  - [x] Re-measure the §0.4 funnel: TS function definitions vs those matching `_is_test_function`.
        **Confirm or refute that the TS flag population is ~0** before you build anything on it.
  - [x] **Write your §0.8 guard predictions into the Dev Agent Record NOW, before touching code.**
- [x] **Task 1 — Reproduce the surviving false accusation before you fix it (AC: 1)**
  - [x] Stand up the Allman-brace `.test.js` and `.test.ts` fixtures through the real index; show
        **FLAGGED=True** today. **RED first.**
  - [x] Show the assertion-free counterpart is also flagged, and must stay so.
  - [x] Measure `plainfn.test.js` and record `statement_count == 0` with its cause (§0.2).
- [x] **Task 2 — The vocabulary (AC: 2, 4)**
  - [x] Measure the actual assertion callees of both TS members; compare to §0.5's table.
  - [x] Widen `_ASSERTION_CALLEES` only. Flat, language-agnostic, comment-grouped. Record each
        name's justification and the excluded pair with its reason.
  - [x] Prove the thresholds, `VacuousTestScore` and the frozen table byte-identical by diff.
- [x] **Task 3 — Measure the delta and the moat (AC: 3, 5)**
  - [x] Flags GAINED / LOST per member, before and after, as numbers. Target **0 / 0**.
  - [x] `ast_corroborated` byte-identical across all three members.
  - [x] Run the full suite. Confirm `-116` is the **only** guard that moved; re-author it.
  - [x] Verify `-115` green on **both** arms by execution.
- [x] **Task 4 — The record (AC: 6)**
  - [x] Append the corroboration-limitation entry with its six CC-3 fields, the §0.7 measurement,
        the Epic 15 consequence and a **named owner**.
- [x] **Task 5 — The two entries that name this story (AC: 7.6, 7.7)**
  - [x] `importorskip` → named `UNEVALUABLE` failure in `tests/test_vacuous_detector.py`.
  - [x] `_ASSIGNMENT_RE` re-anchored, with equivalence demonstrated; docstring claim made true.
  - [x] Record both dispositions in the ledger.
- [x] **Task 6 — Platform neutrality (AC: 7)**
  - [x] CRLF regression test on a `.test.ts` fixture; Unicode-safe matching; no `$`-anchored regex;
        `pathlib` + explicit `encoding="utf-8"`; Windows path form to `git -C`.
  - [x] Write the explicit "what could NOT be verified locally" statement.
- [x] **Task 7 — Gates, artifacts, hand-off (AC: 8)**
  - [x] Full suite + `mypy argus` + `bandit -r argus`, as numbers with Δ. **No new skip.**
  - [x] Re-measure module sizes. **No exemption.** Confirm the new module is under the ceiling.
  - [x] Run the dogfood currency guard. **Predicted green** — if it fires, explain before acting.
  - [x] Re-run the full suite **after** your last prose edit.

### Review Findings

Adversarial pass, iteration 1. Every number below was re-derived by direct execution against
the shipped code on this tree (`d339076`), not read from this record. Full baseline reproduced
first: `pytest` 1631 collected / exit 0 / no F or E markers; `mypy argus` Success on 87 files;
`bandit -r argus` 19 Low / 0 Medium / 0 High. `_ASSERTION_CALLEES` = 89, `_CORROBORATION_ASSERTION_CALLEES`
= 23, thresholds byte-identical. AC1's RED-then-green, AC3's per-member GAINED/LOST/fingerprint
identity (0/0 on all three pinned members, re-derived independently over freshly materialized
`git archive` trees of all three shas), AC5's `-116` re-authoring, AC7's `_ASSIGNMENT_RE`/
`_LEADING_CHAIN_RE` equivalence (including the CRLF-only divergence the docstring now correctly
attributes to `$` vs `\Z`), module sizes, and the dogfood LOC-proxy explanation for the wrong P7
prediction all reproduced exactly as recorded — no finding on any of those.

Two issues did not survive adversarial reproduction:

- [x] [Review][Decision] Six of the 36 newly-added `_ASSERTION_CALLEES` names collide with
  ordinary non-assertion Python identifiers, silently un-flagging genuinely vacuous Python
  tests — the story's own DN-14-3-2 exclusion principle, applied inconsistently — [`argus/detectors/vacuous_test.py:355-411`]. DN-14-3-2 excludes `match`/`doesNotMatch` with the
  stated reason *"`expect` has no common non-assertion meaning; `match` does, in both
  languages that matter"*. That same test fails for at least `ok`, `equal`, `Error`, `Equal`
  (all common Python identifiers/constructors — `Error` in particular is a routine custom-exception
  class name) and, less commonly, `throws`/`rejects`. Reproduced by execution: six synthetic
  Python test functions with **zero** real assertions but a same-named local helper/class call
  (`ok("computed")`, `equal(x, 5)`, `Error("bad")`, `Equal(x, 5)`, `throws(fn)`,
  `rejects(x)`) score `heuristically_vacuous=False` on the current table; the identical fixtures
  score `heuristically_vacuous=True` (correct) when scored against the pre-14.3 53-name table.
  The error direction is flag-reducing only (never manufactures a false 🔴, consistent with the
  locked asymmetry) and the ratified-corpus measurement (0 lost across 4,746 real test functions
  in all three pinned members, and 0 hits for these six names in `tests/cartridges/`) is
  unaffected — this is a latent risk on Python code outside the three sampled corpora, not a
  live regression in anything currently shipped or measured. It needs a human call, mirroring how
  `match`/`doesNotMatch` was resolved: either exclude `ok`/`equal`/`Error`/`Equal` (and decide
  `throws`/`rejects`) with the same recorded reason, or explicitly accept and record the cost
  for each one (AC2.6 already drafts this language for `expect`/`ok` in the story's own AC text
  but it is not present as a code comment or an executable non-vacuity check the way the
  naming-convention's collision cost is, at `vacuous_test.py:425-431`).

- [x] [Review][Patch] `TC-ArgusAgent-DETECT-001-131` does not exercise the mechanism its
  docstring and `DF-14-3-D` claim it demonstrates, because the widened table it is itself
  testing short-circuits it first — [`tests/test_vacuous_cross_language.py:624-674`]. `_ast_corroborated`
  returns `False` immediately when `heuristically_vacuous` is `False` (`vacuous_test.py:1025-1026`),
  before `provenance_evidence` is ever called. Reproduced by execution: the shipped `-131` fixture
  scores `assertion_sites=2`, `statement_count=1` (Allman JS/TS bodies collapse to exactly one
  logical statement under 14.2's bracket-continuation scanner, regardless of real body size — a
  pre-existing, out-of-scope property of `body_statement_count` this story is the first to
  build a claim on top of), `assertion_density=2` — well above the floor — so
  `heuristically_vacuous=False` and `ast_corroborated=False` follows trivially, never reaching
  the `_MOCK_CALLEES`/fact-(b) structural barrier the test claims to pin. Reshaping the same
  fixture to clear `mock_ratio > MOCK_RATIO_CEILING` instead (3 mock constructions against 2
  non-mock calls, e.g. `compute()` + three `Mock()` bindings + one bare `assertEquals(...)`)
  DOES reach `heuristically_vacuous=True` and DOES then call `provenance_evidence`, which
  reproduces `ast_corroborated=False` for the mechanism actually claimed — so the underlying
  `DF-14-3-D` conclusion holds, it is just not the thing the shipped guard tests. Separately,
  the exact `provenance_evidence` figures the shipped `-131` fixture reproduces are `frozen:
  sut=4 discarded=False mock_ref_asserts=0` (matches the ledger's cited *"sut=4"* for the FROZEN
  table) but `widened (one-table hypothetical): sut=2` (the ledger and §0.7(c) both cite
  *"sut=3"* for this arm) — the CORROBORATED=False conclusion is unaffected, but the specific
  number does not reproduce against the fixture that shipped, and should be corrected or
  re-derived against a named fixture in `deferred-work.md`'s `DF-14-3-D` entry and this story's
  §0.7(c). Fix: give `-131` a non-vacuity floor (`assert score.heuristically_vacuous is True`
  before asserting `ast_corroborated`, mirroring the pattern `-115` already uses at
  `test_vacuous_density.py:482`) and reshape the fixture (or add a companion case) so the
  assertion genuinely exercises `provenance_evidence`, then correct the `sut=3`/`sut=4` figures
  against whichever fixture is actually pinned.

### Review resolution — iteration 2 (2026-08-18)

**Both High findings resolved. Neither was argued away.** Every figure below was produced by
execution on this tree; the review's own reproductions were confirmed, not restated.

**FINDING 1 — the collision rule, now applied to every name (`DN-14-3-5`).** The review is
right and its framing is the important part: the defect was not six names, it was that
`DN-14-3-2`'s test was applied to `match`/`doesNotMatch` and to nothing else. So the answer is
a rule, measured, applied uniformly, and shown to reproduce the two decisions already ratified.

Python collisions were counted with the **stdlib `ast` module** — deliberately not with Argus's
own index, because deriving a collision argument from the thing under test is circular — over
**4,046 independent Python files**: the three pinned corpus members, Argus itself, this
environment's `site-packages`, and the CPython 3.11 standard library. JS/TS benefits are call
edges emitted by the shipped index over the staged test files of the two ratified TypeScript
members at their pinned shas.

| name | py collisions | js/ts benefit | benefit/cost | decision |
|---|---|---|---|---|
| `match` | **706** | 476 | 0.7× | ⛔ excluded — *already ratified; the rule reproduces it* |
| **`Error`** | **164** | **0** | 0× | ⛔ **DROPPED, new this round** |
| `equal` | 34 | 1,548 | 45× | ✅ admitted, cost recorded |
| `expect` | 29 | 6,876 | 237× | ✅ admitted — *already ratified; the rule reproduces it* |
| `ok` | 10 | 764 | 76× | ✅ admitted, cost recorded |
| `throws` | 0 | 19 | — | ✅ admitted, no collision found |
| `rejects` | 0 | 1 | — | ✅ admitted, no collision found |
| `Equal` | 0 | 0 | — | ✅ admitted, inert (`DN-14-3-3`) |

⛔ **The rule is not fitted to a conclusion, and that is the only reason to trust it:** it
excludes `match` and admits `expect` by the same arithmetic that decides the six.

Per name, on the merits:

- **`Error` — DROPPED.** The clearest case in the table. **164** measured Python call sites:
  CPython's own `wave`, `aifc` and `sunau` each define `class Error(Exception)` and call it, and
  mypy's `stubtest` yields `Error(...)` records. Against a benefit measured at **exactly zero** —
  Go's `t.Error` is unreachable by *two independent* barriers (`DF-14-3-A` never scores a Go
  test; `DF-14-3-B` never emits a selector-expression call), and in JS/TS `throw new Error(...)`
  is the standard **non**-assertion idiom, so it collides in the other language too. It costs the
  most of any candidate and buys nothing. Its absence breaks the Go family's symmetry
  deliberately; `-133` holds it out so nobody tidies it back.
- **`ok` — KEPT, cost recorded and made executable.** The collision is real and is not
  hand-waved: `env.ok(...)` is a **result constructor** in agent-smith's production surface (9
  sites), plus `self.frame.ok()` in `site-packages`. Ten sites against **764** JS edges. It
  carries half of `node:assert`.
- **`equal` — KEPT, cost recorded and made executable.** The collision shape is the *worst* of
  the admitted names and it is stated rather than minimised: `jsonschema._utils.equal(a, b)` is a
  **boolean-returning comparison predicate** (33 sites), and a Python test whose body is
  `equal(compute(x), 5)` with no `assert` is *precisely* the vacuous shape this detector exists
  to flag. It is accepted anyway at 45×, because `equal` is the single most-written name in a
  ratified member's entire harness (**1,548** edges) and dropping it re-opens, for that member's
  dominant idiom, the exact false accusation this story exists to close.
- **`throws` / `rejects` — KEPT, and argued from measurement rather than intuition, as the
  review required.** **Zero** collisions across all 4,046 Python files, in either the bare
  `throws(...)` or the attribute `x.throws(...)` form. That is not an accident of sampling:
  Python's word for this is `raises`, and `throws`/`rejects` are Java/JS spellings. Benefit is
  small but real and measured (19 and 1 edges of `node:assert` core).
- **`Equal` — KEPT.** Zero collisions and zero benefit; it is inert for the same two structural
  reasons as `Error`, but unlike `Error` it costs nothing, so `DN-14-3-3`'s ratified trade
  (ship the Go family so nobody re-opens this table when `A`/`B` finally move) still carries it.

⚠️ **The rule disagrees with the project on exactly one name, and that is recorded rather than
bent.** `doesNotMatch` measures 0 collisions against 76 edges, so `DN-14-3-5` would admit it;
AC2.3 excludes it by name. **The project standard wins** — it is `match`'s negation and would
read as `match` being half-admitted — and the tradeoff is written into the code beside the rule.

**Containment, verified and not used as an excuse.** `_CORROBORATION_ASSERTION_CALLEES` is
byte-unchanged at 23 (confirmed by diff), so nothing here can reach verdict-eligibility; that is
why the finding is High and not Critical, and `-133` asserts it rather than assuming it.

**RED-first, by execution.** `-133` was written first and run against the shipped table with
`git checkout -- argus/detectors/vacuous_test.py` in place: **FAILED**, `assertion_sites=1`,
`heuristically_vacuous=False` — a Python test with no assertion at all going unflagged. Green
after the drop, with the same fixture.

**Re-measured after (AC3, in full):**

| Member | scored | flagged before | flagged after | GAINED | LOST | fingerprint set |
|---|---|---|---|---|---|---|
| minions @`ec63b729` | 3,551 | 653 | 653 | **0** | **0** | **byte-identical** |
| agent-smith @`9ab774d7` | 1,122 | 295 | 295 | **0** | **0** | **byte-identical** |
| xagents-webapp @`33a86525` | 73 | 17 | 17 | **0** | **0** | **byte-identical** |

Compared as sorted `file::name@line` fingerprints, not as totals. **No member's flag set moved,
so there is no delta to report** — and the mechanism is measured, not assumed: none of the six
names occurs as a callee in any of the 4,746 scored test functions. Cartridge recall is
unchanged (`tests/cartridges/` carries none of the six; the cartridge and precision-replay
suites are green).

**FINDING 2 — the guard was itself a vacuous test, and the sweep found a second one.**
Confirmed by execution before anything was changed: the shipped `-131` fixture scores
`assertion_sites=2 statement_count=1 density=2`, therefore `heuristically_vacuous=False`,
therefore `_ast_corroborated` returns at `if not heuristically_vacuous: return False` — the case
asserted a `False` it was always going to get, and `provenance_evidence` was never called. The
irony is taken at face value: this was a vacuous test inside the vacuous-test detector's own
suite, in the epic built to stop exactly that, and it is the strongest argument for AC1 there is.

Fixed as required, and one step further:

1. **Non-vacuity floor** — `-131` now asserts `heuristically_vacuous is True` *before* it asserts
   anything about corroboration, mirroring `-115`'s own floor, with a failure message that says
   to reshape the FIXTURE rather than weaken the assertion.
2. **Fixture reshaped to reach the predicate through `mock_ratio`** — the half this story did
   *not* widen. Four `Mock()` bindings against a `compute()` and an `expect(...).toHaveBeenCalled()`:
   `mock_ratio = 4/7 > 1/2`. The strict `>` is asserted explicitly, because the review is right
   that a fixture sitting exactly ON the boundary fires nothing. The second short-circuit
   (`if not reaches_sut`) is floored too.
3. **The mechanism is now asserted directly rather than inferred from a `False`.**
   `_mock_bound_names` is run over the JavaScript source and over the identical Python binding:
   `const fake = Mock();` binds **nothing**, `fake = Mock()` binds **`fake`**. *That* is what
   "fact (b)'s assignment machinery is Python-syntax-shaped" means, and it is now measured. Both
   fact-(b) clauses are asserted under **both** vocabularies.
4. **Figures corrected** in `deferred-work.md` and §0.7(c) above, named to a fixture, with the
   undefined field (`consumed_sut_calls`) spelled out and the wrong number left visible.
5. **The sweep over `-123`..`-132`, which the review called the highest-value work — and it
   found a second instance.** `-132` concluded "nothing was scored" from `scored == []` and
   `findings == ()`, both of which are *also* exactly what an unparsed file produces: it would
   have gone on passing if the Go or JavaScript grammar disappeared. It now proves each fixture
   parsed, asserts the definitions extracted, asserts the degrade REASON is `no_test_functions`,
   and measures `DF-14-3-B` live (`Fatalf` is absent from the Go edge set) instead of quoting it
   from the ledger. `-124` gained the same treatment on its end-to-end arm (`findings == ()` is
   what a *degraded* run returns). `-123`, `-125`, `-126`, `-127`, `-128`, `-129`, `-130` were
   each re-checked against the same question and already carried a floor — recorded as
   confirmations, not silently passed over (`AI-E12-10`).

### Code review — gate verification, iteration 2 (2026-08-18)

**✅ Clean review — no unresolved `decision-needed` or `patch` findings.** Both High findings from
iteration 1 were re-verified as genuinely closed, not merely re-argued. Every load-bearing number
below was independently re-derived by execution against the diff `d339076..d563fa9` (`cce9897`
code, `d563fa9` artifacts) and the working tree — none of it was taken from the story's own prose.

**Full suite, independently re-run:** `1632 passed, 0 failed, 0 skipped`, exit 0 (`python -m
pytest`, no duplicated `-q`; the story's own `-q` invocation elsewhere in this record is silent on
the final summary line only because `-ra -q` from `pyproject.toml` plus an explicit `-q` on the
command line is `-qq`, which pytest suppresses the summary line at — a harness quirk, not a repo
defect, confirmed by re-running without the duplicate flag). `_ASSERTION_CALLEES` = **88**,
`_CORROBORATION_ASSERTION_CALLEES` = **23**, `Error`/`match`/`doesNotMatch` absent,
`ok`/`equal`/`Equal`/`throws`/`rejects`/`expect` present — all confirmed by import, not by prose.

**DN-14-3-5's collision table — reproduced independently, digit for digit, on a from-scratch
harness.** Built the exact stated population (three pinned corpus members via `git archive` at
their pinned shas, this repo's git-tracked `.py` files, this venv's `site-packages`, this
interpreter's stdlib) and confirmed it sums to **exactly 4,046 files**, matching the story's
population size before a single collision was counted. Then counted `ast.Call` sites for every
candidate name over that population with a from-scratch script (not Argus's index, per the story's
own anti-circularity constraint):

| name | story's count | independently reproduced |
|---|---|---|
| `Error` | 164 | **164** ✅ exact |
| `match` | 706 | **706** ✅ exact |
| `expect` | 29 | **29** ✅ exact |
| `ok` | 10 | **10** ✅ exact |
| `equal` | 34 | **34** ✅ exact |
| `Equal` | 0 | **0** ✅ exact |
| `throws` | 0 | **0** ✅ exact |
| `rejects` | 0 | **0** ✅ exact |
| `doesNotMatch` | 0 | **0** ✅ exact |

Every single collision figure in the table reproduced exactly. The JS/TS benefit side was
re-derived from the shipped index over freshly `git archive`d copies of the same two members
(slightly fewer files matched my glob than the dev's — 86/265 vs the story's 88/279 — so raw call
totals differ by ~1% where volumes are large) but the combined and small-volume figures matched
exactly: `match` 469+7=**476** (story: 476), `doesNotMatch` 76+0=**76** (story: 76), `equal`
**1548** (story: 1548), `deepEqual` **506** (story: 506), `toHaveBeenCalledWith` **696** (story:
696), `throws` **19** (story: 19), `rejects` **1** (story: 1). This is not post-hoc rationalization
— the rule really does reproduce both previously-ratified decisions (`match` excluded, `expect`
admitted) by the same arithmetic that decides the six.

**The RED-first claim for `-133`, reproduced exactly.** Loaded iteration-1's shipped
`vacuous_test.py` (`git show d339076:...`, table size 89, `Error` present) and scored the
`Error("bad")` collision fixture against it directly: `assertion_sites=1,
heuristically_vacuous=False` — a genuinely assertion-free Python test going unflagged, matching the
story's claimed RED exactly. Against the current (iteration-2) table: `assertion_sites=0,
heuristically_vacuous=True` — correctly flagged.

**`-131`'s non-vacuity floor is load-bearing, confirmed by mutation rather than by reading the
assertion.** Scored iteration-1's original (weaker) fixture — a single `Mock()` binding instead of
four — against the *current* detector: `mock_ratio=1/5, heuristically_vacuous=False`. The new
floor (`assert score.heuristically_vacuous is True`) would fail on it. That is direct proof the
floor is not decoration: the exact defect iteration 1 shipped (a guard whose fixture never reaches
`_ast_corroborated`'s real branch) is caught by the floor that was added to fix it. The reshaped
fixture itself scores `mock_ratio=4/7 > 1/2, heuristically_vacuous=True`, reaching
`provenance_evidence` for real, and the corrected `consumed_sut_calls` figures
(`frozen=3, one-table=1`) were independently re-derived and matched the corrected
`deferred-work.md` entry exactly, with the original wrong `sut=3`/`sut=4` figures still legible.

**The `-123`..`-133` sweep, checked case by case.** Read every case in
`tests/test_vacuous_cross_language.py`: `-123`/`-124`/`-126`/`-128`/`-129` each assert
`statement_count > 0` or an equivalent reachability floor before trusting a negative result;
`-124`'s end-to-end arm additionally asserts `result.degraded == () and result.entries`; `-125`
directly asserts the mechanism (`statement_count == 0`) rather than inferring it from silence, so
it needs no floor; `-127` inspects the frozensets directly and carries its own non-vacuity
(`len(_ASSERTION_CALLEES) >= 88`, membership assertions); `-130` carries positive AND negative
controls after the story's own account of catching its first version over-matching; `-131` is
covered above; `-132` now asserts `entry.ast_eligible and not entry.parse_failed` plus the exact
extracted definitions and edges for both the Go and callback fixtures before trusting their
silence, and separately measures `"Fatalf" not in {edge callees}` live rather than citing
`DF-14-3-B` from the ledger. No case in the swept range concludes a mechanism from an
unfloored negative.

**Standing constraints, spot-checked by execution, not by re-reading the record:**
`argus/pipeline.py` untouched at exactly 1,111 lines and absent from the `d339076..d563fa9` diff;
`ASSERTION_DENSITY_FLOOR`/`MOCK_RATIO_CEILING` byte-unchanged (`Fraction(1,4)`/`Fraction(1,2)`);
`VacuousTestScore` still `ConfigDict(frozen=True, extra="forbid")`; no `pytest.skip` /
`importorskip` call sites anywhere in the touched test files (only prose explaining why they were
removed); the dogfood proof artifact's own committed figures read `29483` LOC / `435/29483` for
NFR-C1 — the numerator is exactly what the story claims stayed put; `deferred-work.md`'s working-
tree diff against `d339076` contains **zero removed lines** — genuinely append-only, confirmed by
`git diff | grep -c '^-[^-]'` returning 0. `DF-14-3-H` (the 39-line-headroom deferral) carries a
real owner (`XAgent007 (Engineering Lead)`) and a real `target_story: 13-5`, and the judgement to
defer the split rather than do it inside a two-High-finding fix round is sound: splitting ~35
guards out of the tightest module in the repo is itself a regression-risk-bearing change, and doing
it under this round's budget would trade a known risk (an unsplit-but-green module) for an unknown
one (a silently dropped case in the split). Accepted, not a finding.

No decision-needed, patch, or unresolved High/Medium finding remains. Nothing was deferred by this
review round (both of iteration 1's findings are closed; `DF-14-3-G`/`DF-14-3-H` were filed by the
dev, not by this review, and are judged sound above rather than re-filed).

---

## Dev Agent Record

### Agent Model Used

`claude-opus-5[1m]` (BMAD `dev-story` worker, single pass, 2026-08-18).

### Guard predictions (write these BEFORE measuring — §0.8)

**Written before a single line of `argus/` was edited**, immediately after Task 0's measurement
and before Task 1's fixtures existed. Recorded here so a wrong one is visible as wrong, on the
precedent 14.2's dev set when they predicted `-109`/`-110` would move and `-101`/`-102` did.

| # | Guard | My prediction | Reasoning I committed to in advance | Outcome |
|---|---|---|---|---|
| P1 | `TC-ArgusAgent-DETECT-001-116` | ⚠️ **RED** | Its `cross_language` literal asserts `not (cross_language & _ASSERTION_CALLEES)` over 12 names, **10 of which** I intend to add. It is 14.2's *"14.3 has not happened yet"* assertion and this story is what falsifies it | ✅ **RIGHT** — RED, and the only one |
| P2 | `TC-ArgusAgent-DETECT-001-115` | 🟢 green, **both arms** | Its fixture's callees are `compute`/`Mock`/`calculate`/`assert_called_once_with`; none is a candidate name, so neither `widened_sut` nor `mock_referencing_assertions` can move | ✅ RIGHT |
| P3 | `TC-ArgusAgent-DETECT-001-117` | 🟢 green | Both-directions vocabulary guard over Python `unittest.mock` / `pytest.raises` / `assert_*` fixtures — disjoint from the cross-language additions | ✅ RIGHT |
| P4 | `-87`, `-88`, `-89`..`-93`, `-101`..`-108`, `-109`..`-112` | 🟢 green | All Python fixtures; §0.8 measured that no candidate name appears in any of them. `-88` is the one whose movement would mean the fix broke the moat it protects | ✅ RIGHT |
| P5 | `TC-ArgusAgent-VERDICT-001-30` (both arms), `-116`, `-117` | 🟢 green | End-to-end verdict path; the widening is flag-**reducing** on the density half only and cannot reach fact (b) at all (DN-14-2-1) | ✅ RIGHT |
| P6 | `-113`, `-114`, `-118`..`-122` | 🟢 green | 14.2's denominator guards; I touch no denominator code | ✅ RIGHT |
| P7 | dogfood currency (`test_dogfood_plan/proof/artifact_currency`) | 🟢 green — **`AI-E12-11` NOT needed** | §0.8's reversal of the usual expectation: predicted 0 flags moved over Argus's own 1,777 test functions | ❌ **WRONG — see below** |
| P8 | `test_module_size_ceiling.py` | 🟢 green | New cases go to a NEW module; `vacuous_test.py` has 271 lines of headroom | ✅ RIGHT |
| P9 | `TC-ArgusAgent-DOCS-001-78` | 🟢 green, **conditional on my own prose** | It lints this file. It goes red if I write a `DF-*` id on a closure-verb line the ledger does not back — so my two `CLOSED` dispositions must land in `deferred-work.md` **first** | ✅ RIGHT (held after the ledger append) |
| P10 | `test_pipeline_signature_demo`, `test_cartridge_selfaudit`, `test_precision_replay` | 🟢 green | Detector-output-dependent, predicted unchanged for the same measured reason as P7 | ✅ RIGHT |

⛔ **P7 IS RECORDED AS WRONG, AND IT CAUGHT A REAL MISUNDERSTANDING.** The dogfood artifacts DID
move, and the story predicted they would not. **This is a finding, and it is explained before it
was discharged** — see "The P7 finding" in the Debug Log. Predicting it green was reasonable from
§0.8's stated measurement and it was still wrong; the mechanism §0.8 did not model is that Argus's
own test tree contains Python tests whose **only** assertion is a name this story newly admits.

### Task 0 — the premise, re-measured on MY baseline

`HEAD` = `e2e278c` (`e2e278cffa0c9f1d527e6fdee444b2995041c223`), matching §0's contexting base.

| Premise (§0) | My re-measurement | |
|---|---|---|
| `pytest` → 1621 / 0 failed / 0 skipped, exit 0 | **1621 passed, 0 failed, 0 skipped, exit 0** | ✅ |
| `mypy argus` → Success, 87 source files | **Success: no issues found in 87 source files** | ✅ |
| `bandit -r argus` → 19 Low / 0 Med / 0 High | **19 Low / 0 Medium / 0 High** | ✅ |
| `_ASSERTION_CALLEES` = **53** (not the story's headline 23) | **53** | ✅ |
| `_CORROBORATION_ASSERTION_CALLEES` = 23 | **23** | ✅ |
| `ASSERTION_DENSITY_FLOOR` `1/4` · `MOCK_RATIO_CEILING` `1/2` | **`1/4` · `1/2`** | ✅ |
| minions 3,551 scored / 653 flagged (18.4%) | **3,551 / 653 — 18.4%** | ✅ exact |
| agent-smith 1,122 scored / 295 flagged (26.3%) | **1,122 / 295 — 26.3%** | ✅ exact |
| xagents-webapp 73 scored (72 `.py` + 1 `.ts`) / 17 flagged | **73 (72 `.py`, 1 `.ts`) / 17 — 23.3%** | ✅ exact |
| corroborated, any member | **0 / 0 / 0** | ✅ |
| Module sizes 929 · 926 · 1,060 · 1,128 · 1,111 | **929 · 926 · 1,060 · 1,128 · 1,111** | ✅ exact |

**The §0.4 funnel, re-measured and CONFIRMED — the refuted prediction is refuted on my baseline too:**

| | agent-smith | xagents-webapp |
|---|---|---|
| TS/JS test files staged | **88** | **279** |
| AST-eligible | **88** | **277** (2 not eligible) |
| `function` definitions extracted | **169** | **410** |
| …matching `_is_test_function` (case-sensitive) | **0** | **1** |
| …case-INsensitive | **0** | **1** |
| TS test functions scored / flagged | **0 / 0** | **1 / 0** |

⛔ **I confirm §0.4 rather than inheriting it: the TS flag population is ~0 BEFORE I build anything
on it.** minions stages **0** TS/JS test files at all.

**One §0 fact did NOT survive, and it is a path, not a number.** §0.1's clone table gives
xagents-webapp as `D:/ProjectX/XAgents/XAgents-WebApp`; `git -C` there fails **exit 128** (no
repository). The real clone is `D:/ProjectX/XAgents/XAgents/XAgents-WebApp` — one level deeper,
the same nesting the ledger already records for agent-smith. The **sha is reachable and unchanged**
(`git cat-file -t 33a86525` → `commit`), so every §0.4 figure stands; only the story's path
literal was stale. Recorded rather than silently corrected, per `AI-E12-10`.

### Debug Log

#### Task 1 — the RED, demonstrated before the fix (AC1)

Reproduced through the **real** tree-sitter JS/TS grammars and the **real** `VacuousTestDetector`,
on the unmodified tree, before `_ASSERTION_CALLEES` was touched:

```
BEFORE (shipped 53-name table)
  allman.test.js  testAllman   asserts=0 stmts=1 density=0  FLAGGED=True   <- THE FALSE ACCUSATION
  allman.test.ts  testAllman   asserts=0 stmts=1 density=0  FLAGGED=True   <- and in TypeScript
  empty.test.js   testNothing  asserts=0 stmts=1 density=0  FLAGGED=True   <- correct, must STAY
  plainfn.test.js testAdds     asserts=0 stmts=0 density=0  FLAGGED=False  <- §0.2, statement_count==0

AFTER (widened table)
  allman.test.js  testAllman   asserts=2 stmts=1 density=2   FLAGGED=False  ✅ closed
  allman.test.ts  testAllman   asserts=2 stmts=1 density=2   FLAGGED=False  ✅ closed
  empty.test.js   testNothing  asserts=0 stmts=1 density=0   FLAGGED=True   ✅ signal preserved
  plainfn.test.js testAdds     asserts=2 stmts=0 density=0   FLAGGED=False  — unflagged for the SAME
                                                                              reason as before
```

§0.3 is reproduced exactly, including the brace-style dependence: the K&R fixture scores
`statement_count == 0` and is therefore unflagged **by the §0.2 mechanism, not by this story**.
That is asserted in the new module rather than remembered, so the day the denominator changes
again the reason is pinned.

#### The P7 finding — the dogfood prediction was wrong, and the mechanism is NOT the obvious one

§0.8 predicted the currency guards would not fire and told me to treat a firing one as a **finding**
rather than a routine regeneration. **Two fired** —
`test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation`
and `test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run`.

⚠️ **My first hypothesis was wrong and I am recording it as wrong.** I assumed the artifacts moved
because the widened vocabulary un-flagged Python tests in Argus's own tree. **It did not.** The
mechanism was established by diffing the regenerated artifacts *before* committing them, and the
entire delta is three lines:

```
commit descriptor   2eeaace -> e252043     (the artifacts cite `git rev-parse HEAD` at generation)
total physical LOC    29270 -> 29411       (+141)
partition 3 LOC       14669 -> 14810       (+141)
```

…plus the bundle content hash, which folds the two figures above. **`+141` is exactly
`vacuous_test.py` (+112) plus `provenance_scan.py` (+29)** — verified by `git show e2e278c:<path>`
against the working tree. **No finding count, no flag count and no audit-cost figure moved:** the
NFR-C1 ratio went `87/5854` → `435/29411`, and those share the numerator `435` (`87/5854` is the
same fraction reduced) — only the **denominator** changed.

**So §0.8's measurement was RIGHT and its inference was WRONG.** 0 flags do move over Argus's own
1,777 test functions. But the dogfood artifacts are not solely detector-derived: they record the
**build-cost proxy** — total physical LOC over tracked `argus/` — and the generating commit sha. A
**comment-only** commit to `argus/` would have moved them just as much. The prediction confused
*"the detector's output does not change"* with *"the artifacts do not change"*, and that distinction
is worth more than the regeneration was.

Discharged through `AI-E12-11`'s pre-authorised sequence: commit the `argus/` delta (`e252043`) →
`python scripts/regenerate_dogfood_artifacts.py` → commit the three artifacts **separately**
(`d339076`). **No artifact was hand-edited and no assertion was loosened** (`DF-8-5-B`).

#### What could NOT be verified locally (AC7.8) — CI evidence is NOT ESTABLISHED

Every gate below was run on **Windows 11 / CPython 3.11 only**. `audit-ci.yml` runs an ubuntu
matrix; this repository has already shipped POSIX-only bugs out of a green Windows run
(`AI-E13-1`), so these are reasoned-about, **not executed**:

1. **`ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` on ubuntu.** ⚠️ **A STALE PREMISE, corrected:** AC7.5
   describes `tree-sitter-javascript` / `tree-sitter-typescript` as *optional `[languages]`
   extras*. **They are not, and have not been since Story 12.5** — `pyproject.toml` promoted all
   ten grammars to **BASE** dependencies and retains `[languages]` only as a
   backward-compatibility alias, pinned equal to them by `TC-ArgusAgent-DOCS-001-61`. That makes
   the `UNEVALUABLE` treatment more clearly right, not less. Both packages are installed locally,
   so the failing branch of `_grammars_or_unevaluable` **never executed on this machine**; only
   the shape of its message did. Whether an ubuntu runner could ever lack them is NOT ESTABLISHED
   by anything I ran.
2. **The same for `DF-14-2-A`'s replacement** in `test_vacuous_detector.py`: the two
   `importorskip` calls are gone, but the failure they now produce instead of a skip was only
   exercised through the synthetic control, never by an actually-missing grammar.
3. **Line terminators.** The CRLF case is asserted locally on a `.test.ts` fixture written with
   explicit `\r\n` and compared byte-for-byte against its LF twin, but git's `core.autocrlf`
   behaviour on the ubuntu checkout is NOT ESTABLISHED.
4. **Path separators.** All changed code is `pathlib`-only with explicit `encoding="utf-8"`; no
   POSIX run confirms it. The corpus harness that produced every AC3 number is a scratch script,
   not tracked, and passes `git -C` the Windows path form — it is not part of the suite.
5. **Filesystem case-sensitivity.** `_is_test_function` is untouched, but ubuntu's case-sensitive
   filesystem could in principle stage a differently-cased fixture path; not exercised.

**All gate numbers in this record are LOCAL.**

#### Review iteration 2 — what could NOT be verified locally (AC7.8), the delta

The five limits above still stand verbatim. Iteration 2 adds three of its own, and they are
named rather than folded into a general disclaimer:

6. **The collision measurement is a scratch harness, not a tracked tool.** The 4,046-file
   `ast` sweep that produced every number in `DN-14-3-5` is not part of the suite and cannot be
   re-run by CI. It is reproducible only by rebuilding it — which is precisely why the residual
   is filed with a named owner rather than declared closed.
7. **The Python population is this machine's.** `site-packages` is this environment's dependency
   closure and the standard library is CPython 3.11 on Windows; a different interpreter or a
   different dependency set would produce different collision counts. The **direction** of every
   decision is robust to that (164 vs 0 for `Error`; 0 in either form for `throws`/`rejects`),
   but the exact integers are environment-scoped and must not be quoted as universal.
8. **The reshaped `-131` fixture's `mock_ratio` was measured on this tree only.** It sits at
   `4/7` against a strict `> 1/2` ceiling; that margin is asserted in the case itself, so a
   denominator change on ubuntu would fail loudly rather than hollow the guard out silently —
   but no POSIX run has executed it. *CI evidence is NOT ESTABLISHED.*

### Completion Notes

**What shipped.** ONE table widened: `_ASSERTION_CALLEES`, the density numerator, **53 → 89**
names. `_CORROBORATION_ASSERTION_CALLEES` is byte-unchanged at 23, the thresholds are
byte-unchanged, and `argus/pipeline.py`, `_count_statements`, `logical_statement_count`,
`body_statement_count`, `_is_test_function` and `_MOCK_CALLEES` were not touched.

**AC1 — the RED came first.** The Allman-brace fixture was measured `asserts=0 stmts=1 density=0
FLAGGED=True` through the real tree-sitter index and the real detector **on the unmodified tree**,
in JavaScript and in TypeScript, with `expect`/`toBe` provably present in the edge set the whole
time — so the diagnosis is a VOCABULARY gap, not a parsing failure. After: `asserts=2 FLAGGED=False`.
The byte-identical assertion-free twin stays `FLAGGED=True`. The RED is not merely recorded here —
`-123`/`-124`/`-126` recompute the pre-14.3 numerator **on every run**, so the defect is
re-demonstrated by execution rather than remembered.

**AC1.3 / DN-14-3-4 — the epic's criterion was NOT discharged against the fixture it names.**
`plainfn.test.js` scores `statement_count == 0` and is unflagged for 14.2's denominator reason, not
this story's fix. `-125` pins that mechanism and asserts the two fixtures differ **only** in brace
placement, so the vacuously-true criterion cannot be mistaken for evidence.

**AC3 — measured, per member, before and after:**

| Member | scored | flagged BEFORE | flagged AFTER | **GAINED** | **LOST** | corroborated |
|---|---|---|---|---|---|---|
| minions @`ec63b729` | 3,551 | 653 (18.4%) | 653 (18.4%) | **0** | **0** | 0 → 0 |
| agent-smith @`9ab774d7` | 1,122 | 295 (26.3%) | 295 (26.3%) | **0** | **0** | 0 → 0 |
| xagents-webapp @`33a86525` | 73 | 17 (23.3%) | 17 (23.3%) | **0** | **0** | 0 → 0 |

Stronger than the counts: the flagged **SETS** are byte-identical, compared as sorted
`file::name@line` fingerprints, so 0/0 is a real identity and not two equal totals hiding a swap.
§0.4's refuted corpus prediction **reproduces on my baseline with a LARGER vocabulary than the one
§0.4 tested** — which also means not one of the 36 added names removes a single real Python flag
across 4,746 test functions. That is the measured backing for keeping `match`/`doesNotMatch` out:
the names that are safe are demonstrably safe, and those two were not tested because they were not
shipped.

`ast_corroborated` is 0 across all three members before and after. ⚠️ **On its own that is an EMPTY
DENOMINATOR — `UNEVALUABLE`, not a confirmation** (14.2 §0.4). The evidence that corroboration
cannot move is the MECHANISM: the corroboration path reads the frozen table by name (DN-14-2-1),
proven green on both arms of `-115` and end-to-end by `-131`.

**AC5 — `-116` re-authored, not nudged.** Predicted RED before the suite ran (P1), and verified
red-by-construction: all **12** names in its `cross_language` literal now intersect the widened
table, so the original arm would fail. The literal is **byte-identical**; only the expectation was
inverted, from `not (cross_language & widened)` to `cross_language <= widened`, plus a new arm
asserting the frozen table still contains none of them. Deleting the arm was rejected: it would
have left the moat unwatched from that direction. Its other three arms are unchanged. **`-116` was
the ONLY guard that moved**, exactly as predicted.

**AC6 — `DF-14-3-D` filed** with six CC-3 fields and a named owner, carrying the §0.7 measurement
and the Epic 15 consequence (a TypeScript bench member can contribute advisory findings only, never
a data point for the ≥80% precision gate) and `target_story: 15-1-…`.

**AC7.6/7.7 — both inherited entries discharged, and one found a defect they did not name.**
`DF-14-2-A`'s `importorskip` became a named `UNEVALUABLE` failure. `DF-14-2-B`'s `_ASSIGNMENT_RE`
was re-anchored with the equivalence **demonstrated** — 218,017 corpus lines, 25,649 assignment
matches, **0 disagreements**. ⚠️ The sweep I wrote to make the docstring claim checkable (`-130`)
immediately found a **second** `^` anchor, `_LEADING_CHAIN_RE`, which the ledger entry never named
and which reading the entry would have left in place.

**Non-vacuity, deliberately.** `-123` asserts `statement_count > 0` before trusting any "not
flagged" result, because the §0.2 silence would otherwise satisfy it for free; `-130` asserts ≥4
patterns were extracted and carries four positive controls, two of which exist because my **first**
version of that predicate reported `[^=]` as an anchor — a false accusation inside the guard against
false claims, caught only because I verified the fix instead of assuming it.

**AC8 — gates, as numbers with their Δ, re-run AFTER the last prose edit (AC8.6):**

| Gate | Baseline (§0.1) | Mine | Δ |
|---|---|---|---|
| `pytest` (full suite) | 1621 passed / 0 failed / 0 skipped, exit 0 | **1631 passed / 0 failed / 0 skipped, exit 0** | **+10** — exactly this story's ten new cases. **No new skip, xfail or narrowed population** |
| `mypy argus` | Success, 87 source files | **Success: no issues found in 87 source files** | 0 |
| `bandit -r argus` | 19 Low / 0 Med / 0 High (conf 0/0/6/13) | **19 Low / 0 Medium / 0 High** (conf 0/0/6/13) | 0 |

**Module sizes, re-measured with the ceiling test's own method** (`len(read_text(encoding="utf-8").splitlines())`) — **no exemption added, none requested:**

| Module | Before | After | Headroom |
|---|---|---|---|
| `argus/detectors/vacuous_test.py` | 929 | **1,041** | 159 |
| `argus/detectors/provenance_scan.py` | 926 | **955** | 245 |
| `tests/test_vacuous_cross_language.py` | — | **738** | 462 |
| `tests/test_vacuous_density.py` | 1,060 | **1,087** | 113 |
| `tests/test_vacuous_detector.py` | 1,128 | **1,161** | **39** ⚠️ tightest in the repo |
| `argus/pipeline.py` | 1,111 | **1,111** | 89 — **untouched**, as AC4.5 requires |

`git tag -l` is empty; nothing pushed.

---

#### Review iteration 2 (2026-08-18) — gates, sizes and artifacts, re-measured

| Gate | Iteration 1 | Iteration 2 | Δ |
|---|---|---|---|
| `pytest` (full suite) | 1631 passed / 0 failed / 0 skipped | **1632 passed / 0 failed / 0 skipped**, exit 0 | **+1** — `-133`. No new skip, xfail or narrowed population |
| `mypy argus` | Success, 87 files | **Success: no issues found in 87 source files** | 0 |
| `bandit -r argus` | 19 Low / 0 Med / 0 High | **19 Low / 0 Medium / 0 High** (conf 0/0/6/13) | 0 |
| `_ASSERTION_CALLEES` | 89 | **88** | **−1** (`Error`) |
| `_CORROBORATION_ASSERTION_CALLEES` | 23 | **23** | **0 — byte-unchanged, confirmed by diff** |
| `ASSERTION_DENSITY_FLOOR` / `MOCK_RATIO_CEILING` | `1/4` · `1/2` | **`1/4` · `1/2`** | 0 — byte-unchanged |

| Module | Iteration 1 | Iteration 2 | Headroom |
|---|---|---|---|
| `argus/detectors/vacuous_test.py` | 1,041 | **1,113** | 87 |
| `tests/test_vacuous_cross_language.py` | 738 | **1,027** | 173 |
| `argus/detectors/provenance_scan.py` | 955 | **955** | 245 — untouched |
| `tests/test_vacuous_density.py` | 1,087 | **1,087** | 113 — untouched |
| `tests/test_vacuous_detector.py` | 1,161 | **1,161** | **39 — untouched; ZERO lines added** |
| `argus/pipeline.py` | 1,111 | **1,111** | 89 — untouched, as AC4.5 requires |

**No size exemption added, none requested.** ⚠️ **On the 39 lines, asked and answered rather
than left implicit: no, that is not an acceptable steady state to end an epic in** — it is the
tightest tracked module in the repository, it holds the moat's own false-accusation guard, and
Story 13.5 and Epic 15 both land on this detector next. It is nonetheless **deliberately not
split in a review fix round**: moving ~35 guards is a change with its own regression surface and
its own risk of silently dropping a case, and doing it in the same pass as two High findings
under a three-round budget trades a known risk for an unknown one. This round added **zero**
lines to that file. Both halves of that judgement are filed with a named owner and a target
story so the next writer is forced to confront it before adding a case rather than after.

**Dogfood artifacts — the currency guards fired again, and this time it is not a finding.** P7's
mechanism is now understood rather than surprising: the guards track `argus/` **LOC** as the
build-cost proxy, so any LOC change moves them. The entire delta is the generating commit sha,
**29411 → 29483 (+72** — exactly `vacuous_test.py`'s 1,041 → 1,113**)**, the same +72 in
partition 3, and the bundle hash that folds both. ⛔ **The NFR-C1 numerator is unchanged at
435**, so no finding count, no flag count and no audit-cost figure moved — which is the
independent confirmation that dropping `Error` is behaviourally inert on Argus's own tree too.
Discharged through `AI-E12-11`'s sequence: `argus/` delta committed (`cce9897`) → regenerate →
artifacts committed **separately** (`d563fa9`). No artifact hand-edited; no assertion loosened.

`git tag -l` is empty; nothing pushed.

⚠️ **Honest limits.** All gates are **LOCAL (Windows)**; *CI evidence is NOT ESTABLISHED* — see the
Debug Log for the five specific ubuntu behaviours reasoned about but not executed. The corpus
harness that produced every AC3 number is a scratch script, not tracked and not part of the suite,
so those figures are reproducible only by re-running it. **Go and Java tests remain unscored and
idiomatic Jest/Mocha/Vitest suites remain invisible** (`DF-14-3-A`/`-B`/`-C`, cited and not fixed;
`-132` pins it). The Go names ship **measurably inert** and are recorded as inert.

### File List

**Modified — `argus/` (committed `e252043`)**

- `argus/detectors/vacuous_test.py` — `_ASSERTION_CALLEES` 53 → 89 names + its comment block. 929 → **1,041** lines
- `argus/detectors/provenance_scan.py` — `_ASSIGNMENT_RE` and `_LEADING_CHAIN_RE` re-anchored `\A`/`\Z`; docstring claim corrected. 926 → **955** lines

**Tests (committed `e252043`)**

- `tests/test_vacuous_cross_language.py` — **NEW**, `TC-ArgusAgent-DETECT-001-123`..`-132`. **738** lines
- `tests/test_vacuous_density.py` — `-116` re-authored in place. 1,060 → **1,087** lines
- `tests/test_vacuous_detector.py` — the two `importorskip` lines → `_grammars_or_unevaluable()`. 1,128 → **1,161** lines (headroom **39** — the tightest module in the repo, and it got tighter; the story's "add no cases here" fence held, this is the two-line replacement it explicitly sanctioned)

**Regenerated artifacts (committed SEPARATELY, `d339076`, via `AI-E12-11`)**

- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md`
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md`
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md`

**Records (NOT committed — the working tree carries unrelated pre-existing work, §0.11)**

- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — **APPENDED ONLY** (+130 lines; append-only verified programmatically by prefix comparison)
- `_bmad-output/design-artifacts/ArgusAgent/stories/14-3-…md` — this file
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — the `14-3` key only

**Review iteration 2 — modified `argus/` + tests (committed `cce9897`)**

- `argus/detectors/vacuous_test.py` — `Error` removed from `_ASSERTION_CALLEES` (89 → **88**); the `DN-14-3-5` collision rule, its 4,046-file measurement and its per-name decisions recorded beside the table. 1,041 → **1,113** lines
- `tests/test_vacuous_cross_language.py` — **`-133` NEW** (the collision rule, RED-first); `-131` re-authored with a non-vacuity floor, a `mock_ratio`-reachable fixture and the `_mock_bound_names` mechanism asserted directly; `-132` given parse/definition/degrade-reason floors and a live `DF-14-3-B` measurement; `-124` given a degraded-run floor; `-127` extended to hold `Error` out; module docstring records what the review found. 738 → **1,027** lines

**Review iteration 2 — regenerated artifacts (committed SEPARATELY, `d563fa9`, via `AI-E12-11`)**

- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md`
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md`
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md`

**Review iteration 2 — records (NOT committed)**

- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — `DF-14-3-G` and `DF-14-3-H` appended with named owners; `DF-14-3-D`'s unreproducible `sut=3` corrected in place with the original left visible and the amendment dated
- `_bmad-output/design-artifacts/ArgusAgent/stories/14-3-…md` — this file (§0.7(c) figure corrected the same way; `DN-14-3-5`; the iteration-2 resolution, gates and limits)
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — the `14-3` key only

---

## Change Log

| Date | Note |
|---|---|
| 2026-08-18 | Story contexted on HEAD `e2e278c` (post-14.1, post-14.2). All premises re-derived by execution through the shipped index and scorer. **Two premises did NOT survive.** (1) The named JS fixture is **no longer flagged**: 14.2's logical-statement denominator scores a K&R-brace JS function body at `statement_count = 0`, and the flag predicate requires `> 0` — so the epic's *"re-measured and is NOT flagged"* criterion is now **vacuously true** and would pass with no code change (§0.2, DN-14-3-4). The false accusation survives only in the **Allman-brace** shape, reproduced FLAGGED and measured closed by the widening (§0.3). (2) The §2.3 corpus prediction is **REFUTED, not merely unmeasured**: over all three members at their pinned shas the widening moves **0 flags gained, 0 lost** — agent-smith scores **0** TypeScript test functions of 169 extracted, xagents-webapp exactly **1** of 410, because `DF-14-3-A`/`-C` keep TS tests out of the scorer entirely (§0.4). The rationale therefore narrows to the mechanism and the fixture, exactly as the proposal's §3.3 pre-registered. Baselines re-measured: **1621 passed / 0 failed / 0 skipped**, mypy Success-87, bandit 19L/0M/0H; flag rates **653/3,551 · 295/1,122 · 17/73**; `_ASSERTION_CALLEES` is **53** names, not 23. `DN-14-2-1` vs NFR-P2 resolved without conflict: one table widened, two tables partitioned by QUESTION not by language (§0.7). The JS/TS verdict-ineligibility limitation was measured to be caused by `_MOCK_CALLEES`, **not** by DN-14-2-1 — so it is not a trap 14.2 laid — and is made AC6 rather than left unrecorded. `TC-ArgusAgent-DETECT-001-116` identified as the **only** guard that will go red, by design. Status `backlog` → `ready-for-dev`. |
| 2026-08-18 | **Implemented (Story 14.3).** ONE table widened: `_ASSERTION_CALLEES`, the density numerator, **53 → 89** names; `_CORROBORATION_ASSERTION_CALLEES` byte-unchanged at 23 and both thresholds byte-unchanged. **The RED came first** — the Allman-brace fixture measured `asserts=0 stmts=1 FLAGGED=True` in JS *and* TS on the unmodified tree, with `expect`/`toBe` provably already in the edge set (so the defect was a vocabulary gap, not a parse failure), and `asserts=2 FLAGGED=False` after, while its byte-identical assertion-free twin stays flagged. The epic's own criterion was **not** discharged against the fixture it names: `plainfn.test.js` scores `statement_count == 0` and is silent for 14.2's denominator reason (DN-14-3-4), pinned by `-125`. **AC3 measured per member, before and after: 0 flags GAINED and 0 LOST on all three, with the flagged SETS byte-identical** (653/3,551 · 295/1,122 · 17/73; corroborated 0 → 0) — §0.4's refuted corpus prediction reproduces on a LARGER vocabulary than §0.4 tested, so none of the 36 added names removes a real Python flag across 4,746 test functions. Vocabulary measured, not copied (`expect` 6876 · `toBe` 2560 · `toHaveBeenCalledWith` 696 · `equal` 1548 · `ok` 758 · `deepEqual` 506); `match`/`doesNotMatch` **excluded** with their reason, and `objectContaining` excluded as an argument builder rather than an assertion. `TC-ArgusAgent-DETECT-001-116` predicted RED **before** the suite ran and **re-authored, not nudged** — the 12-name literal is byte-identical and only the expectation inverted; it was the **only** guard that moved. New cohesion module `tests/test_vacuous_cross_language.py` (`-123`..`-132`, 738 lines). `DF-14-2-A` and `DF-14-2-B` both discharged, and the sweep written for the latter found a **second** `^` anchor (`_LEADING_CHAIN_RE`) the ledger entry never named; equivalence demonstrated over 218,017 lines / 25,649 matches / **0 disagreements**. `DF-14-3-D` filed with a named owner recording that no non-Python test can reach verdict-eligibility — measured to be caused by `_MOCK_CALLEES`, **not** by DN-14-2-1, so 14.2 laid no trap — plus `DF-14-3-E`/`-F`. ⚠️ **Guard prediction P7 was WRONG and is recorded as wrong:** the dogfood currency guards fired, and the mechanism is **not** the flag delta §0.8 measured (that was right — 0 flags moved) but the artifacts' **build-cost proxy**, total physical LOC, which rose by exactly the +141 lines added to `argus/`; a comment-only commit would have moved them identically. Discharged through `AI-E12-11` (`e252043` → regenerate → `d339076`), no artifact hand-edited, no assertion loosened. Gates **LOCAL, CI evidence NOT ESTABLISHED**. Status `ready-for-dev` → `review`. |
| 2026-08-18 | **Review iteration 1 — FAIL, two High findings; both resolved in iteration 2.** The review reproduced AC1's RED-then-green, AC3's 0/0 with byte-identical fingerprints on all three pinned shas, AC5's `-116` re-authoring, AC7's regex equivalence, the module sizes and the P7 explanation by independent execution — the story's substance held. What did not survive: (1) **the exclusion principle had been applied to `match`/`doesNotMatch` and to nothing else**, leaving six ordinary non-assertion Python identifiers (`ok`, `equal`, `Error`, `Equal`, `throws`, `rejects`) in the density numerator, where a wrong match RAISES density and REMOVES a flag — silent recall loss, contained only by the frozen corroboration table; (2) **`TC-ArgusAgent-DETECT-001-131` was itself a vacuous test** — its fixture's widened assertion cleared the density floor, so `_ast_corroborated` returned at `if not heuristically_vacuous: return False` and never called `provenance_evidence`, asserting a `False` it was always going to get, inside the vacuous-test detector's own suite. **Resolution.** `DN-14-3-5` replaces the judgement with a RULE — admit a name when its measured Python collision is materially below its measured JS/TS benefit — counted with the stdlib `ast` module over **4,046 independent Python files** (three pinned members, Argus, `site-packages`, the CPython 3.11 stdlib) against call-edge benefits from the shipped index. It reproduces both previously-ratified decisions (`match` out at **706 vs 476**, `expect` in at **29 vs 6,876**), which is the only reason to trust it, and it drops exactly one name: **`Error`, 164 measured Python call sites against a benefit of ZERO** — CPython's own `wave`/`aifc`/`sunau` each define `class Error(Exception)`, Go's `t.Error` is unreachable by two independent barriers, and JS/TS spells the non-assertion `throw new Error(...)`. `ok` (10 vs 764) and `equal` (34 vs 1,548) are **kept with their cost recorded and asserted by execution**, because they carry `node:assert`, the whole harness of a ratified member; `throws`/`rejects`/`Equal` are kept on **0** measured collisions in either call form. The rule disagrees with AC2.3 on `doesNotMatch` (0 vs 76) — **the project standard wins** and the tradeoff is recorded rather than bent. `-133` is new and was demonstrated **RED against the shipped table** (`assertion_sites=1`, `heuristically_vacuous=False` — a Python test with no assertion going unflagged). Re-measured after: **0 GAINED / 0 LOST with byte-identical `file::name@line` fingerprint sets on all three members**, none of the six names occurring as a callee in any of the 4,746 scored test functions, cartridge recall unchanged, `_CORROBORATION_ASSERTION_CALLEES` byte-unchanged at 23 and thresholds byte-unchanged. `-131` re-authored with a non-vacuity floor (`heuristically_vacuous is True`, mirroring `-115`), a fixture reaching the predicate through `mock_ratio 4/7 > 1/2` (the strict boundary asserted, not assumed) and **the mechanism asserted directly**: `_mock_bound_names` binds nothing in `const fake = Mock();` and binds `fake` in `fake = Mock()`. ⚠️ **The sweep of `-123`..`-132` found a SECOND instance** — `-132` concluded silence from `scored == []`, which is exactly what an unparsed file produces; it now proves each fixture parsed, names the degrade reason and measures `DF-14-3-B` live. `-124` given the same floor. The unreproducible `sut=3` figure corrected in `deferred-work.md` and §0.7(c), named to a fixture, field spelled out, wrong number left visible. `DF-14-3-G` (nothing forces a future name through the rule) and `DF-14-3-H` (`test_vacuous_detector.py` ends the epic at 1,161/1,200 — judged **not** an acceptable steady state, deliberately not split inside a fix round, zero lines added) filed with named owners. Gates: **1632 passed / 0 failed / 0 skipped**, mypy Success-87, bandit 19L/0M/0H. Dogfood guards fired on the LOC proxy again — understood, not a finding: the NFR-C1 numerator is unchanged at **435**, so nothing behavioural moved; discharged through `AI-E12-11` (`cce9897` → regenerate → `d563fa9`). Gates **LOCAL, CI evidence NOT ESTABLISHED**. Status `in-progress` → `review`. |
| 2026-08-18 | **Review iteration 2 — PASS.** Both High findings independently re-verified as closed by execution, not by re-reading iteration 1's record. `DN-14-3-5`'s collision table reproduced **exactly** on a from-scratch 4,046-file population built independently (`Error` 164, `match` 706, `expect` 29, `ok` 10, `equal` 34, `Equal`/`throws`/`rejects`/`doesNotMatch` 0 — every figure exact); the JS/TS benefit side matched exactly on every small-volume and combined figure (`match` 476, `doesNotMatch` 76, `equal` 1,548, `deepEqual` 506, `toHaveBeenCalledWith` 696, `throws` 19, `rejects` 1) and within ~1% on the two largest (`expect`, `toBe`) where the file-glob differed slightly. The `-133` RED-first claim reproduced exactly against iteration-1's own shipped table. `-131`'s non-vacuity floor confirmed **load-bearing by mutation**: scoring iteration-1's own weaker fixture against the current detector fails the new floor, proving it is not decoration. The `-123`..`-133` sweep checked case by case — no unfloored negative found. The corrected `consumed_sut_calls` figures (frozen=3, one-table=1) re-derived independently and matched `deferred-work.md` exactly. `deferred-work.md`'s working-tree diff confirmed genuinely append-only (0 removed lines). `DF-14-3-H`'s deferral judged sound: splitting ~35 guards out of the tightest module in the repo inside a two-High-finding fix round would trade a known risk for an unknown one. Full suite independently re-run: **1632 passed / 0 failed / 0 skipped**, exit 0. No decision-needed, patch, or unresolved High/Medium finding remains. Status `review` → `done`. Epic 14 is complete; Story 13-5 is unblocked. |
