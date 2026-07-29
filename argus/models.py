"""ArgusAgent invocation-contract model — the frozen ``AuditRequest`` (PURE).

Drivers: ArgusAgent-FR-30 (headless invocation contract — ``repo + commit + budget +
materiality_bar → verdict artifact + exit code``; this model is the request half
of that contract), AR2 (the CLI is stdlib ``argparse`` thin wiring that builds
this request), AR8 (pure/impure separation — ``AuditRequest`` is a frozen,
construction-pure contract; the impure ``cli``/``pipeline`` shell consumes it),
ArgusAgent-NFR-M2 (frozen, additive-only Pydantic v2 contracts), AR4 (no ``float`` in a
persisted payload — ``budget`` is an ``int`` of credits, NEVER ``float``).

Why this is the ONLY new model here (architecture §Reuse Patterns / §3.3)
------------------------------------------------------------------------
The architecture's ``models.py`` lists ``AuditRequest`` + ``AuditVerdict`` +
``Finding`` + ``LLMRecording``. Of those, ``AuditVerdict`` already lives in
``verdict/verdict_gate.py`` (Story 1.6 — NOT moved here), the ``Finding`` row IS
the Story 1.2 ``Recording``, and ``LLMRecording`` is Epic-6. So the Epic-1
capstone adds exactly ONE new contract: :class:`AuditRequest`. It is reused by the
pipeline (the input) and recorded into the persisted run-state for provenance.

Locked field/type decisions (frozen for downstream — recorded per the story)
---------------------------------------------------------------------------
- ``repo_path: str`` — the audited-repo path as a plain ``str`` (the impure
  pipeline ``Path``-coerces it). It is NOT persisted into the verdict artifact
  (the audited-repo absolute root is held only transiently by the pipeline,
  mirroring the 1.4 ``RepoIntake`` precedent — NFR-S1). The request itself IS
  recorded for provenance, so an absolute host path here would leak; the pipeline
  records only the request's NON-path provenance fields (commit/budget/
  materiality_bar/schema_version) into the persisted state, never ``repo_path``.
- ``commit: str`` — the pinned commit (ref / short SHA / tag — resolved by the
  1.4 loader). Required (a pinned commit is the determinism precondition, FR1).
- ``budget: int`` — credits, an ``int`` (NEVER ``float`` — the 1.1 serializer
  rejects ``float`` as an NFR-P1 byte-diff landmine, AR4). Story 3.1 (Epic 3)
  gives this field its CONFIGURATION meaning via ``cost/budget_governor.py``:
  ``budget == 0`` (the CLI default) → ``ceiling_credits = None`` (NO ceiling — a
  first-class admit-everything state; there is NO hardcoded numeric default, which
  OI3 defers to Story 7.1), a positive ``budget`` → that ``int`` ceiling the cost
  accounting accounts against. The mid-run HALT on exhaustion is Story 3.2 (this
  field configures the ceiling; the model itself enforces nothing). ``ge=0`` keeps
  a negative budget a typed ``ValidationError``.
- ``materiality_bar: str`` — the materiality bar the request carries. V1 RECORDS
  it but does NOT yet apply it to filter findings (negative-assurance semantics
  are Epic 4 — the seam is documented).
- ``schema_version: str`` — a localized module constant (never env / clock),
  mirroring the 1.2/1.6 precedent; part of any hashed payload that embeds it.

Construction-PURE (AR8): no clock / uuid / random / float, no I/O, so the request
round-trips byte-identically through the single 1.1 ``canonical.dumps`` when it is
recorded as run provenance.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "AUDIT_REQUEST_SCHEMA_VERSION",
    "AuditRequest",
]

# Single localized source for this contract's schema version (additive-only;
# part of any hashed payload that embeds the request — never env / clock).
AUDIT_REQUEST_SCHEMA_VERSION = "1"


class AuditRequest(BaseModel):
    """Frozen invocation contract: ``repo + commit + budget + materiality_bar`` (FR30).

    ``frozen=True, extra="forbid"`` (the Story 1.1/1.2/1.6 precedent): an unknown
    field on read-back is a typed ``ValidationError``. Construction-pure (AR8) — no
    clock / uuid / random / float, no I/O — so it serializes byte-identically
    through the single 1.1 ``canonical.dumps`` when recorded as run provenance.

    ``budget`` is an ``int`` of credits (NEVER ``float`` — AR4). V1 carries +
    records ``budget`` and ``materiality_bar`` but enforces NEITHER (the budget
    governor is Epic 3; negative-assurance materiality filtering is Epic 4).

    Story 2.3 adds the ADDITIVE operator-designation channel (FR4/FR30/NFR-M2): two
    optional ``tuple[str, ...]`` fields defaulting to empty so a pre-2.3 invocation
    round-trips byte-identically when unused. ``critical_paths`` FORCES files
    critical (the lever for a true critical the 2.1 substring matcher missed);
    ``excluded_critical_paths`` REMOVES files (the documented correction for the 2.1
    substring over-flag). The paths are repo-RELATIVE + secret-safe and are recorded
    into the run-state provenance (still NEVER ``repo_path``). NEVER ``float`` (AR4).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(
        default=AUDIT_REQUEST_SCHEMA_VERSION,
        description="AuditRequest schema version (localized constant; additive-only).",
    )
    repo_path: str = Field(..., description="Audited-repo path (str; the pipeline Path-coerces it).")
    commit: str = Field(..., description="Pinned commit (ref/short-SHA/tag) — the FR1 determinism pin.")
    budget: int = Field(
        ..., ge=0, description="Audit budget in credits (int, NEVER float — AR4). Recorded; not enforced in V1 (Epic 3)."
    )
    materiality_bar: str = Field(
        ..., description="Materiality bar the request carries. Recorded; not applied in V1 (Epic 4)."
    )
    critical_paths: tuple[str, ...] = Field(
        default=(),
        description="Operator-forced critical subsystem paths (FR4; additive, repo-relative). Default empty.",
    )
    excluded_critical_paths: tuple[str, ...] = Field(
        default=(),
        description="Operator-excluded critical subsystem paths (FR4; exclude wins on a tie). Default empty.",
    )
    enabled_passes: tuple[str, ...] = Field(
        default=("coverage", "vacuous", "security", "orphan", "prosecutor"),
        description="Enabled audit passes/detectors (default: all passes enabled).",
    )
    enabled_reports: tuple[str, ...] = Field(
        default=("final-verdict", "coverage-ledger"),
        description="Enabled end-user report types to generate.",
    )
    report_dir: str = Field(
        default="",
        description="Optional output directory path for generated markdown reports.",
    )

    def to_provenance_payload(self) -> dict[str, object]:
        """Return the request's NON-path provenance (NFR-S1 — never ``repo_path``).

        The audited-repo path is an absolute-host-path leak risk, so the persisted
        run-state records only the determinism-relevant, secret-safe request fields
        (``commit`` / ``budget`` / ``materiality_bar`` / ``schema_version`` plus the
        Story-2.3 operator designation paths, which are repo-RELATIVE + secret-safe).
        The absolute repo root is held only transiently by the impure pipeline (the
        1.4 ``RepoIntake`` precedent) — ``repo_path`` is NEVER recorded.
        """
        return {
            "schema_version": self.schema_version,
            "commit": self.commit,
            "budget": self.budget,
            "materiality_bar": self.materiality_bar,
            "critical_paths": list(self.critical_paths),
            "excluded_critical_paths": list(self.excluded_critical_paths),
            "enabled_passes": list(self.enabled_passes),
            "enabled_reports": list(self.enabled_reports),
        }

