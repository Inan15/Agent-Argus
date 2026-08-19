# Story 15.2: The detector and the index agree on what a line is

Status: done

| | |
|---|---|
| **Epic** | 15 — Make the Gate Evaluable — a bench with the defect class in it |
| **Story key** | `15-2-the-detector-and-the-index-agree-on-what-a-line-is` |
| **Source** | [sprint-change-proposal-2026-08-19.md](../sprint-change-proposal-2026-08-19.md), **APPROVED by XAgent007, 2026-08-19** · [epics.md](../epics.md) §Story 15.2 (`epics.md:2905`) |
| **Contexted on** | HEAD `72a95ef` (`docs(15): correct-course — the detector and the index disagree on a line`), equal to `origin/master` |
| **Ordering** | ⛔ must be `done` **before any commit containing Argus output over any Epic-15 candidate**. **NOT** coupled to Story 15.1 in either direction — 15.1 is selection-only, and the two may run in either order or concurrently. |
| **Precondition** | ⛔ the **cohesion split of `tests/test_vacuous_detector.py` happens FIRST** (`DF-14-3-H`, re-pointed at this story on 2026-08-19). |

---

## Story

As the Argus maintainer,
I want the detector to read the same lines the index numbered,
So that an invisible character in a file cannot make Argus say a fully-asserted test asserts
nothing.

### What this story IS

A repair of an **unstated line-numbering contract** between `argus/detectors/vacuous_test.py`
and the Story 1.4 tree-sitter index. The detector consumes line **spans** the index numbered by
newline, then re-derives the **text** those spans point at with `str.splitlines()`, which splits
on ten more things. Every occurrence of one of the eight that survive the production read path
shifts the detector's view forward by one line, and the scored window silently loses its last
line — which, in a conventionally-written test, is where the assertions are.

It is also the repair of **two guards that cannot fail**: `TC-ArgusAgent-DETECT-001-107`
(VACUOUS) and `TC-ArgusAgent-DETECT-001-118` (WEAK), both named for exactly this subject and
neither able to observe it.

### What it is NOT

- **NOT** a form-feed special case. A patch naming `\x0c` and no other character does not
  satisfy AC2 — by explicit approval, since §3.1 option 3 of the source proposal was named as
  *the trap* so it could not be chosen quietly.
- **NOT** a fix of `argus/detectors/secret_scan.py`. It carries the same breach and is cited,
  not repaired here (`DF-15-2-B`, owner XAgent007) — see §0.15 for the decision and its price.
- **NOT** a change to `_is_test_function`, the edge extractor, or `_ASSERTION_CALLEES`.
  `DF-14-3-A` and `DF-14-3-B` are COUPLED and neither may move alone.
- **NOT** a threshold change. `ASSERTION_DENSITY_FLOOR`, `MOCK_RATIO_CEILING`, the ≥80% gate,
  FR34, `protocol_cleared`, `GATE_OUTCOMES`, corpus membership and `MANIFEST_FIELDS` are all
  byte-unchanged. A defect in a line count is not a reason to move a floor
  (precision-validation protocol §5; Story 13.3 / AC5).
- **NOT** a new epic, a re-opening of Epic 13 or Epic 14 (both `done`), or a re-run of Story
  13.5's gate round. `DF-13-5-A`'s ONE-round rule is **cited by this story and never executed
  by it.**

---

## ⛔ §0 — Premise re-measurement (this project's create-story control)

> **Why this section exists, restated because it keeps earning its keep.** `AI-E12-10` →
> `AI-E14-8` → `AI-E13F-2`: this phase refuted **four** premises in Epic 14 alone, and the
> source proposal itself corrected a fifth (`vacuous_test.py` briefed at *"~1,041 lines"*,
> measured **1,113**). **This pass found FOUR more.** They are §0.4, §0.5, §0.6 and **§0.17**, and
> each is recorded as a correction with the original named as wrong. **The defect itself, and
> every figure that describes it, survived re-measurement intact** — what did not survive was four
> figures *about* the defect's surroundings, which is exactly the class this control catches.

### §0.0 — Method

Every number below was produced on **2026-08-19** at HEAD `72a95ef` by **out-of-tree probes** in
the session scratchpad that import the **shipped** `argus.index.ast_index.build_ast_index`,
`argus.detectors.vacuous_test.VacuousTestDetector._score`,
`argus.detectors.secret_scan.SecretScanDetector._scan` and `argus.pipeline_stages._read_source`
read-only, over synthetic fixtures in a `TemporaryDirectory`. `git status --porcelain argus
tests` was **empty at the start of this pass and empty at the end**. **No file under `argus/` or
`tests/` was written.** The probes are **measurements, not designs** — they must **not** be
copied into the tree; this story writes its own guards.

### §0.1 — Baselines, verbatim. Re-derive these on YOUR tree before you touch anything

| | Measured at HEAD `72a95ef`, 2026-08-19 |
|---|---|
| `git rev-parse --short HEAD` | `72a95ef`, equal to `origin/master` |
| `git status --porcelain argus tests` | **empty** — both trees clean |
| `git diff --stat 57946a8..72a95ef -- argus tests` | `tests/test_status_document_registry.py \| 17 +` and **nothing else** — so every §2.4 figure in the source proposal was measured against a tree equivalent to yours for the modules that matter |
| Full suite, `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 python -m pytest -q` | **exit 0**, re-run during this pass. ⚠️ **Re-measure the counts yourself**; the orchestrator's hand-off states **1641 passed / 0 failed / 0 skipped**. |
| CI | green on `ubuntu-latest` × Python 3.10 / 3.11 / 3.12 through `72a95ef` |
| Local interpreter | CPython **3.11.15** (Windows). ⚠️ Console default codec is **cp1252** — see §0.18 |

**Module sizes, re-measured with the ceiling guard's own method (`_CEILING = 1200`;
`MAINT-001-03` pins 1200 pass / 1201 fail):**

| Module | Source proposal §2.4 | **Measured at `72a95ef`** | Headroom | Verdict |
|---|---|---|---|---|
| `argus/detectors/vacuous_test.py` | 1,113 | **1,113** | 87 | ✅ survives |
| `argus/detectors/provenance_scan.py` | 955 | **955** | 245 | ✅ survives |
| `argus/pipeline.py` | 1,111 | **1,111** | 89 | ✅ survives — ⛔ **must not be added to** |
| `tests/test_vacuous_detector.py` | 1,161 | **1,161** | **39** | ✅ survives |
| `tests/test_vacuous_density.py` | 1,087 | **1,087** | 113 | ✅ survives |
| `tests/test_vacuous_cross_language.py` | 1,027 | **1,027** | 173 | ✅ survives |
| `argus/detectors/secret_scan.py` | 583 | **575** | 625 | ⛔ **DOES NOT SURVIVE — §0.4** |

Line references, all re-verified by reading the files:

| Cited | Status at `72a95ef` |
|---|---|
| `argus/detectors/vacuous_test.py:958` — `source_lines = source.splitlines()` | ✅ **exact.** The defect site, inside `run()`. |
| `argus/detectors/vacuous_test.py:913` — *"reads the `source.splitlines()` list the detector already holds"* | ✅ exact — prose that goes stale, in scope |
| `argus/pipeline_stages.py:124` — `read_text(encoding="utf-8", errors="replace")` | ✅ exact — universal newlines, the production read path |
| `argus/detectors/secret_scan.py:334` — `source.count("\n", 0, match_start) + 1` in `_line_span` | ✅ exact |
| `argus/detectors/secret_scan.py:434` / `:447` — `source.splitlines()` / `source_lines[match.start_line - 1]` | ✅ exact |
| `tests/test_vacuous_detector.py:581` — `test_score_is_identical_on_CRLF_and_LF_source` (`-107`) | ✅ `def` at 581, id in the docstring at 582 |
| `tests/test_vacuous_density.py:708` — `test_the_denominator_is_identical_on_CRLF_and_LF_source` (`-118`) | ✅ `def` at 708, id in the docstring at 709 |
| `tests/test_vacuous_density.py:120` — `_score_one` scores `source.splitlines()` of the **in-memory** string | ✅ exact |
| `argus/detectors/vacuous_test.py:860-861` — `_is_test_function` is case-**sensitive** `startswith("test")` | ✅ **`DF-14-3-A` is still unfixed** |
| `argus/verdict/verdict_gate.py:86-96` — *"verdict-blocking ⇔ verdict-eligible ⇔ `depth_supported is not None`"* | ✅ exact |
| `tests/test_default_path_blocking_verdict.py:246` — `VERDICT-001-30`, TWO ARMS | ✅ exact |

### §0.2 — ⛔ THE DEFECT REPRODUCES EXACTLY. The briefed table came back byte-for-byte

Through the **REAL index** (`build_ast_index`) and the **production read path**
(`pipeline_stages._read_source`), on a **genuine, mock-free, fully-asserted** ten-line test
(nine body statements, three bare asserts), varying only the number of form feeds inside a
trailing comment on line 1:

| form feeds | `len(source.splitlines())` | index line count | index span | `assertion_sites` | `statement_count` | `assertion_density` | `heuristically_vacuous` |
|---|---|---|---|---|---|---|---|
| 0 | 10 | 10 | (1, 10) | 3 | 9 | **1/3** | `False` — correct |
| 1 | 11 | 10 | (1, 10) | 2 | 8 | **1/4** | `False` — *exactly on the floor* |
| 2 | 12 | 10 | (1, 10) | 1 | 7 | **1/7** | **`True` — FALSE ACCUSATION** |
| 3 | 13 | 10 | (1, 10) | 0 | 6 | **0** | **`True` — FALSE ACCUSATION** |

`ASSERTION_DENSITY_FLOOR` read from the shipped module: **`Fraction(1, 4)`**.
`MOCK_RATIO_CEILING`: **`Fraction(1, 2)`**. The premise **survives without amendment**: every
cell matches the figure this story was briefed with.

Note the shape of the mechanism, because it is what makes the contract framing the only correct
one: **the index span is right** — `(1, 10)` in every row — and **the edge line numbers are
right**, because both are the index's own numbering. What is wrong is only the **text** the
detector recovers for lines 1..10, because it recovers it from an eleven-element list.

### §0.3 — All EIGHT desynchronise. `\r` and `\r\n` cannot reach the detector — re-verified, not inherited

Measured through `pipeline_stages._read_source`. This is the load-bearing claim: **the entire
scope decision rests on which characters actually survive to the detector.**

| separator | survives the read path? | `splitlines()` count | newline count | decompositions diverge? | index span | flagged? |
|---|---|---|---|---|---|---|
| *(control — none)* | — | 10 | 10 | no | (1, 10) | no |
| `\x0b` VT | **yes** | 11 | 10 | **yes** | (1, 10) | 1 sep: no (on the floor) · 2 seps: **YES** |
| `\x0c` FF | **yes** | 11 | 10 | **yes** | (1, 10) | ″ |
| `\x1c` FS | **yes** | 11 | 10 | **yes** | (1, 10) | ″ |
| `\x1d` GS | **yes** | 11 | 10 | **yes** | (1, 10) | ″ |
| `\x1e` RS | **yes** | 11 | 10 | **yes** | (1, 10) | ″ |
| `\x85` NEL | **yes** | 11 | 10 | **yes** | (1, 10) | ″ |
| `\u2028` LS | **yes** | 11 | 10 | **yes** | (1, 10) | ″ |
| `\u2029` PS | **yes** | 11 | 10 | **yes** | (1, 10) | ″ |
| `\r` CR | **NO — normalised to `\n`** | 10 | 10 | no | (1, 10) | unreachable |
| `\r\n` CRLF | **NO — normalised to `\n`** | 11 | 11 | no | (1, 11) | unreachable |

**Both halves of the claim hold.** The eight arrive intact and desynchronise the two views; `\r`
and `\r\n` are collapsed to `\n` by `read_text`'s universal-newline decoding **before the
detector exists**, after which the two decompositions agree by construction. **That single fact
is why the two broken guards are broken**: the CRLF property they assert is true by construction
in production, and the eight characters that are *not* true by construction are the ones nothing
tests.

⚠️ **A consequence you must not lose:** `\r` and `\r\n` are still in AC3's measured list. They are
measured to establish the **normalisation**, not a desync — and the normalisation is a property
of `pipeline_stages.py`, not of the detector, so a guard asserting it must go **through the read
path** or it asserts nothing. That is exactly the failure `-118` has.

### §0.4 — ⛔⛔ CORRECTED FIGURE #1. `secret_scan.py` is **575** lines, not 583

The source proposal's §2.4 blast-radius table states `argus/detectors/secret_scan.py` at **583**.
**That figure is wrong.** Measured with `wc -l`:

- at HEAD `72a95ef`: **575**
- at `57946a8`, the sha the proposal measured against: **575**
- last commit touching the file: `58821c3` — so it was 575 when the proposal was written, too.

**The briefed figure was never measured.** It changes nothing about the decision it appears in
(575 and 583 are both far under 1,200 and the file is out of scope either way), and it is
recorded anyway because *"a figure stated as measured and carried forward unmeasured"* is the
class `AI-E13F-*` records four occurrences of, the proposal caught the fifth, and this is the
sixth. **Do not propagate 583.**

### §0.5 — ⛔⛔ CORRECTED FIGURE #2. The module to be split holds **24** ids, not "roughly thirty-five"

`DF-14-3-H` says `tests/test_vacuous_detector.py` is *"where roughly thirty-five of this
detector's guards live (`-87`, `-88`, `-89`..`-93`, `-101`..`-112`)"*. Measured by execution:

- unique `TC-ArgusAgent-DETECT-001-NN` ids in the module: **24**
- unique `TC-ArgusAgent-*-001-NN` ids of **any** verification area in the module: **24** — so
  every id in it is a `DETECT` id, and AC7's by-execution inventory has a single namespace
- the ids in full: **`-85`, `-86`, `-87`, `-88`, `-89`, `-90`, `-91`, `-92`, `-93`, `-94`,
  `-95`, `-100`, `-101`, `-102`, `-103`, `-104`, `-105`, `-106`, `-107`, `-108`, `-109`,
  `-110`, `-111`, `-112`**

The parenthesised enumeration inside the ledger entry is itself only ~19 ids, so the *"roughly
thirty-five"* prose disagrees with its own parenthesis. **24 is the number AC7's before/after
inventory must come back with.** This corrects one measurement inside `DF-14-3-H`; the entry
itself stays OPEN and nothing here disposes of it.

Where the neighbouring ids actually live, so the split does not go looking for them here:

| Module | ids | lines |
|---|---|---|
| `tests/test_vacuous_detector.py` | `-85`..`-95`, `-100`..`-112` (**24**) | 1,161 |
| `tests/test_vacuous_density.py` | `-113`..`-122` (**10**) | 1,087 |
| `tests/test_vacuous_cross_language.py` | `-123`..`-133` (**11**) | 1,027 |
| `tests/test_default_path_blocking_verdict.py` | `VERDICT-001-30`, `-116`, `-117` | — |

### §0.6 — ⛔ CORRECTED CLAIM #3. `DF-15-2-B`'s *"the scanner reports line 3"* is fixture-dependent

That ledger entry states that with one form feed in a comment above the secret *"the scanner
reports line 3 and the suppression engine is handed `'tail'`"*. Re-measured against the shipped
`SecretScanDetector._scan` on a minimal two-newline-line fixture:

| separator | line the scanner reports | text handed to the suppression engine | correct? |
|---|---|---|---|
| *(control)* | **2** | `AWS_KEY = "AKIAIOSFODNN7EXAMPLE"  # argus: ignore-secret` | ✅ yes |
| `\x0c` FF | **2** | `' tail'` | ❌ **WRONG LINE** |
| `\x0b` VT | **2** | `' tail'` | ❌ **WRONG LINE** |
| `\x1e` RS | **2** | `' tail'` | ❌ **WRONG LINE** |
| `\u2028` LS | **2** | `' tail'` | ❌ **WRONG LINE** |

**The mechanism and the direction reproduce exactly.** The reported line number is **2**, not 3,
because that number is a property of where the secret sits in the fixture, and the ledger's
fixture put it one line lower. This is a **nuance, not a defect in the entry** — recorded so
nobody re-measures it, gets 2, and concludes the entry is unreliable. The entry stays OPEN, and
its substance is confirmed: the suppression engine is handed the wrong line's text and the
operator's `argus: ignore-secret` is dropped.

### §0.7 — NEW MEASURED FACT the proposal did not have: the population contains **ZERO** of the eight

Scanned every source file (`.py .js .ts .tsx .jsx .go .java .rs .c .cpp .rb .php`, excluding
`.git`, `node_modules`, `__pycache__`, `.venv`) for the eight characters:

| tree | files scanned | occurrences |
|---|---|---|
| `argus/` | 87 | **NONE** |
| `tests/` | 120 | **NONE** |
| `d:/ProjectX/XAgents/XAgents/Minions` (corpus member, read-only) | 757 | **NONE** |
| `d:/ProjectX/XAgents/XAgents/XAgents/Agent-Smith` (corpus member, read-only) | 852 | **1 × `\x85` NEL** |

