"""Import-isolation gate for ArgusAgent store modules (AC7 / AR7 / AR9).

Verification area ArgusAgent-STORE (TC-ArgusAgent-STORE-001-50). ArgusAgent is downstream of the
HTTP/A2A boundary: its modules must NOT transitively import the web stack
(``fastapi`` / ``uvicorn`` / ``starlette``). This durable, committed gate is
seeded here (story 1.1) and extended by later stories as new ArgusAgent modules land.

Each import runs in a CLEAN subprocess (fresh ``sys.modules``) so a web import
pulled in by an unrelated test earlier in the session cannot mask a real leak.
"""

from __future__ import annotations

import ast
import os
import pathlib
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
    # It reuses argus.shared.budget_guardrails BY IMPORT (AR7) for the
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
    # Story 12.3 — the IMPURE composition that WIRES the 5.1 key + the 5.2 store onto the
    # pipeline's deterministic detect/grade stage (FR27/NFR-D1). It is the first module in
    # `argus.cache` to be reachable from `argus.cli` on the DEFAULT path, which makes its
    # import hygiene load-bearing rather than incidental: it now runs on every invocation.
    # It composes the 5.1 key + 5.2 store + the 1.4 index's version probe + the intake's
    # source state, and imports ONLY done ArgusAgent leaves — no web stack, no
    # LLM/api/providers module, and in particular NOT `argus.audit.*`, whose dispatch
    # surface must never reach the memoization path (NFR-S6). The AC6.1 fence therefore
    # names the deep pass's rule stem as a literal and joins it to
    # `deep_pass.RULE_DEGRADED_DEEP_READ` in the TEST layer
    # (`TC-ArgusAgent-CACHE-001-97`), never by importing it here. Extend the guard (do NOT
    # fork) per AI-E4-7.
    "argus.cache.stage_memo",
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
    # Story 12.1 — the audit fold's DERIVATION stages extracted from pipeline.py (a pure
    # no-behaviour-change refactor to bring pipeline.py back under the §3.2 / NFR-M1
    # 1200-line limit, which it had breached at 1331). It is IMPURE in the same sense
    # pipeline.py is — it READS source files and runs the four V1 deterministic detectors —
    # so it is added to the import-isolation coverage (FastAPI-free) but NOT to any
    # purity-asserting guard, exactly as `argus.pipeline_persist` was in 6.3. It imports
    # ONLY done ArgusAgent leaves (grounding / detectors / index / ledger / cost) — no web
    # stack, no LLM/api/providers module. Extend the guard (do NOT fork) per AI-E5-7.
    "argus.pipeline_stages",
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
    # Story 9.2 / DF-8-5-D — the two PURE siblings the proof-run generator was split
    # into. ``proof_types`` holds the five frozen result dataclasses; ``proof_render``
    # holds the pure markdown renderer + the externalization-guard sentence it renders.
    # Neither imports ``proof_run`` (the impure shell) — the edge runs one way only,
    # which is what makes the AR8 pure/impure line structural rather than narrated. Both
    # are registered here so importing them can never quietly pull the web stack or a
    # provider module through a future edit. Extend the guard (do NOT fork) per AI-E5-7.
    "argus.dogfood.proof_types",
    "argus.dogfood.proof_render",
    # Story 12.6 / FR35 — the MCP stdio adapter. THIS IS THE GATE THAT DECIDED THE
    # ARCHITECTURE, not one that merely observes it: the official `mcp` Python SDK declares
    # `starlette`, `uvicorn` and `sse-starlette` as REQUIRED dependencies (it carries its
    # HTTP server transports in the base package, not behind an extra), so adopting it
    # would have put a web server into this distribution's dependency tree and turned this
    # very gate red. The JSON-RPC layer is hand-rolled from the standard library instead,
    # which is what keeps ADR #20 ("downstream of the HTTP/A2A boundary — takes no A2A
    # token, registers no route") true by construction rather than by discipline.
    # `protocol` is the PURE message layer and `server` the IMPURE stdin→stdout shell, so
    # both are added to the import-isolation coverage but only the split itself is a
    # purity claim (mirroring how pipeline_persist.py and store/writer.py are treated).
    # A stronger, adapter-specific gate lives beside them in tests/test_mcp_server.py
    # (`-04` bans `socket`/`http`/`ssl`/`asyncio` outright over `argus/mcp/**`, and `-05`
    # observes the REAL process opening no listener) — this registry is the standing
    # web-stack quarantine every module joins. Extend the guard (do NOT fork) per AI-E3-6.
    "argus.mcp",
    "argus.mcp.protocol",
    "argus.mcp.server",
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

