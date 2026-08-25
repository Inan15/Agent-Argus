"""Zero-token breadth-tool runner + tool-failure-AS-FINDING (impure shell / pure core).

Drivers: ArgusAgent-FR-14 (a tool failure OR an unestablishable-traceability condition
becomes a recorded FINDING rather than a crash — the central driver), ArgusAgent-NFR-C3
(deterministic, zero-LLM-token tools perform BREADTH so LLM spend is reserved for
depth — the cost-efficiency keystone), ArgusAgent-FR-5 (the fixed-enum coverage ledger —
this module is the FIRST PRODUCER of the ``tool_scanned_only`` state Story 2.1
documented + classified), ArgusAgent-NFR-R1 / AR10 (a tool / parse failure or an
unestablishable-traceability condition degrades to a recorded finding or a coverage
downgrade — NEVER an uncaught crash, a fabricated pass, or a silent skip),
ArgusAgent-FR-13 (every finding carries >=1 verifiable locator or is rejected — via the
1.5 ``build_recording``), ArgusAgent-NFR-D2 (deterministic, zero-LLM-token — the runner
calls NO LLM; the OUTCOME classification + finding build are pure), ArgusAgent-NFR-S1
(source / secret / api-key bytes — AND raw tool stderr / host paths — never appear
in ledgers, evidence, logs, traces, or any finding / degraded reason), AR1
(``radon`` is the already-installed / sanctioned V1 breadth tool; ``cloc`` /
linters / SAST are the OPTIONAL / best-effort family deferred), AR4 (single
canonical serializer; metrics as ``int`` / ``Fraction``, NEVER ``float``;
content-derived ids; no clock / uuid / random / iteration-order in any ``.argus/``
write path), AR8 (pure / impure separation — the tool INVOCATION + output read are
the impure injectable shell; the OUTCOME classification + finding / grade build +
metric fold are PURE), AR11 (``.argus/`` finding filenames content-derived),
ArgusAgent-NFR-M1 (<=1200-line files), ArgusAgent-NFR-M2 (frozen, additive-only contracts).

The pure / impure split (the master rule, AR8)
----------------------------------------------
The 1.5 ``Detector`` protocol docstring says ``run`` "MUST be pure". This detector
is the FIRST whose CORE requires impurity (running an external metric tool). The
two concerns are SEPARATED:

- an IMPURE, INJECTED invocation shell — a ``ToolInvoker`` callable that takes
  ``(file_path, source)`` and returns a captured :class:`ToolInvocation` (or raises).
  The default :func:`radon_invoker` calls the ``radon`` **library API** in-process
  (``radon.raw.analyze`` for LOC, ``radon.complexity.cc_visit`` for cyclomatic
  complexity) — NO subprocess, NO shell, NO ``timeout``/locale risk. A library call
  can still raise (a syntax error, a non-ASCII / unparseable file), so the
  failure-as-finding discipline + the injection seam STILL apply. Tests inject a
  fake invoker (the AR8 testability seam AND the AC6 failure-injection mechanism)
  WITHOUT spawning anything;
- a PURE classifier (:meth:`ToolRunnerDetector.classify_outcomes`) that maps the
  captured per-file outcomes -> a frozen :class:`~argus.detectors.base.DetectorResult`
  (``tool_scanned_only`` entries + ``tool_failure`` / ``traceability_not_establishable``
  findings + degraded conditions). The classifier has all the determinism / no-float
  / no-clock guarantees.

V1 tool set (LOCKED) + the family deferred
------------------------------------------
V1 breadth = ``radon`` ONLY (library API; already installed + sanctioned, AR1). The
breadth metrics produced are raw LOC (``radon.raw.analyze`` ``loc``) and aggregate
cyclomatic complexity (sum of ``radon.complexity.cc_visit`` block complexities). The
architecture names ``cloc`` / linters / SAST as the breadth-tool FAMILY; they are
OPTIONAL / best-effort and deferred to a future story (recorded as such — not built
here). A future tool that shells out MUST honour the AC7 safe-bounded-subprocess
rules (``shell=False``, explicit arg list, hard ``timeout=``, explicit UTF-8 decode
``errors="replace"``) — the injected-invoker seam stays the test mechanism.

Tool OUTPUT is hostile — producer-side redaction extended to it (NFR-S1, keystone)
-----------------------------------------------------------------------------------
A tool's error text / output can echo source lines, secret bytes, or absolute host
paths. Raw tool output is NEVER placed into a :class:`ToolRunOutcome`, a
``tool_failure`` finding, a ``DegradedCondition.reason``, a log line, or a raised
exception message. Only a fixed reason TOKEN (``radon_crashed`` / ``radon_timed_out``
/ ``radon_unavailable`` / ``radon_unparseable``) + bounded non-secret ``int`` metrics
survive. The structural guarantee (the 2.5 precedent): :class:`ToolRunOutcome` has
**NO** raw-output field — a value cannot leak if there is nowhere to store it.

The ``tool_scanned_only`` emission rule + no-double-count (LOCKED — AC5)
-----------------------------------------------------------------------
``tool_scanned_only`` is minted via the 2.1 single classifier
(``classify_depth(DepthEvidence(kind=EvidenceKind.TOOL_BREADTH_ONLY))`` -> the 1.2
``grade_entry``) — the enum member is NOT minted ad hoc and NO state is added. It is
DENOMINATOR-only: the 1.6 deep-% numerator counts ONLY ``audited_deep`` (FR8,
UNCHANGED), so a breadth-scanned file can never satisfy a deep gate (tools do
breadth, tokens do depth — the NFR-C3 cost split). The no-double-count rule: the
runner grades ``tool_scanned_only`` ONLY for files the breadth tool COVERED that
were NOT already graded by the depth / shallow path. The caller passes the set of
``already_graded_paths``; a file in that set is skipped by the breadth channel even
when the tool covered it. A run producing no NEW ``tool_scanned_only`` files is
ledger + verdict byte-identical to the pre-2.6 run (the regression-safe path).

Unestablishable-traceability V1 definition (LOCKED — AC3)
---------------------------------------------------------
The FR14 second clause at a Tier-A grade: when the breadth tool ran CLEAN over a
covered file that was NOT otherwise depth-graded but produced NO usable signal (zero
LOC AND zero complexity — an empty / signal-less unit), no breadth grade can be
earned, so the condition is recorded as a ``traceability_not_establishable`` finding
rather than fabricating a ``tool_scanned_only`` grade. The full requirement<->code
traceability graph (orphan / dead-code) is the Epic-6 orphan detector (FR12) and is
NOT built here — this records the CONDITION as a finding.

Advisory-by-contract (LOCKED — V1)
----------------------------------
Both finding types are ``advisory=True``, ``depth_supported=None`` in V1: a tool
failure / unestablishable-traceability condition is an HONESTY signal, not a code
defect, so it never moves the 1.6 verdict to blocking on its own (the frozen 1.6
gate is UNTOUCHED). Promoting either to verdict-blocking is a deferred future story.
"""

