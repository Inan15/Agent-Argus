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
:class:`~argus.models.AuditRequest`, calls ``pipeline.run_audit_detailed``,
prints a secret-safe machine-readable summary to stdout, and RETURNS the 1.6
``AuditVerdict.exit_code`` (``0``/``2``/``3``).

~~A TYPED pipeline failure (``RepoIntakeError`` / ``WorkspaceContainmentError`` /
``CanonicalSerializationError`` / ``PipelineError`` / any ``ValueError``) is mapped to a
secret-safe stderr line + return ``1`` (the reserved crash code, AR3/AR10) — never a Python
traceback to the user.~~ (§3.4 struck, not deleted — corrected 2026-08-15 by Story 12.8 /
AC5, closing ``DF-8-4-D``. The paragraph was accurate about the CATCH and false about what
the user was told, in two ways that compounded. First, *"any ``ValueError``"* is not a fifth
member of a list of four typed subclasses: it is the CATCH-ALL that swallows them, and
Pydantic's ``ValidationError`` — an internal defect — is a ``ValueError`` subclass, so a bug
in Argus was reported to the operator in the same words as an expected refusal. Second, and
this is why splitting THIS arm alone could not have closed it: ``pipeline.py``'s four stage
wraps already converted **any** unexpected exception into a ``PipelineError``, which the
list above enumerates as expected — so an internal defect arrived here PRE-DISGUISED and no
``except`` precision on this side could tell the two apart.)

**What ships.** Every failure below returns ``1`` — the reserved *no verdict was produced*
code — and no failure ever prints a Python traceback (AR3 is frozen; there is no fifth wire
code). The DISTINCTION is carried in the MESSAGE, which is what ``DF-8-4-D`` asked for:

