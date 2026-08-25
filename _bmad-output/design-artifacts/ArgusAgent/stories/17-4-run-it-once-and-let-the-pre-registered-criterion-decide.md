---
baseline_commit: 682b074
---

# Story 17.4: Run it once, and let the pre-registered criterion decide

Status: review

<!-- Contexted 2026-08-25 at HEAD `682b074` (branch `docs/merge-strategy-decision`, 17 ahead of
     `origin/master`) by the create-story workflow (Opus 5).

     ⛔ THE TREE IS NOT CLEAN AT CONTEXTING. `git status --porcelain` shows TWO STAGED paths
     belonging to the PEER SESSION — `sprint-status.yaml` and
     `stories/17-3-grade-what-the-assertion-constrains.md`, both `M ` (staged, worktree clean).
     They are 17.3's review close-out. ⛔ Stage by explicit path; never `git add -A`, or this
     story's first commit swallows the peer's staged work.

     EVERY FIGURE IN SECTION 0 WAS READ OFF THIS TREE BY EXECUTION at `682b074`, not copied from
     `epics.md`, from `deferred-work.md` or from 17.1/17.2/17.3's story records. The criterion
     module was IMPORTED and its floors RESOLVED; the seal partition was re-walked against the
     ratified member set; the adjudication record was re-counted; the 1,032 was re-derived per
     member out of `adjudication-set-13-5.json`; all five pinned corpus shas were probed with
     `git cat-file -e` at their real checkout paths; `f906d04`'s ancestry was re-checked;
     `-138`/`-139`/`-140` were re-run green.

     ⛔⛔ THE ONE THING THAT MAKES THIS STORY DIFFERENT FROM EVERY OTHER STORY IN THE EPIC:
     THE NUMBER THIS STORY MEASURES DOES NOT EXIST YET, AND IT DID NOT EXIST WHILE THESE
     ACCEPTANCE CRITERIA WERE BEING WRITTEN. The contexting session DELIBERATELY DID NOT RUN
     THE MEASUREMENT (section 1.1). Story 17.1 froze the criterion while the answer was zero;
     17.2 refused to publish S1's reach as a number and handed it here BY NAME; 17.3 built S1 and
     published no reach figure. A story file that arrived with the number already in it would
     have thrown away everything the previous three stories paid for. ⛔ NO ACCEPTANCE
     CRITERION BELOW PRESUPPOSES A PASS, AND NONE PREDICTS A VALUE.

     FIVE PREMISES MOVED OR SHARPENED AGAINST WHAT `epics.md` ASSUMES, and each is load-bearing:

       (1) 0.7 — ⛔ **S1 IS ALREADY PUBLICLY CONSUMABLE AND HAS A NAMED SINGLE ENTRY POINT**,
           which `epics.md` (written 2026-08-24, before 17.3 existed) could not know:
           `VacuousTestDetector.successor_evidence(source_lines, span_edges, start, end)` ->
           `SuccessorVacuityEvidence`, COMPOSITION-ONLY over the public
           `assertion_strength.s1_corroborated` and `grade_span_assertions`. 17.3's own docstring
           says it exists so that *"Story 17.4 measures the same predicate this detector would
           report"*. ⛔ There is therefore NOTHING to re-derive, and re-deriving is the AR7 defect
           the epic exists to close.

       (2) 0.4 + 0.3 — ⛔ **THE CRITERION RETURNS `UNEVALUABLE` ON TWO INDEPENDENT ARMS THAT
           BOTH READ FAILED TODAY, BEFORE ANY NUMBER EXISTS.** `sealed_contributing_members`
           resolves to a floor of **3** and the measured sealed contribution over the ratified
           corpus is **0** — sealed-intersect-ratified is EMPTY, re-verified at HEAD. And the
           adjudicated population for any successor class is **EMPTY**, because adjudication is an
           operator act. ⛔ This is NOT a prediction about S1's reach: it is arithmetic over the
           population, and Story 17.1 sections 3.1/3.2 WROTE IT DOWN before the successor existed.
           The honest shape of this story is *run it, and record what it returns*.

       (3) 1.2 — ⛔ **THIS STORY DOES NOT ADJUDICATE, AND THEREFORE CANNOT REPORT A PRECISION
           RATIO.** Protocol section 2: `UNADJUDICATED` is the ONLY disposition an automated
           producer may write. `AI-E16-7` — section 4's External adjudicator — is UNFILLED. The
           16.7 precedent is exact: `silent-class-record.json` carries 36 rows, all
           `UNADJUDICATED`, `exhaustive: false`, `gates_anything: false`. `epics.md`'s *"the
           precision measured"* is honoured by CALLING the frozen fold with the real counts and
           recording what it returns — which, on an empty denominator, is `UNEVALUABLE` with
           `AI-E11-1`'s reason.

       (4) 0.9 — ⛔ **`DF-13-5-A`'s CONDITION 1 WAS SHARPENED ON 2026-08-24 AND ITS SUBJECT IS
           THE *SHIPPED VERDICT-ELIGIBLE* PREDICATE**, *"whatever that predicate is at the time
           of measurement"*. 17.3 landed S1 **ADVISORY** (specification section 6.5), so S1's
           reach — however large — is **not** a shipped promotion. The trigger is EVALUATED here
           by measurement and, on the evidence available at contexting, does not fire. ⛔ Measure
           it; do not assume it.

       (5) 0.10 — ⛔ **THIS STORY SPENDS NONE OF `DN-17-1-1`'s FOUR argus COSTS**, because it
           writes no `argus/` byte: no dogfood regeneration, no `Evidence-partition:` trailer (the
           `SEAL_CITATION_RULE` trailer fires only on `argus/detectors` and
           `argus/precision/replay_harness.py`), no `DOCS-001-54` wheel-figure move. 17.3 spent
           all four. ⛔ VERIFY this rather than assume it — if the measurement forces an `argus/`
           byte, all four come back and that is an AC10 escalation.

     ⛔ NOTHING HERE RATIFIES A MEMBER, FETCHES A THIRD-PARTY SOURCE, SPENDS `DF-13-5-A`'s ROUND,
     ADJUDICATES A ROW, AMENDS THE SEAL, ADDS A PROTOCOL ROW, MOVES A FROZEN FIELD, OR MAKES ANY
     FINDING VERDICT-ELIGIBLE. `scripts/precision_preregistration.py` stays BYTE-FROZEN and
     `successor-vacuity-predicate-specification.md` is CITED, never re-specified. Story 17.5 owns
     the six `DF-*` re-homings; they are NOT pulled in here. -->

## Story

As the **Engineering Lead**,
I want **the successor predicate `S1` measured exactly once over the five already-ratified members at their pinned shas, and the result folded through the criterion Story 17.1 froze in commit `f906d04`**,
so that **the outcome is decided by arithmetic that was written down while the answer was still zero — including when that arithmetic returns `UNEVALUABLE`.**

### What this story IS

The **measurement**, and nothing else. 17.1 wrote the standard. 17.2 wrote the predicate and
refused to say how far it reached. 17.3 built it and still refused. **This story runs it, once,
and reports what comes back.**

Its deliverable is three things and they are separable:

1. a **producer** that walks the 1,032 recorded `vacuous_test_heuristic` findings at the five
   pinned shas, scores each span with the **shipped** `S1`, and writes a machine record under a
   **declared** `SUCCESSOR_OUTPUT_PATHS` prefix;
2. the **fold** — the measured counts handed unmodified to
   `precision_preregistration.evaluate()`, and its `CriterionAssessment` recorded together with
   the counts and the reason string that produced it;
3. the **ordering guard** — the epic's binding constraint, asserted against the real object
   database rather than promised in prose, and it is the **inversion** of `-139` (§1.4).

### What it is NOT

⛔ **It is not a story that may move the bar.** If the measurement misses, the story records the
miss. There is no story-local threshold, no *"provisional"* floor, no fourth terminal state, and
no argument that a floor was set too high. `precision_preregistration.py` is **byte-frozen** and
`TC-ArgusAgent-PRECISION-001-140` enforces the direction: the ceiling may only fall, the ratio
may only rise, and `POPULATION_ID` / `PROTOCOL_VERSION` may not move at all.

⛔ **It is not a story that may acquire a population.** No corpus member is ratified, no member
moves between partitions, no sealed member is admitted, no third-party source is fetched, no
`DF-13-5-A` round is spent. **Reaching the gate by changing the corpus after seeing the number is
the named anti-pattern of this epic** (§2.1), and it is the one failure that would make all four
stories worthless at once.

⛔ **It is not an adjudication.** Nothing is judged TP or FP here (§1.2).

⛔ **It is not Story 17.5.** The six `DF-*` re-homings, the four Epic-18 scheduling notes and the
four shipped-module comment corrections are 17.5's by name. This story writes **exactly one**
ledger note, and it is `DF-13-5-A`'s trigger observation.

⛔ **It is not a promotion.** `CONSEQUENCE_MET` is explicit: meeting the criterion *"promotes
nothing and moves no gate condition"*. Nothing here flips a `verdict_eligible`, a `rule_id` or a
`depth_supported`, and the externalization gate stays `BLOCKED` at every outcome.

---

## §0 — PREMISES MEASURED BY EXECUTION at HEAD `682b074`

⛔ **Task 0 re-measures every row of this section before a line is written.** If any row has
moved, **say so loudly in the story record** and re-derive; do not paper over it and do not quote
this section as though it were still true (`AI-E9-7`).

### §0.0 The tree, the paths, the baseline

| fact | value at `682b074` |
|---|---|
| branch | `docs/merge-strategy-decision`, **17 ahead** of `origin/master` (`c2ce00f`) |
| working tree | ⛔ **NOT clean** — 2 staged peer-session paths (see the contexting note) |
| artifacts root | `_bmad-output/design-artifacts/ArgusAgent/` |
| criterion module | `scripts/precision_preregistration.py`, **774 lines**, ⛔ FROZEN |
| criterion guards | `tests/test_precision_preregistration.py`, 1,121 lines, `-135`..`-141` |
| `S1` implementation | `argus/detectors/assertion_strength.py`, **500 lines** |
| `S1` entry point | `argus/detectors/vacuous_test.py::VacuousTestDetector.successor_evidence` (`:791`) |
| the 1,032-finding harness | `scripts/build_silent_class_record.py`, **834 lines** |
| highest `TC-ArgusAgent-PRECISION-001-` id in use | **`-146`** → this story mints from **`-147`** |
| highest `TC-ArgusAgent-DETECT-001-` id in use | `-153` |
| `deferred-work.md` | 602,265 bytes, ⛔ **1 CR / 0 CRLF / 7,623 LF** — the lone-CR invariant |
| `sprint-status.yaml` | ⛔ **1,264 lines / 1,264 CR bytes**, `last_updated: 2026-08-25` |

### §0.1 What is FROZEN coming in, and what may not move

| artifact | state | enforced by |
|---|---|---|
| `scripts/precision_preregistration.py` | ⛔ **byte-frozen**; strengthening-only | `-140` (ceiling ≤ pin, ratio ≥ pin, `POPULATION_ID`/`PROTOCOL_VERSION` **equal**) |
| `successor-vacuity-predicate-specification.md` | CITED, never re-specified | `-142`..`-144` |
| `precision-validation-protocol.md` | byte-unchanged; `V1.3` is the change-log head | `refuse_protocol_drift` + `-135` |
| `adjudication-record.json` | byte-unchanged (this story adjudicates nothing) | AC7.4 |
| `silent-class-record.json` / `-worklist.md` | byte-identical before and after | AC9.3 neutrality control |
| `argus/` tree | byte-unchanged | AC5.4 |
| `vacuous_test.py::_ast_corroborated` return expression | unchanged | `-146` |

### §0.2 The criterion, RESOLVED at HEAD — not re-typed from any document

```
python -c "import sys;sys.path.insert(0,'scripts');import precision_preregistration as P;f=P.resolution_floors();print(P.precision_floor(),f.verdict_eligible_population,f.contributing_members,f.sealed_contributing_members,f.validation_set_floor_n,P.MAX_FALSE_ACCUSATION_EXPOSURE)"
```

| resolved quantity | value | meaning |
|---|---|---|
| ratio floor (`precision_floor()`) | **`Fraction(4, 5)`** | protocol §5's own locked threshold, the `Fraction` object itself |
| `verdict_eligible_population` floor | **5** | smallest denominator at which *"≥ 80%"* is not silently *"100%"* |
| `contributing_members` floor | **3** | a score drawn from one repository is not a score |
| `sealed_contributing_members` floor | **3** | …and they must be members the tool was never tuned against |
| `validation_set_floor_n` | **5** | the one locked `N`, reached through `corpus_manifest_module()` |
| `MAX_FALSE_ACCUSATION_EXPOSURE` | **26** | absolute integer cap, evaluated JOINTLY with and INDEPENDENTLY of the ratio |
| `PREREGISTRATION_COMMIT_SHA` | `f906d04997b391bea4592aabc0343d1234b3b060` | ⛔ **is an ancestor of HEAD** (re-checked) |
| `SUCCESSOR_OUTPUT_PATHS` | `…/validation-corpus/successor`, `_bmad-output/audit-reports/successor` | ⛔ **both ABSENT on disk at HEAD** (re-checked) |
| `CRITERION_OUTCOMES` | `MET`, `NOT_MET`, `UNEVALUABLE` | ⛔ closed at three |

⛔ **Import every one of these. Re-type none.** `AI-E9-7` / `DF-8-5-C`: a prose copy of a pinned
constant is a second source of truth that drifts silently, and this project has already paid for
one.

### §0.3 ⛔ `sealed ∩ ratified` IS EMPTY — RE-VERIFIED AT HEAD, AND IT DOES NOT MOVE HERE

```
python -c "from argus.precision.replay_harness import corpus_manifest_module as C;m=C();print(m.eligible_member_count());print(sorted(m.PRE_SEAL_MEMBER_IDS));print(m.SEALED_PARTITION_TABLE)"
```

| fact | measured at `682b074` |
|---|---|
| `eligible_member_count()` | **5** |
| eligible members | `minions`, `agent-smith`, `agent-markovich`, `xagents-webapp`, `ai-body-runtime` |
| `PRE_SEAL_MEMBER_IDS` | ⛔ **exactly those same five** |
| `SEALED_PARTITION_TABLE` sealed members | `aws-aws-sam-cli`, `celery-celery`, `certbot-certbot`, `conda-conda`, `getsentry-sentry-python`, `googleapis-google-auth-library-python` — ⛔ **none of them ratified** |
| **`sealed ∩ ratified`** | ⛔ **EMPTY** |
| therefore `sealed_contributing_member_count` over the pinned population | ⛔ **0**, against a floor of **3** |

⛔ **THIS IS NOT A PREDICTION ABOUT `S1`.** It is arithmetic about the *population*, and Story
17.1 §3.1 wrote it down **before any successor existed**: *"THE EXTERNALIZATION GATE CANNOT REACH
`CLEARED` FROM THIS MEASUREMENT, AT ANY RATIO. 'Precision came out at 84%, so the gate clears' is
FALSE, and it is written down here before anyone has a number to say it about."*

⛔ **THE ONLY THING THAT WOULD CHANGE IT IS A PROTOCOL §6 R2 OPERATOR ACT RATIFYING SEALED
MEMBERS, AND NO EPIC 17 STORY MAY TAKE ONE.** If the dev finds itself reasoning about how to make
the sealed arm clear, ⛔ **STOP** — that reasoning is the anti-pattern (§2.1, AC10.3).

### §0.4 ⛔ THE ADJUDICATED POPULATION — 31 / 26 FP / 5 BORDERLINE / **ZERO TP** — RE-COUNTED

```
python -c "import json,collections;d=json.load(open('_bmad-output/design-artifacts/ArgusAgent/validation-corpus/adjudication-record.json'));print(len(d['rows']),collections.Counter(r['disposition'] for r in d['rows']),collections.Counter(r['rule_id'] for r in d['rows']))"
```

| fact | measured |
|---|---|
| rows | **31** |
| `FP` | **26** — and this is exactly where `MAX_FALSE_ACCUSATION_EXPOSURE = 26` came from |
| `BORDERLINE` | **5** — the ladder engaged and did not terminate |
| **`TP`** | ⛔ **0, across the record's whole life** |
| `rule_id` | `vacuous_test_ast` on all 31 |
| `protocol_version` | `V1.3` |
| `reproducibility_verified` | `True`; `expert_hours` `None` |

⛔ **CONSEQUENCE FOR THE FOLD, AND IT IS THE SECOND INDEPENDENT `UNEVALUABLE` ARM.** These 31 rows
are `vacuous_test_ast` — the *shipped* rule class. There are **zero adjudicated rows of any
successor class**, and this story may not create any (§1.2). So the counts handed to `evaluate()`
carry `true_positive_count = 0` and `false_accusation_count = 0`, `precision_fraction(0, 0)`
returns `None`, and step (2) of the fold returns `UNEVALUABLE` — *"the adjudicated population is
EMPTY, so there is no denominator and no ratio to compare against the floor. Exhaustiveness over
nothing is the guard that passes forever (`AI-E11-1`)."*

