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
- ``--commit`` — OPTIONAL, defaulting to ``HEAD``. A pinned commit is the FR1
  determinism precondition, and this contract was originally written as REQUIRED
  with "no silent HEAD default". The default was later relaxed so a first run works
  on any directory — including one with no git metadata at all — and the enforcement
  moved to ``--strict``, but THIS PARAGRAPH WAS NOT UPDATED and went on asserting the
  opposite of the shipped behaviour on the single flag that carries the determinism
  guarantee. The binding statement is: the pin is enforced by ``--strict`` (below),
  which refuses a non-git, dirty, or ``HEAD != --commit`` tree; without it the audit
  proceeds over whatever source state is present and RECORDS which state that was
  (``intake/source_state.resolve_source_state``), so a relaxed run is still honest
  about what it examined — it is simply not reproducible.
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

The rest of the accepted surface (added 2026-08-10 by Story 10.3 / ``DF-AUD-APAA-E``)
-------------------------------------------------------------------------------------
The block above stopped at SEVEN arguments and the parser accepts FOURTEEN. Six of
the missing flags had ZERO occurrences anywhere in the binding contract corpus
(``E-PRD/prd.md``, ``E-PRD/addendum.md``, ``architecture.md``, ``epics.md``,
``CHANGELOG.md``, ``README.md``) — they were accepted by the shipped tool and
specified nowhere. Commit ``230bf5c`` repaired the ``--commit`` paragraph above and
left that omission untouched; this completes it. **This block is the contract
statement closest to the code, and ``tests/test_invocation_contract.py``
(``TC-ArgusAgent-CLI-001-38``) now fails if any accepted flag is missing from it.**

- ``--strict`` — ``store_true``, DEFAULT ``False``. Release-gate mode: requires a git
  repository, a clean working tree and ``HEAD == --commit``, refusing otherwise
  (``intake/source_state.resolve_source_state``). This is the enforcement of the FR1
  determinism pin described under ``--commit`` above. OFF by default so a first run
  works on any directory. Entered in ``ae5f00c`` (Epic 8); specified by Story 10.3.
- ``--passes <csv>`` — DEFAULT: every pass (``_ALL_PASSES``). An exact selection; a
  trailing comma is not a selection, and an explicit flag selecting NOTHING stays
  empty rather than reverting to the default. Entered in ``084c6a7``; Story 10.3.
- ``--skip-pass <pass>`` — REPEATABLE, DEFAULT ``None``. Subtracts from whatever
  ``--passes`` selected, so the two compose in ONE direction only: a skip can never
  re-add a pass the operator excluded. Entered in ``084c6a7``; Story 10.3.
- ``--reports <csv>`` — DEFAULT ``_DEFAULT_REPORTS`` (``final-verdict``,
  ``coverage-ledger``). Selects the report types rendered. ⚠️ **CONDITIONALLY INERT:
  reports are only rendered when ``--report-dir`` is set, so ``--reports`` alone
  renders nothing.** Entered in ``084c6a7``; specified by Story 10.3, which also
  records that ``.github/workflows/argus-student-audit.yml`` depends on it.
- ``--report-dir <path>`` — DEFAULT ``""`` (render nothing). Output directory for the
  generated Markdown reports; the switch that makes ``--reports`` do anything.
- ``--ignore-path <glob>`` — REPEATABLE, DEFAULT ``[]``. Extends the built-in
  ``detectors/secret_suppression.DEFAULT_TEST_PATH_PATTERNS`` for the secret scan.
  Matched with ``fnmatchcase`` (NFR-P1 — never ``fnmatch``, which lower-cases on
  Windows). **It cannot suppress a high-confidence live production key.**
- ``--ignore-pattern <substr>`` — REPEATABLE, DEFAULT ``[]``. Suppresses a secret
  finding whose value contains the pattern. Matched by BARE SUBSTRING, so a short
  pattern is a wide net. **Since Story 10.3 it is evaluated BELOW the Live-Key
  Safeguard** — before that, ``--ignore-pattern A`` silently suppressed every live
  AWS key, GitHub PAT, Slack token and PEM private key in the repository. A
  suppression either of the two ``--ignore-*`` flags causes is now RECORDED as a
  non-blocking, redacted ``operator_suppressed_secret:<reason>`` finding and DISCLOSED
  on stderr. Threat model: ``architecture.md`` §G *"Suppression threat model"*.
