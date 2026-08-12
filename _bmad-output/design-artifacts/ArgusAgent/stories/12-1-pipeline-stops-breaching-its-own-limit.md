---
baseline_commit: ca37283baf12d05293b8fbdd62a613a58ef7353f
baseline_note: >-
  `HEAD` = `ca37283` on `master`. **The tracked tree is CLEAN** — `git status --porcelain` shows only
  untracked orchestrator/host directories (`.bmad-drift-audit/`, `_bmad-output/audit-reports/*`,
  `argusdemo/`, `bmad-dev-loop-pack/`). This is a CHANGE from every Epic-11 story: Epic 11's five
  deltas were committed as `ca37283`, so you start on a clean tree and AI-E11-5 now applies.
  `git tag -l` is **EMPTY**; `origin/master` has **not** moved. **No CI run has ever seen a line of
  Epic 10, Epic 11 or Epic 12.** Every figure in this story is **LOCAL, Windows / CPython 3.11.15**
  under the dated risk acceptance in §0.2 — carried forward, not re-taken. **Make no CI claim.**
  ⚠️ **ONE TEST IS ALREADY RED AND YOU ARE FIXING IT.** `DF-11-1-A` /
  `tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed`
  has been carved out by node id for **five consecutive stories**. §A.0 closes it in two lines and
  the fix was **verified green by execution** before this story was written. Your baseline is
  therefore **1405 collected / 1404 passed / 1 failed**, and your target is **1405 / 1405 / 0**
  plus whatever you add. **Any red that is not DF-11-1-A is yours.**
  ⚠️ **THE EPIC-11 "NO NEW `argus/**` FILE" FENCE IS LIFTED FOR EPIC 12.** See §0.1 — an operator
  ruling of 2026-08-12 pre-authorises the regeneration sequence. **Publication is still forbidden**
  (§0.3).
  ⚠️ **FOUR OF THIS STORY'S INHERITED PREMISES ARE STALE OR FALSE**, including `DF-8-2-A`'s own
  named remedy, which no longer meets `DF-8-2-A`'s own goal. See §0.4. **Do not implement the
  sentence. Implement §A.**
  **Every count, line number, LOC figure, partition id, verdict and exit code below was produced by
  EXECUTING code on THIS tree on 2026-08-12.** Treat every line number as a hint you must re-verify
  by anchor text.
story_key: 12-1-pipeline-stops-breaching-its-own-limit
epic: 12
---