- an EXPECTED, typed refusal — ``RepoIntakeError`` / ``SourceStateError`` (the repository or
  the pin), ``WorkspaceContainmentError``, ``CanonicalSerializationError``,
  ``PipelineError`` / ``ResumeStateError`` — prints the typed reason **and the operator
  action that changes it** (FR37: the next action is in the tool's own output);
- an INTERNAL DEFECT — ``pipeline.UnexpectedStageError`` (the stage wraps, which now carry
  the distinction from the wrap site), ``ShipReadinessError``, or any OTHER ``ValueError``
  reaching this module — prints the stable ``INTERNAL DEFECT`` token, says plainly that this
  is a bug in Argus rather than a problem with the user's repository, and names where to
  report it. It carries the exception CLASS, never ``str(exc)`` (``DF-10-4-C`` / NFR-S1).

The per-cause wording is ``reports/plain_english.render_audit_failed_next_action``, which
Story 12.4 shipped for FR37 and which had ZERO production callers until this story wired it.
It is EXTENDED, never duplicated (AR7) — the same words reach the CLI's audit arm, the CLI's
ship-readiness arm and the SECOND invocation surface's failure arm (the argv-free stdio
transport adapter Story 12.6 added; named by transport rather than protocol for the reason
recorded in the ``__all__`` note below — its token would make this module an unregistered
disclosure surface for ``tests/test_instrument_disclosure.py``'s ``-49`` closure).

**A USAGE error is not a verdict** (Story 12.8 / AC8). ``argparse`` exits ``2``, and
``action.yml`` publishes ``2`` as ``verdict=NOT_READY_FOR_RELEASE assessed=true`` — so until
2026-08-15 a typo (``--budget 1.5``, ``argus bogus``, a bare ``argus``) fabricated an
assessment for a run that never happened. ``main`` now maps a parser rejection to the same
reserved ``1``, which ``action.yml`` already renders as ``AUDIT_FAILED`` / ``assessed=false``.
``--help`` / ``-h`` still exits ``0``, untouched. The mapping lives in ``main`` and NEVER in
``build_parser`` or a parser subclass (DN-5), so ``build_parser().parse_args`` stays
byte-identical for every guard that drives it and for the second invocation surface, which
already ruled that a parse rejection is not a verdict.

``main`` is testable WITHOUT a real ``sys.exit`` (it returns the code); the console wrapper
does ``sys.exit(main())``.

The LOCKED CLI contract (frozen + documented per the story)
-----------------------------------------------------------
``argus audit <repo> --commit <sha> --budget <int> --materiality-bar <bar>``
- sub-command ``audit`` — ~~the only V1 sub-command; an additive seam for future ones~~
  (§3.4 struck, not deleted — 2026-08-15, Story 12.7 / FR35. The first clause became FALSE
  and the second was HONOURED: ``install-commands`` is the second V1 sub-command, and it
  entered through exactly the seam this sentence reserved. It is a sub-command rather than
  a fifth console alias precisely because of that record: 12.6's second alias was justified
  only by a DIFFERENT transport (a JSON-RPC message stream on stdio), while this step's
  transport is argv — identical to this one — so a separate alias would be a fork of an
  entry point rather than an extension of one (AR7 / architecture §3.3). Being a
  sub-command it adds no ``[project.scripts]`` entry, so the console-alias closures, the
  reachability floors and the second surface's published tool schema — which derives from
  the ``audit`` sub-parser alone — are all untouched. (This paragraph names that surface's
  TRANSPORT rather than its protocol on purpose: the protocol's token would make this
  module an unregistered disclosure surface for ``tests/test_instrument_disclosure.py``'s
  ``-49`` closure, and 12.6 ruled on exactly that trade — a false registry entry is worse
  than a coy docstring.)
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

The SECOND sub-command: ``argus install-commands`` (added 2026-08-15 by Story 12.7 / FR35)
-------------------------------------------------------------------------------------------
``argus install-commands [--host <name>]… [--dest <dir>] [--dry-run] [--remove]`` places the
packaged command assets (``argus/assets/commands/**``) into an assistant's configuration
directory, and removes them again. It is the ONE placement mechanism: ``install.sh``,
``install.ps1`` and ``uninstall.sh`` delegate to it rather than copying anything themselves,
which is what closes the measured defect that both of them created ``~/.claude/commands/``
and then copied the adapter files BESIDE it. All logic lives in ``argus/commands/**``
(NFR-M1 — no business logic in the entry point); this module declares the arguments, prints
the rendered outcome, and maps a typed failure to exit ``1`` exactly as ``audit`` does.

- ``--host <name>`` — REPEATABLE (``action="append"``), DEFAULT ``None``. Restricts the step
  to named hosts from the CLOSED registry in ``argus/commands/hosts.py``. Omitted means
  *every registered host whose configuration directory is DETECTED*; naming one skips
  detection, because an operator naming a host has already made the statement detection
  would infer. An unregistered name is a typed refusal, never a silent skip.
- ``--dest <dir>`` — DEFAULT ``""`` (the user's home directory). Overrides the
  host-configuration ROOT the registry's paths are relative to. This is the TESTABILITY
  SEAM: every guard drives the real step against a temporary directory, so no test in this
  suite reads or writes a real ``$HOME``.
- ``--dry-run`` — ``store_true``, DEFAULT ``False``. Resolves and containment-checks the
  whole plan, prints exactly what would be written, and writes nothing.
- ``--remove`` — ``store_true``, DEFAULT ``False``. Deletes exactly the files this step
  wrote — recognised by the marker each asset carries — and nothing else. It closes the
  asymmetry ``uninstall.sh`` had: it ran ``pip uninstall`` only, leaving every copied file
  in the user's home directory forever.

It obeys the CLI's existing contracts unchanged: the AR3 exit-code wire contract, a
secret-safe stderr line and return ``1`` on a typed failure (never a traceback, NFR-R1), no
absolute host path in any message (NFR-S1 — the outcome structure carries only
destination-relative paths), and no ``.argus/`` write, network call or egress. It writes
ONLY inside the resolved destination root; a path escaping it — via ``..``, an absolute
asset name, or a symlinked configuration directory — is refused with a typed error.

**The accepted surface is DERIVED, never transcribed.** ``build_parser`` below is the
source of truth; this prose is checked against it by ``TC-ArgusAgent-CLI-001-35``
(equality, both directions) and ``-37`` (defaults and shapes). A flag added to the
parser without a contract site turns those red — that is the guard working.

**So are the defaults in ``--help``** (added 2026-08-15 by Story 12.8 / AC2 / DN-2).
``build_parser`` installs ``argparse.ArgumentDefaultsHelpFormatter`` on every sub-parser, so
each argument's rendered help ends with the default the parser ACTUALLY holds. It is a
formatter rather than a sentence per flag because a hand-typed default is a transcription of
a pinned value — the class AI-E9-7 forbids and the exact drift ``-35``/``-37`` exist to close,
one layer out — and because a future flag inherits it with no edit anywhere.
``TC-ArgusAgent-CLI-001-52`` compares the rendered text against the live ``action.default``
over the SAME closure ``-35``/``-37``/``-38`` walk, so the two cannot drift. Three help
strings additionally carry the operator-consequence fact their contract paragraph above
already records — ``--reports`` is inert without ``--report-dir``; ``--ignore-pattern``
matches by bare substring; neither ``--ignore-*`` can suppress a live production key —
because omitting it is what costs a user a run.

**Three flags name a CLOSED, code-defined vocabulary and now REFUSE an unknown token**
(Story 12.8 / AC3 / DN-3): ``--passes``, ``--skip-pass`` and ``--reports``. The refusal
fires inside ``parse_args`` — so ``TC-ArgusAgent-DOCS-001-28`` catches a bad token in every
committed invocation automatically — and the accepted set is DERIVED from the one definition
of each (``_ALL_PASSES`` + ``plain_english.LLM_DEEP_PASSES``;
``reports/generator.ACCEPTED_REPORT_TOKENS``), never a second hand-list. Measured on
``2f84a0b``, ``--passes securty`` silently disabled EVERY detector pass and still returned
``RELEASE_READY`` exit ``0``: a false green opened by a typo, on the flag whose whole purpose
is selecting safety passes. The OPEN vocabularies — ``--critical-subsystem`` /
``--exclude-critical``, which take paths — are DISCLOSED on stderr instead of refused, because
designating a subtree absent from this partition is legal.

The CLI is a developer-tool invocation contract (argv / stdout / exit-code), NOT a
UI (CLAUDE.md §3.7) — no HTML/CSS/JS, no web surface. ArgusAgent is downstream of the
HTTP/A2A boundary (it takes no token, registers no route — AR9).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from argus.detectors.secret_scan import RULE_OPERATOR_SUPPRESSED_SECRET
from argus.models import AuditRequest
from argus.pipeline import run_audit_detailed
# The ONE definition of which report types exist (Story 12.8 / AC3). Before it, the
# renderer's vocabulary was four inline `if` literals with no constant naming them, which
# is why nothing could validate a `--reports` token: there was nothing to validate against.
from argus.reports.generator import ACCEPTED_REPORT_TOKENS
from argus.reports.plain_english import (
    LLM_DEEP_PASSES,
    ShipReadinessError,
    deep_pass_enabled,
    render_audit_failed_next_action,
    render_grammar_downgrade_summary,
    render_inert_reports_disclosure,
    render_ship_readiness,
    render_unmatched_designation_disclosure,
    render_usage_error_next_action,
    with_deep_pass,
)
from argus.verdict.negative_assurance import (
    INSTRUMENT_STATUS,
    render_instrument_disclosure,
)
from argus.verdict.verdict_gate import AuditVerdict

# PUBLIC SURFACE. `build_parser` and `main` were the whole of it until 2026-08-15, when
# Story 12.6 PROMOTED five names that were previously `_`-prefixed. The promotion is the
# point, not an incidental tidy-up: a SECOND invocation surface now projects argv onto the
# same `AuditRequest`, and the only two ways to give it that projection are to reuse this
# one or to write a second. A rule implemented twice drifts in one of the two — Story 11.3
# / DN-2 promoted `executable_line_numbers` for exactly this reason — and the rule at stake
# here is the one that decides WHICH POPULATION gets assessed (`--coverage-scope` defaults
# to `application` here while `AuditRequest.coverage_scope` defaults to `repository`, the
# announced Story 10.3 / DN-8 divergence). A copy of that projection would silently assess
# a different population and could return a different verdict on an unchanged repository.
# Reaching through an `_`-prefixed name would have been the same coupling without the
# promise, so the names are public, documented, and covered by the parity guard.
__all__ = [
    "PROG",
    "ClosedVocabulary",
    "build_parser",
    "build_request",
    "emit_egress_disclosure",
    "harden_output_streams",
    "main",
    "resolve_passes",
    "summary_line",
]

# The one program token every message this tool prints is prefixed with. Public since
# 2026-08-15 (Story 12.6) so a second surface reports a failure in the SAME words rather
# than spelling the prefix a second time.
PROG = "argus"
# Exit code reserved for a fatal/typed pipeline error (AR3 — the crash code).
_CRASH_EXIT_CODE = 1
# The full pass set a bare invocation runs, and the reports a bare invocation renders.
_ALL_PASSES = ("coverage", "vacuous", "security", "orphan", "prosecutor")
_DEFAULT_REPORTS = ("final-verdict", "coverage-ledger")
# NOTE the deep pass is deliberately ABSENT from `_ALL_PASSES`: FR36 is off by default,
# ALWAYS, so a bare invocation must never select it. It is selected only by
# `--deep-audit`, through `with_deep_pass` — this module never spells the token itself,
# so the flag, the pass set and the disclosure cannot drift apart (AR7 / §3.3).

# Every pass token the tool HAS, as opposed to the ones a bare run SELECTS (Story 12.8 /
# AC3). Composed from the two existing definitions rather than re-typed: `_ALL_PASSES`
# above, and `LLM_DEEP_PASSES` — the deep token's existing home in `plain_english`, which
# is why the `--deep-audit` opt-in and this validator cannot come to disagree about the
# spelling of `deep`. `--skip-pass deep` stays meaningful, which is Story 12.2's contract.
_ACCEPTED_PASSES: tuple[str, ...] = _ALL_PASSES + LLM_DEEP_PASSES


class ClosedVocabulary:
    """An argparse ``type=`` that REFUSES a token outside a closed, code-defined set.

    Story 12.8 / AC3 / DN-3. Three flags (``--passes``, ``--skip-pass``, ``--reports``) name
    members of finite sets defined in code, so an unmatched token is unambiguously a mistake
    and refusal is the honest answer. Measured on ``2f84a0b``, all three accepted anything:
    ``--passes securty`` made every membership test in ``pipeline_stages`` false, so EVERY
    detector pass was silently disabled and the run could only report zero blocking
    findings — a false-green channel opened by a typo, exit ``0``, with no message anywhere.

    **It is a ``type=`` callable and therefore fires INSIDE ``parse_args``**, which is the
    load-bearing choice rather than a convenience: ``TC-ArgusAgent-DOCS-001-28`` drives every
    committed invocation through the real ``build_parser().parse_args``, so from this change
    on, a bad token in README, ``action.yml``, a workflow or a shipped command asset is RED
    at edit time instead of silent at audit time. (It caught one immediately:
    ``.github/workflows/argus-student-audit.yml`` requested the report type
    ``vacuous-tests``, which does not exist.)

    The value is returned UNCHANGED, so ``args.passes`` / ``args.reports`` stay the raw
    strings ``build_request`` splits and ``-37``'s derived shapes and defaults are untouched.
    The accepted set is passed in from its ONE definition; this function holds no list.

    *hint* completes the message: the four exemplars already in the tree name a cause AND an
    act that changes it, and ``install-commands --host nosuch`` (Story 12.7) is the model
    for the refusal shape — *"unknown --host value(s) […]; this build supports […]"*.

    **It is a CLASS with a public ``accepted`` attribute rather than a closure**, so the
    accepted set is INTROSPECTABLE off the live parser (``action.type.accepted``).
    ``TC-ArgusAgent-CLI-001-36`` drives every registered spelling through the real parser with
    a sample value, and a fixed placeholder (``"x"``) is not a legal value for a closed
    vocabulary — so without this attribute that guard would have to hand-list a valid token
    per flag, which is the second hand-list AR7 forbids and the instrument this project has
    now found wrong four times. Reading it off the parser means a FUTURE closed-vocabulary
    flag is covered with no edit to the guard.
    """

    def __init__(
        self, flag: str, accepted: tuple[str, ...], *, csv: bool, hint: str
    ) -> None:
        self.flag = flag
        #: The live accepted set — introspected by the contract guards; never re-typed.
        self.accepted = accepted
        self.csv = csv
        self.hint = hint

    def __call__(self, raw: str) -> str:
        tokens = [t.strip() for t in raw.split(",")] if self.csv else [raw.strip()]
        unknown = [t for t in tokens if t and t not in self.accepted]
        if unknown:
            raise argparse.ArgumentTypeError(
                f"unknown {self.flag} value(s) {unknown}; this build supports "
                f"{list(self.accepted)}. {self.hint}"
            )
        return raw


def build_parser() -> argparse.ArgumentParser:
    """Build the LOCKED stdlib-``argparse`` parser (AR2 — zero new dependency).

    ``ArgumentDefaultsHelpFormatter`` is installed on the top-level parser and on every
    sub-parser (Story 12.8 / AC2 / DN-2), so every argument's rendered help ends with the
    default the parser ACTUALLY holds — derived, never transcribed. Argparse appends nothing
    to a POSITIONAL, which is correct and is the recorded decision for ``repo``: it is
    required, and "the default of a required argument" is not a fact that exists.
    """
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="ArgusAgent — coverage-grounded release-readiness auditor (headless).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser(
        "audit",
        help="Audit a repository @ a pinned commit and emit a verdict + exit code.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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
        type=ClosedVocabulary(
            "--passes",
            _ACCEPTED_PASSES,
            csv=True,
            hint=(
                "Correct the token, or omit --passes to run every deterministic pass — an "
                "unrecognised one used to disable every pass silently and still return a "
                "verdict."
            ),
        ),
        help=(
            "Comma-separated audit passes to run (e.g. "
            "'coverage,security,orphan,vacuous,prosecutor'). Omitted runs every "
            "deterministic pass; an unknown token is refused, never ignored."
        ),
    )
    audit.add_argument(
        "--skip-pass",
        dest="skip_pass",
        action="append",
        default=None,
        metavar="PASS",
        type=ClosedVocabulary(
            "--skip-pass",
            _ACCEPTED_PASSES,
            csv=False,
            hint="Correct the token, or drop --skip-pass to run the selected passes.",
        ),
        help=(
            "Audit pass to skip (e.g. '--skip-pass security'). Repeatable. Subtracts from "
            "whatever --passes selected; a skip can never re-add a pass you excluded."
        ),
    )
    audit.add_argument(
        "--reports",
        dest="reports",
        default=None,
        type=ClosedVocabulary(
            "--reports",
            ACCEPTED_REPORT_TOKENS,
            csv=True,
            hint="Correct the token, or omit --reports for the default selection.",
        ),
        help=(
            "Comma-separated report types to render (e.g. "
            "'final-verdict,coverage-ledger,security-review'). INERT WITHOUT --report-dir: "
            "reports are only written when an output directory is set, so --reports alone "
            "renders nothing. An unknown token is refused, never ignored."
        ),
    )
    audit.add_argument(
        "--report-dir",
        dest="report_dir",
        default="",
        help=(
            "Output directory path for generated Markdown reports. Empty renders nothing; "
            "this is the switch that makes --reports do anything."
        ),
    )
    audit.add_argument(
        "--ignore-path",
        action="append",
        dest="ignore_paths",
        default=[],
        help=(
            "Path glob pattern to ignore / treat as mock fixture (can specify multiple). "
            "IT CANNOT SUPPRESS A HIGH-CONFIDENCE LIVE PRODUCTION KEY — the Live-Key "
            "Safeguard is evaluated first, and every suppression is recorded and disclosed."
        ),
    )
    audit.add_argument(
        "--ignore-pattern",
        action="append",
        dest="ignore_patterns",
        default=[],
        help=(
            "Secret string pattern to exclude from findings (can specify multiple). "
            "MATCHED BY BARE SUBSTRING, so a short pattern is a wide net. IT CANNOT "
            "SUPPRESS A HIGH-CONFIDENCE LIVE PRODUCTION KEY — the Live-Key Safeguard is "
            "evaluated first, and every suppression is recorded and disclosed."
        ),
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

    # Story 12.7 / FR35 — the SECOND V1 sub-command, entering through the additive seam the
    # docstring above reserved. It is declared here, beside `audit`, because `build_parser`
    # is the single source of truth for the accepted surface; the logic it reaches is in
    # `argus/commands/**`. The `audit` sub-parser above is UNTOUCHED by this addition, which
    # is what keeps 12.6's published tool schema and argv projection — both derived from the
    # `audit` sub-parser alone — byte-identical. (Named by transport rather than protocol, for
    # the reason recorded in the module docstring.)
    install = subparsers.add_parser(
        "install-commands",
        help=(
            "Place the packaged assistant command assets into a supported assistant's "
            "configuration directory, or remove them again with --remove."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    install.add_argument(
        "--host",
        dest="host",
        action="append",
        default=None,
        metavar="NAME",
        help=(
            "Restrict the step to a registered assistant host (repeatable). Omitted: every "
            "registered host whose configuration directory is detected. An unregistered "
            "name is refused rather than skipped."
        ),
    )
    install.add_argument(
        "--dest",
        dest="dest",
        default="",
        metavar="DIR",
        help=(
            "Override the host-configuration root the registry's paths are relative to. "
            "Defaults to your home directory. Writes never leave the resolved root."
        ),
    )
    install.add_argument(
        "--dry-run",
        dest="dry_run",
        action="store_true",
        help="Resolve and check the whole plan, print what would be written, write nothing.",
    )
    install.add_argument(
        "--remove",
        dest="remove",
        action="store_true",
        help="Delete exactly the files this step wrote (recognised by their marker), and nothing else.",
    )
    return parser


def summary_line(
    verdict_token: str,
    deep_ratio: object,
    blocking: int,
    scope: object = None,
) -> str:
    """A secret-safe machine-readable summary (NFR-S1 — no source/secret/abs-path).

    PUBLIC since 2026-08-15 (Story 12.6) — see the ``__all__`` note above. The shape below
    is the FROZEN FR18/AR3 wire contract; a second surface that described the same run in
    different words would be a second contract, so it renders this one.

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


def harden_output_streams(*streams: object) -> None:
    """Make the output streams tolerate characters the console cannot encode.

    The HUMAN register is full of em dashes (every ship-readiness headline carries
    one). On a console whose code page cannot encode them — Windows cp437/cp850,
    ``PYTHONIOENCODING=ascii``, POSIX ``LC_ALL=C`` — writing that prose raises
    ``UnicodeEncodeError``, which is a ``ValueError``. PROSE MUST NEVER BE THE THING
    THAT FAILS A RUN: degrade the un-encodable characters instead, so a completed
    audit reports its own verdict rather than the terminal's limitation.

    PUBLIC since 2026-08-15 (Story 12.6) — see the ``__all__`` note above. Called with no
    arguments it hardens the process streams, exactly as it always did. A caller that owns
    its own streams passes them, which is what lets a second invocation surface inherit
    this defence instead of forking a second copy of it (AR7). A stream that cannot be
    reconfigured — an in-memory buffer, a non-text stream — is skipped, not an error.
    """
    for stream in streams or (sys.stdout, sys.stderr):
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


def resolve_passes(args: argparse.Namespace) -> tuple[str, ...]:
    """Resolve ``--passes`` / ``--skip-pass`` into the enabled pass tuple.

    PUBLIC since 2026-08-15 (Story 12.6) — see the ``__all__`` note above. Pure: it reads
    a parsed namespace and returns a tuple; it prints nothing and touches no filesystem.

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


def build_request(
    args: argparse.Namespace, enabled_passes: tuple[str, ...]
) -> AuditRequest:
    """Project the parsed namespace onto the frozen ``AuditRequest`` (FR30).

    Pure translation — every ``or ()`` here is argparse's ``append`` default (``None``)
    being normalised to the empty tuple the model requires, NOT a policy decision.

    PUBLIC since 2026-08-15 (Story 12.6) — see the ``__all__`` note above. This function
    is THE reason the promotion happened: it is where the parser's defaults become the
    request's values, so a surface that reuses it inherits the CLI's defaults BY
    CONSTRUCTION and a surface that constructs ``AuditRequest(...)`` itself inherits the
    model's instead. On ``coverage_scope`` those two answers differ, deliberately and by
    announcement (Story 10.3 / DN-8), which means the copy would assess a different
    population and could report a different verdict for an unchanged repository.
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
        f"{PROG}: security findings suppressed by your --ignore-path/--ignore-pattern "
        f"rules: {detail}. A live production key is never suppressed by either flag.",
        file=sys.stderr,
    )


def emit_egress_disclosure(message: str) -> None:
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

    PUBLIC since 2026-08-15 (Story 12.6) — see the ``__all__`` note above. A second
    invocation surface hands the pipeline THIS callable, not a lookalike: the egress
    consent channel and the sentence that discloses it stay single, which is Story 12.2's
    stated contract. It writes to ``sys.stderr`` at call time, so a caller that has
    rebound that stream (a stdio protocol adapter must) receives it on its own stream
    without this function knowing anything about that caller.
    """
    print(f"{PROG}: {message}", file=sys.stderr)


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
        f"{PROG}: {render_instrument_disclosure(INSTRUMENT_STATUS)}",
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
        _emit_audit_failure(exc)
        return _CRASH_EXIT_CODE
    except ValueError as exc:
        print(f"{PROG}: ship-readiness not rendered: {exc}", file=sys.stderr)
    return None


def _emit_audit_failure(exc: BaseException) -> None:
    """Print the ONE failure vocabulary: the typed cause, then FR37's next action.

    Story 12.8 / AC4 / DN-7. Three surfaces print an audit failure — this module's audit
    arm, this module's ship-readiness arm and the second invocation surface's — and 12.6 made it the
    contract that they say the SAME words, character for character, so the two surfaces
    cannot describe one failure differently. This is the function that makes that true of the
    failure path as well as of the success path, and it is why the second line comes from
    ``plain_english.render_audit_failed_next_action`` — the renderer Story 12.4 shipped for
    FR37 and which had zero production callers until now — rather than from a sentence
    written here.

    TWO lines, not one, and the split is deliberate: the first is the typed CAUSE (which
    since this story also carries the operator act that changes it, for the causes an
    operator CAN change), the second is the class-level next action, which is where the
    ``INTERNAL DEFECT`` token lands for a failure no repository change can clear. A CI log
    scraper keys on the token; a human reads the sentence.

    Secret-safe (NFR-S1): every string it prints is either a typed message the raising layer
    already made repository-relative, or a pure constant. It never touches ``str`` of an
    unexpected exception and never resolves a path.
    """
    print(f"{PROG}: audit failed: {exc}", file=sys.stderr)
    print(f"{PROG}: {render_audit_failed_next_action(cause=exc)}", file=sys.stderr)


def _emit_grammar_downgrade(reasons: tuple[str, ...]) -> None:
    """Say WHY files were downgraded by a grammar failure, on the DEFAULT run (Story 12.8/AC7).

    NFR-P3's second clause, ``DF-10-4-C``, and the handover Story 12.5 wrote by name:
    *"``render_grammar_downgrade_summary`` is the function 12.8 wires"*. Measured on
    ``2f84a0b`` that renderer had exactly ONE production caller —
    ``reports/generator.py``, inside the report path, which runs only when ``--report-dir``
    is set. So on the invocation almost everyone runs, a downgraded grammar was invisible:
    the operator saw a lower ratio and no reason, which reads as a judgement about their
    code rather than about the toolchain that could not read it.

    ONE renderer, TWO callers. The sentences are NOT copied here and the tokens are NOT
    re-classified by prefix at this call site — ``grammar_status.classify_reason`` did that
    once, in the pipeline, and that module's docstring records exactly what a second prefix
    guess costs (a silent skip, or telling someone to
    ``pip install tree-sitter-entrypoint_missing_go``).

    STDERR and silent when there is nothing to say: unlike the FR34 and suppression
    disclosures, this one describes a CONDITION rather than a policy, so "no grammar failed"
    is fully carried by the coverage numbers already printed above it.
    """
    for sentence in render_grammar_downgrade_summary(reasons):
        print(f"{PROG}: {sentence}", file=sys.stderr)


def _emit_selection_disclosures(
    args: argparse.Namespace, request: AuditRequest
) -> None:
    """Disclose the OPEN-vocabulary operator inputs that quietly did nothing (Story 12.8/AC3).

    DN-3 draws the line: a CLOSED, code-defined vocabulary (``--passes``, ``--skip-pass``,
    ``--reports``) is REFUSED inside ``parse_args``, because an unmatched token there is
    unambiguously a mistake. These two are OPEN and are DISCLOSED instead:

    * ``--reports`` with no ``--report-dir`` — legal and simply INERT. Refusing it would
      break a caller that sets the flag unconditionally and the directory conditionally;
    * ``--critical-subsystem`` / ``--exclude-critical`` — they take PATHS, so refusing one
      that matches nothing would break the legitimate case of designating a subtree absent
      from this partition. Measured, though, the silence is expensive: on ``2f84a0b``
      ``--critical-subsystem does/not/exist`` moved the verdict from ``RELEASE_READY``
      (exit 0) to ``INSUFFICIENT_COVERAGE`` (exit 3) and named nothing.

    The precedent is this project's own ``_emit_suppression_disclosure`` (Story 10.3 /
    AC4.3) and so is the register: STDERR, because stdout is the FR18/AR3 wire contract a CI
    step parses positionally.

    The existence probe is repository-root-relative and its RESULT is all that leaves this
    function — the disclosure echoes the operator's own argv spelling, never a resolved
    absolute path (NFR-S1).
    """
    if request.enabled_reports and not request.report_dir and args.reports:
        print(
            f"{PROG}: {render_inert_reports_disclosure(request.enabled_reports)}",
            file=sys.stderr,
        )

    root = Path(request.repo_path)
    for flag, designated in (
        ("--critical-subsystem", request.critical_paths),
        ("--exclude-critical", request.excluded_critical_paths),
    ):
        unmatched = tuple(
            path for path in designated if not _designation_matches(root, path)
        )
        if unmatched:
            print(
                f"{PROG}: {render_unmatched_designation_disclosure(flag, unmatched)}",
                file=sys.stderr,
            )


def _designation_matches(root: Path, designated: str) -> bool:
    """Does *designated* name anything in the audited tree? (Story 12.8 / AC3)

    All three accepted spellings count, because ``--exclude-critical``'s own contract
    paragraph accepts all three: an exact path, a directory prefix that clears a subtree,
    and a glob. ``Path.exists`` answers the first two (a directory prefix IS a directory)
    and ``Path.glob`` answers the third — and answers the first two as well, so the two
    probes are belt-and-braces rather than a partition.

    FAILS OPEN, deliberately: any error resolving the operator's own string (an absolute
    spelling, a ``..``, a pattern this host's ``glob`` rejects) returns ``True`` — "matched",
    hence NO disclosure. A disclosure engine that can itself fail would otherwise turn a
    resolution quirk into a false accusation about the operator's input, and a wrong
    disclosure is worse than none. Nothing here changes the audit; only whether a sentence
    is printed.
    """
    try:
        if (root / designated).exists():
            return True
        return any(root.glob(designated))
    except (OSError, ValueError, IndexError, NotImplementedError):
        return True


def _run_install_commands(args: argparse.Namespace) -> int:
    """Thin adapter for ``argus install-commands`` — resolve, print, map the exit code.

    Story 12.7 / FR35. EVERY decision this step makes is made in ``argus/commands/**``: the
    closed host registry, the pure asset x host fold, containment, the FR34 disclosure
    render and the report text. What is left here is the entry point's own job and only
    that — call the shell, print what it returns, and translate a typed failure into the
    AR3 wire contract (NFR-M1 — no business logic in the entry point).

    The failure arm is deliberately the SAME shape ``main`` already uses for the audit:
    every typed failure in ``argus/commands/**`` is a ``ValueError`` subclass, so it maps to
    one secret-safe stderr line and the reserved exit code ``1`` with no new vocabulary and
    no traceback (AR10/NFR-R1). Authoring new diagnosis prose is Story 12.8's fence.
    """
    from argus.commands.installer import install_commands, render_outcome

    try:
        outcome = install_commands(
            dest=args.dest,
            requested_hosts=tuple(args.host or ()),
            dry_run=args.dry_run,
            remove=args.remove,
        )
    except ValueError as exc:
        # ~~Authoring new diagnosis prose is Story 12.8's fence.~~ (§3.4 struck, not deleted
        # — 2026-08-15. That fence is now spent: the failure carries FR37's next action from
        # the SAME renderer the audit arm uses, so `install-commands` cannot describe a
        # typed failure differently from `audit` (DN-7). The cause line keeps its own
        # sub-command prefix, which is the only part that legitimately differs.)
        print(f"{PROG}: install-commands failed: {exc}", file=sys.stderr)
        print(f"{PROG}: {render_audit_failed_next_action(cause=exc)}", file=sys.stderr)
        return _CRASH_EXIT_CODE
    for line in render_outcome(outcome):
        print(line)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse argv → ``AuditRequest`` → pipeline → exit code (FR30/FR18/AR3).

    Returns the process exit code (testable without a real ``sys.exit``):
    ``AuditVerdict.exit_code`` (``0``/``2``/``3``) on a completed audit, or ``1``
    on a TYPED pipeline failure (with a secret-safe stderr line). NO business logic
    lives here — all audit logic is in ``pipeline.py`` + the reused modules.

    Since 2026-08-15 (Story 12.7) it dispatches on the sub-command. The dispatch sits ABOVE
    everything audit-specific and returns, so an ``audit`` invocation executes exactly the
    statements it executed before — same order, same calls, same bytes on both streams.

    Story 12.8 / AC8: a PARSER rejection is mapped here, and ONLY here (DN-5). See the module
    docstring — argparse's exit ``2`` was published by ``action.yml`` as a real verdict, so a
    typo produced an assessment for a run that never happened. ``build_parser().parse_args``
    is untouched, which is what keeps ``-28``, ``-35``..``-40``,
    ``tests/test_cli_flag_contract.py``, ``tests/invocation_sources.py`` and
    the second invocation surface — which deliberately catches the parser's ``SystemExit`` as a
    NON-verdict — working exactly as they did.
    """
    harden_output_streams()

    try:
        args = build_parser().parse_args(argv)
    except SystemExit as exc:
        if exc.code in (0, None):
            raise  # `--help` / `-h` succeeded and printed; exit 0, untouched.
        print(f"{PROG}: {render_usage_error_next_action()}", file=sys.stderr)
        return _CRASH_EXIT_CODE

    if args.command == "install-commands":
        return _run_install_commands(args)

    enabled_passes = resolve_passes(args)
    request = build_request(args, enabled_passes)

    # AUDIT + WIRE CONTRACT. A failure here means no verdict reached the consumer, so
    # exit `1` is the honest answer (AR10 / NFR-R1).
    try:
        # The egress disclosure sink is handed to the pipeline ONLY when the operator
        # opted in. A default run's call is therefore EXACTLY the call it was before
        # Story 12.2 — no new keyword, no new object — which is one fewer thing that
        # could differ on the path AC2.4 requires to be byte-identical. It also avoids
        # handing a callback to a run that structurally cannot use it.
        deep_kwargs = (
            {"disclose": emit_egress_disclosure}
            if deep_pass_enabled(enabled_passes)
            else {}
        )
        # `run_audit_detailed` rather than `run_audit` since 2026-08-15 (Story 12.8 / AC7 /
        # DN-4): the grammar-downgrade diagnosis rides on `AuditResult`, and `run_audit` is a
        # thin wrapper that returns `run_audit_detailed(...).verdict`, so the pipeline call
        # itself is byte-identical and nothing about the audit changed.
        result = run_audit_detailed(request, **deep_kwargs)  # type: ignore[arg-type]
        verdict = result.verdict
        print(
            summary_line(
                verdict.verdict.value,
                verdict.deep_ratio,
                verdict.blocking_finding_count,
                verdict.coverage_scope,
            )
        )
    except ValueError as exc:
        # TYPED and secret-safe (AR10). Which typed class it is decides the SECOND line —
        # an expected refusal names the act that clears it, an internal defect says plainly
        # that no such act exists and where to report it (`DF-8-4-D`; see the module
        # docstring). Never source, never an absolute host path, never a traceback.
        _emit_audit_failure(exc)
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
    # the first line an operator sees on stderr (pinned by tests/test_cli.py). Every
    # disclosure below is subject to that ordering rule for the same reason — the block
    # above states the verdict, and these state what shaped it.
    _emit_grammar_downgrade(result.grammar_downgrade_reasons)
    _emit_selection_disclosures(args, request)
    _emit_suppression_disclosure(verdict)
    _emit_instrument_disclosure()

    return verdict.exit_code


if __name__ == "__main__":  # pragma: no cover - process entrypoint
    sys.exit(main())
