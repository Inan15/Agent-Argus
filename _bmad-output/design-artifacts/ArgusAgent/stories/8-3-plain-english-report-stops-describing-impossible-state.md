---
baseline_commit: 9109e16b4e86436a8315ed2cb967b75cdced4296
baseline_note: >-
  HEAD is 9109e16, but the working tree carries Stories 8.1 AND 8.2's deltas
  UNCOMMITTED (git status: ~14 modified argus/ + tests/ files, 3 added test
  files/fixtures). 8.3 builds ON TOP of that uncommitted tree. Do NOT stash,
  revert, `git checkout --`, or hard-reset anything — 8.1's and 8.2's work is
  not recoverable from any commit.
  Two untracked files at the repo root — `action.yml` and
  `.github/workflows/argus-student-audit.yml` — are the USER's (packaging/CI,
  Epic 9 territory). They are OUT OF SCOPE: do not modify, delete or build on
  them, and do not be surprised by them.
---

# Story 8.3: The plain-English report stops describing an impossible state

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **ArgusAgent story — Argus repo, `argus/` tree only.** ArgusAgent (formerly APAA) is a self-contained
> headless audit tool extracted from the Minions monorepo into its own repository (`Agent-Argus`,
> distribution `argus-agent`, package `argus/`, console scripts `argus` / `argus-agent` / `repo-audit`).
> **RS-1 is binding: all work lands in `argus/` in THIS repo. The `minions_core/apaa/` copy in the Minions
> repo is legacy — no modification, no back-port, no dual maintenance.** Planning artifacts live under
> `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is that folder's `sprint-status.yaml`. Prose in
> older documents saying `design-artifacts/APAA/` or `minions_core/apaa/` should be read as
> `design-artifacts/ArgusAgent/` / `argus/` (RS-4b, the bulk provenance sweep, is deferred out of this delta).
>
> **This is the THIRD story of Epic 8** ("The Honest Verdict — no block without a finding"). `epic-8` is
> already `in-progress`. **Stories 8.1 and 8.2 are both `done`** (each PASSED code review at iteration 2).
>
> **THIS STORY DELIVERS DR-11 — the report-surface reconciliation, on BOTH surfaces.** The verdict is now
> honest (8.1) and the critical gate is now satisfiable (8.2); the two *human* surfaces that describe them
> are not. `argus/reports/plain_english.py` renders the row-1 sentence *"too little of the code was examined
> deeply"* for a row-4 run that examined **100 %** of the code, and carries a `NOT VOUCHED` else-branch that
> `evaluate_verdict` can no longer reach. `argus/reports/generator.py` prints
> `> [!CAUTION] Repository is NOT ready for release …` six lines under
> `- **Final Verdict**: **INSUFFICIENT_COVERAGE** (Exit Code 3)` — a persisted artifact contradicting itself.
> **Everything below was reproduced live on this tree; nothing is quoted from a prior record on trust.**
>
> **It does NOT deliver:** DR-1/2/3/4/9 (Story 8.1, done); DR-5/6/7 (Story 8.2, done); DR-8 + RS-4a — the
> integrator release note and `argus/__init__.py`'s stale `minions_core/argus/` claim are **Story 8.4**;
> DR-10 — the dogfood re-derivation and BOTH published `final-verdict.md` artifacts are **Story 8.5**
> (sequenced last by design, so a slip stays visible).
>
> **DF-8-1-A IS pulled in — confirmed against `epics.md`.** The ledger entry
> (`deferred-work.md:498-518`) carries `target_story: 8-3 (DR-11 report-surface reconciliation)`, and the
> epic's Story 8.3 AC block independently owns the same code: *"Given `argus/reports/generator.py` — the
> **second** verdict-rendering surface, with its own FR16 reasoning … its independent branches on the verdict
> enum, deep-ratio threshold and `blocking_finding_count` (`:62-79`, `:304`) agree with the amended table."*
> Both halves of DF-8-1-A (`generator.py:337-339` **and** `plain_english.py:109-113`) are named in **AC5**
> and **AC2** respectively. **Fix it here.**
>
> **DF-8-2-A is NOT closed here, and that is the correct disposition.** `argus/pipeline.py` is at **1199 of
> the 1200-line NFR-M1 cap** (re-measured: `wc -l` = 1199). This story **does not need to touch
> `pipeline.py` at all** — every surface it changes is reachable from arguments `generate_reports` already
> receives. **AC14 fences `pipeline.py` as must-not-modify**, so the cap cannot be breached by this delta and
> the extraction stays queued for the next story that genuinely edits it. See **D6**.
>
> **DF-8-2-B is NOT pulled in.** Its ledger `target_story` is conditional — *"8-3 (**or the first story that
> edits `argus/detectors/vacuous_test.py`**)"* — and this story does not edit that file (AC14 fences it). It
> is a detector-semantics defect (🟢, zero live instances in this repo), not a report-surface one. See **D7**.

---

## Story

As an **operator reading the human output of `argus audit`** — who today can be handed a `final-verdict.md`
whose second line says `INSUFFICIENT_COVERAGE (Exit Code 3)` and whose eighth line says
`Repository is NOT ready for release`, or a stderr summary telling me *"too little of the code was examined
deeply"* about a run in which **every single file reached `audited_deep`** —

I want **the report to describe only states the gate can actually produce, and to describe each of them in
the words that are true of it**,

so that **I am not shown a branch the tool can no longer reach.** An assurance product whose own report
contradicts its own verdict has already demonstrated the defect class it exists to detect; the operator who
notices it stops believing the green results too.

---

## Story Context

### The bug, precisely — MEASURED IN PLACE on the real working tree

> ⚠️ **Method statement (read this; the 8.1 SM's method cost a fix round).** Everything in this section was
> produced by **importing the shipped `argus` functions and calling them in place** on
> `d:/ProjectX/XAgents/XAgents/ArgusAgent`, HEAD `9109e16` **plus 8.1's and 8.2's uncommitted deltas**, with
> `.git` and `_bmad-output/` present — **not** on a scratch copy (the 8.1 SM measured on a copy with no
> `.git` / no `_bmad-output/` and misclassified `tests/test_dogfood_proof.py`, which cost a review round;
> the 8.2 SM measured in place and was exact). The four FR16 rows were built with real
> `evaluate_verdict(...)` folds over real `CoverageLedger.build(...)` ledgers and real
> `build_recording(FindingDraft(...), depth_supported=...)` findings, then rendered through the real
> `render_ship_readiness` and `render_final_verdict_report`. No `.argus/` was written into this repo.
> **Re-derive these figures yourself — do not trust this table.**

**Surface A — `argus/reports/plain_english.py::_headline` (`:95-123`).** Rendered to **stderr** by
`cli.py:292` and embedded as the **first quoted line** of `final-verdict.md` by `generator.py:269`.

| FR16 row | Input measured | What `_headline` renders TODAY | Verdict |
|---|---|---|---|
| 1 — `row_1_below_floor` | 1/10 deep, 0 findings | `NOT ASSESSED — too little of the code was examined deeply to make any call.` | ✅ **correct** |
| 2 — `row_2_blocking_findings` | 3/5 deep, 1 AST-corroborated finding | `BLOCKED — 1 verdict-blocking finding(s) must be resolved.` | ✅ **correct** |
| 3 — `row_3_gates_met` | 3/5 deep, 0 findings | `READY — no blocking problems found, and enough of the code was examined deeply to say so.` | ✅ **correct** |
| 4 — `row_4_gate_unmet_no_findings` (coverage) | 2/5 deep, 0 findings | `NOT ASSESSED — too little of the code was examined deeply…` | ❌ **FALSE.** 40 % ≥ the 20 % floor; the floor is not what happened |
| 4 — `row_4_gate_unmet_no_findings` (critical only) | **5/5 deep**, 0 findings, 1 critical not deep | `NOT ASSESSED — too little of the code was examined deeply…` | ❌ **FALSE and absurd.** **100 % of files reached `audited_deep`** and the report says too little was examined |
| — | *(the `NOT VOUCHED` else-branch, `:119-123`)* | **NEVER RENDERED** | ❌ **unreachable** — see the sweep below |

**The unreachability sweep (this is the DR-11 proof, and it is a committed test in AC2).** Every
`(total 0..8) × (deep 0..total) × (blocking findings 0,1,2) × (criticals all-deep True/False)` combination —
**270 real `evaluate_verdict` folds** — produced exactly five `(verdict, row, has-blocking)` triples:

```
('INSUFFICIENT_COVERAGE', 'row_1_below_floor',           False) -> 24
('INSUFFICIENT_COVERAGE', 'row_1_below_floor',           True ) -> 48   # FLOOR WINS over findings
('INSUFFICIENT_COVERAGE', 'row_4_gate_unmet_no_findings', False) -> 47
('NOT_READY_FOR_RELEASE', 'row_2_blocking_findings',      True ) -> 132
('RELEASE_READY',         'row_3_gates_met',             False) -> 19
NOT_READY_FOR_RELEASE with blocking == 0  ->  0 occurrences
```

`_headline`'s trailing `return` fires **only** on `NOT_READY_FOR_RELEASE ∧ blocking_finding_count == 0`.
That state has **zero** occurrences. It is unreachable from `evaluate_verdict`, and `evaluate_verdict` is
the **only** producer of any verdict either surface ever renders (verified: `render_ship_readiness` is called
from `cli.py:292` and `generator.py:269`; `render_final_verdict_report` only from `generate_reports`, only
from `pipeline.py:793` — in every case with the live fold's result. **No code path in `argus/` re-renders a
verdict read back from disk**, so a pre-amendment `schema_version:"1"` payload cannot reach these functions).

> 🔑 **The resolution is not a deletion — it is a RELOCATION.** Read the unreachable branch's own text:
> *"NOT VOUCHED — nothing broken was found, but a coverage gate was not met, so no release-readiness claim
> is made. This is a statement about the audit, not about the code."* **That is exactly the row-4 message.**
> The prose is right and the predicate is wrong: it was written for the pre-amendment world where row 4's
> case arrived wearing a `NOT_READY_FOR_RELEASE` label. Move the words to where they are true; delete the
> predicate that can never fire. See **D2**.

**Surface B — `argus/reports/generator.py::render_final_verdict_report` (`:250-365`).** Writes the
**persisted** `final-verdict.md`.

| FR16 row | Branch taken | What it prints TODAY | Verdict |
|---|---|---|---|
| 3 | `if verdict.verdict.value == "RELEASE_READY"` (`:304`) | `[!TIP] Repository satisfies all deterministic release readiness criteria.` | ✅ correct |
| 1 | `elif verdict.is_below_floor` (`:306`) — **8.1's fix** | `[!WARNING] Repository deep coverage ratio is below the required floor.` | ✅ correct |
| 2 | `else` (`:316-342`) | `[!CAUTION] Repository is NOT ready for release — 1 verdict-blocking finding(s).` | ✅ correct **as far as it goes** — but see the row-2 contamination below |
| **4** | `else` (`:316-342`) | `[!CAUTION] Repository is NOT ready for release — deep coverage 2/5 is below the 3/5 release threshold.` | ❌ **DF-8-1-A, reproduced verbatim.** Six lines under `INSUFFICIENT_COVERAGE (Exit Code 3)` |
| **4** (critical only) | `else` | `[!CAUTION] Repository is NOT ready for release — at least one critical subsystem is not audited deep (FR16).` | ❌ same falsehood, different clause |

**Row-2 contamination — a SECOND, previously unnamed defect, measured.** For a row-2 run (1 blocking
finding) over a test-diluted ledger (40 application files all deep + 86 test files shallow → whole-repo
`20/63`), the `reasons` accumulator at `:322-336` appends **gate clauses the amended table never evaluated**:

```
[!CAUTION] Repository is NOT ready for release — 1 verdict-blocking finding(s); deep coverage `20/63`
           is below the `3/5` release threshold.
[!NOTE]    This coverage result is driven by test-file dilution. …
           Note that 1 blocking finding(s) would still block.
