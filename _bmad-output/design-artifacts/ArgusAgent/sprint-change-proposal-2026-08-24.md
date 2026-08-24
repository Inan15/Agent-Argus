# Sprint Change Proposal — 2026-08-24

**Author:** XAgent007 (Engineering Lead) · **Workflow:** `bmad-correct-course` · **Mode:** incremental
**Trigger:** operator-directed; **no story**. The Epic 16 roll-up (`5cc83af`) closed `epics.md` at
Epic 16 with no Epic 17, and both outstanding operator obligations have now been taken.
**HEAD at authoring:** `7d8c9ba`

> ⛔ **STATUS: AWAITING OPERATOR APPROVAL.** Epics 17 and 18 and all nine stories are filed at
> `backlog`. Nothing in either epic may start before approval.
>
> ⛔ **THIS PROPOSAL DOES NOT SPEND `DF-13-5-A`'s ROUND, and approving it is not approval to spend
> it.** The entry was DECLINED a second time on 2026-08-24 (`7edf74e`), stays **OPEN and UNSPENT**,
> `members_ratified` **NONE**, `protocol_edit` **NONE**. No member is ratified and no third-party
> source is fetched by anything proposed here.

---

## 1. Issue Summary

### What triggered this

Two operator obligations were left open by the Epic 16 roll-up, and both were discharged on
2026-08-24:

1. **`DF-13-5-A`'s re-review trigger fired** when Stories 16.6 and 16.7 both reached `done`. Ruling:
   **DECLINED**, with the calendar-shaped trigger replaced by a substantive one (`7edf74e`, sharpened
   later the same day in `7d8c9ba`).
2. **"What is Epic 17 for?"** — the Epic 16 retrospective named three candidate charters and
   deliberately chose none. The operator declined to choose from the menu and asked instead whether
   the detectors were mis-built or the defect class simply rare. **That question was answered by
   measurement**, and the answer is neither.

### The core problem, stated precisely

*Category: technical limitation discovered during implementation.*

`argus/detectors/vacuous_test.py` is a two-stage detector. **The two stages are graded on different
definitions of "vacuous", and on the ratified corpus their intersection is empty.**

- **Stage 1 (flagging)** fires on `assertion_density < 1/4` **OR** `mock_ratio > 1/2` — a **density**
  property, proxy for test *style*.
- **Stage 2 (corroboration, "fact (b)")** requires a discarded SUT call, **no** consumed SUT call,
  **and** an assertion referencing a **mock-bound name** — a **provenance** property, proxy for test
  *wiring*.

### Evidence

Full record: [research/technical-argusagent-stage-mismatch-measurement-2026-08-24.md](research/technical-argusagent-stage-mismatch-measurement-2026-08-24.md),
committed at `7d8c9ba` with five reproducible harnesses under `research/`. Measured over **all 1,032**
`vacuous_test_heuristic` findings at the five pinned corpus shas:

| observation | value |
|---|---:|
| stage 1 selection: `density_only` | **1,025 (100%)** |
| stage 1 selection: `mock_only` / `both` | **0 / 0** |
| stage 2 promotions (shipped fact (b)) | **0** |
| `mock_referencing_assertions ≥ 1` | **0 of 1,032** |
| flagged tests binding **no mock at all**, by any idiom | **1,025 (99.3%)** |
| carrying ≥3 **consumed** SUT calls | **917 (88.9%)** |

⛔ **Three findings that change what the project believed:**

1. **"The corroborable ceiling is six" is a misreading.** Six is `W1` — fact (b) with its
   mock-referencing clause **deleted**. The shipped predicate's output is **zero**, and always was.
2. **The obvious repair is a dead end, and this was measured rather than assumed.**
   `_mock_bound_names` genuinely cannot see `@patch` injection, fixture injection, or `setUp`'s
   `self.attr`. An extended resolver covering all four idioms moves the count **0 → 1**. Filed as
   `DF-INV-VACUOUS-B` precisely so it is not later mistaken for the remedy.
   **Control:** the corpus *does* mock (23.2% / 22.9% / 11.5% of test files in three members) — the
   **flagged population** does not.
3. **The reading error underneath both `DF-13-5-A` branches.** *"0 blocking findings"* has been read
   as a fact about the **world** — the detector is too conservative (branch b), or the corpus too
   small (branch a). **It is a fact about the instrument.** No conclusion about the real-world base
   rate of vacuous tests is available from this evidence.

### A second issue, found while assessing impact

**`Story 6.2` is `done`, and it never contained the work four modules and six ledger entries say it
owns.** Its story file explicitly carves out dataflow — *"does NOT re-parse source, does NOT add a
second tree-sitter call"*, *"only GRADES grounding"* — and it was scoped to claim-grounding for
**non-test** Python files, closing `DF-1-7-B`.

