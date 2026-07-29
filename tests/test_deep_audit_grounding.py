"""ArgusAgent-AUDIT (TC-ArgusAgent-AUDIT-001-46..) — the FR7 deep-claim AST-grounding validator.

Drivers: ArgusAgent-FR-7 (validate a deep claim against source structure — Python AST in
V1 — and downgrade an unverifiable claim), ArgusAgent-FR-6 (the EXISTING claim-required
``audited_deep`` / silence→shallow keystone, composed not forked), ArgusAgent-NFR-P2 (the
stack-agnostic ``claim → validated?`` interface; Python = impl #1; non-Python →
``claim_emitted`` proxy; V2 additive), ArgusAgent-AR10 (a malformed / empty / None /
parse-failed grading input → a typed boolean, NEVER an uncaught raise),
ArgusAgent-NFR-D1/D2 (pure + deterministic + zero-token), ArgusAgent-AR7/§3.3 (REUSE the 1.4
``definitions`` BY IMPORT — no re-parse), ArgusAgent-AR8 (pure), ArgusAgent-AR4 (no float).

This module closes the long-carried 🟡 DF-1-7-B (AI-E5-5): the interim FR6
claim-PRESENCE proxy graded EVERY cleanly-parsed non-test Python file
``audited_deep``; FR7 grades ``audited_deep`` ONLY when the claim is AST-GROUNDED
(≥1 real ``Definition``). The (b) zero-definition member below is the closure proof
(RED against the over-grading ``claim_present=True``-always shape, GREEN under the
validator).

Complete-the-declared-set (AI-E5-1) — the FULL grading-input shape set:
  (a) clean-parsed Python, ≥1 def      → grounded  → audited_deep
  (b) clean-parsed Python, ZERO defs   → ungrounded → audited_shallow  (DF-1-7-B closure)
  (c) parse_failed=True Python         → skipped
  (d) ast_eligible=False non-Python    → claim_emitted proxy (non-deep, unchanged)
  (e) malformed / empty / None entry   → typed non-deep, NEVER an uncaught raise (AR10)
  (f) non-ASCII path / non-ASCII name  → grades + stable key under PYTHONIOENCODING=utf-8 (AI-E1-1)
"""

from __future__ import annotations

import pytest

from argus.audit.grounding import is_deep_claim_grounded
from argus.index.ast_index import AstIndexEntry, Definition
from argus.ledger.coverage_ledger import CoverageDepth, grade_entry
from argus.store import canonical


def _def(name: str = "compute", kind: str = "function") -> Definition:
    return Definition(name=name, kind=kind, start_line=1, end_line=2)


def _entry(
    *,
    file_path: str = "src/mod.py",
    ast_eligible: bool = True,
    parse_failed: bool = False,
    parse_failure_reason: str | None = None,
    definitions: tuple[Definition, ...] = (),
) -> AstIndexEntry:
    return AstIndexEntry(
        file_path=file_path,
        ast_eligible=ast_eligible,
        parse_failed=parse_failed,
        parse_failure_reason=parse_failure_reason,
        definitions=definitions,
    )


# ── (a) clean-parsed Python with ≥1 def → GROUNDED → audited_deep ───────────────


def test_clean_parse_with_one_def_is_grounded() -> None:
    """TC-ArgusAgent-AUDIT-001-46 — a clean-parse file with ≥1 real Definition is grounded (FR7)."""
    entry = _entry(definitions=(_def(),))
    assert is_deep_claim_grounded(entry) is True
    # Composed through the UNCHANGED grade_entry: present → audited_deep.
    graded = grade_entry(
        file_path=entry.file_path,
        proposed_depth=CoverageDepth.AUDITED_DEEP,
        claim_present=True and is_deep_claim_grounded(entry),
    )
    assert graded.depth is CoverageDepth.AUDITED_DEEP


def test_clean_parse_with_class_def_is_grounded() -> None:
    """TC-ArgusAgent-AUDIT-001-48 — a class definition also grounds the claim."""
    assert is_deep_claim_grounded(_entry(definitions=(_def(name="Calc", kind="class"),))) is True


def test_clean_parse_with_many_defs_is_grounded() -> None:
    """TC-ArgusAgent-AUDIT-001-49 — multiple defs ground the claim (the conservative bar is ≥1)."""
    entry = _entry(definitions=(_def(name="a"), _def(name="b", kind="class")))
    assert is_deep_claim_grounded(entry) is True


# ── (b) clean-parsed Python with ZERO defs → UNGROUNDED → audited_shallow ───────
#    The DF-1-7-B closure: RED against the over-grading shape, GREEN under FR7.


