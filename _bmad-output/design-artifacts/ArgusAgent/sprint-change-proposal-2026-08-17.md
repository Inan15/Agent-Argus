# Sprint Change Proposal — 2026-08-17

**Project:** ArgusAgent (formerly APAA — AI Project Assurance Audit)
**Author:** Correct Course workflow (`bmad-correct-course`), batch mode
**Requested by:** XAgent007
**Trigger type:** Failed approach requiring a different solution — the instrument under measurement was found defective by the measurement itself
**Change scope classification:** **MAJOR** — fundamental replan (PM / Architect involvement)
**Status:** ✅ **APPROVED by XAgent007, 2026-08-17 — all §4 edits APPLIED to all six artifacts**

> **Nothing in `argus/` was modified to produce this document.** Every number below was
> re-derived by running the **committed** detector over the corpus members at their **pinned
> shas**, and the one forward-looking claim (§3.4) was measured with an out-of-tree probe that
> imports the shipped modules read-only. `git status` is unchanged from the start of the
> session.

---

## 1. Issue Summary

### 1.1 What triggered this

Story 13.3 recorded the >=80%-precision externalization gate as **`BLOCKED`** over the ratified
5-repository validation corpus: **0 TP / 26 FP / 5 BORDERLINE**, all **31** emitted blocking
findings in a **single rule class** — `vacuous_test_ast`, which is verdict-eligible and can take a
build to 🔴.

Epic 13's charter is *"remove the disclosure by measuring, not by deleting."* The measurement ran
and it worked. What it found is that **the instrument is defective**, not that the repositories
were clean. That is a result Epic 13 can produce but cannot act on: Epic 13 is explicitly *"not a
build task"* (epics.md L2481), and the remedy is a build task.

### 1.2 Problem statement

**`vacuous_test_ast` — the only verdict-eligible finding class Argus ships — is not evidence of
what it claims.** Its AST corroboration step, which the architecture designates as the
false-accusation moat, tests whether a test constructs a mock. It does not test whether the
asserted values derive from something other than the system under test.

The consequence is not noise. It is that **the one rule capable of failing a user's build fired 31
times on real repositories and was right zero times.**

### 1.3 Evidence — measured, not inferred

A diagnosis pass on 2026-08-17 re-derived all 31 findings by materialising each member's files at
its pinned sha (`git show`, never a working tree — both checkouts have moved), building the index
with the committed `build_ast_index`, and running the committed `VacuousTestDetector.run()`.

| Reproduction | Result |
|---|---|
| `minions` @ `ec63b729` | `vacuous_test_ast` = **24**, heuristic-only = 150 — **exact set match** to the 24 adjudicated locators |
| `agent-smith` @ `9ab774d7` | `vacuous_test_ast` = **7**, heuristic-only = 17 — **exact set match** to the 7 adjudicated locators |

No misses, no extras, in either member.

**Finding A — one flag branch, never the other.** 31 of 31 flagged via `assertion_density < 1/4`.
The `mock_ratio > 1/2` clause fired **0** times across the 31 and **0** times across all **1,812**
heuristic flags in the minions test tree (327 files, 3,509 test functions, **51.6%** flagged).

**Finding B — the density denominator counts lines, not statements.** `_count_statements` counts
every non-blank, non-comment line in the span, so continuation lines of multi-line calls,
dict-literal entries, closing brackets and docstring lines each count as a statement. Measured
against a true `ast`-module statement count over the 1,812 flagged tests: **2.04× inflation**.

**Finding C — the assertion list knows no pytest.** `_ASSERTION_CALLEES` is documented as
*"unittest family + pytest helpers"* and contains **no pytest helper**. It misses `pytest.raises`,
every `unittest.mock` assertion method (`assert_not_called`, `assert_called_once_with`, …) and
project helpers such as `_assert_one_rejection`. Present in **13 of the 31** spans.

Attribution of B and C against the `1/4` floor, per finding:

| Correction | Findings it lifts back above the floor |
|---|---|
| Statement denominator alone | **14 / 31** |
| Assertion names alone | **4 / 31** |
| Both together | **23 / 31** |
| **Neither — still flagged** | **8 / 31** |

