---
baseline_commit: 93adc94d0203eaaf4d1cb1d8bc7113e9b885beed
baseline_note: >-
  `HEAD` = `93adc94` on `master`, **6 commits unpushed**, `git tag -l` **EMPTY** (both re-measured
  2026-08-12). Epic 10 is 5/5 `done`; Stories 11.1–11.4 are `done` and **their deltas are in the tree,
  uncommitted**. **No CI run has ever seen a line of Epic 10 or Epic 11.** Every baseline figure in
  this story is **LOCAL, Windows / CPython 3.11.15**, under the dated risk acceptance recorded in
  Story 11.1 §0.1 (AI-E10-1, 2026-08-11, XAgent007) — carried forward, not re-taken. **Make no CI
  claim.**
  ⚠️ **The tree is NOT clean and you did not dirty it.** `git status --porcelain -- argus/` shows
  exactly **six ` M` lines** — `argus/cli.py`, `argus/detectors/vacuous_test.py`,
  `argus/index/ast_index.py`, `argus/reports/generator.py`, `argus/shared/grammar_status.py`,
  `argus/verdict/negative_assurance.py` — the reviewed and `done` deltas of 11.1/11.2/11.4.
  `CHANGELOG.md` is **staged** (`M `) from 11.3. `README.md`, `pyproject.toml`,
  `tests/test_release_surface_honesty.py`, `tests/test_invocation_contract.py` and the four
  `_bmad-output/**` planning artifacts are inherited-dirty from 10.5/11.1–11.4. `_bmad/**` churn is
  AI-E10-9's. `bmad-dev-loop-pack/`, `.bmad-drift-audit/`, `_bmad-output/audit-reports/*` and the
  untracked `argusdemo/` belong to the orchestrator/host. **Do not commit, revert, restage or "tidy"
  any of it.** THIS FILE is untracked and IS yours: `git add` it with your delta or you repeat AI-E8-1.
  ⚠️ **ONE TEST IS ALREADY RED AND IT IS NOT YOURS.** See §0.4 (`DF-11-1-A`), carved out **by node id**
  for the **fifth** consecutive story. Any *second* red is yours.
  ⚠️ **THE UNIT-2 LOC CLIFF IS 13 PHYSICAL LINES AND THIS STORY LANDS IN UNIT 2.** See §0.2. The
  minimum working fix was BUILT AND MEASURED: **+8**. It fits with **5 lines spare**. This is not an
  estimate — see §A.1.
  ⚠️ **THREE OF THE EPIC'S PREMISES FOR THIS STORY ARE STALE OR FALSE.** See §0.3. Two of the three
  README "falsehoods" the epic names are **already corrected on this tree**, and the module-count
  premise is off by one in both numerator and denominator. **Do not implement the sentence. Implement
  §A.**
  **Every count, coordinate, verdict, exit code, LOC figure, sha256 and partition id below was
  produced by EXECUTING code on THIS tree on 2026-08-12.** Treat every line number as a hint you must
  re-verify by anchor text.
story_key: 11-5-published-artifact-is-complete-and-true
epic: 11
---

