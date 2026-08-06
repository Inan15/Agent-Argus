---
baseline_commit: 9109e16b4e86436a8315ed2cb967b75cdced4296
baseline_note: >-
  HEAD is 9109e16, but the working tree carries Story 8.1's delta UNCOMMITTED
  (git status: 7 modified argus/ + tests/ files, 2 staged-new test files).
  8.2 builds ON TOP of that uncommitted tree. Do NOT stash, revert, or
  `git checkout --` anything — 8.1's work is not recoverable from a commit.
---

# Story 8.2: Critical-subsystem gates an operator can actually satisfy

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
> **This is the SECOND story of Epic 8** ("The Honest Verdict — no block without a finding"). `epic-8` is
> already `in-progress`. **Story 8.1 is `done`** (code-review PASS at iteration 2).
>
> **THIS STORY DELIVERS DR-5, DR-6 and DR-7 (verify-only)** — the heuristic critical-set **eligibility
> filter** (a file Argus can never grade `audited_deep` is ineligible for the *heuristically-derived*
> critical set), the **explicit exemption** of operator `--critical-subsystem` designation from that filter,
> and a **regression pin** on the already-landed pattern-matched `--exclude-critical` (exact / directory
> prefix / glob via `fnmatchcase`). Plus the two boundaries the epic attached to them: **B3** (a vacuously
> satisfied gate must be visible) and **B5** (one explicit, test-pinned precedence order), and the **F1
> inversion** (the false-green counterweight).
>
> **It does NOT deliver:** DR-1/2/3/4/9 (Story 8.1, done); **DR-11's report-surface reconciliation** —
> `argus/reports/plain_english.py`, `argus/reports/generator.py` wording, the empty-critical-set *rendering*
> and the "NOT VOUCHED" unreachable-branch audit are **Story 8.3**; DR-8 + RS-4a (release note / package
> front door — Story 8.4); DR-10 (dogfood re-derivation — Story 8.5, deliberately last so a slip is visible).
>
> **DF-8-1-A is NOT pulled in.** Checked against `epics.md` as instructed: the deferred entry
> (`deferred-work.md`, the row-4 `final-verdict.md` self-contradiction at `argus/reports/generator.py:339`)
> carries `target_story: 8-3 (DR-11 report-surface reconciliation)`, and the epic's **Story 8.3** AC block
> explicitly owns `argus/reports/generator.py` — *"Given `argus/reports/generator.py` … When Story 8.2's
> eligibility filter empties the critical set Then its 'critical paths that withheld `RELEASE_READY`'
> section renders correctly for an empty set"*. The epic genuinely places it in 8.3. **Do not fix it here.**

---

## Story

As an **operator running `argus audit` on a real repository** — who today is told that the
critical-subsystem gate is unmet, opens the report, and finds that **62 of the 112 flagged "critical
subsystems" on this very repo are files Argus structurally cannot ever grade `audited_deep`** (52 test files,
which are the *subject* of the vacuous-test pass and are graded `audited_shallow` by construction, plus 10
zero-definition `__init__.py` modules, which have nothing in them to ground a claim against) —

I want **the heuristically-derived critical set to contain only files Argus can actually grade
`audited_deep`**, with my own `--critical-subsystem` designations still honoured verbatim and my
`--exclude-critical` patterns unchanged,

so that **the gate is a real signal rather than one I learn to ignore.** A gate no run can satisfy is not a
gate; and an operator who learns to ignore one gate learns to ignore all of them — which is how an assurance
product stops assuring anything.

---

## Story Context

### The bug, precisely — measured on THIS tree, not assumed

`argus/ledger/critical_subsystems.py::identify_critical_subsystems` computes

```python
final = {p for p in (heuristic | designated) if not _matches_exclusion(p, excluded)}
```

where `heuristic` is *every* candidate whose 2.1 `assess_criticality` returned `Criticality.CRITICAL`.
`assess_criticality` matches security tokens (`auth`, `crypto`, `secret`, `token`, `permission`, …) over the
file's **content** — which is exactly right for anti-rename-gaming (FR4), and exactly wrong when the file is
a *test* for the security module (its content is full of the same tokens) or a package `__init__.py` that
*re-exports* the security boundary.

The pipeline then grades those files:

| Class | Where graded | Depth it can reach | Can it ever be `audited_deep`? |
|---|---|---|---|
| test file (`is_test_file` true) | `pipeline.py:456-466` → `VacuousTestDetector.run` (`vacuous_test.py:392,400`) or the non-Python shallow branch | `audited_shallow` **always** | **No — by construction** |
| clean parse, **0** definitions | `pipeline.py:384-396` → `is_deep_claim_grounded` False → `grade_entry(claim_present=False)` | `audited_shallow` | **No — nothing to ground** |
| parse-failed / AST-ineligible | `pipeline.py:384-389` | `skipped` | **Not in this run** (see D3 — these stay ELIGIBLE) |
| clean parse, ≥1 definition | `pipeline.py:390-396` | `audited_deep` | **Yes** |

`critical_subsystems_all_deep` is then `False` forever for any repo whose critical set contains a member of
row 1 or row 2. That is a permanently unsatisfiable gate.

### Measured blast radius — HOW it was measured, and on WHICH tree

