# Successor-predicate precision criterion — PRE-REGISTRATION

| field | value |
|---|---|
| **Date** | **2026-08-25** |
| **Registered by** | **Engineering Lead** (Epic 17 / Story 17.1), recorded by the dev-story workflow |
| **Epic / Story** | Epic 17 — *Say What The Assertion Constrains* / Story 17.1 — *Write down what would count as precision, before the number exists* |
| **Criterion as code** | `scripts/precision_preregistration.py` |
| **Guards** | `tests/test_precision_preregistration.py` — `TC-ArgusAgent-PRECISION-001-135`..`-141` |
| **Adjudication protocol in force** | `PROTOCOL_VERSION` — **named**, not created (see §4) |
| **Status of the externalization gate** | `BLOCKED`, and this document moves it nowhere (see §3) |

> **⚠ EVERY VALUE IN THIS DOCUMENT IS CITED BY CONSTANT NAME, NOT COPIED.** `AI-E9-7`: a prose
> copy of a pinned constant is a second source of truth that drifts silently, and this project has
> already paid for one (`DF-8-5-C`). Where a number is pinned in code, the constant is named here
> and the reproduction command is given, so a reader gets the value from the same place the
> arithmetic does. Nothing below is a hand-written figure that can go stale inside its own
> document.

---

## 1. What this is, and why the date is the point

A **pre-registration** is a criterion committed to the object database **before** the measurement
it will judge exists. Its entire value is the **order**. A threshold chosen once the result is in
view is not a threshold — it is a description of the result, written in the grammar of a standard.

Epic 17 is about to move the verdict-eligible population of the vacuous-test detector from **zero**
to something. This document, and the module it describes, write down what *"good enough"* means
**while the answer is still zero**. No successor predicate exists. No finding of the class this
criterion will judge exists. There is nothing yet to be tempted by.

The precedent is this project's own. On **2026-08-17** — before Story 13.5 ran, before Epic 15's
bench was chosen, before any number existed — it recorded that *"we pursue ONE bench-expansion
round … if precision lands below 80% we take option (b)."* That rule is worth something for
exactly one reason: nobody knew the answer when it was written. This is the same act, one level
down. Story 15.1 performed it one level up, in `scripts/candidate_selection.py`.

**The criterion is frozen as CODE, not as prose.** Prose is not falsifiable; a module walked by an
AST guard is. Seven guards make each claim below fail loudly rather than be asserted:

| guard | what it makes falsifiable |
|---|---|
| `-135` | the ratio floor and the three resolution floors are **resolved**, never re-typed |
| `-136` | the exposure ceiling **re-derives** from its pinned blob |
| `-137` | the ceiling is **not redundant** with the ratio — both arms watched failing |
| `-138` | a thin or narrow population is `UNEVALUABLE`, **never** `MET` |
| `-139` | the ordering claim, checked against **real git history** |
| `-140` | the criterion's **directional** immutability — strengthening only |
| `-141` | the structural ban: this module cannot look, cannot fetch, cannot write |

---

## 2. The criterion

### 2.1 The population — `POPULATION_ID`, `POPULATION_DERIVATION`, `POPULATION_SOURCE_ARTIFACTS`

The criterion is measured over the `vacuous_test_heuristic` findings recorded for the **five
already-ratified repository-corpus members at their pinned shas** — `minions`, `agent-smith`,
`agent-markovich`, `xagents-webapp`, `ai-body-runtime`. Not a new bench, not a sealed candidate,
not the open partition.

`POPULATION_DERIVATION` states how the count is reached and `POPULATION_SOURCE_ARTIFACTS` names the
two committed artifacts it re-derives from. It re-derives from **both**, independently, and that is
the point: one artifact is a claim, two that agree is a measurement. Nothing was run to produce it
— a re-measurement would be a detector run this story is forbidden.

`ai-body-runtime` contributes **zero** findings of this class and is still part of the population.
A member that contributes nothing is a member the ratio was measured over, not a member quietly
dropped from the denominator.

**Rejected:** including any **sealed** candidate. That requires a protocol §6 **R2** ratification,
which is an operator act, spends `DF-13-5-A`, and is forbidden to this story and to Story 17.4
alike.

### 2.2 The ratio floor — `precision_floor()`

The criterion's ratio floor **is protocol §5's own locked threshold**, resolved by calling
`precision_floor()`, which returns `replay_harness.PRECISION_GATE_THRESHOLD` — the exact
`Fraction` object itself. It is never re-typed as a decimal, never reconstructed from a numerator
and a denominator, never rendered as a percentage string. `-135` walks the module's AST and fails
on any numeric literal equal to it.

**Rejected:** a story-local, lower *"Story 17.4 acceptance threshold."* A second threshold is
precisely how this project came to have two corpora (`DN-3`), and a threshold set below the gate's
own is a threshold chosen to be passable. If the successor cannot reach the number the gate
already requires, that is a **result**, not a calibration problem.

