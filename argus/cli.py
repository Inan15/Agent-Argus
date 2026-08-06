"""IMPURE ``argus`` console entrypoint — thin ``argparse`` invocation contract.

Drivers: ArgusAgent-FR-30 (headless invocation contract — ``argus audit <repo> --commit
<sha> --budget <X> --materiality-bar <bar>`` builds the request), ArgusAgent-FR-18
(deterministic exit code + machine-readable verdict summary), AR2 (stdlib
``argparse`` ONLY — zero new dependency), AR3 (exit-code wire contract
``0``/``2``/``3``/``1``), AR8 (pure/impure separation — the CLI is the impure
shell: argv parsing + request construction + pipeline call + stdout/stderr/exit;
all audit logic lives in ``pipeline.py`` and the reused modules), ArgusAgent-NFR-M1
(≤1200-line files; NO business logic in the entrypoint), ArgusAgent-NFR-S1 (the verdict
summary carries the verdict token + deep-% + blocking count + relative locators —
never source / secret bytes / an absolute host path).

THIN WIRING ONLY (CLAUDE.md §3.1 spirit / NFR-M1)
-------------------------------------------------
``main(argv=None) -> int`` parses the LOCKED invocation contract into an
:class:`~argus.models.AuditRequest`, calls ``pipeline.run_audit``,
prints a secret-safe machine-readable summary to stdout, and RETURNS the 1.6
``AuditVerdict.exit_code`` (``0``/``2``/``3``). A TYPED pipeline failure
(``RepoIntakeError`` / ``WorkspaceContainmentError`` / ``CanonicalSerializationError``
/ ``PipelineError`` / any ``ValueError``) is mapped to a secret-safe stderr line +
return ``1`` (the reserved crash code, AR3/AR10) — never a Python traceback to the
user. ``main`` is testable WITHOUT a real ``sys.exit`` (it returns the code); the
console wrapper does ``sys.exit(main())``.

The LOCKED CLI contract (frozen + documented per the story)
-----------------------------------------------------------
``argus audit <repo> --commit <sha> --budget <int> --materiality-bar <bar>``
- sub-command ``audit`` (the only V1 sub-command; an additive seam for future ones)
- positional ``<repo>`` — the audited-repo path → ``AuditRequest.repo_path``
- ``--commit`` — REQUIRED (a pinned commit is the FR1 determinism precondition;
  there is no silent HEAD default — an unpinned audit is not reproducible)
- ``--budget`` — an ``int`` of credits (AR4 — argparse ``type=int`` rejects a
  float spelling) → ``AuditRequest.budget``. Story 3.1 gives it CONFIGURATION
  meaning: ``0`` / omitted = NO ceiling (OI3 — first-class no-ceiling; no
  hardcoded numeric default, deferred to Story 7.1), a positive value configures
  the ceiling the cost accounting accounts against (the mid-run halt is Story 3.2)
- ``--materiality-bar`` — a free string → ``AuditRequest.materiality_bar``
  (recorded; not applied in V1, Epic 4)
- ``--critical-subsystem <path>`` — REPEATABLE (``action="append"``), OPTIONAL →
  ``AuditRequest.critical_paths`` (Story 2.3, FR4): force a repo-relative path
  critical (the lever for a true critical the 2.1 substring matcher missed)
- ``--exclude-critical <path>`` — REPEATABLE, OPTIONAL →
  ``AuditRequest.excluded_critical_paths`` (Story 2.3, FR4): remove a path from the
  critical set (the documented correction for a 2.1 substring over-flag; exclude
  wins on a tie). Both designation flags are ADDITIVE (NFR-M2) — a pre-2.3
  invocation without them is byte-identical.

The CLI is a developer-tool invocation contract (argv / stdout / exit-code), NOT a
UI (CLAUDE.md §3.7) — no HTML/CSS/JS, no web surface. ArgusAgent is downstream of the
HTTP/A2A boundary (it takes no token, registers no route — AR9).
"""

from __future__ import annotations

import argparse
import sys

from argus.models import AuditRequest
from argus.pipeline import run_audit
from argus.reports.plain_english import ShipReadinessError, render_ship_readiness

__all__ = ["build_parser", "main"]

_PROG = "argus"
# Exit code reserved for a fatal/typed pipeline error (AR3 — the crash code).
_CRASH_EXIT_CODE = 1


