"""Detector ``Protocol`` + the locator-required ``Recording`` finding builder (PURE).

Drivers: ArgusAgent-FR-13 (every finding carries ≥1 verifiable locator or is rejected,
not emitted), ArgusAgent-FR-33-support / cross-cutting #6 (advisory-by-contract: the
finding carries the eligibility signal a downstream verdict gate (Story 1.6)
reads so a heuristic-only finding can never move the verdict to 🔴 on its own),
AR8 (PURE — the builder performs no I/O, no clock, no ``uuid4``/``random``, no
LLM), AR10 (typed failure — a locator-less finding is rejected via a typed error,
never minted; no bare ``except: pass``, no ``print()``).

Why this module exists
----------------------
Every ArgusAgent detector emits the SAME finding row — the Story 1.2 ``Recording`` —
and the SAME locator-or-reject discipline (FR13). This module owns that single
builder so a detector never reimplements finding construction or a parallel
finding model (§3.3 reuse-canonical). The ``Recording`` / ``Locator`` models are
reused VERBATIM; this module does NOT modify ``ledger/recording.py``.

Contract decisions locked here (frozen for downstream detectors)
----------------------------------------------------------------
- The detector ``Protocol`` is a ``typing.Protocol`` declaring the two members the
  shipped detectors actually share: a ``str`` ``rule_id`` and a callable ``run``
  returning a ``DetectorResult``. It deliberately does NOT describe ``run``'s
  parameters — the detectors take different keyword-only signatures on purpose, and
  the 1.5 ``run(self, *args: object, **kwargs: object)`` spelling was measured to make
  ``mypy`` REJECT all four of them. A concrete detector satisfies it structurally — no
  inheritance required — and every detector module carries a static conformance pin
  against it under ``if TYPE_CHECKING:``, so the blocking ``mypy argus`` gate is what
  enforces this bullet rather than prose (Story 18.4).
- ``DetectorResult`` is a frozen ``extra="forbid"`` pure model (the Story 1.1/1.2
  precedent): the per-file ``CoverageLedgerEntry`` candidates the detector graded
  via ``grade_entry``, the ``Recording`` findings, and the per-file DEGRADED
  conditions (AR10) the Story 1.7 pipeline folds. The detector does NOT assemble
  the whole ``CoverageLedger`` (that aggregation is the pipeline's job).
- The finding builder ``build_recording`` mints a 1.2 ``Recording`` from a
  ``FindingDraft``. The FR13 locator-or-reject rule is enforced at the DATA layer
  (the ``Recording`` raises ``RecordingValidationError`` on an empty ``locators``
  tuple); the builder SURFACES that — it never silently mints a locator-less
  finding and never swallows the rejection.
- The recording id is CONTENT-DERIVED (a sha256 over the canonical draft payload
  via the single Story 1.1 serializer) — NEVER ``uuid4`` / a counter / arrival
  order (AR4/AR11). Two hosts that flag the same finding mint the same id.
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from argus.ledger.coverage_ledger import CoverageDepth, CoverageLedgerEntry
from argus.ledger.recording import (
    Locator,
    Recording,
    RecordingValidationError,
)
from argus.store import canonical

__all__ = [
    "FindingDraft",
    "DegradedCondition",
    "DetectorResult",
    "Detector",
    "build_recording",
]


class FindingDraft(BaseModel):
    """A pre-validation finding description the builder turns into a ``Recording``.

    Frozen ``extra="forbid"`` (the Story 1.1/1.2 precedent). Its EIGHT fields are
    exactly the inputs the FR13 builder needs: ``file_path`` + the 1-based
    ``start_line``/``end_line`` span, an optional 1.4 ``Definition.ast_span`` token,
    the ``rule_id`` provenance, the advisory-by-contract flag, an optional
    ``cartridge_id``, and the ``coverage_envelope_slice`` reference.

    Two things this draft does NOT carry, stated because the 1.5 docstring claimed
    both and neither exists on the model (Story 18.4 item C, measured from
    ``FindingDraft.model_fields``):

    - **the supported coverage depth.** ``depth_supported`` is a keyword PARAMETER of
      :func:`build_recording`, never a draft field. It reaches the ``Recording``
      through the builder's signature, so a detector chooses it per finding at
      construction time rather than declaring it on the draft.
    - **the evidence the finding carries with it.** No evidence field exists on
      ``FindingDraft``, on ``DetectorResult`` or on the ten-field ``Recording``. The
      FR10 "carrying their evidence counts" gap is REPOSITORY-WIDE and OPEN: Story
      18.2 measured that ``Recording`` has no field that could hold a count and
      concluded that widening one detector in isolation is the wrong shape of repair.
      This docstring therefore states the absence; it does not add a field (DN-18-4-6).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_path: str = Field(..., description="File the finding refers to.")
    start_line: int = Field(..., ge=1, description="1-based inclusive start line (>= 1).")
    end_line: int = Field(..., ge=1, description="1-based inclusive end line (>= start_line).")
    ast_span: str | None = Field(
        default=None, description="Optional 1.4 Definition.ast_span token for Locator.ast_span."
    )
    rule_id: str = Field(..., description="Detector rule provenance id.")
    advisory: bool = Field(..., description="Advisory-by-contract flag (cross-cutting #6).")
    cartridge_id: str | None = Field(default=None, description="Optional defect-cartridge id.")
    coverage_envelope_slice: str | None = Field(
        default=None, description="Reference to the coverage-envelope slice this finding falls in."
    )


