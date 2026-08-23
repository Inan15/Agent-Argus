---
baseline_commit: d6625b5
---

# Story 16.7: Adjudicate the silent-test class before anyone proposes promoting it

Status: in-progress

<!-- Contexted 2026-08-23 at HEAD `d6625b5` by the create-story workflow (Opus 5).

     ⛔ EVERY FIGURE IN §0 WAS READ OFF THE TREE BY EXECUTION — the class re-derived at HEAD,
     the gate blast radius simulated in memory against the committed record, the three
     registries that go RED proved by running their own walks, the baseline gates all re-run.
     Nothing below is copied from `epics.md`, from `sprint-change-proposal-2026-08-22.md` or
     from the sprint-status comment. Where an artifact and the tree disagree, §0 says so and
     THE TREE WINS.

     ⛔ NO `argus/`, `tests/` or `scripts/` file was touched to produce this story. Every
     simulation was in-memory monkeypatching of module globals inside a throwaway interpreter;
     `adjudication-record.json` was proved byte-identical before and after (§0.3). No detector
     ran over any BENCH member; no third-party fetch; nothing ratified; no disposition written;
     no role filled; no `V1.4` row; `DF-13-5-A` OPEN and UNSPENT.

     ⛔ THIS FILE IS WRITTEN AGAINST THE EPIC'S OWN RECORD OF HOW ITS STORIES FAIL. Stories 16.5
     AND 16.6 each failed an independent readiness validation, and in both cases every blocking
     defect was in the STORY TEXT, not in the research: an AC unsatisfiable inside its own
     byte-unchanged fence · two ACs that contradicted each other · a motivating premise that was
     factually false · an AC repaired on one side of the file while its executable twin in the
     task list kept the defect. So: every AC below is individually satisfiable, is named by at
     least one task, and every task cites the AC it discharges. §3 carries the AC↔Task map, and
     it is there to be checked rather than trusted. -->

## Story

As the **Engineering Lead**,
I want **the silent-test class adjudicated by a named human under protocol §4, as a MEASUREMENT**,
so that **any future promotion proposal carries a measurement instead of an estimate.**

### What this story IS

An **instrument plus a measurement**, in that order, over a **36-member advisory class** that the
tool currently flags and nobody has ever judged.

Formulating the per-call question as *"reaches the SUT, discards the result, and asserts nothing at
all"* — the **V2 silent** variant — reaches **36** of the 1,032 recorded `vacuous_test_heuristic`
findings at HEAD (§0.1). The shipped verdict-eligibility predicate reaches **0**; dropping its
provably-dead mock-referencing clause reaches **6**. The class is the largest cheaply-reachable
population there is, and its **true-positive proportion is unmeasured**.

The story builds the derivation, publishes the class, seeds one `UNADJUDICATED` row per member,
hands the worklist to the named human, and **STOPS**. The judgements are the human's act.

### What it is NOT

- ⛔ **NOT a promotion.** No finding becomes verdict-eligible. Not one row's `verdict_eligible`
  moves off `False`, and no `argus/detectors/**` byte changes.
- ⛔ **NOT a change to the gate.** `adjudication-record.json`, `adjudication-set-13-5.json`,
  `adjudication-set.json` and `gate-decision-record.json` are **byte-unchanged**. The gate stays
  `BLOCKED`, `protocol_cleared` stays `False`, `SECTION_5_CONDITIONS` stays at **SEVEN**,
  `PRECISION_GATE_THRESHOLD` stays `Fraction(4, 5)`, `VALIDATION_SET_FLOOR_N` stays 5, `N` stays 5.
  ⛔ **§0.3 measures what happens if you get this wrong, and it is the single most consequential
  fact in this story.**
- ⛔ **NOT a new adjudication set, and NOT a detector run.** No member is audited, no bench
  candidate is fetched, `DF-13-5-A`'s ONE round stays **UNSPENT**. The class is re-derived
  **read-only from pinned git objects** over the population the committed
  `adjudication-set-13-5.json` already records.
- ⛔ **NOT an independence claim, and NOT a role being filled.** Independence for this population is
  **DERIVED** from the ids that actually authored rows, through the **existing**
  `assess_independence`, and it **gates nothing** (AC6). The External adjudicator stays *unfilled*.
- ⛔ **NOT a widening of the closed vocabularies.** `DISPOSITIONS` stays at **four** members and
  `ROW_FIELDS` at **eleven**. §0.3 measures why touching either is fatal, not merely unwise.
- ⛔ **NOT a protocol amendment.** §2, §3, §4 and §5 are byte-unchanged, no `V1.4` row is added, and
  the change-log head stays **V1.3**.

---

## §0 — PREMISES RE-MEASURED BY EXECUTION at HEAD `d6625b5`

⛔ **Task 0 re-derives every row below before a line is written.** Every story in Epic 16 found a
stated premise false by executing it — 16.4 found three, 16.6 found two. **This story already
carries two of its own (§0.2's stale `DF-16-7-A` figure, and §0.7's unsatisfiable invariance
contract inherited from 16.6). Expect a third.**

### §0.0 The tree, the paths, and the baseline