- ``--deep-audit`` — ``store_true``, DEFAULT ``False``. Story 12.2 / FR36. Enables the
  LLM-backed deep-audit pass by adding the EXISTING ``deep`` pass token to
  ``enabled_passes`` — it is a new ENTRANCE, not a new mechanism, so ``--skip-pass deep``
  still subtracts it and the one ``deep`` vocabulary runs end to end (flag →
  ``enabled_passes`` → ``LLM_DEEP_PASSES`` → ``render_depth_meaning``). **THIS FLAG IS
  THE ONLY OPT-IN TO EGRESS.** It is a flag rather than a ``--passes`` token or an
  environment variable for three measured reasons: (a) ``--passes …,deep`` was ALREADY
  accepted and already produced a false deep claim (Story 12.2 §0.5), so making that
  spelling the consent would collide the fix with the feature; (b) ``--passes`` is an
  EXACT selection, so ``--passes deep`` alone silently disables every deterministic
  safety pass — a footgun on the one flag that must be unambiguous; (c) the ``[llm]``
  extra is NOT an egress gate (it contains only ``litellm``, while ``httpx`` is a BASE
  dependency, so a no-extras install already carries a complete egress path), and
  ``OpenLLMAdapter`` silently absorbs six environment variables, so neither packaging nor
  the environment can constitute an operator act. Off, the run is byte-identical to a
  pre-12.2 run and transmits nothing.
- ``--coverage-scope {repository,application}`` — DEFAULT ``application``. The
  population the deep-coverage gate assesses. ⚠️ **Deliberate, documented divergence
  (Story 10.3 / DN-8): ``AuditRequest.coverage_scope`` defaults to ``repository``, so a
  library consumer constructing the request directly gets a different assessed
  population than a CLI consumer.** Both are shipped, announced defaults; neither is
  changed here, and ``TC-ArgusAgent-CLI-001-37b`` pins the divergence in both
  directions so it cannot drift or close by accident.

**The accepted surface is DERIVED, never transcribed.** ``build_parser`` below is the
source of truth; this prose is checked against it by ``TC-ArgusAgent-CLI-001-35``
(equality, both directions) and ``-37`` (defaults and shapes). A flag added to the
parser without a contract site turns those red — that is the guard working.

The CLI is a developer-tool invocation contract (argv / stdout / exit-code), NOT a
UI (CLAUDE.md §3.7) — no HTML/CSS/JS, no web surface. ArgusAgent is downstream of the
HTTP/A2A boundary (it takes no token, registers no route — AR9).
"""

from __future__ import annotations

import argparse
import sys

from argus.detectors.secret_scan import RULE_OPERATOR_SUPPRESSED_SECRET
from argus.models import AuditRequest
from argus.pipeline import run_audit
from argus.reports.plain_english import (
    ShipReadinessError,
    deep_pass_enabled,
    render_ship_readiness,
    with_deep_pass,
)
from argus.verdict.negative_assurance import (
    INSTRUMENT_STATUS,
    render_instrument_disclosure,
)
from argus.verdict.verdict_gate import AuditVerdict

__all__ = ["build_parser", "main"]

_PROG = "argus"
# Exit code reserved for a fatal/typed pipeline error (AR3 — the crash code).
_CRASH_EXIT_CODE = 1
# The full pass set a bare invocation runs, and the reports a bare invocation renders.
_ALL_PASSES = ("coverage", "vacuous", "security", "orphan", "prosecutor")
_DEFAULT_REPORTS = ("final-verdict", "coverage-ledger")
# NOTE the deep pass is deliberately ABSENT from `_ALL_PASSES`: FR36 is off by default,
# ALWAYS, so a bare invocation must never select it. It is selected only by
# `--deep-audit`, through `with_deep_pass` — this module never spells the token itself,
# so the flag, the pass set and the disclosure cannot drift apart (AR7 / §3.3).


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
        "--deep-audit",
        dest="deep_audit",
        action="store_true",
        help=(
            "Enable the LLM-backed deep-audit pass (FR36). OFF BY DEFAULT, ALWAYS. This "
            "is the ONLY way to enable it: no environment variable and no packaging "
            "extra turns it on. Enabling it SENDS REPOSITORY METADATA TO A THIRD-PARTY "
            "PROVIDER — the run states what will be transmitted and to which provider "
            "before the first byte leaves. Without a provider endpoint configured the "
            "pass degrades honestly (a recorded finding + a coverage downgrade) and "
            "never fabricates a deep read."
        ),
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


def _harden_output_streams() -> None:
    """Make the output streams tolerate characters the console cannot encode.

    The HUMAN register is full of em dashes (every ship-readiness headline carries
    one). On a console whose code page cannot encode them — Windows cp437/cp850,
    ``PYTHONIOENCODING=ascii``, POSIX ``LC_ALL=C`` — writing that prose raises
    ``UnicodeEncodeError``, which is a ``ValueError``. PROSE MUST NEVER BE THE THING
    THAT FAILS A RUN: degrade the un-encodable characters instead, so a completed
    audit reports its own verdict rather than the terminal's limitation.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="backslashreplace")  # type: ignore[union-attr]
        except (AttributeError, ValueError):  # pragma: no cover - non-reconfigurable stream
            pass