from __future__ import annotations

import enum
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from argus.detectors.base import (
    DegradedCondition,
    DetectorResult,
    FindingDraft,
    build_recording,
)
from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedgerEntry,
    grade_entry,
)
from argus.ledger.depth_semantics import (
    DepthEvidence,
    EvidenceKind,
    classify_depth,
)
from argus.ledger.recording import Recording

__all__ = [
    "TOOL_RUN_SCHEMA_VERSION",
    "RULE_TOOL_FAILURE",
    "RULE_TRACEABILITY_NOT_ESTABLISHABLE",
    "V1_BREADTH_TOOL_ID",
    "ToolOutcome",
    "ToolRunnerError",
    "ToolRunOutcome",
    "ToolInvocation",
    "ToolInvoker",
    "radon_invoker",
    "ToolRunnerDetector",
]

# Single localized source for this contract's schema version (additive-only).
TOOL_RUN_SCHEMA_VERSION = "1"

# The frozen rule-id vocabulary for this runner's two finding types.
RULE_TOOL_FAILURE = "tool_failure"
RULE_TRACEABILITY_NOT_ESTABLISHABLE = "traceability_not_establishable"

# V1 breadth tool (LOCKED — AR1; cloc/linters/SAST are the deferred family).
V1_BREADTH_TOOL_ID = "radon"

# Sanitized failure-reason TOKENS (NEVER raw tool output — NFR-S1). Mapped from a
# closed ToolOutcome so a leaky free-form reason can never be produced.
_REASON_TOKEN_BY_OUTCOME: dict["ToolOutcome", str] = {}


