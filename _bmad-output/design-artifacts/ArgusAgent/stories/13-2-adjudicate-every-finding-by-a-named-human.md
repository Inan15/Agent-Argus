# Story 13.2: Adjudicate every finding, by a named human

Status: done

<!-- Created 2026-08-16 by create-story. Every premise below was re-measured by execution on
     HEAD bc55e36 before this file was written; see §0. Three defects in the gate-flip path were
     found BY EXECUTION and are reproduced verbatim in §0.1 — read that section first. Validation
     is optional — run bmad-create-story:validate for a second pass before dev-story. -->

## Story

As the accountable adjudicator,
I want to judge each emitted finding true or false against the recorded protocol,
So that the precision figure is a measurement rather than an estimate.

This is the **second** story of **Epic 13 — Earn the Gate**, and the only one whose deliverable is a
**human act**. 13.1 decides what the corpus is and builds it; **13.2 measures it**; 13.3 records the
result and lets it decide. The dependency is strictly sequential — *"each story's output is the next
one's input"* (`epics.md:2485`).

**The story therefore has two halves, and the boundary is the whole point.** The **instrument** — the
adjudication record, the fold from human dispositions into the precision arithmetic, and the guards
that stop an unmeasured corpus certifying itself — is fully autonomous. The **judgement** — every
`TP`/`FP` disposition — is not, and no agent may supply it. See ⛔ ESCALATION.

### What it is NOT

- **No agent, LLM or heuristic adjudicates a finding.** A disposition enters the record only from the
  named human (**XAgent007**, `sprint-status.yaml:414`/`:416`, protocol §2 Engineering Lead). *An
  autonomous story that tags its own findings TP has measured nothing and has produced the exact
  artifact this epic exists to make impossible.* This is the single hardest constraint in the file.
- **It does not flip the gate.** `protocol_cleared` stays `False`. `INSTRUMENT_STATUS` stays
  `NOT_INDEPENDENTLY_VALIDATED`. Computing the outcome against §5 is **13.3**. 13.2 produces the
  *measurement*; 13.3 produces the *decision*.
- **It does not soften a threshold or a method.** ≥80% exact `Fraction`, 0 clean-repo blocking FP,
  N ≥ 5, **full-corpus exhaustive — not sampled** (§4). If the corpus is thin, that is a fact to
  record, never a reason to sample.
- **It does not re-open 13.1's corpus decision.** DN-1 (the PRD governs; cartridges are the recall
  instrument) is settled upstream. 13.2 *measures against* it.
- **It publishes nothing outward-facing.** No tag, no push beyond ordinary commits, no release.
  `DF-12-9-A` remains unauthorised and untouched.

### ⛔ Hard precondition — 13.1 must be `done`

`epics.md:2485`: *"13.1 -> 13.2 -> 13.3, strictly sequential. No parallelism."* At the time this file
was written **13.1 is `ready-for-dev`, not `done`** (`sprint-status.yaml:415`), and 13.1's own AC3b
(populate the corpus to N ≥ 5) **may terminate HALTED awaiting operator ratification**.

**Consequence, stated so it is not discovered late:** 13.2's AC1–AC6 (the instrument) are buildable
and provable against a synthetic fixture **whatever 13.1's AC3b did**. AC7 (the run itself) is
evaluable **only** if 13.1 delivered a populated manifest. If it did not, AC7's terminal state is
**`Unevaluable` — recorded, with the count of members actually available** (DN-5). It is never a pass,
and never a silent skip.

## Acceptance Criteria

### AC1: The flip path cannot certify a corpus it never measured — three defects, all reproduced by execution

**Given** the gate flips when `provisional is False`, which `replay_harness.py:327-331` computes as
`not (n >= floor_n and protocol_cleared and precision >= 4/5)` — and **all three inputs are
independently reachable without a single adjudicated finding**, as measured on `bc55e36` in §0.1

**Then** each of the three is closed, **additively**, and each closure carries RED-then-green evidence
at the real seam:

**AC1a — `n` must count the population that was actually adjudicated.** `compute_precision` accepts a
`registry=` injection (`:225`) but computes `n = registry_module.populated_planted_defect_count()`
(`:322`) — **the cartridge count, ignoring the injected population entirely**. Measured: injecting a
**2**-member registry still reports **`N=7`** and the gate string reads *"cleared … N=7 labeled
cartridges >= floor N=5"*. For the repository corpus 13.1 builds, `n` is therefore **structurally
wrong** and wrong in the direction that satisfies the floor.

**AC1b — a degenerate precision denominator can never clear the gate.** `precision` is
`Fraction(1, 1)` by convention when `TP + FP == 0` (`:318`) — *"no false positive emitted"* — and
`meets_threshold` compares that `1/1` against `Fraction(4, 5)` and passes. Measured: a corpus emitting
**nothing at all** (0 TP / 0 FP / 8 FN) returns `precision=1/1`, `provisional=False`, and the gate
string *"cleared"*. **An empty denominator is not an 80% result; it is no result.** The outcome must
be `Unevaluable`, recorded with its counts — never `cleared`.

**AC1c — §5's clean-repo false-positive condition must name the corpus it is measured over.**
`clean_repo_fp` accumulates only where `_is_clean_repo(spec)` holds — empty golden key **and**
`max_blocking == 0` (`:202-209`). A real-repository corpus member has no golden key and no
`max_blocking`, so on that corpus the condition is **vacuously 0 for every possible input**. Either it
is measured over the cartridge corpus and says so, or it is recorded **not applicable with a reason** —
a §5 condition that cannot fail is not a threshold.

⚠️ **AC1a's N comes from 13.1, not from a new count.** 13.1's AC3a delivers *"a function returning the
count of `eligible_for_n` members, compared against `VALIDATION_SET_FLOOR_N` — reusing the existing
constant, never forking a second floor"*. **Call it.** Authoring a second eligible-member count here is
the fork 13.1's DN-3 already refused, and it would let the two disagree about N — which is the exact
class of defect this story is closing.

**And** every change here is **additive with defaults preserving today's behaviour**: the 6.6/7.1
contract tests (`TC-ArgusAgent-DOGFOOD-001-11`/`-12`, `TC-ArgusAgent-PRECISION-001-08`/`-09`) must
pass **byte-unchanged** without being edited. A test that had to be adjusted to accommodate this
change is a signal the change was not additive.

**Why this is 13.2's work and not 13.3's:** 13.3 is the story that passes `protocol_cleared=True`. A
story that both repairs the instrument and flips the gate with it is measuring its own homework —
the shape this epic exists to delete.

### AC2: The protocol is amended BEFORE the run, and it says what one "finding" is

**Given** §7 locks *"precision is measured over **FINDINGS**, not repos"* (`protocol.md:160`) while
the implementation takes `emitted_keys_by_cartridge: dict[str, frozenset[MatchKey]]` and computes
`tp = len(tp_keys)` (`:276-287`) — **a count of distinct `(rule_id, verdict_eligible, advisory)`
CLASSES, not of findings.** Measured consequence: `minions-dogfood-proof.md:80-82` reports
`hardcoded_secret` ×**26** and `orphan_code` ×**92** as **one row each**; under the harness they are
**one key each**. A class with 92 findings and a class with 1 weigh identically — and on the
superseded Minions population (`deferred-work.md:823-830`, `hardcoded_secret` ×**2289**) the
divergence between the locked quantity and the computed one is three orders of magnitude.

