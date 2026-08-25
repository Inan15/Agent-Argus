"""PURE orphan / dead-code detector over the 1.4 AST index (CONSERVATIVE).

Drivers: ArgusAgent-FR-12 (detect orphan / dead code — a function/class with no
referencing requirement or caller — each with a verifiable locator), ArgusAgent-FR-13
(every finding carries ≥1 verifiable locator or is rejected, not emitted — via the
EXISTING 1.5 ``build_recording``), ArgusAgent-FR-33-support / cross-cutting #6
(advisory-by-contract: the orphan finding is ``advisory=True`` and CANNOT alone
move the verdict to 🔴 — the Story 6.4 Prosecutor owns promotion), ArgusAgent-NFR-D2 (a
pure, zero-LLM-token scorer over recorded inputs), AR10 / NFR-R1 (a malformed /
empty / None index, a ``parse_failed`` entry, a ``Definition`` with a ``None``/empty
name → a recorded ``DegradedCondition`` or a NOT-orphan classification, NEVER an
uncaught raise — NAMED handling, no bare ``except``), AR7 / §3.3 (REUSE the 1.4
pre-built ``definitions``/``edges`` — NO re-parse, NO second tree-sitter / ``ast`` /
``radon`` call; compose the EXISTING ``build_recording`` — NO finding fork), AR8
(PURE — no I/O, no clock, no LLM, no provider import, no float), AR4 (single
canonical serializer; content-derived ids; no clock/uuid/random/iteration-order),
AR11 (findings emitted in a SORTED deterministic order), ArgusAgent-NFR-S1 (cite the
``Definition`` name / ``ast_span`` / counts — NEVER a source excerpt),
ArgusAgent-AI-E1-1 (non-ASCII / locale discipline — a non-ASCII ``Definition.name``
classifies + serializes under ``PYTHONIOENCODING=utf-8``).

Consumes DF-1-4-A (the carry-forward this story closes)
-------------------------------------------------------
This detector is DF-1-4-A's ``target_story``. The 1.4 ``CodeEdge`` set is
UNRESOLVED-NAME only — the bare callee identifier / trailing attribute at a line,
with NO name binding, NO scope resolution, NO import resolution, NO method-vs-
function disambiguation (architecture/1.4: "name binding / scope resolution is
deliberately not done here … NOT a full call-graph resolver — that is Epic-6
depth"). The reference graph is therefore a NAME-MATCH graph, not a resolved call
graph. The detector consumes the SAME pre-built ``definitions``/``edges`` (it does
NOT re-parse) and computes a CONSERVATIVE name-reachability fact.

The conservative rule (DN-CONSERVATIVE) + its HONEST limitation
---------------------------------------------------------------
A false dead-code accusation (deleting LIVE code) is far more harmful than a missed
orphan, so the bar is ASYMMETRIC toward silence — the detector NEVER cries wolf on
the unresolved-name substrate. A ``function``/``class`` ``Definition`` is flagged an
orphan ONLY when ALL hold:

  1. its ``name`` appears as NO ``CodeEdge.callee`` ANYWHERE in the whole index
     (a name-match miss — the unresolved-name reachability fact), AND
  2. its ``name`` is not on the locked EXCLUSION set (dunders, ``__all__``/export
     hooks, ``test_*``/``setUp``/``tearDown`` entrypoints, and a small locked set of
     known framework/registry/decorator hook names the unresolved substrate cannot
     reason about), AND
  3. its ``name`` is NOT part of a NAME-COLLISION where ANY twin is referenced (two
     defs share a ``name``; if any one of them is referenced, BOTH are NOT-orphan —
     because the unresolved graph cannot tell which def the callee resolves to).

When in doubt → NOT-orphan. The finding is ``advisory=True`` (CC #6): it informs,
it does not, alone, block. HONEST limitation (documented in the SAME register as the
1.5 vacuous detector): the detector grounds REACHABILITY over an UNRESOLVED-name
graph — it can MISS an orphan a resolved graph would catch (LOW recall), but it does
NOT falsely accuse live code (HIGH precision is the asymmetric priority).
Requirement-traceability is NOT established in V1 (there is no V1 requirement graph —
that is the 2.6 "traceability not establishable" register); FR12's "no referencing
requirement" half is satisfied CONSERVATIVELY by the exclusion/entrypoint set, NOT by
inventing a requirement graph. A resolved call graph for higher recall is the deferred
V2 / Epic-6-depth work (DF-1-4-A names it).

Whole-index, not per-file (DN-WHOLE-INDEX)
------------------------------------------
Orphan detection is INHERENTLY cross-file — a def in file A is "not an orphan"
because file B references it. ``run`` consumes the WHOLE ``AstIndex`` (or the
``entries`` it derives the global callee-name set + the global name-collision set
from ONCE) in a single pass. It is a FINDING-ONLY detector: it produces NO coverage
``entries`` (orphan detection does not grade file depth — the 2.5 secret-detector
additive-findings, no-double-count pattern). A no-orphan repo yields an empty
``DetectorResult`` → the pipeline ledger + verdict are BYTE-IDENTICAL to pre-6.3.

Test area: ArgusAgent-ORPHAN (``TC-ArgusAgent-ORPHAN-001-NN`` — index from ``-01``).
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from argus.detectors.base import (
    DegradedCondition,
    DetectorResult,
    FindingDraft,
    build_recording,
)
from argus.index.ast_index import AstIndex, AstIndexEntry, Definition
from argus.ledger.recording import Recording

__all__ = [
    "RULE_ORPHAN_CODE",
    "ORPHAN_EXCLUSION_NAMES",
    "OrphanCodeError",
    "OrphanCodeDetector",
]

# The single rule-id vocabulary for this detector (frozen for 6.4 / 6.5).
RULE_ORPHAN_CODE = "orphan_code"

# The LOCKED exclusion set (the false-accusation moat — frozen for 6.5's clean
# controls). A def whose name is here is NEVER flagged an orphan even with no
# name-match caller, because the UNRESOLVED-name substrate cannot reason about its
# reachability (it is reached by the interpreter / a framework / a registry /
# dynamic dispatch the bare-callee edges cannot see). Dunders are matched
# STRUCTURALLY below (``__x__``) so the literal list need only carry the
# non-dunder framework/entrypoint/export hooks.
ORPHAN_EXCLUSION_NAMES: frozenset[str] = frozenset(
    {
        # ── unittest / test-harness entrypoints (called by the runner, not by name) ──
        "setUp",
        "tearDown",
        "setUpClass",
        "tearDownClass",
        "setUpModule",
        "tearDownModule",
        "asyncSetUp",
        "asyncTearDown",
        # ── pytest fixtures / hooks the collector invokes reflectively ──
        "pytest_configure",
        "pytest_collection_modifyitems",
        "pytest_addoption",
        "conftest",
        # ── common framework / lifecycle hooks reached by the framework, not a call ──
        "main",
        "handler",
        "lambda_handler",
        "setup",
        "teardown",
        "startup",
        "shutdown",
        "on_startup",
        "on_shutdown",
    }
)


class OrphanCodeError(ValueError):
    """Raised on a malformed argument to the detector (AR10 typed failure).

    A ``ValueError`` subclass localized to this module (mirroring
    ``SecretScanError`` / ``RecordingValidationError``). Its message names the failing
    argument only — it carries NO source bytes (NFR-S1).
    """


def _is_dunder(name: str) -> bool:
    """True iff *name* is a dunder (``__x__``) — a hook reached structurally.

    A dunder method (``__init__`` / ``__call__`` / ``__enter__`` / …) is invoked by
    the interpreter/protocol, not by a name-match call edge, so it is NEVER an
    orphan on the unresolved substrate (the conservative exclusion).
    """
    return len(name) >= 5 and name.startswith("__") and name.endswith("__")


def _is_test_entrypoint(name: str) -> bool:
    """True iff *name* is a ``test_*`` / ``test`` entrypoint (runner-invoked).

    A test function is collected + invoked by the test runner reflectively (never by
    a name-match call edge from another module), so it is NEVER an orphan.
    """
    return name == "test" or name.startswith("test_")


def _is_excluded(name: str) -> bool:
    """True iff *name* is on the conservative exclusion set (NOT-orphan, AC3).

    The union of: dunders (structural ``__x__``), test entrypoints (``test_*``), and
    the locked :data:`ORPHAN_EXCLUSION_NAMES` framework/export/lifecycle hooks. An
    excluded def is never flagged even with no establishable caller — the
    unresolved-name substrate cannot prove it dead.
    """
    return _is_dunder(name) or _is_test_entrypoint(name) or name in ORPHAN_EXCLUSION_NAMES


class OrphanCodeDetector:
    """PURE conservative orphan / dead-code detector (satisfies ``detectors.base.Detector``).

    ``run`` is a pure whole-index fold over the 1.4 ``AstIndex``: NO I/O, NO clock,
    NO LLM (zero-token), NO ``uuid4``/``random``, NO ``float`` field, NO
    set/dict-iteration-order reliance in any emitted value. A malformed / None /
    parse-failed entry degrades to a recorded :class:`DegradedCondition` or a
    NOT-orphan classification — it NEVER raises out of the pipeline (AR10). The
    finding is built via the EXISTING ``build_recording`` (FR13 locator-or-reject,
    content-derived id) and is ``advisory=True`` (CC #6).
    """

    rule_id = RULE_ORPHAN_CODE

    def run(
        self,
        *,
        index: AstIndex,
        coverage_envelope_slice: str | None = None,
    ) -> DetectorResult:
        """Flag conservatively-unreachable defs as advisory orphan findings (FR12).

        Consumes the WHOLE pre-built 1.4 ``AstIndex`` (the ``entries`` it derives the
        global callee-name set + the name-collision set from ONCE). For each
        ast-eligible entry's ``Definition`` it flags an orphan iff the def's ``name``
        appears in NO edge callee across the index AND it is not excluded AND it is
        not part of a referenced name-collision (DN-CONSERVATIVE). Emits an
        ``advisory=True`` ``orphan_code`` ``Recording`` via ``build_recording``
        (locator from the def's file + line span + ``ast_span`` — FR13). Produces NO
        coverage ``entries`` (finding-only — a no-orphan repo is byte-identical to
        pre-6.3). Findings are SORTED (file_path, start_line, name — AR11).

        Raises:
            OrphanCodeError: only on a structurally malformed argument (a non-
                ``AstIndex`` ``index``) — a typed failure, never a leak. A degraded
                PER-ENTRY shape is recorded, not raised (AR10).
        """
        if not isinstance(index, AstIndex):
            raise OrphanCodeError("index must be an AstIndex")

        entries = index.entries

        # ── ONE pass to derive the global name-match facts (DN-WHOLE-INDEX) ──
        # The set of every callee name referenced ANYWHERE (the unresolved-name
        # reachability universe) + a name → def-count histogram so a name-collision
        # (two defs share a name) can make BOTH conservative if any twin is referenced.
        referenced_names: set[str] = set()
        definition_name_counts: Counter[str] = Counter()
        degraded: list[DegradedCondition] = []

        for entry in entries:
            if not isinstance(entry, AstIndexEntry):
                # A malformed entry shape — record + skip, never crash (AR10).
                degraded.append(
                    DegradedCondition(file_path="<unknown>", reason="orphan_malformed_entry")
                )
                continue
            for edge in entry.edges:
                callee = getattr(edge, "callee", None)
                if isinstance(callee, str) and callee:
                    referenced_names.add(callee)
            if not entry.ast_eligible:
                # A non-Python / parse-failed entry carries no auditable defs to
                # classify — it is recorded by the 1.4 index already; nothing to do
                # here (no finding, no degraded — the per-file degrade is the 1.4
                # index's job; we simply do not analyze defs we do not have).
                continue
            for definition in entry.definitions:
                name = getattr(definition, "name", None)
                if not isinstance(name, str) or not name:
                    # A def with a None/empty name cannot be classified — record it
                    # (AR10) and treat it as NOT-orphan (never flag the unnameable).
                    degraded.append(
                        DegradedCondition(file_path=entry.file_path, reason="orphan_unnamed_definition")
                    )
                    continue
                definition_name_counts[name] += 1

        # ── Second pass: classify each named def (whole-index facts are now fixed) ──
        findings: list[Recording] = []
        for entry in entries:
            if not isinstance(entry, AstIndexEntry) or not entry.ast_eligible:
                continue
            for definition in entry.definitions:
                if not self._is_orphan(definition, referenced_names, definition_name_counts):
                    continue
                draft = FindingDraft(
                    file_path=entry.file_path,
                    start_line=definition.start_line,
                    end_line=definition.end_line,
                    ast_span=definition.ast_span,
                    rule_id=RULE_ORPHAN_CODE,
                    advisory=True,
                    coverage_envelope_slice=coverage_envelope_slice,
                )
                # FR13 locator-or-reject: a malformed span would raise inside
                # build_recording; a Definition's span is index-validated (>=1,
                # end>=start), so the locator is always buildable here.
                findings.append(
                    build_recording(draft, depth_supported=None, claim_present=False)
                )

        findings.sort(key=lambda f: (f.locators[0].file_path, f.locators[0].start_line, f.rule_id, f.recording_id))
        return DetectorResult(findings=tuple(findings), degraded=tuple(degraded))

    @staticmethod
    def _is_orphan(
        definition: Definition,
        referenced_names: set[str],
        definition_name_counts: Counter[str],
    ) -> bool:
        """The CONSERVATIVE orphan predicate (DN-CONSERVATIVE / AC3). PURE.

        Orphan iff: a function/class def whose ``name`` (a) is not referenced by any
        edge callee, (b) is not excluded, AND (c) is not part of a name-collision
        (>1 def shares the name → BOTH conservative, NOT-orphan — the DF-1-4-A
        unresolved-name guard). Any ambiguity → NOT-orphan.
        """
        name = getattr(definition, "name", None)
        if not isinstance(name, str) or not name:
            return False
        if definition.kind not in ("function", "class"):
            return False
        if name in referenced_names:
            return False
        if _is_excluded(name):
            return False
        # Name-collision guard: if two+ defs share this name, the unresolved-name
        # graph cannot tell which one a (hypothetical) callee would resolve to, so
        # NEITHER may be accused — conservative even when this particular twin has no
        # caller (RED against a naive per-def check that would false-flag it).
        if definition_name_counts.get(name, 0) > 1:
            return False
        return True


if TYPE_CHECKING:  # pragma: no cover - static conformance pin; TYPE_CHECKING is False at runtime
    # Story 18.4 / AC2 - the STATIC conformance pin. `mypy argus` is a blocking CI gate
    # and this line is what it checks: drop `rule_id`, retype it non-`str`, drop `run` or
    # regress its return type and THIS goes red. It lives inside `argus/` on purpose -
    # there is no [tool.mypy] section in this repository and CI runs `mypy argus` only, so
    # the same pin written under `tests/` would be enforced by nothing.
    from argus.detectors.base import Detector

    _DETECTOR_CONFORMANCE_PIN: Detector = OrphanCodeDetector()