# Story 11.5: The published artifact is complete and says only true things

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **ArgusAgent story — Argus repo.** ArgusAgent (formerly APAA) is a self-contained headless audit
> tool extracted from the Minions monorepo into its own repository (`Agent-Argus`, distribution
> `argus-agent`, package `argus/`). **RS-1 is binding: all work lands in THIS repo. The
> `minions_core/apaa/` copy in the Minions repo is legacy — no modification, no back-port.** Planning
> artifacts live under `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is that folder's
> `sprint-status.yaml`. Prose in older documents saying `design-artifacts/APAA/`, `minions_core/apaa/`
> or `tests/apaa/` should be read as `design-artifacts/ArgusAgent/`, `argus/` and `tests/`.
>
> 🔵 **This is the LAST story of Epic 11.** The epic retrospective runs immediately after it closes.
> **It still publishes nothing** — no push, no tag, no release, no `workflow_dispatch`. The publish is
> Story **12.9**. This story proves a claim *about* the artifact by **building it locally**.

---

## Story

As a developer installing Argus from a public index,
I want every shipped module to import and every claim in the docs to be true,
so that what I install is what the documentation describes.

**Why this is one story, and what it is not.** Epic 11's charter is *"nothing unsafe or untrue can be
published."* Stories 11.1–11.4 closed defects in what Argus **says** and **decides**. This one closes
the last class: defects in **the thing that actually ships** and in **the sentences that describe it**.
It makes five shipped modules importable from the distribution, replaces the source-tree guard that
cannot see the difference with one that inspects a **locally built wheel and sdist**, corrects the
stale published import figures, and corrects the false-subject "Minions" claims — including the two
that are printed on a user's terminal by `argus audit .` today. It ships **no new detector**, changes
**no decision-table row, threshold or exit code**, adds **no dependency**, adds **no file under
`argus/`**, and publishes **nothing**.

**Why it is release-blocking.** The defect is invisible from inside this repository by construction.
The test suite runs with `tests/` on `sys.path`; the wheel does not contain `tests/`. Every gate this
project owns is green while five of the seventy-two shipped modules raise `ModuleNotFoundError` on the
first line a consumer types. Publishing converts that from an internal curiosity into the first thing
a stranger sees. Worse: **the guard that is supposed to hold the line has been proven blind** (§A.2).

**The direction that matters.** A wrong number in a published document is not cosmetic here. Epic 9's
retrospective named this exact class — *"prose that restates a pinned figure is a fork of that figure,
and a fork can rot inside a single story"* — and prescribed the remedy: *where a document states a
number that a test also pins, either the document cites the pin or a test asserts the document.* **The
fork rotted again.** `README.md:151` and `CHANGELOG.md:397,402` still publish *"66 of the 71 shipped
modules import"*. Measured today from a freshly built wheel: **67 of 72 import**. Both numbers moved
and nothing went red.

⚠️ **Read §0 before anything else.** Six items gate this story.

---

## Story Context

### Method statement — everything in §0–§F was MEASURED on this tree on 2026-08-12

Every count, coordinate, verdict, exit code, sha256, LOC figure and partition id below was produced by
running `git`, `pytest --junit-xml`, `mypy`, `python -m argus.cli audit .`, `python -m build`, by
importing and calling `argus.dogfood.partition_plan.build_full_repo_plan('.')`, and — for §A.1 and
§A.2 — by a **REVERSIBLE ON-DISK EXPERIMENT**: the candidate fix was written into the real
`argus/precision/replay_harness.py`, a wheel was built from it, every shipped module was imported in a
clean subprocess with this repository removed from `sys.path`, the full suite and `mypy` were re-run,
and the file was then **restored and sha256 round-tripped byte-identically**
(`be468fdfe9ea646ce5407f7b9d945a9c10574d5121cb24b6a476326dacb238ad` before **and** after;
`git status --porcelain -- argus/` shows no `M` line for it). **Re-derive everything; transcribe
nothing.**

---

### §0. The six gates on this story — read these first

#### 0.1 — 🔴 DATED RISK ACCEPTANCE, CARRIED FORWARD (AI-E10-1)

**Recorded by XAgent007 (operator), 2026-08-11. Carried forward, not re-taken.** No CI run covers any
Epic 10 or Epic 11 sha. Every figure in this story and every figure you produce is **LOCAL,
Windows / CPython 3.11.15**. CI evidence for your delta is **NOT ESTABLISHED** and you must write that
phrase rather than imply a run. A human establishes one later by pushing and running `audit-ci.yml`.

#### 0.2 — 🔴 THE `DF-10-4-D` FENCE **AND** THE 13-LINE LOC CLIFF — BOTH BIND

**(a) No new file under `argus/**`.** Measured: `git ls-files -- argus` = **72**. It must still be
**72** when you finish, before *and* after `git add`. `git ls-files` reads the **index**, so staging a
new module moves the audited population even if you never commit. `argus/shared/grammar_status.py`
and the other four `argus/shared/` modules already exist — extending an existing module is fine.

**(b) The unit-2 LOC cliff is 13 physical lines, and this story writes into unit 2.** Measured twice
by executing `build_full_repo_plan('.')`:

| unit | partition_id (12ch) | LOC | files |
|---|---|---|---|
| 1 | `477ef77d7b65` | 1330 | 21 |
| 2 | `82a3d605e61e` | **14987** | 39 |
| 3 | `ed6d08f25ce3` | 4116 | 12 |

The soft target is **15000**. The cliff was measured **to the line** by perturbing the in-memory LOC
map for `argus/precision/replay_harness.py`:

- `+13` → unit 2 = 15000, **all three partition_ids byte-unchanged**.
- `+14` → unit 2 splits: ids become `58dbc3251926` (14743) and `9408a0fe1acf` (4374). **Two of three
  ids move.**

Units **1 and 3 absorb +3000 with all ids unchanged** (measured). `tests/**`, `action.yml`,
`.github/**`, `pyproject.toml`, `README.md` and `CHANGELOG.md` are **outside the audited population
entirely** — `scope_prefix` is `'argus/'` — so nothing you write there costs a line of this budget.

**`argus/precision/replay_harness.py` is in UNIT 2** (verified against the unit-2 work manifest). So
is `argus/dogfood/proof_run.py`, `proof_types.py`, `argus/audit/deep_audit.py`,
`argus/cost/budget_governor.py`, `argus/evidence/bundle.py` and `argus/index/partitioner.py`.

**⛔ IF YOUR UNIT-2 DELTA WOULD EXCEED +13: HALT AND ESCALATE. DO NOT REGENERATE ANY DOGFOOD
ARTIFACT.** That remedy belongs to Story 12.1; Story 10.4 refused it once already, and regenerating a
committed artifact to make your own change look clean is falsifying the record. Re-measure with
`build_full_repo_plan('.')` **after** staging and quote all three ids.

**Measured consequence of overrun, so you know exactly what you are avoiding:** at `+17` the full
suite produced **exactly one** additional red —
`tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation`
(*"unit '58dbc3251926' missing from the committed plan (rot?)"*). Not five. The "five committed-artifact
staleness tests" figure inherited from Story 10.4 describes the **new-file** trigger, not the
**LOC** trigger; only the partition-plan artifact pins the ids.

#### 0.3 — 🟠 THREE OF THE EPIC'S PREMISES ARE STALE OR FALSE (AI-E10-3, discharged)

Re-measured by execution on this tree, 2026-08-12:

| Epic AC premise | Measured today | Verdict |
|---|---|---|
| *"**5 of 71** wheel modules fail to import"* | The wheel holds **72** `argus/**` modules (77 entries = 72 `.py` + 5 `dist-info`). **67 of 72 import; 5 fail**, all `ModuleNotFoundError: No module named '_registry'`, and they are exactly the five named. | **Numerator and denominator both stale by one.** The five-module list is **exact**. Use **67 of 72**. |
| *"**22** bare-word 'Minions' subject claims across **14** `argus/**` modules"* | **21** occurrences across **14** modules. (The ledger `DF-9-2-B` says 25 total / 23 outside `dogfood/`; also stale.) | **Count stale; module count exact.** §A.3 gives the full enumeration — use it, do not re-count by hand. **This project has hand-counted wrong six times.** |
| *"README's *'INTERIM — resolve straight from this repository at a tag'* is false"* and *"its CLI example omits the `audit` subcommand and the required repo positional"* | **Both already corrected on this tree.** `README.md:51-57` carries an explicit ⚠️ block: *"This command does not resolve today. Tag `v0.1.0` has not been created or pushed — `git tag -l` is empty at this commit."* `README.md:~200` reads *"the `audit` sub-command is required"* with `argus audit .` and an inline *"Corrected 2026-08-10 (Story 10.3 / DF-AUD-APAA-E)"* note. | **CLOSED by prior stories.** Do **not** "fix" them again. AC4 instead **mechanises** the tag disclosure so it cannot rot in either direction. |

**The one README claim in that clause that IS still live:** `README.md:189` — *"When installed,
`ArgusAgent` registers slash commands in your AI coding assistant (Claude Code, Cursor, Cline, etc.)"*
followed by **seven** `/audit …` commands. Measured: `pyproject.toml:73-76` ships **three** console
aliases (`argus`, `argus-agent`, `repo-audit`) **all → `argus.cli:main`**, and the built wheel contains
**zero** non-`.py` data assets (77 entries = 72 modules + 5 `dist-info`). **There is no registration
mechanism and no command asset in the distribution.** `README.md:31` makes a similar claim but is
already under a heading that says *"repository-only; these directories are not part of the
`argus-agent` distribution"* — that one is qualified; `:189` is not.

#### 0.4 — 🟡 ONE RED IS ALREADY THERE AND IT IS NOT YOURS (`DF-11-1-A`)

`tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed`
fails on this tree because the untracked `epic-10-retro-2026-08-11.md` is an unregistered status
document. Measured baseline: **1395 collected / 1394 passed / 1 failed / 0 errors / 0 skipped.**

It is **carved out BY NODE ID for the fifth consecutive story** and is **NOT closed, NOT touched**.
Closing it would mean amending a signed Epic-10 retrospective from inside Epic 11 to make a test pass
(Story 8.1's AC18 precedent). **Any second red is yours.**

#### 0.5 — 🔴 NOTHING IS PUBLISHED BY THIS STORY

No `git push`, no `git tag`, no `gh release`, no `workflow_dispatch`, no index upload. This is
pointed here because the story is *about* the published artifact: **you must verify a claim about the
artifact WITHOUT publishing it.** You build the wheel and sdist **locally**, into a directory that is
**not** committed, and you delete or gitignore them. `git tag -l` must still be empty when you finish.
`origin/master` must not move.

#### 0.6 — 🟡 THIS WILL BE THE **FIFTH** CONSECUTIVE EDIT TO `_NOTE_SECTIONS` (`DF-11-4-D`)

`tests/test_release_surface_honesty.py`'s `_NOTE_SECTIONS` registry has been edited by 11.1, 11.2,
11.3 and 11.4. AC5 requires a new `### …` section in `CHANGELOG.md`, and that registry is designed to
go **RED** until a new section is registered deliberately — so **this story makes it five.** Stated
here explicitly, as `DF-11-4-D` asks. **This is not a licence to skip the CHANGELOG section**: an
unrecorded consumer-visible fix is exactly the failure this epic exists to prevent. Register it
deliberately, state your ordering reason in the comment as the registry's own comment demands, demote
nothing, and note the fifth-edit fact in your completion notes so the operator's Epic-11 checkpoint
review has it.

---

### §A. What was measured, and what it changes

#### A.1 🔑 THE DECIDING MEASUREMENT — the fix FITS, with 5 lines spare

Story 11.4's dev **predicted** 11.5 "will not fit". That was a prediction, not a measurement. It has
now been settled by building the fix and measuring it.

The whole of DF-9-2-A is **one file**, `argus/precision/replay_harness.py` (381 lines, unit 2). Its
defect is at `:86-96`: a **module-level** `sys.path.insert` of `<repo>/tests/cartridges` followed by an
unconditional `from _registry import …`. `tests/` is not in the distribution and must not be.

**The measured minimum working fix is `+8` physical lines** (381 → 389). Executed, not estimated:

| measurement | result |
|---|---|
| unit 2 after the fix | **14995 / 15000** — 8 of 13 consumed, **5 remaining** |
| partition ids after the fix | `477ef77d7b65` / `82a3d605e61e` / `ed6d08f25ce3` — **all three BYTE-UNCHANGED** |
| `mypy argus` | **clean, 72 source files** |
| full suite (`DF-11-1-A` deselected) | **1394 tests / 0 failures / 0 errors / 0 skipped** |
| freshly built wheel, repo off `sys.path`, one clean subprocess per module | **72 of 72 import, 0 fail** (baseline: **67 of 72, 5 fail**) |

The proven shape (this is the *demonstrated-viable* form, not a mandate — see §B):

```python
from typing import TYPE_CHECKING, Any
...
# The 6.5 cartridge registry (tests/cartridges/, repository-only — the DISTRIBUTION does
# not carry it and must not) is resolved ON DEMAND, never at module import: DF-9-2-A.
_CARTRIDGES_DIR = Path(__file__).resolve().parents[2] / "tests" / "cartridges"
if TYPE_CHECKING:
    from _registry import CartridgeSpec, GoldenFinding  # type: ignore[import-not-found]


def _registry_module() -> Any:
    """Import ``_registry`` lazily (DF-9-2-A) — never at module import time."""
    if _CARTRIDGES_DIR.is_dir() and str(_CARTRIDGES_DIR) not in sys.path:
        sys.path.insert(0, str(_CARTRIDGES_DIR))
    import _registry  # type: ignore[import-not-found]

    return _registry
```

…plus, inside `compute_precision`: `registry: tuple[CartridgeSpec, ...] | None = None`, a two-line
`if registry is None:` resolution, `n = registry_module.populated_planted_defect_count()`, a local
`floor_n`, and a keyword-only `floor_n: int | None = None` on `precision_gate_status_for` so
`argus/dogfood/proof_run.py:642`'s existing call **does not change**. `VALIDATION_SET_FLOOR_N` leaves
`__all__` (see DN-2). **No constant is forked** — every value still comes from `_registry` (AR7/§3.3).

#### A.2 🔑 THE EXISTING GUARD IS VACUOUS AND THE README SAYS IT IS NOT

`tests/test_release_preflight.py::test_TC_ArgusAgent_RELEASE_001_11_distribution_gap_is_pinned_exactly`
computes `_modules_reaching("_registry")` by **walking the source tree's import graph with `ast`**. It
was described in `README.md:166-167` as *"pinned in both directions … so this list cannot drift from
the code."*

**Both halves of that sentence are false, and both were demonstrated:**

1. **It cannot see the fix.** With the `+8` lazy fix on disk — wheel behaviour changed from *5 fail* to
   *0 fail* — `-11` **stayed GREEN**. `import _registry` inside a function body is still an
   `ast.Import` node named `_registry`, so the walk finds it exactly as before. The guard is
   structurally incapable of distinguishing a module-level import from a lazy one, which is **the
   entire content of the fix**. `DF-9-2-A`'s stated close condition — *"which is pinned in BOTH
   directions, so a fix that leaves the record stale goes RED"* — **is false as written.**
2. **The record already drifted while it was green.** The denominator moved 71 → 72 and the importable
   count 66 → 67 during Epics 10–11, and no test noticed, because the guard pins a *set of paths*, not
   the *numbers* the documents publish.

**This is the story's central design constraint: a guard that inspects the SOURCE TREE instead of the
BUILT ARTIFACT is vacuous by construction for a claim about the built artifact.** AC2 requires the
replacement to build a real wheel and sdist and import from them.

#### A.3 The 21 bare-word "Minions" occurrences, enumerated by execution, with their unit

Regex `(?<![A-Za-z_])Minions(?![A-Za-z_])` over `git ls-files -- argus`. Do **not** re-count by hand;
re-run the regex.

**Unit 1 — free (≥3000 lines headroom):**

| site | text (trimmed) |
|---|---|
| `argus/__init__.py:21` | *"It installs and runs **with no Minions package present**"* |
| `argus/audit/minions_llm_adapter.py:1` | *"Backward-compatible Minions LLM Adapter wrapper…"* |
| `argus/cost/__init__.py:4` | *"…reusing the Minions configuration contract…"* |
| `argus/dogfood/proof_render.py:71` | *"The independent Story-7.2 run over the Minions …"* |
| `argus/evidence/__init__.py:3` | *"…SEPARATE from the Minions …"* |
| `argus/store/__init__.py:7` | *"…the Minions `WorkspaceContainmentError` containment logic…"* |

**Unit 3 — free (≥3000 lines headroom). Two of these are USER-FACING RUNTIME OUTPUT:**

| site | text (trimmed) |
|---|---|
| `argus/store/paths.py:7`, `:17`, `:72` | *"REUSE Minions' canonical containment authority by import"* etc. |
| `argus/store/writer.py:15` | *"the Minions `WorkspaceContainmentError` + `Path.resolve()`…"* |
| 🔑 `argus/verdict/negative_assurance.py:174` | *"Its findings rest on the **Minions dogfood corpus**, a self-audit of this repository…"* |
| 🔑 `argus/verdict/negative_assurance.py:183` | *"…adjudication over the **Minions dogfood corpus**."* |

**Unit 2 — 9 occurrences across 5 modules. EVERY LINE HERE COSTS BUDGET:**

| site | text (trimmed) |
|---|---|
| `argus/audit/deep_audit.py:4` | *"wired into the Minions product run path — nothing in Minions orchestration"* |
| `argus/cost/budget_governor.py:35`, `:275`, `:276` | *"the UPSTREAM Minions cost-guardrails module"*, *"Minions stayed the ONE hard-ceiling authority"* |
| `argus/dogfood/proof_run.py:5` | *"Story 7.2 originally ran it over the Minions platform"* |
| `argus/evidence/bundle.py:49`, `:51` | *"Separateness from the Minions governance bundle"* |
| `argus/index/partitioner.py:42` | *"the 18-2 Minions `is_relative_to`-not-`startswith` precedent"* |

#### A.4 🔑 The two occurrences that are printed on a user's terminal today

Verified by running `python -m argus.cli audit .`; stdout contains, verbatim:

> `argus: Instrument status: Argus's own finding precision has not been independently validated. Its
> findings rest on the Minions dogfood corpus, a self-audit of this repository with no human
> true-positive/false-positive adjudication behind it. …`

This is `INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED` at
`argus/verdict/negative_assurance.py:173-179` — **Story 11.1's FR34 disclosure**. Its sibling
`INSTRUMENT_DISCLOSURE_VALIDATED` (`:181-186`) carries the same phrase in the *future cleared* text.

**It is a false subject claim, and the sentence contradicts itself.** The corpus is a self-audit of
*this* repository — the sentence says so four words later — and `argus/dogfood/proof_run.py:5` records
that the Minions run was **Story 7.2's, superseded**. `argus/__init__.py:21` states Argus *"installs
and runs with no Minions package present."* Calling it *"the Minions dogfood corpus"* on the highest-
visibility surface Argus has is exactly `DF-9-2-B`'s class at its worst.

**It is already single-sourced, which makes it safe to change:** the module comment at `:165-171`
records that these constants are *"the ONE source for every surface"* and that `README.md`,
`CHANGELOG.md`, `pyproject.toml` and `action.yml` are **compared against them** by
`tests/test_instrument_disclosure.py`. Measured: the identical sentence appears at `README.md:10` and
`CHANGELOG.md:52`. Change the constant and those two copies **in the same change**, or 11.1's guard
turns red — which is the guard working.

#### A.5 Baseline gates, re-measured on this tree 2026-08-12

| gate | value |
|---|---|
| full suite | **1395 collected / 1394 passed / 1 failed / 0 errors / 0 skipped**; the one red is `DF-11-1-A` |
| `mypy argus` | **clean, 72 source files** |
| `git ls-files -- argus` | **72** |
| `git tag -l` | **empty** |
| dogfood units | `477ef77d7b65` 1330 / `82a3d605e61e` **14987** / `ed6d08f25ce3` 4116; `source_file_count` 72, `total_loc` 20433 |
| `python -m argus.cli audit .` | `verdict=RELEASE_READY deep_ratio=61/168 blocking_findings=0 assessed_deep_ratio=61/77 scope=application held_out=91`, **exit 0** |
| built wheel | `argus_agent-0.1.0-py3-none-any.whl`, **77 entries = 72 `.py` + 5 `dist-info`**; sdist `argus_agent-0.1.0.tar.gz`, **76 members**, **contains no `tests/`** |
| wheel importability | **67 of 72 import; 5 fail** — `argus/precision/__init__.py`, `argus/precision/replay_harness.py`, `argus/dogfood/proof_types.py`, `argus/dogfood/proof_render.py`, `argus/dogfood/proof_run.py` |

⚠️ **Measurement trap that cost a whole cycle — do not repeat it.** `.venv/Lib/site-packages/argus.pth`
is an **editable install pointing at this repository**. Running the import probe with `python -I`
(which implies `-E`, dropping `PYTHONPATH`) silently resolves `argus` **from the repo**, where
`tests/cartridges` exists, and reports a false **72 of 72**. The measurement is only valid when the
repository root is genuinely off `sys.path`. The method that works: extract the wheel to a temp dir,
launch `python -c` with a prelude that removes the repo root from `sys.path` by normalised absolute
path and prepends the extraction dir, from a `cwd` that is **not** the repository — then assert
`argus.__file__` resolves **into the temp dir** before trusting a single import result. **A probe that
cannot prove where it imported from is not a probe.**

---

### §B. The shape — proven viable under the fence and the budget, not mandated

You are free to implement DF-9-2-A differently, but whatever you do must satisfy **all** of:

- **no new file under `argus/**`** (§0.2a);
- **≤ +13 physical lines in unit 2** (§0.2b), re-measured after staging;
- every one of the **72** shipped modules imports from a **freshly built wheel** with the repo off
  `sys.path` (AC1);
- **no constant is forked** — `VALIDATION_SET_FLOOR_N` and `CARTRIDGE_REGISTRY` still come from
  `_registry`, never re-declared (AR7 / §3.3);
- `tests/test_precision_replay.py` and `tests/test_dogfood_plan.py` pass with **zero assertion
  changes** — their eight `compute_precision(emitted)` calls rely on the registry default and must
  keep working;
- `argus/dogfood/proof_run.py:642`'s call to `precision_gate_status_for` is **unchanged** (it is in
  unit 2 and every line there costs budget).

§A.1's shape satisfies all six and was executed end-to-end. If you deviate, re-run **all** of §A.1's
measurements, not a subset.

---

### §C. Design constraints a reviewer will check

1. **AR8 purity deviation, recorded not hidden.** `compute_precision`'s docstring says *"PURE (no I/O
   / clock / LLM / random — AR8)"* and the module header says the same. After the fix it performs one
   module import on the default path. **This is a strict REDUCTION of the module's existing I/O** — it
   previously did the same import unconditionally at *import* time, on every consumer's start-up path.
   Nothing became less pure; the blast radius shrank. **But the docstring must be corrected in place**,
   because this is the story whose thesis is that shipped modules say only true things. Correcting it
   costs 0 lines if you edit within the existing line span; it costs budget if you add lines. Budget
   for it in your ≤13.
2. **The `_registry` import must be guarded, not merely moved.** `_CARTRIDGES_DIR.is_dir()` before the
   `sys.path.insert` — inserting a non-existent path onto a consumer's `sys.path` is a side effect on
   someone else's process for no benefit.
3. **The module's other stale claims.** `:24` cites the caller as `tests/argus/test_precision_replay.py`;
   the real path is `tests/test_precision_replay.py`. `:83` cites `tests/argus/cartridges/`; the real
   path is `tests/cartridges/`. In-place corrections, 0 lines.
4. **`negative_assurance.py` is Story 11.1's surface.** Additive-and-corrective only. Do not reword the
   *status semantics*, do not touch the two-member `InstrumentStatus` vocabulary, do not change what
   removes the notice (Epic 13's adjudication), and do not delete either constant. You are correcting a
   **subject**, not a **claim**.
5. **FR16/FR37 boundary (11.1's precedent).** No verdict is reworded, upgraded or hedged. The decision
   table is untouched. `argus audit .` must still print `verdict=RELEASE_READY … exit 0` with
   `blocking_findings=0` and `assessed_deep_ratio=61/77`.
6. **`held_out` / `deep_ratio` arithmetic.** Each new test **file** you add moves `argus audit .`'s
   `deep_ratio` denominator and `held_out` by exactly **+1** each (measured precedent: 11.2 took
   `165→166` / `88→89`). Explain the movement arithmetically; an unexplained move is a finding.
7. **No new dependency.** `python -m build` and `zipfile`/`tarfile` are already available (`build` is
   used by `release.yml`); if `build` is absent in the dev environment the guard must **skip with a
   named reason**, never pass silently.
8. **Do not build a second build/inspect mechanism (AR7 / §3.3).** `scripts/release_preflight.py`
   already owns the release vocabulary — `PreflightContext.dist_files`, `check_e6_incomplete_build`
   ("both artifacts, or none"), `Unevaluable` for "could not ask". Your guard **extends** that
   vocabulary; it does not fork a parallel notion of "the built distribution". `release.yml` already
   runs `python -m build`; do not add a second build invocation to any workflow (and do not edit any
   workflow at all — §D).
9. **`argus/precision/__init__.py` must not need to change.** It re-exports six names, none of them
   registry symbols, and it was verified importable from the built wheel after the fix. If you find
   yourself editing it, your fix is in the wrong place.

**Watchlist — these must still pass, unmodified. Run them individually after T3:**

| test | why it is on the list |
|---|---|
| `tests/test_no_web_imports.py` (`:206`, `:435-456`) | imports `argus.precision.replay_harness` live and asserts it pulls in no LLM adapter — a lazy import must not change that |
| `tests/test_instrument_disclosure.py::test_TC_ArgusAgent_DOCS_001_45_the_precision_harness_is_not_on_the_user_path` | 11.1's `DN-3`: the harness stays **off** `argus.cli`'s import path. Making it *safe* to import is not licence to import it |
| `tests/test_instrument_disclosure.py::test_TC_ArgusAgent_DOCS_001_46…` | pins the disclosure/expiry mechanics you are editing the text of (AC6.2) |
| `tests/test_precision_replay.py` (15 tests) | eight `compute_precision(emitted)` calls depend on the registry default |
| `tests/test_dogfood_plan.py` | the partition-plan artifact test — **this is the one that goes red if you blow the LOC budget** |
| `tests/test_cartridge_selfaudit.py` | imports `_registry` directly; unaffected, but proves the registry itself was not touched |
| `tests/test_release_surface_honesty.py` `-16`/`-17`/`-18` | the note-section registry and the over-claim guard over `README.md`/`CHANGELOG.md` |

---

### §D. ⛔ FENCES — what this story must NOT touch

| fence | why |
|---|---|
| **No new file under `argus/**`** — `git ls-files -- argus` stays **72** | `DF-10-4-D` / AI-E10-2 |
| **≤ +13 physical lines in unit 2**; HALT rather than exceed | `DF-10-4-D` second trigger, measured §0.2b |
| **No dogfood artifact regenerated** (`minions-dogfood-partition-plan.md`, `-budget-plan.md`, `-proof.md`) | That remedy is Story 12.1's; 10.4 refused it once |
| **`argus/pipeline.py` byte-unchanged** | NFR-M1 breach at 1331/1200, fenced to Story 12.1 |
| **`argus/verdict/verdict_gate.py` byte-unchanged** | FR16 decision table; no verdict change in this story |
| **Nothing published** — no push, tag, release, dispatch, index upload; `git tag -l` stays empty | §0.5; the publish is 12.9 |
| **`DF-11-1-A` not touched, not closed** — carved out by node id | §0.4 |
| **No blanket find-and-replace of "Minions"** | Epic AC is explicit: each occurrence is read and classified |
| **Built `dist/` artifacts are not committed** | They are a measurement, not a deliverable |

**Ruled OUT of scope, with reasons** — re-verified 2026-08-12 and left open:

- **`DF-11-2-A` / `-B`** — target Story 12.5 with named owners; unchanged here.
- **`DF-11-4-A` / `-B` / `-C`** — 11.4 review items; `-C` is an accepted design property, the others
  have no owning story in this epic.
- **`DF-10-2-A`** (C/C++/Ruby/Rust ground but extract zero definitions) — AI-E10-4 offers "(11.5), or a
  dated V2 decision" as its home. **Ruled OUT of 11.5.** It is a *detector-coverage* change that moves
  classification on real repositories; this story is packaging and documentation correctness, and
  widening extraction here would put an unrelated behavioural change inside the epic's last story with
  no room in the unit-2 budget to do it safely. Recorded for the Epic-11 retrospective so it does not
  vanish: **AI-E10-4 remains OPEN and still needs a home or a dated deferral.**
- **The untracked `argusdemo/demo.sh`** — an operator item held for the epic checkpoint.
- **`DF-9-2-C`** (three tracked `.pyc` files under `argus/dogfood/__pycache__/`) — adjacent and
  tempting; `git rm --cached` changes the index, which is precisely the `DF-10-4-D` trigger. **Leave
  it.**

---

### §E. Traps previous stories already paid for — the five that apply

1. **A guard that inspects the wrong artifact is decorative** (11.3's run-block resolver blind to an
   ordinary YAML shape; §A.2's source-tree walk blind to the whole fix). Prove your guard bites by
   making it **RED first** against the genuinely unfixed tree, with the **final** test code.
2. **A premise can expire between the epic and the story** (11.2's `DF-8-2-B`; 11.4's headline
   `Given`). §0.3 already found three. Re-measure anything else you are about to rely on.
3. **Hand-counting has been wrong six times in this project.** Every count in your ACs must be produced
   by a closure over the real artifact, not a literal list (AI-E10-5).
4. **Prose that restates a pinned figure is a fork of that figure** (Epic-9 retro). The remedy is
   AC3: the documents must be **asserted by a test**, not re-typed correctly once.
5. **Staging is a state change.** `git ls-files` reads the index. Re-measure the fence and the budget
   **after** `git add`, not before.

---

## Acceptance Criteria

### AC1 — Every shipped module imports from a locally built distribution

1. `argus/precision/replay_harness.py`'s registry import is **lazy or optional**: importing the module
   from a distribution that contains no `tests/` tree **succeeds**. No new file under `argus/**`.
2. Proven from a **freshly built** wheel — `python -m build`, then one clean subprocess per shipped
   module with this repository removed from `sys.path` and `cwd` outside the repository. The probe
   **asserts `argus.__file__` resolves into the extracted distribution** before trusting any result
   (§A.5's trap). Result recorded: **72 of 72 import, 0 fail.**
3. The same probe run against the **unfixed** file reproduces **67 of 72 / 5 fail** with
   `ModuleNotFoundError: No module named '_registry'`, naming the five modules. RED-first, with the
   **final** guard code.
4. No constant is forked: `CARTRIDGE_REGISTRY`, `VALIDATION_SET_FLOOR_N` and
   `populated_planted_defect_count` are still sourced from `_registry` (AR7 / §3.3).
5. `tests/test_precision_replay.py` and `tests/test_dogfood_plan.py` pass with **zero assertion
   changes**, and `argus/dogfood/proof_run.py` is **byte-unchanged**.

### AC2 — 🔑 The guard inspects the BUILT ARTIFACT, and the vacuous one is retired

1. A committed guard **builds the wheel and the sdist locally** and asserts, over the **archive
   members**, that (a) every shipped `argus/**` module imports in a clean subprocess with the repo off
   `sys.path`, and (b) the sdist contains no `tests/` tree. Nothing is published, pushed or uploaded.
2. `_NOT_IMPORTABLE_FROM_DISTRIBUTION` is updated to the measured post-fix set (**empty**) and the
   record is pinned so a **regrowth** of the broken set fails.
3. **The vacuity is demonstrated, not asserted.** The story records — and a test comment states — that
   `TC-ArgusAgent-RELEASE-001-11`'s source-tree `ast` walk stayed **GREEN** across the entire fix.
   `-11` is **narrowed or replaced explicitly, never silently deleted**: if it survives, its docstring
   must say what it can and cannot see.
4. The new guard **fails when the artifact is wrong**: proven by injecting a module that imports
   `_registry` at module level into the *built* tree (or by building from the unfixed file) and
   observing RED, then restoring and re-measuring green.
5. If `build` is unavailable, the guard **skips with a named reason**. It never passes silently.
6. AC2's guard is a **closure over the archive**, never a hard-coded module list (AI-E10-5).

### AC3 — Every published module figure is asserted, not re-typed

1. `README.md:151` and `CHANGELOG.md:397,402` are corrected from **"66 of the 71"** / **"the wheel
   holds 71 modules"** to the measured values, and the five-module list is replaced by the true
   post-fix state.
2. `README.md:166-167`'s claim that the five files are *"pinned in both directions by
   `TC-ArgusAgent-RELEASE-001-11`, so this list cannot drift from the code"* is **corrected** — it was
   measurably false (§A.2) — and made true by naming the guard that actually holds it.
3. A test **asserts the documents against the live measurement** so the fork cannot rot again
   (Epic-9 retro's rule: *the document cites the pin, or a test asserts the document*). The test goes
   RED if the wheel's module count changes and a document is not updated, in **both** directions.
4. No document states a module count that this story did not re-derive by execution.

### AC4 — The tag disclosure is mechanised instead of re-fixed

1. Re-verified and recorded: `git tag -l` is **empty**, and `README.md:51-57` and `:104` already
   disclose that the interim install command does not resolve. **No re-fix is applied.**
2. A test pins the disclosure **in both directions**: while no tag exists the "does not resolve today"
   caveat must be present; the day a `v*.*.*` tag exists the test goes RED so the stale caveat is
   removed deliberately rather than shipped as a new falsehood.

### AC5 — The slash-command claim is marked forthcoming, never deleted

1. `README.md:189`'s unqualified *"When installed, `ArgusAgent` registers slash commands…"* is
   corrected to state what the distribution actually ships — measured: **three console aliases, all →
   `argus.cli:main`, and zero command assets in the wheel** — and the seven `/audit …` commands are
   **marked as forthcoming with their story reference (Story 12.7 / FR35)**, not removed.
2. A test asserts the documented-but-undelivered set is **marked**, so the docs never describe a
   capability the artifact lacks; it goes RED if a command is documented as available while
   `pyproject.toml` ships no mechanism for it. 12.7 removes the marker when it delivers.
3. `CHANGELOG.md` gains one new `### …` section recording the consumer-visible fixes, registered
   deliberately in `_NOTE_SECTIONS` with a stated ordering reason. **No existing section is demoted or
   reordered.** The **fifth-consecutive-edit** fact (§0.6, `DF-11-4-D`) is stated in the completion
   notes.

### AC6 — The 21 "Minions" claims are classified one by one, and the two user-facing ones are corrected

1. Every occurrence of the bare word is **read and classified** true-historical (keep) or
   false-subject-claim (rewrite). **No blanket replace.** The classification is recorded per site with
   its reason.
2. 🔑 `argus/verdict/negative_assurance.py:174` and `:183` are corrected: *"the Minions dogfood corpus"*
   is a **false subject** — the corpus is Argus's own self-audit of this repository, as the same
   sentence says four words later. The **single-sourced** copies at `README.md:10` and
   `CHANGELOG.md:52` are updated in the **same change**, and `tests/test_instrument_disclosure.py`'s
   comparison passes without weakening. Status semantics, the `InstrumentStatus` vocabulary and the
   removal condition (Epic 13) are **unchanged**.
3. A closure re-derives the occurrence set from the tree — the list in §A.3 is context, never the
   contract — and the guard goes RED if a **new** bare-word subject claim appears in `argus/**`
   without being classified.
4. Unit-2 occurrences (`deep_audit.py`, `budget_governor.py`, `proof_run.py`, `bundle.py`,
   `partitioner.py`) are rewritten **in place with zero net line change**, or **left and filed** with
   a reason. Budget beats prose.

### AC7 — Fences, budget, gates, and the one permitted red

1. `git ls-files -- argus` = **72** before *and* after `git add`. **No `A ` line under `argus/`.**
2. Dogfood budget re-measured by executing `build_full_repo_plan('.')` **after staging**: unit 2 ≤
   **15000** and **all three partition_ids byte-unchanged** (`477ef77d7b65` / `82a3d605e61e` /
   `ed6d08f25ce3`). Record the exact consumed/remaining figures. **⛔ If it does not hold: HALT and
   escalate. Do NOT regenerate any dogfood artifact.**
3. `argus/pipeline.py` and `argus/verdict/verdict_gate.py` **byte-unchanged** (sha256 quoted).
4. Full suite re-run with `--junit-xml`: **exactly one** failure, and it is
   `tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed`
   (`DF-11-1-A`), carved out **by node id**. **Any second red is yours.** `mypy` clean on **72** source
   files. `bandit` 0 High / 0 Medium.
5. `python -m argus.cli audit .` re-run and compared **field by field**: `verdict=RELEASE_READY`,
   `blocking_findings=0`, `assessed_deep_ratio=61/77`, `scope=application`, **exit 0** unchanged. Any
   movement in `deep_ratio` / `held_out` is **+1 per new test file** and **arithmetically explained**.
6. **NOTHING PUBLISHED.** `git tag -l` still empty; `origin/master` unmoved; no release, no dispatch,
   no upload. Built `dist/` artifacts are deleted or ignored, never committed.
7. **CI evidence: NOT ESTABLISHED** — write that phrase. Every figure is LOCAL Windows / CPython
   3.11.15 under AI-E10-1.
8. `deferred-work.md` is appended **append-only** (verified programmatically, `-0` removals):
   `DF-9-2-A` **CLOSED** with the freshly-built-wheel measurement attached; `DF-9-2-B` closed or
   partially closed with the per-site classification; anything you decline is **filed with an owner**,
   never dropped.

---

### §F. Write set — exactly this, nothing else

**Modify (existing files only):**

- `argus/precision/replay_harness.py` — the lazy registry resolution + the stale-claim corrections
  (unit 2, **≤13 lines**, measured minimum **+8**)
- `argus/verdict/negative_assurance.py` — the two disclosure constants (unit 3, free)
- up to five unit-2 modules and up to nine unit-1/unit-3 modules for AC6, per the §A.3 table
- `tests/test_release_preflight.py` — `_NOT_IMPORTABLE_FROM_DISTRIBUTION`, and `-11` narrowed or
  replaced with its docstring corrected
- `tests/test_release_surface_honesty.py` — one `_NOTE_SECTIONS` entry (the **fifth** edit, §0.6)
- `README.md`, `CHANGELOG.md` — AC3 / AC4 / AC5 corrections and the new note section
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — append-only
- **THIS story file** — Dev Agent Record, and `git add` it

**Add (tests only — outside the audited population):**

- one new test module for the built-artifact guard (AC1/AC2/AC3/AC4/AC5), or additions to
  `tests/test_release_preflight.py` if that reads better

**Do not touch:** `argus/pipeline.py`, `argus/verdict/verdict_gate.py`, `action.yml`,
`.github/workflows/**`, any `minions-dogfood-*.md`, `epics.md`, `prd.md`, `architecture.md`, and every
inherited-dirty path named in the frontmatter.

---

## Tasks / Subtasks

- [x] **T1 — Re-derive the baseline before writing a byte** (AC7): full suite `--junit-xml`, `mypy`,
      `git ls-files -- argus`, `git tag -l`, `build_full_repo_plan('.')`, `argus audit .`, and the
      wheel-import probe **against the unfixed tree** (expect 67/72, 5 fail). Quote every figure.
- [x] **T2 — Write the built-artifact guard FIRST and prove it RED** (AC1.3, AC2.1, AC2.4): build,
      probe, assert `argus.__file__` lands in the extraction dir, watch it fail naming the five
      modules.
- [x] **T3 — Make the registry import lazy** (AC1.1, AC1.4, §B): implement, then **immediately**
      re-measure unit 2 and all three partition_ids. **HALT if > +13.**
- [x] **T4 — Correct the module's own stale claims in place** (§C.1, §C.3): the AR8 purity line, the
      two wrong `tests/argus/…` paths. Zero added lines.
- [x] **T5 — Retire or narrow the vacuous guard** (AC2.2, AC2.3): update
      `_NOT_IMPORTABLE_FROM_DISTRIBUTION`; state in the docstring what a source-tree walk can and
      cannot see.
- [x] **T6 — Assert the documents** (AC3): correct the three sites, correct the false "cannot drift"
      sentence, and add the test that asserts documents against the live measurement in both
      directions.
- [x] **T7 — Mechanise the tag disclosure** (AC4) and **mark the slash commands forthcoming** (AC5.1,
      AC5.2).
- [x] **T8 — Classify all 21 "Minions" occurrences** (AC6): closure first, then the two user-facing
      corrections plus their `README.md:10` / `CHANGELOG.md:52` copies; unit-2 sites in place at zero
      net lines or filed.
- [x] **T9 — CHANGELOG section + `_NOTE_SECTIONS` registration** (AC5.3), stating the ordering reason
      and recording the fifth-edit fact.
- [x] **T10 — Re-run every gate after `git add`** (AC7): fence, budget + three ids, suite (one red,
      by node id), `mypy`, `bandit`, `argus audit .` field-by-field, `git tag -l` empty. Delete the
      built `dist/`.
- [x] **T11 — Ledger** (AC7.8): close `DF-9-2-A` with the freshly-built-wheel measurement; record
      `DF-9-2-B`'s disposition; file anything declined with an owner; verify append-only
      programmatically.
- [x] **T12 — Completion notes**: the fifth `_NOTE_SECTIONS` edit, the AI-E10-4 / `DF-10-2-A` still-open
      restatement, "CI evidence: NOT ESTABLISHED", and "nothing published".

### Review Findings

**Adversarial code review, 2026-08-12 — every headline claim independently re-derived on disk, not
transcribed from the story.** Method: `git diff HEAD` per file, a from-scratch wheel build + import
probe script written independently of `tests/test_built_distribution.py`, `build_full_repo_plan('.')`
re-executed, `pytest --junit-xml`, `mypy`, `bandit`, `python -m argus.cli audit .`, and `sha256sum` on
every byte-fenced file — all against the actual working tree, not the story's tables.

- [x] **[Review][Verified]** The guard inspects the BUILT artifact and is not vacuous. Read
  `tests/test_built_distribution.py` in full: `_build_distribution()` runs a real `python -m build
  --no-isolation` subprocess into a `tempfile.mkdtemp()` outside the repo; the probe prelude strips the
  repo root from `sys.path` by normalised absolute path and REFUSES with `PROBE-INVALID` unless
  `argus.__file__` resolves inside the extraction dir (`-21` is the positive control, proven by
  deliberately prepending the repo root and observing refusal); `-23` injects a module-level `import
  _registry` into the *extracted* tree and proves RED then green; `-24` proves the missing-tool path
  returns a named `Unevaluable` and never passes silently, and additionally asserts the guard is
  *evaluable in this environment* so skip can never become the normal path. Ran `tests/test_built_distribution.py` standalone: 10/10 pass in ~5s.
- [x] **[Review][Verified]** Re-derived the 67-of-72 and 72-of-72 figures myself, independently of the
  story's own guard: wrote a standalone build+probe script, ran it against the current tree (72/72,
  0 fail), then temporarily swapped `argus/precision/replay_harness.py` for the `git show HEAD:` version,
  rebuilt, and reproduced **67 of 72, 5 fail**, naming the exact same five modules with
  `ModuleNotFoundError: No module named '_registry'`. Restored the fixed file afterward; sha256
  `03d20940a5dce73ebca85a2b0768c51093737957f4f1253c89eb2a76d515d5b6` matches the pre-experiment byte
  state exactly (`git status --porcelain` shows only the pre-existing `M ` for it, no new diff).
- [x] **[Review][Verified]** LOC cliff re-derived by executing `build_full_repo_plan('.')` on the
  current staged tree: `477ef77d7b65` 1330/21 · `82a3d605e61e` **14997**/39 · `ed6d08f25ce3` 4127/12,
  `source_file_count=72`, `total_loc=20454` — all three ids and both LOC figures match the story's
  table exactly (+10 of 13, 3 remaining). No PEP-562 `__getattr__` present anywhere in the diff; the
  shipped shape is the plain lazy-import function described in §A.1.
