"""PURE FR29 evidence-bundle export — no source retention (the security keystone).

Drivers: ArgusAgent-FR-29 (an operator can export an evidence bundle [coverage ledger,
scope statement, findings, verdict]; the operated-service path retains no source —
the CENTRAL driver), ArgusAgent-NFR-S3 (on the operated-service path, customer source is
never retained after an audit completes — the no-source-retention keystone),
ArgusAgent-NFR-S1 (source / prompt / response / API-key bytes never appear in ledgers,
evidence, logs, OTLP spans, traces, or any response — the bundle is "evidence",
squarely in scope), ArgusAgent-FR-28 (producer-side redaction — findings cite locations,
never source/secret bytes; the bundle exports the already-redacted findings
verbatim; the durable CI-blocking property suite that enforces it is Story 4.4),
ArgusAgent-FR-17 / NFR-A3 (the negative-assurance verdict + scope statement + disclaimer
+ point-in-time stamp the bundle exports — REUSED from 4.1, framing preserved),
ArgusAgent-FR-26 / NFR-A2 (the referential-integrity-lint report the bundle includes —
REUSED from 4.2), ArgusAgent-FR-33 (the verdict-impact-ordered findings the bundle
exports — REUSED unchanged from the 1.6 gate), ArgusAgent-FR-25 / NFR-A1 (if persisted,
the content-hashed, schema-versioned, prev-hash-chained envelope via the 1.3 shell),
ArgusAgent-NFR-D2 (deterministic, zero-LLM-token — a pure fold over the EXISTING records,
no source re-read), ArgusAgent-NFR-D3 (the content hash covers the canonical payload
ONLY — the point-in-time stamp is the envelope ``created_at``, EXCLUDED from the
hash; this module NEVER reads a clock), ArgusAgent-NFR-P1 (byte-identical /
order-independent bundle for the same audit result; no float; sorted collections),
ArgusAgent-NFR-S5 (any FS write is containment-checked via the 1.3 shell), ArgusAgent-NFR-M1
(≤1200-line files), ArgusAgent-NFR-M2 (frozen, schema-versioned, additive-only contract),
AR4 (no ``float``; ratios are exact ``Fraction`` REUSED from the verdict; single
canonical serializer; no clock/uuid/random/iteration-order — content-derived,
AR11), AR8 (pure/impure separation — the bundle model + builder + render are PURE;
the optional WRITE is the impure 1.3 shell), AR10 (typed failure —
:class:`EvidenceBundleError`, never an uncaught raise).

Test area ArgusAgent-EVIDENCE (``TC-ArgusAgent-EVIDENCE-001-NN``) — the NEW area for the
``evidence/`` sub-package; the first test file in it
(``tests/argus/test_evidence_bundle.py``), starting index ``...-01``.

The no-source-retention keystone (FR29 / NFR-S3 — the whole point of the story)
------------------------------------------------------------------------------
The exported bundle contains NO audited source-code byte and NO secret value —
only locations + redacted indicators. The moat is STRUCTURAL (the ABSENCE of a
value field), not a redaction pass at serialization time — the same argument
Story 2.5 used (the ``Recording`` / ``Locator`` carry no source-value field). The
bundle aggregates BY REFERENCE the already-redacted surfaces (the 4.1 wrapper, the
2.2 coverage report, the 1.6 ``Recording`` findings, the 4.2 integrity report) and
adds NO field that could hold a source byte / raw excerpt / secret value. Even a
future caller cannot route a source byte into the bundle. The mandatory
no-source-retention test (AC2) plants a sentinel source byte AND a sentinel secret
value and proves both ABSENT from the serialized bundle while the bundle is
non-empty + the secret finding present (redaction != suppression).

Separateness from the Minions governance bundle (the no-coupling rule)
----------------------------------------------------------------------
ArgusAgent's evidence bundle is a DIFFERENT artifact from Minions'
``governance/evidence.py`` (decision ledger / policy traces / A2A audit). This
module does NOT import, fork, or couple to it. ArgusAgent consumes-not-owns shared LEAF
layers (the 1.1 serializer / 1.3 store) but owns its own audit-evidence bundle.

PURE (AR8): the model + :func:`build_evidence_bundle` + :func:`bundle_to_canonical_payload`
perform NO source re-read, NO filesystem I/O, NO clock read, NO ``uuid``/``random``,
NO LLM/network, NO set/dict-iteration-order reliance. The ONLY impure surface is
the OPTIONAL :func:`persist_evidence_bundle` (the 1.3 writer). Joins the
import-isolation ``_MODULES_UNDER_GUARD`` gate.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from argus.ledger.coverage_report import CoverageReport
from argus.ledger.recording import Recording
from argus.store import canonical
from argus.store.integrity import IntegrityReport
from argus.store.writer import ApaaStoreWriter
from argus.verdict.negative_assurance import NegativeAssuranceVerdict

__all__ = [
    "EVIDENCE_BUNDLE_SCHEMA_VERSION",
    "EVIDENCE_BUNDLE_PRODUCER",
    "EvidenceBundleError",
    "EvidenceBundle",
    "build_evidence_bundle",
    "bundle_to_canonical_payload",
    "bundle_to_canonical_bytes",
    "persist_evidence_bundle",
]

# Single localized source for this contract's schema version (additive-only,
# NFR-M2; part of the hashed payload — a bump deliberately changes the content hash).
EVIDENCE_BUNDLE_SCHEMA_VERSION = "1"

# Producer token for the (optional) persisted bundle envelope (provenance — not a
# path/secret). Distinct from every pipeline producer token (it names THIS bundle).
EVIDENCE_BUNDLE_PRODUCER = "argus.evidence.bundle"


class EvidenceBundleError(ValueError):
    """A TYPED malformed-input failure for the bundle builder (AR10).

    A ``ValueError`` subclass localized to this module (mirroring
    ``NegativeAssuranceError`` / ``IntegrityLintError`` / ``CoverageReportError``).
    Raised on a non-``NegativeAssuranceVerdict`` / non-``CoverageReport`` /
    non-``IntegrityReport`` section, a non-``Recording`` finding, a non-``str``
    ``commit`` / ``argus_version``, or an ``AuditResult`` missing the 4.1
    ``negative_assurance`` wrapper — never a silent coerce / bare ``except: pass`` /
    ``print()`` in library code. The message names the offending value/type only —
    never source / secret bytes (NFR-S1).
    """


class EvidenceBundle(BaseModel):
    """Frozen FR29 evidence bundle — aggregates the already-redacted audit surfaces.

    Story 4.3 (FR29 / NFR-S3 / NFR-M2). ``frozen=True, extra="forbid"`` (the
    1.1/1.2/1.6/4.1/4.2 precedent), localized
    :data:`EVIDENCE_BUNDLE_SCHEMA_VERSION`. AGGREGATES BY REFERENCE (does not
    re-derive): the 4.1 ``NegativeAssuranceVerdict`` (verdict + scope statement +
    disclaimer + materiality + deep-%), the 2.2 ``CoverageReport`` (per-file depth
    states + per-depth counts + exact-``Fraction`` deep-%), the verdict-ordered 1.6
    ``Recording`` findings (locators + ids + advisory + ``contained_secret``
    indicator ONLY), the 4.2 ``IntegrityReport``, and bundle metadata.

    The no-source-retention MOAT (AC3): EVERY leaf is a repo-relative POSIX locator
    / id / closed-enum kind / a redacted-or-masked indicator / a deterministic
    statement / a ``Fraction`` / ``int`` / ``bool`` — there is NO field that holds a
    file's source bytes / a raw excerpt / a secret value (the ABSENCE of a value
    field is the moat, not a redaction pass). NO ``repo_path`` / absolute host path.
    NO ``float`` anywhere. NO volatile ``run_id`` / ``created_at`` in the hashed
    payload (NFR-D3 — the stamp is the envelope ``created_at`` IF persisted).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default=EVIDENCE_BUNDLE_SCHEMA_VERSION,
        description="Evidence-bundle schema version (localized constant; additive-only).",
    )
    argus_version: str = Field(..., description="ArgusAgent package version that built this bundle.")
    commit: str = Field(..., description="The audited commit pin (REUSED from the request).")
    materiality_bar: str = Field(
        ..., description="The operator materiality bar the audit ran under (REUSED)."
    )
    negative_assurance: NegativeAssuranceVerdict = Field(
        ..., description="The 4.1 negative-assurance verdict (verdict + scope + disclaimer)."
    )
    coverage: CoverageReport = Field(
        ..., description="The 2.2 per-file coverage ledger + per-depth counts + deep-% (Fraction)."
    )
    findings: tuple[Recording, ...] = Field(
        default=(),
        description="The verdict-impact-ordered 1.6 findings (locators + ids + advisory ONLY).",
    )
    integrity_report: IntegrityReport = Field(
        ..., description="The 4.2 referential-integrity-lint report (consistent + sorted findings)."
    )


