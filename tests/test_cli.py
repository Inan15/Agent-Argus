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


def test_cli_summary_line_does_not_carry_the_decision_row(tmp_path: Path, capsys) -> None:
    """TC-ArgusAgent-CLI-001-30 — Story 8.1 / AC10: the stdout machine line is UNCHANGED.

    The FR16 decision row surfaces on the verdict ARTIFACT and (Story 8.3) in prose on
    the human stderr register — deliberately NOT as a new field on the stdout machine
    summary, which is a frozen wire surface that CI scripts parse. Its shape stays
    exactly ``verdict=<TOKEN> deep_ratio=<num/den> blocking_findings=<n>``.
    """
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")
    cli.main(["audit", str(repo), "--commit", "HEAD", "--budget", "100"])

    summary = [
        line for line in capsys.readouterr().out.splitlines() if line.startswith("verdict=")
    ]
    assert len(summary) == 1, "exactly one machine summary line"
    # The frozen shape, including the scope suffix the default run narrows with.
    assert summary[0] == (
        "verdict=NOT_READY_FOR_RELEASE deep_ratio=1/2 blocking_findings=1 "
        "assessed_deep_ratio=1 scope=application held_out=1"
    )
    assert "decision_row" not in summary[0]
    assert "row_" not in summary[0]


def test_cli_summary_line_is_unchanged_for_a_non_blocking_verdict(
    tmp_path: Path, capsys
) -> None:
    """TC-ArgusAgent-CLI-001-31 — Story 8.3 / AC9: the wire surface survives a reword.

    ``-30`` pins the line for a row-2 (blocking) run. Story 8.3 rewrites the HUMAN
    register for the two ``INSUFFICIENT_COVERAGE`` rows, so the golden that matters is
    the one for a NON-row-2 verdict: this is where a story rewriting prose could most
    easily leak a character onto the machine surface CI scripts parse.

    Also pins the register SPLIT that keeps the two from competing for one stream:
    stdout carries exactly one line and it starts with ``verdict=``; the reworded
    human block goes to stderr, in full, and never to stdout.
    """
    repo, _sha = stage_cartridge("orphan_basic", tmp_path / "repo")
    code = cli.main(
        [
            "audit",
            str(repo),
            "--commit",
            "HEAD",
            "--budget",
            "100",
            "--coverage-scope",
            "repository",
        ]
    )
    assert code == 3

    captured = capsys.readouterr()
    stdout_lines = captured.out.splitlines()

    assert len(stdout_lines) == 1, "stdout is the wire contract: exactly one line"
    assert stdout_lines[0] == (
        "verdict=INSUFFICIENT_COVERAGE deep_ratio=1/2 blocking_findings=0"
    )
    assert "decision_row" not in stdout_lines[0]
    assert "row_" not in stdout_lines[0]
    # No prose crosses over — not the headline, not a fragment of it.
    assert "NOT VOUCHED" not in captured.out
    assert "Ship-readiness" not in captured.out

    # …and the human register really did reach the operator, on stderr.
    assert captured.err.startswith("Ship-readiness: NOT VOUCHED")
    assert "coverage or critical-subsystem gate was not met" in captured.err
    assert "too little of the code was examined" not in captured.err


def test_cli_degrades_to_exit_1_on_an_impossible_verdict(tmp_path: Path, capsys, monkeypatch) -> None:
    """TC-ArgusAgent-CLI-001-32 — Story 8.3 / AC2: the typed refusal degrades honestly.

    ``plain_english.ShipReadinessError`` is raised when a verdict the FR16 gate cannot
    produce reaches the human renderer. Asserted, not assumed: it must reach the
    operator as the AR10 typed failure — exit ``1``, one secret-safe stderr line, no
    traceback — rather than as a rendered falsehood or an uncaught crash.
    """
    from argus.reports.plain_english import ShipReadinessError

    def _boom(_request):
        raise ShipReadinessError("NOT_READY_FOR_RELEASE with blocking_finding_count=0")

    monkeypatch.setattr(cli, "run_audit", _boom)
    code = cli.main(["audit", str(tmp_path), "--commit", "HEAD"])

    assert code == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "audit failed" in captured.err
    assert "blocking_finding_count=0" in captured.err
    assert "Traceback" not in captured.err