- [x] **[Review][Verified]** Figure self-maintenance is real, not re-pinned: `TC-ArgusAgent-DOCS-001-54`
  re-derives every published figure from a freshly built wheel/sdist at test time via
  `_live_figures()`/regex, in both directions (stale-document and deleted-sentence failure modes both
  covered) — confirmed by reading the assertions, not just their names.
- [x] **[Review][Verified]** AC4/AC5 mechanised both ways: `-55` computes real `git tag --list v*` and
  flips the required assertion direction on tag existence (three caveat spellings, the third one — the
  README `pyproject.toml` block's "⚠️ Unresolvable" — genuinely found by the closure per the dev's own
  account); `-56` flips on `dist.data_assets` (measured empty today) and would go red the day a data
  asset ships without the marker being removed, or the marker survives after one ships.
  `tests/test_release_preflight.py`'s narrowing of `-11` was read in full: `_NOT_IMPORTABLE_FROM_DISTRIBUTION`
  is now `frozenset()` and is **imported** (not copied) into `test_built_distribution.py`, so there is
  exactly one place the figure can rot. `-11` itself still runs and still asserts a (different, disjoint)
  claim — it did not become a no-op.
- [x] **[Review][Verified]** Nothing published: `git tag -l` empty, `HEAD` unmoved at `93adc94`, the
  pre-existing `dist/` wheel+sdist are dated 2026-08-08 22:59 (untouched), `git ls-files -- argus` = 72
  with `git status --porcelain -- argus` showing zero `A ` lines.