def build_evidence_bundle(
    result: Any,
    integrity_report: IntegrityReport,
    *,
    commit: str,
    argus_version: str,
) -> EvidenceBundle:
    """Fold the EXISTING in-memory records into the FR29 evidence bundle (PURE).

    ``result`` is the pipeline ``AuditResult`` (duck-typed against its real shape —
    ``verdict``, ``negative_assurance``, ``coverage_report`` — so this pure module
    does NOT import the impure ``pipeline`` and create a circular import). The
    builder READS the already-redacted surfaces — the 4.1 wrapper from
    ``result.negative_assurance``, the 2.2 coverage report from
    ``result.coverage_report``, the verdict-ordered findings from
    ``result.verdict.ordered_findings``, the 4.2 ``integrity_report`` verbatim — and
    assembles them with the metadata. It does NOT re-run the gate, re-derive the
    deep-%, re-walk the integrity graph, or re-read source. Honest + populated for
    ALL THREE verdicts; the disclaimer + assurance statement are REUSED verbatim
    from 4.1 (no re-authored verdict language — AC4).

    Raises :class:`EvidenceBundleError` (AR10) on a malformed input (a missing 4.1
    wrapper / missing coverage report, a wrong-typed section / finding, or a
    non-``str`` ``commit`` / ``argus_version``) — never a silent coerce. PURE (AR8):
    no I/O, no clock, no ``uuid``/``random``, no LLM/network, no ``float``, no
    set/dict-order reliance. Same inputs → byte-identical bundle (NFR-P1) — the
    findings preserve the verdict-impact order the gate already fixed (FR33).
    """
    if not isinstance(commit, str):
        raise EvidenceBundleError(f"commit must be a str, got {type(commit).__name__}")
    if not isinstance(argus_version, str):
        raise EvidenceBundleError(
            f"argus_version must be a str, got {type(argus_version).__name__}"
        )
    if not isinstance(integrity_report, IntegrityReport):
        raise EvidenceBundleError(
            "build_evidence_bundle requires an IntegrityReport, "
            f"got {type(integrity_report).__name__}"
        )

    negative_assurance = getattr(result, "negative_assurance", None)
    if not isinstance(negative_assurance, NegativeAssuranceVerdict):
        raise EvidenceBundleError(
            "result.negative_assurance must be a NegativeAssuranceVerdict (the 4.1 wrapper); "
            f"got {type(negative_assurance).__name__}"
        )

    coverage = getattr(result, "coverage_report", None)
    if not isinstance(coverage, CoverageReport):
        raise EvidenceBundleError(
            "result.coverage_report must be a CoverageReport (the 2.2 surface); "
            f"got {type(coverage).__name__}"
        )

    verdict = getattr(result, "verdict", None)
    ordered = getattr(verdict, "ordered_findings", None)
    if not isinstance(ordered, tuple):
        raise EvidenceBundleError(
            "result.verdict.ordered_findings must be a tuple of Recording (the 1.6 verdict); "
            f"got {type(ordered).__name__}"
        )
    findings: tuple[Recording, ...] = tuple(ordered)
    for finding in findings:
        if not isinstance(finding, Recording):
            raise EvidenceBundleError(
                f"every ordered finding must be a Recording, got {type(finding).__name__}"
            )

    return EvidenceBundle(
        argus_version=argus_version,
        commit=commit,
        materiality_bar=negative_assurance.materiality_bar,
        negative_assurance=negative_assurance,
        coverage=coverage,
        findings=findings,
        integrity_report=integrity_report,
    )