```

Post-8.1 the table **short-circuits at row 2**: coverage and the critical clause were *never reached*, so
neither is a reason for this outcome. Calling this *"a coverage result"* is false — it is a **findings**
result. This is squarely inside the epic's *"its independent branches on the verdict enum, deep-ratio
threshold and `blocking_finding_count` (`:62-79`, `:304`) agree with the amended table"* AC. See **AC6**.

**A third measured inconsistency in the same function — `_render_test_dilution_hint:67`.** It classifies
application-vs-test with `is_test_file(e.file_path)` — **name only, no `ast_entry`** — while the pipeline's
own scope narrowing uses `is_test_file(..., ast_entry=…)` (`pipeline.py:692`), whose docstring says in as
many words: *"Without it the two stages could disagree … and a disagreement inside one run is precisely the
kind of inconsistency this tool exists to surface in other people's repositories."* **Measured on this repo
right now: 147 indexed files, exactly ONE disagreement** — `argus/detectors/vacuous_test.py`
(`is_test_file(path) → True`, `is_test_file(path, ast_entry=entry) → False`). So the report's
"APPLICATION files" denominator and the verdict's assessed population genuinely differ by one file on
Argus's own repository. `render_final_verdict_report` **already receives `ast_index`** (`:257`, threaded
from `pipeline.py:797`), so this is fixable without touching `pipeline.py`. See **AC8**.

### The published proof of the DF-8-1-A defect class, already on disk

`_bmad-output/reports/final-verdict.md` (committed) reads:

```
- **Final Verdict**: **`NOT_READY_FOR_RELEASE`** (Exit Code `2`)
- **Blocking Findings**: **0**
> [!CAUTION] Repository is NOT ready for release — deep coverage `11/28` is below the `3/5` release threshold; …
```

A blocking verdict with zero findings, published. ⚠️ **That artifact is Story 8.5's to re-derive (DR-10),
and AC14 fences it.** It is reproduced here only so you understand what the code change prevents from ever
being written again.

### The contracts this story touches — all frozen, all REUSE-not-fork (§3.3 / AR7)

- **`argus/reports/plain_english.py` (186 lines, PURE).** Module docstring locks its role: *"It does not
  change the verdict, the exit code, or the machine summary … A wording layer must never become a second,
  disagreeing source of truth; **every statement here is a restatement of a counter already on the
  verdict**."* That sentence is the whole design brief for this story. It imports **only**
  `argus.verdict.verdict_gate`; keep it that way.
- **`AuditVerdict.is_below_floor` (`verdict_gate.py:380-402`) is THE single source of truth** for the
  row-1-vs-row-4 distinction. Its own docstring: *"THE single source of truth for every consumer that has to
  distinguish 'too little was assessed' (row 1) from 'nothing was found and a gate was not met' (row 4) …
  Re-deriving this from the counters in each consumer would fork the decision table (§3.3)."* **Branch on
  `is_below_floor`. Never on `decision_row` directly** (it is `None` for a pre-amendment payload, and
  `is_below_floor` already carries the correct fallback), and **never** on a re-derived
  `deep_ratio < INSUFFICIENT_COVERAGE_FLOOR` comparison. `generator.py:306` already does this correctly —
  copy that pattern into `plain_english.py`.
- **`Verdict` (3 members) and `DecisionRow` (4 members) do not grow. `AuditVerdict` gains no field.
  `VERDICT_SCHEMA_VERSION` stays `"2"`.** 8.1 bumped it; a second bump in the same epic for a *wording*
  change is not sanctioned and would move every persisted content hash for nothing.
- **`CRITICAL_SUBSYSTEMS_SCHEMA_VERSION` stays `"2"`.** 8.2 bumped it. This story persists nothing new.
- **The stdout machine summary line is FROZEN** — `cli.py::_summary_line` (`:199-224`),
  `verdict=<TOKEN> deep_ratio=<num/den> blocking_findings=<n>` (+ `assessed_deep_ratio`/`scope`/`held_out`
  when narrowed). Story 8.1's **LOCKED channel decision** (epics.md:1440-1457) says the row surfaces on the
  artifact and in stderr prose, and **never** on stdout. `TC-ArgusAgent-CLI-001-30` already pins it; AC9
  extends it. **`argus/cli.py` itself needs no edit** — `render_ship_readiness`'s signature does not change.
- **`render_callout` / `format_locator_link` / `mask_secret` (`reports/formatter.py`) are unchanged.** Use
  the existing `render_callout(level, text)`; do not hand-roll a `> [!X]` block.
- **The two report surfaces are already coupled in the right direction**: `generator.py:22` imports
  `render_depth_meaning, render_ship_readiness` from `plain_english`. `plain_english` is the PURE, lower
  module. **Any shared wording helper this story needs belongs in `plain_english.py`** and is imported by
  `generator.py` — never the reverse, and never duplicated.

### Live consumers — read before you change anything

| Site | What it does | Impact of this story |
|---|---|---|
| `argus/cli.py:292` | prints `render_ship_readiness(verdict, enabled_passes=…)` to **stderr** | ⚠️ **strings change.** Signature unchanged → **no `cli.py` edit** (AC14) |
| `argus/cli.py:279-286` | the **stdout** machine summary line | **must stay byte-identical** — AC9 |
| `argus/reports/generator.py:269` | `"> " + render_ship_readiness(verdict)[0]` — the report headline | ⚠️ inherits the new row-4 wording automatically |
| `argus/reports/generator.py:301` | `render_callout("NOTE", render_depth_meaning(...))` | none — `render_depth_meaning` is out of scope and unchanged |
| `argus/reports/generator.py:304-342` | the verdict-branch block | ⚠️ **the substance — AC5, AC6, AC7** |
| `argus/reports/generator.py:41-100` | `_render_test_dilution_hint` | ⚠️ **AC6 (row-2 suppression) + AC8 (classification)** |
| `argus/reports/generator.py:103-136` | `_render_critical_blockers` | ⚠️ **AC7** (guidance) + empty-set pin |
| `argus/pipeline.py:793` | `generate_reports(request, verdict, ledger, …, source_state=…, ast_index=…)` | **none — do NOT edit (AC14, DF-8-2-A)** |
| `argus/verdict/negative_assurance.py:322-332` | the persisted row-1/row-4 assurance-statement split | **already correct (8.1).** Do not re-litigate; **reuse its wording register** so the two artifacts agree |
| `argus/cost/exhaustion.py` `below_floor` | keys on row 1 (8.1) | none |
| `argus/reports/formatter.py`, `argus/ledger/coverage_report.py` | callout/table rendering, the coverage-ledger report | none expected |

### Tests that assert the strings this story changes — the complete measured work list

Grepped and read on this tree. **Every one of these is legitimate to update here** — unlike Story 8.1,
whose AC15 explicitly fenced rendered strings. But *update* means **re-point to the true state and keep or
strengthen the subject assertion**; it never means delete, skip, weaken, or assert less.

| # | Test | Today | Disposition |
|---|---|---|---|
| 1 | `test_plain_english.py::test_zero_finding_block_does_not_read_as_a_defect_claim` | builds `NOT_READY_FOR_RELEASE` + `blocking=0` **by hand** (bypasses the gate) and asserts `"NOT VOUCHED" in headline` | **RE-POINT** to a real row-4 `INSUFFICIENT_COVERAGE` fold — this is the epic's explicit AC3 instruction. **Keep its subject**: "a zero-finding outcome must not read as a defect claim". The hand-built impossible verdict moves to the AC2 contract-violation test |
| 2 | `test_plain_english.py::test_insufficient_coverage_reads_as_not_assessed_never_as_a_defect` | `INSUFFICIENT_COVERAGE`, `decision_row=None` → `is_below_floor` falls back True → row-1 headline. **Stays green unchanged** | **SPLIT** into an explicit row-1 case and a row-4 case (AC3/AC4). Keep a `decision_row=None` case as the pre-amendment-payload regression pin |
| 3 | `test_plain_english.py::test_real_blocking_findings_do_read_as_a_defect_claim` | asserts `"BLOCKED"` + `"3 verdict-blocking finding(s)"` + `"NOT VOUCHED" not in headline` | **Stays green.** Strengthen with the AC1 `N ≥ 1` sweep |
| 4 | `test_plain_english.py` — the other 7 tests (`release_ready`, `counts_restate`, `scoped_verdict`, `scope_suggestion`, `next_step_critical`, 3× `depth_meaning`, `deterministic_no_host_path`) | body/counter/determinism pins | **Must stay green unmodified.** If one breaks you changed a counter line you were not asked to change |
| 5 | `test_report_honesty.py::test_critical_block_names_the_gate_and_the_files` (`-002-01`) | **row 4**; asserts `"critical subsystem is not audited deep" in text`, `"due to blocking findings" not in text`, names the files | **Stays green** if the row-4 detail keeps the clause phrase. **Do not drop the phrase** |
| 6 | `test_report_honesty.py::test_designated_critical_absent_from_ledger_is_labelled` (`-002-02`) | row 4; `"never examined"` | **Stays green** |
| 7 | `test_report_honesty.py::test_blocking_findings_are_named_when_they_are_the_cause` (`-002-03`) | **row 2**, 3/3 deep; `"1 verdict-blocking finding(s)"` | **Stays green.** Extend for AC6 with a *diluted* row-2 ledger asserting the coverage clause is **absent** |
| 8 | `test_report_honesty.py::test_dilution_hint_does_not_over_promise_when_another_gate_blocks` (`-002-05`) | row 4; asserts the literal `"Note that the critical-subsystem clause would still block"` | ⚠️ **WILL BREAK** if you correct "block" → "withhold `RELEASE_READY`" (row 4 does not block). **RE-POINT the string, keep the subject** (the hint must not over-promise) |
| 9 | `test_report_honesty.py::test_dilution_hint_appears_and_quantifies_the_gap` (`-002-04`) | row 4; `"40/40"`, `"86 test file(s)"`, `"No other gate is currently unmet."` | **Stays green** unless you reword the caveat; if you do, re-point |
| 10 | `test_report_honesty.py::test_no_dilution_hint_when_narrowing_would_not_help` / `…once_already_scoped` / `…release_ready_report_has_no_block_explanation` / `…ratio_shown_is_the_one_the_gate_used` (`-002-06/07/08/09`) | negative + scope pins | **Must stay green unmodified** |
| 11 | `test_report_generator.py::test_render_final_verdict_report`, `::test_generate_reports` | RELEASE_READY + smoke | **Stay green unmodified** |
| 12 | `test_critical_eligibility_pipeline.py::…PIPELINE_002_07_no_surface_claims_all_criticals_examined_deeply` | runs `_assert_makes_no_positive_critical_claim` over the **rendered report** AND `render_ship_readiness` output | ⚠️ **KEYSTONE — must stay green.** Banned substrings (case-insensitive): `"all critical"`, `"every critical"`, `"all criticals"`, `"criticals examined"`, `"critical subsystems examined deeply"`, `"critical subsystems were examined"`. **Your new prose must avoid every one of them** |
| 13 | `test_cli.py::test_cli_summary_line_does_not_carry_the_decision_row` (`CLI-001-30`) | pins the exact stdout line for a row-2 cartridge | **Must stay green unmodified.** AC9 **adds** a case, it does not edit this one |
| 14 | `test_critical_eligibility_pipeline.py:535` | `render_ship_readiness(result.verdict)` on a vacuously-satisfied row-3 run | **Stays green** — row 3 wording is unchanged |

**No test outside these files should change.** If a fifteenth test goes red, it is telling you something —
read it before you touch it.

### Known-red carve-out — inherited/deferred, user-adjudicated, DO NOT touch

Re-measured in place immediately before this story was written:

```
PYTHONIOENCODING=utf-8 python -m pytest tests/     →  3 failed, 1108 passed in 211.76s
                                                       (1111 collected, 0 skipped)
