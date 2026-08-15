"""PURE report generator for ArgusAgent end-user developer reports (AR8 / NFR-S1).

Reads the audit execution results (intake, verdict, ledger, findings) and renders
structured Markdown reports according to user-selected report choices (`enabled_reports`).
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from pathlib import Path

from argus.ledger.coverage_ledger import CoverageDepth, CoverageLedger
from argus.ledger.coverage_report import build_coverage_report, render_text as render_coverage_text
from argus.models import AuditRequest
from argus.reports.formatter import (
    format_locator_link,
    mask_secret,
    render_callout,
    render_markdown_table,
)
from argus.reports.plain_english import (
    render_depth_meaning,
    render_grammar_downgrade_summary,
    render_ship_readiness,
)
from argus.detectors.vacuous_test import partition_application_files

# The reason-token vocabulary is a PURE contract shared with the PRODUCER
# (``argus/index/ast_index.py``). Importing it here — rather than importing the impure
# ``index/`` layer for a constant, or re-parsing the token with a second ``startswith`` —
# is what keeps the remedy this report prints tied to the cause the index actually recorded
# (Story 10.4 / DN-3; the arrow stays impure-shell → pure-contract, AR8).
from argus.shared.grammar_status import (
    CORE_PACKAGE, INSPECT_CORE_VERSION_COMMAND, SUPPORTED_CORE_RANGE,
    GrammarFailure, classify_reason, grammar_package_for,
)
# The FR34 instrument-status disclosure is a PURE constant + renderer in the verdict
# layer, which this module already depends on. Reaching it from here rather than from each
# renderer is what lets ONE injection point cover all four artifacts (Story 11.1 / §C.2).
from argus.verdict.negative_assurance import (
    INSTRUMENT_STATUS,
    render_instrument_disclosure,
)
from argus.verdict.verdict_gate import (
    RELEASE_READY_DEEP_THRESHOLD,
    AuditVerdict,
    Verdict,
)

__all__ = [
    "generate_reports",
    "render_final_verdict_report",
    "render_security_review_report",
    "render_architecture_review_report",
]


_MAX_LISTED_CRITICAL_BLOCKERS = 20


# ── The finding-shape adapter (the ONE place a finding row is read) ───────────
#
# The pipeline hands these reports ``Recording.model_dump()`` rows. That shape has
# ``rule_id`` + a ``locators`` LIST — it has NO ``detector_id``, no top-level
# ``file_path``/``line_number`` and no ``snippet``. Reading those absent keys is not
# a cosmetic slip: ``render_security_review_report`` filtered on ``detector_id``,
# which no real row carries, so EVERY secret finding was dropped and the report
# affirmatively stated "no hardcoded credentials detected" on a repository where the
# scanner had just written a ``hardcoded_secret`` row to ``.argus/findings/``. A
# false negative on the exact claim this tool exists to make.
#
# The legacy FLAT shape is still accepted, because callers and fixtures construct it
# directly. Both shapes now go through these three readers, so a future divergence
# has one place to be fixed rather than four call sites to be kept in sync.


def _finding_rule_id(finding: dict[str, object]) -> str:
    """The rule/detector provenance id, from either finding shape."""
    return str(finding.get("rule_id") or finding.get("detector_id") or "")


def _finding_location(finding: dict[str, object]) -> tuple[str, int | None]:
    """The (file_path, line) of a finding, from either shape.

    Prefers the real ``locators[0]`` (FR13 guarantees at least one locator on a
    minted ``Recording``); falls back to the flat ``file_path``/``line_number``.
    """
    locators = finding.get("locators")
    if isinstance(locators, (list, tuple)) and locators:
        first = locators[0]
        if isinstance(first, dict):
            path = str(first.get("file_path", ""))
            start = first.get("start_line")
            return path, start if isinstance(start, int) and start > 0 else None
    path = str(finding.get("file_path", ""))
    raw_line = finding.get("line_number")
    line = (
        int(raw_line)
        if isinstance(raw_line, (int, str)) and str(raw_line).isdigit()
        else None
    )
    return path, line


def _finding_ast_span(finding: dict[str, object]) -> str:
    """The first locator's ``ast_span`` (the self-describing detail), or ``""``."""
    locators = finding.get("locators")
    if isinstance(locators, (list, tuple)) and locators:
        first = locators[0]
        if isinstance(first, dict):
            span = first.get("ast_span")
            if isinstance(span, str) and span:
                return span
    return ""


def _finding_masked_value(finding: dict[str, object]) -> str:
    """A display cell for the matched value that NEVER reconstructs a secret.

    A real ``Recording`` carries NO value at all: ``SecretScanDetector`` discards it
    in the same pure step that computes the mask (NFR-S2 — the field does not exist,
    which is the structural redaction guarantee). So the honest cell for a real row
    is a fixed mask plus a statement that the value was never retained — NOT a
    guess like "High Entropy Token", which implies the tool is holding something it
    deliberately threw away. A legacy row that DOES carry a snippet is masked.
    """
    snippet = finding.get("snippet") or finding.get("matched_string")
    if isinstance(snippet, str) and snippet:
        return mask_secret(snippet)
    return "**** (value discarded at detection — NFR-S2)"