class ToolOutcome(str, enum.Enum):
    """Closed per-file breadth-tool outcome (the 1.2/1.6 closed-enum precedent).

    ``str``-valued so the token serializes verbatim. Exactly five members:

    - ``OK`` — the tool ran clean and produced breadth metrics for the file.
    - ``UNAVAILABLE`` — the tool binary / import is missing (no run possible).
    - ``CRASHED`` — the tool raised / exited non-zero on the file.
    - ``TIMED_OUT`` — the tool exceeded a bounded, deterministic timeout.
    - ``UNPARSEABLE`` — the tool's output (or the file) could not be parsed
      (a syntax error / a non-ASCII-mangled / undecodable unit).
    """

    OK = "ok"
    UNAVAILABLE = "unavailable"
    CRASHED = "crashed"
    TIMED_OUT = "timed_out"
    UNPARSEABLE = "unparseable"


_REASON_TOKEN_BY_OUTCOME = {
    ToolOutcome.UNAVAILABLE: "radon_unavailable",
    ToolOutcome.CRASHED: "radon_crashed",
    ToolOutcome.TIMED_OUT: "radon_timed_out",
    ToolOutcome.UNPARSEABLE: "radon_unparseable",
}


class ToolRunnerError(ValueError):
    """Raised on a MALFORMED ARGUMENT to the runner (AR10 typed failure).

    A ``ValueError`` subclass localized to this module (mirroring ``SecretScanError``
    / ``RecordingValidationError`` / ``RepoIntakeError`` / ``PartitionerError``). Its
    message names the failing argument only — it NEVER contains raw tool output,
    source bytes, a secret, or an absolute host path (NFR-S1). A tool FAILURE is NOT
    raised — it degrades to a ``tool_failure`` finding; only a programmer-supplied
    bad argument raises here.
    """


class ToolRunOutcome(BaseModel):
    """Frozen, redaction-safe per-file breadth outcome (NFR-S1 / NFR-M2 / AR4).

    Mirrors the 2.5 ``SecretFindingEvidence`` / 1.5 ``VacuousTestScore`` precedent:
    detector evidence on a separate frozen model carrying ONLY redaction-safe
    metadata. ``frozen=True, extra="forbid"``; all metrics are ``int`` (radon's
    natural ``float`` complexity is summed over integer block complexities, so no
    quantization is needed — NEVER a ``float`` field, the 1.1 serializer rejects it).

    There is **NO** raw-stdout / raw-stderr / source-text field on this model AT ALL
    — the ABSENCE of the field is the structural redaction guarantee (the 2.5 "no
    value field" precedent). ``failure_reason`` is a CONSTANT TOKEN drawn from a
    closed map (never free-form, never raw output).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default=TOOL_RUN_SCHEMA_VERSION,
        description="ToolRunOutcome schema version (additive-only).",
    )
    tool_id: str = Field(..., description="The breadth tool id (e.g. 'radon').")
    file_path: str = Field(..., description="Repo-relative POSIX path the outcome refers to.")
    outcome: ToolOutcome = Field(..., description="Closed per-file outcome enum.")
    total_loc: int = Field(default=0, ge=0, description="Lines of code (radon raw; 0 unless OK).")
    total_complexity: int = Field(
        default=0, ge=0, description="Aggregate cyclomatic complexity (radon cc; 0 unless OK)."
    )
    failure_reason: str | None = Field(
        default=None,
        description="Sanitized constant reason TOKEN on failure (never raw output); None when OK.",
    )


class ToolInvocation(BaseModel):
    """A captured per-file invocation outcome the IMPURE shell hands the PURE core.

    The injectable seam's return type (AR8). ``frozen=True, extra="forbid"``; carries
    ONLY redaction-safe captured data — a closed :class:`ToolOutcome` + bounded
    ``int`` metrics. There is NO raw-output field: even the impure shell sanitizes at
    the boundary, so raw tool bytes never reach the pure classifier (NFR-S1).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_path: str = Field(..., description="Repo-relative POSIX path the invocation covered.")
    outcome: ToolOutcome = Field(..., description="Closed per-file outcome enum.")
    total_loc: int = Field(default=0, ge=0, description="Lines of code (0 unless OK).")
    total_complexity: int = Field(
        default=0, ge=0, description="Aggregate cyclomatic complexity (0 unless OK)."
    )


# The injected impure-shell seam: (file_path, source) -> a captured invocation.
# The default radon_invoker calls the radon library API; tests inject a fake.
ToolInvoker = Callable[[str, str], ToolInvocation]


