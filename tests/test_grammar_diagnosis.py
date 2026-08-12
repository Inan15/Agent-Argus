"""A grammar that fails to load must name WHY — and every arm must be reachable and registered.

Verification areas ArgusAgent-INDEX (``TC-ArgusAgent-INDEX-001-NN``),
ArgusAgent-REPORT (``TC-ArgusAgent-REPORT-002-NN``), ArgusAgent-DOCS
(``TC-ArgusAgent-DOCS-001-NN``). Story 10.4 / ``DF-AUD-APAA-F``.

What this file exists to stop
------------------------------
``_get_parser_for_lang`` wrapped the entire grammar load in
``except (ImportError, Exception): pass``. ``ImportError`` is a subclass of ``Exception``,
so that tuple is ``except Exception`` written to look like it discriminates — and the
redundancy was the tell. **Four** distinguishable failures collapsed into one token,
``grammar_missing_<lang>``, and three of the four implied a remedy that cannot work.
Measured on this tree 2026-08-10 against a ``.go`` fixture, patching only the
``importlib.import_module`` seam:

======================================  ================================  ==================
Simulated failure                       Recorded BEFORE                   Recorded AFTER
======================================  ================================  ==================
``ModuleNotFoundError`` on the package  ``grammar_missing_go``            ``grammar_missing_go``
entry point absent (``getattr``→None)   ``grammar_missing_go``            ``grammar_entrypoint_missing_go``
entry point / ``Language()`` raises     ``grammar_missing_go``            ``grammar_load_failed_go``
the ``tree_sitter`` CORE is broken      ``grammar_missing_go``            ``tree_sitter_runtime_missing``
======================================  ================================  ==================

Why a table of four is NOT the load-bearing assertion
------------------------------------------------------
Story 10.2's hand-written site list was wrong three times, and it recorded the lesson:
*the closure guard, not the site list, is what closes the class.* A four-row table closes
today's four instances. ``-111`` closes the class, by parsing
``argus/index/ast_index.py`` with the stdlib ``ast`` module and walking
``_get_parser_for_lang``'s **own control flow**: every ``except`` arm must be typed,
non-empty and non-redundant, and every ``return`` must hand back a **registered**
``GrammarFailure`` (or the single success). A fifth arm added later turns this red until
it is registered AND driven by ``-108``.

Why non-vacuity is mandatory here
----------------------------------
A source-walking guard goes green by finding nothing (Story 10.3's ``-39`` paid for this
lesson, and AI-E3-1 before it: this project has shipped a keystone test that was green over
its own keystone bug). ``-114`` fails if zero arms were walked, zero causes exercised, zero
classes registered, or if ``_get_parser_for_lang`` could not be located at all — a rename
must turn this red, never silently green.

RED evidence (AC5.8 / AC6.4), captured before any ``argus/`` edit — see the story's Dev
Agent Record for the raw output.
"""

from __future__ import annotations

import ast
import builtins
import importlib
import json
import sys
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pytest

pytest.importorskip("tree_sitter")

from argus.cache.key import CACHE_KEY_SCHEMA_VERSION  # noqa: E402
from argus.index import ast_index  # noqa: E402
from argus.index.ast_index import build_ast_index  # noqa: E402
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit  # noqa: E402
from argus.reports import generator as report_generator  # noqa: E402
from argus.shared.grammar_status import (  # noqa: E402
    CORE_PACKAGE,
    CORE_RUNTIME_TOKEN,
    GRAMMAR_PACKAGE_BY_LANGUAGE,
    GrammarDiagnosis,
    GrammarFailure,
    classify_reason,
    grammar_package_for,
    reason_token_for,
    registered_failures,
)
from argus.shared.source_languages import LANGUAGE_BY_SUFFIX  # noqa: E402

_LOADER_NAME = "_get_parser_for_lang"
_LOAD_RESULT_NAME = "_ParserLoad"
_LANG = "go"
_GRAMMAR_MODULE = f"tree_sitter_{_LANG}"
_CORE_MODULE = "tree_sitter"
_FIXTURE = "main.go"
_FIXTURE_SOURCE = "package main\n\nfunc Add(a int, b int) int { return a + b }\n"

#: A message shaped exactly like the real ABI failure, carrying a HOST FILESYSTEM PATH.
#: NFR-S1: no fragment of it may reach the persisted index (``-110``).
_HOST_PATH_MESSAGE = (
    "/home/operator/secret/lib/libtree_sitter_go.so: cannot open shared object file"
)

_ARCHITECTURE_DOC = (
    Path(__file__).resolve().parents[1]
    / "_bmad-output"
    / "design-artifacts"
    / "ArgusAgent"
    / "architecture.md"
)


# ─────────────────────────────────────────────────────────────────────────────
# The simulated failure modes — driven at the `importlib.import_module` seam
# ─────────────────────────────────────────────────────────────────────────────
#
# NEVER by uninstalling a real grammar and NEVER by mutating `_ENTRY_POINT_BY_LANGUAGE`:
# both make the test a statement about the machine instead of about the code, and the
# second would corrupt a module-level registry every other test in the session shares.


def _module_without_entry_point() -> types.ModuleType:
    """An installed grammar package that exports no entry point Argus knows.

    This is cause 2, and it is the one the ledger's stated repair (splitting the
    ``except``) does NOT catch — **nothing raises**. ``tree_sitter_typescript`` and
    ``tree_sitter_php`` were real instances of it (Story 10.2 / ``_ENTRY_POINT_BY_LANGUAGE``).
    """
    return types.ModuleType(_GRAMMAR_MODULE)


def _module_whose_entry_point_raises() -> types.ModuleType:
    """An installed grammar that is BROKEN for this runtime — the OSError shape."""
    mod = types.ModuleType(_GRAMMAR_MODULE)

    def language() -> object:
        raise OSError(_HOST_PATH_MESSAGE)

    mod.language = language  # type: ignore[attr-defined]
    return mod


def _module_with_a_substituted_grammar() -> types.ModuleType:
    """An installed grammar package that loads cleanly and is the WRONG GRAMMAR (cause 5).

    Story 11.4. Nothing is missing and nothing raises: ``Parser(Language(...))`` constructs
    perfectly and the parser then extracts something other than what Argus was validated
    against. This is the ONLY cause that can produce a false 🟢 — the other four leave the
    index empty, so the coverage floor already withholds the verdict.

    Simulated by handing the Go seam Python's grammar capsule, which is the shape a drifted,
    vendored, patched or mis-resolved grammar package actually has. ⛔ Never by installing or
    uninstalling a real package (§0.1.4; Story 10.4's E.3 rule).
    """
    import tree_sitter_python

    mod = types.ModuleType(_GRAMMAR_MODULE)
    mod.language = tree_sitter_python.language  # type: ignore[attr-defined]
    return mod