- [x] **[Review][Verified]** Test ledger: independently ran the full suite with `--junit-xml`:
  `tests="1405" errors="0" failures="1"`, the sole failure is
  `test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed` (`DF-11-1-A`) — no second red.
  `mypy argus`: clean, 72 source files. `bandit -r argus`: 0 High / 0 Medium / 19 Low. `sha256sum` on
  `argus/pipeline.py`, `argus/verdict/verdict_gate.py`, `argus/dogfood/proof_run.py` all matched the
  story's quoted hashes exactly (byte-unchanged). `python -m argus.cli audit .` reproduced
  `verdict=RELEASE_READY deep_ratio=61/169 blocking_findings=0 assessed_deep_ratio=61/77
  scope=application held_out=92`, exit 0, verbatim. The narrowing of `-11` genuinely **relocated**
  coverage rather than gutting it: the distribution-import claim now lives in `-20` (which the old
  guard could never make), and `-11`'s own (narrower, honestly labelled) claim about which modules
  name `_registry` in source is still asserted and still wired to `-12`'s consumer-surface check.
- [x] **[Review][Verified]** `tests/test_precision_replay.py` and `tests/test_dogfood_plan.py` are
  byte-identical to `HEAD` (`git diff` empty) — zero assertion changes, as AC1.5 requires.
  `argus/precision/__init__.py` is untouched. `action.yml` carries only the SHORT disclosure form
  (no "dogfood corpus" phrase), so it needed no AC6.2 edit and the fence held.