> ⚠️ **Method matters here.** Story 8.1's blast-radius measurement was taken on a *scratch copy* of the tree
> with no `.git` and no `_bmad-output/`, and that environment difference caused it to **misclassify
> `tests/test_dogfood_proof.py`** as an environment-only failure when it was in fact delta-caused (see 8.1's
> review finding R3 / Variance V2). Everything below was therefore measured **on the real working tree, in
> place** — `d:/ProjectX/XAgents/XAgents/ArgusAgent`, HEAD `9109e16` **plus Story 8.1's uncommitted delta**,
> `.git` and `_bmad-output/` present — using the **shipped `argus` functions by import** (`resolve_source_state`
> → `build_ast_index` → `assess_criticality` / `is_test_file` / `is_deep_claim_grounded`), never a
> re-implementation. Cartridge figures come from **real `run_audit_detailed` runs** into a temp store, with
> the recomputed critical set **cross-checked against the pipeline's own
> `verdict.critical_subsystems_all_deep`** (they agree on all 10 cartridges — that agreement is the
> measurement's own self-check). No `.argus/` was written into this repo.

**(A) The ArgusAgent repository itself, defaults (`--coverage-scope application`):**

| Quantity | Measured |
|---|---|
| files in the AST index | **145** |
| heuristic `CRITICAL` hits (today) | **112** |
| … of which **test files** | **52** |
| … of which **clean-parse, zero-definition** modules | **10** (`argus/__init__.py` + 9 package `__init__.py`) |
| … of which **parse-failed / AST-ineligible** | **0** |
| … **deep-gradable survivors** | **50** |
| critical paths **not** `audited_deep` today | **62** |
| critical paths **not** `audited_deep` after DR-5 | **0** |
| application-scope deep ratio | **57/73** ≈ 78 % (≥ the 3/5 gate) |

> The epic's AC says *"the previously unreachable blockers (51 test files + 10 `__init__.py`) are gone — the
> measured 62 → ~0"*. **Two corrections from the live measurement:** it is **52** test files, not 51 (the
> epic's own "51 + 10" already did not sum to its own "62"); and the resulting count is exactly **0**, not
> "~0". The **62** total is confirmed. Use the measured numbers.

**⚠️ Consequence you must expect (record it; do NOT pin it as an AC).** With the critical clause satisfied,
78 % application deep coverage, and the zero blocking findings this repo reports today, `argus audit .` on
ArgusAgent moves to **FR16 row 3 → `RELEASE_READY` / exit `0`**. That is the *honest* result of the amended
contract, and it is why the epic sequences the dogfood re-derivation **last** (Story 8.5 / DR-10, boundary
B1: *"pinning a predetermined verdict on an assurance tool's own proof artifact invites the story to be made
to pass"*). This story **records** the actual observed result in the Dev Agent Record; it does **not**
require any particular verdict, and it does **not** touch a proof artifact.

**(B) The 10 self-audit cartridges — real `run_audit_detailed` runs:**

| Cartridge | Verdict today | Heuristic critical set | Removed by DR-5 | Survivors | `all_deep` today → after |
|---|---|---|---|---|---|
| `vacuous_basic` | `NOT_READY_FOR_RELEASE` / 2 | 0 | 0 | 0 | True → True |
| `hardcoded_secret` | `RELEASE_READY` / 0 | 1 | 0 | 1 (deep) | True → True |
| `orphan_basic` | `INSUFFICIENT_COVERAGE` / 3 | 0 | 0 | 0 | True → True |
| `clean_control` | `RELEASE_READY` / 0 | 0 | 0 | 0 | True → True |
| **`holdout_vacuous`** | `NOT_READY_FOR_RELEASE` / 2 | **1** (`tests/test_inventory.py`) | **1** | **0** | **False → True** |
| `evidence_sentinel` | `RELEASE_READY` / 0 | 1 | 0 | 1 (deep) | True → True |
| `nonascii_unicode` | `NOT_READY_FOR_RELEASE` / 2 | 0 | 0 | 0 | True → True |
| `tool_breadth` | `RELEASE_READY` / 0 | 0 | 0 | 0 | True → True |
| `vacuous_heuristic_basic` | `INSUFFICIENT_COVERAGE` / 3 | 0 | 0 | 0 | True → True |
| `cross_partition_seam` | `INSUFFICIENT_COVERAGE` / 3 | 0 | 0 | 0 | True → True |

**Exactly one cartridge is touched: `holdout_vacuous`.** Its lone critical path is a test file, so DR-5
empties its critical set and `critical_subsystems_all_deep` flips `False → True`. **Its verdict must NOT
move**: `holdout_vacuous` carries a real AST-corroborated blocking finding (`max_blocking=1`), and under the
Story-8.1 four-row table **row 2 (findings) is evaluated before row 3 (gates)** — so the verdict stays
`NOT_READY_FOR_RELEASE` / exit `2`. Its **persisted verdict payload does change bytes**
(`critical_subsystems_all_deep` `false → true`, and the `critical_subsystems_not_deep` key is popped when
the clause is satisfied — `verdict_gate.py:432-433`). **`CARTRIDGE_REGISTRY` needs no edit.**

**(C) Baseline suite state — re-measured in place, not inherited from the 8.1 record:**

```
PYTHONIOENCODING=utf-8 python -m pytest tests/ -q     →  1075 collected, 3 failed
  FAILED tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation
  FAILED tests/test_dogfood_plan.py::test_budget_reuses_the_31_accountant_no_fork
  FAILED tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run
```

Exactly the three user-adjudicated reds. See **Known-red carve-out** below. **Any fourth red is yours.**

### The contracts this story touches — all frozen, all REUSE-not-fork (§3.3 / AR7)

- **`argus/ledger/critical_subsystems.py` (Story 2.3, 378 lines).** PURE. Its module docstring **LOCKS its
  import set**: *"Imports ONLY the 2.1 `depth_semantics` … + the 1.2 ledger models"*. It is a `ledger/`
  module; `detectors/` and `audit/` are **higher** layers. It is in `_MODULES_UNDER_GUARD`
  (`tests/test_no_web_imports.py:87`). **Do not import `argus.detectors.*` or `argus.audit.*` from it.**
- **The merge formula is LOCKED and documented** at `critical_subsystems.py:45-53`: final =
  `(heuristic ∪ operator_designated) − operator_excluded`, **exclude wins on a tie**. This story inserts the
  eligibility filter *inside* the `heuristic` term and changes nothing else about the formula.
- **The conservative unmatched-path policy is LOCKED** (`:54-61`): an operator-designated path matching no
  candidate stays in `paths` **and** in `designated_but_unmatched`, so an operator typo can only make the
  gate **stricter**. Unchanged, and DR-6 explicitly re-pins it.
- **`_matches_exclusion` uses `fnmatchcase`, never `fnmatch`** (`:225-228`) — host case-folding would break
  byte-identity across hosts (NFR-P1/AR4). DR-7 is **verify-only**: pin it, write no new matcher.
- **`CriticalCandidate` / `CriticalSubsystemSet` are `frozen=True, extra="forbid"`.** Any new field
  **must carry a default**, or existing construction sites and persisted read-back break. (Same constraint
  8.1 met for `decision_row` under assumption A8.)
- **`CriticalSubsystemSet` is PERSISTED** — `pipeline_persist.persist_critical_subsystems` writes
  `critical.model_dump(mode="json")` to `state/`, content-addressed, stamped with
  `CRITICAL_SUBSYSTEMS_SCHEMA_VERSION`. It has **no omit-when-empty machinery**: every field is serialized.
- **`Criticality` (2.1) does not grow**, and `assess_criticality` is **not modified**. This story does not
  change what "critical" *means*; it changes which critical files the **heuristic** set may contain.
- **`Verdict` does not grow, `AuditVerdict` gains no field, `VERDICT_SCHEMA_VERSION` stays `"2"`.**
  8.1 bumped it; a second bump in the same epic for an unrelated reason is not sanctioned.
- **The advisory moat and FR16 row order are untouched.** This story supplies a different **input** to the
  gate; it does not touch `evaluate_verdict`.

### Live consumers of the critical set — read before you change anything

| Site | What it does | Impact of this story |
|---|---|---|
| `argus/pipeline.py:434-439` | builds `CriticalCandidate` per file | ⚠️ **the seam — AC7.** Must supply the eligibility fact |
| `argus/pipeline.py:456` | `is_test_file(rel, ast_entry=entry)` for the grading branch | ⚠️ compute **once** and reuse — AC7 |
| `argus/pipeline.py:686-694` | `identify_critical_subsystems` → `critical_subsystems_not_deep` → the gate | none — call signature unchanged |
| `argus/pipeline.py:1068` (resume) | builds candidates from **resume-target entries only** | none new — see the pre-existing-asymmetry note in Dev Notes. **Do not "fix" it here** |
| `argus/pipeline_persist.py:212-235` | persists `CriticalSubsystemSet` | ⚠️ payload gains a key + a stamp — AC8/AC12 |
| `argus/verdict/negative_assurance.py:240-280` | `_critical_narration` splits `critical.paths` into examined-deep / not-examined-deep | reads the **filtered** set; no code change (see D5) |
| `argus/reports/generator.py:80-136,332` | `_render_critical_blockers` (returns `[]` for an empty set) + the dilution hint | **Story 8.3 owns it.** No change here |
| `argus/reports/plain_english.py:162-178` | branches on `critical_subsystems_all_deep` | **Story 8.3 owns it (DR-11).** No change here |
| `argus/cache/key.py:227-231,276-277` | folds `critical_paths` / `excluded_critical_paths` — the **operator intent**, not the computed set | **none.** The memo cache fingerprints *recording*-producing inputs; the verdict is re-folded every run. **No cache-busting is needed or wanted** |

### Known-red carve-out — inherited/deferred, adjudicated by the user, DO NOT touch

Three tests are red at this story's baseline and must be **left red and unmodified**:

1. `tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation`
2. `tests/test_dogfood_plan.py::test_budget_reuses_the_31_accountant_no_fork`
   — both **inherited**; red at `9109e16` too (confirmed by the 8.1 reviewer in a clean detached worktree).
3. `tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run`
   — **delta-caused by 8.1 and deliberately left red.** It is a rot check on `minions-dogfood-proof.md`,
   which is **Story 8.5 / DR-10**'s deliverable; the epic sequences 8.5 last *by design, so a slip is
   visible*. **This story will change its failure message again** (the live re-derivation moves once the
   critical clause clears). That is expected. **Do not fix it, do not weaken it, do not touch
   `minions-dogfood-proof.md`.**

**Do not absorb these into this story's result.** Record their exact state verbatim in the Dev Agent Record.

---

## Acceptance Criteria

**Eligibility filter (DR-5)**

1. **Given** a candidate file that `assess_criticality` flags `CRITICAL` from security tokens in its content
   **and** that `is_test_file` classifies as a test file,
   **When** the **heuristic** critical set is derived,
   **Then** it is **excluded** — a test file is `audited_shallow` **by construction** (it is the *subject* of
   the vacuous-test pass, never a target of deep grounding),
   **And** this is demonstrated **RED-first**: a committed test that fails against the current
   implementation before the fix, with the observed RED output recorded verbatim in the Dev Agent Record.

2. **Given** a **clean-parsed module with zero definitions** (`__init__.py`, constants-only, re-export,
   docstring-only) that `assess_criticality` flags `CRITICAL`,
   **When** the heuristic set is derived,
   **Then** it is **excluded** — there is nothing in it to ground a deep claim against, and the pipeline
   already downgrades exactly this class to `audited_shallow` via `is_deep_claim_grounded`.

3. **Given** a **parse-failed** or **AST-ineligible** file (no grammar installed, syntax error) that is
   flagged `CRITICAL`,
   **When** the heuristic set is derived,
   **Then** it is **KEPT** — it is *not* `audited_shallow` by construction, it is `skipped` **by
   circumstance**, and silently dropping an unparseable security-relevant file from the critical set is a
   false-green (LOCKED decision **D3**; FR4 enumerates exactly two by-construction classes and this is not
   one of them). Pinned by a test asserting the survival explicitly, with the reason in its docstring.

**Operator channels (DR-6, DR-7)**

4. **Given** an operator passes `--critical-subsystem` for **(a)** a test file, **(b)** a clean-parsed
   zero-definition module, **or (c)** a path matching nothing,
   **When** the set is derived,
   **Then** all three designations are **honoured** and appear in `paths` with origin
   `OPERATOR_DESIGNATED`; **(c)** additionally appears in `designated_but_unmatched`; and each can still
   withhold `RELEASE_READY` — **operator designation is exempt from the eligibility filter** (DR-6),
   **And** an operator-designated path is **never** recorded as eligibility-excluded (AC8's disclosure map
   must not contain it).

5. **Given** `--exclude-critical` with **an exact path**, **a directory prefix** (`tests`, `tests/`) and
   **a glob** (`argus/*/__init__.py`, `*_test.py`),
   **When** applied,
   **Then** all three match via `fnmatchcase` (case-sensitive, host-independent), **exclude still wins on a
   tie** with `--critical-subsystem`, and an exclude path matching nothing is still a harmless no-op —
   a **regression pin on already-landed behaviour (DR-7), with NO new implementation**. `_matches_exclusion`
   ends this story **byte-identical** to its current source.
   ⚠️ **Most of this already exists** — `tests/test_critical_exclusion_patterns.py` carries nine tests
   covering exact / trailing-slash / directory-prefix / glob / prefix-must-be-a-directory-boundary /
   exclude-wins / unmatched-designation / no-op / determinism. **Verify them green and add only the two
   things they do not yet assert:** (i) that the matcher is `fnmatchcase` and **not** `fnmatch`
   (source-level or behavioural, so a host case-folding regression is caught), and (ii) that the DR-7
   behaviours are unchanged **in the presence of** the new eligibility filter. Do not rewrite the nine.

6. **Given** a path that is simultaneously heuristic-`CRITICAL`, **eligibility-ineligible**,
   **operator-designated** *and* **operator-excluded**,
   **When** the set is derived,
   **Then** a **single explicit precedence order governs and is pinned by test, not left to implementation
   order** (boundary **B5**). The LOCKED order (see **D2**) is:
   **(i) eligibility filter — heuristic term ONLY → (ii) union with operator designation (exempt) →
   (iii) minus operator exclusion (pattern-matched; exclude wins).**
   All four two-way and the one four-way combinations are pinned as an explicit truth table.

**The seam (how the eligibility fact reaches the pure module)**

7. **Given** `argus/ledger/critical_subsystems.py` is PURE, is in `_MODULES_UNDER_GUARD`, and its docstring
   LOCKS its import set to `depth_semantics` + the 1.2 ledger models,
   **When** the filter is implemented,
   **Then** the eligibility fact is **computed in the impure shell and carried as DATA** on
   `CriticalCandidate` (LOCKED decision **D1**) — `critical_subsystems.py` gains **no new import**, and
   `test_no_web_imports.py` plus the module's AST-purity scan
   (`TC-ArgusAgent-LEDGER-001-146`) stay green **unmodified**,
   **And** the shell **REUSES** `is_test_file` and `is_deep_claim_grounded` **by import — no fork, no second
   predicate** (§3.3 / AR7),
   **And** `is_test_file(rel, ast_entry=entry)` is evaluated **once per file** and the same value drives both
   the grading branch (`pipeline.py:456`) and the eligibility fact, so the two stages **cannot disagree**
   (the same reasoning `_assessment_scope_paths` records at `pipeline.py:640-645`),
   **And** the new field's **default means ELIGIBLE**, so a directly-constructed `CriticalCandidate`
   (11 such sites exist across `tests/`) keeps its exact current behaviour and the failure mode of a
   forgetful caller is **over-inclusion (a stricter gate)**, never a false green.

**Disclosure — a vacuously satisfied gate must be visible (boundary B3)**

8. **Given** a repository whose heuristic critical hits were **all** ineligible, so the filter empties the
   critical set,
   **When** the run completes,
   **Then** the persisted `CriticalSubsystemSet` **discloses every path the eligibility filter removed and
   why**, via a new default-carrying field keyed path → a **closed** `CriticalIneligibility` reason token
   (LOCKED decision **D4**),
   **And** the map contains **only** paths that would otherwise have been in the heuristic set — never every
   ineligible file in the repo,
   **And** an **empty** critical set is therefore distinguishable on disk from a repo that genuinely had no
   critical subsystems,
   **And** a test proves that **no surface reachable from this story asserts "all critical subsystems
   examined deeply" (or any equivalent positive claim) for a vacuously-satisfied gate** — the persisted
   negative-assurance `assurance_statement`, `scope_statement.critical_examined_deep` and the report
   surfaces are all inspected for such a claim and none is made. *(Adding the positive prose that names the
   vacuity for a human is **Story 8.3 / DR-11**; this story's obligation is the machine-readable disclosure
   plus the proof that no false positive claim exists.)*

9. **Given** the meaning of `CriticalSubsystemSet.paths` changes (it is now eligibility-filtered) and the
   model gains a field it always serializes,
   **Then** `CRITICAL_SUBSYSTEMS_SCHEMA_VERSION` moves `"1"` → `"2"` (LOCKED decision **D4**; NFR-M2's
   sanctioned lever), sets persisted before this story are **not rewritten** and keep their `"1"` stamp (no
   migration code), and `tests/test_critical_subsystems.py::test_schema_version_is_localized_constant`
   (`TC-ArgusAgent-LEDGER-001-148`) is re-pointed to `"2"` — the only edit that test needs.

**The false-green counterweight (inversion F1) — the most important AC in this story**

10. **Given** a repository containing a **genuinely security-relevant module that is `audited_shallow` and
    NOT operator-designated** — the epic's own example: a clean-parsed zero-definition `__init__.py` that
    re-exports a security boundary —
    **When** the eligibility filter removes it from the heuristic critical set,
    **Then** **both** legs are proven and committed:
    **(a) the gate still withholds `RELEASE_READY` where it should** — with the filter applied and that file
    removed, a fixture whose coverage ratio is below `3/5` (or which carries ≥1 blocking finding) still does
    **not** reach `RELEASE_READY`; and
    **(b) the loosening is measured, not hidden** — a sibling fixture identical except that every *other*
    gate is met **does** now reach `RELEASE_READY` where it previously could not, and that transition is
    asserted explicitly and documented in Dev Notes as the **accepted residual exposure**,
    **And** the existing clean-control / trap cartridges (`clean_control`, `hardcoded_secret`,
    `evidence_sentinel`, `tool_breadth`) and the three genuinely-blocking cartridges (`vacuous_basic`,
    `holdout_vacuous`, `nonascii_unicode`, each `max_blocking=1`) keep their **exact** current
    verdict/exit expectations — **the false-green direction must not loosen anywhere else.**
    *(Rationale: every other guard in this delta points at "don't over-block". DR-5 plus the already-landed
    `--coverage-scope application` default make `RELEASE_READY` **easier** to reach — twice. The PRD names
    **zero false-`RELEASE_READY`** as the fatal error, and the existing clean controls only guard the
    false-**red** direction. Without this AC the delta loosens the gate twice with nothing testing the
    loosening.)*

**Self-audit (the epic's headline AC)**

11. **Given** ArgusAgent audited against itself with defaults,
    **When** the heuristic critical set is derived,
    **Then** the previously unreachable blockers are gone: the measured **62** critical paths that can never
    be `audited_deep` (**52** test files + **10** zero-definition `__init__.py`) become **0**, and the
    heuristic critical set is **50** deep-gradable files,
    **And** the resulting end-to-end verdict of `argus audit .` is **RECORDED verbatim** in the Dev Agent
    Record (verdict, exit code, decision row, deep ratio, blocking count) — **and is NOT pinned as a
    required value** (boundary B1's reasoning: a predetermined verdict on an assurance tool's own repository
    invites the story to be "made to pass"). Story 8.5 / DR-10 owns the proof artifacts.

**Determinism, purity and the byte-delta proof**

12. **Given** the persisted `CriticalSubsystemSet` payload necessarily changes (the new always-serialized
    field + the version stamp),
    **When** `tests/test_verdict_schema_bump.py` runs,
    **Then** it is **EXTENDED, never relaxed**:
    `TC-ArgusAgent-VERDICT-003-01`'s "every non-verdict artifact is byte-identical" assertion is refined so
    that the **critical-subsystem envelope** may differ from the captured pre-amendment fixture by
    **exactly** `schema_version` `"1"→"2"` and the added key — and **reverting exactly those two reproduces
    the old bytes**, mirroring `-003-02`'s existing shape; **every other artifact stays byte-identical**;
    the artifact **count** is unchanged; and no assertion is deleted or widened to "ignore".
    ⚠️ **`tests/fixtures/verdict_schema_v1_row2_artifacts.json` MUST NOT be regenerated.** It is the
    pre-amendment evidence captured at `9109e16`; regenerating it destroys the proof.
    *(`vacuous_basic` has an empty critical set — measured — so its added key is empty and the stamp is the
    only substantive delta.)*

13. **Given** two runs over the same repository,
    **When** compared byte-for-byte,
    **Then** they are identical; `paths`, `designated_but_unmatched` and the new disclosure map are
    deterministic and order-independent under re-ordered candidate input (extend
    `TC-ArgusAgent-LEDGER-001-152`); the module stays **PURE** (no I/O, no clock, no `uuid`/`random`, no
    LLM); there is **no `float`** anywhere (the single 1.1 `canonical.dumps` rejects float leaves — keep it
    as the proof); and no emitted field carries an absolute host path, source byte or secret byte (NFR-S1 —
    the new map carries only repo-relative POSIX paths and closed enum tokens).

14. **Given** `holdout_vacuous` is the one cartridge whose critical set the filter empties,
    **When** the self-audit harness runs,
    **Then** its verdict is still `NOT_READY_FOR_RELEASE` / exit `2` with its `vacuous_test_ast` golden
    finding unchanged (FR16 **row 2 precedence** — a real finding outranks the gates), and
    **`tests/cartridges/_registry.py` is NOT modified by this story**. A test asserts the row-2 precedence
    explicitly for this case so the flip is understood rather than merely survived.

**Whole-system**

15. **Given** the delta has landed,
    **When** the full suite runs (`PYTHONIOENCODING=utf-8 python -m pytest tests/ -q`),
    **Then** the **only** red is the three-test adjudicated carve-out above (2 inherited + 1 deferred to
    8.5), **no test is deleted, skipped, weakened or re-pointed to assert less**, the collected count does
    not fall below **1075**, `python -m mypy argus` is clean, and no source file exceeds 1200 lines
    (NFR-M1 — `critical_subsystems.py` is 378 today).

16. **Given** the epic's story boundaries,
    **Then** this story does **not** modify `argus/reports/plain_english.py`, `tests/test_plain_english.py`,
    `argus/reports/generator.py`, `argus/verdict/verdict_gate.py`, `argus/verdict/prosecutor.py`,
    `argus/cli.py`, `argus/__init__.py`, `argus/ledger/depth_semantics.py`,
    `tests/cartridges/_registry.py`, `argus/dogfood/*`, `minions-dogfood-proof.md`, or either
    `final-verdict.md` — those are Stories 8.1 (done) / 8.3 / 8.4 / 8.5. **Verified by `git diff` → empty
    for each.** No new cartridge is added to `CARTRIDGE_REGISTRY` (it is the ground truth of the 6.6
    precision replay harness, `argus/precision/replay_harness.py:91,222`, and DF-6-6-A's gate reads that
    figure).

---

## Tasks / Subtasks

- [x] **Task 1 — RED first (AC1).**
  - [x] Write the failing tests for a heuristic-`CRITICAL` **test file** and a heuristic-`CRITICAL`
        **clean-parse zero-definition module** being excluded from the heuristic set, against the
        **current** implementation. Run them; capture the RED output **verbatim** for the Dev Agent Record.
  - [x] Write the failing test for AC8's disclosure map (red for a "field does not exist" reason — note
        that).
  - [x] Do **not** flip the story to `review` before the tests exist (process watch-item AI-E2-1).

- [x] **Task 2 — Carry the eligibility fact as data (AC7).** `argus/ledger/critical_subsystems.py`
  - [x] Add `class CriticalIneligibility(str, enum.Enum)` with **exactly two** members —
        `TEST_FILE = "test_file"`, `ZERO_DEFINITION_MODULE = "zero_definition_module"` (the LOCKED shape in
        **D4**). Export it in `__all__`. Add a membership pin test mirroring
        `TC-ArgusAgent-LEDGER-001-148`'s style.
  - [x] Add `CriticalCandidate.ineligibility: CriticalIneligibility | None = Field(default=None, …)`.
        **The default is mandatory** (`extra="forbid"`, 11 direct construction sites in `tests/`).
        `None` means **eligible**.
  - [x] Update the module docstring's "Decisions LOCKED here" block with the eligibility rule, the
        precedence order (**D2**) and the DR-6 exemption. State explicitly that the module still imports
        only `depth_semantics` + the 1.2 ledger models.

- [x] **Task 3 — Apply the filter to the heuristic term only (AC1, AC2, AC3, AC4, AC6).**
      `identify_critical_subsystems`
  - [x] Build `heuristic` as today, then **partition** it: a candidate with
        `criticality is CRITICAL` **and** `ineligibility is not None` goes to the excluded map instead of
        the heuristic set.
  - [x] Keep the merge formula otherwise **verbatim**:
        `final = (heuristic_eligible ∪ designated) − excluded` with `_matches_exclusion` unchanged.
  - [x] A path that is ineligible **and** operator-designated is **IN** `final` with origin
        `OPERATOR_DESIGNATED` and is **NOT** recorded in the excluded map.
  - [x] `designated_but_unmatched` semantics unchanged.
  - [x] Add the truth-table test for AC6 (all combinations of ineligible × designated × excluded).

- [x] **Task 4 — Disclose it (AC8, AC9).** `argus/ledger/critical_subsystems.py`
  - [x] Add `CriticalSubsystemSet.heuristic_excluded_ineligible: dict[str, CriticalIneligibility] =
        Field(default_factory=dict, …)` — mirrors the existing `origins` dict shape; the single 1.1
        serializer sorts keys, so determinism is inherited (pin it anyway).
  - [x] Bump `CRITICAL_SUBSYSTEMS_SCHEMA_VERSION` to `"2"`. **No migration code, no rewrite pass.**
  - [x] Re-point `TC-ArgusAgent-LEDGER-001-148` to `"2"` (the only edit that test needs).
  - [x] Write the AC8 "no surface makes a vacuous positive claim" test: build a run whose critical set is
        emptied by the filter, then assert the persisted `assurance_statement`,
        `scope_statement.critical_examined_deep/critical_not_examined_deep` and the rendered report contain
        **no** "all critical subsystems …" / "all criticals examined" style claim.

- [x] **Task 5 — Wire the shell (AC7).** `argus/pipeline.py::_detect_per_file`
  - [x] Hoist `is_test_file(rel, ast_entry=entry)` to a single local **before** the candidate is built
        (currently evaluated at `:456`, after the `candidates.append` at `:434`) and use that one value in
        **both** places.
  - [x] Compute the ineligibility token by **REUSE**:
        `TEST_FILE` if that local is true; else `ZERO_DEFINITION_MODULE` if the entry is **cleanly parsed**
        (`not entry.parse_failed and entry.ast_eligible`) **and** `is_deep_claim_grounded(entry)` is
        `False`; else `None`. ⚠️ The clean-parse guard is **load-bearing** —
        `is_deep_claim_grounded` also returns `False` for parse-failed / AST-ineligible entries, which
        **must stay eligible** (AC3).
  - [x] Confirm `argus/audit/grounding.is_deep_claim_grounded` is imported in `pipeline.py` already (it is,
        via `_grade_non_test_source`) — add no second predicate.
  - [x] Leave the resume path's candidate handling (`:1068`) alone (see Dev Notes).

- [x] **Task 6 — The F1 counterweight (AC10).**
  - [x] Build the two-leg fixture: a staged repo with a security-token-bearing, clean-parsed,
        **zero-definition** `__init__.py` re-exporting a security boundary, and **not** operator-designated.
  - [x] Leg (a): with another gate genuinely unmet, `RELEASE_READY` is still withheld.
  - [x] Leg (b): with every other gate met, `RELEASE_READY` **is** now reached where it previously was not —
        assert the transition explicitly and write the accepted residual exposure into Dev Notes.
  - [x] Also pin the operator's remedy: `--critical-subsystem <that path>` restores the block (the DR-6
        lever is what makes the residual acceptable).
  - [x] **Do NOT add a cartridge to `CARTRIDGE_REGISTRY`** (AC16).

- [x] **Task 7 — Extend the byte-delta proof (AC12, AC13, AC14).**
  - [x] `tests/test_verdict_schema_bump.py`: refine `-003-01` and add the revert-proof for the
        critical-subsystem envelope. **Do not regenerate the fixture. Do not weaken an assertion.**
  - [x] Extend `TC-ArgusAgent-LEDGER-001-152` (order-independence) to cover the new map.
  - [x] Add the `holdout_vacuous` row-2-precedence test (AC14).
  - [x] Re-run the import-isolation gate and the module AST-purity scan with the changed modules.

- [x] **Task 8 — Measure and record (AC11, AC15, AC16).**
  - [x] Re-derive the 145 / 112 / 52 / 10 / 0 / 50 figures on the **real tree** (do not trust this story's
        table — the standing rule since Epic 6 is *verify independently*), and record them.
  - [x] Run `argus audit .` end-to-end and record verdict / exit / decision row / deep ratio / blocking
        count **verbatim**. Do not adjust anything to make it a particular value.
  - [x] Full suite + `mypy`; record counts and the three carve-out reds verbatim.
  - [x] `git diff` over every AC16 path → confirm **empty**.

### Review Findings

*(code review, iteration 1, 2026-08-05 — adversarial re-verification against the working tree.
Everything below was reproduced by the reviewer; nothing is taken from the Dev Agent Record on trust.)*

- [x] **[Review][Patch] D3/AC3 FALSE GREEN — a parse-failed production module with an ambiguous
      `*_test.py` name is silently dropped from the critical set** `[argus/pipeline.py:423-424]`
      **Severity: HIGH.** The `if is_test:` branch is evaluated *before* the clean-parse guard, so the
      guard the docstring calls "LOAD-BEARING" does not protect the `TEST_FILE` path at all.
      `is_test_file`'s tier-3 disambiguator `_exhibits_test_definitions`
      (`argus/detectors/vacuous_test.py:211-222`) **deliberately answers `True` for any entry it cannot
      read** (parse-failed / AST-ineligible / wrong-shaped) — a failure direction calibrated for its
      ORIGINAL consumer (grading, where "assume test" is the conservative side). Story 8.2 reuses that
      same value for a SECOND consumer where the identical direction is the **loosening** one.
      Reproduced end-to-end by the reviewer on a staged repo:
      ```
      app/auth_test.py    critical  parse_failed=True  depth=skipped  ineligibility=TEST_FILE  -> REMOVED + disclosed as "test_file"
      app/broken_auth.py  critical  parse_failed=True  depth=skipped  ineligibility=None       -> KEPT (correct)
      ```
      The *same* `app/auth_test.py` with a clean parse is correctly kept (pinned by
      `TC-ArgusAgent-PIPELINE-002-02`), so the classification **flips on parse state** — shallow by
      CIRCUMSTANCE, exactly the class **D3** and **AC3** say must stay ELIGIBLE. Two harms: (i) a
      security-token-bearing file the tool could not read exits the gate silently — the false-green class
      the PRD names as fatal; (ii) the **B3 disclosure map records a FALSE reason** (`test_file`) for a
      production module, so the operator-facing disclosure misinforms.
      *Reachability:* needs `*_test.py`/`*test.py` **outside** a test dir, not `test_`-prefixed,
      heuristic-CRITICAL, and parse-failed. **Zero instances on this repo today** (reviewer measured 0
      parse-failed among the 115 criticals), so this is a latent defect, not a live regression — but the
      repo does ship exactly that filename shape (`argus/detectors/vacuous_test.py`).
      **Suggested fix — do NOT simply hoist the parse guard above `if is_test:`.** That would also make
      grammar-less / parse-failed *genuine* test files (tier 1/2, graded `audited_shallow` BY
      CONSTRUCTION at `pipeline.py:502`) eligible again and re-create the unsatisfiable gate DR-5 exists
      to kill. Distrust the test label only when it came from the AMBIGUOUS tier **and** the content was
      unreadable. Export the predicate from the module that OWNS the classification (AR7 no-fork — do not
      re-declare `_AMBIGUOUS_PYTHON_TEST_SUFFIXES` in `pipeline.py`), e.g.
      `argus/detectors/vacuous_test.py::is_test_classification_content_dependent(file_path) -> bool`
      (True iff the path reaches tier 3 — neither the test-directory nor the unambiguous-name tier
      fired), then:
      ```python
      if is_test:
          if (entry.parse_failed or not entry.ast_eligible) and is_test_classification_content_dependent(entry.file_path):
              return None  # the "test" label was a GUESS made because the file could not be read
          return CriticalIneligibility.TEST_FILE
      ```
      Pin it with a seam test that stages a syntax-error `app/auth_test.py` beside `-002-02`'s
      clean-parse twin and asserts the two land on the SAME side (eligible) once the content is
      unreadable.

- [x] **[Review][Patch] The AC3 fold test is tautological — it cannot catch a D3 regression**
      `[tests/test_critical_eligibility.py:93-111]` **Severity: MEDIUM.**
      `TC-ArgusAgent-LEDGER-001-158` hands `identify_critical_subsystems` a candidate with
      `ineligibility=None` and asserts it survives — that restates the fold rule, it does not test D3.
      Its own docstring concedes *"The shell expresses this by leaving `ineligibility` at `None` for such
      an entry"*, i.e. the property under test lives entirely in the SHELL, which this test never
      exercises. Consequence: the only real D3 pin is `TC-ArgusAgent-PIPELINE-002-01`, and it covers only
      the *unambiguously-named* parse-failed file — which is precisely why the finding above went
      undetected. Weak / implementation-coupled test (it asserts the implementation's own input, not the
      behaviour). **Suggested fix:** rescope `-158`'s docstring to what it actually pins (the fold
      contract: `ineligibility is None ⇒ survives`) and move the AC3 claim to the seam — parametrize
      `-002-01`'s parse-failed row over BOTH filename shapes (`app/broken_auth.py` and
      `app/auth_test.py`), asserting `ineligibility is None` and `depth is SKIPPED` for each.

