# Ledger verification worklist — every `target_story` that points at a closed story

> ⛔ **THIS DOCUMENT CLOSES NOTHING BY ARGUMENT.** Every row below carries the command that
> decided it and that command's output. `AI-E12-3` — *resolving entries in prose rather than
> against evidence* — is the named defect this story exists to end, and it was committed once
> already inside the story written to end it. Produced by Story 19.6 from
> `ledger-verification-record.json`.

**Population:** 47 entries — 46 registry-bound plus `DF-AUD-DETECT-C`, which is **not** in the registry and whose verification therefore cannot change it.

**Outcomes:** 23 STILL-OPEN · 18 ALREADY-RESOLVED · 4 NEEDS-A-HUMAN · 2 BLOCKED

**Registry shrink: 2 pairs.**

⛔ **THE SHRINK IS AN OUTCOME, NEVER A TARGET.** Every ALREADY-RESOLVED entry was tested against s0.4's ONLY legitimate exit: the pair moves to _DISPOSING_STORY_POINTERS, and only with DF-1-7-B three-way evidence (story file AND retrospective AND shipped code). 18 entries are ALREADY-RESOLVED; only 2 clear that bar. No target_story field was rewritten and no target_story: NONE was introduced to manufacture a larger shrink.

## The registry shrink, and why only these

| entry | story | evidence |
|---|---|---|
| `DF-14-2-A` | `14-3-…` | story file names it · Epic-14 retro records *"2 closed (`DF-14-2-A`, `DF-14-2-B`)"* and *"both verified as genuinely received by the ledger"* · `importorskip` count in `tests/test_vacuous_detector.py` is **0** |
| `DF-14-2-B` | `14-3-…` | same story file and retro · `provenance_scan.py` now uses `\A`/`\Z` and its docstring records *"Also re-anchored `\A` 2026-08-18 (Story 14.3)"* |

⛔ **Sixteen other entries are ALREADY-RESOLVED and do NOT leave the registry.** Their
`target_story` names a story that did not discharge them, or the retrospective does not record
the closure, so they fail `DF-1-7-B`'s three-way bar. `DF-10-3-A` is the clearest: it is
genuinely fixed, and its own entry says the fix landed in Story **12.8** while the pointer names
**12.9** — *"the entry names this story rather than 12.8, so it was invisible to the story that
fixed it"*. Rewriting that pointer to manufacture an exit is the forbidden mechanism 2.

## ⛔ Questions for the operator — STATED, NOT ANSWERED

### `DF-10-4-A`

- **Command:** `grep -c 'if eligible:' argus/reports/generator.py`
- **Output:** 3 occurrences - the all-or-nothing trigger is LIVE
- **Finding:** CONTRADICTION FOUND, REPORTED NOT RESOLVED. The ledger records 'status: CLOSED 2026-08-16', but the defect it describes (the all-or-nothing readability trigger) is still in the code, and DF-11-4-A explicitly says 'the SAME trigger already filed as DF-10-4-A' and is itself open. QUESTION FOR THE OPERATOR, NOT ANSWERED HERE: was DF-10-4-A closed by supersession into DF-11-4-A (coherent), or is this an AI-E12-6 false closure? Only the operator can say which was intended.

### `DF-11-4-B`

- **Command:** `grep -n tree-sitter pyproject.toml; grep -n CORE_VERSION_CEILING_EXCLUSIVE argus/shared/grammar_status.py`
- **Output:** pin 'tree-sitter>=0.25.0,<0.26' intact; CORE_VERSION_CEILING_EXCLUSIVE=(0,26,0)
- **Finding:** QUESTION FOR THE OPERATOR, NOT ANSWERED HERE: should the <0.26 bound be re-validated against a real 0.26 install and lifted? The entry names owner 'XAgent007 (operator) for the decision'. Re-validation needs a throwaway environment, which is an operator action.

### `DF-11-4-D`

- **Command:** `grep -c _NOTE_SECTIONS tests/*.py`
- **Output:** still present; test_release_surface_honesty.py carries 6 references
- **Finding:** QUESTION FOR THE OPERATOR, NOT ANSWERED HERE: the entry asks the Epic-11 CHECKPOINT REVIEW to read this file's edit history after the pattern ran to five consecutive _NOTE_SECTIONS edits. That is a human review act, not a code defect, and no code change can discharge it.