- [x] **[Review][Judgment — DF-11-4-D, for the Epic-11 retrospective]** The `_NOTE_SECTIONS` registry
  is on its fifth consecutive story edit. Read all five comment blocks in
  `tests/test_release_surface_honesty.py`: each edit still does genuine comparative reasoning about
  placement (11.5's own comment explicitly considers and declines promotion above 11.3 with a stated
  reason), so this is **not yet a rubber stamp** — the ordering decisions are substantive, not
  ritual. The concern for the retro is cost, not correctness: each edit now requires an
  ever-longer prose justification referencing every prior entry, which is a rising maintenance tax
  on a file whose job is a release-note ordering guarantee. Recommend the retro decide whether a
  lighter-weight ordering mechanism (e.g. a numeric priority field per entry) should replace the
  narrative-comment convention before a sixth story adds to it.
- [x] **[Review][Low — informational, no action required]** `precision_gate_status_for`'s own
  `floor_n is None` fallback (`argus/precision/replay_harness.py`) calls `_registry_module()` a second
  time, independently of `compute_precision`'s resolution, to keep the function safe if ever called
  directly. DN-2 measured zero such direct callers today, so this is currently a defensive branch with
  no exerciser. Acceptable: removing it would only save one branch and would make the public function
  crash instead of self-resolving if a future caller ever does invoke it directly with `floor_n=None`.
  No fix requested.

**Verdict: PASS.** No unresolved decision-needed or patch findings; no High/Medium issues found; all
ACs independently reproduced; tests/mypy/bandit green with the one pre-existing, correctly carved-out
red. `-> done`.

---

## Dev Notes

### LOCKED decisions taken at story design — record these, do not re-litigate

- **DN-1 — The fix is a lazy `_registry_module()` helper, not a redesign of `compute_precision`'s
  contract.** A cleaner AR8-pure design exists (make `registry` a required argument and push the
  import entirely into the test-harness shell), but it changes a frozen Epic-6 signature and breaks
  eight existing call sites for no gain the consumer can see. **Rationale (project context beats
  generic best practice):** §3.3/AR7 forbid a second mechanism where one exists, and the epic's own
  close condition is *"make the import lazy or optional"* — not "re-architect the harness". Measured
  cost of the chosen shape: **+8 of 13**.
- **DN-2 — `VALIDATION_SET_FLOOR_N` leaves `replay_harness.__all__`.** Measured: **zero** importers
  anywhere in `argus/**`, `tests/**` or `scripts/**` take it from this module; `tests/` imports it
  from `_registry` directly. Keeping the re-export would cost a PEP-562 `__getattr__` block (+9 lines,
  taking the total to +17 and **over the cliff**, measured). The constant itself is untouched and is
  still read from `_registry` at every use — **no fork**.
