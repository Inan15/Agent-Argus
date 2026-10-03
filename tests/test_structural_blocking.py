"""wq-1083 — the two structural facts that make a seeded-defect-class finding BLOCK.

Verification areas ArgusAgent-DETECT (``-153``..) for ``vacuous_test_cannot_fail`` and
ArgusAgent-ORPHAN (``-18``..) for the blocking ``orphan_code`` subset. Drivers:
``argus/detectors/structural_blocking.py`` (both predicates and the measurements behind
their exits), ``evaluation/seeded-defect-harness/`` (the shapes ``a4``/``a6``/``c1``/``c2``/
``c3`` are planted verbatim below), cross-cutting #6 (every exit keeps a finding exactly as
advisory as it was — each exit has its own case here, because an exit nothing pins is an
exit the next change can delete silently). wq-1101 added the exits wq-1091's six probes
showed were missing (``-185``/``-186``, ``ORPHAN-001-26``..``-28``).

Every case stands up the REAL Story-1.4 index via ``build_ast_index`` and runs the real
detector, so a case measures what the pipeline would emit, not a reconstruction of it.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

from argus.detectors.orphan_code import RULE_ORPHAN_CODE, OrphanCodeDetector  # noqa: E402
from argus.detectors.structural_blocking import RULE_CANNOT_FAIL  # noqa: E402
from argus.detectors.vacuous_test import RULE_HEURISTIC, VacuousTestDetector  # noqa: E402
from argus.index.ast_index import AstIndex, build_ast_index  # noqa: E402
from argus.ledger.coverage_ledger import CoverageDepth  # noqa: E402
from argus.ledger.recording import Recording  # noqa: E402
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit_detailed  # noqa: E402
from argus.verdict.verdict_gate import is_verdict_blocking  # noqa: E402

_SUT = """def subtotal(items):
    total = 0
    for price, qty in items:
        total = total + price * qty
    return total
"""


def _write(root: Path, files: dict[str, str]) -> AstIndex:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    python_files = tuple(sorted(rel for rel in files if rel.endswith(".py")))
    return build_ast_index(root, python_files)


def _vacuous(tmp_path: Path, test_source: str) -> Recording:
    """The ONE finding the vacuous detector emits for *test_source* (it must be flagged)."""
    rel = "tests/test_cart.py"
    index = _write(tmp_path, {rel: test_source})
    entry = {e.file_path: e for e in index.entries}[rel]
    result = VacuousTestDetector().run(file_path=rel, source=test_source, ast_entry=entry)
    assert len(result.findings) == 1, (
        f"the fixture must be heuristically flagged exactly once; got {result.findings!r} — "
        "a case whose premise does not hold measures nothing"
    )
    return result.findings[0]


def _orphans(
    tmp_path: Path, files: dict[str, str], *, with_sources: bool = True
) -> dict[str, Recording]:
    """Every orphan finding, keyed by the flagged def's name (from its ``ast_span``)."""
    index = _write(tmp_path, files)
    sources = dict(files) if with_sources else None
    result = OrphanCodeDetector().run(index=index, sources=sources)
    return {
        f.locators[0].ast_span.split(":", 1)[1].split("@", 1)[0]: f  # type: ignore[union-attr]
        for f in result.findings
    }


def _assert_blocks(finding: Recording, rule_id: str, depth: CoverageDepth) -> None:
    assert finding.rule_id == rule_id
    assert finding.depth_supported is depth
    assert is_verdict_blocking(finding)


def _assert_advisory(finding: Recording, rule_id: str) -> None:
    assert finding.rule_id == rule_id
    assert finding.depth_supported is None
    assert not is_verdict_blocking(finding)


# ── vacuous_test_cannot_fail: the shapes that block ────────────────────────────