**Finding D — the moat, and the reason B and C are not sufficient.** `_ast_corroborated`'s fact (b)
is `assertion_sites >= 1 and mock_sites >= 1`. Across **1,836** flagged tests in both contributing
members, `ast_corroborated` is equivalent to `mock_sites >= 1` in **1,835** cases — facts (a) and
(assertions ≥ 1) never excluded anything on their own. The single exception is
`test_ir_copilot.py:138`, whose only assertion is `pytest.raises`; Finding C's gap is the only
reason it stayed advisory.

**Even with B and C corrected, 8 of the 31 still flag — and all 8 remain verdict-eligible**,
because fact (b) only asks whether a mock was constructed.

**Finding E — the mitigation of record does not reach this class.** Story 1.5's code review logged
this exact scenario and cleared it:

> *"A genuine test that mocks a dependency but asserts on the real SUT return and happens to trip
> the density floor could be AST-corroborated. … mitigated by the finding remaining `advisory=True`
> plus the architecture's required Epic-6 Prosecutor sign-off before any real 🔴. **No moat
> bypass. No action needed in V1.**"*

The Prosecutor **is** built (`argus/verdict/prosecutor.py`, called at `pipeline.py:535`). It does
not catch these findings, for two structural reasons:

1. **It is a one-way promoter.** Its own contract, lines 56–57: *"A finding already verdict-eligible
   (`depth_supported is not None`) is left UNCHANGED."* Sign-off gates findings being lifted *into*
   eligibility. A `vacuous_test_ast` finding arrives already carrying `AUDITED_SHALLOW`.
2. **Its sign-off authority is dormant.** The production call site passes no `sign_offs` set — the
   V1 default is deliberately empty to keep the path deterministic and zero-token.

So *"AST corroboration AND Prosecutor sign-off"* is an `AND` only for the findings that do not need
it, and an `OR` for the one class that does.

### 1.4 The governing invariant already says what is required

This is the decisive point for the governance weight of this change. **Cross-cutting concern #6**
(`architecture.md` L137–140) reads, verbatim:

> *the vacuous-test detector … **cannot move the verdict to 🔴 without `audited_deep` AST
> corroboration AND Prosecutor sign-off**. Protects the false-accusation moat (a wrong 🔴 is the
> lethal failure).*

The shipped detector grants **`AUDITED_SHALLOW`**, not `audited_deep`, and requires **no**
sign-off. On the corroboration half, this is therefore a **conformance defect against a standing
architectural invariant** — not a new decision requiring ratification. The invariant does not
change; the code is brought to it.

Only **Finding B** amends a ratified decision (§4.2).

---

## 2. Impact Analysis

### 2.1 Epic impact

| Epic | Impact |
|---|---|
| **Epic 1** (Story 1.5 — the detector) | Its locked denominator decision is amended. The story is `done` and stays done; the amendment is appended, struck-not-deleted (§3.4 evidence immutability). |
| **Epic 6** (Prosecutor) | No change proposed. Finding E is recorded as a characterisation of the delivered design, not a defect in it — the promoter is correct for its own purpose. What was wrong was relying on it as this class's gate. |
| **Epic 13** (Earn the Gate) | **Cannot complete as planned.** Its output measured an instrument since found defective. It gains one story (13.5) to re-run the measurement once the instrument is fixed, and its completion now depends on the new epic. |
| **NEW Epic 14** | The build work. Two stories. |

**Epic 13 is not rolled back and its record is not rewritten.** The 0/26 measurement remains a
true, byte-reproducible measurement *of the detector as it was on 2026-08-17*. The adjudication
record is append-only; new findings produce new rows, and the existing 31 rows stay as history.

### 2.2 Story impact

**New — Epic 14:**

- **14.1 — A verdict-eligible vacuous finding proves vacuity, not mocking.** Replaces fact (b) with
  a signal that discriminates. CC#6 conformance. Blocking for 13.5.
- **14.2 — The density scorer counts statements, and knows the assertions the ecosystem writes.**
  Findings B and C. Amends the Story 1.5 lock.

**New — Epic 13:**