def build_parser() -> argparse.ArgumentParser:
    """Build the LOCKED stdlib-``argparse`` parser (AR2 — zero new dependency)."""
    parser = argparse.ArgumentParser(
        prog=_PROG,
        description="ArgusAgent — coverage-grounded release-readiness auditor (headless).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser(
        "audit",
        help="Audit a repository @ a pinned commit and emit a verdict + exit code.",
    )
    audit.add_argument("repo", help="Path to the repository to audit.")
    audit.add_argument(
        "--commit",
        default="HEAD",
        help=(
            "Commit to pin (ref/short-SHA/tag). Defaults to HEAD. Only meaningful with "
            "a clean git tree; a dirty tree or a directory without git is audited as-is "
            "and labelled accordingly in the report."
        ),
    )
    audit.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Release-gate mode: require a git repository, a clean working tree, and "
            "HEAD == --commit, refusing otherwise. Use this in CI, where commit-pinned "
            "evidence is the contract. Off by default so a first run works anywhere."
        ),
    )
    audit.add_argument(
        "--budget",
        type=int,
        default=0,
        help=(
            "The configured audit ceiling in credits (int). Omitted / 0 = NO ceiling "
            "(OI3 — no hardcoded numeric default; the dogfood ceiling is sized in "
            "Story 7.1). A positive value configures the ceiling the cost accounting "
            "(Story 3.1) accounts against; the mid-run halt on exhaustion is Story 3.2."
        ),
    )
    audit.add_argument(
        "--materiality-bar",
        dest="materiality_bar",
        default="",
        help="Materiality bar (free string; recorded, not applied in V1).",
    )
    # Story 2.3 — ADDITIVE operator-designation channel (FR4/FR30/NFR-M2). Both are
    # repeatable (action="append") and OPTIONAL; absent → byte-identical to pre-2.3.
    audit.add_argument(
        "--critical-subsystem",
        dest="critical_subsystem",
        action="append",
        default=None,
        metavar="PATH",
        help="Force a repo-relative path critical (repeatable). FR4 operator designation.",
    )
    audit.add_argument(
        "--exclude-critical",
        dest="exclude_critical",
        action="append",
        default=None,
        metavar="PATH",
        help=(
            "Exclude paths from the critical set (repeatable; exclude wins on a tie). "
            "Accepts an exact path, a directory prefix that clears the whole subtree "
            "(`tests`), or a glob (`argus/*/__init__.py`)."
        ),
    )
    audit.add_argument(
        "--passes",
        dest="passes",
        default=None,
        help="Comma-separated audit passes to run (e.g. 'coverage,security,orphan,vacuous,prosecutor'). Default: all.",
    )
    audit.add_argument(
        "--skip-pass",
        dest="skip_pass",
        action="append",
        default=None,
        metavar="PASS",
        help="Audit pass to skip (e.g. '--skip-pass security'). Repeatable.",
    )
    audit.add_argument(
        "--reports",
        dest="reports",
        default=None,
        help="Comma-separated report types to render (e.g. 'final-verdict,coverage-ledger,security-review').",
    )
    audit.add_argument(
        "--report-dir",
        dest="report_dir",
        default="",
        help="Output directory path for generated Markdown reports.",
    )
    audit.add_argument(
        "--ignore-path",
        action="append",
        dest="ignore_paths",
        default=[],
        help="Path glob pattern to ignore / treat as mock fixture (can specify multiple).",
    )
    audit.add_argument(
        "--ignore-pattern",
        action="append",
        dest="ignore_patterns",
        default=[],
        help="Secret string pattern to exclude from findings (can specify multiple).",
    )
    audit.add_argument(
        "--coverage-scope",
        dest="coverage_scope",
        choices=("repository", "application"),
        default="application",
        help=(
            "Population the deep-coverage gate assesses. 'application' (default) holds "
            "out test files, which are graded shallow BY CONSTRUCTION — they are the "
            "subject of the vacuous-test pass, never a target of deep grounding — and so "
            "can only ever dilute the ratio. 'repository' counts every file, including "
            "those test files; use it for the strict whole-tree view. Either way the "
            "assessed population is disclosed on the verdict and in the report, both "
            "ratios are printed, and the coverage floor is re-applied WITHIN the scope, "
            "so a narrowing can never lower the bar for a claim."
        ),
    )
    return parser


def _summary_line(
    verdict_token: str,
    deep_ratio: object,
    blocking: int,
    scope: object = None,
) -> str:
    """A secret-safe machine-readable summary (NFR-S1 — no source/secret/abs-path).

    Emits ``verdict=<TOKEN> deep_ratio=<num/den> blocking_findings=<n>`` — the
    verdict token + the exact ``Fraction`` deep-ratio (``num/den``, never a float)
    + the verdict-eligible blocking count. No file content, no absolute host path.

    When the assessment was NARROWED, the ratio the gate actually decided on is
    appended as ``assessed_deep_ratio``/``scope`` alongside the unchanged
    whole-repository ``deep_ratio``. Printing only the whole-repository ratio next to
    a scoped verdict reads as a contradiction (a RELEASE_READY beside a 39% ratio);
    printing only the scoped one would hide the repository-wide truth. Both, always.
    """
    line = f"verdict={verdict_token} deep_ratio={deep_ratio} blocking_findings={blocking}"
    if scope is not None:
        line += (
            f" assessed_deep_ratio={scope.assessed_deep_ratio}"  # type: ignore[attr-defined]
            f" scope={scope.scope_id}"  # type: ignore[attr-defined]
            f" held_out={scope.excluded_count}"  # type: ignore[attr-defined]
        )
    return line