# Story 12.1: The file everything lands in stops breaching its own limit

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **ArgusAgent story — Argus repo.** ArgusAgent (formerly APAA) is a self-contained headless audit
> tool extracted from the Minions monorepo into its own repository (`Agent-Argus`, distribution
> `argus-agent`, package `argus/`). **RS-1 is binding: all work lands in THIS repo. The
> `minions_core/apaa/` copy in the Minions repo is legacy — no modification, no back-port.** Planning
> artifacts live under `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is that folder's
> `sprint-status.yaml`. Prose in older documents saying `design-artifacts/APAA/`, `minions_core/apaa/`
> or `tests/apaa/` should be read as `design-artifacts/ArgusAgent/`, `argus/` and `tests/`.
>
> 🔵 **This is the FIRST story of Epic 12 and a hard enabler.** Stories 12.2 (deep-audit wiring) and
> 12.3 (memo-store wiring) both land in `argus/pipeline.py` and are explicitly gated behind it.
> **It publishes nothing.** The publish is Story **12.9** and the orchestrator halts before it.

---

## Story

As the Argus maintainer,
I want `pipeline.py` under the NFR-M1 ceiling, the ceiling enforced repo-wide, and the committed
dogfood artifacts unable to rot silently,
so that the two wirings this epic depends on are not built on a file that already fails the rule, and
so that the next seven stories do not each pay the two-step tax that halted Story 10.4.

**Why this is one story.** Every clause above is the same subject: *a maintainability standard this
project states, does not enforce, and is currently breaking*. The extraction removes the breach; the
sweep makes the breach impossible to re-acquire silently; the dogfood remedy removes the collateral
damage that any module extraction causes in this repository. Splitting them would produce a story
that fixes a number without fixing the reason the number drifted 131 lines uncaught.

**What it is NOT.** It ships **no new detector**, changes **no decision-table row, threshold, exit
code or verdict**, adds **no dependency**, changes **no user-facing output byte**, and publishes
**nothing**. It is a **pure restructuring** plus **three guards**. If any behaviour changes, you have
made a mistake — see AC5.

**Why it is not merely cosmetic.** `argus/pipeline.py` is the file three further Epic-12 stories must
edit. It is 131 lines over a cap that this project's architecture states in four places and that its
own per-module tests assert file by file — while no assertion anywhere covers `pipeline.py` itself.
That is the same shape as this project's dominant defect class: a rule that is stated, locally
asserted, and structurally unable to see the one place it is broken.

⚠️ **Read §0 before anything else. Five items gate this story.**

---

## Story Context

### Method statement — everything in §0–§F was MEASURED on this tree on 2026-08-12

Every count, coordinate, LOC figure, partition id, verdict and exit code below was produced by running
`git`, `wc -l`, `pytest`, `pytest --collect-only`, `mypy`, `bandit`, `python -m argus.cli audit .`,
and by importing and calling `argus.dogfood.partition_plan.build_full_repo_plan('.')`,
`render_partition_plan_markdown`, `render_budget_plan_markdown` and
`argus.index.partitioner._split_oversized_component` directly against the real tree. The §0.4 and §B.3
findings come from a **faithful simulation** of the partitioner's own split step over the real file
list with a modified LOC map — the baseline arm of that simulation reproduces the live partition
byte-for-byte, which is what makes its predictions load-bearing. **Re-derive everything; transcribe
nothing.**

---

## §0. The five gates on this story — read these first

### 0.1 — 🔴 OPERATOR RULING: THE EPIC-11 FENCE IS LIFTED FOR EPIC 12 (discharges AI-E11-2 / SD-1)

**Granted by XAgent007 (operator), 2026-08-12**, in response to the Epic-11 retrospective's SD-1 hard
stop. Recorded verbatim:

> SD-1 said Story 12.1 cannot execute under the regime that carried Epic 11: 12.1's extraction both
> CREATES a new `argus/**` module (moving the dogfood-audited population at `git add`) and MOVES >=131
> lines out of a unit-2 file, tripping BOTH DF-10-4-D triggers at once. Epic 11's blanket "no new
> `argus/**` file" prohibition is logically inapplicable to a story whose deliverable is creating one.
>
> **RULING:** for **EPIC 12** (not just this story), the following sequence is **PRE-AUTHORISED** —
> implement -> commit -> regenerate the dogfood artifacts **THROUGH THEIR OWN RENDERERS** at a truthful
> provenance sha -> re-run the gates. This is the same sequence the operator already ruled for Story
> 10.4, which is commit `93adc94`. The Epic-11 "no new `argus/**` file" fence is **LIFTED for Epic 12**.
> Every regenerated artifact must cite a truthful provenance sha that is an **ancestor of HEAD**, and
> the story must say so as an AC.
>
> **STILL BINDING, NOT LIFTED:** (a) nothing is published — no push, no tag, no release, no
> `workflow_dispatch`, no index upload. Publication is Story 12.9 alone. (b) A regeneration is only
> legitimate when produced by the artifacts' **own renderers** at a truthful sha; **hand-editing a
> dogfood artifact is still forbidden.**

**What this means for you, concretely.** You may create `argus/**` modules. When the dogfood guards go
red because you did, that is expected and pre-authorised — you fix it by **regenerating**, never by
loosening an assertion and never by editing the `.md` by hand. The ordering is in §C (Task 5).

### 0.2 — 🔴 DATED RISK ACCEPTANCE, CARRIED FORWARD (AI-E10-1)

**Recorded by XAgent007 (operator), 2026-08-11.** Carried forward, **not re-taken by this story**. No
CI run covers any Epic 10, 11 or 12 sha. Every figure in this story and every figure you produce is
**LOCAL, Windows / CPython 3.11.15**. CI evidence for your delta is **NOT ESTABLISHED** and you must
write that phrase rather than imply a run.

**The retrospective's own caveat, restated so it is not lost:** an acceptance inherited indefinitely
stops being an acceptance and becomes a default (Epic-11 retro §6 SD-2). Re-taking it for Epic 12 is
**AI-E11-4**, owned by the operator, and is **not this story's to take**. Do not re-take it; do not
treat its absence as a blocker either — record what you measured and label it LOCAL.

### 0.3 — 🔴 NOTHING IS PUBLISHED

No `git push`, no `git tag`, no GitHub release, no `workflow_dispatch`, no PyPI/index upload, no
marketplace listing. `git tag -l` is empty and must stay empty. Publication is Story **12.9**.
**You DO commit** — see §0.5.

### 0.4 — 🔴 FOUR INHERITED PREMISES ARE STALE OR FALSE (AI-E10-3, discharged at create-story time)

Re-measured by **execution** on this tree, 2026-08-12. The full table is §B.1. The four that change
what you build:

1. **`DF-8-2-A`'s own named remedy is now insufficient.** The ledger says close it by *"extract a
   shell-helper module (e.g. `argus/pipeline_facts.py` carrying `_critical_ineligibility` and its
   siblings)"*. Measured: that family (`_critical_ineligibility` -> `_critical_candidates`,
   `argus/pipeline.py:406-465`) is **~59 lines**. You must shed **>= 131**. The prescribed remedy
   leaves the file at ~1272 — **still over the cap**. It was written when the file was 1199 and needed
   to shed one line. **Do not implement it as written.** See §A.1 for the measured alternative.
2. **The NFR-M1 breach is NOT confined to `argus/**`.** Measured over all **169** tracked `.py` files,
   **four** exceed 1200 lines, not one:
   `argus/pipeline.py` **1331** · `tests/test_pipeline_signature_demo.py` **1326** ·
   `tests/test_v1_commitment_closure.py` **1308** · `tests/test_grammar_diagnosis.py` **1203**.
   The project's own per-module NFR-M1 tests assert *"this test file is <= 1200 lines"*, so test files
   are unambiguously in scope for the standard. A naive repo-wide sweep is **red on four files**. §A.2
   rules how to handle that without turning this story into a test-file refactor.
3. **`architecture.md` §Enforcement claims an enforcement that does not exist.** It says NFR-M1 is
   *"enforced by ... file-size CI — committed under `tests/apaa/`"*. Measured: `tests/apaa/` **does not
   exist**, and `grep` over `.github/workflows/*.yml` (`argus-student-audit.yml`, `audit-ci.yml`,
   `release.yml`) finds **no file-size step**. The architecture asserts a guard that was never built.
   §A.4 corrects it in the same change that makes it true.
4. **The committed dogfood artifacts are STALE RIGHT NOW, at HEAD, with all five guards GREEN.** This
   is the single most important finding in this story and it changes the remedy. See §0.5 and §B.2.

### 0.5 — 🔴 THE DOGFOOD GUARDS ARE VACUOUS AGAINST THE ROT THEY CLAIM TO PREVENT

`DF-8-5-B` and `DF-10-4-D` describe the guards as *breaking too often*. Measured today, the opposite
failure is **also live and worse**: they are **green over three artifacts that are already wrong**.

Rendered live at HEAD and diffed against the committed files:

| Artifact | Field | Committed | Live at HEAD |
|---|---|---|---|
| `minions-dogfood-partition-plan.md` | Provenance sha | `a9cc933` | `ca37283` |
| | Total physical LOC | 19783 | **20454** |
| | Recorded cut edges | 57 | **64** |
| | Unit 2 LOC | 14793 | **14997** |
| | Unit 3 LOC | 3660 | **4127** |
| `minions-dogfood-budget-plan.md` | Build-cost proxy | 19783 | **20454** |
| | NFR-C1 baseline ratio | `360/19783` | **`60/3409`** |
| `minions-dogfood-proof.md` | Provenance sha / LOC | `a9cc933` / 19783 | `ca37283` / **20454** |

**Every one of the five `DF-10-4-D` assertions is GREEN over that table.** They are green because of
what they actually assert, which is far less than what their own docstrings claim:

- `TC-ArgusAgent-DOGFOOD-001-03` — docstring: *"the artifact cannot silently rot away from the
  generator."* Asserts: the literal `Unit count: 3`, each `partition_id[:12]` substring, and the
  presence of the word `Reused planner`. **It cannot see a single figure in the table above.**
- `-06` — asserts `sized_ceiling` (450, unchanged) is present.
- `-41` — asserts subject-honesty tokens.
- `-20` — asserts the live verdict token, exit code, `843`, the grade, and three headings.

**This is AI-E11-1's question answered in the affirmative: the defect exists while every observable is
unchanged.** It is the fifth-plus instance of this project's dominant defect class, and it is sitting
in the exact surface this story is chartered to fix. **Therefore the `DF-8-5-B`/`DF-10-4-D` remedy
"name a regeneration entry point in the failure message" is necessary but NOT sufficient** — it
improves a red that today never appears. §A.3 specifies the remedy that closes both directions, and
its RED-first demonstration is free, because **it is red on this tree right now**.

---

## Acceptance Criteria

> **Guard-adequacy clause (AI-E11-1) — binding on every AC below that ships a test.** For each
> committed guard, the implementation notes must state (i) the guard's **observable**, (ii) a
> demonstration that the defect **moves that observable** — proven RED at the **real seam**, with the
> **final** test code, not a reconstruction — and (iii) at least one adversarial variant **generated**
> from the structure the guard closes over (with its count), not hand-listed. A guard that cannot be
> shown red against the defect it names is not evidence.

### AC1 — Every `argus/**` file is at or under 1200 lines, measured and recorded

**Given** `DF-8-2-A` recorded `pipeline.py` at 1199/1200 and warned *"the next edit of any size
breaches NFR-M1"*, and it is now **1331** (re-measured 2026-08-12)
**When** the extraction completes
**Then** `git ls-files -- argus | xargs wc -l` shows **no file over 1200**, and the story records the
before/after line count of every file created or modified.

**And** the extraction is a **cohesion split**, not a line-count shave: the moved code is a family that
belongs together, the module docstring names why the module exists (the `argus/pipeline_persist.py`
precedent, §B.4), and no function is split across the boundary.

**And** the public import surface is **unchanged**: `argus.pipeline.__all__` still exports
`PipelineError`, `ResumeStateError`, `AuditResult`, `run_audit`, `run_audit_detailed`,
`resume_audit_detailed`, `resume_audit`, and every existing `from argus.pipeline import X` in `argus/`
and `tests/` still resolves. Pinned by test.

### AC2 — A repo-wide sweep makes a silent breach impossible

**Given** NFR-M1 is enforced **per-module and ad hoc** — `tests/test_cache_invalidation.py:690`,
`tests/test_cartridge_selfaudit.py:472`, `tests/test_dogfood_module_split.py:168`,
`tests/test_dogfood_plan.py:485`, `tests/test_dogfood_proof.py:629`,
`tests/test_evidence_bundle.py:497`, `tests/test_hitl_escalation.py:614`,
`tests/test_memo_store.py:497` — **with no repo-wide sweep and no assertion covering `pipeline.py`**,
which is why 131 lines of drift went uncaught
**Then** a committed sweep test asserts the ceiling over **every tracked `.py` file**, enumerated from
`git ls-files '*.py'` — never hand-listed.

**And** the population is **non-vacuous**: the test asserts the enumeration is non-empty and covers
both `argus/` and `tests/`, so a broken glob turns it **red**, not silently green.

**And** the **boundary** is pinned in both directions: a synthesized file of exactly 1200 lines passes
and 1201 fails, driven through the sweep's own predicate.

**And** the three breaching test files (§0.4 item 2) are **named exemptions carrying a written reason
and a date**, following this repository's established `_EXCLUDED_BY_DESIGN` / `_PRESERVED_RECORD`
precedent (`tests/test_evidence_citation.py:91`, `tests/test_release_surface_honesty.py:178` —
re-measured; `test_evidence_citation.py`'s own comment cites the latter at `:89-96`, which is stale)
— **never silence, never a narrowed population**.

**And** the exemption registry is a **shrinking** allow-list, not a parking lot: the test fails if an
exemption names a file that no longer exists **or that is no longer over the cap**, so a fixed file
cannot leave dead weight behind. `argus/pipeline.py` **must not** appear in it.

**And** each exemption is filed in `deferred-work.md` with an owner and a target story, so the three
test-file breaches carry a date and an owner (AI-E11-10's alternative DoD) rather than vanishing into
a registry.

### AC3 — The committed dogfood artifacts cannot rot silently, and a red says how to fix it

**Given** `DF-8-5-B` and `DF-10-4-D` are both open, both name the same class, and `DF-10-4-D`
supersedes `DF-8-5-B` with a stronger trigger (`git ls-files` reads the **index**, so the population
moves at `git add`, before any commit)
**And** re-measurement shows the guards are **currently green over three stale artifacts** (§0.5)
**Then** a committed guard fails whenever a committed dogfood artifact no longer describes the tree it
cites — closing **both** directions of the defect, the noisy one and the silent one.

**And** the guard's failure message **names the exact regeneration command**, so the remedy is
discoverable from the red output. This is `DF-8-5-B`'s stated close condition and it is **not
optional**.

**And** the artifacts' **claimed** provenance and their **actual** enumeration are reconciled and the
choice is recorded: `DF-10-4-D` measured that they claim `HEAD` provenance in their own Provenance
block while enumerating `git ls-files` (the **index**), *"and those are two different trees."* State
which tree the artifacts describe, and make the code and the prose agree.

**And** the fix is **not** a loosened assertion. `DF-8-5-B`: *"Do not close it by loosening an
assertion."* Widening `-03` to see more of the artifact is a strengthening and is welcome; deleting an
assertion is a violation.

**And** every regenerated artifact cites a provenance sha that is a **real commit and an ancestor of
`HEAD`** — asserted by test, not by inspection (§0.1's ruling made mechanical). At the last honest
regeneration this held: `git diff a9cc933 93adc94 -- argus/` is **empty** and `a9cc933` is an ancestor
of `HEAD`. It does **not** hold today.

### AC4 — Every ledger item that gates on this extraction is closed or re-recorded with a reason

**Given** `DF-8-2-A`, `DF-8-3-A`, `DF-8-3-C`, `DF-8-5-B` and `DF-10-4-D` all name this extraction
**Then** each is **closed with its evidence** or its **remaining scope is re-recorded with a reason and
a new target story** — none is left pointing at work that has now happened.

**And** `DF-8-3-A`'s recorded blocker is explicitly discharged: it deferred *"AFTER the DF-8-2-A
shell-helper extraction has made room in `pipeline.py`"*. This story **makes that room**. If it is not
closed here, the entry must say that the room now exists and name the new reason — not repeat the old
one. (§A.5 rules it.)

**And** the append-only discipline holds (§3.4): nothing above the new heading in `deferred-work.md`
is edited, reordered or deleted. Prove it with `git diff --numstat` showing **0** deletions on that
file.

### AC5 — Behaviour is proven untouched, not assumed

**Given** the extraction is pure restructuring
**Then** the full suite passes with **no test modified to accommodate the move** other than import-path
updates that are enumerated in the File List, and `mypy` is clean over the same source count.

**And** a dogfood re-run produces an **identical verdict**: `argus audit .` returns
`verdict=RELEASE_READY deep_ratio=61/169 blocking_findings=0 assessed_deep_ratio=61/77
scope=application held_out=92`, **exit 0** — the figures measured on this tree at `ca37283` before any
change. A change in **any** of those numbers is a behaviour change and fails this AC.

**And** the four report artifacts and the `.argus/` persisted output are **byte-identical** across the
change for a fixed input, or the difference is explained and shown to be provenance-only.

**And** the Story 6.1 determinism quarantine, the `argus.* ⊬ fastapi` import-isolation gate and the
Story 11.2 `ast`-walk over `argus/pipeline.py`
(`tests/test_classification_word_boundary.py::TC-ArgusAgent-PIPELINE-002-11`) all still pass. **Note:
`-11` parses `argus/pipeline.py` by name and walks its control flow** — if you move code it reads, it
goes red. That red is the guard working; fix the guard's reach, do not narrow its claim.

### AC6 — `DF-11-1-A` is closed, and this story's baseline is honestly stated

**Given** `tests/test_evidence_citation.py::TC-ArgusAgent-DOCS-001-22` has been carved out **by node
id by five consecutive stories** and this story would be the sixth
**Then** `epic-10-retro-2026-08-11.md` and `epic-11-retro-2026-08-12.md` are registered in
`_STATUS_DOCUMENTS`, the suite is **1405/1405/0** before your delta, and `DF-11-1-A` is marked CLOSED
with a date.

**And** no signed retrospective is edited and no citation is minted. **Verified by execution before
this story was written:** `_status_assertions()` returns **0** assertions for both documents, so
registration is inert against every other assertion in that file (§B.5).

**And** if registration turns any *other* assertion red — it will not, but if it does — you **HALT and
report**. You do not loosen `test_evidence_citation.py` and you do not edit a retrospective.

---

## Tasks / Subtasks

- [x] **Task 0 — Establish the baseline by execution, before touching anything (AC5, AC6)**
  - [x] Confirm `git rev-parse HEAD` = `ca37283…` and `git status --porcelain` shows only the untracked
        host dirs from the frontmatter. If the tree is dirty in `argus/` or `tests/`, **HALT** — you
        did not dirty it and you must not tidy it.
  - [x] `pytest -q` -> record collected/passed/failed. Expect **1405 / 1404 / 1**, the single red being
        `DOCS-001-22`. Any other red: **HALT**.
  - [x] `mypy argus` (expect *no issues found in 72 source files*), `bandit -r argus`
        (expect **0 High / 0 Medium / 19 Low**).
  - [x] `python -m argus.cli audit .` -> record the full verdict line and exit code verbatim. This is
        AC5's fixture.
  - [x] Record `wc -l` for `argus/pipeline.py` and for every file you intend to touch, with `sha256`.

- [x] **Task 1 — Close `DF-11-1-A` first, on its own (AC6)**
  - [x] Add the two retro filenames to `_STATUS_DOCUMENTS` in `tests/test_evidence_citation.py`.
  - [x] `pytest tests/test_evidence_citation.py -q` -> green. Full suite -> **1405/1405/0**.
  - [x] Do this **before** the extraction so your post-extraction baseline is a clean green.

- [x] **Task 2 — Land the repo-wide NFR-M1 sweep RED-FIRST (AC2)**
  - [x] Write the sweep in a new `tests/test_module_size_ceiling.py` **before** the extraction, with
        `argus/pipeline.py` **not** exempted. Run it. It **must be RED**, naming `pipeline.py` at 1331.
        Capture that output — it is AC2's guard-adequacy evidence (ii), at the real seam, with the
        final test code.
  - [x] Add the three test-file exemptions with written reasons + date; re-run; now red **only** on
        `pipeline.py`.
  - [x] Add the non-vacuity assertions and the 1200/1201 generated boundary pair.
  - [x] Add the shrinking-registry assertion (an exemption for a file that is no longer over the cap
        fails).

- [x] **Task 3 — Extract the cohesion family from `pipeline.py` (AC1, AC5)**
  - [x] Re-derive the candidate boundary yourself (§A.1 gives the measured recommendation and its
        numbers — verify them, do not transcribe them).
  - [x] Create the new module with a docstring in the `argus/pipeline_persist.py` form: drivers, why
        this module exists, what stayed behind, and the explicit *no-behaviour-change* statement.
  - [x] Re-export from `argus/pipeline.py` so every existing import site resolves unchanged; leave
        `__all__` byte-identical.
  - [x] `wc -l` both files. Re-run the sweep: **green**.
  - [x] Full suite + `mypy` + `bandit`. Enumerate every test whose import path you had to touch.
  - [x] `python -m argus.cli audit .` -> verdict line **identical** to Task 0. If not, stop and find
        out why before proceeding.

- [x] **Task 4 — Rule and record the ledger items (AC4)**
  - [x] `DF-8-2-A` — close with evidence, **and record that its own named remedy was measured
        insufficient** (§0.4 item 1) so the next reader does not repeat it.
  - [x] `DF-8-3-C` — close by adding the shared helper and calling it from both sites (§A.5), or
        re-record with a reason.
  - [x] `DF-8-3-A` — apply §A.5's ruling and record it either way.
  - [x] `DF-8-5-B` / `DF-10-4-D` — close **together, never separately** (`DF-10-4-D`'s own
        instruction), citing the AC3 guard.
  - [x] `DF-11-1-A` — CLOSED, dated.
  - [x] Append-only proof: `git diff --numstat -- <deferred-work.md>` shows **0** deletions.

- [x] **Task 5 — Commit, then regenerate, then re-run (AC3) — THIS ORDER, it is the bootstrap**
  - [x] `git add` the full delta **including this story file** (untracked story files are AI-E8-1).
  - [x] Commit. This commit contains the `argus/**` delta and is the **truthful provenance sha**.
  - [x] Regenerate all three dogfood artifacts **through their own renderers** —
        `render_partition_plan_markdown`, `render_budget_plan_markdown`, `render_proof_markdown` —
        writing the rendered output verbatim. **No hand-editing. Not one character.**
  - [x] Commit the regenerated artifacts as a **separate** commit, exactly as `93adc94` did.
  - [x] Verify the invariant: `git diff --quiet <provenance-sha> HEAD -- argus/` is **empty** and
        `git merge-base --is-ancestor <provenance-sha> HEAD` succeeds.
  - [x] Re-run the **full** suite, `mypy`, `bandit`, `argus audit .`. Everything green; verdict
        identical to Task 0.

- [x] **Task 6 — Land the AC3 guard and the §Enforcement registration (AC3, AC2)**
  - [x] Demonstrate the AC3 guard RED **on the pre-regeneration tree** (it is red at `ca37283` today —
        that is your free RED-first, §0.5) and GREEN after regeneration. Capture both.
  - [x] Register the NFR-M1 sweep rule **and** the artifact-currency rule in `architecture.md`
        §Enforcement in the established form (rule text + enforcing module + test ids), and **correct
        the false "file-size CI / `tests/apaa/`" claim** in the same edit (§0.4 item 3).
  - [x] Add the `-NN` assertion that the §Enforcement text and this registration are still present,
        following `-23` / `-41` / `-52` / `-53` / `-55`.
  - [x] Add the release-note section **only if** a user-visible surface changed. It did not — record
        that decision (§A.6).

- [x] **Task 7 — Final gates and honest reporting**
  - [x] Full suite / `mypy` / `bandit` / `argus audit .` one final time, on the final tree.
  - [x] Record every figure as **LOCAL, Windows / CPython 3.11.15**; write **CI evidence: NOT
        ESTABLISHED**.
  - [x] `sha256` every file in the File List.

---

## §A. What to build — the rulings

### A.0 — `DF-11-1-A` (AC6): verified, not assumed

Registration is a two-line edit. It was **executed** before this story was written: loading
`tests/test_evidence_citation.py` and calling `_status_assertions()` on both retro documents returns
**0** status assertions for each, so the per-document loop hits `continue` and every other assertion in
the file is untouched. Both files exist, are non-empty and parse to far more than 10 sentences. The
`missing` check at `:548` is satisfied because both are found by the `epic-*-retro-*.md` glob.

**Ruling, and why it is in this story rather than left with the operator.** AI-E11-3 assigns it to
XAgent007 as type (H). The Epic-11 retrospective's own sharpest conclusion is that *"items addressed to
a human's discretion do not execute in this project ... the only reliable way to make something happen
here is to make a story unable to proceed without it."* This story's central AC5 is *"the full suite
passes, behaviour untouched"* — an AC whose evidentiary value is materially degraded by a carried red.
The cost is two lines; nothing is decided, only registered; no signed document is edited and no
citation is minted. **Project standards win over role boundaries here**, and the standard being served
is the project's own.

### A.1 — The extraction (AC1): measured recommendation, not a prescription

**The measured facts.** `argus/pipeline.py` is 1331 lines and must shed **>= 131**.

| Candidate family | Location | Lines | `pipeline.py` after |
|---|---|---|---|
| `_critical_ineligibility` + `_critical_candidate` + `_critical_candidates` (`DF-8-2-A`'s named remedy) | `:406-465` | ~59 | **~1272 — STILL OVER** |
| Cost/budget helpers (`_build_cost_ledger` … `_skipped_remainder_entries`) | `:589-688` | ~99 | ~1232 — still over |
| **The resume family** — `_list_locators`, `_to_native_payload`, `_read_prior_state`, `_carried_forward_entries`, `resume_audit_detailed`, `_merge_findings`, `resume_audit` | `:975-1331` | **357** | **~980 — 220 lines of headroom** |

**Recommendation: extract the resume family into `argus/pipeline_resume.py`.** It is the strongest
candidate on every axis that matters here:

- It is **already a delimited cohesion unit** in the file: `pipeline.py:975-988` carries its own banner
  — *"Story 3.4 — resumability from on-disk `.argus/` state (FR31 / NFR-R2) — The IMPURE resume
  shell"* — and states its own single concern. A cohesion split does not have to be invented; it has
  to be honoured.
- **One extraction is enough.** 357 lines clears the cap with 220 lines of headroom, which is what
  12.2 (deep-audit wiring) and 12.3 (memo-store wiring) need. Two extractions would clear it too, but
  **every new `argus/**` module costs a dogfood regeneration and shifts partition ids** (§B.3) — so
  the number of new modules is a real cost, not a style preference. Prefer **one**.
- It follows the **exact established precedent**: `argus/pipeline_persist.py` (Story 6.3,
  `DN-PIPELINE-SPLIT`) was created for this identical reason at 1190/1200 and its docstring records
  the doctrine — *"a PURE no-behavior-change refactor ... the functions are byte-identical to their
  pre-6.3 form; `pipeline.py` imports them and the public entrypoints + their import locations are
  unchanged."* Follow it exactly, including the sibling-module naming (`pipeline_*.py`) and the
  two-sided docstring note (in **both** modules, per §3.2).

**The one complication `pipeline_persist.py` did not have:** `resume_audit` and `resume_audit_detailed`
are **public** (`argus/pipeline.py:221-229`, `__all__`). They must be re-imported into `pipeline.py`
and `__all__` left byte-identical, so `from argus.pipeline import resume_audit` keeps working. Pin that
with a test — an import-surface regression here would be invisible to the dogfood verdict and visible
to a consumer.

**You may choose a different boundary** if you measure a better one. What you may not do: shave lines,
split a function, change `__all__`, or leave the file over 1200. Record your boundary and your reason.

### A.2 — The sweep's population (AC2): all tracked `.py`, with named dated exemptions

**The decision.** Enumerate **every tracked `.py`** via `git ls-files '*.py'` (169 files today), and
carry the three known test-file breaches as **named exemptions with written reasons and a date**.

**Why not `argus/**` only** — it would be green today over three files that breach a standard the
project's own per-module tests assert file by file. Narrowing a population until the guard is green is
the exact move this project treats as a defect.

**Why not "fix all four"** — splitting `test_pipeline_signature_demo.py` (1326),
`test_v1_commitment_closure.py` (1308) and `test_grammar_diagnosis.py` (1203) is a substantial refactor
of three of this repository's most load-bearing guard files, in a story whose defining AC is *behaviour
untouched*. That is a different story with a different risk profile. It is deferred **visibly**, not
silently.

**Why `git ls-files` and not a filesystem walk** — a walk picks up `.venv/`, `__pycache__` and
untracked scratch. `DF-10-4-D` correctly warns that `git ls-files` reports the **index**; for *this*
guard that is the desirable behaviour (your new module is checked the moment you stage it, which is
when you want to know), and it must be stated in the test's docstring so the next reader is not
surprised.

**Anti-vacuity is mandatory** (AC2): non-empty enumeration, coverage of both trees, a generated
1200/1201 boundary pair, and a shrinking registry. A sweep that goes green by enumerating nothing is
the failure mode this whole story exists to close.

### A.3 — The dogfood remedy (AC3): the property, and a validated mechanism

**The property the AC requires:** a committed dogfood artifact that no longer describes the tree it
cites must turn a committed guard **RED**, and that red must name the regeneration command.

**A mechanism that satisfies it, validated against real history — you may use it or better it:**

> An artifact is **current** iff (a) the provenance sha it cites is a real commit and an ancestor of
> `HEAD`, and (b) `git diff --quiet <cited-sha> HEAD -- argus/` is empty — i.e. **nothing in `argus/**`
> has changed since the tree the artifact says it describes**.

**Why this is the right shape, and why it is not a loosened assertion:**

- It is a **closure over the real structure** (the actual `argus/**` content delta) rather than a list
  of three tokens the artifact happens to contain — AI-E10-5, *the list is never the contract*.
- It is **RED-first for free**: it is red at `ca37283` **today**, on the real defect, with no
  reconstruction. `git diff a9cc933 HEAD -- argus/` = 7 files, 749 insertions, 78 deletions.
- It would have been **GREEN at the last honest regeneration**: `git diff a9cc933 93adc94 -- argus/`
  is **empty** (93adc94 touched only `.md` and `.yaml`), and `a9cc933` is an ancestor of `HEAD`. Both
  verified by execution. So it does not simply fail always — it distinguishes the honest state from
  the rotten one, which is the whole requirement.
- It **subsumes** `DF-8-5-B`'s stated remedy rather than replacing it: the failure message still names
  the regeneration entry point, and now the message actually appears when the artifacts are wrong.
- It does **not** go red on every commit the way naive byte-equality would (which would re-red on the
  provenance sha alone and make the two-step tax permanent). It goes red exactly when `argus/**`
  moved, which is exactly when the figures are wrong.
- It **mechanises §0.1's ruling**: "cites a truthful provenance sha that is an ancestor of HEAD"
  becomes an assertion instead of a promise.

**Also required by AC3 and easy to forget:** reconcile the Provenance block's claim with the
enumeration. `enumerate_minions_source_files` calls `git ls-files argus` (**index**) while the
rendered block says *"Commit descriptor (HEAD at generation)"*. Either the label tells the truth about
what was enumerated, or the enumeration is pinned to the commit (`git ls-files --with-tree=HEAD`).
Decide, implement, and record which — `DF-10-4-D` asks for exactly this and calls it *"the honest
[narrower fix]"*.

**Strengthening `-03` is welcome**; deleting an assertion is a violation.

### A.4 — `architecture.md` §Enforcement (AC2/AC3)

Register both new rules in the established form (rule text + enforcing module + test ids + a
non-vacuity note), beside the 10.1 / 10.3 / 10.4 / 10.5 / 11.1 / 11.2 / 11.4 registrations, and add the
`-NN` assertion that the text is still present. In the **same** edit, correct the §Enforcement sentence
claiming NFR-M1 is enforced by *"file-size CI — committed under `tests/apaa/`"*: `tests/apaa/` does not
exist and no workflow contains a file-size step. **An architecture that claims an enforcement it does
not have is the same defect class this story is closing** — it must not survive the story that makes
the claim true.

Do **not** attempt AI-E11-1's own promotion (the guard-adequacy clause into §Enforcement) — that is
assigned to the Architect and is not this story's. Applying the clause, as this story does, is the
part that binds you.

### A.5 — The ledger rulings (AC4)

| Item | Ruling | Reason |
|---|---|---|
| **`DF-8-2-A`** | **CLOSE**, and record that its own named remedy was measured insufficient | The extraction happens here. The entry's prescription (`pipeline_facts.py`, ~59 lines) was correct at 1199 and is not at 1331. Recording that is the difference between a closed entry and a closed entry that teaches. |
| **`DF-8-3-C`** | **CLOSE** — add the shared helper, call it from both sites | Pure de-duplication with no behaviour change; sits squarely inside this story's charter. ⚠️ **Its recorded coordinates are STALE**: the entry names `pipeline.py:686-694` and `generator.py:86-93`; re-measured they are **`argus/pipeline.py:745`** and **`argus/reports/generator.py:176`**. Find them by anchor text. The entry names `argus/detectors/vacuous_test.py` (beside `is_test_file`) as the helper's home — an **existing** file, so it costs no new module. |
| **`DF-8-3-A`** | **RE-RECORD with a new reason and target Story 12.4** | Its recorded blocker — *"no room in `pipeline.py`"* — is **discharged by this story**, and the entry must say so. What remains is a **scope** ruling, not a room ruling: threading `CriticalSubsystemSet.heuristic_excluded_ineligible` into `generate_reports` and naming the vacuity in prose is a **report-content change**, which AC5 of this story forbids by construction (*behaviour untouched, verdict identical, report bytes identical*). Its natural home is **Story 12.4**, whose entire subject is what a terminal outcome says and why — including the `INSUFFICIENT_COVERAGE` and critical-subsystem explanations this disclosure belongs beside. Re-recording it with a live target is what the epic AC asks for (*"closed **or** its remaining scope re-recorded with a reason"*), not a dodge. |
| **`DF-8-5-B` + `DF-10-4-D`** | **CLOSE TOGETHER** via AC3 | `DF-10-4-D` instructs: *"supersede or close them together, never separately."* Record the §0.5 finding — that the class had a second, silent direction neither entry measured — as part of the closure. |
| **`DF-11-1-A`** | **CLOSE**, dated (§A.0) | |
| **`DF-10-2-A`** | **RULE OUT of this story** | 🟠, unowned for two epics, and named critical-path twice (AI-E10-4, AI-E11-7). It is about C/C++/Ruby/Rust grounding with zero definition extraction — **no relationship to `pipeline.py`, NFR-M1, or the dogfood artifacts**. AI-E11-7 asks for a **dated operator decision** (*"a fix is probably not needed ... what is needed is a dated decision"*), which is type (H) and outside a dev agent's authority to take. Folding an unrelated governance decision into a restructuring story would be scope creep in the one story that must prove *nothing changed*. **It stays open and unowned, and this story says so out loud rather than quietly not mentioning it.** |
| **`DF-11-4-D`** (AI-E11-6, `_NOTE_SECTIONS` impact rank) | **RULE OUT of this story → target Story 12.4** | See §A.6. |

### A.6 — `DF-11-4-D` / AI-E11-6: ruled OUT of 12.1, INTO 12.4

The Epic-11 retrospective recommends the `_NOTE_SECTIONS` rework be *"naturally folded into Story
12.1's write set"* (~15 lines, type (S)). **Ruled otherwise, for three measured reasons — recorded
here because the instruction was to rule either way:**

1. **The trigger does not fire at 12.1.** AI-E11-6's stated urgency is *"before Epic 12 adds nine more
   release-note sections"* and `DF-11-4-D`'s rule of thumb is *the next story that edits the file*.
   **This story adds no release-note section** — it changes no user-visible surface (AC5 forbids it),
   so it does not touch `_NOTE_SECTIONS` at all. Folding the rework in would mean editing a registry
   this story otherwise has no reason to open, which is precisely the *"routinely widened to fit
   whatever the current story needs"* pattern `DF-11-4-D` was filed about.
2. **Single-purpose.** 12.1's write set is already large and load-bearing: an extraction, a repo-wide
   sweep, a dogfood-currency guard, an architecture registration, five ledger rulings and a two-commit
   regeneration sequence. Adding an unrelated guard redesign raises the probability the load-bearing
   work is done badly — and the retrospective's own §3.1 finding is that this project's defects come
   from guards written under load.
3. **12.4 owns the vocabulary.** AI-E11-6's proposed rank vocabulary is
   `changes_exit_code` > `changes_verdict` > `security_on_executable_surface` > `changes_no_observable`
   — an **outcome-impact** vocabulary. Story 12.4 must enumerate exactly those outcomes and their
   consequences to satisfy FR37, and it is the first Epic-12 story that certainly **does** add a note
   section. Designing the rank there costs less and is more likely to be right.

**AI-E11-6's alternative DoD is explicitly NOT taken:** this is not a dated acceptance that the
narrative convention is fine. It is a **re-targeting**. Record it in `deferred-work.md` as
`target_story: 12-4-every-outcome-names-its-next-action`, so the item has a live owner and does not
become a sixth unowned carry.

---

## §B. Measured evidence

### B.1 — Premise re-measurement (AI-E10-3), 2026-08-12, `HEAD` = `ca37283`, LOCAL Windows / CPython 3.11.15

| Premise (source) | Re-measured by execution | Verdict |
|---|---|---|
| `pipeline.py` = 1331 vs cap 1200 (retro SD-5, epics, sprint-status) | 1331 | **HELD** |
| `pipeline.py` is the only `argus/**` file over the cap | Only file > 1000 lines in `argus/`; all others well under | **HELD** |
| `git ls-files -- argus` = 72 | 72 | **HELD** |
| Suite = 1405 collected / 1404 pass / 1 red | 1405 / 1404 / 1 | **HELD** |
| The single red is `DF-11-1-A` (`DOCS-001-22`) | Confirmed; no other failure | **HELD** |
| `mypy` clean on 72 sources | *Success: no issues found in 72 source files* | **HELD** |
| `bandit` 0 High / 0 Medium / 19 Low | 0 / 0 / 19 | **HELD** |
| Dogfood unit 2 = 14997 LOC vs 15000 soft ("3 lines of slack") | 14997; soft ceiling 15000 | **HELD** |
| Unit 2 file count vs the 40-file soft limit | **39 / 40** — one file of slack, not previously recorded | **NEW** |
| `git tag -l` empty, `origin/master` unmoved | Both confirmed | **HELD** |
| Working tree dirty with six ` M` `argus/` files (11.5's baseline) | **Tracked tree is CLEAN**; Epic 11 committed as `ca37283` | **STALE — CHANGED** |
| `DF-8-2-A`'s remedy (`pipeline_facts.py`, `_critical_ineligibility` + siblings) suffices | ~59 lines; **>= 131 required**; leaves ~1272 | **STALE — remedy insufficient** |
| `DF-8-3-C` sites at `pipeline.py:686-694`, `generator.py:86-93` | Now `argus/pipeline.py:745`, `argus/reports/generator.py:176` | **STALE coordinates** |
| `DF-8-3-A` blocked by "no room in `pipeline.py`" | Room is created by this story; only a scope reason remains | **CHANGED** |
| NFR-M1 breach confined to `argus/**` | **4** tracked `.py` files breach: 1331 / 1326 / 1308 / 1203 | **FALSE** |
| `architecture.md`: NFR-M1 enforced by "file-size CI under `tests/apaa/`" | `tests/apaa/` absent; no file-size step in any of the 3 workflows | **FALSE AS WRITTEN** |
| `DF-8-5-B`/`DF-10-4-D`: the guards break too often | True — **and** they are green over three already-stale artifacts today | **UNDERSTATED** |
| Epic 12.4's quoted self-audit `deep_ratio=57/149 … held_out=76` | Now `61/169`, `assessed 61/77`, `held_out=92` | **STALE (12.4's problem, flagged here)** |

### B.2 — The stale-artifact measurement (§0.5)

Produced by rendering live and diffing against the committed files. Full table in §0.5. Supporting
history, verified: `a9cc933` **is** an ancestor of `HEAD`; `git diff a9cc933 93adc94 -- argus/` is
**empty**; `git diff a9cc933 HEAD -- argus/` = **7 files, +749 / −78**; `93adc94` touched only three
`.md` artifacts, `sprint-status.yaml` and one story file.

### B.3 — What your new module will do to the partition (simulated on the real structure)

`argus/pipeline.py` lives in **unit 2** (39 files / 14997 LOC / `82a3d605e61e`). Units 2 and 3 are the
two halves of one oversized cohesion component, split greedily by
`argus/index/partitioner.py::_split_oversized_component`, which **never** lets a unit exceed the soft
target (40 files / 15000 LOC).

The split step was re-run over the real file list with a modified LOC map. **The baseline arm
reproduces the live partition exactly** (39/14997/`82a3d605e61e`, 12/4127/`ed6d08f25ce3`), which is
what makes the rest load-bearing:

| New module (with `pipeline.py` -> 1150, new file 220) | Resulting units | Ids changed |
|---|---|---|
| `argus/pipeline_stages.py` | 39/14778 `45cbaf975494` · 13/4385 `9408a0fe1acf` | **both** |
| `argus/verdict/stages.py` | 39/14816 `82a3d605e61e` · 13/4347 `cd400bde7ea5` | unit 3 only |
| `argus/audit/stages.py` | 39/14778 `5bd97f63c7d1` · 13/4385 `9408a0fe1acf` | **both** |

**Conclusions you can rely on:**
- **Unit count stays 3** under every placement tested, so `-03`'s `Unit count: 3` assertion survives.
- **At least one `partition_id` changes under every placement.** `TC-ArgusAgent-DOGFOOD-001-03` **will
  go RED.** That is expected, pre-authorised (§0.1) and fixed by regeneration — never by editing the
  `.md`.
- A late-alphabet placement (`argus/verdict/…`, `argus/shared/…`) preserves unit 2's id. **Do not let
  this drive the design.** Regeneration is required either way, and `argus/pipeline_resume.py` — a
  sibling of the file it came from, following the `pipeline_persist.py` precedent — is the honest
  name. Naming a module to flatter a hash is exactly the kind of thing this project files as a defect.
- The soft-ceiling breach itself is **not** a test failure: only the **hard** ceiling (60 files /
  25000 LOC) is asserted (`TC-ArgusAgent-DOGFOOD-001-01`), and unit 2 is already
  `context_pressure=True`. The "3 lines of slack" is real but its consequence is a **re-split and new
  ids**, not a red envelope assertion.

### B.4 — The precedent you are following

`argus/pipeline_persist.py` (268 lines, Story 6.3, `DN-PIPELINE-SPLIT`). Its docstring is the template
for yours — read it in full before writing. Load-bearing lines:

> *"`pipeline.py` reached the §3.2 1200-line hard limit (1190/1200) at Story 6.2, so the Story 6.3
> orphan-detector WIRING had no room to land. Per DN-PIPELINE-SPLIT this is a PURE no-behavior-change
> refactor ... The functions are byte-identical to their pre-6.3 form; `pipeline.py` imports them and
> the public `run_audit` / `run_audit_detailed` / `resume_audit_detailed` entrypoints + their import
> locations are unchanged. The verdict math / persist order / producer tokens are UNCHANGED — only the
> home of the persist helpers moved (the split documented in BOTH this docstring and `pipeline.py`'s
> docstring, §3.2)."*

Note the last clause: **both** docstrings. `argus/pipeline.py:231-236` already carries the 6.3 note;
add yours beside it.

### B.5 — `DF-11-1-A` registration, verified green before this story was written

`_status_assertions()` over `epic-10-retro-2026-08-11.md` -> **0** assertions.
Over `epic-11-retro-2026-08-12.md` -> **0** assertions. Both are found by the `epic-*-retro-*.md` glob
and both parse to well over 10 sentences, so `-21`'s non-vacuity floor and `-22`'s `missing` check are
both satisfied by registration alone.

---

## §C. Sequencing (why the order in Tasks is not negotiable)

`DF-10-4-D` names the **bootstrap ordering hazard** explicitly: *"12.1 is the story that owns the
remedy and the story most certain to trip the defect before the remedy exists, so it must regenerate
first and fix second, in that order."*

Concretely: `DOGFOOD-001-03` goes red the moment you `git add` your new module (§B.3), and it stays
red until the artifacts are regenerated at a commit that contains the module. So:

1. Baseline (Task 0) — you cannot prove *unchanged* without a recorded *before*.
2. `DF-11-1-A` (Task 1) — get to a genuinely green suite first, or every later comparison carries a
   caveat.
3. Sweep RED-first (Task 2) — the guard must be demonstrated against the live defect **before** the
   defect is removed. After Task 3 the demonstration is impossible without a reconstruction, and a
   reconstruction is what AI-E11-1 rejects.
4. Extract (Task 3) — sweep goes green, dogfood goes red. Both expected.
5. Commit -> regenerate -> commit (Task 5) — the regeneration must be able to cite a sha that already
   contains the delta. Regenerating before committing produces an artifact citing a tree that does not
   exist, which is the falsehood this whole story is closing.
6. AC3 guard (Task 6) — land it after you have both a red tree and a green tree to demonstrate against.

---

## §D. Fences — what you must not touch

- **No publication of any kind** (§0.3).
- **No hand-editing of any `minions-dogfood-*.md`.** Renderer output, verbatim, or nothing.
- **No loosening or deletion of any existing assertion.** If an existing guard goes red because you
  moved code it reads by name (`TC-ArgusAgent-PIPELINE-002-11` parses `argus/pipeline.py` directly),
  **extend the guard's reach so it still sees what it claimed to see**. Narrowing its claim to make it
  green is the defect class this story exists to close.
- **No behaviour change**: no decision-table row, threshold, exit code, verdict, report byte, `.argus/`
  layout, producer token or CLI flag. No new dependency.
- **No changes to `__all__`** or to any public import path.
- **No edits to signed retrospectives** or to anything above the new heading in `deferred-work.md`.
- **Do not tidy the untracked host directories** (`argusdemo/`, `bmad-dev-loop-pack/`,
  `.bmad-drift-audit/`, `_bmad-output/audit-reports/*`). `argusdemo/` disposal is AI-E11-9, the
  operator's.
- **`git add` this story file** with your delta. An untracked story file is AI-E8-1 and `git diff`
  cannot see it.

---

## §E. HALT conditions

Stop and report rather than improvising if:

1. The baseline suite is anything other than **1405 / 1404 / 1** with `DOCS-001-22` as the single red.
2. Registering the two retros in `_STATUS_DOCUMENTS` turns any **other** assertion red.
3. After extraction, `argus audit .` returns any figure different from
   `RELEASE_READY / 61/169 / 0 / 61/77 / application / 92`, exit 0 — and you cannot show the difference
   is provenance-only.
4. No cohesion boundary exists that gets `pipeline.py` under 1200 **without** splitting a function or
   changing behaviour.
5. Regeneration through the renderers produces an artifact that still does not satisfy the AC3
   invariant.
6. Any fix would require editing a signed retrospective, loosening an existing assertion, or
   publishing anything.

---

## Dev Notes

### Testing standards

- `pytest` (9.1.1) under `tests/`; `testpaths = ["tests"]`. Test ids follow
  `TC-ArgusAgent-<AREA>-<NNN>-<NN>`. **Next free ids measured on this tree:** `DOCS-001` is used
  through **-58** (next free **-59**); `PIPELINE-002` is used through **-13** (next free **-14**).
  Verify before use.
- Every test carries a docstring naming its TC id, the AC it serves and its driver.
- Non-vacuity assertions are **mandatory** for any guard that goes green by finding nothing — this
  repository has five precedents (`-39`, `-118`, `-51`, `-99`, `-122`) and they are the reason this
  project catches its own vacuous guards.
- `mypy` must stay clean over the source count (72 today; **73** after one new module — state the new
  number rather than repeating 72).

### External / latest-technology research: deliberately NOT performed, and why

This story **adds no dependency, calls no external API and uses no library feature that could have
drifted**. Everything it touches is stdlib (`ast`, `pathlib`, `subprocess`/`git`), `pytest`, `mypy`,
`bandit`, and this repository's own modules. The one version-sensitive dependency in the tree
(`tree-sitter`, bounded `<0.26`) is untouched here and is Story 12.5's under `DF-11-4-B`. Pinned
toolchain on this host, measured: **CPython 3.11.15**, **pytest 9.1.1**. A web-research pass would
have produced nothing the dev could act on, so it was skipped **deliberately** rather than omitted —
recorded here so the omission is a decision, not a gap.

### Project structure

- Modules: `snake_case.py`, `<= 1200` lines (NFR-M1, `architecture.md:698`). Sibling extraction from
  `pipeline.py` uses the `pipeline_*.py` form (`pipeline_persist.py` precedent).
- Pure/impure separation (AR8) is the master rule. The resume family is the **IMPURE shell** and says
  so in its banner — the new module inherits that classification and must state it.
- AR7 / §3.3: **reuse, never fork.** The `DF-8-3-C` helper exists to delete a fork, not to add a
  parallel derivation.
- AR10: typed failures. `PipelineError` / `ResumeStateError` move with the code that raises them and
  must remain importable from `argus.pipeline`.

### References

- [Source: epics.md#Story 12.1] — the five AC blocks this story implements.
- [Source: epics.md#Epic 12] — dependency flow; 12.1 FIRST as a hard enabler.
- [Source: deferred-work.md#DF-8-2-A, #DF-8-3-A, #DF-8-3-C, #DF-8-5-B, #DF-10-4-D, #DF-10-2-A,
  #DF-11-4-D] — the ledger items ruled in §A.5.
- [Source: epic-11-retro-2026-08-12.md#§3.3, #§6 SD-1, #AI-E11-1, #AI-E11-2, #AI-E11-3, #AI-E11-6,
  #AI-E11-10] — the retrospective findings this story discharges.
- [Source: architecture.md#Enforcement] — the registration form and the false file-size-CI claim.
- [Source: architecture.md:263, :698, :857] — NFR-M1's four statements.
- [Source: argus/pipeline_persist.py] — the `DN-PIPELINE-SPLIT` precedent and docstring template.
- [Source: stories/10-4-a-grammar-that-fails-to-load-names-why.md] — the regeneration sequence the
  operator ruling reuses (commit `93adc94`).

### Project Structure Notes

No conflict with the unified structure. The new module is a sibling of `argus/pipeline.py` inside the
existing `argus/` package, matching `argus/pipeline_persist.py`. The new test file joins the flat
`tests/` tree. The one recorded variance is deliberate and is AC2's subject: the NFR-M1 ceiling is
enforced repo-wide **with three named, dated, filed exemptions**, because three test files breach it
today and fixing them is out of scope for a restructuring story.

---

## Dev Agent Record

### Agent Model Used

claude-opus-5[1m] (Claude Opus 5, 1M context) — BMAD `dev-story`, 2026-08-12.

### Debug Log References

All figures **LOCAL, Windows / CPython 3.11.15, pytest 9.1.1, mypy 2.3.0, bandit 1.9.4**, measured by
execution on 2026-08-12 under the dated risk acceptance of 2026-08-11 (§0.2, carried forward, **not**
re-taken). **CI evidence: NOT ESTABLISHED** — no CI run has seen any Epic 10, 11 or 12 sha, and none
was attempted. `git tag -l` is empty and `origin/master` is unmoved (`00c8d1b`), both re-verified
after the last commit. Nothing was pushed, tagged, released, dispatched or uploaded.

| Gate | Task 0 baseline (`ca37283`) | Final |
|---|---|---|
| `pytest` | **1405 collected / 1404 passed / 1 failed** (`DOCS-001-22` = `DF-11-1-A`) | **1425 / 1425 / 0** |
| `mypy argus` | clean, **72** source files | clean, **73** source files |
| `bandit -r argus` | 0 High / 0 Medium / **19** Low | 0 High / 0 Medium / **19** Low |
| `argus audit .` | `RELEASE_READY 61/169 0 61/77 application 92`, exit 0 | see AC5 below |
| `git ls-files -- argus` | 72 | 73 |
| `git ls-files '*.py'` | 169 | 173 |
| files over 1200 lines | **4** (`argus/pipeline.py` 1331, `test_pipeline_signature_demo.py` 1326, `test_v1_commitment_closure.py` 1308, `test_grammar_diagnosis.py` 1203) | **3** — all named, dated, filed exemptions |
| `argus/pipeline.py` | **1331** | **944** |
| dogfood partition | 3 units · `477ef77d7b65` / `82a3d605e61e` / `ed6d08f25ce3` · unit-2 39 files / 14997 LOC | 3 units · re-derived, ids moved (§B.3 predicted it) |

Every §B.1 premise was re-derived rather than transcribed. All HELD except the four §0.4 already
flagged, plus one this story adds: **`DF-9-2-C` is already resolved** — it claims three
`argus/dogfood/__pycache__/*.pyc` files are tracked and targets this story; measured,
`git ls-files -- argus` contains **zero** `__pycache__` paths and **no non-`.py` path at all**.
Recorded as verified-absent; no `git rm --cached` was run, because that would move the git index
inside the story that must prove its own audit population unchanged.

### Completion Notes List

#### AC1 — `argus/pipeline.py` is under the ceiling, by a cohesion split

`argus/pipeline.py` **1331 → 944** (256 lines of headroom for 12.2/12.3/12.4). New sibling
`argus/pipeline_stages.py` (513 lines). `git ls-files -- argus | xargs wc -l` shows **no `argus/**`
file over 1200** (next largest: `argus/pipeline.py` 944, `argus/dogfood/proof_run.py` 749).

**The boundary was re-derived, and it is NOT the one §A.1 recommended.** §A.1 recommended the
357-line Story-3.4 resume family and explicitly permitted a better measured boundary. An `ast` walk
over the pre-split file measured the **dependency direction**, which decided it:

| Candidate | Lines shed | Names it needs from the file it leaves | Consequence |
|---|---|---|---|
| Resume family (§A.1's recommendation) | 357 | **11** (`_assemble_and_persist`, `_detect_per_file`, `_project_halt`, `_critical_candidates`, `_skipped_remainder_entries`, `_orphan_findings`, `_build_cost_units`, `_ORPHAN_RULE_ID`, `AuditResult`, `PipelineError`, `ResumeStateError`) | a **module-level import cycle** — `pipeline.py` must keep re-exporting `resume_audit`/`resume_audit_detailed` from `__all__`, survivable only by a bottom-of-file import (which breaks if the new module is imported first) or by function-local imports |
| **Derivation stages (taken)** | **403** | **3**, all constants — and they moved with it | dependency points **strictly downward**, no cycle, no import trick, every moved body byte-identical |

`argus/pipeline_stages.py` holds the sixteen functions `_is_python` … `_assessment_scope_paths`:
grade one file, run the four V1 detectors over it, derive the FR4 critical candidates, the per-file
cost units, the halt projection, the LOC map, the partition plan and the assessment scope. It is a
real cohesion unit statable in one sentence — *take the index and the request, return entries /
findings / candidates / cost units / a projection / a plan, and write nothing* — and it is closed
under its own call graph (nothing outside it depends on anything inside it except through the four
entry points the orchestrators call). It is also contiguous in the file: 349–751, with
`_assemble_and_persist` at 754 beginning the orchestration/persistence layer that stays.
**No function is split across the boundary.** §B.3 showed a late-alphabet placement would have
preserved unit 2's `partition_id`; that was deliberately **not** allowed to influence the choice —
regeneration is required either way, and naming a module to flatter a hash is a defect.

**Purity proven mechanically, not asserted.** The 16 moved definitions and the 13 that stayed were
compared by `ast` span against `git show HEAD:argus/pipeline.py`: **29 of 29 byte-identical**, joined
moved-body sha256 `c6edd6fa9ddd105fb0684647e2bf3c7595bb418fe44558679c1d737cb87ac97b` on both sides.
`pipeline.py` imports all sixteen back under their original private names, so `__all__` is
byte-identical (7 entries, unchanged), **every** existing `from argus.pipeline import X` resolves —
including the private `_detect_per_file` (`tests/test_classification_word_boundary.py`,
`tests/test_critical_eligibility_pipeline.py`) and `_assessment_scope_paths`
(`tests/test_pipeline_coverage_scope.py`) — and
`monkeypatch.setattr(pipeline_mod, "_detect_per_file", …)`
(`tests/test_pipeline_signature_demo.py:883`) still intercepts the real call, because the name it
patches is the one `run_audit_detailed` looks up. **Zero import sites were edited.** The split is
documented in **both** module docstrings, per §3.2 and the `pipeline_persist.py` precedent.

#### AC2 — the repo-wide sweep, RED-first with the final test code

`tests/test_module_size_ceiling.py`, verification area **`TC-ArgusAgent-MAINT-001-01`..`-05`** (a new
area; no global TC-id registry exists, verified by grep) plus `TC-ArgusAgent-DOCS-001-59`.

- **(i) The observable:** the set `{tracked .py file : physical lines > 1200} − exemptions`, derived
  from `git ls-files -- '*.py'` on every run.
- **(ii) RED at the real seam, with the FINAL committed test code** — run before the extraction:
  `AssertionError: NFR-M1 breach — file(s) over the 1200-line ceiling: argus/pipeline.py (1331
  lines, 131 over). Split the file along a COHESION boundary …`. Not a reconstruction: the file as
  committed produced that message against the live defect.
- **(ii-b) The population is genuinely repo-wide**, proven with the same final code by emptying
  `_EXEMPT_BY_DESIGN` in-process: `… argus/pipeline.py (1331 lines, 131 over),
  tests/test_grammar_diagnosis.py (1203, 3 over), tests/test_pipeline_signature_demo.py (1326, 126
  over), tests/test_v1_commitment_closure.py (1308, 108 over)` — all four of §0.4 item 2, reproduced
  independently.
- **(iii) Adversarial variants GENERATED from the structure, with the count:** `-05` pads **every one
  of the 169 (now 173) files in the live population** past the ceiling and requires the predicate to
  flag each, and trims each to exactly 1200 and requires it not to be flagged — **173 generated
  over-cap variants and 173 at-cap variants**, asserted `>= 150`, never a hand-listed sample.
- **Non-vacuity:** `-01` fails on an empty enumeration, on a population under 100, on a one-sided one
  (`>= 50` from each of `argus/` and `tests/`), on a non-`.py` leak, and on any enumerated path
  missing from disk. `-03` pins the boundary in both directions **through the sweep's own
  predicate**: 0/1/1199/1200 pass, 1201/1202/1331 fail, plus the no-trailing-newline case (the count
  never under-counts relative to `wc -l`).
- **The registry SHRINKS:** `-04` fails if an exemption names a file that is gone **or is no longer
  over the cap**, if it lacks a reason (>= 80 chars), an ISO date, an owner or a target story, or if
  its `deferred-work.md` id or target story is not actually filed there. `argus/pipeline.py` is
  asserted **unaddable**. All three exemptions are filed as `DF-12-1-A`/`-B`/`-C` with owners and
  live target stories (12.2, 12.3, 12.5).
- **`git ls-files` vs a filesystem walk** — stated in the module docstring as §A.2 requires: the
  index is deliberate (a module is swept the moment it is `git add`-ed), a walk was rejected because
  it drags in `.venv/`, `__pycache__` and untracked scratch. The mirror-image blind spot — a module
  written and never staged — **bit during this implementation** (see the `-11` note below) and is
  filed as **`DF-12-1-D`** rather than left unsaid.

#### AC3 — the artifacts cannot rot silently, and the red says how to fix it

`tests/test_dogfood_artifact_currency.py`, **`TC-ArgusAgent-DOGFOOD-001-49`..`-52`**.

- **(i) The observable:** for each committed artifact, the pair *(is the cited sha an ancestor of
  `HEAD`?, has `argus/**` changed since it?)*.
- **(ii) RED at the real seam, for free, on §0.5's live defect** — with the final test code, before
  any regeneration: `STALE committed dogfood artifact(s) … minions-dogfood-partition-plan.md: cites
  a9cc933; argus/ has moved since (7 files changed, 749 insertions(+), 78 deletions(-))` for all
  three, followed by the exact remedy. **§0.5's finding is confirmed independently**: all five
  `DF-10-4-D` assertions were green over those three stale artifacts at `ca37283`.
- **(iii) Adversarial set GENERATED from real history, with counts:** `-52` classifies **every commit
  reachable from `HEAD`** (up to 400) with the same predicate and requires **both** classes to be
  non-empty — so a predicate that always says "current" (green forever) and one that always says
  "stale" (the permanent two-step tax `DF-8-5-B` was filed about) are both refuted on every run, from
  live data rather than from this note. It additionally derives that `HEAD` is current and the oldest
  reachable commit is stale.
- **The failure message names the exact regeneration command**, and the command is **real**:
  `scripts/regenerate_dogfood_artifacts.py` is a committed entry point that re-renders all three
  artifacts through `render_partition_plan_markdown` / `render_budget_plan_markdown` /
  `render_proof_markdown`, asserts each file equals the renderer's return value after writing, and
  **refuses to run on a dirty `argus/` tree** (exit 2) because that would manufacture a false
  citation. `-51` asserts the script exists, is the command the message names, and calls all three
  renderers — a named remedy that cannot be run is worse than none.
- **`-51` also closes the registry** over `minions-dogfood-*.md` by glob: a fourth committed artifact
  that is neither registered nor a named preserved record **fails**. The frozen Story-7.2 superseded
  run is exempt **by name with its reason** (it is *supposed* to cite a tree that no longer exists).
- **Nothing was loosened. Two assertions were WIDENED**, which `DF-8-5-B` welcomes:
  `TC-ArgusAgent-DOGFOOD-001-03` now asserts the source-file count, the total physical LOC and each
  unit's file count and LOC (the figures its own docstring always promised and its code could not
  see); `-20` now asserts the audited population and the total LOC. Both were proven red on the
  pre-regeneration tree — `-20`'s red was `assert '**20152**' in <committed proof>`, i.e. the live
  20152 against the published 19783. All five committed-artifact assertions now carry the
  regeneration remedy.
- **Provenance/enumeration reconciliation — decided, implemented and recorded.** `DF-10-4-D`:
  *"they currently claim `HEAD` provenance in their own Provenance block while enumerating the index,
  and those are two different trees."* **Decision: the LABEL now tells the truth** rather than
  pinning the enumeration to the commit. The renderers emit
  `- Commit descriptor (\`git rev-parse HEAD\` at generation): \`<sha>\`` followed by a new
  `- Enumerated population (the HONEST label …)` bullet stating that the file list comes from the git
  **index**, that the two coincide exactly when `argus/` has no staged-or-uncommitted change, and
  that `-50` fails unless they agree. **Why not pin the enumeration:** `git ls-files --with-tree=HEAD`
  would change what the dogfood planner enumerates — a verdict-adjacent behaviour change inside the
  one story whose defining criterion is *behaviour proven untouched* — and it would break the staged
  fixture repositories `tests/test_dogfood_*.py` build. The prose and the code now agree, **and** the
  divergence is detectable rather than merely described.
- **Truthful provenance, asserted rather than promised** (§0.1's ruling, mechanised): `-49` requires
  each cited sha to be a real commit **and** an ancestor of `HEAD`. This is not hypothetical — the
  artifact Story 10.4 replaced cited `7be90f77`, which is not an ancestor of this history.

#### AC4 — the ledger

`deferred-work.md` **+301 / −0** (`git diff --numstat`) — **append-only proven, zero deletions**,
nothing above the new heading touched. **CLOSED:** `DF-8-2-A` (with its own named remedy recorded as
measured insufficient), `DF-8-3-C`, `DF-8-5-B` + `DF-10-4-D` (**together**, per `DF-10-4-D`'s own
instruction), `DF-11-1-A`, `DF-11-5-A`, `DF-9-2-C` (already true on arrival, verified).
**RE-RECORDED with a new reason and a live target:** `DF-8-3-A` → `12-4` — its *"no room in
`pipeline.py`"* blocker is **explicitly discharged** (256 lines of headroom now exist) and the entry
says so; what remains is a **scope** ruling, because threading `heuristic_excluded_ineligible` into
the reports is a report-content change that AC5 forbids by construction. **RULED OUT with reasons,
out loud:** `DF-10-2-A` stays **open and unowned** (unrelated subject; `AI-E11-7` wants a dated
*operator* decision, type (H), not a dev's to take); `DF-11-4-D`/`AI-E11-6` re-targeted to `12-4`
(the trigger does not fire here — 12.1 adds no release-note section), with `AI-E11-6`'s alternative
DoD explicitly **not** taken. **OPENED:** `DF-12-1-A`/`-B`/`-C` (the three NFR-M1 test-file
exemptions, each with an owner and a live target story), `DF-12-1-D` (the sweep's index blind spot),
`DF-12-1-E` (three `pipeline*.py` siblings and no guard on the family's layering).

#### AC5 — behaviour proven untouched

**The strongest available proof, because the in-place figures necessarily move.** `argus audit .` on
the working tree now reads `62/171 … 31/39 … held_out=93` rather than the fixture's `61/169 … 61/77
… held_out=92`. That is a **population** change, not a behaviour change, and it is arithmetically
exactly this story's own two source files: +1 deep (`argus/pipeline_stages.py`), +1 held out
(`tests/test_module_size_ceiling.py`); `assessed_deep_ratio` is a reduced `Fraction`, and
`62/78 = 31/39`. Asserting that is not evidence, so the two variables were **separated**:

> **The NEW code, over the PRE-STORY population** — a pristine detached `git worktree` at `ca37283`,
> audited with the post-12.1 package — returns
> `verdict=RELEASE_READY deep_ratio=61/169 blocking_findings=0 assessed_deep_ratio=61/77
> scope=application held_out=92`, **exit 0**: byte-identical to the Task 0 fixture. The refactor
> moves **no figure**.

**Report and `.argus/` byte-identity, measured as an A/B over one tree.** The same `ca37283` worktree
was audited twice with `--reports final-verdict,coverage-ledger,security-review,architecture-review`
and an identical `--report-dir`: once by the **pre-12.1** code (run from inside the worktree) and once
by the **post-12.1** code. `diff -r`: **4 report files byte-identical, 848 `.argus/` files
byte-identical.** No caveat, no explained difference.

**No test was modified to accommodate the move.** Import-path edits required: **zero** — the
re-export made the split invisible. Four test/registry files were touched, each for a stated reason,
and every change is a **strengthening**:

1. `tests/test_evidence_citation.py` — two names added to `_STATUS_DOCUMENTS` (AC6).
2. `tests/test_no_web_imports.py` — `argus.pipeline_stages` added to the import-isolation coverage,
   the `AI-E5-7` *"extend the guard, do NOT fork"* rule, mirroring what 6.3 did for
   `argus.pipeline_persist`.
3. `tests/test_classification_word_boundary.py` — **`TC-ArgusAgent-PIPELINE-002-11` went RED, and
   that red was the guard working.** It `ast`-parses `argus/pipeline.py` by name and both
   construction sites it walks (`_detect_per_file`, `_critical_candidate`) moved. Per §D its **reach
   was widened, its claim was not narrowed**: it now walks every `argus/pipeline*.py` module, and the
   family is resolved by **glob**, so 12.2's next sibling is swept the moment it exists. (First
   written against `git ls-files -- 'argus/pipeline*.py'`; that went red *for the wrong reason* —
   the new module was not yet staged — which is the measurement behind `DF-12-1-D`.)
4. `tests/test_dogfood_plan.py` / `tests/test_dogfood_proof.py` — `-03` and `-20` widened, remedy
   sentences added (AC3). No assertion removed or weakened.

**Two published DERIVED FIGURES were updated** because `TC-ArgusAgent-DOCS-001-54` requires the
documents to track the built artifact and *"the artifact is the fact"*: `README.md` and `CHANGELOG.md`
now say **73 of the 73 shipped modules import** (was 72 of 72), the wheel holds **73** modules, **78**
wheel entries and **77** sdist files. These are measurements, never claims; the historical sentence
*"Five of the seventy-two shipped modules did it"* was deliberately left intact because it describes
2026-08-12's state truthfully. No release-note section was added — **no user-visible surface changed**
(§A.6's decision, recorded and honoured).

The Story 6.1 determinism quarantine, the `argus.* ⊬ fastapi` import-isolation gate, the FR32
signature demo, the resume byte-identity keystones and the cartridge self-audit all pass unmodified.

#### AC6 — `DF-11-1-A`

Closed on its own, first, before anything else, exactly as Task 1 required: two names appended to
`_STATUS_DOCUMENTS`. `pytest tests/test_evidence_citation.py` green, and the **full suite went
1405/1405/0** before the extraction began — so every later comparison is against a genuinely green
baseline rather than one carrying a red. Registration is inert (`_status_assertions()` = **0** for
both documents). **No retrospective was edited and no citation was minted**; the §H-citation half of
the entry's close condition is deliberately **not** taken and the reason is recorded in the ledger.
No other assertion went red, so §E's HALT condition 2 did not fire.

#### Decisions, tradeoffs and where a project standard outranked a general best practice

1. **Extraction boundary (§7/§8 authority).** §A.1's recommendation was overridden on a measurement,
   which §A.1 explicitly permits, and both the measurement and the reason are recorded above and in
   the ledger. The general principle applied is the acyclic-dependencies / stable-dependencies
   principle: a high-level module must not be extracted out from under a low-level one that has to
   keep re-exporting it.
2. **`_HasFilePath` Protocol over importing `CoverageLedgerEntry`** in `argus/detectors/vacuous_test.py`
   (`DF-8-3-C`). Nominal typing would read better; **the project standard wins** — the
   import-isolation gate keeps `argus.detectors.*` a leaf, and a new import edge from a detector to
   the ledger is a cost the general readability gain does not justify. Structural typing also
   preserves each caller's element type.
3. **The sweep's population is the git INDEX.** General best practice for a file-size guard is a
   filesystem walk; **the project standard wins** — `git ls-files` is this repository's established
   enumeration (`argus/dogfood/partition_plan.py`, `tests/test_built_distribution.py`) and a walk
   would sweep `.venv/`. The cost is a real blind spot, so it is **filed** (`DF-12-1-D`) rather than
   hidden. The one guard where the blind spot is fatal (`PIPELINE-002-11`, which must see a module
   that exists whether or not it is staged) uses a filesystem glob instead, and says why.
4. **`-59`'s false-claim assertion permits the quotation.** The correction block necessarily quotes
   the sentence it corrects, so the assertion requires every occurrence of
   `` committed under `tests/apaa/` `` to be on a `>` blockquote line — and separately requires the
   quotation to still **exist**, because deleting it would delete the lesson.
5. **Re-exporting all sixteen private names**, not only the two `tests/` currently import. Six are
   unused inside `pipeline.py` itself. The alternative — re-export only what is used today — would
   make the split visible to the next consumer that reaches for one, which is exactly the
   compatibility claim the `pipeline_persist.py` precedent makes.

#### What this story did NOT do

No push, no tag, no release, no `workflow_dispatch`, no index upload — `git tag -l` empty and
`origin/master` unmoved, re-verified after the final commit. No dogfood artifact hand-edited: all
three were produced by `scripts/regenerate_dogfood_artifacts.py`, which physically cannot hand-edit
one. No new dependency. No decision-table row, threshold, exit code, verdict, report byte, `.argus/`
layout, producer token or CLI flag changed. No signed retrospective edited. No existing assertion
loosened, deleted, skipped or `xfail`-ed. The untracked host directories (`argusdemo/`,
`bmad-dev-loop-pack/`, `.bmad-drift-audit/`, `_bmad-output/audit-reports/*`) were not touched.

### File List

**New**

- `argus/pipeline_stages.py`
- `tests/test_module_size_ceiling.py`
- `tests/test_dogfood_artifact_currency.py`
- `scripts/regenerate_dogfood_artifacts.py`

**Modified — code**

- `argus/pipeline.py`
- `argus/detectors/vacuous_test.py`
- `argus/reports/generator.py`
- `argus/dogfood/partition_plan.py`
- `argus/dogfood/proof_render.py`

**Modified — tests**

- `tests/test_evidence_citation.py`
- `tests/test_no_web_imports.py`
- `tests/test_classification_word_boundary.py`
- `tests/test_dogfood_plan.py`
- `tests/test_dogfood_proof.py`

**Modified — documents and artifacts**

- `README.md`
- `CHANGELOG.md`
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md`
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md`
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml`
- `_bmad-output/design-artifacts/ArgusAgent/stories/12-1-pipeline-stops-breaching-its-own-limit.md`
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md` *(regenerated)*
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md` *(regenerated)*
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md` *(regenerated)*

### Change Log

| Date | Change |
|---|---|
| 2026-08-12 | Closed `DF-11-1-A` first and alone: registered the Epic-10 and Epic-11 retrospectives in `_STATUS_DOCUMENTS`, ending a five-story node-id carve-out. Suite 1405/1404/1 → **1405/1405/0**. |
| 2026-08-12 | Landed `tests/test_module_size_ceiling.py` **RED-first with the final test code**, naming `argus/pipeline.py` at 1331/1200, and independently reproduced all four repo-wide breaches. |
| 2026-08-12 | Extracted `argus/pipeline_stages.py` (16 definitions, byte-identical) — `argus/pipeline.py` **1331 → 944**. Boundary chosen on a measured dependency direction rather than §A.1's recommendation; reason recorded. |
| 2026-08-12 | Closed `DF-8-3-C`: one `partition_application_files` helper in `argus/detectors/vacuous_test.py`, called from both former copies. |
| 2026-08-12 | Widened `TC-ArgusAgent-PIPELINE-002-11`'s reach to the whole globbed `argus/pipeline*.py` family (guard working; claim not narrowed), and registered `argus.pipeline_stages` in the import-isolation gate. |
| 2026-08-12 | Landed `tests/test_dogfood_artifact_currency.py` **RED on the live defect** and `scripts/regenerate_dogfood_artifacts.py`; widened `-03`/`-20` to the derived figures; named the regeneration command in all five committed-artifact failure messages; made the renderers' provenance label tell the truth about the index enumeration. |
| 2026-08-12 | Ruled and recorded nine ledger items; `deferred-work.md` **+301 / −0** (append-only proven). |
| 2026-08-12 | Registered both new rules in `architecture.md` §Enforcement and **corrected its false claim** that NFR-M1 was enforced by file-size CI under a `tests/apaa/` directory that does not exist. |
| 2026-08-12 | Committed the implementation, regenerated all three dogfood artifacts **through their own renderers** at a truthful provenance sha, and committed them separately (the §0.1 / `93adc94` sequence). Nothing published. |