class DegradedCondition(BaseModel):
    """A per-file degraded outcome (AR10) — recorded, never a false flag / crash.

    An un-parseable / un-analyzable / non-test file routes here instead of being
    flagged vacuous. A later story (1.7) MAY mint a ``parse_failure``-style finding
    or a coverage downgrade from it; this V1 detector only RECORDS the condition.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_path: str = Field(..., description="File whose analysis degraded.")
    reason: str = Field(..., description="Degradation reason token (e.g. 'parse_failed').")


class DetectorResult(BaseModel):
    """The frozen pure result the Story 1.7 pipeline folds (AR8).

    ``entries`` are per-file ``CoverageLedgerEntry`` candidates the detector graded
    via ``grade_entry`` (the detector does NOT assemble the whole ``CoverageLedger``).
    ``findings`` are the 1.2 ``Recording`` rows. ``degraded`` are the AR10 recorded
    conditions. All tuples (deterministic, no set/dict-order reliance).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    entries: tuple[CoverageLedgerEntry, ...] = Field(
        default=(), description="Per-file coverage entries (graded via grade_entry)."
    )
    findings: tuple[Recording, ...] = Field(
        default=(), description="The 1.2 Recording findings emitted (each carries >=1 locator)."
    )
    degraded: tuple[DegradedCondition, ...] = Field(
        default=(), description="Per-file degraded conditions (AR10 recorded, not flagged)."
    )