⛔ **RECORD THAT SENTENCE, DO NOT ROUTE AROUND IT.** The measured precedent is `bc55e36`, where a
corpus that emitted nothing reported a **cleared** gate.

### §0.5 ⛔ THE TWO KNOWN BANDS OF (c′) DRAW FROM **TWO** MEMBERS — a prior, NOT a prediction

Read from `silent-class-record.json` at HEAD (`class_by_corpus_member`):

| band | definition | contributing members | reach |
|---|---|---|---|
| `V0` shipped | `disc ≥ 1 ∧ cons == 0 ∧ mref ≥ 1` | none — population empty | **0** |
| `V1` drop-mref | `disc ≥ 1 ∧ cons == 0` | **2** (`minions`, `agent-smith`) | 6 |
| `V2` silent | `disc ≥ 1 ∧ span asserts nothing` | **2** (`agent-smith` 22, `minions` 14) | **36** |
| `V5` unrelated | `disc ≥ 1 ∧ asserts, none about the SUT` | not measured per member | 125 (the research script's own `ast` reasoning) |
| **`S1`** | (a) ∧ (b′) ∧ (c′) | ⛔ **UNKNOWN — THIS STORY MEASURES IT** | ⛔ **UNKNOWN** |

⛔ **`V2 = 36` AND `V5 = 125` ARE NOT COMPARABLE PRIORS AND THEIR SUM IS NOT A PREDICTION.**
Specification §4 is explicit: they were measured **by two different instruments at two different
HEADs**, `V5` by the research harness's `ast.walk` and `V2` by the shipped tree-sitter index.
Adding them is arithmetic across two instruments. ⛔ **Do not report `S1`'s measured reach as
"confirming" or "missing" 161, 125 or 36.** Report it as what it is: the first measurement of
`S1` that has ever been taken.

⛔ **AND DO NOT ARGUE THE BREADTH FLOOR DOWN.** Specification §7.2 already refused: *"Story 17.1
already pre-registered the consequence for exactly this situation: the outcome is `UNEVALUABLE` —
NEVER a pass and NEVER a failure, and never an invitation to argue the floor down."*

### §0.6 The corpus is RUNNABLE at HEAD — locally, on Windows, and only there

All five pinned shas probed with `git cat-file -e <sha>^{commit}` at their real checkout paths
under `--checkout-root d:/ProjectX/XAgents/XAgents`:

| member | pinned sha | checkout (relative to root) | reachable | `vacuous_test_heuristic` findings |
|---|---|---|---|---|
| `minions` | `ec63b7293b70` | `Minions` | ✅ | **648** |
| `agent-smith` | `9ab774d7bf5d` | ⛔ `XAgents/Agent-Smith` — **one level deeper**, has cost a cycle before | ✅ | **295** |
| `agent-markovich` | `a561668636d8` | `AgentMarkovich` | ✅ | **72** |
| `xagents-webapp` | `33a86525a498` | `XAgents-WebApp` | ✅ | **17** |
| `ai-body-runtime` | `4480ffdeb4c5` | `ai_body_runtime` | ✅ | **0** |
| | | | | **TOTAL 1,032** of 4,284 emitted |

⛔ **`ai-body-runtime` contributes ZERO and is STILL a member of the population.** A member that
contributes nothing is a member the ratio was measured over, not a member quietly dropped from the
denominator (`POPULATION_DERIVATION`, verbatim).

⛔ **The run is LOCAL-ONLY.** CI has no third-party checkouts, so the producer is a **recorded
measurement with its command in the story record**, never a committed test — a test that needs the
checkouts reds every CI run. ⛔ **Every committed guard must be green on the ubuntu matrix with no
checkouts present**, which means guards read the *committed record* and the *object database*, not
the corpus.

⛔ **Use a SHORT `--snapshot-root` on Windows.** `build_silent_class_record.py`'s own `--help`
records that the deepest in-scope path can push the absolute path past `MAX_PATH` under the default
temp root, and *"a partially-extracted tree derives clean"* — i.e. it fails silently in the
dangerous direction.

### §0.7 ⛔ `S1` IS PUBLICLY CONSUMABLE — THE ONE DERIVATION, NAMED

`epics.md` predates Story 17.3 and does not know this. Measured by import at HEAD:

```python
from argus.detectors.vacuous_test import VacuousTestDetector
ev = VacuousTestDetector.successor_evidence(source_lines, span_edges, start, end)
# -> SuccessorVacuityEvidence(assertions_none, assertions_existence,
#                             assertions_value, assertions_unestablished, s1_corroborated)
```

- `argus.detectors.assertion_strength.__all__` = `('ASSERTION_STRENGTH_BANDS',
  'AssertionStrengthCounts', 'S1_SPECIFICATION', 'UNESTABLISHED', 'UnregisteredStrength',
  'grade_span_assertions', 's1_corroborated', 'strength_meaning', 'strength_ordinal')`.
- `s1_corroborated(source_lines, span_edges, start, end) -> bool` is the **whole** predicate — all
  three conjuncts, including fact (a) through `candidate_sut_edges` and (b′) through
  `provenance_evidence` with the **FROZEN** table. It is `PUBLIC on purpose (AC5.6)`, and its
  docstring names this story: *"Story 17.4 must be able to MEASURE the shipped predicate without
  re-deriving it. A private copy buried in the detector would force 17.4 to fork the predicate,
  which is the AR7 defect this epic exists to close."*
- `successor_evidence` is `COMPOSITION ONLY` — *"Reading this method and reading `s1_corroborated`
  must never be able to give different answers."*
- ⛔ `SuccessorVacuityEvidence` is deliberately **NOT** in `vacuous_test.__all__` (`-143` pins that
  list at nine). **Import it by path**, exactly as `assertion_strength` is imported.
- ⛔ `silent_class.SpanScore` does **NOT** carry `s1_corroborated` (its five fields are
  `discarded_sut_calls`, `consumed_sut_calls`, `mock_referencing_assertions`, `statement_count`,
  `asserts_anything`). ⛔ **Do not widen it** — `DETECT-001-119` pins `VacuousTestScore`'s field set
  exactly and `-143` pins the `__all__`; widening a model to fit new code, then editing the green
  guard that pinned it, is `DF-8-5-B` by name. Call `successor_evidence` **beside**
  `silent_class.score_span`, on the same `(source_lines, span_edges, start, end)`.

### §0.8 ⛔ THE POPULATION IS SINGLE-RULE-CLASS — do not invent a second axis

All 1,032 rows carry `rule_id = vacuous_test_heuristic` (`SILENT_CLASS_RULE_ID`, re-derived above).
`epics.md` AC1 asks for the distribution across *"contributing members and rule classes"*. ⛔ **The
rule-class axis has exactly ONE member and must be reported as one** — reporting *"1 rule class"*
is the measurement; manufacturing a second axis to make the report look richer is the `DF-8-5-C`
shape.

⛔ **The meaningful second axis already exists and 17.3 built it**: the assertion-strength band
distribution (`none` / `existence` / `value` / `unestablished`), which carries **no verdict weight**
in Epic 17 and is explicitly *"17.4's reporting axis"* (17.3 §0.5). Report it as counts, never as
rendered sets (NFR-D2 / AR4).

### §0.9 ⛔ `DF-13-5-A`'s TRIGGER, READ AS SHARPENED — its subject is the SHIPPED predicate

`deferred-work.md`, **TRIGGER SHARPENED 2026-08-24 by XAgent007**, condition 1 restated verbatim:

> **the count of findings the SHIPPED verdict-eligible predicate promotes over the five
> ALREADY-RATIFIED members — whatever that predicate is at the time of measurement — rises above
> ZERO.** Measured on the ratified corpus with **no member ratified, no third-party source fetched
> and no round spent**, with the harnesses under `research/` or their successors, and reported
> together with the predicate definition in force.

Condition 2: **2026-11-22**, ⛔ *"still not re-dated"*.

⛔ **`S1` IS ADVISORY.** Specification §6.5 and 17.3's AC6 both require it: `S1` moves no
`verdict_eligible`, no `rule_id`, no `depth_supported`, and `_ast_corroborated`'s return expression
is byte-unchanged (`-146`). ⛔ **So `S1`'s reach, whatever it turns out to be, is NOT a shipped
promotion and does NOT fire condition 1.** The shipped verdict-eligible predicate is still
`disc ≥ 1 ∧ cons == 0 ∧ mref ≥ 1`, which measured **0 of 1,032**.

⛔ **MEASURE IT ANYWAY.** The trigger says *"whatever that predicate is at the time of
measurement"*; the producer is already walking every span, so reporting the shipped predicate's
promotion count at the same HEAD costs one field and converts an assumption into a measurement.
⛔ **This story takes NO branch** (`epics.md` AC5): the entry stays **OPEN and UNSPENT**,
`branch_taken: NEITHER`, `members_ratified: NONE`, `round_state: UNSPENT`.

### §0.10 ⛔ THE FOUR `argus/` COSTS — AND THIS STORY SPENDS NONE OF THEM

| cost | trigger | spent here? |
|---|---|---|
| dogfood artifact regeneration | any `argus/` byte | ⛔ **NO** |
| `Evidence-partition:` commit trailer | a commit touching `argus/detectors` or `argus/precision/replay_harness.py` (`SEAL_CITATION_RULE` / `DETECTOR_TUNING_PATHS`) | ⛔ **NO** |
| `DOCS-001-54` wheel figures (README / CHANGELOG module + LOC counts) | a new `argus/` module | ⛔ **NO** |
| `mypy argus` / `bandit -r argus` / the coverage floor | always run; but nothing new to type-check under `argus/` | run as evidence |

⛔ **VERIFY, DO NOT ASSUME.** `git diff --stat HEAD -- argus/` must be **empty** at every commit of
this arc (AC5.4). If the measurement genuinely requires an `argus/` byte, that is an **AC10.2
escalation** with all four costs counted in the story record — not a quiet widening.

Two guards worth knowing are **not** in scope and must not be tripped:

- `TC-ArgusAgent-PRECISION-001-127` walks the `argus/` tree only and fences the promotion-class
  predicate out of the detector package. ⛔ **`scripts/` is outside its population** —
  `build_silent_class_record.py` already imports from `argus.detectors.secret_scan` and
  `argus.detectors.vacuous_test`, so the new producer may import `assertion_strength` freely.
- `tests/test_status_document_registry.py` globs `sprint-change-proposal-*.md` and
  `epic-*-retro-*.md` in the artifacts root only. A record under `validation-corpus/successor/`
  matches neither and must **not** be registered (registering it would turn the guard RED — this is
  `DN-17-1-8`'s exact reasoning, reused).

### §0.11 NFR-M1 headroom, and the split trigger PRE-REGISTERED before a line is written

`tests/test_module_size_ceiling.py` sweeps **every tracked `.py`** — `argus/`, `tests/` **and
`scripts/`** — at a **1,200-line** ceiling (`TC-ArgusAgent-MAINT-001-02`).

| file | lines at HEAD | headroom |
|---|---|---|
| `scripts/build_silent_class_record.py` (the model to imitate) | 834 | 366 |
| `scripts/precision_preregistration.py` | 774 (⛔ frozen) | — |
| `tests/test_precision_preregistration.py` | 1,121 | ⛔ **79** |
| `tests/test_assertion_strength.py` | 1,127 | ⛔ **73** |
| `tests/test_successor_predicate_specification.py` | 735 | 465 |
| `tests/test_successor_predicate_s1.py` | 269 | 931 |

⛔ **PRE-REGISTERED SPLIT TRIGGER** (17.3 §0.8's precedent, so a split is never discovered at
review): if the new producer projects **> 1,000 lines**, split the record model out first; if the
new test module projects **> 1,000 lines**, split it before writing the second half.

⛔ **`tests/test_precision_preregistration.py` HAS 79 LINES OF HEADROOM.** The ordering guard
(`-147`) is a substantial test with three non-vacuity preconditions and an executed RED
demonstration. ⛔ **Do not append it to that file.** It belongs in this story's **new** test module.
And ⛔ **do not edit `-135`..`-141`** — they are green and they belong to a frozen story.

### §0.12 What is already true and must NOT be re-done

- The criterion exists and is frozen — **do not re-write it, do not re-argue it, do not add a
  "17.4 acceptance threshold"** (`precision_floor()`'s docstring rejects exactly that).
- `S1` exists as shipped code — **do not re-specify it and do not re-implement it** (§0.7).
- `-139` already proves *no commit reachable from `f906d04` touches successor output*. ⛔ **This
  story's guard is the OTHER half** (§1.4) and `-139` is not edited.
- `DF-INV-VACUOUS-B` is already dispositioned moot-by-replacement (17.2) and `DF-AUD-DETECT-D` is
  already closed (17.3). ⛔ **Do not re-close either.**
- The `V2` class record already exists — **do not regenerate it**; prove it **byte-identical**
  instead (AC9.3 neutrality control).

---

## §1 — THE DECISIONS THIS STORY MAKES, AND WHY

### §1.1 ⛔ THE NUMBER DOES NOT EXIST YET, AND THESE ACs WERE WRITTEN WITHOUT IT

**DECISION.** The contexting session **deliberately did not run the measurement**, and no
acceptance criterion below names, bounds or predicts `S1`'s reach.

**Why.** This is the epic's whole discipline applied to its own story file. 17.1 froze the
criterion while the answer was zero. 17.2 §5.1 declined the per-member re-run that was *"one re-run
away"* precisely because *"a story chartered to prevent a number being fitted to a standard may not
publish a number that was never measured"* (`DN-17-2-4`), and because *"a story that quietly ran it
first would make 17.4's own ordering guard argue about a commit nobody planned"*. 17.3 published no
reach figure. ⛔ **A story file that arrived with the number in it would be the fourth story in a
row breaking the rule the first three kept.**

**Rejected:** *"measure it during contexting so the ACs can be sharper."* Sharper ACs written
against a known answer are a description of the answer in the grammar of a standard — the exact
sentence `precision_preregistration.py`'s module docstring opens with.

**What the ACs assert instead:** the **shape** of the record, the **provenance** of every figure,
the **identity** of the predicate, and **internal consistency** — that the recorded outcome
re-derives from the recorded counts through the frozen fold. ⛔ **No guard asserts a value.**
Non-vacuity is asserted **structurally** (`population_walked == 1032`, `population_skipped == 0`,
the member set equals the five ratified), never as *"reach > 0"* — a floor on the reach would be a
prediction, and a prediction is the thing being refused.

### §1.2 ⛔ THIS STORY DOES NOT ADJUDICATE — and therefore reports NO precision ratio

**DECISION.** Every row the producer writes is seeded `UNADJUDICATED`, with no adjudicator and no
date. The fold is called with `true_positive_count = 0` and `false_accusation_count = 0`, and
whatever it returns is recorded.

**Why, three reasons and each is sufficient.**

1. ⛔ **Protocol §2.** `UNADJUDICATED` is the **only** disposition an automated producer may write;
   the TP/FP judgement is the named human's act. `silent-class-record.json` says so in its own
   `transcription_note`: *"NOTHING ON THIS RECORD WAS TRANSCRIBED. Every row was SEEDED
   UNADJUDICATED … and carries no adjudicator and no date."*
2. ⛔ **`AI-E16-7` is UNFILLED.** Protocol §4's ladder — locator re-examination → golden-key
   correction → **external tie-break** — has no step-3 holder. `epics.md` states it as a
   precondition: *"Story 17.4 additionally requires `AI-E16-7` … to be filled before it can produce
   an adjudicated borderline, or it STOPS."* The record already carries **5 `BORDERLINE`** rows
   (§0.4) from the last time a human ran this ladder — 16% of the adjudicated rows. The base rate
   of reaching the third rung is not low.
3. ⛔ **17.1 §3.4 / `CONSEQUENCE_MET`.** Meeting the criterion *"promotes nothing"* and produces a
   **proposal**. A proposal does not require an adjudication to be a proposal.

**Consequence, stated plainly so nobody reads it as a dodge.** `epics.md` AC1 asks for *"the
precision measured under the protocol version 17.1 named"*. ⛔ **The pre-registered answer to a
measurement with no denominator is `UNEVALUABLE`, and `evaluate()` step (2) returns exactly that.**
Recording `UNEVALUABLE` **is** measuring the precision under the protocol — the protocol's own
answer to an empty denominator. ⛔ **What is forbidden is reporting `100%`, or `0%`, or omitting
the ratio and implying the population was fine.**

**Rejected:** *"seed the rows and have the dev agent judge a sample."* That is an operator act
taken by an automation, over a population whose ladder has no third rung, on the exact axis the
whole epic exists to protect. It is refused.

**⛔ AC7.3 stands regardless:** if a row ever *is* adjudicated in this story and the ladder does not
terminate, the story **STOPS** and reports which rows and why. It never resolves by default.

### §1.3 Where the producer and the record live

**DECISION — the producer and its record model live under `scripts/`**, not under the `argus/`
tree. Default name: `scripts/build_successor_reach_record.py`, modelled on
`scripts/build_silent_class_record.py` and on `scripts/precision_preregistration.py`'s precedent
(17.1 shipped a frozen measurement module in `scripts/`).

**Why.**

1. It is a **measurement producer**, not shipped detector behaviour. Nothing in the shipped package
   consumes it.
2. It keeps **all four `DN-17-1-1` costs unspent** (§0.10) for a story that ships no capability.
3. ⛔ **`-127`'s own reasoning argues against the alternative:** *"One import line is the whole
   distance between 'a question for a human' and 'a shipped verdict.'"* Making a successor-reach
   model importable from the shipped package, while the criterion says the successor is **not
   promoted**, builds exactly that import line.

**Counter-precedent, named rather than hidden:** the `V2` class record model lives at
`argus/precision/silent_class.py`. ⛔ **If the dev finds the model genuinely must be importable by a
shipped consumer, that is an AC10.2 escalation with the four costs counted — not a silent move.**

**The output artifact** lands under `SUCCESSOR_OUTPUT_PATHS[0]` =
`_bmad-output/design-artifacts/ArgusAgent/validation-corpus/successor/` — ⛔ **imported from the
criterion module, never re-typed** — and **nowhere else** (specification §8.2 pointer 1:
*"output committed elsewhere makes 17.4's ordering guard unprovable against the object database"*).

⛔ **NFR-S1.** No source byte of any corpus member reaches the machine record. If a human-readable
worklist is produced at all, it inherits 16.7's **four-part carve-out verbatim** — spans in that
Markdown file and nowhere else, read from the **pinned blob** and proved by blob hash, bounded to
the flagged test function, and **redacted to a locator** wherever the shipped hardcoded-secret
detector fires, with the redaction recorded on the row.

### §1.4 ⛔ THE ORDERING GUARD IS THE **INVERSION** OF `-139`, AND THAT CHANGES ITS NON-VACUITY

`-139` asserts an **absence**: *no commit reachable from `f906d04` touches successor output.* Its
non-vacuity problem is that a misspelled pathspec returns empty and is indistinguishable from a
clean ordering — solved with a control path known to carry commits.

⛔ **This story's guard (`-147`) asserts a UNIVERSAL over a population this story CREATES**: *for
every commit touching any `SUCCESSOR_OUTPUT_PATHS` entry, `PREREGISTRATION_COMMIT_SHA` is an
ancestor of it.*

⛔ **THE INVERSION.** Before this story, that population is **empty** and the universal is
**vacuously true**. ⛔ **The same "git log found nothing" state is a legitimate PASS for `-139` and
a DEAD GUARD here.** So `-147` must assert, as a first-class precondition, that the population is
**NON-EMPTY** — and it can only do that once this story's own output commit exists.

⛔ **THEREFORE THE COMMIT ORDER IS LOAD-BEARING:** `-147` **may not land in a commit earlier than
the first commit touching a `SUCCESSOR_OUTPUT_PATHS` entry.** Landing it first ships a guard that
passes by finding nothing, which is the failure mode 17.3's AC9.3 and `-127`'s docstring both name.

**Proving it RED.** The violating arrangement is *successor output committed without the
pre-registration as an ancestor*. ⛔ **Build it in a THROWAWAY repository under the scratch
directory** — `git init`, two commits, the successor path written in a commit that is not a
descendant of the stand-in criterion commit — and drive the guard's **pure predicate** against it.
⛔ **Never in this repository's object database**, and ⛔ **never with `git replace` / `git graft` /
`git commit-tree` against the shared tree**: a peer session commits to this branch (§2.5) and a
rewritten object graph is not recoverable by `git checkout`.

The predicate must therefore be **pure and exported** — commits in, offenders out — so the RED
demonstration drives the real seam rather than a re-implementation of it. This is
`tests/test_vacuous_cross_language.py:169`'s `_anchors_on_caret_or_dollar` shape, reused.

### §1.5 The fold is CALLED, never re-implemented — and the record carries its reason

**DECISION.** The outcome is produced by `precision_preregistration.evaluate(...)`, called with the
measured counts **unmodified**, and the record stores the returned `CriterionAssessment` in full:
`outcome`, `reason`, all seven counts, `measured_precision`, `ratio_floor`, `exposure_ceiling` and
the resolved `floors` **with their derivation strings**.

**Why the reason string is not optional.** `evaluate()`'s own docstring: *"A bare verdict is
unauditable — `NOT_MET` with no counts cannot be told apart from `NOT_MET` measured over four
findings."* And `ResolutionFloors` carries its derivations *"so the prose a record publishes and the
arithmetic the gate runs are one object rather than two statements that can disagree
(`DF-8-5-C`)"*.

⛔ **No re-implementation of the ordering of checks, of `precision_fraction`, or of any floor.**
⛔ **No injection of `floors=` or `ratio_floor=` with anything other than the resolved defaults** —
the injection points exist for a caller that already resolved them, not for a caller that wants
different ones.

⛔ **`CONSEQUENCE_BELOW` and `CONSEQUENCE_MET` are recorded VERBATIM from the imported constants**
where the outcome invokes them, never paraphrased (`AI-E9-7`).

### §1.6 `DF-13-5-A` — evaluated by measurement, and no branch taken

**DECISION.** The producer additionally reports the count the **shipped verdict-eligible predicate**
promotes over the same walk, together with that predicate's definition in force, and **one** dated
append-only ledger note records the observation against both trigger conditions.

⛔ **The note records an OBSERVATION, not a disposition.** No closure verb appears beside the entry.
`branch_taken: NEITHER`, `members_ratified: NONE`, `round_state: UNSPENT`, `protocol_edit: NONE`,
and the entry **STAYS OPEN**. Condition 2's `2026-11-22` backstop is ⛔ **not re-dated** — re-dating
it *"would convert a bounded deferral into a rolling one, which is precisely the silence this entry
forbids."*

### §1.7 What this story does NOT fix, named so it is not mistaken for fixed

- The externalization gate stays `BLOCKED`; `protocol_cleared` stays `False`; the ≥80% keystone
  stays **NOT CLEARED**; FR34's disclosure stands. At **every** outcome.
- `consumed == 0` is not loosened, reached or measured.
- `S1`'s threshold is not widened to admit the `existence` band — that is *"a SEPARATE, FUTURE ACT
  REQUIRING ITS OWN PRE-REGISTRATION"* (specification §2.2). ⛔ **Not a tuning knob**, and
  emphatically not one to reach for after seeing a reach figure.
- `DF-AUD-DETECT-C` (span-scan cost) stays **OPEN and undispositioned**.
- `DF-INV-VACUOUS-B`'s residual stays as 17.2 recorded it.
- The six `DF-*` re-homings and four Epic-18 scheduling notes are **Story 17.5's**.

---

## §2 — THE COUPLINGS THAT WILL BITE

### §2.1 ⛔ CORPUS-SHOPPING IS THE NAMED ANTI-PATTERN OF THIS STORY

If the measurement comes back short, there are four ways to make the gate reachable and ⛔ **all
four are forbidden**:

| tempting move | why it is refused |
|---|---|
| ratify a sealed member so `sealed_contributing_members` can clear | protocol §6 **R2 operator act**; spends `DF-13-5-A`; ⛔ **no Epic 17 story may take one** (17.1 §3.1) |
| add a corpus member so `contributing_members` reaches 3 | same act, same refusal. And `DF-13-5-A`'s own entry: *"A larger bench samples more repositories through an aperture that is structurally shut."* |
| amend `SEAL_CITATION_VALUES` / move a member between partitions | `SEAL_CITATION_RULE` names this failure mode by construction |
| lower a floor, or introduce a story-local threshold | `-140` turns **RED** on a loosening; `precision_floor()`'s docstring: *"a threshold set below the gate's own is a threshold chosen to be passable"* |

⛔ **`UNEVALUABLE` IS A RESULT.** 17.1 §3.2 calls it *"the most valuable pre-registered sentence
available to this story"*: **written now it is discipline; written after the measurement reports it,
it is a concession.** It was written on 2026-08-25 in `f906d04`, before `S1` existed. ⛔ **Record it
and stop.**

### §2.2 ⛔ THE GUARDS THAT WOULD GO GREEN BY FINDING NOTHING

Three in this story, and each needs its non-vacuity asserted **before** the claim it protects:

1. **`-147`, the ordering guard** — passes vacuously while no successor-output commit exists (§1.4).
   Assert the offender population is **non-empty** first.
2. **the "no successor output outside the declared prefixes" guard** — a sweep with a broken glob
   finds nothing and reports a clean tree. Assert the enumeration is real and two-sided
   (`MAINT-001-01`'s shape).
3. **the "no second derivation of `S1`" guard** — an `ast` walk that parsed zero files reports *"no
   second derivation"* forever. Assert the walk parsed the producer and resolved its **known-present
   outbound edge** to `assertion_strength` (`-127`'s own non-vacuity move, reused).

⛔ **Every guard is driven RED at its real seam by an EXECUTED mutation**, and ⛔ **no mutation
touches disk** — the tree is shared (§2.5). Mutate in memory, or in a throwaway scratch repo, and
verify byte-exact restoration by `sha256` where a file was involved. This is 17.3's discipline and
it survived review.

### §2.3 The commit arc — THREE commits, and the order is load-bearing

| # | commit | contains | why here |
|---|---|---|---|
| 1 | `feat(17-4): …` the producer | `scripts/build_successor_reach_record.py` + its unit guards + the `S1`-single-derivation guard | ⛔ **no successor output yet** — the producer is reviewable on its own |
| 2 | `chore(17-4): …` the measurement | ⛔ the record under `validation-corpus/successor/` (± the worklist) | ⛔ **the FIRST commit touching a `SUCCESSOR_OUTPUT_PATHS` entry** |
| 3 | `docs(17-4): …` the close-out | `-147` the ordering guard · the **one** `DF-13-5-A` ledger note · this story record · `sprint-status.yaml` | ⛔ `-147`'s non-vacuity precondition is satisfiable only **at or after** commit 2 (§1.4) |

⛔ **`-147` may be merged into commit 2 instead, but never into commit 1.**

⛔ **No `Evidence-partition:` trailer is required** on any of the three, because none touches
`argus/detectors` or `argus/precision/replay_harness.py` (§0.10). ⛔ **Verify with
`git diff --stat <sha> -- argus/` rather than asserting it.**

### §2.4 ⛔ THE LEDGER'S BYTE INVARIANTS AND ITS CLOSURE VOCABULARY

`deferred-work.md` is **602,265 bytes / 1 CR / 0 CRLF / 7,623 LF** at HEAD. ⛔ **Edit it in BINARY
mode** — a text-mode round-trip eats the lone CR and rewrites the whole file. ⛔ **Append-only**:
the note is dated, added beneath `DF-13-5-A`'s existing notes, and ⛔ **no line above it is
rewritten** (§3.4 evidence immutability).

⛔ **NO CLOSURE VERB beside `DF-13-5-A`.** It is an *observation against a trigger*, not a
disposition. ⛔ **Exactly ONE entry is written this round** (AC8.4/AC8.5).

⛔ **Grep the ledger before filing anything else** — it usually already knows, and re-filing known
prior art is its own defect.

### §2.5 ⛔ THE TREE IS SHARED

A peer session commits to `docs/merge-strategy-decision`, and **two of its paths are already
staged at contexting** (`sprint-status.yaml`, `stories/17-3-*.md`).

- ⛔ **Never `git add -A`.** Stage by explicit path and verify with `git status --porcelain`
  against the AC-declared write set before every commit.
- ⛔ **Never rewrite history, never `git replace`/`graft`/`commit-tree`, never `git stash`** —
  the RED demonstration goes in a throwaway repo (§1.4).
- ⛔ **`sprint-status.yaml` is edited SURGICALLY**: one status value per transition; `last_updated`
  only if it is not already today's date (it already reads `2026-08-25`). It must stay at
  **1,264 lines / 1,264 CR bytes**, and the comment blocks and the **STATUS DEFINITIONS** block must
  survive byte-for-byte.
- ⛔ **Do NOT use `sed -i` on `sprint-status.yaml`, on `deferred-work.md`, or on any artifact
  file** — GNU sed on this host flattens CRLF across the whole file.

### §2.6 ⛔ LOCAL GATES ARE WINDOWS-ONLY; CI IS AN UBUNTU MATRIX

`audit-ci.yml` triggers on `master`/`main` only and this branch is unpushed, so ⛔ **no CI evidence
exists at any sha in this arc** (`AI-E13-1`; epic-18 retro SD-4). ⛔ **Label every gate figure
LOCAL (Windows).** A green local suite has already shipped POSIX-only bugs to master.

Concretely for this story:

- ⛔ **Every committed guard must be green with NO third-party checkouts present** — otherwise it
  reds every CI run. Guards read the committed record and the object database; the corpus walk is a
  recorded local measurement.
- ⛔ **`SUCCESSOR_OUTPUT_PATHS` entries are used as git pathspecs verbatim** — forward-slash,
  repository-relative, never `os.path.join`, never a backslash. `-139` already asserts that shape;
  `-147` asserts it again for its own invocation.
- ⛔ **No `str.splitlines()`** anywhere on span text — use `index_aligned_lines` (the line-numbering
  contract). `splitlines()` splits on eleven things where the index counts one.
- ⛔ **No `^`/`$` regex anchors** — `\A`/`\Z` only (`DF-14-2-B`).
- ⛔ **`encoding="utf-8"` named on every read and write**; canonical JSON through
  `argus.store.canonical.dumps`/`loads`, exactly as `build_silent_class_record.py` does, so the
  record is byte-stable across platforms.
- ⛔ **No platform path separator and no `os.sep`** on any locator path — POSIX forward slashes,
  built from what the index gave you.
- ⛔ **Short `--snapshot-root`** on Windows (`MAX_PATH`; §0.6).

### §2.7 The idioms you need, so you do not go looking for them

| need | take it from |
|---|---|
| ⛔ **`S1` for one span** | `VacuousTestDetector.successor_evidence` (`vacuous_test.py:791`) — composition-only, imported by path |
| the read-only pinned-blob walk over five members | `scripts/build_silent_class_record.py::derive` / `_derive_member` (`:287` / `:358`) |
| the read-only git vocabulary, asserted rather than promised | `build_silent_class_record.READ_ONLY_GIT_COMMANDS` (`cat-file`, `ls-tree`, `rev-parse`, `status`) |
| materialize **and prove** the pinned bytes | `scripts/pinned_corpus_snapshot.py` — `pinned_tree`, `materialize_pinned_bytes`, `verify_pinned_bytes` |
| the checkout map (⛔ `agent-smith` is one level deeper) | `build_silent_class_record.DEFAULT_CHECKOUT_MAP` |
| a row seeded `UNADJUDICATED`, never transcribed | `silent_class.seed_row` + `build_silent_class_record._TRANSCRIPTION_NOTE` |
| the exhaustiveness / `gates_anything` payload shape | `silent_class.exhaustiveness_payload` |
| a REFUSAL instead of a silent skip | `build_silent_class_record.Refused` + the four `raise Refused(...)` sites in `derive` |
| the fold, and its outcome vocabulary | `precision_preregistration.evaluate` / `CRITERION_OUTCOMES` / `criterion_outcome_meaning` |
| the git-ancestry idiom with three non-vacuity preconditions | `tests/test_precision_preregistration.py:852` (`-139`) — ⛔ **read it before writing `-147`** |
| a pure, exported predicate with positive controls both ways | `tests/test_vacuous_cross_language.py:169` |
| an `ast` sweep that CLASSIFIES references rather than counting strings | `tests/test_silent_class.py:525` (`-127`) |
| a dated, append-only ledger note | `deferred-work.md` — `DF-13-5-A`'s own 2026-08-24 declination and sharpening |
| the source-span carve-out, verbatim | `build_silent_class_record._CARVE_OUT` |

---

## §3 — AC ↔ TASK MAP

| AC | what it protects | tasks | guards |
|---|---|---|---|
| AC1 | the measurement is real, complete and over the right population | 0, 1, 2 | `-148`, `-149` |
| AC2 | the criterion is called, not re-implemented, not amended | 2, 3 | `-150`, `-135`..`-141` re-run |
| AC3 | `UNEVALUABLE` is recorded as a result, not repaired | 2, 3 | `-150` |
| AC4 | the binding ordering constraint, proven against git | 4 | ⛔ `-147` |
| AC5 | ONE derivation for `S1`; the `argus/` tree untouched | 1, 2 | `-151` |
| AC6 | output lands where it was declared, and nowhere else | 2, 3 | `-152` |
| AC7 | nothing adjudicated; the ladder is not engaged | 2, 3 | `-149` |
| AC8 | `DF-13-5-A` evaluated, no branch taken, ONE note | 2, 5 | `-78` (record integrity) |
| AC9 | every guard non-vacuous and driven RED | 1, 3, 4, 5 | all |
| AC10 | escalate, do not decide | 0, 5 | — |

---

## Acceptance Criteria

### AC1 — THE MEASUREMENT RUNS ONCE, OVER THE PINNED POPULATION, AND REPORTS WHAT IT FINDS

**AC1.1** The producer walks **all 1,032** recorded `vacuous_test_heuristic` findings across the
five ratified members at their pinned shas, reading each member from its **pinned blob** through
`pinned_tree` / `materialize_pinned_bytes` / `verify_pinned_bytes`, and the record carries
`population_walked = 1032` and `population_skipped = 0`.

**AC1.2** ⛔ **A finding that cannot be resolved at the pin is a REFUSAL, never a skip.** The
producer raises (the `Refused` idiom) with the unresolved locators named. *"A skipped finding and a
non-member are indistinguishable in the output."*

**AC1.3** The record reports, as **counts** (NFR-D2 / AR4 — never rendered sets, never a `float`):
the **eligible population** (spans `S1` corroborates), its **distribution across contributing
members**, and its **distribution across rule classes** — ⛔ which is **exactly one**
(`vacuous_test_heuristic`), reported as one and not invented into more (§0.8).

**AC1.4** The record additionally reports the **assertion-strength band distribution**
(`none` / `existence` / `value` / `unestablished`) — 17.3's reporting axis, ⛔ carrying **no verdict
weight**.

**AC1.5** ⛔ **Every figure is DERIVED BY THIS RUN.** None is copied from `epics.md`, from
`V2 = 36`, from `V5 = 125`, or from their sum. ⛔ **The record does not describe `S1`'s reach as
confirming, missing or approaching any prior figure** — §0.5: two instruments, two HEADs, not
comparable.

**AC1.6** ⛔ **NO member ratified** (`eligible_member_count()` reads **5** before and after, and the
record says so), ⛔ **NO third-party source fetched** (the read-only git vocabulary is asserted, not
promised), ⛔ **NO round spent**.

**AC1.7** The record names its own `derivation_method` and `derivation_source`, in
`silent-class-record.json`'s house form, so a reader can reproduce it without re-running a detector.

### AC2 — THE CRITERION IS CALLED, NOT RE-IMPLEMENTED, AND NOT AMENDED

**AC2.1** The outcome is produced by `precision_preregistration.evaluate()`, called with the
measured counts **unmodified** and with the **resolved default** floors and ratio floor.

**AC2.2** ⛔ `scripts/precision_preregistration.py` is **BYTE-UNCHANGED** (`git diff` empty), and
`TC-ArgusAgent-PRECISION-001-135`..`-141` are re-run and recorded green — ⛔ **`-140` especially**,
which is the strengthening-only direction guard.

**AC2.3** The record stores the returned `CriterionAssessment` **in full**: `outcome`, `reason`,
all counts, `measured_precision`, `ratio_floor`, `exposure_ceiling`, and the resolved `floors`
**with their derivation strings**. ⛔ A bare verdict is unauditable.

**AC2.4** ⛔ **IF THE MEASUREMENT MISSES THE GATE, THE STORY RECORDS THE MISS.** No threshold is
moved; no story-local threshold is introduced; no floor is argued down; no terminal state is
invented (`CRITERION_OUTCOMES` stays closed at three, `CONDITION_VERDICTS` at four, `GATE_OUTCOMES`
at three). ⛔ Where the outcome invokes it, `CONSEQUENCE_BELOW` (or `CONSEQUENCE_MET`) is recorded
**verbatim from the imported constant**.

**AC2.5** ⛔ The story writes **no number** into the criterion module and **no value** into any
frozen field. `POPULATION_ID`, `PROTOCOL_VERSION`, `MAX_FALSE_ACCUSATION_EXPOSURE`,
`PREREGISTRATION_COMMIT_SHA` and `SUCCESSOR_OUTPUT_PATHS` are **imported and unmoved**.

### AC3 — `UNEVALUABLE` IS A RESULT, NOT A FAILURE, AND NOT A THING TO REPAIR

**AC3.1** If any resolution floor is short, the record carries `UNEVALUABLE`, the **shortfall
named** (measured count vs floor), and the floor's **own derivation string**.

**AC3.2** ⛔ The `sealed_contributing_member_count` is **reported as measured** and **not repaired**:
no member is ratified, no member moves between partitions, `SEAL_CITATION_VALUES` is not amended,
`SEAL_CONDITION_ID` is not touched.

**AC3.3** An **empty adjudicated population** is recorded as `UNEVALUABLE` with `AI-E11-1`'s reason
— ⛔ never as a flattering `100%`, never as `0%`, and never omitted with the population implied to
be fine.

**AC3.4** The record states `promotes_nothing: true` and `gates_anything: false`, and states in
terms that the externalization gate stays `BLOCKED` and the ≥80% keystone **NOT CLEARED** — ⛔ **at
every outcome, including `MET`** (`CONSEQUENCE_MET`, verbatim).

### AC4 — THE BINDING ORDERING CONSTRAINT, ASSERTED AGAINST GIT

**AC4.1** A committed guard `TC-ArgusAgent-PRECISION-001-147` asserts, by **git ancestry**, that
`PREREGISTRATION_COMMIT_SHA` is an ancestor of **every** commit touching **any**
`SUCCESSOR_OUTPUT_PATHS` entry.

**AC4.2** Both constants are **IMPORTED** from `scripts/precision_preregistration.py` and re-typed
neither (`DN-16-4-2` / `AI-E9-7`).

**AC4.3** ⛔ **Non-vacuity, three ways, each asserted BEFORE the claim:**
(a) the declared path set is **non-empty** and every entry is repository-relative and
forward-slash (portable as a git pathspec on both the Windows local gate and the ubuntu matrix);
(b) ⛔ **the offender-candidate population is asserted NON-EMPTY** — i.e. at least one commit does
touch a declared prefix. ⛔ **This is the inversion of `-139`** (§1.4): the same *"git log found
nothing"* state is a legitimate pass there and a dead guard here;
(c) the ancestry predicate is driven to **BOTH** outcomes on real, resolvable shas in this
repository, neither fabricated.

**AC4.4** ⛔ The guard is **driven RED against a violating arrangement**, built in a **throwaway
repository under the scratch directory**. ⛔ **Nothing is written to this repository's object
database, and no `git replace` / `graft` / `commit-tree` / history rewrite touches the shared
branch.** The guard's offender-finding predicate is **pure and exported** so the RED demonstration
drives the real seam.

**AC4.5** The guard is green on the ubuntu CI matrix **with no third-party checkouts present** — it
reads the object database only.

**AC4.6** ⛔ `-139` is **not edited**. It proves the complementary half and belongs to a closed
story (`DF-8-5-B`: a green guard is never edited to accommodate new code).

**AC4.7** ⛔ `-147` does **not** land in a commit earlier than the first successor-output commit
(§2.3).

### AC5 — ONE DERIVATION FOR `S1`, AND THE `argus/` TREE IS BYTE-UNCHANGED

**AC5.1** The producer obtains `S1` from the **shipped public surface** —
`VacuousTestDetector.successor_evidence`, or `assertion_strength.s1_corroborated` /
`grade_span_assertions` directly — and ⛔ **re-implements no conjunct** of it: not fact (a), not
fact (b′), not the band grading, not the statement boundary, not the SUT-derived-name resolution.

**AC5.2** ⛔ **No `import ast`, no re-parse, no second grammar call** on the producer's scoring
path. The research resolver (`research/investigate-per-call-scoping.py`) is ⛔ **not ported**.

**AC5.3** A guard (`-151`) walks the producer by `ast` and **fails on a second derivation** of
`S1`, of the span scoring, or of the statement boundary — with its non-vacuity asserted first (the
walk parsed the producer **and** resolved its known-present outbound edge to `assertion_strength`).

**AC5.4** ⛔ **`git diff --stat <base> HEAD -- argus/` is EMPTY** at every commit of the arc.
Consequently: no dogfood regeneration, no `Evidence-partition:` trailer, no `DOCS-001-54` wheel
figure moves. ⛔ **Verified by execution and recorded, not assumed.**

**AC5.5** `silent_class.SpanScore`, `VacuousTestScore` and `vacuous_test.__all__` are **unwidened**;
`_ast_corroborated`'s return expression is byte-unchanged (`-146` green).

### AC6 — THE OUTPUT LANDS WHERE IT WAS DECLARED, AND NOWHERE ELSE

**AC6.1** Committed successor output lands under a declared `SUCCESSOR_OUTPUT_PATHS` prefix and
⛔ **nowhere else**.

**AC6.2** The prefix is **imported** from the criterion module, never re-typed.

**AC6.3** A guard (`-152`) asserts that no successor-predicate output exists outside the declared
prefixes, with the enumeration asserted **real and two-sided** first (a broken glob finds nothing
and reports a clean tree).

**AC6.4** ⛔ **NFR-S1: no corpus source byte reaches the machine record.** If a human-readable
worklist is produced, it inherits 16.7's four-part carve-out **verbatim** (spans in that file and
nowhere else; read from the pinned blob and proved by blob hash; bounded to the flagged test
function; **redacted to a locator** where the shipped hardcoded-secret detector fires, with the
redaction recorded on the row). ⛔ **No span is copied into the story file, the ledger or any commit
message.**

**AC6.5** The record is canonical JSON (`argus.store.canonical`), byte-stable, and ⛔ **not
registered** in `tests/test_status_document_registry.py` (registering it would turn that guard RED —
`DN-17-1-8`).

### AC7 — NOTHING IS ADJUDICATED, AND THE LADDER IS NOT ENGAGED

**AC7.1** Every row is seeded `UNADJUDICATED`, with **no adjudicator and no date**, and the record
carries a transcription note stating that nothing was transcribed.

**AC7.2** ⛔ `AI-E16-7` is recorded as a **stated precondition that was NOT REACHED** — because
nothing was adjudicated — ⛔ **never as "satisfied" and never silently omitted.**

**AC7.3** ⛔ **If any row is adjudicated in this story and protocol §4's ladder does not terminate,
the story STOPS and reports which rows and why.** It never resolves by default and never invents a
tie-break.

**AC7.4** `adjudication-record.json` is **byte-unchanged**; `MAX_FALSE_ACCUSATION_EXPOSURE`'s pinned
blob (`EXPOSURE_SOURCE_SHA`) still re-derives to **26** (`-136` green).

**AC7.5** The record's exhaustiveness payload states `exhaustive: false` with the gap named and
what would close it — 16.7's shape, reused.

### AC8 — `DF-13-5-A` EVALUATED, AND NO BRANCH TAKEN

**AC8.1** Condition 1 **as sharpened 2026-08-24** is evaluated ⛔ **by measurement at HEAD**: the
count the **shipped verdict-eligible predicate** promotes over the five ratified members, reported
**together with that predicate's definition in force** (the trigger's own requirement).

**AC8.2** Condition 2 (`2026-11-22`) is checked against the run date and ⛔ **not re-dated**.

**AC8.3** ⛔ **`S1`'s reach is NOT reported as a shipped promotion.** 17.3 landed `S1` advisory
(specification §6.5); the trigger's subject is the shipped verdict-eligible predicate.

**AC8.4** The observation is recorded in ⛔ **exactly ONE** dated, append-only ledger note beneath
`DF-13-5-A`'s existing notes, with ⛔ **no closure verb**, `branch_taken: NEITHER`,
`members_ratified: NONE`, `round_state: UNSPENT`, `protocol_edit: NONE`, entry **OPEN**.

**AC8.5** ⛔ **No other ledger entry is written, edited, closed or dispositioned.** Story 17.5's six
re-homings and four scheduling notes are **not** pulled in. `deferred-work.md`'s **1 CR / 0 CRLF**
invariant holds and every byte above the new note is unchanged.

### AC9 — THE GUARDS, EACH WITH AN OBSERVABLE AND AN EXECUTED MUTATION

**AC9.1** New guards are minted from **`TC-ArgusAgent-PRECISION-001-147`** upward (`-146` is the
highest in use). Each carries, in its docstring: the **observable**, the **defect it moves**, and
the **non-vacuity** it asserts first.

**AC9.2** ⛔ Each is driven **RED at its real seam by an EXECUTED mutation**, and ⛔ **no mutation
touches disk** in this repository. Where a file must be involved, use a throwaway scratch tree and
verify byte-exact restoration by `sha256`.

**AC9.3** ⛔ **NEUTRALITY CONTROL:** `silent-class-record.json` and `silent-class-worklist.md` are
proven **BYTE-IDENTICAL** before and after this story
(`build_silent_class_record.py --check`, exit 0), and the `argus/` tree is byte-unchanged. A
measurement that moved the thing it measured is not a measurement.

**AC9.4** ⛔ **No guard asserts a predicted value.** `-150` asserts **internal consistency** — the
recorded outcome and reason re-derive from the recorded counts through the **frozen fold** — not
that the outcome equals any particular member of `CRITERION_OUTCOMES`.

**AC9.5** New modules stay under NFR-M1's **1,200** lines; the §0.11 split trigger (1,000) is
honoured **before** the second half is written, not discovered at review.

**AC9.6** ⛔ `-135`..`-146` are **not edited**. Local gates re-run and recorded **LOCAL (Windows)**:
`pytest`, `mypy argus`, `bandit -r argus --severity-level medium`, the coverage floor, and
`-127` / `-140` / `-146` / `-78` explicitly.

### AC10 — ESCALATE, DO NOT DECIDE

**AC10.1** ⛔ **Task 0 re-measures every §0 row by execution before a line is written.** Any row
that has moved is reported **loudly** in the story record — with the old value, the new value and
the command — and the story re-derives rather than quoting.

**AC10.2** If the measurement requires an `argus/` byte, or requires the record model to live under
the `argus/` tree: ⛔ **escalate**, with all four `DN-17-1-1` costs counted, before writing it.

**AC10.3** ⛔ **STOP** if reaching a non-`UNEVALUABLE` outcome would require: ratifying a member,
moving a member between partitions, amending the seal, adding a protocol row, spending
`DF-13-5-A`'s round, fetching a third-party source, or moving any frozen field. ⛔ **That is
corpus-shopping, it is this epic's named anti-pattern, and no amount of local justification makes
it permissible.**

**AC10.4** ⛔ **STOP** if the criterion module would have to change for the fold to be callable.

**AC10.5** ⛔ **STOP** if a row reaches protocol §4's third rung (AC7.3).

**AC10.6** ⛔ If the pinned corpus is unreachable, or a pinned blob fails `verify_pinned_bytes`:
**REFUSE** and report. Do not measure a tree nobody pinned.

---

## Dev Notes

### Decisions this story TAKES, each with its rejected alternative

| # | decision | rejected alternative, and why |
|---|---|---|
| `DN-17-4-1` | ⛔ **The ACs were written WITHOUT the number**; the contexting session did not run the measurement | *"measure first so the ACs can be sharper"* — sharper ACs against a known answer are a description of the answer in the grammar of a standard (§1.1) |
| `DN-17-4-2` | ⛔ **This story does not adjudicate**; rows are seeded `UNADJUDICATED` and the fold sees an empty denominator | *"judge a sample"* — an operator act (protocol §2) taken by an automation, on a ladder with no third rung (`AI-E16-7`) (§1.2) |
| `DN-17-4-3` | ⛔ **The producer and record model live under `scripts/`**; the `argus/` tree is byte-unchanged | `argus/precision/successor_reach.py` — the `silent_class.py` counter-precedent, named. It costs all four `DN-17-1-1` costs and builds the one import line `-127` exists to prevent (§1.3). ⛔ Reversible via AC10.2 escalation |
| `DN-17-4-4` | ⛔ **`-147` asserts a UNIVERSAL and needs a NON-EMPTY population**, so it may not land before the first successor-output commit | mirroring `-139`'s emptiness assertion — the same *"found nothing"* state is a pass there and a dead guard here (§1.4) |
| `DN-17-4-5` | ⛔ **The RED demonstration is built in a throwaway repo**, never in this object database | `git replace` / `graft` on the shared tree — a peer session commits to this branch and a rewritten graph is not recoverable (§2.5) |
| `DN-17-4-6` | ⛔ **`S1` comes from `successor_evidence`**; nothing is re-derived | a local re-implementation, or porting the research `ast` resolver — the AR7 defect the epic exists to close, and 17.3 made the surface public for exactly this (§0.7) |
| `DN-17-4-7` | ⛔ **The rule-class axis is reported as ONE class** | manufacturing a second axis to make the report look richer — `DF-8-5-C` (§0.8) |
| `DN-17-4-8` | ⛔ **`DF-13-5-A`'s condition 1 is measured on the SHIPPED predicate**, and `S1`'s advisory reach is not a promotion | reporting `S1`'s reach as the trigger metric — the trigger's own words are *"the SHIPPED verdict-eligible predicate"* (§0.9) |
| `DN-17-4-9` | ⛔ **Non-vacuity is asserted STRUCTURALLY** (`walked == 1032`, `skipped == 0`, member set == the five) | a floor on the reach (*"reach > 0"*) — that is a prediction, and a prediction is the thing being refused (§1.1) |

### Locked decisions this story CITES rather than reopens

- **The 2026-08-17 rule** — the branch was chosen before Story 13.5 ran, before the bench was
  chosen, before any number existed. Unamended.
- **`DN-3`** — one floor, never forked; `sealed_member_floor` calls `contributing_member_floor`.
- **`DN-17-1-4`** — `MAX_FALSE_ACCUSATION_EXPOSURE` is frozen as a **literal** because the record
  grows and **this story appends to it**. ⛔ A live ceiling would move the moment the number it
  judges came into view.
- **`DN-17-1-5`** — the criterion judges the **successor**, not the **gate**.
- **`DN-17-1-6`** — strengthening only: the ceiling may fall, the ratio may rise, `POPULATION_ID`
  and `PROTOCOL_VERSION` may not move. `-140`.
- **`DN-17-1-8`** — the pre-registration is deliberately unregistered in `_STATUS_DOCUMENTS`.
- **`DN-17-2-4`** — a story chartered to prevent a number being fitted to a standard may not publish
  a number that was never measured.
- **The 2026-08-20 operator decision** — *"a decision folded across an amendment is a
  re-interpretation of judgements nobody re-made"*; no protocol version row is added.
- **`SEAL_CITATION_RULE`** — amending the seal citation values is the corpus-shopping failure mode,
  by name.

### Open ledger entries bearing on this story — ⛔ verify against `deferred-work.md` on disk

| entry | status at contexting | this story |
|---|---|---|
| `DF-13-5-A` | **OPEN and UNSPENT**; declined twice (2026-08-22, 2026-08-24); trigger sharpened 2026-08-24 | ⛔ **evaluates the trigger, writes ONE observation note, takes NO branch** |
| `DF-INV-VACUOUS-A` | OPEN — the stage mismatch; 1,032 / stage 1 `density_only` 1,025 (100%) / stage 2 promotes 0 | cited; ⛔ re-homing is **17.5's** |
| `DF-INV-VACUOUS-B` | dispositioned **moot-by-replacement** by 17.2 | ⛔ **not re-closed** |
| `DF-AUD-DETECT-C` | OPEN and **undispositioned** (span-scan cost) | ⛔ **untouched** — this is not a performance story |
| `DF-AUD-DETECT-D` | **closed** by 17.3 at `ea2c2f5` | ⛔ **not re-closed** |
| `DF-16-7-A` / `-B`, `DF-12-2-D`, `DF-12-3-A`, `DF-14-1-A` | OPEN, naming Story 6.2 | ⛔ **Story 17.5's six re-homings — NOT pulled in** |
| `DF-AUD-DETECT-A`/`-B`/`-E`/`-F` | Epic 18 | ⛔ **17.5's scheduling notes — NOT pulled in** |

### Dependencies — none are added, and that is a requirement

The producer uses only what is already vendored: the shipped `argus` package,
`scripts/pinned_corpus_snapshot.py`, `scripts/precision_preregistration.py`, and the standard
library. ⛔ **No new third-party dependency, no network access, no clock, no `uuid4`, no `random`,
and no environment read on any derivation path.**

### Standing rules (non-negotiable)

1. ⛔ **Never `git add -A`** — the tree is shared and two peer paths are already staged.
2. ⛔ **Never `sed -i`** on `sprint-status.yaml`, `deferred-work.md` or any artifact file.
3. ⛔ **`deferred-work.md` is edited in BINARY mode** (1 CR / 0 CRLF invariant), append-only.
4. ⛔ **`sprint-status.yaml` stays at 1,264 lines / 1,264 CR bytes**, comments and STATUS
   DEFINITIONS byte-preserved.
5. ⛔ **Label every gate figure LOCAL (Windows)** — no CI evidence exists on this branch.
6. ⛔ **Counts, never rendered sets. No `float`.** (NFR-D2 / AR4.)
7. ⛔ **A failure is a RECORDED condition, never an uncaught raise** on a derivation path (NFR-R1) —
   except where refusing a malformed input at construction is correct, which `evaluate()` already
   does and this producer imitates.
8. ⛔ **Grep `deferred-work.md` before filing anything.**

### Project Structure Notes

- `scripts/` — measurement producers and the frozen criterion. ⛔ **Outside `-127`'s population**,
  so importing `argus.detectors.assertion_strength` here is fine and already precedented by
  `build_silent_class_record.py`.
- `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/successor/` — ⛔ **created by this
  story**, and it is the **only** place successor output may be committed.
- `tests/` — one new module for this story's guards. ⛔ **Not appended to
  `tests/test_precision_preregistration.py`** (79 lines of headroom, and it belongs to a frozen
  story).
- ⛔ **No file under the `argus/` tree is created or edited.**

**Detected variance, with rationale:** the `V2` class record model lives at
`argus/precision/silent_class.py` while this story's model lives under `scripts/`. Recorded as
`DN-17-4-3` with its reasoning and its escalation path, rather than silently diverging.

### Previous-story intelligence

- **17.1** (`f906d04` + the follow-up that filled its own sha): froze the criterion as **code, not
  prose** — *"Prose is not falsifiable; a module walked by an AST guard is."* Seven guards. ⛔ Its
  §3.1/§3.2 pre-wrote both `UNEVALUABLE` arms this story will hit. Its one review finding was **an
  unanchored whole-document regex** — anchor every extraction.
- **17.2** (`126f502`, `579a342`): specified `S1` and ⛔ **refused to publish its reach**, handing it
  here by name. Quoted `SILENT_CLASS_DEFINITION` **verbatim from the imported constant** rather than
  re-typing it — do the same with `CONSEQUENCE_BELOW` / `CONSEQUENCE_MET`. Wrote **exactly one**
  ledger entry.
- **17.3** (`4336d48`..`682b074`, five commits plus a fix round): built `S1` **advisory**; made
  `s1_corroborated` and `successor_evidence` **public on purpose for this story**; landed evidence
  on a **sibling model** rather than widening a pinned one (`DN-17-3-14`); pre-registered a split
  trigger before writing; wrote **exactly one** ledger entry.
  ⛔ **Its review finding is the lesson to carry:** a span-wide observed-line set leaked `value`
  into unrelated sibling assertions. The repair was **a projection, never a second walk**, proven
  output-identical over 3,259 spans with **zero** divergences. ⛔ **Prove neutrality by
  re-derivation over the real population, not by argument.**
- Across all three: ⛔ **exactly one ledger entry per story**, dated and append-only; ⛔ **every
  guard driven RED by an executed mutation that never touches disk**; ⛔ **every §0 premise
  re-measured at HEAD before writing**.

### Git intelligence

`682b074` `docs(17-3): close review iteration 1's finding; record the round-2 fix` ·
`7e72d91` `chore(17-3): regenerate the dogfood artifacts at f738df0` ·
`f738df0` `fix(17-3): scope the fail-closed band rule to the observing block's OWN lines` ·
`ea2c2f5` `docs(17-3): close DF-AUD-DETECT-D; record the 17.3 dev round` ·
`8516297` `chore(17-3): regenerate the dogfood artifacts at 90b5235`

**Patterns to copy:** one concern per commit; the ledger note, the story record and the
`sprint-status.yaml` transition land **together in the last commit**; dogfood regeneration is
**always its own commit** (⛔ not needed here — no `argus/` byte moves); commit subjects are
`type(story): imperative`.

### References

- [epics.md](../epics.md) — Epic 17: the binding ordering constraint, the `AI-E16-7` precondition,
  and Story 17.4's five acceptance criteria
- [successor-predicate-precision-preregistration.md](../successor-predicate-precision-preregistration.md)
  — §2 the criterion · §3.1 the gate cannot clear from this measurement · §3.2 both candidates
  `UNEVALUABLE` on breadth · §3.3 `CONSEQUENCE_BELOW` · §3.5 `AI-E16-7` · §4 what the act does not
  do · §5 the hand-off to this story
- [successor-vacuity-predicate-specification.md](../successor-vacuity-predicate-specification.md)
  — §2.1 `S1`'s three conjuncts · §2.2 the threshold, pre-refused from widening · §4 the two
  instruments and the two HEADs · §6.5 advisory · §7.2 the breadth floor is not argued down ·
  §8.2 the three pointers to this story
- [precision-validation-protocol.md](../precision-validation-protocol.md) — §2 who validates ·
  §4 the adjudication method and the borderline ladder · §5 thresholds · §6 R2 · §7 the OI1 lock
- [deferred-work.md](../deferred-work.md) — `DF-13-5-A` (declination 2026-08-24; trigger sharpened
  2026-08-24) · `DF-INV-VACUOUS-A` · `DF-AUD-DETECT-C`
- `scripts/precision_preregistration.py` — `evaluate`, `resolution_floors`, `precision_floor`,
  `CRITERION_OUTCOMES`, `SUCCESSOR_OUTPUT_PATHS`, `PREREGISTRATION_COMMIT_SHA`
- `scripts/build_silent_class_record.py` — `derive`, `_derive_member`, `Refused`,
  `READ_ONLY_GIT_COMMANDS`, `DEFAULT_CHECKOUT_MAP`, `_CARVE_OUT`
- `argus/detectors/vacuous_test.py:791` — `successor_evidence` ·
  `argus/detectors/assertion_strength.py` — `s1_corroborated`, `grade_span_assertions`
- `tests/test_precision_preregistration.py:852` — `-139`, the ancestry idiom this story inverts

---

## Tasks & Subtasks

### ⛔ Task 0 — RE-MEASURE §0 BEFORE WRITING ANYTHING (AC10.1)

- [x] Re-run every command in §0.2, §0.3, §0.4 and §0.6 and record the output verbatim in the Dev
      Agent Record.
- [x] Re-check `git merge-base --is-ancestor f906d04… HEAD`, and that **both**
      `SUCCESSOR_OUTPUT_PATHS` prefixes are **absent on disk**.
- [x] Re-run `-135`..`-141`, `-146`, `-127`, `-78` and record green.
- [x] Capture baseline hashes of `silent-class-record.json`, `silent-class-worklist.md`,
      `adjudication-record.json`, `scripts/precision_preregistration.py`, and
      `git rev-parse HEAD:argus`, for the AC5.4 / AC9.3 neutrality proofs.
- [x] ⛔ **Any row that has moved is reported LOUDLY** — old value, new value, command — and §0 is
      re-derived, not quoted.
- [x] ⛔ Re-check `git status --porcelain` for the peer session's staged paths and record the exact
      write set you will stage.

### Task 1 — THE PRODUCER (AC1, AC5, AC9.5)

- [x] Write `scripts/build_successor_reach_record.py`, modelled on `build_silent_class_record.py`:
      read-only git vocabulary, `DEFAULT_CHECKOUT_MAP`, `--check` / `--checkout-root` / `--map` /
      `--snapshot-root`, and `Refused` on any unresolvable finding.
- [x] Score each span with ⛔ **`VacuousTestDetector.successor_evidence`**, beside
      `silent_class.score_span`. ⛔ **Re-derive nothing.**
- [x] Record model in the same module (⛔ split at 1,000 lines per §0.11): counts, no `float`,
      canonical JSON, `population_walked` / `population_skipped`, the per-member distribution, the
      band distribution, `promotes_nothing` / `gates_anything`, the exhaustiveness payload, the
      transcription note, and the **shipped-predicate promotion count** for AC8.1.
- [x] Write the single-derivation guard `-151` (AC5.3), with its non-vacuity first.

### Task 2 — RUN IT ONCE, AND FOLD IT (AC1, AC2, AC3, AC6, AC7, AC8.1)

- [x] ⛔ **Run the producer ONCE** against the five checkouts (`--checkout-root
      d:/ProjectX/XAgents/XAgents`, short `--snapshot-root`). Record the exact command and its
      output.
- [x] Verify `population_walked == 1032`, `population_skipped == 0`, contributing members are a
      subset of the five ratified, and `eligible_member_count() == 5`.
- [x] Call `precision_preregistration.evaluate()` with the measured counts **unmodified**; store the
      full `CriterionAssessment`, including the reason and the floors' derivations.
- [x] ⛔ **Record whatever comes back.** If it is `UNEVALUABLE`, record the shortfall and the floor's
      derivation. If it is `NOT_MET`, record `CONSEQUENCE_BELOW` verbatim. If it is `MET`, record
      `CONSEQUENCE_MET` verbatim — including that it **promotes nothing** and the gate stays
      `BLOCKED`. ⛔ **Do not tune, reinterpret or amend anything.**
- [x] Write the record under `SUCCESSOR_OUTPUT_PATHS[0]` (imported), and ⛔ **nowhere else**. If a
      worklist is produced, apply the four-part carve-out and the secret redaction.
- [x] Measure the **shipped** verdict-eligible predicate's promotion count over the same walk, with
      its definition in force (AC8.1).
- [x] ⛔ Confirm `git diff --stat -- argus/` is empty and `adjudication-record.json` is
      byte-unchanged.

### Task 3 — THE CONSISTENCY AND OUTPUT-LOCATION GUARDS (AC2, AC3, AC6, AC7, AC9.4)

- [x] `-148` / `-149`: the record's population and member set re-derive from
      `adjudication-set-13-5.json`; every row is `UNADJUDICATED` with no adjudicator and no date;
      `exhaustive: false`; `AI-E16-7` recorded as **not reached**.
- [x] `-150`: ⛔ **the recorded outcome and reason RE-DERIVE from the recorded counts through the
      frozen fold.** ⛔ **Assert no particular outcome value.** Drive it RED by mutating a count in
      an in-memory copy of the record.
- [x] `-152`: no successor output outside the declared prefixes; enumeration asserted real and
      two-sided first.

### Task 4 — THE ORDERING GUARD (AC4)

- [x] ⛔ **Only at or after the successor-output commit.** Write `-147` in the new test module.
- [x] Import `PREREGISTRATION_COMMIT_SHA` and `SUCCESSOR_OUTPUT_PATHS`; re-type neither.
- [x] Assert the three non-vacuity preconditions (AC4.3), ⛔ **including the NON-EMPTY offender
      population** — the inversion of `-139`.
- [x] Extract the offender-finding predicate as **pure and exported**; drive it RED in a
      ⛔ **throwaway repo under the scratch directory**. ⛔ **Nothing written to this object
      database; no history rewrite on the shared branch.**
- [x] Confirm the guard needs no third-party checkout (CI-safe).

### Task 5 — LEDGER, RECORD, AND THE TRANSITION (AC8, AC9.3, AC9.6, AC10)

- [x] ⛔ Re-prove `silent-class-record.json` / `silent-class-worklist.md` **byte-identical** and the
      `argus/` tree byte-unchanged.
- [x] Write ⛔ **exactly ONE** dated, append-only `DF-13-5-A` observation note in **binary mode**;
      verify **1 CR / 0 CRLF** and that every byte above it is unchanged. ⛔ **No closure verb.**
      ⛔ **No other entry touched.**
- [x] Run the local gates and record them **LOCAL (Windows)**: `pytest`, `mypy argus`,
      `bandit -r argus --severity-level medium`, coverage, and `-127` / `-140` / `-146` / `-78`.
- [x] Fill the Dev Agent Record: the exact measurement command, the outcome, the counts, the fold's
      reason, and every §0 row that moved.
- [x] Update `sprint-status.yaml` **surgically** (1,264 lines / 1,264 CR bytes preserved); stage by
      **explicit path**; commit per the §2.3 arc.
- [x] ⛔ If any AC10 condition fired, **STOP and escalate** rather than proceeding.

---

## Dev Agent Record

### Agent Model Used

`bmad-dev-story` (Opus 5), round 1 `implement`, 2026-08-25 → 2026-08-26 (the clock rolled over
mid-run; see "Dates" below). Baseline `682b074`, branch `docs/merge-strategy-decision`.

`bmad-dev-story` (Opus 5), **round 2 `fix`, 2026-08-26** — the operator resolution of round 1's
escalation, and the completion of the arc. Same baseline, same branch.

---

### ⛔ ROUND 2 (2026-08-26) — THE ESCALATION WAS RESOLVED BY THE OPERATOR, AND THE STORY IS COMPLETE

⛔ **THE MEASUREMENT DID NOT MOVE, WAS NOT RE-RUN, AND WAS NOT RE-RECORDED.** Round 2 changed no
count, no floor, no reason and no outcome. The record committed at `5bf27ca` is **byte-identical**
to the artifact round 1 wrote — `--check` exit 0, 85 rows, `UNEVALUABLE`, sealed contributing
members **0** below the floor of **3**. ⛔ Nothing was tuned, ratified, sealed, adjudicated or
reinterpreted, and **no figure recorded below changed for any reason**.

#### ⛔ THE OPERATOR DECISION, RECORDED AS SUCH

⛔ **Authorized by the human operator on 2026-08-26**, through this story's dev loop, after round 1
**halted rather than deciding it alone** (which was the right call — AC10: *escalate, do not
decide*).

> **`AC9.6` IS AMENDED, NARROWLY AND FOR `TC-ArgusAgent-PRECISION-001-146` PART (2) ONLY**, to
> permit **RE-SCOPING** that part from a **filesystem existence** check to a claim over **Story
> 17.3's OWN COMMIT RANGE** — *"no commit of 17.3's arc created these paths"* — which is permanent
> and checkable rather than self-destructing the moment 17.4 legitimately writes its output.

⛔ **The rationale the operator recorded, and it is a precedent rather than a novelty:** this is the
**same repair this epic already accepted as `DN-17-2-12`**, where `-144`'s git half was scoped to
its own story's `(17-2)`-tagged commits *precisely because the literal wholesale form would redden
the moment a later story legitimately wrote inside the fenced area*. Story 17.2's code review
judged that sound at the time. ⛔ **Re-scoping preserves the guard's real intent; deleting it would
not.**

⛔ **Two alternatives were considered by the operator and REJECTED**, and they are recorded so the
decision is auditable rather than merely stated:

| rejected option | why it was refused |
|---|---|
| **retire part (2) into `-152`** | `-152` is this story's guard and is correct after 17.4 as well as before it — but retiring part (2) costs the same AC9.6 amendment *and* strips a third of `-146`'s stated observable from the story that owns it |
| **defer the committed artifact (and `-147`) to a follow-up** | AC4 and AC6 would go unmet in 17.4 and `-147` — the epic's own *binding constraint* — would never be minted here |

⛔ **THE FENCES THAT DID NOT MOVE.** Parts (1) and (3) of `-146` are **byte-untouched**. No other
frozen guard moved: `-135`..`-145` are unedited, `scripts/precision_preregistration.py` is
**BYTE-FROZEN** (sha256 `f31ae29c…`, `git status` empty) and `-140` did not move. Verified by
execution, not asserted.

#### The re-scoped `-146` part (2), and ⛔ WHY IT CAN GO RED

The claim is now: **no commit of this story's own `(17-3)`-scoped arc created either
`SUCCESSOR_OUTPUT_PATHS` prefix**, asked of git over `_BASELINE_COMMIT..HEAD`. It is the claim
`-146`'s own docstring always made — *"THIS STORY commits `S1`'s CODE and never its OUTPUT over a
corpus member"* — and unlike the filesystem form it survives 17.4 legitimately writing its record.

⛔ **A guard that cannot go red is worse than the one it replaced, so it was DRIVEN RED**, at its
real seam, in a **throwaway repository** built under `tmp_path` — ⛔ never against this
repository's object database, and no `git replace` / `graft` / `commit-tree` / history rewrite
anywhere (`DN-17-4-5`; the tree is shared). **The executed demonstration, verbatim:**

```
=== -146 part (2), RE-SCOPED, DRIVEN RED IN A THROWAWAY REPO ===
throwaway repo : …\Temp	mpwaxitncl	hrowaway-ordering-repo
range          : 479174e .. b309910
control        : {'dae32f5': 'chore(17-3): rogue control, touching no declared prefix'}
OFFENDERS      : {'b309910': 'chore(17-3): commit successor output with no pre-registration ancestor'}
RED            : AssertionError: {'b309910': …} — commit(s) of THIS story's arc touch a
                 declared successor-output prefix

=== -147, DRIVEN RED AT THE SAME SEAM ===
compliant (descendant of criterion) -> ()
offender  (unrelated root)          -> ['b309910']

=== the SAME queries against THIS repository ===
in-repo arc control : 3 commits          (non-vacuity: the range + tag filter + pathspec FIND things)
in-repo arc created : {}                 (the claim)
```

⛔ The synthetic offender is **one commit that violates both claims at once**: it carries the
`(17-3)` scope *and* creates a declared prefix *and* sits on a root the criterion stand-in does not
precede. The demonstration is **committed inside both guards**, so it re-runs on every suite run
rather than living only in this record.

⛔ **The residual risk is disclosed, not hidden**, and it is the one `DN-17-2-12` already recorded:
a future `(17-3)`-scoped commit that writes successor output *without carrying the tag* would not
be seen. It is bounded by the same commit-message convention `-78` already relies on and is written
into the guard's own docstring.

#### `-147` LANDED, AND IT LANDED NON-VACUOUS

`tests/test_successor_output_ordering.py` — the universal *"for every commit touching any declared
`SUCCESSOR_OUTPUT_PATHS` entry, `PREREGISTRATION_COMMIT_SHA` is an ancestor of it"*, with all three
AC4.3 preconditions asserted **before** the claim and the second being ⛔ **the inversion of
`-139`**: the offender-candidate population is asserted **NON-EMPTY**.

| `-147` fact | measured after commit 2 |
|---|---|
| offender-candidate population | **1** commit — `5bf27ca chore(17-4): the ONE measurement, …` |
| offenders (ancestry) | ⛔ **NONE** |
| `PREREGISTRATION_COMMIT_SHA` | `f906d04997b391bea4592aabc0343d1234b3b060`, **IMPORTED**, ancestor of HEAD |
| population **before** commit 2 | **0** — so `-147` was correctly RED, and ⛔ **did not land in commit 1** (AC4.7 / `DN-17-4-4`) |
| third-party checkouts required | **NONE** — the object database and a `tmp_path` repo only (AC4.5) |
| `-139` | ⛔ **not edited**, still green (AC4.6) |

⛔ **ONE DERIVATION, NOT TWO.** `commits_touching_prefixes` and `ancestry_offenders` are **pure and
exported**, and the re-scoped `-146` part (2) asks git the *same* question through the *same*
function `-147` uses. Two guards that disagreed about *"which commits touched a declared prefix"*
would be `DF-8-5-C` in miniature.

---

### ROUND 1 (2026-08-25 → 26) — ⛔ HALTED AT AC10; **RESOLVED IN ROUND 2, ABOVE**

⛔ **Preserved unedited as the escalation record.** Everything below was true when it was written;
the blocker it describes is the one the operator resolved above.

⛔ **THE MEASUREMENT IS DONE, IT WAS TAKEN ONCE, AND ITS RESULT IS RECORDED BELOW AND IN THE
MACHINE RECORD.** Nothing about the outcome is in question and nothing was tuned to reach it.

⛔ **WHAT IS BLOCKED IS ONLY THE COMMIT ARC**, by a *mechanically proven contradiction between two
of this story's own acceptance criteria* — **AC6.1 vs AC9.6** — discovered by execution after the
measurement landed. It is written up in full under "THE BLOCKER" below. ⛔ **No frozen guard was
edited, no floor was moved, no member was ratified and no corpus was shopped.**

---

### THE MEASUREMENT — taken ONCE, on 2026-08-25, and recorded exactly as it returned

**The exact command** (LOCAL, Windows; there is no CI evidence at any sha on this branch —
`audit-ci.yml` triggers on `master`/`main` only and this branch is unpushed):

```
python scripts/build_successor_reach_record.py \
    --checkout-root d:/ProjectX/XAgents/XAgents --snapshot-root c:/t/ar174
```

| measured quantity | value |
|---|---|
| `population_walked` | **1032** |
| `population_skipped` | **0** |
| rule classes walked | **1** — `vacuous_test_heuristic`, reported as one (`DN-17-4-7`) |
| members walked | all **5** ratified: `agent-markovich`, `agent-smith`, `ai-body-runtime`, `minions`, `xagents-webapp` |
| **`S1` eligible population** | ⛔ **85** |
| `S1` by contributing member | `minions` **54**, `agent-smith` **28**, `agent-markovich` **3** |
| contributing members | **3** |
| sealed contributing members | **0** |
| assertion bands, ELIGIBLE (assertion counts) | `none` 59 · `existence` 0 · `value` 0 · `unestablished` 0 |
| assertion bands, WALKED (assertion counts) | `none` 206 · `existence` 97 · `value` 1380 · `unestablished` 0 |
| **SHIPPED verdict-eligible predicate promotes** | ⛔ **0 of 1032** |
| `true_positive_count` / `false_accusation_count` | **0 / 0** — this story adjudicates nothing |
| `measured_precision` | **`null`** — no denominator (never `100%`, never `0%`) |

**⛔ THE OUTCOME THE FROZEN CRITERION RETURNED:**

> ### `UNEVALUABLE`
>
> *"sealed contributing members: 0, below the resolved floor of 3. The criterion is UNEVALUABLE
> over this population -- a recorded failure to evaluate, which is neither a pass nor a fail and
> is not an invitation to argue the floor down."*

`criterion_shortfalls` = exactly one: `sealed_contributing_members`, measured **0**, required
**3**. The floor's own derivation string is recorded on the artifact, unparaphrased.

⛔ **THIS IS A SUCCESSFUL OUTCOME OF THIS STORY, AND IT WAS PRE-REGISTERED ON 2026-08-25 IN
`f906d04`, BEFORE `S1` EXISTED.** Story 17.1 §3.1/§3.2 wrote both `UNEVALUABLE` arms down while the
answer was still zero. Nothing here was engineered to reach it and nothing was engineered around
it. The fold was CALLED — `precision_preregistration.evaluate()` with the measured counts
**unmodified**, with neither `floors=` nor `ratio_floor=` injected — and what it returned is what
is recorded.

#### ⛔ THREE THINGS THE MEASUREMENT SAYS THAT §0 DID NOT KNOW, reported as measured

⛔ **None of these is offered as confirming, missing or approaching any prior figure.** §0.5 is
explicit that `V2 = 36` and `V5 = 125` were measured by two different instruments at two different
HEADs, are not comparable priors, and that their sum is not a prediction. **This is the first
measurement of `S1` that has ever been taken.**

1. ⛔ **`S1` CLEARS THE BREADTH FLOOR. The sealed arm is the ONLY arm that failed.** §0.3 and §0.4
   named two independent `UNEVALUABLE` arms, and §0.5 recorded that both known bands (`V1`, `V2`)
   draw from exactly **TWO** contributing members against a floor of three. `S1` draws from
   **THREE** (`minions`, `agent-smith`, `agent-markovich`), so `contributing_members` **CLEARED**
   at 3/3 and `verdict_eligible_population` **CLEARED** at 85/5. The full floor table is recorded
   on the artifact as `criterion_floor_results` — what cleared as well as what did not.
2. ⛔ **THE EMPTY-DENOMINATOR ARM WAS NEVER REACHED, AND IS RECORDED ANYWAY.** `evaluate()`
   evaluates the three resolution floors **before** it looks at any ratio and returns on the first
   shortfall, so the sealed arm answered first and step (2)'s `AI-E11-1` reason never fired. Both
   arms are true; only the check order decides which reason the verdict carries. ⛔ AC3.3 forbids
   omitting an empty denominator with the population implied to be fine, so the artifact carries
   `criterion_empty_denominator_arm` — 0 TP, 0 FP, `precision_fraction` → `null`,
   `reached_by_the_fold: false`, and `AI-E11-1`'s content stated as this record's own prose,
   ⛔ **not paraphrased as though it were the frozen constant**. This disclosure field was added
   AFTER the first run (see "two producer runs" below).
3. ⛔ **`DF-13-5-A`'s CONDITION 1 DOES NOT FIRE.** The **shipped** verdict-eligible predicate
   promotes **0 of 1032** over the five ratified members, measured at HEAD rather than assumed —
   §0.9 predicted this and it is now a measurement. `S1`'s 85 is **not** a shipped promotion:
   `S1` is ADVISORY (specification §6.5), `_ast_corroborated`'s return expression is byte-unchanged,
   and the trigger's subject is the shipped predicate. **Condition 1: NOT FIRED. Condition 2
   (`2026-11-22`): not reached, and ⛔ NOT re-dated.** `branch_taken: NEITHER`,
   `members_ratified: NONE`, `round_state: UNSPENT`, `protocol_edit: NONE`, entry stays **OPEN**.

#### The measurement is byte-reproducible, proved rather than asserted

```
python scripts/build_successor_reach_record.py --check \
    --checkout-root d:/ProjectX/XAgents/XAgents --snapshot-root c:/t/ar174
→ exit 0, "is current against a re-measurement at the pins"

python scripts/build_successor_reach_record.py --check
→ exit 0, round-trips through argus.store.canonical AND the recorded outcome UNEVALUABLE
  re-derives from the recorded counts through the frozen fold
```

No clock, no `uuid4`, no `random`, no environment read and no network is reachable from any
derivation path, which is what makes `--check` a byte comparison rather than a re-render.

---

### ⛔ THE BLOCKER — `TC-ArgusAgent-PRECISION-001-146` PART (2) vs THIS STORY'S DELIVERABLE

**AC6.1 and AC9.6 cannot both hold. This is not a judgement call; it is mechanical.**

`-146` (`tests/test_successor_predicate_s1.py:216-222`, Story 17.3, `done`) asserts:

```python
for prefix in SUCCESSOR_OUTPUT_PATHS:
    assert not (_REPO_ROOT / prefix).exists(), (
        f"{prefix!r} exists. This story commits S1's CODE and never its OUTPUT over a "
        f"corpus member (AC6.4); committing one scored row would make Story 17.4's "
        f"ancestry guard argue about a commit nobody planned."
    )
```

- **AC6.1 / §1.3** require this story's record to land under `SUCCESSOR_OUTPUT_PATHS[0]` and
  ⛔ **nowhere else**. Both prefixes are checked by `-146`, so `SUCCESSOR_OUTPUT_PATHS[1]` is not
  an escape — and relocating the output is forbidden anyway.
- **AC9.6** states: ⛔ *"`-135`..`-146` are **not edited**"*, and **AC4.6** restates the principle
  (`DF-8-5-B`: a green guard is never edited to accommodate new code).
- Therefore: **the story's deliverable existing on disk is exactly the condition `-146` reds on.**
  There is no arrangement in which both criteria hold.

**Why §0 missed it, stated precisely, because the distinction is the lesson.** §0.12 and AC4.6 did
this analysis for `-139` and got it **right**: `-139` walks *commits reachable from `f906d04`*, and
this story's commits are descendants, so `-139` stays green — verified, still green. The authors
generalised from `-139` to `-146` — but ⛔ **`-146` part (2) is a FILESYSTEM EXISTENCE assertion,
not a git-ancestry one, and filesystem existence is not scoped by commit ancestry.** §0.2 even
records *"`SUCCESSOR_OUTPUT_PATHS` … ⛔ both ABSENT on disk at HEAD (re-checked)"* as a **premise**
— without noticing that a frozen guard mechanically enforces that premise, and that this story is
chartered to end it.

**`-146`'s own docstring says its part (2) is scoped to Story 17.3**, not to the epic:

> *"Both `SUCCESSOR_OUTPUT_PATHS` prefixes asserted ABSENT on disk. **This story** commits the
> predicate's CODE and never its OUTPUT over a corpus member, which is what leaves **Story 17.4's
> ancestry guard nothing to argue about**."*

Its purpose is to stop any story **before** 17.4 from creating successor output. 17.4 creating it
is *the planned commit* that fence was protecting. The fence is correct and has expired — but
**expiring it is an edit to a closed story's green guard, which AC9.6 forbids in bold and
`DF-8-5-B` names as this project's signature defect.** ⛔ **That decision is not mine to take**
(AC10: *escalate, do not decide*), so I took none.

**Consequences, all of them, so nothing is discovered later:**

- ⛔ **Task 4 (`-147`) is BLOCKED BY THE SAME CONTRADICTION**, not merely unstarted. `DN-17-4-4`
  requires `-147` to assert a **NON-EMPTY** offender population, which is satisfiable only at or
  after the first successor-output **commit** (§1.4 / AC4.7). That commit is what reds `-146`. So
  `-147` cannot be written non-vacuously until this is resolved. Writing it now would ship a guard
  that passes by finding nothing — the exact failure `DN-17-4-4` exists to prevent.
- ⛔ **The `DF-13-5-A` ledger note is MEASURED BUT HELD, not forgotten.** Its content is fully
  determined and is recorded verbatim above (condition 1 **NOT FIRED**, `0 of 1032`). It is not yet
  appended to `deferred-work.md` because AC8.4 requires ⛔ **exactly ONE** entry this round, and an
  entry written now would be duplicated or contradicted when the arc is re-driven.
  `deferred-work.md` is **byte-unchanged** (sha256 `6b58f210…`, 602,265 bytes / 1 CR / 0 CRLF /
  7,623 LF).
- ⛔ **Nothing is committed.** The tree carries the work uncommitted. `sprint-status.yaml` reads
  `in-progress` for this story and **not** `review`.
- ⛔ **The record is LEFT ON DISK ON PURPOSE**, so the one red guard tells the truth about the
  contradiction. Deleting the deliverable would make the suite green and hide the blocker, which
  is the opposite of what this story is for.

#### Options for the operator (⛔ I took none of them)

1. ⛔ **Scope `-146` part (2) to its stated purpose** — assert the prefixes carry no output *as of
   Story 17.3's commit range*, which is what its own docstring already says it means, e.g. by
   asking git (`git log <17.3 range> -- <prefixes>` empty) rather than the filesystem. Parts (1)
   and (3) stay untouched and the guard says what it always meant. **Cost:** it is an edit to a
   closed story's green guard, which AC9.6 forbids — so it needs an explicit operator decision and
   a recorded AC9.6 amendment.
2. **Retire part (2) into `-152`.** `TC-ArgusAgent-PRECISION-001-152` (this story, green) already
   asserts the two-sided *"no successor output outside the declared prefixes"* claim, and it is
   correct after 17.4 as well as before it. **Cost:** the same AC9.6 amendment; `-146` also loses
   a third of its docstring's stated observable.
3. **Re-scope this story.** Keep the measurement as an uncommitted, reproducible local result and
   defer the committed artifact (and `-147`) to a follow-up that carries the `-146` decision.
   **Cost:** AC4 and AC6 go unmet in 17.4 and `-147` is never minted here, so the ordering guard
   the epic calls its *binding constraint* stays unwritten.

⛔ **What I did NOT do, and will not do without an operator act:** edit `-146` or any of
`-135`..`-145`; move the output outside the declared prefixes; delete the measurement; loosen
`-152`; or make the gate reachable by touching the corpus, the seal or a floor.

---

### §0 RE-MEASUREMENT (Task 0, AC10.1) — every row re-derived by execution at `682b074`

⛔ **EVERY §0 ROW REPRODUCED EXACTLY** except the two recorded under "rows that moved" below.

| §0 row | re-measured | verdict |
|---|---|---|
| `precision_floor()` / floors / ceiling | `4/5`, 5, 3, 3, 5, 26 | ✅ unchanged |
| `PREREGISTRATION_COMMIT_SHA` | `f906d04997b391bea4592aabc0343d1234b3b060`, ancestor of HEAD ✅ | ✅ |
| `SUCCESSOR_OUTPUT_PATHS` | both ABSENT on disk at start of run | ✅ |
| `CRITERION_OUTCOMES` | closed at three | ✅ |
| `eligible_member_count()` | **5**; `PRE_SEAL_MEMBER_IDS` = the same five | ✅ |
| `SEALED_PARTITION_TABLE` | 6 sealed / 8 open; ⛔ `sealed ∩ ratified` **EMPTY** | ✅ |
| `adjudication-record.json` | 31 rows · 26 `FP` · 5 `BORDERLINE` · **0 `TP`** · all `vacuous_test_ast` · `V1.3` · `reproducibility_verified: True` · `expert_hours: None` | ✅ |
| the 1,032, re-derived per member | `minions` 648 · `agent-smith` 295 · `agent-markovich` 72 · `xagents-webapp` 17 · `ai-body-runtime` 0 = **1032** of 4,284 | ✅ |
| five pinned shas, `git cat-file -e <sha>^{commit}` | all **5** reachable (⛔ `agent-smith` at `XAgents/Agent-Smith`, one level deeper) | ✅ |
| module sizes | criterion 774 · `-135`..`-141` module 1,121 · `assertion_strength` 500 · `build_silent_class_record` 834 | ✅ |
| highest `PRECISION-001` id in use | **`-146`**; `-147` unused in the tree | ✅ |
| `deferred-work.md` | 602,265 bytes · **1 CR / 0 CRLF / 7,623 LF** | ✅ |
| `sprint-status.yaml` | **1,264 lines / 1,264 CR / 1,264 CRLF**, `last_updated: 2026-08-25` | ✅ |
| `-135`..`-141`, `-146`, `-127`, `-78` | re-run **GREEN** before a line was written (20 passed) | ✅ |

#### ⛔ ROWS THAT MOVED — reported loudly, per AC10.1

1. ⛔ **§0.0 "working tree" moved.** §0.0 records *"2 staged peer-session paths"* (`M `). At the
   start of this round `git status --porcelain` read **`MM sprint-status.yaml`** — staged **and**
   worktree-modified — plus `M  stories/17-3-*.md` and `?? stories/17-4-*.md`.
   **Old:** 2 staged paths, worktree clean. **New:** the peer's 17.3 close-out is *staged*; this
   story's own contexting line (`17-4-…: backlog → ready-for-dev`) is *unstaged*; this story's
   file is *untracked*. Commands: `git status --porcelain`,
   `git diff -U0 -- …/sprint-status.yaml`.
   **Impact: none on any measurement** — the unstaged hunk is this story's own contexting
   transition. ⛔ Recorded because §0.0's stated tree state is no longer literally true, and
   because it sharpens the staging rule: `git add -A` here would swallow the peer's 17.3 close-out.
2. ⛔ **§0.2's "`SUCCESSOR_OUTPUT_PATHS` both ABSENT on disk" is a premise THIS STORY ENDS**, and
   §0 did not record that a frozen guard mechanically enforces it. That is **the blocker**,
   written up in full above.

**Baseline hashes captured for the AC5.4 / AC7.4 / AC9.3 neutrality proofs** (all re-verified
identical after the measurement):

```
f784df63…  validation-corpus/silent-class-record.json
cd3cb293…  validation-corpus/silent-class-worklist.md
71fb73e7…  validation-corpus/adjudication-record.json
f31ae29c…  scripts/precision_preregistration.py        ⛔ BYTE-FROZEN, unchanged
6b58f210…  deferred-work.md
git rev-parse HEAD:argus → 9910f4b10f92eee05f20dd5d9f378ca6ddf42d61
```

---

### Debug Log References

**Neutrality and immutability, verified by execution after the measurement (AC5.4 / AC7.4 / AC9.3):**

| claim | command | result |
|---|---|---|
| `argus/` tree byte-unchanged | `git diff --stat 682b074 -- argus/` | ⛔ **EMPTY** |
| `argus/` tree object | `git rev-parse HEAD:argus` | `9910f4b1…`, unchanged |
| criterion module byte-frozen | sha256 | `f31ae29c…`, unchanged |
| `adjudication-record.json` byte-unchanged | sha256 | `71fb73e7…`, unchanged |
| silent-class artifacts byte-identical | `build_silent_class_record.py --check --checkout-root … --snapshot-root c:/t/sc174` | ⛔ **exit 0**, *"artifacts are current (36 rows, re-derived from 1032 recorded findings at the pins)"* |
| `deferred-work.md` untouched | sha256 + CR/CRLF/LF counts | `6b58f210…`, 1 CR / 0 CRLF / 7,623 LF |

⛔ **Consequently NONE of `DN-17-1-1`'s four `argus/` costs is spent** (§0.10, verified rather than
assumed): no dogfood regeneration, no `Evidence-partition:` trailer (nothing touches
`argus/detectors` or `argus/precision/replay_harness.py`), no `DOCS-001-54` wheel-figure move.

**Local gates — ⛔ LOCAL (Windows). There is NO CI evidence at any sha on this branch**
(`audit-ci.yml` triggers on `master`/`main` only; this branch is unpushed — `AI-E13-1`, epic-18
retro SD-4):

| gate | command | result |
|---|---|---|
| full suite | `python -m pytest` | ⛔ **1 failed, 1756 passed** in 245.87s — the ONE failure is `-146`, and it IS the blocker above |
| coverage floor | `pytest --cov=argus --cov-fail-under=80` | ✅ **95.87%** (floor 80%) |
| types | `mypy argus` | ✅ *"Success: no issues found in 96 source files"* |
| security (blocking) | `bandit -r argus --severity-level medium` | ✅ **exit 0** |
| the frozen criterion | `-135`..`-141` | ✅ green (incl. ⛔ `-140`, the strengthening-only direction guard) |
| the one-way import edge | `-127` | ✅ green |
| record integrity | `-78` | ✅ green |
| `-146` | `-146` | ⛔ **RED on part (2) only.** Part (1) — `_ast_corroborated`'s return expression as a parsed AST expression — **PASSES**: the verdict line did not move. Part (3) passes. |

⛔ **AC5.5's substantive claim therefore HOLDS**: `_ast_corroborated`'s return expression is
byte-unchanged and nothing verdict-eligible flipped. What is red is `-146`'s Story-17.3 scope
fence, not the invariant AC5.5 names.

**New guards, each driven RED at its real seam by an EXECUTED mutation, ⛔ none touching disk:**

| guard | observable | RED demonstration |
|---|---|---|
| `-151` | `ast` walk over BOTH producer modules, classifying imports and call sites | three in-memory mutations: `import ast` prepended; `s1_corroborated(...)` called beside the entry point; the `successor_evidence` call removed. All three flagged by the **pure, exported** `second_derivation_offenders()` |
| `-149` | the row constructor and `seed_successor_row`, DRIVEN not read | six refusals driven: `disposition=TP`/`FP`, an adjudicator, a date, `verdict_eligible=True`, a non-corroborated span, and three non-portable locators |
| `-148` | `population_walked` / `skipped` / `members_walked` / `rule_classes_walked` | population re-derived **independently** from `adjudication-set-13-5.json`; both sides asserted non-empty first |
| `-150` | the recorded outcome re-derived through the frozen fold | the fold watched producing **two different answers** (starved → `UNEVALUABLE`, satisfied → `MET`); then a mutation **GENERATED from the record's own floor table** raises every short count to its floor and the reason changes |
| `-152` | `git ls-files`, partitioned by declared prefix | the classifier driven to **both** outcomes on real strings; enumeration asserted > 200 paths first |

⛔ `-151`'s and `-152`'s non-vacuity preambles are asserted **before** the absence they protect;
`-148`'s non-vacuity is **structural** (`walked == the re-derived population`, `skipped == 0`,
member set == the ratified corpus) and ⛔ **never a floor on the reach** — a floor would be a
prediction, and a prediction is the thing this story refuses (`DN-17-4-9`).

⛔ **`-150` asserts NO particular outcome** (AC9.4). It asserts internal consistency only. It would
stay green, unedited, if the measurement legitimately returned something else.

---

### Completion Notes List

**Decisions this round took beyond the story's `DN-17-4-1`..`-9`, each with its rejected
alternative, recorded rather than silently diverged from:**

- **`DN-17-4-10` — NO human worklist is rendered.** *Rejected:* Story 16.7's worklist shape.
  16.7 rendered one because it was asking a named human for 36 judgements and **the spans were the
  question**. This story asks for **no** judgement (`DN-17-4-2`), so a worklist would spend
  `NFR-S1`'s four-part source-span carve-out — publishing third-party source bytes into a committed
  artifact — to support a judgement nobody requested. AC6.4 makes the worklist conditional
  (*"if a human-readable worklist is produced at all"*). ⛔ Consequence: **no corpus source byte
  exists in any artifact this story produces**; the machine record carries locators and counts
  only, and `-148` asserts no row carries a `source` or `span` key.
- **`DN-17-4-11` — the producer was SPLIT at the §0.11 pre-registered trigger, BEFORE the second
  half was written.** The single-module producer projected **1,152 lines** against §0.11's 1,000
  trigger (and `NFR-M1`'s 1,200 ceiling, which sweeps `scripts/`). Per §0.11 the record model was
  split out **first**: `scripts/successor_reach_model.py` (711) +
  `scripts/build_successor_reach_record.py` (522). ⛔ Honoured at the trigger, not discovered at
  review. The seam is honest: the model knows what a record is and how the frozen criterion folds
  it; the producer knows how to walk five checkouts at their pins. Only the walk needs a corpus,
  which is why every committed guard is CI-safe.
- **`DN-17-4-12` — the guards are in THREE modules, not one, and the split is by WHAT THEY READ.**
  `tests/test_successor_reach_producer.py` (`-151`, `-149`) reads only committed source and is
  green **before** any measurement exists — which is what lets the producer land in its own
  reviewable commit (§2.3 commit 1). `tests/test_successor_reach_record.py` (`-148`, `-150`,
  `-152`) reads the committed record and can only be green at or after commit 2. `-147` was to go
  in `tests/test_successor_output_ordering.py` for commit 3. *Rejected:* one module — it would
  have been RED at commit 1 by construction, and it projected past §0.11's 1,000-line trigger.
  ⛔ **`-147` was deliberately NOT written into `tests/test_precision_preregistration.py`** (79
  lines of headroom, and it belongs to a frozen story), and ⛔ `-135`..`-141` were not edited.
- **`DN-17-4-13` — `criterion_empty_denominator_arm` and `criterion_floor_results` were ADDED to
  the record after the first run.** AC3.3 requires an empty adjudicated population to be recorded
  and ⛔ *"never omitted with the population implied to be fine"*. Because `evaluate()` returned on
  the sealed floor, step (2)'s reason never fired and the first record disclosed the empty
  denominator only as `measured_precision: null`. ⛔ These two fields are **pure disclosure**: they
  changed no count, no floor, no outcome and no reason. See "two producer runs" below for the
  proof.
- **`DN-17-4-14` — `--snapshot-root` is REQUIRED alongside `--checkout-root`**, where
  `build_silent_class_record.py` defaults it to a temp directory. That script's own `--help`
  records that the default temp root can push the deepest in-scope path past `MAX_PATH` on Windows
  and that *"a partially-extracted tree derives clean"* — i.e. it fails silently in the dangerous
  direction. ⛔ A measurement that fails silently towards CLEAN is exactly what this story must not
  ship, so the flag is mandatory rather than defaulted.
- **The shipped predicate's discard half is read off the SHIPPED property, not re-typed.**
  `ProvenanceEvidence.sut_result_is_discarded` is constructed from `score_span`'s own three counts
  and read, rather than writing `disc >= 1 and cons == 0` here — so this record and
  `_ast_corroborated` cannot disagree about it. *Rejected:* a second call to `span_provenance`,
  which would put a second full span scan on the walk (`DF-AUD-DETECT-C` is OPEN and undispositioned,
  and this is not a performance story).

**Dates, and the two producer runs — disclosed rather than smoothed over:**

- The round began **2026-08-25** and the clock rolled to **2026-08-26** during the full-suite run.
  The measurement was taken on **2026-08-25**. ⛔ `sprint-status.yaml`'s `last_updated` was left at
  `2026-08-25`: it was today's date when the one status value was edited, and rewriting it now
  would also re-date the peer session's staged 17.3 close-out in the same file.
- ⛔ **The producer ran twice, and both runs are disclosed.** Run 1 (sha256
  `b7ab4348d3941206bb6ea409445ad11b9132d325cace62f5798856e7310bdd4e`, 70,235 bytes) IS the
  measurement. Run 2 followed `DN-17-4-13`'s disclosure fields. ⛔ **Every measured figure is
  identical across both runs** — 85 eligible, `{minions: 54, agent-smith: 28, agent-markovich: 3}`,
  3 contributing, 0 sealed, 0/0 adjudicated, `measured_precision: null`, shipped predicate 0/1032,
  1032 walked / 0 skipped, outcome `UNEVALUABLE` with the identical reason and the identical single
  shortfall. ⛔ **Nothing was re-run in order to change an answer**, and `--check --checkout-root`
  then re-measured from the pins and compared **bytes**: exit 0.

**AC10 conditions — evaluated, and the one that fired:**

| condition | fired? |
|---|---|
| AC10.1 — a §0 row moved | ⛔ **YES** — two rows, reported loudly above |
| AC10.2 — an `argus/` byte required | NO — `git diff --stat -- argus/` empty at every point |
| AC10.3 — reaching a non-`UNEVALUABLE` outcome would need corpus-shopping | ⛔ **NOT ATTEMPTED.** The sealed arm can only clear via a protocol §6 R2 operator act ratifying ≥3 sealed members. ⛔ No such reasoning was pursued: `UNEVALUABLE` was recorded and the story stopped, which is §2.1's instruction |
| AC10.4 — the criterion module would have to change | NO — `evaluate()` was callable exactly as frozen |
| AC10.5 — a row reached protocol §4's third rung | NO — nothing was adjudicated, so the ladder was never engaged; `AI-E16-7` recorded **NOT REACHED** |
| AC10.6 — pinned corpus unreachable / a blob failed verification | NO — all 5 shas reachable, all `verify_pinned_bytes` proofs passed |
| ⛔ **AC6.1 vs AC9.6 contradiction** | ⛔ **YES — and it is not in AC10's list.** Escalated rather than decided |

**Acceptance criteria status — ROUND 1, at the halt** (round 2's final table follows):

| AC | status |
|---|---|
| AC1 (measurement complete, over the right population) | ✅ **MET** — 1032 / 0, 5 members, 1 rule class, bands as counts, every figure derived by this run |
| AC2 (criterion called, not re-implemented or amended) | ✅ **MET** — `evaluate()` called with unmodified counts and resolved defaults; criterion byte-frozen; `-135`..`-141` green |
| AC3 (`UNEVALUABLE` recorded, not repaired) | ✅ **MET** — shortfall named with its floor's own derivation; sealed count reported as measured; empty denominator recorded, never `100%`/`0%`; gate `BLOCKED` at every outcome |
| AC4 (ordering guard `-147`) | ⛔ **NOT MET — BLOCKED** by the `-146` contradiction (its non-vacuity needs the successor-output commit) |
| AC5 (one derivation; `argus/` untouched) | ✅ **MET** — `-151` green; `argus/` diff empty; `SpanScore` / `VacuousTestScore` / `__all__` unwidened. AC5.5's *invariant* holds (`-146` part (1) green); `-146` part (2) is the blocker |
| AC6 (output lands where declared) | ⚠️ **PARTIAL** — the record is under `SUCCESSOR_OUTPUT_PATHS[0]` (imported), canonical, unregistered, carries no source byte; `-152` green. ⛔ **Not committed**, because committing it reds `-146` |
| AC7 (nothing adjudicated) | ✅ **MET** — every row `UNADJUDICATED`, no adjudicator/date, `AI-E16-7` **NOT REACHED**, `exhaustive: false` with the gap named, `adjudication-record.json` byte-unchanged |
| AC8 (`DF-13-5-A` evaluated, no branch taken) | ⚠️ **MEASURED, NOTE HELD** — condition 1 **NOT FIRED** (0 of 1032, measured); condition 2 not re-dated; no branch taken. The single ledger note is held pending the blocker |
| AC9 (guards non-vacuous, driven RED) | ✅ **MET for the five guards written**; `-147` blocked. Neutrality control ✅; no guard asserts a predicted value; both new modules within `NFR-M1` |
| AC10 (escalate, do not decide) | ✅ **HONOURED** — escalated, decided nothing |

---

**⛔ ROUND 2 (2026-08-26) — DECISIONS TAKEN, each with its rejected alternative:**

- **`DN-17-4-15` — `-146` part (2) is RE-SCOPED, not deleted and not retired.** ⛔ Taken under the
  operator's 2026-08-26 amendment of AC9.6, which is narrow to that part and to no other. The claim
  moves from *"the prefixes are absent on disk"* to *"no commit of Story 17.3's arc created them"* —
  the claim the guard's own docstring always made, and the only form of it that survives 17.4
  legitimately writing the record AC6.1 demands. *Rejected (by the operator):* retiring part (2)
  into `-152`, and deferring the committed artifact to a follow-up. ⛔ **Precedent, not novelty:**
  `DN-17-2-12`, reviewed and judged sound. ⛔ Parts (1)/(3) byte-untouched; `-135`..`-145` unedited;
  the criterion module byte-frozen.
- **`DN-17-4-16` — the offender-finding queries are ONE pure, exported pair shared by `-146` part
  (2) and `-147`.** `commits_touching_prefixes` / `ancestry_offenders` in
  `tests/test_successor_output_ordering.py`. *Rejected:* a private query inside each guard — two
  derivations of *"which commits touched a declared prefix"* that can disagree is `DF-8-5-C` in
  miniature, and it would also mean the RED demonstration drives a re-implementation rather than
  the real seam (§1.4's explicit requirement).
- **`DN-17-4-17` — the `-146` amendment landed in COMMIT 2, not commit 1.** *Rejected:* landing it
  in commit 1 "to keep the fence current". ⛔ Every commit of the arc is green **as a tree**:
  commit 1 carries no successor output, so the *unamended* `-146` is still correct there; commit 2
  carries the record, the amendment and `-147` together, which is the first tree in which the
  amended form and `-147`'s non-empty population are both true. §2.3 permits `-147` in commit 2 and
  forbids it in commit 1.
- **`DN-17-4-18` — the 17.3 story file receives a dated, APPEND-ONLY note, and 17.3 is NOT
  reopened.** Its Status stays `done`; no AC, task, decision or record of that story is edited.
  *Rejected:* recording the amendment only here. A change to a closed story's guard that is
  discoverable only from another story's file is a change nobody maintaining 17.3 will find.
- **⚠️ `DN-17-4-19` — `sprint-status.yaml` and the 17-3 story file were committed WITH the peer
  session's already-staged edits riding along, disclosed rather than smoothed over.** Both files
  carried the peer's staged 17.3 review close-out **in the shared index** before this round began,
  and both are files this story must also write. The two edits cannot be separated inside one file
  without synthesising a blob neither session authored. ⛔ **Nothing was staged with `git add -A`,
  nothing was amended or rebased, no history was rewritten, and no other peer path was touched** —
  every commit used `git commit -- <explicit paths>`. The peer's content lands verbatim; only its
  authorship attribution moves. *Rejected:* rewriting the index to split the file (a blob nobody
  wrote), and leaving `sprint-status.yaml` uncommitted (the §2.3 arc requires the transition to
  land with the record).

**⛔ ROUND 2 — ACCEPTANCE CRITERIA, FINAL:**

| AC | status |
|---|---|
| AC1 (measurement complete, over the right population) | ✅ **MET** — unchanged from round 1; 1,032 / 0, five members, one rule class, every figure derived by the single run |
| AC2 (criterion called, not re-implemented or amended) | ✅ **MET** — criterion byte-frozen (`f31ae29c…`, `git status` empty); `-135`..`-141` re-run green |
| AC3 (`UNEVALUABLE` recorded, not repaired) | ✅ **MET** — recorded exactly as returned; ⛔ **not re-run and not re-recorded in round 2** |
| AC4 (ordering guard `-147`) | ✅ **MET** — `-147` landed in commit 2, population **1**, offenders **none**, three preconditions asserted first, driven RED in a throwaway repo, CI-safe, `-139` unedited |
| AC5 (one derivation; `argus/` untouched) | ✅ **MET** — `git diff --stat 682b074 -- argus/` **EMPTY**; `HEAD:argus` still `9910f4b1…`; `-151` green; `-146` part (1) green |
| AC6 (output lands where declared) | ✅ **MET** — the record is **committed** at `5bf27ca` under `SUCCESSOR_OUTPUT_PATHS[0]` (imported), canonical, unregistered, carrying no corpus source byte; `-152` green |
| AC7 (nothing adjudicated) | ✅ **MET** — unchanged; `adjudication-record.json` byte-unchanged (`71fb73e7…`) |
| AC8 (`DF-13-5-A` evaluated, no branch taken) | ✅ **MET** — ⛔ **exactly ONE** dated append-only note, no closure verb, condition 1 **NOT FIRED** (0 of 1,032), condition 2 **not re-dated**, entry **OPEN and UNSPENT**; ledger 1 CR / 0 CRLF held |
| AC9 (guards non-vacuous, driven RED) | ✅ **MET** — six guards, each with an executed RED demonstration; ⛔ AC9.6 **amended by operator decision for `-146` part (2) ONLY**, recorded here, in the guard, in 17.3's file and in the commit message |
| AC10 (escalate, do not decide) | ✅ **HONOURED** — round 1 escalated and decided nothing; round 2 executed the operator's decision and invented none of its own |

---

### File List

⛔ **Paths relative to the repository root. Every path below was staged EXPLICITLY**
(`git commit -- <paths>`); ⛔ **`git add -A` was never run, no history was rewritten and nothing
was amended or rebased.**

**Added — committed in the three-commit arc:**

- `scripts/successor_reach_model.py` — the record model and the fold (789 lines) — commit 1
- `scripts/build_successor_reach_record.py` — the corpus walk and CLI (523 lines) — commit 1
- `tests/test_successor_reach_producer.py` — `-151`, `-149` (404 lines) — commit 1
- `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/successor/successor-reach-record.json`
  — ⛔ **THE MEASUREMENT**, canonical JSON, 85 rows, 71,858 bytes, sha256
  `3a1b9bbc824409427244cdf7ebe5d9169404616b3837bec8a6f0c9dbc7fafabc` — commit 2. ⛔ **Byte-identical
  to the artifact round 1 wrote; round 2 did not re-run the producer.**
- `tests/test_successor_reach_record.py` — `-148`, `-150`, `-152` (474 lines) — commit 2
- `tests/test_successor_output_ordering.py` — ⛔ `-147` and the two pure, exported git seams
  (360 lines) — commit 2

**Modified:**

- `tests/test_successor_predicate_s1.py` (269 → 355 lines) — ⛔ **`-146` part (2) RE-SCOPED under
  the operator's AC9.6 amendment, and NOTHING ELSE.** Parts (1) and (3) byte-untouched. Commit 2
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — ⛔ **exactly ONE** dated,
  append-only `DF-13-5-A` trigger observation; 602,265 → 607,244 bytes with the **1 CR / 0 CRLF /
  7,686 LF** invariant held and **every byte above the note byte-identical**. ⛔ No closure verb; no
  other entry touched. Commit 3
- `_bmad-output/design-artifacts/ArgusAgent/stories/17-3-grade-what-the-assertion-constrains.md`
  — ⛔ a dated **APPEND-ONLY** note recording that `-146` was amended by operator decision under
  17.4, so the change is discoverable from the story that owns the guard. ⛔ **17.3 is NOT
  reopened** — Status stays `done` and every byte above the note is identical. Commit 3
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — ⛔ **one status value**
  (`17-4-…: in-progress → review`) and `last_updated: 2026-08-25 → 2026-08-26`; **1,264 lines /
  1,264 CR / 1,264 CRLF preserved**, comments and STATUS DEFINITIONS byte-intact. Commit 3
- `_bmad-output/design-artifacts/ArgusAgent/stories/17-4-…md` — this record. Commit 3

**⛔ NOT written, and deliberately so:** any `argus/**` file (`git diff --stat 682b074 -- argus/`
**EMPTY**, `HEAD:argus` still `9910f4b10f92eee05f20dd5d9f378ca6ddf42d61`); any human worklist
(`DN-17-4-10`); `scripts/precision_preregistration.py` (BYTE-FROZEN, `f31ae29c…`);
`adjudication-record.json` (`71fb73e7…`); `silent-class-record.json` / `-worklist.md`
(`f784df63…` / `cd3cb293…`); `tests/test_precision_preregistration.py` (`-135`..`-141` unedited);
`-142`..`-145` (unedited); any second ledger entry.

**⚠️ DISCLOSED — the peer session's staged work rode along in commit 3** (`DN-17-4-19`).
`sprint-status.yaml` and `stories/17-3-….md` both carried the peer session's staged 17.3 review
close-out **in the shared index** before this round began, and both are files this story must also
write; one file cannot be split between two authors without synthesising a blob neither wrote. The
peer's content lands **verbatim** — only its authorship attribution moves. ⛔ No other peer path was
touched, `git add -A` was never run, and no history was rewritten.

**⛔ ROUND 2 LOCAL GATES — LOCAL (Windows). There is NO CI evidence at any sha in this arc**
(`audit-ci.yml` triggers on `master`/`main` only; this branch is unpushed — `AI-E13-1`):

| gate | command | result |
|---|---|---|
| full suite | `python -m pytest` | ✅ **1,758 passed, 0 failed** in 242.27s — ⛔ round 1's single failure (`-146`) is gone, and it is gone because the guard was **re-scoped by operator decision**, not because the deliverable was removed |
| coverage floor | `pytest --cov=argus --cov-fail-under=80` | ✅ **95.87%** (floor 80) |
| types | `mypy argus` | ✅ *"Success: no issues found in 96 source files"* |
| security (blocking) | `bandit -r argus --severity-level medium` | ✅ **0 medium / 0 high**, exit 0 |
| the frozen criterion + the named guards | `-135`..`-141`, `-127`, `-146`, `-147`, `-78` | ✅ **11 passed** |
| the record, re-checked | `python scripts/build_successor_reach_record.py --check` | ✅ exit 0 — round-trips canonical **and** `UNEVALUABLE` re-derives from the recorded counts through the frozen fold |
| `argus/` neutrality | `git diff --stat 682b074 -- argus/` | ✅ **EMPTY** |

⛔ **NFR-M1 (1,200-line ceiling, swept over `argus/`, `tests/` AND `scripts/`):** every file this
story wrote is inside it — 789 / 523 / 474 / 404 / 360 / 355. §0.11's pre-registered **1,000-line
split trigger** was honoured before the second half was written (`DN-17-4-11`), not discovered at
review.

### Change Log

| date | change |
|---|---|
| 2026-08-25 | Task 0: every §0 row re-measured by execution at `682b074`. Two rows moved and are reported loudly (§0.0's tree state; §0.2's prefix-absence premise). `-135`..`-141`, `-146`, `-127`, `-78` re-run green (20 passed) before a line was written; baseline hashes captured. |
| 2026-08-25 | Status `ready-for-dev` → `in-progress` in the story file and in `sprint-status.yaml` (one value; CR invariants preserved). |
| 2026-08-25 | Tasks 1/3: `scripts/successor_reach_model.py` + `scripts/build_successor_reach_record.py` written, SPLIT at §0.11's pre-registered 1,000-line trigger before the second half (`DN-17-4-11`). Guards `-151`, `-149`, `-148`, `-150`, `-152` written, each driven RED at its real seam by an executed in-memory mutation. |
| 2026-08-25 | ⛔ **Task 2 — THE MEASUREMENT, TAKEN ONCE.** 1,032 walked / 0 skipped over the five ratified members at their pins. `S1` eligible **85** (`minions` 54, `agent-smith` 28, `agent-markovich` 3), 3 contributing members, 0 sealed. Shipped verdict-eligible predicate promotes **0 of 1,032**. The frozen fold returned ⛔ **`UNEVALUABLE`** — sealed contributing members 0, below the floor of 3. Recorded exactly as returned; nothing tuned, nothing reinterpreted, no floor argued down. |
| 2026-08-25 | `DN-17-4-13`: `criterion_empty_denominator_arm` + `criterion_floor_results` added as pure AC3.3 disclosure; producer re-run; every measured figure proved identical to run 1, and `--check --checkout-root` byte-compared green. |
| 2026-08-25 | Neutrality proved by re-derivation rather than argument: silent-class artifacts byte-identical (`--check` exit 0 over the same 1,032), `adjudication-record.json` and the criterion module byte-unchanged, `argus/` diff EMPTY. `DN-17-1-1`'s four `argus/` costs all UNSPENT. |
| 2026-08-26 | Local gates (LOCAL, Windows): `pytest` **1 failed / 1756 passed**, coverage **95.87%**, `mypy argus` clean, `bandit --severity-level medium` exit 0. |
| 2026-08-26 | ⛔ **HALTED at AC10.** `TC-ArgusAgent-PRECISION-001-146` part (2) asserts both `SUCCESSOR_OUTPUT_PATHS` prefixes are ABSENT ON DISK — a Story 17.3 scope fence that this story's deliverable necessarily ends. **AC6.1 and AC9.6 cannot both hold.** `-146` NOT edited, output NOT relocated, measurement NOT deleted. `-147` and the `DF-13-5-A` ledger note are blocked by the same contradiction. Nothing committed; status left `in-progress`; three options recorded for the operator. |
| 2026-08-26 | ⛔ **ROUND 2 (fix) — THE ESCALATION WAS RESOLVED BY THE OPERATOR, not by this agent.** `AC9.6` amended **narrowly and for `-146` part (2) ONLY**: that part is RE-SCOPED from a filesystem existence check to a claim over Story **17.3's own commit range**, which is what its docstring always said it meant and which is permanent rather than self-destructing. Rationale recorded as the `DN-17-2-12` precedent (`-144`'s git half, scoped for the identical reason and judged sound at review). Options *"retire part (2) into `-152`"* and *"defer the committed artifact to a follow-up"* were **considered and REJECTED by the operator**, and are recorded. ⛔ Parts (1)/(3) byte-untouched; `-135`..`-145` unedited; `precision_preregistration.py` BYTE-FROZEN and `-140` unmoved. |
| 2026-08-26 | The re-scoped `-146` part (2) driven **RED at its real seam** against a synthetic `(17-3)`-tagged commit that creates a declared prefix, built in a **throwaway repo** under `tmp_path` — ⛔ never against this object database, no history rewritten. The demonstration is **committed inside the guard**, and its transcript is recorded above. Its non-vacuity (range + scope filter + pathspec find 3 real control commits) is asserted **before** the claim. |
| 2026-08-26 | ⛔ **Task 4 — `-147` LANDED AND LANDED NON-VACUOUS.** `tests/test_successor_output_ordering.py`: the universal over every commit touching a declared prefix, with the offender-candidate population asserted **NON-EMPTY** first (**the inversion of `-139`**) — **1** commit, **0** offenders. Its offender-finding predicate is **pure and exported** and is shared with `-146` part (2), so there is ONE derivation of *"which commits touched a declared prefix"*. `-139` **not edited**. |
| 2026-08-26 | ⛔ **THE MEASUREMENT DID NOT MOVE.** The producer was **not** re-run; the committed record is byte-identical to round 1's artifact (sha256 `3a1b9bbc…`, 71,858 B, 85 rows) and `--check` exits 0. `UNEVALUABLE`, sealed contributing members **0** below the floor of **3**, `measured_precision` **null**, shipped verdict-eligible predicate **0 of 1,032** — every figure unchanged. ⛔ Nothing tuned, ratified, sealed, adjudicated or reinterpreted. |
| 2026-08-26 | ⛔ **Task 5 — EXACTLY ONE ledger entry**: a dated, append-only `DF-13-5-A` trigger **observation** with **no closure verb** and no disposition. Condition 1 **NOT FIRED** (0 of 1,032, reported with the predicate definition in force); condition 2 `2026-11-22` **NOT re-dated**; `branch_taken: NEITHER`, `members_ratified: NONE`, `round_state: UNSPENT`, `protocol_edit: NONE`, entry **OPEN**. `deferred-work.md` 602,265 → 607,244 bytes, **1 CR / 0 CRLF** held, every byte above the note identical. Story 17.5's six re-homings and four scheduling notes **NOT** pulled in. |
| 2026-08-26 | A dated **append-only** note added to `stories/17-3-…md` recording the amendment to its guard, so the change is discoverable from the story that owns it. ⛔ **17.3 is not reopened**; its Status stays `done` and every byte above the note is identical. |
| 2026-08-26 | **Three-commit arc**, order load-bearing: `0b4bfd8` `feat(17-4)` the producer (no successor output yet) → `5bf27ca` `chore(17-4)` **THE MEASUREMENT** — the FIRST commit touching a `SUCCESSOR_OUTPUT_PATHS` entry — with `-148`/`-150`/`-152`, `-147` and the `-146` amendment → this record, the ledger note, the 17.3 note and the `sprint-status.yaml` transition. ⛔ `-147` did **not** land in commit 1. ⚠️ `DN-17-4-19` discloses the peer session's staged edits riding along in commit 3. |
| 2026-08-26 | Local gates re-run and recorded **LOCAL (Windows)**: `pytest` ⛔ **1,758 passed / 0 failed**, coverage **95.87%**, `mypy argus` clean over 96 files, `bandit -r argus --severity-level medium` **0 medium / 0 high**, `-135`..`-141` / `-127` / `-146` / `-147` / `-78` green (11 passed). `argus/` diff **EMPTY**; criterion module, `adjudication-record.json` and both silent-class artifacts byte-unchanged. **Status `in-progress` → `review`.** |
