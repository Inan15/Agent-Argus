"""PURE report generator for ArgusAgent end-user developer reports (AR8 / NFR-S1).

Reads the audit execution results (intake, verdict, ledger, findings) and renders
structured Markdown reports according to user-selected report choices (`enabled_reports`).
"""

from __future__ import annotations

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
from argus.verdict.verdict_gate import AuditVerdict

__all__ = [
    "generate_reports",
    "render_final_verdict_report",
    "render_security_review_report",
    "render_architecture_review_report",
]


def render_final_verdict_report(
    request: AuditRequest,
    verdict: AuditVerdict,
    ledger: CoverageLedger,
    total_findings_count: int,
) -> str:
    """Render the `final-verdict.md` end-user summary report."""
    lines: list[str] = []
    lines.append("# ⚖️ Argus Final Audit Verdict Report")
    lines.append("")
    lines.append(f"- **Commit Pinned**: `{request.commit}`")
    lines.append(f"- **Final Verdict**: **`{verdict.verdict.value}`** (Exit Code `{verdict.exit_code}`)")
    lines.append(f"- **Deep Coverage Ratio**: **`{verdict.deep_ratio}`** ({verdict.deep_count}/{verdict.total_count} files)")
    lines.append(f"- **Blocking Findings**: **{verdict.blocking_finding_count}**")
    lines.append(f"- **Total Findings Emitted**: **{total_findings_count}**")
    lines.append("")

    if verdict.verdict.value == "RELEASE_READY":
        lines.append(render_callout("TIP", "Repository satisfies all deterministic release readiness criteria. Zero blocking findings emitted."))
    elif verdict.verdict.value == "INSUFFICIENT_COVERAGE":
        lines.append(render_callout("WARNING", "Repository deep coverage ratio is below the required floor. Additional definitions or tests required."))
    else:
        lines.append(render_callout("CAUTION", "Repository is NOT ready for release due to blocking findings or unresolved security/correctness rules."))

    lines.append("")
    scope_statement = getattr(verdict, "scope_statement", "Scope: Whole repository audit at pinned commit.")
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
) -> dict[str, Path]:
    """Generate requested Markdown end-user reports and write to *output_dir*.

    Returns a dict mapping report keys (e.g. ``"final-verdict"``) to written file paths.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    generated: dict[str, Path] = {}

    enabled_set = set(request.enabled_reports)

    if "final-verdict" in enabled_set or "all" in enabled_set:
        content = render_final_verdict_report(request, verdict, ledger, len(findings))
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
