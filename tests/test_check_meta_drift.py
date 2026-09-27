"""Story 21.1 / AC3 — the §CD-2 advisory reader never HALTs and never blocks.

Verification area for ``scripts/check_meta_drift.py``: no test file existed for this module
before this story (checked: no ``test_*meta_drift*`` under ``tests/`` at this story's baseline
commit). The module's own docstring states the contract this file asserts: *"this script always
exits 0 on a clean parse. A non-zero exit means the script could not READ its inputs — never that
a finding was made."*

**The regression this file exists to pin (AC3's second half).** Epic 21's own seed commit
(``fd56de3``) records a real break: seeding ``epics.md`` with a ``**Capability delivered:**``
value beginning ``⛔`` (U+26D4) crashed ``report_epics``'s ``print(f"      capability: {cap[:64]}")``
on a default Windows console — ``UnicodeEncodeError`` in ``cp1252``, exit 1 — while
``PYTHONIOENCODING=utf-8`` exited 0. That is a FALSE "cannot read its inputs" signal, exactly the
false-failure class the module's own ADVISORY disposition exists to avoid (its docstring cites
``TC-ArgusAgent-DOCS-001-78`` going RED three times from prose in one day as the scar this
design choice answers). The commit worked around it by moving the ⛔ later in the sentence and
named the durable fix as belonging in the script ("encode defensively"), routed to this story.
This file both proves the durable fix (``_console_safe``) holds and proves the live advisory
read against the real, current ``epics.md`` exits 0.

Two tests, not one, because they attack the failure mode two different ways:

* ``test_advisory_path_exits_zero_on_a_clean_parse_of_the_real_repo`` is the literal AC3
  assertion — a real subprocess, the real ``epics.md``, and (this is the point) the **default**
  environment: ``PYTHONUTF8`` / ``PYTHONIOENCODING`` are explicitly stripped from the child
  process so the test cannot pass merely because the *harness's* environment happens to force
  UTF-8. If the console encoding heuristic ever changes on this machine such that stdout is
  already UTF-8 by default, this test would stop being able to reproduce the regression's
  precondition — ``test_default_stdout_encoding_is_the_regression_precondition`` pins that
  precondition explicitly so a silent environment change cannot make this file quietly stop
  proving anything.
* ``test_console_safe_survives_a_leading_non_cp1252_glyph`` reproduces the *exact* original crash
  shape (a non-encodable character at the START of the capability text, inside the ``cap[:64]``
  window) directly against ``report_epics``, with ``sys.stdout`` replaced by a strict ``cp1252``
  writer — the precise codec the seed commit named. It does not depend on the machine's actual
  console encoding at all, so it keeps proving the fix even on a machine where the first test's
  precondition no longer reproduces naturally.
"""

from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import check_meta_drift as cmd  # noqa: E402


def _run_advisory(env_overrides: dict[str, str] | None = None) -> subprocess.CompletedProcess[bytes]:
    """Run the real script as a subprocess against the real, committed ``epics.md``."""
    import os

    env = dict(os.environ)
    # Strip every encoding override this workspace's own tooling sets (windows-environment.md
    # requires PYTHONUTF8=1 for every uv run) — the regression's precondition IS their absence.
    for key in ("PYTHONUTF8", "PYTHONIOENCODING", "PYTHONLEGACYWINDOWSSTDIO"):
        env.pop(key, None)
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        [sys.executable, str(_REPO_ROOT / "scripts" / "check_meta_drift.py")],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        env=env,
        timeout=60,
    )