def _module_with_bad_capsule() -> types.ModuleType:
    """An installed grammar whose capsule ``Language()`` rejects.

    Measured on this host: ``Language(42)`` → ``ValueError('invalid language ID')``,
    ``Language(object())`` → ``TypeError('an integer is required')``. Cause 3 is "the parser
    could not be constructed", whichever of those the runtime happens to raise — which is
    why classification is by ARM POSITION and never by exception type (DN-4).
    """
    mod = types.ModuleType(_GRAMMAR_MODULE)
    mod.language = lambda: 42  # type: ignore[attr-defined]
    return mod


@dataclass(frozen=True)
class _Mode:
    """One simulated grammar-load outcome.

    ``failure`` is ``None`` for the success baseline. ``target`` names the module whose
    import is intercepted; ``behaviour`` either returns a stand-in module or raises.
    """

    name: str
    failure: GrammarFailure | None
    target: str | None
    behaviour: Callable[[], types.ModuleType] | None

    @property
    def expected_token(self) -> str | None:
        if self.failure is None:
            return None
        return reason_token_for(self.failure, _LANG)


def _raise_module_not_found() -> types.ModuleType:
    raise ModuleNotFoundError(f"No module named {_GRAMMAR_MODULE!r}")


def _raise_core_import_error() -> types.ModuleType:
    raise ImportError(f"No module named {_CORE_MODULE!r}")


_MODES: tuple[_Mode, ...] = (
    _Mode("baseline_grammar_loads", None, None, None),
    _Mode("package_missing", GrammarFailure.PACKAGE_MISSING, _GRAMMAR_MODULE, _raise_module_not_found),
    _Mode("entry_point_missing", GrammarFailure.ENTRY_POINT_MISSING, _GRAMMAR_MODULE, _module_without_entry_point),
    _Mode("load_failed_entry_raises", GrammarFailure.LOAD_FAILED, _GRAMMAR_MODULE, _module_whose_entry_point_raises),
    _Mode("load_failed_bad_capsule", GrammarFailure.LOAD_FAILED, _GRAMMAR_MODULE, _module_with_bad_capsule),
    _Mode("core_runtime_missing", GrammarFailure.CORE_RUNTIME_MISSING, _CORE_MODULE, _raise_core_import_error),
    _Mode(
        "runtime_unvalidated",
        GrammarFailure.RUNTIME_UNVALIDATED,
        _GRAMMAR_MODULE,
        _module_with_a_substituted_grammar,
    ),
)

_MODES_BY_NAME: dict[str, _Mode] = {mode.name: mode for mode in _MODES}

#: The FOUR causes in which no parser could be constructed at all. Story 11.4 added a fifth
#: (``RUNTIME_UNVALIDATED``) in which one COULD be — see ``-114``'s docstring for why the
#: two groups are asserted separately rather than merged or loosened.
_LOAD_FAILURE_CAUSES: frozenset[GrammarFailure] = frozenset(
    {
        GrammarFailure.PACKAGE_MISSING,
        GrammarFailure.ENTRY_POINT_MISSING,
        GrammarFailure.LOAD_FAILED,
        GrammarFailure.CORE_RUNTIME_MISSING,
    }
)


def _install_seam(monkeypatch: pytest.MonkeyPatch, mode: _Mode) -> None:
    """Intercept exactly ``mode.target``'s import; delegate every other import untouched.

    ``ast_index.importlib`` IS the real ``importlib`` package, so this patch is
    process-wide for the duration of the test — delegation is what keeps pytest, pydantic
    and every other importer working while it is installed. ``monkeypatch`` restores it.
    """
    if mode.target is None or mode.behaviour is None:
        return
    real = importlib.import_module
    target, behaviour = mode.target, mode.behaviour

    def hook(name: str, package: str | None = None) -> types.ModuleType:
        if name == target:
            return behaviour()
        return real(name, package)

    monkeypatch.setattr(ast_index.importlib, "import_module", hook)