- **13.5 — Re-measure the gate against the corrected instrument.** Re-audit the five ratified
  members at their **unchanged** pinned shas, append superseding adjudication rows for the new
  finding population, re-run `decide_gate`, and record whatever it says.

**Unaffected:** 13-4 (`split-the-status-document-registry`, `ready-for-dev`) is independent and
need not wait.

### 2.3 Artifact conflicts

| Artifact | Change | Weight |
|---|---|---|
| `epics.md` | Add Epic 14; amend Epic 13 (story 13.5 + dependency) | Structural — `epics.md` currently ends at Epic 13 (`AI-E13-12`) |
| `stories/1-5-…md` | Amend the locked denominator decision, dated, struck-not-deleted | **Ratified-decision amendment** |
| `architecture.md` | Add a *Vacuity-corroboration enforcement* entry to §Enforcement, recording the CC#6 divergence and what now enforces it | Additive; CC#6 itself unchanged |
| `E-PRD/prd.md` | Append to §Business Success: the recorded `BLOCKED` measurement was taken with an instrument since found defective; frontmatter `amendments` entry | Amendment; **FR10 unchanged** |
| `sprint-status.yaml` | `epic-14`, `14-1`, `14-2`, `13-5` entries | Mechanical |
| `deferred-work.md` | Correct `DF-13-3-A` (§2.6); file the deferred refinement in §3.4 | Correction + new entry |

**No change to FR10.** Its binding text — *"detect tests that appear vacuous … and report them as
**advisory** findings carrying their evidence counts"* — describes what the detector will still do.
**No change to the >=80% threshold, the corpus, or FR34.** Moving any of those in response to a
failed measurement is precisely what protocol §5 and Story 13.3 / AC5 forbid.

### 2.4 Technical impact

- **`tests/test_vacuous_detector.py`** — `TC-ArgusAgent-DETECT-001-86` pins the *current*
  corroboration behaviour using a test that asserts on `sut`, the real SUT result. Under a correct
  fact (b) that example must **not** corroborate. The test is re-authored by 14.1; the story must
  state that as an intended behaviour change with its reason, not slip it in.
- **Cartridges** — `vacuous_basic`, `holdout_vacuous`, `nonascii_unicode` assert that a planted
  vacuous test still emits `vacuous_test_ast` and blocks (`max_blocking=1`, exit 2). **Measured as
  preserved** — see §3.4.
- **Dogfood artifacts** — detector-output-dependent, guarded by
  `test_dogfood_artifact_currency.py`; regenerate through their own renderers (the existing
  `scripts/regenerate_dogfood_artifacts.py` path).
- **Records go stale** — `validation-corpus/adjudication-record.json` and
  `gate-decision-record.json` describe the old finding population. 13.5 supersedes; it must not
  rewrite.
- **Windows-only local gates.** The corroboration work adds source-text scanning, which is
  path- and newline-adjacent. CI runs an ubuntu matrix and this repository has shipped POSIX-only
  bugs out of a green Windows run. 14.1 and 14.2 must not be marked done on a local pass alone.

### 2.5 The consequence that is not a build problem

**Correcting the detector will probably make the precision gate *unevaluable* rather than
*cleared*, and that must be understood before approving.**

Measured: under the candidate predicate (§3.4), corroborated findings across the whole minions test
tree go from **24 to 0**. If the other four members behave similarly, the corrected detector emits
**no blocking findings** on the ratified corpus. `architecture.md` records that an **empty precision
denominator is `UNEVALUABLE`, not the `Fraction(1,1)` convention that read as "cleared"**. Deleting
the findings deletes the measurement, not the shortfall.

So the honest range of outcomes for 13.5 is:

- **`BLOCKED` / `UNEVALUABLE`** — most likely. No blocking findings to adjudicate; the FR34
  disclosure stays.
- **`CLEARED`** — only if the corrected detector finds genuinely vacuous tests on the corpus and
  the named human adjudicates ≥80% of them real.

**This is not an argument against the fix.** A tool that blocks builds on evidence it does not have
is worse than a tool that blocks nothing. But it means **the fix does not clear the gate**, and the
path to a cleared gate may require a corpus that actually contains the defect class Argus exists to
catch. That is an operator decision, flagged here and deliberately not taken by this proposal.

