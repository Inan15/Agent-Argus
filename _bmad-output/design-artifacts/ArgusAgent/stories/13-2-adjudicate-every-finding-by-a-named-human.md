# Story 13.2: Adjudicate every finding, by a named human

Status: ready-for-dev

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

- [ ] **Task 0 — Confirm the precondition (AC: all)**
  - [ ] Verify 13.1 is `done` in `sprint-status.yaml` and its corpus manifest exists
  - [ ] Record whether 13.1's AC3b completed or HALTED — it decides AC7's terminal state
  - [ ] Re-assert the start condition by execution: the adjudicator is named
- [ ] **Task 1 — Re-measure every §0/§0.1/§0.3 premise on your implementation baseline (AC: all)**
  - [ ] Re-run the two §0.1 snippets; record the actual output in Debug Log §1
  - [ ] Record confirmations *and* divergences; if a premise moved under 13.1, say so before acting
- [ ] **Task 2 — Close the three flip-path defects, additively (AC1)**
  - [ ] AC1a: `n` counts the adjudicated population; RED-then-green against the 2-member reproduction
  - [ ] AC1b: an empty denominator is `Unevaluable`, never `cleared`; RED against the 0/0/8 reproduction
  - [ ] AC1c: §5's clean-repo condition names its corpus or is recorded not-applicable with a reason
  - [ ] Prove additivity: the 6.6/7.1 contract tests pass **unedited**
  - [ ] Register any new `protocol_cleared=True` test file in `_PROTOCOL_CLEARED_TEST_EXEMPTIONS`
- [ ] **Task 3 — Amend the protocol BEFORE the run (AC2)**
  - [ ] Decide and record the unit: per finding **or** per class; correct §4/§5/§7's wording to match
  - [ ] Amend §1/§2/§3/§4 for the repository corpus, rebased onto 13.1's amendments
  - [ ] Append to the change log with date + reason (strike, never erase)
  - [ ] Guard: the record's protocol version equals the change log head; RED on a superseded version
- [ ] **Task 4 — Build the adjudication record (AC3)**
  - [ ] Schema keyed on `finding_match_key`; closed disposition vocabulary that **raises**
  - [ ] Append-only with supersession; a correction carries its date and reason
  - [ ] Committed in git (**not** `.argus/` — `.gitignore:19`); NFR-S1 asserted
  - [ ] Adjudicator attribution checked against protocol §2's role table
- [ ] **Task 5 — Prove exhaustiveness and determinism (AC4, AC6)**
  - [ ] Every emitted key has exactly one live disposition; residuals → `Unevaluable`, counted
  - [ ] Non-vacuity: > 0 rows asserted before any other assertion
  - [ ] Byte-reproducibility proven first, via the existing check, recorded on the record
- [ ] **Task 6 — Record expert-hours (AC5)**
  - [ ] Actual hours as a field; compared to §3's ≤4h as a **report**, not a gate
  - [ ] If exceeded, record what made it expensive — never trim the adjudication to fit
- [ ] **Task 7 — The run (AC7 — see ESCALATION)**
  - [ ] Present the adjudication-ready finding set to the named human, per §4 as written
  - [ ] Record each disposition with its locator, reason, date and adjudicator
  - [ ] If the corpus is absent/under-populated: mark **`Unevaluable` — recorded**, with the count and
        what would close the gap. **Invent nothing.**
- [ ] **Task 8 — Ledger and documents (AC8)**
  - [ ] Close or re-scope `DF-6-6-A` / `-P1` / `-P2` / `DF-7-2-A` with reasons; `+n / -0`
  - [ ] Land `AI-E12-6`'s ledger-claim cross-check guard, or decide it with a named owner
  - [ ] Rule on `AI-E12-3`'s four entries (`DF-8-3-A`, `DF-10-4-A`, `DF-10-4-B`, `DF-12-3-A`)
  - [ ] Register the guard-adequacy clause in §Enforcement (`AI-E12-5`), or re-home it with an owner
  - [ ] Note `AI-E12-1`'s already-satisfied half rather than redoing it
- [ ] **Task 9 — Gates and hand-off**
  - [ ] `pytest` / `mypy` / `bandit` with actual numbers, labelled **LOCAL**
  - [ ] NFR-M1 re-measured on every touched file (two are effectively full)
  - [ ] `protocol_cleared` still `False` everywhere in `argus/**`; `-46` still green
  - [ ] Nothing outward-facing performed; re-assert by execution (`git tag -l`, remote unmoved)

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

<!-- record model + version -->

### Debug Log

#### §1 — Task 1: every §0/§0.1/§0.3 premise re-measured on the implementation baseline, by execution

#### §2 — RED evidence, captured at the real seam (AI-E11-1 clause ii), before or during each guard

#### §3 — findings this story did not expect, and corrected rather than papered over

#### §4 — measured environment facts that changed the design

#### §5 — gates, all LOCAL (architecture.md §H: a local run is necessary, never sufficient)

#### §6 — decisions taken, with their rejected alternatives

#### §7 — the adjudication: who, when, how many hours, and what was NOT adjudicated

### Completion Notes

### File List

### Review Findings

<!-- The reviewer writes findings HERE, in this file, not only into sprint-status.yaml (AI-E12-10). -->

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-08-16 | v0.1 | Story contexted. Premises re-measured on `bc55e36`. **Three defects in the gate-flip path found by execution** — `n` ignores the injected population (reports 7 for a 2-member corpus), an empty precision denominator returns `1/1` and reads "cleared", and §5's clean-repo FP condition is vacuous on a repository corpus. Also recorded: the protocol's "precision over FINDINGS" and the harness's per-class arithmetic are different quantities; the 6.7 decision writer is unreusable as a class (wrong semantic, gitignored destination); and `AI-E12-6`, `AI-E12-3` and `AI-E12-5` are all unlanded and all named by the Epic-12 retrospective as Epic-13 preconditions. | Scrum Master (create-story) |
