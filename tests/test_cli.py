"""Story 1.7 — the thin ``argparse`` CLI invocation contract (AC3).

Verification area ArgusAgent-CLI (TC-ArgusAgent-CLI-001-NN). Exercises ``cli.main(argv=[...])``
returning the right exit code WITHOUT a real ``sys.exit``: the signature-demo
cartridge → exit 2, the clean control → exit 0, a bad repo → exit 1 with a
secret-safe stderr line + NO traceback to the user, and the LOCKED flag contract
(``--commit`` required, ``--budget`` int-typed).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

try:
    import tree_sitter
    import tree_sitter_python
    HAS_TREE_SITTER = True
except ImportError:
    HAS_TREE_SITTER = False

sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))

from _cartridge import stage_cartridge  # noqa: E402

from argus import cli  # noqa: E402


def test_cli_signature_demo_returns_exit_2(tmp_path: Path, capsys) -> None:
    """TC-ArgusAgent-CLI-001-01 — main() on cartridge #1 returns 2 + prints a verdict summary."""
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")
    code = cli.main(["audit", str(repo), "--commit", "HEAD", "--budget", "100", "--materiality-bar", "default"])
    assert code == 2

    out = capsys.readouterr().out
    assert "verdict=NOT_READY_FOR_RELEASE" in out
    assert "blocking_findings=" in out
    # NFR-S1: no source bytes / absolute repo path leak into stdout.
    assert "compute_total" not in out
    assert str(repo) not in out


def test_cli_clean_control_returns_exit_0(tmp_path: Path, capsys) -> None:
    """TC-ArgusAgent-CLI-001-02 — main() on the clean control returns 0."""
    repo, _sha = stage_cartridge("clean_control", tmp_path / "repo")
    code = cli.main(["audit", str(repo), "--commit", "HEAD"])
    assert code == 0
    assert "verdict=RELEASE_READY" in capsys.readouterr().out


def test_cli_bad_repo_returns_exit_1_no_traceback(tmp_path: Path, capsys) -> None:
    """TC-ArgusAgent-CLI-001-03 — AC6: a bad repo → exit 1 + secret-safe stderr, no traceback."""
    code = cli.main(["audit", str(tmp_path / "nope"), "--commit", "HEAD"])
    assert code == 1
    captured = capsys.readouterr()
    assert "audit failed" in captured.err
    assert "Traceback" not in captured.err
    assert "Traceback" not in captured.out


def test_cli_commit_is_required(tmp_path: Path) -> None:
    """TC-ArgusAgent-CLI-001-04 — AC3: --commit is REQUIRED (no silent HEAD default)."""
    with pytest.raises(SystemExit) as exc:
        cli.main(["audit", str(tmp_path)])
    assert exc.value.code != 0  # argparse exits 2 on a missing required arg


def test_cli_budget_rejects_float(tmp_path: Path) -> None:
    """TC-ArgusAgent-CLI-001-05 — AC1/AR4: --budget is int-typed (a float spelling is rejected)."""
    with pytest.raises(SystemExit):
        cli.main(["audit", str(tmp_path), "--commit", "HEAD", "--budget", "1.5"])


def test_cli_unknown_subcommand_rejected() -> None:
    """TC-ArgusAgent-CLI-001-06 — AC3: an unknown sub-command is rejected (sub-command required)."""
    with pytest.raises(SystemExit):
        cli.main(["bogus"])


def test_cli_designation_flags_are_repeatable_and_populate_request() -> None:
    """TC-ArgusAgent-CLI-001-07 — story 2.3: --critical-subsystem / --exclude-critical are repeatable."""
    from argus.models import AuditRequest

    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "audit",
            "repo",
            "--commit",
            "HEAD",
            "--critical-subsystem",
            "src/a.py",
            "--critical-subsystem",
            "src/b.py",
            "--exclude-critical",
            "src/c.py",
        ]
    )
    request = AuditRequest(
        repo_path=args.repo,
        commit=args.commit,
        budget=args.budget,
        materiality_bar=args.materiality_bar,
        critical_paths=tuple(args.critical_subsystem or ()),
        excluded_critical_paths=tuple(args.exclude_critical or ()),
    )
    assert request.critical_paths == ("src/a.py", "src/b.py")
    assert request.excluded_critical_paths == ("src/c.py",)


def test_cli_without_designation_flags_is_byte_identical() -> None:
    """TC-ArgusAgent-CLI-001-08 — story 2.3: absent flags → empty tuples (byte-identical to pre-2.3)."""
    from argus.models import AuditRequest

    parser = cli.build_parser()
    args = parser.parse_args(["audit", "repo", "--commit", "HEAD"])
    assert args.critical_subsystem is None
    assert args.exclude_critical is None
    request = AuditRequest(
        repo_path=args.repo,
        commit=args.commit,
        budget=args.budget,
        materiality_bar=args.materiality_bar,
        critical_paths=tuple(args.critical_subsystem or ()),
        excluded_critical_paths=tuple(args.exclude_critical or ()),
    )
    assert request.critical_paths == ()
    assert request.excluded_critical_paths == ()
