# Story 12.5: The default install grounds the languages it claims

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

> **ArgusAgent story — Argus repo.** ArgusAgent (formerly APAA) is a self-contained headless audit
> tool extracted from the Minions monorepo into its own repository (`Agent-Argus`, distribution
> `argus-agent`, package `argus/`). **RS-1 is binding: all work lands in THIS repo.** Planning
> artifacts live under `_bmad-output/design-artifacts/ArgusAgent/`; the tracker is that folder's
> `sprint-status.yaml`.
>
> 🔵 **This is the FIFTH story of Epic 12.** 12.1 (`done`) gave `argus/pipeline.py` its headroom;
> 12.2 (`done`) wired the deep pass; 12.3 (`done`) delivered the stage memoization cache (FR27/NFR-D1);
> 12.4 (`review`) delivered FR37 outcome explanations and ingestion boundary disclosures.
> **This story delivers NFR-P3: promoting the 9 multi-language tree-sitter grammars to default dependencies (or explicitly reconciling packaging and output disclosures so a missing grammar states its reason at the point of downgrade).** It publishes nothing until Story **12.9**.

---

## Story

As a developer whose project is not Python,
I want the public install to work on my stack out of the box,
So that I am not silently given a worse result because of a packaging choice.

**Why this is one story.** Every clause addresses **NFR-P3**: *ensuring the default public installation grounds the languages the tool claims to support without requiring a user to discover an optional extra, and stating the absence and reason in the tool's own output whenever a language grammar is uninstalled or downgraded*.

**What it is NOT.** It introduces no new parsing engine or new language grammars beyond the 10 auditable source languages (`Python`, `JavaScript`, `TypeScript`, `Go`, `Rust`, `Java`, `C`, `C++`, `Ruby`, `PHP`). It does NOT alter the AST index canary validation engine (`argus/shared/grammar_status.py`, `argus/index/ast_index.py`). And it **publishes nothing**.

---

## Acceptance Criteria

### AC1: Default Package Dependencies Include All 10 Supported Language Grammars (NFR-P3)
- **Given** NFR-P3 classifies coverage degraded by a grammar absent from the default install as a packaging defect
- **When** `argus-agent` is installed via its primary public install command (`pip install argus-agent`)
- **Then** `pyproject.toml` promotes the 9 non-Python language grammars (`tree-sitter-javascript`, `tree-sitter-typescript`, `tree-sitter-go`, `tree-sitter-rust`, `tree-sitter-java`, `tree-sitter-c`, `tree-sitter-cpp`, `tree-sitter-ruby`, `tree-sitter-php`) from optional dependencies (`[project.optional-dependencies] languages`) into core dependencies (`[project.dependencies]`).
- **Then** installing `argus-agent` without extras grounds all 10 supported source languages out of the box.

### AC2: Explicit Downgrade Reason Reporting in Tool Output
- **Given** a environment where a language grammar is uninstalled or deliberately missing
- **Then** its absence and the exact remediation reason appear **in the tool's own output at the point the file is downgraded** (`audited_shallow`), including the specific missing grammar package name (e.g. `tree-sitter-go`) and the `pip install` command required to restore deep grounding.
- **Then** the terminal report and plain English summary state the specific missing grammar package per missing language class.

### AC3: Reconcile Documentation & CI Environment Guards
- **Given** Story 10.2 documented `[languages]` extra and `audit-ci.yml` sets `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`
- **Then** `README.md`, `CHANGELOG.md`, `architecture.md`, and `pyproject.toml` are reconciled so the documentation and package metadata describe the same default grounding behavior.
- **Then** `[project.optional-dependencies] languages` is retained as an alias or documented backward-compatibility extra so existing `pip install "argus-agent[languages]"` commands continue to work without error.