def _render_test_dilution_hint(
    verdict: AuditVerdict, ledger: CoverageLedger, ast_index: object | None = None
) -> list[str]:
    """Explain a COVERAGE outcome that is an artifact of test-file dilution, if it is one.

    A test file is graded ``audited_shallow`` BY CONSTRUCTION — it is the subject of
    the vacuous-test pass, not a target of deep grounding. In a repository with more
    test files than application files those entries dominate the denominator, and the
    repository is denied ``RELEASE_READY`` for being well-tested.

    ``--coverage-scope application`` fixes that, but it is opt-in (the default stays
    whole-repository so persisted evidence and existing CI gates keep their meaning).
    Opt-in only helps an operator who knows the flag exists — so when the coverage
    gate is the thing withholding the verdict AND narrowing would clear it, the report
    says so here rather than leaving them to discover it.

    Called from the two ``INSUFFICIENT_COVERAGE`` arms of
    :func:`render_final_verdict_report` ONLY — FR16 row 1 and row 4. It is deliberately
    NOT called for row 2: the amended decision table short-circuits at the findings row,
    so coverage was never evaluated and "this coverage result is driven by test-file
    dilution" would describe a result that coverage did not drive (Story 8.3 / AC6).
    That call-site restriction is why this function carries no ``RELEASE_READY`` guard
    and no ``blocking_finding_count`` clause: both became unreachable with the split,
    and DR-11's rule is to remove an unreachable branch rather than leave it as untested
    dead code.

    Deliberately does NOT promise ``RELEASE_READY``: it reports only that the COVERAGE
    gate would be satisfied, because the critical-subsystem clause is unaffected by
    scope. Over-promising here would be the same class of dishonesty as the false block
    message this work replaced.

    *ast_index* is the pre-built 1.4 index when the caller has one (the pipeline does).
    It disambiguates an ambiguously-named ``*_test.py`` module BY CONTENT, exactly as
    ``pipeline._assessment_scope_paths`` does when it narrows the assessed population —
    without it the report's APPLICATION denominator and the verdict's assessed
    population can disagree inside a single run. ``None`` (the unit-test callers) keeps
    the previous name-only behaviour byte-for-byte.
    """
    if verdict.coverage_scope is not None:
        return []  # already narrowed — nothing to suggest
    if verdict.deep_ratio >= RELEASE_READY_DEEP_THRESHOLD:
        return []  # coverage is not what withheld the verdict

    # ONE application/test derivation for the whole run (§3.3 / AR7): literally the same
    # function the pipeline's scope narrowing calls, fed from the same index. Story 12.1
    # closed `DF-8-3-C` here — the predicate was already shared, but this plumbing around it
    # was a verbatim second copy, and the report's APPLICATION denominator and the verdict's
    # assessed population must not be able to drift apart.
    application, held_out = partition_application_files(ledger.entries, ast_index)
    if not application or held_out == 0:
        return []

    app_deep = sum(1 for e in application if e.depth is CoverageDepth.AUDITED_DEEP)
    app_ratio = Fraction(app_deep, len(application))
    if app_ratio < RELEASE_READY_DEEP_THRESHOLD:
        return []  # narrowing would not clear the gate — do not suggest it

    # The critical-subsystem clause is the ONE gate narrowing cannot clear. It WITHHOLDS
    # `RELEASE_READY` (row 4) rather than blocking — saying "block" here would repeat,
    # in miniature, the false accusation this story removes from the callout above.
    caveat = (
        " Note that the critical-subsystem clause would still withhold `RELEASE_READY`."
        if not verdict.critical_subsystems_all_deep
        else " No other gate is currently unmet."
    )

    return [
        render_callout(
            "NOTE",
            f"This coverage result is driven by test-file dilution. "
            f"{app_deep}/{len(application)} (`{app_ratio}`) of APPLICATION files are "
            f"audited deep — above the `{RELEASE_READY_DEEP_THRESHOLD}` threshold — but "
            f"{held_out} test file(s), graded shallow by construction, are counted in the "
            f"whole-repository denominator. Re-run with `--coverage-scope application` to "
            f"assess application files only; the narrowing is disclosed in the verdict and "
            f"does not lower the coverage floor.{caveat}"
        ),
        "",
    ]


#: The lead sentence for FR16 row 4, where the unmet critical clause IS the cause of
#: the verdict (jointly with, or instead of, the coverage threshold).
_CRITICAL_LEAD_CAUSAL = "These withheld `RELEASE_READY` (FR16)."

#: The lead for every OTHER row. Rows 1 and 2 fire before the critical clause is ever
#: evaluated, so it caused nothing there and may not be presented as a reason (AC6 /
#: D3) — but the work list still belongs in the document, because the ship-readiness
#: block counts these files and points here for their names.
_CRITICAL_LEAD_NOT_THE_CAUSE = (
    "Not the reason for this verdict — that is stated in the callout above. Listed "
    "because the clause is still unmet and will withhold `RELEASE_READY` once the "
    "stated reason is resolved."
)

#: The row-independent half of the section's prose (AC7). Every row below the heading
#: is a REAL work item because FR4/DR-5 already removed the ungradable ones, and the
#: single exception — a DR-6 operator designation — is stated rather than left to be
#: discovered. Contains no ``_FALSE_POSITIVE_CLAIMS`` substring
#: (``TC-ArgusAgent-PIPELINE-002-07``).
_CRITICAL_LIST_GUIDANCE = (
    "A file Argus can never grade `audited_deep` — a test file, or a clean-parsed "
    "module with zero definitions — is already dropped from the heuristic critical set "
    "automatically (FR4/DR-5), so every row below is a real work item: bring it to "
    "`audited_deep`, or remove it with `--exclude-critical` if it is not genuinely "
    "critical. The one exception is a path you designated yourself with "
    "`--critical-subsystem`: an explicit designation is exempt from that automatic "
    "removal (DR-6), so it can be listed here even when Argus has no way to grade it "
    "deeply."
)


