# Story-readiness validation — Story 16.5

**Story:** `16-5-the-record-says-who-judged-and-whether-they-were-independent`
**Story file:** `_bmad-output/design-artifacts/ArgusAgent/stories/16-5-the-record-says-who-judged-and-whether-they-were-independent.md`
**Workflow:** `bmad-create-story`, **validate** action (`.claude/skills/bmad-create-story/checklist.md`)
**Run:** 2026-08-23, fresh context, at HEAD `52143eb` on `epic-16/discharge-df-15-2-d`
**Mode:** READ-ONLY quality gate. No story rewritten, no code touched, no test run, no
sprint-status transition. `development_status[16-5-…]` was `ready-for-dev` on entry and is
`ready-for-dev` on exit.

## VERDICT: FAIL — NOT READY FOR DEV

Two of the story's acceptance criteria are **jointly unsatisfiable with its own scope fence**, and a
third rests on a premise this validation measured **false**. A fresh dev agent cannot implement 16.5
from this file alone: it would reach Task 4, discover that every route to AC2.3 is closed by AC7.1,
and either escalate (best case) or take one of the two routes the story explicitly forbids (the
likely case, given the pattern-matching pressure §2.1 itself warns about).

This is **not** a quality complaint about a verbose story. The story is unusually well-researched —
**every numeric premise in §0 re-derived clean** (see the verification table). The failure is
structural and it is in the ACs.

---

## 1. What was verified, and what it measured

Every figure below was read off the tree, not off the story's prose.

| Claim | Where the story states it | Measured | Result |
|---|---|---|---|
| `epics.md` §Story 16.5 opens "QA Lead and External adjudicator both **unfilled**" | §0.2 | `epics.md:3191` is the `### Story 16.5` heading; the AC block's first `**Given**` is at `epics.md:3199` and reads exactly that | PASS — substantively true (see L-1 on the line cite) |
| That premise was true 2026-08-20 and is **FALSE now** | §0.2 | protocol §2 holder table `:144` — QA Lead **Veer Pratap Singh**, "named 2026-08-22"; dated block at `:161` | **PASS — the correction is correct** |
| Commit `1bb7088` filled the QA Lead | §0.2 | `1bb7088a622…`, Sat 22 Aug 2026, *"docs(protocol): the QA Lead role is filled - Veer Pratap Singh"*, touches only `precision-validation-protocol.md` (+35) and `sprint-status.yaml` | **PASS** |
| External adjudicator stays unfilled; §2 hands the independence question to 16.5 | §0.2(3) | protocol `:145` *unfilled*; `:186-192` — *"Whether any given adjudication was independent is Story **16.5**'s question to record, not this block's to assert."* | **PASS — the charter is committed** |
| Change-log head still **V1.3**, no `V1.4` row | §0.2(1), §2.4 | record `protocol_version` = `V1.3`; `1bb7088` added no change-log row | PASS |
| **31** live rows on the committed adjudication record | §0.1 | 31 total, 31 live (no superseding rows) | PASS |
| **26 FP · 5 BORDERLINE · 0 TP · 0 UNADJUDICATED** | §0.1 | exactly that | PASS |
| Distinct adjudicators = **exactly one**, `XAgent007 (Engineering Lead)` | §0.1 | `{'XAgent007 (Engineering Lead)': 31}` | PASS |
| `expert_hours` null | §0.1 | `None` | PASS |
| Decision record: `adjudicators == ["XAgent007 (Engineering Lead)"]`, outcome `BLOCKED`, `evaluable`/`fold_evaluable` false, breadth/seal/yield = false/false/true | §0.1 | all exactly as stated | PASS |
| **Derived answer today is `NOT_INDEPENDENT`** | §0.1 | 31/31 authored by the Engineering Lead, who is the tool's author | **PASS — confirmed expected output, not a failure** |
| Zero assertions over `adjudicators` in `tests/**` / `scripts/**` | §0.1 last row | `grep -rn "adjudicators" tests/ scripts/ --include=*.py` → **zero hits** | PASS |
| *"**Nothing in the repository reads it.**"* | "What this story IS", §0.1 callout | **FALSE** — see **B-3** | **FAIL** |
| `SECTION_5_CONDITIONS` = **7**, byte-unchanged | §2.1, AC4.1 | 7, in the stated order | PASS |
| `precision_evaluable` = exactly **four** conjuncts | §2.2, AC4.2 | `gate_decision.py:360-364` — four, exactly as quoted | PASS |
| `CONDITION_VERDICTS` 4 · `GATE_OUTCOMES` 3 · `PROTOCOL_ADJUDICATOR_ROLES` 3 · `DISPOSITIONS` 4 · `PRECISION_GATE_THRESHOLD` 4/5 · `MANIFEST_FIELDS` 9 | §2.1 table | all exact | PASS |
| `VALIDATION_SET_FLOOR_N = 5` lives in **`tests/cartridges/_registry.py`**, not `_manifest.py` | §2.1 table | `tests/cartridges/_registry.py:57` | PASS (the "not where a reader would guess" note is correct and useful) |
| `precision_gate_status_for` has **three** return branches, precision figure in all three | §0.3 | `replay_harness.py:803/813/821` — unevaluable / provisional / cleared, `precision={ratio}` in each | PASS |
| The optional-keyword-with-inert-default shape was taken twice (`population_label`, `unevaluable_reason`) | §0.3 | both present in the signature with inert defaults | PASS |
| Module line counts (§0.5, 18 rows) | §0.5 | re-measured with the guard's **own** `_physical_line_count`: `gate_decision.py` **1084**, `test_gate_seal.py` **1145**, `test_vacuous_density.py` **1159**, `replay_harness.py` **825**, `adjudication.py` **973**, `test_gate_decision_artifact.py` **451**, `gate_conditions.py` **234**, `_CEILING` **1200** | **PASS — every spot-checked row exact** |
| Next free ids: PRECISION `-105`, DOCS `-80` | §0.6 | max in `tests/`+`scripts/`+`argus/` is `-104` and `-79` | PASS |
| Ledger states: `DF-13-5-A` OPEN/UNSPENT · `DF-16-1-A` OPEN · `DF-16-3-A` OPEN · `DF-15-2-E` OPEN | Dev Notes table | confirmed in `deferred-work.md` (`:4766`, `:5325`, `:5342`, `:5479`, `:5508`) | PASS |
| Ledger states: `DF-15-2-D` CLOSED by `4123931` | Dev Notes table | confirmed in `deferred-work.md` (`:5266`..) | PASS |