def main(argv: list[str] | None = None) -> int:
    """Parse argv → ``AuditRequest`` → pipeline → exit code (FR30/FR18/AR3).

    Returns the process exit code (testable without a real ``sys.exit``):
    ``AuditVerdict.exit_code`` (``0``/``2``/``3``) on a completed audit, or ``1``
    on a TYPED pipeline failure (with a secret-safe stderr line). NO business logic
    lives here — all audit logic is in ``pipeline.py`` + the reused modules.
    """
    # The HUMAN register is full of em dashes (every ship-readiness headline carries
    # one). On a console whose code page cannot encode them — Windows cp437/cp850,
    # ``PYTHONIOENCODING=ascii``, POSIX ``LC_ALL=C`` — writing that prose raises
    # ``UnicodeEncodeError``, which is a ``ValueError``. PROSE MUST NEVER BE THE THING
    # THAT FAILS A RUN: degrade the un-encodable characters instead, so a completed
    # audit reports its own verdict rather than the terminal's limitation.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="backslashreplace")  # type: ignore[union-attr]
        except (AttributeError, ValueError):  # pragma: no cover - non-reconfigurable stream
            pass

    parser = build_parser()
    args = parser.parse_args(argv)

    all_passes = ("coverage", "vacuous", "security", "orphan", "prosecutor")
    if args.passes:
        enabled_passes = tuple(p.strip() for p in args.passes.split(",") if p.strip())
    else:
        enabled_passes = all_passes

    if args.skip_pass:
        skips = set(args.skip_pass)
        enabled_passes = tuple(p for p in enabled_passes if p not in skips)

    if args.reports:
        enabled_reports = tuple(r.strip() for r in args.reports.split(",") if r.strip())
    else:
        enabled_reports = ("final-verdict", "coverage-ledger")

    request = AuditRequest(
        repo_path=args.repo,
        commit=args.commit,
        budget=args.budget,
        materiality_bar=args.materiality_bar,
        critical_paths=tuple(args.critical_subsystem or ()),
        excluded_critical_paths=tuple(args.exclude_critical or ()),
        enabled_passes=enabled_passes,
        enabled_reports=enabled_reports,
        report_dir=args.report_dir or "",
        ignore_paths=tuple(args.ignore_paths or ()),
        ignore_patterns=tuple(args.ignore_patterns or ()),
        coverage_scope=args.coverage_scope,
        strict=args.strict,
    )


    # AUDIT + WIRE CONTRACT. A failure here means no verdict reached the consumer, so
    # exit `1` is the honest answer (AR10 / NFR-R1).
    try:
        verdict = run_audit(request)
        print(
            _summary_line(
                verdict.verdict.value,
                verdict.deep_ratio,
                verdict.blocking_finding_count,
                verdict.coverage_scope,
            )
        )
    except ValueError as exc:
        # RepoIntakeError / WorkspaceContainmentError / CanonicalSerializationError
        # / PipelineError are all ValueError subclasses — TYPED, secret-safe (AR10).
        # The message names the typed reason only, never source / an absolute path.
        print(f"{_PROG}: audit failed: {exc}", file=sys.stderr)
        return _CRASH_EXIT_CODE

    # HUMAN REGISTER, guarded SEPARATELY (DF-8-3-B). It goes to STDERR on purpose: stdout
    # is the wire contract a CI step / orchestrating agent parses positionally (FR18/AR3),
    # and appending prose to it would break that. Two failures are possible here and they
    # are NOT the same class, so they do not share an exit code:
    #
    #   * `ShipReadinessError` — the renderer refusing a verdict FR16 cannot produce. That
    #     is a CONTRACT VIOLATION; the run is not trustworthy, so it degrades to the AR10
    #     typed exit `1`. Before DF-8-3-B this escaped `main()` as an uncaught traceback on
    #     every default invocation (masked only when `--report-dir` was set, because the
    #     pipeline renders the same block inside `run_audit`, whose own guard caught it).
    #   * any other `ValueError` — overwhelmingly an encoding failure on the em-dash-bearing
    #     prose. The audit COMPLETED, persisted, and already printed its verdict on stdout.
    #     Reporting "audit failed" / exit `1` there would be a false statement about a run
    #     that succeeded, and would contradict the published contract that exit `1` means no
    #     verdict exists. The prose degrades; the verdict stands.
    try:
        for line in render_ship_readiness(verdict, enabled_passes=enabled_passes):
            print(line, file=sys.stderr)
    except ShipReadinessError as exc:
        print(f"{_PROG}: audit failed: {exc}", file=sys.stderr)
        return _CRASH_EXIT_CODE
    except ValueError as exc:
        print(f"{_PROG}: ship-readiness not rendered: {exc}", file=sys.stderr)

    return verdict.exit_code


if __name__ == "__main__":  # pragma: no cover - process entrypoint
    sys.exit(main())