### 2.3 The three resolution floors — `resolution_floors()`

A ratio alone is satisfiable by a tiny denominator, and that is the **downward** half of the
exposure question. It is answered by **resolving three floors that already exist** rather than by
authoring any:

| floor | resolved from | answers |
|---|---|---|
| verdict-eligible population | `gate_yield.verdict_eligible_population_floor(precision_floor())` | the smallest denominator at which *"≥ 80%"* is not silently *"100%"* |
| distinct contributing members | `gate_breadth.contributing_member_floor(N)` | a score drawn from one repository is not a score |
| sealed contributing members | `gate_seal.sealed_member_floor(N)` | …and they must be members the tool was never tuned against |

`N` is reached through `replay_harness.corpus_manifest_module()` — the **one** declared lazy edge
to the repository-only manifest (`DF-9-2-A`), the same edge `gate_decision` uses. The last two
floors are the **same derived number reached two ways**, deliberately: `sealed_member_floor` calls
`contributing_member_floor` (`DN-3` — one floor, never forked).

**A population failing any one of the three is `UNEVALUABLE`.** That name is resolved from
`gate_conditions.CONDITION_VERDICTS`, not typed: the module looks it up in the imported vocabulary
at import time and **fails to import** if §5's terminal states are ever changed underneath it. No
new terminal state is invented here — `CONDITION_VERDICTS` stays closed at four and `GATE_OUTCOMES`
closed at three.

### 2.4 The false-accusation exposure ceiling — `MAX_FALSE_ACCUSATION_EXPOSURE`

This is the **upward** half, and the one genuinely new quantity this story lands. Eighty percent of
a thousand findings is two hundred wrong accusations, and a ratio cannot see that. The criterion
therefore carries an **absolute integer cap** on adjudicated false positives, evaluated **jointly
with, and independently of**, the ratio.

**The rule, stated:**

> The successor may not, over the pinned population, produce more adjudicated false accusations
> than **this instrument's entire recorded false-accusation history**.

That history is `EXPOSURE_SOURCE_PATH` read at `EXPOSURE_SOURCE_SHA` — a full 40-character
lowercase pin, which is an **ancestor of HEAD**. Reproduce the derivation:

```
git show <EXPOSURE_SOURCE_SHA>:<EXPOSURE_SOURCE_PATH>
```

and count the rows whose `disposition` is `FP`. Every row in that record carries `rule_id`
`vacuous_test_ast`, was judged by a **named human** under the protocol version in force, and the
record contains **zero** true positives across its whole life. `EXPOSURE_CEILING_DERIVATION` states
this in the module's own words, beside the number, in the `YIELD_FLOOR_DERIVATION` house form.
`-136` performs the re-derivation on every run rather than trusting the literal.

**Why this derivation and not a preference.**

1. It is **measured and committed**, not invented. The project put its blocking findings in front
   of a human once, and most came back false. Nothing about that is negotiable after the fact.
2. It **reproduces from a pinned blob**, so a guard can prove the derivation instead of trusting a
   literal.
3. It **bites without being a shutdown.** At the largest known candidate reach the ratio binds
   first; above roughly 130 verdict-eligible findings the ceiling becomes the binding constraint.
   Protocol §5 refuses both *"a condition that cannot fail"* and a floor that *"would make
   `CLEARED` unreachable by construction."* This sits between them.

**It is FROZEN AS A LITERAL, and this is the one place a literal is right** (`DN-17-1-4`). The
module says so on the line: **the record grows** — Story 17.4 appends to it — so a ceiling resolved
live would move the moment the number it judges came into view. That is the exact defect this
story exists to prevent.

#### The rejected ceilings — `REJECTED_EXPOSURE_CEILINGS`

Recorded in code as well as here, so the next author cannot re-propose one as though it were new:

| rejected ceiling | why not |
|---|---|
| `floor(yield_floor × (1 − threshold))` | At a target population of ~125 it demands better than 99% precision. That is a **shutdown**, which §5's own rule-class reasoning refuses. |
| the verdict-eligible population floor itself | The same failure, less obviously — a handful of permitted false accusations over a population two orders of magnitude larger is a shutdown wearing a derivation. |
| **48**, from `DF-16-7-B`'s *"what the moat is worth here"* | Nearly twice the measured exposure. It could not bite at any reachable population, and a condition that cannot fail is not a threshold. |
| a **percentage** of the population | That is the ratio again wearing a different hat. An absolute is asked for precisely because a proportion cannot see unbounded harm behind a good ratio. |
| **resolved live** from the adjudication record | The record grows; Story 17.4 appends to it. A criterion that moves once the number is in view is not a criterion. |