### `DF-AUD-DETECT-C`

- **Command:** `grep -rn '_evidence_for|scan_evidence' argus/detectors/secret_scan.py`
- **Output:** _evidence_for at :421, reachable only from scan_evidence at :399-414; pipeline calls run()
- **Finding:** NOT IN THE REGISTRY (s0.3) so this verification cannot and does not change it. QUESTION FOR THE OPERATOR, NOT ANSWERED HERE: the entry names two NON-EQUIVALENT repairs - delete the call and correct the comment (matches what ships), or widen DetectorResult to carry evidence (matches what Story 2.5 SAYS). The entry itself says choosing is the Engineering Lead's.

## Blocked on an operator act

### `DF-6-6-A`

- **Command:** `import PRECISION_GATE_THRESHOLD; read gate-decision-record.json`
- **Output:** threshold 4/5; gate outcome = BLOCKED
- **Finding:** BLOCKED ON AN OPERATOR ACT. Asks for the human TP/FP adjudication that clears the >=80% gate - that is Story 19.4 (and 19.2 before it). Story 19.6 AC6.2: adjudicating a finding is NOT an autonomous act, so this STOPS here.

### `DF-7-2-A`

- **Command:** `same as DF-6-6-A`
- **Output:** gate outcome = BLOCKED
- **Finding:** BLOCKED ON THE SAME OPERATOR ACT as DF-6-6-A - the human adjudication over the dogfood findings. Not verifiable further without 19.4.

## Already resolved — verified against the code

### `DF-10-3-A`

- **Command:** `python -m argus.cli audit --nosuchflag . ; python -m argus.cli`
- **Output:** exit 1 ; exit 1
- **Finding:** Usage errors now exit 1 (reserved 'no verdict'), not 2. The BLOCKED-code collision is gone. Ledger already records CLOSED 2026-08-15 by Story 12.8/AC8.

### `DF-11-5-A`

- **Command:** `grep -oE '1[45][0-9]{3}' minions-dogfood-partition-plan.md`
- **Output:** 14638 / 14758 against the 15000 budget
- **Finding:** Entry recorded 14997/15000 - three lines of headroom. Now 14758: 242 lines. The named cliff ('the next story that writes more than 3 lines cannot proceed') no longer exists.

### `DF-11-5-C`

- **Command:** `grep -c FORTHCOMING README.md; ls argus/assets/commands/`
- **Output:** 0 markers; 3 command assets ship (argus-audit.md, argus-audit-report.md, argus-audit-security.md)
- **Finding:** BOTH halves of TC-ArgusAgent-DOCS-001-56 moved together: marker removed AND the wheel ships commands. target_story named 12-7, which is the story that delivered it - REGISTRY-EXIT CANDIDATE, pending three-way evidence.

### `DF-13-1-A`

- **Command:** `import VALIDATION_CORPUS, eligible_member_count, validation_floor_n`
- **Output:** 21 members; eligible N = 5; floor = 5
- **Finding:** Entry: 'the manifest is SPECIFIED and EMPTY; populating it is an operator act that has not been performed'. It has since been performed - N = 5 >= floor 5. DF-13-2-A's own note corroborates ('N = 5 >= 5, from Story 13.1').

### `DF-14-2-A`

- **Command:** `grep -c importorskip tests/test_vacuous_detector.py`
- **Output:** 0
- **Finding:** The importorskip gate is gone, and ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1 now converts skip to failure in tests/test_multilanguage_audit.py:41,65.

### `DF-14-2-B`

- **Command:** `sed -n '163,168p' argus/detectors/provenance_scan.py; grep -n anchored argus/detectors/provenance_scan.py`
- **Output:** _ASSIGNMENT_RE now uses \A ... \Z; docstring :80 corrected to 'No pattern below is anchored with ^ or $ - every one uses \A'; :171 records 'Also re-anchored \A 2026-08-18 (Story 14.3)'
- **Finding:** BOTH halves the entry offered are done: the pattern was re-anchored AND the docstring claim corrected. The code names the discharging story and date. target_story names 14-3, which IS the discharger: STRONGEST REGISTRY-EXIT CANDIDATE.

### `DF-14-3-H`

