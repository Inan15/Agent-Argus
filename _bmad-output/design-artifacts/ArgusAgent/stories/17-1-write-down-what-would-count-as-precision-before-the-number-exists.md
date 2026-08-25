---
baseline_commit: c2ce00f
---

# Story 17.1: Write down what would count as precision, before the number exists

Status: review

<!-- Contexted 2026-08-25 at HEAD `c2ce00f` (branch `docs/merge-strategy-decision`, working tree
     CLEAN) by the create-story workflow (Opus 5).

     EVERY FIGURE IN SECTION 0 WAS READ OFF THIS TREE BY EXECUTION, not copied from `epics.md`,
     from `sprint-change-proposal-2026-08-24.md`, from the 2026-08-24 research document or from
     `deferred-work.md`. The corpus manifest was imported and its partitions derived; the two
     committed adjudication artifacts were parsed; the pinned blob of `adjudication-record.json`
     was read out of the object database with `git show`; the four precision floors were resolved
     by calling the functions that derive them; the four detector conformance pins were read at
     HEAD.

     THREE PREMISES MOVED AGAINST WHAT THE EPIC ASSUMES, and each is load-bearing for this story:

       (1) SECTION 0.4 - `sealed n ratified` is EMPTY. All five ratified members are `pre-seal`.
           Protocol section 5's SEAL condition therefore reads FAILED over the population Story
           17.4 is chartered to measure, TODAY, before any successor exists. The measurement 17.4
           runs CANNOT clear the >=80% gate by construction, and 17.1 must pre-register that -
           or it gets discovered with a number in view, which is the exact failure this story
           exists to prevent.

       (2) SECTION 0.5 - the BREADTH floor is 3 distinct contributing members, and BOTH candidate
           successors whose per-member distribution is known today draw from exactly TWO.
           `V1` = minions 1 + agent-smith 5; `V2` = agent-smith 22 + minions 14. Each returns
           `UNEVALUABLE` on breadth as it stands. Pre-registering the consequence of that is
           worth more than any other sentence in this story.

       (3) SECTION 0.6 - the instrument's ENTIRE adjudicated history is 31 rows: 26 FP,
           5 BORDERLINE, ZERO TP. That is the measured anchor the false-accusation exposure
           ceiling is derived from, and it reproduces byte-exactly from the pinned blob.

     NOTHING HERE RATIFIES A MEMBER, FETCHES A THIRD-PARTY SOURCE, OR SPENDS `DF-13-5-A`'s
     ROUND. `eligible_member_count()` is 5 and stays 5. No detector was run over any corpus
     member to produce this file; every measurement is a read of committed artifacts, the
     manifest, or the git object database.

     NO SUCCESSOR PREDICATE IS DESIGNED HERE. `V1`/`V2`/`V5` appear only as the populations
     whose SHAPE the criterion must be able to grade. Choosing among them is Story 17.2's. -->

## Story

As the **Engineering Lead**,
I want **the precision criterion for any successor vacuity predicate committed, dated and frozen in code before that predicate exists**,
so that **a yield increase cannot be graded against a standard chosen once the result is in view.**

### What this story IS

The 2026-08-17 discipline applied one level down. That rule — *"we pursue ONE bench-expansion
round … if precision lands below 80% we take option (b)"* — was written **before Story 13.5 ran,
before Epic 15's bench was chosen, and before any number existed**, and that is the only reason it
is worth anything. Epic 17 is about to move the verdict-eligible population from **0** to
something. This story writes down what "good enough" means **while the answer is still 0**.

It lands **four artifacts and nothing else**:

1. **`scripts/precision_preregistration.py`** — the criterion as **frozen, pure code**: the
   population it will be measured over, the protocol version in force, the ratio floor *resolved*
   from the shipped constant, the three resolution floors *resolved* from the functions that
   derive them, the absolute false-accusation exposure ceiling with its pinned-blob provenance,
   the declared successor-output path set, and one pure fold that turns a candidate population
   into `MET` / `NOT_MET` / `UNEVALUABLE`.
2. **`_bmad-output/design-artifacts/ArgusAgent/successor-predicate-precision-preregistration.md`**
   — the dated, committed prose record: what was decided, when, by whom, why, and the named
   consequence of falling below.
3. **`tests/test_precision_preregistration.py`** — seven guards
   (`TC-ArgusAgent-PRECISION-001-135`..`-141`) that make each of the above **falsifiable** rather
   than asserted.
4. **This story's record**, and the two `sprint-status.yaml` transitions.

### What it is NOT

- ⛔ **NOT a successor predicate.** No detector logic, no scoring, no clause, no `V2`/`V5`
  implementation, no edit anywhere under `argus/detectors/**`. Story 17.2 specifies the successor;
  Story 17.3 builds it. **If a line of this story needs to know which successor wins, that line is
  in the wrong story.**
- ⛔ **NOT a protocol amendment.** `precision-validation-protocol.md` is **byte-unchanged**. No
  `V1.4` row, no new section-5 condition, no edit to the change log. §0.3 records why: the
  2026-08-20 operator decision states that adding a version row re-stamps `protocol_version`
  across all **31** committed human judgements, and *"a decision folded across an amendment is a
  re-interpretation of judgements nobody re-made."* The 2026-08-24 change proposal's artifact
  table lists **no** protocol change, and the epic approval unblocks **Story 17.1 only** — not a
  protocol act.
- ⛔ **NOT a new gate condition.** The criterion pre-registered here judges **the successor
  predicate**; §5's condition set judges **the gate**. They are different questions and the
  document must say so in terms. The gate stays `BLOCKED`, `protocol_cleared` stays `False`,
  the ≥80% keystone stays **NOT CLEARED**, FR34's disclosure stands.
- ⛔ **NOT a loosening of `consumed == 0`.** That asymmetry is the false-accusation moat. This
  story does not reach it, mention it as movable, or measure anything that would.
- ⛔ **NOT a change under `argus/**`.** §2.1 gives the reason in figures. Nothing here touches the
  shipped package, so there is **no `code_identity` question, no dogfood-artifact regeneration,
  no `Evidence-partition:` trailer obligation and no effect on `--cov=argus --cov-fail-under=80`.**
- ⛔ **NOT a ledger write.** `deferred-work.md` is **not in the write set**. Epic 17 assigns every
  re-homing and scheduling note to **Story 17.5**, and that file carries byte invariants (§2.6).
  ⛔ This story therefore claims **no `DF-*` closure** and must not write the word `CLOSED` on any
  line naming a `DF-*` id — `TC-ArgusAgent-DOCS-001-78` reads story files line-scoped for exactly
  that verb.
- ⛔ **NOT a spend of `DF-13-5-A`.** No member ratified, no third-party source fetched, no round
  consumed, branch (a) not executed and branch (b) not declared. The entry stays **OPEN and
  UNSPENT**. ⚠️ This story does not evaluate its 2026-08-24 trigger either — that is **17.4's**,
  by name.
- ⛔ **NOT a re-measurement of Epic 17's premise.** The Epic-18 retrospective's SD-2 already
  verified the 1,032-finding pinned-corpus re-derivation survived Epic 18's `code_identity` bump,
  with the reviewer re-running it independently. §0.2 re-derives the population **from the
  committed artifacts** rather than by running anything.
- ⛔ **NOT a reopening of Epics 1–16, Story 6.2, or any signed retrospective.**

---

## §0 — PREMISES MEASURED BY EXECUTION at HEAD `c2ce00f`

⛔ **Task 0 re-derives every row below before a line is written.** Every figure here is cheap to
reproduce — none requires running a detector, staging a corpus member, or fetching anything.
**A row that does not reproduce is an escalation (AC7), not a number to adjust.**

### §0.0 The tree, the paths, the baseline

| fact | value |
|---|---|
| HEAD | `c2ce00f545d89a0947d4706a3d0387c4cad59b0f` (`c2ce00f`) |
| branch | `docs/merge-strategy-decision` |
| `git status --porcelain` | **EMPTY** — the tree is clean at contexting, unlike 18.4's |
| artifact root | `_bmad-output/design-artifacts/ArgusAgent/` |
| story location | `…/stories/` (`sprint-status.yaml:6`) |
| next free `PRECISION-001` id | **`-135`** (area runs to `-134` in `tests/test_release_preflight.py`, `tests/test_silent_class.py`, `tests/test_silent_class_record.py`) |
| CI gates | `mypy argus` · `bandit -r argus --severity-level medium` · `pytest --cov=argus --cov-fail-under=80` (`.github/workflows/audit-ci.yml`) — **none of the three has `scripts/` in scope** |
| NFR-M1 | ≤1200 physical lines, population `git ls-files -- '*.py'`, so **`scripts/**` and `tests/**` are both swept** |

### §0.1 The four floors, RESOLVED by calling the code that derives them

```
PRECISION_GATE_THRESHOLD                        = Fraction(4, 5)    argus/precision/replay_harness.py:285
verdict_eligible_population_floor(4/5)          = 5                 argus/precision/gate_yield.py
contributing_member_floor(validation_floor_n()) = 3                 argus/precision/gate_breadth.py
sealed_member_floor(validation_floor_n())       = 3                 argus/precision/gate_seal.py
validation_floor_n() = 5     eligible_member_count() = 5     len(MANIFEST_FIELDS) = 9
GATE_OUTCOMES      = ['CLEARED', 'NOT_CLEARED', 'BLOCKED']
CONDITION_VERDICTS = ['MET', 'FAILED', 'NOT_APPLICABLE', 'UNEVALUABLE']
BREADTH_CONDITION_ID = 'denominator-breadth-contributing-members'
SEAL_CONDITION_ID    = 'gate-evidence-drawn-from-the-sealed-partition'
```

⛔ **Both member floors are the SAME derived number reached two ways** — `sealed_member_floor`
*calls* `contributing_member_floor`. `DN-3`'s one-floor rule. **The pre-registration resolves all
four; it re-types none of them.**

### §0.2 The population, re-derived from committed artifacts (nothing was run)

`validation-corpus/adjudication-set-13-5.json`, parsed at HEAD:

| member | total findings | `vacuous_test_heuristic` | share of 1,032 | seal partition | `eligible_for_n` |
|---|---:|---:|---:|---|---|
| minions | 1,727 | **648** | 62.8% | `pre-seal` | True |
| agent-smith | 898 | **295** | 28.6% | `pre-seal` | True |
| agent-markovich | 152 | **72** | 7.0% | `pre-seal` | True |
| xagents-webapp | 1,494 | **17** | 1.6% | `pre-seal` | True |
| **ai-body-runtime** | 13 | **0** | **0.0%** | `pre-seal` | True |
| **total** | **4,284** | **1,032** | 100% | | |

Rule classes emitted across the set: `orphan_code` 1,675 · `hardcoded_secret` 1,330 ·
`vacuous_test_heuristic` **1,032** · `cross_partition` 231 · `traceability_not_establishable` 16.

`validation-corpus/silent-class-record.json` independently reports `population_walked: 1032`,
`population_skipped: 0`, `protocol_version: V1.3`. **The 1,032 reproduces from two artifacts.**

⛔ **Four of five ratified members contribute a flagged finding; `ai-body-runtime` contributes
zero.** The breadth floor of 3 is met *at the flagged-population level*. It is **not** met by
either known candidate successor — §0.5.

### §0.3 The protocol version in force is **V1.3**, and it does not move

Change-log head: **V1.3, 2026-08-16** (Story 13.2). Both committed records carry
`protocol_version: "V1.3"`. `gate_decision.py:336` and `:841` **raise** when a record's
`protocol_version` differs from the change-log head, so the version is not decorative.

The three 2026-08-20 §5 amendments — **breadth** (16.1), **seal** (16.2), **yield** (16.3) — sit as
dated blocks **under V1.3**, deliberately: *"Adding a `V1.4` row would re-stamp `protocol_version`
across all 31 [judgements] — precisely the act `decide_gate`'s own refusal names."*