#### The strengthening-only asymmetry — `STRENGTHENING_ONLY_ASYMMETRY` (`DN-17-1-6`)

The operator may **LOWER** `MAX_FALSE_ACCUSATION_EXPOSURE` and may **RAISE** the ratio floor, at
any time, without reopening this pre-registration. **Neither may move the other way** once
`PREREGISTRATION_COMMIT_SHA` exists.

This is the same asymmetry that lets protocol §5 be amended by dated addition: an amendment is
permitted precisely because it can only make clearing **harder**. `-140` enforces the direction
against the pinned blob — `ceiling ≤ ceiling_at_pin` and `ratio ≥ ratio_at_pin`, with
`POPULATION_ID` and `PROTOCOL_VERSION` **equal** — so a loosening is a **red test** rather than a
diff nobody reads. `PREREGISTRATION_COMMIT_SHA` itself is excluded from the frozen field set, since
the commit that records it legitimately writes it.

⚠ **The ceiling is an Engineering Lead act of the same class as the 2026-08-17 rule** (taken by
XAgent007). It lands here **with its derivation and its rejected alternatives** and is **raised for
ratification** in Story 17.1's record. It may be strengthened thereafter and never loosened.

### 2.5 The fold — `evaluate()` → `CriterionAssessment`, and `CRITERION_OUTCOMES`

`evaluate()` is a pure fold: a candidate population's counts in, one registered outcome plus **the
counts that produced it** out. A bare verdict is unauditable — `NOT_MET` with no counts cannot be
told apart from `NOT_MET` measured over four findings.

**The order is the protocol's, not a convenience:**

1. **the three resolution floors**, before any ratio is looked at — exactly as
   `adjudication.fold_adjudicated_precision` evaluates reproducibility and exhaustiveness before it
   will report a figure;
2. **the denominator** — an empty adjudicated population is `UNEVALUABLE`, never a flattering
   `100%` (`AI-E11-1`; measured at `bc55e36`, where a corpus that emitted nothing reported a
   cleared gate);
3. **the two joint conditions** — the ratio floor **and** the absolute ceiling, each able to
   produce `NOT_MET` on its own.

`CRITERION_OUTCOMES` is closed at three — `MET`, `NOT_MET`, `UNEVALUABLE` — in `GATE_OUTCOMES`'
shape: a mapping from the outcome to what it **means**, so a caller cannot render one without the
sentence that qualifies it. An unregistered outcome raises.

---

## 3. ⛔ What this criterion judges — and what it does NOT

### 3.1 It judges the successor predicate. It does not judge the gate. (`DN-17-1-5`)

**Measured at pre-registration time, the intersection of the SEALED partition and the RATIFIED
members is EMPTY.** All five ratified members are `pre-seal`; every member in the `sealed`
partition is `eligible_for_n = False`. Against `sealed_member_floor`, protocol §5's
`gate-evidence-drawn-from-the-sealed-partition` condition therefore reads **FAILED** over the very
population a successor will be measured on — **today**, before any successor exists.

Only a protocol §6 **R2** operator act ratifying sealed members could change that, and **no Epic 17
story may take one.**

> **⛔ THE EXTERNALIZATION GATE CANNOT REACH `CLEARED` FROM THIS MEASUREMENT, AT ANY RATIO.**
> *"Precision came out at 84%, so the gate clears"* is **FALSE**, and it is written down here
> before anyone has a number to say it about.

The gate stays `BLOCKED`. `protocol_cleared` stays `False`. The ≥80% keystone stays **NOT
CLEARED**. FR34's disclosure stands. This document creates no §5 condition and changes none.

### 3.2 ⛔ Both known candidate successors draw from TWO contributing members

Measured from `validation-corpus/silent-class-record.json` at this story's HEAD, and from the
2026-08-24 stage-mismatch measurement:

| candidate | definition | contributing members | breadth verdict |
|---|---|---|---|
| shipped (`V0`) | `disc ≥ 1 ∧ cons == 0 ∧ mref ≥ 1` | none — population empty | no population |
| `V1` drop-mref | `disc ≥ 1 ∧ cons == 0` | **2** — `minions`, `agent-smith` | ⛔ **`UNEVALUABLE`** |
| `V2` silent | `disc ≥ 1 ∧ the span asserts nothing` | **2** — `agent-smith`, `minions` | ⛔ **`UNEVALUABLE`** |
| `V5` unrelated | `disc ≥ 1 ∧ asserts, none about the SUT` | not measured per member | unknown |

Against the resolved contributing-member floor, **each of the two candidates whose per-member
distribution is known today returns `UNEVALUABLE` on breadth as it stands.**

**This is the most valuable pre-registered sentence available to this story.** `UNEVALUABLE` is a
recorded failure to evaluate — not a pass, not a fail, and **not an invitation to argue the floor
down**. Written now it is discipline; written after Story 17.4 reports it, it is a concession.
`-138` drives the fold at exactly that measured shape.

