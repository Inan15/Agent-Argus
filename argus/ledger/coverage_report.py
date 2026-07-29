"""PURE readable per-file coverage-ledger surface — FR9 anti-black-box render.

Drivers: ArgusAgent-FR-9 (an operator can read EXACTLY which files were examined deeply,
shallowly, tool-scanned, inferred, or skipped — and the evidence that justified
each — the central inspectability driver), ArgusAgent-FR-5 (renders the fixed-enum 1.2
coverage ledger — five states, no sixth), ArgusAgent-NFR-S1 (no source/secret/absolute-
host-path bytes in the rendered surface — paths + depth tokens + claim flags +
opaque recording-id strings + counts ONLY), ArgusAgent-NFR-D2 (deterministic, zero-LLM-
token — a pure render over recorded data), ArgusAgent-NFR-P1 (byte-identical rendering
across hosts/runs for the same ledger), ArgusAgent-NFR-M2 (frozen, additive-only
contracts — localized ``schema_version``), AR4 (no ``float``; ratios are exact
``Fraction``; the single 1.1 canonical serializer; no clock/uuid/random/iteration-
order in any rendered output), AR8 (PURE — no I/O, no clock, no LLM; the impure
caller does the stdout write / ``.argus/`` persist), AR10 (typed failure — a
malformed input raises a localized ``ValueError`` subclass, never a silent coerce /
bare ``except: pass`` / ``print()`` in library code), AR9 (headless / no web
surface — a developer-readable text/JSON artifact, NOT a UI).

Why this module exists
----------------------
The 1.2 ``CoverageLedger`` carries every fact this surface needs (per-file
``file_path`` + ``depth`` + ``claim_present`` + ``recording_ids``, plus the pure
aggregate accessors ``counts_by_depth``/``deep_count``/``total``). What was MISSING
is the FR9 *readable surface* — a deterministic, byte-stable text/JSON rendering an
Engineering Lead can read to answer "how much did ArgusAgent actually look at, and why"
WITHOUT needing the verdict. This module is that render. It is a RENDER story, not
a data-model story: it adds NO field to the 1.2 ledger, modifies NO accessor, and
re-implements NO arithmetic — it READS the ledger and the 1.6 deep-% form.

Contract decisions LOCKED here (frozen for downstream — additive-only, NFR-M2)
------------------------------------------------------------------------------
- **Module placement** — ``ledger/coverage_report.py`` (cohesive with the 1.2
  ledger it renders; the architecture maps FR9 to the ledger layer). NOT a
  ``verdict/``-adjacent module (this renders the LEDGER, not the verdict).
- **Aggregate model = frozen ``DepthAggregate``** (``frozen=True, extra="forbid"``,
  the 1.1/1.2/1.6/2.1 precedent), carrying ``counts_by_depth: dict[CoverageDepth,
  int]`` (zero-filled, all five members), ``total: int``, ``deep_count: int``,
  ``deep_ratio: Fraction`` (== the 1.6 gate's ``Fraction(deep_count, total)``,
  ``Fraction(0,1)`` at ``total==0``), and ``percentages: dict[CoverageDepth,
  Fraction]`` (per-depth ``Fraction(count, total)``). NEVER a ``float`` (AR4).
- **Report model = frozen ``CoverageReport``** carrying ``schema_version`` +
  ``entries: tuple[CoverageLedgerEntry, ...]`` (the already-``file_path``-sorted
  1.2 entries verbatim) + the ``DepthAggregate``.
- **Deep-% AGREEMENT with the gate (reuse, not re-derive)** — ``deep_ratio`` is the
  exact ``Fraction(deep_count, total)`` arithmetic the 1.6 ``evaluate_verdict``
  uses (``Fraction(0,1)`` at ``total==0``), so the surfaced deep-% AGREES with the
  gate's ``deep_ratio``. A cross-check test pins this. No second formula.
- **Render API = three pure functions** + a dispatcher: ``build_coverage_report``,
  ``render_text``, ``render_json``, and ``render(ledger, *, fmt=...)`` over the
  supported set ``{"text", "json"}``. An unsupported ``fmt`` raises
  :class:`CoverageReportError` (AR10). Every function RETURNS a string / frozen
  model — none ``print()``s or ``open()``s (the impure caller persists).
- **Textual format (FROZEN markdown)** — a per-file table with columns
  ``file_path | depth | claim_present | recording_ids`` (one row per entry, in the
  ledger's sorted order), then an aggregate block: ``total``, ``deep_count``, the
  deep-% as the exact ``"num/den"`` fraction, and a per-depth count + percentage
  line for EVERY one of the five members (zero-filled, never omitted). The
  percentage is rendered as the EXACT fraction's ``"num/den"`` string — NEVER
  ``float(frac)*100`` (the AR4 byte-diff landmine).
- **JSON payload (FROZEN additive-only) routed THROUGH ``store/canonical.dumps``** —
  ``{"schema_version", "entries": [{"file_path","depth","claim_present",
  "recording_ids"}], "aggregate": {"total","deep_count","deep_ratio",
  "counts_by_depth","percentages"}}``. ``Fraction`` leaves are handed LIVE to the
  1.1 serializer so its frozen ``"num/den"`` encoding applies (NO second
  ``json.dumps`` — the committed AST gate forbids it). ``ensure_ascii=False`` so a
  non-ASCII ``file_path`` round-trips verbatim (AI-E1-1).
- **Typed error = :class:`CoverageReportError`** (a ``ValueError`` subclass
  localized to this module, mirroring ``RecordingValidationError`` /
  ``CanonicalSerializationError`` / ``DepthSemanticsError``).
- **Pipeline/cli seam (AC5 Task 5) = OPTION (a) — pure-library-only.** The render
  is a pure library function consumed by tests + a future story; NO additive
  ``cli.py``/``pipeline.py`` stdout/persist call is wired in this story (minimal
  scope; recommended default). The existing 1.7 summary line + exit-code wire
  contract are therefore untouched by construction.

Secret-safety by construction (NFR-S1)
--------------------------------------
The ``CoverageLedger`` holds NO source/secret bytes (only paths + depth tokens +
claim flags + opaque recording-id strings). This render NEVER reads a source file
and NEVER embeds finding bodies / source excerpts / secret values / an absolute
host path — it operates PURELY on the in-memory ledger. The Epic-4 containment
property suite later enforces this mechanically; this story is the producer-side
guarantee.

PURE (AR8): no filesystem I/O, no clock read, no ``uuid4``/``random``/
``os.getpid()``, no LLM/network, no dict/set-iteration-order reliance (per-depth
output iterates the closed ``CoverageDepth`` enum in its fixed declaration order;
entries iterate the already-sorted ``ledger.entries``). Imports ONLY the 1.2 ledger
models + the 1.1 serializer. Joins the import-isolation ``_MODULES_UNDER_GUARD``
gate.
"""