def _render_critical_blockers(
    verdict: AuditVerdict, ledger: CoverageLedger, *, lead: str
) -> list[str]:
    """Render the critical paths below ``audited_deep``, with their actual depth.

    "At least one critical subsystem is not audited deep" tells an operator that a gate
    is unmet but not by what, so there is no next action. Naming each file and the
    depth it actually reached turns the gate into a work list.

    Rendered on EVERY row that has a non-empty set, not only the row the clause caused
    (Story 8.3 review finding R1). ``render_ship_readiness`` counts these files on the
    other human surface and says "see the final-verdict report for the named critical
    files" — so omitting the section on rows 1 and 2 left one surface of a single run
    pointing at a work list the other surface did not contain, which is the
    cross-surface contradiction DR-11 exists to delete. *lead* is supplied by the
    calling arm and is the ONLY row-dependent sentence: causal on row 4, explicitly
    non-causal elsewhere, because appending it as a REASON on rows 1 and 2 would be the
    false causal claim AC6 removed from the reason list.

    The list is TRUNCATED at :data:`_MAX_LISTED_CRITICAL_BLOCKERS` with an explicit
    "and N more" line — never a silent cut, because a report that quietly drops rows
    is exactly the kind of thing this tool exists to catch.
    """
    blockers = verdict.critical_subsystems_not_deep
    if not blockers:
        return []

    depth_by_path = {entry.file_path: entry.depth.value for entry in ledger.entries}
    lines = [
        f"### Critical subsystems below `audited_deep` ({len(blockers)})",
        "",
        lead,
        "",
        # ONE Markdown paragraph, emitted as ONE line. The guidance used to be
        # hard-wrapped across list items, which meant every asserted phrase in it
        # straddled a newline and any re-wrap silently broke a pin for a reason that
        # had nothing to do with the words.
        _CRITICAL_LIST_GUIDANCE,
        "",
        "| File | Depth reached |",
        "|---|---|",
    ]
    for path in blockers[:_MAX_LISTED_CRITICAL_BLOCKERS]:
        # A designated-critical path absent from the ledger was never examined at all.
        depth = depth_by_path.get(path, "not in ledger (never examined)")
        lines.append(f"| `{path}` | `{depth}` |")
    remaining = len(blockers) - _MAX_LISTED_CRITICAL_BLOCKERS
    if remaining > 0:
        lines.append(f"| … and {remaining} more | |")
    lines.append("")

    crit_set = getattr(verdict, "critical_subsystems", None)
    if crit_set is not None and getattr(crit_set, "heuristic_excluded_ineligible", None):
        ineligible = crit_set.heuristic_excluded_ineligible
        if ineligible:
            ineligible_paths = ", ".join(f"`{p}`" for p in sorted(ineligible.keys())[:5])
            lines.append(
                f"> **Vacuous Critical Subsystem Exclusion (DF-8-3-A)**: "
                f"{len(ineligible)} critical path(s) heuristically excluded as ungradable by construction "
                f"(test files or 0-definition modules): {ineligible_paths}"
                f"{' ...' if len(ineligible) > 5 else ''}."
            )
            lines.append("")

    return lines



def _render_grammar_remedy(failure: GrammarFailure, counts: Counter[str]) -> str:
    """One line per failure CLASS, carrying the remedy that class actually needs.

    Never a blended sentence. A polyglot repository can hit several of these at once, and a
    merged ``pip install`` line is wrong for at least one of them by construction: cause 1's
    package is absent, cause 3's is present and broken, and cause 2's is present and fine —
    Argus is the one at fault.
    """
    languages = sorted(counts)
    files = sum(counts.values())
    where = ", ".join(f"{counts[lang]} {lang}" for lang in languages)
    packages = " ".join(grammar_package_for(lang) for lang in languages)

    if failure is GrammarFailure.PACKAGE_MISSING:
        return (
            f"- **Grammar package not installed** ({where}): run "
            f"`pip install {packages}` and re-run."
        )
    if failure is GrammarFailure.ENTRY_POINT_MISSING:
        return (
            f"- **Argus does not recognise this grammar package's entry point** ({where}): the "
            f"package IS installed, so there is nothing for you to install — this is an **Argus** "
            f"defect. Please report it with the installed version of `{packages}`."
        )
    if failure is GrammarFailure.LOAD_FAILED:
        return (
            f"- **The installed grammar could not be loaded on this runtime** ({where}): "
            f"reinstall or rebuild `{packages}` and check that its version pairs with the "
            f"installed `{CORE_PACKAGE}` (an ABI mismatch or a corrupt build looks like this)."
        )
    if failure is GrammarFailure.CORE_RUNTIME_MISSING:
        # Deliberately not per-language: EVERY language is down, so naming one grammar package
        # here would be the maximally wrong remedy. It is why this token carries no `<lang>` suffix.
        return (
            f"- **The `{CORE_PACKAGE}` core runtime is not importable** ({files} file(s)): run "
            f"`pip install {CORE_PACKAGE}` and re-run. **Every** language is affected by this — it is "
            f"not a per-language problem, so installing individual grammar packages will not help."
        )
    if failure is GrammarFailure.RUNTIME_UNVALIDATED:
        # Also not per-language, and for a sharper reason than cause 4's: the parser CONSTRUCTED
        # fine, so there is nothing visibly broken to reinstall. No observed version, exception
        # message or host path is rendered (NFR-S1 / 10.4 DN-5) — the operator is given the range
        # and the command to read their own environment; a richer diagnostic is Story 12.8's.
        return (
            f"- **The installed parsing toolchain did not pass Argus's self-check** ({files} file(s)): "
            f"Argus withholds a verdict rather than compute one on a toolchain it has not validated. "
            f"Install a supported `{CORE_PACKAGE}` (`{SUPPORTED_CORE_RANGE}`) and re-run; check what "
            f"you have with `{INSPECT_CORE_VERSION_COMMAND}`. **Every** language is affected — "
            f"installing individual grammar packages will not help."
        )
    # DF-10-4-E (closed by Story 11.4). This was an unconditional fallthrough, so a fifth cause
    # would have silently rendered the fourth's remedy — reintroducing, inside 10.4's own fix, the
    # exact "named reason whose remedy cannot work" defect 10.4 existed to close. An unregistered
    # member is now LOUD at the one surface an operator reads, not plausible-looking prose.
    raise ValueError(
        f"no operator remedy is registered for GrammarFailure.{failure.name}. Every registered "
        "cause must render ITS OWN remedy: falling through to another cause's would tell the "
        "operator to run a command that cannot help them (argus/shared/grammar_status.py)."
    )


