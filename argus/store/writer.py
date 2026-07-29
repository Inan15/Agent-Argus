"""IMPURE ``.argus/`` artifact writer — content-addressed, single-serializer bytes.

Drivers: ArgusAgent-FR-25 (writes go through the content-hashed envelope),
ArgusAgent-NFR-P1 (byte-identical on-disk state via the single serializer + the fixed
tree + content-addressed filenames), AR4 (single canonical serializer — the bytes
written are EXACTLY ``canonical.dumps_bytes(...)``; NO second ``json.dumps``),
AR7 (REUSE the canonical containment authority via :mod:`store.paths` — no fork),
AR8 (this is the IMPURE shell; filesystem I/O lives here), AR10 (typed failure —
no bare ``except: pass``, no ``print()``, no fabricated locator / silent partial),
AR11 (filenames from content-sha256 / a stable assignment-id, never arrival order).

Reuse decision (recorded per the story / architecture Decision F)
-----------------------------------------------------------------
The writer delegates ALL containment to :class:`ApaaStorePaths` (which thin-wraps
the Minions ``WorkspaceContainmentError`` + ``Path.resolve()``/``is_relative_to``
logic — see ``store/paths.py`` for the thin-wrap-vs-delegate rationale). The
writer adds NO second containment check. Serialization is delegated to the Story
1.1 ``canonical`` serializer + ``EnvelopeWriter``; the writer never builds JSON
itself.

Determinism contract (locked + golden-tested)
---------------------------------------------
- Content-addressed artifacts (state snapshots, findings) → ``<sub>/<content_hash>.json``
  where ``content_hash`` is the Story 1.1 envelope ``content_hash`` (sha256 over
  the canonical payload only). Two hosts producing the same payload write a
  byte-identical file with an identical name (NFR-P1 / AR11).
- Assignment manifests → ``assignments/<assignment_id>.json`` where
  ``assignment_id`` is a caller-supplied STABLE, content-derived id — never
  ``uuid4`` / a counter / arrival order.
- The returned locator is the ``.argus/``-root-relative POSIX path (DN-3 / NFR-S1
  spirit) — never an absolute host path.

Payload contract (round-trip fidelity)
--------------------------------------
A persisted payload is a JSON-PRIMITIVE dict — exactly what ``model_dump(mode=
"json")`` produces (enums → their ``str`` value, tuples → lists). Passing a
Python-mode dump (enum members / tuples) still serializes correctly (the
canonical serializer rewrites enum-str/Decimal leaves), but byte-for-byte
envelope-equality on read-back holds only for JSON-primitive payloads — so the
content hash is taken over, and the reader reconstructs, the canonical JSON form.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from argus.store import canonical
from argus.store.envelope import Envelope, EnvelopeWriter
from argus.store.paths import ApaaStorePaths

__all__ = ["ApaaStoreWriter"]

# JSON file suffix for every persisted artifact.
_JSON_SUFFIX = ".json"


class ApaaStoreWriter:
    """Writes envelope-wrapped payloads to the contained ``.argus/`` tree.

    Constructed with the audited-repo root (or an :class:`ApaaStorePaths`). All
    containment delegates to :class:`ApaaStorePaths`; all serialization delegates
    to the single ``canonical`` serializer + ``EnvelopeWriter``.
    """

    def __init__(self, repo_root: str | Path | ApaaStorePaths) -> None:
        self._paths = (
            repo_root if isinstance(repo_root, ApaaStorePaths) else ApaaStorePaths(repo_root)
        )

    @property
    def paths(self) -> ApaaStorePaths:
        return self._paths

    def write_envelope(self, subdir: str, envelope: Envelope) -> str:
        """Write a pre-built :class:`Envelope` to ``<subdir>/<content_hash>.json``.

        The on-disk bytes are EXACTLY ``canonical.dumps_bytes(envelope_payload)``
        (AR4 single serializer). The filename derives from the envelope
        ``content_hash`` (content-addressed, AR11) — never arrival order. Returns
        the ``.argus/``-root-relative POSIX locator (NFR-S1 spirit).

        Raises:
            WorkspaceContainmentError: if the resolved target escapes the
                ``.argus/`` root (raised by :class:`ApaaStorePaths` BEFORE any
                write).
            canonical.CanonicalSerializationError: if the envelope is not
                canonically serializable (typed failure, AR10).
            OSError: propagated on a write failure to a legitimately-confined path
                (no fabricated locator, no silent partial).
        """
        relative = f"{subdir}/{envelope.content_hash}{_JSON_SUFFIX}"
        return self._write_model(relative, envelope)

    def write_payload(
        self,
        subdir: str,
        payload: dict[str, Any],
        *,
        schema_version: str,
        producer: str,
        prev_hash: str | None = None,
    ) -> str:
        """Wrap ``payload`` in an envelope (Story 1.1) then write it (content-addressed).

        REUSES ``EnvelopeWriter.build`` — content-hash over the payload only,
        ``prev_hash`` chaining (defaults to the genesis sentinel), ``schema_version``
        + ``producer`` + the single-source ``argus_version``. Returns the
        ``.argus/``-root-relative POSIX locator.
        """
        if prev_hash is None:
            envelope = EnvelopeWriter.build(
                payload, schema_version=schema_version, producer=producer
            )
        else:
            envelope = EnvelopeWriter.build(
                payload, prev_hash=prev_hash, schema_version=schema_version, producer=producer
            )
        return self.write_envelope(subdir, envelope)

    def write_assignment(self, assignment_id: str, envelope: Envelope) -> str:
        """Write an assignment manifest to ``assignments/<assignment_id>.json``.

        The filename derives from the caller-supplied STABLE ``assignment_id``
        (content-derived, never ``uuid4`` / counter / arrival order — AR11). The
        bytes are still the single-serializer canonical bytes of the envelope.
        """
        relative = f"assignments/{assignment_id}{_JSON_SUFFIX}"
        return self._write_model(relative, envelope)

    def _write_model(self, relative: str, envelope: Envelope) -> str:
        # Containment check + parent-dir creation happen in paths.ensure_parent
        # BEFORE any byte write; an escape raises there.
        target: Path = self._paths.ensure_parent(relative)
        data = canonical.dumps_bytes(envelope.model_dump())
        target.write_bytes(data)
        return self._paths.to_locator(relative)