def _split_csv(raw: str | None, default: tuple[str, ...]) -> tuple[str, ...]:
    """Parse a comma-separated option into a tuple; an omitted flag yields ``default``.

    Blank segments are dropped so a trailing comma is not a selection. An explicit flag
    that selects nothing at all stays empty rather than silently reverting to the
    default — narrowing to zero is an operator statement, not a missing one.
    """
    if not raw:
        return default
    return tuple(item.strip() for item in raw.split(",") if item.strip())


def _resolve_passes(args: argparse.Namespace) -> tuple[str, ...]:
    """Resolve ``--passes`` / ``--skip-pass`` into the enabled pass tuple.

    ``--skip-pass`` subtracts from whatever ``--passes`` selected, so the two compose
    in one direction only: a skip can never re-add a pass the operator excluded.

    Story 12.2: ``--deep-audit`` ADDS the existing ``deep`` token before the subtraction,
    which is what keeps the composition one-directional in the same sense — the flag is a
    selection, ``--skip-pass deep`` is still able to remove it, and a skip still cannot
    re-add anything. Adding it before the subtraction rather than after is deliberate:
    the alternative would make ``--deep-audit`` override an explicit ``--skip-pass deep``,
    i.e. let a convenience flag silently win over an operator's explicit exclusion, on
    the one pass where that exclusion means *do not transmit my source*.
    """
    enabled = _split_csv(args.passes, _ALL_PASSES)
    if getattr(args, "deep_audit", False):
        enabled = with_deep_pass(enabled)
    if not args.skip_pass:
        return enabled
    skipped = set(args.skip_pass)
    return tuple(name for name in enabled if name not in skipped)


def _build_request(
    args: argparse.Namespace, enabled_passes: tuple[str, ...]
) -> AuditRequest:
    """Project the parsed namespace onto the frozen ``AuditRequest`` (FR30).

    Pure translation — every ``or ()`` here is argparse's ``append`` default (``None``)
    being normalised to the empty tuple the model requires, NOT a policy decision.
    """
    return AuditRequest(
        repo_path=args.repo,
        commit=args.commit,
        budget=args.budget,
        materiality_bar=args.materiality_bar,
        critical_paths=tuple(args.critical_subsystem or ()),
        excluded_critical_paths=tuple(args.exclude_critical or ()),
        enabled_passes=enabled_passes,
        enabled_reports=_split_csv(args.reports, _DEFAULT_REPORTS),
        report_dir=args.report_dir or "",
        ignore_paths=tuple(args.ignore_paths or ()),
        ignore_patterns=tuple(args.ignore_patterns or ()),
        coverage_scope=args.coverage_scope,
        strict=args.strict,
    )