def _render_readability_warning(
    ledger: CoverageLedger, ast_index: object | None
) -> list[str]:
    """Warn when Argus could not READ what it enumerated — loudly, and with a remedy that works.

    A repository whose language has no usable tree-sitter grammar produces a perfectly
    ordinary-looking ``INSUFFICIENT_COVERAGE``. Technically true, and badly misleading: it
    reads as "your repo needs more tests" when the actual meaning is "I could not parse a
    single file". This is the ``no silent no-op`` rule — an audit that examined nothing must
    say so in the loudest register the report has, never imply a coverage judgement it did
    not make.

    **This is the ONLY place the reason token reaches an operator** (measured, whole-tree:
    ``DetectorResult.degraded`` records it and no production code reads it back — filed as
    ``DF-10-4-B`` for Story 10.5's reverse sweep). It also had never executed under test,
    which is why Story 10.4 wrote ``tests/test_grammar_diagnosis.py`` ``…-26``/``-27`` RED
    before touching it: splitting the reason token without covering this function would have
    silently disabled the one message an operator ever sees, and nothing would have gone red.

    Classification goes through ``argus.shared.grammar_status.classify_reason``, never through
    prefix arithmetic. The removed version sliced the language out of the token with
    ``reason[len(prefix):]`` against cause 1's prefix, which skips
    ``grammar_entrypoint_missing_go`` outright (SILENT); widening that prefix to ``grammar_``
    would have sliced the same token into the "language" ``entrypoint_missing_go`` and printed
    ``pip install tree-sitter-entrypoint_missing_go`` (MISDIRECT). One shared definition,
    imported by producer and consumer alike, is the only shape that cannot drift.

    ⛔ The all-or-nothing trigger below (``if eligible: return []``) is Story 12.5's, not this
    function's: a polyglot repository whose Python parses still learns nothing here about its
    failed Go grammar. That blind spot is measured and FILED (``DF-10-4-A``), not fixed —
    widening the trigger adds a per-file point-of-downgrade surface 12.5 owns by name.
    """
    if ast_index is None:
        return []
    entries = getattr(ast_index, "entries", ()) or ()
    if not entries:
        return []

    eligible = sum(1 for e in entries if getattr(e, "ast_eligible", False))
    if eligible:
        return []  # something was parseable — this is a real coverage result

    # Failure class → language → file count. Deterministic ordering (AR4): classes in
    # declaration order, languages sorted inside each.
    by_class: dict[GrammarFailure, Counter[str]] = {}
    for entry in entries:
        diagnosis = classify_reason(getattr(entry, "parse_failure_reason", None))
        if diagnosis is None:
            continue  # syntax_error / read_error / non_python — not a grammar-LOAD failure
        by_class.setdefault(diagnosis.failure, Counter())[diagnosis.language or ""] += 1

    if not by_class:
        return []

    remedies = [
        _render_grammar_remedy(failure, by_class[failure])
        for failure in GrammarFailure
        if failure in by_class
    ]
    return [
        render_callout(
            "CAUTION",
            f"**No file could be parsed — this verdict reflects tooling, not code quality.** "
            f"Argus enumerated {len(entries)} file(s) and ZERO reached `audited_deep`, so the "
            f"coverage numbers below are a floor imposed by grammar loading rather than a "
            f"judgement about this code. What failed, and what fixes each one:\n\n"
            + "\n".join(remedies)
        ),
        "",
    ]


#: How many downgraded files the point-of-downgrade table names before it summarises the
#: rest. Same shape and reason as ``_MAX_LISTED_CRITICAL_BLOCKERS``: a work list nobody can
#: read is not a work list, and the remaining count is stated rather than dropped.
_MAX_LISTED_GRAMMAR_DOWNGRADES = 20


