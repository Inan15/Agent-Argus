---
baseline_commit: 52ae0e5
---

# Story 17.2: A different predicate, argued as one

Status: done

<!-- Contexted 2026-08-25 at HEAD `52ae0e5` (branch `docs/merge-strategy-decision`) by the
     create-story workflow (Opus 5).

     ⛔ THE WORKING TREE IS **NOT** CLEAN AT CONTEXTING, unlike 17.1's. Two artifact files are
     STAGED (`M ` in `git status --porcelain`) by the reviewer that closed 17.1:
     `…/stories/17-1-…-before-the-number-exists.md` and `…/sprint-status.yaml`. This story's
     first commit MUST carry them or explicitly leave them staged — ⛔ **it must not lose them
     and must not sweep them into an unrelated commit.** §2.6 gives the procedure.

     EVERY FIGURE IN SECTION 0 WAS READ OFF THIS TREE BY EXECUTION at `52ae0e5`, not copied
     from `epics.md`, from the 2026-08-24 research, from `deferred-work.md` or from 17.1's
     story record. `argus.detectors.vacuous_test` and `argus.detectors.vacuous_vocabulary`
     were IMPORTED and their tables sized; `silent-class-record.json` was parsed; every
     non-comment reference to `mock_referencing_assertions` under `argus/**` was walked and
     CLASSIFIED; the research harness's own variant definitions were read out of its source;
     the five corpus checkouts were probed for existence; the two declared
     `SUCCESSOR_OUTPUT_PATHS` were probed for absence; byte invariants were counted.

     FOUR PREMISES MOVED AGAINST WHAT THE EPIC ASSUMES, and each is load-bearing:

       (1) SECTION 0.3 — `argus/precision/silent_class.py` ALREADY SHIPS the `V2` half of the
           successor, as `SILENT_CLASS_DEFINITION` + `span_asserts_anything` + `score_span`,
           and `SILENT_CLASS_DEFINITION` ALREADY CONTAINS this story's core argument in its
           own committed words. ⛔ This story CITES it verbatim. It does not re-derive,
           paraphrase or re-declare it. Re-typing it is the `DF-8-5-C` defect and `-144`
           exists to make that impossible.

       (2) SECTION 0.4 — `TC-ArgusAgent-PRECISION-001-127` FENCES `argus/detectors/**` and
           `argus/precision/gate_*` out of `silent_class.py`, transitively, over the whole
           `argus/**` import graph. The successor CANNOT be built in 17.3 by importing the
           shipped V2 scorer from the detector. One import line turns `-127` RED. This is the
           single most expensive thing 17.3 could get wrong and it must be written down here.

       (3) SECTION 0.5 — **`V5` (125) WAS COMPUTED BY THE RESEARCH SCRIPT'S OWN `ast`
           REASONING, NOT BY A SHIPPED HELPER.** Its own docstring says so: *"V5 additionally
           needs SUT-derived name binding, which no shipped helper provides."* `V2` (36) WAS
           measured by shipped code at a different HEAD. **So `36 + 125 = 161` is arithmetic
           across two instruments, not a measurement**, and this story must refuse to publish
           it as one. 17.4 measures the successor's reach. 17.2 does not.

       (4) SECTION 0.6 — `mock_referencing_assertions` has EXACTLY ONE DECISION SITE in the
           whole of `argus/**` (`vacuous_test.py:796`). Every other occurrence is a field
           declaration or an observation carried for a reader. That measured fact — not an
           assumption about the future — is what makes AC3's `DF-INV-VACUOUS-B` disposition
           true TODAY.

     NOTHING HERE RATIFIES A MEMBER, FETCHES A THIRD-PARTY SOURCE, RUNS A DETECTOR OVER ANY
     CORPUS MEMBER, OR SPENDS `DF-13-5-A`'s ROUND. No successor predicate is IMPLEMENTED here
     — 17.3 builds it — and no finding becomes verdict-eligible. `argus/**` is byte-unchanged
     and `scripts/precision_preregistration.py` is FROZEN. -->

## Story

As the **Engineering Lead**,
I want **the successor vacuity signal specified and argued, in a committed record, as a genuinely different predicate**,
so that **it cannot be mistaken for — or later defended as — a loosening of fact (b) by clause removal.**

### What this story IS

`DF-16-7-B` recorded a rule and then stopped short of applying it: *"Promoting V2 would be a
genuinely DIFFERENT predicate, not a loosening of fact (b) by clause removal, **and it must be
argued as one**."* Epic 17's charter repeats it and names the owner: *"Story 17.2 is that
argument."*

This story writes the argument down, in the only order that makes it worth anything: **before
the predicate exists, and immediately after the criterion that will judge it was frozen**
(17.1, `f906d04`). It lands **four artifacts and nothing else**:

1. **`_bmad-output/design-artifacts/ArgusAgent/successor-vacuity-predicate-specification.md`**
   — the committed specification: the successor's definition, the defect shape it claims to
   detect, the **two-directional** differential against the shipped predicate and against
   every clause-removal variant of it, the non-loosening argument stated in terms, and the
   mock-binding decision.
2. **`tests/test_successor_predicate_specification.py`** — three guards
   (`TC-ArgusAgent-PRECISION-001-142`..`-144`) that make the specification's checkable claims
   **falsifiable** rather than asserted.
3. **A dated, append-only disposition of `DF-INV-VACUOUS-B`** in `deferred-work.md` —
   *moot-by-replacement* (AC3), and **that entry only**.
4. **This story's record**, and the two `sprint-status.yaml` transitions.

### What it is NOT

- ⛔ **NOT an implementation.** No detector logic, no scorer, no grading function, no clause,
  no edit anywhere under `argus/**`. **Story 17.3 builds the successor.** §2.1 counts the four
  costs a single `argus/**` byte would spend and §0.4 names the guard it would redden.
  **If a line of this story needs the scorer to exist, that line is in the wrong story.**
- ⛔ **NOT a measurement.** No detector is run over any corpus member, no corpus blob is
  materialised, no research harness is re-executed, and **no successor-predicate output is
  produced or committed**. §1.5 gives the reason in full: 17.4 is chartered to *"run it
  **once**"*, and a story that quietly ran it first would make 17.4's own ordering guard
  argue about a commit nobody planned. Every figure in the specification is **cited from a
  committed artifact with its pin**.
- ⛔ **NOT a tuning of 17.1's criterion.** `scripts/precision_preregistration.py` is **FROZEN**
  and is **not in the write set**. `TC-ArgusAgent-PRECISION-001-140` enforces the
  strengthening-only asymmetry *directionally* against the pinned blob — `POPULATION_ID` and
  `PROTOCOL_VERSION` must be **equal**, the ceiling may only fall and the ratio may only
  rise. ⚠️ **A specification written after the criterion may not move the criterion, and this
  story may not propose that it be moved.** The criterion was written while the answer was
  still zero and it stays there.
- ⛔ **NOT a loosening of `consumed == 0`.** AC2 is the whole of §1.3, and the claim is made
  **checkable** (AC5.3) rather than promised.
- ⛔ **NOT a promotion, and not a proposal to promote.** Nothing becomes verdict-eligible.
  The gate stays `BLOCKED`, `protocol_cleared` stays `False`, the ≥80% keystone stays **NOT
  CLEARED**, FR34's disclosure stands.
- ⛔ **NOT a protocol amendment.** `precision-validation-protocol.md` is **byte-unchanged**.
  No `V1.4` row, no new §5 condition, no terminal state invented. `DN-17-1-2`'s reasoning is
  cited, not re-derived.
- ⛔ **NOT a ledger sweep.** **Exactly ONE** entry is written: `DF-INV-VACUOUS-B`.
  ⛔ `DF-INV-VACUOUS-A`, `DF-16-7-A`, `DF-16-7-B`, `DF-14-1-A`, `DF-12-2-D`, `DF-12-3-A` and
  every `DF-AUD-DETECT-*` entry stay **untouched** — their re-homing and scheduling notes are
  **Story 17.5's**, by name, and splitting that across two stories is how an append-only
  ledger acquires two half-notes (`DN-17-1-9`).
- ⛔ **NOT a spend of `DF-13-5-A`.** No member ratified, no third-party source fetched, no
  round consumed, branch (a) not executed and branch (b) not declared. The entry stays **OPEN
  and UNSPENT**, and its 2026-08-24 trigger is **17.4's** to evaluate, by name.
- ⛔ **NOT a reopening of Epics 1–16 or 18, of Story 6.2, or of any signed retrospective.**

---

## §0 — PREMISES MEASURED BY EXECUTION at HEAD `52ae0e5`

⛔ **Task 0 re-derives every row below before a line is written.** Every figure is cheap to
reproduce — none requires running a detector, materialising a corpus blob or fetching
anything. **A row that does not reproduce is an escalation (AC7), not a number to adjust.**

### §0.0 The tree, the paths, the baseline

| fact | value |
|---|---|
| HEAD | `52ae0e5df79704d02124ae32aa7ecd6d9133d3fc` (`52ae0e5`) |
| branch | `docs/merge-strategy-decision`, **ahead of `origin/master`** |
| 17.1's arc | `72e630d` chore → **`f906d04` feat (the pre-registration commit)** → `4c3a517` docs → `52ae0e5` fix |
| `git status --porcelain` | ⛔ **NOT EMPTY** — two artifact files STAGED (`M `): 17.1's story file and `sprint-status.yaml`. §2.6. |
| artifact root | `_bmad-output/design-artifacts/ArgusAgent/` |
| story location | `…/stories/` (`sprint-status.yaml:6`) |
| next free `PRECISION-001` id | **`-142`** (`-115`..`-134` are Story 16.7's; `-135`..`-141` are 17.1's) |
| CI gates | `mypy argus` · `bandit -r argus --severity-level medium` · `pytest --cov=argus --cov-fail-under=80` (`.github/workflows/audit-ci.yml`) — **none has `scripts/` in scope**; `audit-ci.yml` triggers on `master`/`main` only |
| NFR-M1 | ≤1200 physical lines, population `git ls-files -- '*.py'` — `tests/**` is swept |
| `deferred-work.md` byte invariants | **589,632 bytes · exactly 1 CR byte · 7,489 LF · 0 CRLF.** ⛔ Edit in **binary** mode; a text-mode round-trip eats the lone CR. |
| `sprint-status.yaml` byte invariants | **1,264 lines · 1,264 CR bytes.** Both must be identical after the edit. |

### §0.1 What 17.1 froze, and what this story may not touch

`scripts/precision_preregistration.py` at HEAD, read by import:

```
PREREGISTRATION_COMMIT_SHA = "f906d04997b391bea4592aabc0343d1234b3b060"   # ancestor of HEAD: True
POPULATION_ID              — the five ratified members at their pinned shas
PROTOCOL_VERSION           = "V1.3"
MAX_FALSE_ACCUSATION_EXPOSURE = 26        EXPOSURE_SOURCE_SHA = 6c59115…
SUCCESSOR_OUTPUT_PATHS = ("_bmad-output/design-artifacts/ArgusAgent/validation-corpus/successor",
                          "_bmad-output/audit-reports/successor")
CRITERION_OUTCOMES = {MET, NOT_MET, UNEVALUABLE}
evaluate(...) -> CriterionAssessment      # floors FIRST, then denominator, then ratio ∧ ceiling
```

⛔ **BOTH `SUCCESSOR_OUTPUT_PATHS` ENTRIES ARE ABSENT ON DISK — verified.** That absence is the
subject of `-139`, and it is what makes 17.4's ancestry guard provable.
⛔ **This story creates neither path and writes nothing under either.** If a later story ever
needs to commit successor output, it lands **under one of these two prefixes and nowhere
else** — output committed elsewhere makes 17.4's ordering guard unprovable against the
object database, which is the one thing the epic's BINDING ORDERING CONSTRAINT exists to
prevent.

### §0.2 The shipped predicate, read at HEAD — fact (a), fact (b), and the two tables

`argus/detectors/vacuous_test.py:754`–`:796`, `_ast_corroborated`:

