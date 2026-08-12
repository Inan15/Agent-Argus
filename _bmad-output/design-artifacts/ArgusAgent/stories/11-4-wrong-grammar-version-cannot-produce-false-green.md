---
baseline_commit: 93adc94d0203eaaf4d1cb1d8bc7113e9b885beed
baseline_note: >-
  `HEAD` = `93adc94` on `master`, **6 commits unpushed**, `git tag -l` **empty** (both re-measured
  2026-08-12). Epic 10 is 5/5 `done`; Stories 11.1, 11.2 and 11.3 are `done` and **their deltas are
  in the tree, uncommitted**. **No CI run has ever seen a line of Epic 10 or Epic 11.** Every
  baseline figure in this story is **LOCAL, Windows / CPython 3.11.15**, under the dated risk
  acceptance recorded in Story 11.1 §0.1 (AI-E10-1, 2026-08-11, XAgent007). See §0.1 — carried
  forward, not re-taken.
  ⚠️ **The tree is NOT clean and you did not dirty it.** `git status --porcelain -- argus/` shows
  exactly **four ` M` lines** — `argus/cli.py`, `argus/detectors/vacuous_test.py`,
  `argus/reports/generator.py`, `argus/verdict/negative_assurance.py` — the reviewed and `done`
  deltas of 11.1 and 11.2. `action.yml`, `CHANGELOG.md` are staged (`M `) from 11.3. `README.md`,
  `pyproject.toml`, `tests/test_release_surface_honesty.py`, `tests/test_invocation_contract.py` are
  inherited-dirty from 10.5/11.1/11.2/11.3. `_bmad/**` churn is AI-E10-9's. `bmad-dev-loop-pack/`,
  `.bmad-drift-audit/`, `_bmad-output/audit-reports/*` and the untracked `argusdemo/` belong to the
  orchestrator/host. **Do not commit, revert, restage or "tidy" any of it.** THIS FILE is untracked
  and IS yours: `git add` it with your delta or you repeat AI-E8-1.
  ⚠️ **ONE TEST IS ALREADY RED AND IT IS NOT YOURS.** See §0.4 (`DF-11-1-A`), carved out **by node
  id** for the fourth consecutive story.
  ⚠️ **THE EPIC'S HEADLINE PREMISE FOR THIS STORY IS PARTLY FALSE.** See §0.3. It was re-measured by
  execution and by reading the upstream release notes, and the specific flip it names does **not**
  reproduce in the direction it names. **The hazard is real and worse than written; the sentence is
  wrong.** Do not implement the sentence. Implement §A.
  **Every count, coordinate, verdict, exit code, LOC figure and partition id below was produced by
  EXECUTING code on THIS tree on 2026-08-12.** Treat every line number as a hint you must re-verify
  by anchor text.
story_key: 11-4-wrong-grammar-version-cannot-produce-false-green
epic: 11
---