def _render_grammar_downgrade_section(
    ledger: CoverageLedger, ast_index: object | None
) -> list[str]:
    """Name the files a grammar failure downgraded, AT THE POINT OF DOWNGRADE (Story 12.5).

    NFR-P3's second clause: *where a language grammar is uninstalled or downgraded, its
    absence and the reason are stated in the tool's own output at the point the file is
    downgraded*. Closes ``DF-10-4-A``, measured and filed by Story 10.4 and handed here by
    name: ``_render_readability_warning`` returns early on ``if eligible: return []``, so a
    polyglot repository whose Python parses was told NOTHING about its failed Go grammar —
    it saw only a coverage ratio, which reads as a judgement about the code.

    ⛔ A SEPARATE surface, not a widening of 10.4's trigger, and the distinction is the whole
    design. The two answer different questions: 10.4's says *"no file could be parsed, so
    this verdict reflects tooling and not code quality"* — a sentence that is FALSE for a
    partially-parsed repository — while this one says *"these specific files were downgraded,
    this is the package that would have grounded them, and this is the command"*. Rendering
    both for a total failure would state one set of remedies twice in two registers, so this
    one stands down when nothing parsed (``TC-ArgusAgent-REPORT-002-36`` pins both halves).

    The per-class prose is ``plain_english.render_grammar_downgrade_summary`` — REUSED, not
    re-authored. The two human surfaces of one run naming different packages for the same
    failure is precisely the drift ``argus/shared/grammar_status.py`` exists to prevent, and
    a second copy of the wording is how that starts. What this function adds is the half a
    sentence cannot carry: WHICH files, and what depth they actually reached.
    """
    if ast_index is None:
        return []
    entries = getattr(ast_index, "entries", ()) or ()
    if not entries:
        return []
    if not any(getattr(entry, "ast_eligible", False) for entry in entries):
        return []  # nothing parsed — 10.4's callout owns this run, in a louder register

    downgraded: list[tuple[str, str]] = []  # (file_path, missing package)
    reasons: list[str | None] = []
    for entry in entries:
        reason = getattr(entry, "parse_failure_reason", None)
        diagnosis = classify_reason(reason)
        if diagnosis is None:
            continue  # syntax_error / read_error / non_python — not a grammar-LOAD failure
        reasons.append(reason)
        package = (
            grammar_package_for(diagnosis.language)
            if diagnosis.language
            else CORE_PACKAGE  # the runtime-scoped causes are not about one language
        )
        downgraded.append((str(getattr(entry, "file_path", "")), package))
    if not downgraded:
        return []

    depth_by_path = {entry.file_path: entry.depth.value for entry in ledger.entries}
    downgraded.sort()  # deterministic (AR4), and stable against index iteration order

    lines: list[str] = [
        render_callout(
            "WARNING",
            f"**{len(downgraded)} file(s) were downgraded because a language grammar was not "
            f"usable — not because of anything in the code.** The rest of this report's "
            f"coverage numbers count them at the depth below, so this is a floor imposed by "
            f"grammar loading. What failed, and what fixes each one:\n\n"
            + "\n".join(
                f"- {sentence}"
                for sentence in render_grammar_downgrade_summary(reasons)
            )
        ),
        "",
        "### Files downgraded by a grammar failure",
        "",
        "| File | Depth reached | Grammar package |",
        "|---|---|---|",
    ]
    for path, package in downgraded[:_MAX_LISTED_GRAMMAR_DOWNGRADES]:
        # A file the index examined but the ledger never graded is stated as such rather
        # than given a plausible default — the `_render_critical_blockers` precedent.
        depth = depth_by_path.get(path, "not in ledger (never graded)")
        lines.append(f"| `{path}` | `{depth}` | `{package}` |")
    remaining = len(downgraded) - _MAX_LISTED_GRAMMAR_DOWNGRADES
    if remaining > 0:
        lines.append(f"| … and {remaining} more | | |")
    lines.append("")
    return lines


def _render_source_state(request: AuditRequest, source_state: object | None) -> list[str]:
    """Render WHAT was audited and whether anyone else can reconstruct it.

    Argus no longer refuses to run on a dirty tree or a repository without git —
    refusing produced no audit, which helps nobody. The rigour moved here instead:
    the report states which source state was audited, and a non-``commit`` state is
    labelled NOT third-party reproducible rather than being quietly presented as if
    it were a pinned commit.
    """
    if source_state is None:  # pre-source-state callers (and unit tests)
        return [f"- **Commit Pinned**: `{request.commit}`"]

    kind = getattr(source_state, "kind", "commit")
    identity = getattr(source_state, "identity", request.commit)
    reproducible = getattr(source_state, "reproducible", True)

    label = {
        "commit": "Commit (pinned, clean tree)",
        "worktree": "Working tree (uncommitted changes present)",
        "directory": "Directory (no git metadata)",
    }.get(kind, kind)

    lines = [
        f"- **Source State**: `{kind}` — {label}",
        f"- **Identity**: `{identity}`",
    ]
    if not reproducible:
        lines.append(
            "- **Reproducible by a third party**: **No** — the identity pins the exact "
            "bytes audited, but they cannot be retrieved from a ref. Use `--strict` for "
            "commit-pinned evidence."
        )
    excluded = getattr(source_state, "excluded_by_reason", None) or {}
    total_excluded = sum(excluded.values())
    if total_excluded:
        # Never a silent exclusion: an audit that quietly skipped 2,000 files while
        # reporting a coverage ratio is exactly the misrepresentation this tool exists
        # to catch, so the magnitude and the reasons are stated up front.
        breakdown = ", ".join(f"{n} {reason}" for reason, n in sorted(excluded.items()) if n)
        lines.append(
            f"- **Excluded from audit**: {total_excluded} file(s) — {breakdown}"
        )
    return lines


