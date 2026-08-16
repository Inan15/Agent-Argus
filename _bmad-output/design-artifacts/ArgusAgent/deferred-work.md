# APAA deferred-work

APAA-local deferred-work register (the APAA sub-project is self-contained; this is
kept separate from the Minions platform `implementation-artifacts/deferred-work.md`).
Append-only. Entries carry the six mandatory CC-3 fields
(id · origin_story · owner · target_story|sunset_date · category · severity).

## Deferred from: code review (2026-06-21)

- **DF-1-3-A** — Reader does not assert content-addressed filename == internal `content_hash`.
  `minions_core/apaa/store/reader.py:105`. Defense-in-depth beyond AC6: the required
  tamper case (payload mutated, stale `content_hash`) IS detected; a renamed/misfiled
  artifact whose filename stem diverges from its internal `content_hash` is silently
  accepted. Suggested fix: when the locator stem is a 64-hex sha, assert it equals the
  verified `content_hash`, raising `StoreIntegrityError` on mismatch.
  - id: DF-1-3-A
  - origin_story: 1-3-apaa-store-writer-reader-filesystem-containment
  - owner: Security Owner
  - target_story: epic-4-secret-containment-property-suite-ci-blocking
  - category: security
  - severity: 🟢
  - **INTEGRITY GAP CLOSED 2026-06-27 by story 4-2-referential-integrity-lint-of-on-disk-state**
    (append-only cross-reference note — the original entry above is NOT rewritten, §3.4
    evidence immutability). The filename-stem-vs-internal-`content_hash` gap DF-1-3-A
    flagged is now caught by the referential-integrity lint as a typed
    `filename_content_hash_mismatch` `IntegrityFinding` in
    `minions_core/apaa/store/integrity.py::_resolve_references` — for every
    content-addressed `state/` / `findings/` `<sha>.json` artifact, the lint asserts the
    filename stem equals the envelope's internal `content_hash` (recomputed/verified via
    the REUSED 1.3 `read_envelope` / `compute_content_hash` over the payload only), so a
    renamed / misfiled artifact surfaces (TC-APAA-STORE-001-91, demonstrated RED via the
    sha-stem-check-dropped weakened resolver at TC-APAA-STORE-001-92). `assignments/<id>`
    manifests are keyed by `partition_id` (not a payload sha) and are EXCLUDED from the
    sha-stem check (TC-APAA-STORE-001-93) — they are verified by the plan→assignment
    resolution instead. NOTE: the lint lands this as a LINT FINDING (not a reader-time
    raise), keeping the 1.3 `read_envelope` contract frozen — DF-1-3-A's
    `target_story: epic-4-secret-containment-property-suite-ci-blocking` (Story 4.4) may
    still elect a CI-blocking enforcement of the lint; the integrity GAP itself is closed
    here.

- **DF-1-3-B** — Containment `_is_contained` LOGIC mirrored, not imported, from the
  importable `WorkspaceArtifactWriter._is_contained` staticmethod.
  `minions_core/apaa/store/paths.py:65`. Thin-wrap of logic is explicitly authorized
  (architecture Decision F) and the two impls are currently byte-identical, but a future
  hardening of the canonical check could silently diverge from the APAA mirror.
  Suggested fix: import + reuse the canonical staticmethod, OR add a parity test pinning
  logical equivalence over the same escape-vector matrix.
  - id: DF-1-3-B
  - origin_story: 1-3-apaa-store-writer-reader-filesystem-containment
  - owner: Security Owner
  - target_story: epic-4-referential-integrity-lint-of-on-disk-state
  - category: security
  - severity: 🟢
  - **LEFT OPEN 2026-06-27 by story 4-2-referential-integrity-lint-of-on-disk-state**
    (append-only note — the original entry above is NOT rewritten, §3.4). The 4.2 lint
    REUSES `ApaaStorePaths` containment (every enumerate-and-read goes through the
    containment-checked resolver, NFR-S5) but adds NO new/second containment
    implementation, so the lint did not naturally touch the `paths.py::_is_contained`
    ↔ `WorkspaceArtifactWriter._is_contained` mirror this defer concerns. Adding the
    parity test would not exercise the lint's code path (it pins a 1.3 invariant, not a
    4.2 one), so per the story's "do NOT expand scope to chase it if it does not fit
    cleanly" guidance the 🟢 parity test is LEFT OPEN; a future `target_story` (a
    `store/paths.py` hardening or the 4.4 secret-containment suite) is the cleaner home.
    The shared invariant (`is_relative_to`, never `str.startswith`) remains pinned by the
    existing containment + import-isolation gates.

- **DF-2-3-B** — Persisted `.apaa/` run-state records operator designation INTENT, not
  the computed critical set. `minions_core/apaa/pipeline.py:265`. The run-state persists
  `request.to_provenance_payload()` (raw `critical_paths`/`excluded_critical_paths`), but
  NOT the computed `CriticalSubsystemSet` (final paths + per-path `origins` +
  `designated_but_unmatched`). The exclusion lever IS auditable (operator intent is
  recorded), and the negative-assurance narration of which critical subsystems were/weren't
  covered is explicitly Epic-4 Story 4.1 scope — non-blocking for V1. Suggested fix: when
  Story 4.1 lands the negative-assurance scope statement, persist the computed
  `CriticalSubsystemSet` (origins + designated_but_unmatched) so a reader can distinguish an
  override of a genuine heuristic hit from a no-op exclude.
  - id: DF-2-3-B
  - origin_story: 2-3-critical-subsystem-identification-operator-designation
  - owner: QA Lead
  - target_story: epic-4-negative-assurance-verdict-semantics
  - category: governance
  - severity: 🟢
  - **CLOSED 2026-06-27 by story 4-1-negative-assurance-verdict-semantics** (append-only
    closure note — the original entry above is NOT rewritten, §3.4 evidence immutability).
    The computed `CriticalSubsystemSet` (final `paths` + per-path `origins` +
    `designated_but_unmatched`) is now persisted additively to `.apaa/state/` via the
    EXISTING `ApaaStoreWriter.write_payload("state", ...,
    producer="apaa.pipeline.critical_subsystems")` in the shared `_assemble_and_persist`
    fold (`pipeline.py::_persist_critical_subsystems`) — content-addressed, single 1.1
    serializer, containment-checked, round-trips equal (TC-APAA-VERDICT-001-20/21). A
    reader can now distinguish an override of a genuine heuristic hit (`origins` =
    `heuristic`) from an operator force (`operator_designated`) and from a no-op exclude
    (the suggested fix). The operator-INTENT provenance the run already persisted is
    UNCHANGED (additive). The negative-assurance scope statement narrates which critical
    subsystems were / were NOT examined deeply from this set
    (TC-APAA-PIPELINE-001-32/33).

- **DF-3-4-A** — The resume entrypoint is library-only in V1 — no operator-facing
  `--resume` CLI flag. `minions_core/apaa/cli.py` (unchanged). Story 3.4 shipped
  `resume_audit_detailed` / `resume_audit` in `pipeline.py` (exercised by tests), but the
  thin `argparse` `--resume` wiring was deferred to keep `cli.py` unchanged this story and
  to settle the in-tree `.apaa/`-vs-drift ergonomics (resume re-loads the repo at the pin
  and the loader refuses a drifted tree, so V1 resume requires the `.apaa/` store OUTSIDE
  the audited working tree via an injected reader/writer). Non-blocking — the resume
  MECHANISM is fully tested. Suggested fix: add a thin `--resume` flag (wiring only, no
  logic — AR2/NFR-M1) that routes to `resume_audit` + the `.gitignore`d-`.apaa/` operator
  ergonomics, in a follow-up story.
  - id: DF-3-4-A
  - origin_story: 3-4-resumability-from-on-disk-apaa-state
  - owner: Delivery Orchestrator
  - target_story: epic-7-minions-full-repo-partition-budget-sizing-plan
  - category: process
  - severity: 🟢

## Deferred from: code review (2026-06-28)