# Story 11.4: A wrong grammar version cannot silently produce a false green

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **ArgusAgent story — Argus repo.** ArgusAgent (formerly APAA) is a self-contained headless audit
> tool extracted from the Minions monorepo into its own repository (`Agent-Argus`, distribution
> `argus-agent`, package `argus/`). **RS-1 is binding: all work lands in THIS repo. The
> `minions_core/apaa/` copy in the Minions repo is legacy — no modification, no back-port.** Planning
> artifacts live under `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is that folder's
> `sprint-status.yaml`. Prose in older documents saying `design-artifacts/APAA/`,
> `minions_core/apaa/` or `tests/apaa/` should be read as `design-artifacts/ArgusAgent/`, `argus/`
> and `tests/`.
>
> ⚠️ **This is the FIRST Epic 11 story whose write set is INSIDE `argus/`.** 11.1 and 11.2 measured
> the `DF-10-4-D` fence and found it slack; 11.3's write set was entirely outside `argus/` so it did
> not bind at all. **Here it binds, and the LOC budget binds to the physical line.** §0.2 gives the
> exact cliff, measured: **+100 physical lines to unit 2 is safe; +101 changes two partition ids.**

---

## Story

As an operator on a machine whose environment I did not build,
I want an unvalidated parser to withhold a verdict rather than compute one,
so that an assurance tool never emits a false green from a dependency it did not check.

**Why this is one story, and what it is not.** Epic 11's charter is *"nothing unsafe or untrue can be
published."* This story closes exactly one defect class: **Argus computing and publishing a verdict
on top of a parsing toolchain it has never checked.** It adds a startup validation of the tree-sitter
toolchain at the one seam every parse already passes through, degrades a failed validation to the
existing named-degraded-outcome machinery, and thereby makes `RELEASE_READY` **unreachable** under an
unvalidated parser. It ships **no new detector**, changes **no decision-table row, threshold or exit
code mapping**, adds **no dependency**, adds **no file under `argus/`**, and publishes **nothing**.

**Why it is release-blocking.** Every other verdict Argus emits is defended: the floor defends
against too little coverage, row 2 defends against blocking findings, cross-cutting #6 defends
against a wrong 🔴. **Nothing defends against a wrong 🟢 caused by the parser itself.** Argus resolves
`tree-sitter-<lang>` versions and folds them into the cache key (Story 10.2), but it has **never once
asked whether the toolchain it is about to trust actually behaves the way it was validated against**
— measured: `grep -rn "importlib.metadata" argus/` returns exactly one site,
`argus/index/ast_index.py::_package_version`, and it **records** a version, it never **checks** one.
On a public index the environment is the user's, not ours. A metadata bound in `pyproject.toml`
constrains a *resolver*; it constrains **nothing** on a machine where the package is already
installed, pinned by another tool, vendored, or patched.

**The direction that matters.** `argus/dogfood/proof_types.py:132` already names it: the
false-`RELEASE_READY` direction is **inversion F1**, the PRD-fatal one. A false 🔴 is an annoyance a
user argues with. A false 🟢 from an assurance tool is the product thesis inverted, and the user has
no way to detect it — **which is exactly what §A.2 demonstrates: the deep-coverage ratio is
UNCHANGED, so no surface Argus prints can see the loss.**

⚠️ **Read §0 before anything else.** Six items gate this story. One of them is the epic's own AC text,
which is **wrong** and which you must not implement literally.

---

## Story Context

### Method statement — everything in §0–§F was MEASURED on this tree on 2026-08-12

Every count, coordinate, verdict, exit code, hash prefix and LOC figure below was produced by
running `git`, `pytest`, `mypy`, `python -m argus.cli audit .`, by importing and calling
`argus.dogfood.partition_plan.build_full_repo_plan('.')`, and — for §A.2 and §A.3 — by **executing
the real pipeline over real staged cartridges inside a REVERSIBLE IN-MEMORY EXPERIMENT**: module
attributes of `argus.index.ast_index` were monkeypatched inside one Python process, the audit was
re-run, and the attributes were restored. **No file on disk was modified by any measurement in this
story**, which is why no `sha256` round-trip is quoted for them. The upstream release-note facts in
§A.5 came from the `py-tree-sitter` releases page, read 2026-08-12. **Re-derive everything;
transcribe nothing.**

---

### §0. The six gates on this story — read these first

#### 0.1 — 🔴 DATED RISK ACCEPTANCE, CARRIED FORWARD (AI-E10-1)

**Recorded by: XAgent007 (operator), 2026-08-11. Carried forward to this story, not re-taken.**

> **No CI run covers any Epic 10 or Epic 11 sha.** Re-verified this session: `HEAD` = `93adc94`, **6
> commits ahead of `origin/master`** (`git rev-list --count origin/master..HEAD` = 6), `git tag -l`
> **empty**. Every gate figure this story cites — **1371 collected tests**, `mypy` **clean on 72
> source files**, the three dogfood partition ids — is a **LOCAL run on a Windows host at CPython
> 3.11.15**. CI is ubuntu × 3.10/3.11/3.12, and this project has measured evidence that the
> difference matters (six of the twelve commits in `cd60dbb..00c8d1b` were host-portability defects
> invisible on exactly this machine).

**🚩 This gate has a specific edge here that no previous story had.** Your subject IS the toolchain
version, and **this host has exactly one** (`tree-sitter 0.25.2`, `tree-sitter-python 0.25.0`, plus
eight more grammars at 0.23.1–0.25.0 — §A.4 has the full table). You cannot prove your bound against
a real out-of-bound install without changing this environment, and **you must not**: mutating the
venv would invalidate every other figure in this story and in the three stories before it.
**Therefore:**

1. Every negative case is driven through a **simulated seam**, never by installing or uninstalling a
   real package. This is 10.4's `E.3` rule, and 10.4 proved it works for exactly this module.
2. Label every figure **LOCAL**; cite an `audit-ci.yml` run id **plus the sha it covers**, or record
   **`NOT ESTABLISHED`** and name the command a human runs (Story 10.1's rule, enforced by
   `tests/test_evidence_citation.py`).
3. ⛔ **Do not push, tag or `workflow_dispatch` to manufacture a citation** (10.1's DN-7).
4. ⛔ **Do not `pip install`, `pip uninstall` or otherwise change this venv.** Not to test the bound,
   not to "just check 0.26". If you believe the story cannot be proven without it — **HALT**.

#### 0.2 — ⛔ THE `DF-10-4-D` FENCE AND THE LOC BUDGET — BOTH BIND HERE, AND THE BUDGET IS EXACT

**The operator ruling stands for ALL of Epic 11: NO Epic 11 story may create or stage a new
`argus/**` source file.** The mechanism, re-verified this session:
`argus/dogfood/partition_plan.py::enumerate_minions_source_files` enumerates via **`git ls-files
argus`**, and `git ls-files` reports the **INDEX**, not `HEAD` — so the dogfood-audited population
moves the instant a new `argus/**` module is **staged**, before any commit, at the exact moment
`AI-E8-1` *requires* the `git add`. In Story 10.4 that turned five committed-artifact staleness tests
red mid-implementation and halted the story.

**Measured this session by executing `build_full_repo_plan('.')`:**

| Quantity | Measured 2026-08-12 | Meaning for this story |
|---|---|---|
| `git ls-files -- argus` | **72** | must still read **72** after you stage |
| `git status --porcelain -- argus/` | exactly **four ` M`** lines, **no ` A`** line | 11.1's three + 11.2's one. Add none; expect yours to join them as ` M`. |
| dogfood `scope_prefix` | **`argus/`** | `tests/**`, `pyproject.toml`, `action.yml`, `.github/**` are **outside** the audited population and cost **0** budget |
| `source_file_count` / `total_loc` | **72** / **20034** | unit 1 = **1330**, unit 2 = **14900**, unit 3 = **3804** |
| unit 1 id | `477ef77d7b65…` | must be byte-unchanged |
| unit 2 id | `82a3d605e61e…` (soft cap **15000**) | must be byte-unchanged |
| unit 3 id | `ed6d08f25ce3…` | must be byte-unchanged |

**🚩 THE CLIFF, MEASURED TO THE LINE.** The LOC map was perturbed in memory (nothing on disk touched)
and `build_full_repo_plan` re-run at each step:

| Perturbation | unit LOCs | partition ids |
|---|---|---|
| `argus/index/ast_index.py` **+99** | 1330 / **14999** / 3804 | **unchanged** ✅ |
| `argus/index/ast_index.py` **+100** | 1330 / **15000** / 3804 | **unchanged** ✅ |
| `argus/index/ast_index.py` **+101** | 1330 / **14743** / **4062** | **TWO IDS CHANGE** ❌ |
| `argus/shared/grammar_status.py` **+500** | 1330 / 14900 / **4304** | **unchanged** ✅ |
| `argus/shared/grammar_status.py` **+2000** | 1330 / 14900 / **5804** | **unchanged** ✅ |

**Read that table again, because it decides your design.** Unit 2 is a single cohesion blob at the
soft cap; the **101st** added line makes it oversized, the packer flushes earlier, and two of three
`partition_id` sha256 values move — turning five committed-artifact staleness tests red. **Unit 3 has
at least 2000 lines of headroom.**

**Which files are in which unit** (the three you will want):

| File | Unit | Budget there |
|---|---|---|
| `argus/index/ast_index.py` (554 lines) | **2** | shares the **100** |
| `argus/reports/generator.py` (774 lines) | **2** | shares the **100** |
| `argus/shared/grammar_status.py` (251 lines) | **3** | ≥ **2000** |

⛔ **Therefore the design rule, which is an AC (AC6.2): every line that CAN live in the pure contract
module MUST live there.** `argus/shared/grammar_status.py` is unit 3. This is not a style preference —
it is the difference between a green suite and five reds you did not cause. It also happens to be the
architecturally correct home (AR8, §C.1). The two are aligned; do not fight either.

**MANDATED HALTS:**

- If `git ls-files -- argus` is not **72** after you stage — **STOP and HALT**.
- If any `partition_id` changes, or unit 2's LOC exceeds **15000** — **STOP and HALT**.
- If you find the design genuinely needs a **new** `argus/**` module — **STOP and HALT** and say so.
  §B was proven to fit without one, but the operator ruling outranks §B.
- ⛔ **NEVER regenerate a committed dogfood artifact to make a staleness test pass.** That is the
  antipattern this project has refused three times. Regeneration is an operator decision, taken out
  of band, at a commit that genuinely contains the delta.

#### 0.3 — 🔴🔴 THE EPIC'S OWN PREMISE IS WRONG. RE-MEASURED PREMISES (AI-E10-3)

`AI-E10-3` requires every Epic 11 premise to be re-measured at create-story time and the divergence
recorded. For 11.1 two of three premises were stale; for 11.2 the central premise had **expired**;
for 11.3 the headline measurement **held exactly**. **For 11.4 the headline premise is the first one
that is affirmatively FALSE in the direction it names.** The epic-10 retrospective predicted this
(`SD-2`: *"the flip must be re-measured on the new loader"*). It was. Here is the result.

| Premise as `epics.md:2089-2101` / `architecture.md:573-577` / `pyproject.toml:19-24` write it | Measured on this tree, 2026-08-12 | Verdict |
|---|---|---|
| *"on `0.26.0` the cartridge self-audit flips `NOT_READY_FOR_RELEASE` → `RELEASE_READY`"* | **NOT REPRODUCIBLE AS STATED, in two independent ways.** (a) **Upstream:** `py-tree-sitter` 0.26.0's breaking changes are `Language.version`→`Language.abi_version`, `Language.query()`→`Query(...)`, `Parser.timeout_micros`/`QueryCursor.timeout_micros`→`progress_callback`, and `Point` becoming a tuple subclass rather than a namedtuple. **Argus uses none of them** — it uses `Language()`, `Parser()`, `parse()`, `root_node`, `has_error`, `.type`, `.children`, `.child_by_field_name`, `.start_point[0]`, `.text`; `grep -rn "Query\|timeout_micros\|\.version" argus/index/` finds no use. The grammar ABI floor is **unchanged**. §A.5. (b) **Behavioural:** when AST extraction is made to fail *totally* (the shape a core/ABI break would have), the cartridges land on **`INSUFFICIENT_COVERAGE` / exit 3 / `row_1_below_floor`**, **not** `RELEASE_READY` — because zero definitions means zero deep coverage and the **floor row fires first**. §A.3, scenarios C and D. | ❌ **FALSE as written** |
| *"a metadata bound constrains a resolver, never an already-installed environment … so it must also be asserted at runtime"* | **HOLDS, and is the durable half of the premise.** Measured: `argus/` contains exactly **one** `importlib.metadata` call site (`ast_index.py::_package_version`, line 263) and it **records** versions for the cache key. **There is no version comparison anywhere in `argus/`.** `pyproject.toml:26` pins `tree-sitter>=0.25.0,<0.26`; nothing at runtime reads it. | ✅ **holds — this is the story** |
| *"the degradation must not itself be a crash (NFR-R1) … a typed finding and a non-vouching verdict"* | **HOLDS, and the architecture already prescribes the exact shape.** `architecture.md:695-697`: *"Failure → typed finding, never an uncaught raise … the run still produces a verdict (degraded → `INSUFFICIENT_COVERAGE`)."* You are not inventing a degradation policy; you are routing a new cause into the one that exists. §B. | ✅ **holds — cite it** |
| *"the failure is silent today"* | **HOLDS, and is worse than "silent".** §A.2: the false green is **invisible on every surface Argus prints**, because `deep_ratio` is **unchanged** (5/6 before and after). The tool reports the *same* coverage while having lost the finding. | ✅ **holds — sharpened** |
| Retro `SD-2`: *"11.4 should **extend `GrammarFailure`** rather than invent a second mechanism — which also makes `DF-10-4-E` 11.4's problem to inherit"* | **HOLDS on both halves, and both are scoped in.** `GrammarFailure` has four members and a two-direction closure test that forces a fifth to be registered and driven (`tests/test_grammar_diagnosis.py::…-111`/`-115`). `DF-10-4-E` (`_render_grammar_remedy` has no exhaustiveness guard; its last branch is an unconditional fallthrough) carries `target_story: NONE — schedule against whichever future story next extends GrammarFailure's membership`. **This is that story.** §0.6 records the ruling. | ✅ **holds → AC1, AC4** |

**⛔ WHAT THIS MEANS FOR YOUR IMPLEMENTATION — the single most important paragraph in this file.**
**Do not build "assert `tree-sitter < 0.26`".** Three separate reasons, each sufficient:

1. It would be **built on a claim this story just disproved**, and it would encode that claim as a
   runtime behaviour — turning unverified folklore into shipped policy.
2. It is **vacuous by construction**. A version-string comparison never demonstrates that a wrong
   version changes parse behaviour. §A.2's false green happens at an **in-bound** version. A guard
   that pins the string is green on the very tree where the false green is live. **Story 11.3 failed
   its first review because its guard was blind to an ordinary YAML shape; 11.2's premise had
   silently expired. A version pin here is the same failure, third instance.**
3. It **cannot close the class**. Grammar packages drift independently of the core (this host runs
   grammars from four different minor lines — §A.4), and a vendored, patched or partially-installed
   grammar reports whatever version metadata it likes.

**Build the thing that actually decides it: a behavioural self-check of the toolchain.** The version
bound is *recorded evidence beside* the check, never the check itself. §B.

#### 0.4 — ⛔ ONE TEST IS ALREADY RED. IT IS `DF-11-1-A` AND IT IS NOT YOURS

`tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed`
**FAILS on this tree, before you touch anything.** Re-run in full this session (`pytest tests/` —
**1371 collected, 1370 passed, 1 failed**):

```
AssertionError: status-asserting document(s) exist but are not registered:
['epic-10-retro-2026-08-11.md']
```

**Attribution is PROVEN, not assumed.** Story 11.1's review adjudicated it by a positive git-stash
isolation experiment (all nine of 11.1's touched files reverted, the identical failure reproduced
from the untracked `epic-10-retro-2026-08-11.md` alone, stash popped content-identical). Stories 11.2
and 11.3 carried it forward unchanged. It is Story 10.1's own citation guard working **as designed**
on an Epic-10 artifact that was never registered.

**Ruled for this story: `DF-11-1-A` STAYS DEFERRED. Do not close it here** (recorded as **DN-9**):

1. It is an **artifact-registration** item about an Epic-10 retrospective document. It shares no
   line, no file and no defect class with tree-sitter toolchain validation.
2. Closing it means registering the retro in `_STATUS_DOCUMENTS`, which then obliges the retro itself
   to carry a run id **plus the sha it covers**, or a `NOT ESTABLISHED` marker. There is no such run
   id (§0.1), so closing it from here means either editing a signed Epic-10 retrospective or minting
   a citation this story is forbidden to create.
3. Its owner is **XAgent007 (operator)** by the ledger, not Engineering.
4. Precedent: Story 8.1's AC18 carve-out; 11.2's DN-7; 11.3's DN-8 — all ruled identically.

**What this obliges you to do (AC6.3):** your "full suite green" claim must carve this failure out
**BY NODE ID** and assert it is the **only** failure. ⛔ **A second red is yours, whatever its file.**
Do not add `epic-10-retro-2026-08-11.md` to `_STATUS_DOCUMENTS`, do not `git add` it, do not delete
it.

*(Standing red across four consecutive stories. Surfaced to the operator again as open question 1.)*

#### 0.5 — ⛔ NOTHING IS PUBLISHED BY THIS STORY

**No push. No tag. No release. No `workflow_dispatch`. No `pip install`. No venv change.** The
publish is **Story 12.9**, by design (`epics.md` Epic 11 preamble; `sprint-status.yaml` Epic 11
header). This story's own subject makes one temptation specific and it must be named: **you may not
change what is installed in order to observe your change.** See §0.1.4.

#### 0.6 — ⛔ FOUR OPEN LEDGER ITEMS. THREE ARE OUT; ONE IS RULED **IN**, WITH REASONS

| Item | Ruling | Reason |
|---|---|---|
| **`DF-11-2-A`** (six real test-name conventions unrecognised — every one a false negative) and **`DF-11-2-B`** (`c`/`php` ground with no convention at all) | ⛔ **OUT** | Both are **file-classification** defects in `argus/detectors/vacuous_test.py`, both carry `target_story: 12.5` and an owner in the ledger, and both *widen* classification and *move* verdicts on real repositories — the opposite shape to this story. 11.3 ruled identically. Do not touch, fix or re-file them. |
| **`DF-11-1-A`** | ⛔ **OUT** | §0.4. |
| **`DF-10-4-E`** — `_render_grammar_remedy`'s per-cause branching has no exhaustiveness guard; its last branch is an unconditional fallthrough, so a fifth `GrammarFailure` member would **silently render the core-runtime remedy** | ✅ **IN — scoped to this story (AC4.3)** | Its ledger entry says `target_story: **NONE — unscheduled; Engineering Lead to schedule** against whichever future story next extends `GrammarFailure`'s membership (none proposes a fifth cause today)`. **This story proposes the fifth cause.** Leaving it open would mean this story's own new cause renders the *wrong remedy* to an operator — reintroducing, in the same function, the exact defect Story 10.4 existed to close. The epic-10 retrospective anticipated this and assigned it here by name (`SD-2`). Cost is ~6 lines in a unit-2 file; budgeted in §0.2. |

⛔ **`DF-10-2-A`** (C/C++/Ruby/Rust parse and yield **zero definitions**) is a **different defect** and
is **OUT**: those grammars load, parse cleanly, and return an empty definition set for structural
reasons, not because the toolchain is unvalidated. **Do not conflate it with §A.2's degradation, and
do not let your self-check fire on it.** §C.4 is the specific trap.

⛔ **The untracked `argusdemo/demo.sh` at the repo root is an OPERATOR decision held for the epic
checkpoint.** It is not yours. Do not scope it, delete it, stage it or reference it.

---

### §A. What was measured, and what it changes

#### A.1 — 🚩 There is no version check anywhere in `argus/`. There never has been.

Measured by grep over `argus/**/*.py`:

| Question | Answer |
|---|---|
| `importlib.metadata` call sites | **exactly one** — `argus/index/ast_index.py::_package_version` (line 263) |
| What it does | `importlib.metadata.version(f"tree-sitter-{lang}")`, falling back to `"unknown"`; the result is **recorded** into `AstIndex.grammar_versions` for the Epic-5 cache key |
| Is the **core** `tree-sitter` version resolved at all? | **NO.** Only `tree-sitter-<lang>` is. The core package's version is never read by any line of `argus/`. |
| Any comparison, bound, range or assertion on any version? | **NONE.** `pyproject.toml:26` declares `tree-sitter>=0.25.0,<0.26`; **no runtime line reads it.** |
| Is `packaging` available to parse a specifier? | **Present in this venv at 26.2, but ONLY transitively** (via `bandit`/`build`). It is absent from `pyproject.toml`'s `dependencies` **and** its `[dev]` extra. ⛔ **Do not import it** — 11.3's DN-5 measured the identical trap with `PyYAML`. Stdlib only. |

`argus/shared/grammar_status.py` — the pure contract Story 10.4 created — is the natural home for the
bound, and it is **already proven pure** by `tests/test_grammar_diagnosis.py::…-119`, which asserts
its import set is a subset of `{__future__, enum, typing}`. That test is a **fence you must respect**:
the bound and the expectations are pure data; the probe that reads `importlib.metadata` is not, and
belongs in `ast_index.py`. This is the same split `cache/key.py` ↔ `ast_index.py` already uses for
`GrammarProvenance`, so there is a working precedent to copy rather than a pattern to invent.

#### A.2 — 🚩🚩 THE FALSE GREEN, DEMONSTRATED — exit 2 → exit 0, with `deep_ratio` UNCHANGED

**This is the measurement the story exists for. Reproduce it RED-first before you write a line of
fix.** Method: stage the real `vacuous_basic` cartridge, add four clean production modules so the
repository sits **above** the 60% deep gate (as this repository itself does — §A.6), commit, audit.
Then, **in memory only**, rename the tree-sitter call/reference node-type vocabulary
(`argus.index.ast_index._CALL_NODE_TYPES`) — the shape a grammar whose node names have drifted
actually has — and audit the **identical commit** again.

```
IN-BOUND  grammar : NOT_READY_FOR_RELEASE exit=2 deep=5/6 blocking=1
                    [('orphan_code', False), ('vacuous_test_ast', True)]
