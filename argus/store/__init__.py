"""ArgusAgent on-disk store sub-package (``.argus/`` artifacts).

Story 1.1 lands the PURE determinism spine — the single canonical serializer
(``canonical.py``) and the content-hashed, schema-versioned, prev-hash-chained
envelope builder (``envelope.py``). Story 1.3 adds the impure write/read shell:
``paths.py`` (the ``.argus/`` fixed tree + containment-checked resolver, REUSING
the Minions ``WorkspaceContainmentError`` containment logic), ``writer.py`` (the
IMPURE content-addressed, single-serializer byte writer), and ``reader.py`` (the
PURE deserialize/validate read primitive — the FR31 resumability seam).

Drivers: ArgusAgent-FR-25, ArgusAgent-FR-31, ArgusAgent-NFR-A1, ArgusAgent-NFR-D3, ArgusAgent-NFR-P1,
ArgusAgent-NFR-S5, AR4, AR7, AR8, AR10, AR11.
"""

__all__: list[str] = []