### 2.6 A defect found in the record while measuring

**`DF-13-3-A` is wrong and should be corrected.** It records the `agent-smith` pinned sha
`9ab774d7…` as unreachable — *"absent from the remote and from every git repository found in a
depth-4 scan of the local drives"* — and 7 of the 31 findings were consequently adjudicated against
a reconstruction at `origin/development d9bb793`.

The repository is on this machine at `D:/ProjectX/XAgents/XAgents/XAgents/Agent-Smith` — depth
**five**, one level past where that scan stopped. Its `origin` is the same
`https://github.com/Inan15/agent-smith.git` the entry names, and the pinned sha is that checkout's
`HEAD`:

```
$ git -C D:/ProjectX/XAgents/XAgents/XAgents/Agent-Smith cat-file -t 9ab774d7bf5d61da552c61094b2d478f72dfbb6d
commit
```

All 7 agent-smith findings in §1.3 were therefore measured against the **true pinned tree**. A
commit sha is a content identity, so byte-identity with the audited source **is** established for
those 7 and their evidence is as strong as the minions rows, not weaker. This does not move the
gate — `BLOCKED` rests on the 5 undispositioned rows — but the ledger should stop saying the
evidence is unrecoverable.

---

## 3. Recommended Approach

### 3.1 Options evaluated

| # | Option | Verdict |
|---|---|---|
| 1 | **Direct adjustment** — fix all three defects under a new epic, then re-measure | ✅ **Selected** |
| 2 | **Rollback** — revert Story 1.5 / withdraw the detector | ❌ Not viable. It is the product's wedge (PRD §What Makes This Special). Withdrawing it removes the only differentiator; the defect is in one predicate, not the concept. |
| 3 | **PRD MVP review** — re-scope the vacuous detector out of V1 | ❌ Not viable and not needed. FR10's contract is already satisfied by the advisory half, which is not defective. Only verdict-eligibility is. |
| 4 | *(Considered and rejected)* Demote `vacuous_test_ast` to advisory permanently | ❌ Rejected. It clears the false accusations by removing the capability, leaves the FR20 recall cartridges with nothing to assert, and yields `UNEVALUABLE` anyway — the same outcome as option 1 without the fix. |

### 3.2 Selected: Option 1, sequenced

```
Epic 14 (build)                          Epic 13 (measure, re-opened)
  14.1  corroboration -> CC#6 conformance  ─┐
  14.2  density scorer + assertion names   ─┴─>  13.5  re-audit, re-adjudicate, re-decide
  (13-4 proceeds independently)
```

14.1 before 14.2: the moat is the defect that causes harm, and 14.2 changes flag *volume*, which is
easier to evaluate once eligibility is correct.

### 3.3 Effort, risk, timeline