@pytest.mark.skipif(sys.platform != "win32", reason="the regression is a Windows console-codepage default")
def test_default_stdout_encoding_is_the_regression_precondition() -> None:
    """Pin the precondition: a bare child process on this platform defaults to a non-UTF-8
    stdout encoding. If this ever stops being true, the crash this file guards against can no
    longer occur by default and the next test's negative form (proving no crash) would be
    proving less than it claims — so that fact is asserted here, not assumed.
    """
    import os

    env = dict(os.environ)
    for key in ("PYTHONUTF8", "PYTHONIOENCODING", "PYTHONLEGACYWINDOWSSTDIO"):
        env.pop(key, None)
    probe = subprocess.run(
        [sys.executable, "-c", "import sys; print(sys.stdout.encoding)"],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    encoding = probe.stdout.strip().lower()
    assert encoding not in ("utf-8", "utf8"), (
        f"a bare child Python process on this machine now defaults to stdout encoding "
        f"{encoding!r}, not a legacy code page. The §CD-2 regression this file pins can no "
        "longer be reproduced by omitting PYTHONUTF8/PYTHONIOENCODING alone; "
        "test_advisory_path_exits_zero_on_a_clean_parse_of_the_real_repo would pass without "
        "ever having exercised the crash path. Re-derive a real reproduction (e.g. force the "
        "legacy code page explicitly) before trusting that test again."
    )


def test_advisory_path_exits_zero_on_a_clean_parse_of_the_real_repo() -> None:
    """AC3, literally: the advisory read exits 0 on a clean parse — asserted against the real,
    current ``epics.md``, in an environment that reproduces the regression's precondition
    (no PYTHONUTF8/PYTHONIOENCODING override) rather than one that happens to avoid it.
    """
    result = _run_advisory()
    assert result.returncode == 0, (
        f"scripts/check_meta_drift.py exited {result.returncode} on a clean parse of the real "
        f"epics.md with no PYTHONUTF8/PYTHONIOENCODING override — the module's own docstring "
        "says a non-zero exit here means it could not read its inputs, never that a finding was "
        "made, and it always found epics.md readable in this run. "
        f"stderr:\n{result.stderr.decode('utf-8', 'replace')}"
    )
    # A crash surfaces as a Python traceback on stderr; a clean parse never does, whatever the
    # findings say (findings print with `!!` on stdout and are not failures — see the module
    # docstring). This distinguishes "exited 0 and reported nothing wrong" (which this assertion
    # does NOT require) from "exited 0 having actually read and printed the report".
    stdout = result.stdout.decode("utf-8", "replace")
    assert "Traceback" not in result.stderr.decode("utf-8", "replace")
    assert "ADVISORY meta-work drift report" in stdout


def test_advisory_path_exits_zero_via_json_mode_too() -> None:
    """The ``--json`` path shares ``classify``/``guard_evidence``/``duplication`` with the text
    path but not ``report_epics`` (the function the regression actually broke) — asserted
    separately so a future change to ``main`` cannot silently narrow AC3 to only the text mode.
    """
    result_json = subprocess.run(
        [sys.executable, str(_REPO_ROOT / "scripts" / "check_meta_drift.py"), "--json"],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        timeout=60,
    )
    assert result_json.returncode == 0, (
        f"--json mode exited {result_json.returncode}; stderr: "
        f"{result_json.stderr.decode('utf-8', 'replace')}"
    )


def test_console_safe_survives_a_leading_non_cp1252_glyph() -> None:
    """Reproduces the exact original crash shape directly: a ``**Capability delivered:**`` value
    that BEGINS with ``⛔`` (U+26D4, the character the seed commit named), well inside the
    ``cap[:64]`` window ``report_epics`` prints — against a ``sys.stdout`` stand-in that is a
    real, strict ``cp1252`` encoder, the exact codec the seed commit's traceback named. Before
    ``_console_safe`` existed, this raised ``UnicodeEncodeError`` here directly (reproduced by
    hand while writing this test); after it, ``report_epics`` must complete without raising.
    """
    row = {
        "epic": 999,
        "title": "synthetic regression fixture",
        "pre_rule": False,
        "stories": 1,
        "product": 0,
        "process": 1,
        "process_ids": ["999.1"],
        "covers_names_driver": True,
        "covers_present": True,
        # The exact original shape: a non-cp1252-encodable glyph at the very START of the
        # capability text, so it falls inside cap[:64] rather than past it.
        "capability": "⛔ leading glyph the original crash used, cp1252 cannot encode it",
    }

    strict_cp1252 = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")
    old_stdout = sys.stdout
    sys.stdout = strict_cp1252
    try:
        cmd.report_epics([row])  # must not raise UnicodeEncodeError
    finally:
        sys.stdout = old_stdout
        strict_cp1252.close()


def test_console_safe_neutralises_relative_to_the_live_stdout_encoding() -> None:
    """``_console_safe`` reads ``sys.stdout.encoding`` at call time (so it degrades relative to
    whatever the *real* target encoding is, not a hardcoded one) — asserted directly by pointing
    ``sys.stdout`` at a strict ``cp1252`` writer, matching the seed commit's traceback, and
    proving the returned string is then safe against exactly that encoder.
    """
    unsafe = "⛔ unencodable-in-cp1252"
    with pytest.raises(UnicodeEncodeError):
        unsafe.encode("cp1252")  # sanity: the raw string really is the regression's shape

    old_stdout = sys.stdout
    sys.stdout = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")
    try:
        safe = cmd._console_safe(unsafe)
        safe.encode("cp1252")  # raises if _console_safe did not actually neutralise it
    finally:
        sys.stdout.close()
        sys.stdout = old_stdout


def test_console_safe_is_actually_wired_into_the_capability_print() -> None:
    """A narrower, direct check that the fix is not merely present in the module but actually
    sits between ``cap[:64]`` and the ``print`` call in ``report_epics`` — so a future refactor
    that reintroduces a bare ``print(f"...{cap[:64]}")`` (bypassing ``_console_safe``) is caught
    even if it happens not to trip the end-to-end fixture above. Reads the source rather than
    re-running the whole function, since the end-to-end test already proves behaviour; this
    proves the *wiring* specifically.
    """
    source = (_REPO_ROOT / "scripts" / "check_meta_drift.py").read_text(encoding="utf-8")
    assert "_console_safe(cap[:64])" in source, (
        "report_epics no longer routes cap[:64] through _console_safe before printing it — the "
        "§CD-2 encoding regression (Epic 21 seed commit fd56de3) could recur even though the "
        "helper function still exists and is tested in isolation above."
    )