- **Command:** `wc -l < tests/test_vacuous_detector.py`
- **Output:** 791
- **Finding:** Entry recorded 1161/1200 - 39 lines of headroom, 'the tightest tracked module in the repository'. Now 791: 409 lines of headroom. The squeeze is gone.

### `DF-5-1-A`

- **Command:** `ls minions_core/apaa/cache/key.py; grep -n prompt_template_version argus/cache/key.py`
- **Output:** minions_core path ABSENT; argus/cache/key.py:308 prompt_template_version field present
- **Finding:** Slot exists in RecordingProducingClosure. Ledger itself already records CLOSED 2026-06-28. APAA tree separated into argus/.

### `DF-8-1-A`

- **Command:** `sed -n '717,745p' argus/reports/generator.py`
- **Output:** row 4 renders WARNING 'Release readiness is NOT VOUCHED - Argus found nothing blocking, but ... This is a statement about the audit, not about the code.'
- **Finding:** The CAUTION 'Repository is NOT ready for release' now lives ONLY in row 2 (blocking_finding_count > 0). The row-4 code comment names DF-8-1-A as the defect it closes. REGISTRY-EXIT CANDIDATE pending three-way evidence.

### `DF-8-2-A`

- **Command:** `wc -l < argus/pipeline.py`
- **Output:** 1111
- **Finding:** Entry: 1199/1200, 'next line breaches'. Now 1111 - 89 under the cap. The edge condition no longer exists.

### `DF-8-2-B`

- **Command:** `grep -A4 _UNAMBIGUOUS_TEST_SUFFIXES argus/detectors/vacuous_test.py; is_test_file probes`
- **Output:** suffixes now _spec.rb/_test.rs/... ; latest.java->False, myspec.rb->False, foo_spec.rb->True
- **Finding:** Separator-less 'test.java'/'spec.rb' are gone. Verified BOTH directions: false positives cleared AND the true positive still fires.

### `DF-8-3-B`

- **Command:** `grep -n 'render_ship_readiness|except' argus/cli.py`
- **Output:** line 874 call is inside try; 876 except ShipReadinessError; 879 except ValueError
- **Finding:** The call is no longer outside the guard - a raise can no longer escape main() as an uncaught traceback.

### `DF-8-4-A`

- **Command:** `grep -B2 -A8 INSUFFICIENT_COVERAGE action.yml`
- **Output:** exit 1 -> AUDIT_FAILED, documented 'NOT a verdict ... never read as a ran-and-under-covered result'
- **Finding:** The 'else -> INSUFFICIENT_COVERAGE' swallow of exit 1 is gone.

### `DF-8-5-A`

- **Command:** `grep -n 'DOGFOOD_ArgusAgent_VERSION' argus/dogfood/proof_run.py; grep '^version' pyproject.toml`
- **Output:** proof_run.py:227 DOGFOOD_ArgusAgent_VERSION = _ARGUS_VERSION ; pyproject version = 0.1.0
- **Finding:** Hardcoded '1.43.0' replaced by derivation from the package version, so the bundle token cannot contradict the package.

### `DF-9-2-C`

- **Command:** `git ls-files argus/dogfood/ | grep -c '.pyc$'`
- **Output:** 0
- **Finding:** Entry claimed 3 tracked .cpython-312.pyc files. Zero remain tracked.

### `DF-AUD-APAA-D`

- **Command:** `grep -rn 'multi-language|V2' architecture.md`
- **Output:** line 315 '~~multi-language AST,~~' STRUCK; line 317 'multi-language AST grounding is delivered in V1'; line 1406 '~~multi-language AST (V2),~~' STRUCK
- **Finding:** The V2 designation the entry says was never updated has since been struck (not erased - s3.4 form) and the V1 delivery stated positively.

### `DF-AUD-APAA-E`

- **Command:** `grep 'status:' entry block; grep -c 'argus audit' README.md docs/first-run.md`
- **Output:** entry's own status: 'CLOSED 2026-08-10 - remedy delivered, and the entry's own enumeration corrected from four to six'; README 21 / first-run 5 documented invocations
- **Finding:** Closed in the ledger with its enumeration corrected at closure time. Nothing re-opened it.

### `DF-AUD-APAA-F`