def _coverage_payload(coverage: CoverageReport) -> dict[str, object]:
    """Canonical-safe coverage payload with LIVE ``Fraction`` leaves (the 2.2 form).

    Mirrors ``coverage_report._to_canonical_payload`` (live ``Fraction`` deep-% +
    per-depth percentages + ``CoverageDepth`` enum values) so the single 1.1
    serializer applies its frozen ``num/den`` encoding (AR4). Reuses the closed
    enum's declaration order for the per-depth maps (deterministic, no
    iteration-order reliance).
    """
    agg = coverage.aggregate
    return {
        "schema_version": coverage.schema_version,
        "entries": [
            {
                "file_path": entry.file_path,
                "depth": entry.depth.value,
                "claim_present": entry.claim_present,
                "recording_ids": list(entry.recording_ids),
            }
            for entry in coverage.entries
        ],
        "aggregate": {
            "total": agg.total,
            "deep_count": agg.deep_count,
            "deep_ratio": agg.deep_ratio,
            "counts_by_depth": {
                depth.value: count for depth, count in agg.counts_by_depth.items()
            },
            "percentages": {
                depth.value: pct for depth, pct in agg.percentages.items()
            },
        },
    }


def bundle_to_canonical_payload(bundle: EvidenceBundle) -> dict[str, object]:
    """Build the canonical-safe payload dict for the single 1.1 serializer (AC5).

    Re-installs the LIVE ``Fraction`` leaves (the 4.1 wrapper's ``deep_ratio`` + the
    2.2 coverage report's ``deep_ratio`` / per-depth percentages) so the single 1.1
    ``canonical.dumps_bytes`` applies its frozen ``num/den`` encoding — NO second
    ``json.dumps`` (the committed AST gate forbids it). Every other leaf (the
    findings' ``model_dump(mode="json")``, the integrity report's dump, the metadata
    strings) is already canonical-safe. Raises :class:`EvidenceBundleError` on a
    non-``EvidenceBundle`` argument (AR10).
    """
    if not isinstance(bundle, EvidenceBundle):
        raise EvidenceBundleError(
            f"bundle_to_canonical_payload requires an EvidenceBundle, got {type(bundle).__name__}"
        )
    return {
        "schema_version": bundle.schema_version,
        "argus_version": bundle.argus_version,
        "commit": bundle.commit,
        "materiality_bar": bundle.materiality_bar,
        "negative_assurance": bundle.negative_assurance.to_canonical_payload(),
        "coverage": _coverage_payload(bundle.coverage),
        "findings": [finding.model_dump(mode="json") for finding in bundle.findings],
        "integrity_report": bundle.integrity_report.model_dump(mode="json"),
    }


