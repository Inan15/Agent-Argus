# Story 13.4: Split the status-document registry

Status: ready-for-dev

<!-- Created 2026-08-17 by create-story on HEAD 867a3bd. Every premise below was re-measured BY
     EXECUTION before this file was written; see §0. THE DEADLOCK WAS REPRODUCED, not assumed —
     the transcript is in §0.1 and it is the reason this story exists. A feasibility dry-run of
     the split was also executed and reverted; its measured numbers are in §0.2, so the line
     arithmetic in AC4 is measured rather than estimated. Validation is optional — run
     bmad-create-story:validate for a second pass before dev-story. -->

## Story

As a maintainer of this repository's governance record,
I want the status-document registry to live in its own module under the NFR-M1 ceiling,
So that the next retrospective or change proposal can be registered at all.

This story is **Epic 13's own unblocker**. It was authorised directly by **XAgent007** on
2026-08-17, deliberately **without a sprint-change proposal**, because filing a change proposal
is the very act this story unblocks. It discharges **`AI-E13-2`**, ranked #3 on the interim
retrospective's critical path (`epic-13-retro-INTERIM-2026-08-17.md:507-508`): *"the FINAL Epic-13
retrospective **cannot be written and registered** until this lands."*

### What this story IS

A **cohesion split** of one load-bearing guard file, performed as a **pure relocation**. The rule
does not change, the ids do not change, the registry's membership does not change, and the
population does not narrow. When it is done, the repository can register a status document again.

### What it is NOT

- **NOT a scope change and NOT a capability addition.** No new behaviour, no new verification
  area, no new `TC-` id. `-23` is *extended by one anchor*; nothing else gains an assertion it
  did not have, and nothing loses one.
- **NOT a threshold amendment, in either direction.** `_CEILING = 1200` and `_breaches_ceiling`
  in `tests/test_module_size_ceiling.py` are **byte-unchanged**. So is
  `_STATUS_DOCUMENT_PATTERNS`.
- **NOT an exemption.** `AI-E13-2` forbids it in its own words: *"do not add an
  `_EXEMPT_BY_DESIGN` entry — 12.1's rule requires a date, an owner and a ledger id, and this is
  a structural problem, not an exemption case."*
- **NOT a line-shave.** `tests/test_validation_set_decision.py:9-11` records the sanctioned
  remedy as a cohesion split, *"never shaving lines to make room, and never an exemption."*
- **NOT a re-derivation of the remedy.** How this may be done is **locked**; cite it, do not
  re-argue it. See §"Locked decisions".
- **NOT the retrospective.** This story does not write, register or trigger the final Epic-13
  retrospective. It makes writing one possible. `epic-13-retrospective` is its own sprint-status
  item and stays `in-progress`.
- **NOT a fix for the DOCS-index collision it found.** See §0.3 — recorded and filed, not fixed.

---

## ⛔ WHY THIS STORY EXISTS — a measured deadlock, not a tidy-up

`tests/test_evidence_citation.py` stands at **exactly 1200 / 1200** physical lines. The predicate
is `len(text.splitlines()) > 1200` (`tests/test_module_size_ceiling.py::_breaches_ceiling`), so
**one more line breaches it**. It reached 1200 because the Epic-13 interim retrospective
registered itself in `_STATUS_DOCUMENTS` — and that registration is not optional:

`_STATUS_DOCUMENT_PATTERNS` (`tests/test_evidence_citation.py:130-133`) resolves
`sprint-change-proposal-*.md` **and** `epic-*-retro-*.md` **by glob** against the artifact
directory. Any new change proposal or retrospective must therefore be registered in
`_STATUS_DOCUMENTS` or `TC-ArgusAgent-DOCS-001-22` goes RED — **and registering it breaches the
ceiling.** The guard globs the directory, so leaving the document uncommitted does not avoid it.

**There is no green intermediate state.** That is the deadlock, and §0.1 is the transcript of it
happening on this tree. It blocks (a) Epic 13's FINAL retrospective, (b) the Epic 14 change
proposal drafted 2026-08-17, and (c) every future status document.

---

## Acceptance Criteria

### AC1 — The registry and its closure move into ONE new cohesive module, and the boundary is RECORDED as a boundary

1. A new module **`tests/test_status_document_registry.py`** is created and it **owns the
   governed population and its closure**:
   `_STATUS_DOCUMENTS`, `_STATUS_DOCUMENT_PATTERNS`, `_EXCLUDED_BY_DESIGN`, `_registered_paths`,
   `TC-ArgusAgent-DOCS-001-21` and `TC-ArgusAgent-DOCS-001-22`.
2. `tests/test_evidence_citation.py` **keeps the derivation and its semantics**: the marker
   vocabularies (`_STATUS_CLAIMS`, `_DENIAL_MARKERS`, `_QUALIFIER_MARKERS`,
   `_CITATION_DENIAL_MARKERS`, `_NOT_ESTABLISHED_MARKER`), the regexes, `_strip_struck`,
   `_is_attribution`, `_strip_attributed_quotations`, `_split_sentences`, `_is_denied`,
   `_status_assertions`, `_executed_gate_citations`, `_flatten`, `_section`, `_head_sha`, and the
   assertions `-20`, `-21b`, `-23`, `-24`, `-25`, `-25b`.
3. **The cohesion statement is written into both module docstrings, in one sentence each**, and
   each docstring answers *"where did the other half go, and why"* so neither end is a dead
   pointer:
   - new module — *"**WHICH** planning records are governed, and is that set closed?"*
   - `test_evidence_citation.py` — *"**WHAT** is a status claim, **what** is an executed-gate
     citation, and do the records and the consumer surfaces carry them?"*
