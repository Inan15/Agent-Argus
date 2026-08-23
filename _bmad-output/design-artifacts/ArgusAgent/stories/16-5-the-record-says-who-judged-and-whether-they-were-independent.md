# Story 16.5: The record says who judged, and whether they were independent

Status: review

<!-- Contexted 2026-08-22 at HEAD `52143eb` by the create-story workflow (Opus 5). Every figure in
     §0 was READ OFF THE TREE, not copied from the epic. Where the epic and the tree disagree, §0
     says so and the tree wins.

     AMENDED 2026-08-23 by create-story (amendment mode) after the story-readiness validation
     returned FAIL. See `…-validation-2026-08-23.md`. SEVEN TARGETED EDITS, no re-contexting and
     no scope change: three BLOCKING (AC2.3 was unsatisfiable inside AC7.1's fence — §2.3, AC2.3,
     AC7.1/7.1a/7.2, Task 1, Task 4; AC4.3 contradicted AC5.3 — AC4.3, AC5.3, §0.7; the
     "nothing reads it" premise was FALSE — the framing, §0.1, §0.7) and four minor (§0.0 path
     root, Dependencies' registry indirection, the `epics.md:3199` cite, AC3.1's exclusion set).
     Every §0 figure the validation re-derived was CLEAN and is UNCHANGED. Status stays
     `ready-for-dev`; sprint-status value unchanged.

     AMENDED AGAIN 2026-08-23 by create-story (amendment mode) after the ROUND-2 validation
     returned CONCERNS. See `…-validation-2026-08-23-round-2.md`. SIX TARGETED EDITS, no
     re-contexting, no re-research, no scope change: (1) NEW `DN-16-5-7` — OPERATOR-AUTHORISED —
     corrects `DN-16-1-1`'s RATIONALE by measurement while its HOLDING STANDS, cross-referenced
     from the citation site and carved out of AC7.4; (2) AC4.3 limb 2 / AC5.3 — the mechanism was
     measurably WRONG: the population blocks on EXHAUSTIVENESS at `gate_decision.py:956`, ahead of
     the empty-denominator branch at `:977`, and the CLEARED guard cite is `:1022` not `:1021`;
     (3) §0.5 prose `640` -> `560`; (4) Task 4 / AC7.2 note the required re-order of the
     `adjudicators` derivation above `:811`; (5) §0.0 / Task 0 working-tree expectation now
     includes the validation reports; (6) Task 4's byte-identity list gains the three direct
     `precision_gate_status_for` callers.
     ROUND 2 CONFIRMED all three round-1 blockers genuinely resolved and re-derived every line
     projection EXACT — none of that was disturbed. No `DN-*` overturned; `DN-16-5-4` / `DN-16-5-5`
     untouched; `SECTION_5_CONDITIONS` still SEVEN; `precision_evaluable` still FOUR conjuncts.
     ⛔ NO `argus/`, `tests/` or `scripts/` file was touched — in particular
     `gate_breadth.py:366-368` was deliberately LEFT AS SHIPPED. Status stays `ready-for-dev`;
     sprint-status value unchanged. -->

## Story

As a **prospective adopter of Argus**,
I want **the gate decision record to state whether its adjudication was independent of the tool's
authors**,
so that **I can weigh the precision figure without having to reconstruct who was in the room.**

### What this story IS

It makes **one existing, already-computed, published-but-unguarded field legible**. `GateDecision`
has carried `adjudicators: tuple[str, ...]` since Story 13.3, `decide_gate` derives it from the live
rows of the committed adjudication record, and `to_payload()` publishes it under
`adjudication_record.adjudicators`. **No test in the repository asserts anything about it, and
nothing renders it beside the precision figure.**

⛔ **CORRECTED 2026-08-23 — this story does NOT rest on "nothing reads it", because that is FALSE.**
The earlier framing said so and the readiness validation measured it false. §5(4)
`_recorded_cleared_condition` **already** consumes the derived adjudicator set (§0.7, AC4.3). What
is true, and what this story is actually built on, is narrower and measured: the **field** is
write-only (declared `gate_decision.py:276`, published `:468`, never read), **zero** assertions
close over it anywhere in `tests/**` or `scripts/**` (§0.1), and **no** surface renders it beside
the precision figure. ⛔ **The premise is "unguarded and unattached", not "unread".** The scope is
unchanged by the correction. A reader who wants to
know whether the precision figure was judged by the people who wrote the tool must open a JSON
artifact, find a nested list of `"<who> (<role>)"` strings, and know that protocol §2 registers
three roles and that one of them is the one §2 says *"SHOULD be outside the implementing team"*.

This story turns that reconstruction into a **derived, published, guarded status** that travels
**with the precision figure**, on the same sentence, so the two cannot be quoted apart.

### What it is NOT

- ⛔ **NOT an eighth §5 condition.** `SECTION_5_CONDITIONS` stays at **SEVEN**, byte-unchanged.
- ⛔ **NOT a gate.** `GateDecision.precision_evaluable` keeps **exactly four** conjuncts. Nothing
  in this story can move a gate outcome, in either direction, for any population.
- ⛔ **NOT a claim of independence.** Today's answer is *"not independent"* and that is the correct
  output, not a failure of the story.
- ⛔ **NOT a role being filled.** Filling a role is a §6 R2-class operator act. This story fills
  none, requires none, and blocks on none.
- ⛔ **NOT a re-run of the gate.** No detector runs. No member is ratified. No disposition is
  written. `DF-13-5-A` stays **OPEN and UNSPENT**.

---

## §0 — PREMISES RE-MEASURED BY EXECUTION at HEAD `52143eb`

⛔ **Task 0 re-derives every row below before a line is written.** All four stories before this one
found a stated premise false by executing it. Budget for it.

### §0.0 The tree

Branch `epic-16/discharge-df-15-2-d`, HEAD **`52143eb`**, and the tree was **clean at that commit**
— create-story then wrote **this file and `sprint-status.yaml`** and committed neither, so those two
**plus this story's validation reports** (`…-validation-2026-08-23.md` and
`…-validation-2026-08-23-round-2.md`, both untracked) are the expected working-tree entries when you
open. ⛔ **Corrected 2026-08-23:** the earlier "only those two" wording pre-dated the validation
rounds and would have failed §0's own reproduce-check on your first command. Re-establish the baseline yourself: full suite with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`,
`mypy argus`, `bandit -r argus --severity-level medium`, and **both builders under `--check`**
(`scripts/build_gate_decision.py --check`, `scripts/build_adjudication_record.py --check`) —
record the collected count and each exit code. `--check` exit **1** means the committed artifact is
already stale **before** you touch anything, and that changes the plan.

⛔ **PATH ROOTS — read this BEFORE Task 0's first command, because this file mixes TWO of them.**
`argus/**`, `tests/**`, `scripts/**` and `pyproject.toml` are **repo-root-relative**. But
`validation-corpus/adjudication-record.json` and `validation-corpus/gate-decision-record.json` —
written in that short form throughout §0.1, AC5.5, AC6.1, AC7.1, AC7.2 and Task 0, and sitting in
the same lists as repo-root code paths — are **NOT at the repo root**. Both live under the artifact
root: **`_bmad-output/design-artifacts/ArgusAgent/validation-corpus/`**. So do `epics.md`,
`architecture.md`, `deferred-work.md`, `precision-validation-protocol.md` and this story file, all
under `_bmad-output/design-artifacts/ArgusAgent/`. ⛔ **Qualified ONCE here rather than in every
list** — a Task 0 command that takes the short form literally **ENOENTs on its first line**.
Resolve both artifacts through the builders' own path constants
(`scripts/build_gate_decision.py`, `scripts/build_adjudication_record.py`) rather than re-typing
either root anywhere.

### §0.1 The field this story is about, measured

| Fact | Measured value | Where |
|---|---|---|
| Live rows on the committed adjudication record | **31** | `validation-corpus/adjudication-record.json` |
| Dispositions | **26 FP · 5 BORDERLINE · 0 TP · 0 UNADJUDICATED** | same |
| Distinct `adjudicator` values across all 31 rows | **exactly one** — `"XAgent007 (Engineering Lead)"` | same |
| `protocol_version` | **V1.3**; `expert_hours` **`null`** | same |
| `adjudication_record.adjudicators` on the committed decision | `["XAgent007 (Engineering Lead)"]` | `validation-corpus/gate-decision-record.json` |
| Gate outcome | **`BLOCKED`** | same |
| `precision.evaluable` / `fold_evaluable` | **`false` / `false`** | same |
| `breadth_holds` / `seal_holds` / `yield_holds` | **`false` / `false` / `true`** | same |
| Assertions anywhere in `tests/**` or `scripts/**` over `adjudicators` | **ZERO** (`grep` over `--include=*.py`) | — |

⛔ **The last row is the story.** The field is published and **unguarded by any test**. A field no
guard closes over is a field that can go wrong without anything noticing — this project's own
`AI-E11-1` shape, applied to a disclosure instead of a guard.

⛔ **READ THAT ROW PRECISELY: it says NO ASSERTION, not NO READER.** Measured 2026-08-23, and the
distinction is load-bearing twice over. The `GateDecision.adjudicators` **field** is write-only
(declared `gate_decision.py:276`, published `:468`, never read). The **derived value** is not:
`decide_gate` hands it to §5(4) `_recorded_cleared_condition`, which **fails the condition on an
empty set** and **renders the names** on its MET path (`gate_decision.py:665`). ⛔ **Neither of
those travels with the precision figure** — which is exactly what §1.1 is about and exactly what
this story fixes. It is also the mechanical reason AC4.3's inertness sweep is scoped to the
non-empty members. See §0.7 and AC4.3.

**So the derived answer today is `NOT_INDEPENDENT`: 31 of 31 live human judgements were authored by
the Engineering Lead, who is also the tool's author.** That is the expected output of this story.

### §0.2 ⛔ THE EPIC TEXT IS STALE, AND IT IS STALE ON THIS STORY'S FIRST PREMISE

