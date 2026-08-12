---
baseline_commit: 93adc94d0203eaaf4d1cb1d8bc7113e9b885beed
baseline_note: >-
  HEAD is `93adc94` on `master`, **6 commits unpushed**, `git tag -l` **empty**. Epic 10 is
  5/5 `done` and its retrospective (`epic-10-retro-2026-08-11.md`) is signed. **No CI run has
  ever seen a line of Epic 10** — the last executed `audit-ci.yml` run (`31341363300`) is
  sha-scoped to `00c8d1b`, which contains none of it. Every baseline figure in this story is
  **LOCAL, Windows / CPython 3.11.15**, on a host whose divergence from the ubuntu CI matrix is
  documented. See §0 — the operator has recorded a **dated risk acceptance** for this.
  ⚠️ **The tree is NOT clean.** `tests/test_v1_commitment_closure.py` is **staged and
  uncommitted** (Story 10.5's guard), the 10.5 story file is `AM`, and `_bmad/**` config churn is
  ` M` (AI-E10-9). `git status --porcelain -- argus/` **IS empty** — that is the one that matters
  for your fences. Do not commit, revert or restage anything you did not author.
  ⚠️ **`bmad-dev-loop-pack/`, `.bmad-drift-audit/` and `_bmad-output/audit-reports/*` belong to
  the orchestrator/host — do not add, move or delete them.** THIS FILE is untracked and IS
  yours: `git add` it with your delta or you repeat AI-E8-1.
  **Every figure, coordinate and count below was measured on THIS tree on 2026-08-11.** Locate
  every site by its **anchor text**; treat every line number here as a hint you must re-verify
  (this project has produced five stale coordinates in four days).
story_key: 11-1-tool-discloses-its-status-with-an-expiry
epic: 11
---

# Story 11.1: The tool discloses its own status, and the disclosure has an expiry

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **ArgusAgent story — Argus repo, `argus/` tree only.** ArgusAgent (formerly APAA) is a
> self-contained headless audit tool extracted from the Minions monorepo into its own repository
> (`Agent-Argus`, distribution `argus-agent`, package `argus/`). **RS-1 is binding: all work lands in
> THIS repo. The `minions_core/apaa/` copy in the Minions repo is legacy — no modification, no
> back-port.** Planning artifacts live under `_bmad-output/design-artifacts/ArgusAgent/`; the tracker
> is that folder's `sprint-status.yaml`. Prose in older documents saying `design-artifacts/APAA/`,
> `minions_core/apaa/` or `tests/apaa/` should be read as `design-artifacts/ArgusAgent/`, `argus/`
> and `tests/`.

---

## Story

As an independent developer installing Argus,
I want the tool to tell me the validation state of its own findings wherever it gives me a verdict,
so that I can weigh its output correctly — and so that its status cannot quietly become permanent.

**Why this is Epic 11's first story, and why it is one story.** Epic 11's charter is *"nothing
unsafe or untrue can be published."* Every other story in the epic closes a specific defect that
gets worse on publication — a misclassified file (11.2), a shell injection (11.3), a false green
(11.4), a broken wheel and a false README (11.5). **This one closes the defect that is true of
every verdict the tool has ever emitted**: Argus states a release-readiness verdict without stating
that its own finding-precision has never been independently measured. The epic's dependency flow
puts it first for a reason the PRD spells out — *"no verdict surface ships without disclosure."*

**Its deliverable is narrow: one disclosure, one mechanism, an enumerated surface set, and an
expiry.** It ships **no new capability**, changes **no verdict**, and touches **no threshold**. If
you find yourself reasoning about whether a verdict is right, you have left the story.

⚠️ **Read §0 before anything else.** Three Epic-10 retrospective action items gate this story, and
one of them (the `DF-10-4-D` constraint) constrains your *design*, not merely your process.

---

## Story Context

### Method statement — everything in §0–§F was MEASURED on this tree on 2026-08-11

Every count, coordinate, ratio and partition id below was produced by executing `git`, `grep`,
`wc`, `mypy`, `pytest --collect-only`, or by importing and running `argus.dogfood.partition_plan.
build_full_repo_plan('.')` in this working tree. **Three figures are NOT re-measured here and are
attributed rather than restated**: coverage 95.51%, `bandit` 0 High / 0 Medium (19 Low), and
`argus audit .` → `RELEASE_READY / blocking_findings=0`. Those are Story 10.5's dev-and-reviewer
runs at `93adc94`. **Re-derive everything; transcribe nothing.**

---

### §0. The three Epic-10 gates on this story — read these first

Epic 10's retrospective named three items as **critical, before Epic 11 story 1 is contexted**
(`epic-10-retro-2026-08-11.md` §7, §8). All three are discharged here, and two of them bind you.

#### 0.1 — 🔴 DATED RISK ACCEPTANCE, 2026-08-11 (AI-E10-1)

**Recorded by: XAgent007 (operator), 2026-08-11. Accepted by: XAgent007.**

> **No CI run covers any Epic 10 sha.** Re-measured this session: `HEAD` = `93adc94`, **6 commits
> ahead of `origin/master`**, `git tag -l` **empty**. The last executed `audit-ci.yml` run
> (`31341363300`) is sha-scoped to `00c8d1b`, which contains **none** of Epic 10. Every gate figure
> this story cites as a baseline — 1336 tests, `mypy` clean on 72 files, 95.51% coverage,
> `RELEASE_READY` — is a **LOCAL run on a Windows host at CPython 3.11.15**. CI is ubuntu ×
> 3.10/3.11/3.12, and this project has direct measured evidence that the difference matters: **six
> of the twelve commits in `cd60dbb..00c8d1b` were host-portability defects invisible on exactly
> this machine and fatal on the runner.**
>
> **The operator has ruled: Epic 11 proceeds WITHOUT a CI run, and this is the dated record of who
> accepted the risk.** The consequence, stated plainly rather than hedged: **this story's baseline
> figures are local-only and unverified by any executed gate.** A portability defect in Epic 10's
> `argus/**` changes would be discovered at the end of Epic 11 rather than the start.

**What this obliges you to do (and it is not optional):** apply Story 10.1's evidence-citation rule
(`architecture.md` §H + §Enforcement, enforced by `tests/test_evidence_citation.py`) to **your own**
gate run. Label every figure you record **LOCAL**, and either cite an `audit-ci.yml` run id **plus
the sha it covers** for your own HEAD, or record the status **`NOT ESTABLISHED`** and name the
command a human runs. ⛔ **Do not push, tag or `workflow_dispatch` to manufacture a citation**
(10.1's DN-7). *A local run is necessary and not sufficient* is this project's own rule, written by
the epic you are building on.

#### 0.2 — ⛔ THE `DF-10-4-D` CONSTRAINT (AI-E10-2) — this constrains your DESIGN

**Operator ruling for the whole of Epic 11: NO Epic 11 story may create or stage a new
`argus/**` source file.**

The mechanism, measured (`deferred-work.md` `DF-10-4-D`):
`argus/dogfood/partition_plan.py::enumerate_minions_source_files` enumerates via
**`git ls-files argus`**, and `git ls-files` reports the **INDEX**, not `HEAD`. So the
dogfood-audited population moves the instant a new `argus/**` module is **staged** — before any
commit, and at the exact moment `AI-E8-1` *requires* the `git add`. In Story 10.4 that turned
**five** committed-artifact staleness tests red mid-implementation and **halted the story**. Its
remedy is targeted at **Story 12.1 — after Epic 11**.

**Confirmed feasible: this story's scope can be delivered under that constraint, and §C.1 shows
how.** Every line of it lands in files that already exist. The design consequence is recorded as
**DN-2** and it is not negotiable.

**⚠️ There is a SECOND trigger the operator ruling does not name, and this story walks straight
into it. §A.5 measures it: you have a budget of 207 physical lines.** Read §A.5 before you write
code.

#### 0.3 — 🔴 RE-MEASURED PREMISES (AI-E10-3)

Story 11.1's ACs were drafted on **2026-08-10b**, before Stories 10.2/10.3/10.4 changed `argus/**`.
The re-measurement is §A. **Two of this story's own premises diverged and one held.** Each
divergence changes an AC; none changes the story's purpose.

| Premise as the epic writes it | Measured on this tree, 2026-08-11 | Verdict |
|---|---|---|
| *"`demo-heuristic-only` … exist **only** in `argus/dogfood/proof_run.py` and `proof_render.py`"* | **The tree AGREED** for `demo-heuristic-only`: 8 occurrences, 5 + 3, in exactly those two modules and nowhere else in `argus/**`. | ✅ **holds** |
| *"…and the `provisional` gate string"* — same two modules | **The tree DIVERGED.** `provisional` appears in **five** `argus/**` modules: `precision/replay_harness.py` (**24**), `dogfood/proof_run.py` (8), `dogfood/proof_render.py` (4), `precision/__init__.py` (2), `dogfood/proof_types.py` (1). `argus/precision/` is the **origin** — `precision_gate_status_for` and `PrecisionResult.provisional` live there and dogfood *consumes* them. | ❌ **stale** → §A.1, and it changes AC2 (there is already a producer; do not build a second one) |
| *"the disclosure reaches … the **MCP surface**"* | **The tree DIVERGED.** `grep -rni "mcp"` over `argus/`, `pyproject.toml` and `action.yml` returns **zero**. The MCP surface **does not exist** and is built by **Story 12.6**, whose sprint-status entry already says *"Carries the FR34 disclosure."* | ❌ **stale** → §A.2, and it changes AC4 (11.1 must make 12.6 *unable* to ship without it, not build it) |

---

### §A. What was measured, and what it changes

#### A.1 — 🚩 The disclosure has a PRODUCER already, and it is unsafe to import

`argus/precision/replay_harness.py` computes the instrument's own gate state today:

- `compute_precision(..., protocol_cleared: bool = False, ...)` — **`replay_harness.py:223`**.
- `PrecisionResult.provisional` is `True` unless the corpus reached the `N ≥ 5` floor **and**
  `protocol_cleared=True` was passed (`:320-322`).
- **Measured: no call site anywhere passes `protocol_cleared=True`.** The only two occurrences are
  in tests that exist to prove the flip path is reachable (`tests/test_dogfood_plan.py:406,410`).
  Story 13.3 is the story that will pass it `True`.

**Why this matters twice.** (a) **AR7 / §3.3 forbid a second mechanism where one exists** — the
instrument's status must not become a hand-maintained boolean that can disagree with the harness.
(b) **You must NOT import it on any user-facing path.** `replay_harness.py:86-97` performs a
`sys.path.insert` of `<repo>/tests/cartridges` and then `from _registry import …` at **module
level**. That is precisely the defect **Story 11.5** exists to fix (*"5 of 71 wheel modules fail to
import — `No module named '_registry'`"*). Importing it from `cli.py` or `reports/` would put the
broken import on every install's critical path and convert a latent packaging defect into a
crash-on-start.

**The resolution is DN-3, and it is the interesting design decision in this story:** the constant is
declared **without importing the harness**, and a **committed guard imports the harness (tests may;
tests already do) and asserts the two agree.** No second mechanism, no unsafe runtime import, and
the disagreement is caught by CI rather than by a user.

#### A.2 — 🚩 The MCP surface does not exist. Do not build it; make it unable to escape

`grep -rni "mcp\|model.context.protocol"` over `argus/`, `pyproject.toml` and `action.yml` →
**0 hits**. FR35 / Story 12.6 delivers it. The epic AC names it because FR34's binding half is
*"the surface set is enumerated in a committed test that fails on an unenumerated member — a new
verdict surface must either carry the disclosure or fail CI."*

**So the AC is satisfied by the closure, not by the surface.** 11.1's guard must be written so that
when 12.6 adds an MCP entry point, the guard goes **RED** until that surface is registered *and*
carries the disclosure. That is AC4, and it is the load-bearing AC of this story.

⚠️ **Do not add an `mcp` stub, an entry point, an extra or a flag.** `tests/test_invocation_contract.py`
derives the accepted surface from the live `argparse` parser in both directions; an unspecified flag
fails it. FR35 is 12.6's.

#### A.3 — The surface inventory, measured

| # | Surface | Where it is emitted, measured | Exists today? |
|---|---|---|---|
| 1 | **CLI — machine line** | `argus/cli.py::_summary_line` → **stdout**, `verdict=… deep_ratio=… blocking_findings=…` | ✅ |
| 2 | **CLI — human register** | `argus/cli.py::_emit_ship_readiness` → **stderr**; `tests/test_cli.py:112` pins `captured.err.startswith("Ship-readiness: …")` | ✅ |
| 3 | **CLI — suppression disclosure** | `argus/cli.py::_emit_suppression_disclosure` → **stderr**, printed on **every** run including when the count is zero (Story 10.3 / AC4.3). **This is your precedent, in register, placement and unconditionality.** | ✅ |
| 4–7 | **Generated reports** | `argus/reports/generator.py::generate_reports` writes **exactly four** files: `final-verdict.md`, `coverage-ledger.md`, `security-review.md`, `architecture-review.md`. It is the **single write point** — every `dest.write_text(...)` for a report is in that one function. | ✅ |
| 8 | **Distribution listing — index summary** | `pyproject.toml [project].description` (the PyPI one-liner) | ✅ |
| 9 | **Distribution listing — long description** | `README.md` (`readme = "README.md"` → this *is* the PyPI page body) | ✅ |
| 10 | **Distribution listing — marketplace summary** | `action.yml` top-level `description:` (the GitHub Marketplace listing) | ✅ |
| 11 | **Release note** | `CHANGELOG.md` — already carries `### No assurance claim is made by this release` | ✅ |
| — | **MCP surface** | *(none)* | ❌ **12.6** |
| — | **Persisted verdict artifact** | `NegativeAssuranceVerdict` under `.argus/` | ✅, but **FENCED** — see §D |

**`coverage-ledger.md` is rendered by `argus/ledger/coverage_report.py::render_text`, not by
`generator.py`.** Do **not** make `argus/ledger/**` import `argus/reports/**` or
`argus/verdict/negative_assurance.py` to reach the constant — that inverts the layering
(`generator.py:14` already imports *from* `coverage_report`). §C.2 gives the injection point that
avoids it entirely.

#### A.4 — The guard inventory: what "extend, never duplicate" actually names

The epic AC says the *"two-sided `DOGFOOD_EXTERNALIZATION_GUARD` test is **extended** (presence AND
over-claim-phrase absence), never duplicated."* Measured, that mechanism is spread across three
files, and **"two-sided" means presence + absence, not two files**:

| Guard | Id(s) | Side |
|---|---|---|
| `tests/test_dogfood_module_split.py` | `TC-ArgusAgent-DOGFOOD-001-48` | **both** — pins the guard sentence byte-for-byte **and** scans it for over-claim phrases |
| `tests/test_dogfood_proof.py` | `-25` / `-26` | presence in the artifact / RED-first over-claim absence |
| `tests/test_release_surface_honesty.py` | `-16`, `-17`, `-17b`, `-18`, `-19` | registry + **sentence-scoped** over-claim detector + **closed set** + honesty-language presence |

**`test_release_surface_honesty.py` is the one you extend**, and the reusable part is
`_OVER_CLAIMS`, `_DENIAL_MARKERS`, `_QUALIFIER_MARKERS`, `_split_sentences`, `_is_denied` and
`_affirmative_over_claims` — a *position-aware*, sentence-scoped detector that already survived a
code-review escape (a trailing negation, `-17b`). **Import it. Do not re-author it.** That is what
"never duplicated" means here, and re-authoring a blunt substring scan would reopen the exact hole
`-17b` closed.

Two registries in that file will bite you if you miss them:

- **`_NOTE_SECTIONS` is ORDER-PINNED** (`-16` asserts `present == list(_NOTE_SECTIONS)`). A new
  `CHANGELOG.md` `### ` section that is not registered **in the right position** fails.
- **`_RELEASE_SURFACES` does not contain `pyproject.toml`** (7 entries, measured at
  `tests/test_release_surface_honesty.py:88-96`). If you put the disclosure in the PyPI summary,
  register it in **both** `_RELEASE_SURFACES` and `_RELEASE_SURFACE_PATTERNS`, or `-18`'s
  closed-set assertion is a set that does not contain the surface you just published on.

#### A.5 — 🚩🚩 THE MEASUREMENT THAT CONSTRAINS YOUR IMPLEMENTATION: you have **207 lines**

Live derivation, run in this tree on 2026-08-11 (`build_full_repo_plan('.')`):

| Unit | `partition_id[:12]` | Files | Physical LOC | Headroom to the 15 000 soft target |
|---|---|---|---|---|
| 1 | `477ef77d7b65` | 21 | 1 330 | 13 670 |
| **2** | **`82a3d605e61e`** | **39** | **14 793** | **207** |
| 3 | `ed6d08f25ce3` | 12 | 3 660 | 11 340 |
| | | **72** | **19 783** | |

`DEFAULT_SOFT_LOC_LIMIT = 15_000` and `DEFAULT_SOFT_FILE_LIMIT = 40`
(`argus/index/partitioner.py:108-109`). The 19 783 total reconciles **exactly** with the figure
`DF-10-4-D` recorded after Story 10.4, so this is the live, current state.

**`DF-10-4-D` has a second, independent trigger, and the operator ruling in §0.2 does not cover
it:** *"~700 added physical lines tipped an `NFR-SC1` bin-packing boundary … changing two of three
`partition_id` sha256 values on their own."* `TC-ArgusAgent-DOGFOOD-001-03` asserts every live
`partition_id[:12]` appears in the **committed** `minions-dogfood-partition-plan.md`. So:

> **If your delta adds more than 207 physical lines to files inside unit 2, the packer re-flows,
> two partition ids change, and you get Story 10.4's red mid-implementation — without having staged
> a single new file.**

**Every file this story would naively touch is in unit 2:** `argus/cli.py` (479 lines),
`argus/reports/generator.py` (743), `argus/reports/plain_english.py` (258),
`argus/ledger/coverage_report.py`. **`argus/verdict/negative_assurance.py` (424 lines) is in unit
3, with 11 340 lines of headroom.** That is one of four reasons DN-1 puts the constant there — and
it is recorded as a *measured consequence*, never as the architecture argument (see DN-1; designing
a module layout around a sha256 is the "tail-wagging-dog" `DF-10-4-D` itself warns against, so the
architecture case has to stand on its own, and it does).

⛔ **If it tips anyway: STOP.** Do not regenerate the artifacts (that is `DF-10-4-D`'s remedy,
verdict-adjacent, fenced by 10.4's DN-9 and targeted at **12.1**), and do not shrink docstrings to
hold a sha256 stable. **HALT, record the measurement, and escalate** — exactly as Story 10.4 did,
which the retrospective calls *"the epic's best moment."*

#### A.6 — Baseline, re-measured this session (LOCAL — see §0.1)

| Gate | Measured 2026-08-11, this tree | Source |
|---|---|---|
| Tests | **1 336 collected across 83 test files** (`ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`) | re-measured here |
| `mypy argus` | **clean, 72 source files** | re-measured here |
| Tracked `argus/**` modules | **72** (`git ls-files -- argus` → 72, all `.py`) | re-measured here |
| `git status --porcelain -- argus/` | **EMPTY** | re-measured here |
| `argus/pipeline.py` | **1 331 lines** vs the NFR-M1 cap of **1 200** — the only file over, no repo-wide assertion exists | re-measured here |
| Coverage | 95.51% (gate 80%) | ⚠️ **not re-run here** — Story 10.5's dev + reviewer at `93adc94` |
| `bandit -r argus --severity-level medium` | 0 High / 0 Medium (19 Low) | ⚠️ **not re-run here** — as above |
| `argus audit .` | `RELEASE_READY`, `blocking_findings=0`, exit 0 | ⚠️ **not re-run here** — as above |

**Re-verify the three ⚠️ rows rather than adopting them.** Every Epic-10 dev re-measured the SM's
figures and every divergence they found was real.

---

### §B. Where the disclosure text has to come from

**FR34, quoted** (`E-PRD/prd.md:538-543`) — *"APAA can disclose its own validation status on **every**
user-facing verdict surface, and cannot emit a verdict on a surface that omits it."* Its five
sub-clauses are the shape of your ACs:

1. **Content** — the tool's finding-precision validation state (validated / **not independently
   validated**) **and the corpus it rests on**.
2. **Mechanical enforcement, not editorial discipline** — the surface set is enumerated in a
   committed test that fails on an unenumerated member. *"A disclosure that depends on an author
   remembering is not a disclosure."*
3. **Distinct from FR17, and both apply** — FR17 bounds *this audit*; FR34 bounds *the tool*.
   *"An audit can be perfectly scoped and still be produced by an unvalidated instrument."*
4. **Removable only on measurement, and replaced rather than deleted** — when the ≥80% gate clears,
   the disclosure is **replaced** by a statement of the cleared status and the corpus that cleared
   it. *"The surface never becomes silent, and the enforcing test never becomes vacuous."*
5. **Not a permanent state** — coupled to a committed programme to clear it (**Epic 13**); if that
   programme is abandoned, the free public tier is withdrawn rather than the disclosure.

**And the architecture's binding table** (`architecture.md:185-194`) — ⚠️ **the single most
important paragraph in this story:**

| | **Run grade** (`grade: demo-heuristic-only`) | **Instrument status** (FR34) |
|---|---|---|
| Describes | how *this run* was configured | how the *tool's findings* have been validated |
| True when | the deep-audit seam was not engaged | the ≥80% precision gate is uncleared |
| Varies | **per run** | **per tool version** |
| Removed by | engaging the deep pass | **Epic 13 clearing the gate — nothing else** |

> *"Merging them would produce two wrong outcomes: a `--deep` run mislabelled heuristic-only, and a
> disclosure that appears to lift when a user enables a flag. **Enabling deep audit changes the
> run's grade. It does not validate the instrument.**"*

**Therefore: `DOGFOOD_EXTERNALIZATION_GUARD` is NOT your disclosure text.** It is a *run-grade*
sentence about the dogfood run (*"This dogfood run is a demo-heuristic-only (Tier-A) result…"*),
pinned byte-for-byte by `-48`, and reusing it on the CLI would state a per-run fact as a per-tool
fact. **What you extend is the two-sided GUARD MECHANISM (§A.4); what you author is a new,
instrument-scoped constant** (DN-4). `architecture.md:200-202` is consistent with this and says so
in the same breath: *"FR34 extends the existing guard, never a second mechanism … the two-sided
`DOGFOOD_EXTERNALIZATION_GUARD` (presence AND over-claim-phrase absence) is **widened to the
user-facing surface set**."* The *guard* is widened. The *sentence* is not moved.

---

### §C. The instrument — reuse the idiom, do not invent one

10.1–10.5 each landed a guard of the same shape, and all five passed review on iteration 1:
**registry + closure + both-direction positive control + non-vacuity.** Use it. Only the closure
device changes:

| Story | Closure device |
|---|---|
| 10.1 `test_evidence_citation.py` | **glob** over `sprint-change-proposal-*.md` — a new document cannot escape by being new |
| 10.3 `test_invocation_contract.py` | **live `argparse` walk** — the parser is exactly enumerable |
| 10.4 `test_grammar_diagnosis.py` | **the module's own source, parsed with `ast`** — the failure arms are exactly enumerable from the code |
| 10.5 `test_v1_commitment_closure.py` | **claim-shape sweep × static import-reachability walk** |
| **11.1 (this story)** | **`ast` walk of `generate_reports`' own body** (every written artifact must flow through the disclosure helper) **× a registry of non-code surfaces resolved by glob** (a new consumer-facing surface fails until registered) |

**AI-E10-5, adopted as a standing rule and applied here:** *where an AC names a set of sites, flags,
causes or requirements, the load-bearing AC is a **closure guard that FAILS on an unenumerated
member**; the list is a convenience, never the contract.* Five hand-counted enumerations in this
project were re-measured on 2026-08-10/11 and **all five were wrong**. Your surface list will be
wrong too. The closure is what saves it.

#### C.1 — The placement, decided (DN-1, DN-2)

| What | Where | Unit | Why |
|---|---|---|---|
| The status vocabulary, the constant, the pure renderer | **`argus/verdict/negative_assurance.py`** (existing, 424/1200 lines) | 3 | See DN-1 |
| CLI emission | `argus/cli.py` (existing) | 2 | ~10 lines |
| Report emission | `argus/reports/generator.py` (existing) | 2 | ~12 lines, ONE helper |
| Listing text | `pyproject.toml`, `README.md`, `action.yml`, `CHANGELOG.md` | — | not Python |
| The guard | `tests/test_instrument_disclosure.py` (**NEW**, `tests/` is outside `argus/**`) | — | plus small extensions to `tests/test_release_surface_honesty.py` |

⛔ **No new `argus/**` file. Not one.** §0.2. `git ls-files -- argus` must still return **72** at the
end, and `git status --porcelain -- argus/` must contain **only** `M` lines for the two or three
files above.

#### C.2 — The injection point that avoids the layering inversion

`generate_reports` (`argus/reports/generator.py:695-743`) is the **single write point** for all four
report artifacts — four `dest.write_text(content, encoding="utf-8")` calls in one function.

**Route every one of them through one helper**, e.g. `_with_instrument_disclosure(content) -> str`,
and let the guard **parse `generate_reports` with the stdlib `ast` module** and assert that *every*
`write_text` call in its body receives a value that flowed through that helper. A **fifth** report
added without it turns the guard RED — the 10.4 `_get_parser_for_lang` closure idiom, applied to the
report writer.

**This is why `coverage-ledger.md` needs no `argus/ledger/**` edit at all.** The content still comes
from `render_coverage_text`; the disclosure is added at the write. No inverted import, no
`argus/ledger/**` diff, no unit-2 lines spent there.

---

### §D. ⛔ FENCES — what this story must NOT touch

| Fenced | Owner | Why, and where the line sits |
|---|---|---|
| **Creating or staging ANY new `argus/**` file** | **12.1** | §0.2 / `DF-10-4-D`. Operator ruling for all of Epic 11. `git ls-files -- argus` stays at **72**. |
| **> 207 added physical lines inside dogfood unit 2** | **12.1** | §A.5. Verify empirically (AC6.3); HALT if it tips. |
| **Regenerating `minions-dogfood-*.md`** | **12.1** | Verdict-adjacent; fenced by 10.4's DN-9. Their bytes must not move. |
| **The verdict, the FR16 decision table, any threshold, any exit code** | — | ⛔ **The epic AC is explicit: *"no verdict is reworded, upgraded or hedged by this story. The decision table is untouched."*** FR37 governs explanation; FR16 governs classification. If `argus audit .` returns anything other than `RELEASE_READY / blocking_findings=0`, you have broken something. |
| **`NegativeAssuranceVerdict`'s persisted schema** (adding a field) | later story | Costs a `NEGATIVE_ASSURANCE_SCHEMA_VERSION` bump + a content-hash change + regenerated determinism goldens, and moves persisted verdict bytes inside an epic that must not. **The constant lives in the module; it does NOT become a model field.** DN-6. |
| **`argus/pipeline.py`** | **12.1** | 1 331/1 200 measured. Byte-unchanged. Nothing in this story needs it. |
| **`argus/precision/replay_harness.py`** — the `sys.path`/`_registry` import | **11.5** | Do not fix it, and do not import it from a user-facing path. §A.1 / DN-3. |
| **Building an MCP surface, entry point, extra or flag** | **12.6** | §A.2. Make it *unable to escape the guard*; do not create it. |
| **`README.md`'s INTERIM tag path, the slash-command claim, the CLI example** | **11.5 / 12.7** | Your README edit is the **disclosure paragraph only**. Do not repair adjacent falsehoods — 11.5 owns them and has ACs for each. |
| **The `tree-sitter <0.26` false green** | **11.4** | |
| **`action.yml`'s five `${{ inputs.* }}` `run:` interpolations** | **11.3** | Your `action.yml` edit is the `description:` field (+ optionally an output description). Do not touch `run:` bodies. |
| **The ≥80% precision gate itself** | **Epic 13** | **NOT CLEARED, and nothing here clears it.** `protocol_cleared` stays `False` at every call site. |
| **Publishing, tagging, `workflow_dispatch`, `git push`** | **12.9 / operator** | 10.1's DN-7: triggering a run to manufacture a citation is manufacturing evidence. |
| **🚨 H0 (who files the Minions handoff H1–H4) · `DF-7-2-A` (the human TP/FP adjudication)** | **UNOWNED / XAgent007, OPEN** | Both stay **OPEN**. `tests/test_v1_commitment_closure.py::-38` pins them; do not let a disclosure edit read as closing either. |
| **`epics.md`, `E-PRD/prd.md`, `architecture.md` §H/§Enforcement rewrites, every Epic 1–9 artifact and retrospective, the three dogfood artifacts, `_bmad/**`, `audit-ci.yml`, `.github/workflows/release.yml`** | — | ⛔ Byte-unchanged. *(One exception, additive only: `architecture.md` §Enforcement gains the FR34 guard registration — AC5.4.)* |
| **The uncommitted work already in the tree** (`tests/test_v1_commitment_closure.py` staged, 10.5's story file, `_bmad/**` churn) | operator / AI-E10-9 | Not yours. Do not commit, revert or restage it. |

---

### §E. Traps previous stories already paid for — the six that apply

| # | Trap | What it costs you here |
|---|---|---|
| **E.1** | **AI-E3-1 — a keystone test that was green over its own keystone bug** (Story 3.4). | **RED-first is MANDATORY.** Run the guard against the **undisclosed** tree and record the failures: every surface missing the disclosure, and the `write_text` closure red before the helper exists. A guard written after the change proves nothing. 10.1 went further and *repeated* the red demonstration with the final test code — do that. |
| **E.2** | **Five hand-counted enumerations, five wrong** (10.2 ×3, 10.3 4→6, 10.4 2→4, 10.5 1→3). | AC4's **closure** is load-bearing; §A.3's surface table is its *input*. Do not close this with a hand list. |
| **E.3** | **A guard that passes vacuously** (10.3's `-39`, 10.4's `-118`, 10.5's `-39`). | Assert non-zero floors: reports written > 0, registered surfaces resolved > 0, `write_text` calls found > 0. **A rename of `generate_reports`, a move of the module, or an `ast.parse` failure must turn this RED, not silently green.** |
| **E.4** | **Positive control, both directions** (10.1/10.3/10.4/10.5). | A surface *without* the disclosure must **fire**; one *with* it must **not**. An affirmative over-claim must **fire**; the honest denial form must **not** (reuse `-17b`'s cases — a trailing negation escaped the first version of that filter). Pure functions over synthetic inputs — **never** by editing a real surface during a test. |
| **E.5** | **AI-E8-1 — `git diff` cannot see an untracked path.** | `git add` this story file **and** the new test before you claim a write-set fence. Verify with `git status --porcelain` **and** `git diff --stat`. |
| **E.6** | **AI-E9-7 — never publish a prose copy of a pinned figure.** | The disclosure text lives in **one** Python constant. `README.md` / `CHANGELOG.md` / `action.yml` / `pyproject.toml` carry it because the guard **compares them against the constant**, not because someone retyped it. A hand-typed second copy is the drift class this project has hit five times. |

---

## Acceptance Criteria

### AC1 — There is ONE instrument-status vocabulary, in ONE existing module, and it is a closed set

1. **`argus/verdict/negative_assurance.py`** (existing; **no new file** — §0.2) gains, beside the
   existing `DISCLAIMER` constant it deliberately mirrors:
   - a **closed** status vocabulary with exactly **two** members — *not independently validated*
     (today) and *validated* (post-Epic-13) — expressed as an `Enum` or a frozen literal set, with
     the members' meaning documented;
   - the **disclosure text for each member**, as module constants;
   - a **pure renderer** taking the status and returning the disclosure line(s).
2. **The renderer's branch is EXHAUSTIVE and RAISES on an unregistered member** — the house pattern
   (`exit_code_for_verdict`, `_assurance_statement`, `ShipReadinessError`). ⛔ Never a silent
   default: a fall-through would render "not validated" for a state nobody registered, which is the
   *comfortable* wrong answer.
3. **The current-state text satisfies FR34's Content clause** — it states (a) that Argus's
   **finding precision has not been independently validated**, (b) **the corpus that claim rests
   on**, and (c) **what would remove it**: the **≥80% precision gate**, cleared by the human TP/FP
   adjudication in **Epic 13** — *nothing else*.
4. **It is instrument-scoped, never run-scoped** (§B). It must NOT mention `demo-heuristic-only`,
   `--deep`, Tier-A, or anything that varies per run, and `render_depth_meaning`
   (`plain_english.py:117`) is **unchanged** — a reader must not be able to conclude that enabling a
   flag lifts the disclosure.
5. **It contains no over-claim phrase.** It passes `_affirmative_over_claims` (imported, §A.4) and
   contains none of the `NegativeAssuranceVerdict` forbidden stems (`certif`, `is correct`,
   `proven`, `guarantee`, `defect-free`, `bug-free`, `passed`) — cheap insurance so the constant
   stays safe if a later story does persist it.
6. **PURE (AR8)** — no I/O, no clock, no `uuid`/`random`, no `float`, no network, and **no new
   dependency**.

### AC2 — The disclosure does not fork the state the tool already computes

1. **⛔ `argus/precision/replay_harness.py` is NOT imported by `cli.py`, `reports/**`,
   `verdict/**` or any module reachable from `argus.cli`** (§A.1 — its module-level `sys.path`
   insert + `from _registry import` is 11.5's wheel defect; putting it on the user path converts a
   latent packaging defect into a crash-on-start). Asserted by a static import walk that **does not
   `import argus`** (the 10.5 DN-6 idiom).
2. **A committed guard proves the constant and the harness agree.** The *test* may import
   `argus.precision.replay_harness` (tests already do). It asserts that the declared status is
   *not independently validated* **if and only if** no production call site passes
   `protocol_cleared=True` — measured today: **zero such call sites**, the only two occurrences
   being `tests/test_dogfood_plan.py:406,410`, which exist to prove the flip path is reachable and
   are exempted **by name with their reason**.
3. **This is the expiry, mechanised.** When Story 13.3 passes `protocol_cleared=True`, this guard
   turns **RED** until the disclosure is **replaced** by the cleared statement. ⛔ **That red is the
   guard working** — state it in the failure message, in the 10.3/10.5 house style.

### AC3 — Every surface that emits a verdict emits the disclosure

1. **CLI.** The disclosure is printed on **stderr**, **on every run that emits a verdict**,
   **unconditionally** — following `_emit_suppression_disclosure` exactly (Story 10.3 / AC4.3:
   printed even when the count is zero, *"a disclosure that only appears when something was hidden
   is one an operator learns nothing from"*).
   - **stdout is the frozen wire contract** (FR18 / AR3) and is **byte-unchanged**: a CI step parses
     it positionally. Record this choice and its residual (a consumer discarding stderr) rather than
     leaving it implicit.
   - **Placement:** after the ship-readiness block. ⛔ `tests/test_cli.py:112` asserts
     `captured.err.startswith("Ship-readiness: …")` — it must still pass.
   - **The invariant, and it is what makes this testable:** *an invocation that prints a `verdict=`
     line prints the disclosure; an invocation that exits `1` (no verdict produced, AR10) prints
     neither.* Assert both directions.
2. **Reports.** Every artifact `generate_reports` writes carries the disclosure — all **four**
   today (`final-verdict.md`, `coverage-ledger.md`, `security-review.md`,
   `architecture-review.md`), via the **single helper at the write point** (§C.2). ⛔ No
   `argus/ledger/**` edit and no inverted import.
3. **Distribution listing** — all three strings a stranger reads before installing:
   `pyproject.toml [project].description`, `README.md` (above the fold, in the same eyeline as the
   install instruction), and `action.yml`'s top-level `description:`.
4. **Release note.** `CHANGELOG.md` gains **one** `### ` section under `## Unreleased` recording the
   new disclosure. ⛔ **It must be registered in `_NOTE_SECTIONS` in the correct position** —
   `-16` pins order, not just membership (§A.4).
5. **Every listing/note copy is checked against the constant, never retyped** (E.6). The guard reads
   `argus/verdict/negative_assurance.py`'s constant and asserts each surface contains it (or a
   registered, reason-carrying shortened form for the two one-line summary fields, where a
   multi-sentence paragraph does not fit — the shortening must itself be a constant, and the guard
   must assert it is a **prefix-or-substring relation** to the full text, never an independent
   sentence).
6. **⛔ No verdict, ratio, exit code or decision-table string changes.** `argus audit .` still
   returns `RELEASE_READY / blocking_findings=0 / exit 0`, re-run and compared.

### AC4 — 🔑 The surface set is a CLOSURE: an unenumerated surface FAILS CI

**This is the load-bearing AC.** FR34's binding half is mechanical enforcement, not a list.

1. **Code side — an `ast` closure over `generate_reports`' own body.** Parse
   `argus/reports/generator.py` with the stdlib `ast` module, locate `generate_reports`, and assert
   that **every** `write_text` call in it receives a value produced by the disclosure helper. A
   **fifth report added without the helper turns this RED.** (The 10.4 `_get_parser_for_lang`
   idiom, `tests/test_grammar_diagnosis.py::-115`.)
2. **Non-code side — a registry resolved by glob, closed in both directions.** Extend
   `tests/test_release_surface_honesty.py`'s `_RELEASE_SURFACES` / `_RELEASE_SURFACE_PATTERNS` so
   that (a) `pyproject.toml` is registered, and (b) any consumer-facing surface the globs resolve
   which is **not** registered fails `-18`, as it does today.
3. **The MCP surface, which does not exist (§A.2).** A registered pin — with `12.6` named in its
   failure message — asserts that **no MCP entry point, console script, extra or module exists
   without being a registered disclosure surface.** ⛔ Do **not** create one. When 12.6 lands, this
   goes RED until 12.6 registers its surface and carries the disclosure — which is precisely what
   *"the disclosure reaches the MCP surface"* can honestly mean in a story that must not build it.
4. **Two-sided, per the epic AC and `architecture.md:200-202`: presence AND over-claim absence.**
   Reuse `_affirmative_over_claims` and its marker tuples **by import** from
   `tests/test_release_surface_honesty.py` (§A.4). ⛔ Do not re-author a substring scan —
   `-17b` documents an escape a naive one already let through.
5. **Non-vacuity is mandatory** (E.3): assert `> 0` written reports, `> 0` resolved surfaces, `> 0`
   `write_text` calls found. A rename, a module move or an `ast.parse` failure must go **RED**.
6. **Positive controls, both directions** (E.4), over synthetic inputs only.

### AC5 — The disclosure is written to be REPLACED, never deleted, and the guard cannot go vacuous

1. **The surface is never silent.** A guard asserts that **some** registered instrument-status text
   is present on every enumerated surface — so satisfying AC3 by *removing* the sentence fails.
   (This is `-19`'s shape: `-17` proves nothing bad was added; `-19` proves the honest language is
   still *there*.)
2. **Flipping the token does not make the guard pass.** A positive control renders the *validated*
   member and asserts the surfaces would go **RED** against it — i.e. the guard is keyed on *the
   rendered text for the current status*, never on a hardcoded string whose absence is trivially
   satisfiable. **This is the epic AC's "cannot pass vacuously once the token changes" clause and it
   is not optional.**
3. **The removal condition is named in the text itself** (AC1.3) and asserted: the disclosure must
   mention the ≥80% gate and Epic 13, so a reader learns what would end it. Pin it by **anchor
   text, never by line number** (`test_v1_commitment_closure.py::-31`'s standing rule).
4. **Registered in `architecture.md` §Enforcement**, in the established form used by 10.1/10.3/10.4/
   10.5 — the rule text plus the enforcing test module and its ids — and the guard asserts that
   registration is present (the `-23`/`-29`/`-41` pattern). ⛔ **Additive paragraph only**; §H and
   the rest of §Enforcement are byte-unchanged.

### AC6 — The gates run, the fences hold, and the write set is exactly what it says

1. **Gates re-run and LABELLED LOCAL** (§0.1): `mypy argus` · `bandit -r argus --severity-level
   medium` · `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 pytest tests/ --cov=argus --cov-fail-under=80` ·
   `python -m argus.cli audit .`. **Baseline re-measured by the SM 2026-08-11: 1 336 tests across
   83 files; `mypy` clean on 72 source files.** The count grows by **exactly** your new cases; **no
   test removed, skipped, weakened or `xfail`ed.** Re-verify coverage / bandit / the dogfood verdict
   rather than adopting §A.6's attributed figures.
2. **`git ls-files -- argus` returns 72**, unchanged. `git status --porcelain -- argus/` contains
   **only `M` lines** for `verdict/negative_assurance.py`, `cli.py` and `reports/generator.py` (any
   additional file is a scope leak — stop and record why).
3. **🔑 The dogfood artifacts stay byte-identical, and this is VERIFIED, not assumed** (§A.5).
   Re-run `build_full_repo_plan('.')` after implementation and assert the three `partition_id`s are
   still `477ef77d7b65…`, `82a3d605e61e…`, `ed6d08f25ce3…`, and that
   `TC-ArgusAgent-DOGFOOD-001-03`, `-06`, `-41` and the two proof assertions are green. Record the
   **added physical line count inside unit 2** against the **207-line** budget. ⛔ **If it tips:
   HALT and escalate. Do not regenerate; do not shrink prose to hold a sha stable.**
4. **Evidence-citation compliance** (10.1, `architecture.md` §H): cite the `audit-ci.yml` run
   covering **your own HEAD** *with the sha it covers*, or record **`NOT ESTABLISHED`** and name the
   command a human runs. ⛔ Do not push, tag or `workflow_dispatch`.
5. **Write set — the fence, checked with `git status --porcelain` AND `git diff --stat`:**

   | Permitted | For |
   |---|---|
   | `argus/verdict/negative_assurance.py` (**additive**; no model field — DN-6) | AC1, AC2 |
   | `argus/cli.py` (emission only) | AC3.1 |
   | `argus/reports/generator.py` (helper + four write sites) | AC3.2, AC4.1 |
   | `pyproject.toml` (`[project].description` only) · `README.md` (the disclosure paragraph only) · `action.yml` (`description:` only) · `CHANGELOG.md` (one registered section) | AC3.3, AC3.4 |
   | `tests/test_instrument_disclosure.py` (**NEW**) · `tests/test_release_surface_honesty.py` (registry extension) | AC4, AC5 |
   | `architecture.md` (**§Enforcement registration paragraph ONLY**) | AC5.4 |
   | `deferred-work.md` (**append-only**, if you file) · this story file · `sprint-status.yaml` | process |

   **Byte-unchanged, verified with `git diff --quiet`:** all of `argus/**` except the three files
   above · `argus/pipeline.py` · `argus/precision/**` · `argus/ledger/**` · `argus/reports/plain_english.py` ·
   `epics.md` · `E-PRD/**` · `audit-ci.yml` · `.github/workflows/release.yml` · the three
   `minions-dogfood-*.md` artifacts · every Epic 1–9 artifact and retrospective · `_bmad/**`.
6. **Whole-system, not just the ACs.** The full suite is green and the story leaves the system
   working end-to-end. Specifically re-run, standalone, the guards your edits land inside the read
   range of: `test_cli.py`, `test_release_surface_honesty.py`, `test_dogfood_module_split.py`,
   `test_dogfood_proof.py`, `test_dogfood_plan.py`, `test_invocation_contract.py`,
   `test_evidence_citation.py`, `test_v1_commitment_closure.py`, and the report/verdict areas.
7. **If you file anything, file it with a named human owner** (AI-E9-8, adopted as a convention:
   13/13 Epic-10 filings carry one) and append-only (§3.4), verified programmatically
   (`after.startswith(before)`), never by eye.

---

## Tasks / Subtasks

- [x] **T1 — Re-measure before you write anything — FIRST** (AC6)
  - [x] `git rev-parse --short HEAD` · `git status --porcelain -- argus/` (**must be empty**) ·
        `git ls-files -- argus | wc -l` (**72**) · `git tag -l` (**empty**).
  - [x] Re-derive §A.5: run `build_full_repo_plan('.')`, record the three `partition_id`s, the
        per-unit file/LOC rows and **your own unit-2 headroom**. This is your line budget.
  - [x] Re-derive §A.1: `grep -rn "protocol_cleared" --include=*.py .` — confirm **no production
        call site passes `True`**, and record the two test exemptions by name.
  - [x] Re-derive §A.2: `grep -rni "mcp" argus/ pyproject.toml action.yml` → expect **0**.
  - [x] Re-verify the baseline: **1 336 / 83 files**, **`mypy` clean on 72**. Record divergence
        rather than adopting the figure.
- [x] **T2 — Write the guard RED, against the undisclosed tree (AC4, AC5) — BEFORE any emission code**
  - [x] `tests/test_instrument_disclosure.py`, ids continuing the locked index: **`DOCS-001-42`..**
        (high-water is `-41`), plus **`CLI-001-50`..** (`-49`) and **`REPORT-002-30`..** (`-29`)
        where the area fits. Import the over-claim detector from `test_release_surface_honesty.py`;
        do not re-author it.
  - [x] Run it. **Record the RED output**: every surface missing the disclosure, the `write_text`
        closure red before the helper exists, the MCP pin, the non-vacuity floors.
  - [x] sha256 round-trip any file you touched to produce the RED state (10.1's pattern), and repeat
        the red demonstration with the **final** test code if the test changes afterwards.
- [x] **T3 — The constant and the renderer (AC1, AC2)**
  - [x] Add the closed vocabulary, the two texts and the pure exhaustive renderer to
        `argus/verdict/negative_assurance.py`. ⛔ **No new file. No model field.**
  - [x] Add the harness-agreement guard (AC2.2) and the static import-walk assertion (AC2.1).
- [x] **T4 — Emission (AC3)**
  - [x] `cli.py`: emit on stderr after the ship-readiness block, unconditionally, whenever a
        `verdict=` line was printed. Verify `test_cli.py:112`'s first-line pin still passes.
  - [x] `generator.py`: one helper, routed through all four `write_text` calls.
  - [x] `pyproject.toml` · `README.md` · `action.yml` · `CHANGELOG.md` (register the section in
        `_NOTE_SECTIONS` **in position**).
- [x] **T5 — Close the loop (AC5)**
  - [x] The never-silent assertion, the flipped-token positive control, the removal-condition
        anchor-text pin.
  - [x] `architecture.md` §Enforcement registration — expect it RED first (the anchor does not
        exist yet), then green.
- [x] **T6 — Gates, fences, write set (AC6)**
  - [x] mypy · bandit · full suite · coverage · `argus audit .` compared to
        `RELEASE_READY / blocking_findings=0`.
  - [x] **Re-run `build_full_repo_plan('.')` and compare the three partition ids.** Record added
        unit-2 lines vs the 207 budget. ⛔ HALT if it tipped.
  - [x] Re-run the sibling guards listed in AC6.6 standalone.
  - [x] `git status --porcelain -- argus/` shows only the permitted `M` lines; `git diff --quiet` on
        every byte-unchanged path; `git add` the new test **and** this story file (E.5).
  - [x] Record CI evidence per AC6.4 — a run covering your own HEAD, or **`NOT ESTABLISHED`**.
- [ ] **T7 — Commit this story's delta as the story closes** (AI-E10-7)
  - [ ] One commit, this story only. ⛔ Do not commit the pre-existing staged/modified files you did
        not author (`tests/test_v1_commitment_closure.py`, the 10.5 story file, `_bmad/**`).

### Review Findings

**Reviewer: bmad-code-review gate, iteration 1 (Sonnet). Verdict: PASS.** Independently re-verified
on disk — not read off the story or the dev's figures. Method and evidence below.

**The deciding question — the `test_evidence_citation.py::-22` attribution — INDEPENDENTLY PROVEN,
not merely accepted.** Beyond the dev's own measurement (git log + mtime), the reviewer ran a
positive isolation experiment: `git stash push` on exactly this story's nine touched files (`argus/
cli.py`, `argus/reports/generator.py`, `argus/verdict/negative_assurance.py`, `tests/
test_instrument_disclosure.py`, `tests/test_release_surface_honesty.py`, `README.md`,
`CHANGELOG.md`, `pyproject.toml`, `action.yml`) reverted the tree to pre-11.1 state (verified by
`git status --porcelain`) while leaving the untracked `epic-10-retro-2026-08-11.md` untouched.
`pytest tests/test_evidence_citation.py` was re-run against that reverted tree: **the identical
failure reproduced byte-for-byte** — `-22` fails because `epic-10-retro-2026-08-11.md` is
unregistered in `_STATUS_DOCUMENTS`, with zero involvement from any line this story wrote. The
stash was popped and every file's content re-hashed identical (two hashes differed by CRLF/LF
normalization noise from the Windows stash round-trip only — confirmed by normalizing line endings
before comparing; content was byte-identical). **The red is proven unattributable to this story's
delta.** Deferring it as `DF-11-1-A` (owner XAgent007, named, append-only, `deferred-work.md`
+272/−0 verified as a pure append) is judged **legitimate**: the fix (`tests/
test_evidence_citation.py::_STATUS_DOCUMENTS`) sits outside this story's AC6.5 write-set fence, and
fixing it would close an Epic-10 retrospective governance item from inside an Epic-11 story — the
same cross-scope discipline this project enforced in Story 8.1's `AC18` carve-out of three
user-adjudicated pre-existing reds.

**Independently re-run and confirmed, not adopted from the story:**
- `pytest tests/` → **1352 collected, 1351 passed, 1 failed (the attributed one above), 0 errors, 0
  skipped** (junit-xml counts). Sibling guards run standalone and green: `test_cli.py`,
  `test_release_surface_honesty.py`, `test_dogfood_module_split.py`, `test_dogfood_proof.py`,
  `test_dogfood_plan.py`, `test_invocation_contract.py`, `test_v1_commitment_closure.py`,
  `test_instrument_disclosure.py` — exit 0.
- `mypy argus` → clean, 72 source files.
- `bandit -r argus --severity-level medium` → 0 High / 0 Medium (19 Low) — exact match.
- `python -m argus.cli audit .` → `verdict=RELEASE_READY deep_ratio=61/165 blocking_findings=0
  assessed_deep_ratio=61/77 scope=application held_out=88`, exit 0, stdout exactly one
  byte-unchanged line; the FR34 disclosure correctly appears on stderr, after the ship-readiness
  block and the suppression disclosure.
- **DF-10-4-D fence** — `git ls-files -- argus` = 72 (unchanged); `git status --porcelain -- argus/`
  = exactly three ` M` lines (`cli.py`, `reports/generator.py`, `verdict/negative_assurance.py`); no
  new or untracked `argus/**` file. Holds.
- **AC6.3 LOC budget** — re-ran `build_full_repo_plan('.')` directly: partition ids unchanged
  (`477ef77d7b65`, `82a3d605e61e`, `ed6d08f25ce3`), file count 72, unit 2 = 14867 (14793 baseline,
  **+74 of the 207-line budget**). No dogfood artifact touched or regenerated. Holds.
- **Nothing published** — `git tag -l` empty, HEAD is 6 commits ahead of `origin/master` unpushed,
  no reflog evidence of any push/fetch/dispatch activity. Holds.
- **The two closures genuinely bite, not vacuously.** Read `tests/test_instrument_disclosure.py` in
  full: `unrouted_write_text_calls`/`write_text_call_count` parse `generate_reports`' real `ast` and
  are positively controlled both directions (`-32`, a synthetic 5th unrouted report is caught, a
  wrong-named helper is caught, a renamed write point zeroes the counter). `protocol_cleared_call_
  sites` is a real `ast.Call`-keyword walk, independently re-verified: `grep`-ing `argus/**` and
  `tests/**` for `protocol_cleared=True` confirms exactly the 3 real call sites the guard's
  registry names (`tests/test_dogfood_plan.py:410`, `tests/test_precision_replay.py:356,400`) across
  2 files, zero production call sites — the guard correctly excludes `test_dogfood_proof.py:567`'s
  string-literal mention, which a substring scan would have miscounted (the sixth wrong hand-count
  the story itself documents). The MCP token scan (`mcp_surface_tokens`) is scoped to `argus/**` +
  `pyproject.toml` + `action.yml` only, so it cannot false-positive on this very test file's own
  "MCP" prose.
- **The two judgement calls hold up.** (1) The harness-agreement guard as an `ast` call-site walk is
  the correct fix for a measured false positive (a substring scan flags a docstring and a comment as
  production sites) — verified the false positive is real and the `ast` fix eliminates it exactly.
  (2) The CLI invariant keyed on the `verdict=` line, not the exit code: read `argus/cli.py::main` —
  `_summary_line` (the `verdict=` line) prints at line ~486, **before** `_emit_ship_readiness` is
  even called at line 500, so by the time the `ShipReadinessError` path is reached a verdict line has
  already reached stdout; emitting the FR34 disclosure there is consistent with the stated invariant
  and does not dress a refusal as a result.

**Observations recorded, Low severity, not blocking:**
- **[Low] AC6.6 ("the full suite is green") is in tension with the one proven-pre-existing red.**
  The story's own AC6.6 does not carve out `DF-11-1-A` the way Story 8.1's `AC18` explicitly named
  its three adjudicated carve-outs. Recommend a future story or the SM amend AC6.6's text (or the
  epic's definition of "green suite") to name `DF-11-1-A` explicitly, so subsequent review passes
  don't have to re-derive the attribution from first principles. Not a code defect; no action
  required of this story's write set.
- **[Low] The AC6.5 "byte-unchanged" fence table does not literally hold against committed HEAD**
  for `architecture.md` (beyond the one permitted §Enforcement paragraph) and `E-PRD/prd.md`, but
  this is entirely inherited: both carry **pre-existing, already-reviewed Story 10.5 deltas**
  (the "Delivery-closure enforcement" paragraph and the FR23/24/26/29 struck-not-deleted amendments)
  that predate this story's session — confirmed via the sprint-status log's chronological ordering
  (10.5 code-review PASS → done precedes `create-story 11-1`). This story added exactly one
  additional paragraph to `architecture.md` (verified: `git diff` shows the "Instrument-status
  enforcement" paragraph as the only 11.1-attributable hunk) and made zero edits to `E-PRD/prd.md`.
  Not caused by 11.1. Recommend future story fences be worded as "no further diff added by this
  session" when `baseline_note` already discloses a dirty tree, to remove this ambiguity.

**All ACs (1–6) independently checked against the diffs and judged met.** SOLID/DRY/KISS/YAGNI:
the constant/vocabulary/renderer are co-located with their sibling `DISCLAIMER` (single
responsibility, no new module per DN-2's constraint); the over-claim detector and the static
import-graph walker are imported, not re-authored (DRY, avoiding the `-17b` regression class); the
single injection point at the write call avoids a layering inversion (`generator.py` already
depends on `coverage_report`, not vice versa); no speculative generalization (the MCP registry is
empty until 12.6 needs it, per YAGNI). No security, coupling or testability concerns found; every
new assertion is a pure function over synthetic or committed-text input, with real positive and
negative controls, matching this project's established idiom.

---

## Dev Notes

### LOCKED decisions taken at story design — record these, do not re-litigate

| # | Decision | Rationale |
|---|---|---|
| **DN-1** | **The constant, the vocabulary and the renderer live in `argus/verdict/negative_assurance.py`.** | Four reasons, in order of weight. (a) **It already owns this exact pattern**: `DISCLAIMER` (`:108-113`) is a fixed, no-interpolation, over-claim-free module constant stating audit-grade humility — FR34's disclosure is its sibling, and the PRD says so explicitly (*"Distinct from FR17, and both apply"*). Co-locating them makes the distinction reviewable side by side instead of asserted in prose. (b) **It is PURE (AR8) and layered correctly**: `argus/verdict/**` is already an upstream dependency of `cli.py` and `reports/generator.py`, so **no new dependency direction is created and no import cycle exists** — whereas `argus/reports/plain_english.py`, the other candidate, would have forced `argus/ledger/** → argus/reports/**` to reach `coverage-ledger.md` (C.2 removes that need entirely). (c) At **424/1200 lines** it has ample NFR-M1 room. (d) **Measured consequence, recorded honestly and deliberately NOT the argument**: it sits in dogfood **unit 3** with 11 340 lines of headroom, while every other candidate is in **unit 2** with **207** (§A.5). A module layout chosen to hold a sha256 stable is the "tail-wagging-dog" `DF-10-4-D` itself warns against — so (a)–(c) have to carry the decision on their own, and they do. |
| **DN-2** | **⛔ Zero new `argus/**` files — not "few". Zero.** The architecturally *neutral* home would have been a new `argus/shared/instrument_status.py`, following the `grammar_status.py` precedent exactly. **It is unavailable**, and the reason is recorded rather than hidden: the operator's Epic-11 ruling on `DF-10-4-D` (§0.2) forbids staging an `argus/**` module, because doing so moves the dogfood-audited population and turns five committed-artifact staleness tests red mid-implementation. **This is a constraint-driven placement, not a design-optimal one.** It is worth revisiting when Story 12.1 lands the decoupling; it does not need revisiting before then, because DN-1(a)–(c) make `negative_assurance.py` a defensible home on its own merits. |
| **DN-3** | **The disclosure declares its status WITHOUT importing `argus.precision.replay_harness`; a committed guard imports the harness and asserts they agree.** | Both halves are forced. **Not importing** is forced by measurement: `replay_harness.py:86-97` does a module-level `sys.path.insert` + `from _registry import …`, which is exactly the defect **Story 11.5** must fix for the wheel — routing it through `cli.py` would put a known-broken import on every install's critical path. **Guarding** is forced by AR7 / §3.3: a hand-maintained status that can silently disagree with the harness *is* the second mechanism the architecture forbids. A test-side closure gets both — and it is this project's established idiom (10.5's static walk, 10.3's parser walk, 10.4's `ast` walk). |
| **DN-4** | **`DOGFOOD_EXTERNALIZATION_GUARD` is NOT reused as the disclosure text. The GUARD MECHANISM is extended; the SENTENCE is not moved.** | `architecture.md:185-194` makes merging run grade and instrument status a *stated error*: it would mislabel a `--deep` run heuristic-only, and — far worse here — make the disclosure appear to lift when a user enables a flag. The guard sentence is also pinned **byte-for-byte** by `TC-ArgusAgent-DOGFOOD-001-48` precisely so it cannot be softened or repurposed. What `architecture.md:200-202` asks for is the *two-sided* (presence + over-claim-absence) **guard** widened to the user-facing surface set — which is AC4.4, satisfied by **importing** `_affirmative_over_claims` rather than re-authoring it. |
| **DN-5** | **The CLI disclosure goes to STDERR, and stdout is byte-unchanged.** | stdout is the FR18/AR3 wire contract a CI step parses positionally; the project has ruled this way twice already for the same reason (the ship-readiness block, `plain_english`; the suppression disclosure, 10.3 / AC4.3). Unconditional emission — including on a `RELEASE_READY` run — follows 10.3's stated reason: *"a disclosure that only appears when something was hidden is one an operator learns nothing from."* **The residual is real and must be recorded, not hidden:** a consumer that discards stderr sees a verdict without the disclosure. It is bounded by the FR34-compliant invariant AC3.1 pins (verdict line ⟺ disclosure line, same invocation) and by the fact that the machine consumer's own artifacts — the four reports — all carry it. |
| **DN-6** | **The disclosure does NOT become a field on `NegativeAssuranceVerdict`, and no persisted artifact schema changes.** | Adding a field costs a `NEGATIVE_ASSURANCE_SCHEMA_VERSION` bump, a changed content hash, regenerated determinism goldens and moved persisted verdict bytes — inside an epic whose charter forbids moving a verdict and whose first story must not perturb the dogfood run. The four report artifacts and the CLI already discharge the epic's enumerated surface set. If a later story wants FR34 inside the persisted evidence bundle (FR29, itself unreachable today), that is a scoped, versioned change with its own goldens — not a side effect of this one. |
| **DN-7** | **Enforcement is a CLOSURE over `generate_reports`' own body, not a list of four report names.** | AI-E10-5, now a standing story-authoring rule: *where an AC names a set, the load-bearing AC is a closure that FAILS on an unenumerated member.* Five hand-counted enumerations in this project were re-measured on 2026-08-10/11 and **all five were wrong**. A fifth report type is exactly the kind of thing Epic 12 adds. |
| **DN-8** | **11.1 does NOT build an MCP surface. It makes 12.6 unable to ship without the disclosure.** | The surface does not exist (§A.2, measured: 0 hits) and FR35 is 12.6's, whose sprint-status entry already commits it to *"Carries the FR34 disclosure."* Building a stub would also fail `test_invocation_contract.py`, which derives the accepted surface from the live parser in both directions. The honest reading of *"the disclosure reaches the MCP surface"* in a story that must not build it is: **the closure fires the day it appears.** |
| **DN-9** | **The listing/note copies are CHECKED against the constant, never retyped** — and where a one-line summary field cannot hold the full paragraph, the shortened form is itself a constant whose relation to the full text is asserted. | AI-E9-7, the most successfully adopted rule in this project's history: *never publish a prose copy of a pinned figure*, because a prose copy of an enumerable fact drifts. Four surfaces × one hand-typed sentence is four future drift sites. |
| **DN-10** | **⛔ No verdict, threshold, decision-table string, exit code or `render_depth_meaning` text changes.** | The epic AC states it outright (*"no verdict is reworded, upgraded or hedged by this story. The decision table is untouched."*). FR37 governs explanation; FR16 governs classification; this story is neither — it is a statement about the *instrument*. `argus audit .` returning anything other than `RELEASE_READY / blocking_findings=0` means something broke. |

### Architecture patterns & constraints a reviewer will check

- **AR8 pure/impure** — the constant and renderer are PURE; the print and the write are the impure
  shell (`cli.py`, `generate_reports`). No I/O, clock, `uuid`, `random`, `float` or network in the
  pure half.
- **AR7 / §3.3 no-fork** — one status source (DN-3), one disclosure text (DN-9), one injection point
  per surface class (§C.2). Do not add a second comparison, a second constant or a second scan.
- **AR10 / §Error-Degradation** — a closed vocabulary gets an exhaustive branch and a **typed
  raise**, never a silent default (AC1.2). The existing `ShipReadinessError` /
  `NegativeAssuranceError` / `exit_code_for_verdict` are the precedent.
- **NFR-M1 ≤1200 lines per `argus/**` file** — `negative_assurance.py` 424, `cli.py` 479,
  `generator.py` 743, all with room. (The cap is scoped to `argus/**`, **not** `tests/` —
  `architecture.md:660,813`; 10.5's 1308-line guard was correctly dismissed as a non-violation.)
- **NFR-S1** — the disclosure carries no source, secret or absolute host path. It is a fixed
  constant with no interpolation.
- **NFR-P1 / determinism** — the disclosure is a constant, so the reports stay byte-stable for the
  same inputs. No clock, no run id, no host path.
- **§3.4 evidence immutability** — corrections are **struck, not deleted**, dated and attributed;
  `deferred-work.md` is append-only (`+n / −0`), verified programmatically.
- **Import-isolation** — `argus.* ⊬ fastapi` (ADR #20) still holds; add no dependency. If the new
  module surface belongs in `_MODULES_UNDER_GUARD`, **extend it, never fork it**.

### Testing standards — the house form your new file matches

- **One test file per closure, ids from the locked index.** High-water measured 2026-08-11:
  `DOCS-001` → **`-41`**, `CLI-001` → **`-49`**, `REPORT-002` → **`-29`**. Continue; do not reuse.
- **Every test's docstring names its id, its AC and what failure it prevents** — read
  `tests/test_grammar_diagnosis.py` and `tests/test_release_surface_honesty.py` for the register.
- **RED-first, recorded** (E.1). **Positive controls in both directions** (E.4). **Non-vacuity
  floors** (E.3). **Failure messages say what to do**, including *"this red is the guard working"*
  where that is the truth (AC2.3).
- **Synthetic inputs only** for controls — never mutate a real surface or the real package during a
  test. Where a guard must prove it bites on the real code (10.4's reviewer injected a fifth arm
  into the live loader), restore the file and verify `git diff --quiet` afterwards.
- **Run with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`**, and set `PYTHONIOENCODING=utf-8` on this host if
  console encoding bites the em-dash-bearing prose.

### Previous story intelligence — Epic 10, all five `done`, all PASS on review iteration 1

- **10.1** wrote the evidence-citation rule you are bound by (§0.1) and demonstrated RED **twice**,
  restoring documents byte-identically by sha256 round-trip. Its DN-7 forbids triggering a CI run to
  manufacture a citation.
- **10.2** fixed multi-language grounding 8/10 → 10/10 and recorded that its own hand-written site
  list was wrong **three times** — the origin of *"the closure guard, not the site list, is the
  load-bearing AC."* Also: `except (ImportError, Exception)` moved `:266` → `:294`. **Coordinates
  drift; use anchors.**
- **10.3** moved the Live-Key Safeguard above both suppression arms and shipped
  `_emit_suppression_disclosure` — **your precedent for register, placement and unconditionality**
  (AC3.1). Its dev recorded that `cli.py`'s two `except ValueError` arms **moved ~60 lines** and must
  be located **by anchor text**.
- **10.4** turned one blanket `except` into four named arms behind an `ast`-closure guard — **the
  closure idiom AC4.1 reuses** — and **HALTED** rather than regenerate evidence at a sha that did not
  contain the deltas. Its `DF-10-4-D` is the constraint in §0.2 and §A.5. **If §A.5 tips, do what
  10.4 did.**
- **10.5** established that *a V1 commitment is delivered only when a production call site reaches
  it*, and pinned H0 and `DF-7-2-A` **open** so a sweep could not close them by accident. Its
  `tests/test_v1_commitment_closure.py::-31` **forbids line numbers in registry evidence and requires
  anchor text** — AC5.3 inherits that. Its DN-6 (a guard must not `import argus`) is AC2.1's form.
- **Recent commits, read:** `93adc94` (regenerated dogfood artifacts at a truthful sha), `a9cc933`
  (10.1–10.4 product deltas), `58821c3`, `ae5c6a3`, `ce2cc7e`. Commit-message register:
  `type(scope): a sentence in the story's own voice`.

### Runtime & toolchain, verified on this machine 2026-08-11

Windows 11 · CPython **3.11.15** · `.venv` present · `pydantic` v2 (`model_fields` on an *instance*
is deprecated — use the class) · `tree-sitter>=0.25,<0.26` with the nine-grammar `[languages]` extra
installed · CI is **ubuntu × 3.10/3.11/3.12** and has **never seen this tree** (§0.1). Console
scripts `argus` / `argus-agent` / `repo-audit`, all → `argus.cli:main` (`pyproject.toml:59-62`).

### Project structure notes

`argus/` is the only live tree. Planning artifacts are under
`_bmad-output/design-artifacts/ArgusAgent/`; the PRD is at `E-PRD/prd.md` (**not** `prd.md`) — the
skill's default glob resolves the folder, not a top-level file. Stories live in `stories/`. `tests/`
is flat (83 files) and outside `argus/**` for both NFR-M1 and the dogfood population.

### Open questions for the operator — saved for the end, as the workflow requires

1. **The stderr residual (DN-5).** A CI consumer that discards stderr sees a verdict without the
   disclosure. The alternative — an additive field on the stdout wire line — would touch the FR18
   contract that four tests pin positionally. Ruled **stderr** here, consistent with two prior
   rulings; flag it if you want the wire line to carry a token instead.
2. **`pyproject.toml [project].description` (AC3.3).** Ruled **in scope** because it is the PyPI
   summary a stranger reads before the README. If you would rather the one-liner stay clean and the
   disclosure live only in the README body + `action.yml`, say so — it is a one-line reversal, and
   `_RELEASE_SURFACES` registration would come out with it.
3. **`DF-10-2-A` (AI-E10-4) still has `target_story: NONE`** — C/C++/Ruby/Rust ground and extract
   **zero** definitions under a V1 "delivered" claim, inside the epic about publishing nothing
   untrue. The retro's natural home is **11.5**. **Not scoped here** and deliberately not filed by
   this story; it needs a story id or a dated V2 decision before Epic 11 closes.
4. **`AI-E10-8`** — `pipeline.py` is 1 331/1 200 today with **no repo-wide assertion**. The cheap
   half (the sweep test) could land before Epic 11 ends and would stop a second file joining it. Not
   scoped here; 12.1 owns the extraction.

### References

- `epics.md:1966-2016` — Epic 11 charter, dependency flow, and Story 11.1's five Given/Then ACs.
- `E-PRD/prd.md:538-543` — **FR34**, all five clauses. `:139`, `:159`, `:223`, `:300`, `:321` — the
  gate's status and the two binding conditions.
- `architecture.md:177-202` — the **run-grade vs instrument-status table** (§B) and *"FR34 extends
  the existing guard, never a second mechanism"*. `:529-552` — §H evidence-citation rule.
  `:712-758` — §Enforcement, the registration form AC5.4 follows.
- `epic-10-retro-2026-08-11.md` — §3.1 (no CI), §3.2 (`DF-10-4-D`), §6 SD-1/SD-2/SD-3, §7
  AI-E10-1/-2/-3/-5/-7.
- `deferred-work.md` — `DF-10-4-D` (the full measured mechanism), `DF-10-4-E`, `DF-10-2-A`.
- `sprint-status.yaml:384-394` — Epic 11's block, the 11.1 annotation, and the epic invariant
  *"NO STORY IN THIS EPIC PUBLISHES ANYTHING — the publish is 12.9, by design."*
- Code: `argus/cli.py:267-292` (`_summary_line`), `:362-393` (`_emit_suppression_disclosure`),
  `:396-428` (`_emit_ship_readiness`), `:431-475` (`main`) · `argus/reports/generator.py:695-743`
  (`generate_reports`) · `argus/reports/plain_english.py:117-140` (`render_depth_meaning` —
  **unchanged**) · `argus/verdict/negative_assurance.py:98-113` (`DISCLAIMER`) ·
  `argus/dogfood/proof_render.py:42-49` (`DOGFOOD_EXTERNALIZATION_GUARD` — **not your text**) ·
  `argus/precision/replay_harness.py:86-97, 219-232, 316-343` · `argus/index/partitioner.py:108-109`
  (the soft limits behind §A.5).
- Tests: `tests/test_release_surface_honesty.py:88-232` (the registries + the detector you import),
  `:235-379` (`-16`..`-19`) · `tests/test_dogfood_module_split.py:207-245` (`-48`, the two-sided
  guard) · `tests/test_dogfood_proof.py:404-440` (`-25`/`-26`) ·
  `tests/test_dogfood_plan.py:177-193` (`-03`, the partition-id staleness assertion) ·
  `tests/test_cli.py:109-112` (the stderr first-line pin) · `tests/test_grammar_diagnosis.py`
  (the `ast`-closure idiom) · `tests/test_v1_commitment_closure.py` (the anchor-text rule, `-31`;
  the open-item pins, `-38`).

---

## Dev Agent Record

### Context Reference

This story file, in full. `architecture.md` §B (run grade vs instrument status), §H, §Enforcement ·
`E-PRD/prd.md` FR34 · `tests/test_release_surface_honesty.py` (the detector imported, not
re-authored) · `tests/test_v1_commitment_closure.py` (the static import graph, imported) ·
`tests/test_grammar_diagnosis.py` (the `ast`-closure idiom).

### Agent Model Used

`claude-opus-5[1m]` (BMAD dev-story worker, mode `implement`, iteration 1).

### Debug Log References

**Every figure below is LOCAL — Windows 11 / CPython 3.11.15, `.venv`. NO CI RUN COVERS THIS WORK
(§0.1's dated risk acceptance applies unchanged).**

**T1 — re-measurement, before any write.** `HEAD` `93adc94`; `git status --porcelain -- argus/`
EMPTY; `git ls-files -- argus` **72**; `git tag -l` EMPTY. `build_full_repo_plan('.')` reproduced
§A.5 **exactly** — `477ef77d7b65` 21/1 330 · `82a3d605e61e` 39/**14 793** · `ed6d08f25ce3` 12/3 660,
total 19 783 over 72 files, so the unit-2 budget was confirmed at **207 lines**. Baseline
**1 336 tests across 83 test files** and `mypy argus` clean on **72 source files** both reproduced.
`grep -rni "mcp\|model.context.protocol" argus/ pyproject.toml action.yml` → **0**, §A.2 held.

**T2 — RED first, twice, as 10.1 did.** *Stage 1* (guard written, nothing else): collection
`ImportError: cannot import name 'INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED'` — the
vocabulary did not exist. *Stage 2* (vocabulary added, no emission): **7 of 16 RED** — `-46`
(harness agreement), `-47` (no surface carries it), `-51` (flipped-token control), `-52` (no
§Enforcement registration), `CLI-001-50`, `REPORT-002-30`, `REPORT-002-31` (*"the disclosure helper
`_with_instrument_disclosure()` is gone from the write point's module"*). *Stage 3, with the FINAL
test code* — 8 sha256 round-trips, each removing the disclosure from one real site, running the
guard, restoring, and re-hashing: `README.md`, `CHANGELOG.md`, `pyproject.toml`, `action.yml`,
`argus/reports/generator.py` (helper unrouted), `argus/cli.py` (emission removed → **2** red),
`architecture.md` (registration renamed → 1 red), and `negative_assurance.py`
(`INSTRUMENT_STATUS` flipped to `VALIDATED` → **5** red, which is AC5.2 demonstrated on the real
tree rather than only in a synthetic control). **All 8 bit; all 8 restored with a matching
sha256.**

**T6 — gates, LOCAL.** `pytest tests/` **1 352 passed / 1 failed / 0 skipped** — 1 352 = 1 336 + the
**16** new cases, exactly, nothing removed, skipped, weakened or `xfail`ed. `mypy argus` **clean, 72
source files**. `bandit -r argus --severity-level medium` **0 High / 0 Medium (19 Low)** —
identical to the attributed baseline, re-run not adopted. Coverage **95.77%** against the 80% gate
(baseline 95.51%, re-run not adopted). `python -m argus.cli audit .` →
`verdict=RELEASE_READY deep_ratio=61/165 blocking_findings=0 assessed_deep_ratio=61/77
scope=application held_out=88`, **exit 0**, stdout one line and byte-unchanged in shape.

**T6 — AC6.3, the measurement that could have halted this story.** Re-ran
`build_full_repo_plan('.')` after implementation **and again after `git add`** of the new test:
partition ids **`477ef77d7b65` / `82a3d605e61e` / `ed6d08f25ce3` — all three unchanged**, file count
still **72**. Unit 2 went **14 793 → 14 867 = +74 physical lines against the 207 budget** (133
spare); unit 3 went 3 660 → 3 804 (11 340 headroom). **No dogfood artifact was regenerated and none
was touched.** `TC-ArgusAgent-DOGFOOD-001-03`/`-06`/`-41` and the proof assertions are green inside
the full run.

**T6 — AC6.4, evidence citation.** **`NOT ESTABLISHED`.** No `audit-ci.yml` run covers this HEAD;
nothing was pushed, tagged or `workflow_dispatch`ed (10.1's DN-7). The command a human runs to
establish it: push `master` and cite the resulting `audit-ci.yml` run id **together with the sha it
covers**.

### Completion Notes List

**What shipped.** One instrument-status vocabulary (`InstrumentStatus`, closed at two members), the
disclosure text for each member plus a shortened constant for the two one-line summary fields, and
one pure exhaustive renderer — all in the **existing** `argus/verdict/negative_assurance.py`, beside
the `DISCLAIMER` it is the sibling of. Emission on `stderr` after the ship-readiness block, and one
helper at the report write point that all four `write_text` calls flow through. Four listing/note
surfaces compared **against the constant**, never transcribed.

**Design decisions taken here (beyond the locked DN-1..DN-10, which were followed as written).**

1. **The harness-agreement guard is an `ast` call-site walk, not a substring scan** — and this was
   forced by a measured false positive, not by taste. The obvious `"protocol_cleared=True" in source`
   form reported `argus/precision/replay_harness.py` **and** `argus/verdict/negative_assurance.py` as
   production sites that had cleared the gate; both were *mentions* — a docstring and this story's own
   honesty comment. A guard that cannot tell a mention from a call would have declared the precision
   gate cleared by four modules that clear nothing. `protocol_cleared_call_sites()` matches only an
   `ast.Call` carrying `protocol_cleared=True`, and carries positive controls in both directions.
2. **The CLI invariant is keyed on the `verdict=` line, not on the exit code.** The `ShipReadinessError`
   path prints a verdict on stdout and *then* exits `1`. The suppression disclosure is correctly
   withheld there — it is a claim about what THIS RUN found, beside a verdict the tool has just refused
   to vouch for — but withholding FR34 too would leave a verdict on stdout with no instrument-status
   line anywhere, which is the exact gap FR34 forbids. FR34 is a statement about the **tool**, so it
   can only add caution to a refusal, never dress one as a result. `CLI-001-51` pins both directions.
3. **The short form is a SUBSTRING of the full text, asserted** (`-48`), so the two one-line fields
   cannot drift into an independently authored second sentence (AI-E9-7).
4. **`pyproject.toml` was registered in `_RELEASE_SURFACES` *and* `_RELEASE_SURFACE_PATTERNS`**, per
   AC4.2 — publishing on a surface `-17` does not scan is where an over-claim lands unseen.

**Tradeoffs recorded rather than hidden.**

* **DN-5's stderr residual is real**: a consumer that discards stderr sees a verdict without the
  disclosure. Bounded by the AC3.1 invariant and by the four report artifacts, which all carry it.
  stdout stays the FR18/AR3 wire contract, byte-unchanged.
* **DN-2's placement is constraint-driven, not design-optimal.** The neutral home was a new
  `argus/shared/instrument_status.py`; it is unavailable under the operator's Epic-11 `DF-10-4-D`
  ruling. Worth revisiting when 12.1 lands the decoupling — DN-1(a)–(c) hold it in the meantime.

**MEASURED DIVERGENCES from this story's own context — recorded, not adopted (AI-E10-3's rule
applied to the story itself).**

1. **§A.1's call-site count was wrong, which is the SIXTH wrong hand-count in this project.** The
   story records *"the only two occurrences being `tests/test_dogfood_plan.py:406,410`"*. Measured:
   `:406` passes `False`, and the real `protocol_cleared=True` **call sites are three across two
   files** — `tests/test_dogfood_plan.py:410` and `tests/test_precision_replay.py:356,400`. A fourth
   file, `tests/test_dogfood_proof.py`, holds the literal as a *string being searched for*, not a
   call. Both registries in `_PROTOCOL_CLEARED_TEST_EXEMPTIONS` are closed in both directions, so this
   list cannot silently drift again. **The story's own headline conclusion is unchanged and was
   re-verified: ZERO production call sites pass `True`.**
2. **`tests/` holds 85 `.py` files, 83 of which contain tests** — the story's "83 test files" figure is
   the second number. No divergence in substance; recorded so the next re-measurement matches.

**⚠️ ONE PRE-EXISTING FAILURE, NOT CAUSED BY AND NOT CLOSED BY THIS STORY.**
`tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed`
fails on `epic-10-retro-2026-08-11.md`, an **untracked** Epic-10 artifact that was never registered
in `_STATUS_DOCUMENTS`. That is Story 10.1's glob closure working exactly as designed on Epic 10's
delta. **Attribution measured, not asserted:** the assertion reads two inputs only — the glob's
matches and `_STATUS_DOCUMENTS` — and this story authored neither
(`git status --porcelain -- tests/test_evidence_citation.py` is EMPTY, mtime `2026-08-10`; the retro
file is `??` untracked with mtime `2026-08-11T20:04`, ~75 minutes before this story's first write at
`21:20`). Fixing it would edit a file outside AC6.5's write set and close another epic's item, so it
is **filed as `DF-11-1-A`** (owner **XAgent007**, `deferred-work.md` append-only verified
programmatically, **+32 / −0**) and left open.

**⚠️ T7 (commit) DELIBERATELY NOT PERFORMED — the one task left unchecked.** The delta is **staged**
(`git add` of `tests/test_instrument_disclosure.py` and this story file, per E.5) and the fence was
re-verified **after** staging. Committing was not requested by the operator for this run and **no
acceptance criterion requires it** — AC6.5 requires only that the write set be *verifiable*, which
staging achieves. The commit is left to the operator / review gate. Nothing pre-existing
(`tests/test_v1_commitment_closure.py`, the 10.5 story file, `_bmad/**`) was committed, reverted or
restaged; `tests/test_v1_commitment_closure.py` is still `A ` exactly as it was found.

**Fences, verified.** `git ls-files -- argus` = **72**. `git status --porcelain -- argus/` = exactly
three ` M` lines: `argus/cli.py`, `argus/reports/generator.py`,
`argus/verdict/negative_assurance.py`. `argus/pipeline.py`, `argus/precision/**`, `argus/ledger/**`,
`argus/reports/plain_english.py`, the three `minions-dogfood-*.md` artifacts, `E-PRD/**`,
`epics.md`, `audit-ci.yml`, `.github/workflows/release.yml` and `_bmad/**` are all untouched by this
story. `architecture.md` gained **2 lines, 0 deletions** (the §Enforcement paragraph plus its blank
line); no MCP surface, entry point, extra or flag was created; no verdict, threshold, decision-table
string, exit code or `render_depth_meaning` text changed.

### File List

**Modified — `argus/**` (the three permitted, additive):**
- `argus/verdict/negative_assurance.py` — `InstrumentStatus`, the four disclosure constants, the
  status/text map, `INSTRUMENT_STATUS`, `render_instrument_disclosure`; `__all__` extended. No model
  field, no schema bump (DN-6).
- `argus/cli.py` — `_emit_instrument_disclosure()` + two call sites; the `negative_assurance` import.
- `argus/reports/generator.py` — `_with_instrument_disclosure()` + the four `write_text` calls routed
  through it; the `negative_assurance` import.

**Modified — listing / note surfaces:**
- `pyproject.toml` (`[project].description` only) · `README.md` (the disclosure paragraph only) ·
  `action.yml` (top-level `description:` only) · `CHANGELOG.md` (one registered `### ` section under
  `## Unreleased`).

**Added / modified — tests:**
- `tests/test_instrument_disclosure.py` (**NEW**, staged) — `TC-ArgusAgent-DOCS-001-42`..`-52`,
  `TC-ArgusAgent-CLI-001-50`..`-51`, `TC-ArgusAgent-REPORT-002-30`..`-32` (16 cases).
- `tests/test_release_surface_honesty.py` — `_NOTE_SECTIONS` gains the new section **in position**;
  `_RELEASE_SURFACES` and `_RELEASE_SURFACE_PATTERNS` gain `pyproject.toml`.

**Modified — process artifacts:**
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md` (§Enforcement registration paragraph
  ONLY, additive) · `deferred-work.md` (append-only, `DF-11-1-A`) · this story file ·
  `sprint-status.yaml`.

---

## Change Log

| Date | Version | Description | Author |
|---|---|---|---|
| 2026-08-11 | 0.2 | **FR34 implemented; Status `ready-for-dev` → `in-progress` → `review`.** One closed two-member `InstrumentStatus` vocabulary, four disclosure constants and one pure exhaustive renderer added to the **existing** `argus/verdict/negative_assurance.py` (**zero new `argus/**` files** — DN-2/§0.2 held; `git ls-files -- argus` still **72**). CLI emission on stderr after the ship-readiness block; one `_with_instrument_disclosure()` helper routing all four `write_text` calls in `generate_reports`; four listing/note surfaces compared **against the constant**, never retyped. Two closures shipped in `tests/test_instrument_disclosure.py` (16 cases): an `ast` walk of the write point's own body (a fifth report goes RED) and a glob-resolved surface registry plus an MCP pin that fires the day 12.6 lands (**no MCP surface built**). The expiry is mechanised — the declared status must be *not independently validated* iff no production call site passes `protocol_cleared=True`. **AC6.3 verified, not assumed: unit 2 `14 793 → 14 867` = +74 of the 207-line budget; all three `partition_id`s unchanged, before and after staging; nothing regenerated.** LOCAL gates: 1 352 tests (= 1 336 + exactly 16), `mypy` clean 72, `bandit` 0H/0M/19L, coverage 95.77%, `argus audit .` `RELEASE_READY / blocking_findings=0 / exit 0`. CI **NOT ESTABLISHED** — nothing pushed, tagged or dispatched. Two divergences from the story's own context measured and recorded (the `protocol_cleared` call-site count; the tests-file count); one **pre-existing, unrelated** red (`test_evidence_citation.py::-22`, the unregistered Epic-10 retrospective) attributed by measurement and filed as **`DF-11-1-A`** (owner XAgent007, ledger +32/−0). **T7 (commit) deliberately left unchecked**: the delta is staged, and the commit is the operator's. | Amelia (Developer) |
| 2026-08-11 | 0.1 | Story contexted from `epics.md` Epic 11 / Story 11.1, the PRD FR34 clauses, `architecture.md` §B/§H/§Enforcement and the Epic-10 retrospective. All premises re-measured on `93adc94` per **AI-E10-3** (two diverged, one held — §0.3, §A.1, §A.2); the **AI-E10-1** dated risk acceptance is recorded at §0.1; the **AI-E10-2** `DF-10-4-D` constraint is recorded at §0.2 and confirmed satisfiable, with its unnamed second trigger measured at §A.5 (a **207-line** budget in dogfood unit 2). Status `backlog` → `ready-for-dev`. | Bob (Scrum Master) |