def _run_mode(mode: _Mode, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> object:
    """Build a real index over a one-file Go repo under *mode*'s simulated failure."""
    root = tmp_path / mode.name
    root.mkdir(parents=True, exist_ok=True)
    (root / _FIXTURE).write_text(_FIXTURE_SOURCE, encoding="utf-8")
    with monkeypatch.context() as patch:
        _install_seam(patch, mode)
        return build_ast_index(root, (_FIXTURE,))


def _sole_entry(index: object) -> object:
    entries = getattr(index, "entries", ())
    assert len(entries) == 1, f"expected exactly one index entry, got {len(entries)}"
    return entries[0]


# ─────────────────────────────────────────────────────────────────────────────
# AC1 / AC5.1 — the behavioural matrix: every cause, its exact token
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("mode_name", sorted(_MODES_BY_NAME))
def test_each_grammar_failure_records_its_own_cause(
    mode_name: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TC-ArgusAgent-INDEX-001-108 — each of the four causes records ITS OWN token.

    Before Story 10.4 all four recorded ``grammar_missing_go``, so three of four operators
    were told to install a package they already had (or, for the core-runtime case, to
    install one language package while every language was down).
    """
    mode = _MODES_BY_NAME[mode_name]
    entry = _sole_entry(_run_mode(mode, tmp_path, monkeypatch))
    actual = getattr(entry, "parse_failure_reason", None)

    assert actual == mode.expected_token, (
        f"simulated mode {mode.name!r} recorded parse_failure_reason={actual!r}, expected "
        f"{mode.expected_token!r}. A degraded outcome must record the cause it ACTUALLY "
        f"had: the token is the operator's whole remedy. Fix the arm in "
        f"argus/index/{Path(ast_index.__file__).name}::{_LOADER_NAME} that handles this "
        f"failure, not this expectation."
    )

    if mode.failure is None:
        assert getattr(entry, "ast_eligible") is True, (
            "the success baseline did not ground — the seam itself is broken, so every "
            "other row in this matrix is meaningless (non-vacuity, E.4)."
        )


def test_grammar_missing_token_keeps_its_exact_spelling() -> None:
    """TC-ArgusAgent-INDEX-001-109 — cause 1's token is UNCHANGED, spelling and meaning.

    The epic requires it ("a missing package keeps ``grammar_missing_<lang>``"),
    ``TC-ArgusAgent-INDEX-001-73`` pins it, and the report's remedy for it — a single
    ``pip install`` — is the one remedy that was always correct. Renaming it would break
    the one case that never needed fixing.
    """
    assert reason_token_for(GrammarFailure.PACKAGE_MISSING, "go") == "grammar_missing_go"
    assert reason_token_for(GrammarFailure.ENTRY_POINT_MISSING, "go") == "grammar_entrypoint_missing_go"
    assert reason_token_for(GrammarFailure.LOAD_FAILED, "go") == "grammar_load_failed_go"
    assert reason_token_for(GrammarFailure.CORE_RUNTIME_MISSING) == "tree_sitter_runtime_missing"

    # Cause 4 carries NO language suffix: the core being down is not a fact about one
    # language, and a suffix would invite exactly the wrong single-package remedy.
    assert CORE_RUNTIME_TOKEN == "tree_sitter_runtime_missing"
    assert not CORE_RUNTIME_TOKEN.endswith("_go")

    # The classifier is the ONLY parser of these tokens (AC3.3 / AC6.1).
    assert classify_reason("grammar_missing_go") == GrammarDiagnosis(GrammarFailure.PACKAGE_MISSING, "go")
    assert classify_reason("grammar_entrypoint_missing_go") == GrammarDiagnosis(
        GrammarFailure.ENTRY_POINT_MISSING, "go"
    )
    assert classify_reason("grammar_load_failed_go") == GrammarDiagnosis(GrammarFailure.LOAD_FAILED, "go")
    assert classify_reason(CORE_RUNTIME_TOKEN) == GrammarDiagnosis(GrammarFailure.CORE_RUNTIME_MISSING, None)

    # …and it must NOT claim tokens that are not grammar-load failures. A `syntax_error`
    # given a "pip install" remedy is this story's own defect, pointed the other way.
    for unrelated in ("syntax_error", "parser_error", "read_error", "non_python", "", None):
        assert classify_reason(unrelated) is None, (
            f"{unrelated!r} is not a grammar-load failure but classify_reason claimed it. "
            "It would be handed a grammar remedy it cannot use."
        )


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — the degradation itself is unchanged, per cause
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("mode_name", sorted(n for n, m in _MODES_BY_NAME.items() if m.failure is not None))
def test_degradation_shape_is_identical_for_every_cause(
    mode_name: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TC-ArgusAgent-INDEX-001-110 — naming the cause changes the RECORD, never the GRADE.

    ``parse_failed`` stays ``False`` for all four: the flag means *a parse was attempted and
    failed*, and no parse is attempted when no parser exists (the convention ``non_python``
    already follows). Flipping it would move the coverage denominator — a verdict change
    this story is explicitly fenced against (DN-6 / DN-9).
    """
    mode = _MODES_BY_NAME[mode_name]
    index = _run_mode(mode, tmp_path, monkeypatch)
    entry = _sole_entry(index)

    assert getattr(entry, "ast_eligible") is False, f"{mode.name}: a failed grammar must not be ast_eligible"
    assert getattr(entry, "parse_failed") is False, (
        f"{mode.name}: parse_failed flipped to True. No parse was ATTEMPTED — there was no "
        "parser — so this would move the coverage denominator and turn a diagnosis fix into "
        "a verdict change (DN-6)."
    )
    assert getattr(entry, "definitions") == (), f"{mode.name}: a file that never parsed cannot yield definitions"
    assert getattr(entry, "edges") == (), f"{mode.name}: a file that never parsed cannot yield edges"

    # AC4.3 — a grammar that never parsed contributes NO provenance row. The cache key is a
    # function of the AUDIT, not of the host (Story 10.2 / DN-6).
    assert getattr(index, "grammar_versions") == (), (
        f"{mode.name}: a grammar that failed to load recorded a GrammarProvenance row. It "
        "never parsed anything, so it cannot vouch for this index."
    )
    assert getattr(index, "schema_version") == "2", (
        f"{mode.name}: AstIndex.schema_version moved. Story 10.4 adds NO field (DN-5); a "
        "silent schema bump is the cache-invalidation class DF-5-1-A files."
    )


def test_no_schema_or_cache_key_version_moved() -> None:
    """TC-ArgusAgent-INDEX-001-111 — no field added, no schema bump, no cache-key move (AC3.4).

    Story 10.2 spent both bumps deliberately (``AstIndex`` 1→2, cache key 2→3). Spending a
    second one inside the same epic, on a 🟢 diagnosis fix, would invalidate every cached
    audit for no behavioural gain.
    """
    from argus.index.ast_index import AstIndex, AstIndexEntry

    assert AstIndex.model_fields["schema_version"].default == "2"
    assert CACHE_KEY_SCHEMA_VERSION == "3"
    assert set(AstIndexEntry.model_fields) == {
        "file_path",
        "ast_eligible",
        "parse_failed",
        "parse_failure_reason",
        "definitions",
        "edges",
    }, (
        "AstIndexEntry gained or lost a field. DN-5 locks the shape: the epic asks for a "
        "distinct TOKEN, not a detail payload, and a persisted free-text slot's only natural "
        "filler is str(exc) — a host path, breaching NFR-S1."
    )


def test_no_exception_detail_or_host_path_is_persisted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TC-ArgusAgent-INDEX-001-112 — NFR-S1: the exception's message never reaches the index (AC2.5).

    The realistic broken-grammar failure is ``OSError('/home/…/libfoo.so: cannot open shared
    object file')``. Recording ``str(exc)`` to be "helpful" would write a host filesystem path
    into a persisted, shareable artifact — the containment rule Stories 2.5 and 4.4 are built
    on. Asserted against the WHOLE serialized index, not just the one field, because a leak
    that lands anywhere is still a leak.
    """
    mode = _MODES_BY_NAME["load_failed_entry_raises"]
    index = _run_mode(mode, tmp_path, monkeypatch)
    serialized = index.model_dump_json()  # type: ignore[attr-defined]

    # Round-trips as JSON, so the assertion is over what actually gets written.
    json.loads(serialized)

    for fragment in (
        _HOST_PATH_MESSAGE,
        "/home/operator",
        "libtree_sitter_go.so",
        "cannot open shared object file",
        "OSError",
        "Traceback",
    ):
        assert fragment not in serialized, (
            f"the serialized AstIndex contains {fragment!r}. An exception's message, repr or "
            "traceback must never be persisted: it carries host filesystem paths (NFR-S1). "
            "Classify by ARM POSITION and record a token, not a detail (DN-4/DN-5)."
        )

    assert _sole_entry(index).parse_failure_reason == "grammar_load_failed_go"  # type: ignore[attr-defined]


def test_keyboard_interrupt_still_propagates_out_of_the_loader(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-ArgusAgent-INDEX-001-113 — AR10 degrades ERRORS, never SIGNALS (AC2.4).

    ``BaseException`` is not caught today and must stay uncaught: an operator pressing
    ctrl-c during a grammar load must interrupt the audit, not be swallowed into a
    ``grammar_load_failed_go`` record and a cheerfully-continuing run. A guard assertion,
    not a hope.
    """
    real = importlib.import_module

    def hook(name: str, package: str | None = None) -> types.ModuleType:
        if name == _GRAMMAR_MODULE:
            mod = types.ModuleType(_GRAMMAR_MODULE)

            def language() -> object:
                raise KeyboardInterrupt("operator pressed ctrl-c")

            mod.language = language  # type: ignore[attr-defined]
            return mod
        return real(name, package)

    monkeypatch.setattr(ast_index.importlib, "import_module", hook)

    with pytest.raises(KeyboardInterrupt):
        getattr(ast_index, _LOADER_NAME)(_LANG, "language")


def test_verdict_and_coverage_are_identical_across_all_four_causes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TC-ArgusAgent-INDEX-001-114 — AC4.2: the graded outcome does not move (DN-9).

    Before Story 10.4 all four causes produced the same record, so they necessarily
    produced the same grade. Splitting the token must leave that invariant intact: the
    pipeline and the grounding audit branch on the ``parse_failed`` / ``ast_eligible``
    BOOLEANS, never on the token, and this asserts they still do. A divergence here means
    the token reached a decision — a 🟢 diagnosis story turned into a release-integrity change.

    ⚠️ NARROWED BY STORY 11.4, DELIBERATELY AND WITH A REASON (11.4 AC4.1 / DN-10; 10.4's
    own DN-9 fenced the version comparison TO 11.4 by name, so this is the sanctioned
    crossing, not a regression). The scope is now the **four LOAD causes** — the ones in
    which no parser could be constructed — held to the invariant they always had. It is
    narrowed by an explicit membership set with an asserted count, **never** by deleting the
    test and never by loosening the equality: a scope that could silently shrink to one
    cause would pass trivially, which is the failure mode 10.3's ``-39`` paid for.

    11.4's fifth cause is asserted SEPARATELY below. Its recorded shape is deliberately the
    same (DN-2: no new verdict, no new row, no ``verdict_gate.py`` change) — what differs is
    the STATE it fires from. Cause 5 fires where a parser WAS constructible, i.e. exactly
    where the other four cannot fire and where the run would otherwise have produced a
    confident verdict. That difference is only visible above the 60% deep gate, and it is
    measured there by
    ``tests/test_grammar_runtime_validation.py::…-121`` — not here, where the one-file Go
    fixture is below the floor by construction.
    """
    graded: dict[str, tuple[object, ...]] = {}
    for mode in _MODES:
        if mode.failure is None or mode.failure not in _LOAD_FAILURE_CAUSES:
            continue
        root = tmp_path / f"repo_{mode.name}"
        root.mkdir(parents=True, exist_ok=True)
        (root / "go.mod").write_text("module example.com/app\n\ngo 1.21\n", encoding="utf-8")
        (root / _FIXTURE).write_text(_FIXTURE_SOURCE, encoding="utf-8")

        with monkeypatch.context() as patch:
            _install_seam(patch, mode)
            verdict = run_audit(
                AuditRequest(repo_path=str(root), commit="HEAD", budget=100, materiality_bar="default")
            )
        graded[mode.name] = (
            verdict.verdict,
            verdict.total_count,
            verdict.deep_count,
            tuple(sorted(f.rule_id for f in verdict.ordered_findings)),
        )

    driven_load_causes = {_MODES_BY_NAME[name].failure for name in graded}
    assert driven_load_causes == _LOAD_FAILURE_CAUSES, (
        f"the load-cause scope drifted: drove {sorted(f.value for f in driven_load_causes)}, "
        f"expected {sorted(f.value for f in _LOAD_FAILURE_CAUSES)}. Narrowing this test is "
        "allowed ONLY as a deliberate, counted decision (11.4 AC4.1); a scope that quietly "
        "shrinks makes the equality below pass over nothing."
    )
    assert len(_LOAD_FAILURE_CAUSES) == 4, (
        f"{len(_LOAD_FAILURE_CAUSES)} load causes, expected exactly 4. A fifth LOAD cause "
        "belongs in this invariant; 11.4's RUNTIME_UNVALIDATED is not one — a parser WAS "
        "constructed — so it is asserted separately rather than folded in here."
    )
    assert len(graded) >= 4, "fewer than four causes were graded — the matrix went vacuous (E.4)"
    distinct = set(graded.values())
    assert len(distinct) == 1, (
        "the four grammar-LOAD causes produced DIFFERENT graded outcomes: "
        f"{json.dumps({k: str(v) for k, v in graded.items()}, indent=2)}. Naming the cause "
        "must change the EVIDENCE, never the verdict (DN-9). Something downstream is "
        "branching on the reason token instead of on ast_eligible/parse_failed."
    )

    # ── Story 11.4's fifth cause, asserted SEPARATELY (AC4.1) ────────────────────────
    # Its recorded shape matches the four (DN-2 routes it into the SAME floor row rather
    # than inventing a verdict), and that sameness is the load-bearing claim: it is what
    # lets the story change no decision-table row. What is deliberately different is where
    # it fires from — a toolchain that WAS constructible — and that is measured above the
    # deep gate in tests/test_grammar_runtime_validation.py::…-121.
    unvalidated = _MODES_BY_NAME["runtime_unvalidated"]
    assert unvalidated.failure not in _LOAD_FAILURE_CAUSES, (
        "RUNTIME_UNVALIDATED was folded into the load-cause set. It is not a load failure — "
        "the parser constructed — and merging it would hide the one cause that can produce a "
        "false 🟢 behind an invariant written for the four that cannot."
    )
    root = tmp_path / "repo_runtime_unvalidated"
    root.mkdir(parents=True, exist_ok=True)
    (root / "go.mod").write_text("module example.com/app\n\ngo 1.21\n", encoding="utf-8")
    (root / _FIXTURE).write_text(_FIXTURE_SOURCE, encoding="utf-8")
    with monkeypatch.context() as patch:
        _install_seam(patch, unvalidated)
        fifth = run_audit(
            AuditRequest(repo_path=str(root), commit="HEAD", budget=100, materiality_bar="default")
        )
    assert (
        fifth.verdict,
        fifth.total_count,
        fifth.deep_count,
        tuple(sorted(f.rule_id for f in fifth.ordered_findings)),
    ) == distinct.pop(), (
        "the fifth cause produced a DIFFERENT graded shape from the four load causes. DN-2 "
        "routes it into the existing floor row precisely so that no new verdict, row or "
        "threshold is introduced; a divergence here means verdict_gate.py or pipeline.py was "
        "touched after all."
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC5.2 — 🔑 the closure: over the function's own control flow, not over a list
# ─────────────────────────────────────────────────────────────────────────────


def _find_function(tree: ast.AST, name: str) -> ast.FunctionDef | None:
    """Locate a top-level-or-nested ``def name`` in a parsed module (PURE, total)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def _loader_ast() -> ast.FunctionDef:
    """``_get_parser_for_lang``'s own AST, or a LOUD failure.

    Never returns an empty node set: if the function is renamed or moved, this fails
    rather than silently walking nothing (E.4 / AC5.5).
    """
    source = Path(ast_index.__file__).read_text(encoding="utf-8")
    function = _find_function(ast.parse(source), _LOADER_NAME)
    if function is None:
        pytest.fail(
            f"{_LOADER_NAME} was not found in {ast_index.__file__}. This guard closes over "
            "that function's own control flow, so a rename or move makes it vacuous. Point "
            "_LOADER_NAME at the new name — do NOT delete this assertion."
        )
    return function


def _handler_exception_names(handler: ast.ExceptHandler) -> list[str]:
    """The exception names a handler catches, flattened out of tuples (PURE)."""
    caught = handler.type
    if caught is None:
        return []
    nodes = caught.elts if isinstance(caught, ast.Tuple) else [caught]
    names: list[str] = []
    for node in nodes:
        if isinstance(node, ast.Name):
            names.append(node.id)
        elif isinstance(node, ast.Attribute):
            names.append(node.attr)
    return names


def _is_lone_pass(handler: ast.ExceptHandler) -> bool:
    """True when a handler's whole body is ``pass`` or ``...`` — a swallowed failure (PURE)."""
    if len(handler.body) != 1:
        return False
    only = handler.body[0]
    if isinstance(only, ast.Pass):
        return True
    return isinstance(only, ast.Expr) and isinstance(only.value, ast.Constant) and only.value.value is Ellipsis


def _redundant_pairs(names: list[str]) -> list[tuple[str, str]]:
    """Pairs in a caught tuple where one member SUBCLASSES the other (PURE).

    ``except (ImportError, Exception)`` is the shape this story removes: it reads like two
    discriminated arms and is ``except Exception``. Resolving the names against ``builtins``
    makes the check structural rather than a blocklist of one spelling.
    """
    redundant: list[tuple[str, str]] = []
    for outer in names:
        for inner in names:
            if outer == inner:
                continue
            outer_cls = getattr(builtins, outer, None)
            inner_cls = getattr(builtins, inner, None)
            if not (isinstance(outer_cls, type) and isinstance(inner_cls, type)):
                continue
            if issubclass(outer_cls, inner_cls):
                redundant.append((outer, inner))
    return redundant


def _returned_failure_names(function: ast.FunctionDef) -> tuple[list[str], int, int]:
    """Walk every ``return`` in *function*: (registered failure names, success returns, total).

    THE CLOSURE. Every exit must hand back ``_ParserLoad(<parser>, GrammarFailure.X)`` or
    ``_ParserLoad(<parser>, None)``. A fifth arm returning a bare ``None``, or a
    ``GrammarFailure`` member that is not registered, cannot pass.
    """
    failures: list[str] = []
    successes = 0
    total = 0
    for node in ast.walk(function):
        if not isinstance(node, ast.Return):
            continue
        total += 1
        value = node.value
        assert isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id == _LOAD_RESULT_NAME, (
            f"{_LOADER_NAME} has a `return` that is not a {_LOAD_RESULT_NAME}(...) call "
            f"(line {node.lineno}). Every exit from the loader must carry its cause, or an "
            "arm can leave without recording why it failed — the defect this story closes."
        )
        assert len(value.args) == 2, (
            f"{_LOAD_RESULT_NAME}(...) at line {node.lineno} takes (parser, failure); got "
            f"{len(value.args)} positional arg(s)."
        )
        marker = value.args[1]
        if isinstance(marker, ast.Constant) and marker.value is None:
            successes += 1
            continue
        assert (
            isinstance(marker, ast.Attribute)
            and isinstance(marker.value, ast.Name)
            and marker.value.id == GrammarFailure.__name__
        ), (
            f"the failure slot at line {node.lineno} is not a {GrammarFailure.__name__} "
            "member. Classification must come from the shared registry so the producer and "
            "the report cannot drift (AC3.1)."
        )
        failures.append(marker.attr)
    return failures, successes, total


def test_loader_has_no_unnamed_swallowed_or_redundant_arm() -> None:
    """TC-ArgusAgent-INDEX-001-115 — 🔑 the closure over the loader's own control flow (AC5.2).

    A hand-written table of four causes closes today's four instances. This closes the
    CLASS: it walks ``_get_parser_for_lang``'s own AST and refuses any arm that is bare,
    silent, redundant, catches a signal, or exits without a registered cause. A fifth arm
    added later turns this red until it is registered in ``GrammarFailure`` — which is the
    point, because registration is meant to cost a deliberate edit (Story 10.3's precedent).
    """
    function = _loader_ast()
    handlers = [node for node in ast.walk(function) if isinstance(node, ast.ExceptHandler)]

    assert handlers, (
        f"{_LOADER_NAME} contains no `except` handler at all. Either the loader no longer "
        "guards its imports (a crash out of the builder, breaching AR10) or this walk is "
        "vacuous. Both are failures."
    )

    for handler in handlers:
        names = _handler_exception_names(handler)

        assert handler.type is not None, (
            f"bare `except:` at line {handler.lineno} in {_LOADER_NAME}. architecture.md:698 "
            "and AR10 forbid it by name — it catches KeyboardInterrupt and SystemExit too."
        )
        assert not _is_lone_pass(handler), (
            f"the handler at line {handler.lineno} in {_LOADER_NAME} is a lone `pass`/`...`. "
            "Every caught exception must produce a RECORDED outcome (AR10, architecture.md:698, "
            "Story 4.3). `except …: pass` is how four different failures came to share one "
            "token and three wrong remedies."
        )

        redundant = _redundant_pairs(names)
        assert not redundant, (
            f"the handler at line {handler.lineno} in {_LOADER_NAME} catches a REDUNDANT "
            f"tuple {names}: {redundant[0][0]} is a subclass of {redundant[0][1]}, so the "
            "tuple reads like it discriminates and does not. That exact shape — "
            "`except (ImportError, Exception)` — was the tell that four causes had collapsed "
            "into one token. Split the arms by POSITION instead."
        )

        for signal in ("BaseException", "KeyboardInterrupt", "SystemExit"):
            assert signal not in names, (
                f"{_LOADER_NAME} catches {signal} at line {handler.lineno}. AR10 degrades "
                "ERRORS, never SIGNALS: ctrl-c during a grammar load must interrupt the audit, "
                "not be recorded as a broken grammar (see -113)."
            )

    failures, successes, total = _returned_failure_names(function)
    registered = {failure.name for failure in registered_failures()}

    assert successes == 1, (
        f"{_LOADER_NAME} has {successes} success exits, expected exactly 1. More than one "
        "means a parser can be returned from an unaudited path."
    )
    assert total >= len(registered) + 1, (
        f"{_LOADER_NAME} has only {total} exits for {len(registered)} registered failure "
        "classes plus one success — an arm is missing, or several share one exit and can no "
        "longer be told apart."
    )

    unregistered = sorted(set(failures) - registered)
    assert not unregistered, (
        f"{_LOADER_NAME} returns GrammarFailure member(s) {unregistered} that are not "
        "registered in argus/shared/grammar_status.py. The producer and the report read the "
        "SAME registry; an unregistered cause reaches the operator as no callout at all."
    )

    unreached = sorted(registered - set(failures))
    assert not unreached, (
        f"registered failure class(es) {unreached} are never returned by {_LOADER_NAME}. "
        "A class nothing can produce is an unread seam (the DF-6-7-A defect class); either "
        "wire the arm or delete the member."
    )


def test_registry_and_behavioural_matrix_close_over_each_other(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TC-ArgusAgent-INDEX-001-116 — the registry and the matrix are the SAME set (AC5.3).

    Both directions, because either alone is a false green: a class registered and never
    driven is untested, and a token observed and never registered reaches the report as
    silence. Story 10.3 proved the same pair on the CLI surface.
    """
    observed: dict[str, GrammarFailure] = {}
    for mode in _MODES:
        if mode.failure is None:
            continue
        entry = _sole_entry(_run_mode(mode, tmp_path, monkeypatch))
        diagnosis = classify_reason(getattr(entry, "parse_failure_reason", None))
        assert diagnosis is not None, (
            f"mode {mode.name!r} recorded "
            f"{getattr(entry, 'parse_failure_reason', None)!r}, which the shared classifier "
            "does not recognise as a grammar-load failure. An unclassifiable token is "
            "invisible to the report — the operator sees NOTHING."
        )
        observed[mode.name] = diagnosis.failure

    registered = registered_failures()
    driven = set(observed.values())

    assert observed, "no failure mode was exercised at all (non-vacuity, E.4)"

    undriven = sorted(failure.value for failure in registered - driven)
    assert not undriven, (
        f"failure class(es) {undriven} are registered but no mode in _MODES drives them. "
        "Add a simulated mode: an untested class is how AC6's target lines went a whole "
        "epic without executing."
    )

    unregistered = sorted(failure.value for failure in driven - registered)
    assert not unregistered, (
        f"mode(s) produced failure class(es) {unregistered} that registered_failures() does "
        "not know. The report classifies through that registry, so this reaches an operator "
        "as no callout at all."
    )


def test_registry_closure_positive_control_both_directions() -> None:
    """TC-ArgusAgent-INDEX-001-117 — the closure FIRES on a fault and stays quiet otherwise (AC5.4).

    A guard that cannot fail is not a guard (AI-E3-1: this project shipped a keystone test
    that was green over its own keystone bug). Pure functions over SYNTHETIC inputs — never
    by uninstalling a real grammar and never by mutating the shared registry.
    """
    # Direction 1 — an observed token no registered class explains must be caught.
    assert classify_reason("grammar_frobnicated_go") is None, (
        "an unregistered token classified as a known failure — the closure cannot detect a "
        "fifth cause, so registration would stop costing anything."
    )
    assert classify_reason("grammar_load_failed_go") is not None, (
        "a REGISTERED token failed to classify — the control is inverted and every 'no "
        "unregistered tokens' result above is meaningless."
    )

    # Direction 2 — a registered class that nothing drives must be caught. This is the exact
    # set arithmetic -116 relies on, exercised on a KNOWN-short "driven" set so the assertion
    # there cannot be quietly comparing something that is always empty.
    registered = registered_failures()
    assert registered, "registered_failures() is empty — every closure above is vacuous"
    driven_short = set(registered) - {GrammarFailure.CORE_RUNTIME_MISSING}
    assert sorted(f.value for f in registered - driven_short) == ["core_runtime_missing"], (
        "the 'registered but undriven' difference does not surface a missing class; -116's "
        "undriven assertion would never fire."
    )
    assert sorted(f.value for f in registered - set(registered)) == [], (
        "the same difference reports a phantom gap when every class IS driven — -116 would "
        "fail on correct code and get weakened away."
    )

    # Direction 3 — the AST walker itself must fail loudly on a module that lacks the loader.
    assert _find_function(ast.parse("x = 1\n"), _LOADER_NAME) is None, (
        "_find_function claimed to locate a function in a module that has none — a rename "
        "of the loader would then pass silently over an empty node set (E.4)."
    )
    assert _find_function(ast.parse(f"def {_LOADER_NAME}():\n    pass\n"), _LOADER_NAME) is not None, (
        "_find_function cannot locate a function that IS present — the control is inverted."
    )

    # Direction 4 — the structural checks fire on the exact shape this story removed.
    removed_shape = ast.parse(
        "def f():\n"
        "    try:\n"
        "        pass\n"
        "    except (ImportError, Exception):\n"
        "        pass\n"
    )
    handler = next(node for node in ast.walk(removed_shape) if isinstance(node, ast.ExceptHandler))
    names = _handler_exception_names(handler)
    assert names == ["ImportError", "Exception"]
    assert _redundant_pairs(names) == [("ImportError", "Exception")], (
        "the redundancy check does not fire on `except (ImportError, Exception)` — the exact "
        "shape Story 10.4 exists to remove could come straight back."
    )
    assert _is_lone_pass(handler), "the lone-`pass` check does not fire on a `pass` body"

    kept_shape = ast.parse(
        "def f():\n"
        "    try:\n"
        "        pass\n"
        "    except (ImportError, AttributeError):\n"
        "        return 1\n"
    )
    kept = next(node for node in ast.walk(kept_shape) if isinstance(node, ast.ExceptHandler))
    assert _redundant_pairs(_handler_exception_names(kept)) == [], (
        "the redundancy check fires on `except (ImportError, AttributeError)`, which is a "
        "legitimate two-arm catch — neither is a subclass of the other. A guard that flags "
        "correct code gets weakened away."
    )
    assert not _is_lone_pass(kept), "the lone-`pass` check fires on a handler that returns"


def test_this_guard_cannot_pass_vacuously() -> None:
    """TC-ArgusAgent-INDEX-001-118 — non-vacuity, asserted rather than assumed (AC5.5 / E.4).

    Story 10.3's ``-39`` exists because a source-walking guard goes green by finding
    nothing. Every count this file depends on is pinned here, so deleting a mode, emptying
    the registry or renaming the loader turns the suite RED instead of quiet.
    """
    assert len(_MODES) >= 6, f"only {len(_MODES)} simulated modes — the five causes plus a baseline are the floor"
    assert any(mode.failure is None for mode in _MODES), "no success baseline: a seam that never works looks like a pass"
    assert {mode.failure for mode in _MODES if mode.failure is not None} == registered_failures(), (
        "the mode table and the registry have drifted apart; -116's both-direction closure "
        "is comparing something other than the registered causes."
    )

    assert len(registered_failures()) == 5, (
        f"{len(registered_failures())} failure classes registered, expected the five measured "
        "causes (10.4's four load causes + Story 11.4's RUNTIME_UNVALIDATED). A sixth is fine "
        "— register it, drive it in _MODES, give it a remedy in the report, and update this "
        "number deliberately. Updating it is the point: registration must cost an edit."
    )
    assert _LOAD_FAILURE_CAUSES < registered_failures(), (
        "the load-cause subset -114 narrows to is no longer a PROPER subset of the registry. "
        "Either the fifth cause was deleted or -114 quietly re-absorbed it (11.4 DN-10)."
    )

    function = _loader_ast()
    handlers = [node for node in ast.walk(function) if isinstance(node, ast.ExceptHandler)]
    assert len(handlers) >= 2, (
        f"{_LOADER_NAME} has {len(handlers)} except handler(s). The core import and the "
        "parser construction are different failures with different remedies and cannot share one."
    )
    _, successes, total = _returned_failure_names(function)
    assert total >= 5 and successes == 1, (
        f"{_LOADER_NAME} exposes {total} exit(s) with {successes} success(es) — the walk in "
        "-115 has nothing to close over."
    )

    assert _ARCHITECTURE_DOC.is_file(), (
        f"architecture.md not found at {_ARCHITECTURE_DOC} — -119 would pass by never reading it."
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC5.7 — the rule lives in the document AND in this test
# ─────────────────────────────────────────────────────────────────────────────


def test_degradation_rule_and_guard_are_registered_in_architecture() -> None:
    """TC-ArgusAgent-DOCS-001-29 — the rule is written down and this guard is named (AC5.7).

    A rule that lives only in a test is not a rule; a rule that lives only in prose is not
    enforced. Story 10.1's ``-23`` and Story 10.3's ``-28`` established this pairing; this
    is Story 10.4's.
    """
    text = _ARCHITECTURE_DOC.read_text(encoding="utf-8")

    for anchor, why in (
        (
            "a degraded outcome records the cause it actually had",
            "the §Error/Degradation rule Story 10.4 establishes",
        ),
        (
            "a recorded reason token names a remedy that works",
            "the second half of that rule — a token whose remedy cannot work is a named "
            "reason in form only",
        ),
        (
            "tests/test_grammar_diagnosis.py",
            "this guard's registration in §Enforcement, beside 10.1's, 10.2's and 10.3's",
        ),
        (
            "### Error / Degradation Patterns",
            "the section the rule belongs to",
        ),
        (
            "### Enforcement",
            "the section the guard is registered in",
        ),
    ):
        assert anchor in text, (
            f"architecture.md no longer contains {anchor!r} — {why}. Restore it: the "
            "governing document and the executable guard must not drift apart."
        )


# ─────────────────────────────────────────────────────────────────────────────
# AC6 — the ONE surface an operator sees: not silent, not misdirecting
# ─────────────────────────────────────────────────────────────────────────────
#
# Measured 2026-08-10 with `pytest --cov=argus.reports.generator` over every test file that
# imports the generator: lines 322-336 — the whole grammar-counting block, the package
# lookup and the callout body — reported **Missing**. The only message about a failed
# grammar that ever reaches an operator had NEVER executed in this suite. Splitting the
# token without these tests would have silently disabled it and turned nothing red.


def _index_stub(reasons: dict[str, int]) -> object:
    """A minimal duck-typed AstIndex carrying *reasons* → count (PURE, synthetic).

    ``_render_readability_warning`` reads its argument by ``getattr``, so a stub is the
    honest unit here and keeps the mixed-class case reachable without six monkeypatched
    grammar loads.
    """

    class _Entry:
        def __init__(self, path: str, reason: str) -> None:
            self.file_path = path
            self.ast_eligible = False
            self.parse_failed = False
            self.parse_failure_reason = reason
            self.definitions: tuple[object, ...] = ()
            self.edges: tuple[object, ...] = ()

    class _Index:
        def __init__(self) -> None:
            entries: list[_Entry] = []
            for reason, count in reasons.items():
                for n in range(count):
                    entries.append(_Entry(f"{reason}_{n}.src", reason))
            self.entries = tuple(entries)

    return _Index()


def _callout(reasons: dict[str, int]) -> str:
    from argus.ledger.coverage_ledger import CoverageLedger

    lines = report_generator._render_readability_warning(CoverageLedger(entries=()), _index_stub(reasons))
    return "\n".join(lines)


def test_grammar_package_table_covers_every_enumerable_language() -> None:
    """TC-ArgusAgent-REPORT-002-25 — an eleventh language cannot be added to one table only (AC6.6).

    The package table moved out of ``generator.py`` into the shared pure module (Story 10.4
    decision DEV-2): the report's remedy and the producer's classification now read one
    table. Pinned against ``LANGUAGE_BY_SUFFIX``'s value set so the move cannot rot.
    """
    assert set(GRAMMAR_PACKAGE_BY_LANGUAGE) == set(LANGUAGE_BY_SUFFIX.values()), (
        "the grammar-package table and the enumerable language set have diverged: "
        f"{sorted(set(LANGUAGE_BY_SUFFIX.values()) ^ set(GRAMMAR_PACKAGE_BY_LANGUAGE))}. A "
        "language Argus enumerates but cannot name a package for gets a remedy the operator "
        "cannot run."
    )
    assert not hasattr(report_generator, "_GRAMMAR_PACKAGE_BY_LANGUAGE"), (
        "generator.py still carries its own copy of the package table. Two copies is how the "
        "suffix map came to exist four times (argus/shared/source_languages.py:9-25)."
    )
    for language, package in GRAMMAR_PACKAGE_BY_LANGUAGE.items():
        assert package == f"tree-sitter-{language}", f"{language} → {package} breaks the published naming convention"
    assert grammar_package_for("go") == "tree-sitter-go"
    assert CORE_PACKAGE == "tree-sitter"


def test_every_cause_reaches_the_operator_with_a_remedy_that_works() -> None:
    """TC-ArgusAgent-REPORT-002-26 — the callout does not go SILENT and does not MISDIRECT (AC6.2).

    This is the story's whole point delivered at the only surface that has it. Before Story
    10.4 the report recovered the language by string arithmetic on ``grammar_missing_``:
    ``grammar_entrypoint_missing_go`` does not start with that prefix, so it would have been
    skipped entirely (SILENT); a naive widening to ``grammar_`` would have sliced it into the
    "language" ``entrypoint_missing_go`` and printed
    ``pip install tree-sitter-entrypoint_missing_go`` (MISDIRECT).
    """
    # Cause 1 — the ONE case whose remedy was always a pip install.
    text = _callout({"grammar_missing_go": 2})
    assert text, "cause 1 produced NO callout — the operator is told nothing at all"
    assert "pip install tree-sitter-go" in text
    assert "go" in text

    # Cause 2 — an Argus defect. It must NOT tell the operator to install what they have.
    text = _callout({"grammar_entrypoint_missing_php": 1})
    assert text, (
        "cause 2 produced NO callout. `grammar_entrypoint_missing_php` does not start with "
        "`grammar_missing_`, so a prefix-arithmetic reader skips it silently — the exact "
        "regression AC6 exists to prevent."
    )
    assert "pip install tree-sitter-php" not in text, (
        "cause 2's callout tells the operator to install a package they ALREADY HAVE. That "
        "sentence is the DF-AUD-APAA-F harm, reintroduced by the story meant to fix it."
    )
    assert "entrypoint_missing" not in text, (
        "the raw token leaked into operator prose — a prefix slice is being used somewhere "
        "instead of the shared classifier (AC6.1)."
    )
    assert "Argus" in text, "cause 2 is an Argus defect and the callout must say so plainly"

    # Cause 3 — installed and broken. Reinstall/rebuild, not a fresh install.
    text = _callout({"grammar_load_failed_rust": 3})
    assert text, "cause 3 produced NO callout"
    assert "pip install tree-sitter-rust" not in text, (
        "cause 3's grammar IS installed — it is broken for this runtime. `pip install` will "
        "re-fetch the same broken wheel and change nothing."
    )
    assert "tree-sitter-rust" in text, "cause 3's callout does not name which grammar is broken"

    # Cause 4 — the CORE is down and EVERY language is affected.
    text = _callout({"tree_sitter_runtime_missing": 4})
    assert text, "cause 4 produced NO callout"
    assert "pip install tree-sitter\n" in text or "`pip install tree-sitter`" in text, (
        "cause 4's remedy must name the CORE package. Naming one language package is the "
        "maximally wrong message: every language is down, not this one."
    )
    assert "tree-sitter-go" not in text, "cause 4 named a per-language package; the core is what is broken"

    # Not a grammar failure at all — no grammar remedy.
    assert _callout({"syntax_error": 3}) == "", (
        "a syntax error was given a grammar remedy. Only grammar-LOAD failures may claim one."
    )


def test_mixed_failure_classes_each_keep_their_own_remedy() -> None:
    """TC-ArgusAgent-REPORT-002-27 — a mixed index names EACH class with ITS remedy (AC6.3).

    Never one blended sentence. A polyglot repository can hit several of these at once, and
    a merged remedy is wrong for at least one of them by construction.
    """
    text = _callout(
        {
            "grammar_missing_go": 2,
            "grammar_entrypoint_missing_php": 1,
            "grammar_load_failed_rust": 1,
        }
    )
    assert text, "a mixed-cause index produced no callout at all"
    assert "pip install tree-sitter-go" in text, "the installable cause lost its remedy in the mix"
    assert "pip install tree-sitter-go tree-sitter-php" not in text, (
        "the remedies were BLENDED into one `pip install` line. `tree-sitter-php` is already "
        "installed — its failure is an Argus entry-point defect — so this line tells the "
        "operator to do something that cannot work."
    )
    assert "pip install tree-sitter-rust" not in text, "the broken-grammar cause was blended into the install line"
    assert text.count("- ") >= 3, (
        "fewer than three per-class lines for three distinct failure classes — the classes "
        f"were merged. Rendered:\n{text}"
    )
    assert "go" in text and "php" in text and "rust" in text, "a language present in the index went unmentioned"


def test_report_classifies_through_the_shared_contract_not_a_prefix() -> None:
    """TC-ArgusAgent-REPORT-002-28 — no second prefix parse anywhere (AC6.1 / AC3.3).

    ``reason[len(prefix):]`` at the old ``generator.py:327`` is REMOVED, not widened. One
    definition, imported by both sides, is the only shape that cannot drift.
    """
    source = Path(report_generator.__file__).read_text(encoding="utf-8")
    assert "grammar_missing_" not in source, (
        "generator.py still hard-codes a grammar token prefix. It must ask "
        "argus.shared.grammar_status.classify_reason instead — a second prefix guess is how "
        "`grammar_entrypoint_missing_go` becomes the 'language' `entrypoint_missing_go`."
    )
    assert "classify_reason" in source, "generator.py does not import the shared classifier"

    index_source = Path(ast_index.__file__).read_text(encoding="utf-8")
    assert 'f"grammar_missing_{lang}"' not in index_source, (
        "ast_index.py still builds the token by f-string. The token spelling belongs to "
        "argus/shared/grammar_status.py::reason_token_for so the producer and the report "
        "cannot disagree about it."
    )
    assert "reason_token_for" in index_source, "ast_index.py does not use the shared token builder"


def test_the_all_or_nothing_trigger_is_unchanged() -> None:
    """TC-ArgusAgent-REPORT-002-29 — the partial-failure trigger is Story 12.5's, not this one (AC6.5).

    ``if eligible: return []`` means the callout fires ONLY when nothing parsed. In a
    polyglot repository whose Python parses, a failed Go grammar is still invisible. That is
    a real, measured blind spot — filed as ``DF-10-4-A`` for Story 12.5, NOT fixed here.
    Widening the trigger would add an operator surface 12.5 owns by name. This pins the
    fence in both directions so neither story can silently take the other's ground.
    """
    partial = _index_stub({"grammar_missing_go": 1})
    entries = list(partial.entries)  # type: ignore[attr-defined]
    entries[0].ast_eligible = True
    partial.entries = tuple(entries)  # type: ignore[attr-defined]

    from argus.ledger.coverage_ledger import CoverageLedger

    assert report_generator._render_readability_warning(CoverageLedger(entries=()), partial) == [], (
        "the readability callout now fires when SOME files parsed. That is Story 12.5's "
        "point-of-downgrade surface (epics.md:2328-2330), not Story 10.4's. 10.4's obligation "
        "is only that the EXISTING callout does not go silent or misdirect."
    )
    assert report_generator._render_readability_warning(CoverageLedger(entries=()), None) == []
    assert report_generator._render_readability_warning(CoverageLedger(entries=()), _index_stub({})) == []


# ─────────────────────────────────────────────────────────────────────────────
# AC3.2 — the token module is PURE
# ─────────────────────────────────────────────────────────────────────────────


def test_grammar_status_module_is_pure() -> None:
    """TC-ArgusAgent-INDEX-001-119 — the contract module imports no shell (AR8 / AC3.2).

    The dependency arrow is impure-shell → pure-contract. ``reports/`` importing the impure
    ``index/`` for a constant would invert it, which is why this module exists at all rather
    than the token set living beside the loader.
    """
    module = sys.modules["argus.shared.grammar_status"]
    source = Path(module.__file__ or "").read_text(encoding="utf-8")
    tree = ast.parse(source)

    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])

    forbidden = imported & {
        "importlib",
        "tree_sitter",
        "os",
        "sys",
        "pathlib",
        "subprocess",
        "argus",
    }
    assert not forbidden, (
        f"argus/shared/grammar_status.py imports {sorted(forbidden)}. It is a PURE contract "
        "(AR8): frozen data and pure functions, no I/O, no importlib.metadata, no tree-sitter. "
        "Anything that needs the shell belongs in argus/index/ast_index.py."
    )
    assert imported <= {"__future__", "enum", "typing"}, (
        f"unexpected import(s) {sorted(imported - {'__future__', 'enum', 'typing'})} in a pure "
        "contract module — justify them here or move the code to the shell."
    )