> ⛔ **ROW SPLIT 2026-08-23 by Story 16.5's dev pass — a FORMATTING correction, not a finding
> change.** The two rows above were ONE row, and every word, cite and verdict in them is
> preserved verbatim; nothing was added, removed or re-verdicted. The single row listed four
> **OPEN** ids and one **CLOSED** id on the same physical line, and
> `TC-ArgusAgent-DOCS-001-78`'s `story_closure_claims` analyzer is **line-scoped by design** —
> its docstring says so, and says why: widening the window to a paragraph *"swept unrelated ids
> into the claim"*. So the line read as a claim that all five were closed, and the guard
> correctly went RED on the four that are not. The analyzer is right and was NOT touched; the
> record is what had to say one thing per line. The four ids remain **OPEN** on the ledger and
> this report asserts nothing else about them.
| `InstrumentStatus` is a closed **two**-member vocabulary; `INSTRUMENT_STATUS = NOT_INDEPENDENTLY_VALIDATED` | AC3.2, `DN-16-5-2` | `negative_assurance.py:124`, `:251`; the enum's docstring makes the run-grade/instrument-status warning the story cites | PASS |
| Dogfood `derive_gate_status` passes `precision=None` and no record | §2.6, AC3.4 | `proof_run.py:653-661` — `precision=None`, no record argument | PASS |
| Cited guard ids all exist | throughout | `-40`, `-45`, `-61`, `-63`, `-82`, `-104`, `DOCS-001-54/77/78`, `MAINT-001-04` all resolve | PASS |

### Target-file drift — checked, and clean for code