def bundle_to_canonical_bytes(bundle: EvidenceBundle) -> bytes:
    """The single-serializer UTF-8 bytes of the bundle's canonical payload (AC5/AC6).

    Routes :func:`bundle_to_canonical_payload` through the single 1.1
    ``canonical.dumps_bytes`` — byte-stable + order-independent for the same audit
    result (NFR-P1). Secret-safe by construction (no source/secret field exists).
    """
    return canonical.dumps_bytes(bundle_to_canonical_payload(bundle))


def persist_evidence_bundle(
    writer: ApaaStoreWriter, bundle: EvidenceBundle
) -> str:
    """OPTIONAL impure persist of the bundle to ``state/`` (additive — DN-WIRING, AC5).

    The IMPURE shell: the bundle lands content-addressed in ``state/`` via the
    EXISTING ``ApaaStoreWriter.write_payload`` → ``EnvelopeWriter.build`` → the
    single 1.1 ``canonical`` serializer (no second serializer / ``json.dumps`` — the
    AST gate enforces it). The bytes come from :func:`bundle_to_canonical_payload`
    (LIVE ``Fraction`` → the canonical ``num/den`` encoding). The point-in-time
    stamp is the envelope ``created_at`` (NFR-D3 — never in the hashed payload). The
    payload carries ONLY locations + redacted indicators + provenance — never an
    absolute host path / source / secret byte (NFR-S1 / NFR-S3). Returns the
    ``.argus/``-root-relative POSIX locator. Containment is the 1.3 writer's
    ``ApaaStorePaths`` ``is_relative_to`` check (NFR-S5). NOT wired into the
    pipeline (the testable deliverable is the bundle + its no-source guarantee).
    """
    if not isinstance(bundle, EvidenceBundle):
        raise EvidenceBundleError(
            f"persist_evidence_bundle requires an EvidenceBundle, got {type(bundle).__name__}"
        )
    return writer.write_payload(
        "state",
        bundle_to_canonical_payload(bundle),
        schema_version=bundle.schema_version,
        producer=EVIDENCE_BUNDLE_PRODUCER,
    )