- **fact (a), reachability** — `len(self._sut_call_sites(span_edges)) >= 1`: the span reaches a
  candidate SUT (≥1 non-assertion, non-mock call on the span's edges).
- **fact (b), vacuity** — `evidence.sut_result_is_discarded and evidence.mock_referencing_assertions >= 1`,
  where `evidence` is `provenance_evidence(..., assertion_callees=_CORROBORATION_ASSERTION_CALLEES, mock_callees=_MOCK_CALLEES)`.
- Corroboration is granted **only** when both hold; when either cannot be established it is
  **not** granted. ⛔ **The conservative default IS the moat** (cross-cutting #6).

The two vocabularies, **sized by import at HEAD** (`DN-14-2-1`, the two-table split):

| table | size | used for | direction of harm if widened |
|---|---:|---|---|
| `_CORROBORATION_ASSERTION_CALLEES` **FROZEN** | **23** | the detector's corroboration path — *"does this span corroborate the SUT result?"* | widening moves a test **towards** an accusation |
| `_ASSERTION_CALLEES` **WIDE** + `\A_?assert\w*\Z` | **89** + convention | *"does this span assert anything at all?"* | **narrowing** would score an asserting test as silent — the harm is **REVERSED** |
| `_MOCK_CALLEES` | **10** | mock-call recognition on both paths | — |

⛔ **The successor's `asserts anything` question reads the WIDE table and the corroboration
arithmetic reads the FROZEN one.** That is not an inconsistency; it is `DN-14-2-1` applied to
two questions whose harm points in opposite directions, and `silent_class.span_asserts_anything`
already writes the reasoning out in full. **17.3 must not "unify" them.**

### §0.3 ⛔ THE `V2` HALF OF THE SUCCESSOR ALREADY SHIPS — do not rebuild it

`argus/precision/silent_class.py` (Story 16.7), read at HEAD:

| symbol | what it already is |
|---|---|
| `SILENT_CLASS_DEFINITION` | the `V2` predicate **in the words a promotion proposal would have to defend**, including *"V1 is a SUBSET of V2 and 30 of the 36 lie outside V1 entirely … which no clause removal from fact (b) can ever reach. Promoting V2 would be a genuinely DIFFERENT predicate, not a loosening."* |
| `SpanScore.is_silent_class_member` | `discarded_sut_calls >= 1 and not asserts_anything` — two conjuncts, no threshold |
| `span_asserts_anything(...)` | the WIDE-vocabulary silence question, via `opens_bare_assert` + `is_assertion_callee` |
| `span_provenance(...)` | fact (b)'s **own** arithmetic, FROZEN table — composed, never re-implemented |
| `score_span(...)` | the whole V2 score, calling four shipped helpers and re-implementing none |
| `IDIOMS` / `SILENT_CLASS_ROW_FIELDS` / `SmokeTestProportion` | the human-judgement machinery, already committed |

⛔ **THE SPECIFICATION QUOTES `SILENT_CLASS_DEFINITION` VERBATIM AND DOES NOT PARAPHRASE IT.**
A prose copy of a committed constant is a second source of truth that drifts silently, this
project has already paid for one (`DF-8-5-C`), and `AI-E9-7` forbids it. **`-144` compares the
document's quotation to the imported constant, character for character.**

### §0.4 ⛔ `TC-ArgusAgent-PRECISION-001-127` FENCES THE DETECTOR OUT OF `silent_class.py`

`tests/test_silent_class.py:525` walks **every** `argus/**` module's import graph, resolves it
**transitively**, and asserts that nothing in the fenced set reaches `argus/precision/silent_class.py`:

```
fenced = argus/detectors/**  ∪  argus/precision/gate_*.py
         ∪ {adjudication.py, replay_harness.py, argus/precision/__init__.py}
non-vacuity asserted first: ≥60 modules parsed, ≥12 modules fenced,
                            the target's own known outbound edge resolved
```

Its own words: *"A predicate in the detector package is a promotion waiting for someone to
wire it up."*

⛔ **CONSEQUENCE FOR STORY 17.3, recorded here because 17.2 is where it is cheapest to learn:**
the successor's scorer **cannot** be assembled by importing `silent_class` from
`argus/detectors/**`. One import line turns `-127` RED, and the correct response is **never**
to widen the fence (`DF-8-5-B`). The successor's grading must ship where the detector may
reach it, and the shared helpers it composes (`provenance_evidence`, `opens_bare_assert`,
`is_assertion_callee`, `body_statement_count`) are **already** on the detector side of the
fence — which is exactly why `silent_class` was able to compose them one-way.
⛔ **17.2 takes no decision about the module's path** — that is 17.3's — but §2.2 records the
four costs any new `argus/**` module spends, so 17.3 does not discover them at review.

### §0.5 ⛔ THE VARIANT ARITHMETIC, AND THE TWO INSTRUMENTS IT COMES FROM

Read out of the committed harness `research/investigate-per-call-scoping.py` (its own
docstring and `main()`), and out of the 2026-08-24 research document §5:

| variant | definition, verbatim from the harness | reach | instrument |
|---|---|---:|---|
| `V0` shipped | `disc>=1 AND cons==0 AND mref>=1` | **0** | shipped code |
| `V1` drop-mref | `disc>=1 AND cons==0` | **6** | shipped code |
| `V2` silent | `disc>=1 AND the span asserts NOTHING AT ALL` (WIDE vocab) | **36** | **shipped** `silent_class`, HEAD `b3b761f` |
| `V3` strict | `V1 AND the span asserts nothing at all` | **6** | shipped code |
| `V4` per-call | `disc>=1` alone | **676** | shipped code |
| `V5` unrelated | `disc>=1 AND span HAS assertions AND no assertion references a name bound from a SUT call` | **125** | ⛔ **the script's OWN `ast` reasoning** |

⛔ **`V5` IS NOT A SHIPPED MEASUREMENT.** The harness says so on the line:
*"V5 additionally needs SUT-derived name binding, **which no shipped helper provides**; it is
computed with Python `ast` and is therefore THIS SCRIPT'S OWN reasoning, not the shipped
predicate. Flagged as such in the output."* Two consequences, both load-bearing:

1. **`36 + 125 = 161` IS ARITHMETIC ACROSS TWO INSTRUMENTS AT TWO HEADS, NOT A MEASUREMENT**,
   and the specification must publish it as **provisional, 17.4's to measure**, never as the
   successor's reach. Writing `161` as a measured figure here is the `DF-8-5-C` shape
   committed by the story whose job is to prevent it.
2. **The SUT-derived-name-binding resolver does not exist in `argus/` and Story 17.3 must
   build it.** That is the single largest piece of unbuilt work in Epic 17 and it is what
   `DF-16-7-A` means by *"per-call observation analysis needs real dataflow."*

`V2` and `V5` are **disjoint by definition** — `V2` requires the span to assert nothing, `V5`
requires it to assert something. (`DF-16-7-B`(a) records the boundary moving three rows from
one to the other when `AssertionError` became a recognised assertion callee: 122 → 125.)

⚠️ **A cheap datum the research did not quote, and it is worth naming for 17.4.** The harness
already collects `per_member["V5:{mid}"]` (`:219`) and prints it under *"per-member for the
two live candidates"*. **`V5`'s per-member distribution is one re-run away**, and all five
corpus checkouts were verified **PRESENT** at the paths `CHECKOUTS` names — including
`agent-smith` at the depth-5 path `D:/ProjectX/XAgents/XAgents/XAgents/Agent-Smith`.
⛔ **This story does NOT re-run it** (§1.5). It hands the pointer to 17.4.

### §0.6 ⛔ `mock_referencing_assertions` HAS EXACTLY ONE DECISION SITE IN `argus/**`

Every non-comment reference, walked and classified at HEAD:

| site | kind |
|---|---|
| `argus/detectors/provenance_scan.py:841` | the `ProvenanceEvidence` **field declaration** |
| **`argus/detectors/vacuous_test.py:796`** | ⛔ **THE ONLY DECISION** — `… and evidence.mock_referencing_assertions >= 1` |
| `argus/precision/silent_class.py:232` | a `SpanScore` field, carried *"so a promotion proposal can see it"* |
| `argus/precision/silent_class.py:328` | that field being populated |

**One comparison. One branch. One predicate.** `DF-INV-VACUOUS-B`'s own severity note says the
entry *"becomes load-bearing only if a future predicate depends on mock binding"* — and the
successor specified here does not. **That is why AC3's disposition is true today rather than
a claim about the future**, and `-143` is what keeps it true.

Corroborating figures, from `silent-class-record.json` parsed at HEAD and from the 2026-08-24
research: `mref >= 1` holds in **0 of 1,032**; an extended resolver covering **all four**
dominant Python mock idioms moves that count **0 → 1**; **1,025 of 1,032 (99.3%)** bind no
mock at all by any idiom; and the corpus itself does mock (`agent-smith` 23.2% of test files,
`minions` 22.9%) — *the corpus mocks; the flagged population does not*.

### §0.7 `silent-class-record.json`, parsed at HEAD — the committed `V2` evidence

```
class_size 36     class_by_corpus_member {agent-smith: 22, minions: 14}
files_by_corpus_member {agent-smith: 10, minions: 9}
population_walked 1032   population_skipped 0   protocol_version V1.3
counts {UNADJUDICATED: 36, TP: 0, FP: 0, BORDERLINE: 0}
gates_anything False     promotes_nothing True
exhaustiveness {exhaustive: False, adjudicated_count: 0, residual_count: 36}
smoke_test_proportion.measured False   idiom_counts {NOT_ASSESSED: 36, …: 0}
independence.status NOT_ESTABLISHED
```

⛔ **THE `V2` CLASS IS DERIVED, PUBLISHED AND UNJUDGED.** `DF-16-7-B`(b) is explicit: the
TP/FP/BORDERLINE judgement is an **OPERATOR ACT** no automated producer may take (protocol
§2), the DELIBERATE-SMOKE-TEST proportion — where *"does not raise"* IS the assertion —
remains **NOT MEASURED**, and *"until it is, no promotion proposal for this predicate carries
evidence."* **The specification must carry that sentence forward**, not quietly build on 36
as though it were 36 true positives. **Two contributing members** is also below the resolved
breadth floor of 3 — 17.1 §0.5 pre-registered the consequence (`UNEVALUABLE`) precisely so
nobody has to argue it now.

### §0.8 The detector surface, and what 17.2 does NOT trip

`epic-18-retro-2026-08-25.md` **SD-1** requires every Epic-17 story touching a detector class
to carry the conformance-pin obligation. Re-measured at HEAD:

| landed by 18.4 | measured |
|---|---|
| `Detector` Protocol = `rule_id -> str` + `run -> Callable[..., DetectorResult]`, both read-only `@property` | `argus/detectors/base.py:147`–`:190` |
| `@runtime_checkable` **DELIBERATELY ABSENT** — ⛔ no Epic-17 guard may decide by `isinstance`/`issubclass` | `base.py:176`–`:180` |
| **Four** `if TYPE_CHECKING:` static conformance pins, all inside `argus/` | `orphan_code.py:310`, `secret_scan.py:633`, `tool_runner.py:459`, `vacuous_test.py:799` |
| `TC-ArgusAgent-DETECT-001-145` — every class defining `run() -> DetectorResult` must carry a pin | `tests/test_detector_base.py:224` |
| `TC-ArgusAgent-DETECT-001-146` — the Protocol's measured shape is a FENCE | `tests/test_detector_base.py:257` |

⛔ **This story adds no detector class and edits none, so `-145`/`-146` cannot fire here.**
The obligation is handed to **17.3 by name**: `-145` goes RED from the moment a new class
defining `run() -> DetectorResult` is written until its `if TYPE_CHECKING:` pin lands.

### §0.9 What is already true and must NOT be re-done

- ⛔ **`_STATUS_DOCUMENTS` — do not register the specification.** `TC-ArgusAgent-DOCS-001-22`
  closes in **both** directions: it fails on a globbed file that is unregistered **and** on a
  registered name the globs cannot find. The globs are `sprint-change-proposal-*.md` and
  `epic-*-retro-*.md`; `successor-vacuity-predicate-specification.md` matches neither.
  **Registering it turns `-22` RED** (`DN-17-1-8`, reused not re-derived). ⛔ The document must
  also carry **no undenied phrase from `_STATUS_CLAIMS`** (*"release ready"*, *"production
  ready"*, *"safe to ship"*, …) — it asserts a specification, never a release status.
- ⛔ **`TC-ArgusAgent-DOCS-001-78` is the ledger cross-check and it is already the guard for
  AC3.** It extracts every `DF-*` id a story file claims to have **CLOSED** (line-scoped,
  closure-verb anchored, negation-aware) and requires `deferred-work.md` to carry a matching
  disposition. ⛔ **Do not write a fourth guard for this** — an id-scoped duplicate is an `AR7`
  fork of a guard that already closes in both directions. §2.5 gives the operating rule.
- Guard-RED observations are recorded **automatically** by `tests/conftest.py` into
  `.argus/guard-fires.jsonl` (gitignored). ⛔ **Do not hand-write a fires ledger.**
- The **ruling index** (`architecture.md:1150`) does not exist as a document in this tree.
  ⛔ Do not create it — no guard requires it, `DN-17-1-*` established the precedent that
  `DN-17-2-*` rulings live in this story record, and the additive-only rule points there.
- `scripts/check_meta_drift.py` is **advisory** — not in CI, not in `tests/`.

---

## §1 — THE DECISIONS THIS STORY MAKES, AND WHY

### §1.1 The successor's definition — `S1`, and it is NOT one of `V0`..`V5`

Locked. The successor vacuity predicate is named **`S1`** and is defined over a flagged test
span as **three conjuncts**:

> **(a) REACHABILITY — UNCHANGED.** The span reaches a candidate SUT: ≥1 non-assertion,
> non-mock call on the span's edges. *(Shipped fact (a), byte-for-byte.)*
>
> **(b′) DISCARD — UNCHANGED.** `discarded_sut_calls >= 1`: at least one SUT call's result is
> thrown away. *(Fact (b)'s own arithmetic, through the FROZEN corroboration table.)*
>
> **(c′) NO ASSERTION CONSTRAINS AN SUT-DERIVED VALUE — NEW.** Every assertion in the span
> grades at the weakest band of Story 17.3's committed strength scale — *does not reference an
> SUT-derived value* — **including the degenerate case of a span with no assertions at all.**

⛔ **`S1` IS NOT A MEMBER OF THE `V0`..`V5` FAMILY** and the specification must say so in
terms. `V2` and `V5` are two **disjoint bands of (c′)** measured separately by two different
instruments (§0.5); `S1` is the predicate they are bands of. Naming it `V6` was **rejected**:
the `V` numbers are the research harness's investigation vocabulary, and adopting one would
imply `S1` was measured by that harness. It was not measured at all yet.

**The threshold, stated so it cannot drift:** `S1` requires **every** assertion at the weakest
band. A span carrying a single *constrains only its existence or type* assertion is **NOT**
corroborated by `S1`. ⛔ **Widening `S1` to admit that band is a separate, future act requiring
its own pre-registration** — it is not a tuning knob and this story pre-refuses it, in the
same discipline and for the same reason 17.1 pre-registered its floors.

**The defect shape `S1` claims to detect:** *a test that runs the code under test, throws the
result away, and does not meaningfully constrain what it returned.* That is one definition of
vacuity, and it is the same one **both** stages would then be graded on — which is the
architectural repair `DF-INV-VACUOUS-A` measured the need for.

**Rejected, each recorded in the specification with its reason:**

| rejected successor | why not |
|---|---|
| `V1` — drop the mock clause | Reaches **6**, from **2** members. It is a **clause removal**, which is exactly what the epic forbids, and it leaves the two stages graded on different definitions. |
| `V2` alone — the silent class | Reaches **36** and is already derived, published and **UNJUDGED** (§0.7). It is a **band** of (c′), not the predicate: it cannot see a test that asserts loudly about nothing. |
| `V5` alone — asserts, none about the SUT | The complementary band, and it **cannot see a span that asserts nothing**. Half a predicate, and the half whose 125 is not a shipped measurement. |
| `V4` — `disc >= 1` alone | **676** (65.5%). The research's own word for it is *"too loose"*. It is fact (b) with both remaining clauses removed and no new evidence at all. |
| widen `_mock_bound_names` to all four idioms | ⛔ **Measured: 0 → 1.** `DF-INV-VACUOUS-B` exists *"specifically so the gap is not rediscovered in six months and mistaken for the remedy."* |
| widen the FROZEN corroboration table | ⛔ Measured at **36 → 84** — *"48 false accusations is what the moat is worth here"* (`DF-16-7-B`). It moves tests **towards** accusation. `DN-14-2-1`. |

### §1.2 The differential — stated in BOTH directions, and cited, never re-measured

AC1 asks *"which findings each admits that the other does not."* Against the shipped
predicate the answer is one-sided and must be labelled as such; the argument that carries
weight is against the **clause-removal lattice**.

| comparison | `S1` admits, the other does not | the other admits, `S1` does not | source |
|---|---|---|---|
| vs `V0` **shipped** | everything `S1` admits — `V0` is **empty** | **∅**, and it is empty *by measurement* (0 of 1,032), not by construction | research §2; `silent-class-record.json` |
| vs `V1` **drop-mref** | ⛔ **≥30 findings**, each carrying **≥1 CONSUMED SUT call** (one carries **thirteen**) — findings `cons == 0` **affirmatively excludes**, which **no removal of any subset of fact (b)'s clauses can ever reach while `cons == 0` stands** | **∅** — `V1` ⊂ `V2` ⊆ (c′), measured (`V3 = V1 = 6`) | `SILENT_CLASS_DEFINITION`; `DF-16-7-B` |
| vs `V4` **both clauses removed** | **∅** — `S1` ⊆ `V4` (both require `disc ≥ 1`) | ⛔ **the large majority of `V4`'s 676**, refused by `S1` on **positive new evidence**: those spans *do* constrain the SUT result | research §5 |

⚠️ **The `V4` residual is deliberately written as *"the large majority"* and NOT as a
figure.** `676 − 161 = 515` would be arithmetic across two instruments at two HEADs (§0.5).
**17.4 measures it. The specification records the direction and the reason, and hands the
number to 17.4 by name.**

⛔ **THIS IS THE ARGUMENT, in one sentence:** `S1` is **not on the clause-removal axis at
all** — it admits findings the lattice cannot reach at its tightest and refuses findings the
lattice admits at its loosest, and it does both on evidence fact (b) never computed.

### §1.3 ⛔ `consumed == 0` IS NOT LOOSENED — and the claim is made checkable

AC2 is the most misreadable requirement in the epic, so the specification answers it in four
separate registers rather than one sentence:

1. **Not edited.** `consumed == 0` is not deleted from, weakened in, widened within, or
   re-scoped in **any** shipped module by this story. ⛔ **`argus/**` is byte-unchanged**, and
   AC5.3 proves it against the object database rather than promising it in prose.
2. **Not the route to corroboration.** Where `S1` admits a finding that carries consumed SUT
   calls, it does so on the strength of **new positive evidence** — every assertion in the
   span graded at the weakest band — and **not** on the absence of the clause. That is
   precisely what the epic's *"does not reach corroboration by removing it"* means, and it is
   the difference between `S1` and `V4`.
3. **The moat is preserved by SHAPE, not by that clause.** Cross-cutting #6's moat is two
   things: corroboration requires **positive** AST evidence, and **failure to establish it
   refuses** (`NFR-R1`; the conservative default). `S1` keeps **both**, and 17.3's AC restates
   the second verbatim. What `S1` does not keep is `cons == 0` as a **whole-function-scope
   PROXY** for (c′) — a proxy measured to select a population **disjoint** from the one stage
   1 produces (`DF-INV-VACUOUS-A`: `density_only` 1,025 of 1,032; `both` 0).
4. **Honest about direction.** ⛔ **The specification must state, without hedging, that `S1`'s
   population is LARGER than every clause-removal variant that keeps `cons == 0`** (`V1` = 6).
   Claiming otherwise would be false and would be caught. **The epic's constraint is not that
   the population must be smaller** — it is that the predicate must be *different* and must be
   *argued*, and §1.2 is that argument. **Yield and precision move in opposite directions;
   that is exactly why 17.1's criterion was frozen first, and why 17.4 — not 17.2, and not
   17.3 — decides.**

### §1.4 Mock binding is NOT an input to `S1` — and `DF-INV-VACUOUS-B` is dispositioned

**The decision:** `S1` takes **no** mock-binding input. `_mock_bound_names`,
`mock_referencing_assertions` and the `mref` clause play **no part** in (a), (b′) or (c′).

**The evidence, all of it already committed or measured at HEAD:**

- `mref >= 1` holds in **0 of 1,032** — measured twice, by two independent instruments.
- An extended resolver covering **all four** dominant Python mock idioms moves the count
  **0 → 1** (`DF-INV-VACUOUS-B`, measured, not estimated).
- (c′) needs a **SUT-derived name binding** resolver — a different question from mock binding,
  requiring a resolver that does not exist in `argus/` today (§0.5).
- **§0.6, measured at HEAD:** `mock_referencing_assertions` has **exactly one decision site**
  in `argus/**`. The entry's own load-bearing condition is answered **NO** by a committed
  specification, **today**.

**⇒ `DF-INV-VACUOUS-B` is dispositioned `moot-by-replacement`, dated 2026-08-25, append-only.**

⚠️ **The residual is recorded WITH the disposition, not omitted from it.** Until 17.3 lands
`S1`, the shipped `mref >= 1` clause still stands and the resolver gap still exists — **latent
and harmless**, direction-of-error *under-claiming*, worth a measured 0 → 1. The disposition
does not claim the code changed. It records that **no future predicate will depend on mock
binding**, which is the entry's own stated trigger for ever mattering.

⛔ **What this does NOT do.** It disposes of **no other entry**. `DF-INV-VACUOUS-A` stays
**OPEN** — the stage mismatch is what Epic 17 exists to fix and it is not fixed by a
specification. `DF-16-7-A`, `DF-16-7-B`, `DF-14-1-A`, `DF-12-2-D`, `DF-12-3-A` stay **OPEN and
untouched** (17.5). `DF-13-5-A` stays **OPEN and UNSPENT**.

### §1.5 ⛔ NO MEASUREMENT IS RUN, AND THE REASON IS THE EPIC'S OWN

The temptation is real and cheap: all five checkouts are present, the harness reads pinned
blobs, and one re-run would produce `V5`'s per-member distribution and a first `S1` reach.
**It is refused, on four grounds, and the refusal is recorded in the specification so nobody
has to re-litigate it:**

1. **17.4 is chartered to run it *once*** and to report *"the eligible population, its
   distribution across contributing members and rule classes."* That is 17.4's deliverable,
   by name.
2. **A number produced here would arrive without an adjudication.** `DF-16-7-B`(b): *"until
   [the TP/FP proportion] is [measured], no promotion proposal for this predicate carries
   evidence."* An unadjudicated reach figure is a headline, not evidence.
3. **It would put successor-predicate output in the object database on an unplanned
   commit.** If it is ever committed it must land under `SUCCESSOR_OUTPUT_PATHS` (§0.1),
   and 17.4's ancestry guard should have exactly one arc to reason about.
4. **`AI-E16-7` is UNFILLED** — protocol §4's External adjudicator tie-break. A measurement
   that reaches a borderline before the ladder has a third rung **STOPS**, and that is 17.4's
   stated precondition, not a surprise to discover here.

⚠️ **Recorded as considered-and-declined, with the pointer**, so 17.4 inherits it: the
harness already collects `per_member["V5:{mid}"]` at `investigate-per-call-scoping.py:219`.

### §1.6 What this story does NOT fix, named so it is not mistaken for fixed

- ⛔ `DF-13-5-A` — **OPEN and UNSPENT**. Not evaluated here; **17.4** owns its trigger.
- ⛔ `DF-INV-VACUOUS-A` — **OPEN**. Specifying the replacement is not shipping it.
- ⛔ `DF-16-7-A` (`V5` needs real dataflow), `DF-16-7-B`, `DF-14-1-A`, `DF-12-2-D`,
  `DF-12-3-A` — **OPEN and untouched.** Re-homing notes are **17.5's**.
- ⛔ `DF-AUD-DETECT-C` (unscheduled, `AI-E18-10`) and `-D` (17.3) — untouched.
- ⛔ `AI-E16-7` — **UNFILLED.** 17.2 adjudicates nothing and does not need it; **17.4 does**,
  and the specification restates it as a stated precondition.
- ⛔ The `V2` class's **36 UNADJUDICATED rows** — an **OPERATOR ACT** (protocol §2). No
  automated producer may judge them and this story does not.
- ⛔ The **SUT-derived name binding resolver** — does not exist, and is **17.3's** to build.

---

## §2 — THE COUPLINGS THAT WILL BITE

### §2.1 ⛔ NO `argus/**` BYTE, AND THE REASON IS THE SAME FOUR COSTS 17.1 COUNTED

`DN-17-1-1` measured them and they have not moved:

1. **Dogfood-artifact currency** — *"an artifact is CURRENT iff … `argus/**` has not changed
   since that sha."* Any `argus/**` byte forces `python scripts/regenerate_dogfood_artifacts.py`
   plus its own commit, and `DF-INV-MERGE-A` means a squashed PR reddens `master` afterwards.
2. **`Evidence-partition:` trailer** — `gate_seal.DETECTOR_TUNING_PATHS` is
   `("argus/detectors", "argus/precision/replay_harness.py")`. ⚠️ **A new module under
   `argus/detectors/` DOES trigger it**, and 18.1 lost a sha to a forgotten trailer. **That is
   17.3's obligation, and it is why it is written down here.**
3. **`--cov=argus --cov-fail-under=80`** — a new `argus/` module drags the coverage gate.
4. **`mypy argus` / `bandit -r argus`** — blocking gates over a module that ships in the wheel.

**17.2 spends none of them**: the specification is a document, the guards are under `tests/`,
and the ledger note is an artifact. ⛔ **`git diff <base> HEAD -- argus/` must be EMPTY**
(AC5.3, AC6.3).

### §2.2 The commit arc — THREE commits, and the third is load-bearing

⛔ **`TC-ArgusAgent-DOCS-001-78` closes in both directions**, so the story record's closure
claim and the ledger's disposition **must land in the SAME commit** or CI goes RED. That is
why the arc is what it is. There is no sha to pin here, so 17.1's `PREREGISTRATION_COMMIT_SHA`
problem does not recur, and there is **no dogfood-regeneration commit** (§2.1).

- **Commit O — `chore(17-2): open the successor-predicate specification story`**
  this story file + `sprint-status.yaml` `ready-for-dev` → `in-progress`.
  ⚠️ **The two already-staged artifact files (§0.0) belong to 17.1's close-out, not to this
  story.** Either carry them in this commit **with a message line saying so**, or `git reset`
  their staging and leave them for the peer session. ⛔ **Do not lose them and do not fold
  them silently into a 17.2 commit.**
- **Commit A — `docs(17-2): specify the successor vacuity predicate and argue it as a different predicate`**
  the specification document + `tests/test_successor_predicate_specification.py`.
- **Commit B — `docs(17-2): disposition DF-INV-VACUOUS-B moot-by-replacement; record the 17.2 dev round`**
  the `deferred-work.md` note **and** this story's record **and** the `sprint-status.yaml`
  transition — **together, in one commit** (`-78`).

### §2.3 ⛔ THE GUARDS, AND THE ONE THAT WOULD GO GREEN BY FINDING NOTHING

Two of this story's three guards assert a **negative**. Per the **GUARD-ADEQUACY CLAUSE**
(`architecture.md:1132`, Story 13.2 / AC8.4) each states (i) its observable, (ii) a
demonstration that the defect **moves** that observable — **RED at the REAL SEAM**, not
against a reconstruction — and (iii) at least one adversarial variant **GENERATED** from the
record it closes over, **with its count**:

- a figure-extractor that matches nothing makes `-142` compare an empty set → **the extracted
  figure count is asserted ≥ a floor, and the source artifacts asserted non-empty, FIRST**;
- an AST walk that resolves no reference passes `-143` forever → **the known decision site is
  asserted FOUND before any absence is asserted**;
- `-144` compares a quotation to a constant: **both are asserted non-empty and longer than a
  floor before equality**, or an empty-vs-empty match passes silently.

⛔ **A fourth guard cross-checking `DF-INV-VACUOUS-B`'s disposition was CONSIDERED and
DECLINED**: `TC-ArgusAgent-DOCS-001-78` already does exactly that, over every story file and
every id, with its own non-vacuity floor and its own generated adversarial variants. A
second, id-scoped copy is an `AR7` fork of a working guard.

### §2.4 ⛔ THE LEDGER'S BYTE INVARIANTS AND ITS CLOSURE VOCABULARY

`deferred-work.md` carries **exactly one CR byte** in 589,632 (§0.0). ⛔ **Read and write it in
BINARY mode**; a text-mode round-trip normalises that byte away and produces a 1-byte diff
across a 590 KB file that no reviewer will see. Verify the count before and after.

The ledger writes a closure two ways, **both** of which `ledger_closed_ids` recognises:
inline on the entry's own line, and as a trailing `- status: **CLOSED …**` field under the
entry's id (resolved by carrying the most recent id seen). **`DF-AUD-DETECT-F` at
`deferred-work.md:6838` is the shape to copy**, landed five commits ago.

### §2.5 ⛔ THE CLOSURE-VERB RULE, AND HOW TO SATISFY IT EITHER WAY

`story_closure_claims` is **line-scoped** and anchored to a closure verb
(`CLOSED|Closes|closes|Closed by this story`), negation-aware on the same line. The rule for
this story is therefore mechanical:

- **If** the ledger receives a terminal disposition for `DF-INV-VACUOUS-B` in the vocabulary
  `ledger_closed_ids` recognises, the story record **may** write the closure verb on a line
  naming it — **in the same commit** (§2.2 B), and not before.
- **If** the dev instead lands the weaker *"dispositioned, stays OPEN pending 17.3"* form,
  then ⛔ **no line of this story record may carry a closure verb next to `DF-INV-VACUOUS-B`**,
  and every other `DF-*` mention must read *"stays OPEN"*.
- ⛔ **Either way, no line of this story record may write a closure verb next to any OTHER
  `DF-*` id.** This story closes nothing else.

### §2.6 ⛔ THE TREE IS SHARED, AND TWO FILES ARE ALREADY STAGED

A peer session commits to this same branch. ⛔ **Never `git add -A`.** Stage by **explicit
path** and verify the final write set with `git status --porcelain` against AC6.1 before every
commit.

⛔ **`sprint-status.yaml` is edited SURGICALLY** — one status value per transition, and
`last_updated` only if its value is not already today's date. It carries extensive comment
blocks and a **STATUS DEFINITIONS** block that must survive byte-for-byte, and it must stay at
**1,264 lines / 1,264 CR bytes**. ⛔ **Do not use `sed -i` on it or on any artifact file** —
GNU sed on this host flattens CRLF across the whole file.

### §2.7 The idioms you need, so you do not go looking for them

| need | take it from |
|---|---|
| a specification document that cites constants instead of copying them | `…/successor-predicate-precision-preregistration.md` (17.1) — the `⚠ EVERY VALUE IS CITED BY CONSTANT NAME` preamble |
| a predicate definition written *"in the words a promotion proposal would have to defend"* | `silent_class.SILENT_CLASS_DEFINITION` |
| import a `scripts/` module from a test | `tests/test_candidate_selection.py:52`–`:57` (`sys.path.insert`) |
| a pure git read that never mutates | `tests/test_candidate_selection.py:95`–`:102` (`_git`, `capture_output`, `timeout=120`) |
| an AST walk that classifies references rather than counting strings | `tests/test_silent_class.py:457` (`-126`) and `:525` (`-127`) |
| adversarial variants **generated** from a live record, with a count | `tests/test_governance_record_integrity.py:198` (`-78`) |
| a rule written down where the next author reads it | `gate_seal.SEAL_CITATION_RULE`, `gate_breadth.BREADTH_MEMBER_FLOOR_DERIVATION` |
| a dated, append-only ledger disposition | `deferred-work.md:6838` (`DF-AUD-DETECT-F`) |

---

## §3 — AC ↔ TASK MAP

| AC | what it fixes | tasks | guards |
|---|---|---|---|
| AC1 | the successor is defined, its defect shape stated, the differential given in both directions | 0, 1 | `-142`, `-144` |
| AC2 | `consumed == 0` is not loosened, and the successor does not reach corroboration by removing it | 1 | `-144`, AC5.3 |
| AC3 | the mock-binding decision, and `DF-INV-VACUOUS-B` dispositioned | 2 | `-143`, `-78` |
| AC4 | it measures nothing, ratifies nothing, spends nothing — and says so | 1, 3 | AC5.3 |
| AC5 | three guards, each with an observable and an executed mutation | 3, 4 | all three |
| AC6 | scope, gates and the commit arc | 4 | — |
| AC7 | escalate, do not decide | all | — |

---

## Acceptance Criteria

### AC1 — A COMMITTED SPECIFICATION STATES THE DEFINITION, THE DEFECT SHAPE, AND THE DIFFERENTIAL

**Given** `DF-16-7-B` records that promoting `V2` would be a genuinely DIFFERENT predicate and
that **30 of its 36 rows lie outside `V1` entirely**,
**When** this story completes,
**Then** `_bmad-output/design-artifacts/ArgusAgent/successor-vacuity-predicate-specification.md`
exists, is dated **2026-08-25**, names its author role, and states all of the following:

- **AC1.1** — `S1`'s definition as **three conjuncts**, in §1.1's exact shape: (a)
  reachability **UNCHANGED**, (b′) discard **UNCHANGED**, (c′) *no assertion in the span
  constrains an SUT-derived value*, **including the empty-assertion-set span**.
- **AC1.2** — the **threshold**: every assertion at the weakest band; a single
  *constrains-existence-or-type* assertion **refuses**; widening to admit that band is a
  **separate future act requiring its own pre-registration**.
- **AC1.3** — the **defect shape** `S1` claims to detect, in one sentence: *a test that runs
  the code under test, throws the result away, and does not meaningfully constrain what it
  returned* — and that this is **one** definition of vacuity, on which **both** stages would
  then be graded.
- **AC1.4** — the **differential in BOTH directions**, as §1.2's table: vs `V0` (one-sided,
  and empty **by measurement**), vs `V1` (**≥30** findings carrying **≥1 CONSUMED** SUT call,
  unreachable by any clause removal that keeps `cons == 0`; and **∅** the other way), vs `V4`
  (**∅** one way; the large majority of 676 refused on **positive new evidence** the other).
- **AC1.5** — the **rejected successors** with their reasons: `V1`, `V2` alone, `V5` alone,
  `V4`, widening `_mock_bound_names` (**0 → 1**), widening the FROZEN table (**36 → 84**;
  *"48 false accusations is what the moat is worth here"*).
- **AC1.6** — that `S1` is **NOT** a member of the `V0`..`V5` family, and why the `V6` name was
  rejected.
- **AC1.7** — ⛔ **the instrument provenance of every figure it quotes**, and in particular
  that **`V5` = 125 is the research script's OWN `ast` reasoning, not a shipped measurement**,
  that `V2` = 36 was measured by shipped code at a **different HEAD**, and that therefore
  **`S1`'s reach is NOT stated as a number here** — it is **17.4's to measure**. Any
  provisional arithmetic that appears is labelled **PROVISIONAL** on the line.
- **AC1.8** — that the `V2` class's **36 rows are UNADJUDICATED**, that the TP/FP judgement is
  an **operator act**, that the deliberate-smoke-test proportion is **NOT MEASURED**, and
  `DF-16-7-B`'s sentence: *"until it is, no promotion proposal for this predicate carries
  evidence."*
- **AC1.9** — that the two known bands draw from **two** contributing members, below the
  resolved breadth floor of **3**, and that 17.1 **already pre-registered** the consequence
  (`UNEVALUABLE`). ⛔ The specification **does not argue the floor down** and does not propose
  a bigger bench.
- **AC1.10** — ⛔ the document **quotes `silent_class.SILENT_CLASS_DEFINITION` VERBATIM** and
  attributes it, rather than paraphrasing it (`AI-E9-7` / `DF-8-5-C`).
- **AC1.11** — the constraints handed **forward by name**: `-127`'s one-way fence (§0.4),
  `-145`'s conformance-pin obligation (§0.8), the `Evidence-partition:` trailer (§2.1),
  the missing **SUT-derived name binding resolver** (§0.5) — all **17.3's**; and
  `SUCCESSOR_OUTPUT_PATHS`, `per_member["V5:…"]` and `AI-E16-7` — all **17.4's**.
- **AC1.12** — the document is **NOT** registered in `_STATUS_DOCUMENTS` and contains **no
  undenied `_STATUS_CLAIMS` phrase** (§0.9).

### AC2 — THE `consumed == 0` CLAUSE IS NOT LOOSENED, AND THE SPECIFICATION SAYS SO IN TERMS

**Given** `consumed == 0` is what keeps the false-accusation moat closed,
**Then** the specification states **all four** registers of §1.3, each as its own labelled
clause:

- **AC2.1 — not edited.** The clause is not deleted from, weakened in, widened within or
  re-scoped in any shipped module by this story; **`argus/**` is byte-unchanged**, proved by
  AC5.3.
- **AC2.2 — not the route to corroboration.** Where `S1` admits a finding carrying consumed
  SUT calls it does so on **new positive evidence**, not on the clause's absence — *"does not
  reach corroboration by removing it"*, and this is what separates `S1` from `V4`.
- **AC2.3 — the moat is preserved by shape.** Corroboration still requires **positive** AST
  evidence and **failure to establish still refuses** (`NFR-R1`, cross-cutting #6). What is
  not preserved is `cons == 0` as a **whole-function-scope PROXY** for (c′) — a proxy measured
  (`density_only` **1,025 of 1,032**, `both` **0**) to select a population **disjoint** from
  stage 1's.
- **AC2.4 — honest about direction.** ⛔ The specification states **without hedging** that
  `S1`'s population is **larger** than every clause-removal variant that keeps `cons == 0`,
  that yield and precision move in **opposite** directions, and that **17.4 — not 17.2 and not
  17.3 — decides**, against a criterion frozen at `f906d04` before any of this existed.
- **AC2.5 — advisory until an operator says otherwise.** The specification states that `S1`
  landing in 17.3 makes **nothing verdict-eligible**; 17.1's `CONSEQUENCE_MET` is explicit
  that meeting the criterion *"promotes nothing"* and produces a **proposal**. ⛔ 17.3 must
  land `S1` such that no finding's `verdict_eligible` flips on it within Epic 17.

### AC3 — THE MOCK-BINDING QUESTION IS ANSWERED, AND `DF-INV-VACUOUS-B` IS DISPOSITIONED

**Given** the mock-referencing clause fires **0 times in 1,032**,
**Then**:

- **AC3.1** — the specification **records the decision explicitly**: mock binding is **NOT** an
  input to `S1`; `_mock_bound_names`, `mock_referencing_assertions` and the `mref` clause play
  no part in (a), (b′) or (c′) — with §1.4's four pieces of evidence, including the
  **single-decision-site** measurement re-derived at HEAD.
- **AC3.2** — `deferred-work.md` carries a **dated (2026-08-25), append-only** disposition of
  `DF-INV-VACUOUS-B` as **`moot-by-replacement`**, naming this story, in the shape of
  `DF-AUD-DETECT-F` at `:6838`. ⛔ **The entry above it is NOT rewritten** (§3.4 — strike,
  never erase).
- **AC3.3** — the note **records the residual with the disposition**: the shipped `mref >= 1`
  clause stands until 17.3, the resolver gap is **latent and harmless** (direction of error:
  under-claiming; worth a measured **0 → 1**), and the disposition rests on the entry's **own**
  stated trigger being answered NO — **not** on a claim that the code changed.
- **AC3.4** — ⛔ **NO OTHER LEDGER ENTRY IS TOUCHED.** `DF-INV-VACUOUS-A`, `DF-16-7-A`,
  `DF-16-7-B`, `DF-14-1-A`, `DF-12-2-D`, `DF-12-3-A`, every `DF-AUD-DETECT-*` and `DF-13-5-A`
  stay exactly as they stand. Verified by `git diff` hunk inspection (AC6.1).
- **AC3.5** — the story record and the ledger **agree**, in the **same commit**, per §2.5's
  two-branch rule. `TC-ArgusAgent-DOCS-001-78` is the guard and it is not duplicated.

### AC4 — IT MEASURES NOTHING, RATIFIES NOTHING, SPENDS NOTHING — AND SAYS SO

**Given** `DF-13-5-A` is OPEN and UNSPENT,
**Then** the specification states in terms, each as its own sentence:

- **AC4.1** — **no detector is run** over any corpus member, **no corpus blob is
  materialised**, **no research harness is re-executed**, and **no successor-predicate output
  is produced or committed** — with §1.5's four reasons recorded so the refusal is not
  re-litigated.
- **AC4.2** — **no corpus member is ratified.** `eligible_member_count()` is **5** before and
  **5** after.
- **AC4.3** — **no third-party source is fetched.** Nothing reaches the network.
- **AC4.4** — **no round is spent.** `DF-13-5-A` stays **OPEN and UNSPENT**; branch (a) not
  executed, branch (b) not declared; its 2026-08-24 trigger is **17.4's** to evaluate.
- **AC4.5** — **no protocol row is added**, no §5 condition created, no terminal state
  invented; `precision-validation-protocol.md` is **byte-unchanged**; `PROTOCOL_VERSION` stays
  **V1.3**.
- **AC4.6** — ⛔ **17.1's criterion is NOT MOVED.** `scripts/precision_preregistration.py` is
  **byte-unchanged**; `POPULATION_ID`, `PROTOCOL_VERSION`, the resolved ratio floor and
  `MAX_FALSE_ACCUSATION_EXPOSURE` are identical at the `f906d04` pin, so `-140` stays green.
  ⛔ The specification **does not propose** that any of them be moved.
- **AC4.7** — **no FR is amended**, **no finding becomes verdict-eligible**, **nothing
  published changes**, and the gate stays `BLOCKED` with FR34's disclosure standing.

### AC5 — THREE GUARDS, EACH WITH AN OBSERVABLE AND AN EXECUTED MUTATION

**Given** the **GUARD-ADEQUACY CLAUSE** (`architecture.md:1132`),
**Then** `tests/test_successor_predicate_specification.py` commits **exactly three** guards,
each discharging (i) observable, (ii) RED **at the real seam** by an **executed** mutation,
(iii) an adversarial variant **generated** from a live record **with its count**, in its own
docstring:

- **AC5.1 — `TC-ArgusAgent-PRECISION-001-142` — the specification's figures RE-DERIVE from the
  committed artifacts.** *Observable:* every numeric figure the document attributes to a
  committed artifact, extracted by a **pure, exported analyzer**, compared to
  `silent-class-record.json` (`class_size`, `class_by_corpus_member`, `files_by_corpus_member`,
  `population_walked`, `population_skipped`, `counts`) and to
  `silent_class.SILENT_CLASS_DEFINITION`'s own figures. *Non-vacuity FIRST:* the extractor must
  return **at least a stated floor** of figures and the artifacts must parse non-empty, or the
  comparison observes nothing. *Adversarial, GENERATED with a count:* every extracted figure is
  perturbed and the comparison must **reject each one**. *Mutation:* change one figure in the
  document → RED.
- **AC5.2 — `TC-ArgusAgent-PRECISION-001-143` — the mock-binding decision rests on a measured
  fact.** *Observable:* an `ast` walk over **every** `argus/**` module collecting each
  reference to `mock_referencing_assertions` and **classifying** it — a comparison / boolean
  decision, versus a field annotation or keyword-argument carry. The claim: **exactly one
  decision site**, in `argus/detectors/vacuous_test.py`. *Non-vacuity FIRST:* the walk must
  parse a floor of modules **and must resolve the KNOWN decision site**, or *"no other decision
  site"* is a broken walk reporting silence. ⛔ **It must classify AST nodes, not count string
  occurrences** — a substring counter is a guard over the shape of the input, not its effect
  (the GUARD-ADEQUACY CLAUSE's input-side twin). ⛔ **No `isinstance`/`issubclass` decision
  against a Protocol** (18.4 / AC5.4). *Mutation:* plant a second comparison in a real
  `argus/**` module → RED; restore **byte-exact, sha256-verified**.
- **AC5.3 — `TC-ArgusAgent-PRECISION-001-144` — the specification QUOTES the committed
  definition and the moat's arithmetic did not move.** *Observable, two halves:* (1) the
  document's `SILENT_CLASS_DEFINITION` quotation compared **character for character** to the
  imported constant; (2) `git log <base>..HEAD -- argus/` is **EMPTY** — the `consumed == 0`
  arithmetic and everything around it are untouched by this story's arc. *Non-vacuity FIRST:*
  the constant and the quotation are both asserted non-empty and above a length floor; and a
  **control path known to carry commits in the same range** is asserted **non-empty** — a
  misspelled or moved pathspec returns empty and is **indistinguishable from a clean tree**
  (`-75`/`-139`'s answer, reused verbatim, not re-invented). *Mutation:* alter one character
  of the quotation → RED.
- **AC5.4** — every guard is **PURE** except for read-only `git` verbs, carries its
  `TC-ArgusAgent-…` id in its name and first docstring line, and runs in the default suite. ⛔
  **No new area id is opened** — `PRECISION-001` continues at `-142`.
- **AC5.5** — ⛔ **a guard is never weakened to go green** (`DF-8-5-B`). If a guard is RED
  because the specification is wrong, the specification is fixed.

### AC6 — SCOPE, GATES AND THE COMMIT ARC

- **AC6.1 — the write set is EXACTLY:** the specification document ·
  `tests/test_successor_predicate_specification.py` · the `DF-INV-VACUOUS-B` note in
  `deferred-work.md` · this story file · `sprint-status.yaml`. ⛔ **Nothing else**, verified by
  `git status --porcelain` and by `git diff --stat` before each commit. ⛔ The two artifact
  files staged at contexting are handled per §2.2 and are **not** silently absorbed.
- **AC6.2 — `argus/**` is byte-unchanged**, so there is **no `code_identity` movement, no
  dogfood-artifact regeneration, no `Evidence-partition:` trailer obligation** and no effect on
  `--cov=argus --cov-fail-under=80`.
- **AC6.3 — proved, not asserted:** `git diff <base> HEAD -- argus/ scripts/ _bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md _bmad-output/design-artifacts/ArgusAgent/E-PRD/ _bmad-output/design-artifacts/ArgusAgent/architecture.md _bmad-output/design-artifacts/ArgusAgent/epics.md _bmad-output/design-artifacts/ArgusAgent/validation-corpus/`
  is **EMPTY**, with the output recorded in the Dev Agent Record.
- **AC6.4 — every gate, every exit code, recorded:** full `pytest` (exit 0, pass count, no
  `F`/`E` markers) · `tests/test_successor_predicate_specification.py` · `-127` · `-140` ·
  `-22` · `-78` · `mypy argus` · `bandit -r argus --severity-level medium` ·
  coverage ≥80% · NFR-M1 sweep. ⚠️ **These are LOCAL (Windows) and must be labelled so** —
  `audit-ci.yml` triggers on `master`/`main` only, this branch is unpushed, and CI runs an
  **ubuntu matrix** a green Windows suite has previously failed to predict (`AI-E13-1`; epic-18
  retro SD-4).
- **AC6.5 — the three-commit arc of §2.2**, with the ledger note, the story record and the
  `sprint-status.yaml` transition **together in commit B** (`-78`).
- **AC6.6 — byte invariants verified after every artifact write:** `deferred-work.md` **1 CR**;
  `sprint-status.yaml` **1,264 lines / 1,264 CR**.
- **AC6.7 — no `git add -A`.** Explicit paths only; the tree is shared.

### AC7 — ESCALATE, DO NOT DECIDE

**Given** this story's whole value is that it argues honestly rather than conveniently,
**Then** the dev **STOPS and escalates in the story record** — it does not adjust a number, a
threshold or a claim — if any of the following is observed:

- **AC7.1** — any §0 row fails to reproduce at HEAD.
- **AC7.2** — `git log <base>..HEAD -- argus/` is non-empty, or `scripts/precision_preregistration.py`
  differs from its `f906d04` pin in any frozen field.
- **AC7.3** — a **second** decision site for `mock_referencing_assertions` is found in
  `argus/**`, which would falsify AC3's basis outright.
- **AC7.4** — the ledger's closure vocabulary cannot express `moot-by-replacement` without
  either rewriting the entry above it (§3.4) or making a claim the tree does not support. ⛔
  **Land the weaker §2.5 form and escalate; do not invent a fifth disposition.**
- **AC7.5** — the specification cannot be written without either running a measurement
  (§1.5) or publishing an unmeasured figure as measured (AC1.7).
- **AC7.6** — `argus/**` or the protocol document turns out to need an edit for any AC to hold.

---

## Dev Notes

### Decisions this story TAKES, each with its rejected alternative

- **`DN-17-2-1` — the successor's definition has EXACTLY ONE authoritative declaration, and it
  is NOT in this story.** The specification is prose that **cites**; the definition-as-code
  ships where 17.3 ships it, inside `argus/`. *Rejected:* a `scripts/successor_predicate_spec.py`
  in 15.1/17.1's frozen-module house form. It reads right — until 17.3 declares the same scale
  inside `argus/` and the repository has two, which is the `AR7` defect and `DF-8-5-C`'s exact
  shape. **17.1's module could be frozen in `scripts/` because nothing else would ever declare
  a precision criterion. A grading scale is different: it must ship.**
- **`DN-17-2-2` — the successor is named `S1`, not `V6`.** *Rejected:* extending the research
  harness's `V` series, which would imply `S1` was measured by that harness. It was not
  measured at all yet, and §0.5 is why that distinction is load-bearing.
- **`DN-17-2-3` — `S1` is `V2 ⊎ V5` as BANDS of one new conjunct, not either variant alone.**
  *Rejected:* `V2` alone (blind to a test that asserts loudly about nothing) and `V5` alone
  (blind to a span that asserts nothing). Each is half of (c′), and picking one would reproduce
  the stage mismatch `DF-INV-VACUOUS-A` measured, one level down.
- **`DN-17-2-4` — `S1`'s reach is NOT stated as a number.** *Rejected:* publishing `161`.
  `V2`'s 36 is a shipped measurement at HEAD `b3b761f`; `V5`'s 125 is the research script's own
  `ast` reasoning at a different HEAD. Their sum is arithmetic across two instruments, and the
  story chartered to prevent a number being fitted to a standard may not publish one that was
  never measured. **17.4 measures it.**
- **`DN-17-2-5` — the threshold is `every assertion at the weakest band`, and widening it is
  pre-refused.** *Rejected:* admitting *constrains only existence or type* now, "to get a
  useful population". That is a yield decision taken by the story with no measurement, against
  a criterion frozen four commits ago. It is exactly the move 17.1 exists to prevent.
- **`DN-17-2-6` — no measurement is run, even though it is cheap and all five checkouts are
  present.** *Rejected:* one re-run of `investigate-per-call-scoping.py` for `V5`'s per-member
  distribution. §1.5's four reasons; the pointer is handed to 17.4 instead.
- **`DN-17-2-7` — AC2 is answered in four registers, and the fourth is an admission.** *Rejected:*
  arguing that `S1`'s population is somehow not larger than `V1`'s. It **is** larger, by a lot,
  and a specification that fudges that is the one document in this epic that must not.
  The epic's constraint is *different and argued*, not *smaller*.
- **`DN-17-2-8` — exactly ONE ledger entry is written, and it is dispositioned with its
  residual attached.** *Rejected:* a clean *"CLOSED, superseded"* with no residual (claims the
  code changed; it did not), and *"leave it OPEN"* (the epic's AC says otherwise, and the
  entry's own trigger is now answered).
- **`DN-17-2-9` — three guards, and the fourth was declined as an `AR7` fork of
  `TC-ArgusAgent-DOCS-001-78`.** *Rejected:* an id-scoped ledger cross-check for
  `DF-INV-VACUOUS-B`. `-78` already checks in **both** directions, with its own non-vacuity
  floor and its own generated adversarial variants.
- **`DN-17-2-10` — the specification is not registered in `_STATUS_DOCUMENTS`.** *Rejected:*
  registering it "for safety" — `-22` closes in both directions and would go RED (`DN-17-1-8`,
  cited not re-derived).

### Locked decisions this story CITES rather than reopens

`DN-3` (one floor, never forked) · `DN-4` (pin by commit) · **`DN-14-2-1`** (the two-table
split; the frozen corroboration table — §0.2) · **`DN-16-7-1`** (the silent-class record lives
at its own address; the committed adjudication record is byte-unchanged) · **`DN-16-7-2`** (the
idiom axis is orthogonal to the disposition; `DISPOSITIONS` is closed at four) ·
`DN-16-4-2` / `AI-E9-7` (constants imported, never re-typed; no prose copy of a pinned
constant) · **`DN-17-1-1`** (the four costs of an `argus/**` byte) · **`DN-17-1-2`** (no
protocol amendment; V1.3 is named, not created) · **`DN-17-1-5`** (the criterion judges the
predicate, not the gate) · **`DN-17-1-6`** (strengthening-only asymmetry) · **`DN-17-1-8`**
(`_STATUS_DOCUMENTS`) · **`DN-17-1-9`** (`deferred-work.md` writes belong to the story the epic
assigns them to) · §3.4 evidence immutability (strike, never erase) · the OI1 lock (protocol
§7) · cross-cutting #6 (advisory-by-contract; the conservative default IS the moat) · `AR4`
(no floats; counts, never rendered sets) · `AR7` (one derivation per question) · `AR8` (pure) ·
`NFR-D2` · `NFR-R1` · `NFR-M1` (≤1200) · `NFR-S1` · `DF-8-5-B` (a guard is never weakened to go
green) · `AI-E9-8` (recording is the story's, filing is the operator's) · `AI-E11-1` (an
absence is evidence only over a population proved non-empty) · `AI-E12-6` (a claimed closure
the ledger never received fails CI).

### Open ledger entries bearing on this story — verify against `deferred-work.md` on disk

| entry | state at contexting | bearing |
|---|---|---|
| `DF-INV-VACUOUS-B` | **OPEN**, 🟡 latent, `target_story` **NONE yet** — *"it rides with whatever story reworks the predicate"* | ⛔ **THE ONE ENTRY THIS STORY WRITES.** Dispositioned `moot-by-replacement` (AC3). |
| `DF-INV-VACUOUS-A` | **OPEN**, 🟠 | The measured reason Epic 17 exists. Specifying the replacement does not fix the mismatch. ⛔ **Untouched.** |
| `DF-16-7-B` | **OPEN**, 🟠 | Source of *"a genuinely DIFFERENT predicate … must be argued as one"*, of `V1 ⊂ V2` / 30-outside, and of the 36 → 84 / **48 false accusations** figure. ⛔ **Cited, not written.** Its re-homing is 17.5's. |
| `DF-16-7-A` | **OPEN** | *"per-call observation analysis needs real dataflow"* — the SUT-derived-binding resolver 17.3 must build. ⛔ Untouched. |
| `DF-14-1-A`, `DF-12-2-D`, `DF-12-3-A` | **OPEN** | Re-homing is **17.5's**. ⛔ Untouched. |
| `DF-13-5-A` | **OPEN, UNSPENT.** Declined twice; trigger sharpened 2026-08-24 to *"shipped promotions rise above ZERO"*; backstop **2026-11-22** | ⛔ Neither spent nor evaluated here. **17.4** evaluates the trigger. |
| `DF-AUD-DETECT-C` | **OPEN**, unscheduled (`AI-E18-10`) | ⛔ Untouched. |
| `DF-AUD-DETECT-D` | **OPEN**, scheduled on **17.3** | ⛔ Untouched. |
| `DF-8-5-C` | historical; not open, and this story claims nothing about it | The defect class `-142`/`-144` exist to prevent: a prose copy of a pinned constant drifting. |
| `AI-E16-7` | **UNFILLED** — protocol §4's External adjudicator tie-break | Not needed here (nothing is adjudicated); **needed by 17.4**, and restated as a precondition. |

### Dependencies — none are added, and that is a requirement

No new third-party dependency, no `pyproject.toml` edit, no lockfile change. The guard module
adds `ast`, `json`, `re`, `subprocess`, `pathlib`, `hashlib` — all already used by
`tests/test_silent_class.py`, `tests/test_candidate_selection.py` and
`tests/test_governance_record_integrity.py`.
⚠️ **No web research is warranted for this story and none was performed.** Nothing here
depends on a library version, an external API or a framework release; the stack is CPython
3.11–3.13 with `pytest`, `mypy` and `bandit`, all pinned by `pyproject.toml`, and none is on
the path this story touches. **Recorded as considered-and-declined rather than skipped**
(17.1 recorded the same, for the same reason).

### Standing rules (non-negotiable)

1. **The guards may shell out to `git` for read-only verbs. Nothing else here does I/O beyond
   reading committed files.**
2. **Counts, never rendered sets** (`NFR-D2` / `AR4`). **No floats**; exact `Fraction` if a
   ratio is ever written, which it should not be here.
3. **No source bytes, no secret values, no exception text, no host paths** in any committed
   artifact (`NFR-S1`). ⚠️ §0.5 names the corpus checkout paths **in this story record only**,
   for reproduction; ⛔ **they do not go into the specification document.**
4. **A negative is only evidence if the population was proved non-empty first** (`AI-E11-1`).
5. **§3.4:** nothing already committed is rewritten. Corrections are dated additions.
6. **`DF-8-5-B`:** a guard is never weakened to go green.
7. **A figure is cited with the instrument that produced it and the HEAD it was produced at**,
   or it is not written down.

### Previous-story intelligence

**Story 17.1 is the immediate predecessor and it is `done`** (arc `72e630d` → `f906d04` →
`4c3a517` → `52ae0e5`; review iteration 2, VERDICT **pass**, Sonnet 5). What carries forward:

- **The §0-before-a-line-is-written discipline.** 17.1's §0 moved **three** premises against
  what the epic assumed, and each was load-bearing. §0 here moved **four**. ⛔ Task 0 is not a
  formality.
- **⛔ 17.1's ONE review finding was an UNANCHORED WHOLE-DOCUMENT REGEX.** `protocol_change_log_head`
  scanned the whole protocol document with an unanchored pattern; a same-shaped row planted
  above the `## Change log` heading resolved the **wrong** row and `refuse_protocol_drift`
  returned **silently**. It was fixed **by deletion** — routed through the one existing
  anchored derivation (`DN-17-1-15`, `AR7`). ⚠️ **`-142` extracts figures from a markdown
  document. Anchor the extraction — to a labelled table, a fenced block or an explicit marker
  — and drive an adversarial decoy through it.** This is the same defect class, one story
  later, in the same area id.
- **The `scripts/` placement decision and its four costs** (`DN-17-1-1`) — reused verbatim as
  §2.1, and it is why 17.2 writes no `argus/**` byte.
- **A commit cannot contain its own sha** (`DN-17-1-7`) — **does not recur here**; 17.2 pins no
  sha, so the arc is three commits for a different reason (§2.2, the `-78` co-location).
- **From 18.1** — a `feat` commit lost a sha to a **forgotten `Evidence-partition:` trailer**.
  17.2's answer is the same as 17.1's: stay out of `DETECTOR_TUNING_PATHS` entirely. ⚠️ **17.3
  cannot**, and §2.1 says so.
- **From 18.4** — the pattern of a story that lands a **contract plus its enforcing guard**;
  and SD-1's detector-contract obligations, re-measured as §0.8.
- **From 16.7** — the whole shape of the artifact this story specifies: a predicate published
  **as a question for a human**, with `gates_anything: False` and `promotes_nothing: True` on
  the record itself, and a one-way import fence (`-127`) proving it cannot be wired up by
  accident.
- **From 16.4** — a story may legitimately **HALT on an operator act** and be answered. AC7 is
  shaped that way deliberately.

### Git intelligence

```
52ae0e5 fix(17-1): resolve the change-log head through the one existing derivation
4c3a517 docs(17-1): record the pre-registration commit and the dev round
f906d04 feat(17-1): pre-register the successor-predicate precision criterion   <- the pin
72e630d chore(17-1): open the pre-registration story
c2ce00f Merge origin/master into docs/merge-strategy-decision
```

Read off that arc and applied above: 17.1's **three-part convention**
(`chore` open → `feat`/`docs` land → `docs` record) is kept, with the third commit's contents
**re-composed** so the ledger note and the story record are co-located (§2.2, `-78`).
⚠️ The branch is **ahead of `origin/master`** and `audit-ci.yml` triggers on `master`/`main`
only, so **no CI evidence is available for this work at its own sha**; every gate claim is
**LOCAL (Windows)** until it is green at a pushed sha (`AI-E13-1`; epic-18 retro SD-4). ⚠️ **CI
runs an ubuntu matrix and a green local suite has previously shipped POSIX-only defects.**

### References

- `…/epics.md:3400`–`3489` — Epic 17 charter, the `consumed == 0` constraint, the BINDING
  ORDERING CONSTRAINT, the operator approval, and Story 17.2's three ACs (`:3517`–`:3535`)
- `…/stories/17-1-write-down-what-would-count-as-precision-before-the-number-exists.md` —
  `DN-17-1-1`..`-15`, §0.4 (`sealed ∩ ratified = ∅`), §0.5 (both candidates at 2 members),
  §0.6 (26 FP of 31), §2.1–§2.7
- `…/successor-predicate-precision-preregistration.md` — §2 (the criterion), §3.1 (it judges
  the predicate, not the gate), §3.3 `CONSEQUENCE_BELOW`, §3.4 `CONSEQUENCE_MET`, §3.5
  (`AI-E16-7`), §4 (what the act does not do), §5 (hand-off to 17.4)
- `…/sprint-change-proposal-2026-08-24.md` `:158` (*"Story 17.2 is that argument"*), `:176`
  (the per-story table)
- `…/research/technical-argusagent-stage-mismatch-measurement-2026-08-24.md` §2 (clause counts,
  per-member table), §3 (the resolver gap, 0 → 1), §4 (the two stages, `density_only` 1,025),
  §5 (the `V0`..`V5` table and the two charter constraints), §6 (reproduction)
- `…/research/investigate-per-call-scoping.py` — the variant definitions in its own docstring
  (`:9`–`:24`), `CHECKOUTS` (`:55`), `per_member["V5:…"]` (`:219`)
- `…/deferred-work.md` — `DF-16-7-B` (`:6114`), `DF-INV-VACUOUS-A` (`:6189`),
  `DF-INV-VACUOUS-B` (`:6238`), the `DF-AUD-DETECT-F` closure shape (`:6838`), the re-homing
  roll-up table (`:7052`–`:7054`)
- `…/precision-validation-protocol.md` §2 (roles; `UNADJUDICATED` is the only member an
  automated producer may write), §4 (the ladder; step 3 unfilled), §5 (the conditions; *"a §5
  condition that cannot fail is not a threshold"*), §7 (OI1)
- `…/epic-18-retro-2026-08-25.md` **SD-1** (§0.8), **SD-2** (Epic 17's premise survived),
  **SD-4** (evidence is local/unpushed), §11 (Epic-17 prep table)
- `…/architecture.md:1132` **GUARD-ADEQUACY CLAUSE** and its input-side twin · `:1140`
  **Ledger-claim cross-check** · `:1150` **Ruling-index** (additive; do not create the index)
- `argus/detectors/vacuous_test.py:754`–`:796` (`_ast_corroborated`), `:799` (the conformance
  pin) · `argus/detectors/vacuous_vocabulary.py` (`_ASSERTION_CALLEES` 89,
  `_CORROBORATION_ASSERTION_CALLEES` 23, `_MOCK_CALLEES` 10) ·
  `argus/detectors/provenance_scan.py:794` (`_mock_bound_names`), `:841`, `:905` ·
  `argus/detectors/base.py:147`–`:190`
- `argus/precision/silent_class.py:106` (`SILENT_CLASS_DEFINITION`), `:217`–`:333`
  (`SpanScore`, `span_asserts_anything`, `span_provenance`, `score_span`), `:137` (`IDIOMS`)
- `argus/precision/gate_seal.py:280` (`DETECTOR_TUNING_PATHS`)
- `scripts/precision_preregistration.py:500` (`SUCCESSOR_OUTPUT_PATHS`), `:518`
  (`PREREGISTRATION_COMMIT_SHA`), `:617` (`evaluate`)
- `tests/test_silent_class.py:457` (`-126`), `:525` (`-127`) ·
  `tests/test_precision_preregistration.py:852` (`-139`) ·
  `tests/test_governance_record_integrity.py:40`–`:96` (the analyzers), `:198` (`-78`) ·
  `tests/test_status_document_registry.py:78`, `:461`–`:500` (`-22`) ·
  `tests/test_detector_base.py:224`, `:257` · `tests/test_module_size_ceiling.py:68`
- `…/validation-corpus/silent-class-record.json` · `…/validation-corpus/silent-class-worklist.md`
- `…/E-PRD/prd.md` — FR10 (advisory vacuous-test detector), FR7 (AST grounding), FR34 (the
  disclosure), the ≥80% keystone (`:173`, `:190`)

---

## Tasks & Subtasks

### ⛔ Task 0 — RE-MEASURE §0 BEFORE WRITING ANYTHING (AC1.7, AC4.*, AC7)

- [x] **0.1** Confirm HEAD, branch, and record `git status --porcelain` **verbatim**. ⛔ Note
      the two staged artifact files and decide their handling per §2.2 **before** committing
      anything.
- [x] **0.2** Re-derive §0.1: import `scripts/precision_preregistration.py`; confirm
      `PREREGISTRATION_COMMIT_SHA` resolves and is an ancestor of HEAD; confirm **both**
      `SUCCESSOR_OUTPUT_PATHS` entries are **absent** on disk.
- [x] **0.3** Re-derive §0.2 by **import**: `len(_CORROBORATION_ASSERTION_CALLEES)`,
      `len(_ASSERTION_CALLEES)`, `len(_MOCK_CALLEES)`, and read `_ast_corroborated`'s return
      expression.
- [x] **0.4** Re-derive §0.3 by **import**: `SILENT_CLASS_DEFINITION`,
      `SpanScore.is_silent_class_member`'s expression, and the four helpers `score_span` calls.
- [x] **0.5** Re-run `TC-ArgusAgent-PRECISION-001-127` and record it **green**; confirm the
      fenced-set size and the parsed-module count.
- [x] **0.6** Re-derive §0.5 from the harness **source** (do **not** execute it): the six
      variant definitions, the `V5`-is-the-script's-own-reasoning sentence, `CHECKOUTS`, and
      the `per_member["V5:…"]` collection site.
- [x] **0.7** Re-derive §0.6: walk `argus/**` with `ast`, classify every
      `mock_referencing_assertions` reference, and confirm **exactly one decision site**.
      ⛔ **AC7.3 if a second is found.**
- [x] **0.8** Parse `silent-class-record.json` and confirm every §0.7 figure.
- [x] **0.9** Re-derive §0.8's five detector-surface rows and §0.0's byte invariants.
- [x] **0.10** Record every row in the Dev Agent Record with the command that produced it.
      ⛔ **A row that does not reproduce is AC7, not a number to adjust.**

### Task 1 — THE SPECIFICATION (AC1, AC2, AC4)

- [x] **1.1** Write `…/successor-vacuity-predicate-specification.md`: dated **2026-08-25**,
      author role named, in the pre-registration document's house form (a *"values are cited,
      never copied"* preamble; a reproduction command beside every cited figure).
- [x] **1.2** §"The predicate": AC1.1, AC1.2, AC1.3, AC1.6 — the three conjuncts, the
      threshold and its pre-refused widening, the defect shape, and why `S1` is not a `V`.
- [x] **1.3** §"The differential": AC1.4's both-directions table and AC1.5's rejected
      successors. ⛔ **Quote `SILENT_CLASS_DEFINITION` VERBATIM** (AC1.10) — copy it from the
      **imported constant**, not by eye.
- [x] **1.4** §"Instrument provenance": AC1.7 — the two instruments, the two HEADs, the
      `V5`-is-the-script's-own sentence quoted, and **no reach figure for `S1`**. Any
      provisional arithmetic labelled **PROVISIONAL** on its own line.
- [x] **1.5** §"What the evidence does and does not support": AC1.8 (36 UNADJUDICATED, operator
      act, smoke-test proportion NOT MEASURED, *"no promotion proposal … carries evidence"*)
      and AC1.9 (two members, breadth floor 3, `UNEVALUABLE` already pre-registered; ⛔ the
      floor is **not** argued down).
- [x] **1.6** §"`consumed == 0` is not loosened": AC2.1–AC2.5, four labelled registers plus the
      advisory-until-an-operator clause.
- [x] **1.7** §"What this act does not do": AC4.1–AC4.7, each its own sentence, with §1.5's
      four reasons for refusing to measure.
- [x] **1.8** §"Hand-off": AC1.11 — 17.3's four constraints and 17.4's three pointers, each
      naming the story that owns it.
- [x] **1.9** ⛔ Verify: no `_STATUS_CLAIMS` phrase; **not** registered in `_STATUS_DOCUMENTS`;
      no corpus checkout path; no host path; no source bytes.

### Task 2 — THE LEDGER DISPOSITION (AC3)

- [x] **2.1** Grep `deferred-work.md` for `DF-INV-VACUOUS-B` and for prior art on
      `moot-by-replacement`. ⛔ **Cite prior art rather than re-filing.**
- [x] **2.2** Read `deferred-work.md` in **binary**; record byte / CR / LF counts.
- [x] **2.3** Append the dated disposition in `DF-AUD-DETECT-F`'s shape (`:6838`) — AC3.2,
      AC3.3. ⛔ **Do not rewrite the entry above it.** ⛔ **Touch no other entry** (AC3.4).
- [x] **2.4** Re-verify byte invariants: **exactly 1 CR**, LF grew by the lines added, 0 CRLF.
- [x] **2.5** Apply §2.5's two-branch closure-verb rule to this story record, and confirm
      `TC-ArgusAgent-DOCS-001-78` green **after** the ledger and the record are both written.

### Task 3 — THE THREE GUARDS (AC5)

- [x] **3.1** `tests/test_successor_predicate_specification.py` with `-142`, `-143`, `-144`,
      each discharging (i)/(ii)/(iii) in its own docstring.
- [x] **3.2** ⛔ **Anchor `-142`'s figure extraction** to a labelled table or an explicit
      marker, and drive an adversarial **decoy** through it — 17.1's one review finding was an
      unanchored whole-document scan in this exact area id.
- [x] **3.3** ⛔ **`-143` classifies AST nodes, not substrings.** Assert the known decision
      site is FOUND before asserting no other exists.
- [x] **3.4** ⛔ **`-144`'s git half asserts a control path known to carry commits in the same
      range is NON-EMPTY first** (`-75`/`-139`'s idiom, reused verbatim).
- [x] **3.5** Drive **each** guard RED **at its real seam** by an **executed** mutation of the
      real artifact or module; restore **byte-exact** and verify by **sha256**. Record each
      mutation, its RED message and the restore hash.

### Task 4 — PROVE NOTHING MOVED, AND RUN EVERY GATE (AC4, AC5.3, AC6)

- [x] **4.1** AC6.3's `git diff` over `argus/`, `scripts/`, the protocol, the PRD, the
      architecture, `epics.md` and `validation-corpus/` — **EMPTY**, output recorded.
- [x] **4.2** Confirm `eligible_member_count()` is **5**, `PROTOCOL_VERSION` is **V1.3**, and
      `-140` is green against the `f906d04` pin.
- [x] **4.3** AC6.4's full gate sweep with **every exit code**, ⚠️ labelled **LOCAL
      (Windows)**; NFR-M1 re-measured for the new test file.
- [x] **4.4** `git status --porcelain` and `git diff --stat` against AC6.1's write set, before
      **each** commit. ⛔ No `git add -A`.
- [x] **4.5** Verify `sprint-status.yaml` at **1,264 lines / 1,264 CR** after its edit.

### Task 5 — THE ARC AND THE HAND-OFF (AC6.5, AC7)

- [x] **5.1** Commit O, A, B per §2.2, staging by explicit path.
- [x] **5.2** ⛔ Ledger note + story record + `sprint-status.yaml` transition **together in
      commit B**.
- [x] **5.3** Record in the story: the four constraints handed to **17.3** by name (`-127`'s
      fence, `-145`'s pin, the `Evidence-partition:` trailer, the missing SUT-derived-binding
      resolver) and the three handed to **17.4** (`SUCCESSOR_OUTPUT_PATHS`,
      `per_member["V5:…"]`, `AI-E16-7`).
- [x] **5.4** Record any AC7 escalation with its evidence, or state explicitly that none was
      reached.

### Review Findings

**Code review — iteration 1 (Sonnet 5), 2026-08-25. VERDICT: PASS.** Scope: commits
`5999624..579a342` (base `52ae0e5`) — the specification document, the three guards, and the
`DF-INV-VACUOUS-B` disposition. Independently re-executed rather than read back: full suite
(`python -m pytest -q --cov=argus --cov-fail-under=80`) exit 0, **1741 passed**, zero `F`/`E`
markers (counted from the dot stream, matching the claimed count exactly), coverage **95.69%**;
`tests/test_successor_predicate_specification.py` 3/3; `mypy argus` clean over 95 files;
`bandit -r argus --severity-level medium` clean; `-127`/`-140`/`-22`/`-78` green;
`tests/test_module_size_ceiling.py` green (new module 735/1200 lines, confirmed by `wc -l`);
`deferred-work.md` binary-read invariants **593,897 bytes / 1 CR / 7,534 LF** and
`sprint-status.yaml` **1,264 lines / 1,264 CR**, both matching the Dev Agent Record exactly;
`git status --porcelain` clean throughout.

**All three guards independently mutated and confirmed to fire at their real seam** (not
`f(x) == f(x)`), each restored via `git checkout --` with the tree re-verified clean afterward:
`-142` (`record.class_size` 36→37 in the live document) reddened naming the exact key and both
values; `-143` (a second real `evidence.mock_referencing_assertions >= 2` comparison planted in
`argus/precision/silent_class.py`) reddened listing both decision sites, confirming the
classifier walks `ast.Compare` nodes rather than counting substrings; `-144` (one character of
the `SILENT_CLASS_DEFINITION` quotation altered) reddened with the exact offset and both
characters. `AC6.3`'s scope fence independently re-run
(`git diff 52ae0e5 HEAD -- argus/ scripts/ …/precision-validation-protocol.md …/E-PRD/
…/architecture.md …/epics.md …/validation-corpus/`) — **empty**; `eligible_member_count()`
(`tests/corpus/_manifest.py`) — **5**, unchanged. `161` does not appear anywhere in the
specification (`grep` confirmed), and none of `_STATUS_CLAIMS`' 12 phrases occur in it either.

**The three dev-flagged items, judged, not just relayed:**

1. **`DN-17-2-12` (`-144`'s git half scoped to this story's own `(17-2)`-tagged commits, not
   `<base>..HEAD` wholesale) — judged SOUND.** The literal AC5.3 reading, applied to a guard that
   ships in the permanent suite, is self-destructing: Story 17.3 is chartered to write inside
   `argus/`, so an unscoped `base..HEAD` check would go RED the first time a later story does its
   own job legitimately, and the only available response would be to delete a real guard. The
   scoped form keeps a permanently true, permanently checkable claim about *this story's own
   commits* and still fires on a future `fix(17-2)` that touched the package. The one residual
   risk — a 17.2 fix-round commit that touches `argus/` without carrying the `(17-2)` tag would
   not be caught — is bounded by the commit-message convention this whole repo already relies on
   for `TC-ArgusAgent-DOCS-001-78` and is explicitly flagged in the guard's own comment
   (`_STORY_SCOPE`: "update it, never widen it"), not smuggled in silently. No action item.
2. **`DN-17-2-11` (the two 17.1 close-out files carried into commit O with a disclosure) —
   verified ACCURATE.** `git diff 52ae0e5 5999624 -- .../17-1-….md` is exactly the iteration-2
   review-record append plus the `Status: review` → `done` flip — nothing else rode along.
   `git diff 52ae0e5 5999624 -- sprint-status.yaml` touches only the 17-1 status line
   (`review`→`done`) and the 17-2 line (`backlog`→`in-progress`, collapsing two working-tree-only
   transitions — `backlog`→`ready-for-dev` from the SM's own uncommitted contexting hunk, then
   `ready-for-dev`→`in-progress` from this dev round — into one commit because neither had been
   committed separately; both transitions are named in the line's own comment). Commit O's message
   discloses both files by name and states neither was edited by this story. No action item.
3. **`161` refusal — verified GENUINE, not smuggled.** `grep -n "161"` over the specification
   returns nothing. §4's instrument-provenance table and Dev Notes correctly attribute `V2=36` to
   shipped code at a different HEAD and `V5=125` to the research script's own `ast` reasoning
   (quoted verbatim from the harness docstring), label any provisional arithmetic on its own line,
   and hand the measurement to 17.4 by name (§8.2) with the concrete pointer to
   `per_member["V5:…"]` at `investigate-per-call-scoping.py:219`. No action item.

**Absences checked against the story and the ledger before being considered findings:** the six
`DF-*` re-homing notes stay untouched (Story 17.5's, per `DN-17-2-8`/§8.3) — not filed here.
`DF-INV-MERGE-A` (squash/rebase incompatibility, `deferred-work.md:7477`) already covers the
general class of risk a squash-merge would pose to any commit-scoped guard including `-144`'s git
half; not a new finding specific to this story.

**No `argus/**` byte, no `scripts/precision_preregistration.py` byte** — both re-verified against
the object database, not promised. `argus/**` unchanged, `PROTOCOL_VERSION` still `V1.3`,
`eligible_member_count()` still 5. **Zero findings.** `review` → `done`.

---

## Dev Agent Record

### Agent Model Used

`claude-opus-5[1m]` (Opus 5, 1M context), via the `bmad-dev-story` workflow. Round 1,
`implement`. No prior review findings existed for this story.

### Debug Log References

⚠️ **Every gate below is LOCAL (Windows).** This branch is unpushed and `audit-ci.yml`
triggers on `master`/`main` only, so **no CI evidence exists at any sha in this arc**, and
CI runs an **ubuntu matrix** a green Windows suite has previously failed to predict
(`AI-E13-1`; epic-18 retro SD-4).

#### Task 0 — §0 re-measured by execution at HEAD `52ae0e5`. ⛔ EVERY ROW REPRODUCED.

| § | row | measured | command |
|---|---|---|---|
| 0.0 | HEAD / branch | `52ae0e5df79704d02124ae32aa7ecd6d9133d3fc` on `docs/merge-strategy-decision`, **4 commits ahead of `origin/master`** | `git rev-parse HEAD`; `git rev-list --count origin/master..HEAD` |
| 0.0 | `git status --porcelain` | ⛔ **NOT EMPTY**, and **it had moved since contexting**: `MM sprint-status.yaml` (not `M `), `M  stories/17-1-….md`, `?? stories/17-2-….md`. The extra unstaged hunk is the SM's own `backlog → ready-for-dev` transition for 17-2. §2.6 handling applied — see `DN-17-2-11`. | `git status --porcelain` |
| 0.0 | next free `PRECISION-001` id | `-142` — confirmed unused | `grep -rn "PRECISION-001-14[2-9]" tests/` → none |
| 0.0 | `deferred-work.md` invariants | **589,632 bytes · 1 CR · 7,489 LF · 0 CRLF** — exact | binary read, `count(b"\r")` |
| 0.0 | `sprint-status.yaml` invariants | **1,264 lines · 1,264 CR** — exact, and **all 1,264 are CRLF pairs** | binary read |
| 0.1 | `PREREGISTRATION_COMMIT_SHA` | `f906d04997b391bea4592aabc0343d1234b3b060`, **ancestor of HEAD: True** | import; `git merge-base --is-ancestor` |
| 0.1 | `PROTOCOL_VERSION` / `MAX_FALSE_ACCUSATION_EXPOSURE` / `EXPOSURE_SOURCE_SHA` | `V1.3` / `26` / `6c59115…` | import |
| 0.1 | `SUCCESSOR_OUTPUT_PATHS` | both entries **ABSENT on disk** — `False`, `False` | `Path(...).exists()` |
| 0.1 | `CRITERION_OUTCOMES` | `{MET, NOT_MET, UNEVALUABLE}` | import |
| 0.2 | the three vocabularies | `_CORROBORATION_ASSERTION_CALLEES` **23** · `_ASSERTION_CALLEES` **89** · `_MOCK_CALLEES` **10** | `len()` after import |
| 0.2 | `_ast_corroborated` return | `evidence.sut_result_is_discarded and evidence.mock_referencing_assertions >= 1`, over `provenance_evidence(..., assertion_callees=_CORROBORATION_ASSERTION_CALLEES, mock_callees=_MOCK_CALLEES)`; fact (a) is `len(self._sut_call_sites(span_edges)) >= 1` | source read at `vacuous_test.py:754`–`:796` |
| 0.3 | `SILENT_CLASS_DEFINITION` | **903 characters**, sha256 `7bc277fa678b09ea…`; carries *"Promoting V2 would be a genuinely DIFFERENT predicate, not a loosening"* verbatim | import |
| 0.3 | `SpanScore.is_silent_class_member` | `self.discarded_sut_calls >= 1 and not self.asserts_anything` — two conjuncts, no threshold | `inspect.getsource` |
| 0.3 | `score_span` composes four shipped helpers | `span_provenance` → `provenance_evidence`, `body_statement_count`, `opens_bare_assert`, `is_assertion_callee`; re-implements none | `inspect.getsource` |
| 0.4 | `TC-ArgusAgent-PRECISION-001-127` | **GREEN**, exit 0 | `pytest tests/test_silent_class.py -k 127` |
| 0.5 | the six variant definitions | reproduced **verbatim** from the harness docstring `:9`–`:24`; `V0` 0 · `V1` 6 · `V2` 36 · `V3` 6 · `V4` 676 · `V5` 125 (`V3` is in the harness docstring, not in research §5's table) | source read, **not executed** |
| 0.5 | the `V5` sentence | *"V5 additionally needs SUT-derived name binding, which no shipped helper provides; it is computed with Python `ast` and is therefore THIS SCRIPT'S OWN reasoning, not the shipped predicate."* — present, on the line | source read |
| 0.5 | `CHECKOUTS`, `per_member["V5:{mid}"]` | five entries incl. `agent-smith` at the depth-5 path; the collection site is at `:219` | source read |
| 0.6 | ⛔ `mock_referencing_assertions` decision sites | **EXACTLY ONE**: `argus/detectors/vacuous_test.py:796`. The other three are `provenance_scan.py:841` (field decl), `silent_class.py:232` (`SpanScore` field), `:328` (that field populated). **95 modules parsed.** ⛔ **AC7.3 NOT triggered.** | `ast` walk, classified by node kind |
| 0.7 | `silent-class-record.json` | `class_size` **36** · `{agent-smith: 22, minions: 14}` · `files {10, 9}` · `population_walked` **1032** · `population_skipped` **0** · `protocol_version` **V1.3** · `counts {UNADJUDICATED: 36, TP: 0, FP: 0, BORDERLINE: 0}` · `gates_anything` **False** · `promotes_nothing` **True** · `exhaustiveness {exhaustive: False, adjudicated: 0, residual: 36}` · `smoke_test_proportion.measured` **False** · `independence.status` **NOT_ESTABLISHED** | `json.load` |
| 0.8 | the detector surface | `Detector` Protocol at `base.py:147`–`:190`, both members read-only `@property`; `@runtime_checkable` **DELIBERATELY ABSENT**; **four** `if TYPE_CHECKING:` pins at `orphan_code.py:310`, `secret_scan.py:633`, `tool_runner.py:459`, `vacuous_test.py:799`; `-145`/`-146` present at `test_detector_base.py:224`/`:257` | source read |
| 0.9 | `_STATUS_DOCUMENTS` globs | `sprint-change-proposal-*.md` and `epic-*-retro-*.md` — the specification's filename matches **neither**, so it is correctly left unregistered; `-22` re-run **GREEN** | source read + `pytest` |
| 0.9 | `_STATUS_CLAIMS` | 12 phrases; **zero occur** in the specification, denied or otherwise | executed over the committed document |

⛔ **AC7 was NOT reached.** No §0 row failed to reproduce; `git log 52ae0e5..HEAD -- argus/`
is empty for this story's arc; the criterion is byte-unchanged at its pin; **no second
decision site exists**; the ledger's closure vocabulary expressed `moot-by-replacement`
without rewriting anything; and the specification was written without running a measurement
and without publishing an unmeasured figure as measured.

⚠️ **One §0 row moved between contexting and dev, and it is recorded rather than adjusted.**
§0.0 states `git status --porcelain` shows two files staged `M `. At dev time
`sprint-status.yaml` was `MM`, not `M ` — the extra unstaged hunk being the create-story
workflow's own `backlog → ready-for-dev` transition for this story, written after §0.0 was
measured. This is the story's own footprint, not a third party's, so it is a self-consistent
drift rather than an AC7.1 failure. `DN-17-2-11` records the handling.

#### Task 3.5 — every guard driven RED at its REAL seam by an EXECUTED mutation

| guard | seam mutated | RED message (head) | exit | restore |
|---|---|---|---|---|
| `-142` | the **real** specification: `record.class_size` `**36**` → `**37**` in the anchored table | *"the specification's cited figure(s) no longer re-derive from the committed artifacts: `record.class_size`: document says 37, record says 36"* | **1** | sha256 `e0e5eb298bcb317f…` **identical** before and after |
| `-143` | the **real** `argus/precision/silent_class.py`: a second real comparison `evidence.mock_referencing_assertions >= 2` planted above `score_span` | *"mock_referencing_assertions has 2 decision site(s) in the argus package, not one: [('argus/detectors/vacuous_test.py', 796, 'decision'), ('argus/precision/silent_class.py', 310, 'decision')]"* | **1** | sha256 `8a8299ccf1d2927e…` **identical** before and after |
| `-144` (quotation half) | the **real** specification: one character of the quotation, `span` → `spam` | *"NOT character-for-character identical to the imported constant. First difference at offset 31: document has 'm reaches the system under tes', constant has 'n reaches…'. Lengths 903 vs 903."* | **1** | sha256 `e0e5eb298bcb317f…` **identical** before and after |
| `-144` (git half) | ⛔ **not mutable by a file edit — the seam is the object database.** The **unchanged** predicate was driven over **real history**: `base = ee855a6~8` (`9e3fdc2`), scope `(18-4)` → 16 arc commits, **4** scope-matched, **1** argus-touching, **intersection NON-EMPTY**: `0ba6a98 feat(18-4): narrow the Detector Protocol…` | the intersection `-144` asserts empty is **watched non-empty** on real shas | — | nothing written; `git` read-only verbs only |

⚠️ **Why `-144`'s git half is scoped to THIS STORY'S ARC and not to `<base>..HEAD` wholesale**
(`DN-17-2-12`). AC5.3 words it as *"`git log <base>..HEAD -- argus/` is EMPTY"*. Taken
literally that guard is **guaranteed to go RED the moment Story 17.3 lands**, because 17.3
is chartered to write inside the shipped package — and the only available response to that
RED would be to delete the guard, throwing away a real claim with a badly scoped one. The
claim Story 17.2 actually makes is about **its own commits**, so the guard intersects the
range's argus-touching commits with the range's `(17-2)`-scoped commits and asserts the
intersection empty. **It is strictly stronger where it matters** (it survives 17.3 and still
fires on a `fix(17-2)` that touched the package) and it stays checkable forever. Two
non-vacuity preconditions precede it: the `argus` pathspec is proved capable of finding
commits at all, and the `(17-2)` selector is proved to find this story's own commits.

#### Task 4 — AC6.3: nothing outside the write set moved

`git diff 52ae0e5 HEAD -- argus/ scripts/ …/precision-validation-protocol.md …/E-PRD/ …/architecture.md …/epics.md …/validation-corpus/`
→ **EMPTY** (exit 0, zero bytes of output), re-verified at commit A and again at commit B.

`eligible_member_count()` = **5** (unchanged) · `PROTOCOL_VERSION` = **V1.3** (unchanged) ·
`TC-ArgusAgent-PRECISION-001-140` **GREEN** against the `f906d04` pin.

#### Task 4.3 — AC6.4, every gate with its exit code. ⚠️ ALL LOCAL (Windows).

| gate | result | exit |
|---|---|---|
| `python -m pytest` | **1741 passed** in 249s, no `F`/`E` markers (1738 at 17.1 close + these three guards) | **0** |
| `python -m pytest tests/test_successor_predicate_specification.py` | 3 passed | **0** |
| `python -m pytest --cov=argus --cov-fail-under=80` | *"Required test coverage of 80% reached. Total coverage: **95.69%**"* | **0** |
| `python -m mypy argus` | *"Success: no issues found in **95** source files"* | **0** |
| `python -m bandit -r argus --severity-level medium` | **Medium 0, High 0** | **0** |
| `-127` (the import fence) | GREEN | **0** |
| `-140` (directional immutability) | GREEN | **0** |
| `-22` (`_STATUS_DOCUMENTS` closure) | GREEN | **0** |
| `-78` (ledger cross-check) | GREEN **after** the ledger note and this record were both written | **0** |
| NFR-M1 sweep (`tests/test_module_size_ceiling.py`) | GREEN; the new module is **735** physical lines against the **1200** ceiling | **0** |
| `deferred-work.md` invariants after the write | **593,897 bytes · 1 CR · 7,534 LF · 0 CRLF** — +45 lines, **+0 deletions** | — |
| `sprint-status.yaml` invariants after both writes | **1,264 lines · 1,264 CR** — unchanged | — |

### Completion Notes List

- **AC1 — the specification exists and states the definition, the defect shape and the differential.** `_bmad-output/design-artifacts/ArgusAgent/successor-vacuity-predicate-specification.md`, dated 2026-08-25, author role named. `S1` is defined as three conjuncts (§2.1); the threshold is *every* assertion at the weakest band with the widening **pre-refused** (§2.2); the defect shape is one sentence (§2.3); `S1` is stated **not** to be a `V0`..`V5` member with the `V6` rejection recorded (§2.4); the differential is given in **both** directions (§3) and the six rejected successors each carry their reason (§3.2).
- **AC1.7 — the instrument provenance is the load-bearing section, and `S1`'s reach is NOT a number.** §4 names the two instruments and the two HEADs, quotes the harness's own *"THIS SCRIPT'S OWN reasoning, not the shipped predicate"* sentence, and states that summing the two band counts is **PROVISIONAL** arithmetic across two instruments — labelled on its own line, and never written as `S1`'s reach. **The figure `161` does not appear in the document at all.** Story 17.4 measures it.
- **AC1.10 — the quotation is generated, not typed.** `SILENT_CLASS_DEFINITION` was written into §2.4 **programmatically from the imported constant**; no character of it was transcribed by eye. `-144` compares it back, character for character, on every run.
- **AC2 — `consumed == 0` is answered in four registers plus the advisory clause** (§6.1–§6.5), including the unhedged admission that `S1`'s population **is larger** than every `cons == 0`-preserving variant. `argus/**` is byte-unchanged and that is proved against the object database, not promised.
- **AC3 — the mock-binding decision is recorded, and the mock-idiom ledger entry is dispositioned.** ⛔ **`DF-INV-VACUOUS-B` is CLOSED 2026-08-25 as `moot-by-replacement` by this story.**
  The note is dated, append-only and 45 lines, written in the shape of the 2026-08-25
  detector-audit Protocol disposition further down the ledger (`§2.4`'s named prior art at
  `deferred-work.md:6838`). It carries the **residual with the disposition** and rests on the
  entry's **own** stated trigger being answered NO by a committed artifact, rather than on any
  claim that the code changed. **Zero deletions** in the ledger diff; the entry above it and the
  2026-08-24 roll-up sentence below it are both left unedited (§3.4 strike-never-erase).
  `ledger_closed_ids` recognised the disposition: **39 → 40**, exactly one new id.
- **AC4 — nothing was measured, ratified, fetched or spent.** No detector was run over any corpus member, no corpus blob was materialised, the research harness was **read but never executed**, and no successor-predicate output was produced. `eligible_member_count()` is 5 before and after. Nothing reached the network. Both `SUCCESSOR_OUTPUT_PATHS` prefixes remain absent on disk.
- **AC5 — three guards, each with an observable, an executed real-seam mutation and generated adversarial variants.** `-142` generates **19 decoys + 19 perturbations** from the live document on every run; `-143` generates a real second comparison into each of the **3** referencing modules; `-144` generates **41** one-character perturbations from the live constant. No guard was weakened to go green.
- **AC5 — 17.1's review finding was treated as a live hazard in the same area id.** `-142` extracts figures from a markdown document, which is exactly the shape of 17.1's unanchored whole-document regex. Extraction is anchored to `<!-- CITED-FIGURES:BEGIN/END -->`, and every run plants a decoy row **outside** the anchors that must be **invisible** to the anchored extractor **and visible** to a deliberately-kept unanchored one — the second half is what proves the planted input carries the defect rather than proving the extractor found nothing.
- **AC6 — the write set is exactly five paths** and the three-commit arc landed as §2.2 specifies, with the ledger note, this record and the `sprint-status.yaml` transition **together in commit B** (`-78`). Staged by explicit path throughout; **no `git add -A`**.
- **AC7 — no escalation was reached.** Every §0 row reproduced. The one drift (§0.0's porcelain line) is this story's own footprint and is recorded above rather than adjusted.

**Decisions this dev round took, beyond the ten the story locked:**

- **`DN-17-2-11` — the two artifact files staged at contexting were CARRIED in commit O, with a disclosure block in the message.** *Rejected:* `git reset`-ing them and leaving them for the peer session. `sprint-status.yaml` is **one file** and its 17-1 `review → done` hunk cannot be staged apart from 17-2's transition; committing the transition while leaving 17-1's story record uncommitted would produce an inconsistent pair. §2.2 sanctions carrying them *"with a message line saying so"*, and commit O names both files, says whose close-out they are, and states that this story edited neither.
- **`DN-17-2-12` — `-144`'s git half is scoped to THIS STORY'S ARC by commit scope, not to `<base>..HEAD` wholesale.** *Rejected:* the literal reading of AC5.3. See the Task 3.5 note above: the literal form is guaranteed RED the moment Story 17.3 legitimately writes inside the shipped package, and the only response would be to delete it. ⚠️ **This is a deliberate divergence from the AC's wording in service of the AC's claim**, recorded here with its evidence rather than taken silently. The coupling — that the arc's commits carry a `(17-2)` scope — is written into the guard's own constant with the instruction to **update it, never widen it**.
- **`DN-17-2-13` — `-142` compares in BOTH directions, not only document-against-authority.** *Rejected:* checking only that cited figures match. A row silently deleted from the table would then pass, and a shrinking comparison is how a guard goes quiet. Every `definition.*` figure the constant states must be present in the document, and every cited key must resolve to a named authority.

**Handed forward, by name:**

- **To Story 17.3** — `-127`'s transitive one-way import fence (the `S1` scorer **cannot** import `silent_class` from the detector package; **never widen the fence**); `-145`'s `if TYPE_CHECKING:` conformance-pin obligation, RED from the moment a new `run() -> DetectorResult` class is written; the `Evidence-partition:` trailer, which a new module under the detector package **does** trigger; and the **SUT-derived name binding resolver**, which does not exist and is the largest piece of unbuilt work in this epic. Plus the three further costs of any shipped byte: dogfood-artifact regeneration, the coverage gate, and `mypy`/`bandit`.
- **To Story 17.4** — `SUCCESSOR_OUTPUT_PATHS` (both prefixes still absent; successor output lands under one of them and nowhere else); the harness's already-collected `per_member["V5:…"]` breakdown at `investigate-per-call-scoping.py:219`, **one re-run away** and declined here; and `AI-E16-7`, **UNFILLED**, which is 17.4's stated precondition and not this story's problem.
- **To Story 17.5** — every ledger re-homing note except this story's one entry.

### File List

- `_bmad-output/design-artifacts/ArgusAgent/successor-vacuity-predicate-specification.md` — **NEW**, 423 lines
- `tests/test_successor_predicate_specification.py` — **NEW**, 735 lines (`TC-ArgusAgent-PRECISION-001-142`..`-144`)
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — **MODIFIED**, +45 lines / −0, pure append
- `_bmad-output/design-artifacts/ArgusAgent/stories/17-2-a-different-predicate-argued-as-one.md` — **NEW** (this file)
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — **MODIFIED**, two status transitions for this story plus `last_updated`

⛔ **Nothing else.** `argus/**`, `scripts/**`, `precision-validation-protocol.md`, `epics.md`,
`architecture.md`, the PRD and `validation-corpus/**` are all **byte-unchanged** (AC6.3,
verified by `git diff` returning empty).

---

## Change Log

| Date | Change | Author |
|---|---|---|
| 2026-08-25 | **STORY CONTEXTED** at HEAD `52ae0e5` (branch `docs/merge-strategy-decision`, **two artifact files STAGED** — §0.0). §0's ten rows measured **by execution** against this tree, not copied from `epics.md`, from the 2026-08-24 research or from 17.1's record. Four premises moved against what the epic assumes: (1) `argus/precision/silent_class.py` **already ships** the `V2` half of the successor and `SILENT_CLASS_DEFINITION` already carries this story's core argument in committed words — so it is **quoted verbatim** and `-144` enforces that; (2) `TC-ArgusAgent-PRECISION-001-127` **fences the detector package out of `silent_class.py`** transitively, which is the single most expensive thing Story 17.3 could get wrong; (3) **`V5` = 125 is the research script's OWN `ast` reasoning, not a shipped measurement**, and `V2` = 36 was measured at a different HEAD — so `161` is arithmetic across two instruments and this story **refuses to publish `S1`'s reach as a number**, handing it to 17.4; (4) `mock_referencing_assertions` has **exactly one decision site** in all of `argus/**`, which is what makes AC3's `DF-INV-VACUOUS-B` disposition true **today** rather than a claim about the future. Ten decisions taken (`DN-17-2-1`..`-10`), each with its rejected alternative — notably that the definition-as-code is **17.3's**, not a `scripts/` module that would fork it (`AR7`), and that AC2 is answered in **four registers** including the admission that `S1`'s population **is** larger than every clause-removal variant keeping `cons == 0`. Scope: **one** ledger entry written, `argus/**` byte-unchanged, `scripts/precision_preregistration.py` frozen, **no measurement run**. `backlog` → `ready-for-dev`. | Scrum Master (create-story, Opus 5) |
| 2026-08-25 | **DEV ROUND 1 (implement) COMPLETE — `in-progress` → `review`.** Three-commit arc `5999624` chore → `126f502` docs → this record. Task 0 re-measured **all ten §0 rows by execution at HEAD `52ae0e5` and EVERY ROW REPRODUCED**, so ⛔ **AC7 was not reached**: the criterion is byte-unchanged at its `f906d04` pin, both `SUCCESSOR_OUTPUT_PATHS` prefixes are still absent, the three vocabularies size 23/89/10, `SILENT_CLASS_DEFINITION` is 903 characters, and `mock_referencing_assertions` still has **exactly one decision site** across all 95 shipped modules. Landed: the specification document (`S1` as three conjuncts, the threshold pre-refused against widening, the differential in **both** directions, six rejected successors, `consumed == 0` answered in four registers including the unhedged admission that `S1`'s population **is larger**, and ⛔ **no reach figure for `S1` anywhere** — `161` does not appear, because it is arithmetic across two instruments at two HEADs and 17.4 measures it); three guards `-142`..`-144`, each driven **RED at its real seam by an executed mutation** of the real artifact or the real module and restored byte-exact by sha256, with the `-144` git half driven to a **non-empty** intersection on real history instead; and ⛔ **exactly ONE ledger entry** — `DF-INV-VACUOUS-B` **CLOSED** as `moot-by-replacement`, append-only, residual attached, zero deletions, `ledger_closed_ids` 39 → 40. Two decisions beyond the story's ten: `DN-17-2-11` (the staged 17.1 files carried in commit O **with a disclosure block**, because `sprint-status.yaml` cannot be split) and ⚠️ `DN-17-2-12` (**a deliberate divergence from AC5.3's literal wording**: `-144`'s git half is scoped to this story's own arc, because the literal form is guaranteed RED the moment 17.3 legitimately writes inside the shipped package). LOCAL (Windows) gates, every exit code **0**: pytest **1741 passed**, coverage **95.69%**, `mypy argus` clean over 95 files, `bandit` 0 medium / 0 high, `-127`/`-140`/`-22`/`-78` green, NFR-M1 735/1200. ⚠️ **No CI evidence at any sha in this arc** — unpushed branch, ubuntu matrix. `argus/**` byte-unchanged; nothing ratified, fetched, measured or spent. | Developer (dev-story, Opus 5) |
| 2026-08-25 | **CODE REVIEW, iteration 1 (Sonnet 5). VERDICT: PASS.** Zero findings. Independently re-executed rather than read back: full suite exit 0, **1741 passed**, zero `F`/`E` markers, coverage **95.69%**; the three guards, `-127`/`-140`/`-22`/`-78` and NFR-M1 all green; `mypy`/`bandit` clean; `deferred-work.md` (593,897 bytes / 1 CR / 7,534 LF) and `sprint-status.yaml` (1,264 lines / 1,264 CR) invariants confirmed exact; AC6.3's scope-fence diff re-run empty; `eligible_member_count()` still 5; `161` confirmed absent from the specification by grep; all 12 `_STATUS_CLAIMS` phrases confirmed absent. All three guards independently mutated at their real seam (`-142` figure, `-143` second decision site, `-144` quotation character) and confirmed RED with the expected message, then restored via `git checkout --` with the tree re-verified clean. `DN-17-2-12` judged **sound** — the literal AC5.3 reading would self-destruct the moment Story 17.3 legitimately writes inside `argus/`, and the scoped form keeps a permanently checkable claim about this story's own commits; the one residual risk (a future `(17-2)`-scoped commit that touches `argus/` without the tag) is bounded by the same commit-message convention `-78` already relies on and is disclosed in the guard's own comment, not hidden. `DN-17-2-11`'s disclosure verified **accurate** by diffing the two carried files directly — nothing rode along beyond the iteration-2 review record and the two status-line flips. The `161` refusal verified **genuine**: absent from the document, with `V2`/`V5` correctly attributed to their two different instruments and HEADs, and the measurement handed to 17.4 by name with a concrete pointer. `review` → `done`. | Reviewer (code-review, Sonnet 5, iteration 1) |
