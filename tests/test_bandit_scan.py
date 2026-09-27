"""Bandit findings-only SAST detector — Stage 1, wq-620.

Verification area: BanditScanDetector (`argus/detectors/bandit_scan.py`), wired per
`company/argus-finding-shape-ruling-2026-09-22.md` Part 1 Stage 1. Covers: the
detector NEVER mints a coverage entry regardless of what bandit finds (the load-
bearing invariant); a real bandit run over a real MEDIUM-severity fixture produces
exactly one advisory, non-blocking finding with the correct locator + rule_id; a
LOW-severity-only fixture produces nothing (the locked severity>=MEDIUM scope); the
empty-targets short-circuit calls bandit zero times; a raising / malformed / non-
conforming invoker degrades rather than crashing (AR10); duplicate issues collapse;
output order is deterministic regardless of input order (AR4); and the Windows
`.\\` filename-prefix bandit adds is normalized back to the POSIX path it was given.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from argus.detectors.bandit_scan import (
    BanditInvocationResult,
    BanditIssue,
    BanditOutcome,
    BanditScanDetector,
    BanditScanError,
    _normalize_bandit_filename,
)

_CLEAN_SOURCE = "def add(a, b):\n    return a + b\n"

# pickle.loads over unvalidated input -> bandit B301, MEDIUM severity, HIGH confidence.
_MEDIUM_SOURCE = "import pickle\n\n\ndef load(data):\n    return pickle.loads(data)\n"

# subprocess.run with an explicit arg list / shell=False -> bandit B603, LOW severity.
# Below the locked severity>=MEDIUM scope, so this must never surface a finding.
_LOW_ONLY_SOURCE = (
    "import subprocess\n\n\n"
    "def run(argv):\n"
    "    return subprocess.run(argv, shell=False, timeout=5)\n"
)


def _write(repo: Path, rel: str, source: str) -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")


def _issue(*, file_path="app/leaky.py", start_line=5, end_line=5, test_id="B301") -> BanditIssue:
    return BanditIssue(
        file_path=file_path, start_line=start_line, end_line=end_line, test_id=test_id
    )


# ── the load-bearing invariant: entries is ALWAYS empty ─────────────────────


def test_entries_is_always_empty_even_when_findings_are_produced(tmp_path: Path) -> None:
    """The coverage ledger cannot move because of this detector — findings-only,
    on the SecretScanDetector pattern. Proven against a REAL finding, not an empty run.
    """
    _write(tmp_path, "app/leaky.py", _MEDIUM_SOURCE)
    result = BanditScanDetector().run(repo_root=tmp_path, targets=("app/leaky.py",))
    assert result.findings, "sanity: the fixture must actually produce a finding"
    assert result.entries == ()


def test_empty_targets_short_circuits_without_calling_the_invoker(tmp_path: Path) -> None:
    calls: list[object] = []

    def _spy(repo_root: Path, file_paths):  # pragma: no cover - must never run
        calls.append(file_paths)
        raise AssertionError("invoker must not be called for empty targets")

    result = BanditScanDetector(invoker=_spy).run(repo_root=tmp_path, targets=())
    assert result.entries == () and result.findings == () and result.degraded == ()
    assert calls == []


# ── a real bandit run: MEDIUM surfaces, LOW/clean does not ──────────────────


def test_real_bandit_medium_severity_issue_surfaces_as_advisory_finding(tmp_path: Path) -> None:
    _write(tmp_path, "app/leaky.py", _MEDIUM_SOURCE)
    result = BanditScanDetector().run(repo_root=tmp_path, targets=("app/leaky.py",))

    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.rule_id == "bandit_B301"
    assert finding.advisory is True
    assert finding.depth_supported is None
    assert finding.claim_present is False
    loc = finding.locators[0]
    assert loc.file_path == "app/leaky.py"
    assert loc.start_line == 5
    assert loc.end_line == 5


def test_real_bandit_low_severity_only_is_scoped_out(tmp_path: Path) -> None:
    """The locked severity>=MEDIUM scope decision (§ ruling 5.1): a real B603 LOW
    finding must not surface, matching the CI gate's own `--severity-level medium`.
    """
    _write(tmp_path, "app/runner.py", _LOW_ONLY_SOURCE)
    result = BanditScanDetector().run(repo_root=tmp_path, targets=("app/runner.py",))
    assert result == result.__class__()


def test_real_bandit_clean_file_produces_nothing(tmp_path: Path) -> None:
    _write(tmp_path, "app/clean.py", _CLEAN_SOURCE)
    result = BanditScanDetector().run(repo_root=tmp_path, targets=("app/clean.py",))
    assert result == result.__class__()


# ── AR10: a tool failure degrades, it never crashes the pipeline ────────────


def test_unavailable_outcome_from_injected_invoker_degrades_to_empty_result(
    tmp_path: Path,
) -> None:
    def _unavailable(repo_root: Path, file_paths) -> BanditInvocationResult:
        return BanditInvocationResult(outcome=BanditOutcome.UNAVAILABLE)

    result = BanditScanDetector(invoker=_unavailable).run(
        repo_root=tmp_path, targets=("app/leaky.py",)
    )
    assert result == result.__class__()


def test_raising_invoker_is_caught_and_degrades_rather_than_propagating(
    tmp_path: Path,
) -> None:
    def _explode(repo_root: Path, file_paths) -> BanditInvocationResult:
        raise RuntimeError("bandit exploded")

    result = BanditScanDetector(invoker=_explode).run(
        repo_root=tmp_path, targets=("app/leaky.py",)
    )
    assert result == result.__class__()


def test_misbehaving_invoker_returning_the_wrong_type_degrades(tmp_path: Path) -> None:
    def _wrong_type(repo_root: Path, file_paths):
        return "not a BanditInvocationResult"

    result = BanditScanDetector(invoker=_wrong_type).run(  # type: ignore[arg-type]
        repo_root=tmp_path, targets=("app/leaky.py",)
    )
    assert result == result.__class__()


# ── AR10: malformed arguments raise a typed error, never a tool failure ─────


def test_non_path_repo_root_raises_typed_error() -> None:
    with pytest.raises(BanditScanError):
        BanditScanDetector().run(repo_root="not-a-path", targets=())  # type: ignore[arg-type]


def test_non_sequence_targets_raises_typed_error(tmp_path: Path) -> None:
    with pytest.raises(BanditScanError):
        BanditScanDetector().run(repo_root=tmp_path, targets="app/leaky.py")  # type: ignore[arg-type]


def test_empty_string_target_raises_typed_error(tmp_path: Path) -> None:
    with pytest.raises(BanditScanError):
        BanditScanDetector().run(repo_root=tmp_path, targets=("",))


# ── pure-core behaviour: dedup + deterministic order (injected invoker) ─────


def test_duplicate_issues_collapse_to_one_finding(tmp_path: Path) -> None:
    duplicate = (_issue(), _issue())

    def _invoker(repo_root: Path, file_paths) -> BanditInvocationResult:
        return BanditInvocationResult(outcome=BanditOutcome.OK, issues=duplicate)

    result = BanditScanDetector(invoker=_invoker).run(
        repo_root=tmp_path, targets=("app/leaky.py",)
    )
    assert len(result.findings) == 1


def test_finding_order_is_deterministic_regardless_of_invoker_order(tmp_path: Path) -> None:
    issues = (
        _issue(file_path="app/z.py", start_line=1, end_line=1, test_id="B101"),
        _issue(file_path="app/a.py", start_line=9, end_line=9, test_id="B999"),
        _issue(file_path="app/a.py", start_line=2, end_line=2, test_id="B301"),
    )

    def _invoker(repo_root: Path, file_paths) -> BanditInvocationResult:
        return BanditInvocationResult(outcome=BanditOutcome.OK, issues=issues)

    result = BanditScanDetector(invoker=_invoker).run(
        repo_root=tmp_path, targets=("app/a.py", "app/z.py")
    )
    file_lines = [(f.locators[0].file_path, f.locators[0].start_line) for f in result.findings]
    assert file_lines == sorted(file_lines)


# ── the impure shell's Windows filename-prefix normalization ────────────────


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("app/leaky.py", "app/leaky.py"),
        ("./app/leaky.py", "app/leaky.py"),
        (".\\app\\leaky.py", "app/leaky.py"),
        (".\\app/leaky.py", "app/leaky.py"),
    ],
)
def test_normalize_bandit_filename(raw: str, expected: str) -> None:
    assert _normalize_bandit_filename(raw) == expected