### 3.3 The named consequence of falling below — `CONSEQUENCE_BELOW`

> **If, over the pinned population, the successor's measured precision is below the resolved ratio
> floor, OR its adjudicated false accusations exceed `MAX_FALSE_ACCUSATION_EXPOSURE`, OR the
> population is `UNEVALUABLE` under any of the three resolution floors — the successor predicate is
> NOT promoted to verdict-eligible.**
>
> It ships **advisory-only**. The `consumed == 0` asymmetry and the conservative default stay
> exactly as they are; the FR34 disclosure stands; the gate stays `BLOCKED`. The next attempt
> requires **a different predicate — not a bigger bench and not a loosened clause.**

⛔ **`DF-13-5-A` is NOT spent by that outcome and its branch (b) is NOT declared by it.** That
entry's pre-registered conditions are *zero blocking findings* or *precision below 80%* **over a
spent round**, and Story 17.4 spends no round, ratifies no member and fetches no source.
`DF-13-5-A` stays **OPEN and UNSPENT** either way. Its 2026-08-24 trigger is **Story 17.4's** to
evaluate, by name, and is not evaluated here.

### 3.4 …and the converse — `CONSEQUENCE_MET`

> **Meeting this criterion promotes nothing and moves no gate condition.**

It produces a recorded, evidenced **proposal** to promote. Promotion is an operator act. This half
is stated because it is the half that gets misread.

### 3.5 A stated precondition for the measurement itself — `AI-E16-7`

Protocol §4's **External adjudicator** tie-break role is **UNFILLED**. Story 17.1 adjudicates
nothing and does not need it. **Story 17.4 does.** It is recorded here as a stated precondition
rather than left to be discovered when the ladder needs its third rung.

---

## 4. ⛔ What this act does NOT do — stated in terms, not by implication

Each clause below is a sentence somebody would otherwise omit.

1. **No corpus member is ratified.** `eligible_member_count()` is what it was before this act and
   what it is after. Selecting or admitting a member is a protocol §6 R2 operator act.
2. **No third-party source is fetched.** Protocol §6 R2, verbatim: *"choosing which repositories
   are legitimate members, and fetching third-party source, are not autonomous acts."* Nothing here
   reaches the network; `-141` enforces that structurally over the module's AST.
3. **No bench-expansion round is spent.** `DF-13-5-A` remains **OPEN and UNSPENT**; its branch (a)
   is not executed and its branch (b) is not declared.
4. **No protocol row is added and no §5 condition is created.** `PROTOCOL_VERSION` **names** the
   version in force; it does not create one. `precision-validation-protocol.md` is
   **byte-unchanged**. A new version row would re-stamp `protocol_version` across every committed
   human judgement in the adjudication record, and *"a decision folded across an amendment is a
   re-interpretation of judgements nobody re-made"* (locked operator decision, 2026-08-20). The
   module **refuses** a version that is not the change-log head — `refuse_protocol_drift()` — and
   the remedy for that refusal is never to edit the constant to agree.
5. **No FR is amended.** **No finding becomes verdict-eligible.** **Nothing published changes.**
6. **No successor predicate is implemented.** No detector logic, no clause, no scoring rule, no
   edit anywhere under `argus/detectors/**`. Story 17.2 specifies the successor; Story 17.3 builds
   it. `argus/**` is byte-unchanged, so there is no `code_identity` movement and no dogfood
   artifact regeneration.
7. **The `consumed == 0` asymmetry is not loosened, reached, or measured.** It is the
   false-accusation moat.

---

## 5. Hand-off

Story 17.4 **imports** `PREREGISTRATION_COMMIT_SHA` and `SUCCESSOR_OUTPUT_PATHS` from
`scripts/precision_preregistration.py` and re-types neither (`DN-16-4-2` / `AI-E9-7`). The ancestry
guard over commits **later** than the pre-registration is **Story 17.4's to write**; `-139` here
proves only the claim this story can prove — that **no commit reachable from the pre-registration
touches any declared successor-output path**, with the three non-vacuity preconditions asserted
first.

---

## 6. Registration note

⛔ **This document is deliberately NOT registered in `tests/test_status_document_registry.py`'s
`_STATUS_DOCUMENTS`** (`DN-17-1-8`). That guard closes in **both** directions: it fails on a globbed
file that is unregistered **and** on a registered name its globs cannot find. Its globs are
`sprint-change-proposal-*.md` and `epic-*-retro-*.md`; this filename matches neither, so registering
it would turn the guard **RED**. Leaving it alone is correct.

This document asserts a **criterion**. It asserts no release status of any kind, and carries no
phrase from `_STATUS_CLAIMS`.
