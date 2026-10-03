"""wq-1211 — wq-1147's r3 false block as a regression probe, and the dunder caveat on the never-raise list.

Verification area ArgusAgent-DETECT (``-198``, ``-199``). r3 is a GREEN suite whose test calls
``ratio(1, 2)`` and discards the result; the callee divides, so it can fail on its input
(``ZeroDivisionError``) and the test is a "should not raise" test. wq-1164's builtin list never saw it
because ``/`` is an operator, not a call. The class is closed by operator shape (``/ // % ** << >> @``),
not by the name ``ratio``. Each case is paired with a near neighbour that must still block.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit_detailed  # noqa: E402
from argus.verdict.verdict_gate import is_verdict_blocking  # noqa: E402

_TEST = "from src.stats import ratio\n\n\ndef test_ratio():\n    ratio(1, 2)\n"


def _blocking(tmp_path: Path, files: dict[str, str], *, scope: str | None = None) -> list[str]:
    """Rule ids of every verdict-blocking finding over a repo built from *files*."""
    repo = tmp_path / "repo"
    for rel, text in {"src/__init__.py": "", "tests/__init__.py": "", **files}.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    kwargs = {} if scope is None else {"coverage_scope": scope}
    request = AuditRequest(repo_path=str(repo), commit="HEAD", budget=0, materiality_bar="", **kwargs)
    verdict = run_audit_detailed(request).verdict
    return sorted(f.rule_id for f in verdict.ordered_findings if is_verdict_blocking(f))


@pytest.mark.parametrize(
    "body",
    [
        "return a / b",
        "return a // b + a % b",
        "return a ** b",
        "return a << b",
        "return a >> b",
        "total = a\n    total /= b\n    return total",
        "return a @ b",
    ],
    ids=["r3-div", "floordiv-mod", "pow", "lshift", "rshift", "augassign-div", "matmul"],
)
def test_r3_operator_that_can_raise_makes_a_validating_callee(tmp_path: Path, body: str) -> None:
    """TC-ArgusAgent-DETECT-001-198 — a callee that divides (or raises to a power, or shifts) rejects
    some operand, so a test feeding it a literal and discarding the result is not an absent assertion."""
    files = {"src/stats.py": f"def ratio(a, b):\n    {body}\n", "tests/test_stats.py": _TEST}
    assert _blocking(tmp_path, files) == []


def test_r3_holds_through_a_pure_helper_of_the_same_module(tmp_path: Path) -> None:
    """The dividing helper is reached through a call to another function of the module."""
    files = {
        "src/stats.py": "def _div(a, b):\n    return a / b\n\n\ndef ratio(a, b):\n    return _div(a, b)\n",
        "tests/test_stats.py": _TEST,
    }
    assert _blocking(tmp_path, files) == []


def test_r3_neighbour_non_raising_arithmetic_still_blocks(tmp_path: Path) -> None:
    """``+ - *`` on numbers cannot reject an operand: the callee has no failure signal and still blocks."""
    files = {"src/stats.py": "def ratio(a, b):\n    return a + b * 2\n", "tests/test_stats.py": _TEST}
    assert _blocking(tmp_path, files) == ["assertion_absent"]


@pytest.mark.parametrize("scope", ["application", "repository"])
def test_r3_gives_zero_blocking_in_both_coverage_scopes(tmp_path: Path, scope: str) -> None:
    """wq-1185 measured r3 in both scopes; the regression probe pins both."""
    files = {"src/stats.py": "def ratio(a, b):\n    return a / b\n", "tests/test_stats.py": _TEST}
    assert _blocking(tmp_path, files, scope=scope) == []


# ── the dunder caveat on _NEVER_RAISE_BUILTINS ───────────────────────────────────────────────


def test_dunder_caveat_a_module_instance_with_a_raising_str_is_a_known_false_block(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-199 — ``str``/``bool``/``repr`` run the argument's own ``__str__``,
    ``__bool__`` or ``__repr__``, which can raise. A test can only hand the callee literals, so the
    value must come from outside the arguments — here a module-level instance. The callee below can
    fail, the rule reads it as unable to, and the test blocks. This pins the documented limitation
    (see the comment at ``_NEVER_RAISE_BUILTINS``): if a future change narrows the list so this stops
    blocking, update this probe and the comment together."""
    files = {
        "src/render.py": (
            "class Config:\n"
            "    def __str__(self):\n"
            "        raise ValueError('not configured')\n\n\n"
            "CONFIG = Config()\n\n\n"
            "def render():\n"
            "    return str(CONFIG)\n"
        ),
        "tests/test_render.py": "from src.render import render\n\n\ndef test_render():\n    render()\n",
    }
    assert _blocking(tmp_path, files) == ["assertion_absent"]
