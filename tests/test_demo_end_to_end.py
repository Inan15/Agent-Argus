"""wq-1211 — the README's front-page demo, run end to end, with its exit codes asserted.

Verification area ArgusAgent-DOCS (``-60``). The README says ``python examples/demo.py`` blocks a green
suite (``exit 2``) and then clears it after a real fix (``exit 0``). On the wq-1164 branch that stopped
being true — the demo's unused ``apply_discount`` became a blocking ``orphan_code`` finding, the "fixed"
run still exited 2, and the demo reported its own failure with exit 1 — and NO test noticed, because
nothing ran the demo (wq-1168). This is that test.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

if shutil.which("git") is None:  # the demo builds a git repository; without git it exits 1 by design
    pytest.skip("examples/demo.py needs git on PATH", allow_module_level=True)

_DEMO = Path(__file__).resolve().parent.parent / "examples" / "demo.py"


@pytest.fixture(scope="module")
def demo() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(_DEMO)], capture_output=True, text=True, timeout=900, check=False
    )


def test_demo_exits_zero_when_it_behaves_as_described(demo: subprocess.CompletedProcess[str]) -> None:
    """TC-ArgusAgent-DOCS-001-60 — exit 0 is the demo's claim that every step went as narrated."""
    assert demo.returncode == 0, demo.stdout + demo.stderr
    assert "The demo did NOT behave as described above" not in demo.stdout


def test_demo_narrates_exit_2_then_exit_0_from_argus(demo: subprocess.CompletedProcess[str]) -> None:
    """TC-ArgusAgent-DOCS-001-61 — the blocked run exits 2 on one finding; the fixed run exits 0."""
    lines = [line.strip() for line in demo.stdout.splitlines()]
    verdicts = [line for line in lines if line.startswith("verdict=")]
    exits = [line for line in lines if line.startswith("exit ")]
    assert len(verdicts) == 2, demo.stdout
    assert verdicts[0].startswith("verdict=NOT_READY_FOR_RELEASE") and "blocking_findings=1 " in verdicts[0]
    assert verdicts[1].startswith("verdict=RELEASE_READY") and "blocking_findings=0 " in verdicts[1]
    # pytest's own exit (0), then argus's blocked run (2), then argus's fixed run (0).
    assert exits == ["exit 0", "exit 2", "exit 0"], demo.stdout
