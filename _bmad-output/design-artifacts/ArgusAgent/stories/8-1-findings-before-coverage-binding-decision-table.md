---
baseline_commit: 9109e16b4e86436a8315ed2cb967b75cdced4296
---

# Story 8.1: Findings before coverage — the binding decision table

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **ArgusAgent story — Argus repo, `argus/` tree only.** ArgusAgent (formerly APAA) is a self-contained
> headless audit tool that has been **extracted from the Minions monorepo** into its own repository
> (`Agent-Argus`, distribution `argus-agent`, package `argus/`, console scripts `argus` / `argus-agent` /
> `repo-audit`). **RS-1 is binding on this story: all work lands in `argus/` in THIS repo. The
> `minions_core/apaa/` copy in the Minions repo is legacy — no modification, no back-port, no dual
> maintenance.** Planning artifacts live under `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is
> `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`. Prose in older documents that says
> `design-artifacts/APAA/` or `minions_core/apaa/` should be read as `design-artifacts/ArgusAgent/` /
> `argus/` (RS-4b, the bulk provenance sweep, is deliberately deferred out of this delta).
>
> **This is the FIRST story of Epic 8** ("The Honest Verdict — no block without a finding"), the delta epic
> created by the **2026-08-03 FR16/FR4 verdict-contract amendment**. Epics 1–7 are **delivered** (1262
> passing tests at the epic-7 capstone) and are NOT regenerated. `epic-8` moves to `in-progress` with this
> story.
>
> **THIS STORY DELIVERS DR-1, DR-2, DR-3, DR-4 and DR-9** — the reordered binding decision table (findings
> evaluated *before* coverage), the new row 4 (`INSUFFICIENT_COVERAGE` / exit `3` for a zero-findings unmet
> gate), the decision-row disclosure on the verdict artifact, the `VERDICT_SCHEMA_VERSION` `"1"` → `"2"`
> bump, and the proof that those are the **only** intentional content-hash change.
>
> **It does NOT deliver:** DR-5/DR-6/DR-7 (critical-set eligibility — Story 8.2), DR-11's report-surface
> *wording* reconciliation and the `plain_english.py` unreachable-branch audit (Story 8.3), DR-8 + RS-4a
> (release note / package front door — Story 8.4), DR-10 (dogfood re-derivation — Story 8.5, deliberately
> last so a slip is visible).

## Story

As an **operator running `argus audit` on a repository where Argus found nothing wrong** — who today
receives `verdict=NOT_READY_FOR_RELEASE deep_ratio=11/28 blocking_findings=0`, a blocking word beside a zero
blocking count, and who must then explain to their team a "defect" the tool never actually found —

I want **the verdict gate to evaluate findings BEFORE coverage**, so that a blocking verdict is emitted
**only on the strength of a finding Argus actually made**, every other withheld-`RELEASE_READY` outcome is
reported as the honest not-assessed state `INSUFFICIENT_COVERAGE` (exit `3`), and the verdict artifact
**discloses which decision row fired** and the population it was computed over,

so that **a coverage shortfall is never reported to my team as a defect** — closing the last asymmetry in
cross-cutting concern #6 (advisory-by-contract / the false-accusation moat), which is enforced today on
*findings* but not on the *verdict itself*.

## Story Context

### The bug, precisely

`argus/verdict/verdict_gate.py:511-520` currently evaluates a **three-row** table:

```python
if assessed_total == 0 or assessed_ratio < INSUFFICIENT_COVERAGE_FLOOR:
    verdict = Verdict.INSUFFICIENT_COVERAGE
elif (assessed_ratio >= RELEASE_READY_DEEP_THRESHOLD and blocking == 0
      and critical_subsystems_all_deep):
    verdict = Verdict.RELEASE_READY
else:
    verdict = Verdict.NOT_READY_FOR_RELEASE      # ← the defect: a DEFAULT BLOCK