def radon_invoker(file_path: str, source: str) -> ToolInvocation:
    """Default IMPURE invoker — the ``radon`` library API over one file (AR1/AR8).

    Computes raw LOC (``radon.raw.analyze``) + aggregate cyclomatic complexity
    (``radon.complexity.cc_visit``) in-process (no subprocess / shell / timeout /
    locale risk). Any failure is CAUGHT and mapped to a closed :class:`ToolOutcome`
    — it NEVER raises out (AR10): a missing ``radon`` import -> ``UNAVAILABLE``; a
    ``SyntaxError`` / parse failure -> ``UNPARSEABLE``; any other tool error ->
    ``CRASHED``. The raw error text is DROPPED here at the boundary (NFR-S1) — the
    returned :class:`ToolInvocation` carries only the closed outcome + ``int`` metrics.
    """
    try:
        from radon.complexity import cc_visit  # type: ignore[import-untyped]
        from radon.raw import analyze  # type: ignore[import-untyped]
    except Exception:  # noqa: BLE001 — import missing -> unavailable, never raise (AR10)
        return ToolInvocation(file_path=file_path, outcome=ToolOutcome.UNAVAILABLE)

    try:
        raw = analyze(source)
        blocks = cc_visit(source)
    except SyntaxError:
        return ToolInvocation(file_path=file_path, outcome=ToolOutcome.UNPARSEABLE)
    except Exception:  # noqa: BLE001 — any other tool error -> crashed, never raise / leak
        return ToolInvocation(file_path=file_path, outcome=ToolOutcome.CRASHED)

    total_complexity = sum(int(getattr(block, "complexity", 0)) for block in blocks)
    return ToolInvocation(
        file_path=file_path,
        outcome=ToolOutcome.OK,
        total_loc=int(getattr(raw, "loc", 0)),
        total_complexity=total_complexity,
    )