Every code path named in the ACs exists at the path given. The only two misses are
`argus/precision/gate_independence.py` and `tests/test_gate_independence.py`, both correctly
declared **(new)**. The DF-15-2-D move is correctly reflected: `argus/detectors/vacuous_vocabulary.py`
exists and the story cites it as the new home. **No repeat of the moved-module bite.**

### Ledger / split-first triggers — checked, and adequately handled

- New guards go to a **new** module (AC5.1); `tests/test_gate_seal.py` (1,145, `DF-16-3-A`, trigger
  1,180) and `tests/test_vacuous_density.py` (1,159, `DF-15-2-E`, trigger 1,180) are both on the
  must-not-move list. PASS
- `tests/test_gate_decision_artifact.py` takes AC5.5's guard at 451/1,200. No risk. PASS
- `argus/precision/gate_decision.py` at 1,084/1,200 is the only real trigger, and **Task 1 pre-empts
  it correctly** — projection before the first line, split-first-alone above 1,150, file a `DF-16-5-*`
  between 1,100 and 1,150. This is the best-handled part of the story. PASS
- One consequence of **B-1**: whichever module the dev must edit to resolve AC2.3 is *not* in the
  headroom projection. `adjudication.py` (973) and `gate_seal.py` (777) have room, so this does not
  create a new trigger — but the projection is incomplete until B-1 is answered.

---

## 2. BLOCKING findings

### B-1 — AC2.3 is unsatisfiable inside AC7.1's byte-unchanged fence. Every route is closed.

AC2.3 requires the independence note to be carried through **all four** renderers the
`precision_gate_status` branch set can return. Measured, each of those four is a call to
`precision_gate_status_for` made from **inside a module the story forbids or omits**:

| Renderer AC2.3 names | Where the call actually is | Status under AC7.1 / AC7.2 |
|---|---|---|
| `fold.gate_status` | `argus/precision/adjudication.py:963` — computed once and **stored as a plain `str` field** (`adjudication.py:829`) | §0.5 marks the module **"Read-only for this story"**; AC7.2 does **not** list it as expected to change |
| `effective_precision_gate_status` | `argus/precision/gate_breadth.py:381` | AC7.1 — **BYTE-UNCHANGED, asserted** |
| `sealed_precision_gate_status` | `argus/precision/gate_seal.py:698` | AC7.1 — **BYTE-UNCHANGED, asserted** |
| `yielded_precision_gate_status` | `argus/precision/gate_yield.py:493` | AC7.1 — **BYTE-UNCHANGED, asserted** |

Worse, all three arm renderers **short-circuit** — `if fold.evaluable == (fold.evaluable and
X.holds): return fold.gate_status` — so even the pass-through path hands back the fold's
**precomputed** string. A keyword added to `precision_gate_status_for` (AC2.1) reaches **none** of
the four unless an intermediate module also gains a parameter and forwards it.

The three escape routes are each independently forbidden by the story:

1. Edit `gate_breadth`/`gate_seal`/`gate_yield` → violates **AC7.1**, which asserts them byte-unchanged.
2. Edit `adjudication.py` → contradicts **§0.5** ("read-only") and is absent from **AC7.2**.
3. Post-process the returned string, or re-render in `gate_decision.py` → forbidden by **§2.3**,
   **`DN-16-5-5`** and **AC3.1**'s no-second-renderer walk.

**This is a closed box.** AC2.3 cannot be met. The story needs a decision it has not taken: which
modules move, and AC7.1/AC7.2 amended to say so. Note this is not academic — today `breadth is not
None` and `breadth_holds = false`, so the live path returns `effective_precision_gate_status`, i.e.
route 1's module, the one asserted byte-unchanged.

**Suggested fix:** move `argus/precision/gate_breadth.py`, `gate_seal.py`, `gate_yield.py` and
`adjudication.py` from AC7.1 to AC7.2, scoped to *"one optional keyword forwarded, no other byte,
no behaviour change, default renders byte-identically"* — the same NFR-P1 shape §0.3 already
identifies. Re-run the Task 1 headroom projection over the four.

