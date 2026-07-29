"""ArgusAgent cache sub-package — reproducible-verdict memoization (Epic 5, Tier-B).

Drivers: ArgusAgent-FR-27 (reproduce the same verdict for the same repository and ArgusAgent
version), ArgusAgent-NFR-D1 (content-addressed memoization key = content-hash + model
checkpoint + detector-set hash), ArgusAgent-AR5 (ONE cache-key derivation function),
ArgusAgent-AR8 (pure module — no I/O / clock / LLM).

Story 5.1 lands ONLY the PURE cache-key derivation (``key.py``) over the full
recording-producing closure + a CI canary. The memoization STORE (5.2) and
INVALIDATION / rejected-finding key-busting (5.3) ride on the key this package
defines and are explicitly out of 5.1's scope. This package writes NO
``.argus/cache/`` byte (5.2 owns the cache tree).
"""

from __future__ import annotations

__all__: list[str] = []