class ToolRunnerDetector:
    """Zero-token breadth runner: impure injected invoker + PURE outcome classifier.

    The impure invocation is the injected :class:`ToolInvoker` (default
    :func:`radon_invoker`); the OUTCOME classification + finding / grade build are
    PURE (no clock, no ``uuid``/``random``, no LLM, no network, no set/dict-order
    reliance). Satisfies the ``detectors.base.Detector`` protocol structurally via
    :meth:`run`.
    """

    rule_id = RULE_TOOL_FAILURE

    def __init__(self, *, tool_invoker: ToolInvoker | None = None) -> None:
        self._invoker: ToolInvoker = tool_invoker if tool_invoker is not None else radon_invoker

    def run(
        self,
        *,
        targets: Sequence[tuple[str, str]],
        already_graded_paths: Sequence[str] = (),
    ) -> DetectorResult:
        """Run breadth over *targets* and classify the outcomes (AR8 shell + pure core).

        *targets* is a sequence of ``(file_path, source)`` pairs (the impure source
        read is the caller's job — the 1.7 pipeline). For each target the injected
        invoker is called; a raising invoker is CAUGHT and mapped to ``CRASHED`` (the
        runner never lets a tool failure escape — AR10). The captured invocations are
        then handed to the PURE :meth:`classify_outcomes`.

        Raises :class:`ToolRunnerError` (AR10) ONLY on a malformed argument — never on
        a tool failure (which degrades to a ``tool_failure`` finding).
        """
        if not isinstance(targets, Sequence) or isinstance(targets, (str, bytes)):
            raise ToolRunnerError("targets must be a sequence of (file_path, source) pairs")

        invocations: list[ToolInvocation] = []
        for target in targets:
            if (
                not isinstance(target, tuple)
                or len(target) != 2
                or not isinstance(target[0], str)
                or not target[0]
                or not isinstance(target[1], str)
            ):
                raise ToolRunnerError(
                    "each target must be a (non-empty-str file_path, str source) pair"
                )
            file_path, source = target
            try:
                invocation = self._invoker(file_path, source)
            except Exception:  # noqa: BLE001 — a raising invoker is a CRASH, never a leak (AR10)
                invocation = ToolInvocation(file_path=file_path, outcome=ToolOutcome.CRASHED)
            if not isinstance(invocation, ToolInvocation):
                # A misbehaving invoker that returns a non-invocation is a crash, not a leak.
                invocation = ToolInvocation(file_path=file_path, outcome=ToolOutcome.CRASHED)
            invocations.append(invocation)

        return self.classify_outcomes(
            invocations, already_graded_paths=already_graded_paths
        )

    def classify_outcomes(
        self,
        invocations: Sequence[ToolInvocation],
        *,
        already_graded_paths: Sequence[str] = (),
    ) -> DetectorResult:
        """PURE: captured invocations -> a frozen :class:`DetectorResult` (AR8).

        Deterministic — same invocations -> same result (sorted by ``file_path``; no
        iteration-order reliance). For each invocation:

        - already-graded file -> skipped by the breadth channel (no double-count, AC5);
        - ``OK`` with usable signal (LOC or complexity > 0) -> a ``tool_scanned_only``
          entry via the 2.1 ``classify_depth`` / 1.2 ``grade_entry`` (denominator-only);
        - ``OK`` with NO usable signal -> a ``traceability_not_establishable`` finding
          + a recorded ``skipped`` entry (examined-but-ungradable — never fabricated
          as covered);
        - any failure outcome -> a ``tool_failure`` finding (sanitized reason token) +
          a recorded ``skipped`` entry (downgrade — the tool did not scan the file).

        No raw output enters any field; every reason is a closed TOKEN (NFR-S1).
        """
        if not isinstance(invocations, Sequence) or isinstance(invocations, (str, bytes)):
            raise ToolRunnerError("invocations must be a sequence of ToolInvocation")
        for invocation in invocations:
            if not isinstance(invocation, ToolInvocation):
                # AR10 typed failure — never let a bad element raise a raw
                # AttributeError out of the sort/iteration below (no leak).
                raise ToolRunnerError("each invocation must be a ToolInvocation")

        already_graded = frozenset(already_graded_paths)

        entries: list[CoverageLedgerEntry] = []
        findings: list[Recording] = []
        degraded: list[DegradedCondition] = []

        for invocation in sorted(invocations, key=lambda inv: inv.file_path):
            rel = invocation.file_path
            if rel in already_graded:
                # The depth / shallow path already graded this file — the breadth
                # channel must not re-grade it (no double-count, AC5 keystone).
                continue

            if invocation.outcome is ToolOutcome.OK:
                if invocation.total_loc > 0 or invocation.total_complexity > 0:
                    depth = classify_depth(
                        DepthEvidence(kind=EvidenceKind.TOOL_BREADTH_ONLY)
                    )
                    entries.append(
                        grade_entry(
                            file_path=rel,
                            proposed_depth=depth,
                            claim_present=False,
                        )
                    )
                else:
                    # Ran clean but no usable signal — FR14 second clause (AC3).
                    findings.append(
                        self._finding(rel, RULE_TRACEABILITY_NOT_ESTABLISHABLE)
                    )
                    entries.append(
                        grade_entry(
                            file_path=rel,
                            proposed_depth=CoverageDepth.SKIPPED,
                            claim_present=False,
                        )
                    )
                continue

            # A failure outcome (UNAVAILABLE / CRASHED / TIMED_OUT / UNPARSEABLE):
            # a recorded tool_failure finding + a coverage downgrade (AC2 keystone).
            findings.append(self._finding(rel, RULE_TOOL_FAILURE))
            degraded.append(
                DegradedCondition(
                    file_path=rel,
                    reason=_REASON_TOKEN_BY_OUTCOME[invocation.outcome],
                )
            )
            entries.append(
                grade_entry(
                    file_path=rel,
                    proposed_depth=CoverageDepth.SKIPPED,
                    claim_present=False,
                )
            )

        return DetectorResult(
            entries=tuple(entries),
            findings=tuple(findings),
            degraded=tuple(degraded),
        )

    @staticmethod
    def _finding(file_path: str, rule_id: str) -> Recording:
        """Mint a repo-anchored advisory finding via the 1.5 ``build_recording`` (FR13).

        A tool failure / unestablishable-traceability condition is repo / file-scoped,
        not span-scoped, so the locator anchors the covered file at line 1 (the FR13
        non-empty-locator contract is satisfied). ``advisory=True``,
        ``depth_supported=None`` (V1 advisory-by-contract — the frozen 1.6 gate is
        untouched). No raw output enters the draft.
        """
        draft = FindingDraft(
            file_path=file_path,
            start_line=1,
            end_line=1,
            rule_id=rule_id,
            advisory=True,
        )
        return build_recording(draft, depth_supported=None, claim_present=False)


if TYPE_CHECKING:  # pragma: no cover - static conformance pin; TYPE_CHECKING is False at runtime
    # Story 18.4 / AC2 - the STATIC conformance pin. `mypy argus` is a blocking CI gate
    # and this line is what it checks: drop `rule_id`, retype it non-`str`, drop `run` or
    # regress its return type and THIS goes red. It lives inside `argus/` on purpose -
    # there is no [tool.mypy] section in this repository and CI runs `mypy argus` only, so
    # the same pin written under `tests/` would be enforced by nothing.
    from argus.detectors.base import Detector

    _DETECTOR_CONFORMANCE_PIN: Detector = ToolRunnerDetector()
