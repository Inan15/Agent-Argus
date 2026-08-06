---
baseline_commit: 9109e16b4e86436a8315ed2cb967b75cdced4296
baseline_note: >-
  HEAD is 9109e16, but the working tree carries Stories 8.1, 8.2 AND 8.3's deltas
  UNCOMMITTED (git status: ~15 modified argus/ + tests/ files, 4 added test
  files/fixtures). 8.4 builds ON TOP of that uncommitted tree. Do NOT stash,
  revert, `git checkout --`, or hard-reset anything — 8.1's, 8.2's and 8.3's work
  is not recoverable from any commit. `git diff HEAD` IS the integrator-visible
  delta this story documents, and it is the measuring instrument.
  ⚠️ A CONCURRENT SESSION outside this loop is working Epic 9 in this same tree.
  Files confirmed FOREIGN — not yours, do not modify, do not build on, do not be
  surprised by: `argus/audit/minions_llm_adapter.py`, `tests/test_no_web_imports.py`,
  `stories/9-1-argus-stops-importing-thing-it-audits.md`, `action.yml`,
  `.github/workflows/argus-student-audit.yml`. EXCLUDE them from every figure you
  report, and when you write `sprint-status.yaml` change ONLY the `8-4-…` key.
---

# Story 8.4: Tell integrators what changed

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **ArgusAgent story — Argus repo, `argus/` tree only.** ArgusAgent (formerly APAA) is a self-contained
> headless audit tool extracted from the Minions monorepo into its own repository (`Agent-Argus`,
> distribution `argus-agent`, package `argus/`, console scripts `argus` / `argus-agent` / `repo-audit`).
> **RS-1 is binding: all work lands in `argus/` in THIS repo. The `minions_core/apaa/` copy in the Minions
> repo is legacy — no modification, no back-port, no dual maintenance.** Planning artifacts live under
> `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is that folder's `sprint-status.yaml`. Prose in
> older documents saying `design-artifacts/APAA/` or `minions_core/apaa/` should be read as
> `design-artifacts/ArgusAgent/` / `argus/`.
>
> **This is the FOURTH story of Epic 8** ("The Honest Verdict — no block without a finding"). `epic-8` is
> already `in-progress`. **Stories 8.1, 8.2 and 8.3 are all `done`** (each PASSED code review).
>
> **THIS STORY DELIVERS DR-8 + RS-4a — the paper trail.** Epic 8 changed the verdict contract three times
> over: the FR16 decision table was reordered (8.1), the critical-set gate became satisfiable (8.2), and
> both human report surfaces were re-worded (8.3). **Two schema versions were bumped, one exit code moved
> for a whole class of runs, a new exception type was introduced where prose used to render, and several
> persisted strings changed.** Not one word of that has been published to anyone consuming Argus. The epic's
> own outcome statement requires that an operator *"finds **no published Argus artifact contradicting the
> shipped contract**"* — right now the published artifacts do not contradict the contract, they are **silent
> about it**, which for a CI integrator is the same failure with a longer fuse.
>
> **It does NOT deliver:** DR-1/2/3/4/9 (Story 8.1, done); DR-5/6/7 (Story 8.2, done); DR-11 (Story 8.3,
> done); **DR-10 — the dogfood re-derivation, `minions-dogfood-proof.md` and BOTH published
> `final-verdict.md` artifacts are Story 8.5** (sequenced last by design so a slip stays visible). This
> story documents the *contract*; 8.5 re-derives the *evidence*. Do not do 8.5's work here and do not cite
> this repository's own current verdict as proof of anything.
>
> **🚫 EPIC 9 IS EXPLICITLY OUT OF SCOPE — read this before you interpret "tell integrators".** A release
> *note* is documentation. A release *process* is not. Epic 9 owns **IN-0 / Story 9.2 — "ship a distribution
> another repo can actually resolve"**: the release workflow, the version tag, the index/VCS-pin decision,
> and the proof that a clean install works. This story must **not** create `.github/workflows/*`, must not
> touch `action.yml`, must not tag, must not bump `pyproject.toml`'s `version`, and must not claim in prose
> that `argus-agent` `0.1.0` is published — **it is not on any index** (assumption A1, falsified 2026-08-03).
> A note that says "released" would itself become a published Argus artifact asserting something untrue.
> See **D2** for how the note is headed instead.
>
> **DF-8-3-B IS pulled in and closed here.** Its ledger `target_story` reads **`8-4`** (or the first story
> that edits `argus/cli.py`) — 8-4 is named first and unconditionally. It is ~5 lines plus one test, and it
> is *in this story's domain*: the note publishes the AR3/AR10 exit-code contract, including *"a typed
> failure degrades to exit `1`"*, and today the default `argus audit <path>` invocation (no `--report-dir`)
> can escape `main()` as an **uncaught traceback** instead. Publishing that contract while it is false on
> the default path is precisely the over-claim Epic 8 exists to delete. See **D5**.
>
> **DF-8-2-A, DF-8-2-B, DF-8-3-A and DF-8-3-C are NOT pulled in** — none of their `target_story` values name
> 8-4, and this story touches none of their trigger files. **AC12 fences all four.** See **D6**.

---

## Story

As a **CI integrator wiring `argus audit` into a pipeline** — who today can pull this branch, watch a job
that was exiting `2` start exiting `3`, watch a `schema_version` assertion on the persisted verdict fail,
watch a `grep` on `final-verdict.md` stop matching, and find **nothing anywhere in the repository that says
any of it happened** —

I want **one written, findable, verifiable statement of every consumer-visible change this amendment made,
and of what it deliberately did NOT change**,

so that **I can tell in five minutes whether my pipeline needs to change (it very likely does not) instead of
discovering it from a red build.** An assurance product that ships a behaviour change without telling its
consumers has committed the omission it exists to detect in other people's repositories.

---

## Story Context

### Method statement — MEASURED IN PLACE, on the real working tree

> ⚠️ **Read this; the 8.1 SM's method cost a fix round.** Everything below was produced on
> `d:/ProjectX/XAgents/XAgents/ArgusAgent` itself — HEAD `9109e16` **plus 8.1's, 8.2's and 8.3's uncommitted
> deltas**, `.git` and `_bmad-output/` present — **not** on a scratch copy. Two instruments were used:
>
> 1. **`git diff HEAD -- argus/`** — HEAD *is* the pre-Epic-8 baseline, because none of Epic 8 is committed.
>    That diff is literally the integrator-visible delta; every "before" string below is quoted from the
>    `-` side of it, not from memory.
> 2. **Importing the shipped `argus` functions and calling them in place** — real `evaluate_verdict(...)`
>    folds over real `CoverageLedger` inputs, rendered through the real `render_ship_readiness` and the real
>    `render_final_verdict_report`. No `.argus/` was written into this repo.
>
> The foreign Epic-9 files listed in the frontmatter are **excluded from every count below**.
> **Re-derive these figures yourself — do not trust this document.**

### The complete, concrete list of consumer-visible changes — this IS the changelog surface

Nothing here is abstract. Each row was measured; the "verify with" column is how you re-derive it.

#### A. Exit-code behaviour (DR-8 — the epic's headline item)

Exit-code **values** are unchanged (`0`/`2`/`3`/`1`, AR3). What moved is **which runs map to which value**.

| Run shape | Before (HEAD `9109e16`) | After (Epic 8) |
|---|---|---|
| ≥1 verdict-blocking finding, coverage ≥ floor | `NOT_READY_FOR_RELEASE` / **2** | `NOT_READY_FOR_RELEASE` / **2** — unchanged |
| assessed ratio `< 1/5` (the floor) | `INSUFFICIENT_COVERAGE` / **3** | `INSUFFICIENT_COVERAGE` / **3** — unchanged |
| ratio ≥ `3/5` **and** all criticals deep, 0 findings | `RELEASE_READY` / **0** | `RELEASE_READY` / **0** — unchanged |
| **0 blocking findings + an unmet coverage or critical gate, at or above the floor** | `NOT_READY_FOR_RELEASE` / **2** | **`INSUFFICIENT_COVERAGE` / 3** ← **the only behaviour change** |

Measured exit map (imported `exit_code_for_verdict` over the whole `Verdict` enum):
`RELEASE_READY→0 · NOT_READY_FOR_RELEASE→2 · INSUFFICIENT_COVERAGE→3`. Unchanged as a mapping.

The three consequences an integrator actually needs, and all three must appear in the note:

- A step branching only on **`0` vs non-zero` is unaffected**. Nothing that was non-zero became zero.
- A step distinguishing **`2` from `3`** now receives the **correct** one for the zero-findings case, with
  **no consumer code change** — `2` means *Argus found something*, `3` means *Argus did not examine enough
  to vouch*. That was the point of the amendment.
- **Nothing became a silent pass.** Exit `3` still fails an unconfigured CI step. A pipeline that treats `3`
  as success has changed its own risk posture, not inherited one.

#### B. Two schema-version bumps — both consumer-visible, both measured

| Constant | Before | After | Where |
|---|---|---|---|
| `VERDICT_SCHEMA_VERSION` | `"1"` | **`"2"`** | `argus/verdict/verdict_gate.py:182` (was `:149`) |
| `CRITICAL_SUBSYSTEMS_SCHEMA_VERSION` | `"1"` | **`"2"`** | `argus/ledger/critical_subsystems.py:146` (was `:106`) |

**The epic's AC names only the verdict bump. There are two.** The second landed in Story 8.2, after the
epic text was written. A note that discloses one bump and conceals the other commits exactly the omission
boundary **B8** was raised against — see **Variance from the epic**.

**Measured payloads** (imported models, canonical serializer):

- Verdict artifact, live run, all four rows — payload keys are
  `blocking_finding_count · counts_by_depth · critical_subsystems_all_deep · decision_row · deep_count ·
  deep_ratio · exit_code · ordered_findings · schema_version · total_count · verdict`.
  **`decision_row` is the added key.** Row 2 example, canonical bytes:
  `{"blocking_finding_count":1,…,"decision_row":"row_2_blocking_findings","deep_count":9,"deep_ratio":"9/…`
- **Backward compatibility is real and was verified, not assumed.** A pre-amendment payload
  (`schema_version="1"`, no `decision_row`) still validates under `extra="forbid"`, and
  `to_canonical_payload()` **omits the key entirely** rather than emitting `"decision_row":null` — measured
  key list for a v1 read-back is the old ten keys exactly, so a `"1"`-stamped verdict re-serializes
  **byte-identically** and keeps its content hash. `AuditVerdict.is_below_floor` carries the fallback.
- Critical-subsystem artifact, before: `{"designated_but_unmatched":[],"origins":{},"paths":[],"schema_version":"1"}`
  (quoted from the committed fixture `tests/fixtures/verdict_schema_v1_row2_artifacts.json`).
  After: `{"designated_but_unmatched":[],"heuristic_excluded_ineligible":{},"origins":{},"paths":[],"schema_version":"2"}`.
  ⚠️ **`heuristic_excluded_ineligible` is emitted UNCONDITIONALLY — even when empty.** Unlike
  `decision_row`/`coverage_scope`/`critical_subsystems_not_deep`, it has no omit-when-unengaged rule, so
  **every** critical-subsystems artifact changes bytes on **every** run. Populated example:
  `"heuristic_excluded_ineligible":{"tests/test_auth.py":"test_file"}`.

**Consequence an integrator will hit and the exit-code framing conceals:** `.argus/` filenames are
**content-addressed** (`state/<sha256>.json`). Both bumps change the content hash, therefore the **filename**.
A consumer that pinned a previous artifact path or hash will not find it. This is the sanctioned
additive-only lever (NFR-M2, `verdict_gate.py`'s own rule) — it is intentional, and it must be *stated*.

#### C. New / changed public Python surface (for library consumers, not just CLI)

Measured by importing each name from the shipped tree:

| Name | Kind | Where |
|---|---|---|
| `DecisionRow` | **new** 4-member `str` enum: `row_1_below_floor · row_2_blocking_findings · row_3_gates_met · row_4_gate_unmet_no_findings` | `argus/verdict/verdict_gate.py:210` |
| `AuditVerdict.decision_row` | **new** field, `DecisionRow \| None`, default `None` | `verdict_gate.py:338` |
| `AuditVerdict.is_below_floor` | **new** derived property — THE single source of truth for row 1 vs row 4 | `verdict_gate.py:381` |
| `ShipReadinessError` | **new** `ValueError` subclass, **exported** | `argus/reports/plain_english.py:90` |
| `CriticalIneligibility` | **new** 2-member `str` enum: `test_file · zero_definition_module` | `argus/ledger/critical_subsystems.py` |
| `CriticalCandidate.ineligibility` | **new** field | `critical_subsystems.py` |
| `CriticalSubsystemSet.heuristic_excluded_ineligible` | **new** field, always serialized | `critical_subsystems.py` |
| `ProsecutionResult.verdict_changed` | **new** field; new rationale token `reclassified:<from>-><to>` | `argus/verdict/prosecutor.py` |
| `is_test_classification_content_dependent` | now **exported** from `argus/detectors/vacuous_test.py` | Story 8.2 |

⚠️ **`ShipReadinessError` is the load-bearing one and the note must call it out by name.** It is a **NEW
RAISE at a site that previously always returned prose**: `render_ship_readiness` / `_headline` used to have
a terminal `else` returning a "NOT VOUCHED" sentence; that predicate (`NOT_READY_FOR_RELEASE` with
`blocking_finding_count == 0`) is now unreachable from `evaluate_verdict` and raises instead. **Anyone
calling `render_ship_readiness` directly must know it can now raise.** Verified in place: constructing that
verdict by hand and rendering it raises
`ShipReadinessError: NOT_READY_FOR_RELEASE with blocking_finding_count=0: FR16 row 2 is the only producer of
this verdict and it requires at least one verdict-eligible finding`, and `isinstance(exc, ValueError)` is
`True`.

#### D. Rendered strings that changed — anything string-matching Argus output is affected

**Measured by rendering both surfaces for every FR16 row.** "Before" is quoted from `git diff HEAD`'s `-`
side; "after" from a live render.

**Human register (`render_ship_readiness`, stderr + the first quoted line of `final-verdict.md`):**

| Row | Before | After |
|---|---|---|
| 1 (below floor) | `NOT ASSESSED — too little of the code was examined deeply to make any call. This is a statement about the audit, not about the code.` | **byte-identical** |
| 2 (blocking) | `BLOCKED — N verdict-blocking finding(s) must be resolved.` | **byte-identical** (N ≥ 1 always now) |
| 3 (gates met) | `READY — no blocking problems found, and enough of the code was examined deeply to say so.` | **byte-identical** |
| 4 (gate unmet, nothing found) | `NOT VOUCHED — nothing broken was found, but **a coverage gate** was not met, so no release-readiness claim is made. …` | `NOT VOUCHED — nothing broken was found, but **a coverage or critical-subsystem gate** was not met, so no release-readiness claim is made. …` |

Row 4 also **changed which verdict it wears**: before, that prose appeared under `NOT_READY_FOR_RELEASE` /
exit `2`; now under `INSUFFICIENT_COVERAGE` / exit `3`.

**Persisted report (`render_final_verdict_report` → `final-verdict.md`):**

| Row | Before | After |
|---|---|---|
| 2 | `> [!CAUTION] Repository is NOT ready for release — 1 verdict-blocking finding(s)**; deep coverage `x/y` is below the `3/5` release threshold; at least one critical subsystem is not audited deep (FR16)**.` — clauses appended | `> [!CAUTION] Repository is NOT ready for release — 1 verdict-blocking finding(s).` — **coverage/critical clauses removed** |
| 4 | `> [!CAUTION] Repository is NOT ready for release — deep coverage `3/10` is below the `3/5` release threshold.` | `> [!WARNING] Release readiness is NOT VOUCHED — Argus found nothing blocking, but deep coverage `3/10` is below the `3/5` release threshold. This is a statement about the audit, not about the code.` — **callout LEVEL changed CAUTION→WARNING** |
| 4 (critical-clause cause, 10/10 deep) | same false `[!CAUTION] … NOT ready for release …` | `> [!WARNING] Release readiness is NOT VOUCHED — Argus found nothing blocking, but at least one critical subsystem is not audited deep (FR16). …` |
| 1, 3 | `[!WARNING] Repository deep coverage ratio is below the required floor…` / `[!TIP] Repository satisfies all deterministic release readiness criteria…` | **byte-identical** |

Also changed: the dilution note `" Note that <…> would still block."` → `" Note that the
critical-subsystem clause would still withhold `RELEASE_READY`."`; and **`### Critical subsystems below
`audited_deep` (N)` now renders on EVERY row carrying a non-empty critical set**, not only the blocking one
(Story 8.3 review round 2) — its heading text also changed from *"the critical paths that withheld
`RELEASE_READY`"*.

**Persisted negative-assurance statement** (`.argus/state/*.json`, producer
`argus.verdict.negative_assurance`) — a machine-read artifact string, easily missed:

- Before, for the row-4 case: `Assessed coverage is below the floor; no repo-wide verdict was rendered (…).`
- After: `No blocking findings were detected within the assessed scope; a coverage or critical-subsystem
  gate was not met, so release readiness was not vouched for (…).`
- The row-1 sentence is **byte-identical** to before.

#### E. What deliberately did NOT change — the reassurance half, and it is load-bearing

- **The stdout machine summary line is byte-identical**, per the Story 8.1 **LOCKED channel decision**:
  `verdict=<TOKEN> deep_ratio=<num/den> blocking_findings=<n>` (+ `assessed_deep_ratio` / `scope` /
  `held_out` when narrowed). **No decision-row field was added to it.** `argus/cli.py` is byte-identical to
  HEAD (`git diff --stat HEAD -- argus/cli.py` → empty) before this story's DF-8-3-B fix.
- **The verdict enum did not grow.** Adding `COVERAGE_GATE_UNMET` was considered and rejected (addendum §A1).
- **Exit-code values are unchanged** (`0`/`2`/`3`/`1`).
- **The row is derivable from the unchanged stdout line** — this is the LOCKED decision's *accepted residual
  risk*, and the note is the only place it can be mitigated: `INSUFFICIENT_COVERAGE` with assessed ratio
  `< 1/5` ⇒ row 1; `NOT_READY_FOR_RELEASE` ⇒ row 2; `RELEASE_READY` ⇒ row 3; `INSUFFICIENT_COVERAGE` with
  assessed ratio `>= 1/5` ⇒ row 4. **The artifact carries the row authoritatively; a consumer needing
  certainty should read `decision_row` there rather than re-derive.**
- **Persisted pre-amendment verdicts under `.argus/` are not rewritten** and keep their `"1"` stamp (DR-4).

#### F. The `--coverage-scope` default flip — landed earlier, never announced

**Measured:** `git show HEAD:argus/cli.py` already has `default="application"` at `:184`. So this flip
(CR-2, 2026-08-03) landed **before** Epic 8 and is **not** part of the `git diff HEAD` delta — which is
exactly why it has no note and why the epic AC drags it into this one. A pipeline relying on the
whole-repository denominator **must now pass `--coverage-scope repository` explicitly**. Both ratios remain
printed on every run and the assessed population stays disclosed, so no consumer loses information; the
floor is still applied *within* the scope, so narrowing never lowers the bar.

### `argus/__init__.py` — the package front door (RS-4a), measured

`wc -l` = **66**, md5 `54c57920747166235627dac097055fbd`, **byte-identical to HEAD** (untouched by 8.1–8.3).
RS-4a names line 37, but reading the whole file shows the line is not the only falsehood in it — and this
file is *"the first thing any reader of the package sees"*:

| Line(s) | Claim | Status |
|---|---|---|
| 37 | `Lives at ``minions_core/argus/`` as a self-contained sub-package` | ❌ **FALSE** — RS-4a, the named target |
| 3–8 | `STATUS: **EXPERIMENTAL** (story 22-15, M9 decision)` … `DF-22-15-A` | ❌ stale — Minions-tracker story/ledger ids that do not exist in this repo |
| 10–13 | `RESERVED PACKAGE SHELL — no business logic yet` … `do NOT add audit logic here` | ❌ **FALSE** — 7 epics of business logic have landed |
| 30–31 | `distributed via the optional extra ``minions[argus]``` | ❌ **FALSE** — `pyproject.toml` declares `argus-agent` with extras `dev`/`llm`/`languages`; there is no `minions[argus]` extra here (that is the **Minions-side** IN-1 handoff) |
| 38–41 | `It reuses proven Minions infrastructure via direct import` | ❌ **FALSE and now actively wrong** — Epic 9 Story 9.1 removed the last `minions_core` import |
| 46 | `_bmad-output/planning-artifacts/decisions/2026-06-18-argus-placement-under-minions-core.md` | ❌ path does not exist in this repo |
| 48–49 | `Architecture / epics / stories: TO BE CREATED` | ❌ **FALSE** — all three exist |
| 51–53 | `Architecture-driver IDs … do not exist yet and must not be invented` | ❌ **FALSE** — the `ArgusAgent-AR*` namespace is defined and cited throughout |
| 56–66 | `__version__ = "0.1.0"`, `__status__`, `__all__` | ✅ **correct — DO NOT TOUCH.** `__version__` is the envelope's `argus_version` field, folded into content hashes (NFR-P1). Changing it changes every artifact hash. |

**Scope call (D3):** RS-4a is *"fix the package front door"* and the front door is **this file**. All of the
above is in scope. RS-4b is *"the remaining … references in `argus/` docstrings and comments"* — i.e. **every
other file**, which stays deferred. See **D3**.

### RS-4b sizing — measured, so the ledger entry is actionable rather than "~48, somewhere"

`grep -rn "minions_core" argus/ --include=*.py`, excluding `__pycache__` **and the foreign
`argus/audit/minions_llm_adapter.py`**: **16 references across 9 files**.

- `argus/__init__.py:37` → **RS-4a, fixed by this story**.
- The remaining **15 across 8 files** → RS-4b: `audit/deep_audit.py:21` · `audit/ports.py:4` ·
  `cost/budget_governor.py:15` · `dogfood/partition_plan.py:481,490,554` · `dogfood/proof_run.py:52,53,486,597,609,610` ·
  `governance/escalation.py:35` · `store/envelope.py:25` · `verdict/prosecutor.py:36`.
- ⚠️ **The self-consistency pass's "not prose only" warning is CONFIRMED by measurement.**
  `dogfood/partition_plan.py:481,554` and `dogfood/proof_run.py:597` are **`lines.append(...)` calls that
  emit the stale path INTO generated Markdown artifacts** (`"> AUTO-GENERATED by
  `minions_core/apaa/dogfood/partition_plan.py`"`, `"> AUTO-GENERATED by
  `minions_core/argus/dogfood/proof_run.py`"`). A prose-only sweep of docstrings would miss them, and the
  committed artifacts they produce would keep regenerating stale.
- ⚠️ Those same generated artifacts (`minions-dogfood-partition-plan.md`, `minions-dogfood-proof.md`) are
  **Story 8.5 / DR-10's** deliverable. RS-4b's sweep of the *generators* must therefore be sequenced with
  8.5's re-derivation, not before it. Record that in the ledger entry.

### `action.yml` — an integrator surface this story must NOT touch

`action.yml` (repo root, **untracked, foreign, Epic-9-owned**) maps the audit exit code to a verdict output:
`0→RELEASE_READY`, `2→NOT_READY_FOR_RELEASE`, **`else→INSUFFICIENT_COVERAGE`**. That `else` also swallows
**exit `1`** — a typed crash — and publishes it to downstream steps as `verdict=INSUFFICIENT_COVERAGE`, i.e.
a *ran-and-under-covered* result for a run that never produced a verdict at all. This is **pre-existing**
(exit `1` predates Epic 8) and it is on a file this loop must not edit. **File it (AC10), do not fix it.**

### Live consumers of the surfaces this story documents — read before writing a word

| Consumer | Reads | Note |
|---|---|---|
| `argus/cli.py:279-294` | `_summary_line` (stdout, frozen) + `render_ship_readiness` (stderr) | the DF-8-3-B site is `:292` |
| `argus/reports/generator.py:341` | `render_ship_readiness(verdict)[0]` as `final-verdict.md`'s first quoted line | note: returns a **tuple of lines**, not a string |
| `argus/verdict/negative_assurance.py:320-333` | `verdict.is_below_floor` → the persisted assurance sentence | changed string, section D |
| `argus/cost/exhaustion.py:496` | `verdict.is_below_floor` → `InsufficientCoverageFloorReport.below_floor` | field *description* changed; value semantics fixed |
| `action.yml` (**foreign**) | exit code → `verdict` / `exit-code` GitHub Action outputs | do not touch |
| `.github/workflows/audit-ci.yml` | the repo's own CI gate | read-only for this story |

### Known-red carve-out — inherited/deferred, user-adjudicated, DO NOT touch

Suite state as measured by the 8.3 reviewer on this exact tree, minutes before this story was written:

```
PYTHONIOENCODING=utf-8 python -m pytest tests/ -q  →  1127 collected / 1124 passed / 3 failed / 0 skipped
python -m mypy argus                                →  Success: no issues found in 69 source files
```

```
FAILED tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation
FAILED tests/test_dogfood_plan.py::test_budget_reuses_the_31_accountant_no_fork
FAILED tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run
```

1–2 are **inherited** (red at `9109e16`). 3 is **deliberate** — a rot check on `minions-dogfood-proof.md`,
which is **Story 8.5 / DR-10**'s deliverable. **Leave all three red and unmodified.** The `+1 collected`
versus 8.3's earlier baseline is the **concurrent Epic-9 session**'s `tests/test_no_web_imports.py`, not
yours — do not absorb it into your numbers. **Any fourth red is yours.**

Fence baselines to re-verify at the end (measured now):
`argus/pipeline.py` **1199 lines**, md5 `399d6da1d36d668352fd7b0d539cc307` ·
`argus/detectors/vacuous_test.py` md5 `8a0705030391df92ad1404af9d044758` ·
`argus/__init__.py` **66 lines** md5 `54c57920747166235627dac097055fbd` (yours to change) ·
`argus/cli.py` **298 lines** md5 `9a849a794c37e1d4c54e362e18560a05` (yours to change, DF-8-3-B only) ·
`argus/reports/plain_english.py` 258 · `argus/reports/generator.py` 613.

---

## Acceptance Criteria

> The epic's five ACs for Story 8.4 are carried in full as **AC1, AC2, AC3, AC8, AC10**. **AC4–AC7, AC9,
> AC11–AC13** are **additions made at story design after measuring the delta against the real tree** — each
> is justified in *Variance from the epic, recorded*.

**The release note (`CHANGELOG.md`) — DR-8**

1. **Given** the FR16/FR4 amendment has shipped,
   **When** a CI integrator reads the release note,
   **Then** it states plainly that **some runs which previously exited `2` now exit `3`** — specifically and
   only the case *zero verdict-blocking findings with an unmet coverage or critical-subsystem gate, at or
   above the 20 % floor*,
   **And** that **a step branching only on `0` vs non-zero is unaffected**,
   **And** that **a step distinguishing `2` from `3` now receives the correct one with NO consumer code
   change** (DR-8),
   **And** that **exit-code values themselves are unchanged** (`0`/`2`/`3`/`1`) and **nothing became a
   silent pass** — exit `3` still fails an unconfigured CI step,
   **And** the full four-row FR16 decision table (condition → verdict → exit) is reproduced so the claim is
   checkable rather than asserted.

2. **Given** an artifact consumer that validates `schema_version`,
   **When** it reads the note,
   **Then** the note states **BOTH** bumps — `VERDICT_SCHEMA_VERSION` `"1"`→`"2"` **and**
   `CRITICAL_SUBSYSTEMS_SCHEMA_VERSION` `"1"`→`"2"` — with the module path of each (boundary **B8**; the
   epic AC names only the first, and the second is equally consumer-visible — see *Variance*),
   **And** names the **new fields** each bump carries: `decision_row` (values enumerated) on the verdict,
   `heuristic_excluded_ineligible` on the critical-subsystem set,
   **And** states the two **different** compatibility behaviours, because they are genuinely different:
   `decision_row` is **omitted entirely** from a pre-amendment (`"1"`-stamped) payload so it round-trips
   byte-identically, while `heuristic_excluded_ineligible` is emitted **unconditionally, even when empty**,
   so **every** critical-subsystem artifact changes bytes on every run,
   **And** states the consequence: `.argus/` filenames are content-addressed, so a changed payload means a
   **changed filename** — a consumer pinning a previous artifact path or hash will not find it,
   **And** states that verdicts already persisted under `.argus/` are **not rewritten** and keep their
   `"1"` stamp (DR-4).

3. **Given** the `--coverage-scope application` default flip landed earlier (CR-2, 2026-08-03) without a
   published note,
   **When** the same release note is read,
   **Then** it carries that change too, stating that a pipeline relying on the whole-repository denominator
   **must now pass `--coverage-scope repository` explicitly**,
   **And** that both ratios remain printed and the assessed population remains disclosed, so no consumer
   loses information,
   **And** that the coverage floor is still applied **within** the scope — narrowing changes what is
   claimed, never the bar for claiming it,
   **And** the note is honest that this flip **predates** the Epic-8 delta rather than implying it is part
   of it (measured: `default="application"` is already present at HEAD `9109e16`).

4. **Given** any consumer that string-matches Argus's human or persisted output,
   **When** it reads the note,
   **Then** the note enumerates the **rendered strings that changed**, concretely and quotably — at minimum:
   the row-4 ship-readiness headline (`a coverage gate` → `a coverage or critical-subsystem gate`, and its
   move from exit `2` to exit `3`); the `final-verdict.md` row-4 callout (`[!CAUTION] Repository is NOT ready
   for release — …` → `[!WARNING] Release readiness is NOT VOUCHED — Argus found nothing blocking, but …`,
   **including the callout-level change**); the row-2 callout losing its appended coverage/critical clauses;
   the `### Critical subsystems below `audited_deep`` section now rendering on every row that carries a
   non-empty critical set; and the **persisted negative-assurance statement** for row 4,
   **And** it states equally explicitly which strings are **byte-identical** to before (rows 1, 2, 3
   ship-readiness headlines; the row-1 and row-3 callouts; the row-1 assurance sentence),
   **And** every "before" string in the note is the **real pre-Epic-8 string**, re-derived by the dev from
   `git diff HEAD` / `git show HEAD:<file>` — **not** copied from this story on trust.

5. **Given** the Story 8.1 **LOCKED channel decision**,
   **When** the note describes the machine surfaces,
   **Then** it states that the **stdout summary line is byte-identical** to the pre-amendment format —
   `verdict=<TOKEN> deep_ratio=<num/den> blocking_findings=<n>` (+ `assessed_deep_ratio`/`scope`/`held_out`
   when narrowed) — and carries **no** new decision-row field,
   **And** it publishes the **row-derivation rule** from that unchanged line (ratio `< 1/5` +
   `INSUFFICIENT_COVERAGE` ⇒ row 1; `NOT_READY_FOR_RELEASE` ⇒ row 2; `RELEASE_READY` ⇒ row 3;
   `INSUFFICIENT_COVERAGE` + ratio `>= 1/5` ⇒ row 4) — this note is the **only** place the LOCKED decision's
   *accepted residual risk* can actually be mitigated,
   **And** it directs a consumer needing certainty to read **`decision_row` on the artifact** rather than
   re-derive, because re-deriving is a partial copy of the decision table and that fragility is what caused
   this bug,
   **And** it states that the verdict **enum did not grow** — `COVERAGE_GATE_UNMET` was considered and
   rejected (addendum §A1).

6. **Given** a library consumer importing `argus.*` rather than shelling out,
   **When** it reads the note,
   **Then** the note carries a short **API surface** section listing the added names — `DecisionRow`,
   `AuditVerdict.decision_row`, `AuditVerdict.is_below_floor`, `ShipReadinessError`, `CriticalIneligibility`,
   `CriticalCandidate.ineligibility`, `CriticalSubsystemSet.heuristic_excluded_ineligible`,
   `ProsecutionResult.verdict_changed` (+ the `reclassified:<from>-><to>` rationale token), and the newly
   exported `is_test_classification_content_dependent`,
   **And** it flags **`ShipReadinessError` as a behavioural change, not merely an addition**: a call site
   that previously always returned prose can now **raise**, and the note says which state triggers it and
   that it is a `ValueError` subclass the CLI degrades to exit `1`,
   **And** every name in that list is verified to be importable from the shipped tree (no name is listed
   from this story on trust).

7. **Given** the release note must be findable and must not become a second, drifting copy of anything,
   **When** it is placed,
   **Then** it lives at **`CHANGELOG.md` in the repository root** (see **D1**), is headed as **unreleased**
   per **D2** — it must **not** assert that `argus-agent` `0.1.0` is tagged or published to any index,
   because it is not (assumption A1, falsified; Story 9.2 owns that) —
   **And** `README.md` gains **exactly one** pointer line to it, and **no** duplicated exit-code table or
   contract text anywhere else in the repo (§3.3 no-fork applied to documentation — one statement, one
   place),
   **And** the note creates **no** release workflow, tag, `action.yml` edit, or `pyproject.toml` version
   change (see **AC12** fences).

**The package front door — RS-4a**

8. **Given** `argus/__init__.py`,
   **When** it is read,
   **Then** it **no longer claims the package lives at `minions_core/argus/`** (RS-4a, the epic AC), and it
   no longer carries the other measured falsehoods enumerated in *Story Context* — the `RESERVED PACKAGE
   SHELL — no business logic yet` claim, the `EXPERIMENTAL (story 22-15) / DF-22-15-A` Minions-tracker
   status, the `minions[argus]` distribution claim, the `reuses proven Minions infrastructure via direct
   import` claim (falsified outright by Epic 9's Story 9.1), the dead
   `_bmad-output/planning-artifacts/decisions/…` path, and `Architecture / epics / stories: TO BE CREATED`,
   **And** what replaces them is **true and verifiable today**: the package is `argus/` in the standalone
   Agent-Argus repo, distribution `argus-agent`, console scripts `argus` / `argus-agent` / `repo-audit`,
   installs and runs with no Minions present, with authoritative-source paths that **exist** on disk,
   **And** **`__version__ = "0.1.0"`, `__status__` and `__all__` are BYTE-IDENTICAL** — `__version__` is the
   envelope's `argus_version` field and is folded into every content hash (NFR-P1); changing it would change
   every artifact hash in the repo,
   **And** a committed test pins the removal: the file contains **zero** occurrences of `minions_core`, of
   `RESERVED PACKAGE SHELL`, and of `minions[argus]`, and `argus.__version__ == "0.1.0"`.

**Keeping the note honest — the rot check**

9. **Given** an assurance product whose central claim is that no published artifact of its own contradicts
   its shipped contract,
   **When** the release note is committed,
   **Then** a committed test **fails** if the note drifts from the code — it asserts, by **importing the
   shipped constants and rendering the shipped strings**, that `CHANGELOG.md` contains the live values of
   `VERDICT_SCHEMA_VERSION` and `CRITICAL_SUBSYSTEMS_SCHEMA_VERSION`, the live `exit_code_for_verdict`
   mapping for all three verdicts, every `DecisionRow` member value, and the four live ship-readiness
   headlines produced by real `evaluate_verdict` folds,
   **And** it asserts the note does **not** contain the pre-amendment strings it says were replaced (e.g.
   the bare `a coverage gate was not met` row-4 wording),
   **And** it asserts the note makes **no published-distribution claim** — no `pip install argus-agent` from
   an index, no version tag — while `argus-agent` is on no index (the D2 honesty pin),
   **And** it is demonstrated **RED-first**: show it failing against a deliberately-stale note before it
   passes against the real one, and record the failure output verbatim,
   **And** it introduces **no new dependency** and needs no network, no LLM and no `.argus/` write
   (NFR-D2). Precedent: `tests/test_dogfood_proof.py`'s committed-artifact rot check; repo-root located as
   `Path(__file__).resolve().parents[1]`.

**Ledger obligations — RS-4b and the two findings this story made**

10. **Given** the bulk provenance sweep is out of scope,
    **Then** **RS-4b is filed in `deferred-work.md`** with the six mandatory CC-3 fields
    (`id · origin_story · owner · target_story|sunset_date · category · severity`) and
    `origin_story: 8-4-tell-integrators-what-changed` (the epic AC),
    **And** the entry is **actionable, not a gesture**: it carries the **measured** surface — 15 references
    across 8 `argus/*.py` files, enumerated with line numbers, foreign files excluded — and explicitly
    records that **three of them are `lines.append(...)` calls that emit the stale path into GENERATED
    Markdown artifacts** (`dogfood/partition_plan.py:481,554`, `dogfood/proof_run.py:597`), so a prose-only
    sweep would miss them,
    **And** it records the sequencing constraint that those generators produce **Story 8.5 / DR-10's**
    artifacts, so the sweep follows 8.5's re-derivation rather than preceding it,
    **And** a second entry **`DF-8-4-A`** is filed with the same six fields for the `action.yml` exit-`1`
    mislabel measured above, `target_story: 9-2-ship-distribution-another-repo-can-actually-resolve`,
    explicitly noting the file is **untracked, foreign and Epic-9-owned — not to be edited by Epic 8**,
    **And** both filings are **append-only** at the end of the register under a dated section header,
    rewriting **nothing** (§3.4 evidence immutability). ⚠️ **Re-read `deferred-work.md` immediately before
    writing it** — a concurrent session shares this tree.

**DF-8-3-B — closed here, per its ledger `target_story: 8-4`**

11. **Given** `argus/cli.py:292` calls `render_ship_readiness(verdict)` **outside** the
    `try/except ValueError` that wraps `run_audit(request)` at `:270-277`, so a `ShipReadinessError` at that
    site would escape `main()` as an **uncaught traceback** rather than the typed, secret-safe exit `1` the
    AR10 / NFR-R1 degradation contract requires (masked only when `--report-dir` is set, and `report_dir`
    defaults to empty),
    **When** this story lands,
    **Then** the guard covers the real site — widen the `try` to include the summary-line + ship-readiness
    block, or move the render inside it — **without changing stdout/stderr byte output or the returned exit
    code on any non-raising path**,
    **And** a test lets the **REAL** `render_ship_readiness` raise on the way out of `main()` **with no
    `--report-dir`**, and asserts `main()` returns `1` with a secret-safe stderr line naming the typed
    reason only (no traceback, no absolute path, no source bytes) — Story 8.3's `TC-ArgusAgent-CLI-001-32`
    monkeypatches `cli.run_audit` and therefore proves the AC's letter without exercising this site; do not
    repeat that,
    **And** the existing stdout-summary-line golden assertions still pass **byte-identically** (this is the
    frozen wire contract, section E),
    **And** the ledger entry `DF-8-3-B` is **closed with an append-only closure note** naming the closing
    test id — the original entry is not rewritten.

**Standing Epic-8 obligations**

12. **Given** the fences,
    **Then** these files are **MUST-NOT-MODIFY** for this story:
    - `argus/pipeline.py` — **DF-8-2-A**, 1199/1200 lines, md5 `399d6da1d36d668352fd7b0d539cc307`. If you
      believe you must edit it, **STOP**: the close condition is *extract a shell-helper module first*, and
      that is not this story's job.
    - `argus/detectors/vacuous_test.py` — **DF-8-2-B**, md5 `8a0705030391df92ad1404af9d044758`.
    - `argus/verdict/verdict_gate.py`, `argus/ledger/critical_subsystems.py`,
      `argus/reports/plain_english.py`, `argus/reports/generator.py`,
      `argus/verdict/negative_assurance.py`, `argus/verdict/prosecutor.py`, `argus/cost/exhaustion.py` —
      **this story DOCUMENTS the contract; it does not change it.** A single behavioural edit here
      invalidates the note it is writing.
    - `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md`,
      `minions-dogfood-partition-plan.md`, `minions-dogfood-budget-plan.md`,
      `_bmad-output/reports/final-verdict.md`, `_bmad-output/audit-reports/final-verdict.md`,
      `tests/test_dogfood_proof.py`, `tests/test_dogfood_plan.py` — **Story 8.5 / DR-10**.
    - `action.yml`, `.github/workflows/*`, `argus/audit/minions_llm_adapter.py`,
      `tests/test_no_web_imports.py`, `stories/9-1-*.md` — **FOREIGN / Epic 9**.
    - `pyproject.toml` `version`, and `argus/__init__.py`'s `__version__` / `__status__` / `__all__`.
    - `tests/fixtures/verdict_schema_v1_row2_artifacts.json` — **evidence, not a golden to regenerate**.
    **And** each fence is verified at the end by `git diff --stat HEAD -- <path>` (empty) or by md5, and the
    result recorded.

13. **Given** the whole-system obligation,
    **Then** the full suite runs (`PYTHONIOENCODING=utf-8 python -m pytest tests/ -q`) and `python -m mypy
    argus` is clean, with the **exact** collected/passed/failed/skipped numbers recorded verbatim,
    **And** the **only** failures are the three adjudicated carve-out reds, unmodified — **any fourth red is
    yours**,
    **And** `argus audit .` is run live on this repository and its **actual** stdout summary line + exit code
    are recorded **as observed, nothing adjusted** — this is a consistency check on the note, not a target;
    if the run contradicts anything the note claims, **fix the note, never the run**,
    **And** the dispositions of **DF-8-2-A, DF-8-2-B, DF-8-3-A, DF-8-3-C** are each stated explicitly in the
    Dev Agent Record as **carried forward, not closed**, with the reason (their `target_story` does not name
    8-4 and their trigger files are fenced),
    **And** the concurrent Epic-9 session's contribution to any count is separated out rather than absorbed.

---

## Tasks / Subtasks

- [x] **Task 0 — Re-derive before you write (AC1–AC6, AC9).** Do NOT trust this story's tables.
  - [x] `git status` / `git rev-parse HEAD` — confirm HEAD `9109e16` and the uncommitted 8.1–8.3 tree.
  - [x] `git diff HEAD -- argus/` and `git show HEAD:argus/reports/plain_english.py` /
        `:argus/reports/generator.py` / `:argus/verdict/verdict_gate.py` / `:argus/ledger/critical_subsystems.py`
        / `:argus/cli.py` — extract every **before** string first-hand.
  - [x] Import the shipped tree and re-render all four FR16 rows through the real `evaluate_verdict` →
        `render_ship_readiness` / `render_final_verdict_report` (note: `render_ship_readiness` returns a
        **tuple of lines**; `render_final_verdict_report(request, verdict, ledger, total_findings_count, *,
        source_state=None, ast_index=None)`). Capture the **after** strings.
  - [x] Verify every API name in AC6 is importable; verify the v1 read-back key list and the two
        critical-subsystem payloads.
  - [x] Record the method (in place, which tree, foreign files excluded) in the Dev Agent Record.
- [x] **Task 1 — Write `CHANGELOG.md` (AC1–AC7).**
  - [x] Heading + honesty preamble per **D2**; sections per **D4**'s proposed shape.
  - [x] Exit-code section (AC1) incl. the four-row table.
  - [x] Schema section (AC2) — **both** bumps, both compatibility behaviours, content-address consequence.
  - [x] `--coverage-scope` section (AC3), honest about it predating the delta.
  - [x] Changed-strings section (AC4) with a matching **unchanged** list.
  - [x] Unchanged-machine-surface section (AC5) incl. the row-derivation rule and the "read `decision_row`
        instead" direction.
  - [x] API-surface section (AC6) with `ShipReadinessError` flagged as behavioural.
  - [x] One pointer line in `README.md` (AC7). No second copy of any contract text anywhere.
- [x] **Task 2 — Rewrite `argus/__init__.py`'s docstring (AC8).**
  - [x] Replace the stale docstring; verify every path it cites exists on disk.
  - [x] Leave `__version__` / `__status__` / `__all__` byte-identical; confirm by diff.
  - [x] Add the pin test (zero `minions_core`, zero `RESERVED PACKAGE SHELL`, zero `minions[argus]`,
        `__version__ == "0.1.0"`).
- [x] **Task 3 — The rot check (AC9), RED-first.**
  - [x] New `tests/test_release_note.py`, ids `TC-ArgusAgent-DOCS-001-01`… (new area — no `DOCS` area exists
        yet; do **not** restart an existing sequence).
  - [x] Prove RED against a deliberately-stale note; paste the failure verbatim into the Dev Agent Record;
        then make it green.
- [x] **Task 4 — DF-8-3-B (AC11).**
  - [x] Widen the `try` in `argus/cli.py::main` to cover `:279-294`; keep every non-raising path
        byte-identical.
  - [x] Test that lets the REAL `render_ship_readiness` raise with **no** `--report-dir` → `main()` returns
        `1`, stderr secret-safe. Continue `TC-ArgusAgent-CLI-001-33`+ (8.3 locked to `-32`).
  - [x] Re-run the existing stdout golden assertions.
  - [x] Append-only closure note on `DF-8-3-B`.
- [x] **Task 5 — Ledger (AC10).** Re-read `deferred-work.md` immediately before writing. Append a dated
      section with **RS-4b** and **DF-8-4-A**, six CC-3 fields each, measured surfaces, no rewrites.
- [x] **Task 6 — Fences + whole system (AC12, AC13).** Verify every fenced path by `git diff --stat HEAD`
      or md5; run the full suite + mypy; run `argus audit .` live; record everything verbatim, including the
      four carried DF dispositions and the concurrent-session separation.

### Review Findings

> Code review iteration 1 — 2026-08-06. Every figure below was **re-derived by the reviewer**, in place, on
> this tree. What was independently confirmed and needs no rework: both schema bumps and their two different
> compatibility behaviours (v1 verdict payload re-validates under `extra="forbid"`, `decision_row` omitted,
> ten keys, `canonical.dumps` round-trip **byte-identical**; empty critical-subsystem payload sha256
> `71bf02…` → `154d11…`, i.e. the **filename** really does move); exactly **one** run class moved `2`→`3`
> (HEAD's fold has three branches with `else → NOT_READY_FOR_RELEASE`, the live fold has four); all four
> live ship-readiness headlines and all four `final-verdict.md` callouts match the note **byte-for-byte**,
> including the row-4 `CAUTION`→`WARNING` level change; all 9 API names import; `--coverage-scope`'s
> `default="application"` is present at `git show HEAD:argus/cli.py:184`, so the note attributes the flip
> correctly as pre-dating the delta; RS-4b re-measured at **15 refs / 8 files**, of which **6 refs across 5
> `lines.append(...)` sites** (`partition_plan.py:481,490,554`, `proof_run.py:597,609-610`) — the dev's
> upward correction is right and the ledger reflects it; `RS-4b` / `DF-8-4-A` filed with six CC-3 fields each,
> `deferred-work.md` **250 added / 0 removed** (genuinely append-only); Story 8.5's artifacts and
> `tests/test_dogfood_proof.py` / `test_dogfood_plan.py` are **untouched** and the proof rot check is
> **unweakened** (still the full `` `RELEASE_READY` (exit `0`) `` assertion); fences hold —
> `argus/pipeline.py` md5 `399d6da1d36d668352fd7b0d539cc307` @ 1199 lines and
> `argus/detectors/vacuous_test.py` md5 `8a0705030391df92ad1404af9d044758`; `__version__` / `__status__` /
> `__all__` byte-identical; `CHANGELOG.md` and `tests/test_release_note.py` are both `git add`ed.
> **Reviewer's own suite: 1145 collected / 1142 passed / 3 failed / 0 skipped** (progress map 15×72+65, exactly
> three `F`, zero `s`, zero `E`) — exactly the adjudicated carve-out; `mypy` clean over 69 source files.
> **DF-8-3-B closure independently verified**: the pre-fix `argus/cli.py` was injected at runtime (`git show
> HEAD:argus/cli.py`, md5 `ffa368d9…`) and `TC-ArgusAgent-CLI-001-33` went **RED with an uncaught
> `argus.reports.plain_english.ShipReadinessError` escaping `main()`** from the real renderer at
> `plain_english.py:182` on the default no-`--report-dir` path, while `-30` / `-31` / `-32` all stayed
> **green** against that same pre-fix file — which is the proof that `-32` never exercised the site and that
> the widening moves no golden. `cli.py` restored to md5 `2b671c71c43c7fb556d3e734cd91185e`.
>
> **The three items flagged for adjudication are ruled as follows.**
> **(1) AC4-vs-AC9 reconciliation — SOUND, accepted.** Taken literally the two ACs are unsatisfiable;
> requiring every pre-amendment string to sit in an explicitly-labelled *"before"* context is the only
> reading that honours both, it is the universal changelog convention, and `TC-ArgusAgent-DOCS-001-06`
> asserts **both** directions (the history is present *and* labelled, and the live replacement is published),
> so a note that simply deletes the history fails too. No change required.
> **(2) The deliberate deviation on `argus/__init__.py`'s `__status__` comment — CORRECT, stands.** The
> binding fence is **AC12**, which names the three **assignments** (`__version__` / `__status__` / `__all__`),
> not lines 56-66; the "56-66 do-not-touch" range is a descriptive Story Context measurement, and a
> measurement table does not bind against an AC. **AC8** binds and explicitly requires the file to stop
> carrying *"the `EXPERIMENTAL (story 22-15) / DF-22-15-A` Minions-tracker status"* — which lived in that
> comment as well as in the docstring. Leaving it would have left AC8 half-met and left dead cross-repo
> tracker ids in the front door, i.e. the exact RS-4a defect. Verified: all three assignments are
> byte-identical to HEAD, the NFR-P1 hash contribution is untouched, and `TC-ArgusAgent-DOCS-001-10` pins
> them mechanically. **Do not revert.**
> **(3) RS-4b's re-measurement — CONFIRMED.** Six refs across five `lines.append(...)` sites, total unchanged
> at 15/8, and `proof_run.py:486` is correctly identified as a third kind (a `DogfoodProofError` message).
> The ledger entry reflects the measured six.
>
> **PRIORITY-1 ruling — the `RELEASE_READY` → `INSUFFICIENT_COVERAGE` move is BENIGN and is finding R2's
> cause, not a regression.** It is none of the three candidate explanations. The cause is a **changed
> invocation**: the dev ran `python -m argus.cli audit . --commit HEAD --budget 200`, whereas 8.2 and 8.3 ran
> `python -m argus.cli audit .`. `--budget` **defaults to `0` = NO ceiling** (`argus/cli.py:101-111`); `200`
> is a positive credit ceiling that halts the deep pass early, taking `deep_count` **57 → 29**. Reviewer's
> re-runs on this exact tree, minutes apart:
> `audit .` → `verdict=RELEASE_READY deep_ratio=57/149 blocking_findings=0 assessed_deep_ratio=57/73
> scope=application held_out=76`, **exit `0`**, a real `row_3_gates_met`; `audit . --commit HEAD --budget 200`
> → `verdict=INSUFFICIENT_COVERAGE deep_ratio=29/149 … assessed_deep_ratio=29/73 …`, **exit `3`**, a real
> `row_4_gate_unmet_no_findings`. Both folds are **correct**: `57/73 ≥ 3/5` with 0 findings and all criticals
> deep is row 3; `29/73` (≥ the `1/5` floor, < `3/5`) with 0 findings is row 4. The `+1` in the denominator
> (`148`→`149`, `held_out` `75`→`76`) is this story's own `tests/test_release_note.py`. **Nothing in 8.4 or
> in the concurrent Epic-9 session moved the verdict path**, and the row-4 fold the dev observed is an
> honest row 4 — which is the epic working, not failing.

**Resolved — fix round 2, 2026-08-06. All four addressed; see *Fix round 2* in the Dev Agent Record.**

- [x] [Review][Patch] **R1 (Med) — the note publishes a FALSE "before" string for the persisted
      negative-assurance statement, and silently omits the real one** [`CHANGELOG.md:176-181`]. Violates
      **AC4**'s binding *"every 'before' string in the note is the real pre-Epic-8 string, re-derived by the
      dev from `git diff HEAD` / `git show HEAD:<file>` — **not** copied from this story on trust"*, and the
      Epic-8 outcome statement. **Re-derived by executing HEAD's `_assurance_statement` verbatim** (extracted
      with `git show HEAD:argus/verdict/negative_assurance.py` and `exec`'d against the real `ScopeStatement`):
      that function branches **only** on `verdict.verdict`, and HEAD's fold gave a row-4-shaped run
      (0 blocking findings + an unmet gate, at or above the floor) the verdict `NOT_READY_FOR_RELEASE`.
      So the real pre-amendment sentence for the run class that moved is
      `Blocking findings were detected within the assessed scope (…).`
      The note instead publishes `Assessed coverage is below the floor; no repo-wide verdict was rendered (…).`
      — which HEAD produced **only** for `INSUFFICIENT_COVERAGE`, i.e. **row 1**, and which the note itself
      already (correctly) lists as byte-identical at `:193`. Two defects in one: the stated "before" is
      false, and the **most consequential persisted-string change in the whole delta is omitted** — a
      machine-read `.argus/state/*.json` string that used to assert *"Blocking findings were detected"* for a
      run with **zero** findings now asserts *"No blocking findings were detected…"*. That is precisely the
      audience section *Output: changed strings* addresses, and it is the sharpest demonstration of the bug
      the epic fixed. This is the one claim in the note that the dev's *"every 'before' re-derived from
      `git show HEAD:<file>`"* record does not hold for — it was copied from this story's own §D table
      (`:230`), the exact trap *Traps a previous story already paid for* warns about.
      **Fix:** set the row-4 "before" to `Blocking findings were detected within the assessed scope (…).`;
      leave `Assessed coverage is below the floor; …` where it belongs (row 1, already in the byte-identical
      list); optionally add one sentence that the single pre-amendment `INSUFFICIENT_COVERAGE` sentence is now
      split on the decision row.
- [x] [Review][Patch] **R2 (Med) — the Dev Agent Record states a false negative about the live run**
      [`stories/8-4-tell-integrators-what-changed.md:1039-1041`]. Violates **AC13**'s *"recorded as observed,
      nothing adjusted"* and the epic's own honesty standard. The record asserts *"D8's parenthetical claim
      that `argus audit .` currently returns `RELEASE_READY` on ArgusAgent **did not reproduce**"*. It does
      reproduce — the dev did not run `argus audit .`; it ran `argus audit . --commit HEAD --budget 200`, and
      `--budget` defaults to `0` = no ceiling. See the PRIORITY-1 ruling above for both re-runs. Recording the
      observation was right; the **inference** attached to it attributes a flag's effect to the tool, and it
      is the kind of unsupported negative claim this epic exists to delete. **Fix:** amend the record to name
      the `--budget 200` invocation, state that the row-4 result is the correct fold for a budget-capped run,
      and state that D8 reproduces under the unflagged invocation 8.2/8.3 used. Nothing in `CHANGELOG.md`
      needs to change — D8 correctly kept this run out of the note.
- [x] [Review][Patch] **R3 (Low) — the rot check leaves the note's `final-verdict.md` callouts and the
      persisted assurance sentence unpinned** [`tests/test_release_note.py:105-315`]. The module *is*
      genuinely code-anchored, not a copy of itself — verified: `-02` imports the live schema constants,
      `-03`/`-04` fold real `evaluate_verdict` results and the live `exit_code_for_verdict` map, `-05` renders
      through the real `render_ship_readiness`, `-14` imports every API name. But `CHANGELOG.md:153-181`
      publishes the row-2 and row-4 `final-verdict.md` callouts (**including the `CAUTION`→`WARNING` level**,
      the sharpest grep-facing claim in the note) and the row-4 negative-assurance sentence, and **no test
      renders either surface**. `render_final_verdict_report` or `_assurance_statement` can be reworded and
      the note rots silently — which is AC9's stated failure mode, and R1 is an instance of drift this check
      structurally cannot see. **Fix:** add folds that render `render_final_verdict_report` for rows 1-4 and
      `_assurance_statement` for rows 1 and 4, and assert the note carries the live callout text **and**
      level, and the live assurance sentence.
- [x] [Review][Patch] **R4 (Low) — `TC-ArgusAgent-DOCS-001-02` cannot detect a schema *downgrade***
      [`tests/test_release_note.py:128-132`]. `any(f'`"{live}"`' in row for row in rows)` scans the **whole**
      table row, which also contains the *Before* cell `` `"1"` ``. If a constant were reverted to `"1"` the
      assertion would still pass off the Before column, so the check is one-directional. **Fix:** split the
      row on `|` and assert the **After** cell specifically (`cells[2] == f'`"{live}"`'), the way `-03`
      already locates its cells.

---

> **Code review iteration 2 — 2026-08-06.** Full re-review (not a fix-round spot check), three parallel
> adversarial layers, every figure re-derived in place on this tree.
>
> **R1–R4 are all independently CONFIRMED FIXED, and the fixes have teeth.** HEAD's fold and HEAD's
> `_assurance_statement` were extracted and **executed** over a row-4-shaped run (3/10 deep, 0 findings):
> HEAD really does persist `Blocking findings were detected within the assessed scope (…)`, which is exactly
> what `CHANGELOG.md:203` now publishes — **R1's correction is right**. Re-introducing R1's false "before"
> goes RED on `-16`. `-15`/`-16` compare `(level, message)` per row by equality; flipping the published
> row-4 level `WARNING`→`CAUTION`, rewording either callout, or rewording either assurance sentence each go
> RED — **R3's accepted version is not the toothless first draft**. `-02` reads the After cell via `_cells()`
> and catches a downgrade the old `any(... in row)` scan accepted — **R4 fixed**. **R2** fixed: `--budget`
> is `default=0` = no ceiling (`argus/cli.py:101-111`), the record names the `--budget 200` invocation and
> withdraws the inference.
>
> **Independently confirmed clean and needing no rework:** every "before" string in `CHANGELOG.md` was
> re-derived by *executing* HEAD's producers (`negative_assurance`, `generator`, `plain_english`,
> `verdict_gate`) over six shapes — **all reproduce byte-for-byte**, and a full four-row report diff
> HEAD↔live shows only the row-4 headline, the row-4 `Final Verdict` line, the `CAUTION`→`WARNING` callout
> and one blank line, i.e. **no undisclosed changed string**. All 9 API names import. v1 verdict payload:
> 10 keys, validates under `extra="forbid"`, `decision_row is None`, `canonical.dumps` round-trip
> byte-identical. FR16 ratio boundaries re-folded live at exactly `1/5`, exactly `3/5`, `0/0` and `0/10` —
> the note's table is correct at every one. `_summary_line` diff HEAD↔live is **empty** (frozen wire
> contract intact). AC12 fences hold: `argus/pipeline.py` md5 `399d6da1d36d668352fd7b0d539cc307` @ **1199**
> lines, `argus/detectors/vacuous_test.py` md5 `8a0705030391df92ad1404af9d044758`, `__version__` /
> `__status__` / `__all__` byte-identical to HEAD, `pyproject.toml` unmodified, dogfood artifacts absent
> from `git status`. Ledger is a pure append (`@@ -492,3 +492,253 @@`, **0 removed**). **Reviewer's own
> suite: 1147 collected / 1144 passed / 3 failed / 0 skipped** — exactly the three adjudicated carve-out
> reds, **no fourth red**; `mypy` clean over 69 source files. All 13 ACs assessed **MET**.
>
> **The findings below are not AC failures.** They are places where the rot check — the artifact whose whole
> job is to stop this note going stale — can be defeated, plus four accuracy gaps in the note itself. They
> matter because AC9's stated failure mode is *"the note rots silently"*, and each item below is a live
> route to exactly that.

- [x] [Review][Patch] **D1 (Med) — RULED 2026-08-06: fix (a) + (c) — split the handler AND harden stderr.**
      The human-register loop gets its own guard: `ShipReadinessError` stays on the AR10 exit-`1` path (AC11
      preserved, `TC-ArgusAgent-CLI-001-33` must stay green), any other `ValueError` from rendering emits a
      degraded note and returns `verdict.exit_code`; plus `sys.stderr.reconfigure(errors="backslashreplace")`
      at the top of `main()` so prose can never be the thing that fails. `CHANGELOG.md:33,74` then stay TRUE
      as written and need no amendment. **Original finding below.**
      **exit `1` says "audit failed" for an audit that SUCCEEDED, and the note
      published in the same commit says exit `1` means no verdict existed** [`argus/cli.py:278-301`,
      `CHANGELOG.md:33,74`]. Found independently by all three layers. **Reproduced first-hand with no
      monkeypatching**: a clean two-file repo that genuinely audits `RELEASE_READY` / exit `0`, run with a
      `cp437` stderr (Windows console code pages 437/850, `PYTHONIOENCODING=ascii`, POSIX `LC_ALL=C`),
      returns **`1`** with `argus: audit failed: 'charmap' codec can't encode character '—'` — while
      **stdout already holds** `verdict=RELEASE_READY deep_ratio=1/2 blocking_findings=0 …`. Every
      ship-readiness headline carries an em dash (`plain_english.py:166,172,177,188`), and
      `UnicodeEncodeError` **is a `ValueError` subclass**, so the widened guard swallows it and labels a
      completed, persisted, verdict-bearing run a failure. `CHANGELOG.md:33` (*"`1` remains the reserved
      code for a typed failure that produced no verdict at all"*) and `:74` (*"degrades the run before a
      verdict exists"*) are both falsified by the shipped behaviour, in the same commit — the precise
      defect class Epic 8 exists to delete. **Not an exit-code regression:** verified that at HEAD the
      render sat outside the guard, so the same input raised an uncaught traceback and the process still
      exited `1`. What this story changed is a visible crash into a **false statement**. **The fix is
      genuinely ambiguous, hence a decision:** (a) give the human-register loop its own handler that emits
      a degraded note and returns `verdict.exit_code`, keeping `ShipReadinessError` on the exit-`1` path —
      this preserves AC11 but requires distinguishing a *contract violation* from a *cosmetic render
      failure*; (b) leave the code and amend `CHANGELOG.md:33,74` to state that exit `1` may follow an
      already-emitted summary line; (c) additionally `sys.stderr.reconfigure(errors="backslashreplace")` so
      prose can never be the thing that fails. Note AC11 binds only *"on any non-raising path"*, so all
      three options are AC-compliant.
- [x] [Review][Patch] **P1 (Med) — the ship-readiness headline pins are defeatable in BOTH directions; the
      note's flagship string is not actually pinned by the rot check**
      [`tests/test_release_note.py:348,373-374`]. Two holes, one fix. (i) `-05` is
      `assert headline in note` — a **whole-document substring**; reverting `plain_english._headline`'s
      row-4 wording to the pre-amendment text left **all 19 rot-check tests green**, because the note
      publishes that exact text at `CHANGELOG.md:152` as `- Row 4, before:`. A straight revert of the
      amendment's headline string is invisible to the module written to catch it. (ii) `-06`'s guard is
      `assert "before" in context` over a lowercased **two-line window** — and the note contains the word
      "before" on seven non-marker lines. **Verified by me directly**: inserting the pre-amendment row-4
      headline as a *current* claim immediately under `CHANGELOG.md:214`
      (`**Byte-identical to before — these did *not* change:**`, an **unchanged-list header**) leaves `-06`
      **passing**, because that header supplies the word. So the one test whose stated job is *"replaced
      wording appears ONLY as history"* accepts a note asserting the replaced wording as current — the
      exact AC4/AC9 reconciliation the dev recorded as Completion Note 1. **Fix:** parse the note's
      `- Row N, after:` / `- Row N, before:` markers into a `{row: headline}` map and compare per row with
      `==` (the module already does this correctly in `_PUBLISHED_CALLOUT` / `_PUBLISHED_ASSURANCE`), and
      anchor `-06`'s context on `^\s*-?\s*Row \d+,\s*before:` rather than a bare substring.
- [x] [Review][Patch] **P2 (Med) — the `1/5` coverage floor is published six times and pinned by nothing**
      [`CHANGELOG.md:39,41,61,136,239,241`]. Patching every binding of `INSUFFICIENT_COVERAGE_FLOOR`
      (`verdict_gate.py:188` **and** `cost/exhaustion.py:97` — both must be patched; a single-module patch
      is a no-op because consumers use `from … import`) from `1/5` to `1/4` leaves the **entire rot check
      green**, while the note's binding FR16 decision table keeps publishing `< 1/5`. It only goes red at
      values extreme enough to move `_ROW_SHAPES`' `(1,10)`/`(3,10)` folds into a different row — i.e. the
      constant is covered by accident, never by name. It appears in no rendered string, so nothing else
      covers it. Symmetrically, republishing the floor as `1/3` in the note also passes. **Fix:** assert the
      published literal directly at each site — `assert f"`{INSUFFICIENT_COVERAGE_FLOOR}`" in note` — the
      way `-02` already pins the schema constants. Same treatment for `3/5`, which *is* currently covered
      but only via `-15`'s rendered text.
- [x] [Review][Patch] **P3 (Med) — the content-address warning enumerates two artifact classes; a real run
      persists seven, and five keep their `"1"` stamp** [`CHANGELOG.md:118-122`]. The note says *"Every
      critical-subsystem artifact is affected; a verdict artifact is affected once it is re-derived under
      `"2"`"*. **Verified on a live run**: seven artifacts persist, **two** at `schema_version=2` and
      **five** at `"1"` — including `argus.verdict.negative_assurance`, whose payload carries
      `assurance_statement`, **which this very note documents as changed for row 4**. Its filename is its
      own payload hash, so a row-4 run moves that file too — **with no schema signal at all**. That is the
      most dangerous case for the path-pinning consumer AC2 is written to protect, and it is the one the
      enumeration omits. **Fix:** add the negative-assurance artifact to that paragraph, stating explicitly
      that its stamp stays `"1"` while its bytes move.
- [x] [Review][Patch] **P4 (Med) — row 4 renders three distinct `final-verdict.md` callouts; the note
      publishes one, and `-15` structurally FORBIDS publishing the other two**
      [`CHANGELOG.md:155,162,169-170`; `tests/test_release_note.py:97-101,174-183`].
      `generator.py:420-441` builds row 4's callout by `"; ".join(reasons)` over two independent gates, so
      three shapes exist: coverage-only (published + pinned), critical-only (present at `:169-170` as
      **wrapped prose**, never as a `- Row 4 …:` line, therefore **never compared**), and **both gates
      unmet — absent entirely**. `_ROW_SHAPES` contains exactly one row-4 fold, `(3,10,0)`, and never
      passes `critical_subsystems_all_deep=False`, so `-15` can only ever pin the first; and
      `_published_callouts` asserts `f"row {match['row']} published twice"`, verified to fail on a second
      `- Row 4` line. So `CHANGELOG.md:155`'s claim — *"Every row's current callout is published here
      verbatim … so it can be diffed against a real run"* — is **false for two of row 4's three shapes**,
      and a reword of the critical clause or of the `; ` join rots the note with nothing failing.
      **Fix:** key `_published_callouts` / `_live_cases` on `(row, variant)`
      (`- Row 4 (coverage) after:` / `(critical)` / `(both)`), add the two folds with
      `critical_subsystems_all_deep=False`, publish all three verbatim.
- [x] [Review][Patch] **P5 (Low) — `-08` asserts none of the three properties its name and docstring claim**
      [`tests/test_release_note.py:488-499`]. Named `note_needs_no_network_llm_or_argus_write`, docstring
      *"nothing in this module dispatches, writes, or reaches a network"* — the body asserts only that the
      **note** contains no absolute host path. The property does hold (the folds are pure), but an
      unsupported claim inside the module whose thesis is that unsupported claims are the defect is worth
      closing. **Fix:** rename to `note_publishes_no_absolute_host_path`, or add the missing assertion
      (monkeypatch `socket.socket` / the store writer to raise for the test's duration).
- [x] [Review][Patch] **P6 (Low) — the package front door over-claims that the note is pinned to the code**
      [`argus/__init__.py`, "Consumer contract" section]. It tells every reader the note *"is pinned against
      the shipped code by a test; nothing here restates it, so there is no second copy to go stale."* Given
      P1–P4 the pin covers rendered strings and schema constants but **not** the floor, **not** the prose,
      **not** two of row 4's three callouts and **not** the exit-code semantics. **Fix:** close the gaps, or
      soften to name what is actually pinned (*"its rendered strings, schema versions and decision table are
      pinned by `tests/test_release_note.py`"*).
- [x] [Review][Patch] **P7 (Low) — the row-derivation recipe tells consumers to read a field that does not
      exist under `--coverage-scope repository`** [`CHANGELOG.md:239-241`]. The recipe keys on *"assessed
      ratio"*, but `_summary_line` appends `assessed_deep_ratio`/`scope`/`held_out` **only when
      `scope is not None`** (`argus/cli.py:219-224`) — i.e. only when the assessment was narrowed. A
      `--coverage-scope repository` run prints `verdict=… deep_ratio=… blocking_findings=…` and nothing
      else, so the AC5 mitigation of the LOCKED decision's *accepted residual risk* is unimplementable as
      written for exactly the consumers AC3 tells to pass that flag. **Fix:** state which field to read when
      the scope suffix is absent (`deep_ratio` is then the assessed ratio).
- [x] [Review][Patch] **P8 (Low) — three parsing/coverage defects in the rot check**
      [`tests/test_release_note.py:59-61,324-337,597`]. (i) `-04` accepts any line containing both a verdict
      token and a code **anywhere**, so it can satisfy a pair off two different columns of the historical
      table (`CHANGELOG.md:41` carries `` `NOT_READY_FOR_RELEASE` / `2` `` and
      `` `INSUFFICIENT_COVERAGE` / `3` `` on one line); harmless only because `-03` pins the same map
      column-anchored. (ii) `-12`'s parametrize is
      `["argus-agent", "argus/", "argus-agent", "repo-audit"]` — `"argus-agent"` twice, the `argus` console
      script **never checked**, while the docstring claims *"the three console scripts"*. (iii) `_cells()`
      splits on a bare `|`, so a cell containing an escaped `\|` mis-columns: probed directly,
      `` | `X` | `"1"` | `"2" \| null` | `mod.py` | `` yields **5** cells with index 2 = `` `"2" \ ``. The
      note already uses escaped pipes (`CHANGELOG.md:256`, `` `DecisionRow \| None` ``); not triggered today
      because no such row carries a pinned value, but `-02`/`-03` index by position and would silently read
      the wrong column if the API table grew one. **Fix:** scope `-04` to the FR16 table as `-03` does;
      derive `-12`'s params from `-13`'s `scripts` list (or delete `-12`, a strictly weaker `-13`); split on
      `(?<!\\)\|` and assert the expected column count before indexing.
- [x] [Review][Patch] **P9 (Low) — "The four sections below" — there are six** [`CHANGELOG.md:27`]. Sections
      after `## Unreleased`: Behaviour, Artifacts, Defaults, Output, Unchanged on purpose, API — then the
      "Do I need to change anything?" summary. A miscount in the document whose thesis is precision.
      **Fix:** say "six", or drop the count.
- [x] [Review][Defer] **W1 (Low) — the rot check pins no prose; whole integrator-facing sections can be
      deleted silently** [`tests/test_release_note.py`, module-wide] — deferred, beyond AC9's enumerated
      scope. Note-side mutations all **MISSED**: deleting the entire "Do I need to change anything?" section;
      deleting the entire "Defaults: `--coverage-scope`" section (the only warning that a pipeline must now
      pass `--coverage-scope repository`); deleting the content-address "your pinned artifact path moved"
      warning; deleting *"If you call `render_ship_readiness()` directly, it can now raise."*; and
      corrupting the published before/after artifact-bytes example. Every **consumer-action** claim in the
      note is unpinned. AC9 enumerates what must be pinned and does not include prose sections, so this is
      hardening rather than a breach — but it is the largest remaining route to silent rot.
- [x] [Review][Defer] **W2 (Low) — the `### Critical subsystems below `audited_deep`` body text changed
      materially and is summarised, not quoted** [`CHANGELOG.md:180-182`] — deferred, AC4's "at minimum"
      list is satisfied. HEAD emitted, on every row, `These withheld `RELEASE_READY` (FR16). Each must reach
      `audited_deep`, …`; live emits a row-dependent lead (row 2: *"Not the reason for this verdict — that
      is stated in the callout above…"*) **plus a wholly new FR4/DR-5 exemption paragraph on every row**. A
      grep-facing consumer gets no quotable before/after for a paragraph that changed on every affected run.
- [x] [Review][Defer] **W3 (Low) — the widened `except ValueError` is broader than the comment beside it**
      [`argus/cli.py:295-299`] — deferred, pre-existing. The comment enumerates five typed subclasses; the
      clause catches base `ValueError`, so pydantic's `ValidationError` reports as an expected typed
      degradation rather than surfacing as the internal bug it is. Pre-existing around `run_audit`; the
      widening adds only the two `print` calls, so the *new* swallow surface is `ShipReadinessError` plus
      stream errors (see **D1**). Latent, not introduced here.

**Resolved — fix round 3 (reviewer-applied), 2026-08-06. All 10 patches applied; 3 defers filed.**

Suite **1150 collected / 1147 passed / 3 failed / 0 skipped** (progress-map census: 1147 `.`, exactly 3
`F`, zero `s`, zero `E`) — the same three adjudicated carve-out reds, **no fourth red**. `mypy` clean over
69 source files. The **+3** over the previous 1147/1144 is entirely this round's: `tests/test_release_note.py`
19 → **21** (`-17`, `-18`), `tests/test_cli.py` 12 → **13** (`-34`). Fences re-verified **byte-identical**:
`argus/pipeline.py` md5 `399d6da1d36d668352fd7b0d539cc307` @ 1199 lines, `argus/detectors/vacuous_test.py`
md5 `8a0705030391df92ad1404af9d044758`; `git diff HEAD -- argus/__init__.py` contains **no `+`/`-` line
touching `__version__` / `__status__` / `__all__`**. `argus/cli.py` 307 → **329** lines, `argus/__init__.py`
59 → **66** — both far inside NFR-M1. No Story-8.5 artifact and no foreign Epic-9 file was opened for
writing.

**RED-first, every new and every changed pin** (note mutated in memory via `_note()`, constants patched at
every binding; **nothing written to disk**):

```
P1a  -05  reverted row-4 live headline                    -> RED
P1b  -06  stale wording asserted as CURRENT               -> RED
P2   -17  floor 1/5 -> 1/4, note untouched                -> RED
P4   -15  row 4 (coverage) unpublished                    -> RED
P4   -15  row 4 (critical) unpublished                    -> RED
P4   -15  row 4 (both)     unpublished                    -> RED
P8   -04  NOT_READY_FOR_RELEASE mapped to exit 3          -> RED
control   the real note, all five tests                   -> GREEN
```

**D1** — the handler is split. `run_audit` + the stdout wire line keep the original
`except ValueError → exit 1` (a failure there means no verdict reached the consumer, so exit `1` is
honest). The human register is guarded separately: `ShipReadinessError` still degrades to exit `1` (AC11
intact, `-33` green), any other `ValueError` prints `ship-readiness not rendered:` and **leaves
`verdict.exit_code` standing**. Both streams also get `reconfigure(errors="backslashreplace")`, so prose
can never be the thing that fails a run. Verified end-to-end on a real repo with a real `cp437` stderr:
**before** the fix `main()` returned `1` / `argus: audit failed` for a repository that genuinely audits
`RELEASE_READY`; **after**, it returns **`0`** with the em dash degraded to `—` and the headline
intact. Pinned by `TC-ArgusAgent-CLI-001-34`. `CHANGELOG.md:33,74` therefore stay true as written and were
**not** amended — the code was brought up to the published contract rather than the contract down to the
code.

**P1** — the note now publishes each row's current ship-readiness headline as
`- Headline row N (after|unchanged): …`, and `-05` compares **per row by equality** instead of searching the
whole document; `-06` anchors on a `before:` **label** instead of the bare word "before" in a two-line
window. **P2** — `-17` imports `INSUFFICIENT_COVERAGE_FLOOR` / `RELEASE_READY_DEEP_THRESHOLD` and asserts
the published literals, plus their presence in the binding FR16 table. **P3** — the content-address section
now states that a run persists more artifacts than the two that were bumped, that the negative-assurance
artifact moves on any row-4 run, and that it **keeps its `"1"` stamp**: *a stamp that did not change is not
a promise that the bytes did not*. **P4** — all three row-4 callouts are published as
`- Row 4 (coverage|critical|both) after:` and `-15` keys on `(row, variant)` against three real folds.
**P5** — `-08` renamed to what it asserts; the NFR-D2 claim it used to make is now **proven** by `-18`,
which runs the live folds with `socket.socket`, `socket.create_connection`, `ApaaStoreWriter.write_envelope`
and `.write_payload` all replaced by detonators. **P6** — the front door now names *which* surfaces are
pinned rather than claiming the note as a whole is. **P7** — the derivation recipe says to read
`assessed_deep_ratio=` when present and `deep_ratio=` when it is not (the fields are appended only when the
assessment was narrowed). **P8** — `_cells()` splits on `(?<!\\)\|` and a new `_cell(..., expected=N)`
fails loudly on a reshaped table; `-04` reads verdict and exit from their own columns inside the FR16 table;
`-12`'s duplicated param is gone and its docstring now says why the bare `argus` script is `-13`'s job, not
its own. **P9** — "four sections" corrected.

One documentation fork was closed while doing this: rows 1-3's headlines were being stated twice (once as
current, once in the byte-identical list). They are now stated once and pointed at, matching how the
callouts and assurance sentences already worked (§3.3 / AR7 applied to documentation).

---

## Dev Notes

### LOCKED decisions taken at story design — with rationale (record these; do not re-litigate)

**D1 — The release note is `CHANGELOG.md` at the repository root.** Considered and rejected:
`docs/` (its own README declares it the BMad `project_knowledge` root for generated docs — a hand-authored
consumer contract does not belong there); `_bmad-output/design-artifacts/ArgusAgent/` (planning artifacts, an
integrator will never look there, and the epic AC says *"an integrator reads the release note"*); the PRD
addendum (already states the migration and is *not published to consumers* — that is literally DR-8's
"Current state: the addendum states it; no release note is published"); `README.md` alone (a changelog inside
a feature README goes stale and buries the contract). A root `CHANGELOG.md` is the universal convention, is
picked up by `flit` in the sdist, and is where every integrator looks first.

**D2 — The note is headed UNRELEASED, and says so out loud.** `pyproject.toml` declares `version = "0.1.0"`,
but `argus-agent` is **on no index and has no release workflow** (assumption A1, falsified 2026-08-03; IN-0
is Story **9.2**'s). Heading a section `## 0.1.0 — 2026-08-06` would make this very note a **published Argus
artifact asserting something untrue** — the exact defect class Epic 8 exists to delete, committed in the
document written to close Epic 8. So: head it `## Unreleased`, and carry a one-line preamble stating that
`0.1.0` is declared but not tagged or published, that "unreleased" means *on the default branch of
Agent-Argus*, and that packaging/distribution is tracked separately. **Do not name Story 9.2, do not promise
a date, do not create anything.** AC9 pins this honesty so a later edit cannot quietly turn it into a
release claim.

**D3 — RS-4a is the FILE `argus/__init__.py`, not only line 37.** The requirement's own words are *"fix the
package front door"*, and the front door is one file whose docstring a reader meets before any code. Fixing
line 37 while leaving `RESERVED PACKAGE SHELL — no business logic yet` and `reuses proven Minions
infrastructure via direct import` standing (the latter now falsified outright by Epic 9's Story 9.1) would
leave the front door *still lying*, in a story whose entire purpose is that no Argus artifact contradicts the
shipped contract. RS-4b's own text scopes it to *"the **remaining** ~48 stale references in `argus/`
docstrings and comments"* — i.e. the **other** files. Measured boundary: **1 reference here (RS-4a) / 15 in 8
other files (RS-4b)**. Best practice would keep a documentation story to its single named line; the project
standard (*"no published Argus artifact contradicting the shipped contract"*, and §3.4's rule that a
persisted artifact must not assert a falsehood) wins, and it is recorded here.

**D4 — Proposed shape for `CHANGELOG.md` (a starting point, not a straitjacket).** Ordered by what breaks a
pipeline soonest:

```
# Changelog                       ← + Keep-a-Changelog pointer, + the D2 honesty preamble
## Unreleased
### Behaviour: exit codes         ← AC1 (4-row table, the one moved case, the 3 reassurances)
### Artifacts: schema versions    ← AC2 (both bumps, both compat behaviours, content-address consequence)
### Defaults: --coverage-scope    ← AC3 (predates this delta; say so)
### Output: changed strings       ← AC4 (changed list + byte-identical list)
### Unchanged on purpose          ← AC5 (stdout line, enum, exit values, row-derivation rule)
### API (library consumers)       ← AC6 (ShipReadinessError flagged behavioural)
### Do I need to change anything? ← a 4-line decision list; this is what an integrator actually reads
```

The last section is the story's user value in one place: *branch only on `0` vs non-zero → **no change***;
*distinguish `2` from `3` → **no change**, you now get the right one*; *validate `schema_version` → **update
your expected value(s)***; *string-match reports or pin `.argus/` paths → **re-check, see above***.

**D5 — DF-8-3-B is pulled in; the reasoning is recorded so it is not re-litigated.** Its ledger
`target_story` is `8-4` (named first, unconditionally) *or* the first story that edits `argus/cli.py` — and
Epic 8 has one story left after this (8.5, dogfood artifacts) while Epic 9's remaining story is packaging, so
"the first story that edits `cli.py`" plausibly never fires inside this delta and the item rots. It is ~5
lines plus one test in a 298-line file with ample NFR-M1 headroom, it is fenced by no other DF, and it is
**in this story's domain**: AC1/AC5 publish the AR3/AR10 exit-code contract including *typed failure → exit
`1`*, and today the default `argus audit <path>` invocation does not honour it. Publishing a contract the
default path does not keep would be an over-claim in the document written to stop over-claims. It is kept
independently testable as its own AC and task so a reviewer can assess it separately.

**D6 — DF-8-2-A, DF-8-2-B, DF-8-3-A, DF-8-3-C are all CARRIED FORWARD, not closed.**
- **DF-8-2-A** (`pipeline.py` at 1199/1200) — `target_story: 8-3 (or the first story after 8.2 that edits
  argus/pipeline.py)`. This story needs nothing from `pipeline.py`; **AC12 fences it**, so the cap cannot be
  breached and the extraction stays queued for the next story that genuinely edits it.
- **DF-8-2-B** (`_UNAMBIGUOUS_TEST_SUFFIXES` missing separators) — `target_story: 8-3 (or the first story
  that edits argus/detectors/vacuous_test.py)`. Conditional; the condition does not fire (fenced). Still
  zero live instances in this repository.
- **DF-8-3-A** (no surface names a *vacuously* satisfied critical clause) — `target_story: the story that
  performs the DF-8-2-A pipeline.py extraction`. Not this story; it needs a new `generate_reports` argument
  threaded from `pipeline.py:793`, i.e. exactly the fenced edit.
- **DF-8-3-C** (the ast-index → application/test partition written twice) — same `target_story`; its only
  sensible homes are the two fenced files.
Each disposition must be **restated in the Dev Agent Record**, not merely inherited from here.

**D7 — `action.yml` is filed, not fixed.** Its `else → INSUFFICIENT_COVERAGE` swallows exit `1`, publishing a
crashed run as an under-covered one. Real, integrator-visible, and **pre-existing** (exit `1` predates Epic
8). But the file is untracked, foreign, and Epic-9/9.2 territory, and a concurrent session owns it. The
register is exactly the mechanism for *found it, not ours* — hence `DF-8-4-A` in AC10. Do **not** edit it,
and do **not** describe it in `CHANGELOG.md` as though this delta changed it.

**D8 — The note describes the CONTRACT, never this repository's own verdict.** `argus audit .` currently
returns `RELEASE_READY` on ArgusAgent. That result belongs to **Story 8.5 / DR-10**, it carries the hard
`grade: demo-heuristic-only` flag, and it is **not** clearance. AC13 runs it as a consistency check only. Do
not put it in `CHANGELOG.md`, do not cite it as evidence the amendment works.

### Architecture patterns & constraints (non-negotiable — AR/NFR ids a reviewer will check)

- **AR3 wire contract.** Exit codes `0`/`2`/`3`/`1` and the stdout summary-line format are frozen. AC11's
  `try` widening must not move a single byte of stdout or stderr on any non-raising path.
- **AR10 typed failure / NFR-R1.** The error path prints the typed reason only — never source bytes, never
  a secret, never an absolute host path, never a bare traceback. **No `print()` in library code**: `cli.py`
  owns printing; do not add one to `plain_english.py` or `generator.py` (you are not editing them anyway).
- **§3.3 / AR7 no-fork — applied to documentation too.** The exit-code contract, the four-row table and the
  schema values are stated in **one** place (`CHANGELOG.md`). Do not restate them in `README.md`,
  `argus/__init__.py` or a docstring: a second copy is a second thing that can go stale, which is the exact
  failure this story exists to end. `README.md` gets a **link**.
- **NFR-M2 additive-only.** The `schema_version` bump is the sanctioned lever for an intentional
  content-hash change. This story adds, removes and renames **no** field.
- **NFR-P1 / AR4 determinism.** `__version__` is folded into every envelope's content hash — byte-identical
  or every artifact hash in the repo moves. Ratios stay exact `Fraction`; do not compute a percentage
  anywhere, including in the changelog prose (quote `3/5`, `1/5`, `9/10` as the tool prints them).
- **NFR-S1.** Nothing you write may contain source bytes, secret bytes or an absolute host path — including
  the changelog examples. Use repo-relative POSIX paths.
- **NFR-D2 zero-token testability.** Every AC is provable with no LLM, no network and no `.argus/` write.
  AC13's live `argus audit .` is a consistency check, not a proof obligation.
- **NFR-M1** ≤1200 lines. Today: `cli.py` **298** (ample), `__init__.py` **66**, `pipeline.py` **1199**
  ⚠️ (fenced).
- **Contract/Format pattern** — the verdict vocabulary (`RELEASE_READY` / `NOT_READY_FOR_RELEASE`
  (`BLOCKED` = demo shorthand) / `INSUFFICIENT_COVERAGE`) is used **verbatim**. Do not invent a fourth state
  word in the changelog, and do not describe `INSUFFICIENT_COVERAGE` as a failure — the PRD is explicit that
  it is a *not-assessed* state and **not** a blocking verdict.

### Traps a previous story already paid for (Epic 1–8.3 learnings that apply here)

- **Measure IN PLACE, never on a scratch copy.** 8.1's blast radius was taken on a tree with no `.git` and
  no `_bmad-output/`; it misclassified `tests/test_dogfood_proof.py` and cost a review round. 8.2 and 8.3
  measured in place and were exact. **This story's entire content is measurement — get it from `git diff
  HEAD` and from importing the shipped functions, on this tree.**
- **Verify independently; do not trust a prior record.** Every Epic-6/7/8 review re-ran everything itself.
  The tables above are the SM's measurement, not scripture — and a reviewer *will* re-derive the "before"
  strings from `git show HEAD:…`.
- **A re-pointed or re-worded assertion must keep its subject and gain precision** — it never asserts less.
- **RED-first or it does not count.** 8.3's review accepted the DF-8-1-A closure only because the pre-fix
  code was rebuilt and the new test shown failing against it. AC9's rot check gets the same treatment.
- **Do not trade one dead artifact for another.** A changelog nobody can verify is the documentation
  equivalent of the unreachable branch DR-11 deleted. That is why AC9 exists.
- **Run tests as** `PYTHONIOENCODING=utf-8 python -m pytest tests/ -q` — the suite carries non-ASCII
  fixtures and the strings you are quoting are full of em-dashes; Windows `cp1252` stdout will
  `UnicodeEncodeError`. `pytest-timeout` is **not** installed — do not pass `--timeout`. A full run takes
  ≈3.5 minutes.
- **Do not flip the story to `review` before the tests exist** (AI-E2-1, Epic-2 retrospective).
- **The tree is shared.** Re-read `deferred-work.md` and `sprint-status.yaml` immediately before writing
  either, and when you write `sprint-status.yaml` change **only** the `8-4-…` key.

### Runtime, library and toolchain specifics (verified on this machine, 2026-08-06)

`python 3.11.15` · `pydantic 2.13.4` · `pytest 9.1.1` · `mypy 2.3.0` (clean over 69 files) ·
`tree-sitter` pinned `>=0.25,<0.26` (folded into the Epic-5 determinism closure — **do not bump it**, and do
not mention a version bump in the changelog: there isn't one). Interpreter for in-place measurement:
`./.venv/Scripts/python.exe`.

**No new dependency is introduced by this story** — Markdown, one small test module, and ~5 lines of
`cli.py`. **No web research obligation:** this delta touches no external API, no library version and no
network surface; it is documentation over frozen in-repo contracts, and every fact in it is derivable from
this tree. (Keep-a-Changelog is a *format convention*, not a dependency — follow its shape if you like, but
do not add a tool, a linter or a CI job for it; that would be packaging work, and packaging is Epic 9's.)

Python specifics that bite on this exact change:

- `render_ship_readiness(verdict, *, enabled_passes=…)` returns a **tuple of lines**, not a string —
  `[0]` is the headline. `render_final_verdict_report(request, verdict, ledger, total_findings_count, *,
  source_state=None, ast_index=None)` returns the document text.
- `AuditRequest` requires `materiality_bar` (no default) — a measurement script that omits it raises a
  `ValidationError` before it renders anything.
- `AuditVerdict` is `frozen=True, extra="forbid"`. Constructing one **directly** bypasses `evaluate_verdict`
  and leaves `decision_row=None` — legitimate **only** for the AC11 contract-violation pin; every other
  measurement must fold a real `evaluate_verdict`, or it proves nothing about what the tool can produce.
- `Fraction` in an f-string normalises: `Fraction(5, 5)` → `"1"`, `Fraction(3, 10)` → `"3/10"`. A 100 %-deep
  run genuinely prints `**Deep Coverage Ratio**: **`1`**`. Pre-existing, asserted by existing tests, and
  **not** something to "fix" or to quietly correct in the changelog.
- `str`-valued enums serialize to `.value`; `DecisionRow.BLOCKING_FINDINGS` is the wire token
  `"row_2_blocking_findings"`.

### Recent git context

`9109e16` docs(readiness) · `d8ba5ad` docs(prd): FR16/FR4 amendment propagated to epics · `faeefd9`
fix(verdict): stop reporting a block when nothing was found · `ae5f00c` fix(audit): make verdicts honest and
the tool runnable on any repo · `37ca977` feat(verdict): verdict gate for core readiness. The pattern is
**small, single-concern changes with the paper trail landing first** — this story *is* the paper trail.
Stories 8.1, 8.2 and 8.3 are **all uncommitted on top of `9109e16`**; `git stash`, `git checkout --` or a
reset would destroy them.

### Pre-existing observations — NOT this story's bugs, do not fix here

- **`Fraction(5, 5)` renders as `1`** in reports. Ugly, honest, pre-existing, test-asserted. Leave it.
- **`action.yml`'s exit-`1` mislabel** — filed as `DF-8-4-A` (AC10), foreign file, do not edit (**D7**).
- **`tests/test_dogfood_plan.py`'s two reds** — inherited, red at `9109e16`.
- **`tests/test_dogfood_proof.py`'s red** — deliberate, Story 8.5's deliverable.
- **`README.md`'s "Repository Structure" tree and slash-command list** are broader project prose (RAM
  framework, phases, adapters) and are **not** RS-4a/RS-4b targets. Add the one pointer line; change nothing
  else there.

### Project Structure Notes

- **Files this story is expected to create/modify:** `CHANGELOG.md` (**new**, repo root) ·
  `README.md` (one pointer line) · `argus/__init__.py` (docstring only) · `argus/cli.py` (AC11 `try` widen
  only) · `tests/test_release_note.py` (**new**) · `tests/test_cli.py` (add only, AC11) ·
  `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (append only) ·
  `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` (**only** the `8-4-…` key).
- **Files this story must NOT modify:** see **AC12** for the binding list.
- **No new module in `argus/`.** No entry is added to `_MODULES_UNDER_GUARD` (no new `argus/` module
  exists), and `tests/test_no_web_imports.py` is **foreign — do not touch it**.
- **Test tree:** `tests/` at the repo root — *not* the `tests/apaa/` path in older architecture prose, which
  describes the pre-extraction Minions monorepo.
- **Test-id convention:** `TC-ArgusAgent-<AREA>-<SEQ>-<SUBSEQ>`. The CLI area is `TC-ArgusAgent-CLI-001-NN`,
  currently to **-32** (8.3's) — continue at **-33**. The release-note tests introduce a **new** area,
  `TC-ArgusAgent-DOCS-001-NN`, starting at **-01** (verified: no `DOCS` area exists in `tests/`). **Do not
  restart an existing sequence.**
- ⚠️ **The working tree carries Stories 8.1, 8.2 AND 8.3's UNCOMMITTED deltas, and a concurrent session is
  editing Epic 9 surfaces.** Do not stash, checkout or reset.

### Variance from the epic, recorded

The epic's five ACs for Story 8.4 are carried in full (**AC1** ← epic AC1/DR-8; **AC2** ← epic AC2/B8;
**AC3** ← epic AC3; **AC8** ← epic AC4/RS-4a; **AC10** ← epic AC5/RS-4b). The additions were made at story
design **after measuring the delta against the real tree**:

- **AC2 widened to BOTH schema bumps** — *measured*: `CRITICAL_SUBSYSTEMS_SCHEMA_VERSION` also went
  `"1"`→`"2"`, in Story 8.2, **after** the epic text was written. Boundary B8's stated concern is *"a
  consumer-visible change the exit-code framing alone conceals"*. Disclosing one bump while concealing the
  other reproduces that concern inside the very AC raised to prevent it. The unconditional emission of
  `heuristic_excluded_ineligible` makes it strictly more consumer-visible than the verdict bump, not less.
- **AC4 (changed rendered strings)** — *measured*: five distinct persisted/rendered strings changed,
  including a **callout-level** change (`CAUTION`→`WARNING`) and a persisted `.argus/` assurance sentence. An
  integrator who greps `final-verdict.md` or reads the assurance statement is broken by this **with no
  schema signal at all** — the exit-code and schema framings both miss it entirely.
- **AC5 (unchanged machine surfaces + the row-derivation rule)** — the Story 8.1 LOCKED channel decision
  records an *accepted residual risk*: a consumer who needs the row must re-derive it from the unchanged
  stdout line. The release note is the **only** artifact where that derivation can be published, so
  publishing it is what converts an accepted risk into a mitigated one. Stating what did *not* change is
  also the fastest route to the epic's own promise that most pipelines need no change.
- **AC6 (API surface)** — *measured*: `ShipReadinessError` is a **new raise at a site that previously always
  returned prose**. A note framed only around exit codes and schema versions would leave a library consumer
  to discover it from a traceback.
- **AC7 (placement, findability, no-fork)** — the epic AC presupposes "the release note" exists somewhere an
  integrator reads. **There is no changelog in this repository at all**, so placement is a real decision and
  is locked in **D1**/**D2** rather than left to the dev.
