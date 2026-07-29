"""ArgusAgent report generation package."""

from argus.reports.formatter import format_locator_link, mask_secret, render_markdown_table
from argus.reports.generator import (
    generate_reports,
    render_architecture_review_report,
    render_final_verdict_report,
    render_security_review_report,
)

__all__ = [
    "mask_secret",
    "format_locator_link",
    "render_markdown_table",
    "generate_reports",
    "render_final_verdict_report",
    "render_security_review_report",
    "render_architecture_review_report",
]
