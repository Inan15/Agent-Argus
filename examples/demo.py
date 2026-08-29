#!/usr/bin/env python3
"""Agent-Argus in 90 seconds — a test that passes and proves nothing.

    python examples/demo.py

WHAT THIS SHOWS, in one arc:

  1. A repository whose test suite is GREEN. `pytest` says `1 passed`.
  2. `argus audit .` says NOT_READY_FOR_RELEASE and exits 2, naming one
     verdict-blocking finding.
  3. The test is fixed to assert the real result instead of a mock's.
  4. `argus audit .` says RELEASE_READY and exits 0.

The planted defect is the one this tool exists for: a test that *reaches* the
code under test, then asserts a value it made up itself. It passes on every CI
in the world. It tests nothing.

HERMETIC AND HONEST. Everything below is built from bytes in this file — no
network, no fixture downloaded, no corpus member read, nothing cached. Every
figure this script prints comes from a real run performed while you watch; there
are no recorded or expected outputs baked in, deliberately, because a demo with
hardcoded output is a screenshot that can rot without anyone noticing.

Exit code: 0 if the demo behaved as described, 1 if it did not — so this file is
also a (small) end-to-end check of the claim the README makes on its front page.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ── The demo repository, as bytes ────────────────────────────────────────────

SUT = '''\
def subtotal(items):
    total = 0
    for price, qty in items:
        total = total + price * qty
    return total


def apply_discount(total, rate):
    return total - (total * rate)
'''

# The defect. It calls subtotal(...) — so a "does the test touch the SUT?" check
# passes — and then asserts a Mock's own configured return value. Green forever.
VACUOUS_TEST = '''\
from unittest.mock import Mock

from src.cart import subtotal


def test_subtotal():
    subtotal([(10, 2), (5, 1)])
    fake = Mock()
    fake.compute.return_value = 25
    pretended = fake.compute()
    assert pretended == 25
'''

# The fix: assert the value the SUT actually returned.
HONEST_TEST = '''\
from src.cart import subtotal


def test_subtotal():
    result = subtotal([(10, 2), (5, 1)])
    assert result == 25
'''

BOLD, DIM, RESET = "\033[1m", "\033[2m", "\033[0m"


def say(text: str = "") -> None:
    print(text, flush=True)


def run(argv: list[str], cwd: Path) -> tuple[int, str]:
    done = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True)
    return done.returncode, (done.stdout + done.stderr)


def summary_line(output: str) -> str:
    for line in output.splitlines():
        if line.startswith("verdict="):
            return line
    return "(no summary line — the run did not reach a verdict)"


def build(root: Path, test_source: str) -> None:
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / "src" / "cart.py").write_text(SUT, encoding="utf-8")
    (root / "tests" / "test_cart.py").write_text(test_source, encoding="utf-8")
    shutil.rmtree(root / ".argus", ignore_errors=True)
    if not (root / ".git").exists():
        run(["git", "init", "-q", "."], root)
        run(["git", "config", "user.email", "demo@agent-argus.invalid"], root)
        run(["git", "config", "user.name", "Agent-Argus demo"], root)
    run(["git", "add", "-A"], root)
    run(["git", "commit", "-qm", "demo"], root)


def main() -> int:
    if shutil.which("git") is None:
        say("This demo needs `git` on PATH."); return 1

    ok = True
    with tempfile.TemporaryDirectory(prefix="agent-argus-demo-") as tmp:
        repo = Path(tmp) / "shopping-cart"

        say(f"\n{BOLD}1. A small repository. Its test suite is green.{RESET}")
        build(repo, VACUOUS_TEST)
        say(f"{DIM}   $ cat tests/test_cart.py{RESET}")
        for line in VACUOUS_TEST.rstrip().splitlines():
            say(f"     {line}")

        say(f"\n{DIM}   $ pytest tests/ -q{RESET}")
        code, out = run([sys.executable, "-m", "pytest", "tests/", "-q"], repo)
        say(f"     {out.strip().splitlines()[-1] if out.strip() else '(no output)'}")
        say(f"     exit {code}")
        if code != 0:
            say("     ! expected the suite to PASS — the point is that it does")
            ok = False

        say(f"\n{BOLD}2. Now ask Argus.{RESET}")
        say(f"{DIM}   $ argus audit .{RESET}")
        code, out = run([sys.executable, "-m", "argus.cli", "audit", "."], repo)
        for line in out.splitlines():
            if line.startswith("Ship-readiness:") or line.strip().startswith("- Verdict-blocking"):
                say(f"     {line.strip()}")
        say(f"     {summary_line(out)}")
        say(f"     exit {code}")
        if code != 2:
            say("     ! expected exit 2 (NOT_READY_FOR_RELEASE)")
            ok = False

        say(f"\n{DIM}   The test called subtotal(...) and then asserted a value it")
        say(f"   invented. It reaches the code and proves nothing about it.{RESET}")

        say(f"\n{BOLD}3. Fix the test — assert what the code actually returned.{RESET}")
        build(repo, HONEST_TEST)
        for line in HONEST_TEST.rstrip().splitlines():
            say(f"     {line}")

        say(f"\n{DIM}   $ argus audit .{RESET}")
        code, out = run([sys.executable, "-m", "argus.cli", "audit", "."], repo)
        say(f"     {summary_line(out)}")
        say(f"     exit {code}")
        if code != 0:
            say("     ! expected exit 0 (RELEASE_READY)")
            ok = False

    say()
    if ok:
        say(f"{BOLD}Green suite, blocked release, then a real fix that clears it.{RESET}")
        say("No API key. No network. No LLM tokens. Same commit, same answer,")
        say("on any machine.")
        say()
        say(f"{DIM}What Argus does NOT claim: its finding precision has not been{RESET}")
        say(f"{DIM}independently validated, and a verdict is never an attestation{RESET}")
        say(f"{DIM}that code is correct. See the instrument status in README.md.{RESET}")
        return 0
    say(f"{BOLD}The demo did NOT behave as described above.{RESET}")
    say("That is a real failure worth an issue: https://github.com/Inan15/Agent-Argus/issues")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