def _emit_suppression_disclosure(verdict: AuditVerdict) -> None:
    """Disclose how many security findings the OPERATOR's own rules suppressed (Story 10.3/AC4.3).

    Printed on EVERY run, including when the answer is zero. A disclosure that only appears
    when something was hidden is one an operator learns nothing from — silence would be
    indistinguishable from "the feature is not wired".

    This is the register the project already uses for a narrowing: `--coverage-scope` is the
    precedent (`CHANGELOG.md` §Defaults) — a narrowing is PERMITTED, DISCLOSED, and never
    allowed to lower a bar. Before this, `--ignore-path` / `--ignore-pattern` were permitted
    and not disclosed: the operator's inputs were persisted into run-state provenance while
    the effect — that a secret was found and suppressed — left no trace at all.

    STDERR, like the human register and for the same reason: stdout is the wire contract a CI
    step parses positionally (FR18/AR3) and appending to it would break that. Secret-safe by
    construction (NFR-S1) — a count and a flag name, never a locator, a pattern or a value.
    """
    suppressed = sum(
        1
        for finding in verdict.ordered_findings
        if finding.rule_id.startswith(RULE_OPERATOR_SUPPRESSED_SECRET)
    )
    detail = (
        "none were"
        if suppressed == 0
        else f"{suppressed} were — they are recorded as `{RULE_OPERATOR_SUPPRESSED_SECRET}:*`"
    )
    print(
        f"{_PROG}: security findings suppressed by your --ignore-path/--ignore-pattern "
        f"rules: {detail}. A live production key is never suppressed by either flag.",
        file=sys.stderr,
    )


def _emit_egress_disclosure(message: str) -> None:
    """Disclose what will be transmitted and to whom, BEFORE the first byte (AC2.5).

    Story 12.2 / FR36 / NFR-S6. The pipeline hands this callable to the deep pass, which
    calls it BEFORE it dispatches anything — the ordering is the requirement, not the
    presence of a sentence. A disclosure printed at the end of a run tells an operator
    what already left; this one tells them what is about to.

    STDERR, for the reason every other disclosure in this module uses: stdout is the
    FR18/AR3 wire contract a CI step parses positionally, and appending prose to it would
    break that.

    It is UNCONDITIONAL within an opted-in run — it fires even when no provider is
    configured and therefore nothing will be sent, because "nothing will be transmitted"
    is exactly the fact an operator who just asked for a deep read needs to be told.
    """
    print(f"{_PROG}: {message}", file=sys.stderr)


def _emit_instrument_disclosure() -> None:
    """Disclose how the TOOL's own findings have been validated (FR34 / Story 11.1).

    Printed on EVERY invocation that emitted a ``verdict=`` line, unconditionally,
    including a clean ``RELEASE_READY`` run — ``_emit_suppression_disclosure``'s reason
    applies unchanged: a disclosure that only appears when something is wrong is one an
    operator learns nothing from.

    DISTINCT FROM THE SHIP-READINESS BLOCK AND FROM THE FR17 DISCLAIMER, and both apply.
    Those bound THIS AUDIT — what was assessed, how deeply, with what materiality bar.
    This bounds THE INSTRUMENT: an audit can be perfectly scoped and still be produced by
    a tool whose finding precision nobody has measured. It is also NOT the run grade: it
    does not move when a deeper pass is engaged, and it is removed only by Epic 13
    clearing the >=80% precision gate.

    STDERR, for the reason the human register and the suppression disclosure both use:
    stdout is the FR18/AR3 wire contract a CI step parses positionally, and appending to
    it would break that. THE RESIDUAL IS REAL AND IS RECORDED RATHER THAN HIDDEN — a
    consumer that discards stderr sees a verdict without the disclosure. It is bounded by
    the invariant above (a ``verdict=`` line and this line always appear together in one
    invocation) and by the fact that the machine consumer's own artifacts — the four
    generated reports — each carry it too.

    The text is the ONE constant in ``argus/verdict/negative_assurance.py``, never a
    second copy: the listing surfaces are compared against it rather than transcribed.
    """
    print(
        f"{_PROG}: {render_instrument_disclosure(INSTRUMENT_STATUS)}",
        file=sys.stderr,
    )


