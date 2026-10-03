"""wq-1084 — family B: a test whose every assertion is true by construction BLOCKS.

Verification area ArgusAgent-DETECT (``-160``..``-169``). Drivers:
``argus/detectors/tautological_assertion.py`` (the fact and its exits),
``evaluation/seeded-defect-harness/`` (the harness shapes ``a3``/``b1``..``b5`` are planted
verbatim in ``-160``), cross-cutting #6 (every exit has its own silent case — an exit nothing
pins is an exit the next change can delete silently).

The SYNTHETIC cases (``-161``..``-165``) are deliberately NOT harness shapes: other names, other
domains, other spellings of the same fact. They are what shows the rule fires on the shape and
not on the harness's text.

Every case stands up the REAL Story-1.4 index via ``build_ast_index`` and runs the real detector.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

from argus.detectors.tautological_assertion import (  # noqa: E402
    RULE_TAUTOLOGICAL_ASSERTION,
    TautologicalAssertionDetector,
)
from argus.index.ast_index import build_ast_index  # noqa: E402
from argus.ledger.coverage_ledger import CoverageDepth  # noqa: E402
from argus.verdict.verdict_gate import is_verdict_blocking  # noqa: E402


def _flagged(tmp_path: Path, test_source: str, *, rel: str = "tests/test_subject.py") -> list[str]:
    """The names of the tests the detector blocks in *test_source* (asserting each blocks)."""
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(test_source, encoding="utf-8")
    entry = build_ast_index(tmp_path, (rel,)).entries[0]
    result = TautologicalAssertionDetector().run(file_path=rel, source=test_source, ast_entry=entry)
    names = []
    for finding in result.findings:
        assert finding.rule_id == RULE_TAUTOLOGICAL_ASSERTION
        assert finding.depth_supported is CoverageDepth.AUDITED_SHALLOW
        assert is_verdict_blocking(finding)
        assert result.entries == (), "family B emits findings only; the vacuous pass grades the file"
        names.append(finding.locators[0].ast_span.split(":", 1)[1].split("@", 1)[0])  # type: ignore[union-attr]
    return names


_HARNESS_SHAPES = {
    "a3": 'from src.cart import subtotal\n\n\ndef test_subtotal():\n    subtotal([(10, 2), (5, 1)])\n    assert "ok"\n',
    "b1": "from src.cart import subtotal\n\n\ndef test_subtotal():\n    subtotal([(10, 2), (5, 1)])\n    assert True\n",
    "b2": "from src.cart import subtotal\n\n\ndef test_subtotal():\n    subtotal([(10, 2), (5, 1)])\n    assert 1 == 1\n",
    "b4": "from src.cart import subtotal\n\n\ndef test_subtotal():\n    subtotal([(10, 2), (5, 1)])\n    assert isinstance(5, int)\n",
    "b5": "from src.cart import subtotal\n\n\ndef test_subtotal():\n    subtotal([(10, 2), (5, 1)])\n    expected = 25\n    assert expected == 25\n",
}


# wq-1134: harness case b3 (`x = subtotal(...); assert x == x`) is deliberately NOT here. A reflexive
# assert on a name bound from a call is the not-NaN idiom (wq-1128 probe q1), so the rule stands down;
# the measured cost is one of the 20 seeded cases (18 -> 17 of 20).


def test_reflexive_assert_on_call_bound_name_is_the_not_nan_idiom(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-195 — harness ``b3`` shape: computed value, ``assert x == x`` can fail on NaN."""
    source = "from src.cart import subtotal\n\n\ndef test_subtotal():\n    x = subtotal([(10, 2)])\n    assert x == x\n"
    assert _flagged(tmp_path, source) == []


@pytest.mark.parametrize("case", sorted(_HARNESS_SHAPES))
def test_harness_shapes_block(tmp_path: Path, case: str) -> None:
    """TC-ArgusAgent-DETECT-001-160 — the six harness shapes of the fact, verbatim, each block."""
    assert _flagged(tmp_path, _HARNESS_SHAPES[case]) == ["test_subtotal"]


# ── synthetic: fires (not harness text) ─────────────────────────────────────────────────────