def test_zero_def_clean_parse_is_ungrounded_df_1_7_b_closure() -> None:
    """TC-ArgusAgent-AUDIT-001-50 — a clean-parse ZERO-definition module is UNGROUNDED (DF-1-7-B closure).

    The over-grading proof: the INTERIM shape (``claim_present=True`` always) graded
    this constants-only / re-export / docstring-only module ``audited_deep`` — RED,
    the DF-1-7-B over-grading. Under the FR7 validator the claim is ungrounded, so
    passing ``claim_present=(claim_emitted AND claim_grounded)`` downgrades it to
    ``audited_shallow`` — GREEN. This is the AI-E5-5 closure.
    """
    entry = _entry(file_path="src/constants.py", definitions=())

    # RED — the interim over-grading shape (claim_present=True always) graded it deep.
    interim = grade_entry(
        file_path=entry.file_path,
        proposed_depth=CoverageDepth.AUDITED_DEEP,
        claim_present=True,  # the FR6 presence proxy — the DF-1-7-B over-grading
    )
    assert interim.depth is CoverageDepth.AUDITED_DEEP  # the bug being removed

    # GREEN — the FR7 validator finds the claim ungrounded → audited_shallow.
    claim_grounded = is_deep_claim_grounded(entry)
    assert claim_grounded is False
    fr7 = grade_entry(
        file_path=entry.file_path,
        proposed_depth=CoverageDepth.AUDITED_DEEP,
        claim_present=True and claim_grounded,
    )
    assert fr7.depth is CoverageDepth.AUDITED_SHALLOW  # the over-grading removed


# ── (c) parse_failed=True Python → skipped (not grounded) ───────────────────────


def test_parse_failed_python_is_not_grounded() -> None:
    """TC-ArgusAgent-AUDIT-001-51 — a parse-failed Python file is never grounded → skipped path."""
    entry = _entry(
        file_path="src/broken.py",
        ast_eligible=False,
        parse_failed=True,
        parse_failure_reason="syntax_error",
        definitions=(),
    )
    assert is_deep_claim_grounded(entry) is False


def test_parse_failed_with_stale_definitions_still_not_grounded() -> None:
    """TC-ArgusAgent-AUDIT-001-52 — parse_failed wins even if a stale definitions tuple is present."""
    entry = _entry(
        file_path="src/broken.py",
        ast_eligible=False,
        parse_failed=True,
        parse_failure_reason="syntax_error",
        definitions=(_def(),),
    )
    assert is_deep_claim_grounded(entry) is False


# ── (d) ast_eligible=False non-Python → claim_emitted proxy (non-deep) ──────────


def test_non_python_routes_to_proxy_not_grounded() -> None:
    """TC-ArgusAgent-AUDIT-001-53 — a non-Python file (ast_eligible=False) routes to the proxy (NFR-P2)."""
    entry = _entry(
        file_path="README.md",
        ast_eligible=False,
        parse_failed=False,
        parse_failure_reason="non_python",
        definitions=(),
    )
    # The Python AST-grounding impl returns False; presence governs at the call site.
    assert is_deep_claim_grounded(entry) is False


# ── (e) malformed / empty / None entry → typed non-deep, NEVER an uncaught raise ─


@pytest.mark.parametrize(
    "bad",
    [
        None,
        object(),
        "not-an-entry",
        123,
        {"file_path": "x.py"},
        (),
        [],
    ],
)
def test_malformed_entry_never_raises_returns_false(bad: object) -> None:
    """TC-ArgusAgent-AUDIT-001-54 — a None / wrong-type / malformed entry → False, never a raise (AR10)."""
    assert is_deep_claim_grounded(bad) is False  # type: ignore[arg-type]


def test_empty_definitions_and_edges_is_not_grounded() -> None:
    """TC-ArgusAgent-AUDIT-001-55 — an empty-definitions clean entry is ungrounded (the (b) edge, typed)."""
    assert is_deep_claim_grounded(_entry(definitions=())) is False


# ── (f) non-ASCII path / non-ASCII Definition.name → stable grade + key (AI-E1-1) ─


def test_non_ascii_path_and_name_grounds_and_serializes_stably() -> None:
    """TC-ArgusAgent-AUDIT-001-56 — a non-ASCII path + non-ASCII Definition.name grounds + stable key (AI-E1-1)."""
    entry = _entry(
        file_path="src/café/модуль.py",
        definitions=(_def(name="вычислить", kind="function"),),
    )
    assert is_deep_claim_grounded(entry) is True

    graded = grade_entry(
        file_path=entry.file_path,
        proposed_depth=CoverageDepth.AUDITED_DEEP,
        claim_present=True and is_deep_claim_grounded(entry),
    )
    assert graded.depth is CoverageDepth.AUDITED_DEEP
    assert graded.file_path == "src/café/модуль.py"

    # The single ensure_ascii=False serializer renders the non-ASCII bytes verbatim
    # and is byte-stable across calls (NFR-P1 / AI-E1-1).
    once = canonical.dumps(graded.model_dump(mode="json"))
    twice = canonical.dumps(graded.model_dump(mode="json"))
    assert once == twice
    assert "café" in once
    assert "модуль" in once


# ── purity / no-float (AR8 / AR4) ───────────────────────────────────────────────


def test_validator_is_deterministic() -> None:
    """TC-ArgusAgent-AUDIT-001-57 — the same entry yields the same boolean (deterministic, pure)."""
    entry = _entry(definitions=(_def(),))
    assert is_deep_claim_grounded(entry) == is_deep_claim_grounded(entry)


def test_validator_returns_a_bool_not_a_count() -> None:
    """TC-ArgusAgent-AUDIT-001-58 — the grounding fact is a bool (no float / ratio — AR4)."""
    result = is_deep_claim_grounded(_entry(definitions=(_def(), _def(name="b"))))
    assert isinstance(result, bool)
