---
baseline_commit: 7be90f7788c66d040a887b6b68f1358856961d4c
baseline_note: >-
  HEAD is 7be90f7 ("feat(dogfood,verdict): complete Epic 8 — the honest verdict").
  Epic 8 is fully COMMITTED, including the two files the retrospective flagged as
  untracked (AI-E8-1 — re-measured 2026-08-08 with `git ls-files`: BOTH
  `minions-dogfood-proof-story-7-2-superseded.md` and
  `stories/8-5-re-derive-proof-evidence-matches-tool.md` are now tracked; that item
  is CLOSED). `git status --porcelain`, when this context was authored, reported exactly
  one entry, `?? bmad-dev-loop-pack/`, which belongs to the dev-loop orchestrator and is
  NOT yours — do not add, move or delete it. ⚠️ It now reports a SECOND entry:
  `?? _bmad-output/design-artifacts/ArgusAgent/stories/9-2-ship-distribution-another-repo-can-actually-resolve.md`
  — THIS FILE. It was left unstaged on purpose, so it does not perturb the `git status`
  baseline AC9 depends on. It IS yours: `git add` it with your delta, or you repeat
  AI-E8-1 exactly — Epic 8 shipped with its own story file untracked, and the fence check
  missed it because `git diff` cannot see an untracked path. It is not gitignored.
  Consequence you must internalise, exactly as in 8.5: `git diff HEAD` is
  EMPTY, so it is not the measuring instrument. Every figure in this story was produced
  by IMPORTING and CALLING the shipped `argus` functions in place, by running the
  shipped test suite, and by simulating the extraction over an isolated copy of the
  tree. Re-derive them yourself; do not read them off this document.
story_key: 9-2-ship-distribution-another-repo-can-actually-resolve
epic: 9
---

# Story 9.2: Ship a distribution another repo can actually resolve

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
> **This is the SECOND AND LAST story of Epic 9, and the LAST STORY IN THE ENTIRE ArgusAgent PLAN.**
> `epic-9` is already `in-progress`; Story 9.1 (`argus.* ⊬ minions_core`) is `done`. Epic 8 is `done`
> (5/5 stories, retrospective complete). There is no story after this one to inherit anything you leave
> behind. **Anything you defer here is deferred to nobody.** Read AC14 before you reach for the ledger.
>
> **THIS STORY DELIVERS IN-0 — the distribution.** Epic 8 made the verdict honest. Epic 9 must ship it in
> a box that does not contradict the label. Today there is **no release workflow** (measured: `.github/workflows/`
> holds exactly two files, `audit-ci.yml` and `argus-student-audit.yml` — neither builds or publishes),
> **no git tag** (measured: `git tag -l` is empty), and `argus-agent` is on no index. `install.sh` /
> `install.ps1` both do `pip install -e .` from a clone. There is nothing for a consumer to resolve.
>
> **🚨 THIS STORY HAS BEEN RE-SCOPED BY OPERATOR DECISION (2026-08-08).** The Epic-8 retrospective raised
> **SD-1**: three ledger entries name this story as their `target_story` and appear in **none** of the five
> acceptance criteria `epics.md:1653-1678` gives it. The operator ruled that 9.2 **absorbs them as a single
> story rather than splitting**. Those three are **DF-8-5-A** (🟠), **DF-8-4-A** and **RS-4b**, and they
> bring a fourth with them, **DF-8-5-D** (🟠). A fifth, **DF-8-4-B**, fires on this story by its own
> `target_story` wording the moment you edit `tests/test_release_note.py` — which AC6 requires. All five
> have explicit dispositions below. The variance from `epics.md` is recorded in **§Variance from the epic**;
> `epics.md` itself is NOT edited by this story.
>
> **🚩 The single largest trap in this story.** Publishing `0.1.0` while the SIGNED, content-hashed evidence
> bundle stamps `argus_version = "1.43.0"` ships the exact class of contradiction Epic 8 was created to
> delete — inside signed evidence, which is a worse place for one than prose. The package's own front door
> says so in the shipped code: `argus/__init__.py:56-58` — *"the single source for the envelope
> `argus_version` field … **Never hardcode this literal at call sites**."* `argus/dogfood/proof_run.py:168`
> hardcodes it. **AC7 exists for this. Read D3, D4 and D5 before you touch anything.**
>
> **🚫 H0 IS NOT IN THIS STORY AND IS NOT SILENTLY ABSORBED BY IT.** `epics.md:1693` records that **no
> story in this breakdown owns filing** the Minions-repo handoff H1–H4, and `sprint-status.yaml`'s DELTA
> NOTE records the handoff as deliberately **not tracked here** because it executes in another repository
> and this repo's CI cannot verify it. H0 is still **UNOWNED**, escalated as readiness-report **F5 (LIVE)**
> on 2026-08-03 and re-raised as **AI-E8-10** on 2026-08-08. It needs a human, not a story. **Do not create
> it, do not claim it, do not close it.** See AC16.

---

## Story

As a **downstream integrator** — today the Minions repository, which under **IN-1** must replace a vendored
`minions_core/apaa/` fork with a dependency, and under **IN-3** must run `argus audit .` as a CI gate keyed
to the `0`/`2`/`3`/`1` wire contract —

I want **`argus-agent` to exist as an installable, versioned artifact I can resolve from my own CI, whose
published evidence does not contradict the version I install**,

so that **I can depend on it instead of vendoring a copy that drifts** — and so that the first thing an
external consumer ever resolves from this project is not a signed proof asserting a version that does not
exist.

---

## Story Context

### Method statement — MEASURED IN PLACE, on the real working tree

> ⚠️ **Read this.** Every figure below was produced on `d:/ProjectX/XAgents/XAgents/ArgusAgent` itself at
> HEAD `7be90f7`, with `.git` and `_bmad-output/` present — **not** on a scratch copy, except where a
> simulation is explicitly labelled as such. `git diff HEAD` is empty (Epic 8 is committed), so the
> instruments were:
>
> 1. **Importing the shipped `argus` functions and calling them in place** — the real
>    `build_full_repo_plan`, `enumerate_minions_source_files`, `read_sources`, `compute_loc_by_file`,
>    `build_ast_index`, `derive_partition_plan`, `size_budget`, `enumerate_tracked_sources`.
> 2. **Running the shipped test suite** — `PYTHONIOENCODING=utf-8 python -m pytest tests/ --tb=no -q`,
>    with the progress census counted character-by-character rather than read off a summary line.
> 3. **`python -m mypy argus`.**
> 4. **Reading the shipped source with line numbers** for every code claim.
> 5. **One labelled SIMULATION** (§F) of the DF-8-5-D extraction, run over an isolated `tempfile` copy of
>    `argus/` so the real tree was never mutated; `git status --porcelain` was re-checked afterwards and
>    still reported only `?? bmad-dev-loop-pack/`.
>
> **Two things this SM could NOT measure and does not assert.** They are marked ⚠️ **UNMEASURED** wherever
> they appear, and each has an AC requiring *you* to measure it:
> - **The contents of a built sdist/wheel.** `flit_core` is not installed in this environment
>   (`ModuleNotFoundError: No module named 'flit_core'`), so no distribution was built. Everything said
>   about what the artifact contains is derived from `pyproject.toml` and flit's documented behaviour, not
>   from a built file. **AC4 requires you to build it and list its contents.**
> - **Whether the GitHub remote is reachable / public, and whether any PyPI credential exists.**
>   `git remote -v` names `https://github.com/Inan15/Agent-Argus.git`; no fetch was attempted and no
>   authentication was tested. **AC3 requires you to record what a consumer actually needs.**
>
> **Re-derive every figure yourself — do not trust this document.** Epic 8's retrospective found four
> separate cases of a figure that "was already established" failing to reproduce, including one in a
> Story-Context table (`50/65` vs the real `48/10`). The check and the belief share an origin.

### Baseline, measured 2026-08-08 at HEAD `7be90f7`