- **Command:** `grep -n 'except' argus/index/ast_index.py`
- **Output:** ast_index.py:434-436 documents 'This function USED TO BE one try ending in except (ImportError, Exception): pass'; arms now split - 405 tree_sitter_runtime_unvalidated, 492 grammar_load_failed_<lang>
- **Finding:** The exact remedy the entry names - split the arms, add a distinct broken-grammar token, pin both - is delivered. target_story named 10-4, which is the story that delivered it: REGISTRY-EXIT CANDIDATE pending three-way evidence.

## Still open — verified still present

### `DF-10-2-A`

- **Command:** `count 'declarator' in argus/index/ast_index.py`
- **Output:** 0 occurrences
- **Finding:** C/C++ carry a function_definition's name under the declarator field; the vocabulary still has no declarator handling, so those languages still extract zero Definitions. Entry's owner is OPERATOR (XAgent007) and AI-E11-7 says what is needed is a dated decision, not an implementation.

### `DF-10-4-B`

- **Command:** `grep -rn '\.degraded' argus/ --include=*.py | grep -v 'degraded='`
- **Output:** 1 hit, and it is generator.py:421 DOCSTRING saying 'no production code reads it back - filed as DF-10-4-B'
- **Finding:** Zero real production readers remain. The code's own docstring corroborates the entry.

### `DF-10-4-C`

- **Command:** `grep -rn 'grammar_load_failed' argus/index/ast_index.py | head`
- **Output:** token recorded; no exception-class detail persisted
- **Finding:** Story 10.4's DN-5 deliberately persists no exception detail. Unchanged.

### `DF-10-4-D`

- **Command:** `grep -n 'ls-files' argus/dogfood/partition_plan.py`
- **Output:** line 241 git ls-files -z (the INDEX)
- **Finding:** Population still moves on git add alone. Mechanism unchanged.

### `DF-11-2-A`

- **Command:** `see DF-11-2-B: _NO_CONVENTION_EXEMPTIONS still lists c and php`
- **Output:** c and php still exempt, still targeting 12.5
- **Finding:** No test-name convention was added for c or php. The entry's own close condition is 'jointly with DF-11-2-B', which is also open.

### `DF-11-2-B`

- **Command:** `grep -A6 _NO_CONVENTION_EXEMPTIONS tests/test_classification_word_boundary.py`
- **Output:** 'c' and 'php' both still registered exemptions, reasons still naming target 12.5
- **Finding:** Registered gap, not a fixed one - exactly as the entry says.

### `DF-11-4-A`

- **Command:** `sed -n '408,470p' argus/reports/generator.py`
- **Output:** 'if eligible: return []' still live at the trigger; docstring says 'The all-or-nothing trigger below is Story 12.5's, not this one's'
- **Finding:** Trigger unchanged and the code itself names 12.5 as the owner.

### `DF-12-1-A`

- **Command:** `wc -l < tests/test_pipeline_signature_demo.py`
- **Output:** 1326
- **Finding:** Exactly the claimed 1326. 126 over the 1200 cap. Carried by three consecutive stories; escalated to the Epic-12 retrospective.

### `DF-12-1-B`

- **Command:** `grep -n 'DF-12-1-B' tests/test_module_size_ceiling.py`
- **Output:** line 129 deferred_work_id="DF-12-1-B" - the exemption is still registered
- **Finding:** The size exemption this entry covers is still live in the ceiling guard.

### `DF-12-1-C`

- **Command:** `wc -l < tests/test_grammar_diagnosis.py`
- **Output:** 1203
- **Finding:** Exactly the claimed 1203. 3 over cap. Its own appended note already records target_story as NONE-unscheduled.

### `DF-12-2-C`

- **Command:** `wc -l < tests/test_v1_commitment_closure.py`
- **Output:** 1711
- **Finding:** ROW MOVED AND IN THE WRONG DIRECTION: entry recorded 1412 (212 over cap). Now 1711 - 511 over. The split 12.3 owns has grown by a further 299 lines since filing.

### `DF-12-2-D`

- **Command:** `grep -rn 'structured_output=()' argus/audit/open_llm_adapter.py`
- **Output:** lines 139, 166, 200 all construct structured_output=()
- **Finding:** [17-5 group] The 'delivered' branch is still unreachable through the shipped adapter. deep_pass.py:68's own docstring corroborates: 'back with structured_output == (), so it degrades as empty-response'.

