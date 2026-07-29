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
        required=True,
        help="Pinned commit (ref/short-SHA/tag) — REQUIRED (the FR1 determinism pin).",
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
        help="Exclude a repo-relative path from the critical set (repeatable; exclude wins on a tie).",
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
    return parser


def _summary_line(verdict_token: str, deep_ratio: object, blocking: int) -> str:
    """A secret-safe machine-readable summary (NFR-S1 — no source/secret/abs-path).

    Emits ``verdict=<TOKEN> deep_ratio=<num/den> blocking_findings=<n>`` — the
    verdict token + the exact ``Fraction`` deep-ratio (``num/den``, never a float)
    + the verdict-eligible blocking count. No file content, no absolute host path.
    """
    return f"verdict={verdict_token} deep_ratio={deep_ratio} blocking_findings={blocking}"


def main(argv: list[str] | None = None) -> int:
    """Parse argv → ``AuditRequest`` → pipeline → exit code (FR30/FR18/AR3).

    Returns the process exit code (testable without a real ``sys.exit``):
    ``AuditVerdict.exit_code`` (``0``/``2``/``3``) on a completed audit, or ``1``
    on a TYPED pipeline failure (with a secret-safe stderr line). NO business logic
    lives here — all audit logic is in ``pipeline.py`` + the reused modules.
    """
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
    )


    try:
        verdict = run_audit(request)
    except ValueError as exc:
        # RepoIntakeError / WorkspaceContainmentError / CanonicalSerializationError
        # / PipelineError are all ValueError subclasses — TYPED, secret-safe (AR10).
        # The message names the typed reason only, never source / an absolute path.
        print(f"{_PROG}: audit failed: {exc}", file=sys.stderr)
        return _CRASH_EXIT_CODE

    print(
        _summary_line(
            verdict.verdict.value,
            verdict.deep_ratio,
            verdict.blocking_finding_count,
        )
    )
    return verdict.exit_code


if __name__ == "__main__":  # pragma: no cover - process entrypoint
    sys.exit(main())