_PACKAGE_ROOT = pathlib.Path(__file__).resolve().parents[1] / "argus"

# ─────────────────────────────────────────────────────────────────────────────
# Story 12.2 / AC2.2 — THE POPULATIONS ARE DERIVED, NOT LISTED (AI-E10-5: *the list is
# never the contract*).
#
# Both populations below used to be hand-written tuples, and both were structurally
# blind to the change Story 12.2 makes:
#
#   * the FORBIDDEN set named ``ports`` / ``deep_audit`` / ``minions_llm_adapter`` and
#     silently omitted ``open_llm_adapter`` — the module that actually performs the HTTP
#     dispatch — so the one file in the package that can open a socket was never on the
#     list that exists to keep sockets off the default path. A NEW ``argus/audit/*``
#     module (this story adds ``deep_pass.py``) would likewise have leaked past.
#   * the ENTRY-POINT set was the three-tuple ``(models, pipeline, cli)``, written before
#     ``pipeline_persist.py`` (6.3) and ``pipeline_stages.py`` (12.1) existed. Neither was
#     ever added, so two thirds of the pipeline surface was outside the gate.
#
# Deriving both from the package's real contents means a module added AFTER this story is
# covered without anyone remembering to add it. `-12` asserts the derivation is
# non-vacuous by GENERATING a new module and observing that it is covered with no edit
# here at all.
# ─────────────────────────────────────────────────────────────────────────────

# The ONE `argus.audit` module the zero-token pipeline path is allowed to import: the
# PURE, provider-free FR7 grounding validator (Story 6.2's carve-out, unchanged). It is
# named as an EXCEPTION to a derived population rather than as a member of a listed one —
# the difference between "everything is forbidden unless excused" and "everything is
# allowed unless listed", which is the whole of AI-E10-5.
_PURE_AUDIT_LEAVES = frozenset({"argus.audit.grounding"})