4. **The boundary is justified in prose, not by line count** (`AI-E13-2`; `_REMEDY`). In
   particular the docstrings must record **DN-2** below — why `-21b` did **not** move with `-21`
   — because that is the one placement a reader will question.
5. The new module imports the derivation **from the module that owns it**, by import, never by
   copy: `from tests.test_evidence_citation import (...)`. Forking the derivation is the AR7
   defect this repository has recorded four times. There is exactly one import direction
   (new → old); **an import back from `test_evidence_citation.py` into the new module is
   forbidden** — it would be a cycle. See DN-3.
6. `_REPO_ROOT` / `_ARTIFACT_DIR` are **re-derived** in the new module from `Path(__file__)`,
   matching every other test module in this tree (`test_module_size_ceiling.py:55-56`,
   `test_governance_record_integrity.py:28-29`). They are derived paths, not policy.

### AC2 — Test ids are BYTE-IDENTICAL. Nothing is renamed, renumbered, added or removed

1. The set of `test_TC_ArgusAgent_*` function names present across
   `tests/test_evidence_citation.py` **plus** `tests/test_status_document_registry.py` after the
   change is **exactly equal** to the set present in `tests/test_evidence_citation.py` before it.
   Prove it by execution — extract both sets (`git show HEAD:tests/test_evidence_citation.py`
   versus the working tree) and compare, and paste the comparison into the Debug Log.
2. **No new `TC-` id is opened by this story**, and no verification area is opened. `-23` is
   extended by adding anchors to its existing enumeration; it is not replaced and not renumbered.
3. The full-suite **collected count is IDENTICAL** before and after: **1597**. A pure relocation
   cannot change it. A different number means a test was lost, duplicated or invented — stop and
   find out which.

**Why this AC is hard-locked:** `TC-ArgusAgent-DOCS-001-20`..`-23` are cited by name in
`architecture.md:648` and `:964`, in `deferred-work.md` (`:1384`, `:2236`, `:2523`), and by five
test modules. Renumbering would silently invalidate every one of those citations at once.

### AC3 — Every moved assertion keeps its meaning AND is proven able to fail, at the REAL SEAM

The **GUARD-ADEQUACY CLAUSE** (`architecture.md` §Enforcement, `AI-E11-1`) applies in full: RED at
the real seam, not against a reconstruction. **Prove it; do not assert it.**

1. **`-21` proven RED from its new home.** Temporarily append a live, uncited, first-person
   release-status claim to a **registered** status document on disk, run `-21` from the new
   module, capture the RED output verbatim, then restore the document with
   `git checkout -- <path>` and show `git status --porcelain -- <path>` is empty.
2. **`-22` proven RED from its new home.** Create an unregistered probe matching
   `sprint-change-proposal-*.md` under the artifact directory, run `-22`, capture the RED,
   register it, show GREEN, then remove both the probe and the registration and show GREEN again.
3. **`-21b` still bites from its retained home** (it is the control for the derivation the new
   module imports): run it and record the result. It must not have been touched.
4. Every RED and GREEN transcript goes into the Dev Agent Record's Debug Log, with the command.

### AC4 — The deadlock is demonstrably BROKEN: two further registrations fit, measured

1. **Reproduce the deadlock on the pre-change tree first**, exactly as §0.1 records it, so the
   dev's own baseline confirms the premise rather than inheriting it.
2. After the split, plant **TWO** probe status documents in the artifact directory — one matching
   each pattern, e.g. `sprint-change-proposal-2026-08-17-PROBE-A.md` and
   `epic-99-retro-PROBE-B-2026-08-17.md` — each with **more than 10 sentences** (`-21` requires
   it), each written with `encoding="utf-8"` and `newline="\n"`. Register **both** in
   `_STATUS_DOCUMENTS`.
3. With both registered, **run the FULL suite**. It must be green, and the collected count must be
   1597. Running only `-21`/`-22`/`MAINT-001-*` is not sufficient: the point of the exercise is to
   learn whether *anything else* in the tree fires on a new status document.
4. Remove both probes and both registration lines. **Run the full suite again** — green, 1597 —
   and show `git status --porcelain` carries **no residue** under `tests/` or the artifact
   directory. **The probes must never be committed.**
5. Record the measured line count and remaining headroom of **both** modules, and express the
   registry host's headroom as *"N lines ≈ N further registrations"*.
   **DoD (`AI-E13-2`), satisfied in the stronger form:** both modules are under the ceiling, and
   the module that hosts `_STATUS_DOCUMENTS` has headroom for **far more than two** further
   registrations. Measured projection from the §0.2 dry-run: registry host ≈ **192-280 lines**
   (≈ 920-1008 spare), `test_evidence_citation.py` ≈ **1030-1070** (≈ 130-170 spare).