- [x] **[Review][Patch] The story's two new test modules are UNTRACKED and UNSTAGED**
      `[tests/test_critical_eligibility.py, tests/test_critical_eligibility_pipeline.py]`
      **Severity: MEDIUM.** `git check-ignore` exits `1` for both (they are NOT ignored) and `git status`
      reports them `??`. **30 of this story's 33 new tests** — the entire DR-5/DR-6 fold evidence, the
      AC6 truth table, the AC8 disclosure proof, the AC10/F1 counterweight and the AC14 `holdout_vacuous`
      row-2 pin — vanish the moment this delta is committed, and the suite is 30 tests thinner for
      everyone else. This is the identical finding class raised at iteration 1 of Story 8.1 (its R4), and
      8.1's own new evidence is correctly staged (`tests/fixtures/verdict_schema_v1_row2_artifacts.json`
      and `tests/test_verdict_schema_bump.py` both show `A`), so the remediation is already established
      in this epic. **Suggested fix:**
      `git add tests/test_critical_eligibility.py tests/test_critical_eligibility_pipeline.py`.

- [x] **[Review][Defer] `argus/pipeline.py` finished at 1199/1200 lines — NFR-M1 headroom is exhausted**
      `[argus/pipeline.py:1]` — deferred, logged as **DF-8-2-A** in `deferred-work.md`
      (`target_story: 8-3`). **Severity: LOW; not a defect in this delta.** The dev complied with this
      story's explicit "No new module" constraint and recorded the consequence in the Completion Notes,
      which was the correct call under the fence. Recorded so the constraint is not discovered at edit
      time: `_critical_ineligibility` is a cohesive derived-fact helper living in a module that already
      owns intake wiring, per-file detection, scope resolution, assembly, persistence and resume (SRP
      pressure / low cohesion), and the next line added to `pipeline.py` breaches NFR-M1.

#### Verified clean by the reviewer (recorded so iteration 2 need not re-derive)

- **D1 purity holds.** `argus/ledger/critical_subsystems.py` imports only `enum`, `fnmatchcase`,
  `typing`, `pydantic`, `coverage_ledger`, `depth_semantics` (+ a `TYPE_CHECKING`-only entry). **No
  function-local / deferred imports anywhere in the module** (grepped). `tests/test_no_web_imports.py`
  and the AST purity scan `TC-ArgusAgent-LEDGER-001-146` pass **unmodified** (73 passed).
- **DR-7 is genuinely verify-only.** `_matches_exclusion` compared programmatically against
  `9109e16` — 1424 characters both sides, **byte-identical**.
- **The 62-vs-65 discrepancy is BENIGN and fully reconciled.** Reviewer re-measured independently via
  `resolve_source_state` → `build_ast_index` → the shipped predicates: **147** indexed, **115** heuristic
  CRITICAL, **65** ineligible (`55 test_file` + `10 zero_definition_module`), **50** eligible survivors,
  **0** parse-failed among the criticals. `65 − 3` (this story's own `test_critical_eligibility.py`,
  `test_critical_eligibility_pipeline.py`, and `test_verdict_schema_bump.py`, which the delta's own edits
  flipped `NORMAL → CRITICAL`) = **62**, the SM's figure exactly. Both figures the AC actually asserts
  (**0** and **50**) match.
