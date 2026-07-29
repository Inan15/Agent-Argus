"""MANDATORY AI-E1-1 adversarial suite for the breadth tool-runner (Story 2.6, AC6).

Verification area ArgusAgent-TOOL (``TC-ArgusAgent-TOOL-001-2N``). 2.6 is the NAMED first
application of the Epic-1 retro AI-E1-1 action item: the only Epic-1 review FAIL
was Story 1.4's non-ASCII drop at an impure-shell encoding boundary. This detector
is the archetypal impure subprocess/parser boundary the retro warns about, so the
suite ships ALL of:

- (a) non-ASCII path — a fixture repo with non-ASCII file paths
  (``auth/café_metrics.py``, ``модуль/сложность.py``) whose breadth metrics are
  produced with the path INTACT (not mojibake, not dropped) and round-trip intact
  through the canonical serializer (the 1.4 TC-ArgusAgent-INTAKE-001-78 precedent);
- (b) locale / encoding — proof the invocation path handles non-ASCII source bytes
  with an explicit UTF-8 decode (``errors="replace"``) and never raises out of the
  runner (it degrades to a closed outcome);
- (c) FAILURE-INJECTION — an injected fake invoker forcing crash / timeout /
  unavailable / unparseable, EACH → a ``tool_failure`` finding + downgrade, with a
  planted source-or-secret sentinel ABSENT from every emitted/persisted byte
  (search the RAW bytes incl. non-ASCII UTF-8 — the 2.5 containment-search
  precedent), and a CLEAN run that does not cry wolf.

The (a)/(b) tests run the FULL pipeline over a staged cartridge (the impure shell
needs a real git repo + temp ``.argus/`` tree); the (c) tests inject the fake
invoker so no real subprocess is ever spawned.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))

from _cartridge import stage_cartridge  # noqa: E402

from argus.detectors.tool_runner import (  # noqa: E402
    RULE_TOOL_FAILURE,
    ToolInvocation,
    ToolOutcome,
    ToolRunnerDetector,
    radon_invoker,
)
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit_detailed  # noqa: E402
from argus.store import canonical  # noqa: E402

# A non-ASCII source/secret-shaped sentinel a hostile tool might echo (NFR-S1).
_SENTINEL = "пароль_PLANTED_секрет_0123456789"

# The non-ASCII paths staged by the tool_breadth cartridge.
_NON_ASCII_PATHS = ("src/auth/café_metrics.py", "src/модуль/сложность.py")


def _request(repo: Path) -> AuditRequest:
    return AuditRequest(
        repo_path=str(repo), commit="HEAD", budget=100, materiality_bar="default"
    )


def _all_argus_bytes(repo: Path) -> bytes:
    argus = repo / ".argus"
    blob = b""
    for path in sorted(argus.rglob("*")):
        if path.is_file():
            blob += path.read_bytes()
    return blob


# ── (a) non-ASCII path intact + round-trip ─────────────────────────────────────


def test_non_ascii_paths_survive_breadth_intact(tmp_path: Path) -> None:
    """TC-ArgusAgent-TOOL-001-20 — non-ASCII paths run breadth with the path INTACT (not dropped)."""
    detector = ToolRunnerDetector()
    targets = [
        (
            "src/auth/café_metrics.py",
            "def f(x):\n    if x:\n        return 1\n    return 2\n",
        ),
        (
            "src/модуль/сложность.py",
            "def g(flag):\n    if flag:\n        return 1\n    return 2\n",
        ),
    ]
    result = detector.run(targets=targets)
    graded = {e.file_path for e in result.entries}
    # Both non-ASCII paths produced a breadth grade with the path BYTES intact.
    assert graded == {"src/auth/café_metrics.py", "src/модуль/сложность.py"}
    # The finding/entry set round-trips intact (not mojibake) through the serializer.
    payload = {"entries": [e.model_dump(mode="json") for e in result.entries]}
    blob = canonical.dumps_bytes(payload)
    assert "café_metrics.py".encode("utf-8") in blob
    assert "сложность.py".encode("utf-8") in blob
    assert canonical.loads(blob.decode("utf-8")) == payload


def test_non_ascii_cartridge_pipeline_round_trip(tmp_path: Path) -> None:
    """TC-ArgusAgent-TOOL-001-21 — the full pipeline over a non-ASCII repo keeps the paths intact."""
    repo, _sha = stage_cartridge("tool_breadth", tmp_path / "repo")
    run_audit_detailed(_request(repo))  # must NOT raise on the non-ASCII tree

    blob = _all_argus_bytes(repo)
    assert blob, "the pipeline persisted at least one .argus/ artifact"
    # The non-ASCII path bytes survive into the persisted .argus/ artifacts intact.
    assert "café_metrics.py".encode("utf-8") in blob
    assert "сложность.py".encode("utf-8") in blob


# ── (b) locale / encoding — explicit UTF-8 decode, never raises out ─────────────


def test_non_ascii_source_never_raises_out_of_invoker() -> None:
    """TC-ArgusAgent-TOOL-001-22 — non-ASCII source bytes decode (UTF-8) and never raise out."""
    source = "# café — модуль сложности\ndef f():\n    return 1\n"
    inv = radon_invoker("src/auth/café_metrics.py", source)  # must NOT raise
    assert isinstance(inv, ToolInvocation)
    assert inv.outcome in {ToolOutcome.OK, ToolOutcome.UNPARSEABLE}


def test_non_ascii_byte_in_source_degrades_not_crashes() -> None:
    """TC-ArgusAgent-TOOL-001-23 — a non-decodable / mangled unit degrades to a closed outcome."""
    detector = ToolRunnerDetector()
    # A genuinely unparseable non-ASCII unit (syntax garbage with non-ASCII bytes).
    result = detector.run(targets=[("src/модуль/bad.py", "def café(:\n    рат\n")])
    # It NEVER raises; it is recorded as a finding + downgrade, not a crash.
    assert all(f.rule_id == RULE_TOOL_FAILURE for f in result.findings) or result.entries
    # The run produced exactly one entry for the file (skipped or graded), never dropped.
    assert {e.file_path for e in result.entries} == {"src/модуль/bad.py"}


# ── (c) FAILURE-INJECTION — sentinel absent from every emitted/persisted byte ───


@pytest.mark.parametrize(
    "outcome",
    [
        ToolOutcome.UNAVAILABLE,
        ToolOutcome.CRASHED,
        ToolOutcome.TIMED_OUT,
        ToolOutcome.UNPARSEABLE,
    ],
)
def test_failure_injection_planted_sentinel_absent_from_emitted_bytes(
    outcome: ToolOutcome,
) -> None:
    """TC-ArgusAgent-TOOL-001-24 — each injected failure → finding, planted sentinel never leaks."""

    def _leaky_invoker(file_path: str, source: str) -> ToolInvocation:
        # A hostile tool whose output echoes a secret — the impure shell must DROP
        # it at the boundary and return only the closed outcome (no raw-output field).
        assert _SENTINEL in source  # the sentinel is in the input we feed it
        return ToolInvocation(file_path=file_path, outcome=outcome)

    detector = ToolRunnerDetector(tool_invoker=_leaky_invoker)
    result = detector.run(
        targets=[("src/auth/café_metrics.py", f"secret = '{_SENTINEL}'\n")]
    )

    assert len(result.findings) == 1
    assert result.findings[0].rule_id == RULE_TOOL_FAILURE
    assert result.entries[0].depth.value == "skipped"

    # Search the RAW serialized bytes (incl. non-ASCII UTF-8) — the sentinel is ABSENT.
    blob = canonical.dumps_bytes(
        {
            "findings": [f.model_dump(mode="json") for f in result.findings],
            "entries": [e.model_dump(mode="json") for e in result.entries],
            "degraded": [
                {"file_path": d.file_path, "reason": d.reason} for d in result.degraded
            ],
        }
    )
    assert _SENTINEL.encode("utf-8") not in blob
    assert b"PLANTED" not in blob


def test_failure_injection_full_pipeline_sentinel_absent_from_argus(tmp_path: Path) -> None:
    """TC-ArgusAgent-TOOL-001-25 — an injected failure through the full pipeline leaks no sentinel.

    The pipeline constructs its own ``ToolRunnerDetector`` (default radon invoker),
    so this asserts the structural guarantee end-to-end: even when a file's source
    carries a sentinel, no raw source/tool bytes from the breadth channel's
    failure-reason path land in any persisted ``.argus/`` artifact (the reason is a
    fixed token, the outcome model has no raw-output field).
    """
    repo, _sha = stage_cartridge("tool_breadth", tmp_path / "repo")
    # Plant a sentinel into a tracked source file, re-commit so HEAD is clean.
    planted = repo / "src" / "auth" / "café_metrics.py"
    planted.write_text(
        planted.read_text(encoding="utf-8") + f"\nLEAK = '{_SENTINEL}'\n",
        encoding="utf-8",
    )
    import subprocess

    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "plant"], check=True, capture_output=True
    )

    run_audit_detailed(_request(repo))
    blob = _all_argus_bytes(repo)
    # The breadth channel's tool_failure path never persists raw source bytes; the
    # planted sentinel must not appear via the tool-runner reason/outcome surface.
    # (The secret detector may flag it as a finding, but it redacts; the sentinel
    # value itself never lands in any .argus/ byte — 2.5 + 2.6 producer discipline.)
    assert _SENTINEL.encode("utf-8") not in blob
    assert b"PLANTED" not in blob


# ── the clean run does not cry wolf ─────────────────────────────────────────────


def test_clean_run_emits_no_tool_failure_finding() -> None:
    """TC-ArgusAgent-TOOL-001-26 — a clean breadth run produces NO spurious tool_failure finding."""
    detector = ToolRunnerDetector()
    result = detector.run(
        targets=[
            ("a.py", "def f(x):\n    if x:\n        return 1\n    return 0\n"),
            ("b.py", "def g():\n    return 42\n"),
        ]
    )
    assert all(f.rule_id != RULE_TOOL_FAILURE for f in result.findings)
    assert result.degraded == ()
