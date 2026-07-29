"""PURE ``.argus/`` deserialize/validate read primitive — the resumability seam.

Drivers: ArgusAgent-FR-31 (resumability — the reader deserializes/validates ``.argus/``
state so a later resume re-loads it), AR8 (PURE deserialize/validate — the reader
MAY read the bytes off disk as the resumability read primitive, but performs NO
clock read, NO ``uuid4``/``random``, NO LLM/network, NO write), AR10 (typed
failure — corrupt/tampered/missing state degrades to a typed error, never an
uncaught crash / silent empty model / fabricated valid-looking result).

Pure classification (architecture §Pure/Impure Separation)
----------------------------------------------------------
``store/reader.py`` is the resumability read primitive: it reads bytes off disk
(via :class:`ApaaStorePaths`, containment-checked) and turns them into validated,
frozen models. It writes nothing, reads no clock, mints no id. The byte read is
the ONLY side effect.

Read taxonomy (locked + documented per the story)
-------------------------------------------------
PER-TYPE readers (``read_envelope`` / ``read_ledger`` / ``read_recording``) over a
shared generic core (``_read_validated``). Each:
  1. resolves + containment-checks the locator via :class:`ApaaStorePaths`,
  2. reads the bytes (``FileNotFoundError`` for the missing-file case),
  3. ``canonical.loads`` (``CanonicalSerializationError`` / ``json``-decode →
     wrapped as ``CanonicalSerializationError`` for non-JSON / non-UTF-8),
  4. validates against the frozen Pydantic v2 model (``ValidationError`` for an
     unknown field — ``extra="forbid"`` from Stories 1.1/1.2 — or a bad shape),
  5. reconstructs a model EQUAL to the original; re-serializing through
     ``canonical.dumps_bytes`` yields bytes byte-identical to what was read
     (round-trip stability).

Tamper guard (recommended option, taken)
-----------------------------------------
``read_envelope`` (and the ledger/recording readers, which read an envelope) RE-
VERIFY the envelope ``content_hash`` against a hash re-computed over the loaded
payload (``compute_content_hash``). A mismatch raises :class:`StoreIntegrityError`
(a ``ValueError`` subclass added ONLY for this tamper case — no existing type
fits). This makes AC6's tamper case real and cheap.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from argus.ledger.coverage_ledger import CoverageLedger
from argus.ledger.recording import Recording
from argus.store import canonical
from argus.store.envelope import Envelope, compute_content_hash
from argus.store.paths import ApaaStorePaths

__all__ = ["StoreIntegrityError", "ApaaStoreReader"]


class StoreIntegrityError(ValueError):
    """Raised when a stored envelope's ``content_hash`` fails re-verification.

    A ``ValueError`` subclass (mirroring ``CanonicalSerializationError`` /
    ``WorkspaceContainmentError``) — the typed failure for the AC6 tamper case
    (the on-disk payload was mutated without recomputing its hash). The message
    names the offending RELATIVE locator only — never file content (NFR-S1 spirit).
    """


class ApaaStoreReader:
    """PURE deserialize/validate reader over the contained ``.argus/`` tree.

    Constructed with the audited-repo root (or an :class:`ApaaStorePaths`).
    Containment delegates to :class:`ApaaStorePaths`; deserialization delegates to
    the single ``canonical`` serializer.
    """

    def __init__(self, repo_root: str | Path | ApaaStorePaths) -> None:
        self._paths = (
            repo_root if isinstance(repo_root, ApaaStorePaths) else ApaaStorePaths(repo_root)
        )

    @property
    def paths(self) -> ApaaStorePaths:
        return self._paths

    def read_bytes(self, relative_path: str | Path) -> bytes:
        """Read the raw bytes for a ``.argus/`` locator (containment-checked).

        Raises:
            WorkspaceContainmentError: if the locator escapes the ``.argus/`` root.
            FileNotFoundError: if no file exists at the (confined) locator.
        """
        target: Path = self._paths.resolve(relative_path)
        return target.read_bytes()

    def _load_object(self, relative_path: str | Path) -> Any:
        raw = self.read_bytes(relative_path)
        try:
            return canonical.loads(raw)
        except UnicodeDecodeError as exc:
            raise canonical.CanonicalSerializationError(
                f"artifact '{relative_path}' is not valid UTF-8"
            ) from exc
        except json.JSONDecodeError as exc:
            raise canonical.CanonicalSerializationError(
                f"artifact '{relative_path}' is not valid JSON"
            ) from exc

    def read_envelope(self, relative_path: str | Path, *, verify_hash: bool = True) -> Envelope:
        """Load + validate an :class:`Envelope`; re-verify its ``content_hash`` (tamper guard).

        Raises:
            WorkspaceContainmentError / FileNotFoundError: locator escape / missing.
            CanonicalSerializationError: non-UTF-8 / non-JSON bytes.
            pydantic.ValidationError: bad shape / unknown field (``extra="forbid"``).
            StoreIntegrityError: the stored ``content_hash`` does not match a hash
                re-computed over the loaded payload (tamper detection).
        """
        obj = self._load_object(relative_path)
        envelope = Envelope.model_validate(obj)
        if verify_hash:
            recomputed = compute_content_hash(envelope.payload)
            if recomputed != envelope.content_hash:
                raise StoreIntegrityError(
                    f"content_hash mismatch for artifact '{relative_path}' "
                    f"(tamper detected: stored != recomputed)"
                )
        return envelope

    def read_ledger(self, relative_path: str | Path) -> CoverageLedger:
        """Load an envelope at ``relative_path`` and validate its payload as a CoverageLedger."""
        envelope = self.read_envelope(relative_path)
        return CoverageLedger.model_validate(envelope.payload)

    def read_recording(self, relative_path: str | Path) -> Recording:
        """Load an envelope at ``relative_path`` and validate its payload as a Recording."""
        envelope = self.read_envelope(relative_path)
        return Recording.model_validate(envelope.payload)