- **AC9 (rot check)** — the epic's Epic-8 outcome statement requires *no published Argus artifact
  contradicting the shipped contract*. An unpinned hand-written note is the **next** such artifact by
  construction: it is correct exactly once. The repo already has the pattern
  (`tests/test_dogfood_proof.py`), and using it here is the difference between closing the epic and
  restarting it.
- **AC11 (DF-8-3-B)** — pulled in per its ledger `target_story: 8-4`; justified in **D5**.
- **AC12/AC13** — the standing fence, honest-recording and whole-system obligations every Epic-8 story
  carries.

Scope boundaries are stated in **D2** (no packaging/release work — Epic 9), **D3** (RS-4a = the file, RS-4b
still deferred), **D6** (four DF items carried forward), **D7** (`action.yml` filed, not fixed) and **D8**
(the note documents the contract, not this repo's verdict).

### References

- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Story 8.4: Tell integrators what changed`] (lines 1540–1564) — the five ACs carried above
- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Derived Delta Requirements (DR)`] (lines 1166, 1161–1162) — **DR-8**, and DR-3/DR-4's binding default-field + no-rewrite clauses
- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Repo-Separation Requirements (RS)`] (lines 1200–1201) — **RS-4a** (carried here) and **RS-4b** (deferred, incl. the "not prose only / generated artifacts" scope note this story measured and confirmed)
- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Story 8.1`] (lines 1440–1457) — the **LOCKED channel decision**: artifact = explicit field, **stdout summary line UNCHANGED**, and the accepted residual re-derivation risk AC5 mitigates
- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Story 9.2`] (lines 1653–1678) and `#Epic 9` (1618–1625) — **IN-0**: the release workflow, tag and distribution are **not this story's**
- [Source: `_bmad-output/design-artifacts/ArgusAgent/E-PRD/addendum.md#A1`] — the options matrix (why the enum did not grow), the *"Integrator migration note"* paragraph DR-8 says is unpublished, and the CR-2 `--coverage-scope` paragraph AC3 must carry
- [Source: `_bmad-output/design-artifacts/ArgusAgent/E-PRD/prd.md#Release-Readiness Verdict`] (lines 411–425) — the binding FR16 four-row table, *"`INSUFFICIENT_COVERAGE` … is **not** a blocking verdict"*, *"Nothing becomes a silent pass"*, and FR18 (*"consume the verdict as a deterministic exit code and a machine-readable artifact"*) — the requirement this story serves
- [Source: `_bmad-output/design-artifacts/ArgusAgent/architecture.md#Contract / Format Patterns`] (lines 362–373) — the canonical verdict vocabulary + exit codes `0/2/3/1`, *"downstream artifacts use this vocabulary verbatim"*; **#Error / Degradation Patterns** (388–393) — typed failure, no uncaught raise, no `print()` in library code (AC11); **#Naming & Structure Patterns** (353–360) — ≤1200 lines, `TC-<AREA>-<SEQ>-<SUBSEQ>`
- [Source: `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`] (lines 544–675) — **DF-8-2-A**, **DF-8-2-B**, **DF-8-3-A**, **DF-8-3-C** (all carried) and **DF-8-3-B** (closed here); lines 5–6 — the six mandatory CC-3 fields
- [Source: `_bmad-output/design-artifacts/ArgusAgent/stories/8-1-findings-before-coverage-binding-decision-table.md`] — the four-row fold, `DecisionRow` / `is_below_floor`, the `VERDICT_SCHEMA_VERSION` bump and the v1 round-trip evidence fixture
- [Source: `_bmad-output/design-artifacts/ArgusAgent/stories/8-2-critical-subsystem-gates-operator-can-actually-satisfy.md`] — `CriticalIneligibility`, `heuristic_excluded_ineligible`, the `CRITICAL_SUBSYSTEMS_SCHEMA_VERSION` bump
- [Source: `_bmad-output/design-artifacts/ArgusAgent/stories/8-3-plain-english-report-stops-describing-impossible-state.md`] — `ShipReadinessError`, the four-row headline split, the generator's four arms, and the measurement-method lesson this story reuses
- [Source: `argus/verdict/verdict_gate.py:160-233,320-441,487-668`] — `VERDICT_SCHEMA_VERSION`, `DecisionRow`, `AuditVerdict` (+ `decision_row`, `is_below_floor`, `to_canonical_payload`'s omit rules), `exit_code_for_verdict`, the four-row fold
- [Source: `argus/ledger/critical_subsystems.py:129-146,245`] — `CRITICAL_SUBSYSTEMS_SCHEMA_VERSION`, `CriticalIneligibility`, `heuristic_excluded_ineligible`
- [Source: `argus/reports/plain_english.py:82-206`] — `ShipReadinessError` and the four-row `_headline`
- [Source: `argus/reports/generator.py:322-365`] — the four FR16 arms and the changed callouts; `git show HEAD:argus/reports/generator.py` (`:304-338`) for the pre-amendment block
- [Source: `argus/verdict/negative_assurance.py:287-333`] — the row-1/row-4 persisted assurance-statement split (AC4)
- [Source: `argus/cost/exhaustion.py:402-497`] — `below_floor` re-keyed onto `is_below_floor` (a consumer of the new property)
- [Source: `argus/cli.py:180-190,199-224,227-298`] — the `--coverage-scope` default (**already `application` at HEAD**), the frozen `_summary_line`, and the `try/except ValueError` at `:270-277` vs the unguarded `render_ship_readiness` at `:292` (**AC11 / DF-8-3-B**)
- [Source: `argus/__init__.py:1-66`] — the front door (**AC8**); `__version__` at `:59` is the envelope's `argus_version` and must not move
- [Source: `pyproject.toml:5-14,33-61`] — `name = "argus-agent"`, `version = "0.1.0"`, the real extras (`dev`/`llm`/`languages`) and the three console scripts — the facts that replace `__init__.py`'s `minions[argus]` claim
- [Source: `tests/fixtures/verdict_schema_v1_row2_artifacts.json`] — the committed **v1** payload shapes quoted in *Story Context* B (**evidence, not a golden**)
- [Source: `tests/test_dogfood_proof.py:1-60`] — the committed-artifact rot-check pattern AC9 follows, and `_REPO_ROOT = Path(__file__).resolve().parents[1]`

---

## Dev Agent Record

### Context Reference

Story file (this document), fully contexted. `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`
(DF-8-3-B closed, RS-4b + DF-8-4-A filed). No other planning artifact was modified.

### Agent Model Used

claude-opus-5[1m] (Opus 5, 1M context)

### Debug Log References

**Measurement method — IN PLACE, on the real working tree.** Everything below was produced on this
repository itself: HEAD `9109e16b4e86436a8315ed2cb967b75cdced4296` **plus 8.1's, 8.2's and 8.3's
uncommitted deltas**, `.git` and `_bmad-output/` present. Not a scratch copy. Interpreter
`./.venv/Scripts/python.exe` (python 3.11 venv). Two instruments, exactly as the story prescribes:

1. `git show HEAD:<file>` for every **before** string (`argus/reports/plain_english.py`,
   `argus/reports/generator.py`, `argus/verdict/verdict_gate.py`, `argus/ledger/critical_subsystems.py`,
   `argus/verdict/negative_assurance.py`, `argus/cli.py`). No "before" string in `CHANGELOG.md` was copied
   from this story on trust.
2. Importing the shipped `argus` functions and calling them in place — real `evaluate_verdict(...)` folds
   over real `CoverageLedger` inputs, rendered through the real `render_ship_readiness` and the real
   `render_final_verdict_report`.

The foreign Epic-9 files (`argus/audit/minions_llm_adapter.py`, `tests/test_no_web_imports.py`,
`action.yml`, `.github/workflows/argus-student-audit.yml`, `stories/9-1-*.md`) were **excluded from every
figure** and were not read, modified, or built upon.

**Re-derived facts (all confirmed; the story's tables held, with one refinement noted below).**

- Exit map, imported `exit_code_for_verdict` over the whole `Verdict` enum:
  `RELEASE_READY→0 · NOT_READY_FOR_RELEASE→2 · INSUFFICIENT_COVERAGE→3`. Unchanged as a mapping.
- Pre-amendment fold (`git show HEAD:argus/verdict/verdict_gate.py:511-520`) had **three** branches:
  floor → `INSUFFICIENT_COVERAGE`; `ratio >= 3/5 AND blocking == 0 AND critical_all_deep` →
  `RELEASE_READY`; **else → `NOT_READY_FOR_RELEASE`**. Post-amendment has four. Confirms **exactly one run
  class moved**: 0 blocking findings + an unmet gate, at or above the floor, `2` → `3`.
- `VERDICT_SCHEMA_VERSION`: HEAD `:149` = `"1"` → now `:182` = `"2"`.
  `CRITICAL_SUBSYSTEMS_SCHEMA_VERSION`: HEAD `:106` = `"1"` → now `:146` = `"2"`. **Both confirmed.**
- `DecisionRow` members: `row_1_below_floor`, `row_2_blocking_findings`, `row_3_gates_met`,
  `row_4_gate_unmet_no_findings`.
- Verdict payload keys (live row-2 fold): `blocking_finding_count · counts_by_depth ·
  critical_subsystems_all_deep · decision_row · deep_count · deep_ratio · exit_code · ordered_findings ·
  schema_version · total_count · verdict`. `decision_row` is the added key.
- **v1 round-trip verified, not assumed.** The committed fixture's verdict envelope
  (`state/734b989b841fc4fb0efa658102c4b77b34e208f05aaf7b7c276cff076d5649ca.json`) validates under
  `extra="forbid"`; `decision_row` is `None`; `to_canonical_payload()` returns the **same ten keys** and
  `canonical.dumps(round_trip) == canonical.dumps(original)` → **True**. `is_below_floor` fell back to the
  enum correctly.
- Critical-subsystem payload, before (from the fixture):
  `{"designated_but_unmatched":[],"origins":{},"paths":[],"schema_version":"1"}`; after (live empty set):
  `{"designated_but_unmatched":[],"heuristic_excluded_ineligible":{},"origins":{},"paths":[],"schema_version":"2"}`
  — i.e. **emitted unconditionally**, so every such artifact changes bytes and therefore filename.
- All four live ship-readiness headlines and all five live `final-verdict.md` callouts rendered and
  compared against the `-` side of `git show HEAD:…`. Every row in the story's tables reproduced exactly.
- Every AC6 name resolved from the shipped tree. `ShipReadinessError` raise reproduced in place:
  `NOT_READY_FOR_RELEASE with blocking_finding_count=0: FR16 row 2 is the only producer of this verdict and
  it requires at least one verdict-eligible finding`; `isinstance(exc, ValueError)` → `True`.
- `--coverage-scope` default: `git show HEAD:argus/cli.py:184` already reads `default="application"` —
  **byte-identical to the current file**. The flip genuinely predates this delta, and `CHANGELOG.md` says
  so rather than implying otherwise.

**AC9 RED-first — verbatim.** A deliberately-stale `CHANGELOG.md` was installed (four independent rot
modes: heading turned into `## 0.1.0 - 2026-08-06`; `VERDICT_SCHEMA_VERSION`'s "after" value reverted to
`"1"`; the row-4 entry dropped from the decision table; the row-4 headline reverted to the pre-amendment
`a coverage gate was not met` wording). `PYTHONIOENCODING=utf-8 python -m pytest tests/test_release_note.py -q`
→ **6 failed**:

```
FAILED tests/test_release_note.py::test_TC_ArgusAgent_DOCS_001_01_note_exists_and_is_headed_unreleased
E   AssertionError: the note must carry an `## Unreleased` heading (D2)
FAILED tests/test_release_note.py::test_TC_ArgusAgent_DOCS_001_02_note_carries_both_live_schema_versions
E   AssertionError: VERDICT_SCHEMA_VERSION is live at '2', but no note row for it says so:
    ['| `VERDICT_SCHEMA_VERSION` | `"1"` | `"1"` | `argus/verdict/verdict_gate.py` |']
FAILED tests/test_release_note.py::test_TC_ArgusAgent_DOCS_001_03_note_reproduces_the_live_decision_table
E   AssertionError: the note's decision table must carry EVERY DecisionRow member exactly once;
    missing ['row_4_gate_unmet_no_findings']
FAILED tests/test_release_note.py::test_TC_ArgusAgent_DOCS_001_05_note_quotes_the_four_live_headlines
E   AssertionError: row_4_gate_unmet_no_findings's live headline is absent from the note:
    'NOT VOUCHED — nothing broken was found, but a coverage or critical-subsystem gate was not met, so no
     release-readiness claim is made. This is a statement about the audit, not about the code.'
FAILED tests/test_release_note.py::test_TC_ArgusAgent_DOCS_001_06_note_states_the_stale_wording_only_as_history
E   AssertionError: the pre-amendment wording 'but a coverage gate was not met' appears outside a
    'before' context, i.e. as though it were current
FAILED tests/test_release_note.py::test_TC_ArgusAgent_DOCS_001_07_note_makes_no_published_distribution_claim
E   AssertionError: the note must not head a released version section: ['## 0.1.0 - 2026-08-06']
```

Against the real note: **17 passed** (the module was later extended to 17 tests; all green). (A 7th failure in the first RED pass, `-08`, was a false positive —
its absolute-path regex matched the `https:` in a URL. The regex was anchored to a token boundary and
re-run; it is a genuine NFR-S1 assertion, not a weakened one.)

**AC11 RED-first — verbatim.** `TC-ArgusAgent-CLI-001-33` run against the **pre-fix** `argus/cli.py`:

```
argus\reports\plain_english.py:182: ShipReadinessError
E   argus.reports.plain_english.ShipReadinessError: NOT_READY_FOR_RELEASE with blocking_finding_count=0:
    FR16 row 2 is the only producer of this verdict and it requires at least one verdict-eligible finding
---------------------------- Captured stdout call -----------------------------
verdict=NOT_READY_FOR_RELEASE deep_ratio=9/10 blocking_findings=0
FAILED tests/test_cli.py::test_cli_degrades_when_the_real_renderer_raises_on_the_way_out
```

The exception escaped `main()` uncaught, on the default no-`--report-dir` path, from the **real**
`render_ship_readiness` at the **real** call site — DF-8-3-B reproduced, not simulated. Post-fix: green,
and the whole of `tests/test_cli.py` (12 tests, including the frozen stdout goldens `-30` / `-31`) passes.

### Fix round 2 (2026-08-06) — the four review findings

**R1 — the row-4 persisted "before" was FALSE, and the delta's sharpest change was omitted. Fixed, and the
correct string was obtained by EXECUTING HEAD's code, not by reasoning about it.**

Round 1's "every before re-derived from `git show HEAD:<file>`" did not hold for this one line: it was
copied from this story's own §D table (`:230`) — the exact trap *Traps a previous story already paid for*
warns about. The correction was derived the only way that counts. `git show HEAD:argus/verdict/verdict_gate.py`
and `git show HEAD:argus/verdict/negative_assurance.py` were `exec`'d into live modules and **run** over a
row-4-shaped input (3/10 deep — at or above the `1/5` floor, below `3/5` — and **zero** blocking findings):

```
HEAD fold, row-4-shaped run (3/10 deep, 0 findings):
  verdict           = NOT_READY_FOR_RELEASE
  blocking_findings = 0
  exit_code         = 2
HEAD fold, row-1-shaped run (1/10 deep): INSUFFICIENT_COVERAGE

HEAD's PERSISTED assurance sentence for the row-4-shaped run:
  Blocking findings were detected within the assessed scope (examined 3 deeply, sampled 7, did not cover 0 of 10).
HEAD's assurance sentence for the row-1-shaped run:
  Assessed coverage is below the floor; no repo-wide verdict was rendered (examined 1 deeply, sampled 9, did not cover 0 of 10).

LIVE fold, same input: verdict = INSUFFICIENT_COVERAGE  row = DecisionRow.GATE_UNMET_NO_FINDINGS
LIVE assurance sentence (row 4):
  No blocking findings were detected within the assessed scope; a coverage or critical-subsystem gate was not met, so release readiness was not vouched for (examined 3 deeply, sampled 7, did not cover 0 of 10).
LIVE assurance sentence (row 1):
  Assessed coverage is below the floor; no repo-wide verdict was rendered (examined 1 deeply, sampled 9, did not cover 0 of 10).
```

HEAD's `_assurance_statement` branches **only** on `verdict.verdict`, and HEAD's three-branch fold gave the
row-4 shape `NOT_READY_FOR_RELEASE`. So the real pre-amendment row-4 sentence is **`Blocking findings were
detected within the assessed scope (…).`** The string round 1 published there —
`Assessed coverage is below the floor; …` — is what HEAD produced for `INSUFFICIENT_COVERAGE`, i.e. **row
1**, which the note already listed as byte-identical. Two defects, both now closed:

1. **The false "before" is corrected.** The floor sentence stays where it belongs, on row 1.
2. **The omission — the more serious half — is closed.** The note now *publishes* the change it had
   dropped: a machine-read `.argus/state/*.json` field that asserted **"Blocking findings were detected"**
   for a run with **zero** findings now asserts **"No blocking findings were detected…"**. That is the
   sharpest single demonstration of the bug this epic deleted, it is machine-read by integrators, and no
   schema signal announces it. It is now the lead of that section rather than absent from it.

The note is also explicit that this before-string was **not replaced** — it is still exactly what row 2
renders today, for a run that really did find something. Row 4 stopped borrowing it. Saying "replaced"
would have been a second false claim in the correction of the first.

**R2 — the false negative about the live run is withdrawn and corrected**; see *AC13 live run* below,
including a first-hand unflagged re-run (not inherited from the review) showing `RELEASE_READY` / exit `0`.

**R3 — the callouts and the assurance sentence are now pinned, and the pins were shown RED against the
historical implementations.** R3 + R4 together meant the rot check structurally could not see the very
drift R1 was an instance of; fixing R1 without them would have left the hole open.

Two new tests, `TC-ArgusAgent-DOCS-001-15` (the `final-verdict.md` callouts) and `-16` (the persisted
assurance sentences). The first drafts of both had **no teeth** and this was caught before they were
accepted: asserting only *"the live text appears somewhere in the note"* still passed when HEAD's
generator was injected, because HEAD collapses rows 1 and 4 onto **one** callout and the note publishes
that text for row 1. A level-only check was no better — it passes off the quoted *before*. So the note now
publishes **every row's current callout and current assurance sentence, one row per line, level first**,
and the tests compare `(level, message)` **per row, for equality**. Two `(after|unchanged)` markers make a
line current; a `before:` line deliberately does not match, so history can never satisfy a liveness
assertion. This also removed a documentation fork: rows 1/3's callouts and rows 1/2/3's sentences were
being stated twice (once as current, once in the byte-identical list) — they are now stated once and
pointed at (§3.3 / AR7 applied to documentation).

RED-first, by injecting HEAD's implementations at **runtime** — no fenced file was written to:

```
=== against the LIVE implementations (expected GREEN) ===
GREEN -15 callouts
GREEN -16 assurance

=== with HEAD's render_final_verdict_report injected (expected RED) ===
RED   -15 callouts
      AssertionError:
      row_4_gate_unmet_no_findings's live final-verdict.md callout is not what the note publishes
        live:      ('WARNING', 'Repository deep coverage ratio is below the required floor. Additional definitions or tests required.')
        published: ('WARNING', 'Release readiness is NOT VOUCHED — Argus found nothing blocking, but deep coverage `3/10` is below the `3/5` release threshold. This is a statement about the audit, not about the code.')

=== with HEAD's _assurance_statement injected (expected RED) ===
RED   -16 assurance
      AssertionError:
      row_4_gate_unmet_no_findings's live assurance sentence is not what the note publishes
        live:      Assessed coverage is below the floor; no repo-wide verdict was rendered
        published: No blocking findings were detected within the assessed scope; a coverage or critical-subsystem gate was not met, so release readiness was not vouched for
```

(Note the two injections are different experiments and both are honest: R1's verification ran HEAD's
**fold** *and* HEAD's function, which is what establishes the historical before-string; the `-16` injection
above holds the LIVE fold and swaps only the sentence function, which is what a future reword would look
like. The `CAUTION`→`WARNING` level is pinned by `-15`'s tuple equality.)

**R4 — `-02` now reads the After cell.** `_cells()` splits the row on `|` (the way `-03` already located
its cells) and the live value is asserted against `cells[2]`. `-03` was refactored onto the same helper
rather than keeping a second copy of the splitting logic. Demonstrated against a **published downgrade** —
the note mutated in memory so the After cell reads `"1"` while the constant is live at `"2"`; the file on
disk was never written:

```
mutated row: | `VERDICT_SCHEMA_VERSION` | `"2"` | `"1"` | `argus/verdict/verdict_gate.py` |

OLD assertion  any(f'`"{live}"`' in row for row in rows): PASS <-- the hole
NEW assertion  RED
      AssertionError:
      VERDICT_SCHEMA_VERSION is live at '2', but no note row publishes it in the After column:
      rows=['| `VERDICT_SCHEMA_VERSION` | `"2"` | `"1"` | `argus/verdict/verdict_gate.py` |'], after cells=['`"1"`']
```

**Not re-done, and not regressed** — everything the review verified clean was left alone: DF-8-3-B's
closure, both schema bumps and their compatibility behaviours, the API names, the `--coverage-scope`
attribution, the RS-4b measurement, the ledger filings, the `## Unreleased` heading and D2 preamble, and
the +18 accounting. **The `argus/__init__.py` `__status__`-comment deviation was RULED CORRECT and was NOT
reverted.** No `argus/` source file was modified in this round at all — the fix is documentation and tests.

**Fix-round suite (fences re-verified):**

```
PYTHONIOENCODING=utf-8 python -m pytest tests/ -q
  →  1147 collected / 1144 passed / 3 failed / 0 skipped
python -m mypy argus
  →  Success: no issues found in 69 source files
```

Exactly the same three adjudicated carve-out reds, unmodified; **zero new reds**. The delta over the
reviewer's 1145 is **+2 collected / +2 passed**, and both are mine: `tests/test_release_note.py` 17 → **19**
(`-15`, `-16`). `tests/test_cli.py` is unchanged at **12**. **Nothing in this delta came from the
concurrent Epic-9 session.** Fences re-checked after the round: `argus/pipeline.py` md5
`399d6da1d36d668352fd7b0d539cc307` @ **1199 lines** and `argus/detectors/vacuous_test.py` md5
`8a0705030391df92ad1404af9d044758` — both **byte-identical**; Story 8.5's artifacts and
`tests/test_dogfood_*.py` not opened for writing; `argus/reports/generator.py`,
`argus/verdict/negative_assurance.py`, `argus/reports/plain_english.py` and `argus/verdict/verdict_gate.py`
were **read** (and `git show`n at HEAD) but never written — they remain `M` from 8.1–8.3 only.

**Observation recorded, not fixed — not this story's, and no AC covers it.** `git status` shows three
**tracked `.pyc` files** as modified (`argus/cost/__pycache__/exhaustion.cpython-312.pyc`,
`argus/ledger/__pycache__/critical_subsystems.cpython-312.pyc`,
`tests/cartridges/__pycache__/_registry.cpython-312.pyc`). They are compiled artifacts of modules Stories
8.1–8.3 changed, and **any** test run rewrites their bytes — so running the suite dirties the working
tree. **26 `.pyc` files are tracked** even though `.gitignore` line 2 already carries `__pycache__/`, i.e.
they were committed before that rule existed and are not being ignored now. This is pre-existing repo
hygiene, it touches no fenced path and no AC, and it is **stated rather than silently absorbed** so it is
not mistaken for this story's delta. Not filed as a DF: it is Epic-9 packaging territory (`.gitignore` /
distribution hygiene) and this loop does not own that file.

**AC13 — whole system, recorded verbatim.** (Round 1's figures, kept as the record of that round;
**superseded by the fix-round run above** — 1147 / 1144 / 3 / 0.)

```
PYTHONIOENCODING=utf-8 python -m pytest tests/ -q
  →  1145 collected / 1142 passed / 3 failed / 0 skipped
python -m mypy argus
  →  Success: no issues found in 69 source files
```

```
FAILED tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation
FAILED tests/test_dogfood_plan.py::test_budget_reuses_the_31_accountant_no_fork
FAILED tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run
```

**Exactly the three adjudicated carve-out reds, unmodified — zero new reds.** 1–2 are inherited (red at
`9109e16`); 3 is deliberate and is Story 8.5 / DR-10's deliverable. None of the three files was touched.

**Count reconciliation — the concurrent Epic-9 session's contribution is separated out, not absorbed.**
Baseline (8.3 reviewer, this tree): 1127 collected / 1124 passed / 3 failed. Now: 1145 / 1142 / 3.
Delta **+18 collected, +18 passed, +0 failed**, and **all 18 are mine**: `tests/test_release_note.py`
collects **17** (13 single tests + a 4-way parametrize) and `TC-ArgusAgent-CLI-001-33` adds **1** to
`tests/test_cli.py` (12, was 11). Nothing in the delta came from the Epic-9 session; its earlier
`tests/test_no_web_imports.py` addition was already inside the 1127 baseline.

**AC13 live run — `argus audit .` on this repository, as observed, nothing adjusted.**

⚠️ **Corrected in fix round 2 (finding R2).** Round 1 recorded the run below and drew a false inference
from it. **The invocation was not the bare one**: it was `audit . --commit HEAD --budget 200`. `--budget`
defaults to `0`, which means **no ceiling** (`argus/cli.py:101-111`); `200` is a positive credit ceiling
that halts the deep pass early and takes `deep_count` **57 → 29**. The row-4 result below is the correct
fold *for a budget-capped run* — it is a property of the flag, not of the tool.

```
$ python -m argus.cli audit . --commit HEAD --budget 200 ; echo EXIT=$?
verdict=INSUFFICIENT_COVERAGE deep_ratio=29/149 blocking_findings=0 assessed_deep_ratio=29/73 scope=application held_out=76
EXIT=3
stderr: Ship-readiness: NOT VOUCHED — nothing broken was found, but a coverage or critical-subsystem gate
        was not met, so no release-readiness claim is made. This is a statement about the audit, not about
        the code.
```

**`D8` REPRODUCES under the unflagged invocation 8.2 and 8.3 used.** Re-run first-hand in fix round 2 on
this same tree (not inherited from the review — re-derived):

```
$ python -m argus.cli audit . ; echo EXIT=$?
verdict=RELEASE_READY deep_ratio=57/149 blocking_findings=0 assessed_deep_ratio=57/73 scope=application held_out=76
EXIT=0
stderr: Ship-readiness: READY — no blocking problems found, and enough of the code was examined deeply to
        say so.
```

**Both folds are correct, and neither contradicts the note.** `57/73 ≥ 3/5` with 0 findings and every
critical subsystem deep is an honest FR16 **row 3**; `29/73` (at or above the `1/5` floor, below `3/5`)
with 0 findings is an honest **row 4** — precisely the one run class `CHANGELOG.md` says moved from exit
`2` to exit `3`, with a stderr headline byte-identical to the row-4 string the note publishes. Per **D8**
neither result is cited in `CHANGELOG.md` or offered as evidence of anything; they are the AC13
consistency check only.

**Round 1's claim that "D8 did not reproduce" is withdrawn as unsupported.** The *observation* was
recorded honestly and nothing was adjusted to fit; the *inference* attached to it attributed a flag's
effect to the tool, which is exactly the class of unsupported negative claim this epic exists to delete.
Recording an observation and asserting a cause are two different acts, and only the first was earned.
The live runs wrote a (gitignored) `.argus/` state directory, **left in place** rather than deleted — a
concurrent session shares this tree and that directory is not mine to remove.

**Fence verification (AC12).** `git diff --stat HEAD` cannot be empty for files 8.1–8.3 already changed in
this uncommitted tree, so md5 / line count is the correct instrument, exactly as the story's own fence
baselines anticipate:

| Fenced path | Instrument | Result |
|---|---|---|
| `argus/pipeline.py` | md5 + `wc -l` | `399d6da1d36d668352fd7b0d539cc307`, **1199 lines** — **byte-identical**, DF-8-2-A intact, cap not approached |
| `argus/detectors/vacuous_test.py` | md5 | `8a0705030391df92ad1404af9d044758` — **byte-identical**, DF-8-2-B intact |
| `argus/reports/plain_english.py` | `wc -l` | **258** — matches the story's baseline; untouched |
| `argus/reports/generator.py` | `wc -l` | **613** — matches the story's baseline; untouched |
| `argus/verdict/verdict_gate.py`, `argus/ledger/critical_subsystems.py`, `argus/verdict/negative_assurance.py`, `argus/verdict/prosecutor.py`, `argus/cost/exhaustion.py` | `git status` set comparison | still `M` from 8.1–8.3 only; **no new modification** — this story DOCUMENTS the contract, it did not change it |
| `action.yml`, `.github/workflows/*`, `argus/audit/minions_llm_adapter.py`, `tests/test_no_web_imports.py`, `stories/9-1-*.md` | not opened for writing | **untouched** (foreign / Epic 9) |
| `minions-dogfood-*.md`, both `final-verdict.md`, `tests/test_dogfood_proof.py`, `tests/test_dogfood_plan.py` | not opened for writing | **untouched** (Story 8.5 / DR-10) |
| `pyproject.toml` `version`; `argus/__init__.py`'s `__version__` / `__status__` / `__all__` | `git diff HEAD` | **no `+`/`-` line touches any of the three assignments**; `pyproject.toml` not modified at all |
| `tests/fixtures/verdict_schema_v1_row2_artifacts.json` | read-only | used as **evidence**; not regenerated |

`argus/cli.py` 298 → **307** lines (+9, AC11 only). `argus/__init__.py` 66 → **59** lines (docstring only).
Both far inside NFR-M1's 1200-line cap. **No new dependency; no `.github/workflows/*`, no tag, no
`pyproject.toml` version change, no `action.yml` edit, and no prose anywhere claiming a published
distribution.**

**Sprint-status write:** the file was re-read immediately before writing and **only** the
`8-4-tell-integrators-what-changed` key was changed (byte-level replace of that one line, CRLF preserved).
`epic-9` / `9-1-` / `9-2-` and every comment + the STATUS DEFINITIONS block are untouched.

### Completion Notes List

**Deferred-item dispositions (AC13) — restated here, not inherited.**

- **DF-8-3-B — CLOSED by this story.** Its ledger `target_story` names `8-4` first and unconditionally.
  Closing test `TC-ArgusAgent-CLI-001-33`, demonstrated RED-first against the pre-fix `cli.py`. Closure
  recorded in `deferred-work.md` as an **append-only** note; the original entry was not rewritten.
- **DF-8-2-A — CARRIED FORWARD, not closed.** `target_story` is *"8-3 (or the first story after 8.2 that
  edits `argus/pipeline.py`)"* — it does not name 8-4, and this story needed nothing from `pipeline.py`.
  AC12 fenced it and the file is verified **byte-identical** (md5 above), so the 1199/1200 cap was not
  approached and the shell-helper extraction stays queued.
- **DF-8-2-B — CARRIED FORWARD, not closed.** `target_story` is conditional on a story editing
  `argus/detectors/vacuous_test.py`; the condition did not fire (fenced, md5 verified byte-identical).
  Still zero live instances in this repository.
- **DF-8-3-A — CARRIED FORWARD, not closed.** `target_story` is *"the story that performs the DF-8-2-A
  `pipeline.py` extraction"*. Closing it needs a new `generate_reports` argument threaded from
  `pipeline.py:793` — i.e. exactly the fenced edit. Not this story.
- **DF-8-3-C — CARRIED FORWARD, not closed.** Same `target_story`; its only sensible homes are the two
  fenced files (`pipeline.py`, `vacuous_test.py`).
- **Newly filed (AC10):** `RS-4b` and `DF-8-4-A`, both with the six mandatory CC-3 fields, appended under a
  dated section header. Append-only was **verified byte-for-byte**: the 48 684-byte prefix of
  `deferred-work.md` is unchanged after the write.

**Decisions taken, and the disagreements recorded rather than acted on silently.**

1. **AC4 vs AC9 reconciled explicitly, not fudged.** AC4 requires `CHANGELOG.md` to **quote** the strings it
   says were replaced; AC9 requires a test asserting the note does **not contain** them. Taken literally
   together they are unsatisfiable. `TC-ArgusAgent-DOCS-001-06` implements the only reading that honours
   both: every occurrence of a pre-amendment string must sit in an explicitly-labelled *"before"* context
   (the line itself or the line introducing it). The note may quote the old wording as **history**; it may
   not **state** it as current. The test also asserts the fragment is present at all, so a note that simply
   deletes the history fails too, and separately asserts the live replacement is published.
2. **One deviation from the Story Context table, deliberate and recorded.** The table marks
   `argus/__init__.py:56-66` as *"correct — DO NOT TOUCH"*, but lines 61–63 are a **comment** citing
   `story 22-15` and `DF-22-15-A` — Minions-tracker ids that do not exist in this repository — and stating
   that ArgusAgent is *"NOT wired into the Minions product run path"*. AC8's binding text explicitly
   requires the file to stop carrying *"the `EXPERIMENTAL (story 22-15) / DF-22-15-A` Minions-tracker
   status"*. An AC binds; a descriptive measurement table does not. So that **comment** was rewritten while
   the three **assignments** the fence actually protects (`__version__`, `__status__`, `__all__`) are
   byte-identical — verified by `git diff HEAD -- argus/__init__.py`, which contains no `+`/`-` line
   touching any of them. The load-bearing rationale in both AC8 and AC12 is `__version__`'s NFR-P1 hash
   contribution, and that is untouched. **If a reviewer reads the fence as covering the comment too, this
   is the disagreement, stated rather than hidden — reverting those three comment lines is a two-line
   change that costs nothing else.**
3. **RS-4b's measured surface is refined upward, in the direction of accuracy.** The story states *"three
   of them are `lines.append(...)` calls that emit the stale path into GENERATED Markdown artifacts"*.
   Re-measured: it is **six references across five `lines.append(...)` call sites** —
   `partition_plan.py:481`, `:490`, `:554` and `proof_run.py:597`, `:609-610`. The story's three
   (`481`, `554`, `597`) are the AUTO-GENERATED banners; it missed `partition_plan.py:490`'s provenance
   line and `proof_run.py:609-610`'s scope paragraph, which are also emitters. `proof_run.py:486` is a
   third kind again (an operator-visible `DogfoodProofError` message). The **total is unchanged at 15
   references across 8 files**, matching the story exactly. The ledger entry records the measured six,
   because a ledger entry that understates its own surface is the same defect class this story exists to
   close.
4. **AC11 implemented as the AC's first sanctioned option** — *widen* the `try`, rather than *move* the
   render. Moving the render before the summary print would also have guarded it, but it would reorder the
   writes to the two registers; widening leaves stdout and stderr byte-identical, in the same order, on
   every non-raising path. One visible consequence is recorded honestly in the test rather than papered
   over: on the raising path the stdout wire line has **already** been written when the failure lands, so
   the run emits a summary line and then exits `1`.
   Second-order effect, disclosed: `UnicodeEncodeError` is a `ValueError` subclass, so a console-encoding
   failure while printing the (em-dash-bearing) human register now degrades to the AR10 typed exit `1`
   instead of a bare traceback. That is the AR10 contract working as specified, not a new behaviour class.
5. **`TC-ArgusAgent-CLI-001-33` does not repeat `-32`'s mistake.** The prior test monkeypatched
   `cli.run_audit` to **raise**, so its exception originated inside the `try` and the test would pass no
   matter where `render_ship_readiness` was called. Here `run_audit` is stubbed to **return** the one
   verdict FR16 cannot produce, and the **real** `render_ship_readiness` raises the **real**
   `ShipReadinessError` at the **real** site with **no** `--report-dir`. Hand-constructing that
   `AuditVerdict` is the story's own sanctioned exception for exactly this contract-violation pin —
   `evaluate_verdict` structurally cannot emit that state, which is the invariant Story 8.1 established, so
   there is no other way to reach the site.
6. **§3.3 / AR7 no-fork applied to documentation.** The exit-code contract, the four-row FR16 table and the
   schema values are stated in **one** place, `CHANGELOG.md`. `README.md` gained a single pointer line with
   **no** contract text in it, and the rewritten `argus/__init__.py` docstring deliberately **points at**
   `CHANGELOG.md` rather than restating any of it. A second copy is a second thing that can go stale, which
   is the failure this story exists to end.
7. **Epic 9 untouched, and its work not absorbed.** No release workflow, no tag, no `pyproject.toml`
   version bump, no `action.yml` or `.github/workflows` edit, and no prose claiming `argus-agent` is
   published — `TC-ArgusAgent-DOCS-001-07` pins that last one mechanically so a later edit cannot quietly
   turn `## Unreleased` into a release heading. `action.yml`'s exit-`1` mislabel was **filed as DF-8-4-A,
   not fixed** (D7).

### File List

**New**

- `CHANGELOG.md` — the integrator release note (DR-8). `git add`ed. Fix round 2 corrected the row-4
  persisted-assurance *before* string, published the assurance-sentence change it had omitted, and
  restructured the callout + assurance lists so every row's **current** string is published once, per row,
  level first (R1, R3).
- `tests/test_release_note.py` — `TC-ArgusAgent-DOCS-001-01..16` (**19** collected); the AC9 rot check plus
  the AC8 front-door pins. New verification area `ArgusAgent-DOCS`. `git add`ed. Fix round 2 added `-15`
  (the `final-verdict.md` callouts, text **and** alert level, per row) and `-16` (the persisted
  negative-assurance sentences, per row, plus the code-anchored row-4 *before*), and re-pointed `-02` at
  the After cell (R3, R4).

**Modified**

- `argus/__init__.py` — docstring rewritten (RS-4a / AC8). `__version__` / `__status__` / `__all__`
  byte-identical. 66 → 59 lines.
- `argus/cli.py` — AC11 / DF-8-3-B: the `try/except ValueError` in `main()` widened to span the summary-line
  print and the ship-readiness render. 298 → 307 lines.
- `tests/test_cli.py` — added `TC-ArgusAgent-CLI-001-33` (add-only; no existing test altered).
- `README.md` — one pointer line to `CHANGELOG.md` (AC7). No contract text.
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — **append-only**: RS-4b, DF-8-4-A, and the
  DF-8-3-B closure note.
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — **only** the
  `8-4-tell-integrators-what-changed` key.
- `_bmad-output/design-artifacts/ArgusAgent/stories/8-4-tell-integrators-what-changed.md` — this file
  (Status, Tasks, Dev Agent Record, File List, Change Log).

**Deliberately NOT modified** — see the AC12 fence table in *Debug Log References*.

## Change Log

| Date | Change |
|---|---|
| 2026-08-06 | **DR-8 — `CHANGELOG.md` created** at the repository root, headed `## Unreleased` with the D2 honesty preamble. Publishes: the one run class that moved exit `2`→`3` plus the full four-row FR16 table (AC1); **both** schema bumps with their two **different** compatibility behaviours and the content-addressed-filename consequence (AC2); the `--coverage-scope` flip, honest that it predates the delta (AC3); every changed rendered string with a matching byte-identical list (AC4); the unchanged stdout line, the unchanged enum, and the row-derivation rule with the "read `decision_row` instead" direction (AC5); the API surface with `ShipReadinessError` flagged **behavioural** (AC6). Every "before" string re-derived from `git show HEAD:<file>`; every "after" string rendered live. |
| 2026-08-06 | **AC7 — placement + no-fork.** `README.md` gained exactly one pointer line to `CHANGELOG.md`, carrying no contract text. No release workflow, tag, `action.yml` edit or `pyproject.toml` version change was created. |
| 2026-08-06 | **RS-4a / AC8 — `argus/__init__.py` front door rewritten.** Removed: the `minions_core/argus/` placement claim, `RESERVED PACKAGE SHELL — no business logic yet`, the `EXPERIMENTAL (story 22-15) / DF-22-15-A` Minions-tracker status, the `minions[argus]` distribution claim, the "reuses proven Minions infrastructure via direct import" claim, the dead `_bmad-output/planning-artifacts/decisions/…` path, and `Architecture / epics / stories: TO BE CREATED`. Replaced with facts cross-checked against `pyproject.toml` and against paths verified to exist on disk. `__version__` / `__status__` / `__all__` byte-identical (NFR-P1). |
| 2026-08-06 | **AC9 — rot check added, RED-first.** `tests/test_release_note.py` imports the shipped constants and renders the shipped strings through real `evaluate_verdict` folds, then pins `CHANGELOG.md` against them. Shown failing (6 tests, 4 independent rot modes) against a deliberately-stale note; failure output recorded verbatim. No new dependency, no network, no LLM, no `.argus/` write. |
| 2026-08-06 | **AC11 — DF-8-3-B CLOSED.** `argus/cli.py::main`'s `try/except ValueError` widened to cover the summary-line + ship-readiness block, so a `ShipReadinessError` on the default no-`--report-dir` path degrades to the AR10 typed exit `1` instead of escaping as an uncaught traceback. Closing test `TC-ArgusAgent-CLI-001-33` lets the **real** renderer raise at the **real** site (no monkeypatched stand-in for the raise), demonstrated RED-first. Frozen stdout goldens `-30`/`-31` still pass byte-identically. |
| 2026-08-06 | **AC10 — ledger.** `RS-4b` (15 refs / 8 files, enumerated; **six** of them across five `lines.append(...)` sites emit into GENERATED artifacts; sequenced to follow Story 8.5) and `DF-8-4-A` (`action.yml`'s `else` publishes exit `1` as `INSUFFICIENT_COVERAGE`; foreign file, filed not fixed) appended with the six CC-3 fields each, plus the DF-8-3-B closure note. **Append-only verified byte-for-byte.** |
| 2026-08-06 | **Code review round 1 — 4 findings resolved (1 blocking Med, 1 record-correction Med, 2 Low).** **R1:** the note's row-4 persisted negative-assurance *before* was FALSE (it published row 1's floor sentence). Corrected to `Blocking findings were detected within the assessed scope (…).`, obtained by **executing** HEAD's fold and HEAD's `_assurance_statement` verbatim (`git show HEAD:…` → `exec`) over a row-4-shaped run, not by reading them; and the omitted half — a machine-read `.argus/state/*.json` string that asserted *"Blocking findings were detected"* for a run with **zero** findings and now asserts *"No blocking findings were detected…"* — is now **published** as the lead of that section, with the note explicit that the string was not replaced but is still row 2's. **R2:** the Dev Agent Record's *"D8 did not reproduce"* is **withdrawn as unsupported** — the run carried `--budget 200` (a positive ceiling; the default `0` means none), and a first-hand unflagged re-run gives `RELEASE_READY` / exit `0` / 57/73. **R3:** `-15` and `-16` pin the `final-verdict.md` callouts (text **and** the `CAUTION`→`WARNING` level) and the persisted assurance sentences, **per row, by equality** — the first drafts had no teeth and were rejected before acceptance; shown **RED** by injecting HEAD's `render_final_verdict_report` and `_assurance_statement` at runtime. **R4:** `-02` now asserts the **After** cell via a shared `_cells()` helper, shown RED against a published downgrade the old scan passed. Suite **1147 / 1144 / 3 / 0** — the same three carve-out reds, zero new; mypy clean over 69 files; fences byte-identical; no `argus/` source file modified in this round. |
| 2026-08-06 | **AC12/AC13 — fences + whole system.** `argus/pipeline.py` and `argus/detectors/vacuous_test.py` verified **byte-identical by md5**; all other fenced paths verified untouched. Suite **1145 collected / 1142 passed / 3 failed / 0 skipped** — exactly the three adjudicated carve-out reds, **zero new reds**; mypy **clean over 69 files**. The +18 delta over the 1127 baseline is entirely this story's new tests; the concurrent Epic-9 session contributed nothing to it. `argus audit .` run live: `INSUFFICIENT_COVERAGE` / exit `3`, a real FR16 row 4 — recorded as observed, not cited in the note (D8). |