6. **The residual is recorded, not left to be rediscovered** — this is the lesson the interim
   retrospective drew about this exact file (*"it worked by consuming the last unit of a budget
   nobody was watching"*). If `tests/test_evidence_citation.py` measures **above 1100** after the
   change, append a note to `deferred-work.md` naming the **next** cohesion boundary — the Story
   12.9 release-surface half (`_STATUS_STATEMENT_REQUIRED`, `_STATUS_STATEMENT_NOT_REQUIRED`,
   `_head_sha`, `-24`, `-25`, `-25b`) — with an owner. Naming the next boundary is not a
   commitment to take it.

### AC5 — NOTHING IS WEAKENED. Shown by construction and by measurement

1. **No assertion is deleted, softened, skipped, xfailed or narrowed.** Every moved `assert`
   arrives with its message and its meaning intact.
2. **No `_EXEMPT_BY_DESIGN` entry is added** to `tests/test_module_size_ceiling.py`, and
   `_CEILING`, `_breaches_ceiling`, `_physical_line_count`, `_tracked_python_files` and
   `_measure_population` are **byte-unchanged**.
3. **`_STATUS_DOCUMENT_PATTERNS` is byte-unchanged.** Narrowing the globs would make the deadlock
   disappear by making the guard blind, which is the move this project files as a defect
   (`test_module_size_ceiling.py:35-39`).
4. **`_STATUS_DOCUMENTS` arrives with the same members in the same order, and every registration
   comment travels verbatim with its entry.** Those comments are the record of each registration
   decision; dropping them to save lines is the shave this story exists not to do. The one
   permitted edit is to the trailing sentence of the `epic-13-retro-INTERIM-2026-08-17.md`
   comment, which currently reads *"THIS LINE PUTS THIS FILE AT EXACTLY 1200/1200 … The NEXT
   status document cannot be registered until this module is split — filed as AI-E13-2"*: that
   sentence has become false in the direction that matters, so **strike it and append the
   correction** naming Story 13.4 and the new host (§3.4 — supersede, never erase).
5. **`_EXCLUDED_BY_DESIGN` travels byte-unchanged**, including all four reasons and the
   `_PRESERVED_RECORD` precedent note.
6. **The derivation vocabularies are byte-unchanged**, both in content and in file:
   `_STATUS_CLAIMS`, `_DENIAL_MARKERS`, `_QUALIFIER_MARKERS`, `_CITATION_DENIAL_MARKERS`.
7. **The retained half is edited in exactly four ways, enumerated in the Dev Agent Record**:
   (i) removal of the moved blocks; (ii) the module-docstring amendment (AC1.3/AC1.4, including
   the two docstring bullets at `:32-38` whose subjects — `-22`'s glob closure and `-21b` — now
   sit either side of the boundary); (iii) the `:63-81` comment block's one-clause re-point of
   `_STATUS_DOCUMENTS` to its new home, **preserving the Story 12.9 decision it records**;
   (iv) the `-23` extension and its module-path constant. **Any fifth edit is a line-shave until
   proven otherwise** — justify it in writing or revert it.
8. **Total `assert` count across the two files is greater than or equal to the original count in
   `test_evidence_citation.py`.** Report both numbers.

### AC6 — The new module is REGISTERED where guard ownership is recorded, so every citation stays resolvable

1. **`architecture.md` §H (`:648`)** and **§Enforcement (`:963-969`, "Governance enforcement")**
   are amended to name **both** modules and state which ids each holds. Amend in place, dated and
   attributed in the established form — *(amended 2026-08-17 by Story 13.4)*. **This is a pointer
   update, not the retraction of a claim, so §3.4's strike form is not required here**; the rule
   text itself is unchanged and must remain so.
2. **`-23` is extended** to assert the new module's path in **both** §H and §Enforcement. It
   currently asserts only `_GUARD_FILE`; after this change an unregistered second guard would be
   exactly the orphan `-23` exists to prevent. Every existing anchor in `-23`'s enumeration
   **stays**.
3. **`AI-E12-1`'s second half is written down as a rule** — the other deliverable `AI-E13-2`
   names, and the thing the interim retrospective says *"no document yet requires"*. Add to
   §Enforcement, beside the governance-enforcement paragraph: **any document matching
   `sprint-change-proposal-*.md` or `epic-*-retro-*.md` under the artifact directory is registered
   in `_STATUS_DOCUMENTS` in the same change that creates it; the retrospective and
   change-proposal steps do not hand off until their own output is registered and the guard is
   green.** `-23` asserts one anchor phrase from it, so the rule cannot be deleted silently.
   **Scope note:** the *orchestrator-side* half of `AI-E13-2` (editing the dev-loop retrospective
   skill's own DoD) is **not this story's to make** and stays with its named owner; putting the
   rule in `architecture.md` gives it a reader inside this repository, which is what `AI-E9-8`
   demands and what `AI-E12-1` asked for three times.
4. **`tests/test_module_size_ceiling.py:34`** cites `tests/test_evidence_citation.py:91` as the
   `_EXCLUDED_BY_DESIGN` precedent. Re-point it to the new module **by SYMBOL, not by line
   number** — `tests/test_status_document_registry.py::_EXCLUDED_BY_DESIGN`. Record why: the
   existing cite had **already drifted** (the symbol is at `:138`, and `:91` now lands inside the
   registry comment), which is this repository's most-repeated defect and an argument against
   line-number citations generally. **Docstring only — not one assertion in that file changes.**
5. **`tests/test_spec_claim_scope.py:5`** and **`tests/test_v1_commitment_closure.py:4`** carry
   live DOCS-index ownership clauses stating that `-20`..`-23` belong to
   `tests/test_evidence_citation.py`. Amend both to name the two hosts. **Docstrings only.**
6. **`deferred-work.md` is APPEND-ONLY.** Nothing at `:1381-1386` (the `DF-AUD-APAA-C` closure
   note), `:2235-2249` or `:2523` is edited — those are records, and `:2523` cites a full pytest
   node id that this change relocates. A dated **"Story 13.4 dispositions — 2026-08-17"** section
   records the new node ids and states that no prior entry was touched. This is the same form
   Story 13.1 used for `DF-13-1-A`: an appended note, never an edit.
7. **LEAVE BYTE-UNCHANGED — these are measurements taken at their own baselines and remain true
   as history.** Do not "helpfully" update them: `tests/test_validation_set_decision.py:6-14`,
   `tests/test_gate_flip_path.py:4`, `tests/test_gate_decision.py:4`,
   `tests/test_adjudication_record.py:4`, `tests/test_governance_record_integrity.py:3-5`, and
   **every** `epic-*-retro-*.md` and `sprint-change-proposal-*.md`. Editing a retrospective to
   reflect a later tree is the §3.4 violation, and `-20`/`-21`/`-22` would notice.

### AC7 — Gates, ledger and hand-off

1. **All three gates run locally with ACTUAL numbers, reported as deltas against these measured
   baselines on `867a3bd`** (never "all green"):
   `pytest` **1597 collected / 1597 passed / 0 failed / 0 skipped, exit 0** ·
   `mypy argus` **Success, 86 source files** ·
   `bandit -r argus` **19 Low / 0 Medium / 0 High** (confidence 0 / 0 / 6 / 13).
   Expected after this change: **all three identical**. pytest count identical because the move is
   pure; mypy identical because it runs over `argus` only; bandit identical because no `argus/`
   file is touched. **Any divergence is a finding — name it, do not average it away.**
   Label them **LOCAL** and record that **CI evidence is NOT ESTABLISHED** for this tree.
   **A skip appearing is a regression signal.**
2. **`deferred-work.md`** receives the append-only Story 13.4 section (AC6.6), which also files
   the DOCS-index collision found in §0.3 as **`DF-13-4-A`** — **record only, no fix in this
   story** — with owner **XAgent007 (Engineering Lead)** and a stated `target_story`.
3. **Nothing outward-facing.** No tag, no release, no visibility change, no edit to
   `DF-12-9-A`'s disposition. `git tag -l` is empty and must stay empty. Measured 2026-08-17:
   `origin/master` **equals** HEAD `867a3bd` — the Epic-13 delta has been pushed, which is a
   change from the 13.3 baseline and is why AC7.4 matters more than usual.
4. **HAND OFF GREEN.** `AI-E13-1` is the defect this epic recorded about itself: the SM phase
   wrote a story file, nothing re-ran the suite, the commit was pushed, and `audit-ci` went red on
   ubuntu. **In this repository `stories/*.md`, `architecture.md` and `deferred-work.md` are
   TESTED ARTIFACTS** (`DOCS-001-78` globs `stories/*.md`; `-22` globs the artifact directory;
   `-23` and `DOCS-001-77` read `architecture.md`). Run the full suite **after** the last prose
   edit, not before it.

---

## Developer Context & Guardrails

### §0 — Premise re-measurement (this project's create-story control; twelve-for-twelve since Epic 11)

Measured **2026-08-17 on `867a3bd`** (HEAD), **by execution**. Per `AI-E12-10`, confirmations are
recorded as well as divergences. **Re-measure on your own baseline (Task 0)** — inherit nothing.

| Premise, as the tracker / retrospective states it | Re-measured on `867a3bd` | Consequence |
|---|---|---|
| `tests/test_evidence_citation.py` is at exactly 1200/1200 | ✅ **HOLDS. 1200 lines**, headroom **0** | The whole premise. AC4 |
| The predicate is `len(text.splitlines()) > 1200` | ✅ **CONFIRMED.** `test_module_size_ceiling.py::_breaches_ceiling` / `_CEILING = 1200`; `MAINT-001-03` pins 1200 pass / 1201 fail through that same function | One line breaches it. **Do not touch either** |
| `_STATUS_DOCUMENT_PATTERNS` is at `:130-133` and matches both classes | ✅ **CONFIRMED.** `("sprint-change-proposal-*.md", "epic-*-retro-*.md")`, resolved by glob under the artifact directory | AC5.3 |
| Registering a new status document breaches the ceiling | ✅ **REPRODUCED BY EXECUTION.** See §0.1 — there is **no green intermediate state** | The deadlock is real |
| The remedy is locked as a COHESION SPLIT | ✅ **CONFIRMED.** `test_validation_set_decision.py:9-11` + `test_module_size_ceiling.py::_REMEDY`; *"never shaving lines to make room, and never an exemption"* | **Cite it. Do not re-derive it** |
| Story 13.1 met this wall at 1199/1200 and DECLINED | ✅ **CONFIRMED.** `test_validation_set_decision.py:6-14` — *"splitting `test_evidence_citation.py` … belongs to a story that says so"* | **This is that story.** That precedent is why `-73`..`-76` are not in this file |
| The split is mechanically feasible and the moved tests pass from a new home | ✅ **PROVEN BY A DRY RUN**, executed and reverted. See §0.2 | AC1/AC4 line arithmetic is **measured**, not estimated |
| `-20`..`-23` are cited at `architecture.md:648` and `:964` | ✅ **BOTH EXACT** | AC6.1 |
| `-20`..`-23` are cited in `deferred-work.md` | ⚠️ **YES — at `:1384`, `:2236` and `:2523`, and the ledger is APPEND-ONLY.** `:2523` cites a full pytest **node id** that this change relocates | **AC6.6 — append, never edit** |
| Five test modules cite `-20`..`-23` or the file | ⚠️ **PARTLY — the form differs and it matters.** `test_spec_claim_scope.py:5` and `test_v1_commitment_closure.py:4` cite the **ids** (live ownership clauses → amend); `test_module_size_ceiling.py:34` cites the **file and a line number** (→ re-point by symbol); `test_validation_set_decision.py:6-14` and `test_governance_record_integrity.py:3-5` are **dated measurements** (→ leave byte-unchanged) | **Three different treatments. AC6.4-6.7** |
| No test enumerates TC-id → owning-module as machine data | ✅ **CONFIRMED** — searched every `tests/*.py`; ownership lives in docstrings only | Nothing breaks mechanically on relocation; the prose must be corrected by hand |
| `tests/__init__.py` exists, so `from tests.x import y` resolves | ✅ **CONFIRMED**, and the pattern is already in use: `test_evidence_citation.py:82` imports `_RELEASE_SURFACES` from `tests.test_release_surface_honesty` | AC1.5 has precedent |
| `-21b` / `-24` / `-25` / `-25b` touch `_STATUS_DOCUMENTS` | ❌ **NONE OF THEM DO** (verified by reference scan). Its only readers are `_registered_paths`, `-21` and `-22` | The boundary is **clean**. DN-1 |
| Test-id high-water marks | Measured: `DOCS-001-`**79** · `PRECISION-001-`**64** · `MAINT-001-`**05** | **This story opens none.** AC2.2 |
| Other files near the ceiling | `test_built_distribution.py` **1198 (2 left)** · `test_instrument_disclosure.py` **1194 (6)** · `test_grammar_diagnosis.py` **1203 (exempt, `DF-12-1-C`)** · `test_pipeline_signature_demo.py` **1326 (exempt)** · `test_v1_commitment_closure.py` **1708 (exempt)** | **Three more files are effectively full.** Do not solve them here — AC4.6 records, it does not fix |
| Baseline gates on `867a3bd` | ✅ **MEASURED BY EXECUTION.** `pytest` **1597 collected / 1597 passed / 0 failed / 0 skipped**, exit 0 · `mypy argus` **Success, 86 source files** · `bandit -r argus` **19 Low / 0 Med / 0 High** | Report deltas against these exact numbers |
| Nothing is published | ✅ **`git tag -l` empty** | AC7.3 |
| `origin/master` is behind HEAD | ❌ **NO LONGER — `origin/master` == HEAD == `867a3bd`, 0 ahead.** The 13.3 story's *"13 commits behind"* is **stale**; the delta was pushed | **`AI-E13-1` matters more, not less: master is live.** AC7.4 |
| A `project-context.md` exists | ❌ **NONE.** `architecture.md`, `deferred-work.md`, the retrospectives and this file **are** the context | — |

### §0.1 — THE DEADLOCK, REPRODUCED BY EXECUTION on `867a3bd`

Not inferred. Run on this tree, then fully reverted (`git status --porcelain` empty for every
touched path afterwards). **Reproduce it yourself as Task 0** — that is the point of §0.

```
STEP 1: an unregistered probe status document on disk
  tests/test_evidence_citation.py = 1200 lines
  TC-ArgusAgent-DOCS-001-22            -> FAILED   (exit 1)
  TC-ArgusAgent-MAINT-001-02           -> passed   (exit 0)

STEP 2: the probe REGISTERED — the only sanctioned fix for that red
  tests/test_evidence_citation.py = 1201 lines
  TC-ArgusAgent-DOCS-001-22            -> passed   (exit 0)
  TC-ArgusAgent-DOCS-001-21            -> passed   (exit 0)
  TC-ArgusAgent-MAINT-001-02           -> FAILED   (exit 1)   <- NFR-M1 breach, 1 over
```

**Read what this says.** Step 1 is red because the set is not closed. Step 2 closes the set and is
red because the file is full. **There is no third state.** The only moves that would make both
green are the two the repository forbids by name — shave a line, or file an exemption.

### §0.2 — FEASIBILITY DRY RUN, executed and reverted

The four blocks were relocated verbatim into a probe module, the suite was run, and everything was
restored. **Measured, mechanical move only — before the docstrings and the `-23` extension:**

| | Lines | Headroom |
|---|---|---|
| `tests/test_evidence_citation.py` | **1030** | 170 |
| `tests/test_status_document_registry.py` | **192** | 1008 |

`-21` and `-22` **passed from the new module**, the retained module's six remaining tests
(`-20`, `-21b`, `-23`, `-24`, `-25`, `-25b`) **passed**, and the cross-module import resolved with
no `conftest.py` change. Adding the docstrings AC1.3/AC1.4 require and the `-23` extension will
move these to roughly **1060-1070** and **250-280**. **Do not treat these as targets** — measure
your own and report them.

The blocks, located by anchor text (line numbers are given for orientation and **must be
re-verified by anchor**, not trusted):

| Block | Anchor (first line) | Lines on `867a3bd` |
|---|---|---|
| Registry + patterns + exclusions | `# Every status-asserting planning record under the artifact` | 90-166 (77) |
| `_registered_paths` | `def _registered_paths() -> list[Path]:` | 449-450 (2) |
| `-21` | `def test_TC_ArgusAgent_DOCS_001_21_every_status_claim_cites_an_executed_gate` | 543-583 (41) |
| `-22` | `def test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed` | 706-755 (50) |

Imports the new module needs from `tests.test_evidence_citation`: `_NOT_ESTABLISHED_MARKER`,
`_executed_gate_citations`, `_split_sentences`, `_status_assertions`. Nothing else.

### §0.3 — FOUND BY MEASUREMENT, recorded and NOT fixed here: a DOCS-index collision

`TC-ArgusAgent-DOCS-001-24` and `-25` are defined **twice**, in two modules, by two stories:

- `tests/test_evidence_citation.py:827` / `:877` — Story 12.9
- `tests/test_spec_claim_scope.py:298` / `:339` — Story 10.2, whose docstring allocates
  `-24`..`-27` to itself

Two distinct pytest node ids, **one ambiguous verification id**. It predates this story by three
epics and nothing here creates or worsens it. **Fixing it would renumber ids, which AC2 forbids
absolutely.** File it as `DF-13-4-A` (AC7.2), record only. This is the `AI-E9-8` discipline: an
observation with no owner is how the last one evaporated.

### Locked decisions this story must CITE rather than reopen

| Locked | Where | Consequence here |
|---|---|---|
| **The remedy for a full guard file is a COHESION SPLIT** — never a shave, never an exemption | `test_module_size_ceiling.py::_REMEDY`; Story 12.8 precedent | The whole method. **Do not re-derive** |
| **Splitting THIS file belongs to a story that says so** | `test_validation_set_decision.py:6-14` (Story 13.1 declined at 1199/1200) | **This is that story** |
| **`AI-E13-2` forbids the exemption route explicitly** | `epic-13-retro-INTERIM-2026-08-17.md:484` | AC5.2 |
| **Narrowing a population until it goes green is a defect** | `test_module_size_ceiling.py:35-39`; 12.1's rule | AC5.3 — the globs stay |
| **AR7 / single implementation** — a rule with two implementations is a fork | `architecture.md` §Enforcement | AC1.5 — import, never copy |
| **Two guards sharing one mutable POLICY table is tighter coupling than duplicated policy** | `test_evidence_citation.py:7-15` | Share the **derivation**; never merge the marker vocabularies |
| **§3.4 evidence immutability — supersede, strike, never erase** | `architecture.md` §3.4 | AC5.4, AC6.6, AC6.7 |
| **GUARD-ADEQUACY CLAUSE — RED at the REAL SEAM, not a reconstruction** | `architecture.md` §Enforcement (13.2 / AC8.4) | AC3 |
| **A rule that lives only in a test is not a rule; one that lives only in prose is not enforced** | `architecture.md:921-922`; `-23` | AC6.2, AC6.3 |
| **`AI-E8-6`** — a guard narrower than its own AC is a breach | Epic-8 retro | AC5 |
| **`AI-E9-8`** — never leave an entry without a named owner | Epic-9 retro | AC7.2 |
| **Ledger-claim cross-check — a claimed closure the ledger never received fails CI** | `architecture.md` §Enforcement; `DOCS-001-78` | See "Traps" below |
| **Nothing outward-facing** | `DF-12-9-A`; `AI-E13-6` | AC7.3 |

### Decisions taken by this story (record each in the Dev Agent Record with its rejected alternative)

- **DN-1 — the cohesion boundary is POPULATION versus DERIVATION, and it was chosen by
  measurement, not by line count.** `_STATUS_DOCUMENTS` has exactly three readers
  (`_registered_paths`, `-21`, `-22`) and none of them is `-20`, `-21b`, `-23`, `-24`, `-25` or
  `-25b` — verified by reference scan. So the registry, its glob closure and its exclusion table
  lift out as a closed unit with **one** import edge. *Rejected alternative:* splitting off the
  Story 12.9 release-surface half (`-24`/`-25`/`-25b`) instead. It moves more lines and would read
  as choosing the boundary that helps the arithmetic most — the thing `_REMEDY` forbids — and it
  leaves the registry in the file that is full. It stays on record as the **next** boundary
  (AC4.6), which is a different decision for a different day.
- **DN-2 — `-21b` does NOT move with `-21`, and the docstrings say why.** `-21b` is the positive
  control for `_status_assertions` and `_executed_gate_citations`: it drives them over synthetic
  and quoted strings and never reads `_STATUS_DOCUMENTS`. Its subject is the **derivation**, which
  stays. *Rejected alternative:* moving it because its id says `21`. That would separate a control
  from the code it controls, put the derivation's two controls (`-21b` and `-25b`) in different
  modules for no stated reason, and buy 118 lines — i.e. it would be a line-count decision wearing
  an id's clothes. **Both docstrings must answer the "where is `-21`'s control?" question at both
  ends**, or the next reader reconstructs this argument from scratch.
- **DN-3 — the import direction is new → old, once, and never back.** The new module imports four
  derivation symbols. `test_evidence_citation.py` must **not** import the new module's guard-path
  constant for `-23`; it declares `tests/test_status_document_registry.py` as a literal beside
  `_GUARD_FILE`, with a comment stating that the literal exists to avoid a cycle. *Rejected
  alternative:* importing it for single-sourcing — a circular import between two test modules
  fails at collection, and a two-word path string is not a policy table.
- **DN-4 — the registry stays PYTHON, not a data file.** `AI-E13-2` offers *"or move the registry
  to a data file"*; it is rejected. Every entry in `_STATUS_DOCUMENTS` carries a prose comment
  recording **why and when it was registered and what was verified before registering it**; a JSON
  or YAML sidecar either loses those or turns them into uncommentable data, and it would let the
  governed population be edited without touching a guard. *Rejected alternative recorded here
  because it was explicitly offered and must be seen to have been considered.*
- **DN-5 — `architecture.md` §H and §Enforcement are amended IN PLACE, not struck.** §3.4 governs
  **records** and **claims about the world that turned out false**. *"This rule is enforced by file
  X"* is a **pointer**, and after this change it is simply where the code is. *Rejected
  alternative:* striking and appending, which would leave the architecture stating two enforcement
  locations, one of which is wrong — the exact reading defect that `test_module_size_ceiling.py`'s
  `-59` exists to prevent. The amendment is **dated and attributed** so the change is still
  traceable. **`deferred-work.md` is the opposite case and stays append-only** (AC6.6).

### Files to touch

| Path | Action |
|---|---|
| `tests/test_status_document_registry.py` | **NEW** — the registry, its closure, `-21`, `-22` |
| `tests/test_evidence_citation.py` | **UPDATE** — four edits only, enumerated in AC5.7 |
| `_bmad-output/design-artifacts/ArgusAgent/architecture.md` | **UPDATE** — §H `:648`, §Enforcement `:963-969` (+ the AC6.3 rule) |
| `tests/test_module_size_ceiling.py` | **UPDATE — DOCSTRING `:34` ONLY.** No assertion changes |
| `tests/test_spec_claim_scope.py` | **UPDATE — DOCSTRING `:5` ONLY** |
| `tests/test_v1_commitment_closure.py` | **UPDATE — DOCSTRING `:4` ONLY** |
| `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` | **APPEND ONLY** — the Story 13.4 section + `DF-13-4-A` |
| `_bmad-output/design-artifacts/ArgusAgent/stories/13-4-split-the-status-document-registry.md` | **UPDATE** — Dev Agent Record, File List, Change Log |
| **Everything else** | **DO NOT TOUCH.** In particular: `prd.md`, `epics.md`, `precision-validation-protocol.md`, every `epic-*-retro-*.md`, every `sprint-change-proposal-*.md`, `validation-corpus/**`, all of `argus/**` |

⚠️ There is an **uncommitted external edit to `README.md` preserved in `git stash`**. It is
irrelevant to this story. **Do not restore, apply, reference or mention it**, and do not run
`git stash pop`.

### Previous story intelligence — traps already paid for; do not pay again

- **`AI-E13-1`, and this story is where it would bite hardest.** Story 13.3's SM phase wrote
  `stories/13-3-*.md`, nothing re-ran the suite, the commit was pushed, and `audit-ci` failed on
  ubuntu py3.12 (`TC-ArgusAgent-DOCS-001-78`, 1 failed / 1580 passed). **Run the full suite after
  your last prose edit.**
- **`story_closure_claims` is LINE-SCOPED** (`test_governance_record_integrity.py:58-72`), and it
  swept a seven-id table row in 13.3 to produce a **false positive**. In every document you write
  here: **never put a `DF-*` id on the same line as `CLOSED`, `Closes` or `closes` unless
  `deferred-work.md` really carries that closure.** `DOCS-001-78` reads `stories/*.md`, and this
  story file is inside that glob. `AI-E13-3` owns the narrowing; do not attempt it here.
- **Guards going RED on a full run are usually guards WORKING.** 13.2 hit four and loosened none.
  If a guard you did not expect fires, read what it says before touching it — and never make it
  green by narrowing it.
- **Story 13.1's precedent is your template for a NEW cohesive test module**:
  `tests/test_validation_set_decision.py` opens with a docstring that states the id range, why the
  module exists, why it is not an extension of `test_evidence_citation.py`, and what the rule is.
  Follow that shape exactly — **except** that this module opens **no** new ids and must say so.
- **Line numbers in this repository drift, constantly.** Every story since Epic 11 has found a
  stale coordinate; `test_module_size_ceiling.py:34`'s cite (AC6.4) is another one. **Locate every
  block by anchor text and re-verify before editing.**
- **Local gates are Windows-only; CI is an ubuntu matrix**, and a green local suite has already
  shipped POSIX-only bugs to master from this tree. See "Testing requirements".

### Testing requirements

- **Platform neutrality is not optional.** In the new module and in every probe you write:
  `pathlib` only (no `os.sep`, no drive letter, no backslash literal, no `Path` compared to a
  hand-built string); **explicit `encoding="utf-8"`** on every read and write; **explicit
  `newline="\n"`** on every write; **no CRLF-sensitive byte or line count**; deterministic
  ordering (`sorted()`) wherever a set or a glob is rendered into a message. The moved code
  already does all of this — **preserve it, do not "modernise" it**.
- **Non-vacuity travels with the assertions.** `-21`'s *"registry is non-empty / file exists /
  parses to more than 10 sentences"* and `-22`'s *"globs resolve to something / every registered
  name is found"* are the anti-vacuity machinery. If any of them is dropped in the move, the guard
  passes by reading nothing.
- **RED-then-green at the real seam, with the transcript** (AC3). A relocation that is never seen
  to fail from its new home is a relocation nobody has watched work.
- **The full suite is the gate, twice more than usual:** once with the two probe registrations in
  place (AC4.3) and once after removing them (AC4.4), plus the ordinary final run after the last
  prose edit (AC7.4).
- **Report actual numbers against the `867a3bd` baselines** (AC7.1). Never "all green".

---

## Tasks & Subtasks

- [ ] **Task 0 — Re-measure the premise on your own baseline (AC: 4.1)**
  - [ ] Record your HEAD sha. Measure `len(text.splitlines())` for
        `tests/test_evidence_citation.py` — expect **1200**.
  - [ ] **Reproduce §0.1 yourself**: probe document → `-22` RED; register it → `-22` GREEN and
        `MAINT-001-02` RED. Capture both. **Revert completely and prove it with
        `git status --porcelain`.**
  - [ ] Capture the three baseline gate numbers. Report any divergence from §0 as a finding.
- [ ] **Task 1 — Create the new module (AC: 1, 5)**
  - [ ] Locate the four blocks **by anchor text** (§0.2) and relocate them **verbatim** —
        comments, messages and blank-line structure intact.
  - [ ] Write the module docstring: cohesion statement, the id range it holds, **that it opens no
        new ids**, why the boundary is where it is (DN-1), why `-21b` stayed (DN-2), and the one
        import edge (DN-3, AC1.5).
  - [ ] Add the four imports and the two derived path constants (AC1.6).
- [ ] **Task 2 — Edit the retained module, and only in the four permitted ways (AC: 1, 5.7)**
  - [ ] Remove the moved blocks.
  - [ ] Amend the module docstring: the new cohesion statement, where the registry went, and the
        two bullets at `:32-38` whose subjects now straddle the boundary.
  - [ ] Re-point the `:63-81` Story 12.9 comment's `_STATUS_DOCUMENTS` reference, **preserving the
        decision it records**.
  - [ ] Add the new module's path constant beside `_GUARD_FILE`, with the DN-3 cycle comment.
  - [ ] Strike-and-correct the `epic-13-retro-INTERIM` registration comment's now-false last
        sentence, in its new home (AC5.4).
- [ ] **Task 3 — Register the new guard where guards are registered (AC: 6.1, 6.2, 6.3)**
  - [ ] Amend `architecture.md` §H `:648` and §Enforcement `:963-969`, dated and attributed.
  - [ ] Add the `AI-E12-1` registration rule to §Enforcement.
  - [ ] Extend `-23`'s anchor enumeration: the new module's path in **both** sections, plus one
        phrase from the registration rule. **Add only.**
- [ ] **Task 4 — Re-point the three live docstring citations (AC: 6.4, 6.5)**
  - [ ] `test_module_size_ceiling.py:34` — by **symbol**, and record the drift you found.
  - [ ] `test_spec_claim_scope.py:5` and `test_v1_commitment_closure.py:4` — name both hosts.
  - [ ] **Verify you changed no assertion in any of the three** (`git diff` them and say so).
- [ ] **Task 5 — Prove every moved assertion still bites (AC: 3)**
  - [ ] `-21` RED at the real seam from its new home, then restored and proven restored.
  - [ ] `-22` RED → registered → GREEN → removed → GREEN.
  - [ ] `-21b` run from its retained home; confirm untouched.
  - [ ] Paste every command and its output into the Debug Log.
- [ ] **Task 6 — Prove the deadlock is broken (AC: 4)**
  - [ ] Plant **two** probe status documents, one per pattern, >10 sentences each, LF, utf-8.
  - [ ] Register both. **Full suite** — green, 1597 collected.
  - [ ] Remove both probes and both registrations. **Full suite** — green, 1597 collected.
  - [ ] `git status --porcelain` shows no residue anywhere. **Nothing probe-related is committed.**
  - [ ] Record both modules' final line counts and headroom; if the retained module is above 1100,
        do AC4.6.
- [ ] **Task 7 — Verify the invariants (AC: 2, 5)**
  - [ ] Compare `test_TC_ArgusAgent_*` name sets before (`git show HEAD:...`) and after. Equal.
  - [ ] Collected count identical: **1597**.
  - [ ] `assert` counts before/after. Enumerate the four permitted edits and state that there is
        no fifth.
- [ ] **Task 8 — Ledger, gates, hand-off (AC: 7)**
  - [ ] Append the dated Story 13.4 section to `deferred-work.md`, including `DF-13-4-A`
        (record-only) and the relocated node ids. **Append only — edit nothing above it.**
  - [ ] Run all three gates. Report actual numbers as deltas against §0's baselines.
  - [ ] **Run the full suite after the last prose edit** (`AI-E13-1`).
  - [ ] Fill in the Dev Agent Record, File List and Change Log. Confirm `git tag -l` is still
        empty and nothing outward-facing was performed.

---

## Dev Agent Record

### Agent Model Used

_To be completed by the dev agent._

### Debug Log

_To be completed by the dev agent. Required: the Task 0 reproduction, every RED/GREEN transcript
from Tasks 5 and 6, the two full-suite runs with probes in and out, the id-set comparison, the
assert counts, and the final line counts of both modules with headroom._

### Completion Notes

_To be completed by the dev agent. Required: DN-1..DN-5 each confirmed or diverged-from with the
rejected alternative named; the enumerated list of edits to `tests/test_evidence_citation.py` with
the statement that there is no fifth; and the measured gate deltas._

### File List

_To be completed by the dev agent._

### Review Findings

_To be completed by the code-review agent._

---

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-08-17 | v0.1 | Story contexted on HEAD `867a3bd`. **The deadlock was REPRODUCED BY EXECUTION, not assumed** (§0.1): with an unregistered probe status document on disk `TC-ArgusAgent-DOCS-001-22` fails and `MAINT-001-02` passes; registering the probe — the only sanctioned fix for that red — takes `tests/test_evidence_citation.py` to **1201 lines**, so `-22` and `-21` pass and `MAINT-001-02` fails. **There is no green intermediate state**, and the only two moves that would produce one are the two this repository forbids by name. A **feasibility dry run of the split was also executed and reverted** (§0.2): the four blocks relocate verbatim, `-21` and `-22` pass from the new module, the retained module's six remaining assertions pass, the cross-module import resolves with no `conftest.py` change, and the measured result is **1030 / 192 lines** before docstrings. The remedy is **cited, not re-derived** — `test_validation_set_decision.py:6-14` and `test_module_size_ceiling.py::_REMEDY` lock it as a cohesion split, *"never shaving lines to make room, and never an exemption"*, and record that splitting this file *"belongs to a story that says so"*. **Test ids are hard-locked** (AC2): `-20`..`-23` are cited at `architecture.md:648` and `:964`, at `deferred-work.md:1384`/`:2236`/`:2523` — one of which is a full pytest node id — and by five test modules **in three different forms requiring three different treatments**, measured and separated in §0 (ids to amend, a line-number cite to re-point by symbol, dated measurements to leave byte-unchanged). **Boundary decided and recorded as DN-1**: `_STATUS_DOCUMENTS` has exactly three readers and none is `-20`/`-21b`/`-23`/`-24`/`-25`/`-25b`, so the population lifts out with one import edge; the Story 12.9 release-surface half was the rejected alternative and is recorded as the **next** boundary rather than taken here. **DN-2** keeps `-21b` beside the derivation it controls and requires both docstrings to say so. **DN-4** rejects `AI-E13-2`'s data-file option, because every registry entry carries the prose record of its own registration. **`AI-E12-1`'s second half is written down as a rule** in §Enforcement (AC6.3), which is the other deliverable `AI-E13-2` names. **Found by measurement and recorded rather than fixed** (§0.3): `TC-ArgusAgent-DOCS-001-24`/`-25` are defined **twice**, by Story 10.2 and Story 12.9 in two modules — a three-epoch-old id collision that AC2 forbids fixing here; filed as `DF-13-4-A`, record only. **One tracker premise measured stale:** `origin/master` **equals** HEAD, not 13 commits behind — master is live, so `AI-E13-1`'s hand-off-green requirement is load-bearing. Baselines, measured by execution: `pytest` **1597 collected / 1597 passed / 0 failed / 0 skipped, exit 0**; `mypy argus` **Success, 86 source files**; `bandit -r argus` **19 Low / 0 Medium / 0 High**. `git tag -l` empty; nothing outward-facing. | Scrum Master (create-story) |