Dangling references: `argus/detectors/provenance_scan.py:55`, `argus/audit/deep_pass.py:93` and
`:314`, `argus/audit/deep_audit.py:23`, `argus/audit/__init__.py:13`; ledger entries `DF-12-2-D`,
`DF-12-3-A`, `DF-14-1-A`, `DF-16-7-A`, `DF-16-7-B`, `DF-INV-VACUOUS-A`. ⚠️ **`DF-1-7-B` is NOT in
that set** — it is CLOSED and correctly names 6.2 as its closer.

⛔ **Consequence for the prior research.** The 2026-08-21 detector-categories research recommends
*"Complete Story 6.2 … already scheduled."* It rests on the stale reference. **The
assertion-strength work is not scheduled anywhere** — it has no container at all, which is `SD-5`'s
pathology recurring. This strengthens the case for a new epic rather than weakening it.

---

## 2. Impact Analysis

### Epic impact

| Epic | Impact |
|---|---|
| **Epics 1–16** | **None.** All `done`, retrospectives signed. ⛔ **Not reopened, not regenerated** — the `sprint-status.yaml` header rule and the Epic 8/9/10 delta precedent both forbid it. |
| **Epic 6 / Story 6.2** | ⛔ **Not reopened.** Its closed record stands. The work it was believed to own is re-homed forward, never backward. |
| **Epic 17 (new)** | Carries the assertion-strength capability. 5 stories. |
| **Epic 18 (new)** | Discharges the 2026-08-24 detector audit. 4 stories. Sequenced **first**. |

### Story impact

No existing story changes status, scope or acceptance criteria. **This proposal adds; it does not
edit delivered work.**

### Artifact conflicts

| Artifact | Change |
|---|---|
| `epics.md` | Two new epic sections; a one-line note under the FR7 / FR10 / FR11 Coverage-Map rows |
| `sprint-status.yaml` | 13 new keys at `backlog` (109 → 122) |
| `tests/test_status_document_registry.py` | This document registered — `-22`'s glob closure sees it |
| `deferred-work.md` | ⏸️ **DEFERRED to a follow-up commit** — see §5 |
| `prd.md` | **None.** No FR added, amended or dispositioned. The ≥80% keystone is untouched and stays **NOT CLEARED** |
| `architecture.md` | **None.** Cross-cutting #6 is satisfied, not changed — the conservative default remains the moat |
| UX / spec | **N/A** — this project has neither |

⚠️ **Observed, NOT fixed here.** `epics.md`'s Requirements Inventory, FR Coverage Map and Final
Validation Summary all stop at **Epic 13** — Epics 14, 15 and 16 never updated them. That drift
predates this proposal; fixing it here would be scope creep. It is recorded for the Epic 17
retrospective.

### Technical impact

Epic 17 changes detector internals only; no new architecture, no execution sandbox, no egress seam,
no new adjudicator role. Epic 18 changes `secret_scan` / `secret_suppression` behaviour in the
**under-reporting-to-correct** direction.

---

## 3. Recommended Approach

**Option 1 — Direct Adjustment, as a new-epic delta.** ✅ **SELECTED.**

- **Option 2 — Rollback:** ❌ not viable and not desirable. Nothing is broken to revert. The code is
  careful, pure and well-tested; Story 14.1's conformance repair was correct; `consumed == 0` is
  doing its job.
- **Option 3 — PRD / MVP review:** ❌ not required. No FR moves and the ≥80% keystone is unchanged.
  The gate stays `BLOCKED`; FR34's DISCLOSED tier remains the honest fallback.

**Effort:** Medium (9 stories across 2 epics). **Risk:** Medium — concentrated in Story 17.3, and
mitigated by 17.1 landing first. **Timeline:** unblocks nothing currently scheduled; Epic 18's 18.1
is days.

⛔ **Two constraints carried onto the charter, not into its aftermath:**

1. **Yield and precision move in opposite directions.** Going from 0 to ~12% eligible mechanically
   increases false-accusation exposure, and ≥80% precision is the whole gate. **Story 17.1 —
   pre-registration — must land before any successor predicate exists**, enforced by a git-ancestry
   guard in 17.4. This is the 2026-08-17 discipline applied one level down.
2. **`consumed == 0` is NOT loosened.** It is what keeps the false-accusation moat closed. Epic 17
   **replaces** the vacuity signal; it does not widen fact (b) by clause removal. Per `DF-16-7-B`, a
   different predicate must be **argued** as one — Story 17.2 is that argument.

---