### B-2 — AC4.3 and AC5.3 are jointly unsatisfiable for `NOT_ESTABLISHED`, because §5(4) already reads the adjudicator set.

`_recorded_cleared_condition` (`gate_decision.py:626-690`) takes `adjudicators` as a parameter and:

```python
if not adjudicators:
    problems.append(
        "NO adjudicator is named on any live row — an unattributed adjudication run "
        "is not a recorded one (non-vacuity floor, AI-E11-1)"
    )
```

An empty adjudicator set therefore forces §5(4) `FAILED`, and the CLEARED branch of the outcome
dispatch is guarded by `all(condition.verdict == "MET" for condition in conditions)`
(`gate_decision.py:1021`). So:

- **AC5.3** requires every vocabulary member to be **reached by a generated population**. Reaching
  `NOT_ESTABLISHED` means an empty adjudicator set (AC1.2: *"no live human disposition exists"*).
- **AC4.3** requires that over *"a population constructed to be otherwise `CLEARED`… flipping the
  independence status through **every** member of the vocabulary leaves `outcome`, `outcome_reason`,
  **all seven condition verdicts**, `precision_evaluable` and `precision.meets_threshold`
  byte-identical."*
- Flipping to `NOT_ESTABLISHED` **necessarily** flips §5(4) MET→FAILED and `outcome` CLEARED→NOT_CLEARED.

It fails twice over, in fact: with no live human disposition, TP+FP = 0, so `fold.precision is None`
and the dispatch BLOCKS on the empty denominator (`:977`) before §5(4) is even weighed. The same
applies to AC4.3's second required direction (the live `BLOCKED` population): emptying the
adjudicator set changes `outcome_reason` from the exhaustiveness reason to the empty-denominator one.

A dev who takes AC4.3 literally will build a fixture that cannot go green, and the likeliest
resolution under time pressure is to weaken the guard until it passes — **the exact vacuity failure
§2.8 spends a page warning about**, arrived at by following the ACs rather than by ignoring them.

**Suggested fix:** scope AC4.3's inertness proof to *"flipping among the members that a
non-empty adjudicator set can produce (`NOT_INDEPENDENT`, `SECOND_REVIEWER_INTERNAL`,
`EXTERNAL_ADJUDICATOR_PARTICIPATED`)"*, and state explicitly that `NOT_ESTABLISHED` is **already**
gate-relevant through §5(4)'s pre-existing non-vacuity conjunct — that this story neither adds nor
removes that coupling, and that AC5.3 reaches `NOT_ESTABLISHED` over a population that is BLOCKED
for that independent reason.

### B-3 — the "entirely unread" premise is false, and it is the premise the story is built on.

The story's framing sentence — *"**Nothing in the repository reads it.**"* — and the §0.1 callout
*"The last row is the story. The field is published and unguarded"* are **contradicted by
`gate_decision.py:626-690`**, which reads the adjudicator set twice:

1. as the §5(4) **non-vacuity conjunct** quoted in B-2 (it can move a condition verdict, hence the
   gate outcome); and
2. on the MET path it renders the names into a **published sentence**:
   `f"recorded cleared: run attributed to {', '.join(adjudicators)} over …"` (`:665`).

The §0.1 *table row* is precisely and correctly scoped ("assertions in `tests/**` or `scripts/**`" —
verified **zero**), and §0.7 correctly notes that `decide_gate` *derives* the tuple. What the story
missed is the **consumer**. The `GateDecision.adjudicators` **field** is indeed write-only
(`:276` declared, `:468` published, never read) — but the derived **value** is load-bearing already.

This matters three ways: it is the mechanical cause of **B-2**; it means AC3.1's "only status
renderer" walk must be written to distinguish a `ConditionResult.measured` string from a gate-status
sentence, or it will red on `:665`; and the story's own §1.1 argument ("those two facts are separable
by copy-and-paste") is *weakened but not destroyed* — §5(4)'s attributed sentence exists only on the
MET path, which the live record does not reach (`adjudication_run_recorded_cleared: false`).