| | Assessment |
|---|---|
| **Effort** | 14.1 Medium · 14.2 Low–Medium · 13.5 Low to run, gated on a human adjudication (protocol §3's ≤4 expert-hour ceiling is a report, not a gate) |
| **Technical risk** | **Medium.** The predicate must separate real vacuity from mock-using-but-valid tests with no dataflow. Measured as achievable (§3.4), but the probe is not production quality. |
| **Governance risk** | **Low.** The corroboration half conforms to a standing invariant; only the denominator is an amendment, and it is recorded. |
| **Strategic risk** | **The real one — §2.5.** The gate probably becomes `UNEVALUABLE`. |
| **Timeline** | Does not block 13-4. Does block Epic 13 closure and the epic-13 retrospective, which is already `in-progress` on an INTERIM document. |

### 3.4 Feasibility, measured

The recommendation rests on a claim that must not be asserted: **that a name-level fact (b),
reachable from the unresolved 1.4 edge set plus source text and with no dataflow, separates real
vacuity from the 31 false positives.**

The planted cartridges carry a signature the 31 do not: the SUT is called **with its result
discarded**, and the assertion is on a value bound from a **separately configured mock**. A probe
was built out of tree implementing exactly that — bind mock names, classify calls whose receiver is
a mock-bound name as mock-derived rather than SUT, require that no SUT call's result is consumed,
and require that an assertion references a mock-bound value.

| Population | Requirement | Measured |
|---|---|---|
| 3 planted-vacuous cartridges (incl. the anti-overfitting **holdout** and the non-ASCII one) | must stay corroborated | **3 / 3 kept** |
| 31 adjudicated findings | must lose corroboration | **30 / 31 demoted** |
| Whole minions test tree, 3,509 test functions | — | promotions **24 → 0** |

**The single survivor is `test_ir_copilot.py:128`, and it is not an FP** — the adjudicator recorded
it **BORDERLINE**, for the same reason the probe keeps it:

> *"asserts fail-closed behaviour via `pytest.raises(...)`, which is a genuine constraint on the
> SUT, but its only other assertion is `call_count == MAX_RETRIES + 1`, which constrains the mock's
> interaction rather than the system's output. Real in one direction, mock-interaction in the
> other."*

The probe's one retained corroboration lands on the one finding the named human could not call
clean. That is a point in the approach's favour, not against it.

**One probe defect identified, to be specified in 14.1 rather than inherited:** a SUT call inside a
`pytest.raises` / `assertRaises` context is currently read as *result discarded*, when raising **is**
the observation. 14.1 must treat a raises-context SUT call as consumed.

**What this probe is not.** It is a feasibility measurement, not a design. 14.1 owns the
implementation, its purity (AR8), its determinism (NFR-D2/AR4), and its own tests. Full
dataflow-grounded provenance remains **Story 6.2**'s scope and is not claimed here.

---

## 4. Detailed Change Proposals

### 4.1 `epics.md` — 2 edits

**Edit 4.1.1 — new epic, appended after Epic 13.**

```markdown
## Epic 14: Make the Moat Hold — the blocking rule proves what it claims · *Argus repo*

Epic 13 measured the >=80%-precision gate and returned 0 TP / 26 FP over 31 findings in one rule
class. The measurement worked; what it found is that the instrument is defective. This epic fixes
the instrument. It does NOT re-measure — that is Story 13.5, and it does not begin until this epic
closes.

**Covers:** the cross-cutting-#6 conformance gap; the Story 1.5 denominator amendment
**Depends on:** nothing. **Blocks:** Story 13.5, and therefore Epic 13's closure.
**Source:** [sprint-change-proposal-2026-08-17.md](sprint-change-proposal-2026-08-17.md)

> ⚠️ **This epic does not clear the gate and cannot.** Correcting the detector is expected to take
> the corpus to zero blocking findings, which `architecture.md` records as `UNEVALUABLE`, never
> `CLEARED`. Clearing requires findings that are real, which requires a corpus containing the
> defect class. That is an operator decision recorded at §2.5 of the source proposal, not work in
> this epic.

### Story 14.1: A verdict-eligible vacuous finding proves vacuity, not mocking

As the Argus maintainer,
I want the AST corroboration step to be evidence that the asserted values do not derive from the
SUT, so that a 🔴 rests on the fact cross-cutting concern #6 requires rather than on the presence
of a mock.

**Acceptance Criteria:**

**Given** `_ast_corroborated`'s fact (b) is `assertion_sites >= 1 and mock_sites >= 1`, and across
1,836 heuristically-flagged tests in the two contributing corpus members `ast_corroborated` is
equivalent to `mock_sites >= 1` in 1,835 cases
**When** this story completes
**Then** fact (b) is a signal that discriminates real vacuity from mock-using-but-valid tests, and
the equivalence above no longer holds on the same population — re-measured and recorded, not
asserted.

**Given** the false-accusation moat is the point
**Then** a test whose assertions constrain the real SUT result is NOT corroborated, however many
mocks it constructs; and a SUT call inside a `pytest.raises` / `assertRaises` context counts as
result-CONSUMED, because raising is the observation.

**Given** cartridges `vacuous_basic`, `holdout_vacuous` and `nonascii_unicode` assert that a
planted vacuous test emits `vacuous_test_ast` and blocks — `holdout_vacuous` being the
anti-overfitting control
**Then** all three stay green, and the story records the measured recall rather than assuming it.

**Given** `TC-ArgusAgent-DETECT-001-86` currently pins corroboration on a test that asserts on the
real SUT result
**Then** it is re-authored as an intended behaviour change, with the reason recorded in the story —
never silently adjusted to match new output.

**Given** the conservative default IS the moat (module docstring)
**Then** where the unresolved edge set cannot establish fact (b), corroboration is NOT granted and
the finding stays `vacuous_test_heuristic` / advisory.

**Given** AR8 (the scorer is PURE), AR4 (`Fraction`, never `float`) and NFR-D2 (deterministic,
zero-token)
**Then** all three hold unchanged, and no clock / uuid / random / iteration-order enters any
`.argus/`-bound output.

**Given** local gates are Windows-only and CI runs an ubuntu matrix
**Then** this story is not marked done on a local pass alone.

### Story 14.2: The density scorer counts statements, and knows the assertions the ecosystem writes

As the Argus maintainer,
I want the assertion-density score computed over real statements and real assertions,
So that the advisory signal stops flagging half of every test suite.

**Acceptance Criteria:**

**Given** `_count_statements` counts non-blank/non-comment LINES, measured at 2.04x inflation
against a true statement count over 1,812 flagged tests
**When** this story completes
**Then** the denominator counts statements, multi-line statements count once, and the Story 1.5
locked decision is amended at its source with a date and a reason (struck, never erased).

**Given** `_ASSERTION_CALLEES` is documented as "unittest family + pytest helpers" and contains no
pytest helper
**Then** it recognises `pytest.raises`/`warns`, the `unittest.mock` assertion methods, and
project-defined helpers by naming convention — 13 of the 31 adjudicated findings call an assertion
it cannot currently see.

**Given** the thresholds `ASSERTION_DENSITY_FLOOR = 1/4` and `MOCK_RATIO_CEILING = 1/2`
**Then** they are NOT changed by this story. A failed measurement is not a reason to move a
threshold; if the corrected counts argue for different thresholds, that is a separate, evidenced
decision.

**Given** the flag rate is 51.6% of all test functions on the minions tree today
**Then** the story records the re-measured rate over the same population, as a number.

**Given** committed dogfood artifacts are detector-output-dependent
**Then** they are regenerated through their own renderers and
`test_dogfood_artifact_currency.py` is green.
```

**Edit 4.1.2 — Epic 13 gains Story 13.5 and a dependency note.**

```markdown
> ⚠️ **RE-OPENED 2026-08-17.** Stories 13.1-13.3 completed and the gate decision was recorded as
> `BLOCKED`. The measurement then established that the single rule class it measured is defective
> (sprint-change-proposal-2026-08-17.md). Epic 13 cannot close on a measurement of a broken
> instrument. **Story 13.5 re-runs it; Epic 14 blocks 13.5.** The 13.1-13.3 records are NOT
> rewritten - they are the true measurement of the detector as it stood on 2026-08-17.

### Story 13.5: Re-measure the gate against the corrected instrument

**Given** Epic 14 has closed and the detector's blocking rule now proves vacuity
**When** the five ratified members are re-audited at their UNCHANGED pinned shas
**Then** the new blocking-finding population is adjudicated by the named human (protocol §2), the
rows are APPENDED as superseding rows - the record is append-only and 13.1-13.3's rows stay - and
`decide_gate` is re-run over the result.

**Given** correcting the detector is expected to take the corpus to zero blocking findings
**Then** an empty precision denominator is recorded as `UNEVALUABLE`, never as `CLEARED`, and the
FR34 disclosure stays. Whatever the arithmetic says is what is recorded.

**Given** `DF-13-3-A` records the agent-smith pinned sha as unreachable
**Then** that entry is corrected first (it is reachable - see §2.6 of the source proposal), so the
re-run measures all five members against their true pinned trees.
```

### 4.2 `stories/1-5-…md` — 1 edit (the ratified-decision amendment)

In **Locked contract decisions**, the denominator bullet:

**OLD**
```markdown
- **Assertion-density denominator = test-body STATEMENTS** (non-blank/non-comment body lines, def
  header excluded) — robust to multi-line statements.
```

**NEW**
```markdown
- **Assertion-density denominator = test-body STATEMENTS** ~~(non-blank/non-comment body lines, def
  header excluded) — robust to multi-line statements~~ **— AMENDED 2026-08-17 by
  sprint-change-proposal-2026-08-17.md / Story 14.2.** The struck text is self-contradictory: a
  count of LINES is not robust to multi-line statements, it is the thing multi-line statements
  break. Measured against a true statement count over 1,812 flagged tests in the minions corpus,
  the line count inflates the denominator **2.04x**, and correcting it alone lifts 14 of the 31
  adjudicated false positives back above the 1/4 floor. The decision was validly taken — AC1
  delegated the choice of denominator to the dev — so it is amended on the record, not treated as a
  gap. The denominator is now real statements; multi-line statements count once.
```

**Rationale:** Story 1.5 is `done` and stays `done`. §3.4 evidence immutability: the decision was
the state the story was written in, so it is struck rather than erased.

### 4.3 `architecture.md` — 1 edit

Append to §Enforcement, in the established house form:

```markdown
**Vacuity-corroboration enforcement** *(added 2026-08-17 by Story 14.1)*. **The rule: a
`vacuous_test_ast` finding is verdict-eligible only on evidence that the asserted values do not
derive from the SUT - never on the mere presence of a mock.** Cross-cutting concern #6 has required
`audited_deep` AST corroboration AND Prosecutor sign-off since the architecture was written; the
Story 1.5 detector shipped `AUDITED_SHALLOW` with no sign-off, and its fact (b) reduced to
`mock_sites >= 1`. **Measured on the day it was found, which is why this is a rule and not a
preference:** over the ratified 5-repository corpus the rule class emitted 31 blocking findings and
the named human adjudicated 0 of them true - and across 1,836 heuristically-flagged tests
`ast_corroborated` was equivalent to `mock_sites >= 1` in 1,835 cases, so the corroboration step
added no evidence the heuristic did not already have. The Epic-6 Prosecutor does not close this:
`prosecutor.py:56-57` leaves an ALREADY-eligible finding UNCHANGED, so sign-off gates only the
promotion path, and the V1 call site passes no sign-offs. **The moat is therefore enforced at the
detector**, and the conservative default is restored: where the unresolved 1.4 edge set cannot
establish fact (b), corroboration is NOT granted and the finding stays advisory.
```

### 4.4 `E-PRD/prd.md` — 2 edits

**Edit 4.4.1** — append to §Business Success, after the 2026-08-17 correction:

```markdown
⚠️ **The instrument, recorded 2026-08-17 (sprint-change-proposal-2026-08-17.md).** The `BLOCKED`
decision above is a true and byte-reproducible measurement, and it stands. What it measured has
since been established as defective: all 31 findings are one rule class, `vacuous_test_ast`, whose
AST corroboration step tests whether a test constructs a mock rather than whether the asserted
values derive from the SUT - a conformance gap against cross-cutting concern #6. **Epic 14 fixes
the instrument and Story 13.5 re-measures.** ⛔ **Nothing here clears, softens or re-scopes the
gate, and the >=80% threshold and the corpus are unchanged** - moving either in response to a
failed measurement is what protocol §5 and Story 13.3 / AC5 forbid. **The expected outcome of the
re-run is `UNEVALUABLE`, not `CLEARED`:** a corrected detector is expected to emit no blocking
findings on this corpus, and an empty precision denominator is `UNEVALUABLE` by construction.
```

**Edit 4.4.2** — frontmatter `amendments`:

```yaml
  - date: 2026-08-17
    scope: >-
      The recorded BLOCKED gate decision is annotated with the defect found in the instrument it
      measured (vacuous_test_ast corroboration vs cross-cutting #6). Epic 14 added to fix the
      detector; Story 13.5 added to re-measure. FR10 is UNCHANGED - its contract is the advisory
      finding with evidence counts, which is not the defective half. The >=80% threshold, the
      corpus and FR34 are unchanged, and this amendment does not clear the gate.
    signal: _bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-08-17.md
    approvedBy: XAgent007
    sections: ['Business Success']
```

### 4.5 `sprint-status.yaml` — 4 entries

```yaml
  epic-14: backlog          # added 2026-08-17 by sprint-change-proposal-2026-08-17.md
  14-1-a-verdict-eligible-vacuous-finding-proves-vacuity-not-mocking: backlog
  14-2-the-density-scorer-counts-statements-and-knows-the-assertions: backlog
  13-5-re-measure-the-gate-against-the-corrected-instrument: backlog   # BLOCKED on epic-14
```

Epic 13 stays `in-progress`; `epic-13-retrospective` stays `in-progress` on its INTERIM document
and cannot close until 13.5 completes.

### 4.6 `deferred-work.md` — 2 edits

**Edit 4.6.1** — correct `DF-13-3-A` with an appended, dated note (never a rewrite): the pinned sha
IS reachable at `D:/ProjectX/XAgents/XAgents/XAgents/Agent-Smith`, depth 5, past the depth-4 scan
that filed the entry; `origin` matches; byte-identity with the audited source IS establishable for
those 7 findings; the "no longer re-verifiable" consequence is withdrawn on evidence.

**Edit 4.6.2** — file `DF-14-1-A`: name-level fact (b) is a proxy. True dataflow-grounded assertion
provenance remains **Story 6.2**'s scope; 14.1 delivers the conservative name-level version and the
entry records what it cannot prove.

---

## 5. Implementation Handoff

**Scope classification: MAJOR.** It adds an epic, amends a ratified story decision, amends the PRD,
and raises a strategic question (§2.5) that is the operator's to answer.

| Recipient | Responsibility |
|---|---|
| **PM / Architect (XAgent007)** | Approve this proposal. Answer §2.5: if the corrected detector yields `UNEVALUABLE`, is the path to a cleared gate a corpus containing real vacuous tests, or does the FR34 disclosure stay indefinitely? **Not a build decision.** |
| **Scrum Master** (`bmad-create-story`) | Context 14.1, then 14.2 |
| **Developer** (`bmad-dev-story`) | Implement 14.1 → 14.2 |
| **Review** (`bmad-code-review`, Sonnet) | Adversarial review per story |
| **Named human adjudicator (XAgent007)** | 13.5's adjudication — protocol §2, no agent may supply it |

**Success criteria for the change as a whole:**

1. `ast_corroborated` no longer equivalent to `mock_sites >= 1` on the same 1,836-test population — re-measured.
2. All 3 planted-vacuous cartridges still block; `holdout_vacuous` green.
3. The 31 adjudicated locators re-measured, with the count that remain verdict-eligible recorded.
4. Flag rate over the minions tree re-measured against today's 51.6%.
5. Full suite green **on both Windows and the ubuntu CI matrix**.
6. Dogfood artifacts regenerated and current.
7. 13.5 records whatever the gate says — including `UNEVALUABLE`.

---

## 6. Approval

✅ **APPROVED** by **XAgent007** on **2026-08-17**

**Applied 2026-08-17.** All six §4 edits landed:

| § | Artifact | Applied |
|---|---|---|
| 4.1.1 | `epics.md` — Epic 14 + stories 14.1, 14.2 | ✅ |
| 4.1.2 | `epics.md` — Epic 13 RE-OPENED note + Story 13.5 | ✅ |
| 4.2 | `stories/1-5-…md` — denominator lock amended, struck-not-deleted | ✅ |
| 4.3 | `architecture.md` — *Vacuity-corroboration enforcement* | ✅ |
| 4.4 | `E-PRD/prd.md` — §Business Success annotation + frontmatter amendment | ✅ |
| 4.5 | `sprint-status.yaml` — `epic-14`, `14-1`, `14-2`, `13-5` | ✅ |
| 4.6 | `deferred-work.md` — `DF-13-3-A` corrected; `DF-14-1-A` filed | ✅ |

**`argus/` is byte-unchanged by this proposal.** No detector, threshold, predicate or test was
modified — that is Epic 14's work, and it has not started.

**⚠️ Open, and owned by the operator — §2.5.** If the corrected detector yields `UNEVALUABLE`
rather than `CLEARED`, the path to a cleared gate requires a corpus that contains the defect class.
That decision is not scheduled by this proposal and is not a build task.