def _emit_ship_readiness(
    verdict: AuditVerdict, enabled_passes: tuple[str, ...]
) -> int | None:
    """Print the human register to stderr; return an exit code ONLY on contract violation.

    HUMAN REGISTER, guarded SEPARATELY (DF-8-3-B). It goes to STDERR on purpose: stdout
    is the wire contract a CI step / orchestrating agent parses positionally (FR18/AR3),
    and appending prose to it would break that. Two failures are possible here and they
    are NOT the same class, so they do not share an exit code:

    * ``ShipReadinessError`` — the renderer refusing a verdict FR16 cannot produce. That
      is a CONTRACT VIOLATION; the run is not trustworthy, so it degrades to the AR10
      typed exit ``1``. Before DF-8-3-B this escaped ``main()`` as an uncaught traceback on
      every default invocation (masked only when ``--report-dir`` was set, because the
      pipeline renders the same block inside ``run_audit``, whose own guard caught it).
    * any other ``ValueError`` — overwhelmingly an encoding failure on the em-dash-bearing
      prose. The audit COMPLETED, persisted, and already printed its verdict on stdout.
      Reporting "audit failed" / exit ``1`` there would be a false statement about a run
      that succeeded, and would contradict the published contract that exit ``1`` means no
      verdict exists. The prose degrades; the verdict stands.

    Returns ``_CRASH_EXIT_CODE`` for the first case and ``None`` for the second — a
    ``None`` return means "the verdict's own exit code still governs".
    """
    try:
        for line in render_ship_readiness(verdict, enabled_passes=enabled_passes):
            print(line, file=sys.stderr)
    except ShipReadinessError as exc:
        print(f"{_PROG}: audit failed: {exc}", file=sys.stderr)
        return _CRASH_EXIT_CODE
    except ValueError as exc:
        print(f"{_PROG}: ship-readiness not rendered: {exc}", file=sys.stderr)
    return None


def main(argv: list[str] | None = None) -> int:
    """Parse argv → ``AuditRequest`` → pipeline → exit code (FR30/FR18/AR3).

    Returns the process exit code (testable without a real ``sys.exit``):
    ``AuditVerdict.exit_code`` (``0``/``2``/``3``) on a completed audit, or ``1``
    on a TYPED pipeline failure (with a secret-safe stderr line). NO business logic
    lives here — all audit logic is in ``pipeline.py`` + the reused modules.
    """
    _harden_output_streams()

    args = build_parser().parse_args(argv)
    enabled_passes = _resolve_passes(args)
    request = _build_request(args, enabled_passes)

    # AUDIT + WIRE CONTRACT. A failure here means no verdict reached the consumer, so
    # exit `1` is the honest answer (AR10 / NFR-R1).
    try:
        # The egress disclosure sink is handed to the pipeline ONLY when the operator
        # opted in. A default run's call is therefore EXACTLY the call it was before
        # Story 12.2 — no new keyword, no new object — which is one fewer thing that
        # could differ on the path AC2.4 requires to be byte-identical. It also avoids
        # handing a callback to a run that structurally cannot use it.
        deep_kwargs = (
            {"disclose": _emit_egress_disclosure}
            if deep_pass_enabled(enabled_passes)
            else {}
        )
        verdict = run_audit(request, **deep_kwargs)  # type: ignore[arg-type]
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

    readiness_failure = _emit_ship_readiness(verdict, enabled_passes)
    if readiness_failure is not None:
        # A ShipReadinessError is a CONTRACT VIOLATION: the run is not trustworthy and exits
        # `1`, meaning no verdict reached the consumer. Disclosing a suppression count beside
        # a verdict we have just refused to vouch for would dress a non-result as a result.
        #
        # FR34 still applies here, and that is not an inconsistency: a `verdict=` line HAS
        # reached stdout, and the instrument disclosure is a statement about the TOOL, never
        # about this run — it can only add caution to a refusal, never dress one as a result.
        # The invariant is therefore keyed on the verdict line, not on the exit code.
        _emit_instrument_disclosure()
        return readiness_failure

    # AFTER the human register, deliberately: `Ship-readiness: …` is the headline and stays
    # the first line an operator sees on stderr (pinned by tests/test_cli.py).
    _emit_suppression_disclosure(verdict)
    _emit_instrument_disclosure()

    return verdict.exit_code


if __name__ == "__main__":  # pragma: no cover - process entrypoint
    sys.exit(main())