from __future__ import annotations

from fractions import Fraction

from pydantic import BaseModel, ConfigDict, Field

from argus.store import canonical
from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    CoverageLedgerEntry,
)

__all__ = [
    "COVERAGE_REPORT_SCHEMA_VERSION",
    "SUPPORTED_FORMATS",
    "CoverageReportError",
    "DepthAggregate",
    "CoverageReport",
    "build_depth_aggregate",
    "build_coverage_report",
    "render_text",
    "render_json",
    "render",
]

# Single localized source for this contract's schema version (additive-only,
# NFR-M2; part of the rendered/JSON payload).
COVERAGE_REPORT_SCHEMA_VERSION = "1"

# The supported render-format selectors for :func:`render` (AR10 — an unsupported
# selector raises CoverageReportError, never a silent default).
SUPPORTED_FORMATS: tuple[str, ...] = ("text", "json")


class CoverageReportError(ValueError):
    """Raised on a malformed render input (AR10).

    A ``ValueError`` subclass localized to this module (mirroring
    ``ledger.recording.RecordingValidationError`` /
    ``store.canonical.CanonicalSerializationError`` /
    ``ledger.depth_semantics.DepthSemanticsError``) — the typed failure for a
    non-``CoverageLedger`` argument or an unsupported render-format selector.
    NEVER a silent coerce / bare ``except: pass`` / ``print()`` in library code.
    """