python -m mypy argus                               →  Success: no issues found in 69 source files
```

```
FAILED tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation
FAILED tests/test_dogfood_plan.py::test_budget_reuses_the_31_accountant_no_fork
FAILED tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run
```

1–2 are **inherited** (red at `9109e16` too; confirmed by the 8.1 reviewer in a clean detached worktree).
3 is **deliberate** — a rot check on `minions-dogfood-proof.md`, which is **Story 8.5 / DR-10**'s deliverable;
the epic sequences 8.5 last *by design, so a slip stays visible*. Its current message is
`assert '`RELEASE_READY` (exit `0`)' in <the stale committed markdown>` — i.e. it already reflects 8.2's
honest outcome. **Leave all three red and unmodified. Do not touch `minions-dogfood-proof.md`.**

**Do not absorb these into this story's result.** Record their exact state verbatim in the Dev Agent Record.
**Any fourth red is yours.**

---

## Acceptance Criteria

> The epic's six ACs for Story 8.3 are carried in full as **AC1–AC5, AC9**. **AC6, AC7, AC8, AC10–AC15** are
> **additions made at story design after measuring the change against the real tree** — each one is
> justified in *Variance from the epic, recorded*.

**The human register (`argus/reports/plain_english.py`) — DR-11 half 1**

1. **Given** a `NOT_READY_FOR_RELEASE` verdict,
   **When** it is rendered by `render_ship_readiness`,
   **Then** the headline reads `BLOCKED — N verdict-blocking finding(s) …` with **N ≥ 1 ALWAYS**,
   **And** the invariant is proven, not asserted: a committed test sweeps **every**
   `(total 0..8) × (deep 0..total) × (findings 0,1,2) × (criticals True/False)` combination through the real
   `evaluate_verdict` and shows that no fold produces `NOT_READY_FOR_RELEASE` with
   `blocking_finding_count == 0` (the SM measured 270 folds → 0 occurrences; re-derive it),
   **And** the row-2 headline string is otherwise **unchanged**.

2. **Given** `argus/reports/plain_english.py::_headline`,
   **When** its branches are audited,
   **Then** the trailing `NOT VOUCHED` else-branch — which fires **only** on the unreachable
   `NOT_READY_FOR_RELEASE ∧ blocking == 0` state — is **removed as unreachable**, per **D2**: its *prose*
   relocates to FR16 row 4, where it is true and reachable, and its *predicate* is deleted,
   **And** the resulting `_headline` is a **total function with no untested branch** — every remaining branch
   is demonstrated reachable from a real `evaluate_verdict` fold by a committed test (DR-11's actual
   requirement: *"either delete it or prove it still reachable … not left as untested dead code"*),
   **And** the now-impossible input state cannot silently render the original bug string
   `BLOCKED — 0 verdict-blocking finding(s)`: a hand-constructed contract-violating `AuditVerdict` raises a
   **typed `ValueError` subclass** defined in this module (the `exit_code_for_verdict` /
   `NegativeAssuranceError` / `CriticalSubsystemError` house pattern — *never a silent default*), pinned by a
   test that constructs exactly that verdict,
   **And** the CLI degrades honestly on it (`cli.py:272` already catches `ValueError` → exit `1`, AR10) —
   assert that, do not assume it.

3. **Given** `tests/test_plain_english.py`,
   **When** the suite runs,
   **Then** **no test asserts a state the amended gate cannot produce**; the case pinning the
   zero-finding/blocking split (`test_zero_finding_block_does_not_read_as_a_defect_claim`) is **re-pointed to
   a real row-4 `INSUFFICIENT_COVERAGE` fold** while keeping its original subject assertion — a zero-finding
   outcome must not read as a defect claim,
   **And** every re-pointed test asserts something strictly **more** specific than before (the standing
   Epic-8 rule: a re-point keeps its subject and gains precision; it never asserts less),
   **And** no test in this file is deleted, skipped or weakened.

4. **Given** two `INSUFFICIENT_COVERAGE` verdicts — one from **row 1** (below the floor) and one from
   **row 4** (a gate unmet, nothing found) — both carrying exit `3` and the same enum,
   **When** each is rendered for a human,
   **Then** they read **differently and truthfully**: row 1 ≈ *"I examined too little to say anything"*;
   row 4 ≈ *"I examined plenty and found nothing, but a coverage or critical-subsystem gate was not met"*
   (boundary **B4** — the human register is the **only** surface on which an operator can tell which action
   is called for),
   **And** the row-4 wording covers **both** its causes: it must be true of the measured 5/5-deep,
   zero-findings, critical-clause-unmet run, so it may **not** mention coverage alone (today's else-branch
   text says *"a coverage gate"* — widen it),
   **And** the split is driven by **`AuditVerdict.is_below_floor`** — never by `decision_row` directly and
   never by a re-derived ratio comparison (§3.3 no-fork; `is_below_floor` carries the pre-amendment
   `decision_row is None` fallback, and a `decision_row=None` verdict is pinned to still render the row-1
   text),
   **And** the row-1 headline string is **byte-identical to today's**.

**The persisted report (`argus/reports/generator.py`) — DR-11 half 2, and DF-8-1-A**

5. **Given** a **row-4** run (`INSUFFICIENT_COVERAGE`, exit `3`, zero blocking findings, a coverage or
   critical-subsystem gate unmet),
   **When** `render_final_verdict_report` renders it,
   **Then** the document contains **no sentence asserting that the repository is not ready for release** —
   the measured `> [!CAUTION] Repository is NOT ready for release — deep coverage 2/5 is below the 3/5
   release threshold.` six lines under `- **Final Verdict**: **INSUFFICIENT_COVERAGE** (Exit Code 3)` is
   **gone** (this closes **DF-8-1-A**),
   **And** what replaces it is true of row 4, states that **nothing blocking was found**, names the gate(s)
   that actually were unmet, and says plainly that this is a statement about the **audit**, not about the
   **code** — the same register `negative_assurance._assurance_statement` already uses for row 4 on the
   persisted artifact, so the two artifacts of one run agree,
   **And** it is demonstrated **RED-first**: a committed test that fails against the current implementation
   before the fix, with the observed RED output captured **verbatim** in the Dev Agent Record,
   **And** `render_ship_readiness(verdict)[0]` — the quoted report headline at `:269` — carries the AC4
   row-4 wording, so the head of the document and its callout no longer disagree.

6. **Given** a **row-2** run (`NOT_READY_FOR_RELEASE`, ≥1 blocking finding),
   **When** it is rendered,
   **Then** the report names **only the finding(s)** as the reason. The coverage-threshold clause and the
   critical-subsystem clause are **NOT appended** — the amended table short-circuits at row 2 and never
   evaluated them, so presenting them as reasons is a false causal claim (measured: a diluted row-2 run
   today prints *"1 verdict-blocking finding(s); deep coverage `20/63` is below the `3/5` release
   threshold"*),
   **And** `_render_test_dilution_hint` emits **nothing** for a row-2 run — *"This coverage result is driven
   by test-file dilution"* is false when the result was driven by a finding,
   **And** — critically — the suppression must **not trade one dead branch for another**: once row 2 is
   suppressed, the `if verdict.blocking_finding_count > 0: remaining.append(…)` clause inside
   `_render_test_dilution_hint` (`:78-79`) becomes unreachable, and once row 4 owns the `else` arm the
   `detail = … if reasons else "a release gate was not satisfied"` fallback at `:336` becomes unreachable
   too (row 4 fires *because* a gate is unmet, so `reasons` is never empty). **Each must be removed or
   proven reachable.** Apply DR-11's own rule to every branch this story makes unreachable, and record the
   branch-by-branch analysis in the Dev Agent Record,
   **And** the row-2 callout text is otherwise **unchanged** (`Repository is NOT ready for release —
   N verdict-blocking finding(s).` is correct and must survive).

7. **Given** Story 8.2's eligibility filter,
   **When** `_render_critical_blockers` renders,
   **Then** for an **empty** `critical_subsystems_not_deep` it renders **nothing** and the surrounding
   document makes **no** critical-subsystem claim of any kind — pinned by a test (a row-4 run blocked on
   coverage **only**, and the 8.2 `_VACUOUSLY_SATISFIED` fixture whose whole critical set the filter empties),
   **And** its *"Each must reach `audited_deep`, or be removed from the critical set with
   `--exclude-critical` if it is not genuinely critical"* guidance (`:122-123`) is corrected: files Argus can
   never grade `audited_deep` (test files, clean-parsed zero-definition modules) are **already removed
   automatically** by FR4/DR-5, so every listed row is a real work item — and the guidance states the one
   exception, that an operator's own `--critical-subsystem` designation is **exempt** from that removal
   (DR-6) and can therefore appear here while being ungradable,
   **And** the new prose contains **none** of the `_FALSE_POSITIVE_CLAIMS` substrings
   (`"all critical"`, `"every critical"`, `"all criticals"`, `"criticals examined"`,
   `"critical subsystems examined deeply"`, `"critical subsystems were examined"`) — verified by keeping
   `TC-ArgusAgent-PIPELINE-002-07` green.

8. **Given** `_render_test_dilution_hint` splits application from test files at `:67`,
   **When** it classifies,
   **Then** it uses the **same** content-disambiguated call the pipeline uses —
   `is_test_file(path, ast_entry=…)` — sourced from the `ast_index` **already passed into**
   `render_final_verdict_report` (`:257`) and `generate_reports` (`:465`); it does **not** add a parameter to
   either public signature, does **not** touch `argus/pipeline.py`, and does **not** write a second
   classification predicate (§3.3 / AR7),
   **And** when `ast_index is None` (the existing unit-test callers) behaviour is **unchanged**,
   **And** the measured disagreement is pinned: on this repository exactly one of 147 indexed files —
   `argus/detectors/vacuous_test.py` — is classified `True` by name and `False` with its AST entry;
   a test proves the report's application/test split and the verdict's assessed population now agree on it.

**Wire contract, determinism and secret-safety**

9. **Given** any run,
   **When** the machine summary line is emitted to **stdout**,
   **Then** it is **byte-identical to the pre-amendment format** —
   `verdict=<TOKEN> deep_ratio=<num/den> blocking_findings=<n>` (+ `assessed_deep_ratio`/`scope`/`held_out`
   when narrowed) — carrying **no** decision-row field and **no** prose, per Story 8.1's LOCKED channel
   decision,
   **And** the existing golden `TC-ArgusAgent-CLI-001-30` stays green **unmodified**, and a **new** golden
   case pins the line for a **non-row-2** verdict (an `INSUFFICIENT_COVERAGE` cartridge run), so a story that
   rewrites the human register cannot leak a single character onto the wire surface,
   **And** a test asserts the two registers do not cross streams: the reworded human block appears on
   **stderr** only, and stdout contains exactly one line and it starts with `verdict=`.

10. **Given** both report surfaces,
    **When** rendered twice over the same inputs,
    **Then** they are **byte-identical** (PURE — no clock, no `uuid`/`random`, no set/dict iteration-order
    reliance, no `float`),
    **And** neither emits an absolute host path, a source byte or a secret byte (NFR-S1),
    **And** `plain_english`'s existing pin (`test_rendering_is_deterministic_and_leaks_no_host_path`) stays
    green **unmodified**, while an **equivalent pin is ADDED for `render_final_verdict_report`** — measured
    gap: no determinism / secret-safety test exists for the generator surface today,
    **And** `argus/reports/plain_english.py` still imports **only** `argus.verdict.verdict_gate`, and
    `argus/reports/generator.py` gains **no new import** beyond what it already has.

11. **Given** the epic's *"an operator can tell which action is called for"* purpose (boundary B4),
    **When** all four rows are rendered through **both** surfaces,
    **Then** a single committed test renders **one real fold per FR16 row** through
    `render_ship_readiness` **and** `render_final_verdict_report` and asserts, for each, that the rendered
    text is **consistent with the verdict and exit code printed in the same document** — specifically that
    no `INSUFFICIENT_COVERAGE` document contains a not-ready-for-release assertion and no `RELEASE_READY`
    document contains a block explanation. This is the story's end-to-end anti-regression net: it is the
    single test that would have caught DF-8-1-A.

**Whole-system and fences**

12. **Given** the delta has landed,
    **When** the full suite runs (`PYTHONIOENCODING=utf-8 python -m pytest tests/ -q`),
    **Then** the **only** reds are the three-test adjudicated carve-out (2 inherited `test_dogfood_plan` +
    1 deliberate `test_dogfood_proof` owned by Story 8.5), **no test is deleted, skipped, weakened or
    re-pointed to assert less**, the collected count does **not fall below 1111**, `python -m mypy argus` is
    clean (69 files), and **no source file exceeds 1200 lines** (NFR-M1).

13. **Given** the repository's own audit,
    **When** `argus audit .` is run end-to-end after the delta,
    **Then** its verdict / exit code / decision row / deep ratio / blocking count are **RECORDED verbatim**
    in the Dev Agent Record together with the stderr human block it printed, **and nothing is adjusted to
    make it a particular value** (boundary B1 — pinning a predetermined verdict on an assurance tool's own
    output invites the story to be *made to pass*). 8.2 recorded `RELEASE_READY` / exit `0` /
    `row_3_gates_met` / assessed `57/73` / 0 blocking / 50 critical paths; whatever this run says, record it.

14. **Given** the epic's story boundaries and the two open deferred items,
    **Then** this story does **NOT** modify: `argus/pipeline.py` (**DF-8-2-A** — 1199/1200 lines; the
    extraction belongs to the next story that genuinely edits it), `argus/detectors/vacuous_test.py`
    (**DF-8-2-B**), `argus/verdict/verdict_gate.py`, `argus/verdict/prosecutor.py`,
    `argus/verdict/negative_assurance.py`, `argus/cost/exhaustion.py`,
    `argus/ledger/critical_subsystems.py`, `argus/cli.py`, `argus/__init__.py` (**Story 8.4** / RS-4a),
    `argus/dogfood/*`, `tests/cartridges/_registry.py`, `tests/fixtures/*`,
    `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md`,
    `_bmad-output/reports/final-verdict.md`, `_bmad-output/audit-reports/final-verdict.md` (**Story 8.5** /
    DR-10), `action.yml`, `.github/workflows/argus-student-audit.yml` (the user's, Epic 9).
    **Verified by `git diff` → empty for each path**, reported per path in the Dev Agent Record.
    No new cartridge is added to `CARTRIDGE_REGISTRY`.

15. **Given** the deferred-work ledger,
    **Then** (a) **DF-8-1-A is closed** by this story, with the closing evidence named (the RED-first test id
    and the resulting text); (b) **DF-8-2-A is carried forward, not closed** — an **append-only** one-line
    note records that Story 8.3 did not edit `pipeline.py`, so the file stays at 1199 lines and the
    extraction remains owed by the next story that does (the original entry is **not rewritten** — §3.4
    evidence immutability); (c) **DF-8-2-B is carried forward untouched** with a one-line append recording
    that 8.3 did not edit `argus/detectors/vacuous_test.py`; (d) if you conclude that naming the *vacuously
    satisfied* critical gate in human prose requires threading the `CriticalSubsystemSet` through
    `pipeline.py` (see **D5**), file it as a **new** entry with the six mandatory CC-3 fields
    (`id`, `origin_story`, `owner`, `target_story`, `category`, `severity` — copy the shape from
    `deferred-work.md:513-518`) targeted at the story that performs the DF-8-2-A extraction.

---

## Tasks / Subtasks

- [x] **Task 1 — RED first (AC1, AC2, AC5, AC6).** *Do not flip the story to `review` before these exist*
      (process watch-item AI-E2-1 from the Epic-2 retrospective).
  - [x] Write the failing test for the **row-4 plain-English headline** (a real `evaluate_verdict` fold at
        2/5 deep, 0 findings, and a second at 5/5 deep with the critical clause unmet) asserting it does
        **not** claim too little was examined. Run it; capture the RED output **verbatim**.
  - [x] Write the failing test for the **row-4 `final-verdict.md` self-contradiction** (DF-8-1-A): the
        document must not contain a not-ready-for-release assertion. Capture the RED output verbatim.
  - [x] Write the failing test for the **row-2 contamination** (AC6): a diluted row-2 fold's report must not
        name the coverage threshold as a reason, and must emit no dilution NOTE.
  - [x] Write the **reachability sweep** (AC1/AC2) and record the measured triple counts.

- [x] **Task 2 — Reconcile the human register (AC1–AC4).** `argus/reports/plain_english.py`
  - [x] Restructure `_headline` to branch: `RELEASE_READY` → `INSUFFICIENT_COVERAGE` **split on
        `verdict.is_below_floor`** (row 1 / row 4) → `NOT_READY_FOR_RELEASE`. Delete the unreachable
        `NOT_READY ∧ blocking == 0` predicate.
  - [x] Relocate the `NOT VOUCHED` prose to the row-4 branch and **widen** *"a coverage gate"* →
        *"a coverage or critical-subsystem gate"* (measured: row 4 fires at 5/5 deep on the critical clause
        alone). Keep the rows 1/2/3 strings **byte-identical**.
  - [x] Add the typed error class (a `ValueError` subclass, export it in `__all__`) raised on the
        contract-violating `NOT_READY ∧ blocking == 0` input — with a docstring saying exactly why the state
        is impossible and citing FR16 row 2. Never a silent default.
  - [x] Update the module docstring: the four-row mapping it now renders, and the `is_below_floor` /
        no-fork rule. Do **not** add an import.
  - [x] Consider whether the row-4 message should also carry the AC7 "which gate" naming; if you extract a
        shared helper for that, it lives **here** (PURE, lower module) and `generator.py` imports it — never
        the reverse, never duplicated. → **Considered and DECLINED — no duplication exists** (see the
        deviation note in Completion Notes). The headline names the gate CLASS ("a coverage or
        critical-subsystem gate"); only `generator.py` names the specific unmet gate with its ratio, and it
        does so once. Extracting a helper used by exactly one caller would add indirection without removing
        a fork (KISS/YAGNI). If a second consumer ever needs that sentence, it belongs in `plain_english.py`.

- [x] **Task 3 — Reconcile the persisted report (AC5, AC6, AC7).** `argus/reports/generator.py`
  - [x] Split the `else` at `:316` into a **row-2** arm and a **row-4** arm, keyed on
        `verdict.blocking_finding_count` (row 1 is already handled by `elif verdict.is_below_floor` and row 3
        by the `RELEASE_READY` arm — the four arms are then exactly the four FR16 rows).
  - [x] Row 2: keep `CAUTION` + `Repository is NOT ready for release — N verdict-blocking finding(s).`
        **Drop the coverage and critical clauses from its reason list.** Emit **no** dilution hint.
  - [x] Row 4: replace the `CAUTION`/not-ready sentence with wording true of row 4 — nothing blocking found,
        the named unmet gate(s), and the audit-not-the-code statement. Keep the critical-clause phrase
        `"critical subsystem is not audited deep"` so `TC-ArgusAgent-REPORT-002-01` stays green. Keep the
        dilution hint and `_render_critical_blockers` on this arm.
  - [x] `_render_test_dilution_hint`: remove or prove-reachable the now-dead
        `blocking_finding_count > 0` clause (AC6); re-word the `caveat` so a row-4 outcome is described as
        **withholding `RELEASE_READY`**, not as blocking. Audit the two early-return guards at `:62-65` the
        same way and record the finding. → see the **branch-by-branch dead-code audit** in Completion Notes.
  - [x] `_render_critical_blockers`: rewrite the `:122-123` guidance per AC7, including the DR-6 exemption
        sentence. Check every new sentence against the six `_FALSE_POSITIVE_CLAIMS` substrings.
  - [x] Do **not** change `render_depth_meaning`, `_render_readability_warning`, `_render_source_state`, the
        counter lines at `:272-293`, or the Negative-Assurance block.

- [x] **Task 4 — Classification consistency (AC8).** `argus/reports/generator.py`
  - [x] Thread the `ast_index` already present in `render_final_verdict_report` into
        `_render_test_dilution_hint` and call `is_test_file(path, ast_entry=…)`, mirroring
        `pipeline.py:692`. **No public signature change. No `pipeline.py` edit. No second predicate.**
  - [x] Preserve `ast_index=None` behaviour exactly (the existing unit-test callers pass nothing).
  - [x] Pin the measured one-file disagreement (`argus/detectors/vacuous_test.py`).

- [x] **Task 5 — Tests: re-point, extend, and add the net (AC3, AC9, AC10, AC11).**
  - [x] `tests/test_plain_english.py`: re-point per the work-list table; add the reachability sweep, the
        row-1/row-4 split, the `decision_row=None` regression pin and the typed-error pin. Continue
        `TC-ArgusAgent-REPORT-002-NN` from **-10** (currently to -09).
  - [x] `tests/test_report_honesty.py`: re-point `-002-05`'s literal; extend `-002-03` with the diluted
        row-2 case; add the empty-critical-set pin.
  - [x] Add the **AC11 four-row cross-surface consistency net** and the **AC10 generator determinism +
        secret-safety pin** (new — measured gap). → in the NEW module
        `tests/test_report_surface_consistency.py` (stated choice; see Completion Notes).
  - [x] `tests/test_cli.py`: add `TC-ArgusAgent-CLI-001-31` — a non-row-2 cartridge run pinning the exact
        stdout line **and** that the human block went to stderr. **Do not edit `-30`.**
  - [x] Non-ASCII adversarial coverage (standing requirement AI-E1-1 since Epic 1's only review FAIL): this
        story renders paths into a Markdown table, so include a non-ASCII critical path in the
        `_render_critical_blockers` pin rather than declaring it discharged.

- [x] **Task 6 — Measure, record, fence (AC12, AC13, AC14, AC15).**
  - [x] Re-derive the SM's figures on the **real tree**: the 270-fold sweep, the 4×2 rendered-row table, the
        147-file / one-disagreement classification measurement. **Do not trust this story's numbers.**
  - [x] Run `argus audit .` end-to-end; record verdict / exit / row / ratio / blocking count and the stderr
        block **verbatim**. Adjust nothing.
  - [x] Full suite + `mypy`; record counts and the three carve-out reds verbatim.
  - [x] `git diff` over **every** AC14 path → confirm empty, report per path.
  - [x] Ledger work per AC15: close DF-8-1-A; **append-only** carry-forward notes on DF-8-2-A and DF-8-2-B;
        file the new entry if D5's conclusion holds. → **DF-8-3-A filed** (D5's conclusion held).

### Review Findings

> **code-review 2026-08-06, iteration 1 — VERDICT: FAIL** (one Medium regression). Everything below was
> re-derived by the reviewer against the working tree; nothing was taken from the Dev Agent Record on trust.
>
> **What was independently VERIFIED and is confirmed good** (recorded so the next dev round does not
> re-litigate it):
> - **DF-8-1-A is genuinely CLOSED, both halves.** The reviewer rebuilt the pre-8.3 implementation of BOTH
>   surfaces and injected it at runtime (`plain_english._headline` rebound; `render_final_verdict_report`
>   re-compiled with the historic three-arm block). Against that historic code, `-002-20`'s assertions fail
>   for **both** row-4 causes — at 2/5 deep (`[!CAUTION] Repository is NOT ready for release — deep coverage
>   `2/5` is below the `3/5` release threshold.`) and at **5/5 deep / `deep_ratio == 1`** (`… — at least one
>   critical subsystem is not audited deep (FR16).`), with the headline rendering row 1's *"too little of the
>   code was examined deeply"* in both. The closing test is a real regression test, not a rubber stamp.
> - **The `NOT VOUCHED` predicate deletion is SAFE, re-derived independently of the SM's sweep.** Not by
>   re-running the 270 folds but STRUCTURALLY: `AuditVerdict` has exactly **one** construction site in
>   `argus/` (`verdict_gate.py:651`), inside `evaluate_verdict`, where `Verdict.NOT_READY_FOR_RELEASE` is set
>   only in the `elif blocking >= 1` arm and `blocking_finding_count=blocking` is the same value. No
>   `AuditVerdict.model_validate` and no read-back of a persisted verdict exists anywhere (`store/reader.py`
>   rehydrates only `CoverageLedger`/`Recording`; the resume path re-folds), so on-disk v1 state cannot reach
>   the renderer. The prosecutor's second path — `prosecutor.py:494` `verdict.model_copy(update={...})` —
>   updates **only** `ordered_findings`, so it preserves the candidate's `NOT_READY ⟹ blocking ≥ 1`; the
>   other arm returns a real `evaluate_verdict` result. Budget-exhaustion / degraded / escalation code only
>   READS a verdict. **No reachable path now raises `ShipReadinessError` where the old code rendered prose.**
> - **Rows 1/2/3 headlines are BYTE-IDENTICAL**, proven by differential render (historic vs current):
>   row 1 `NOT ASSESSED — …`, row 2 `BLOCKED — 1 verdict-blocking finding(s) must be resolved.`, row 3
>   `READY — …` all compare equal; only row 4 changed, to prose true of both its causes.
> - **Row 2 is clean**: a diluted (`20/63`) row-2 render names only `1 verdict-blocking finding(s).` — no
>   coverage clause, no critical clause, no dilution NOTE. No `_FALSE_POSITIVE_CLAIMS` substring in any new
>   prose (checked on both new documents).
> - **AC14 fence held.** `argus/pipeline.py` = 1199 lines, md5 `399d6da1d36d668352fd7b0d539cc307`;
>   `argus/cli.py` and `argus/__init__.py` empty-diff vs `9109e16`; `argus/detectors/vacuous_test.py` md5
>   `8a0705030391df92ad1404af9d044758` with DF-8-2-B's unseparated `"test.java"`/`"spec.rb"` still present
>   (so DF-8-2-B was NOT pulled in); `minions-dogfood-proof.md` and both `final-verdict.md` artifacts
>   empty-diff — the DR-10 artifact was NOT re-derived and `test_dogfood_proof.py` was not modified (its red
>   still asserts the full ``'`RELEASE_READY` (exit `0`)'`` string — the check is not weakened). D5's
>   exclusion respected; DF-8-3-A filed with all six CC-3 fields. DF-8-2-A not re-litigated.
> - **`tests/test_report_surface_consistency.py` is STAGED (`A`)** and not ignored.
> - **No new dead code.** Every surviving guard in `_render_test_dilution_hint`, all four generator arms and
>   all five `_headline` paths verified reachable; the four removed branches are genuinely gone.
> - **Reviewer's own runs.** `PYTHONIOENCODING=utf-8 python -m pytest tests/ -q` → **1126 collected /
>   1123 passed / 3 failed / 0 skipped** (progress map contains no `s`), the 3 reds being exactly the
>   adjudicated carve-out; `python -m mypy argus` → clean, 69 files; no `argus/` file over 1200 lines;
>   live `argus audit .` → `verdict=RELEASE_READY deep_ratio=57/148 blocking_findings=0
>   assessed_deep_ratio=57/73 scope=application held_out=75`, exit `0` — identical to the Dev record.
> - **Test re-points reviewed one by one** in `test_plain_english.py`, `test_report_honesty.py`,
>   `test_cli.py`: every re-point keeps its subject and asserts something strictly more specific
>   (`"coverage gate"` → `"coverage or critical-subsystem gate was not met"`; `"would still block"` →
>   `"would still withhold \`RELEASE_READY\`"` **plus** a new `"would still block" not in text`; the row-1
>   literal newly pinned byte-exact as `_ROW_1_HEADLINE`). **Nothing asserts less than before.**

- [x] **[Review][Patch] R1 (Medium) — the arm split silently dropped the critical-subsystem work list from
      FR16 row 2, and `plain_english` still points the operator at it** `[argus/reports/generator.py:350-364]`
      *(also `argus/reports/plain_english.py:250-254`)*.
      Before this story `_render_critical_blockers` lived in the `else` arm, which covered rows 2 **and** 4;
      the four-arm split left it on row 4 only. **Reproduced by the reviewer both ways** on a row-2 fold
      (3/5 deep, 1 AST finding, `critical_subsystems_not_deep=("src/auth.py","src/pay.py")`):
      the historic renderer emits `### Critical subsystems below \`audited_deep\` (2)` and names both files;
      the current renderer emits **no occurrence of the word "critical" anywhere in the document**. Yet
      `render_ship_readiness` for that same run still prints
      `- Critical files not examined deeply: 2` and
      `Next: see the final-verdict report for the named critical files and their actual depth; \`--exclude-critical <path>\` removes one that is not genuinely critical`.
      **Violates:** DR-11 / boundary B4 — one run's two human surfaces must not disagree; this is the same
      defect class Story 8.1's AC block already had to fix once (*"generator.py drops the critical-blockers
      block"*). It is also an unrecorded behaviour change: no AC asked for this removal (AC6 forbids the
      coverage/critical **reason clauses** and the dilution NOTE on row 2, not the work list), and the
      story's own branch-by-branch audit — which AC6 required for every branch this delta touched — does not
      mention it. AC11's cross-surface net (`-002-21`) does not catch it because it only checks
      block-assertion consistency, never that a `Next:` pointer resolves.
      **Suggested fix (a design choice, pick one and record it):** either (i) call
      `_render_critical_blockers` from the row-2 arm as well, with a row-aware lead — its current sentence
      *"These withheld `RELEASE_READY` (FR16)."* is itself false for row 2, where the finding is the whole
      reason, so it needs a non-causal variant such as *"Not the reason for this verdict — the finding(s)
      above are. Listed so the gate is actionable once they are resolved."*; or (ii) make
      `plain_english`'s `--exclude-critical` `Next:` line conditional so it never points at a section the
      document will not contain. **Either way, extend `TC-ArgusAgent-REPORT-002-21` to assert that every
      `Next:` pointer emitted by `render_ship_readiness` resolves inside the same run's rendered document**
      — that is the generalisation of the net this story is supposed to leave behind.

- [x] **[Review][Patch] R2 (Low) — duplicate test id `TC-ArgusAgent-REPORT-002-17`**
      `[tests/test_report_honesty.py::test_TC_ArgusAgent_REPORT_002_17_row_2_names_only_the_findings]` and
      `[tests/test_plain_english.py::test_TC_ArgusAgent_REPORT_002_17_row_1_and_row_4_both_read_as_not_a_defect]`.
      Both files declare verification area `TC-ArgusAgent-REPORT-002-NN`; `test_plain_english.py` used
      `-002-10`…`-002-17` and `test_report_honesty.py` restarted at `-002-17`. **Violates** the project's
      `TC-<AREA>-<SEQ>-<SUBSEQ>` uniqueness convention (architecture.md, *Naming & Structure Patterns*) and
      this story's own instruction to *"continue from -10 … Do not restart a sequence"*. It also makes the
      Dev Agent Record's AC map ambiguous (AC4 → `-002-17` **and** AC6 → `-002-17`).
      **Fix:** renumber the `test_report_honesty.py` case to `-002-24` (the honesty file's `-18`/`-19` may
      stay, or shift to `-25`/`-26` if you prefer one contiguous block), and update the AC-by-AC map in the
      Dev Agent Record and the `deferred-work.md` DF-8-1-A closure note if it names the id.

- [x] **[Review][Defer] R3 (Low) — `render_ship_readiness`'s new raise site sits OUTSIDE the CLI's
      `except ValueError`** `[argus/cli.py:271-292]` — deferred, `cli.py` is on the AC14 fence and the state
      is unreachable. `cli.py` wraps only `run_audit(request)`; `render_ship_readiness(verdict, …)` is called
      **after** the `try`, so a `ShipReadinessError` raised there would escape as an uncaught traceback, not
      the AR10/NFR-R1 typed exit `1`. In practice it is masked whenever `--report-dir` is set (the pipeline
      calls `generate_reports` → `render_ship_readiness` inside `run_audit` first), but `report_dir` defaults
      to empty, so the default invocation has no guard. `TC-ArgusAgent-CLI-001-32` monkeypatches
      `cli.run_audit` itself and therefore proves AC2's *letter* (`cli.py:272` degrades a `ValueError`)
      without ever exercising the real raise site. Harmless today — the state has no producer (see the
      structural proof above) — so filed as **DF-8-3-B**, not fixed here.

- [x] **[Review][Defer] R4 (Low) — the ast-index → application/test split is now written twice**
      `[argus/reports/generator.py:86-93]` vs `[argus/pipeline.py:686-694]` — deferred, both files are
      AC14-fenced this story. AC8 is satisfied in the way that matters: the **predicate** is reused
      (`is_test_file(path, ast_entry=…)`), no second classifier was written, and the reviewer confirmed the
      two call sites agree. But the *plumbing* around it — build `{entry.file_path: entry}` from
      `ast_index.entries`, then filter `ledger.entries` through the predicate — is now duplicated verbatim
      and can drift (e.g. the generator uses `getattr(ast_index, "entries", ()) or ()` while the pipeline
      uses `index.entries if index is not None else {}`). **DRY / AR7:** the natural home is one helper
      beside `is_test_file` in `argus/detectors/vacuous_test.py`. Filed as **DF-8-3-C**.

> **code-review 2026-08-06, iteration 2 — VERDICT: PASS.** Scoped to the delta plus the regression sweep.
> Every claim below was re-derived by the reviewer on this working tree; nothing was taken from the Dev
> Agent Record on trust. The reviewer touched no source, no test and no ledger.
>
> **R1 (Med) — CLOSED, and the disposition landed as described.**
> - **The RED claim is REAL, verified by runtime injection** (the Story-8.2 technique): the round-1
>   implementation was reconstructed textually — `_render_critical_blockers` called only from the row-4 arm,
>   causal lead hard-wired, no hoist — compiled and bound over `generator.render_final_verdict_report`.
>   Against it the **extended `-002-21` fails**: ``row_1_below_floor: `Next:` points at a section this run's
>   document does not contain — 'Next: see the final-verdict report for the named critical files …' ->
>   '### Critical subsystems below `audited_deep`'``, and **`-002-24` fails** on
>   ``assert "### Critical subsystems below `audited_deep` (1)" in text``. Both are green against the
>   current code. Neither is a rubber stamp.
> - **(i) The two surfaces agree for every reachable row/state.** Enumerated every named quantity on
>   `render_ship_readiness` against the document: `Verdict-blocking findings: N` → `**Blocking Findings**`;
>   `Deeply examined: …` → `**Deep Coverage Ratio**` (both the scoped and unscoped variants);
>   `Critical files not examined deeply: N` → ``### Critical subsystems below `audited_deep` (N)``, now on
>   **every** row that carries one. The only `Next:` line that is *not* registered in `_REPORT_POINTERS` is
>   the `--coverage-scope application` advice, which points at a **flag**, not at a document section — the
>   right exclusion. The one residual asymmetry the reviewer could construct — `critical_subsystems_all_deep`
>   False with an **empty** `critical_subsystems_not_deep`, which would print the counter and the pointer
>   over an absent section — **has no producer**: `pipeline.py:730-732` derives `all_deep = not not_deep`
>   from one call, and `verdict_gate.py:663` forces `not_deep = ()` whenever `all_deep` is True. It is
>   reachable only by hand-constructing an inconsistent `evaluate_verdict` call, i.e. the same
>   contract-violation class `ShipReadinessError` already covers. Not a finding; recorded so it is not
>   re-derived.
> - **(ii) Row 4's causal lead is byte-identical.** ``These withheld `RELEASE_READY` (FR16).`` compares
>   equal to the sentence at `9109e16`'s `generator.py` (`git show HEAD:argus/reports/generator.py`), and
>   `-002-21` pins it to row 4 **and only** row 4.
> - **(iii) The non-causal lead is TRUE for rows 1 and 2.** Row 1 folds on the floor
>   (`verdict_gate.py:627`), row 2 on `blocking >= 1` (`:631`) — neither evaluated the critical clause, and
>   `_CRITICAL_LEAD_NOT_THE_CAUSE` asserts no causation ("Not the reason for this verdict"). Its forward
>   claim — the clause "will withhold `RELEASE_READY` once the stated reason is resolved" — is the correct
>   reading of the table for both rows (resolving the stated reason lands the run in row 4, not row 3).
> - **(iv) AC6's cleanup is INTACT.** Re-read the row-2 arm (`generator.py:397-411`): it appends the
>   `CAUTION` finding sentence and nothing else — no coverage clause, no critical clause, and
>   `_render_test_dilution_hint` is not called. `-002-24` pins all three negatives **plus** the new positives
>   (list present, non-causal lead present, causal lead absent). The restored section is a work LIST under an
>   explicitly non-causal lead, not a reason clause; the distinction is asserted, not merely argued.
> - **No new dead code from the R1 fix.** Both new branches are exercised: `if critical_blockers:` either
>   way, and `if lines[-1] != ""` both ways (row 2 ends on a callout → True; rows 1/4 end on a blank → False).
>   `critical_lead`'s default is reachable via rows 1 and 2; row 3 cannot carry a non-empty set at all
>   (`RELEASE_READY` requires `critical_subsystems_all_deep`), so the section is vacuously absent there.
>   The row decision is still made in exactly one place — the helper derives no row (§3.3 / AR7).
>
> **The dev's claimed SECOND instance (row 1) is REAL — but its provenance in the record is wrong, and the
> reviewer has corrected it here rather than opening a finding.** Verified independently: against the
> reconstructed round-1 code, a below-floor fold (10 files, 1 deep, one unmet critical) emits the counter and
> the `Next:` pointer while the document contains **zero occurrences of the word "critical"**. So it is a
> genuine pre-existing defect, the widened scope was justified, and `-002-21` now closes it. **However** the
> Dev Agent Record and the Change Log say it "has [existed] since Story 8.1 split the below-floor arm out of
> the `else`". That is off by at least one story: at `9109e16` — *before* 8.1 — the arm was
> `elif verdict.verdict.value == "INSUFFICIENT_COVERAGE"` and equally omitted `_render_critical_blockers`,
> and `HEAD:argus/reports/plain_english.py:178-180` already emitted the pointer. The defect predates 8.1;
> 8.1 only changed that arm's predicate. Nothing in the code or the disposition changes — if anything the
> defect is older and the fix better justified — so this is a record correction, not an action item. (§3.4
> evidence immutability: the original text is left standing and corrected here.)
>
> **R2 (Low) — CLOSED.** Extracted every `TC-ArgusAgent-<AREA>-<SEQ>-<SUBSEQ>` id from every test **function
> name** in `tests/`: **zero duplicates suite-wide**. `test_plain_english.py` owns `-002-10…-17`,
> `test_report_honesty.py` owns `-002-18/-19/-24`, `test_report_surface_consistency.py` owns `-002-20…-23`.
> The AC map is unambiguous (AC4 → `-002-17`, AC6 → `-002-24`), and `deferred-work.md` names `-002-20` for
> the DF-8-1-A closure, so no ledger edit was owed — the ledger is byte-unchanged this round, as claimed.
>
> **REGRESSION SWEEP — all clean, re-derived not assumed.**
> - **DF-8-1-A stays closed, both halves.** The **pre-8.3** implementation of both surfaces was rebuilt
>   (historic `_headline` + the three-arm block keyed on `is_below_floor`) and injected. Against it the
>   2/5-deep cause renders ``> Repository is NOT ready for release — deep coverage `2/5` is below the `3/5`
>   release threshold.`` and the **5/5-deep** cause (`deep_ratio == 1`, i.e. 100 %) renders
>   ``> Repository is NOT ready for release — at least one critical subsystem is not audited deep (FR16).``,
>   with the row-1 *"too little of the code was examined deeply"* headline on **both**. `-002-20` is RED
>   against that code and green against the current code.
> - **The `NOT VOUCHED` deletion stays safe.** Re-checked structurally: `AuditVerdict` still has exactly ONE
>   construction site in `argus/` (`verdict_gate.py:651`); the only other producer is
>   `prosecutor.py:494`'s `model_copy(update={"ordered_findings": …})`, which cannot change
>   `blocking_finding_count`; no `model_validate`, no read-back. No reachable path raises
>   `ShipReadinessError` where the old code rendered prose. `plain_english.py` is unchanged this round.
> - **Rows 1/2/3 headlines are byte-identical**, compared directly against
>   `HEAD:argus/reports/plain_english.py:95-123`. Only row 4 differs (the relocated + widened `NOT VOUCHED`
>   prose). Row 1's *body* legitimately gained the work list; its *headline* did not move.
> - **AC14 fences held.** `argus/pipeline.py` = **1199 lines, md5 `399d6da1d36d668352fd7b0d539cc307`** —
>   exactly the orchestrator's independent measurement; `argus/cli.py` and `argus/__init__.py` `git diff` →
>   empty; `tests/test_dogfood_proof.py`, `minions-dogfood-proof.md` and **both** `final-verdict.md`
>   artifacts absent from `git diff` entirely — the DR-10 artifact was **not** re-derived and the rot check
>   was **not** weakened (it still asserts the full ``'`RELEASE_READY` (exit `0`)'`` string).
>   DF-8-2-A / DF-8-2-B / DF-8-3-B / DF-8-3-C not re-litigated.
>
> **The concurrent-session accounting is HONEST — the dev did not absorb a foreign change.** Verified:
> `tests/test_no_web_imports.py` holds **12** test defs at `HEAD` and **13** in the worktree (+1 collected,
> +1 passed — foreign, Epic 9). The two files this round touched hold **12** (`test_report_honesty.py`) and
> **4** (`test_report_surface_consistency.py`) test defs, matching the round-1 counts: `-002-17`→`-002-24`
> is a rename and `-002-21` was extended in place, so this round added **zero** test functions. The
> 1126/1123 → 1127/1124 movement is fully attributable to the foreign edit, exactly as recorded.
>
> **Reviewer's own runs (iteration 2).** `PYTHONIOENCODING=utf-8 python -m pytest tests/ -q --tb=no` →
> **1127 collected / 1124 passed / 3 failed / 0 skipped** (progress map carries no `s`; collection
> re-counted independently at 1127), the 3 reds being **exactly** the adjudicated carve-out
> (`test_dogfood_plan.py` ×2 inherited, `test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run`
> deliberate / Story 8.5). `python -m mypy argus` → `Success: no issues found in 69 source files`.
> `wc -l` → `generator.py` 613, `plain_english.py` 258, `pipeline.py` 1199 — all under NFR-M1's 1200.
> Live `python -m argus.cli audit .` → `verdict=RELEASE_READY deep_ratio=57/148 blocking_findings=0
> assessed_deep_ratio=57/73 scope=application held_out=75`, exit `0` — identical to the Dev record and to
> the reviewer's iteration-1 run; nothing was adjusted to make it any value (B1).
>
> **No open findings. Both iteration-1 findings are genuinely closed, the widened scope rested on a true
> premise, and nothing regressed.** Status → `done`.

---

## Dev Notes

### LOCKED decisions taken at story design — with rationale (record these; do not re-litigate)

**D1 — the row-1-vs-row-4 split is driven by `AuditVerdict.is_below_floor`, never by `decision_row` and
never by a re-derived ratio comparison.**
*Rationale:* `is_below_floor`'s own docstring names it *"THE single source of truth for every consumer that
has to distinguish [row 1] from [row 4]"* and warns that *"re-deriving this from the counters in each
consumer would fork the decision table (§3.3)"*. It also carries the pre-amendment fallback (a
`decision_row is None`, `schema_version "1"` payload resolves to the old — and for such a payload still
correct — enum equivalence), which a raw `decision_row is DecisionRow.BELOW_FLOOR` check would get wrong.
`generator.py:306` already keys on it; `plain_english.py` should match. *Rejected alternative:* branching on
`decision_row` directly — it would make the two surfaces disagree on exactly the pre-amendment payload the
8.1 A8 work exists to protect.

**D2 — the `NOT VOUCHED` branch is RESOLVED BY RELOCATION: the prose moves to row 4; the unreachable
predicate is deleted; the impossible input becomes a typed raise.**
*Rationale:* DR-11 offers two outs — *"either delete it or prove it still reachable"* — and the 270-fold
sweep settles it: there is no reachable path. But the branch's *text* is not the problem; it is the correct
row-4 message written against the pre-amendment world, and deleting good prose to re-author it elsewhere
would be pointless churn. So the words move to where they are true. What must **not** happen is the third
outcome: a bare structural deletion that lets a contract-violating input fall into the row-2 arm and print
`BLOCKED — 0 verdict-blocking finding(s)` — the *original bug string*, reintroduced. The house pattern for
"closed vocabulary, exhaustive branch, no silent default" is a typed raise, used twice in this exact
neighbourhood: `exit_code_for_verdict` (*"RAISES on a member missing here … never a silent default"*,
`verdict_gate.py:496-502`) and `_assurance_statement` (`raise NegativeAssuranceError` on an unhandled
verdict, `negative_assurance.py:333-335`). A raise is also **testable**, which is precisely what DR-11
demands instead of untested dead code, and `cli.py:272` already degrades a `ValueError` to a typed,
secret-safe exit `1` (AR10). *Rejected alternatives:* (a) keep the branch and "prove reachability" — there
is none, and manufacturing one by hand-constructing a verdict would prove only that Pydantic lets you build
an illegal object; (b) delete it and let the state fall through to row 2 — reintroduces the bug string;
(c) `assert` — stripped under `python -O`, and this codebase never uses bare asserts for contract
enforcement.

**D3 — a row-2 report names ONLY the finding. Coverage and the critical clause are not "reasons".**
*Rationale:* FR16's table is *evaluated in order* and short-circuits: when row 2 fires, rows 3 and 4 were
never reached, so their conditions are not the cause of anything. Appending them is a **false causal claim**
of exactly the kind this epic exists to delete — it is the mirror image of DF-8-1-A (there, a coverage
result was described as a defect; here, a defect result is described as partly a coverage problem).
Measured live: a diluted row-2 run today prints both. *Where best practice and project context could
conflict:* one could argue "more information is better" and keep the clauses as context. **The project
standard wins** — PRD FR16's binding contract is that a verdict asserts exactly one thing, and cross-cutting
concern #6 (the false-accusation moat) is about not attaching claims the tool did not make. Recorded per the
conflict rule.

**D4 — the two surfaces share ONE register, and any shared helper lives in `plain_english.py`.**
*Rationale:* `generator.py` already imports from `plain_english` (`:22`); `plain_english` is the PURE, lower
module and imports only `verdict_gate`. A helper in the other direction would invert the layering and drag
`CoverageLedger`/`AuditRequest` into a module whose whole point is that it depends on nothing but the
verdict. If you find yourself writing the same "which gate was unmet" sentence twice, that is the §3.3 fork
signal — extract it into `plain_english.py` and import it. *Corollary:* the row-4 wording must also agree
with `negative_assurance._assurance_statement`'s already-landed row-4 sentence (*"No blocking findings were
detected within the assessed scope; a coverage or critical-subsystem gate was not met, so release readiness
was not vouched for"*) — that is the persisted machine artifact for the same run, and one run's artifacts
must not describe themselves differently.

**D5 — naming the VACUOUSLY-SATISFIED critical gate in human prose is OUT of scope, deliberately.**
Story 8.2's D5 wrote *"adding the POSITIVE prose that names the vacuity for a human is Story 8.3 / DR-11"*.
Examined and **declined**, for three converging reasons: (i) the **epic's own AC block for 8.3 does not ask
for it** — it asks that the critical-paths section *"renders correctly for an empty set"* and that the
`--exclude-critical` guidance stop being wrong, both of which **AC7** delivers; (ii) the information does not
exist on `AuditVerdict` — `critical_subsystems_all_deep=True` with an empty `critical_subsystems_not_deep` is
identical for "the set was emptied by the filter" and "there were never any criticals". Only
`CriticalSubsystemSet.heuristic_excluded_ineligible` (8.2's disclosure map) distinguishes them, and getting
it into the report means a new argument on `generate_reports` **threaded from `pipeline.py:793`** — an edit
to a file at **1199 of 1200** lines, which **DF-8-2-A** says must trigger a module extraction first; (iii)
8.2 already proved the strong property that matters — `TC-ArgusAgent-PIPELINE-002-07` shows **no surface
asserts** a vacuous positive. What remains is an *omission*, not a falsehood, and this story's subject is
falsehoods. *Rejected alternative:* re-deriving the vacuity inside `generator.py` from `ast_index` — that is
a §3.3 fork of the eligibility filter, categorically forbidden. **Action:** per **AC15(d)**, file it as a new
deferred entry targeted at the story that performs the DF-8-2-A extraction. If you find a route that needs
neither a `pipeline.py` edit nor a re-derivation, you *may* implement it — but it is **not** an AC and it
must not expand the delta.

**D6 — DF-8-2-A is honoured by NOT touching `pipeline.py`, not by extracting a module.**
*Rationale:* the ledger's close condition is *"extract a shell-helper module … as the FIRST act of whichever
story next edits `pipeline.py`, rather than adding to it"*. This story, by design (D5 + AC8's use of the
already-threaded `ast_index`), edits nothing in `pipeline.py` — so the trigger never fires and performing an
unrelated refactor of the largest file in the tree inside a *wording* story would be exactly the
scope-bundling that makes deltas unreviewable. The constraint is instead **converted into a fence** (AC14)
so it cannot be breached accidentally, and carried forward append-only (AC15b). *Rejected alternative:*
doing the extraction here "since we're in the neighbourhood" — we are not in the neighbourhood, and 8.2's
review explicitly recorded *"DF-8-2-A stands unchanged for 8.3"*.

**D7 — DF-8-2-B is NOT pulled in.**
*Rationale:* its ledger `target_story` is **conditional** — *"8-3 (or the first story that edits
`argus/detectors/vacuous_test.py`)"* — and this story does not edit that file. It is a **detector-semantics**
defect (two `_UNAMBIGUOUS_TEST_SUFFIXES` entries missing a word separator), not a report-surface one; the
reviewer measured **zero instances in this repository** (no `.java`/`.rb` sources among 147 indexed files)
and proved it is not a false green, because the grading stage misclassifies identically. Folding a detector
fix into a rendering story would break story single-purpose and put a `tests/test_vacuous_detector.py`
corpus change in a diff nobody would expect it in. Carried forward append-only (AC15c). *(Note: **AC8 reads
`is_test_file` differently** — with `ast_entry=` — but does not modify `vacuous_test.py`; that file stays on
the AC14 fence.)*

**D8 — no new module, no new CLI flag, no schema bump.**
This story changes **prose and branch structure** in two existing files plus their tests. `Verdict`,
`DecisionRow`, `AuditVerdict`, `VERDICT_SCHEMA_VERSION` (`"2"`),
`CRITICAL_SUBSYSTEMS_SCHEMA_VERSION` (`"2"`), the exit-code map and the stdout line are all untouched. The
only new *symbol* is the typed error class D2 requires. Nothing this story emits is persisted under
`.argus/`, so **no content hash and no cache key moves** — the reports are written to `request.report_dir`,
outside the content-addressed store.

### Proposed shape — the branch structure and the strings (a starting point, not a straitjacket)

The ACs bind the **meaning**; the exact words are yours, provided every assertion in the work-list table
above still holds. This sketch exists so you do not spend the delta re-deriving a structure the SM already
walked. **Deviate freely — but record the deviation and its reason.**

```python
# argus/reports/plain_english.py

class ShipReadinessError(ValueError):
    """A verdict the FR16 gate cannot produce reached the human renderer (AR10).

    Raised ONLY for NOT_READY_FOR_RELEASE with blocking_finding_count == 0: post-Story-8.1
    the ONLY path to NOT_READY_FOR_RELEASE is row 2, which requires >= 1 verdict-eligible
    finding. Rendering that state would print "BLOCKED - 0 verdict-blocking finding(s)" -
    the exact false accusation this epic exists to delete - so it is a typed failure, never
    a silent default (the exit_code_for_verdict / NegativeAssuranceError house pattern).
    """


def _headline(verdict: AuditVerdict) -> str:
    if verdict.verdict is Verdict.RELEASE_READY:                      # row 3
        return "READY — ..."                                          # UNCHANGED
    if verdict.verdict is Verdict.INSUFFICIENT_COVERAGE:
        if verdict.is_below_floor:                                    # row 1  (D1)
            return "NOT ASSESSED — ..."                               # UNCHANGED, byte-identical
        return (                                                      # row 4  (relocated prose, D2)
            "NOT VOUCHED — nothing broken was found, but a coverage or critical-subsystem "
            "gate was not met, so no release-readiness claim is made. This is a statement "
            "about the audit, not about the code."
        )
    if verdict.blocking_finding_count < 1:                            # impossible (D2)
        raise ShipReadinessError(...)
    return f"BLOCKED — {verdict.blocking_finding_count} verdict-blocking finding(s) must be resolved."
```

Note the row-4 string is today's else-branch text with **one widening**: `"a coverage gate"` →
`"a coverage or critical-subsystem gate"` (measured: row 4 fires at 5/5 deep on the critical clause alone).
Rows 1, 2 and 3 stay byte-identical, which is what keeps 8 of the 10 existing `test_plain_english.py` tests
green untouched.

```python
# argus/reports/generator.py — the four arms are exactly the four FR16 rows

if verdict.verdict is Verdict.RELEASE_READY:            # row 3 — TIP, unchanged
    ...
elif verdict.is_below_floor:                            # row 1 — WARNING, unchanged (8.1)
    ...
elif verdict.blocking_finding_count > 0:                # row 2 — findings ONLY (D3)
    lines.append(render_callout(
        "CAUTION",
        f"Repository is NOT ready for release — "
        f"{verdict.blocking_finding_count} verdict-blocking finding(s)."))
    # NO coverage clause, NO critical clause, NO dilution hint — the table short-circuited here.
else:                                                   # row 4 — the DF-8-1-A fix
    #   assessed_ratio < 3/5   -> "deep coverage `X` is below the `3/5` release threshold"
    #   not all criticals deep -> "at least one critical subsystem is not audited deep (FR16)"
    #     ^ KEEP this exact phrase: TC-ArgusAgent-REPORT-002-01 asserts it
    lines.append(render_callout(
        "WARNING",
        f"Release readiness is NOT VOUCHED — Argus found nothing blocking, but {detail}. "
        f"This is a statement about the audit, not about the code."))
    lines.extend(_render_test_dilution_hint(verdict, ledger, ast_index))
    lines.extend(_render_critical_blockers(verdict, ledger))
```

Two things to get right in that `else`: (i) the `detail` join must never be empty — row 4 fires *because*
at least one gate is unmet, so the existing `"a release gate was not satisfied"` fallback becomes
unreachable; delete it or prove it reachable (**AC6**'s rule applies to it too). (ii) `WARNING` vs `CAUTION`
is a deliberate de-escalation: GitHub renders `CAUTION` as the "negative consequences" level, which is the
wrong register for *"I did not look at enough to say"*. `WARNING` matches the row-1 arm 8.1 already landed,
so the two `INSUFFICIENT_COVERAGE` rows share a severity and differ only in words — which is precisely
boundary B4.

### Architecture patterns & constraints (non-negotiable — AR/NFR ids a reviewer will check)

- **AR8 pure/impure master rule.** Both modules are PURE renderers: no I/O, no clock, no LLM, no
  `uuid4`/`random`, no set/dict iteration-order reliance. `plain_english.py` imports **only**
  `argus.verdict.verdict_gate` — adding any import to it is a review finding.
- **§3.3 / AR7 no-fork.** Do not write a second decision table, a second "which gate was unmet" sentence, or
  a second test-file predicate. Every consumer that needs to know *why* a verdict was rendered reads
  `is_below_floor` / `decision_row` / `blocking_finding_count` from the verdict it was handed.
- **AR4 determinism.** Ratios are exact `Fraction`, **never `float`** — including inside f-strings. Do not
  compute a percentage. `Fraction(5, 5)` renders as `1`, not `5/5`; that is pre-existing and **not** this
  story's to change (see *Pre-existing observations*).
- **AR3 wire contract.** Exit codes `0`/`2`/`3`/`1` are untouched. `1` is the pipeline's typed-error
  degradation — which is where D2's raise lands, and that is deliberate.
- **AR10 typed failure.** The new error is a `ValueError` subclass with a message naming the typed reason
  only — never source bytes, never an absolute path, never a bare `except: pass`. **No `print()` in library
  code** (architecture.md, *Error / Degradation Patterns*): both modules **return** strings/tuples; the CLI
  owns the printing. Do not add a `print`, a logger call or a `sys.stderr.write` to either module.
- **Contract/Format pattern — *"Verdict vocabulary (canonical) … Downstream artifacts use this vocabulary
  verbatim"*** (architecture.md, *Contract / Format Patterns*). The enum tokens `RELEASE_READY` /
  `NOT_READY_FOR_RELEASE` / `INSUFFICIENT_COVERAGE` and the exit codes `0/2/3/1` are printed verbatim by
  `generator.py:272` and must stay so. Your prose is the *human companion* to those tokens, never a
  replacement and never a fourth vocabulary — do not invent a new state word that reads like an enum member.
- **NFR-S1.** No source bytes, secret bytes or absolute host paths in any rendered line. Everything either
  surface prints must be a restatement of a counter already on the verdict, or a repo-relative POSIX path.
- **NFR-D2 zero-token testability.** Every AC except AC13 is provable over synthetic ledgers with no LLM and
  no network. Do not reach for a live audit run to prove a pure-rendering property.
- **NFR-M1** ≤1200 lines per file. Today: `plain_english.py` **186**, `generator.py` **505**,
  `cli.py` **298**, `pipeline.py` **1199** ⚠️ (fenced). Ample headroom in the two files you are editing.
- **NFR-M2** additive-only contracts. No field is added, removed or renamed by this story.

### Traps a previous story already paid for (Epic 1–8.2 learnings that apply here)

- **Measure IN PLACE, never on a scratch copy.** 8.1's blast radius was taken on a tree with no `.git` and
  no `_bmad-output/`; it misclassified `tests/test_dogfood_proof.py` as environmental when it was
  delta-caused, and cost a review round (8.1 finding R3). 8.2 measured in place and was exact. This story's
  numbers were measured in place by importing the shipped functions — **re-derive them the same way**.
- **Verify independently; do not trust a prior record.** Every Epic-6/7/8 review re-ran everything itself.
  The tables above are the SM's measurement, not scripture.
- **A re-pointed test must keep its original subject and gain precision.** 8.1's review checked every
  re-point for this. `test_zero_finding_block_does_not_read_as_a_defect_claim` keeps its subject; only the
  verdict it is asserted against moves from an impossible state to the real row-4 state.
- **Do not trade one piece of dead code for another.** DR-11 exists because 8.1's CR-2 stopgap left dead
  code behind. AC6's `blocking_finding_count > 0` clause is the same trap one level down — the SM found it
  by reading, not by running. Audit every branch you make unreachable.
- **"Extended, not forked" applies to guard lists and evidence fixtures.** `_MODULES_UNDER_GUARD` is
  appended to, never replaced. `tests/fixtures/verdict_schema_v1_row2_artifacts.json` is **evidence**, not a
  golden to regenerate (8.1 finding R4) — and it is on the AC14 fence.
- **Non-ASCII adversarial coverage (AI-E1-1) is a standing requirement** since Epic 1's only review FAIL.
  This story renders paths into a Markdown table; discharge it with an actual non-ASCII path, not a sentence.
- **Do not flip the story to `review` before the tests exist** (AI-E2-1, Epic-2 retrospective).
- **Run tests as** `PYTHONIOENCODING=utf-8 python -m pytest tests/ -q` (the suite carries non-ASCII
  fixtures, and Windows `cp1252` stdout will `UnicodeEncodeError` on the em-dashes these very modules
  emit — the SM hit this while measuring). `pytest-timeout` is **not** installed — do not pass `--timeout`.
  A full run takes ≈3.5 minutes.

### Runtime, library and toolchain specifics (verified on this machine, 2026-08-05)

`python 3.11.15` · `pydantic 2.13.4` · `pytest 9.1.1` · `mypy 2.3.0` (clean over 69 files) ·
`tree-sitter` pinned `>=0.25,<0.26` (folded into the Epic-5 determinism closure — do not bump it here).
**No new dependency is introduced by this story**; everything it needs is stdlib plus what the two modules
already import. There is **no web research obligation** here: this delta touches no external API, no
library version and no network surface — it is prose and branch structure over frozen in-repo contracts.

Python/Pydantic specifics that bite on this exact change:

- `AuditVerdict` is `ConfigDict(frozen=True, extra="forbid")`. The tests in `test_plain_english.py`
  construct it **directly**, bypassing `evaluate_verdict` — which is exactly how the impossible
  `NOT_READY ∧ blocking == 0` state gets built. That is legitimate for the AC2 contract-violation pin and
  illegitimate everywhere else: **every other new test must fold a real `evaluate_verdict`**, or it proves
  nothing about what the tool can produce.
- `decision_row` defaults to `None`. A directly-constructed `AuditVerdict` therefore has `is_below_floor ==
  (verdict is INSUFFICIENT_COVERAGE)`. That is why test #2 in the work-list table stays green today and why
  the row-1/row-4 split needs **real folds** to be meaningful.
- `Fraction` in an f-string uses `str(Fraction)`, which normalises: `Fraction(5, 5)` → `"1"`,
  `Fraction(40, 126)` → `"20/63"`. Existing tests depend on this; do not "fix" it.
- `render_callout(level, text)` from `reports/formatter.py` produces `> [!LEVEL]\n> text`. Use it.
- `str`-valued enums serialize to `.value`; `Verdict.INSUFFICIENT_COVERAGE.value` is the wire token
  `generator.py:272` prints. Unchanged.

### Recent git context (last commits on `fix/honest-verdict-reporting`)

`9109e16` docs(readiness) · `d8ba5ad` docs(prd): FR16/FR4 verdict-contract amendment propagated to epics ·
`faeefd9` fix(verdict): stop reporting a block when nothing was found · `ae5f00c` fix(audit): make verdicts
honest and the tool runnable on any repo · `37ca977` feat(verdict): verdict gate for core readiness.
The pattern of the last five commits is **small, single-concern changes to the verdict path, with the paper
trail landing first**. Follow it: this story is two source files plus their tests. Stories 8.1 and 8.2 are
**both uncommitted on top of `9109e16`** — `git stash`, `git checkout --` or a reset would destroy them.

### Pre-existing observations — NOT this story's bugs, do not fix here

- **`Fraction(5, 5)` renders as `1`.** A 100 %-deep run prints `Deeply examined: 5 of 5 files (1)` and
  `**Deep Coverage Ratio**: **1** (5/5 files)`. Ugly, honest, pre-existing, and asserted by existing tests
  (`test_report_honesty.py::…ratio_shown_is_the_one_the_gate_used` compares `str(Fraction)`). **Leave it.**
- **`plain_english`'s `Next: --coverage-scope application` line can fire for a row-2 run** (measured). It is
  *advice*, not a causal claim, and it is not false — narrowing genuinely is available. AC6 governs only the
  **causal** framing in `generator.py`. Considered and deliberately left; if you disagree, say so in the Dev
  Agent Record rather than silently changing it.
- **`_render_test_dilution_hint`'s `if verdict.verdict is Verdict.RELEASE_READY: return []` guard is
  redundant** with the `deep_ratio >= threshold` guard two lines later (a scoped RELEASE_READY is caught by
  the first guard; an unscoped one has `deep_ratio >= 3/5`). Pre-existing. AC6 asks you to *audit and record*
  it, not necessarily to change it.
- **The resume path builds critical candidates from resume-target entries only** (`pipeline.py:1068`).
  8.2 recorded it; unchanged and unrelated. `pipeline.py` is fenced anyway.

### Project Structure Notes

- **Files this story is expected to modify:** `argus/reports/plain_english.py` (the substance — `_headline`
  restructure, row-4 relocation, typed error), `argus/reports/generator.py` (the four-arm branch split, the
  row-2/row-4 reason lists, the dilution hint, the critical-blocker guidance, the `ast_entry` fix), and the
  test files: `tests/test_plain_english.py`, `tests/test_report_honesty.py`, `tests/test_cli.py` (add only),
  plus **new** tests for the AC11 cross-surface net and the AC10 generator determinism/secret pin (either a
  new module or an addition to `tests/test_report_honesty.py` — your call, state it).
- **Files this story must NOT modify:** see **AC14** for the binding list.
- **No new module is required** in `argus/`. If you add a test module, follow the existing naming
  (`tests/test_<subject>.py`) and add nothing to `_MODULES_UNDER_GUARD` (no new `argus/` module exists).
- **Test tree:** `tests/` at the repo root — *not* the `tests/apaa/` path in the older architecture prose,
  which describes the pre-extraction Minions monorepo.
- **Test-id convention:** `TC-ArgusAgent-<AREA>-<SEQ>-<SUBSEQ>`. The report area is
  `TC-ArgusAgent-REPORT-002-NN`, currently to **-09** (`test_report_honesty.py`); `test_plain_english.py`
  declares the same area but numbers nothing — **number your new tests and continue from -10**. The CLI area
  is `TC-ArgusAgent-CLI-001-NN`, currently to **-30** (8.1's) — continue at **-31**. Do not restart a
  sequence.
- ⚠️ **The working tree carries Stories 8.1 AND 8.2's UNCOMMITTED deltas.** Do not stash, checkout or reset.

### Variance from the epic, recorded

The epic's six ACs for Story 8.3 are carried in full (**AC1** ← epic AC1; **AC2** ← epic AC2; **AC3** ←
epic AC3; **AC4** ← epic AC4/boundary B4; **AC5 + AC7** ← epic AC5; **AC9** ← epic AC6). The additions were
made at story design **after measuring the change against the real tree**:

- **AC6 (row-2 contamination)** — *measured, not predicted*: a diluted row-2 run today names the coverage
  threshold as a reason and prints a "this coverage result is driven by test-file dilution" NOTE. The epic
  AC says generator's branches *"agree with the amended table"*; this is the concrete way in which they do
  not. Its dead-branch sub-clause exists because the fix creates a new unreachable branch — the exact defect
  DR-11 was raised to remove.
- **AC8 (classification consistency)** — *measured*: exactly one file of 147 on this repo is classified
  differently by the report and by the pipeline. It is fixable with the `ast_index` `generate_reports`
  already receives, i.e. without breaching the DF-8-2-A constraint, and a report whose denominator disagrees
  with the verdict's is the same defect class as a report whose callout disagrees with the verdict.
- **AC10 (determinism + secret-safety on the generator surface)** — the epic AC says *"the existing
  determinism and secret-safety properties of both report surfaces remain pinned"*. Measured: `plain_english`
  has such a pin; **`render_final_verdict_report` has none**. "Remain pinned" cannot be satisfied for a
  surface that was never pinned, so the pin is added.
- **AC11 (four-row cross-surface net)** — the single test that would have caught DF-8-1-A. Without it every
  other AC can pass while a fifth combination stays self-contradicting.
- **AC12/AC13/AC14/AC15** — the standing whole-system, honest-recording, fence and ledger obligations every
  Epic-8 story carries.

They are in scope under the standing rule that a story must leave the system working end-to-end and must
never ship an artifact that contradicts the shipped contract. The scope boundaries are stated in **D5**
(vacuity prose — out), **D6** (`pipeline.py` / DF-8-2-A — fenced, carried forward) and **D7** (DF-8-2-B —
carried forward). **DF-8-1-A is pulled in and closed here**, per both its ledger `target_story` and the
epic's own 8.3 AC block.

### References

- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Story 8.3: The plain-English report stops describing an impossible state`] (lines 1505–1538) — the six ACs carried above, including boundary **B4**
- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Derived Delta Requirements (DR)`] (line 1169) — **DR-11**, incl. the self-consistency pass that widened it to `generator.py`
- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Story 8.1`] (lines 1440–1457) — the **LOCKED channel decision**: artifact = explicit field, **stdout summary line UNCHANGED**, stderr = prose
- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Story 8.5`] (lines 1566–1614) — why both `final-verdict.md` artifacts and `minions-dogfood-proof.md` are NOT this story's
- [Source: `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md#Release-Readiness Verdict`] (lines 411–425) — the binding FR16 four-row table and the canonical verdict vocabulary (*"`INSUFFICIENT_COVERAGE` … is not a blocking verdict"*)
- [Source: `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md#User Success`] (line 135) — *"Actionable, not a hedge: a plain-English line the user acts on"* — the product goal this story serves
- [Source: `_bmad-output/design-artifacts/ArgusAgent/architecture.md#Implementation Patterns & Consistency Rules`] (lines 332–400) — *Pure/Impure Separation* (master rule), *Determinism Patterns* (no float, one serializer), *Contract / Format Patterns* (*"Verdict vocabulary (canonical) … Downstream artifacts use this vocabulary verbatim"*), *Reuse / Import Patterns*, *Error / Degradation Patterns* (*"no `print()` in library code"*), *Naming & Structure Patterns* (≤1200 lines, `TC-<AREA>-<SEQ>-<SUBSEQ>`)
- [Source: `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`] (lines 496–564) — **DF-8-1-A** (closed here), **DF-8-2-A** (carried), **DF-8-2-B** (carried), and the six mandatory CC-3 fields
- [Source: `_bmad-output/design-artifacts/ArgusAgent/stories/8-1-findings-before-coverage-binding-decision-table.md`] — the four-row fold, `DecisionRow`/`is_below_floor`, **D4**'s conflict rule, **D5**'s accepted transient (*"`plain_english.py`'s `INSUFFICIENT_COVERAGE` headline will be imprecise for row 4 … Story 8.3 … its ACs already specify the two-way wording split"*), and the scratch-tree measurement lesson
- [Source: `_bmad-output/design-artifacts/ArgusAgent/stories/8-2-critical-subsystem-gates-operator-can-actually-satisfy.md`] — the eligibility filter, `heuristic_excluded_ineligible`, **D5**'s hand-off of the vacuity prose, and the live-consumer table naming both report surfaces as 8.3's
- [Source: `argus/reports/plain_english.py:95-186`] — `_headline` (the unreachable branch at `:119-123`) and `render_ship_readiness`
- [Source: `argus/reports/generator.py:41-136,250-365`] — `_render_test_dilution_hint`, `_render_critical_blockers`, `render_final_verdict_report` (the branch block at `:304-342`, DF-8-1-A at `:337-339`)
- [Source: `argus/verdict/verdict_gate.py:210-233,380-402,505-668`] — `DecisionRow`, `is_below_floor` (the §3.3 single source of truth) and the four-row fold
- [Source: `argus/verdict/negative_assurance.py:284-335`] — the already-landed row-1/row-4 persisted statement split, whose register the report must match (**D4**)
- [Source: `argus/cli.py:199-224,279-294`] — `_summary_line` (frozen) and the stdout/stderr register split
- [Source: `argus/pipeline.py:686-694,780-800`] — `_assessment_scope_paths` (the `ast_entry=` precedent for AC8) and the `generate_reports` call site (**fenced**)
- [Source: `argus/detectors/vacuous_test.py`] — `is_test_file(path, ast_entry=…)` and `is_test_classification_content_dependent` (**read, not modified**)
- [Source: `tests/test_plain_english.py`, `tests/test_report_honesty.py`, `tests/test_report_generator.py`, `tests/test_cli.py:45-66`, `tests/test_critical_eligibility_pipeline.py:454-537`] — the complete measured work list of string-asserting tests

---

## Dev Agent Record

### Context Reference

- This story file (self-contained). Story key: `8-3-plain-english-report-stops-describing-impossible-state`.

### Agent Model Used

Claude Opus 5 (1M context) — `claude-opus-5[1m]`, via the BMAD `dev-story` workflow (mode=implement).

### Debug Log References

**Every figure below was RE-DERIVED IN PLACE** on `d:/ProjectX/XAgents/XAgents/ArgusAgent`, HEAD `9109e16`
plus 8.1's and 8.2's uncommitted deltas, `.git` and `_bmad-output/` present — by importing the shipped
`argus` functions and calling them, exactly as the SM did. Nothing in the story's tables was taken on trust.
Scratch scripts lived outside the repo (session scratchpad); no `.argus/` write and no repo file was created
by the measurement itself.

**1 — the 270-fold reachability sweep (AC1/AC2). Re-derived: IDENTICAL to the SM's table.**

```
=== SWEEP: 270 folds ===
  ('INSUFFICIENT_COVERAGE', 'row_1_below_floor', False) -> 24
  ('INSUFFICIENT_COVERAGE', 'row_1_below_floor', True) -> 48
  ('INSUFFICIENT_COVERAGE', 'row_4_gate_unmet_no_findings', False) -> 47
  ('NOT_READY_FOR_RELEASE', 'row_2_blocking_findings', True) -> 132
  ('RELEASE_READY', 'row_3_gates_met', False) -> 19
  NOT_READY_FOR_RELEASE with blocking == 0 -> 0 occurrences
```

Committed as `TC-ArgusAgent-REPORT-002-10`, which pins the exact `Counter` (not merely the zero), so a
future change to the table that reshuffles the population fails loudly instead of silently.

**2 — the pre-fix rendered-row table (both surfaces). Re-derived: the SM's defects reproduce verbatim.**

| FR16 row | `_headline` BEFORE | `final-verdict.md` callout BEFORE |
|---|---|---|
| 1 (1/10 deep) | `NOT ASSESSED — too little of the code was examined deeply…` ✅ | `[!WARNING] …below the required floor.` ✅ |
| 2 (3/5, 1 AST finding) | `BLOCKED — 1 verdict-blocking finding(s) must be resolved.` ✅ | `[!CAUTION] Repository is NOT ready for release — 1 verdict-blocking finding(s).` ✅ |
| 3 (3/5, 0 findings) | `READY — …` ✅ | `[!TIP] …satisfies all deterministic release readiness criteria.` ✅ |
| **4 (2/5, 0 findings)** | `NOT ASSESSED — too little of the code was examined deeply…` ❌ | `[!CAUTION] Repository is NOT ready for release — deep coverage `2/5` is below the `3/5` release threshold.` ❌ **DF-8-1-A** |
| **4 (5/5 deep, 0 findings, 1 critical not deep)** | `NOT ASSESSED — too little of the code was examined deeply…` ❌ (at `deep_ratio == 1`, i.e. **100 %**) | `[!CAUTION] Repository is NOT ready for release — at least one critical subsystem is not audited deep (FR16).` ❌ |

**3 — the row-2 contamination (AC6). Re-derived verbatim** on the 40-app-deep / 86-test-shallow ledger
(`deep_ratio 20/63`), pre-fix:

```
> [!CAUTION]
> Repository is NOT ready for release — 1 verdict-blocking finding(s); deep coverage `20/63` is below the `3/5` release threshold.

> [!NOTE]
> This coverage result is driven by test-file dilution. 40/40 (`1`) of APPLICATION files are audited deep …
> Note that 1 blocking finding(s) would still block.
```

**4 — the classification disagreement (AC8). Re-derived: 147 indexed files, exactly ONE disagreement.**

```
source state: worktree files: 147
indexed: 147
disagreements: 1
   ('argus/detectors/vacuous_test.py', True, False)     # is_test_file(path)=True, (…, ast_entry=e)=False
```

(That count is 147 as measured BEFORE this story added `tests/test_report_surface_consistency.py`; the live
`argus audit .` below enumerates 148 for the same reason.)

**5 — RED output, captured VERBATIM before any source change** (`pytest tests/test_report_honesty.py
tests/test_report_surface_consistency.py -q`; `tests/test_plain_english.py` was a separate RED — a hard
`ImportError: cannot import name 'ShipReadinessError'` — and its behavioural assertions were verified green
only after the class and the branch split landed):

```
FAILED tests/test_report_honesty.py::test_dilution_hint_does_not_over_promise_when_another_gate_blocks
  E  AssertionError: assert 'Note that the critical-subsystem clause would still withhold `RELEASE_READY`.' in '…'
FAILED tests/test_report_honesty.py::test_TC_ArgusAgent_REPORT_002_17_row_2_names_only_the_findings
  E  AssertionError: assert 'Repository is NOT ready for release — 1 verdict-blocking finding(s).' in '…'
FAILED tests/test_report_honesty.py::test_TC_ArgusAgent_REPORT_002_19_critical_blocker_table_is_non_ascii_safe
  E  AssertionError: assert 'already dropped from the heuristic critical set' in '…'
FAILED tests/test_report_surface_consistency.py::test_TC_ArgusAgent_REPORT_002_20_row_4_document_asserts_no_block
  E      AssertionError: coverage: document still asserts a block
  E      assert not True
  E       +  where True = _asserts_a_block('# ⚖️ Argus Final Audit Verdict Report\n\n> Ship-readiness: NOT ASSESSED — too little of the code was examined deeply …')
FAILED tests/test_report_surface_consistency.py::test_TC_ArgusAgent_REPORT_002_21_all_four_rows_agree_across_both_surfaces
  E          AssertionError: row_4_gate_unmet_no_findings asserts a block on a non-blocking verdict
  E          assert not True
FAILED tests/test_report_surface_consistency.py::test_TC_ArgusAgent_REPORT_002_23_report_split_matches_the_pipeline_classification
  E  AssertionError: assert '2/2 (`1`) of APPLICATION files' in '…'
```

**6 — AC13, the live self-audit. `PYTHONIOENCODING=utf-8 python -m argus.cli audit . --commit HEAD
--report-dir <scratch>` run AFTER the delta. Recorded verbatim; nothing was adjusted to make it any
particular value (boundary B1).**

- exit code: **0**
- stdout (the frozen wire line):
  `verdict=RELEASE_READY deep_ratio=57/148 blocking_findings=0 assessed_deep_ratio=57/73 scope=application held_out=75`
- decision row (read back from the persisted `.argus/state/` verdict envelope):
  `"decision_row":"row_3_gates_met"` beside `"verdict":"RELEASE_READY"`
- deep ratio: assessed **57/73** (whole repository 57/148) · blocking findings: **0** · total findings
  emitted: 622 · 2231 files excluded (2127 dependencies, 104 gitignored)
- stderr human block, verbatim:

```
Ship-readiness: READY — no blocking problems found, and enough of the code was examined deeply to say so.
  - Verdict-blocking findings: 0
  - Deeply examined: 57 of 73 assessed files (57/73) — scope 'application', 75 held out (test_files)
  - What `audited_deep` means in this run: the file parsed cleanly, contains at least one real function or class, and every enabled deterministic detector ran over it. No language model read any source — no LLM-backed deep pass was enabled. This is a structural and deterministic assurance grade, not a comprehension grade.
```

Same figures as 8.2's recorded run (`RELEASE_READY` / exit `0` / `row_3_gates_met` / assessed `57/73` / 0
blocking); the whole-repository denominator moved 147 → 148 because this story added one test module.
Reports were written to a scratch directory, NOT into `_bmad-output/` — the two committed `final-verdict.md`
artifacts are Story 8.5's (DR-10) and are on the AC14 fence.

**7 — AC12 whole-system.**

```
PYTHONIOENCODING=utf-8 python -m pytest tests/ -q   →  tests="1126" failures="3" errors="0" skipped="0"
                                                        (junitxml, time 369.3s) — i.e. 1123 passed
python -m mypy argus                                →  Success: no issues found in 69 source files
```

The three reds are EXACTLY the adjudicated carve-out, unchanged and untouched:

```
FAILED tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation
FAILED tests/test_dogfood_plan.py::test_budget_reuses_the_31_accountant_no_fork
FAILED tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run
```

1–2 are inherited (red at `9109e16`). 3 is the deliberate rot check on `minions-dogfood-proof.md`, Story
8.5 / DR-10's deliverable; its message is still
``assert '`RELEASE_READY` (exit `0`)' in <the stale committed markdown>`` — unchanged by this delta.
Collected count **1126** (baseline 1111; +15 net, nothing deleted or skipped). No source file exceeds 1200
lines: `plain_english.py` 186 → **258**, `generator.py` 505 → **560**, `pipeline.py` **1199** (untouched).

**8 — AC14 fence verification, per path.**

`git diff` is empty for every fenced path this story could have touched:

| Path | Result |
|---|---|
| `argus/cli.py` | `git diff` → 0 files changed (byte-identical to `9109e16`) |
| `argus/__init__.py` | `git diff` → 0 files changed |
| `argus/dogfood/*` | `git diff` → 0 files changed |
| `tests/fixtures/*` | `git diff` → 0 files changed (`verdict_schema_v1_row2_artifacts.json` stays 8.1's staged-added evidence, unmodified) |
| `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md` | `git diff` → 0 files changed |
| `_bmad-output/reports/final-verdict.md` | `git diff` → 0 files changed |
| `_bmad-output/audit-reports/final-verdict.md` | `git diff` → 0 files changed |
| `action.yml`, `.github/workflows/argus-student-audit.yml` | still `??` untracked and unmodified (the user's, Epic 9) |

The remaining fenced paths already carry 8.1/8.2's UNCOMMITTED deltas, so `git diff` against `9109e16` is
non-empty for reasons that predate this story; byte-identity to their pre-8.3 state is evidenced by an
unchanged mtime (all before this session's first edit) and unchanged size/hash:
`argus/pipeline.py` (mtime 2026-08-05 08:00:33, **1199 lines**, md5 `399d6da1d36d668352fd7b0d539cc307`),
`argus/detectors/vacuous_test.py` (07:38:47, md5 `8a0705030391df92ad1404af9d044758`),
`argus/verdict/verdict_gate.py` (2026-08-04 14:25:33), `argus/verdict/prosecutor.py` (17:25:13),
`argus/verdict/negative_assurance.py` (14:46:15), `argus/cost/exhaustion.py` (14:44:28),
`argus/ledger/critical_subsystems.py` (21:48:02), `tests/cartridges/_registry.py` (14:53:04 — and
`CARTRIDGE_REGISTRY` gained no row). `argus/cli.py` is also mtime-clean (2026-08-03 07:37:48).

### Completion Notes List

**What changed, and why it is the smallest change that closes DR-11.** Two source files, prose and branch
structure only. No new module, no CLI flag, no schema bump, no field, no dependency. `Verdict` (3),
`DecisionRow` (4), `VERDICT_SCHEMA_VERSION` `"2"`, `CRITICAL_SUBSYSTEMS_SCHEMA_VERSION` `"2"`, the exit-code
map and the stdout summary line are all untouched (D8 held). The only new symbol is `ShipReadinessError`.

1. **`argus/reports/plain_english.py`** — `_headline` now has one branch per FR16 row. The
   `INSUFFICIENT_COVERAGE` arm splits on **`AuditVerdict.is_below_floor`** (D1 — never on `decision_row`,
   never on a re-derived ratio), and the unreachable `NOT_READY ∧ blocking == 0` predicate is gone. Its
   prose was RELOCATED, not deleted (D2): the `NOT VOUCHED` sentence is now FR16 row 4's, where it is true
   and reachable, with the single widening the 5/5-deep measurement forces — *"a coverage gate"* →
   *"a coverage or critical-subsystem gate"*. Rows 1, 2 and 3 are **byte-identical** to their pre-story
   text, which is what keeps the untouched pins in `test_plain_english.py` green. The impossible input is a
   typed `ShipReadinessError(ValueError)` — never a silent default, never the original bug string
   `BLOCKED — 0 verdict-blocking finding(s)`. The module still imports **only**
   `argus.verdict.verdict_gate`; its docstring gained the four-row table and the no-fork rule.
2. **`argus/reports/generator.py`** — the verdict block is now **four arms that are exactly the four FR16
   rows**: `RELEASE_READY` (row 3, unchanged) → `is_below_floor` (row 1, 8.1's, unchanged) →
   `blocking_finding_count > 0` (row 2) → `else` (row 4). Row 2 names **only** the finding; the coverage and
   critical clauses are gone from its reason list and it emits no dilution hint (D3 — the table
   short-circuited there, so those gates were never evaluated and cannot be reasons). Row 4's
   `[!CAUTION] Repository is NOT ready for release — …` is replaced by
   `[!WARNING] Release readiness is NOT VOUCHED — Argus found nothing blocking, but <the gates actually
   unmet>. This is a statement about the audit, not about the code.` — `WARNING` deliberately matching
   row 1's severity so the two `INSUFFICIENT_COVERAGE` rows differ only in words (boundary B4). The register
   matches `negative_assurance._assurance_statement`'s already-landed row-4 sentence, so one run's two
   artifacts now describe it the same way (D4).
3. **AC8** — `_render_test_dilution_hint` takes the `ast_index` `render_final_verdict_report` already
   receives and calls `is_test_file(path, ast_entry=…)`, the same call `pipeline._assessment_scope_paths`
   makes. No public signature changed, no second predicate was written, `pipeline.py` was not touched, and
   `ast_index=None` keeps the previous name-only behaviour byte-for-byte.
4. **AC7** — the `--exclude-critical` guidance now says that files Argus can never grade `audited_deep`
   (test files, clean-parsed zero-definition modules) are already removed automatically by FR4/DR-5, so
   every listed row is a real work item — and states the one exception, that an operator's own
   `--critical-subsystem` designation is exempt from that removal (DR-6). Every new sentence in both files
   was checked against all six `_FALSE_POSITIVE_CLAIMS` substrings; `TC-ArgusAgent-PIPELINE-002-07` (the
   keystone) is green untouched, and `TC-ArgusAgent-REPORT-002-18` adds an independent check of the same
   six phrases on an empty-critical-set row-4 document.

**Branch-by-branch dead-code audit (AC6 — "do not trade one piece of dead code for another").**

*Made unreachable by this delta → REMOVED:*

| Branch | Disposition |
|---|---|
| `_headline`'s trailing `NOT VOUCHED` else (fires only on `NOT_READY ∧ blocking == 0`) | prose relocated to row 4; predicate replaced by the TYPED raise, which is reachable-by-contract-violation and pinned by `-002-16`. Not dead code: it is tested. |
| `_render_test_dilution_hint`'s `if verdict.blocking_finding_count > 0: remaining.append(…)` | REMOVED — row 2 no longer calls the hint at all, so the clause had no producer. The `remaining` list collapsed with it to a two-way `caveat`, since only the critical clause can survive. |
| `_render_test_dilution_hint`'s `if verdict.verdict is Verdict.RELEASE_READY: return []` guard | REMOVED. It was already *redundant* pre-story (the `deep_ratio >= threshold` guard two lines below catches every case it caught); after the split it is *unreachable*, because both surviving call sites are `INSUFFICIENT_COVERAGE` arms. Recorded per the task's "audit the two early-return guards the same way". |
| `detail = "; ".join(reasons) if reasons else "a release gate was not satisfied"` | REMOVED. Row 4 is the negation of row 3's conjunction over the same assessed ratio the gate used, so at least one of the two clauses always holds and `reasons` cannot be empty. Deliberately NOT replaced by a defensive fallback string: a fallback for a state the gate cannot produce is precisely the silent default this epic deletes. |

*Audited and KEPT — each proven reachable by a committed test:*
`coverage_scope is not None` (`-002-07`, a scoped run) · `deep_ratio >= RELEASE_READY_DEEP_THRESHOLD`
(`-002-20` critical case: row 4 at 5/5 deep, where coverage is NOT what was unmet) ·
`not application or held_out == 0` (`-002-18`, an all-application ledger) · `app_ratio < threshold`
(`-002-06`) · `_render_critical_blockers`' `if not blockers: return []` (`-002-18`) ·
`_MAX_LISTED_CRITICAL_BLOCKERS` truncation (pre-existing pin). The **row-1 arm's** call to the dilution hint
is reachable (dilution can push a repo under the FLOOR, not just under the threshold — e.g. 3 deep app files
among 20 test files gives whole `3/23 < 1/5` with app `3/3 ≥ 3/5`) but has no dedicated committed pin. That
branch is 8.1's and this story did not make it unreachable, so DR-11's rule does not bite; noted here rather
than silently expanding the delta.

**Deviations from the story's proposed shape, and why.**
- The story sketched `raise ShipReadinessError(...)` under `if verdict.blocking_finding_count < 1:` — kept
  exactly. The message names the typed reason only (`NOT_READY_FOR_RELEASE with blocking_finding_count=0:
  FR16 row 2 is the only producer of this verdict and it requires at least one verdict-eligible finding`) —
  no source byte, no path (NFR-S1), asserted by `-002-16`.
- **No shared "which gate" helper was extracted** (Task 2's last subtask, left to judgement). There is no
  duplication to remove: the headline names the gate CLASS, `generator.py` names the specific gate with its
  ratio, and it does so in one place. A helper with one caller is indirection, not DRY (KISS/YAGNI). If a
  second consumer appears it belongs in `plain_english.py` and is imported downward, never the reverse (D4).
- The row-3 arm's `verdict.verdict.value == "RELEASE_READY"` became `verdict.verdict is
  Verdict.RELEASE_READY`. Behaviour-identical, no rendered string moves; it keeps the `Verdict` import
  load-bearing after the hint's enum guard was removed and matches how every other branch in both modules
  reads the enum.
- **AC10/AC11's new tests went into a NEW module**, `tests/test_report_surface_consistency.py`, rather than
  into `test_report_honesty.py` (the story left the choice open and asked that it be stated). Their subject
  is the relationship BETWEEN the two surfaces plus the generator's purity, which is not
  `test_report_honesty.py`'s subject (does the block message name the right gate). The new file is
  `git add`-ed.
- Three pre-existing `test_plain_english.py` cases (`…scoped_verdict…`, `…scope_suggestion…`,
  `…next_step_appears_for_the_critical_clause…`) used the helper's default zero-finding
  `NOT_READY_FOR_RELEASE` fixture — the state the renderer now refuses. They pass `blocking=1` explicitly
  now. **Not a weakening:** every assertion is unchanged, and the fixture moved from a state the gate cannot
  produce to one it can. Their subjects (scope disclosure, `Next:` advice) are row-independent.
- `test_insufficient_coverage_reads_as_not_assessed_never_as_a_defect` was SPLIT as the story's work-list
  directed, into `-002-14` (row 1 vs row 4 read differently; row 1 byte-identical), `-002-15` (the
  `decision_row=None` pre-amendment payload still renders row 1) and `-002-17` (its original subject, now
  asserted over all THREE real `INSUFFICIENT_COVERAGE` folds instead of one hand-built verdict).

**Conflict-resolution record (project standard vs best practice).** D3 — one could argue "more information
is better" and keep the coverage/critical clauses on a row-2 report as context. The **project standard
wins**: PRD FR16's binding contract is that a verdict asserts exactly one thing, and cross-cutting concern
#6 (the false-accusation moat) forbids attaching claims the tool did not make. The clauses are dropped from
row 2. Recorded per the conflict rule, as D3 requires.

**Deliberately NOT done** (each recorded, none silently dropped): naming the *vacuously satisfied* critical
gate in prose (D5 — examined, declined, and filed as the new ledger entry **DF-8-3-A** per AC15(d), with the
six CC-3 fields, targeted at the story that performs the DF-8-2-A extraction); the `pipeline.py` shell-helper
extraction (D6 — the trigger never fired because this story does not edit `pipeline.py`; carried forward
append-only); the `_UNAMBIGUOUS_TEST_SUFFIXES` separator fix (D7 — conditional target, condition not met;
carried forward append-only); the pre-existing observations the story listed as out of scope — `Fraction(5,5)`
rendering as `1`, and `plain_english`'s `Next: --coverage-scope application` line firing for a row-2 run
(advice, not a causal claim; considered and left, as the story invited, with no disagreement to record).

**AC-by-AC:** AC1 `-002-10` · AC2 `-002-10`/`-002-11`/`-002-16`/`CLI-001-32` · AC3 `-002-12` (re-point,
subject kept, precision gained) · AC4 `-002-13`/`-002-14`/`-002-15`/`-002-17` (`test_plain_english.py`) ·
AC5 `-002-20` (RED-first, output above) · AC6 `-002-24` (`test_report_honesty.py`, renumbered from `-002-17`
at R2) + the branch audit · AC7 `-002-18`/`-002-19` + `PIPELINE-002-07` green ·
AC8 `-002-23` · AC9 `CLI-001-31` (`-30` untouched) · AC10 `-002-22` + the import checks above ·
AC11 `-002-21` (extended at R1 — pointer resolution) · AC12 §7 above · AC13 §6 above · AC14 §8 above ·
AC15 the four ledger edits.

---

### Review round 2 — the two open findings, resolved (2026-08-06)

**R1 [Med] — RESOLVED. Route (a), extended to EVERY row.** Reproduced first, exactly as the reviewer
described, on a row-2 fold (3/5 deep, 1 AST finding, `critical_subsystems_not_deep=("src/m4.py",)`):

```
row: row_2_blocking_findings  blocking: 1
occurrences of 'critical' in document: 0
'Ship-readiness: BLOCKED — 1 verdict-blocking finding(s) must be resolved.'
'  - Verdict-blocking findings: 1'
'  - Deeply examined: 3 of 5 files (3/5) — whole repository, test files included'
'  - Critical files not examined deeply: 1'
'  Next: see the final-verdict report for the named critical files and their actual depth; `--exclude-critical <path>` removes one that is not genuinely critical'
```

RED capture of the extended `-002-21` against the pre-fix code, verbatim:

```
FAILED tests/test_report_surface_consistency.py::test_TC_ArgusAgent_REPORT_002_21_all_four_rows_agree_across_both_surfaces
E  AssertionError: row_1_below_floor: `Next:` points at a section this run's document does not
   contain — 'Next: see the final-verdict report for the named critical files and their actual depth;
   `--exclude-critical <path>` removes one that is not genuinely critical'
   -> '### Critical subsystems below `audited_deep`'
```

*Why route (a) and not (b).* Route (b) — making `plain_english`'s `Next:` line conditional — makes the two
surfaces agree by **removing information from the honest one**. It also does not go where the reviewer's own
reasoning leads: the pointer is emitted whenever `critical_subsystems_all_deep` is False, which is rows 1,
2 **and** 4, so (b) would have to suppress the only actionable next step on two of the three rows that have
one — while the counter line `- Critical files not examined deeply: N` stays, naming a quantity with
nothing behind it. That is a *quieter* contradiction, not a resolved one. Route (a) restores the work list,
and the operator on a row-2 run gets what they had before Story 8.3 landed. **Weighed and rejected:** a
third option, dropping the counter line too, was declined — it is a restatement of a counter on the verdict,
which is precisely what this module's docstring says every line must be.

*Measured while fixing it: the defect was WIDER than reported.* **Row 1 has the same dangling pointer**, and
it is not a Story-8.3 regression — Story 8.1 created the `elif verdict.is_below_floor` arm and moved row 1
out of the `else` that carried `_render_critical_blockers`, so a below-floor run with an unmet critical
clause has been pointing at a section its own document does not contain since 8.1. Both are fixed, because
the instruction and DR-11 both say the surfaces must agree *for every row*, and fixing one row while leaving
the identical defect on its neighbour would leave the closing test asserting less than it can.

*The shape.* `_render_critical_blockers` is **hoisted out of the arms** and called once below the four-row
chain, for every row with a non-empty set. Only its **lead sentence** is row-dependent, and it is supplied
by the arm — so the row decision still happens in exactly one place (§3.3 / AR7: no second derivation of the
row inside the helper):

- row 4 — `_CRITICAL_LEAD_CAUSAL` = `These withheld \`RELEASE_READY\` (FR16).` — **byte-identical to today's**;
- rows 1, 2 (and vacuously row 3, whose set is always empty) — `_CRITICAL_LEAD_NOT_THE_CAUSE` =
  *"Not the reason for this verdict — that is stated in the callout above. Listed because the clause is
  still unmet and will withhold `RELEASE_READY` once the stated reason is resolved."*

The non-causal lead is what keeps R1's fix from re-opening AC6: a work LIST is not a reason CLAUSE, and the
lead says so in as many words. **AC6's cleanup is intact and re-pinned** — the row-2 document still contains
no coverage clause, no `critical subsystem is not audited deep` clause and no dilution NOTE (`-002-24`
asserts all three, unchanged, and now also asserts the causal lead is ABSENT there).

*Blank-line handling.* The hoisted call adds a separating blank line only when `lines[-1] != ""`, so the
row-4 and row-1 documents are **byte-identical to before this fix** (both arms already end on a blank line,
with or without the dilution hint); only rows that previously rendered nothing gain the section.

*Incidental fix, recorded.* The AC7 guidance was hard-wrapped across eight list items, which put every
phrase `-002-19` asserts across a newline — the re-wrap broke `already dropped from the heuristic critical
set` for reasons that had nothing to do with the words. It is now ONE Markdown paragraph in one string
constant (`_CRITICAL_LIST_GUIDANCE`); the prose is unchanged word-for-word, and `PIPELINE-002-07` (the
`_FALSE_POSITIVE_CLAIMS` keystone) is green.

*The net the reviewer asked for.* `-002-21` now (i) puts an unmet critical clause on **every** row that can
carry one (row 3 cannot — `RELEASE_READY` requires `critical_subsystems_all_deep`), (ii) asserts through
`_assert_every_pointer_resolves` that **every `Next:` line referencing the final-verdict report resolves
inside the same run's document**, with a registry (`_REPORT_POINTERS`) that **fails an unregistered
pointer**, so a future `Next:` line cannot reference the report without proving the reference lands, and
(iii) asserts the causal lead appears on row 4 and **only** on row 4.

**R2 [Low] — RESOLVED.** `tests/test_report_honesty.py::test_TC_ArgusAgent_REPORT_002_17_row_2_names_only_the_findings`
→ `…_002_24_row_2_names_only_the_findings` (docstring id updated, renumber reason recorded in it). The
honesty file's `-002-18`/`-002-19` are left where they are — the reviewer allowed either, and moving green
pins for tidiness would add diff for no assertion. `test_plain_english.py` keeps `-002-17`. The AC map above
is now unambiguous (AC4 → `-002-17` in `test_plain_english.py`; AC6 → `-002-24` in `test_report_honesty.py`).
`deferred-work.md`'s DF-8-1-A closure note names `-002-20`, not `-002-17`, so no ledger edit was required —
verified by grep, and the ledger is untouched this round.

**R3 / R4 — NOT this round's work** (deferred by the reviewer as DF-8-3-B and DF-8-3-C). Neither was touched.

**Whole-system re-measurement after the round-2 delta (nothing adjusted to make it a value — B1):**

```
PYTHONIOENCODING=utf-8 python -m pytest tests/ --tb=no
    →  3 failed, 1124 passed in 187.25s   (1127 collected, 0 skipped)
       FAILED tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation
       FAILED tests/test_dogfood_plan.py::test_budget_reuses_the_31_accountant_no_fork
       FAILED tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run
python -m mypy argus                       →  Success: no issues found in 69 source files
wc -l  argus/reports/generator.py 613 · argus/reports/plain_english.py 258 · argus/pipeline.py 1199
live `python -m argus.cli audit .`         →  exit 0
  stdout: verdict=RELEASE_READY deep_ratio=57/148 blocking_findings=0 assessed_deep_ratio=57/73 scope=application held_out=75
  stderr: Ship-readiness: READY — no blocking problems found, and enough of the code was examined deeply to say so.
            - Verdict-blocking findings: 0
            - Deeply examined: 57 of 73 assessed files (57/73) — scope 'application', 75 held out (test_files)
            - What `audited_deep` means in this run: … (unchanged disclosure)
```

The three reds are EXACTLY the adjudicated carve-out, unmodified. The live audit is identical to the
reviewer's own run (`RELEASE_READY` / exit `0` / row 3 / assessed `57/73` / 0 blocking).

⚠️ **Counts moved from the reviewer's 1126/1123 to 1127/1124, and NOT because of this round.** A CONCURRENT
session edited this working tree while this fix round ran: `argus/audit/minions_llm_adapter.py` and
`tests/test_no_web_imports.py` became modified and a Story 9.1 file appeared, none of which were dirty at
the start of this round. `tests/test_no_web_imports.py` went from 12 test functions at `HEAD` to 13 — that
is the +1 collected and the +1 passed. **This round added ZERO test functions** (proven: the two files it
touched hold 4 and 12 test defs both before and after — `-002-17`→`-002-24` is a rename and `-002-21` was
extended in place), so the delta is not attributable to it. Recorded rather than absorbed, per the
"any fourth red is yours" rule and its converse: an unexplained count movement is not a pass.

**Fences re-verified after the round-2 delta:** `argus/pipeline.py` 1199 lines, md5
`399d6da1d36d668352fd7b0d539cc307` (unchanged); `argus/cli.py`, `argus/__init__.py`,
`argus/detectors/vacuous_test.py`, `argus/verdict/*`, `_bmad-output/**/minions-dogfood-proof.md` and both
`final-verdict.md` artifacts: not opened, not edited. `argus/reports/plain_english.py` is **unchanged this
round** — the fix is entirely on the generator surface plus tests.

### File List

Modified:

- `argus/reports/plain_english.py` — `ShipReadinessError`; `_headline` restructured to one branch per FR16
  row with the row-1/row-4 split on `is_below_floor`; `NOT VOUCHED` prose relocated + widened; module and
  `render_ship_readiness` docstrings updated. No import added.
- `argus/reports/generator.py` — four-arm FR16 branch block (row-2 and row-4 arms split out of the old
  `else`); row-4 `NOT VOUCHED` callout replacing the false block sentence; row-2 reason list reduced to the
  finding; `_render_test_dilution_hint` takes `ast_index` and uses `is_test_file(…, ast_entry=…)`, drops two
  now-unreachable branches and re-words the caveat; `_render_critical_blockers` guidance rewritten (AC7).
  No import added. **Review round 2 (R1):** `_render_critical_blockers` gains a required `lead` keyword and
  is hoisted out of the four arms so it renders on EVERY row with a non-empty set; two lead constants
  (`_CRITICAL_LEAD_CAUSAL`, byte-identical to the previous sentence, and `_CRITICAL_LEAD_NOT_THE_CAUSE`) and
  `_CRITICAL_LIST_GUIDANCE` (the row-independent prose, re-flowed into one paragraph, words unchanged) added.
  Still no import added.
- `tests/test_plain_english.py` — `TC-ArgusAgent-REPORT-002-10`…`-17` added/re-pointed; real-fold helpers
  (`_ledger`, `_fold`) reusing `tests.test_verdict_gate._ast_finding`; three fixtures moved off the
  impossible verdict.
- `tests/test_report_honesty.py` — `-002-05`'s caveat literal re-pointed; `-002-03` strengthened with the
  verbatim row-2 callout; `TC-ArgusAgent-REPORT-002-17`/`-18`/`-19` added. **Review round 2:** `-002-17`
  renumbered to `-002-24` (R2, duplicate id) and strengthened (R1) — it now also pins that the row-2 work
  list IS rendered, names the file, and carries the NON-causal lead.
- `tests/test_cli.py` — `TC-ArgusAgent-CLI-001-31` (non-row-2 golden stdout + the stdout/stderr register
  split) and `TC-ArgusAgent-CLI-001-32` (the typed refusal degrades to exit 1) added. `-30` untouched.
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — DF-8-1-A closure note; DF-8-2-A and DF-8-2-B
  carry-forward notes; new entry DF-8-3-A. All append-only (§3.4).
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — this story `ready-for-dev` →
  `in-progress` → `review`.
- `_bmad-output/design-artifacts/ArgusAgent/stories/8-3-plain-english-report-stops-describing-impossible-state.md`
  — Status, Tasks/Subtasks, Dev Agent Record, File List, Change Log.

Added (`git add`-ed):

- `tests/test_report_surface_consistency.py` — `TC-ArgusAgent-REPORT-002-20`…`-23`: the DF-8-1-A closer, the
  four-row cross-surface net, the generator determinism + secret-safety pin, and the AC8 classification pin.
  **Review round 2 (R1):** `-002-21` extended — every row that can carry an unmet critical clause now does,
  `_REPORT_POINTERS` + `_assert_every_pointer_resolves` assert that every `Next:` pointer into the report
  resolves in the same run's document (an unregistered pointer fails), and the causal lead is pinned to row 4
  only.

Deleted: none.

---

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-08-06 | 1.1 | **Addressed code review iteration 1 — 2 of 2 open findings resolved (R3/R4 were deferred by the reviewer as DF-8-3-B / DF-8-3-C and are not this round's work).** **R1 (Med)** — the four-arm split had dropped `_render_critical_blockers` from FR16 row 2 while `render_ship_readiness` kept printing `Critical files not examined deeply: N` and `Next: see the final-verdict report for the named critical files`: one surface pointed at a work list the other no longer contained. Reproduced first (row-2 fold, 3/5 deep, 1 AST finding, one unmet critical → **zero occurrences of "critical" in the whole document**), then captured RED through the extended `-002-21`, verbatim in the Dev Agent Record. **Route (a) chosen and recorded**: `_render_critical_blockers` is hoisted out of the arms and rendered for EVERY row with a non-empty set, with the ONLY row-dependent sentence — its lead — supplied by the arm, so the row is still decided in exactly one place (§3.3/AR7). Row 4 keeps the byte-identical causal lead `These withheld \`RELEASE_READY\` (FR16).`; rows 1 and 2 get an explicitly NON-causal lead, which is what keeps AC6 intact — a work LIST is not a reason CLAUSE, and the row-2 document still carries no coverage clause, no critical clause and no dilution NOTE. Route (b) (suppressing the `Next:` pointer) was weighed and rejected: it makes the surfaces agree by deleting the only actionable next step from the honest one, on two rows, while leaving the counter that names the quantity. **Measured while fixing: row 1 has the identical dangling pointer and has had it since Story 8.1 split the below-floor arm out of the `else` — fixed too, because DR-11/B4 require agreement on EVERY row.** The reviewer's requested generalisation landed: `-002-21` now puts an unmet critical clause on every row that can carry one and asserts through `_REPORT_POINTERS` / `_assert_every_pointer_resolves` that every `Next:` line referencing the report resolves in the same run's document, failing an UNREGISTERED pointer so a future one cannot slip through. Row-4 and row-1 documents are byte-identical to before (the separating blank line is added only when the previous line is not already blank). Incidental, recorded: the AC7 guidance was re-flowed from eight hard-wrapped list items into one Markdown paragraph constant, words unchanged, because every phrase `-002-19` asserts straddled a newline. **R2 (Low)** — `test_report_honesty.py`'s `TC-ArgusAgent-REPORT-002-17` renumbered to `-002-24` (`test_plain_english.py` keeps `-002-17`), restoring `TC-<AREA>-<SEQ>-<SUBSEQ>` uniqueness and disambiguating the AC map (AC4 → `-002-17`, AC6 → `-002-24`); `deferred-work.md` names `-002-20` for the DF-8-1-A closure, so no ledger edit was needed and the ledger is untouched this round. `argus/reports/plain_english.py` unchanged this round. Fences re-verified: `argus/pipeline.py` still 1199 lines, md5 `399d6da1d36d668352fd7b0d539cc307`; `argus/cli.py` and every other AC14 path untouched. Whole system re-run after the delta — counts, `mypy` and the live `argus audit .` recorded in the Dev Agent Record; the only reds remain the three adjudicated carve-out tests. Status: review. | Dev Agent (dev-story, fix round 2) |
| 2026-08-05 | 1.0 | **DR-11 delivered on BOTH report surfaces; DF-8-1-A CLOSED.** Every SM figure re-derived IN PLACE before any code changed — 270-fold sweep identical (0 occurrences of `NOT_READY ∧ blocking == 0`), the 4×2 rendered-row table reproduced, the row-2 contamination reproduced verbatim, and the classification disagreement re-measured at exactly 1 of 147 files (`argus/detectors/vacuous_test.py`). `argus/reports/plain_english.py`: `_headline` now has one branch per FR16 row, splitting `INSUFFICIENT_COVERAGE` on `is_below_floor` (D1); the unreachable `NOT VOUCHED` predicate is deleted and its prose RELOCATED to row 4 (D2) with the one widening the 5/5-deep case forces (`a coverage gate` → `a coverage or critical-subsystem gate`); the impossible input is the new typed `ShipReadinessError(ValueError)`, never a silent default. Rows 1/2/3 byte-identical. `argus/reports/generator.py`: four arms that are exactly the four FR16 rows; row 2 names ONLY the finding (D3 — the short-circuited table never evaluated the other gates) and emits no dilution NOTE; row 4's `[!CAUTION] Repository is NOT ready for release …` is replaced by `[!WARNING] Release readiness is NOT VOUCHED — Argus found nothing blocking, but …`, matching `negative_assurance`'s row-4 register (D4); `_render_test_dilution_hint` now classifies with `is_test_file(…, ast_entry=…)` off the `ast_index` it was already handed (AC8), and the AC7 `--exclude-critical` guidance is corrected including the DR-6 exemption. Four branches this delta made unreachable were REMOVED, not left as dead code, and every retained guard is proven reachable by a named test — the audit is recorded branch-by-branch. RED-first evidence captured verbatim for AC5/AC6. Tests: `TC-ArgusAgent-REPORT-002-10`…`-23` (new module `tests/test_report_surface_consistency.py` for the cross-surface net + the generator determinism/secret pin — a measured gap), `TC-ArgusAgent-CLI-001-31`/`-32`; `-002-05`'s literal re-pointed, `-002-03` strengthened, `test_zero_finding_block_does_not_read_as_a_defect_claim` re-pointed to a real row-4 fold with its subject intact. Whole-system: **1126 collected / 1123 passed / 3 failed / 0 skipped** — the three reds are EXACTLY the adjudicated carve-out (2 inherited `test_dogfood_plan`, 1 deliberate `test_dogfood_proof` owned by Story 8.5), nothing deleted, skipped or weakened; `mypy` clean (69 files); no file over 1200 lines. **`argus/pipeline.py` NOT touched — still 1199 lines, byte-identical (DF-8-2-A carried forward append-only, AC15b)**; every AC14 fence verified per path. Live `argus audit .` recorded verbatim and unadjusted: `RELEASE_READY` / exit `0` / `row_3_gates_met` / assessed `57/73` / 0 blocking (B1). Ledger: DF-8-1-A closed with named evidence, DF-8-2-A and DF-8-2-B carried forward, and **DF-8-3-A filed** for D5's declined vacuity prose. Status: review. | Dev Agent (dev-story) |
| 2026-08-05 | 0.1 | Story drafted from the Epic-8 delta (DR-11 + boundary B4 + DF-8-1-A). **Blast radius MEASURED IN PLACE on the real working tree** (`d:/ProjectX/XAgents/XAgents/ArgusAgent`, HEAD `9109e16` + 8.1's and 8.2's uncommitted deltas, `.git` and `_bmad-output/` present) by importing the shipped `argus` functions — explicitly NOT on a scratch copy, the method that cost 8.1 a review round. Findings: all four FR16 rows rendered through BOTH surfaces; row 4 renders the row-1 sentence on both (measured at 2/5 deep AND at **5/5 deep**, where the report claims too little was examined while 100 % of files reached `audited_deep`); DF-8-1-A reproduced verbatim; the `NOT VOUCHED` branch proven unreachable by a **270-fold exhaustive `evaluate_verdict` sweep** (0 occurrences of `NOT_READY ∧ blocking == 0`); a **second, previously unnamed defect** found — a row-2 run appends coverage/critical clauses the short-circuited table never evaluated, plus a false "this coverage result is driven by test-file dilution" NOTE; a **third** found — `generator.py:67` classifies test files by name only while `pipeline.py:692` uses `ast_entry=`, measured to disagree on exactly **1 of 147** files on this repo (`argus/detectors/vacuous_test.py`). Baseline re-measured: **1111 collected / 1108 passed / 3 failed / 0 skipped** (the adjudicated carve-out only), `mypy` clean (69 files), `pipeline.py` **1199** lines. ACs 6, 8, 10, 11, 12–15 added at story design over the epic's six, each with its measured justification; eight LOCKED decisions (D1–D8) recorded with rationale and rejected alternatives. **DF-8-1-A confirmed against `epics.md` and PULLED IN (AC5/AC2, closed by AC15a). DF-8-2-A NOT closed — this story does not edit `pipeline.py` at all (AC14 fences it, AC15b carries it forward append-only). DF-8-2-B NOT pulled in — its ledger target is conditional on editing `argus/detectors/vacuous_test.py`, which this story does not (D7).** Status: ready-for-dev. | Scrum Master (create-story) |