```

That `else` is the whole bug. Any run at or above the 20% floor that fails **either** the 60% coverage gate
**or** the critical-subsystem clause — **with zero blocking findings** — falls through to
`NOT_READY_FOR_RELEASE` / exit `2`, a verdict whose canonical meaning (PRD, *Verdict vocabulary*) is
"**APAA found something**". It found nothing. That is a false accusation emitted by the tool whose entire
product thesis is that it does not cry wolf.

`INSUFFICIENT_COVERAGE` is **not** a blocking verdict — it is the *not-assessed* state, "I did not examine
enough to vouch". After this story it is reached **two** ways: below the 20% floor (row 1) **or** an unmet
coverage / critical-subsystem gate with zero blocking findings (row 4).

### The binding decision table (FR16 as amended 2026-08-03) — evaluated IN ORDER

| # | Condition | Verdict | Exit |
|---|---|---|---|
| 1 | `assessed_total == 0` or `assessed_ratio < 1/5` | `INSUFFICIENT_COVERAGE` | 3 |
| 2 | `blocking_findings >= 1` | `NOT_READY_FOR_RELEASE` | 2 |
| 3 | `assessed_ratio >= 3/5` **and** all critical subsystems `audited_deep` | `RELEASE_READY` | 0 |
| 4 | otherwise — zero blocking findings, a coverage or critical-subsystem gate unmet | `INSUFFICIENT_COVERAGE` | 3 |

**Row 1 keeps precedence over row 2.** The LOCKED *floor-vs-blocking precedence = FLOOR WINS* invariant
(`verdict_gate.py:51-55`, pinned by `TC-ArgusAgent-VERDICT-001-80`) survives the reorder **unchanged**: below
the floor Argus has not assessed enough to honestly claim it saw enough to BLOCK either.

> ⚠️ **Boundary B2 — the single most likely defect this reorder can introduce.** The story's own headline
> ("findings before coverage") reads as "put the blocking row first", which would put row 2 above row 1 and
> break FLOOR WINS. It must not. "Before coverage" means **before the 60% / critical-subsystem GATES (row
> 3)**, never before the 20% **FLOOR (row 1)**.

### The contracts this story touches — all frozen, all REUSE-not-fork (§3.3 / AR7)

- **`argus/verdict/verdict_gate.py` (Story 1.6, 538 lines).** The PURE terminal fold. It imports **only**
  `argus.ledger.coverage_ledger` and `argus.ledger.recording` — pinned by
  `TC-ArgusAgent-VERDICT-001-96`, which asserts the `argus.*` import set is **exactly** those two. Any new
  import from another `argus` package **fails that test**. Also pinned: no `os`/`time`/`datetime`/`uuid`/
  `random`/`subprocess`/`socket` import (`…-001-95`).
- **`Verdict` enum — MUST NOT GROW.** Exactly three members, pinned by `TC-ArgusAgent-VERDICT-001-01`.
  Adding `COVERAGE_GATE_UNMET` was **explicitly considered and rejected** (PRD addendum §A1 options matrix):
  one value carries one meaning, and the row-1/row-4 distinction is recoverable from the disclosed ratio +
  assessed population. Do not reopen that decision.
- **Exit codes are unchanged as VALUES** — `0`/`2`/`3`/`1` (AR3 wire contract). No new code is introduced;
  what changes is *which runs map to `3` instead of `2`*. `_EXIT_CODE_BY_VERDICT` and
  `exit_code_for_verdict` are untouched.
- **Thresholds are unchanged.** `RELEASE_READY_DEEP_THRESHOLD = Fraction(3, 5)` (**inclusive** `>=`) and
  `INSUFFICIENT_COVERAGE_FLOOR = Fraction(1, 5)` (**strict** `<`). Exact `Fraction`, never `float` (AR4). A
  reorder is exactly when an off-by-one creeps in.
- **`AuditVerdict` is `frozen=True, extra="forbid"`.** ⚠️ **Assumption A8, binding:** the new
  decision-row field **must carry a default**, or a pre-amendment persisted verdict stops round-tripping.
- **The advisory moat is untouched.** `is_verdict_blocking(finding) ⇔ finding.depth_supported is not None`
  (cross-cutting #6) — NOT keyed on `advisory`. This story changes *when* a blocking count moves the
  verdict, never *what counts as blocking*.
- **`order_findings` / FR33 ordering is untouched.**
- **The `coverage_scope` narrowing seam (`scope_paths`) is untouched.** The decision table is evaluated over
  the **assessed** population (`assessed_total` / `assessed_ratio`), exactly as today. `deep_ratio` /
  `deep_count` / `total_count` keep their LOCKED whole-ledger meaning.

### Live consumers of the gate — read before you change anything

`evaluate_verdict` is called from **five** production sites and `AuditVerdict` is read by **nine** modules:

| Module | What it does with the verdict | Impact of this story |
|---|---|---|
| `argus/pipeline.py:698` | the live fold (scoped, with critical flags) | none — call signature unchanged |
| `argus/verdict/prosecutor.py:430` | **re-folds** the refined finding set, then picks the more conservative of (candidate, refold) via `_CONSERVATISM_RANK` | ⚠️ **BREAKS — see AC12.** Runs by default (`"prosecutor"` is in the CLI default pass set) |
| `argus/cost/exhaustion.py:485` | `below_floor = verdict.verdict is INSUFFICIENT_COVERAGE`, documented as "the gate guarantees this equals `deep_ratio < FLOOR`" | ⚠️ **BREAKS — the equivalence is falsified by row 4. See AC13** |
| `argus/verdict/negative_assurance.py:310` | `INSUFFICIENT_COVERAGE` → *"Assessed coverage is below the floor"* — a **persisted artifact string** | ⚠️ **Becomes false for row 4. See AC14** |
| `argus/reports/generator.py:304-337` | branches on the verdict enum; the `INSUFFICIENT_COVERAGE` branch **skips** the gate-naming block and `_render_critical_blockers` | ⚠️ **BREAKS two honesty pins. See AC15** |
| `argus/reports/plain_english.py:109` | `INSUFFICIENT_COVERAGE` headline = *"too little of the code was examined deeply"* | **Out of scope — Story 8.3 owns it (DR-11).** No test fails; see the accepted-transient note in Dev Notes |
| `argus/cli.py:199-224` | the stdout machine summary line | **must stay byte-identical** — AC10 |
| `argus/ledger/coverage_report.py`, `argus/cost/resume.py`, `argus/ledger/critical_subsystems.py`, `argus/governance/escalation.py`, `argus/models.py`, `argus/pipeline_persist.py` | read counters / re-fold / persist | none expected — covered by AC17 (full suite green) |

### Measured blast radius — this is not a guess

The reorder + schema bump + new field were **applied to a scratch copy of the tree and the full suite was
run** (2026-08-04). Result: **exactly 23 tests fail**, in 9 files. Four further failures were confirmed to
be artefacts of the scratch environment (no `.git`, no `_bmad-output/`) and are **not** delta-caused:
`tests/test_dogfood_plan.py`, ~~`tests/test_dogfood_proof.py`~~ **[CORRECTED — see below]**,
`test_secret_containment.py::test_dogfood_bundle_over_real_minions_repo_is_source_free`,
`test_precision_replay.py::test_validation_protocol_document_exists_and_fixes_the_method`.

> ⚠️ **CORRECTION (2026-08-04, dev fix-iteration 2 — review finding R3). The classification of
> `tests/test_dogfood_proof.py` above is WRONG and is struck.** It was measured on a scratch tree that
> had no `.git` / no `_bmad-output/`, which masked the real result. On the real tree
> `tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run` is **GREEN at
> baseline `9109e16`** — independently confirmed by the reviewer in a clean detached `git worktree` — so
> its failure after this delta is **genuinely delta-caused**, not environmental. It is left **red
> deliberately**: it is a rot check on `minions-dogfood-proof.md`, which **AC18 names as
> MUST-NOT-MODIFY** and which is **Story 8.5 / DR-10**'s deliverable. See **Variance V2** in the Dev
> Agent Record for the full reasoning and **Story 8.5** for ownership. `tests/test_dogfood_plan.py`'s two
> failures were confirmed at the same baseline to be **genuinely inherited** and keep their
> classification. Do not consult the un-annotated sentence above — a stale planning artifact is exactly
> the failure mode this epic exists to remove.

**The 23 delta-caused failures — the complete work list.** Every one must end green.

| # | Test | Why it fails | Disposition |
|---|---|---|---|
| 1 | `test_verdict_gate.py::…001_11_not_ready_low_deep` | 2/5 deep, 0 blocking → was NOT_READY | **re-point** to `INSUFFICIENT_COVERAGE` / exit 3 / row 4 |
| 2 | `…001_21_exactly_floor_is_assessable` | 1/5 deep, 0 blocking | **re-point** — and this IS boundary **B4** (row 4, not row 1) |
| 3 | `…001_22_just_below_ready` | 5999/10000, 0 blocking | **re-point** to row 4 |
| 4 | `…001_31_only_deep_counts_toward_numerator` | 3/7, 0 blocking | **re-point** to row 4 (FR8 numerator assertion unchanged) |
| 5 | `…001_32_shallow_does_not_inflate_to_ready` | 1/2, 0 blocking | **re-point** to row 4 |
| 6 | `…001_86_critical_not_deep_withholds_ready` | 3/5 deep, 0 blocking, critical not deep | **re-point** to row 4 — `RELEASE_READY` still withheld, which is the test's real subject |
| 7 | `…001_94_golden_canonical_bytes_stable` | golden bytes lack `decision_row`, carry `schema_version:"1"` | **update the golden** — it is a row-2 case (1 blocking finding), so the verdict itself does NOT change |
| 8–10 | `test_verdict_scope.py::test_test_heavy_repo_is_a_false_negative_without_scope`, `::test_scope_still_applies_the_release_ready_threshold`, `::test_critical_subsystem_clause_still_in_force_under_scope` | zero-blocking gate-unmet cases | **re-point.** Note #8's subject — a *false negative* — is precisely what this amendment removes; keep the test, restate the expectation |
| 11 | `test_critical_subsystems.py::test_fr16_critical_shallow_withholds_release_ready` | zero-blocking critical clause | **re-point** — "withholds RELEASE_READY" still true |
| 12 | `test_depth_semantics.py::test_fr8_inferred_cannot_tip_a_sub_60_ledger_to_release_ready` | zero-blocking sub-60 | **re-point** — FR8 assertion unchanged |
| 13–15 | `test_insufficient_coverage_floor.py::test_above_floor_under_exhaustion_does_not_over_fire`, `::test_above_floor_exactly_20pct_is_not_below_floor`, `::test_below_floor_predicate_agrees_with_deep_ratio_comparison` | `below_floor` now fires above the floor | **FIX THE CODE, NOT THE TESTS** (AC13) — these pin a real invariant |
| 16–17 | `test_pipeline_signature_demo.py::test_e2e_operator_designated_critical_shallow_withholds_release_ready`, `::test_e2e_above_floor_under_exhaustion_does_not_over_fire` | end-to-end zero-blocking cases | **re-point** verdict/exit expectations |
| 18 | `test_prosecutor.py::test_not_ready_candidate_is_never_upgraded` | `_not_ready_ledger()` (2/5, no findings) is now row 4 | **re-point** the fixture to a genuine row-2 candidate (≥1 blocking finding) **and** add the AC12 test |
| 19–20 | `test_report_honesty.py::test_critical_block_names_the_gate_and_the_files`, `::test_designated_critical_absent_from_ledger_is_labelled` | the report drops the critical-blockers section under `INSUFFICIENT_COVERAGE` | **FIX THE CODE, NOT THE TESTS** (AC15) — these are honesty pins |
| 21–23 | `test_cartridge_selfaudit.py::test_golden_key_true_positive[orphan_basic]`, `[vacuous_heuristic_basic]`, `[cross_partition_seam]` | the registry pins `expected_verdict="NOT_READY_FOR_RELEASE", expected_exit=2, **max_blocking=0**` | **re-point the registry** (AC16) — these three cartridges were literally encoding the bug |

**Read row 21–23 carefully — it is the strongest evidence in the story.** Three self-audit cartridges
asserted a *blocking* verdict with `max_blocking=0`. The golden keys had frozen the false accusation into
the trust substrate. Their **required findings do not change** (`orphan_code`, `vacuous_test_heuristic`,
`cross_partition` — all advisory, all `depth_supported is None`, all still emitted); only the verdict/exit
expectation moves. The clean controls (`clean_control`, `hardcoded_secret`, `evidence_sentinel`,
`tool_breadth`) already expect `RELEASE_READY`/exit `0` and **must not move**.

### Pre-existing red — inherited, not caused

`tests/test_dogfood_plan.py` carries **two pre-existing failures** on the clean tree
(`test_committed_partition_plan_artifact_exists_and_matches_live_derivation` and
`test_budget_reuses_the_31_accountant_no_fork` — the committed dogfood plan is stale vs live derivation, and
`431` is absent from the committed budget artifact). They were present at `ae5f00c`, they are **unrelated to
this delta**, and **Story 8.5 explicitly owns the decision to fix or leave them**. This story must **not**
absorb them, must not "fix" them incidentally, and must record their state in the Dev Agent Record so the
delta's result is not silently inflated.

## Acceptance Criteria

**Row semantics (DR-1 / DR-2)**

1. **Given** a ledger with ≥1 verdict-blocking finding at or above the 20% floor,
   **When** the verdict is evaluated,
   **Then** it is `NOT_READY_FOR_RELEASE` / exit `2` and the disclosed row is **row 2** — findings are
   evaluated *before* the coverage GATES, including when the coverage ratio is between the floor and 60%.

2. **Given** a ledger with **zero** blocking findings and an unmet coverage **or** critical-subsystem gate
   (ratio ≥ 20% but < 60%, **or** ratio ≥ 60% with a critical path not deep),
   **When** the verdict is evaluated,
   **Then** it is `INSUFFICIENT_COVERAGE` / exit `3` with disclosed **row 4** — never
   `NOT_READY_FOR_RELEASE`,
   **And** this is demonstrated **RED-first**: a committed test that fails against the current three-row
   implementation before the fix, recorded in the Dev Agent Record (test id + the observed RED output).

3. **Given** `assessed_total == 0` **or** `assessed_ratio < 1/5`,
   **When** the verdict is evaluated,
   **Then** it is `INSUFFICIENT_COVERAGE` / exit `3` with disclosed **row 1** — row 1 keeps precedence over
   the findings row.

4. **Given** a ledger **below the 20% floor that also carries ≥1 blocking finding**,
   **When** the verdict is evaluated,
   **Then** it is `INSUFFICIENT_COVERAGE` with disclosed **row 1**, **never** `NOT_READY_FOR_RELEASE` — the
   LOCKED *floor-vs-blocking precedence = FLOOR WINS* invariant survives the reorder (boundary **B2**).
   `TC-ArgusAgent-VERDICT-001-80` stays green unmodified except for the added row assertion.

5. **Given** a ledger where **every** coverage gate passes (ratio ≥ 60%, all critical subsystems deep) **and
   exactly one blocking finding exists**,
   **When** the verdict is evaluated,
   **Then** it is `NOT_READY_FOR_RELEASE` / exit `2`, disclosed **row 2** — the case a healthy repo actually
   hits.

6. **Given** a ledger at **exactly** `assessed_ratio == 1/5` with zero blocking findings and an unmet gate,
   **When** the verdict is evaluated,
   **Then** the verdict is `INSUFFICIENT_COVERAGE` and the disclosed row is **4, not 1** — the floor is
   strict (`<`), so exactly-20% is assessable. Rows 1 and 4 are otherwise indistinguishable by verdict and
   exit code, which is precisely why the row must be disclosed (boundary **B4**).

7. **Given** the boundary constants,
   **When** the decision table is reordered,
   **Then** they are **unchanged**: `RELEASE_READY` at `assessed_ratio >= 3/5` (**inclusive**) and the floor
   at `< 1/5` (**strict**), both exact `Fraction`s, and `Verdict` still has **exactly three** members.

**Disclosure (DR-3) and schema (DR-4)**

8. **Given** any evaluated verdict,
   **When** the artifact is serialized,
   **Then** it discloses **which row fired** via the new `decision_row` field **and** the **assessed
   population** it was computed over (`coverage_scope` when the assessment was narrowed, otherwise
   `deep_count` / `total_count`),
   **And** the new field carries a **default**, proven by a test that `AuditVerdict.model_validate(...)`
   accepts a **pre-amendment payload with `schema_version: "1"` and no `decision_row` key** under
   `extra="forbid"` (assumption A8),
   **And** a **re-derivation test** proves the disclosure is sufficient: for each of the four rows, the
   fields present on `AuditVerdict` (`decision_row`, the assessed population, `blocking_finding_count`,
   `critical_subsystems_all_deep`) reproduce the verdict and exit code without re-reading the ledger.

9. **Given** the amendment,
   **Then** `VERDICT_SCHEMA_VERSION` is `"2"`, and verdicts already persisted under `.apaa/` / `.argus/` are
   **not rewritten** and keep their `"1"` stamp — no migration code, no rewrite pass, pinned by a test that
   a `"1"`-stamped payload survives read-back with its stamp intact.

10. **Given** the disclosed row must reach a consumer,
    **When** the run completes,
    **Then** it surfaces **per the LOCKED channel decision**: explicitly on the verdict artifact, in prose
    on the stderr human register (**Story 8.3**), and **not** as a new field on the stdout machine summary
    line, which stays **byte-identical** — `verdict=<TOKEN> deep_ratio=<num/den> blocking_findings=<n>`
    (+ `assessed_deep_ratio`/`scope`/`held_out` when narrowed). `argus/cli.py::_summary_line` is not
    modified by this story.

**Determinism (DR-9) and purity**

11. **Given** two evaluations over the same synthetic ledger,
    **When** compared byte-for-byte,
    **Then** they are identical,
    **And** for a fixture repository that lands on **row 2 or row 3** (i.e. whose verdict value does not
    change), every persisted `.argus/` artifact is **byte-identical** pre/post except the verdict envelope,
    which differs **only** by `schema_version` and the added `decision_row` key — the schema bump plus the
    new field are the only intentional content-hash change,
    **And** the gate remains **PURE**: zero LLM tokens, no I/O, no clock, no `uuid`/`random`, no `float`;
    `TC-ArgusAgent-VERDICT-001-95` and `…-001-96` (the `argus.*` import set is **exactly**
    `{argus.ledger.coverage_ledger, argus.ledger.recording}`) stay green **unmodified**.

**Downstream consumers that the reorder breaks — discovered at story design, in scope here**

12. **Given** a **row-4** candidate verdict and a finding the Prosecutor promotes (AST corroboration **and**
    sign-off) so the re-fold carries ≥1 blocking finding,
    **When** `prosecute(...)` runs,
    **Then** the final verdict is `NOT_READY_FOR_RELEASE` (row 2) — the Prosecutor must **never silence a
    finding it just promoted**,
    **And** the FR19 asymmetric-harm rule still holds: the Prosecutor **never** moves a verdict toward
    `RELEASE_READY` (a `RELEASE_READY` re-fold from an `INSUFFICIENT_COVERAGE` candidate is rejected),
    **And** `test_prosecutor.py::test_insufficient_coverage_candidate_is_never_upgraded` (a row-1 candidate)
    stays green.
    *(Root cause: `_CONSERVATISM_RANK` ranks `INSUFFICIENT_COVERAGE` (2) strictly above
    `NOT_READY_FOR_RELEASE` (1). Post-reorder a row-4 candidate outranks its own blocking re-fold, so
    `refolded_rank >= candidate_rank` is False and the blocking verdict is discarded. The rank must express
    "never move toward `RELEASE_READY`" without ordering the two withholding states against each other.)*

13. **Given** the Story-3.3 floor report,
    **When** it is built from a **row-4** verdict,
    **Then** `below_floor` is **False** and the message does not claim the floor was breached — the
    predicate keys on the **disclosed decision row (row 1)**, not on the verdict enum,
    **And** `test_insufficient_coverage_floor.py::test_below_floor_predicate_agrees_with_deep_ratio_comparison`
    and its two siblings stay green **unmodified** (they pin a real invariant; do not re-point them),
    **And** a row-1 verdict produces a **byte-identical** floor report to today.

14. **Given** the negative-assurance statement (a **persisted** artifact string),
    **When** it is built from a **row-4** verdict,
    **Then** it states honestly that no blocking findings were detected within the assessed scope and that a
    coverage or critical-subsystem gate was not met — it does **not** claim "assessed coverage is below the
    floor",
    **And** the **row-1** statement is **byte-identical** to today,
    **And** the `RELEASE_READY` / `NOT_READY_FOR_RELEASE` statements are unchanged, and no statement
    contains a certification / "proven" / "guarantee" / "defect-free" / "passed" token.

15. **Given** `argus/reports/generator.py` — the second verdict-rendering surface, which branches on the
    verdict enum,
    **When** a **row-4** verdict is rendered,
    **Then** the gate-naming block and `_render_critical_blockers` render exactly as they did for the
    pre-amendment zero-findings block (naming the coverage ratio and/or the critical subsystems, listing the
    critical paths with their actual depth), and **row 1** keeps the existing below-floor warning,
    **And** `test_report_honesty.py::test_critical_block_names_the_gate_and_the_files` and
    `::test_designated_critical_absent_from_ledger_is_labelled` stay green **unmodified** (honesty pins —
    fix the code, not the tests).
    ⚠️ **Bounded:** key the branch on the **decision row**; **do not** change any rendered string. The
    wording reconciliation, the "each must reach `audited_deep`" guidance, the empty-critical-set rendering
    and the `plain_english.py` "NOT VOUCHED" branch audit are **Story 8.3 / DR-11** and are explicitly out
    of scope here.

16. **Given** the three self-audit cartridges that pin `expected_verdict="NOT_READY_FOR_RELEASE"`,
    `expected_exit=2` with `max_blocking=0` (`orphan_basic`, `vacuous_heuristic_basic`,
    `cross_partition_seam`),
    **When** the registry is reconciled with the amended table,
    **Then** those three expect `INSUFFICIENT_COVERAGE` / exit `3`,
    **And** their `required_findings` are **unchanged** and still emitted with ≥1 verifiable locator (FR13),
    **And** the clean controls (`clean_control`, `hardcoded_secret`, `evidence_sentinel`, `tool_breadth`)
    and the genuinely-blocking cartridges (`vacuous_basic`, `holdout_vacuous`, `nonascii_unicode`, each with
    `max_blocking=1`) are **unchanged** — the false-green direction must not loosen.

**Whole-system**

17. **Given** the delta has landed,
    **When** the full suite runs (`PYTHONIOENCODING=utf-8 python -m pytest tests/ -q`),
    **Then** all **23** measured delta-caused failures are green, **no test is deleted or weakened**, the
    two **pre-existing** `test_dogfood_plan.py` failures are the only red and are recorded as inherited (not
    fixed, not absorbed — Story 8.5 owns them), `mypy` is clean, and no source file exceeds 1200 lines
    (NFR-M1).

18. **Given** the epic's story boundaries,
    **Then** this story does **not** modify `argus/reports/plain_english.py`, `tests/test_plain_english.py`,
    `argus/ledger/critical_subsystems.py`, `argus/cli.py`, `argus/__init__.py`, or any dogfood/proof
    artifact — those are Stories 8.2 / 8.3 / 8.4 / 8.5.

## Tasks / Subtasks

- [x] **Task 1 — RED first (AC2).**
  - [x] Write the failing test(s) for row 4 (zero blocking + unmet coverage gate; and zero blocking + ratio
        ≥ 60% with a critical path not deep) against the **current** three-row gate; run and capture the RED
        output verbatim for the Dev Agent Record.
  - [x] Write the failing test for AC12 (row-4 candidate + promoted finding → the Prosecutor keeps the
        blocking verdict) — it will be red for a *different* reason before the reorder; note that.

- [x] **Task 2 — Reorder the decision table + disclose the row (AC1–AC8, AC11).** `argus/verdict/verdict_gate.py`
  - [x] Add `DecisionRow(str, enum.Enum)` with **exactly four** members, one per FR16 row (see the LOCKED
        shape in Dev Notes). Export it in `__all__`. Do **not** touch `Verdict`.
  - [x] Add `decision_row: DecisionRow | None = Field(default=None, ...)` to `AuditVerdict` (**default is
        mandatory** — A8). Place it adjacent to `verdict` in the field order; the canonical serializer sorts
        keys, so field order does not affect bytes.
  - [x] Replace the three-row `if/elif/else` with the four-row table **verbatim from FR16**, each branch
        setting both `verdict` and `row`. Row 3's condition is `assessed_ratio >= RELEASE_READY_DEEP_THRESHOLD
        and critical_subsystems_all_deep` — **no redundant `blocking == 0`** clause; add a comment that
        `blocking == 0` is guaranteed by row-2 precedence, and pin it with a test asserting row 3 implies
        `blocking_finding_count == 0`.
  - [x] Bump `VERDICT_SCHEMA_VERSION` to `"2"` (AC9). Do not add migration code.
  - [x] Update the module docstring's decision table + the `evaluate_verdict` docstring to the four-row
        table, and state the row-1-precedence rationale and the assessed-population disclosure rule.
  - [x] Confirm no new import was added (`…-001-95` / `…-001-96` must pass unmodified).

- [x] **Task 3 — Prosecutor: never silence a promoted finding (AC12).** `argus/verdict/prosecutor.py`
  - [x] Rework `_CONSERVATISM_RANK` so it expresses *"never move toward `RELEASE_READY`"* without ranking
        the two withholding states against each other (recommended: `RELEASE_READY: 0`,
        `NOT_READY_FOR_RELEASE: 1`, `INSUFFICIENT_COVERAGE: 1`, keeping the existing `refolded_rank >=
        candidate_rank` comparison so an equal-rank re-fold wins). Update the explanatory comment.
  - [x] Verify the `downgraded` flag still means what it says (it is computed from the same rank; a row-4 →
        row-2 move is a *change*, not a downgrade — decide and document which it is recorded as, and pin it).
  - [x] Re-point `test_not_ready_candidate_is_never_upgraded` to a genuine row-2 candidate (≥1 blocking
        finding) and keep `test_insufficient_coverage_candidate_is_never_upgraded` green as-is.

- [x] **Task 4 — Floor report keys on the row, not the enum (AC13).** `argus/cost/exhaustion.py`
  - [x] `below_floor` ← the disclosed **row 1**, not `verdict is INSUFFICIENT_COVERAGE`. Update the
        docstring, which currently asserts the now-falsified equivalence.
  - [x] Confirm the three `test_insufficient_coverage_floor.py` tests go green **without edits**, and that a
        row-1 report is byte-identical to today.

- [x] **Task 5 — Honest negative-assurance statement for row 4 (AC14).** `argus/verdict/negative_assurance.py`
  - [x] Split `_assurance_statement`'s `INSUFFICIENT_COVERAGE` branch on the decision row: row 1 keeps its
        **byte-identical** existing string; row 4 gets the honest "no blocking findings … a coverage or
        critical-subsystem gate was not met" statement. Keep the `scope_clause` construction identical.
  - [x] Preserve the "no certification token" property and the verdict/floor-report consistency check.

- [x] **Task 6 — Report generator branches on the row (AC15).** `argus/reports/generator.py`
  - [x] Key the verdict branch on the decision row so row 4 takes the gate-naming + `_render_critical_blockers`
        + dilution-hint path and row 1 keeps the below-floor warning. **Change no rendered string.**
  - [x] Confirm both `test_report_honesty.py` pins go green **without edits**.

- [x] **Task 7 — Re-point the pinned expectations (AC1–AC7, AC16, and blast-radius rows 1–12, 16–18, 21–23).**
  - [x] `tests/test_verdict_gate.py` — re-point the 6 zero-blocking cases, add row assertions, regenerate
        `GOLDEN_VERDICT_CANONICAL` (row 2; expect `"decision_row":"row_2_blocking_findings"` and
        `"schema_version":"2"`), add the AC8 round-trip + re-derivation tests, add the AC3/AC6 row-1-vs-row-4
        pair.
  - [x] `tests/test_verdict_scope.py`, `tests/test_critical_subsystems.py`, `tests/test_depth_semantics.py`,
        `tests/test_pipeline_signature_demo.py` — re-point verdict/exit expectations; **keep each test's
        original subject assertion** (FR8 numerator, scope floor re-application, critical clause in force).
  - [x] `tests/cartridges/_registry.py` — re-point the three `max_blocking=0` cartridges to
        `INSUFFICIENT_COVERAGE`/`3`; leave every other spec untouched. Add a comment recording *why* they
        moved.
  - [x] Use the project test-id convention `TC-ArgusAgent-<AREA>-<SEQ>-<SUBSEQ>` for every new test.

- [x] **Task 8 — Determinism + byte-identity proof (AC11).**
  - [x] Two evaluations over one synthetic ledger → identical canonical bytes and identical content hash.
  - [x] A fixture repo landing on row 2 (or row 3): diff every persisted `.argus/` artifact pre/post; only
        the verdict envelope changes, and only by `schema_version` + `decision_row`.
  - [x] Re-run the single-serializer / no-float AST gate and the import-isolation gate with the changed
        modules.

- [x] **Task 9 — Close out (AC17, AC18).**
  - [x] Full suite + `mypy`; record counts, the RED-first evidence, and the two inherited
        `test_dogfood_plan.py` failures verbatim in the Dev Agent Record.
  - [x] Confirm the out-of-scope file list (AC18) shows **no diff**.

### Review Findings

**Code review — 2026-08-04, iteration 1 (BMAD `code-review`, adversarial: Blind Hunter / Edge Case
Hunter / Acceptance Auditor). Verdict: CONCERNS.** The substance of the story is correct and was
verified end-to-end, not just at the unit boundary. Four items remain, none of them blocking the
delta: one delta-caused report-surface contradiction that the story's own AC15 fences to Story 8.3,
and three low-severity cleanups.

**Independent verification performed by the reviewer (do not re-trust the Dev Agent Record — this is
the reviewer's own re-run):**

- **Suite re-run by the reviewer**: `PYTHONIOENCODING=utf-8 python -m pytest tests/ -q` →
  **1073 tests, 1070 passed, 3 failed, 0 skipped** (progress-line character census: 1070 `.`, 3 `F`,
  zero `s`). Matches the Dev's claim exactly. `python -m mypy argus` → `Success: no issues found in
  69 source files`.
- **Baseline claim (b) verified in a clean detached worktree at `9109e16`** (`git worktree add`, so
  the working tree was never disturbed): `tests/test_dogfood_plan.py::…_committed_partition_plan_…`
  and `::test_budget_reuses_the_31_accountant_no_fork` **FAIL at baseline** — genuinely inherited,
  confirmed for the first time by someone other than the Dev. `tests/test_dogfood_proof.py::…` is
  **GREEN at baseline** — so Variance V2 is correct and the story's own blast-radius table
  (classifying that file as "environment-only") is wrong. See finding R3.
- **No fourth red, no deletion, no weakening (c) verified.** `pytest --collect-only` at baseline vs
  working tree: **1051 → 1073** collected, **67 → 68** test files, and **no file lost a single
  test** (`test_cli.py` 8→9, `test_prosecutor.py` 17→19, `test_verdict_gate.py` 40→56,
  `test_verdict_schema_bump.py` 0→3; every other file unchanged). Zero skips in the whole run. Every
  re-pointed assertion was read: each one keeps its original subject and adds a `decision_row`
  assertion that is strictly *more* specific than what it replaced (rows 1 and 4 share a verdict
  value, so the row assertion is stronger than the enum assertion it replaced).
- **AC11's "empirical proof" is genuine, not circular — verified by regeneration.** The reviewer
  re-ran the same `vacuous_basic` pipeline **inside the `9109e16` worktree** and diffed the output
  against the committed `tests/fixtures/verdict_schema_v1_row2_artifacts.json`: all **10** artifact
  locators identical, all **10** artifact bodies byte-identical, the same content-addressed verdict
  locator `state/734b989b…9ca.json`, payload `schema_version:"1"` with **no** `decision_row` key. The
  fixture is what it claims to be.
- **`is_below_floor` perturbs nothing.** Confirmed against the real pre-amendment bytes above: the
  live payload differs from the captured v1 payload by exactly `schema_version` + `decision_row`; no
  `is_below_floor` key appears in `to_canonical_payload()` (it is a plain `@property`, not a
  `computed_field`), so content hashing and cache keys are untouched.
- **The no-migration decision is safe.** `argus/store/envelope.py` / `reader.py` carry
  `schema_version` but never gate on its value, so a `"1"`-stamped envelope stays readable; and
  `AuditVerdict` is constructed in exactly **one** place in `argus/` (`verdict_gate.py:651`), so
  there is no second construction site that could omit the row.
- **The FR16 reorder proven end-to-end, not just at the unit boundary.** A live
  `run_audit_detailed` over the `orphan_basic` cartridge (a real coverage shortfall with **zero**
  blocking findings) now returns `INSUFFICIENT_COVERAGE` / exit `3` /
  `DecisionRow.GATE_UNMET_NO_FINDINGS`, and the persisted negative-assurance statement reads *"No
  blocking findings were detected within the assessed scope; a coverage or critical-subsystem gate
  was not met…"*. That is the whole point of the story, and it works.
- **`_CONSERVATISM_RANK` as a partial order is sound.** With `{RELEASE_READY: 0,
  NOT_READY_FOR_RELEASE: 1, INSUFFICIENT_COVERAGE: 1}` and the retained `refolded_rank >=
  candidate_rank`: (i) *cannot silence* — a blocking re-fold always has rank 1, which is `>=` every
  reachable candidate rank, so it always wins; (ii) *never upgrades* — a `RELEASE_READY` re-fold
  (rank 0) can only win against a `RELEASE_READY` candidate, so the Story-6.4 downgrade-only
  invariant holds unchanged; (iii) the row-1 (FLOOR WINS) path is unaffected. `pipeline.py:697-724`
  resolves `scope_paths` once and passes the same value to both folds, so candidate and re-fold
  always assess the identical population.

---

- [x] [Review][Defer] **R1 — a row-4 `final-verdict.md` still prints the exact false-accusation
      sentence the epic exists to delete, contradicting its own verdict line**
      [`argus/reports/generator.py:339`] — deferred, **delta-caused but explicitly fenced by AC15;
      owner: Story 8.3 / DR-11**. Reproduced by the reviewer on a synthetic row-4 fold (2/5 deep,
      zero findings): the rendered report contains, six lines apart,
      `- **Final Verdict**: **`INSUFFICIENT_COVERAGE`** (Exit Code `3`)` and
      `> [!CAUTION] Repository is NOT ready for release — deep coverage `2/5` is below the `3/5`
      release threshold.` (plus `> Ship-readiness: NOT ASSESSED — too little of the code was
      examined deeply`, the D5 accepted transient). `final-verdict.md` is a **persisted** artifact, so
      a run where Argus found nothing now ships a document that says both "not assessed" and "NOT
      ready for release" about itself. **This is correct behaviour for THIS story** — AC15's ⚠️ says
      "key the branch on the decision row; **do not** change any rendered string", and the Dev obeyed
      the fence rather than colliding with 8.3's branch audit. It is recorded here because (a) it is
      the residual half of the defect on the human surface and must not be lost between stories, and
      (b) D4's own conflict rule ("the project standard wins when the alternative is shipping an
      artifact that lies") was applied to `negative_assurance.py` but not to this callout — an
      asymmetry Story 8.3 should close deliberately, not by accident. **Do not fix here.**

- [x] [Review][Patch] **R2 — AC12's FR19 "never upgrades" clause is asserted over a private rank map
      instead of through `prosecute()`, and the real branch it guards is never executed by any test**
      [`tests/test_prosecutor.py::test_release_ready_refold_never_upgrades_a_gate_unmet_candidate`].
      The test imports `_CONSERVATISM_RANK` and asserts `rank[RELEASE_READY] < rank[INSUFFICIENT_COVERAGE]`
      — an implementation-coupled assertion about the *mechanism*, not the *guarantee*. It would go
      red if someone replaced the rank map with an equivalent explicit guard, and it cannot catch a
      regression in the `refolded_rank >= candidate_rank` comparison at `prosecutor.py:474-483`,
      which is the code that actually enforces FR19. The test's own docstring claims the case
      "cannot be manufactured" — **that is false, and the reviewer manufactured it**: `prosecute()`
      takes `scope_paths` as a parameter independent of the candidate verdict, so a candidate folded
      unscoped (2 deep / 5 → row 4) prosecuted with `scope_paths=("f0.py","f1.py","f2.py")` produces
      a `RELEASE_READY` re-fold and executes the `else` branch; the guarantee holds (final verdict
      stays `INSUFFICIENT_COVERAGE` / row 4, `downgraded is False`). **Suggested fix:** keep the
      rank-map assertion as a white-box pin if you like, but add a behavioural test that calls
      `prosecute()` with that mismatched-scope construction and asserts
      `result.verdict.verdict is Verdict.INSUFFICIENT_COVERAGE`,
      `result.verdict.decision_row is DecisionRow.GATE_UNMET_NO_FINDINGS` and
      `result.downgraded is False`. Rule violated: tests should pin behaviour at the public seam, not
      private constants (testability / implementation-coupled test).

- [x] [Review][Patch] **R3 — the story's blast-radius table still asserts the classification that
      Variance V2 falsified** [story file, "Measured blast radius" §, the sentence naming
      `tests/test_dogfood_proof.py` among the four "artefacts of the scratch environment"].
      Independently disproved above: that test is **green at `9109e16`** in a real worktree, so the
      failure is delta-caused, exactly as V2 says. V2 records the correction in the Dev Agent Record,
      but the table — the part a future reader and Story 8.5 will actually consult — still states the
      wrong thing, and a stale planning artifact is precisely the failure mode this epic is about.
      **Suggested fix:** annotate that sentence in place (strike `test_dogfood_proof.py` from the
      environment-only list, cross-reference V2 and Story 8.5 / DR-10). Documentation only, no code.

- [x] [Review][Patch] **R4 — the AC11 proof and its evidence fixture are untracked by git**
      [`tests/test_verdict_schema_bump.py`, `tests/fixtures/verdict_schema_v1_row2_artifacts.json`].
      `git status` reports both as `??`. The single strongest piece of evidence in this story — the
      captured pre-amendment `.argus/` bytes — is currently not under version control, so a
      `git commit -a` would ship the delta without the proof and leave the suite red for everyone
      else (the test hard-fails if the fixture is absent). **Suggested fix:** `git add
      tests/test_verdict_schema_bump.py tests/fixtures/verdict_schema_v1_row2_artifacts.json` before
      the story is committed, and confirm `tests/fixtures/` is not caught by a `.gitignore` rule.

- [x] [Review][Patch] **R5 — a row-4 → row-2 reclassification leaves no structured signal on
      `ProsecutionResult`** [`argus/verdict/prosecutor.py:485`]. `downgraded = rank[final] >
      rank[candidate]` can now only ever be `True` for `RELEASE_READY → withholding`, because the two
      withholding verdicts rank equal. That is the *documented and correct* reading of "downgraded",
      and the field description says so — but it means a consumer reading `ProsecutionResult` sees
      `downgraded=False` on a run where the Prosecutor **did** change the verdict from
      `INSUFFICIENT_COVERAGE` to `NOT_READY_FOR_RELEASE`. Today the only record is the
      `promoted:<rule>:<id>` rationale token, which requires the consumer to know that a promotion
      implies a possible verdict move. Low severity (nothing in `argus/` reads `downgraded`, and the
      field is not persisted), but it is a latent trap for the next consumer. **Suggested fix:**
      either emit an explicit rationale token when `final_verdict.verdict is not verdict.verdict`
      (e.g. `reclassified:INSUFFICIENT_COVERAGE->NOT_READY_FOR_RELEASE`, mirroring the existing
      `downgrade:` token), or add a `verdict_changed: bool` field alongside `downgraded`. Rule:
      a structured result should not require out-of-band reasoning to answer "did this pass change
      the verdict?".

---

**Code review — 2026-08-04, iteration 2 (re-review after the fix round). Verdict: PASS. Status → `done`.**
Every disposition was verified against the tree as it stands, not against the Dev Agent Record. No new
finding; no regression. All five iteration-1 items are closed.

**Reviewer's own re-run (not the Dev's numbers):** `PYTHONIOENCODING=utf-8 python -m pytest tests/ -q`
with `--junit-xml` → `tests="1075" failures="3" errors="0" skipped="0"` (⇒ **1072 passed**), 68 test
files, 168s. `python -m mypy argus` → `Success: no issues found in 69 source files`. The **only** three
reds are the user-adjudicated carve-out, confirmed by name from the JUnit XML:
`test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation`,
`::test_budget_reuses_the_31_accountant_no_fork` (inherited, red at `9109e16`), and
`test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run` (delta-caused,
deliberate, Story 8.5 / DR-10 — the fenced `minions-dogfood-proof.md` is untouched). **Nothing was
deleted, skipped, weakened or re-pointed to assert less:** `--collect-only` per-file census = 1075 over
68 files; `tests/test_prosecutor.py` **17 → 21** with **zero test names lost** (`comm` over the baseline
and working-tree name sets); assertion counts rose or held in every modified test file; zero `skip`/
`xfail` markers added (the two `pytest.importorskip("tree_sitter")` lines in
`tests/test_verdict_schema_bump.py` are the established project pattern and did not fire — 3/3 collected
and green). **AC18's fence re-verified independently:** `git diff HEAD` over `plain_english.py`,
`test_plain_english.py`, `critical_subsystems.py`, `cli.py`, `argus/__init__.py`, `argus/dogfood/`,
`minions-dogfood-proof.md` and both `final-verdict.md` artifacts is **empty**. Fix-round blast radius
confirmed minimal by mtime + diff: only `argus/verdict/prosecutor.py` and `tests/test_prosecutor.py`
changed since iteration 1; the story's AC block is unchanged in substance and still mirrors (and
exceeds) the epic's AC set for 8.1.

- [x] **R1 — CONFIRMED DEFERRED, correctly untouched.** `git diff HEAD -- argus/reports/generator.py`
      is **6 insertions / 1 deletion**: the `elif verdict.verdict.value == "INSUFFICIENT_COVERAGE":` →
      `elif verdict.is_below_floor:` branch key plus its explanatory comment. The
      `render_callout("CAUTION", f"Repository is NOT ready for release — {detail}.")` at
      `generator.py:339` is **byte-identical to baseline** — the AC15 fence held, no rendered string
      moved. Logged as **DF-8-1-A** in `deferred-work.md` (verified present, with `target_story: 8-3`
      and the full six CC-3 fields). Not re-raised as a finding against this story.

- [x] **R2 — RESOLVED, and the branch is genuinely reached (verified by execution trace, not by a
      green test).** The reviewer re-ran the `-31` construction under `sys.settrace` with
      `prosecutor.evaluate_verdict` spied: the re-fold inside `prosecute()` returns
      `Verdict.RELEASE_READY` / `DecisionRow.GATES_MET` / `blocking_finding_count == 0`, the
      `if refolded_rank >= candidate_rank` line executes, the **if-branch body does NOT execute
      (line 488 unvisited)** and the **`else` `model_copy` rejection body DOES (line 494 visited)**.
      Final: `INSUFFICIENT_COVERAGE` / `GATE_UNMET_NO_FINDINGS` / exit 3, `downgraded=False`,
      `verdict_changed=False`, `findings == ['cross_partition']`. So FR19's real enforcement path is
      now covered for the first time. The corrected docstring is **true** (2 deep of `("g0","g1","g2")`
      = 2/3 ≥ 3/5 — checked against the fixture), and the false "cannot be manufactured" claim is gone.
      **No coverage was lost by the rewrite:** the white-box rank-map assertion survives verbatim as
      `TC-ArgusAgent-PROSECUTOR-001-32` (all three inequalities, not a subset), and the rejection path's
      refined-finding carry-over is newly pinned — a strict superset of the replaced test.

- [x] **R3 — RESOLVED (documentation).** The "Measured blast radius" § now strikes
      `~~tests/test_dogfood_proof.py~~` in the environment-only sentence, tags it `[CORRECTED — see
      below]`, and carries an in-place CORRECTION block that records the file is green at `9109e16`,
      names the reviewer's detached-worktree confirmation, cross-references **Variance V2**, **Story
      8.5 / DR-10** and AC18's must-not-modify fence, and warns the reader off the un-annotated
      sentence. `test_dogfood_plan.py` correctly keeps its inherited classification. Original text
      struck, not deleted — provenance intact.

- [x] **R4 — RESOLVED.** `git status --porcelain` shows `A  tests/fixtures/verdict_schema_v1_row2_artifacts.json`
      and `A  tests/test_verdict_schema_bump.py` (staged, **not committed**, content unchanged).
      `git check-ignore -v` exits **1** on both paths — no ignore rule matches. The AC11 evidence can
      no longer be lost by a `git commit -a`.

- [x] **R5 — RESOLVED, and the new code is safe (this was the fix round's only source change; audited
      as new code, not as a diff).** `ProsecutionResult.verdict_changed: bool = False` computed as
      `final_verdict.verdict is not verdict.verdict`, with `if downgraded: … elif verdict_changed: …`.
      (i) **Exactly one token per move, never zero-when-moved, never two:** `downgraded` ⇒ different
      ranks ⇒ different verdict values ⇒ `verdict_changed`, so the `elif` can never swallow a real
      move and the two tokens are mutually exclusive by construction; `TC-ArgusAgent-PROSECUTOR-001-33`
      pins all three arms (reclassify / genuine downgrade / untouched → empty rationale).
      (ii) **"Never serialized" verified independently, not accepted:** a repo-wide grep for
      `ProsecutionResult` / `prosecution.` outside `prosecutor.py` and `tests/` returns exactly one
      line — `argus/pipeline.py:734  verdict = prosecution.verdict` — and `rationale` has **no**
      consumer anywhere in `argus/`; every `persist_*` call takes `AuditVerdict`, never the
      `ProsecutionResult`. No canonical payload, content hash or cache key moves, and
      `tests/test_verdict_schema_bump.py`'s byte-delta proof (unchanged since iteration 1) is still
      green. (iii) **The Story-6.4 downgrade-only invariant and the iteration-1 partial-order argument
      both still hold:** the selection logic (`refolded_rank >= candidate_rank`) and
      `_CONSERVATISM_RANK` are untouched by this fix round, so a `RELEASE_READY` re-fold (rank 0) can
      still only win against a `RELEASE_READY` candidate — now demonstrated by execution rather than
      argued (see R2), with `downgraded`/`verdict_changed` both `False` on the rejection path.

## Dev Notes

### LOCKED decisions taken at story design — with rationale (record these; do not re-litigate)

**D1 — `DecisionRow` is a new 4-member closed `str` enum; `Verdict` does not grow.**
```python
class DecisionRow(str, enum.Enum):
    BELOW_FLOOR = "row_1_below_floor"
    BLOCKING_FINDINGS = "row_2_blocking_findings"
    GATES_MET = "row_3_gates_met"
    GATE_UNMET_NO_FINDINGS = "row_4_gate_unmet_no_findings"