class DepthAggregate(BaseModel):
    """Frozen per-depth aggregate over a coverage ledger (FR9/AR4; NEVER float).

    ``frozen=True, extra="forbid"`` (the 1.1 ``Envelope`` / 1.2 ``Recording`` /
    1.6 ``AuditVerdict`` / 2.1 ``DepthEvidence`` precedent): an unknown field on
    read-back is a typed ``ValidationError``. Every ratio is an exact ``Fraction``
    (the 1.1 serializer rejects ``float``); counts are ``int``. ``deep_ratio`` is
    the SAME ``Fraction(deep_count, total)`` the 1.6 gate uses — reuse, not a
    second formula.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    counts_by_depth: dict[CoverageDepth, int] = Field(
        ..., description="Per-depth entry counts (reuse of CoverageLedger.counts_by_depth())."
    )
    total: int = Field(..., ge=0, description="Total ledger entries (the deep-% denominator).")
    deep_count: int = Field(..., ge=0, description="Number of audited_deep entries (the numerator).")
    deep_ratio: Fraction = Field(
        ...,
        description="audited_deep / total as an exact Fraction (== the 1.6 gate's deep_ratio).",
    )
    percentages: dict[CoverageDepth, Fraction] = Field(
        ..., description="Per-depth count/total as an exact Fraction (NEVER float, AR4)."
    )


class CoverageReport(BaseModel):
    """Frozen readable coverage-report model — per-file entries + the aggregate.

    ``frozen=True, extra="forbid"`` (the project precedent). ``entries`` is the
    1.2 ``CoverageLedger.entries`` tuple verbatim (already ``file_path``-sorted —
    the render introduces NO re-sort that diverges from it). A localized
    ``schema_version`` (additive-only, NFR-M2). PURE construction — no I/O, no
    clock, no ``float``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default=COVERAGE_REPORT_SCHEMA_VERSION,
        description="Coverage-report schema version (additive-only).",
    )
    entries: tuple[CoverageLedgerEntry, ...] = Field(
        default=(), description="Per-file entries verbatim from the 1.2 ledger (sorted order)."
    )
    aggregate: DepthAggregate = Field(..., description="The per-depth counts + exact-Fraction ratios.")


def _require_ledger(ledger: object) -> CoverageLedger:
    """Return ``ledger`` as a ``CoverageLedger`` or raise the typed error (AR10)."""
    if not isinstance(ledger, CoverageLedger):
        raise CoverageReportError(
            f"build_coverage_report requires a CoverageLedger, got {type(ledger)!r}"
        )
    return ledger


def build_depth_aggregate(ledger: CoverageLedger) -> DepthAggregate:
    """Build the per-depth aggregate from a ledger (PURE, AC2).

    Reuses the 1.2 ``counts_by_depth()``/``deep_count()``/``total()`` accessors and
    the 1.6 gate's exact ``Fraction(deep_count, total)`` deep-% (``Fraction(0,1)``
    at ``total==0``) — so the surfaced deep-% AGREES with
    ``evaluate_verdict(ledger).deep_ratio`` (reuse, NOT a divergent formula). Each
    per-depth percentage is the exact ``Fraction(count, total)`` (``Fraction(0,1)``
    at ``total==0``). NEVER a ``float`` (AR4).
    """
    ledger = _require_ledger(ledger)
    counts = ledger.counts_by_depth()
    total = ledger.total()
    deep = ledger.deep_count()
    deep_ratio = Fraction(deep, total) if total > 0 else Fraction(0, 1)
    percentages = {
        depth: (Fraction(counts[depth], total) if total > 0 else Fraction(0, 1))
        for depth in CoverageDepth
    }
    return DepthAggregate(
        counts_by_depth=counts,
        total=total,
        deep_count=deep,
        deep_ratio=deep_ratio,
        percentages=percentages,
    )


def build_coverage_report(ledger: CoverageLedger) -> CoverageReport:
    """Build the frozen :class:`CoverageReport` from a 1.2 ledger (PURE, AC1/AC2).

    The entries are the ledger's already-``file_path``-sorted tuple verbatim (no
    re-sort, no dict/set iteration-order reliance — AR4); the aggregate is
    :func:`build_depth_aggregate`. Raises :class:`CoverageReportError` on a
    non-``CoverageLedger`` argument (AR10).
    """
    ledger = _require_ledger(ledger)
    return CoverageReport(
        entries=ledger.entries,
        aggregate=build_depth_aggregate(ledger),
    )


def _fraction_str(value: Fraction) -> str:
    """Render an exact ``Fraction`` as its ``"num/den"`` string (AR4 — never float)."""
    return f"{value.numerator}/{value.denominator}"


def _recording_ids_str(recording_ids: tuple[str, ...]) -> str:
    """Render opaque recording ids for the textual table (empty → ``[]``, never omitted)."""
    if not recording_ids:
        return "[]"
    return "[" + ", ".join(recording_ids) + "]"