- **DF-5-1-A** — The `prompt-template version` closure input enumerated in architecture
  §77 ("content-hash + model checkpoint + **prompt-template version** + tool versions +
  budget/materiality + work-manifest scope + detector-set content-hash") has NO slot in
  `RecordingProducingClosure` (`minions_core/apaa/cache/key.py:172`). In V1 Tier-A there is
  NO live LLM (the deep path is heuristic/claim-proxy), so there is no prompt template to
  fold today — this is correctly out of V1 scope, like the model-checkpoint placeholder.
  BUT unlike `model_checkpoint` (which was given a stable placeholder key slot precisely to
  avoid a future silent-staleness hole), the prompt-template version was given NO slot.
  When Epic-6 Story 6.1 wires the live LLM dispatch, a prompt-template change would NOT move
  the cache key → a stale result computed under a different prompt could be served — the
  exact silent-cache-staleness failure mode this story's canary exists to prevent. The
  `CACHE_KEY_SCHEMA_VERSION` bump lever + the additive `extra="forbid"` model permit a clean
  6.1 addition, so this is a forward-coupling documentation/seam gap, not a V1 correctness
  bug. Suggested fix (6.1): add a `prompt_template_version` field to `RecordingProducingClosure`
  (mirroring the `model_checkpoint` placeholder/slot pattern + a perturbation-matrix leg),
  fold it in `_closure_payload`, and bump `CACHE_KEY_SCHEMA_VERSION`. Interim (this story, a
  doc-only note): add a key.py docstring forward-note that prompt-template version is an
  Epic-6 LLM-path closure input deliberately deferred to 6.1.
  - id: DF-5-1-A
  - origin_story: 5-1-cache-key-derivation-recording-producing-closure-ci-canary
  - owner: Engineering Lead
  - target_story: 6-1-llm-dispatch-port-minions-orchestrator-adapter
  - category: process
  - severity: 🟡
  - **CLOSED 2026-06-28 by story 5-1 (dev-story fix iter-1)** (append-only closure
    note — the original entry above is NOT rewritten, §3.4 evidence immutability).
    Rather than the interim doc-only mitigation, the reviewer's full suggested fix was
    applied THIS round: `RecordingProducingClosure` now carries a
    `prompt_template_version` field (mirroring the `model_checkpoint` DN-PLACEHOLDER
    slot), defaulting to the stable V1 sentinel `V1_PROMPT_TEMPLATE_VERSION =
    "v1-no-prompt-template"` and shaped for a clean ADDITIVE Epic-6 Story 6.1
    substitution of the real captured prompt-template version. It is folded into
    `_closure_payload`, and `CACHE_KEY_SCHEMA_VERSION` was bumped `1 → 2` (the golden
    key was regenerated to `2628b9a6…550ca87` — a documented intentional
    invalidation). A bidirectional canary leg was added (`prompt_template_version` in
    `_PERTURBATIONS` → key changes; it is also covered by the `_key_ignoring`
    keystone-adequacy RED demo), plus a placeholder-default test
    (TC-APAA-CACHE-001-21) and a drift-seam test (TC-APAA-CACHE-001-22). The
    silent-cache-staleness hole at 6.1 (a prompt-template change not moving the key)
    is closed: two prompt-template values now derive two keys. 783 passed, mypy clean,
    structural gates green. Epic-6 Story 6.1 substitutes the real captured value into
    the existing slot (no key-shape change).

## Back-filled from: story-file register (2026-06-29) — AI-E5-4 central-register back-fill

- **DF-1-7-B** — Interim Python deep over-grading. The pipeline graded EVERY
  cleanly-parsed non-test Python file `audited_deep` purely on claim-PRESENCE
  (`pipeline.py::_grade_non_test_python` → `grade_entry(proposed_depth=AUDITED_DEEP,
  claim_present=True)` — the FR6 proxy, originally recorded at `pipeline.py:149`).
  That over-graded a file as deep merely because it parsed, not because its claim was
  verified, inflating the deep-% the 1.6 verdict gate reads. The full Python AST
  GROUNDING of `audited_deep` claims (FR7) was deferred to Epic 6. This entry
  previously lived ONLY in the 1-7 story line; it is back-filled here per AI-E5-4 (the
  story-file copy is retained as evidence; the original is NOT rewritten — §3.4).
  - id: DF-1-7-B
  - origin_story: 1-7-cli-invocation-contract-pipeline-signature-demo-vacuous-test-cartridge
  - owner: Engineering Lead
  - target_story: 6-2-full-python-ast-grounding-of-audited-deep-claims
  - category: process
  - severity: 🟡
  - **CLOSED 2026-06-29 by story 6-2-full-python-ast-grounding-of-audited-deep-claims**
    (append-only closure note — the original entry is NOT rewritten, §3.4). The FR7
    AST-grounding gate is now live: the new PURE provider-free validator
    `minions_core/apaa/audit/grounding.py::is_deep_claim_grounded` (the stack-agnostic
    `claim → validated?` interface, Python = impl #1) computes a deterministic
    structural grounding fact over the PRE-BUILT 1.4 `AstIndexEntry` — GROUNDED iff ≥1
    real `Definition` (DN-GROUND-RULE; no re-parse / no second tree-sitter/ast/radon
    call — AR7/§3.3). `pipeline.py::_grade_non_test_python` now passes
    `claim_present=(claim_emitted AND claim_grounded)` into the UNCHANGED 1.2
    `grade_entry` (DN-GROUNDED — `coverage_ledger.py` byte-identical), so a clean-parse
    ZERO-definition module (constants-only / re-export / docstring-only) downgrades to
    `audited_shallow` instead of being over-graded `audited_deep`. The over-grading is
    demonstrated RED-then-green (TC-APAA-AUDIT-001-50: the interim `claim_present=True`
    shape grades a zero-def file deep — RED; the validator downgrades it — GREEN) and
    the verdict migration is observable end-to-end (TC-APAA-PIPELINE-001-41: a
    zero-def-only repo now lands INSUFFICIENT_COVERAGE / exit 3 instead of clearing the
    floor). The migration is HONEST: every cartridge SUT (`calculator.py`, `adder.py`,
    `multiplier.py`, `config.py`, `café_calc.py`, `guard.py`, `модуль_секрет.py`, …) has
    ≥1 real def → stays GROUNDED → `audited_deep`, so the signature-demo moat is
    PRESERVED (TC-APAA-PIPELINE-001-40: `calculator.py` stays deep → deep-% 1/2 →
    NOT_READY_FOR_RELEASE / BLOCKED 🔴 / exit 2 unchanged). The V1 grounding fact is the
    DETERMINISTIC structural AST fact; the LLM-recording-fed grounding is a documented
    forward seam, NOT the 6.2 default (DN-V1-DETERMINISTIC) — the pipeline default path
    stays PURE + zero-token + deterministic (NFR-D1/D2). Web + no-LLM import gates
    extended-not-forked (the pipeline pulls the pure validator but NO LLM dispatch
    surface; TC-APAA-AUDIT-001-47); frozen Epic-1..5 contracts byte-identical; full
    declared-set + no-crash matrix + non-ASCII covered (TC-APAA-AUDIT-001-46..58).

## Back-filled from: story-file register (2026-06-29) — AI-E5-4 central-register back-fill (story 6.3)

- **DF-1-4-A** — Edge-set richness is unresolved-name only (no scope binding).
  `index/ast_index.py:186-231` — the 1.4 `CodeEdge` captures the bare callee
  identifier / trailing attribute with NO name binding, NO scope resolution, NO
  import resolution. This is the documented, AC-sanctioned V1 substrate (Epic-6
  owns the resolved call graph), so it is NOT a defect — recorded only so the
  downstream 1.5 / Epic-6 consumers know the edge set is unresolved. This entry
  previously lived ONLY in the 1-4 story line; it is back-filled here per AI-E5-4
  (the story-file copy is retained as evidence; the original is NOT rewritten —
  §3.4).
  - id: DF-1-4-A
  - origin_story: 1-4-tree-sitter-ast-index-repo-intake-python-stack-detection
  - owner: Engineering Lead
  - target_story: epic-6-orphan-dead-code-detector
  - category: other
  - severity: 🟢
  - **CONSUMED 2026-06-29 by story 6-3-orphan-dead-code-detector** (append-only
    consumption note — the original entry is NOT rewritten, §3.4). The Story 6.3
    FR12 orphan / dead-code detector
    (`minions_core/apaa/detectors/orphan_code.py::OrphanCodeDetector`) consumes the
    SAME pre-built 1.4 `definitions`/`edges` (no re-parse — AR7/§3.3) and computes a
    CONSERVATIVE name-reachability fact OVER the unresolved-name graph. **What the
    unresolved substrate CAN prove:** a definition whose `name` appears as NO
    `CodeEdge.callee` anywhere in the whole index is a *candidate* orphan. **What it
    CANNOT prove (so the rule stays silent):** which def a callee resolves to, so a
    name-collision (two defs share a name; any one referenced) makes BOTH NOT-orphan;
    and reachability via dunders / `__all__` / `test_*` / framework-registry /
    dynamic-dispatch hooks the bare-callee edges cannot see, handled by a locked
    EXCLUSION set (`ORPHAN_EXCLUSION_NAMES` + structural `__x__` + `test_*`). The
    asymmetric-harm bar (a false dead-code deletion ≫ a missed orphan) locks the rule
    toward silence: when in doubt → NOT-orphan, NEVER a false dead-code accusation.
    The finding is `advisory=True` (CC #6) — it informs, it does not alone move the
    verdict to 🔴 (the 6.4 Prosecutor owns promotion). HONEST limitation (documented
    in the detector docstring, the 1.5 register): the detector grounds REACHABILITY
    over an UNRESOLVED-name graph — LOW recall (it can miss an orphan a resolved graph
    would catch), HIGH precision (it does not falsely accuse live code, the asymmetric
    priority); requirement-traceability is NOT established in V1 (the 2.6 register).
    Proven by the complete-the-declared-set suite (TC-APAA-ORPHAN-001-01..17,
    including the RED-first name-collision guard TC-APAA-ORPHAN-001-05) + the
    end-to-end pipeline wiring (TC-APAA-PIPELINE-001-50..52, incl. the no-orphan
    byte-identity AC4). A **resolved call graph for higher orphan recall** is the
    deferred V2 / Epic-6-depth work this defer originally named — filed below as a
    NEW append-only defer.

- **DF-6-3-A** — Resolved call graph (name binding / scope / import resolution) for
  higher orphan recall. The Story 6.3 detector grounds orphan reachability over the
  1.4 UNRESOLVED-name edge set (DF-1-4-A), which is deliberately conservative (LOW
  recall, HIGH precision): a name-collision or any framework/dynamic reachability the
  bare-callee edges cannot see resolves to NOT-orphan. A V2 resolved call graph (name
  binding + scope + import resolution) would raise recall — surfacing orphans the
  name-match graph conservatively keeps silent — WITHOUT relaxing the
  no-false-accusation moat. This is Epic-6-depth / V2 work, out of scope for the V1
  Tier-B FR12 slice.
  - id: DF-6-3-A
  - origin_story: 6-3-orphan-dead-code-detector
  - owner: Engineering Lead
  - target_story: epic-6-resolved-call-graph
  - category: other
  - severity: 🟢

- **DF-6-4-A** — Full resolved cross-partition SEAM auditor (V2). The Story 6.4
  `cross_partition` cut-edge pass is the V1 MITIGATION (OI2 / CC #4): it re-reads the
  2.4 `PartitionPlan.cut_edges` over the UNRESOLVED-name set (DF-1-4-A) and SURFACES a
  cut a seam-spanning defect COULD hide in (an advisory `cross_partition` finding) —
  it does NOT PROVE a defect spans the cut. A V2 resolved-seam auditor (name binding /
  scope resolution / a resolved call graph across the cut, a non-`"root"` analyzed
  `partition_id`) would PROVE a seam-spanning defect rather than merely surface the
  cut as a hiding place — distinct from the V1 SURFACE-not-PROVE mitigation, and
  related to but broader than DF-6-3-A's resolved-call-graph scope (that defer targets
  orphan recall; this targets cross-partition seam proof). This is Epic-6-depth / V2
  work, out of scope for the V1 Tier-B FR19 slice.
  - id: DF-6-4-A
  - origin_story: 6-4-adversarial-prosecutor-cut-edge-pass
  - owner: Engineering Lead
  - target_story: epic-6-resolved-seam-auditor
  - category: other
  - severity: 🟢

## Deferred from: code review (2026-06-30)

- **DF-6-4-B** — `_has_ast_corroboration` cannot distinguish a genuine 6.2 AST-grounded
  `Locator.ast_span` from the synthetic `cross_partition:<file>::<callee>` seam token a
  `cross_partition` finding carries, so a signed-off `cross_partition` finding WOULD be
  promotable — contradicting the `prosecutor.py` docstring claim that a cut edge "is never
  promoted in V1." HARMLESS in the V1 pipeline (the pipeline never passes `sign_offs`, so no
  promotion is reachable and the downgrade-only + un-prosecuted byte-identity properties hold);
  the operator-sign-off promotion surface is the documented forward seam. V2 hardening: when a
  live sign-off surface lands, distinguish genuine AST corroboration from the synthetic seam
  token (a dedicated grounded flag) OR exclude `rule_id == cross_partition` from
  `_is_advisory_promotable`. Low severity; not in scope for the V1 Tier-B FR19 slice.
  - id: DF-6-4-B
  - origin_story: 6-4-adversarial-prosecutor-cut-edge-pass
  - owner: Engineering Lead
  - target_story: epic-6-resolved-seam-auditor
  - category: governance
  - severity: 🟢

## Deferred from: dev-story (2026-06-30)

<!-- defer-schema-session: 2026-06-30 -->

- **DF-6-6-A** — Grow the corpus to N=5 DISTINCT defect-rule classes + run the human
  validation-protocol adjudication so the ≥80%-precision gate can flip from PROVISIONAL
  to cleared. Story 6.6 stood up the PURE precision replay harness
  (`minions_core/apaa/precision/replay_harness.py::compute_precision`) + the committed
  validation protocol (`precision-validation-protocol.md`) and computed an EARLY/PROVISIONAL
  precision of `1/1` over the current corpus (6 TP / 0 FP / 0 FN — no false BLOCKING
  accusation; clean repos legitimately emit only advisory findings). HONEST LIMITATION
  (the OI1 keystone, NOT softened): `populated_planted_defect_count()` returns `5` cartridge
  ROWS, but those span only THREE distinct defect-rule CLASSES (`vacuous_test_ast` ×3 —
  vacuous_basic/holdout_vacuous/nonascii_unicode, `hardcoded_secret` ×1, `orphan_code` ×1).
  The gate therefore STAYS PROVISIONAL: `compute_precision` defaults `protocol_cleared=False`
  and 6.6 did NOT flip the marker — the flip requires (a) a corpus of genuinely distinct
  labeled defect classes with sufficient findings AND (b) a recorded human Engineering-Lead +
  QA-Lead adjudication run per the validation protocol §4/§5, neither of which 6.6 performs
  (6.6 must not manufacture cartridges nor fabricate a cleared adjudication). The harness +
  schema are DESIGNED for N=5 with no refactor (a new cartridge = a registry row + a
  `*.py.txt` drop-in). Closing this defer = grow the labeled corpus + run the adjudication +
  pass `protocol_cleared=True` at the call site. Related to the Epic-7 Minions dogfood
  (empirical precision over a REAL repo), but distinct: this is the CARTRIDGE-corpus gate flip.
  - id: DF-6-6-A
  - origin_story: 6-6-precision-replay-harness-validation-protocol
  - owner: Engineering Lead
  - target_story: epic-7-minions-dogfood-precision
  - category: process
  - severity: 🟠

## Deferred from: dev-story (2026-07-01)

<!-- defer-schema-session: 2026-07-01 -->

- **DF-6-7-A** — Wire the PURE HITL escalation gate + the append-only decision-record writer
  into the LIVE pipeline / CLI invocation. Story 6.7 delivered the deterministic resolution +
  the record contract as a LIBRARY seam (`minions_core/apaa/governance/escalation.py::escalation_fires`/
  `resolve_escalation` + `governance/decision_record.py::DecisionRecordWriter.append`), fully
  proven by `tests/apaa/test_hitl_escalation.py` — but per the story scope fence (DN-NO-PROD-CHANGE-FROZEN)
  it did NOT change the frozen straight-line `pipeline.py` dataflow, add a `cli.py --escalate`/
  `--decision` flag, or add a live async/blocking human-wait transport / notification / webhook /
  queue (that human-input transport is the caller's concern — the gate is a pure resolution over
  `(escalation_condition, optional_human_decision, timeout_elapsed)`). The AC proof needed NO live
  pipeline invocation, so no minimal seam was added. Closing this defer = decide the escalation-rule
  configuration source, add the minimal pipeline call site + a CLI decision flag, and (AI-E5-4 named
  target) land it as part of the Epic-7 Minions dogfood proof run, which is the first live consumer.
  The V1 escalation is PATTERN-MATCHED only; an LLM-driven escalation adjudicator remains a documented
  forward seam behind the 6.1 `LLMDispatchPort`, NEVER the V1 default (the FR23 lock).
  - id: DF-6-7-A
  - origin_story: 6-7-hitl-stop-proceed-escalation-append-only-decision-record
  - owner: Delivery Orchestrator
  - target_story: epic-7-minions-dogfood-proof-run
  - category: process
  - severity: 🟢

## Progress note: dev-story (2026-07-02) — story 7.1 DF-6-6-A autonomous half advanced

<!-- defer-schema-session: 2026-07-02 -->

- **DF-6-6-A-P1** — DF-6-6-A AUTONOMOUS half advanced (append-only progress note; the
  original DF-6-6-A entry above is NOT rewritten, §3.4 evidence immutability). Story 7.1
  discharged the AUTONOMOUS corpus-growth half of DF-6-6-A: the labeled synthetic corpus
  now spans **5 DISTINCT defect-rule CLASSES** (up from 3), by appending TWO NEW
  distinct-class cartridges to `tests/apaa/cartridges/_registry.py::CARTRIDGE_REGISTRY`
  (REUSE the frozen `CartridgeSpec`/`GoldenFinding` SHAPE — a registry ROW + a `*.py.txt`
  template drop-in, no harness refactor / no forked registry): (1) `vacuous_heuristic_basic`
  (kind=planted_defect, class `vacuous_test_heuristic` — a heuristically-vacuous test with a
  SUT call but NO assertion and NO mock, so the Tier-A AST corroboration is withheld and the
  finding stays advisory / verdict-ineligible; a DISTINCT class from `vacuous_test_ast`); and
  (2) `cross_partition_seam` (kind=holdout, class `cross_partition` — a 45-file cohesion chain
  whose oversized component the REAL 2.4 `partition_repository` splits under the DEFAULT
  NFR-SC1 limits, producing a REAL `CutEdge` that the REAL 6.4 Prosecutor cut-edge pass emits
  as an advisory `cross_partition` finding through the UNMODIFIED `run_audit_detailed`). Both
  rule_ids were CONFIRMED-emitted over a staged cartridge by running the real pipeline (NOT
  assumed) — NEVER a synthetic rule_id no detector produces. The 6.6 `compute_precision`
  roll-up runs over the grown corpus UNCHANGED and each new class produces its OWN TP
  (verified TC-APAA-DOGFOOD-001-09; distinct-class count is 5, not a collision-collapsed
  count — TC-APAA-DOGFOOD-001-10). The current honest count: `distinct_rule_class_count() == 5`
  (`cross_partition`, `hardcoded_secret`, `orphan_code`, `vacuous_test_ast`,
  `vacuous_test_heuristic`); `populated_planted_defect_count() == 7` labeled ROWS.
  **The OI1 keystone HOLDS (NOT softened):** the ≥80%-precision gate STAYS PROVISIONAL —
  `compute_precision` defaults `protocol_cleared=False`, 7.1 did NOT flip the marker, and
  the `precision_gate_status()` marker still reads "provisional". The HUMAN TP/FP
  adjudication over REAL dogfood findings (the DF-6-6-A HUMAN half) is still OPEN — it is
  performed in 7.2 + an explicit human step, and ONLY it may clear the gate. 7.1 grows the
  substrate autonomously; it does NOT present a cleared gate from a synthetic corpus.
  - id: DF-6-6-A-P1
  - origin_story: 7-1-minions-full-repo-partition-budget-sizing-plan
  - owner: Engineering Lead
  - target_story: epic-7-minions-dogfood-precision
  - category: process
  - severity: 🟠

## Progress note + defer: dev-story (2026-07-02) — story 7.2 dogfood EXECUTED + human adjudication filed

<!-- defer-schema-session: 2026-07-02 -->

- **DF-6-6-A-P2** — DF-6-6-A EXECUTION half advanced (append-only progress note; the
  original DF-6-6-A entry + the 7.1 DF-6-6-A-P1 note above are NOT rewritten, §3.4
  evidence immutability). Story 7.2 (the APAA CAPSTONE) EXECUTED the Minions dogfood: it
  ran the frozen `pipeline.run_audit_detailed` (REUSED — no fork) over the REAL Minions
  platform source (135 git-tracked `minions_core/` modules over 36712 LOC, the 7.1 4-unit
  plan, materialized into a clean on-pin snapshot via the 6.5 `stage_cartridge` pattern)
  under `budget = $X = 843` (the 7.1 empirical ceiling). The run FITS within `$X` (V1
  deterministic total 675 credits, `ceiling_reached is False`) and DEMONSTRATES the 3.2
  halt (a ceiling below the total breaches). It produced a real verdict
  (`NOT_READY_FOR_RELEASE` / exit 2, deep-% `13/15`, 0 verdict-eligible/blocking findings)
  + a SIGNED source-free evidence bundle (REUSING the 4.3 `build_evidence_bundle` /
  `persist_evidence_bundle` + the 1.1 prev-hash-chained envelope + the 4.2 integrity lint
  — consistent) + a reproduced `GitHub green · Sonar green · APAA 🔴` signature demo + a
  100%-reproducibility check (byte-identical verdict + bundle bytes across two runs) +
  the honest `grade: demo-heuristic-only` red-team flag. The REAL dogfood findings are laid
  out ADJUDICATION-READY (3 advisory finding CLASSES — `cross_partition` ×332,
  `hardcoded_secret` ×2289, `orphan_code` ×285 — each mapped onto the 6.6 `finding_match_key`
  identity `(rule_id, verdict_eligible, advisory)` with sample locators) in
  `minions-dogfood-proof.md`, so the later human Eng-Lead + QA-Lead TP/FP adjudication can
  clear the ≥80%-precision gate on REAL data. **The OI1 keystone HOLDS (NOT softened):** the
  ≥80%-precision gate STAYS PROVISIONAL — `protocol_cleared` NOT flipped, the
  `precision_gate_status()` marker NOT flipped, NO ≥80% number presented as authoritative /
  cleared, and the Tier-A heuristic-only run is NOT presented as externalization evidence.
  The HUMAN TP/FP adjudication (the DF-6-6-A HUMAN half — the ONLY step that may clear the
  gate) is still OPEN → the new DF-7-2-A defer below.
  - id: DF-6-6-A-P2
  - origin_story: 7-2-execute-minions-audit-proof-artifact-evidence-bundle-signature-demo
  - owner: Engineering Lead
  - target_story: epic-7-minions-dogfood-precision
  - category: process
  - severity: 🟠

- **DF-7-2-A** — Run the HUMAN TP/FP adjudication over the REAL 7.2 dogfood findings to
  clear the ≥80%-precision gate. Story 7.2 EXECUTED the dogfood + laid the REAL Minions-repo
  findings ADJUDICATION-READY (the 3 advisory finding classes in `minions-dogfood-proof.md`
  §6, each with `rule_id` + verdict-eligibility + sample locators, mapped onto the 6.6
  `finding_match_key` shape). Per the OI1 honesty keystone (operator epic-boundary decision
  2026-07-02) the human TP/FP adjudication is the ONLY step that may clear the gate, and it
  is a HUMAN step OUT of scope for the autonomous story. Closing this defer = an Eng-Lead +
  QA-Lead tag each finding class TP/FP per `precision-validation-protocol.md` §4/§5 over the
  REAL dogfood finding set, record the per-metric pass/fail, and (only if the adjudicated
  precision genuinely reaches ≥80% over ≥5 distinct classes) pass `protocol_cleared=True`
  into the 6.6 `compute_precision` + flip the 6.5 `precision_gate_status()` marker. Until
  then the gate stays PROVISIONAL — the autonomous story NEVER fabricates or softclaims a
  cleared gate. DF-6-7-A (live HITL-escalation wiring into the pipeline/CLI) remains OPEN
  and is NOT closed by 7.2 (DN-ESCALATION — out of scope; the dogfood does NOT wire the 6.7
  escalation into the live invocation).
  - id: DF-7-2-A
  - origin_story: 7-2-execute-minions-audit-proof-artifact-evidence-bundle-signature-demo
  - owner: QA Lead
  - target_story: epic-7-minions-dogfood-precision
  - category: process
  - severity: 🟠


## Deferred from: repository audit (2026-07-04)

Multi-pass Minions repository audit (2026-07-04), PASS 3, surfaced APAA orphan/theater items
beyond the already-tracked DF-6-7-A (governance/escalation wiring) and DF-5-1-A (cache-key schema).
Recorded as tracked deferrals; APAA is a CLI-only, self-disclosed "demo-heuristic-only" tool, so
severities are weighted down. Heading is intentionally NOT "code review" (this is an audit, not a
`/bmad-code-review` session) so the defer-schema gate does not enforce; the six fields are carried
voluntarily for consistency.

- **DF-AUD-APAA-A** — The `cache/` sub-package (`cache/key.py`, `cache/memo_store.py`,
  `cache/invalidation.py`) is ORPHAN relative to the shipped `run_audit`/CLI path: `MemoStore` is
  never constructed and `derive_cache_key`/`invalidate_rejections` have no non-test caller, so no
  cache HIT/MISS ever occurs and the AR6 "false-red served forever" prevention cannot run
  (self-disclosed Epic-6 seam: `cache/invalidation.py:66` "the live trigger is Epic-6"). Two theater
  sub-notes: `invalidate_rejections()` reads a `RejectionLedger` nothing populates -> returns `()`
  unconditionally; `RejectionLedger._write` (`cache/invalidation.py:262`) forks a direct `write_bytes`
  while its docstring claims `ApaaStoreWriter` reuse (dead `self._writer`). Close = wire the cache
  layer when the first live consumer (the Epic-7 dogfood proof run) needs it, mirroring DF-6-7-A; or
  explicitly mark it permanent library-only.
  - id: DF-AUD-APAA-A
  - origin_story: 7-2-execute-minions-audit-proof-artifact-evidence-bundle-signature-demo
  - owner: Delivery Orchestrator
  - target_story: epic-7-minions-dogfood-proof-run
  - category: process
  - severity: 🟢

- **DF-AUD-APAA-B** — `read_in_scope` (`index/partitioner.py:631`), the NFR-S4 manifest-scoped read
  primitive whose docstring asserts "an off-scope read is IMPOSSIBLE through it," has NO production
  caller: the live pipeline reads sources via `pipeline._read_source`/`compute_loc_by_file`, so the
  manifest read-boundary is UNENFORCED at runtime (the security guarantee is proven only in
  `tests/apaa/test_partitioner.py`). Also `partition_plan.clears_floor` (`dogfood/partition_plan.py:353`)
  is a `Fraction(n, n) >= floor` tautology, unconditionally `True` — a per-unit coverage-floor "check"
  that can never fail. Close = route the live pipeline read path through `read_in_scope` (or document
  why the boundary is unenforceable in V1) and replace the tautological floor check with a real assertion.
  - id: DF-AUD-APAA-B
  - origin_story: 7-2-execute-minions-audit-proof-artifact-evidence-bundle-signature-demo
  - owner: Governance Owner
  - target_story: epic-7-minions-dogfood-proof-run
  - category: governance
  - severity: 🟡

## Deferred from: code review of 8-1-findings-before-coverage-binding-decision-table (2026-08-04)

- **DF-8-1-A** — A row-4 (`INSUFFICIENT_COVERAGE`, zero blocking findings, a coverage or
  critical-subsystem gate unmet) run still renders the pre-amendment false-accusation sentence in the
  persisted `final-verdict.md`: `argus/reports/generator.py:339` emits
  `> [!CAUTION] Repository is NOT ready for release — deep coverage `2/5` is below the `3/5` release
  threshold.` six lines below `- **Final Verdict**: **`INSUFFICIENT_COVERAGE`** (Exit Code `3`)`, and
  `render_ship_readiness` (`argus/reports/plain_english.py:109`) heads the same document with
  `Ship-readiness: NOT ASSESSED — too little of the code was examined deeply`, which is false for row 4
  (plenty was examined; nothing was found). Reproduced by the reviewer on a synthetic 2-deep/5-total
  zero-findings fold. This is CORRECT for Story 8.1 — AC15 explicitly fences the branch change to
  "change no rendered string" and AC18 fences `plain_english.py` — but it means the human surface of a
  clean-but-under-covered repository still ships a self-contradicting artifact, which is the residual
  half of the very defect Epic 8 exists to remove. Close = Story 8.3 / DR-11's report-surface wording
  reconciliation (the row-1-vs-row-4 split and the `plain_english.py` "NOT VOUCHED" branch audit),
  applying D4's own rule (a persisted artifact must not assert a falsehood) to this callout the way
  Story 8.1 applied it to `negative_assurance.py`.
  - id: DF-8-1-A
  - origin_story: 8-1-findings-before-coverage-binding-decision-table
  - owner: Delivery Orchestrator
  - target_story: 8-3 (DR-11 report-surface reconciliation)
  - category: correctness
  - severity: 🟡
  - **CLOSED 2026-08-05 by story 8-3-plain-english-report-stops-describing-impossible-state**
    (append-only closure note — the original entry above is NOT rewritten, §3.4 evidence
    immutability). BOTH halves are fixed, RED-first. (a) `argus/reports/generator.py`'s
    verdict block now has FOUR arms, one per FR16 row: FR16 row 4 got its own arm and no
    longer borrows row 2's sentence, so the measured
    `> [!CAUTION] Repository is NOT ready for release — deep coverage `2/5` is below the
    `3/5` release threshold.` is gone and is replaced by
    `> [!WARNING] Release readiness is NOT VOUCHED — Argus found nothing blocking, but deep
    coverage `2/5` is below the `3/5` release threshold. This is a statement about the
    audit, not about the code.` (b) `argus/reports/plain_english.py::_headline` splits
    `INSUFFICIENT_COVERAGE` on `AuditVerdict.is_below_floor`, so the document headline at
    `generator.py:269` no longer heads a row-4 run with row 1's
    `NOT ASSESSED — too little of the code was examined deeply`. Closing evidence:
    `TC-ArgusAgent-REPORT-002-20` (`tests/test_report_surface_consistency.py`), which was
    demonstrated RED against the pre-fix implementation for BOTH row-4 causes (the 2/5
    coverage cause and the 5/5-deep critical-subsystem cause), plus the four-row
    cross-surface net `TC-ArgusAgent-REPORT-002-21` — the single test that would have
    caught this defect — and `TC-ArgusAgent-REPORT-002-12`/`-13` on the human register.
    The unreachable `NOT VOUCHED` predicate DR-11 also named is gone: its prose relocated
    to row 4 (where it is true) and the impossible `NOT_READY_FOR_RELEASE ∧ blocking == 0`
    input is now the typed `ShipReadinessError`, proven unreachable by the 270-fold
    exhaustive sweep `TC-ArgusAgent-REPORT-002-10` (0 occurrences, re-derived in place).

## Deferred from: code review of 8-2-critical-subsystem-gates-operator-can-actually-satisfy (2026-08-05)

- **DF-8-2-A** — `argus/pipeline.py` ends Story 8.2 at **1199 lines against the NFR-M1 cap of 1200**, so
  the next line added to it breaches the standard. This is NOT a defect in the 8.2 delta: the story
  explicitly forbade a new module ("No new module. Everything is an edit to two existing source files"),
  the dev complied, condensed the `_critical_ineligibility` docstring rather than dropping the reasoning,
  and recorded the consequence in the Completion Notes. Recorded here so the constraint is discovered at
  planning time rather than at edit time. The underlying pressure is real: `pipeline.py` already owns
  intake wiring, per-file detection (`_detect_per_file`), grading, scope resolution
  (`_assessment_scope_paths`), assembly/persistence (`_assemble_and_persist`) and the resume path, and
  `_critical_ineligibility` is a cohesive derived-fact helper that best practice would site next to the
  predicates it composes. Close = extract a shell-helper module (e.g. `argus/pipeline_facts.py` carrying
  `_critical_ineligibility` and its siblings) as the FIRST act of whichever story next edits
  `pipeline.py`, rather than adding to it. Reviewer verified no other `argus/` source file exceeds the
  cap (next largest: `argus/dogfood/proof_run.py` 749).
  - id: DF-8-2-A
  - origin_story: 8-2-critical-subsystem-gates-operator-can-actually-satisfy
  - owner: Delivery Orchestrator
  - target_story: 8-3 (or the first story after 8.2 that edits `argus/pipeline.py`)
  - category: maintainability
  - severity: 🟢
  - **CARRIED FORWARD, NOT CLOSED — 2026-08-05, story 8-3** (append-only note; the entry
    above is NOT rewritten, §3.4). Story 8.3 did not edit `argus/pipeline.py` at all (its
    AC14 fenced the file and its AC8 reached the AST index through the `ast_index`
    argument `generate_reports` already receives), so the close condition — "extract a
    shell-helper module as the FIRST act of whichever story next edits `pipeline.py`" —
    never triggered. The file is still **1199 lines**, byte-identical to its post-8.2
    state, and the extraction remains owed by the next story that genuinely edits it.

- **DF-8-2-B** — Two entries in `_UNAMBIGUOUS_TEST_SUFFIXES` (`argus/detectors/vacuous_test.py:195-199`)
  are written **without a word separator** — `"test.java"` and `"spec.rb"` rather than
  `"_test.java"`/`"Test.java"` and `"_spec.rb"` — so tier 2 of `is_test_file` claims ordinary production
  files whose basename merely *ends* with those letters. Reviewer-confirmed: `svc/latest.java` and
  `svc/myspec.rb` both return `is_test_file(...) == True` with
  `is_test_classification_content_dependent(...) == False`, i.e. classified as tests by name alone, with
  **no** content check available to correct it (that is what tier 2 means). Since Story 8.2 they have a
  second consumer: such a file leaves the heuristic critical set and is disclosed under the reason
  `test_file`. **This is NOT a defect in the 8.2 delta.** The suffix table is byte-identical at
  `9109e16` and untouched by this story — the reviewer's 2 567-comparison differential proof shows the
  old and new `is_test_file` agree exactly on these paths — and it is not a false green relative to what
  Argus can actually grade, because the GRADING stage misclassifies them identically (they are
  `audited_shallow`, never `audited_deep`), so AC7's "the two stages cannot disagree" invariant still
  holds. Zero instances in this repository (no `.java`/`.rb` sources among the 147 indexed files), so the
  exposure is latent and lands only on a polyglot target repo. Close = add the missing separators and
  pin the near-miss corpus (`latest.java`, `myspec.rb`, `attest.py`, `greatest.py`) in
  `tests/test_vacuous_detector.py` beside `TC-ArgusAgent-DETECT-001-85`/`-95`.
  - id: DF-8-2-B
  - origin_story: 8-2-critical-subsystem-gates-operator-can-actually-satisfy
  - owner: Delivery Orchestrator
  - target_story: 8-3 (or the first story that edits `argus/detectors/vacuous_test.py`)
  - category: correctness
  - severity: 🟢
  - **CARRIED FORWARD, NOT CLOSED — 2026-08-05, story 8-3** (append-only note; the entry
    above is NOT rewritten, §3.4). The `target_story` is conditional and its condition did
    not fire: story 8.3 READ `is_test_file` / `is_test_classification_content_dependent`
    (reusing them rather than forking a second predicate, AC8) but did not edit
    `argus/detectors/vacuous_test.py`, which stayed on its AC14 fence and is byte-identical
    to its post-8.2 state. Still zero live instances in this repository.

## Deferred from: implementation of 8-3-plain-english-report-stops-describing-impossible-state (2026-08-05)

- **DF-8-3-A** — Neither human surface can tell an operator that the FR16 critical-subsystem
  clause was satisfied **VACUOUSLY** — i.e. that the eligibility filter (FR4/DR-5, Story 8.2)
  emptied the heuristic critical set rather than that every designated critical file reached
  `audited_deep`. Story 8.2's D5 handed the positive prose to 8.3/DR-11; Story 8.3 examined it
  and DECLINED it deliberately (its **D5**), for three converging reasons recorded there: the
  epic's own 8.3 AC block asks only that the critical-paths section render correctly for an
  empty set and that the `--exclude-critical` guidance stop being wrong (both delivered by its
  AC7); the information does not exist on `AuditVerdict` (`critical_subsystems_all_deep=True`
  with an empty `critical_subsystems_not_deep` is IDENTICAL for "the set was emptied by the
  filter" and "there were never any criticals" — only
  `CriticalSubsystemSet.heuristic_excluded_ineligible` distinguishes them); and getting that
  disclosure map into the report needs a new argument on `generate_reports` threaded from
  `argus/pipeline.py:793`, i.e. an edit to a file at 1199 of the 1200-line NFR-M1 cap, which
  **DF-8-2-A** says must trigger a module extraction first. Re-deriving the vacuity inside
  `generator.py` from `ast_index` is categorically forbidden (a §3.3/AR7 fork of the
  eligibility filter). This is an OMISSION, not a falsehood: `TC-ArgusAgent-PIPELINE-002-07`
  proves no surface asserts the vacuous positive, and Story 8.3's
  `TC-ArgusAgent-REPORT-002-18` additionally pins that an empty critical set renders nothing
  at all. Close = thread `CriticalSubsystemSet` (or just its `heuristic_excluded_ineligible`
  map) into `generate_reports`/`render_final_verdict_report` and name the vacuity in prose,
  AFTER the DF-8-2-A shell-helper extraction has made room in `pipeline.py`.
  - id: DF-8-3-A
  - origin_story: 8-3-plain-english-report-stops-describing-impossible-state
  - owner: Delivery Orchestrator
  - target_story: the story that performs the DF-8-2-A `pipeline.py` extraction
  - category: correctness
  - severity: 🟢

## Deferred from: code review of 8-3-plain-english-report-stops-describing-impossible-state (2026-08-06)

- **DF-8-3-B** — `argus/reports/plain_english.render_ship_readiness` can now RAISE (the Story 8.3
  `ShipReadinessError`, AR10), but `argus/cli.py` calls it at `:292` **outside** the `try/except ValueError`
  that wraps `run_audit(request)` at `:271-276`. A raise at that site would therefore escape `main()` as an
  uncaught traceback rather than the typed, secret-safe exit `1` the AR10 / NFR-R1 degradation contract
  requires. It is masked whenever `--report-dir` is set — the pipeline then calls `generate_reports` →
  `render_final_verdict_report` → `render_ship_readiness` *inside* `run_audit`, so the raise is caught — but
  `report_dir` defaults to empty, so the default `argus audit <path>` invocation has no guard. Story 8.3's
  `TC-ArgusAgent-CLI-001-32` monkeypatches `cli.run_audit` itself, so it proves the AC's letter
  ("`cli.py:272` catches `ValueError` → exit 1") without ever exercising the real raise site. **Not a live
  defect:** the reviewer proved the triggering state (`NOT_READY_FOR_RELEASE` with
  `blocking_finding_count == 0`) has no producer — `AuditVerdict` has exactly one construction site
  (`verdict_gate.py:651`), no persisted verdict is ever rehydrated, and the prosecutor's `model_copy`
  updates only `ordered_findings` — so this is defence-in-depth, not an operator-visible bug. **Not fixable
  in Story 8.3:** its AC14 fences `argus/cli.py` as must-not-modify. Close = widen the `try` to cover the
  summary-line + ship-readiness block (or move the render inside it) and add a test that lets the REAL
  `render_ship_readiness` raise on the way out of `main()` with no `--report-dir`.
  - id: DF-8-3-B
  - origin_story: 8-3-plain-english-report-stops-describing-impossible-state
  - owner: Delivery Orchestrator
  - target_story: 8-4 (or the first story that edits `argus/cli.py`)
  - category: correctness
  - severity: 🟢

- **DF-8-3-C** — The ast-index → application/test partition is now written twice. Story 8.3's AC8 correctly
  REUSED the predicate (`is_test_file(path, ast_entry=…)`) rather than forking a second classifier, and the
  reviewer confirmed the two call sites agree — but the plumbing around it is duplicated verbatim:
  `argus/pipeline.py:686-694` builds `{e.file_path: e for e in index.entries} if index is not None else {}`
  and filters `ledger.entries`, and `argus/reports/generator.py:86-93` now builds
  `{entry.file_path: entry for entry in (getattr(ast_index, "entries", ()) or ())}` and filters
  `ledger.entries` the same way. Two spellings of the same derivation, in two modules, with the report's
  APPLICATION denominator and the verdict's assessed population depending on them staying identical — which
  is precisely the disagreement class AC8 was raised to remove one level down. **Not fixable in Story 8.3:**
  its AC14 fences BOTH `argus/pipeline.py` (DF-8-2-A, 1199/1200 lines) and `argus/detectors/vacuous_test.py`
  (DF-8-2-B), which are the only two sensible homes for the shared helper. Close = add one helper beside
  `is_test_file` in `argus/detectors/vacuous_test.py` (e.g.
  `partition_application_files(ledger_entries, ast_index) -> tuple[list, int]`) and call it from both sites,
  as part of the story that performs the DF-8-2-A extraction.
  - id: DF-8-3-C
  - origin_story: 8-3-plain-english-report-stops-describing-impossible-state
  - owner: Delivery Orchestrator
  - target_story: the story that performs the DF-8-2-A `pipeline.py` extraction
  - category: maintainability
  - severity: 🟢

## Deferred from: dev of 8-4-tell-integrators-what-changed (2026-08-06)

- **RS-4b** — The bulk `minions_core` provenance sweep across `argus/`. Story 8.4 fixed the package FRONT
  DOOR only (`argus/__init__.py`, RS-4a); every other stale reference remains. **Measured in place on this
  tree** with `grep -rn "minions_core" argus/ --include=*.py`, excluding `__pycache__` and the foreign
  Epic-9-owned `argus/audit/minions_llm_adapter.py`: **15 references across 8 files** —
  `audit/deep_audit.py:21` · `audit/ports.py:4` · `cost/budget_governor.py:15` ·
  `dogfood/partition_plan.py:481,490,554` · `dogfood/proof_run.py:52,53,486,597,609,610` ·
  `governance/escalation.py:35` · `store/envelope.py:25` · `verdict/prosecutor.py:36`.
  ⚠️ **This is NOT a prose-only sweep.** Six of the fifteen, across five `lines.append(...)` call sites,
  emit the stale path INTO GENERATED Markdown artifacts rather than into a docstring:
  `partition_plan.py:481` and `:554` (the two "AUTO-GENERATED by" banners naming
  `minions_core/apaa/dogfood/partition_plan.py`, on the partition plan and the budget plan),
  `partition_plan.py:490` (the provenance line naming `minions_core/` and `minions_core/apaa/`),
  `proof_run.py:597` (the proof artifact's "AUTO-GENERATED by" banner naming
  `minions_core/argus/dogfood/proof_run.py`) and
  `proof_run.py:609-610` (the scope paragraph). A docstring/comment-only pass would miss all five, and the
  committed artifacts they produce would keep regenerating stale. (`proof_run.py:486` is a third kind
  again — an operator-visible `DogfoodProofError` message.) The remaining nine are genuine
  docstring/comment prose.
  ⚠️ **Sequencing constraint — this sweep must FOLLOW Story 8.5.** The generators above produce
  `minions-dogfood-partition-plan.md`, `minions-dogfood-budget-plan.md` and `minions-dogfood-proof.md`,
  which are **Story 8.5 / DR-10's** deliverable (8.5 re-derives them, and `tests/test_dogfood_proof.py`
  carries a committed-artifact rot check that compares them against a live run). Editing the generators
  before 8.5 re-derives would either break that rot check or force 8.5 to re-derive twice. Close = sweep
  the 15 references after 8.5 lands, re-derive the three generated artifacts in the same change, and keep
  the rot check green.
  - id: RS-4b
  - origin_story: 8-4-tell-integrators-what-changed
  - owner: Delivery Orchestrator
  - target_story: 9-2-ship-distribution-another-repo-can-actually-resolve (after 8-5-re-derive-proof-evidence-matches-tool)
  - category: maintainability
  - severity: 🟢

- **DF-8-4-A** — `action.yml` publishes a CRASHED run as an under-covered one. The composite action maps the
  audit exit code to its `verdict` output as `0 → RELEASE_READY`, `2 → NOT_READY_FOR_RELEASE`,
  **`else → INSUFFICIENT_COVERAGE`**. That `else` also swallows exit **`1`** — the AR10 typed-failure code,
  which means the run produced NO verdict at all — and publishes it downstream as
  `verdict=INSUFFICIENT_COVERAGE`, i.e. a *ran-and-under-covered* result. A consuming workflow cannot
  distinguish "Argus examined the repo and could not vouch" from "Argus never produced a verdict", so a
  crash reads as a completed audit. `INSUFFICIENT_COVERAGE` is also, per the PRD, a **not-assessed** state
  rather than a failure, which makes the mislabel an over-claim in the direction this epic exists to
  remove. **Pre-existing, not introduced by Epic 8:** exit `1` predates the FR16/FR4 amendment and the
  amendment changed no exit-code VALUE. **Not fixable in Story 8.4:** `action.yml` is untracked, foreign
  and Epic-9-owned, a concurrent session is editing it, and Story 8.4's AC12 fences it — filing it is
  exactly what the register is for. Close = give exit `1` its own arm (an explicit
  `verdict=AUDIT_FAILED`-style value, or fail the step outright) rather than letting it fall into the
  `else`; decide the output vocabulary with the packaging/distribution work that owns this file.
  - id: DF-8-4-A
  - origin_story: 8-4-tell-integrators-what-changed
  - owner: Delivery Orchestrator
  - target_story: 9-2-ship-distribution-another-repo-can-actually-resolve
  - category: correctness
  - severity: 🟢

- **DF-8-3-B — CLOSURE NOTE (append-only; the original entry above is NOT rewritten).** Closed by Story
  8.4. The `try/except ValueError` in `argus/cli.py::main` was widened to span the summary-line print and
  the ship-readiness render, rather than wrapping `run_audit(request)` alone — so the render is now inside
  the guard on the default no-`--report-dir` path. Widening (rather than moving the render) was chosen
  deliberately: it leaves the write ORDER of the two registers unchanged, so every non-raising run is
  byte-identical on both stdout and stderr, and the frozen stdout-summary goldens
  (`TC-ArgusAgent-CLI-001-30` / `-31`) still pass unchanged. Closing test:
  **`TC-ArgusAgent-CLI-001-33`** (`tests/test_cli.py::test_cli_degrades_when_the_real_renderer_raises_on_the_way_out`)
  — it does NOT monkeypatch the raise: `run_audit` is stubbed to RETURN the one verdict FR16 cannot
  produce, and the REAL `render_ship_readiness` raises the REAL `ShipReadinessError` at the real call site,
  with no `--report-dir`. Demonstrated RED-first against the pre-fix `cli.py`, where it failed with an
  uncaught `argus.reports.plain_english.ShipReadinessError` escaping `main()`. Post-fix `main()` returns
  `1` with a secret-safe stderr line (no traceback, no host path, no source bytes).


---

## Deferred from: code review of story 8-4-tell-integrators-what-changed (2026-08-06)

Three items raised by code-review **iteration 2** and routed to `defer`. None is an AC failure for Story
8.4 — all 13 ACs were assessed MET and R1-R4 independently confirmed fixed. These are recorded so the
rot-check's remaining blind spots do not become invisible once the epic closes.

- **id:** `DF-8-4-B`
  **origin_story:** `8-4-tell-integrators-what-changed`
  **owner:** Delivery Orchestration
  **target_story:** the first story after 8.5 that edits `tests/test_release_note.py` (or Epic-9 `9-2`, whichever fires first)
  **category:** test-adequacy
  **severity:** 🟢
  The AC9 rot check pins what the code *renders* and the schema constants it *imports*, but pins **no prose**
  in `CHANGELOG.md`. Verified by mutation: deleting the entire *"Do I need to change anything?"* section, the
  entire *"Defaults: `--coverage-scope`"* section (the only warning that a pipeline must now pass
  `--coverage-scope repository`), the content-address *"your pinned artifact path moved"* warning, and the
  *"If you call `render_ship_readiness()` directly, it can now raise."* line each leave the whole module
  **green**; so does corrupting the published before/after artifact-bytes example. Every **consumer-action**
  claim in the note is therefore unpinned. AC9 enumerates what must be pinned and prose sections are not on
  that list, so this is hardening, not a breach — but it is the largest remaining route to the silent rot
  AC9 names as its own failure mode. **Suggested close:** a section-presence assertion over each `###`
  heading and each `- **You …** →` bullet, plus an equality check of the published bytes example against
  `CriticalSubsystemSet().model_dump(mode="json")` (verified byte-accurate today, so it would pass on
  arrival).

- **id:** `DF-8-4-C`
  **origin_story:** `8-4-tell-integrators-what-changed`
  **owner:** Delivery Orchestration
  **target_story:** the first story that edits `argus/reports/generator.py`'s critical-subsystems section
  **category:** documentation-completeness
  **severity:** 🟢
  `CHANGELOG.md:180-182` summarises the `### Critical subsystems below \`audited_deep\`` change (*"now
  renders on every row … its lead sentence is row-dependent"*) without quoting a before/after pair. Measured
  HEAD vs live over a non-empty critical set: HEAD emitted on **every** row `These withheld \`RELEASE_READY\`
  (FR16). Each must reach \`audited_deep\`, or be removed from the critical set with \`--exclude-critical\` if it
  is not genuinely critical.`; live emits a **row-dependent** lead (row 2: *"Not the reason for this verdict
  — that is stated in the callout above. Listed because the clause is still unmet …"*) **plus a wholly new
  FR4/DR-5 exemption paragraph on every row**. AC4's *"at minimum"* list is satisfied, so this is a
  completeness gap rather than a breach — but a consumer grepping `final-verdict.md` gets no quotable
  before/after for a paragraph that changed on every affected run.

- **id:** `DF-8-4-D`
  **origin_story:** `8-4-tell-integrators-what-changed`
  **owner:** Engineering
  **target_story:** the first story that edits `argus/cli.py::main`'s exception handling
  **category:** error-handling-precision
  **severity:** 🟢
  The `except ValueError` at `argus/cli.py:295-299` catches the **base** class while the comment beside it
  enumerates five typed subclasses. Pydantic's `ValidationError` is a `ValueError` subclass, so a genuine
  internal validation bug is reported as an expected, typed *"audit failed"* degradation instead of
  surfacing. **Pre-existing** — the same clause wrapped `run_audit` at HEAD; Story 8.4's widening added only
  the two `print` calls, so the newly-swallowed surface is `ShipReadinessError` plus stream/encoding errors.
  The encoding half is tracked separately as review finding **D1** on the story, which is a live decision,
  not a deferral. **Suggested close:** catch the named subclasses explicitly.

---

## Deferred from: dev of 8-5-re-derive-proof-evidence-matches-tool (2026-08-07)

**APPEND-ONLY.** Nothing above this line was edited, reordered or deleted. Story 8.5 (DR-10) re-derived the
three committed dogfood artifacts and both verdict-report directories so that no published Argus artifact
contradicts the FR16/FR4 contract Epic 8 shipped. The notes below record what that re-derivation did to
work already filed here.

### Progress note — DF-6-6-A / DF-7-2-A must now adjudicate against a DIFFERENT artifact

`minions-dogfood-proof.md` has been REGENERATED. Its §6 finding population is no longer the Story-7.2
Minions one, because the generator's `enumerate_tracked_sources` defaults to `scope_prefix="argus"` — it
audits **this repository's own `argus/` package**, and Minions source is not in this repository (RS-1).
The QA-Lead work `DF-7-2-A` describes is defined over the Minions population, so it must be read against
the preserved copy, not the live file.

Measured 2026-08-07 by running the shipped generators in place at HEAD `be9d744`:

| Adjudication class | Story-7.2 Minions run (preserved) | Re-derived Argus SELF-audit (live) |
|---|---|---|
| `cross_partition` | 332 | **2** |
| `hardcoded_secret` | 2289 | **22** |
| `orphan_code` | 285 | **77** |
| Total findings emitted | 2906 | **101** |
| Source files audited / LOC | 135 / 36712 | **69 / 18206** |
| Verdict | `NOT_READY_FOR_RELEASE` (exit `2`) | **`RELEASE_READY` (exit `0`)**, row `row_3_gates_met` |

- The Minions finding classes survive **only** at
  `minions-dogfood-proof-story-7-2-superseded.md` (RS-3 supersede-don't-erase; the original body is
  preserved verbatim beneath a hand-authored header). They can never be re-derived in this repository.
- The re-derived proof is a **SELF-audit of Argus** and says so in §1. It is a materially weaker evidence
  class than the independent run it supersedes, and it is not independent corroboration of anything.
- `DF-6-6-A` / `DF-6-6-A-P1` / `DF-6-6-A-P2` / `DF-7-2-A` all stay **OPEN** and are **not** rewritten. The
  only change is which file the human adjudication reads. The >=80%-precision gate stays PROVISIONAL:
  `protocol_cleared` was never passed `True` and the 6.5 marker was not flipped.

### Progress note — RS-4b, measured: 6 of 15 references CONSUMED, 9 remain

Story 8.5 consumed exactly the references that are **emitted into a committed `.md` artifact**; it left
every reference that only ever reaches a Python reader. Re-measured on this tree after the change with
`grep -rn "minions_core" argus/ --include=*.py` (excluding `__pycache__` and the Epic-9-owned
`argus/audit/minions_llm_adapter.py`):

- **CONSUMED (6 of 15)** — `dogfood/partition_plan.py:481, 490, 554` and `dogfood/proof_run.py:597, 609,
  610`, i.e. the three `AUTO-GENERATED by ...` banners, the `- Source files (tracked ...)` provenance line
  and the proof's scope paragraph. `argus/dogfood/partition_plan.py` now contains **zero** `minions_core`
  references. The banners now name the real modules `argus/dogfood/partition_plan.py` and
  `argus/dogfood/proof_run.py`, and a committed test (`TC-ArgusAgent-DOGFOOD-001-36`) resolves **every**
  path each artifact cites against the filesystem.
- **REMAINING (9 of 15)** — `audit/deep_audit.py:21` · `audit/ports.py:4` · `cost/budget_governor.py:15` ·
  `dogfood/proof_run.py:52, 53` (module docstring) · `dogfood/proof_run.py:632` (the `DogfoodProofError`
  operator message; this line was `:486` before the change — the line number moved, the string did not) ·
  `governance/escalation.py:35` · `store/envelope.py:25` · `verdict/prosecutor.py:36`. All nine are
  docstring / comment / operator-message prose; none reaches a committed artifact.
- Additionally, the bare-word *"Minions"* SUBJECT claims, which were never on RS-4b's list of 15 and were
  wholly Story 8.5's, are now gone from all three artifacts. Exactly one occurrence of the word survives
  in `minions-dogfood-proof.md`, in the sentence pointing a reader at the preserved Story-7.2 record — a
  true historical statement, not a claim that Minions source was audited.
- **RS-4b's sequencing constraint is now satisfied** (it required the sweep to FOLLOW Story 8.5). Its
  remaining scope is the 9 references above. RS-4b stays **OPEN** and its entry above is **not** rewritten.

### Inversion F5 — the originating operator command, re-run at BOTH scopes (2026-08-07)

The command that triggered the FR16/FR4 amendment (`sprint-change-proposal-2026-08-03.md`) recorded
`verdict=NOT_READY_FOR_RELEASE deep_ratio=11/28 blocking_findings=0`. Re-run after Stories 8.1-8.4, on the
working tree:

```
$ python -m argus.cli audit .                             # default scope (application)
verdict=RELEASE_READY deep_ratio=57/149 blocking_findings=0 assessed_deep_ratio=57/73 scope=application held_out=76
exit 0

$ python -m argus.cli audit . --coverage-scope repository # the population the symptom was measured under
verdict=INSUFFICIENT_COVERAGE deep_ratio=57/149 blocking_findings=0
exit 3
```

**The reported symptom — a blocking verdict carrying zero findings — is NOT reproducible at either
scope.** The whole-repository branch, which is the one that used to render `NOT_READY_FOR_RELEASE`, now
renders row 4 → `INSUFFICIENT_COVERAGE` / exit `3`. Recorded here so the evidence outlives the story file.

### New defers

- **DF-8-5-A** — The signed evidence bundle stamps a version token that contradicts the shipped package.
  `argus/dogfood/proof_run.py` defines `DOGFOOD_ArgusAgent_VERSION = "1.43.0"` and passes it to
  `build_evidence_bundle(..., argus_version=...)`, so it is written into the SIGNED, content-hashed
  evidence bundle as `argus_version`. Measured on this tree: `pyproject.toml:7` declares
  `version = "0.1.0"` and `argus/__init__.py:59` declares `__version__ = "0.1.0"`. The bundle therefore
  carries a provenance claim about which Argus built it that no shipped artifact supports — a falsehood
  inside signed evidence, which is a worse place for one than prose. **Deliberately NOT fixed by Story
  8.5:** changing the token changes the bundle's content hash, and therefore the content hash the proof
  artifact publishes as its signature; and the version token belongs with the packaging/release work that
  owns `pyproject.toml`. **Close =** source the value from `argus.__version__` instead of a module
  literal, re-derive the proof artifact in the same change, and update `TC-ArgusAgent-DOGFOOD-001-34`'s
  `assert DOGFOOD_ArgusAgent_VERSION == "1.43.0"` pin along with it rather than around it.
  - id: DF-8-5-A
  - origin_story: 8-5-re-derive-proof-evidence-matches-tool
  - owner: Delivery Orchestrator
  - target_story: 9-2-ship-distribution-another-repo-can-actually-resolve
  - category: provenance-correctness
  - severity: 🟠

- **DF-8-5-B** — The committed-artifact rot checks re-break on any commit that changes `argus/**`
  composition, and nothing warns before they do. Three tests compare a committed `.md` against a LIVE
  derivation over the working tree: `TC-ArgusAgent-DOGFOOD-001-03` (asserts `Unit count: N` and each
  `partition_id[:12]`), `-06` (asserts `str(sized_ceiling)`), and `-20` (asserts the live verdict token +
  exit code). **Measured mechanism:** a `partition_id` is a sha256 over its unit's sorted member paths, so
  adding, removing or merely re-balancing one file under `argus/` changes it; `sized_ceiling` is
  `total_credits × 5/4` where `total_credits` folds `files_indexed + python_files + detector_passes`, so
  it moves with the file count; the verdict moves with the ledger. **Measured history:** `-03` and `-06`
  were RED across four consecutive commits (`ae5f00c` … `be9d744`) before this story, and `-20` joined
  them at `be9d744` when the Epic-8 delta moved the live verdict. Story 8.5's own work had to re-derive
  these artifacts **three times** for the same reason — every edit to `argus/dogfood/*.py` changed
  `total_loc` and the figures derived from it. The failure mode is therefore structural, not incidental:
  the checks are correct, but they make every `argus/**` change a two-step change, and a developer who
  does not know that reads three unexplained reds. **Close =** either a documented regeneration entry
  point named in the failure message of all three assertions, or a CI step that regenerates and fails on
  a diff — so the remedy is discoverable from the red output. Do **not** close it by loosening an
  assertion.
  - id: DF-8-5-B
  - origin_story: 8-5-re-derive-proof-evidence-matches-tool
  - owner: Engineering
  - target_story: the first story after Epic 9 that edits `tests/test_dogfood_plan.py` or `tests/test_dogfood_proof.py`
  - category: developer-experience
  - severity: 🟢

---

## Deferred from: code review of 8-5-re-derive-proof-evidence-matches-tool, iteration 1 (2026-08-07)

**APPEND-ONLY.** Nothing above this line was edited, reordered or deleted. Review iteration 1 returned
`CONCERNS` with five **Low** findings. Three were fixed in code (the unmatched `argus/tests/` exclusion
prefix plus the directory-blind citation guard; the `0`-as-absent live-sizing sentinel; the fatal-on-any-
read-failure critical-set read-back and its missing >1-match guard). The remaining two are recorded here,
because the review's own remedy for each was a ledger id rather than a code change.

### New defers

- **DF-8-5-C** — The published proof artifact states a precision-corpus figure of **N=0** that is measurably
  wrong. `argus/dogfood/proof_run.py:764-765` calls `precision_gate_status_for(precision=Fraction(0, 1),
  n=0, provisional=True, ...)` **unconditionally** — the arguments are literals, not a measurement of the
  corpus — and the resulting string is rendered verbatim into `minions-dogfood-proof.md:87` as
  *"precision=0/1 over FINDINGS not repos; N=0 labeled cartridges populated, floor N=5"*. **Measured today
  by calling the shipped registry** (`tests/cartridges/_registry.py`, imported and executed, not read off a
  document): `distinct_rule_class_count() == 5` and `populated_planted_defect_count() == 7`. So the
  artifact publishes `N=0` about a corpus that holds 5 distinct rule classes across 7 populated rows.
  **Direction matters:** the figure **UNDERSTATES** — it makes the provisional gate look further from its
  `N>=5` floor than it is, so it cannot be read as an over-claim and it cannot make a gate look cleared. It
  is nonetheless a number in a proof artifact that no one measured, which is the exact defect class Epic 8
  exists to delete. **Deliberately NOT fixed by Story 8.5:** the story's own Known-red carve-out directs
  *"Do NOT fix it here … File it (AC8)"*, and wiring the real counts touches the 6.5/6.6 precision surface
  (`precision_gate_status()` / the cartridge registry) that no AC in Epic 8 owns; changing the rendered
  string also changes the committed artifact, so it must land with a regeneration. **Recorded because the
  decision was previously only in a closing story's Completion Notes**, and `DF-6-6-A-P1` / `DF-7-2-A`
  record the corpus counts but say nothing about the published artifact rendering `N=0` — verified at
  `deferred-work.md:362-394`. **Close =** pass the measured `distinct_rule_class_count()` /
  `populated_planted_defect_count()` (or an explicit "corpus not consulted by this run" token) into
  `precision_gate_status_for`, regenerate `minions-dogfood-proof.md` in the same change, and keep
  `protocol_cleared=False` and the `provisional=True` framing untouched — this is a correctness fix to a
  reported number, never a step toward clearing the gate.
  - id: DF-8-5-C
  - origin_story: 8-5-re-derive-proof-evidence-matches-tool
  - owner: Engineering
  - target_story: the first story that edits the 6.5/6.6 precision surface (`argus/precision/**` or the
    cartridge registry) after the human `DF-7-2-A` adjudication
  - category: published-figure-correctness
  - severity: 🟢

- **DF-8-5-D** — `argus/dogfood/proof_run.py` carries five responsibilities in one module and is now
  **1196 / 1200 lines (4 lines of headroom)** against the NFR-M1 ceiling. **Measured composition:** module
  constants + the typed `DogfoodProofError`, five frozen value dataclasses (`AdjudicationRow`,
  `CostSummary`, `ScopeDisclosure`, `CriticalClauseDisclosure`, `DogfoodProofRun`), the impure
  git/snapshot/store shell (`enumerate_tracked_sources`, `materialize_snapshot`,
  `_read_critical_subsystem_set`, `run_dogfood`, `build_dogfood_proof`), the pure cost accountant
  (`cost_summary`, `adjudication_rows`), and ~390 lines of pure renderer (`render_proof_markdown` and its
  six `_render_*` / `_*_clause` helpers). That is an SRP/SoC violation held together only by the AR8
  pure/impure narration in its docstring. It grew 749 → 1154 in Story 8.5 and 1154 → 1196 across review
  iteration 1; **the next edit of any size breaches NFR-M1**, which is why this is filed rather than
  observed. **The extraction was considered and rejected TWICE and the rejection stands for Story 8.5:**
  AC13 does not authorise a restructure, and the final story of an epic whose subject is "no surprises" is
  the wrong place for one. **The blocker previously recorded (a circular import) is softer than stated and
  is corrected here:** extracting the pure renderers to `argus/dogfood/proof_render.py` needs the five
  dataclasses moved to a sibling (e.g. `argus/dogfood/proof_types.py`) and **re-exported** from
  `proof_run.py`, which preserves the public import surface — every existing
  `from argus.dogfood.proof_run import ...` keeps working — with no cycle. **A second, MEASURED constraint
  the closing story discovered:** the dogfood plans over `argus/**` itself, so adding a module changes the
  partition input set, and `TC-ArgusAgent-DOGFOOD-001-18` pins `unit_count >= 3` while this tree yields
  **exactly 3** — the extraction must therefore regenerate all three committed dogfood artifacts in the same
  change and re-measure the unit count, and a drop to 2 units is a finding to report, never a licence to
  loosen the assertion. **Close =** perform that extraction with the re-export shim, regenerate the three
  artifacts, and keep both modules under 1200 lines.
  - id: DF-8-5-D
  - origin_story: 8-5-re-derive-proof-evidence-matches-tool
  - owner: Engineering
  - target_story: the first story that edits `argus/dogfood/proof_run.py` for any reason
  - category: maintainability
  - severity: 🟠

---

## Deferred from: 9-2-ship-distribution-another-repo-can-actually-resolve (2026-08-08) — THE LAST STORY IN THE PLAN

**APPEND-ONLY.** Nothing above this line was edited, reordered or deleted.

> **Read this section differently from every other one in this register.** Story 9.2 is the last story of
> Epic 9 and the last story in the entire ArgusAgent plan. **There is no successor story to inherit a
> deferral.** Every `target_story` below that names "the first story that…" is now a conditional pointing at
> a story that does not exist and may never exist. Where that is the case it is said explicitly, because an
> item that reads like a handoff and is in fact abandoned is worse than an item marked abandoned: the first
> costs someone a search, the second costs them nothing. §5 of the Epic-8 retrospective established that
> items framed as handoffs evaporate while items attached to a named deliverable land; this section is
> written to make the evaporation visible rather than to prevent it, which is not in a story's power.

### Closed by this story

- **DF-8-5-A — CLOSED.** `argus/dogfood/proof_run.py` now reads
  `DOGFOOD_ArgusAgent_VERSION = _ARGUS_VERSION` with `from argus import __version__ as _ARGUS_VERSION`;
  the module literal `"1.43.0"` is gone. **Closing evidence, measured in place, not asserted:**
  (a) RED-first, through the shipped path — an evidence bundle was built with the pre-fix constant and
  persisted, and the resulting `.argus/state/<hash>.json` read
  `envelope.argus_version = "0.1.0"` while `envelope.payload.argus_version = "1.43.0"` (AGREE = False);
  post-fix the same path yields `0.1.0` on both levels (AGREE = True).
  (b) The dogfood bundle content hash moved
  `a1e76c01cbd29241a928f71b724b4c4c01d1211e0a4ae8a6e266386f811e0c0e` (which matched the committed
  `minions-dogfood-proof.md:57` signature line exactly, re-derived rather than read off the document) →
  `b3588816088920936de7a3fea17eaba747f7ad3c1af1ff93b0f4f4474acb6dc6` from the version fix alone →
  `da17b0fe19d121a4414ea542e8b9061abc73eca549aadb45b178cfc1fced89fc` after the DF-8-5-D extraction
  changed the audited population. The artifact was regenerated so it publishes the last of these.
  (c) `TC-ArgusAgent-DOGFOOD-001-34` was updated THROUGH the fix — it now asserts
  `DOGFOOD_ArgusAgent_VERSION == argus.__version__` rather than a second copy of the value — and its
  adjacent comment, which claimed the provenance was "the pyproject version token" while the code carried
  a literal that disagreed with pyproject, was corrected.
  (d) New enumerated guards: `TC-ArgusAgent-DOCS-001-14` (the three version-bearing surfaces agree) and
  `TC-ArgusAgent-DOCS-001-15` (an AST sweep of all 71 `argus/**` modules permits exactly ONE semver
  literal, at `argus/__init__.py`), so a fourth version literal goes RED.
  - id: DF-8-5-A
  - closed_by: 9-2-ship-distribution-another-repo-can-actually-resolve
  - closed_on: 2026-08-08
  - status: CLOSED

- **DF-8-5-D — CLOSED.** `argus/dogfood/proof_run.py` was split into three modules with a re-export shim.
  **Measured line counts:** `proof_run.py` 1196 → **679**, new `argus/dogfood/proof_render.py` **447**,
  new `argus/dogfood/proof_types.py` **207**; all three under the NFR-M1 1200 ceiling. (The three do not
  sum to 1196 + headers: the DF-8-5-A fix added 3 lines, the shim adds an import block, and each new
  module carries its own docstring and `__all__`.)
  **Corrections to this entry's own text, measured rather than inherited:**
  (a) The entry estimates the renderer at "~390 lines"; **measured it is 391** (`:809-1199` of the
  pre-split file).
  (b) The entry says "the next edit of any size breaches NFR-M1". The DF-8-5-A fix is **+3 lines net**
  and left the module at **1199/1200** — it FIT. The NFR-M1 fence did **not** force this extraction; the
  `target_story` did ("the first story that edits `argus/dogfood/proof_run.py` for any reason"), together
  with the absence of any later story. This correction matters because the fence narrative implies the
  work was unavoidable; it was not — it was *chosen*, on the ledger's instruction and because deferring it
  here means dropping it.
  (c) The entry warns that `unit_count` may drop to 2. **It did not: it held at 3**, measured on the real
  tree after the extraction. What moved instead was **every one of the three `partition_id`s** —
  `2c0f52f60457`/`681c496d09ed`/`973f3f199d1c` → `085854c90586`/`477ef77d7b65`/`bde14bbf3bcf` — because
  a `partition_id` is a sha256 over its unit's sorted member paths and adding two modules re-balanced all
  three units. A simulation over an isolated copy had predicted only ONE id would move; the real split
  moved three. The prediction was directionally right and numerically wrong, which is exactly why the
  measurement was repeated on the real tree.
  **Closing evidence:** the pure-move was proven by rendering the SAME `DogfoodProofRun` before and after
  the extraction and comparing bytes — **9927 → 9927 bytes byte-identical** for a real dogfood run, and
  **55101 → 55101 bytes byte-identical** across six synthetic runs covering every renderer branch (scope
  present/absent, critical clause not-captured / not-retrieved / vacuous / non-empty / not-satisfied,
  ceiling pair with and without a live sizing). New tests `TC-ArgusAgent-DOGFOOD-001-45`..`-48` pin the
  `__all__` import surface (fails on removal as well as on a broken import), the re-export IDENTITY
  (`proof_run.X is proof_types.X` — `==` would not catch a fork), the three line counts, the structural
  purity of both new modules, and the externalization-guard text.
  **One deliberate content change, disclosed rather than folded into "pure move":** the artifact's
  provenance banner now reads ``AUTO-GENERATED by `argus/dogfood/proof_render.py`
  (`render_proof_markdown`, re-exported from `argus/dogfood/proof_run.py`, which orchestrates the run)``.
  Leaving it naming only `proof_run.py` would still have resolved — and would still have pointed a reader
  at a file that no longer contains the generator. This is the ONLY difference between the pre- and
  post-extraction renders; it was made after the byte-identity proof was captured, not before.
  **Second disclosed move:** `DOGFOOD_EXTERNALIZATION_GUARD` moved from `proof_run.py` to
  `proof_render.py` because the renderer is its only consumer and leaving it behind would have forced
  `proof_render → proof_run`, i.e. the cycle the shim exists to avoid. Its text is byte-identical and is
  now pinned by an equality assertion (`TC-ArgusAgent-DOGFOOD-001-48`), so Story 9.2 / AC12's "unchanged"
  is verified rather than asserted.
  - id: DF-8-5-D
  - closed_by: 9-2-ship-distribution-another-repo-can-actually-resolve
  - closed_on: 2026-08-08
  - status: CLOSED

- **DF-8-4-A — CLOSED.** `action.yml`'s exit-code map is now explicit over the complete space
  `{0, 2, 3, 1, anything else}`. Exit `1` has its own arm and renders `verdict=AUDIT_FAILED`, and the
  catch-all renders the same failure token rather than a verdict token, so an unmapped future exit code
  can never surface as an assessment. **Vocabulary decision and why:** `AUDIT_FAILED` was chosen over
  failing the step outright because a composite action that dies takes the consumer's ability to branch
  with it — a caller that wants to tolerate a tooling failure and a caller that wants to block on one need
  different behaviour, and only the caller knows which they are. A new `assessed` output (`true` for
  0/2/3, `false` otherwise) gives them the boolean without string-matching, and the `1`/unmapped arms emit
  a GitHub `::error::` annotation so the failure is visible even when the step is tolerated.
  `outputs.verdict` and `outputs.exit-code` descriptions were rewritten; they had documented only three
  codes and never mentioned `1`. `strict` stays `"false"` (see the fenced note below).
  - id: DF-8-4-A
  - closed_by: 9-2-ship-distribution-another-repo-can-actually-resolve
  - closed_on: 2026-08-08
  - status: CLOSED

- **RS-4b — CLOSED.** All nine remaining `minions_core` references under `argus/**` were swept:
  `audit/deep_audit.py:21`, `audit/ports.py:4`, `cost/budget_governor.py:15`, `dogfood/proof_run.py:52`,
  `:53`, `:666` (the operator-visible `DogfoodProofError` message), `governance/escalation.py:35`,
  `store/envelope.py:25`, `verdict/prosecutor.py:36`. **The stale line reference in this register's own
  RS-4b entry (`proof_run.py:632`, corrected to `:666` by AI-E8-7) is closed out by the sweep rather than
  re-filed with a fourth line number** — the reference no longer exists at any line.
  **One of the nine was not merely stale but FALSE:** `cost/budget_governor.py:15` claimed
  "AR7 (reuse ``minions_core.cost.budget_guardrails`` BY IMPORT)" while the module actually imports
  `argus.shared.budget_guardrails` (vendored by the repo separation). It now names the real module.
  A tenth, identical false claim in `tests/test_no_web_imports.py:89` was corrected in the same pass and
  is disclosed here because it is outside RS-4b's stated `argus/**` scope.
  **The two decoys were left standing** — `argus/audit/minions_llm_adapter.py:5` and `:29` are Story 9.1's
  TRUE NEGATIVE statements about a dependency that no longer exists, and deleting them would delete the
  documentation of RS-1/IN-2.
  **Closing evidence:** `grep -rn "minions_core" argus/ --include=*.py` (excluding `__pycache__`) now
  returns exactly those two lines and nothing else. Two new guards make it an enumerated space:
  `TC-ArgusAgent-STORE-001-109` walks all 71 modules and fails on any occurrence outside an allowlist that
  contains exactly `argus/audit/minions_llm_adapter.py` (and fails if the allowlisted count changes, so
  the negative statements cannot be silently deleted either), and `TC-ArgusAgent-STORE-001-110` requires
  every surviving occurrence to sit in a line that DENIES the dependency — so the allowlist cannot be
  repurposed into a smuggling route for a real provenance claim.
  **Bare-word "Minions" (NOT `minions_core`, and NOT RS-4b):** bounded to `argus/dogfood/**` per the
  story's D10 and swept there — measured per file, `proof_run.py` 13 → 1, `partition_plan.py` 6 → 0,
  `dogfood/__init__.py` 2 → 0 (20 removed). Historical statements that are TRUE were kept (the superseded Story-7.2 run over
  the Minions platform really did happen, and `proof_render.py` still cites it). The remaining
  occurrences elsewhere under `argus/**` are explicitly OUT OF SCOPE and are filed as `DF-9-2-B` below.
  - id: RS-4b
  - closed_by: 9-2-ship-distribution-another-repo-can-actually-resolve
  - closed_on: 2026-08-08
  - status: CLOSED

- **DF-8-4-B — PARTIALLY CLOSED (heading half closed; bytes-example half explicitly left OPEN).**
  Its `target_story` reads "the first story after 8.5 that edits `tests/test_release_note.py` (or Epic-9
  `9-2`, whichever fires first)"; **both clauses fired**, because AC6 had to update
  `TC-ArgusAgent-DOCS-001-01`'s `"## Unreleased"` pin. **Closed:** `TC-ArgusAgent-DOCS-001-16` registers
  every `###` section of `CHANGELOG.md` as an enumerated, ORDERED space — a removed section fails, an
  unregistered added section fails, and a reordering fails. **Deliberately NOT closed:** the suggested
  bytes-example equality check. The note already carries byte-for-byte equality assertions over the
  surfaces that matter — the FR16 decision table, the ship-readiness headlines, the `final-verdict.md`
  callouts and the persisted assurance sentences, via `TC-ArgusAgent-DOCS-001-03`..`-06` — so a second
  generic bytes check would add duplication rather than coverage. **This half now has no owner** (see
  below).
  - id: DF-8-4-B
  - closed_by: 9-2-ship-distribution-another-repo-can-actually-resolve (heading half only)
  - closed_on: 2026-08-08
  - status: PARTIALLY CLOSED — bytes-example half OPEN and UNOWNED

### Opened by this story

- **DF-9-2-A** — 🟠 **Five shipped module files cannot be imported from the built distribution.**
  MEASURED, not inferred: `python -m build` produced `argus_agent-0.1.0.tar.gz` (75 files) and
  `argus_agent-0.1.0-py3-none-any.whl` (76 entries = **71** `argus/**` modules + 5 `dist-info`). Each of
  those 71 modules was imported in its own clean subprocess with the wheel's contents on `sys.path` and
  this repository **removed** from it: **66 of the 71 import. Five do not:**
  `argus/precision/__init__.py`, `argus/precision/replay_harness.py`, `argus/dogfood/proof_types.py`,
  `argus/dogfood/proof_render.py`, `argus/dogfood/proof_run.py` — all with
  `ModuleNotFoundError: No module named '_registry'`. **Single cause:**
  `argus/precision/replay_harness.py:87-90` inserts `<repo>/tests/cartridges` onto `sys.path` and
  unconditionally imports `_registry` from it; `tests/` is not in the distribution and should not be.
  Everything else is that one import reached transitively (`argus/precision/__init__.py` re-exports it,
  and the dogfood modules import `MatchKey` from it).
  ⚠️ **Figure corrected at code-review iteration 1 (2026-08-09), stated rather than quietly swapped.**
  This entry first read *"65 of the 69 shipped modules import"* and named only four broken modules. `69`
  was the **pre-split** module count — the tree has been 71 since this same story's AC8 landed — and the
  four-module list omitted `argus/precision/replay_harness.py`, the module that actually contains the
  offending import, while the committed pin `_NOT_IMPORTABLE_FROM_DISTRIBUTION` correctly listed five.
  The replacement figures above were **re-measured from scratch**, not re-derived from the old sentence.
  The disposition below is unchanged: only the numbers were wrong.
  **Pre-existing, verified not assumed:** the identical import exists at HEAD `7be90f7`
  (`git show 7be90f7:argus/precision/replay_harness.py`), and the pre-split `proof_run.py` imported
  `argus.precision.replay_harness` at its line 127. The Story-9.2 split did not create the defect and did
  not widen the consumer surface — the two new modules fail only because they re-export what already
  failed. **Nothing that imported before imports less now.**
  **Not fixed here, deliberately:** `argus/precision/**` is FENCED by Story 9.2 / AC15, and the fix is a
  behavioural change to the precision substrate inside a release story with no mandate over it.
  **Impact is bounded and stated:** IN-1/IN-3 need `argus audit`, and the whole CLI path imports and RUNS
  from the wheel (`argus --help` exit `0`; `argus audit <fixture>` → `RELEASE_READY`, exit `0`, executed
  from a working directory that is not this repository). What a consumer cannot do from the distribution
  alone is re-run Argus's own dogfood proof generator, which is a self-audit tool, not a consumer feature.
  README.md and CHANGELOG.md both state this split explicitly rather than leaving it to be discovered.
  **Close =** make the registry import lazy or optional in `replay_harness.py` (import inside the function
  that needs it, or degrade to an explicit "no labelled corpus available" state), then re-measure the
  importable count from a freshly built wheel and update `_NOT_IMPORTABLE_FROM_DISTRIBUTION` in
  `tests/test_release_preflight.py` — which is pinned in BOTH directions, so a fix that leaves the record
  stale goes RED.
  - id: DF-9-2-A
  - origin_story: 9-2-ship-distribution-another-repo-can-actually-resolve
  - owner: Engineering
  - target_story: **NONE — no story exists after 9.2.** This needs a named human to schedule it.
  - category: packaging-correctness
  - severity: 🟠

- **DF-9-2-B** — 🟢 **Bare-word "Minions" subject claims outside `argus/dogfood/**`.** Story 9.2's D10
  bounded the subject-claim sweep to `argus/dogfood/**` (where the modules were being rewritten anyway).
  **Measured:** the bare word ran 45 times across 17 `argus/**` modules at HEAD `7be90f7` and runs **25
  times across 15** now — 20 removed, all inside `argus/dogfood/**` (`proof_run.py` 13 → 1,
  `partition_plan.py` 6 → 0, `dogfood/__init__.py` 2 → 0), with 2 kept there deliberately because they
  are TRUE historical statements about the superseded Story-7.2 run (`proof_run.py:5`,
  `proof_render.py:71`). ⚠️ The story context stated 44 across 17; re-measured in place it is 45. Of the
  25 that remain, 2 are those deliberate keeps and **23 are elsewhere under `argus/**`** — historical
  narration in
  modules Story 9.2 did not touch (e.g. `cost/budget_governor.py`'s "the Minions `BudgetPolicy` fields are
  `float`", which is a true statement about the vendored guardrail's shape). They are not falsehoods of the
  RS-4b class and none of them names a package that no longer exists; they are simply subject language
  inherited from the monorepo. Sweeping them is an unbounded prose pass, which is why RS-4b was scoped away
  from them in the first place. **Close =** a bounded prose pass that reads each one and decides whether it
  is a true historical statement (keep) or a false subject claim (rewrite) — never a blanket replace.
  - id: DF-9-2-B
  - origin_story: 9-2-ship-distribution-another-repo-can-actually-resolve
  - owner: Engineering
  - target_story: **NONE — no story exists after 9.2.**
  - category: documentation-accuracy
  - severity: 🟢

- **DF-9-2-C** — 🟢 **`argus/dogfood/__pycache__/*.pyc` are tracked in git.** Measured with
  `git ls-files argus/dogfood/`: three compiled `.cpython-312.pyc` files are committed even though
  `.gitignore:2` lists `__pycache__/` (the ignore rule cannot affect already-tracked paths). They do not
  reach the partition plan — `enumerate_tracked_sources` filters by `_SOURCE_SUFFIXES`, which is why
  `source_file_count` is 71 and not 74 — and they were not added or touched by Story 9.2. Filed rather
  than fixed because `git rm --cached` on tracked paths is a repository-hygiene change outside this
  story's scope, and because a silent deletion of tracked files during a release story is precisely the
  kind of unannounced side effect Epic 8 exists to prevent. **Close =** `git rm --cached` the three paths
  in a change that says so.
  - id: DF-9-2-C
  - origin_story: 9-2-ship-distribution-another-repo-can-actually-resolve
  - owner: Engineering
  - target_story: **NONE — no story exists after 9.2.**
  - category: repository-hygiene
  - severity: 🟢

### Re-recorded as OPEN and, after this story closes, UNOWNED

> Each of the following keeps its original entry text, unedited. What is recorded here is that its
> `target_story` no longer resolves to anything. This is the honest outcome of ending a plan with items in
> the register, and it is materially better than performing a large risky refactor inside a release story
> to avoid writing an uncomfortable sentence (Story 9.2 / D11).

- **DF-8-5-C — OPEN, and knowingly REPUBLISHED unchanged by this story.** `proof_run.py`'s
  `precision_gate_status_for(precision=Fraction(0, 1), n=0, provisional=True, ...)` literals were
  re-rendered verbatim into the regenerated `minions-dogfood-proof.md`, which again publishes
  "N=0 labeled cartridges populated, floor N=5" while the shipped registry measures
  `distinct_rule_class_count() == 5` and `populated_planted_defect_count() == 7`. **It UNDERSTATES**, so it
  makes the provisional gate look FURTHER from its floor than it is and can never make a gate look
  cleared. Not fixed here because its `target_story` names the 6.5/6.6 precision surface **after the human
  `DF-7-2-A` adjudication**, which has not occurred, and because `argus/precision/**` is fenced by AC15.
  **Reprinting it while naming it is the honest act; reprinting it silently was the failure mode.**
  Owner after 9.2: **none.**
- **DF-8-5-B — OPEN.** Its `target_story` reads "the first story **after Epic 9**", so it was never
  Story 9.2's to close — but 9.2 hit exactly the pain it describes: `TC-ArgusAgent-DOGFOOD-001-03` and
  `-06` were verified RED against the committed artifacts before regeneration (all three live
  `partition_id`s absent from the committed plan; `443` absent from the committed budget plan) and green
  after. **Whether 9.2 made the remedy discoverable: NO, and deliberately so.** The entry asks for a named
  regeneration entry point in the failure message of all three assertions, or a CI regenerate-and-diff
  step. Neither was added: the first edits assertion text in tests this story must not weaken, and the
  second adds a CI job with a ~2-minute dogfood run to a release story. What 9.2 DID add is a documented
  regeneration sequence in its story record (source edits → tests → stage → regenerate → re-run), which is
  a story artifact and not the discoverable-from-red-output remedy the entry asks for. Owner after 9.2:
  **none.**
- **DF-8-4-C** and **DF-8-4-D** — OPEN. Their targets (`reports/generator.py`'s critical-subsystems
  section; `cli.py::main`'s exception handling) are inside Story 9.2's AC15 fence and were not opened.
  Owner after 9.2: **none.**
- **DF-8-2-A**, **DF-8-3-A**, **DF-8-3-C** — OPEN, and all three gate on the `argus/pipeline.py`
  extraction. Measured today: `pipeline.py` is **1199 / 1200 lines**, one line from the NFR-M1 ceiling.
  Story 9.2 FENCED it (D11) — the extraction is a second unrelated restructure inside a release story, it
  touches the module that produces every verdict, and nothing in IN-0 requires it. **Consequence, stated
  plainly: the next edit of any size to `pipeline.py` breaches NFR-M1, and there is no story queued to
  perform the extraction.** Owner after 9.2: **none.**
- **DF-6-6-A**, **DF-6-6-A-P1**, **DF-6-6-A-P2**, **DF-7-2-A** — OPEN and NOT rewritten by this story.
  `DF-7-2-A` is the human Eng-Lead + QA-Lead TP/FP adjudication that is the only thing that can clear the
  ≥80%-precision gate. It has not happened. Owner: a named human, as it always was.
- **DF-6-7-A** — OPEN (HITL wiring), untouched.

### The register as a whole, after Story 9.2 closes

**Nobody is looking after this.** Epic 9 is the last epic; there is no Epic 10, no next sprint in this
tracker, and no story whose `target_story` clause will fire. Twelve entries remain OPEN
(`DF-6-6-A`, `-P1`, `-P2`, `DF-6-7-A`, `DF-7-2-A`, `DF-8-2-A`, `DF-8-3-A`, `DF-8-3-C`, `DF-8-4-C`,
`DF-8-4-D`, `DF-8-5-B`, `DF-8-5-C`), plus the bytes-example half of `DF-8-4-B` and the three items this
story opened (`DF-9-2-A`, `DF-9-2-B`, `DF-9-2-C`). **Each needs a named human to schedule it or an
explicit decision to abandon it.** Neither is a thing an autonomous story can do, and pretending
otherwise by re-targeting them at a hypothetical future story would be the evaporation §5 of the Epic-8
retrospective described.

**H0 is NOT in this register and was NOT filed by this story.** `epics.md:1693-1699` records that no story
in this breakdown owns filing the Minions-repo handoff H1–H4, that H0 is **UNOWNED**, and that "a handoff
nobody files is a handoff that does not exist". It was escalated as readiness-report **F5 (LIVE)** on
2026-08-03 and re-raised as **AI-E8-10** on 2026-08-08. Story 9.2 did not create it, claim it, or close
it. Two related facts are restated once so they are not lost when this repository's plan closes:
assumption **A5** is ⚠️ **Unsupported** — after the FR16/FR4 amendment the Minions repository is expected
to land on row 4 → exit `3`, which still fails an unconfigured blocking CI gate, so **H3** needs a policy
decision before that gate can be made blocking — and **IN-1** must be an optional extra
(`minions[argus]`-shaped), never a base dependency, because Minions declares `dependencies = []`.

---

## Deferred from: code review of story 9-2-ship-distribution-another-repo-can-actually-resolve (2026-08-09)

Appended by the code-review gate, iteration 1. Append-only: nothing above this heading was edited,
reordered or deleted. One item only — every other review finding is an actionable `[Review][Patch]`
item inside the story file and is being fixed in this story, not deferred.

- **DF-9-2-D** — 🟢 **`action.yml` interpolates a consumer-supplied action input into shell source.**
  `action.yml:127` runs `if [ "${{ inputs.strict }}" = "true" ]`, expanding the composite action's
  `strict` input into the `run:` body before `bash` parses it. A consumer who sets `strict` to a crafted
  value executes shell in the calling workflow's job. **Pre-existing and out of the 9.2 delta, verified
  not assumed:** the line is byte-identical to HEAD `7be90f7`; Story 9.2 rewrote the exit-code `case`
  arm immediately above it (DF-8-4-A / AC10) and did not touch this line. Deferring it was the correct
  scoping call — widening a release story into an unrelated hardening pass on the consumer-facing action
  is the scope creep AC15's fences exist to prevent.
  **Close =** bind the input through `env:` (`env:\n  STRICT: ${{ inputs.strict }}`) and compare
  `"$STRICT"`; do the same sweep over every other `${{ inputs.* }}` occurrence in `action.yml` in one
  pass, and add a guard test that fails on any `${{ inputs.` appearing inside a `run:` block.
  - id: DF-9-2-D
  - origin_story: 9-2-ship-distribution-another-repo-can-actually-resolve (code review, iteration 1)
  - owner: Engineering
  - target_story: **NONE — no story exists after 9.2.** Needs a named human to schedule it, exactly as
    DF-9-2-A/B/C do.
  - category: security-hardening
  - severity: 🟢

## Deferred from: repository audit (2026-08-09)

- **DF-AUD-APAA-C** — A release status was asserted over a gate that had never executed.
  `sprint-change-proposal-2026-07-28.md:63` records *"Upgraded from NEEDS TARGETED REWORK to
  READY FOR RELEASE!"*, evidenced by a LOCAL pytest run (`:55`, "916 PASSED"). Item 6 of that
  same proposal CREATED `.github/workflows/audit-ci.yml`; its only run on `master`
  (`30774175196`) is `failure`, dying at the `bandit` step in 40s — before pytest was ever
  reached — because `bandit -r argus` exits 1 on any severity and this tree carries 18 benign
  Low findings. A second, independent break: `pytest --cov` was invoked while `pytest-cov` was
  absent from the `[dev]` extra, so the `--cov-fail-under=80` gate could not run either. Both
  were repaired 2026-08-09 and a clean-venv reproduction of every step passes on 3.12; the
  repair is NOT the deferred item. Close = adopt the Story 10.1 evidence standard: a release
  status cites an executed gate (CI run id) or is recorded NOT ESTABLISHED, and the 2026-07-28
  record is corrected in place, dated and reasoned (§3.4 evidence immutability — never a
  silent rewrite).
  - id: DF-AUD-APAA-C
  - owner: Delivery Orchestrator
  - target_story: 10-1-release-status-must-cite-evidence
  - category: process
  - severity: 🟠
  - **CLOSED 2026-08-10 by story 10-1-release-status-must-cite-evidence**
    (append-only closure note — the original entry above is NOT rewritten, §3.4 evidence
    immutability. That matters more than usual here: the entry contains a sentence the
    executed gate contradicted, and quietly fixing it would be a third instance of the very
    class this entry files. See (b).)
    **(a) The executed gate the entry asked for now exists.** `audit-ci.yml` run
    **`31341363300`** concluded **`success`** in 1m54s on 2026-08-09T23:13:27Z covering sha
    **`00c8d1b`** (`00c8d1bea695dc2e210b1a8c83bd5c69fd019fe0`), with **3/3 matrix legs green**
    — 3.10 ✅, 3.11 ✅, 3.12 ✅, each job conclusion read individually rather than inferred from
    the run's top-level status. The record under correction is amended in place:
    `sprint-change-proposal-2026-07-28.md:63` is now **struck** beside a dated §5 correction
    block that names the failed run, the superseding run and the sha each one covers, and
    records the release status itself as **NOT ESTABLISHED**.
    **(b) 🚩 A NEW FINDING, recorded because it is this entry's own defect.** The sentence
    above — *"Both were repaired 2026-08-09 and a clean-venv reproduction of every step passes
    on 3.12; the repair is NOT the deferred item"* — **was contradicted by the executed gate at
    the moment it was written.** The repair commit `cd60dbb`'s own CI run **`31322881580`**
    (sha `cd60dbbe45d03b7bc647307a3b14a66a2bd019ff`) concluded **`failure`**: the **3.11 leg
    failed at *"Run Pytest & Coverage Assurance Gate"*** and the **3.10 and 3.12 legs were
    `cancelled`** by fail-fast — so *"passes on 3.12"* was never executed on 3.12 at all. A
    clean-venv reproduction on a Windows workstation is a LOCAL run; it is necessary, not
    sufficient, and it is exactly the substitution this entry was filed about. **The class
    recurred inside the record of the class**, which is why it is recorded here rather than
    silently repaired.
    **(c) The measured cause — and it was not the workflow.**
    `git diff cd60dbb 00c8d1b -- .github/workflows/audit-ci.yml pyproject.toml` is **empty**:
    the workflow repair was correct and is byte-identical between the two shas. What was still
    broken was **product code on POSIX**, visible in the failed log as
    `Failed: DID NOT RAISE WorkspaceContainmentError`. Every one of these defects was invisible
    on the Windows development host and fatal on the ubuntu runner — the structural reason a
    local run can never discharge the rule.
    **(d) What closed it:** the twelve commits `cd60dbb..00c8d1b`, of which six are the
    POSIX/non-ASCII chain — `d0e0a5c` (non-ASCII filenames crashed under a C locale), `ebdca75`
    (containment decided differently on POSIX than on Windows — the `DID NOT RAISE` failure),
    `f7c666e`, `266bb28` (F-21 surrogate repair), `f85fe76`, `40c0727`.
    **(e) The standard is now committed, both halves.** The rule is written in
    `architecture.md` §H and named in §Enforcement (a rule that lives only in a test is not a
    rule); the guard is `tests/test_evidence_citation.py`
    (`TC-ArgusAgent-DOCS-001-20`..`-23`), which resolves `sprint-change-proposal-*.md` and
    `epic-*-retro-*.md` by glob so a new proposal cannot escape by being new, and which was
    demonstrated RED against the uncorrected documents before the corrections landed.
    **(f) What remains OPEN and is NOT closed by this entry:** the ≥80% precision
    externalization gate is **not cleared** (Epic 13 owns it); nothing is tagged, pushed or
    published (operator step **AI-E9-1**, still unowned); and **no CI run covers any tree later
    than `00c8d1b`**, including the commit carrying this note — run ids are sha-scoped, and the
    run that evidences this commit does not exist until the operator pushes. Recorded as
    NOT ESTABLISHED rather than assumed.

- **DF-AUD-APAA-D** — Multi-language AST grounding shipped in V1 while every specification
  still designates it V2, and its determinism provenance is wrong for non-Python repos. The
  capability entered via `sprint-change-proposal-2026-07-28.md:18` (*"user intent requested…
  multi-language auditing capability"*) with no story and no PRD/architecture amendment; PRD
  L23/L180 and architecture L220/L237 were never updated. Consequences: (a) the V2 roadmap
  double-counts delivered work; (b) `index/ast_index.py:311` records ONE `grammar_version`
  resolved from `tree-sitter-python` for a 10-language index, so a Go/Rust/JS grammar change
  would not move the R3 cache key — the identical silent-cache-staleness failure mode
  DF-5-1-A already flags for `prompt_template_version`, and the architecture's R3 key
  (L77-78, L201) was DESIGNED for a single grammar, making this a design change not a defect
  fix; (c) the `[languages]` extra is documented in neither README nor CHANGELOG, so a
  consumer cannot discover it. Drift direction is an UNDERSELL — no false capability claim
  reached a consumer. Close = Story 10.2: amend PRD + architecture (incl. R3), make
  provenance per-grammar BEFORE the Epic-5 store is wired (free now, needs a
  `CACHE_KEY_SCHEMA_VERSION` bump and migration later), and document the extra.
  - id: DF-AUD-APAA-D
  - owner: Engineering Lead
  - target_story: 10-2-multi-language-grounding-is-v1-in-the-specs
  - category: process
  - severity: 🟡
  - **CLOSED 2026-08-10 by Story 10.2 — append-only closure note. The entry above is left
    byte-for-byte intact, INCLUDING the site enumeration ("PRD L23/L180 and architecture
    L220/L237") that measurement has now shown to be incomplete. Correcting it in place would
    destroy the evidence that the enumeration kept being wrong, which is the finding (§3.4,
    DN-8).**
    **(a) The enumeration was wrong a THIRD time, and that is the story's central finding.**
    This entry names 4 sites; the epic later corrected it to 7, then to 10. Measured against the
    working tree on 2026-08-10 the real figure is **12 to amend + 2 to exempt**: PRD `:23`,
    `:121`, `:193`, `:214`, `:364`, `:438`, `:469` (FR7), `:571` (NFR-P2) and architecture
    `:89`, `:267`, `:317`, `:800`. Architecture `:89` (*"AST = Python in V1"*) and `:800`
    (*"Future enhancement: multi-language AST (V2)"*) were missed by **all three** prior
    hand-counts. `:89` shows why: it scopes deep grounding to Python with **no `V2` marker
    anywhere in the sentence**, so every keyword sweep for "V2" walked straight past it. The two
    exempt sites — architecture `:471` and `:766` — are **true statements about the default
    install** (the nine grammars are an optional extra, so `pip install argus-agent` really does
    ground Python only); amending them would replace a true sentence with a false one, and they
    belong to Story 12.5 / NFR-P3. They are exempted **by name with that reason recorded**, never
    silently. **The remedy is therefore not a corrected list — a hand-counted list is what failed
    three times — but a committed closure guard**, `tests/test_spec_claim_scope.py`
    (`TC-ArgusAgent-DOCS-001-24`..`-27`), which resolves `E-PRD/*.md` + `architecture.md` by
    **glob** so a new specification file cannot escape by being new, matches the claim as a
    **pattern** over sentence units so a claim rewritten at a new line cannot escape by moving,
    carries a positive control in both directions, and fails if it scans nothing or if an
    exemption stops matching. It was demonstrated RED against the unamended specifications first
    and named all 12 sites.
    **(b) The specification was overselling in one direction and the CODE was underselling in the
    other: only 8 of 10 languages actually grounded.** Measured by executing `build_ast_index`
    over a ten-language fixture on this host: `a.ts` and `a.php` returned `ast_eligible=False`
    with `grammar_missing_typescript` / `grammar_missing_php` **while both grammar packages were
    installed and both were declared in the `[languages]` extra**. Cause: grammar loading resolved
    only `getattr(mod, "language", None)`, and those two packages ship several dialects instead
    (`language_typescript`/`language_tsx`, `language_php`/`language_php_only`). Nothing raised —
    the code fell through to the "grammar missing" branch — so the reason token **told an operator
    to install a package they already had**. That is the `DF-AUD-APAA-F` / Story 10.4 harm ("the
    remedy the report gives an operator is wrong") from a **third** cause, and 10.4's fix does not
    reach it: splitting `except (ImportError, Exception)` does nothing where nothing raises. Fixed
    here with a declarative per-language entry-point map (plus a suffix-level override so `.tsx`
    gets the JSX-aware grammar), because AC1 amends **FR7, the binding capability contract**, and
    writing "delivered in V1" into FR7 while two of the ten returned `ast_eligible=False` would
    have replaced one false spec claim with another — this time in the **oversell** direction,
    which this entry correctly notes the original was not. Measured after: **10 of 10 ground**,
    plus `.tsx`. Blast radius on this repository is zero (`git ls-files` matches 0
    `.ts/.tsx/.mts/.cts/.php` files) and the dogfood verdict is byte-identical
    (`RELEASE_READY deep_ratio=30/79 blocking_findings=0 assessed_deep_ratio=15/19`).
    **(c) Provenance and the R3 key.** Measured: a ten-language index recorded
    `grammar_version='0.25.0'` (tree-sitter-python's) for a build in which tree-sitter-rust 0.24.2,
    tree-sitter-java 0.23.5 and tree-sitter-ruby 0.23.1 had each parsed — wrong for 7 of the 8
    languages that then grounded. `AstIndex` and `RecordingProducingClosure` now carry per-grammar
    provenance for exactly the grammars that **parsed**; folding every *installed* grammar was
    rejected because it would key the cache on the host rather than the audit, and both directions
    are pinned (`TC-ArgusAgent-CACHE-001-77`/`-78`). Additive per PRD §"Migration guide":
    `grammar_version` is retained with its description corrected to say what it always actually was
    (the `tree-sitter-python` package version, never the index's provenance);
    `AstIndex.schema_version` `"1"`→`"2"` and `CACHE_KEY_SCHEMA_VERSION` `"2"`→`"3"`. The bump cost
    one constant because the licensing measurement held: no production caller derives a key.
    **The store was deliberately NOT wired** — that is Story 12.3, and the ordering is recorded in
    architecture.md §C as load-bearing.
    **(d) The extra is documented**, in README (install command, languages, and what a missing
    grammar does to a file's grade) and in CHANGELOG under `## Unreleased`. Where the grammars
    live is untouched: that is Story 12.5's open NFR-P3 decision.
    **(e) What is NOT closed by this entry:** `DF-10-2-A` below — C, C++, Ruby and Rust ground but
    extract no definitions, so a file in those four cannot reach `audited_deep`. It is a NEW
    finding of this story, filed rather than folded in, because Story 10.2's AC3 is fenced to a
    grammar-resolution fix. **Gate status: NOT ESTABLISHED.** Local gates were re-run and are
    recorded as LOCAL in the story file; no CI run covers this tree, run ids are sha-scoped, and
    the run that would evidence this commit does not exist until an operator pushes.

- **DF-10-2-A** — Four languages GROUND but extract no structure, so no file in them can reach
  `audited_deep`. Measured 2026-08-10 while closing `DF-AUD-APAA-D`, on the fixed loader: C, C++,
  Ruby and Rust all parse cleanly (`ast_eligible=True`, no error) and return **zero
  `Definition`s**. Cause is `argus/index/ast_index.py`'s definition vocabulary, written against
  Python's node names: C/C++ carry a `function_definition`'s name under the `declarator` field
  rather than `name`, so `_node_name` finds nothing; Ruby's method node is `method`, absent from
  `_DEF_KIND_BY_NODE`; Rust's node is `function_item` while the map lists `fn_item`. Consequence:
  a file in one of those four is read and graded but has **no function or class for the depth gate
  to stand on**, so it is capped below `audited_deep` — a real limit on what "multi-language
  grounding" buys a consumer, and the same gap-between-adjacent-capabilities shape as
  `DF-AUD-APAA-D`(b), one level deeper. **Deliberately not fixed in Story 10.2:** AC3 is fenced to
  a *grammar-resolution* fix, and widening the definition vocabulary changes which files reach
  `audited_deep` in any polyglot repository — a capability change owing its own ACs and its own
  cartridges, not a line squeezed into a specification-correction story. Blast radius on this
  repository is zero (`git ls-files` matches 0 `.c/.h/.cpp/.hpp/.cc/.cxx/.hh/.rb/.rs` files).
  **Pinned in BOTH directions meanwhile** by `TC-ArgusAgent-INTAKE-003-09`
  (`tests/test_multilanguage_audit.py::_YIELDS_DEFINITIONS`), which fails if one of the four
  starts extracting definitions as loudly as if one of the working six stopped — so the limit
  cannot silently widen, and cannot silently close while the README and FR7 still describe it.
  Close = extend `_DEF_KIND_BY_NODE` / `_node_name` per grammar with a fixture per language,
  re-measure the dogfood verdict (more files reaching `audited_deep` moves ratios), and update
  FR7's measured-shortfall bullet, the README limits paragraph and this entry together.
  - id: DF-10-2-A
  - owner: Engineering Lead
  - target_story: NONE — unscheduled; **Engineering Lead to schedule.** Not folded into Story 10.4
    (which owns grammar *diagnosis*, a different function) nor 11.4 (runtime version bounds);
    naming a wrong owner-story is how a deferral becomes nobody's (AI-E9-8).
  - category: capability
  - severity: 🟡

- **DF-AUD-APAA-E** — Four CLI flags are accepted by the shipped parser and specified
  nowhere. `--passes`, `--skip-pass`, `--ignore-path`, `--ignore-pattern` have ZERO occurrences
  across epics, stories, PRD, addendum, both prior change proposals, CHANGELOG and README,
  while FR30 and architecture L226 specify four parameters and Story 1.7 declares the flag
  names LOCKED. They entered in the root commit `084c6a7` (the 426-file separation seed) and
  `b05fa4c`, so no gate ever saw them. They were also entirely INERT until 2026-08-09 — every
  production call site dropped the `request` argument — so no consumer can depend on their
  behaviour and neither blessing nor removal is a behavioural break. Two of them
  (`--ignore-path`, `--ignore-pattern`) suppress SECURITY findings with no threat model. Close
  = Story 10.3: rule on each flag (bless with ACs + CHANGELOG entry, or remove), require a
  threat model before blessing either suppression flag, and pin parser-vs-contract equality
  with a test so the two cannot diverge again.
  - id: DF-AUD-APAA-E
  - owner: Governance Owner
  - target_story: 10-3-invocation-contract-says-what-the-cli-accepts
  - category: governance
  - severity: 🟡

- **DF-AUD-APAA-F** — A grammar that fails to LOAD is reported as a grammar that is MISSING.
  `index/ast_index.py:266` catches `(ImportError, Exception)` and returns `None`, so an
  uninstalled grammar and an installed-but-broken one (ABI mismatch, corrupt build) both
  surface as `grammar_missing_<lang>` — and the remedy the report gives an operator ("install
  the package") is wrong in the second case. The tuple is redundant (`Exception` subsumes
  `ImportError`), which hides that the catch is total; it is the only bare `except: …pass` in
  `argus/`, a shape AR10 and Story 4.3 explicitly forbid. Degradation itself is correct — the
  file is recorded `ast_eligible=False`, never a false deep claim — so this is a
  diagnosis-quality defect, not a correctness one. Close = Story 10.4: split the arms, add a
  distinct broken-grammar reason token, and pin both tokens with a test.
  - id: DF-AUD-APAA-F
  - owner: Engineering Lead
  - target_story: 10-4-a-grammar-that-fails-to-load-names-why
  - category: process
  - severity: 🟢

---

## Ownership resolutions — 2026-08-10b

Appended by `bmad-correct-course` after [sprint-change-proposal-2026-08-10b.md](sprint-change-proposal-2026-08-10b.md).
**Append-only (§3.4): nothing above this heading was edited, reordered or deleted.** Every entry below
resolves an OWNER, not a technical finding — the original entries keep their text and their severity.

- **DF-7-2-A — OWNER NAMED. XAgent007.** *(Was: open and UNOWNED since Epic 7; restated as unowned by
  Story 9.2 and by the superseded 2026-08-10 proposal.)* The human TP/FP adjudication is the **only**
  step that can clear the ≥80%-precision attested-externalization gate. XAgent007 is recorded as the
  **primary adjudicator**, filling the Engineering Lead role in `precision-validation-protocol.md` §2.
  The QA Lead second and the external tie-break remain unfilled and are only required on a borderline
  finding (§4). **Scheduled as Epic 13** (13.1 corpus → 13.2 adjudication → 13.3 record-and-decide);
  Story 13.2's start condition — *"the adjudicator is named in `sprint-status.yaml`"* — is now **met**.
  **The item is NOT closed:** an owner is named, the measurement has not been run, and
  `protocol_cleared` remains `False` at `argus/precision/replay_harness.py:223`.
  - id: DF-7-2-A
  - owner: **XAgent007 (Engineering Lead role, protocol §2 primary adjudicator)** — was UNOWNED
  - target_story: 13-2-adjudicate-every-finding-by-a-named-human
  - status: OPEN, owned
  - severity: unchanged

- **DF-6-6-A / -P1 / -P2 — OWNER NAMED by inheritance. XAgent007.** These describe the human half of the
  same adjudication and were re-recorded as UNOWNED when the plan closed after Story 9.2. They are
  **absorbed into Story 13.2**, which closes each on the merits or re-records its remaining scope with a
  reason. Owner follows DF-7-2-A. Entry text unchanged.
  - target_story: 13-2-adjudicate-every-finding-by-a-named-human
  - status: OPEN, owned

- **H0 — CLOSED via the pre-authorised option (b).** `epics.md` recorded two acceptable closures for the
  unowned handoff-filing action: **(a)** a named owner files H1–H4 against the Minions backlog, or
  **(b)** it is explicitly recorded that filing is the operator's own step, taken outside this workflow.
  **The operator (XAgent007) elects (b).** H0 is **no longer UNOWNED**.
  **Scope of the closure, stated so it is not read as stronger than it is:** this ends the *ownership*
  gap — the failure mode where a handoff exists in a document and in no backlog. **It does not mean
  H1–H4 have been filed.** Until they are, the integration remains planned-and-relocated and this
  repository's CI cannot verify any of it. Assumption **A5 remains ⚠️ UNSUPPORTED**, and H3's
  blocking-vs-advisory policy decision is still required before that gate can be made blocking.
  - id: H0
  - owner: **XAgent007 (operator's own step, outside this workflow)** — was UNOWNED
  - status: CLOSED (ownership) / NOT FILED (execution)

**Ledger state after this append.** DF-7-2-A and DF-6-6-A/-P1/-P2 are owned but open. H0's ownership is
closed. The ≥80% gate is **NOT CLEARED** and nothing in Epics 10–12 clears it. The remaining open ledger
entries — DF-6-7-A (HITL wiring), DF-8-4-B (bytes-example half), DF-8-4-C, DF-8-4-D, DF-8-5-B, DF-8-5-C,
DF-9-2-C — are **not** claimed by this append and still need a named human or an explicit decision to
abandon. DF-8-2-A, DF-8-3-A and DF-8-3-C are now owned by Story 12.1 (the `pipeline.py` extraction they
all gate on).

---

## Release triage of the remaining open entries — 2026-08-10b

Operator asked whether the seven still-unowned entries are **required for the planned V1.5 public
release**. Each was re-read and re-measured against Epics 10–13 and the independent-developer audience.
**Append-only (§3.4): nothing above this heading was edited.** Original entries keep their text and
severity; what is recorded here is a disposition.

- **DF-9-2-C — CLOSED. Already fixed; the ledger was stale.** Re-measured with the entry's own
  instrument: `git ls-files argus/dogfood/` returns **five `.py` files and no `.pyc`**, and
  `git ls-files | grep -c '\.pyc$'` returns **0** — no compiled artifact is tracked anywhere in the
  repository. The three `.cpython-312.pyc` files the entry describes were untracked at some point after
  2026-08-09 and the closure was never recorded. Not release-relevant either way.
  - status: **CLOSED 2026-08-10b — verified by re-measurement, not by report**

- **DF-8-4-D — RELEASE-RELEVANT. Absorbed into Story 12.8.** `argus/cli.py:295-299` catches base
  `ValueError`; Pydantic's `ValidationError` is a `ValueError` subclass, so an internal defect is
  reported as an expected typed *"audit failed"* degradation. **Severity re-assessed for the new
  audience, and the original 🟢 is not rewritten:** it was correct when every user could read a stack
  trace. For a public CLI a masked bug costs the user a next action — which **FR37 forbids** — and costs
  the maintainer the bug report. Sits on the **public entry point**.
  - target_story: 12-8-the-tool-explains-itself · status: OPEN, owned

- **DF-8-5-C — RELEASE-RELEVANT. Absorbed into Story 13.1.** `proof_run.py:764-765` passes
  `precision=Fraction(0, 1), n=0` as **literals**, publishing *"N=0 labeled cartridges populated, floor
  N=5"* into `minions-dogfood-proof.md:87` while the shipped registry measures **5 distinct rule classes
  across 7 populated rows**. The figure **understates**, so it never made a gate look cleared — but
  Epic 13 measures that corpus and Story 11.1 puts precision-gate status on every user surface.
  - target_story: 13-1-decide-what-validation-set-is-then-build-it · status: OPEN, owned

- **DF-8-5-B — NOT release-blocking; ENABLER. Absorbed into Story 12.1.** The three committed-artifact
  rot checks re-break on any `argus/**` composition change with no warning (`-03`/`-06` were RED across
  four consecutive commits; Story 8.5 re-derived three times). Invisible to users. **Epic 12 changes
  `argus/**` more than any epic since Epic 6** — 12.1 restructures `pipeline.py`, 12.2/12.3 wire into it,
  12.6 adds a module — so the structural two-step lands repeatedly. Same reasoning that promoted the
  `pipeline.py` extraction from enabler to gate.
  - target_story: 12-1-pipeline-stops-breaching-its-own-limit · status: OPEN, owned

- **DF-6-7-A — PLAN INCONSISTENCY, now assigned. Absorbed into Story 10.5.** FR23 (human STOP/PROCEED
  escalation, default-STOP) is **in the binding FR contract** and delivered only as a **library seam**;
  nothing in `pipeline.py` or `cli.py` invokes it. **This is the identical defect class as FR27/NFR-D1 —
  a built, unwired capability — which the 2026-08-10b proposal made Story 12.3 while leaving FR23
  unlisted. The inconsistency was introduced by that proposal and is recorded rather than quietly
  fixed.** Resolved by *not guessing*: Story 10.5 gains a **reverse sweep** — FR1–37 for requirements
  with no reachable production call site — and **FR23 takes a dated disposition by name** (wired, or
  recorded as a library seam for V1.5 with the call site deferred and a reason).
  - target_story: 10-5-a-v1-commitment-is-delivered-or-explicitly-not-v1 · status: OPEN, owned

- **DF-8-4-B (bytes-example half) — NOT release-required.** The entry itself already assessed the
  suggested check as *"duplication rather than coverage"* — byte-equality over the surfaces that matter
  is held by `TC-ArgusAgent-DOCS-001-03`..`-06`. Internal test hygiene.
  - status: OPEN, UNOWNED — deliberately not scheduled

- **DF-8-4-C — NOT release-required, and arguably moot.** A missing before/after quote in `CHANGELOG.md`
  for an Epic-8 rendering change. Its purpose is to help **existing integrators** migrate; a **first**
  public release has none. Revisit only if a second release changes the same surface.
  - status: OPEN, UNOWNED — deliberately not scheduled

**Triage result: 2 of 7 bear on the public release** (DF-8-4-D, DF-8-5-C), plus one enabler (DF-8-5-B)
and one plan inconsistency (DF-6-7-A). **No new story was created** — all four are AC additions to
stories that already own the surface. DF-8-4-B and DF-8-4-C remain open and unowned **by decision**,
which is a disposition, not a drift.

---

## Story 10.3 closure + new filings — 2026-08-10

Appended by Story 10.3 (`10-3-invocation-contract-says-what-the-cli-accepts`).
**Append-only (§3.4): nothing above this heading was edited, reordered or deleted** — including
`DF-AUD-APAA-E`'s original entry, which stays byte-intact above and is *annotated* here rather than
rewritten. `git diff --numstat` on this file is `+n / -0`.

### `DF-AUD-APAA-E` — CLOSED, and the entry it closes was WRONG IN THREE WAYS

Closed by Story 10.3. The remedy the entry prescribed was carried out — every flag took a recorded
ruling, a threat model was written before either suppression flag was blessed, and parser-vs-contract
equality is pinned by test. But **re-measuring the entry before acting on it changed the story three
times over, and the closure would be dishonest if it recorded only the remedy.**

**1. The enumeration was FOUR. Measured, it is SIX.** The entry names `--passes`, `--skip-pass`,
`--ignore-path`, `--ignore-pattern`. Differencing the LIVE parser (`argus/cli.py::build_parser` walked
at run time: **15 actions on `audit` — `-h`, the `repo` positional and 13 optional flags**) against the
binding contract corpus (`E-PRD/prd.md`, `E-PRD/addendum.md`, `architecture.md`, `epics.md`,
`CHANGELOG.md`, `README.md`) found **two more with zero occurrences anywhere in it**:

- **`--reports`** — entered in **`084c6a7`**, the *same* 426-file separation seed as the ledger's four,
  so it is the identical defect class and was missed only because the list was hand-counted. **Worse in
  one respect: a committed workflow depends on it** — `.github/workflows/argus-student-audit.yml:48`
  runs `--reports "final-verdict,coverage-ledger,security-review,vacuous-tests"` — so removal was never
  free for this one the way it was for the other five. It is also **conditionally inert**:
  `pipeline.py` only renders when `--report-dir` is set, so `--reports` alone renders nothing.
- **`--strict`** — entered in **`ae5f00c`** (Epic 8) alongside `--coverage-scope`, but only
  `--coverage-scope` got a CHANGELOG entry. It is the **enforcement of the FR1 determinism pin** and
  `argus/cli.py` names it as that pin's binding statement, so it was under-specified, not unwanted.

Provenance measured with `git log -S"--<flag>" -- argus/cli.py`. `--report-dir` was assessed and
deliberately **excluded** from the six: thin, but present and consumer-facing (`README.md`,
`action.yml`). *A hand-counted list has now been the wrong instrument three stories running (10.2 drew
the same lesson twice); the closure of this entry is therefore a **closure guard**, not a list.*

**2. `--ignore-pattern` DEFEATED the Live-Key Safeguard, and nothing was recorded.** The entry says the
two suppression flags "suppress SECURITY findings with no threat model" and treats them as a pair.
Measurement separates them decisively. `argus/detectors/secret_suppression.py`'s own module docstring
promises that *"high-confidence live production key signatures override folder glob exemptions unless
annotated with an explicit inline line comment"* — and `evaluate_suppression` ran the CLI-supplied
`ignore_patterns` arm **above** that safeguard, matching by **bare substring**. Executed on this tree
2026-08-10 (`file_path="argus/prod.py"`, snippet `AKIAABCDEFGHIJKLMNOP`):

| invocation | result |
|---|---|
| no flags | `(False, None)` — reported |
| `--ignore-path 'argus/**'` | `(False, None)` — **safeguard HELD** |
| `--ignore-pattern "AKIA"` | `(True, 'custom_ignore_pattern')` — **suppressed** |
| `--ignore-pattern "A"` | `(True, 'custom_ignore_pattern')` — **one character, suppressed** |

11 of 24 (live-key pattern × hostile pattern) combinations escaped. **And nothing was recorded at all**:
`argus/detectors/secret_scan.py` bound the reason token to `_reason` and `continue`d, so the operator's
*inputs* were persisted through `AuditRequest.to_provenance_payload()` while the *effect* — that a
secret was found and suppressed — left no trace anywhere. That is unevidenced green on the security
surface, in a tool whose own report recommends the flag.

**3. The reverse direction existed and the entry never looked for it.** Parser-vs-contract equality has
two directions. `README.md:195` documented `argus --budget 500 --materiality critical`, which executed
gives `argus: error: argument command: invalid choice: '500'` and **`SystemExit 2`**: the required
`audit` sub-command was missing and `--materiality` is not a flag this parser has ever accepted. **The
first command a new user copied failed.**

**Dispositions taken — none of the six was removed:**

| flag | ruling | basis |
|---|---|---|
| `--passes`, `--skip-pass` | **BLESSED** | fully consumed, recorded in run-state provenance, and the narrowing was already disclosed to the operator |
| `--reports` | **BLESSED**, with its conditional inertness stated | a committed workflow depends on it; concealing that it renders nothing without `--report-dir` would be this epic's own defect |
| `--strict` | **BLESSED** | the only lever that refuses a drifted tree; removing it would delete the FR1 pin's enforcement |
| `--ignore-path` | **BLESSED** | bounded by the Live-Key Safeguard *measurably*, and it is the remedy Argus's own report recommends |
| `--ignore-pattern` | **BLESSED — the conditional branch, because the condition was MET** | the bless was conditional on the layering being fixed and the suppression being recorded. Both landed, so the parser-removal fallback was not taken. `AuditRequest.ignore_patterns` is untouched and `argus/models.py` is byte-unchanged, so the additive-only schema policy is not engaged. |

Each blessed flag carries a behavioural acceptance criterion pinned by test — not a sentence — a
CHANGELOG entry in the *documented-not-new* register, and an entry in the contract registry naming the
document that specifies it.

**Enforced by:** `tests/test_invocation_contract.py` (`TC-ArgusAgent-CLI-001-35`..`-41`,
`TC-ArgusAgent-DOCS-001-28`), `tests/test_cli_flag_contract.py` (`-42`..`-49`),
`tests/test_secret_suppression_recording.py` (`TC-ArgusAgent-SECRET-001-15`..`-22`); registered in
`architecture.md` §Enforcement.

- id: DF-AUD-APAA-E
- owner: Governance Owner
- target_story: 10-3-invocation-contract-says-what-the-cli-accepts
- status: **CLOSED 2026-08-10** — remedy delivered, and the entry's own enumeration corrected from four
  to six with the two new instances named and their provenance measured

### New filings

- **DF-10-3-A** — **argparse's usage exit code `2` collides with the BLOCKED verdict code.** An
  argparse usage error (a mistyped flag, a missing `audit` sub-command) exits **`2`**, and the published
  AR3/FR18 wire contract defines `0`=RELEASE_READY · **`2`=BLOCKED** · `3`=INSUFFICIENT_COVERAGE ·
  `1`=crash. `CHANGELOG.md`'s decision table states *"`1` is not in this table because no verdict
  produces it"*; **usage errors are named nowhere.** A CI step branching on exit `2` therefore reads a
  typo in its own workflow as *"Argus found a blocking defect"* — a false blocking verdict, the failure
  mode this project treats as lethal. Measured 2026-08-10 by executing `README.md:195`'s own documented
  invocation. **Deliberately NOT fixed by Story 10.3:** changing a published exit code touches
  `action.yml`, both workflows and every integrator already branching on it, which is irreversible for
  consumers and exceeds a story-level ruling (10.3 / DN-11). Story 10.3 removed the *immediate* exposure
  by making every committed invocation parse (`TC-ArgusAgent-DOCS-001-28`); the collision itself
  remains. Candidate resolutions, none chosen here: map usage errors onto the reserved crash code `1`;
  introduce a distinct usage code outside `{0,1,2,3}`; or document the collision in the wire contract
  and require consumers to disambiguate on the stdout summary line's presence.
  - id: DF-10-3-A
  - owner: **Engineering Lead**
  - target_story: **12-9-publishing-and-release-surface** — the release-surface story that already owns
    `action.yml` and the published consumer contract; to be scheduled there or explicitly re-homed by
    the Engineering Lead, never left unowned (AI-E9-8)
  - category: contract
  - severity: 🟡

- **DF-10-3-B** — **built-in secret suppressions are not disclosed.** Story 10.3 records and discloses
  suppressions an *operator's own flag* caused (`--ignore-path` / `--ignore-pattern`). It deliberately
  does **not** disclose the pre-existing built-in layers — the public sentinels, the inline
  `# argus:ignore` annotation and `DEFAULT_TEST_PATH_PATTERNS` — because no operator flag caused them
  and folding them in would move the finding count on runs that pass no flags at all (10.3 / AC4.5). A
  reader of a report still cannot tell how many candidate secrets the built-in layers absorbed. This is
  a **reporting enhancement, not a correctness defect**: no live production key can be suppressed by any
  of these paths except an explicit inline annotation, which is reviewable in the diff.
  - id: DF-10-3-B
  - owner: **Engineering Lead**
  - target_story: **NONE — unscheduled; Engineering Lead to schedule** against the Epic-12 report-quality
    surface once Epic 12's story list is fixed. Deliberately not asserted onto a story id that does not
    yet exist (AI-E9-8: a wrong owner-story is how a deferral becomes nobody's).
  - category: capability
  - severity: 🟢

- **DF-10-3-C** — **`--ignore-pattern` matches by bare substring, so a short pattern is a wide net.**
  After Story 10.3 no `--ignore-pattern` can reach a high-confidence live production key, and any
  suppression it causes is recorded and disclosed. Within everything the Live-Key Safeguard does not
  cover — the generic assigned-secret and high-entropy classes, which are the majority of real findings
  — `pat in snippet` is unchanged, and `--ignore-pattern "a"` still suppresses nearly all of them at
  once. Bounding the *matching semantics* (anchoring, a minimum pattern length, requiring a path scope
  alongside the pattern) is a **behavioural redesign of a shipped flag** and was explicitly out of
  Story 10.3's scope (AC3.4 states the residual risk; architecture §G's suppression threat model
  records it as accepted). Filed rather than silently redesigned.
  - id: DF-10-3-C
  - owner: **Engineering Lead**
  - target_story: **NONE — unscheduled; Engineering Lead to schedule.** Deliberately not folded into an
    Epic-12 report story (a different function) nor Epic 13 (precision measurement): naming a wrong
    owner-story is how a deferral becomes nobody's (AI-E9-8). The owner is named, which is the part
    that must never be missing.
  - category: security
  - severity: 🟡

---

## Story 10.4 closure + new filings — 2026-08-10

Appended by Story 10.4 (`10-4-a-grammar-that-fails-to-load-names-why`).
**Append-only (§3.4): nothing above this heading was edited, reordered or deleted** — including
`DF-AUD-APAA-F`'s original entry, which stays byte-intact above and is *annotated* here rather than
rewritten. `git diff --numstat` on this file is `+n / -0`.

### `DF-AUD-APAA-F` — CLOSED, and the entry counted TWO causes where there are FOUR

Closed by Story 10.4. The remedy the entry prescribed was carried out — the arms are split, the tokens
are distinct, and both are pinned by test. But **re-measuring the entry before acting on it changed the
story, and a closure that recorded only the remedy would repeat the defect the entry describes: a
record that names a cause which is not the cause.**

**1. The enumeration was TWO. Measured, it is FOUR — and all four emitted the SAME token.** The entry
(and `epics.md:1906-1912`) describe two states: *missing* vs *installed-but-broken*. Executing
`build_ast_index` against a `.go` fixture on this host on 2026-08-10, patching only the
`importlib.import_module` seam inside `argus/index/ast_index.py`, measured four:

| # | What the operator actually has | Recorded BEFORE | Records NOW | Remedy that works |
|---|---|---|---|---|
| 1 | the grammar package is not installed (`ModuleNotFoundError`) | `grammar_missing_go` | `grammar_missing_go` *(unchanged)* | `pip install tree-sitter-go` |
| 2 | the package **is** installed; Argus does not know its entry point | `grammar_missing_go` | `grammar_entrypoint_missing_go` | **nothing the operator can do — an Argus defect** |
| 3 | the package is installed and **broken** for this runtime | `grammar_missing_go` | `grammar_load_failed_go` | reinstall/rebuild; check the core–grammar version pair |
| 4 | the `tree_sitter` **core** is not importable | `grammar_missing_go` | `tree_sitter_runtime_missing` | `pip install tree-sitter`; **every** language is down |

**Three of the four implied a remedy that cannot work**, and cause 2's is the entry's own worst
sentence — it tells an operator to install a package they already have.

**Provenance of the two the entry did not have.** Cause 2 is **the cause the entry's own prescribed
repair does not catch**: splitting the `except` changes nothing there, because *nothing raises* —
`getattr(mod, entry_point, None)` simply returns `None` and the code falls through. Story 10.2
measured this independently, fixed its two live instances (TypeScript and PHP, via
`_ENTRY_POINT_BY_LANGUAGE`) and handed the **class** forward to this story by name
(`10-2-…md:169-170`). Cause 4 appears in **no prior document** — ledger, epic or story — and produces
the maximally wrong message: "install `tree-sitter-go`" while every language is down.

**2. The only surface that shows the token was UNTESTED, and it is ALL-OR-NOTHING.**
`parse_failure_reason` has three consumers; exactly one reaches an operator —
`argus/reports/generator.py::_render_readability_warning`. Measured with
`pytest --cov=argus.reports.generator` over **every** test file that imports the generator
(`test_report_generator`, `test_report_honesty`, `test_report_surface_consistency`, `test_release_note`,
`test_release_preflight`, `test_critical_eligibility_pipeline`, `test_secret_scan_precision`):
**`Missing … 316, 322-336`** — the entire grammar-counting block, the package lookup and the callout
body had **never executed in this suite**. Consequence, and the reason Story 10.4 grew a whole AC for
it: *splitting the token without covering this file would have silently disabled the one message an
operator ever sees, and nothing in the repository would have turned red.* Worse, the removed code
recovered the language by string arithmetic against cause 1's prefix, so
`grammar_entrypoint_missing_go` would have been **skipped outright** (silent) — and the obvious
widening to `startswith("grammar_")` would have sliced it into the "language"
`entrypoint_missing_go` and printed `pip install tree-sitter-entrypoint_missing_go` (misdirect).
Classification now lives in ONE pure module both sides import.

**3. Two coordinates in the entry are stale; the anchor is not.** The entry cites
`index/ast_index.py:266`; Story 10.2's Dev Agent Record says `:294`; it was measured at **`:350`** on
the tree this story started from. **Three coordinates for one clause in two days** — recorded here as
the standing argument for locating by anchor text (`except (ImportError, Exception):`) rather than by
line number.

**4. What is NOT closed by this entry.** `DF-10-4-A`, `DF-10-4-B` and `DF-10-4-C` below — all three are
NEW findings of this story, filed rather than folded in, because each belongs to a story that owns that
surface by name. `DF-10-2-A` (C/C++/Ruby/Rust ground but extract zero definitions) is a **different**
failure — those grammars load and parse — and is deliberately not conflated with this one.
**Verdict impact: NONE, asserted.** `pipeline.py`, `audit/grounding.py` and `vacuous_test.py` branch on
the `parse_failed` / `ast_eligible` booleans and never on the token; `TC-ArgusAgent-INDEX-001-114` runs
a real audit under each of the four causes and requires the verdict, counts and findings to be
identical across all four. `parse_failed` stays `False` (no parse was *attempted*), no field was added,
`AstIndex.schema_version` stays `"2"` and `CACHE_KEY_SCHEMA_VERSION` stays `"3"`.
**Gate status: NOT ESTABLISHED.** Local gates were re-run and are recorded as LOCAL in the story file;
no CI run covers this tree, run ids are sha-scoped, and the run that would evidence this commit does
not exist until an operator pushes.

- status: **CLOSED 2026-08-10** — remedy delivered, and the entry's own enumeration corrected from two
  causes to four, with the entry-point fall-through and the core-runtime arm named and their provenance
  measured

### New filings

- **DF-10-4-A** — **the readability callout is ALL-OR-NOTHING, so a polyglot repository is told
  nothing.** `_render_readability_warning` returns early at `if eligible: return []` — it fires only
  when **zero** files parsed. In this story's own persona's repository — *"an operator auditing a
  polyglot repository"* — the Python files parse, so `eligible > 0`, so a failed Go or Rust grammar is
  **invisible in the report** no matter how precisely Story 10.4 now names its cause. Measured
  2026-08-10; pinned in both directions by `TC-ArgusAgent-REPORT-002-29`, which fails if the trigger is
  either widened or removed, so neither story can silently take the other's ground. **Deliberately NOT
  fixed by Story 10.4** (DN-7): widening the trigger adds a *per-file point-of-downgrade* surface, and
  Story 12.5 owns that surface by name (*"its absence and the reason appear in the tool's own output at
  the point the file is downgraded"*, `epics.md:2328-2330`). Story 10.4's obligation was only that the
  **already-existing** callout does not go silent or misdirect under the new token set. **This is the
  residual Story 10.4 knowingly leaves open**: if 12.5 slips, a mixed Python/Go audit still says nothing
  about its failed Go grammar.
  - id: DF-10-4-A
  - owner: **Engineering Lead**
  - target_story: **12-5-default-install-grounds-languages-it-claims**
  - category: capability
  - severity: 🟡

- **DF-10-4-B** — **`DetectorResult.degraded` has ZERO production readers: the reason is recorded and
  then dropped.** Measured 2026-08-10, whole-tree: `grep -rn "\.degraded" argus/` (excluding
  `degraded=` constructions) returns **0 hits**. Three detectors (`vacuous_test`, `orphan_code`,
  `tool_runner`) build `DegradedCondition` tuples, `detectors/base.py` declares the field, **21 tests
  assert on it — and no code in `argus/` ever reads it.** So `vacuous_test.py:400`'s careful
  `ast_entry.parse_failure_reason or "not_ast_eligible"` writes a diagnosis into a structure nothing
  consumes. This is `DF-6-7-A`'s class exactly — *a delivered seam with no reachable production call
  site* — and it is the same shape as Story 10.3's central finding (*"the operator's INPUTS are
  persisted while the EFFECT leaves no trace"*), one level down. **Deliberately NOT fixed by Story
  10.4**: giving it a reader is either a new report surface (12.5's) or an outcome-names-its-next-action
  change (12.4's), and Story 10.5's fourth AC is already the reverse-sweep for exactly this class
  (`epics.md:1951-1958`). Recorded here so 10.5 inherits a **measurement** instead of a rediscovery —
  the courtesy Story 10.2 paid Story 10.4.
  - id: DF-10-4-B
  - owner: **Governance Owner**
  - target_story: **10-5-a-v1-commitment-is-delivered-or-explicitly-not-v1**
  - category: capability
  - severity: 🟡

- **DF-10-4-C** — **the exception CLASS behind a broken grammar is diagnosed and then discarded.**
  Story 10.4 classifies by arm position and records a token; it deliberately persists **no** exception
  detail. An operator debugging `grammar_load_failed_rust` may still want to know whether the load died
  with a `ValueError` (bad capsule), a `TypeError` (a missing `()` on the entry point) or an `OSError`
  (the shared object would not open) — three quite different next actions. **Deliberately NOT fixed by
  Story 10.4** (DN-5): a persisted free-text slot's only natural filler is `str(exc)`, which carries a
  host filesystem path into a shareable artifact (NFR-S1, measured — the real message shape is
  `/home/…/libfoo.so: cannot open shared object file`), and `argus/` has **no logging facility** to put
  it anywhere else. It would also cost a second `AstIndex` schema bump inside one epic on a 🟢
  diagnosis defect. The **type/class only — never the message** is the safe payload, and it belongs on
  the surface that renders it: Story 12.8 already *"extends 10.4's diagnosis principle to the user
  surface"* and names *"missing grammar"* among the errors it must make actionable (`epics.md:2405`).
  - id: DF-10-4-C
  - owner: **Engineering Lead**
  - target_story: **12-8-the-tool-explains-itself**
  - category: capability
  - severity: 🟢

- **DF-10-4-D** — **the committed-dogfood-artifact guards break on `git add` alone, so ANY story that
  adds a module to `argus/` halts on five reds it did not cause.** Filed by operator decision
  (XAgent007, 2026-08-10) after Story 10.4 halted on exactly this. **Measured mechanism, and it is
  strictly stronger than `DF-8-5-B`'s:** `argus/dogfood/partition_plan.py::enumerate_minions_source_files`
  enumerates via `git ls-files argus`, and `git ls-files` reports the **INDEX**, not `HEAD`. So the
  planned population moves the instant a new `argus/**` module is **staged** — before any commit, and at
  the exact moment `E.5` / `AI-E8-1` *requires* the `git add` (*"`git diff` cannot see an untracked
  path"*, the defect that shipped Epic 8's own story file untracked). `DF-8-5-B` measured the trigger as
  *"any commit that changes `argus/**` composition"*; the trigger is in fact *"any story that stages an
  `argus/**` source file"*, which no story can avoid and which fires mid-implementation. **Measured blast
  radius, Story 10.4, 2026-08-10:** one new module (`argus/shared/grammar_status.py`) moved the planned
  population **71 → 72**, and with it total physical LOC (18418 → 19783), the sized ceiling `$X`
  (443 → 450), the recorded cut edges (49 → 57) and the critical-set size — turning **five** tests red
  across **three** committed artifacts: `TC-ArgusAgent-DOGFOOD-001-03`, `-06`, `-41`
  (`minions-dogfood-partition-plan.md`, `minions-dogfood-budget-plan.md`) and the two proof assertions
  over `minions-dogfood-proof.md`. A **second, independent** trigger fired in the same story: ~700 added
  physical lines tipped an `NFR-SC1` bin-packing boundary (a unit of 40 files / 14100 LOC no longer fit
  under the 15000-LOC soft target, so it became 39 / 14793), changing two of three `partition_id`
  sha256 values on their own. Either trigger alone is sufficient; a story that adds a module hits both.
  **Why this is now 🟡 rather than `DF-8-5-B`'s 🟢:** it has measurably **halted a story** rather than
  merely surprised a developer, and the remaining roadmap walks into it repeatedly — **Story 12.1**
  splits `pipeline.py` (1331 lines vs the 1200 cap) and therefore adds modules *by construction*,
  **12.2** wires the deep-audit seam, **12.6** adds an MCP adapter module, **11.5** changes the wheel's
  module set, and **12.3** wires `cache/memo_store.py`. There is also a **bootstrap ordering hazard**:
  12.1 is the story that owns the remedy *and* the story most certain to trip the defect before the
  remedy exists, so it must regenerate first and fix second, in that order. **The remedy is unchanged
  from `DF-8-5-B` and must not be a loosened assertion:** either a documented regeneration entry point
  **named in the failure message of every one of the five assertions**, or a CI step that regenerates and
  fails on a diff. If a narrower fix is preferred, the honest one is to decide — and record — whether the
  artifacts are meant to describe the **committed** tree (`git ls-files --with-tree=HEAD`, so staging is
  inert) or the **working** tree (today's behaviour); they currently claim `HEAD` provenance in their own
  Provenance block while enumerating the index, and those are two different trees. **Story 10.4 FILED
  this and deliberately did NOT fix it:** the coupling lives in `argus/dogfood/`, which is outside 10.4's
  AC7.6 write set, and changing what the dogfood enumerates is a verdict-adjacent change 10.4's `DN-9`
  fences to Epic 11/12. What 10.4 *did* do, under operator authorisation, is regenerate the three
  artifacts through their own renderers at a commit that genuinely contains the deltas they describe —
  which restores truth for one story and closes nothing for the next one.
  - id: DF-10-4-D
  - origin_story: 10-4-a-grammar-that-fails-to-load-names-why
  - owner: **Engineering Lead**
  - target_story: **12-1-pipeline-stops-breaching-its-own-limit** (which already ABSORBS `DF-8-5-B`, the
    same class measured one trigger short — supersede or close them together, never separately)
  - category: developer-experience
  - severity: 🟡

## Deferred from: code review of 10-4-a-grammar-that-fails-to-load-names-why (2026-08-11)

Appended by the `bmad-code-review` gate, iteration 1 (verdict: PASS). **Append-only (§3.4): nothing
above this heading was edited, reordered or deleted.**

- **`_render_grammar_remedy`'s per-cause branching has no exhaustiveness guard of its own**
  (`argus/reports/generator.py:295-332`). `_get_parser_for_lang`'s AST-closure guard (AC5.2,
  `tests/test_grammar_diagnosis.py::-115`) forces any FUTURE fifth `GrammarFailure` member to be
  registered and driven through the loader, but nothing forces a matching branch in
  `_render_grammar_remedy`: its last branch is an unconditional fallthrough (a comment, not an
  assertion), so a hypothetical fifth cause would silently render the core-runtime remedy instead of
  failing loudly — the one place in Story 10.4's own design that does not match the "fail loudly, never
  silently" standard it otherwise establishes (E.4's spirit, applied to the report side rather than the
  loader side). **Not a defect today**: `GrammarFailure` has exactly the four members AC1.1 of Story
  10.4 locks, and `tests/test_grammar_diagnosis.py::REPORT-002-26/-27` behaviourally exercise all four
  correctly. No operator-visible harm exists on this tree. Verified by reading
  `argus/reports/generator.py:295-332` directly and confirming no `else: raise` / no AST-closure
  equivalent to `-115` exists for this function.
  - id: DF-10-4-E
  - origin_story: 10-4-a-grammar-that-fails-to-load-names-why (code review, iteration 1)
  - owner: **Engineering Lead**
  - target_story: **NONE — unscheduled; Engineering Lead to schedule** against whichever future story
    next extends `GrammarFailure`'s membership (none proposes a fifth cause today)
  - category: developer-experience
  - severity: 🟢

## Deferred from: Story 10.5 — the V1 delivery-closure sweep (2026-08-11)

Appended by Story 10.5 (*a V1 commitment is delivered, or it is explicitly not V1*), the last story
of Epic 10. **Append-only (§3.4): nothing above this heading was edited, reordered or deleted —
verified programmatically (`after.startswith(before)`), not by eye.** Every disposition below is
dated 2026-08-11 and was produced by measurement: a claim-shape parse of the whole `E-PRD/prd.md`
(forward) and a static `ast` import-reachability walk of `argus/**` from `argus/cli.py` (reverse),
both now committed as `tests/test_v1_commitment_closure.py`.

### The closing statement of the class — read this first

**This defect class was filed four times over five weeks and swept zero times.** `DF-AUD-APAA-A` and
`DF-AUD-APAA-B` (2026-07-04) named it exactly — *"ORPHAN relative to the shipped `run_audit`/CLI
path"*, *"has NO production caller … the security guarantee is proven only in tests"*. `DF-6-7-A`
filed FR23. `DF-10-4-B` filed `DetectorResult.degraded`. **Each was recorded as an instance; none
triggered a sweep**, and two of the four were pointed at `epic-7-minions-dogfood-proof-run` — an
epic that is `done` — so they could never be closed by the thing they named.
`implementation-readiness-report-2026-08-03.md:400` had even scored the blind spot eight days before
this story ran: *"The failures are all in the same blind spot: obligations the PRD binds without an
FR number. The requirement-ID pass scores 100%; **the unnumbered-obligation pass scores 68%**."* The
score was never acted on either. Measured today, the reverse sweep is **not one hit but four** —
FR23, FR24, FR26, FR29 — and **three of them had never been filed at all**, while
`architecture.md`'s *"No FR is unsupported"* certified all of them over a module-**placement** table.
**`tests/test_v1_commitment_closure.py` is what makes the fifth filing impossible:** a V1 commitment
now carries exactly one dated disposition or the suite is red, and a `wired` disposition is refuted
mechanically by the import graph rather than believed. A list closes today's instances; a closure
closes the class.

### Dispositions of entries that named this class

- **`DF-6-7-A` — CLOSED 2026-08-11 by disposition (not by wiring).** FR23 is disposed
  **`library-seam`** (Story 10.5, DN-3), and `E-PRD/prd.md`'s FR23 text is amended
  struck-not-deleted, dated and attributed, to record that the pattern-matched escalation evaluator,
  the resolution model and `DecisionRecordWriter` are **delivered and test-proven**
  (`tests/test_hitl_escalation.py`) while **their INVOCATION is deferred**. Measured 2026-08-11:
  `argus/governance/escalation.py` is not in the transitive import closure from `argus/cli.py`, and
  its single importer inside the package (`governance/decision_record.py`) is itself unreachable.
  **The reason has two halves and both bind:** (a) every call site lands in `argus/pipeline.py`,
  **1331 lines against the NFR-M1 cap of 1200**, byte-fenced to Story 12.1; and (b) the V1 default
  path is **unattended CI** (Journeys 3 and 5) with **no human to answer a default-STOP gate**, so a
  naive wiring would deadlock every automated audit. **The cost is stated, not hidden:** the
  §Cut-Order marks **FR23 non-negotiable core** — only FR24 is `[Tier B]` — and
  `implementation-readiness-report-2026-08-03.md:365` already flagged FR23 as stranded in a slippable
  epic. This closure de-scopes a non-negotiable-core capability's invocation to an unscheduled story.
  **It is the one decision in Story 10.5 an operator may reasonably overturn**, and the honest route
  to overturning it is a new Epic 12 story, not a quiet re-wiring.
  - id: DF-6-7-A
  - owner: **XAgent007 (Governance Owner)**
  - target_story: **NONE — unscheduled; Governance Owner to schedule** once Story 12.1 lifts the
    NFR-M1 gate on `pipeline.py` (the `DF-10-4-E` form: house-legal because a human is named)
  - status: **CLOSED (disposition recorded) / OPEN (invocation)** — superseded for tracking purposes
    by the FR23 amendment in `E-PRD/prd.md` and by `tests/test_v1_commitment_closure.py`, which turns
    red the day the seam becomes reachable and the disposition still says it is not

- **`DF-10-4-B` — DISPOSED 2026-08-11 and RE-TARGETED OFF STORY 10.5.** Story 10.4 filed it against
  10.5 so 10.5 would inherit a measurement rather than a rediscovery; that hand-off is hereby
  discharged. **`DetectorResult.degraded` is not an FR**, so it is not an AC4 hit — it is the same
  class **one level down**, and it is the evidence that the class is systemic rather than FR-shaped:
  a reason is computed, recorded and then read by nothing. Re-measured 2026-08-11 and **unchanged**:
  zero production readers. **It is not fixed here** — Epic 10 closes the record and ships nothing,
  and giving the field a reader is a product change in a fenced file. It now carries a **live**
  target instead of pointing at the story that is closing.
  - id: DF-10-4-B
  - owner: **Engineering Lead**
  - target_story: **12-4-every-outcome-names-its-next-action** (which owns *outcome names its next
    action*, the natural first reader of a recorded degradation cause) — with
    **12-5-default-install-grounds-languages-it-claims** as the secondary surface if 12.4 renders the
    cause only in the terminal and not in the persisted report
  - status: OPEN, owned — **no longer targeted at Story 10.5**
  - severity: 🟡 unchanged

- **`DF-AUD-APAA-A` — RE-TARGETED 2026-08-11 (entry text above is unchanged).** Its stated target,
  `epic-7-minions-dogfood-proof-run`, is an epic that is **`done`**, so the entry was **unclosable as
  written** — an orphan, in the register that exists to prevent orphans. Re-measured today: the
  `cache/` sub-package is still outside the closure from `argus/cli.py` (`memo_store.py` and
  `invalidation.py` unreachable; `key.py` is reachable but `MemoStore` is never constructed).
  ⚠️ **It is NOT an FR-delivery defect**, and Story 10.5's reverse sweep says so explicitly: **FR27
  is disposed `delivered-differently`, not `library-seam`.** FR27 promises *the same verdict for the
  same repository and APAA version*; the default run is zero-token and deterministic, so the property
  **holds by determinism rather than by cache**. Recording FR27 as undelivered would have been a
  false accusation — the failure mode this product exists to prevent — and this entry tracks the
  **mechanism**, not the requirement.
  - id: DF-AUD-APAA-A
  - owner: **Engineering Lead**
  - target_story: **12-3-memoization-mechanism-is-wired** (was: `epic-7-minions-dogfood-proof-run`, an
    epic already `done`)
  - status: OPEN, owned — mechanism deferred; **FR27 itself is delivered by determinism**
  - severity: 🟢 unchanged

- **`DF-AUD-APAA-B` — RE-RECORDED 2026-08-11 as open-and-unowned-BY-DECISION (entry text above is
  unchanged).** Same orphaned target as `-A`. Re-measured today: `read_in_scope`
  (`argus/index/partitioner.py`) still has **no production caller**, so the NFR-S4 manifest read
  boundary remains **unenforced at runtime** while its docstring asserts an off-scope read is
  impossible. Story 10.5 disposes the `work_manifest` commitment **`nfr-backed`** — *specified, not a
  gap* (DN-5): the FR preamble binds capabilities and NFR-S4 is a binding requirement, so treating it
  as a missing FR would manufacture a defect and dilute the four real hits. **The reachability half
  is a genuine hit and stays open here rather than being re-filed under a new id** — re-filing a
  five-week-old finding as new would reset its age, which is the opposite of what this ledger is for.
  - id: DF-AUD-APAA-B
  - owner: **XAgent007 (Governance Owner)** — named human, per AI-E9-8
  - target_story: **NONE — open, unowned by decision; Governance Owner to schedule** against Story
    12.1, since routing the live read path through `read_in_scope` edits `argus/pipeline.py` (1331 /
    1200, fenced)
  - status: OPEN, owned — explicitly *not* closed by Story 10.5
  - severity: 🟡 unchanged

### New filings — the three library seams that had NEVER been filed, and the V2 re-entry point

Each of the three below is **built, typed and test-proven**, and each is **unreachable from
`argus/cli.py`**. *"It has tests"* is therefore not evidence of delivery, and saying so is half the
point of Story 10.5. All three are amended in `E-PRD/prd.md` struck-not-deleted, dated and
attributed. **None is fixed here**: every call site lands in `argus/pipeline.py` (1331 / 1200) or
needs a new CLI surface, and both are fenced.

- **`DF-10-5-A` — FR24's append-only decision record has no production call site, and had never been
  filed.** `argus/governance/decision_record.py::DecisionRecordWriter` is built, typed and
  test-proven, and has **no importer at all inside `argus/`**; its only trace in the package is a
  prose mention in `store/integrity.py`. It follows FR23 by construction — a decision record has
  nothing to record until the gate it records for is invoked — so it must be scheduled **with** FR23,
  never separately. Close = wire it behind FR23's gate, or record it permanently library-only with a
  contract amendment. Tier B.
  - id: DF-10-5-A
  - origin_story: 10-5-a-v1-commitment-is-delivered-or-explicitly-not-v1
  - owner: **XAgent007 (Governance Owner)**
  - target_story: **NONE — unscheduled; Governance Owner to schedule** together with `DF-6-7-A`
    once Story 12.1 lifts the NFR-M1 gate on `pipeline.py`
  - category: capability
  - severity: 🟡

- **`DF-10-5-B` — FR26 / NFR-A2's referential-integrity lint never runs on an operator's audit, and
  had never been filed.** `argus/store/integrity.py::lint_referential_integrity` is proven by
  `tests/test_store_integrity_lint.py` and is imported only by `dogfood/proof_run.py` and
  `evidence/bundle.py` — **both themselves unreachable from `argus/cli.py`**. Consequence stated
  precisely: **no audit an operator can run today lints its own on-disk state**, so a dangling
  reference in `.argus/` would be caught in the dogfood harness and nowhere else. ⚠️ This is a
  **governance** defect, not a correctness defect — it changes no verdict, gate or finding today.
  Close = call the lint at the end of the pipeline's write phase (Story 12.1's file), or amend NFR-A2
  to say the lint is a maintainer tool. Tier B.
  - id: DF-10-5-B
  - origin_story: 10-5-a-v1-commitment-is-delivered-or-explicitly-not-v1
  - owner: **XAgent007 (Governance Owner)**
  - target_story: **NONE — unscheduled; Governance Owner to schedule** against Story 12.1
  - category: capability
  - severity: 🟡

- **`DF-10-5-C` — FR29 says an OPERATOR can export an evidence bundle, and no operator can. Never
  filed.** The sharpest of the four, because the FR text names the actor: `build_evidence_bundle` /
  `persist_evidence_bundle` (`argus/evidence/bundle.py`) are proven by `tests/test_evidence_bundle.py`,
  **no `argus` CLI subcommand exports a bundle**, and the only importer in the package is
  `dogfood/proof_run.py`. **Journey 4's hand-delivered bundle is produced by the dogfood harness, not
  by a surface Dana's engineer can invoke** — which is why this one is worth more than its severity:
  it is the gap between a journey the PRD tells and a command that exists. Close = add an
  `argus evidence-bundle` subcommand (a CLI-surface change, Story 12.8's fence), or amend FR29 to name
  the operated-service harness as the only producer. The **source-retention guarantee** in FR29 is
  unaffected and still binding.
  - id: DF-10-5-C
  - origin_story: 10-5-a-v1-commitment-is-delivered-or-explicitly-not-v1
  - owner: **XAgent007 (Governance Owner)**
  - target_story: **NONE — unscheduled; Governance Owner to schedule** against Story 12.8 (the CLI
    surface), which must not be started before 12.1 lands
  - category: capability
  - severity: 🟡

- **`DF-10-5-D` — the `standards_refs[]` V2 re-entry point, so a reclassification is not a
  disappearance.** Story 10.5 reclassified `standards_refs[]` + CWE-required-on-every-security-category
  -finding (with its `^CWE-\d+$` format validation) from **V1 to V2** at all three sites that bound it,
  and merged it into §Growth Features (V2)'s pre-existing *standards mapping (CWE/ASVS/ISO 25010/SLSA)*
  item. **This entry is the ledger's record that the commitment exists and is owed**, so it cannot
  quietly become *"it was always V2"*. Re-entry conditions, both required: (1) the ≥80%
  finding-precision gate is **CLEARED** (Epic 13) — until then no attested audience is served by the
  field; and (2) a `finding`-schema amendment is scheduled that respects NFR-A1/NFR-M2 additive-only
  and re-bounds the redaction surface (NFR-S1/S2). Consequence today, recorded at
  `E-PRD/prd.md` §Journey 4: a V1 security finding — in practice an **FR11** hardcoded-secret finding,
  the one security-category producer in V1 — carries **no standards reference**, so the evidence
  bundle is weaker compliance evidence than §Compliance & Regulatory previously implied.
  - id: DF-10-5-D
  - origin_story: 10-5-a-v1-commitment-is-delivered-or-explicitly-not-v1
  - owner: **XAgent007 (Governance Owner)**
  - target_story: **NONE — unscheduled; Governance Owner to schedule** once Epic 13 clears the
    precision gate (V2 scope by decision DN-1, not a V1.5 slip)
  - category: governance
  - severity: 🟢

### ⛔ What Story 10.5 did NOT close — asserted, not remembered

Story 10.5 is the story most likely to close an open item **by accident**, because *sweep everything
and classify it* reads like permission to tidy. The first two below are pinned **by test**
(`tests/test_v1_commitment_closure.py::-38`), so the guard defends against its own author; the rest
were verified by inspection and are recorded here so the inspection is auditable.

- **H0 — the Minions handoff H1–H4 is STILL NOT FILED.** ⚠️ **A measured correction to Story 10.5's
  own brief**, recorded rather than quietly adopted: the story was written expecting H0 to be *"OPEN
  and UNOWNED"*, and on this tree it is not — the 2026-08-10b append records H0's **ownership**
  closed via pre-authorised option (b), the operator electing to file outside this workflow. The
  **residual** is the execution, and the same entry states it: *"It does not mean H1–H4 have been
  filed"*, and *"Assumption A5 remains ⚠️ UNSUPPORTED"*. Story 10.5's forward sweep therefore disposes
  §Product Scope's *"APAA specifies the cost/memory consumption-contracts it will need from Minions
  (a)/(d)/(e)"* as **`specified-not-built`** — the specification exists (§Dependencies /
  Cross-product Boundary), the **filing does not** — and **never as `done`**. Pinning the stale
  *"UNOWNED"* would have been pinning a fact that stopped being true the day before; the guard pins
  the residual that is still true instead. **Unchanged by this story.**
- **`DF-7-2-A` — the human TP/FP adjudication is OPEN.** An owner was named on 2026-08-10b
  (XAgent007); **a named owner is not an adjudication**, `protocol_cleared` is still `False`, and only
  Epic 13 can clear it. **Unchanged by this story.**
- **The ≥80% finding-precision gate — NOT CLEARED.** Nothing in Epic 10 clears, softens or schedules
  it. Journey 4's new consequence note is explicitly written not to read as if it does.
- **`DF-10-2-A`, `DF-10-4-A`, `-C`, `-D`, `-E`, `DF-6-6-A` / `-P1` / `-P2`, `DF-8-*`, `DF-9-2-C`** —
  untouched, by inspection. `DF-10-4-D`'s dogfood-staleness trap did not fire because this story's
  write set contains **no `argus/**` file** — a **designed property**, not luck (DN-7): `git ls-files
  argus` cannot move if nothing under `argus/` is created, modified or staged.
- **`AI-E8-9` — only the F2/CWE half is disposed**, by the DN-1 decision. Its **F4 (`SC-E`), F10
  (`architecture.md`) and D1 (config drift) are STILL OPEN and are not Story 10.5's.** Naming them
  closed would be the exact over-claim this epic exists to stop.


## Story 11.1 filing — a red the story did not cause and must not close (2026-08-11)

**Filed by Story 11.1's dev run. Nothing in Story 11.1 is closed by this entry, and Story 11.1
deliberately did NOT fix it** — the fix edits `tests/test_evidence_citation.py`, which is outside
this story's declared write set, and it closes an item belonging to Epic 10's retrospective rather
than to FR34.

- **`DF-11-1-A` — the Epic-10 retrospective is an unregistered status document, and
  `TC-ArgusAgent-DOCS-001-22` is red on `master` because of it.** Story 10.1's evidence-citation
  closure resolves `epic-*-retro-*.md` **by glob** under the artifact directory precisely so a new
  document cannot escape the rule by being new. `epic-10-retro-2026-08-11.md` was then written
  (untracked, mtime 2026-08-11T20:04) and never registered in `_STATUS_DOCUMENTS`, so `-22`'s
  closed-set assertion fails. **The guard is working exactly as designed** — this is the red it
  exists to produce.
  **Attribution, measured rather than asserted:** the failing assertion reads two inputs only — the
  files matching the glob, and `_STATUS_DOCUMENTS`. Story 11.1 authored neither
  (`git status --porcelain -- tests/test_evidence_citation.py` is EMPTY, mtime 2026-08-10; the retro
  file is `??` untracked and predates this story's first write by ~75 minutes). It was red before
  this story began and is red after it, unchanged.
  Close = register the retrospective in `_STATUS_DOCUMENTS` **and** give it the §H citation it now
  owes (an `audit-ci.yml` run id plus the sha it covers, or a `NOT ESTABLISHED` marker) — the
  registration alone would only move the failure to `-20`/`-21`.
  - id: DF-11-1-A
  - origin_story: 11-1-tool-discloses-its-status-with-an-expiry
  - owner: **XAgent007 (operator — the retrospective's author)**
  - target_story: **NONE — unscheduled; operator to schedule before Epic 11 closes**, since a red
    committed guard on `master` degrades every subsequent story's ability to distinguish its own
    regressions from inherited ones
  - category: governance
  - severity: 🟡

## Deferred from: implementation of 11-2-polyglot-repository-is-classified-correctly (2026-08-11)

- **`DF-8-2-B` — CLOSED 2026-08-11 by story 11-2-polyglot-repository-is-classified-correctly**
  (append-only closure note, §3.4 — the original entry at `DF-8-2-B` above is NOT rewritten; this
  section was appended to the END of this file and `after.startswith(before)` was verified
  programmatically, +n/-0). Three things the original entry got wrong or could not have known are
  recorded here rather than edited into it:
  1. **The count was TWO and it is THREE.** Every planning document, four times over, named
     `"test.java"` and `"spec.rb"`. `_AMBIGUOUS_PYTHON_TEST_SUFFIXES` also carried a bare
     `"test.py"` with the identical defect — `contest.py`, `attest.py`, `greatest.py`, `latest.py`
     and `mytest.py` all matched it. That is the **sixth** hand-counted enumeration in this project
     to be re-measured and found wrong, which is why the close is a CLOSURE over both tables
     (`tests/test_classification_word_boundary.py::TC-ArgusAgent-DETECT-001-97`/`-98`/`-99`) and
     not the list of near-misses the original close condition asked for.
  2. **The premise "not a false green" EXPIRED.** It was written 2026-08-04, when Java had no
     grammar and both stages misclassified these files identically. Re-measured 2026-08-11:
     `build_ast_index` over `svc/latest.java` returns `ast_eligible=True`, `parse_failed=False`,
     **2 definitions** — the file is deep-*gradable*, so the agreement between the stages now costs
     real assurance coverage.
  3. **The measured consequence, which escalates the severity the entry recorded as 🟢.** Driving
     the real pipeline over a polyglot fixture at `93adc94` with the defect live:
     `svc/latest.java is_test=True depth=audited_shallow crit=CRITICAL inelig=test_file`, **critical
     set `()`**, `excluded {'svc/latest.java': 'test_file'}`. Ordinary production Java that Argus
     assesses CRITICAL was removed from the FR4 critical set under a reason that is false, emptying
     the set, so FR16's *"all critical subsystems deep"* clause was satisfied **vacuously** and
     `RELEASE_READY` was reachable on a repository whose one critical production file was never
     deep-graded — a false green in the PRD-fatal direction (inversion F1). The entry is
     append-only, so the escalation is recorded here rather than by editing the original 🟢
     (operator open question 3 of story 11.2).
  **What actually shipped:** `"test.java"` / `"spec.rb"` / bare `"test.py"` removed;
  `_CASE_SENSITIVE_TEST_SUFFIXES = ("Test.java",)` added inside tier 2 and matched against the
  ORIGINAL-CASE basename (DN-1 — Java's separator is the CamelCase capital; the original entry's
  alternative spelling `"_test.java"` would have deleted every Java true positive, because
  `_lower_basename` destroys exactly that boundary); `_AMBIGUOUS_PYTHON_TEST_BASENAMES =
  ("conftest.py",)` added inside tier 3 (DN-2 — the whole-basename rule the bare `"test.py"` was
  really standing in for, keeping `TC-ArgusAgent-DETECT-001-95` passing UNMODIFIED). Zero existing
  tests changed. The near-miss corpus is pinned in `tests/test_vacuous_detector.py`
  (`TC-ArgusAgent-DETECT-001-100`) as the original close condition asked, by IMPORT from the single
  declaration in `tests/test_classification_word_boundary.py`.

- **`DF-11-2-A` — six real test-name conventions are UNRECOGNISED, and every one of them is a false
  NEGATIVE.** Measured 2026-08-11 by cross-referencing `argus/shared/source_languages.py`'s ten
  grounded languages against both classification tables: minitest's `*_test.rb`, Maven Surefire's
  `**/*Tests.java`, `**/*TestCase.java` and `**/Test*.java` (the prefix form — `TestUserService.java`
  lowercases to `testuserservice.java`, which does NOT match tier 2's `startswith("test.")`; only
  the exact name `test.java` does), PHPUnit's `*Test.php`, and C's `*_test.c`. A genuine test file
  carrying one of these is classified PRODUCTION, so it is graded as if it were the system under
  test and the vacuous-test pass never runs over it.
  **Story 11.2 deliberately did NOT fix these.** They are a different defect class from the one it
  closed: that story only *removes* false positives, and every entry here would *add* true positives
  and therefore MOVE classification on real repositories — a widening, in an epic whose charter is
  "nothing unsafe or untrue can be published". `TC-ArgusAgent-DETECT-001-99` makes the gap
  registered rather than invisible, so this stays visible until it is decided.
  Close = add each convention to the table whose boundary rule it satisfies (`_test.rb`/`_test.c` to
  `_UNAMBIGUOUS_TEST_SUFFIXES`; `Tests.java`/`TestCase.java`/`Test.php` to
  `_CASE_SENSITIVE_TEST_SUFFIXES`; the `Test*` PREFIX form needs a new case-sensitive PREFIX
  registration, which is why it is the expensive one), remove the matching
  `_NO_CONVENTION_EXEMPTIONS` entry in `tests/test_classification_word_boundary.py`, and MEASURE the
  classification movement on a polyglot fixture rather than asserting there is none.
  - id: DF-11-2-A
  - origin_story: 11-2-polyglot-repository-is-classified-correctly
  - owner: **Delivery Orchestrator**
  - target_story: **12.5** (`a deliberately-excluded language states its absence AND reason at the
    point of downgrade` — the same disclosure surface answers both; recommendation of record from
    story 11.2's operator open question 1)
  - category: correctness
  - severity: 🟡

- **`DF-11-2-B` — `c` and `php` ground but have NO test-name convention at all, and the exemption is
  now load-bearing.** Eight of the ten languages in `LANGUAGE_BY_SUFFIX` carry at least one
  registered convention; `c` and `php` carry none, so on a C or PHP repository EVERY file — test
  suites included — is classified production. They are registered as reason-carrying exemptions in
  `tests/test_classification_word_boundary.py::_NO_CONVENTION_EXEMPTIONS` so that
  `TC-ArgusAgent-DETECT-001-99` goes RED the day an eleventh language is grounded without a decision
  being taken, or the day one of these two quietly acquires a convention.
  **This is a REGISTERED gap, not a fixed one.** The registration forces a decision; it does not
  authorise adding a convention (that is `DF-11-2-A`).
  Close = jointly with `DF-11-2-A`, or by a recorded ruling that these two languages are out of
  V1 scope, in which case the exemption reason is updated to cite that ruling.
  - id: DF-11-2-B
  - origin_story: 11-2-polyglot-repository-is-classified-correctly
  - owner: **Delivery Orchestrator**
  - target_story: **12.5** (with `DF-11-2-A`)
  - category: correctness
  - severity: 🟢

## Story 11.3 closure — 2026-08-12

- **`DF-9-2-D` — CLOSED 2026-08-12 by story
  `11-3-published-action-cannot-execute-consumer-input`** (append-only closure note — the original
  entry at *"Deferred from: code review of story 9-2…"* is **NOT rewritten**, §3.4 evidence
  immutability. That matters here more than usual: the original entry contains a **count and a
  coordinate that are both wrong**, and correcting them by editing it would destroy the record of
  what the project believed when it filed the item.)

  **(a) The real count is FIVE consumer-controlled sites, not one.** The entry describes a single
  site. Re-derived 2026-08-12 by regex over `action.yml` and cross-checked against the run-block
  resolver, every `${{ inputs.* }}` occurrence sitting inside a `run:` body was at
  **`:74` (`mkdir -p`), `:78` (the `argus audit` positional), `:79` (`--commit`), `:80`
  (`--report-dir`) and `:126` (the `strict` comparison)** — identical in the working tree and at
  `HEAD` `93adc94`. The entry's own **Close** condition did ask for the sweep (*"do the same sweep
  over every other `${{ inputs.* }}` occurrence… in one pass"*), so the defect was under-*described*
  rather than under-*scoped*.

  **(b) The entry's one coordinate, `action.yml:127`, is OFF BY ONE.** The site is **`:126`**, which
  carries `if [ "${{ inputs.strict }}" = "true" ] && [ "$EXIT_CODE" -ne 0 ]; then`. Line `:127` is
  the `echo "❌ Argus Release Gate failed with exit code $EXIT_CODE"` beneath it, which contains no
  interpolation at all. Recorded because this is the **seventh** stale coordinate this project has
  found in its own records, and the pattern — not the individual typo — is the finding.

  **(c) There was a SIXTH in-`run:` interpolation that no document named: `:68`,
  `pip install "${{ github.action_path }}"[languages]`.** It is **not** the vulnerability —
  `github.action_path` is set by the runner to the action's own checkout directory and is not
  consumer-settable — so it is not a `DF-9-2-D` instance. It was swept anyway (story DN-3): it cost
  three lines and buys a materially stronger claim on the **published** artifact, namely *zero*
  interpolations inside any `run:` body in `action.yml`, with **no exemption registered against the
  one file a consumer's job executes**. Behaviour is identical; only the moment the text is produced
  differs.

  **(d) `:135`, `with: path: ${{ inputs.report-dir }}`, is NOT a shell site and was deliberately
  NOT changed** (story DN-4). It is an **action input** to `actions/upload-artifact`, not shell
  source — the same distinction `.github/workflows/release.yml:84-87` already documents in prose for
  its `ref:`. A step-level `env:` cannot reach a later step's `with:` in any case, and routing it
  through a step output would add machinery to "fix" a non-bug. `TC-ArgusAgent-SECURITY-001-25`
  asserts that line is still present, so the non-change is pinned rather than merely explained: a
  future sweep that "tidies" it goes red.

  **(e) The exploit was DEMONSTRATED, not asserted, and the method is recorded because the method is
  the evidence.** At story-design time the `:126` template was rendered with the crafted `strict`
  value `x" = "x" ]; then echo PWNED_ARBITRARY_EXECUTION; id -un; fi; if [ "z` and the resulting
  script handed to a **real `bash`** exactly as the runner does; the injected `id -un` **executed**
  and printed the username, rc `0`. The same value through the `env:`-bound form printed `GATE_OFF`,
  rc `0`, executing nothing. **That demonstration is deliberately NOT in the test suite** — a
  `bash`-dependent guard cannot run on a Windows developer's machine, `pytest.skip` is a false green
  in this project (`audit-ci.yml` sets `ARGUS_REQUIRE_LANGUAGE_GRAMMARS=1` precisely to make a skip a
  hard failure), `PyYAML` is not a declared dependency, and a committed test that spawns a shell to
  prove code execution is itself a liability. What ships instead is the stronger, portable,
  stdlib-only property: **the `run:` script text of every step is INVARIANT under the value of every
  action input** (`TC-ArgusAgent-SECURITY-001-27`), with a mandatory positive control (`-28`) that
  applies the identical assertion to the pre-fix line held as a literal and requires it to FAIL.

  **(f) The Close condition's guard is delivered as a CLOSURE, and the obvious implementation of it
  would have been VACUOUS.** The entry asks for *"a guard test that fails on any `${{ inputs.`
  appearing inside a `run:` block"*. This repository already owned a run-block resolver
  (`tests/test_invocation_contract.py::_executable_line_numbers`) and AR7 / architecture §3.3 forbid
  a second mechanism where one exists — but that resolver keyed on `^-?\s*run:\s*[|>]?[-+]?\s*$`,
  whose `\s*$` requires end-of-line after the key, so it recognised **block scalars only**. Measured:
  against a synthetic `- run: echo "${{ inputs.evil }}"` it returned an **empty** line set, and it
  was missing four real single-line `run:` steps in `release.yml`. A guard built naively on it would
  have passed while the vulnerability stood, blind to the cheapest way to reintroduce this exact
  defect. The resolver was therefore **generalized in place and renamed public**
  (`executable_line_numbers`), not forked; the documented-invocation set it also feeds was proven
  **element-identical** across the change (5 before, 5 after, 0 added, 0 removed). The guard bans
  `inputs.*` **and** `github.event.*` outright with no exemption possible, so it protects the future
  rather than today's five sites, and detects over the JOINED run-body text so a `${{` wrapped onto
  the next line cannot escape it.

  - id: DF-9-2-D
  - closed_by_story: 11-3-published-action-cannot-execute-consumer-input
  - closed: 2026-08-12
  - verification: `tests/test_workflow_input_containment.py`
    (`TC-ArgusAgent-SECURITY-001-24`..`-31`), 8 tests. Post-fix measurement over the whole committed
    corpus: **zero** interpolations inside any `run:` body in `action.yml` (was six), and **zero**
    forbidden contexts corpus-wide (was five).
  - residual: **two registered, reason-carrying exemptions remain**, both
    `.github/workflows/argus-student-audit.yml` `${{ github.sha }}` — runner-provided 40-hex, not
    attacker-settable. One interpolates into **Python** source inside a `python -c "…"` body and is
    registered separately for that reason. `.github/workflows/release.yml` and `audit-ci.yml`
    measured **ZERO** hits: they already complied and were not touched.
  - evidence_status: **LOCAL** (Windows, CPython 3.11.15). CI evidence: **NOT ESTABLISHED** — no
    `audit-ci.yml` run has ever executed any Epic 10 or Epic 11 sha, and the artifact hardened here
    executes **only** inside GitHub Actions. The command a human runs to establish it is
    `gh workflow run audit-ci.yml --ref master` after pushing, then citing the run id **plus the sha
    it covers**. Nothing was pushed, tagged, released or dispatched by this story (`AI-E10-1`
    dated risk acceptance, carried forward; publication is Story 12.9).

  **(g) APPENDED 2026-08-12 — Story 11.3 review iteration 1. The guard delivered under (f) was
  itself VACUOUS against nine ordinary `run:` header spellings, and this is recorded because the
  pattern, not the individual miss, is the finding.** The generalised resolver classified a `run:`
  line by asking *"is anything left on the line after the key?"* and calling a non-empty remainder
  the command. That is true of a block header carrying a trailing YAML comment
  (`run: | # scrub inputs before use`) and of one carrying an indentation indicator (`run: |2` — a
  digit is not `[-+]`, so no comment is even needed), so both were misread as the single-line form:
  `run_indent` was never set and **the indented body, where the script and any `${{ inputs.* }}`
  live, was never scanned at all**. Measured on the unfixed resolver, `interpolations()` returned
  `()` against an `action.yml`-shaped document containing `echo "${{ inputs.strict }}"`, and 102 of
  the 108 spellings YAML's `c-b-block-header` grammar admits were blind. `action.yml` never used
  that shape, so the six sites closed above were and are genuinely closed — but the guard's mandate
  is the NEXT one, and a contributor appending a comment to a `run: |` would have reopened
  `DF-9-2-D` with the suite fully green.

  **The repair, and the reason it is not a fourth item on a list.** The classification now keys on
  the PRESENCE of the `|`/`>` block indicator, which YAML permits only a comment to follow — so the
  remainder is never the command, and the recognised set is the grammar rather than an enumeration.
  A single-line `run:` whose value carries an unclosed `${{` also absorbs its continuation lines,
  closing the folded-plain-scalar shape. `TC-ArgusAgent-SECURITY-001-32` asserts this over the
  GENERATED cross product (style x indentation indicator x chomping indicator x comment, both
  indicator orders, 108 spellings); `-29` gained four readable shapes. Both were demonstrated RED
  against the pre-fix resolver with the final test code and a `sha256` round-trip
  (`55b3efa15c18ea09…` -> `6025e2d0f8298015…` -> `55b3efa15c18ea09…`). The resolver change is
  provably inert on the real corpus: **zero** executable lines added or removed in any of
  `action.yml`, the three workflows or `README.md`, and `extract_documented_invocations()` still
  returns the same **5** invocations element-for-element. This supersedes the `-24`..`-31` / 8-test
  figure in `verification` below, which was correct when written: the set is now
  `TC-ArgusAgent-SECURITY-001-24`..`-32`, **9 tests**, 1371 collected suite-wide. **LOCAL**
  (Windows, CPython 3.11.15); CI evidence remains **NOT ESTABLISHED**; nothing pushed, tagged,
  released or dispatched.

## Deferred from: Story 11.4 — a wrong grammar version cannot silently produce a false green (2026-08-12)

Appended by Story 11.4. **Append-only (§3.4): nothing above this heading was edited, reordered or
deleted — verified programmatically (`after.startswith(before)`), not by eye.** Every figure below is
**LOCAL** (Windows, CPython 3.11.15); CI evidence remains **NOT ESTABLISHED** (`AI-E10-1`) — a human
establishes it by pushing and running `audit-ci.yml`, then citing the run id **plus the sha it
covers**. Nothing was pushed, tagged, released or dispatched.

- **`DF-10-4-E` — CLOSED 2026-08-12 by Story 11.4.** Its entry (above, from Story 10.4's review
  iteration 1) carried `target_story: **NONE — unscheduled; Engineering Lead to schedule** against
  whichever future story next extends `GrammarFailure`'s membership (none proposes a fifth cause
  today)`. **Story 11.4 is that story**: it registers a fifth member, `RUNTIME_UNVALIDATED`.

  **Why it could not be deferred again.** `argus/reports/generator.py::_render_grammar_remedy` ended
  in an **unconditional fallthrough**, so the fifth cause would have silently rendered the
  *core-runtime* remedy — telling an operator to `pip install tree-sitter` when the core is installed,
  importable and fine. That is precisely the "a recorded reason token names a remedy that works" rule
  Story 10.4 exists to enforce, violated **inside 10.4's own fix**, by the first story to extend it.
  Deferring would have shipped the defect it was filed to prevent.

  **The repair.** The fallthrough is now an explicit `if failure is GrammarFailure.CORE_RUNTIME_MISSING`
  arm, and the function ends in a `raise ValueError` naming the unregistered member. An unregistered
  cause is therefore **loud at the one surface an operator reads**, rather than plausible-looking prose
  for a different cause. The pure contract gained the matching import-time closure: every
  `GrammarFailure` member must own exactly one token spelling in `TOKEN_PREFIX_BY_FAILURE`
  (language-scoped) or `TOKEN_BY_UNSUFFIXED_FAILURE` (runtime-scoped), so a sixth member with neither
  fails at **import** rather than at audit time.

  **Verification.** `TC-ArgusAgent-REPORT-002-33` drives **all five** causes to the operator surface and
  asserts each renders its **own** distinct remedy (five causes → five distinct strings), plus a
  negative control proving an unregistered member **raises**; `-34` asserts the fifth cause is not
  silent at the callout and keeps its own remedy when mixed with a load cause. Cost: 19 physical lines
  in `argus/reports/generator.py`, inside the measured dogfood unit-2 budget.

  - status: **CLOSED**
  - closed_by: `11-4-wrong-grammar-version-cannot-produce-false-green`
  - closed_date: 2026-08-12
  - verification: `tests/test_grammar_runtime_validation.py::TC-ArgusAgent-REPORT-002-33`, `-34`

### Re-affirmed as OPEN and explicitly NOT absorbed by Story 11.4

Recorded so the next story inherits a measurement rather than a rediscovery. Each was re-verified
against the working tree on 2026-08-12; none is a new item and none is edited above.

- **`DF-10-2-A`** (C / C++ / Ruby / Rust parse cleanly and extract **zero definitions**) — **OPEN,
  re-measured, and deliberately ACCOMMODATED rather than fixed.** Re-confirmed by execution: the four
  grammars load, `has_error` is `False`, and `_extract` returns no definitions because their definition
  nodes are `function_item` / `method` / a `declarator` field that `_DEF_KIND_BY_NODE` and `_node_name`
  do not cover. Story 11.4's canary expectations therefore pin **today's honest truth per language**,
  including the empty tuples, and `TC-ArgusAgent-INDEX-001-123` asserts all four pass their canaries
  **by name**. A uniform "≥1 definition" canary would have fired on four **healthy** grammars and taken
  every polyglot audit to `INSUFFICIENT_COVERAGE` — a false-green fix that ships a mass false red. When
  `DF-10-2-A` is fixed those expectations must be re-measured and updated deliberately; `-123` is
  written to go **red** at that moment rather than silently absorb the change.
  - owner: unchanged · target_story: unchanged (`NONE`)

- **`DF-11-1-A`** (`tests/test_evidence_citation.py::test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed`
  fails because `epic-10-retro-2026-08-11.md` is unregistered) — **OPEN, carved out by node id for the
  FIFTH consecutive story.** Owner remains **XAgent007 (operator)**. Closing it means registering the
  retro in `_STATUS_DOCUMENTS`, which then obliges that retro to carry a run id **plus the sha it
  covers**; no such run exists (`AI-E10-1`), so closing it from a story means either editing a signed
  Epic-10 retrospective or minting a citation no story may create. **Now a standing carve-out rather
  than an exception, and it should be adjudicated at the Epic 11 checkpoint.**
  - owner: unchanged · target_story: unchanged

- **`DF-11-2-A`** / **`DF-11-2-B`** (six unrecognised real test-name conventions; `c`/`php` grounded
  with no convention) — **OPEN, untouched.** Both are file-classification defects in
  `argus/detectors/vacuous_test.py`, both carry `target_story: 12.5`, and both *widen* classification
  and *move* verdicts on real repositories — the opposite shape to a story that withholds a verdict.
  Story 11.3 ruled identically.
  - owner: unchanged · target_story: unchanged (12.5)

### New this story

- id: DF-11-4-A
  - title: **The runtime toolchain check does not reach the operator on a PARTIAL failure**
  - detail: `_render_readability_warning`'s all-or-nothing trigger (`if eligible: return []`) means the
    new `tree_sitter_runtime_unvalidated` cause is announced **only when nothing at all parsed**. On a
    polyglot repository whose Python validates and whose Rust does not, the Rust files are recorded
    `ast_eligible=False` with the correct token, the coverage numbers move honestly, and **no callout
    names the cause**. This is not a new blind spot — it is the **same** trigger already filed as
    `DF-10-4-A` — but it now has a fifth, more consequential cause behind it, because the other four
    mean "a grammar is visibly absent" while this one means "a grammar is present and lying".
  - measured: 2026-08-12, by reading the live trigger and by `TC-ArgusAgent-REPORT-002-29`, which pins
    the narrow trigger in **both** directions and is deliberately left unrelaxed by this story.
  - why_not_fixed_here: widening the trigger adds a per-file point-of-downgrade operator surface that
    **Story 12.5 owns by name** (`epics.md` Epic 12). Taking it here would be scope leak into another
    story's ground, and Story 10.4 already refused the same widening for the same reason.
  - owner: **Engineering Lead**
  - target_story: **12.5** — fold into `DF-10-4-A`'s remedy; the two share one trigger and one fix.
  - category: developer-experience
  - severity: 🟡 (upgraded from `DF-10-4-A`'s 🟢: silence about an *absent* grammar is a slower path to
    the right answer, silence about a *drifted* one leaves a wrong 🟢 unexplained)

- id: DF-11-4-B
  - title: **The `tree-sitter <0.26` pin's stated reason is disproved; the pin itself is unre-validated**
  - detail: Story 11.4 measured that 0.26.0's breaking changes touch nothing Argus uses and that the
    stated cartridge flip is not reproducible (`architecture.md` §Packaging, corrected in place). The
    pin was **retained** as conservative-by-default (DN-7) and its prose corrected, but nobody has run
    the suite against a real 0.26 install. The bound is now duplicated-by-design in exactly two places
    — `pyproject.toml`'s specifier and `argus/shared/grammar_status.py`'s integer tuples — held equal
    in both directions by `TC-ArgusAgent-DOCS-001-54`, so this is a *decision* to take, not a drift to
    fix.
  - why_not_fixed_here: dependency **bounds** are a packaging decision with a named owner (NFR-P3;
    `architecture.md` records it as *"a decision, not decided here"*), and §0.1.4 forbids this story
    from changing the venv to observe a change. Re-validating requires a throwaway environment, which
    is an operator action.
  - owner: **XAgent007 (operator)** for the decision; **12.5** for the packaging change if taken
  - target_story: **12.5**
  - category: packaging
  - severity: 🟢 (the runtime defence this story added is what now carries the guarantee; the pin is no
    longer the only line of defence, which is precisely why widening it is now a *choice*)

## Deferred from: code review of story 11-4-wrong-grammar-version-cannot-produce-false-green (2026-08-12)

Appended by the `bmad-code-review` gate, iteration 1 (verdict: PASS). **Append-only (§3.4): nothing
above this heading was edited, reordered or deleted.**

- **Canary is a finite-sample check, not a universal grammar verifier**
  (`argus/shared/grammar_status.py::GrammarCanary`). `canary_matches` proves the toolchain behaves as
  validated on ONE pinned snippet per `(language, entry point)` seam; it cannot prove correctness for
  every input the toolchain will ever see. This is inherent to any canary/sample-based check, not a
  defect in this story's design, and is already disclosed in `DEV-1`'s own docstring (sensitivity to a
  deliberate change of `_DEF_KIND_BY_NODE` / `_CALL_NODE_TYPES` is named as intended). Not actionable.
  - id: DF-11-4-C
  - origin_story: 11-4-wrong-grammar-version-cannot-produce-false-green (code review, iteration 1)
  - owner: Engineering Lead
  - target_story: NONE — accepted design property, revisit only if a real drift is found that a canary
    cannot see
  - category: testability
  - severity: 🟢

- **`tests/test_release_surface_honesty.py`'s note-section registry has been edited by three
  consecutive stories** (11.1, 11.2/11.3, 11.4). Each edit examined by this review is a clean, justified
  insertion — Story 11.4's is a pure addition with zero lines removed or reordered, placed second on the
  registry's own stated ordering principle, and it did not demote Story 11.1's instrument disclosure.
  Flagged as a pattern, not a defect: a registry that is routinely widened to fit whatever the current
  story needs to say is a registry that is one unexamined edit away from becoming decorative. Recommend
  the operator review this file's edit history at the Epic 11 checkpoint.
  - id: DF-11-4-D
  - origin_story: 11-4-wrong-grammar-version-cannot-produce-false-green (code review, iteration 1)
  - owner: XAgent007 (operator)
  - target_story: NONE — epic checkpoint review item
  - category: process
  - severity: 🟡

## Deferred from: story 11-5-published-artifact-is-complete-and-true (2026-08-12)

Appended by `dev-story`. **Append-only (§3.4): nothing above this heading was edited, reordered or
deleted** — verified programmatically (`git diff --numstat` on this file shows `-0` deletions).

Every figure below is **LOCAL, Windows / CPython 3.11.15**, under the dated risk acceptance recorded
in Story 11.1 §0.1 (AI-E10-1, 2026-08-11, XAgent007), carried forward rather than re-taken.
**CI evidence: NOT ESTABLISHED.** Nothing was published: `git tag -l` is empty, `origin/master` did
not move, no release and no index upload. The wheel and sdist were built into a temporary directory
outside the repository.

### Closed by this story

- **`DF-9-2-A` — CLOSED 2026-08-12.** `argus/precision/replay_harness.py` now resolves the 6.5
  cartridge registry through a lazy `_registry_module()` helper instead of a module-level
  `sys.path.insert` + `from _registry import …`; `compute_precision` takes `registry=None` and
  `precision_gate_status_for` takes a keyword-only `floor_n=None`, so
  `argus/dogfood/proof_run.py:642` is **byte-unchanged**. **Measured on a freshly built wheel**
  (`python -m build --no-isolation`, `argus_agent-0.1.0-py3-none-any.whl`, 77 entries = 72
  `argus/**` modules + 5 `dist-info`; sdist `argus_agent-0.1.0.tar.gz`, 76 members, no `tests/`),
  one clean subprocess per module, this repository removed from `sys.path` by normalised absolute
  path, `cwd` outside the repository, and `argus.__file__` asserted to resolve inside the extraction
  directory before any result was trusted: **72 of 72 import, 0 fail** — against a baseline
  re-measured the same way on the same tree of **67 of 72, 5 fail**
  (`ModuleNotFoundError: No module named '_registry'`: `argus/precision/__init__.py`,
  `argus/precision/replay_harness.py`, `argus/dogfood/proof_types.py`,
  `argus/dogfood/proof_render.py`, `argus/dogfood/proof_run.py`).
  ⚠️ **The stated close condition was FALSE and is corrected here rather than quietly satisfied.**
  It read *"update `_NOT_IMPORTABLE_FROM_DISTRIBUTION` … which is pinned in BOTH directions, so a fix
  that leaves the record stale goes RED."* `TC-ArgusAgent-RELEASE-001-11` pinned that constant by
  walking the **source tree** with `ast`, and an `import _registry` inside a function body is the
  same AST node as one at module level — so `-11` **stayed GREEN across the entire fix**, and would
  have stayed green had the record been left stale. It also could not see the published figures
  rotting from *"66 of the 71"* to a measured 67 of 72 across Epics 10–11, because it pins a set of
  paths and the documents publish numbers. A guard that inspects the source tree is vacuous by
  construction for a claim about the distribution. `-11` is **narrowed, not deleted** (it still
  honestly names which modules mention the repository-only test tree, and its docstring now says what
  it can and cannot see); the distribution claim moved to `TC-ArgusAgent-RELEASE-001-20`
  (`tests/test_built_distribution.py`), which builds a real wheel and sdist and imports every shipped
  module out of the built artifact, with `-21` as the provenance control, `-23` as the
  fails-when-the-artifact-is-wrong control and `-24` as the never-passes-silently control.
  - id: DF-9-2-A
  - closed_by: 11-5-published-artifact-is-complete-and-true
  - closed_on: 2026-08-12
  - status: CLOSED

- **`DF-9-2-B` — PARTIALLY CLOSED 2026-08-12.** The bounded prose pass its close condition asked for
  was performed: **all 21** bare-word `Minions` occurrences under `argus/**` were re-derived by
  executing the regex `(?<![A-Za-z_])Minions(?![A-Za-z_])` over `git ls-files -- argus` (the ledger's
  own figure of *25 total / 23 outside `dogfood/`* was stale, as was the epic's *22 across 14*), read
  one by one, and classified. **19 are TRUE HISTORICAL and were kept** — each records where a design,
  a constant or a containment rule came FROM (AR7 reuse provenance, negative dependency claims,
  superseded-run citations); deleting them would make the modules less true, not more. **2 were FALSE
  SUBJECT claims and were rewritten**: `argus/verdict/negative_assurance.py`'s two FR34 instrument
  disclosures said the findings rest on *"the Minions dogfood corpus"* and then described that corpus
  four words later as *"a self-audit of this repository"*. Those two sentences are the
  highest-visibility text Argus has — `argus audit .` prints one of them on `stderr` on every run —
  and they are single-sourced, so the copies at `README.md:10` and `CHANGELOG.md:52` were updated in
  the same change and `tests/test_instrument_disclosure.py` passes without weakening. The subject was
  corrected; the claim, the negation, the two-member `InstrumentStatus` vocabulary and the removal
  condition (Epic 13's human adjudication) are unchanged. The classification is now a **closure**, not
  a list: `TC-ArgusAgent-DOCS-001-57` re-derives the occurrence set from the tree and goes RED on any
  unclassified member, in both directions.
  **What is NOT closed:** this covers `argus/**` only, which is what `DF-9-2-B` scoped. Bare-word
  occurrences elsewhere in the repository (planning artifacts, `tests/**`, the preserved Story-7.2
  record) are untouched and were never in its scope.
  - id: DF-9-2-B
  - closed_by: 11-5-published-artifact-is-complete-and-true
  - closed_on: 2026-08-12
  - status: PARTIALLY CLOSED — `argus/**` closed; the rest of the repository was never in scope

### Restated as OPEN, so it does not vanish when Epic 11 closes

- **`AI-E10-4` / `DF-10-2-A` remain OPEN and still have no home.** `AI-E10-4` offered *"(11.5), or a
  dated V2 decision"* as `DF-10-2-A`'s home (C/C++/Ruby/Rust ground with `ast_eligible=True` but
  extract zero function/class definitions). **Story 11.5 rules it OUT with reasons** (DN-7): it is a
  *detector-coverage* change that moves classification on real repositories, this story is packaging
  and documentation correctness, and the unit-2 LOC budget had 3 lines left after the DF-9-2-A fix —
  nowhere near enough to widen extraction safely. **Epic 11 closes after this story with both still
  open.** A dated decision is needed.
  - id: DF-10-2-A
  - owner: **XAgent007 (operator)** for the dated decision; Engineering for the change if taken
  - target_story: **NONE** — needs a named owner or a dated V2 deferral
  - category: detector-coverage
  - severity: 🟡 (unchanged)

- **`DF-11-4-D` reached its FIFTH consecutive `_NOTE_SECTIONS` edit here** (11.1, 11.2, 11.3, 11.4,
  11.5). Story 11.5's edit is a pure zero-deletion insertion registered fifth, with its ordering
  reason stated and a promotion above 11.3's security entry explicitly considered and declined; no
  existing section moved and none was demoted. Recorded rather than left to be counted, as
  `DF-11-4-D` asks. **The Epic-11 checkpoint review should read this file's edit history**: the
  pattern the reviewer flagged after three consecutive edits has now run to five.
  - id: DF-11-4-D
  - owner: XAgent007 (operator)
  - target_story: NONE — epic checkpoint review item
  - category: process
  - severity: 🟡 (unchanged)

- **`DF-9-2-C` deliberately NOT closed.** The three tracked `argus/dogfood/__pycache__/*.pyc` files
  are adjacent and tempting, and `git rm --cached` would fix them in one line — but that changes the
  git **index**, which is exactly the `DF-10-4-D` trigger this story is fenced by (`git ls-files --
  argus` must read 72 before and after staging). Left for whoever owns Story 12.1.
  - id: DF-9-2-C
  - owner: Engineering
  - target_story: **12.1**
  - category: repository-hygiene
  - severity: 🟢 (unchanged)

### Opened by this story

- **DF-11-5-A** — 🟡 **The unit-2 dogfood LOC budget is down to 3 lines.** Measured after this
  story's `git add`: unit `82a3d605e61e` = **14997 / 15000**, all three partition_ids byte-unchanged
  (`477ef77d7b65` 1330 / `82a3d605e61e` 14997 / `ed6d08f25ce3` 4116). The cliff was measured to the
  line by Story 11.5's SM: `+13` keeps all three ids, `+14` splits unit 2 and moves two of them,
  turning the committed-artifact staleness test RED. This story consumed **10 of the 13** available.
  **The next story that writes more than 3 physical lines into any unit-2 module cannot proceed
  without regenerating the dogfood artifacts**, which is Story 12.1's remedy and which 10.4 and 11.5
  both refused to take on their own authority. This is not a defect in any story; it is a budget that
  has nearly run out and now needs an owner.
  - id: DF-11-5-A
  - origin_story: 11-5-published-artifact-is-complete-and-true
  - owner: **Engineering Lead**
  - target_story: **12.1** — regenerate the dogfood plan/budget/proof artifacts at a truthful sha
  - category: process
  - severity: 🟡

- **DF-11-5-B** — 🟢 **The built-artifact guard costs ~5 seconds of wall clock per suite run.**
  `tests/test_built_distribution.py` invokes `python -m build --no-isolation` once per session
  (~2.2 s) and then spawns one subprocess per shipped module (72 of them, ~2.5 s across 8 worker
  threads). It is the only test in this suite that shells out to a build backend. It is cheap enough
  today and deliberately NOT marked `slow` — a guard behind an opt-in marker is a guard nobody runs —
  but the cost scales with the module count and should be revisited if the suite gains a fast/slow
  split.
  - id: DF-11-5-B
  - origin_story: 11-5-published-artifact-is-complete-and-true
  - owner: Engineering
  - target_story: NONE — revisit if a fast/slow split is introduced
  - category: testability
  - severity: 🟢

- **DF-11-5-C** — 🟢 **`README.md`'s seven `/audit …` commands are documented but undelivered.**
  Marked FORTHCOMING against Story 12.7 / FR35 rather than deleted, because the shape is the contract
  12.7 delivers against. `TC-ArgusAgent-DOCS-001-56` holds it in both directions: it fails if the
  marker is removed while the wheel still ships no command asset, **and** it fails if the marker
  survives once the wheel ships one. Filed so that 12.7 knows the marker is its to remove.
  - id: DF-11-5-C
  - origin_story: 11-5-published-artifact-is-complete-and-true
  - owner: Engineering
  - target_story: **12.7**
  - category: documentation-accuracy
  - severity: 🟢

## Deferred from: story 12-1-pipeline-stops-breaching-its-own-limit (2026-08-12)

**Append-only (§3.4): nothing above this heading was edited, reordered or deleted.** Every figure
below is **LOCAL, Windows / CPython 3.11.15**, re-derived by execution on this tree on 2026-08-12
under the dated risk acceptance of 2026-08-11 (carried forward, not re-taken). **CI evidence: NOT
ESTABLISHED.**

### Closed by this story

- **`DF-8-2-A` — CLOSED 2026-08-12.** `argus/pipeline.py` was **1331** lines against the NFR-M1
  cap of 1200 — 131 over, drifted from the 1199 this entry recorded at Story 8.2 and warned about
  in exactly these words: *"the next edit of any size breaches NFR-M1"*. It is now **944**, with
  256 lines of headroom for the three Epic-12 stories that must land in it. The audit fold's
  DERIVATION stages (`_is_python` … `_assessment_scope_paths`, sixteen functions) were extracted
  verbatim into the new sibling `argus/pipeline_stages.py`, following Story 6.3's
  `DN-PIPELINE-SPLIT` precedent. Proven a pure restructuring rather than asserted to be one: the
  sixteen moved definitions and the thirteen that stayed are **byte-identical** to their pre-12.1
  form (compared by `ast` span and sha256), and the pre- and post-change code produce
  **byte-identical** reports (4 files) and `.argus/` output (848 files) over an identical tree.
  **⚠️ RECORD FOR THE NEXT READER — this entry's OWN named remedy was measured INSUFFICIENT.** It
  prescribed *"extract a shell-helper module (e.g. `argus/pipeline_facts.py` carrying
  `_critical_ineligibility` and its siblings)"*. Re-measured 2026-08-12: that family is **~59
  lines** against the **>=131** required, and would have left `pipeline.py` at ~1272 — **still over
  the cap**. The prescription was correct when the file was 1199 and needed to shed one line; it
  stopped being correct as the file drifted. A remedy written against a measurement expires with
  that measurement.
  **The boundary that was taken, and why it beat the story's own recommendation.** Story 12.1
  recommended the 357-line Story-3.4 resume family (`argus/pipeline_resume.py`) and explicitly
  permitted a better measured boundary. The dependency direction was measured by an `ast` walk over
  the pre-split file and decided it: the resume family references **eleven** names that would stay
  behind (`_assemble_and_persist`, `_detect_per_file`, `_project_halt`, `_critical_candidates`,
  `AuditResult`, `ResumeStateError` …) while `pipeline.py` must keep re-exporting `resume_audit`
  from `__all__` — a module-level import **cycle** survivable only by a bottom-of-file or
  function-local import trick. The derivation stages reference **three** names that stay behind,
  all constants, which moved with them — so the dependency points strictly downward, there is no
  cycle, every moved body is byte-identical (no call site had to be rewritten to reach back into
  the parent module), and it sheds **403** lines rather than 357. A restructuring story whose
  defining criterion is *behaviour proven untouched* must not ship a fragile import graph to save a
  line count.
  - id: DF-8-2-A
  - closed_by: 12-1-pipeline-stops-breaching-its-own-limit
  - closed_on: 2026-08-12
  - status: CLOSED — `argus/pipeline.py` 1331 → 944; enforced repo-wide by
    `tests/test_module_size_ceiling.py` (`TC-ArgusAgent-MAINT-001-01`..`-05`)

- **`DF-8-3-C` — CLOSED 2026-08-12.** The duplicated ast-index → application/test plumbing is gone.
  One helper, `partition_application_files(entries, ast_index) -> (application, held_out)`, now
  lives beside `is_test_file` in `argus/detectors/vacuous_test.py` — the home this entry named, an
  **existing** file, so it cost no new module — and **both** sites call it:
  `pipeline_stages._assessment_scope_paths` (which narrows the assessed population the verdict gate
  folds over) and `reports.generator._render_test_dilution_hint` (which derives the report's
  APPLICATION denominator). The two derivations whose agreement the verdict depended on are now
  literally the same code. It is typed structurally (a `_HasFilePath` Protocol + a `TypeVar`) so
  this leaf detector module gains **no new import edge** — the import-isolation gate keeps
  `argus.detectors.*` a leaf, and each caller gets its own element type back.
  **⚠️ Its recorded coordinates were STALE, as Story 12.1's create-story pass measured.** The entry
  named `pipeline.py:686-694` and `generator.py:86-93`; the sites were found at
  `argus/pipeline.py:745` and `argus/reports/generator.py:176` — and by the time the change landed
  the first had moved again, into `argus/pipeline_stages.py`, by this story's own extraction. Found
  by **anchor text**, never by line number. That is the fourth stale-coordinate finding in this
  ledger in three days.
  - id: DF-8-3-C
  - closed_by: 12-1-pipeline-stops-breaching-its-own-limit
  - closed_on: 2026-08-12
  - status: CLOSED — one derivation, two call sites, no behaviour change (the 848-file `.argus/`
    and 4-file report A/B is byte-identical across the change)

- **`DF-8-5-B` + `DF-10-4-D` — CLOSED TOGETHER 2026-08-12**, per `DF-10-4-D`'s own instruction
  (*"supersede or close them together, never separately"*). Closed by
  `tests/test_dogfood_artifact_currency.py` (`TC-ArgusAgent-DOGFOOD-001-49`..`-52`) plus the
  regeneration-command sentence now carried by every one of the five committed-artifact
  assertions' failure messages.
  **The remedy both entries named was necessary and NOT sufficient, and the reason is a finding
  neither entry measured.** Both describe the class as *guards that break too often*. Measured on
  this tree at `ca37283`, the opposite failure was **also live and worse**: all three committed
  dogfood artifacts were **already stale** — provenance `a9cc933` vs `HEAD` `ca37283`, total
  physical LOC 19783 vs 20454, recorded cut edges 57 vs 64, unit-2 LOC 14793 vs 14997, unit-3 3660
  vs 4127, the NFR-C1 baseline ratio `360/19783` vs `60/3409` — **while all five `DF-10-4-D`
  assertions were GREEN**. They were green because of what they actually assert, which is far less
  than their own docstrings claim: `-03` says *"the artifact cannot silently rot away from the
  generator"* and checks the literal `Unit count: 3`, three 12-character `partition_id` prefixes and
  the phrase `Reused planner` — it cannot see a single figure in that list. So *"name a regeneration
  entry point in the failure message"* improved a red that today never appeared. **This is the
  fifth-plus instance of this project's dominant defect class** (Epic-11 retrospective, `AI-E11-1`):
  a guard structurally incapable of seeing the thing it names.
  **What was built instead — a closure over the real structure, not over a list of tokens.** An
  artifact is CURRENT iff (a) the provenance sha it cites is a real commit **and an ancestor of
  `HEAD`**, and (b) `git diff --quiet <cited-sha> HEAD -- argus/` is empty. It was **RED at
  `ca37283` for free**, on the real defect, with no reconstruction (`git diff a9cc933 HEAD --
  argus/` = 7 files, +749/−78), and it would have been **GREEN at the last honest regeneration**
  (`git diff a9cc933 93adc94 -- argus/` is empty and `a9cc933` is an ancestor of `HEAD`) — so it
  distinguishes the honest state from the rotten one rather than failing always. **No assertion was
  loosened or deleted**; `-03` was widened, which `DF-8-5-B` explicitly welcomes.
  **The provenance/enumeration reconciliation `DF-10-4-D` asked for, decided and recorded.** The
  artifacts claimed *"Commit descriptor (HEAD at generation)"* while
  `enumerate_minions_source_files` reads `git ls-files` — the **INDEX** — *"and those are two
  different trees."* **Decision: the label now tells the truth about what was enumerated**, rather
  than pinning the enumeration to the commit. Reason: pinning would have changed what the dogfood
  planner enumerates, which is a verdict-adjacent behaviour change inside the one story whose
  defining criterion is *behaviour proven untouched*, and it would have broken the staged fixture
  repositories `tests/test_dogfood_*.py` build. The two trees are now reconciled **mechanically**
  as well as in prose: the currency guard fails unless `argus/**` at the cited sha equals `argus/**`
  at `HEAD`, which is exactly the condition under which the index-enumerated population and the
  `HEAD`-cited provenance describe the same `argus/` tree.
  - id: DF-8-5-B
  - closed_by: 12-1-pipeline-stops-breaching-its-own-limit
  - closed_on: 2026-08-12
  - status: CLOSED — jointly with `DF-10-4-D`
  - id: DF-10-4-D
  - closed_by: 12-1-pipeline-stops-breaching-its-own-limit
  - closed_on: 2026-08-12
  - status: CLOSED — jointly with `DF-8-5-B`; the bootstrap ordering hazard it named was executed
    in the order it prescribed (implement → commit → regenerate through the renderers → re-run)

- **`DF-11-1-A` — CLOSED 2026-08-12.** `epic-10-retro-2026-08-11.md` and
  `epic-11-retro-2026-08-12.md` are registered in `_STATUS_DOCUMENTS`
  (`tests/test_evidence_citation.py`), ending a carve-out that five consecutive stories had passed
  down by node id. `TC-ArgusAgent-DOCS-001-22` is green and the suite is clean of it: **1405
  collected / 1405 passed / 0 failed** immediately after the two-line registration, against the
  1405/1404/1 baseline this story started from. **Registration is inert against every other
  assertion in that file, verified by execution**: `_status_assertions()` returns **0** status
  assertions for each retrospective, so `-21`'s per-document loop short-circuits. **No
  retrospective was edited and no citation was minted** — the entry's close condition also asked for
  a §H citation, and that half is *not* taken here: minting a citation for a document this dev did
  not author, on a tree no CI run has seen, would manufacture exactly the false-citation class Epic
  10 exists to close. The registration alone is sufficient because both documents make **zero**
  status claims; the day either one makes a claim, `-20`/`-21` will demand the citation from its
  author, which is the correct owner.
  - id: DF-11-1-A
  - closed_by: 12-1-pipeline-stops-breaching-its-own-limit
  - closed_on: 2026-08-12
  - status: CLOSED — registered; the §H-citation half is deliberately NOT taken (both documents make
    zero status claims, so it is not owed; `-20`/`-21` will demand it the day one is made)

- **`DF-11-5-A` — CLOSED 2026-08-12.** *"The unit-2 dogfood LOC budget is down to 3 lines … the next
  story that writes more than 3 physical lines into any unit-2 module cannot proceed without
  regenerating the dogfood artifacts."* That is this story, and it regenerated them — through
  `render_partition_plan_markdown`, `render_budget_plan_markdown` and `render_proof_markdown`, at a
  provenance sha that genuinely contains the delta, under the operator ruling of 2026-08-12 that
  pre-authorises the sequence for all of Epic 12. Not one character of any artifact was hand-edited.
  The budget did exactly what this entry predicted: the extraction re-split the oversized cohesion
  component and moved partition ids, `TC-ArgusAgent-DOGFOOD-001-03` went red by construction, and
  the remedy was regeneration rather than a loosened assertion.
  - id: DF-11-5-A
  - closed_by: 12-1-pipeline-stops-breaching-its-own-limit
  - closed_on: 2026-08-12
  - status: CLOSED

- **`DF-9-2-C` — ALREADY RESOLVED; verified, not assumed.** The entry says three
  `argus/dogfood/__pycache__/*.pyc` files are tracked and names Story 12.1 as its target. Measured
  on this tree 2026-08-12: `git ls-files -- argus | grep -c pycache` returns **0**, and
  `git ls-files -- argus` contains **no non-`.py` path at all**. They were untracked at or before
  `ca37283`. **Nothing was done here** — recording a verified absence rather than performing a
  `git rm --cached` that would have moved the git index, which is the `DF-10-4-D` trigger, inside
  the one story that must prove its own audit population unchanged.
  - id: DF-9-2-C
  - closed_by: 12-1-pipeline-stops-breaching-its-own-limit
  - closed_on: 2026-08-12
  - status: CLOSED — already true on arrival; verified by measurement, no change made

### Re-recorded with a new reason and a live target

- **`DF-8-3-A` — RE-RECORDED, target `12-4-every-outcome-names-its-next-action`.** Its recorded
  blocker is **DISCHARGED**: it deferred *"AFTER the DF-8-2-A shell-helper extraction has made room
  in `pipeline.py`"*, and the room now exists — `argus/pipeline.py` is 944 lines with 256 of
  headroom. **What remains is not a room ruling but a SCOPE ruling, and it is a different reason
  from the old one.** Threading `CriticalSubsystemSet.heuristic_excluded_ineligible` into
  `generate_reports` / `render_final_verdict_report` and naming the vacuity in prose is a
  **report-content change**. Story 12.1's AC5 forbids that by construction — its evidence is that
  the four report artifacts and the 848-file `.argus/` output are **byte-identical** across the
  change, and a new disclosure sentence would have destroyed exactly that proof. Its natural home is
  Story 12.4, whose entire subject (FR37) is what a terminal outcome says and why, including the
  `INSUFFICIENT_COVERAGE` and critical-subsystem explanations this disclosure belongs beside.
  - id: DF-8-3-A
  - owner: Engineering
  - target_story: **12-4-every-outcome-names-its-next-action**
  - category: correctness
  - severity: 🟢 (unchanged)
  - blocker_status: the `pipeline.py` room blocker is **DISCHARGED** by 12.1; the remaining reason is
    scope, not room

### Ruled OUT of this story, with reasons, rather than quietly not mentioned

- **`DF-10-2-A` — stays OPEN and UNOWNED. Ruled out of Story 12.1 deliberately.** It is 🟡, has been
  unowned for two epics, and has been named critical-path twice (`AI-E10-4`, `AI-E11-7`). It is about
  C/C++/Ruby/Rust grounding with zero definition extraction — **no relationship to `pipeline.py`,
  to NFR-M1, or to the dogfood artifacts**. `AI-E11-7` asks for a **dated operator decision**
  (*"a fix is probably not needed … what is needed is a dated decision"*), which is a type-(H) item
  and outside a dev agent's authority to take. Folding an unrelated governance decision into a
  restructuring story would be scope creep in the one story that must prove nothing changed. **Said
  out loud here rather than passed over in silence — that is the whole point of this paragraph.**
  - id: DF-10-2-A
  - owner: **XAgent007 (operator)** for the dated decision — UNCHANGED, still unassigned in practice
  - target_story: **NONE** — third consecutive story to carry it forward without a home
  - severity: 🟡 (unchanged)

- **`DF-11-4-D` / `AI-E11-6` (the `_NOTE_SECTIONS` impact rank) — RE-TARGETED to Story 12.4**, not
  folded into 12.1 as the Epic-11 retrospective suggested. Three measured reasons: (1) **the trigger
  does not fire here** — `DF-11-4-D`'s rule of thumb is *the next story that edits the file*, and
  Story 12.1 **adds no release-note section** (it changes no user-visible surface, which AC5
  forbids), so folding the rework in would mean opening a registry this story otherwise has no
  reason to touch, which is precisely the *"routinely widened to fit whatever the current story
  needs"* pattern the entry was filed about; (2) **single-purpose** — 12.1's write set is already an
  extraction, a repo-wide sweep, a currency guard, an architecture registration, nine ledger rulings
  and a two-commit regeneration sequence, and the Epic-11 retrospective's own §3.1 finding is that
  this project's defects come from guards written under load; (3) **12.4 owns the vocabulary** —
  `AI-E11-6`'s proposed rank (`changes_exit_code` > `changes_verdict` >
  `security_on_executable_surface` > `changes_no_observable`) is an **outcome-impact** vocabulary,
  and 12.4 must enumerate exactly those outcomes to satisfy FR37 and is the first Epic-12 story that
  certainly does add a note section. **`AI-E11-6`'s alternative DoD is explicitly NOT taken:** this
  is a re-targeting, not a dated acceptance that the narrative convention is fine.
  - id: DF-11-4-D
  - owner: Engineering
  - target_story: **12-4-every-outcome-names-its-next-action**
  - category: process
  - severity: 🟡 (unchanged)

### Opened by this story

- **DF-12-1-A** — 🟢 **`tests/test_pipeline_signature_demo.py` is 1326 lines, 126 over the NFR-M1
  ceiling.** Registered as a NAMED, DATED exemption in
  `tests/test_module_size_ceiling.py::_EXEMPT_BY_DESIGN`, never as silence and never by narrowing
  the swept population — the sweep covers **all 169 tracked `.py` files** and is red on this one
  without the entry (demonstrated: with the registry emptied, the sweep names all four breaching
  files). **Not fixed here:** this file demonstrates the FR32 pipeline signature end to end over
  real git fixtures; splitting it is a substantial refactor of a load-bearing guard file inside a
  story whose defining criterion is that behaviour is PROVEN untouched, and a restructuring story
  must not also refactor the guard that would notice if it broke something. The exemption registry
  **shrinks**: `TC-ArgusAgent-MAINT-001-04` fails if this entry names a file that no longer exists
  **or that is no longer over the cap**, so it cannot become dead weight.
  - id: DF-12-1-A
  - origin_story: 12-1-pipeline-stops-breaching-its-own-limit
  - owner: Engineering
  - target_story: **12-2-deep-audit-is-wired-opt-in-and-honest** — the next story to edit the
    pipeline surface this file demonstrates
  - category: maintainability
  - severity: 🟢

- **DF-12-1-B** — 🟢 **`tests/test_v1_commitment_closure.py` is 1308 lines, 108 over the NFR-M1
  ceiling.** Same registry, same reason. This is Story 10.5's delivery-closure guard: two static
  closures that meet in the middle over `E-PRD/prd.md` and the `argus/**` import graph. Its own
  architecture registration predicts that **Story 12.3** will edit it (wiring the memo-store seam
  flips a `library-seam` disposition and turns it red until the disposition is updated), which makes
  12.3 the honest target rather than an invented one.
  - id: DF-12-1-B
  - origin_story: 12-1-pipeline-stops-breaching-its-own-limit
  - owner: Engineering
  - target_story: **12-3-a-re-run-returns-the-recorded-result**
  - category: maintainability
  - severity: 🟢

- **DF-12-1-C** — 🟢 **`tests/test_grammar_diagnosis.py` is 1203 lines — three lines over the NFR-M1
  ceiling.** Same registry, same reason. Story 10.4's grammar-diagnosis guard, including the `ast`
  closure over the loader's own control flow. **Three lines** is the cheapest of the three to close
  and the most likely to be closed by accident by any story that touches it, which is why it carries
  a live target rather than `NONE`: Story 12.5 owns the grammar / NFR-P3 surface this file guards.
  - id: DF-12-1-C
  - origin_story: 12-1-pipeline-stops-breaching-its-own-limit
  - owner: Engineering
  - target_story: **12-5-default-install-grounds-languages-it-claims**
  - category: maintainability
  - severity: 🟢

- **DF-12-1-D** — 🟡 **The NFR-M1 sweep reads the git INDEX, so an unstaged module escapes it.**
  `tests/test_module_size_ceiling.py` enumerates `git ls-files -- '*.py'` deliberately: a module is
  swept the moment it is `git add`-ed, which is when a developer wants to know. The cost is the
  mirror image — a module that is written and **never staged** is not swept at all, so a dev agent
  could finish a story with an over-cap module the guard never saw. This is the same
  index-versus-worktree seam `DF-10-4-D` measured in `argus/dogfood/`, read in the other direction.
  It bit during this story's own implementation: `TC-ArgusAgent-PIPELINE-002-11`'s widened reach was
  first written against `git ls-files -- 'argus/pipeline*.py'` and went **red for the wrong reason**
  because the new module was untracked; it was moved to a filesystem glob for that guard. The sweep
  itself keeps the index population on purpose — a filesystem walk would drag in `.venv/`,
  `__pycache__` and untracked scratch, which the standard does not govern — so the honest fix is
  probably a second, cheap assertion over untracked-but-present `argus/**` and `tests/**` sources,
  not a change of population. **Filed rather than fixed**: adding a second population to the guard
  this story ships, in the same story, is how a guard gets written under load.
  - id: DF-12-1-D
  - origin_story: 12-1-pipeline-stops-breaching-its-own-limit
  - owner: Engineering
  - target_story: NONE — the next story that edits `tests/test_module_size_ceiling.py`
  - category: testability
  - severity: 🟡

- **DF-12-1-E** — 🟢 **There are now three `argus/pipeline*.py` siblings, and no guard asserts the
  family's SHAPE.** `pipeline.py` (944), `pipeline_persist.py` (268) and `pipeline_stages.py`
  together are the audit fold. Two guards now close over the family by glob
  (`TC-ArgusAgent-PIPELINE-002-11`), but nothing states the intended layering — orchestration and
  the typed contracts in `pipeline.py`, `.argus/` writes in `pipeline_persist.py`, derivation in
  `pipeline_stages.py` — or fails when a future story puts an orchestration decision in a derivation
  module. The layering is currently documented in three docstrings and enforced only by the fact
  that the dependency graph happens to be acyclic today. **Not built here:** an `ast`-derived
  layering assertion is a third new guard, and 12.1 already ships two.
  - id: DF-12-1-E
  - origin_story: 12-1-pipeline-stops-breaching-its-own-limit
  - owner: Engineering
  - target_story: NONE — the next story that adds a fourth `argus/pipeline*.py` module (12.2 is the
    likely trigger)
  - category: maintainability
  - severity: 🟢

## Deferred from: story 12-2-deep-audit-is-wired-opt-in-and-honest (2026-08-13)

**Append-only (§3.4): nothing above this heading was edited, reordered or deleted.** Proven
programmatically, not by eye — `git diff --numstat <base> HEAD -- deferred-work.md` shows **zero
deletions**. Every figure below is **LOCAL, Windows / CPython 3.11.15**, re-derived by execution on
this tree on 2026-08-13 under the dated risk acceptance of 2026-08-11 (carried forward, not
re-taken). **CI evidence: NOT ESTABLISHED** — no CI run has executed any Epic 10, 11 or 12 sha.

### Rulings on entries that named this story

- **`DF-12-1-A` — RE-RECORDED, not closed. The trigger FIRED and is ruled on rather than ignored.**
  Its target was *"the next story to edit the pipeline surface this file demonstrates"*, and this
  story did edit that surface: `argus/pipeline.py` gained a gated deep-pass call site and
  `run_audit` / `run_audit_detailed` each gained two optional keyword seams (`deep_port`,
  `disclose`). So the trigger fired honestly and is not dodged. **It is NOT closed here, for a
  measured reason.** `tests/test_pipeline_signature_demo.py` is still **1326** lines (re-measured
  2026-08-13; unchanged by this story, which did not touch it). Splitting it is a refactor of the
  load-bearing guard file that demonstrates the FR32 pipeline signature end to end over real git
  fixtures — inside a story that adds the only egress path in the product and carries seven ACs,
  one of which requires proving the DEFAULT path byte-identical. **Refactoring the guard that would
  notice a pipeline regression, in the same change that modifies the pipeline, removes the witness
  for the property this story most needs witnessed.** That is the same reasoning 12.1 gave, and it
  is stronger here, not weaker. The exemption registry still **shrinks**
  (`TC-ArgusAgent-MAINT-001-04` fails if the entry names a file that is gone or no longer over the
  cap), so this cannot become dead weight. Re-targeted at a live story with a named condition.
  - id: DF-12-1-A
  - origin_story: 12-1-pipeline-stops-breaching-its-own-limit
  - owner: Engineering
  - target_story: **12-3-a-re-run-returns-the-recorded-result** — which already owns `DF-12-1-B`,
    the sibling exemption, so both over-cap guard files are split by one story with one method
    rather than one-at-a-time by whichever story happens to brush past them
  - category: maintainability
  - severity: 🟢

- **`DF-12-1-E` — the trigger did NOT fire. Recorded explicitly rather than left silent.** Its
  condition is *"the next story that adds a fourth `argus/pipeline*.py` module"*. This story added
  **`argus/audit/deep_pass.py`**, not a fourth pipeline sibling: re-measured 2026-08-13,
  `git ls-files -- 'argus/pipeline*.py'` is still **three** (`pipeline.py` 1007,
  `pipeline_persist.py` 268, `pipeline_stages.py` 512). The placement followed the story's §A.1
  recommendation for the reasons it gave and which were re-checked here: `argus/audit/` is where the
  determinism quarantine already reasons, so the new module was INSIDE the fence AC2.2 widened
  before it had any behaviour, whereas a fourth `pipeline*.py` sibling would have put a
  provider-adjacent concern in the family this entry says has no layering guard. **`pipeline.py`
  grew 944 → 1007** (+63, still 193 under the cap) — the call site, the two optional seams and their
  reasoning. Entry unchanged and still open.
  - id: DF-12-1-E
  - origin_story: 12-1-pipeline-stops-breaching-its-own-limit
  - owner: Engineering
  - target_story: NONE — the next story that adds a fourth `argus/pipeline*.py` module (12.2 did
    NOT; re-confirmed 2026-08-13)
  - category: maintainability
  - severity: 🟢

- **`DF-12-1-D` — conditional trigger did NOT fire, but the HAZARD was live and was heeded.** Its
  condition is *"the next story that edits `tests/test_module_size_ceiling.py`"*; this story did not
  edit that file. The hazard itself, however, applied directly: the NFR-M1 sweep reads the git
  **INDEX**, and this story adds a new `argus/**` module, so an unstaged `argus/audit/deep_pass.py`
  would have been invisible to the sweep that governs it. **`git add`-ed early, deliberately**, and
  the population moved **73 → 74** tracked `argus` files as a result — which is also what turned the
  dogfood currency guards red by design and triggered the sanctioned regeneration. Entry unchanged.
  - id: DF-12-1-D
  - origin_story: 12-1-pipeline-stops-breaching-its-own-limit
  - owner: Engineering
  - target_story: NONE — the next story that edits `tests/test_module_size_ceiling.py`
  - category: testability
  - severity: 🟡

### Ruled OUT of this story, with reasons

- **`DF-10-2-A` — RULED OUT and ESCALATED. This is the THIRD consecutive story to carry it with no
  home, and it is not a dev agent's to close.** C/C++/Ruby/Rust grammars load and ground but extract
  zero definitions. It has no relationship to the LLM seam, egress, the opt-in, spend or honest
  degradation — nothing in this story touches it, and it is confirmed untouched. `AI-E11-7` states
  the need precisely: *"a fix is probably not needed … what is needed is a dated decision"* — a
  type-(H) governance decision outside the authority of an implementing agent. **Escalated as an
  operator-level item for the Epic-12 retrospective rather than folded in silently.** Recording it
  as "not mine" for a third time without escalating would be the drift the ledger exists to prevent.
  - id: DF-10-2-A
  - owner: **OPERATOR (XAgent007)** — needs a dated decision, not an implementation
  - target_story: NONE — **Epic-12 retrospective**, as a governance item
  - category: governance
  - severity: 🟡

- **`DF-11-2-A` / `DF-11-2-B` and SD-4's four convergent filings — OUT.** Grammar and
  test-name-convention surface, targeted at **12.5**. Confirmed untouched by this story: no module
  under `argus/detectors/` was modified, and no convention table was edited.
- **`DF-8-3-A` — OUT.** Report next-action vocabulary, deliberately re-recorded to **12.4** by Story
  12.1 with measured reasons. This story's §A.4 fence holds: the depth-honesty disclosure sentence
  and its predicate were changed because FR36's *"never produces a false deep claim"* is this
  story's own requirement; nothing else in the report vocabulary was restructured.
- **`DF-11-4-D` / `AI-E11-6` — OUT, and the caveat is discharged explicitly.** This story DID have
  to touch `_NOTE_SECTIONS` (a new release-note section for `--deep-audit` is required by the
  invocation-contract registry, which demands a real CHANGELOG site). **Adding a section is not the
  same as re-opening the impact-rank question, and the rank question was not re-opened**: the new
  entry is a PURE INSERTION placed sixth with its placement reasoned in the registry comment, and
  **no existing section moved relative to any other**. The registry's cost/benefit question stays
  open and stays 12.4's.

### New filings

- **`DF-12-2-A` — 🟡 `--passes` silently accepts unknown tokens, and `_ALL_PASSES` is a DEFAULT, not
  a whitelist.** `argus/cli.py::_resolve_passes` calls `_split_csv(args.passes, _ALL_PASSES)`, where
  `_ALL_PASSES` is the value used when the flag is OMITTED — it never validates. So
  `--passes coverage,typo` runs coverage and silently ignores `typo`, and an operator who misspells
  a pass name gets a narrower audit than they asked for with no diagnostic. This was the mechanism
  behind the false deep claim Story 12.2 closed (`--passes coverage,deep` reached the disclosure
  predicate with nothing wired), and **that specific harm is fixed**: the disclosure is now derived
  from work performed, so an unknown `deep` token can no longer produce a depth claim. **The general
  validation gap is deliberately NOT fixed here**, for two measured reasons: (a) it changes the
  behaviour of a **LOCKED** flag for every pass, not just `deep` — a run that quietly ignored a typo
  would start failing, which is correct but is a consumer-visible contract change; and (b)
  `.github/workflows/argus-student-audit.yml` depends on `--passes`, and this story has **no CI
  evidence** (§0.2, `AI-E10-1`) with which to verify a workflow-affecting change. Strict validation
  would be defence in depth, not the remedy — the remedy landed.
  - id: DF-12-2-A
  - origin_story: 12-2-deep-audit-is-wired-opt-in-and-honest
  - owner: Engineering
  - target_story: NONE — the next story with executed CI evidence that may change a LOCKED flag's
    accept/reject behaviour
  - category: correctness
  - severity: 🟡

- **`DF-12-2-B` — 🔴 `OpenLLMAdapter._dispatch_httpx` FABRICATES an `LLMRecording` when no endpoint
  is configured, and it is indistinguishable from a real dispatch at the port boundary.** Measured
  2026-08-13 at the anchor `if not self._api_base:` with the comment *"Fake/Mock dispatch mode when
  no live endpoint is configured"*: the branch returns `input_tokens=10`, `output_tokens=5`,
  `credits_used` from `0.000025`, `finish_reason="stop"`. A caller cannot tell that from a real
  response — it is a synthetic result manufactured out of an unconfigured environment. Combined with
  `__init__` absorbing six environment variables and defaulting the API key to the literal
  `"mock-key"`, an adapter constructed by accident produces plausible-looking depth. **Story 12.2's
  own path is safe and that is proven** (`TC-ArgusAgent-AUDIT-001-69`): the deep pass validates
  provider configuration BEFORE dispatch and refuses to construct an adapter when none is present
  (§A.5 option 1), so the branch is unreachable from the verdict. **THE RESIDUAL IS REAL AND IS
  DISCLOSED RATHER THAN HIDDEN: the adapter still fabricates for every OTHER caller**, and any
  future caller that constructs it directly inherits the hazard. The honest fix is option (2) —
  `_dispatch_httpx` raises `LLMDispatchError` instead of fabricating — which was NOT taken here
  because it changes a module whose own committed tests (`tests/test_open_llm_adapter.py`,
  `tests/test_minions_llm_adapter.py`) assert the mock-mode behaviour, i.e. a behaviour change with
  a test-suite blast radius inside a story already carrying seven ACs.
  - id: DF-12-2-B
  - origin_story: 12-2-deep-audit-is-wired-opt-in-and-honest
  - owner: Engineering
  - target_story: NONE — the next story that may change `argus/audit/open_llm_adapter.py` behaviour
    and re-baseline its two committed adapter test files
  - category: correctness
  - severity: 🔴 (the severity is about the hazard's nature, not its current reachability: no
    production path reaches it today, and that is asserted by a committed gate)

- **`DF-12-2-C` — 🟢 `tests/test_v1_commitment_closure.py` grew 1308 → 1412 lines under exemption
  `DF-12-1-B`, so the split 12.3 owns got bigger.** AC7 required edits to this file (FR36's
  disposition flip, the `seam_modules` field, the `not_built_refutations` direction and its
  positive control `-37b`). They were kept as tight as the reasoning allows and the prose was
  trimmed once specifically to reduce the growth, but the file is now **212 over** the NFR-M1 cap
  rather than 108. **Filed rather than silently absorbed**, because `DF-12-1-B`'s estimate of the
  work is now stale and 12.3 should size against the real number. The alternative — putting `-37b`
  in a dedicated file — was considered and DECLINED: it is the third direction of one closure and
  belongs beside `-36`/`-37`, and separating a positive control from the function it controls is
  exactly how a control stops being maintained alongside it.
  - id: DF-12-2-C
  - origin_story: 12-2-deep-audit-is-wired-opt-in-and-honest
  - owner: Engineering
  - target_story: **12-3-a-re-run-returns-the-recorded-result** — the story that already owns
    `DF-12-1-B` for this same file
  - category: maintainability
  - severity: 🟢

## Deferred from: code-review of story 12-2-deep-audit-is-wired-opt-in-and-honest (2026-08-13, iteration 1)

**Append-only (§3.4): nothing above this heading was edited, reordered or deleted.**

- **`DF-12-2-E` — 🟢 `argus/audit/deep_pass.py::PROVIDER_ENDPOINT_VARIABLES` (3 vars) duplicates
  `argus/audit/open_llm_adapter.py::OpenLLMAdapter.__init__`'s `_api_base` derivation
  (`OPENAI_BASE_URL` / `OLLAMA_HOST` / `OLLAMA_URL`) as a second, hand-written literal instead of
  importing or deriving it from the adapter.** Verified during code review: the two lists are
  currently identical and the duplication is on the SAFE side (a variable added only to the
  adapter's `_api_base` chain would make `resolve_provider_endpoint()` under-report configuration —
  degrade, never fabricate) — so this is not a security defect, but it is the same "two literals
  that can drift apart" shape `deep_pass_enabled()` / `with_deep_pass()` elsewhere in this same
  story deliberately collapsed to one. A future change to the adapter's endpoint-variable set would
  not be caught by any test the way `TC-ArgusAgent-AUDIT-001-62`'s `ast`-derived population catches
  the adapter's full env-var surface.
  - id: DF-12-2-E
  - origin_story: 12-2-deep-audit-is-wired-opt-in-and-honest (filed at code review)
  - owner: Engineering
  - target_story: NONE — the next story that touches `argus/audit/deep_pass.py` or
    `argus/audit/open_llm_adapter.py`'s endpoint resolution
  - category: maintainability
  - severity: 🟢

- **`DF-12-2-D` — 🟡 The `delivered` branch of the deep pass is UNREACHABLE through the shipped
  `OpenLLMAdapter`: neither `_dispatch_litellm` nor `_dispatch_httpx` ever populates
  `LLMRecording.structured_output`.** Both methods capture the response's `model`, `usage` and
  `finish_reason` and DISCARD the completion content, constructing `structured_output=()`
  unconditionally (three construction sites in `argus/audit/open_llm_adapter.py`).
  `argus/audit/deep_pass.py::_dispatch_one` requires a non-empty `structured_output` and returns
  `REASON_EMPTY_RESPONSE` BEFORE `_claim_is_ast_grounded` is ever consulted. **Consequence,
  measured over a mocked transport (no socket, no DNS — `.invalid` endpoint per RFC 6761):** a
  fully successful dispatch to a healthy provider returning well-formed content yields
  `structured_output == ()`, so EVERY real dispatch — success or failure — degrades as
  `empty-response`, and `delivered_count > 0` is reachable only through an injected test double.
  **This is a PRE-EXISTING limitation of `open_llm_adapter.py`** (unmodified by Story 12.2's diff;
  independently corroborated by the pre-existing `tests/test_open_llm_adapter.py` assertion that a
  real dispatch yields `rec.structured_output == ()`, written for NFR-S1 reasons) **made
  load-bearing for the first time by Story 12.2's wiring.**

  **It is NOT a safety hole and it is NOT a vacuous wiring — both were tested, not assumed.** The
  egress path genuinely fires: the pipeline constructs the real adapter and the request really
  reaches the transport (`TC-ArgusAgent-AUDIT-001-73` asserts the POSTs and their targets). What is
  unreachable is only the FAVOURABLE outcome, so the failure polarity is the opposite of this
  project's dominant defect class: the pass UNDER-claims rather than over-claims, and FR36's *"never
  produces a false deep claim"* is made unconditional by the gap rather than weakened by it. The gap
  is **one field wide and it is the adapter's**: `TC-ArgusAgent-AUDIT-001-74` is the positive control
  — same real adapter, same mocked transport, same real pipeline entry point, the discarded
  completion carried onto `structured_output` and NOTHING else changed — and the pass delivers, the
  strengthened disclosure becomes true, and the AR4 credit string is the real adapter's own. So
  everything Story 12.2 wired downstream of the port is proven correct on real provider-shaped input.

  **Why it was NOT closed in Story 12.2's review round, measured rather than assumed.** Populating
  the field honestly is not a one-line change: (a) `_build_messages` never ASKS the model for
  structured output — there is no claim grammar and no response contract, so there is nothing
  well-formed to parse; (b) `structured_output`'s documented contract in `argus/audit/ports.py` is
  *claim/locator-shaped strings, NEVER raw prompt/response bytes* (NFR-S1 producer-side redaction),
  so tipping the completion text into it is a documented contract VIOLATION rather than a fix; (c)
  `tests/test_open_llm_adapter.py` asserts `rec.structured_output == ()` with the explicit rationale
  *"NFR-S1 — the recording carries metadata only; no prompt/response bytes anywhere"*, so closing
  the gap requires re-baselining a committed NFR-S1 security assertion on the product's ONLY egress
  path; (d) a real claim format means a prompt contract, a redacting parser and a
  `DEEP_PROMPT_TEMPLATE_VERSION` bump, which is an AR5 cache-key closure input; and (e) it could not
  be validated — §0.3 forbids any live dispatch and CI evidence is NOT ESTABLISHED (AI-E10-1).
  **`deep_audit.py` and `_claim_is_ast_grounded` both already name full claim-grammar grounding as
  Story 6.2's**, so the work has an owner already and doing it here would fork it.

  **Disclosed, not hidden, in four places** (the discipline `DF-12-2-B` set): the `deep_pass.py`
  module docstring; the FR36 `_Delivery` note in `tests/test_v1_commitment_closure.py`, which is
  where the word `wired` is asserted and where it is now explicitly scoped; a user-facing KNOWN
  LIMITATION paragraph in `CHANGELOG.md` telling an operator not to pay a provider for depth they
  will not get; and the two committed measurements above. **`TC-ArgusAgent-AUDIT-001-73` is designed
  to go RED the day this entry is closed**, so the record cannot rot into a stale assertion.
  - id: DF-12-2-D
  - origin_story: 12-2-deep-audit-is-wired-opt-in-and-honest (filed at code review, iteration 1;
    measured and dispositioned in the iteration-1 fix round)
  - owner: Engineering
  - target_story: **6-2-style claim-grammar work — the story that gives the deep pass a declared
    claim format and a response contract**; until one is scheduled, the next story that changes
    `argus/audit/open_llm_adapter.py`'s response handling (which is also `DF-12-2-B`'s trigger —
    the two should be closed together, since both are about what that module returns)
  - category: correctness
  - severity: 🟡 (the capability is incomplete, but it fails SAFE and is now disclosed at
    every site a user or a reader of FR36 would otherwise be misled)

## Deferred from: story 12-3-a-re-run-returns-the-recorded-result (2026-08-13)

**Baseline re-measured on this tree before any edit, never transcribed:** bare `python -m pytest`
= **1441 passed / 0 failed / 0 error / 0 skipped in 137.81s**; `HEAD` `58c8f6b`; `origin/master`
UNMOVED at `00c8d1b`; `git tag -l` EMPTY; `git ls-files -- argus` = **74**; `python -m argus.cli
audit .` = `RELEASE_READY deep_ratio=64/177 blocking_findings=0 assessed_deep_ratio=4/5
scope=application held_out=97`, exit 0; `.argus/cache/` held **0** files (the zero-migration
premise, confirmed). Closure probe re-run against the guard's own builder: **74** graph nodes,
**58** reachable from `argus.cli`, `argus.cache.memo_store` **reachable=False**.

### New filing

- **`DF-12-3-A` — 🟡 PRD §501 is NOT delivered: with `--deep-audit` on, a re-run still
  dispatches, so the DEEP component of a verdict is not reproducible through the FR27/NFR-D1
  memoization path.** `E-PRD/prd.md:501` (under FR36) states *"Determinism is preserved by the
  FR27/NFR-D1 memoization path — a re-run returns the recorded result. Enabling this pass must not
  make the verdict irreproducible."* Story 12.3 wired that path, and it is **scoped to the
  deterministic detect/grade stage only**. The deep pass runs DOWNSTREAM of the memo hook, inside
  `pipeline._assemble_and_persist`, and no LLM-derived byte is ever served from the store.
  Measured, not asserted: `TC-ArgusAgent-CACHE-001-98` runs `--deep-audit` twice over one repo
  with an injected port and shows the deterministic stage HITS while the port dispatches the SAME
  number of times on both runs, and it sweeps the persisted slot BYTES for LLM-derived rule ids.

  **Why it was scoped rather than delivered — three measured reasons, none of them convenience.**
  (a) The cache key's `model_checkpoint` is the fixed sentinel `v1-heuristic-no-llm` and its
  `prompt_template_version` is `v1-no-prompt-template`, while the deep pass dispatches under
  `DEEP_PROMPT_TEMPLATE_VERSION = "argus-deep-v1"` to whatever `ARGUS_LLM_MODEL` / `OLLAMA_MODEL`
  resolves. **Neither value reaches the key**, so memoizing deep output under this key as it
  stands would let two runs against two DIFFERENT MODELS collide on ONE cache slot, and the store
  would serve a result computed under model A to a run that asked for model B — the single failure
  `argus/cache/key.py` exists to make impossible. (b) `DF-12-2-D` (open) records that the
  `delivered` branch is unreachable through the shipped adapter, so what would be memoized today
  is the `empty-response` DEGRADATIONS — *"memoization caches errors → reproducibility ≠
  correctness"* is `memo_store.py`'s own named failure mode. (c) Doing it honestly requires
  folding the CAPTURED checkpoint and a real prompt-template version into the closure — that is
  `argus/audit/deep_audit.py::build_closure_from_recording` plus a claim grammar, which
  **`DF-12-2-D` already assigns to 6.2-style claim-grammar work with a named owner**; re-homing it
  here would fork an owned item. Story 12.3's §0.3(c) also forbids the live dispatch that would be
  needed to validate it, and `AI-E10-1` records that CI evidence is NOT ESTABLISHED.

  **Made impossible rather than left as a warning.** `argus/cache/memo_store.py::_fence_llm_derived`
  refuses, at the store's write path, to persist a payload containing an LLM-derived recording
  while the closure carries the V1 placeholder checkpoint, and its message names the
  model-collision hazard rather than merely forbidding the act. The fence is CONDITIONAL: once a
  real captured checkpoint reaches the closure the key can discriminate and the fence stands down
  by itself, so it fences a key that cannot yet tell two models apart rather than banning deep
  memoization forever. Both directions are pinned by `TC-ArgusAgent-CACHE-001-96`, and
  `-97` pins the fence's rule-id vocabulary against `deep_pass.RULE_DEGRADED_DEEP_READ` so the
  literal cannot silently drift out of step (memo_store may not import deep_pass — NFR-S6).

  **Disclosed where a reader would otherwise be misled**, per the discipline `DF-12-2-B` set: the
  `argus/cache/stage_memo.py` module docstring (the module that owns the hook) carries a 🔴 SCOPE
  DISCLOSURE section; the hook's call site in `argus/pipeline.py` carries the same scope note;
  `architecture.md` §Memoization carries it under the amended step-2 record; and **Story 12.4 is
  named explicitly** — that story writes the next-action text a user reads about what a verdict
  means, and **it must not imply that a deep verdict is reproducible.**
  - id: DF-12-3-A
  - origin_story: 12-3-a-re-run-returns-the-recorded-result
  - owner: Engineering
  - target_story: **the same 6.2-style claim-grammar work `DF-12-2-D` already names** — the two
    are the same blocker seen from two sides and should be closed together: a declared claim
    format makes the `delivered` branch reachable AND supplies the real prompt-template version
    that, with the captured checkpoint, lets the key discriminate between models. Until one is
    scheduled: the next story that folds a captured checkpoint into `RecordingProducingClosure`.
  - category: correctness
  - severity: 🟡 (a documented capability is narrower than the PRD states; it fails SAFE — the
    deterministic component is fully memoized and the deep component is recomputed every run,
    which is slower, never wrong — and it is now disclosed at four sites)
  - cross-reference: `DF-12-2-D` (why the `delivered` branch is unreachable today), `DF-5-1-A`
    (closed — the prompt-template slot that makes the eventual fix additive)

### Corrections to an existing entry — recorded as a new append (§3.4 append-only)

- **`DF-12-1-B` — its stated TRIGGER is measurably FALSE, and its size figure is stale by 111.**
  The entry says wiring the memo store *"flips a `library-seam` disposition and turns it red until
  the disposition is updated"*. **It does not, and this was established by EXECUTING the guard's
  own code rather than by reading it.** FR27 was disposed **`delivered-differently`**, never
  `library-seam`; `reachability_refutations` refutes exactly `wired`-over-unreachable and
  `library-seam`-over-reachable, and its own docstring says `delivered-differently` *"makes no
  reachability claim and is never refuted here"*. Executed on `58c8f6b` with `memo_store` forced
  REACHABLE, the FR27 tuple returned `()` while the identical tuple disposed `library-seam` fired
  immediately. **So wiring the store would have turned NOTHING red**, and the registry would have
  gone on asserting *"the memoization MECHANISM is unwired … Mechanism deferred to Story 12.3"*
  about a mechanism that had just been built, behind a fully green suite. The SUBSTANCE the entry
  pointed at was real; the mechanism it named would never have fired.
  **Both halves are now closed** (Story 12.3, AC6.3): FR27's entry is re-derived to `wired` with
  the superseded sentence recorded rather than deleted, AND the refutation gap that let it rot is
  closed by `delivered_differently_refutations` — a fourth direction, as narrow as Story 12.2's
  `not_built_refutations`, firing only when a reason makes a registered unwiredness/deferral claim
  over a module that IS reachable. Proven **RED-first with the final committed code** against the
  real pre-fix registry state, and driven in all three outcomes over a synthetic graph by
  `TC-ArgusAgent-DOCS-001-37c`. Registered in `architecture.md` §Enforcement.
  **Size figure:** the entry records `tests/test_v1_commitment_closure.py` at **1308** lines; it
  measured **1419** at the start of this story and **1581** after it (this story edits the registry
  that file holds). The 1200-line breach itself **stays exempt** for the reason 12.1 and 12.2 both
  gave, and which is stronger here: splitting a delivery-closure guard inside the very story that
  changes what that guard measures removes the evidence for the property being changed. The
  exemption registry still SHRINKS (`TC-ArgusAgent-MAINT-001-04`), so it cannot become dead weight.
  - id: DF-12-1-B (correction appended; the original entry is NOT edited — §3.4)
  - origin_story: correction filed by 12-3-a-re-run-returns-the-recorded-result
  - owner: Engineering
  - target_story: unchanged
  - category: correctness (of the ledger entry itself) + maintainability (the size exemption)
  - severity: 🟡

### Every other §F item, ruled — none left silent (AC7.6)

- **`DF-12-1-A` — 🟢 OUT, and ESCALATED rather than re-homed a FOURTH time.**
  `tests/test_pipeline_signature_demo.py`, re-measured **1326** lines (unchanged by this story).
  The measured reason not to close it here is the same one 12.1 and 12.2 gave and is again
  stronger: **this story modifies the pipeline surface that file demonstrates**, and refactoring
  the witness in the same change that alters what it witnesses removes the evidence for the
  property this story most needs witnessed. It has now been carried by THREE consecutive stories
  and was already escalated to the **Epic-12 retrospective** as needing a dedicated home rather
  than a fourth re-homing. **This story does not re-escalate it as if new and does not re-home
  it** — it records that the escalation still stands and that the file is unchanged.
- **`DF-12-2-D` — 🟡 OUT. Cited, NOT re-homed.** Owner and target are already assigned. It is
  load-bearing CONTEXT for `DF-12-3-A` above and is cited there in full; silently adopting it here
  would fork an owned item.
- **`DF-12-2-E` — 🟢 OUT, trigger did NOT fire.** Its trigger is a story that touches
  `argus/audit/deep_pass.py` or the adapter's endpoint resolution. **Story 12.3 did not edit
  either file** — verified by `git status`/`git diff --stat`. The AC6.1 fence deliberately lives
  in `argus/cache/memo_store.py`, not in `deep_pass.py`, precisely because `memo_store` may not
  import the dispatch surface (NFR-S6); the join between the fence's rule-id literal and
  `deep_pass.RULE_DEGRADED_DEEP_READ` is made in the TEST layer (`TC-ArgusAgent-CACHE-001-97`),
  which is the same "two literals that can drift" shape this entry is about, closed the same way.
- **`DF-10-2-A` — 🟡 OUT, and it is not this story's to close.** C/C++/Ruby/Rust ground but
  extract zero definitions. Story 12.2 escalated it to the **Epic-12 retrospective** with owner
  **OPERATOR (XAgent007)**; `AI-E11-7` says what is needed is *a dated decision, not an
  implementation*. **Left flagged for the retrospective, not silently re-homed and not
  re-escalated as if new.**
- **`DF-12-1-D` — 🟡 hazard was LIVE; trigger did NOT fire.** Its trigger is *"the next story that
  edits `tests/test_module_size_ceiling.py`"* and **this story does not edit that file**. The
  HAZARD applied directly and was handled: the NFR-M1 sweep reads the git **INDEX**, so an
  unstaged new module is invisible to the guard that governs it. `argus/cache/stage_memo.py` and
  all three new test files were `git add`-ed IMMEDIATELY on creation, and the sweep then did its
  job — it caught `tests/test_stage_memo_wiring.py` at **1388** lines, 188 over the ceiling, and
  the sanctioned remedy (a COHESION split, never shaving lines and never an exemption) was taken:
  the file was split into `tests/test_stage_memo_wiring.py` (*is the cache load-bearing?*) and
  `tests/test_stage_memo_contract.py` (*can the cache lie?*) over a shared
  `tests/_stage_memo_corpus.py`, following the `tests/cartridges/_cartridge.py` fixture-module
  precedent. **No exemption was added.**
- **`DF-12-1-E` — 🟢 trigger did NOT fire, recorded either way.** Its trigger is *"the next story
  that adds a fourth `argus/pipeline*.py` module"*. Re-measured after this story's changes:
  `git ls-files -- 'argus/pipeline*.py'` is still **three** (`pipeline.py`, `pipeline_persist.py`,
  `pipeline_stages.py`). This story's new module is `argus/cache/stage_memo.py` — placed in the
  package that already owns the cache concern, which is both the story's own structural guidance
  and the reason the trigger does not fire.
- **`DF-5-1-A` — CLOSED 2026-06-28, not reopened.** Its CONTRACT is live and is now proven over
  the wired path: `TC-ArgusAgent-CACHE-001-94` asserts the `prompt_template_version` slot still
  moves the key, using the LIVE `DEEP_PROMPT_TEMPLATE_VERSION` rather than another sentinel, so
  the forward-coupling hole stays closed for the day a real value lands.

### Ruled OUT OF SCOPE with reasons, as AC5.4 requires out loud

- **Story 5.3 ACTIVE invalidation (`argus/cache/invalidation.py`) — 🟢 OUT OF SCOPE, option (b).**
  Not silence: the ruling is asserted by `TC-ArgusAgent-CACHE-001-95`, which requires the 5.3
  surface to remain importable and intact AND records the measured fact the ruling rests on —
  `argus.cache.invalidation` is **not** in the import closure from `argus.cli` (re-measured after
  this story: 75 graph nodes, 60 reachable; `memo_store` flipped to reachable, `invalidation` did
  not). Reasons: the epic AC names only *"the DF-5-1-A invalidation contract holds over the wired
  path"*, which is delivered by `-94` plus the NATURAL misses of `-86`/`-92`/`-93`; wiring active
  eviction is a SECOND delivery with its own correctness surface (deleting entries is destructive
  in a way consulting them is not); and it is unnecessary for correctness here, because a
  detector-set edit ALREADY moves the key onto a different slot — the 5.2-vs-5.3 fence
  `memo_store.py` states in its own docstring. **If a later story wires it, `-95` goes red and the
  ruling must be re-taken rather than inherited.**
  - id: DF-12-3-B
  - origin_story: 12-3-a-re-run-returns-the-recorded-result
  - owner: Engineering
  - target_story: NONE — unscheduled; the natural MISS makes it an optimization, not a correctness
    requirement. To be scheduled if cache-slot growth over long-lived repositories becomes a
    measured problem (nothing measures it today, and nothing claims it does).
  - category: scope
  - severity: 🟢

### Filed in passing — measured by this story, NOT caused by it, NOT fixed by it

- **`DF-12-3-C` — 🟢 `tests/test_secret_containment.py` cannot be collected in ISOLATION: it
  inserts a `sys.path` entry for `argus/cartridges`, a directory that has never existed.** The
  cartridges live at `tests/cartridges`. Measured 2026-08-13 while running the AC7.2 gate list as
  a subset: `python -m pytest tests/test_secret_containment.py` alone fails at COLLECTION with
  `ModuleNotFoundError: No module named '_cartridge'`. It passes in the full suite only because
  another module (e.g. `tests/test_sequential_portability.py`, which inserts the CORRECT
  `tests/cartridges` path) happens to be imported first, leaving the right directory on
  `sys.path`. **Attributed, not inherited:** the file is byte-identical to `58c8f6b`
  (`git diff HEAD -- tests/test_secret_containment.py` empty), the same line is present in the
  `58c8f6b` blob at line 66, and `git ls-tree 58c8f6b -- argus/cartridges` is empty, so the
  directory never existed at the baseline either. **This is therefore PRE-EXISTING and is not a
  regression introduced by Story 12.3.** It is filed rather than fixed because fixing an
  unrelated test module's import path inside the story that wires the memoization store would mix
  two changes, and because the guard is GREEN in the only configuration the gates actually run it
  in (the full suite). The risk it carries is real but latent: any future change to test ordering,
  or any attempt to run this NFR-S1 containment gate on its own, silently gets a collection error
  rather than a security assertion.
  - id: DF-12-3-C
  - origin_story: 12-3-a-re-run-returns-the-recorded-result (measured in passing; not caused here)
  - owner: Engineering
  - target_story: NONE — the next story that touches `tests/test_secret_containment.py` or the
    cartridge staging convention
  - category: maintainability (test-harness fragility on a security gate)
  - severity: 🟢


## Deferred from: story 12-7-commands-the-readme-promises-actually-exist (2026-08-15)

**Append-only (§3.4): nothing above this heading was edited, reordered or deleted.**

### Closed by this story

- **`DF-11-5-C` — CLOSED 2026-08-15.** *"`README.md`'s seven `/audit …` commands are documented but
  undelivered"* — filed by Story 11.5 so that 12.7 would know the `FORTHCOMING` marker was its to
  remove. It is closed in the only way that is a delivery rather than a deletion: the distribution
  now **ships** the command assets (`argus/assets/commands/*.md`, in the built wheel **and** sdist),
  a documented packaged step places them (`argus install-commands`), and the marker is gone because
  the gap it described is gone. **Four of the seven commands were removed rather than built**, each
  with its reason recorded on the consumer surfaces (struck, not deleted): `repo` and `architecture`
  name no pass the CLI has, `subsystem <name>` needs a scoping capability that does not exist, and
  `resume` is `DF-3-4-A` — a working engine with no CLI entrance, which stays open and is NOT
  re-filed here. Three commands ship and resolve through the real parser.
  ⚠️ **The guard that held this entry was CORRECTED, not merely satisfied.**
  `TC-ArgusAgent-DOCS-001-56`'s delivered-state branch had **never executed** (it carried
  `# pragma: no cover`) and, as written, asserted only *"the marker is gone"* and then `return`ed —
  so from the moment an asset shipped, nothing held the documented set to the shipped set, and the
  test could have been satisfied by DELETING the commands from the README. The branch now asserts
  set equality in both directions with a non-vacuity floor on each side. Recorded here because a
  guard that stops guarding at the moment of delivery is the defect class this ledger exists for,
  and this is its third instance in Epic 12 (`-49`'s registered-surface loop, `_ENTRY_POINT`'s
  prose, and now `-56`).

### Re-stated, NOT re-filed — cited by this story and still open

- **`DF-3-4-A`** (resume has no CLI entrance) and **`DF-10-5-C`** (FR29 evidence export needs a CLI
  surface) are the reasons two published commands were removed rather than implemented. Both stay
  open under their existing owners and target stories; neither is re-filed, because a gap filed
  twice is a gap that gets closed once and left looking open.

### Filed by this story

- **`DF-12-7-A` — 🟢 the host registry ships ONE verified member (`claude-code`), while five hosts
  named by the old README have no registered convention.** DN-2 made this a decision rather than an
  omission: an entry exists only if its exact configuration directory and its exact resulting
  command spelling were verified, and six two-to-three-line `adapters/**` stubs were not a delivery
  for the other five. Each remaining host is **one reviewed registry entry, one derived README row
  and no new code path** away — the asset tree, the placement mechanism, the containment rule and
  the disclosure render are all host-independent by construction. Filed so the narrowing is visible
  rather than inferred from a list that got shorter.
  - id: DF-12-7-A
  - origin_story: 12-7-commands-the-readme-promises-actually-exist
  - owner: Engineering
  - target_story: NONE — unscheduled; the next story that adds a supported assistant
  - category: scope (deliberate narrowing, recorded)
  - severity: 🟢

- **`DF-12-7-B` — 🟢 a STALE installed command asset is detectable but not detected FOR the user.**
  AC6 asks which of two properties Epic 13's expiry gets, and the answer is stated rather than
  implied: **re-running `argus install-commands` produces the new text** (the render is a pure
  function of the packaged asset and the pinned constant, so an install after Story 13.3 flips
  `INSTRUMENT_STATUS` rewrites every file), and staleness **is** detectable — the bytes on disk stop
  equalling the bytes the renderer now produces. What does NOT exist is anything that *tells the
  user* their installed copy is stale; nothing warns them, and the tool never reads back what it
  wrote. Building that would need a read-back-and-compare path this story's sentence does not cover.
  Filed with a named owner rather than left silent, per AC6's own instruction.
  - id: DF-12-7-B
  - origin_story: 12-7-commands-the-readme-promises-actually-exist
  - owner: Engineering
  - target_story: **13.3** — the story that flips the instrument status is the one whose users will
    hold a stale copy
  - category: documentation-accuracy (FR34 expiry on a placed artifact)
  - severity: 🟢

---

## Story 12.8 closures + dispositions — 2026-08-15

Appended by Story 12.8 (`12-8-the-tool-explains-itself`).
**Append-only (§3.4): nothing above this heading was edited, reordered or deleted.** `git diff --numstat`
on this file is `+n / -0`. Two entries this story OWNS are dispositioned below; three it CITES are
restated without being re-filed, per 12.7's recorded rule — *a gap filed twice is a gap that gets closed
once and left looking open*.

### Closed by this story

- **`DF-8-4-D` — CLOSED 2026-08-15. An internal defect is now distinguishable from an expected
  degradation.** The entry's own coordinates were stale and its mechanism was **wider than recorded**;
  both are stated rather than quietly fixed. It cited `argus/cli.py:295-299`, corrected once to
  `:368-372`; on `2f84a0b` the audit arm was at **`:758`**, and there were **THREE** base-`ValueError`
  arms in `cli.py` (`:679` ship-readiness, `:707` `install-commands` — added by 12.7 and therefore
  invisible to the 2026-08-10 citation audit — and `:758` audit) plus a fourth in `argus/mcp/server.py`.
  The remedy anchors on TEXT, not on a line number (`epics.md:1771`).
  **The entry's suggested close — *"catch the named subclasses explicitly"* — would NOT have closed it,
  and this is the finding worth recording.** Measured: `argus/pipeline.py`'s four stage wraps already
  converted **any** unexpected exception into `PipelineError(f"… stage failed: {type(exc).__name__}")`,
  and `PipelineError` is one of the classes `cli.py`'s own comment enumerates as an EXPECTED typed
  degradation. An internal defect therefore arrived at the CLI **pre-disguised**, and no amount of
  `except` precision on the CLI side could have told the two apart. The distinction is carried **from the
  wrap site** by a new `pipeline.UnexpectedStageError` (a `PipelineError` subclass, so every existing
  handler catches it unchanged), and the renderer dispatches on typed class.
  **What ships:** a stable `INTERNAL DEFECT` marker on stderr saying plainly that this is a bug in Argus
  rather than a problem with the user's repository, plus where to report it; the exception **CLASS**
  only, never `str(exc)` (`DF-10-4-C`'s rule and NFR-S1's); exit **`1` for both**, because AR3 is frozen
  and the distinction belongs in the message, which is what this entry asked for.
  **Pinned in BOTH directions** by `TC-ArgusAgent-CLI-001-60`: a real missing repo path must NOT print
  the marker, and a real `pydantic.ValidationError` injected at the REAL intake seam — so it travels the
  real wrap — MUST. Neither direction alone is a guard. The enumeration itself is closed over the tree by
  `TC-ArgusAgent-REPORT-003-08`..`-10`.
  - status: **CLOSED 2026-08-15** — remedy delivered, entry's coordinates and mechanism corrected in
    place, and the un-closable form of the suggested close recorded rather than silently improved on

- **`DF-10-4-C` — PARTIALLY CLOSED 2026-08-15; the remaining half is RE-RECORDED with a reason, not
  carried forward silently.** The entry has two halves and they had different fates.
  **CLOSED — the surface.** The entry's own conclusion was that the diagnosis *"belongs on the surface
  that renders it"*, and Story 12.5 handed the function over by name. Measured on `2f84a0b`,
  `render_grammar_downgrade_summary` had exactly ONE production caller — `reports/generator.py:516`,
  inside the report path, which runs only when `--report-dir` is set — so on the DEFAULT invocation a
  downgraded grammar was invisible and the operator saw a lower ratio with no reason for it. It now
  reaches the default run's stderr from the SAME renderer (one renderer, two callers; the tokens are
  classified once, by `grammar_status.classify_reason`, and never re-classified by a second prefix
  guess). The plumbing is an additive optional `AuditResult` field — a thin value holder, NOT a persisted
  model — so **nothing new is persisted, no schema bumped and no verdict field added**; 10.4 / DN-5's
  double refusal stands. Proven at the real `importlib.import_module` seam with no `--report-dir`
  (`TC-ArgusAgent-CLI-001-63`), with the negative direction pinned by `-64`.
  **STILL OPEN — the exception CLASS behind a grammar-load failure** (`ValueError` vs `TypeError` vs
  `OSError`), with the reason stated so this is a disposition and not a drift. The recorded
  `parse_failure_reason` token carries the ARM (`grammar_load_failed_rust`), which is the distinction
  10.4 deliberately built and which the shipped remedy already acts on. Carrying the raw Python exception
  class as well needs a channel from `ast_index`'s loader to the renderer that does not go through the
  persisted `AstIndex` — and the only such channel is a SECOND diagnosis path running beside
  `parse_failure_reason`, which is the fork AR7 forbids and precisely what
  `argus/shared/grammar_status.py`'s docstring warns about. It is not blocked by this story; it is
  unfunded by any evidence that an operator needs it, and the honest record is that nobody has measured
  a case where the arm was insufficient.
  - id: DF-10-4-C
  - owner: **Engineering Lead** (unchanged)
  - target_story: **NONE — unscheduled.** The surface half is delivered; the class-payload half needs a
    story that also decides the second-channel question, and re-targeting it at a hypothetical future
    story would be the evaporation the Epic-8 retrospective §5 described
  - category: capability
  - severity: 🟢

### Re-stated, NOT re-filed — cited by this story and still open

- **`DF-3-4-A`** (resume has no CLI entrance) and **`DF-10-5-C`** (FR29 evidence export needs a CLI
  surface). Story 12.8 is *"the CLI surface"* story and both entries point at it, so the temptation to
  absorb them was real and is declined on the record. `DF-3-4-A` stays open under its existing owner —
  12.7 removed the published `/audit resume` command citing it and recorded *"stays open and is NOT
  re-filed"*, and this story CITES it for the same reason. `DF-10-5-C` names *"Story 12.8 (the CLI
  surface)"* as **where** such a sub-command would go, not as its owner, and leaves it `target_story:
  NONE — unscheduled; Governance Owner to schedule`; building it would be an unscheduled capability
  addition, which DN-6 (*this story adds explanation, not surface*) forbids. Neither is re-filed.
- **`DF-12-7-A`** (the host registry ships one verified member). Cited, untouched, still unscheduled.
- **`DF-12-1-C`** — noted rather than re-filed: its `target_story` names `12-5-…`, a story that is `done`
  and did not perform the split, so the `tests/test_grammar_diagnosis.py` exemption is ORPHANED. Story
  12.8 did NOT grow it — the CLI grammar-downgrade guard is homed in `tests/test_cli.py` beside the other
  diagnosis guards, deliberately, so an exemption nobody owns does not get larger — and the registry
  entry's reason is amended in place to say so. Its exemption's target is re-recorded as
  `NONE — unscheduled; the split is owed and belongs to a story that says so` — the same string the registry now carries, because
  `TC-ArgusAgent-MAINT-001-04` requires the two to agree and a target pointing at a completed story is
  a clause that can never fire.
  - id: DF-12-1-C (annotated here, NOT re-filed — the original entry above is byte-intact)
  - owner: **Engineering** (unchanged)
  - target_story: **NONE — unscheduled; the split is owed and belongs to a story that says so**

---

## Story 12.9 — the release is staged, and its status cites the gate (2026-08-15)

**Append-only, as always (§3.4 evidence immutability).** Nothing above this line was edited: the diff
for this story against `deferred-work.md` is `+n / -0`, verified programmatically
(`git diff --numstat -- _bmad-output/design-artifacts/ArgusAgent/deferred-work.md`).

### Closed by this story

- **`DF-10-3-A` — CLOSED 2026-08-15. argparse's usage exit code no longer collides with the BLOCKED
  verdict code.** The entry (filed by Story 10.3, owner **Engineering Lead**) offered three candidate
  resolutions and chose none, the first being *"map usage errors onto the reserved crash code `1`"*.
  **Story 12.8 / AC8 shipped exactly that first resolution** — and the ledger was never told, because
  the entry names *this* story rather than 12.8, so it was invisible to the story that fixed it. It
  therefore stood OPEN at `de05dec` describing a defect that no longer existed.
  **VERIFIED BY EXECUTION before closing, not on this story's say-so** (2026-08-15, `de05dec`, LOCAL):

  ```
  $ python -m argus.cli            -> exit 1
  $ python -m argus.cli audit --nosuchflag .   -> exit 1
  argus: the command line was rejected by the parser (see the usage message above), so NO audit ran
  and NO verdict was produced — exit 1 is the reserved 'no verdict' code, never a verdict.
  ```

  The mapping lives in `main()` only; `build_parser().parse_args` is byte-identical, so nothing that
  embeds the parser changed behaviour. `action.yml:110-135` carries the corrected map comment.
  `docs/first-run.md`'s exit table states the reserved `1` and is DERIVED from `exit_code_for_verdict`
  by `TC-ArgusAgent-DOCS-001-64`, so the published contract cannot drift back. Story 12.9's own
  `scripts/release_notes.py` now derives the same map into the GitHub Release note
  (`TC-ArgusAgent-DOCS-001-67`), which closes the last surface that transcribed it by hand.
  **What is NOT closed:** nothing. The two alternatives the entry listed (a distinct usage code outside
  `{0,1,2,3}`; documenting the collision and making consumers disambiguate) were not taken and are not
  needed — the chosen remedy removes the collision rather than describing it.
  - id: DF-10-3-A
  - owner: **Engineering Lead** (unchanged)
  - status: **CLOSED 2026-08-15** — remedy delivered by Story 12.8 / AC8, verified by execution here
  - target_story: **CORRECTED, append-only.** The entry above reads
    `12-9-publishing-and-release-surface`, which **is not a story key this tracker has**. The key is
    **`12-9-release-is-published-and-cites-its-gate`**, and the remedy in fact landed in
    **`12-8-the-tool-explains-itself`**. The original string is left byte-intact above; a ledger that
    names a story id the tracker does not have is how a deferral becomes nobody's (AI-E9-8), and that
    is precisely what happened to this entry.

### Filed by this story

- **`DF-12-9-A`** — **the seven outward-facing publication acts are staged, enumerated and NOT
  performed.** Story 12.9 built, proved, derived, guarded and documented the release and then HALTED:
  every act that reaches outside this working tree needs an explicit human authorisation naming that
  act, and none was given. Filed **once**, here, with a named human — the AC9 table in the story file
  is the detail, this is the ledger's single pointer to it, and it is deliberately not also implied
  anywhere else (12.7's rule: *a gap filed twice is a gap that gets closed once and left looking
  open*). The acts, with blast radius: (1) `git push origin master` — 34 commits, reversible only by
  force-push, and the ONLY thing that can turn the release status from `NOT ESTABLISHED` into a
  citation; (2) `git tag v0.1.0` — local, reversible; (3) `git push origin v0.1.0` — effectively
  irreversible, triggers `release.yml`; (4) the GitHub Release — irreversible in effect; (5) making the
  repository public — irreversible in effect, 34 commits of history and every planning artifact become
  world-readable; (6) a Marketplace listing — **DN-2: not performed**, blocked by (5) rather than by
  Story 11.3, which is `done`; (7) a PyPI/index publish — **DN-1: out of scope**, permanently
  irreversible and a locked decision restated in four places.
  **Ordering is binding and is already delivered:** the tag-state guard
  (`TC-ArgusAgent-DOCS-001-55`/`-55b`) was widened to every registered release surface BEFORE any tag
  exists, so act (2)/(3) turns all four pins on three surfaces RED at once instead of converting two
  of them into published falsehoods invisibly.
  - id: DF-12-9-A
  - owner: **Engineering Lead** (the human who holds the credentials; `release.yml`'s own header
    records that a publish *"is an operator decision taken with credentials in hand — not a decision a
    story author may take unilaterally"*)
  - target_story: **NONE — unscheduled; Engineering Lead to authorise act-by-act.** Deliberately not
    asserted onto a story id (AI-E9-8): these are operator acts, not development work, and inventing a
    story for them would move an authorisation decision into a backlog. The Epic-12 retrospective is
    the next scheduled moment a human reads this file.
  - category: governance
  - severity: 🟡

### Re-stated, NOT re-filed — cited by this story and still open

- **`DF-3-4-A`** (resume has no CLI entrance). Cited, untouched. 12.7 recorded *"stays open and is NOT
  re-filed"*, 12.8 cited it again, and this story does the same: building a `--resume` entrance would
  be an unscheduled capability addition inside the story that publishes.
- **`DF-10-5-C`** (FR29 evidence export needs a CLI surface, `target_story: NONE — unscheduled;
  Governance Owner to schedule`). Cited, untouched. An `argus evidence-bundle` sub-command is a
  capability addition, and this story adds none.
- **`DF-12-7-A`** (the assistant-host registry ships one verified member). Cited, untouched, still
  unscheduled. Registering further hosts is 12.7 / DN-2's decision and is not reopened here.
- **`DF-10-3-B`** (built-in secret suppressions are not disclosed) and **`DF-10-3-C`**
  (`--ignore-pattern` matches by bare substring). Both cited, both untouched, both still
  `target_story: NONE — unscheduled`. `DF-10-3-B`'s own text names *"the Epic-12 report-quality
  surface"* as a candidate home and deliberately declines to assert a story id; this story does not
  assert one for it either, and does not absorb it merely because it happened to be reading the same
  region of this file while closing `DF-10-3-A`.
- **`DF-10-4-D`** (the dogfood artifact-currency bootstrap). Cited because Story 12.9 had to decide
  whether it applied: it does **not** — `argus/**` is **byte-unchanged** by this story (DN-7, verified
  by `git diff --stat -- argus`), so no regeneration is owed and none was performed.

---

## Ledger follow-up under `DF-12-9-A` — the gate ran, and the citation was RE-DERIVED (2026-08-16)

**Append-only, as always (§3.4 evidence immutability).** Nothing above this line was edited: the diff
for this follow-up against `deferred-work.md` is `+n / -0`, verified programmatically
(`git diff --numstat -- _bmad-output/design-artifacts/ArgusAgent/deferred-work.md`).

**This is NOT a re-opening of Story 12.9, which stays `done`.** It is the outcome of the entry above
becoming partly answerable: `DF-12-9-A` act (1) — `git push origin master` — was performed by the
operator, which is the one act that could turn the release status from `NOT ESTABLISHED` into a
citation. The recorded statement then stopped being accurate. It was an *understatement* rather than an
over-claim, which is the harmless direction, and it is corrected anyway: `architecture.md:610-627`
requires the status to be **derived from what was observed**, and a derivation whose input is stale is
not a derivation, whichever way it errs.

### What was verified, read-only, before anything was written

Every fact below was re-measured through `gh` / `git` rather than taken from the request that prompted
this work. No workflow was triggered or re-run; no tag, release, push or visibility change was made.

```
$ git rev-parse HEAD                                        -> cea92689b14f730ff529caeabd74c1f33f84821b
$ git rev-list --left-right --count origin/master...master  -> 0   0     (origin/master IS HEAD)
$ gh run list --workflow=audit-ci.yml --branch master
    31908861401  success  cea9268...  2026-08-15T21:13:58Z   (push, master)
    31895158449  failure  50eedbd...  2026-08-15T16:18:46Z
    31341363300  success  00c8d1b...  2026-08-09T23:13:27Z
$ gh run view 31908861401 --json workflowName,headSha,conclusion,jobs
    "ArgusAgent Repository Audit & Assurance CI"  (= .github/workflows/audit-ci.yml)
    headSha cea92689b14f730ff529caeabd74c1f33f84821b, conclusion success,
    3 matrix legs (3.10 / 3.11 / 3.12), every leg `success`
$ gh run view 31908861401 --job <each of the 3> --log
    every leg: "1539 passed, 4 skipped"
    every leg: SKIPPED [4] tests/test_installed_artifact.py:241: [E6] ... NOT EVALUATED
$ git tag -l                                                -> empty
$ gh release list                                           -> empty
$ gh repo view Inan15/Agent-Argus --json visibility,isPrivate,pushedAt
    -> PRIVATE / true / 2026-08-15T21:13:56Z
```

**So for the first time a successful gate run covers the commit being released** — and the run that
FAILED (31895158449, the POSIX-containment / shallow-clone defect fixed by `40cdb3c`) covers `50eedbd`,
a different tree, and is deliberately **not** named inside the citation: attaching a run to a tree it
does not cover is the defect this derivation exists to prevent, and it is no more permissible in the
pessimistic direction than in the flattering one.

### What was changed, and what deliberately was not

- **`scripts/release_notes.py`** — `RECORDED_GATE_OBSERVATION` now holds the 2026-08-16 observation.
  `derive_release_status` is **the same function**: no second derivation was written, and no surface
  types a run id, a sha or a status. The 2026-08-15 observation is **retained** as
  `SUPERSEDED_GATE_OBSERVATIONS[0]` rather than deleted (§3.4), and it is a live input — it is what
  drives the `NOT ESTABLISHED` branch in the guard, so that branch is still exercised by an
  observation that really happened.
- **`README.md` / `CHANGELOG.md`** — re-rendered. The superseded `NOT ESTABLISHED` paragraph is
  **struck, not deleted** on both, with a dated correction beside it. `CHANGELOG.md`'s honesty
  preamble carried a second stale absolute — *"there is no Actions run id and no release URL to
  cite"* — which conflated two workflows; it is struck and narrowed: `release.yml` is still
  never-executed and there is still no release URL, but `audit-ci.yml` has run. The `## Unreleased`
  section heading that ended *"and the status is NOT ESTABLISHED"* is restated in place (position
  unchanged, so `-16`'s order pin is untouched), because a heading is the one line a skimming reader
  takes and a correction in the body underneath does not reach them.
- **The GitHub Release note** — carries the new statement automatically; it renders the derivation and
  types nothing. Verified by rendering it (`python scripts/release_notes.py --tag v0.1.0`).
- **NOT changed:** `argus/**` is byte-unchanged (`git diff --stat -- argus` is empty), so
  `DF-10-4-D`'s dogfood bootstrap is not owed. No guard was loosened, skipped, xfailed or narrowed.
  No tag, release, push, visibility change or workflow dispatch was performed; `DF-12-9-A` acts
  (2)-(7) remain unperformed and that entry stays **OPEN** for them.

### The citation carries its SCOPE, and that is the substantive judgement here

A run id quoted without the sha it covers is a claim about an unknown **tree** — the half-truth Story
10.1 wrote the rule against, because it was the only one reachable while no run covered the release
commit. The moment one does, a second half-truth opens: **the run's green is read as covering guards
the run itself declined to evaluate.** On this repository that is not hypothetical. All three legs of
run 31908861401 reported `1539 passed, 4 skipped`, and the four skips are
`tests/test_installed_artifact.py::TC-ArgusAgent-RELEASE-001-25`..`-28` — AC1's fresh-environment
installed-artifact proof, which is **the front-door claim of this release** and the very claim
`CHANGELOG.md` names a guard for. It did not execute on any leg, because `audit-ci.yml` provisions the
job with `pip` on a bare ubuntu runner and `uv` is never installed there.

Citing that run without saying so would have implied the installed-artifact proof was exercised by the
gate. It was not. So the derivation renders the scope **inside the statement**, reaching every surface
at once: the guards the run recorded as `NOT EVALUATED`, the reason it gave, and the fact that the
proof is therefore held by LOCAL runs only. The scope is derived from an observed field
(`GateObservation.unexercised`), not appended as boilerplate — `TC-ArgusAgent-DOCS-001-25` drives both
directions, so a run that really did evaluate everything publishes no caveat, and a run that did not
cannot suppress one.

### Filed by this follow-up

- **`DF-12-9-B`** — **the installed-artifact guard is VACUOUS on every CI run, and its own
  anti-vacuity assertion cannot fire.** Two halves, one entry, because they are one hole:
  1. **The environment half.** `.github/workflows/audit-ci.yml` never installs `uv`, and
     `tests/test_installed_artifact.py::unevaluable_install_tooling` correctly reports
     `release_preflight.Unevaluable("E6", ...)` when `uv` is absent — so `_artifact()` calls
     `pytest.skip` and **all four** guards (`TC-ArgusAgent-RELEASE-001-25`..`-28`) skip on all three
     legs of every run. Measured, not inferred: run 31908861401's logs, all three jobs. The guard
     behaves exactly as designed — it refuses rather than passing silently, which is AR10 / NFR-R1
     working — but the effect is that the release's front-door claim is enforced **only** on a
     developer machine that happens to carry `uv`.
  2. **The unreachable-assertion half.** `-28` closes with *"the installed-artifact guard is skipping
     in the dev environment; a permanently skipped guard is a guard nobody runs"* — the assertion
     whose whole job is to stop the skip becoming the normal path. It sits **after**
     `artifact = _artifact()`, which is the call that skips. So in precisely the environment where the
     skip HAS become the normal path, the line that would say so is never reached. This is the same
     shape `tests/test_built_distribution.py::-24` was written to prevent for the *build* tooling —
     and that one worked: it went red in CI, and `40cdb3c`'s answer was to add `build` + `flit_core`
     to the `[dev]` extra rather than to loosen the guard. The install half has the assertion but not
     the reachability.
  **NOT FIXED HERE, and the boundary is deliberate.** Putting `uv` on the CI runner is a CI-tooling
  decision for a human — it adds a second package manager to a `pip`-provisioned job — and re-ordering
  `-28` so its anti-vacuity half runs before the skip is a change to a shipped guard that belongs with
  that decision rather than ahead of it. Recorded rather than papered over: **the release-status
  citation now states this limitation in its own text**, on every surface, so a reader of the citation
  cannot conclude the installed-artifact proof ran.
  - id: DF-12-9-B
  - origin_story: ledger follow-up under `DF-12-9-A` (2026-08-16); the defect was MEASURED by this
    follow-up and is NOT caused by it
  - owner: **Engineering Lead** (the same human who holds `DF-12-9-A` — this is a CI-provisioning
    decision, and the two are read together)
  - target_story: **NONE — unscheduled; Engineering Lead to decide whether `uv` is provisioned on the
    `audit-ci.yml` runner.** Deliberately not asserted onto a story id (AI-E9-8): a named human is
    recorded instead of a backlog slot, because the first half is a provisioning choice rather than
    development work. The second half becomes a small, obvious change the moment the first is decided.
  - category: assurance (a committed guard that cannot execute where it matters)
  - severity: 🟡 — it fails SAFE (the guard refuses and names its reason; it never passes silently),
    and the claim it holds is separately true by LOCAL execution. It is not 🔴 because nothing false
    is published: the citation now states the limitation in the same breath as the run id.
  - cross-reference: `DF-12-9-A` (the operator acts; act (1) is now performed, (2)-(7) are not),
    `DF-10-4-D` (not owed — `argus/**` is byte-unchanged)

### Re-stated, NOT re-filed

- **`DF-12-9-A`** stays **OPEN**. Act (1) `git push origin master` is **performed** (2026-08-15
  21:13:56Z; `origin/master` = `cea9268`) and is recorded here rather than by editing the entry above.
  Acts (2) `git tag v0.1.0`, (3) `git push origin v0.1.0`, (4) the GitHub Release, (5) making the
  repository public, (6) the Marketplace listing (**DN-2**) and (7) a PyPI publish (**DN-1**) are all
  **still unperformed**, re-verified by execution: `git tag -l` empty, `gh release list` empty,
  `gh repo view` reports `PRIVATE`. The entry's binding ordering statement is unaffected —
  `TC-ArgusAgent-DOCS-001-55` / `-55b` was widened before any tag exists, and still is.
- **`DF-3-4-A`**, **`DF-10-5-C`**, **`DF-12-7-A`**, **`DF-10-3-B`**, **`DF-10-3-C`** — cited by Story
  12.9 and untouched here. This follow-up adds no capability and closes none of them; a gap filed
  twice is a gap that gets closed once and left looking open (12.7's rule).

---

## Story 13.1 closure + progress notes — 2026-08-16

Story 13.1 (*Decide what the validation set is, then build it*) — the corpus DECISION and the
manifest that makes Story 13.2's adjudication possible. Append-only per §3.4: nothing above is
rewritten, and every entry below states what was MEASURED rather than what was assumed.

### Closed by this story

- **`DF-8-5-C` — CLOSED 2026-08-16 against evidence.** The generator no longer passes a literal
  corpus figure. `argus/dogfood/proof_run.py` now calls the new `derive_gate_status()`, which
  reads both corpora through `argus.precision.replay_harness.measure_validation_corpus()` and
  renders the result; `minions-dogfood-proof.md` was regenerated through its own renderer
  (`scripts/regenerate_dogfood_artifacts.py` at `59a2ad4`), never hand-edited.
  - **Guarded:** `TC-ArgusAgent-DOGFOOD-001-53` (the measurement equals an independent fold over
    both tables), `-54` (the committed artifact carries the LIVE derivation, verbatim), `-55`
    (the literals cannot return: an `ast` read of the call site, plus the harness now RAISING on
    `precision=None, provisional=False`). **RED-first discharged at the real seam** — reverting
    the call site to `precision=Fraction(0, 1), n=0` turns `-54` and `-55` RED; restoring turns
    them green.
  - **⚠️ NOT closed the way the entry proposed, and the divergence is deliberate.** This entry's
    close condition said *"pass the measured `distinct_rule_class_count()` /
    `populated_planted_defect_count()`"* — i.e. publish `n=7`. That was written before Story 13.1
    took the DN-1 decision, and following it literally would have published *"N=7 … floor N=5"*,
    which reads as **floor MET** for a gate the cartridges do not gate at all. That is a worse
    published statement than the one it replaced, and in the **over-claiming** direction rather
    than the understating one. Under DN-1 the gate's `N` is the **repository** corpus, measured
    at **0**, and the cartridge substrate (7 populated rows / 5 distinct rule classes, measured
    live) is reported beside it with its role named. **The published number is the same `0` it
    always was; what changed is that it is now a measurement of a named population instead of a
    literal.** The `precision` argument became `None` — *"NOT COMPUTED BY THIS RUN"* — because
    that is the truth: this generator audits a repository and never invokes the replay harness.
    `precision=0/1` was the stronger, false claim that it had been measured and found to be zero.
  - **The direction of the original error is preserved as the entry recorded it:** the literal
    `n=0` UNDERSTATED the cartridge corpus, so nothing published was ever an over-claim and no
    gate was ever made to look cleared. It is nonetheless a hand-written number in a proof
    artifact *about the very gate this epic measures*, and it survived five epics inside the
    generator that exists to prevent exactly that.
  - **Tracker citation corrected while closing (AI-E12-3 / AI-E12-6).** Three documents cited
    this one defect at three different lines: `epics.md` and the tree agree on
    `proof_run.py:643-644`; `sprint-status.yaml` said `:764-765`, which **does not exist** — the
    file was 611 lines. The `:764-765` figure appears in this ledger at `:944` and `:1619` too.
    Those lines are NOT rewritten (§3.4); the correct citation is recorded here instead.

### Progress notes — NOT closed, and the target they adjudicate has moved

- **`DF-6-6-A` / `-P1` / `-P2` / `DF-7-2-A` — all four stay OPEN and are NOT rewritten.** They
  are the HUMAN half (the Eng-Lead + QA-Lead TP/FP adjudication), owned by **XAgent007**, and
  Story 13.1 is autonomous by design — a story that adjudicates its own corpus has proven
  nothing. This note records **which corpus each now adjudicates**, because Story 8.5 already
  moved that target once without telling them (`deferred-work.md:813-839`) and this story moves
  it again — this time deliberately, and this time recorded.
  - **The target is now the REPOSITORY corpus**, `tests/corpus/_manifest.py::VALIDATION_CORPUS`,
    per Story 13.1 / DN-1: the PRD governs, so the ≥80% gate is measured over real repositories
    and `precision-validation-protocol.md` §5's cartridge floor is struck.
  - **What that means for each:** the adjudication these entries describe is no longer performed
    over cartridge findings at all. `DF-6-6-A`'s "grow the corpus to N=5 distinct classes" was
    **satisfied for the cartridges** (5 classes across 7 rows, measured) and that satisfaction
    **does not advance the gate** — it is now recorded as recall evidence (FR20). `DF-7-2-A`'s
    adjudication over the 7.2 dogfood findings is **unperformable as written**: that run *"can
    never be re-derived in this repository"*, which is why it is recorded in the manifest as
    `provenance: superseded`, `eligible_for_n: False`.
  - **What actually discharges them:** Story 13.2, adjudicating the findings from the members
    ratified under Story 13.1 / AC3b. **AC3b was NOT performed** (see below), so the population
    those entries will be adjudicated over does not yet exist. None of the four is closable
    until it does.

### Ruled on, as `AI-E9-8` requires (a named human, never `target_story: NONE` alone)

- **`DF-10-2-A` — RULED 2026-08-16. Decided as a CORPUS-ELIGIBILITY rule, not as a detector
  story** (Story 13.1 / DN-6). Four consecutive retrospectives named it critical-path
  (`AI-E10-4` → `AI-E11-7` → `AI-E12-9`) with `target_story: NONE`, and `AI-E11-7` said what was
  needed was *"a dated decision, not an implementation"*. This is that decision.
  - **The rule:** a validation-set member whose `primary_language` cannot support `audited_deep`
    grounding **cannot count toward N**. It is enforced where the row is CONSTRUCTED —
    `CorpusMemberSpec.__post_init__` raises — so it cannot be skipped at a call site, and it is
    guarded by `TC-ArgusAgent-PRECISION-001-26` / `-27` / `-30`.
  - **⚠️ MEASURED CORRECTION to this entry's own premise, recorded rather than inherited.** The
    entry states that C, C++, Ruby **and Rust** *"ground cleanly and extract zero definitions"*.
    Re-measured 2026-08-16 by executing `build_ast_index` over a probe file per language at the
    pinned grammar versions: **three of the four hold; Rust does not.** Rust extracts its
    `struct_item` and misses only functions, because the extractor's vocabulary entry is
    `fn_item` — **a node type `tree-sitter-rust` does not emit** (the emitted one is
    `function_item`), so that entry matches nothing. Per-language mechanisms, all measured:
    **C** (0 defs) and **C++** (0 defs) — `function_definition` IS in the vocabulary, but a C/C++
    function carries its name under a `declarator` field while `_node_name` reads `name` only, so
    every definition is matched and then dropped for having no name; C++ classes are
    `class_specifier`, absent from the vocabulary. **Ruby** (0 defs) — a pure vocabulary gap: its
    nodes are `method` and `class`, the extractor knows `method_definition` / `class_definition`.
  - **Rust stays ineligible**, on the narrower and correct ground: a member whose FUNCTIONS can
    never be grounded cannot support the `audited_deep` claims the gate is about, and admitting
    it on the strength of struct extraction alone is the over-claim OI1 forbids.
  - **The underlying detector gap is NOT fixed here and is NOT claimed to be.** Fixing it means
    editing `_DEF_KIND_BY_NODE` and `_node_name` in `argus/index/ast_index.py`, which no Story
    13.1 AC owns, and which would change grounding results across four languages — a behaviour
    change that belongs to a story that says so. `AST_INELIGIBILITY_REASONS` records the measured
    mechanism per language so the eventual fix has a starting point rather than a slogan.
  - **The eligibility rule is self-retiring:** `TC-ArgusAgent-PRECISION-001-30` re-measures the
    zero-extraction set on every run and FAILS if it moves, in both directions — so a language
    that starts extracting definitions cannot stay banned by inertia, and a language that stops
    cannot silently become eligible.
  - id: DF-10-2-A
  - owner: **Engineering Lead (XAgent007)** — unchanged; the ruling is recorded, not re-homed
  - target_story: **13-1-decide-what-validation-set-is-then-build-it** for the CORPUS-ELIGIBILITY
    half (ruled here, dated, guarded). The **detector half** — making C / C++ / Ruby / Rust
    extract definitions — remains **unscheduled with a named owner (XAgent007)**, deliberately
    not asserted onto a story id (`AI-E9-8`), because it is a multi-language grounding change
    rather than corpus work.
  - status: **corpus half CLOSED; detector half OPEN, owned, unscheduled**

### Filed by this story

- **`DF-13-1-A`** — **the validation-set manifest is SPECIFIED and EMPTY; populating it is an
  operator act that has not been performed.** Story 13.1 / AC3b requires N ≥ 5 independent
  repositories staged at pinned shas and audited through the unmodified
  `pipeline.run_audit_detailed`. It was **not performed**, and the story's own ESCALATION
  designates that a legitimate terminal state (the Story 12.9 / AC9 precedent) for two reasons
  that are both operator judgements rather than development work: **(1) which repositories** —
  licence, provenance and independence are calls with an accountable owner, and the manifest is
  a *proposal* until ratified; **(2) fetching** — cloning external code is a network act against
  third-party hosts, performed on the operator's machine.
  **Deliberately NOT worked around.** Populating the manifest with plausible repository names to
  make a count look met would be a fabricated corpus in the story that defines the corpus — the
  worst available outcome — so the manifest holds **zero** eligible members and says so
  everywhere it is reported.
  - id: DF-13-1-A
  - origin_story: 13-1-decide-what-validation-set-is-then-build-it
  - owner: **Engineering Lead (XAgent007)** — the same named human the protocol §2 designates as
    primary adjudicator and whom `sprint-status.yaml:414`/`:416` already name
  - target_story: **13-1 AC3b on ratification** — the specification, the guards and the derived
    floor are all delivered and committed; what is outstanding is the single ratification act
    plus the staging it authorises. It is NOT re-homed to 13.2, because 13.2 adjudicates a
    populated corpus and cannot begin without one.
  - category: corpus (a specified population awaiting an operator act)
  - severity: 🟠 — it is the **critical path** to clearing the externalization gate, and Epic 13
    is the only work in the plan that can remove the tool's provisional status. It is not 🔴
    because nothing false is published: the gate is reported PROVISIONAL on every surface, the
    manifest reports `N = 0` derived rather than asserted, and no over-claim exists anywhere.

### Re-stated, NOT re-filed

- **`AI-E10-8`** (*"`argus/pipeline.py` is 1331 lines against NFR-M1"*) — **ALREADY FIXED; the
  action item was never told.** Re-measured 2026-08-16: **1111** lines, under the 1200 ceiling.
  Story 12.1 closed it. **Not re-fixed here**, and recorded so the next story does not spend a
  cycle on it. *Second-order note:* `sprint-status.yaml`'s create-story entry for this story
  records the same file as **1005** lines. Neither figure is a typo — **1005 is what
  `Get-Content | Measure-Object -Line` returns**, because that idiom scores an empty line as
  zero lines and this file has 106 blank ones. The true physical count is **1111**
  (`len(text.splitlines())`, which is what `tests/test_module_size_ceiling.py` uses). Both are
  under the ceiling, so the conclusion is unaffected — but a 10% silent undercount is a real
  hazard for a project whose maintainability standard is a line ceiling, and it is recorded here
  rather than left to surprise the next person who measures on Windows.
- **`AI-E12-1`** (*"register `epic-12-retro-2026-08-15.md` in `_STATUS_DOCUMENTS`"*) —
  **first half ALREADY DONE**, verified at `tests/test_evidence_citation.py:125`. Not
  re-registered. The second half (making registration part of the retrospective step's DoD)
  remains unverified and is not this story's.
- **`DF-12-9-A`** stays **OPEN and untouched.** Story 13.1 published **nothing**: re-verified by
  execution at hand-off — `git tag -l` empty, and no push was performed. No release, no tag, no
  visibility change.
- **`DF-9-2-A`** — honoured, not closed. Both `tests/cartridges/` and the new `tests/corpus/` are
  repository-only, and both are reached through the declared lazy edges
  (`registry_module()` / `corpus_manifest_module()`). `TC-ArgusAgent-PRECISION-001-29` asserts no
  `argus/**` module imports either at module level, which is the seam
  `tests/test_built_distribution.py::-20` would otherwise catch only after a wheel was built.
---

## Story 13.1 code-review correction — 2026-08-16

Raised by code review iteration 1 (three adversarial layers, all three independently). Appended
per §3.4: nothing above is rewritten, including the entry this note corrects.

### Corrected by this note

- **`DF-13-1-A` — the entry above is FACTUALLY WRONG as of HEAD, and the correction is appended
  rather than applied in place.** It reads *"the validation-set manifest is SPECIFIED and EMPTY;
  populating it is an operator act that has not been performed … the manifest holds **zero**
  eligible members and says so everywhere it is reported."* **That was true when it was filed and
  false four commits later, in the same story.** Measured at HEAD: `eligible_member_count()`
  returns **5** and `meets_validation_floor()` returns **True**.
  - **What actually happened.** The entry was written while AC3b was still escalated. The operator
    (XAgent007) then **ratified five members** — `ai-body-runtime`, `agent-markovich`, `minions`,
    `xagents-webapp`, `agent-smith` — each measured before admission and audited through the
    unmodified `run_audit_detailed` (commit `1518cf2`, then `1d044af`). All five are
    **byte-reproducible across two runs**. **31 blocking findings** (24 `minions` + 7
    `agent-smith`, every one `vacuous_test_ast`) are emitted adjudication-ready, nothing
    pre-adjudicated.
  - **`DF-13-1-A` is therefore CLOSED**, not merely corrected: the act it was filed to track —
    the operator ratification and the corpus build — was performed. What remains is Story 13.2's
    human adjudication, which is `DF-7-2-A` / `DF-6-6-A`'s territory and was never this entry's.
  - **The defect class, named plainly, because it is this project's dominant one.** A
    hand-written figure went stale inside the story that closed `DF-8-5-C` — a defect defined as
    *a hand-written figure diverging from measured reality*. The **derived** surfaces
    (`minions-dogfood-proof.md`, the manifest, the gate status) all tracked the change correctly
    and needed no edit; only the prose rotted. That is the story's own thesis demonstrating
    itself in both directions at once.
  - **Worst detail, and the reason this is filed rather than quietly fixed:**
    `tests/test_validation_set_decision.py` **required** the literal string `N = 0 eligible
    members` to appear in `prd.md`. A guard written to protect the record was enforcing the
    falsehood and holding the suite green over it. `TC-ArgusAgent-DOCS-001-75` now **derives**
    the count from the manifest and fails if any document disagrees with the live corpus — so
    ratifying a sixth member turns it red until the documents are updated.
  - **Corrected in the same change, all struck-not-erased:** `prd.md` (§Measurable Outcomes and
    the open-inputs table), `precision-validation-protocol.md` §5 + a **V1.2** change-log row,
    `architecture.md` at **all three** resolution sites (identically — `-73` counts them), and
    four stale docstrings in `tests/corpus/_manifest.py`, `argus/dogfood/proof_run.py` and
    `tests/test_validation_corpus.py`.
  - id: DF-13-1-A
  - status: **CLOSED 2026-08-16** — ratified, populated, audited. Superseding the "OPEN, owned"
    state recorded above.
  - owner: Engineering Lead (XAgent007) — unchanged
  - cross-reference: `DF-7-2-A` / `DF-6-6-A` / `-P1` / `-P2` (the human adjudication, still OPEN
    and now with a real population to adjudicate); `DF-8-5-C` (closed earlier in this story — the
    defect class this correction is an instance of)

### Also corrected by this review, in code rather than prose

- **`argus/precision/replay_harness.py::measure_validation_corpus` conflated two substrates.**
  `validation_floor_n()` routes through `registry_module()`, so a **cartridge-registry** failure
  was caught by the **manifest's** handler: the result reported `validation_set_available=False`
  and blamed the manifest while `validation_set_n` still carried the real measured count, and
  `corpus_note()` rendered *"the repository corpus manifest was NOT CONSULTED by this run"*
  beside a number that had been consulted. **A published figure contradicting its own provenance
  note is `DF-8-5-C` reproduced inside the fix for `DF-8-5-C`.** Split into three independent
  `try` blocks, and the floor is now read from the registry directly (DN-3's single source),
  which removes the coupling entirely. **Not filed as a new ledger id** because it is closed in
  the same change that found it.
- **The same handler caught `Exception`, not `ImportError`.** A malformed manifest row raises
  `ValueError` from `CorpusMemberSpec.__post_init__` at import time; that was being reported as
  ordinary "not consulted" absence, silently converting a data-integrity defect into a benign
  note in a proof artifact. Only `ImportError` now means absent; everything else propagates.
- **`scripts/audit_validation_corpus.py` rendered a WITHHELD member as a CLEAN one.** Findings
  from a non-byte-reproducible member are withheld (correct, protocol §4) — but the worklist then
  folded an empty list and wrote *"0 blocking / Nothing to adjudicate"*, byte-identical to a
  genuinely clean member, **and persisted it before the exit-2 fired**. A human reading the
  artifact rather than the process exit code was told a member was clean when its findings had
  been suppressed. Now renders an explicit `⛔ FINDINGS WITHHELD` block naming the first-run
  counts and stating it is *not* a clean member.

> **Note on this file''s diff numstat, recorded rather than glossed (2026-08-16).** `git diff
> --numstat` reports **-1** for this append. **No ledger content was erased** — verified by
> `git diff --word-diff`, which shows additions only, and the affected line
> (*"…`tests/test_built_distribution.py::-20` would otherwise catch only after a wheel was
> built."*) is present and byte-identical. The `-1` is the **newline-at-end-of-file marker**:
> Story 13.1''s first append left the file without a trailing newline, so the next append
> necessarily touched that last line. A trailing newline has now been added so subsequent
> appends are clean `+n / -0`. Recorded because AC6 states a mechanical `+n / -0` rule, and
> quietly reporting a number that does not match what `git` prints is the exact habit this
> ledger exists to prevent.

---

## Story 13.2 dispositions — 2026-08-16

Story 13.2 (*Adjudicate every finding, by a named human*) — the **instrument** half. Appended per
§3.4: nothing above is rewritten, and every ruling below states what was **measured by execution**
rather than what a prior story record claimed. That distinction is this section's subject twice
over: it is what `AI-E12-3` asked for, and it is what `AI-E12-6`'s new guard now enforces.

### The four human-adjudication entries — RE-SCOPED, with the instrument delivered and the judgement NOT taken

- **`DF-6-6-A`, `DF-6-6-A-P1`, `DF-6-6-A-P2`, `DF-7-2-A` — all four stay OPEN, owned, and their
  remaining scope is re-recorded here with a reason.** None is closed, and none is left pointing
  at a run that has now happened. AC8.1 of Story 13.2 required exactly this choice, and closure is
  not available: the act these four describe **has not been performed**.
  - **What Story 13.2 DID deliver, and it is not the judgement.** The whole instrument: a
    committed, append-only, machine-readable adjudication record
    (`validation-corpus/adjudication-record.json`, **31 rows**, one per emitted blocking finding
    from the five members Story 13.1 / AC3b ratified); a closed disposition vocabulary that
    **raises** on an unregistered member; adjudicator attribution asserted against protocol §2 at
    **construction**; append-only supersession (§3.4 — strike, never erase); an exhaustiveness
    proof with a non-vacuity floor; the reuse of 13.1's **existing** byte-reproducibility result
    as §4's determinism precondition; expert-hours as a `Fraction` field reported against §3's
    ceiling; and the fold from human dispositions into the **shared** precision arithmetic.
  - **What was NOT delivered, deliberately: a single disposition.** All 31 rows are
    `UNADJUDICATED` and carry **no adjudicator**. The fold over the committed record returns
    `Unevaluable`, **recorded with residual 31**. No agent may adjudicate — protocol §2 assigns it
    to the **Engineering Lead**, and `sprint-status.yaml:414`/`:416` name **XAgent007**. *An
    autonomous story that tags its own findings TP has measured nothing and has produced the exact
    artifact Epic 13 exists to make impossible.* This is enforced, not promised:
    `AdjudicationRow.__post_init__` **raises** if an `UNADJUDICATED` row carries an adjudicator id,
    so a machine signing the named human's name is a construction-time failure.
  - **The remaining scope, stated so no reader has to infer it.** For all four entries what
    remains is **one act**: XAgent007 adjudicates each of the 31 blocking findings TP/FP at its
    cited locator under protocol §4 as amended, records the actual expert-hours, and appends the
    rows. `blocking-worklist.md` is the human-readable list; the record is the machine one. After
    that, Story 13.3 computes the four §5 conditions. Nothing else is outstanding on the
    instrument side.
  - **`DF-7-2-A`'s original text remains unperformable as written and is NOT re-fixed here** —
    Story 13.1 already recorded why (the Story 7.2 dogfood run *"can never be re-derived in this
    repository"*, hence `provenance: superseded`, `eligible_for_n: False`). Its adjudication target
    is the repository corpus, as 13.1 recorded and this story mechanised.
  - id: DF-6-6-A / DF-6-6-A-P1 / DF-6-6-A-P2 / DF-7-2-A
  - owner: **Engineering Lead (XAgent007)** — unchanged, and now with a delivered instrument and a
    populated 31-row worklist in front of it
  - target_story: **13-2-adjudicate-every-finding-by-a-named-human**, whose AC7 is recorded
    **HALTED — awaiting the named adjudicator** (the Story 12.9 / AC9 precedent, where a halt is
    the *designed* terminal state). NOT re-homed to 13.3: 13.3 computes over an adjudicated record
    and cannot begin without one.
  - status: **OPEN, owned, instrument-complete, judgement outstanding**

### `AI-E12-3` — the four falsely-closed entries, VERIFIED BY EXECUTION and disposed

The Epic-12 retrospective ranked this #4 and required *"verification by execution and then either a
closure entry or a re-record with a reason."* All four were re-measured against the tree at
`1816524`. **Two are genuinely delivered and are closed here against that evidence; one is
delivered on a different surface than its entry proposed and is closed with the divergence stated;
one is NOT delivered and its story record was wrong.**

- **`DF-8-3-A` — CLOSED 2026-08-16 against evidence.** The entry asked that the FR16
  critical-subsystem heuristic exclusion be named to an operator in prose. **Measured:**
  `CriticalSubsystemSet.heuristic_excluded_ineligible` is read back and rendered in **both** human
  surfaces — `argus/reports/generator.py:331-332` and `argus/reports/plain_english.py:706-707`.
  Story 12.4's record claimed this and the claim is **true in code**; what was missing was the
  ledger entry, which is precisely the `AI-E12-6` class. Closed by the evidence, not by the claim.
  - id: DF-8-3-A · owner: Engineering Lead (XAgent007) · status: **CLOSED 2026-08-16**
- **`DF-10-4-A` — CLOSED 2026-08-16 against evidence, with the divergence stated.** The entry
  described the readability callout as **all-or-nothing**, so a polyglot repository learns nothing
  about its failed Go grammar. **Measured:** the all-or-nothing trigger in `_grammar_diagnosis` is
  **unchanged** — `argus/reports/generator.py:436-439` still documents it and still returns early
  when any language is eligible. What Story 12.5 delivered instead is a **separate
  point-of-downgrade surface**: `render_grammar_downgrade_summary`, wired into `argus/cli.py:268`
  and `:931` and `argus/reports/generator.py:25`, which reports per-failure-class reasons on a
  **default** run regardless of the trigger. The operator-facing gap the entry was filed about is
  therefore closed; **the mechanism named in the entry is not the mechanism that closed it**, and
  that is recorded rather than glossed, because a closure justified by the wrong surface is how an
  entry gets re-opened by the next person who reads the original code.
  - id: DF-10-4-A · owner: Engineering Lead (XAgent007) · status: **CLOSED 2026-08-16**
- **`DF-10-4-B` — NOT DELIVERED. Re-recorded OPEN with a named owner, and TWO story records that
  claim otherwise are corrected here.** The entry asks for a **production reader** of
  `DetectorResult.degraded` in the terminal / next-action output. **Measured tree-wide at
  `1816524`: there is none.** `argus/reports/generator.py:420-422` says so **in its own
  docstring** — *"`DetectorResult.degraded` records it and no production code reads it back —
  filed as `DF-10-4-B`"* — and every other occurrence of the attribute is a **write** in
  `argus/detectors/*` or an unrelated `deep_pass` degradation counter.
  **`12-4-every-outcome-names-its-next-action.md` records it as an integrated, checked-off task
  (`:126`, `:152`) and `10-5-a-v1-commitment-is-delivered-or-explicitly-not-v1.md` records a
  closure. Both are FALSE against the tree.** This is the single clearest instance of the class
  `AI-E12-6` exists to close, and the new guard
  (`tests/test_governance_record_integrity.py::TC-ArgusAgent-DOCS-001-78`) found it independently.
  **Not fixed here:** adding a reader changes operator-facing report content, which no Story 13.2
  AC owns, and doing it inside the precision-gate story would be exactly the unscoped drift this
  ledger exists to catch.
  - id: DF-10-4-B · owner: **Engineering Lead (XAgent007)** · target_story: **NONE — unscheduled
    with a named owner** (`AI-E9-8`: never `NONE` *alone*; the owner is named) · category: reports
    · severity: 🟡 — nothing false is published to an operator; a recorded condition is simply
    never surfaced · status: **OPEN, owned, unscheduled; story records corrected**
- **`DF-12-3-A` — the DISCLOSURE half is CLOSED 2026-08-16; the MECHANISM half is re-recorded
  OPEN.** The entry has two halves and they were being conflated. **Disclosure — measured
  delivered:** `argus/reports/plain_english.py:249` and `:257` carry the exact sentence *"results
  are recomputed per run and not served from the offline stage memo store"*, which is what Story
  12.4's task claimed and it is true. **Mechanism — measured NOT delivered:** PRD §501's *"a re-run
  returns the recorded result"* still does not hold with `--deep-audit`; the deep pass is
  recomputed. So the story record's claim is **half true**, and a single CLOSED line would have
  published the wrong half.
  - id: DF-12-3-A · owner: **Engineering Lead (XAgent007)** · target_story: **NONE — unscheduled
    with a named owner** for the mechanism half · status: **disclosure half CLOSED 2026-08-16;
    mechanism half OPEN, owned, unscheduled**

### `AI-E12-6` — LANDED, and it found nineteen instances on its first run

- **The ledger-claim cross-check guard exists.** `tests/test_governance_record_integrity.py`
  (`TC-ArgusAgent-DOCS-001-78`) extracts every `DF-*` a committed story file claims to CLOSE and
  fails unless `deferred-work.md` carries a matching disposition. Non-vacuous by construction: it
  asserts `> 0` ledger closures and `> 0` extracted claims **before** asserting anything about
  them, and it drives its own analyzers over synthetic input as a positive control.
  **Measured on landing: 47 closure claims across the story corpus, of which 19 are unbacked** —
  including `DF-10-4-A` (Story 12.5) and `DF-8-3-A` (Story 8.3), i.e. the guard reproduced
  `AI-E12-3`'s finding from scratch. The 19 are registered **by name, with this date and this
  owner**, in `_UNBACKED_AT_LANDING`, following Story 12.1's `_EXEMPT_BY_DESIGN` precedent for a
  correct rule landing over a repository that predates it. **The registry can only shrink** — an
  entry that becomes backed **fails** — and any *new* unbacked claim fails immediately, which
  covers Story 13.2 and everything after it.
  - **Why it was not made green by closing the nineteen.** That would be `AI-E12-3`'s own defect —
    closing entries in prose rather than against evidence — committed inside the guard written to
    stop it. This story has evidence for four of them and ruled on those four above.
  - id: AI-E12-6 · owner: Engineering Lead (XAgent007) · status: **guard LANDED 2026-08-16;
    19-entry backlog registered, dated and owned**

### `AI-E12-5` — the guard-adequacy clause is REGISTERED; `AI-E11-8`'s two rules are RE-HOMED

- **The GUARD-ADEQUACY CLAUSE is now in `architecture.md` §Enforcement**, in the established form
  (rule text + enforcing module + test ids), asserted present by `TC-ArgusAgent-DOCS-001-77`,
  together with the input-side twin the Epic-12 retrospective §3.5 found (*a guard over the SHAPE
  of an input is not a guard over its EFFECT*). **Fourth consecutive retrospective to ask; first
  registration.** Registered by Story 13.2 rather than by the Architect it was assigned to, for the
  reason `AI-E12-5` states itself: Story 13.3 needs it on the most consequential guard in the
  project, and 13.2 is the story that builds that guard.
  - id: AI-E12-5 · owner: Architect / Engineering Lead (XAgent007) · status: **CLOSED 2026-08-16
    for the guard-adequacy clause**
- **`AI-E11-8` — the two Epic-11 rules are NOT registered here, and are re-homed with a named
  owner rather than left to a fifth retrospective.** (a) **workflow input containment** (Story
  11.3) and (b) **built-artifact inspection** (Story 11.5). Both are outside Story 13.2's write
  set — neither concerns the precision gate, and a story that edited §Enforcement for unrelated
  rules would be doing unscoped work in the story whose whole subject is a scoped, recorded act.
  Recorded here so the count is honest: **learned three times, registered zero.**
  - id: AI-E11-8 · owner: **Architect, escalating to Engineering Lead (XAgent007)** ·
    target_story: **NONE — unscheduled with a named owner** (`AI-E9-8`) · status: **OPEN, owned,
    re-homed**

### Filed by this story

- **`DF-13-2-A` — the adjudication instrument is complete and the adjudication has NOT happened.**
  The record holds 31 `UNADJUDICATED` rows; `AdjudicationRecord.exhaustiveness()` returns
  `Unevaluable` with residual 31; `expert_hours` is `null` (**NOT RECORDED**, never zero). The
  externalization gate is therefore **not** cleared and moved no closer to cleared: of protocol
  §5's four conditions exactly one holds (N = 5 ≥ 5, from Story 13.1), the ≥80% figure is
  **UNEVALUABLE**, the clean-repo blocking-FP condition is **NOT APPLICABLE** over the repository
  corpus with its reason recorded, and no adjudication run is recorded cleared.
  **Deliberately not worked around.** Populating dispositions to make the exhaustiveness guard go
  green would clear the externalization gate on evidence that does not exist, and every guard
  downstream — including Story 13.3's — would agree that it had.
  - id: DF-13-2-A
  - origin_story: 13-2-adjudicate-every-finding-by-a-named-human
  - owner: **Engineering Lead (XAgent007)** — protocol §2 primary adjudicator
  - target_story: **13-2 AC7 on adjudication** — the instrument, the guards and the 31-row
    worklist are delivered and committed; what is outstanding is the judgement itself
  - category: precision gate (a delivered instrument awaiting a human act)
  - severity: 🟠 — the critical path to clearing the externalization gate. Not 🔴 because nothing
    false is published: every surface reports the gate PROVISIONAL or UNEVALUABLE, and
    `protocol_cleared` has still never been `True` anywhere in the tree.

### Re-stated, NOT re-filed

- **`DF-12-9-A` stays OPEN and untouched.** Story 13.2 published **nothing**: re-verified by
  execution at hand-off — `git tag -l` empty, `origin/master` unmoved, no push, no release, no
  visibility change.
- **`DF-9-2-A`** — honoured, not closed. `argus/precision/adjudication.py` resolves **no**
  repository-only path at module level; the repository corpus is reached through the existing lazy
  `corpus_manifest_module()` edge, and the record path is a repository-relative **string** the
  caller resolves. A module-level import of `tests/` or `_bmad-output/` would ship a wheel that
  cannot import, which `tests/test_built_distribution.py` exists to catch.
- **`DF-8-5-B` / `DF-10-4-D` bootstrap** — applied, because `argus/**` moved: the `argus/` delta
  was committed first, the three dogfood artifacts were regenerated through their own renderers,
  and the regeneration was committed separately (`AI-E12-11`).
