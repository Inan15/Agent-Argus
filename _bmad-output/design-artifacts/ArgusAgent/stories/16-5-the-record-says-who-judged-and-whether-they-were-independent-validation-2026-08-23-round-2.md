# Story-readiness validation — Story 16.5 — **ROUND 2** (post-amendment)

**Story:** `16-5-the-record-says-who-judged-and-whether-they-were-independent`
**Story file:** `_bmad-output/design-artifacts/ArgusAgent/stories/16-5-the-record-says-who-judged-and-whether-they-were-independent.md`
**Workflow:** `bmad-create-story`, **validate** action
**Run:** 2026-08-23, fresh context, at HEAD `52143eb` on `epic-16/discharge-df-15-2-d`
**Iteration:** 2. Round 1 (`…-validation-2026-08-23.md`) returned **FAIL** on B-1 / B-2 / B-3.
**Mode:** READ-ONLY quality gate. No story file rewritten, no `argus/` / `tests/` / `scripts/` byte
touched, no test, builder or detector executed, no sprint-status transition.
`development_status[16-5-…]` was `ready-for-dev` on entry and is `ready-for-dev` on exit.

## VERDICT: CONCERNS — implementable, but two items should be fixed before hand-off

**All three round-1 blockers are genuinely resolved, not reworded.** I re-derived each one against
the tree rather than against the amendment's claims. AC2.3 is now reachable end to end; the
AC4.3/AC5.3 contradiction is dissolved rather than relocated; the "nothing reads it" premise is
corrected in all three places and the consequence (AC3.1's exclusion set) is mechanically sound.

The load-bearing new artefact — **the AC7.1a forwarding budget** — survives adversarial scrutiny,
including the compatibility check that would have sunk it: **no shipped guard closes over the
signatures or call kwargs of the four widened modules**, so AC7.1a and AC7.1's byte-unchanged test
fence are jointly satisfiable. See §2.

What holds this back from `pass` is **one un-rebutted conflict with a locked decision recorded in
shipped code** (`DN-16-1-1`, §3 C-1) and **one measurably wrong mechanism the story orders a dev to
write into a guard docstring as a "found fact"** (§3 C-2). Neither closes a route. Both are a
paragraph. A dev who hits C-1 mid-Task-4 will correctly stop and escalate under AC7.4 — which is the
escalation discipline working, but it is an avoidable round trip.

---

## 1. The three round-1 blockers, re-measured

### B-1 — AC2.3 unsatisfiable inside AC7.1's fence → **RESOLVED**

Every mechanical claim the amendment rests on was re-derived, not trusted:

| Claim (§2.3 / AC2.3 / AC7.1a) | Measured | Result |
|---|---|---|
| `fold.gate_status` computed at `adjudication.py:963` | `gate_status=precision_gate_status_for(` at `:963`, inside `fold_adjudicated_precision` (AST-resolved enclosing scope) | PASS |
| …and stored as a plain `str` field at `adjudication.py:829` | `gate_status: str` at `:829` on `AdjudicatedPrecision` | PASS |
| `effective_precision_gate_status` renders at `gate_breadth.py:381` | `return precision_gate_status_for(` at `:381`, enclosing fn `effective_precision_gate_status` | PASS |
| `sealed_precision_gate_status` at `gate_seal.py:698` | same shape, enclosing fn `sealed_precision_gate_status` | PASS |
| `yielded_precision_gate_status` at `gate_yield.py:493` | same shape, enclosing fn `yielded_precision_gate_status` | PASS |
| All three arm renderers short-circuit `if fold.evaluable == (fold.evaluable and X.holds): return fold.gate_status` | verbatim in all three, immediately above the re-render | PASS |
| Each of the four has **exactly one** `precision_gate_status_for` call in the function AC7.1a(b) names | one each; no second call anywhere in those functions | PASS |
| `decide_gate` is `fold_adjudicated_precision`'s **only production caller**, "verified repo-wide" | repo-wide grep: one `def`, one `__all__` entry, one call at `gate_decision.py:811`, two docstring `:func:` references (`replay_harness.py:296`, `scripts/build_gate_decision.py:7` — **not calls**), and 6 call sites in `tests/**` | **PASS — the claim is exact** |
| The four are OFF AC7.1's fence and ON AC7.2 | AC7.1's list no longer names `gate_breadth.py` / `gate_seal.py` / `gate_yield.py`; all four appear in AC7.2 under the AC7.1a budget | PASS |

**Reachability traced end to end, which is the question that actually matters.** `decide_gate`
derives the note → passes it into `fold_adjudicated_precision` → `fold.gate_status` carries it →
each arm module forwards the same keyword on its re-render path, and inherits the note for free on
its short-circuit path. I then checked the one thing that could still have broken it silently:
`GateDecision.precision_gate_status` (`gate_decision.py:380-396`) selects a branch by **string
comparison**, `if breadth_status != self.fold.gate_status: return breadth_status`. Because the note
lands in **both** operands, the comparison is unchanged and the property's branch selection stays
byte-behaviour-identical. **AC2.3 is genuinely satisfiable.**

### B-2 — AC4.3 contradicted AC5.3 → **DISSOLVED, not relocated**

`_recorded_cleared_condition` is at `gate_decision.py:626-690`, takes `adjudicators: Sequence[str]`,
appends the quoted non-vacuity problem on an empty set, and renders the names at `:665` — all four
cites exact. The amendment scopes AC4.3's inertness sweep to the three **non-empty** members and
carves `NOT_ESTABLISHED` out with a stated reason; AC5.3 correspondingly asserts **the derived
status** on that population and explicitly forbids asserting gate inertness there. The two ACs no
longer make opposing demands of one fixture. §0.7 gained the `_recorded_cleared_condition` entry
with a do-not-re-implement / do-not-weaken fence. **The circularity is gone.**
*(One limb of the stated mechanism is wrong — see C-2. The scoping decision it supports is right.)*

### B-3 — "nothing in the repository reads it" was FALSE → **CORRECTED, and the consequence holds**

Restated as *"unguarded by any test" / "unattached"* in all three places (the framing block, §0.1's
callout, §1.1's qualification). Re-measured: the **field** is write-only — declared `:276`,
published `:468`, and `self.adjudicators` is read nowhere else (`:887` and `:1076` read the
**local**, not the field). The **derived value** is load-bearing via §5(4). The story now says
exactly that.

**And the downstream fix (L-2) is mechanically sound, which I checked rather than assumed.** AC3.1's
guard predicate is *"a gate-status sentence is one carrying the `precision=` surface"*. Measured
across `argus/**`: the `precision={ratio}` surface is emitted at **exactly three sites**, all three
branches of `precision_gate_status_for` (`replay_harness.py:808 / :815 / :822`). §5(1)'s
`ConditionResult.measured` uses `precision = {ratio}` **with spaces** (`gate_decision.py:556`,
`:575`), and §5(4)'s attributed sentence at `:665` carries **no ratio at all**. So the predicate
neither reds on master nor is vacuous. This is the exclusion set doing real work.

---

## 2. The AC7.1a forwarding budget — scrutinised hardest, and it holds

### 2.1 Is the budget precise enough to be checkable? **Yes.**

AC7.1a is exactly (a) one optional keyword on one function, (b) forwarded to the one existing
`precision_gate_status_for` call in that function, (c) one docstring line — plus four hard fences:
byte-identical rendering when omitted (proven by rendering strings, not by reading the diff), no
module derives/parses/words the note, no second parameter, no new import edge (in particular no
`gate_independence` import), no `__all__` change — and **anything beyond (a)/(b)/(c) is an AC7.4
escalation with a STOP**. That is falsifiable per-module by inspection. **Task 8 does verify it**,
in both required ways (read the diff for the budget shape; render-and-compare for byte-identity),
and adds the note that `PROTOCOL_ADJUDICATOR_ROLES` / `DISPOSITIONS` live in `adjudication.py`,
which is no longer whole-module fenced — so AC4.4's by-value assertion now carries weight it did not
carry before. That is a genuinely well-made catch by the amendment.

### 2.2 Does the widening collide with a shipped guard? **No — and this was the real risk.**

Three of the four widened modules are covered by AST closures in test files that AC7.1 fences
**byte-unchanged**. If any closed over a signature or a call's kwargs, AC7.1a and AC7.1 would be
jointly unsatisfiable and this would be a round-2 FAIL. Measured:

| Guard | What it actually closes over | Effect of one forwarded keyword |
|---|---|---|
| `tests/test_gate_breadth.py:357` | the `contributing_member_floor` FunctionDef body only | none |
| `tests/test_gate_seal.py:420` (`-87` (iv)) | `gate_seal.py`'s **imports** against a banned set `{subprocess, pathlib, datetime, random, os, time, urllib, socket, uuid}`, plus `open()` calls | none — an opaque `str | None` adds no import |
| `tests/test_gate_yield.py:569` (`-99`) | `_structural_names()` ∩ `_FORBIDDEN_NAMES` (recall/FN/golden-key/bench-content names) — a **disjointness** check, not an exact-set check; it does collect `ast.arg` | none, provided the keyword is not named after a forbidden term |
| any `inspect.signature` / `getfullargspec` closure over the four | **none exists** anywhere in `tests/**` | — |

**AC7.1a and AC7.1 are compatible.** Worth stating in the story so the dev does not have to
re-derive it under pressure — but it is not a defect.

### 2.3 The four projections, re-derived with the ceiling guard's own `_physical_line_count`

`len(text.splitlines())`, `_CEILING = 1200` (`tests/test_module_size_ceiling.py:176-188`):

| Module | Story says | Measured | Headroom |
|---|---|---|---|
| `argus/precision/adjudication.py` | 973 / 227 | **973** | 227 |
| `argus/precision/gate_seal.py` | 777 / 423 | **777** | 423 |
| `argus/precision/gate_yield.py` | 560 / 640 *(§0.5 table, Task 1)* | **560** | 640 |
| `argus/precision/gate_breadth.py` | 436 / 764 | **436** | 764 |
| `argus/precision/gate_decision.py` | 1,084 / 116 | **1,084** | 116 |

All exact. **The amendment's conclusion is correct: at a single-digit per-module delta none of the
four can approach 1,100, let alone the 1,150 split-first trigger or the 1,200 ceiling, so the
widening adds NO new NFR-M1 trigger and `gate_decision.py` at 1,084 remains the only one to watch.**
I also re-measured the whole of §0.5 (21 rows) and every row is exact. No wrong projection walks the
dev into a mid-story split-first trigger. *(One transcription slip in the §0.5 prose — see L-1.)*

### 2.4 Did the amendment widen scope beyond what the fix required? **No.**

Moving four modules off the byte-unchanged fence is a real widening, and I looked for a quiet
licence in it. There is none: AC7.1a is strictly narrower than "these modules may change", it names
the one function and the one call per module, it forbids a second parameter, it re-affirms
`DN-16-5-5` in terms (*"forwarding a keyword through the call chain is the opposite of string
surgery on another function's output, not an exception to it"*), and it routes any overflow to
AC7.4 rather than to judgement. `argus/precision/gate_conditions.py`, `gate_evidence.py`,
`gate_disclosure.py`, `negative_assurance.py`, `argus/dogfood/**`, `argus/detectors/**` and the nine
fenced test files all remain on AC7.1. **The fence moved by exactly four modules and one keyword.**

---

## 3. Findings

### C-1 (CONCERN) — the budget takes the move `DN-16-1-1` is recorded, **in shipped code**, as having rejected — and the story neither names nor rebuts it

`argus/precision/gate_breadth.py:366-368` says, in the shipped docstring of the very renderer AC2.3
depends on:

> **The fold is NOT forked** (DN-16-1-1). `fold_adjudicated_precision` and `AdjudicatedPrecision`
> are byte-untouched: threading a breadth argument into the fold would widen a signature shared
> with the cartridge path, where breadth is meaningless.

AC7.1a threads an argument into `fold_adjudicated_precision`. The story lists `DN-16-1-1` under
**"Locked decisions this story CITES rather than reopens"** and says nothing about the conflict.

I measured whether 16.1's objection actually applies, and **it does not**: the cartridge path is
`replay_harness.compute_precision`, which returns a **different type** (`PrecisionResult`, not
`AdjudicatedPrecision`) and does **not** call `fold_adjudicated_precision`. The signature is
adjudication-only, so 16.1's stated reason is factually loose and 16.5's move is defensible — the
note is a property of the adjudication record the fold already takes as its first argument. **But
the dev will not know that.** A dev at Task 4 reads `gate_breadth.py:366` — the module they are
about to edit — sees a locked decision that appears to forbid the exact edit AC7.1a mandates, and
under AC7.4 (*"if the note cannot be threaded within this budget, do NOT widen it silently"*) the
correct behaviour is to STOP and escalate. That is an avoidable round trip on the story's
load-bearing fix.

**Suggested fix (one `DN-16-5-7`, three sentences):** record that AC7.1a threads a keyword into
`fold_adjudicated_precision`; that `DN-16-1-1`'s *"signature shared with the cartridge path"*
objection was measured and does not hold (`compute_precision` returns `PrecisionResult` and does not
call the adjudicated fold); that independence, unlike breadth, is a property of the record the fold
already receives; and that the fold is **widened by one inert keyword, not forked** — `DN-16-1-1`'s
actual subject (no second fold, no second arithmetic) is untouched.

### C-2 (CONCERN) — AC4.3 orders a **measurably wrong mechanism** written into a guard docstring as a "found fact"

AC4.3 (and AC5.3, which repeats it) states that reaching `NOT_ESTABLISHED` means an empty adjudicator
set which:

> 2. **before even that**, makes TP+FP = 0, so `fold.precision` is `None` and the dispatch **BLOCKS
>    on the empty denominator** (`gate_decision.py:977`)

Measured, this is wrong about which branch fires. `AdjudicationRow.__post_init__`
(`adjudication.py:376-377`) calls `adjudicator_role(self.adjudicator or "")` for every disposition in
`HUMAN_DISPOSITIONS = ("TP", "FP", "BORDERLINE")`, which **raises** on an empty or unregistered id.
So a TP/FP/BORDERLINE row **cannot be constructed without a registered adjudicator**, and an empty
adjudicator set therefore implies **every live row is `UNADJUDICATED`** — which makes the record
**non-exhaustive**. `decide_gate` reaches `elif not isinstance(fold.exhaustiveness, Exhaustive)` at
**`:956`**, which precedes `elif fold.precision is None` at `:977`. The population blocks on
**exhaustiveness**, with the exhaustiveness `outcome_reason` and closure path, not on the empty
denominator.

A smaller cite slip in the same passage: the `CLEARED` branch guard
`all(condition.verdict == "MET" for condition in conditions)` is at **`:1022`**, not `:1021`
(`:1021` is `closure = yield_closure_path(detector_yield)`). *(Round 1 introduced this cite and the
amendment carried it forward; by the story's own standard — the one that motivated the
`:3191`→`:3199` tightening — it should be exact.)*

**Why this is a concern and not cosmetic:** AC4.3 instructs *"State this coupling explicitly **in the
guard docstring** as a found, pre-existing fact"*, and AC5.3 repeats the denominator claim. Under
GUARD-ADEQUACY (i)/(ii) and this repository's own `DF-9-2-B` standard, a guard docstring asserting a
mechanism the code does not exhibit is exactly the defect class the story spends §2.8 warning about.
A dev who additionally asserts `outcome_reason` on that fixture will go red for a reason the story
told them not to expect.

**Suggested fix:** replace limb 2 with the measured mechanism — *"an empty adjudicator set is only
constructible when every live row is `UNADJUDICATED` (`adjudication.py:376-377` refuses a human
disposition without a registered adjudicator), which makes the record non-exhaustive; the dispatch
therefore BLOCKS at `gate_decision.py:956` on exhaustiveness, ahead of both the empty-denominator
branch (`:977`) and §5(4)"* — and correct `:1021` → `:1022`. The **scoping decision AC4.3 takes is
unaffected and remains correct**: `NOT_ESTABLISHED` necessarily moves the outcome, so it is rightly
excluded from the inertness sweep, and AC5.3's "assert the STATUS, not gate inertness" is right.

### L-1 (LOW) — §0.5's amended prose transcribes a **headroom** as a **line count**

§0.5's amendment paragraph reads *"at 973 / 777 / **640** / 436 lines against a 1,200 ceiling"*.
`gate_yield.py` is **560** lines with **640** of headroom — §0.5's own table row and Task 1 both say
`560/640` correctly. The error is conservative (640 > 560) so it cannot hide a trigger, but it is a
line-count slip inside the paragraph the story tells the dev to trust for the split-first decision.
*Fix: 640 → 560.*

### L-2 (LOW) — Task 4 presents the `decide_gate` wiring as a forward, but it requires a re-ordering

`decide_gate` calls `fold_adjudicated_precision` at `:811`, and derives `live = record.live_rows()` /
`adjudicators = …` at **`:820-823` — after it**. To pass the note *into* the fold, that derivation
must move above `:811`. Task 4 says only *"`decide_gate` derives it from the `adjudicators` tuple it
already computes"*, and AC7.2 says only *"the forwarded argument at `:811`"*. The edit is trivial and
lands inside an AC7.2 module, so nothing is blocked — but it is a re-ordering inside the gate's
central function presented as a one-line forward. *Fix: one clause in Task 4 noting the derivation
moves above the fold call, with everything it depends on (`record.live_rows()`) already available
there.*

### L-3 (LOW) — Task 0's working-tree expectation is now stale

§0.0 and Task 0 require `git status --porcelain` to show **only** the story file and
`sprint-status.yaml`. Measured now: **three** entries — round 1's validation report is untracked too,
and this report makes four. A dev following Task 0 literally hits a §0 mismatch on their first
command and, per §0's own *"report any row that differs"* culture, may treat it as the next false
premise. *Fix: "…plus this story's validation reports".*

### L-4 (LOW) — Task 4's byte-identity confirmation list omits three direct callers of the renderer

AC2.1 requires **every existing caller** of `precision_gate_status_for` to render byte-identically.
Task 4's confirmation list names only callers of the **fold builder**
(`test_adjudication_record.py`, `test_gate_breadth.py`, `test_gate_decision.py`,
`test_gate_decision_artifact.py`, `scripts/build_gate_decision.py`). Measured, there are three
further **direct** callers not on AC7.1's fence and not on AC7.2: `tests/test_gate_flip_path.py`
(`:232`, `:240`, `:251`), `tests/test_precision_replay.py` (`:390`, `:395`) and
`tests/test_validation_corpus.py` (`:909`, `:917`) — plus `argus/dogfood/proof_run.py` `:591`/`:653`
and `replay_harness.py:570`, which **are** covered (AC7.1's `argus/dogfood/**`, AC3.4). AC2.1's
blanket wording covers them, so nothing is unsatisfiable; the confirmation list is just incomplete.
*Fix: add the three to Task 4's list.*

---

## 4. Invariants — all confirmed intact

| Invariant | Measured | Result |
|---|---|---|
| `SECTION_5_CONDITIONS` still **SEVEN**, byte-unchanged | 7, in order, `gate_conditions.py`; `gate_conditions.py` on AC7.1's fence; no AC anywhere adds an eighth (AC4.1, §2.1 explicit) | PASS |
| `precision_evaluable` exactly **four** conjuncts | `gate_decision.py:360-364`, four, exactly as §2.2 quotes; AC4.2 forbids a fifth and forbids a `_precision_condition` branch | PASS |
| `DN-16-5-4` intact, not overturned | AC1.5 unchanged; the roster/record distinction is still required **in the published sentence** | PASS |
| `DN-16-5-5` intact, not overturned | re-affirmed verbatim in §2.3 **and** AC2.3 **and** AC7.1a; post-processing still forbidden; the budget is forwarding, not string surgery | PASS |
| §2.1's constants, by value | `CONDITION_VERDICTS` 4 · `GATE_OUTCOMES` 3 · `PROTOCOL_ADJUDICATOR_ROLES` 3 · `DISPOSITIONS` 4 · `PRECISION_GATE_THRESHOLD` 4/5 · `MANIFEST_FIELDS` 9 · `VALIDATION_SET_FLOOR_N` 5 in `tests/cartridges/_registry.py:57` | PASS |
| §0.1's measured premises (spot-check after amendment) | 31 rows / 31 live · 26 FP · 5 BORDERLINE · 0 TP · 0 UNADJUDICATED · one distinct adjudicator `XAgent007 (Engineering Lead)` · V1.3 · `expert_hours` null · gate `BLOCKED` · `precision.evaluable` false · breadth/seal/yield false/false/true | PASS — unchanged and exact |
| §0.2 (the epic's stale premise) | protocol §2 `:144` QA Lead **Veer Pratap Singh** named 2026-08-22 · dated block `:161` under V1.3, no `V1.4` row · External adjudicator `:145` **unfilled** | PASS |
| L-1 cite fix from round 1 | `epics.md:3191` = `### Story 16.5` heading; `:3199` = the *"both **unfilled**"* **Given** | PASS — exact |
| M-1 path-root fix from round 1 | both JSONs exist under `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/` and nowhere at the repo root; §0.0 qualifies it once | PASS |
| M-2 from round 1 | `replay_harness.py:788` is `floor_n = registry_module().VALIDATION_SET_FLOOR_N if floor_n is None else floor_n`, inside `precision_gate_status_for` | PASS |
| §0.6 id allocation | highest in `argus/` + `tests/` + `scripts/` + architecture/protocol is `PRECISION-001-104` and `DOCS-001-79`; `-105` / `-80` are free | PASS |
| Every AC-named path exists today | all present; the only two absent are `argus/precision/gate_independence.py` and `tests/test_gate_independence.py`, both correctly declared **(new)** | PASS |

## 5. Split-first triggers under the widened file set

- `tests/test_gate_seal.py` — **1,145 / 1,200**, `DF-16-3-A` OPEN, ledger trigger **1,180**
  (`deferred-work.md:5479+`). On AC7.1's fence; AC5.1 sends new guards to a **new** module. **Safe.**
- `tests/test_vacuous_density.py` — **1,159 / 1,200**, `DF-15-2-E` OPEN, trigger **1,180**
  (`:5325+`). On AC7.1's fence, untouched by this story. **Safe.**
- `tests/test_gate_independence.py` — **new**, from zero. Cannot cross a trigger.
- `tests/test_gate_decision_artifact.py` — 451, takes AC5.5's single artifact guard. 749 headroom.
- The four newly-widened `argus/` modules — 973 / 777 / 560 / 436, single-digit delta each.
  **No new trigger** (§2.3 above).
- `argus/precision/gate_decision.py` — **1,084 / 116**, no ledger entry, the only real trigger.
  Task 1 pre-empts it correctly: project before the first line, split-first-alone above 1,150, file
  a `DF-16-5-*` between 1,100 and 1,150, `MAINT-001-04` respected (no `_EXEMPT_BY_DESIGN` entry).

**No plausible edit in this story crosses a split-first trigger, and the story states the one that
could.** The widened file set changes nothing here.

## 6. Dimensions that PASS

- **Single-purpose.** Unchanged by the amendment: one field made legible, one new module, one
  keyword, one payload key. The four-bullet "What it is NOT" fence still holds, and the amendment
  did not smuggle a second subject in behind the budget.
- **ACs individually testable.** Every AC names an observable and a falsification. With C-2's
  mechanism corrected, AC4.3 is now buildable — which was the one exception round 1 recorded.
- **Collectively sufficient.** The chain derive → publish → render → guard → regenerate → record is
  complete, and AC6.1's builder-regeneration + AC5.5's artifact re-derivation close the drift path.
- **Reuse over reinvention.** `adjudicator_role()`, `PROTOCOL_ADJUDICATOR_ROLES`, `live_rows()`,
  `__post_init__`'s refusal and the already-computed `adjudicators` tuple — all verified to exist and
  to do what §0.7 says.
- **Operator-act boundary.** §2.9 / AC4.5 / `DN-16-5-3` keep the story clear of §6 R2: no role
  filled, no ratification, no disposition, no detector run, no bench mutation, `DF-13-5-A` unspent.
- **Escalation discipline.** AC7.4's four triggers plus AC7.1a's own overflow clause mean C-1 and
  C-2 would surface as escalations rather than as silent damage — which is why this is `concerns`
  and not `fail`.

## 7. Recommendation

**Fix C-1 and C-2, then go.** Both are paragraph-sized and neither reopens scope:

1. **C-1** — add `DN-16-5-7` rebutting `DN-16-1-1`'s objection with the measurement
   (`compute_precision` returns `PrecisionResult` and does not call the adjudicated fold), so the dev
   is not stopped by a shipped docstring that appears to forbid AC7.1a.
2. **C-2** — replace AC4.3 limb 2 with the exhaustiveness mechanism (`:956`, ahead of `:977`) and
   correct `:1021` → `:1022`, so the guard docstring the AC mandates states a true found fact.

L-1 through L-4 are one line each and can ride along. **Everything else in the file — including all
of §0's numeric research, re-derived a second time — stands as written.**

---

## 8. Latent, out of scope for 16.5 — recorded so it is not lost

`argus/precision/gate_decision.py:971` publishes, in the non-exhaustive branch's closure path:
*"the QA-Lead second reviewer and, on persistent disagreement, the external tie-break adjudicator are
FILLED — protocol §2 records both roles as **unfilled**"*. Since `1bb7088` (2026-08-22) that is
**false**: the QA Lead is filled. No test asserts the string (grepped `tests/` and `scripts/`), and
the committed `gate-decision-record.json` does **not** contain it — the live record blocks on the
empty-emitted-population branch, so the stale sentence is currently unpublished. **It is therefore
correctly out of 16.5's scope and this is not a finding against the story.** But it is the exact
roster-vs-record conflation `DN-16-5-4` exists to prevent, sitting unguarded in the module 16.5
edits, and it becomes a published falsehood the moment the dispatch reaches that branch. Worth a
`deferred-work.md` append (AC6.4 already permits a pure append) or a note to the next story that
touches §2's roster — **not** an in-scope edit here.

---

*Read-only validation, round 2. No story file was modified, no `argus/`, `tests/` or `scripts/` file
was touched, no test, builder or detector was executed, nothing was ratified, no disposition was
written, no bench member was read or mutated, and no sprint-status value was changed —
`development_status[16-5-…]` remains `ready-for-dev`.*
