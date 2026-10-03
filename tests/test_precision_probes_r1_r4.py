"""wq-1164 — the three false blocks wq-1147 found on green suites, as regression probes r1, r2 and r4.

Verification area ArgusAgent-DETECT (``-195``..``-197``). They extend wq-1134's q1-q4
(``test_precision_probes_q1_q4.py``): each is a GREEN suite that development never blocked. Every
probe runs ``run_audit_detailed`` end to end and expects NO blocking finding; each is paired with
its near neighbour, which must still block, so the fix is the rule's shape and not a blanket silence.
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


@pytest.mark.parametrize(
    "body",
    [
        "return dict(p.split('=') for p in text.split(';'))",
        "return list(map(int, text.split(',')))",
        "return sum(text.split(','))",
        "return len(text)",
        "return sorted(text.split(','))",
    ],
    ids=["r1-dict", "list-map-int", "sum", "len", "sorted"],
)
def test_r1_builtin_that_can_raise_makes_a_validating_callee(tmp_path: Path, body: str) -> None:
    """TC-ArgusAgent-DETECT-001-195 — ``dict``/``list``/``sum``/``len``/``sorted`` reject some inputs,
    so a callee built on one is validated by a test that feeds it a literal and discards the result."""
    files = {
        "src/conv.py": f"def conv(text):\n    {body}\n",
        "tests/test_conv.py": "from src.conv import conv\n\n\ndef test_conv():\n    conv('a=1;b=2')\n",
    }
    assert _blocking(tmp_path, files) == []


def test_r1_neighbour_never_raise_builtins_still_block(tmp_path: Path) -> None:
    """A callee whose only builtins cannot raise (``str``/``repr``/``bool``) has no failure signal."""
    files = {
        "src/label.py": "def label(v):\n    return repr(str(bool(v)))\n",
        "tests/test_label.py": "from src.label import label\n\n\ndef test_label():\n    label(1)\n",
    }
    assert _blocking(tmp_path, files) == ["assertion_absent"]


def test_r2_not_nan_idiom_on_a_fixture_value_is_not_a_tautology(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-196 — ``def test(m): assert m == m`` on a fixture value fails on NaN."""
    files = {
        "tests/conftest.py": "import pytest\n\n\n@pytest.fixture\ndef m():\n    return 1.0\n",
        "tests/test_fixture.py": "def test_m_is_not_nan(m):\n    assert m == m\n",
    }
    assert _blocking(tmp_path, files) == []


def test_r2_neighbour_reflexive_on_a_literal_still_blocks(tmp_path: Path) -> None:
    """A literal comparison in a parameter-free test is still a tautology."""
    files = {"tests/test_lit.py": "def test_x():\n    assert 5 == 5\n"}
    assert _blocking(tmp_path, files) == ["tautological_assertion"]


def test_r4_test_prefixed_fake_with_init_is_not_collected(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-197 — pytest skips a ``Test*`` class that defines ``__init__``."""
    files = {
        "src/net.py": "def ping():\n    return 1\n",
        "tests/test_net.py": (
            "from src.net import ping\n\n\nclass TestDriver:\n    def __init__(self):\n        self.up = True\n\n"
            "    def test_connection(self):\n        pass\n\n\ndef test_ping():\n    assert ping() == 1\n"
        ),
    }
    assert _blocking(tmp_path, files) == []


def test_r4_neighbour_testcase_with_init_is_still_collected(tmp_path: Path) -> None:
    """unittest collects a ``TestCase`` subclass whatever its constructor: still blocks."""
    files = {
        "tests/test_net.py": (
            "import unittest\n\n\nclass TestDriver(unittest.TestCase):\n    def __init__(self, *a):\n"
            "        super().__init__(*a)\n\n    def test_connection(self):\n        pass\n"
        ),
    }
    assert "vacuous_test_cannot_fail" in _blocking(tmp_path, files)
