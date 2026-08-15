"""Story 10.3 / AC2.1 — each blessed flag has a BEHAVIOURAL acceptance criterion, pinned.

Verification area ArgusAgent-CLI (``TC-ArgusAgent-CLI-001-42``..``-48``, CONTINUING the index;
``-35``..``-41`` are the parser-vs-contract equality guard in ``tests/test_invocation_contract.py``).

``DF-AUD-APAA-E``'s remedy is *"bless with acceptance criteria and a CHANGELOG entry, or remove"* —
and the epic is explicit that a **sentence** is not an acceptance criterion. Six flags shipped in
``0.1.0`` with no specification at all; specifying them means writing down what they DO, and pinning
that. Every assertion below states behaviour that was MEASURED on 2026-08-10 and is deliberately
left unchanged: this is a specification-correction story, and AC2.3 forbids smuggling a behaviour
change in under "blessing". The one exception is the security-suppression layering, which AC4 makes
the CONDITION of the bless — pinned in ``tests/test_secret_suppression_recording.py``.

Two flags are specified elsewhere and are not duplicated here:

* ``--ignore-path`` / ``--ignore-pattern`` — ``tests/test_secret_suppression_recording.py``
  (``TC-ArgusAgent-SECRET-001-15``..``-22``), because their acceptance criterion IS the Live-Key
  Safeguard property and the operator-attributable record.
* ``--coverage-scope`` — its default divergence is DN-8's, pinned in both directions by
  ``TC-ArgusAgent-CLI-001-37b``.

``--help`` PROSE IS NOT THIS STORY'S. Story 12.8 asserts parser-vs-help parity *alongside* this
story's parser-vs-contract test; do not add help-text assertions here.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from argus import cli
from argus.detectors.secret_suppression import (
    DEFAULT_TEST_PATH_PATTERNS,
    SecretSuppressionEngine,
)
from argus.intake.source_state import SourceStateError, resolve_source_state


def _namespace(*argv: str):
    """Parse a full argv through the REAL parser — never a hand-built Namespace."""
    return cli.build_parser().parse_args(["audit", "/repo", *argv])


def _request(*argv: str):
    """argv → the frozen ``AuditRequest``, through the real translation path."""
    args = _namespace(*argv)
    return cli.build_request(args, cli.resolve_passes(args))


# ─────────────────────────────────────────────────────────────────────────────
# --passes / --skip-pass  (DN-3)
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_CLI_001_42_passes_selects_exactly_the_named_passes() -> None:
    """TC-ArgusAgent-CLI-001-42 — `--passes` is an exact selection, and empty means empty.

    Story 10.3 / AC2.1, DN-3. Three properties, all measured:
    an explicit CSV selects exactly those passes; a trailing comma is not a selection (a blank
    segment is dropped rather than becoming a pass named ``""``); and an explicit flag that selects
    NOTHING stays empty rather than silently reverting to the default — narrowing to zero is an
    operator statement, not a missing one, and reverting would run five passes the operator just
    asked not to run.
    """
    assert _request("--passes", "coverage,security").enabled_passes == ("coverage", "security")
    assert _request().enabled_passes == cli._ALL_PASSES, "an omitted flag runs every pass"

    assert _request("--passes", "coverage,").enabled_passes == ("coverage",)
    assert _request("--passes", " coverage , security ").enabled_passes == (
        "coverage",
        "security",
    )

    assert _request("--passes", ",").enabled_passes == (), (
        "an explicit --passes that selects nothing silently reverted to the default pass set"
    )


def test_TC_ArgusAgent_CLI_001_43_skip_pass_is_repeatable_and_subtracts_only() -> None:
    """TC-ArgusAgent-CLI-001-43 — `--skip-pass` composes in ONE direction only.

    Story 10.3 / AC2.1, DN-3. It subtracts from whatever `--passes` selected, so a skip can never
    re-add a pass the operator excluded. The asymmetry is the point: two narrowing flags that could
    widen each other would let a typo silently broaden an audit the operator meant to bound.
    """
    assert _request("--skip-pass", "security").enabled_passes == tuple(
        name for name in cli._ALL_PASSES if name != "security"
    )
    assert _request("--skip-pass", "security", "--skip-pass", "orphan").enabled_passes == tuple(
        name for name in cli._ALL_PASSES if name not in ("security", "orphan")
    )

    # Subtracts from the --passes selection…
    assert _request("--passes", "coverage,security", "--skip-pass", "security").enabled_passes == (
        "coverage",
    )
    # …and CANNOT re-add. `orphan` was never selected, so skipping it changes nothing and, above
    # all, naming it does not bring it back.
    assert _request("--passes", "coverage", "--skip-pass", "orphan").enabled_passes == ("coverage",)
    assert "orphan" not in _request("--passes", "coverage", "--skip-pass", "orphan").enabled_passes

    # A skip that empties the selection leaves it empty, not defaulted.
    assert _request("--passes", "coverage", "--skip-pass", "coverage").enabled_passes == ()


# ─────────────────────────────────────────────────────────────────────────────
# --reports / --report-dir  (DN-4, AC7.2, AC7.3)
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_CLI_001_44_reports_selects_report_types_and_defaults_to_two() -> None:
    """TC-ArgusAgent-CLI-001-44 — `--reports` selects rendered report types.

    Story 10.3 / AC2.1, DN-4. `--reports` was missed by the 2026-08-09 audit even though a
    committed workflow depends on it (`.github/workflows/argus-student-audit.yml:48`), which is why
    removal was never free for this one the way it was for the other five.

    ⚠️ **CORRECTED 2026-08-15 by Story 12.8 / AC3, and the correction is evidence rather than
    maintenance.** The multi-token case below used to end in `vacuous-tests` — a token
    `generate_reports` has never rendered — and this guard asserted that the CLI faithfully
    carried it onto the request. It did, and that was the defect: nothing anywhere validated a
    report token, so `--reports vacuous-tests` selected a report that does not exist, rendered
    nothing, and said nothing. The committed workflow at `argus-student-audit.yml:48` shipped
    exactly that string. The token is replaced with `architecture-review`, which is REAL, so this
    guard still pins what it was written to pin — the CSV selection is honoured verbatim on the
    request — over a value the tool can actually deliver. The refusal itself is pinned in
    `tests/test_cli.py` (this file's `:22` fences it to behaviour of the blessed flags, and the
    accepted set is derived rather than transcribed there).
    """
    assert _request().enabled_reports == cli._DEFAULT_REPORTS == (
        "final-verdict",
        "coverage-ledger",
    )
    assert _request(
        "--reports", "final-verdict,coverage-ledger,security-review,architecture-review"
    ).enabled_reports == (
        "final-verdict",
        "coverage-ledger",
        "security-review",
        "architecture-review",
    )
    # Same CSV discipline as --passes: it is the one shared parser, not two.
    assert _request("--reports", "final-verdict,").enabled_reports == ("final-verdict",)


def test_TC_ArgusAgent_CLI_001_45_reports_is_conditionally_inert_without_report_dir() -> None:
    """TC-ArgusAgent-CLI-001-45 — `--reports` renders NOTHING unless `--report-dir` is set.

    Story 10.3 / AC2.1, AC7.2, DN-4. Blessing a flag while concealing that it does nothing half the
    time would be this epic's own defect committed inside its own remedy. The selection is still
    recorded on the request — it is the RENDERING that is conditional — so a run states what was
    asked for even when nothing was written.

    Pinned STRUCTURALLY rather than by executing an audit: the condition lives at
    ``pipeline.py:848`` (``if request.report_dir:``) and ``argus/pipeline.py`` is byte-fenced to
    Story 12.1, so this reads the committed source rather than importing a private symbol that a
    refactor inside that fence would break.
    """
    request = _request("--reports", "security-review")
    assert request.enabled_reports == ("security-review",)
    assert request.report_dir == "", "--report-dir defaults to empty, so nothing is rendered"

    pipeline_source = (
        Path(__file__).resolve().parents[1] / "argus" / "pipeline.py"
    ).read_text(encoding="utf-8")
    assert "if request.report_dir:" in pipeline_source, (
        "the report-rendering condition this contract statement describes has moved. `--reports`' "
        "documented conditional inertness (CHANGELOG '### Specified: `--reports` and "
        "`--report-dir`') is now a claim about code that no longer exists — re-measure and amend "
        "the contract rather than deleting this assertion."
    )

    with_dir = _request("--reports", "security-review", "--report-dir", "out")
    assert with_dir.report_dir == "out"


# ─────────────────────────────────────────────────────────────────────────────
# --strict  (DN-5)
# ─────────────────────────────────────────────────────────────────────────────


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        env={"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
             "GIT_COMMITTER_EMAIL": "t@t", "PATH": __import__("os").environ.get("PATH", "")},
    )


def test_TC_ArgusAgent_CLI_001_46_strict_is_off_by_default_and_reaches_the_request() -> None:
    """TC-ArgusAgent-CLI-001-46 — `--strict` is `store_true`, OFF by default, and wired through.

    Story 10.3 / AC2.1, DN-5. `--strict` is the enforcement of the FR1 determinism pin —
    `cli.py`'s own docstring names it as the BINDING statement of that pin — and it had zero
    occurrences in the binding contract corpus. Off by default is the load-bearing half: a first run
    must work on any directory, including one with no git metadata at all.
    """
    assert _request().strict is False, "--strict must stay OFF by default (a first run works anywhere)"
    assert _request("--strict").strict is True


@pytest.mark.skipif(
    subprocess.run(["git", "--version"], capture_output=True).returncode != 0,
    reason="git is not available on this host",
)
def test_TC_ArgusAgent_CLI_001_47_strict_refuses_a_dirty_tree_and_a_head_mismatch(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-CLI-001-47 — release-gate mode refuses what it promises to refuse.

    Story 10.3 / AC2.1, DN-5. The non-git refusal is already pinned by
    ``test_source_state.py::test_strict_refuses_without_git_and_explains_the_way_forward``; the
    other two arms of the same contract sentence were pinned by nothing. Without `--strict` the same
    trees are audited as-is and recorded honestly as non-reproducible — that is AR10, and it is why
    the flag exists rather than the refusal being unconditional.
    """
    root = tmp_path / "repo"
    root.mkdir()
    (root / "app.py").write_text("x = 1\n", encoding="utf-8")
    _git(root, "init", "-q")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "one")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True
    ).stdout.strip()

    # Clean + pinned: strict is satisfied.
    assert resolve_source_state(root, commit=head, strict=True).reproducible is True

    # HEAD != --commit.
    (root / "app.py").write_text("x = 2\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "two")
    with pytest.raises(SourceStateError, match="working tree drift"):
        resolve_source_state(root, commit=head, strict=True)
    assert resolve_source_state(root, commit=head).kind is not None, (
        "without --strict the same tree is audited as-is, not refused"
    )

    # Dirty tree.
    (root / "app.py").write_text("x = 3\n", encoding="utf-8")
    with pytest.raises(SourceStateError, match="uncommitted changes"):
        resolve_source_state(root, strict=True)
    assert resolve_source_state(root).reproducible is False, (
        "without --strict a dirty tree is audited and RECORDED as non-reproducible (AR10)"
    )


# ─────────────────────────────────────────────────────────────────────────────
# --ignore-path  (DN-5) — the extension half; the safeguard half is SECRET-001-15..-22
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_CLI_001_48_ignore_path_extends_the_built_in_fixture_patterns() -> None:
    """TC-ArgusAgent-CLI-001-48 — `--ignore-path` EXTENDS the defaults; it never replaces them.

    Story 10.3 / AC2.1, DN-5. The flag mirrors `DEFAULT_TEST_PATH_PATTERNS`, and Argus's own report
    recommends it (`reports/generator.py`). Matching is `fnmatchcase`, never `fnmatch` — NFR-P1
    host-invariance: `fnmatch` lower-cases on Windows, so the same repository would hide a
    credential on one host and report it on another.
    """
    assert SecretSuppressionEngine.is_test_fixture_path("vendor/blob.py") is False
    assert SecretSuppressionEngine.is_test_fixture_path("vendor/blob.py", ("vendor/**",)) is True

    # The built-ins survive the extension.
    for pattern_sample in ("tests/x.py", "pkg/test_x.py", "pkg/fixtures/x.py", "pkg/mock_x.py"):
        assert SecretSuppressionEngine.is_test_fixture_path(pattern_sample, ("vendor/**",)) is True
    assert DEFAULT_TEST_PATH_PATTERNS, "the built-in fixture patterns must not be empty"

    # Host-invariant: case is significant, and it errs toward REPORTING a secret.
    assert SecretSuppressionEngine.is_test_fixture_path("Vendor/blob.py", ("vendor/**",)) is False

    assert _request("--ignore-path", "vendor/**", "--ignore-path", "third_party/**").ignore_paths == (
        "vendor/**",
        "third_party/**",
    ), "--ignore-path must be repeatable and preserve operator order"


# ─────────────────────────────────────────────────────────────────────────────
# AC4.3 — the disclosure an operator actually sees
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_CLI_001_49_every_run_discloses_its_operator_suppression_count(
    tmp_path: Path, capsys
) -> None:
    """TC-ArgusAgent-CLI-001-49 — the run says how many findings the operator's rules suppressed.

    Story 10.3 / AC4.3. The register is the one the project already uses for a narrowing:
    ``--coverage-scope`` is the precedent — a narrowing is PERMITTED, DISCLOSED, and never allowed
    to lower a bar. Before this, ``--ignore-path``/``--ignore-pattern`` were permitted and NOT
    disclosed.

    Disclosed on EVERY run, including when the answer is zero: a line that appears only when
    something was hidden teaches an operator nothing, because silence is indistinguishable from
    "the feature is not wired". STDERR, because stdout is the FR18/AR3 wire contract a CI step
    parses positionally.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    secret = "Plausible" + "Secret" + "Value01234567890123"
    (repo / "app.py").write_text(f'TOKEN = "{secret}"\n\n\ndef go():\n    return TOKEN\n', encoding="utf-8")
    (repo / "test_app.py").write_text("from app import go\n\n\ndef test_go():\n    assert go()\n", encoding="utf-8")

    cli.main(["audit", str(repo)])
    baseline = capsys.readouterr()
    assert "security findings suppressed by your --ignore-path/--ignore-pattern rules: none were" in (
        baseline.err
    ), f"a run that suppressed nothing did not say so:\n{baseline.err}"
    assert secret not in baseline.err and secret not in baseline.out, (
        "the disclosure register leaked the secret (NFR-S1)"
    )

    cli.main(["audit", str(repo), "--ignore-pattern", secret[:10]])
    suppressed = capsys.readouterr()
    assert "rules: 1 were" in suppressed.err, (
        f"an operator-caused suppression was not disclosed:\n{suppressed.err}"
    )
    assert "operator_suppressed_secret:*" in suppressed.err
    assert secret not in suppressed.err, "the disclosure leaked the secret it suppressed (NFR-S1)"
    assert secret[:10] not in suppressed.err, (
        "the disclosure echoed the operator's --ignore-pattern, which may itself be secret bytes"
    )
    assert str(repo) not in suppressed.err, "the disclosure leaked an absolute host path (AR8)"
