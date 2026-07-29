"""Story 1.7 — the frozen ``AuditRequest`` invocation contract (AC1).

Verification area ArgusAgent-PIPELINE (TC-ArgusAgent-PIPELINE-001-NN). Pins: frozen +
``extra="forbid"``; ``budget`` is an ``int`` (NEVER float — AR4); the request
round-trips byte-identically through the single 1.1 ``canonical.dumps`` (no float,
no clock); and ``to_provenance_payload`` never leaks ``repo_path`` (NFR-S1).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from argus.models import AUDIT_REQUEST_SCHEMA_VERSION, AuditRequest
from argus.store import canonical


def _request() -> AuditRequest:
    return AuditRequest(
        repo_path="/some/repo", commit="HEAD", budget=250, materiality_bar="default"
    )


def test_audit_request_is_frozen() -> None:
    """TC-ArgusAgent-PIPELINE-001-20 — AC1: AuditRequest is immutable (frozen=True)."""
    request = _request()
    with pytest.raises(ValidationError):
        request.commit = "other"  # type: ignore[misc]


def test_audit_request_forbids_extra() -> None:
    """TC-ArgusAgent-PIPELINE-001-21 — AC1: an unknown field is rejected (extra='forbid')."""
    with pytest.raises(ValidationError):
        AuditRequest(
            repo_path="/r", commit="HEAD", budget=1, materiality_bar="m", surprise=True
        )


def test_audit_request_budget_rejects_float() -> None:
    """TC-ArgusAgent-PIPELINE-001-22 — AC1/AR4: budget is an int, a float is rejected (strict-ish)."""
    with pytest.raises(ValidationError):
        AuditRequest(repo_path="/r", commit="HEAD", budget=1.5, materiality_bar="m")


def test_audit_request_canonical_roundtrip() -> None:
    """TC-ArgusAgent-PIPELINE-001-23 — AC1: round-trips byte-identically through the 1.1 serializer."""
    request = _request()
    payload = request.model_dump(mode="json")
    data = canonical.dumps_bytes(payload)
    assert canonical.loads(data) == payload
    # Deterministic re-serialization (no float / clock landmine).
    assert canonical.dumps_bytes(payload) == data


def test_provenance_payload_excludes_repo_path() -> None:
    """TC-ArgusAgent-PIPELINE-001-24 — NFR-S1: provenance carries no repo_path (no abs-path leak)."""
    payload = _request().to_provenance_payload()
    assert "repo_path" not in payload
    assert payload["commit"] == "HEAD"
    assert payload["budget"] == 250
    assert payload["schema_version"] == AUDIT_REQUEST_SCHEMA_VERSION
    # The provenance payload is itself canonically serializable.
    canonical.dumps_bytes(payload)
