---
baseline_commit: be9d7449cf564bd8cc1e9a9000c04d78f7e0021c
baseline_note: >-
  HEAD is be9d744 ("feat(verdict,reports,packaging): land Epic 8 stories 8.1-8.4
  and Epic 9 story 9.1"). UNLIKE stories 8.1-8.4, the Epic-8 delta is now COMMITTED —
  `git status` is clean except one untracked directory, `bmad-dev-loop-pack/`, which
  belongs to the orchestrator and is NOT yours. Do not add, move or delete it.
  Consequence you must internalise: `git diff HEAD` is EMPTY, so it is no longer the
  measuring instrument. Every "before" figure in this story was produced by IMPORTING
  and CALLING the shipped `argus` functions in place, and by running the shipped CLI.
  Re-derive them the same way; do not read them off this document and do not trust it.
  Because the tree is dirty the moment you start work, `--strict` cannot be used and
  every report you regenerate will honestly carry `Source State: worktree`. That is
  expected — see D8.
---

# Story 8.5: Re-derive the proof so the evidence matches the tool

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
> **This is the FIFTH AND LAST story of Epic 8** ("The Honest Verdict — no block without a finding").
> `epic-8` is already `in-progress`. **Stories 8.1, 8.2, 8.3 and 8.4 are all `done`** (each PASSED code
> review). 8.5 was sequenced last **by design**: it re-derives the published evidence, so if any of 8.1-8.4
> slipped, the slip becomes *visible* here rather than shipping silently.
>
> **THIS STORY DELIVERS DR-10 — the evidence.** Epic 8 changed what a verdict *means* (8.1), which files a
> critical gate may demand (8.2), what the two report surfaces *say* (8.3), and published the migration
> contract (8.4). What it has **not** done is go back to the artifacts Argus has already committed to this
> repository and make them agree. Right now this repository publishes **three** artifacts asserting
> `NOT_READY_FOR_RELEASE` with `Blocking Findings: 0` — the exact impossible state the whole epic exists to
> delete — plus **two committed dogfood plan artifacts that no longer match their own generator.** An
> assurance product whose own published evidence contradicts its shipped contract has committed the defect
> it exists to detect in other people's repositories. That is not a documentation gap; on this product it
> is the cardinal defect.
>
> **It does NOT deliver:** DR-1/2/3/4/9 (8.1, done); DR-5/6/7 (8.2, done); DR-11 (8.3, done); DR-8 + RS-4a
> (8.4, done). It does not touch `argus/verdict/`, `argus/ledger/`, `argus/reports/`, `argus/pipeline.py`,
> `argus/cli.py` or `CHANGELOG.md` — see **AC13**.
>
> **🚫 EPIC 9 IS EXPLICITLY OUT OF SCOPE.** Story 9.1 (`argus` stops importing `minions_core`) is `done`;
> **Story 9.2 (IN-0 — ship a resolvable distribution) is `backlog` and owns everything release-shaped**:
> the release workflow, the tag, the version bump, `action.yml`, `.github/workflows/*`, and any prose
> claiming `argus-agent` is published (it is on no index — assumption A1, falsified 2026-08-03). This story
> creates none of those and claims none of it.
>
> **🚩 The single largest trap in this story.** The dogfood generator's name and prose say *Minions*. Its
> code does not. `argus/dogfood/proof_run.py::enumerate_tracked_sources` defaults to
> `scope_prefix="argus"` — **it audits THIS repository's own `argus/` package.** Minions source is not in
> this repo and cannot be. If you simply regenerate the artifact you will publish a document that says
> *"the frozen audit over the REAL Minions repo"* and *"The audited BYTES are the real Minions source"*
> about a **self-audit of Argus** — a brand-new published falsehood, introduced by the story whose entire
> purpose is that no Argus artifact lies. **AC2 exists for this. Read D2 and D3 before you touch anything.**

---

## Story

As the **XAgents platform owner** — who can today clone this repository, open
`_bmad-output/audit-reports/final-verdict.md`, and read Argus asserting
**`NOT_READY_FOR_RELEASE` (Exit Code `2`)** directly above **`Blocking Findings: 0`**, which under the
contract this very epic just shipped is a verdict Argus can no longer produce —

I want **the published proof and verdict artifacts re-derived so they agree with the shipped contract, each
one disclosing what was actually audited, which decision row fired, and the inputs it was computed from**,

so that **Argus is not itself over-claiming — the defect it exists to detect.** And so that when the
originating operator command is run again, the symptom that triggered this whole amendment is demonstrably
gone rather than merely believed to be gone.

---

## Story Context

### Method statement — MEASURED IN PLACE, on the real working tree

> ⚠️ **Read this.** Everything below was produced on `d:/ProjectX/XAgents/XAgents/ArgusAgent` itself at
> HEAD `be9d744`, with `.git` and `_bmad-output/` present — **not** on a scratch copy. Unlike stories
> 8.1-8.4, **`git diff HEAD` is empty** (Epic 8 is committed), so the instruments were:
>
> 1. **Importing the shipped `argus` functions and calling them in place** — the real
>    `build_dogfood_proof` / `run_dogfood` / `build_full_repo_plan` / `evaluate_verdict` /
>    `render_proof_markdown` / `render_partition_plan_markdown` / `render_budget_plan_markdown`, and the
>    real `ApaaStoreReader` over the real `.argus/` tree.
> 2. **Running the shipped CLI** — `python -m argus.cli audit .` at both coverage scopes.
> 3. **`python -m pytest tests/ --tb=no`** for the exact baseline red set.
>
> No `.argus/` write, no report and no artifact was left behind by the SM outside the scratchpad, except
> the `.argus/` tree the CLI runs legitimately produced (gitignored).
> **Re-derive every figure yourself — do not trust this document.**

### Baseline, measured 2026-08-07 at HEAD `be9d744`

| Instrument | Result |
|---|---|
| `python -m pytest tests/ --tb=no` | **1147 passed, 3 failed** in 173s |
| `python -m mypy argus` | **Success: no issues found in 69 source files** |
| `git status --porcelain` | `?? bmad-dev-loop-pack/` only (orchestrator's — not yours) |

**The three failures are this story's deliverable, not incidental damage:**

| Test | Why it is red |
|---|---|
| `tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation` | committed plan pins units `8c20feb2c997` / `ab6ff465ec4a` / `b66e4aaf9a15`; the live derivation now yields `2c0f52f60457` / `681c496d09ed` / `973f3f199d1c` |
| `tests/test_dogfood_plan.py::test_budget_reuses_the_31_accountant_no_fork` | `assert '431' in <committed budget plan>` — the committed artifact records the old sized ceiling `406` |
| `tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run` | ``assert '`RELEASE_READY` (exit `0`)' in <committed proof>`` — the committed artifact records ``NOT_READY_FOR_RELEASE`` / exit ``2`` |

> ⚠️ **The epic's precondition note is now partly out of date and you must not be misled by it.** It says
> `tests/test_dogfood_plan.py` carries **two** pre-existing failures present on the clean tree at `ae5f00c`
> and *"unrelated to this delta"*. Both are still red — **and a third has joined them**,
> `test_committed_proof_artifact_exists_and_matches_live_run`, which **is** delta-caused: the amended
> decision table (8.1) plus the amended critical-set eligibility (8.2) moved the live dogfood verdict from
> `NOT_READY_FOR_RELEASE` to `RELEASE_READY`, so the committed proof stopped matching. **AC6 requires you
> to fix all three and to report the first two as pre-existing rather than absorbing them into this
> delta's own result.** See **D6** for the reasoning and for what is genuinely different about them.

### The re-derivations, MEASURED — every number here was produced by calling the shipped code

#### A. The live dogfood, run through the real `build_dogfood_proof('.')`

| Field | Committed artifact (stale) | Live derivation (measured) |
|---|---|---|
| Commit descriptor | `7f8e1478573d3208c1df16aaaaa4f6f0bb0afea0` | `be9d7449cf564bd8cc1e9a9000c04d78f7e0021c` |
| Source files audited | 135 | **69** |
| Total LOC | 36712 | **17736** |
| Partition units | 4 | **3** |
| **Verdict** | **`NOT_READY_FOR_RELEASE` (exit `2`)** | **`RELEASE_READY` (exit `0`)** |
| Deep-% | `13/15` | **`53/69`** |
| Blocking findings | 0 | **0** |
| Total findings | 2906 | **97** |
| Cost total / ceiling | 675 / 843 | **345 / 843** (fits) |
| Baseline ratio | `675/36712` | **`115/5912`** |
| Adjudication classes | `cross_partition` 332 · `hardcoded_secret` 2289 · `orphan_code` 285 | **`cross_partition` 2 · `hardcoded_secret` 19 · `orphan_code` 76** |

Straight off the `AuditVerdict` the live run produced (`run_dogfood('.', …).result.verdict`):

```
verdict RELEASE_READY   exit 0
decision_row  DecisionRow.GATES_MET          # -> "row_3_gates_met"
deep_ratio 53/69   deep 53   total 69
coverage_scope None                          # the snapshot holds no test files, so NO narrowing occurred
blocking 0
critical_subsystems_not_deep  ()             # empty
schema_version "2"   is_below_floor False
```

**Boundary B1 held exactly as the epic predicted.** The epic explicitly refused to pin a verdict here and
warned that clearing the critical clause at high deep-% moves the run to **row 3 → `RELEASE_READY` / exit
`0`**, *not* row 4 as an earlier draft asserted. It does. **Do not treat this as a target to hit** — if
your tree produces something else, the artifact records what your tree produced. AC1 pins the **method**,
never the outcome.

#### B. The historical Story-7.2 Minions run, folded through the real amended gate

Minions source is **not in this repository** and cannot be re-run here, so this half is **analytic**. The
7.2 recorded facts are deep-% `13/15`, **0** blocking findings, and the critical-subsystem clause as the
only thing withholding `RELEASE_READY`. Folded through the real shipped `evaluate_verdict` over a synthetic
15-entry ledger at 13 deep (zero LLM tokens, pure function):

| Critical clause | Verdict | Exit | Row |
|---|---|---|---|
| unmet (as recorded in 7.2) | `INSUFFICIENT_COVERAGE` | `3` | `row_4_gate_unmet_no_findings` |
| cleared by the DR-5 eligibility filter | `RELEASE_READY` | `0` | `row_3_gates_met` |

**The load-bearing, fully determinable statement: under the amended table those inputs cannot produce
`NOT_READY_FOR_RELEASE` / exit `2` under ANY branch.** Which of row 3 / row 4 actually fires depends on
recomputing DR-5 eligibility over the Minions ledger, which is **not obtainable in this repository**. Say
that plainly; do not guess, and do not quietly pick one.

#### C. The originating operator command, re-run (Inversion F5)

The command that triggered this entire amendment — `argus audit .` on ArgusAgent — recorded in
[sprint-change-proposal-2026-08-03.md](../sprint-change-proposal-2026-08-03.md) as returning
`verdict=NOT_READY_FOR_RELEASE deep_ratio=11/28 blocking_findings=0`. Re-run at HEAD `be9d744`:

```
$ python -m argus.cli audit .                                # default scope (application)
verdict=RELEASE_READY deep_ratio=57/149 blocking_findings=0 assessed_deep_ratio=57/73 scope=application held_out=76
exit 0

$ python -m argus.cli audit . --coverage-scope repository    # the ORIGINAL scope of the reported symptom
verdict=INSUFFICIENT_COVERAGE deep_ratio=57/149 blocking_findings=0
exit 3
```

**The symptom is not reproducible at either scope.** Note the second line especially: the reported symptom
was measured under the *whole-repository* denominator, and that is the branch that used to render
`NOT_READY_FOR_RELEASE`. It now renders row 4 → `INSUFFICIENT_COVERAGE` / exit `3`. Both scopes must be
run and both recorded, or the F5 evidence is one flag away from being vacuous (**AC10**).

#### D. The three stale verdict/report artifacts on disk

| Path | Tracked? | Currently asserts | Verdict |
|---|---|---|---|
| `_bmad-output/audit-reports/final-verdict.md` | **YES — committed** | `NOT_READY_FOR_RELEASE` (exit `2`), deep `49/125`, **Blocking Findings: 0** | published contradiction |
| `_bmad-output/audit-reports/coverage-ledger.md` | **YES — committed** | its sibling from the same stale run | regenerate with it |
| `_bmad-output/reports/final-verdict.md` | no — **gitignored** (`.gitignore:20 _bmad-output/reports/`) | `NOT_READY_FOR_RELEASE` (exit `2`), deep `11/28`, **Blocking Findings: 0** | local only |

Regenerated live to a scratch directory, the same generator now emits a document that opens with
`Ship-readiness: READY`, discloses **both** ratios, the assessment scope and the 76 held-out files, and
carries the `[!NOTE]` stating *"No language model read any source … a structural and deterministic
assurance grade, not a comprehension grade."* The honesty carrier already exists in the shipped generator —
you do not need to add one, and **you must not hand-edit a generated file to add one** (**D5**).

#### E. What the committed proof artifact says that is simply not true

Measured by reading `render_proof_markdown` and comparing to what the code does:

| Rendered claim | Reality |
|---|---|
| `# Minions Dogfood — Proof Artifact` | the generator enumerates `scope_prefix="argus"` — it audits **this** repo's `argus/` tree |
| `## 1. Dogfood execution … the frozen audit over the REAL Minions repo` | a **self-audit** of Argus |
| *"REAL Minions platform source (git-tracked `minions_core/`, excluding the self-audited `minions_core/argus/` sub-tree)"* | git-tracked `argus/`, excluding `argus/tests/` |
| *"The audited BYTES are the real Minions source"* | the audited bytes are Argus's own source |
| *"Proven over the REAL Minions tree by `tests/security/test_argus_secret_containment.py`"* | **that path does not exist**; `tests/security/` does not exist |
| *"in `tests/argus/test_dogfood_proof.py`"* (×2) | **that path does not exist**; the file is `tests/test_dogfood_proof.py` |
| `> AUTO-GENERATED by `minions_core/argus/dogfood/proof_run.py`` | **that path does not exist**; the file is `argus/dogfood/proof_run.py` |

The partition/budget renderers carry the same class of defect: `# Minions Dogfood — …` titles, *"tracked
Minions content"*, `- Source files (tracked `minions_core/`, excluding `minions_core/apaa/`)`, and
`> AUTO-GENERATED by `minions_core/apaa/dogfood/partition_plan.py`` (×2).

**A re-derived artifact that keeps these is a NEW published falsehood, authored by this story.** AC2.

#### F. The internal contradiction the re-derivation would otherwise publish

The proof artifact says *"It FITS under the **7.1 empirical ceiling** `$X` = **843**"*. The live 7.1 budget
plan sizes `$X` = **431** (total 345 × 5/4). After this story regenerates both, two committed Argus
artifacts would disagree about what "the 7.1 empirical ceiling" is. `843` is a **frozen historical
constant** (`DOGFOOD_BUDGET_CEILING`, pinned by `TC-ArgusAgent-DOGFOOD-001-19` and by the artifact rot
check) and must stay — but it must stop being *called* the current 7.1 sizing. **AC1 + D7.**

#### G. The critical-subsystem clause is retrievable — and on a green result it must be disclosed

Proven in place against this repo's `.argus/` store, using only already-shipped seams:

```python
from argus.store.reader import ApaaStoreReader
from argus.ledger.critical_subsystems import CriticalSubsystemSet
from argus.pipeline_persist import CRITICAL_SUBSYSTEMS_PRODUCER   # "argus.pipeline.critical_subsystems"

r = ApaaStoreReader(<repo>)                       # run_dogfood already builds one for the 4.2 lint
env = <the state/*.json envelope whose .producer == CRITICAL_SUBSYSTEMS_PRODUCER>
cs  = CriticalSubsystemSet.model_validate(env.payload)
# measured on THIS repo: len(cs.paths) == 50, len(cs.heuristic_excluded_ineligible) == 65,
#                        cs.designated_but_unmatched == ()
```

This matters because the epic's **Inversion F1** is unguarded: the delta **loosens** the critical gate
twice (DR-5 auto-exclusion + the `--coverage-scope application` default), and *nothing* guards the
PRD-fatal false-`RELEASE_READY` direction. A green verdict whose critical clause was satisfied because the
critical set was **empty** is a vacuously satisfied gate, and boundary **B3** says a vacuously satisfied
gate must be visible. On this repo the set is genuinely 50 paths — but the artifact must **state** which
case it is, per run, rather than leave the reader to assume. **AC1.**

#### H. Strings and headings the EXISTING tests already pin — your honesty rewrite must preserve every one

This is the single most likely way to turn 3 red tests into 8. Each row is a live assertion in the two
dogfood test modules, verified today. **Read this table before you edit a renderer.**

| Pinned by | Assertion (paraphrased from the source) | Consequence for your rewrite |
|---|---|---|
| `…-001-20` proof rot check | headings `"## 1. Dogfood execution"`, `"## 3. The SIGNED, source-free evidence bundle"`, `"## 7. The"` must appear in **both** the live render and the committed file | you may change the **tail** of heading 1 (`… — the frozen audit over the REAL Minions repo`); you may **not** renumber or re-word the stems |
| `…-001-20` | `"$X` = 843"` **or** `"843"` in the artifact | D7's frozen ceiling must stay rendered |
| `…-001-20` | `"REUSED"` or `"REUSING"` in the artifact | keep the AR7 no-fork narration |
| `…-001-25` | `f"grade: {DOGFOOD_GRADE}"`, and lowercased: `"not presented as externalization"`, `"demo-heuristic-only"`, `"tier-a"` | AC3's flag and guard are load-bearing text, not decoration |
| `…-001-26` | none of `externalization-grade`, `validated deep audit`, `assurance-grade result`, `gate cleared`, `>=80% achieved`, `precision gate cleared` (lowercased, artifact **and** live render) | your new self-audit prose must not reach for any of these |
| `…-001-03` partition rot check | `f"Unit count: {n}"` and each `partition_id[:12]` present; `"REUSING"` or `"Reused planner"` | keep the `Unit count:` label verbatim |
| `…-001-07` | partition plan contains `"no cross-partition"`, `"seam analysis"`, `"cross_partition"`, `"v2"` (case-insensitive) | the Scope-honesty section survives untouched |
| `…-001-06` budget rot check | `str(sized_ceiling)` present, **and** `"no numeric"` or `"no hardcoded"` | keep the OI3 invariant paragraph |
| `…-001-33` | `proof_run.py` contains driver tokens `ArgusAgent-FR-29/17/30/21`, `ArgusAgent-NFR-D1/S1`, `ArgusAgent-AR4`; the **test module docstring** contains `"The complete-the-declared-set matrix"`, `"(1) the reproducible dogfood execution"`, `"(6) the adjudication-ready findings layout"`, `"(7) the provisional-gate honesty"`; both files ≤1200 lines | if you edit either module docstring, these markers must survive |
| `…-001-18` | `source_file_count >= 60`, `total_loc >= 10000`, **`unit_count >= 3`**, `1 <= unit_count <= source_file_count` | ⚠️ the live tree yields **exactly 3** units — a knife edge. Your LOC edits feed the NFR-SC1 packer; if partitioning drops to 2, this goes red and it is **not** a licence to loosen the assertion. Regenerate, re-measure, and if it genuinely moves, report it |
| `…-001-31` / `…-001-13` | `deferred-work.md` contains `DF-6-6-A-P2`, `DF-7-2-A`, `DF-6-7-A`, `epic-7-minions-dogfood-precision`, `7-2-execute-minions-audit`, `7-1-minions-full-repo-partition-budget-sizing-plan`, and the five CC-3 field labels | your append-only additions must not disturb these; **append**, never restructure |

Also relevant to naming the tree truthfully — the real signature you are describing:

```python
enumerate_tracked_sources(repo_root, *, scope_prefix="argus", exclude_prefixes=("argus/tests/",))
```

### Known-red carve-out and pre-existing observations — do NOT silently fix, do NOT silently inherit

- **The 3 baseline failures** are yours (AC6) — but two of them predate this delta and must be reported as
  such.
- **`DOGFOOD_ArgusAgent_VERSION = "1.43.0"`** (`proof_run.py:163`) is stamped into the **SIGNED evidence
  bundle** as `argus_version`, while `pyproject.toml` and `argus/__init__.py` both declare `0.1.0`. That is
  a provenance falsehood inside signed evidence. **Do NOT fix it here** — changing it changes the bundle's
  content hash and the version token belongs with the packaging/release work. **File it (AC8).**
- **The gate-status string** rendered in §7 reads *"N=0 labeled cartridges populated"* because
  `build_dogfood_proof` passes `precision=Fraction(0,1), n=0` unconditionally, while `DF-6-6-A-P1` records
  `distinct_rule_class_count() == 5` and `populated_planted_defect_count() == 7`. It **understates**, so it
  is not an over-claim, but it is still a wrong number in a proof artifact. **Do NOT fix it here** (it
  would touch the 6.5/6.6 precision surface, which no AC in this story owns). **File it (AC8).**
- **`argus/pipeline.py` is 1199 lines** — one line under the NFR-M1 ceiling of 1200. `DF-8-2-A` /
  `DF-8-3-A` / `DF-8-3-C` all wait on its extraction. **This story does not touch it** (AC13).
- **`bmad-dev-loop-pack/`** is untracked and belongs to the orchestrator. Never `git add` it, never delete
  it, and exclude it from every figure you report.

---

## Acceptance Criteria

> The epic's seven ACs for Story 8.5 plus its precondition note are carried as **AC1, AC3, AC4, AC5, AC6,
> AC7, AC8, AC9, AC10**. **AC2, AC11, AC12, AC13** are **additions made at story design after measuring the
> artifacts against the real tree** — each is justified in *Variance from the epic, recorded*.

**The re-derived dogfood proof artifact — DR-10**

1. **Given** the Story 7.2 dogfood recorded `NOT_READY_FOR_RELEASE` / exit `2` at deep-% `13/15` with **0**
   verdict-eligible findings,
   **When** it is re-derived under **both** the amended decision table (8.1) **and** the amended
   critical-set eligibility (8.2),
   **Then** `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md` records **whatever outcome
   honestly results** from the live generator — the verdict token, the exit code, and **no predetermined
   value anywhere in this story, its tests, or the generator** (boundary **B1**),
   **And** it records **which decision row fired**, by its literal `DecisionRow` value
   (`row_1_below_floor` / `row_2_blocking_findings` / `row_3_gates_met` /
   `row_4_gate_unmet_no_findings`) — not a paraphrase and not a re-derivation from the verdict token,
   **And** it records **the inputs the row was computed from**: the deep count/total and exact `Fraction`
   ratio, the blocking-finding count, the **assessed population** (`coverage_scope`'s assessed
   deep/total + scope id + held-out count and reason when a narrowing occurred; the whole-ledger numbers
   and an explicit statement that **no narrowing occurred** when `coverage_scope is None`), and the
   critical-subsystem clause state,
   **And** the critical-subsystem clause disclosure distinguishes **a set that was non-empty and fully
   deep** from **a set that was empty** — a vacuously satisfied gate is visible, never implied (boundary
   **B3**, inversion **F1**); it names the critical-set size, the count heuristically excluded as
   ineligible under DR-5, and any `designated_but_unmatched` paths,
   **And** it states the ceiling honesty pair: the **frozen historical** `$X` = `DOGFOOD_BUDGET_CEILING`
   the run was executed under **and** the **live** 7.1 `sized_ceiling` from the same `build_full_repo_plan`
   call the generator already makes, and whether the run fits under **each** — so that the proof artifact
   and the budget artifact this story also regenerates cannot contradict each other (**D7**),
   **And** every figure is rendered from the live run object — **no figure is hand-written into the
   artifact and no historical figure is hardcoded into the generator.**

2. **Given** `enumerate_tracked_sources` defaults to `scope_prefix="argus"`, so the dogfood audits **this
   repository's own `argus/` package** and never Minions,
   **When** the artifact is re-derived,
   **Then** the artifact **names the tree it actually audited** — the git-tracked `argus/` package of the
   Agent-Argus repository, excluding `argus/tests/` — and **no rendered line claims Minions source was
   audited**: specifically the H1 title, the `## 1.` heading, the scope paragraph, the *"tracked Minions
   content"* clause and the *"audited BYTES are the real Minions source"* sentence,
   **And** the artifact **states plainly that this is a SELF-audit** — Argus auditing Argus — and that a
   self-audit is materially weaker evidence than the independent-repository run it supersedes; it is
   reportable, never presented as independent corroboration,
   **And** **every file path the artifact cites exists on disk**, verified by the dev: the two
   `tests/argus/test_dogfood_proof.py` citations and the `tests/security/test_argus_secret_containment.py`
   citation are corrected to real paths **or removed**, and the three `AUTO-GENERATED by …` provenance
   banners (proof ×1, partition ×1, budget ×1) name the real generator module,
   **And** the same treatment is applied to `render_partition_plan_markdown` and
   `render_budget_plan_markdown`, whose titles and `- Source files (tracked …)` line carry the identical
   falsehood,
   **And** the scope of this correction is **bounded and recorded**: only strings that are **emitted into a
   committed artifact**. Docstrings, comments and the `DogfoodProofError` message are **RS-4b's** and are
   left alone (**D3** measures the exact split).

3. **Given** the re-derivation lands on `RELEASE_READY`,
   **When** the artifact is published,
   **Then** it still carries the hard **`grade: demo-heuristic-only`** flag and the externalization guard
   verbatim,
   **And** it is **not** presented as externalization or assurance evidence anywhere — in the artifact, in
   the story record, or in the ledger notes: a green result from a Tier-A, zero-token, heuristic-only run
   is **reportable, never a clearance**,
   **And** the existing forbidden-phrase guard (`TC-ArgusAgent-DOGFOOD-001-26`) still passes over the new
   prose, and the new prose introduces no phrase of that class.

4. **Given** re-derivation may be a fresh run or analytic rather than a fresh run,
   **When** the method is chosen,
   **Then** **each** re-derived artifact **discloses which method produced it**: a re-run cites its commit
   pin and its budget ceiling; an analytic re-derivation names the inputs it folded and states plainly that
   **no new audit was executed**,
   **And** the disclosure is accurate per artifact — the live self-audit is a **re-run** (commit pin +
   `$X`), the historical Minions statement is **analytic** (**AC5**), and the two are never blended into
   one undifferentiated claim.

**The historical record — §3.4 evidence immutability**

5. **Given** the committed `minions-dogfood-proof.md` is today the **only** surviving record of the real
   Story-7.2 Minions run (135 files / 36712 LOC / commit `7f8e147`, bundle hash `c0c4c35e…`, and the three
   adjudication classes at counts 332 / 2289 / 285 that **DF-7-2-A's** human TP/FP adjudication is defined
   over), and regenerating that file **overwrites** it,
   **When** the artifact is re-derived,
   **Then** the original artifact's bytes are **preserved, not erased**, at
   `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof-story-7-2-superseded.md` — the original
   body **verbatim and unmodified** beneath a clearly delimited, hand-authored supersession header (the
   RS-3 *supersede-don't-erase* pattern),
   **And** that header carries the **analytic re-derivation** of the historical run through the real
   shipped `evaluate_verdict`: the inputs folded (`13/15` deep, 0 blocking, critical clause unmet), the
   determinable result — **`NOT_READY_FOR_RELEASE` / exit `2` is unreachable under the amended table for
   those inputs** — the two possible rows with the condition that selects each, and an explicit statement
   that **no new audit was executed over Minions and none can be, because Minions source is not in this
   repository**,
   **And** it carries a forward pointer to the re-derived artifact and a back pointer from it,
   **And** the header does **not** assert which of row 3 / row 4 actually fires — that requires the Minions
   ledger, and guessing it would be the over-claim this story exists to delete,
   **And** the file is **hand-authored, never generated**, so no generator carries frozen historical data.

**The other committed artifacts**

6. **Given** the epic's precondition demands an explicit statement about the pre-existing red tests,
   **When** this story completes,
   **Then** `minions-dogfood-partition-plan.md` and `minions-dogfood-budget-plan.md` are **re-derived from
   the live generator** and both pre-existing failures —
   `test_committed_partition_plan_artifact_exists_and_matches_live_derivation` and
   `test_budget_reuses_the_31_accountant_no_fork` — are **FIXED, deliberately, and recorded as
   pre-existing** (present on the clean tree at `ae5f00c`, subject = the very artifacts this story owns),
   **And** the story record states them **separately** from
   `test_committed_proof_artifact_exists_and_matches_live_run`, which **is** delta-caused (8.1+8.2 moved
   the live verdict) — the three are **not** absorbed into one undifferentiated "3 tests fixed" claim,
   **And** the two plan artifacts receive the same subject/provenance honesty treatment as the proof
   artifact (**AC2**).

7. **Given** `_bmad-output/reports/final-verdict.md` and `_bmad-output/audit-reports/final-verdict.md`,
   **When** inspected after this story,
   **Then** both agree with the amended contract — **neither asserts a blocking verdict alongside zero
   blocking findings**,
   **And** each is produced by a **recorded, reproducible CLI invocation** whose exact command line,
   working directory, exit code and resulting `Source State` / `Identity` line are written into the Dev
   Agent Record — not hand-edited, not partially edited, not patched,
   **And** the invocation regenerates the **sibling** reports already present in each directory
   (`coverage-ledger.md` in both; `security-review.md` in `_bmad-output/reports/`), so no directory is left
   half-fresh,
   **And** the record states which of the two is **published evidence** (`_bmad-output/audit-reports/` is
   git-tracked) and which is a **local run output** (`_bmad-output/reports/` is gitignored at
   `.gitignore:20`), because that distinction is what makes the first one matter,
   **And** neither regenerated report is cited anywhere as evidence that Argus is release-ready — see
   **AC3**'s standard, which applies to every green artifact this story produces.

**The ledger — append-only**

8. **Given** **DF-6-6-A** and **DF-7-2-A** depend on these artifacts,
   **When** the artifacts are re-derived,
   **Then** an **append-only** note in `deferred-work.md` records that the precision adjudication must run
   against re-derived artifacts, that the re-derived proof is a **self-audit of Argus with a different
   finding population** (2 / 19 / 76) than the Minions run it supersedes (332 / 2289 / 285), and that the
   Minions finding classes survive **only** at the preserved path from **AC5** — **the original entries are
   NOT rewritten** (§3.4),
   **And** an append-only **RS-4b progress note** records exactly which of its 15 enumerated
   `minions_core` references this story consumed and which remain, measured on the tree — so RS-4b's
   remaining scope stays honest,
   **And** two new defers are filed with the six CC-3 fields each: **(a)** the
   `DOGFOOD_ArgusAgent_VERSION = "1.43.0"` vs shipped `0.1.0` provenance mismatch stamped into the signed
   evidence bundle, `target_story` = `9-2-…`; **(b)** the structural fragility that the committed-artifact
   rot checks re-break on any later commit that changes `argus/**` LOC composition or partition membership
   (they were red across four commits before this story), with the measured mechanism named,
   **And** no existing ledger entry is edited, reordered or deleted.

9. **Given** the ≥80 %-precision externalization gate,
   **When** this story completes,
   **Then** it stays **PROVISIONAL** — `protocol_cleared` is never passed `True`, the 6.5
   `precision_gate_status()` marker is not flipped, no ≥80 % number is presented as authoritative, and the
   §7 provisional-gate section of the artifact survives the re-derivation intact,
   **And** `tests/test_dogfood_proof.py::test_red_first_gate_not_silently_flipped` and
   `::test_precision_gate_stays_provisional` still pass unchanged.

**The delta's own acceptance test — Inversion F5**

10. **Given** the operator command that triggered this entire amendment — `argus audit .` on ArgusAgent,
    which returned `verdict=NOT_READY_FOR_RELEASE deep_ratio=11/28 blocking_findings=0`,
    **When** that exact command is re-run after Stories 8.1-8.4,
    **Then** the reported symptom — **a blocking verdict carrying zero findings** — is **not
    reproducible**, and the actual result is recorded verbatim (stdout summary line + exit code),
    **And** it is re-run at **both** coverage scopes — the current default (`application`) **and**
    `--coverage-scope repository`, which is the population under which the symptom was originally measured
    — because passing only under the narrowed default would leave the F5 evidence one flag away from
    vacuous,
    **And** both results are recorded in the Dev Agent Record **and** summarised in the ledger note from
    **AC8**, so the evidence outlives this story file,
    **And** if either invocation *does* reproduce the symptom, the story **HALTS and reports it** — it is
    not worked around, not re-scoped, and not fixed here: it would mean an earlier Epic-8 story slipped,
    which is precisely why 8.5 is sequenced last.

**Non-regression, purity and fences**

11. **Given** the rot checks are the only thing standing between a stale artifact and a silent
    contradiction,
    **When** the tests are updated,
    **Then** the three baseline failures are green **without weakening any existing assertion** — no
    assertion is deleted, loosened to a substring that cannot fail, or converted to a skip,
    **And** new tests continue the existing verification area at **`TC-ArgusAgent-DOGFOOD-001-35`** and
    upward (measured: `-01` … `-34` are taken; do **not** restart the sequence and do **not** reuse an id),
    **And** new coverage pins, at minimum: (a) the artifact discloses a `DecisionRow` value that **matches
    the live run's** `verdict.decision_row`; (b) the artifact names **no** Minions-source-audited claim and
    **every** path it cites resolves on disk; (c) the end-to-end guard — the real dogfood run may **never**
    yield `NOT_READY_FOR_RELEASE` while `blocking_finding_count == 0`, asserted on the existing
    module-scoped `dogfood_proof` fixture so it costs no extra runtime; (d) the ceiling honesty pair from
    **AC1**; (e) the preserved supersession file from **AC5** exists and contains the original artifact's
    distinctive bytes,
    **And** at least the artifact-content pins are demonstrated **RED first** against the pre-fix artifact
    or a deliberately-stale variant, with the failure output pasted verbatim into the Dev Agent Record —
    an assertion never shown to fail is not a rot check.

12. **Given** the architectural rules this repository enforces,
    **When** the work lands,
    **Then** the renderers stay **PURE** (no I/O, no clock, no `uuid4`, no `getpid()`, no iteration-order
    dependence) and remain deterministic and byte-stable for the same tracked content — proven by the
    existing `test_full_repo_plan_is_deterministic_and_byte_reproducible` and
    `test_dogfood_is_100pct_reproducible_byte_identical`,
    **And** ratios remain exact `Fraction`, never `float` (AR4),
    **And** no artifact gains a source byte or a secret value — only provenance, counts, rule-ids and
    repo-relative POSIX locators (NFR-S1); the existing containment assertions still pass,
    **And** `argus/dogfood/proof_run.py` and `argus/dogfood/partition_plan.py` each stay **≤1200 lines**
    (NFR-M1; measured today at 749 and 612), as do both test modules (605 / 509),
    **And** any new field on `DogfoodProofRun` / the plan result carries a **default**, so no existing
    construction site breaks,
    **And** the final state is **`1150 passed, 0 failed`** or better — every one of the 1147 baseline
    passes still passes, the 3 baseline failures are green, and `python -m mypy argus` is clean; the exact
    counts are pasted into the Dev Agent Record.

13. **Given** this is the last story of Epic 8 and the epic must close without collateral,
    **When** the work lands,
    **Then** these are **NOT modified** and each is verified untouched by `git diff --stat` at the end:
    `argus/verdict/**`, `argus/ledger/**`, `argus/reports/**`, `argus/pipeline.py`, `argus/pipeline_persist.py`,
    `argus/cli.py`, `argus/__init__.py`, `CHANGELOG.md`, `README.md`, `pyproject.toml`, `action.yml`,
    `.github/workflows/**`, and `bmad-dev-loop-pack/**`,
    **And** **`sprint-status.yaml` is edited only at the `8-5-…` key** (plus its own `last_updated`) — no
    other story key, no epic key,
    **And** no `.md` file under `_bmad-output/design-artifacts/ArgusAgent/` is modified except
    `minions-dogfood-proof.md`, `minions-dogfood-partition-plan.md`, `minions-dogfood-budget-plan.md`,
    `deferred-work.md`, this story file, and the **new** `minions-dogfood-proof-story-7-2-superseded.md`,
    **And** the dispositions of the five carried deferred items are recorded explicitly: **RS-4b**
    partially consumed and progress-noted (AC8); **DF-8-2-A / DF-8-3-A / DF-8-3-C** untouched (they gate on
    a `pipeline.py` extraction this story does not perform); **DF-8-4-A / DF-8-4-B / DF-8-4-C / DF-8-4-D**
    untouched (Epic-9 / `test_release_note.py` / `cli.py` surfaces, all fenced above).

---

## Tasks / Subtasks

- [x] **Task 0 — Re-derive before you change anything (all ACs).** Do NOT trust this story's tables.
  - [x] `git status --porcelain` + `git rev-parse HEAD` — confirm `be9d744` and the lone untracked
        `bmad-dev-loop-pack/`. Note that `git diff HEAD` is **empty** and is not your instrument here.
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/ --tb=no` — record the exact baseline pass/fail
        counts and the failing node ids **before** you touch a file.
  - [x] Call `build_dogfood_proof('.')` and `run_dogfood('.', …)` in place; capture the full
        `DogfoodProofRun` **and** `result.verdict` (`decision_row`, `coverage_scope`,
        `critical_subsystems_not_deep`, `deep_count`/`total_count`, `blocking_finding_count`).
  - [x] Call `build_full_repo_plan('.')`; capture unit ids, `total_credits`, `sized_ceiling`,
        `build_cost_proxy`, `baseline_ratio`.
  - [x] Read the persisted `CriticalSubsystemSet` out of the snapshot's `.argus/state/` via
        `ApaaStoreReader` + `CRITICAL_SUBSYSTEMS_PRODUCER` (recipe in **Story Context §G**).
  - [x] Fold the historical 7.2 inputs through the real `evaluate_verdict` for **both** critical-clause
        branches (**Story Context §B**).
  - [x] Record the method (in place, which tree, which instruments) in the Dev Agent Record.
- [x] **Task 1 — Preserve the historical record FIRST (AC5).** Before a single regeneration.
  - [x] Copy `minions-dogfood-proof.md` byte-for-byte to
        `minions-dogfood-proof-story-7-2-superseded.md`; prepend the hand-authored supersession header
        (analytic re-derivation, forward pointer, the "no new audit was executed over Minions" statement,
        and the explicit refusal to pick row 3 vs row 4).
  - [x] Verify the original body survives verbatim below the header (diff the tail against
        `git show HEAD:…/minions-dogfood-proof.md`).
- [x] **Task 2 — Make the generators tell the truth (AC1, AC2, AC4), RED-first where testable.**
  - [x] `argus/dogfood/proof_run.py` — correct the rendered subject/provenance/citation strings; add the
        decision row, the assessed-population disclosure, the critical-clause disclosure (non-empty-and-deep
        vs empty, set size, DR-5-excluded count, `designated_but_unmatched`), the ceiling honesty pair, and
        the re-run method disclosure. New `DogfoodProofRun` fields carry defaults.
  - [x] `argus/dogfood/partition_plan.py` — correct the two titles, the `tracked … content` clause, the
        `- Source files (tracked …)` line and the two `AUTO-GENERATED by …` banners.
  - [x] Stay inside the **D3** boundary: emitted-into-artifact strings only. No docstring/comment sweep.
  - [x] **Check every edit against Story Context §H** — the strings and heading stems the existing tests
        already pin. Turning 3 reds into 8 here is the predictable failure mode.
  - [x] Confirm both files remain ≤1200 lines and `mypy argus` is clean.
- [x] **Task 3 — Regenerate the three dogfood artifacts LAST, after every source edit (AC1, AC2, AC6).**
  - [x] Re-run the generators on the final tree and write
        `minions-dogfood-proof.md` / `minions-dogfood-partition-plan.md` / `minions-dogfood-budget-plan.md`.
  - [x] Do **not** hand-edit any of the three afterwards. If a line is wrong, fix the renderer and
        regenerate.
  - [x] Re-run `tests/test_dogfood_plan.py tests/test_dogfood_proof.py` — the three baseline reds must be
        green.
- [x] **Task 4 — Regenerate the verdict reports (AC7).**
  - [x] `python -m argus.cli audit . --report-dir _bmad-output/audit-reports` (tracked / published).
  - [x] `python -m argus.cli audit . --reports final-verdict,coverage-ledger,security-review --report-dir _bmad-output/reports`
        (gitignored / local) — match the three files already present.
  - [x] Record both command lines, exit codes, and the resulting `Source State` / `Identity` lines.
  - [x] Confirm by `grep` that neither `final-verdict.md` still pairs a blocking verdict with
        `Blocking Findings: 0`.
- [x] **Task 5 — Inversion F5 (AC10).**
  - [x] `python -m argus.cli audit .` and `python -m argus.cli audit . --coverage-scope repository`.
  - [x] Paste both stdout summary lines and exit codes verbatim.
  - [x] If either reproduces `NOT_READY_FOR_RELEASE` with `blocking_findings=0` — **HALT and report**.
- [x] **Task 6 — Tests (AC11), RED-first.**
  - [x] Extend `tests/test_dogfood_proof.py` / `tests/test_dogfood_plan.py` from
        `TC-ArgusAgent-DOGFOOD-001-35` upward with the five pins in AC11.
  - [x] Demonstrate the artifact-content pins RED against a deliberately-stale variant; paste the failure
        output verbatim.
  - [x] Verify no existing assertion was deleted or loosened (`git diff` the two test files and say so).
- [x] **Task 7 — Ledger (AC8).** Re-read `deferred-work.md` immediately before writing; append one dated
      section containing the DF-6-6-A/DF-7-2-A re-targeting note, the RS-4b progress note (which of the 15
      consumed), and the two new defers with six CC-3 fields each. Rewrite nothing.
- [x] **Task 8 — Fences and whole-system proof (AC12, AC13).**
  - [x] `git diff --stat` — verify every fenced path in AC13 is untouched.
  - [x] Full suite + `mypy argus`; paste exact counts.
  - [x] Record the five carried deferred-item dispositions.

### Review Findings

> **Code review — iteration 1, 2026-08-07. Verdict: CONCERNS.** Every finding below is
> **Low** severity and every one is an unambiguous patch. Nothing here disputes the delta's
> correctness: the reviewer independently re-ran the full suite (**1157 passed / 0 failed /
> 0 skipped**, progress-character census `Counter({'.': 1157})`, exit 0), `python -m mypy argus`
> (**clean, 69 files**), re-rendered all three dogfood artifacts from the live generators and
> confirmed each is **byte-identical** to its committed copy (no hand-editing anywhere),
> re-ran `argus audit .` at **both** coverage scopes and reproduced the F5 result verbatim,
> re-measured the RS-4b split (**exactly 9 `minions_core` refs remain, at exactly the 9 lines
> the ledger names; `partition_plan.py` is at zero**), confirmed `git diff -U0` shows **zero
> deleted lines** in both test modules, confirmed the preserved Story-7.2 record ends with the
> original 6994 bytes **verbatim**, and independently folded `13/15` + 0 blocking through the
> real `evaluate_verdict` for both branches (row 4 / exit 3 and row 3 / exit 0 — matching the
> supersession header exactly). AC1–AC13 are all materially met. Fix the four items below and
> this is a `pass`.

- [x] [Review][Patch] The republished §7 `N=0` understatement was neither fixed nor filed — no ledger trace exists [argus/dogfood/proof_run.py:727-729 → minions-dogfood-proof.md:87]
      — **Rule violated:** the story's own Known-red carve-out directs *"It is still a wrong number in a proof artifact. **Do NOT fix it here** … **File it (AC8)**"*; and the epic's standard that a published artifact must not state an unmeasured figure. `build_dogfood_proof` passes `precision=Fraction(0, 1), n=0` unconditionally, so the regenerated artifact republishes *"N=0 labeled cartridges populated"* while the measured corpus is 5 distinct classes / 7 populated rows. The Completion Notes argue this is covered by `DF-6-6-A-P1` / `DF-7-2-A`; **verified and it is not** — `deferred-work.md:362-394` records the corpus counts (`distinct_rule_class_count() == 5`, `populated_planted_defect_count() == 7`) but never records that the published proof artifact renders `N=0`. AC8's enumerated two defers *are* satisfied, and the decision *was* recorded, which is why this is Low and not a blocker — but the known-wrong published number now survives only in a closed story's notes. **Fix:** append `DF-8-5-C` (append-only, six CC-3 fields) naming the unconditional `precision=Fraction(0, 1), n=0` call site, the measured true values, why it understates rather than over-claims, and a `target_story`. No code change, no regeneration.

- [x] [Review][Patch] The artifacts publish an exclusion prefix that does not exist on disk, and the AC11b citation guard structurally cannot catch it [argus/dogfood/proof_run.py:189 + argus/dogfood/partition_plan.py:121; guard at tests/test_dogfood_proof.py:667]
      — **Rule violated:** AC2 (*"every file path the artifact cites exists on disk"*) and AC11b (*"every path it cites resolves on disk"*). All three artifacts render *"excluding `argus/tests/`"* (proof §1, both plan Provenance lines). **`argus/tests/` does not exist** — tests are flat under `tests/`, as the story's own Project Structure Notes state. The clause therefore tells a reader that a test subtree was held out of the 69-file population when nothing was held out at all. The new guard misses it because `_PATH_TOKEN = re.compile(r"`([A-Za-z0-9_.\-/]+\.(?:py|md|yaml|toml))(?::\d+)?`")` only matches tokens ending in a file suffix, so **directory citations are outside the guard AC11b demands** — the guard is narrower than the AC it implements. **Fix:** extend `_PATH_TOKEN` (or add a second pattern) to backticked directory-shaped tokens, and either render the exclusion with its measured effect (*"excluding `argus/tests/` — 0 tracked files matched"*) or drop unmatched prefixes from the rendered clause. Do **not** close this by special-casing `argus/tests/` in the guard.

- [x] [Review][Patch] `live_sized_ceiling` uses `0` as an "absent" sentinel, so a genuinely-zero sizing would be published as "not supplied" [argus/dogfood/proof_run.py:257 and :927]
      — **Rule violated:** the module's own better pattern and the epic's don't-assert-what-you-didn't-measure rule. `CostSummary.live_sized_ceiling: int = 0` collapses *"no live sizing was supplied"* and *"the live sizing is 0"* into one value, and `_render_ceiling_pair` branches on `if cost.live_sized_ceiling:` — so a zero-credit derivation would render *"**Live 7.1 sizing:** not supplied to this derivation"*, a false statement about what the generator was actually given. This is inconsistent with the correct treatment two dataclasses up: `CriticalClauseDisclosure.set_retrieved` exists precisely so an unread set is never reported as an empty one (and the docstring says so). **Fix:** make it `live_sized_ceiling: int | None = None` (or add an explicit `live_sizing_supplied: bool`) and branch on `is not None`. Unreachable on this tree today; the point is that the sentinel encodes the same ambiguity the story elsewhere refuses.

- [x] [Review][Patch] The optional critical-set read-back can abort the whole proof run, and its first-match-wins scan has no recency ordering [argus/dogfood/proof_run.py:575-607]
      — **Rule violated:** separation of concerns / graceful degradation, and the disclosure's own claim to name *"the SAME set the gate keyed on"*. Two mechanisms: **(a)** `_read_critical_subsystem_set` scans **every** `state/*.json` and re-raises **any** `read_envelope` failure as a fatal `DogfoodProofError` (`:594`), including a hash-mismatch on an envelope that has nothing to do with the critical set — so a store the 4.2 lint would have reported as `integrity_consistent: False` in §3 can now no longer produce the artifact that reports it. The class already models the graceful case (`set_retrieved=False` → *"could NOT be read back"*), which is strictly better for an artifact whose purpose is reporting store state. **(b)** `for child in sorted(state_dir.glob("*.json"))` returns the **first** producer match; filenames are content-addressed, so `sorted` gives lexicographic — not recency — order. `materialize_snapshot` does `dest.mkdir(exist_ok=True)`, so a reused snapshot dir carrying two critical-subsystem envelopes would silently disclose whichever hash sorts first. **Fix:** restrict the raise to the envelope that actually claims `CRITICAL_SUBSYSTEMS_PRODUCER` and degrade everything else to `set_retrieved=False` with a rendered reason; and either raise a typed error on >1 producer match or select the envelope via the run's own result rather than a directory scan.

- [x] [Review][Patch] `proof_run.py` is now 1154/1200 lines and the rejected renderer extraction has no ledger id [argus/dogfood/proof_run.py:1-1154]
      — **Rule violated:** SRP / separation of concerns, and this repo's own established mechanism for a module approaching NFR-M1. The **rejection itself is judged sound for this story** — AC13 does not authorise the restructure, the epic's last story is the wrong place for it, and the tradeoff is recorded honestly. But the module now carries constants, five value dataclasses, the impure git/snapshot/store shell, the pure cost accountant and ~390 lines of pure renderer, with **46 lines of headroom**, and the observation lives only in a closed story's Completion Notes. The repo's actual mechanism is a ledger id: `DF-8-2-A` exists for exactly this shape (`pipeline.py` at 1199), and this story filed `DF-8-5-B` for a smaller DX issue. Note also that the stated blocker is softer than recorded — extracting the pure renderers to `argus/dogfood/proof_render.py` needs the dataclasses moved to a sibling module and **re-exported** from `proof_run.py`, which preserves the public import surface without a circular import. **Fix:** file a defer (six CC-3 fields) for the renderer extraction with that mechanism named, `target_story` = the first story that edits the module.

### Review Findings — resolution (dev fix iteration 1, 2026-08-07)

All five findings are addressed. None is silently dropped; none is closed by weakening an assertion. Three
were fixed in code and each behavioural fix was demonstrated **RED-first** (failure output in the Debug Log
below); two were closed the way the review itself prescribed — with a ledger id. Everything below was
**re-measured by this session**, not carried over.

**F1 — the republished `N=0`: FILED, not fixed (as the story's own carve-out directs).** `DF-8-5-C` appended
to `deferred-work.md` with the six CC-3 fields. It names the unconditional call site
(`argus/dogfood/proof_run.py:764-765` — `precision_gate_status_for(precision=Fraction(0, 1), n=0,
provisional=True, …)`, literal arguments, no measurement), the exact rendered line
(`minions-dogfood-proof.md:87`), and the true values **re-measured by EXECUTING the shipped registry** in
place rather than reading them off `DF-6-6-A-P1`: `distinct_rule_class_count() == 5`,
`populated_planted_defect_count() == 7`. It states the direction explicitly — the figure **understates**, so
it can never make the provisional gate look cleared — and gives a `Close =` that keeps `protocol_cleared`
false. The reviewer's premise was verified before filing: `deferred-work.md:362-394` does record the corpus
counts and does **not** record that the published artifact renders `N=0`. No code change, no regeneration.

**F2 — the non-existent `argus/tests/` exclusion + the directory-blind guard: FIXED, both halves.** The
generator half was closed by MEASUREMENT, not by prose: `build_dogfood_proof` now records
`DogfoodProofRun.effective_exclude_prefixes` = `effective_exclusions(enumerate_tracked_sources(root,
exclude_prefixes=()), _DEFAULT_EXCLUDE_PREFIXES)` — the subset of configured prefixes that measurably held
≥1 tracked file out — and `_audited_tree_clause` renders **that**, mirroring the treatment
`partition_plan.py` already carries. Measured on this tree the subset is **empty** (`argus/tests/` held out
**0** files, which is precisely the finding), so all three artifacts now render **no** exclusion clause;
`grep` over the three regenerated artifacts returns **0** occurrences of `argus/tests`. The configured
prefix is still recorded on the run, so nothing was hidden — only the unmeasured claim was withdrawn. The
guard half was closed **generically**: `tests/test_dogfood_proof.py` gains `_DIR_TOKEN`
(`` `segment(/segment)*/` ``) and `_cited_paths_resolve` now resolves directory citations with `is_dir()`
alongside the file-suffixed ones. Nothing about `argus/tests/` is special-cased — the guard is now as wide
as AC11b's wording. **RED-first is the real pre-fix committed artifact**, pasted verbatim below.

**F3 — the `0`-as-absent live-sizing sentinel: FIXED.** `CostSummary.live_sized_ceiling` is `int | None =
None`, `cost_summary(*, live_sized_ceiling: int | None = None)` folds the second fit only when a sizing was
supplied, and `_render_ceiling_pair` branches on `is not None`, so a derivation given a genuinely-zero
ceiling now publishes that zero with its fit verdict instead of the false *"not supplied to this
derivation"*. This matches `CriticalClauseDisclosure.set_retrieved`, which exists to refuse exactly this
ambiguity. Pinned by `TC-ArgusAgent-DOGFOOD-001-44`, RED-first against the restored `int = 0` body.

**F4 — the fatal optional read + the unordered first-match-wins scan: FIXED, both mechanisms.**
`_read_critical_subsystem_set` returns `(CriticalSubsystemSet | None, measured_reason)`. **(a)** An
unreadable `state/*.json` is now **degraded**, not fatal: the locator and exception type are collected into
the reason, the scan continues, and if no producer match is found the run reports `set_retrieved=False`
with that reason **rendered into the artifact** (the `retrieval_note` field the class already carried is now
wired end-to-end: `_DogfoodExecution.critical_subsystems_note` → `CriticalClauseDisclosure.retrieval_note` →
`_render_critical_clause`). A store the 4.2 lint would report as `integrity_consistent: False` can once
again produce the artifact that reports it. The typed `DogfoodProofError` is now raised only for an envelope
that **actually claims** `CRITICAL_SUBSYSTEMS_PRODUCER` and carries a payload that is not a
`CriticalSubsystemSet` — the case where the failure is unambiguously ours (AR10 preserved). **(b)** All
producer matches are collected and **>1 raises** a typed `DogfoodProofError` naming the count and the
`.argus/`-relative locators, because the filenames are content-addressed and `sorted` is lexicographic, not
recency — disclosing whichever hash sorts first would name a set the gate may never have keyed on. Pinned by
`TC-ArgusAgent-DOGFOOD-001-43` (all three legs: degrade; still find the real set despite the unreadable
sibling; refuse ambiguity), RED-first against the restored fatal body.

**F5 — the rejected renderer extraction: FILED, and the rejection is re-affirmed with the record corrected.**
`DF-8-5-D` appended with the six CC-3 fields, `target_story` = *the first story that edits
`argus/dogfood/proof_run.py` for any reason*, severity 🟠. It records the measured composition (constants +
typed error, five frozen dataclasses, the impure git/snapshot/store shell, the pure cost accountant, ~390
lines of pure renderer) and **corrects the blocker this story previously recorded**: the stated circular
import is softer than claimed — extracting the pure renderers to `argus/dogfood/proof_render.py` needs the
five dataclasses moved to a sibling and **re-exported** from `proof_run.py`, which preserves every existing
`from argus.dogfood.proof_run import …` with no cycle. It also adds a constraint the review did not have,
measured here: the dogfood plans over `argus/**` itself, so **adding a module changes the partition input
set** while `TC-ArgusAgent-DOGFOOD-001-18` pins `unit_count >= 3` and this tree yields exactly **3** — the
extraction must regenerate all three artifacts in the same change and re-measure, and a drop to 2 units is a
finding to report, never a licence to loosen the pin. **The extraction was still not performed here**: AC13
does not authorise it, the reviewer judged the rejection sound for this story, and doing it during a
five-Low-finding fix round would put a knife-edge partition figure at risk for no in-scope benefit.

> ⚠️ **Honest disclosure the next reviewer must weigh, stated rather than buried.** These fixes grew
> `argus/dogfood/proof_run.py` from **1154 to 1196 lines** — NFR-M1 headroom is now **4 lines**, down from
> 46. It does **not** breach the 1200-line fence, and nothing else was trimmed to fit: the only prose
> shortened was prose this same session had just written (two comment blocks and one docstring paragraph
> added minutes earlier), and the parallel `matches` / `payloads` lists were folded into one list of tuples,
> which is better code independently. No pre-existing comment, docstring, assertion or behaviour was removed
> to buy room. The situation `DF-8-5-D` describes is therefore materially more urgent than when the review
> wrote it — which is why it is filed at 🟠 rather than 🟢, and why this paragraph exists instead of a
> quiet line-count edit.

### Review Findings — iteration 2, 2026-08-08. Verdict: PASS

> **All five iteration-1 findings are adjudicated GENUINELY RESOLVED — none papered over.** Everything
> below was **re-measured by this reviewer on the working tree**, never read off the story. Independent
> evidence: full suite `PYTHONIOENCODING=utf-8 python -m pytest tests/ -q --tb=short` → **exit 0**, progress
> census `Counter({'.': 1160})` — **1160 passed / 0 failed / 0 skipped**, zero `F`/`E`/`s`/`x`/`X`;
> `python -m mypy argus` → *Success: no issues found in 69 source files*; all three dogfood artifacts
> **re-rendered from the live generators and sha256-compared byte-for-byte to their committed copies —
> IDENTICAL** (`minions-dogfood-proof.md` `1a709e6ea9482291`, `…-partition-plan.md` `7b018e3869dd3946`,
> `…-budget-plan.md` `9613bd285a1b7b25`), so every published figure is a measured one; `argus audit .`
> re-run at **both** scopes with the exit code captured directly (not through a pipe): `RELEASE_READY`
> **exit 0** / `INSUFFICIENT_COVERAGE` **exit 3** — the F5 symptom is not reproducible; the AC5 supersession
> tail is byte-identical to `git show HEAD:…/minions-dogfood-proof.md` (**6994** chars) and the analytic
> fold was reproduced independently through the shipped `evaluate_verdict` (`row_4_gate_unmet_no_findings`
> /exit 3 · `row_3_gates_met`/exit 0, `NOT_READY_FOR_RELEASE` unreachable); AC13 fences all clean by
> `git diff --stat`, `sprint-status.yaml` touched only at the `8-5-…` key + `last_updated`.

**Per-finding adjudication.**

- **F1 → FILED, honestly.** `DF-8-5-C` exists with the six CC-3 fields. Every fact it cites was re-verified:
  `argus/dogfood/proof_run.py:764-765` is exactly `precision=Fraction(0, 1),` / `n=0,` (literals, no
  measurement); `minions-dogfood-proof.md:87` is exactly the `Gate status:` line carrying *"N=0 labeled
  cartridges populated"*; and executing the shipped registry here returns
  `distinct_rule_class_count() == 5` / `populated_planted_defect_count() == 7`. Deferring is **defensible** —
  the story's own carve-out directs file-don't-fix and the review's own prescribed remedy was a ledger id;
  the `target_story` (first story editing the 6.5/6.6 precision surface) is correctly aimed.
- **F2 → FIXED, verified hardest.** The emptiness is **measured truth, not prose**: `git ls-files argus/tests`
  returns **0** and no such directory exists; a live re-derivation prints `effective_exclude=()` for **both**
  generators; `grep argus/tests` over the three artifacts returns **0 / 0 / 0**. **No information was
  dropped:** the clause now reads *"the git-tracked `argus` package tree"* / *"Source files (tracked
  `argus/`): **69***" and 69 **is** every tracked `.py` under `argus/` (counted independently), so the
  population statement is now exactly complete — the removed clause was the thing that misinformed, and the
  configured set is still recorded on the run and asserted by `TC-…-42`. The `_DIR_TOKEN` guard was proven
  RED **against real pre-fix data by this reviewer**: run over the three `HEAD` artifacts it flags the
  directory citations `minions_core/` and `minions_core/apaa/`, which the old suffix-only `_PATH_TOKEN` was
  structurally blind to; run over the three current artifacts it returns `[]` for all three.
- **F3 → FIXED.** `live_sized_ceiling: int | None = None`, `cost_summary(*, live_sized_ceiling: int | None)`
  folds the second fit only under `is not None`, `_render_ceiling_pair` branches on `is not None`. `TC-…-44`
  pins absent→`None`, supplied-zero→`0`, and that the two render differently.
- **F4 → FIXED, both mechanisms.** `_read_critical_subsystem_set` returns `(set | None, reason)`; an
  unreadable envelope is collected and the scan continues; the typed `DogfoodProofError` now fires only for a
  malformed payload under the actual producer or for **>1** producer match (naming the count and
  `.argus/`-relative locators). `retrieval_note` is wired end-to-end into `_render_critical_clause`.
  `TC-…-43` covers all three legs.
- **F5 → FILED, and the ledger entry is better than the review asked for.** `DF-8-5-D` carries the six CC-3
  fields, the measured composition, the **corrected** blocker (dataclasses to a sibling + re-export, no
  cycle) and a constraint the review did not have (the `unit_count >= 3` knife edge). Severity raised to 🟠
  with the 4-line headroom disclosed in the open. Deferring is defensible; AC13 does not authorise the
  restructure.

**Disclosure claims verified with git, not taken on trust.** `git diff -U0 HEAD` over
`tests/test_dogfood_proof.py` + `tests/test_dogfood_plan.py` shows **zero** deleted lines. `git diff -U0
HEAD -- argus/dogfood/proof_run.py` shows exactly **22** deleted lines and each was read: all are the
false-subject / false-citation strings AC2 requires replacing plus three signature lines — **nothing
pre-existing was trimmed to buy room** under the 1196/1200 fence. `TC-…-41` is **strengthened, not
loosened**: it now derives the expected subject line from the recorded scope + `effective_exclude_prefixes`,
**adds** a negative (a configured-but-unmatched prefix must not appear) and cross-checks
`effective_exclude_prefixes` against a fresh un-excluded enumeration.

Two **Low, non-blocking** items remain. Neither withholds the pass; both are for the next editor of these
files.

- [ ] [Review][Patch] The RS-4b progress note publishes a post-change line number that fix iteration 1 made stale [_bmad-output/design-artifacts/ArgusAgent/deferred-work.md:855 → argus/dogfood/proof_run.py:666]
      — **Rule violated:** AC8 (*"an append-only RS-4b progress note … measured on the tree — so RS-4b's
      remaining scope stays honest"*) and this epic's own standard that a published figure is a measured one.
      The note is explicitly framed as a post-change measurement (*"Re-measured on this tree after the
      change"*) and cites `dogfood/proof_run.py:632` for the remaining `DogfoodProofError` operator message.
      Fix iteration 1 inserted 42 lines above it: the reference now lives at **`proof_run.py:666`**, and
      line 632 is an unrelated f-string. Measured by this reviewer with
      `grep -rn "minions_core" argus --include=*.py`; the rest of the note is **correct** — 9 references
      remain (11 hits minus the 2 in the Epic-9-owned `argus/audit/minions_llm_adapter.py`, which RS-4b
      excludes), in exactly the 9 named files, with 8 of the 9 line numbers exact. The same stale `:632`
      appears in this story's Completion Notes (AC8/D3 paragraph). **Low** because the file + string identify
      the reference unambiguously and RS-4b's remaining scope is unchanged in substance. **Fix:** append a
      one-line correction to the ledger (append-only — do not rewrite the note) recording `:632 → :666`, or
      re-measure the note when RS-4b is executed.

- [ ] [Review][Patch] `build_dogfood_proof` records the artifact's subject from a module constant instead of the value the enumeration actually used [argus/dogfood/proof_run.py:791-796]
      — **Rule violated:** DRY / single-source-of-truth, and the asymmetry with the better pattern this same
      change established one module over. `build_full_repo_plan` records `scope_prefix=scope_prefix` /
      `exclude_prefixes=tuple(exclude_prefixes)` — the **arguments the enumerator was actually given**
      (`partition_plan.py:486-488`), so the rendered subject cannot drift from the derivation. The proof side
      instead writes `scope_prefix=_DEFAULT_SCOPE_PREFIX, exclude_prefixes=_DEFAULT_EXCLUDE_PREFIXES` back
      onto the run. **Not a falsehood today** — neither `run_dogfood` nor `build_dogfood_proof` accepts a
      scope parameter, so the constant *is* the value used, and `TC-…-42` pins
      `exclude_prefixes == _DEFAULT_EXCLUDE_PREFIXES`. It is a latent trap of exactly the shape AC2 exists to
      delete: the first person to add a `scope_prefix=` parameter to either entry point gets an artifact that
      names a tree the run did not read, with no test to catch it. **Fix:** thread `scope_prefix` /
      `exclude_prefixes` through `run_dogfood` / `build_dogfood_proof` as parameters defaulting to the module
      constants and record the parameters, mirroring `build_full_repo_plan`. Natural companion to
      `DF-8-5-D`'s extraction.

---

## Dev Notes

### LOCKED decisions taken at story design — with rationale (record these; do not re-litigate)

**D1 — The re-derivation is a RE-RUN for the live artifact and ANALYTIC for the historical one, and the two
are kept in separate files.** Considered and rejected: (a) *analytic only*, which would leave the three
committed rot checks red and the artifact permanently divorced from its generator — the checks compare the
committed markdown against a **live** run, so nothing analytic can turn them green; (b) *re-run only*,
which silently destroys the Minions record (**D4**); (c) *both inside one generated file*, which would
require hardcoding the frozen 7.2 figures into `proof_run.py` — a generator carrying historical evidence
data is exactly the fork/staleness shape AR7 exists to prevent. The live re-run satisfies the rot checks
and DR-10's "re-derive"; the analytic fold satisfies DR-10's "or explicitly re-affirm" for the run that
cannot be re-executed. AC4 makes each file say which it is.

**D2 — The subject correction is IN SCOPE and is not optional.** Best practice says a re-derivation story
re-runs a generator and stops. The project standard wins and is explicit: the epic's own outcome statement
requires an operator to find *"no published Argus artifact contradicting the shipped contract"*, and 8.4's
**D3** already established for this codebase that a persisted artifact must not assert a falsehood. The
generator today renders *"the frozen audit over the REAL Minions repo"* about a self-audit of `argus/`, and
cites three file paths that do not exist. Regenerating without fixing that does not preserve a pre-existing
falsehood — it **publishes a fresh one, dated today, authored by this story.** That is a worse position
than leaving the artifact stale, and it is the precise defect class Epic 8 exists to delete.

**D3 — The RS-4b boundary, measured on the tree, so the two stories do not collide.** RS-4b enumerates 15
`minions_core` references across 8 files and states its sweep must **follow** 8.5. This story consumes
exactly **6 of the 15** — the ones that are emitted into a committed artifact:
`partition_plan.py:481, 490, 554` and `proof_run.py:597, 609, 610`. It leaves the other **9**:
`audit/deep_audit.py:21`, `audit/ports.py:4`, `cost/budget_governor.py:15`, `proof_run.py:52`,
`proof_run.py:53`, `proof_run.py:486` (a `DogfoodProofError` operator message), `governance/escalation.py:35`,
`store/envelope.py:25`, `verdict/prosecutor.py:36`. Separately, the bare-word *"Minions"* subject claims
(`proof_run.py:594, 599, 605, 613, 672, 675, 682, 695` and `partition_plan.py:478, 483, 551`) are **not on
RS-4b's list at all** — they are wholly this story's. Rule of thumb for the dev: **if the string reaches a
committed `.md`, it is yours; if it only ever reaches a Python reader, it is RS-4b's.** AC8 makes you record
the split so RS-4b's remaining scope stays truthful.

**D4 — The historical Minions record is preserved in a sibling file, not left to git history.** Considered
and rejected: *"the bytes are recoverable via `git show be9d744:…`"*. That is true and it is the argument
every team makes immediately before losing an artifact. Three concrete reasons it is insufficient here:
**(i)** `DF-7-2-A`'s owner is a **human QA Lead** who is told to adjudicate *"the REAL 7.2 dogfood findings
in `minions-dogfood-proof.md` §6"* — after regeneration that file contains a different finding population
over a different repository, and nothing on disk says so; **(ii)** §3.4 evidence immutability and RS-3's
*supersede, don't erase* are the project's stated standard, and RS-3 exists precisely because an
undifferentiated sweep would destroy an audit trail — *"which, on an assurance product, is the one thing
that must not happen"*; **(iii)** the Minions finding classes (332 / 2289 / 285) are the substrate for the
≥80 %-precision gate and can never be re-derived in this repository. Filename locked as
`minions-dogfood-proof-story-7-2-superseded.md` — date-free so it does not depend on when the story runs.

**D5 — The canonical filenames do NOT change, and no generated file is ever hand-edited.**
`minions-dogfood-proof.md`, `minions-dogfood-partition-plan.md` and `minions-dogfood-budget-plan.md` keep
their paths. Renaming them would break `tests/test_dogfood_proof.py::_PROOF_ARTIFACT`,
`tests/test_dogfood_plan.py::_PARTITION_PLAN` / `_BUDGET_PLAN`, the epic's own AC text, and the ledger's
cross-references — and an evidence path that moves is an evidence path that gets lost. The **title and body
tell the truth; the filename is a historical identifier.** Corollary, stated because it is the most likely
shortcut: the artifacts carry *"do NOT hand-edit"* in their own banner. If a rendered line is wrong, fix
`render_*_markdown` and regenerate. A hand-patched artifact passes the rot check exactly once.

**D6 — The three red tests: all three are FIXED here, and they are reported as two distinct populations.**
The epic's precondition demands an explicit fix-or-leave statement. **Fix**, because the failing assertions
are literally *"the committed artifact matches the live derivation"*, which **is** this story's deliverable
— leaving two of the three red while re-deriving the third artifact in the same family would be incoherent,
and would leave Epic 8 closing on a red suite. But the precondition also forbids absorbing them silently:
`…partition_plan_artifact…` and `…budget_reuses_the_31_accountant…` were red on the clean tree at `ae5f00c`
and are **repo-growth drift**, unrelated to the FR16/FR4 delta; `…proof_artifact_exists_and_matches_live_run…`
is **delta-caused** — 8.1's reorder plus 8.2's eligibility filter moved the live verdict from
`NOT_READY_FOR_RELEASE` to `RELEASE_READY`. Report them as 2 + 1, never as 3.

**D7 — `$X` = 843 stays frozen; the artifact stops calling it the current 7.1 sizing.** Considered and
rejected: re-pointing `DOGFOOD_BUDGET_CEILING` at the live `sized_ceiling` (431). That would edit
`TC-ArgusAgent-DOGFOOD-001-19`'s pin (`assert cost.ceiling == DOGFOOD_BUDGET_CEILING == 843`) and the
artifact rot check's `843` assertion in a story that has no mandate over the budget contract, and it would
make a frozen historical execution parameter float. Instead the artifact states **both** numbers and
whether the run fits under **each** — measured today: total 345, fits under 843 **and** under 431. Cost:
about four rendered lines. Benefit: two artifacts this story publishes in the same change cannot contradict
each other about what "the 7.1 empirical ceiling" is.

**D8 — A `worktree` / `-dirty` identity on the regenerated reports is ACCEPTED and disclosed, not
engineered away.** `--strict` refuses on a dirty tree, and the tree is unavoidably dirty while the story is
being implemented (your own edits, plus the orchestrator's untracked `bmad-dev-loop-pack/`). The shipped
report already discloses this honestly — `Source State: worktree`, and
*"**Reproducible by a third party**: **No** — the identity pins the exact bytes audited, but they cannot be
retrieved from a ref."* That self-disclosure **is** the AC4 method statement for those two artifacts. Do
not fake a clean identity, do not stash to manufacture one, and do not hand-edit the line. Likewise the
dogfood artifact's `Commit descriptor (HEAD at generation)` will read the **pre-commit** HEAD; the label
already says "at generation" and is therefore true. Record it; do not invent a future SHA.

**D9 — `_bmad-output/audit-reports/` is regenerated, not deleted.** Considered and rejected:
`git rm --cached` on it, on the grounds that its twin `_bmad-output/reports/` is gitignored and this is
plainly a leftover run output. Rejected because the epic AC names the path explicitly and requires it to
*agree with the contract*, and because §3.4/RS-3 say supersede rather than erase — regeneration **is** the
supersession. The distinction between the tracked copy (published evidence) and the gitignored copy (local
output) is recorded in AC7 rather than acted on.

**D10 — No `CHANGELOG.md` entry.** 8.4 owns the integrator contract and pins it with
`tests/test_release_note.py`. This story changes no shipped verdict, no exit code, no persisted schema, and
no string rendered by `argus/reports/**` or `argus/cli.py`. The only rendered strings that change belong to
`argus/dogfood/**` — internal proof-artifact tooling, not a documented integrator surface. Touching
`CHANGELOG.md` would also risk the AC9 rot check in a story with no mandate over it. `CHANGELOG.md` is
fenced in AC13.

**D11 — The story does not pin a verdict, anywhere, ever.** Not in an AC, not in a test, not in a default.
The epic is explicit: *"Pinning a predetermined verdict on an assurance tool's own proof artifact invites
the story to be 'made to pass,' which is the failure mode this product exists to name."* Everything this
story asserts is a property of the **method** (the row is disclosed; the inputs are disclosed; the subject
is named truthfully; a blocking verdict never coexists with zero findings). If your tree yields a different
verdict than §A measured, that is data, not a defect — record it and continue.

### Architecture patterns & constraints (non-negotiable — AR/NFR ids a reviewer will check)

- **AR8 pure/impure master rule.** `render_*_markdown` and `cost_summary` / `adjudication_rows` are PURE;
  `run_dogfood` / `enumerate_tracked_sources` / `materialize_snapshot` are the impure shell. New rendering
  logic goes in the pure half. Reading the persisted `CriticalSubsystemSet` (Story Context §G) is **impure**
  and belongs in `run_dogfood` / `build_dogfood_proof`, never in a renderer.
- **AR7 no-fork / REUSE.** Do not write a second partitioner, cost accountant, store reader or verdict
  fold. `run_dogfood` already constructs `ApaaStoreReader(snapshot_repo)` for the 4.2 lint — reuse that
  instance. `build_dogfood_proof` already calls `build_full_repo_plan` — take `sized_ceiling` from it.
- **AR4 determinism.** Exact `Fraction`, never `float`. No wall-clock, `uuid4`, `getpid()` or set-iteration
  order in anything that reaches a rendered byte. `sorted()` every collection you enumerate.
- **AR10 typed failure.** Any new failure path raises the existing `DogfoodProofError` / `DogfoodPlanError`
  — never a bare traceback, and the message names a relative condition, never an absolute host path.
- **NFR-S1 / S3 no source retention.** Artifacts carry provenance, counts, closed-enum tokens and
  repo-relative POSIX locators only. A critical-subsystem **path** is a locator and is allowed; a source
  line is not.
- **NFR-M1.** No source file over 1200 lines. `argus/pipeline.py` sits at **1199** — do not touch it.
- **NFR-M2 additive-only.** New `DogfoodProofRun` fields carry defaults. `DOGFOOD_PROOF_SCHEMA_VERSION`
  is **not persisted anywhere** (verified: it appears only in `__all__` and its own assignment), so no bump
  is required; if you bump it anyway, say why in the Completion Notes.
- **Cross-cutting concern #6 — advisory-by-contract / the false-accusation moat.** This story is the moat
  applied to Argus's own published evidence. Every disclosure AC1 demands exists so a reader can falsify
  the verdict rather than trust it.

### Traps a previous story already paid for (Epic 1-8.4 learnings that apply here)

1. **Measure in place, on the real tree, not on a scratch copy.** 8.1 lost a review round to this. Both
   generators read `git ls-files` and the working-tree bytes — a scratch copy has neither the right index
   nor the right content.
2. **Regenerate LAST.** Every artifact figure depends on `argus/**` bytes. Editing `proof_run.py` after
   regenerating changes `total_loc`, may change partition membership (and therefore the sha256
   `partition_id`s, which are computed over sorted member paths), and will re-break the rot check you just
   turned green. Source edits → tests → **then** regenerate → then re-run tests.
3. **RED-first, and paste the failure.** 8.3's review reconstructed the pre-fix implementation and injected
   it at runtime rather than reading the Dev's claim. Assume the same. An assertion never shown to fail is
   not evidence.
4. **Windows console.** Run everything as `PYTHONIOENCODING=utf-8 python -m pytest tests/ -q`; the
   artifacts contain `≥`, `→`, `·` and `🔴` and cp1252 stdout will mangle or crash on them. Write every file
   with `encoding="utf-8"`.
5. **Don't fix what you were told not to fix.** 8.4 shipped clean partly by fencing four deferred items and
   saying so. The version-token mismatch and the gate-status `N=0` understatement in Story Context are
   **file-and-leave**, not fix.
6. **The `dogfood_proof` fixture is module-scoped and the run takes ~2 minutes.** Add end-to-end assertions
   to tests that already take that fixture (AC11c) rather than creating new module-scoped runs.

### Runtime, library and toolchain specifics (verified on this machine, 2026-08-07)

- Python invoked as `python` (Windows). `python -m argus.cli audit .` works from the repo root; the
  console script `argus` may not be on PATH in this environment — prefer `python -m argus.cli`.
- `python -m mypy argus` → *Success: no issues found in 69 source files*. Keep it there.
- Full suite runtime ≈ **173 s**. `tests/test_dogfood_proof.py` + `tests/test_dogfood_plan.py` alone are the
  expensive part (two real audits of the repo).
- `pydantic` 2.13 — `AuditVerdict` is `extra="forbid"`; `CoverageLedgerEntry`'s field is `file_path` (not
  `path`) and `claim_present` is required. `CriticalSubsystemSet.model_fields` =
  `schema_version, paths, origins, designated_but_unmatched, heuristic_excluded_ineligible`.
- `evaluate_verdict(ledger, findings=(), *, critical_subsystems_all_deep=True,
  critical_subsystems_not_deep=(), scope_paths=None, scope_id='application',
  scope_excluded_reason='test_files') -> AuditVerdict`.
- `DecisionRow` values: `row_1_below_floor`, `row_2_blocking_findings`, `row_3_gates_met`,
  `row_4_gate_unmet_no_findings`. `VERDICT_SCHEMA_VERSION == "2"`.
- CLI defaults: `--coverage-scope application`; `--reports` defaults to `final-verdict,coverage-ledger`.
- **No web research was required.** This story adds no dependency, calls no external API and pins no new
  library version; every technical fact above was verified by execution against the installed toolchain,
  which is a stronger source than release notes.

### Recent git context

`be9d744` *feat(verdict,reports,packaging): land Epic 8 stories 8.1-8.4 and Epic 9 story 9.1* — the entire
Epic-8 delta plus 9.1, committed as one change. `9109e16` readiness report; `d8ba5ad` the PRD FR16/FR4
amendment; `faeefd9` *fix(verdict): stop reporting a block when nothing was found*; `ae5f00c`
*fix(audit): make verdicts honest and the tool runnable on any repo* — the tree on which the two plan-artifact
tests were already red. The practical consequence for you: **`git show HEAD:<path>` is now the way to get a
"before" string**, and `git diff HEAD` will show only *your* work, which makes AC13's fence check trivial.

### Project Structure Notes

- Package tree `argus/` — subpackages `audit/ cache/ cost/ detectors/ dogfood/ evidence/ governance/
  index/ ledger/ precision/ reports/ store/ verdict/` plus `cli.py`, `pipeline.py`, `pipeline_persist.py`,
  `models.py`.
- Tests are **flat** under `tests/` (`tests/test_dogfood_proof.py`) — there is **no** `tests/argus/` and
  **no** `tests/security/`, which is exactly why the artifact's citations are wrong (AC2).
- Planning artifacts and the tracker: `_bmad-output/design-artifacts/ArgusAgent/`; story files in its
  `stories/` subfolder. **Config drift, known and deliberate:** `_bmad/bmm/config.yaml` declares
  `_bmad-output/planning-artifacts` / `_bmad-output/implementation-artifacts`, neither of which exists;
  `_bmad/custom/config.toml` pins both keys to the folder above. Use the on-disk layout; do not create the
  config-declared paths.
- Verification-area ids: `TC-ArgusAgent-<AREA>-<SEQ>-<SUBSEQ>`. This story continues **DOGFOOD-001** at
  **-35**.

### Variance from the epic, recorded

- **AC2 (subject/provenance/citation honesty) is an addition.** The epic assumed the dogfood still audited
  Minions. Measured: it does not — `enumerate_tracked_sources(scope_prefix="argus")`. Justified under
  **D2**; without it this story publishes a fresh falsehood.
- **AC5's preserved sibling file is an addition.** The epic requires an append-only *ledger* note about
  DF-6-6-A/DF-7-2-A but does not notice that regeneration **destroys the artifact those defers are defined
  over**. Justified under **D4** (§3.4 / RS-3).
- **AC1's ceiling-honesty pair is an addition.** Emergent: the epic could not know the live 7.1 sizing had
  drifted 843 → 431, creating a contradiction between two artifacts this story publishes together
  (**D7**).
- **AC1's critical-clause empty-vs-satisfied disclosure is an addition**, promoted from the epic's boundary
  **B3** and inversion **F1** because the re-derivation actually landed on `RELEASE_READY`, which is the
  direction those two notes say nothing currently guards.
- **AC10's second scope (`--coverage-scope repository`) is an addition.** The epic names only
  `argus audit .`. Measured: the default flipped to `application` in CR-2, so the plain command no longer
  exercises the population under which the symptom was reported. Without the second run the F5 evidence is
  one flag away from vacuous.
- **AC11, AC12, AC13 are additions** following this project's established story shape (mechanized
  non-regression, purity/NFR proof, explicit fences) — 8.2, 8.3 and 8.4 each carried the equivalent.
- **The epic's precondition text is partly stale** (two failures, "unrelated to this delta"); measured
  today it is three, and the third is delta-caused. Reconciled in **D6** rather than silently.

### References

- [Source: epics.md#Story 8.5: Re-derive the proof so the evidence matches the tool] — the seven ACs and
  the red-test precondition.
- [Source: epics.md#Derived Delta Requirements (DR)] — DR-10 (stale proof artifacts), DR-3 (row +
  population disclosure), DR-9 (schema bump is the only intentional byte change).
- [Source: epics.md#Epic 8: The Honest Verdict] — the story-ordering constraint that puts 8.5 last, and the
  *"no published Argus artifact contradicting the shipped contract"* outcome statement.
- [Source: epics.md frontmatter] — inversion **F1** / **F5**, self-consistency and boundary-sweep
  (**B1**, **B3**) outcomes.
- [Source: epics.md#Repo-Separation Requirements (RS)] — RS-1 (`argus/` is the only live tree), RS-3
  (supersede, don't erase), RS-4b (the bulk sweep, and its "must follow 8.5" sequencing).
- [Source: E-PRD/prd.md + E-PRD/addendum.md] — FR16 (the binding 4-row table) and FR4 (critical-set
  eligibility), as amended 2026-08-03.
- [Source: sprint-change-proposal-2026-08-03.md] — the originating operator command and its recorded
  output (`deep_ratio=11/28`), the F5 baseline.
- [Source: architecture.md] — AR3/AR4/AR7/AR8/AR10/AR11, NFR-D1/D2/D3, NFR-P1, NFR-S1/S3, NFR-M1/M2.
- [Source: deferred-work.md] — DF-6-6-A, DF-6-6-A-P1, DF-6-6-A-P2, DF-7-2-A, RS-4b, DF-8-4-A…D and the six
  CC-3 field convention.
- [Source: stories/8-4-tell-integrators-what-changed.md#Dev Notes] — **D3** (front door vs bulk sweep), the
  precedent this story's **D3** boundary follows.
- [Source: stories/8-3-plain-english-report-stops-describing-impossible-state.md] — the DR-11 report-surface
  reconciliation whose output the regenerated `final-verdict.md` now carries.
- [Source: minions-dogfood-proof.md, minions-dogfood-partition-plan.md, minions-dogfood-budget-plan.md] —
  the three artifacts being re-derived.

---

## Dev Agent Record

### Context Reference

All figures below were **re-derived by this dev session**, not read off the story. Instruments, in the
order they were used, all on `d:/ProjectX/XAgents/XAgents/ArgusAgent` itself at HEAD `be9d744` with `.git`
and `_bmad-output/` present — never a scratch copy:

1. `git rev-parse HEAD` / `git status --porcelain` — confirmed `be9d7449cf56…`, untracked
   `bmad-dev-loop-pack/` (the orchestrator's — never `git add`ed, never deleted, excluded from every
   figure) plus the SM's own `sprint-status.yaml` edit and the untracked story file. `git diff HEAD` over
   `argus/` was **empty** at start, as the story warned, so it was not used as a measuring instrument.
2. `PYTHONIOENCODING=utf-8 python -m pytest tests/ --tb=no -q` — the baseline red set.
3. A throwaway script importing and CALLING the shipped functions in place: `build_full_repo_plan('.')`,
   `run_dogfood('.', …)`, `build_dogfood_proof('.', …)`, and `ApaaStoreReader` over the run's own
   `.argus/state/` tree resolved by `CRITICAL_SUBSYSTEMS_PRODUCER`.
4. The real `evaluate_verdict` folded over a synthetic 15-entry `CoverageLedger` for the analytic half.
5. The shipped CLI: `python -m argus.cli audit .` at both coverage scopes and with both `--report-dir`s.

> ⚠️ **One SM figure did not reproduce, and the artifact records what was measured, not what was
> expected.** Story Context §G reports the critical-subsystem set as `len(paths) == 50` /
> `len(heuristic_excluded_ineligible) == 65`. That is the set for a **whole-repository** audit of this
> tree. The dogfood does not audit the whole repository — it audits a materialized snapshot containing
> only `argus/` minus `argus/tests/`. Read out of the **snapshot's own** `.argus/state/`, which is the set
> the gate that produced this verdict actually keyed on, it is **48 paths / 10 DR-5-excluded / 0
> `designated_but_unmatched`**. The artifact discloses 48/10/0. Disclosing 50/65 would have been a figure
> from a different run.

### Agent Model Used

Claude Opus 5 (1M context) — model id `claude-opus-5[1m]` — via the BMAD `dev-story` workflow, run as a
single-story worker under the `bmad-dev-loop` orchestrator.

### Debug Log References

**Baseline, measured before any file was touched (2026-08-07, HEAD `be9d744`):**

```
$ PYTHONIOENCODING=utf-8 python -m pytest tests/ --tb=no -q
1150 collected — 1147 passed, 3 failed
FAILED tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation
FAILED tests/test_dogfood_plan.py::test_budget_reuses_the_31_accountant_no_fork
FAILED tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run
$ python -m mypy argus
Success: no issues found in 69 source files
```

**Live re-derivation, measured by calling the shipped code in place (before any edit):**

```
plan.commit_descriptor  be9d7449cf564bd8cc1e9a9000c04d78f7e0021c
plan  69 files / 17736 LOC / 3 units [2c0f52f60457, 681c496d09ed, 973f3f199d1c] / 50 cut edges
budget  total_credits 345  sized_ceiling 431  headroom 86  baseline_ratio 115/5912
verdict RELEASE_READY   exit 0
decision_row  row_3_gates_met
deep 53/69   deep_count 53  total_count 69
blocking_finding_count 0     total findings 97
coverage_scope None                       # the snapshot holds no test files → NO narrowing
critical_subsystems_all_deep True   critical_subsystems_not_deep ()
schema_version "2"   is_below_floor False
CriticalSubsystemSet (from the snapshot's .argus/state/): paths 48, heuristic_excluded_ineligible 10,
                                                          designated_but_unmatched ()
```

**Analytic fold of the historical 7.2 inputs through the real `evaluate_verdict` (§B):**

```
unmet (as recorded in 7.2)     -> INSUFFICIENT_COVERAGE exit 3 row row_4_gate_unmet_no_findings deep 13/15 blocking 0
cleared by the DR-5 filter     -> RELEASE_READY         exit 0 row row_3_gates_met              deep 13/15 blocking 0
```

`NOT_READY_FOR_RELEASE` / exit `2` is unreachable for those inputs under either branch — row 2 is the only
row that renders it and row 2 requires ≥1 blocking finding. Which of row 3 / row 4 fires is **not**
determinable here and is not guessed.

**RED-first, pasted verbatim.** The seven new pins were run against the *pre-fix committed artifacts*
before regeneration. All seven failed; the RED-first for the artifact-content pins is the pre-8.5 artifact
itself, which is stronger than a synthetic stale variant.

```
$ python -m pytest tests/test_dogfood_plan.py::test_plan_artifacts_name_the_tree_they_actually_planned -q
E   AssertionError: FALSE SUBJECT in committed partition: 'minions_core/' — the plan enumerates
    scope_prefix='argus/' (this repository's own package)
E   assert 'minions_core/' not in '# minions d...ovenance).\n'
E     'minions_core/' is contained here:
E       rated by `minions_core/apaa/dogfood/partition_plan.py` (`render_partition_plan_markdown`).
E       reproducible + byte-stable for the same tracked minions content — do not hand-edit. ...
tests\test_dogfood_plan.py:546: AssertionError
FAILED tests/test_dogfood_plan.py::test_plan_artifacts_name_the_tree_they_actually_planned

$ python -m pytest tests/test_dogfood_proof.py -q -k "<the six new pins>" --tb=line
tests/test_dogfood_proof.py:730: AssertionError: FALSE SUBJECT — the proof artifact claims 'the real
    minions repo', but the dogfood enumerates scope_prefix='argus' (it audits THIS repository's own package)
tests/test_dogfood_proof.py:768: AssertionError: the committed proof artifact pairs a blocking verdict with
    zero blocking findings — the exact published contradiction DR-10 deletes
    assert not (True and True)
tests/test_dogfood_proof.py:793: AssertionError: the artifact must state BOTH the frozen $X and the live
    7.1 sizing
    assert ('843' in '# Minions Dogfood — Proof Artifact (Story 7.2, APAA CAPSTONE)…' and '431' in …)
tests/test_dogfood_proof.py:843: AssertionError: the re-derived artifact must carry a back pointer to the
    preserved record
tests/test_dogfood_proof.py:885: AssertionError: assert 'Critical-set size (`CriticalSubsystemSet.paths`):
    **48**' in '# Minions Dogfood — Proof Artifact (Story 7.2, APAA CAPSTONE)…'
FAILED tests/test_dogfood_proof.py::test_artifact_discloses_the_live_decision_row
FAILED tests/test_dogfood_proof.py::test_artifact_names_its_real_subject_and_every_citation_resolves
FAILED tests/test_dogfood_proof.py::test_real_dogfood_never_blocks_without_a_finding
FAILED tests/test_dogfood_proof.py::test_artifact_states_the_ceiling_honesty_pair
FAILED tests/test_dogfood_proof.py::test_superseded_story_7_2_record_is_preserved_verbatim
FAILED tests/test_dogfood_proof.py::test_red_first_vacuously_satisfied_critical_gate_is_named
```

**The new citation guard caught a real dangling citation on its first green run** — evidence it is not
decorative. After the first regeneration, 40 of 41 dogfood tests passed and
`TC-ArgusAgent-DOGFOOD-001-36` reported:

```
E   AssertionError: DANGLING CITATION in minions-dogfood-budget-plan.md: ['budget_governor.py'] —
    an artifact that cites a path which does not exist is asserting a falsehood
```

The budget artifact's OI3 paragraph cited a bare `budget_governor.py`; the real path is
`argus/cost/budget_governor.py`. Fixed in the renderer (never in the artifact) and regenerated.

**Report regeneration (AC7) — both invocations, verbatim.** Working directory
`d:/ProjectX/XAgents/XAgents/ArgusAgent` for both.

```
$ python -m argus.cli audit . --report-dir _bmad-output/audit-reports      # TRACKED = published evidence
verdict=RELEASE_READY deep_ratio=57/149 blocking_findings=0 assessed_deep_ratio=57/73 scope=application held_out=76
exit 0
  → wrote final-verdict.md + coverage-ledger.md (the two files already present; none left half-fresh)
  - **Source State**: `worktree` — Working tree (uncommitted changes present)
  - **Identity**: `be9d7449cf56-dirty+88176af21377`
  - **Reproducible by a third party**: **No** — the identity pins the exact bytes audited, but they cannot
    be retrieved from a ref. Use `--strict` for commit-pinned evidence.

$ python -m argus.cli audit . --reports final-verdict,coverage-ledger,security-review \
      --report-dir _bmad-output/reports                                   # GITIGNORED = local run output
verdict=RELEASE_READY deep_ratio=57/149 blocking_findings=0 assessed_deep_ratio=57/73 scope=application held_out=76
exit 0
  → wrote final-verdict.md + coverage-ledger.md + security-review.md (the three files already present)
  - **Source State**: `worktree` — Working tree (uncommitted changes present)
  - **Identity**: `be9d7449cf56-dirty+88176af21377`
  - **Reproducible by a third party**: **No** — … Use `--strict` for commit-pinned evidence.
```

Neither `final-verdict.md` now pairs a blocking verdict with zero blocking findings: grepped, both contain
`- **Final Verdict**: **\`RELEASE_READY\`** (Exit Code \`0\`)` beside `- **Blocking Findings**: **0**`, and
neither file contains the token `NOT_READY_FOR_RELEASE` at all. Neither report is cited anywhere in this
story, the artifacts or the ledger as evidence that Argus is release-ready — see AC3's standard.

**Inversion F5 (AC10) — the originating operator command, both scopes, verbatim:**

```
$ python -m argus.cli audit .                              # default scope (application)
verdict=RELEASE_READY deep_ratio=57/149 blocking_findings=0 assessed_deep_ratio=57/73 scope=application held_out=76
exit 0

$ python -m argus.cli audit . --coverage-scope repository  # the scope the symptom was reported under
verdict=INSUFFICIENT_COVERAGE deep_ratio=57/149 blocking_findings=0
exit 3
```

**The symptom is NOT reproducible at either scope. No HALT.** Neither invocation wrote a report (the CLI
only writes when `--report-dir` is passed — verified by unchanged mtimes on both report directories), so
the AC7 evidence above was not disturbed.

**Final validation:**

```
$ PYTHONIOENCODING=utf-8 python -m pytest tests/ -q --tb=short   → exit code 0
$ python -m pytest tests/ --collect-only -q                      → 1157 collected
progress-character census over the full run: Counter({'.': 1157})  — 1157 '.', zero F/E/s/x/X
$ python -m mypy argus
Success: no issues found in 69 source files
```

---

**FIX ITERATION 1 (2026-08-07) — the review's five Low findings. RED-first, pasted verbatim.**

The state this session inherited is recorded honestly because it matters: a prior interrupted fix attempt
had already landed **finding 3 in full** and **finding 2's `partition_plan.py` half** (`effective_exclusions`
+ `FullRepoPlan.effective_exclude_prefixes`), and had added the `retrieval_note` /
`critical_subsystems_note` fields **without wiring them**. Nothing was assumed: each finding was re-checked
against the file on disk before deciding what remained. `proof_run.py`'s half of finding 2, all of finding
4, both ledger entries, all three new tests and every regeneration are this session's.

**(a) The directory-citation guard, RED against the REAL pre-fix committed artifact** — no synthetic
variant needed, which is stronger:

```
$ PYTHONIOENCODING=utf-8 python -m pytest tests/test_dogfood_proof.py::test_artifact_names_its_real_subject_and_every_citation_resolves -q --tb=short
tests\test_dogfood_proof.py:758: in test_artifact_names_its_real_subject_and_every_citation_resolves
    assert not dangling, (
E   AssertionError: DANGLING CITATION in minions-dogfood-proof.md: ['argus/tests/'] — an artifact that
    cites a path which does not exist is asserting a falsehood
E   assert not ['argus/tests/']
FAILED tests/test_dogfood_proof.py::test_artifact_names_its_real_subject_and_every_citation_resolves
```

**(b) The two behavioural pins, RED against the restored PRE-FIX bodies.** `proof_run.py` was backed up,
the `int = 0` sentinel and the fatal first-match-wins scan were re-injected by a scratch script, the two new
tests were run, and the file was restored from the backup (`mypy` clean before and after, 1196 lines both
times):

```
$ PYTHONIOENCODING=utf-8 python -m pytest tests/test_dogfood_proof.py -q --tb=short \
      -k "sentinel_separates_absent or degrades_and_refuses"
FF                                                                       [100%]
____ test_optional_critical_set_read_degrades_and_refuses_ambiguity ____
argus\store\reader.py:120: in read_envelope
    raise StoreIntegrityError(
E   argus.store.reader.StoreIntegrityError: content_hash mismatch for artifact
    'state/79934d7b...245.json' (tamper detected: stored != recomputed)
The above exception was the direct cause of the following exception:
tests\test_dogfood_proof.py:980: in test_optional_critical_set_read_degrades_and_refuses_ambiguity
    found, note = proof_run_module._read_critical_subsystem_set(reader)
E   argus.dogfood.proof_run.DogfoodProofError: could not read the persisted envelope at
    'state/79934d7b...245.json' while resolving the critical-subsystem set (StoreIntegrityError)
____ test_live_sizing_sentinel_separates_absent_from_zero ____
tests\test_dogfood_proof.py:1031: in test_live_sizing_sentinel_separates_absent_from_zero
    assert absent.live_sized_ceiling is None
E   assert 0 is None
E    +  where 0 = CostSummary(total_credits=5, ceiling=843, ..., live_sized_ceiling=0,
E                             fits_within_live_sized_ceiling=False).live_sized_ceiling
FAILED tests/test_dogfood_proof.py::test_optional_critical_set_read_degrades_and_refuses_ambiguity
FAILED tests/test_dogfood_proof.py::test_live_sizing_sentinel_separates_absent_from_zero
```

The first failure **is** finding 4 reproduced end-to-end: a tampered envelope belonging to an unrelated
producer aborts the entire proof-run read. Both are green against the fixed bodies.

**(c) The measured exclusion, which is what closed finding 2 on the generator side.** Re-running the live
derivation after the change prints `effective_exclusions=()` for BOTH generators — the configured
`argus/tests/` prefix held out **zero** tracked files, confirming the reviewer's claim by measurement rather
than by inspection. `grep -c "argus/tests"` over the three regenerated artifacts returns `0 / 0 / 0`.

**(d) Regeneration after the fix (source edits first, artifacts LAST — trap 2):**

```
$ PYTHONIOENCODING=utf-8 python <scratch>/regen_artifacts.py
plan  files=69 loc=18276 units=3 ids=['2c0f52f60457','681c496d09ed','973f3f199d1c'] sized_ceiling=431
      total_credits=345 baseline=115/6092 effective_exclusions=()
proof verdict=RELEASE_READY exit=0 row=row_3_gates_met deep=53/69 blocking=0 findings=101 files=69
      loc=18276 units=3 cost=345/843 live_ceiling=431 scope=None effective_exclusions=()
critical retrieved=True size=48 dr5_excluded=10 unmatched=() all_deep=True note=''
```

`total_loc` moved **18206 → 18276**: exactly the +70 lines this fix round added to `argus/**`
(`proof_run.py` 1154→1196, `partition_plan.py` 677→705). Findings 97→101 track the same growth. The
knife-edge **`unit_count` held at 3** and the three `partition_id`s are unchanged. No artifact was
hand-edited; all three were written by `render_*_markdown` + `"\n"`.

**(e) AC7 reports and AC10/F5 re-run against the FINAL tree** (they depend on `argus/**` bytes, which
changed, so the previously recorded figures could not simply be carried):

```
$ python -m argus.cli audit . --report-dir _bmad-output/audit-reports          # TRACKED = published
verdict=RELEASE_READY deep_ratio=57/149 blocking_findings=0 assessed_deep_ratio=57/73 scope=application held_out=76
exit 0    Source State: `worktree`   Identity: `be9d7449cf56-dirty+5223af66e13b`
          Reproducible by a third party: **No** — … Use `--strict` for commit-pinned evidence.

$ python -m argus.cli audit . --reports final-verdict,coverage-ledger,security-review \
      --report-dir _bmad-output/reports                                        # GITIGNORED = local
verdict=RELEASE_READY deep_ratio=57/149 blocking_findings=0 assessed_deep_ratio=57/73 scope=application held_out=76
exit 0    (same Source State / Identity)

$ python -m argus.cli audit .                              # F5, default scope
verdict=RELEASE_READY deep_ratio=57/149 blocking_findings=0 assessed_deep_ratio=57/73 scope=application held_out=76
exit 0
$ python -m argus.cli audit . --coverage-scope repository  # F5, the symptom's original scope
verdict=INSUFFICIENT_COVERAGE deep_ratio=57/149 blocking_findings=0
exit 3
```

The `Identity` moved `…+88176af21377` → `…+5223af66e13b` because the worktree bytes changed — the identity
is doing its job. **The F5 symptom is still NOT reproducible at either scope; no HALT.** `grep -c
NOT_READY_FOR_RELEASE` over both `final-verdict.md` files returns `0 / 0`.

**(f) Final validation of the fix round:**

```
$ PYTHONIOENCODING=utf-8 python -m pytest tests/ --tb=short   → exit 0
1160 passed in 233.57s (0:03:53)
progress-character census over the full run: Counter({'.': 1160})   — 1160 '.', zero F/E/s/x/X
$ python -m mypy argus
Success: no issues found in 69 source files
```

### Completion Notes List

**FIX ITERATION 1 (2026-08-07) — dispositions.** F1 **filed** (`DF-8-5-C`), F2 **fixed** (both halves), F3
**fixed**, F4 **fixed** (both mechanisms), F5 **filed** (`DF-8-5-D`) with the rejection re-affirmed and its
blocker corrected. Full per-finding reasoning is in *Review Findings — resolution* above. Suite **1157 →
1160 passed / 0 failed / 0 skipped** (+3 new tests, `TC-ArgusAgent-DOGFOOD-001-42/-43/-44`), `mypy argus`
clean at 69 files. **No existing assertion was deleted, loosened or skipped:** `git diff -U0` over both test
modules still shows **zero** deleted lines against `HEAD`. Exactly one assertion written earlier in this
same story was **changed**, and it is called out rather than buried — `TC-ArgusAgent-DOGFOOD-001-41`'s
subject-line pin asserted the artifact renders the **configured** exclusion
(`- Source files (tracked \`argus/\`, excluding \`argus/tests/\`)`), which encoded the exact defect finding 2
names. It now asserts the **measured** exclusion plus the negative (`excluding \`<unmatched>\`` must not
appear) and cross-checks `effective_exclude_prefixes` against a fresh un-excluded enumeration — strictly
stronger, not looser. `argus/pipeline.py` remains at **1199** lines and absent from `git diff --stat`; every
AC13 fence re-verified clean.

**AC12 — suite counts.** Baseline **1147 passed / 3 failed** (1150 collected). End of the first pass:
**1157 passed / 0 failed / 0 skipped** (1157 collected), `mypy argus` clean at 69 source files. Every one of
the 1147 baseline passes still passes; the 3 baseline failures are green; the 7 new tests are green. This
clears AC12's "1150 passed, 0 failed or better". **Superseded by fix iteration 1: the current state is 1160
passed / 0 failed / 0 skipped** (+3 review-driven regression tests) — see the fix-iteration note above.

**AC6 / D6 — the three reds, reported as 2 + 1, not as 3.**

- **2 PRE-EXISTING (repo-growth drift, red on the clean tree at `ae5f00c`, unrelated to the FR16/FR4
  delta):** `test_committed_partition_plan_artifact_exists_and_matches_live_derivation` — the committed
  plan pinned units `8c20feb2c997 / ab6ff465ec4a / b66e4aaf9a15` while the live derivation yields
  `2c0f52f60457 / 681c496d09ed / 973f3f199d1c`; and `test_budget_reuses_the_31_accountant_no_fork` — the
  committed budget artifact recorded the old sized ceiling `406` while the live sizing is `431`. Both were
  fixed by re-deriving the artifacts they assert over.
- **1 DELTA-CAUSED:** `test_committed_proof_artifact_exists_and_matches_live_run` — 8.1's decision-table
  reorder plus 8.2's DR-5 eligibility filter moved the live dogfood verdict from `NOT_READY_FOR_RELEASE` /
  exit `2` to `RELEASE_READY` / exit `0`, so the committed proof stopped matching its own generator.
- No assertion in any of the three was deleted, loosened or skipped. `git diff -U0` over both test modules
  shows **zero deleted lines** — the change is purely additive.

**AC1 / D11 — what the live run actually produced (recorded, not targeted).** `RELEASE_READY` / exit `0`,
`decision_row = row_3_gates_met`, deep `53/69` (exact `Fraction`, `deep_count` 53 / `total_count` 69),
`blocking_finding_count` 0, `coverage_scope is None` → **no narrowing occurred** (the snapshot contains no
test files, so nothing was held out), critical clause **satisfied over a NON-EMPTY set** — 48 critical
paths, all `audited_deep`, 10 removed from the heuristic term as DR-5-ineligible, 0
`designated_but_unmatched`, 0 not-deep. Boundary **B1** held as the epic predicted (row 3, not row 4). No
verdict is pinned anywhere in the generator, the artifact or any test: the tests assert properties of the
METHOD (the row is disclosed and is a real enum member; the row and the token cannot disagree; a blocking
verdict can never coexist with zero blocking findings), never an outcome.

**AC1 / D7 — the ceiling honesty pair, measured.** Frozen `$X` = `DOGFOOD_BUDGET_CEILING` = **843** (the
parameter the run was executed under, untouched — `TC-ArgusAgent-DOGFOOD-001-19`'s pin still reads
`cost.ceiling == DOGFOOD_BUDGET_CEILING == 843`); live 7.1 `sized_ceiling` = **431** from the same
`build_full_repo_plan` call the generator already makes. Total 345 credits fits under **both**. The proof
artifact and the budget artifact now state the same two numbers and cannot contradict each other about
what "the 7.1 empirical ceiling" is.

**AC2 / D2 — the subject correction, and one figure that moved because of it.** The generators now render
their subject from the scope the derivation **recorded** (`FullRepoPlan.scope_prefix` /
`exclude_prefixes`, `DogfoodProofRun.scope_prefix` / `exclude_prefixes`), never from a hardcoded literal,
so an artifact cannot name a tree the derivation did not read. All three `AUTO-GENERATED by …` banners now
name modules that exist; the three dangling test-path citations
(`tests/security/test_argus_secret_containment.py`, `tests/argus/test_dogfood_proof.py` ×2) are corrected
to the real `tests/test_secret_containment.py` / `tests/test_dogfood_proof.py` with their TC ids; a fourth
dangling citation (`budget_governor.py`) that no one had noticed was caught by the new guard and
corrected. Exactly **one** occurrence of the word "Minions" survives in the three artifacts — the sentence
pointing a reader at the preserved Story-7.2 record, which is a true historical statement, not a claim
that Minions source was audited.

**AC8 / D3 — the RS-4b split, re-measured after the change.** **6 of 15 consumed** —
`dogfood/partition_plan.py:481, 490, 554` and `dogfood/proof_run.py:597, 609, 610`;
`argus/dogfood/partition_plan.py` now has **zero** `minions_core` references. **9 of 15 remain** —
`audit/deep_audit.py:21`, `audit/ports.py:4`, `cost/budget_governor.py:15`, `dogfood/proof_run.py:52`,
`:53`, `dogfood/proof_run.py:632` (the `DogfoodProofError` operator message; this was `:486` before the
change — the line moved, the string did not), `governance/escalation.py:35`, `store/envelope.py:25`,
`verdict/prosecutor.py:36`. All nine are docstring / comment / operator-message prose and none reaches a
committed artifact, exactly as D3's rule requires. RS-4b's "must follow 8.5" sequencing constraint is now
satisfied; RS-4b stays OPEN and its ledger entry was not rewritten.

**AC13 — deferred-item dispositions.**

- **RS-4b** — PARTIALLY CONSUMED (6 of 15) and progress-noted append-only. Stays open.
- **DF-8-2-A / DF-8-3-A / DF-8-3-C** — UNTOUCHED. All three gate on a `argus/pipeline.py` extraction this
  story does not perform; `argus/pipeline.py` is absent from `git diff --stat` and remains at 1199 lines.
- **DF-8-4-A / DF-8-4-B / DF-8-4-C / DF-8-4-D** — UNTOUCHED. Their surfaces (`action.yml`,
  `tests/test_release_note.py`, `argus/reports/generator.py`, `argus/cli.py`) are all fenced by AC13 and
  all are absent from `git diff --stat`.
- **DF-6-6-A / DF-6-6-A-P1 / DF-6-6-A-P2 / DF-7-2-A / DF-6-7-A** — all stay OPEN, none rewritten; an
  append-only note records that the human adjudication must now read the preserved sibling file.

**AC8 — the two new defers filed, and the two things deliberately NOT fixed.** `DF-8-5-A` (the
`DOGFOOD_ArgusAgent_VERSION = "1.43.0"` vs shipped `0.1.0` provenance falsehood inside the SIGNED evidence
bundle; `target_story: 9-2-…` because changing it changes the bundle content hash the proof publishes as
its signature) and `DF-8-5-B` (the structural fragility of the three committed-artifact rot checks, with
the measured mechanism — sha256-over-sorted-member-paths `partition_id`s, `total_credits × 5/4` sizing —
and the measured history of four consecutive red commits). Both carry the six CC-3 fields. The §7
gate-status `N=0` understatement was left alone as instructed: it understates rather than over-claims, and
fixing it would touch the 6.5/6.6 precision surface that no AC here owns. ~~It is covered by the already-open
`DF-6-6-A-P1` / `DF-7-2-A` pair rather than duplicated as a third new id.~~ **CORRECTED in fix iteration 1 —
this last sentence was wrong and the review caught it.** `deferred-work.md:362-394` records the corpus
counts but says nothing about the published artifact rendering `N=0`, so the known-wrong number had no
ledger trace at all. `DF-8-5-C` now carries it, with the call site, the rendered line and the true values
re-measured by execution.

**AC9 — the gate stayed provisional.** `protocol_cleared` was never passed `True` (the grep-style guard in
`TC-ArgusAgent-DOGFOOD-001-30` still passes over the edited `proof_run.py`), the 6.5
`precision_gate_status()` marker was not flipped, §7 survives the re-derivation intact, and both
`test_red_first_gate_not_silently_flipped` and `test_precision_gate_stays_provisional` pass unchanged.

**AC3 — the green result is not sold as clearance.** The re-derived artifact still carries
`grade: demo-heuristic-only` and the externalization guard verbatim, the forbidden-phrase guard
(`TC-ArgusAgent-DOGFOOD-001-26`) passes over the entirely new prose, and §1 now states in the artifact
itself that a self-audit is materially weaker evidence than the independent run it supersedes and is
"never independent corroboration". Nothing in this story record, the artifacts or the ledger cites the
`RELEASE_READY` verdict or either regenerated report as evidence that Argus is release-ready.

**AC12 — purity, determinism and size.** All new rendering logic is in the pure half: `_scope_clause`,
`_audited_tree_clause`, `_row_token`, `_render_assessed_population`, `_render_critical_clause`,
`_render_ceiling_pair` take a value object and return strings — no I/O, no clock, no `uuid4`, no
`getpid()`, no set iteration (every collection rendered is an already-sorted tuple). The one new impure
read, `_read_critical_subsystem_set`, lives in `run_dogfood` and REUSES the `ApaaStoreReader` instance
that was already being built for the 4.2 lint rather than constructing a second one; its `state/` scan is
`sorted()`. Ratios stayed exact `Fraction`. `test_full_repo_plan_is_deterministic_and_byte_reproducible`
and `test_dogfood_is_100pct_reproducible_byte_identical` both pass. No artifact gained a source byte or a
secret value — only provenance, counts, closed-enum tokens and repo-relative POSIX locators; the
containment assertions (`TC-…-DOGFOOD-001-22`, `-15`, `TC-…-SECURITY-001-23`) all pass. Every new field on
`CostSummary` / `DogfoodProofRun` / `FullRepoPlan` / `_DogfoodExecution` carries a default, so no existing
construction site broke. File sizes **after fix iteration 1**: `proof_run.py` **1196**, `partition_plan.py`
**705**, `tests/test_dogfood_proof.py` **1042**, `tests/test_dogfood_plan.py` **589** — all ≤1200 (NFR-M1),
with `proof_run.py` down to **4 lines of headroom** (disclosed above; `DF-8-5-D` filed).
`DOGFOOD_PROOF_SCHEMA_VERSION` was **not** bumped: it is persisted nowhere, and the two new dataclasses are
additive.

**Tradeoff recorded (project standard over principle).** `proof_run.py` grew from 749 to **1154** lines —
inside NFR-M1 but with only 46 lines of headroom. The SOLID/SoC move would be to extract the pure renderer
into a sibling `argus/dogfood/proof_render.py`. That was considered and **rejected here**: the renderer
reads `DogfoodProofRun`, which lives in `proof_run.py`, so the split needs either a circular import or a
migration of the dataclasses too — a restructuring with real blast radius, landed in the final story of an
epic whose whole point is not shipping surprises, and one that AC13 does not authorise. The project
standard (fenced scope, ≤1200 lines, additive-only) wins; the headroom is recorded here rather than
silently consumed. ~~This is an observation for whoever next edits the module, not a new ledger id — the
already-filed `DF-8-2-A` establishes the precedent for how this repo handles a module approaching the cap.~~
**CORRECTED in fix iteration 1.** The review was right that `DF-8-2-A` is the *precedent for filing an id*,
not a substitute for one, and it was right that the stated blocker is softer than recorded: the split needs
the dataclasses moved to a sibling and **re-exported**, which is not a circular import. `DF-8-5-D` now
carries it, plus a constraint measured here that the review did not have — a new module under `argus/`
changes the partition input set while `TC-…-DOGFOOD-001-18` pins `unit_count >= 3` at exactly 3. The module
is now **1196/1200**, so the extraction is the next editor's first task, not an optional cleanup.

**AC5 / D4 — the historical record.** `minions-dogfood-proof-story-7-2-superseded.md` was written FIRST,
before any regeneration. Its tail was verified byte-identical to
`git show HEAD:…/minions-dogfood-proof.md` (6994 characters, exact match) — the original body survives
verbatim, `APAA-` prefixes, `minions_core/` banner, dangling citations and all, because correcting a
historical record destroys the record. The hand-authored header carries the analytic re-derivation, the
determinable statement, the two candidate rows with their selecting conditions, the explicit "no new audit
was executed over Minions and none can be", a forward pointer, and an explicit refusal to pick row 3 vs
row 4. The re-derived artifact carries the back pointer. The file is hand-authored; no generator holds any
historical figure.

**AC11 — the new coverage, all continuing the area at `-35` and upward (`-01`…`-34` were taken; no id
reused).** `TC-ArgusAgent-DOGFOOD-001-35` the live decision row is disclosed and cannot disagree with the
verdict token · `-36` no Minions-source-audited claim and every cited path in all three artifacts resolves
on disk · `-37` the end-to-end impossible-state guard, asserted on the existing module-scoped
`dogfood_proof` fixture so it costs no extra runtime · `-38` the ceiling honesty pair, including that the
live figure is the one `build_full_repo_plan` actually derives · `-39` the preserved supersession file
exists and still contains the original's distinctive bytes (`7f8e147…`, `c0c4c35e…`, `**135**`,
`**36712**`, `| 332 |`, `| 2289 |`, `| 285 |`) plus pointers in both directions · `-40` the vacuous-gate
split, RED-first by rendering the SAME renderer over an empty-but-retrieved set and over an unretrieved
one · `-41` (in `test_dogfood_plan.py`) the plan artifacts name the tree they actually planned.

### File List

Paths relative to the repository root. Verified against `git status --porcelain` + `git diff --stat`
at the end of the story.

**Source (generators only — no verdict, ledger, report, pipeline or CLI file was touched):**

```
M argus/dogfood/proof_run.py        749 → 1154 → 1196 lines   (fix it.1: findings 2, 3, 4)
M argus/dogfood/partition_plan.py   612 →  677 →  705 lines   (fix it.1: finding 2, measured exclusions)
```

**Tests (purely additive vs `HEAD` — `git diff -U0` shows zero deleted lines in both):**

```
M tests/test_dogfood_proof.py       605 →  885 → 1042 lines
                                    (+ TC-ArgusAgent-DOGFOOD-001-35…-40, fix it.1: -42/-43/-44
                                     + the _DIR_TOKEN directory-citation guard)
M tests/test_dogfood_plan.py        509 →  564 →  589 lines
                                    (+ TC-ArgusAgent-DOGFOOD-001-41; fix it.1 STRENGTHENED its
                                     subject-line pin from the configured to the MEASURED exclusion)
```

**Artifacts — REGENERATED from the live generators, never hand-edited:**

```
M _bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md
M _bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md
M _bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md
M _bmad-output/audit-reports/final-verdict.md            (regenerated by the recorded CLI invocation)
M _bmad-output/audit-reports/coverage-ledger.md          (same invocation — no directory left half-fresh)
```

**Artifacts — HAND-AUTHORED (AC5; never generated, so no generator holds historical data):**

```
A _bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof-story-7-2-superseded.md
```

**Ledger + tracking:**

```
M _bmad-output/design-artifacts/ArgusAgent/deferred-work.md    (APPEND-ONLY: +199 lines, 0 deletions —
                                                                127 first pass + 72 in fix it.1 for
                                                                DF-8-5-C and DF-8-5-D)
M _bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml  (the 8-5 key + last_updated ONLY)
M _bmad-output/design-artifacts/ArgusAgent/stories/8-5-re-derive-proof-evidence-matches-tool.md
```

**Untracked / gitignored, written but not committable:**

```
- _bmad-output/reports/final-verdict.md      (gitignored at .gitignore:20 — local run output)
- _bmad-output/reports/coverage-ledger.md    (same)
- _bmad-output/reports/security-review.md    (same)
```

**Verified NOT modified (AC13 fences), by absence from `git diff --stat`:** `argus/verdict/**`,
`argus/ledger/**`, `argus/reports/**`, `argus/pipeline.py` (still 1199 lines), `argus/pipeline_persist.py`,
`argus/cli.py`, `argus/__init__.py`, `CHANGELOG.md`, `README.md`, `pyproject.toml`, `action.yml`,
`.github/workflows/**`, and `bmad-dev-loop-pack/**` (still untracked, never `git add`ed, never deleted).
No `.md` under `_bmad-output/design-artifacts/ArgusAgent/` was modified other than the three regenerated
dogfood artifacts, `deferred-work.md`, this story file, and the new superseded sibling.

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-08-07 | 0.1 | Story created. Ultimate context-engine analysis completed — comprehensive developer guide created. All figures measured in place at HEAD `be9d744` by importing the shipped `argus` functions and running the shipped CLI; baseline 1147 passed / 3 failed, mypy clean. | Scrum Master (create-story) |
| 2026-08-07 | 1.1 | **Code review iteration 1 addressed — 5 of 5 findings resolved, none dropped.** FIXED IN CODE (each RED-first, failure pasted verbatim): the artifacts stop publishing an exclusion prefix that held nothing out — both generators now render only `effective_exclude_prefixes`, MEASURED as empty for `argus/tests/` on this tree — and the AC11b citation guard gained a generic `_DIR_TOKEN` so directory citations are inside it (RED against the real pre-fix artifact); `CostSummary.live_sized_ceiling` became `int \| None = None` so a genuinely-zero sizing is no longer published as "not supplied"; `_read_critical_subsystem_set` now returns `(set, measured_reason)`, DEGRADES on an unreadable unrelated envelope instead of aborting the proof run (reason rendered into the artifact), and raises a typed error on >1 producer match rather than trusting content-addressed filename order. FILED, as the review prescribed: `DF-8-5-C` (the republished `N=0` vs the executed corpus — 5 classes / 7 rows) and `DF-8-5-D` (the renderer extraction, with the softer real blocker named and the partition-knife-edge constraint added). Added `TC-ArgusAgent-DOGFOOD-001-42/-43/-44`; STRENGTHENED `-41`'s subject-line pin from the configured exclusion to the measured one (the old form encoded the defect); zero assertions deleted, loosened or skipped. Regenerated all three dogfood artifacts and both report directories from the live generators / recorded CLI invocations after the source edits; F5 re-run at both scopes, symptom still not reproducible. **1157 → 1160 passed / 0 failed / 0 skipped**, `mypy argus` clean. Disclosed, not buried: `proof_run.py` is now 1196/1200 — 4 lines of NFR-M1 headroom — which is why `DF-8-5-D` is filed at 🟠. | Dev Agent (dev-story, fix iteration 1) |
| 2026-08-07 | 1.0 | DR-10 implemented. Preserved the Story-7.2 Minions run verbatim at a superseded sibling (AC5) BEFORE regenerating anything. Corrected the generators' subject / provenance / citations so the artifacts name the tree they actually audit — this repository's own `argus/` package — and added the DR-3 disclosures: literal `DecisionRow`, deep count/total + exact `Fraction`, assessed population (explicitly "no narrowing occurred"), the critical-subsystem clause with the vacuous-vs-real split (48 paths / 10 DR-5-ineligible / 0 unmatched, read from the run's OWN snapshot store), the ceiling honesty pair (frozen `$X` 843 + live 7.1 sizing 431, fit verdict for each), and the re-run method statement. Regenerated the three dogfood artifacts and both report directories from recorded CLI invocations. Appended an RS-4b progress note (6 of 15 consumed, 9 remain, measured), a DF-6-6-A/DF-7-2-A re-targeting note, the F5 evidence, and two new defers (`DF-8-5-A`, `DF-8-5-B`). Added `TC-ArgusAgent-DOGFOOD-001-35`…`-41`, each demonstrated RED against the pre-fix artifacts. Baseline 1147 passed / 3 failed → final **1157 passed / 0 failed / 0 skipped**, `mypy argus` clean; the 3 baseline reds reported as 2 pre-existing + 1 delta-caused. | Dev Agent (dev-story) |