The single hit is
`agentsmith-ui/.next/dev/static/chunks/node_modules_next_dist_build_polyfills_polyfill-nomodule.js`
— under **both** `node_modules` (`argus/intake/ignore_rules.py:103`, `DEPENDENCIES`) **and**
`.next` (`:139`, `BUILD_OUTPUT`), so it is excluded from the audited population before any
detector sees it. Separately, **no test source in `tests/` even mentions any of the eight as an
escape sequence** — `grep` for `x0b|x0c|x1c|x1d|x1e|x85|u2028|u2029` across `tests/` and `argus/`
returns nothing.

**Why this is load-bearing, in three directions:**

1. **It makes AC4's prediction concrete and checkable.** The predicted flag-count delta over the
   ratified corpus members is **exactly 0**, in both directions. That is a number to be
   **refuted or confirmed by execution**, not a hope. If the dev measures a non-zero delta, the
   prediction was wrong, the reason must be found, and **the wrong prediction is recorded as
   wrong.**
2. **It makes AC8's guard-movement prediction concrete.** No existing fixture in `tests/`
   contains any of the eight, so **no existing guard's scored span can move** — provided §0.8
   holds. Any guard that *does* move is evidence the fix changed something other than the
   contract: a stop-and-investigate signal, not a number to re-baseline.
3. **It is the honest severity picture.** The defect is real, measured and reproducible, and it
   is **currently firing on nothing.** That is not a reason to skip the repair — Epic 15 is about
   to run `DF-13-5-A`'s ONE round on this instrument over repositories nobody has scanned, and
   `\u2029` arrives in any file that has passed through a word processor — but the story must
   **not** claim it is repairing a live corpus failure, because it is not.

### §0.8 — NEW MEASURED FACT: the corrected decomposition is **byte-identical** on all 219 tracked `.py` files

AC4's inertness requirement needs a decomposition provably equal to `splitlines()` on all-`\n`
source. **The naive one is not.** `"a\nb\n".split("\n")` is `['a', 'b', '']` — a phantom trailing
element `splitlines()` does not produce. Measured over the whole tracked tree and over the edge
cases, with:

```
newline_lines(s) := parts = s.split("\n"); drop ONE trailing "" if present
```

| input | `splitlines()` | `newline_lines()` | equal |
|---|---|---|---|
| `''` | `[]` | `[]` | ✅ |
| `'\n'` | `['']` | `['']` | ✅ |
| `'a'` | `['a']` | `['a']` | ✅ |
| `'a\n'` | `['a']` | `['a']` | ✅ |
| `'a\nb'` | `['a', 'b']` | `['a', 'b']` | ✅ |
| `'a\nb\n'` | `['a', 'b']` | `['a', 'b']` | ✅ |
| `'\n\n'` | `['', '']` | `['', '']` | ✅ |
| **every tracked `.py` file** | — | — | ✅ **219 of 219, zero disagreements** |

This is offered as **evidence that AC4 is satisfiable**, and as a warning about the one
off-by-one that would otherwise be discovered by a red guard. It is **not** a prescription of the
implementation: the decomposition's shape is `DN-15-2-2` and the dev owns it. Whatever shape is
chosen must be shown equal on this population **by execution**, not by argument.

### §0.9 — `-107` is VACUOUS and `-118` is WEAK. Both confirmed by execution, both figures exact

**`TC-ArgusAgent-DETECT-001-107`** — `tests/test_vacuous_detector.py:581`. Headline claim: *"the
predicate reads SOURCE LINES, so line endings must not matter."*

```python
crlf = lf.replace("\n", "\r\n")
assert "\r\n" in crlf                                    # the fixture really is CRLF
lf_score   = detector._score(lf.splitlines(),   edges, defn)
crlf_score = detector._score(crlf.splitlines(), edges, defn)
assert lf_score == crlf_score
```

Executed: `"\r\n" in crlf` → `True`, **and `lf.splitlines() == crlf.splitlines()` → `True`.** The
two calls to `_score` receive the same list value, the same `edges` and the same `defn`. `_score`
is pure (AR8, asserted in the module docstring). The headline assertion is therefore
`f(x) == f(x)` and **no line-ending defect can falsify it.** The guard asserts its fixture is
CRLF and then throws the CRLF away in the very expression that feeds the code under test.

Its only other live assertion is `assert lf_score.ast_corroborated is True`. Compared against
`TC-ArgusAgent-DETECT-001-104` (`tests/test_vacuous_detector.py:506`): **byte-identical six-line
`test_cartridge_shape` fixture, identical three-element edge list (`compute_total`@2, `Mock`@3,
`calculate`@5), identical expectation** — reached through `_score` instead of `_corroborated`.
**`-107` is a strict subset of `-104`.** Confirmed.

**`TC-ArgusAgent-DETECT-001-118`** — `tests/test_vacuous_density.py:708`. Three of its four
assertions are load-bearing (`statement_count == 4`, `assertion_sites == 1`,
`assertion_density == Fraction(1, 4)`). **The arm it is named for cannot fail**, for two
independently measured reasons, both re-confirmed here:

1. `_score_one` (`tests/test_vacuous_density.py:120`) calls
   `VacuousTestDetector()._score(source.splitlines(), entry.edges, definition)` — the
   **in-memory** string, not the file it just wrote. The denominator's input is byte-identical in
   both arms *by construction*, and `lf.splitlines() == crlf.splitlines()` was re-executed on
   this fixture too: `True`.
2. The on-disk bytes are not what the fixture says either. `target.write_text(source,
   encoding="utf-8")` uses `newline=None`. **Re-measured on this Windows host, exactly the
   briefed figures:** the "LF" arm is written **11 CRLF / 0 bare CR / 0 bare LF**; the "CRLF" arm
   is written **11 CRLF / 11 bare CR** — i.e. `\r\r\n`. Neither arm ever presents an LF file to
   the parser, and both produce an identical index.

### §0.10 — AC1 stays an OPEN QUESTION. Here is what makes the answer consequential

**What is established at `72a95ef`:** every reproduction in §0.2 and §0.3 returns
**`ast_corroborated = False`**, in *every* row, including the two false-accusation rows. So the
**measured** severity is a false `heuristically_vacuous` flag → a `RULE_HEURISTIC` finding with
`depth_supported = None` → **ADVISORY**.

**Why that says nothing about the real question, and the reason is mechanical:** the fixture is
**mock-free and call-free**, so `_ast_corroborated`'s **fact (a)** short-circuits —
`len(self._sut_call_sites(span_edges)) >= 1` is `False` because there are no calls at all — and
the function returns before **fact (b)** is ever evaluated. **The corroboration path was never
exercised by any reproduction that exists.** Confirmed by reading
`argus/detectors/vacuous_test.py:1053-1113`.

**The chain that makes the answer matter — established by reading the code, and this part is NOT
open:**

```
_score()  ast_corroborated = True
  -> run():978    rule_id = RULE_AST                     argus/detectors/vacuous_test.py:978
  -> run():982    depth   = CoverageDepth.AUDITED_SHALLOW
  -> build_recording(depth_supported=depth)              argus/detectors/base.py:163-204
  -> "verdict-blocking <=> verdict-eligible <=> depth_supported is not None"
                                                         argus/verdict/verdict_gate.py:86-96
  -> TC-ArgusAgent-VERDICT-001-30 arm 1: a DEFAULT run_audit_detailed -- no flags, no deep
     pass, no LLM, no cartridge harness -- reaches NOT_READY_FOR_RELEASE through exactly
     this rule.                       tests/test_default_path_blocking_verdict.py:246-263
```

So **if** the shifted line view can flip `ast_corroborated` from `False` to `True`, the false
accusation is not advisory — it is a **🔴 blocking verdict on the default path with no flags
set**, which is the lethal class.

**The mechanism that makes it conceivable, stated as a HYPOTHESIS TO TEST and explicitly NOT as
an answer:** `_edges_in_span` filters by the *index's* line numbers and is therefore correct, but
`provenance_evidence` is handed the **wrong text** for those same line numbers. An edge on index
line *N* whose real text is `captured = sut(3, 4)` (a **consumed** SUT call) can be classified
against the text of line *N−k*, e.g. `sut(1, 2)` (a **discarded** one) — and
`sut_result_is_discarded` is precisely the clause that must be `True` for corroboration. Both
directions are conceivable: corroboration wrongly **granted**, and corroboration wrongly
**withheld**.

⛔ **You may not inherit that paragraph as a finding.** It is a place to look. AC1 requires the
answer to be **determined by execution**, in either direction, and **"no reproduction found" is
recorded as exactly that and never as "cannot happen."** If you predict one answer and measure
the other, **record the prediction as wrong** — that is the whole reason the prediction is
written down first.

⚠️ **The fixture family this needs does not exist yet, and building it is the story's work.** See
§0.14 for the shape it must have, because getting that shape wrong made a real bug look absent
twice this week.

### §0.11 — ⛔ THE STRUCTURAL ROOT CAUSE of `-107`'s vacuity, and what it demands of the fix

`-107` is not vacuous by carelessness. It is vacuous because of **where the seam is**: `_score`
takes `list[str]`, so **the caller owns the decomposition**. Production's caller is `run():958`.
The guard's caller is the guard — and it re-implemented the decomposition, with the same
function, on an input it had normalised itself.

**Therefore: a fix that changes only the expression at `:958` leaves the hole open.** Every one of
`-101`..`-112` calls `_score` or `_corroborated` with a list it built itself; none of them would
observe a future regression at `:958`, for exactly `-107`'s reason. The next author gets the next
`-107` for free.

**What this story requires (AC2.3):** the line decomposition becomes a **named, importable,
single-definition** thing in `argus/detectors/vacuous_test.py` — *the* contract — and the new
guards exercise **that function or `run()`**, never a re-implementation of it. The shape is
`DN-15-2-2` and the dev chooses it (a module-level helper `run()` calls and tests import; or
`_score` taking `source: str`), but **whichever is chosen, a guard must be able to go RED when
the decomposition regresses.** Record the rejected alternative.