DRIFTED   grammar : RELEASE_READY          exit=0 deep=5/6 blocking=0
                    [('orphan_code', False), ('orphan_code', False), ('vacuous_test_heuristic', False)]
```

**Read every column.**

- **The verdict inverted.** `NOT_READY_FOR_RELEASE` → `RELEASE_READY`. **Exit 2 → exit 0.** A CI gate
  that blocked now passes.
- **The planted defect is still there and Argus still half-sees it** — but `vacuous_test_ast`
  (`depth_supported is not None`, verdict-**eligible**) silently became `vacuous_test_heuristic`
  (`depth_supported is None`, advisory-only). Cross-cutting #6 guarantees a heuristic-only finding
  can **never** move the verdict. The moat that protects against a false 🔴 is the mechanism that
  produces this false 🟢.
- **🚩 `deep_ratio` IS UNCHANGED: 5/6 in both runs.** This is why the failure is not merely silent
  but *undetectable from outside*. Every honesty surface this project built — the coverage ledger,
  the negative-assurance scope statement, the plain-English report, the disclosure line — reports the
  **same numbers** in both runs. There is no figure a user could compare.

**This is the false-green path an AC must demand be demonstrated.** Not a version assertion. This.

#### A.3 — 🚩 The epic's stated flip does NOT reproduce, and the reason is load-bearing for your design

Same method, four degradation shapes, run over the real cartridge corpus:

| # | Simulated drift (in-memory) | `vacuous_basic` | `clean_control` |
|---|---|---|---|
| A | none (baseline, `tree-sitter 0.25.2`) | `NOT_READY_FOR_RELEASE` / 2 / deep 1/2 / blk 1 | `RELEASE_READY` / 0 / deep 2/3 |
| B | call/edge node types renamed, definitions intact | `INSUFFICIENT_COVERAGE` / 3 / deep 1/2 / **blk 0**, finding downgraded to `vacuous_test_heuristic` | `RELEASE_READY` / 0 |
| C | the `name` **field** renamed (definitions found but unnamed) | `INSUFFICIENT_COVERAGE` / 3 / **deep 0** / `row_1_below_floor` | `INSUFFICIENT_COVERAGE` / 3 |
| D | only `function_definition` renamed (classes intact) | `INSUFFICIENT_COVERAGE` / 3 / **deep 0** | `INSUFFICIENT_COVERAGE` / 3 |
| E | test-named definitions lost only, coverage preserved | `INSUFFICIENT_COVERAGE` / 3 / deep 1/2 / **blk 0**, finding **gone entirely** | `RELEASE_READY` / 0 |

**Two conclusions, both binding:**

1. **The cartridges cannot show the epic's flip, and never could.** They sit at deep 1/2 = 50%, below
   the 60% row-3 gate, so they can only fall to `INSUFFICIENT_COVERAGE`. The epic's sentence names a
   transition the corpus it cites is structurally incapable of making. §A.2 shows the flip **is** real
   — it just needs a repository above the gate, which is what a real user's repository is, and what
   **this** repository is (§A.6).
2. **🔑 Total AST loss is ALREADY SAFE, and that is the shape your fix should route into.** Scenarios
   C and D show that when definitions vanish, `deep_count` → 0, the **floor row fires first** (row 1
   keeps precedence over everything), and the verdict is the honest `INSUFFICIENT_COVERAGE` / exit 3.
   **The existing machinery already withholds a verdict correctly when the index is empty.** You do
   not need a new verdict, a new row, a new threshold, or a change to `verdict_gate.py`. You need the
   unvalidated-toolchain case to *reach* that state. §B.

#### A.4 — The toolchain on this host, exactly

| Package | Installed | `pyproject.toml` declares |
|---|---|---|
| `tree-sitter` (core) | **0.25.2** | `>=0.25.0,<0.26` (base dep, `:26`) |
| `tree-sitter-python` | **0.25.0** | `>=0.25.0,<0.26` (base dep, `:27`) |
| `tree-sitter-javascript` | 0.25.0 | `>=0.25.0,<0.26` (`[languages]`) |
| `tree-sitter-go` | 0.25.0 | `>=0.23.0,<0.26` |
| `tree-sitter-typescript` | 0.23.2 | `>=0.23.0,<0.26` |
| `tree-sitter-java` | 0.23.5 | `>=0.23.0,<0.26` |
| `tree-sitter-rust` | 0.24.2 | `>=0.23.0,<0.26` |
| `tree-sitter-c` | 0.24.2 | `>=0.23.0,<0.26` |
| `tree-sitter-cpp` | 0.23.4 | `>=0.23.0,<0.26` |
| `tree-sitter-ruby` | 0.23.1 | `>=0.23.0,<0.26` |
| `tree-sitter-php` | 0.24.1 | `>=0.23.0,<0.26` |
| Python | **3.11.15** | `requires-python >=3.10` |

**🚩 Note the spread: four different minor lines across the grammars, all in-bound.** A single core
version number tells you nothing about the nine grammar packages that actually produce the nodes. It
is a second, independent argument for a behavioural check over a metadata check.

#### A.5 — What `py-tree-sitter` 0.26.0 actually changed (read 2026-08-12)

| Change | Does Argus use it? |
|---|---|
| `Language.version` removed → `Language.abi_version` | **No** — `grep` finds no `.version` on a `Language` in `argus/` |
| `Language.query(source)` removed → `Query(language, source)` | **No** — Argus does structural walking, not queries |
| `Parser.timeout_micros` / `QueryCursor.timeout_micros` removed → `progress_callback` | **No** |
| `Point` is now a tuple subclass rather than a namedtuple | **Used, but compatibly** — `node.start_point[0]` / `end_point[0]` index positionally, which both support |
| `Language()`, `Parser()`, `Node.children`, `Node.child_by_field_name`, `Node.has_error`, minimum grammar ABI | **unchanged upstream** |

⚠️ **This does not make 0.26 safe and it is not a licence to widen the pin.** It makes the *stated
reason* for the pin unproven. **⛔ Do not touch `pyproject.toml`'s bounds** — that is a packaging
decision with an owner (§D), and this story is the one that adds the *runtime* defence precisely so
that the pin stops being the only defence. What you **must** do is stop the project from repeating an
unverified sentence: AC5 corrects it in the three places it is written.

#### A.6 — Baseline, re-measured this session (LOCAL — see §0.1)

| Gate | Measured 2026-08-12 |
|---|---|
| `pytest tests/` | **1371 collected · 1370 passed · 1 failed** — the failure is `DF-11-1-A` (§0.4), by node id |
| `mypy argus` | **Success: no issues found in 72 source files** |
| `python -m argus.cli audit .` | `verdict=RELEASE_READY deep_ratio=61/167 blocking_findings=0 **assessed_deep_ratio=61/77** scope=application held_out=90`, exit 0 |
| `git ls-files -- argus` | **72** |
| dogfood units | 1330 / **14900** / 3804 · ids `477ef77d7b65…` / `82a3d605e61e…` / `ed6d08f25ce3…` |
| `bandit` | **0 High / 0 Medium (19 Low)** — ATTRIBUTED to Story 11.2's run at this tree, not re-measured here |
| coverage | **95.82%** — ATTRIBUTED to Story 11.2's run at this tree, not re-measured here |

🚩 **`assessed_deep_ratio = 61/77 = 79%` — this repository is ABOVE the 60% row-3 gate.** That is
exactly the §A.2 condition. **Argus's own dogfood self-audit is a live false-green surface**, and
after your change it must still read `RELEASE_READY` on an in-bound toolchain (AC6.5) — a green you
must not break, sitting one degraded grammar away from a green you must make impossible.

---

### §B. The shape — proven viable under the fence and the budget, not mandated

You own the design (§0.2's HALTs are the only hard boundaries). This shape was checked against every
fence, the 100-line budget, the purity test and the existing closure guards, and it fits. Deviate
with a recorded reason.

**B.1 — Pure contract, in `argus/shared/grammar_status.py` (unit 3, ≥2000 lines of headroom).**
1. A **fifth `GrammarFailure` member** — e.g. `RUNTIME_UNVALIDATED` — and a token that carries **no
   `<lang>` suffix**, for the same reason `CORE_RUNTIME_TOKEN` carries none: an unvalidated toolchain
   is a fact about the runtime, not about one language, and suffixing it would invite a
   per-language remedy that cannot help. The module's own import-time
   `_assert_prefixes_are_unambiguous()` already forbids a token that another prefix could swallow —
   it will tell you at import if you pick a bad spelling.
2. The **declared supported range**, as pure data (a lower bound and an exclusive upper bound as
   integer tuples, not a specifier string — you have no `packaging`, §A.1).
3. The **behavioural expectation corpus**: for each language, a tiny source snippet and the exact
   `(definitions, edges)` Argus must extract from it. Pure data. This is where the story's real
   weight lives, and unit 3 is where it costs nothing.
4. A **pure comparison** function `(observed_version_tuple) -> bool`, and a pure
   `(extracted, expected) -> bool` verdict on one canary. No I/O, no imports beyond
   `{__future__, enum, typing}` — `…-119` will fail you otherwise.

**B.2 — Impure probe + a fifth arm, in `argus/index/ast_index.py` (unit 2, share of 100 lines).**
Add **ARM 0** to `_get_parser_for_lang`, ahead of ARM 3's construction, or immediately after it:
after a parser is successfully constructed for a language, **parse that language's canary and compare
the extraction against the pure expectation**. If it does not match — or if the resolved core version
falls outside the declared range — return `_ParserLoad(None, GrammarFailure.RUNTIME_UNVALIDATED)`.
The existing per-`(lang, entry_point)` load cache means **the canary is parsed at most once per
language per run**, so the cost is bounded and deterministic.

**Why returning "no parser" is the right degradation, not a blunt one.** It is precisely what the
user story asks for — *"withhold a verdict rather than compute one"* — and §A.3 scenarios C/D
**measured** that it lands on `INSUFFICIENT_COVERAGE` / exit 3 / `row_1_below_floor`: the honest
"Argus has not assessed enough to vouch" state, which `architecture.md:695-697` already names as the
prescribed degradation. **No verdict-gate change. No `pipeline.py` change. No new row. No new
threshold.** The recorded `parse_failure_reason` token is the typed record the epic asks for, and it
flows to the operator through the report path Story 10.4 already built.

**B.3 — Report side, in `argus/reports/generator.py` (unit 2).** One new branch in
`_render_grammar_remedy` for the fifth cause, naming the remedy that actually works (install a
supported `tree-sitter`; the observed version is obtained by the operator running `pip show
tree-sitter`, not persisted — see DN-5), **plus** `DF-10-4-E`'s exhaustiveness guard: the trailing
unconditional fallthrough becomes an explicit final arm with a `raise` on an unregistered member, so
a sixth cause can never silently render a fourth cause's remedy.

**B.4 — Tests (outside `argus/`, budget-free).** New file
`tests/test_grammar_runtime_validation.py`, area `TC-ArgusAgent-INDEX-001-120`… (the INDEX-001 series
is used up to **119**; start at **120**). Extend, never duplicate,
`tests/test_grammar_diagnosis.py`'s existing closures where they are the right home (AR7 / §3.3
forbid a second mechanism where one exists).

**B.5 — Regression watchlist: the four things your change passes closest to.**

| # | What | Why it will bite |
|---|---|---|
| 1 | **`tests/test_grammar_diagnosis.py::test_verdict_and_coverage_are_identical_across_all_four_causes` (`…-114`)** | It asserts all `GrammarFailure` modes in `_MODES` produce an **identical** graded outcome, and its failure message literally says *"the 11.4 fence crossed"*. Your fifth cause **does** change the verdict — that is the point of the story. ⛔ **Do not delete or weaken this test.** Scope it explicitly to the **four load causes**, assert it still covers exactly four (so it cannot go vacuous), and add a **separate** assertion for the refusal cause. Record the reasoning in the docstring: 10.4's DN-9 fenced the version comparison **to this story**, so this is the sanctioned crossing, not a regression. |
| 2 | **`…-111` / `-115`** — the registry closure and the AST walk over `_get_parser_for_lang`'s arms | They will **fail** the moment you add a member without an arm, or an arm without a member. That is them working. Make the fifth arm satisfy the same "named, non-silent, non-redundant handler" shape. |
| 3 | **`…-119`** — the purity test on `grammar_status.py` | It caps that module's imports at `{__future__, enum, typing}`. Your canary corpus and bound are data; your probe is not. |
| 4 | **`tests/test_cache_key.py` / `test_cache_invalidation.py` / `test_memo_store.py`** | ⛔ **Do not add the core version to the R3 cache key.** `CACHE_KEY_SCHEMA_VERSION` and golden fixtures move together, and that is a determinism change this story has not reasoned about. §D. |
| 5 | **`tests/test_multilanguage_audit.py`** | It honours `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` (set by `audit-ci.yml`) to turn a skip into a hard failure. Your canaries must **pass for every installed grammar on this host** — if one of the ten fails its canary, you have found either a real drift or a wrong expectation; **investigate, do not relax the expectation.** |

---

### §C. Design constraints a reviewer will check

**C.1 — AR8, the pure/impure arrow.** shell → contract, never the reverse. `grammar_status.py` may
not import `importlib`, `tree_sitter`, `os`, `sys`, `pathlib`, `subprocess` or `argus`. The precedent
is `GrammarProvenance` (defined in pure `cache/key.py`, resolved in impure `ast_index.py`) and the
epic-10 retro records that this boundary *"held under pressure"*.

**C.2 — AR10 / `architecture.md:701-712`.** Classify by **arm position**, never by exception type or
message. Persist **no** exception message, `repr`, traceback or host path (NFR-S1). A broad
`except Exception` needs `# noqa: BLE001` **and** a comment naming the degraded outcome it records.
A tuple whose members subclass one another is **forbidden**. `BaseException` stays uncaught.

