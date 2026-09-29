"""wq-1134 — the four false blocks wq-1128 found on green suites, as regression probes q1-q4.

Verification area ArgusAgent-DETECT (``-191``..``-194``). They sit beside wq-1091's six probes
(p1-p6, in ``test_structural_blocking.py`` and ``test_ineffective_assertion.py``): each is a
GREEN suite that development never blocked, so a block here is a precision loss on the number
the pre-registration scores. Every probe runs ``run_audit_detailed`` end to end and expects NO
blocking finding; each is paired with its near neighbour, which must still block, so the fix is
shown to be the rule's shape and not a blanket silence.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit_detailed  # noqa: E402
from argus.verdict.verdict_gate import is_verdict_blocking  # noqa: E402


def _blocking(tmp_path: Path, files: dict[str, str]) -> list[str]:
    """Rule ids of every verdict-blocking finding over a repo built from *files*."""
    repo = tmp_path / "repo"
    for rel, text in {"src/__init__.py": "", "tests/__init__.py": "", **files}.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    request = AuditRequest(repo_path=str(repo), commit="HEAD", budget=0, materiality_bar="")
    verdict = run_audit_detailed(request).verdict
    return sorted(f.rule_id for f in verdict.ordered_findings if is_verdict_blocking(f))


_STATS = "def mean(xs):\n    return sum(xs) / len(xs)\n"
_PRICES = 'PRICES = {"apple": 3}\n\n\ndef price_of(name):\n    return PRICES[name]\n'
_CODES = "def code_of(ch):\n    return ord(ch)\n"


def test_q1_not_nan_idiom_is_not_a_tautology(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-191 — ``m = mean(xs); assert m == m`` fails on NaN, so it can fail."""
    files = {
        "src/stats.py": _STATS,
        "tests/test_stats.py": (
            "from src.stats import mean\n\n\ndef test_mean_is_not_nan():\n"
            "    m = mean([1.0, 2.0])\n    assert m == m\n"
        ),
    }
    assert _blocking(tmp_path, files) == []


def test_q1_neighbour_reflexive_on_a_literal_binding_still_blocks(tmp_path: Path) -> None:
    """A name bound to a literal, not a call, is not a computed value: still a tautology."""
    files = {"tests/test_stats.py": "def test_x():\n    y = 5\n    assert y == y\n"}
    assert _blocking(tmp_path, files) == ["tautological_assertion"]


def test_q2_fake_class_method_is_not_collected(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-192 — a ``test*`` method of a class that is neither ``Test*`` nor a
    ``TestCase`` subclass is never run, so it cannot pass green and is not accused."""
    files = {
        "src/net.py": "def ping():\n    return 1\n",
        "tests/test_net.py": (
            "from src.net import ping\n\n\nclass FakeDriver:\n    def test_connection(self):\n        pass\n\n\n"
            "def test_ping():\n    assert ping() == 1\n"
        ),
    }
    assert _blocking(tmp_path, files) == []


@pytest.mark.parametrize(
    "header",
    ["class TestDriver:", "class DriverChecks(unittest.TestCase):", "class Derived(TestBase):"],
    ids=["Test-prefixed", "TestCase-subclass", "same-file-collected-base"],
)
def test_q2_neighbour_collected_class_with_pass_still_blocks(tmp_path: Path, header: str) -> None:
    """The exit is the collection rule, not "any method of any class": a collected class still blocks."""
    files = {
        "tests/test_net.py": (
            "import unittest\n\n\nclass TestBase:\n    def test_a(self):\n        assert 2 > 1\n\n\n"
            f"{header}\n    def test_connection(self):\n        pass\n"
        ),
    }
    assert "vacuous_test_cannot_fail" in _blocking(tmp_path, files)


@pytest.mark.parametrize(
    ("module", "name", "call"),
    [(_PRICES, "prices", 'price_of("apple")'), (_CODES, "codes", 'code_of("a")')],
    ids=["q3-dict-subscript", "q4-ord"],
)
def test_q3_q4_validating_callee_is_a_should_not_raise_test(
    tmp_path: Path, module: str, name: str, call: str
) -> None:
    """TC-ArgusAgent-DETECT-001-193/-194 — a callee that can raise on its input (a dict read, ``ord``)
    is validated by a test that feeds it a literal and discards the result."""
    fn = call.split("(")[0]
    files = {
        f"src/{name}.py": module,
        f"tests/test_{name}.py": f"from src.{name} import {fn}\n\n\ndef test_{fn}():\n    {call}\n",
    }
    assert _blocking(tmp_path, files) == []


def test_q3_q4_neighbour_pure_callee_still_blocks(tmp_path: Path) -> None:
    """A callee with no failure signal but its return value (``lower``/``split``/``join``) still blocks."""
    files = {
        "src/slug.py": "def slugify(t):\n    return '-'.join(t.lower().split())\n",
        "tests/test_slug.py": "from src.slug import slugify\n\n\ndef test_slugify():\n    slugify('A B')\n",
    }
    assert _blocking(tmp_path, files) == ["assertion_absent"]