⚠️ This is also the narrow, mechanisable half of what `DF-15-2-A` proposes — *a guard asserting
`f(a) == f(b)` must first assert `a != b`*. That entry stays OPEN and is **not** implemented by
this story (it is a change to the loop's phase rules, not to this repository); but **this story's
own new guards must satisfy it**, which is AC9.

### §0.12 — The cohesion split: the boundary, PRESCRIBED, with the rejected alternative

⛔ **The split happens FIRST, before any case is added** — `DF-14-3-H`'s *"precondition, not
afterthought"*, re-pointed at this story on 2026-08-19. 39 lines of headroom; `MAINT-001-03` pins
**1,201 as the failure**.

⛔ **No `_EXEMPT_BY_DESIGN` entry and no shave.** `MAINT-001-04` asserts the registry may only
shrink; `test_module_size_ceiling.py::_REMEDY` names the cohesion split as *the* remedy and
forbids *"shaving lines"* and *"narrowing this guard's population"* by name.

**The module's structure, mapped by execution (`def` line → section banner):**

| Lines | Section banner | Contents | Needs the real index? |
|---|---|---|---|
| 1–44 | *(docstring + imports)* | — | — |
| 45–336 | `# ── Pure-logic cases (no tree-sitter) — construct the AstIndexEntry directly ──` | `_entry`, `-85`, `-95`, `-100`, `-86`, `-87`, `-88`, `-89`, `-90`, `-91`, `-92`, `-93` | no |
| 337–837 | `# ── Story 14.1: every branch of the NEW fact (b), reached deliberately ──` | `_corroborated`, `-101`..`-106`, **`-107`**, `_CONTINUATION_SHAPES`, `-109`, `-110`, `-108` | no |
| 838–954 | `# ── Integration cases over the real 1.4 AST substrate (tree-sitter) ──` | `_grammars_or_unevaluable()` + its module-level call, the `build_ast_index` import, `_VACUOUS_FIXTURE` / `_SUT_ASSERTING_FIXTURE` / `_GENUINE_FIXTURE`, `-94` | **yes** |
| 955–1161 | `# ── The SAME callee called more than once on ONE physical line ──` | `_DUP_HEAD`, `_REPEATED_CALLEE_SHAPES`, `_corroborated_over_real_index`, `-111`, `-112` | `-111` yes; `-112` no, but it shares `_DUP_HEAD` with `-111` |

**⛔ PRESCRIBED BOUNDARY (`DN-15-2-1`): lines 838 → EOF move verbatim to a sibling module.**

- **What the new module is about:** *cases that stand up the **real** Story-1.4 tree-sitter
  substrate*, plus the occurrence-resolution family that shares its fixtures. The retained module
  keeps *cases that construct an `AstIndexEntry` by hand*. **This boundary is not invented here —
  the module's own docstring already states it** (`tests/test_vacuous_detector.py:8-11`: *"The
  pure-logic cases construct an `AstIndexEntry` directly; the integration cases build it from a
  real tiny fixture via `build_ast_index`"*). The split makes an already-stated distinction
  physical.
- **Why 838 and not 955:** `_grammars_or_unevaluable()`, its module-level call and the
  `build_ast_index` import all live at 838–872, and `-111` at 1063 depends on all three. Splitting
  at 955 would separate `-111` from the guard that makes its dependency a NAMED `UNEVALUABLE`
  failure — reintroducing `DF-14-2-A`'s false green.
- **Why `-112` travels with it even though it is pure logic:** it shares `_DUP_HEAD` and
  `_REPEATED_CALLEE_SHAPES` with `-111`, and it exists specifically to pin `-111`'s
  order-invariance. Separating them splits one subject across the boundary.
- **No function is split across the boundary.** Every moved unit is a whole `def` or a whole
  module-level datum.
- **Suggested name:** `tests/test_vacuous_detector_index.py`. The dev may choose otherwise and
  record why; **the boundary is the prescription, the filename is not.**
- **Arithmetic, PREDICTED:** retained ≈ **837**; new ≈ **324 + header/imports ≈ 370**. ⛔ **This is
  a prediction. Measure both after the move and record the actual numbers.**
- ⛔ **`_grammars_or_unevaluable()` must be present in BOTH modules or in NEITHER.** If any case
  remaining in the retained module needs tree-sitter, the retained module needs the guard too.
  Measured: none does — but **verify rather than inherit**.

**REJECTED ALTERNATIVES, to be recorded in the new module's docstring (the remedy requires it):**

1. Splitting at the `-111` / `-112` pair so the new module holds *only* cases that literally call
   `build_ast_index`. **Rejected:** it splits the `_REPEATED_CALLEE_SHAPES` family across the
   boundary and separates `-112` from the guard it exists to pin.
2. Splitting by **id range** (`-85`..`-100` / `-101`..`-112`). **Rejected: an id range is an
   arithmetic boundary, not a subject boundary** — the choice `_REMEDY` forbids by name.

**⛔ WHERE THE NEW CASES GO — decided here, before they are written.** The separator table, the
control, the read-path guards and AC1's corroboration fixture family **all need the real index**.
They therefore belong in the **new** module, on the boundary above. `-107`, once rebuilt around
the split, **moves there too** — it currently lives at 581 in the pure-logic half, and its rebuilt
form must go through the real index or it cannot observe the thing it is named for. **Nothing in
this story is added to the retained module.**

### §0.13 — Guards: PREDICT before you measure. Write the predictions down first

Changing what `_score` reads changes flag rates in principle. Write these predictions into the
Dev Agent Record **before** running anything, then measure, then record every miss as a miss.

**Must stay GREEN and must NOT change verdict** — `-87`, `-88` and `VERDICT-001-30` are the moat's
own false-accusation guards, and a green suite that quietly lost one of them is the failure this
story is most capable of causing:

`DETECT-001-87` · **`-88`** · `-101`..`-106` · `-108`..`-117` · `-119`..`-133` ·
`VERDICT-001-116` · `VERDICT-001-117` · **`VERDICT-001-30` and its TWO-ARM structure**
(`tests/test_default_path_blocking_verdict.py:246`) · `MAINT-001-02` / `-03` / `-04` ·
`DOCS-001-77` / `-78`

**Will change, by intent, each as a recorded behaviour change:** `DETECT-001-107` (rebuilt,
relocated) · `DETECT-001-118` (terminator arm made able to fail; **its three load-bearing
assertions preserved byte-unchanged**).

**The prior, from §0.7, stated so it can be refuted:** **zero** existing guards change verdict and
the corpus flag-count delta is **zero in both directions**, because no fixture in `tests/` and no
in-scope file in either corpus member contains any of the eight. ⛔ **If anything moves, stop.** A
moved guard means the change touched something other than the contract. **Do not re-baseline a
threshold or an expected count to agree with a new output** — that is the antipattern this
repository refused in Story 11.2 and named again in Story 13.3 / AC5.

### §0.14 — ⚠️ FIXTURE GATE SHAPE, or you will draw a false conclusion

Two different shapes reach a flag, and **AC1 needs the second one while §0.2 uses the first.**

1. **The density-floor shape (mock-free).** What §0.2 uses. No mocks, no calls; the flag comes
   from `assertion_density < 1/4`. It **cannot** reach corroboration: fact (a) needs ≥1 candidate
   SUT call and there are none, so `_ast_corroborated` returns `False` before fact (b) runs.
   **Useless for AC1.**
2. **The mock-ratio shape.** To be flagged through `mock_ratio > 1/2` you need roughly **three
   mock constructions against two SUT calls**. ⛔ **A two-mock fixture sits exactly ON the strict
   `> 1/2` boundary and fires nothing.** This is already written into the tree —
   `tests/test_vacuous_detector.py:957-961`: *"three mock constructions are deliberate — a
   two-mock fixture never clears the STRICT `> 1/2` mock ceiling against two SUT calls, which is
   what makes this shape family easy to probe for and conclude, wrongly, that it is already
   safe."* **This made a real bug look absent twice this week.**

**AC1's fixture family therefore needs both properties at once:** a body that is heuristically
vacuous, *and* has mock-bound assertions, *and* has SUT calls whose results are
discarded/consumed on **specific lines**, so that a one-line shift moves an edge from a consumed
occurrence onto a discarded one. `_DUP_HEAD` (`tests/test_vacuous_detector.py:962`) is the
established prefix for exactly this and is the right thing to build on — **reuse it rather than
inventing a fourth vacuous fixture** (AR7 / §3.3: two spellings of one question is the
disagreement class this detector keeps closing elsewhere).

### §0.15 — `DF-15-2-B` — the scope decision, taken explicitly, with its price stated

**DECISION: `argus/detectors/secret_scan.py` is NOT repaired by this story.** That entry stays
OPEN, with owner **XAgent007 (Engineering Lead)** and `target_story: NONE`.

**The argument FOR folding it in, stated fairly because it looks like the stronger one:** it is
the *same root cause*, measured (§0.6), in the same repository — and a contract stated in one
detector and breached in another is not a contract. Fixing both together is what makes the framing
honest.

**The argument AGAINST, which wins:**

1. **Blast radius, and it is arithmetic, not taste.** This story already owes a cohesion split of
   a 1,161-line module, a production change to a 1,113-line one, ten separator guards, a rebuilt
   guard, a strengthened guard and an open measurement question (AC1). Adding a second detector
   with its own suppression-engine surface is how a scoped repair loses its scope.
2. **The measured direction is the safe one.** In `secret_scan` the suppression is **dropped**, so
   the secret is **reported** — over-reporting, which an operator can see and argue with. In
   `vacuous_test` the direction is a **false accusation against a genuine test.** Different
   severities justify different schedules.
3. **The dangerous mirror is unestablished.** Whether a suppression comment on an unrelated line
   can be applied to a real secret is **not** measured, and measuring it is part of that entry —
   which makes its own severity conditional on work this story is not doing.
4. **Sequencing, from the entry itself.** It records that the repair *"should land deliberately,
   after Story 15.2 has established what the corrected line-numbering contract looks like, rather
   than as a drive-by beside it."* Doing it here inverts that.

**The price, stated so it is not discovered later:** after this story lands, the repository has a
**stated** line-numbering contract that **one detector honours and another breaches.** AC10
requires the story to say so in plain words, **in the code that states the contract** — so the
next author meets the gap as a documented fact rather than as a surprise.

⛔ **The contract must be written where a second detector can adopt it.** If it is stated only
inside a private helper in `vacuous_test.py`, the `secret_scan` repair will invent a second
spelling of it. This is a constraint on `DN-15-2-2` — **not** a licence to build a shared utility
module now.

### §0.16 — OUT OF SCOPE: cite, do not drift

| Item | Why it is out, and what happens if you drift |
|---|---|
| `DF-14-3-A` — `_is_test_function` is case-**sensitive** `startswith("test")`, so Go's `TestXxx` and JUnit's annotation-marked methods are **never scored** | ⛔ **COUPLED to `DF-14-3-B`.** Verified still unfixed at `vacuous_test.py:860-861`. |
| `DF-14-3-B` — Go selector-expression calls never reach the edge set, so a Go test's assertions are invisible | ⛔ **The one-character fix to `-A` alone would score every Go test, find `assertion_sites=0` because `-B` hides the assertions, and FLAG IT — converting Go's harmless silence into a fresh false accusation across an entire language.** Restated because this story touches the same file and the temptation is adjacent. |
| `DF-14-3-C` — `describe`/`it` callback blocks yield **zero** definitions, so idiomatic Jest / Mocha / Vitest suites are invisible | AC10 requires the story to state plainly that this stays true after it lands. |
| `argus/detectors/secret_scan.py` | §0.15. |
| `argus/pipeline.py` (**1,111**, byte-fenced by Story 12.1; Story 10.3 routed a field *around* it) | ⛔ **No line is added to it.** |
| Any threshold · `protocol_cleared` · `GATE_OUTCOMES` · FR34 · `MANIFEST_FIELDS` · corpus membership · the adjudication record | Untouched. |
| `DF-13-5-A`'s ONE-round rule | **Cited by this story, never executed by it.** This story runs no gate round. |
| `DF-15-2-A` (a vacuity sweep in the DoD) and `DF-15-2-C` (the sweep's verdict table has no durable home) | Both stay OPEN with named owners. This story implements neither; AC9 makes its **own** guards exemplary against `DF-15-2-A`'s narrow half. ⛔ **`AI-E14-2` is NOT discharged by this story.** |

### §0.17 — Working tree state you must NOT disturb

Committed and pushed through `72a95ef`.

⛔⛔ **CORRECTED FIGURE #4, and it is the one most likely to make you damage something.** This
story was briefed with a working-tree list naming `architecture.md`, `deferred-work.md`,
`stories/13-4-*.md`, `stories/14-1-*.md`, `sprint-change-proposal-2026-08-17.md` / `-17b.md`,
`tests/test_evidence_citation.py`, `tests/test_module_size_ceiling.py`,
`tests/test_spec_claim_scope.py`, `tests/test_v1_commitment_closure.py` and
`tests/test_status_document_registry.py` as **uncommitted**. **That list is STALE.** Commits
`f1ab81c`, `57946a8` and `72a95ef` landed all of them. **Measured with `git status --porcelain`
at the moment this story was written**, the working tree is:

| State | Path |
|---|---|
| `M` | `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md` |
| `M` | `_bmad-output/design-artifacts/ArgusAgent/epics.md` |
| `M` | `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — ⚠️ **this story's own status edit is in here** |
| `M` | `_bmad-output/design-artifacts/ArgusAgent/stories/1-5-heuristic-vacuous-test-detector-tier-a-vacuous-path-ast-subset.md` |
| `??` | `_bmad-output/design-artifacts/ArgusAgent/stories/15-1-…md` (Epic 15's other story, selection-only) |
| `??` | `_bmad-output/design-artifacts/ArgusAgent/stories/15-2-…md` (**this file**) |
| `??` | `.bmad-drift-audit/` · `argusdemo/` · `bmad-dev-loop-pack/` · `_bmad-output/audit-reports/{ollama-audit,run-demo,self-audit}/` |

⛔ **`argus/` and `tests/` are BOTH CLEAN** — `git status --porcelain argus tests` is **empty**.
That is the state you start from and the state your diff must be measurable against. ⛔ **Re-derive
this list yourself before your first commit**; the one above is a measurement with a timestamp,
not a standing fact, and the brief that preceded it was wrong by ten paths.

⛔ Both corpus checkouts — `d:/ProjectX/XAgents/XAgents/Minions` and
`d:/ProjectX/XAgents/XAgents/XAgents/Agent-Smith` — are **live third-party trees. STRICTLY
READ-ONLY.**

### §0.18 — "Not done on a Windows-only pass" is now a concrete obligation, not a disclaimer

**This changed today.** CI runs and is **green** on `ubuntu-latest` × Python 3.10/3.11/3.12, and
everything through `72a95ef` has been pushed and exercised there. So AC11 is not *"be careful
about platforms"* — it is *"push, and read the matrix."*

⛔ **`pytest.skip` is a FALSE GREEN here.** `audit-ci.yml` sets
`ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`, and `pytest.importorskip` **ignores that variable** —
`DF-14-2-A`, filed by Story 14.2 against this very module. The correct pattern is already in the
tree and must be followed: a named **`UNEVALUABLE`** failure raised at import time
(`tests/test_vacuous_detector.py:841-870`), which fails **collection** and reads RED where a skip
reads green.

⛔ **The non-ASCII separators are exactly the class that behaves differently off this host.** Three
specific, nameable hazards, each an explicit obligation:

1. **Locale / stdout codec.** This host's console codec is **cp1252**, and printing `\x85` to it
   raises `UnicodeEncodeError` — **measured this session, in the first probe run.** A guard whose
   failure message interpolates a raw separator can therefore die with an encoding error instead
   of a useful assertion. ⛔ **Every new guard must render separators with `ascii()` or an escaped
   literal in its message, never raw.**
2. **File encoding.** Fixtures must be written with an **explicit** `encoding="utf-8"` and read
   back through the **production** read path. `\x85` is one byte in latin-1 and two in UTF-8;
   `\u2028` / `\u2029` are three. A fixture relying on the platform default encoding will not mean
   the same thing on ubuntu.
3. **Line-ending rewriting.** `write_text(..., newline=None)` rewrites `\n` → `\r\n` on Windows and
   not on Linux — **the exact defect that makes `-118` weak.** Any fixture asserting a terminator
   property must use `newline=""` or `write_bytes`, and **must assert the bytes it wrote**, on both
   platforms.

**AC11's discharge is:** a pushed branch, a CI run over the matrix, and the run's result recorded
in this story — with anything that could not be established locally written down as **NOT
ESTABLISHED** rather than assumed (the form Story 14.3 / AC7.8 established).

---

## Acceptance Criteria

> Derived from [epics.md](../epics.md) §Story 15.2 (`epics.md:2905`), which is itself the source
> proposal's §4.1(b) verbatim. The AC text below **refines and sequences** those criteria against
> the §0 re-measurement; it does not weaken any of them, and every AC in `epics.md` appears here.

### AC1 — Whether the corrupted span can reach VERDICT-ELIGIBILITY is DETERMINED BY EXECUTION

**Given** every reproduction that exists (§0.2, §0.3) uses a fixture with **no mock-bound
assertions and no calls at all**, so `_ast_corroborated`'s fact (a) short-circuits and **the
corroboration path was never exercised**, and the source proposal explicitly declines to assert an
answer

**When** this story completes

**Then** it is **DETERMINED BY EXECUTION** whether the shifted line view can carry a finding to
**verdict-eligibility** — i.e. whether the corrupted span can make `ast_corroborated` read `True`
where a correct span reads `False`, **or the reverse**.

1. **AC1.1** — A **prediction is written into the Dev Agent Record BEFORE the fixture family is
   built**, with its reasoning. If the measurement contradicts it, **the prediction is recorded as
   wrong**, in those words.
2. **AC1.2** — The fixture family is built to §0.14's **mock-ratio shape** (≥3 mock constructions
   against 2 SUT calls; a two-mock fixture sits exactly on the strict `> 1/2` ceiling and fires
   nothing) and is driven **through the real index and the production read path**, not through a
   hand-built `AstIndexEntry`.
3. **AC1.3** — **Both directions are attempted**: corroboration wrongly *granted* (`False` →
   `True`) and corroboration wrongly *withheld* (`True` → `False`). The named hypothesis of §0.10 —
   an edge whose real text is a *consumed* SUT call being classified against the text of a
   *discarded* one, flipping `sut_result_is_discarded` — is a **place to look, not a finding**, and
   must not be recorded as an answer it did not measure.
4. **AC1.4** — The answer is **recorded as a measurement in either direction.** ⛔ **"No
   reproduction found" is recorded as exactly that, never as "cannot happen."** If the answer is
   *yes*, the story **records that the severity is higher than the proposal that created it
   assumed**, and says so in those terms.
5. **AC1.5** — Whatever the answer, the reproduction — or the recorded failure to reproduce — is
   **committed as a guard**, so the question cannot be re-opened by a future reader with no way to
   re-run it. If the answer is *no*, that guard pins **why**: the precondition state that makes the
   absence meaningful (`AI-E14-1` / `AI-E13F-1`), never a bare `assert ... is False`.

### AC2 — The fix is a stated LINE-NUMBERING CONTRACT, not a character special-case

**Given** `str.splitlines()` splits on eleven things and the Story 1.4 index numbers lines by
newline alone

**Then**:

1. **AC2.1** — The fix is **stated and implemented as a contract**: *the detector's line
   decomposition is the index's line decomposition.* ⛔ **A patch that names `\x0c` — or any single
   character — and no other does NOT satisfy this AC.** Nor does a membership test against a
   separator set: the decomposition must be newline-based **by construction**, so that the ninth
   exotic separator is handled by a mechanism nobody has to remember.
2. **AC2.2** — The contract is **written down where the next author will read it**: in
   `argus/detectors/vacuous_test.py`, naming the index as the counterparty and naming
   `argus/pipeline_stages.py:124` as the reason `\r` / `\r\n` are not part of the problem.
3. **AC2.3** — ⛔ **The decomposition becomes a named, single-definition, importable thing**, and
   the new guards exercise **it or `run()`** — never a re-implementation of it. §0.11 is the
   reason: `-107` is vacuous *because* `_score` takes `list[str]` and the guard owned the
   decomposition. A fix that only edits the expression at `:958` leaves that hole open and the next
   `-107` comes free. The shape is `DN-15-2-2`; **record the rejected alternative.**
4. **AC2.4** — The contract is stated so a **second detector could adopt it** (§0.15) — without
   building a shared utility module in this story.

### AC3 — Every one of the ten is MEASURED, and each is shown RED before the fix

**Given** eight characters were measured to survive the production read path and desynchronise the
two views (§0.3), and two were measured to be normalised away

**Then**:

1. **AC3.1** — A guard covers **each of the eight**: `\x0b` (VT), `\x0c` (FF), `\x1c` (FS), `\x1d`
   (GS), `\x1e` (RS), `\x85` (NEL), `\u2028` (LS), `\u2029` (PS) — **through the real index** — and
   **each is shown to go RED against the current detector before the fix lands**, with the RED
   transcript recorded. ⛔ **Not a claim that it would go red. The observation.**
2. **AC3.2** — `\r` and `\r\n` are measured **too**, and their normalisation at
   `argus/pipeline_stages.py:124` is **re-verified by execution rather than inherited** from §0.3
   or from any list. Their guard must go through the **read path**, because the property belongs to
   `pipeline_stages.py`; a guard that normalises its own input asserts nothing, which is exactly
   `-118`'s defect.
3. **AC3.3** — The eight are driven as **data** — a table, on the `_CONTINUATION_SHAPES` /
   `_REPEATED_CALLEE_SHAPES` / `_DENOMINATOR_SHAPES` precedent — not as eight hand-written
   functions. The table asserts **both directions**, so a fix that bought safety by flagging
   nothing would fail it.
4. **AC3.4** — Every guard renders separators with `ascii()` or an escaped literal in its failure
   message, never raw (§0.18 hazard 1: this host's cp1252 console raises on `\x85` — measured).

### AC4 — The change is INERT on all-`\n` source, and the corpus delta is a measured number

**Given** the corrected decomposition changes what `_score` reads for **every** file, not only
pathological ones

**Then**:

1. **AC4.1** — It is demonstrated **by execution** that on all-`\n` source the corrected and
   current decompositions are **identical**. §0.8 measured this over **all 219 tracked `.py` files**
   plus seven edge cases with zero disagreements, using *"drop ONE trailing empty"*; ⛔ the naive
   `source.split("\n")` is **not** identical — it produces a phantom trailing element. **Re-run this
   against YOUR implementation**: §0.8 establishes that the AC is satisfiable, not that your code
   satisfies it.
2. **AC4.2** — The **flag-count delta over the ratified corpus members is measured and recorded as
   a number, in both directions.** ⛔ **Predicted: 0 and 0**, on the §0.7 measurement that no
   in-scope file in either member contains any of the eight. **If the measured delta is non-zero,
   the prediction was wrong, it is recorded as wrong, and the cause is found before the story
   proceeds.**
3. **AC4.3** — Both corpus checkouts are **read-only third-party trees.** Measurement only; no
   write of any kind.

### AC5 — `TC-ArgusAgent-DETECT-001-107` is REBUILT, not deleted, and proven RED by a mutation

**Given** `-107` is **VACUOUS** — `lf.splitlines() == crlf.splitlines()` is `True` (re-executed,
§0.9), so its headline assertion is `f(x) == f(x)` on a pure function, and its only live assertion
duplicates `-104` verbatim (byte-identical fixture, identical edges, identical expectation)

**Then**:

1. **AC5.1** — `-107` is **REBUILT around the split rather than deleted.** The subject is genuinely
   unguarded, and deleting the guard would remove the id that names it.
2. **AC5.2** — It is re-authored **`-86`-style: as an intended behaviour change, with the reason
   recorded in the docstring** — what the old assertion claimed, why it could not fail, and what
   the new one observes instead. ⛔ **Never silently adjusted until it matches output.**
3. **AC5.3** — It is **demonstrated by a MUTATION that makes it RED**, named and recorded in this
   story. ⛔ Confirm RED **against the current detector before making it green**.
4. **AC5.4** — It **moves to the new module** (§0.12): its rebuilt form needs the real index.
5. **AC5.5** — The duplication with `-104` is resolved by `-107` asserting something `-104` does
   not, and the story says which.

### AC6 — `TC-ArgusAgent-DETECT-001-118`'s terminator arm is made able to fail

**Given** `-118` is **WEAK** — `_score_one` (`tests/test_vacuous_density.py:120`) scores the
**in-memory** string, and on Windows `write_text(newline=None)` writes the "LF" arm as CRLF
(**re-measured: 11 CRLF / 0 bare CR**) and the "CRLF" arm as `\r\r\n` (**11 CRLF / 11 bare CR**)

**Then**:

1. **AC6.1** — The fixtures are written with the terminators they claim (`newline=""` or
   `write_bytes`), and **the guard asserts the bytes it actually wrote** before scoring them.
2. **AC6.2** — The scored source is derived from **the file that was written**, through **the same
   read path production uses** — not from the in-memory string.
3. **AC6.3** — ⛔ **Its three load-bearing assertions are preserved byte-unchanged:**
   `statement_count == 4`, `assertion_sites == 1`, `assertion_density == Fraction(1, 4)`.
4. **AC6.4** — Re-authored `-86`-style with the reason recorded, and **confirmed RED before green**
   by a named mutation, exactly as AC5.
5. **AC6.5** — ⚠️ After AC6.2 the arm may become *true by construction again*, because both arms
   normalise to `\n` at the read path (§0.3). ⛔ **If so, say so, and make the guard assert the
   normalisation itself** rather than an equality it cannot fail. **A guard that cannot fail is not
   repaired by moving where its input comes from.**

### AC7 — The COHESION SPLIT happens FIRST, and the id inventory is compared by execution

**Given** `tests/test_vacuous_detector.py` is at **1,161 of NFR-M1's 1,200** — 39 lines — and
`DF-14-3-H` requires the split **first**

**Then**:

1. **AC7.1** — ⛔ **The split happens BEFORE any case is added**, in its own step, as a **pure
   relocation** (the Story 13.4 precedent: *"the four blocks relocate verbatim"*).
2. **AC7.2** — The boundary is `DN-15-2-1` (§0.12): **lines 838 → EOF**, on the subject *cases that
   stand up the real Story-1.4 tree-sitter substrate*. **No function is split across the boundary.**
3. **AC7.3** — **The rejected alternatives are recorded in the new module's docstring** — the
   `-111`/`-112` boundary and the id-range boundary, each with its reason (§0.12). `_REMEDY`
   requires the docstring to name why the module exists.
4. **AC7.4** — ⛔ **NO `_EXEMPT_BY_DESIGN` entry and NO shave.** `MAINT-001-04` asserts the registry
   may only shrink; `argus/pipeline.py` must remain absent from it.
5. **AC7.5** — **Given** splitting the module that holds the moat's own false-accusation guards
   risks silently dropping a case (`AI-E3-1`), **then** the `TC-ArgusAgent-*` id inventory is
   compared **BY EXECUTION** before and after, and shown equal. **Measured before: 24** (§0.5).
   After the split and before `-107`'s rebuild the union across both modules must be **24**; after
   the story's new guards are added it is **24 + (new ids added)**, and **no id is lost**. ⛔ **By
   execution, never by eye** — this is `AI-E3-1`'s failure mode.
6. **AC7.6** — Collected-test count and per-module line counts are recorded before and after.
   §0.12 predicts ≈ **837 retained / ≈370 new**; **record the actual figures.**
7. **AC7.7** — Every import path and every full pytest node id cited elsewhere in the repository
   for a moved test is re-pointed, and the re-pointing is verified by execution. Story 13.4 found
   ids cited *"in three different forms requiring three different treatments"* — search
   `architecture.md`, `deferred-work.md`, `epics.md`, the retros and every test module.
8. **AC7.8** — ⛔ **`argus/pipeline.py` is byte-unchanged. No line is added to it.**

### AC8 — Guards move only where intended, and the prediction is written before the measurement

**Given** changing the scored span changes flag rates in principle

**Then**:

1. **AC8.1** — The §0.13 prediction is transcribed into the Dev Agent Record **before** the fix is
   run, split into *must not move* and *moves by intent*.
2. **AC8.2** — After the fix, the full suite is run and **every** delta against the prediction is
   recorded, including deltas of zero. ⛔ **A wrong prediction is recorded as wrong.**
3. **AC8.3** — These stay GREEN with their assertions byte-unchanged: `DETECT-001-87`, **`-88`**,
   `-101`..`-106`, `-108`..`-117`, `-119`..`-133`, `VERDICT-001-116`, `VERDICT-001-117`, and
   **`VERDICT-001-30` with its TWO-ARM structure intact**.
4. **AC8.4** — ⛔ **No threshold, expected count or floor is re-baselined to agree with a new
   output.** If a guard moves, the change is wrong until proven otherwise (Story 13.3 / AC5;
   protocol §5).

### AC9 — This story's OWN guards are exemplary, and each records the mutation that reddens it

**Given** Epic 14 shipped **35** guards of which **4 did not hold what their titles claimed** —
`-131`, `-132` (found in Story 14.3's review), `-107` (vacuous) and `-118` (weak) — and `DF-15-2-A`
proposes making a vacuity sweep part of the definition of done

**Then**:

1. **AC9.1** — Every guard this story adds or re-authors that asserts an **absence**, an
   **equality** or an **invariance** records **one mutation that was executed and observed to make
   it RED.** Not a claim that one exists: the mutation, named, and the observation. This is
   `DF-15-2-A`'s arm (a), applied to this story's own output — the entry itself stays OPEN and is
   not implemented here.
2. **AC9.2** — ⛔ **A guard asserting `f(a) == f(b)` first asserts `a != b` at the seam it varies
   them across.** This is the widening `-107` proves: `-107` varies line terminators across a seam
   (`splitlines()`) that **erases** them, and `-118` varies them across a `write_text` that
   **rewrites** them. **Both are the same defect: the variable under test was constant.**
3. **AC9.3** — Every guard asserting a **NEGATIVE** first pins the **precondition state that makes
   the absence meaningful** (`AI-E14-1` / `AI-E13F-1`) — e.g. that the fixture really does contain
   the separator, that the parse really did succeed, that the definition really was found and the
   span really is what the index returned.
4. **AC9.4** — No `pytest.skip` / `importorskip` anywhere in the new or moved code. The named
   `UNEVALUABLE` failure at import time is the pattern (§0.18).

### AC10 — What stays broken is stated plainly, in the code

**Then** the story records, in the module that states the contract and in the completion notes:

1. **AC10.1** — `argus/detectors/secret_scan.py` carries the **same** breach (`:334` counts
   newlines, `:447` indexes `splitlines()`), **cited and NOT repaired here** (`DF-15-2-B`, owner
   XAgent007) — and **the repair is scoped to one detector while the contract is repository-wide**
   (§0.15).
2. **AC10.2** — `DF-14-3-A` and `DF-14-3-B` are **COUPLED**; this story does **NOT** touch
   `_is_test_function`, the edge extractor or `_ASSERTION_CALLEES`; and **Go and Java remain
   unscored** and **callback-style JS/TS suites remain invisible** (`DF-14-3-C`) after it lands.
3. **AC10.3** — `argus/detectors/provenance_scan.py:63-73`, `:132` and `:452` document themselves
   as *"line-terminator-agnostic by construction … it reads the `source.splitlines()` list the
   detector already holds"*. That prose is **re-derived against the corrected decomposition and
   corrected if it has become false.** ⚠️ It very likely has: under a newline decomposition a line
   can now carry `\x0b`, `\x0c`, `\x85`, `\u2028`, `\u2029` — and Python's `\s` and `str.strip()`
   both treat those as whitespace, so `_ASSIGNMENT_RE`'s `\A\s*` and the statement counter's
   stripping now see characters they never saw. **Measure it; do not reason about it.** The same
   applies to `argus/detectors/vacuous_test.py:913`.
4. **AC10.4** — `AI-E14-2` is **not** discharged by this story (its verdict table still has no
   durable home — `DF-15-2-C`), and `DF-14-3-H` stays OPEN with the split recorded against it.

### AC11 — "Not done on a Windows-only pass" is discharged concretely

**Given** local gates are Windows-only, CI now runs and is green on `ubuntu-latest` × Python
3.10/3.11/3.12, and non-ASCII line separators are exactly the class that behaves differently under
a different locale and a case-sensitive filesystem

**Then**:

1. **AC11.1** — The work is **pushed** and the **CI matrix result is recorded in this story** —
   run id / conclusion per Python version. ⛔ A local green is not a discharge.
2. **AC11.2** — ⛔ **`pytest.skip` is a FALSE GREEN** here (`audit-ci.yml` sets
   `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`, which `importorskip` ignores — `DF-14-2-A`). A named
   `UNEVALUABLE` failure is the correct pattern.
3. **AC11.3** — The three §0.18 hazards are each discharged with a named mechanism: `ascii()` in
   messages; explicit `encoding="utf-8"` on every fixture write **and** an assertion on the bytes
   written; `newline=""` / `write_bytes` wherever a terminator is claimed.
4. **AC11.4** — Anything that could **not** be established locally is written down as **NOT
   ESTABLISHED**, in those words (Story 14.3 / AC7.8's form).

### AC12 — Invariants, gates and hand-off

1. **AC12.1** — **AR8 purity** holds: no I/O, clock, LLM, `uuid4`, `random` or network anywhere in
   the scorer. The decomposition is a pure function of the source string.
2. **AC12.2** — **AR4**: exact `Fraction`, never `float`. `VacuousTestScore` stays **frozen** with
   `extra="forbid"` and its field set unchanged.
3. **AC12.3** — **NFR-D2** determinism and zero-token; every rendered set is `sorted()`.
4. **AC12.4** — **NFR-P2**: the language conditional stays in `argus/index/`.
5. **AC12.5** — `RULE_AST` / `RULE_HEURISTIC` vocabulary and the **Story 1.6 eligibility surface**
   are unchanged. **No threshold moves** — not `ASSERTION_DENSITY_FLOOR`, not `MOCK_RATIO_CEILING`,
   not the ≥80% gate, not FR34, not `protocol_cleared`, not `GATE_OUTCOMES`.
6. **AC12.6** — **NFR-M1**: every touched module ≤1,200 lines, measured, with `MAINT-001-02`,
   `-03`, `-04` green.
7. **AC12.7** — Gates re-run and recorded: `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 pytest` (counts +
   exit code), `mypy argus`, `bandit -r argus` — each against the §0.1 baseline, with every delta
   explained.
8. **AC12.8** — **Dogfood regeneration via `AI-E12-11`, in the required order:** commit the
   `argus/` delta → run `python scripts/regenerate_dogfood_artifacts.py` → commit the three
   artifacts **SEPARATELY**. ⚠️ The currency guards track `argus/` **LOC**, not behaviour, so they
   fire on a comment-only change (`AI-E14-7`).
9. **AC12.9** — ⛔ **`deferred-work.md` is never edited to make a guard quiet.** If
   `TC-ArgusAgent-DOCS-001-78` goes red, **fix the prose** — a disposition recorded in prose and
   not in the ledger is not a disposition (`AI-E12-3` / `AI-E12-6`).
10. **AC12.10** — The full suite is green at hand-off, with the counts recorded, and the story
    records what it did **not** establish.

---

## Developer Context & Guardrails

### Locked decisions this story must CITE, never re-derive

| Decision | Where it is locked | What you do |
|---|---|---|
| The remedy for a full guard file is a **COHESION SPLIT** — never a shave, never an exemption | `tests/test_module_size_ceiling.py::_REMEDY`; `MAINT-001-04`; Story 12.8 / 13.4 precedent | Cite it. **Do not re-derive.** |
| `MAINT-001-04`'s registry may only **shrink**, and `argus/pipeline.py` can never be added to it | `tests/test_module_size_ceiling.py:307` | Cite it. |
| **1,200 passes, 1,201 fails**, through the predicate | `MAINT-001-03` (`tests/test_module_size_ceiling.py:269`) | The boundary is measured, not argued. |
| A missing grammar is a named **`UNEVALUABLE`** failure at import time, never a skip | `tests/test_vacuous_detector.py:841-870`; `DF-14-2-A` | Follow the pattern exactly. |
| **Verdict-blocking ⇔ verdict-eligible ⇔ `depth_supported is not None`** — NOT keyed on `advisory` | `argus/verdict/verdict_gate.py:86-96` | The chain AC1 measures against. **Do not restate it as `advisory`.** |
| The corroboration path reads the **FROZEN** `_CORROBORATION_ASSERTION_CALLEES`, never the widened `_ASSERTION_CALLEES` | `DN-14-2-1`; `argus/detectors/vacuous_test.py:1103-1108` | Any new fixture must pass the frozen table where production does. |
| Fact (b) = SUT result discarded **and** ≥1 mock-referencing assertion; fact (a) = ≥1 candidate SUT call | `argus/detectors/vacuous_test.py:1053-1113` | This is why the mock-free reproduction says nothing about AC1. |
| A **failed measurement is not a reason to amend a threshold** | precision-validation protocol §5; Story 13.3 / AC5 | AC8.4. |
| Records are **superseded, never erased**; amendments are append-only | §3.4 of the source proposal; `AI-E13F-8` | Applies to `DF-14-3-H`, to the retros, and to this story's own record. |
| `DF-13-5-A` pre-registers **ONE** round for Epic 15 | ledger | **Cited, never executed by this story.** |

### Decisions this story must TAKE, each with its rejected alternative recorded

| Id | Decision | Guidance |
|---|---|---|
| **`DN-15-2-1`** | The cohesion boundary of `tests/test_vacuous_detector.py` | **Prescribed** in §0.12 (lines 838 → EOF). Two rejected alternatives are named there and must be written into the new module's docstring. If you choose a different boundary, it must be justified **by subject cohesion**, never by arithmetic, and the rejected ones still get recorded. |
| **`DN-15-2-2`** | The **shape** of the line-numbering contract | A module-level named decomposition `run()` calls and tests import, **or** `_score` taking `source: str`. §0.11 gives the constraint (a guard must be able to go RED when the decomposition regresses) and §0.15 gives the second (a different detector must be able to adopt the contract). Record the rejected shape. |
| **`DN-15-2-3`** | Whether `-107`'s rebuilt form supersedes `-104`'s duplicated assertion or asserts a genuinely new thing | AC5.5. |
| **`DN-15-2-4`** | What `-118`'s terminator arm asserts once its input comes from the file (AC6.5) | If the arm becomes true-by-construction again, the guard must move to asserting the **normalisation**, and that is a decision with a rejected alternative (deleting the arm). |
| **`DN-15-2-5`** | The `DF-15-2-B` scope decision | **Already taken** in §0.15: `secret_scan` is not repaired here. Restate it in the completion notes with its price (AC10.1). |

### Files to touch

| File | Lines now | Action |
|---|---|---|
| `tests/test_vacuous_detector.py` | 1,161 | **SPLIT FIRST** (`DN-15-2-1`). Retains the pure-logic half. Predicted ≈837. ⛔ **Nothing new is added to it.** |
| `tests/test_vacuous_detector_index.py` *(NEW; name is a suggestion)* | — | **NEW.** Receives lines 838→EOF verbatim, then `-107` rebuilt, then every new guard from AC1/AC3/AC4. Predicted ≈370 before the new cases. |
| `argus/detectors/vacuous_test.py` | 1,113 (87 headroom) | The contract lands here: the named decomposition, `run():958`, the docstring at `:913` re-derived. ⚠️ **87 lines of headroom — measure after.** |
| `tests/test_vacuous_density.py` | 1,087 (113 headroom) | `-118` re-authored in place (AC6). |
| `argus/detectors/provenance_scan.py` | 955 (245 headroom) | ⚠️ **Docstrings at `:63-73`, `:132`, `:452` re-derived** against the corrected decomposition and corrected if false (AC10.3). |
| `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` | — | Append-only, **if** AC1 or AC10.3 produces something new. ⛔ **Never edited to make a guard quiet** (AC12.9). |
| `argus/pipeline.py` | 1,111 | ⛔ **DO NOT TOUCH.** |
| `argus/detectors/secret_scan.py` | 575 | ⛔ **DO NOT TOUCH** (§0.15). |
| The three dogfood artifacts | — | Regenerated via `AI-E12-11`'s ordering (AC12.8), committed **separately**. |

### Previous-story intelligence — traps already paid for

1. **From Story 13.4 (the split precedent).** The split lands as a **pure relocation**; the id name-sets are compared **by execution** and shown byte-identical; **no new `TC-` id** is minted by the move itself; the collected count is identical; every moved assertion is proven RED **at the real seam from its new home** and then restored. Its baseline diverged from the story's §0 and **that was recorded, not smoothed** — expect the same and do the same.
2. **From Story 14.3.** Two premises did not survive its own §0, and one **corpus prediction was refuted**. The story recorded the refutation rather than quietly re-scoping. **Do that here**, especially for AC4.2's predicted 0/0.
3. **From Story 14.1 / `-86`.** A guard whose fixture no longer means what it meant is **re-authored as an intended behaviour change with the reason in the docstring**, never adjusted until it matches. `-107` and `-118` follow that form.
4. **From Story 11.2.** A count that turns out wrong is **re-derived by execution by two independent routes**, and the guard's floor is **not** re-baselined to agree with it.
5. **From `AI-E13-1` / `AI-E14-4`.** `TC-ArgusAgent-DOCS-001-78` went RED **three times in one epic**, twice out of prose written by a phase with no suite gate. ⛔ **Re-run the full suite after writing prose**, including this story file and the completion notes.
6. **From `AI-E12-11`.** Dogfood regeneration has a required commit ORDER. Getting it wrong produces a currency-guard red that looks like a behaviour change and is not.
7. **From `DF-14-2-A`.** `pytest.importorskip` ignores `ARGUS_REQUIRE_LANGUAGE_GRAMMARS` and once made ~40 guards — including the moat's own `-88` — report SKIPPED while the run read green.

### Testing requirements

- **Framework:** `pytest`, run as `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 python -m pytest -q`.
- **Ids:** new guards continue the `TC-ArgusAgent-DETECT-001-NN` sequence; **`-133` is the highest allocated** (in `tests/test_vacuous_cross_language.py`), so new ids start at **`-134`**. Verify by execution before allocating — do not trust this sentence.
- **Every guard's docstring** names its id, the AC it serves, and — per AC9.1 — the **mutation observed to make it RED**.
- **Data-driven** tables over hand-written repetition, on the established precedent (AC3.3).
- **Both directions** in every table: a fix that flagged nothing must fail, and a fix that flagged everything must fail.
- **Never** `pytest.skip` / `importorskip`.
- **Never** a raw separator in a failure message (§0.18).

### Project structure notes

- The detector is `argus/detectors/vacuous_test.py`; the statement/provenance primitives it reuses
  are in `argus/detectors/provenance_scan.py` (**AR7 REUSE — do not write a second scanner**); the
  index is `argus/index/ast_index.py`; the impure read is `argus/pipeline_stages.py:124`.
- Test modules are flat under `tests/`. The sibling-module split follows
  `tests/test_vacuous_density.py` / `tests/test_vacuous_cross_language.py` /
  `tests/test_status_document_registry.py`.
- ⛔ The language conditional stays in `argus/index/` (**NFR-P2**). The detector must not grow one.

### References

- [sprint-change-proposal-2026-08-19.md](../sprint-change-proposal-2026-08-19.md) — §1.3 the defect, §1.4 `-107`, §1.5 `-118`, §1.6 the second instance, §2.3 the open severity, §2.4 blast radius, §3.1 the rejected options, §4.1 the ACs, §5 the process lesson
- [epics.md](../epics.md) §Epic 15 (`:2827`), §Story 15.1 (`:2852`), **§Story 15.2 (`:2905`)**
- [epic-14-retro-2026-08-18.md](../epic-14-retro-2026-08-18.md) — `AI-E14-1`, `AI-E14-2`, `AI-E14-4`, `AI-E14-5`, `AI-E14-7`, `AI-E14-8`
- [epic-13-retro-2026-08-19.md](../epic-13-retro-2026-08-19.md) — `AI-E13F-1` (the standing non-vacuity rule), `AI-E13F-2` (premise re-measurement with teeth), `AI-E13F-8`
- [deferred-work.md](../deferred-work.md) — `DF-14-3-A`/`-B`/`-C`, `DF-14-3-H` (amended 2026-08-19), `DF-15-2-A`, `DF-15-2-B`, `DF-15-2-C`, `DF-14-2-A`, `DF-13-5-A`
- [precision-validation-protocol.md](../precision-validation-protocol.md) — §5 (a failed measurement is not a reason to move a threshold), §6 R2
- `architecture.md` §Enforcement — the registration form every standing rule must take
- Source: `argus/detectors/vacuous_test.py:913`, `:958`, `:1006-1051`, `:1053-1113`;
  `argus/detectors/provenance_scan.py:58-80`, `:128-140`, `:445-460`;
  `argus/pipeline_stages.py:115-124`; `argus/verdict/verdict_gate.py:86-96`;
  `argus/detectors/base.py:163-204`; `argus/intake/ignore_rules.py:103`, `:139`
- Guards: `tests/test_vacuous_detector.py:581` (`-107`), `:506` (`-104`), `:841-870`
  (`UNEVALUABLE`), `:957-961` (the mock-ratio shape), `:962` (`_DUP_HEAD`);
  `tests/test_vacuous_density.py:120` (`_score_one`), `:708` (`-118`);
  `tests/test_module_size_ceiling.py:68-110` (`_CEILING`, `_REMEDY`, `_EXEMPT_BY_DESIGN`);
  `tests/test_default_path_blocking_verdict.py:246` (`VERDICT-001-30`);
  `tests/test_governance_record_integrity.py:198` (`DOCS-001-78`)

---

## Tasks & Subtasks

- [x] **Task 0 — Re-derive §0 on YOUR tree (AC-wide precondition).** Do not start until this is done.
  - [x] Confirm HEAD, `git status --porcelain argus tests` empty, and the three gate baselines
        (`pytest` counts + exit code, `mypy argus`, `bandit -r argus`). Record them verbatim.
  - [x] Re-measure the seven module line counts. ⛔ **`secret_scan.py` is 575, not the 583 the
        proposal states** (§0.4) — confirm, and do not propagate 583.
  - [x] Re-confirm `-107` at `tests/test_vacuous_detector.py:581` and `-118` at
        `tests/test_vacuous_density.py:708`, and that `DF-14-3-A` is still unfixed at
        `argus/detectors/vacuous_test.py:860-861`.
  - [x] Re-run the §0.2 reproduction and the §0.3 separator table **out of tree**. If any cell
        differs, **record the corrected value and say the original was wrong.**
  - [x] Re-execute the `-107` tautology check and the `-118` byte counts (§0.9).
  - [x] Re-run the §0.7 corpus scan and the §0.8 decomposition-equality sweep on your tree.

- [x] **Task 1 — Write the predictions BEFORE measuring (AC1.1, AC8.1).**
  - [x] AC1's verdict-eligibility prediction, with reasoning.
  - [x] The §0.13 guard table: must-not-move vs moves-by-intent.
  - [x] AC4.2's corpus flag-delta prediction (§0.7 says 0 and 0).
  - [x] AC7.6's post-split line counts (§0.12 says ≈837 / ≈370).

- [x] **Task 2 — THE COHESION SPLIT, FIRST (AC7).**
  - [x] Capture the `TC-ArgusAgent-*` id inventory and the collected-test count **by execution**.
  - [x] Relocate lines 838 → EOF verbatim to the new sibling module. No function split.
  - [x] Write the new module's docstring: what it is about, the id set it holds, **both rejected
        boundaries with reasons** (§0.12).
  - [x] Amend the retained module's docstring: the new cohesion statement and where the rest went.
  - [x] Ensure `_grammars_or_unevaluable()` ends up in both modules or in neither, on evidence.
  - [x] Re-point every citation of a moved id — `architecture.md`, `deferred-work.md`, `epics.md`,
        the retros, other test modules — including any full pytest node id.
  - [x] Compare the id inventory and collected count by execution; assert equality. Record actual
        line counts. Full suite green **before** any new case is written.

- [x] **Task 3 — Reproduce the RED, before any fix (AC3.1, AC3.2, AC5.3, AC6.4).**
  - [x] In the new module: the control + one row per separator, through the real index and the
        production read path. **Observe RED. Record the transcript.**
  - [x] The `\r` / `\r\n` read-path normalisation guard. **Observe what it does before the fix.**
  - [x] The mutation that reddens the rebuilt `-107`, named and observed.
  - [x] The mutation that reddens `-118`'s repaired terminator arm, named and observed.

- [x] **Task 4 — AC1: determine verdict-eligibility by execution.**
  - [x] Build the mock-ratio fixture family (§0.14: ≥3 mocks / 2 SUT calls; `_DUP_HEAD` is the
        established prefix — reuse, do not re-invent).
  - [x] Attempt **both** directions: corroboration wrongly granted and wrongly withheld.
  - [x] Record the answer as a measurement. ⛔ "No reproduction found" is recorded as exactly that.
        If the prediction was wrong, **say it was wrong.** If the answer is *yes*, record that the
        severity is higher than the proposal assumed.
  - [x] Commit the reproduction — or the recorded failure to reproduce — as a guard with its
        precondition floor (AC1.5).

- [x] **Task 5 — The fix: state the contract (AC2).**
  - [x] Implement the newline-based decomposition as a **named, single-definition** thing
        (`DN-15-2-2`), with the rejected shape recorded.
  - [x] Point `run():958` at it. ⛔ No character special-case, no separator membership test.
  - [x] Write the contract prose: the index is the counterparty; `pipeline_stages.py:124` is why
        `\r` / `\r\n` are not part of the problem; a second detector could adopt this.
  - [x] Re-derive `argus/detectors/vacuous_test.py:913` and
        `argus/detectors/provenance_scan.py:63-73` / `:132` / `:452` (AC10.3) — **measure whether
        the "line-terminator-agnostic by construction" claim is still true**, since a line may now
        carry `\x0b`, `\x0c`, `\x85`, `\u2028`, `\u2029`, all of which Python's `\s` and
        `str.strip()` treat as whitespace.

- [x] **Task 6 — Turn the REDs green, and prove inertness (AC3, AC4).**
  - [x] All ten separator rows green. Re-verify the read-path normalisation by execution.
  - [x] AC4.1: corrected vs current decomposition identical on all-`\n` source, by execution, over
        the whole tracked tree. ⛔ Mind the phantom trailing element (§0.8).
  - [x] AC4.2: flag-count delta over both ratified corpus members, as a number, in both
        directions. **Corpora are READ-ONLY.**

- [x] **Task 7 — `-107` and `-118` (AC5, AC6).**
  - [x] `-107` rebuilt in the new module, `-86`-style, with the reason recorded, RED demonstrated
        first, and `DN-15-2-3` written down.
  - [x] `-118` re-authored in place: terminators actually written, bytes asserted, source read
        through the production path, **three load-bearing assertions byte-unchanged**, `DN-15-2-4`
        recorded — including AC6.5 if the arm is still true by construction.

- [x] **Task 8 — Guard sweep on this story's own output (AC9).**
  - [x] Every new/re-authored absence, equality or invariance guard carries its observed RED
        mutation.
  - [x] Every `f(a) == f(b)` guard first asserts `a != b` at the seam.
  - [x] Every negative pins its precondition.

- [x] **Task 9 — Measure against the predictions (AC8).**
  - [x] Full suite. Compare every guard against Task 1's prediction. **Record every miss as a
        miss.** ⛔ Nothing is re-baselined to agree with new output.

- [x] **Task 10 — Gates, artifacts, hand-off (AC10, AC11, AC12).**
  - [x] `pytest` / `mypy argus` / `bandit -r argus`, each against the Task 0 baseline, every delta
        explained.
  - [x] Module sizes re-measured; `MAINT-001-02`/`-03`/`-04` green; no `_EXEMPT_BY_DESIGN` entry
        added; `argus/pipeline.py` byte-unchanged.
  - [x] Dogfood regeneration in `AI-E12-11`'s order: commit the `argus/` delta → run
        `python scripts/regenerate_dogfood_artifacts.py` → commit the three artifacts separately.
  - [x] AC10's plain statements written into the code and the completion notes.
  - [x] **Push. Read the CI matrix. Record run id and conclusion per Python version.** Anything not
        established locally is written down as **NOT ESTABLISHED**.
  - [x] ⛔ **Re-run the full suite after writing the completion notes** — `DOCS-001-78` lints prose
        and has gone red three times in one epic. ⛔ **Never append a disposition to
        `deferred-work.md` to make a guard quiet.**

### Review Findings

**Code review, iteration 1 (2026-08-19, Sonnet).** Scope: commits `3acb028`, `e5a9e76`, `e3b9b52`,
`c66a065` (`git diff 72a95ef..c66a065`). VERDICT: **concerns**. Independently re-verified by
execution, not inherited from the Dev Agent Record: full suite **1645 collected, exit 0**;
`mypy argus` **Success, 87 files**; `index_aligned_lines` correctly desynchronises from
`splitlines()` on all eight separators and agrees with it on every all-`\n` edge case tried
(empty, no trailing newline, BOM, separator-only, mixed separators, multi-blank-tail) plus a
fresh 324-file tracked-tree sweep (0 disagreements, superset of the story's 219); the `-137` /
AC1 claim was reproduced from scratch with an independent script — the granting direction does
NOT reproduce against shipped code, DOES reproduce under all eight separators once
`provenance_scan`'s `located is None: consumed += 1` defensive line is removed (with the pre-fix
decomposition), and does NOT reproduce even with that line removed once the fix (`index_aligned_lines`)
is applied — confirming `-137` is genuinely load-bearing and not vacuous; `secret_scan.py`,
`pipeline.py` and `deferred-work.md` are byte-unchanged (`git diff` empty); no `_EXEMPT_BY_DESIGN`
entry added; module sizes, CI run conclusions (`32217374903`, success on 3.10/3.11/3.12) and the
`-88`→`-94` guard-message correction all confirmed independently. No functional defect found; all
ACs the reviewer sampled are met by execution. The findings below are documentation/process
completeness gaps, all Low severity — cleanups for the next round, not blockers.

- [x] [Review][Patch] Production-module headroom (`argus/detectors/vacuous_test.py` now
      1,186/1,200, 14 lines) is disclosed only in this story's Completion Notes, not in
      `deferred-work.md` — the dev's own text "recommend a ledger entry" was not acted on.
      `DF-14-3-H` covers the identical condition for the TEST module (now resolved by this
      story's split) but nothing in the ledger tracks the analogous, now-live condition on the
      PRODUCTION module, even though this project has repeatedly named "a disposition recorded
      in prose and not in the ledger is not a disposition" (`AI-E12-3`/`AI-E12-6`, restated in
      this story's own AC12.9) as a recurring failure class. Not a functional defect — the
      `MAINT-001-02`/`-03` ceiling guard remains the live safety net and will fail loudly, not
      silently, the moment a future change pushes past 1,200. Action: append a
      `DF-15-2-D`-style entry (owner + target_story) mirroring `DF-14-3-H`'s format.
      [`_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`]
- [x] [Review][Patch] `DN-15-2-2`'s rejected alternative (`_score` taking `source: str` instead
      of `list[str]`) is recorded only in this story's Completion Notes prose, never in
      `argus/detectors/vacuous_test.py` itself — inconsistent with this story's own pattern for
      every other DN it took (`DN-15-2-1` is recorded in both split modules' docstrings,
      `DN-15-2-3` in `-107`'s docstring, `DN-15-2-4` in `-118`'s), and short of AC2.2's "written
      down where the next author will read it" for this specific decision. Also worth
      re-examining on the merits next time the file has headroom: the blast radius cited for the
      rejection ("forced edits to `-101`..`-112`/`-118`") is broader than what a byte-diff check
      shows — only three shared helper functions (`_score_one` in `test_vacuous_density.py` and
      `test_vacuous_cross_language.py`, and the single direct call at
      `test_vacuous_detector.py:320`, id `-93`) call `_score` with a hand-built
      `.splitlines()` list; each would need a one-line internal edit and no `assert` statement
      would change, so AC8.3's actual text ("assertions byte-unchanged") would not literally be
      violated by the rejected shape. The chosen shape is a defensible, legitimate choice on its
      own merits (it lets arithmetic-only guards like `-93` stay decoupled from the decomposition
      contract) — this is a documentation-accuracy note, not a request to redo the decision.
      Action: correct the docstring's rationale and/or add a short cross-reference to
      `DN-15-2-2` in `index_aligned_lines`'s docstring next time this file has headroom to spend.
      [`argus/detectors/vacuous_test.py:911-980`]
- [x] [Review][Patch] Nine `(X)` placeholder markers were left unfilled in new/edited docstrings
      — apparent leftovers from an unfinished numbered-list template, not meaningful content.
      Action: renumber `(1)`/`(2)`/`(3)`/... or drop the parenthetical entirely.
      [`argus/detectors/vacuous_test.py:916,952,960,970`; `argus/detectors/provenance_scan.py:66`;
      `tests/test_vacuous_detector_index.py:418,479,662,727,993`]

**Code review, iteration 2 (2026-08-19, Sonnet).** Scope: `git diff c66a065..79a78cf` — `be3ff0a`
(code + ledger), `bc4bce9` (dogfood artifacts, per `AI-E12-11`, not hand-edited), `79a78cf` (story
record + sprint-status). VERDICT: **pass**. Iteration 1's own re-derivations (`index_aligned_lines`
newline-based by construction, the 324-file sweep, the `-137`/AC1 contingency) were **not** redone —
confirmed undisturbed by diff. Independently re-verified by execution this round: full suite
**1645 passed, exit 0** (`236.57s`); CI green on `bc4bce9` — run `32221995572` (`ubuntu-latest` ×
3.10/3.11/3.12) and `32221995581` (security shield), both `conclusion: success`, confirmed via
`gh run view`; `argus/pipeline.py` **1,111** and `argus/detectors/secret_scan.py` **575**, both
byte-unchanged over the whole story (`git diff 72a95ef..HEAD` empty for each); no threshold,
`GATE_OUTCOMES`, `protocol_cleared` or FR34 constant touched; `DF-14-3-A`/`-B`/`-C` cited, not
drifted into; the story's own placeholder sweep (`TODO`/`FIXME`/`XXX`/`TBD`/`(N)`/`<X>`) re-run
independently over `git diff 72a95ef..HEAD -- argus tests` — nothing found beyond the one false
positive (`TestXxx` inside prose about `DF-14-3-A`).

**Fix 1 — `DF-15-2-D`.** Well-formed and genuinely OPEN: owner XAgent007, `target_story: NONE`,
records **1,196/1,200** (re-measured: `wc -l argus/detectors/vacuous_test.py` → **1196**, exact),
`MAINT-001-02`/`-03` green, no `_EXEMPT_BY_DESIGN` entry, and the trigger. Re-ran
`ledger_closed_ids()` (imported live from `tests/test_governance_record_integrity.py`) against the
current `deferred-work.md` text: **`DF-15-2-D` not present** in the closed-id set. Re-ran
`story_closure_claims()` against the full story file text: **zero claims**. Nothing was closed.

**Fix 2 — `DN-15-2-2` moved into the docstring, blast radius corrected.** Re-derived the "three
pre-existing sites" claim from scratch by grepping every `_score(` call site across `tests/`:
confirms exactly `tests/test_vacuous_density.py:121`, `tests/test_vacuous_cross_language.py:203`
and `tests/test_vacuous_detector.py:320` (`-93`) hand a hand-built `.splitlines()` list to `_score`
— matches iteration 1's own count and the story's restated count; no fourth site exists (the two
calls inside `test_vacuous_detector_index.py` use `index_aligned_lines(read_back)`, not
`.splitlines()`, and the `(X)`-era code fragment at `test_vacuous_detector_index.py:799-800`
showing `.splitlines()` is inside a docstring illustrating the OLD, now-deleted guard — not live
test code). The decision is defended on decoupling, and the number matches what was measured.

**Fix 3 — `(X)` markers.** Confirmed by diff and by grepping both the pre-fix (`c66a065`) and
post-fix (`79a78cf`) trees: zero placeholder `(X)` markers remain anywhere in `argus/` or `tests/`;
the two survivors (`provenance_scan.py:764`, `test_vacuous_detector.py:348`) are byte-identical
`pytest.raises(X)` code examples. ⚠️ **One arithmetic slip, noted for the record and NOT blocking:**
the commit message and Completion Notes say "**nine** ... markers resolved — three numbered ...
six dropped" (3 + 6 = 9). Recount by diff: `vacuous_test.py` has 4 pre-fix occurrences (1 dropped +
3 renumbered `(1)`/`(2)`/`(3)`), `provenance_scan.py` has 1 (dropped), `test_vacuous_detector_index.py`
has 5 (all dropped) — **10 markers actually touched** (3 numbered + **7** dropped, not 6). The
resolution is **more complete than claimed, not less** — every real marker is gone, confirmed by
grep on both trees — so this is a pure count-in-prose error, not a missed marker. It is the same
class the review itself keeps flagging elsewhere (a number stated but not re-derived); recorded
here rather than silently corrected, and not worth a dev round on its own.

**New, Low: `DF-15-2-D`'s own ledger text contains two literal raw control-character bytes.**
`_bmad-output/design-artifacts/ArgusAgent/deferred-work.md:5205-5206` reads "the reason `` `<CR>` ``
/ `` `<CR><LF>` are not part of the problem" with **actual 0x0D bytes** embedded in the markdown
(confirmed with `cat -A` and a `rb'\r'` scan — two hits at byte offsets 1799/1805 of the entry),
where escaped literal text (`` `\r` `` / `` `\r\n` ``) was evidently intended, matching every other
occurrence of these separators in this story's prose. **No guard is affected** — every consumer
(`test_governance_record_integrity.py`, `test_module_size_ceiling.py`) reads the ledger via
`Path.read_text(encoding="utf-8")`, whose universal-newline translation normalises the bytes before
any string comparison runs; confirmed the full suite is green with this content present. It is a
rendering/authoring defect only (a raw `\r` byte reads as a line break in most viewers, and a raw
`\r\n` pair literally is one), not a functional one — noted because a ledger entry about a
line-terminator contract carrying an uncontrolled line terminator is exactly the kind of thing this
project's own `AI-E13F-*` class exists to catch, and it costs nothing to fix on next touch. Action:
next edit to that entry, replace the two literal bytes with the escaped `` `\r` `` / `` `\r\n` ``
text the surrounding sentence already uses everywhere else. [`_bmad-output/design-artifacts/ArgusAgent/deferred-work.md:5205-5206`]

**Headroom adjudication (`argus/detectors/vacuous_test.py`, 1,196/1,200, 4 lines), taken squarely.**
Four lines is genuinely tight — tighter than any module this story otherwise measured — and the
next touch to this file, of *any* size, is forced into an unplanned cohesion split. That cost is
real and is not waved through lightly. It is judged **correctly deferred, not a defect in this
story**, for four reasons: (1) `MAINT-001-02`/`-03` is a **hard, loud** CI failure at 1,201, not a
silent one — the trigger DF-15-2-D states ("the next change of any size performs the cohesion split
FIRST") is backed by a guard that makes violating it materially impossible to land unnoticed, not a
form of words resting on someone remembering; (2) placing Fix 2's content in
`index_aligned_lines`'s own docstring, rather than in `tests/test_vacuous_detector_index.py` or a
new shared module, was the right call, not just the cheapest one — AC2.2 requires the decision live
"where the next author will read it," which for a decision about a *production* function's contract
is the production function's own docstring, and §0.15 explicitly forecloses building a new shared
module now; a test-file location would hide a production-facing decision from the population that
needs it; (3) production-module cohesion is **not** an obvious, already-named boundary the way the
test module's "pure-logic vs. tree-sitter-integration" split was (stated in that module's own
docstring before this story existed) — inventing one now, under a fix-round's three-Low-finding
scope, risks the arbitrary-restructuring failure mode this project's controls exist to prevent, so
filing a ledgered, mechanically-enforced trigger is the more disciplined choice than an improvised
split; (4) `MAINT-001-04` forbids exactly the shortcut that would otherwise relieve the pressure
(shaving or exempting), and none was taken. **Should this story have split the production module
too? No — correctly deferred, not a gap in this story's scope**, on the record above.

**Not repeated this round, confirmed undisturbed:** AR8 purity of `index_aligned_lines` (still a
pure function of `source: str`, no I/O/clock/random in the diff); AR4 `Fraction` usage untouched;
determinism / `sorted()` usage untouched; corpus checkouts (`Minions`, `Agent-Smith`) not written by
this round — only read for the placeholder/`(X)` sweep, confirmed via `git -C` status showing only
pre-existing, unrelated modifications in those independent trees.

---

## Dev Agent Record

### Agent Model Used

`claude-opus-5[1m]` (Opus 5, 1M context), via the BMAD `dev-story` workflow. Session 2026-08-19,
baseline HEAD `72a95ef`.

### Predictions, written BEFORE measuring (AC1.1, AC8.1, AC4.2, AC7.6)

⛔ **Written before Task 2, before the AC1 fixture family existed, and before the fix was
implemented.** Every one is scored against its measurement in "Task 9 — predictions vs
measurements" below, including the ones that were wrong.

**P1 — AC1.1, verdict-eligibility. PREDICTED: YES, and in BOTH directions.**
Reasoning available to me at prediction time, from reading `provenance_scan.provenance_evidence`
and `vacuous_test._ast_corroborated` only: `_edges_in_span` filters by the *index's* line numbers
and is therefore correct, but each surviving edge is then classified by reading
`source_lines[line - 1]` — the detector's own, shifted list. With one separator above the body the
detector's element *k* holds the index's line *k−1*. In a `_DUP_HEAD`-shaped fixture holding both a
**discarded** `sut(1, 2)` and a **consumed** `captured = sut(3, 4)` on adjacent lines, the consumed
call's edge should be classified against the discarded call's text — setting
`sut_result_is_discarded` true and leaving no consumed call, which is exactly fact (b). That takes
`ast_corroborated` `False → True`, `rule_id` to `RULE_AST`, `depth_supported` to
`AUDITED_SHALLOW`, and — through `verdict_gate.py:86-96` and `VERDICT-001-30` arm 1 — to
`NOT_READY_FOR_RELEASE` **on a default run with no flags set**. I predict the reverse direction
(corroboration wrongly *withheld*) is reachable too, by putting the consumed call above the
discarded one.
**Confidence: moderate.** The named risk to the prediction is that `_locate_call` may simply fail
to find `sut(` on the shifted line and the evidence may degrade to "no SUT call located" rather
than to the opposite classification — in which case the answer is *no reproduction found* and
**this prediction is wrong.**

**P2 — AC8.1, guard movement.**

| | Prediction |
|---|---|
| **Must not move (assertions byte-unchanged, verdict unchanged)** | `DETECT-001-87`, **`-88`**, `-101`..`-106`, `-108`..`-117`, `-119`..`-133`, `VERDICT-001-116`, `VERDICT-001-117`, **`VERDICT-001-30` with its two-arm structure**, `MAINT-001-02`/`-03`/`-04`, `DOCS-001-77`/`-78` |
| **Moves by intent** | `DETECT-001-107` (rebuilt + relocated), `DETECT-001-118` (terminator arm made able to fail; three load-bearing assertions byte-unchanged) |
| **Predicted count of unintended moves** | **0.** Justification: §0.7, re-measured on my tree — no fixture in `tests/` contains any of the eight, so no existing guard's scored span can move. |

**P3 — AC4.2, corpus flag-count delta. PREDICTED: 0 and 0.**
On my own re-run of §0.7: `argus/` 87 files / 0 occurrences, `tests/` 120 / 0, Minions 757 / 0,
Agent-Smith 852 / 1 — the single `\x85` hit being under **both** `node_modules` and `.next`, so
excluded from the audited population before any detector sees it. ⛔ **A zero delta is the
PREDICTED and CORRECT outcome here, not evidence the fix did nothing** — the fix's inertness on
all-`
` source is AC4.1 and is measured separately.

**P4 — AC7.6, post-split line counts. PREDICTED: retained ≈837, new ≈370** (§0.12's arithmetic:
324 moved lines + header/imports).

### Task 0 — the premise, re-measured on MY baseline

Every §0 figure was re-derived on this tree before anything was written, by out-of-tree probes
in the session scratchpad importing the **shipped** modules read-only. `git status --porcelain
argus tests` was **empty at the start**.

| Baseline | §0.1 said | I measured | Verdict |
|---|---|---|---|
| `git rev-parse --short HEAD` | `72a95ef` | `72a95ef` | ✅ |
| `git status --porcelain argus tests` | empty | **empty** | ✅ |
| Full suite | 1641 passed / 0 failed / 0 skipped, exit 0 | **1641 collected, exit 0** | ✅ |
| `mypy argus` | — | **Success, 87 source files** | baseline recorded |
| `bandit -r argus` | — | **20 issues: 0 High / 0 Med / 20 Low severity** | baseline recorded |
| `vacuous_test.py` | 1,113 | **1,113** | ✅ |
| `provenance_scan.py` | 955 | **955** | ✅ |
| `pipeline.py` | 1,111 | **1,111** | ✅ |
| `test_vacuous_detector.py` | 1,161 | **1,161** | ✅ |
| `test_vacuous_density.py` | 1,087 | **1,087** | ✅ |
| `test_vacuous_cross_language.py` | 1,027 | **1,027** | ✅ |
| `secret_scan.py` | **575**, not the proposal's 583 | **575** | ✅ §0.4's correction CONFIRMED; 583 not propagated |
| ids in `test_vacuous_detector.py` | **24**, not "roughly thirty-five" | **24** | ✅ §0.5's correction CONFIRMED |
| `-107` at `:581`, `-118` at `:708`, `DF-14-3-A` unfixed at `:860-861` | — | all three **exact** | ✅ |

**§0.2 reproduced BYTE-FOR-BYTE** through `build_ast_index` + `pipeline_stages._read_source`,
on the story's own fixture shape (`def` on line 1, form feeds in a trailing comment):

| form feeds | `splitlines()` | index lines | span | assertion_sites | statements | density | vacuous |
|---|---|---|---|---|---|---|---|
| 0 | 10 | 10 | (1, 10) | 3 | 9 | **1/3** | `False` |
| 1 | 11 | 10 | (1, 10) | 2 | 8 | **1/4** | `False` — on the floor |
| 2 | 12 | 10 | (1, 10) | 1 | 7 | **1/7** | **`True` — FALSE ACCUSATION** |
| 3 | 13 | 10 | (1, 10) | 0 | 6 | **0** | **`True` — FALSE ACCUSATION** |

`ASSERTION_DENSITY_FLOOR = 1/4`, `MOCK_RATIO_CEILING = 1/2`, read from the shipped module.
**Every cell matches §0.2.** §0.3 also reproduced in full: all eight survive `_read_source` and
desynchronise the two views while the index span stays `(1, 10)`; `\r` and `\r\n` are
normalised and cannot. §0.9 re-executed: `lf.splitlines() == crlf.splitlines()` is **`True`**,
so `-107`'s headline assertion was `f(x) == f(x)`. §0.7 re-run: `argus/` **87 files / 0**,
`tests/` **120 / 0**, Minions **757 / 0**, Agent-Smith **852 / 1** — the single `\x85` under
both `node_modules` and `.next`. §0.8 re-run: **219 tracked `.py` files, 0 disagreements** for
"drop one trailing empty"; the naive `split("\n")` disagrees on **219 of 219**.

**Nothing in §0 was refuted on my tree.** The story's four corrections all held.

### Debug Log — REDs observed, and the mutations executed

⛔ Every mutation below was **executed and observed**, not asserted. One claim I wrote was
**measured FALSE and is recorded as false** rather than deleted.

**The RED before the fix (AC3.1).** With the decomposition still `splitlines()`, `-134` failed
on the first row and every row after it:

```
AssertionError: 1x VT ('\x0b') changed the score of a byte-equivalent genuine test:
  assertion_sites=2 statement_count=8 assertion_density=Fraction(1, 4)   <- shifted
  vs control
  assertion_sites=3 statement_count=9 assertion_density=Fraction(1, 3)   <- correct
```

24 of 24 separator rows RED (8 separators × 1/2/3 occurrences). `-135`'s CR arm and `-136` also
RED. **Observed, then made green.**

| # | Mutation | Guard | Observed |
|---|---|---|---|
| M1 | decomposition reverted to `source.splitlines()` (= HEAD `72a95ef`) | `-134`, `-107`, `-137` | **RED** (exit 1) |
| M2 | trailing-empty pop deleted (`if False:`) | `-136` | **RED** (exit 1) |
| M3 | `_read_source` → `read_bytes().decode("utf-8","replace")` (no universal newlines) | `-135`, `-118` | **RED** (exit 1) |
| M4 | `provenance_scan`'s `located is None` → `continue` instead of `consumed += 1` | `-137` | ⛔ **GREEN — my claim was WRONG** |

**M4: a claim of mine that did not survive its own check.** I had written into `-137`'s
docstring that M4 was the mutation that reddens it. Executed, **M4 leaves `-137` green**, because
with the contract in place both arms read the same lines and the consumed policy never comes
into play. The docstring was corrected to name **M1** as `-137`'s reddening mutation (verified
RED), and M4 was re-stated as what it actually is — see AC1 below, where it turned out to be the
most important measurement in the story.

### Task 4 — AC1: verdict-eligibility, DETERMINED BY EXECUTION

Fixture family built to §0.14's mock-ratio shape from `_DUP_HEAD`'s established prefix (three
`MagicMock` constructions), driven through the **real index and the production read path**, over
**six structurally distinct layouts** × 8 separators × 2 occurrence counts.

- **Corroboration wrongly WITHHELD (`True` → `False`): REPRODUCES.** A genuinely vacuous,
  corroborated fixture loses corroboration at one separator. Direction: accusation → advisory.
  Safe. Now guarded by `-107`.
- **Corroboration wrongly GRANTED (`False` → `True`): NO REPRODUCTION FOUND** against the
  shipped code, in any of the six layouts. ⛔ **Recorded as exactly that, never as "cannot
  happen."**

⛔ **And the absence was measured to be CONTINGENT, not structural — which is the finding.**
Every failure to read in `provenance_evidence` counts CONSUMED (`provenance_scan.py:907` and
two siblings), and "no SUT result is consumed" is a clause fact (b) requires; meanwhile the
shift moves the window backwards, so the span loses its trailing lines and
`mock_referencing_assertions` falls toward zero. Both clauses degrade the same, safe way. **I
tested that explanation instead of resting on it:** with the **pre-fix** decomposition and *only*
the conservative default removed (M4), the granting direction **reproduces immediately** —
`duplicated-assertions-padded` goes `False` → `True` under **all eight** separators at one
occurrence.

**So: severity is NOT higher than the proposal assumed — the measured reach was a false
ADVISORY flag, not a false blocking verdict — but the margin was a single line of defensive
coding in a different module, and nothing had pinned it.** `-137` is that pin.

⛔ **AC1.1: MY PREDICTION WAS WRONG, and is recorded as wrong.** I predicted **YES in both
directions**. The withholding direction reproduced; **the granting direction did not.** The
prediction missed the conservative CONSUMED default on an unlocatable edge — and that omission
turned out to be the load-bearing mechanism, not a detail.

### Task 9 — predictions vs measurements

| Prediction | Predicted | Measured | Verdict |
|---|---|---|---|
| **P1** AC1 verdict-eligibility | YES, both directions | withheld **yes**, granted **no** | ⛔ **WRONG — recorded as wrong** |
| **P2** unintended guard movement | **0** | **0** | ✅ correct |
| **P3** corpus flag delta | **0 and 0** | **0 gained / 0 lost** on all three | ✅ correct |
| **P4** post-split line counts | ≈837 retained / ≈370 new | **791** retained / **391** new (before new cases) | ⚠️ both off by ~45; the docstring rewrites account for it. Recorded, not smoothed |

**AC4.2, measured in both directions, corpora strictly read-only:**

| member | scored files | flags before | flags after | GAINED | LOST | files with any of the eight |
|---|---|---|---|---|---|---|
| Minions | 300 | 540 | 540 | **0** | **0** | **0** |
| Agent-Smith | 104 | 334 | 334 | **0** | **0** | **0** |
| Argus (self) | 148 | 275 | 275 | **0** | **0** | **0** |

A zero delta here is the **predicted and correct** outcome, not evidence the fix did nothing —
inertness is AC4.1 and is measured separately (`-136`, over all 219 tracked `.py` files).

**AC8.3 — all held GREEN with assertions byte-unchanged:** `-87`, **`-88`**, `-101`..`-106`,
`-108`..`-117`, `-119`..`-133`, `VERDICT-001-116`, `VERDICT-001-117`, **`VERDICT-001-30` with
its two-arm structure**, `MAINT-001-02`/`-03`/`-04`, `DOCS-001-77`/`-78`. **Nothing was
re-baselined.** The only two guards that moved are the two that moved BY INTENT (`-107`, `-118`).

### Task 2 — the cohesion split (AC7)

Split **first**, as a pure relocation, before any case was added; full suite green at that point.
Boundary `DN-15-2-1` as prescribed: **lines 838 → EOF**, the real-tree-sitter-substrate subject.
Both rejected boundaries (`-111`/`-112`; id-range) written into the new module's docstring with
reasons.

| | before | after |
|---|---|---|
| `tests/test_vacuous_detector.py` | 1,161 | **791** |
| `tests/test_vacuous_detector_index.py` | — | **391** at the split, **1,065** with this story's cases |
| `TC-` id union across the two | 24 | **24** — ⛔ **compared BY EXECUTION, none lost** |
| collected tests across the two | 24 | **24** at the split |

`_grammars_or_unevaluable()` travels with the integration cases and is **absent from the
retained module**, verified rather than inherited: measured, no retained case needs tree-sitter
(`build_ast_index` appears in the retained module only in prose).

⚠️ **The split falsified a claim in the guard it moved, and that was fixed rather than carried.**
`_grammars_or_unevaluable`'s failure message named `TC-ArgusAgent-DETECT-001-88` as the moat
guard a missing grammar would silence. After the split that is **false** — `-88` is pure logic
and stayed behind, where no grammar is needed. The message now names **`-94`**, the *integration*
false-accusation guard, which is the one actually at risk. Also corrected: the stale module-size
prose in `tests/test_vacuous_cross_language.py` (it claimed 1,163 / 1,060; the real figures were
1,161 / 1,087), left as the measurement that motivated that module with a note that Story 15.2
has since split the first again.

**AC7.7 — citations.** Every citation of a moved id outside the two modules lives in *historical
story records and retros*, which are **superseded, never erased** (`AI-E13F-8`), so none was
rewritten. The one live pytest node id cited elsewhere
(`stories/11-2-*.md:311`) names a test that **stayed** in the retained module. No import path
anywhere referenced a moved symbol.

### Completion Notes

#### Review iteration 1 — the three Low findings, addressed (2026-08-19)

⛔ **Documentation and ledger only. No behaviour changed, and none needed to.** The review found
**no functional defect and no unmet AC**, and re-derived the substance independently rather than
inheriting this record — including that `-137` is genuinely load-bearing (the granting direction
does not reproduce against shipped code, DOES reproduce under all eight separators once
`provenance_scan`'s defensive `consumed += 1` is removed with the pre-fix decomposition, and does
not reproduce even then once the fix is applied). **Nothing in that verification was redone,
re-measured or disturbed.** The delta of this round touches only docstrings, comments, this record
and the ledger; no expression, no threshold, no assertion and no test id moved. Gates re-run
after: suite **1645 collected, exit 0**; `mypy argus` **Success, 87 files**.

**Finding 1 — the ledger entry this story recommended and did not file. FILED.** The completion
notes below wrote *"recommend a ledger entry"* for the production module's headroom and stopped
there, which is the exact class `AI-E12-3` / `AI-E12-6` and this story's own `AC12.9` name: a
disposition recorded in prose and not in the ledger is not a disposition. **`DF-15-2-D`** is now
appended to `deferred-work.md` — OPEN, owner **XAgent007 (Engineering Lead)**, `target_story:
NONE` — recording the measured size, that `MAINT-001-02`/`-03` are green with **no
`_EXEMPT_BY_DESIGN` entry**, that the docstring was condensed twice and deliberately not shaved
below the content AC2.2 / AC2.4 / AC10.1 / AC10.2 require to be in the code, and the trigger:
**the next change of any size to `argus/detectors/vacuous_test.py` performs the cohesion split
first.** `DF-14-3-H` covers the test module only and stays OPEN; **nothing was disposed of** by
this append, and `TC-ArgusAgent-DOCS-001-78` was re-run against both analyzers to prove it —
`ledger_closed_ids` does not contain `DF-15-2-D`, and this story file yields **zero** closure
claims.

**Finding 2 — `DN-15-2-2` moved into the code, and its rationale CORRECTED.** The rejected
alternative (`_score` taking `source: str`) lived only in this file's prose, unlike `DN-15-2-1`
(both split modules' docstrings), `DN-15-2-3` (`-107`) and `DN-15-2-4` (`-118`) — short of AC2.2's
*"written down where the next author will read it."* It now lives in `index_aligned_lines`'s
docstring, the thing it governs. ⛔ **And my rationale was overstated, which is recorded rather
than quietly repaired.** I wrote that the rejected shape would force edits to `-101`..`-112` and
`-118`; the reviewer measured, and I re-confirmed by execution, that only **three** pre-existing
sites hand `_score` a list they built — `_score_one` in `tests/test_vacuous_density.py:121` and
`tests/test_vacuous_cross_language.py:203`, and the single direct call in `-93`
(`tests/test_vacuous_detector.py:320`) — one internal line each, **no `assert` changed**, so
AC8.3's literal *"assertions byte-unchanged"* would not have been violated either way. **The
decision stands** on its real merit (arithmetic decoupled from decomposition: a guard checking
only ratio exactness need not stand up a source string), **and the number does not.** An
overstated rationale defending a correct decision is still the `DF-8-5-C` class.

**Finding 3 — nine unfilled `(X)` markers. All nine fixed; the population was swept.** Three of
them form a real series in `index_aligned_lines`'s docstring and are now numbered **(1)** / **(2)**
/ **(3)**; the other six were standalone and the marker is dropped
(`argus/detectors/vacuous_test.py:916`, `argus/detectors/provenance_scan.py:66`,
`tests/test_vacuous_detector_index.py:418`, `:479`, `:662`, `:727`, `:993` — line numbers as at
`c66a065`). ⛔ **`argus/detectors/provenance_scan.py:764` was NOT touched**: its
`with pytest.raises(X): parse(bad)` is a legitimate code example, as is the identical construct at
`tests/test_vacuous_detector.py:348`; both are byte-identical at `72a95ef`, so neither was
introduced by this story. **Swept rather than spot-fixed:** the story's own `argus`/`tests` delta
grepped for `(X)` returns **exactly the nine**, and for `TODO` / `FIXME` / `XXX` / `TBD` / `(?)` /
`(N)` / `<X>` / *placeholder* returns **nothing**.

⚠️ **The cost of Finding 2, stated because it is the subject of Finding 1.** Moving `DN-15-2-2`
into the code added **10 lines** to `argus/detectors/vacuous_test.py`: **1,186 → 1,196 of 1,200,
headroom 14 → 4.** It fits; the ceiling guard is green; **no exemption was added and no line was
shaved from the AC2.2 / AC2.4 / AC10.1 / AC10.2 content.** The addition was condensed to eight
prose lines and deliberately reuses item **(2)**'s existing statement of the shape rather than
restating it. `argus/pipeline.py` stays at **1,111** and `argus/detectors/secret_scan.py` at
**575**, both byte-unchanged, and `DF-15-2-B` stays excluded per AC10.1. **`DF-15-2-D` records the
new number, not the old one** — the fix that resolves one finding is what consumed the headroom
the other is about, and that is written into the entry rather than absorbed.

**What was implemented.** A stated **line-numbering contract** —
`argus/detectors/vacuous_test.index_aligned_lines(source: str) -> list[str]` — newline-based
**by construction**, with no separator set and no `\x0c` special case, so the ninth exotic
separator is handled by a mechanism nobody has to remember. `run()` calls it. `DN-15-2-2`:
module-level named decomposition. **Rejected alternative: making `_score` take `source: str`** —
it would have forced edits to `-101`..`-112`, `-118` and `_score_one`, and AC8.3 requires those
assertions byte-unchanged; the named function achieves the same seam (a guard *can* now go RED
when the decomposition regresses — M1 proves it) without that blast radius.

**AC2.4 / AC10.1 — the price, stated in the code.** The contract's docstring says in plain words
that `secret_scan.py` carries the **same breach** (`:334` counts newlines, `:447` indexes
`splitlines()`), is **not repaired here** (`DF-15-2-B`, owner XAgent007), and that **the contract
is repository-wide while the repair is one detector deep**. `DN-15-2-5` restated: excluded
deliberately, because that direction over-reports (visible and arguable) where this one falsely
accuses a genuine test.

**AC10.2 — what stays broken, in the same docstring.** `DF-14-3-A`/`-B` are **COUPLED** and
neither moved: `_is_test_function` is still case-sensitive `startswith("test")`, Go and Java
remain **unscored**, Go selector calls still never reach the edge set, and fixing `-A` alone
would flag every Go test — a language-wide false accusation. `DF-14-3-C`: callback-style Jest /
Mocha / Vitest suites remain **invisible**.

**AC10.3 — measured, not reasoned.** `provenance_scan.py`'s "line-terminator-agnostic by
construction … reads the `source.splitlines()` list" prose at `:63-73`, `:132` and `:452` had
become stale in its wording. Under the corrected decomposition a line may now legitimately
*contain* `\x0b`/`\x0c`/`\x85`/`\u2028`/`\u2029`, which `\s` and `str.strip()` treat as
whitespace. **Measured** with each of the eight at the leading and trailing edge of a body line:
`body_statement_count` and `logical_statement_starts` return values **identical to the
separator-free control in all sixteen cases**. The claim survives; the wording did not, and is
corrected in place. Same for `vacuous_test.py:913`.

**A measured asymmetry found and recorded (not repaired).** `build_ast_index` reads files itself
rather than through `_read_source`, and tree-sitter does not accept a lone `\r` as a line break:
a **CR-only** file is numbered as **one line** by the index while the read path reads ten. The
contract still holds (the detector scores the line the index numbered) and the outcome is the
safe one — no statements, so no flag — and `-135` asserts both. It lives in `argus/index/`,
CR-only source occurs nowhere in the audited population, and it is **out of scope**, written
down so it is met as a measurement rather than a mystery.

**AC11 — the platform obligation.** `ascii()` in every new failure message (this host's cp1252
console **did** raise `UnicodeEncodeError` on a raw `\x85` during this session — hazard 1
confirmed live). Every fixture written with explicit `encoding="utf-8"` and `newline=""` or
`write_bytes`, **and the bytes asserted before scoring**. No `pytest.skip` / `importorskip`
anywhere in new or moved code; the named `UNEVALUABLE` failure at import time is the pattern.

**AC12 — invariants.** AR8 purity: `index_aligned_lines` is a total function of the source
string. AR4: no `float`, `Fraction` throughout; `VacuousTestScore` frozen, `extra="forbid"`,
field set unchanged. **No threshold moved** — `ASSERTION_DENSITY_FLOOR`, `MOCK_RATIO_CEILING`,
the ≥80% gate, FR34, `protocol_cleared`, `GATE_OUTCOMES`, corpus membership and `MANIFEST_FIELDS`
are byte-unchanged. `RULE_AST`/`RULE_HEURISTIC` and the Story 1.6 surface unchanged.
**`argus/pipeline.py` and `argus/detectors/secret_scan.py` are byte-unchanged** (`git diff`
empty). No `_EXEMPT_BY_DESIGN` entry added. `deferred-work.md` was **not touched during implementation**; the
iteration-1 fix round APPENDS one entry (`DF-15-2-D`, OPEN) and disposes of nothing — no entry
was marked closed, and no guard was quieted by prose.

**Module sizes after (NFR-M1 = 1,200):**

| module | before | after | headroom |
|---|---|---|---|
| `argus/detectors/vacuous_test.py` | 1,113 | **1,196** | **4** |
| `argus/detectors/provenance_scan.py` | 955 | **976** | 224 |
| `argus/pipeline.py` | 1,111 | **1,111** | 89 |
| `tests/test_vacuous_detector.py` | 1,161 | **791** | 409 |
| `tests/test_vacuous_detector_index.py` | — | **1,065** | 135 |
| `tests/test_vacuous_density.py` | 1,087 | **1,159** | 41 |
| `tests/test_vacuous_cross_language.py` | 1,027 | **1,031** | 169 |

⚠️ **A cost to flag for the reviewer, stated rather than buried:** `vacuous_test.py` ended
iteration 1 at **1,186 / 1,200 — 14 lines of headroom**, and ends the iteration-1 fix round at
**1,196 / 1,200 — 4 lines** (measured with the ceiling guard's own `_physical_line_count`).
`MAINT-001-02`/`-03` are green and the AC12.6 bound holds, but this is the same condition
`DF-14-3-H` was filed about for the test module, and the next story touching this file will hit
the ceiling. The contract docstring was condensed twice to buy that margin; it was **not** shaved
below the content AC2.2 / AC2.4 / AC10.1 / AC10.2 require to be *in the code*, and **no exemption
was added**. The proper remedy is a cohesion split of `vacuous_test.py`, which this story is not
scoped to perform. ⛔ **The recommendation is no longer prose:** it is filed as **`DF-15-2-D`**
(OPEN, owner XAgent007), with the trigger written down — the next change of any size to this
module performs the split first.

**Gates, against the Task 0 baseline:**

| Gate | Baseline | After | Delta |
|---|---|---|---|
| `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 pytest` | 1641 collected, exit 0 | **1645 collected, exit 0** | **+4** — exactly `-134`, `-135`, `-136`, `-137`. `-107` moved (not new), `-118` re-authored in place |
| `mypy argus` | Success, 87 files | **Success, 87 files** | none |
| `bandit -r argus` | 20 issues, 0 High / 0 Med / 20 Low | **20 issues, 0 High / 0 Med / 20 Low** | none |

Mid-round the two `AI-E12-11` dogfood currency guards fired (`argus/` LOC 29,755 → 29,776).
Understood, not a finding — they track LOC, not behaviour, and the corpus flag delta is 0/0.
Closed through that item's own pre-authorised order: commit the `argus/` delta (`3acb028`) →
`python scripts/regenerate_dogfood_artifacts.py` → commit the three artifacts **separately**
(`e5a9e76`). No artifact hand-edited; no assertion loosened, skipped, xfailed or narrowed
(`DF-8-5-B`).

**⛔ NOT ESTABLISHED (AC11.4), in those words.**

- **CI matrix: ESTABLISHED — pushed, run, and read.** ⛔ AC11.1 asked for observation rather than
  care, and this is the observation. Commit `e3b9b52` on `master`:

  | Workflow | Run id | Job | Conclusion |
  |---|---|---|---|
  | ArgusAgent Repository Audit & Assurance CI | **32217374903** | Argus Quality Gates & Audit Suite (**3.10**) | ✅ **success** |
  | ″ | ″ | Argus Quality Gates & Audit Suite (**3.11**) | ✅ **success** |
  | ″ | ″ | Argus Quality Gates & Audit Suite (**3.12**) | ✅ **success** |
  | ArgusAgent Student Code Audit & Security Shield | **32217374974** | Argus Code Quality & Security Audit | ✅ **success** |

  **Review iteration 1's fix round was pushed and read the same way.** Commit `bc4bce9` on
  `master` (`be3ff0a` docstrings + ledger, `bc4bce9` the regenerated artifacts):

  | Workflow | Run id | Job | Conclusion |
  |---|---|---|---|
  | ArgusAgent Repository Audit & Assurance CI | **32221995572** | Argus Quality Gates & Audit Suite (**3.10**) | ✅ **success** |
  | ″ | ″ | Argus Quality Gates & Audit Suite (**3.11**) | ✅ **success** |
  | ″ | ″ | Argus Quality Gates & Audit Suite (**3.12**) | ✅ **success** |
  | ArgusAgent Student Code Audit & Security Shield | **32221995581** | Argus Code Quality & Security Audit | ✅ **success** |

  This is the part that could not be established on a Windows-only pass: `ubuntu-latest` is a
  **case-sensitive filesystem with a UTF-8 default locale**, and `\x85` / `\u2028` / `\u2029` —
  one byte in latin-1, two and three in UTF-8 — are exactly the class that behaves differently
  there. `audit-ci.yml` sets `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`, so a missing grammar could not
  have been answered with a skip. The four new guards ran and passed on all three interpreters.
- **Not established:** whether a suppression comment on an unrelated line can be applied to a
  real secret in `secret_scan.py` (the dangerous mirror of `DF-15-2-B`). Out of scope; unmeasured.
- **Not established:** whether the granting direction is reachable through some layout not among
  the six attempted. "No reproduction found" is a bounded search, not a proof of impossibility.

**`AI-E14-2` is NOT discharged by this story** (`DF-15-2-C` — its verdict table still has no
durable home). `DF-14-3-H` stays OPEN with the split recorded against it. `DF-15-2-A` and
`DF-15-2-B` stay OPEN. `DF-13-5-A`'s ONE-round rule was **cited and never executed** — this story
ran no gate round.

### File List

**Modified**
- `argus/detectors/vacuous_test.py` — `index_aligned_lines` (the contract), `run()` points at it, `:913` prose re-derived. **Review iteration 1:** `DN-15-2-2` and its corrected blast radius moved into the contract docstring; four `(X)` markers resolved
- `argus/detectors/provenance_scan.py` — AC10.3 prose re-derived at `:63-73`, `:132`, `:452` (docstrings/comments only; no logic). **Review iteration 1:** one `(X)` marker resolved at `:66`; `:764` deliberately untouched
- `tests/test_vacuous_detector.py` — cohesion split (retains the pure-logic half); `-107` removed from here
- `tests/test_vacuous_density.py` — `-118` re-authored (AC6)
- `tests/test_vacuous_cross_language.py` — stale module-size prose corrected
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md` — regenerated
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md` — regenerated
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md` — regenerated
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — `ready-for-dev` → `in-progress` → `review`
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — **review iteration 1:** `DF-15-2-D` appended (OPEN). Append-only; nothing disposed of
- `_bmad-output/design-artifacts/ArgusAgent/stories/15-2-the-detector-and-the-index-agree-on-what-a-line-is.md` — this record

**Added**
- `tests/test_vacuous_detector_index.py` — the integration half of the split, plus `-107` rebuilt and `-134`/`-135`/`-136`/`-137`. **Review iteration 1:** five `(X)` markers resolved (comments/docstrings only)

**Deliberately NOT touched:** `argus/pipeline.py`, `argus/detectors/secret_scan.py`,
`architecture.md`, `epics.md`, and every pre-existing uncommitted path
(`E-PRD/prd.md`, `stories/1-5-*.md`, `stories/15-1-*.md`, `argusdemo/`, `.bmad-drift-audit/`,
`bmad-dev-loop-pack/`, `_bmad-output/audit-reports/*`). Both corpus checkouts were read
**read-only**; no write of any kind, no checkout, stash, clean, reset or worktree.

---

## Change Log

| Date | Version | Note | Author |
|---|---|---|---|
| 2026-08-19 | v0.1 | **Story contexted on HEAD `72a95ef`.** §0 re-measurement executed out-of-tree against the shipped modules; `git status --porcelain argus tests` empty before and after. **THE DEFECT SURVIVED RE-MEASUREMENT INTACT:** the form-feed table reproduces byte-for-byte through the real index (3/9 → 2/8 → 1/7 → 0/6; flagged at 2 and 3 form feeds), all **eight** exotic separators desynchronise the two views, and `\r`/`\r\n` are confirmed normalised at `argus/pipeline_stages.py:124` so they cannot reach the detector. `-107`'s tautology re-executed (`lf.splitlines() == crlf.splitlines()` is `True`; its live assertion is a byte-identical duplicate of `-104`); `-118`'s Windows byte counts re-measured exactly (LF arm 11 CRLF / 0 bare CR, CRLF arm 11 CRLF / 11 bare CR). **FOUR PREMISES DID NOT SURVIVE and are corrected, not propagated:** (1) `argus/detectors/secret_scan.py` is **575** lines, not the **583** stated in the proposal's §2.4 — 575 at HEAD and at `57946a8`, so the briefed figure was never measured; (2) `tests/test_vacuous_detector.py` holds **24** `TC-ArgusAgent-*` ids, not `DF-14-3-H`'s *"roughly thirty-five"* — 24 is the number AC7's by-execution inventory must return; (3) `DF-15-2-B`'s *"the scanner reports line 3"* is **fixture-dependent** — a minimal fixture reports **2** — while the mechanism and the wrong-line direction reproduce exactly; (4) **§0.17** — the briefed working-tree list was stale by **ten paths**, all of them landed by `f1ab81c` / `57946a8` / `72a95ef`, and `argus/` and `tests/` are both **clean**. **TWO NEW MEASURED FACTS the proposal did not have:** the audited population contains **ZERO** of the eight separators (`argus/` 87 files, `tests/` 120, Minions 757, Agent-Smith 852 with its one NEL hit under both `node_modules` and `.next`), which turns AC4.2's corpus delta into a falsifiable prediction of **0 and 0**; and the *"drop one trailing empty"* newline decomposition is **byte-identical to `splitlines()` on all 219 tracked `.py` files** plus seven edge cases, which establishes AC4.1 is satisfiable and names the phantom-trailing-element trap. **AC1 is preserved as an OPEN question in both directions**, as approved: every reproduction returns `ast_corroborated=False` because the mock-free fixture short-circuits fact (a), so the corroboration path has still never been exercised — and the chain that would make a *yes* lethal was established by reading (`RULE_AST` → `depth_supported` non-`None` → `verdict_gate.py:86-96` → `VERDICT-001-30` arm 1 → `NOT_READY_FOR_RELEASE` on a default run). **The cohesion split is PRESCRIBED with its boundary and two rejected alternatives** (`DN-15-2-1`: lines 838 → EOF, the real-tree-sitter-substrate subject the module's own docstring already names), and **where every new case lives is decided before it is written.** **The structural root cause of `-107`'s vacuity is named** (`_score` takes `list[str]`, so the caller owns the decomposition and the guard re-implemented it) and turned into AC2.3. **`DF-15-2-B` scope decision taken explicitly** with the argument for folding it in stated fairly and the price of excluding it recorded as AC10.1. Full suite re-run after writing this file. Nothing committed, staged or pushed; no file under `argus/` or `tests/` was modified. | Scrum Master (create-story) |
| 2026-08-19 | v1.0 | **Implemented (dev-story).** §0 re-derived on this tree before anything was written: **every figure held**, including the story's four corrections (`secret_scan.py` **575**, **24** ids, the `DF-15-2-B` fixture nuance, the working-tree list) — and §0.2 reproduced **byte-for-byte** (3/9 → 2/8 → 1/7 → 0/6, flagged at 2 and 3 form feeds). **The fix is a stated CONTRACT, not a character special-case:** `index_aligned_lines(source)` is newline-based **by construction** — no separator set, no `\x0c` case — so the ninth exotic separator needs nobody to remember it (`DN-15-2-2`; rejected: `_score` taking `source: str`, which would have forced edits to `-101`..`-112`/`-118`/`_score_one` that AC8.3 forbids). **Cohesion split FIRST** (`DN-15-2-1`, lines 838 → EOF): `test_vacuous_detector.py` **1,161 → 791** + `test_vacuous_detector_index.py`, both rejected boundaries in the new docstring, id union **24 → 24 by execution, none lost**, suite green before a single case was added. ⚠️ **The split falsified the moved `UNEVALUABLE` guard's own message** — it named `-88`, which stayed behind in the grammar-free half — now corrected to `-94`, the integration moat guard actually at risk. **RED observed before green on all 24 separator rows**, and **every mutation claimed in a docstring was executed**: M1 (revert decomposition) reddens `-134`/`-107`/`-137`, M2 (drop the trailing-empty pop) reddens `-136`, M3 (defeat universal newlines) reddens `-135`/`-118`. ⛔ **One of my own claims was measured FALSE and is recorded as false:** I had written that M4 (`consumed += 1` → `continue`) reddens `-137`; executed, it does not, and the docstring was corrected to name M1. **AC1 DETERMINED BY EXECUTION over six layouts × 8 separators × 2 counts, through the real index and read path:** corroboration wrongly **WITHHELD reproduces**; corroboration wrongly **GRANTED does NOT reproduce** against shipped code — recorded as *"no reproduction found"*, **never as "cannot happen"** — **and the absence was measured to be CONTINGENT:** with the pre-fix decomposition and *only* the conservative `consumed += 1` removed, the granting direction **reproduces under all eight separators**. So severity is **not** higher than the proposal assumed, but the margin was **one line of defensive coding that nothing had pinned**; `-137` is that pin. ⛔ **My AC1.1 prediction ("YES both directions") was WRONG and is recorded as wrong.** `-107` **REBUILT** (it was VACUOUS: `lf.splitlines() == crlf.splitlines()` is `True`, so its headline was `f(x) == f(x)`, and its only live assertion duplicated `-104`) and relocated, now pinning corroboration-invariance across the seam — something `-104` cannot see (`DN-15-2-3`). `-118` re-authored: bytes written and **asserted**, source read through the production path, **three load-bearing assertions byte-unchanged**; AC6.5 honoured — the arm is **still** true by construction, said so out loud, and now asserts **the normalisation itself** (`DN-15-2-4`; rejected: deleting the arm). **AC4.2 measured in both directions, corpora strictly read-only: 0 GAINED / 0 LOST** on Minions (540/540), Agent-Smith (334/334) and Argus (275/275) — **the predicted outcome**; inertness measured separately over all **219** tracked `.py` files. **P4 was off** (predicted ≈837/≈370, measured **791/391**) and is recorded rather than smoothed. AC10.3 **measured, not reasoned**: with each of the eight at both edges of a body line the statement counter and statement starts are **identical to control in all sixteen cases** — the claim survives, its wording did not, and `provenance_scan.py:63-73`/`:132`/`:452` plus `vacuous_test.py:913` are corrected in place. **A measured asymmetry recorded and not repaired:** a CR-only file is numbered as ONE line by the index while the read path reads ten; the contract still holds, the outcome is the safe degrade, `-135` asserts both, and it belongs to `argus/index/`. **Nothing re-baselined; no threshold moved;** `argus/pipeline.py` and `argus/detectors/secret_scan.py` **byte-unchanged**; no `_EXEMPT_BY_DESIGN` entry; **`deferred-work.md` not touched**. Gates: `pytest` **1645 collected, exit 0** (+4 = exactly the four new ids), `mypy argus` **Success 87**, `bandit` **0 High / 0 Med / 20 Low** — all unchanged from baseline. Dogfood currency guards fired on the LOC proxy (29,755 → 29,776) and were closed through `AI-E12-11`'s own order: `3acb028` → regenerate → `e5a9e76`. ⚠️ **Flagged for review:** `vacuous_test.py` ends at **1,186 / 1,200 (14 headroom)** — the `DF-14-3-H` condition, now on the production module; recommend a ledger entry, no exemption added. **CI matrix ESTABLISHED and GREEN** on `e3b9b52`: run **32217374903** succeeded on `ubuntu-latest` x Python **3.10 / 3.11 / 3.12**, and run **32217374974** (security shield) succeeded — so the non-ASCII separators were exercised under a UTF-8 locale and a case-sensitive filesystem, which a Windows-only pass could not establish. `AI-E14-2` **not** discharged; `DF-13-5-A` cited, never executed. Status `in-progress` → `review`. | Dev (dev-story) |
| 2026-08-19 | v1.1 | **Code review iteration 1 addressed (dev-story, fix mode) — 3 of 3 Low findings resolved; documentation and ledger ONLY, no behaviour changed.** The review found **no functional defect and no unmet AC**, and re-derived the substance independently rather than inheriting this record — `index_aligned_lines` newline-based by construction, the 324-file tracked-tree sweep, and the `-137`/AC1 contingency claim reproduced from scratch (does NOT reproduce against shipped code; DOES under all eight separators once `provenance_scan`'s defensive `consumed += 1` is removed with the pre-fix decomposition; does NOT even then once the fix is applied — so `-137` is genuinely load-bearing, not vacuous). ⛔ **None of that was redone, re-measured or disturbed.** **(1) `DF-15-2-D` FILED** in `deferred-work.md` — OPEN, owner XAgent007, `target_story: NONE` — for the production module's headroom, because this record wrote *"recommend a ledger entry"* and filed none, which is exactly `AI-E12-3`/`AI-E12-6` and this story's own `AC12.9`: a disposition recorded in prose and not in the ledger is not a disposition. The entry records the measured size, `MAINT-001-02`/`-03` green with **no `_EXEMPT_BY_DESIGN` entry**, the deliberate refusal to shave below the AC2.2/AC2.4/AC10.1/AC10.2 content, and the trigger: the next change of any size to that module performs the cohesion split FIRST. **Append-only; nothing disposed of** — `DOCS-001-78` re-run against both analyzers (`ledger_closed_ids` has no `DF-15-2-D`; this file yields zero closure claims). **(2) `DN-15-2-2` MOVED INTO THE CODE** it governs (`index_aligned_lines`'s docstring), matching this story's own pattern for `DN-15-2-1`/`-3`/`-4` and AC2.2's *"where the next author will read it"* — ⛔ **and my own rationale was measured OVERSTATED and is recorded as wrong, not quietly repaired:** I claimed the rejected shape (`_score` over `source: str`) would force edits to `-101`..`-112`/`-118`; in fact only **three** pre-existing sites hand `_score` a list they built (`_score_one` in `test_vacuous_density.py:121` and `test_vacuous_cross_language.py:203`, and the direct call in `-93` at `test_vacuous_detector.py:320`), one internal line each, **no `assert` changed**, so AC8.3's literal text was not at stake either way. The decision **stands** on decoupling; the number does not — an overstated rationale defending a correct decision is still the `DF-8-5-C` class. **(3) Nine unfilled `(X)` markers RESOLVED** — three numbered **(1)**/**(2)**/**(3)** as the real series they are in the contract docstring, six dropped; ⛔ `provenance_scan.py:764` and `test_vacuous_detector.py:348` NOT touched (legitimate `pytest.raises(X)` code examples, byte-identical at `72a95ef`); swept for `TODO`/`FIXME`/`XXX`/`TBD`/`(N)`/`<X>`/placeholder across this story's whole `argus`/`tests` delta — **nothing further found**. ⚠️ **The cost, stated not buried:** Finding 2 added **10 lines** to `argus/detectors/vacuous_test.py` — **1,186 → 1,196 of 1,200, headroom 14 → 4** by the ceiling guard's own method. It fits, no exemption was added, no AC-required content was shaved, and **`DF-15-2-D` carries the NEW number**: the fix that resolves one finding is what consumed the headroom the other is about. `argus/pipeline.py` **1,111** and `argus/detectors/secret_scan.py` **575** byte-unchanged; `DF-15-2-B` stays excluded (AC10.1); `DF-14-3-A`/`-B`/`-C` cited, not drifted into; no threshold, corpus, FR34, `protocol_cleared` or `GATE_OUTCOMES` touched. Gates: `pytest` **1645 passed, exit 0** (unchanged — no id added or removed), `mypy argus` **Success, 87 files**. Dogfood currency guards fired on the LOC proxy (29,776 → 29,786) and were re-closed through `AI-E12-11`'s own order: `be3ff0a` → regenerate → `bc4bce9`, no `.md` hand-edited and no assertion loosened (`DF-8-5-B`). **CI matrix GREEN on `bc4bce9`:** run **32221995572** succeeded on `ubuntu-latest` × Python **3.10/3.11/3.12**, run **32221995581** (security shield) succeeded. Status stays `review`. | Dev (dev-story, review fix 1) |
| 2026-08-19 | v1.2 | **Code review iteration 2 (Sonnet) — VERDICT PASS.** Scope `git diff c66a065..79a78cf`. Iteration 1's own re-derivations left undisturbed, confirmed by diff. Independently re-verified: suite **1645 passed, exit 0**; CI green on `bc4bce9` (`32221995572`, `32221995581`, confirmed via `gh run view`); `pipeline.py` **1,111** / `secret_scan.py` **575** byte-unchanged over the whole story. **All three iteration-1 findings confirmed genuinely resolved:** `DF-15-2-D` well-formed, OPEN, `target_story: NONE`, not in `ledger_closed_ids()`, story yields zero closure claims; `DN-15-2-2`'s "three pre-existing sites" re-derived independently and confirmed exact; zero placeholder `(X)` markers remain in `argus`/`tests` (only the two legitimate `pytest.raises(X)` examples survive). Two Low, non-blocking notes recorded for the ledger's own housekeeping, not gating this verdict: the "nine markers" count in the commit message/Completion Notes undercounts by one (actual: 10 touched — 3 numbered + 7 dropped; the resolution is *more* complete than claimed, not less); and `deferred-work.md:5205-5206` (the `DF-15-2-D` entry itself) contains two literal raw CR bytes where escaped `` `\r` ``/`` `\r\n` `` text was clearly intended — no guard reads the file that way (`Path.read_text()` universal-newline-normalises), so it is cosmetic only. **Headroom adjudicated squarely:** `vacuous_test.py` at **1,196/1,200 (4 lines)** is tight and the cost is real, but correctly deferred rather than a defect in this story — `MAINT-001-02`/`-03` is a loud, unavoidable CI gate backing `DF-15-2-D`'s trigger (not a comfortable form of words); placing Fix 2's content in the production docstring rather than the test file was the right call under AC2.2 and §0.15's prohibition on a new shared module; and a production-module cohesion split has no already-named boundary the way the test module's did, so inventing one now would itself be the arbitrary-restructuring failure this project's controls exist to prevent. Status `review` → `done`. | Reviewer (code-review, iteration 2) |