**Suggested fix:** correct the framing to *"the field is published and **unguarded by any test**;
its emptiness is already a §5(4) conjunct, and its contents are already rendered on §5(4)'s MET
path — neither of which travels with the precision figure"*, and add `_recorded_cleared_condition`
to §0.7's "already true, do not re-do" list.

---

## 3. Non-blocking findings

- **M-1 — artifact paths are given repo-root-relative but are not.** `validation-corpus/adjudication-record.json`
  and `validation-corpus/gate-decision-record.json` (§0.1 "Where", AC6.1, AC7.1, AC7.2, Task 0)
  do not exist at those paths. They live at
  `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/`. The story mixes repo-root paths
  (`argus/`, `tests/`, `scripts/`) with artifact-dir-relative ones in the same lists without saying
  so. A dev's first Task 0 command will fail with ENOENT. *Fix: qualify both, once, in §0.0.*
- **M-2 — `DF-9-2-A` "no new import edge into `tests/`" needs a caveat.** `replay_harness.py:788`
  already resolves `VALIDATION_SET_FLOOR_N` through a `registry_module()` indirection into
  `tests/cartridges/`. The story's Dependencies note says "no **new** edge", which is correct, but a
  dev reading AC1.1's purity clause alongside §2.1's `_registry.py` pointer may conclude the
  existing indirection is a defect to fix. *Fix: one sentence noting the indirection is deliberate
  and out of scope.*
- **L-1 — line-cite imprecision.** §0.2 and the References say `epics.md:3191` "opens" with the
  `**Given** … unfilled` sentence. `:3191` is the section heading; the sentence is at `:3199`. The
  claim is substantively right; only the cite is loose. Given the story's own standard ("read off
  the tree"), worth tightening.
- **L-2 — AC3.1's walk needs its exclusion set stated.** Per B-3, `gate_decision.py:665`,
  `breadth_blocked_reason`, `seal_blocked_reason` and `yield_blocked_reason` all render
  sentences about the gate. AC3.1 will either red on them or be written loose enough to be
  vacuous. *Fix: name what counts as "a gate-status sentence" (the `precision=` surface) explicitly.*

## 4. Checklist dimensions that PASS

- **Single-purpose.** One field made legible, one module, one keyword. The four-bullet "What it is
  NOT" fence is exemplary.
- **Testable ACs.** With the exception of AC4.3 (B-2), every AC names an observable and a
  falsification. AC2.4's two-direction mutation and AC5.2's pinned-term generation directly target
  the lockstep trap that fired in 16.1/16.2/16.3.
- **Reuse over reinvention.** §0.7 correctly forbids a second parser, a second role list and a
  recount, and points at `adjudicator_role()`, `PROTOCOL_ADJUDICATOR_ROLES`, `live_rows()` and the
  already-computed `adjudicators` tuple. Verified all four exist and do what the story says.
- **Previous-story intelligence.** Concrete and correct, including the 16.4-closed-by-decision
  consequence (the record is still the 2026-08-17 set of 31 — verified).
- **Escalation discipline.** AC7.4 names four escalation triggers with a STOP, and B-1/B-2 would
  both surface as escalations rather than as silent damage — which is why this is a `fail`, not a
  catastrophe.
- **Operator-act boundary.** §2.9, AC4.5 and `DN-16-5-3` correctly keep the story out of §6 R2
  territory: no role filled, no ratification, no disposition, no detector run, no bench mutation.

## 5. Recommendation

Return to create-story for a **targeted amendment** — not a rewrite. Three edits clear it:

1. **B-1:** move the four renderer-owning modules from AC7.1 to AC7.2 with a byte-stability-scoped
   change budget, and re-run Task 1's projection over them.
2. **B-2:** restrict AC4.3's inertness sweep to the non-empty members and state §5(4)'s pre-existing
   coupling as a *found* fact.
3. **B-3:** correct the "nothing reads it" framing and extend §0.7.

M-1 and M-2 are one sentence each. Everything else in the file stands as written and re-measured.

---

*Read-only validation. No story file was modified, no `argus/`, `tests/` or `scripts/` file was
touched, no test or builder was executed, no sprint-status value was changed.*