**Then** the quantity is **decided and written down before any disposition is recorded** — either
adjudication is per **class** (and §4/§5/§7's wording is corrected to say class), or per **finding**
(and the harness needs a multiset the current signature cannot express). *Whichever is chosen, the
epic's own instruction binds:* **"the protocol is amended BEFORE the run, never reinterpreted during
it"** (`epics.md`, Story 13.2 AC2).

**And** the amendment is appended to the protocol change log (§3.4 — **strike, never erase**), carries
its date and reason, and covers the **corpus** change 13.1 made: §1 substrate, §2 roles, §3 budget and
§4 method must all read correctly against a repository corpus, not only a cartridge one.

**And** ordering is **mechanical, not a promise**: the adjudication record carries the protocol
version it was adjudicated under, and a committed guard asserts that version equals the protocol
change log's **current head**. A record adjudicated under a superseded protocol fails.

### AC3: The adjudication record — append-only, committed, machine-readable, and human-attributed

**Given** the epic's §3.4 clause: *"the adjudication record is **append-only**: a finding's
disposition is never rewritten, and a corrected judgement is recorded as a correction with its date
and reason"*

**Then** a committed, machine-readable adjudication record exists, and each row carries at minimum:
the `finding_match_key` identity `(rule_id, verdict_eligible, advisory)`, the corpus member it came
from, ≥1 **locator** (FR13 — the thing §4's borderline ladder re-examines), the **disposition**, the
**adjudicator id**, the **date**, a **reason**, and a `supersedes` field for corrections.

**And** the disposition vocabulary is **closed and raises** on an unregistered member (the
`DF-10-4-E` exhaustive-dispatch shape, as 12.5/12.8 already do). It must include a state for *"looked
at, could not decide"* — §4's **borderline** ladder is a first-class outcome, not an absence.

**And** the record is a **committed repository artifact**. ⚠️ **Measured: `.gitignore:19` ignores
`.argus/`.** The 6.7 `DecisionRecordWriter` writes to `.argus/decisions/` — *gate evidence that is not
in git is not evidence*. See DN-3 for what to reuse and what not to.

**And** `NFR-S1` holds absolutely: rule-id provenance, locators and counts only. **No source byte, no
secret value, no absolute host path** — the same contract `minions-dogfood-proof.md` already satisfies.

**And** the human attribution is **asserted, not assumed**: a guard checks every disposition's
adjudicator id is a role registered in protocol §2. An unattributed disposition is a failure.

### AC4: Exhaustiveness is proven, not asserted (§4 — full-corpus, not sampled)

**Given** §4: *"Precision is computed over the **FULL** populated corpus … not a sample … Every
emitted finding is classified; nothing is sampled out"* (`protocol.md:87-89`)

**Then** a committed guard proves **every** emitted key in the corpus finding set has exactly **one
live disposition** (superseded rows excluded). A member with any undisposed key makes the run
**`Unevaluable`, recorded with the residual count** — never a pass over the adjudicated subset.

**And non-vacuity is mandatory** (the `-39` argparse-internals precedent, `AI-E11-1`): the guard
asserts it extracted **> 0** rows before asserting anything about them. A guard that silently iterates
an empty record passes forever, and that is the failure mode with the worst possible blast radius
here.

### AC5: Actual expert-hours are recorded against §3's ceiling — recorded, not enforced

**Given** §3: *"Per gate-flip adjudication run (the full corpus at N≥5): ≤ **4 expert-hours**"*
(`protocol.md:76-78`), and the epic's *"actual expert-hours are **recorded**, so the next run can be
scheduled on evidence rather than on the estimate"*

**Then** the actual hours are a **field on the record**, not prose, and they are compared against the
4-hour ceiling **as a report**. Exceeding it is **not a failure** — §3 says the budget is *"a ceiling,
not a target"* and that overrun *"is a signal the cartridge is ambiguous"* (`:80-81`). Record the
overrun and what made it expensive; never trim the adjudication to fit the estimate.

### AC6: The determinism precondition is proven BEFORE any disposition is recorded

**Given** §4's last bullet: *"Adjudication is only valid over a **byte-reproducible** harness run
(NFR-P1): the harness MUST produce identical per-cartridge rows + precision ratio across two runs over
the same corpus **before any pass/fail is recorded**"* (`protocol.md:105-107`)

**Then** the reproducibility check runs first, **reusing the existing check** — never a second one —
and its result is recorded on the adjudication record. A non-reproducible run makes the adjudication
**invalid**, and the record says so rather than carrying dispositions that rest on nothing.

### AC7: The run — the human half (see ⛔ ESCALATION)

**Given** 13.1 delivered a populated validation-set manifest at N ≥ 5, and the protocol has been
amended per AC2

**Then** the named human adjudicates **every** emitted finding per §4 as written: blocking findings
judged genuinely real by inspecting the cited locator; borderline → locator re-examination →
golden-key correction → external tie-break; each step recorded.

**And if the corpus is absent or under-populated** — the live outcome if 13.1's AC3b HALTED — the
result is **`Unevaluable`, recorded with the member count actually available and what would close the
gap**. Under **no** circumstance is a disposition invented, inferred, or defaulted to make AC4's
exhaustiveness guard go green. **A fabricated adjudication in the story that defines adjudication is
the worst available outcome, and it is worse than an unfinished story.**

### AC8: Every document and ledger entry this story touches is CORRECTED, never loosened

1. **`deferred-work.md` is append-only** — `git diff --numstat` must be `+n / -0`.
   - `DF-6-6-A`, `DF-6-6-A-P1`, `DF-6-6-A-P2`, `DF-7-2-A` — the epic requires each is *"closed here or
     its remaining scope re-recorded with a reason — **none is left pointing at a run that has now
     happened**"*. Measured: all four are `OPEN, owned` with `target_story:
     13-2-adjudicate-every-finding-by-a-named-human` (`deferred-work.md:1553-1573`), while **all four
     original bodies still carry the stale `target_story: epic-7-minions-dogfood-precision`**
     (`:329`, `:392`, `:428`, `:450`) — which is correct under §3.4 (originals are not rewritten) and
     is exactly why the **closing** note must be unambiguous about which record supersedes which.
2. **`AI-E12-6` — the ledger-claim cross-check guard.** The Epic-12 retrospective's ranked item **#7**
   reads: *"Land the ledger-claim cross-check guard **before 13.2 files its adjudication record**"*
   (`epic-12-retro-2026-08-15.md:324`). **Measured: it does not exist** (no test extracts a story
   file's claimed `DF-*` closures and checks the ledger). This story is the one it was written for —
   land it, or record a dated decision not to with a named owner.
3. **`AI-E12-3` — the four falsely-closed entries.** The same retrospective ranks at **#4**: *"Dispose
   the four falsely-closed ledger entries **before Epic 13**, whose entire deliverable is a recorded
   human adjudication of exactly this shape"* (`:321`). Measured still open: `DF-8-3-A`,
   `DF-10-4-A`, `DF-10-4-B`, `DF-12-3-A`. **No story owns them.** Rule on them or re-home each with a
   named owner — `AI-E9-8` forbids leaving an entry without one.
4. **`AI-E12-5` — the guard-adequacy clause is still unregistered.** Measured: `grep -c
   "GUARD-ADEQUACY" architecture.md` → **0**, across 16 §Enforcement rules. This is now the **fourth**
   consecutive retrospective to ask, and `:322` names the reason it matters here: *"Story 13.3 asks
   for a non-vacuity proof on the single most consequential guard in the project, and the rule that
   answers it has been unregistered for three epics."* Register it, or re-home it with a named owner.
5. **No guard is narrower than its AC** (`AI-E8-6`), and every new guard satisfies the
   **GUARD-ADEQUACY CLAUSE** (`AI-E11-1`): (i) its observable is named, (ii) the defect is demonstrated
   to move it **at the real seam**, (iii) at least one adversarial variant is **generated** from the
   record it closes over.
6. **NFR-M1**: no module or test file crosses **1200 lines**. Headroom is measured in §0 and two files
   are effectively full.

---

## Developer Context & Guardrails

### §0 — Premise re-measurement (this project's create-story control, ten-for-ten since Epic 11)

Measured **2026-08-16 on `bc55e36`** (HEAD; `origin/master` == HEAD, 0 ahead / 0 behind), by
**execution**. Per the Epic-11 retro §3.2 refinement and `AI-E12-10`, **confirmations are recorded as
well as divergences.**

| Premise, as `epics.md` / `sprint-status.yaml` state it | Re-measured on `bc55e36` | Consequence |
|---|---|---|
| *"the adjudicator is **named in `sprint-status.yaml`**, and the story does not begin otherwise"* (the start condition) | ✅ **HOLDS.** `sprint-status.yaml:414`/`:416` name **XAgent007**; `deferred-work.md:1553-1560` records the same as `DF-7-2-A`'s owner, Engineering Lead role, protocol §2 primary | **The start condition is MET.** The QA-Lead second and external tie-break stay unfilled until a borderline finding requires them (§4) |
| *"DF-7-2-A … has been open and unowned since Epic 7"* | ✅ **HOLDS, with the owner since named.** `status: OPEN, owned`; `target_story: 13-2-…` | AC8.1 |
| *"§4 method — full-corpus exhaustive, not sampled"* | ✅ **HOLDS.** `protocol.md:87-89` | AC4 |
| *"§3 budgets ≤4 expert-hours for a full gate-flip adjudication at N≥5"* | ✅ **EXACT.** `protocol.md:76-78`; and `:80-81` states the budget is *"a ceiling, not a target"* | **AC5 — and the ceiling is a report, not a gate** |
| *"§3.4 evidence immutability → the adjudication record is append-only"* | ✅ **HOLDS as a requirement, and NOTHING IMPLEMENTS IT.** No adjudication record of any kind exists in the tree | **AC3 — this story builds it** |
| *"precision is measured over **FINDINGS**, not repos"* (§7 OI1 lock) | ❌ **DIVERGES FROM THE IMPLEMENTATION.** `compute_precision` takes `frozenset[MatchKey]` and does `tp = len(tp_keys)` (`:276-287`) — distinct **CLASSES**. `minions-dogfood-proof.md:80-82`: `hardcoded_secret` ×26 and `orphan_code` ×92 collapse to **one key each** | 🚨 **AC2.** The protocol's locked quantity and the harness's arithmetic are not the same quantity |
| *"`replay_harness.py:223` is where `protocol_cleared` is passed"* (13.3's premise, verified early because AC1 edits the same function) | ⚠️ **DRIFTED BY 3.** `compute_precision` is defined at **`:222`**; `protocol_cleared: bool = False` is at **`:226`** | Same divergence 13.1 recorded. Confirmed independently |
| `protocol_cleared` is never passed `True` from production | ✅ **CONFIRMED.** `tests/test_instrument_disclosure.py::-46` enforces it, and the exemption set names exactly two test files | **AC1's changes must not add a third without registering it** — see §0.2 |
| *"`n` reflects the corpus being measured"* (implied by every §5 threshold) | ❌ **FALSE — MEASURED BY EXECUTION.** Injecting a **2**-member registry still reports `N=7` | 🚨 **AC1a.** See §0.1 |
| *"precision ≥ 4/5 means 80% of blocking findings were real"* | ❌ **FALSE ON AN EMPTY DENOMINATOR — MEASURED.** 0 TP / 0 FP / 8 FN → `precision=1/1`, `provisional=False`, gate *"cleared"* | 🚨 **AC1b.** See §0.1 |
| *"0 clean-repo blocking FP is a threshold"* | ❌ **VACUOUS ON A REPOSITORY CORPUS.** `_is_clean_repo` (`:202-209`) needs an empty golden key **and** `max_blocking == 0`; no repo-corpus member has either | 🚨 **AC1c** |
| The live adjudication target has blocking findings to adjudicate | ❌ **IT HAS NONE.** `minions-dogfood-proof.md:80-82`: all three classes are `verdict-eligible: False` / `advisory: True`. `compute_precision` counts an FP only when `key[1]` is True (`:283`) | **The Argus self-audit cannot produce a precision measurement at all** — one more reason 13.1's real-repository corpus is the prerequisite |
| *"the record can reuse the 6.7 append-only decision writer"* (the obvious reuse) | ❌ **IT CANNOT, TWICE OVER.** `DecisionRecordWriter.append` accepts **only** an `EscalationResolution` (`decision_record.py:180-184`) — a STOP/PROCEED HITL semantic — and writes under `.argus/decisions/`, which **`.gitignore:19` ignores** | **DN-3.** Reuse the discipline, not the class |
| `AI-E12-6` — the ledger-claim cross-check guard exists | ❌ **DOES NOT EXIST.** No test extracts a story file's claimed `DF-*` closures | **AC8.2.** The retro asked for it *"before 13.2 files its adjudication record"* |
| `AI-E12-5` — the guard-adequacy clause is registered in §Enforcement | ❌ **NOT REGISTERED.** `grep -c "GUARD-ADEQUACY" architecture.md` → **0**, over 16 §Enforcement rules | **AC8.4.** Fourth consecutive retrospective |
| `AI-E12-3` — the four falsely-closed entries are disposed | ❌ **STILL OPEN.** `DF-8-3-A`, `DF-10-4-A`, `DF-10-4-B`, `DF-12-3-A` — and no story owns them | **AC8.3** |
| `AI-E12-1` — register `epic-12-retro-2026-08-15.md` in `_STATUS_DOCUMENTS` | ✅ **ALREADY DONE.** `tests/test_evidence_citation.py:125` | Do not redo. Same as 13.1 recorded |
| `sprint-status.yaml:415` states *"`argus/pipeline.py` is **1005** lines"* | ❌ **A THIRD DIFFERENT NUMBER FOR ONE FILE.** Measured: **1111**. `AI-E10-8` said 1331; the 13.1 story file says 1111 | **Confirms the story's own thesis:** a hand-transcribed number drifts. This is why AC1's figures are derived |
| Nothing has been published | ✅ **HOLDS.** `git tag -l` → **empty** (0 tags); `origin/master` == `bc55e36` == HEAD | This story stays inside that. `DF-12-9-A` untouched |
| Baseline gates on `bc55e36` | ✅ **MEASURED BY EXECUTION.** `pytest` **1543 collected**, full run **exit code 0** (no failure or error); `mypy` **clean, 83 source files**; `bandit` **19 Low / 0 Medium / 0 High**. 13.1 independently recorded **1543 passed / 0 failed / 0 skipped** on this same sha | Report deltas against these exact numbers, never "all green". **A skip appearing is a regression signal** |
| Test-case id high-water marks | Measured: `PRECISION-001-**20**` · `CARTRIDGE-001-**15**` · `DOGFOOD-001-**52**` · `DOCS-001-**72**` · `HITL-001-**31**` | New ids continue from these. **Opening a new area is a decision that needs a recorded reason** |
| NFR-M1 headroom (files this story may touch) | `argus/precision/replay_harness.py` **391** · `argus/governance/decision_record.py` **253** · `tests/test_precision_replay.py` **513** · `tests/test_hitl_escalation.py` **620** · `tests/test_dogfood_plan.py` **655** · `tests/test_release_preflight.py` **938** · `tests/test_dogfood_proof.py` **1106** (94 left) · `tests/test_instrument_disclosure.py` **1179** (21 left) · `tests/test_evidence_citation.py` **1199** (**1 left**) | 🚨 **Two files are effectively full.** New guards go in a **new module**; apply 12.8's cohesion-split precedent, do not shave |

### §0.1 — THE FLIP PATH IS REACHABLE WITHOUT A SINGLE ADJUDICATED FINDING

Reproduced on `bc55e36`. **Run these first — they are AC1's RED, and they already fail today.**

```python
import sys; sys.path.insert(0, "tests/cartridges")
from argus.precision.replay_harness import compute_precision
import _registry as r

# (1) EMPTY DENOMINATOR — a corpus that emits nothing at all.
empty = {s.cartridge_id: frozenset() for s in r.CARTRIDGE_REGISTRY}
res = compute_precision(empty, protocol_cleared=True)
# MEASURED: tp=0 fp=0 fn=8 | precision=1/1 | provisional=False
#           gate_status -> "cleared (Story 6.6 precision harness; precision=1/1 >= 4/5 ..."

# (2) WRONG N — inject a 2-member population; n still counts CARTRIDGES.
custom = r.CARTRIDGE_REGISTRY[:2]
res2 = compute_precision({s.cartridge_id: frozenset() for s in custom},
                         registry=custom, protocol_cleared=True)
# MEASURED: rows=2 | n=7 | floor_n=5 | provisional=False
#           gate_status -> "cleared ... N=7 labeled cartridges >= floor N=5"
```

**Read the two together.** A corpus of **two** members that emitted **zero** findings reports
`N=7`, `precision=1/1`, and a gate status that says **cleared** — the moment a caller passes
`protocol_cleared=True`. The only thing standing between this repository and a false cleared claim
today is a human's decision not to pass that flag. **13.2 is the story that produces the value 13.3
will pass.** Closing this is therefore not defensive polish; it is the story's first job.

**Add the third to your RED set:** `_is_clean_repo` (`:202-209`) can never be `True` for a
repository-corpus member, so §5's *"0 clean-repo blocking FP"* condition is satisfied by
construction on the corpus that actually gates externalization (AC1c).

### §0.2 — The two guards that will go RED on you, and what each red means

| Guard | Trips when | The correct response |
|---|---|---|
| `tests/test_instrument_disclosure.py` `TC-ArgusAgent-DOCS-001-46` (`:587-635`) | **(a)** any `argus/**` call site passes `protocol_cleared=True` — that is **13.3's** red, not yours; **(b)** any **test** file passes it that is not in `_PROTOCOL_CLEARED_TEST_EXEMPTIONS` (`:266-276`), measured today as exactly `tests/test_dogfood_plan.py` + `tests/test_precision_replay.py` | AC1's RED tests **will** pass `protocol_cleared=True`. **Register the new file BY NAME WITH ITS REASON.** The set fails in **both** directions — a stale entry fails too. ⚠️ That file has **21 lines** of NFR-M1 headroom |
| `tests/test_module_size_ceiling.py` (`TC-ArgusAgent-MAINT-001-01..-05`) | any tracked `.py` crosses 1200 lines; it closes over `git ls-files -- '*.py'`, so a file is swept the moment it is `git add`-ed | Do not shave a file to fit. Split for cohesion (12.8) or file a dated, owned `_EXEMPT_BY_DESIGN` entry with a `deferred-work.md` id |

### §0.3 — THE INVENTORY: what exists to adjudicate WITH, and what is missing

| Instrument | Lives at | State on `bc55e36` |
|---|---|---|
| The precision fold (TP/FP/FN → exact `Fraction`) | `argus/precision/replay_harness.py:222` | ✅ Exists. **Reuse — do not fork.** Needs AC1's three additive corrections |
| The shared match key | `replay_harness.py:117` `finding_match_key` | ✅ Exists. `(rule_id, verdict_eligible, advisory)`. **One key, no second one** (DN-MATCH-KEY-REUSE) |
| The gate-status string | `replay_harness.py:356` `precision_gate_status_for` | ✅ Exists. **Extend, never fork a second marker** |
| Append-only, prev-hash-chained record discipline | `argus/governance/decision_record.py` | ⚠️ Exists but is **HITL-STOP-shaped and gitignored**. Discipline reusable; class is not (DN-3) |
| The canonical serializer | `argus/store/canonical.py:230` `dumps_bytes` | ✅ **The only serializer** (AR4). Never `json.dumps` |
| The three-outcome discipline (`Refusal` / `Unevaluable` / pass) | `scripts/release_preflight.py:159` | ✅ Exists. **The precedent for DN-5** |
| The validation-set manifest | `tests/corpus/_manifest.py` | ⛔ **13.1 builds it.** Absent today |
| **The adjudication record** | **nowhere** | ⛔ **This story builds it** |
| Human dispositions | **nowhere** | ⛔ **XAgent007 supplies them. No agent may.** |

### Files to touch

**NEW.** Decide repository-only vs. shipped **deliberately** and record the reason: `tests/` is absent
from the built distribution (`DF-9-2-A`), which is why `replay_harness.py:93-99` reaches the registry
through a single lazy edge. Anything reaching the adjudication record from `argus/**` inherits that
constraint — **a module-level import of a repository-only path ships a wheel that cannot import, and
`tests/test_built_distribution.py` is the guard that catches it.**

| Path (indicative) | Purpose |
|---|---|
| the adjudication-record schema + reader | AC3. Mirror `_registry.py`'s frozen-spec shape and `decision_record.py`'s supersede-never-erase discipline. Closed disposition vocabulary that **raises** |
| the committed record artifact itself | AC3/AC7. **In git** — `.argus/` is ignored (`.gitignore:19`) |
| a new guard module for AC1–AC4 | 🚨 **Must be new.** `test_evidence_citation.py` is at **1199/1200** and `test_instrument_disclosure.py` at **1179/1200** |

**UPDATE — read each completely before editing.**

| Path | What it does today | What must be preserved |
|---|---|---|
| `argus/precision/replay_harness.py` (391) | `compute_precision` (`:222`); `registry=` injection (`:225`); `protocol_cleared` default `False` (`:226`); `n` from `populated_planted_defect_count()` (`:322`); `provisional` (`:327-331`); lazy `_registry_module()` (`:93-99`); `_is_clean_repo` (`:202-209`) | **Additive only.** New parameters default to today's behaviour. `Fraction` only — never a float (AR4). **One impure edge** — adding a second way to reach a registry is the fork this codebase keeps refusing. `protocol_cleared` is **never** defaulted `True` and **never** passed `True` from `argus/**` |
| `precision-validation-protocol.md` (175) | §1 substrate, §2 roles (`:57-63`), §3 budget (`:69-81`), §4 method (`:87-107`), §5 thresholds (`:113-122`), §6 phases, §7 OI1 (`:157-167`), change log (`:175`) | §7 is **not softened** — its own heading says so. §3.4: **append to the change log, strike in place, never erase.** ⚠️ 13.1 also amends §1/§4/§5/§6 — **rebase onto 13.1's amended text; do not overwrite it** |
| `tests/cartridges/_registry.py` (332) | `VALIDATION_SET_FLOOR_N = 5`; `populated_planted_defect_count()`; `precision_gate_status()` | **One floor, two populations** (13.1 DN-3). Do not fork a second floor |
| `_bmad-output/…/deferred-work.md` (3918) | Append-only ledger | `+n / -0`. AC8.1–AC8.3 |
| `_bmad-output/…/architecture.md` (1280) | §Enforcement (16 rules, `:1031`+); the model form is *rule text + enforcing module + test ids* | Strike-not-delete. AC8.4 registers the guard-adequacy clause in that exact form |
| `argus/dogfood/proof_run.py` (679) / `minions-dogfood-proof.md` (89) | 13.1 rewires `:642-647` to derive the figure | **Only if AC1 changes what that call renders.** Then the `DF-8-5-B`/`DF-10-4-D` bootstrap applies — see Testing |

### Locked decisions this story must cite rather than reopen

| Locked | Where | Consequence here |
|---|---|---|
| **OI1 — N LOCKED at 5; no over-claim; the harness never silently clears the gate** | protocol §7 | AC1 makes the lock **true**, rather than dependent on a caller's restraint |
| **The gate flips only when all four §5 conditions hold AND the adjudication run is recorded** | protocol §5 (`:120-122`), §6.4 | 13.2 produces the *recorded run*. It does not evaluate the four |
| **`protocol_cleared=True` is passed by the harness *caller*, never defaulted** | `replay_harness.py:226` | Untouched. 13.3 owns the flip |
| **Precision is an exact `Fraction`, rendered `"num/den"`** | AR4; `_ratio_string` (`:212`) | No float, no rounding, no percentage literal |
| **DN-MATCH-KEY-REUSE — one match key, no second, divergent one** | `replay_harness.py:32-36` | The record keys on `finding_match_key`. Never a parallel identity |
| **NFR-S1 — no source or secret bytes in any artifact** | architecture §G; 4.3/4.4 CI-blocking canary suite | The record carries locators + rule-id provenance + counts. Nothing else |
| **`DF-9-2-A` — `tests/` is absent from the built distribution** | `replay_harness.py:85-88` | Anything `argus/**` reads from `tests/` goes behind the existing lazy edge |
| **`DF-10-4-E` — an exhaustive dispatch RAISES on an unregistered member** | 12.5 `_downgrade_sentence`; 12.8 AC4 | AC3's closed disposition vocabulary takes this shape |
| **`AI-E9-7` / single-source** — never publish a prose copy of a pinned constant | architecture §Enforcement | Every figure in the record is derived |
| **`AI-E9-8`** — never `target_story: NONE` without a named human | Epic-9 retro | AC8.2/8.3/8.4 |
| **`AI-E8-6`** — a guard narrower than its own AC is a breach | Epic-8 retro | AC8.5 |
| **`AI-E11-1` GUARD-ADEQUACY CLAUSE** — observable named, defect moved **at the real seam**, adversarial variant **generated** | Epic-11 retro §3.1 (**still unregistered** — AC8.4) | Every new guard here |
| **`DF-8-5-B` / `DF-10-4-D` bootstrap** — commit the `argus/` delta → regenerate artifacts → commit separately | 12.5–12.8 Debug Logs; `AI-E12-11` | Applies **iff** AC1 changes what a generated artifact renders |
| **§3.4 evidence immutability** — supersede, strike, never erase | architecture §3.4 | The record's correction semantics **are** this rule, mechanised |
| **Nothing outward-facing** | `DF-12-9-A`; `AI-E12-2` | No tag, no release, no visibility change |

### Decisions taken by this story (record each in the Dev Agent Record with its rejected alternative)

- **DN-1 — The adjudication record IS the golden key for the repository corpus.** Protocol §2
  already says exactly this: *"A finding's classification (TP/FP/FN) is **mechanically derived** by
  the harness from the golden key; the human roles above adjudicate the **golden key itself**"*
  (`protocol.md:61-63`). So the human dispositions become the ground truth, and the **existing** fold
  computes precision from them through the **existing** `registry=` injection seam. *Rejected
  alternative:* a second precision function for repository corpora — two folds is how two corpora
  happened, and the arithmetic that gates externalization must have exactly one implementation.
- **DN-2 — Every harness change is an ADDITIVE keyword with a default that preserves today's
  behaviour.** *Rejected alternative:* changing `compute_precision`'s semantics in place. It would move
  every existing caller's result and force edits to the 6.6/7.1 contract tests — and a contract test
  edited to accommodate a change has stopped being a contract test.
- **DN-3 — The record is a committed repository artifact; the 6.7 writer is reused as a
  *discipline*, not as a class.** Measured twice over: `DecisionRecordWriter.append` accepts only an
  `EscalationResolution` (`decision_record.py:180-184`), and it writes under `.argus/`, which
  `.gitignore:19` ignores. *Rejected alternative:* shoehorn adjudications into `EscalationResolution`.
  A false record entry is worse than a coy one (12.6 / DN-8), and gate evidence outside git is not
  evidence.
- **DN-4 — Reuse the canonical serializer and the supersede-never-erase chain; author no second
  serializer, hasher, or envelope.** `argus/store/canonical.py:230` is the one serializer (AR4).
- **DN-5 — A degenerate, partial, or absent adjudication is `Unevaluable`, recorded — never a silent
  skip and never a pass.** The `scripts/release_preflight.py:159` three-outcome precedent. *A green
  run that silently skipped the adjudication is worse than a red one.*
- **DN-6 — No agent adjudicates.** Dispositions enter only from the named human, and the record
  asserts its adjudicator against protocol §2's role table. *Rejected alternative:* an LLM
  pre-classification the human "reviews". Measured reason: `minions-dogfood-proof.md:76` already
  reserves the `TP/FP` column *"left empty for the human"* — the design has held that line since
  Story 7.2, and this is the story where breaking it would be invisible.
- **DN-7 — The gate is not flipped here, and the disclosure is not touched.** `protocol_cleared`
  stays `False`; `INSTRUMENT_STATUS` stays `NOT_INDEPENDENTLY_VALIDATED`;
  `TC-ArgusAgent-DOCS-001-46` stays green. Turning it red is **13.3's** job and its red is that
  guard working.

### Toolchain and external facts, verified on this machine 2026-08-16

- HEAD `bc55e36`; `origin/master` identical (0 ahead / 0 behind); `git tag -l` **empty**; the working
  tree carries six untracked non-source artifacts (`.bmad-drift-audit/`, `argusdemo/`,
  `bmad-dev-loop-pack/`, three `_bmad-output/audit-reports/` folders) — `AI-E12-12` owns them; **do
  not sweep them as part of this story**, and never let one enter the corpus.
- Python **3.11** via `uv run --python 3.11`. Gates are **local** — `architecture.md` §H: a local run
  is necessary, never sufficient, and is labelled **LOCAL**. **CI evidence: NOT ESTABLISHED** for any
  Epic-10/-11/-12/-13 sha (`audit-ci.yml`'s latest run covers `00c8d1b`, 2026-08-09).
- ⚠️ **Local gates are Windows-only here; CI runs an ubuntu matrix.** A green local suite has already
  shipped POSIX-only bugs to master. Anything path-shaped in the record (locators, member ids, staging
  paths) gets `pathlib` and forward-slash normalisation, never string concatenation.
- **The suite must not reach the network** (13.1 DN-5, inherited).
- **No new third-party dependency is required or permitted by this story.** The instrument is built
  from the stdlib (`fractions`, `dataclasses`, `pathlib`) plus what is already pinned — `pytest`,
  `mypy`, `bandit`, and the project's own `argus.store.canonical` serializer. Adding a dependency to a
  story whose entire subject is the credibility of a measurement is a decision that needs a recorded
  reason, not a convenience.
- No `project-context.md` exists in this repository (searched `**/project-context.md`). The
  architecture, `precision-validation-protocol.md` and this file are the context.

### Previous story intelligence — traps already paid for, do not pay again

From Story 13.1 (the immediately preceding story, `ready-for-dev` at the time of writing) and
Epics 10–12:

1. **The §0 re-measurement is not ceremony.** It has caught a materially wrong premise in every story
   since Epic 11 — this time, three *executable* defects in the gate-flip path plus four unregistered
   retrospective items. **Re-measure on your own baseline (Task 1)** — §0 was measured before you
   started, and 13.1 will have landed underneath you.
2. **13.1 lands in the same files.** `precision-validation-protocol.md`, `deferred-work.md`,
   `architecture.md` and `tests/cartridges/_registry.py` are all touched by 13.1 first. **Rebase onto
   its text; never overwrite an amendment you did not make.** §3.4 makes overwriting a defect, not a
   merge conflict.
3. **The artifact-currency bootstrap bites whenever `argus/**` moves** (`AI-E12-11`; ten of Epic 12's
   28 commits). Sequence: commit the `argus/` delta → regenerate the artifacts → commit the
   regeneration separately.
4. **Commit each story's delta as the story closes** (`AI-E10-7`). Do not implement into one dirty
   working tree — six untracked artifacts are already sitting there.
5. **A story record that claims a ledger closure the ledger never received is the live defect class**
   (`AI-E12-3`, `AI-E12-6`; four such claims from Stories 12.4/12.5 are still being dispositioned).
   **This story is the one the cross-check guard was written for** (AC8.2). If your Completion Notes
   say "closed `DF-7-2-A`", `deferred-work.md` must show it, **in the same commit**.
6. **The resumed-session integrity check** (`AI-E11-11` / `AI-E12-8`): if this session resumed after a
   transport error, re-derive state from the tree before continuing. A dev agent already died
   mid-story once and left a partially-applied change.
7. **12.6 / DN-7** — need a helper from a `_`-prefixed API? **Promote it to public**; never reach
   through.
8. **12.6 / DN-8** — a false registry entry is worse than a coy docstring. Applied here: an
   `UNADJUDICATED` row that says so beats a `TP` row that guessed.

### Testing requirements

- **Framework/gates, all run locally before hand-off:** `pytest` (full suite — the baseline on
  `bc55e36` is **1543 collected, exit 0, 0 failed / 0 skipped**; a *skip* appearing is a regression
  signal), `mypy` (**clean, 83 source files**), `bandit` (**19 Low / 0 Medium / 0 High**). Report each
  with its actual numbers in the Dev Agent Record — never "all green".
- **Test ids continue from the measured high-water marks:** `PRECISION-001-21+`, `CARTRIDGE-001-16+`,
  `DOGFOOD-001-53+`, `DOCS-001-73+`, `HITL-001-32+`. Opening a new area is a decision that needs a
  recorded reason, not a convenience.
- **RED-then-green is mandatory evidence, at the real seam** (`AI-E11-1` clause ii). For each new
  guard capture in the Debug Log: the observable, the planted defect, the RED output, the fix, the
  GREEN output. Specifically —
  - **AC1a/AC1b**: the two §0.1 snippets are your RED. They must go from *"provisional=False /
    cleared"* to *"Unevaluable, recorded"* — and the **existing** 6.6/7.1 contract tests must stay
    green **unedited**.
  - **AC1c**: a repository-corpus member must not be able to satisfy the clean-repo condition
    silently.
  - **AC2**: change the protocol's change-log head → the version guard goes RED.
  - **AC3**: a disposition with an unregistered vocabulary member **raises**; a correction that
    rewrites a prior row instead of superseding it **fails**; a row with a source byte in it **fails**.
  - **AC4**: remove one disposition from a fully-adjudicated fixture → the exhaustiveness guard must
    report `Unevaluable`, not pass. **Generate** at least one adversarial variant **from the record
    itself**, not hand-written.
- **Non-vacuity**: any guard that walks the record asserts it extracted **> 0** rows first (the `-39`
  argparse-internals precedent). A guard that silently iterates an empty adjudication record passes
  forever — and here that guard is the one protecting the externalization gate.
- **Determinism precondition (§4)**: prove byte-reproducibility across two runs **before** recording
  any disposition, **reusing the existing check** — not a new one.

---

## Tasks & Subtasks

- [x] **Task 0 — Confirm the precondition (AC: all)**
  - [x] Verify 13.1 is `done` in `sprint-status.yaml` and its corpus manifest exists
  - [x] Record whether 13.1's AC3b completed or HALTED — it decides AC7's terminal state
  - [x] Re-assert the start condition by execution: the adjudicator is named
- [x] **Task 1 — Re-measure every §0/§0.1/§0.3 premise on your implementation baseline (AC: all)**
  - [x] Re-run the two §0.1 snippets; record the actual output in Debug Log §1
  - [x] Record confirmations *and* divergences; if a premise moved under 13.1, say so before acting
- [x] **Task 2 — Close the three flip-path defects, additively (AC1)**
  - [x] AC1a: `n` counts the adjudicated population; RED-then-green against the 2-member reproduction
  - [x] AC1b: an empty denominator is `Unevaluable`, never `cleared`; RED against the 0/0/8 reproduction
  - [x] AC1c: §5's clean-repo condition names its corpus or is recorded not-applicable with a reason
  - [x] Prove additivity: the 6.6/7.1 contract tests pass **unedited**
  - [x] Register any new `protocol_cleared=True` test file in `_PROTOCOL_CLEARED_TEST_EXEMPTIONS`
- [x] **Task 3 — Amend the protocol BEFORE the run (AC2)**
  - [x] Decide and record the unit: per finding **or** per class; correct §4/§5/§7's wording to match
  - [x] Amend §1/§2/§3/§4 for the repository corpus, rebased onto 13.1's amendments
  - [x] Append to the change log with date + reason (strike, never erase)
  - [x] Guard: the record's protocol version equals the change log head; RED on a superseded version
- [x] **Task 4 — Build the adjudication record (AC3)**
  - [x] Schema keyed on `finding_match_key`; closed disposition vocabulary that **raises**
  - [x] Append-only with supersession; a correction carries its date and reason
  - [x] Committed in git (**not** `.argus/` — `.gitignore:19`); NFR-S1 asserted
  - [x] Adjudicator attribution checked against protocol §2's role table
- [x] **Task 5 — Prove exhaustiveness and determinism (AC4, AC6)**
  - [x] Every emitted key has exactly one live disposition; residuals → `Unevaluable`, counted
  - [x] Non-vacuity: > 0 rows asserted before any other assertion
  - [x] Byte-reproducibility proven first, via the existing check, recorded on the record
- [x] **Task 6 — Record expert-hours (AC5)**
  - [x] Actual hours as a field; compared to §3's ≤4h as a **report**, not a gate
  - [x] If exceeded, record what made it expensive — never trim the adjudication to fit
- [x] **Task 7 — The run (AC7 — see ESCALATION)**
  - [x] Present the adjudication-ready finding set to the named human, per §4 as written
  - [ ] ⛔ **HALTED — awaiting the named adjudicator (XAgent007).** Record each disposition
        with its locator, reason, date and adjudicator. **0 of 31 recorded.** No agent may
        supply one (DN-6 / ESCALATION); see Debug Log §7 and `DF-13-2-A`
  - [x] If the corpus is absent/under-populated: mark **`Unevaluable` — recorded**, with the count and
        what would close the gap. **Invent nothing.**
- [x] **Task 8 — Ledger and documents (AC8)**
  - [x] Close or re-scope `DF-6-6-A` / `-P1` / `-P2` / `DF-7-2-A` with reasons; `+n / -0`
  - [x] Land `AI-E12-6`'s ledger-claim cross-check guard, or decide it with a named owner
  - [x] Rule on `AI-E12-3`'s four entries (`DF-8-3-A`, `DF-10-4-A`, `DF-10-4-B`, `DF-12-3-A`)
  - [x] Register the guard-adequacy clause in §Enforcement (`AI-E12-5`), or re-home it with an owner
  - [x] Note `AI-E12-1`'s already-satisfied half rather than redoing it
- [x] **Task 9 — Gates and hand-off**
  - [x] `pytest` / `mypy` / `bandit` with actual numbers, labelled **LOCAL**
  - [x] NFR-M1 re-measured on every touched file (two are effectively full)
  - [x] `protocol_cleared` still `False` everywhere in `argus/**`; `-46` still green
  - [x] Nothing outward-facing performed; re-assert by execution (`git tag -l`, remote unmoved)

---

## ⛔ ESCALATION — the judgement this story cannot give itself (AC7)

**AC1–AC6 and AC8 are fully autonomous. AC7 is not, and the boundary is the reason this epic exists.**

`DF-7-2-A` has said it since Epic 7: the human TP/FP adjudication is *"the ONLY step that can clear
the attested gate"*. Protocol §2 assigns it to the **Engineering Lead** with a **QA Lead** second.
**The named human already exists — XAgent007** (`sprint-status.yaml:414`/`:416`) — so this is a
bounded, explicit act, not an open-ended block. What is needed from them:

1. **A disposition for every emitted finding** in the corpus, per §4 as written.
2. **The actual expert-hours spent** (AC5).
3. **A QA-Lead second and/or external tie-break** only if a borderline finding requires one (§4) —
   both roles are currently unfilled, and filling them is itself an operator act.

**If the adjudication is not obtained in this session:** complete AC1–AC6 and AC8 in full, land the
instrument with its guards proven against a synthetic fixture, and mark AC7 **HALTED — awaiting the
named adjudicator**, following the Story 12.9 / AC9 precedent where a halt is the *designed* terminal
state and does not block the story's pass.

> **The one thing that must not happen.** Do not populate dispositions to make AC4's exhaustiveness
> guard go green. Do not infer a disposition from a rule id, a locator, a detector's confidence, or a
> prior story's prose. Do not let a model "pre-classify for the human to confirm". **A fabricated
> adjudication would clear the externalization gate on evidence that does not exist, and every guard
> downstream — including 13.3's — would agree that it had.** An honest HALT is a better outcome than
> a green story, and it is the outcome this file is designed to make easy.

---

## Dev Agent Record

### Agent Model Used

Claude Opus 5 (`claude-opus-5[1m]`), via the `bmad-dev-story` workflow, 2026-08-16.

### Debug Log

#### §1 — Task 1: every §0/§0.1/§0.3 premise re-measured on the implementation baseline, by execution

Baseline **`1816524`** — **NOT** the sha §0 was measured on (`bc55e36`). Story 13.1 landed underneath
this story across five commits, so every premise was re-measured rather than inherited.
`origin/master == HEAD`, 0 ahead / 0 behind; `git tag -l` **empty**.

| Premise, as §0/§0.1/§0.3 state it | Re-measured on `1816524` | Consequence |
|---|---|---|
| §0.1 (1) — a corpus emitting nothing returns `precision=1/1`, `provisional=False`, gate *"cleared"* | ✅ **REPRODUCED VERBATIM.** `tp=0 fp=0 fn=8 \| precision=1/1 \| provisional=False`, gate `"cleared (… precision=1/1 >= 4/5 … N=7 labeled cartridges >= floor N=5…"` | AC1b's RED. Closed |
| §0.1 (2) — a 2-member injected registry still reports `N=7` | ✅ **REPRODUCED VERBATIM.** `rows=2 n=7 floor=5 provisional=False`, same *"cleared … N=7"* string | AC1a's RED. Closed |
| §0.1 (3) — `_is_clean_repo` is vacuous on a repository corpus | ✅ **CONFIRMED by construction** and now measured: folding only the golden-key-bearing cartridges (structurally the repo-corpus shape) gives `clean_repo_fp == 0` with **no member able to fail** | AC1c. Closed |
| 13.1 is `done` and its corpus manifest exists | ✅ **HOLDS.** `sprint-status.yaml:415` = `done`; `validation-corpus/adjudication-set.json` (2.0 MB) + `blocking-worklist.md` present | **Task 0 precondition MET** |
| 13.1's AC3b completed or HALTED | ✅ **COMPLETED, RATIFIED.** Operator XAgent007 ratified five members 2026-08-16; `eligible_member_count()` = **5**, floor MET; **31 blocking findings**, all `vacuous_test_ast`; all 5 byte-reproducible | **AC7 is evaluable in principle** — the corpus exists. It is HALTED for the *other* reason: the judgement is a human act |
| The adjudicator is named | ✅ **HOLDS.** `sprint-status.yaml:414`/`:416` and `deferred-work.md` name **XAgent007**; protocol §2 Engineering Lead | Start condition MET |
| `replay_harness.py` is **391** lines | ❌ **DRIFTED: 608.** 13.1 added `corpus_manifest_module`, `ValidationCorpusMeasurement`, `measure_validation_corpus` and three `precision_gate_status_for` parameters | The §0.3 inventory is 13.1-shaped; rebased onto it, not over it |
| Test-id high-water marks `PRECISION-20 · CARTRIDGE-15 · DOGFOOD-52 · DOCS-72 · HITL-31` | ❌ **MOVED by 13.1: PRECISION-31 · DOGFOOD-55 · DOCS-76** (CARTRIDGE-15, HITL-31 unchanged) | New ids continue from the **live** marks: `PRECISION-001-32`.., `DOCS-001-77`.. |
| NFR-M1 headroom: `test_evidence_citation.py` **1199** (1 left), `test_instrument_disclosure.py` **1179** (21 left) | ✅ **BOTH EXACT.** Also `test_dogfood_proof.py` 1106, `proof_run.py` 760 (was 679) | **Every new guard went in a NEW module.** Nothing was shaved |
| `protocol_cleared` is never passed `True` from production; exemptions = exactly 2 test files | ✅ **CONFIRMED**, `-46` green | Registered `tests/test_gate_flip_path.py` **by name with its reason** — the set fails in both directions |
| `AI-E12-6`'s ledger-claim guard does not exist | ✅ **CONFIRMED absent** | AC8.2. **Landed** |
| `AI-E12-5` — `grep -c "GUARD-ADEQUACY" architecture.md` → 0 | ✅ **CONFIRMED 0** across (now) 17 §Enforcement rules | AC8.4. **Registered** |
| `AI-E12-3`'s four entries are undisposed | ✅ **CONFIRMED.** `DF-8-3-A`, `DF-10-4-A`, `DF-10-4-B`, `DF-12-3-A` — none carried a disposition | AC8.3. **All four ruled, by execution** |
| The 6.7 writer is unreusable as a class | ✅ **CONFIRMED.** `DecisionRecordWriter.append` takes only `EscalationResolution`; `.gitignore:19` ignores `.argus/` | DN-3. Discipline reused, class not |
| Baseline gates | ✅ `mypy` **83 files clean**; `bandit` **19 Low / 0 Med / 0 High**; the 13.1 suite figure is **1561** | Deltas reported against these |

#### §2 — RED evidence, captured at the real seam (AI-E11-1 clause ii), before or during each guard

| Guard | Observable | Planted / live defect | RED | GREEN |
|---|---|---|---|---|
| `PRECISION-001-32` | `PrecisionResult.n` + the `N=` figure in `gate_status` | **live, not planted** — the §0.1 (2) snippet | `rows=2 n=7 floor=5 provisional=False`, *"cleared … N=7 labeled cartridges >= floor N=5"* | `rows=2 n=2 provisional=True`, `unevaluable (…)` |
| `PRECISION-001-33` | `n` for every **generated** prefix of the live registry vs the registry's own predicate | a second eligible-member count would diverge on ≥1 prefix | (design-time) | 10 generated populations, 0 divergences |
| `PRECISION-001-35` | `provisional`, `meets_threshold`, `precision_evaluable`, first word of `gate_status` | **live** — the §0.1 (1) snippet | `precision=1/1 provisional=False` → `"cleared …"` | `evaluable=False meets=False provisional=True` → `"unevaluable …"` |
| `PRECISION-001-36` | can the renderer be made to say *cleared* for an unmeasured run | 16 **generated** (tp, fp) combinations + both honesty flags | `precision_gate_status_for(evaluable=False, provisional=False)` returned a string | now **raises**; 15/16 non-cleared, exactly 1 legitimately cleared |
| `PRECISION-001-37` | `clean_repo_fp_applicable` | **generated** from the live registry: fold only the golden-key-bearing members | condition reported satisfied over a population that cannot fail it | `applicable=False` + `NOT APPLICABLE … BY CONSTRUCTION` |
| `PRECISION-001-43` | what `AdjudicationRecord` accepts | three variants **generated from the committed record's own first row**: a non-superseding second row, a correction naming a missing row, a correction naming a different finding | all three constructed silently before the invariant existed | all three **raise**; the superseded row stays present |
| `PRECISION-001-45` | `protocol_version` vs the change-log head | a **V9.9** row prepended to a copy of the real protocol | the record still matched → guard pinned to whatever it first saw | head moves to `V9.9`, the record no longer matches |
| `PRECISION-001-47` | `exhaustiveness()` | **generated from the record**: judge all 31, then remove exactly one | a fold over the adjudicated subset would have reported a ratio | `Unevaluable(residual_count=1)`; `BORDERLINE` is also a residual |
| `PRECISION-001-49` | ordering of the §4 preconditions | a **full** sweep of 31 TP judgements over a `reproducibility_verified=False` record | a determinism check evaluated *beside* the ratio would still publish `31/31` | `precision is None`, `evaluable=False`, `unevaluable …` |
| `DOCS-001-78` | claimed `DF-*` closures vs the ledger | **live, and it found 19** | 19 unbacked claims across 15 story files, incl. `DF-10-4-A` (12.5) and `DF-8-3-A` — i.e. it reproduced `AI-E12-3` from scratch | 17 registered dated+owned; 2 (`DF-8-3-A`, `DF-10-4-A`) **removed the same day** because this story closed them against evidence |

**A RED I planted in my own guard and did not weaken.** `DOCS-001-78`'s first id pattern was lazy
(`DF-[A-Za-z0-9-]*?[A-Za-z0-9]`), so it matched `DF-12` inside `DF-12-3-A` and produced **eight false
accusations** on its first run — a guard failing in the direction that looks like a finding. Fixed by
matching the id **whole and greedily**; the wrong pattern and the reason are recorded in the module,
because the next person to widen it will reach for a lazy quantifier too.

**A RED that was not mine and was not planted.** `tests/test_dogfood_plan.py::-03` went red the moment
`argus/precision/adjudication.py` landed: total tracked `argus/` LOC moved 25 776 → 25 856 and the
committed partition plan cites the old figure. That is the `DF-8-5-B` / `DF-10-4-D` artifact-currency
bootstrap working exactly as designed (`AI-E12-11`), and it was resolved by the sanctioned sequence —
commit the `argus/` delta, regenerate through the renderers, commit the regeneration separately —
never by editing an artifact or loosening an assertion.

#### §3 — findings this story did not expect, and corrected rather than papered over

1. **`DF-10-4-B` is NOT delivered, and two story records say it is.** `AI-E12-3` asked for
   verification by execution; this is what execution found. `argus/reports/generator.py:420-422`
   states **in its own docstring** that *"`DetectorResult.degraded` records it and no production code
   reads it back"*, and a tree-wide sweep confirms every other occurrence is a write. Yet
   `12-4-…md:126`/`:152` records it as an integrated, checked-off task and `10-5-…md` records a
   closure. Both are false against the tree. **Re-recorded OPEN with a named owner; not fixed here**,
   because adding an operator-facing reader is report behaviour no 13.2 AC owns.
2. **`DF-10-4-A` is delivered — by a different mechanism than its entry names.** The all-or-nothing
   trigger the entry describes is **unchanged** (`generator.py:436-439` still documents and performs
   it); what closed the operator-facing gap is 12.5's separate `render_grammar_downgrade_summary`
   surface, wired at `cli.py:931`. Closed **with the divergence stated**, because a closure justified
   by the wrong surface is how an entry gets re-opened by the next person who reads the original code.
3. **`DF-12-3-A` is half true, and a single CLOSED line would have published the wrong half.** The
   *disclosure* exists verbatim (`plain_english.py:249`/`:257`); the *mechanism* (PRD §501 — a re-run
   returns the recorded result under `--deep-audit`) does not. Split: disclosure CLOSED, mechanism
   re-recorded OPEN with an owner.
4. **The obvious reuse for the fold is wrong, and silently so.** Synthesising a golden key from the
   TP dispositions and letting `compute_precision` diff against it — the natural reading of DN-1 —
   classifies by class MEMBERSHIP, so a class in the golden key contributes its **whole**
   multiplicity as TP. On a real repository one class routinely holds both real and false findings.
   Adding a multiplicity map to `compute_precision` (the story's own suggested alternative) carries
   the multiset faithfully and **still** assigns all 24 `minions` findings to one side. Resolved as
   DN-2b: fork nothing, share the **arithmetic**.
5. **`_UNBACKED_AT_LANDING` shrank on the day it landed** — `DF-8-3-A` and `DF-10-4-A` had to be
   removed within the same change, because ruling them CLOSED in the ledger made the guard's own
   shrink assertion fire. That is the registry behaving correctly on its first run, and it is
   recorded rather than quietly edited.

#### §4 — measured environment facts that changed the design

- **`_bmad-output/` is tracked and `.argus/` is ignored** (`.gitignore:19`), which is the whole of
  DN-3. The record lives beside 13.1's corpus artifacts, in git, and `PRECISION-001-40` asserts
  `git ls-files` returns it — a path assertion would have passed for an ignored file.
- **`argus/precision/adjudication.py` resolves NO repository-only path at module level.** The corpus
  is reached through 13.1's existing lazy `corpus_manifest_module()` edge and the record path is a
  repository-relative **string** the caller resolves (`DF-9-2-A`; `tests/test_built_distribution.py`
  is the guard that would have caught the alternative only after a wheel was built).
- ⚠️ **Windows-only local gates, ubuntu CI.** Every path in the new code is `pathlib`; every file
  read passes `encoding="utf-8"` explicitly; the record is written `newline="\n"`; and the locator
  regex **rejects** a drive letter, a leading `/`, a `..` segment and a backslash — so a Windows-only
  locator is a construction-time failure rather than a POSIX-only bug shipped behind a green local
  suite. `PRECISION-001-44` generates five adversarial locators to prove it.
- **The suite reaches no network.** The new modules import only `hashlib`, `re`, `dataclasses`,
  `fractions`, `pathlib`, `subprocess` (one `git ls-files`) and this project's own serializer.
- **No new third-party dependency** was added or needed.

#### §5 — gates, all LOCAL (architecture.md §H: a local run is necessary, never sufficient)

| Gate | Result | Baseline (13.1 on `1816524`) |
|---|---|---|
| `pytest` (full suite) | **1585 passed / 0 failed / 0 errors / 0 skipped**, exit 0 | 1561 → **+24** (7 `PRECISION-001-32..-38`, 14 `PRECISION-001-39..-52`, 3 `DOCS-001-77..-79`) |
| `mypy argus` | **Success: no issues found in 84 source files** | 83 → 84 (`adjudication.py`), clean |
| `bandit -r argus` | **19 Low / 0 Medium / 0 High** (confidence 0 Low / 6 Med / 13 High) | identical |
| NFR-M1 (≤1200) | measured by `len(text.splitlines())`, the sweep's own idiom: `adjudication` **923** · `replay_harness` **786** · `test_adjudication_record` **768** · `test_release_preflight` **948** · `test_gate_flip_path` **354** · `_registry` **347** · `test_governance_record_integrity` **311** · `build_adjudication_record` **228** · `test_instrument_disclosure` **1194** (6 left) | `TC-ArgusAgent-MAINT-001-01..-05` **green**; no unexempted breach. Every new guard went in a **NEW** module and nothing was shaved — `test_evidence_citation.py` is untouched at **1199** |
| `deferred-work.md` append-only | `git diff --numstat` → **186 / 0** | `+n / -0` satisfied |
| `-46` (`protocol_cleared` disclosure) | **green**; the exemption set now names **4** test files, each with its reason | the set fails in both directions — both new files were caught by it, not remembered |

**Four guards went RED on the full-suite run and every one of them was a guard working.** None was
loosened; each was answered by recording a decision or by correcting a document.

1. `TC-ArgusAgent-DOCS-001-46` — `tests/test_adjudication_record.py` passes `protocol_cleared=True`
   (in `-49` and `-52`, both to prove the gate is REFUSED). **Registered by name with its reason.**
   I had registered `test_gate_flip_path.py` from memory and forgotten the second file; the closure
   caught it, which is precisely why this project stopped trusting hand-counted enumerations.
2. `TC-ArgusAgent-RELEASE-001-11` — `argus/precision/adjudication.py` joined the set of `argus/**`
   modules **naming** the repository-only tree. Registered as a **deliberate** decision with the
   reason: it names `tests/corpus/_manifest.py` only in prose, reaches it exclusively through the
   declared lazy `corpus_manifest_module()` edge, and resolves no repository path at module level.
3. `TC-ArgusAgent-DOCS-001-54` — four published figures went stale the moment a module was added:
   `README.md` (importable modules 83→84, wheel entries 91→92, sdist members 90→91) and
   `CHANGELOG.md` (83→84 twice). **The artifact is the fact**; the documents were corrected, and the
   guard measured them against a freshly built wheel rather than against each other.
4. `TC-ArgusAgent-DOCS-001-78` — **my own new guard, firing on my own story record.** See the
   Completion Notes; the correction is recorded there rather than quietly applied.

**CI evidence: NOT ESTABLISHED.** No CI run covers any Epic-10/-11/-12/-13 sha; `audit-ci.yml`'s
latest run covers `00c8d1b` (2026-08-09). ⚠️ **These gates ran on Windows only.**

**Nothing outward-facing was performed**, re-asserted by execution at hand-off: `git tag -l`
**empty**, `origin/master` **unmoved**. No push, no tag, no release, no visibility change.
`DF-12-9-A` untouched. The six untracked root artifacts (`AI-E12-12`) were **not swept** and none
entered the corpus.

#### §6 — decisions taken, with their rejected alternatives

- **DN-1 — ADOPTED.** The adjudication record IS the golden key for the repository corpus, exactly as
  protocol §2 already says. *Rejected:* a second precision function per corpus.
- **DN-2 — ADOPTED.** Every harness change is an additive keyword whose default preserves today's
  behaviour. Proven: `TC-ArgusAgent-DOGFOOD-001-11`/`-12` and `TC-ArgusAgent-PRECISION-001-08`/`-09`
  pass **byte-unedited**. *Rejected:* changing `compute_precision`'s semantics in place.
- **🆕 DN-2a — the unit of adjudication is the FINDING, not the rule CLASS** (AC2's decision).
  Protocol §7 locks it and §7's own heading forbids softening; the alternative — amending §4/§5/§7 to
  say *class* — would redefine the gate's denominator **downward**, and on this corpus 31 blocking
  findings are 1 class, so the gate would have been computed over a denominator of **one**. Written
  into the protocol as **V1.3 before** the record was generated, and the ordering is mechanical:
  `PRECISION-001-45` fails a record whose `protocol_version` is not the change-log head.
- **🆕 DN-2b — the fold shares the ARITHMETIC, not the function.** `fold_adjudicated_precision`
  counts dispositions directly and calls `precision_fraction`, `gate_is_provisional`,
  `PRECISION_GATE_THRESHOLD` and `precision_gate_status_for` — the same objects `compute_precision`
  uses. *Rejected (and it was the story's own suggestion):* a multiplicity map on `compute_precision`.
  It carries the multiset correctly and still cannot express *"this class is 20 TP and 4 FP"*,
  because the golden-key diff classifies by membership. See §3.4.
- **DN-3 — ADOPTED.** Committed repository artifact; the 6.7 writer reused as a *discipline*.
  *Rejected:* shoehorning adjudications into `EscalationResolution` under `.argus/`.
- **DN-4 — ADOPTED.** `argus.store.canonical.dumps_bytes` only; row ids are content-addressed through
  it. No second serializer, hasher or envelope.
- **DN-5 — ADOPTED.** Three outcomes, `release_preflight.py`'s precedent. `AdjudicationUnevaluable`
  is a **type**, not a flag, so no call site can treat it as falsy by forgetting to look.
- **DN-6 — ADOPTED, and made structural.** `UNADJUDICATED` is the only member an automated producer
  may write, and a row carrying it **raises** if it has an adjudicator id. *Rejected:* an LLM
  pre-classification the human "reviews".
- **DN-7 — ADOPTED.** `protocol_cleared` stays `False`; `INSTRUMENT_STATUS` untouched; `-46` green.
- **🆕 DN-8 — the 19 historical unbacked ledger claims are a dated, owned, SHRINKING registry.**
  *Rejected:* closing 19 entries this story has no evidence for — `AI-E12-3`'s own defect committed
  inside the guard written to stop it. *Also rejected:* narrowing the guard to recent stories, which
  is the move Story 12.1 files as a defect. A listed entry that becomes backed **fails**.
- **🆕 DN-9 — `AI-E11-8`'s two Epic-11 rules are re-homed, not registered.** Both are outside this
  story's write set; registering unrelated rules inside the story whose subject is a scoped, recorded
  act would be the drift the ledger exists to catch. Recorded with a named owner (`AI-E9-8`).

#### §7 — the adjudication: who, when, how many hours, and what was NOT adjudicated

**No finding was adjudicated. Zero. This is the designed terminal state, and it is recorded, not
skipped.**

- **Who:** protocol §2 assigns the judgement to the **Engineering Lead**, and
  `sprint-status.yaml:414`/`:416` name **XAgent007**. No agent may supply a disposition, and this
  session had no operator present.
- **When:** not yet. `expert_hours` is `null` — **NOT RECORDED**, never `0`; a zero would claim the
  work took no time rather than that it has not happened.
- **What is ready:** all **31** blocking findings — 24 `minions` + 7 `agent-smith`, every one
  `vacuous_test_ast` — are in the committed record as `UNADJUDICATED` rows, each with its member,
  its `finding_match_key` identity, its locator, and **no adjudicator**. `blocking-worklist.md` is
  the human-readable form.
- **What the instrument reports over that record, measured:** `exhaustiveness()` →
  `Unevaluable(residual_count=31, adjudicated_count=0)`; `precision` → `None` /
  `"NOT COMPUTED BY THIS RUN"`; `provisional` → `True` **even when the caller claims
  `protocol_cleared=True`**; `gate_status` → `"unevaluable …"`; `clean_repo_fp_applicable` → `False`
  with its reason.
- **What was NOT done, deliberately:** no disposition was invented, inferred from a rule id, guessed
  from a locator, or defaulted to make `PRECISION-001-47` go green. *A fabricated adjudication in the
  story that defines adjudication would clear the externalization gate on evidence that does not
  exist, and every guard downstream — including 13.3's — would agree that it had.*
- **What closes the gap, in one act:** XAgent007 judges each of the 31 at its cited locator per §4,
  records the hours, and appends the rows. Filed as `DF-13-2-A`.

### Completion Notes

**AC1 ✅ — all three flip-path defects closed, additively.** (a) `n` now closes over the population
actually folded, through the registry's **own** predicate given an additive parameter — no second
count (13.1 / DN-3). (b) An empty denominator is `precision_evaluable=False`, `meets_threshold`
forced `False`, the gate forced provisional, and a **third** gate-status outcome, `unevaluable`;
`precision_gate_status_for(evaluable=False, provisional=False)` raises. (c) The clean-repo condition
names its population and reports NOT APPLICABLE where no member can fail it. **Additivity proven:**
the 6.6/7.1 contract tests (`DOGFOOD-001-11`/`-12`, `PRECISION-001-08`/`-09`) pass **byte-unedited**.

**AC2 ✅ — the protocol is amended BEFORE the run, and the ordering is mechanical.** V1.3 decides
**the unit is the FINDING** (§7 upheld, not softened), defines the finding identity, records why the
obvious fold is wrong, and amends §1/§2/§3/§4/§5 — rebased onto 13.1's V1.1/V1.2 text, struck never
erased. `PRECISION-001-45` fails any record whose `protocol_version` is not the change log's head,
proven RED by prepending a V9.9 row to a copy of the real document.

**AC3 ✅ — the record exists, in git, machine-readable, human-attributed.** 31 rows keyed on
`(member_id, rule_id, verdict_eligible, advisory, locator)` with the 6.6 match key reused unchanged;
a closed vocabulary that **raises**; append-only supersession where a correction must name the row it
replaces and the superseded row is retained; NFR-S1 enforced **structurally** by a closed schema plus
a locator regex that rejects drive letters, absolute paths, `..` and backslashes; attribution checked
against protocol §2's role table **in both directions**.

**AC4 ✅ — exhaustiveness proven, with the non-vacuity floor inside the guard.** Every emitted finding
must carry exactly one live TP/FP disposition; a residual yields `Unevaluable` **with its count and
what would close the gap**; an **empty** population is itself `Unevaluable`, not "exhaustive over
nothing". The adversarial variant is generated from the committed record.

**AC5 ✅ — hours are a `Fraction` field, reported not enforced.** The ≤4h ceiling is cross-checked
against §3's own text (`AI-E9-7`), an overrun reads *"RECORDED, NOT FAILED"*, and `null` reads
*"NOT RECORDED"*, never zero.

**AC6 ✅ — determinism first, via the EXISTING check.** 13.1's per-member
`byte_reproducible_across_two_runs` is carried onto the record with its source named; the fold
evaluates it **before** exhaustiveness and before the ratio, proven by a fixture with 31 TP
judgements over a non-reproducible corpus that still produces no number.

**AC7 ⛔ HALTED — awaiting the named adjudicator.** See §7. The corpus exists (13.1 delivered N=5 and
31 blocking findings), so this is not the under-population case: it is the case the ⛔ ESCALATION
section names, and the Story 12.9 / AC9 precedent applies. Recorded as `Unevaluable`, residual 31,
with `DF-13-2-A` filed.

**AC8 ✅ —** `deferred-work.md` **`+186 / -0`**. The four human-adjudication entries stay OPEN with
their remaining scope re-recorded and none left pointing at a run that has happened.
`AI-E12-6`'s guard **landed** and found 19 unbacked claims on its first run, reproducing `AI-E12-3`
independently. All four of `AI-E12-3`'s entries **ruled by execution**: `DF-8-3-A` CLOSED, and
`DF-10-4-A` CLOSED with its divergence stated.
`DF-10-4-B` is **NOT delivered** — re-recorded OPEN with a named owner, and two story records
saying otherwise are corrected. `DF-12-3-A` is split: disclosure half closed, mechanism half OPEN.

> **This paragraph was itself corrected by `DOCS-001-78`, on its first run over this story.** The
> original wording put `DF-10-4-B` on the same line as a closure verb, so the new guard read it as a
> claim that the ledger never received — and it was right to: a reader skimming that line would have
> drawn the same conclusion. The guard's author was its first subject, which is the most useful
> possible evidence that it is not vacuous.

The **GUARD-ADEQUACY CLAUSE** is registered in
§Enforcement (`AI-E12-5`, fourth request / first registration) with its input-side twin, alongside
two more Story 13.2 rules; `AI-E11-8` re-homed with a named owner. `AI-E12-1`'s satisfied half
recorded, not redone. Every new guard is in a **new** module — nothing was shaved.

**The gate did not move, and could not have.** `protocol_cleared` is still `False` and still never
passed `True` from `argus/**`; `INSTRUMENT_STATUS` is untouched; one of §5's four conditions holds
(N=5, from 13.1) and the other three do not — the ≥80% figure is **UNEVALUABLE**, the clean-repo
condition is **NOT APPLICABLE** with its reason, and no adjudication run is recorded. This story
makes the measurement possible and refuses to make it up.

### File List

**NEW**

| Path | What |
|---|---|
| `argus/precision/adjudication.py` | AC2–AC6 — the adjudication record: closed vocabulary, attributed rows, append-only supersession, exhaustiveness + determinism, the expert-hours report, and the fold into the shared arithmetic |
| `scripts/build_adjudication_record.py` | AC3/AC7 — seeds/re-seeds the record from 13.1's adjudication set; append-only, and structurally incapable of adjudicating |
| `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/adjudication-record.json` | AC3/AC7 — the committed record. 31 `UNADJUDICATED` rows, zero judgements |
| `tests/test_gate_flip_path.py` | `TC-ArgusAgent-PRECISION-001-32`..`-38` (AC1) |
| `tests/test_adjudication_record.py` | `TC-ArgusAgent-PRECISION-001-39`..`-52` (AC2–AC7) |
| `tests/test_governance_record_integrity.py` | `TC-ArgusAgent-DOCS-001-77`..`-79` (AC8.2/8.3/8.4) |

**MODIFIED**

| Path | What |
|---|---|
| `argus/precision/replay_harness.py` | AC1a/b/c — `precision_fraction` + `gate_is_provisional` extracted as the SHARED arithmetic; `PRECISION_GATE_THRESHOLD` promoted public (alias kept); `population_n` added; `n` closes over the folded population; `precision_evaluable` / `clean_repo_fp_applicable` / `measurement_note` / `precision_or_none` added; `meets_threshold` gated on evaluability; `precision_gate_status_for` gains `evaluable` and a third outcome |
| `tests/cartridges/_registry.py` | AC1a — `populated_planted_defect_count(registry=None)`: additive parameter, default identical; `LABELED_CARTRIDGE_KINDS` named once |
| `tests/test_instrument_disclosure.py` | `tests/test_gate_flip_path.py` and `tests/test_adjudication_record.py` registered by name in `_PROTOCOL_CLEARED_TEST_EXEMPTIONS`, each with its reason |
| `tests/test_release_preflight.py` | `argus/precision/adjudication.py` registered in `_MODULES_NAMING_THE_TEST_TREE_IMPORT` as a deliberate decision, with the reason it is safe (prose only; the lazy edge; no module-level path) |
| `README.md` · `CHANGELOG.md` | `TC-ArgusAgent-DOCS-001-54` — the four published built-artifact figures re-derived against a freshly built wheel (modules 83→84, wheel entries 91→92, sdist members 90→91) |
| `_bmad-output/…/precision-validation-protocol.md` | AC2/AC5/AC1b/AC1c — §1, §2, §3, §4, §5 amended; §6/§7 unchanged and re-affirmed; **V1.3** change-log entry |
| `_bmad-output/…/architecture.md` | AC8.4 — three §Enforcement registrations: the GUARD-ADEQUACY CLAUSE, adjudication-record enforcement, ledger-claim cross-check enforcement |
| `_bmad-output/…/deferred-work.md` | AC8.1–8.3 — append-only `+186 / -0` |
| `_bmad-output/…/minions-dogfood-proof.md` · `-partition-plan.md` · `-budget-plan.md` | regenerated through their own renderers (`DF-8-5-B` / `DF-10-4-D` bootstrap, `argus/` LOC moved) |
| `_bmad-output/…/sprint-status.yaml` | status transitions |
| `_bmad-output/…/stories/13-2-…md` | this file |

### Review Findings

<!-- The reviewer writes findings HERE, in this file, not only into sprint-status.yaml (AI-E12-10). -->

**Code review — 2026-08-17 (Sonnet), commits `e991a00`+`4c6c76d`+`411d891` (`1816524`..`HEAD`).
VERDICT: PASS.** Ran the bmad-code-review workflow's three adversarial layers (Blind Hunter,
Edge Case Hunter, Acceptance Auditor against this story's ACs) plus independent execution. No
High or Medium finding. No unresolved `[Decision]` or `[Patch]` item. Status -> `done`.

**The six claims this review was specifically directed to verify, and what was found:**

1. **AC7 `Unevaluable`-by-design — RULED LEGITIMATE, not an unmet AC waved through.** The
   story's own `## ⛔ ESCALATION` section (written by `create-story`, **before** `dev-story`
   ran) explicitly designs this exact outcome and names the Story 12.9 / AC9 precedent. That
   precedent was independently confirmed: `stories/12-9-release-is-published-and-cites-its-gate.md`
   AC9's HALT (outward-facing acts requiring explicit human authorisation) was itself reviewed
   and landed as a **CLEAN PASS** (`sprint-status.yaml`'s `12-9` history). AC7's case is if
   anything *stronger* than 12.9's: DN-6 (`argus/precision/adjudication.py:20-27`, protocol §2)
   makes the judgement **definitionally** a human act — `AdjudicationRow.__post_init__` raises if
   an `UNADJUDICATED` row carries an adjudicator id, so no agent could supply the disposition even
   if instructed to. `adjudication-record.json` independently parsed: **31/31 rows
   `UNADJUDICATED`, `adjudicator: null` on every row** — matches the Debug Log §7 claim exactly.
   This is a locked, pre-designed terminal state, not an absence to flag as a defect.
2. **Protocol V1.3 amendment — checked adversarially for loosening, NONE found.**
   `precision-validation-protocol.md` diff reviewed line-by-line: every change is
   strike-in-place-never-erase, the §5 `N >= 5` and `>= 4/5` literals are byte-unchanged, the
   clean-repo condition went from *falsely satisfiable* to *explicitly NOT APPLICABLE with a
   reason* (a tightening, not a softening), and the finding-level unit (31 distinct rows) is
   **more** granular than the rejected per-class alternative (which the amendment's own text
   shows would have gated on a denominator of 1) — i.e. the road not taken was the easier one, and
   it was rejected. §7's *"precision over FINDINGS"* is now independently enforced by
   `TC-ArgusAgent-PRECISION-001-46`, not merely asserted. No goalpost movement.
3. **The record — independently re-parsed with a fresh script**, not taken on the dev's word:
   `python -c "json.load(...)"` over the committed `adjudication-record.json` confirms **31 rows**,
   `{'UNADJUDICATED'}` as the only disposition set, `{None}` as the only adjudicator set. Confirmed.
4. **DN-2b (fold shares arithmetic, not `compute_precision`) — RULED justified, not a DRY
   violation.** `fold_adjudicated_precision` (`argus/precision/adjudication.py:839-923`) calls the
   same shared objects `compute_precision` uses — `precision_fraction`, `gate_is_provisional`,
   `PRECISION_GATE_THRESHOLD`, `precision_gate_status_for` — so the arithmetic genuinely is not
   forked. What is *not* shared is `compute_precision`'s golden-key **membership diff**, which is a
   structurally different algorithm from a direct per-row disposition tally and cannot express
   "this class is 20 TP and 4 FP" (demonstrated in the module docstring, `:45-62`). Sharing the
   quantities that must agree while not forcing an incompatible classification algorithm into one
   function is correct separation of concerns, not duplication.
5. **Windows-only-shipping-POSIX-bugs risk — scrutinized, no defect found.** `pathlib` used
   throughout `adjudication.py`, `build_adjudication_record.py` and the new test modules;
   `encoding="utf-8"` explicit on every read; `newline="\n"` explicit on the one write
   (`build_adjudication_record.py:184`); the locator regex (`adjudication.py:216`) rejects a drive
   letter, a leading `/`, a `..` segment and a backslash at **construction time**; every
   path-to-string boundary uses `.as_posix()` (`tests/test_adjudication_record.py:60-73`,
   `:151`). Independently measured on this Windows machine: the committed
   `adjudication-record.json` is **0 CRLF bytes** (`git ls-files --eol` reports `i/lf w/lf`) — the
   canonical serializer's single-line-JSON convention sidesteps the CRLF/LF class of defect this
   project has been bitten by before. CI evidence remains **NOT ESTABLISHED** (noted per the
   story's own §0, not a blocking finding — this is a pre-existing project-level gap, not
   something this story could close).
6. **DF-10-4-B correction and the 19 unbacked ledger claims — spot-checked, both accurate.**
   `argus/reports/generator.py:420-422`'s own docstring (unmodified by this diff, pre-existing)
   states in its own words that `DetectorResult.degraded` "records it and no production code reads
   it back" — confirming `DF-10-4-B` is genuinely not delivered. Cross-checked against
   `stories/12-4-every-outcome-names-its-next-action.md:126` which **does** check off `DF-10-4-B`
   as `[x]` delivered — the correction is accurate, not overreach. The `AI-E12-6` guard
   (`tests/test_governance_record_integrity.py`) and its `_UNBACKED_AT_LANDING` registry were read
   in full; its regex fix (whole-and-greedy `DF-[A-Z0-9]+(?:-[A-Z0-9]+)*`, correcting an earlier
   lazy pattern that matched `DF-12` inside `DF-12-3-A`) and its shrink-only assertion
   (`test_TC_ArgusAgent_DOCS_001_78`) are sound and match 12.1's `_EXEMPT_BY_DESIGN` precedent.

**Independently re-run, not read off the Dev Agent Record:**

- `pytest` (full suite): **100% green** — every batch of dots, 0 `F`/`E`/`s` markers, exit code 0.
  The four new/changed test modules run in isolation also pass cleanly:
  `tests/test_adjudication_record.py` (14), `tests/test_gate_flip_path.py` (7),
  `tests/test_governance_record_integrity.py` (3) — 24 new tests, matching the claimed `+24`.
- `mypy argus`: **Success: no issues found in 84 source files.** Matches the claim exactly.
- `bandit -r argus`: **19 Low / 0 Medium / 0 High.** Matches the claim exactly.
- NFR-M1 line counts independently measured (`wc -l`) and match the Dev Agent Record exactly:
  `adjudication.py` 923, `replay_harness.py` 786, `test_adjudication_record.py` 768,
  `test_gate_flip_path.py` 354, `test_governance_record_integrity.py` 311,
  `build_adjudication_record.py` 228, `test_instrument_disclosure.py` 1194.
- `git tag -l` empty, `origin/master` unmoved, working tree carries only the six pre-existing
  untracked non-source artifacts §0 already named (`AI-E12-12`, out of scope) — nothing
  outward-facing performed.

**No findings requiring action.** No `[Decision]`, `[Patch]`, or unresolved item is filed. Nothing
was deferred to `deferred-work.md` by this review.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-08-17 | v0.3 | **Code review: PASS. Status -> done.** Adversarial re-verification (Blind Hunter / Edge Case Hunter / Acceptance Auditor) of `e991a00`+`4c6c76d`+`411d891`. AC7's HALT independently ruled a legitimate designed terminal state (the story's own ESCALATION section + the verified 12.9/AC9 precedent), not an unmet AC. Protocol V1.3 checked adversarially and found NOT loosened. `adjudication-record.json` independently re-parsed: 31/31 UNADJUDICATED, no adjudicator anywhere. DN-2b ruled justified separation, not a DRY violation. Windows/POSIX handling scrutinized — no defect found. `DF-10-4-B` correction spot-checked and confirmed accurate. Independently re-ran: pytest full suite green, mypy clean 84 files, bandit 19/0/0, all NFR-M1 line counts match. No High/Medium findings. See Review Findings above. | Reviewer (code-review) |
| 2026-08-16 | v0.2 | **AC1–AC6 and AC8 complete; AC7 HALTED by design; status -> review.** All three §0.1 flip-path defects **reproduced verbatim on `1816524`** and closed additively — a 2-member injected corpus reported `N=7`, a corpus emitting nothing reported `precision=1/1` / `provisional=False` / *"cleared"*, and §5's clean-repo condition was vacuous on the corpus that gates externalization. The 6.6/7.1 contract tests pass **byte-unedited**. Protocol **V1.3** amended **before** the record was generated and decides the unit is the **FINDING** (§7 upheld, not softened — on this corpus 31 blocking findings are **1** rule class, so a per-class fold would have gated on a denominator of one); the ordering is mechanical, not a promise. The adjudication record is committed in git with **31 `UNADJUDICATED` rows and zero judgements**: no agent may adjudicate, and an `UNADJUDICATED` row carrying an adjudicator id now **raises at construction**. AC7 is **HALTED — awaiting XAgent007** (Story 12.9 / AC9 precedent), recorded as `Unevaluable` with residual **31**, filed as `DF-13-2-A`. AC8: ledger `+186 / -0`; `AI-E12-6`'s guard **landed** and found **19** unbacked ledger claims on its first run, reproducing `AI-E12-3` independently; all four of `AI-E12-3`'s entries **ruled by execution** (`DF-10-4-B` is **not** delivered and two story records saying otherwise are corrected); the **GUARD-ADEQUACY CLAUSE** is registered in §Enforcement at the fourth request. Gates LOCAL: pytest **1585/0/0**, mypy clean **84** files, bandit **19 Low / 0 Med / 0 High**. `protocol_cleared` still `False` everywhere; nothing outward-facing. | Developer (dev-story) |
| 2026-08-16 | v0.1 | Story contexted. Premises re-measured on `bc55e36`. **Three defects in the gate-flip path found by execution** — `n` ignores the injected population (reports 7 for a 2-member corpus), an empty precision denominator returns `1/1` and reads "cleared", and §5's clean-repo FP condition is vacuous on a repository corpus. Also recorded: the protocol's "precision over FINDINGS" and the harness's per-class arithmetic are different quantities; the 6.7 decision writer is unreusable as a class (wrong semantic, gitignored destination); and `AI-E12-6`, `AI-E12-3` and `AI-E12-5` are all unlanded and all named by the Epic-12 retrospective as Epic-13 preconditions. | Scrum Master (create-story) |