def test_synthetic_tuple_assert_blocks(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-161 — ``assert (cond, "msg")`` is a non-empty tuple: always true."""
    source = (
        "from billing.invoice import render\n\n\n"
        "def test_render_has_header():\n"
        "    page = render({'id': 7})\n"
        '    assert (page.startswith("INVOICE"), "header missing")\n'
    )
    assert _flagged(tmp_path, source) == ["test_render_has_header"]


def test_synthetic_literal_forms_block(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-162 — other spellings: ``or True``, ``not None``, a bound tuple, ``in``."""
    source = (
        "import billing\n\n\n"
        "def test_or_true():\n"
        "    assert billing.total([1, 2]) == 3 or True\n\n\n"
        "def test_not_none():\n"
        "    billing.flush()\n"
        "    assert not None\n\n\n"
        "def test_bound_tuple():\n"
        "    billing.flush()\n"
        "    limits: tuple = (1, 2)\n"
        "    assert limits == (1, 2)\n\n\n"
        "class TestMembership:\n"
        "    def test_in(self):\n"
        "        billing.flush()\n"
        '        assert "a" in "abc"\n'
        "        assert isinstance([1], (list, tuple))\n"
    )
    assert _flagged(tmp_path, source) == ["test_or_true", "test_not_none", "test_bound_tuple", "test_in"]


# ── synthetic: correctly silent ─────────────────────────────────────────────────────────────


def test_synthetic_real_assertions_stay_silent(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-163 — assertions that read the code under test are not tautologies."""
    source = (
        "from billing.invoice import render, total\n\n\n"
        "def test_render_has_header():\n"
        "    page = render({'id': 7})\n"
        '    assert page.startswith("INVOICE"), "header missing"\n\n\n'
        "def test_total():\n"
        "    expected = 25\n"
        "    assert total([(10, 2), (5, 1)]) == expected\n\n\n"
        "def test_placeholder_beside_real_assertion():\n"
        "    assert True\n"
        "    assert total([]) == 0\n\n\n"
        "def test_rebound_name_is_not_a_constant():\n"
        "    expected = 25\n"
        "    expected = total([(10, 2), (5, 1)])\n"
        "    assert expected == 25\n\n\n"
        "def test_mutable_literal_is_not_substituted():\n"
        "    items = []\n"
        "    total(items)\n"
        "    assert items == []\n\n\n"
        "def test_call_twice_is_not_reflexive():\n"
        "    assert total([1]) == total([1])\n"
    )
    assert _flagged(tmp_path, source) == []


def test_contradiction_and_other_assertion_forms_stay_silent(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-164 — ``assert 1 == 2`` fails red (not a false green); other
    assertion sites, a ``raise`` and a same-file helper are each an exit."""
    source = (
        "import pytest\n"
        "from billing import total\n\n\n"
        "def _check_total(v):\n"
        "    assert v == 3\n\n\n"
        "def test_always_fails():\n"
        "    assert 1 == 2\n\n\n"
        "def test_raises_too():\n"
        "    assert True\n"
        "    with pytest.raises(ValueError):\n"
        "        total(None)\n\n\n"
        "def test_raise_statement():\n"
        "    assert True\n"
        "    if total([1]) != 1:\n"
        "        raise AssertionError('bad')\n\n\n"
        "def test_delegates():\n"
        "    helper_result = total([1, 2])\n"
        "    assert True\n"
        "    _check_total(helper_result)\n"
    )
    assert _flagged(tmp_path, source) == []


def test_equality_contract_and_fixture_data_stay_silent(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-165 — ``obj == obj`` in an ``__eq__`` test, and a module no runner
    collects (Minions ``tests/**/fixtures/**/dispatch_check.py`` at ``dcd90233``)."""
    eq_source = (
        "from money import Money\n\n\n"
        "def test_eq_is_reflexive():\n"
        "    m = Money(5)\n"
        "    assert m == m\n"
    )
    assert _flagged(tmp_path, eq_source) == []
    fixture = "def test_dispatch_under_load():\n    assert True\n"
    assert _flagged(tmp_path, fixture, rel="tests/fixtures/load/dispatch_check.py") == []
    assert _flagged(tmp_path, fixture, rel="tests/load/test_dispatch.py") == ["test_dispatch_under_load"]


def test_unparseable_and_non_test_files_stay_silent(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-166 — a file ``ast`` cannot parse, and a production module."""
    assert _flagged(tmp_path, "def test_x(:\n    assert True\n") == []
    assert _flagged(tmp_path, "def test_x():\n    assert True\n", rel="src/helpers.py") == []


@pytest.mark.parametrize(
    "source",
    [
        "import pytest\n\n\n@pytest.mark.skip(reason='later')\ndef test_later():\n    assert True\n",
        "import pytest\n\n\n@pytest.mark.skip(reason='later')\nclass TestLater:\n    def test_later(self):\n"
        "        assert True\n",
        "import pytest\n\npytestmark = pytest.mark.skip(reason='later')\n\n\ndef test_later():\n    assert True\n",
        "import unittest\n\nraise unittest.SkipTest('later')\n\n\ndef test_later():\n    assert True\n",
    ],
    ids=["own-skip", "class-skip", "module-pytestmark", "module-skiptest"],
)
def test_runner_may_skip_stays_silent(tmp_path: Path, source: str) -> None:
    """TC-ArgusAgent-DETECT-001-167 — a skipped ``assert True`` placeholder never passes green
    (wq-1127, the family-A exit of wq-1091 probes p2/p3 applied to family B); the same test
    in an undecorated class still blocks."""
    assert _flagged(tmp_path, source) == []
    plain = "class TestLater:\n    def test_later(self):\n        assert True\n"
    assert _flagged(tmp_path, plain) == ["test_later"]