def _audit_package_modules() -> frozenset[str]:
    """Every module under ``argus/audit/**``, read off the filesystem (never listed)."""
    found = set()
    for path in sorted((_PACKAGE_ROOT / "audit").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        stem = path.stem
        if stem == "__init__":
            continue
        found.add(f"argus.audit.{stem}")
    return frozenset(found)


def derive_pipeline_forbidden_prefixes() -> tuple[str, ...]:
    """The LLM-dispatch surface the default pipeline path may not import (NFR-D2).

    Every module under ``argus/audit/**`` EXCEPT the pure provider-free leaves, plus the
    provider package prefix. Sorted, so a failure message is stable.

    The ``argus.audit`` package ``__init__`` is deliberately NOT forbidden: importing the
    permitted ``argus.audit.grounding`` necessarily loads its parent package, so banning
    the parent would make the existing, correct 6.2 carve-out impossible to satisfy and
    the gate would be red for a reason unrelated to egress.
    """
    return tuple(
        sorted(("minions_core.providers", *(_audit_package_modules() - _PURE_AUDIT_LEAVES)))
    )


def derive_pipeline_entry_points() -> tuple[str, ...]:
    """The default-path entry points the quarantine covers (AC2.2).

    Derived: ``argus/cli.py``, ``argus/models.py`` and EVERY ``argus/pipeline*.py``
    sibling — so the family that grew from one module to three without the gate noticing
    cannot grow again unnoticed.
    """
    modules = {"argus.cli", "argus.models"}
    for path in sorted(_PACKAGE_ROOT.glob("pipeline*.py")):
        modules.add(f"argus.{path.stem}")
    return tuple(sorted(modules))


_PIPELINE_LLM_FORBIDDEN_PREFIXES = derive_pipeline_forbidden_prefixes()


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

    Story 6.2: the pipeline imports the PURE provider-free FR7 grounding validator
    (``argus.audit.grounding``), so the pipeline-scoped forbidden set bans providers.* +
    the LLM-dispatch audit modules but ALLOWS the pure grounding validator.

    Story 12.2 / AC2.2: BOTH populations are now DERIVED from the package rather than
    hand-listed, and both are asserted non-empty here — a derivation that silently
    produced nothing would turn this gate into a no-op that passes forever.

    🔴 READ THIS BEFORE TREATING THIS TEST'S GREEN AS EVIDENCE. Since Story 12.2 the
    pipeline reaches the deep pass through a FUNCTION-LOCAL import, so on a default run
    the import statement never executes and this gate is green BY CONSTRUCTION — for a
    reason that has nothing to do with safety. A one-directional import-absence gate over
    a deferred path is a guard that passes by NOT EXECUTING. Its green is evidence only
    when read together with the POSITIVE CONTROL in
    ``test_TC_ArgusAgent_PIPELINE_001_11_deferred_dispatch_surface_appears_only_when_opted_in``,
    which proves the surface DOES appear when the opt-in is given.
    """
    entry_points = derive_pipeline_entry_points()
    assert len(entry_points) >= 4, (
        f"the entry-point derivation collapsed to {entry_points}; it must at least find "
        "cli, models and the pipeline family"
    )
    assert len(_PIPELINE_LLM_FORBIDDEN_PREFIXES) >= 5, (
        f"the forbidden-surface derivation collapsed to {_PIPELINE_LLM_FORBIDDEN_PREFIXES}"
    )
    # The module that can actually open a socket must be in the derived set. It was
    # MISSING from the hand-written tuple this replaced.
    assert "argus.audit.open_llm_adapter" in _PIPELINE_LLM_FORBIDDEN_PREFIXES
    assert "argus.audit.grounding" not in _PIPELINE_LLM_FORBIDDEN_PREFIXES, (
        "the pure FR7 validator is the 6.2 carve-out and must stay importable"
    )

    for module in entry_points:
        _assert_no_llm_import(module, _PIPELINE_LLM_FORBIDDEN_PREFIXES)


def test_TC_ArgusAgent_PIPELINE_001_12_a_new_audit_module_is_covered_without_a_registry_edit() -> None:
    """TC-ArgusAgent-PIPELINE-001-12 — AC2.2: the derivation is NON-VACUOUS, proven by generation.

    Story 12.2. AI-E10-5 — *the list is never the contract*. The previous forbidden set
    was a hand-written tuple, so a module added to ``argus/audit/`` was outside the gate
    until somebody remembered to add it, and nothing ever went red to remind them. That
    is not hypothetical: ``open_llm_adapter.py`` — the one module in the package that
    performs a live HTTP dispatch — was never on it.

    THE ADVERSARIAL VARIANT IS GENERATED, NOT HAND-LISTED: a real ``argus/audit/*.py``
    module is written to disk, the derivation is re-run, and the new module must appear
    in the forbidden population with NO edit to this file. The variant is removed in a
    ``finally`` so a failure cannot leave the package dirty.

    The count is asserted to GROW BY EXACTLY ONE, so a derivation that returned some
    fixed superset (and would therefore "cover" anything) cannot pass either.
    """
    before = derive_pipeline_forbidden_prefixes()
    probe = _PACKAGE_ROOT / "audit" / "_synthetic_egress_probe.py"
    assert not probe.exists(), "the probe module leaked from an earlier run"
    try:
        probe.write_text(
            '"""Synthetic AC2.2 probe — written and removed by a test."""\n',
            encoding="utf-8",
        )
        after = derive_pipeline_forbidden_prefixes()
    finally:
        probe.unlink(missing_ok=True)
        # A stale .pyc would make the module importable after the source is gone.
        for cached in (_PACKAGE_ROOT / "audit" / "__pycache__").glob(
            "_synthetic_egress_probe*.pyc"
        ):
            cached.unlink(missing_ok=True)

    assert "argus.audit._synthetic_egress_probe" in after, (
        "a NEW argus/audit module was not picked up by the derived forbidden set — the "
        "population is not actually derived from the package"
    )
    assert len(after) == len(before) + 1, (
        f"the derivation must grow by exactly one, not from {len(before)} to {len(after)}"
    )
    assert not probe.exists()


def test_TC_ArgusAgent_PIPELINE_001_11_deferred_dispatch_surface_appears_only_when_opted_in(
    tmp_path: pathlib.Path,
) -> None:
    """TC-ArgusAgent-PIPELINE-001-11 — AC3: the POSITIVE CONTROL for a deferred import.

    Story 12.2. ``test_pipeline_is_zero_token`` above asserts that the LLM dispatch
    surface is ABSENT after a default run. Since 12.2 wires the deep pass through a
    function-local import, that absence is guaranteed by the fact that the import
    statement never runs — so on its own it proves nothing about whether the pass is
    wired at all. A gate that is green because the code it guards was never reached is
    the deferred-import form of a vacuous guard, and this story creates that hazard on
    purpose.

    THE POSITIVE CONTROL closes it, in BOTH directions, each in a FRESH subprocess so an
    earlier import cannot mask or manufacture either answer:

    * opt-in ABSENT  → ``argus.audit.deep_audit`` / ``deep_pass`` NOT in ``sys.modules``
      (NFR-S6: nothing leaves on the default path, and nothing is even loaded);
    * opt-in PRESENT → they ARE in ``sys.modules`` (the wiring is real and reachable).

    NO EGRESS EITHER WAY: the opted-in leg runs with NO provider endpoint configured, so
    the pass refuses to construct an adapter and degrades. The observation is which
    modules loaded, never a byte on a wire.
    """
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "m.py").write_text(
        "def f(x):\n    return x + 1\n", encoding="utf-8"
    )

    probe = textwrap.dedent(
        """
        import sys
        from argus.cli import main
        main(sys.argv[1:])
        watched = ("argus.audit.deep_audit", "argus.audit.deep_pass")
        print("LOADED:" + ",".join(sorted(m for m in watched if m in sys.modules)))
        """
    )

    def _loaded(*argv: str) -> set[str]:
        env = dict(os.environ)
        # Strip any ambient provider configuration so neither leg can dispatch.
        for name in ("OPENAI_BASE_URL", "OLLAMA_HOST", "OLLAMA_URL"):
            env.pop(name, None)
        proc = subprocess.run(
            [sys.executable, "-c", probe, "audit", str(tmp_path), *argv],
            capture_output=True,
            text=True,
            env=env,
        )
        line = [ln for ln in proc.stdout.splitlines() if ln.startswith("LOADED:")]
        assert line, f"probe produced no marker: {proc.stdout} {proc.stderr}"
        return {m for m in line[0][len("LOADED:") :].split(",") if m}

    default_run = _loaded()
    assert default_run == set(), (
        "NFR-S6: a DEFAULT run loaded an LLM dispatch module — the deferred import "
        f"executed when it must not have: {sorted(default_run)}"
    )

    opted_in = _loaded("--deep-audit")
    assert opted_in == {"argus.audit.deep_audit", "argus.audit.deep_pass"}, (
        "AC3 POSITIVE CONTROL FAILED: with --deep-audit given, the deep-audit seam was "
        f"still not loaded, so the absence above proves nothing: {sorted(opted_in)}. "
        "Either the pass is not wired, or the gate cannot see it."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Story 12.2 / AC2.3 — THE ENVIRONMENT IS NEVER AN OPT-IN
# ─────────────────────────────────────────────────────────────────────────────


def adapter_environment_variables() -> tuple[str, ...]:
    """Every environment variable ``OpenLLMAdapter`` reads, derived by ``ast`` (AC2.3).

    DERIVED FROM THE ADAPTER'S OWN SOURCE, never transcribed, because the risk this gate
    exists to cover is precisely *someone adds a seventh variable*. A hand-copied list
    would go stale on exactly the change that matters and would keep passing.

    Walks ``argus/audit/open_llm_adapter.py`` for ``os.getenv("NAME")`` calls and returns
    the sorted literal names.
    """
    source = (_PACKAGE_ROOT / "audit" / "open_llm_adapter.py").read_text(encoding="utf-8")
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        func = node.func
        is_getenv = (isinstance(func, ast.Attribute) and func.attr == "getenv") or (
            isinstance(func, ast.Name) and func.id == "getenv"
        )
        if is_getenv and isinstance(node.args[0], ast.Constant):
            value = node.args[0].value
            if isinstance(value, str):
                names.add(value)
    return tuple(sorted(names))


def test_TC_ArgusAgent_AUDIT_001_62_a_live_looking_environment_is_not_an_opt_in(
    tmp_path: pathlib.Path,
) -> None:
    """TC-ArgusAgent-AUDIT-001-62 — AC2.3: only the FLAG opts in. Never the environment.

    Story 12.2 / FR36 / NFR-S6. MEASURED on ``2bea92f``: ``OpenLLMAdapter.__init__``
    silently absorbs the ambient environment and defaults its API key to the literal
    ``"mock-key"`` — with ``OLLAMA_HOST`` set, a freshly constructed adapter reports that
    host as its ``_api_base``. So CONSTRUCTING the adapter is already a configuration
    decision made by the environment, and any design in which the environment could cause
    construction would be an environment-triggered egress path.

    THE OBSERVABLE: which modules are resident after a run. With EVERY variable the
    adapter reads set to a live-looking value and the opt-in ABSENT, the run must load no
    dispatch surface at all — no adapter is constructed, so nothing can transmit.

    THE POPULATION IS DERIVED (``adapter_environment_variables``), so a variable added to
    the adapter tomorrow is covered by this gate today.

    ⚠️ The values are deliberately UNROUTABLE (``.invalid`` is RFC 6761 reserved and can
    never resolve) so that even a total failure of this gate cannot open a socket to a
    real host. Story 12.2 §0.3: no live dispatch, ever, for any reason.
    """
    variables = adapter_environment_variables()
    assert len(variables) >= 6, (
        f"the ast derivation found only {variables}; the adapter reads more than that. "
        "A derivation that under-counts silently narrows the gate."
    )

    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "m.py").write_text("def f():\n    return 1\n", encoding="utf-8")

    env = dict(os.environ)
    for name in variables:
        env[name] = "http://argus-must-never-dial.invalid:11434"

    probe = textwrap.dedent(
        """
        import sys
        from argus.cli import main
        main(sys.argv[1:])
        watched = (
            "argus.audit.deep_audit",
            "argus.audit.deep_pass",
            "argus.audit.open_llm_adapter",
            "argus.audit.ports",
            "httpx",
        )
        print("LOADED:" + ",".join(sorted(m for m in watched if m in sys.modules)))
        """
    )
    proc = subprocess.run(
        [sys.executable, "-c", probe, "audit", str(tmp_path)],
        capture_output=True,
        text=True,
        env=env,
    )
    marker = [ln for ln in proc.stdout.splitlines() if ln.startswith("LOADED:")]
    assert marker, f"probe produced no marker: {proc.stdout} {proc.stderr}"
    loaded = {m for m in marker[0][len("LOADED:") :].split(",") if m}

    assert loaded == set(), (
        "AC2.3 VIOLATED: with every adapter environment variable set to a live-looking "
        f"value and NO --deep-audit flag, the run loaded {sorted(loaded)}. An environment "
        "variable must never be able to enable egress; only the operator's explicit "
        "invocation-level act may."
    )


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



# ─────────────────────────────────────────────────────────────────────────────
# Story 9.2 / AC11 (ledger item RS-4b) — the `minions_core` TEXTUAL sweep, as an
# ALLOWLIST over an enumerated space, not a zero-count assertion.
#
# TC-ArgusAgent-STORE-001-51 above proves no argus module IMPORTS minions_core. That is
# the runtime half. This is the textual half: after the repo separation, `minions_core`
# survived in nine docstrings/comments and one operator-visible error message as a stale
# PROVENANCE claim — prose asserting a dependency, a reuse-by-import, or a source tree
# that no longer exists anywhere in this repository. Story 9.2 swept all nine.
#
# It is deliberately an ALLOWLIST and never `count == 0`. Two occurrences MUST survive,
# both in `argus/audit/minions_llm_adapter.py`, and both written by Story 9.1 as TRUE
# NEGATIVE statements — "requiring the unpackaged `minions_core` library" (the thing the
# adapter exists NOT to need) and "zero dependency on `minions_core`". Deleting them
# would delete the documentation of RS-1/IN-2, which is the opposite of the sweep's
# intent; a naive grep-and-delete gets exactly this wrong. RS-4b's own text excludes the
# file by name.
#
# The enumerated space is the allowlist itself: any occurrence in any OTHER module fails,
# so a re-introduction cannot hide, and a new allowlisted file cannot be added silently.
# ─────────────────────────────────────────────────────────────────────────────

# The ONLY paths permitted to mention the token, with the number of occurrences each is
# permitted to carry. Both are Story 9.1's true negative statements.
_MINIONS_CORE_ALLOWLIST: dict[str, int] = {
    "argus/audit/minions_llm_adapter.py": 2,
}

_MINIONS_CORE_TOKEN = "minions_core"


def test_TC_ArgusAgent_STORE_001_109_minions_core_text_only_in_the_allowlist() -> None:
    """TC-ArgusAgent-STORE-001-109 — Story 9.2/AC11 (RS-4b): no stale provenance claim survives.

    Walks every ``argus/**/*.py`` module and counts occurrences of the token. Any module
    outside :data:`_MINIONS_CORE_ALLOWLIST` fails, and an allowlisted module that grows
    or loses occurrences also fails — so neither a re-introduction nor a silent deletion
    of Story 9.1's negative statements can pass.
    """
    package_root = pathlib.Path(__file__).resolve().parents[1] / "argus"
    repo_root = package_root.parent
    counts: dict[str, int] = {}
    modules = 0
    for path in sorted(package_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        modules += 1
        n = path.read_text(encoding="utf-8").count(_MINIONS_CORE_TOKEN)
        if n:
            counts[path.relative_to(repo_root).as_posix()] = n

    # Non-vacuity: the sweep really walked the package.
    assert modules >= 60, f"the sweep only walked {modules} modules"
    unexpected = {k: v for k, v in counts.items() if k not in _MINIONS_CORE_ALLOWLIST}
    assert not unexpected, (
        "RS-4b: a stale `minions_core` provenance claim was re-introduced outside the "
        f"allowlist: {unexpected}"
    )
    assert counts == _MINIONS_CORE_ALLOWLIST, (
        "the allowlisted true-negative statements changed; they document RS-1/IN-2 and "
        f"must not be deleted. expected {_MINIONS_CORE_ALLOWLIST}, measured {counts}"
    )


def test_TC_ArgusAgent_STORE_001_110_allowlisted_mentions_are_negative_statements() -> None:
    """TC-ArgusAgent-STORE-001-110 — Story 9.2/AC11 (D9): the allowlist is not a loophole.

    An allowlist that merely permits a filename would let a genuine stale claim be
    smuggled back into the one exempt module. Each surviving occurrence must sit in a
    line that DENIES the dependency, so the exemption cannot be repurposed into a
    provenance claim.
    """
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    denial_markers = ("zero dependency", "unpackaged", "without", "no longer", "never")
    for rel in _MINIONS_CORE_ALLOWLIST:
        lines = (repo_root / rel).read_text(encoding="utf-8").splitlines()
        hits = [ln for ln in lines if _MINIONS_CORE_TOKEN in ln]
        assert len(hits) == _MINIONS_CORE_ALLOWLIST[rel]
        for line in hits:
            lowered = line.lower()
            assert any(marker in lowered for marker in denial_markers), (
                f"{rel}: {line.strip()!r} mentions the token without denying the "
                "dependency — the allowlist covers TRUE NEGATIVE statements only"
            )