⛔ **The pre-registration NAMES V1.3. It does not create a version, add a §5 condition, or edit one
byte of `precision-validation-protocol.md`.**

### §0.4 ⛔ `sealed ∩ ratified` IS EMPTY — the gate cannot clear from 17.4's population

Derived from `tests/corpus/_manifest.py` (`CorpusMemberSpec.partition`, itself derived from each
row's pin by `gate_seal.partition_of`):

| partition | count | members |
|---|---:|---|
| `pre-seal` | **5** | the five **ratified** members — all of them |
| `sealed` | 6 | `aws-aws-sam-cli`, `celery-celery`, `certbot-certbot`, `conda-conda`, `getsentry-sentry-python`, `googleapis-google-auth-library-python` — **all `eligible_for_n=False`** |
| `open` | 10 | `pypa-pip`, `scrapy-scrapy`, `mitmproxy-mitmproxy`, `python-poetry-poetry`, `redis-redis-py`, `spotify-luigi`, `streamlink-streamlink`, `tox-dev-tox`, `argus-self-audit`, `minions-story-7-2-superseded` — all `eligible_for_n=False` |

**`sealed ∩ eligible = ∅`.** Against `sealed_member_floor = 3`, §5's seal condition
(`gate-evidence-drawn-from-the-sealed-partition`) reads **FAILED** over the five ratified members
**today**, and only a protocol §6 **R2** operator act ratifying ≥3 sealed members could change it.
⛔ **17.1 may not take that act and 17.4 is forbidden it.**

**Consequence, and this is the whole reason it is in §0:** whatever precision Story 17.4 measures
over the five ratified members, the **≥80% externalization gate cannot reach `CLEARED` from it**.
The pre-registration must therefore state, in advance, that its criterion is a judgement about
**the successor predicate**, not about the gate — and that meeting it moves **no gate condition**.
A criterion that is silent on this invites exactly one sentence six weeks from now: *"precision
came out at 84%, so the gate clears."* It does not.

### §0.5 ⛔ BOTH KNOWN CANDIDATE SUCCESSORS DRAW FROM TWO MEMBERS — below the breadth floor of 3

From `silent-class-record.json` (parsed at HEAD) and the 2026-08-24 measurement's §2 / §5 tables:

| candidate | definition | reach over 1,032 | contributing members | breadth verdict at floor 3 |
|---|---|---:|---|---|
| `V0` **shipped** | `disc≥1 ∧ cons==0 ∧ mref≥1` | **0** | **0** | population empty |
| `V1` drop-mref | `disc≥1 ∧ cons==0` | 6 | **2** (minions 1, agent-smith 5) | ⛔ **UNEVALUABLE** |
| `V2` silent | `disc≥1 ∧ span asserts NOTHING` | 36 | **2** (agent-smith 22, minions 14) | ⛔ **UNEVALUABLE** |
| `V5` unrelated | `disc≥1 ∧ asserts, none about the SUT` | 125 | **not measured per member** | unknown |
| `V4` per-call | `disc≥1` alone | 676 | not measured | *"too loose"* |

`silent-class-record.json` states `class_by_corpus_member: {agent-smith: 22, minions: 14}`,
`class_size: 36`, `counts: {UNADJUDICATED: 36, TP: 0, FP: 0, BORDERLINE: 0}`,
`gates_anything: False`, `promotes_nothing: True`.

⛔ **The most valuable pre-registered sentence available to this story is the consequence of a
2-member population.** It is `UNEVALUABLE` — a recorded failure to evaluate, not a pass, not a
fail, and **not** an invitation to argue the floor down. Written now it is discipline; written
after 17.4 reports `UNEVALUABLE` it is a concession.

### §0.6 ⛔ THE INSTRUMENT'S ENTIRE ADJUDICATED HISTORY: 31 rows, 26 FP, 5 BORDERLINE, **ZERO TP**

`validation-corpus/adjudication-record.json`, parsed at HEAD **and** re-read from the pinned blob:

```
git show 6c59115b2aad1e6ab9c7dd3ebba011f7d37376dd:_bmad-output/design-artifacts/ArgusAgent/validation-corpus/adjudication-record.json
  rows 31   dispositions {'FP': 26, 'BORDERLINE': 5}   TP 0
  protocol_version V1.3   adjudication_unit 'finding'   rule_id 'vacuous_test_ast' (31/31)
  by member {'minions': 24, 'agent-smith': 7}      <- TWO contributing members again
  6c59115 is an ANCESTOR of HEAD: True
```

**26 is the number of false accusations this instrument has produced across its entire recorded
history, judged by a named human under V1.3.** Zero true positives have ever been recorded.
§1.3 turns that into the exposure ceiling; `-136` turns the derivation into a guard.

### §0.7 The detector surface Epic 17 will touch — narrowed **after** Epic 17's plan was written

`epic-18-retro-2026-08-25.md` **SD-1** asks this story's §0 to record it, so it is recorded here
once and every later Epic-17 story cites this section rather than re-measuring:

| landed by 18.4 at HEAD | measured |
|---|---|
| `Detector` Protocol narrowed to `rule_id -> str` + `run -> Callable[..., DetectorResult]`, **both read-only `@property`** | `argus/detectors/base.py:147`–`:190` |
| `@runtime_checkable` **DELIBERATELY ABSENT** — no guard may decide by `isinstance`/`issubclass` | `base.py:176`–`:180` |
| **Four** `if TYPE_CHECKING:` static conformance pins, all **inside `argus/`** | `orphan_code.py:310`, `secret_scan.py:633`, `tool_runner.py:459`, `vacuous_test.py:799` |
| `TC-ArgusAgent-DETECT-001-145` — AST walk: **every** class defining `run() -> DetectorResult` must carry a pin | `tests/test_detector_base.py:224` |
| `TC-ArgusAgent-DETECT-001-146` — the Protocol's measured shape is a FENCE | `tests/test_detector_base.py:257` |
| shipped fact (b) | `vacuous_test.py:754`–`:797` `_ast_corroborated` → `sut_result_is_discarded ∧ mock_referencing_assertions >= 1` |

⛔ **This story moves none of it** and adds no detector class, so `-145` cannot fire here. **It is
recorded because 17.2/17.3 will add or edit one, and `-145` goes RED from the moment such a class
is written until its pin lands.** A dev who does not know why will be tempted to weaken the guard;
`DF-8-5-B` forbids that.

### §0.8 The precedent this story copies, rather than invents

**Story 15.1 is the same shape one level up** and its answer is reused wholesale:

| 15.1 | 17.1 |
|---|---|
| `scripts/candidate_selection.py` holds the frozen criteria (`CRITERIA`, `COOCCURRENCE_FILE_FLOOR`, `TEST_FILE_FLOOR`) | `scripts/precision_preregistration.py` holds the frozen criterion |
| `tests/test_candidate_selection.py` (`-74`..`-79`) guards them | `tests/test_precision_preregistration.py` (`-135`..`-141`) |
| `CRITERIA_COMMIT_SHA = "16d7100d…"` — a **full 40-hex** literal, recorded in a **later** commit than the one it names | `PREREGISTRATION_COMMIT_SHA`, same treatment (§2.2) |
| `CANDIDATE_OUTPUT_PATHS` — declared, non-empty, **candidate-scoped** so the absence asserted is a real one | `SUCCESSOR_OUTPUT_PATHS`, same treatment |
| `-75` ancestry check: sha must **resolve**; a **control path known to carry commits** asserted non-empty **first**; predicate driven to **both** outcomes | `-139`, reusing the idiom verbatim |
| `tests/test_gate_ordering.py` (16.4) **imports** those constants, never re-types them (`DN-16-4-2` / `AI-E9-7`) | Story 17.4 will import `SUCCESSOR_OUTPUT_PATHS` and `PREREGISTRATION_COMMIT_SHA` from here |

### §0.9 What is already true and must NOT be re-done

- The three §5 resolution conditions **already exist** and already return `UNEVALUABLE` /
  `FAILED`. ⛔ **No new terminal state is invented** — `CONDITION_VERDICTS` stays closed at four,
  `GATE_OUTCOMES` closed at three.
- `TC-ArgusAgent-DOCS-001-22`'s glob patterns are exactly `sprint-change-proposal-*.md` and
  `epic-*-retro-*.md`. The pre-registration document matches **neither**, so it needs **no**
  registration — and ⛔ **registering it would turn `-22` RED**, because `-22` also asserts every
  registered name is *found by the globs*. §2.4.
- Guard-RED observations are recorded **automatically** by `tests/conftest.py` into
  `.argus/guard-fires.jsonl` (gitignored). ⛔ **Do not hand-write a fires ledger.**
- `scripts/check_meta_drift.py` is **advisory** — not in CI, not in `tests/`. Its 2026-08-23
  baseline observes that **76% of `argus/` change over 128 commits was `argus/precision/`**, which
  is itself an argument for §2.1's placement decision.

---

## §1 — THE DECISIONS THIS STORY MAKES, AND WHY

### §1.1 The population: the five ALREADY-RATIFIED members, and only those

Locked. The criterion is measured over the **1,032 `vacuous_test_heuristic` findings recorded at
the five pinned shas** in `adjudication-set-13-5.json`. Not the sealed candidates, not the open
partition, not a new bench.

**Rejected:** including any sealed candidate — that requires a §6 R2 ratification, which is an
operator act, spends `DF-13-5-A`, and is forbidden to this story and to 17.4 alike.

### §1.2 The ratio floor: `PRECISION_GATE_THRESHOLD`, RESOLVED

The criterion's ratio floor **is the gate's own** — `Fraction(4, 5)`, imported from
`argus.precision.replay_harness`, compared as an exact `Fraction`, **never re-typed as `0.8`, as
`4/5`, or as the string `80%`**.

**Rejected:** a story-local, lower "17.4 acceptance threshold". A second threshold is precisely how
this project ended up with two corpora (`DN-3`), and a threshold set below the gate's own is a
threshold chosen to be passable.

### §1.3 ⛔ The false-accusation exposure ceiling — the one genuinely new quantity

**AC2 is explicit that a ratio alone is not enough.** It is insufficient in **both** directions and
the pre-registration answers both:

- **Downward (a tiny denominator).** Answered by **resolving the three floors that already
  exist** — yield ≥ 5, breadth ≥ 3 contributing members, seal ≥ 3 sealed contributing members —
  and pre-registering that a population failing any of them is `UNEVALUABLE`. ⛔ These are
  resolved, not authored.
- **Upward (unbounded absolute harm behind a good ratio).** 80% of 1,000 is 200 wrong
  accusations. This is what needs a new number: an **absolute integer ceiling** on adjudicated
  false accusations, evaluated **jointly** with the ratio.

**THE DECISION — `MAX_FALSE_ACCUSATION_EXPOSURE = 26`, derived, not chosen.**

> **The successor may not, over the pinned population, produce more adjudicated false accusations
> than this instrument's entire recorded false-accusation history.** That history is
> `adjudication-record.json` at `6c59115`: **26 FP** of 31 rows, judged by a named human under
> protocol V1.3 on 2026-08-17 (§0.6).

**Why this derivation and not a preference:**

- It is **measured and committed**, not invented — the project put 31 blocking findings in front
  of a human once, and 26 came back false. Nothing about the number is negotiable after the fact.
- It **reproduces from a pinned blob** (`git show 6c59115:…`), so `-136` can prove the derivation
  rather than trust the literal.
- It **bites without being a shutdown.** At the largest known candidate reach (`V5` = 125), the
  ratio binds first (26/125 → 79.2% < 80%); above ~130 eligible findings the ceiling becomes the
  binding constraint. §5 of the protocol refuses both *"a condition that cannot fail"* and, in the
  rule-class arm's words, a floor that *"would make CLEARED unreachable by construction"*. This
  sits between them.

**Rejected, each recorded in the document with its reason:**

| rejected ceiling | why not |
|---|---|
| `floor(yield_floor × (1 − p))` = **1** | At a target population of ~125 it demands ≥99.2% precision. That is a **shutdown**, which §5's own rule-class reasoning refuses. |
| `yield_floor` = **5** | Same failure, less obviously. |
| **48** (`DF-16-7-B`'s *"48 false accusations is what the moat is worth here"*) | Nearly twice the expected exposure — it could not bite at any reachable population, and *"a condition that cannot fail is not a threshold."* |
| a **percentage** of the population | That is the ratio again, wearing a different hat. AC2 asks for an absolute. |
| **resolved live** from `adjudication-record.json` | ⛔ **The record grows** — 17.4 appends to it. A ceiling that moves once the number is in view is the exact defect this story exists to prevent. It is **frozen as a literal, with the pinned sha it came from**, and `-136` re-derives from the pin. |

⛔ **The asymmetry is pre-registered with the number** (`DN-17-1-6`): the operator may **LOWER**
the ceiling or **RAISE** the ratio at any time. Neither may move the other way once
`PREREGISTRATION_COMMIT_SHA` exists. `-140` enforces exactly that, directionally.

### §1.4 The named consequence of falling below

Pre-registered in the shape of the 2026-08-17 rule — a branch, not a discussion:

> **If, over the pinned population, the successor's measured precision is `< PRECISION_GATE_THRESHOLD`,
> OR its adjudicated false accusations exceed `MAX_FALSE_ACCUSATION_EXPOSURE`, OR the population is
> `UNEVALUABLE` under any of the three resolution floors — the successor predicate is NOT promoted
> to verdict-eligible.** It ships **advisory-only**; `consumed == 0` and the conservative default
> stay exactly as they are; the FR34 disclosure stands; the gate stays `BLOCKED`; and the next
> attempt requires **a different predicate — not a bigger bench and not a loosened clause.**
>
> ⛔ **`DF-13-5-A` is NOT spent by that outcome and branch (b) is NOT declared by it.** Its
> pre-registered conditions are *zero blocking findings* or *precision below 80%* **over a spent
> round**, and 17.4 spends no round.
>
> ⛔ **AND THE CONVERSE, stated because it is the half that gets misread:** meeting the criterion
> **does not promote anything**. It produces a recorded, evidenced *proposal* to promote. Promotion
> is an operator act, `sealed ∩ ratified` is empty (§0.4), and Story 17.4 *"takes no branch."*

### §1.5 What the document must state in terms (AC3)

Verbatim obligations, because each is a sentence somebody will otherwise omit: **no member is
ratified** (`eligible_member_count()` is 5 before and after); **no third-party source is fetched**;
**no round is spent** — `DF-13-5-A` stays OPEN and UNSPENT, branch (a) not executed, branch (b) not
declared; **no protocol row is added** and no §5 condition is created; **no FR is amended**; **no
finding becomes verdict-eligible**; **nothing published changes.**

### §1.6 What this story does NOT fix, named so it is not mistaken for fixed

- ⛔ `DF-13-5-A` — **OPEN and UNSPENT**. Not evaluated here; 17.4 owns its trigger.
- ⛔ `DF-INV-VACUOUS-A` / `-B`, `DF-16-7-A` / `-B`, `DF-14-1-A`, `DF-12-2-D`, `DF-12-3-A` — all
  stay **OPEN and untouched**. Their re-homing notes are **Story 17.5's**.
- ⛔ `DF-AUD-DETECT-C` (unscheduled, `AI-E18-10`) and `-D` (Story 17.3) — untouched.
- ⛔ `AI-E16-7` — protocol §4's External adjudicator is still **UNFILLED**. This story needs no
  adjudicator (it adjudicates nothing). **17.4 does**, and the pre-registration must say so as a
  stated precondition rather than leave it to be discovered.
- ⛔ The **ruling index** (`architecture.md:1150`) does not exist as a document in this tree. This
  story does **not** create it — no guard requires it and doing so is scope creep. Its `DN-17-1-*`
  rulings live in this story record, which is what the rule points at.

---

## §2 — THE COUPLINGS THAT WILL BITE

### §2.1 ⛔ `scripts/`, NOT `argus/precision/` — and the reason is measured

Putting the criterion under `argus/precision/` looks natural and costs four things this story has
no business spending:

1. **Dogfood-artifact currency** (`architecture.md`, Story 12.1): *"an artifact is CURRENT iff …
   `argus/**` has not changed since that sha."* Any `argus/**` byte forces
   `python scripts/regenerate_dogfood_artifacts.py` plus its own commit, and `DF-INV-MERGE-A`
   means a squashed PR reddens `master` afterwards.
2. **`Evidence-partition:` trailer** — not triggered by `argus/precision/**` today
   (`DETECTOR_TUNING_PATHS` is `("argus/detectors", "argus/precision/replay_harness.py")`), but it
   puts this story one file away from a rule it has no reason to be near.
3. **`--cov=argus --cov-fail-under=80`** — a new `argus/` module drags the coverage gate.
4. **`mypy argus` / `bandit -r argus`** — blocking gates over a module that ships in the wheel and
   is never imported by `argus.cli`. The meta-drift baseline already records that 76% of recent
   `argus/` growth is gate machinery unreachable from the CLI.

**Story 15.1 put the identical artefact in `scripts/` and it has held for two epics.** Follow it.
`scripts/**` is still swept by NFR-M1 (`git ls-files -- '*.py'`) and still imported by tests via
the `sys.path.insert(_REPO_ROOT / "scripts")` idiom already in `tests/test_candidate_selection.py`.

### §2.2 ⛔ A COMMIT CANNOT CONTAIN ITS OWN SHA — the arc is THREE commits, in this order

`PREREGISTRATION_COMMIT_SHA` names the commit that froze the criterion, so it must be written
**after** that commit exists. 15.1 hit this and solved it the same way. 18.4's four-part arc
collapses to three here, because this story owes **no dogfood-regeneration commit** (§2.1).

- **Commit O — `chore(17-1): open the pre-registration story`**
  this story file + `sprint-status.yaml` `ready-for-dev` → `in-progress`. **Nothing else.**
- **Commit A — `feat(17-1): pre-register the successor-predicate precision criterion`**
  `scripts/precision_preregistration.py` (with `PREREGISTRATION_COMMIT_SHA = None`),
  the pre-registration document, and `tests/test_precision_preregistration.py` **minus `-139`
  and `-140`**, which are the two sha-dependent guards.
- **Commit B — `docs(17-1): record the pre-registration commit and the dev round`**
  fills `PREREGISTRATION_COMMIT_SHA` with commit A's **full 40-character lowercase** sha, adds
  `-139` and `-140`, and lands this story's record + the `sprint-status.yaml` transition.

⛔ **Commit A must touch NONE of `SUCCESSOR_OUTPUT_PATHS`** — that is the ordering claim `-139`
will assert about it, and 17.4's ancestry guard will assert about every later commit.
⛔ Commit messages **pure ASCII** (`DF-16-6-F`).

### §2.3 ⛔ THE GUARD THAT GOES GREEN BY FINDING NOTHING

Five of this story's seven guards assert a **negative**. This project shipped **35** guards in one
epic of which **4** were not real, one reducing to `f(x) == f(x)`. Every guard here therefore
pins its **precondition before its assertion** and is driven to **both** outcomes by an **executed
mutation**, per the GUARD-ADEQUACY CLAUSE (`architecture.md`, Story 13.2 / AC8.4):

- an empty `SUCCESSOR_OUTPUT_PATHS` makes `-139` forbid nothing → asserted non-empty first;
- `git log <sha> -- <pathspec>` returns empty both for a clean history **and for a misspelled
  path** → a **control path known to carry commits** is asserted non-empty first (`-75`'s answer,
  reused not re-invented);
- a pinned blob that fails to parse makes `-136` vacuous → row count and disposition vocabulary
  asserted non-empty first;
- an AST walk that matches nothing passes → `-135`/`-141` assert the walk found the module's real
  symbols before asserting what it did not find.

### §2.4 ⛔ DO NOT REGISTER THE DOCUMENT IN `_STATUS_DOCUMENTS`

`TC-ArgusAgent-DOCS-001-22` closes in **both** directions: it fails on a globbed file that is
unregistered **and** on a registered name the globs cannot find. The globs are
`sprint-change-proposal-*.md` and `epic-*-retro-*.md`; the pre-registration matches neither.
**Registering it turns `-22` RED. Leaving it alone is correct.**
⛔ Also: the document must contain **no undenied phrase from `_STATUS_CLAIMS`** (`"release ready"`,
`"production ready"`, `"safe to ship"`, …). It asserts a criterion, never a release status.

### §2.5 ⛔ DO NOT WRITE A CLOSURE VERB NEXT TO A `DF-*` ID

`story_closure_claims` is **line-scoped** and matches `CLOSED|Closes|closes|Closed by this story`
unless negated on the same line. This story closes nothing. Write *"stays OPEN and UNSPENT"*.

### §2.6 ⛔ THE TREE IS SHARED, AND THE ARTIFACT FILES CARRY BYTE INVARIANTS

A peer session commits to this same branch. ⛔ **Never `git add -A`.** Stage by explicit path and
verify the final write set with `git status --porcelain` against AC6.1.
⛔ `deferred-work.md` is **not in this story's write set at all**, which is the cleanest possible
answer to its byte invariants. ⛔ `sprint-status.yaml` is edited **surgically** — one status value
per transition, `last_updated` only; it carries extensive comment blocks and a STATUS DEFINITIONS
block that must survive byte-for-byte.

### §2.7 The idioms you need, so you do not go looking for them

| need | take it from |
|---|---|
| import a `scripts/` module from a test | `tests/test_candidate_selection.py:52`–`:57` (`sys.path.insert`) |
| a pure git read that never mutates | `tests/test_candidate_selection.py:95`–`:102` (`_git`, `capture_output`, `timeout=120`) |
| ancestry + non-vacuity preconditions | `tests/test_candidate_selection.py:198`–`:245` (`-75`) and `tests/test_gate_ordering.py:118` (`-101`) |
| an AST walk that forbids a symbol class | `argus/precision/gate_yield.py`'s `-99`; `tests/test_candidate_selection.py`'s `-74` |
| a rule written down where the next author reads it | `gate_seal.SEAL_CITATION_RULE`, `gate_breadth.BREADTH_MEMBER_FLOOR_DERIVATION` |
| resolving a repo path from a module that ships in a wheel | `gate_seal.DETECTOR_TUNING_PATHS` — repository-relative strings, resolved **by the caller** (`DF-9-2-A`) |
| exact-`Fraction` comparison, never float | `replay_harness.PRECISION_GATE_THRESHOLD`, `precision_fraction` |
| a fold that evaluates preconditions BEFORE the ratio | `adjudication.fold_adjudicated_precision` |

---

## §3 — AC ↔ TASK MAP

| AC | what it fixes | tasks | guards |
|---|---|---|---|
| AC1 | the criterion exists, dated, committed, complete | 0, 1, 2 | `-135`, `-137` |
| AC2 | exposure, not only a ratio | 1, 2 | `-136`, `-137`, `-138` |
| AC3 | ratifies / fetches / spends nothing, and says so | 2, 4 | `-141` |
| AC4 | the ordering is provable, not promised | 1, 5 | `-139`, `-140` |
| AC5 | the guards are real | 3, 5 | all seven |
| AC6 | scope, gates, commit arc | 4, 5 | — |
| AC7 | escalate, do not decide | all | — |

---

## Acceptance Criteria

### AC1 — A COMMITTED, DATED PRE-REGISTRATION EXISTS, AND IT IS COMPLETE

*(epics.md AC1: "a committed, dated pre-registration states the population precision will be
measured over, the adjudication protocol version, the acceptance threshold, and the named
consequence of falling below it — with no successor predicate implemented and no new finding in
existence".)*

- **AC1.1** — `scripts/precision_preregistration.py` exists, is **PURE** (no I/O, no clock, no
  `uuid`, no `random`, no network, no subprocess at import or in any exported function), and
  exports at minimum:
  `PREREGISTRATION_DATE` (`"2026-08-25"`), `PREREGISTERED_BY`, `POPULATION_ID`,
  `POPULATION_DERIVATION`, `POPULATION_SOURCE_ARTIFACTS`, `PROTOCOL_VERSION`,
  `precision_floor()`, `resolution_floors()`, `MAX_FALSE_ACCUSATION_EXPOSURE`,
  `EXPOSURE_CEILING_DERIVATION`, `EXPOSURE_SOURCE_PATH`, `EXPOSURE_SOURCE_SHA`,
  `CONSEQUENCE_BELOW`, `CONSEQUENCE_MET`, `SUCCESSOR_OUTPUT_PATHS`,
  `PREREGISTRATION_COMMIT_SHA`, `CRITERION_OUTCOMES`, and one pure fold
  `evaluate(...) -> CriterionAssessment`.
- **AC1.2** — `PROTOCOL_VERSION` is **`"V1.3"`**, and it is **checked against the change-log head**
  rather than asserted: the module (or its guard) resolves the head of
  `precision-validation-protocol.md`'s change-log table and refuses a mismatch, in the shape
  `gate_decision.py:336` already uses. ⛔ **No `V1.4` row is added and
  `precision-validation-protocol.md` is byte-unchanged.**
- **AC1.3** — `precision_floor()` **RESOLVES** `argus.precision.replay_harness.PRECISION_GATE_THRESHOLD`
  and `resolution_floors()` **RESOLVES** `verdict_eligible_population_floor`,
  `contributing_member_floor` and `sealed_member_floor` against `validation_floor_n()`.
  ⛔ **No floor is re-typed as a literal** (`DN-3`; `AI-E9-7`).
- **AC1.4** — `POPULATION_ID` names the five **already-ratified** members at their pinned shas and
  the `vacuous_test_heuristic` rule class; `POPULATION_DERIVATION` states the count (**1,032**) and
  the two committed artifacts it re-derives from. ⛔ **No sealed or open member is named as part of
  the population.**
- **AC1.5** — `CONSEQUENCE_BELOW` states §1.4's branch in terms, **including** the two ⛔ clauses:
  `DF-13-5-A` is not spent and branch (b) is not declared by a below-criterion outcome; and
  `CONSEQUENCE_MET` states that meeting the criterion **promotes nothing** and moves no gate
  condition.
- **AC1.6** — `_bmad-output/design-artifacts/ArgusAgent/successor-predicate-precision-preregistration.md`
  is committed, carries the date **2026-08-25**, the author role, the epic and story it belongs to,
  and states every field above **plus** §0.4's finding: that `sealed ∩ ratified` is **empty**, so
  the criterion judges the **successor predicate** and **not** the ≥80% gate, which stays `BLOCKED`.
- **AC1.7** — ⛔ **NO SUCCESSOR PREDICATE IS IMPLEMENTED AND NO NEW FINDING EXISTS.** Verified
  mechanically, not asserted: `git status --porcelain` shows nothing under `argus/detectors/**`,
  and `-139` proves no commit reachable from the pre-registration touches `SUCCESSOR_OUTPUT_PATHS`.

### AC2 — EXPOSURE, NOT ONLY A RATIO

*(epics.md AC2: "it states the maximum acceptable false-accusation exposure, not only a precision
floor — a ratio alone is satisfiable by a tiny denominator".)*

- **AC2.1 — the downward half.** The criterion states that a population failing **any** of the
  three resolution floors — yield `< 5`, contributing members `< 3`, sealed contributing members
  `< 3` — is **`UNEVALUABLE`**, resolved from `CONDITION_VERDICTS` (imported, never re-typed).
  ⛔ **No new terminal state is invented.**
- **AC2.2 — the upward half.** `MAX_FALSE_ACCUSATION_EXPOSURE` is an **absolute integer** cap on
  adjudicated false positives, evaluated **jointly with, and independently of**, the ratio.
  Its value is **26**; `EXPOSURE_CEILING_DERIVATION` records §1.3's derivation in the module's own
  words; `EXPOSURE_SOURCE_PATH` / `EXPOSURE_SOURCE_SHA` record the artifact and the **full 40-hex**
  pin (`6c59115b2aad1e6ab9c7dd3ebba011f7d37376dd`) it was derived from.
- **AC2.3** — the ceiling is **frozen as a literal**, ⛔ **never resolved live** from
  `adjudication-record.json`, and the module says why on the line (the record grows; 17.4 appends).
- **AC2.4** — `evaluate()` returns `NOT_MET` for at least one population whose **ratio passes** and
  whose **FP count exceeds the ceiling**, proving the second condition is not redundant with the
  first (`-137`).
- **AC2.5** — the document records the **four rejected ceilings** of §1.3's table with their
  reasons, and the **strengthening-only asymmetry**: the ceiling may be lowered and the ratio
  raised; neither may move the other way once `PREREGISTRATION_COMMIT_SHA` exists.

### AC3 — IT RATIFIES NOTHING, FETCHES NOTHING, SPENDS NOTHING — AND SAYS SO

*(epics.md AC3: "the pre-registration ratifies no member, fetches no third-party source, spends no
round, and says so in terms".)*

- **AC3.1** — the document states each of §1.5's clauses **in terms**, not by implication.
- **AC3.2** — measured before and after and recorded in the story: `eligible_member_count()` **5 →
  5**, `len(MANIFEST_FIELDS)` **9 → 9**, `len(GATE_OUTCOMES)` **3 → 3**,
  `len(CONDITION_VERDICTS)` **4 → 4**, `validation_floor_n()` **5 → 5**.
- **AC3.3 — enforced structurally, not promised** (`-141`): an AST walk of
  `scripts/precision_preregistration.py` rejects any import of `argus.detectors.*`,
  `urllib`, `requests`, `http.client`, `socket`, `ftplib`, or `subprocess`; and any write mode
  (`open(..., "w"/"a")`, `Path.write_*`, `json.dump`) anywhere in the module.
  Driven RED by **generated** mutants — one per forbidden symbol — not by a hand-written example.
- **AC3.4** — ⛔ `precision-validation-protocol.md`, `tests/corpus/_manifest.py`, everything under
  `validation-corpus/`, `E-PRD/prd.md`, `architecture.md`, `epics.md` and `deferred-work.md` are
  **byte-unchanged**, verified with `git status --porcelain`.

### AC4 — THE ORDERING IS PROVABLE FROM THE OBJECT DATABASE, NOT PROMISED IN PROSE

- **AC4.1** — `SUCCESSOR_OUTPUT_PATHS` is declared, **non-empty**, repository-relative,
  forward-slash, and **successor-scoped**: it names where a successor predicate's output over a
  corpus member would land. ⛔ It must **not** be widened to *"anything under
  `validation-corpus/`"* — the existing artifacts there are output over the ratified members and
  predate this story by weeks; folding them in would make the guard assert something false and
  invite someone to "fix" it by loosening the assertion (`-75`'s recorded reasoning).
- **AC4.2** — `PREREGISTRATION_COMMIT_SHA` is a **full 40-character lowercase hex** sha that
  **resolves to a commit** in this repository and is an **ancestor of `HEAD`**.
- **AC4.3** — `-139` asserts, over real git history, that **no commit reachable from
  `PREREGISTRATION_COMMIT_SHA` touches any `SUCCESSOR_OUTPUT_PATHS` entry** — with the three
  non-vacuity preconditions of §2.3 asserted **first**, and the ancestry predicate driven to
  **both** outcomes on real resolvable shas.
- **AC4.4** — ⛔ **The ancestry guard over *later* commits is Story 17.4's, not this story's.**
  This story exports the two constants 17.4 will **import** (`DN-16-4-2` / `AI-E9-7`) and records
  that hand-off by name in the story record.
- **AC4.5** — `-140` asserts the frozen field set — `POPULATION_ID`, `PROTOCOL_VERSION`,
  the ratio floor, `MAX_FALSE_ACCUSATION_EXPOSURE` — read from the **pinned blob**
  (`git show <PREREGISTRATION_COMMIT_SHA>:scripts/precision_preregistration.py`), and enforces the
  asymmetry **directionally**: `ceiling <= ceiling_at_pin` and `ratio >= ratio_at_pin`, with
  `POPULATION_ID` and `PROTOCOL_VERSION` **equal**. ⛔ `PREREGISTRATION_COMMIT_SHA` itself is
  **excluded** from the frozen field set — commit B legitimately writes it (§2.2).

### AC5 — SEVEN GUARDS, EACH WITH AN OBSERVABLE AND AN EXECUTED MUTATION

⛔ **GUARD-ADEQUACY CLAUSE.** For **each** guard the story record states (i) the observable,
(ii) a demonstration that the defect **moves** that observable — RED at the **real seam**, not
against a reconstruction — and (iii) at least one adversarial variant **generated** from the
module, the record or the path set rather than hand-written.

New module `tests/test_precision_preregistration.py`, area `TC-ArgusAgent-PRECISION-001-135`..`-141`.
⛔ **No new verification area is opened** — the pre-registration governs the precision gate's
substrate, so it continues `PRECISION-001`. ⛔ Ids are the next **actually free** ones; **no
existing id is renumbered** (§0.0).

- **`-135`** — **the ratio and the floors are RESOLVED, never re-typed.** AST-walk the module;
  fail on any numeric literal or `Fraction(...)` construction equal to the threshold or to any of
  the three floors, and fail if the resolving imports are absent. *Adversarial:* mutants generated
  by substituting each resolved call with its current integer value.
- **`-136`** — **the exposure ceiling re-derives from the pinned blob.**
  `git show <EXPOSURE_SOURCE_SHA>:<EXPOSURE_SOURCE_PATH>`, parse, count `FP`, assert it equals
  `MAX_FALSE_ACCUSATION_EXPOSURE` (**26**). Preconditions first: the sha resolves, is an ancestor
  of `HEAD`, the blob parses, `rows` is non-empty, the disposition vocabulary is non-empty.
  *Adversarial:* perturb the counted label and assert the count moves.
- **`-137`** — **the ceiling is not redundant with the ratio.** `evaluate()` driven over four
  synthetic populations: ratio-pass/exposure-pass → `MET`; ratio-pass/exposure-fail → `NOT_MET`;
  ratio-fail/exposure-pass → `NOT_MET`; both fail → `NOT_MET`. ⛔ **This is AC2's whole point and
  it is watched failing, not only passing.**
- **`-138`** — **a thin or narrow population is `UNEVALUABLE`, never `MET`.** Driven at breadth 2
  (**the measured shape of both `V1` and `V2`**, §0.5), yield 4, and sealed-contributing 0 — each
  independently, and each with a ratio that would otherwise pass. `UNEVALUABLE` is read from
  `CONDITION_VERDICTS`, not typed.
- **`-139`** — **the ordering** (AC4.3), reusing `-75`'s preconditions verbatim.
- **`-140`** — **the criterion's directional immutability** (AC4.5).
- **`-141`** — **AC3.3's structural ban**, plus the five before/after constants of AC3.2 compared
  by import.
- **AC5.8** — every guard's docstring names its `TC-` id, its AC, its observable and its
  non-vacuity precondition, per the house pattern in `tests/test_candidate_selection.py`.

### AC6 — SCOPE, GATES AND THE COMMIT ARC

- **AC6.1 — ⛔ THE WRITE SET IS EXACTLY:**
  1. `scripts/precision_preregistration.py` — **NEW**
  2. `_bmad-output/design-artifacts/ArgusAgent/successor-predicate-precision-preregistration.md` — **NEW**
  3. `tests/test_precision_preregistration.py` — **NEW**
  4. this story file
  5. `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — **status transitions and
     `last_updated` only**

  ⛔ **NOT in it:** anything under `argus/**`, anything under `tests/corpus/**` or
  `validation-corpus/**`, `precision-validation-protocol.md`, `deferred-work.md`, `epics.md`,
  `architecture.md`, `E-PRD/prd.md`, `tests/test_status_document_registry.py`,
  `tests/test_candidate_selection.py`, `tests/test_gate_ordering.py`, any other test module, any
  other `scripts/` module, the dogfood artifacts, `meta-drift-baseline.md`, any `done` story's
  record, and **anything under `minions_core/apaa/`**.
- **AC6.2** — the commit arc is **three** commits in §2.2's order (`chore` open → `feat` → `docs`
  record), messages **pure ASCII**. ⛔ **No `Evidence-partition:` trailer is required or added** — the write set
  touches neither `argus/detectors` nor `argus/precision/replay_harness.py`, the only two
  `DETECTOR_TUNING_PATHS` entries. Adding one anyway would assert a corpus provenance that does
  not exist.
- **AC6.3** — ⛔ **No dogfood-artifact regeneration and no `code_identity` movement.** `argus/**`
  is byte-unchanged; if it is not, the story has left its scope (AC7).
- **AC6.4** — green at the end, **every exit code recorded**: `python -m pytest -q`; the same with
  `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`; `pytest --cov=argus --cov-report=term-missing --cov-fail-under=80`;
  `mypy argus`; `bandit -r argus -f txt --severity-level medium`;
  and by name `tests/test_precision_preregistration.py`, `tests/test_module_size_ceiling.py`,
  `tests/test_status_document_registry.py`, `tests/test_governance_record_integrity.py`,
  `tests/test_candidate_selection.py`, `tests/test_gate_ordering.py`, `tests/test_gate_seal.py`,
  `tests/test_gate_breadth.py`, `tests/test_validation_corpus.py`, `tests/test_silent_class.py`,
  `tests/test_dogfood_artifact_currency.py`, `tests/test_release_preflight.py`,
  `tests/test_evidence_citation.py`.
  ⛔ Run with `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared.
- **AC6.5** — NFR-M1: both new `.py` files stay ≤ **1,200** physical lines. **Split, never shave,
  never exempt.**
- **AC6.6** — `AI-E13-1`: the local run is **Windows-only** and is recorded as **LOCAL**. CI's
  ubuntu matrix owns the cross-platform claim. ⛔ `-136`/`-139`/`-140` shell out to `git`; use
  `subprocess.run([...])` with an explicit `-C`/`cwd`, **never** `shell=True`, and **no**
  POSIX-only path assumptions.
- **AC6.7** — ⛔ stage by **explicit path**; verify the final write set equals AC6.1 exactly with
  `git status --porcelain`. ⛔ **Never `git add -A`** — a peer session shares this branch (§2.6).

### AC7 — ESCALATE, DO NOT DECIDE

⛔ **STOP and escalate — do not decide — if any of these becomes necessary:**

- any **§0 row fails to reproduce** at Task 0 — in particular §0.4's empty `sealed ∩ ratified`,
  §0.5's 2-member candidate distributions, or §0.6's **26**. ⛔ **The fallback is not to adjust the
  number.** Report the measurement and STOP;
- the **exposure ceiling** must differ from **26**, or its derivation must change. ⛔ That is the
  Engineering Lead's act — the 2026-08-17 rule was taken by XAgent007, and this is the same act
  class. **Land 26 with its recorded derivation and rejected alternatives, and RAISE it for
  ratification** (Task 6.2); do not substitute a preference;
- `precision-validation-protocol.md` must be edited, a `V1.4` row added, or a §5 condition created;
- a member must be ratified, a third-party source fetched, or `DF-13-5-A` spent;
- `argus/**`, `tests/corpus/**` or anything under `validation-corpus/` must be written;
- any successor-predicate logic, however small, looks necessary here;
- `CONDITION_VERDICTS`, `GATE_OUTCOMES`, `MANIFEST_FIELDS`, `VALIDATION_SET_FLOOR_N` or
  `PRECISION_GATE_THRESHOLD` must move;
- a **guard must be loosened, skipped or deleted** to go green (`DF-8-5-B`);
- a **new `DF-*` entry** looks necessary — `AI-E9-8`: recording is this story's job in its own
  record, **filing is the Engineering Lead's**;
- any `DN-*` must be reopened. ⛔ **A `DN-*` you disagree with is an escalation, not a story
  decision.**

---

## Dev Notes

### Decisions this story TAKES, each with its rejected alternative

- **`DN-17-1-1` — the criterion lives in `scripts/`, not `argus/precision/`.** *Rejected:*
  `argus/precision/preregistration.py`, which is where it "belongs" by subject matter. §2.1 counts
  the four costs; Story 15.1's `scripts/candidate_selection.py` is the precedent and it has held
  for two epics.
- **`DN-17-1-2` — no protocol amendment; V1.3 is NAMED, not created.** *Rejected:* a `V1.4` row or
  an eighth §5 condition. The 2026-08-20 operator decision records that a version row re-stamps 31
  committed judgements; the 2026-08-24 change proposal lists **no** protocol change; the epic
  approval unblocks 17.1 only.
- **`DN-17-1-3` — the exposure ceiling is 26, DERIVED from the pinned adjudication record.**
  *Rejected:* 1, 5, 48, a percentage, and a live resolution — §1.3's table, reproduced verbatim in
  the document.
- **`DN-17-1-4` — the ceiling is frozen as a literal with a pinned-blob provenance, and the guard
  re-derives it.** *Rejected:* resolving it live, which would move the criterion the moment 17.4
  appends a row. This is the one place a literal is right, and the reason is written on the line.
- **`DN-17-1-5` — the criterion judges the SUCCESSOR PREDICATE, not the gate.** *Rejected:*
  wording it as a gate criterion. §0.4 measured `sealed ∩ ratified = ∅`, so 17.4's population
  cannot clear the gate; a criterion silent on that invites *"84%, so the gate clears."*
- **`DN-17-1-6` — the strengthening-only asymmetry is pre-registered WITH the number.** *Rejected:*
  an immutable ceiling. §5's own amendments are permitted precisely because they can only make
  clearing harder; the same asymmetry is what lets the operator ratify a stricter value without
  reopening the pre-registration.
- **`DN-17-1-7` — a three-commit arc (`chore` open → `feat` → `docs`).** *Rejected:* folding the
  criterion and its sha into one commit — a commit cannot contain its own sha (§2.2), and 15.1
  solved this the same way. *Also rejected:* 18.4's fourth `chore`, the dogfood regeneration, which
  this story does not owe because `argus/**` is out of its write set.
- **`DN-17-1-8` — the pre-registration document is NOT registered in `_STATUS_DOCUMENTS`.**
  *Rejected:* registering it "for safety". `-22` closes in both directions and would go RED
  (§2.4).
- **`DN-17-1-9` — `deferred-work.md` is not in the write set.** *Rejected:* appending a note here.
  Epic 17 assigns every re-homing and scheduling note to Story 17.5; splitting that across two
  stories is how an append-only ledger acquires two half-notes.

### Locked decisions this story CITES rather than reopens

`DN-3` (one floor, never forked) · `DN-4` (pin by commit) · `DN-14-2-1` (the two-table split;
the frozen corroboration table) · `DN-16-4-2` / `AI-E9-7` (constants imported, never re-typed;
no prose copy of a pinned constant) · `DN-MATCH-KEY-REUSE` · §3.4 evidence immutability (strike,
never erase) · the OI1 lock (protocol §7: precision over **findings**, `N` locked at 5) ·
cross-cutting #6 (advisory-by-contract; the conservative default IS the moat) · `AR4` (no floats;
counts, never rendered sets) · `AR7` (one derivation per question) · `AR8` (pure) · `NFR-D2` ·
`NFR-R1` · `NFR-M1` (≤1200) · `NFR-S1` (no source bytes, no exception text persisted) ·
`DF-8-5-B` (a guard is never weakened to go green) · `AI-E9-8` (recording is the story's, filing
is the operator's) · `AI-E11-1` (an absence is evidence only over a population proved non-empty).

### Open ledger entries bearing on this story — verify against `deferred-work.md` on disk

| entry | state at contexting | bearing |
|---|---|---|
| `DF-13-5-A` | **OPEN, UNSPENT.** Declined twice (2026-08-22, 2026-08-24); trigger sharpened 2026-08-24 to *"shipped promotions rise above ZERO"*; backstop **2026-11-22, not re-dated** | ⛔ This story neither spends nor evaluates it. **17.4** evaluates the trigger. |
| `DF-INV-VACUOUS-A` | OPEN | The measured reason Epic 17 exists (§0.5). Names the two charter constraints this story discharges the first of. |
| `DF-INV-VACUOUS-B` | OPEN, 🟡 latent | ⛔ *"DO NOT PROPOSE THIS AS THE YIELD FIX — worth 0 → 1."* Not touched here. |
| `DF-16-7-B` | OPEN | Records that `V2` is a genuinely **different** predicate and **30 of its 36 rows lie outside `V1`**; and that 36 → 84 through the wide table is **48 false accusations**. Cited in §1.3's rejected table. |
| `DF-16-7-A`, `DF-14-1-A`, `DF-12-2-D`, `DF-12-3-A` | OPEN | Re-homing is **Story 17.5's**. Untouched. |
| `DF-AUD-DETECT-C` | OPEN, **unscheduled** (`AI-E18-10`) | Untouched. |
| `DF-AUD-DETECT-D` | OPEN, scheduled on **17.3** | Untouched. |
| `AI-E16-7` | **UNFILLED** — protocol §4's External adjudicator tie-break | Not needed here; **is** needed by 17.4. The pre-registration states it as a precondition. |

### Dependencies — none are added, and that is a requirement

No new third-party dependency, no `pyproject.toml` edit, no lockfile change. The criterion module
imports only the stdlib plus the existing `argus.precision` / `tests.corpus` symbols it resolves;
the guard module adds `ast`, `json`, `subprocess`, `pathlib` — all already used by
`tests/test_candidate_selection.py` and `tests/test_gate_ordering.py`.
⚠️ **No web research is warranted for this story and none was performed** — nothing here depends on
a library version, an external API, or a framework release. The stack is CPython 3.11–3.13,
`pytest`, `mypy`, `bandit`, all already pinned by `pyproject.toml`, and none is on the path this
story touches. Recorded as *considered and declined* rather than skipped.

### Standing rules (non-negotiable)

1. **PURE means pure** — the criterion module takes no I/O, no clock, no `uuid`, no `random`, no
   network, no subprocess. The **guards** may shell out to `git` for read-only verbs; the module
   may not.
2. **Exact `Fraction`, never float.** `precision >= Fraction(4, 5)`, never `>= 0.8` (AR4).
3. **Counts, never rendered sets** (NFR-D2 / AR4).
4. **No source bytes, no secret values, no exception text, no host paths** in any committed
   artifact (NFR-S1).
5. **Failure is a recorded condition, never an uncaught raise** out of a public entry point
   (NFR-R1) — except at construction, where refusing a malformed pin is correct
   (`UnsealablePin`'s precedent).
6. **A negative is only evidence if the population was proved non-empty first** (`AI-E11-1`).
7. **§3.4:** nothing already committed is rewritten. Corrections are dated additions.

### Previous-story intelligence

**There is no Story 17.0 — this is Epic 17's first story.** The nearest predecessors are Epic 18's
four (all `done`, 2026-08-24/25) and Epic 16's seven. What carries forward:

- **From 18.4** — SD-1's detector-contract change (§0.7); and the pattern of a story that lands a
  **contract plus its enforcing guard** and proves the change **output-neutral**. 18.4 passed
  review at **iteration 1 with zero findings**, with `§0` re-measured before a line was written.
- **From 18.1** — a `feat` commit lost a sha to a **forgotten `Evidence-partition:` trailer**.
  This story's answer is different and stronger: it stays out of `DETECTOR_TUNING_PATHS` entirely
  (AC6.2), so the trailer is neither required nor added.
- **From 18.3** — a `code_identity` bump busts every stage memo and moves the cache key. ⛔ This
  story must not move it; `argus/**` is out of the write set.
- **From 16.4** — a story may legitimately **HALT on an operator act** and be answered. AC7's
  exposure-ceiling escalation is deliberately *not* shaped that way: the number **lands with its
  derivation** and the operator ratifies or tightens it, so the loop is not blocked on a value that
  can only be strengthened afterwards.
- **From 15.1** — the whole shape of this story (§0.8), including the two-commit sha arc and the
  three non-vacuity preconditions on an ancestry guard.
- **From 16.1/16.2/16.3** — the house form of a pre-registered rule: a `*_DERIVATION` string that
  states the rule, the rejected alternatives, and *why the shape is the shape*, living **beside**
  the constant so the next author reads it without hunting.

### Git intelligence

`c2ce00f` (merge) ← `ee855a6` `docs(18-1): disclose the second hardcoded_secret finding` ←
`21f849a` (merge) ← `ab9f47f` `docs(18): commit the epic-18 review record, retrospective and
roll-up` ← `28b1f64` `docs(18-4): close DF-AUD-DETECT-F in the ledger; record the 18.4 dev round`
← `0729325` `chore(18-4): regenerate the three dogfood artifacts` ← `0ba6a98` `feat(18-4): narrow
the Detector Protocol…` ← `a862d8a` `chore(18-4): open the detector-Protocol story`.

Read off that arc and applied above: the **four-part commit convention**
(`chore` open → `feat` → `chore` regenerate → `docs` record) collapses here to **two**, because
this story writes nothing under `argus/**` and therefore owes **no dogfood regeneration commit** —
the one thing `0729325` exists for. The opening `chore` (`a862d8a`'s shape) is kept. ⚠️ The branch is **ahead of `origin/master`** and
`audit-ci.yml` triggers on `master`/`main` only, so **no CI evidence is available for this work at
its own sha**; every gate claim in the record is **LOCAL (Windows)** until it is green at a pushed
sha (`AI-E13-1`; epic-18 retro SD-4).

### References

- `_bmad-output/design-artifacts/ArgusAgent/epics.md:3400`–`3489` — Epic 17 charter, the binding
  ordering constraint, the operator approval, and Story 17.1's three ACs
- `…/sprint-change-proposal-2026-08-24.md` §2 (artifact conflicts — **no** protocol/PRD/architecture
  change), §3 (the two charter constraints), §5 (handoff: *"⛔ 17.1 must precede any 17.3 output"*)
- `…/precision-validation-protocol.md` §1 (substrate), §2 (roles), §4 (adjudication ladder; step 3
  unfilled), §5 (the seven conditions; the 2026-08-20 breadth/seal/yield blocks; *"a §5 condition
  that cannot fail is not a threshold"*; *"NO CHANGE-LOG VERSION WAS TAKEN"*), §7 (OI1), Change log
- `…/deferred-work.md` — `DF-13-5-A` (the 2026-08-17 rule; two declinations; the 2026-08-24
  sharpened trigger), `DF-16-7-B`, `DF-INV-VACUOUS-A`/`-B`
- `…/research/technical-argusagent-stage-mismatch-measurement-2026-08-24.md` §2 (clause counts and
  the per-member table), §5 (the `V0`..`V5` variant table)
- `…/epic-18-retro-2026-08-25.md` **SD-1** (the detector-contract context update §0.7 discharges),
  **SD-2** (Epic 17's premise survived intact), **SD-4** (evidence is local/unpushed)
- `…/architecture.md` — Implementation Patterns; **GUARD-ADEQUACY CLAUSE**; Adjudication-record,
  Gate-decision, Module-size, Dogfood-currency, Ledger-claim-cross-check and Ruling-index
  enforcement blocks
- `argus/precision/replay_harness.py:285`; `argus/precision/gate_yield.py`;
  `argus/precision/gate_breadth.py`; `argus/precision/gate_seal.py:271`–`:305`, `:338`;
  `argus/precision/gate_decision.py:222,336,841`; `argus/precision/gate_conditions.py:80`;
  `argus/precision/adjudication.py` (`fold_adjudicated_precision`)
- `tests/corpus/_manifest.py:110` (`MANIFEST_FIELDS`), `:1058` (`eligible_member_count`), `:1072`
- `tests/test_candidate_selection.py:52`–`:102`, `:198`–`:245`; `tests/test_gate_ordering.py:1`–`:33`
- `tests/test_status_document_registry.py:78`, `:375`–`:395`, `:461`–`:500`
- `tests/test_governance_record_integrity.py:40`–`:72`, `:197`
- `argus/detectors/base.py:147`–`:190`; `argus/detectors/vacuous_test.py:754`–`:807`;
  `tests/test_detector_base.py:224`, `:257`

---

## Tasks & Subtasks

### ⛔ Task 0 — RE-MEASURE §0 BEFORE WRITING ANYTHING (AC1.7, AC3.2, AC7)

- [x] 0.1 Confirm `git status --porcelain` is **empty** (or that every dirty path belongs to the
      peer session and is none of AC6.1's). Record `git rev-parse HEAD`.
- [x] 0.2 Re-derive **§0.1**'s four floors and five vocabulary sizes by importing and calling.
- [x] 0.3 Re-derive **§0.2**'s per-member table from `adjudication-set-13-5.json`, and cross-check
      `1032` against `silent-class-record.json`'s `population_walked`.
- [x] 0.4 Re-derive **§0.4**: `sealed ∩ eligible`. ⛔ **If it is non-empty, STOP** — a §6 R2
      ratification happened and the whole criterion needs re-shaping (AC7).
- [x] 0.5 Re-derive **§0.5**: `class_by_corpus_member` from `silent-class-record.json`; confirm
      **2** contributing members.
- [x] 0.6 Re-derive **§0.6** twice — from the working-tree file **and** from the pinned blob at
      `6c59115` — and confirm **26 FP / 31 rows / 0 TP** both ways and that `6c59115` is an
      ancestor of `HEAD`. ⛔ **If 26 does not reproduce, STOP** (AC7).
- [x] 0.7 Re-read **§0.7** at HEAD: the four `if TYPE_CHECKING:` pins and `-145`/`-146`.
- [x] 0.8 Confirm `-135` is still the next free `PRECISION-001` id.
- [x] 0.9 Record every row that came out **different**, with the new value. ⛔ **Record it; do not
      smooth it.**

### Task 1 — THE CRITERION AS CODE (AC1.1–AC1.5, AC2.1–AC2.4, AC4.1)

- [x] 1.1 Create `scripts/precision_preregistration.py`. Module docstring states: what a
      pre-registration is, why it is dated, the 2026-08-17 precedent, and ⛔ that nothing here
      ratifies/fetches/spends.
- [x] 1.2 `precision_floor()` and `resolution_floors()` — **resolving** calls only. No literals.
- [x] 1.3 `POPULATION_ID` / `POPULATION_DERIVATION` / `POPULATION_SOURCE_ARTIFACTS` — the five
      ratified members, their pinned shas, the rule class, the count 1,032, the two artifacts.
- [x] 1.4 `PROTOCOL_VERSION = "V1.3"` + the change-log-head check (AC1.2).
- [x] 1.5 `MAX_FALSE_ACCUSATION_EXPOSURE = 26`, `EXPOSURE_CEILING_DERIVATION`,
      `EXPOSURE_SOURCE_PATH`, `EXPOSURE_SOURCE_SHA` — with §1.3's four rejected alternatives named
      in the derivation string, and the *"never resolved live"* reason on the line (AC2.3).
- [x] 1.6 `CONSEQUENCE_BELOW` / `CONSEQUENCE_MET` — §1.4 verbatim, both ⛔ clauses included.
- [x] 1.7 `SUCCESSOR_OUTPUT_PATHS` — non-empty, successor-scoped, repository-relative,
      resolved **by the caller** (`DETECTOR_TUNING_PATHS`' treatment, `DF-9-2-A`).
- [x] 1.8 `CRITERION_OUTCOMES` (`MET` / `NOT_MET` / `UNEVALUABLE`) — refusing an unregistered
      member, `GATE_OUTCOMES`' shape. `UNEVALUABLE` reached from `CONDITION_VERDICTS`.
- [x] 1.9 `evaluate(...) -> CriterionAssessment` — a pure fold taking the eligible count, the
      contributing-member count, the sealed-contributing count, and the TP/FP counts; returning the
      outcome **plus the counts that produced it**. ⛔ Resolution floors evaluated **before** the
      ratio, exactly as `fold_adjudicated_precision` evaluates reproducibility first.
- [x] 1.10 `PREREGISTRATION_COMMIT_SHA = None` for commit A.

### Task 2 — THE DATED DOCUMENT (AC1.6, AC2.5, AC3.1)

- [x] 2.1 Write `successor-predicate-precision-preregistration.md`: date **2026-08-25**, author
      role, epic/story, and every field — **citing the module's constants by name rather than
      restating their values where a value is pinned elsewhere** (`AI-E9-7`).
- [x] 2.2 State **§0.4** in terms: `sealed ∩ ratified` is empty, the seal condition reads FAILED,
      the criterion judges the **successor**, the gate stays `BLOCKED`.
- [x] 2.3 State **§0.5** in terms: both known candidates draw from 2 members and are
      `UNEVALUABLE` on breadth as they stand.
- [x] 2.4 State the four rejected ceilings and the strengthening-only asymmetry (AC2.5).
- [x] 2.5 State AC3's five clauses **in terms**, and `AI-E16-7` as a **17.4 precondition**.
- [x] 2.6 ⛔ Contains no undenied `_STATUS_CLAIMS` phrase; ⛔ contains no closure verb on a line
      naming a `DF-*` id; ⛔ **not** added to `_STATUS_DOCUMENTS` (§2.4).

### Task 3 — THE GUARDS THAT DO NOT NEED A SHA (AC5, AC2.4, AC3.3)

- [x] 3.1 Create `tests/test_precision_preregistration.py`; module docstring in the
      `test_candidate_selection.py` form — area, why no new area is opened, and the vacuity it is
      built against.
- [x] 3.2 `-135`, `-136`, `-137`, `-138`, `-141`. Each: precondition asserted first, assertion,
      then an **executed** adversarial mutation.
- [x] 3.3 Run each one RED at its **real seam** before it is green; record the id, the mutation and
      the observation. (`.argus/guard-fires.jsonl` records automatically — **do not hand-write it**.)

### Task 4 — PROVE NOTHING MOVED (AC3.2, AC3.4, AC6.3)

- [x] 4.1 Re-measure AC3.2's five constants; record **before → after**.
- [x] 4.2 `git status --porcelain` — confirm `argus/**`, `tests/corpus/**`, `validation-corpus/**`,
      `precision-validation-protocol.md`, `deferred-work.md`, `epics.md`, `architecture.md`,
      `E-PRD/prd.md` are **all absent** from the diff.
- [x] 4.3 Confirm no dogfood artifact changed and no `code_identity` moved.

### Task 5 — THE ARC, THE SHA, AND THE ORDERING GUARDS (AC4.2–AC4.5, AC6.2, AC6.4, AC6.7)

- [x] 5.0 Commit **O** (`chore`) — this story file + `sprint-status.yaml` `ready-for-dev` →
      `in-progress`, and **nothing else** — before any of Tasks 1–4 is staged.
- [x] 5.1 Stage **by explicit path** and make **commit A** (`feat`). ⛔ Verify with
      `git show --stat` that it touches **no** `SUCCESSOR_OUTPUT_PATHS` entry.
- [x] 5.2 Read commit A's **full 40-hex** sha; write it into `PREREGISTRATION_COMMIT_SHA`.
- [x] 5.3 Add `-139` and `-140`; run both RED first (a deliberately wrong sha for `-139`; a raised
      ceiling for `-140`), then green.
- [x] 5.4 Run AC6.4's gate list; record every exit code as **LOCAL (Windows)**.
- [x] 5.5 Make **commit B** (`docs`) — module sha + the two guards + this story's record +
      `sprint-status.yaml` transition.

### Task 6 — HAND-OFF (AC4.4, AC7)

- [x] 6.1 Record, in the Completion Notes, the two constants Story 17.4 must **import**
      (`PREREGISTRATION_COMMIT_SHA`, `SUCCESSOR_OUTPUT_PATHS`) and ⛔ that 17.4's ancestry guard
      over later commits is 17.4's to write.
- [x] 6.2 Record the **exposure-ceiling ratification** owed to XAgent007 (AC7) — value, derivation,
      rejected alternatives, and the fact that it may only be **lowered**.
- [x] 6.3 Record anything **observed but not filed** (`AI-E9-8`) — recording is this story's job,
      filing is the operator's.
- [x] 6.4 ⛔ Confirm `DF-13-5-A` is untouched and `deferred-work.md` is absent from the diff.

---

## Dev Agent Record

### Agent Model Used

Opus 5 (`claude-opus-5[1m]`), `bmad-dev-story` workflow, iteration 1. Local gate run is
**Windows-only** and is recorded as **LOCAL** throughout (`AI-E13-1`; epic-18 retro SD-4). The
branch is ahead of `origin/master` and `audit-ci.yml` triggers on `master`/`main` only, so **no CI
evidence exists for this work at its own sha.**

### Debug Log References

#### Task 0 — §0 RE-MEASURED BY EXECUTION at `c2ce00f`. ⛔ EVERY ROW REPRODUCED.

Nothing was smoothed and nothing came out different. No detector was run, no corpus member staged,
nothing fetched. Every figure below is a read of a committed artifact, the manifest, or the git
object database.

| §0 row | expected | measured | verdict |
|---|---|---|---|
| HEAD / branch | `c2ce00f…`, `docs/merge-strategy-decision` | identical | ✅ |
| `git status --porcelain` | clean | carried **only** the create-story output (this story file untracked; `sprint-status.yaml` modified with `epic-17 backlog→in-progress`, `17-1 backlog→ready-for-dev`) — both AC6.1 members, landed by commit **O** | ✅ |
| §0.1 `PRECISION_GATE_THRESHOLD` | `Fraction(4, 5)` | `Fraction(4, 5)` | ✅ |
| §0.1 `verdict_eligible_population_floor` | 5 | 5 | ✅ |
| §0.1 `contributing_member_floor` / `sealed_member_floor` | 3 / 3 | 3 / 3 | ✅ |
| §0.1 `validation_floor_n` / `eligible_member_count` / `len(MANIFEST_FIELDS)` | 5 / 5 / 9 | 5 / 5 / 9 | ✅ |
| §0.1 `GATE_OUTCOMES` / `CONDITION_VERDICTS` | 3 / 4 | 3 / 4 | ✅ |
| §0.2 per-member `vacuous_test_heuristic` | 648 / 295 / 72 / 17 / 0 = **1,032** of 4,284 | identical | ✅ |
| §0.2 rule classes | `orphan_code` 1,675 · `hardcoded_secret` 1,330 · `vacuous_test_heuristic` 1,032 · `cross_partition` 231 · `traceability_not_establishable` 16 | identical | ✅ |
| §0.2 `silent-class-record.json` | `population_walked` 1,032, `population_skipped` 0, `V1.3` | identical | ✅ |
| §0.3 protocol change-log head | **V1.3**, 2026-08-16 | identical — parsed from the table, not read off prose | ✅ |
| §0.4 `sealed ∩ eligible` | **∅** | **∅** — `pre-seal` 5 (all eligible), `sealed` 6 / `open` 10 (all `eligible_for_n=False`) | ✅ ⛔ |
| §0.5 `class_by_corpus_member` | `{agent-smith: 22, minions: 14}`, `class_size` 36 | identical; `counts {UNADJUDICATED: 36, TP/FP/BORDERLINE: 0}`, `gates_anything False`, `promotes_nothing True` | ✅ ⛔ |
| §0.6 worktree record | 31 rows, 26 FP, 5 BORDERLINE, **0 TP** | identical | ✅ |
| §0.6 **pinned blob** `6c59115:…` | 31 rows, 26 FP, **0 TP**, `V1.3`, unit `finding`, `vacuous_test_ast` 31/31, by member `{minions 24, agent-smith 7}` | identical, and `6c59115` **is an ancestor of HEAD** | ✅ ⛔ |
| §0.7 detector pins | four `if TYPE_CHECKING:` pins at `orphan_code:310`, `secret_scan:633`, `tool_runner:459`, `vacuous_test:799`; `@runtime_checkable` absent; `-145`/`-146` present | identical | ✅ |
| §0.8 next free id | `-135` | highest **actually used** `PRECISION-001` id is `-134`; `-135` appears only in this story file | ✅ |

⛔ **AC7 was not triggered.** Every escalation condition was checked and none fired: `sealed ∩
ratified` is still empty, the two candidate distributions are still 2 members, and **26 still
reproduces from the pinned blob**. The exposure ceiling therefore did **not** have to differ from
26 (see Completion Note 6.2 for the ratification that is owed anyway).

#### Task 3.3 / 5.3 — EVERY GUARD DRIVEN RED AT ITS REAL SEAM, BY AN EXECUTED MUTATION

The mutation was applied to the **real module**, the guard run against it, and the module restored
byte-for-byte (verified by comparing bytes, not by re-writing from memory). `.argus/guard-fires.jsonl`
records RED observations automatically; **no fires ledger was hand-written**.

| guard | mutation applied to the real source | observed |
|---|---|---|
| `-135` | `contributing_members=contributing_member_floor(floor_n)` → `contributing_members=3` | **RED**, exit 1 — *"re-types a resolved floor"* |
| `-135` | `return PRECISION_GATE_THRESHOLD` → `return Fraction(4, 5)` | **RED**, exit 1 |
| `-135` | change-log head mutated to `V99.9` in the generated protocol text | `refuse_protocol_drift` **raised**, and raised again on a table with no rows |
| `-136` | `MAX_FALSE_ACCUSATION_EXPOSURE` 26 → 27 | **RED**, exit 1 |
| `-136` | pin re-pointed to `c2ce00f` | ⚠️ **stayed GREEN** — *and that is a true measurement, not a hole:* the record is byte-stable between `6c59115` and HEAD, so the count is 26 at both. Recorded rather than smoothed. Replaced with a genuinely discriminating pin below. |
| `-136` | pin re-pointed to **`e991a00b`** — the pre-adjudication blob (31 rows, all `UNADJUDICATED`, **0 FP**) | **RED**, exit 1. This is the mutation that proves `EXPOSURE_SOURCE_SHA` is load-bearing. |
| `-136` | in-guard: every `FP` row relabelled | count moved 26 → 0, as required |
| `-137` | `exposure_holds = false_accusation_count <= MAX_…` → `exposure_holds = True` | **RED**, exit 1 — the ceiling proved non-redundant |
| `-138` | resolution-floor loop emptied (i.e. ratio evaluated before the floors) | **RED**, exit 1 |
| `-141` | `import subprocess` injected | **RED**, exit 1 |
| `-141` | `from argus.detectors.vacuous_test import _ast_corroborated` injected | RED at **collection** (exit 4) — weaker evidence, so re-run with `import argus.detectors` |
| `-141` | `import argus.detectors` injected | **RED**, exit 1 — the guard's own assertion fired: *"imports ['argus.detectors']"* |
| `-141` | `Path("x").write_text(...)` injected into a real function body | **RED**, exit 1 |
| `-139` | at commit **A** (`HEAD == the pin`) | **RED** on precondition 3 by design — the ordering claim requires a **strict** ancestor. GREEN from commit **B** onward. |
| `-139` | sha replaced with a well-formed but **unresolvable** 40-hex | **RED** — *"does not resolve to a commit in this repository"* |
| `-139` | sha replaced with the **short** form `f906d04` | **RED** — *"must be recorded as a full 40-character lowercase hex sha"* |
| `-139` | sha set back to `None` at a `HEAD` past it | **RED** — *"PREREGISTRATION_COMMIT_SHA is still None"* |
| `-139` | `SUCCESSOR_OUTPUT_PATHS` emptied | **RED** on precondition 1 — *"an absence over nothing"* |
| `-139` | `SUCCESSOR_OUTPUT_PATHS` widened to `tests/corpus/_manifest.py`, a path that **does** carry commits | **RED** on the CLAIM itself — *"6 commit(s) reachable from the pre-registration sha touch a declared successor-output path"*. ⛔ This is the strongest non-vacuity evidence in the module: the assertion is watched **firing**, not only passing. |
| `-140` | `MAX_FALSE_ACCUSATION_EXPOSURE` 26 → 27 (a **raised** ceiling) | **RED** — *"STRENGTHENING ONLY: the ceiling may be lowered and never raised"* |
| `-140` | `POPULATION_ID` moved after the pin | **RED** — *"measuring a different population is not a strengthening"* |
| `-140` | `PROTOCOL_VERSION` moved `V1.3` → `V1.4` after the pin | **RED** — *"a pre-registration folded across an amendment is a re-interpretation of judgements nobody re-made"* |
| `-140` | in-guard: raised ceiling and lowered ratio driven through the direction predicate | both **rejected**; unchanged / lowered-ceiling / raised-ratio all **accepted** |

#### Task 4 — PROVE NOTHING MOVED

`git status --porcelain` after Tasks 1–3 listed **exactly** three untracked paths — the two new
modules and the new document — and nothing else. ⛔ **Absent from the diff, verified:** everything
under `argus/**`, `tests/corpus/**` and `validation-corpus/**`; `precision-validation-protocol.md`;
`deferred-work.md`; `epics.md`; `architecture.md`; `E-PRD/prd.md`. No dogfood artifact changed and
**no `code_identity` moved** — `argus/**` is byte-unchanged, so `tests/test_dogfood_artifact_currency.py`
is green without a regeneration commit and AC6.3 holds by construction.

**AC3.2, measured before and after by import:**

| constant | before | after |
|---|---|---|
| `eligible_member_count()` | 5 | **5** |
| `len(MANIFEST_FIELDS)` | 9 | **9** |
| `len(GATE_OUTCOMES)` | 3 | **3** |
| `len(CONDITION_VERDICTS)` | 4 | **4** |
| `validation_floor_n()` | 5 | **5** |

`-141` re-asserts all five on every run, so this is a guarded property rather than a recorded
observation.

#### Task 5.4 — AC6.4 GATES, EVERY EXIT CODE. ⛔ LOCAL (WINDOWS) — CI OWNS THE CROSS-PLATFORM CLAIM

Run with `PYTHONDONTWRITEBYTECODE=1` and every `__pycache__` cleared first.

| gate | result | exit |
|---|---|---|
| `python -m pytest` (post-commit-B, **nothing deselected**) | **1,738 passed** (268.84s) | **0** |
| `python -m pytest -q` (pre-commit-B, `-139` deselected — see below) | 1,737 passed, 1 deselected (259.72s) | **0** |
| `python -m pytest -q` with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` | all passed | **0** |
| `pytest --cov=argus --cov-report=term-missing --cov-fail-under=80` | **95.69%** (7,316 statements, 315 missed) | **0** |
| `mypy argus` | *Success: no issues found in 95 source files* | **0** |
| `bandit -r argus -f txt --severity-level medium` | no medium-or-above issue | **0** |
| the thirteen modules named by AC6.4, run by name | all passed | **0** |
| `tests/test_precision_preregistration.py` | **7 passed** (post-commit-B, `-139` included) | **0** |

⛔ The deselection above is `-139` only, and only for the runs taken **while `HEAD` was commit A
itself** — the guard requires the pre-registration to be a **strict** ancestor of `HEAD`, which it
is not at the moment it is created. It was run and is **green from commit B onward**; the
post-commit re-run is the row that carries the claim.

**NFR-M1 (AC6.5):** `scripts/precision_preregistration.py` **772** lines,
`tests/test_precision_preregistration.py` **1,037** lines — both under the 1,200 ceiling, with
headroom. Nothing was shaved and no `_EXEMPT_BY_DESIGN` entry was added.

### Completion Notes List

**What landed.** Four artifacts and nothing else: the criterion as pure code, the dated document,
seven guards, and this record with the two `sprint-status.yaml` transitions.

**Design decisions taken inside the story's authority, each with its rejected alternative:**

- **`DN-17-1-10` — `resolution_floors()` reaches `N` through `replay_harness.corpus_manifest_module()`,
  the ONE declared lazy edge.** *Rejected:* reading `registry_module().VALIDATION_SET_FLOOR_N`
  directly, which is a **second** path to a number `_manifest.validation_floor_n()` already
  answers — `AR7` permits one derivation per question, and `DN-3` is the same rule for the floor
  itself. *Also rejected:* resolving `N` at module scope, which would make the file unimportable
  in an environment without `tests/` (`DF-9-2-A`). The resolution happens inside the function.
- **`DN-17-1-11` — AC1.2's change-log-head check is split: a PURE parser in the module, the file
  read in the guard.** *Rejected:* opening `precision-validation-protocol.md` from the module.
  AC1.1 requires the module to be pure and AC1.2 permits *"the module **or its guard**"* to do the
  resolving; splitting it keeps both. `protocol_change_log_head()` / `refuse_protocol_drift()` take
  text and raise `ProtocolVersionDrift` — `gate_decision.py:336`'s shape — and `-135` performs the
  read. An unparseable table **refuses** rather than returning `PROTOCOL_VERSION`, which would have
  made the check `f(x) == f(x)`.
- **`DN-17-1-12` — `-140` reads the ratio floor AT THE PIN from the pinned `replay_harness` blob,
  not from the live import.** *Rejected:* comparing `precision_floor()` against `precision_floor()`,
  which is the `f(x) == f(x)` shape Epic 14 shipped four times. Because the criterion **resolves**
  its ratio floor, *"the ratio at the pin"* is whatever protocol §5's threshold was at that commit,
  and that is only knowable from the object database.
- **`DN-17-1-13` — the pinned blob is PARSED (`ast.literal_eval`), never executed.** *Rejected:*
  `exec`-ing a historical revision of the module to read its constants. Reading a blob to compare
  it is a much smaller act than running it.
- **`DN-17-1-14` — `NOT_MET` is this criterion's own name for its own negative.** `MET` and
  `UNEVALUABLE` are **resolved** from `CONDITION_VERDICTS` through a lookup that raises, so the
  module stops importing if §5's vocabulary changes underneath it. ⛔ No §5 terminal state was
  invented, added or renamed: `CONDITION_VERDICTS` is still 4 and `GATE_OUTCOMES` still 3, and
  `NOT_MET` is never written into a §5 condition or a gate record.
- **`SUCCESSOR_OUTPUT_PATHS` is successor-scoped**, exactly as `-75`'s reasoning demands:
  `…/validation-corpus/successor` and `_bmad-output/audit-reports/successor`. Both were verified to
  carry **zero** commits across all refs, so the guard's absence is real and was not widened to
  *"anything under `validation-corpus/`"* — which would have been false against artifacts that
  predate this story by weeks.
- **`evaluate()` refuses malformed input at construction** (negative counts; an adjudicated
  population larger than the verdict-eligible one; sealed contributors exceeding contributors).
  NFR-R1's stated exception: refusing a malformed pin is correct, and folding an impossible
  population would return a registered outcome for something that cannot exist.

**6.1 — HAND-OFF TO STORY 17.4 (AC4.4).** 17.4 **imports** two constants from
`scripts/precision_preregistration.py` and re-types neither (`DN-16-4-2` / `AI-E9-7`):

- `PREREGISTRATION_COMMIT_SHA` = `f906d04997b391bea4592aabc0343d1234b3b060` (full 40-hex, resolves,
  ancestor of `HEAD`, and touches **no** `SUCCESSOR_OUTPUT_PATHS` entry — proved by `-139`);
- `SUCCESSOR_OUTPUT_PATHS`.

⛔ **The ancestry guard over commits LATER than the pre-registration is Story 17.4's to write, not
this story's.** `-139` proves only the claim this story can prove.
⚠️ 17.4 also inherits a **stated precondition**: protocol §4's External adjudicator (`AI-E16-7`) is
**UNFILLED**. 17.1 adjudicates nothing and does not need it; 17.4 does. It is written into
`CONSEQUENCE_MET` and into §3.5 of the document rather than left to be discovered.

**6.2 — ⛔ RATIFICATION OWED TO THE ENGINEERING LEAD (XAgent007), AC7.** The exposure ceiling is a
**new absolute quantity** and setting one is an operator act of the same class as the 2026-08-17
rule. Per AC7 it was **landed with its derivation** rather than substituted by a preference, and it
is raised here for ratification:

- **value:** `MAX_FALSE_ACCUSATION_EXPOSURE` = **26**;
- **derivation:** the `FP` disposition count of the 31-row adjudication record at
  `6c59115b2aad1e6ab9c7dd3ebba011f7d37376dd` — the instrument's entire recorded false-accusation
  history, judged by a named human under V1.3, with **zero** TP ever recorded. Re-derived on every
  run by `-136`, and driven RED against a pin where the count differs;
- **rejected alternatives:** 1 (`floor(yield_floor × (1 − p))`) and 5 (`yield_floor`) — both
  shutdowns; **48** (`DF-16-7-B`) — cannot bite at any reachable population; a percentage — the
  ratio wearing a different hat; live resolution — the record grows and 17.4 appends to it;
- **⛔ it may only be LOWERED.** `-140` enforces `ceiling ≤ ceiling_at_pin` and
  `ratio ≥ ratio_at_pin` against the pinned blob, so a loosening is a red test.

**6.3 — OBSERVED BUT NOT FILED (`AI-E9-8`: recording is this story's job, filing is the operator's).**
The ledger was read before writing any of this and each observation below already has prior art in
it; **none is filed here and `deferred-work.md` is absent from this story's diff.**

1. **A pin whose blob has not changed cannot falsify a pin-provenance guard.** Re-pointing `-136`'s
   sha at `c2ce00f` left it green, because `adjudication-record.json` is byte-stable between
   `6c59115` and HEAD. The guard is sound — a discriminating pin (`e991a00b`) reddens it — but the
   general shape is *"a mutation that does not move the observable proves nothing"*, which is the
   `DF-8-5-B` / GUARD-ADEQUACY family. **Recorded, not filed.**
2. **`-139` is red at the exact commit it describes**, because the ordering claim needs a strict
   ancestor. That is correct behaviour and it is `-75`'s behaviour too, but it means the
   sha-dependent guards genuinely cannot live in the commit they name — the three-commit arc is a
   structural requirement, not a convention. Worth a line in an epic retrospective; **not a ledger
   entry.**
3. **`argus/precision/gate_seal.py` exports `SEALED_MEMBER_FLOOR_DERIVATION`**, not
   `SEAL_MEMBER_FLOOR_DERIVATION` as §2.7's shorthand suggested. A naming observation only; nothing
   was renamed and no `argus/**` byte moved.

**6.4 — ⛔ `DF-13-5-A` IS UNTOUCHED, and stays OPEN and UNSPENT.** Its branch (a) was not executed,
its branch (b) was not declared, no round was spent, no member was ratified and no third-party
source was fetched. Its 2026-08-24 trigger was **not evaluated** — that is Story 17.4's, by name.
`deferred-work.md` is **absent from this story's diff** (verified with `git status --porcelain`),
which is the cleanest possible answer to its byte invariants. ⛔ This story therefore claims **no
`DF-*` disposition change** of any kind, and every other open entry named in the story context —
`DF-INV-VACUOUS-A`/`-B`, `DF-16-7-A`/`-B`, `DF-14-1-A`, `DF-12-2-D`, `DF-12-3-A`,
`DF-AUD-DETECT-C`/`-D` — stays exactly as it was. Their re-homing notes remain Story 17.5's.

**What this story did NOT do, restated so it is not mistaken for done:** no successor predicate
exists; no protocol row was added and `precision-validation-protocol.md` is byte-unchanged; no §5
condition was created; the gate stays `BLOCKED` and `protocol_cleared` stays `False`; `consumed == 0`
was not reached; the document was **not** registered in `_STATUS_DOCUMENTS` (`DN-17-1-8` — `-22`
closes in both directions and registering it would turn that guard red); no `Evidence-partition:`
trailer was required or added, because the write set touches neither `DETECTOR_TUNING_PATHS` entry.

### File List

**New**

- `scripts/precision_preregistration.py`
- `_bmad-output/design-artifacts/ArgusAgent/successor-predicate-precision-preregistration.md`
- `tests/test_precision_preregistration.py`

**Modified**

- `_bmad-output/design-artifacts/ArgusAgent/stories/17-1-write-down-what-would-count-as-precision-before-the-number-exists.md` (this file)
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` (status transitions and `last_updated` only)

**Commit arc (AC6.2 — three commits, pure-ASCII messages)**

| commit | message | contents |
|---|---|---|
| **O** `72e630d` | `chore(17-1): open the pre-registration story` | this story file + `sprint-status.yaml` (`epic-17 → in-progress`, `17-1 ready-for-dev → in-progress`) |
| **A** `f906d04` | `feat(17-1): pre-register the successor-predicate precision criterion` | the criterion (with `PREREGISTRATION_COMMIT_SHA = None`), the document, and `-135`/`-136`/`-137`/`-138`/`-141` |
| **B** | `docs(17-1): record the pre-registration commit and the dev round` | the sha, `-139`/`-140`, this record, and `17-1 → review` |

⛔ Staged **by explicit path** on every commit; `git add -A` was never used — a peer session shares
this branch (§2.6).

## Change Log

| Date | Change | By |
|---|---|---|
| 2026-08-25 | Story contexted at HEAD `c2ce00f`; `backlog` → `ready-for-dev`. §0 measured by execution; three premises recorded that the epic's plan did not carry — empty `sealed ∩ ratified`, both candidate successors at 2 contributing members, and 26 FP / 0 TP across the instrument's whole adjudicated history. | Scrum Master (create-story, Opus 5) |
| 2026-08-25 | **DEV round 1.** §0 re-measured by execution before a line was written — **every row reproduced**, AC7 not triggered. Landed `scripts/precision_preregistration.py` (the criterion as pure code: population, protocol version checked against the change-log head, ratio floor and three resolution floors RESOLVED, `MAX_FALSE_ACCUSATION_EXPOSURE = 26` derived from a pinned blob, both consequence clauses, and a pure fold evaluating the floors before the ratio), the dated pre-registration document, and seven guards `TC-ArgusAgent-PRECISION-001-135`..`-141` — each driven RED at its real seam by an executed mutation. Three commits, pure-ASCII messages. Local (Windows) gates all exit 0: 1,737 passed, coverage 95.69%, `mypy` clean, `bandit` clean. Nothing ratified, fetched or spent; `argus/**` byte-unchanged; `deferred-work.md` untouched. `ready-for-dev` → `in-progress` → `review`. | Developer (dev-story, Opus 5) |