- **DN-3 — `precision_gate_status_for` gains keyword-only `floor_n: int | None = None`.** This keeps
  `argus/dogfood/proof_run.py:642` byte-unchanged (it is in unit 2). When `None`, the floor resolves
  lazily — so the dogfood proof generator's behaviour from a wheel is *unchanged* (it still needs the
  repository), and nothing regresses.
- **DN-4 — The AR8 purity claim is corrected, not defended.** See §C.1. Recorded as a deviation with
  its rationale because this is a story about modules that say only true things.
- **DN-5 — The replacement guard must inspect a BUILT artifact.** Non-negotiable, and the reason is
  measured, not theoretical (§A.2). A source-tree import-graph walk is vacuous by construction for a
  claim about the distribution.
- **DN-6 — The "Minions" sweep is budget-fenced, not scope-fenced.** Units 1 and 3 are free; unit 2 is
  in-place-or-filed. Prose quality never wins over the partition-id fence.
- **DN-7 — `DF-10-2-A` is ruled OUT** despite AI-E10-4 naming 11.5 as a candidate home. Reason in §D.
  It is restated as OPEN for the Epic-11 retrospective rather than silently absorbed.
- **DN-8 — The two README items the epic calls falsehoods are already fixed** (§0.3). Re-fixing them
  would be a fabricated finding. AC4 mechanises the one that can rot again.
- **DN-9 — `DF-11-1-A` stays open and carved out by node id**, fifth consecutive story. Closing it
  would require amending a signed retrospective from inside Epic 11 to make a test pass.

### Architecture patterns & constraints a reviewer will check

- **AR7 / §3.3 — no second mechanism, no forked constant.** Every registry value still comes from
  `_registry`.
- **AR8 / Pure-Impure master rule** — pure modules take no I/O; the impure shell sits at the edges.
  The lazy helper *is* the declared edge, and the docstring must say so.
- **NFR-M1 ≤1200 lines per module** — `replay_harness.py` goes 381 → ~389; no risk.
- **AR10 / NFR-R1 — failure becomes a typed, named outcome, never a bare raise or a silent skip.**
  Applies to the guard's "build unavailable" path (AC2.5).
- **NFR-S1** — no source or secret byte crosses any surface; the golden key is value-free, which is
  why importing the registry leaks nothing.
- **§H evidence-citation rule** — a status claim carries an executed-gate citation (run id **plus**
  the sha it covers) or the literal **NOT ESTABLISHED** marker. You have no CI run. Write the marker.
- **Enforcement / AI-E10-5** — where an AC names a set of sites, causes or requirements, the committed
  guard closes over the **live source of that set** and fails on an unenumerated member.

### Testing standards — the house form

- Area `ArgusAgent-RELEASE` (`TC-ArgusAgent-RELEASE-001-NN`, continuing from `-19`) for artifact
  guards; area `ArgusAgent-DOCS` (`TC-ArgusAgent-DOCS-001-NN`) for document-honesty guards. Continue
  the indices; do not restart them.
- **RED-first with the FINAL test code**, then green, and say which control you used. A guard that was
  never observed failing is not evidence.
- **Closures, not lists** (AI-E10-5). Both directions: grow **and** shrink.
- No network, no LLM, no `.argus/` write from a guard, no new dependency.

### Previous story intelligence (11.1–11.4, 10.4, 9.2)

- **11.1** wrote the FR34 disclosure into `negative_assurance.py` beside `DISCLAIMER`, with a
  glob-resolved surface registry and an `ast` walk of `generate_reports`. Its `DN-3` pinned
  `replay_harness` **off** every user-facing import path and named it *"Story 11.5's wheel defect"*
  verbatim in `TC-ArgusAgent-DOCS-001-45`. **That test must still pass** — your fix makes the module
  safe to import, it does not make it appropriate to import from `argus.cli`.
- **11.2** proved a "latent, zero-instance" ledger item was release-blocking on the *public* audience
  and delivered its ACs as closures over the real tables. Its review's one finding was a **prose
  count** that was wrong — the same class as AC3 here.
- **11.3** failed review iteration 1 for a guard blind to an ordinary YAML shape, and the fix turned
  out to be **wider** than reported (nine spellings, not one). Assume your first guard is narrower
  than you think; construct adversarial cases the implementation did not generate.
- **11.4** measured the LOC cliff by perturbing the LOC map, put its pure contract in unit 3 and its
  impure probe in unit 2, and kept `pipeline.py`/`verdict_gate.py` byte-unchanged. Same discipline
  applies here.
- **10.4** hit `DF-10-4-D` head-on, **HALTed**, and the operator resolved it by committing and
  regenerating at a truthful sha. **You do not have that option** — the remedy is 12.1's. HALT
  instead.
- **9.2** is where all of this originates: it built the artifact, discovered the import defect from
  the built wheel (*"a defect no source-tree test could see"* — its own words at
  `tests/test_release_preflight.py:221`), fenced `argus/precision/**`, and filed `DF-9-2-A` and
  `DF-9-2-B`. **It already told you the source tree cannot see this.** The guard it left behind
  forgot.

### Runtime & toolchain, verified on this machine 2026-08-12

CPython **3.11.15**, Windows. `flit_core >=3.2,<4` build backend; `python -m build` present and working
(it produced both artifacts during the §A.1 experiment). `pydantic>=2`, `jsonschema`, `radon`, `httpx`,
`tree-sitter 0.25.x`, `tree-sitter-python 0.25.x`. `.venv` carries an **editable** install
(`argus.pth`) — see §A.5's trap.

### Latest external technical facts (checked 2026-08-12)

- **PEP 562 module `__getattr__`** is the standard lazy-attribute mechanism (Python ≥3.7). It was
  measured and **rejected on budget**, not on correctness (DN-2).
- **Wheel/sdist inspection** needs no dependency: `zipfile` and `tarfile` are stdlib, and reading
  archive members is the only way to assert what actually ships.
- **flit** packages `[tool.flit.module] name = "argus"` and nothing else — confirmed by the built
  artifacts (77 wheel entries, 76 sdist members, no `tests/`). Any claim about "what the distribution
  contains" is therefore checkable locally, with no index and no publish.

### Project structure notes

`argus/precision/` is a two-module package (`__init__.py`, `replay_harness.py`); `__init__.py`
re-exports six names and is the reason the breakage is transitive. `argus/dogfood/` holds the
self-audit proof generator, which is **not** a consumer feature — README already states that split and
that framing must survive your edits.

### Open questions for the operator — saved for the end, as the workflow requires

1. **`DF-10-2-A` still has no home.** AI-E10-4 offered "(11.5), or a dated V2 decision"; this story
   rules it out with reasons (§D, DN-7). **Epic 11 closes after this story with it still open.** A
   dated decision is needed.
2. **`DF-11-4-D` reaches five consecutive `_NOTE_SECTIONS` edits here** (§0.6). The Epic-11 checkpoint
   review this story triggers should look at that file's edit history.
3. **`DF-9-2-C`** (three tracked `.pyc` files) is deliberately left because `git rm --cached` trips
   `DF-10-4-D`. It is a one-line fix for whoever owns 12.1.
4. **The instrument disclosure's wording change (AC6.2) is consumer-visible text.** It is a *subject*
   correction, not a *claim* change, and 11.1's guard enforces consistency across four surfaces — but
   an operator may want to read the final sentence before it is published by 12.9.

### References

- [Source: `_bmad-output/design-artifacts/ArgusAgent/epics.md#Story 11.5` (L2128-2151) and
  `#Epic 11` (L1966-1987)]
- [Source: `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — `DF-9-2-A` (L1155-1196),
  `DF-9-2-B` (L1198-1218), `DF-9-2-C` (L1220-1234), `DF-10-4-D` (L1942-1983), `DF-11-1-A` (L2235-2255),
  `DF-11-4-D` (L2598-2611)]
- [Source: `_bmad-output/design-artifacts/ArgusAgent/architecture.md#I. Packaging & Deployment` (L554+),
  `#Pure/Impure Separation` (L681+), `#Reuse / Import Patterns` (L726+), `#Enforcement` (L750+)]
- [Source: `_bmad-output/design-artifacts/ArgusAgent/epic-9-retro-2026-08-09.md` — learning on forked
  figures (L142) and `AI-E9-4` (L208)]
- [Source: `_bmad-output/design-artifacts/ArgusAgent/epic-10-retro-2026-08-11.md` — `AI-E10-1`,
  `AI-E10-2`, `AI-E10-3`, `AI-E10-4`, `AI-E10-5`]
- [Source: `argus/precision/replay_harness.py:86-96` — the defect; `:17` — the AR8 claim]
- [Source: `argus/verdict/negative_assurance.py:165-186` — the single-sourced disclosure constants]
- [Source: `tests/test_release_preflight.py:218-368` — the Story-9.2 measurement block and the
  source-tree guard proven vacuous in §A.2]
- [Source: `tests/test_instrument_disclosure.py:455-481` — 11.1's `DN-3` pin naming this story's defect]
- [Source: `README.md:140-168, 189-215`; `CHANGELOG.md:394-407`; `pyproject.toml:73-76`]

---

## Dev Agent Record

### Context Reference

This story file, in full. Every §0–§F figure was **re-derived by execution on this tree** before a
byte was written; none was transcribed. Where a re-derivation disagreed with the story it is called
out below (it agreed everywhere except one omission I found and one figure I had to widen).

### Agent Model Used

`claude-opus-5[1m]` (BMAD `dev-story`, single pass, `mode=implement`).

### Debug Log References

**All figures are LOCAL, Windows / CPython 3.11.15**, under the dated risk acceptance carried forward
from Story 11.1 §0.1 (AI-E10-1, 2026-08-11, XAgent007). **CI evidence: NOT ESTABLISHED** — no CI run
has executed a line of this delta. **Nothing was published:** no push, no tag, no release, no
`workflow_dispatch`, no index upload; `git tag -l` is empty before and after; `origin/master` did not
move.

#### T1 — baseline, re-derived by execution (2026-08-12)