**C.3 — 🔑 NON-VACUITY IS THE LOAD-BEARING PROPERTY OF THIS STORY.** Three prior stories in this epic
were reviewed on exactly this axis and one failed. Every guard you write must have a **negative
control that fires** and a **positive control that does not**, driven through the **real seam**, and
must assert **non-zero** work was done (non-zero canaries run, non-zero languages checked, non-zero
arms walked). ⛔ **A guard that goes green by finding nothing is a failed guard**, not a passed one.

**C.4 — ⛔ THE TRAP THAT WILL BREAK YOUR CANARY IF YOU IGNORE IT (`DF-10-2-A`).** **C, C++, Ruby and
Rust load, parse cleanly, and extract ZERO definitions on this tree.** That is a known, filed,
open defect about node-type coverage — **not** a toolchain-validation failure. If your canary asserts
"≥1 definition extracted" uniformly across all ten languages, **it will fire on four healthy
grammars and take the whole audit to `INSUFFICIENT_COVERAGE` on any polyglot repository.** Your
expectations must be **per-language and measured on this host**, not assumed. Measure all ten before
you pin any. If a language's honest current expectation is "parses, zero definitions", pin **that**,
and say in the docstring that `DF-10-2-A` owns changing it.

**C.5 — The bound must have exactly one source of truth.** If the supported range lives in
`grammar_status.py` **and** in `pyproject.toml`, it will drift — this project has paid for a
duplicated enumerable fact at least four times (`source_languages.py`'s docstring lists the tally).
A test must **parse `pyproject.toml` and assert equality with the pure constant**, in both
directions, failing loudly if either is unparseable. Stdlib only: `tomllib` is in the 3.11 standard
library, and `requires-python` is `>=3.10` — ⛔ so `tomllib` is **not** guaranteed on the minimum
supported interpreter. Use `re` over the file text, or guard the `tomllib` import; either way the
guard must **fail loudly** rather than skip when it cannot parse.

**C.6 — Determinism (AR4/NFR-P1/NFR-D2).** The canary parse is in-process, over frozen data, with no
clock, no randomness and no iteration-order reliance. It must not change any recorded artifact on an
in-bound toolchain — AC6.5 pins that by re-running the dogfood audit and comparing.

**C.7 — No new dependency.** `argus/` gains no import that is not already declared. §A.1: `packaging`
is present transitively and is **not** yours to use.

---

### §D. ⛔ FENCES — what this story must NOT touch

| Fenced | Owner | Why, and where the line sits |
|---|---|---|
| **`pyproject.toml` dependency bounds — the `<0.26` pin and the `[languages]` ranges** | **12.5 / operator** | §A.5 shows the pin's *stated reason* is unproven; it does **not** show the pin is wrong. Widening it is a packaging decision (NFR-P3, `architecture.md:579-583` records it as *"a decision, not decided here"*). **This story adds the runtime defence; it does not relax the resolver.** You may correct the *prose comment* that states the false claim (AC5.2) — you may not change the specifier. |
| **`argus/verdict/verdict_gate.py` — the FR16 decision table, its four rows, thresholds, exit codes, `Verdict` membership** | **frozen contract** | §A.3 measured that the existing rows already produce the correct honest outcome. Any change here is a contract change Epic 11 has not reasoned about. |
| **`argus/pipeline.py` — must be BYTE-UNCHANGED** | **12.1** | NFR-M1: **1331 lines against a 1200 cap**, breached today with no repo-wide gate. §B was designed to be reachable without it. If you believe you need it — HALT. |
| **The R3 cache key / `CACHE_KEY_SCHEMA_VERSION` / `GrammarProvenance`'s shape** | **12.x** | Adding the core version to the key is defensible and is **not this story**: it moves a schema version and a committed golden, and 10.2 already paid for that migration once. File it, do not do it. |
| **Operator-facing prose, `--help` text, the observed-version display** | **12.8** | 12.8 *"extends 10.4's diagnosis principle to the user surface"*. Your remedy line states the supported range and the command to inspect; a richer diagnostic is 12.8's (DN-5). |
| **`DF-10-2-A`** (C/C++/Ruby/Rust extract zero definitions) | already filed, open, `target_story: NONE` | A **different** failure. §C.4. Do not fix it, and do not let your canary fire on it. |
| **`DF-11-2-A` / `-B` / `DF-11-1-A`** | 12.5 / operator | §0.6, §0.4. |
| **`epics.md`, `E-PRD/*`, `README.md`, `action.yml`, `.github/workflows/**`** | — | This story corrects **no requirement**. `architecture.md` §Packaging + §Error/Degradation and the `pyproject.toml` **comment** are the only specification surfaces you may touch, and only as AC5 defines. If you are editing a contract document, scope has leaked — stop and record why. |
| **Publishing, tagging, `workflow_dispatch`, any `pip` command** | 12.9 / operator | §0.5, §0.1.4. |
| **The Epic 13 precision gate; the FR34 disclosure 11.1 shipped** | Epic 13 / 11.1 | Nothing here clears the gate or reworks the disclosure. |
| **`argusdemo/demo.sh`** | operator, epic checkpoint | §0.6. |

---

### §E. Traps previous stories already paid for — the six that apply

| # | Trap | What it costs you here |
|---|---|---|
| **E.1** | **AI-E3-1 — a keystone test green over its own keystone bug** (Story 3.4). | **RED-first is MANDATORY for AC2.** Reproduce §A.2's exit-2→exit-0 flip against the **pre-change** tree and paste the transcript into the Dev Agent Record. A test written after the fix proves nothing about a defect that was never demonstrated. |
| **E.2** | **10.2's hand-list was wrong three times; 11.3's ledger coordinate was the seventh stale one.** | Do not close this with a hand-typed language list or a hand-typed version table. Derive from `LANGUAGE_BY_SUFFIX` / `GRAMMAR_PACKAGE_BY_LANGUAGE`, and pin the pyproject↔constant equality (§C.5). |
| **E.3** | **Positive control, both directions** (10.1 / 10.3 / 10.4). | A simulated out-of-bound version and a simulated drifted vocabulary must **fire**; the real in-bound toolchain must **not**. ⛔ **Never by installing or uninstalling a real package** (§0.1.4) and never by mutating a shared registry outside a `monkeypatch.context()`. |
| **E.4** | **A guard that passes vacuously** (10.3's `-39`, 11.3's blind run-block resolver). | §C.3. Assert non-zero canaries, non-zero languages, non-zero arms. |
| **E.5** | **AI-E8-1 / -E8-2 — `git diff` cannot see an untracked path.** | `git add` this story file **and** your new test file before you claim a write-set fence. Verify with `git status --porcelain` **and** `git diff --stat`. |
| **E.6** | **11.3's fix iteration 1: a guard that was blind to an ordinary shape of its own subject.** | Your canary must be exercised for **every language that actually loads on this host** — ten of them (§A.4) — not just Python. A Python-only canary is the same blindness. |

---

## Acceptance Criteria

### AC1 — A fifth cause exists, is registered, and is reachable from the real loader

1. `GrammarFailure` gains **exactly one** new member meaning *"a parser was constructible, but the
   toolchain did not pass Argus's validation"*, with a token that carries **no `<lang>` suffix** and
   that the module's import-time prefix-ambiguity assertion accepts.
2. `_get_parser_for_lang` gains a **corresponding arm** that returns it. The arm is named,
   non-silent, and non-redundant in the sense `…-115` enforces; the existing four arms are
   **behaviourally unchanged** (AC4.1 pins this).
3. `registered_failures()` / `reason_token_for()` / `classify_reason()` round-trip the new token in
   both directions, and the existing `…-111` registry closure passes **without being relaxed**.
4. The token spelling is **locked in the story** by the dev in the Dev Agent Record before the tests
   are written, so a later rename is a recorded decision rather than a drift.

### AC2 — 🔑 THE FALSE GREEN IS DEMONSTRATED RED-FIRST, THEN PROVEN CLOSED

1. A committed test **reproduces §A.2 exactly**: a staged repository above the 60% deep gate with a
   planted vacuous test; audit once with the real toolchain → **`NOT_READY_FOR_RELEASE`, exit 2,
   ≥1 verdict-eligible finding**; audit the identical commit again with a **simulated drifted
   extraction vocabulary** → and assert the **pre-fix** behaviour is the false green.
2. The pre-fix transcript (exit 2 → exit 0, `deep_ratio` unchanged in both runs) is **captured
   against the unmodified tree** and pasted into the Dev Agent Record. ⛔ A test authored after the
   fix, with no recorded pre-fix red, does **not** satisfy this AC.
3. **After the fix**, the same drifted run must **not** produce `RELEASE_READY` and must **not** produce
   exit `0`. The test asserts the *property* — "no green under an unvalidated toolchain" — not a
   specific replacement verdict, so a later legitimate change to the decision table cannot silently
   void it.
4. The test asserts, in the same run, that the **`deep_ratio` alone cannot distinguish the two
   states** pre-fix — i.e. it pins *why* this was undetectable — so the story's premise cannot
   silently expire the way 11.2's did.
5. ⛔ **A version-string assertion does not satisfy any part of AC2.** The demonstrated drift in AC2.1
   happens at an **in-bound** version.

### AC3 — The check is behavioural, per-language, and measured — not a version comparison

1. For **every language that loads on this host**, a pinned canary source and its **measured**
   expected extraction exist. The expectations are **measured before they are pinned**, and the
   measurement is recorded in the Dev Agent Record as a ten-row table.
2. The canary runs **through the real loader seam** — the same `_get_parser_for_lang` every audit
   uses — and at most **once per (language, entry point) per run** (the existing load cache).
3. A guard proves the canary is **actually reached** by a real `build_ast_index` call: it asserts a
   non-zero number of canaries executed. A canary that never runs is the vacuity failure of §C.3.
4. ⛔ **`DF-10-2-A` must not fire it.** The four languages that legitimately extract zero definitions
   on this tree (§C.4) pass their canaries. A test asserts this by name for each of the four, so a
   future change that makes them fire is caught as a regression rather than shipped as a mass
   downgrade.
5. The declared version bound is **recorded and checked as a second, independent signal** — an
   out-of-bound core version also yields the fifth cause — but a test proves the behavioural check
   **fires on its own** when the version is in bound (AC2.3 is that proof).

### AC4 — Nothing Story 10.4 established is weakened, and `DF-10-4-E` is closed

1. The four existing causes still produce **identical** graded outcomes to each other
   (`…-114`'s invariant), the test still covers **exactly four** load causes, and its scope is
   narrowed **explicitly and with a docstring reason** rather than by deletion or by loosening the
   assertion. A separate assertion covers the fifth cause's **deliberately different** outcome.
2. `…-111`, `-115` and `-119` pass **unrelaxed**. In particular `grammar_status.py`'s import set
   remains a subset of `{__future__, enum, typing}`.
3. **`DF-10-4-E` is closed**: `_render_grammar_remedy`'s trailing unconditional fallthrough becomes an
   explicit final arm, and an unregistered `GrammarFailure` member raises rather than silently
   rendering another cause's remedy. A test drives **all five** causes to the operator surface and
   asserts each gets **its own** remedy, plus a negative control proving an unregistered member
   raises. The ledger entry is marked closed with the date and this story id.
4. The fifth cause's operator remedy names the **supported range** and the command to inspect the
   installed version. ⛔ It persists **no** version string, exception message or host path (NFR-S1,
   10.4 DN-5).

### AC5 — The three places that state the false claim are corrected

1. **`architecture.md:573-577`** — the 🚩 *"On `0.26.0` the cartridge self-audit flips
   `NOT_READY_FOR_RELEASE` → `RELEASE_READY`"* block is corrected to what §0.3 and §A.3/§A.5
   measured: the claim is **unverified upstream and not reproducible on the cited corpus**; the pin
   is **retained** as conservative-by-default with its reason restated honestly; and the runtime
   defence this story adds is recorded as the thing that now carries the guarantee. **Struck, not
   deleted** (§3.4 evidence immutability) — the original sentence stays legible with its correction
   beside it.
2. **`pyproject.toml:19-24`** — the same claim in the dependency comment is corrected the same way.
   ⛔ **The specifier itself is unchanged** (§D).
3. **`epics.md` Story 11.4's first AC** — corrected in place, dated, with the reason, following the
   10.2 precedent for an enumeration/premise fix in an unstarted story. The story's *intent* is
   unchanged; only the false measurement is.
4. **`deferred-work.md`** — append-only: `DF-10-4-E` closed (AC4.3), and any new item this story
   discovers filed with an owner and a `target_story`. The append-only property is verified
   **programmatically** (`after.startswith(before)`), not by eye.
5. A test asserts **no surviving occurrence** of the uncorrected claim shape across the artifact set,
   with a positive control proving the search would find one if it existed.

### AC6 — Fences, budget, gates, and the one permitted red

1. **`git ls-files -- argus` is exactly 72** after staging. `git status --porcelain -- argus/` shows
   only ` M` lines and **no ` A` line**. ⛔ **HALT** if either moves.
2. **Dogfood unit 2 total LOC ≤ 15000**, and **all three `partition_id`s byte-unchanged**
   (`477ef77d7b65…` / `82a3d605e61e…` / `ed6d08f25ce3…`). Re-measure by executing
   `build_full_repo_plan('.')` **after** staging, and record the three ids and three LOC figures.
   ⛔ **HALT** if any moves. ⛔ **NEVER regenerate a committed dogfood artifact to make a staleness
   test pass.**
3. **Full suite green except one**: `pytest tests/` with
   `tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed`
   carved out **by node id**, asserted to be the **only** failure. Report collected/passed/failed
   counts against the **1371 / 1370 / 1** baseline.
4. **`mypy argus` clean on 72 source files.** No new `# type: ignore` without an inline reason.
5. **`python -m argus.cli audit .` still returns `RELEASE_READY`, exit 0**, with
   `assessed_deep_ratio` unchanged at **61/77** — i.e. the in-bound path is byte-behaviour-identical
   and this story did not downgrade Argus's own audit. ⛔ **HALT** if the dogfood verdict moves.
6. Every figure labelled **LOCAL**; an `audit-ci.yml` run id **plus its sha**, or **`NOT
   ESTABLISHED`** with the command a human runs. ⛔ No push, tag, dispatch, or `pip` command.
7. **`argus/pipeline.py` byte-unchanged**; `verdict_gate.py` byte-unchanged; no new dependency; no
   cache-key or schema-version change. Verified with `git diff --stat`, not asserted.

---

### §F. Write set — exactly this, nothing else

| Path | Change | Unit / budget |
|---|---|---|
| `argus/shared/grammar_status.py` | **UPDATE** — fifth member, token, bound, canary corpus, pure predicates | unit 3, ≥2000 free |
| `argus/index/ast_index.py` | **UPDATE** — the fifth arm + the impure probe. **Keep it minimal.** | unit 2, shares 100 |
| `argus/reports/generator.py` | **UPDATE** — fifth remedy branch + `DF-10-4-E`'s exhaustiveness arm | unit 2, shares 100 |
| `tests/test_grammar_runtime_validation.py` | **NEW** — `TC-ArgusAgent-INDEX-001-120`… | outside scope, free |
| `tests/test_grammar_diagnosis.py` | **UPDATE** — `…-114` scoping + the fifth-cause assertions | outside scope, free |
| `_bmad-output/design-artifacts/ArgusAgent/architecture.md` | **UPDATE** — AC5.1 only | — |
| `pyproject.toml` | **UPDATE** — AC5.2, the **comment** only | — |
| `_bmad-output/design-artifacts/ArgusAgent/epics.md` | **UPDATE** — AC5.3 only | — |
| `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` | **APPEND** — AC5.4 | — |
| `CHANGELOG.md` | **UPDATE** — one entry | — |
| THIS story file | **UPDATE** — Dev Agent Record; `git add` it (E.5) | — |

⛔ **Anything outside this table is scope leak.** ⛔ **No `argus/**` file is CREATED.**

---

## Tasks / Subtasks

- [x] **T0 — Re-derive the baseline** (AC6). `git ls-files -- argus`; `git status --porcelain`;
      `build_full_repo_plan('.')` → three ids + three LOCs; `pytest tests/` counts; `mypy argus`;
      `python -m argus.cli audit .`. Paste all of it into the Dev Agent Record **before** editing.
- [x] **T1 — 🔑 Reproduce the false green RED-first** (AC2.1, AC2.2, E.1). Build §A.2's above-the-gate
      repository, capture exit 2 → exit 0 with `deep_ratio` unchanged, paste the transcript.
- [x] **T2 — Measure the ten canary expectations** (AC3.1, §C.4). Run every installed grammar through
      the real loader over a candidate snippet; record the ten-row table; only then pin it.
- [x] **T3 — Pure contract** (AC1.1, AC1.3, AC3.1, AC3.5) in `grammar_status.py`. Confirm `…-119`
      still passes after every edit.
- [x] **T4 — The fifth arm + probe** (AC1.2, AC3.2) in `ast_index.py`. **Re-measure unit-2 LOC after
      this task** (AC6.2) — this is the task that can blow the budget.
- [x] **T5 — Report side + `DF-10-4-E`** (AC4.3, AC4.4) in `generator.py`. Re-measure unit-2 LOC again.
- [x] **T6 — Tests** (AC2.3–2.5, AC3.3, AC3.4, AC4.1, AC4.2, AC5.5) with both-direction controls and
      explicit non-vacuity assertions.
- [x] **T7 — Corrections** (AC5.1–5.4): architecture, pyproject comment, epics AC, ledger append
      (verified programmatically), CHANGELOG.
- [x] **T8 — Gate run** (AC6). Stage everything including this file, then re-measure **all** of T0 and
      compare. HALT on any fence movement rather than adjusting an artifact.

### Review Findings

**Code review (iteration 1, 2026-08-12, model: Sonnet).** Adversarial re-derivation of every load-bearing
claim, ON DISK, independent of the Dev Agent Record's own transcripts. Method and evidence below; nothing
in this section was transcribed from the story's own tables without being re-executed.

**What was independently re-run and confirmed, item by item against the reviewer's ten adjudication
points:**

1. **False green real and closed, reconstruction faithful.** Ran
   `tests/test_grammar_runtime_validation.py::test_a_drifted_grammar_cannot_produce_a_green_verdict`
   (`-125`) as part of the full suite. Read `_disable_the_fix` (`ast_index.py`,
   `monkeypatch.setattr(ast_index, "_toolchain_is_validated", lambda *a, **k: True)`) — this disables the
   *actual* new predicate at the *actual* call site, i.e. it reconstructs the real pre-fix control flow
   rather than a canary-shaped strawman. Confirmed PASS in the full run (below).
2. **No version assertion shipped.** Read `grammar_status.py` in full: the mechanism is
   `_toolchain_is_validated`'s behavioural canary; `core_version_is_supported` is an explicit second,
   weaker signal (DN-1). `git diff -- pyproject.toml` shows the dependency **comment** rewritten; the
   specifiers `tree-sitter>=0.25.0,<0.26` / `tree-sitter-python>=0.25.0,<0.26` are byte-identical to
   `HEAD`. Confirmed.
3. **DEV-1 observable, attacked.** `canary_matches` requires TOTAL equality on `parse_error`,
   `vocabulary`, `definitions` AND `edges` — not "non-empty intersection." A degraded grammar that
   destroys extraction would already fail on `definitions`/`edges` alone; `vocabulary` is the field that
   additionally catches Ruby's vacuous-by-construction case (`((), ())`, satisfiable by a broken grammar
   on `definitions`/`edges` alone). `_observe_canary` recomputes its "known" node-type set from the
   *live* `_DEF_KIND_BY_NODE ∪ _CALL_NODE_TYPES` on every call, so a drift to those tables (§A.2's
   simulated attack) is visible in the canary's own observation, not just in production extraction — the
   check cannot be defeated by drifting the table independently of what the canary measures. Residual,
   disclosed limitation (not a defect): a finite pinned snippet cannot prove universal correctness for
   every possible input the toolchain will see; this is inherent to any canary/sample-based check and is
   explicitly named in `GrammarCanary`'s and `DEV-1`'s own docstrings as an accepted tradeoff. **Low —
   accepted, not actionable.**
4. **Eleven expectations, DF-10-2-A accommodation.** `tests/test_grammar_runtime_validation.py::-120`
   through `-124` measure the corpus against the live loader and against `LANGUAGE_BY_SUFFIX` in both
   directions; `-123` names `c`, `cpp`, `ruby`, `rust` explicitly and asserts their `definitions == ()`
   pinning is deliberate, not accidental. Confirmed by execution (full suite green on these tests).
5. **DF-10-4-E closure, injected and reverted.** Reviewer edited `grammar_status.py` to add a sixth
   `GrammarFailure` member (`HYPOTHETICAL_SIXTH`, registered with its own token so import-time purity
   held), added no arm and no remedy branch, and re-ran the suite: `test_loader_has_no_unnamed_swallowed_or_redundant_arm`
   (`-115`), `test_registry_and_behavioural_matrix_close_over_each_other` (`-116`),
   `test_this_guard_cannot_pass_vacuously` (`-118`), and
   `test_all_five_causes_render_their_own_remedy_and_a_sixth_raises` (REPORT `-33`) all went **RED**
   exactly as claimed. Reverted the edit; `git diff --stat -- argus/shared/grammar_status.py` after
   revert is byte-identical to before the experiment (325 insertions / 13 deletions, unchanged).
   Confirmed genuinely non-vacuous.
6. **Byte-unchanged fences.** `git diff --numstat -- argus/pipeline.py argus/verdict/verdict_gate.py argus/cache/key.py`
   → empty. Confirmed byte-unchanged.
7. **Fences and budget, re-derived by execution, not by reading the table:**
   - `git ls-files -- argus` → **72**. `git status --porcelain -- argus/` → six ` M` lines
     (`cli.py`, `detectors/vacuous_test.py`, `index/ast_index.py`, `reports/generator.py`,
     `shared/grammar_status.py`, `verdict/negative_assurance.py`), **no ` A`** — confirming
     `grammar_status.py` was extended, not created.
   - Ran `build_full_repo_plan('.')` directly: units **1330 / 14987 / 4116**, partition ids
     `477ef77d7b65…` / `82a3d605e61e…` / `ed6d08f25ce3…` — all three **byte-unchanged**, unit 2 at
     **14987/15000 (13 lines of slack)**. This independently confirms the operator-facing headroom
     figure: **13 lines, not more** — Story 11.5 and 12.1 have essentially no margin in this unit.
   - `deferred-work.md`: zero removed lines anywhere in the cumulative diff since `HEAD`; append-only
     holds once CRLF checkout normalization is accounted for (`git diff` reports `LF will be replaced by
     CRLF`, which is a Windows checkout artifact, not a content edit). `DF-11-4-A` / `DF-11-4-B` both
     present. Minor: the dev's claimed `+8489` bytes for the 11.4-only section could not be exactly
     reproduced (a naive slice from the 11.4 heading to EOF measures `+8654` bytes); the append-only
     *property* is what is load-bearing here and it holds — the exact byte count is cosmetic
     documentation precision. **Low — informational, not actionable.**
   - Nothing pushed/tagged/dispatched: `git tag -l` empty; no new commits beyond the pre-existing
     unpushed six.
8. **Test ledger, re-derived via `--junitxml` (avoids a local terminal-summary quirk that suppressed the
   final pytest summary line in this environment):** `tests="1395" errors="0" failures="1" skipped="0"`
   → **1395 collected / 1394 passed / 1 failed**, sole failure
   `tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed`
   (`DF-11-1-A`) — matches exactly. `--deselect` on that node id → `tests="1394" failures="0" errors="0"`.
   No second red. `mypy argus` → clean, 72 files. `bandit -r argus` → 0 High / 0 Medium / 19 Low.
   `python -m argus.cli audit .` → `RELEASE_READY`, exit **0**, `assessed_deep_ratio=61/77`. `-114`'s
   narrowing is explicit (an asserted `_LOAD_FAILURE_CAUSES` set of exactly 4, non-vacuity asserted via
   `len(graded) >= 4`), not a deletion or a loosened equality. Confirmed unrelaxed.
9. **`tests/test_release_surface_honesty.py` — the third-consecutive-story write.** `git diff --cached`
   shows **zero removed lines**: 11.4's new CHANGELOG section is a pure insertion, placed second, and
   11.1's instrument disclosure is not demoted or reordered. This instance is legitimate
   guard-satisfaction — the registry's own stated ordering principle was applied, not bent, and no
   existing entry's text or position was altered. **Flagging the pattern anyway, as asked**: this file's
   note-section registry has now been edited by three consecutive stories in this epic (11.1, 11.2/11.3,
   11.4) to accommodate each story's own CHANGELOG entry. Each edit examined so far has been a clean,
   justified insertion — but a registry that is routinely widened to fit whatever the current story
   needs to say is a registry that is one "trust me, it's fine" story away from becoming decorative.
   Recommend the operator watch this at the epic checkpoint rather than treating each individual
   insertion's cleanliness as proof the pattern is safe long-term. **Low — process observation, not a
   defect in this story.**
10. **SOLID / DRY / KISS / YAGNI / coupling / testability.** The unsuffixed-token table
   (`TOKEN_BY_UNSUFFIXED_FAILURE`) replacing what would have been a third `if failure is …` special
   case is a genuine DRY improvement with the import-time closure (`_assert_prefixes_are_unambiguous`)
   generalized correctly to catch a future unregistered member. The AR8 pure/impure split is honored
   (`grammar_status.py` imports only `{__future__, enum, typing}`, confirmed by inspection and by `-119`
   passing). `_observe_canary`'s coupling to the live extraction tables is deliberate and load-bearing,
   not leaky — it is what makes the check non-vacuous, and it is documented as such. Tests throughout use
   `monkeypatch.context()`, real seams, and explicit non-vacuity assertions (both-direction controls) —
   exemplary test design for this house style. No SOLID/DRY/KISS/YAGNI violation found that rises above
   Low.

**Independently confirmed gates (all re-run by the reviewer, not read from the Dev Agent Record):**
`git ls-files -- argus`=72; six ` M`, no ` A`; dogfood units 1330/14987/4116 with all three partition ids
unchanged; `pytest tests/` via junit-xml = 1395/1394/1; deselect run = 1394/0; `mypy argus` clean/72;
`bandit` 0H/0M/19L; `python -m argus.cli audit .` → RELEASE_READY exit 0, 61/77; `pipeline.py` /
`verdict_gate.py` / `cache/key.py` byte-unchanged; `pyproject.toml` specifiers byte-unchanged; sixth
`GrammarFailure` member injected → `-115`/`-116`/`-118`/REPORT`-33` all RED, then reverted
byte-identically.

- [x] **[Review][Defer] Canary is a finite-sample check, not a universal grammar verifier** [argus/shared/grammar_status.py — `GrammarCanary`] — deferred, pre-existing design property, inherent to any canary-based validation and already disclosed in `DEV-1`'s own docstring; not actionable and not specific to this story.
- [x] **[Review][Defer] `tests/test_release_surface_honesty.py`'s note-section registry has been edited by three consecutive stories** [tests/test_release_surface_honesty.py:53-92] — deferred, pattern-level process observation for the epic checkpoint; this instance is a clean, justified insertion with zero lines removed or reordered, not a defect in Story 11.4.

---

## Dev Notes

### LOCKED decisions taken at story design — record these, do not re-litigate

| # | Decision | Reason |
|---|---|---|
| **DN-1** | **The check is BEHAVIOURAL first, metadata second.** A version comparison is a recorded second signal, never the mechanism. | §0.3. §A.2's false green occurs at an **in-bound** version, so a version pin is green on the exact tree where the defect is live. The epic's own premise for the version bound was measured false (§A.5). |
| **DN-2** | **The degradation is "no parser", routed into the existing floor row.** No new verdict, row, threshold or `verdict_gate.py` change. | §A.3 C/D **measured** that this lands on `INSUFFICIENT_COVERAGE` / exit 3 / `row_1_below_floor`, which is exactly `architecture.md:695-697`'s prescribed degradation and exactly the user story's *"withhold a verdict rather than compute one"*. Also the only shape reachable with `pipeline.py` byte-fenced. |
| **DN-3** | **Extend `GrammarFailure`; do not invent a second mechanism.** | AR7 / §3.3 forbid a parallel mechanism where one exists; the epic-10 retro assigned this shape to 11.4 by name; and it inherits the report-side plumbing, the classifier and the closure guards for free. |
| **DN-4** | **The pure/impure split follows the money AND the architecture.** Contract + canary corpus + bound → `grammar_status.py` (unit 3, ≥2000 free); probe + arm → `ast_index.py` (unit 2, 100 total). | §0.2's measured cliff makes this a correctness constraint, not a preference. It coincides with AR8's arrow, which is why it is safe. |
| **DN-5** | **No observed version string, exception message or host path is persisted.** The remedy names the supported range and the command to inspect. | NFR-S1 and 10.4's DN-5. A richer diagnostic is Story 12.8's surface. |
| **DN-6** | **`DF-10-4-E` is closed by this story.** | Its ledger entry defers it to *"whichever future story next extends `GrammarFailure`'s membership"*; this is that story; and leaving it open would make this story's own new cause render the **wrong** remedy — reintroducing 10.4's defect inside 10.4's fix. ~6 lines, budgeted. |
| **DN-7** | **`pyproject.toml`'s specifier is NOT widened or narrowed. Only its false comment is corrected.** | §A.5 disproves the pin's stated *reason*, not the pin. Packaging bounds have an owner (12.5 / operator, NFR-P3). Conservative-by-default is the right posture for an assurance tool, and the runtime defence is what this story adds in its place. |
| **DN-8** | **`DF-10-2-A` must not fire the canary.** Expectations are per-language and measured, including "parses, zero definitions" where that is today's truth. | §C.4. A uniform "≥1 definition" canary would downgrade every polyglot audit — turning a false-green fix into a mass false-`INSUFFICIENT_COVERAGE`, which is its own dishonesty. |
| **DN-9** | **`DF-11-1-A` stays deferred, carved out by node id.** | §0.4; fourth consecutive story to rule this way. |
| **DN-10** | **`…-114` is narrowed explicitly, never deleted or loosened.** | It is 10.4's DN-9 fence, and 11.4 is the story that fence names. The crossing is sanctioned; erasing the guard is not. |

### Architecture patterns & constraints a reviewer will check

- **AR8** — pure contract ← impure shell, one direction. `…-119` enforces it mechanically.
- **AR10 / `architecture.md:695-712`** — failure → named degraded outcome, never an uncaught raise;
  classify by arm position; no exception detail persisted; `BaseException` uncaught.
- **AR4 / NFR-D2 / NFR-P1** — deterministic, zero-token, no float, no clock, no iteration-order
  reliance; byte-identical across runs.
- **NFR-R1** — *"the run still produces a verdict (degraded → `INSUFFICIENT_COVERAGE`)"*. This is the
  story's target state, quoted verbatim from the architecture.
- **FR15/FR16** — the verdict is a pure fold over the ledger, and the four-row table is frozen. This
  story changes the **ledger's inputs**, never the fold.
- **FR7** — AST grounding is the thing being defended; `argus/shared/source_languages.py` is the
  source of truth for which languages exist. Do not hand-type the list.
- **Cross-cutting #6** — a heuristic-only finding can never move the verdict. §A.2 shows this moat is
  the *carrier* of the false green; do not weaken it, defend upstream of it.

### Testing standards — the house form

- One file per verification area, `TC-ArgusAgent-<AREA>-<NNN>-<NN>` in the test docstring and the
  function name. INDEX-001 is used to **119**; start at **120**.
- Every test docstring names the AC it satisfies and the driver it enforces.
- Simulate through `monkeypatch.context()` at the module seam; **never** mutate a shared registry
  outside a context manager; **never** install/uninstall a package.
- Both-direction controls and explicit non-vacuity assertions in every guard (§C.3).
- Stdlib only. No `packaging`, no `PyYAML`, no network, no `bash`, no `pytest.skip` as an answer.

### Previous story intelligence (10.4, 11.1, 11.2, 11.3)

- **10.4** built `grammar_status.py` and the four-arm loader, and **fenced the version comparison,
  the typed finding and the verdict change to this story by name** (its DN-9). Its `…-114` invariant
  is written to *detect this story crossing the fence* — see B.5/DN-10. Its `E.3` rule (simulate, do
  not uninstall) is the one you will lean on hardest.
- **11.1** established the FR34 disclosure and the git-stash isolation method for attributing a red.
- **11.2** shipped after its **central premise had silently expired**; its lesson is written into
  AC2.4 — pin *why* the defect was invisible, so the premise cannot expire unnoticed.
- **11.3** **failed review iteration 1** because its guard was blind to an ordinary shape of its own
  subject. Its lesson is E.6 and AC3.3: exercise every language, assert non-zero work.
- All three ruled `DF-11-1-A` deferred and carved it out by node id. So does this one.

### Runtime & toolchain, verified on this machine 2026-08-12

Windows · CPython **3.11.15** · `pytest` 9.1.1 · `mypy` clean on 72 files · `tree-sitter` **0.25.2**
with ten grammars across four minor lines (§A.4) · `packaging` 26.2 present **transitively only** —
not importable by contract · `tomllib` available at 3.11 but **not** at the declared floor of 3.10.

### Latest external technical facts (checked 2026-08-12)

`py-tree-sitter` 0.26.0's breaking changes are confined to `Language.version`→`abi_version`,
`Language.query()`→`Query(...)`, the two `timeout_micros` removals in favour of `progress_callback`,
and `Point` becoming a tuple subclass. `Language()`, `Parser()`, `Node.children`,
`Node.child_by_field_name`, `Node.has_error` and the minimum grammar ABI are **unchanged**. Sources:
the `py-tree-sitter` releases page and its 0.26.0 documentation, read 2026-08-12.

### Project structure notes

Write set is three existing `argus/` modules, two test files, four planning artifacts and the
CHANGELOG (§F). **No new `argus/**` module** (§0.2). Test ids continue INDEX-001 from 120. The story
file lives under `stories/` per `sprint-status.yaml`'s `story_location`.

### Open questions for the operator — saved for the end, as the workflow requires

1. **`DF-11-1-A` is now red across four consecutive stories.** Registering
   `epic-10-retro-2026-08-11.md` obliges the retro itself to carry a run id **plus its sha**, which
   does not exist. Options: (a) push and cite a real run, closing `AI-E10-1` too; (b) register the
   retro with an explicit `NOT ESTABLISHED` marker; (c) leave it red and accept that the count of
   permitted reds is now a standing carve-out rather than an exception.
2. **The `tree-sitter <0.26` pin's stated reason is measurably unverified (§A.5).** This story
   retains the pin and corrects the prose (DN-7). Does the operator want the pin **re-validated**
   against a real 0.26 install in a throwaway environment — which no story may currently do (§0.1.4)
   — or is conservative-by-default plus the new runtime defence sufficient for V1.5?
3. **`argusdemo/demo.sh`** remains untracked at the repo root and is explicitly out of scope for the
   fourth story running. Confirm at the epic checkpoint.
4. **`argus/pipeline.py` is 1331 lines against a 1200 cap** with no repo-wide gate until 12.1, and
   `DF-10-4-D`'s remedy is two epics away while Epic 12 adds modules by construction. This story
   survives both; 11.5 and 12.1 may not.

### References

- [epics.md §Epic 11 / Story 11.4](../epics.md) — the epic ACs, **first AC corrected by AC5.3**
- [epic-10-retro-2026-08-11.md §SD-2, §SD-3](../epic-10-retro-2026-08-11.md) — the stale-premise
  warning and the `DF-10-4-D` sequencing hazard
- [architecture.md §Packaging L560-583](../architecture.md) — the load-bearing-pin claim (AC5.1)
- [architecture.md §Error / Degradation L694-712](../architecture.md) — the prescribed degradation
- [E-PRD/prd.md FR7 L493](../E-PRD/prd.md) — AST grounding as the binding capability contract
- [deferred-work.md `DF-10-4-D`, `DF-10-4-E`, `DF-10-2-A`, `DF-11-1-A`, `DF-11-2-A/B`](../deferred-work.md)
- [stories/10-4-a-grammar-that-fails-to-load-names-why.md §D, DN-9](10-4-a-grammar-that-fails-to-load-names-why.md)
  — the fence that names this story
- [stories/11-3-published-action-cannot-execute-consumer-input.md §0.2, §0.4](11-3-published-action-cannot-execute-consumer-input.md)
  — the fence/red precedents carried forward
- `argus/index/ast_index.py::_get_parser_for_lang`, `argus/shared/grammar_status.py`,
  `argus/reports/generator.py::_render_grammar_remedy`, `argus/verdict/verdict_gate.py` (read-only),
  `tests/test_grammar_diagnosis.py::…-111/-114/-115/-119`

---

## Dev Agent Record

### Context Reference

This story file, read in full. No artifact was consulted that is not cited in §References.

### Agent Model Used

`claude-opus-5[1m]` (BMAD `dev-story`, mode `implement`, single pass, no fix iteration).

### Debug Log References

**All figures below are LOCAL — Windows, CPython 3.11.15 — under the dated risk acceptance
`AI-E10-1` (§0.1). CI evidence: `NOT ESTABLISHED`.** A human establishes it by pushing and running
`audit-ci.yml`, then citing the run id **plus the sha it covers**. ⛔ Nothing was pushed, tagged,
released or dispatched; ⛔ no `pip install`/`uninstall` was run and the venv is unchanged.

#### T0 — baseline re-derived by execution BEFORE any edit (2026-08-12)

| Gate | Measured | Matches story? |
|---|---|---|
| `git ls-files -- argus` | **72** | ✅ |
| `git status --porcelain -- argus/` | exactly four ` M` (`cli.py`, `detectors/vacuous_test.py`, `reports/generator.py`, `verdict/negative_assurance.py`), **no ` A`** | ✅ |
| `git rev-parse HEAD` | `93adc94d0203eaaf4d1cb1d8bc7113e9b885beed` | ✅ |
| `build_full_repo_plan('.')` | 72 files / 20034 LOC · **1330 / 14900 / 3804** · `477ef77d7b65…` / `82a3d605e61e…` / `ed6d08f25ce3…` | ✅ exact |
| `pytest tests/` | **1371 collected · 1370 passed · 1 failed** — `DF-11-1-A` | ✅ exact |
| `mypy argus` | Success: no issues found in **72** source files | ✅ |
| `python -m argus.cli audit .` | `RELEASE_READY deep_ratio=61/167 blocking_findings=0 **assessed_deep_ratio=61/77**`, exit **0** | ✅ |

Every §0/§A premise the story asserts was reproduced. **No transcription.**

#### T1 — 🔑 THE FALSE GREEN, REPRODUCED RED-FIRST AGAINST THE UNMODIFIED TREE (AC2.2 / E.1)

Captured **before a single line of `argus/` was edited.** Method: stage the real `vacuous_basic`
cartridge, add four clean production modules so the repository sits **above** the 60% deep gate,
`git commit`, audit; then rename `argus.index.ast_index._CALL_NODE_TYPES` **in memory only** and
audit the **identical commit** again. The module attribute was restored and asserted `is` the
original object; no file on disk outside the temp repo was touched, and no package was changed.

```
IN-BOUND  grammar : NOT_READY_FOR_RELEASE exit=2 deep=5/6 blocking=1
                    [('vacuous_test_ast', ELIGIBLE=True), ('orphan_code', False) x5]
DRIFTED   grammar : RELEASE_READY          exit=0 deep=5/6 blocking=0
                    [('orphan_code', False) x10, ('vacuous_test_heuristic', False)]

deep_ratio identical in BOTH runs: True (5/6 vs 5/6)
```

**This reproduces §A.2 exactly**, including the part that makes it undetectable: the verdict
inverted, exit 2 → exit 0, the planted defect stayed put, `vacuous_test_ast` (verdict-**eligible**)
silently became `vacuous_test_heuristic` (advisory-only), and **`deep_ratio` did not move**. The
drift occurred at an **in-bound `tree-sitter 0.25.2`** — which is the whole argument against
shipping a version assertion.

⛔ The transcript is **not** the only evidence, on purpose. `…-125` reconstructs the pre-fix loader
in memory (`_disable_the_fix`) and re-asserts the false green **on every run**, so the demonstration
cannot rot into a quoted paragraph (`AI-E3-1`).

#### T2 — the ELEVEN canary expectations, MEASURED before being pinned (AC3.1 / §C.4)

Every row produced by running the candidate snippet through the **real** `_get_parser_for_lang` +
`_extract` on this host. **Nothing assumed.** (Eleven rows, not ten: the corpus is keyed by
`(language, entry point)` — the same pair the loader caches on — so both TypeScript dialects are
validated separately, which is the `.tsx` blind spot Story 10.2 paid for.)

| language | entry point | `has_error` | vocabulary (∩ Argus's extraction tables) | definitions | edges |
|---|---|---|---|---|---|
| c | `language` | False | `call_expression`, `function_definition` | **()** 🚩 | `argus_probe` |
| cpp | `language` | False | `call_expression`, `function_definition` | **()** 🚩 | `argus_probe` |
| go | `language` | False | `call_expression`, `function_declaration` | `argus_probe`, `argus_canary` | `argus_probe` |
| java | `language` | False | `class_declaration`, `method_declaration`, `method_invocation` | `ArgusCanary`(class), `argus_probe`, `argus_canary` | `argus_probe` |
| javascript | `language` | False | `call_expression`, `function_declaration` | `argus_canary` | `argus_probe` |
| php | `language_php` | False | `function_call_expression`, `function_definition` | `argus_probe`, `argus_canary` | **()** |
| python | `language` | False | `call`, `function_definition` | `argus_canary` | `argus_probe` |
| ruby | `language` | False | `call` | **()** 🚩 | **()** |
| rust | `language` | False | `call_expression` | **()** 🚩 | `argus_probe` |
| typescript | `language_typescript` | False | `call_expression`, `function_declaration` | `argus_canary` | `argus_probe` |
| typescript | `language_tsx` | False | `call_expression`, `function_declaration` | `argus_canary` | `argus_probe` |

🚩 **`DF-10-2-A` reproduced exactly as §C.4 warned** — `c`, `cpp`, `ruby`, `rust` extract **zero
definitions** while parsing cleanly. A uniform "≥1 definition" canary would have fired on four
**healthy** grammars. Their expectations pin today's honest truth, and `…-123` asserts all four
pass **by name**, so a future `DF-10-2-A` fix goes red rather than being silently absorbed.

**🔑 The measurement that decided the design.** Ruby's `_extract` output is `((), ())` — an
expectation a **totally broken** Ruby grammar also satisfies. That is a vacuous canary (§C.3), so
the observable had to be widened: `vocabulary` is the **live intersection of the parsed tree's node
types with `_DEF_KIND_BY_NODE ∪ _CALL_NODE_TYPES`**, which is **non-empty for all eleven seams**,
including Ruby's (`call`), and is *precisely* the surface §A.2's drift destroys.

#### Negative controls, both measured (E.3)

| Control | Result |
|---|---|
| Go canary parsed by the **Python** grammar (a substituted/vendored grammar) | `has_error=True`, vocabulary `('call',)` ≠ `('call_expression','function_declaration')` → **FIRES** ✅ |
| §A.2's `_CALL_NODE_TYPES` drift, python / ruby / rust | vocabulary `('function_definition',)` / `()` / `()` → **FIRES** on all three ✅ |
| The real in-bound toolchain, all **eleven** seams | `parser=True failure=None` → **does not fire** ✅ |

#### T3–T5 — the RED-first sequence on the closure guards

Adding the fifth `GrammarFailure` member with no arm turned exactly the designed guards red, which
is them working:

```
FAILED …::test_loader_has_no_unnamed_swallowed_or_redundant_arm        (-115: registered, unreached)
FAILED …::test_registry_and_behavioural_matrix_close_over_each_other   (-116: registered, undriven)
FAILED …::test_this_guard_cannot_pass_vacuously                        (-118: count 4 → 5)
```

All three green after the arm, the `_MODES` entry and the deliberate count update.

#### T8 — gate run, AFTER staging (compare against T0)

| Gate | Baseline (T0) | After | Verdict |
|---|---|---|---|
| `git ls-files -- argus` | 72 | **72** | ✅ **fence holds** |
| `git status --porcelain -- argus/` | four ` M`, no ` A` | **six ` M`, no ` A`** (my 2 join 11.1/11.2's 4; `generator.py` was already one of the four) | ✅ **no new `argus/**` file** |
| unit 1 | `477ef77d7b65…` / 1330 | **`477ef77d7b65…` / 1330** | ✅ byte-unchanged |
| unit 2 | `82a3d605e61e…` / 14900 | **`82a3d605e61e…` / 14987** | ✅ id unchanged, **+87 of the 100** budget, ≤ 15000 |
| unit 3 | `ed6d08f25ce3…` / 3804 | **`ed6d08f25ce3…` / 4116** | ✅ id unchanged (+312, of ≥2000 free) |
| `pytest tests/` | 1371 / 1370 / 1 | **1395 collected · 1394 passed · 1 failed** | ✅ +24 tests, all green |
| the one failure | `DF-11-1-A` | **`DF-11-1-A`, and nothing else** | ✅ see below |
| `mypy argus` | clean, 72 files | **clean, 72 files** | ✅ no new `# type: ignore` beyond the existing duck-typed-node idiom |
| `bandit -r argus` | 0 High / 0 Med / 19 Low | **0 High / 0 Medium / 19 Low** | ✅ unmoved |
| `argus audit .` | `RELEASE_READY`, exit 0, **61/77** | **`RELEASE_READY`, exit 0, `assessed_deep_ratio=61/77`** | ✅ **AC6.5 holds** |

**AC6.3, asserted rather than eyeballed** — the carve-out run:

```
pytest tests/ --deselect "tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed"
  → 1394 passed, 1 deselected
```

**Zero failures with `DF-11-1-A` deselected by node id.** It is the only red, it is not mine
(§0.4 / DN-9), and it was neither closed, staged nor deleted.

`deep_ratio` moved 61/167 → 61/168 and `held_out` 90 → 91 purely because the **new test file** is
enumerated and held out. `assessed_deep_ratio` — the figure AC6.5 pins — is **unchanged at 61/77**.

**AC6.7, verified with `git diff --stat`, not asserted:**
`git diff --stat -- argus/pipeline.py argus/verdict/verdict_gate.py` → **empty output. Both
byte-unchanged.** No new dependency (`grammar_status.py`'s imports remain `{__future__, enum,
typing}` — `…-119` passes unrelaxed); no cache-key or schema-version change.

### Completion Notes List

**AC1.4 — THE TOKEN SPELLING, LOCKED BEFORE THE TESTS WERE WRITTEN.** Member
`GrammarFailure.RUNTIME_UNVALIDATED` (value `"runtime_unvalidated"`), reason token
**`tree_sitter_runtime_unvalidated`** — **no `<lang>` suffix**, for the same reason
`CORE_RUNTIME_TOKEN` carries none and a sharper one: the parser *constructed*, so there is nothing
per-language to reinstall. Accepted by the module's import-time prefix-ambiguity assertion, which
this story **generalised** (see DEV-2).

**DN-1 honoured — no version assertion was shipped.** The mechanism is the behavioural canary; the
declared range is a second, independent signal. `…-125` proves the behavioural check fires **on its
own at an in-bound version**; `…-127` proves the bound fires **on its own with a healthy grammar**.
Neither alone would have closed the class, which is exactly why the epic's AC was corrected (AC5.3)
rather than implemented.

**DN-2 honoured — the degradation is "no parser", routed into the existing floor row.**
`verdict_gate.py` and `pipeline.py` are byte-unchanged; no new verdict, row, threshold or exit-code
mapping. `…-114` now asserts, in the same run, that the fifth cause's graded shape is *identical* to
the four load causes — that sameness is the load-bearing claim, and it is what proves nothing
downstream started branching on the token.

#### Design decisions taken under my authority, with their tradeoffs

- **DEV-1 — the observable is the extraction-vocabulary intersection, not just the extracted
  output.** Forced by measurement, not preference: Ruby's honest expectation is `((), ())`, which a
  broken grammar satisfies (§C.3 vacuity). The intersection is non-empty for all eleven seams and is
  the exact surface §A.2's drift destroys. **Tradeoff:** it is sensitive to a deliberate change of
  `_DEF_KIND_BY_NODE` / `_CALL_NODE_TYPES` — i.e. a future `DF-10-2-A` fix will turn `…-120` red.
  **That is intended**, it is stated in the corpus docstring and in the ledger, and the alternative
  (a canary blind to a vocabulary change) is the defect this story exists to close.
- **DEV-2 — the unsuffixed tokens became a TABLE, replacing two `if failure is …` special cases.**
  With two runtime-scoped causes, a third would have been a third special case in three functions —
  the duplicated-parse shape `grammar_status.py` exists to remove. The import-time assertion was
  generalised with it, and now also fails when **any** registered member owns no token spelling.
  **Tradeoff:** ~20 lines in the pure module, which is unit 3 — free under the measured cliff.
- **DEV-3 — the probe FAILS CLOSED on an unpinned seam.** `canary_for` returning `None` yields
  `RUNTIME_UNVALIDATED`. Fail-open would let an eleventh language escape the check entirely — the
  "guard green by finding nothing" failure. **Tradeoff:** adding a language without a canary would
  downgrade every audit of it, so `…-124` closes the corpus over `LANGUAGE_BY_SUFFIX` in **both**
  directions and goes red **at edit time**, before it can grey an audit.
- **DEV-4 — `_package_version` was refactored to `_distribution_version`.** The core distribution's
  version was needed and the old helper only formed `tree-sitter-<lang>`. DRY, and it gave the tests
  one seam to simulate the version at. Net **+2** physical lines; existing behaviour identical.
- **DEV-5 — placement inside `_get_parser_for_lang`.** ARM 5 sits **after** ARM 3 because the canary
  needs a constructed parser. ARM 3's `return` became an assignment plus a single success `return`,
  which keeps `…-115`'s "exactly one success exit" invariant intact (6 exits for 5 causes + 1
  success).
- **DEV-6 — prose moved to unit 3 under budget pressure (AC6.2, and a conflict resolved).** The
  first draft of `ast_index.py` cost **+85** lines, leaving too little for the report branch. Rather
  than delete rationale, the *why* was moved beside the contract in `grammar_status.py` (unit 3,
  free) with pointers left in the shell — the story's own design rule. Final: **+68** ast_index,
  **+19** generator = **+87 of 100**. **This is where a project standard beat a general principle**:
  ordinary style would keep an explanation next to its code, but §0.2's measured LOC cliff makes
  placement a *correctness* constraint here. Recorded rather than silently traded.

#### `DF-10-4-E` closed (AC4.3 / DN-6)

`_render_grammar_remedy`'s trailing unconditional fallthrough is now an explicit
`if failure is GrammarFailure.CORE_RUNTIME_MISSING` arm ending in a `raise ValueError` that names
the unregistered member. Without this, **this story's own fifth cause would have rendered the
core-runtime remedy** — "run `pip install tree-sitter`" when the core is installed and fine —
reintroducing 10.4's defect inside 10.4's fix. `…-33` drives **all five** causes and asserts five
**distinct** remedies plus a negative control proving an unregistered member raises. Ledger marked
closed with the date and this story id.

#### Fences, re-verified

⛔ **Not touched:** `pyproject.toml`'s specifiers (only the false **comment** was corrected — AC5.2 /
DN-7), `verdict_gate.py`, `pipeline.py`, the R3 cache key / `CACHE_KEY_SCHEMA_VERSION` /
`GrammarProvenance`, `DF-10-2-A`, `DF-11-2-A/-B`, `DF-11-1-A`, `argusdemo/`, `README.md`,
`action.yml`, `.github/workflows/**`, `E-PRD/*`. ⛔ No push, tag, release, dispatch or `pip` command.
⛔ No committed dogfood artifact was regenerated.

**One write outside §F, declared: `tests/test_release_surface_honesty.py`.** The CHANGELOG entry
(in §F) turned `TC-ArgusAgent-DOCS-001-16` red — the note-section registry demanding that a new
consumer-facing claim be registered **deliberately**. That red was **mine**, and registering is the
guard working as designed, not scope leak: it is the mandated consequence of an in-scope change.
The section is registered **second**, on the registry's own stated principle (*what breaks a
pipeline soonest*): it is the only entry that can change an **exit code** on an unchanged
repository, for every language and channel. 11.1's instrument disclosure was **not** demoted, and no
existing section moved relative to any other — the insertion was performed as a byte-identical block
move, verified `sha256 d0233fe9aa02a5bf → d0233fe9aa02a5bf` with the file length unchanged.

#### Open questions for the operator (carried forward from §Dev Notes, plus one)

1. **`DF-11-1-A` is red across FIVE consecutive stories now.** It should be adjudicated at the Epic
   11 checkpoint rather than carried a sixth time. Options unchanged: (a) push and cite a real run;
   (b) register the retro with an explicit `NOT ESTABLISHED` marker; (c) accept it as a standing
   carve-out and say so in the ledger.
2. **The `tree-sitter <0.26` pin is retained but its stated reason is disproved** — filed as
   **`DF-11-4-B`**. Does the operator want it re-validated against a real 0.26 install in a
   throwaway environment (which no story may currently do, §0.1.4), or is conservative-by-default
   plus this story's runtime defence sufficient for V1.5?
3. **`argusdemo/demo.sh`** — untracked, out of scope for the fifth story running. Confirm at the
   checkpoint.
4. **`argus/pipeline.py` is 1331 lines against a 1200 cap** and unit 2 is now **14987 / 15000**.
   This story survived the cliff with **13** lines to spare. **Story 11.5 and Story 12.1 will not.**
   The `DF-10-4-D` remedy is two epics away while Epic 12 adds modules by construction — this is the
   most likely thing to halt the next story, and it is now measured to the line.
5. **New: `DF-11-4-A`** — the operator callout for the new cause is invisible on a *partial* failure,
   because `_render_readability_warning`'s all-or-nothing trigger belongs to Story 12.5
   (`DF-10-4-A`'s trigger, unchanged here). Severity raised to 🟡 in the ledger with the reason.

### File List

**Modified — `argus/` (3, all pre-existing; no file created — `DF-10-4-D` fence holds at 72):**
- `argus/shared/grammar_status.py` — fifth `GrammarFailure` member + token, the unsuffixed-token
  table and generalised import-time closure, the declared version range as integer tuples, the pure
  version parse/compare, the eleven-row canary corpus, `canary_for` / `canary_matches` (unit 3, +312)
- `argus/index/ast_index.py` — `_distribution_version`, `_observe_canary`, `_toolchain_is_validated`,
  ARM 5 in `_get_parser_for_lang` (unit 2, **+68**)
- `argus/reports/generator.py` — the fifth remedy branch + `DF-10-4-E`'s exhaustiveness arm and
  `raise` (unit 2, **+19**)

**Modified / added — tests:**
- `tests/test_grammar_runtime_validation.py` — **NEW.** `TC-ArgusAgent-INDEX-001-120`..`-127`,
  `TC-ArgusAgent-REPORT-002-33`..`-34`, `TC-ArgusAgent-DOCS-001-54`..`-55` (24 test cases)
- `tests/test_grammar_diagnosis.py` — the fifth simulated mode, `-114` narrowed explicitly with its
  reason and a separate fifth-cause assertion, `-118`'s counts updated deliberately
- `tests/test_release_surface_honesty.py` — the new note section registered (declared above)

**Modified — planning / packaging artifacts:**
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md` — §Packaging claim **struck and
  corrected** (AC5.1); §Enforcement gains the toolchain-validation registration
- `pyproject.toml` — the dependency **comment** corrected (AC5.2). ⛔ Specifier byte-unchanged
- `_bmad-output/design-artifacts/ArgusAgent/epics.md` — Story 11.4's first AC struck and corrected
  in place, dated, with the reason (AC5.3)
- `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` — **APPEND-ONLY** (AC5.4): `DF-10-4-E`
  closed; `DF-10-2-A` / `DF-11-1-A` / `DF-11-2-A` / `-B` re-affirmed open; `DF-11-4-A` / `DF-11-4-B`
  filed with owners and target stories. Verified `after.startswith(before)` → **True** (+8489 bytes)
- `CHANGELOG.md` — one entry under `## Unreleased`
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` — `11-4-…` → `review`
- THIS story file — Dev Agent Record, tasks, status; `git add`-ed with the delta (E.5)

## Change Log

| Date | Change |
|---|---|
| 2026-08-12 | Story created (create-story). All §0–§F figures measured by execution on this tree. Epic premise re-measured and found **false as written** (§0.3); false-green path **demonstrated** (§A.2); LOC cliff measured to the line (§0.2); `DF-10-4-E` ruled **in** scope, `DF-11-2-A/-B`, `DF-11-1-A`, `DF-10-2-A` and `argusdemo/` ruled **out**. |
| 2026-08-12 | **Implemented (dev-story).** False green reproduced **RED-first against the unmodified tree** (exit 2 → exit 0, `deep_ratio` 5/6 both runs) and kept permanently reproducible by `…-125`. Eleven canary expectations **measured before pinning**; `DF-10-2-A`'s four zero-definition languages accommodated by name. Fifth cause `RUNTIME_UNVALIDATED` + token `tree_sitter_runtime_unvalidated` registered; ARM 5 added at the real loader seam; degradation routed through the **existing** floor row. `DF-10-4-E` **closed**. `architecture.md`, `pyproject.toml`'s comment and `epics.md`'s AC corrected (struck, not deleted); ledger appended (append-only verified programmatically). **Gates:** 1395 / 1394 / 1 (the one red is `DF-11-1-A`, carved out by node id and proven the only failure); `mypy` clean on 72; `bandit` 0 High / 0 Medium / 19 Low; `argus audit .` `RELEASE_READY` exit 0 at `assessed_deep_ratio` **61/77**; `git ls-files -- argus` **72**; all three `partition_id`s **byte-unchanged**; unit 2 **14987 ≤ 15000** (**+87 of 100**); `pipeline.py` and `verdict_gate.py` **byte-unchanged**. All **LOCAL**; CI **NOT ESTABLISHED**; nothing published. |