## 4. Detailed Change Proposals

Full text of both epic sections and all nine stories is written directly into `epics.md` by this
change. Summary:

**Epic 17: Say What The Assertion Constrains — grade strength, not wiring**
*Capability delivered:* the detector grades **what a test's assertions actually constrain about the
value the code under test returned**, replacing a mock-provenance signal that cannot fire.
*Covers:* FR10 · FR7 · cross-cutting #6 · `DF-INV-VACUOUS-A` · `DF-14-1-A` · `DF-16-7-A` ·
`DF-16-7-B` · `DF-12-2-D` · `DF-12-3-A`

| Story | Purpose |
|---|---|
| 17.1 | Pre-register the precision criterion **before the predicate exists** |
| 17.2 | Specify the successor and argue it as a **different** predicate |
| 17.3 | Grade what each assertion constrains (**+ `DF-AUD-DETECT-D`**; `-C` as context) |
| 17.4 | Measure once over the five ratified members; the pre-registered criterion decides |
| 17.5 | Re-home the `Story 6.2` danglers + a guard so it cannot recur |

**Epic 18: The Secret Detector Reports What It Finds — discharge the detector audit**
*Capability delivered:* a hardcoded credential is no longer silently dropped because the value it
sits in happens to contain the substring `localhost`.
*Covers:* FR11 · FR28 · `DF-AUD-DETECT-A` · `-B` · `-E` · `-F`

| Story | Purpose |
|---|---|
| 18.1 | Sentinel table matches **values, not substrings**; `DF-10-3-B` falsification recorded |
| 18.2 | The redaction call keeps the evidence it computes |
| 18.3 | Two regex precision defects |
| 18.4 | The `Detector` Protocol is load-bearing or it is deleted |

⛔ **Epic 18 is SEQUENCED BEFORE Epic 17 despite the higher number.** Epic numbers are creation
order in this repo; execution order is stated. `DF-AUD-DETECT-A` is a live security false negative
— reproduced through the shipped `SecretScanDetector.run()`, where a real credential in
`postgres://admin:Tr0ub4dor3@localhost:5432/prod` returns **0 findings** while the same value with
the sentinel substring removed returns **1**. **Nothing in Epic 17 depends on Epic 18**; the ordering
is urgency, not coupling.

⛔ **`DF-AUD-DETECT-A…F` are the peer session's UNCOMMITTED work at the time of writing.** This
proposal **cites** them and **schedules** them; it does not edit, dispose of or commit them.

---

## 5. Implementation Handoff

**Scope classification: MODERATE** — backlog reorganisation, no fundamental replan.

| Recipient | Responsibility |
|---|---|
| **XAgent007 (Engineering Lead)** | Approve or reject this proposal. Until then both epics stay `backlog` |
| **Scrum Master** (`bmad-create-story`) | Draft 18.1 first, then 17.1 |
| **Developer** (`bmad-dev-story`) | Implement in the stated order. ⛔ 17.1 **must** precede any 17.3 output over a corpus member |
| **XAgent007** | `AI-E16-7` — fill protocol §4's External adjudicator role **before** 17.4 produces borderlines, or 17.4 STOPS and reports which rows and why |

### Named follow-up, owed and dated

⏸️ **The `deferred-work.md` re-homing is DEFERRED to a follow-up commit, deliberately and with a
reason.** At authoring time that file holds a concurrent session's uncommitted `DF-AUD-DETECT-A…F`;
staging it by path would sweep unfinished work into this commit, and `git add -A` is forbidden on
this tree. **Owner:** Story 17.5. **What is owed:** dated append-only re-homing notes on
`DF-12-2-D`, `DF-12-3-A`, `DF-14-1-A`, `DF-16-7-A`, `DF-16-7-B` and `DF-INV-VACUOUS-A` pointing at
Epic 17; scheduling notes on `DF-AUD-DETECT-A`/`-B`/`-E`/`-F` pointing at Epic 18 and `-D` at Story
17.3. ⛔ **`DF-1-7-B` is not touched.** ⛔ **This is a deferral WITH a named owner and a written
scope — not a silence.**

### Success criteria

1. Epics 17 and 18 exist in `epics.md`, each carrying `Capability delivered:` **and** `Covers:` —
   closing the `MDB-1`/`MDB-2` gap that has run for four epics.
2. 13 keys land at `backlog`; both `epic-*-retrospective` keys created **in the same act**
   (`AI-E15-9`, second application, still no guard).
3. This document is registered in `_STATUS_DOCUMENTS`, observed **RED before and GREEN after**.
4. `DF-13-5-A` remains OPEN and UNSPENT; nothing published changes; the gate stays `BLOCKED`.