| gate | measured | matches §A.5? |
|---|---|---|
| full suite (`--junit-xml`) | **1395 collected / 1394 passed / 1 failed / 0 errors / 0 skipped**, 146.0 s; the one red is `DF-11-1-A` | ✅ |
| `mypy argus` | clean, **72** source files | ✅ |
| `bandit -r argus` | **0 High / 0 Medium / 19 Low**, 16 323 LOC | ✅ |
| `git ls-files -- argus` / `git tag -l` | **72** / **empty** | ✅ |
| `build_full_repo_plan('.')` | `477ef77d7b65` 1330/21 · `82a3d605e61e` **14987**/39 · `ed6d08f25ce3` 4116/12; `source_file_count` 72, `total_loc` 20433 | ✅ |
| `python -m argus.cli audit .` | `verdict=RELEASE_READY deep_ratio=61/168 blocking_findings=0 assessed_deep_ratio=61/77 scope=application held_out=91`, **exit 0** | ✅ |
| built wheel / sdist | `argus_agent-0.1.0-py3-none-any.whl` **77 entries = 72 `.py` + 5 `dist-info`**; `argus_agent-0.1.0.tar.gz` **76 members**, **no `tests/`** | ✅ |
| wheel-import probe, **unfixed tree** | **67 of 72 import, 5 fail**, all `ModuleNotFoundError: No module named '_registry'`, exactly the five named modules | ✅ |
| `sha256` | `pipeline.py` `05232b51…`, `verdict_gate.py` `d9dd1cb2…`, `replay_harness.py` `be468fdf…` (matches the SM's round-trip hash), `proof_run.py` `5bc4fcea…` | ✅ |

The §A.5 **measurement trap was real and was avoided**: `.venv/Lib/site-packages/argus.pth` contains
`D:\ProjectX\XAgents\XAgents\ArgusAgent`, so the repository is on `sys.path` of every interpreter this
venv starts. The committed probe removes it by normalised absolute path, prepends the wheel extraction
directory, runs from a `cwd` outside the repository with `PYTHONPATH` stripped, and **exits
`PROBE-INVALID` unless `argus.__file__` resolves inside the extraction directory**.
`TC-ArgusAgent-RELEASE-001-21` is the positive control for that refusal, and it is not decorative: it
prepends the repository root deliberately and asserts the probe REFUSES rather than reporting the
false *72 of 72* that cost the SM a cycle.

#### T2 — RED-first, with the FINAL guard code

`tests/test_built_distribution.py` and both `tests/test_release_preflight.py` edits were written and
committed to disk **before** `argus/precision/replay_harness.py` was touched, then run against the
unfixed tree. **8 of the 10 new tests went RED**, and `-20`'s failure message named the five modules
and the real exception:

> `expected [], measured [('argus/dogfood/proof_render.py', "ModuleNotFoundError: No module named
> '_registry'"), ('argus/dogfood/proof_run.py', …), ('argus/dogfood/proof_types.py', …),
> ('argus/precision/__init__.py', …), ('argus/precision/replay_harness.py', …)]`

`-22` (sdist ships no `tests/`) and `-24` (missing-tooling is named, never silent) were GREEN from the
start, correctly — neither describes a defect this story introduced. Saying so is the honest form; a
guard reported as "RED-first" when it never could have been red is the thing §E.1 warns about.

**The `ast`-walk guard's vacuity was reproduced, not taken on trust.**
`TC-ArgusAgent-RELEASE-001-11` was **green before the fix and green after it**, across a wheel that
went from 5 failing modules to 0. It is narrowed (not deleted) and its docstring now states what it
can and cannot see; `_NOT_IMPORTABLE_FROM_DISTRIBUTION` is measured **empty** and is asserted by `-20`,
which is the only guard in this suite that can observe it.

#### T3/T4 — the unit-2 budget, re-measured after `git add`

| | lines | unit 2 | ids |
|---|---|---|---|
| before | `replay_harness.py` 381 | 14987 | `477ef77d7b65` / `82a3d605e61e` / `ed6d08f25ce3` |
| after the lazy fix (T3) | 389 | 14995 | **all three byte-unchanged** |
| after the in-place claim corrections (T4) | **391** | **14997 / 15000** | **all three byte-unchanged** |

**+10 physical lines of the 13 available; 3 remaining.** Re-measured **after** `git add`:
`477ef77d7b65` 1330/21 · `82a3d605e61e` **14997**/39 · `ed6d08f25ce3` 4127/12, `source_file_count` 72,
`total_loc` 20454. Unit 3 absorbed the `negative_assurance.py` correction record (4116 → 4127) with its
id unchanged, exactly as §0.2b measured. **No dogfood artifact was regenerated.**

The `+2` over the SM's measured `+8` is T4, and it was a deliberate spend: §C.1 requires the AR8 purity
claim to be **corrected**, not defended, and the corrected sentence does not fit in the line it
replaces. It cost `+1` in the module header and `+1` in `compute_precision`'s docstring. The two wrong
`tests/argus/…` paths (§C.3) and `PrecisionResult`'s purity line cost **0** — reflowed in place.

#### T10 — every gate, after staging

| gate | baseline | after | verdict |
|---|---|---|---|
| `git ls-files -- argus` | 72 | **72**, and `git status --porcelain -- argus` shows **no `A ` line** | ✅ fence holds |
| unit-2 LOC / three ids | 14987 / three ids | **14997**, **all three ids byte-unchanged** | ✅ |
| `mypy argus` | clean 72 | **clean 72** | ✅ |
| `bandit -r argus` | 0H/0M/19L | **0 High / 0 Medium / 19 Low** | ✅ |
| `argus audit .` | `61/168`, `held_out=91` | `verdict=RELEASE_READY deep_ratio=**61/169** blocking_findings=0 assessed_deep_ratio=**61/77** scope=application held_out=**92**`, **exit 0** | ✅ movement explained below |
| `argus/pipeline.py` | `05232b5133e79b0f252bce452868f0db8a1e49aa205302e58d0a4cf75eb06baa` | **identical** | ✅ byte-unchanged |
| `argus/verdict/verdict_gate.py` | `d9dd1cb2e88123cf2ed1eb2836dba3db2a8861d9361a6a0e261ec7390a5ced13` | **identical** | ✅ byte-unchanged |
| `argus/dogfood/proof_run.py` | `5bc4fceac15573969d79a3d983953b2c0e701312c7bb45a79fad328e35312d26` | **identical** | ✅ AC1.5 |
| `git tag -l` | empty | **empty** | ✅ nothing published |

**`deep_ratio` / `held_out` arithmetic (AC7.5).** `deep_ratio` 61/168 → 61/169 and `held_out` 91 → 92
— **+1 each, and exactly one new test file was added** (`tests/test_built_distribution.py`). Numerator
61 and `assessed_deep_ratio` 61/77 are unchanged because the new file is a test file: it is held out of
the `application` scope, so it enters the whole-repository denominator and the held-out count and
nothing else. This is the measured 11.2 precedent (165→166 / 88→89) reproduced exactly.

**Built artifacts.** The wheel and sdist were built with `python -m build --no-isolation --outdir
<tempdir>` into a directory **outside the repository** (and, in the committed guard, into
`tempfile.mkdtemp()`); `--no-isolation` deliberately, because isolation would make a test reach the
network. The repository's `dist/` directory is **pre-existing** (dated 2026-08-08, Story 9.2),
git-ignored by `.gitignore:24` and untracked; it was **not created, refreshed or committed** by this
story and was left exactly as found, per the frontmatter's "do not tidy inherited state".

### Completion Notes List

1. **`DF-9-2-A` is CLOSED, and its stated close condition was FALSE.** The condition promised that
   updating `_NOT_IMPORTABLE_FROM_DISTRIBUTION` was safe because `TC-ArgusAgent-RELEASE-001-11` pinned
   it "in BOTH directions, so a fix that leaves the record stale goes RED". Reproduced here: `-11`
   walks the **source tree** with `ast`, an `import _registry` inside a function body is the same AST
   node as one at module level, and `-11` **stayed green across the entire fix**. It would have stayed
   green with the record left stale, and it stayed green while the published figures rotted from
   "66 of the 71" to a measured 67 of 72 over two epics. The correction is recorded in the ledger
   rather than quietly satisfied.
2. **The replacement guard inspects the BUILT artifact.** `TC-ArgusAgent-RELEASE-001-20` builds a real
   wheel and sdist, closes over the **archive members** (never a hand list — AI-E10-5), and imports
   every shipped module in a clean subprocess with the repository off `sys.path`: **72 of 72 import,
   0 fail**. Three controls sit beside it so it cannot decay into decoration: `-21` proves the probe
   refuses when it cannot prove provenance, `-23` injects a module-level `import _registry` into the
   *built* tree and proves the guard goes RED then green again, and `-24` proves a missing build
   front-end yields a named `release_preflight.Unevaluable` and a skip, never a silent pass.
3. **🔴 THIS IS THE FIFTH CONSECUTIVE EDIT TO `_NOTE_SECTIONS`** (11.1, 11.2, 11.3, 11.4, **11.5**),
   filed as `DF-11-4-D`. Stated plainly here, as §0.6 requires, so the Epic-11 retrospective has an
   honest count rather than one it has to reconstruct. The edit is a **pure zero-deletion insertion**:
   no existing section moved relative to any other and none was demoted. It is registered **fifth**,
   and the ordering reason is written into the registry comment as the registry itself demands —
   including the promotion above 11.3's security entry that was **considered and declined** (a
   security fix on an executable surface outranks a packaging fix on a non-consumer module surface).
   **The Epic-11 checkpoint should read that file's edit history**; a registry widened by five
   consecutive stories to fit whatever each needed to say is one unexamined edit from decorative.
4. **`AI-E10-4` / `DF-10-2-A` remain OPEN and unowned.** `AI-E10-4` named 11.5 as a candidate home;
   this story rules it out (DN-7, §D) and **restates it as open** in the ledger rather than absorbing
   it silently. **Epic 11 closes after this story with it still needing a dated decision.**
5. **The unit-2 budget is down to 3 lines** (`DF-11-5-A`, opened). The next story that writes more
   than 3 physical lines into any unit-2 module cannot proceed without Story 12.1's remedy.
6. **AC6 was a classification, not a sweep.** All 21 bare-word occurrences were re-derived by regex
   over `git ls-files -- argus` and read one by one: **19 true-historical (kept), 2 false-subject
   (rewritten)**. Every unit-2 site classified as KEEP, so AC6.4 cost **zero lines** — and that is the
   honest outcome, not a budget dodge: each unit-2 occurrence is an AR7 provenance citation or a
   negative boundary claim, and rewriting them would have made the modules less true. The two
   rewritten ones are the FR34 disclosures printed on `stderr` by every `argus audit` run. Their
   single-sourced copies at `README.md:10` and `CHANGELOG.md:52` were updated in the same change and
   `tests/test_instrument_disclosure.py` passes without weakening.
7. **§0.3 was verified before it was trusted, and it was right.** The two README items the epic calls
   falsehoods **are already fixed on this tree** — the ⚠️ tag block at `README.md:51-57` and the
   `argus audit .` correction — and were **not re-fixed**. The module-count premise was stale in both
   numerator and denominator, as §0.3 said: 67 of 72, not 5 of 71.
8. **CI evidence: NOT ESTABLISHED.** Every figure above is LOCAL, Windows / CPython 3.11.15.
9. **Nothing is published.** No push, tag, release, dispatch or index upload; `git tag -l` empty;
   `origin/master` unmoved; no build artifact added to the repository.