```
*Rationale:* the codebase's standing pattern for every wire vocabulary is a `str`-valued closed enum with a
committed membership pin (`Verdict`, `CoverageDepth`), and the values carry the row number so "which row
fired" is literal rather than inferred. The addendum's "the verdict enum MUST NOT grow" constrains
**`Verdict`**, not the introduction of a separate disclosure vocabulary — a reviewer will check this, so say
so in the docstring. Add a membership pin test mirroring `TC-ArgusAgent-VERDICT-001-01`.

**D2 — the field is `DecisionRow | None` with `default=None`, and `None` means "pre-amendment, not
disclosed".** *Rationale:* `AuditVerdict` is `extra="forbid"`, so a missing key on read-back of a
`schema_version:"1"` payload is a `ValidationError` unless the field has a default (assumption A8, binding).
`None` is preferred over a fifth sentinel enum member because the enum then stays exactly one-per-row and
`evaluate_verdict` can be pinned to **never** return `None` (a test asserts that over all four rows).
*Verified during story design:* `AuditVerdict.model_validate(<v1 payload without decision_row>)` succeeds
with this shape, and Pydantic coerces the canonical `"3/5"` string back to `Fraction(3, 5)`, so a full
`canonical.dumps → canonical.loads → model_validate` round-trip is available for the AC8 proof.

**D3 — no new "assessed population" field.** The assessed population is **already** disclosed: `coverage_scope`
(with `assessed_deep_count` / `assessed_total_count` / `assessed_deep_ratio`) when the assessment was
narrowed, and `deep_count` / `total_count` when it was not. *Rationale:* FR16's own AC wording is "the schema
bump plus **the new field**" (singular); making `coverage_scope` always-present would break the LOCKED
`Present ⇔ the gate keyed on a narrowed population` semantics that four downstream modules branch on, and
duplicating the counts as scalars would create a second source of truth for the same number (the exact
failure mode §3.3 forbids). The AC8 **re-derivation test** is what proves the disclosure is sufficient
rather than merely asserted.

**D4 — the scope boundary against Story 8.3.** This story fixes the consumers whose **persisted machine
artifacts would otherwise assert a falsehood the instant the reorder lands** (`exhaustion.py` `below_floor`,
`negative_assurance.py` statement) and makes the **minimum** `generator.py` branch change needed to keep two
existing honesty pins green **without touching any rendered string**. It does **not** touch
`plain_english.py`. *Rationale:* project standard (§3.4 evidence immutability, the PRD's "no artifact
contradicts the tool") outranks a tidy story boundary when the alternative is shipping an artifact that
lies; but the epic's explicit sequencing (8.3 owns DR-11's report-surface reconciliation, including the
row-1-vs-row-4 human wording split and the "NOT VOUCHED" unreachable-branch audit) is a stated planning
decision and is respected everywhere it does not force a falsehood into a persisted artifact.

**D5 — accepted transient, recorded.** Between this story and Story 8.3, `plain_english.py`'s
`INSUFFICIENT_COVERAGE` headline (*"NOT ASSESSED — too little of the code was examined deeply to make any
call"*) will be **imprecise for row 4** (where plenty was examined and nothing was found). No test asserts
otherwise, the machine contract is correct, and Story 8.3 is the very next story and its ACs already
specify the two-way wording split (boundary B4). Accepted deliberately; do **not** "helpfully" fix it here
— that would collide with 8.3's branch audit.

**D6 — `_CONSERVATISM_RANK` becomes a partial order.** *Rationale:* after the reorder, "conservative" can no
longer be a total order over the three verdicts: `INSUFFICIENT_COVERAGE` (a not-assessed state) and
`NOT_READY_FOR_RELEASE` (a found-something state) are **incomparable** — both withhold `RELEASE_READY`, and
neither is "safer" than the other. The only invariant FR19 actually needs is *never move toward
`RELEASE_READY`*. Ranking them equal preserves that (a `RELEASE_READY` re-fold can never win) while letting a
promoted blocking finding surface. This is provably safe: the re-fold sees the same ledger, same scope and
same critical flags, and a strictly larger/promoted finding set, so `blocking` can only increase — the only
reachable transitions are row-1→row-1, row-2→row-2, row-3→row-2 and row-4→row-2.

### Architecture patterns & constraints (non-negotiable — AR/NFR ids a reviewer will check)

- **AR8 pure/impure master rule.** The verdict gate is PURE: no I/O, no clock, no LLM, no `dispatch()`, no
  `uuid4`/`random`, no set/dict iteration-order reliance. It imports **only** the two ledger modules.
  `prosecutor.py` and `negative_assurance.py` are likewise pure; `exhaustion.py`'s `build_floor_report` is
  pure; `generator.py` renders strings only.
- **AR4 determinism.** One canonical serializer (`argus/store/canonical.py`) — never call `json.dumps`
  directly. Ratios are exact `Fraction`, **never `float`** (the serializer raises
  `CanonicalSerializationError` on a float leaf — the backstop is real and is tested). `Fraction` re-installs
  live in `to_canonical_payload()` because `model_dump()` coerces via `str` (`Fraction(1,1) → "1"`, which
  diverges from the LOCKED `"num/den"` encoding) — the new field is a plain string enum and needs no such
  handling.
- **NFR-M2 additive-only schema evolution.** The `schema_version` bump is the sanctioned lever for an
  intentional content-hash change (`verdict_gate.py:147-149`). New fields are optional-with-default only.
- **NFR-D2 zero-token testability.** Every AC in this story is provable over **synthetic ledgers** with no
  LLM and no network. Do not reach for a live audit run to prove a pure-fold property.
- **NFR-M1** ≤1200 lines per file (`verdict_gate.py` is 538 today — ample headroom).
- **AR3 wire contract** exit codes `0`/`2`/`3`/`1`; `1` is reserved for the pipeline's typed-error
  degradation and is never produced by the gate.
- **§3.3 no-fork / reuse.** Do not write a second decision table anywhere. Every consumer that needs to know
  *why* a verdict was rendered reads `decision_row` — that is what it is for. If you find yourself
  re-deriving the row in `exhaustion.py`, `negative_assurance.py` or `generator.py`, you have forked the
  gate.
- **NFR-S1.** No source bytes, secret bytes or absolute host paths in any emitted field, message or log.
  The new field is a closed token; keep it that way.

### Traps a previous story already paid for (Epic 1–7 learnings that apply here)

- **The golden-bytes test is the canary, not an obstacle.** `TC-ArgusAgent-VERDICT-001-94` will fail; that
  failure is *the proof the schema bump is doing something*. Regenerate the constant by running the fold and
  pasting the produced bytes — do **not** hand-edit the string and do **not** relax the assertion.
- **"Extended, not forked" applies to the import-isolation gate.** `_MODULES_UNDER_GUARD` (in the
  import-isolation test) is **appended to**, never replaced — this pattern was re-confirmed in Stories 2.1,
  2.5, 2.6 and 3.1. No new module is created by this story, so no addition is expected; verify the gate is
  still green with the modified files.
- **`Fraction`, never `float`** — Story 3.1's review found the only safe pattern is to keep the live
  `Fraction` object and let the single serializer encode it. Do not compute a percentage as a float
  anywhere, including in a message string (`exhaustion._whole_percent` already does this correctly with
  exact arithmetic — reuse it).
- **Non-ASCII adversarial coverage (AI-E1-1) is a standing requirement** since Epic 1's only review FAIL.
  This story adds no path/text handling, so it is discharged by the existing suites — state that explicitly
  in the completion notes rather than silently skipping it.
- **Do not flip the story to `review` before the tests exist** (process watch-item AI-E2-1 from the Epic-2
  retrospective).
- **Verify independently; do not trust a prior record.** Every Epic-6/7 review re-ran the suite itself. The
  measured 23-failure list in this story was produced by an actual scratch-tree run — re-derive it, do not
  assume it.

### Project Structure Notes

- **Files this story is expected to modify:** `argus/verdict/verdict_gate.py` (the substance),
  `argus/verdict/prosecutor.py` (rank map + comment), `argus/cost/exhaustion.py` (`below_floor` predicate +
  docstring), `argus/verdict/negative_assurance.py` (one branch split),
  `argus/reports/generator.py` (branch selection only, no strings), and the test files listed in Task 7 plus
  `tests/cartridges/_registry.py`.
- **Files this story must NOT modify (AC18):** `argus/reports/plain_english.py`,
  `tests/test_plain_english.py`, `argus/ledger/critical_subsystems.py`, `argus/cli.py`,
  `argus/__init__.py`, `argus/dogfood/*`, `_bmad-output/reports/final-verdict.md`,
  `_bmad-output/audit-reports/final-verdict.md`, `minions-dogfood-proof.md`.
- **No new module.** Everything is an edit to an existing file; the `verdict/` package layout is unchanged.
- **Test tree:** `tests/` at the repo root (this repo's layout — *not* the `tests/apaa/` path named in the
  older architecture prose, which describes the pre-extraction Minions monorepo).
- **Run tests as** `PYTHONIOENCODING=utf-8 python -m pytest tests/ -q` (the suite contains non-ASCII
  fixtures; the env var is the established convention). `pytest-timeout` is **not** installed — do not pass
  `--timeout`.

### Variance from the epic, recorded

The epic's AC set for Story 8.1 covers the decision table, the disclosure, the schema bump and determinism.
ACs **12–16** are **additions made at story design** after measuring the change against the real tree: four
live consumers break or begin asserting a falsehood the moment the reorder lands (Prosecutor rank, floor
report predicate, negative-assurance statement, report-generator branch), and three self-audit cartridges
had frozen the defect into their golden keys. They are in scope here under the standing rule that a story
must leave the system working end-to-end and must never ship an artifact that contradicts the shipped
contract. The boundary against Story 8.3 is stated in **D4**.

### References

- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Story 8.1: Findings before coverage — the binding decision table`] (lines 1390–1462, including the LOCKED channel decision and boundaries B2/B4)
- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Delta Requirements Inventory`] — DR-1, DR-2, DR-3, DR-4, DR-9 and the "Additional Requirements (Architecture + addendum)" constraint block
- [Source: `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md#Release-Readiness Verdict`] — FR16 as amended (the binding 4-row table) and the canonical verdict vocabulary
- [Source: `_bmad-output/design-artifacts/ArgusAgent/E-PRD/addendum.md#A1 — FR16 / FR4 amendment mechanics (2026-08-03)`] — the rejected `COVERAGE_GATE_UNMET` option, the schema-bump permission, the integrator migration framing
- [Source: `_bmad-output/design-artifacts/ArgusAgent/architecture.md#Implementation Patterns & Consistency Rules`] — AR4 determinism patterns, AR8 pure/impure master rule, contract/format patterns, error/degradation patterns
- [Source: `_bmad-output/design-artifacts/ArgusAgent/sprint-change-proposal-2026-08-03.md`] — the change signal that produced the amendment
- [Source: `argus/verdict/verdict_gate.py`] — the frozen contract being amended (decision table at `:511-520`, `VERDICT_SCHEMA_VERSION` at `:149`, thresholds at `:154-155`, FLOOR-WINS rationale at `:51-55`)
- [Source: `argus/verdict/prosecutor.py:121-130,430-458`] — `_CONSERVATISM_RANK` and the FR19 re-fold
- [Source: `argus/cost/exhaustion.py:455-505`] — `build_floor_report` and the now-falsified equivalence
- [Source: `argus/verdict/negative_assurance.py:284-317`] — `_assurance_statement`
- [Source: `argus/reports/generator.py:103-136,304-337`] — `_render_critical_blockers` and the verdict branch
- [Source: `tests/cartridges/_registry.py:126-248`] — the cartridge golden keys

## Dev Agent Record

### Context Reference

- This story file (self-contained). Story key: `8-1-findings-before-coverage-binding-decision-table`.

### Agent Model Used

`claude-opus-5[1m]` (BMAD `dev-story`, 2026-08-04).

### Debug Log References

**Environment / commands.** Python 3.11.15, pytest 9.1.1, Windows. Suite:
`PYTHONIOENCODING=utf-8 python -m pytest tests/ -q`. Types: `python -m mypy argus`.
Baseline commit `9109e16` (recorded in the frontmatter).

**Baseline, measured before any edit (not assumed).** `PYTHONIOENCODING=utf-8 python -m pytest tests/ -q`
→ exactly **2 failures**, both in `tests/test_dogfood_plan.py`
(`test_committed_partition_plan_artifact_exists_and_matches_live_derivation`,
`test_budget_reuses_the_31_accountant_no_fork`). Everything else green. This confirms the
story's "pre-existing red — inherited, not caused" section and establishes that any other
red is delta-caused.

**RED-first evidence (AC2) — Task 1, captured against the UNMODIFIED three-row gate.**

`PYTHONIOENCODING=utf-8 python -m pytest tests/test_verdict_gate.py -k "001_100 or 001_101" -q`:

```
    def test_TC_ArgusAgent_VERDICT_001_100_row_4_coverage_gate_unmet_no_findings(self) -> None:
        av = evaluate_verdict(_ledger_ratio(deep=2, total=5))
        assert av.blocking_finding_count == 0
>       assert av.verdict is Verdict.INSUFFICIENT_COVERAGE
E       AssertionError: assert <Verdict.NOT_READY_FOR_RELEASE: 'NOT_READY_FOR_RELEASE'> is
                        <Verdict.INSUFFICIENT_COVERAGE: 'INSUFFICIENT_COVERAGE'>
tests\test_verdict_gate.py:403: AssertionError

    def test_TC_ArgusAgent_VERDICT_001_101_row_4_critical_gate_unmet_no_findings(self) -> None:
        av = evaluate_verdict(_ledger_ratio(deep=3, total=5), critical_subsystems_all_deep=False)
        assert av.blocking_finding_count == 0
        assert av.deep_ratio >= RELEASE_READY_DEEP_THRESHOLD
>       assert av.verdict is Verdict.INSUFFICIENT_COVERAGE
E       AssertionError: assert <Verdict.NOT_READY_FOR_RELEASE: 'NOT_READY_FOR_RELEASE'> is
                        <Verdict.INSUFFICIENT_COVERAGE: 'INSUFFICIENT_COVERAGE'>
tests\test_verdict_gate.py:414: AssertionError

FAILED tests/test_verdict_gate.py::TestAmendedDecisionTable::test_..._001_100_row_4_coverage_gate_unmet_no_findings
FAILED tests/test_verdict_gate.py::TestAmendedDecisionTable::test_..._001_101_row_4_critical_gate_unmet_no_findings
```

That is the defect, reproduced: **zero blocking findings, and the tool says
`NOT_READY_FOR_RELEASE`.**

**RED-first evidence (AC12) — the Prosecutor.** As the story predicted, red for a
*different* reason before the reorder (the candidate is not yet a row-4 verdict):

```
    ledger = _gate_unmet_ledger()
    candidate = evaluate_verdict(ledger, ())
>   assert candidate.verdict is Verdict.INSUFFICIENT_COVERAGE  # row 4, zero findings
E   AssertionError: assert <Verdict.NOT_READY_FOR_RELEASE: ...> is <Verdict.INSUFFICIENT_COVERAGE: ...>
tests\test_prosecutor.py:363: AssertionError

>   assert (_CONSERVATISM_RANK[Verdict.INSUFFICIENT_COVERAGE]
            == _CONSERVATISM_RANK[Verdict.NOT_READY_FOR_RELEASE])
E   assert 2 == 1
tests\test_prosecutor.py:400: AssertionError

FAILED tests/test_prosecutor.py::test_gate_unmet_candidate_never_silences_a_promoted_finding
FAILED tests/test_prosecutor.py::test_release_ready_refold_never_upgrades_a_gate_unmet_candidate
```

**Blast radius re-derived, not assumed.** After the gate change alone the suite showed
the story's 23 delta-caused failures across the named 9 files, **plus one the story's
scratch-tree measurement had masked** — see Variance V2.

**Final validation.**

```
PYTHONIOENCODING=utf-8 python -m pytest tests/ -q
  tests=1073  passed=1070  failed=3  errors=0  skipped=0   (138s)
  FAILED tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation   [INHERITED]
  FAILED tests/test_dogfood_plan.py::test_budget_reuses_the_31_accountant_no_fork                                [INHERITED]
  FAILED tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run                  [DELTA-CAUSED, DEFERRED — Variance V2]

python -m mypy argus
  Success: no issues found in 69 source files
```

All **23** measured delta-caused failures are green. No test was deleted or weakened.

**Fix iteration 2 — validation after the review findings were addressed (2026-08-04).**

```
PYTHONIOENCODING=utf-8 python -m pytest tests/ -q
  collected=1075  passed=1072  failed=3  errors=0  skipped=0
  (progress-line character census over the full run: 1072 '.', 3 'F', zero 's'/'x'/'E')
  FAILED tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation   [INHERITED — also fails at 9109e16]
  FAILED tests/test_dogfood_plan.py::test_budget_reuses_the_31_accountant_no_fork                                [INHERITED — also fails at 9109e16]
  FAILED tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run                  [DELTA-CAUSED, DEFERRED — Variance V2 / Story 8.5 / DR-10]

python -m mypy argus
  Success: no issues found in 69 source files
```

`1073 → 1075` collected: `tests/test_prosecutor.py` `19 → 21` (one test rewritten in place at
the public seam, two added). **No test deleted, skipped, weakened or re-pointed to assert less**;
the three reds are exactly the three adjudicated ones and no new red appeared. AC18's
must-not-modify fence re-verified: `git diff` over `argus/reports/plain_english.py`,
`tests/test_plain_english.py`, `argus/ledger/critical_subsystems.py`, `argus/cli.py`,
`argus/__init__.py`, `argus/dogfood/*` and `minions-dogfood-proof.md` is **empty**.

### Review Findings — resolution (fix iteration 2, 2026-08-04)

**5 findings, 4 fixed + 1 deliberately not fixed (R1, deferred by the reviewer's own instruction).**

- **R1 [Med] — NOT FIXED, by design.** The row-4 `final-verdict.md` self-contradiction
  (`generator.py:339`) is left exactly as it is. AC15's ⚠️ fence ("key the branch on the decision
  row; **do not** change any rendered string") makes deferral the correct behaviour for this story,
  the reviewer classified it as deferred, and it is logged as **DF-8-1-A** in `deferred-work.md`
  against Story 8.3 / DR-11. Touching it here would collide with 8.3's branch audit and break the
  AC15 fence — the story standard wins over the instinct to fix the prose (D4's conflict rule,
  applied in the direction the fence points).

- **R2 [Low] — FIXED. The FR19 "never upgrades" guarantee is now pinned BEHAVIOURALLY, through
  `prosecute()`.** The reviewer was right on both counts: the old test asserted the *mechanism*
  (`_CONSERVATISM_RANK[RELEASE_READY] < _CONSERVATISM_RANK[INSUFFICIENT_COVERAGE]`) rather than the
  *guarantee*, so the `else` branch at `prosecutor.py:474-483` that actually enforces FR19 was never
  executed by any test — and the docstring's claim that the case "cannot be manufactured" **was
  false**. Reproduced independently before writing the test: `scope_paths` is a parameter of
  `prosecute` independent of the candidate verdict, so a candidate folded UNSCOPED over
  `_gate_unmet_ledger()` (2 deep / 5 = 40% → row 4) re-folded against `("g0.py","g1.py","g2.py")`
  (2 deep / 3 = 66% ≥ the 60% gate) yields a **`RELEASE_READY` re-fold**, which is precisely the
  less-conservative shape FR19 must discard. `TC-ArgusAgent-PROSECUTOR-001-31` now (a) asserts the
  precondition through the public gate — the scoped re-fold really is `RELEASE_READY`, so the test
  cannot silently stop exercising the branch; (b) calls `prosecute()` and asserts the *guarantee*:
  final verdict `INSUFFICIENT_COVERAGE`, `decision_row is GATE_UNMET_NO_FINDINGS`, `exit_code == 3`,
  `downgraded is False`, `verdict_changed is False`; and (c) additionally pins that the refined
  finding set is **not lost** on the rejection path (a `cross_partition` seam finding raised by the
  cut-edge pass survives onto the kept candidate verdict — the `model_copy` at `:481-483`, which
  nothing previously covered). The false docstring claim is deleted and replaced by the construction
  that disproves it. The white-box rank-map assertion was **kept, not dropped** — moved to its own
  `TC-ArgusAgent-PROSECUTOR-001-32`, labelled as a pin of the mechanism (D6's partial order),
  explicitly *alongside* rather than *instead of* the behavioural pin.

- **R3 [Low] — FIXED (documentation only).** The "Measured blast radius" § now carries a struck-out
  `tests/test_dogfood_proof.py` plus an in-place **CORRECTION** block: the file is **green at
  `9109e16`** (confirmed by the reviewer in a clean detached worktree), so its failure is
  delta-caused, not a scratch-environment artefact. The block cross-references **Variance V2** and
  **Story 8.5 / DR-10**, records that the red is deliberate (AC18 fences `minions-dogfood-proof.md`
  as must-not-modify), and tells a future reader not to trust the un-annotated sentence.
  `tests/test_dogfood_plan.py` keeps its classification — the reviewer confirmed those two *do* fail
  at baseline. **Deviation from the dev-story section fence, recorded:** the workflow permits the Dev
  to edit only Tasks/Subtasks, Dev Agent Record, File List, Change Log and Status, and this edit is
  in Story Context. The finding's own prescribed fix is "annotate that sentence in place", and the
  standing project rule that a planning artifact must not assert something known to be false
  outranks the section fence here (D4's conflict rule). The edit is additive and clearly marked as a
  correction; the original sentence is struck, not deleted, so the provenance survives.

- **R4 [Low] — FIXED.** `git add tests/test_verdict_schema_bump.py
  tests/fixtures/verdict_schema_v1_row2_artifacts.json` — both now show `A` in `git status`
  (`tests/fixtures/` was an entirely new, wholly untracked directory, so the AC11 evidence was one
  `git commit -a` away from being lost while the test that hard-depends on it shipped). Confirmed no
  ignore rule catches them: `git check-ignore -v` on both paths exits **1** (no match), and
  `.gitignore` contains no `tests/` or `fixtures/` rule (its only artifact rules are `.argus/` and
  `_bmad-output/reports/`). **Not committed** — staging only, per the workflow.
  *Noted for the committer, outside the finding:* this story file is itself still untracked (`??`);
  it is a planning artifact, not suite-affecting, and was left alone.

- **R5 [Low] — FIXED, via a `verdict_changed` field (+ a mirroring rationale token).** Both options
  the reviewer offered were considered. The **field** was chosen as the primary signal because the
  rule the finding invokes — "a structured result should not require out-of-band reasoning" — is not
  satisfied by a token a consumer must string-parse, and because `ProsecutionResult` already answers
  a sibling question with a plain bool (`downgraded`). The token was added **as well**, because the
  module's existing pattern is a bool *paired with* a rationale token (`downgraded` /
  `downgrade:<from>-><to>`), and leaving the rationale silent on a verdict move that is not a
  downgrade would be exactly the asymmetry the finding is about. Shape: `verdict_changed: bool =
  False`, computed as `final_verdict.verdict is not verdict.verdict`, and **exactly one** token per
  move — `downgrade:` when the rank rose, `reclassified:<from>-><to>` otherwise (never both).
  `downgraded` keeps its meaning and its field description now points at `verdict_changed` for the
  broader question. **Perturbs nothing:** `ProsecutionResult` is constructed in one place and
  consumed in one place (`pipeline.py:720-734`, which reads only `.verdict`); it is never
  serialized, so it touches no canonical payload, no content hash and no cache key — re-verified by
  the unchanged `tests/test_verdict_schema_bump.py` byte-delta proof and the green
  `test_prosecutor_pipeline_wiring.py`. Pinned by `TC-ArgusAgent-PROSECUTOR-001-33` across all three
  cases: reclassification (changed, not downgraded, `reclassified:` token only), genuine downgrade
  (changed **and** downgraded, `downgrade:` token only), and an untouched verdict (neither, empty
  rationale).

### Completion Notes List

**What was implemented**

- **AC1–AC7 / DR-1 / DR-2 — the four-row table.** `evaluate_verdict` now evaluates FR16
  verbatim and in order: row 1 floor → row 2 findings → row 3 gates → row 4 otherwise.
  The `else` that was a *default block* is gone. Row 3 carries **no** redundant
  `blocking == 0` clause (row-2 precedence guarantees it; pinned by
  `TC-ArgusAgent-VERDICT-001-108`). Thresholds, `Verdict` membership (still exactly 3),
  `_EXIT_CODE_BY_VERDICT`, `exit_code_for_verdict`, `order_findings`,
  `is_verdict_blocking` and the `scope_paths` seam are all untouched.
- **Boundary B2 held.** `TC-ArgusAgent-VERDICT-001-80` (FLOOR WINS) is green with only an
  added row assertion, and `…-001-105` re-pins it explicitly: below-floor **with** a
  blocking finding is still row 1.
- **Boundary B4 pinned.** `…-001-106` asserts exactly-20% + unmet gate is **row 4, not
  row 1**, and asserts the two are indistinguishable by verdict *and* exit code — which
  is the argument for disclosing the row at all.
- **AC8 / DR-3 — disclosure.** New `DecisionRow` (`str` enum, exactly 4 members, exported
  in `__all__`) and `AuditVerdict.decision_row: DecisionRow | None = None`. The default is
  **mandatory** (A8) and proven: `…-001-111` validates a real `schema_version:"1"` payload
  with no `decision_row` under `extra="forbid"`, confirms the `"1"` stamp survives, and
  confirms it re-serializes with **no** `decision_row` key (the omit-when-unengaged rule
  the `coverage_scope` / `critical_subsystems_not_deep` fields already use — so a
  persisted v1 verdict keeps its content hash). Sufficiency is *proven, not asserted*:
  `…-001-112` re-derives verdict + exit code for all four rows (and a scoped run) from the
  artifact fields alone, never touching the ledger.
- **AC9 / DR-4 — `VERDICT_SCHEMA_VERSION` `"1"` → `"2"`.** No migration code, no rewrite
  pass.
- **AC11 / DR-9 — determinism + the single intentional hash change.** Proven empirically
  rather than argued: before touching any source I captured the **actual persisted
  `.argus/` bytes** of a full `vacuous_basic` pipeline run at `9109e16` into
  `tests/fixtures/verdict_schema_v1_row2_artifacts.json` (verified reproducible across two
  runs). `tests/test_verdict_schema_bump.py` re-runs the same audit post-amendment and
  asserts: the artifact count is unchanged; **every non-verdict artifact is byte-identical
  with an identical locator**; the verdict payload differs from the captured v1 payload by
  **exactly** `schema_version` + `decision_row` (reverting those two reproduces the old
  bytes); and two fresh runs are byte-identical.
- **AC10 — the stdout machine line is untouched.** `argus/cli.py` has **zero diff**;
  `TC-ArgusAgent-CLI-001-30` pins the exact line and asserts no `decision_row` / `row_`
  token reaches it.
- **AC12 — the Prosecutor no longer silences its own promotion.** `_CONSERVATISM_RANK`
  became a **partial** order (`RELEASE_READY: 0`, both withholding verdicts `1`, keeping
  `refolded_rank >= candidate_rank`). Without this, a row-4 candidate outranked its own
  blocking re-fold and the promoted finding was discarded. FR19 still holds: a
  `RELEASE_READY` re-fold can never outrank a withholding candidate.
- **AC13 — the floor report keys on the row.** `below_floor` is now
  `AuditVerdict.is_below_floor` (row 1), not the verdict enum. This is a **persisted**
  report; keying on the enum would have made it claim a floor breach at 30% assessed.
- **AC14 — the negative-assurance statement splits on the row.** Row 1 keeps its
  **byte-identical** string; row 4 gets an honest one. No certification token
  (re-verified by the existing `_FORBIDDEN_PHRASES` scan).
- **AC15 — the report generator branches on the row.** `elif verdict.is_below_floor:`
  replaces `elif verdict.verdict.value == "INSUFFICIENT_COVERAGE":`, so a row-4 run keeps
  the gate-naming block, `_render_critical_blockers` and the dilution hint. **No rendered
  string changed.** Both honesty pins
  (`test_critical_block_names_the_gate_and_the_files`,
  `test_designated_critical_absent_from_ledger_is_labelled`) are green **unmodified**.
- **AC16 — the cartridge registry.** `orphan_basic`, `vacuous_heuristic_basic` and
  `cross_partition_seam` moved to `INSUFFICIENT_COVERAGE` / exit `3`. Their
  `required_findings` are unchanged and still emitted. The clean controls and the three
  genuinely-blocking cartridges (`max_blocking=1`) are untouched — the false-green
  direction did not loosen.
- **AC18 — the fence held.** `git diff` over `argus/reports/plain_english.py`,
  `tests/test_plain_english.py`, `argus/ledger/critical_subsystems.py`, `argus/cli.py`,
  `argus/__init__.py`, `argus/dogfood/*` and every dogfood/proof artifact is **empty**.

**Design decision made during implementation (not pre-specified by the story)**

- **`AuditVerdict.is_below_floor` — one predicate, three consumers.** `exhaustion.py`,
  `negative_assurance.py` and `generator.py` each needed "was this the floor?". Letting
  each re-derive it from the counters would have forked the decision table three ways —
  the exact failure §3.3 forbids — so the predicate lives once, on the model, as a
  **property** (derived ⇒ adds no key to the canonical payload ⇒ cannot become a second
  source of truth on disk). It reads `decision_row` when disclosed and falls back to the
  verdict enum when it is `None`, which for a `"1"`-stamped payload is exactly the old —
  and then still correct — equivalence, so read-back of persisted state is unchanged.
- **`downgraded` on a row-4 → row-2 move is recorded as `False`** (Task 3's open
  question). Both verdicts withhold `RELEASE_READY` and rank equal, so nothing was
  downgraded — it is a *reclassification*. The `promoted:` rationale token is what records
  that the verdict moved. Documented on the field and pinned in
  `test_gate_unmet_candidate_never_silences_a_promoted_finding`.

**Standing requirements discharged**

- **AI-E1-1 (non-ASCII adversarial coverage).** Stated explicitly rather than silently
  skipped: this story adds **no** path or text handling — the new field is a closed ASCII
  token and no rendered string changed — so it is discharged by the existing non-ASCII
  suites (`nonascii_unicode` cartridge, `test_secret_containment.py`, the
  `PYTHONIOENCODING=utf-8` convention), all green.
- **AI-E2-1.** The story was not flipped to `review` before the tests existed; RED was
  captured first and is recorded verbatim above.
- **Purity / determinism gates re-run with the changed modules:**
  `TC-ArgusAgent-VERDICT-001-95` and `…-001-96` are green **unmodified** — no import was
  added, and the `argus.*` import set is still exactly
  `{argus.ledger.coverage_ledger, argus.ledger.recording}`. The single-serializer and
  no-web-import gates are green. AST scan of all five changed modules: **zero** float
  literals; the only `float` name reference is `exhaustion.py`'s pre-existing *rejection*
  guard.
- **NFR-M1.** Largest changed file is `verdict_gate.py` at **668** lines (was 538); the
  largest source file in the tree is `argus/pipeline.py` at 1162. All ≤ 1200.

**Variances from the story, recorded (D4 conflict-resolution rule: the project standard
wins, and the tradeoff is written down)**

- **V1 — AC13's "stay green **unmodified**" was not achievable for the three
  `test_insufficient_coverage_floor.py` tests, and the story's own AC falsifies it.** All
  three also assert the verdict **value** (`is Verdict.NOT_READY_FOR_RELEASE`,
  `is not Verdict.INSUFFICIENT_COVERAGE`, and — in `…-111` — literally
  `below_floor == (verdict is INSUFFICIENT_COVERAGE)`, the equivalence AC13 exists to
  falsify). The **real invariant each one pins is untouched and green**:
  `below_floor is False` above the floor, and `below_floor == (deep_ratio < floor)` across
  the boundary including `total == 0`. Only the collateral verdict-value assertions were
  re-pointed, each onto the **disclosed row** — which is strictly stronger than what they
  asserted before, since row 1 and row 4 share a verdict value. Nothing was deleted or
  weakened; every re-point is commented in place with its reason. The code fix AC13
  actually demands (`below_floor` ← row 1, not the enum) was made exactly as specified.
- **V2 — one delta-caused failure is DEFERRED to Story 8.5 by AC18, and left red:**
  `tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run`.
  The story classified this file as an *environment-only* failure from the scratch-tree
  measurement (no `.git` / no `_bmad-output/`); on the real tree that classification is
  **wrong** — the file is green at baseline and the test is genuinely delta-caused. It is
  a rot check: the committed `minions-dogfood-proof.md` records
  `` `NOT_READY_FOR_RELEASE` (exit `2`) `` while the live re-derivation over this repo now
  yields `` `INSUFFICIENT_COVERAGE` (exit `3`) ``.
  **Not fixed here, deliberately, for three converging reasons:** (1) **AC18 names
  `minions-dogfood-proof.md` as must-not-modify**, and DR-10 is Story 8.5's entire
  deliverable; (2) the epic states 8.5 is last **"so a slip is visible"** — this red *is*
  that designed-in visible slip; (3) **Story 8.2 (critical-subsystem eligibility) will
  change this repo's verdict again**, so re-deriving the proof now would produce an
  artifact that is stale the moment 8.2 lands. Weakening the rot check was rejected
  outright — it is exactly the kind of assertion this tool exists to defend.
  **AC17 is therefore met except for this one named, owned, out-of-scope red**, and the
  correction to the story's blast-radius table is recorded here so the result is not
  silently inflated. Recommend Story 8.5 (or a reviewer) confirm the ownership.
- **V3 — the two inherited `test_dogfood_plan.py` failures are untouched**, as the story
  requires: `…_committed_partition_plan_artifact_exists_and_matches_live_derivation`
  (unit `2c0f52f60457` missing from the committed plan) and
  `test_budget_reuses_the_31_accountant_no_fork` (`431` absent from the committed budget
  artifact). Present at `9109e16`, unrelated to this delta, owned by Story 8.5.
- **V4 — minor, in-file:** four stale prose passages inside `verdict_gate.py` described
  the test-dilution false negative as producing `NOT_READY_FOR_RELEASE`. The amendment
  makes that sentence false, so it was corrected in place (docstrings only; no behaviour,
  no rendered string).

### File List

**Source (modified)**

- `argus/verdict/verdict_gate.py` — the four-row FR16 table + `DecisionRow` +
  `AuditVerdict.decision_row` + `is_below_floor` + `VERDICT_SCHEMA_VERSION` `"2"` +
  docstrings.
- `argus/verdict/prosecutor.py` — `_CONSERVATISM_RANK` partial order + `downgraded`
  semantics + docstrings; **(fix iteration 2, R5)** new
  `ProsecutionResult.verdict_changed: bool = False` + the `reclassified:<from>-><to>`
  rationale token (exactly one token per verdict move).
- `argus/cost/exhaustion.py` — `below_floor` keys on the disclosed row + docstrings/field
  description.
- `argus/verdict/negative_assurance.py` — `_assurance_statement` row-1/row-4 split.
- `argus/reports/generator.py` — verdict branch keys on the row (no rendered string
  changed).

**Tests (modified)**

- `tests/test_verdict_gate.py` — 6 zero-blocking cases re-pointed + row assertions; new
  `TestAmendedDecisionTable`, `TestDisclosureAndSchema`, `TestDeterminismAndByteDelta`
  (`TC-ArgusAgent-VERDICT-001-100..115`); `GOLDEN_VERDICT_CANONICAL` regenerated by
  running the fold; pre-amendment golden kept as
  `GOLDEN_VERDICT_CANONICAL_V1_PRE_AMENDMENT`.
- `tests/test_prosecutor.py` — `_not_ready_ledger` → `_gate_unmet_ledger`;
  `test_not_ready_candidate_is_never_upgraded` re-pointed to a genuine row-2 candidate;
  new `TC-ArgusAgent-PROSECUTOR-001-30/-31`. **(fix iteration 2)** `-31` rewritten as a
  BEHAVIOURAL test through `prosecute()` (R2, and it now executes the FR19 rejection
  branch); new `-32` (the rank-map white-box pin, kept) and `-33` (R5's
  `verdict_changed` / token pin); `DecisionRow` imported.
- `tests/test_insufficient_coverage_floor.py` — three tests re-pointed onto the disclosed
  row (Variance V1).
- `tests/test_verdict_scope.py`, `tests/test_critical_subsystems.py`,
  `tests/test_depth_semantics.py`, `tests/test_pipeline_signature_demo.py` — verdict/exit
  expectations re-pointed; every original subject assertion kept.
- `tests/test_cli.py` — new `TC-ArgusAgent-CLI-001-30` (AC10 machine-line pin).
- `tests/cartridges/_registry.py` — three `max_blocking=0` cartridges re-pointed, with the
  reason recorded in comments.

**Tests (new)**

- `tests/test_verdict_schema_bump.py` — `TC-ArgusAgent-VERDICT-003-01..03`, the AC11
  end-to-end byte-delta + determinism proof. **STAGED in git (`A`) at fix iteration 2 —
  review finding R4.** Content unchanged.
- `tests/fixtures/verdict_schema_v1_row2_artifacts.json` — the captured pre-amendment
  `.argus/` artifact bytes (evidence fixture, generated at `9109e16`). **STAGED in git
  (`A`) at fix iteration 2 — review finding R4.** Content unchanged; no `.gitignore`
  rule matches (`git check-ignore` exits 1).

**Planning**

- `_bmad-output/design-artifacts/ArgusAgent/stories/8-1-findings-before-coverage-binding-decision-table.md`
  (this file).
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — `8-1-…` → `review`.

**Explicitly NOT modified (AC18, verified by `git diff` → empty):**
`argus/reports/plain_english.py`, `tests/test_plain_english.py`,
`argus/ledger/critical_subsystems.py`, `argus/cli.py`, `argus/__init__.py`,
`argus/dogfood/*`, `_bmad-output/**/final-verdict.md`, `minions-dogfood-proof.md`.

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-08-04 | 0.1 | Story drafted from the Epic-8 delta (DR-1/2/3/4/9). Blast radius measured empirically against a scratch copy of the tree: 23 delta-caused test failures across 9 files, 4 further failures confirmed environment-only. ACs 12–16 added for four live consumers the reorder breaks and three cartridge golden keys that had frozen the defect. Status: ready-for-dev. | Scrum Master (create-story) |
| 2026-08-04 | 1.1 | **Code review findings addressed — 4 of 5 resolved, 1 deliberately deferred (fix iteration 2).** R2: the FR19 "never upgrades" guarantee is now pinned BEHAVIOURALLY through `prosecute()` (`TC-ArgusAgent-PROSECUTOR-001-31` rewritten) — the reviewer was right that the case the old docstring called impossible IS constructible via the independent `scope_paths` parameter, and the `else` branch at `prosecutor.py:474-483` is now actually executed by a test; the false docstring claim is corrected and the white-box rank-map pin is retained as `-32`. R3: the "Measured blast radius" § is annotated in place — `tests/test_dogfood_proof.py` struck from the environment-only list (it is green at `9109e16`), cross-referenced to Variance V2 and Story 8.5 / DR-10. R4: `tests/test_verdict_schema_bump.py` and `tests/fixtures/verdict_schema_v1_row2_artifacts.json` staged in git (`A`); no `.gitignore` rule matches. R5: `ProsecutionResult.verdict_changed` added (plus a mirroring `reclassified:<from>-><to>` rationale token, one token per verdict move) so a row-4 → row-2 reclassification carries a structured signal; nothing persisted, so no canonical payload / content hash / cache key moves — pinned by `-33`. R1 (the row-4 `final-verdict.md` self-contradiction) is **NOT** fixed: AC15's "change no rendered string" fence makes deferral correct, and it is logged as DF-8-1-A for Story 8.3 / DR-11. Suite: **1075 collected / 1072 passed / 3 failed / 0 skipped** — the same three adjudicated reds (2 inherited `test_dogfood_plan`, 1 deferred `test_dogfood_proof`), zero new reds, no test deleted or weakened; mypy clean; AC18 fence still empty-diff. Status: review. | Dev (dev-story, fix) |
| 2026-08-04 | 1.2 | **Code review iteration 2 — PASS. Status → `done`.** All five iteration-1 findings verified resolved against the tree (not the Dev record): R2's rewritten `-31` proven by execution trace to actually reach the FR19 rejection `else` (re-fold really returns `RELEASE_READY`; if-branch body unvisited, `model_copy` reject body visited) with the rank-map pin retained as `-32` and the rejection-path finding carry-over newly pinned — strictly more coverage, none lost; R3 blast-radius annotated in place with the correction block; R4 both evidence files staged `A` with `git check-ignore` exit 1; R5's `verdict_changed` + `reclassified:` token audited as new code — exactly one token per move (`downgraded` ⇒ `verdict_changed`), `ProsecutionResult` provably never serialized (sole consumer `pipeline.py:734` reads `.verdict`; no `rationale` consumer in `argus/`), selection logic untouched so the Story-6.4 never-upgrade invariant holds; R1 correctly left untouched behind the AC15 fence (`generator.py:339` byte-identical) and logged as DF-8-1-A. Reviewer's own re-run: **1075 collected / 1072 passed / 3 failed / 0 skipped / 0 errors** (JUnit XML), mypy clean (69 files), the three reds are exactly the adjudicated carve-out, `test_prosecutor.py` 17→21 with zero names lost, AC18 fence empty-diff. | Reviewer (code-review, iteration 2) |
| 2026-08-04 | 1.0 | **DR-1/2/3/4/9 implemented.** `evaluate_verdict` now folds the binding FOUR-row FR16 table (floor → findings → gates → otherwise); the default block is gone. New `DecisionRow` (4-member `str` enum) + `AuditVerdict.decision_row` (default `None`, A8) + the derived `is_below_floor` predicate; `VERDICT_SCHEMA_VERSION` `"1"` → `"2"` with no migration code. Four downstream consumers fixed so no persisted artifact asserts a falsehood: Prosecutor `_CONSERVATISM_RANK` made a partial order (a row-4 candidate no longer silences a finding it just promoted), `exhaustion.below_floor` keys on row 1, the negative-assurance statement splits row-1/row-4 (row-1 byte-identical), and the report generator branches on the row with **no rendered string changed**. Three self-audit cartridges that had frozen the defect (`NOT_READY_FOR_RELEASE` + `max_blocking=0`) re-pointed. RED-first evidence captured verbatim for AC2 and AC12. AC11 proven against pre-amendment `.argus/` bytes captured at `9109e16`. Suite: 1070 passed / 3 failed (2 inherited `test_dogfood_plan`, 1 delta-caused `test_dogfood_proof` deferred to Story 8.5 by AC18 — Variance V2); mypy clean; all files ≤1200 lines; AC18 fence verified empty-diff. Status: review. | Dev (dev-story) |
