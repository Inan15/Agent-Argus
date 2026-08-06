"""Import-isolation gate for ArgusAgent store modules (AC7 / AR7 / AR9).

Verification area ArgusAgent-STORE (TC-ArgusAgent-STORE-001-50). ArgusAgent is downstream of the
HTTP/A2A boundary: its modules must NOT transitively import the web stack
(``fastapi`` / ``uvicorn`` / ``starlette``). This durable, committed gate is
seeded here (story 1.1) and extended by later stories as new ArgusAgent modules land.

Each import runs in a CLEAN subprocess (fresh ``sys.modules``) so a web import
pulled in by an unrelated test earlier in the session cannot mask a real leak.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap

_FORBIDDEN = ("fastapi", "uvicorn", "starlette")

# Modules added by story 1.1. Later stories APPEND to this tuple.
_MODULES_UNDER_GUARD = (
    "argus.store.canonical",
    "argus.store.envelope",
    # Story 1.2 — coverage-ledger + recording models.
    "argus.ledger.coverage_ledger",
    "argus.ledger.recording",
    # Story 1.3 — impure .argus/ write/read shell (paths/writer/reader). These
    # transitively import argus.shared.workspace_containment, which
    # the architecture cross-cutting #7 verifies is pathlib-only / FastAPI-free.
    "argus.store.paths",
    "argus.store.writer",
    "argus.store.reader",
    # Story 4.2 — pure referential-integrity LINT over the on-disk .argus/ tree
    # (FR26/NFR-A2). PURE _resolve_references core + thin impure enumerate-and-read
    # shell over the 1.3 reader. Imports ONLY the done store leaves (canonical /
    # envelope / paths / reader); no web stack, no LLM/api module, no .argus/ writer.
    # Extend the guard (do NOT fork) per AI-E3-6.
    "argus.store.integrity",
    # Story 1.4 — impure repo-intake + tree-sitter Python AST-index layer. The
    # parsing toolchain (tree-sitter / tree-sitter-python / radon) is web-free;
    # importing these modules must not transitively pull the web stack.
    "argus.intake.repo_loader",
    "argus.intake.stack_detect",
    "argus.index.ast_index",
    # Story 2.4 — pure graph-derived partition planner + frozen Partition/
    # PartitionPlan/WorkManifest contract + the work-manifest permission-boundary
    # primitive (is_in_scope). Imports ONLY the 1.4 AstIndex model; pure planner —
    # no web stack, no LLM/api module, no impure .argus/ writer (the LOC read +
    # manifest write + scoped read are the impure shell).
    "argus.index.partitioner",
    # Story 1.5 — pure defect-detector scorers (heuristic vacuous-test + Tier-A
    # vacuous-path AST subset). Zero-token, web-free; import them must not pull
    # the web stack or any LLM/api module.
    "argus.detectors.base",
    "argus.detectors.vacuous_test",
    # Story 2.5 — pure regex+entropy hardcoded-secret detector with producer-side
    # redaction. Zero-token, web-free; importing it must not pull the web stack or
    # any LLM/api module. Reuses the 1.5 build_recording + 1.2 Recording/Locator +
    # 1.1 serializer (entropy as Fraction); the SecretFindingEvidence carries no
    # value field (the structural redaction guarantee).
    "argus.detectors.secret_scan",
    # Story 2.6 — zero-token breadth tool-runner (radon library API behind an
    # injected invoker seam) + pure outcome classifier. Zero-LLM-token, web-free;
    # importing it must not pull the web stack or any LLM/api/providers module. The
    # injected seam keeps it testable without spawning a subprocess; the runner
    # PRODUCES the tool_scanned_only grade (via 2.1 classify_depth) and tool-failure
    # / unestablishable-traceability findings (via 1.5 build_recording).
    "argus.detectors.tool_runner",
    # Story 1.6 — pure-function verdict gate (fold + finding ordering + exit-code
    # mapping). Imports ONLY the 1.2 ledger/finding models; the pure terminal fold
    # never touches the web stack, the impure .argus/ writer, or any LLM/api module.
    "argus.verdict.verdict_gate",
    # Story 2.1 — pure documented five-state depth-grading rule + content-derived
    # criticality assessment (the FR8 honesty surface). Imports ONLY the 1.2 ledger
    # enum (AST-index entry is a typing-only import); pure classifier — no web stack,
    # no LLM/api module, no impure .argus/ writer.
    "argus.ledger.depth_semantics",
    # Story 2.2 — pure FR9 readable per-file coverage-ledger surface (text +
    # canonical JSON render of the 1.2 ledger). Imports ONLY the 1.2 ledger models
    # + the 1.1 serializer; pure render — no web stack, no LLM/api module, no impure
    # .argus/ writer.
    "argus.ledger.coverage_report",
    # Story 2.3 — pure FR4/FR16 critical-subsystem identification (reuse 2.1
    # assess_criticality) + operator-designation merge + the critical_subsystems_all_deep
    # predicate. Imports ONLY the 2.1 depth_semantics + the 1.2 ledger models; pure —
    # no web stack, no LLM/api module, no impure .argus/ writer.
    "argus.ledger.critical_subsystems",
    # Story 3.1 — pure budget-ceiling config + deterministic cost-accounting core.
    # It reuses minions_core.cost.budget_guardrails BY IMPORT (AR7) for the
    # >=-is-a-breach hard-ceiling DECISION; that leaf is verified FastAPI-free, so
    # importing the cost module must NOT transitively pull the web stack or any
    # LLM/api/providers module. Extend the guard (do NOT fork) per AI-E2-5.
    "argus.cost.budget_governor",
    # Story 3.2 — pure budget-exhaustion halt → skip → downgrade → report mechanism.
    # The deterministic pre-dispatch halt PROJECTION + the frozen HaltReport. It
    # reuses the 3-1 budget_governor._coerce_breach >=-hard-ceiling DECISION BY
    # IMPORT (AR7, no fork) — that core is verified FastAPI-free, so importing this
    # module must NOT transitively pull the web stack or any LLM/api/providers
    # module. Extend the guard (do NOT fork) per AI-E2-5.
    "argus.cost.exhaustion",
    # Story 3.4 — pure resume-plan core (frozen ResumePlan + build_resume_plan). It
    # reuses the 3-2 project_halt_point + the 1.2 CoverageLedger + the 3-1 BudgetConfig
    # BY IMPORT (AR7, no fork) — all verified FastAPI-free, so importing this pure plan
    # builder must NOT transitively pull the web stack or any LLM/api/providers module.
    # The state READ (1-3 reader) + the resumed-artifact WRITE are the impure pipeline
    # shell, NOT this module. Extend the guard (do NOT fork) per AI-E2-5.
    "argus.cost.resume",
    # Story 4.1 — pure negative-assurance verdict WRAPPER over the done 1.6
    # AuditVerdict + 3.3 floor report + 2.3 CriticalSubsystemSet. Imports ONLY those
    # done pure leaves (verdict_gate / exhaustion / critical_subsystems / coverage_ledger);
    # the wrapper model + builder + render are pure — no web stack, no LLM/api module,
    # no impure .argus/ writer (the persistence WRITE is the impure pipeline shell).
    # Extend the guard (do NOT fork) per AI-E3-6.
    "argus.verdict.negative_assurance",
    # Story 4.3 — pure FR29 evidence-bundle export (frozen EvidenceBundle + PURE
    # build_evidence_bundle + canonical-payload render + the OPTIONAL impure persist
    # helper). Aggregates BY REFERENCE the done 4.1 wrapper + 2.2 coverage report +
    # 1.6 ordered findings + 4.2 integrity report through the single 1.1 serializer;
    # the no-source-retention moat is structural (no value field). Imports ONLY those
    # done ArgusAgent leaves (coverage_report / recording / canonical / integrity / writer /
    # negative_assurance) — no web stack, no LLM/api module, and crucially NOT
    # minions_core.governance.evidence (ArgusAgent's bundle is self-contained). Extend the
    # guard (do NOT fork) per AI-E3-6.
    "argus.evidence.bundle",
    # Story 5.1 — pure cache-key derivation over the full recording-producing
    # closure + the declared frozen detector-descriptor set (DN-DETECTORSET).
    # Composes the single 1.1 serializer (canonical.dumps_bytes) + the 1.1
    # content-hash (envelope.compute_content_hash) — no second hasher; PURE (no
    # FS/clock/uuid/random/float/LLM). Imports ONLY the done store leaves
    # (canonical / envelope); no web stack, no LLM/api/providers module, no
    # .argus/cache/ write (5.2 owns the cache tree). Extend the guard (do NOT
    # fork) per AI-E4-7.
    "argus.cache.key",
    # Story 5.2 — the IMPURE content-addressed memoization STORE over the fixed
    # .argus/cache/ tree. It is the IMPURE shell (FS I/O) — added to the
    # import-isolation coverage (FastAPI-free) but NOT to any purity-asserting guard
    # (mirroring how store/writer.py + store/reader.py are treated). It COMPOSES the
    # 1.1 serializer/content-hash + 1.3 ApaaStorePaths/writer/reader (+ its tamper
    # guard) + the 5.1 key; it imports ONLY done ArgusAgent leaves — no web stack, no
    # LLM/api/providers module. Extend the guard (do NOT fork) per AI-E4-7.
    "argus.cache.memo_store",
    # Story 5.3 — the IMPURE AR6 cache-invalidation surface + the V1 rejected-finding
    # SEAM (RejectedFinding record + RejectionLedger). It is the IMPURE shell (FS
    # DELETE + a redacted-record read) — added to the import-isolation coverage
    # (FastAPI-free) but NOT to any purity-asserting guard (mirroring how
    # store/writer.py + store/reader.py + cache/memo_store.py are treated). It
    # COMPOSES the 1.1 serializer/content-hash + 1.3 ApaaStorePaths/writer/reader
    # (+ its tamper guard) + the 5.2 MemoStore + the 5.1 key; it imports ONLY done
    # ArgusAgent leaves — no web stack, no LLM/api/providers module. Extend the guard (do
    # NOT fork) per AI-E4-7.
    "argus.cache.invalidation",
    # Story 1.7 — the Epic-1 capstone: the AuditRequest contract (pure), the
    # sequential pipeline orchestrator (impure shell), and the thin argparse CLI.
    # All three must stay FastAPI-free AND LLM-free (the Epic-1 verdict path is
    # zero-token, NFR-D2): none may transitively import the web stack, providers.*,
    # or argus.audit.* (Epic-6). The pipeline imports ONLY ArgusAgent's own done leaves.
    "argus.models",
    "argus.pipeline",
    "argus.cli",
    # Story 6.1 — the Epic-6 LLM-dispatch seam (audit/). ALL three audit modules
    # must stay web-stack-clean: ports.py + deep_audit.py are PURE; the adapter
    # (minions_llm_adapter.py) imports minions_core.providers.orchestrator (the
    # ONE allowed providers importer in argus.audit), but providers is verified
    # FastAPI-free across Epics 1-5, so importing the adapter keeps the WEB gate
    # green. The orthogonal no-LLM gate below proves the PURE seam ⊬ providers and
    # carves out the adapter as the explicitly-allowed importer. Extend (do NOT
    # fork) per AI-E5-7.
    "argus.audit.ports",
    "argus.audit.deep_audit",
    "argus.audit.minions_llm_adapter",
    # Story 6.2 — the PURE FR7 deep-claim AST-grounding validator (the
    # claim→validated? interface). Imports ONLY the 1.4 AstIndexEntry model; PURE
    # (no FS/clock/LLM/provider import/float) — importing it must not pull the web
    # stack OR any LLM/api/providers module (it is the ONE argus.audit module the
    # zero-token pipeline is allowed to import; see the no-LLM carve-out below).
    # Extend the guard (do NOT fork) per AI-E5-7.
    "argus.audit.grounding",
    # Story 6.3 — the PURE conservative orphan / dead-code detector (FR12). Consumes
    # the 1.4 definitions/edges + composes the 1.5 build_recording; PURE (no
    # FS/clock/LLM/provider import/float) — importing it must not pull the web stack
    # or any LLM/api/providers module. Extend the guard (do NOT fork) per AI-E5-7.
    "argus.detectors.orphan_code",
    # Story 6.3 (DN-PIPELINE-SPLIT) — the IMPURE .argus/ persist helpers extracted
    # from pipeline.py (a pure no-behavior-change refactor to keep pipeline.py under
    # the §3.2 1200-line limit). It is the IMPURE persist shell (FS writes via the
    # 1.3 writer) — added to the import-isolation coverage (FastAPI-free) but NOT to
    # any purity-asserting guard (mirroring store/writer.py). Imports ONLY done ArgusAgent
    # leaves — no web stack, no LLM/api/providers module. Extend (do NOT fork).
    "argus.pipeline_persist",
    # Story 6.4 — the PURE adversarial Prosecutor (FR19) + the CC #4 cross_partition
    # cut-edge pass + the advisory→verdict-eligible promotion authority (DN-PROMOTE).
    # The V1 default path is PURE-of-providers (DN-V1-DETERMINISTIC: the 6.1
    # LLMDispatchPort is the V2 forward seam, NOT the V1 default) — it composes the
    # 1.6 evaluate_verdict/order_findings + the 2.4 CutEdge + the 1.5 build_recording;
    # PURE (no FS/clock/LLM/provider import/float). Importing it must not pull the web
    # stack or any LLM/api/providers module. Extend the guard (do NOT fork) per AI-E5-7.
    "argus.verdict.prosecutor",
    # Story 6.6 — the PURE precision replay harness (FR20 precision MEASUREMENT). It
    # diffs emitted findings against the 6.5 cartridge-registry golden keys into
    # TP/FP/FN → a fixed-precision precision number. PURE (no FS/clock/LLM/provider
    # import/float) — it composes ONLY the 6.5 value-free golden-key registry (the
    # committed ground-truth store under tests/argus/cartridges/, which itself imports
    # only dataclasses and is web-free). Importing it must not pull the web stack or
    # any LLM/api/providers module. Extend the guard (do NOT fork) per AI-E5-7.
    "argus.precision.replay_harness",
    # Story 6.7 — the PURE pattern-matched HITL STOP/PROCEED escalation gate + the
    # frozen escalation-outcome / decision-record schema (governance/escalation.py).
    # The V1 escalation trigger is PATTERN-MATCHED (a deterministic rule over the
    # frozen findings / verdict-state), NOT LLM-judgment (the FR23 lock) — it
    # composes the 1.2 Recording + the 1.6 AuditVerdict/Verdict + the 1.1
    # compute_content_hash for the content-derived decision-id; PURE (no
    # FS/clock/LLM/provider import/float). Importing it must not pull the web stack
    # or any LLM/api/providers module (the no-LLM carve-out below proves it ⊬
    # providers). Extend the guard (do NOT fork) per AI-E5-7.
    "argus.governance.escalation",
    # Story 6.7 — the IMPURE append-only decision-record writer
    # (governance/decision_record.py). It is the IMPURE shell (FS read for
    # chain-head resolution + FS write) — added to the import-isolation coverage
    # (FastAPI-free) but NOT to any purity-asserting guard (mirroring store/writer.py
    # + store/reader.py + cache/memo_store.py). It COMPOSES the 1.1 serializer/
    # envelope + the 1.3 ApaaStoreWriter/ApaaStoreReader/ApaaStorePaths + the 6.7
    # PURE escalation resolution; it imports ONLY done ArgusAgent leaves — no web stack, no
    # LLM/api/providers module. Extend the guard (do NOT fork) per AI-E5-7.
    "argus.governance.decision_record",
    # Story 7.2 — the IMPURE dogfood proof-run generator (dogfood/proof_run.py). It
    # is the IMPURE shell (git enumerate + snapshot-materialize + FS copy + the audit
    # run + the .argus/ bundle persist) — added to the import-isolation coverage
    # (FastAPI-free) but NOT to any purity-asserting guard (mirroring pipeline.py +
    # decision_record.py + store/writer.py). It COMPOSES ONLY done ArgusAgent leaves: the
    # frozen run_audit_detailed (the zero-LLM-token audit), the 7.1 dogfood plan, the
    # 4.3 evidence bundle, the 4.2 integrity lint, the 1.3 writer/reader, and the 6.6
    # finding_match_key. No web stack, no LLM/api/providers module, no live LLM dispatch.
    # Extend the guard (do NOT fork) per AI-E5-7.
    "argus.dogfood.proof_run",
)

# Story 1.7 — the Epic-1 verdict path is ZERO-LLM-token (NFR-D2). The pipeline /
# cli / models must not pull any LLM dispatch surface (providers.*) or the Epic-6
# deep-audit package (argus.audit.*). These are checked in addition to the web
# stack so the zero-token property is mechanically pinned, not promised.
#
# Story 6.2 — the pipeline now imports the PURE provider-free FR7 grounding
# validator (argus.audit.grounding), so the blanket argus.audit.* ban is too broad
# for the pipeline path. The zero-token property is what matters: the pipeline
# must pull NO LLM DISPATCH surface (providers.* + the audit LLM modules: ports /
# deep_audit / minions_llm_adapter), but the pure grounding validator is allowed.
# _LLM_FORBIDDEN_PREFIXES stays as-is for any caller wanting the strict check;
# _PIPELINE_LLM_FORBIDDEN_PREFIXES is the pipeline-scoped set (the carve-out).
_LLM_FORBIDDEN_PREFIXES = ("minions_core.providers", "argus.audit")
_PIPELINE_LLM_FORBIDDEN_PREFIXES = (
    "minions_core.providers",
    "argus.audit.ports",
    "argus.audit.deep_audit",
    "argus.audit.minions_llm_adapter",
)


def _assert_clean_import(module: str) -> None:
    script = textwrap.dedent(
        f"""
        import importlib, sys
        importlib.import_module({module!r})
        leaked = [m for m in {_FORBIDDEN!r} if m in sys.modules]
        if leaked:
            print("LEAK:" + ",".join(leaked))
            raise SystemExit(1)
        raise SystemExit(0)
        """
    )
    proc = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (
        f"{module} transitively imported a web-stack module: "
        f"{proc.stdout.strip()} {proc.stderr.strip()}"
    )


def test_canonical_has_no_web_imports() -> None:
    _assert_clean_import("argus.store.canonical")


def test_envelope_has_no_web_imports() -> None:
    _assert_clean_import("argus.store.envelope")


def test_all_guarded_modules_clean() -> None:
    for module in _MODULES_UNDER_GUARD:
        _assert_clean_import(module)


def _assert_no_llm_import(
    module: str, prefixes: tuple[str, ...] = _LLM_FORBIDDEN_PREFIXES
) -> None:
    """Importing *module* must not transitively pull any LLM dispatch surface (NFR-D2)."""
    forbidden = ",".join(repr(p) for p in prefixes)
    script = textwrap.dedent(
        f"""
        import importlib, sys
        importlib.import_module({module!r})
        prefixes = [{forbidden}]
        leaked = [m for m in sys.modules if any(m == p or m.startswith(p + ".") for p in prefixes)]
        if leaked:
            print("LLM_LEAK:" + ",".join(sorted(leaked)))
            raise SystemExit(1)
        raise SystemExit(0)
        """
    )
    proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert proc.returncode == 0, (
        f"{module} transitively imported an LLM dispatch module (NFR-D2 zero-token): "
        f"{proc.stdout.strip()} {proc.stderr.strip()}"
    )


def test_evidence_bundle_does_not_import_minions_governance_evidence() -> None:
    """TC-ArgusAgent-EVIDENCE-001-20 — ArgusAgent's bundle is SEPARATE from the Minions governance bundle.

    Importing the 4.3 evidence-bundle module must NOT transitively pull
    ``minions_core.governance.evidence`` (the Minions decision-ledger / policy-trace /
    A2A-audit export) — ArgusAgent's audit-evidence bundle is self-contained and unrelated
    by design (the no-coupling rule). Runs in a CLEAN subprocess so an unrelated
    earlier import cannot mask a real coupling.
    """
    script = textwrap.dedent(
        """
        import importlib, sys
        importlib.import_module("argus.evidence.bundle")
        forbidden = "minions_core.governance.evidence"
        if forbidden in sys.modules:
            print("GOV_LEAK:" + forbidden)
            raise SystemExit(1)
        raise SystemExit(0)
        """
    )
    proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert proc.returncode == 0, (
        "argus.evidence.bundle imported the Minions governance evidence "
        f"bundle (it must be self-contained): {proc.stdout.strip()} {proc.stderr.strip()}"
    )


def test_pipeline_is_zero_token() -> None:
    """TC-ArgusAgent-PIPELINE-001-10 — the pipeline path imports NO LLM dispatch surface (NFR-D2).

    Story 6.2: the pipeline now imports the PURE provider-free FR7 grounding
    validator (``argus.audit.grounding``), so the pipeline-scoped forbidden set
    bans providers.* + the LLM-dispatch audit modules (ports / deep_audit /
    minions_llm_adapter) but ALLOWS the pure grounding validator. The zero-token
    property — no LLM dispatch surface is reachable from the default verdict path —
    is preserved (proven additionally below: the pipeline pulls grounding but NOT
    the LLM adapter).
    """
    for module in (
        "argus.models",
        "argus.pipeline",
        "argus.cli",
    ):
        _assert_no_llm_import(module, _PIPELINE_LLM_FORBIDDEN_PREFIXES)


def test_grounding_validator_is_provider_free() -> None:
    """TC-ArgusAgent-AUDIT-001-47 — the pure FR7 grounding validator ⊬ providers (AR8/NFR-D2).

    Story 6.2: importing ``argus.audit.grounding`` must NOT transitively pull
    ``minions_core.providers`` — the validator is a pure fold over the 1.4
    AstIndexEntry with no provider dependency. It legitimately imports its OWN
    argus.audit package shell, so (like the pure seam) assert only the providers
    prefix here.
    """
    script = textwrap.dedent(
        """
        import importlib, sys
        importlib.import_module("argus.audit.grounding")
        leaked = [m for m in sys.modules if m == "minions_core.providers"
                  or m.startswith("minions_core.providers.")]
        if leaked:
            print("PROVIDER_LEAK:" + ",".join(sorted(leaked)))
            raise SystemExit(1)
        raise SystemExit(0)
        """
    )
    proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert proc.returncode == 0, (
        "argus.audit.grounding transitively imported minions_core.providers "
        f"(the pure FR7 validator must stay provider-free): {proc.stdout.strip()} {proc.stderr.strip()}"
    )


def test_prosecutor_is_provider_free() -> None:
    """TC-ArgusAgent-PROSECUTOR-001-20 — the V1 Prosecutor ⊬ providers (AR8/NFR-D2/DN-V1-DETERMINISTIC).

    Story 6.4: importing ``argus.verdict.prosecutor`` must NOT transitively pull
    ``minions_core.providers`` (or any ``argus.audit`` LLM surface) — the V1 default
    Prosecutor is a PURE recording-consumer with NO provider dependency (the 6.1
    ``LLMDispatchPort`` is the documented V2 forward seam, never the V1 default). It
    composes the 1.6 verdict fold + the 2.4 cut-edge set + the 1.5 ``build_recording``.
    """
    script = textwrap.dedent(
        """
        import importlib, sys
        importlib.import_module("argus.verdict.prosecutor")
        forbidden_prefixes = ("minions_core.providers", "argus.audit")
        leaked = [m for m in sys.modules
                  if any(m == p or m.startswith(p + ".") for p in forbidden_prefixes)]
        if leaked:
            print("LLM_LEAK:" + ",".join(sorted(leaked)))
            raise SystemExit(1)
        raise SystemExit(0)
        """
    )
    proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert proc.returncode == 0, (
        "argus.verdict.prosecutor transitively imported an LLM dispatch "
        f"module (the V1 default must be pure-of-providers — DN-V1-DETERMINISTIC): "
        f"{proc.stdout.strip()} {proc.stderr.strip()}"
    )


def test_precision_harness_is_provider_free() -> None:
    """TC-ArgusAgent-PRECISION-001-20 — the 6.6 precision harness ⊬ providers / argus.audit (AR8/NFR-D2).

    Story 6.6: importing ``argus.precision.replay_harness`` must NOT transitively pull
    ``minions_core.providers`` (or any ``argus.audit`` LLM surface) — the precision
    computation is a PURE fold over already-recorded findings with NO provider
    dependency (NFR-D2 zero-token). It composes ONLY the 6.5 value-free golden-key
    registry; the impure staging/auditing is the test-harness shell, not this module.
    """
    script = textwrap.dedent(
        """
        import importlib, sys
        importlib.import_module("argus.precision.replay_harness")
        forbidden_prefixes = ("minions_core.providers", "argus.audit")
        leaked = [m for m in sys.modules
                  if any(m == p or m.startswith(p + ".") for p in forbidden_prefixes)]
        if leaked:
            print("LLM_LEAK:" + ",".join(sorted(leaked)))
            raise SystemExit(1)
        raise SystemExit(0)
        """
    )
    proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert proc.returncode == 0, (
        "argus.precision.replay_harness transitively imported an LLM "
        f"dispatch module (the pure precision fold must be zero-token — NFR-D2): "
        f"{proc.stdout.strip()} {proc.stderr.strip()}"
    )


def test_escalation_gate_is_provider_free() -> None:
    """TC-ArgusAgent-HITL-001-20 — the V1 HITL escalation gate ⊬ providers (AR8/NFR-D2/FR23 lock).

    Story 6.7: importing ``argus.governance.escalation`` must NOT transitively pull
    ``minions_core.providers`` (or any ``argus.audit`` LLM surface) — the V1 default
    escalation trigger is PATTERN-MATCHED (a deterministic rule over frozen
    findings / verdict-state), NEVER an LLM judgment (the FR23 lock; the 6.1
    ``LLMDispatchPort`` is the documented V2 forward seam, never the V1 default). It
    composes the 1.2 Recording + the 1.6 verdict models + the 1.1
    ``compute_content_hash``.
    """
    script = textwrap.dedent(
        """
        import importlib, sys
        importlib.import_module("argus.governance.escalation")
        forbidden_prefixes = ("minions_core.providers", "argus.audit")
        leaked = [m for m in sys.modules
                  if any(m == p or m.startswith(p + ".") for p in forbidden_prefixes)]
        if leaked:
            print("LLM_LEAK:" + ",".join(sorted(leaked)))
            raise SystemExit(1)
        raise SystemExit(0)
        """
    )
    proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert proc.returncode == 0, (
        "argus.governance.escalation transitively imported an LLM "
        f"dispatch module (the V1 pattern-matched gate must be zero-token — FR23): "
        f"{proc.stdout.strip()} {proc.stderr.strip()}"
    )


def test_decision_record_writer_is_provider_free() -> None:
    """TC-ArgusAgent-HITL-001-21 — the append-only decision-record writer ⊬ providers (AR7/NFR-D2).

    Story 6.7: importing ``argus.governance.decision_record`` must NOT transitively
    pull ``minions_core.providers`` (or any ``argus.audit`` LLM surface) — the writer
    is an IMPURE persistence shell composing ONLY the 1.1 envelope + the 1.3 store
    writer/reader/paths + the 6.7 PURE escalation resolution, with NO provider
    dependency.
    """
    script = textwrap.dedent(
        """
        import importlib, sys
        importlib.import_module("argus.governance.decision_record")
        forbidden_prefixes = ("minions_core.providers", "argus.audit")
        leaked = [m for m in sys.modules
                  if any(m == p or m.startswith(p + ".") for p in forbidden_prefixes)]
        if leaked:
            print("LLM_LEAK:" + ",".join(sorted(leaked)))
            raise SystemExit(1)
        raise SystemExit(0)
        """
    )
    proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert proc.returncode == 0, (
        "argus.governance.decision_record transitively imported an LLM "
        f"dispatch module (the writer must be provider-free — AR7/NFR-D2): "
        f"{proc.stdout.strip()} {proc.stderr.strip()}"
    )


def test_pure_audit_seam_is_provider_free() -> None:
    """TC-ArgusAgent-AUDIT-001-10 — the PURE seam (ports/deep_audit) ⊬ providers (AR8/AR9/NFR-D2).

    Story 6.1: importing ``argus.audit.ports`` or ``argus.audit.deep_audit`` must
    NOT transitively pull ``minions_core.providers`` (or any ``argus.audit`` LLM
    surface beyond themselves) — the determinism quarantine: the pure seam is a
    structural Protocol + frozen DTOs + a read-only closure-builder over the 5.1
    cache key, with no provider dependency. The adapter is the ONE allowed
    importer (proven separately below).
    """
    # The pure seam must not pull ``minions_core.providers``. (It legitimately
    # imports its OWN argus.audit package, so the _LLM_FORBIDDEN_PREFIXES check —
    # which forbids argus.audit too — is too broad here; assert only the providers
    # prefix for the pure seam.)
    for module in ("argus.audit.ports", "argus.audit.deep_audit"):
        script = textwrap.dedent(
            f"""
            import importlib, sys
            importlib.import_module({module!r})
            leaked = [m for m in sys.modules if m == "minions_core.providers"
                      or m.startswith("minions_core.providers.")]
            if leaked:
                print("PROVIDER_LEAK:" + ",".join(sorted(leaked)))
                raise SystemExit(1)
            raise SystemExit(0)
            """
        )
        proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
        assert proc.returncode == 0, (
            f"{module} transitively imported minions_core.providers (the PURE seam "
            f"must stay provider-free — AR8/NFR-D2): {proc.stdout.strip()} {proc.stderr.strip()}"
        )


def test_minions_llm_adapter_has_no_minions_core_imports() -> None:
    """TC-ArgusAgent-AUDIT-001-11 — Story 9.1 (IN-2 / RS-1): minions_llm_adapter has ZERO minions_core imports.

    `argus.audit.minions_llm_adapter` delegates to `OpenLLMAdapter` and carries
    zero import dependency on `minions_core`. Importing `minions_llm_adapter`
    must leave `minions_core` completely absent from `sys.modules`.
    """
    script = textwrap.dedent(
        """
        import importlib, sys
        importlib.import_module("argus.audit.minions_llm_adapter")
        leaked = [m for m in sys.modules if m == "minions_core" or m.startswith("minions_core.")]
        if leaked:
            print("MINIONS_CORE_LEAK:" + ",".join(sorted(leaked)))
            raise SystemExit(1)
        raise SystemExit(0)
        """
    )
    proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    assert proc.returncode == 0, (
        "argus.audit.minions_llm_adapter imported minions_core (RS-1 / IN-2 violation): "
        f"{proc.stdout.strip()} {proc.stderr.strip()}"
    )


def test_all_guarded_modules_have_no_minions_core_imports() -> None:
    """TC-ArgusAgent-STORE-001-51 — Story 9.1 (RS-1): NO argus module imports minions_core.

    Importing any module under _MODULES_UNDER_GUARD must leave minions_core
    completely absent from sys.modules.
    """
    for module in _MODULES_UNDER_GUARD:
        script = textwrap.dedent(
            f"""
            import importlib, sys
            importlib.import_module({module!r})
            leaked = [m for m in sys.modules if m == "minions_core" or m.startswith("minions_core.")]
            if leaked:
                print("MINIONS_CORE_LEAK:" + ",".join(sorted(leaked)))
                raise SystemExit(1)
            raise SystemExit(0)
            """
        )
        proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
        assert proc.returncode == 0, (
            f"{module} transitively imported minions_core (RS-1 violation): "
            f"{proc.stdout.strip()} {proc.stderr.strip()}"
        )