#### Decisions taken under domain authority, with their tradeoffs

- **`_NOT_IMPORTABLE_FROM_DISTRIBUTION` stayed at its Story-9.2 address and is IMPORTED by the new
  guard** rather than copied into it. §F puts the constant in `tests/test_release_preflight.py`; the
  measurement can only happen in `tests/test_built_distribution.py`. Copying it would have created a
  second copy of a pinned figure — the exact fork class Epic 9's retrospective named and this
  repository has now rotted twice. **Tradeoff:** one test module now imports another, which is a
  coupling I would normally avoid. Chosen because one source of truth beats module independence for a
  figure whose whole defect history is duplication.
- **The guard reuses `release_preflight`'s vocabulary instead of forking a second notion of "the built
  distribution"** (§C.8 / AR7): `check_e6_incomplete_build` decides "both artifacts or none" over the
  real file names, and `Unevaluable("E6", …)` carries the could-not-build outcome. No second build
  invocation was added to any workflow, and no workflow was edited.
- **`VALIDATION_SET_FLOOR_N` left `replay_harness.__all__`** (DN-2, re-verified by execution): grep
  across `argus/**`, `tests/**` and `scripts/**` found **zero** importers of it from this module —
  `tests/test_precision_replay.py:65` takes it from `_registry` directly. The PEP-562 variant that
  preserves the re-export measures `+17`, over the 13-line cliff, and was **not revived**. The
  constant itself is untouched and still read from `_registry` at every use — **no fork** (AR7/§3.3).
- **`-11` was narrowed rather than deleted** (AC2.3). It still has one honest job — naming which
  modules mention the repository-only test tree, which `-12` reads to keep that reach off the consumer
  surface — and deleting a guard because it turned out to measure something narrower than its name
  claimed would destroy the evidence of what it could not see.
- **`argus/precision/__init__.py` was not touched**, as §C.9 predicted it should not need to be. It
  was verified importable from the built wheel after the fix.
- **The FORTHCOMING marker is enforced in both directions** rather than being a comment: `-56` fails
  if the marker is removed while the wheel ships no command asset, **and** fails once the wheel ships
  one. Story 12.7 cannot ship without removing it, and nobody can remove it early.

#### Where a re-derivation disagreed with the story context

- **§0.3's tag-disclosure premise was right but incomplete.** AC4's closure over *every* pinned VCS
  install command in `README.md` found a **third** caveat spelling my first registry missed —
  `README.md:67`'s *"⚠️ Unresolvable until `v0.1.0` exists"*, which says the same thing in a different
  word. The guard went RED on it and the marker set was widened to three. This is §E's 11.3 lesson
  reproduced exactly: **the first guard was narrower than I thought**, and the closure is what found it
  rather than review.
- **The `DF-9-2-B` ledger figure (25 / 23) and the epic's (22 across 14) are both stale.** Measured
  **21 across 14**, matching §0.3. §A.3's enumeration was correct site-for-site, including the two
  occurrences that share one line in `argus/audit/deep_audit.py:4`.
- **README carried two stale figures §A.5 did not list**: `README.md:134` said the wheel holds **76**
  entries (77) and the sdist **75** files (76). Both are now asserted by `-54` against the live build,
  so they cannot rot again.

### File List

**Modified — production (`argus/**`):**

- `argus/precision/replay_harness.py` — lazy `_registry_module()`; `registry=None`; keyword-only
  `floor_n=None`; `VALIDATION_SET_FLOOR_N` out of `__all__`; AR8 purity claim corrected in place; the
  two stale `tests/argus/…` paths corrected in place. **381 → 391 lines (+10 of 13, unit 2).**
- `argus/verdict/negative_assurance.py` — the two FR34 disclosure constants' **subject** corrected
  (*"the Minions dogfood corpus"* → *"the Argus dogfood corpus"*), plus the correction record above
  them. Unit 3 (free). No status semantics, vocabulary or removal condition changed.

**Modified — tests:**

- `tests/test_release_preflight.py` — `_NOT_IMPORTABLE_FROM_DISTRIBUTION` measured **empty**;
  `_MODULES_NAMING_THE_TEST_TREE_IMPORT` added for what the `ast` walk can actually see; `-11`
  narrowed and renamed with a docstring stating what it can and cannot see; the Story-9.2 measurement
  block extended with the vacuity finding.
- `tests/test_release_surface_honesty.py` — one `_NOTE_SECTIONS` entry, registered fifth (**the fifth
  consecutive edit**, `DF-11-4-D`), pure insertion, ordering reason stated.

**Added — tests (outside the audited population):**

- `tests/test_built_distribution.py` — `TC-ArgusAgent-RELEASE-001-20`..`-24` and
  `TC-ArgusAgent-DOCS-001-54`..`-58`. The only new file in this story.

**Modified — documents:**

- `README.md` — module figures corrected and now asserted (77 wheel entries, 76 sdist files, **72 of
  72 import**); the false *"pinned in both directions by `-11` … cannot drift from the code"* sentence
  retracted and replaced by the guard that actually holds it; the slash-command claim corrected to
  what the wheel ships and the seven commands marked FORTHCOMING (Story 12.7 / FR35); the disclosure
  copy at `:10` updated.
- `CHANGELOG.md` — one new `### Fixed — five shipped modules could not be imported from the
  distribution at all` section under `## Unreleased`; the `### Packaging` figures corrected and now
  asserted; the disclosure copy at `:52` updated.
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — **append-only**, verified
  programmatically (`git diff --numstat` → `778 0`, **zero deletions**): `DF-9-2-A` CLOSED,
  `DF-9-2-B` PARTIALLY CLOSED, `AI-E10-4`/`DF-10-2-A`/`DF-11-4-D`/`DF-9-2-C` restated OPEN,
  `DF-11-5-A`/`-B`/`-C` opened.
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — `ready-for-dev` → `in-progress` →
  `review`; all comments and the STATUS DEFINITIONS block preserved.
- `_bmad-output/design-artifacts/ArgusAgent/stories/11-5-published-artifact-is-complete-and-true.md` —
  this record; `git add`ed with the delta.

**Untouched, verified:** `argus/pipeline.py`, `argus/verdict/verdict_gate.py`,
`argus/dogfood/proof_run.py` (sha256 quoted above), `argus/precision/__init__.py`, `action.yml`,
`.github/workflows/**`, every `minions-dogfood-*.md`, `epics.md`, `prd.md`, `architecture.md`, and
every inherited-dirty path named in the frontmatter.

---

## Change Log

| Date | Change | By |
|---|---|---|
| 2026-08-12 | **Adversarial code review: PASS. `review` → `done`.** Every headline claim independently re-derived on disk (fresh build+import probe reproducing 67/72 baseline and 72/72 fixed; `build_full_repo_plan('.')` re-run matching all three partition ids and the +10/13 LOC figure; full suite re-run matching 1405/1404/1 with the sole red confirmed as the carved-out `DF-11-1-A`; `mypy`/`bandit`/`argus audit .`/sha256 fences all reproduced verbatim). The built-artifact guard was read in full and confirmed non-vacuous: genuine provenance check, fails-when-wrong control, never-silent-skip control. No High/Medium findings; one Low informational note and one judgment note on `DF-11-4-D` filed under Review Findings for the Epic-11 retrospective. This closes the last story of Epic 11. | Reviewer (bmad-code-review) |
| 2026-08-12 | **Implemented; `in-progress` → `review`.** `DF-9-2-A` **CLOSED**: `argus/precision/replay_harness.py`'s module-level `sys.path.insert` + `from _registry import …` became a lazy `_registry_module()` helper (`registry=None`, keyword-only `floor_n=None`), and a **freshly built wheel** goes from **67 of 72 import / 5 fail** to **72 of 72 / 0 fail**, proven RED-first with the final guard code. **`TC-ArgusAgent-RELEASE-001-11`'s source-tree `ast` walk was reproduced GREEN across the entire fix** — the story's headline finding — so it is narrowed with a docstring stating what it can and cannot see, `_NOT_IMPORTABLE_FROM_DISTRIBUTION` is measured **empty**, and the distribution claim moved to `TC-ArgusAgent-RELEASE-001-20`, which builds the wheel **and** the sdist locally and imports every shipped module out of the built artifact (`-21` provenance control, `-23` fails-when-wrong control, `-24` never-silent control). Published figures corrected **and asserted** against the live build (`-54`): README 76→**77** wheel entries, 75→**76** sdist files, "66 of the 71"→**72 of 72**; CHANGELOG 71→**72** modules. Tag disclosure **mechanised** in both directions (`-55`, which found a third caveat spelling my first registry missed). Slash commands **marked FORTHCOMING** against Story 12.7 / FR35, enforced both ways (`-56`). All **21** bare-word "Minions" occurrences re-derived by closure and classified — **19 kept true-historical, 2 rewritten** (the FR34 disclosures printed on every `argus audit` run), with `README.md:10` / `CHANGELOG.md:52` updated in the same change (`-57`, `-58`). **Budget: +10 of 13 unit-2 lines, unit 2 14987 → 14997/15000, all three partition_ids byte-unchanged; no dogfood artifact regenerated.** `git ls-files -- argus` = **72** before and after `git add`, no `A ` line. Suite **1405 / 1404 passed / 1 failed** — the one red is `DF-11-1-A`, carved out by node id, and there is no second. `mypy` clean **72**; `bandit` **0H/0M/19L**; `argus audit .` `RELEASE_READY`, `blocking_findings=0`, `assessed_deep_ratio=61/77`, exit `0`, with `deep_ratio` 61/168→61/169 and `held_out` 91→92 (**+1 each, one new test file**). **CI evidence: NOT ESTABLISHED**; **nothing published** — `git tag -l` empty, `origin/master` unmoved, no build artifact committed. **This is the FIFTH consecutive `_NOTE_SECTIONS` edit** (`DF-11-4-D`), a pure zero-deletion insertion, stated for the retrospective. | Dev Agent (bmad-dev-story) |
| 2026-08-12 | Story created and fully contexted; `backlog` → `ready-for-dev`. The deciding question was settled **by building the fix and measuring it**: the minimum working lazy-import fix is **+8** physical lines against a measured **13**-line unit-2 budget, with all three partition_ids byte-unchanged, 1394/0 failures, mypy clean 72, and **72 of 72** modules importing from a freshly built wheel (baseline **67 of 72**). The file was restored and sha256 round-tripped byte-identically. Three epic premises re-measured and found stale or already-closed; the existing `_NOT_IMPORTABLE_FROM_DISTRIBUTION` guard was **proven vacuous** against the fix. | Scrum Master (bmad-create-story) |