### AC4: Verification Suite & NFR-M1 Compliance
- **Given** changes to `pyproject.toml`, `README.md`, `CHANGELOG.md`, and report output
- **Then** tests in `tests/test_grammar_runtime_validation.py` and `tests/test_release_surface_honesty.py` are updated to assert that all 10 language grammars are declared in core dependencies and that downgrade explanations state exact remedies.
- **Then** all files remain strictly under the NFR-M1 1200-line cap.

---

## Developer Context & Guardrails

### Technical Stack & Dependencies
- Python 3.10+ (std-lib `ast`, `pathlib`, `typing`).
- Core files modified:
  - `pyproject.toml` (promote 9 grammars from `optional-dependencies.languages` to `dependencies`)
  - `argus/reports/plain_english.py` / `argus/reports/generator.py`
  - `README.md`, `CHANGELOG.md`, `architecture.md`
- Test files modified:
  - `tests/test_grammar_runtime_validation.py`
  - `tests/test_release_surface_honesty.py`

### Key Architecture & Design Rules
1. **Packaging Precision (NFR-P3)**: All 10 supported language grammars are part of the base `dependencies` in `pyproject.toml`.
2. **Backward Compatibility**: Keep `languages` in `[project.optional-dependencies]` pointing to the grammars (or empty alias) so `pip install ".[languages]"` does not fail.
3. **No Network Calls in Tests**: All tests must run offline with local mocks/canaries.
4. **File Line Cap (NFR-M1)**: Ensure all modified files remain under the 1200-line limit.

---

## Tasks & Subtasks

- [x] **Task 1: Promote Language Grammars in `pyproject.toml`**
  - [x] Move the 9 tree-sitter grammar dependencies (`tree-sitter-javascript`, `tree-sitter-typescript`, `tree-sitter-go`, `tree-sitter-rust`, `tree-sitter-java`, `tree-sitter-c`, `tree-sitter-cpp`, `tree-sitter-ruby`, `tree-sitter-php`) into `[project.dependencies]`.
  - [x] Retain `[project.optional-dependencies] languages` for backward compatibility.

- [x] **Task 2: Enhance Downgrade Explanation in Plain English & Summary Reports**
  - [x] Audit `_render_grammar_remedy` in `argus/reports/generator.py` and `plain_english.py`.
  - [x] Verify that when any grammar is missing or unvalidated, the tool output explicitly names the missing package and exact `pip install` command at the point of file downgrade (`audited_shallow`).

- [x] **Task 3: Reconcile Documentation & Surface Registration**
  - [x] Update `README.md`, `CHANGELOG.md`, and `architecture.md` to reflect that all 10 supported source languages are grounded by default in `argus-agent`.
  - [x] Register the new release note section in `tests/test_release_surface_honesty.py` `_NOTE_SECTIONS`.