Branch `epic-16/discharge-df-15-2-d`, HEAD **`d6625b5`** (*"docs(16-6): the gate count the record got
wrong, measured a third time"*). Working tree at contexting carried **three** modified files, all
under `_bmad-output/design-artifacts/ArgusAgent/`: `deferred-work.md` (the uncommitted
`DF-16-6-E`/`DF-16-6-F` appends from 16.6's iteration-2 review), `sprint-status.yaml`, and 16.6's
story file. create-story then added **this file** and touched `sprint-status.yaml`.

⛔ **Do NOT assert a COUNT of working-tree entries.** The tree moves between sessions and this epic
has been bitten by that four times. **The invariant that holds, and the only one an AC may assert,
is ZERO entries under `argus/`, `tests/`, `scripts/` or
`_bmad-output/design-artifacts/ArgusAgent/validation-corpus/`** (AC8.1, Task 0.1).

⛔ **PATH ROOTS — read this BEFORE Task 0's first command. This file mixes THREE of them, and
16.6's own PATH ROOTS block was itself wrong the first time it was written.**
1. **Repo-root-relative:** `argus/**`, `tests/**`, `scripts/**`, `pyproject.toml`, `docs/**`.
2. **`_bmad-output/design-artifacts/ArgusAgent/`** holds `epics.md`, `architecture.md`,
   **`deferred-work.md`**, `precision-validation-protocol.md`, the sprint-change proposals, and
   `research/`.
3. **`_bmad-output/design-artifacts/ArgusAgent/validation-corpus/`** holds
   `adjudication-set.json`, `adjudication-set-13-5.json`, `adjudication-record.json`,
   `gate-decision-record.json` and the two blocking worklists — **and nothing else**. This story's
   two NEW artifacts belong here.
4. **`_bmad-output/design-artifacts/ArgusAgent/stories/`** holds this file and its validation
   reports.

⛔ **`deferred-work.md` is NOT under `validation-corpus/`.** Task 8 ENOENTs on its first line if you
look for it there. Resolve the corpus artifacts through the builders' own path constants
(`scripts/build_gate_decision.py`, `scripts/build_adjudication_record.py`,
`argus.precision.adjudication.RECORD_PATH`) rather than re-typing a root.

**THE BASELINE, MEASURED — and it is GREEN, but only on the second attempt. Read the caveat.**

| Gate | Command | Measured at `d6625b5` | Exit |
|---|---|---|---|
| Full suite | `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 pytest` | **1,695 passed, 0 failed** in 299.93s | **0** ✅ |
| Coverage | `pytest --cov=argus --cov-fail-under=80` | **95.55%** (7,095 stmts, 316 missed) | **0** ✅ |
| Types | `mypy argus` (**the CI scope**) | *"Success: no issues found in **94** source files"* | **0** ✅ |
| Security | `bandit -r argus --severity-level medium` | *"No issues identified"* — Medium **0**, High **0**, 25,786 LOC | **0** ✅ |
| Ceiling | `pytest tests/test_module_size_ceiling.py` | **6 passed** | **0** ✅ |
| Builder | `python scripts/build_adjudication_record.py --check` | *"the adjudication record is current (**31** row(s))"* | **0** ✅ |
| Builder | `python scripts/build_gate_decision.py --check` | *"CURRENT — **BLOCKED** (NOT COMPUTED BY THIS RUN)"* | **0** ✅ |

⛔ **THE FIRST FULL-SUITE RUN OF THIS CONTEXTING SESSION WAS RED, AND IT WAS A FALSE RED FROM STALE
BYTECODE.** It failed exactly one case —
`tests/test_release_surface_honesty.py::test_TC_ArgusAgent_DOCS_001_63_the_verdict_vocabulary_on_the_page_is_derived`
— reporting six env-var tokens against `docs/first-run.md`, a file nothing in the tree had touched.
The case **passed in isolation on the next two runs**, and after
`find . -name __pycache__ -type d -exec rm -rf {} +` the whole suite returned **1,695 passed / exit
0**. Nothing in `docs/` had moved. **This is §2.5's recorded 16.2 lesson reproducing live, on this
HEAD, today.**

> ⛔ **WRITING RULE, and it is not optional: run every suite invocation in this story under
> `PYTHONDONTWRITEBYTECODE=1` with `__pycache__` cleared first.** A RED you did not cause will cost
> you a cycle, and this story performs several mutation rounds that each re-import the same modules.

⛔ **SECOND WRITING RULE — the closure-verb trap, which made 16.6's own baseline RED.**
`story_closure_claims` (`tests/test_governance_record_integrity.py`) is **line-scoped by design**,
and its verb set is `CLOSED | Closes | closes | Closed by this story | closed by this story`. It
globs **every** `*.md` under `stories/`. **A closure verb must never share a physical line with a
`DF-*` id the ledger does not back.** Wrap the line instead. `DF-16-6-D` files the recurring
authoring defect; §0.0's rule is the interim remedy.

⚠️ **ONE MEASURED CAVEAT, recorded rather than smoothed.** `mypy argus scripts` — **wider** than
CI — reports pre-existing errors in `scripts/` that predate this story
(`scripts/candidate_selection.py`, `scripts/build_gate_decision.py`,
`scripts/audit_validation_corpus.py`). **CI runs `mypy argus`** (`.github/workflows/audit-ci.yml`),
which is clean. Do not widen the scope on a hunch and then believe you caused the red.

⛔ **Local gates are Windows-only; CI runs an ubuntu matrix.** This story writes a **subprocess-,
path- and encoding-touching builder**, which is precisely the class this repository has already
shipped POSIX-only bugs from (`AI-E13-1`), and `DF-16-6-F` is an OPEN entry for exactly this bug in
a sibling guard. **AC8.4 makes portability an explicit criterion, not a hope.**

### §0.1 ⛔ THE CLASS, RE-DERIVED AT HEAD — 36, and the 39 → 36 delta reproduces exactly

Measured by driving the **shipped** `provenance_evidence()`, the **shipped** `is_assertion_callee` /
`opens_bare_assert` / `index_aligned_lines`, and a real `build_ast_index`, over blobs materialised
from each member's **pinned git object** into a scratch tree — the method
`sprint-change-proposal-2026-08-22.md` certified. **All 1,032 walked, 0 skipped, 0 unresolvable.**

| | Count |
|---|---:|
| Recorded `vacuous_test_heuristic` findings in `adjudication-set-13-5.json` | **1,032** |
| **V2 silent at HEAD** (`disc≥1 ∧ the span asserts NOTHING`, WIDE vocabulary) | **36** |
| V2 with `"AssertionError"` removed from the wide table — i.e. **pre-16.6** | **39** |
| ⛔ **Removed by Story 16.6 — false accusations from the vocabulary gap** | **3** |

**The epic text, the change proposal and the sprint-status comment all say 36 (39 measured, 3
removed). They are RIGHT, and this story CONFIRMS rather than corrects them.** That is worth saying
out loud, because two of the last three stories in this epic found their stated premise false and a
dev arriving with that expectation may go looking for a discrepancy that is not there.

**The three 16.6 removed, named rather than counted:**

| Member | Locator | Test |
|---|---|---|
| minions | `tests/apaa/test_prosecutor.py:347` | `test_malformed_top_level_arguments_raise_typed_error` |
| agent-smith | `agentsmith-core/tests/test_compiler.py:1203` | `test_conformance_structural_checks_are_zero_token` |
| agent-smith | `agentsmith-core/tests/test_surface_envelope.py:223` | `test_an_outcome_outside_the_closed_set_has_no_exit_code_and_no_fallback` |

**By member, at HEAD: `agent-smith` 22 + `minions` 14 = 36**, across **19 distinct files**
(agent-smith 10, minions 9). `agent-markovich`, `xagents-webapp` and `ai-body-runtime` contribute
**ZERO** — a re-derivation reporting a hit in those three has a bug, not a discovery.

**THE 36, IN FULL.** `disc` = `discarded_sut_calls`, `cons` = `consumed_sut_calls`, `cmt` = the span
contains at least one `#` comment (a crude triage aid, **not** a judgement — see `DN-16-7-5`).

| # | Member | Locator | Test | lines | disc | cons | cmt |
|--:|---|---|---|--:|--:|--:|:-:|
| 1 | agent-smith | `agentsmith-core/tests/test_compiler.py:262` | `test_compiler_taint_tracking_success` | 35 | 1 | 1 | Y |
| 2 | agent-smith | `agentsmith-core/tests/test_contracts.py:182` | `test_manifest_schema_with_model_pin` | 29 | 1 | 1 | Y |
| 3 | agent-smith | `agentsmith-core/tests/test_contracts.py:213` | `test_trust_report_schema_with_model_drift` | 44 | 1 | 1 | Y |
| 4 | agent-smith | `agentsmith-core/tests/test_contracts.py:783` | `test_pre_16_1_wir_without_new_fields_still_validates` | 16 | 1 | 1 | – |
| 5 | agent-smith | `agentsmith-core/tests/test_contracts.py:903` | `test_16_1_pre_change_manifest_at_1_4_0_still_schema_valid` | 18 | 1 | 1 | – |
| 6 | agent-smith | `agentsmith-core/tests/test_guarantee_backcompat.py:71` | `test_guarantee_level_admitted_on_all_surfaces` | 7 | 1 | 3 | Y |
| 7 | agent-smith | `agentsmith-core/tests/test_hybrid_composition.py:381` | `test_hybrid_report_validates_against_existing_trust_report_schema` | 25 | 1 | 13 | – |
| 8 | agent-smith | `agentsmith-core/tests/test_observe_network_proxy.py:122` | `test_summary_validates_against_9_1_schema` | 6 | 2 | 3 | Y |
| 9 | agent-smith | `agentsmith-core/tests/test_regression_alarm.py:376` | `test_engine_hook_swallows_a_forced_alarm_producer_error` | 17 | 1 | 4 | Y |
| 10 | agent-smith | `agentsmith-core/tests/test_regression_alarm.py:460` | `test_live_hook_budget_failclose_swallows_alarm_sink_error_ne…` | 28 | 1 | 5 | Y |
| 11 | agent-smith | `agentsmith-core/tests/test_security.py:34` | `test_validate_db_identifiers_accepts_valid_mapping` | 7 | 1 | 0 | Y |
| 12 | agent-smith | `agentsmith-core/tests/test_security.py:59` | `test_validate_db_identifiers_allows_absent_and_null_blocks` | 3 | 2 | 0 | Y |
| 13 | agent-smith | `agentsmith-core/tests/test_security.py:69` | `test_validate_db_identifiers_accepts_valid_select_list` | 4 | 3 | 0 | Y |
| 14 | agent-smith | `agentsmith-core/tests/test_security.py:98` | `test_validate_db_shape_allows_safe_and_non_destructive` | 6 | 4 | 0 | Y |
| 15 | agent-smith | `agentsmith-core/tests/test_security.py:129` | `test_validate_db_identifiers_exempts_non_query_nodes` | 6 | 3 | 0 | Y |
| 16 | agent-smith | `agentsmith-core/tests/test_trust_report.py:629` | `test_report_validates_against_contracts_schema` | 7 | 1 | 6 | – |
| 17 | agent-smith | `agentsmith-core/tests/test_trust_report.py:639` | `test_signed_report_validates_against_contracts_schema` | 6 | 1 | 6 | – |
| 18 | agent-smith | `agentsmith-core/tests/test_ui_emitter.py:92` | `test_ui_emitter_envelope_fit` | 31 | 1 | 3 | Y |
| 19 | agent-smith | `agentsmith-core/tests/test_wir_contracts.py:88` | `test_wir_schema_is_valid_json_schema` | 2 | 1 | 1 | – |
| 20 | agent-smith | `agentsmith-core/tests/test_wir_contracts.py:92` | `test_command_schema_is_valid_json_schema` | 2 | 1 | 1 | – |
| 21 | agent-smith | `agentsmith-core/tests/test_wir_contracts.py:98` | `test_spike_example_wir_validates` | 2 | 1 | 1 | – |
| 22 | agent-smith | `agentsmith-core/tests/test_wir_contracts.py:102` | `test_spike_example_commands_validate` | 4 | 1 | 1 | – |
| 23 | minions | `tests/apaa/test_coverage_ledger.py:239` | `test_no_float_fields_serialize` | 5 | 1 | 3 | Y |
| 24 | minions | `tests/apaa/test_recording_schema.py:155` | `test_recording_serializes_clean` | 3 | 1 | 2 | Y |
| 25 | minions | `tests/config/test_config_llm.py:356` | `test_missing_provider_module_is_silently_skipped` | 11 | 1 | 1 | Y |
| 26 | minions | `tests/governance/test_gate_policy.py:35` | `test_enforce_accepts_valid_approved_gate` | 9 | 1 | 2 | – |
| 27 | minions | `tests/governance/test_hitl_intent_approval.py:467` | `test_ledger_outage_never_turns_a_recorded_approval_into_a_50…` | 10 | 1 | 3 | – |
| 28 | minions | `tests/governance/test_policy_threshold_hardening.py:288` | `test_mint_internal_system_token_satisfies_policy_mutator_cap` | 8 | 1 | 2 | Y |
| 29 | minions | `tests/providers/test_providers_base.py:314` | `test_all_capabilities_present` | 3 | 1 | 1 | – |
| 30 | minions | `tests/providers/test_providers_base.py:318` | `test_llm_request` | 4 | 2 | 1 | – |
| 31 | minions | `tests/providers/test_providers_base.py:323` | `test_llm_response` | 3 | 1 | 1 | – |
| 32 | minions | `tests/providers/test_providers_base.py:327` | `test_dispatch_request_backward_compat` | 5 | 3 | 1 | – |
| 33 | minions | `tests/providers/test_providers_base.py:333` | `test_protocol_imports` | 7 | 5 | 1 | – |
| 34 | minions | `tests/providers/test_providers_base.py:341` | `test_deprecation_warning` | 4 | 2 | 1 | – |
| 35 | minions | `tests/runtime/test_run_index_patrol_escalation.py:84` | `test_escalation_never_raises_even_if_incident_backend_fails` | 9 | 1 | 4 | Y |
| 36 | minions | `tests/test_import_paths.py:225` | `test_component_module_importable` | 3 | 1 | 0 | – |

⛔ **The deliberate smoke test the change proposal names is row 23** — `test_no_float_fields_serialize`,
whose entire assertion is a `# must not raise` comment no analyser can read. **It is IN the class at
HEAD**, confirmed by execution. It is not a hypothetical; it is a member the human will judge.

⛔ **18 of the 36 carry a comment somewhere in the span.** That is an **upper bound on a shape**, not
a count of smoke tests, and it is recorded as triage colour only. `DN-16-7-5` forbids turning it
into a disposition, a default, or an ordering of the worklist.

### §0.2 The variant lattice at HEAD — and `DF-16-7-A`'s figure is now STALE

Re-derived at HEAD by `research/investigate-per-call-scoping.py` (committed, read-only, validated in
both directions by its own harness):

| Variant | Definition | At HEAD | Recorded elsewhere |
|---|---|--:|---|
| **V0 shipped** | `disc≥1 ∧ cons=0 ∧ mref≥1` | **0** | 0 ✅ agrees |
| **V1 drop dead clause** | `disc≥1 ∧ cons=0` | **6** | 6 ✅ agrees |
| **V2 silent** ⬅ **this story** | `disc≥1 ∧ span asserts NOTHING` | **36** | 36 ✅ agrees |
| **V3 strict** | `V1 ∧ silent` | **6** | — |
| **V5 unrelated** | `disc≥1 ∧ asserts, none about the SUT` | **125** | ⛔ `DF-16-7-A` says **122** |
| **V4 upper bound** | `disc≥1` alone | **676** | 676 ✅ agrees |
| — | spans asserting nothing at all, any `disc` | **45** | — |

⛔ **`V3 = 6 = |V1|`, so `V1 ⊆ V2`, and 30 of the 36 lie OUTSIDE V1.** The class is therefore **not**
a superset-by-relaxation of fact (b): thirty of its members have at least one **consumed** SUT call
(one has thirteen), which shipped fact (b) can never reach under any clause removal. **Anyone who
later proposes promoting V2 is proposing a genuinely different predicate, not a loosening.** Record
that; it is the fact a promotion proposal will need and the one nobody has written down.

⛔ **`DF-16-7-A` records V5 = 122; the tree at HEAD says 125.** The delta is **exactly** 16.6's
three: a `raise AssertionError("msg")` is now recognised, so those three spans stopped being
*silent* and became *asserts-but-not-about-the-SUT*. **The ledger entry is not wrong — it is
correctly dated 2026-08-22 and pre-16.6.** ⛔ **Do NOT edit it — the ledger is append-only
(`TC-ArgusAgent-DOCS-001-78`).** Record the re-measurement as a new dated entry (AC8.5,
`DF-16-7-B`), which is this project's *strike, never erase* habit (§3.4).

### §0.3 ⛔⛔ THE BLAST RADIUS — WHERE THE DISPOSITIONS MUST NOT GO. MEASURED, NOT ARGUED.

**This is the single most consequential section in this story, and the one thing a dev is most
likely to get catastrophically wrong.** The obvious move — *"it is an adjudication, so it goes on
the adjudication record"* — silently moves the externalization gate.

`argus/precision/adjudication.py::AdjudicationRecord.counts()` tallies **every live row**, with
**no `verdict_eligible` filter**, and `decide_gate` derives `adjudicators` off `record.live_rows()`.
Simulated in memory by appending 36 advisory `TP` rows attributed to `"Veer Pratap Singh (QA Lead)"`
to the committed record and re-deriving:

| Derived quantity | Today | With 36 advisory rows appended |
|---|---:|---:|
| `precision.total_tp` | **0** | **36** |
| `precision.total_fp` | 26 | 26 |
| `concentration.adjudicated_population` (breadth/seal/yield all read it) | **31** | **67** |
| `concentration.distinct_rule_class_count` | **1** | **2** |
| `independence.status` | **`NOT_INDEPENDENT`** | ⛔ **`SECOND_REVIEWER_INTERNAL`** |
| `breadth.holds` | False | False |
| `yield.holds` | True | True |

⛔ **Two of those are outright forbidden by this story's own charter.** The epic's last AC reads
*"no finding is promoted to verdict-eligible, no threshold moves, `decide_gate` is not re-run"*, and
flipping the published independence status is a claim about the **gate's** adjudication that this
population has no standing to make (§2's 2026-08-23 dated block: *"a claim about the ADJUDICATION
THAT WAS PERFORMED"* — the gate's, not this one's).

⛔ **And it is wrong on the protocol's own terms, independently of the arithmetic.** Every one of the
1,032 is `verdict_eligible: false, advisory: true` — verified by execution. Three separate shipped
surfaces already say advisory findings do not belong on that record:
- protocol §4: *"Advisory findings are recorded but are not false accusations and do not enter the
  precision denominator."*
- `scripts/build_adjudication_record.py`: *"only `verdict_eligible` findings enter the record,
  because only a blocking finding is a false ACCUSATION."*
- `validation-corpus/blocking-worklist-13-5.md`: *"an advisory finding does not move a verdict and
  is not a false accusation, so it is not in the denominator."*

> ⛔ **DECISION `DN-16-7-1`: this story's dispositions live in NEW artifacts of their own, and
> `adjudication-record.json` is BYTE-UNCHANGED.** AC3 and AC8.2 assert it by execution.

⛔ **This does NOT answer, and must not be read as answering, Story 16.4's HALT-2.** HALT-2 (append
a second **blocking** population to the committed record vs. write a fresh superseding one) is
**moot and deliberately unanswered**, and it stays that way: this story produces no blocking
population, so the choice does not arise. Taking it here would be exactly the speculative decision
16.4's AC1.3 forbade.

**AND THE TWO CLOSED SCHEMAS ARE FATAL TO TOUCH. Measured:**

| Simulated change | Measured effect |
|---|---|
| add `"idiom"` to `ROW_FIELDS` | ⛔ `load_record()` on the committed record **RAISES** immediately: `adjudication row schema violation: missing=['idiom']` |
| add a member to `DISPOSITIONS` | `counts()` grows a key; `TC-ArgusAgent-PRECISION-001-38` checks the vocabulary in **both** directions, so an unexercised member is itself a finding, and the gate record republishes the vocabulary |

`adjudication-record.json` was confirmed **byte-identical before and after** the whole simulation,
and `rec.to_bytes() == <committed bytes>` is `True` — so the record is exactly what its own
serializer produces, and any drift is yours.

> ⛔ **DECISION `DN-16-7-2`: this story adds NO field to `ROW_FIELDS` and NO member to
> `DISPOSITIONS`.** The smoke-test outcome is an **orthogonal field on a NEW row type** (AC5),
> never a fifth disposition.

### §0.4 The roles — one FILLED ahead of this story, one still UNFILLED

Read directly out of `precision-validation-protocol.md` §2:

| Role | Holder | State |
|---|---|---|
| Engineering Lead (primary adjudicator) | **XAgent007** | ✅ named |
| QA Lead (second reviewer) | **Veer Pratap Singh** | ✅ **FILLED 2026-08-22**, a dated block under **V1.3**, **no `V1.4` row** — *"filled ahead of Story 16.7 rather than during it"* |
| External adjudicator (tie-break) | — | ⛔ **UNFILLED** |

⛔ **The precondition the epic and the change proposal both state — "the QA Lead role must be filled
before 16.7 runs" — is DISCHARGED. Do not re-plan it, do not re-fill it, and do not gate on it.**
`PROTOCOL_ADJUDICATOR_ROLES` is `("Engineering Lead", "QA Lead", "External adjudicator")`, verified
by import; the exact `adjudicator` string for the QA Lead is **`"Veer Pratap Singh (QA Lead)"`**, and
`AdjudicationRow.__post_init__` raises `UnregisteredAdjudicator` on anything that does not match
`^<who> \(<role>\)$` with a registered role.

⛔ **The External adjudicator is STILL UNFILLED and that is deliberate.** §2's own words: *"a
borderline on which the Engineering Lead and QA Lead persistently disagree still has nowhere to go,
and a story reaching that step must STOP and report the rows rather than resolve them by default."*
⚠️ **A `BORDERLINE` is NOT automatically an escalation.** §4's ladder is three steps —
(1) re-examine the locator, (2) correct the golden key and re-run, (3) external tie-break — and only
**persistent disagreement between the two filled roles** reaches step 3. `BORDERLINE` is a
first-class recorded outcome at any point (AC4.3).

**Expected borderline volume, from the only comparable population:** the 2026-08-16 run produced
**5 BORDERLINE of 31** live rows (verified by reading the committed record's counts:
`TP 0, FP 26, BORDERLINE 5, UNADJUDICATED 0`). §2's dated block predicts *"roughly six"* for this
class. **Do not treat six as a target, a quota or a checksum.**

**Effort:** protocol §3's ceiling for a full adjudication run is **≤ 4 expert-hours**, which over 36
rows is ~6.7 minutes a row. It is **a ceiling, not a target**, and `expert_hours_report()` **returns
a sentence and gates nothing** (AC6.1).

### §0.5 ⛔ THE HUMAN ACT — why this story cannot finish itself, and what "done" means

The record's own vocabulary settles this, mechanically and in writing:

> `UNADJUDICATED` — *"NOT YET JUDGED … **The ONLY member an automated producer may write**, and it
> must carry no adjudicator."* And §2's 2026-08-16 amendment: *"An autonomous story that tags its own
> findings TP has measured nothing and has produced the exact artifact Epic 13 exists to make
> impossible."*

⛔ **The dev agent may not author a TP, an FP or a BORDERLINE. Not one.** `AdjudicationRow`'s
construction-time check cannot tell a machine from a human typing a name — which is precisely why
the rule has to be honoured rather than merely enforced.

**Precedent, twice over.** Story 13.2 *"delivered the instrument (AC1–AC6, AC8) and escalated AC7"* —
that sentence is still the live `expert_hours_note` on the committed record. Story 16.4
*"CLOSED BY DECISION, not by result"*, halting at Task 1 on an operator act, with its own AC1.4
recording that **reaching the halt and reporting is the story succeeding**.

> ⛔ **DECISION `DN-16-7-3`: this story is delivered in TWO halves and the second is an OPERATOR
> ACT.** Tasks 0–6 are fully machine-executable and fully testable and MUST be completed. Task 7 is
> the **HALT**: the dev publishes the worklist, states the exact judgement it needs, and **STOPS**.
> If — and only if — the operator supplies judgements in-session, the dev **TRANSCRIBES** them
> verbatim, records that they were transcribed and from whom, and never infers, completes or
> defaults a single one. **A story that halts here with the instrument built and the worklist
> published has SUCCEEDED** (AC4.5).

⛔ **This does not weaken the epic's AC — it is the only reading consistent with the protocol.** The
epic requires *"every member carries one live TP/FP/BORDERLINE disposition … from a named human"*.
That criterion is **satisfiable only by the named human**, and this story is what makes it
satisfiable. Recorded here rather than silently narrowed.

### §0.6 ⛔ THREE GUARDS GO RED THE MOMENT YOU ADD A FILE UNDER `argus/`. All three MEASURED.

Each of these has burned a cycle in this repository before. All three fire on this story's shape.

**(1) `TC-ArgusAgent-RELEASE-001-11` — the import-reach registry.**
`tests/test_release_preflight.py::_MODULES_NAMING_THE_TEST_TREE_IMPORT` is an **exact-equality**
frozenset of the `argus/**` modules that reach `_registry`. Re-ran its own `ast` walk here:
baseline reach is **14** modules. Injecting a synthetic
`argus/precision/silent_class.py` containing only
`from argus.precision.adjudication import AdjudicationRow` takes it to **15**, with
`argus/precision/silent_class.py` as the new entry. Injecting one that imports only
`argus.detectors.provenance_scan` leaves it at **14**.
⛔ **So: the new module must be REGISTERED, with a prose comment saying the addition is
deliberate** — the pattern Story 16.5 followed verbatim for `gate_independence.py` (read that
comment; it is the template).

**(2) `TC-ArgusAgent-DOGFOOD-001-50` — the dogfood currency guard.**
`tests/test_dogfood_artifact_currency.py` fails the moment `argus/**` moves past the sha the three
committed dogfood artifacts cite. Story 16.6 hit this and had to spend a whole commit on it
(`6304552`, *"regenerate the dogfood artifacts the +79 re-armed"*). ⛔ **And
`scripts/regenerate_dogfood_artifacts.py` REFUSES to run on a dirty `argus/` tree** (exit 2), so the
ordering is forced: **commit `argus/` FIRST, then regenerate, then commit the artifacts separately.**
That is why AC9.2's commit arc has four commits and not three.

**(3) `TC-ArgusAgent-RELEASE-001-20` — the built-distribution import.**
Every shipped module is imported out of a **real wheel** in a clean subprocess with this repository
off `sys.path`. ⛔ **So the new module must resolve NO repository path at module level** (`DF-9-2-A`):
every path is a repo-relative **string** the caller resolves, or an argument. This is the treatment
`adjudication.RECORD_PATH` and `gate_decision.DECISION_RECORD_PATH` already get.

⛔ **`tests/test_gate_seal.py::_ADJUDICATION_SETS` must NOT gain an entry.** It registers **audit
outputs** (`adjudication-set.json`, `adjudication-set-13-5.json`), and Story 16.4 §2.4 recorded that
adding a set to it *"would retroactively declare the newly-audited members `pre-seal` and destroy the
seal condition in the act of satisfying it."* **This story produces no adjudication set.** Leave it
at two.

⛔ **`tests/test_status_document_registry.py::_STATUS_DOCUMENTS` must NOT gain an entry either.**
Measured: it registers **change proposals and retrospectives only**, matched by the glob
`sprint-change-proposal-*.md`. A `validation-corpus/` artifact is out of its subject.

### §0.7 ⛔ THE CORPUS CHECKOUTS — and why 16.6's INVARIANCE contract is itself unsatisfiable here

Measured at contexting, then again ~40 minutes later after the read-only re-derivation:

| Member | Checkout | before | after | byte-identical? |
|---|---|--:|--:|:-:|
| `agent-markovich` | `…/AgentMarkovich` | 0 | 0 | ✅ |
| `minions` | `…/Minions` | **7** | **1** | ⛔ **NO** |
| `xagents-webapp` | `…/XAgents-WebApp` | 1 | 1 | ✅ |
| `agent-smith` | `…/XAgents/XAgents/Agent-Smith` (⚠️ **depth 5**, not 4) | 1 | 1 | ✅ |
| `ai-body-runtime` | `…/ai_body_runtime` | 0 | 0 | ✅ |

⛔ **`minions` changed under me, and nothing this session did could have caused it.** Its seven
entries (four of them about a *defer-ledger-hygiene* story) were replaced by **one entirely different
entry**. It is a **live working tree another party is editing**, and the same tree has now returned
**13 → 14 → 0 → 7 → 1** across five same-day measurements by 16.6 and this session.

> ⛔ **THE INHERITED AC IS UNSATISFIABLE, AND THIS IS EXACTLY THE STORY 16.5 DEFECT CLASS.** Story
> 16.6's AC4.5 requires the members' `git status --porcelain` be **byte-identical before and after**.
> That check **just failed here, for a reason nobody in this story controls.** 16.6 correctly
> replaced *emptiness* with *invariance*; the measurement above shows invariance is **also** not
> assertable on a shared live checkout. **This story does not inherit the defect.**

> ⛔ **DECISION `DN-16-7-4`: the containment claim is about THIS STORY'S ACTIONS, not the member's
> state, and it is proved two ways that are both satisfiable and strictly stronger.**
> **(i)** every read of a member goes through the **shipped, content-addressed** helpers
> `scripts/pinned_corpus_snapshot.py::pinned_tree` / `materialize_pinned_bytes` /
> `verify_pinned_bytes` — `ls-tree` + `cat-file`, both pure reads of the object database, with the
> materialised bytes **proved against the pin by blob hash**. What the working tree holds cannot
> reach the measurement.
> **(ii)** the harness's git command vocabulary is a **named read-only allow-list**, asserted by
> execution; `checkout`, `stash`, `clean`, `reset`, `worktree`, `add`, `commit`, `fetch` and `pull`
> are absent, and the absence is a test, not a promise.
> The porcelain captures are still **taken and RECORDED in Completion Notes as an observation**, and
> a difference is **reported, never failed** (AC8.3).

⛔ **`git status --porcelain` over THIS repository IS invariant across a mutation and IS asserted**
(AC7.2) — that tree is under the story's control and the check is both satisfiable and meaningful.

### §0.8 Module headroom, next free ids, and the ledger's byte state

Measured with the ceiling guard's own `_physical_line_count` (`_CEILING = 1200`) at `d6625b5`:

| File | Lines | Headroom | Note |
|---|--:|--:|---|
| **`argus/precision/silent_class.py`** | — | **1,200** | ⬅ **NEW.** `DN-16-7-6`. |
| **`scripts/build_silent_class_record.py`** | — | **1,200** | ⬅ **NEW.** The I/O half (AR8). |
| **`tests/test_silent_class.py`** | — | **1,200** | ⬅ **NEW.** The guards. |
| `argus/precision/adjudication.py` | 977 | 223 | ⛔ **byte-unchanged** (AC3.4) |
| `argus/precision/gate_decision.py` | 1,132 | **68** | ⛔ `DF-16-5-A` OPEN. Put **nothing** here. |
| `argus/precision/gate_independence.py` | 328 | 872 | imported, not edited |
| `argus/detectors/vacuous_vocabulary.py` | 534 | 666 | ⛔ byte-unchanged |
| `argus/detectors/vacuous_test.py` | 796 | 404 | ⛔ byte-unchanged |
| `argus/detectors/provenance_scan.py` | 976 | 224 | ⛔ byte-unchanged |
| `scripts/audit_validation_corpus.py` | 752 | 448 | ⛔ **not run, not edited** |
| `scripts/pinned_corpus_snapshot.py` | — | — | imported, **not edited** |
| `tests/test_gate_independence.py` | 1,127 | **73** | ⛔ `DF-16-5-B` OPEN |
| `tests/test_vacuous_density.py` | 1,159 | **41** | ⛔ `DF-15-2-E` OPEN, trigger **1,180** |
| `tests/test_vacuous_vocabulary.py` | 757 | 443 | new at 16.6, untouched |
| `tests/test_release_preflight.py` | — | — | ⚠️ **one registry entry + comment** (§0.6) |

**Next free verification ids, re-derived across `argus/`, `tests/`, `scripts/` and the artifact
tree:** `TC-ArgusAgent-PRECISION-001-` is at **114** → ⛔ **this story starts at `-115`**.
(`DETECT-001` is at 144 and `DOCS-001` at 80 — neither is this story's family.) **Re-derive before
writing; do not trust this line.**

**Next free ledger id:** `DF-16-7-A` is **TAKEN** (filed 2026-08-22 by the change proposal). ⛔ **This
story files `DF-16-7-B`.** Confirm on disk before writing and take the next free letter if it moved.

⛔ **`deferred-work.md` byte state, re-measured:** **457,560 bytes**, exactly **one lone `CR`** (a
`\r` not followed by `\n`), **zero** `CRLF` pairs, ends with a newline, and `git ls-files --eol`
reports `i/-text w/-text` — i.e. git treats it as **binary**, which is the only reason
`core.autocrlf=true` leaves it alone. **Any editor that opens and re-saves it destroys it, and git
books that as a one-line DELETION of a historical entry.** It has happened once already
(`9aea1be`, repaired by `a4de7e7`). **Append in binary and assert the bytes** (AC8.5, `DF-16-6-C`).

### §0.9 What is already true and must NOT be re-done

| Already true | Evidence |
|---|---|
| Story **16.6** is `done` | HEAD `d6625b5`; `is_assertion_callee("AssertionError")` is `True`; `len(_ASSERTION_CALLEES) == 89` |
| The **QA Lead role is FILLED** | Veer Pratap Singh, operator act 2026-08-22, dated block under **V1.3**, **no `V1.4` row** (§0.4) |
| The `vacuous_test.py` cohesion split | `4123931` + `ba5e8df`; `DF-15-2-D` disposed 2026-08-22. **Do not re-split anything.** |
| Story 16.4 is terminal | `done` by DECISION 2026-08-22. Its AC7.1 `argus/detectors/**` byte-unchanged fence no longer blocks this story — **but this story keeps `argus/detectors/**` byte-unchanged anyway**, for its own reason (AC2.2). |
| `SECTION_5_CONDITIONS` is at **SEVEN** | Stories 16.1–16.3 + 16.5. `precision_evaluable` has exactly **four** conjuncts. **This story adds neither.** |
| The **36** figure | ✅ **Re-derived at HEAD and it AGREES with the epic** (§0.1) — the rare case in this epic where the artifact is right |
| The baseline is **GREEN** | §0.0 — but the first run was a **false RED from stale bytecode**. Re-verify anyway; that is Task 0. |
| `adjudication-record.json` is its own serializer's output | `rec.to_bytes() == <committed bytes>` is `True`, measured |
| Every one of the 1,032 is **advisory** | `verdict_eligible: false, advisory: true` across the whole set, measured. **Zero blocking findings in `adjudication-set-13-5.json`.** |

---

## §1 — WHY THIS STORY EXISTS

### §1.1 The gate is blocked on an empty denominator, and this is the only measured way out

The corrected detector emits **0 blocking findings of 4,284** over the ratified corpus. The gate is
`BLOCKED` on an **empty denominator**, not on a shortfall, and `DF-13-5-A`'s pre-registered answer to
that is explicit: *"a materially better detector — NOT a bigger bench."*

A better detector needs a **predicate that reaches something**. Three candidates were measured
(§0.2). V1 reaches 6 — too few to rest a precision figure on, and `DF-16-6-A` files why. V5 reaches
125 but needs real dataflow and is chartered to Story 6.2. **V2 reaches 36 and is reachable today.**

### §1.2 …and the class must NOT be promoted on this evidence, which is the whole point

A three-case spot-check found the class contains the **deliberate smoke test** — `# must not raise`,
where *"does not raise"* **is** the assertion, stated in a comment no analyser can read. `DN-3`
already carves out the **explicit** spelling (`pytest.raises`); this is the **implicit** one, and
**the proportion is unmeasured**. Promoting blind would manufacture exactly the false 🔴 that
cross-cutting #6 exists to prevent, in a project whose locked asymmetry says *a false 🔴 is the
lethal failure; a real vacuous test left advisory is tolerable*.

**So this story measures the proportion. It promotes nothing.** If the class turns out to be
predominantly real, a *later* story may propose promotion carrying **this story's number** as its
evidence — which is the same author-then-approve separation §4.3 of the 2026-08-20 proposal
established for the gate amendment.

### §1.3 What this story does NOT fix, named so it is not mistaken for fixed

- **Nothing is promoted.** `verdict_eligible` stays `False` on every one of the 36.
- **`DF-16-6-A`** — fact (b)'s mock-referencing clause is dead over the corpus (0 of 1,032).
  **OPEN, untouched.** Removing it would promote 6.
- **`DF-16-7-A`** — per-call observation analysis (V5) still needs real dataflow, still targets
  Story 6.2. This story only records that its figure moved 122 → 125 (§0.2).
- **`DF-16-6-B`/`-C`/`-D`/`-E`/`-F`, `DF-16-5-A`/`-B`, `DF-16-1-A`, `DF-15-2-E`, `DF-14-1-A`,
  `DF-14-3-A/B/C/H`** — all **OPEN, all untouched.**
- **The External adjudicator role stays unfilled**, and the gate's own independence status stays
  `NOT_INDEPENDENT`.
- **The corpus artifacts do not move.** §0.3, AC8.2.

---

## §2 — THE COUPLINGS THAT WILL BITE

### §2.1 ⛔ The derivation must be COMPOSED from the shipped predicate, never re-implemented

`AR7 / §3.3`: *one arithmetic, one vocabulary, never forked.* The silent predicate is built from
four shipped things and nothing else:

| Question | Shipped answer — **use it** | ⛔ Do NOT |
|---|---|---|
| how many SUT calls are discarded / consumed? | `argus.detectors.provenance_scan.provenance_evidence(...)` | re-walk the AST for it |
| is this callee an assertion? | `argus.detectors.vacuous_vocabulary.is_assertion_callee` (**the WIDE table**) | use `_CORROBORATION_ASSERTION_CALLEES` |
| does this line open a bare `assert`? | `argus.detectors.provenance_scan.opens_bare_assert` | write a second line scanner |
| how do source lines align to the index? | `argus.detectors.vacuous_test.index_aligned_lines` | `str.splitlines()` |

⛔ **The WIDE vocabulary, never the FROZEN one — `DN-14-2-1`.** Routing *"does this test assert
anything at all?"* through the 23-name corroboration table would score a test that asserts through a
widened callee as assertion-free, manufacturing exactly the false accusation the two-table split
exists to prevent. `research/investigate-per-call-scoping.py` says so in its own docstring; the
shipped derivation must say so in its own.

⛔ **`_CORROBORATION_ASSERTION_CALLEES` stays byte-unchanged at 23 and `_ASSERTION_CALLEES` at 89.**
If the derivation appears to need either moved, **STOP — that is an AC9.4 escalation.**

### §2.2 ⛔ The predicate must be UNREACHABLE from the detector path

A new predicate in `argus/**` that scores test functions is one careless import away from becoming a
shipped promotion. So:

- `argus/detectors/**` is **byte-unchanged** (AC2.2), and
- **no module under `argus/detectors/**` and no `argus/precision/gate_*.py` imports the new module** —
  asserted by an `ast` walk of the import graph, in the direction that matters (AC2.3). The new
  module imports *them*; nothing imports *it* except its own test and its own script.

That is the same structural argument `gate_seal.py` and `gate_yield.py` already make about
themselves (`TC-ArgusAgent-PRECISION-001-87` / `-99`) — reuse the shape.

### §2.3 ⛔ Guard vacuity — this project's signature defect, and this story's specific version

This project shipped **4 of 35 unreal guards in Epic 14**; 16.3's own mutation run caught one of its
own; 16.6 expected to find one and did. The **GUARD-ADEQUACY CLAUSE** (`architecture.md`
§Enforcement) applies in all three parts, discharged **in each guard's own docstring**: (i) name the
**observable**; (ii) demonstrate the defect **moves** it — RED **at the real seam**, against a real
`build_ast_index` and the real `provenance_evidence`, not a reconstruction; (iii) at least one
adversarial variant **generated** from a table or population the guard closes over, with its count
asserted.

⛔ **THE LOCKSTEP TRAP, in this story's specific shape, and it has fired five times in this epic.**
A fixture whose silence changes because you **added or removed a line** is a fixture in which the
numerator *and* the denominator moved — the case then measures the fixture, not the predicate.
⛔ **Vary ONE coordinate with the others PINNED:** score the *same* fixture text under the shipped
wide table and under a table with the assertion callee removed, or pair every case with a control
whose `statement_count` and `discarded_sut_calls` are asserted **equal**.

⛔ **The non-vacuity floor is mandatory and is checked FIRST** (`AI-E11-1`): every case asserts its
population is non-empty and its seam reachable — the index really emitted the edges the case is
about, `disc ≥ 1`, `statement_count > 0` — **before** asserting anything about it. A derivation that
returns an empty class passes a "nothing was promoted" guard forever.

⛔ **Run every mutation with `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared** — 16.2 recorded
a false RED from a stale cache, and **§0.0 records this session hitting the identical thing today.**

### §2.4 ⛔ Encoding, paths and subprocess — the POSIX/Windows asymmetry, with an OPEN ledger entry

`DF-16-6-F` is OPEN for precisely this bug in a sibling guard: `tests/test_gate_seal.py::_git` calls
`subprocess.run(..., text=True)` with no `encoding=`, so it decodes with the **locale** codec
(cp1252 here) and crashes on a non-cp1252 byte — **Windows-only, invisible to the ubuntu CI leg.**

This story's builder shells out to git over five repositories of third-party source. **Do not
reproduce the bug:**

- `scripts/pinned_corpus_snapshot.py::_git` is the **correct shape** — `capture_output=True`,
  **no `text=True`**, bytes decoded explicitly. **Reuse it rather than rolling a sixth `_git`.**
- Every `open()` / `read_text()` / `write_text()` in the new code names `encoding="utf-8"`, and every
  artifact write uses `newline="\n"` (the treatment `build_adjudication_record.py` already gives
  `_RECORD.write_text`).
- Every path in every artifact is **repo-relative POSIX**. `LOCATOR_RE` already refuses a drive
  letter, a leading `/`, a `..` segment and a backslash — **let it**, and assert it does.
- The checkout root arrives as a **CLI argument** (`--checkout-root` / `--map`, the
  `audit_validation_corpus.py` shape). ⛔ **No absolute host path is hardcoded, and none reaches any
  committed artifact** (NFR-S1). The `research/*.py` harnesses hardcode `D:/ProjectX/...` — they are
  research scratch and are **not** the model for a shipped script.
- ⛔ **`os.sep`, `os.path.join` and `\\` do not appear in any locator-building code path.** Assert it.

### §2.5 ⛔ The commit ordering is FORCED, and it is four commits

`scripts/regenerate_dogfood_artifacts.py` **refuses a dirty `argus/` tree** (exit 2) because the
artifacts cite `git rev-parse HEAD` as provenance. And a commit cannot cite itself. So:

`chore` (story file + `in-progress`) → `feat` (`argus/` + `scripts/` + `tests/`) →
`chore` (regenerate the three dogfood artifacts) → `docs` (the two new artifacts, the ledger append,
this story's record).

**That is 16.6's own arc with the bracketed regeneration step re-armed** (`6304552`). AC9.2.

---

## §3 — AC ↔ TASK MAP

⛔ **Every AC below is discharged by at least one named task, and every task names the AC it
discharges. This table exists because Stories 16.5 and 16.6 both failed validation on ACs whose
executable twin in the task list had drifted. CHECK IT rather than trusting it.**

⚠️ **THE FIRST DRAFT OF THIS TABLE WAS ITSELF WRONG, AND IT IS RECORDED RATHER THAN QUIETLY FIXED.**
Self-auditing it against the task list found **nine** mis-citations and **one AC with no task at
all** (AC2.1/AC2.3's import-graph guard — which is why Task 4.7 exists). That is the identical shape
16.6's amendment recorded: *"an AC repaired on one side of the file while its executable twin kept
the defect."* ⛔ **It fired again, in the very table built to catch it. Re-check it; do not trust it.**

| AC | Discharged by | AC | Discharged by |
|---|---|---|---|
| AC1.1 | Task 0.3 · 3.2 · 5.1 | AC6.1 | Task 2.4 · 4.4 |
| AC1.2 | Task 3.2 · 5.1 | AC6.2 | Task 2.4 · 4.5 |
| AC1.3 | Task 0.5 · 5.1 | AC7.1 | Task 6.2 · 6.3 · 6.4 |
| AC1.4 | Task 2.2 · 3.7 · 5.1 | AC7.2 | Task 6.1 · 6.2 · 6.3 · 6.4 |
| AC1.5 | Task 0.10 · 5.1 | AC7.3 | **binds Task 4.2 – 4.7** |
| AC2.1 | Task 2.1 · **4.7** | AC7.4 | Task 6.5 |
| AC2.2 | Task 2.5 · 9.3 | AC8.1 | Task 0.1 · 1.1 · 1.2 · 9.3 · 9.4 |
| AC2.3 | Task 3.5 · **4.7** | AC8.2 | Task 8.1 · 9.1 |
| AC3.1 | Task 3.4 · 3.7 · 4.1 | AC8.3 | Task 0.4 · 3.3 · 5.4 |
| AC3.2 | Task 5.2 · 8.1 · 9.3 | AC8.4 | Task 3.3 · 6.6 |
| AC3.3 | Task 2.2 · 4.2 | AC8.5 | Task 8.2 · 8.3 · 8.4 |
| AC3.4 | Task 0.6 · 0.7 · 2.5 · 9.3 | AC8.6 | Task 3.7 |
| AC4.1 | Task 3.6 · 4.6 · 7.1 | AC8.7 | Task 1.3 · 9.1 |
| AC4.2 | Task 3.7 · 7.1 | AC9.1 | Task 0.2 · 9.1 |
| AC4.3 | Task 2.3 · 4.6 | AC9.2 | Task 9.2 |
| AC4.4 | Task 7.2 | AC9.3 | Task 9.3 |
| AC4.5 | Task 3.6 · 7.3 · 9.5 | AC9.4 | Task 7.2 · 9.4 |
| AC5.1 | Task 2.3 · 4.3 | AC9.5 | Task 9.5 |
| AC5.2 | Task 2.3 · 4.3 | | |
| AC5.3 | Task 2.4 · 5.3 | | |

---

## Acceptance Criteria

### AC1 — THE CLASS IS RE-DERIVED AT HEAD AND ITS EXACT MEMBERSHIP RECORDED

**Given** Story 16.6 changed what counts as an assertion
**When** the silent class is derived
**Then** it is derived **at HEAD, after 16.6** — never carried over from the change proposal — and
its exact membership is published.

- **AC1.1** — the class is **36** members, **`agent-smith` 22 + `minions` 14**, and
  `agent-markovich` / `xagents-webapp` / `ai-body-runtime` contribute **0**.
- **AC1.2** — derived over the **1,032** `vacuous_test_heuristic` findings of the committed
  `validation-corpus/adjudication-set-13-5.json`, with **0 skipped and 0 unresolvable**, and the
  non-vacuity of that population asserted **before** anything is asserted about it (`AI-E11-1`).
- **AC1.3** — the **39 → 36** delta is reproduced by executing the derivation a second time with
  `"AssertionError"` absent from the wide table, and **the three findings 16.6 removed are NAMED**
  (§0.1's table reproduced or corrected).
- **AC1.4** — every member is published with `member_id`, a **repo-relative POSIX** locator, the
  test function name, and its measured `discarded_sut_calls` / `consumed_sut_calls`.
- **AC1.5** — ⛔ **if a re-derived figure disagrees with §0.1, §0.2, §0.4, §0.6 or §0.8, THE TREE
  WINS and this story file is corrected** — recording what disagreed and why. **Never adjust the
  derivation to hit a number.**

### AC2 — THE DERIVATION IS COMPOSED FROM THE SHIPPED PREDICATE, AND CANNOT REACH THE DETECTOR

**Given** `AR7` forbids a second vocabulary and `DN-14-2-1` forbids routing this question through the
frozen table
**Then** the derivation composes shipped components and is structurally unreachable from the
detector path.

- **AC2.1** — `provenance_evidence`, `is_assertion_callee` (the **WIDE** table),
  `opens_bare_assert`, `index_aligned_lines` and `build_ast_index` are **called**, not
  re-implemented. ⛔ **No second AST walk computes discarded/consumed counts, and no second line
  scanner decides "is this an assert line".** Asserted by an `ast` walk of the new module's own
  source: it contains **no** `ast.walk`-based SUT-call counter and **no** assertion-name regex.
- **AC2.2** — ⛔ **`argus/detectors/**` is BYTE-UNCHANGED**, including
  `_ASSERTION_CALLEES` at **89**, `_CORROBORATION_ASSERTION_CALLEES` at **23**,
  `_ASSERTION_NAMING_CONVENTION`, `_MOCK_CALLEES` at **10**, `ASSERTION_DENSITY_FLOOR` and
  `MOCK_RATIO_CEILING`. Asserted by `git diff --stat` over `argus/detectors/` being **empty** and by
  importing the constants and checking them.
- **AC2.3** — ⛔ **NOTHING imports the new module except its own test and its own script.** Asserted
  by an `ast` walk over `argus/**`: no module under `argus/detectors/**`, and none of
  `argus/precision/gate_*.py`, `argus/precision/adjudication.py`, `argus/precision/replay_harness.py`
  or `argus/precision/__init__.py`, names it — directly or transitively. **The edge runs one way.**

### AC3 — THE DISPOSITIONS LIVE IN THEIR OWN ARTIFACTS, AND THE GATE'S RECORD DOES NOT MOVE

**Given** §0.3 measured that appending these rows to `adjudication-record.json` takes
`total_tp` **0 → 36**, `adjudicated_population` **31 → 67** and `independence.status`
**`NOT_INDEPENDENT` → `SECOND_REVIEWER_INTERNAL`**
**Then** they are written to NEW artifacts, and the committed record is byte-unchanged.

- **AC3.1** — two NEW artifacts are created under
  `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/`: a **machine record** (JSON,
  serialized **through `argus.store.canonical`** — never `json.dumps`) and a **human worklist**
  (Markdown, DERIVED from the record, not hand-written), following
  `blocking-worklist-13-5.md`'s own precedent and its *"Do not hand-edit: re-run the script"* header.
- **AC3.2** — ⛔ **`validation-corpus/adjudication-record.json`,
  `validation-corpus/adjudication-set.json`, `validation-corpus/adjudication-set-13-5.json` and
  `validation-corpus/gate-decision-record.json` are BYTE-UNCHANGED**, and **both existing builders
  exit 0 under `--check`** at the end.
- **AC3.3** — the new record's row type **REUSES the existing vocabulary**: `DISPOSITIONS`,
  `HUMAN_DISPOSITIONS`, `PROTOCOL_ADJUDICATOR_ROLES`, `adjudicator_role`, `LOCATOR_RE` and
  `finding_row_id` are **imported from `argus.precision.adjudication`**, never re-declared. An
  unregistered disposition RAISES; an unregistered adjudicator role RAISES; a non-human disposition
  carrying an adjudicator RAISES — all at **construction**, and each asserted by a case that
  observes the raise.
- **AC3.4** — ⛔ **`argus/precision/adjudication.py` is BYTE-UNCHANGED.** In particular `ROW_FIELDS`
  stays at **eleven** members and `DISPOSITIONS` at **four**. §0.3 measured that widening
  `ROW_FIELDS` makes `load_record()` on the committed record raise outright. If the design appears
  to need either widened, **STOP — AC9.4 escalation.**

### AC4 — THE JUDGEMENT IS THE NAMED HUMAN'S ACT, AND THE STORY STOPS AT THE HANDOFF

**Given** protocol §2: *"`UNADJUDICATED` is the ONLY member an automated producer may write"*, and
*"an autonomous story that tags its own findings TP has measured nothing"*
**Then** the dev builds the instrument, publishes the worklist, and **HALTS**.

- **AC4.1** — the machine seeds **exactly one `UNADJUDICATED` row per class member — 36 rows**, each
  carrying **no adjudicator and no date**, and each with a distinct `finding_id`.
- **AC4.2** — the worklist gives the human what they need to judge **without opening five
  repositories**: per row, the member, the locator, the test name, the pinned sha, the measured
  `disc`/`cons`, and the test's **source span** rendered from the **pinned blob**.
  ⛔ **NFR-S1: no absolute host path, no secret value.** ⚠️ Source text from a corpus member appearing
  in a committed artifact is a deliberate, bounded exception with its own carve-out — **see AC8.6,
  which decides it. Read AC8.6 before writing this artifact.**
- **AC4.3** — the record admits **`TP`, `FP` and `BORDERLINE`** as live outcomes, with `BORDERLINE`
  a **first-class recorded outcome** (*looked at, could not decide*) that makes the run
  **non-exhaustive** and enters **neither** side of any ratio — reusing
  `AdjudicationRecord.exhaustiveness()`'s own semantics, never a second definition.
- **AC4.4** — ⛔ **if protocol §4's ladder reaches the UNFILLED External adjudicator, the story
  STOPS and reports WHICH ROWS and WHY.** It is never resolved by a default, a majority, or the
  dev's own reading. ⚠️ **A `BORDERLINE` alone is NOT the ladder's third step** (§0.4): step 3 is
  reached only on **persistent disagreement between the two filled roles**.
- **AC4.5** — ⛔ **NO automated step writes a `TP`, `FP` or `BORDERLINE`.** Not one. If the operator
  supplies judgements in-session they are **TRANSCRIBED verbatim**, the record states that they were
  transcribed and from whom, and no row is inferred, completed or defaulted.
  ⛔ **REACHING THIS HALT WITH THE INSTRUMENT BUILT AND THE WORKLIST PUBLISHED IS THIS STORY
  SUCCEEDING** (`DN-16-7-3`; the 13.2 / AC7 and 16.4 / AC1.4 precedent). **It is not a failure and
  must not be reported as one.**

### AC5 — THE SMOKE TEST IS ITS OWN RECORDED OUTCOME, NOT A SILENT FP

**Given** the story exists to learn the smoke-test **proportion**
**Then** the idiom is recorded on an axis **orthogonal** to the disposition, so it can never be
folded into FP without comment.

- **AC5.1** — each row carries an `idiom` field over a **CLOSED, registered vocabulary** whose
  members mean *at least*: **deliberate smoke test** (*"does not raise" IS the assertion*), **not a
  smoke test**, and **not assessed**. An unregistered member **RAISES** (`DF-10-4-E`), and the
  vocabulary is checked in **both directions** — a member no case exercises is itself a finding
  (`TC-ArgusAgent-PRECISION-001-38`'s shape).
- **AC5.2** — ⛔ **`idiom` is NOT a disposition and NOT a fifth member of `DISPOSITIONS`**
  (`DN-16-7-2`, §0.3). A row may be `FP` **and** a deliberate smoke test; that combination is the
  measurement the story exists to produce, and it must be representable.
- **AC5.3** — the record **derives and publishes the proportion** — smoke tests as an exact
  `Fraction` of the assessed rows (`AR4`, never a float) — and the derivation refuses an
  **unassessed** denominator rather than reporting a proportion over rows nobody looked at.
  ⛔ **The `cmt` column of §0.1 is triage colour, not an assessment**: it may not seed, default or
  order this field (`DN-16-7-5`).

### AC6 — HOURS AND INDEPENDENCE ARE REPORTS, DERIVED THROUGH THE EXISTING SURFACES

- **AC6.1** — actual `expert_hours` are recorded as an **exact `Fraction`** (`AR4`) and compared
  against §3's ≤ 4-hour ceiling **by the EXISTING
  `argus.precision.adjudication.expert_hours_report()`** — ⛔ **a report, never a gate. No caller
  branches a pass/fail on it.** `None` means **NOT RECORDED**, never zero. ⛔ **Never trim the
  adjudication to fit the estimate**; an overrun and **what made it expensive** are recorded.
- **AC6.2** — independence for **this** population is **DERIVED** — never typed — by the **EXISTING
  `argus.precision.gate_independence.assess_independence`** over the `"<who> (<role>)"` ids that
  authored **this record's** live rows, and is published on the record **beside its own figure** so
  the two cannot be separated. ⛔ **It EXTENDS FR34's existing disclosure mechanism rather than
  forking a second one**, it **gates nothing**, it **claims no independence**, it **fills no role**,
  and ⛔ **it is NOT written to `gate-decision-record.json`** — that record's `independence` block is
  a claim about the **gate's** adjudication and stays `NOT_INDEPENDENT` (AC3.2). With zero live
  human rows the derived status is **`NOT_ESTABLISHED`**, which is the honest output and not a
  failure.

### AC7 — GUARDS THAT CANNOT BE VACUOUS

**Given** a guard that cannot fail proves nothing, and this project has shipped 4 of 35 unreal ones
**Then** every new guard is driven **RED by executed mutation at the real seam**, with the tree
restored byte-exact.

- **AC7.1** — ⛔ **at least three distinct mutations, each observed RED, each restored**, with the
  exact failure text recorded. **They must include:** (i) remove `"AssertionError"` from the wide
  table — the class must move **36 → 39**; (ii) route the silence question through
  `_CORROBORATION_ASSERTION_CALLEES` instead of the wide table — the class must **change**, which is
  the false accusation `DN-14-2-1` exists to prevent, made executable; (iii) drop the `disc ≥ 1`
  conjunct — the class must grow toward §0.2's **45** silent-of-any-`disc` figure. **RED at the real
  seam** — a real `build_ast_index` and the real `provenance_evidence`, never a reconstruction.
- **AC7.2** — ⛔ **the restoration test is INVARIANCE over THIS repository, not emptiness.** By
  Task 6 the tree necessarily carries the new modules, this story file, `sprint-status.yaml` and the
  new artifacts, so `git status --porcelain` **can never be empty** and a check demanding it fails
  for a reason nobody can fix — the Story 16.5 defect class. **Capture `git status --porcelain`
  immediately BEFORE each mutation and assert it byte-identical after the restoration.** That is
  strictly stronger than emptiness: it also catches a stray `__pycache__`, backup or `.orig` file.
- **AC7.3** — ⛔ **non-vacuity FIRST, in the `-133` shape** (`AI-E11-1`): every case asserts the
  index emitted the edges it is about, `disc ≥ 1`, and `statement_count > 0`, **before** asserting
  anything else — and each carries a **control** with `statement_count` and `discarded_sut_calls`
  asserted **equal**, so the case isolates the PREDICATE from the fixture's SHAPE (§2.3's lockstep
  trap).
- **AC7.4** — at least one adversarial variant is **GENERATED** from a table or population the guard
  closes over — not hand-listed — with its **count asserted**, per the guard-adequacy clause's third
  part.

### AC8 — SCOPE, PATHS, PORTABILITY, CEILINGS AND THE LEDGER

- **AC8.1** — ⛔ **The write set is exactly:**
  **NEW** `argus/precision/silent_class.py` ·
  **NEW** `scripts/build_silent_class_record.py` ·
  **NEW** `tests/test_silent_class.py` ·
  **NEW** `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/<the record>.json` ·
  **NEW** `_bmad-output/design-artifacts/ArgusAgent/validation-corpus/<the worklist>.md` ·
  `tests/test_release_preflight.py` (**one registry entry + its prose comment, §0.6 — the
  `gate_independence.py` precedent, nothing else in the file**) ·
  the three committed dogfood artifacts (**regenerated by their own renderer only, §2.5**) ·
  `_bmad-output/design-artifacts/ArgusAgent/deferred-work.md` (append `DF-16-7-B`) ·
  this story file · `sprint-status.yaml`.
  **Everything else is byte-unchanged**, in particular `argus/detectors/**`,
  `argus/precision/adjudication.py`, `argus/precision/gate_*.py`, `argus/precision/replay_harness.py`,
  `argus/precision/__init__.py`, `scripts/audit_validation_corpus.py`,
  `scripts/pinned_corpus_snapshot.py`, `scripts/build_adjudication_record.py`,
  `scripts/build_gate_decision.py`, `tests/test_gate_*.py`, `tests/test_vacuous_*.py`,
  `tests/test_status_document_registry.py`, `precision-validation-protocol.md`, `epics.md`,
  `pyproject.toml`.
- **AC8.2** — ⛔ **NOTHING ON THE GATE'S DECISION PATH MOVES.** `SECTION_5_CONDITIONS` stays at
  **SEVEN** and `precision_evaluable` keeps exactly **four** conjuncts; `VALIDATION_SET_FLOOR_N`
  stays **5**; `PRECISION_GATE_THRESHOLD` stays `Fraction(4, 5)`; `MANIFEST_FIELDS` stays **9**;
  `N` stays **5**; `protocol_cleared` stays **`False`**; the seal stays closed; the gate outcome
  stays **`BLOCKED`**; the protocol change-log head stays **V1.3** with **no `V1.4` row**;
  `DF-13-5-A` stays **OPEN and UNSPENT**. ⛔ **Discharged by running the EXISTING
  `tests/test_gate_*.py` (all nine) and both builders under `--check` — this story writes NO new
  assertion about `argus/precision/gate_*.py` and imports nothing from `gate_decision` into
  `tests/test_silent_class.py`.** Forking a guard that already exists is the **AR7** defect.
  ⚠️ **The ONE exception is `assess_independence`** (AC6.2), which is *called*, not asserted about.
- **AC8.3** — ⛔ **the derivation WRITES NOTHING to any corpus member**, proved the two ways
  `DN-16-7-4` names: (i) every member read goes through the shipped **content-addressed**
  `pinned_tree` / `materialize_pinned_bytes` / `verify_pinned_bytes`, with the materialised bytes
  **proved against the pin by blob hash**; and (ii) the harness's git command vocabulary is a
  **named read-only allow-list**, asserted by execution, from which `checkout`, `stash`, `clean`,
  `reset`, `worktree`, `add`, `commit`, `fetch` and `pull` are **absent**.
  ⛔ **The members' `git status --porcelain` is CAPTURED and REPORTED, never asserted** — §0.7
  measured `minions` changing under this session by another party's hand, so both *emptiness* and
  *invariance* are checks nobody can satisfy. A difference is recorded in Completion Notes.
- **AC8.4** — ⛔ **POSIX PORTABILITY IS A CRITERION, NOT A HOPE** (`AI-E13-1`, `DF-16-6-F`): every
  subprocess call decodes **explicitly** — no bare `text=True` — and reuses
  `scripts/pinned_corpus_snapshot.py::_git` rather than adding a sixth `_git`; every file read and
  write names `encoding="utf-8"` and every artifact write `newline="\n"`; every locator in every
  artifact is **repo-relative POSIX** and passes `LOCATOR_RE`, asserted over all 36; ⛔ **`os.sep`,
  `os.path.join` and a literal backslash appear nowhere on a locator-building path**, asserted by an
  `ast`/source scan of the new modules; the checkout root arrives as a **CLI argument** and ⛔ **no
  absolute host path is hardcoded or reaches any committed artifact** (NFR-S1).
- **AC8.5** — **`DF-16-7-B`** is appended to `deferred-work.md`, recording (a) `DF-16-7-A`'s V5
  figure re-measured **122 → 125** at HEAD with the cause, and (b) that the class's TP proportion is
  **not yet measured** until the human act completes, with severity, owner and target story.
  ⛔ **Append-only: no historical entry is edited and no other `DF-*` is created or disposed of** —
  in particular `DF-16-7-A`, `DF-16-6-A`…`DF-16-6-F`, `DF-16-5-A`/`-B`, `DF-16-1-A`, `DF-15-2-E`,
  `DF-14-1-A` and `DF-13-5-A` are left exactly as they stand.
  ⛔ **APPEND IN BINARY AND VERIFY THE BYTES (`DF-16-6-C`).** Assert the count of **lone `CR`** bytes
  is still exactly **1**, that `CRLF` pairs stay at **0**, that the file still ends with a newline,
  and that `git diff --numstat` reports **`+n / -0`**. A one-line deletion here is an append-only
  violation and it has happened before (`9aea1be` → `a4de7e7`). ⛔ **Do not add `.gitattributes`** —
  that is `DF-16-6-C`'s proposed remedy and it is repo-wide.
- **AC8.6** — ⛔ **THE SOURCE-SPAN CARVE-OUT, decided here so it is not decided by accident.**
  NFR-S1 forbids *"no source byte, no secret value, no absolute host path in any artifact"*. The
  worklist needs the span for the human to judge at all. **The bounded exception:** spans appear
  **only in the Markdown worklist**, never in the JSON record; each is read from the **pinned blob**
  and is bounded to the flagged test function; **no span is copied into `deferred-work.md`, into
  this story file, or into any commit message**; and the worklist carries a header stating the
  carve-out and its bound. ⛔ **If a member's span carries anything that looks like a credential,
  the row's span is REDACTED and the redaction is recorded** — reuse the shipped
  hardcoded-secret redaction rather than a second one. ⛔ **If the dev judges this exception
  unacceptable, that is an AC9.4 escalation, not a silent narrowing** — publish locators only and
  say so.
- **AC8.7** — every new module ends **≤ 1,200** physical lines with `tests/test_module_size_ceiling.py`
  green; ⛔ **`tests/test_vacuous_density.py` stays at 1,159 and never crosses `DF-15-2-E`'s 1,180
  trigger**; ⛔ **no `_EXEMPT_BY_DESIGN` entry is added** — `MAINT-001-04` lets that registry
  **shrink only**, and the remedy is a cohesion split, never a shave and never an exemption.

### AC9 — GATES AND HAND-OFF

- **AC9.1** — all of §0.0's gates green at the end, at **or above** their baseline numbers: the full
  suite with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` (**≥ 1,695 passed, 0 failed**), coverage
  `--cov-fail-under=80` (**baseline 95.55%**), `mypy argus` (**CI scope**, 94 files, clean),
  `bandit -r argus --severity-level medium` (**no issues**), `tests/test_module_size_ceiling.py`,
  `tests/test_gate_*.py` (all nine, **58 passed** at baseline — AC8.2's whole discharge),
  `tests/test_release_preflight.py`, `tests/test_dogfood_artifact_currency.py`,
  `tests/test_governance_record_integrity.py`, and **both builders under `--check` at exit 0**.
  **Record every exit code.** ⛔ **Run with `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` cleared**
  (§0.0).
- **AC9.2** — the commit arc is **four** commits, in this order and for §2.5's forced reason:
  **`chore`** (story file + `in-progress`) → **`feat`** (`argus/` + `scripts/` + `tests/` + the
  preflight registry entry) → **`chore`** (regenerate the three dogfood artifacts, by their own
  renderer, on a clean `argus/` tree) → **`docs`** (the two new artifacts, `DF-16-7-B`, this story's
  record). ⛔ **A commit cannot cite itself**, and the regeneration script refuses a dirty `argus/`.
- **AC9.3** — the final write set equals AC8.1 exactly. ⛔ **Verify with `git status --porcelain`,
  NOT `git diff --name-only`** — three of this story's deliverables are **NEW untracked** files that
  `git diff` cannot see, so that check would pass while blind to the story's main output.
- **AC9.4** — ⛔ **ESCALATE, do not decide, if:** a finding must become verdict-eligible · or a
  threshold must move · or `ROW_FIELDS` / `DISPOSITIONS` must widen · or
  `_CORROBORATION_ASSERTION_CALLEES` / `_ASSERTION_CALLEES` must move · or an eighth §5 condition ·
  or `adjudication-record.json` / `gate-decision-record.json` must be regenerated · or a `V1.4`
  protocol row · or `DF-15-2-E`'s 1,180 line must be crossed · or Story 16.4's **HALT-2** must be
  answered · or AC8.6's carve-out is judged unacceptable · or any `DN-*` reopened.
  **A `DN-*` you disagree with is an escalation, not a story decision.**
- **AC9.5** — Completion Notes record: the re-derived §0.1/§0.2/§0.4/§0.6/§0.8 figures; the three
  observed mutation REDs with their exact failure text and restoration proof; the corpus porcelain
  captures **as an observation**; every gate exit code; **the HALT, stated plainly, with exactly
  what the named human must do and where the worklist is**; and **any premise in §0 found false**.

---

## Dev Notes

### Decisions this story TAKES, each with its rejected alternative

**`DN-16-7-1` — the dispositions go in NEW artifacts; `adjudication-record.json` is byte-unchanged.**
*Rejected: append them to the committed adjudication record.* Measured (§0.3): `total_tp` 0 → 36,
`adjudicated_population` 31 → 67, `distinct_rule_class_count` 1 → 2, and `independence.status`
flips `NOT_INDEPENDENT` → `SECOND_REVIEWER_INTERNAL`. Two of those are forbidden outright by this
story's charter, and the whole move is wrong on the protocol's own terms: all 1,032 findings are
**advisory**, and protocol §4, `build_adjudication_record.py` and `blocking-worklist-13-5.md` each
say independently that advisory findings are not false accusations and are not in the denominator.
*Also rejected: write them to a second `AdjudicationRecord` at a new path.* `to_payload()` hardcodes
`story = "13-2-adjudicate-every-finding-by-a-named-human"` (measured), so the artifact would
publish a false subject — the `DF-9-2-B` false-subject class this project files rather than
tolerates. *Also rejected: parameterise `_STORY`.* It touches the module the gate reads to buy a
default that must stay byte-identical anyway; the cost/benefit is inverted.
⛔ **This does not answer Story 16.4's HALT-2**, which concerns a **blocking** population and stays
moot and unanswered.

**`DN-16-7-2` — the smoke-test outcome is an ORTHOGONAL FIELD, never a fifth disposition.**
*Rejected: add `SMOKE_TEST` to `DISPOSITIONS`.* The vocabulary is CLOSED and checked in both
directions by `TC-ArgusAgent-PRECISION-001-38`; the gate record republishes it; and it would make
*"is this a false accusation?"* and *"is this idiom deliberate?"* one axis when they are two — a row
can be a genuine FP **and** a deliberate smoke test, and that combination is the measurement.
*Rejected: add `idiom` to `ROW_FIELDS`.* Measured: `load_record()` on the committed record raises
`missing=['idiom']` immediately. The field lives on a NEW row type that **imports** the shared
vocabulary, which is what `AR7` actually protects — the vocabulary and the arithmetic, not the
container.

**`DN-16-7-3` — the story is TWO halves and the second is an OPERATOR ACT; the halt is success.**
*Rejected: have the dev agent author the 36 judgements.* Protocol §2 forbids it in terms —
*"`UNADJUDICATED` is the ONLY member an automated producer may write"* — and *"an autonomous story
that tags its own findings TP has measured nothing and has produced the exact artifact Epic 13
exists to make impossible."* *Rejected: shrink the story to the instrument and drop the measurement
from the charter.* That would quietly delete the epic's stated purpose. The story keeps the full
charter and makes the human half **reachable**: a complete worklist, a seeded record, a stated
question and a halt. Precedent: Story 13.2 (*"delivered the instrument … and escalated AC7"*, still
the live `expert_hours_note`) and Story 16.4 (*"CLOSED BY DECISION, not by result"*, whose AC1.4
records that reaching the halt and reporting **is** the story succeeding).

**`DN-16-7-4` — containment is proved about THIS STORY'S ACTIONS, not the member's state.**
*Rejected: assert the members' porcelain is EMPTY.* Unsatisfiable — three of five are dirty and none
of it is this story's business; cleaning one would mutate a ratified member. *Rejected: assert it is
INVARIANT before/after (Story 16.6's AC4.5).* ⛔ **Measured to fail here**: `minions` went 7 → 1 under
this session by another party's edits (§0.7). Inheriting it would ship the Story 16.5 defect class a
third time. *Selected:* content-addressed reads proved against the pin by blob hash, plus an
asserted read-only git command allow-list. Both are satisfiable, both are about this story, and
together they are **strictly stronger** than either rejected check — they prove the measurement
could not have been tainted *and* that nothing could have been written.

**`DN-16-7-5` — the `cmt` column is TRIAGE COLOUR and may not become a judgement.**
18 of 36 spans contain a `#`. That is a fact about punctuation, not about intent. *Rejected: seed
`idiom` from it, or order the worklist by it.* Either would anchor the human on a signal with no
established relationship to the question — manufacturing the appearance of a measurement, in the one
measurement this story exists to make honestly. It is published as context and asserted nowhere.

**`DN-16-7-6` — the pure half lives in `argus/precision/`, the I/O half in `scripts/`.**
*Rejected: put everything in `scripts/`.* `AR8` separates pure from impure, and the silence
predicate and the record container are pure. *Rejected: put it in `argus/detectors/`.* §2.2 — a
scoring predicate in the detector package is one import from becoming a shipped promotion.
*Rejected: put it in `tests/`.* `DF-9-2-A`: `tests/` is absent from the built distribution, and the
`scripts/` builder would then import from a tree the wheel does not ship. *Selected:*
`argus/precision/silent_class.py`, mirroring exactly what Story 16.5 did with `gate_independence.py`
— including the `TC-ArgusAgent-RELEASE-001-11` registration comment, which §0.6 measured will be
required.

### Locked decisions this story CITES rather than reopens

- **`DN-14-2-1`** — two assertion vocabularies, two questions; the frozen table is the moat. ⛔ **The
  single most load-bearing constraint here** (§2.1), and AC7.1's second mutation makes it executable.
- **`DN-3`** — one floor, resolved from the cartridge registry, never re-typed; `pytest.raises` is
  the **explicit** result-observing carve-out. The smoke test is the **implicit** one, and this story
  measures rather than carves it.
- **`DN-4`** — fact (b) depends on no assertion COUNT and no threshold.
- **`DN-2a` / `DN-MATCH-KEY-REUSE`** — the unit is the **FINDING**, and the finding identity is
  `(member_id, rule_id, verdict_eligible, advisory, locator)`. **Reuse `finding_row_id`.**
- **`DN-6`** — attributing an unadjudicated row to a human is the fabrication the record exists to
  make impossible.
- **`DN-14-3-5`** — a name is admitted on a MEASURED benefit/cost ratio. Not exercised here; cited so
  nobody widens a table in passing.
- **`DN-15-2-*`** — the detector's line decomposition IS the index's (`index_aligned_lines`).
- **`DN-16-2-4`** — `pre-seal` is a distinct partition; an exclusion is never read as an assignment.
- **`DN-16-3-3`** — the yield subject is `adjudicated_population`. §0.3 is why that matters here.
- **§3.4** — amend by dated block; **strike, never erase**; the ledger is append-only.
- **§6 R2** — ratification, third-party fetch and role-filling are **operator acts**.

### Open ledger entries bearing on this story — verify against `deferred-work.md` on disk

| id | State | Bearing |
|---|---|---|
| `DF-13-5-A` | **OPEN, UNSPENT** | Untouched. Its re-review trigger is *16.6 + 16.7 done, or 2026-11-22*. ⛔ **This story does not spend it and does not propose expansion.** |
| `DF-16-7-A` | **OPEN** | Its V5 figure of **122** is now **125** at HEAD (§0.2). ⛔ **Recorded in a NEW entry, never by editing this one.** Target story stays **6.2**. |
| `DF-16-6-A` | **OPEN** | Fact (b)'s mock-referencing clause dead over the corpus. Untouched — disposing of it promotes 6. |
| `DF-16-6-B` | **OPEN** | The bare-`raise` residual, 0 of 1,032. Untouched. |
| `DF-16-6-C` | **OPEN** | `deferred-work.md` is protected from CRLF normalisation by ONE lone `CR`. ⛔ **Read AC8.5's byte checks before Task 8.** |
| `DF-16-6-D` | **OPEN** | The line-scoped closure-claim trap. ⛔ **It made 16.6's own baseline RED.** §0.0's second writing rule is the interim remedy. |
| `DF-16-6-E` | **OPEN** (filed 2026-08-23, **uncommitted at contexting**) | `SEAL_CITATION_VALUES` has no `pre-seal` member. Bears on this story's **commit trailers** if the seal-citation predicate is exercised — do not widen the vocabulary. |
| `DF-16-6-F` | **OPEN** (filed 2026-08-23, **uncommitted at contexting**) | ⛔ **The cp1252 `text=True` decode bug. THIS STORY'S BUILDER IS THE SAME SHAPE.** AC8.4 exists because of it. Do not fix it here; do not reproduce it either. |
| `DF-16-5-A` | **OPEN** | `argus/precision/gate_decision.py` 1,132/1,200. ⛔ **Put nothing there.** |
| `DF-16-5-B` | **OPEN** | `tests/test_gate_independence.py` 1,127/1,200. ⛔ Same. |
| `DF-15-2-E` | **OPEN, trigger NOT fired** | `tests/test_vacuous_density.py` 1,159/1,200, trigger 1,180. Byte-unchanged here. |
| `DF-16-1-A` | **OPEN, unlanded** | Rule-class arm of §5 breadth. ⚠️ §0.3 measured that a bad write would take `distinct_rule_class_count` 1 → 2 — **the arm is unlanded, so it does not gate, and that is not a licence.** |
| `DF-14-1-A` | **OPEN** | Fact (b) is a NAME-level proxy, not dataflow. Target story 6.2. Untouched. |
| `DF-12-1-A/B/C` | **OPEN** | The three `_EXEMPT_BY_DESIGN` entries. ⛔ **`MAINT-001-04`: that registry shrinks only.** |
| `DF-9-2-A` | standing | `tests/` is absent from the built distribution. Why the pure half cannot live there (`DN-16-7-6`). |

⛔ **Writing rule — `TC-ArgusAgent-DOCS-001-78`.** `deferred-work.md` is **append-only**, and a
disposition must be machine-readable (the id on the disposition line, or a trailing `- status:`
field). Edits to historical entries must be annotated, not silent — 16.1's review caught exactly
that, and the remedy was **restoration**. ⛔ **This story disposes of nothing.**

### Dependencies — none are added, and that is a requirement

No new package. No new third-party import. The new `argus/` module imports **only** from
`argus.precision.adjudication`, `argus.precision.gate_independence`, `argus.detectors.*`,
`argus.index.ast_index`, `argus.store.canonical` and the standard library. The new script may
additionally import `scripts/pinned_corpus_snapshot.py`. ⛔ **No import from `argus/**` into
`tests/**`** beyond the shipped surface under test (`DF-9-2-A`). ⛔ **The new module resolves NO
repository path at module level** — every path is a repo-relative string or an argument (§0.6, the
wheel-import guard).

### Standing rules (non-negotiable)

- **AR7 / §3.3** — one arithmetic, one vocabulary, never forked. *"Two spellings of 'is this an
  assert line' is exactly the disagreement class this detector keeps closing elsewhere."*
- **AR8** — pure/impure separation; the predicate and the record are pure, all I/O lives in
  `scripts/`.
- **AR4** — ratios are exact `Fraction`s, never floats. `expert_hours` and the smoke-test proportion
  included.
- **NFR-P1** — no clock, randomness or network on any decision path. The date is **supplied**, never
  read from a clock (`_DATE_RE` validates SHAPE only).
- **NFR-P2** — the language conditional lives in `argus/index/`; the tables stay **FLAT** and
  language-agnostic.
- **NFR-S1** — no source byte, no secret value, no absolute host path in any artifact. ⛔ **AC8.6 is
  the ONE bounded carve-out and it states its own bound.**
- **NFR-M1** — 1,200 physical lines per module. **Split, never shave, never exempt.**
- **`AI-E11-1`** — every guard asserts its population is non-empty **before** asserting anything
  about it.
- **`AI-E13-1`** — the local suite is Windows-only; CI runs an ubuntu matrix. **AC8.4.**
- **`DF-10-4-E`** — an unregistered value RAISES; never defaulted, never tolerated.
- **`AI-E12-3` / `AI-E12-6`** — *a disposition recorded in prose and not in the ledger is not a
  disposition.*

### Previous-story intelligence — 16.1–16.6 all `done`

1. **Every story in Epic 16 found a stated premise false by executing it.** 16.4 found three, 16.6
   found two. **This story already carries two — §0.2's stale `DF-16-7-A` figure and §0.7's
   unsatisfiable inherited invariance contract. Expect a third.**
2. ⛔ **16.5 AND 16.6 each FAILED an independent readiness validation, and every blocking defect was
   in the STORY TEXT.** 16.6's recorded lesson is the one to carry: *"the author self-caught two
   defects, fixed them in the ACs, and left the mirrors live in the Tasks."* **§3's AC↔Task map
   exists to make that class visible; check it.**
3. **16.5's dev found the baseline RED when the story claimed GREEN**, costing a commit. §0.0 states
   it as measured — **and records this session hitting a false RED from stale bytecode on the first
   run.** Re-measure with a cleared cache. That is Task 0.
4. **16.3's own mutation run caught one of its guards UNREAL, and 16.6 expected to find one of its
   own. Expect to find one of yours.** AC7 is written to make that specific failure detectable.
5. **16.6 spent an entire extra commit on the dogfood regeneration it did not plan for** (`6304552`).
   §0.6 and §2.5 plan for it. **Four commits, not three.**
6. **16.4 closed by DECISION, not by result** — nothing ratified, `N` still 5, no detector run over a
   bench member, and **its own AC1.4 records that reaching the halt and reporting is the story
   succeeding.** ⛔ **That is this story's shape too** (`DN-16-7-3`).
7. **Two commits, not one, when a sha must be cited** — a commit cannot cite itself.
8. **The lockstep trap has fired five times.** §2.3 names this story's version.

### Git intelligence

Epic 16's arc: `chore(story file + in-progress) → [refactor/test(split-first, ALONE)] → feat(the
change) → chore(regenerate artifacts) → docs(protocol/architecture/ledger) → docs(the review)`.
**This story's arc omits the split step** (nothing needs splitting) **and RE-ARMS the regeneration
step** (§0.6/(2)), so it is `chore → feat → chore(dogfood) → docs`.

⛔ **Not one Epic 16 commit touches a `CANDIDATE_OUTPUT_PATHS` entry, and the epic's BINDING ORDERING
CONSTRAINT is intact.** This story adds no bench output, so it cannot break it — **verify that claim
with `tests/test_gate_ordering.py` rather than asserting it.**

⚠️ **Commit trailers.** 16.6's commits carried an `Evidence-partition:` trailer and hit `DF-16-6-E`'s
gap (`SEAL_CITATION_VALUES` has no `pre-seal` member) — the judgement was disclosed in the commit
body rather than smoothed. **Do the same; do not widen the vocabulary** (AC9.4). ⛔ **And keep every
commit message pure ASCII**, which 16.6 did deliberately because of `DF-16-6-F`.

### References

- [epics.md](../epics.md) — `## Epic 16` and `### Story 16.7`. ⛔ **Its 36/39/3 figures REPRODUCE at
  HEAD** (§0.1) — the rare case in this epic where the epic text is right.
- [sprint-change-proposal-2026-08-22.md](../sprint-change-proposal-2026-08-22.md) — §1.2 (the clause
  table), §1.4 (why nothing is promoted, and the smoke test), §2.2 (sequencing — **both
  preconditions are now discharged**), §2.4 (what is not in scope), §3.2, §5. **APPROVED by
  XAgent007 2026-08-22.**
- [precision-validation-protocol.md](../precision-validation-protocol.md) — §2 (roles; the
  **2026-08-22 dated block filling the QA Lead**, the **2026-08-23 block on independence**, **no
  `V1.4` row**), §3 (the ≤4-hour budget and `expert_hours` as a field), §4 (the adjudication method,
  the borderline ladder, `BORDERLINE` as first-class, exhaustiveness), §5 (the seven conditions), §6
  (R2 operator acts), §7 (the OI1 lock — precision is measured over **FINDINGS**).
- [deferred-work.md](../deferred-work.md) — `DF-16-7-A`, `DF-16-6-A`, `DF-16-6-B`, `DF-16-6-C`,
  `DF-16-6-D`, `DF-16-6-E`, `DF-16-6-F`, `DF-16-5-A`, `DF-16-5-B`, `DF-16-1-A`, `DF-15-2-E`,
  `DF-14-1-A`, `DF-13-5-A`, `DF-12-1-A`, `DF-9-2-A`
  · `DF-15-2-D` — its disposition is recorded in the ledger, dated 2026-08-22.
  ⛔ **That last id sits on a line of its OWN, deliberately** — `story_closure_claims` is
  **line-scoped**, so a disposition word beside an open id reads as a claim about *every* id on that
  physical line. See `DF-16-6-D` and §0.0's second writing rule.
- [architecture.md](../architecture.md) — §Enforcement (**guard-adequacy clause**), NFR-M1, NFR-P1,
  NFR-P2, NFR-S1, AR4, AR7, AR8
- Research (read-only harnesses, each validated in both directions):
  [`research/investigate-per-call-scoping.py`](../research/investigate-per-call-scoping.py) — ⛔ **the
  V2 derivation this story makes shipped; re-run it FIRST (Task 0.3)**;
  [`research/revalidate-fact-b-widening.py`](../research/revalidate-fact-b-widening.py);
  [`research/measure-vacuous-population-split.py`](../research/measure-vacuous-population-split.py);
  [`research/technical-argusagent-detector-categories-research-2026-08-21.md`](../research/technical-argusagent-detector-categories-research-2026-08-21.md)
- Stories [16.6](16-6-the-assertion-vocabulary-recognises-the-assertion-that-is-a-raise.md),
  [16.5](16-5-the-record-says-who-judged-and-whether-they-were-independent.md),
  [16.4](16-4-ratify-run-adjudicate-and-let-the-arithmetic-decide.md) (**HALT-2, still moot**),
  [13.3](13-3-record-the-result-and-let-it-decide.md),
  [13.2](13-2-adjudicate-every-finding-by-a-named-human.md) (**the instrument-then-escalate
  precedent**),
  [13.1](13-1-decide-what-validation-set-is-then-build-it.md)
- Code: `argus/precision/adjudication.py` (`AdjudicationRow`, `DISPOSITIONS`, `ROW_FIELDS`,
  `PROTOCOL_ADJUDICATOR_ROLES`, `adjudicator_role`, `LOCATOR_RE`, `finding_row_id`,
  `expert_hours_report`, `exhaustiveness`) · `argus/precision/gate_independence.py`
  (`assess_independence`) · `argus/detectors/provenance_scan.py` (`provenance_evidence`,
  `opens_bare_assert`) · `argus/detectors/vacuous_vocabulary.py` (`is_assertion_callee`,
  `_ASSERTION_CALLEES`) · `argus/detectors/vacuous_test.py` (`index_aligned_lines`) ·
  `argus/index/ast_index.py` (`build_ast_index`) · `argus/store/canonical.py` (**the ONE
  serializer**) · `scripts/pinned_corpus_snapshot.py` (`pinned_tree`, `materialize_pinned_bytes`,
  `verify_pinned_bytes`, `_git`) · `scripts/build_adjudication_record.py` (**the builder shape to
  copy**) · `scripts/audit_validation_corpus.py` (**the `--checkout-root` / `--map` CLI shape** —
  ⛔ **not run**) · `scripts/regenerate_dogfood_artifacts.py` ·
  `tests/test_release_preflight.py` (`_MODULES_NAMING_THE_TEST_TREE_IMPORT`) ·
  `tests/test_dogfood_artifact_currency.py` · `tests/test_module_size_ceiling.py` ·
  `tests/test_governance_record_integrity.py`

---

## Tasks & Subtasks

### ⛔ Task 0 — REPRODUCE §0 BEFORE WRITING ANYTHING

- [ ] **0.1** *(AC8.1)* Confirm HEAD, branch and working tree. Expected: branch
      `epic-16/discharge-df-15-2-d`, HEAD at or after **`d6625b5`**, and every
      `git status --porcelain` entry under `_bmad-output/design-artifacts/ArgusAgent/`.
      ⛔ **Do NOT assert a COUNT of entries** (§0.0) — assert the invariant: **ZERO entries under
      `argus/`, `tests/`, `scripts/` or `…/validation-corpus/`.** Anything under those four means
      the tree moved; re-read §0 against it before writing a line.
- [ ] **0.2** *(AC9.1)* ⛔ **Clear `__pycache__` and export `PYTHONDONTWRITEBYTECODE=1` FIRST**
      (§0.0 — this session's own false RED). Then re-run **every** gate in §0.0's table and record
      each exit code and count. ⛔ **A `--check` exit `1` means an artifact was already stale before
      you touched anything — STOP and report.**
- [ ] **0.3** *(AC1.1–1.3)* Re-run
      `research/investigate-per-call-scoping.py` and confirm **V0 0 · V1 6 · V2 36 · V3 6 · V4 676 ·
      V5 125**, with `V2:agent-smith 22` and `V2:minions 14`. ⛔ **If V2 is not 36, the story's
      entire subject has moved — STOP and re-read §0 before writing anything.**
- [ ] **0.4** *(AC8.3)* Capture `git -C <member> status --porcelain` for all five members. ⛔ **Record
      it; assert NOTHING about it** (§0.7, `DN-16-7-4`). Confirm the five checkout paths resolve —
      note `agent-smith` is at **depth 5**.
- [ ] **0.5** *(AC1.3)* Re-derive the **39 → 36** delta and the three names in §0.1's second table,
      by running the derivation once with `"AssertionError"` removed from the wide table **in
      memory**. ⛔ **Do not edit `vacuous_vocabulary.py` to do it.**
- [ ] **0.6** *(AC3.4, §0.3)* Re-measure the blast radius **in memory**: append 36 synthetic advisory
      `TP` rows to a **loaded copy** of `adjudication-record.json` and confirm `total_tp` 0 → 36,
      `adjudicated_population` 31 → 67 and `independence.status` → `SECOND_REVIEWER_INTERNAL`; then
      confirm the file on disk is **byte-identical**. ⛔ **Never write the simulated record.**
- [ ] **0.7** *(AC3.4)* Confirm the two closed-schema traps: widening `ROW_FIELDS` makes
      `load_record()` on the committed record RAISE, and `rec.to_bytes() == <committed bytes>` is
      `True`.
- [ ] **0.8** *(§0.6)* Confirm all three registry guards by execution: the import-reach walk returns
      **14** today; `tests/test_dogfood_artifact_currency.py` is green today; and
      `scripts/regenerate_dogfood_artifacts.py` refuses a dirty `argus/` tree.
- [ ] **0.9** *(§0.4, §0.8)* Confirm the QA Lead is **FILLED** (`"Veer Pratap Singh (QA Lead)"`
      constructs a valid row), the External adjudicator is **unfilled**, the protocol change-log head
      is **V1.3**, the next free `TC-ArgusAgent-PRECISION-001-NN` is **115**, and the next free
      ledger id is **`DF-16-7-B`**.
- [ ] **0.10** *(AC1.5)* Record every disagreement with §0 in Completion Notes. **The tree wins.**

### Task 1 — THE PLACEMENT DECISION, TAKEN BEFORE THE FIRST LINE (`DN-16-7-6`, AC8.7)

- [ ] **1.1** *(AC8.1, `DN-16-7-6`)* Confirm the three new files and their homes:
      `argus/precision/silent_class.py` (pure), `scripts/build_silent_class_record.py` (I/O),
      `tests/test_silent_class.py` (guards).
- [ ] **1.2** *(AC8.1)* ⛔ Confirm the two artifact names and that both land under
      `…/ArgusAgent/validation-corpus/` (§0.0's PATH ROOTS). Write the full paths out before using
      them; the short form ENOENTs on its first line.
- [ ] **1.3** *(AC8.7)* ⛔ **No `_EXEMPT_BY_DESIGN` entry, ever** — `MAINT-001-04` lets that registry
      shrink only, and every new file here starts far below 1,200.

### Task 2 — THE PURE HALF: THE SILENCE PREDICATE (AC1, AC2)

- [ ] **2.1** *(AC2.1)* Write the silence predicate in `argus/precision/silent_class.py`,
      **COMPOSED** from `provenance_evidence`, `is_assertion_callee` (**WIDE**), `opens_bare_assert`
      and `index_aligned_lines`. Its docstring names `DN-14-2-1` and states in its own words why
      the frozen table is the wrong vocabulary for this question.
      💡 **You need NO `ast` walk of your own, and AC2.1 forbids one. Measured:**
      `argus.index.ast_index.Definition` already carries **`name`**, `kind`, `start_line` and
      `end_line` — confirmed by execution against `minions@ec63b72`
      `tests/apaa/test_coverage_ledger.py`, which returns
      `name='test_no_float_fields_serialize' kind='function' span=239..243`. The test name, the span
      and the edges all come off the shipped index. **The `research/*.py` harnesses re-parse with
      `ast` because they predate needing the name cleanly — do not copy that from them.**
- [ ] **2.2** *(AC1.1, AC1.4)* Write the class record: one row per member with `member_id`, POSIX
      `locator`, test name, `disc`, `cons`, `idiom`, `disposition`, `adjudicator`, `adjudicated_on`,
      `reason`. ⛔ **`finding_row_id` and `LOCATOR_RE` are IMPORTED, never re-declared** (AC3.3).
- [ ] **2.3** *(AC4.3, AC5.1, AC5.2)* Register the `idiom` vocabulary as a **CLOSED** mapping with a prose
      meaning per member; an unregistered member RAISES (`DF-10-4-E`). ⛔ **It is NOT a disposition
      and `DISPOSITIONS` is not touched** (`DN-16-7-2`).
- [ ] **2.4** *(AC5.3, AC6.1–6.2)* Derive and publish, on the record: the smoke-test proportion as an
      exact `Fraction` over the **assessed** rows (refusing an unassessed denominator);
      `expert_hours` through the **EXISTING `expert_hours_report()`**; and the independence status
      through the **EXISTING `assess_independence`** over **this record's** live-row adjudicators.
      ⛔ **Call them. Do not re-implement, wrap-and-modify, or copy either.**
- [ ] **2.5** *(AC2.2, AC3.4, AC8.1)* ⛔ Touch **nothing** in `argus/detectors/**`,
      `argus/precision/adjudication.py`, `argus/precision/gate_*.py` or
      `argus/precision/replay_harness.py`. Confirm with `git diff --stat`.
- [ ] **2.6** *(AC9.1, §0.6/(3))* ⛔ **Resolve NO repository path at module level.** Every path is a
      repo-relative **string** or an argument — the treatment `adjudication.RECORD_PATH` gets, for
      the `DF-9-2-A` reason. The wheel-import guard fails otherwise.

### Task 3 — THE I/O HALF: THE BUILDER (AC1.2, AC3.1, AC8.3, AC8.4)

- [ ] **3.1** *(AC3.1)* Write `scripts/build_silent_class_record.py` on
      `scripts/build_adjudication_record.py`'s shape: `--check` verifies currency and writes nothing
      (**exit 0**), a precondition failure is `REFUSED — …` on stderr with **exit 2**, and it is
      **append-only over human judgements** — an existing row carrying a human disposition is
      carried through byte-identically and never re-seeded.
- [ ] **3.2** *(AC1.2)* Read the population from the committed
      `validation-corpus/adjudication-set-13-5.json`, filtering to `rule_id ==
      "vacuous_test_heuristic"`. ⛔ **Assert the population is non-empty (1,032) BEFORE asserting
      anything about it** (`AI-E11-1`), and **REFUSE** on 0 skipped/unresolvable being violated.
- [ ] **3.3** *(AC8.3, AC8.4)* ⛔ Read every member through the shipped **content-addressed**
      `pinned_tree` / `materialize_pinned_bytes` / `verify_pinned_bytes`, proving the materialised
      bytes against the pin **by blob hash**. Route every git call through
      `scripts/pinned_corpus_snapshot.py::_git` — ⛔ **do not add a sixth `_git`, and never
      `text=True` without `encoding=`** (`DF-16-6-F`). The checkout root arrives via
      `--checkout-root` / `--map`; ⛔ **no absolute host path is hardcoded** (NFR-S1).
- [ ] **3.4** *(AC3.1)* Serialize the record through **`argus.store.canonical`** — ⛔ **never
      `json.dumps`** — and write with `encoding="utf-8", newline="\n"`.
- [ ] **3.5** *(AC2.3)* ⛔ The script imports the new module; **nothing in `argus/**` imports the
      script.** Confirm the edge direction now, before Task 6's guard asserts it.
- [ ] **3.6** *(AC4.1, AC4.5)* Seed **exactly 36 `UNADJUDICATED` rows**, each with **no adjudicator and no
      date**. ⛔ **The script must be structurally incapable of writing a `TP`, `FP` or
      `BORDERLINE`** — construct only `UNADJUDICATED` and let `__post_init__` enforce the rest
      (`DN-6`).
- [ ] **3.7** *(AC1.4, AC3.1, AC4.2, AC8.6)* Render the Markdown worklist **from the record**, with
      `blocking-worklist-13-5.md`'s *"DERIVED … do not hand-edit"* header. ⛔ **Read AC8.6 BEFORE
      writing a source span**: spans go in the Markdown only, never the JSON; each is bounded to the
      flagged test function and read from the **pinned blob**; the header states the carve-out and
      its bound; anything credential-shaped is **redacted through the shipped redaction**, and the
      redaction is recorded.

### Task 4 — THE GUARDS (AC1, AC2.3, AC3, AC4, AC5, AC6, AC7)

⛔ **AC7.3 BINDS EVERY SUBTASK BELOW.** Each case states its non-vacuity preamble **before** it
asserts anything — the index really emitted the edges the case is about, `disc ≥ 1`,
`statement_count > 0` — and each carries a **control** with `statement_count` and
`discarded_sut_calls` asserted **equal**, isolating the PREDICATE from the fixture's SHAPE. A case
missing either half is not done.

- [ ] **4.1** *(AC3.1, AC7.3)* `tests/test_silent_class.py`, module docstring naming **why the module
      exists** (mirrors `argus/precision/silent_class.py`; the `gate_independence.py` precedent) and
      the verification area. Ids start at **`TC-ArgusAgent-PRECISION-001-115`**.
- [ ] **4.2** *(AC3.3)* The **vocabulary-reuse** cases: an unregistered disposition RAISES; an
      unregistered adjudicator role RAISES; a non-human disposition carrying an adjudicator RAISES.
      ⛔ **Assert the objects are the SAME objects** (`is`, not `==`) as
      `argus.precision.adjudication`'s — a re-declared copy would leave every other guard green.
- [ ] **4.3** *(AC5.1, AC5.2)* The **`idiom` vocabulary** cases: closed in **both directions** — an
      unregistered member raises, and a registered member no case exercises is itself a finding.
      ⛔ **And the orthogonality case:** a row that is `FP` **and** `DELIBERATE_SMOKE_TEST` is
      constructible and round-trips — that combination is the whole measurement (`DN-16-7-2`).
- [ ] **4.4** *(AC6.1)* The **expert-hours** case: an exact `Fraction`; an overrun **reports and does
      not fail**; `None` reads as **NOT RECORDED**, never zero. ⛔ **Assert no caller branches a
      pass/fail on the sentence.**
- [ ] **4.5** *(AC6.2)* The **independence** case: the status is **DERIVED** from this record's own
      adjudicator ids through `assess_independence`, is `NOT_ESTABLISHED` over a record with zero
      live human rows, and ⛔ **moving it through every reachable member leaves nothing about the
      GATE changed** — the `TC-ArgusAgent-PRECISION-001-109` shape, applied to this record.
- [ ] **4.6** *(AC4.1, AC4.3)* The **seeded-record** cases: exactly 36 `UNADJUDICATED` rows, all with
      no adjudicator and no date; 36 distinct `finding_id`s; `BORDERLINE` is representable, makes the
      run non-exhaustive, and enters **neither** side of any ratio.
- [ ] **4.7** ⛔ *(AC2.1, AC2.3)* **THE STRUCTURAL CASES — the only task that covers them, and the
      one the first draft of §3's map had missing entirely.**
      (a) **Composition, not re-implementation** (AC2.1): an `ast` walk of
      `argus/precision/silent_class.py`'s own source asserts it contains **no** `ast.walk`-based
      SUT-call counter and **no** assertion-name regex, and that it **names** `provenance_evidence`,
      `is_assertion_callee` and `opens_bare_assert`. The `TC-ArgusAgent-PRECISION-001-87` / `-99`
      shape — reuse it.
      (b) **The edge runs ONE WAY** (AC2.3): an `ast` walk over **all** of `argus/**` asserts that
      no module under `argus/detectors/**`, and none of `argus/precision/gate_*.py`,
      `adjudication.py`, `replay_harness.py` or `__init__.py`, names the new module — directly or
      transitively. ⛔ **Assert the walk found something before asserting what it did not find**
      (`AI-E11-1`): a walk that silently parsed zero files passes forever.

### Task 5 — RE-DERIVE, PUBLISH, AND PROVE NOTHING MOVED (AC1, AC3.2, AC8.3)

- [ ] **5.1** *(AC1.1–1.5)* Re-derive **36 / 22+14 / 19 files / 39→36 with the three named / 1,032 walked
      / 0 skipped**, and record every figure. ⛔ **If one disagrees with §0.1, correct the STORY
      (AC1.5) — never the derivation.**
- [ ] **5.2** *(AC3.2)* Build both artifacts. Then confirm `git diff --stat` over
      **`_bmad-output/design-artifacts/ArgusAgent/validation-corpus/`** shows **only the two NEW
      files** and that the four pre-existing JSONs are **byte-unchanged**. ⛔ **Use the FULL path** —
      `validation-corpus/` is not at the repo root.
- [ ] **5.3** *(AC5.3)* Confirm the smoke-test proportion **refuses** an unassessed denominator, and
      that with 36 `NOT_ASSESSED` rows it reports **not measured** rather than a number.
- [ ] **5.4** *(AC8.3)* ⛔ **Write nothing to any corpus member.** Re-capture the five porcelains and
      **record them as an observation** in Completion Notes. ⛔ **Do not assert them equal** —
      `minions` moved under the contexting session by another party's hand (§0.7).

### Task 6 — DRIVE IT RED (AC7)

- [ ] **6.1** *(AC7.2)* `PYTHONDONTWRITEBYTECODE=1`, clear `__pycache__`. **Capture
      `git status --porcelain` over THIS repository NOW and keep it** — that capture, not emptiness,
      is the restoration contract.
- [ ] **6.2** *(AC7.1(i))* Remove `"AssertionError"` from `_ASSERTION_CALLEES` **in memory**. The
      class must move **36 → 39**. Observe RED at the real seam; record the exact failure text;
      restore; assert the porcelain is **byte-identical** to 6.1's capture; re-run **green**.
- [ ] **6.3** *(AC7.1(ii))* Route the silence question through `_CORROBORATION_ASSERTION_CALLEES`.
      The class must **change**. ⛔ **This is `DN-14-2-1` made executable** — the guard's docstring
      states the false accusation it prevents. Observe RED, record, restore.
- [ ] **6.4** *(AC7.1(iii))* Drop the `disc ≥ 1` conjunct. The class must grow toward §0.2's **45**.
      Observe RED, record, restore.
- [ ] **6.5** *(AC7.4)* The **generated adversarial variant**, closed over the derived class or the
      wide table itself — not hand-listed — with its **count asserted**.
- [ ] **6.6** *(AC8.4)* The **portability** cases: every locator matches `LOCATOR_RE` across all 36;
      ⛔ **`os.sep`, `os.path.join` and a literal backslash appear nowhere on a locator-building
      path** (assert by source/`ast` scan of the two new modules); every subprocess call decodes
      explicitly; every read and write names its encoding.

### ⛔ Task 7 — THE OPERATOR HALT — *the judgement is not the dev's, in any part* (`DN-16-7-3`)

- [ ] **7.1** *(AC4.1–4.2)* Publish the worklist and the seeded record. State plainly, in Completion
      Notes and in the worklist header: **36 rows await a named human**, who the registered
      adjudicators are (`"XAgent007 (Engineering Lead)"`, `"Veer Pratap Singh (QA Lead)"`), what each
      row needs (a `TP`/`FP`/`BORDERLINE`, a **reason**, an `idiom`, a date), and where the file is.
- [ ] **7.2** *(AC4.4, AC9.4)* ⛔ **STOP if protocol §4's ladder reaches the UNFILLED External
      adjudicator** — report **which rows and why**, never a default. ⚠️ Re-read §0.4 first: a
      `BORDERLINE` alone is **not** the ladder's third step.
- [ ] **7.3** *(AC4.5)* ⛔ **WRITE NO `TP`, `FP` OR `BORDERLINE`. NOT ONE.** If the operator supplies
      judgements in-session, **TRANSCRIBE them verbatim**, record that they were transcribed and
      from whom, and infer, complete or default nothing. ⛔ **Halting here with the instrument built
      and the worklist published IS this story succeeding** — report it as a HALT, not a failure.

### Task 8 — THE LEDGER (AC8.5)

- [ ] **8.1** *(AC3.2, AC8.2)* Before touching the ledger, confirm both existing builders `--check` → exit 0
      and the four corpus JSONs are byte-unchanged.
- [ ] **8.2** *(AC8.5)* Append **`DF-16-7-B`**: `DF-16-7-A`'s V5 re-measured **122 → 125** at HEAD
      with the cause (16.6's three moved from silent to asserts-not-about-the-SUT), **and** that the
      class's TP proportion is not yet measured pending the human act. Machine-readable fields:
      `id`, `origin`, `owner`, `target_story`, `category`, `severity`.
      ⛔ **Confirm `DF-16-7-B` is still the next free letter** and take the next if it moved.
- [ ] **8.3** *(AC8.5)* ⛔ **Append only.** No historical entry edited — in particular **`DF-16-7-A`
      is not corrected in place** (§3.4: strike, never erase). Nothing disposed of. No absolute host
      path and no corpus source span (NFR-S1, AC8.6).
- [ ] **8.4** *(AC8.5)* ⛔ **THE BYTE CHECKS (`DF-16-6-C`).** Append in **binary**, then assert: lone
      `CR` count still exactly **1**; `CRLF` pairs still **0**; the file still ends with a newline;
      `git diff --numstat` reports **`+n / -0`**. ⛔ **Do NOT add `.gitattributes`.**
- [ ] **8.5** *(§0.0)* ⛔ Re-read §0.0's **closure-verb writing rule** before committing the ledger
      append **or** this story file: a closure verb sharing a physical line with an open `DF-*` id
      turns `tests/test_governance_record_integrity.py` RED, and it is what made 16.6's own baseline
      false (`DF-16-6-D`).

### Task 9 — GATES AND HAND-OFF (AC8.2, AC9)

- [ ] **9.1** *(AC9.1, AC8.2, AC8.7)* ⛔ Clear `__pycache__`, `PYTHONDONTWRITEBYTECODE=1`, then run: the full suite
      with `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1`; coverage ≥ 80%; `mypy argus` (**CI scope — do NOT
      widen to `scripts`**, §0.0's caveat); `bandit -r argus --severity-level medium`;
      `tests/test_module_size_ceiling.py`; `tests/test_gate_ordering.py`;
      `tests/test_release_preflight.py`; `tests/test_dogfood_artifact_currency.py`;
      `tests/test_governance_record_integrity.py`; and **`tests/test_gate_*.py` (all nine) for
      AC8.2**. Record every exit code.
      ⛔ **`tests/test_gate_*.py` staying green IS AC8.2's whole discharge** — write no new assertion
      about `argus/precision/gate_*.py` and import nothing from `gate_decision` into
      `tests/test_silent_class.py`.
- [ ] **9.2** *(AC9.2, §2.5)* The **four-commit arc**: `chore` → `feat` → `chore(dogfood)` → `docs`.
      ⛔ **`scripts/regenerate_dogfood_artifacts.py` REFUSES a dirty `argus/` tree**, so `argus/`
      must be committed before the regeneration runs, and the regenerated artifacts are committed
      separately. **Keep every commit message pure ASCII** (`DF-16-6-F`).
- [ ] **9.3** *(AC9.3, AC8.1)* Confirm the final write set equals AC8.1 exactly. ⛔ **Use
      `git status --porcelain`, NOT `git diff --name-only`** — three deliverables are **NEW
      untracked** files `git diff` cannot see. Expect **nothing** under `argus/detectors/`,
      `argus/precision/gate_*.py`, `argus/precision/adjudication.py` or the four pre-existing
      corpus JSONs.
- [ ] **9.4** *(AC8.1, §0.6)* Confirm the **one** permitted edit to `tests/test_release_preflight.py`: the
      new module registered in `_MODULES_NAMING_THE_TEST_TREE_IMPORT` with its prose comment. ⛔ **No
      assertion, no other registry and no import in that file may change.** Anything wider is AC9.4.
- [ ] **9.5** *(AC9.5)* Completion Notes per AC9.5 — including **the HALT stated plainly**, with
      exactly what the named human must do and where the worklist is.

### Review Findings

*(none yet — the story has not been implemented)*

---

## Change Log

| Date | Change | Author |
|---|---|---|
| 2026-08-23 | Story contexted at HEAD `d6625b5`. **Every §0 figure measured by execution, none copied.** ⛔ **§0.3 is the story's central finding and it is proved rather than argued:** appending these 36 advisory dispositions to `adjudication-record.json` takes `total_tp` **0 → 36**, `adjudicated_population` **31 → 67**, `distinct_rule_class_count` **1 → 2** and `independence.status` **`NOT_INDEPENDENT` → `SECOND_REVIEWER_INTERNAL`** — two of which the epic's own AC forbids outright — and it is wrong on the protocol's terms besides, since all 1,032 findings are advisory and three shipped surfaces say advisory findings are not in the denominator. `DN-16-7-1` sends them to new artifacts instead, **without** answering 16.4's still-moot HALT-2. Both closed schemas measured fatal to widen: adding a field to `ROW_FIELDS` makes `load_record()` on the committed record RAISE (`DN-16-7-2`). **The class re-derived at HEAD is 36** (agent-smith 22 + minions 14, 19 files), **39 pre-16.6 with the three 16.6 removed NAMED** — the epic, the change proposal and the sprint-status comment all REPRODUCE, which is the rare case in this epic where the artifact is right. `V1 ⊆ V2` and 30 of 36 lie outside V1, so promoting V2 later would be a different predicate, not a loosening. ⛔ **Two premises DID fall:** `DF-16-7-A`'s V5 figure is **122 on the ledger, 125 on the tree** (16.6's three moved silent → asserts-not-about-the-SUT), recorded for a new dated entry rather than an edit; and **Story 16.6's AC4.5 invariance contract is unsatisfiable here** — `minions` went 7 → 1 dirty entries under this session by another party's hand, so `DN-16-7-4` replaces it with content-addressed reads proved by blob hash plus an asserted read-only git allow-list, which is strictly stronger and actually satisfiable. **The baseline is GREEN (1,695 passed / mypy 94 files / bandit 0 medium / 95.55% coverage / both builders exit 0) — but the FIRST run of this session was a false RED from stale `__pycache__`**, §2.5's own recorded 16.2 lesson reproducing today, so `PYTHONDONTWRITEBYTECODE=1` is now a writing rule. Three registry guards measured to fire on this story's shape: the import-reach set (14 → 15), the dogfood currency guard (re-arming 16.6's extra commit — hence a **four**-commit arc), and the wheel-import guard. ⛔ **`DN-16-7-3` records the load-bearing scoping decision: the 36 judgements are an OPERATOR ACT no agent may take** (protocol §2: `UNADJUDICATED` is the only member an automated producer may write), so the story builds the instrument, publishes the worklist and **HALTS** — the 13.2 / AC7 and 16.4 / AC1.4 precedent, where reaching the halt and reporting **is** the story succeeding. ⛔ **§3's AC↔Task map was self-audited before this file was finalised and the FIRST DRAFT OF IT WAS WRONG — nine mis-citations and one AC (AC2.1/AC2.3's import-graph guard) with no task at all.** All ten are repaired here and the finding is recorded in §3 rather than smoothed: it is 16.6's own *"an AC repaired on one side of the file while its executable twin kept the defect"* firing inside the table built to catch it. Task **4.7** exists because of it. One reuse trap closed at the same time, by execution: `argus.index.ast_index.Definition` already carries **`name`**, so the builder needs no `ast` walk of its own — and AC2.1 forbids one, which would have made the AC unsatisfiable if the field had not been there. Locked decisions cited and not reopened: `DN-14-2-1`, `DN-3`, `DN-2a`, `DN-6`, `DN-16-3-3`, §3.4, §6 R2. `DF-13-5-A` **OPEN and UNSPENT**; `N` 5; `SECTION_5_CONDITIONS` 7; change-log head **V1.3**; gate **BLOCKED**. `backlog` → `ready-for-dev`. | create-story (Scrum Master) |