def test_pass_body_cannot_fail_and_blocks(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-153 — seeded ``a6``: a body of ``pass`` blocks."""
    finding = _vacuous(tmp_path, "def test_subtotal():\n    pass\n")
    _assert_blocks(finding, RULE_CANNOT_FAIL, CoverageDepth.AUDITED_SHALLOW)


def test_swallowed_sut_call_cannot_fail_and_blocks(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-154 — seeded ``a4``: the call's every exception is swallowed."""
    source = (
        "from src.cart import subtotal\n\n\n"
        "def test_subtotal():\n"
        "    try:\n"
        "        subtotal([(10, 2), (5, 1)])\n"
        "    except Exception:\n"
        "        pass\n"
    )
    _assert_blocks(_vacuous(tmp_path, source), RULE_CANNOT_FAIL, CoverageDepth.AUDITED_SHALLOW)


def test_docstring_then_ellipsis_cannot_fail_and_blocks(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-155 — a placeholder test (docstring + ``...``) blocks."""
    source = 'def test_later():\n    """Skipped: not implemented yet."""\n    ...\n'
    _assert_blocks(_vacuous(tmp_path, source), RULE_CANNOT_FAIL, CoverageDepth.AUDITED_SHALLOW)


# ── vacuous_test_cannot_fail: every exit stays advisory ────────────────────────


def test_discarded_call_without_assertion_stays_advisory(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-156 — seeded ``a1`` IS a "does not raise" test by shape.

    The measured reason the rule is "cannot fail" and not "asserts nothing": on Minions the
    wider rule blocked 9 legitimate tests of exactly this shape. It stays heuristic.
    """
    source = "from src.cart import subtotal\n\n\ndef test_subtotal():\n    subtotal([(10, 2), (5, 1)])\n"
    _assert_advisory(_vacuous(tmp_path, source), RULE_HEURISTIC)


def test_import_smoke_test_stays_advisory(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-157 — an import IS the check; an ImportError fails the test."""
    source = "def test_smoke_imports():\n    from src.cart import subtotal  # noqa: F401\n"
    _assert_advisory(_vacuous(tmp_path, source), RULE_HEURISTIC)


def test_decorated_pass_body_stays_advisory(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-158 — a decorator (here a skip marker) is an exit."""
    source = "import pytest\n\n\n@pytest.mark.skip(reason='later')\ndef test_later():\n    pass\n"
    _assert_advisory(_vacuous(tmp_path, source), RULE_HEURISTIC)


@pytest.mark.parametrize(
    "handler",
    ["except ValueError:\n        pass\n", "except Exception as exc:\n        print(exc)\n"],
    ids=["narrow-except", "handler-does-something"],
)
def test_try_that_can_still_fail_stays_advisory(tmp_path: Path, handler: str) -> None:
    """TC-ArgusAgent-DETECT-001-159 — a narrow ``except`` or a handler that acts is an exit."""
    source = (
        "from src.cart import subtotal\n\n\n"
        "def test_subtotal():\n"
        "    try:\n"
        "        subtotal([(10, 2), (5, 1)])\n"
        f"    {handler}"
    )
    _assert_advisory(_vacuous(tmp_path, source), RULE_HEURISTIC)


@pytest.mark.parametrize(
    "source",
    [
        "import pytest\n\n\n@pytest.mark.skip(reason='later')\n# TODO: re-enable\ndef test_later():\n    pass\n",
        "import pytest\n\n\n@pytest.mark.skip(reason='later')\nclass TestLater:\n    def test_later(self):\n        pass\n",
        "import pytest\n\npytestmark = pytest.mark.skip(reason='later')\n\n\ndef test_later():\n    pass\n",
        "import pytest\n\n\nclass TestLater:\n    pytestmark = pytest.mark.skip(reason='later')\n\n"
        "    def test_later(self):\n        pass\n",
        "import pytest\n\npytest.skip('later', allow_module_level=True)\n\n\ndef test_later():\n    pass\n",
    ],
    ids=["comment-between-decorator", "class-decorator", "module-pytestmark", "class-pytestmark", "module-skip"],
)
def test_skip_marker_outside_the_def_stays_advisory(tmp_path: Path, source: str) -> None:
    """TC-ArgusAgent-DETECT-001-185 — wq-1091 probes p1-p3: pytest reports these SKIPPED.

    A skip can reach a test from a comment-separated decorator, an enclosing class, or a
    ``pytestmark``/module-level skip; a test pytest does not run is not a test that passes.
    """
    _assert_advisory(_vacuous(tmp_path, source), RULE_HEURISTIC)


def test_pass_body_in_undecorated_class_still_blocks(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-186 — the class walk is an exit only when a class carries a marker.

    Minions' two real blocks (``tests/test_remaining_engines.py:566``/``:570``) are this
    shape: a ``unittest.TestCase`` method whose body is ``pass``, which runs and passes.
    """
    source = "import unittest\n\n\nclass TestLater(unittest.TestCase):\n    def test_later(self):\n        pass\n"
    _assert_blocks(_vacuous(tmp_path, source), RULE_CANNOT_FAIL, CoverageDepth.AUDITED_SHALLOW)


# ── orphan_code: the shapes that block ─────────────────────────────────────────

_CART_TEST = "from src.cart import subtotal\n\n\ndef test_subtotal():\n    assert subtotal([(10, 2)]) == 20\n"


def test_unmentioned_def_in_imported_module_blocks(tmp_path: Path) -> None:
    """TC-ArgusAgent-ORPHAN-001-18 — seeded ``c1``: a live module carrying a def nothing mentions."""
    files = {
        "src/cart.py": _SUT + "\n\ndef orphan_module_level(x):\n    return x * 3\n",
        "tests/test_cart.py": _CART_TEST,
    }
    found = _orphans(tmp_path, files)
    _assert_blocks(found["orphan_module_level"], RULE_ORPHAN_CODE, CoverageDepth.TOOL_SCANNED_ONLY)


def test_imported_but_never_called_blocks(tmp_path: Path) -> None:
    """TC-ArgusAgent-ORPHAN-001-19 — seeded ``c3``: an ``import`` line is not a reference."""
    files = {
        "src/cart.py": _SUT + "\n\ndef orphan_behind_import(x):\n    return x * 5\n",
        "tests/test_cart.py": _CART_TEST.replace("import subtotal", "import subtotal, orphan_behind_import"),
    }
    found = _orphans(tmp_path, files)
    _assert_blocks(found["orphan_behind_import"], RULE_ORPHAN_CODE, CoverageDepth.TOOL_SCANNED_ONLY)


def test_uninstantiated_class_blocks_but_its_method_does_not(tmp_path: Path) -> None:
    """TC-ArgusAgent-ORPHAN-001-20 — seeded ``c2``: the class blocks; the METHOD stays advisory.

    The class's own docstring names it — a mention inside its own span is not a reference
    from anywhere else. A method is reachable by override or protocol dispatch the name
    graph cannot see, so it is never promoted.
    """
    files = {
        "src/cart.py": _SUT
        + '\n\nclass PricingHelper:\n    """Nothing ever instantiates PricingHelper."""\n\n'
        "    def orphan_method(self, x):\n        return x * 4\n",
        "tests/test_cart.py": _CART_TEST,
    }
    found = _orphans(tmp_path, files)
    _assert_blocks(found["PricingHelper"], RULE_ORPHAN_CODE, CoverageDepth.TOOL_SCANNED_ONLY)
    _assert_advisory(found["orphan_method"], RULE_ORPHAN_CODE)


# ── orphan_code: every exit stays advisory ─────────────────────────────────────


@pytest.mark.parametrize(
    "importer",
    [{}, {"src/app.py": "from src.config import api_client\n\n\ndef run():\n    return api_client()\n"}],
    ids=["nothing-imports-it", "only-production-imports-it"],
)
def test_module_no_test_imports_stays_advisory(tmp_path: Path, importer: dict[str, str]) -> None:
    """TC-ArgusAgent-ORPHAN-001-21 — a module no TEST imports: no in-repo caller is normal.

    Measured reasons for this exit. Nothing-imports-it: four of this repository's own
    ``max_blocking=0`` cartridges went red on exactly that shape. Only-production-imports-it:
    the dogfood's ``argus/``-only snapshot blocked ``CostAttributionEngine``, whose only
    caller is a test the snapshot does not carry.
    """
    files = {
        "src/config.py": "def aws_client():\n    return 'x'\n\n\ndef api_client():\n    return 'y'\n",
        "tests/test_other.py": "def test_x():\n    assert 1\n",
        **importer,
    }
    _assert_advisory(_orphans(tmp_path, files)["aws_client"], RULE_ORPHAN_CODE)


@pytest.mark.parametrize(
    "extra",
    [
        {"src/__init__.py": "from src.cart import orphan_fn\n"},
        {"src/api.py": "import src.cart\n\n__all__ = ['orphan_fn']\n"},
        {"docs_ref.py": "import src.cart\n\n# see orphan_fn for the legacy path\n"},
        {"pyproject.toml": '[project.scripts]\ntool = "src.cart:orphan_fn"\n'},
    ],
    ids=["package-reexport", "all-string", "comment-mention", "console-script"],
)
def test_any_mention_or_reexport_stays_advisory(tmp_path: Path, extra: dict[str, str]) -> None:
    """TC-ArgusAgent-ORPHAN-001-22 — a re-export, a string, a comment or an entry point exits."""
    files = {
        "src/cart.py": _SUT + "\n\ndef orphan_fn(x):\n    return x\n",
        "tests/test_cart.py": _CART_TEST,
        **extra,
    }
    _assert_advisory(_orphans(tmp_path, files)["orphan_fn"], RULE_ORPHAN_CODE)


def test_non_init_reexport_stays_advisory(tmp_path: Path) -> None:
    """TC-ArgusAgent-ORPHAN-001-26 — wq-1091 probe p5: a re-export from ``api.py`` is public API.

    Only a TEST file's import of a name nothing calls stays blocking (seeded ``c3``).
    """
    files = {
        "src/cart.py": _SUT + "\n\ndef orphan_fn(x):\n    return x\n",
        "src/api.py": "from src.cart import subtotal, orphan_fn  # re-exported\n",
        "tests/test_cart.py": _CART_TEST,
    }
    _assert_advisory(_orphans(tmp_path, files)["orphan_fn"], RULE_ORPHAN_CODE)


@pytest.mark.parametrize(
    "dispatch",
    [
        {"src/cart.py": _SUT + '\n\ndef handle_add(x):\n    return x + 1\n\n\n'
         'def dispatch(kind, x):\n    return globals()["handle_" + kind](x)\n'},
        {"src/cart.py": _SUT + "\n\ndef handle_add(x):\n    return x + 1\n",
         "src/router.py": 'from src import cart\n\n\ndef dispatch(kind, x):\n    return getattr(cart, "handle_" + kind)(x)\n'},
    ],
    ids=["own-globals", "getattr-on-module"],
)
def test_computed_name_lookup_stays_advisory(tmp_path: Path, dispatch: dict[str, str]) -> None:
    """TC-ArgusAgent-ORPHAN-001-27 — wq-1091 probe p4: a def reached by a computed name."""
    files = {**dispatch, "tests/test_cart.py": _CART_TEST}
    _assert_advisory(_orphans(tmp_path, files)["handle_add"], RULE_ORPHAN_CODE)


def test_pipeline_reads_config_text_as_references(tmp_path: Path) -> None:
    """TC-ArgusAgent-ORPHAN-001-28 — wq-1091 probe p6: a handler named only in YAML stays advisory.

    Through ``run_audit_detailed``, so the pipeline's config walk is what is measured: the
    same repository without the YAML file still blocks the handler.
    """
    def _repo(root: Path, with_yaml: bool) -> Path:
        files = {
            "src/__init__.py": "",
            "src/cart.py": _SUT + "\n\ndef on_created(event):\n    return event\n",
            "tests/__init__.py": "",
            "tests/test_cart.py": _CART_TEST,
        }
        if with_yaml:
            files["config/hooks.yaml"] = "created: src.cart.on_created\n"
        for rel, text in files.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return root

    def _blocking(repo: Path) -> list[str]:
        request = AuditRequest(repo_path=str(repo), commit="HEAD", budget=0, materiality_bar="")
        verdict = run_audit_detailed(request).verdict
        return [f.rule_id for f in verdict.ordered_findings if is_verdict_blocking(f)]

    assert _blocking(_repo(tmp_path / "without", with_yaml=False)) == [RULE_ORPHAN_CODE]
    assert _blocking(_repo(tmp_path / "with", with_yaml=True)) == []


def test_decorated_or_test_file_def_stays_advisory(tmp_path: Path) -> None:
    """TC-ArgusAgent-ORPHAN-001-23 — a decorator (registration) and a test-file helper exit."""
    files = {
        "src/cart.py": _SUT + "\n\n@register\ndef on_event(x):\n    return x\n",
        "tests/test_cart.py": _CART_TEST + "\n\ndef make_items():\n    return []\n",
        "src/registry.py": "import src.cart\n\n\ndef register(fn):\n    return fn\n",
    }
    found = _orphans(tmp_path, files)
    _assert_advisory(found["on_event"], RULE_ORPHAN_CODE)
    _assert_advisory(found["make_items"], RULE_ORPHAN_CODE)


def test_without_sources_every_orphan_stays_advisory(tmp_path: Path) -> None:
    """TC-ArgusAgent-ORPHAN-001-24 — no reference universe, no promotion (the pre-wq-1083 path)."""
    files = {
        "src/cart.py": _SUT + "\n\ndef orphan_module_level(x):\n    return x * 3\n",
        "tests/test_cart.py": _CART_TEST,
    }
    found = _orphans(tmp_path, files, with_sources=False)
    _assert_advisory(found["orphan_module_level"], RULE_ORPHAN_CODE)


# ── end to end: the pipeline wires the universe, the clean control stays clean ──


def test_pipeline_blocks_seeded_orphan_and_spares_clean_control(tmp_path: Path) -> None:
    """TC-ArgusAgent-ORPHAN-001-25 — through ``run_audit_detailed``: ``c1`` blocks, ``e4`` does not."""
    seeded = tmp_path / "seeded"
    _write(seeded, {
        "src/__init__.py": "",
        "src/cart.py": _SUT + "\n\ndef orphan_module_level(x):\n    return x * 3\n",
        "tests/__init__.py": "",
        "tests/test_cart.py": _CART_TEST,
    })
    control = tmp_path / "control"
    _write(control, {
        "src/__init__.py": "",
        "src/cart.py": _SUT + '\n\ndef price_summary(items):\n    return f"total: {subtotal(items)}"\n',
        "tests/__init__.py": "",
        "tests/test_cart.py": _CART_TEST.replace("import subtotal", "import subtotal, price_summary")
        + '\n\ndef test_price_summary():\n    assert price_summary([(10, 2)]) == "total: 20"\n',
    })

    def _blocking(repo: Path) -> list[Recording]:
        request = AuditRequest(repo_path=str(repo), commit="HEAD", budget=0, materiality_bar="")
        verdict = run_audit_detailed(request).verdict
        return [f for f in verdict.ordered_findings if is_verdict_blocking(f)]

    seeded_blocking = _blocking(seeded)
    assert [(f.rule_id, f.locators[0].file_path) for f in seeded_blocking] == [
        (RULE_ORPHAN_CODE, "src/cart.py")
    ]
    assert _blocking(control) == []
