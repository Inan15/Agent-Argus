"""Content-hashed, schema-versioned, prev-hash-chained ArgusAgent artifact envelope.

Drivers: ArgusAgent-FR-25 (content-hashed, schema-versioned envelope), ArgusAgent-NFR-A1
(schema-versioned, content-hashed, prev-hash-chained, additive-only envelope),
ArgusAgent-NFR-D3 (hash covers the canonical payload ONLY — excludes volatile
``run_id`` / ``created_at``), ArgusAgent-NFR-P1 (byte-identical across hosts),
ArgusAgent-NFR-M2 (frozen, additive-only contract).

The envelope is a PURE Pydantic v2 builder (AR8) — no filesystem I/O, no clock,
no LLM, no network. The impure ``.argus/`` write/read shell is Story 1.3.

Hash contract (NFR-D3)
----------------------
``content_hash = sha256(canonical.dumps_bytes(payload)).hexdigest()`` — taken
over the canonical bytes of the PAYLOAD ONLY. The volatile ``run_id`` and
``created_at`` fields live on the envelope but are EXCLUDED from the hash, so two
identical audits run on two hosts (different run ids / timestamps) produce an
identical ``content_hash`` (the NFR-P1/D1 reproducibility keystone).

Chain contract (NFR-A1)
-----------------------
Each envelope's ``prev_hash`` is the prior envelope's ``content_hash``; the chain
head uses the fixed genesis sentinel :data:`GENESIS_PREV_HASH` (``"0" * 64``).
This mirrors a hash-chained governance ledger conceptually, but the ArgusAgent envelope
is self-contained — it imports and forks no external ledger implementation.

Additive-only contract (NFR-M2)
-------------------------------
The :class:`Envelope` model is ``frozen=True``. Schema evolution is additive-only:
bump ``schema_version`` and add OPTIONAL fields only — never remove/rename/retype
an existing field. Because the hash covers the payload only, adding an optional
envelope field never changes an existing payload's ``content_hash``.
"""

from __future__ import annotations

import hashlib
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from argus import __version__ as _ArgusAgent_VERSION
from argus.store import canonical

__all__ = [
    "GENESIS_PREV_HASH",
    "Envelope",
    "EnvelopeWriter",
    "compute_content_hash",
]

# Fixed chain-head marker — the 64-char zero sha256 hex string. Used as
# ``prev_hash`` for the first envelope in a chain.
GENESIS_PREV_HASH = "0" * 64


def compute_content_hash(payload: Any) -> str:
    """sha256 hexdigest over the canonical bytes of ``payload`` (NFR-D3).

    Uses the SAME ``canonical.dumps_bytes`` the writer would use, so the hashed
    bytes are exactly the bytes that hit disk. Raises
    ``canonical.CanonicalSerializationError`` if the payload is not canonically
    serializable (typed failure, AR10).
    """
    return hashlib.sha256(canonical.dumps_bytes(payload)).hexdigest()


class Envelope(BaseModel):
    """Frozen, additive-only artifact envelope (ArgusAgent-FR-25 / NFR-A1 / NFR-M2)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = Field(..., description="Envelope schema version (additive-only).")
    producer: str = Field(..., description="Logical producer of the wrapped payload.")
    argus_version: str = Field(..., description="ArgusAgent package version that built this envelope.")
    content_hash: str = Field(..., description="sha256 over the canonical payload ONLY (NFR-D3).")
    prev_hash: str = Field(..., description="Prior envelope's content_hash, or genesis sentinel.")
    payload: dict[str, Any] = Field(..., description="The wrapped JSON-object artifact body.")

    # ── Volatile fields — EXCLUDED from content_hash (NFR-D3) ──
    run_id: str | None = Field(default=None, description="Volatile run id; not hashed.")
    created_at: str | None = Field(default=None, description="Volatile timestamp; not hashed.")


class EnvelopeWriter:
    """PURE builder that wraps a payload in a content-hashed :class:`Envelope`.

    Stateless — no I/O, no clock, no network. ``build`` computes the content
    hash over the canonical payload only and assembles a frozen envelope.
    """

    @staticmethod
    def build(
        payload: dict[str, Any],
        *,
        prev_hash: str = GENESIS_PREV_HASH,
        schema_version: str,
        producer: str,
        argus_version: str = _ArgusAgent_VERSION,
        run_id: str | None = None,
        created_at: str | None = None,
    ) -> Envelope:
        """Build a frozen envelope around ``payload``.

        ``prev_hash`` defaults to :data:`GENESIS_PREV_HASH` for the chain head.
        ``argus_version`` is sourced from the single ArgusAgent-owned constant
        (``argus.__version__``); callers must not pass a literal.
        The ``content_hash`` is computed over the canonical payload ONLY — the
        ``run_id`` / ``created_at`` volatile fields are stored but never hashed.
        Raises ``canonical.CanonicalSerializationError`` on a non-canonical
        payload (typed failure, AR10).
        """
        content_hash = compute_content_hash(payload)
        return Envelope(
            schema_version=schema_version,
            producer=producer,
            argus_version=argus_version,
            content_hash=content_hash,
            prev_hash=prev_hash,
            payload=payload,
            run_id=run_id,
            created_at=created_at,
        )
