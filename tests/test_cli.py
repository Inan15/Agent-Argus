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

    # Patched at `run_audit_detailed` since 2026-08-15 (Story 12.8 / AC7 / DN-4): `cli.main`
    # calls that entry now, because the grammar-downgrade diagnosis rides on `AuditResult`.
    # `run_audit` is a thin wrapper that returns `run_audit_detailed(...).verdict`, so the
    # substitution is at the same seam and this guard's observable is unchanged.
    monkeypatch.setattr(cli, "run_audit_detailed", _boom)
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
    from argus.pipeline import AuditResult

    # `run_audit_detailed` (Story 12.8 / DN-4) — see `-32`'s note. The stand-in returns the
    # real `AuditResult` value holder rather than a bare verdict, which is what `main` reads.
    monkeypatch.setattr(
        cli,
        "run_audit_detailed",
        lambda _request: AuditResult(verdict=impossible, locators=()),
    )

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


def test_cli_budget_rejects_float(tmp_path: Path, capsys) -> None:
    """TC-ArgusAgent-CLI-001-05 — AC1/AR4: --budget is int-typed (a float spelling is rejected).

    ⚠️ **UPDATED DELIBERATELY 2026-08-15 by Story 12.8 / AC8, and the update is the story's
    RED evidence rather than collateral.** This test asserted ``pytest.raises(SystemExit)``,
    which passed because argparse exits ``2`` — and ``action.yml:129`` maps exit ``2`` to
    ``verdict=NOT_READY_FOR_RELEASE assessed=true``. So the shipped behaviour this guard
    pinned was: *a typo publishes a fabricated assessment for a run that never happened*.
    The rejection is still the contract (AR4 — ``--budget`` is ``int``-typed); what changed
    is what the process says about it. ``main`` now returns the reserved AR3 crash code
    ``1`` — *the audit did not complete and NO verdict was produced* — which ``action.yml``
    already renders as ``AUDIT_FAILED`` / ``assessed=false``.

    Do NOT "fix" a future failure of this test by restoring ``SystemExit``: that would
    restore the false verdict. The sibling surface already ruled the same way —
    ``argus/mcp/server.py:107`` catches the parser's ``SystemExit`` and answers *"the audit
    invocation was rejected by the parser"*, explicitly not a verdict.
    """
    code = cli.main(["audit", str(tmp_path), "--commit", "HEAD", "--budget", "1.5"])

    assert code == 1, "a usage error produces NO verdict; 2 and 3 are verdict codes"
    captured = capsys.readouterr()
    # argparse's own cause is still printed…
    assert "invalid int value: '1.5'" in captured.err
    # …and FR37's next action now says what the exit code means (Story 12.8 / AC8).
    assert "NO verdict was produced" in captured.err
    assert captured.out == "", "no wire-contract line for a run that never happened"


def test_cli_unknown_subcommand_rejected(capsys) -> None:
    """TC-ArgusAgent-CLI-001-06 — AC3: an unknown sub-command is rejected (sub-command required).

    ⚠️ **UPDATED DELIBERATELY 2026-08-15 by Story 12.8 / AC8** — see ``-05``'s docstring for
    the full reason. The rejection is unchanged; the published exit code is now ``1``
    (no verdict) instead of ``2`` (``NOT_READY_FOR_RELEASE``).
    """
    code = cli.main(["bogus"])

    assert code == 1
    assert "invalid choice: 'bogus'" in capsys.readouterr().err


def test_cli_help_still_exits_zero_and_is_not_mapped(capsys) -> None:
    """TC-ArgusAgent-CLI-001-55 — Story 12.8 / AC8: ``--help`` is NOT a usage error.

    The mapping in ``main`` keys on the exit CODE argparse chose, so the one thing that
    could go wrong is over-catching: ``--help`` also raises ``SystemExit`` out of
    ``parse_args``, with code ``0``. If that were mapped, every ``argus --help`` in a
    Makefile, a Dockerfile healthcheck or a CI smoke step would start failing.

    ``SystemExit(0)`` is re-raised UNTOUCHED, so the process still exits ``0`` and the
    usage-error sentence never appears beside a successful help render.
    """
    for argv in (["--help"], ["audit", "--help"], ["install-commands", "--help"]):
        with pytest.raises(SystemExit) as raised:
            cli.main(argv)
        assert raised.value.code == 0, f"{argv} must still exit 0"
        captured = capsys.readouterr()
        assert "NO verdict was produced" not in captured.err, (
            f"{argv} was mapped as a usage error — the SystemExit(0) arm over-caught"
        )
        assert "usage:" in captured.out


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


