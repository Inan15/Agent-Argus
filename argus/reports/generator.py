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
from argus.detectors.vacuous_test import is_test_file
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


def _render_test_dilution_hint(verdict: AuditVerdict, ledger: CoverageLedger) -> list[str]:
    """Explain a coverage block that is an artifact of test-file dilution, if it is one.

    A test file is graded ``audited_shallow`` BY CONSTRUCTION — it is the subject of
    the vacuous-test pass, not a target of deep grounding. In a repository with more
    test files than application files those entries dominate the denominator, and the
    repository gets blocked for being well-tested.

    ``--coverage-scope application`` fixes that, but it is opt-in (the default stays
    whole-repository so persisted evidence and existing CI gates keep their meaning).
    Opt-in only helps an operator who knows the flag exists — so when the coverage
    gate is the thing blocking AND narrowing would clear it, the report says so here
    rather than leaving them to discover it.

    Deliberately does NOT promise ``RELEASE_READY``: it reports only that the COVERAGE
    gate would be satisfied, because blocking findings and the critical-subsystem
    clause are unaffected by scope. Over-promising here would be the same class of
    dishonesty as the block message it replaces.
    """
    if verdict.coverage_scope is not None:
        return []  # already narrowed — nothing to suggest
    if verdict.verdict is Verdict.RELEASE_READY:
        return []
    if verdict.deep_ratio >= RELEASE_READY_DEEP_THRESHOLD:
        return []  # coverage is not what is blocking

    application = [e for e in ledger.entries if not is_test_file(e.file_path)]
    held_out = len(ledger.entries) - len(application)
    if not application or held_out == 0:
        return []

    app_deep = sum(1 for e in application if e.depth is CoverageDepth.AUDITED_DEEP)
    app_ratio = Fraction(app_deep, len(application))
    if app_ratio < RELEASE_READY_DEEP_THRESHOLD:
        return []  # narrowing would not clear the gate — do not suggest it

    remaining = []
    if verdict.blocking_finding_count > 0:
        remaining.append(f"{verdict.blocking_finding_count} blocking finding(s)")
    if not verdict.critical_subsystems_all_deep:
        remaining.append("the critical-subsystem clause")
    caveat = (
        f" Note that {' and '.join(remaining)} would still block."
        if remaining
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


def _render_critical_blockers(verdict: AuditVerdict, ledger: CoverageLedger) -> list[str]:
    """Render the critical paths that withheld RELEASE_READY, with their actual depth.

    "At least one critical subsystem is not audited deep" tells an operator that they
    are blocked but not by what, so there is no next action. Naming each file and the
    depth it actually reached turns the block into a work list.

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
        "These withheld `RELEASE_READY` (FR16). Each must reach `audited_deep`, or be",
        "removed from the critical set with `--exclude-critical` if it is not genuinely critical.",
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
    return lines


_GRAMMAR_PACKAGE_BY_LANGUAGE = {
    "javascript": "tree-sitter-javascript",
    "typescript": "tree-sitter-typescript",
    "go": "tree-sitter-go",
    "rust": "tree-sitter-rust",
    "java": "tree-sitter-java",
    "c": "tree-sitter-c",
    "cpp": "tree-sitter-cpp",
    "ruby": "tree-sitter-ruby",
    "php": "tree-sitter-php",
    "python": "tree-sitter-python",
}


def _render_readability_warning(
    ledger: CoverageLedger, ast_index: object | None
) -> list[str]:
    """Warn when Argus could not READ what it enumerated — loudly, and with a remedy.

    A repository whose language has no installed tree-sitter grammar produces a
    perfectly ordinary-looking ``INSUFFICIENT_COVERAGE``. Technically true, and
    badly misleading: it reads as "your repo needs more tests" when the actual
    meaning is "I could not parse a single file". The operator's remedy is a pip
    install, and nothing in the report previously pointed at it.

    This is the ``no silent no-op`` rule. An audit that examined nothing must say so
    in the loudest register the report has, never imply a coverage judgement it did
    not make.
    """
    if ast_index is None:
        return []
    entries = getattr(ast_index, "entries", ()) or ()
    if not entries:
        return []

    eligible = sum(1 for e in entries if getattr(e, "ast_eligible", False))
    if eligible:
        return []  # something was parseable — this is a real coverage result

    prefix = "grammar_missing_"
    missing: Counter[str] = Counter()
    for entry in entries:
        reason = getattr(entry, "parse_failure_reason", None) or ""
        if reason.startswith(prefix):
            missing[reason[len(prefix):]] += 1

    if not missing:
        return []

    packages = sorted(
        {_GRAMMAR_PACKAGE_BY_LANGUAGE.get(lang, f"tree-sitter-{lang}") for lang in missing}
    )
    breakdown = ", ".join(f"{n} {lang}" for lang, n in sorted(missing.items()))
    return [
        render_callout(
            "CAUTION",
            f"**No file could be parsed — this verdict reflects tooling, not code quality.** "
            f"Argus enumerated {len(entries)} file(s) ({breakdown}) but has no installed "
            f"grammar for them, so ZERO reached `audited_deep`. The coverage numbers below "
            f"are therefore a floor imposed by a missing dependency. Install: "
            f"`pip install {' '.join(packages)}` and re-run."
        ),
        "",
    ]


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

    if verdict.verdict.value == "RELEASE_READY":
        lines.append(render_callout("TIP", "Repository satisfies all deterministic release readiness criteria. Zero blocking findings emitted."))
    elif verdict.verdict.value == "INSUFFICIENT_COVERAGE":
        lines.append(render_callout("WARNING", "Repository deep coverage ratio is below the required floor. Additional definitions or tests required."))
        lines.append("")
        # Dilution can push a repo under the FLOOR too, not just under the threshold.
        lines.extend(_render_test_dilution_hint(verdict, ledger))
    else:
        # Name the gate(s) that ACTUALLY failed. A fixed "due to blocking findings"
        # string is false whenever the block came from coverage or the critical-
        # subsystem clause with zero findings — and an operator who reads
        # "blocking findings" beside "Blocking Findings: 0" cannot act on it.
        assessed_ratio = scope.assessed_deep_ratio if scope is not None else verdict.deep_ratio
        reasons: list[str] = []
        if verdict.blocking_finding_count > 0:
            reasons.append(
                f"{verdict.blocking_finding_count} verdict-blocking finding(s)"
            )
        if assessed_ratio < RELEASE_READY_DEEP_THRESHOLD:
            reasons.append(
                f"deep coverage `{assessed_ratio}` is below the "
                f"`{RELEASE_READY_DEEP_THRESHOLD}` release threshold"
            )
        if not verdict.critical_subsystems_all_deep:
            reasons.append(
                "at least one critical subsystem is not audited deep (FR16)"
            )
        detail = "; ".join(reasons) if reasons else "a release gate was not satisfied"
        lines.append(
            render_callout("CAUTION", f"Repository is NOT ready for release — {detail}.")
        )
        lines.append("")
        lines.extend(_render_test_dilution_hint(verdict, ledger))
        lines.extend(_render_critical_blockers(verdict, ledger))

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
    secret_findings = [f for f in findings if str(f.get("detector_id", "")) in ("secret_scan", "hardcoded_secret")]
    
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
        rule_id = str(f.get("rule_id", "hardcoded_secret"))
        file_path = str(f.get("file_path", ""))
        line_no_val = f.get("line_number")
        line_no_int = int(line_no_val) if isinstance(line_no_val, (int, str)) and str(line_no_val).isdigit() else None
        locator = format_locator_link(file_path, line_no_int)
        
        snippet = str(f.get("snippet", f.get("matched_string", "")))
        masked_snippet = mask_secret(snippet) if snippet else "High Entropy Token"
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
        if str(f.get("detector_id", "")) in ("orphan_code", "cross_partition") or str(f.get("rule_id", "")) in ("orphan_code", "cross_partition")
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
        rule_id = str(f.get("rule_id", f.get("detector_id", "architecture_finding")))
        file_path = str(f.get("file_path", ""))
        line_no_val = f.get("line_number")
        line_no_int = int(line_no_val) if isinstance(line_no_val, (int, str)) and str(line_no_val).isdigit() else None
        locator = format_locator_link(file_path, line_no_int)
        details = str(f.get("message", "Architectural boundary/reference finding"))
        rows.append([f"`{rule_id}`", locator, details])

    lines.append(render_markdown_table(headers, rows))
    lines.append("")
    return "\n".join(lines)


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
        dest.write_text(content, encoding="utf-8")
        generated["final-verdict"] = dest

    if "coverage-ledger" in enabled_set or "all" in enabled_set:
        cov_report = build_coverage_report(ledger)
        content = render_coverage_text(cov_report)
        dest = out_path / "coverage-ledger.md"
        dest.write_text(content, encoding="utf-8")
        generated["coverage-ledger"] = dest

    if "security-review" in enabled_set or "all" in enabled_set:
        content = render_security_review_report(request, findings)
        dest = out_path / "security-review.md"
        dest.write_text(content, encoding="utf-8")
        generated["security-review"] = dest

    if "architecture-review" in enabled_set or "all" in enabled_set:
        content = render_architecture_review_report(request, findings)
        dest = out_path / "architecture-review.md"
        dest.write_text(content, encoding="utf-8")
        generated["architecture-review"] = dest

    return generated