def render_final_verdict_report(
    request: AuditRequest,
    verdict: AuditVerdict,
    ledger: CoverageLedger,
    total_findings_count: int,
    *,
    source_state: object | None = None,
    ast_index: object | None = None,
) -> str:
    """Render the `final-verdict.md` end-user summary report."""
    lines: list[str] = []
    lines.append("# ⚖️ Argus Final Audit Verdict Report")
    lines.append("")
    readability = _render_readability_warning(ledger, ast_index)
    lines.extend(readability)
    # NFR-P3 / Story 12.5 — the point-of-downgrade disclosure, above the coverage numbers it
    # explains. Mutually exclusive with the callout above by construction (see the function),
    # so at most one of the two ever renders for a given run.
    lines.extend(_render_grammar_downgrade_section(ledger, ast_index))
    # The human register FIRST (the brief's dual-register output). A reader who opens
    # this report should learn whether they can ship, and why not, before meeting a
    # single enum token or fraction. The machine-grade fields follow immediately below
    # and are unchanged — this adds a way in, it does not replace the record.
    lines.append("> " + render_ship_readiness(verdict)[0])
    lines.append("")
    lines.extend(_render_source_state(request, source_state))
    lines.append(f"- **Final Verdict**: **`{verdict.verdict.value}`** (Exit Code `{verdict.exit_code}`)")
    scope = verdict.coverage_scope
    if scope is None:
        lines.append(f"- **Deep Coverage Ratio**: **`{verdict.deep_ratio}`** ({verdict.deep_count}/{verdict.total_count} files)")
    else:
        # Report BOTH numbers whenever the assessment was narrowed. The assessed ratio
        # is what the gate decided on; the whole-repository ratio stays visible so a
        # scoped verdict can never be mistaken for a repository-wide claim.
        lines.append(
            f"- **Deep Coverage Ratio (assessed scope)**: **`{scope.assessed_deep_ratio}`** "
            f"({scope.assessed_deep_count}/{scope.assessed_total_count} files)"
        )
        lines.append(
            f"- **Deep Coverage Ratio (whole repository)**: `{verdict.deep_ratio}` "
            f"({verdict.deep_count}/{verdict.total_count} files)"
        )
        lines.append(
            f"- **Assessment Scope**: `{scope.scope_id}` — {scope.excluded_count} "
            f"file(s) held out ({scope.excluded_reason})"
        )
    lines.append(f"- **Blocking Findings**: **{verdict.blocking_finding_count}**")
    lines.append(f"- **Total Findings Emitted**: **{total_findings_count}**")
    lines.append("")
    # Qualify the ratio the reader just read, immediately and in the same eyeline.
    # `audited_deep` is defined by the PRD as an AST-validated claim citing specific
    # symbols; with no LLM-backed deep pass enabled it attests something narrower and
    # honest. Printing the bare grade lets the label promise more than the pass
    # delivered — the precise over-claim this tool exists to catch in other people's
    # repositories, so it is not one it may make about itself.
    # Story 12.2: keyed on the deep pass's OUTCOME, carried on the verdict, so the
    # report and the CLI's human register cannot state different things about the same
    # run. `None` on every run that did not opt in — which is every default run.
    lines.append(
        render_callout(
            "NOTE",
            render_depth_meaning(request.enabled_passes, deep_pass=verdict.deep_pass),
        )
    )
    lines.append("")

    # ── The four arms below are EXACTLY the four FR16 rows, in the table's own order
    # of precedence. One arm per row is what stops this surface from describing a run
    # in another row's words — the DF-8-1-A defect, where row 4 was rendered with row
    # 2's sentence six lines under its own non-blocking verdict token.
    #
    # The critical-subsystem WORK LIST is not part of that split: it is rendered once,
    # below the chain, for every row that has one. Only its lead sentence is
    # row-dependent, and row 4 is the only row entitled to a causal one.
    critical_lead = _CRITICAL_LEAD_NOT_THE_CAUSE
    if verdict.verdict is Verdict.RELEASE_READY:  # row 3
        lines.append(render_callout("TIP", "Repository satisfies all deterministic release readiness criteria. Zero blocking findings emitted."))
    elif verdict.is_below_floor:  # row 1 — the FLOOR, the single source of truth (§3.3)
        # Since the amendment (Story 8.1) INSUFFICIENT_COVERAGE is also row 4 — a run
        # ABOVE the floor that found nothing and missed a coverage or critical-subsystem
        # gate — and that run needs the gate-naming + critical-blocker sections below,
        # not a below-floor warning it would contradict. Branching on the verdict enum
        # here silently dropped both sections for every row-4 run.
        lines.append(render_callout("WARNING", "Repository deep coverage ratio is below the required floor. Additional definitions or tests required."))
        lines.append("")
        # Dilution can push a repo under the FLOOR too, not just under the threshold.
        lines.extend(_render_test_dilution_hint(verdict, ledger, ast_index))
    elif verdict.blocking_finding_count > 0:  # row 2 — the ONLY blocking outcome
        # The finding is the whole reason, and the only one this row is entitled to
        # give. FR16's table is evaluated IN ORDER and short-circuits here: rows 3 and
        # 4 were never reached, so the coverage threshold and the critical-subsystem
        # clause were never evaluated and are not causes of anything. Appending them
        # (as this arm did before Story 8.3, alongside a "this coverage result is
        # driven by test-file dilution" note) is a false causal claim — the mirror
        # image of DF-8-1-A, which described a coverage outcome as a defect.
        lines.append(
            render_callout(
                "CAUTION",
                f"Repository is NOT ready for release — "
                f"{verdict.blocking_finding_count} verdict-blocking finding(s).",
            )
        )
    else:  # row 4 — nothing blocking found, a gate unmet
        # NOT a block, and it may not read as one. The verdict is INSUFFICIENT_COVERAGE
        # with zero findings; asserting the repository is not ready for release here is
        # a defect claim the audit never made (DF-8-1-A). The register matches
        # `negative_assurance._assurance_statement`'s already-landed row-4 sentence, so
        # the two artifacts of one run describe it the same way.
        critical_lead = _CRITICAL_LEAD_CAUSAL
        assessed_ratio = scope.assessed_deep_ratio if scope is not None else verdict.deep_ratio
        reasons: list[str] = []
        if assessed_ratio < RELEASE_READY_DEEP_THRESHOLD:
            reasons.append(
                f"deep coverage `{assessed_ratio}` is below the "
                f"`{RELEASE_READY_DEEP_THRESHOLD}` release threshold"
            )
        if not verdict.critical_subsystems_all_deep:
            reasons.append(
                "at least one critical subsystem is not audited deep (FR16)"
            )
        # No "a release gate was not satisfied" fallback: row 4 fires BECAUSE at least
        # one of those two gates is unmet (it is the negation of row 3's conjunction
        # over the same assessed ratio the gate used), so `reasons` cannot be empty. The
        # old fallback became unreachable the moment row 2 got its own arm, and DR-11's
        # rule is to delete an unreachable branch rather than keep it as untested code.
        detail = "; ".join(reasons)
        lines.append(
            render_callout(
                "WARNING",
                f"Release readiness is NOT VOUCHED — Argus found nothing blocking, but "
                f"{detail}. This is a statement about the audit, not about the code.",
            )
        )
        lines.append("")
        lines.extend(_render_test_dilution_hint(verdict, ledger, ast_index))

    critical_blockers = _render_critical_blockers(verdict, ledger, lead=critical_lead)
    if critical_blockers:
        if lines[-1] != "":
            lines.append("")  # a Markdown heading needs a blank line above it
        lines.extend(critical_blockers)

    lines.append("")
    default_scope_statement = "Scope: Whole repository audit at pinned commit."
    if scope is not None:
        # The negative-assurance statement must name the narrowing. A scoped verdict
        # asserts nothing about the held-out files, and says so here.
        default_scope_statement = (
            f"Scope: '{scope.scope_id}' assessment at pinned commit — "
            f"{scope.assessed_total_count} file(s) assessed, {scope.excluded_count} held out "
            f"({scope.excluded_reason}). The coverage floor was applied WITHIN this scope. "
            f"No coverage claim is made about the held-out files; blocking findings and "
            f"critical-subsystem checks remain in force across the whole repository."
        )
    scope_statement = getattr(verdict, "scope_statement", default_scope_statement)
    disclaimer = getattr(verdict, "disclaimer", "Negative Assurance Disclaimer: Deterministic assurance scan completed under configured rules.")

    lines.append("## Negative Assurance & Scope Disclaimer")
    lines.append("")
    lines.append(f"> {scope_statement}")
    lines.append("")
    lines.append(f"> {disclaimer}")
    lines.append("")
    return "\n".join(lines)