class Detector(Protocol):
    """The detector contract — a ``rule_id`` and a pure ``run`` yielding a :class:`DetectorResult`.

    A concrete detector satisfies this structurally (``typing.Protocol``); no
    base-class inheritance is required. ``run`` MUST be pure (AR8): a function over
    recorded inputs (test source text + the Story 1.4 ``AstIndexEntry``), no I/O,
    no clock, no LLM, no ``uuid4``/``random``. (``ToolRunnerDetector`` is the one
    disclosed exception — see its module docstring, Story 2.6.)

    Why it does NOT describe ``run``'s parameters (Story 18.4)
    ---------------------------------------------------------
    The four shipped detectors take deliberately different keyword-only signatures;
    forcing a common one would be a worse design. The 1.5 declaration tried to admit
    them with ``run(self, *args: object, **kwargs: object)``, which does the OPPOSITE:
    an implementation must accept everything the protocol permits, and a keyword-only
    signature accepts no positional argument — so ``mypy`` REJECTED all four shipped
    detectors against it. The protocol was not unused, it was UNUSABLE. What the four
    genuinely share is a ``str`` ``rule_id`` and a callable ``run`` returning a
    ``DetectorResult``; that is what is declared here, and every detector module
    carries a static conformance pin against it under ``if TYPE_CHECKING:`` so the
    blocking ``mypy argus`` gate checks it.

    Both members are read-only properties BY MEASUREMENT, not by taste: a settable
    ``rule_id: str`` data member makes ``issubclass`` raise ``TypeError`` and the
    member invariant, and a settable ``run: Callable[...]`` attribute is rejected for
    all four with *"expected settable variable, got read-only attribute"*. The
    property spelling is the only one all four satisfy unedited, and it is already
    this package's idiom (``vacuous_test._HasFilePath``).

    ``@runtime_checkable`` is DELIBERATELY ABSENT, so ``isinstance``/``issubclass``
    against this protocol is a ``TypeError``, not a weak yes. The runtime check it
    used to offer was measured vacuous — it answers ``True`` for a class whose ``run``
    is the integer ``42`` on CPython 3.11, 3.12 and 3.13 alike — and its verdict is
    not even stable across the CI matrix (3.12 switched ``runtime_checkable`` from
    ``hasattr`` to ``inspect.getattr_static``, so a ``__getattr__``-provided member
    satisfies on 3.11 and does not on 3.12+). Restoring the decorator is a DECISION,
    not the repair of an omission: say why, and do not let it displace the static pins.
    """

    @property
    def rule_id(self) -> str: ...  # pragma: no cover - structural declaration

    @property
    def run(self) -> Callable[..., DetectorResult]: ...  # pragma: no cover - structural


def _recording_id(draft: FindingDraft) -> str:
    """Content-derived recording id: sha256 over the canonical draft (AR4/AR11).

    Uses the single Story 1.1 serializer so the id is byte-stable across hosts —
    NEVER ``uuid4`` / a counter / arrival order. The id covers the locating
    identity (file/span/rule/ast_span/advisory) so two distinct findings on the
    same file get distinct ids while a re-flag of the same finding is stable.
    """
    identity = {
        "file_path": draft.file_path,
        "start_line": draft.start_line,
        "end_line": draft.end_line,
        "ast_span": draft.ast_span,
        "rule_id": draft.rule_id,
        "advisory": draft.advisory,
        "cartridge_id": draft.cartridge_id,
    }
    digest = hashlib.sha256(canonical.dumps_bytes(identity)).hexdigest()
    return f"{draft.rule_id}:{digest}"


def build_recording(
    draft: FindingDraft,
    *,
    depth_supported: CoverageDepth | None = None,
    claim_present: bool = False,
) -> Recording:
    """Mint a 1.2 ``Recording`` from a ``FindingDraft`` (FR13 locator-or-reject).

    Builds exactly ONE verifiable ``Locator`` from the draft's file + line span +
    optional ``ast_span`` and reuses the 1.2 ``Recording`` VERBATIM. The
    locator-or-reject rule is enforced at the DATA layer — the ``Recording`` raises
    :class:`RecordingValidationError` on an empty ``locators`` tuple; this builder
    surfaces that (it constructs the locator first and would raise rather than mint
    a locator-less finding). PURE — no I/O, no clock, no LLM, no ``uuid4``.

    Raises:
        RecordingValidationError: if a verifiable locator cannot be supplied
            (FR13 — rejected, not emitted), or the line span is malformed.
    """
    try:
        locator = Locator(
            file_path=draft.file_path,
            start_line=draft.start_line,
            end_line=draft.end_line,
            ast_span=draft.ast_span,
        )
    except ValueError as exc:
        raise RecordingValidationError(
            f"cannot build a verifiable locator for a {draft.rule_id} finding "
            f"on '{draft.file_path}': {exc} (FR13 locator-or-reject)"
        ) from exc

    return Recording(
        recording_id=_recording_id(draft),
        rule_id=draft.rule_id,
        cartridge_id=draft.cartridge_id,
        advisory=draft.advisory,
        depth_supported=depth_supported,
        claim_present=claim_present,
        locators=(locator,),
        coverage_envelope_slice=draft.coverage_envelope_slice,
    )