- **The new `RELEASE_READY` is EARNED, not manufactured by over-broad exclusion.** The persisted
  `argus.pipeline.critical_subsystems` artifact carries **50 paths, `origins` all `heuristic`**, and the
  live fold reports `critical_subsystems_all_deep=True` with `critical_subsystems_not_deep=()` — the
  clause is satisfied by 50 genuinely deep-graded modules, **not vacuously**. The reviewer audited every
  one of the 65 exclusions for over-breadth: **zero** files labelled `test_file` sit outside a test
  directory or lack a `test_` prefix, and **all 10** `zero_definition_module` entries have literally 0
  definitions and are `__init__.py`. Repo-wide the run is `INSUFFICIENT_COVERAGE` (19/49); the
  `RELEASE_READY` depends on the `--coverage-scope application` default (57/73), which is a pre-existing
  Story-8.1 lever, not this story's.
- **AC12 was extended, not relaxed.** `-003-01` enumerates exactly two permitted movers via a
  `_sole_locator` helper that asserts `len(matches) == 1`, keeps the artifact-count assertion and still
  requires every other artifact byte-identical; `-003-04` applies `-003-02`'s revert-proof shape.
  `tests/fixtures/verdict_schema_v1_row2_artifacts.json` has an **empty worktree diff** and an mtime
  predating this session — **not regenerated**.
- **AC16 fence holds.** `argus/reports/generator.py`, `argus/verdict/verdict_gate.py`,
  `argus/verdict/prosecutor.py` and `tests/cartridges/_registry.py` all carry mtimes from Story 8.1's
  session (14:25-17:25), hours before this story's first write (21:31) — their non-empty diff-vs-HEAD is
  8.1's uncommitted delta, as claimed. `deferred-work.md`'s only diff is 8.1's DF-8-1-A.
- **AC10(b)'s Dev-Notes block was the right call.** AC10(b) and Task 6 explicitly require the residual
  exposure in Dev Notes; the dev added exactly one clearly-labelled, dev-attributed block and altered
  nothing existing. An unmet AC would have been the worse defect, and the tradeoff is recorded in the
  Completion Notes. Accepted, no finding.
- **Suite re-run by the reviewer** (`PYTHONIOENCODING=utf-8 python -m pytest tests/ -p no:randomly`):
  **3 failed, 1105 passed in 151.82s**; `--collect-only` → **1108 collected**; **0 skipped**, 0 xfail.
  The only reds are the three adjudicated carve-outs. `python -m mypy argus` → clean, 69 files.
  **No test deleted, skipped or weakened** — the single removed `def test_` in the whole delta is 8.1's
  rename `..._not_ready_low_deep` → `..._gate_unmet_low_deep`, which asserts strictly more
  (`+ decision_row`). `test_dogfood_proof`'s assertion is **unchanged and un-weakened**, its message
  correctly moved `INSUFFICIENT_COVERAGE` → `RELEASE_READY`, and `minions-dogfood-proof.md` was **not**
  re-derived.

#### Iteration 2 — re-review verdict (code review, 2026-08-05). **PASS.**

*Every disposition below was falsified by the reviewer against the working tree; nothing is accepted on
the Dev Agent Record's word. The `is_test_file` restructure was treated as the highest-risk item and is
proved equivalent differentially, not argued.*