def render_security_review_report(
    request: AuditRequest,
    findings: list[dict[str, object]],
) -> str:
    """Render the `security-review.md` end-user security report."""
    secret_findings = [
        f for f in findings
        if _finding_rule_id(f) in ("secret_scan", "hardcoded_secret")
    ]

    lines: list[str] = []
    lines.append("# 🛡️ Security Review Report")
    lines.append("")
    lines.append(f"- **Secret Scan Status**: {'COMPLETED' if 'security' in request.enabled_passes else 'SKIPPED (Pass Deselected)'}")
    lines.append(f"- **Total Security Findings**: **{len(secret_findings)}**")
    lines.append("")

    if not secret_findings:
        lines.append(render_callout("NOTE", "No high-entropy secrets or hardcoded credentials detected in audited source files."))
        lines.append("")
        return "\n".join(lines)

    lines.append("## Detected Secret Indicators")
    lines.append("")
    
    headers = ["Rule ID", "Location", "Masked Pattern / Context", "Severity"]
    rows: list[list[str]] = []
    for f in secret_findings[:100]:  # Cap table view at 100 entries for readability
        rule_id = _finding_rule_id(f) or "hardcoded_secret"
        file_path, line_no_int = _finding_location(f)
        locator = format_locator_link(file_path, line_no_int)
        masked_snippet = _finding_masked_value(f)
        severity = "BLOCKING" if f.get("depth_supported") is not None else "Advisory"

        rows.append([f"`{rule_id}`", locator, f"`{masked_snippet}`", severity])

    lines.append(render_markdown_table(headers, rows))
    if len(secret_findings) > 100:
        lines.append("")
        lines.append(f"*Note: Showing first 100 of {len(secret_findings)} secret findings. Full log stored in evidence bundle.*")
    lines.append("")
    lines.append("### Recommended Remediation:")
    lines.append("1. **Secrets**: Revoke any active exposed credentials and transition to environment variables or secret managers.")
    lines.append("2. **False Positives**: Use inline annotations `# argus:ignore secret_scan` or add file paths to `ignore_paths` in audit request.")
    lines.append("")
    return "\n".join(lines)