def render_text(report: CoverageReport) -> str:
    """Render the report as a deterministic markdown surface (PURE, AC1/AC2/AC3).

    Locked format: a per-file table (``file_path | depth | claim_present |
    recording_ids``, one row per entry in the ledger's sorted order — the empty
    ``recording_ids`` rendered as ``[]``, never omitted), then an aggregate block
    (``total``, ``deep_count``, the deep-% as the exact ``"num/den"`` fraction, and
    a per-depth count + percentage line for EVERY one of the five members, in the
    closed enum's declaration order — zero-filled, never omitted). Percentages are
    the EXACT fraction's string, NEVER ``float(frac)*100`` (AR4). Secret-safe by
    construction — paths + tokens + claim flags + opaque ids + counts only (NFR-S1).
    """
    if not isinstance(report, CoverageReport):
        raise CoverageReportError(
            f"render_text requires a CoverageReport, got {type(report)!r}"
        )
    agg = report.aggregate
    lines: list[str] = []
    lines.append(f"# ArgusAgent coverage ledger (schema {report.schema_version})")
    lines.append("")
    lines.append("| file_path | depth | claim_present | recording_ids |")
    lines.append("| --- | --- | --- | --- |")
    for entry in report.entries:
        lines.append(
            f"| {entry.file_path} | {entry.depth.value} | "
            f"{str(entry.claim_present).lower()} | {_recording_ids_str(entry.recording_ids)} |"
        )
    lines.append("")
    lines.append("## aggregate")
    lines.append(f"- total: {agg.total}")
    lines.append(f"- deep_count: {agg.deep_count}")
    lines.append(f"- deep_ratio: {_fraction_str(agg.deep_ratio)}")
    for depth in CoverageDepth:
        lines.append(
            f"- {depth.value}: count={agg.counts_by_depth[depth]} "
            f"pct={_fraction_str(agg.percentages[depth])}"
        )
    return "\n".join(lines) + "\n"


def _to_canonical_payload(report: CoverageReport) -> dict[str, object]:
    """Build a canonical-safe payload dict for the 1.1 serializer (live Fractions).

    Pydantic v2's ``model_dump()`` would coerce a ``Fraction`` via ``str``
    (``Fraction(1, 1) → "1"``), diverging from the LOCKED canonical
    ``Fraction → "num/den"`` encoding (the 1.6 ``AuditVerdict.to_canonical_payload``
    precedent). So this builds the payload directly with LIVE ``Fraction`` objects
    and ``CoverageDepth`` enum keys/values handed to ``canonical.dumps`` (which
    applies its frozen exact ratio encoding + ``str``-enum value verbatim). Keys are
    the closed enum's tokens (``depth.value``) so the per-depth maps are
    deterministic, sorted-key JSON.
    """
    agg = report.aggregate
    return {
        "schema_version": report.schema_version,
        "entries": [
            {
                "file_path": entry.file_path,
                "depth": entry.depth.value,
                "claim_present": entry.claim_present,
                "recording_ids": list(entry.recording_ids),
            }
            for entry in report.entries
        ],
        "aggregate": {
            "total": agg.total,
            "deep_count": agg.deep_count,
            "deep_ratio": agg.deep_ratio,
            "counts_by_depth": {
                depth.value: agg.counts_by_depth[depth] for depth in CoverageDepth
            },
            "percentages": {
                depth.value: agg.percentages[depth] for depth in CoverageDepth
            },
        },
    }


def render_json(report: CoverageReport) -> str:
    """Render the report as canonical JSON THROUGH ``store/canonical.dumps`` (AC4).

    Routes the frozen payload (entries + aggregate) through the single 1.1
    serializer — NO second ``json.dumps`` (the committed AST gate forbids it). The
    serializer encodes ``Fraction → "num/den"``, rejects ``float``, sorts keys, and
    is ``ensure_ascii=False`` so a non-ASCII ``file_path`` round-trips verbatim
    (AI-E1-1). Byte-stable across hosts/runs (NFR-P1). Secret-safe by construction.
    """
    if not isinstance(report, CoverageReport):
        raise CoverageReportError(
            f"render_json requires a CoverageReport, got {type(report)!r}"
        )
    return canonical.dumps(_to_canonical_payload(report))


def render(ledger: CoverageLedger, *, fmt: str = "text") -> str:
    """Render a 1.2 ledger to a string in the chosen format (PURE dispatcher, AR10).

    Supported ``fmt`` values are :data:`SUPPORTED_FORMATS` (``"text"`` / ``"json"``);
    an unsupported selector raises :class:`CoverageReportError` (never a silent
    default). Builds the report once and dispatches. The impure caller does any
    stdout write / ``.argus/`` persist — this returns a string only (AR8).
    """
    report = build_coverage_report(ledger)
    if fmt == "text":
        return render_text(report)
    if fmt == "json":
        return render_json(report)
    raise CoverageReportError(
        f"unsupported render format {fmt!r}; supported formats are {SUPPORTED_FORMATS!r}"
    )