- [x] **Task 4: Execute Verification Gates & Dogfood Currency Check**
  - [x] Run `python -m pytest` and verify 100% pass rate across the full test suite. *(Two artifact-currency guards are structurally blocked on the commit — see Debug Log §5; they are not defects in this change and clear mechanically once the `argus/` delta is committed.)*
  - [x] Run `python -m mypy argus` and verify clean static typing.
  - [x] Run `bandit -r argus` and verify no new security findings.
  - [x] Run `python scripts/regenerate_dogfood_artifacts.py` if `argus/` files changed to keep dogfood artifacts current. *(RUN and REFUSED by the script's own designed guard — it will not render an artifact citing a commit that does not contain the code it describes. Commit-then-regenerate is the documented bootstrap; see Debug Log §5.)*

---

## Dev Agent Record

### Debug Log
- Story created via `bmad-create-story` for Story 12-5 (`12-5-default-install-grounds-languages-it-claims`).
- Baseline HEAD commit: `2821301`. Implementation baseline HEAD: `41b8024`.

**§1 — Reconciled a partial start already in the working tree (not re-implemented).**
The tree already carried an unreviewed partial start: the nine grammars promoted in
`pyproject.toml`, `uv.lock` regenerated, README/CHANGELOG/architecture prose rewritten, a
`_NOTE_SECTIONS` registration, an emptied `_EXEMPT_BY_DESIGN`, and a new
`tests/test_default_install_languages.py`. It was extended and CORRECTED rather than
overwritten. What was wrong and what was done about it:

| Pre-existing state | Why it was wrong | Resolution |
|---|---|---|
| `architecture.md` §L446 and §L1071: the ⚠️ open-decision paragraphs were **deleted** and replaced | §3.4 evidence immutability — a superseded record is STRUCK, never deleted; the record of what the default install used to be is what makes this change auditable, and `test_spec_claim_scope.py` enforces the strike form over this exact corpus | Originals restored **struck** (`~~…~~`) with the dated, reasoned resolution beside them, including *why* promote-to-base-deps was chosen over document-the-extra and the cost accepted |
| `_EXEMPT_BY_DESIGN = {}` with `-26`'s `assert _EXEMPT_BY_DESIGN` left standing | **Suite was RED on arrival** (1 failure, the only one in the baseline run) | Emptying is CORRECT — the two exemptions covered exactly the sentences 12.5 struck, and `-26`'s EXERCISED half would have failed on them. The non-emptiness assertion was removed with its reasoning recorded: "nothing needs an exemption" is the healthiest state, and requiring one pressures a future story to invent it. `-27` re-armed to assert both sentences survive **in struck form** |
| `tests/test_default_install_languages.py` (new file, `TC-…-PACKAGING-001-01/-02`) | AC4 names `tests/test_grammar_runtime_validation.py` as the home; a second file is a second home for one fact, and `PACKAGING-001` is an invented verification area with no precedent in the suite | Assertions moved into `test_grammar_runtime_validation.py` beside `-54` (which already parses `pyproject.toml` for the same class of drift), re-issued as `TC-ArgusAgent-DOCS-001-61`, and materially strengthened (see §3). File deleted |
| README: *"As of Story 12.5 (NFR-P3), the default installation grounds…"*, and a table still describing what "the extra changes" | A README is read by strangers, not by the sprint; and the table described the extra as load-bearing, which is exactly the reconciliation AC3 demands | Rewritten as product prose, with the superseded sentence struck in place (README already uses that form at `:260`), and the table re-pointed at the run-time case that survives — grammar unusable **anyway** |
| CHANGELOG: three flat "**No Optional Extra Discovery Required.**"-style paragraphs | Registered in `_NOTE_SECTIONS` with a one-line placement comment, while that registry's own contract is that placement is a reasoned DECISION | Rewritten to the note's register (what a consumer had, what it cost them, what changed, what is retained, what it costs now), and the registry comment now argues its FIRST placement against 11.1's incumbency rather than asserting it |
| `pyproject.toml` promotion carried no reason | The metadata is a release surface; a promotion with no recorded reason is indistinguishable from a mistake | Comments added: why the promotion (NFR-P3 as a packaging defect), why the specifiers are unchanged, why the alias is retained — plus 12.5's explicit decision to **retain** the `tree-sitter<0.26` bound, which `pyproject.toml:33` had recorded as owned by this story |

**§2 — Task 2 was NOT a no-op audit, and the codebase said so by name.**
The task text reads as a verification ("audit `_render_grammar_remedy` … verify"), and the
existing renderer already names the package and the command. The gap is the TRIGGER, and it
was measured, filed and fenced by Story 10.4: `_render_readability_warning` returns early on
`if eligible: return []`, so the disclosure fires only when **nothing** parsed. A polyglot
repository whose Python parses — the exact user in this story's role sentence — learned
nothing about its failed Go grammar. `DF-10-4-A`, and both
`argus/reports/generator.py:398-401` and `tests/test_grammar_diagnosis.py::-002-29` hand it to
Story 12.5 **by name** ("widening the trigger adds a per-file point-of-downgrade surface 12.5
owns"). Closing it is what makes AC2 true rather than nominally satisfied.

**§3 — RED evidence, captured before any `argus/` edit.**
`test_a_missing_grammar_names_itself_at_the_point_of_downgrade`,
`test_the_downgrade_section_does_not_double_report_or_misfire` and
`test_the_plain_english_summary_names_the_package_per_language_class` all failed on
`AttributeError: module 'argus.reports.generator' has no attribute
'_render_grammar_downgrade_section'` / `…'render_grammar_downgrade_summary'` — i.e. the
surface did not exist, which is the honest RED for "the operator is told nothing".
`TC-ArgusAgent-DOCS-001-61` passed on arrival (the pre-existing `pyproject.toml` edit), and is
retained as the guard AC1 needs rather than as evidence of work: it now derives its expectation
from `GRAMMAR_PACKAGE_BY_LANGUAGE` (so an eleventh language fails at edit time), pins the
`[languages]` alias equal to the default requirements **specifier-for-specifier**, and reads
the README through a struck-span filter so the mandated amendment form cannot look like the
defect.

**§4 — Commands run.**
- `python -m pytest -q` — full suite. **Baseline on arrival: 1 failure**
  (`test_spec_claim_scope.py::-26`, caused by the partial start — see §1). **After: 1477
  collected, 1475 passed, 2 failed**, and both are the artifact-currency guards of §5. Every
  other test in the suite is green, including all of Story 10.4's and 11.4's grammar guards
  whose fences this change deliberately did not move.
- `python -m pytest tests/test_grammar_runtime_validation.py -q` → 26 passed.
- `python -m mypy argus` → `Success: no issues found in 75 source files`.
- `python -m bandit -r argus -q` → Low 19 / Medium 0 / High 0. Re-measured with `argus/`
  stashed: **identical 19/0/0**, so the delta introduces no new finding (the raw count alone
  would not have shown that).
- Line counts (NFR-M1 ≤1200): `generator.py` 909, `plain_english.py` 543,
  `test_grammar_runtime_validation.py` 1148, `test_spec_claim_scope.py` 607,
  `test_release_surface_honesty.py` 483, `architecture.md` 1121. ⚠️ For the next story to touch
  it: `test_grammar_runtime_validation.py` has **52 lines of headroom**; it should be split
  rather than extended again.

**§5 — The two dogfood guards, and why they are NOT green (stated, not hidden).**
`tests/test_dogfood_plan.py::test_committed_partition_plan_artifact_exists_and_matches_live_derivation`
and `tests/test_dogfood_proof.py::test_committed_proof_artifact_exists_and_matches_live_run`
fail on the physical-LOC figure (live `22487` vs the committed artifact's), because this change
adds lines to `argus/`. Task 4's remedy was run and **refused by design**:

```
REFUSED — `argus/` has uncommitted changes:
 M argus/reports/generator.py
 M argus/reports/plain_english.py
… Regenerating now would produce an artifact citing a commit that does NOT contain the code
it describes. COMMIT the `argus/` delta first, then re-run this script, then commit the
regenerated artifacts as a separate commit.
```

That refusal is the `DF-10-4-D` bootstrap, stated in the script's own docstring as *"not a
preference"*. This session is under a no-commit instruction, so the ordering cannot be
completed here. ⛔ **Required follow-up, in this order, by whoever commits:** (1) commit the
`argus/` delta; (2) `python scripts/regenerate_dogfood_artifacts.py`; (3) commit the three
regenerated artifacts as a SEPARATE commit. Both guards then pass. Nothing was loosened,
skipped or `xfail`-ed to make them green — `DF-8-5-B`'s rule is *"do not close it by loosening
an assertion"*, and a red that names its own remedy is worth more than a green that hides one.

### Completion Notes

**What was implemented**

1. **AC1 — the default install grounds all ten languages.** The nine non-Python grammars are
   `[project.dependencies]`, at the specifiers the extra already declared (a promotion that
   also moved a bound would be two changes wearing one review). `uv.lock` was already
   regenerated consistently by the partial start and was verified, not re-run.
2. **AC2 — the reason is stated where it costs you.** New
   `argus/reports/generator.py::_render_grammar_downgrade_section` names every downgraded
   file, the depth it actually reached, and the grammar package that would have grounded it;
   new `argus/reports/plain_english.py::render_grammar_downgrade_summary` states the same
   facts once per failure class in the human register. Closes `DF-10-4-A`.
3. **AC3 — one product, described the same way everywhere.** README (struck + rewritten),
   CHANGELOG (new first section, reasoned placement), `architecture.md` (both NFR-P3 sites,
   struck + resolved with the rejected alternative and the accepted cost recorded),
   `pyproject.toml` (the reason in the metadata itself).
4. **AC4 — the guards.** `TC-ArgusAgent-DOCS-001-61` (packaging + docs reconciliation),
   `TC-ArgusAgent-REPORT-002-35`/`-36` (the point-of-downgrade surface, incl. the
   double-report and 10.4-fence controls), `TC-ArgusAgent-REPORT-002-37` (the human register,
   incl. exhaustiveness-with-raise). All files under the 1200-line cap.

**Design decisions, and the reasoning behind them**

- **A SEPARATE surface, not a widening of Story 10.4's trigger.** `TC-…-REPORT-002-29`
  fences `_render_readability_warning` to stay silent when some files parsed, and it is
  RIGHT to: that callout's sentence is *"No file could be parsed — this verdict reflects
  tooling, not code quality"*, which is FALSE for a partially-parsed repository. Widening it
  would have closed `DF-10-4-A` by making 10.4's guarantee untrue. The new section stands
  down when nothing parsed, so exactly one of the two renders per run — both directions
  pinned by `-36`.
- **The wording lives in `plain_english`, the evidence lives in `generator`.** The report
  section REUSES `render_grammar_downgrade_summary` rather than authoring a second copy of
  the remedies. `argus/shared/grammar_status.py` exists because this project has paid
  repeatedly for one fact living in two places; two human surfaces of one run naming
  different packages for the same failure is precisely that defect. What the report adds is
  the half a sentence cannot carry: WHICH files, at WHAT depth.
- **The classification is never re-derived.** Both surfaces call `classify_reason`; neither
  slices the token. A prefix reader goes SILENT on `grammar_entrypoint_missing_go` and
  MISDIRECTS if widened (`pip install tree-sitter-entrypoint_missing_go`) — both pinned.
- **Exhaustive with a raise, no fallthrough.** `_downgrade_sentence` raises for an
  unregistered `GrammarFailure` instead of rendering a neighbouring cause's remedy. This is
  `DF-10-4-E`'s lesson applied on the day the surface was written rather than after it bites;
  `-37` drives all five causes and a fake sixth.
- **Scope boundary held: `argus/cli.py` was NOT touched (this is a deliberate omission, not
  an oversight).** The CLI's stderr human register cannot show these sentences today because
  the grammar diagnosis does not travel on `AuditVerdict`, and `run_audit` returns only that.
  Reaching it would mean either a field on the frozen FR18/AR3 verdict contract or switching
  the CLI to `run_audit_detailed` (which four tests monkeypatch by name). Both are outside
  this story's stated "Core files modified" list, and `epics.md:2431` gives **Story 12.8** the
  operator-error diagnosis surface explicitly naming *"missing grammar"* — a boundary
  `grammar_status.py:62` already states ("the report layer owns report wording, and Story 12.8
  owns the CLI's"). `render_grammar_downgrade_summary` is the function 12.8 wires; it ships
  with a real production caller today, so it is not a dead parameter awaiting a user.
- **`render_ship_readiness` gained NO new keyword.** Considered and rejected: it would have
  had no production caller (the `degraded_conditions` / `non_auditable_suffixes` parameters
  added by 12.4 are already in that state, filed as `DF-10-4-B`). YAGNI, and one fewer
  unwired seam.
- **`tree-sitter<0.26` bound retained.** `pyproject.toml:33` recorded widening it as "a
  packaging decision owned by 12.5 / the operator". 12.5 decides: it stays. NFR-P3 is about
  which grammars the default install carries, not about the core's supported range, and
  Story 11.4's evidence for the bound is untouched — widening it would ship an untested
  toolchain range under cover of a packaging story.

**Tradeoffs accepted, stated rather than buried**

- Every install now pulls nine grammar wheels, including for a Python-only user. Accepted
  because NFR-P3 rules the alternative — a discovery step the user must not miss — a
  packaging defect, and it is recorded in the CHANGELOG rather than left for a reader to
  notice from a slower `pip install`.
- Two small classification loops exist (one in `generator`, one in `plain_english`) rather
  than one shared grouping helper. A shared helper was considered; it would have removed
  `classify_reason` from `generator.py`'s source, which `TC-…-REPORT-002-28` asserts is
  present by name. The duplicated part is a five-line `Counter` fold; the FACTS both folds
  read — classification and package name — remain single-sourced, which is the invariant that
  guard actually protects.

### File List
- `pyproject.toml` (UPDATE: 9 grammars promoted to `[project.dependencies]`; `[languages]` retained as a documented alias; the promotion's reason and the `<0.26` retention decision recorded)
- `uv.lock` (UPDATE: lock regenerated for the promotion — verified consistent, produced by the partial start)
- `argus/reports/plain_english.py` (UPDATE: `render_grammar_downgrade_summary` + `_downgrade_sentence`)
- `argus/reports/generator.py` (UPDATE: `_render_grammar_downgrade_section`, `_MAX_LISTED_GRAMMAR_DOWNGRADES`, wired into `render_final_verdict_report`)
- `README.md` (UPDATE: default-install section rewritten; superseded sentence struck, not deleted)
- `CHANGELOG.md` (UPDATE: new `### Fixed — the default install now grounds every language the tool claims to support`)
- `_bmad-output/design-artifacts/ArgusAgent/architecture.md` (UPDATE: both NFR-P3 sites — decision recorded, originals struck)
- `tests/test_grammar_runtime_validation.py` (UPDATE: `TC-ArgusAgent-DOCS-001-61`, `TC-ArgusAgent-REPORT-002-35`/`-36`/`-37`)
- `tests/test_release_surface_honesty.py` (UPDATE: `_NOTE_SECTIONS` registration with reasoned placement)
- `tests/test_spec_claim_scope.py` (UPDATE: `_EXEMPT_BY_DESIGN` emptiness reasoned; `-26` non-emptiness assertion removed; `-27` re-armed on the struck sentences)
- `tests/test_default_install_languages.py` (DELETED: superseded by `TC-ArgusAgent-DOCS-001-61` in the AC4-named home)
- `_bmad-output/design-artifacts/ArgusAgent/stories/12-5-default-install-grounds-languages-it-claims.md` (UPDATE: tasks, Dev Agent Record, Change Log, Status)
- `_bmad-output/design-artifacts/ArgusAgent/sprint-status.yaml` (UPDATE: 12-5 → in-progress → review)

## Change Log

| Date | Change |
|---|---|
| 2026-08-15 | Story 12.5 implemented (NFR-P3). Nine non-Python tree-sitter grammars promoted to `[project.dependencies]`; `[languages]` retained as an alias pinned equal to the default requirements. New point-of-downgrade disclosure (`_render_grammar_downgrade_section` + `render_grammar_downgrade_summary`) closes `DF-10-4-A`. README / CHANGELOG / `architecture.md` / `pyproject.toml` reconciled, superseded wording struck per §3.4. Guards added: `TC-ArgusAgent-DOCS-001-61`, `TC-ArgusAgent-REPORT-002-35`/`-36`/`-37`. Status → `review`. |