# ─────────────────────────────────────────────────────────────────────────────────────
# Story 12.8 — the operator-error diagnosis surface (AC3 / AC5 / AC6 / AC7)
#
# This file's own docstring already claims "a bad repo -> exit 1 with a secret-safe stderr
# line", so this is that claim's home. Every guard below names its observable, moves it with
# a REAL defect at the REAL seam, and (where it closes over a registry or a grammar) drives
# an adversarial variant GENERATED from that registry rather than hand-written (AI-E11-1).
# ─────────────────────────────────────────────────────────────────────────────────────


def _host_path_forms(path: Path) -> tuple[str, ...]:
    """Every spelling an absolute host path can wear in a message (Story 12.8 / AC6).

    A bare substring search for ``str(tmp_path)`` is NOT sufficient and the difference is not
    academic: ``str(OSError)`` embeds the filename through ``repr``, so on Windows the path
    arrives BACKSLASH-ESCAPED on Windows and a raw comparison misses it entirely —
    the containment guard would have been green against the very leak it exists to catch.
    Three forms are searched: as-is, ``repr``-escaped, and POSIX-slashed (which is how several
    layers here normalise a path before printing it).
    """
    raw = str(path)
    return tuple({raw, raw.replace("\\", "\\\\"), path.as_posix()})