def test_cli_degrades_when_the_real_renderer_raises_on_the_way_out(
    tmp_path: Path, capsys, monkeypatch
) -> None:
    """TC-ArgusAgent-CLI-001-33 — Story 8.4 / AC11 (DF-8-3-B): the REAL site is guarded.

    ``-32`` above monkeypatches ``run_audit`` to RAISE, so its exception originates
    INSIDE the ``try`` and the test passes no matter where ``render_ship_readiness`` is
    called. That proves the AC's letter and nothing about the site that actually
    escapes: ``main()`` renders the human register AFTER the ``try`` closes, on the
    default no-``--report-dir`` path (with ``--report-dir`` set, the pipeline renders
    the same block inside ``run_audit`` and the guard there masks the gap).

    So here the stand-in is removed from the raise: ``run_audit`` RETURNS a verdict —
    the one FR16 cannot produce — and the REAL ``render_ship_readiness`` raises the
    REAL ``ShipReadinessError`` at the real call site. Constructing that verdict by
    hand is legitimate for exactly this pin: ``evaluate_verdict`` cannot emit it (that
    is the invariant Story 8.1 established), so it is the only way to reach the site.

    The AR10 / NFR-R1 contract the release note publishes: a typed failure degrades to
    exit ``1`` with a secret-safe stderr line — never an uncaught traceback.
    """
    from fractions import Fraction

    from argus.verdict.verdict_gate import AuditVerdict, Verdict

    impossible = AuditVerdict(
        verdict=Verdict.NOT_READY_FOR_RELEASE,
        deep_ratio=Fraction(9, 10),
        deep_count=9,
        total_count=10,
        counts_by_depth={"audited_deep": 9, "audited_shallow": 1},
        blocking_finding_count=0,  # the contradiction: row 2 requires >= 1
        ordered_findings=(),
        exit_code=2,
    )
    monkeypatch.setattr(cli, "run_audit", lambda _request: impossible)

    # NO --report-dir: this is the default invocation and the unguarded path.
    code = cli.main(["audit", str(tmp_path), "--commit", "HEAD"])

    assert code == 1, "a typed failure must degrade to exit 1, not escape main()"

    captured = capsys.readouterr()
    # The typed reason reached the operator, naming only the contract it broke.
    assert "audit failed" in captured.err
    assert "blocking_finding_count=0" in captured.err
    assert "NOT_READY_FOR_RELEASE" in captured.err
    # Secret-safe (NFR-S1 / AR10): no traceback, no host path, no source bytes.
    assert "Traceback" not in captured.err
    assert "ShipReadinessError" not in captured.err
    assert str(tmp_path) not in captured.err
    assert "plain_english.py" not in captured.err
    # The human register never rendered, so no half-written falsehood reached stderr.
    assert "Ship-readiness" not in captured.err
    assert "BLOCKED" not in captured.err
    # Recorded as observed, not adjusted: the wire line is written before the render is
    # attempted, so it is already on stdout when the failure lands. Widening the guard
    # (rather than reordering the two writes) is what keeps every non-raising run
    # byte-identical, and this is its one visible consequence.
    assert captured.out == "verdict=NOT_READY_FOR_RELEASE deep_ratio=9/10 blocking_findings=0\n"


def test_cli_a_console_that_cannot_encode_the_prose_does_not_fail_the_audit(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-CLI-001-34 — a SUCCESSFUL audit is never reported as a failure.

    Code-review iteration 2, finding D1. Every ship-readiness headline carries an em
    dash, and ``UnicodeEncodeError`` is a ``ValueError`` — so a single guard spanning
    both the audit and the human register let a console code page decide the exit code.
    Reproduced on a ``cp437`` stderr (Windows cmd at cp437/cp850, ``PYTHONIOENCODING=
    ascii``, POSIX ``LC_ALL=C``): a clean repository that genuinely audits
    ``RELEASE_READY`` returned ``1`` with ``argus: audit failed`` — while stdout already
    carried ``verdict=RELEASE_READY``. That is a false statement about a run that
    succeeded, and it contradicts the contract ``CHANGELOG.md`` publishes in the same
    commit (exit ``1`` means a typed failure degraded the run BEFORE a verdict existed).

    Two independent guarantees are pinned here:

    1. The prose degrades (``errors="backslashreplace"``) rather than raising, so the
       run completes and the em dash survives as an escape rather than killing the audit.
    2. Even if a render failure did occur, it no longer wears the audit's exit code —
       ``ShipReadinessError`` still returns ``1`` (``-33`` above), any other rendering
       ``ValueError`` leaves ``verdict.exit_code`` intact.

    Not monkeypatched: a real repository, a real audit, a real narrow-codec stream.
    """
    import io

    (tmp_path / "mod.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    (tmp_path / "test_mod.py").write_text(
        "from mod import add\n\n\ndef test_add():\n    assert add(1, 2) == 3\n",
        encoding="utf-8",
    )

    out_stream = io.TextIOWrapper(io.BytesIO(), encoding="utf-8", newline="")
    # The narrow console: cp437 has no U+2014.
    err_stream = io.TextIOWrapper(io.BytesIO(), encoding="cp437", newline="")
    real_out, real_err = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = out_stream, err_stream
    try:
        code = cli.main(["audit", str(tmp_path)])
    finally:
        out_stream.flush()
        err_stream.flush()
        stdout_text = out_stream.buffer.getvalue().decode("utf-8")
        stderr_text = err_stream.buffer.getvalue().decode("cp437")
        sys.stdout, sys.stderr = real_out, real_err

    assert code == 0, (
        "a completed audit must return its own verdict's exit code; the console's "
        f"code page is not a verdict. stderr was:\n{stderr_text}"
    )
    assert "verdict=RELEASE_READY" in stdout_text
    # The falsehood that must never be printed about a run that succeeded.
    assert "audit failed" not in stderr_text
    # The prose still reached the operator, with only the un-encodable char degraded.
    assert "Ship-readiness: READY" in stderr_text


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


def test_cli_commit_defaults_to_head(tmp_path: Path) -> None:
    """TC-ArgusAgent-CLI-001-04 — --commit defaults to HEAD; a first run needs NO flags.

    Supersedes the original "commit is REQUIRED" contract. Requiring it made three
    preconditions (a git repo, a clean tree, and an explicit pin) stand between a new
    user and their first audit — and refusing to run produces no audit at all, which
    protects nobody. The pin is still honoured when present; ``--strict`` restores the
    refuse-on-drift contract for a release gate.
    """
    parser = cli.build_parser()
    args = parser.parse_args(["audit", str(tmp_path)])

    assert args.commit == "HEAD"
    assert args.strict is False


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