def render_architecture_review_report(
    request: AuditRequest,
    findings: list[dict[str, object]],
) -> str:
    """Render the `architecture-review.md` end-user architecture & modularity report."""
    arch_findings = [
        f for f in findings
        if _finding_rule_id(f) in ("orphan_code", "cross_partition")
    ]

    lines: list[str] = []
    lines.append("# Architecture & Modularity Review Report")
    lines.append("")
    lines.append(f"- **Cross-Partition Analysis**: {'COMPLETED' if 'prosecutor' in request.enabled_passes else 'SKIPPED'}")
    lines.append(f"- **Orphan Code Analysis**: {'COMPLETED' if 'orphan' in request.enabled_passes else 'SKIPPED'}")
    lines.append(f"- **Architecture Findings Count**: **{len(arch_findings)}**")
    lines.append("")

    if not arch_findings:
        lines.append(render_callout("NOTE", "No cross-partition boundary leaks or unreferenced orphan symbols detected."))
        lines.append("")
        return "\n".join(lines)

    headers = ["Finding Class", "Location", "Details"]
    rows: list[list[str]] = []
    for f in arch_findings[:100]:
        rule_id = _finding_rule_id(f) or "architecture_finding"
        file_path, line_no_int = _finding_location(f)
        locator = format_locator_link(file_path, line_no_int)
        # A real Recording carries no free-text `message`; its self-describing detail
        # is the locator's `ast_span` (the orphaned symbol, or the cross-partition
        # seam descriptor). Fall back to the legacy `message`, then to a fixed label.
        details = str(f.get("message") or _finding_ast_span(f) or "Architectural boundary/reference finding")
        rows.append([f"`{rule_id}`", locator, details])

    lines.append(render_markdown_table(headers, rows))
    lines.append("")
    return "\n".join(lines)


def _with_instrument_disclosure(content: str) -> str:
    """Append the FR34 instrument-status disclosure to a report artifact (PURE).

    Every report is a verdict surface, and FR34 permits none without the disclosure. This
    is the SINGLE injection point: ``generate_reports`` routes all four ``write_text``
    calls through it, and ``tests/test_instrument_disclosure.py`` parses that function's
    own body to require it, so a FIFTH report added without this helper turns the guard
    red rather than shipping undisclosed.

    Injecting at the WRITE rather than in each renderer is what keeps ``coverage-ledger.md``
    covered without an ``argus/ledger/**`` edit: that artifact is rendered by
    ``argus/ledger/coverage_report.py``, and reaching the constant from there would invert
    the layering (``generator.py`` already imports FROM ``coverage_report``).

    PURE (AR8) and deterministic (NFR-P1): a constant appended to a string — no clock, no
    run id, no host path, so the artifacts stay byte-identical for identical inputs.
    """
    return (
        f"{content.rstrip()}\n\n---\n\n"
        f"## Instrument status (FR34)\n\n"
        f"{render_instrument_disclosure(INSTRUMENT_STATUS)}\n"
    )


def generate_reports(
    request: AuditRequest,
    verdict: AuditVerdict,
    ledger: CoverageLedger,
    findings: list[dict[str, object]],
    output_dir: str | Path,
    *,
    source_state: object | None = None,
    ast_index: object | None = None,
) -> dict[str, Path]:
    """Generate requested Markdown end-user reports and write to *output_dir*.

    Returns a dict mapping report keys (e.g. ``"final-verdict"``) to written file paths.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    generated: dict[str, Path] = {}

    enabled_set = set(request.enabled_reports)

    if "final-verdict" in enabled_set or "all" in enabled_set:
        content = render_final_verdict_report(
            request, verdict, ledger, len(findings),
            source_state=source_state, ast_index=ast_index,
        )
        dest = out_path / "final-verdict.md"
        dest.write_text(_with_instrument_disclosure(content), encoding="utf-8")
        generated["final-verdict"] = dest

    if "coverage-ledger" in enabled_set or "all" in enabled_set:
        cov_report = build_coverage_report(ledger)
        content = render_coverage_text(cov_report)
        dest = out_path / "coverage-ledger.md"
        dest.write_text(_with_instrument_disclosure(content), encoding="utf-8")
        generated["coverage-ledger"] = dest

    if "security-review" in enabled_set or "all" in enabled_set:
        content = render_security_review_report(request, findings)
        dest = out_path / "security-review.md"
        dest.write_text(_with_instrument_disclosure(content), encoding="utf-8")
        generated["security-review"] = dest

    if "architecture-review" in enabled_set or "all" in enabled_set:
        content = render_architecture_review_report(request, findings)
        dest = out_path / "architecture-review.md"
        dest.write_text(_with_instrument_disclosure(content), encoding="utf-8")
        generated["architecture-review"] = dest

    return generated