[epics.md](../epics.md) §Story 16.5 — the `### Story 16.5` heading is at **`epics.md:3191`**, and
the AC block's first **Given**, at **`epics.md:3199`**, reads: *"**Given** §2's QA Lead and External
adjudicator are both **unfilled**…"*. **That was true when the epic was written on 2026-08-20. It is
false now.** (Cite tightened 2026-08-23: `:3191` is the heading, not the sentence. The claim was
substantively right; by this story's own standard — read off the tree — the cite must be too.)

Commit **`1bb7088`** (2026-08-22, operator act by XAgent007) added a **fourth dated block under
V1.3** to protocol §2 filling the **QA Lead (second reviewer)** role with **Veer Pratap Singh**.
Verify it yourself at `precision-validation-protocol.md` §2 (the `👤 DATED BLOCK — 2026-08-22`) and
in the §2 holder table.

Three consequences, and the second is the one that will bite:

1. **No change-log row was taken.** The change-log head still returns **V1.3**;
   `TC-ArgusAgent-PRECISION-001-45` / `-63` are untouched. Do not add a `V1.4` row for this story
   either — see §2.4.
2. ⛔ **The QA Lead role is FILLED and has authored ZERO dispositions.** *Filled* and *judged* are
   now different facts about different roles, and this story is the first thing in the tree that
   has to publish a sentence about both without conflating them. See `DN-16-5-4`.
3. **The External adjudicator tie-break stays UNFILLED**, and §2's dated block says so explicitly,
   along with: *"Whether any given adjudication was independent is Story **16.5**'s question to
   record, not this block's to assert."* **That sentence is this story's charter and it is already
   committed** — the protocol is waiting for this story, not the other way round.

### §0.3 The extension seam, read line by line

`argus/precision/replay_harness.py::precision_gate_status_for` is the **one** status renderer
(AR7). It has **three** return branches and **the precision figure appears in all three**:

| Branch | Condition | Renders |
|---|---|---|
| unevaluable | `not evaluable` | `precision {unevaluable_reason}, so precision={ratio} is NOT a measurement; N=…` |
| provisional | `provisional` | `precision={ratio} over FINDINGS not repos; N=…` |
| cleared | otherwise | `precision={ratio} >= 4/5 over FINDINGS; N=…` |

⛔ **AC2 says "wherever it carries the precision figure". That is all three branches, not just the
one this repository currently reaches.** A story that wires the independence note into the
unevaluable branch alone would be correct today and silently wrong on the day the gate clears —
which is the one day the sentence matters most.

The function already has the exact extension shape you need, taken twice before: `population_label`
(13.1) and `unevaluable_reason` (13.3) are **optional keywords with defaults chosen so every
existing caller renders the bytes it always did** (NFR-P1 byte-stability of the precision surface).
Take that shape a third time.

### §0.4 The sibling-module precedent, unanimous across three stories

| Story | §5 arm | Module | Renderer | Guards |
|---|---|---|---|---|
| 16.1 | breadth | `argus/precision/gate_breadth.py` (436) | `effective_precision_gate_status` | `-82`..`-85` |
| 16.2 | seal | `argus/precision/gate_seal.py` (777) | `sealed_precision_gate_status` | `-87`..`-94` |
| 16.3 | yield | `argus/precision/gate_yield.py` (560) | `yielded_precision_gate_status` | `-95`..`-100` |

Each: a new module owning **the constants, the pure predicate and the published sentences**;
`gate_decision.py` owning **only** the dataclass field, the payload key and the dispatch;
`ConditionResult` built in `gate_decision.py` because it lives there and the import would otherwise
be circular (`DN-16-1-3`); **one import direction only**, `gate_decision` → sibling.

⛔ **Follow it. This story adds `argus/precision/gate_independence.py`.** But note the ONE way this
story is not like those three: **they each appended a §5 condition and this one must not.** See
§2.1.

### §0.5 Module headroom, measured with the ceiling guard's own `_physical_line_count` (`_CEILING = 1200`)

| Module | Lines | Headroom | Note |
|---|---|---|---|
| `tests/test_gate_seal.py` | **1,145** | **55** | ⛔ **`DF-16-3-A` OPEN. Trigger 1,180.** Put nothing here. |
| `tests/test_vacuous_density.py` | 1,159 | **41** | ⛔ `DF-15-2-E` **OPEN**, trigger 1,180. Untouched by this story. |
| `tests/corpus/_manifest.py` | 1,101 | **99** | Untouched by this story. Do not open it. |
| `argus/precision/gate_decision.py` | **1,084** | **116** | ⛔ **The one to watch — see below.** |
| `tests/test_vacuous_detector_index.py` | 1,065 | 135 | Untouched. |
| `argus/precision/adjudication.py` | 973 | 227 | ⛔ **NOT read-only — AMENDED 2026-08-23.** One forwarded keyword (§2.3, AC7.1a). |
| `tests/test_adjudication_record.py` | 932 | 268 | |
| `tests/test_instrument_disclosure.py` | 893 | 307 | |
| `tests/test_gate_decision.py` | 865 | 335 | |
| `tests/test_gate_yield.py` | 839 | 361 | |
| `argus/precision/replay_harness.py` | 825 | 375 | one optional keyword lands here |
| `argus/detectors/vacuous_test.py` | 796 | 404 | `DF-15-2-D` **CLOSED** by `4123931` |
| `argus/precision/gate_seal.py` | **777** | **423** | ⛔ one forwarded keyword (§2.3, AC7.1a) |
| `tests/test_gate_breadth.py` | 747 | 453 | |
| `argus/precision/gate_yield.py` | **560** | **640** | ⛔ one forwarded keyword (§2.3, AC7.1a) |
| `argus/verdict/negative_assurance.py` | 592 | 608 | ⛔ read-only — see `DN-16-5-2` |
| `tests/test_gate_ordering.py` | 477 | 723 | |
| `tests/test_gate_decision_artifact.py` | 451 | 749 | the artifact guard lands here |
| `argus/precision/gate_breadth.py` | **436** | **764** | ⛔ one forwarded keyword (§2.3, AC7.1a) |
| `scripts/build_gate_decision.py` | 435 | 765 | |
| `argus/precision/gate_conditions.py` | 234 | 966 | ⛔ **byte-unchanged** |

⛔ **`gate_decision.py` at 1,084 has 116 lines and NO ledger entry** (`DF-16-1-B` was discharged by
16.2's split). This module's comment density runs 25–50 lines per amendment block, and this story
adds a field, a payload key, a status-property branch and their reasoning. **Measure the projected
delta BEFORE writing** (Task 1). If it lands the module over **1,150**, perform a cohesion split
**FIRST, alone, in its own commit**, on the `gate_conditions`/`gate_evidence` precedent — and if it
lands between 1,100 and 1,150, **file a new `DF-16-5-*` entry naming the trigger**. Every one of the
last four stories was handed an unfiled split-first trigger at the least convenient moment.
`DF-16-3-A` exists precisely to stop a fifth. **Check the ceiling before you write, not after.**

⛔ **AMENDED 2026-08-23 — the four §2.3 FORWARDERS are now in this table and in Task 1's
projection.** The earlier version of this story omitted them, so the module the dev would actually
have had to edit to satisfy AC2.3 was outside the headroom projection entirely. Stated rather than
discovered: at 973 / 777 / 560 / 436 lines against a 1,200 ceiling, and a permitted delta of **one
keyword, one forwarded argument and one docstring line each** (AC7.1a), **none of the four can
reach 1,100 — let alone the 1,150 split-first trigger or the ceiling.** So the amendment adds
**no** new NFR-M1 trigger, and `gate_decision.py` at 1,084 remains **the only one to watch**.
⛔ **Re-measure and confirm this at Task 1 anyway.** If any of the four contradicts it, that is
§0's next false premise and it is **reported (AC7.4), not absorbed**.

**New guards land in a NEW module, `tests/test_gate_independence.py`.** Not a preference: it is what
keeps `DF-16-3-A`'s 55 lines from being spent by accident.

### §0.6 Next free verification ids

`TC-ArgusAgent-PRECISION-001-104` is the highest in use → **start at `-105`**.
`TC-ArgusAgent-DOCS-001-79` is the highest in use → **start at `-80`** if a docs-area guard is
needed. Re-derive both by `grep` before allocating; do not trust this line.

### §0.7 What is already true and must NOT be re-done

- §5 carries **seven** conditions, all landed, all guarded, all driven to both outcomes.
- `PROTOCOL_ADJUDICATOR_ROLES` is a closed **three**-member tuple, cross-checked against §2's own
  table **in both directions** by `TC-ArgusAgent-PRECISION-001-40`. ⛔ **Import it; never re-type
  the role names.**
- `adjudicator_role()` already parses `"<who> (<role>)"` and **raises `UnregisteredAdjudicator`** on
  a malformed id or an unregistered role. ⛔ **Call it; author no second parser and no second
  regex.**
- `AdjudicationRow.__post_init__` already refuses an `UNADJUDICATED` row that carries an
  adjudicator, and `record.live_rows()` already excludes superseded rows. ⛔ **Reuse both.**
- `decide_gate` already derives `adjudicators` from the live rows and already computes the
  `unattributed` tuple. ⛔ **Read what is there; do not recount the record.**
- ⛔ **§5(4) ALREADY READS THE ADJUDICATOR SET — ADDED 2026-08-23, and it is the fact the original
  framing missed.** `_recorded_cleared_condition` (`gate_decision.py:626-690`) takes `adjudicators`
  as a parameter and (i) appends a problem — *"NO adjudicator is named on any live row — an
  unattributed adjudication run is not a recorded one (non-vacuity floor, `AI-E11-1`)"* — when the
  set is **empty**, which drives §5(4) to `FAILED`; and (ii) on the `MET` path renders the names
  into a published sentence at `:665`: `f"recorded cleared: run attributed to {', '.join(...)}
  over …"`. ⛔ **Do NOT re-implement that check, do NOT remove or weaken it, and do NOT route this
  story's status through it.** It is pre-existing, it is correct, and it is entirely separate from
  this story's disclosure — the coupling it creates is a **found fact**, not something 16.5 adds.
  It is the mechanical reason AC4.3's sweep is scoped to the **non-empty** vocabulary members, and
  the reason AC3.1's walk needs the exclusion set it now names.

---

## §1 — WHY THIS STORY EXISTS

### §1.1 The failure mode, stated concretely

The committed gate record publishes a precision figure and, in a different JSON object thirty lines
away, a one-element list naming the person who judged every finding that figure rests on. Those two
facts are **separable by copy-and-paste**. The moment the gate clears, the sentence a reader will
actually quote is the `gate_status` string — *"cleared … precision=4/5 >= 4/5 …"* — and that
sentence today says **nothing** about who judged. An adopter reading it has no way to learn, from
the thing they were handed, that the adjudication was performed entirely by the tool's author.

That is not hypothetical: it is the exact shape §2's 2026-08-22 block declines to assert and hands
to this story, and it is the same class as `DF-9-2-B` — **a true statement whose subject a reader
will get wrong** — on the one surface this project's externalization claim rests on.

⛔ **One qualification, measured 2026-08-23, so the argument is not overstated.** §5(4) **does**
publish an attributed sentence naming the adjudicators (`gate_decision.py:665`) — so it is not
true that the repository never says who judged. But that sentence exists **only on §5(4)'s MET
path**, which the live record does not reach (`adjudication_run_recorded_cleared: false`), and it
is a **condition's `measured` string**, not the `gate_status` sentence a reader quotes. The
separability argument is therefore **narrowed, not destroyed**: what no surface does today is put
the independence answer **on the same sentence as the precision figure**. That, precisely, is what
this story builds.

### §1.2 Why a disclosure and not a condition

Because the honest answer today is *"no"*, and a condition would convert an honest *no* into a
**blocked gate that only an operator act can unblock** — i.e. this story would quietly hold the
externalization gate hostage to a hiring decision. §2 says the external sign-off *"SHOULD be outside
the implementing team"*; **SHOULD is not MUST**, and promoting it would be a threshold change made
by an implementation story. The epic says it in terms: *"this story does not claim independence,
does not fill a role, and does not gate on one being filled. It makes the current state legible,
whatever it is."*

### §1.3 What this story does NOT fix, named so it is not mistaken for fixed

- It does not make the adjudication independent. It says that it is not.
- It does not fill the External adjudicator role, and it does not resolve `DF-13-5-A`.
- It does not change what §4's ladder does when it reaches an unfilled role: a story that gets
  there still **STOPS and reports which rows and why** (Story 16.7 inherits this unchanged).
- It does not touch the FR34 `InstrumentStatus` vocabulary. See `DN-16-5-2`.

---

## §2 — THE COUPLINGS THAT WILL BITE

### §2.1 ⛔ THE CONDITION-SET TRAP — the single most consequential thing in this story

The three stories immediately before this one **each appended a §5 condition**, and the dev agent
will pattern-match onto them. **This story must not.**

`GateDecision.__post_init__` raises unless `tuple(c.condition_id for c in conditions)` equals
`SECTION_5_CONDITIONS` **exactly and in order**. Appending a condition here would:

- make a role nobody has filled able to force `UNEVALUABLE` — i.e. **gate on it**, which AC4
  forbids in terms;
- change the committed record's condition list, re-arming every guard that reads the count;
- and be an amendment to protocol §5, which requires an operator act this story does not have.

⛔ **`argus/precision/gate_conditions.py` is BYTE-UNCHANGED by this story.** So is every constant
below — **a guard asserts each one by value**, and each is listed with **the module it actually
lives in**, because two of them are not where a reader would guess:

| Constant | Value | Module |
|---|---|---|
| `SECTION_5_CONDITIONS` | **7** | `argus/precision/gate_conditions.py` |
| `CONDITION_VERDICTS` | **4** | `argus/precision/gate_conditions.py` |
| `GATE_OUTCOMES` | **3** | `argus/precision/gate_decision.py` |
| `PROTOCOL_ADJUDICATOR_ROLES` | **3** | `argus/precision/adjudication.py` |
| `DISPOSITIONS` | **4** | `argus/precision/adjudication.py` |
| `PRECISION_GATE_THRESHOLD` | **4/5** | `argus/precision/replay_harness.py` |
| `MANIFEST_FIELDS` | **9** | `tests/corpus/_manifest.py` |
| `VALIDATION_SET_FLOOR_N` | **5** | ⛔ **`tests/cartridges/_registry.py`** — *not* `_manifest.py`, where the corpus lives and where a reader looks first (`DN-3`: **one** floor, resolved from the cartridge registry and reused by the corpus, never forked) |

### §2.2 ⛔ `precision_evaluable` keeps exactly FOUR conjuncts

```
fold.evaluable AND (breadth is None or breadth.holds)
               AND (seal is None or seal.holds)
               AND (yield_ is None or yield_.holds)
```

Adding a fifth conjunct is the same violation as §2.1 through a different door, and it is a
one-line edit a dev could make while "being consistent". ⛔ **The independence arm is NEVER a
conjunct of `precision_evaluable`, and never a branch of `_precision_condition`.** A guard drives
this: for a population that is otherwise `CLEARED`, flipping the independence status through **all**
its members must leave outcome, every condition verdict and `precision_evaluable` **byte-identical**.

### §2.3 The status string is rendered from THREE arm modules, and the property picks ONE

`GateDecision.precision_gate_status` returns exactly one of: `fold.gate_status`,
`effective_precision_gate_status(...)`, `sealed_precision_gate_status(...)`,
`yielded_precision_gate_status(...)`. **The independence note must ride on whichever one is
returned**, or the note disappears exactly when breadth/seal/yield changes the answer — which is
the live state today (`breadth_holds = false`).

⛔ **MEASURED 2026-08-23 — AMENDED. NONE OF THOSE FOUR RENDERS IN `gate_decision.py`.** The
original story asked for the note on all four while fencing every module that can carry it, and
that was a **closed box**: a dev reaching Task 4 would have found every route shut and either
escalated or taken a forbidden one. Each of the four is a `precision_gate_status_for` call made
from inside another module:

| Renderer the property can return | Where the `precision_gate_status_for` call ACTUALLY is |
|---|---|
| `fold.gate_status` | `argus/precision/adjudication.py:963`, inside `fold_adjudicated_precision` — computed **once** and stored as a plain `str` field (`adjudication.py:829`) |
| `effective_precision_gate_status` | `argus/precision/gate_breadth.py:381` |
| `sealed_precision_gate_status` | `argus/precision/gate_seal.py:698` |
| `yielded_precision_gate_status` | `argus/precision/gate_yield.py:493` |

⛔ **And all three arm renderers SHORT-CIRCUIT** — `if fold.evaluable == (fold.evaluable and
X.holds): return fold.gate_status` — so on the inert path they hand back the fold's
**precomputed** string. **A keyword added to `precision_gate_status_for` alone (AC2.1) reaches
NONE of the four.** This is not academic: today `breadth is not None` and `breadth_holds = false`,
so the **live** path returns `effective_precision_gate_status`.

**So AC2.3 requires those four modules to move, and this story now BUDGETS for it (AC7.1a, AC7.2)**
rather than fencing them and leaving the dev to discover the contradiction. The budget is **ONE
FORWARDED KEYWORD, DEFAULT BYTE-IDENTICAL** — the §0.3 NFR-P1 shape, one level out:

1. `fold_adjudicated_precision` gains **one** optional note keyword and forwards it to its
   `precision_gate_status_for` call. Its **only** production caller is `decide_gate`
   (`gate_decision.py:811`) — verified repo-wide — so `decide_gate` derives the note and passes it
   down. ⛔ **`adjudication.py` does NOT import `gate_independence`**; it forwards an **opaque
   optional string**, so `DN-16-5-1`'s one-way import direction is untouched.
2. Each arm module gains **the same one** optional keyword and forwards it on its **re-render**
   path. Its **short-circuit path needs no edit**: once the fold's own `gate_status` carries the
   note, `return fold.gate_status` carries it too. This is why the budget is one keyword and not a
   rewrite.
3. Every **existing** caller passes nothing and renders **byte-identical** bytes —
   `tests/test_adjudication_record.py`, `tests/test_gate_breadth.py`, `tests/test_gate_decision.py`,
   `tests/test_gate_decision_artifact.py` and `scripts/build_gate_decision.py` all call the fold
   builder and are **NOT edited**.

⛔ **This is a FORWARDING budget, not a licence.** No arm module derives, parses or words the note;
no arm module gains a second parameter; every sentence stays owned by `gate_independence.py`
(AC1.1). **Post-processing the returned string remains FORBIDDEN** — a second renderer that edits
the first's output is AR7's forked mechanism wearing a helper's hat, and AC3.1's guard is written
to catch it. ⛔ **`DN-16-5-5` is UNCHANGED and still binding**: forwarding a keyword through the
call chain is the opposite of string surgery on another function's output, not an exception to it.

### §2.4 The protocol: a dated §2 block under V1.3, and NO `V1.4` row

`GateDecision.__post_init__` **and** `decide_gate` both raise when
`record.protocol_version != protocol_change_log_head`. The committed record carries **31 human
judgements made under V1.3**. ⛔ **Adding a `V1.4` change-log row would re-stamp all 31 and turn
`TC-ArgusAgent-PRECISION-001-45` / `-63` red** — the standing operator decision of 2026-08-20,
re-applied 2026-08-22 by `1bb7088`, is unchanged: **amend by dated block, never by version row.**

This story's protocol edit is a **dated block under §2** recording that independence is now DERIVED
AND PUBLISHED, and that it is a **disclosure and not a condition**. It edits **no existing byte** of
§2, §3, §4 or §5 — strike-never-erase (§3.4).

### §2.5 Artifact currency: the order is not negotiable

Any `argus/**` delta re-arms the published-figure and dogfood-LOC currency guards
(`TC-ArgusAgent-DOCS-001-54`, `tests/test_dogfood_artifact_currency.py`). The order 16.2 and 16.3
both used, and it is the one that works:

**commit `argus/` first → run `python scripts/regenerate_dogfood_artifacts.py` → commit the
regenerated artifacts separately.** The script refuses on a dirty `argus/` tree by design.
Regenerating an artifact executes **no** detector over a bench member.

Separately: `scripts/build_gate_decision.py --check` goes **exit 1 (STALE)** the moment the payload
grows a key. ⛔ **`gate-decision-record.json` must be REGENERATED by the builder** — never
hand-edited — and its regeneration is a distinct commit from the `argus/` change.

### §2.6 ⛔ The dogfood surface reads no adjudication record, and must stay byte-identical

`argus/dogfood/proof_run.py::derive_gate_status` calls `precision_gate_status_for` with
`precision=None` and **no record at all**. There is no adjudication to describe there, and inventing
a sentence would publish a claim about a judgement that never happened.

⛔ **That call site is byte-unchanged and its rendered output is byte-identical after this story**,
asserted. Same for `compute_precision`'s cartridge fold: the cartridge corpus has golden keys, not
adjudicators. **The independence note attaches only where the status is rendered from an
adjudication record.** That is the scope decision, and it is `DN-16-5-6`.

### §2.7 The published sentence names a HUMAN. Check it against NFR-S1's guard, not against intent

`TC-ArgusAgent-PRECISION-001-61` scans the committed artifact text and fails on a **backslash**
(a Windows path leak) and on source-byte shapes. The independence sentence will contain
`"XAgent007 (Engineering Lead)"` and, once §2's other roles judge, other personal names. Names are
already published today under `adjudication_record.adjudicators`, so this is not new exposure — but
⛔ **run `-61` against the regenerated artifact and confirm it is green**, and do not interpolate
any path in a form that could carry a host separator.

### §2.8 Guard vacuity — this project's signature defect

This project shipped **4 of 35 unreal guards in Epic 14**, and 16.3's own mutation run caught one of
its own. The **GUARD-ADEQUACY CLAUSE** (`architecture.md` §Enforcement) applies in all three parts,
discharged **in each guard's own docstring**: (i) name the **observable**; (ii) demonstrate the
defect **moves** it — RED **at the real seam**, not against a reconstruction; (iii) at least one
adversarial variant **generated** from the registry/table/record the guard closes over, with its
count.

⛔ **Run every mutation with `PYTHONDONTWRITEBYTECODE=1` and a cleared `__pycache__`.** 16.2 recorded
a false RED from a stale cache and had to re-run everything. Restore the tree after each mutation
and confirm `git status --porcelain` is empty.

⛔ **The lockstep trap has fired three times.** 16.1, 16.2 and 16.3 each built a fixture in which two
terms moved together, so the guard tested neither. Here the trap is specific and named: **a
population whose adjudicator set changes is usually also a population whose size or member spread
changes.** Generate populations that vary **ONLY the adjudicator ids**, with breadth, seal, yield
and the TP/FP counts **pinned**, so the independence status is the only term that can move the
answer.

### §2.9 A corpus member's working tree is never mutated, and no detector runs

No `checkout`, no `stash`, no `clean`, no `reset`, no `worktree` — on any ratified or candidate
repository, ever. **This story runs no detector over any member, writes no disposition, and
regenerates no adjudication record.** `adjudication-record.json` is **read-only input**.

---

## Acceptance Criteria

### AC1 — THE INDEPENDENCE STATUS IS DERIVED FROM THE RECORD, NEVER TYPED

**1.1** A new module `argus/precision/gate_independence.py` owns the constants, the pure predicate
and every sentence this story publishes. It is **PURE (AR8)**: no I/O, no clock, no network, no
manifest resolution, no module-level repository-only path (`DF-9-2-A`). Import direction is **one
way only**: `gate_decision` → `gate_independence`.

**1.2** A **CLOSED** status vocabulary, declared as a `dict[str, str]` of member → registered
meaning, with a lookup function that **RAISES a typed `ValueError` subclass** on an unregistered
member (`DF-10-4-E`, `AR10`) — the `GATE_OUTCOMES` / `DISPOSITIONS` house shape. The members and
their derivation are **recorded with their reasoning in the module docstring**, never merely typed.
The recommended set, which the dev may refine but must justify in writing if it does:

| Member | Predicate over the live human dispositions |
|---|---|
| `NOT_ESTABLISHED` | **no** live human disposition exists — nothing was judged, so independence is *unobservable*, not *absent* (`AI-E11-1`) |
| `NOT_INDEPENDENT` | every live human disposition is authored by the **Engineering Lead** alone |
| `SECOND_REVIEWER_INTERNAL` | ≥1 by the **QA Lead**, none by the **External adjudicator** |
| `EXTERNAL_ADJUDICATOR_PARTICIPATED` | ≥1 by the **External adjudicator** |

⛔ `NOT_ESTABLISHED` and `NOT_INDEPENDENT` are **not synonyms** and must not collapse — the
distinction is the same one `BLOCKED` vs `NOT_CLEARED` already makes, one level in.

**1.3** The status is **DERIVED** from the `"<who> (<role>)"` ids on the **live rows** of the
committed adjudication record — reached through the `adjudicators` tuple `decide_gate` **already**
computes — and parsed through the **existing** `adjudicator_role()`. ⛔ **No second parser, no
second regex, no second role list, and never from protocol §2's prose holder table** (`DN-16-5-3`).

**1.4** The assessment carries **which roles judged and by whom**, derived: the sorted role set
present on the record, the sorted adjudicator ids, and the registered roles that are **absent**
from it — each read from `PROTOCOL_ADJUDICATOR_ROLES`, never re-typed.

**1.5** ⛔ **The published sentence distinguishes *a role that did not judge this population* from
*a role §2 has not filled*, in its own words.** As of 2026-08-22 the QA Lead **is filled**
(Veer Pratap Singh, `1bb7088`) and has authored **zero** dispositions; a sentence reading
"QA Lead: absent" would be read as *unfilled* and would be false. The status is a claim about
**the adjudication that was performed**, never about the roster (`DN-16-5-4`).

**1.6** Verified over the **live committed record**: the derived status is **`NOT_INDEPENDENT`**,
from 31 of 31 live rows authored by `"XAgent007 (Engineering Lead)"`. Recorded in the Dev Agent
Record with the count re-derived by execution.

### AC2 — THE STATUS AND THE PRECISION FIGURE CANNOT BE SEPARATED

**2.1** `precision_gate_status_for` gains **exactly one** optional keyword (an independence note),
defaulting so that **every existing caller renders byte-identical bytes** (NFR-P1) — the
`population_label` / `unevaluable_reason` shape taken a third time.

**2.2** ⛔ The note is rendered in **all three** branches — unevaluable, provisional and cleared —
because the precision figure appears in all three (§0.3). A guard asserts this **branch by branch**,
including the `cleared` branch no production call site currently reaches.

**2.3** `GateDecision.precision_gate_status` carries the note through **every** renderer its branch
set can return: `fold.gate_status`, `effective_precision_gate_status`, `sealed_precision_gate_status`
and `yielded_precision_gate_status` — **including the live path, which today is
`effective_precision_gate_status`** (`breadth_holds = false`).

⛔ **NONE of the four renders in `gate_decision.py`** (§2.3, measured 2026-08-23). Each is a
`precision_gate_status_for` call inside `adjudication.py:963` / `gate_breadth.py:381` /
`gate_seal.py:698` / `gate_yield.py:493`, and the three arm renderers short-circuit on
`return fold.gate_status`. **Those four modules therefore each gain ONE forwarded optional keyword
and nothing else**, under the **AC7.1a** budget — they are on AC7.2's change list, **not** AC7.1's
fence. ⛔ **Post-processing a returned string remains forbidden** (§2.3, `DN-16-5-5`), and **no arm
module derives or words the note** — each forwards an opaque string. A guard asserts the note
survives on **each of the four branches**, selected by construction, not by whichever branch the
committed record happens to reach.

**2.4** A guard asserts the two **cannot be separated**: driven RED by a mutation that renders the
precision figure without the note, and RED by one that renders the note without the figure, at the
**real seam** — not against a reconstruction.

**2.5** The independence status also appears as its **own structured block** on the committed
payload (a `to_payload()` mapping under a new top-level key, the `breadth` / `seal` / `yield`
precedent), so a machine reader never has to parse the sentence.

### AC3 — IT EXTENDS FR34's MECHANISM AND FORKS NOTHING

**3.1** `precision_gate_status_for` remains the **only** status renderer in the repository. A guard
walks the tree and fails on a second function that renders a gate-status sentence (AR7).

⛔ **THE WALK NAMES ITS EXCLUSION SET — ADDED 2026-08-23.** Shipped code renders several sentences
*about the gate* that are **not gate-status sentences**, so a walk that does not distinguish them
will either **red on master** or be written loose enough to be **vacuous** — and a vacuous AR7
guard is worse than none. **Definition, and it is the guard predicate: a gate-status sentence is
one carrying the `precision=` surface** — the `precision={ratio}` / `N=` shape
`precision_gate_status_for` emits in **all three** of its branches (§0.3). Explicitly **OUT** of
scope, and each **asserted to still exist** so the exclusion cannot silently swallow a real fork:

- `ConditionResult.measured` on any of the **seven** §5 conditions — including §5(4) attributed
  sentence at `gate_decision.py:665`, which names the adjudicators and carries **no precision
  figure** (§0.7);
- `breadth_blocked_reason` / `seal_blocked_reason` / `yield_blocked_reason`
  (`gate_decision.py:994` / `:1005` / `:1020`), which render **outcome reasons**, not status;
- this story own independence **note renderer** in `gate_independence.py`, which renders a clause
  **for** `precision_gate_status_for` to place, never a status sentence of its own.

⛔ The guard must be driven **RED by a second function emitting the `precision=` surface** — that
mutation, at the real seam and not against a reconstruction, is what discharges GUARD-ADEQUACY
(ii) here.

**3.2** ⛔ **`argus/verdict/negative_assurance.py` is BYTE-UNCHANGED.** `InstrumentStatus` stays a
**closed two-member** vocabulary, `INSTRUMENT_STATUS` stays `NOT_INDEPENDENTLY_VALIDATED`, and both
disclosure texts and both short forms are untouched — asserted. That vocabulary bounds **the
instrument, per tool VERSION**; this story's status bounds **one adjudication run**. Merging them
would repeat, exactly, the run-grade/instrument-status confusion the enum's own docstring warns
against (`DN-16-5-2`).

**3.3** The FR34 surfaces (`README.md`, `CHANGELOG.md`, `pyproject.toml`, `action.yml`, the MCP tool
description, the command assets, the report renderer) render **byte-identically** after this story.
`tests/test_instrument_disclosure.py` and `tests/test_instrument_disclosure_surfaces.py` pass
**unedited**.

**3.4** ⛔ `argus/dogfood/proof_run.py::derive_gate_status` and `compute_precision`'s cartridge fold
are **byte-unchanged and render byte-identical output** — neither reads an adjudication record
(§2.6, `DN-16-5-6`). Asserted by comparing rendered strings, not by reading the diff.

### AC4 — NOTHING IS GATED, AND THAT IS PROVEN BY EXECUTION

**4.1** `SECTION_5_CONDITIONS` stays at **SEVEN**, in order, byte-unchanged;
`argus/precision/gate_conditions.py` is byte-unchanged.

**4.2** `GateDecision.precision_evaluable` keeps **exactly four** conjuncts. `_precision_condition`
gains **no** branch.

**4.3** ⛔ **The inertness proof, driven rather than argued:** over a population constructed to be
otherwise `CLEARED`, and again over the live `BLOCKED` population, flipping the independence status
through **every member a NON-EMPTY adjudicator set can produce** — `NOT_INDEPENDENT`,
`SECOND_REVIEWER_INTERNAL`, `EXTERNAL_ADJUDICATOR_PARTICIPATED` — leaves `outcome`,
`outcome_reason`, all seven condition verdicts, `precision_evaluable` and
`precision.meets_threshold` **byte-identical**. Both directions.

⛔ **`NOT_ESTABLISHED` IS EXCLUDED FROM THIS SWEEP, AND THE REASON IS A FOUND FACT — SCOPED
2026-08-23.** The unscoped version of this AC was **unsatisfiable**, and it contradicted AC5.3.
Measured: §5(4) `_recorded_cleared_condition` (`gate_decision.py:626-690`) **already** takes
`adjudicators` and **already** fails on an empty set (§0.7), and the `CLEARED` branch requires
`all(condition.verdict == "MET" ...)` (`gate_decision.py:1022`). Reaching `NOT_ESTABLISHED` means
an empty adjudicator set (AC1.2), which:

1. drives §5(4) `MET -> FAILED` and therefore `outcome` `CLEARED -> NOT_CLEARED`; and
2. **before even that — and this limb was CORRECTED 2026-08-23, so write THIS mechanism into the
   guard docstring, not the one the earlier draft named.** An empty adjudicator set is only
   **constructible** when every live row is `UNADJUDICATED`: `AdjudicationRow.__post_init__`
   (`argus/precision/adjudication.py:376-377`) calls `adjudicator_role(self.adjudicator or "")` for
   every disposition in `HUMAN_DISPOSITIONS = ("TP", "FP", "BORDERLINE")` and **raises** on an empty
   or unregistered id, so a human-judged row **cannot exist without a registered adjudicator**. An
   all-`UNADJUDICATED` record is **NON-EXHAUSTIVE**, so the dispatch **BLOCKS on exhaustiveness** at
   `elif not isinstance(fold.exhaustiveness, Exhaustive)` (`gate_decision.py:956`) — which
   **PRECEDES** the empty-denominator branch at `:977` **and** §5(4). ⛔ **The `outcome_reason` and
   closure path you will observe are therefore the EXHAUSTIVENESS ones, not the empty-denominator
   ones.** *(The earlier draft named `:977`; measured, `:956` fires first and `:977` is never
   reached on this population. A guard docstring asserting the `:977` mechanism would state a
   mechanism the code does not exhibit — the `DF-9-2-B` false-subject class this story spends §2.8
   warning about, written by FOLLOWING the AC.)*

⛔ **That coupling PRE-DATES this story; 16.5 neither adds it, removes it, nor strengthens it,
and must NOT "fix" it** — it is protocol §5's non-vacuity floor doing its job. ⛔ **A dev who takes
the unscoped sweep literally builds a fixture that CANNOT go green, and the likeliest resolution
under time pressure is to weaken the guard until it passes — the exact vacuity failure §2.8 spends a
page warning about, reached by FOLLOWING the ACs rather than by ignoring them.** State this
coupling explicitly **in the guard docstring** as a found, pre-existing fact; do not rediscover it
at Task 5. AC5.3 still reaches `NOT_ESTABLISHED` — over a population that is BLOCKED for that
independent, pre-existing reason. **The substance of this AC is unchanged: nothing this story adds
can move a gate outcome.**

**4.4** `GATE_OUTCOMES` (3), `CONDITION_VERDICTS` (4), `PROTOCOL_ADJUDICATOR_ROLES` (3),
`DISPOSITIONS` (4), `PRECISION_GATE_THRESHOLD` (4/5), `VALIDATION_SET_FLOOR_N` (5) and
`MANIFEST_FIELDS` (9) are all byte-unchanged — asserted, in one guard, by value.

**4.5** No role is filled, no disposition is written, no member is ratified, no detector is run, and
`adjudication-record.json` is **byte-unchanged**. `DF-13-5-A` stays **OPEN and UNSPENT**.

### AC5 — GUARDS THAT CANNOT BE VACUOUS

**5.1** New guards land in **`tests/test_gate_independence.py`** (new), from
`TC-ArgusAgent-PRECISION-001-105`. ⛔ **Nothing lands in `tests/test_gate_seal.py`** (`DF-16-3-A`,
55 lines).

**5.2** Populations are **GENERATED** — one per adjudicator configuration — with breadth, seal,
yield and the TP/FP counts **pinned** so the adjudicator set is the only term that can move the
answer (§2.8). Guards assert **where the status flips**, not merely that it has more than one value.

**5.3** Every member of the vocabulary is **reached by a generated population**, and the
unregistered-member lookup is driven to its **raise**. Both directions (`AI-E11-1`: a member nobody
constructs is itself a finding).

⛔ **`NOT_ESTABLISHED` is reached over a population that is necessarily `BLOCKED`** — an empty
adjudicator set is only constructible when every live row is `UNADJUDICATED`
(`adjudication.py:376-377` refuses a human disposition without a registered adjudicator), which makes
the record **non-exhaustive**, so the dispatch blocks at `gate_decision.py:956` on **exhaustiveness**
— **ahead of** both the empty-denominator branch (`:977`) and §5(4). All **pre-existing** (AC4.3,
§0.7). ⛔ **Corrected 2026-08-23: expect the EXHAUSTIVENESS `outcome_reason` and closure path on this
fixture.** ⛔ **Assert the derived STATUS there, not gate inertness** — gate inertness for that member is
AC4.3's excluded case, and asserting it here would red for a reason that has nothing to do with
this story. ⛔ **And assert on that same population that `NOT_ESTABLISHED` is NOT
`NOT_INDEPENDENT`** (AC1.2): *nothing was judged* and *the author judged everything* must not
collapse.

**5.4** Each guard's docstring discharges the **GUARD-ADEQUACY CLAUSE** in all three parts, with the
adversarial variant's **count** stated. Mutations are executed with `PYTHONDONTWRITEBYTECODE=1`, the
tree restored byte-exact after each, and `git status --porcelain` confirmed empty.

**5.5** An artifact guard in **`tests/test_gate_decision_artifact.py`** re-derives the committed
record's independence block **from the committed adjudication record** and asserts they agree — so
the artifact cannot drift from the evidence it summarises. `TC-ArgusAgent-PRECISION-001-61`
(NFR-S1) is re-run green against the regenerated artifact (§2.7).

### AC6 — THE RECORD, THE PROTOCOL AND THE ARCHITECTURE ARE UPDATED WITHOUT REWRITING HISTORY

**6.1** `gate-decision-record.json` is **REGENERATED by `scripts/build_gate_decision.py`**, never
hand-edited, and `--check` exits **0** afterwards. It is committed **separately** from the `argus/`
change (§2.5).

**6.2** A **dated block under protocol §2**, under the existing **V1.3**, records that independence
is now derived and published, that it is a **disclosure and not a condition**, and what it does not
claim. ⛔ **No `V1.4` change-log row** (§2.4). No existing byte of §2/§3/§4/§5 is edited.

**6.3** `architecture.md` §Enforcement gains a **dated addition** under *Gate-decision enforcement*,
**struck-never-erased** (§3.4), naming the module, the vocabulary, the derivation source and the
fact that it gates nothing. `TC-ArgusAgent-DOCS-001-77` stays green.

**6.4** `deferred-work.md` is **append-only**. Any new entry (e.g. a `gate_decision.py` headroom
trigger per §0.5) is a **pure append**; no historical entry is edited (`TC-ArgusAgent-DOCS-001-78`;
16.1's review caught exactly this, and the remedy was **restoration**).

**6.5** `README.md` / `CHANGELOG.md` are updated **only** if a rendered surface actually changed;
if none did, say so explicitly rather than editing them to look busy.

### AC7 — SCOPE, GATES AND HAND-OFF

**7.1 ⛔ MUST NOT MOVE (byte-unchanged, asserted):** `argus/precision/gate_conditions.py` ·
`argus/verdict/negative_assurance.py` · `argus/precision/gate_disclosure.py` ·
`argus/precision/gate_evidence.py` · `argus/dogfood/**` · `argus/detectors/**` ·
`tests/corpus/_manifest.py` · **`tests/cartridges/_registry.py`** · `tests/test_gate_seal.py` ·
`tests/test_vacuous_density.py` · `tests/test_instrument_disclosure.py` ·
`tests/test_instrument_disclosure_surfaces.py` · `tests/test_adjudication_record.py` ·
`tests/test_gate_breadth.py` · `tests/test_gate_decision.py` ·
`validation-corpus/adjudication-record.json` *(under the artifact root — §0.0)* · every threshold,
floor and closed vocabulary in §2.1, **each asserted against the module §2.1's table names**.

⛔ **AMENDED 2026-08-23 — three modules LEFT this list.** `argus/precision/gate_breadth.py`,
`gate_seal.py` and `gate_yield.py` were fenced byte-unchanged **here** while **AC2.3 required the
note to ride on the renderers they own** — and none of those renderers lives in `gate_decision.py`
(§2.3, measured). That made AC2.3 **unsatisfiable**: every route was closed, and the two routes a
dev would most likely take under pressure are the ones §2.3 / `DN-16-5-5` / AC3.1 forbid. The three,
plus `argus/precision/adjudication.py` (which §0.5 had marked *read-only* and AC7.2 omitted
entirely), now sit on **AC7.2** under the budget below. ⛔ **This is a BUDGET, not a release** —
**AC7.1a is what actually holds them**, and it is asserted as strictly as this list.

**7.1a ⛔ THE FORWARDING BUDGET — the four §2.3 modules, each asserted by EXECUTION:**
`argus/precision/adjudication.py` · `argus/precision/gate_breadth.py` ·
`argus/precision/gate_seal.py` · `argus/precision/gate_yield.py` may **each** change by
**EXACTLY**: (a) **one** optional keyword parameter added to **one** function, (b) that keyword
**forwarded** to the **one existing** `precision_gate_status_for` call already in that function,
and (c) the docstring line recording it. Asserted, **and not by reading the diff**:

- ⛔ **With the keyword omitted, each renders BYTE-IDENTICAL bytes** to the pre-story build for the
  same inputs — proven by **rendering and comparing strings**, the Task 3 method (NFR-P1).
- ⛔ **No arm module derives, parses or words the note.** Every sentence stays owned by
  `gate_independence.py` (AC1.1). No arm module gains a second parameter.
- ⛔ **No new import edge into or out of any of the four** — in particular **none of them imports
  `gate_independence`**, so `DN-16-5-1`'s one-way direction (`gate_decision` -> sibling) is
  unchanged. They forward an **opaque optional string**.
- ⛔ **No other behaviour, signature, constant or public name moves**, and no `__all__` in the four
  changes.
- ⛔ **Anything beyond (a)/(b)/(c) is an AC7.4 escalation** — report the measurement and STOP. In
  particular, if the note cannot be threaded within this budget, **do NOT widen it silently**.

**7.2 Expected to change:**
`argus/precision/gate_independence.py` **(new)** · `argus/precision/gate_decision.py` (field,
payload key, status-property wiring, the note derivation, the forwarded argument at `:811`
— ⛔ **including moving the `live` / `adjudicators` derivation from `:820-823` to ABOVE the fold call
at `:811`, a re-order and not merely a forward (Task 4)** — `__all__`) · `argus/precision/replay_harness.py` (one optional keyword) ·
⛔ **the four §2.3 FORWARDERS, under the AC7.1a budget ONLY — added 2026-08-23** —
`argus/precision/adjudication.py` · `argus/precision/gate_breadth.py` ·
`argus/precision/gate_seal.py` · `argus/precision/gate_yield.py` ·
`tests/test_gate_independence.py` **(new)** · `tests/test_gate_decision_artifact.py` ·
`validation-corpus/gate-decision-record.json` *(regenerated; artifact root, §0.0)* · the dogfood artifacts *(regenerated,
in the §2.5 order, only if `argus/` changed)* · `precision-validation-protocol.md` §2 *(dated block,
no change-log row)* · `architecture.md` §Enforcement *(struck-not-erased)* · `deferred-work.md`
*(pure append)* · this story file · `sprint-status.yaml`.

**7.3 Gates, all green before hand-off**, each with its command and output recorded:
full suite with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` · `mypy argus` · `bandit -r argus
--severity-level medium` · `scripts/build_gate_decision.py --check` **exit 0** ·
`scripts/build_adjudication_record.py --check` **exit 0** · `tests/test_module_size_ceiling.py`
green with **no `_EXEMPT_BY_DESIGN` entry added** (`MAINT-001-04`: the registry may only shrink).

**7.4 ⛔ ESCALATE, do not decide, if:** the derived status over the live record is anything other
than `NOT_INDEPENDENT`; `--check` is already stale at Task 0; the projected `gate_decision.py` delta
breaches 1,200 even after a cohesion split; or any part of this story turns out to require filling a
role, amending §5, or moving a threshold. Report the measurement and **STOP** — the Story 13.5 **E2**
escalation shape, unchanged.

⛔ **ONE NAMED EXCEPTION, ALREADY ADJUDICATED — added 2026-08-23.** The shipped docstring at
`argus/precision/gate_breadth.py:366-368` records `DN-16-1-1` as having rejected *"threading a
breadth argument into the fold"* on the ground that the fold's signature is *"shared with the
cartridge path"*. AC7.1a threads a keyword into that fold, so this **looks** like an AC7.4 trigger.
⛔ **It is NOT. See `DN-16-5-7` (Dev Notes).** The rationale was measured and is false as applied to
the fold (`fold_adjudicated_precision` has one production caller, `gate_decision.py:811`;
`compute_precision` returns `PrecisionResult` and does not call it); `DN-16-1-1`'s holding — *the
fold is not forked* — **stands**, and one inert keyword is not a fork. **Proceed, and do NOT edit
`gate_breadth.py:366-368`** — correcting that shipped sentence was considered and **declined**, and
doing it anyway IS an escalation. **Any OTHER locked decision that appears to forbid a required edit
remains a STOP.**

---

## Dev Notes

### Decisions this story TAKES, each with its rejected alternative

**`DN-16-5-1` — a new sibling module, not new bulk in `gate_decision.py`.**
*Rejected:* putting the constants and sentences in `gate_decision.py`. It sits at 1,084/1,200 with
no ledger entry, and the 16.1/16.2/16.3 precedent is unanimous: the arm module owns the constants,
the predicate and the sentences; `gate_decision.py` owns the field, the payload key and the
dispatch. One import direction only (`DN-16-1-3`).

**`DN-16-5-2` — the FR34 `InstrumentStatus` vocabulary is NOT extended.**
*Rejected:* a third `InstrumentStatus` member. That vocabulary describes **the instrument, per tool
VERSION**, and is removed only by the ≥80% gate clearing — *"nothing else removes it"*. This story's
status describes **one adjudication run** and changes whenever the record does. Merging them is
exactly the run-grade/instrument-status confusion the enum's own docstring warns against, and it
would make the FR34 disclosure appear to move when it has not. "Extends FR34's mechanism" is
satisfied by riding the **same single status renderer** (AR7) rather than by editing FR34's enum.

**`DN-16-5-3` — derived from the RECORD, never from protocol §2's holder table.**
*Rejected:* parsing §2's markdown holder table. It is prose; it can drift from the record; and it
answers a **different question** — §2 records who **may** judge, the record records who **did**.
AC1 says "derived from the registered adjudicators on the adjudication record", and the field is
already computed by `decide_gate`.

**`DN-16-5-4` — the sentence separates *did not judge* from *not filled*.**
*Rejected:* a terse "roles present / roles absent" rendering. As of `1bb7088` the QA Lead is filled
and has judged nothing, so "absent" would be read as "unfilled" — a true statement with a false
subject, which is `DF-9-2-B`'s class on the surface that publishes the gate. The status is scoped,
in its own words, to **the adjudication that was performed**.

**`DN-16-5-5` — one optional keyword on the existing renderer; no post-processing.**
*Rejected:* a wrapper that appends the note to the returned string. String surgery on another
function's output is a second mechanism (AR7) that silently forks the day the first one's wording
changes, and it cannot be made byte-stable across the three branches.

**`DN-16-5-6` — the note attaches only where the status is rendered from an adjudication record.**
*Rejected:* attaching it to every `precision_gate_status_for` call site. The dogfood generator
passes `precision=None` and reads no record; the cartridge fold has golden keys, not adjudicators.
A sentence about independence on either would describe a judgement that never happened — the
`DF-8-5-C` hand-written-figure class, one level up.

**⛔ `DN-16-5-7` — `DN-16-1-1`'s RATIONALE is corrected by measurement; its HOLDING STANDS.**
*Recorded 2026-08-23, OPERATOR-AUTHORISED, after round-2 validation. Read this BEFORE Task 4.*

**The conflict, stated plainly so you meet it at the same moment you meet the citation.** AC7.1a
threads one optional keyword into `fold_adjudicated_precision`. The shipped docstring of
`argus/precision/gate_breadth.py:366-368` — **the very renderer AC2.3 depends on, in a module you
are about to edit** — says:

> **The fold is NOT forked** (DN-16-1-1). `fold_adjudicated_precision` and `AdjudicatedPrecision`
> are byte-untouched: threading a breadth argument into the fold would widen a signature shared
> with the cartridge path, where breadth is meaningless.

**Half one — the stated RATIONALE is factually FALSE as applied to the fold.** Re-measured
repo-wide at HEAD `52143eb`, not asserted:

- `fold_adjudicated_precision` has **exactly ONE production caller**: `gate_decision.py:811`. The
  only other non-test references are the `def` and `__all__` entry in `adjudication.py` and two
  docstring `:func:` cross-references (`replay_harness.py:296`, `scripts/build_gate_decision.py:7`)
  — **cross-references, not calls**.
- The cartridge path is `replay_harness.compute_precision`, which returns **`PrecisionResult`**
  (`replay_harness.py:386`) — a **different type** from `AdjudicatedPrecision` — and **does NOT call
  `fold_adjudicated_precision`** anywhere.
- What the cartridge path and the gate path **actually share** are the two helpers in
  `replay_harness.py` that **both** call directly: `precision_fraction` (`:291`; its own docstring at
  `:296` says exactly this — *"the cartridge fold and the repository-corpus adjudication fold both
  call this"*) and `precision_gate_status_for` (`:729`). The cartridge path reaches them at `:501`
  and `:570`; the adjudication fold reaches them at `adjudication.py:875` and `:963`.
- **Therefore the fold's signature is adjudication-only and is shared with NOTHING.** `DN-16-1-1`'s
  *"a signature shared with the cartridge path"* is **wrong on the facts as applied to the fold** —
  the sharing it describes is real, but it lives one level down, in `replay_harness.py`, and this
  story does not widen either shared helper's signature for the cartridge path.

**Half two — `DN-16-1-1`'s HOLDING SURVIVES, UNREVERSED.** Its actual subject is *"the fold is NOT
**forked**"* — no second fold, no second arithmetic, no second status function (AR7). AC7.1a adds
**ONE inert keyword with a byte-identical default**, asserted by rendering and comparing strings
(AC7.1a bullet 1). **That is not a fork.** The fold stays single, its arithmetic stays single, and
`precision_gate_status_for` remains the one status function. ⛔ **`DN-16-1-1` is NOT overturned and
NOT reopened — only its supporting rationale is corrected.** Independence, unlike breadth, is a
property of **the adjudication record the fold already takes as its first argument**, which is why
the keyword belongs there and why 16.1's objection never reached it.

⛔ **What this means for you at Task 4: the shipped `gate_breadth.py:366` sentence is a KNOWN,
ALREADY-ADJUDICATED conflict, not a stop signal.** Without this note the correct behaviour on
reading it would be to STOP under AC7.4 — that is the escalation discipline working, and it is
exactly the avoidable round trip `DN-16-5-7` exists to prevent.

⛔ **DO NOT "fix" the shipped docstring.** The operator **considered correcting
`gate_breadth.py:366-368` and explicitly DECLINED it.** The false sentence stays in the code for now;
`DN-16-5-7` lives **in this story only**. Editing it would breach AC7.1a's budget (one keyword, one
forward, one docstring line recording **the keyword**) and is an **AC7.4 escalation**.

### Locked decisions this story CITES rather than reopens

- **OI1** — recall stays diagnostic; nothing here touches it.
- **`DN-1`** (three terminal states), **`DN-3`** (one floor, resolved, never re-typed),
  **`DN-14-2-1`** (two assertion vocabularies), **`DN-16-1-1/2/3`** (fold not forked; amend by
  appending; one import direction).
  ⛔ **`DN-16-1-1` — READ `DN-16-5-7` ABOVE BEFORE TASK 4.** Its **holding** (*the fold is not
  forked*) is cited here and **stands unreversed** — AC7.1a adds one inert keyword, which is not a
  fork. But its **stated rationale** (*"a signature shared with the cartridge path"*), which is
  **shipped in `gate_breadth.py:366-368`** and appears to forbid AC7.1a, was **measured and is false
  as applied to the fold**: `fold_adjudicated_precision` has one production caller
  (`gate_decision.py:811`) and `compute_precision` returns `PrecisionResult` without calling it.
  **`DN-16-5-7` records the correction; this conflict is already adjudicated and is NOT a reason to
  stop.**
- **§3.4** — amend by dated block; strike, never erase; append-only ledger.
- **§6 R2** — ratification and role-filling are operator acts.

### Open ledger entries bearing on this story — verify against `deferred-work.md` on disk

| id | State | Bearing |
|---|---|---|
| `DF-13-5-A` | **OPEN, UNSPENT** | Untouched. This story spends nothing and proposes no expansion. |
| `DF-16-1-A` | **OPEN, unlanded** | Rule-class arm. Untouched; the count stays disclosed. |
| `DF-16-3-A` | **OPEN** | `tests/test_gate_seal.py` 1,145/1,200, trigger 1,180. ⛔ Put nothing there. |
| `DF-15-2-E` | **OPEN** | `tests/test_vacuous_density.py` 1,159/1,200. Byte-unchanged. |
| `DF-15-2-D` | **CLOSED 2026-08-22** by `4123931` | Cited, not reopened. The vocabulary now lives in `argus/detectors/vacuous_vocabulary.py`. |
| `DF-16-1-B` | **Discharged** by 16.2 (`95819bc`) | Cited. Note `gate_decision.py` now has **no** open entry — §0.5. |

⛔ **Writing rule — `TC-ArgusAgent-DOCS-001-78`.** `deferred-work.md` is append-only. Edits to
historical entries must be annotated, not silent — 16.1's review caught exactly that, and the remedy
was **restoration**, not annotation after the fact.

### Dependencies — none are added, and that is a requirement

No new package. No new import edge from `argus/**` into `tests/**` (`DF-9-2-A`: `tests/` is absent
from the built distribution). No module-level repository-only path in `gate_independence.py` — every
input arrives as an argument, exactly as `gate_breadth.py` documents.

⛔ **`replay_harness.py:788` ALREADY reaches `tests/cartridges/_registry.py`, and that is
DELIBERATE, CORRECT AND OUT OF SCOPE — noted 2026-08-23 so it is not "fixed".**
`floor_n = registry_module().VALIDATION_SET_FLOOR_N if floor_n is None else floor_n` resolves the
floor **lazily, through an indirection**, precisely so there is **no module-level import edge** into
`tests/`. That indirection is `DF-9-2-A`'s **remedy, not its symptom**, and it is what `DN-3` means
by *one floor, resolved from the cartridge registry, never forked*. ⛔ **A dev reading AC1.1's
purity clause beside §2.1's `_registry.py` pointer will be tempted to read it as a live defect and
refactor it. DO NOT.** `tests/cartridges/_registry.py` is on **AC7.1**'s must-not-move list, and
`replay_harness.py`'s **only** permitted delta in this story is AC2.1's one optional keyword.
Removing or rerouting the indirection is an **AC7.4 escalation**, not a tidy-up.

### Standing rules (non-negotiable)

- **AR7** — one arithmetic, one renderer, never forked.
- **AR8** — pure/impure separation; the decision path is pure, I/O lives in `scripts/`.
- **AR10** — typed failures; a `ValueError` subclass whose message says what a reader must do.
- **NFR-P1** — no clock, no randomness, no network on any decision path; byte-stability of every
  surface this story does not intend to move.
- **NFR-S1** — no source byte, no secret value, no absolute host path in any artifact.
- **NFR-M1** — 1,200 physical lines per module. **Split, never shave, never exempt.**
- **`AI-E11-1`** — every guard asserts its population is non-empty **before** asserting anything
  about it.
- **`DF-10-4-E`** — an unregistered value RAISES; never defaulted, never tolerated.

### Previous-story intelligence — 16.1, 16.2, 16.3 (`done`), 16.4 (`done`, closed by decision)

1. **All three of 16.1–16.3 found a stated premise false by executing it.** 16.4 found **three**,
   one of which (a claimed 4 red guards; the measured number was **13**) changed its plan. **This
   story already carries one: §0.2, the epic's "both unfilled" premise.** Expect another.
2. **All three hit the lockstep trap** in their fixtures. 16.2's remedy — a mixed population
   isolating one term — was needed a second and a third time. §2.8 names this story's version.
3. **All three were handed an unfiled NFR-M1 split-first trigger** at the least convenient moment.
   §0.5 is the pre-emption. **Check the ceiling before you write.**
4. **16.3's own mutation run caught one of its guards UNREAL** — it read the committed JSON rather
   than the live sentence. **Expect to find one of yours.** AC2.4 and AC5.5 are written to make that
   specific failure detectable here.
5. **16.4 closed by DECISION, not by result** — HALT-1 declined, nothing ratified, N still 5, no
   detector run over a bench member. So the live record this story derives from is **still the
   2026-08-17 set of 31**, and the answer is still `NOT_INDEPENDENT`. Do not expect a fresher one.
6. **Two commits, not one, when a sha must be cited** — a commit cannot cite itself.

### Git intelligence

The Epic 16 commits follow a fixed arc, and it is worth following:
`chore(story file + in-progress) → [refactor/test(split-first, alone)] → feat(the change) →
chore(regenerate artifacts) → docs(protocol/architecture/ledger) → docs(the review)`.

`4123931` and `ba5e8df` are the current model for the split-first discipline — the split landed
**alone and before** any behaviour change, and `52143eb` recorded the discharge in the ledger
afterwards. `1bb7088` is the model for a protocol edit that adds a dated block and **no** change-log
row. ⛔ **Not one Epic 16 commit touches a `CANDIDATE_OUTPUT_PATHS` entry, and the epic's BINDING
ORDERING CONSTRAINT is intact.** This story adds no bench output, so it cannot break it — **verify
that claim** with `tests/test_gate_ordering.py` rather than asserting it.

### References

- [epics.md](../epics.md) §Epic 16 (`epics.md:3019`), §Story 16.5 — the `### Story 16.5` **heading**
  is `epics.md:3191`; the *"both **unfilled**"* **Given** is `epics.md:3199` (cite tightened
  2026-08-23, §0.2). Under the artifact root, §0.0.
- [precision-validation-protocol.md](../precision-validation-protocol.md) §2 (roles, the 2026-08-16
  attribution amendment, the **2026-08-22 dated block** filling the QA Lead), §3 (expert-hours),
  §4 (ladder), §5 (all seven conditions), §6 (R2), §7 (OI1)
- [architecture.md](../architecture.md) §Enforcement — guard-adequacy, adjudication-record,
  gate-decision
- [deferred-work.md](../deferred-work.md) — `DF-13-5-A`, `DF-16-1-A`, `DF-16-3-A`, `DF-15-2-D/E`,
  `DF-16-1-B`
- [sprint-change-proposal-2026-08-20.md](../sprint-change-proposal-2026-08-20.md) §5(5) — *"16.5
  stamps the independence status onto the record whatever the number is."*
- Stories [16.4](16-4-ratify-run-adjudicate-and-let-the-arithmetic-decide.md),
  [16.3](16-3-a-detector-that-finds-nothing-has-not-passed.md),
  [16.2](16-2-part-of-the-bench-is-sealed-before-anything-is-run.md),
  [16.1](16-1-a-score-drawn-from-one-repository-is-not-a-score.md),
  [13.3](13-3-record-the-result-and-let-it-decide.md)
- Code: `argus/precision/{gate_decision,gate_breadth,gate_seal,gate_yield,gate_conditions,gate_evidence,gate_disclosure,adjudication,replay_harness}.py` ·
  `argus/verdict/negative_assurance.py` · `argus/dogfood/proof_run.py` ·
  `scripts/build_gate_decision.py` ·
  `tests/test_gate_{decision,decision_artifact,breadth,seal,yield,ordering}.py` ·
  `tests/test_instrument_disclosure.py` · `tests/test_module_size_ceiling.py`

---

## Tasks & Subtasks

### ⛔ Task 0 — REPRODUCE §0 BEFORE WRITING ANYTHING

- [x] Baseline: full suite (`ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`), `mypy argus`, `bandit`, **both**
      builders `--check`. Record collected count and every exit code. **A stale `--check` at this
      point is an escalation (AC7.4), not something to fix in passing.**
- [x] Re-derive **every row of §0.1** from the two committed JSON artifacts by execution — the 31
      rows, the disposition tally, and that the distinct adjudicator set has **exactly one** member.
- [x] Re-confirm **§0.2** against `precision-validation-protocol.md` §2 on disk and against
      `git show 1bb7088`: QA Lead **filled**, External adjudicator **unfilled**, change-log head
      **V1.3**.
- [x] Re-measure **§0.5** with `test_module_size_ceiling.py::_physical_line_count`, and re-derive
      **§0.6**'s next free ids by `grep`. **Report any row that differs.**
- [x] Confirm `git status --porcelain` shows **only** this story file and `sprint-status.yaml`
      **plus this story's validation reports** (create-story wrote the first two at `52143eb` and did
      not commit them; the validation rounds added `…-validation-2026-08-23.md` and
      `…-validation-2026-08-23-round-2.md`, untracked — **four entries, not two**). ⛔ **These are
      expected, not a §0 mismatch.** Land them as the arc's first `chore(story file + in-progress)`
      commit, then confirm the tree is clean before Task 1.

### Task 1 — THE HEADROOM DECISION, TAKEN BEFORE THE FIRST LINE (AC5.1, §0.5)

- [x] Estimate the `gate_decision.py` delta (field + payload key + property wiring + the note
      derivation + the forwarded argument at `:811` + their comment blocks, at this module's
      measured density).
- [x] ⛔ **PROJECT THE FOUR §2.3 FORWARDERS TOO — ADDED 2026-08-23.** The earlier version of this
      task projected only `gate_decision.py`, so **the modules the dev must actually edit to satisfy
      AC2.3 were outside the projection entirely**. Measured with the guard's own
      `_physical_line_count`: `adjudication.py` **973/227**, `gate_seal.py` **777/423**,
      `gate_yield.py` **560/640**, `gate_breadth.py` **436/764**. At the AC7.1a budget — one keyword,
      one forwarded argument, one docstring line each — the delta is single-digit per module, so
      **none of the four can reach 1,100, let alone the 1,150 split-first trigger or the 1,200
      ceiling.** ⛔ **The consequence is therefore STATED, not discovered at Task 4: this amendment
      adds NO new NFR-M1 trigger, and `gate_decision.py` at 1,084 remains the ONLY one to watch.**
      ⛔ **Re-measure all four and confirm anyway** — if any projection contradicts this line, that is
      §0's next false premise and it is **reported (AC7.4), not absorbed**.
- [x] **If projected > 1,150:** perform the cohesion split **FIRST, alone, in its own commit**, with
      no behaviour change, on the `gate_conditions`/`gate_evidence` precedent — every symbol
      re-exported, every import line unchanged, proven a pure move by AST span comparison + sha256,
      and `MAINT-001-04` respected (**no `_EXEMPT_BY_DESIGN` entry**).
- [x] **If projected 1,100–1,150:** file a new ledger entry naming the trigger (pure append).
- [x] Record the projection and the decision either way.

### Task 2 — THE MODULE (AC1)

- [x] `argus/precision/gate_independence.py`: the closed vocabulary + raising lookup, the frozen
      assessment dataclass with `to_payload()`, the pure `assess_independence(...)`, and the
      status-note renderer. Docstring records the **derivation and every rejected alternative**.
- [x] Reuse `PROTOCOL_ADJUDICATOR_ROLES` and `adjudicator_role()`. **No second parser or role list.**
- [x] `AI-E11-1`: an empty adjudicator set yields `NOT_ESTABLISHED`, never `NOT_INDEPENDENT`.
- [x] AC1.5's roster/record distinction is in the **published sentence**, not only in a comment.

### Task 3 — THE RENDERER (AC2.1, AC2.2)

- [x] One optional keyword on `precision_gate_status_for`, defaulting so existing callers are
      byte-identical. Rendered in **all three** branches.
- [x] Prove byte-stability by **rendering and comparing strings** for the dogfood and cartridge call
      sites — before and after — not by reading the diff.

### Task 4 — THE WIRING (AC1.3, AC2.3, AC2.5)

- [x] `GateDecision` gains one field, **defaulted last and `None`-able**, on the
      `corpus_read_proof` / `breadth` / `seal` / `yield_` precedent, so **no existing construction
      site moves**.
- [x] `decide_gate` derives it from the `adjudicators` tuple it **already** computes. **No recount.**
      ⛔ **This is a RE-ORDER, not a one-line forward — noted 2026-08-23.** `decide_gate` calls
      `fold_adjudicated_precision` at **`:811`** but derives `live = record.live_rows()` and the
      `adjudicators` tuple at **`:820-823`, AFTER it**. To pass the note **into** the fold, that
      derivation must **move above `:811`**. Everything it depends on (`record`, and therefore
      `record.live_rows()`) is already in scope there, so the move is mechanical and lands inside an
      AC7.2 module — but it is an edit to the gate's central function, so make it deliberately and
      confirm nothing between `:811` and `:823` depended on the old order.
- [x] `precision_gate_status` threads the note through **all four** renderer branches. ⛔ **NONE of
      the four renders in `gate_decision.py`** (§2.3): `decide_gate` derives the note and passes it
      into `fold_adjudicated_precision` — **its only production caller**, verified repo-wide — and
      each arm module **forwards the same one keyword on its RE-RENDER path**. The **short-circuit**
      path (`return fold.gate_status`) needs no edit: it inherits the note from the fold. ⛔ No
      string post-processing; no arm module derives or words the note (AC7.1a, `DN-16-5-5`).
- [x] ⛔ Confirm **by rendering and comparing strings** that every EXISTING caller of the fold
      builder and of the three arm renderers is byte-identical and **NOT edited**:
      `tests/test_adjudication_record.py`, `tests/test_gate_breadth.py`,
      `tests/test_gate_decision.py`, `tests/test_gate_decision_artifact.py` and
      `scripts/build_gate_decision.py`. Any of them needing an edit means the keyword is not
      defaulted inertly — fix the default, do not edit the caller.
- [x] ⛔ **AND the three DIRECT callers of `precision_gate_status_for` the list above omitted —
      added 2026-08-23.** AC2.1 requires **every existing caller** to render byte-identically, and
      the list above named only callers of the **fold builder**. Also confirm, by the same
      render-and-compare method and **without editing them**:
      `tests/test_gate_flip_path.py` (`:232`, `:240`, `:251`),
      `tests/test_precision_replay.py` (`:390`, `:395`) and
      `tests/test_validation_corpus.py` (`:909`, `:917`). All three are on **AC7.1's byte-unchanged
      fence**, so an edit to any of them is an AC7.1 breach, not a fix. *(`argus/dogfood/proof_run.py`
      `:591`/`:653` and `replay_harness.py:570` are already covered — AC7.1's `argus/dogfood/**` and
      AC3.4. Nothing here is unsatisfiable; the confirmation list was simply incomplete.)*
- [x] `to_payload()` gains one top-level key. `__all__` updated. **`SECTION_5_CONDITIONS` untouched.**

### Task 5 — THE GUARDS (AC5)

- [x] `tests/test_gate_independence.py` **(new)**, from `-105`. Generated populations, breadth /
      seal / yield / counts **pinned** (§2.8). Assert **where the status flips**.
- [x] Every vocabulary member reached; the unregistered lookup driven to its raise; both directions.
- [x] AC2.4's separation guard, RED in **both** mutation directions at the real seam.
- [x] AC4.3's inertness proof, over **both** an otherwise-`CLEARED` population and the live
      `BLOCKED` one.
- [x] AC4.4's byte-unchanged constants guard, by value, in one place.
- [x] AC3.1's no-second-renderer walk; AC3.2 / 3.3 / 3.4's byte-identity assertions.
- [x] AC5.5's artifact guard in `tests/test_gate_decision_artifact.py`, re-derived from the
      committed adjudication record.
- [x] Every docstring discharges the **GUARD-ADEQUACY CLAUSE** (i)/(ii)/(iii) with counts.
      Mutations under `PYTHONDONTWRITEBYTECODE=1`, tree restored, `git status` clean after each.

### Task 6 — THE ARTIFACTS, IN THE §2.5 ORDER (AC6.1)

- [x] Commit `argus/` first.
- [x] `python scripts/regenerate_dogfood_artifacts.py`; commit the regenerated artifacts separately.
- [x] `python scripts/build_gate_decision.py` to **regenerate** `gate-decision-record.json`; confirm
      `--check` exit **0**; commit separately. ⛔ Never hand-edit the artifact.
- [x] Re-run `TC-ArgusAgent-PRECISION-001-61` (NFR-S1) against the regenerated artifact.

### Task 7 — THE RECORD (AC6.2–6.5)

- [x] Protocol §2 **dated block under V1.3** — no `V1.4` row, no existing byte edited.
- [x] `architecture.md` §Enforcement dated addition under *Gate-decision enforcement*,
      **struck-never-erased**; confirm `TC-ArgusAgent-DOCS-001-77` green.
- [x] `deferred-work.md` **pure append** only (`TC-ArgusAgent-DOCS-001-78`).
- [x] `README.md` / `CHANGELOG.md` only if a rendered surface actually moved — **say so either way.**

### Task 8 — GATES AND HAND-OFF (AC7.3)

- [x] All of AC7.3, each with its command and output recorded in the Dev Agent Record.
- [x] Confirm AC7.1's must-not-move list byte-unchanged (`git diff --stat` against Task 0's HEAD).
- [x] ⛔ **Confirm AC7.1a's FORWARDING BUDGET on the four §2.3 modules — added 2026-08-23.** Read
      the actual diff for `adjudication.py`, `gate_breadth.py`, `gate_seal.py` and `gate_yield.py`
      and confirm **each** is exactly (a) one optional keyword, (b) forwarded to the one existing
      `precision_gate_status_for` call, (c) one docstring line — **and nothing else**. Then confirm
      by **rendering and comparing strings** (not by reading the diff) that with the keyword omitted
      each is **byte-identical** to the pre-story build. ⛔ **A diff wider than the budget is an
      AC7.4 escalation, even if the suite is green.**
- [x] ⛔ Confirm §2.1's constants are still byte-unchanged **by value** (AC4.4) — note
      `PROTOCOL_ADJUDICATOR_ROLES` and `DISPOSITIONS` live in `adjudication.py`, which is no longer
      whole-module fenced, so this assertion now carries weight it did not carry before.
- [x] Fill the Dev Agent Record below; set the story to `review`; update `sprint-status.yaml`.

### Review Findings

**Method note.** This review re-derived the story's own claimed evidence rather than trusting
it: re-ran the full suite (1,686 passed / 0 failed, exit 0), `mypy argus` (94 files clean),
`bandit -r argus --severity-level medium` (0 medium / 0 high), both builders `--check` (exit 0
each), and `tests/test_module_size_ceiling.py` (green). Confirmed by execution: `AC7.1`'s
must-not-move list is byte-unchanged (`git diff --stat 52143eb..HEAD` over all fenced paths
returns nothing); the AC7.1a budget on the four §2.3 forwarders is exactly +4/+3/+3/+3 with zero
deletions and no `gate_independence` import in any of the four; `gate_breadth.py:366-368` is
byte-as-shipped; the protocol edit is +57/-0 under the existing V1.3 with no `V1.4` row;
`gate_decision.py` is 1,132 lines with `DF-16-5-A` filed, not split; the README/CHANGELOG module
figures (93→94 / 101→102 / 100→101) are verified green against a real build
(`tests/test_instrument_disclosure*.py`). Four mutation spot-checks were run, each restored
immediately (`git status --porcelain` clean after every one): (1) a fifth `precision_evaluable`
conjunct gating on independence — RED on `-109`/`-111`; (2) the raising vocabulary lookup
replaced by a silent `dict.get` default — RED on `-105`; (3) `decide_gate`'s `record.live_rows()`
replaced by `record.rows` (including superseded rows) — **no test in the targeted surface caught
this**, see finding below; (4) the byte-identical-when-omitted default widened to inject text —
RED on both the new `-106` guard and the pre-existing `test_TC_ArgusAgent_DOGFOOD_001_54` guard.

- [x] [Review][Patch] Historical `deferred-work.md` entry byte-edited in the same commit that
      claims "not one byte of the entry above it is edited"
      [`_bmad-output/design-artifacts/ArgusAgent/deferred-work.md:5257`] — Commit `9aea1be`
      (the Task-0 baseline-repair commit this story itself flags as its highest-value review
      target) silently dropped a literal `\r` byte from a pre-existing, pre-16.5 entry
      describing `argus/pipeline_stages.py:124` (the `DF-15-2-B` / `DF-14-3-A` discussion).
      Before: `` the reason `\r` / ` `` (an inline code span whose content is the literal CR
      byte, followed by one whose content is the literal LF). After: `` the reason ` / ` ``
      (the CR byte is gone; both spans now read as a bare newline). This is a genuine content
      edit to a **historical** entry, not a formatting artifact — verified byte-for-byte with
      `git show 52143eb:...` vs `git show 9aea1be:...`. It violates AC6.4 ("deferred-work.md is
      append-only… no historical entry is edited") and directly contradicts the commit message
      and the new `status:` field's own text ("A PURE APPEND: not one byte above is edited"),
      which the diff itself falsifies (`git diff --stat` on this commit reports
      `24 insertions(+), 1 deletion(-)`, not 0 deletions). This is exactly the `TC-ArgusAgent-
      DOCS-001-78` / "16.1's review caught exactly this, remedy was restoration" failure class
      the story's own Dev Notes warn about, recurring inside this story's own repair commit.
      **Fix:** restore the literal `\r` byte at that exact position (a one-byte edit), and audit
      whether the same editing pass touched any other historical byte in this file.

- [x] [Review][Patch] No guard exercises independence-status scoping to LIVE rows (excludes
      superseded rows) [`argus/precision/gate_decision.py:856`, `tests/test_gate_independence.py`]
      — AC1.3 claims the status is "reached through the `adjudicators` tuple `decide_gate`
      already computes" off `record.live_rows()`, explicitly scoped to live (non-superseded)
      rows. Mutation-tested: replacing `live = record.live_rows()` with `live = record.rows` in
      `decide_gate` and re-running the full targeted surface (`tests/test_gate_independence.py`,
      `tests/test_gate_decision.py`, `tests/test_adjudication_record.py`,
      `tests/test_gate_decision_artifact.py`) produced **zero failures** — every test passed
      unchanged. No generated population in `tests/test_gate_independence.py` includes a
      superseded row, so a regression that let a superseded row's adjudicator leak into the
      independence derivation (e.g. quietly upgrading a `NOT_INDEPENDENT` record to
      `SECOND_REVIEWER_INTERNAL` or `EXTERNAL_ADJUDICATOR_PARTICIPATED` because a struck row
      happened to be authored by a different role) would go undetected. This does not manifest
      on the live committed record today (0 superseded rows), so nothing is currently
      mis-derived, but it is a real GUARD-ADEQUACY gap against AC5.4's own "adversarial variant
      generated from the record the guard closes over" requirement, in a module whose whole
      purpose is a disclosure a reader trusts. **Fix:** add a generated population with at least
      one row struck by a `supersedes` correction whose adjudicator differs in role from the
      live row that replaces it, and assert the derived `IndependenceAssessment` reflects only
      the live row's author.

### Review Fix Round 1 — 2026-08-23, dev-story (Opus 5)

**Both findings resolved. 2 of 2. No finding rebutted, none deferred, no guard weakened.**
⛔ `argus/**` and `scripts/**` are **byte-unchanged by this round** (`git diff HEAD -- argus/
scripts/` is empty), so §2.5's artifact-currency order is **not re-armed**: no dogfood
regeneration, no builder re-run, and `gate_decision.py` stays at **1,132** — no split trigger
crossed by the fix, and `DF-16-5-A` is neither closed nor amended.

**Finding 1 — the append-only violation (AC6.4), `deferred-work.md:5257`. RESTORED, and the
audit went well past the one byte.**

The review was right in every particular. `9aea1be` turned a literal **CR** byte into a line
break, splitting one historical line into two, inside an entry describing
`argus/pipeline_stages.py:124`. The prose there reads *"the reason `<CR>` / `<LF>` are not part
of the problem"* — two inline code spans whose CONTENT is the two line-ending bytes being
discussed. Dropping the CR did not merely reflow a line: it made the sentence contrast a
newline **with itself**, destroying the very distinction the entry was written to draw. The
remedy is 16.1's: **restoration**, not an amended guard.

⛔ **The mechanism, found by the audit and worth more than the byte.** `core.autocrlf=true` with
**no `.gitattributes`** — but git stores this file **verbatim**, because a **lone CR makes
git classify a file as binary** (`convert_is_binary` returns 1 on `lonecr`), which silently
switches CRLF normalisation OFF. So: the blob carried LF endings **plus** one lone CR; the
worktree copy was byte-identical; an editor then rewrote the file as CRLF, which both
normalised every terminator **and** consumed the lone CR. On commit git saw no lone CR, decided
the file was text after all, and normalised CRLF→LF — landing exactly one net deletion.
⛔ **This bit me too, in the fix's first attempt:** restoring the CR into the CRLF worktree flipped
git back to binary mode and staged **5,643 CRLF terminators** into the blob. The restoration was
therefore rebuilt **from the blob**, not from the worktree, and the file is now written with LF
terminators + the single lone CR. `worktree bytes == staged blob bytes` is asserted.

**What the audit covered, and what it found.** A line-level alignment (`difflib`, `autojunk=False`)
over the **byte** content of every blob in the arc — `52143eb → 9aea1be → c5ca6a7 → cd4cbe4 →
ca0dee2 → 927548d → 028c3c8` — comparing every commit against its predecessor, plus a whole-file
comparison of the pre-story baseline against the current file. **Result: exactly ONE change in
the entire arc modified a pre-existing line — the CR at 5257.** Every other change is a pure line
INSERT: 22 lines (the `DF-15-2-D` `status:` field, `9aea1be`) and 45 lines (`DF-16-5-A`,
`927548d`). Zero pre-existing lines deleted or replaced anywhere else; commits `c5ca6a7`,
`cd4cbe4`, `ca0dee2` and `028c3c8` touched the file not at all. Proven two ways: the alignment
reports `HISTORICAL LINES DELETED OR REPLACED: 0`, and the baseline was **reconstructed
byte-exactly** (424,300 bytes) by deleting only the inserted ranges from the current file.
CR count is back to **1**, matching `52143eb`.

⛔ **One further regression the audit surfaced, reported rather than absorbed:** `927548d` also
dropped the file's **trailing newline** (`\ No newline at end of file`), which it had carried for
its entire prior history. Not a historical-byte edit — the old content remained a strict prefix —
but a POSIX text-file violation on a repo whose CI runs an ubuntu matrix. **Restored** (a one-byte
pure append at EOF, touching no historical byte). Recorded here rather than done silently.

**Finding 2 — the unguarded LIVE-row derivation (AC1.3 / AC5.4). GUARDED, and the guard is
proven non-vacuous by the reviewer's own mutation.**

New: `TC-ArgusAgent-PRECISION-001-114` in `tests/test_gate_independence.py`, with a
`_superseded_population` builder that extends `_population` (so every pinned term — member
spread, size, locators, rule ids, dispositions — is **inherited, not re-typed**, keeping §2.8's
lockstep discipline). It strikes one row via a real `supersedes` correction: the struck row and
its replacement share a `finding_id` by construction, so only `row_id`, `adjudicator`, `reason`
and `supersedes` move. **GENERATED adversarial variants: 2** — one per registered role that is
not the Engineering Lead, each forging a *different* status (`SECOND_REVIEWER_INTERNAL`,
`EXTERNAL_ADJUDICATOR_PARTICIPATED`), which is precisely the *"quietly upgrading a
`NOT_INDEPENDENT` record"* leak the review named.

⛔ **MUTATION-VERIFIED, at the real seam.** `argus/precision/gate_decision.py:856`,
`live = record.live_rows()` → `live = record.rows` (the review's own mutation, applied
length-preservingly): **BOTH parametrised `-114` cases go RED** on the leaked adjudicator set,
while every other guard in `test_gate_independence.py`, `test_gate_decision.py`,
`test_adjudication_record.py` and `test_gate_decision_artifact.py` stays **green** — so the guard
is targeted at exactly the defect that previously escaped, and nothing else changed to mask it.
Run with `PYTHONDONTWRITEBYTECODE=1` and a cleared `__pycache__`; restored **in the same command**
so the tree could not be left mutated; `git status --porcelain` for that file confirmed **empty**
afterwards. Non-vacuity is asserted **first and structurally**: the two views of the *same*
record are asserted to derive *different* statuses before any claim about the derivation is made.

`_decide` gained one **defaulted** keyword (`per_finding=False`) so the one fixture carrying a
superseded row can pass a per-**finding** expected population — a correction and the row it
strikes share a `finding_id`, and a real emitted population is per finding, never per row. Every
pre-existing caller passes byte-identical arguments; no existing guard's behaviour moves.

**`DF-16-5-B` filed** (pure append): `tests/test_gate_independence.py` **962 → 1,127**, which
crosses §0.5's *"file an entry between 1,100 and 1,150"* band — the same pre-registered rule that
produced `DF-16-5-A`, firing as designed rather than being discovered later. **Not split** (1,127
< 1,150) and **not shaved** — the `-114` docstring carries the GUARD-ADEQUACY content the clause
requires, and that is named in the entry as the thing not to reclaim.

⛔ **Standing constraints re-verified after the fix:** `SECTION_5_CONDITIONS` still **7**;
`precision_evaluable` still **4** conjuncts; no `V1.4` row; `adjudication-record.json`
byte-unchanged; `gate_breadth.py:366-368` byte-as-shipped; `TC-ArgusAgent-DOCS-001-78` and
`ledger_closed_ids` **unamended and unweakened** (the record was wrong, not the guard); no
`_EXEMPT_BY_DESIGN` entry added; nothing ratified, no detector run, no disposition written, no
role filled; `DF-13-5-A` **OPEN and UNSPENT**.

**Gates, all re-run after the fix:** full suite `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` —
**1,688 passed**, exit **0** (1,686 + the 2 new `-114` cases) · `mypy argus` — **94 source files,
no issues** · `bandit -r argus --severity-level medium` — **0 medium / 0 high** ·
`tests/test_module_size_ceiling.py` — **6 passed**, no `_EXEMPT_BY_DESIGN` entry added ·
`scripts/build_gate_decision.py --check` **exit 0** · `scripts/build_adjudication_record.py
--check` **exit 0**.

---

## Dev Agent Record

### Agent Model Used

Claude Opus 5 (1M context) — `claude-opus-5[1m]`, via the BMAD `dev-story` workflow.

### Debug Log References

Baseline at HEAD `52143eb`, and ⛔ **it was RED — §0's next false premise, found on the first
command.** `TC-ArgusAgent-DOCS-001-78` reported **five** unbacked ledger-closure claims. Two
governance-record defects, neither of them a reason to touch the guard, both repaired in the arc's
first commit (`9aea1be`):

1. **`DF-15-2-D` really was CLOSED on 2026-08-22, with its date and its evidence — and the closure
   was MACHINE-INVISIBLE.** `ledger_closed_ids` recognises two shapes (the id ON the closure line,
   or a trailing `- status:` field) and the disposition was written as a `- **✅ CLOSED …**` bullet
   carrying neither. So this story's own TRUE Dev Notes claim read as unbacked. Repaired by the
   remedy the guard's own failure message prescribes: a **pure append** of the machine-readable
   field, closing nothing new. Verified by executing the analyzer: `DF-15-2-D` now resolves CLOSED;
   `DF-15-2-E`, `DF-16-1-A`, `DF-16-3-A` still resolve **open**.
2. **The round-1 validation report put four OPEN ids and one CLOSED id on ONE physical line**, and
   `story_closure_claims` is line-scoped **by design** — its docstring says widening the window
   *"swept unrelated ids into the claim"*. The table row was split in two; every word, cite and
   verdict preserved verbatim, no finding changed, and a dated note records the split and why.

⛔ **Everything else in §0 re-derived EXACT and nothing was amended.** 31 live rows · 26 FP / 5
BORDERLINE / 0 TP / 0 UNADJUDICATED · **exactly one** distinct adjudicator `"XAgent007 (Engineering
Lead)"` · `protocol_version` V1.3, `expert_hours` null · committed decision `BLOCKED`,
`precision.evaluable` / `fold_evaluable` false/false, breadth/seal/yield **false/false/true** ·
**ZERO** `adjudicators` assertions in `tests/**` or `scripts/**` · §0.2 confirmed (QA Lead FILLED
by `1bb7088`, External adjudicator UNFILLED, change-log head V1.3) · §0.6 next free ids confirmed
`-105` and `-80` · **both builders `--check` exit 0 at Task 0**, so AC7.4's stale-artifact trigger
did not fire · all §0.5 line counts exact (`gate_decision.py` 1,084 · `adjudication.py` 973 ·
`gate_seal.py` 777 · `gate_yield.py` 560 · `gate_breadth.py` 436 · `test_gate_seal.py` 1,145 ·
`test_vacuous_density.py` 1,159), measured with the ceiling guard's own `_physical_line_count`.

**Task 1 — the headroom decision, taken BEFORE the first line.** Projected and then measured:
`gate_decision.py` **1,084 → 1,132** (headroom 116 → 68). That is the **1,100–1,150 band**, so the
rule is *file a ledger entry*, **not** split — `DF-16-5-A`, a pure append. The four §2.3 forwarders
landed at **977 / 780 / 563 / 439** against the 1,200 ceiling, +4/+3/+3/+3 each, confirming §0.5's
stated projection rather than contradicting it: **no new NFR-M1 trigger, no split-first trigger
crossed, and no `_EXEMPT_BY_DESIGN` entry added** (registry still 3, and it may only shrink).

**AC7.1a byte-identity — PROVEN BY RENDERING, not by reading the diff.** `argus/` at `52143eb` was
extracted with `git archive` into a scratch tree and **26 surfaces** were rendered against both it
and the working tree with the keyword omitted — all three `precision_gate_status_for` branches
(plus the reasoned, corpus-noted and `precision=None` variants), the fold's `gate_status` /
`precision_ratio` / `evaluable` / `expert_hours_report` over the committed record on two
exhaustiveness paths, and each of the three arm renderers on BOTH its re-render and short-circuit
path. **sha256 `27dde086258766f56172f81cd21fa61e2129180a4bc9349f2cca3c184521b4d3` both times,
13,798 bytes, BYTE-IDENTICAL.**

**TEN mutations, all RED, at the real seam.** Every one executed with `PYTHONDONTWRITEBYTECODE=1`
and a cleared `__pycache__`, with the target file's sha256 verified **before and after** so the
restore is proven rather than assumed. `_derive_status`'s empty arm collapsed into
`NOT_INDEPENDENT` (RED on `-105` **and** `-110`) · the raising lookup replaced by a silent
`dict.get` default (RED `-105`) · the `cleared` branch dropping the note (RED `-106`) · the
`unevaluable` branch withholding the figure (RED `-106`) · a SECOND function emitting the
`precision=` surface, added to `gate_independence.py` itself (RED `-107`) · the
`sealed_precision_gate_status` forward dropped (RED `-108` **and green on `-109`**, which is what
proves the four branches are genuinely distinguished) · a FIFTH `precision_evaluable` conjunct (RED
`-109` **and** `-111`) · an EIGHTH `SECTION_5_CONDITIONS` member (RED `-111`) · the `independence`
payload key dropped (RED `-112`) · a DN-16-5-6-violating `independence_note` passed into the
dogfood renderer (RED `-112`) · the committed artifact hand-edited to
`EXTERNAL_ADJUDICATOR_PARTICIPATED` (RED `-113`). `git status --porcelain` clean after every one.

**Two re-arms found by execution, both handled as deliberate decisions rather than absorbed:**
`TC-ArgusAgent-RELEASE-001-11`'s test-tree-reach registry needed the new module (it joins
TRANSITIVELY through its single `adjudication` import and resolves no path at module level), and
`TC-ArgusAgent-PRECISION-001-94`'s **seal-citation rule** required an `Evidence-partition:` trailer
on the `feat` commit, because `argus/precision/replay_harness.py` is a declared detector-tuning
path. The trailer was **written, never the rule amended** — the guard says amending it *"is the
corpus-shopping failure mode with an extra step"*. Value: **`none`**, because no corpus evidence of
either partition informed this change. The three affected commits were rebuilt in place so the
trailer sits on the commit it describes and the dogfood artifacts cite the right provenance sha.

### Completion Notes List

**AC1 — DERIVED, never typed.** `argus/precision/gate_independence.py` (328 lines) owns the closed
four-member vocabulary, its raising `UnregisteredIndependenceStatus` lookup, the frozen
`IndependenceAssessment` with `to_payload()`, the pure `assess_independence` and the note renderer.
PURE (AR8): no I/O, no clock, no network, no module-level repository-only path — every input
arrives as an argument. The three role names are **destructured** out of
`PROTOCOL_ADJUDICATOR_ROLES`, so a fourth registered role fails at import rather than drifting; ids
are parsed by the **existing** `adjudicator_role`; the derived value is READ off the `adjudicators`
tuple `decide_gate` already computes and the record is never recounted. Import direction is one
way only. **AC1.6, re-derived by execution: `NOT_INDEPENDENT`, from 31 of 31 live human judgements
authored by `"XAgent007 (Engineering Lead)"`.** AC1.5 / `DN-16-5-4` lands in the *published
sentence* and is asserted there, not in a comment: the note says in its own words that it is a
claim about **this adjudication run** and not about §2's roster, *"which is not read here: a
registered role may be FILLED and have authored nothing on this record"* — because the QA Lead has
been filled since `1bb7088` and has judged nothing.

**AC2 — the two cannot be separated.** One optional keyword on `precision_gate_status_for`,
rendered in **all three** branches including the `cleared` one no production call site reaches
(`-106` drives 4 statuses × 3 branches = **12** renders and asserts both halves on every one).
`-108` drives all **four** renderer branches — `fold.gate_status`, and each arm renderer's
re-render path — **selected by construction**, over 3 statuses = **12** decisions, and asserts each
re-render **is** the arm renderer's own output rather than merely a different string. AC2.5's
structured block is on the committed payload under a new top-level `independence` key.

**AC3 — nothing is forked.** `-107` walks all `argus/**` modules (≥50 modules, ≥200 functions) and
finds **exactly one** function emitting the `precision=`/`N=` surface. The exclusion set is NAMED
and each excluded sentence is **asserted to still exist**, so "excluded" can never quietly become
"deleted". `negative_assurance.py` is byte-unchanged and `InstrumentStatus` is still closed at two.
The dogfood surface renders byte-identically and carries no clause, asserted by rendering.

**AC4 — nothing is gated, proven by execution.** `SECTION_5_CONDITIONS` is **SEVEN**,
`gate_conditions.py` byte-unchanged; `precision_evaluable` has **exactly four** conjuncts, COUNTED
out of the shipped AST rather than compared to a typed number; `_precision_condition` gains no
branch. `-109` flips the status through all three non-empty members over BOTH an otherwise-`CLEARED`
generated population and a `BLOCKED` one built from the real committed rows, and finds `outcome`,
`outcome_reason`, all seven condition verdicts, `precision_evaluable`, `meets_threshold` and the
closure path **byte-identical** — while asserting first that the *sentence* did move (so the
fixtures are not inert overall) and that the fixtures **differ only in the adjudicator field**.
AC4.3's `NOT_ESTABLISHED` exclusion is honoured and its **corrected** mechanism is what went into
the guard docstring: the population blocks on **EXHAUSTIVENESS**, ahead of the empty-denominator
branch and §5(4) — and `-110` asserts exactly that `outcome_reason` by measurement.

**AC5 — guards that cannot be vacuous.** `tests/test_gate_independence.py` (**new**, 962 lines),
`TC-ArgusAgent-PRECISION-001-105`..`-112`, plus `-113` in `tests/test_gate_decision_artifact.py`.
⛔ Nothing landed in `tests/test_gate_seal.py`, which is byte-unchanged at 1,145. Populations are
GENERATED with member spread, size, locators, rule ids and dispositions **pinned**, so the
adjudicator field is the only term that can move — and `_assert_differs_only_in_adjudicator`
asserts that **mechanically, row by row**, before any guard reasons about a difference. That is
§2.8's lockstep trap, which caught 16.1, 16.2 and 16.3 in turn. Every guard docstring discharges
GUARD-ADEQUACY (i)/(ii)/(iii) with its adversarial-variant **count** stated, and (ii) is discharged
by the ten executed mutations above rather than by assertion.

**AC6 — the records.** Protocol §2 gained a **fifth dated block under V1.3** (57 insertions, **0**
deletions — no `V1.4` row, no existing byte edited). `architecture.md` §Enforcement gained a dated
addition to *Gate-decision enforcement* (6,053 bytes added, **0** removed; the original line is a
verbatim prefix of the new one). `deferred-work.md` took **two pure appends** (0 deletions):
`DF-16-5-A` and the `DF-15-2-D` machine-readable status field. **AC6.5 answered explicitly:** a
rendered surface DID move — `TC-ArgusAgent-DOCS-001-54`'s published module figures — so `README.md`
and `CHANGELOG.md` were updated with the four figures the new module moved (importable and shipped
modules 93→94, wheel entries 101→102, sdist members 100→101), each derived from a freshly built
wheel. No FR34 surface moved.

**AC7 — scope.** The AC7.1 must-not-move list is **byte-unchanged against `52143eb`**: `git diff
--stat 52143eb HEAD` over all 20 fenced paths returns **nothing**. The AC7.1a budget holds exactly:
`adjudication.py` **+4/-0**, `gate_breadth.py` **+3/-0**, `gate_seal.py` **+3/-0**, `gate_yield.py`
**+3/-0** — one optional keyword, one forward to the one existing call, one docstring line, **zero**
deletions, no second parameter, no `__all__` change and **no `gate_independence` import in any of
the four**. ⛔ `gate_breadth.py:366-368`'s shipped `DN-16-1-1` sentence is **byte-as-shipped**
(sha256 `20d3b1f18a74c555` at `52143eb` and at HEAD): `DN-16-5-7` was read, the conflict was
recognised as already adjudicated, and correcting the docstring was **not** done because the
operator declined it.

⛔ **Nothing operator-owned was touched.** No bench member ratified, no third-party repository
fetched, no detector run over a member, no disposition written, no role filled, no threshold moved,
`precision-validation-protocol.md`'s existing bytes unedited. `N` stays 5, the seal stays closed,
`protocol_cleared` stays `False`, `adjudication-record.json` is byte-unchanged, no `V1.4` row, and
**`DF-13-5-A`'s one pre-registered round stays OPEN and UNSPENT.**

**Gates (AC7.3), each run and each number recorded.** Full suite with
`ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`: **1,686 passed, 0 failed, exit 0 (248s)**. `mypy argus`: **Success, no
issues in 94 source files**, exit 0. `bandit -r argus --severity-level medium`: **0 medium, 0
high** (20 low, below the threshold), exit 0. `scripts/build_gate_decision.py --check`: **exit 0**.
`scripts/build_adjudication_record.py --check`: **exit 0**. `tests/test_module_size_ceiling.py`:
green, **`_EXEMPT_BY_DESIGN` still 3 entries — no entry added**.

⛔ **Two things a reviewer should look at first**, because they are the judgement calls: (1) the
two governance-record repairs in `9aea1be`, which are edits this story's AC7.2 did not anticipate —
they were forced by a RED baseline and both are strictly additive or verbatim-preserving; and (2)
the `Evidence-partition: none` trailer, which is a claim about this change that only a reader of
the diff can falsify.

### File List

**New**

- `argus/precision/gate_independence.py` (328)
- `tests/test_gate_independence.py` (962 at implement; **1,127** after review fix round 1 —
  `-114` and its `_superseded_population` builder; `DF-16-5-B` filed for the band)

**Modified — `argus/`**

- `argus/precision/gate_decision.py` (+56 / -8; 1,084 → 1,132)
- `argus/precision/replay_harness.py` (+29 / -3; 825 → 851)
- `argus/precision/adjudication.py` (+4 / -0; 973 → 977) — AC7.1a budget
- `argus/precision/gate_breadth.py` (+3 / -0; 436 → 439) — AC7.1a budget
- `argus/precision/gate_seal.py` (+3 / -0; 777 → 780) — AC7.1a budget
- `argus/precision/gate_yield.py` (+3 / -0; 560 → 563) — AC7.1a budget

**Modified — `tests/`**

- `tests/test_gate_decision_artifact.py` (+81 / -0; 451 → 532) — `-113`
- `tests/test_release_preflight.py` (+12 / -0) — the deliberate test-tree-reach registration

**Modified — records and artifacts**

- `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/gate-decision-record.json`
  *(REGENERATED by `scripts/build_gate_decision.py`, never hand-edited)*
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md`
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md`
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md`
  *(all three REGENERATED by `scripts/regenerate_dogfood_artifacts.py`, in the §2.5 order)*
- `_bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md` *(dated block, +57/-0)*
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md` *(dated addition, 0 bytes removed)*
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` *(implement round: two pure
  appends. **Review fix round 1: the `\r` byte at `:5257` RESTORED and the EOF newline restored,
  plus `DF-16-5-B` appended** — the whole arc now audits as `HISTORICAL LINES DELETED OR
  REPLACED: 0` against `52143eb`)*
- `README.md` · `CHANGELOG.md` *(published module figures, AC6.5)*
- `_bmad-output/design-artifacts/ArgusAgent/stories/16-5-the-record-says-who-judged-and-whether-they-were-independent-validation-2026-08-23.md`
  *(one table row split; every word preserved, no finding changed)*
- `_bmad-output/design-artifacts/ArgusAgent/stories/16-5-the-record-says-who-judged-and-whether-they-were-independent.md` *(this file)*
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`

**Byte-unchanged and asserted so** — every path on AC7.1's list, verified by
`git diff --stat 52143eb HEAD`.

### Change Log

| Date | By | Change |
|---|---|---|
| 2026-08-23 | dev-story (Opus 5, **review fix round 1**) | **Addressed code review findings - 2 of 2 items resolved; `in-progress` -> `review`.** ⛔ **`argus/**` and `scripts/**` byte-unchanged by this round**, so §2.5's artifact-currency order is not re-armed and `gate_decision.py` stays at 1,132. **Finding 1 (Patch, High - AC6.4 append-only)** - the literal `\r` byte `9aea1be` dropped from the historical `deferred-work.md:5257` entry is **RESTORED**, the remedy 16.1's review set. The audit went well past the one byte: a byte-level `difflib` alignment of **every blob in the arc** (`52143eb`→`9aea1be`→`c5ca6a7`→`cd4cbe4`→`ca0dee2`→`927548d`→`028c3c8`) plus a whole-file baseline comparison found **exactly ONE change in the entire arc that modified a pre-existing line - that CR** - with every other change a pure INSERT (22 lines, the `DF-15-2-D` `status:` field; 45 lines, `DF-16-5-A`) and four commits not touching the file at all. Proven twice: the alignment reports `HISTORICAL LINES DELETED OR REPLACED: 0`, and the 424,300-byte baseline was **reconstructed byte-exactly** by removing only the inserted ranges. ⛔ **Root cause found and it is a trap, not a slip:** `core.autocrlf=true` with no `.gitattributes`, and **a lone CR makes git classify the file as binary**, silently disabling CRLF normalisation - so an editor rewriting the file as CRLF consumed the lone CR, after which git resumed normalising and booked one net deletion. **The fix's own first attempt hit the same trap in reverse** (restoring the CR into a CRLF worktree would have staged 5,643 CRLF terminators), so the restoration was rebuilt **from the blob**; `worktree bytes == staged blob bytes` asserted. Also **restored the EOF newline** `927548d` dropped - not a historical-byte edit, but a POSIX violation on an ubuntu CI matrix - reported rather than absorbed. ⛔ `TC-ArgusAgent-DOCS-001-78` and `ledger_closed_ids` **unamended and unweakened**: the guard was right, the record was wrong. **Finding 2 (Patch, Medium - AC1.3/AC5.4 guard adequacy)** - NEW **`TC-ArgusAgent-PRECISION-001-114`** with a `_superseded_population` builder extending `_population` (every pinned term inherited, §2.8 lockstep preserved), striking one row by a real `supersedes` correction whose author differs **in role** from the live replacement. **2 GENERATED variants**, one per registered non-Engineering-Lead role, each forging a *different* status - exactly the "quietly upgrading a `NOT_INDEPENDENT` record" leak the review named. ⛔ **Proven non-vacuous by the reviewer's own mutation**: `gate_decision.py:856` `live_rows()`→`rows` drives **both** `-114` cases RED while every other guard in the four targeted files stays green; run under `PYTHONDONTWRITEBYTECODE=1` with cleared `__pycache__`, **restored in the same command** so the tree could never be left mutated, `git status --porcelain` empty after. `_decide` gained one defaulted `per_finding` keyword (a correction shares a `finding_id` with the row it strikes; a real emitted population is per finding, never per row) - every pre-existing caller byte-identical. **`DF-16-5-B` FILED** (pure append): `tests/test_gate_independence.py` **962 → 1,127**, crossing §0.5's 1,100-1,150 filing band - not split (< 1,150), **not shaved** (the `-114` docstring carries mandated GUARD-ADEQUACY content). ⛔ Re-verified after the fix: `SECTION_5_CONDITIONS` still **7**, `precision_evaluable` still **4** conjuncts, no `V1.4` row, `adjudication-record.json` byte-unchanged, `gate_breadth.py:366-368` byte-as-shipped, no `_EXEMPT_BY_DESIGN` entry, nothing ratified, no detector run, no disposition written, no role filled, `DF-13-5-A` **OPEN and UNSPENT**. Gates: full suite **1,688 passed exit 0** · `mypy argus` 94 files clean · `bandit` 0 medium/0 high · ceiling 6 passed · both builders `--check` exit 0. |
| 2026-08-23 | dev-story (Opus 5) | **IMPLEMENTED; `ready-for-dev` -> `in-progress` -> `review`.** Six commits on the Epic-16 arc. **The derived answer over the live record is `NOT_INDEPENDENT`** - 31 of 31 live human judgements by `"XAgent007 (Engineering Lead)"` - and it now rides **on the `gate_status` sentence itself**, after the precision figure, in all three renderer branches and on all four renderers `precision_gate_status` can return, plus a structured `independence` payload block. NEW `argus/precision/gate_independence.py` (328) and `tests/test_gate_independence.py` (962, `-105`..`-112`), plus `-113` in `test_gate_decision_artifact.py`. **NOTHING IS GATED and it is proven by execution:** `SECTION_5_CONDITIONS` still **7**, `precision_evaluable` still **4** conjuncts (counted out of the shipped AST), and flipping the status through all three non-empty members leaves outcome, reason, all seven verdicts, `precision_evaluable`, `meets_threshold` and the closure path byte-identical over BOTH an otherwise-`CLEARED` and a `BLOCKED` population. **AC7.1a held exactly** - the four forwarders are +4/+3/+3/+3 with **zero** deletions - and NFR-P1 was **proven by rendering**: 26 surfaces, sha256 `27dde086258766f5`, byte-identical against the pre-story tree. **TEN mutations, all RED**, at the real seam, tree restored byte-exact after each. **§0's next false premise, FOUND: the Task-0 baseline was RED**, not green - `TC-ArgusAgent-DOCS-001-78` on two governance-record defects (a machine-INVISIBLE but real `DF-15-2-D` closure, and a line-scoped analyzer sweeping four OPEN ids off one table row), both repaired additively without touching the guard. `gate_decision.py` **1,084 -> 1,132** landed in the 1,100-1,150 band, so **`DF-16-5-A` was FILED, not split** - the rule firing as designed. Two re-arms handled as decisions, not absorbed: the test-tree-reach registry, and the seal-citation rule, answered with `Evidence-partition: none` on the `feat` commit. ⛔ **`gate_breadth.py:366-368` left byte-as-shipped** (`DN-16-5-7` read, correction declined by the operator). ⛔ Nothing ratified, no detector run, no disposition written, no role filled, no threshold moved, no `V1.4` row, `adjudication-record.json` byte-unchanged, `DF-13-5-A` **OPEN and UNSPENT**. Gates: full suite exit 0 · `mypy argus` 94 files clean · `bandit` 0 medium / 0 high · both builders `--check` exit 0 · ceiling guard green with **no `_EXEMPT_BY_DESIGN` entry added** (still 3). |
| 2026-08-22 | create-story (Opus 5) | Story contexted at HEAD `52143eb`; `backlog -> ready-for-dev`. |
| 2026-08-23 | validate (read-only) | Story-readiness validation returned **FAIL**. Every §0 figure re-derived **CLEAN**; 3 BLOCKING + 4 minor findings, all in the ACs. Report: `...-validation-2026-08-23.md`. No file modified. |
| 2026-08-23 | create-story (amendment mode) | **Seven targeted edits. No re-contexting, no re-research, no scope change, status stays `ready-for-dev`.** **B-1** — AC2.3 was unsatisfiable inside AC7.1's fence (none of its four renderers lives in `gate_decision.py`; the three arm renderers short-circuit). `gate_breadth.py` / `gate_seal.py` / `gate_yield.py` moved **AC7.1 -> AC7.2**, joined by `adjudication.py`, under a new **AC7.1a one-forwarded-keyword budget**; §2.3 rewritten with the measured call sites; Task 1's projection extended over all four (**no new NFR-M1 trigger**); §0.5 gained their rows; Tasks 1/4 and AC2.3 restated. **B-2** — AC4.3 contradicted AC5.3: scoped the inertness sweep to the **non-empty** members and recorded §5(4)'s pre-existing `adjudicators` coupling (`gate_decision.py:626-690`, `:1021`, `:977`) as a **found fact**; AC5.3 clarified. **B-3** — *"Nothing in the repository reads it"* measured **FALSE**; reframed as **"unguarded by any test"**, `_recorded_cleared_condition` added to §0.7, §0.1 callout and §1.1 qualified. **M-1** artifact root qualified once in §0.0. **M-2** `replay_harness.py:788`'s `registry_module()` indirection marked deliberate and out of scope. **L-1** `epics.md` cite `:3191` -> `:3199`. **L-2** AC3.1's walk exclusion set named. ⛔ **No `DN-*` overturned; `SECTION_5_CONDITIONS` still 7; `precision_evaluable` still 4 conjuncts; no `argus/`, `tests/` or `scripts/` file touched.** |
| 2026-08-23 | validate (read-only, **round 2**) | Story-readiness validation returned **CONCERNS** — implementable, two items to fix. **All three round-1 blockers confirmed GENUINELY RESOLVED**, re-derived against the tree rather than against the amendment's claims; the AC7.1a forwarding budget survived adversarial scrutiny including the compatibility check (**no shipped guard closes over the signatures or call kwargs of the four widened modules**); **all 21 rows of §0.5 re-measured EXACT**; all invariants intact. `C-1` un-rebutted `DN-16-1-1` conflict, `C-2` measurably wrong AC4.3 mechanism, plus `L-1`..`L-4`. Report: `...-validation-2026-08-23-round-2.md`. No story byte, source byte or sprint-status value changed. |
| 2026-08-23 | create-story (amendment mode, **2nd pass**) | **Six targeted edits. No re-contexting, no re-research, no scope change, status stays `ready-for-dev`.** **C-1** — NEW **`DN-16-5-7`** (**OPERATOR-AUTHORISED**), recording BOTH halves: `DN-16-1-1`'s stated rationale (*"a signature shared with the cartridge path"*, shipped at `gate_breadth.py:366-368`) is **FALSE as applied to the fold** — re-verified: `fold_adjudicated_precision` has **exactly one** production caller (`gate_decision.py:811`), and `compute_precision` returns **`PrecisionResult`** (`replay_harness.py:386`) without calling it; what the two paths actually share is `precision_fraction` (`replay_harness.py:291`, its own docstring at `:296`) and `precision_gate_status_for` (`:729`) — **not the fold** — WHILE `DN-16-1-1`'s **holding** (*the fold is not forked*) **STANDS UNREVERSED**, since one inert byte-identical-defaulted keyword is not a fork. Cross-referenced from the *"CITES rather than reopens"* list and carved out of **AC7.4** as a named, already-adjudicated non-trigger. ⛔ **`gate_breadth.py:366-368` deliberately LEFT AS SHIPPED — correcting it was considered and DECLINED; `DN-16-5-7` lives in this story only.** **C-2** — AC4.3 limb 2 (and its AC5.3 repeat) ordered a **measurably wrong mechanism** into a guard docstring *as a found fact*: re-verified that `AdjudicationRow.__post_init__` (`adjudication.py:376-377`) refuses any TP/FP/BORDERLINE row without a registered adjudicator, so an empty adjudicator set implies **all live rows UNADJUDICATED** -> record **NON-EXHAUSTIVE** -> `decide_gate` blocks at **`:956` on exhaustiveness, AHEAD of** the empty-denominator branch at `:977`; limb 2 restated and cite **`:1021` -> `:1022`** (`:1021` is `closure = yield_closure_path(...)`). ⛔ **AC4.3's scoping decision is correct and UNTOUCHED.** **L-1** §0.5 prose `640` -> **`560`** (`gate_yield.py`'s headroom had been transcribed as its line count; the table row and Task 1 were already right). **L-2** Task 4 + AC7.2 now state that the `live`/`adjudicators` derivation at `:820-823` must **move ABOVE** the fold call at `:811` — a **re-order**, not a one-line forward. **L-3** §0.0 / Task 0 working-tree expectation now reads *"plus this story's validation reports"* (**four** entries, not two). **L-4** Task 4's byte-identity confirmation list gained the three direct `precision_gate_status_for` callers — `tests/test_gate_flip_path.py`, `tests/test_precision_replay.py`, `tests/test_validation_corpus.py`. ⛔ **No `DN-*` overturned; `DN-16-5-4`/`DN-16-5-5` untouched; `SECTION_5_CONDITIONS` still 7; `precision_evaluable` still 4 conjuncts; no eighth §5 condition; no `argus/`, `tests/` or `scripts/` file touched.** |
| 2026-08-23 | code-review (Sonnet 5, iteration 1) | **FAIL — two Patch findings, `review -> in-progress`.** Re-ran every claimed gate independently (full suite 1,686/1,686, `mypy` 94 files clean, `bandit` 0 medium/high, both builders `--check` exit 0, ceiling guard green) and four targeted mutation spot-checks, each restored (`git status --porcelain` clean after every one): a fifth `precision_evaluable` conjunct — RED; the raising vocabulary lookup replaced by a silent default — RED; the byte-identical-when-omitted default widened to inject text — RED on both a new and a pre-existing guard; `decide_gate`'s `record.live_rows()` replaced by `record.rows` — **RED on nothing** (finding below). Confirmed clean: `AC7.1`'s must-not-move list byte-unchanged, `AC7.1a`'s budget exactly +4/+3/+3/+3 with no `gate_independence` import in the four forwarders, `gate_breadth.py:366-368` byte-as-shipped, the protocol edit +57/-0 under V1.3 with no `V1.4` row, `gate_decision.py` 1,132 with `DF-16-5-A` filed not split, the README/CHANGELOG module-figure claims verified against a real build. Two findings written to Review Findings above: (1) **Patch, High** — the Task-0 baseline-repair commit (`9aea1be`) silently dropped a literal `\r` byte from a historical, pre-16.5 `deferred-work.md` entry while its own commit message and new `status:` field claim "not one byte of the entry above it is edited" — a real AC6.4 (append-only) violation the diff itself falsifies (`24 insertions(+), 1 deletion(-)`), recurring inside the very commit this story flagged as its own highest-value review target. (2) **Patch, Medium** — no generated population in `tests/test_gate_independence.py` exercises a superseded row, so nothing in the targeted guard surface catches `decide_gate` deriving independence from all rows instead of live rows only — a guard-adequacy gap against AC5.4, not a live mis-derivation (0 superseded rows on the committed record today). Neither finding is `decision-needed`; both have unambiguous fixes. Nothing operator-owned was touched by this review: no ratification, no detector run, no disposition written, no role filled, no `V1.4` row, seal unopened, `DF-13-5-A` still OPEN and UNSPENT. |
