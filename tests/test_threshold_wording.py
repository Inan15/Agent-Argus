"""wq-1211 — the coverage-threshold sentence quotes the gate constant, not a second copy of it.

Verification area ArgusAgent-DOCS (``-62``). ``plain_english`` printed "below the 80% threshold (3/5)"
while the gate (``RELEASE_READY_DEEP_THRESHOLD``) is ``Fraction(3, 5)`` — 60%. The sentence contradicted
its own parenthesis on a real run (7 of the 24 harness cases; wq-1168 row 15). The percentage is now
derived from the constant, so moving the constant moves the sentence.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

from argus.verdict.verdict_gate import RELEASE_READY_DEEP_THRESHOLD  # noqa: E402

_CART = "def subtotal(items):\n    total = 0\n    for price, qty in items:\n        total = total + price * qty\n    return total\n"
_TEST = "from src.cart import subtotal\n\n\ndef test_subtotal():\n    assert subtotal([(10, 2), (5, 1)]) == 25\n"


def test_threshold_sentence_quotes_the_gate_constant(tmp_path: Path) -> None:
    """TC-ArgusAgent-DOCS-001-62 — an application-scope run below the gate names the gate's own percentage."""
    for rel, text in {"src/__init__.py": "", "src/cart.py": _CART, "tests/test_cart.py": _TEST}.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for argv in (["init", "-q", "."], ["add", "-A"]):
        subprocess.run(["git", *argv], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=t@t.invalid", "-c", "user.name=t", "commit", "-qm", "seed"],
        cwd=tmp_path, check=True, capture_output=True,
    )
    done = subprocess.run(
        [sys.executable, "-m", "argus.cli", "audit", ".", "--coverage-scope", "application"],
        cwd=tmp_path, capture_output=True, text=True, check=False,
    )
    out = done.stdout + done.stderr
    expected = f"below the {float(RELEASE_READY_DEEP_THRESHOLD):.0%} threshold ({RELEASE_READY_DEEP_THRESHOLD})"
    assert expected in out, out
    assert "below the 60% threshold (3/5)" in out, out
    assert "80% threshold" not in out, out