def _tiny_repo(root: Path) -> Path:
    """A minimal auditable tree — one graded source file and one test for it."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "mod.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    (root / "test_mod.py").write_text(
        "from mod import add\n\n\ndef test_add():\n    assert add(1, 2) == 3\n",
        encoding="utf-8",
    )
    return root


def test_TC_ArgusAgent_CLI_001_56_a_typo_on_a_closed_vocabulary_is_refused(
    tmp_path: Path, capsys
) -> None:
    """TC-ArgusAgent-CLI-001-56 — Story 12.8 / AC3: the false-green channel is closed.

    **THE defect this story exists to close.** Measured on `2f84a0b` by executing the real
    CLI: `argus audit <repo> --passes securty` returned `verdict=RELEASE_READY`, **exit 0**,
    and printed NOTHING about the typo — because `resolve_passes` returned `('securty',)`,
    every membership test in `pipeline_stages` was then False, and so **every detector pass
    was silently disabled**. A run that looked at nothing can only report zero blocking
    findings. That is a false green produced by one transposed letter, on the flag whose
    entire purpose is selecting safety passes, in the direction `epics.md:2336-2339` calls
    the most dangerous one this tool has.

    **Observable:** the exit code and stderr of the real `cli.main`. Three closed
    vocabularies, and the adversarial token for each is GENERATED from the flag's own live
    accepted set (a real member with one character removed), never hand-typed — so a
    vocabulary that gains a member is still adversarially probed with no edit here.
    """
    repo = _tiny_repo(tmp_path / "repo")
    parser = cli.build_parser()
    audit = parser._subparsers._group_actions[0].choices["audit"]  # noqa: SLF001

    probed = 0
    for action in audit._actions:  # noqa: SLF001
        accepted = getattr(action.type, "accepted", ())
        if not accepted:
            continue
        probed += 1
        spelling = action.option_strings[0]
        real_token = accepted[0]
        typo = real_token[:-1]  # generated from the registry, never hand-written
        assert typo not in accepted, "the generated adversarial token is accidentally valid"

        code = cli.main(["audit", str(repo), spelling, typo])
        captured = capsys.readouterr()

        assert code == 1, (
            f"{spelling} {typo!r} returned {code}. A rejected invocation produces NO verdict; "
            "0/2/3 are verdict codes and returning one for a typo is a fabricated assessment"
        )
        assert f"unknown {spelling} value(s)" in captured.err, (
            f"{spelling} accepted the unknown token {typo!r} silently: {captured.err!r}"
        )
        assert typo in captured.err, "the refusal does not name the offending token"
        assert real_token in captured.err, (
            "the refusal does not name the accepted set, so it names a cause with no fix"
        )
        assert "verdict=" not in captured.out, (
            "a refused invocation still emitted a wire-contract verdict line"
        )

    assert probed >= 3, (
        f"only {probed} closed-vocabulary flag(s) were probed — expected at least the three "
        "AC3 names (--passes, --skip-pass, --reports). The accepted set is read off the live "
        "parser, so a flag losing its validator makes this RED rather than silently green."
    )


def test_TC_ArgusAgent_CLI_001_57_the_committed_workflow_line_is_the_live_instance(
    tmp_path: Path, capsys
) -> None:
    """TC-ArgusAgent-CLI-001-57 — Story 12.8 / AC3: the RED was a committed file, not a fixture.

    AI-E11-1 clause (ii) asks for the defect to be demonstrated at the REAL seam. It does not
    get more real than this: `.github/workflows/argus-student-audit.yml:48` shipped
    `--reports "final-verdict,coverage-ledger,security-review,vacuous-tests"`, and
    `vacuous-tests` is not a report type `generate_reports` has ever rendered. Three reports
    were written, a fourth was silently not, and nothing said so.

    Two halves, and both are needed. (a) The historical string is REFUSED now — the exact
    bytes that shipped. (b) The committed workflow no longer contains it, so
    `TC-ArgusAgent-DOCS-001-28` (every documented invocation must parse) stays green for the
    right reason rather than because the check was weakened.
    """
    repo = _tiny_repo(tmp_path / "repo")

    code = cli.main([
        "audit", str(repo),
        "--reports", "final-verdict,coverage-ledger,security-review,vacuous-tests",
    ])
    assert code == 1
    err = capsys.readouterr().err
    assert "unknown --reports value(s) ['vacuous-tests']" in err

    workflow = (
        Path(__file__).resolve().parents[1]
        / ".github" / "workflows" / "argus-student-audit.yml"
    ).read_text(encoding="utf-8")
    assert "vacuous-tests" not in workflow, (
        "the committed workflow still requests a report type that does not exist; the fix is "
        "to correct the workflow, never to weaken the refusal"
    )


def test_TC_ArgusAgent_CLI_001_58_open_vocabularies_are_disclosed_not_refused(
    tmp_path: Path, capsys
) -> None:
    """TC-ArgusAgent-CLI-001-58 — Story 12.8 / AC3 / DN-3: the other half of the split.

    A path is an OPEN vocabulary: refusing one that matches nothing would break the legitimate
    case of designating a subtree absent from this partition. So these are DISCLOSED. Measured
    on `2f84a0b`, the silence was expensive — `--critical-subsystem does/not/exist` moved the
    verdict from `RELEASE_READY` (exit 0) to `INSUFFICIENT_COVERAGE` (exit 3) and printed
    *"Critical files not examined deeply: 1"* for a path that does not exist.

    **Both directions**, because a disclosure that always fires teaches nothing either: a
    designation that DOES match must produce no such sentence.
    """
    repo = _tiny_repo(tmp_path / "repo")

    # (a) Unmatched -> disclosed, and the run still completes with its real verdict.
    code = cli.main(["audit", str(repo), "--critical-subsystem", "does/not/exist"])
    err = capsys.readouterr().err
    assert code in (0, 2, 3), "an open-vocabulary miss is disclosed, never refused"
    assert "does/not/exist" in err and "no file or directory" in err

    # (b) A designation that matches produces NO disclosure — the guard is not a rubber stamp.
    cli.main(["audit", str(repo), "--critical-subsystem", "mod.py"])
    assert "no file or directory" not in capsys.readouterr().err

    # (c) --reports without --report-dir is inert, and says so (measured: silent before).
    cli.main(["audit", str(repo), "--reports", "final-verdict"])
    inert = capsys.readouterr().err
    assert "--report-dir is not set" in inert and "NO report file was written" in inert

    # (d) …and with --report-dir it does NOT say so.
    cli.main([
        "audit", str(repo), "--reports", "final-verdict",
        "--report-dir", str(tmp_path / "out"),
    ])
    assert "--report-dir is not set" not in capsys.readouterr().err


def test_TC_ArgusAgent_CLI_001_59_two_bad_paths_are_two_distinguishable_causes(
    tmp_path: Path, capsys
) -> None:
    """TC-ArgusAgent-CLI-001-59 — Story 12.8 / AC3: one message for two causes is one too few.

    Measured on `2f84a0b`: `argus audit /no/such/path` and `argus audit README.md` produced the
    **identical** line, *"repo path is not a directory"*. The first path does not exist and the
    second is a file — different mistakes, different corrections. `repo_loader.py` has always
    distinguished them; `source_state.resolve_source_state`, which every CLI audit actually
    reaches, never did.

    Also pins the FIX half of AC3: each names an act that changes the outcome, not just a cause.
    """
    a_file = tmp_path / "a_file.md"
    a_file.write_text("not a repository\n", encoding="utf-8")

    missing_code = cli.main(["audit", str(tmp_path / "nope")])
    missing = capsys.readouterr().err
    file_code = cli.main(["audit", str(a_file)])
    a_file_err = capsys.readouterr().err

    assert missing_code == file_code == 1
    assert "does not exist" in missing, missing
    assert "is not a directory" in a_file_err, a_file_err
    assert missing.splitlines()[0] != a_file_err.splitlines()[0], (
        "the two causes still render the same first line, so an operator cannot tell a "
        "missing path from a path that is a file"
    )
    # Every one of them names an ACT, not only a condition (FR37).
    for text in (missing, a_file_err):
        assert "re-run" in text, f"a cause with no fix reached the operator: {text!r}"


def test_TC_ArgusAgent_CLI_001_60_an_internal_defect_is_distinguishable_from_a_degradation(
    tmp_path: Path, capsys, monkeypatch
) -> None:
    """TC-ArgusAgent-CLI-001-60 — Story 12.8 / AC5, closing `DF-8-4-D`. BOTH directions.

    The ledger entry is about `cli.py`'s `except ValueError`: Pydantic's `ValidationError` is a
    `ValueError` subclass, so an internal defect was reported to the operator in the same words
    as an expected typed refusal. **The trap the entry does not state, and the reason a
    CLI-only split cannot close it:** `argus/pipeline.py`'s four stage wraps already converted
    ANY unexpected exception into a `PipelineError`, which `cli.py`'s own comment enumerates as
    an EXPECTED degradation — so the defect arrived at the CLI *pre-disguised*. The distinction
    is therefore carried from the WRAP SITE, by `pipeline.UnexpectedStageError`.

    **Direction one, at the real seam:** a `pydantic.ValidationError` is injected INSIDE the
    intake stage (not at the CLI arm), so it travels the real wrap path, and the run must carry
    the `INTERNAL DEFECT` token and where to report it.

    **Direction two:** a genuine typed degradation — a repository path that does not exist,
    driven with no monkeypatching at all — must NOT carry that token. One direction alone is
    half a guard: a CLI that printed "INTERNAL DEFECT" on every failure would pass the first.
    """
    import pydantic

    from argus import pipeline
    from argus.reports.plain_english import ARGUS_ISSUE_TRACKER, INTERNAL_DEFECT_MARKER

    class _Model(pydantic.BaseModel):
        n: int

    def _real_pydantic_error() -> pydantic.ValidationError:
        try:
            _Model(n="not-an-int")
        except pydantic.ValidationError as exc:
            return exc
        raise AssertionError("pydantic accepted an invalid payload")

    def _explode(*_args, **_kwargs):
        raise _real_pydantic_error()

    # Direction one — injected at the REAL intake seam, so pipeline.py's wrap runs.
    monkeypatch.setattr(pipeline, "resolve_source_state", _explode)
    code = cli.main(["audit", str(tmp_path)])
    captured = capsys.readouterr()

    assert code == 1, "an internal defect still exits 1 — no fifth wire code (AR3 is frozen)"
    assert INTERNAL_DEFECT_MARKER in captured.err, (
        "a Pydantic ValidationError inside a stage reached the operator wearing the words of "
        f"an expected degradation: {captured.err!r}"
    )
    assert ARGUS_ISSUE_TRACKER in captured.err, "the defect names no place to report it"
    assert "ValidationError" in captured.err, "the exception CLASS is the payload DF-10-4-C asks for"
    assert "Traceback" not in captured.err
    # NFR-S1 / DF-10-4-C: the CLASS, never `str(exc)` — pydantic's message body carries the
    # offending input and a URL to its own docs, and is not this surface's to republish.
    assert "not-an-int" not in captured.err
    monkeypatch.undo()

    # Direction two — a REAL typed degradation, no patching, must stay distinguishable.
    code = cli.main(["audit", str(tmp_path / "definitely-absent")])
    degradation = capsys.readouterr().err
    assert code == 1
    assert "does not exist" in degradation
    assert INTERNAL_DEFECT_MARKER not in degradation, (
        "an ordinary bad path was reported as a bug in Argus — the two have re-merged, in the "
        "other direction, and an operator is now told to file an issue about their own typo"
    )


def test_TC_ArgusAgent_CLI_001_61_no_diagnosis_carries_an_absolute_host_path(
    tmp_path: Path, capsys
) -> None:
    """TC-ArgusAgent-CLI-001-61 — Story 12.8 / AC6 / NFR-S1: a PROPERTY, not a spot check.

    `argus/cli.py`'s own contract claimed *"the message names the typed reason only, never
    source / an absolute path"*, and it was FALSE at the epic's own "unreadable repo" case:
    `intake/source_state.py:122` interpolated a raw `{exc}`, and `str(OSError)` is
    `[Errno 13] Permission denied: '<absolute host path>'` — the host path, verbatim, on stderr.

    The shape is `tests/test_secret_containment.py`'s, REUSED rather than forked: drive the
    REAL failure paths with a temporary directory whose absolute path is a known string, then
    assert that string is absent from **both** streams. Several failure causes are driven, not
    one, because the claim is about the surface rather than about a line.
    """
    marker = _host_path_forms(tmp_path.resolve())
    repo = _tiny_repo(tmp_path / "repo")

    invocations = (
        ["audit", str(tmp_path / "missing-repo")],                 # path does not exist
        ["audit", str(repo / "mod.py")],                           # a file, not a directory
        ["audit", str(repo), "--commit", "deadbeefdeadbeef"],      # unresolvable pin
        ["audit", str(repo), "--strict"],                          # not a git repository
    )
    for argv in invocations:
        cli.main(argv)
        captured = capsys.readouterr()
        # The operator's OWN argv is echoed by the shell, not by us: the guard asserts the
        # tool never ADDS the host path to its diagnosis.
        for stream_name, stream in (("stdout", captured.out), ("stderr", captured.err)):
            leaked = [form for form in marker if form in stream]
            assert not leaked, (
                f"{argv} leaked the absolute host path {leaked} onto {stream_name}: "
                f"{stream!r} (NFR-S1)"
            )
        assert captured.err.strip(), f"{argv} produced no diagnosis at all"


def test_TC_ArgusAgent_CLI_001_62_the_absolute_path_guard_bites(tmp_path: Path) -> None:
    """TC-ArgusAgent-CLI-001-62 — Story 12.8 / AC6: the positive control for `-61`.

    A containment guard that finds nothing passes on any output, including no output at all.
    This reconstructs the EXACT interpolation that shipped — `f"…: {exc}"` over a real
    `OSError` — and proves the property `-61` asserts genuinely fails on it. The reconstruction
    is a real exception raised by a real unreadable path, never a hand-written string.
    """
    marker = _host_path_forms(tmp_path.resolve())
    absent = tmp_path / "nope.py"
    try:
        absent.read_bytes()
    except OSError as exc:
        shipped_form = f"could not read 'nope.py' while pinning source state: {exc}"
        corrected_form = (
            f"could not read 'nope.py' while pinning source state ({type(exc).__name__})."
        )
    else:  # pragma: no cover - the path cannot exist
        raise AssertionError("reading an absent file did not raise")

    assert any(form in shipped_form for form in marker), (
        "the reconstruction of the shipped message does not carry the host path in ANY of "
        "its spellings, so `-61` would have been green against the very defect it exists to "
        f"catch. Message was: {shipped_form!r}"
    )
    assert not any(form in corrected_form for form in marker), (
        "the CORRECTED form still carries the host path — the remedy does not remedy"
    )
    # …and the corrected form still names the typed reason, which is what makes it a
    # diagnosis rather than a redaction (DF-10-4-C: the CLASS is the safe payload).
    assert "FileNotFoundError" in corrected_form


def test_TC_ArgusAgent_CLI_001_63_a_broken_grammar_reaches_the_default_run(
    tmp_path: Path, capsys, monkeypatch
) -> None:
    """TC-ArgusAgent-CLI-001-63 — Story 12.8 / AC7 (NFR-P3, `DF-10-4-C`): 12.5's handover, wired.

    Story 12.5 wrote the sentence and said so in as many words: *"`render_grammar_downgrade_summary`
    is the function 12.8 wires"*. Measured on `2f84a0b` it had exactly ONE production caller —
    `reports/generator.py`, inside the report path, which runs only when `--report-dir` is set. So
    on the invocation almost everyone runs, a downgraded grammar was INVISIBLE: the operator saw a
    lower coverage ratio and no reason for it, which reads as a judgement about their code rather
    than about a toolchain that could not read it.

    **Proven at the real seam, exactly as AC7 requires.** The `importlib.import_module` hook is
    `tests/test_grammar_diagnosis.py`'s — the same one, on the same module attribute — so the
    grammar really fails to load inside the real `build_ast_index`, the real pipeline records the
    real `parse_failure_reason` token, and the real `cli.main` runs. Nothing about the renderer,
    the classifier or the CLI is stubbed.

    **And with NO `--report-dir`**, which is the whole point: that is the invocation on which the
    diagnosis did not exist.

    Homed HERE rather than in `tests/test_grammar_diagnosis.py` deliberately (Story 12.8, §Testing).
    That file is 1203 lines and sits in `test_module_size_ceiling._EXEMPT_BY_DESIGN` under
    `DF-12-1-C`, whose `target_story` is a story that is `done` and did not split it — so adding to
    it would grow an exemption nobody owns. This guard is a CLI-diagnosis guard and this file is
    where the other CLI-diagnosis guards live.
    """
    import importlib
    import types

    from argus.index import ast_index
    from argus.shared.grammar_status import GRAMMAR_PACKAGE_BY_LANGUAGE

    repo = tmp_path / "polyglot"
    repo.mkdir()
    (repo / "mod.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    (repo / "main.go").write_text(
        "package main\n\nfunc Add(a int, b int) int {\n\treturn a + b\n}\n", encoding="utf-8"
    )

    real_import = importlib.import_module

    def hook(name: str, package: str | None = None) -> types.ModuleType:
        if name == "tree_sitter_go":
            raise ImportError("simulated: the Go grammar package is not installed")
        return real_import(name, package)

    monkeypatch.setattr(ast_index.importlib, "import_module", hook)

    code = cli.main(["audit", str(repo)])  # NO --report-dir — the default invocation
    captured = capsys.readouterr()

    assert code in (0, 2, 3), "a grammar downgrade degrades the run; it never fails it"
    assert "Downgraded to `audited_shallow`" in captured.err, (
        "a Go file was downgraded because its grammar would not load and the DEFAULT run said "
        f"nothing about it. stderr was:\n{captured.err}"
    )
    # The remedy names the RIGHT package, from the one classifier — never a prefix guess.
    assert GRAMMAR_PACKAGE_BY_LANGUAGE["go"] in captured.err
    assert "grammar package not installed" in captured.err
    # The wire contract is untouched: prose stays on stderr (FR18/AR3).
    assert "Downgraded" not in captured.out
    # Ship-readiness stays the first line an operator sees (pinned ordering).
    assert captured.err.startswith("Ship-readiness:")
    # NFR-S1: the diagnosis carries no host path and no exception message.
    for form in _host_path_forms(tmp_path.resolve()):
        assert form not in captured.err
    assert "simulated:" not in captured.err, (
        "the exception MESSAGE reached the surface; DF-10-4-C and 10.4/DN-5 permit the "
        "class/cause only, never `str(exc)`"
    )


def test_TC_ArgusAgent_CLI_001_64_a_healthy_grammar_says_nothing(
    tmp_path: Path, capsys
) -> None:
    """TC-ArgusAgent-CLI-001-64 — Story 12.8 / AC7: the other direction, so `-63` is not vacuous.

    A disclosure that fires on every run carries no information, and a guard that only ever
    asserts presence would pass over a CLI that printed the downgrade sentence unconditionally.
    An ordinary Python-only repository, with every grammar it needs, must produce NO downgrade
    sentence at all — the coverage numbers already say everything there is to say.
    """
    repo = _tiny_repo(tmp_path / "repo")
    cli.main(["audit", str(repo)])
    err = capsys.readouterr().err

    assert "Downgraded to `audited_shallow`" not in err, (
        "a healthy run printed a grammar-downgrade remedy, so `-63` proves nothing"
    )
    assert "Ship-readiness:" in err, "the run did not actually produce its human register"