- [x] **[Review][Patch] D3/AC3 FALSE GREEN — CLOSED, verified.** `[argus/pipeline.py:400-430]`
      The dev took the prescribed route, not the forbidden one. `argus/detectors/vacuous_test.py` now
      declares the tier structure **once** (`_lower_basename` + `_is_unambiguous_test_path`), exports
      `is_test_classification_content_dependent`, and `is_test_file` **reads** that structure;
      `_critical_ineligibility` withholds `TEST_FILE` only when `entry.parse_failed or not
      entry.ast_eligible` **and** the label came from tier 3. Reviewer re-ran the seam end-to-end
      through `_detect_per_file` on staged repos (`-002-01[ambiguous-test-suffix]`, `-002-09`): a
      parse-failed `app/auth_test.py` and a parse-failed `app/broken_auth.py` now land on the **same**
      eligible side (`ineligibility=None`, `depth=SKIPPED`, both retained in `critical.paths`, neither
      in `heuristic_excluded_ineligible`), while a parse-failed `tests/test_broken.py` is still
      `TEST_FILE` — so DR-5's deleted unsatisfiable gate stays deleted. No production module is
      disclosed under the false reason `test_file`.
      **Equivalence of the `is_test_file` restructure — PROVED, not accepted.** The reviewer rebuilt the
      HEAD (`9109e16`) function body verbatim from `git show` and differentially compared it against the
      new implementation over **220 paths × 12 entry variants = 2 567 comparisons → 0 mismatches**. The
      corpus was all **147** real indexed repo paths plus 73 synthetic adversarial paths (empty string,
      `/`, `\`, no-extension, dotfiles `.test.py`/`._test.py`, `conftest.py`, nested and cased `tests/`
      `Tests/` `TESTS/` `__tests__/` `spec/` `specs/`, `test_*`/`*_test.py`, every
      `_UNAMBIGUOUS_TEST_SUFFIXES` member and its near-miss, spaces, non-ASCII/emoji basenames); the
      entry variants were `None`, a non-`AstIndexEntry` object, clean-zero-def, clean-test-function,
      clean-`TestCase`-class, clean-production-defs, `parse_failed`, `ast_eligible=False`, both-bad,
      parse-failed-with-defs, the file's **own real** AST entry, and the no-keyword call. Separately,
      `is_test_classification_content_dependent` was checked to be **exactly** "tier 3 decided" over the
      same corpus (0 inconsistencies) **behaviourally**: where it is `True` the answer varies with the
      entry (`None`→True, production-defs→False); where it is `False` the answer is invariant across
      all 12 entry variants. The restructure is a pure extraction.
      **New-seam probe — no remaining escape hatch.** The four branches were enumerated and each
      checked: (i) `is_test` + readable → `TEST_FILE`, agrees with the depth actually graded; (ii)
      `is_test` + unreadable + tier 3 → eligible (the fix); (iii) `is_test` + unreadable + tier 1/2 →
      `TEST_FILE`, correct because test-hood there is a property of LOCATION/reserved name that holds
      however the parse went — such a file could never be `audited_deep` even when readable; (iv) not
      `is_test` + unreadable → eligible. No shallow-**by-circumstance** file exits the set.
      **Over-correction checked in the opposite direction:** a genuine but unreadable `*_test.py`
      outside a test directory is now RETAINED. That is over-inclusion — a *stricter* gate, AC7's
      sanctioned failure direction — and it is **transient**, not structural: repairing the syntax error
      makes the content decide and restores the `TEST_FILE` exclusion, so it does not re-create DR-5's
      unsatisfiable gate.

- [x] **[Review][Patch] The tautological AC3 pin — CLOSED, discrimination independently verified.**
      `[tests/test_critical_eligibility.py:93, tests/test_critical_eligibility_pipeline.py:176,290]`
      `-158` is renamed `test_an_eligible_critical_candidate_survives_and_is_not_disclosed` and its
      docstring now states plainly that it **does not** pin D3, *why* a fold test that hands the answer
      in as its own input cannot, and where D3 is really pinned. The reviewer verified the RED claims by
      **injecting the historical implementations at runtime** (a pytest plugin rebinding
      `argus.pipeline._critical_ineligibility`; no source file was edited):
      • against the **pre-fix** body → exactly `-002-01[ambiguous-test-suffix]` and `-002-09` FAIL while
      `-002-01[production-name]` stays GREEN — so the reds are the defect, not a blanket failure;
      • against the **forbidden naive hoist** (parse guard above `if is_test:`) → `-002-09` FAILS on its
      third row (`tests/test_broken.py` returns `None` instead of `TEST_FILE`) while everything else
      passes. `-002-09` therefore **discriminates the correct fix from the forbidden one** in both
      directions; it is a real regression test, not a rubber stamp. `DETECT-001-95` additionally pins
      the tier predicate in its owning module's suite.

- [x] **[Review][Patch] The two new test modules — CLOSED.**
      `git diff --cached --name-status` shows `A tests/test_critical_eligibility.py` and
      `A tests/test_critical_eligibility_pipeline.py`; `git check-ignore` exits `1` for both (not
      ignored); worktree clean against the index. Staged, uncommitted, will survive the commit.

- [x] **[Review][Defer] NFR-M1 — verified at 1199, and the placement is legitimate, not cap-gaming.**
      `argus/pipeline.py` measured at exactly **1199** lines; no `argus/` source exceeds 1200 (next
      largest `argus/dogfood/proof_run.py` 749). Pushing the substance into `vacuous_test.py`
      (488 → **533**) is the **right** placement on its own merits and was the reviewer's own iteration-1
      prescription: the tier table and the "which tier answered" question are properties of the
      classification and belong in the module that owns it (AR7 no-fork — re-declaring
      `_AMBIGUOUS_PYTHON_TEST_SUFFIXES` in the shell would have been the fork). `vacuous_test.py` gained
      cohesive material inside its own single responsibility and sits at 533/1200, so no SRP problem was
      relocated. **DF-8-2-A stands unchanged for 8.3** — not re-litigated here.

- [x] **[Review][Defer] Two `_UNAMBIGUOUS_TEST_SUFFIXES` entries lack a word separator, so tier 2 can
      claim a production file** `[argus/detectors/vacuous_test.py:195-199]` — deferred, logged as
      **DF-8-2-B**. **Severity: LOW; PRE-EXISTING, not this delta.** `"test.java"` and `"spec.rb"` are
      listed without a leading `_`/`.`, so `svc/latest.java` and `svc/myspec.rb` classify as tier-2
      test files (reviewer-confirmed) and would leave the heuristic critical set disclosed as
      `test_file`. Byte-identical at `9109e16` and unchanged by this story — the reviewer's differential
      proof shows old and new agree on these paths — and DR-5 merely gives the pre-existing
      misclassification a second consumer. Not a false green relative to what Argus can grade: the
      grading stage misclassifies them identically, so they are `audited_shallow` and could never be
      `audited_deep` anyway; AC7's "the two stages cannot disagree" still holds. Zero instances in this
      repo (no `.java`/`.rb` sources). Close = add the separator (`"_test.java"`/`"Test.java"`,
      `"_spec.rb"`) with a pin.

#### Iteration 2 — regression sweep (reviewer-verified, not asserted)

- **`argus/ledger/critical_subsystems.py` untouched this iteration.** mtime `2026-08-04 21:48:02`,
  hours before the fix session's first write (`2026-08-05 07:38:47`). `_matches_exclusion` extracted by
  AST from `9109e16` and from the worktree: **1424 characters both sides, identical SHA-256** — DR-7
  still verify-only, `fnmatchcase` present, bare `fnmatch(` absent. **D1 purity re-verified by AST**:
  imports are only `__future__`, `enum`, `fnmatch.fnmatchcase`, `typing`, `pydantic`,
  `argus.ledger.coverage_ledger`, `argus.ledger.depth_semantics`; **zero function-local imports**.
- **Figures re-derived independently** via the shipped functions by import (`resolve_source_state` →
  `build_ast_index` → `assess_criticality` / `is_test_file` / `_critical_ineligibility` →
  `identify_critical_subsystems`): **147** indexed, **116** heuristic CRITICAL,
  `Counter({'test_file': 56, 'ELIGIBLE': 50, 'zero_definition_module': 10})`, **0** parse-failed among
  the criticals, **50** eligible survivors, **0** unreachable blockers remaining. Both figures AC11
  asserts (**0** and **50**) are unmoved from iteration 1. The `115→116`/`55→56` drift reconciles
  exactly as the dev states (this iteration's additive edit to `tests/test_vacuous_detector.py` added
  `auth`/`token`/`permission` tokens, flipping that one file `NORMAL → CRITICAL`).
- **The High was genuinely LATENT — measured, not assumed.** The reviewer ran the pre-fix and post-fix
  `_critical_ineligibility` over all 147 real entries: **0 files change answer on this repo**. So no
  verdict, artifact or byte-delta evidence could have moved.
- **Over-breadth of the disclosures re-audited: 0 violations.** Every one of the 66 disclosed paths was
  checked — no `test_file` label sits outside a test directory without a `test_` prefix, and all 10
  `zero_definition_module` entries have literally 0 definitions and a clean parse.
- **The repo verdict is still the EARNED `RELEASE_READY` / exit `0`** — observed in the live
  re-derivation inside `test_dogfood_proof`'s (adjudicated-red) failure message, backed by 50
  genuinely deep-graded survivors, `origins` all heuristic. **AC12 fixture NOT regenerated**:
  `tests/fixtures/verdict_schema_v1_row2_artifacts.json` is staged `A` with a clean worktree diff and
  mtime `2026-08-04 14:20:54`, predating the fix session.
- **AC16 fence intact for this iteration.** Every fenced path carries a pre-fix-session mtime
  (`generator.py` 08-04 14:46, `verdict_gate.py` 08-04 14:25, `prosecutor.py` 08-04 17:25,
  `_registry.py` 08-04 14:53, `plain_english.py` 08-03, `cli.py` 08-03, `argus/__init__.py` and
  `depth_semantics.py` 07-28); `minions-dogfood-proof.md` and both `final-verdict.md` have an **empty**
  diff against HEAD. `argus/detectors/vacuous_test.py` / `tests/test_vacuous_detector.py` are not fenced.
- **Suite re-run by the reviewer** — `PYTHONIOENCODING=utf-8 python -m pytest tests/ -p no:randomly` →
  **3 failed, 1108 passed in 141.93s**; `--collect-only -p no:randomly` → **1111 tests collected**;
  **0 skipped, 0 xfail, 0 deselected**. The only reds are the three adjudicated carve-outs
  (`test_dogfood_plan.py` ×2 inherited, `test_dogfood_proof.py` deliberate/8.5-DR-10), left red and
  unmodified. `python -m mypy argus` → **Success: no issues found in 69 source files**. The delta is
  purely additive in `tests/test_vacuous_detector.py`; nothing was deleted, skipped, weakened or
  re-pointed to assert less — `-158` was **narrowed in scope and truthfully renamed**, and the claim it
  used to over-state is now pinned by two stronger behavioural tests.

---

## Dev Notes

### LOCKED decisions taken at story design — with rationale (record these; do not re-litigate)

**D1 — the eligibility fact is computed in the IMPURE SHELL and carried as DATA on `CriticalCandidate`;
`critical_subsystems.py` gains no import.**
*Rationale:* the module's own docstring LOCKS its import set to `depth_semantics` + the 1.2 ledger models,
it sits in `_MODULES_UNDER_GUARD`, and `detectors/` + `audit/` are **higher** layers — a `ledger/` module
importing a detector is a layering inversion the codebase has never made. The project already has a decided
precedent for exactly this shape, written down at `pipeline.py:630-632`: *"Classification lives HERE, in the
impure shell that already owns `is_test_file`, precisely so the PURE verdict gate never has to import a
detector (AR8 import isolation). The gate receives membership as data."* This story follows that ruling.
*Rejected alternative:* a third keyword argument `ineligible_paths=` on `identify_critical_subsystems`. It
would create a **three-channel** precedence puzzle at the call site alongside `operator_designated` /
`operator_excluded`, when eligibility is not an operator channel at all — it is a per-file **fact**, which is
precisely what `CriticalCandidate` exists to carry.

**D2 — the LOCKED precedence order (boundary B5) is: eligibility → designation → exclusion.**
```
heuristic_eligible = {c.file_path for c in candidates
                      if c.criticality is CRITICAL and c.ineligibility is None}
final = (heuristic_eligible ∪ operator_designated) − matches(operator_excluded)
```
*Rationale:* (i) DR-6 says designation is **exempt** from the filter, which is only expressible if the filter
is applied to the heuristic term *before* the union; (ii) the exclude-wins-on-a-tie rule is already LOCKED at
`critical_subsystems.py:50-53` and must stay last; (iii) this is the **minimum** change to a formula four
modules depend on. A path that is both ineligible and excluded is recorded as **eligibility-excluded** (the
first rule that removed it), so the disclosure map is a function of the inputs and not of evaluation order.

**D3 — the filter excludes EXACTLY the two by-construction classes FR4 enumerates. Parse-failed and
AST-ineligible files stay ELIGIBLE.**
*Rationale:* FR4's principle sentence is *"a file APAA can never grade `audited_deep` is ineligible"*, and a
literal reading would also drop parse-failed / no-grammar files, which are `skipped`. **That reading is
rejected.** A test file's shallowness is a property of **what the file is** and is stable across every run
and every host; a parse failure is a property of **this run** (a missing tree-sitter grammar, a syntax error,
a transient) and will resolve the moment the grammar is installed. Dropping an unparseable
security-token-bearing file out of the critical set would mean the tool quietly stops asking about the one
file it could not read — a false green of exactly the class the PRD names as the fatal error. FR4's own
enumeration is *"test files … and clean-parsed zero-definition modules"*: two classes, both by construction.
Measured consequence on this repo: **zero** critical files are parse-failed, so the decision costs nothing
here and buys the safe direction everywhere else. *(Best-practice "follow the stated principle literally"
loses to the project standard "never loosen toward a false `RELEASE_READY`" — the PRD's stated goal. Recorded
per the conflict rule.)*

**D4 — disclosure lives on `CriticalSubsystemSet`, as a path → closed-reason map, with a schema bump.**
```python
class CriticalIneligibility(str, enum.Enum):
    TEST_FILE = "test_file"
    ZERO_DEFINITION_MODULE = "zero_definition_module"

# on CriticalCandidate:
ineligibility: CriticalIneligibility | None = Field(default=None, ...)   # None ⇒ eligible
# on CriticalSubsystemSet:
heuristic_excluded_ineligible: dict[str, CriticalIneligibility] = Field(default_factory=dict, ...)
```
*Rationale:* (i) `CriticalSubsystemSet` is the **persisted artifact whose subject IS the critical set**, and
it already carries the analogous "the operator needs to know this" channel (`designated_but_unmatched`) — the
disclosure belongs where the data is, not bolted onto the verdict; (ii) a **closed enum + `None` default** is
exactly the shape Story 8.1 just landed for `decision_row` (D1/D2 there), so it is the established house
pattern for "disclose *why*"; (iii) a `dict[str, Enum]` mirrors the existing `origins` field byte-for-byte in
shape, so determinism, NFR-S1 and the no-float property are inherited rather than re-argued.
**Why the schema bump is not optional:** `CriticalSubsystemSet` has **no omit-when-empty machinery** —
`persist_critical_subsystems` writes `model_dump(mode="json")`, so the new key is serialized for **every**
repo and the artifact's content hash moves regardless. Given the bytes move anyway, and given the *meaning*
of `paths` changes (filtered vs unfiltered) with no other channel to tell a reader which contract produced
the artifact, NFR-M2's localized `schema_version` is the sanctioned and mandatory lever. Leaving it at `"1"`
would ship a persisted artifact whose stamp misdescribes it — the exact defect class this epic exists to
delete.
**Rejected alternative:** adding the disclosure to `ScopeStatement` (`negative_assurance.py:129-175`). That
model also serializes every field, so it would change the negative-assurance content hash for **every**
repository, for information already available one artifact over — a second wire change with no requirement
behind it. See **D5**.

**D5 — the scope boundary against Story 8.3, and what this story owes B3.** This story delivers the
**machine-readable** disclosure (D4) plus a **proof of the negative**: no surface asserts "all critical
subsystems examined deeply" when the gate is only vacuously satisfied (AC8). It does **not** add the
human-facing prose that names the vacuity, and it does **not** touch `plain_english.py` or `generator.py` —
the epic assigns both report surfaces to **Story 8.3 / DR-11**, whose AC block already covers "renders
correctly for an **empty** set" and the now-wrong *"each must reach `audited_deep`, or be excluded"*
guidance at `generator.py:122-123`. *Rationale:* 8.1's D4 rule is *"a project standard outranks a tidy story
boundary when the alternative is shipping an artifact that **asserts a falsehood**"*. Verified here: with an
emptied critical set, `_render_critical_blockers` returns `[]` (`generator.py:114-116`),
`plain_english.py:162,178` is guarded by `if not verdict.critical_subsystems_all_deep`, and
`_critical_narration` yields two empty tuples — so nothing **asserts** anything false. It is an *omission*,
which is 8.3's job to fill, not a falsehood, which would have been ours.

**D6 — no new CLI flag, no opt-out.** FR4/DR-5 ask for a filter, not a switch, and the operator already has
both levers: `--critical-subsystem` forces any file back in (exempt, DR-6) and `--exclude-critical` takes any
file out (patterns, DR-7). Adding `--no-eligibility-filter` would widen the AR3-adjacent wire contract for a
case both existing flags already cover.

**D7 — the epic's own arithmetic is corrected by measurement, and the correction is recorded here** so the
next reader does not "fix" the code to match a stale number: **52** test files (epic says 51; its own
"51 + 10" did not sum to its own "62"), **10** zero-definition modules, **62** unreachable blockers total
(epic correct), → **0** after the filter (epic says "~0").

### Accepted residual exposure (written by dev-story per Task 6 / AC10(b), 2026-08-04)

> *Recorded here because AC10 requires the loosening to be documented in Dev Notes. This is the only
> dev-authored block outside the Dev Agent Record; the section-fence tradeoff is noted in the Completion
> Notes.*

DR-5 makes `RELEASE_READY` **strictly easier** to reach, and the transition was measured rather than
assumed (`TC-ArgusAgent-PIPELINE-002-04` re-folds the identical candidates with the eligibility fact
stripped — which IS the pre-8.2 contract, since the field defaults to eligible):

- **What is now possible that was not.** A repository containing a **genuinely security-relevant module
  that is `audited_shallow` by construction** — the epic's own example, a clean-parsed zero-definition
  `__init__.py` re-exporting a security boundary — can now reach `RELEASE_READY` when every other gate is
  met. Before the filter that file sat in the critical set at `audited_shallow`, so
  `critical_subsystems_all_deep` was `False` and the verdict was withheld.
- **Why it is accepted.** The withholding was not a signal: it was **unconditional**. No run of any kind
  could have cleared it, because the file class is `audited_shallow` by construction, and on this very
  repository 62–65 of the ~112 flagged "critical subsystems" were in exactly that state. A gate no run can
  satisfy is not a gate, and an operator who learns to ignore one gate learns to ignore all of them.
- **What bounds it.** (i) The removal is **disclosed**, per path with a reason, in the persisted
  `CriticalSubsystemSet` — an emptied critical set is distinguishable on disk from a repo that had none
  (B3). (ii) **Operator designation is exempt** (DR-6): `--critical-subsystem <path>` puts the file back
  and restores the block, pinned by `TC-ArgusAgent-PIPELINE-002-05`. (iii) The filter removes **exactly
  two by-construction classes** — a parse-failed or AST-ineligible file, which is shallow by
  *circumstance*, deliberately stays in the set (D3). (iv) The counter-direction is pinned:
  `TC-ArgusAgent-PIPELINE-002-03` proves an under-assessed repository is still withheld, and the existing
  clean-control and blocking cartridges keep their exact verdicts.
- **What it does NOT cover.** The `--coverage-scope application` default (the *other* loosening in this
  delta) is not this story's change and is not counterweighted here beyond the cartridge suite.

### Architecture patterns & constraints (non-negotiable — AR/NFR ids a reviewer will check)

- **AR8 pure/impure master rule.** `critical_subsystems.py` is PURE: no I/O, no clock, no LLM, no
  `uuid4`/`random`, no set/dict iteration-order reliance. `TC-ArgusAgent-LEDGER-001-146` AST-scans the module
  source for exactly this and must stay green **unmodified**. All filesystem/AST work stays in
  `pipeline.py`, the impure shell.
- **AR7 / §3.3 no-fork.** `is_test_file` and `is_deep_claim_grounded` are **imported and reused**. Writing a
  second "is this a test file" or "does this file have definitions" predicate anywhere is the failure this
  rule exists to prevent — and would let the eligibility stage and the grading stage disagree inside one run,
  which is precisely the inconsistency this tool exists to surface in *other people's* repositories.
- **AR4 determinism.** One canonical serializer (`argus/store/canonical.py`) — never `json.dumps` directly.
  `paths` / `designated_but_unmatched` are sorted tuples; the new map's keys are sorted by the serializer.
  **No `float` anywhere** — the serializer raises `CanonicalSerializationError` on a float leaf; keep that
  as the proof (`TC-ArgusAgent-LEDGER-001-151`).
- **NFR-P1 byte-identical across hosts/runs.** `fnmatchcase`, never `fnmatch` — this is already correct and
  DR-7 pins it; do not "simplify" it.
- **NFR-M2 additive-only schema evolution.** New fields are optional-with-default only; the localized
  `schema_version` bump is the sanctioned lever (D4).
- **NFR-D2 zero-token testability.** Every AC except AC11 is provable over synthetic candidates / synthetic
  ledgers with no LLM and no network. Do not reach for a live audit run to prove a pure-fold property.
- **NFR-S1.** The new map carries only repo-relative POSIX paths and closed enum tokens — no absolute host
  path, no source byte, no secret byte.
- **AR10 typed failure.** Malformed input raises `CriticalSubsystemError` (a `ValueError` subclass), never a
  silent coerce / bare `except: pass` / `print()`.
- **NFR-M1** ≤1200 lines per file. `critical_subsystems.py` is 378 today; `pipeline.py` is the tree's largest
  at 1162 — **watch it**, Task 5's edit lands there.

### Traps a previous story already paid for (Epic 1–8.1 learnings that apply here)

- **Verify independently; do not trust a prior record.** Every Epic-6/7 review re-ran the suite itself, and
  8.1's review caught a mis-measurement precisely by re-running in a clean worktree. The tables in this story
  were measured on the real tree by the SM — **re-derive them, do not assume them.**
- **The scratch-tree trap, concretely.** 8.1's blast radius was measured on a copy with no `.git` and no
  `_bmad-output/`, which silently changed which tests could pass. If you measure anything, measure it where
  the suite actually runs.
- **"Extended, not forked" applies to guard lists and evidence fixtures.** `_MODULES_UNDER_GUARD` is
  appended to, never replaced (re-confirmed in Stories 2.1, 2.5, 2.6, 3.1). `tests/fixtures/
  verdict_schema_v1_row2_artifacts.json` is **evidence**, not a golden to regenerate (8.1 review finding R4).
- **A re-pointed test must keep its original subject assertion.** 8.1's review verified every re-point kept
  its subject and added something strictly *more* specific. `TC-ArgusAgent-LEDGER-001-148` is the only test
  this story should need to re-point, and only its version string.
- **Non-ASCII adversarial coverage (AI-E1-1) is a standing requirement** since Epic 1's only review FAIL.
  This story touches path-keyed structures, so it is **not** discharged by hand-waving: extend the existing
  non-ASCII critical-subsystem tests (`TC-ArgusAgent-LEDGER-001-153/154/155`) to cover an ineligible
  non-ASCII path (e.g. a Cyrillic test file) round-tripping through the new map intact.
- **Run tests as** `PYTHONIOENCODING=utf-8 python -m pytest tests/ -q` (the suite contains non-ASCII
  fixtures). `pytest-timeout` is **not** installed — do not pass `--timeout`.

### Runtime, library and toolchain specifics (verified on this machine, 2026-08-04)

`python 3.11.15` · `pydantic 2.13.4` · `pytest 9.1.1` · `mypy 2.3.0` · `tree-sitter` pinned
`>=0.25,<0.26` (the grammar version is folded into the Epic-5 determinism closure — do not bump it here).
**No new dependency is introduced by this story**; everything it needs is stdlib (`enum`, `fnmatch`) plus
pydantic, all already imported by the touched modules.

Pydantic-v2 specifics that bite on this exact change:

- `CriticalCandidate` / `CriticalSubsystemSet` are `ConfigDict(frozen=True, extra="forbid")`. Under
  `extra="forbid"` a **field without a default** turns every existing construction site and every persisted
  read-back into a `ValidationError` — the same constraint assumption **A8** put on 8.1's `decision_row`.
  Both new fields therefore carry defaults, and there are **11 direct `CriticalCandidate(...)` construction
  sites in `tests/`** that must keep working untouched (`test_critical_exclusion_patterns.py`,
  `test_critical_subsystems.py`, `test_evidence_bundle.py`, `test_negative_assurance.py`,
  `test_negative_assurance_roundtrip.py`).
- A **mutable** default must use `Field(default_factory=dict)`, never `Field(default={})` — the existing
  `origins` field is the in-repo precedent; copy its shape.
- A `str`-valued `enum.Enum` member serializes to its `.value` under `model_dump(mode="json")`, which is why
  every wire vocabulary in this codebase is `class X(str, enum.Enum)`. Keep that.
- `X | None = None` on a frozen model round-trips a payload that omits the key **only** because of the
  default — write the round-trip test, do not assume it (8.1 did exactly this for `decision_row`).

### Recent git context (last commits on `fix/honest-verdict-reporting`)

`9109e16` docs(readiness) · `d8ba5ad` docs(prd): FR16/FR4 verdict-contract amendment propagated to epics ·
`faeefd9` fix(verdict): stop reporting a block when nothing was found · `ae5f00c` fix(audit): make verdicts
honest and the tool runnable on any repo · `37ca977` feat(verdict): verdict gate for core readiness.
Story 8.1's implementation is **on top of `9109e16` and is not yet committed** — the pattern of the last five
commits is small, single-concern changes to the verdict path with the amendment's paper trail landing
first. Follow it: this story is two source files.

### Pre-existing observation — NOT this story's bug, do not fix here

On the **resume** path, `resume_audit_detailed` builds `candidates` from the **resume-target entries only**
(`pipeline.py:1068`), so a carried-forward file contributes no `CriticalCandidate` and can never be in the
heuristic critical set of a resumed run. That asymmetry exists **today**, is unchanged by this story (a
carried-forward file was never a candidate before either), and is orthogonal to DR-5. **Do not fix it here.**
If on inspection you believe it is a genuine defect, file it in `deferred-work.md` with the six mandatory
CC-3 fields (`id`, `origin_story`, `owner`, `target_story`, `category`, `severity` — see **DF-8-1-A** at
`deferred-work.md:498-518` for the exact shape) and move on.

### Project Structure Notes

- **Files this story is expected to modify:** `argus/ledger/critical_subsystems.py` (the substance —
  `CriticalIneligibility`, the candidate field, the filter, the disclosure field, the version bump),
  `argus/pipeline.py` (`_detect_per_file` — hoist `is_test_file`, compute the token), and the test files:
  `tests/test_critical_subsystems.py`, `tests/test_critical_exclusion_patterns.py` (DR-7 pins),
  `tests/test_verdict_schema_bump.py` (extend the byte-delta proof), plus **new** tests for AC10's
  counterweight and AC11's measurement.
- **Files this story must NOT modify (AC16):** `argus/reports/plain_english.py`,
  `tests/test_plain_english.py`, `argus/reports/generator.py`, `argus/verdict/verdict_gate.py`,
  `argus/verdict/prosecutor.py`, `argus/cli.py`, `argus/__init__.py`, `argus/ledger/depth_semantics.py`,
  `tests/cartridges/_registry.py`, `argus/dogfood/*`, `_bmad-output/reports/final-verdict.md`,
  `_bmad-output/audit-reports/final-verdict.md`, `minions-dogfood-proof.md`.
- **No new module.** Everything is an edit to two existing source files; the `ledger/` package layout is
  unchanged.
- **Test tree:** `tests/` at the repo root — *not* the `tests/apaa/` path named in the older architecture
  prose, which describes the pre-extraction Minions monorepo.
- **Test-id convention:** `TC-ArgusAgent-<AREA>-<SEQ>-<SUBSEQ>`. The critical-subsystem area is
  `TC-ArgusAgent-LEDGER-001-NN` (2.3, currently to `-155`) and `TC-ArgusAgent-LEDGER-002-NN` (CR-4 exclusion
  patterns). Continue those sequences; do not restart them.
- ⚠️ **The working tree carries Story 8.1's UNCOMMITTED delta** (7 modified files + 2 staged-new test
  files). `git stash`, `git checkout --`, or a hard reset would **destroy** it. Do not.

### Variance from the epic, recorded

The epic's AC set for 8.2 is reproduced in full above and **extended** at story design after measuring the
change against the real tree. The additions are **AC3** (parse-failed files stay eligible — the epic's FR4
quote is ambiguous and the ambiguity resolves toward a false green if read literally; see **D3**), **AC7**
(the seam and the no-fork/no-import constraint — the epic names the file but not how the fact reaches a PURE
module whose import set is LOCKED), **AC9** (the localized schema bump — forced by the model having no
omit-when-empty machinery; see **D4**), **AC12** (`tests/test_verdict_schema_bump.py` is a keystone honesty
test that **will** break and must be extended rather than relaxed — measured, not predicted), **AC14**
(`holdout_vacuous` is the single cartridge the filter touches — measured), and **AC15/AC16** (the standing
whole-system and fence obligations). They are in scope under the standing rule that a story must leave the
system working end-to-end and must never ship an artifact that contradicts the shipped contract. The boundary
against Story 8.3 is stated in **D5**; **DF-8-1-A is explicitly left to 8.3**, per both the ledger entry's
`target_story` and the epic's own 8.3 AC block.

### References

- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Story 8.2: Critical-subsystem gates an operator can actually satisfy`] (lines 1464–1503, including boundaries B3/B5 and inversion F1)
- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Derived Delta Requirements (DR)`] — DR-5, DR-6, DR-7 and the "Additional Requirements (Architecture + addendum)" constraint block (lines 1163–1189)
- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Story 8.3: The plain-English report stops describing an impossible state`] (lines 1505–1538) — the report-surface boundary this story stops at
- [Source: `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md#FR4`] (line 390) — FR4 as amended: *"A file APAA can never grade `audited_deep` is ineligible for the heuristically-derived critical set — a gate no run can satisfy is not a gate, and an unsatisfiable one trains operators to ignore every gate."*
- [Source: `_bmad-output/design-artifacts/ArgusAgent/E-PRD/addendum.md#A1 — FR16 / FR4 amendment mechanics (2026-08-03)`] — touched modules; the `--coverage-scope application` default flip (the *other* loosening AC10 counterweights)
- [Source: `_bmad-output/design-artifacts/ArgusAgent/architecture.md#Implementation Patterns & Consistency Rules`] — AR4 determinism, AR7 reuse, AR8 pure/impure master rule, AR10 typed failure
- [Source: `_bmad-output/design-artifacts/ArgusAgent/stories/8-1-findings-before-coverage-binding-decision-table.md`] — the just-landed FR16 four-row table, `DecisionRow`/`is_below_floor`, the `_CONSERVATISM_RANK` partial order, D4's conflict rule, and the measurement lesson (review findings R3/R4)
- [Source: `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md#Deferred from: code review of 8-1…`] (lines 496–518) — **DF-8-1-A**, `target_story: 8-3`; the six mandatory CC-3 fields
- [Source: `argus/ledger/critical_subsystems.py`] — the frozen contract being amended (LOCKED decisions `:38-71`, `_matches_exclusion` `:210-238`, `identify_critical_subsystems` `:241-316`, the gate predicates `:319-377`)
- [Source: `argus/ledger/depth_semantics.py:242-337`] — `Criticality` + `assess_criticality` + `CRITICALITY_SIGNAL_TOKENS` (unchanged by this story)
- [Source: `argus/detectors/vacuous_test.py:200-271,392,400`] — `is_test_file` (multi-language, content-disambiguated) and the `audited_shallow`-by-construction grading
- [Source: `argus/audit/grounding.py:69-90`] — `is_deep_claim_grounded` (clean parse + ≥1 `Definition`)
- [Source: `argus/pipeline.py:357-396,399-476,618-656,659-704,1068`] — `_grade_non_test_source`, `_detect_per_file` (the seam), `_assessment_scope_paths` (the decided precedent for D1), `_assemble_and_persist`, the resume-path candidate asymmetry
- [Source: `argus/pipeline_persist.py:212-235`] — `persist_critical_subsystems`
- [Source: `argus/verdict/negative_assurance.py:129-175,240-280`] — `ScopeStatement` (D4's rejected alternative) and `_critical_narration`
- [Source: `argus/reports/generator.py:103-136`] — `_render_critical_blockers`, incl. the *"each must reach `audited_deep`"* guidance that Story 8.3 owns
- [Source: `argus/cache/key.py:196-280`] — the recording-producing closure; the computed critical set is **not** in it (no cache-busting)
- [Source: `argus/precision/replay_harness.py:91,222`] — why `CARTRIDGE_REGISTRY` must not grow in this story
- [Source: `tests/test_verdict_schema_bump.py`] — the byte-delta keystone AC12 extends
- [Source: `tests/test_no_web_imports.py:21,87`] — `_MODULES_UNDER_GUARD` includes `argus.ledger.critical_subsystems`

---

## Dev Agent Record

### Context Reference

- This story file (self-contained). Story key: `8-2-critical-subsystem-gates-operator-can-actually-satisfy`.

### Agent Model Used

`claude-opus-5[1m]` (Opus 5, 1M context) — BMAD `dev-story`, mode `implement`, single pass.

### Debug Log References

**RED capture (AC1) — verbatim, taken BEFORE any source change.**

The new pure-fold module was written first and run against the unmodified implementation:

```
$ PYTHONIOENCODING=utf-8 python -m pytest tests/test_critical_eligibility.py -q
=================================== ERRORS ====================================
_____________ ERROR collecting tests/test_critical_eligibility.py _____________
ImportError while importing test module 'D:\ProjectX\XAgents\XAgents\ArgusAgent\tests\test_critical_eligibility.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\...\Lib\importlib\__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests\test_critical_eligibility.py:29: in <module>
    from argus.ledger.critical_subsystems import (
E   ImportError: cannot import name 'CriticalIneligibility' from 'argus.ledger.critical_subsystems' (D:\ProjectX\XAgents\XAgents\ArgusAgent\argus\ledger\critical_subsystems.py)
=========================== short test summary info ===========================
ERROR tests/test_critical_eligibility.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
```

A collection error proves the vocabulary is absent but says nothing about the BEHAVIOUR being wrong, so
the pre-fix behaviour was also probed directly through the shipped API (this is the substantive RED, and
it is what AC1/AC2/AC8 are actually about):

```
PRE-FIX paths: ('argus/auth/__init__.py', 'argus/auth/guard.py', 'tests/test_auth.py')
PRE-FIX has disclosure field: False
PRE-FIX schema_version: 1
```

i.e. before the fix the heuristic critical set contained the test file **and** the zero-definition
`__init__.py` (both permanently un-`audited_deep`), the disclosure map did not exist, and the stamp was
`"1"`. AC12's keystone was independently RED as predicted, on the real cartridge run:

```
FAILED tests/test_verdict_schema_bump.py::test_TC_ArgusAgent_VERDICT_003_01_only_the_verdict_envelope_changed
E   AssertionError: an artifact other than the verdict envelope changed bytes ...
E   Left contains 1 more item:
E   {'state/154d…json': '{… "payload":{"designated_but_unmatched":[],"heuristic_excluded_ineligible":{},
E     "origins":{},"paths":[],"schema_version":"2"} … "producer":"argus.pipeline.critical_subsystems" …}'}
```

**Re-derived blast radius (AC11 / Task 8) — measured IN PLACE on the real working tree**
(`d:/ProjectX/XAgents/XAgents/ArgusAgent`, HEAD `9109e16` + 8.1's uncommitted delta + this story's delta,
`.git` and `_bmad-output/` present) via the shipped functions by import — `resolve_source_state` →
`build_ast_index` → `assess_criticality` / `is_test_file` / `is_deep_claim_grounded`. Never a
re-implementation, never a scratch copy:

| Quantity | Story table (SM, pre-delta) | **Re-measured (post-delta)** | Reconciliation |
|---|---|---|---|
| files in the AST index | 145 | **147** | +2 = this story's two new test files |
| heuristic `CRITICAL` hits | 112 | **115** | +3, fully accounted below |
| … test files | 52 | **55** | +2 new test files, +1 `tests/test_verdict_schema_bump.py` flipping `NORMAL → CRITICAL` because this story's edits added criticality tokens to it (verified by re-assessing its pre-edit blob from the git index: `pre=NORMAL now=CRITICAL`) |
| … clean-parse zero-definition | 10 | **10** | unchanged (the same 10 `__init__.py`) |
| … parse-failed / AST-ineligible | 0 | **0** | unchanged — D3 costs nothing on this repo |
| … **deep-gradable survivors** | 50 | **50** | **exact match** |
| unreachable blockers | 62 | **65** | = 55 + 10; the +3 is this story's own new/edited test files |
| unreachable blockers **after** the filter | 0 | **0** | **exact match** |

Every deviation from the SM's table is caused by this story's own test files being counted, and the two
figures the AC actually asserts — **0** unreachable blockers and **50** deep-gradable survivors — match
exactly. The `paths` count persisted by the live self-audit is **50** and the disclosure map holds
**65** entries (`Counter({'test_file': 55, 'zero_definition_module': 10})`), which is the same
measurement arriving by a second, independent route (the pipeline's own artifact).

**Live self-audit (AC11) — RECORDED, deliberately NOT pinned.**

```
$ PYTHONIOENCODING=utf-8 python -m argus.cli audit .
Ship-readiness: READY — no blocking problems found, and enough of the code was examined deeply to say so.
  - Verdict-blocking findings: 0
  - Deeply examined: 57 of 73 assessed files (57/73) — scope 'application', 74 held out (test_files)
verdict=RELEASE_READY deep_ratio=19/49 blocking_findings=0 assessed_deep_ratio=57/73 scope=application held_out=74
EXIT=0
```

Full record via `run_audit_detailed` (`budget=0` = no ceiling, `coverage_scope="application"`, the CLI
defaults):

| Field | Value |
|---|---|
| verdict | `RELEASE_READY` |
| exit code | `0` |
| decision row | `row_3_gates_met` |
| deep ratio (repo-wide) | `19/49` |
| assessed deep ratio (application scope) | `57/73` (74 test files held out) |
| blocking findings | `0` |
| `critical_subsystems_all_deep` | `True` |
| `critical_subsystems_not_deep` | `()` |
| `is_below_floor` | `False` |
| persisted critical `paths` | `50` |
| persisted `heuristic_excluded_ineligible` | `65` (55 `test_file`, 10 `zero_definition_module`) |
| persisted `schema_version` | `"2"` |

This is exactly the consequence the story predicted and told the dev to record rather than pin (boundary
B1). **Nothing was adjusted to obtain it**, no proof artifact was touched, and no test asserts it.
⚠️ Note for Story 8.5: with the *default* CLI budget (`0`, no ceiling) the repo lands `RELEASE_READY` /
exit 0; with `--budget 100` a mid-run exhaustion halt still yields `INSUFFICIENT_COVERAGE` / exit 3
(`deep_ratio=5/49`). Both are pre-existing budget behaviour, unrelated to DR-5, but the DR-10
re-derivation must state which invocation it re-derives from.

**Suite + toolchain (AC15).**

```
$ PYTHONIOENCODING=utf-8 python -m pytest tests/
=========================== short test summary info ===========================
FAILED tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation
FAILED tests/test_dogfood_plan.py::test_budget_reuses_the_31_accountant_no_fork
FAILED tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run
3 failed, 1105 passed in 372.45s (0:06:12)

$ PYTHONIOENCODING=utf-8 python -m pytest tests/ --collect-only    # summed per-file counts
TOTAL COLLECTED: 1108

$ python -m mypy argus
Success: no issues found in 69 source files
```

**1108 collected / 1105 passed / 3 failed / 0 skipped.** Baseline for comparison, re-measured in place
before any edit: **1075 collected / 1072 passed / 3 failed / 0 skipped**, mypy clean. Collected count
moved **1075 → 1108** (+33, all new: 22 in `test_critical_eligibility.py`, 8 in
`test_critical_eligibility_pipeline.py`, 2 in `test_critical_exclusion_patterns.py`, 1 in
`test_verdict_schema_bump.py`); the collected count did not fall below 1075; **zero new reds**; no test
deleted, skipped, weakened or re-pointed to assert less.

> ⚠️ Note on `-q`: `pyproject.toml` sets `addopts = "-ra -q"`, so passing `-q` a second time (the command
> the story's baseline section prescribes) **suppresses the final count line entirely**. The counts above
> come from `python -m pytest tests/` (one `-q`, from addopts). A reviewer re-running with `-q` and seeing
> no total is hitting that, not a truncation.

**The three carve-out reds, verbatim and untouched.** All three were red at this story's baseline and are
left exactly as found. The `test_dogfood_proof` assertion message changed as the story predicted it would
— its live re-derivation now reports `RELEASE_READY` / exit `0` where the baseline reported
`INSUFFICIENT_COVERAGE` / exit `3`:

```
baseline:  E  AssertionError: assert '`INSUFFICIENT_COVERAGE` (exit `3`)' in '# Minions Dogfood — Proof Artifact …'
after 8.2: E  AssertionError: assert '`RELEASE_READY` (exit `0`)' in '# Minions Dogfood — Proof Artifact …'
```

That is the expected, documented consequence of the critical clause clearing. `minions-dogfood-proof.md`
was **not** re-derived, the rot check was **not** weakened, and Story 8.5 / DR-10 still owns it.

**File-size gate (NFR-M1 / AC15).** `argus/pipeline.py` **1199** lines (was 1162; the ceiling is 1200 and
was actually hit at 1211 on the first draft — the `_critical_ineligibility` docstring was condensed rather
than the reasoning dropped, and no second module was created since the story forbids one).
`argus/ledger/critical_subsystems.py` **483** lines (was 378).

**AC16 fence — verified by `git diff` per path.** Empty for `argus/reports/plain_english.py`,
`tests/test_plain_english.py`, `argus/cli.py`, `argus/__init__.py`, `argus/ledger/depth_semantics.py`,
`argus/dogfood/*`, `_bmad-output/reports/final-verdict.md`,
`_bmad-output/audit-reports/final-verdict.md`, `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md`.
`argus/reports/generator.py`, `argus/verdict/verdict_gate.py`, `argus/verdict/prosecutor.py` and
`tests/cartridges/_registry.py` carry a non-empty diff **against `HEAD`** — that is Story 8.1's
uncommitted delta, which was present before this session began (see the baseline `git status` in the
frontmatter note) and is byte-for-byte unchanged by this story: the only files this session wrote are the
seven in the File List. `tests/fixtures/verdict_schema_v1_row2_artifacts.json` has an EMPTY worktree diff
— it was **not** regenerated. `_matches_exclusion` ends this story **byte-identical**: no diff hunk in
`critical_subsystems.py` touches lines 210–238 (DR-7 is verify-only, as required).

---

### Review iteration 2 — findings resolved (dev-story, mode `fix`, 2026-08-05)

**Finding 1 [High] — D3/AC3 false green. CLOSED.** Implemented as the reviewer directed: the naive
"hoist the parse guard above `if is_test:`" fix was **rejected**, because it would also make
grammar-less / parse-failed **genuine** test files eligible again and rebuild the unsatisfiable gate
DR-5 exists to delete. The test label is distrusted **only for the AMBIGUOUS tier**, via a predicate
exported from the module that OWNS the classification (AR7/§3.3 — the suffix table is **not**
re-declared in the shell):

- `argus/detectors/vacuous_test.py` — the three tiers `is_test_file` already evaluated inline are
  extracted into `_is_unambiguous_test_path` (tiers 1-2) + `_lower_basename`, and the new public
  `is_test_classification_content_dependent(file_path) -> bool` answers *"did tier 3 decide this?"*.
  **`is_test_file` now READS that structure instead of restating it**, so there is exactly one tier
  declaration in the codebase and the two predicates cannot drift. `is_test_file`'s behaviour is
  unchanged in every tier (pinned by the extended `TC-ArgusAgent-DETECT-001-85`/new `-95`).
- `argus/pipeline.py::_critical_ineligibility` — the `TEST_FILE` answer is withheld when the entry is
  unreadable **and** the label came from tier 3:
  ```python
  unreadable = entry.parse_failed or not entry.ast_eligible
  if is_test:
      if unreadable and is_test_classification_content_dependent(entry.file_path):
          return None
      return CriticalIneligibility.TEST_FILE
  ```

*Why an exported predicate rather than a `pipeline.py`-local check:* the asymmetry being corrected is a
property of the **classification**, not of the pipeline — `_exhibits_test_definitions` returns `True`
for anything it cannot read because that is conservative for its ORIGINAL grading consumer and
loosening for this NEW eligibility consumer. That fact belongs next to the tiers it describes, and
putting it there also kept the change inside `pipeline.py`'s 1-line NFR-M1 headroom (see below).

**Proved on BOTH of the reviewer's cases, end-to-end through `_detect_per_file` on a staged repo** —
and on the counter-case the rejected fix would have broken:

```
app/auth.py            critical parse_failed=False depth=audited_deep    ineligibility=None (ELIGIBLE)
app/auth_test.py       critical parse_failed=True  depth=skipped         ineligibility=None (ELIGIBLE)
app/broken_auth.py     critical parse_failed=True  depth=skipped         ineligibility=None (ELIGIBLE)
tests/test_broken.py   critical parse_failed=True  depth=skipped         ineligibility=test_file
critical paths: ('app/auth.py', 'app/auth_test.py', 'app/broken_auth.py')
disclosed: {'tests/test_broken.py': 'test_file'}
```

The label no longer flips on parse state: `app/auth_test.py` and `app/broken_auth.py` — identical
content, identical parse failure, different names — now land on the **same** (eligible) side, and no
production module is disclosed under the false reason `test_file`. The tier-1 genuine test file is
still `TEST_FILE`, so the gate DR-5 fixed stays fixed. `TC-ArgusAgent-PIPELINE-002-02`'s
clean-parse twin is unchanged and still eligible.

**Finding 2 [Med] — the tautological AC3 pin. CLOSED, and the missing test now exists.**
`TC-ArgusAgent-LEDGER-001-158` is rescoped (renamed
`test_an_eligible_critical_candidate_survives_and_is_not_disclosed`) to the FOLD contract it actually
pins — `ineligibility is None ⇒ survives, origin HEURISTIC, not disclosed` — and its docstring now
states plainly that it does **not** pin D3, why a fold test that hands the answer in as its own input
cannot, and where D3 is really pinned. The D3 claim moved to the seam:
`TC-ArgusAgent-PIPELINE-002-01` is **parametrized over both filename shapes**
(`app/broken_auth.py`, `app/auth_test.py`), asserting `ineligibility is None` and `depth is SKIPPED`
for each. The new `TC-ArgusAgent-PIPELINE-002-09` is the test that **would have caught the High**:
it stages `-002-02`'s clean-parse twin, an unreadable ambiguous-suffix twin and an unreadable
tier-1 test file in one repo and pins all three answers together.
New `TC-ArgusAgent-DETECT-001-95` pins the tier predicate itself in its owning module's suite.

**RED capture — the new tests were run against the pre-fix code, verbatim.** The guard was reverted
in place and both re-run (the unparametrized `production-name` row stayed GREEN, so this is the
defect and not a blanket failure):

```
E   AssertionError: an unreadable file is shallow by CIRCUMSTANCE; the filename must not decide it
E   assert <CriticalIneligibility.TEST_FILE: 'test_file'> is None
E    +  where <CriticalIneligibility.TEST_FILE: 'test_file'> = CriticalCandidate(
E         file_path='app/auth_test.py', criticality=<Criticality.CRITICAL: 'critical'>,
E         ineligibility=<CriticalIneligibility.TEST_FILE: 'test_file'>).ineligibility
FAILED tests/test_critical_eligibility_pipeline.py::…_002_09_an_unreadable_ambiguous_name_keeps_its_place
FAILED tests/test_critical_eligibility_pipeline.py::…_002_01_…[ambiguous-test-suffix]
2 failed, 1 passed
```

**And `-002-09` also rejects the fix the reviewer explicitly forbade.** With the naive
"hoist the parse guard above `if is_test:`" applied instead, the same test fails on its third row —
proof that it discriminates between the correct fix and the one that would rebuild the unsatisfiable
gate, rather than merely tracking the implementation:

```
E   AssertionError: a test file identified by LOCATION is audited_shallow BY CONSTRUCTION whatever
E   the parse did; keeping it would rebuild the unsatisfiable gate DR-5 deletes
E   assert None is <CriticalIneligibility.TEST_FILE: 'test_file'>
```

**Finding 3 [Med] — untracked test modules. CLOSED.**
`git add tests/test_critical_eligibility.py tests/test_critical_eligibility_pipeline.py`; both now
report `A` in `git status`. Not committed — the workflow does not commit.

**Finding 4 [Low] — NFR-M1 headroom. Respected, not consumed.** `argus/pipeline.py` ends this
iteration at **1199 lines — byte-for-byte the same count the reviewer measured**, not 1200 and not
over. The two added guard lines were paid for by tightening `_critical_ineligibility`'s docstring
(reasoning preserved and extended, prose repacked to the wider width the module already uses); the
substance of the fix lives in `vacuous_test.py`, which went 488 → 533 lines. DF-8-2-A stands
unchanged for Story 8.3; nothing here was silently blown.

**Regression re-measurement (nothing the reviewer verified clean was disturbed).**
`argus/ledger/critical_subsystems.py` was **not touched at all** this iteration — D1 purity and the
byte-identical `_matches_exclusion` are untouched by construction. Re-derived on the real tree via
the shipped functions by import: **147** indexed / **116** heuristic CRITICAL /
`Counter({'test_file': 56, 'ELIGIBLE': 50, 'zero_definition_module': 10})` / **0** parse-failed among
the criticals. The two figures the AC asserts are unmoved — **50** eligible survivors and **0**
unreachable blockers after the filter. The `115 → 116` / `55 → 56` drift is the same benign
accounting the reviewer already reconciled: this iteration's edit to `tests/test_vacuous_detector.py`
added criticality tokens (`auth`, `token`, `permission`) to it, flipping that one test file
`NORMAL → CRITICAL`. With 0 parse-failed criticals on this repo the High was **latent**, so the
self-audit verdict, the earned `RELEASE_READY`, and the AC12 byte-delta evidence are unchanged.

**Suite + toolchain, re-run in place after the fix:**

```
$ PYTHONIOENCODING=utf-8 python -m pytest tests/ -p no:randomly
FAILED tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation
FAILED tests/test_dogfood_plan.py::test_budget_reuses_the_31_accountant_no_fork
FAILED tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run
3 failed, 1108 passed in 129.44s (0:02:09)

$ PYTHONIOENCODING=utf-8 python -m pytest tests/ --collect-only -p no:randomly   →  1111 tests collected
$ python -m mypy argus                                                          →  Success: no issues found in 69 source files
```

**1111 collected / 1108 passed / 3 failed / 0 skipped**, up from iteration 1's 1108/1105/3/0 (+3:
the `-002-01` parametrization, `-002-09`, `DETECT-001-95`). The **only** reds are the three
user-adjudicated carve-outs, left red and byte-untouched — `test_dogfood_proof`'s assertion is
unchanged and `minions-dogfood-proof.md` was not re-derived. No test was deleted, skipped, weakened
or re-pointed to assert less; `-158` was rescoped to assert the same thing about a narrower,
truthfully-named subject and the claim it used to over-state is now pinned by two stronger tests.
AC16 fence intact: `argus/detectors/vacuous_test.py` and `tests/test_vacuous_detector.py` are **not**
on the forbidden list, and no fenced file was written this iteration — verified by mtime: every
fenced path (and `argus/ledger/critical_subsystems.py`) still carries its 2026-08-03/04 timestamp,
while the only files written today are the five in the File List.

> **Incidental, recorded so it is not mistaken for this delta:** three tracked `__pycache__/*.pyc`
> build artifacts (`argus/cost/exhaustion`, `argus/ledger/critical_subsystems`,
> `tests/cartridges/_registry`) report `M` against HEAD. They are `cpython-**312**` bytecode and the
> interpreter used throughout this session is **3.11.15**, which cannot write them — the difference
> is pre-existing (they surfaced when `git add` refreshed the index stat cache) and no source
> behaviour depends on them. Left untouched rather than `git checkout`-ed, per the standing rule
> against reverting anything in this working tree.

### Completion Notes List

- **DR-5 landed as a partition, not a subtraction.** `identify_critical_subsystems` now splits the
  CRITICAL candidates into an eligible heuristic set and a disclosed ineligible map in one pass; the merge
  formula, `_matches_exclusion`, the exclude-wins tie and the conservative unmatched policy are otherwise
  verbatim. The LOCKED precedence (D2) — eligibility → designation → exclusion — is pinned by an
  8-row truth table (`TC-ArgusAgent-LEDGER-001-162`) rather than left to evaluation order.
- **D1 honoured exactly: the PURE module gained NO import.** `critical_subsystems.py` still imports only
  `depth_semantics` + the 1.2 ledger models; the eligibility fact travels as data on `CriticalCandidate`.
  `TC-ArgusAgent-LEDGER-001-146` (the AST purity scan) and `tests/test_no_web_imports.py` are green
  **unmodified**.
- **AR7 no-fork honoured.** `_critical_ineligibility` in `pipeline.py` calls `is_deep_claim_grounded`
  by import and receives `is_test` from the caller's single `is_test_file` evaluation. No second
  predicate exists anywhere. `TC-ArgusAgent-PIPELINE-002-01` asserts the derived token against the depth
  the pipeline **actually graded** for all four rows of the grading table in one run, so the two stages
  are compared against each other rather than against a restatement of the rule.
- **D3 held under pressure and is now behaviourally pinned twice** — at the fold
  (`TC-ArgusAgent-LEDGER-001-158`) and at the seam (a real syntax-error file graded `skipped` and left
  ELIGIBLE). Measured cost on this repo: zero (0 parse-failed criticals).
- **AC10 / inversion F1 — the loosening is measured against the REAL pre-filter fold, not narrated.**
  `TC-ArgusAgent-PIPELINE-002-04` re-folds the same candidates with the eligibility fact stripped (which
  IS the pre-8.2 contract, since the field defaults to eligible), shows `app/__init__.py` sitting in the
  critical set at `audited_shallow` (so `RELEASE_READY` was unreachable), and then shows the identical
  repository reaching `RELEASE_READY` / exit 0 / row 3 with the filter. Leg (a) uses the same fixture with
  the coverage gate genuinely unmet (1/4 deep, above the 1/5 floor so it is a GATE decision, row 4) and
  still withholds release. `-002-05` pins the operator remedy.
- **AC12 was EXTENDED, never relaxed.** `-003-01` now names the critical-subsystem envelope as the second
  permitted mover (looked up by `producer`, since content addressing moves its locator) and still requires
  every other artifact byte-identical with an unchanged artifact count; the new `-003-04` applies
  `-003-02`'s revert-proof shape to it — delete `heuristic_excluded_ineligible`, set `schema_version` back
  to `"1"`, and the canonical bytes equal the pre-amendment payload exactly. No assertion was deleted or
  widened to "ignore", and the evidence fixture was not regenerated.
- **AC14 — `holdout_vacuous` behaves exactly as measured.** Its critical set is emptied
  (`{"tests/test_inventory.py": "test_file"}` disclosed), `critical_subsystems_all_deep` flips to `True`,
  and the verdict does **not** move: `NOT_READY_FOR_RELEASE` / exit 2 / `row_2_blocking_findings`, golden
  `vacuous_test_ast` finding intact. `tests/cartridges/_registry.py` untouched; no cartridge added.
- **AC8 / B3 — the disclosure is on disk and no surface over-claims.** A staged repo whose every heuristic
  critical hit is ineligible reaches `RELEASE_READY` with an EMPTY critical set; the persisted payload
  distinguishes that from "there were no criticals". The persisted `assurance_statement`, the three
  `scope_statement` critical tuples, the rendered `final-verdict` report and the ship-readiness summary
  were all inspected for six positive-claim phrasings and make none. Confirms D5: with an emptied set the
  report surfaces **omit**, they do not assert a falsehood — so the prose fix genuinely belongs to 8.3.
- **AI-E1-1 discharged, not waved.** A Cyrillic test-file path round-trips through the new map and the
  single 1.1 serializer byte-intact (`TC-ArgusAgent-LEDGER-001-169`), and `-152` was extended so the map's
  own key order is order-independent.
- **DF-8-1-A left alone** (`argus/reports/generator.py:339`, owned by Story 8.3 / DR-11), as were
  `plain_english.py` and the resume-path candidate asymmetry at `pipeline.py:1068`. Re-inspected the
  resume asymmetry as instructed: it is unchanged by this delta (a carried-forward file was never a
  candidate before either) and is genuinely orthogonal to DR-5, so no new deferred-work entry was filed.
- **No disagreement with any LOCKED decision.** D1–D7 were implemented as written; nothing was
  re-litigated. No new dependency was introduced (stdlib `enum` + `fnmatch` and pydantic only, both
  already imported).
- **Section-fence tradeoff, recorded.** The `dev-story` workflow permits edits only to the frontmatter
  `baseline_commit`, Tasks/Subtasks checkboxes, Dev Agent Record, File List, Change Log and Status — but
  **AC10(b) and Task 6 explicitly require the accepted residual exposure to be written into Dev Notes**.
  The AC won (an unmet AC is a worse defect than a widened edit surface). Exactly one clearly-labelled,
  dev-attributed block was added under Dev Notes ("Accepted residual exposure"); **nothing existing in Dev
  Notes was altered, reordered or deleted**, and no other non-permitted section was touched.
- **One tradeoff worth recording (project standard over best practice).** Best practice would put a
  cohesive derived-fact helper next to the predicates it composes; the project standard forbids a new
  module for this story and caps files at 1200 lines. `_critical_ineligibility` therefore lives in
  `pipeline.py`, which finished at 1199 lines — 1 line of headroom. **The next edit to `pipeline.py` will
  breach NFR-M1**, so the *next* story touching it should expect to extract a shell-helper module rather
  than add to it. Recorded here rather than acted on, because extracting one now would be an unrequested
  refactor of a 1162-line file inside a two-file story.

### File List

| File | Change |
|---|---|
| `argus/ledger/critical_subsystems.py` | modified — `CriticalIneligibility`; `CriticalCandidate.ineligibility`; `CriticalSubsystemSet.heuristic_excluded_ineligible`; the eligibility partition inside `identify_critical_subsystems`; `CRITICAL_SUBSYSTEMS_SCHEMA_VERSION` `"1"→"2"`; LOCKED-decisions docstring block extended. `_matches_exclusion` byte-identical. |
| `argus/pipeline.py` | modified — new `_critical_ineligibility` helper; `_detect_per_file` hoists `is_test_file` to a single local and supplies the fact to `CriticalCandidate`; the grading branch reuses that same local. **Iteration 2 (review fix 1):** the `TEST_FILE` answer is withheld for an UNREADABLE entry whose label came from the ambiguous tier; docstring repacked so the file ends at **1199** lines, unchanged from iteration 1. |
| `argus/detectors/vacuous_test.py` | **modified — iteration 2 (review fix 1).** Tiers 1-2 extracted to `_is_unambiguous_test_path` (+ `_lower_basename`) and `is_test_file` re-expressed in terms of them — one tier declaration, no fork; new public `is_test_classification_content_dependent`, exported in `__all__`. `is_test_file`'s answers are unchanged in every tier. |
| `tests/test_vacuous_detector.py` | **modified — iteration 2.** `TC-ArgusAgent-DETECT-001-95` added: which tier answered, and that the tier-3 unreadable guess itself is unchanged. |
| `tests/test_critical_eligibility.py` | **new (`git add`-ed in iteration 2 — review fix 3)** — 22 tests: the DR-5/DR-6 pure fold, the AC6 truth table, the AC8 disclosure map, the contract shape and the non-ASCII pin. **Iteration 2 (review fix 2):** `TC-ArgusAgent-LEDGER-001-158` rescoped to the fold contract it actually pins, with the D3 claim moved to the seam. |
| `tests/test_critical_eligibility_pipeline.py` | **new (`git add`-ed in iteration 2 — review fix 3)** — the AC7 seam over real AST entries, the AC10/F1 counterweight (both legs + the operator remedy), the AC8 no-over-claim proof and the AC14 `holdout_vacuous` row-2 precedence. **Iteration 2 (review fix 1/2):** `-002-01` parametrized over both parse-failed filename shapes; new `-002-09` (the unreadable ambiguous-suffix twin beside `-002-02`'s clean twin and an unreadable tier-1 test file). 8 → 10 tests. |
| `tests/test_critical_subsystems.py` | modified — `-148` re-pointed to `"2"` (subject unchanged); `-152` extended to cover the new map and its key order. |
| `tests/test_critical_exclusion_patterns.py` | modified — the nine DR-7 tests verified green and left as-is; two added (`LEDGER-002-10` `fnmatchcase`-not-`fnmatch`, `LEDGER-002-11` DR-7 intact under the eligibility filter). |
| `tests/test_verdict_schema_bump.py` | modified — `-003-01` refined to name the second bumped envelope; `-003-04` added with the revert-proof. Fixture NOT regenerated. |
| `_bmad-output/design-artifacts/ArgusAgent/stories/8-2-critical-subsystem-gates-operator-can-actually-satisfy.md` | this story file — tasks, Dev Agent Record, File List, Change Log, Status. |
| `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` | `8-2-…` → `review`; `last_updated` refreshed. |

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-08-05 | 0.3 | **Addressed code review findings — 3 of 3 open items resolved (dev-story, mode `fix`, iteration 2).** **[High] D3/AC3 false green CLOSED** without the fix the reviewer forbade: `argus/detectors/vacuous_test.py` now declares its three tiers ONCE (`_is_unambiguous_test_path` + `_lower_basename`, with `is_test_file` re-expressed in terms of them — no fork, AR7/§3.3) and exports `is_test_classification_content_dependent`; `argus/pipeline.py::_critical_ineligibility` withholds `TEST_FILE` only when the entry is UNREADABLE **and** the label came from the ambiguous tier, so a parse-failed `app/auth_test.py` and a parse-failed `app/broken_auth.py` now land on the SAME (eligible) side and neither is disclosed under a false reason, while a parse-failed `tests/test_broken.py` stays `TEST_FILE` and the DR-5 gate stays satisfiable. **[Med] tautological `-158` CLOSED:** rescoped to the fold contract it actually pins, D3 moved to the seam — `-002-01` parametrized over both filename shapes and new `-002-09` added; both verified RED against the pre-fix code AND `-002-09` verified RED against the forbidden naive hoist, so it discriminates the correct fix rather than tracking the implementation. New `TC-ArgusAgent-DETECT-001-95` pins the tier predicate. **[Med] untracked tests CLOSED:** both new modules `git add`-ed (now `A`; not committed). **[Low] NFR-M1 respected:** `pipeline.py` ends at **1199** lines, exactly as the reviewer measured — the guard was paid for by repacking its docstring, and the substance lives in `vacuous_test.py` (488 → 533). `critical_subsystems.py` NOT touched, so D1 purity and the byte-identical `_matches_exclusion` are untouched by construction. Re-measured on the real tree: 147 indexed / 116 heuristic CRITICAL / 56 `test_file` + 10 `zero_definition_module` / **50** eligible survivors / **0** unreachable blockers and **0** parse-failed criticals (the `115→116` drift is this iteration's own edit to `tests/test_vacuous_detector.py` flipping it `NORMAL→CRITICAL`; both AC-asserted figures unmoved, and the High was latent so no verdict, artifact or byte-delta evidence moved). Suite **1111 collected / 1108 passed / 3 failed / 0 skipped** (+3 tests) — only the three adjudicated carve-out reds, left red and untouched; `mypy argus` clean (69 files). Status: review. | Dev (dev-story, fix) |
| 2026-08-04 | 0.2 | **DR-5 / DR-6 / DR-7 implemented (dev-story, mode=implement).** `argus/ledger/critical_subsystems.py`: added the closed `CriticalIneligibility` vocabulary (`test_file`, `zero_definition_module`), `CriticalCandidate.ineligibility` (default `None` = eligible), `CriticalSubsystemSet.heuristic_excluded_ineligible` (default-factory dict), the eligibility partition applied to the HEURISTIC term only, and `CRITICAL_SUBSYSTEMS_SCHEMA_VERSION` `"1"→"2"`; the merge formula, `_matches_exclusion` (byte-identical), the exclude-wins tie and the conservative unmatched policy are otherwise verbatim, and the module gained **no import** (D1 — it is PURE and in `_MODULES_UNDER_GUARD`). `argus/pipeline.py`: new `_critical_ineligibility` shell helper reusing `is_deep_claim_grounded` by import, with `is_test_file` hoisted to a single per-file local that drives BOTH eligibility and grading (AC7); the parse-failed clean-parse guard keeps skipped-by-circumstance files ELIGIBLE (D3). Tests: 2 new modules (30 tests) + 2 DR-7 pins + `-148` re-pointed to `"2"` + `-152` extended over the new map + `-003-01` refined and `-003-04` added (revert-proof; **fixture NOT regenerated**). Measured in place on the real tree: 147 indexed / 115 heuristic CRITICAL / 55 test + 10 zero-def = 65 unreachable → **0**, **50** deep-gradable survivors (the SM's 50 confirmed exactly; the +2/+3 deltas are this story's own new/edited test files, reconciled in the Dev Agent Record). `argus audit .` RECORDED (not pinned): `RELEASE_READY` / exit 0 / `row_3_gates_met` / assessed 57/73 / 0 blocking / 50 critical paths / 65 disclosed. Suite **1108 collected / 1105 passed / 3 failed / 0 skipped** — exactly the three adjudicated carve-out reds, left red and untouched (the `test_dogfood_proof` message moved `INSUFFICIENT_COVERAGE`→`RELEASE_READY` as predicted; Story 8.5 / DR-10 still owns it). `mypy argus` clean (69 files). NFR-M1: `pipeline.py` 1199 lines (1 line of headroom — flagged for the next story). AC16 fence verified per path; DF-8-1-A left to 8.3. Status: review. | Dev (dev-story) |
| 2026-08-04 | 0.1 | Story drafted from the Epic-8 delta (DR-5/DR-6/DR-7 + boundaries B3/B5 + inversion F1). **Blast radius measured in place on the real working tree** (HEAD `9109e16` + 8.1's uncommitted delta, `.git` and `_bmad-output/` present) using the shipped `argus` functions by import — explicitly NOT on a scratch copy, the method that caused 8.1's mis-measurement: 145 indexed files, 112 heuristic critical hits, 52 test files + 10 zero-definition `__init__.py` = 62 permanently-unreachable blockers → **0** after the filter, 50 deep-gradable survivors, application deep ratio 57/73. All 10 cartridges run live through `run_audit_detailed`: exactly **one** (`holdout_vacuous`) has its critical set emptied, and its verdict must not move (FR16 row-2 precedence). Baseline suite re-measured: 1075 collected, 3 failed — the adjudicated carve-out only. ACs 3, 7, 9, 12, 14, 15, 16 added at story design over the epic's set, each with its measured or architectural justification; seven LOCKED decisions (D1–D7) recorded with rationale and rejected alternatives, including the corrected epic arithmetic (51→52 test files). DF-8-1-A confirmed to belong to Story 8.3 and deliberately NOT pulled in. Status: ready-for-dev. | Scrum Master (create-story) |