### `DF-12-3-A`

- **Command:** `same adapter evidence as DF-12-2-D`
- **Output:** structured_output never populated
- **Finding:** [17-5 group] PRD 501's 'a re-run returns the recorded result' still undelivered for the DEEP component - it shares DF-12-2-D's root cause.

### `DF-12-7-B`

- **Command:** `grep -rn 'stale|out of date|outdated' argus/cli.py`
- **Output:** no hits
- **Finding:** Staleness of an installed command asset remains DETECTABLE but is still not DETECTED FOR the user - no surface tells them. Exactly the property the entry says Epic 13's expiry must choose.

### `DF-13-2-A`

- **Command:** `read adjudication-record.json`
- **Output:** 31 rows; dispositions FP=26 BORDERLINE=5; expert_hours_numerator/denominator = None/None
- **Finding:** ROW MOVED, PARTIALLY: the entry says '31 UNADJUDICATED rows' and they are now ADJUDICATED (26 FP, 5 BORDERLINE). But expert_hours is still NOT RECORDED (null, never zero) and the gate is still BLOCKED, which are the entry's other two clauses. Open on the unmoved half.

### `DF-14-1-A`

- **Command:** `grep -n 'mock_sites|_ast_corroborated' argus/detectors/vacuous_test.py`
- **Output:** vacuous_test.py:85 section 'Why fact (b) is not mock_sites >= 1'
- **Finding:** [17-5 group] The Story 14.1 CONFORMANCE fix landed, but the entry's actual claim - that fact (b) is a NAME-LEVEL proxy rather than dataflow provenance - is a recorded LIMIT that still stands. Real dataflow is DF-16-7-A's territory and also open.

### `DF-14-3-D`

- **Command:** `grep -n 'depth_supported|verdict_eligible' argus/detectors/vacuous_test.py`
- **Output:** advisory=True + depth_supported=None still the non-corroborated path (:52-54)
- **Finding:** No non-Python test can reach verdict-eligibility. Mechanism unchanged; the entry already established this is NOT caused by the split vocabulary.

### `DF-16-7-A`

- **Command:** `grep -n consumed argus/detectors/vacuous_test.py`
- **Output:** lines 119-121: requirement 3's 'no consumed SUT call' still whole-function scoped
- **Finding:** [17-5 group] Per-call observation analysis still needs real dataflow. Scope unchanged.

### `DF-16-7-B`

- **Command:** `read silent-class-record.json`
- **Output:** smoke_test_proportion measured=False, 0 of 36 assessed, proportion_numerator/denominator None
- **Finding:** [17-5 group] The silent class's true-positive proportion is still unmeasured - the record refuses to report 0/36 rather than measuring it (AI-E11-1).

### `DF-8-3-A`

- **Command:** `grep -rn 'critical_subsystems_all_deep' argus/reports/*.py`
- **Output:** 4 sites, ALL of the form 'if not verdict.critical_subsystems_all_deep'
- **Finding:** Only the NEGATIVE is surfaced. Neither human surface can still say the FR16 clause was satisfied VACUOUSLY - i.e. that the eligibility filter emptied the critical set. Story 8.3's D5 declined it deliberately; unchanged.

### `DF-AUD-APAA-A`

- **Command:** `grep -rn 'MemoStore(|derive_cache_key(|invalidate_rejections(' argus/ --include=*.py | grep -v '^argus/cache/'`
- **Output:** no hits - zero production callers outside the package
- **Finding:** The cache sub-package is still ORPHAN relative to run_audit/CLI. The entry's own status line already says 'OPEN, owned'.

### `DF-AUD-APAA-C`

- **Command:** `ls .github/workflows/; CI state per story 19.6 s0.0`
- **Output:** audit-ci.yml present; CI has never run on this branch (Actions outage from 2026-08-26 15:11:58 UTC)
- **Finding:** A release status asserted over a gate that never executed. Still unverified by CI - and the SAME condition is live again today, which is why AI-E17-3 remains open.

### `DF-INV-VACUOUS-A`

- **Command:** `read silent-class-record.json`
- **Output:** class_size 36, rule_id vacuous_test_heuristic, proportion NOT MEASURED
- **Finding:** [17-5 group] Flagging and corroboration are still graded on different definitions and the intersection is still empty.