| Instrument | Result |
|---|---|
| `PYTHONIOENCODING=utf-8 python -m pytest tests/ --tb=no -q` | **1160 passed / 0 failed / 0 skipped**, exit `0`. Progress census counted from the raw output: `Counter({'.': 1160})` — 16 lines of 72 dots + 8. **The suite is fully green; this story starts on NO red.** |
| `python -m mypy argus` | **Success: no issues found in 69 source files** |
| `git status --porcelain` | `?? bmad-dev-loop-pack/` only (orchestrator's — not yours) |
| `git tag -l` | **empty** — no tag exists in this repository |
| `git remote -v` | `origin  https://github.com/Inan15/Agent-Argus.git` (fetch + push) |
| `git branch` | on `fix/honest-verdict-reporting`; `master` and `remotes/origin/master` exist |
| `.github/workflows/` | exactly **2** files: `audit-ci.yml` (test + mypy + bandit + coverage gate), `argus-student-audit.yml` (runs an audit on a consumer repo). **Neither builds, tags, or publishes anything.** |

> ⚠️ **You are on `fix/honest-verdict-reporting`, not `master`.** Both `audit-ci.yml` and
> `argus-student-audit.yml` trigger only on `master`/`main`. Whatever release workflow you add, state
> plainly which ref it triggers on and do **not** assert it has run. See AC2 and D2.

### A. The version contradiction, measured — and it is worse than "two numbers disagree"

| Where | Value | Measured at |
|---|---|---|
| `pyproject.toml:7` | `version = "0.1.0"` | read in place |
| `argus/__init__.py:59` | `__version__ = "0.1.0"` | read in place |
| `argus/dogfood/proof_run.py:168` | `DOGFOOD_ArgusAgent_VERSION = "1.43.0"` | read in place |
| `tests/test_dogfood_proof.py:649` | `assert DOGFOOD_ArgusAgent_VERSION == "1.43.0"` (`TC-ArgusAgent-DOGFOOD-001-34`) | read in place |
| `tests/test_release_note.py:787` | `assert argus.__version__ == "0.1.0"` (`TC-ArgusAgent-DOCS-001-10`) | read in place |

**The project already declares which one is right, in shipped code.** `argus/__init__.py:56-58`:

```
# ArgusAgent's own version constant — the single source for the envelope `argus_version`
# field (story 1.1, ArgusAgent-FR-25). Never hardcode this literal at call sites and
# never derive it from env/clock (it must be byte-stable across hosts, NFR-P1).
```

and `argus/store/envelope.py:99,106-107` — `argus_version: str = _ArgusAgent_VERSION` with the docstring
*"``argus_version`` is sourced from the single ArgusAgent-owned constant (``argus.__version__``); **callers
must not pass a literal.**"* `argus/dogfood/proof_run.py:648,703` passes exactly such a literal.

**The contradiction lives inside ONE persisted file, on two levels.** Traced through the shipped code, not
inferred:

- `run_dogfood` (`proof_run.py:683-684`) calls `build_evidence_bundle(..., argus_version=argus_version)`
  with the `"1.43.0"` default, so `EvidenceBundle.argus_version == "1.43.0"`.
- `persist_evidence_bundle` (`evidence/bundle.py:329-334`) calls
  `writer.write_payload("state", bundle_to_canonical_payload(bundle), ...)` and **does not pass
  `argus_version`**.
- `bundle_to_canonical_payload` (`evidence/bundle.py:285-293`) puts `"argus_version": bundle.argus_version`
  **into the hashed payload**.
- `ApaaStoreWriter.write_payload` (`store/writer.py:110-118`) calls `EnvelopeWriter.build(...)` without
  `argus_version`, so the **envelope** field takes its default `argus.__version__` = `"0.1.0"`.

**Therefore the persisted `.argus/state/<hash>.json` says `"0.1.0"` at the envelope level and `"1.43.0"`
inside the payload it wraps.** ⚠️ **UNMEASURED on disk** — the dogfood writes into a temporary snapshot
tree, and the repo-root `.argus/` was searched (`glob '.argus/**/*.json'`, 0 envelopes with an evidence
producer) and holds none. **AC7 requires you to produce one and read both fields.**

**And the fix DOES move a published signature — verified by mechanism, not assumed.** `content_hash` is
`sha256(canonical.dumps_bytes(payload))` (`store/envelope.py:57-67`), the payload contains `argus_version`,
and `write_envelope` names the file `<content_hash>.json` (`store/writer.py:74-92`). So changing the token
changes the bundle's content hash, therefore its content-addressed locator, therefore the line the proof
artifact publishes as its signature:

```
minions-dogfood-proof.md:57
- Bundle content hash (the signature): `a1e76c01cbd29241a928f71b724b4c4c01d1211e0a4ae8a6e266386f811e0c0e`
```

**One correction to an inherited belief, stated because you will read it elsewhere.**
`tests/test_release_note.py:782-783`'s docstring says `__version__` *"is folded into **every** content hash
(NFR-P1) — changing it moves every artifact hash in the repository."* That is **imprecise and you must not
act on it**: `compute_content_hash` hashes the **payload only**, and `argus_version` is an **envelope**
field, so for every artifact except the evidence bundle it changes the file's **bytes** but not its
**content hash or filename**. The evidence bundle is the exception precisely because it *also* carries the
version inside its payload. This distinction is load-bearing for AC7's blast-radius claim. It is a docstring,
not an assertion — nothing goes red if you leave it — but if you edit that test anyway (AC6/AC12 make it
likely), correct the sentence rather than propagating it.

### B. What a consumer can resolve today — measured

| Surface | Measured state | Consequence for IN-0 |
|---|---|---|
| `pyproject.toml` `[build-system]` | `flit_core >=3.2,<4`, backend `flit_core.buildapi` | Building needs `flit_core`; it is **not installed here** |
| `[tool.flit.module] name = "argus"` | flit packages **exactly the `argus` module** | ⚠️ **UNMEASURED, and it matters:** `audit/`, `phases/`, `adapters/`, `templates/` are sibling top-level directories and, on flit's documented behaviour, are **not in the distribution**. README advertises all four. **AC4/AC5b** |
| non-`.py` files under `argus/` | **zero** (`find argus -type f ! -name '*.py'` → empty) | No package-data problem to solve; the wheel is pure Python |
| `[project.scripts]` | `argus`, `argus-agent`, `repo-audit` → `argus.cli:main` | Pinned by `TC-ArgusAgent-DOCS-001-13`; changing the set breaks it |
| `[project] dependencies` | pydantic, jsonschema, radon, httpx, `tree-sitter>=0.25,<0.26`, `tree-sitter-python>=0.25,<0.26` | The tree-sitter upper bound is **load-bearing, not hygiene** — the comment at `pyproject.toml:18-24` records that `0.26.0` flips the cartridge self-audit to a false `RELEASE_READY`. **Do not widen it in a release story.** |
| `install.sh` / `install.ps1` | `pip install -e .` + `cp -r adapters/... $HOME/.claude` | Presume a **clone**. Neither is reachable by a consumer who resolves the distribution |
| `README.md` "Quickstart" | `./install.sh`, `.\install.ps1`, or `pip install -e .` | Contains **no** instruction a consumer without a clone can follow |
| `action.yml:44` | `pip install "${{ github.action_path }}"[languages]` | Installs from the **action checkout**, not from a released artifact |
| `git tag -l` | empty | Nothing to pin |

### C. `action.yml` publishes a crash as an under-covered run — DF-8-4-A, read in place

`action.yml:56-66`:

```
        echo "exit_code=$EXIT_CODE" >> $GITHUB_OUTPUT
        if [ "$EXIT_CODE" -eq 0 ]; then
          echo "verdict=RELEASE_READY" >> $GITHUB_OUTPUT
        elif [ "$EXIT_CODE" -eq 2 ]; then
          echo "verdict=NOT_READY_FOR_RELEASE" >> $GITHUB_OUTPUT
        else
          echo "verdict=INSUFFICIENT_COVERAGE" >> $GITHUB_OUTPUT
        fi
```

The `else` swallows exit **`1`** — the AR10 typed-failure code, which means **no verdict was produced at
all** — and republishes it as `verdict=INSUFFICIENT_COVERAGE`, a *ran-and-under-covered* result. Per the
amended canonical vocabulary (`epics.md:1146-1150`) `INSUFFICIENT_COVERAGE` is a **not-assessed** state, so
the mislabel is an over-claim in the exact direction Epic 8 exists to remove: a crash reads as a completed
audit. It is **pre-existing** — exit `1` predates the amendment and the amendment changed no exit-code
value. `action.yml:26-27` also documents only three codes (`0=Pass, 2=Fail, 3=Insufficient Coverage`) and
never mentions `1`.

Two further measured facts about the same file, because you are editing it anyway and a reviewer will look:
- `action.yml:22` — `strict` defaults to `"false"`, so today a consumer's gate is advisory by default. That
  is *correct* for assumption **A5** (⚠️ Unsupported: Minions lands on exit `3`, which still fails an
  unconfigured blocking gate), and it is a fact worth stating in the release note rather than changing.
- `action.yml:37-38` pins `python-version: "3.11"` while `pyproject.toml` declares `requires-python = ">=3.10"`
  and `audit-ci.yml` matrixes `3.10/3.11/3.12`. Not a defect; do not "fix" it silently.

### D. RS-4b, re-measured on THIS tree — 9 remain, exactly as the ledger says, and 2 are decoys

`grep -rn "minions_core" argus/ --include=*.py`, excluding `__pycache__`: **11 hits across 9 files.**

**The 9 that ARE RS-4b** (each verified at the line the ledger names):

| File:line | Kind |
|---|---|
| `argus/audit/deep_audit.py:21` | docstring |
| `argus/audit/ports.py:4` | docstring |
| `argus/cost/budget_governor.py:15` | docstring |
| `argus/dogfood/proof_run.py:52` | module docstring |
| `argus/dogfood/proof_run.py:53` | module docstring |
| `argus/dogfood/proof_run.py:666` | **operator-visible** `DogfoodProofError` message |
| `argus/governance/escalation.py:35` | docstring |
| `argus/store/envelope.py:25` | docstring |
| `argus/verdict/prosecutor.py:36` | docstring |

The ledger's own entry gives `proof_run.py:632` for the third of these; **AI-E8-7** already recorded that as
stale. Re-measured today it is **`:666`**. It will move **again** once you perform the DF-8-5-D extraction —
which is the argument for doing the sweep in the *same* change rather than filing a fourth line number.

**The 2 that are NOT RS-4b and must NOT be swept** — `argus/audit/minions_llm_adapter.py:5` (*"requiring the
unpackaged `minions_core` library"*) and `:29` (*"zero dependency on `minions_core`"*). These were written by
**Story 9.1** and are **true negative statements** about a dependency that no longer exists — the opposite of
a stale provenance claim. Deleting them would delete the documentation of RS-1/IN-2. RS-4b's own text
explicitly excludes this file. **Leave them.**

**Out of RS-4b's scope, measured and recorded so it is not confused with it:** the bare word *"Minions"*
(not `minions_core`) appears **44** times across **17** files under `argus/**` — 4 of them in
`minions_llm_adapter.py`. Some are now false subject claims of the class 8.5's AC2 deleted from the
*artifacts* but not from the *docstrings*, e.g. `proof_run.py:401` *"Enumerate the git-TRACKED Minions source
files"* on a function whose `scope_prefix` defaults to `"argus"` (`proof_run.py:189`). **Bounded disposition
in D10:** `argus/dogfood/**` only (measured: 13 in `proof_run.py`, 6 in `partition_plan.py`), because the
extraction rewrites those modules anyway. The rest is filed, not swept.

### E. The regeneration cascade, measured live at HEAD `7be90f7`

`build_full_repo_plan(".")`, called in place:

```
source_file_count: 69      total_loc: 18276     n_partitions: 3
commit_descriptor: 7be90f7788c66d040a887b6b68f1358856961d4c
scope_prefix: 'argus/'   exclude_prefixes: ('argus/tests/',)   effective_exclude_prefixes: ()
budget: total_credits=345  sized_ceiling=431  headroom=86  build_cost_proxy=18276  fits_within_ceiling=True
  unit 2c0f52f60457   9 files   2871 LOC
  unit 681c496d09ed  40 files  14529 LOC
  unit 973f3f199d1c  20 files    876 LOC
```

Note `effective_exclude_prefixes: ()` — the disclosed `argus/tests/` exclusion matches nothing on this tree.
That is the already-corrected 8.5/F2 behaviour working, not a new defect.

**The three rot checks that pin these numbers, read in place:**

| Test | Pins | Moves if… |
|---|---|---|
| `TC-ArgusAgent-DOGFOOD-001-03` (`test_dogfood_plan.py:175-190`) | `f"Unit count: {n}"` **and** `partition_id[:12]` for **every** live unit, present in the committed `minions-dogfood-partition-plan.md` | unit count or any unit's **member path set** changes |
| `TC-ArgusAgent-DOGFOOD-001-06` (`test_dogfood_plan.py:250-274`) | `str(result.budget.sized_ceiling)` present in the committed `minions-dogfood-budget-plan.md` | `total_credits` moves (it folds `files_indexed + python_files + detector_passes`) |
| `TC-ArgusAgent-DOGFOOD-001-20` (`test_dogfood_proof.py:223-243`) | `` f"`{verdict}` (exit `{exit_code}`)" ``, `843`, `DOGFOOD_GRADE`, `REUSED`/`REUSING`, and three heading stems, present in the committed `minions-dogfood-proof.md` | the live verdict, the grade, or a heading changes |

Plus `TC-ArgusAgent-DOGFOOD-001-18` (`test_dogfood_proof.py:154-180`): `source_file_count >= 60`,
`total_loc >= 10000`, **`unit_count >= 3`** and `1 <= unit_count <= source_file_count`.

**Committed artifact values today** (so you can see exactly what will move):
`minions-dogfood-partition-plan.md:15` *"**Unit count: 3**"*, rows `2c0f52f60457` / `681c496d09ed` /
`973f3f199d1c`; `minions-dogfood-budget-plan.md:18` *"**Sized ceiling `$X`: 431 credits**"*;
`minions-dogfood-proof.md:13` *"Commit descriptor (HEAD at generation): `be9d7449…`"* — **already one commit
behind HEAD**, and no assertion pins it, which is why the suite is green. A regeneration will move it to
`7be90f7…` or later. That is expected and honest ("at generation").

### F. ⚠️ SIMULATION — what the DF-8-5-D extraction actually does to the partition

> **This is the one figure in this document that was NOT produced from the real tree.** `argus/` was copied
> into a `tempfile` directory, `proof_run.py` was truncated there and two synthetic sibling modules written,
> and the partitioner + budget accountant were called over the copy. The real tree was not mutated
> (`git status --porcelain` re-checked afterwards: `?? bmad-dev-loop-pack/` only). **Your real split will
> distribute lines differently, so re-measure. Treat the direction as informative and the exact ids as
> not-yet-true.**

| | files | total_loc | units | total_credits | sized_ceiling | unit ids |
|---|---|---|---|---|---|---|
| baseline (copy of live tree) | 69 | 18276 | **3** | 345 | **431** | `2c0f52f60457` · `681c496d09ed` · `973f3f199d1c` |
| after simulated 2-module extraction | 71 | 18306 | **3** | 355 | **443** | `2c0f52f60457` · `681c496d09ed` · **`31483e58e318`** |

**Four things this measurement establishes, two of which correct the inherited narrative:**

1. **`unit_count` did NOT drop to 2 — it stayed at 3.** The retrospective and `DF-8-5-D` both flag *"a drop
   to 2 units is a finding to report, never a licence to loosen the assertion."* That instruction stands and
   you must still verify it, but the measured direction is the opposite: unit `681c496d09ed` sits at
   **exactly 40 files**, which is `DEFAULT_SOFT_FILE_LIMIT = 40` (`argus/index/partitioner.py:107`), so
   adding modules pushes toward a **split**, not a merge. Do not enter this work expecting a drop.
2. **A `partition_id` DID change: `973f3f199d1c` → `31483e58e318`.** The two new modules landed in that unit
   (20 → 22 files). `681c496d09ed` kept its id while its LOC moved 14529 → 14093, which proves the mechanism
   precisely: **`partition_id` is a sha256 over the unit's sorted member PATHS, not over content.**
   Therefore `TC-ArgusAgent-DOGFOOD-001-03` **will** go red and the partition plan **must** be regenerated.
3. **`sized_ceiling` moved 431 → 443**, so `TC-ArgusAgent-DOGFOOD-001-06` **will** go red and the budget plan
   **must** be regenerated.
4. **Nothing enters the partition set until you `git add` it.** `enumerate_tracked_sources`
   (`proof_run.py:395-419`) and `enumerate_minions_source_files` both read `git ls-files -z <scope_prefix>`.
   An untracked new module is **invisible** to the plan. If you regenerate before staging the new modules,
   you will produce artifacts that pass the rot check and are wrong the instant you commit — and, per
   **AI-E8-2**, `git diff` cannot see the omission. **Stage first, regenerate second, and verify with
   `git status --porcelain`, not `git diff`.**

### G. The NFR-M1 fence — what it does and does NOT force

Measured: `find argus -name '*.py' | xargs wc -l | sort -rn`:

```
1199  argus/pipeline.py        ← FENCED by this story (D11)
1196  argus/dogfood/proof_run.py
 705  argus/dogfood/partition_plan.py
 668  argus/verdict/verdict_gate.py
 645  argus/index/partitioner.py
 613  argus/reports/generator.py
```

**Correction to an inherited claim, stated plainly.** SD-1 reads *"The fix is not one line … it edits
`proof_run.py` (1196/1200) → **triggers** DF-8-5-D's extraction."* Two different mechanisms are being
conflated and you should know which one is actually binding:

- **The NFR-M1 fence does NOT force the extraction.** The DF-8-5-A fix replaces a literal with a name.
  Sourcing it as `from argus import __version__ as _ARGUS_VERSION` + `DOGFOOD_ArgusAgent_VERSION = _ARGUS_VERSION`
  is **+1 line net** → 1197/1200. It fits.
- **The ledger DOES force it.** `DF-8-5-D`'s `target_story` is literally *"the first story that edits
  `argus/dogfood/proof_run.py` for any reason"* — and this story does. Combined with **AI-E8-3**
  (*"sequence the extraction as an explicit pre-condition … do not discover it at edit time"*) and the fact
  that **there is no story after this one**, the extraction lands here.

Say this correctly in your Completion Notes. *"The fence forced it"* is not what the measurement shows;
*"the ledger named this story and no later story exists"* is.

**Measured composition of `proof_run.py` (the extraction map):**

| Block | Lines | Destination |
|---|---|---|
| module docstring · `__all__` (`:136`) · constants (`:156-190`) · `DogfoodProofError` (`:193-203`) | 1–203 | **stays** in `proof_run.py` |
| the 5 frozen dataclasses: `AdjudicationRow` `:204` · `CostSummary` `:233` · `ScopeDisclosure` `:266` · `CriticalClauseDisclosure` `:286` · `DogfoodProofRun` `:319` | 204–374 (**171 lines**) | → `argus/dogfood/proof_types.py` |
| impure shell `_run_git` `:375` · `enumerate_tracked_sources` `:395` · `materialize_snapshot` `:422`; pure `adjudication_rows` `:465` · `cost_summary` `:508`; `_DogfoodExecution` `:572` · `_read_critical_subsystem_set` `:588` · `run_dogfood` `:644` · `build_dogfood_proof` `:699` | 375–829 | **stays** |
| pure renderers `_audited_tree_clause` `:830` · `_row_token` `:846` · `_render_assessed_population` `:857` · `_render_critical_clause` `:894` · `_render_ceiling_pair` `:951` · `render_proof_markdown` `:989` | 830–1196 (**367 lines**) | → `argus/dogfood/proof_render.py` |

Arithmetic: 1196 − 171 − 367 = **658** lines left in `proof_run.py`, plus the re-export shim. `DF-8-5-D`
estimates the renderer at *"~390 lines"*; measured it is **367**. State your own number.

### H. The release-note surface you are about to change — and the 21 tests over it

`tests/test_release_note.py` collects **21** cases from **18** test functions. The ones this story touches:

| Test | Assertion, read in place | This story |
|---|---|---|
| `TC-ArgusAgent-DOCS-001-01` (`:361-364`) | `assert "## Unreleased" in note` | **WILL GO RED** when AC6 turns the heading into a version. Update it; do not delete it |
| `TC-ArgusAgent-DOCS-001-10` (`:779-789`) | `argus.__version__ == "0.1.0"` · `__status__ == "experimental"` · `__all__ == ["__version__","__status__"]` | **stays green** under D1 (no version bump). If you bump, this is the test you must update *deliberately* |
| `TC-ArgusAgent-DOCS-001-11` (`:792-804`) | every `_bmad-output…`/`CHANGELOG.md` path cited in `argus/__init__.py`'s docstring **exists on disk** | binds if you add a path to the front door |
| `TC-ArgusAgent-DOCS-001-12` (`:807-825`) | the front door states `argus-agent`, `argus/`, `repo-audit`, `Agent-Argus` | binds if you rewrite the front door |
| `TC-ArgusAgent-DOCS-001-13` (`:827-841`) | `pyproject.toml` contains `name = "argus-agent"` and the console-script set is **exactly** `["argus","argus-agent","repo-audit"]` | **do not change the script set** |

`CHANGELOG.md` structure: `## Unreleased` at `:20`, then `### Behaviour: exit codes` `:30` · `### Artifacts:
schema versions` `:77` · `### Defaults: --coverage-scope` `:129` · `### Output: changed strings` `:147` ·
`### Unchanged on purpose` `:245` · `### API (library consumers)` `:272` · `### Do I need to change
anything?` `:299`. The honesty preamble is `:7-16` and says, verbatim, *"`argus-agent` is **not tagged and
not published to any package index**, and there is no release workflow"* and *"**"Unreleased" below means
exactly one thing: present on the default branch of the Agent-Argus repository**"*. **That preamble becomes
false the moment this story succeeds. AC6 owns it.**

### I. What the release must NOT claim — SD-2, and the reason it is here

Epic 8's retrospective raised **SD-2**: the repo separation silently changed the *class* of Argus's flagship
evidence. Measured by 8.5 and recorded append-only in `deferred-work.md:823-830`:

| | Story-7.2 Minions run (preserved) | Re-derived Argus SELF-audit (live) |
|---|---|---|
| `cross_partition` / `hardcoded_secret` / `orphan_code` | 332 / 2289 / 285 | **2 / 22 / 77** |
| Total findings · files · LOC | 2906 · 135 · 36712 | **101 · 69 · 18206** |
| Verdict | `NOT_READY_FOR_RELEASE` (exit `2`) | **`RELEASE_READY` (exit `0`)**, `row_3_gates_met` |

`minions-dogfood-proof.md:9` states it in the artifact's own words: *"A self-audit is MATERIALLY WEAKER
evidence than the independent-repository run it supersedes … it is **NEVER** independent corroboration."*
The ≥80%-precision externalization gate (`DF-7-2-A` / `DF-6-6-A`) is defined over the **Minions** population,
which now survives only in `minions-dogfood-proof-story-7-2-superseded.md` and *"can never be re-derived in
this repository."*

**Consequence binding on this story:** a release that presents the green self-audit as assurance evidence
would be the release story committing the epic's own defect. `grade: demo-heuristic-only` stays, the gate
stays **PROVISIONAL**, `protocol_cleared` is never passed `True`, and no release prose — README, CHANGELOG,
GitHub Release body, workflow output — says or implies that Argus has been externally validated. **AC12.**

### J. Known figures this story knowingly REPUBLISHES without fixing — say so, do not launder

Regenerating `minions-dogfood-proof.md` reprints a number already **filed as wrong**:

- **`DF-8-5-C`** — `proof_run.py:764-765` calls `precision_gate_status_for(precision=Fraction(0,1), n=0, provisional=True, ...)`
  with **literals**, and the result renders at `minions-dogfood-proof.md:87` as *"N=0 labeled cartridges
  populated, floor N=5"*, while the shipped registry measures `distinct_rule_class_count() == 5` and
  `populated_planted_defect_count() == 7`. It **understates** — it makes the provisional gate look further
  from its floor than it is, so it can never make a gate look cleared.
- Its `target_story` is *"the first story that edits the 6.5/6.6 precision surface (`argus/precision/**` or
  the cartridge registry) **after the human `DF-7-2-A` adjudication**"*. That adjudication has not happened.
  **This story is not it. D8: republish unchanged and state that you did.**

Silently reprinting it is the failure mode; reprinting it while naming it is the honest act. **AC13.**

---

## Acceptance Criteria

> **Story-authoring rule applied throughout (AI-E8-6, from the Epic-8 retrospective).** Where an AC
> quantifies universally — *"every"*, *"each"*, *"no"* — its test must **enumerate the space and FAIL on an
> unenumerated member**, not sample one. All five Epic-8 stories shipped a guard narrower than its own AC.
> AC5, AC11, AC12 and AC15 are written as enumerated spaces for this reason.

### AC1 — The released version is decided, recorded, and consistent across every surface that states it

**Given** `pyproject.toml:7`, `argus/__init__.py:59` and `argus/dogfood/proof_run.py:168` today read
`0.1.0`, `0.1.0` and `1.43.0`
**When** this story completes
**Then** exactly **one** version value is stated by the package, it is **`0.1.0`** (**D1**), and it is
reachable from a single source: `pyproject.toml` and `argus.__version__` both literal `0.1.0`, and every
other in-package version reference derives from `argus.__version__` rather than restating it
**And** a committed test enumerates the version-bearing surfaces and asserts agreement — the enumeration
must include `pyproject.toml`'s `version =`, `argus.__version__`, and `argus.dogfood.proof_run.DOGFOOD_ArgusAgent_VERSION`,
and must **fail** if a new module introduces a fourth version literal
**And** the decision to ship `0.1.0` rather than bump is recorded with its reasons in the Dev Agent Record
(see **D1**), including that `TC-ArgusAgent-DOCS-001-10` pins `0.1.0` and was therefore **not** modified.

### AC2 — A committed release workflow builds an installable artifact for a tagged version, and its claims are bounded by what was actually observed

**Given** `.github/workflows/` today contains no release or publish workflow (measured: only `audit-ci.yml`
and `argus-student-audit.yml`, neither of which builds anything)
**When** this story completes
**Then** a release workflow exists at `.github/workflows/<name>.yml` that, on a version tag, builds **both**
an sdist and a wheel and attaches them to a GitHub Release for that tag
**And** the workflow declares its trigger explicitly (tag pattern and/or `workflow_dispatch`) and its
required permissions, and does not depend on any secret that is not named in AC3's access record
**And** the story records **whether the workflow has ever executed**. ⚠️ If it has not — which is the
expected state, since this branch is `fix/honest-verdict-reporting` and CI here cannot be verified from the
working tree — that is recorded as *"committed, not yet executed"*, with the build proven locally per AC4.
**No AC, no Completion Note, no README line and no CHANGELOG line may state or imply that a release has been
published unless a URL or an `Actions` run id is cited as evidence** (**D2**).

### AC3 — The distribution target is recorded WITH its access requirements, its interim status, and its exit condition

**Given** a consumer's CI must resolve the artifact, and the choices are PyPI, a private index, or a
`git+https://…@<tag>` VCS pin (`epics.md:1665-1667`)
**When** the target is chosen
**Then** the choice is recorded in a consumer-facing document (README and/or CHANGELOG), naming:
1. the **exact dependency string** a consumer writes — for the locked default (**D2**) that is
   `argus-agent @ git+https://github.com/Inan15/Agent-Argus.git@v0.1.0`, cross-checked against the measured
   remote `https://github.com/Inan15/Agent-Argus.git`;
2. **how a consumer's CI authenticates** — including the honest answer *"no credential is required if and
   only if the repository is public"*, with the repository's actual visibility **measured and stated**, not
   assumed;
3. that the VCS pin is **INTERIM**, marked as such in the document itself;
4. the **named condition** under which it moves to an index (e.g. *"when `argus-agent` is claimed on PyPI
   and a `PYPI_API_TOKEN` secret exists in this repository"*), so the interim status has an exit and does
   not become permanent by silence.

**And** the Minions-side shape it enables is stated without being executed here: **IN-1** requires an
optional extra (`minions[argus]`), never a base dependency, because Minions declares `dependencies = []`.
Stating it is in scope; changing the Minions repo is **not** (RS-1, and see AC16).

### AC4 — The artifact is PROVEN by installation into a clean environment, and its contents are MEASURED not assumed

**Given** `epics.md:1672-1674` requires the artifact to be *"proven, not merely built"*
**When** the distribution is built
**Then** the build is executed and the resulting sdist and wheel filenames are recorded
**And** the wheel is installed into a **fresh virtual environment that does not contain this repository on
`sys.path`**, and in that environment:
- `argus --help` exits `0`;
- `argus audit <fixture-repo>` runs to completion and emits a verdict with one of the wire-contract exit
  codes `0`/`2`/`3`;
- `python -c "import argus, sys; assert 'minions_core' not in sys.modules"` succeeds — Story 9.1's RS-1/IN-2
  guarantee is re-proven **from the built artifact**, not only from the source tree;
- `python -c "import argus; print(argus.__version__)"` prints the AC1 version.

**And** the **file list of the built wheel and sdist is recorded verbatim** in the Dev Agent Record. This is
mandatory because it is ⚠️ **UNMEASURED** by this story's context: `[tool.flit.module] name = "argus"` means
the distribution is expected to contain **only** the `argus` package, while `README.md:70-84` advertises
`audit/`, `phases/`, `adapters/` and `templates/` as part of ArgusAgent. **Whatever the listing shows is the
truth and the prose must match it** — see AC5b.

### AC5 — Release edge cases are handled as an ENUMERATED SPACE, and the guard fails on an unenumerated member

**Given** boundary **B10** (`epics.md:1676-1678`)
**When** the release path encounters any of the following
**Then** the workflow behaves **explicitly and refuses**, rather than producing an artifact whose provenance
cannot be established:

| # | Case | Required behaviour |
|---|---|---|
| E1 | working tree dirty at build time | refuse the build |
| E2 | the tag already exists | refuse; no silent overwrite |
| E3 | a re-tag / tag move is attempted | refuse |
| E4 | the version already has a published artifact for that target | refuse; no silent overwrite |
| E5 | the tag does not match the `pyproject.toml` version | refuse — a `v0.2.0` tag on a `0.1.0` tree is a provenance failure, not a rounding error |
| E6 | the build produces no artifact, or only one of sdist/wheel | refuse; do not publish a partial release |

**And** the enumeration lives in **one** named place in the repository (a constant, a table, or a documented
list in the workflow), and a committed test asserts that **every member of that enumeration is handled** and
**fails when a member is added without a handler**. A test that exercises one case and passes is a breach of
this AC, not a satisfaction of it.

### AC5b — The published prose describes the artifact that actually exists

**Given** the AC4 file listing
**When** `README.md` is updated
**Then** it carries an installation path a consumer **without a clone** can follow (the AC3 dependency
string), and it states plainly which capabilities come **with the distribution** and which require the
**git repository** — in particular the RAM `audit/` / `phases/` / `adapters/` / `templates/` surfaces and the
`install.sh` / `install.ps1` scripts, if the AC4 listing shows they are not in the wheel
**And** no README claim survives that the AC4 listing contradicts. If the listing shows all four directories
*are* packaged, record that and leave the prose alone — the AC is *"prose matches measurement"*, in whichever
direction the measurement runs.

### AC6 — `CHANGELOG.md` becomes a released version, and its honesty preamble stops being false

**Given** `CHANGELOG.md:20` is `## Unreleased` and `:7-16` states *"not tagged and not published to any
package index, and there is no release workflow"* and *"'Unreleased' below means exactly one thing: present
on the default branch"*
**When** this story ships a release workflow and a tagged artifact
**Then** the `## Unreleased` heading becomes the released version heading with its date, the preamble is
rewritten to state what is **now** true — bounded strictly by AC2's evidence rule, so if the workflow has not
executed the preamble says *"a release workflow exists and the distribution is resolvable by <the AC3
string>"* and **not** *"published to an index"*
**And** `tests/test_release_note.py::test_TC_ArgusAgent_DOCS_001_01_note_exists_and_is_headed_unreleased`
(`:361-364`) is **updated, not deleted**, so the note still cannot lose its version heading
**And** the note gains a consumer-facing section covering: the AC3 dependency string and its access
requirements; the exit-code arm added by AC10; and the fact that the `argus-agent` **exit-code wire contract
is unchanged by this release** — nothing about `0`/`2`/`3`/`1` moves.

### AC7 — DF-8-5-A: the signed evidence bundle stops asserting a version that does not exist

**Given** `argus/dogfood/proof_run.py:168` defines `DOGFOOD_ArgusAgent_VERSION = "1.43.0"`, passes it at
`:648` and `:703`, and it reaches the SIGNED, content-hashed evidence bundle through
`build_evidence_bundle(..., argus_version=…)` at `:683-684` → `bundle_to_canonical_payload`
(`evidence/bundle.py:288`) → the hashed payload
**When** this story completes
**Then** the value is sourced from `argus.__version__` rather than a module literal, honouring the rule the
package already states at `argus/__init__.py:56-58` (*"Never hardcode this literal at call sites"*) and at
`argus/store/envelope.py:106-107` (*"callers must not pass a literal"*)
**And** `tests/test_dogfood_proof.py:649`'s `assert DOGFOOD_ArgusAgent_VERSION == "1.43.0"`
(`TC-ArgusAgent-DOGFOOD-001-34`) is updated **through** the fix — asserting agreement with
`argus.__version__` — **not around it**, and its adjacent comment *"argus_version provenance is the pyproject
version token"* (which is false today, since pyproject reads `0.1.0`) is corrected
**And** the change is **demonstrated RED-first**: show the pre-fix code producing a bundle whose payload
`argus_version` disagrees with `argus.__version__`, and the post-fix code producing one where they agree
**And** the resulting bundle content hash is re-measured and the new value recorded — the committed
`minions-dogfood-proof.md:57` signature line
(`a1e76c01cbd29241a928f71b724b4c4c01d1211e0a4ae8a6e266386f811e0c0e`) is expected to change, and AC9 requires
the artifact to be regenerated so it publishes the real one
**And** the persisted envelope is inspected on disk and both levels reported: the **envelope**
`argus_version` field (sourced from `argus.__version__`) and the **payload** `argus_version` (sourced from
the dogfood constant) must now agree.

### AC8 — DF-8-5-D: `proof_run.py` is split, with the public import surface preserved

**Given** `argus/dogfood/proof_run.py` is 1196 lines against the NFR-M1 1200-line ceiling and carries five
responsibilities, and `DF-8-5-D`'s `target_story` is *"the first story that edits `argus/dogfood/proof_run.py`
for any reason"* — which this story does
**When** this story completes
**Then** the pure renderers are extracted to `argus/dogfood/proof_render.py` and the five frozen dataclasses
to `argus/dogfood/proof_types.py`, and **both are re-exported from `proof_run.py`** so that every existing
`from argus.dogfood.proof_run import …` continues to work with **no** change at any call site
**And** the preservation of the import surface is proven by an enumerated test: for **every** name in
`argus.dogfood.proof_run.__all__` (`proof_run.py:136`), `from argus.dogfood.proof_run import <name>`
succeeds — and the test **fails if a name is removed from `__all__`**, so shrinking the surface cannot
silently satisfy it
**And** all three modules are ≤1200 lines, with the measured line count of each recorded
**And** no behaviour changes: the extraction is proven to be a **pure move** by showing that
`render_proof_markdown` over the same `DogfoodProofRun` produces byte-identical output before and after
**And** the **actual** renderer size is stated (measured by this context at 367 lines, `:830-1196`; `DF-8-5-D`
estimates ~390 — report your number, not either of these).

### AC9 — The regeneration cascade is executed ONCE, LAST, and every moved figure is re-measured

**Given** AC7 changes the bundle hash the proof publishes, AC8 adds two modules to `argus/**`, and
`enumerate_tracked_sources` / `enumerate_minions_source_files` read `git ls-files -z`
**When** the artifacts are regenerated
**Then** the new modules are **staged in git BEFORE regeneration** — an untracked module is invisible to the
partition plan, and `git diff` cannot see the omission (**AI-E8-2**); verify with `git status --porcelain`
**And** all three committed artifacts — `minions-dogfood-proof.md`, `minions-dogfood-partition-plan.md`,
`minions-dogfood-budget-plan.md` — are regenerated **from the live generators, once, after every source edit**,
and **none is hand-edited** (each carries *"do NOT hand-edit"* in its own banner; if a rendered line is wrong,
fix the renderer and regenerate)
**And** the following are re-measured and reported, each with its before/after value: `unit_count`, every
`partition_id[:12]`, `source_file_count`, `total_loc`, `total_credits`, `sized_ceiling`, the verdict + decision
row, and the bundle content hash. This context measured, at HEAD `7be90f7`: 3 units
(`2c0f52f60457`/`681c496d09ed`/`973f3f199d1c`), 69 files, 18276 LOC, 345 credits, ceiling 431.
**And** `TC-ArgusAgent-DOGFOOD-001-18`'s `unit_count >= 3` is re-verified against the real post-extraction
tree. A simulation in §F held at 3; **if the real split yields 2, that is a finding to REPORT — never a
licence to loosen the assertion.**
**And** after regeneration, `tests/test_dogfood_plan.py` and `tests/test_dogfood_proof.py` are fully green,
and the three rot checks `-03`, `-06`, `-20` are shown green **without any assertion having been weakened**
(`git diff` the two test files and state it).
**And** `DOGFOOD_BUDGET_CEILING = 843` is **not** re-pointed at the live sized ceiling (**D7**, upholding
Story 8.5's own D7).

### AC10 — DF-8-4-A: `action.yml` stops publishing a crash as an under-covered run

**Given** `action.yml:56-66` maps `0 → RELEASE_READY`, `2 → NOT_READY_FOR_RELEASE`, `else → INSUFFICIENT_COVERAGE`,
so exit `1` — the AR10 typed-failure code meaning **no verdict was produced** — is republished as a
*ran-and-under-covered* result
**When** this story completes
**Then** exit `1` has its **own explicit arm**, distinguishable by a consuming workflow from every verdict
value, and the chosen vocabulary is recorded (an `AUDIT_FAILED`-style token, or failing the step outright —
decide and say why)
**And** the exit-code map is enumerated over the **complete** space `{0, 2, 3, 1, anything else}`, with the
final catch-all mapping to a failure token rather than to a verdict token — an unmapped future exit code must
never render as an assessment
**And** `action.yml`'s `outputs.verdict` and `outputs.exit-code` descriptions (`:26-30`) are updated to state
the new arm; they currently document only three codes
**And** the release note records it (AC6), because the released artifact's exit-code behaviour **is** the
integration surface for **IN-3** / handoff **H3**
**And** `strict: "false"` at `:22` is **left as the default** and the reason recorded: assumption **A5**
(⚠️ Unsupported) measures that Minions lands on exit `3` after the amendment, which still fails an
unconfigured blocking gate — advisory-by-default is the correct shipped posture, and changing it here would
pre-empt a policy decision that belongs to H3.

### AC11 — RS-4b: the 9 remaining `minions_core` references are swept, and the 2 decoys are left standing

**Given** RS-4b's sequencing constraint (*"must FOLLOW Story 8.5"*) is now satisfied, and 6 of its 15
references were consumed by Story 8.5
**When** this story completes
**Then** `grep -rn "minions_core" argus/ --include=*.py` (excluding `__pycache__`) returns **only** the two
occurrences in `argus/audit/minions_llm_adapter.py` (`:5`, `:29`), which are Story 9.1's **true negative
statements** about a dependency that no longer exists and must **not** be deleted (**D9**)
**And** the nine swept references are each named with their before/after text: `audit/deep_audit.py:21` ·
`audit/ports.py:4` · `cost/budget_governor.py:15` · `dogfood/proof_run.py:52` · `:53` · `:666`
(the operator-visible `DogfoodProofError` message — a user-facing string, not a comment) ·
`governance/escalation.py:35` · `store/envelope.py:25` · `verdict/prosecutor.py:36`
**And** a committed test enumerates the `argus/**` `.py` tree and **fails on any `minions_core` occurrence
outside an explicit allowlist** containing exactly `argus/audit/minions_llm_adapter.py` — so a re-introduction
in any other module goes red, and the allowlist itself is the enumerated space
**And** the ledger's stale line reference for the third item (`:632`, corrected to `:666` by this context and
by **AI-E8-7**) is closed out by the sweep rather than re-filed with a fourth line number
**And** the bare-word *"Minions"* subject claims inside `argus/dogfood/**` are corrected in the same pass
(**D10**; measured: 13 in `proof_run.py`, 6 in `partition_plan.py` — including `proof_run.py:401`'s *"Enumerate
the git-TRACKED Minions source files"* on a function whose `scope_prefix` defaults to `"argus"` at `:189`),
while the ~21 occurrences elsewhere under `argus/**` are **explicitly out of scope** and recorded as such.

### AC12 — No release surface presents the self-audit as assurance, and the precision gate is not flipped

**Given** SD-2 — Argus's flagship evidence changed class from an independent Minions audit to a self-audit
of `argus/`, and the ≥80%-precision externalization gate is defined over the frozen, non-re-executable
`minions-dogfood-proof-story-7-2-superseded.md`
**When** anything consumer-facing is written or regenerated by this story
**Then** across the **enumerated** set of release surfaces — `README.md`, `CHANGELOG.md`, the release
workflow's own output/body text, `action.yml`, and all three regenerated dogfood artifacts — **none** states
or implies that Argus has been externally validated, that the precision gate is cleared, or that a green
self-audit is assurance evidence
**And** `grade: demo-heuristic-only` is intact in the regenerated proof, `protocol_cleared` is never passed
`True`, the 6.5 marker is not flipped, and `DOGFOOD_EXTERNALIZATION_GUARD` (`proof_run.py:173`) is unchanged —
each verified, not assumed
**And** `DF-6-6-A`, `DF-6-6-A-P1`, `DF-6-6-A-P2` and `DF-7-2-A` remain **OPEN** and are **not** rewritten
**And** the guard test enumerates the surface set above and **fails if a surface is added to the release
without being registered** — the `_REPORT_POINTERS` fail-on-unregistered pattern from Story 8.3, which is this
project's established shape for exactly this (**AI-E8-6**).

### AC13 — Knowingly-republished wrong figures are named in the story record, not laundered by regeneration

**Given** AC9 regenerates `minions-dogfood-proof.md`, which reprints `DF-8-5-C`'s *"N=0 labeled cartridges
populated, floor N=5"* while the measured corpus is 5 distinct rule classes / 7 populated rows
**When** the artifact is republished
**Then** the Completion Notes state explicitly that this figure was **knowingly republished unchanged**,
name `DF-8-5-C`, state that it **understates** (and therefore cannot make a gate look cleared), and state why
it was not fixed here — its `target_story` names the 6.5/6.6 precision surface **after** the human `DF-7-2-A`
adjudication, which has not occurred (**D8**)
**And** `DF-8-5-C` remains **OPEN** and is not rewritten
**And** any *other* figure this story republishes without re-deriving is disclosed the same way. A number that
appears in a published artifact because it was already there is still a number this story published.

### AC14 — Every ledger id that names this story gets an explicit disposition, and nothing is deferred to nobody

**Given** this is the **last story in the plan** — there is no successor to inherit a deferral — and §5 of the
Epic-8 retrospective established that items framed as handoffs evaporate while items attached to a named
deliverable land
**When** this story completes
**Then** `deferred-work.md` is amended **append-only** (nothing above the new section edited, reordered or
deleted) with one dated section that gives a disposition for **each** of the following, by id:

| id | Expected disposition | Basis |
|---|---|---|
| `DF-8-5-A` | **CLOSED** here (AC7) | `target_story: 9-2` |
| `DF-8-5-D` | **CLOSED** here (AC8) | `target_story:` *"the first story that edits `proof_run.py` for any reason"* |
| `DF-8-4-A` | **CLOSED** here (AC10) | `target_story: 9-2` |
| `RS-4b` | **CLOSED** here (AC11) | `target_story: 9-2 (after 8-5)` |
| `DF-8-4-B` | **CLOSED** here, or explicitly left open with a reason | its `target_story` is *"the first story after 8.5 that edits `tests/test_release_note.py` (or Epic-9 `9-2`, whichever fires first)"* — **AC6 edits that file, so it fires** (**D12**) |
| `DF-8-5-C` | stays **OPEN**, republished knowingly (AC13) | target is the precision surface after `DF-7-2-A` |
| `DF-8-5-B` | stays **OPEN** — its target reads *"the first story **after Epic 9**"* | but record that this story hit exactly the pain it describes, and whether the AC9 work incidentally made the remedy discoverable |
| `DF-8-4-C`, `DF-8-4-D` | stay **OPEN** — their targets (`generator.py`'s critical-subsystems section; `cli.py::main`'s exception handling) are **fenced** by AC15 | do not open them |
| `DF-8-2-A`, `DF-8-3-A`, `DF-8-3-C` | stay **OPEN** and are **explicitly re-recorded as unowned after Epic 9** | all gate on the `pipeline.py` (1199/1200) extraction, which AC15 fences |

**And** each closure carries its closing evidence (test id and/or measured before/after), in the CC-3 shape
this register uses
**And** the two Low items Epic 8 left open at PASS (**AI-E8-7**) are resolved: the RS-4b line-number correction
(`:632` → `:666`) is superseded by AC11's sweep, and `build_dogfood_proof` recording its subject from a module
constant rather than the value the enumeration used is either fixed alongside AC8 or given a ledger id
**And** the story states plainly, for the register as a whole, which entries have **no owner after this story
closes** — because after this, nobody is looking.

### AC15 — Fences, and whole-system proof

**Given** this story is large and the two largest modules in the repo are four and one lines from the NFR-M1
ceiling
**When** the delta is measured
**Then** the following are **untouched** — verified with `git status --porcelain` **and** `git diff --stat`
(the first because `git diff` cannot see an untracked path, the exact blind spot that cost Epic 8 its third
recurrence):

`argus/pipeline.py` (**1199/1200 — do not add a line**) · `argus/pipeline_persist.py` ·
`argus/verdict/**` · `argus/ledger/**` · `argus/reports/**` · `argus/cli.py` · `argus/detectors/**` ·
`argus/index/**` · `argus/store/**` *(except the `envelope.py:25` docstring line named by AC11)* ·
`argus/evidence/**` · `argus/precision/**` · `argus/cache/**` ·
`minions-dogfood-proof-story-7-2-superseded.md` (the only surviving copy of the independent Minions run —
**it can never be re-derived in this repository**) · every `_bmad-output/design-artifacts/ArgusAgent/*retro*.md` ·
`epics.md` · `E-PRD/**` · `bmad-dev-loop-pack/` (the orchestrator's — not yours)

**And** the whole system is green at the end: `PYTHONIOENCODING=utf-8 python -m pytest tests/ -q` with the
exact pass/fail/skip counts pasted (baseline measured by this context: **1160 / 0 / 0**, exit `0`), and
`python -m mypy argus` clean (baseline: **69 source files**; expect **71** after AC8)
**And** no file under `argus/` exceeds 1200 lines, with the top-5 line counts pasted
**And** every new test id continues the project's `TC-ArgusAgent-<AREA>-<SEQ>-<SUBSEQ>` convention;
`TC-ArgusAgent-DOGFOOD-001` is taken through **-36**, so new dogfood tests start at **-37**.

### AC16 — H0 is named as still-unowned and is NOT absorbed by this story

**Given** `epics.md:1693-1699` records that **no story in this breakdown owns filing** the Minions handoff
H1–H4, that H0 is **UNOWNED**, and that *"a handoff nobody files is a handoff that does not exist"*; and given
`sprint-status.yaml`'s DELTA NOTE records the handoff as **deliberately not tracked in this repository**
**When** this story completes
**Then** the story record states explicitly that **H0 remains unowned**, that this story did **not** file
H1–H4, and that filing them requires a **named human** — it is not created, claimed, or closed here
**And** no artifact this story produces implies the Minions integration is done, scheduled, or owned
**And** the related unresolved facts are restated once so they are not lost when this repo's plan closes:
assumption **A5** is ⚠️ **Unsupported** (post-amendment Minions lands on row 4 → exit `3`, which still fails an
unconfigured CI gate, so **H3** needs a policy decision before the gate can be blocking), and **IN-1** must be
an optional extra because Minions declares `dependencies = []`.

---

## Tasks / Subtasks

- [x] **Task 0 — Establish the baseline BEFORE changing anything (AC15).**
  - [x] `git log --oneline -1` · `git status --porcelain` · `git tag -l` · `git remote -v` — paste verbatim.
  - [x] `PYTHONIOENCODING=utf-8 python -m pytest tests/ -q` and `python -m mypy argus` — paste the counts.
  - [x] Record the top-5 `argus/**` line counts. Capture the baseline **before** the first edit; a
        reconstructed baseline is a claim, not a measurement (Epic-8 retro §4).

- [x] **Task 1 — DF-8-5-A first, RED-first, BEFORE the extraction (AC7, AC1).**
  - [x] Demonstrate the defect: build an evidence bundle through the shipped path and show
        `payload["argus_version"] == "1.43.0"` while the envelope field reads `"0.1.0"`. Paste it.
  - [x] Record the pre-fix bundle content hash and confirm it matches `minions-dogfood-proof.md:57`.
  - [x] Source the value from `argus.__version__`; update `TC-ArgusAgent-DOGFOOD-001-34` **through** the fix
        and correct its false adjacent comment.
  - [x] Record the post-fix content hash. Do **not** regenerate artifacts yet.
  - [x] Add the AC1 version-surface enumeration test.
  - [x] Confirm `proof_run.py` is still ≤1200 lines (expected ~1197) — it should fit *before* the extraction,
        which is the point of D4.

- [x] **Task 2 — DF-8-5-D extraction (AC8).**
  - [x] Create `argus/dogfood/proof_types.py` (the five frozen dataclasses, `:204-374`) and
        `argus/dogfood/proof_render.py` (the pure renderers, `:830-1196`).
  - [x] Re-export both from `proof_run.py` so `__all__` and every existing import path are unchanged.
  - [x] Prove the pure-move: `render_proof_markdown` over the same `DogfoodProofRun` is byte-identical
        before and after.
  - [x] Add the enumerated `__all__` import-surface test (fails if a name is dropped).
  - [x] Record all three line counts. Keep AR8's pure/impure narration accurate in each module's docstring.

- [x] **Task 3 — RS-4b sweep + the `argus/dogfood/**` subject claims (AC11, D9, D10).**
  - [x] Sweep the nine; leave `minions_llm_adapter.py:5,29` standing.
  - [x] Correct the bare-word "Minions" subject claims in `argus/dogfood/**` only.
  - [x] Add the enumerated allowlist guard test.
  - [x] Re-run `grep -rn "minions_core" argus/ --include=*.py` and paste the result.

- [x] **Task 4 — Stage, THEN regenerate, ONCE, LAST (AC9).**
  - [x] `git add` the two new modules. Verify with `git status --porcelain` (**not** `git diff`).
  - [x] Regenerate all three dogfood artifacts from the live generators. Hand-edit none.
  - [x] Re-measure and tabulate before/after: unit count, every `partition_id[:12]`, file count, total LOC,
        credits, sized ceiling, verdict + row, bundle content hash.
  - [x] Re-run `tests/test_dogfood_plan.py tests/test_dogfood_proof.py`; `git diff` both test files and state
        that no assertion was weakened.
  - [x] If `unit_count` drops below 3 — **HALT and report**; do not touch the assertion.

- [x] **Task 5 — Release infrastructure (AC2, AC3, AC5).**
  - [x] Add the release workflow. Declare trigger + permissions. Do not claim it has run.
  - [x] Implement the E1–E6 enumeration in one named place + the fail-on-unenumerated test.
  - [x] Record the distribution target with its four AC3 elements. **Measure the repository's visibility
        before writing the authentication sentence.**

- [x] **Task 6 — Build and PROVE the artifact (AC4, AC5b).**
  - [x] `pip install flit_core build` (⚠️ it is **not** installed here — `ModuleNotFoundError`), then build
        sdist + wheel. Record filenames.
  - [x] Fresh venv, install the **wheel**, and run the four AC4 probes from a directory that is not this repo.
  - [x] **Paste the full file listing of both artifacts.** Then reconcile `README.md` against it.

- [x] **Task 7 — `action.yml` (AC10).**
  - [x] Give exit `1` its own arm; enumerate `{0,2,3,1,other}` with the catch-all as a failure token.
  - [x] Update the `outputs` descriptions. Leave `strict: "false"` and record why.

- [x] **Task 8 — `CHANGELOG.md` + `README.md` (AC6, AC5b, AC12).**
  - [x] Turn `## Unreleased` into the released version heading with its date.
  - [x] Rewrite the `:7-16` honesty preamble to what is **now** true, bounded by AC2's evidence rule.
  - [x] Update `TC-ArgusAgent-DOCS-001-01`; close or explicitly defer `DF-8-4-B` (D12).
  - [x] Add the AC12 enumerated release-surface guard.

- [x] **Task 9 — Ledger (AC14), append-only.**
  - [x] Re-read `deferred-work.md` immediately before writing. Append one dated section. Rewrite nothing.
  - [x] Give every id in AC14's table its disposition + closing evidence.
  - [x] Name the entries that have **no owner** once this story closes.

- [x] **Task 10 — Fences, H0, and whole-system proof (AC15, AC16).**
  - [x] `git status --porcelain` **and** `git diff --stat` against the AC15 fence list.
  - [x] Full suite + mypy + line counts, pasted.
  - [x] **`git add` THIS STORY FILE** — it is currently `??` and is not gitignored. Confirm that
        `git status --porcelain` shows no `??` under `_bmad-output/design-artifacts/ArgusAgent/` other than
        the orchestrator's `bmad-dev-loop-pack/`. This is AI-E8-1's exact recurrence class, at the last
        opportunity anyone will have to catch it.
  - [x] State H0's unowned status and that this story did not file H1–H4.

### Review Findings

> **Code review — iteration 1, 2026-08-09.** Adversarial review (Blind Hunter / Edge Case Hunter /
> Acceptance Auditor) against the uncommitted working tree vs `7be90f7`. **Verdict: FAIL** — four
> unresolved Medium findings. Everything below was re-measured by the reviewer, not read off this
> document.
>
> **What the reviewer independently confirmed as TRUE** (so the next dev does not redo it):
> suite **1185 passed / 0 failed / 0 skipped**, exit `0`, progress census `Counter({'.': 1185})`;
> `python -m mypy argus` → **71 source files, clean**; no `argus/**` file over 1200 lines
> (`pipeline.py` **1199 untouched**, `partition_plan.py` 706, `proof_run.py` 679, `proof_render.py` 447,
> `proof_types.py` 207). **The PURE MOVE claim holds**: an AST-level comparison of every top-level symbol
> in `git show 7be90f7:argus/dogfood/proof_run.py` against the post-split union of the three modules found
> **0 symbols missing**, 27 AST-identical, and exactly 4 semantic deltas — all of them mandated or
> disclosed (`DOGFOOD_ArgusAgent_VERSION = _ARGUS_VERSION`, `_GENERATOR_MODULE`, the
> `render_proof_markdown` banner line, the `DogfoodProofError` message) — plus 2 docstring-only deltas.
> `__all__` is byte-for-byte the same 17 names in the same order, every name resolves, and
> `proof_run.DogfoodProofRun is proof_types.DogfoodProofRun`. `DOGFOOD_EXTERNALIZATION_GUARD` is
> byte-identical to HEAD. **All three dogfood artifacts re-render BYTE-IDENTICAL** to the committed copies
> (proof 10013/10013 bytes) — they were generated, not hand-edited. The moved figures are measured truth:
> 71 files / 18418 LOC / 3 units / `085854c90586`·`477ef77d7b65`·`bde14bbf3bcf` / 355 credits / ceiling
> **443** / headroom 88. `DOGFOOD_BUDGET_CEILING = 843` frozen; `protocol_cleared` never `True`;
> `grep -rn "minions_core" argus/ --include=*.py` returns exactly the two `minions_llm_adapter.py` decoys;
> `deferred-work.md` is append-only (+287 / −0); `tests/test_dogfood_plan.py` has an **empty** diff; the
> `test_release_note.py` edits **strengthen** `-01`/`-07` rather than weaken them; the fence list is clean
> apart from the two disclosed docstring-only carve-outs (`store/envelope.py`, `verdict/prosecutor.py`),
> both containing zero executable change.
>
> **On DF-9-2-A (the reviewer was asked to scrutinise this hardest): the deferral is JUDGED DEFENSIBLE.**
> The reviewer reproduced the defect independently by copying `argus/` into an isolated tree with no
> sibling `tests/` and importing every module in a clean subprocess. `argus/precision/replay_harness.py:87-91`
> unconditionally `sys.path`-inserts `<parents[2]>/tests/cartridges` and imports `_registry`; the identical
> import exists at `7be90f7`, so it is genuinely pre-existing and the split neither created nor widened it.
> `argus/precision/**` is fenced by this story's own AC15 and no fix exists outside that fence. The
> consumer contract (IN-1/IN-3 = `argus audit`) imports and runs from the distribution, the disclosure is
> prominent (a README callout inside the install section, a dedicated CHANGELOG packaging section) and it
> is pinned in both directions by `TC-ArgusAgent-RELEASE-001-11`. **Filing rather than fixing is the right
> call — but the numbers in that disclosure are wrong; see R1.**

- [x] [Review][Patch] **[Med] The published import figure is a stale pre-split denominator, and it contradicts a correct figure five lines away** [`CHANGELOG.md:110`, `README.md:92`, `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (DF-9-2-A body)] — All three say *"65 of the 69 shipped modules import"*. Re-measured by the reviewer (isolated copy of `argus/` with no sibling `tests/`, one clean subprocess per module): **66 of 71 import, 5 fail**. `69` is the pre-split module count; the tree has been 71 since AC8 landed, which this delta itself states correctly at `CHANGELOG.md:105` (*"the wheel holds 71 modules"*), in the story's verbatim wheel listing (71 `argus/**` entries + 5 `dist-info` = 76, verified exact against `git ls-files argus`), and in mypy's own 71. The prose also names **four** broken modules while the committed pin `_NOT_IMPORTABLE_FROM_DISTRIBUTION` (`tests/test_release_preflight.py:260-268`) lists **five** — `argus/precision/replay_harness.py` is missing from every prose site. **Rule violated:** Epic-8 retro learning #6 / this story's AC13 (*"do not restate a figure you did not re-derive; a number that appears in a published artifact because it was already there is still a number this story published"*) and single-source-of-truth. This is a wrong measured figure in the consumer-facing release contract of the story whose epic exists to delete exactly that. **Fix:** replace with *"66 of the 71 shipped modules import; five module files do not — `argus/precision/__init__.py`, `argus/precision/replay_harness.py`, `argus/dogfood/proof_types.py`, `argus/dogfood/proof_render.py`, `argus/dogfood/proof_run.py`"* at all three sites, and correct the same figure in Completion Note 7 of this story. Do not re-round: state the five files, matching the test pin.

- [x] [Review][Patch] **[Med] The headline install command cannot resolve — tag `v0.1.0` does not exist, and the README sentence introducing it contradicts the command it introduces** [`README.md:33-41`, `CHANGELOG.md:12-16`] — `git tag -l` is empty and nothing has been pushed, so `pip install "argus-agent @ git+https://github.com/Inan15/Agent-Argus.git@v0.1.0"` fails for every reader today. `README.md:36-38` says *"Until a tag is pushed, the resolvable reference is the repository itself:"* and then gives a **tag-pinned** command — the sentence and the code block state different things. `CHANGELOG.md` asserts *"The distribution is therefore **resolvable by the VCS pin below**"*, an affirmative capability claim that has not been exercised by anyone; the mitigating *"no tag exists in this repository yet"* is four paragraphs away and not adjacent to the command. **Rule violated:** AC2's evidence rule / **D13** (*"a committed workflow is a committed workflow; a published release is a URL — write the smaller true sentence"*). **Fix:** add one sentence immediately under **both** code blocks — *"⚠️ Tag `v0.1.0` has not been created or pushed (`git tag -l` is empty at this commit); this command will not resolve until an operator performs the prepared-not-executed steps in the story record"* — and change *"is therefore resolvable by the VCS pin below"* to *"will be resolvable by the VCS pin below once that tag is created and pushed"*. Fix the README lead-in so it stops promising a repo-ref and delivering a tag-ref.

- [x] [Review][Patch] **[Med] E4 is structurally inert in the shipped workflow, and the preflight prints `ok` for a check it could not perform** [`.github/workflows/release.yml:88-91`, `scripts/release_preflight.py:321-340,396-399`] — The pre-build preflight step sets **no `GH_TOKEN`** (only the final `gh release create` step does), so `gh release list` exits non-zero on authentication, `_published_release_tags()` swallows it and returns `()`, and `check_e4_release_already_published` can never fire in CI. The run then prints `E4  the version already has a published artifact for that target  ok` into the workflow log — a **publication surface** — asserting a clearance it was structurally unable to evaluate. **Rule violated:** AC5 (*"the workflow behaves explicitly and refuses"* for every enumerated member) and this repo's own standard that a guard which cannot observe is not a guard; the printed `ok` is an unsupported claim of the exact class Epic 8 exists to remove. **Fix:** (a) add `env:\n  GH_TOKEN: ${{ github.token }}` to the pre-build preflight step; (b) make `_published_release_tags` return `None` for *"could not ask"* as distinct from `()` for *"asked, none exist"*, and have `main()` print `UNKNOWN` (or refuse) rather than `ok` for E4 in that case. `gh release create` still backstops the actual overwrite, so no artifact is at risk — the defect is the false clearance, not a lost refusal.

- [x] [Review][Patch] **[Med] Script-injection surface in the new release workflow: untrusted input interpolated into `run:` bodies on a job holding `contents: write`** [`.github/workflows/release.yml:71-75`, `:88-91`, `:97`, `:118-136`] — `TAG="${{ inputs.tag || github.ref_name }}"` and every later `${{ steps.resolve.outputs.tag }}` are expanded by the runner **into the shell source text** before `bash` sees it. `workflow_dispatch.inputs.tag` is free-form (the tag-push trigger is constrained by the `v[0-9]+.[0-9]+.[0-9]+` filter, the dispatch path is not), so a dispatch with a crafted value executes arbitrary commands in a job with `contents: write` and `github.token` in scope. This is GitHub's documented script-injection anti-pattern, and it is **new supply-chain surface** in the highest-value workflow in the repository. **Fix:** bind through the environment and quote — `env:\n  TAG: ${{ inputs.tag || github.ref_name }}` then `"$TAG"` in every `run:` — and validate the value against `release_preflight._VERSION_TAG` (`^v\d+\.\d+\.\d+$`) as the **first** step, before it reaches any other command. The validator already exists; it is simply run too late to protect the shell.

- [x] [Review][Patch] **[Low] Third-party actions are pinned to mutable major tags on a `contents: write` job** [`.github/workflows/release.yml:53`, `:62`, `:105`] — `actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4`. A moved tag silently changes what runs inside the release job. **Rule:** supply-chain pinning for a publishing workflow. **Fix:** pin each to a full commit SHA with a trailing `# v4.x.y` comment. Non-blocking on its own; bundle it with the R4 hardening pass.

- [x] [Review][Patch] **[Low] `E2` is registered and phase-assigned but unreachable in the shipped workflow, which weakens `-02`'s stated premise** [`scripts/release_preflight.py:145-158`, `.github/workflows/release.yml:88-91`] — `check_e2_tag_already_exists` only fires when `creating_tag=True`, and the workflow never passes `--creating-tag` (neither trigger creates a tag). The module docstring discloses this and the reasoning is sound, so it is a knowing design choice, not a hidden gap — but `TC-ArgusAgent-RELEASE-001-02`'s premise (*"a handled case that never runs is not handled"*) is not actually discharged for E2. **Fix:** either pass `--creating-tag` on the `workflow_dispatch` path, or record in `EDGE_CASE_DESCRIPTIONS["E2"]` (and in `-02`'s docstring) that E2 is a **local-tooling** guard with no CI reachability, so the enumeration does not read as more active than it is.

- [x] [Review][Patch] **[Low] The over-claim denial filter is broad enough to exempt a genuine affirmative claim** [`tests/test_release_surface_honesty.py:125-143`] — `_DENIAL_MARKERS` contains bare `"no "` and `"not "`, so any sentence containing either word anywhere is exempted from `-17`; e.g. *"Argus has been externally validated with no exceptions"* would pass. `-17b` is a real positive control and the docstring discloses that the splitter errs toward larger units, so this is a disclosed trade-off rather than an escape. **Fix (cheap):** require the denial marker to precede the banned phrase within the sentence (index comparison), and add the sentence above to `-17b` as a second negative control.

- [x] [Review][Defer] **[Low] Pre-existing shell interpolation of a composite-action input in `action.yml`** [`action.yml:127`] — `if [ "${{ inputs.strict }}" = "true" ]` expands a consumer-supplied action input into shell source. Untouched by this story (the arm above it was rewritten; this line is byte-identical to HEAD `7be90f7`), so it is out of the delta — deferred, pre-existing. Fix when `action.yml` is next opened: bind `inputs.strict` through `env:` and compare `"$STRICT"`.

> **Code review — iteration 2, 2026-08-09.** Adversarial re-review of the fix round against
> the uncommitted working tree vs `7be90f7`, adjudicating R1–R7 from iteration 1 on the
> merits and independently re-verifying every load-bearing claim rather than trusting the
> dev's record. **Verdict: PASS.** No unresolved Medium/High findings; the single remaining
> item is a disclosed, non-blocking Low.
>
> **Independently re-verified by this reviewer, not read off the story:**
> `PYTHONIOENCODING=utf-8 python -m pytest tests/ -q` → exit `0`, progress census
> `Counter({'.': 1192})` — **1192 passed / 0 failed / 0 skipped**, matching the claimed
> baseline 1185 → 1192 (+7, 0 removed/skipped). `python -m mypy argus` →
> *Success: no issues found in 71 source files*; `python -m mypy scripts/release_preflight.py`
> → clean. `git diff --cached --stat -- argus/` touches exactly the 11 files the record
> claims (2 new: `proof_render.py`/`proof_types.py`); `argus/pipeline.py` untouched at 1199.
> `git diff --cached --numstat -- deferred-work.md` → `323 0`, confirmed append-only with
> zero `-` lines in the full diff. `git tag -l` empty, `git log --all` shows no new commits,
> `git branch -r` shows only `origin/master` — no tag, push or publication occurred.
>
> **R1 (import census) — CLOSED, verified by an independent method.** Rather than trust the
> dev's wheel-extraction re-measurement, this reviewer ran the committed
> `_modules_reaching("_registry")` static AST-walk from `tests/test_release_preflight.py`
> directly and got the identical 5-file set
> (`argus/precision/__init__.py`, `argus/precision/replay_harness.py`,
> `argus/dogfood/proof_types.py`, `argus/dogfood/proof_render.py`, `argus/dogfood/proof_run.py`),
> and confirmed the propagation is real: `proof_types.py:33` does
> `from argus.precision.replay_harness import MatchKey` directly, and `proof_render.py`
> imports `proof_types`, so the transitive closure is not an artifact of the walk. The wheel
> itself was independently opened (`zipfile`) and confirmed 76 entries = 71 `argus/**` `.py` +
> 5 `dist-info`, 0 non-`.py`. All five corrected sites were checked on disk — `README.md:102`,
> `CHANGELOG.md:117`, `deferred-work.md:1159`, `tests/test_release_preflight.py:227` — and all
> five state "66 of the 71" and enumerate the same five files.
>
> **R2 (unresolvable tag) — CLOSED.** `README.md:43-48` and `CHANGELOG.md:18-21` each carry a
> ⚠️ immediately under their code block stating the tag does not exist and the capability is
> prepared, not exercised; the `Resolving argus-agent` table's dependency-string cell
> (`CHANGELOG.md:60`) carries the same warning inline. `git tag -l` re-confirmed empty by this
> reviewer.
>
> **R3 (E4 false clearance) — CLOSED, read in full.** `scripts/release_preflight.py`'s
> `_published_release_tags` returns `None` for all three "could not ask" paths (`gh` absent,
> non-zero exit, unparseable JSON) and `()` only for a genuine empty list; `check_e4_*` returns
> `Unevaluable` on `None`; `main()` prints `UNKNOWN` and a "not a clearance" sentence instead of
> `ok`, and is NOT a hard failure (correct: absence of `gh` locally must not block a release
> `gh release create --verify-tag` still backstops). `.github/workflows/release.yml:123-124`
> confirmed `GH_TOKEN: ${{ github.token }}` on the pre-build preflight step, no `secrets.`
> anywhere in the file.
>
> **R4 (script injection) — CLOSED, verified exhaustively, not sampled.** This reviewer ran the
> committed `_run_block_bodies` extractor against the real `release.yml` independently: **7**
> `run:` bodies found, **0** contain `${{`. A `grep -n '\${{'` over the whole file confirms
> every one of the 9 occurrences sits in a `with:`/`env:`/`ref:` key (action input or env
> binding), never inside a `run:` script. The tag is validated via `--phase validate-tag`
> against `_VERSION_TAG` in the FIRST step, before `pre-build`/`post-build`/`gh release create`
> (index-order checked in the file), and `set -euo pipefail` is present on every multi-line
> block. `ref: ${{ inputs.tag || github.ref }}` on `actions/checkout` is correctly an action
> input, not shell source — not an injection surface.
>
> **R5 (mutable action pins) — CLOSED, cross-checked against the live GitHub API (read-only).**
> `GET /repos/actions/checkout/git/ref/tags/v4.4.0` → object sha
> `11d5960a326750d5838078e36cf38b85af677262` (exact match); `.../setup-python/.../tags/v5.6.0` →
> `a26af69be951a213d495a4c3e4e4022e16d87065` (exact match);
> `.../upload-artifact/.../tags/v4.6.2` → `ea165f8d65b6e75b540449e92b4886f43607fa02` (exact
> match). All three pins are correct.
>
> **R6 (E2 unreachable) — CLOSED, argument accepted on the merits.** `release.yml:63`'s own
> `workflow_dispatch.inputs.tag` description reads *"must already exist and point at the commit
> you dispatch from"* — so passing `--creating-tag` on that path would indeed assert something
> false about the run. `CI_UNREACHABLE = {"E2": …}` is real, the report prints
> `(not reachable from this workflow)`, and the workflow header states
> *"E2 is not reachable from this workflow"* verbatim, matching the pinning test.
>
> **R7 (denial filter escape) — CLOSED, argument accepted and mechanically confirmed.**
> Re-implemented the "pure precede" alternative by hand against
> *"the gate is cleared only by the human tp/fp adjudication…"*: `claim_at` for `"gate is
> cleared"` is `4`; a precede-only rule (no `_QUALIFIER_MARKERS` class) finds no denial marker
> before index 4 and **would** flag this honest sentence — the dev's rejection of a pure
> precede-rule is correct, not just asserted. The actual two-class rule (`_DENIAL_MARKERS` must
> precede, `_QUALIFIER_MARKERS` may appear anywhere) correctly leaves it unflagged, and `-17b`'s
> three trailing-negation positive controls (including the review's own "with no exceptions"
> sentence) all still catch a genuine over-claim.
>
> **AC12 registration re-checked**: `_RELEASE_SURFACES` in `test_release_surface_honesty.py`
> enumerates exactly `README.md`, `CHANGELOG.md`, `action.yml`,
> `.github/workflows/release.yml`, and the three `minions-dogfood-*.md` artifacts —
> matching AC12's named set, with `-18` failing on any unregistered surface found by glob.
>
> **Remaining, disclosed and non-blocking:**

- [x] [Review][Defer] **[Low] Pre-existing shell interpolation of a composite-action input in `action.yml` — still deferred** [`action.yml:127`] — Unchanged since iteration 1; re-confirmed byte-identical to HEAD `7be90f7` in this round's diff too. No new instance was introduced by the R1–R7 fixes. Fix when `action.yml` is next opened.

---

## Dev Notes

### LOCKED decisions taken at story design — with rationale (record these; do not re-litigate)

**D1 — The released version is `0.1.0`. It is NOT bumped.**
Considered and rejected: bumping to `0.2.0`/`1.0.0` to "mark the amendment". Rejected on three measured
grounds. (a) `epics.md:1669-1670` writes the AC as *"**Given** `argus-agent` is at version `0.1.0` **Then**
the released version is pinned and published"* — the epic pins the value. (b) `tests/test_release_note.py:787`
(`TC-ArgusAgent-DOCS-001-10`) asserts `argus.__version__ == "0.1.0"`; keeping `0.1.0` leaves a deliberate pin
untouched instead of editing an assertion to accommodate a change nothing required. (c) `__version__` is the
default `argus_version` on **every** envelope (`store/envelope.py:99`), so bumping changes the **bytes** of
every persisted `.argus/` artifact for no requirement — see the correction in §A about what it does and does
not change. `__status__` stays `"experimental"`: the public Python API is genuinely not stable, and the CLI
wire contract is separately frozen.

**D2 — Distribution target: a GitHub Release carrying sdist + wheel for tag `v0.1.0`, and the
`git+https://github.com/Inan15/Agent-Argus.git@v0.1.0` VCS pin as the documented, explicitly INTERIM consumer
reference. PyPI is NOT attempted by this story.**
Rationale: (a) publishing a name+version to PyPI is **irreversible** — a released version can never be
replaced — which is precisely the class of decision a story author must not take unilaterally; (b) it needs a
credential this story cannot prove exists and this repo's CI cannot verify from the working tree; (c)
`epics.md:1666-1667` explicitly sanctions the VCS pin *provided* it is marked interim with an exit condition,
which AC3 requires; (d) the remote is real and measured (`https://github.com/Inan15/Agent-Argus.git`), so the
pin is genuinely resolvable rather than aspirational. **The exit condition must be named**, not left to
silence — an "interim" with no stated end is a permanent state wearing a temporary label. **If the operator
wants PyPI, that is an operator decision taken with credentials in hand; escalate rather than assume.**

**D3 — DF-8-5-A is FIXED here, not deferred.** Operator decision, 2026-08-08. It is the only 🟠 that is
*consumer-visible at release*: publishing `0.1.0` while the signed evidence bundle asserts `1.43.0` is the
release story committing the epic's own defect class, inside signed evidence. The package's own front door
already forbids the pattern in writing (`argus/__init__.py:56-58`); this is bringing one call site up to a
rule the codebase already states.

**D4 — DF-8-5-D's extraction is performed HERE, and the reason is the LEDGER, not the fence.**
Measured: the DF-8-5-A fix is ~+1 line (1196 → ~1197 ≤ 1200), so NFR-M1 does **not** force it. What forces it
is (a) `DF-8-5-D`'s `target_story` — *"the first story that edits `argus/dogfood/proof_run.py` for any
reason"* — which this story is; (b) **AI-E8-3**, which asks for it as a named pre-condition rather than an
edit-time discovery; and (c) the fact that **this is the last story in the plan**, so "defer it" means "drop
it" and §5 of the retro proved that is what happens. **The decisive efficiency argument:** DF-8-5-A alone
already forces a proof regeneration (the bundle hash it publishes moves), and DF-8-5-D alone forces a
three-artifact regeneration. Doing them **together costs ONE regeneration**; doing them apart costs two, over
rot checks with a measured history of four consecutive red commits (`DF-8-5-B`).

**D5 — The extraction shape is the one `DF-8-5-D` corrected itself to: two siblings plus a re-export shim.**
`argus/dogfood/proof_types.py` (the five frozen dataclasses) + `argus/dogfood/proof_render.py` (the pure
renderers), both re-exported from `proof_run.py`. The circular-import blocker recorded in earlier notes was
corrected **in the ledger entry itself** — moving the dataclasses to a sibling and re-exporting preserves the
public import surface with no cycle. Do **not** "solve" a cycle that the ledger already established does not
exist; and do **not** change `__all__`.

**D6 — Regenerate LAST, once.** Every artifact figure depends on `argus/**` bytes. Editing any `argus/`
module after regenerating changes `total_loc`, may change partition membership and therefore the sha256
`partition_id`s, and re-breaks the rot check you just turned green. Story 8.5 paid for this three times.
**Source edits → tests → stage → regenerate → re-run tests.**

**D7 — `DOGFOOD_BUDGET_CEILING = 843` stays frozen.** Story 8.5's own D7 considered and rejected re-pointing
it at the live `sized_ceiling`: it would edit `TC-ArgusAgent-DOGFOOD-001-19`'s pin and the rot check's `843`
assertion, in a story with no mandate over the budget contract, and would make a frozen historical execution
parameter float. That reasoning is unchanged by this story. The artifact already states both numbers and
whether the run fits under each.

**D8 — `DF-8-5-C`'s `N=0` is republished unchanged, and said so out loud (AC13).** Its `target_story` names
the 6.5/6.6 precision surface *after* the human `DF-7-2-A` adjudication, which has not happened. Fixing it
here would touch a surface no AC owns and would require its own regeneration. The figure **understates**, so
it cannot make a gate look cleared. **The honest act is to name it in the record, not to fix it quietly or
reprint it silently.**

**D9 — The two `minions_core` references in `argus/audit/minions_llm_adapter.py` are NOT swept.** They are
Story 9.1's true negative statements (*"zero dependency on `minions_core`"*). Deleting them would delete the
documentation of RS-1/IN-2. RS-4b's own text excludes this file. A naive `grep`-and-delete sweep gets this
wrong, which is why the AC11 guard is an **allowlist**, not a zero-count assertion.

**D10 — Bare-word "Minions" subject claims: `argus/dogfood/**` only.** Measured 44 occurrences across 17
files under `argus/**`; 19 are in `dogfood/` (13 `proof_run.py`, 6 `partition_plan.py`), the modules this
story rewrites anyway, and several are now **false subject claims** of the class 8.5's AC2 deleted from the
artifacts. The remaining ~21 are historical narration in modules this story does not touch; sweeping them
would be an unbounded prose pass inside a release story, which is exactly why RS-4b was deferred out of the
delta in the first place. **Bounded here, filed for the rest.**

**D11 — `argus/pipeline.py` is FENCED. It is at 1199/1200.** `DF-8-2-A`, `DF-8-3-A` and `DF-8-3-C` all gate on
its extraction. This story does **not** perform it: it is a second unrelated restructure inside a release
story, it touches the pipeline that produces every verdict, and nothing in IN-0 requires it. **AC14 requires
you to record that those three entries are unowned after this story closes** — that is the honest outcome,
and it is materially better than performing a large risky refactor to avoid writing an uncomfortable
sentence.

**D12 — `DF-8-4-B` fires on this story and must be dispositioned.** Its `target_story` is *"the first story
after 8.5 that edits `tests/test_release_note.py` (or Epic-9 `9-2`, whichever fires first)"* — **both clauses
fire**, because AC6 must update `TC-ArgusAgent-DOCS-001-01`'s `"## Unreleased"` pin. Its suggested close is a
section-presence assertion over each `###` heading plus a bytes-example equality check. **Recommended: close
the heading half** — it is directly aligned with **AI-E8-6** (enumerate the space, fail on the unenumerated),
it is cheap, and it protects the release note at the exact moment the note becomes a released version. If you
leave any part open, say which part and why.

**D13 — The story does not claim a release it cannot evidence.** This is the whole point of the epic that
precedes it. A committed workflow is a committed workflow; a published release is a URL. AC2 permits the
first and requires evidence for the second. If the two diverge, **write the smaller true sentence.**

### Architecture patterns & constraints (non-negotiable — the AR/NFR ids a reviewer will check)

- **NFR-M1** — no source file exceeds 1200 lines; business logic stays out of entrypoints. `pipeline.py` is
  at 1199 and is fenced; the three `dogfood/` modules must each finish under the ceiling with room.
- **AR8 pure/impure master rule** — `proof_render.py` must be **pure** (no I/O, no clock, no subprocess); the
  git/snapshot/store shell stays in `proof_run.py`. The extraction is the *opportunity* to make the AR8 line
  structural instead of narrated in a docstring — say so in each module's docstring.
- **AR7 reuse-not-fork** — no second serializer, no second store reader, no forked cost model. The artifacts'
  own `REUSED`/`REUSING` narration is asserted by `TC-ArgusAgent-DOGFOOD-001-03` and `-20`; preserve it.
- **AR4 / NFR-P1 determinism** — exact `Fraction`, never `float`; no wall-clock, `uuid4`, `getpid()`, `random`
  or iteration-order reliance in any `.argus/` write path. A release workflow may use a clock; the **package**
  may not.
- **AR10 typed failure** — a failure surfaces as a typed exception or a finding, never a bare traceback. This
  is *why* exit `1` is distinct from `2`/`3`, and therefore why AC10 exists.
- **NFR-S1 / NFR-S3 containment** — no source byte, no secret value, no absolute host path in any artifact.
  A release workflow's logs are a **new** publication surface: do not echo a repository path or a token.
- **NFR-D3 / NFR-A1 envelope contract** — content hash over the **payload only**; `run_id` / `created_at`
  excluded; `prev_hash` chaining; one `EnvelopeWriter`. §A's envelope-vs-payload distinction follows directly
  from this and is the reason AC7's blast radius is bounded to the evidence bundle.
- **NFR-M2 additive-only schema evolution** — if anything you touch would change a `schema_version`, stop:
  nothing in IN-0 requires it.
- **RS-1** — all work lands in `argus/` in this repo. No Minions-repo change of any kind.

### Traps a previous story already paid for (Epic 1–8.5 learnings that apply here)

1. **Measure in place, on the real tree.** Both generators read `git ls-files` and working-tree bytes; a
   scratch copy has neither the right index nor the right content. 8.1 lost a review round to this. Where this
   context used a copy (§F), it is labelled a **simulation** and is not offered as truth.
2. **Regenerate LAST, and stage BEFORE regenerating.** §F, item 4: an untracked module is invisible to the
   partition plan. 8.5 re-derived three times because it did not sequence this.
3. **`git status --porcelain`, never `git diff` alone, at every fence check.** Epic 8's third recurrence of the
   untracked-evidence class was missed precisely because `git diff --stat` and `git diff -U0` cannot see an
   untracked file (**AI-E8-2**).
4. **RED-first, and paste the failure.** Reviewers on this project reconstruct the pre-fix implementation and
   **inject it at runtime** rather than reading the Dev record — invented in 8.2, reused in 8.3/8.4/8.5, and it
   never edits a source file. Assume it will be done to you. An assertion never shown to fail is not evidence.
5. **An AC that says "every" needs a test that enumerates and rejects the unenumerated.** All five Epic-8
   stories shipped a guard narrower than its own AC. AC5, AC11, AC12 and AC15 are written this way on purpose;
   discharging them with one sample is a breach, not a pass.
6. **Do not restate a figure you did not re-derive.** Four Epic-8 escapes were figures the author believed were
   already established, including one carried in a Story Context (`50/65` vs the real `48/10` — right numbers,
   wrong population). Every number in §A–§H of this document is re-derivable; re-derive it.
7. **Windows console.** Run everything as `PYTHONIOENCODING=utf-8 python -m pytest tests/ -q`. The artifacts
   contain `≥`, `→`, `·`, `🔴`; cp1252 stdout will mangle or crash on them. Write every file with
   `encoding="utf-8"`. 8.4's iteration-2 review reproduced a real `'charmap' codec` failure that turned a
   completed audit into an exit `1`.
8. **The `dogfood_proof` fixture is module-scoped and its run takes roughly two minutes.** Add end-to-end
   assertions to tests that already take that fixture rather than creating new module-scoped runs.
9. **Don't fix what you were told not to fix.** 8.4 shipped clean partly by fencing four deferred items and
   saying so. `DF-8-5-C`, `DF-8-4-C`, `DF-8-4-D`, `DF-8-2-A`, `DF-8-3-A`, `DF-8-3-C` are file-and-leave here.

### Runtime, library and toolchain specifics (verified on this machine, 2026-08-08)

- **Python** `3.11.15 (main, Jun 23 2026)` in the repo `.venv`; a separate `pip 25.0.1` sits on Python 3.12 —
  be explicit about which interpreter you invoke.
- **`flit_core` is NOT installed** (`ModuleNotFoundError: No module named 'flit_core'`), and neither is
  `build`. Installing them fetches from the network; that is fine — **NFR-D2's no-network rule constrains the
  audit, not the packaging toolchain** — but say which you installed and at what version.
- **Build backend:** `flit_core >=3.2,<4` / `flit_core.buildapi`, `[tool.flit.module] name = "argus"`.
- **`tree-sitter` upper bound `<0.26` is load-bearing.** `pyproject.toml:18-24` records that on `0.26.0` the
  cartridge self-audit flips `NOT_READY_FOR_RELEASE → RELEASE_READY` — a false-negative verdict from an
  assurance tool. **Do not widen it in a release story**, and do not "modernise" the pins while you are in the
  file.
- **`requires-python = ">=3.10"`**; `audit-ci.yml` matrixes 3.10/3.11/3.12; `action.yml` pins 3.11. Whatever
  Python your release workflow builds on, the wheel must remain the pure-Python, version-agnostic artifact the
  metadata promises.

### Latest technical information — release toolchain, researched 2026-08-08

> Researched because this story stands up a **new** kind of surface for this project (a build + publish
> pipeline) and nothing in the repo demonstrates one. Every claim below is from current upstream
> documentation, **not** from measurement on this machine — treat it as guidance to verify, not as a figure.

**1. Flit packages the MODULE, and `include`/`exclude` only reach the sdist.** Flit's documented behaviour:
a **wheel** contains the package contents (including non-Python data files, excluding `.pyc`) plus wheel
metadata; an **sdist** additionally contains `pyproject.toml`, the readme, the license, and any declared
external-data folder. `[tool.flit.sdist]` `include`/`exclude` control the **sdist only** — they do **not**
add files to a wheel. With `[tool.flit.module] name = "argus"`, the top-level siblings `audit/`, `phases/`,
`adapters/` and `templates/` are therefore expected to be in **neither** artifact by default. **This is
documentation, not measurement — AC4 requires you to build and list.** If the listing confirms it, AC5b's
honest resolution is to state in the README what the distribution provides versus what the git repository
provides; adding those trees to the distribution is a packaging redesign that **IN-0 does not require** —
Minions needs the `argus audit` CLI, which is entirely inside `argus/`.

**2. If PyPI is ever chosen (D2's exit condition), the current correct shape is Trusted Publishing, not a
token.** `pypa/gh-action-pypi-publish` supports OIDC trusted publishing: give the publishing job
`permissions: id-token: write` and **omit** `username`/`password` entirely — no `PYPI_API_TOKEN` secret is
created or stored. From `v1.11.0` the action also generates and uploads **PEP 740 attestations** by default,
signed via Sigstore with the same GitHub OIDC identity, so provenance and authentication share one identity.
**Known limitation to record if you write the exit condition:** trusted publishing **cannot** be used from
inside a *reusable* workflow — the publish step must live in a non-reusable workflow. **State this as the
named exit path in AC3's item 4** so the interim VCS pin has a concrete, current route out rather than a
vague intention.

**3. `python -m build` is the neutral front end.** It reads `[build-system] requires` and provisions
`flit_core` in an isolated environment, producing both sdist and wheel — which is what AC5's **E6** (refuse a
partial release) is written against. Note it needs network access to provision the backend; that does not
violate **NFR-D2**, which constrains the *audit*, not the packaging toolchain.

**4. Attaching artifacts to a GitHub Release** is the D2 default and needs only `permissions: contents: write`
on the release job — no external credential — which is precisely why it was chosen over PyPI as the
reversible option a story author may take without an operator in the room.

Sources: [PyPA — Publishing package distribution releases using GitHub Actions](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/) ·
[pypa/gh-action-pypi-publish](https://github.com/pypa/gh-action-pypi-publish) ·
[PyPI Docs — Publishing with a Trusted Publisher](https://docs.pypi.org/trusted-publishers/using-a-publisher/) ·
[GitHub Docs — Configuring OpenID Connect in PyPI](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-pypi) ·
[Flit — The pyproject.toml config file](https://flit.pypa.io/en/stable/pyproject_toml.html)

### Recent git context

`7be90f7` *feat(dogfood,verdict): complete Epic 8 — the honest verdict* (the 8.5 delta + both previously
untracked evidence files) · `be9d744` *feat(verdict,reports,packaging): land Epic 8 stories 8.1-8.4 and Epic 9
story 9.1* · `9109e16` *docs(readiness)* · `d8ba5ad` *docs(prd): amend FR16/FR4* · `faeefd9` *fix(verdict): stop
reporting a block when nothing was found*. The working tree is clean apart from `?? bmad-dev-loop-pack/`.
`git diff HEAD` is therefore **empty** and is not your measuring instrument — import and call the shipped
functions instead.

### Project Structure Notes

- New modules land at `argus/dogfood/proof_types.py` and `argus/dogfood/proof_render.py`, matching the
  existing `snake_case.py` sub-package convention. Two new modules take `mypy`'s source count from 69 to 71.
- New tests extend the existing modules rather than creating new ones where a module-scoped fixture already
  exists. Dogfood test ids continue at `TC-ArgusAgent-DOGFOOD-001-37`; docs/release-note ids continue in the
  `TC-ArgusAgent-DOCS-001-*` series (14 upward — `-01`…`-13` are taken).
- Packaging/release files live at the repository root and under `.github/workflows/`, matching the existing
  layout (`pyproject.toml`, `action.yml`, `install.sh`, `install.ps1`, `uninstall.sh`).
- ⚠️ **`_bmad-output/reports/` is gitignored** (`.gitignore:20`), while `_bmad-output/audit-reports/` **is
  tracked** (measured: `git ls-files` returns `coverage-ledger.md` and `final-verdict.md` there). If you
  regenerate verdict reports for any reason, only the tracked directory is published evidence. This story does
  not require regenerating either.

### Variance from the epic, recorded

`epics.md:1653-1678` gives Story 9.2 five acceptance criteria, all release mechanics. This story carries
**sixteen**. The eleven additions are: **AC1** (version consistency), **AC5b** (prose matches the measured
artifact), **AC6** (CHANGELOG becomes a version), **AC7** (`DF-8-5-A`), **AC8** (`DF-8-5-D`), **AC9** (the
regeneration cascade), **AC10** (`DF-8-4-A`), **AC11** (`RS-4b`), **AC12** (SD-2 no-over-claim), **AC13**
(knowingly-republished figures), **AC14** (ledger dispositions) and **AC16** (H0 not absorbed) — with the
epic's original five preserved as **AC2** (release workflow), **AC3** (distribution target + access), **AC1**
(version pinned), **AC4** (clean-environment proof) and **AC5** (edge cases).

**Authority for the variance:** operator decision of 2026-08-08 acting on the Epic-8 retrospective's **SD-1**
and **AI-E8-4**, which recommended re-contexting 9.2 to name the three ledger items targeting it and the
`DF-8-5-A → DF-8-5-D → artifact-regeneration` chain, and explicitly noted that applying such a re-scope
*"exceeds a retrospective's authority."* The operator ruled: **absorb into one story, do not split.**

**`epics.md` is NOT edited by this story.** The variance is recorded here and in the Dev Agent Record so the
plan document remains the frozen record of what was planned, and this file records what was decided.

**Where the retrospective's narrative and this context's measurements disagree, the measurements are recorded
and the disagreement is named** — see §G (the NFR-M1 fence does not force the extraction; the ledger does) and
§F (the simulated extraction held `unit_count` at 3 and moved a `partition_id`, rather than dropping to 2).
Neither correction reduces the work; both change what the dev should expect to see, which is the point.

### References

- **Epic + ACs:** `_bmad-output/design-artifacts/ArgusAgent/epics.md:1618-1678` (Epic 9, Stories 9.1/9.2);
  `:1232-1256` (IN-0…IN-5 + the IN-4 architectural constraint); `:1190-1230` (RS-1…RS-4b);
  `:1682-1757` (Minions-Repo Handoff H0–H4); `:1365-1376` (assumption audit A1/A5/A7).
- **Retrospective:** `epic-8-retro-2026-08-08.md` §6 (next-epic preview + the three-item table + the chained
  constraint), §7 (AI-E8-1…AI-E8-10), §8 (critical path), §9 (**SD-1**, **SD-2**), §10 (readiness).
- **Ledger:** `deferred-work.md:679-709` (RS-4b) · `:711-730` (DF-8-4-A) · `:755-802` (DF-8-4-B/C/D) ·
  `:841-864` (RS-4b progress note, 6-of-15 consumed) · `:866-884` (Inversion F5 re-run) · `:888-905`
  (**DF-8-5-A**) · `:907-929` (DF-8-5-B) · `:943-971` (DF-8-5-C) · `:973-1001` (**DF-8-5-D**).
- **Previous story:** `stories/9-1-argus-stops-importing-thing-it-audits.md` (IN-2/RS-1, `done` 2026-08-06 —
  the source of the two allowlisted `minions_core` references in D9);
  `stories/8-5-re-derive-proof-evidence-matches-tool.md` (the regeneration machinery, its D1–D11 locked
  decisions, and §H's list of strings the existing tests pin — **read §H before editing any renderer**);
  `stories/8-4-tell-integrators-what-changed.md` (the release note and its rot check).
- **Readiness report:** `implementation-readiness-report-2026-08-03.md` §Q7 (the *"no project-init story"*
  rationale is void post-separation; 9.2 covers release infra, the rest of the standalone baseline is unowned),
  §F5 (H0 unowned, 🔴 LIVE).
- **Change proposals:** `sprint-change-proposal-2026-08-03.md` (the FR16/FR4 amendment + repo separation that
  created Epics 8–9); `sprint-change-proposal-2026-07-28.md`.
- **Architecture:** `architecture.md` §"Implementation Patterns & Consistency Rules" (AR4/AR7/AR8/AR10/AR11,
  NFR-M1/M2, containment, error/degradation). ⚠️ **Known stale (readiness finding F10, unfixed):** §I
  *"Packaging & Deployment"* still describes the `minions[apaa]` extra and an `apaa` console script, and the
  package tree still reads `minions_core/apaa/` while omitting the shipped `reports/`, `dogfood/`, `shared/`
  and `pipeline_persist.py`. **Read it for the invariants, not for the packaging facts** — `pyproject.toml` is
  the truth there. Correcting the document is **not** in this story's scope; record it.
- **Shipped code cited above:** `argus/__init__.py:56-59` · `argus/store/envelope.py:25,57-67,74-92,99,106-107`
  · `argus/store/writer.py:74-92,110-118` · `argus/evidence/bundle.py:285-293,308-334` ·
  `argus/dogfood/proof_run.py:52-53,136,156-190,193-1196` · `argus/dogfood/partition_plan.py:452-489` ·
  `argus/index/partitioner.py:107-108` · `argus/cli.py:282-300` · `action.yml:22,26-30,44,56-66` ·
  `pyproject.toml:1-30,55-58` · `tests/test_dogfood_plan.py:175-190,250-274` ·
  `tests/test_dogfood_proof.py:154-180,223-243,642-649` · `tests/test_release_note.py:361-364,779-841`.

---

## Dev Agent Record

### Context Reference

Story context authored 2026-08-08 by the Scrum Master worker of the `bmad-dev-loop` orchestrator, at HEAD
`7be90f7`, under the operator re-scope decision recorded in §Variance from the epic. Every figure in §A–§H was
measured in place on the real working tree except §F, which is a labelled simulation over an isolated copy.

### Agent Model Used

`claude-opus-5[1m]` — BMAD `dev-story` worker of the `bmad-dev-loop` orchestrator, 2026-08-08.

### Debug Log References

Every figure below was RE-DERIVED on this working tree. Nothing was read off the story document.
**⚠️ Boundary declared by the orchestrator and honoured throughout: no push, no tag, no GitHub Release, no
PyPI upload, no API call that makes anything public.** Where an AC's literal satisfaction required one of
those, the work was completed up to that line and the AC is marked **prepared-not-executed** below.

**Baseline, captured BEFORE the first edit (Task 0).**

| Instrument | Result |
|---|---|
| `git log --oneline -1` | `7be90f7 feat(dogfood,verdict): complete Epic 8 — the honest verdict` |
| `git status --porcelain` | `M …/sprint-status.yaml` · `?? …/stories/9-2-….md` · `?? bmad-dev-loop-pack/` |
| `git tag -l` | **empty** |
| `git remote -v` | `origin https://github.com/Inan15/Agent-Argus.git` (fetch + push) |
| `pytest tests/ --tb=no -q` | **1160 passed / 0 failed / 0 skipped**, exit `0`; progress census `Counter({'.': 1160})` |
| `python -m mypy argus` | Success: no issues found in **69** source files |
| top-5 `argus/**` | `pipeline.py` 1199 · `dogfood/proof_run.py` 1196 · `dogfood/partition_plan.py` 705 · `verdict/verdict_gate.py` 668 · `index/partitioner.py` 645 |
| `grep -rn "minions_core" argus/ --include=*.py` | 11 hits / 9 files — exactly as the ledger said |

**AC7 / DF-8-5-A — RED first, through the shipped path.** An `EvidenceBundle` was built with
`argus_version=DOGFOOD_ArgusAgent_VERSION` and persisted via `persist_evidence_bundle`, then the
`.argus/state/<hash>.json` was read off disk:

```
PRE-FIX    envelope['argus_version']            = 0.1.0
           envelope['payload']['argus_version'] = 1.43.0     AGREE? = False
POST-FIX   envelope['argus_version']            = 0.1.0
           envelope['payload']['argus_version'] = 0.1.0      AGREE? = True
```

**Bundle content hash, re-derived by running the real dogfood three times** (never read off the artifact):

| stage | bundle content hash |
|---|---|
| pre-fix (HEAD `7be90f7`) | `a1e76c01cbd29241a928f71b724b4c4c01d1211e0a4ae8a6e266386f811e0c0e` |
| after the DF-8-5-A fix, before the extraction | `b3588816088920936de7a3fea17eaba747f7ad3c1af1ff93b0f4f4474acb6dc6` |
| final, after the extraction (published) | `da17b0fe19d121a4414ea542e8b9061abc73eca549aadb45b178cfc1fced89fc` |

The pre-fix value **reproduced the committed `minions-dogfood-proof.md:57` signature exactly**, which is
what makes the other two trustworthy: the instrument was validated against a known point before it was used
to measure an unknown one.

RED-first for the AC1 guards, without editing a source file (the reviewer's own technique): the `-15` AST
sweep was run over `git show 7be90f7:argus/dogfood/proof_run.py` and returned **2** semver literals with
**2 distinct values** (`1.43.0`, `0.1.0`) — so both `TC-ArgusAgent-DOCS-001-14` and `-15` would have failed
before the fix.

**AC8 / DF-8-5-D — the pure move, proven by bytes.** `render_proof_markdown` was run over the SAME
`DogfoodProofRun` before and after the extraction (the object was pickled across the change):

```
real dogfood run          9927 -> 9927 bytes   byte-identical = True
6 synthetic branch runs  55101 -> 55101 bytes  byte-identical = True
```

The six synthetic runs cover every renderer branch one real run cannot: scope present/absent, the critical
clause not-captured / not-retrieved / vacuously-satisfied / satisfied-over-non-empty / not-satisfied, the
ceiling pair with and without a live sizing, an empty decision row, an unrecorded scope prefix, and a row
with no sample locators. **One deliberate change was made AFTER that proof was captured and is disclosed
separately** — see "Two disclosed content changes" below.

**AC9 — the regeneration cascade, RED-first then green.** Before regenerating, the shipped rot-check
assertions were evaluated against the COMMITTED artifacts using the live post-edit figures:

```
-03  "Unit count: 3" in committed plan                     : True
-03  live unit 085854c90586 present in committed plan      : False
-03  live unit 477ef77d7b65 present in committed plan      : False
-03  live unit bde14bbf3bcf present in committed plan      : False
-06  sized_ceiling 443 present in committed budget plan    : False
-18  unit_count >= 3                                       : True (n=3)
```

So `-03` would have failed three ways and `-06` once. Both are green after regeneration **with
`tests/test_dogfood_plan.py` completely untouched** (`git diff` on that file is empty) — the strongest
available evidence that no assertion was weakened to reach green.

Every moved figure, before → after:

| figure | before (HEAD `7be90f7`) | after |
|---|---|---|
| `source_file_count` | 69 | **71** |
| `total_loc` | 18276 | **18418** |
| `unit_count` | 3 | **3** (never dropped — verified on the real tree, not the simulation) |
| `partition_id[:12]` | `2c0f52f60457` · `681c496d09ed` · `973f3f199d1c` | **`085854c90586` · `477ef77d7b65` · `bde14bbf3bcf`** — all three moved |
| unit shape | 9/2871 · 40/14529 · 20/876 | 10/2993 · 21/1325 · 40/14100 |
| `total_credits` | 345 | **355** |
| `sized_ceiling` | 431 | **443** |
| `headroom_credits` | 86 | **88** |
| `baseline_ratio` | `115/6092` | `355/18418` |
| verdict + decision row | `RELEASE_READY` / `row_3_gates_met` | **unchanged** |
| `exit_code` | 0 | 0 |
| blocking / total findings | — | 0 / 101 |
| `deep_ratio` | — | `55/71` |
| bundle content hash | `a1e76c01…` | **`da17b0fe…`** |
| `DOGFOOD_BUDGET_CEILING` | 843 | **843 — deliberately NOT re-pointed (D7)** |

All three artifacts were regenerated from the live generators in ONE pass, none was hand-edited, and each
was re-rendered a second time and compared with what had just been written: **byte-identical = True** for
all three.

**⚠️ Correction to §F, measured on the real tree.** The simulation predicted ONE `partition_id` would move
(`973f3f199d1c → 31483e58e318`). The real split moved **all three**, and produced a different set of ids
than the simulation. It was right that `unit_count` holds at 3 and that `sized_ceiling` becomes 443. The
story's instruction to re-measure rather than trust the copy was the correct one.

**AC15 — fences, verified with BOTH instruments.** `git diff --cached --stat HEAD` and
`git status --porcelain` (the second because `git diff` cannot see an untracked path — AI-E8-2):

- **Zero diff:** `argus/pipeline.py` (still 1199/1200) · `argus/pipeline_persist.py` · `argus/cli.py` ·
  `argus/ledger/**` · `argus/reports/**` · `argus/detectors/**` · `argus/index/**` · `argus/evidence/**` ·
  `argus/precision/**` · `argus/cache/**` · `minions-dogfood-proof-story-7-2-superseded.md` · every
  `*retro*.md` · `epics.md` · `E-PRD/**` · `bmad-dev-loop-pack/`.
- **Two carve-outs, both docstring-only, both mandated by AC11:** `argus/store/envelope.py` (the `:25`
  line AC15 itself exempts) and `argus/verdict/prosecutor.py` (the `:36` line). **⚠️ AC15 and AC11
  contradict each other on the second one:** AC15 fences `argus/verdict/**` and carves out only
  `store/envelope.py:25`, while AC11 explicitly lists `verdict/prosecutor.py:36` among the nine to sweep.
  AC11 is the more specific instruction and names the exact line, so it was followed. The change is two
  words of prose in a module docstring; `git diff` for both files is shown in full in the debug record and
  contains no executable line.

**Whole-system proof, at the end:**

```
PYTHONIOENCODING=utf-8 python -m pytest tests/ -q   ->  exit 0
progress census: Counter({'.': 1185})               ->  1185 passed / 0 failed / 0 skipped
python -m mypy argus                                ->  Success: no issues found in 71 source files
top-5 argus/**: pipeline.py 1199 · dogfood/partition_plan.py 706 · dogfood/proof_run.py 679
                verdict/verdict_gate.py 668 · index/partitioner.py 645        (no file > 1200)
```

Baseline 1160 → 1185 = **+25 tests, 0 removed, 0 skipped, 0 weakened**.

### Completion Notes List

**What was implemented, and the decisions behind it.**

**1. AC1 / AC7 — one version, one source (DF-8-5-A, CLOSED).** `DOGFOOD_ArgusAgent_VERSION` is now
`_ARGUS_VERSION`, imported from `argus.__init__`. This brings one call site up to a rule the package
already states in shipped code (`argus/__init__.py:56-58`, `argus/store/envelope.py:106-107`). The blast
radius is bounded exactly as §A said and was verified by mechanism: `argus_version` is an *envelope* field
for every artifact except the evidence bundle, which also carries it inside the *hashed payload* — so only
the bundle's content hash, and therefore only its content-addressed filename and the signature the proof
publishes, actually move. The imprecise docstring at `tests/test_release_note.py:782-783` ("folded into
every content hash") was corrected rather than propagated. `TC-ArgusAgent-DOCS-001-10`'s `0.1.0` pin was
**not** modified — D1 ships `0.1.0` un-bumped, so the pin was left standing as the deliberate assertion it
is. Two new guards make the version surface an enumerated space: `-14` (three surfaces agree, each read
from where it lives rather than from a fourth copy in the test) and `-15` (an AST sweep of all 71 modules
permits exactly ONE semver literal, at `argus/__init__.py`).

**2. AC8 — the extraction (DF-8-5-D, CLOSED), and why it happened here.**
`argus/dogfood/proof_run.py` 1196 → **679**; new `argus/dogfood/proof_render.py` **447**; new
`argus/dogfood/proof_types.py` **207**. The moved renderer block measured **391** lines (`:809-1199`),
not the ~390 the ledger estimated and not the 367 the story context stated — state your own number, so
here is mine.

**The NFR-M1 fence did NOT force this.** Measured: the DF-8-5-A fix is **+3 lines net** and left the module
at **1199/1200** — it fit, and it was verified to fit before the extraction was begun, exactly as D4 asks.
What forced it is `DF-8-5-D`'s `target_story` ("the first story that edits `argus/dogfood/proof_run.py` for
any reason"), plus the fact that **no story exists after this one**, so "defer" means "drop". Saying
"the fence forced it" would be repeating a narrative the measurement contradicts.

The import edge runs one way — `proof_run → proof_render → proof_types` — so the AR8 pure/impure line is
now a property of the import graph rather than a paragraph in a docstring; a violation would be a cycle
Python refuses to load. `__all__` is UNCHANGED (17 names), and `TC-ArgusAgent-DOGFOOD-001-45` proves every
one still resolves through the real `from argus.dogfood.proof_run import <name>` statement **and** that the
surface has not shrunk — so the guard cannot be satisfied by narrowing what it promises. `-46` asserts
object IDENTITY (`proof_run.X is proof_types.X`), because `==` would not catch a fork and a fork is the
AR7 failure this is guarding.

**3. Two disclosed content changes, kept separate from "pure move".** Neither is part of the byte-identity
proof above; both were made after it was captured.
   - The artifact's provenance banner now names both modules:
     `` AUTO-GENERATED by `argus/dogfood/proof_render.py` (`render_proof_markdown`, re-exported from
     `argus/dogfood/proof_run.py`, which orchestrates the run) ``. Leaving it naming only `proof_run.py`
     would still have *resolved* — and would still have pointed a reader at a file that no longer contains
     the generator. This is the ONLY line that differs between the pre- and post-extraction renders.
   - `DOGFOOD_EXTERNALIZATION_GUARD` moved to `proof_render.py` with its only consumer, because leaving it
     behind would have forced `proof_render → proof_run` — the cycle the shim exists to avoid. Its text is
     byte-identical and `TC-ArgusAgent-DOGFOOD-001-48` now pins it by equality, so AC12's "unchanged" is
     *verified* rather than asserted. This is the one place where an AC's literal wording ("unchanged at
     `proof_run.py:173`") and the engineering constraint conflicted; the constraint won and the guard was
     strengthened to compensate.

**4. AC11 — RS-4b swept, decoys left standing (CLOSED).** All nine gone; `grep -rn "minions_core" argus/
--include=*.py` now returns exactly `argus/audit/minions_llm_adapter.py:5` and `:29`. One of the nine was
not merely stale but **false**: `cost/budget_governor.py:15` claimed AR7 reuse of
`minions_core.cost.budget_guardrails` while the module imports `argus.shared.budget_guardrails`. A tenth
copy of that same false claim in `tests/test_no_web_imports.py:89` was corrected too — outside RS-4b's
stated `argus/**` scope, disclosed here rather than left because it sits three lines from the new guard.
The guard is an **allowlist**, never a zero-count assertion (`STORE-001-109`), plus `-110`, which requires
every surviving occurrence to sit in a line that DENIES the dependency — so the exemption cannot be
repurposed into a smuggling route. Bare-word "Minions" was bounded to `argus/dogfood/**` per D10:
measured 45 across 17 modules at HEAD, 25 across 15 now; 20 removed, 2 kept there because they are TRUE
historical statements about the superseded Story-7.2 run. (⚠️ The context said 44; re-measured it is 45.)

**5. AC10 — `action.yml` (DF-8-4-A, CLOSED).** Exit `1` has its own arm rendering `AUDIT_FAILED`, and the
catch-all renders the same failure token so an unmapped future code can never surface as an assessment.
**Vocabulary chosen: `AUDIT_FAILED` plus a new `assessed` boolean output, rather than failing the step.**
Reason: a composite action that dies takes the consumer's ability to branch with it, and only the caller
knows whether it wants to tolerate a tooling failure or block on one. `assessed` gives them the answer
without string-matching, and the `1`/unmapped arms emit a `::error::` annotation so the failure stays
visible even when tolerated. `strict: "false"` was left alone and the reason recorded in the file itself:
A5 measures that a post-amendment consumer lands on exit `3`, which already fails a blocking gate, so
advisory-by-default is correct and flipping it would pre-empt H3's policy decision.

**6. AC2 / AC3 / AC5 — the release path.** `.github/workflows/release.yml` triggers on `v[0-9]+.[0-9]+.[0-9]+`
tags and `workflow_dispatch`, declares `permissions: contents: write` and nothing else, references **no**
secret (`TC-ArgusAgent-RELEASE-001-10` asserts `secrets.` does not appear), and contains no
index-publishing step. The E1–E6 enumeration lives in ONE named place — `RELEASE_EDGE_CASE_IDS` in
`scripts/release_preflight.py` — with `_HANDLERS` keyed to it; `TC-ArgusAgent-RELEASE-001-01` asserts the
two are the same set, `-02` asserts every member is assigned to a workflow phase (a handled case that never
runs is not handled), and `-03`..`-08` give each member **both** a refusing and a non-refusing case,
because a check that always refuses would pass a refusal-only test. The script is stdlib-only and lives
outside `argus/` deliberately: it must run on a bare runner before anything is installed, and it is release
machinery, not audit engine.

**7. AC4 — the artifact is PROVEN, and the proof found something.**
`python -m build` (build 1.5.0, flit_core 3.12.0 pinned to the declared `>=3.2,<4`) produced
`argus_agent-0.1.0.tar.gz` (**75 files**) and `argus_agent-0.1.0-py3-none-any.whl` (**76 entries**). Both
listings are in the File List section below. The wheel was installed into a **fresh `uv` venv on Python
3.11.15** and every probe was run from a working directory that is not this repository, with
`argus.__file__` verified to resolve inside the venv:

```
argus --help                                       -> exit 0
argus audit <fixture-repo>                         -> RELEASE_READY, exit 0
python -c "import argus, sys; assert 'minions_core' not in sys.modules"   -> OK
python -c "import argus; print(argus.__version__)" -> 0.1.0
```

**The previously-UNMEASURED packaging question is now measured:** `[tool.flit.module] name = "argus"`
packages the `argus` package and nothing else. `audit/`, `phases/`, `adapters/`, `templates/`,
`install.sh`, `install.ps1` and `tests/` are in **neither** artifact. README.md now states the capability
split as a table instead of advertising all four directories (AC5b).

**And the proof surfaced a real defect no source-tree test could see.** ⚠️ **Figure corrected at review
iteration 1 — see Completion Note 12.** Re-measured 2026-08-09 on the built wheel, one clean subprocess per
module, this repository removed from `sys.path`: **66 of the 71 shipped modules import; five module files
do not** — `argus/precision/__init__.py`, `argus/precision/replay_harness.py`,
`argus/dogfood/proof_types.py`, `argus/dogfood/proof_render.py`, `argus/dogfood/proof_run.py` — all with
`ModuleNotFoundError: No module named '_registry'`, because `argus/precision/replay_harness.py:87-90`
unconditionally imports the labelled-cartridge registry from `tests/cartridges/`, which is not shipped.
(This note originally said *"65 of the 69 ... four do not"*: `69` was the pre-split denominator and the
list dropped `replay_harness.py` itself.)
**Pre-existing, verified not assumed:** the identical import exists at HEAD `7be90f7` and the pre-split
`proof_run.py` imported `argus.precision.replay_harness` at its line 127, so the split neither created it
nor widened the consumer surface. **Not fixed here:** `argus/precision/**` is fenced by AC15 and the fix is
a behavioural change to the precision substrate inside a release story with no mandate over it. Filed as
**DF-9-2-A** with the full measurement, disclosed in README.md and CHANGELOG.md, and pinned in BOTH
directions by `TC-ArgusAgent-RELEASE-001-11` (fails if the broken set grows OR shrinks, so a future fix
cannot leave a stale claim behind) and `-12` (the `argus audit` consumer surface must stay clean).

**8. AC6 / AC5b — the note becomes a version and the preamble stops being false.** `## Unreleased` is now
an empty section above `## 0.1.0 — 2026-08-08`, and the FR16/FR4 amendment content moved under the version
where it belongs. The honesty preamble was rewritten to what is now true, bounded strictly by AC2's
evidence rule: it says a release workflow exists and the distribution is resolvable by the AC3 string, it
says the workflow **has never executed**, and it says `argus-agent` is still **not published to any package
index**. `TC-ArgusAgent-DOCS-001-01` was updated **through** the change — it now requires a version heading
that matches `argus.__version__` (so the note cannot announce a version the code does not carry) and still
requires an `## Unreleased` heading for the next change. `-07`'s honesty pin did not weaken; it got more
specific, forbidding four index-publication phrasings and requiring the "never executed" sentence.

**9. AC12 — no release surface over-claims.** `TC-ArgusAgent-DOCS-001-17` scans the seven enumerated
surfaces; `-18` fails if a NEW consumer-facing surface exists unregistered (the `_REPORT_POINTERS`
fail-on-unregistered shape from Story 8.3); `-19` asserts the honesty language is still PRESENT, because a
surface could satisfy a no-over-claim test by saying nothing at all, and silence about a self-audit reads
as a normal audit. **A blunt substring guard was tried first and failed correctly** on
`minions-dogfood-proof.md`'s "The gate is cleared ONLY by the human TP/FP adjudication" and on CHANGELOG's
own denial — so the scan is sentence-scoped with a denial filter, and `-17b` is the positive control that
proves the filter still catches a genuine affirmative over-claim rather than swallowing everything.
Verified unchanged, not assumed: `grade: demo-heuristic-only` is intact in the regenerated proof,
`protocol_cleared=True` appears in **no** module of `argus/dogfood/**` (the `-30` guard was widened from
one file to the whole package, so the split could not create a blind spot), and
`DOGFOOD_EXTERNALIZATION_GUARD` is byte-identical.

**10. AC13 — knowingly republished, and said out loud.** The regenerated `minions-dogfood-proof.md` again
prints `DF-8-5-C`'s **"N=0 labeled cartridges populated, floor N=5"** while the shipped registry measures
5 distinct rule classes and 7 populated rows. It was **republished unchanged and knowingly**. It
**understates** — it makes the provisional gate look further from its floor than it is, so it cannot make a
gate look cleared. Not fixed because its `target_story` names the 6.5/6.6 precision surface *after* the
human `DF-7-2-A` adjudication, which has not occurred, and because `argus/precision/**` is fenced.
`DF-8-5-C` stays OPEN and was not rewritten. **Other figures this story republished without re-deriving:
none.** Every number in all three regenerated artifacts came out of the live generators in this session;
`DOGFOOD_BUDGET_CEILING = 843` is reprinted as the frozen historical execution parameter it is, beside the
live sizing of 443, with a fit verdict for each — which is the ceiling-honesty pair working as designed.

**11. AC14 / AC16 — dispositions, and who is left holding them.** `deferred-work.md` gained one dated
append-only section (**+287 insertions, 0 deletions**, verified with `git diff --numstat`). `DF-8-5-A`,
`DF-8-5-D`, `DF-8-4-A` and `RS-4b` are **CLOSED** with closing evidence. `DF-8-4-B` is **PARTIALLY
CLOSED** — the heading half by `TC-ArgusAgent-DOCS-001-16`, the bytes-example half explicitly left OPEN
with the reason (the note already carries byte-equality assertions over the surfaces that matter, so a
second generic check would be duplication). `DF-8-5-C`, `DF-8-5-B`, `DF-8-4-C`, `DF-8-4-D`, `DF-8-2-A`,
`DF-8-3-A` and `DF-8-3-C` stay OPEN. Three new items were opened: `DF-9-2-A` (the distribution import
gap), `DF-9-2-B` (the 23 remaining bare-word subject claims outside `dogfood/`), `DF-9-2-C`
(`argus/dogfood/__pycache__/*.pyc` are tracked in git — measured, pre-existing, not touched here because a
silent `git rm --cached` during a release story is precisely the unannounced side effect Epic 8 exists to
prevent).

For `DF-8-5-B` the story asked whether this work incidentally made the remedy discoverable. **It did not,
and deliberately so:** the entry asks for a regeneration entry point named in the failure message of all
three assertions, or a CI regenerate-and-diff step; the first edits assertion text in tests this story must
not weaken, and the second adds a ~2-minute dogfood run as a CI job inside a release story. What exists
instead is a documented sequence in this record, which is a story artifact and not the
discoverable-from-red-output remedy the entry asks for. Saying so is the disposition.

**The register after this story: nobody is looking after it.** Twelve entries remain OPEN, plus half of
`DF-8-4-B` and the three new ones. Every `target_story` of the form "the first story that…" now points at a
story that does not exist. That is recorded explicitly in the ledger rather than papered over by
re-targeting them at a hypothetical successor. In particular: `argus/pipeline.py` is **1199/1200**, the
next edit of any size breaches NFR-M1, and **no story is queued to perform the extraction** that
`DF-8-2-A`/`DF-8-3-A`/`DF-8-3-C` all gate on. Performing that refactor to avoid writing this sentence would
have been the worse choice (D11).

**H0 (AC16):** **still UNOWNED.** This story did **not** file H1–H4, did not claim them, and did not close
them. Filing them requires a named human; it executes in another repository and this repo's CI cannot
verify it. No artifact produced here implies the Minions integration is done, scheduled or owned. Restated
so they are not lost when this plan closes: assumption **A5** is ⚠️ **Unsupported** — post-amendment
Minions is expected to land on row 4 → exit `3`, which still fails an unconfigured blocking gate, so **H3**
needs a policy decision first — and **IN-1** must be an optional extra, never a base dependency, because
Minions declares `dependencies = []`.

**⚠️ PREPARED, NOT EXECUTED — the outward-facing boundary.** The orchestrator forbade any irreversible or
public action, and this story respected that. Everything below is complete and staged; none of it was
performed. **A human operator must run these, in this order, from a clean tree at the commit that carries
this work:**

1. **Commit** the delta (the orchestrator handles this).
2. `git tag -a v0.1.0 -m "argus-agent 0.1.0"` — **not created.** `git tag -l` is still empty.
3. `git push origin <branch> && git push origin v0.1.0` — **not pushed.** Nothing left this machine.
4. The tag push triggers `.github/workflows/release.yml`, which runs the preflight, builds, and creates the
   GitHub Release. **No Actions run id and no release URL exist**, and no document in this delta claims
   one.
5. **Before step 3, verify the two things this story could not:** (a) open
   `https://github.com/Inan15/Agent-Argus` while signed out — if it loads, the README/CHANGELOG "no
   credential required if public" sentence is correct as written; if it does not, both documents need the
   private-repo token sentence promoted from caveat to instruction. (b) Confirm the `argus-agent` name is
   free on PyPI only if you intend to take D2's exit path; this story did not check and does not claim.

**ACs affected by the boundary:** **AC2** is satisfied for "a committed release workflow exists" and is
**prepared-not-executed** for "attaches them to a GitHub Release" — the workflow does it, the workflow has
not run, and every document says so. **AC3** is fully satisfied except that the repository's visibility is
recorded as ⚠️ **measure-this** rather than as a fact, because measuring it requires a network call to a
public URL and the honest thing was to name the check rather than invent the answer. **AC4** is fully
satisfied — the build and the clean-environment proof are local and were executed in full.

**A note on task ordering.** The story's Task 4 (stage + regenerate) is numbered before Tasks 5–8. It was
executed AFTER them, because D6 is the binding rule ("regenerate LAST, once, after every source edit") and
Tasks 5–8 touch `.github/`, `action.yml`, `README.md`, `CHANGELOG.md`, `scripts/` and `tests/` — none of
which is under the `argus/` scope the generators read. Task 4's first sub-step (staging the two new
modules) was performed early, because the build in Task 6 and the plan enumeration both read
`git ls-files`. The regeneration itself ran exactly once, last.

**Test-id index correction.** AC15 states `TC-ArgusAgent-DOGFOOD-001` is taken through `-36` and that new
dogfood tests start at `-37`. Measured: `-37` through `-44` are already in use by Story 8.5's DR-10 members
and its review-iteration patches. **The first free id is `-45`**, which is where the new dogfood tests
start. Recorded here and in the new test module so the next author does not re-derive it.

---

**12. CODE-REVIEW ITERATION 1 (2026-08-09) — all seven patch items addressed, none deferred.**

Scope of this round: **no `argus/**` byte was changed and no artifact was regenerated.** Verified, not
assumed — `git diff --name-only -- argus/` and `git diff --name-only -- '…/minions-dogfood-*.md'` are both
EMPTY against the pre-review index. The review explicitly found no source logic or artifact implicated, and
nothing here contradicted that. `pipeline.py` is still 1199; the ledger is still append-only (+323 / −0
against `7be90f7`, re-verified with `git diff --numstat` after editing inside the block THIS story adds —
that block has never been committed, so correcting a figure inside it leaves the file's diff purely
additive).

**RED first, and shown.** Every behavioural fix was demonstrated to fail against the pre-fix code before it
was made green, by loading the **staged** (pre-fix) `scripts/release_preflight.py`,
`.github/workflows/release.yml` and `tests/test_release_surface_honesty.py` out of the git index
(`git show :<path>`) and exercising them. Observed on the pre-fix code:

```
_published_release_tags() -> ()            # 'could not ask' collapsed into 'asked, none exist'
report line: '  E4 the version already has a published artifact for that target  ok'
closing line: 'all enumerated release edge cases cleared.'
GH_TOKEN in pre-build preflight step -> False
5 run-block(s) interpolate ${{ }} into shell source, e.g. 'TAG="${{ inputs.tag || github.ref_name }}"'
mutable pins -> ['actions/checkout@v4', 'actions/setup-python@v5', 'actions/upload-artifact@v4']
caught? False | "Argus has been externally validated with no exceptions."
```

**R1 [Med] — the stale pre-split import figure. FIXED, and re-measured from scratch rather than copied.**
The reviewer's figures were **not** taken on trust. Method used here: the built wheel
`dist/argus_agent-0.1.0-py3-none-any.whl` was extracted (76 entries = **71** `argus/**` `.py` modules + 5
`dist-info`, zero non-`.py` entries under `argus/`), and each of the 71 modules was imported in **its own
clean subprocess** with the extracted wheel on `sys.path`, the repository root **removed** from `sys.path`
(asserted inside the child, so a silent failure to remove it cannot fake a pass), and the working directory
outside this repository. Result: **66 import, 5 fail**, every one with
`ModuleNotFoundError: No module named '_registry'`:

```
argus/precision/__init__.py
argus/precision/replay_harness.py
argus/dogfood/proof_types.py
argus/dogfood/proof_render.py
argus/dogfood/proof_run.py
```

That is exactly `_NOT_IMPORTABLE_FROM_DISTRIBUTION`, so prose and pin now agree. ⚠️ **Method honesty:** this
re-measurement did **not** re-create a fresh virtualenv (`python -m venv` could not run `ensurepip` on this
machine in this session); it isolates by wheel-extraction plus repo removal from `sys.path`, which
establishes the same property the sentence claims. The published sentences were reworded to describe the
isolation that was actually exercised rather than repeating "in a fresh virtualenv". Corrected at **five**
sites — the three the review named plus two it did not: `CHANGELOG.md`, `README.md`, the `DF-9-2-A` body in
`deferred-work.md`, **Completion Note 7 above**, and the header comment block of
`tests/test_release_preflight.py` (which carried the same "65 of the 69 … 4 do NOT" sentence). All five now
enumerate the five module files. The `DF-9-2-A` **disposition is untouched** — file, don't fix — and the
entry now says out loud which figures were wrong and why, instead of quietly swapping them.

**R2 [Med] — the headline install command cannot resolve. FIXED (documented, not executed).**
Re-verified here: `git tag -l` is **empty**. `CHANGELOG.md`'s *"is therefore resolvable by the VCS pin
below"* became *"**will be** resolvable … **once that tag is created and pushed**"*, and a ⚠️ line sits
**immediately under** the code block saying the tag does not exist and the capability is *prepared, not
exercised*. `README.md`'s lead-in stopped promising "the repository itself" and then handing over a
tag-pinned ref — it now says plainly that the string is a tag-pinned VCS reference — and **both** code
blocks (shell and `pyproject.toml`) carry their own adjacent ⚠️. The `Resolving argus-agent` table's
dependency-string cell carries it too, because that cell is what a consumer copies. **The tag was NOT
created and nothing was pushed** — the outward-facing boundary holds.

**R3 [Med] — E4 was structurally inert and printed `ok` anyway. FIXED, both halves.**
(a) The pre-build preflight step now carries `env: GH_TOKEN: ${{ github.token }}` — the automatic token, so
`TC-ArgusAgent-RELEASE-001-10`'s "no `secrets.`" assertion still holds. (b) `_published_release_tags` now
returns `None` for *could not ask* (missing `gh`, non-zero exit, unparseable output) as distinct from `()`
for *asked, none exist*; `PreflightContext.published_release_tags` is typed
`tuple[str, ...] | None` so the distinction cannot be dropped by accident; `check_e4_*` returns a new
`Unevaluable` outcome; and the report prints **`UNKNOWN`**, lists the unevaluated cases under *"NOT
EVALUATED (this run could not observe these; they are NOT cleared)"*, and replaces the closing *"all
enumerated release edge cases cleared"* with a sentence naming what was not established. **Deliberately
NOT a hard failure:** `gh` is legitimately absent for an operator running the preflight locally, and
`gh release create --verify-tag` still refuses to clobber a published release — so the defect being removed
is the false clearance, not a lost refusal. New guards: `-13` (the three-valued outcome), `-14` (drives
`main()` and asserts the printed E4 line is not `ok`), `-15` (the collector's four failure modes vs a
genuine empty list), `-16` (the workflow really gives that step the token).

**R4 [Med] — script injection on a `contents: write` job. FIXED.**
Every untrusted value is now bound through `env:` and referenced as a quoted shell variable; **no `run:`
body in the file contains a `${{ }}` expression at all** (asserted mechanically by `-17`, which extracts
every `run:` block body and fails on any interpolation, rather than pattern-matching the cases someone
thought of). The tag is validated against the **existing** `release_preflight._VERSION_TAG`
(`^v\d+\.\d+\.\d+$`) — reused, not restated (AR7) — via a new `--phase validate-tag` mode in the FIRST step
that touches the value, and `main()` now refuses a malformed tag in **every** phase before
`gather_context` runs, so no git or `gh` call ever sees an unvalidated value (`-19` proves this by making
`gather_context` raise). `set -euo pipefail` was added to the multi-line blocks so the validation failure
actually aborts the step. `ref: ${{ inputs.tag || github.ref }}` on `actions/checkout` is left as an
expression **on purpose**: it is an ACTION input passed to git as an argument, not shell source, so it is
not an injection surface — and it is validated before any `run:` step uses the value. That reasoning is
recorded in the file rather than left for the next reader to reconstruct.

**R5 [Low] — mutable major-tag action pins. FIXED, with the SHAs verified rather than recalled.**
Each SHA was resolved from the GitHub REST API on 2026-08-09 (read-only `GET`; nothing public was changed)
and cross-checked back to the semver tag that points at it:
`actions/checkout@11d5960a326750d5838078e36cf38b85af677262 # v4.4.0`,
`actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5.6.0`,
`actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4.6.2`. The workflow header records
the method and the date so a future bump re-verifies instead of trusting this line.

**R6 [Low] — E2 registered but unreachable. FIXED by disclosure, not by a flag that would lie.**
Of the review's two options, passing `--creating-tag` on the `workflow_dispatch` path was **rejected**: that
input is documented as a tag that *must already exist*, so the flag would state something false about what
the run is doing **and** E2 would then refuse every legitimate dispatch. Instead `CI_UNREACHABLE` in
`scripts/release_preflight.py` names E2 with the reason, the report prints
`(not reachable from this workflow)` beside it and a `NOT REACHABLE HERE [E2]` paragraph, the workflow
header states it in prose, and `check_e2_*`'s docstring records the rejected alternative. `-18` pins it in
**both** directions: the disclosure may not name a member that is reachable, and the workflow may not start
passing `--creating-tag` while the disclosure still says it does not. `-02`'s premise is now discharged
honestly — phase assignment is necessary, and reachability is stated separately instead of being implied by
it.

**R7 [Low] — the denial filter could exempt a genuine affirmative claim. FIXED.**
The markers were split by how English actually works: `_DENIAL_MARKERS` (negations — `not`, `no`, `never`,
`cannot`, `n't`, …) must now appear **BEFORE** the banned phrase, since negation binds leftward to the claim
it denies; `_QUALIFIER_MARKERS` (`only by`, `stays provisional`, …) may appear anywhere, because they
restrict a phrase rather than negate it and naturally follow it. A pure "must precede" rule was tried first
and **rejected on measurement**: it would have flagged the shipped honest sentence *"The gate is cleared
ONLY by the human TP/FP adjudication"*, which is a real denial with the qualifier trailing. `-17b` gained
**three** trailing-negation positive controls, including the review's own
*"Argus has been externally validated with no exceptions"*, and all four verbatim honest denials still pass
un-flagged.

**Deferred, unchanged:** the one `[Review][Defer]` item (`action.yml:127`'s pre-existing
`inputs.strict` shell interpolation) stays deferred exactly as the reviewer dispositioned it — the line is
byte-identical to HEAD `7be90f7` and is outside this story's delta. Nothing else was deferred, and no
finding was dropped.

**Whole-system, after the fixes:** `PYTHONIOENCODING=utf-8 python -m pytest tests/ -q` → exit `0`, progress
census `Counter({'.': 1192})` — **1192 passed / 0 failed / 0 skipped** (1185 → 1192: seven new
`TC-ArgusAgent-RELEASE-001-13`..`-19`; **zero** tests removed, skipped or weakened). `python -m mypy argus`
→ *Success: no issues found in 71 source files*; `python -m mypy scripts/release_preflight.py` → clean. No
`argus/**` file over 1200 lines (`pipeline.py` 1199, `partition_plan.py` 706, `proof_run.py` 679).
`scripts/release_preflight.py` 410 → 559 lines, `tests/test_release_preflight.py` → 656,
`.github/workflows/release.yml` → 190 — all far under the NFR-M1 ceiling, and no fenced path moved.

### File List

**New — source and release machinery**
- `argus/dogfood/proof_types.py` (207 lines) — the five frozen result dataclasses, moved verbatim
- `argus/dogfood/proof_render.py` (447 lines) — the pure markdown renderer + `DOGFOOD_EXTERNALIZATION_GUARD`
- `scripts/release_preflight.py` (559 lines) — the E1–E6 enumeration and its handlers, the `Unevaluable`
  outcome, `CI_UNREACHABLE`, and the `--phase validate-tag` guard *(review iter-1: 410 → 559)*
- `.github/workflows/release.yml` (190 lines) — the tag-triggered build + GitHub Release workflow, with
  `env:`-bound untrusted input, SHA-pinned actions and `GH_TOKEN` on the preflight step *(review iter-1)*

**New — tests**
- `tests/test_dogfood_module_split.py` — `TC-ArgusAgent-DOGFOOD-001-45`..`-48`
- `tests/test_release_preflight.py` — `TC-ArgusAgent-RELEASE-001-01`..`-19` (new verification area;
  `-13`..`-19` added at review iter-1 for the E4 three-valued outcome, the report, the collector, the
  workflow token, script-injection containment, E2's disclosed unreachability and tag validation order)
- `tests/test_release_surface_honesty.py` — `TC-ArgusAgent-DOCS-001-16`, `-17`, `-17b`, `-18`, `-19`
  (`-17b` gained three trailing-negation positive controls at review iter-1)

**Modified — source**
- `argus/dogfood/proof_run.py` — DF-8-5-A fix, the extraction + re-export shim, docstring rewrite, the
  operator-visible error message, D10 subject claims (1196 → 679 lines)
- `argus/dogfood/partition_plan.py` — D10 subject claims (705 → 706)
- `argus/dogfood/__init__.py` — D10 subject claims
- `argus/audit/deep_audit.py` · `argus/audit/ports.py` · `argus/cost/budget_governor.py` ·
  `argus/governance/escalation.py` · `argus/store/envelope.py` · `argus/verdict/prosecutor.py` — RS-4b
  sweep, docstring text only

**Modified — tests**
- `tests/test_dogfood_proof.py` — `-34` updated through the DF-8-5-A fix; `-30` and `-33` widened from one
  module to the whole `argus/dogfood/` package
- `tests/test_release_note.py` — `-01` and `-07` updated through the AC6 change; `-10`'s docstring
  corrected; `-14`/`-15` added
- `tests/test_no_web_imports.py` — the two new modules registered in `_MODULES_UNDER_GUARD`;
  `STORE-001-109`/`-110` added; one stale `minions_core` comment corrected

**Modified — consumer-facing and packaging**
- `README.md` — the no-clone install path, the AC3 access record, the measured capability split; *(review
  iter-1)* the unresolvable-tag warning under both install blocks and the re-measured 66-of-71 / five-file
  import record
- `CHANGELOG.md` — `## 0.1.0 — 2026-08-08` with the rewritten honesty preamble; `## Unreleased` retained;
  *(review iter-1)* "will be resolvable … once that tag is created and pushed" + the adjacent
  tag-does-not-exist warning, and the re-measured import figures
- `action.yml` — the complete exit-code map, the `assessed` output, the rewritten output descriptions
- `.gitignore` — `dist/`, `build/`, `*.egg-info/`

**Modified — artifacts and records (regenerated, never hand-edited)**
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md`
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md`
- `_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md`
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (append-only: **+323 / −0** against `7be90f7`
  after the review iter-1 correction to the `DF-9-2-A` body; still zero deletions)
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` (status only; comments preserved)
- `_bmad-output/design-artifacts/ArgusAgent/stories/9-2-ship-distribution-another-repo-can-actually-resolve.md`
  (this file — `git add`ed, closing AI-E8-1's recurrence class)

**Built but NOT committed** (`dist/` is gitignored): `dist/argus_agent-0.1.0.tar.gz`,
`dist/argus_agent-0.1.0-py3-none-any.whl`.

#### Measured artifact contents (AC4 — recorded verbatim)

**Wheel `argus_agent-0.1.0-py3-none-any.whl` — 76 entries**: `argus/__init__.py`, `argus/audit/__init__.py`,
`argus/audit/deep_audit.py`, `argus/audit/grounding.py`, `argus/audit/minions_llm_adapter.py`,
`argus/audit/open_llm_adapter.py`, `argus/audit/ports.py`, `argus/cache/__init__.py`,
`argus/cache/invalidation.py`, `argus/cache/key.py`, `argus/cache/memo_store.py`, `argus/cli.py`,
`argus/cost/__init__.py`, `argus/cost/budget_governor.py`, `argus/cost/exhaustion.py`,
`argus/cost/resume.py`, `argus/detectors/__init__.py`, `argus/detectors/base.py`,
`argus/detectors/orphan_code.py`, `argus/detectors/secret_scan.py`,
`argus/detectors/secret_suppression.py`, `argus/detectors/tool_runner.py`,
`argus/detectors/vacuous_test.py`, `argus/dogfood/__init__.py`, `argus/dogfood/partition_plan.py`,
`argus/dogfood/proof_render.py`, `argus/dogfood/proof_run.py`, `argus/dogfood/proof_types.py`,
`argus/evidence/__init__.py`, `argus/evidence/bundle.py`, `argus/governance/__init__.py`,
`argus/governance/decision_record.py`, `argus/governance/escalation.py`, `argus/index/__init__.py`,
`argus/index/ast_index.py`, `argus/index/partitioner.py`, `argus/intake/__init__.py`,
`argus/intake/ignore_rules.py`, `argus/intake/repo_loader.py`, `argus/intake/source_state.py`,
`argus/intake/stack_detect.py`, `argus/ledger/__init__.py`, `argus/ledger/coverage_ledger.py`,
`argus/ledger/coverage_report.py`, `argus/ledger/critical_subsystems.py`,
`argus/ledger/depth_semantics.py`, `argus/ledger/recording.py`, `argus/models.py`, `argus/pipeline.py`,
`argus/pipeline_persist.py`, `argus/precision/__init__.py`, `argus/precision/replay_harness.py`,
`argus/reports/__init__.py`, `argus/reports/formatter.py`, `argus/reports/generator.py`,
`argus/reports/plain_english.py`, `argus/shared/__init__.py`, `argus/shared/budget_guardrails.py`,
`argus/shared/source_languages.py`, `argus/shared/workspace_containment.py`, `argus/store/__init__.py`,
`argus/store/canonical.py`, `argus/store/envelope.py`, `argus/store/integrity.py`, `argus/store/paths.py`,
`argus/store/reader.py`, `argus/store/writer.py`, `argus/verdict/__init__.py`,
`argus/verdict/negative_assurance.py`, `argus/verdict/prosecutor.py`, `argus/verdict/verdict_gate.py`,
`argus_agent-0.1.0.dist-info/METADATA`, `argus_agent-0.1.0.dist-info/RECORD`,
`argus_agent-0.1.0.dist-info/WHEEL`, `argus_agent-0.1.0.dist-info/entry_points.txt`,
`argus_agent-0.1.0.dist-info/licenses/LICENSE`.

**Sdist `argus_agent-0.1.0.tar.gz` — 75 files**: the same 71 `argus/**` modules under
`argus_agent-0.1.0/argus/`, plus exactly four others — `argus_agent-0.1.0/LICENSE`,
`argus_agent-0.1.0/PKG-INFO`, `argus_agent-0.1.0/README.md`, `argus_agent-0.1.0/pyproject.toml`.

**`entry_points.txt`** (unchanged, as `TC-ArgusAgent-DOCS-001-13` requires):
`argus=argus.cli:main`, `argus-agent=argus.cli:main`, `repo-audit=argus.cli:main`.

**Neither artifact contains** `audit/`, `phases/`, `adapters/`, `templates/`, `tests/`, `install.sh`,
`install.ps1`, `uninstall.sh`, `action.yml`, `CHANGELOG.md` or `_bmad-output/`.

## Change Log

- **2026-08-08** — Story 9.2 contexted (`create-story`). Re-scoped by operator decision on the Epic-8
  retrospective's SD-1 / AI-E8-4 to absorb `DF-8-5-A`, `DF-8-4-A` and `RS-4b`, plus the `DF-8-5-D` extraction
  and its artifact-regeneration cascade, and to disposition `DF-8-4-B` which fires on the same file set.
  Status `backlog` → `ready-for-dev`.
- **2026-08-08** — Story 9.2 implemented (`dev-story`). IN-0 delivered up to the outward-facing boundary.
  **Closed:** `DF-8-5-A` (the signed bundle's version token now derives from `argus.__version__`; bundle
  hash `a1e76c01…` → `da17b0fe…`), `DF-8-5-D` (`proof_run.py` 1196 → 679, split into `proof_types.py` 207 +
  `proof_render.py` 447 with a re-export shim, proven a pure move at 9927/9927 and 55101/55101 bytes),
  `DF-8-4-A` (`action.yml` exit `1` gets its own `AUDIT_FAILED` arm plus an `assessed` output), `RS-4b`
  (nine references swept, two true-negative decoys allowlisted). **Partially closed:** `DF-8-4-B` (heading
  half). **Opened:** `DF-9-2-A`, `DF-9-2-B`, `DF-9-2-C`. **Added:** a committed release workflow, the E1–E6
  release-edge-case enumeration with a fail-on-unenumerated guard, a locally-proven sdist + wheel, the
  `0.1.0` release note, and the README distribution record. **Regenerated once, last:** all three dogfood
  artifacts — 69→71 files, 18276→18418 LOC, 345→355 credits, ceiling 431→443, all three `partition_id`s
  moved, `unit_count` held at 3, verdict `RELEASE_READY`/`row_3_gates_met` unchanged. **Suite:** 1160 →
  1185 passed, 0 failed, 0 skipped; mypy clean over 71 files; no `argus/**` file over 1200 lines;
  `pipeline.py` untouched at 1199. **Not executed (operator's call):** no tag, no push, no GitHub Release,
  no PyPI publication. Status `in-progress` → `review`.
- **2026-08-09** — Code review iteration 1: **FAIL** (4 Med + 3 Low). The reviewer independently upheld the
  DF-8-5-D pure move, the byte-identical artifact re-render, the ledger's append-only property and the
  `DF-9-2-A` disposition; the findings were confined to published figures, an unexercised capability claim,
  and the new release/CI surface. Status `review` → `in-progress`.
- **2026-08-09** — Review findings addressed (`dev-story`, fix iteration 1). **7 of 7 patch items resolved,
  0 deferred, 0 dropped**; the single `[Review][Defer]` item (pre-existing `action.yml:127`) is left
  deferred as the reviewer dispositioned it. **R1** the import figure was **re-measured from scratch** (71
  wheel modules, one clean subprocess each, repo removed from `sys.path`) → **66 import / 5 do not**, and
  corrected at five sites with all five module files enumerated, including
  `argus/precision/replay_harness.py` which every prose site had omitted. **R2** the `v0.1.0` install
  command is now marked unresolvable adjacent to every code block (`git tag -l` re-verified empty) and the
  CHANGELOG's capability claim became conditional. **R3** `GH_TOKEN` reaches the pre-build preflight and E4
  reports `UNKNOWN` instead of `ok` when it could not observe. **R4** script-injection surface closed —
  no `run:` body interpolates an expression, and the tag is validated against the existing
  `^v\d+\.\d+\.\d+$` before any command sees it. **R5** all three actions pinned to API-verified commit
  SHAs. **R6** E2's CI-unreachability disclosed and pinned in both directions. **R7** the denial filter now
  requires the negation to precede the claim. **RED demonstrated** for every behavioural fix against the
  pre-fix code recovered from the git index. **Suite 1192 passed / 0 failed / 0 skipped, exit `0`** (+7
  tests, none removed or weakened); mypy clean over 71 `argus` files and over the preflight script. **No
  `argus/**` byte changed and no artifact regenerated** — none was implicated. Still not executed: no tag,
  no push, no Release, no index publication. Status `in-progress` → `review`.
