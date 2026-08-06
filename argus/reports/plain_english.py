"""PURE plain-English (human-register) rendering of a verdict — the dual-register half.

Drivers: ArgusAgent-FR-18 (machine-readable verdict — this module renders the HUMAN
companion to it, never a replacement), ArgusAgent-NFR-S1 (no source / secret bytes /
absolute host path — every line is derived from the already-redacted
:class:`~argus.verdict.verdict_gate.AuditVerdict` counters), ArgusAgent-AR8 (PURE — no
I/O, no clock, no LLM, no float), ArgusAgent-NFR-M1 (≤1200-line files; the CLI stays a
thin shell and imports this instead of growing presentation logic).

Why this module exists — the product brief's "dual-register verdict output"
---------------------------------------------------------------------------
The brief locks TWO registers for every verdict: the audit-grade negative-assurance
artifact (machine-readable, the wire contract) PLUS a plain-English ship-readiness
line for the engineer ICP. Only the first was built. What an operator actually saw
was::

    verdict=NOT_READY_FOR_RELEASE deep_ratio=11/28 blocking_findings=0

— a blocking word beside a zero blocking count, with the real reason (a coverage gate)
nowhere in the line. That reads as a contradiction, and an operator who cannot tell
"I found a defect" from "I did not look at enough" learns to distrust both. This
module is the second register: it names WHICH gate was not met, in the words a human
would use, without touching the machine line.

What it deliberately does NOT do
--------------------------------
It does not change the verdict, the exit code, or the machine summary — those are the
frozen wire contract (AR3/FR18) and are rendered elsewhere, unchanged. A wording layer
must never become a second, disagreeing source of truth; every statement here is a
restatement of a counter already on the verdict.

The honest-``audited_deep`` disclosure (the over-claim this closes)
-------------------------------------------------------------------
``audited_deep`` is defined by the PRD as a claim citing specific symbols / line
ranges validated against the repo AST. In a run with no LLM deep pass enabled, what
the grade actually attests is narrower: the file parsed cleanly, exhibits ≥1 real
definition (the FR7 ``is_deep_claim_grounded`` fact), and the deterministic detectors
ran over it. That is a real, defensible statement — but it is not comprehension, and
presenting the bare label to a human lets the label promise more than the pass
delivered. :func:`render_depth_meaning` states the difference in the report rather
than leaving the reader to infer it.

The disclosure is DERIVED from ``enabled_passes``, not hardcoded: when a deep
LLM-backed pass is built and enabled, the text changes with it and cannot go stale.

The four FR16 rows this module renders (Story 8.3 / DR-11)
----------------------------------------------------------
Since the FR16 amendment (Story 8.1) the gate discloses WHICH of four rows produced a
verdict, and two of them share one enum member. :func:`_headline` renders one message
per row, and exactly four exist:

===========================  ==========================  =====================
FR16 row                     Verdict / exit              Headline opens with
===========================  ==========================  =====================
1 — below the floor          ``INSUFFICIENT_COVERAGE`` 3 ``NOT ASSESSED``
2 — blocking findings        ``NOT_READY_FOR_RELEASE`` 2 ``BLOCKED``
3 — gates met                ``RELEASE_READY`` 0         ``READY``
4 — gate unmet, nothing      ``INSUFFICIENT_COVERAGE`` 3 ``NOT VOUCHED``
    found
===========================  ==========================  =====================

Rows 1 and 4 are the reason this split exists: same token, same exit code, opposite
operator actions ("give me more to look at" vs "I looked, found nothing, and a gate is
unmet"). The human register is the ONLY surface on which the two are distinguishable,
so getting the words wrong here is not cosmetic.

The row-1/row-4 split reads :attr:`AuditVerdict.is_below_floor` and NOTHING else — never
``decision_row`` directly (it is ``None`` for a pre-amendment payload, which
``is_below_floor`` already resolves correctly) and never a re-derived
``deep_ratio < INSUFFICIENT_COVERAGE_FLOOR`` comparison, which would fork the decision
table (§3.3 / AR7). This module holds no copy of the table; it restates the row the gate
disclosed.
"""

from __future__ import annotations

from argus.verdict.verdict_gate import (
    RELEASE_READY_DEEP_THRESHOLD,
    AuditVerdict,
    Verdict,
)

__all__ = [
    "LLM_DEEP_PASSES",
    "ShipReadinessError",
    "render_depth_meaning",
    "render_ship_readiness",
]


class ShipReadinessError(ValueError):
    """A verdict the FR16 gate cannot produce reached the human renderer (AR10).

    Raised ONLY for ``NOT_READY_FOR_RELEASE`` with ``blocking_finding_count == 0``.
    Post-amendment (Story 8.1) the ONLY path to ``NOT_READY_FOR_RELEASE`` is FR16
    row 2, which fires on ``blocking >= 1`` — so that state has no producer, proven
    by an exhaustive sweep of the real fold (``TC-ArgusAgent-REPORT-002-10``).

    It is a raise rather than a rendered default because the default is the bug:
    falling through to the row-2 arm would print ``BLOCKED — 0 verdict-blocking
    finding(s)``, the exact false accusation Epic 8 exists to delete. The house
    pattern for a closed vocabulary with an exhaustive branch is a typed failure and
    never a silent default — ``exit_code_for_verdict`` raises for an unmapped verdict,
    ``_assurance_statement`` raises ``NegativeAssuranceError`` for an unhandled one. A
    ``ValueError`` subclass specifically, because ``cli.py`` already degrades one to a
    typed, secret-safe exit ``1``.
    """

# Pass names that dispatch an LLM-backed deep read. EMPTY-in-effect today: the Epic-6
# LLMDispatchPort + adapters exist, but no pass wires them into the pipeline, so no
# enabled pass can currently supply comprehension-grade evidence. Adding the pass here
# is what flips render_depth_meaning to its stronger wording — the disclosure tracks
# what actually ran instead of drifting out of date.
LLM_DEEP_PASSES: tuple[str, ...] = ("deep",)


def render_depth_meaning(enabled_passes: tuple[str, ...] | list[str]) -> str:
    """State what ``audited_deep`` attests IN THIS RUN (PURE, one sentence-pair).

    Derived from *enabled_passes* so the disclosure can never over-claim: with no
    LLM-backed deep pass enabled, the grade attests structure + deterministic
    detectors, and says so plainly.

    Returned MARKUP-FREE (plain prose plus backticks, which render as-is in a
    terminal) so the same string is correct in the CLI and inside a Markdown callout.
    A caller wanting emphasis adds it; this function never embeds formatting that
    would leak asterisks onto a terminal.
    """
    if any(name in LLM_DEEP_PASSES for name in enabled_passes):
        return (
            "What `audited_deep` means in this run: a deep read was dispatched for the "
            "file and its claim was validated against the repository AST."
        )
    return (
        "What `audited_deep` means in this run: the file parsed cleanly, contains at "
        "least one real function or class, and every enabled deterministic detector ran "
        "over it. No language model read any source — no LLM-backed deep pass was "
        "enabled. This is a structural and deterministic assurance grade, not a "
        "comprehension grade."
    )


def _headline(verdict: AuditVerdict) -> str:
    """The one line a human reads first — names the OUTCOME, not the enum (PURE).

    One branch per FR16 row (see the module docstring's table), and no others. The
    load-bearing split is inside ``INSUFFICIENT_COVERAGE``: row 1 examined too little
    to say anything, row 4 examined plenty, found nothing, and missed a gate. Both
    carry exit ``3``, so an operator who cannot tell them apart cannot tell whether to
    widen the audit or to fix a gate.

    The ``NOT VOUCHED`` wording below is the pre-amendment else-branch's own text,
    RELOCATED (Story 8.3 / D2) rather than re-authored: it was always the row-4
    message, written back when row 4's case arrived wearing a ``NOT_READY_FOR_RELEASE``
    label. Its old predicate — ``NOT_READY_FOR_RELEASE`` with zero blocking findings —
    is now unreachable and is a :class:`ShipReadinessError` instead of a branch. The
    only widening is "a coverage gate" → "a coverage or critical-subsystem gate": row 4
    also fires with 100 % of files at ``audited_deep``, on the critical clause alone,
    and the old text was false for exactly that run.

    Raises:
        ShipReadinessError: the verdict is ``NOT_READY_FOR_RELEASE`` with zero blocking
            findings — a state the gate cannot produce.
    """
    if verdict.verdict is Verdict.RELEASE_READY:  # FR16 row 3
        return (
            "READY — no blocking problems found, and enough of the code was examined "
            "deeply to say so."
        )
    if verdict.verdict is Verdict.INSUFFICIENT_COVERAGE:
        if verdict.is_below_floor:  # FR16 row 1 — the FLOOR, not a gate
            return (
                "NOT ASSESSED — too little of the code was examined deeply to make any "
                "call. This is a statement about the audit, not about the code."
            )
        return (  # FR16 row 4 — a gate unmet with nothing found
            "NOT VOUCHED — nothing broken was found, but a coverage or "
            "critical-subsystem gate was not met, so no release-readiness claim is "
            "made. This is a statement about the audit, not about the code."
        )
    if verdict.blocking_finding_count < 1:
        raise ShipReadinessError(
            f"{verdict.verdict.value} with blocking_finding_count="
            f"{verdict.blocking_finding_count}: FR16 row 2 is the only producer of "
            f"this verdict and it requires at least one verdict-eligible finding"
        )
    return (  # FR16 row 2 — the only blocking outcome, always with N >= 1
        f"BLOCKED — {verdict.blocking_finding_count} verdict-blocking finding(s) "
        f"must be resolved."
    )


def render_ship_readiness(
    verdict: AuditVerdict,
    *,
    enabled_passes: tuple[str, ...] | list[str] = (),
) -> tuple[str, ...]:
    """Render the human-register ship-readiness block (PURE, secret-safe).

    Every line restates a counter already present on *verdict* — no new judgement, no
    file content, no absolute path (NFR-S1). Returns a tuple of plain lines with no
    trailing newline, so the caller owns the surrounding formatting (the CLI prints
    them; the report indents them into Markdown).

    The ``Next:`` line exists because a red light with no next action trains an
    operator to ignore it. It is deliberately CONDITIONAL and never promises
    ``RELEASE_READY``: narrowing the scope can clear the coverage gate but leaves
    blocking findings and the critical-subsystem clause untouched, and over-promising
    here would be the same dishonesty as the contradiction it replaces.

    Raises:
        ShipReadinessError: *verdict* is a state the FR16 gate cannot produce (see
            :func:`_headline`). The CLI degrades this to a typed, secret-safe exit
            ``1`` (AR10) rather than printing a sentence about an impossible run.
    """
    scope = verdict.coverage_scope
    assessed_ratio = scope.assessed_deep_ratio if scope is not None else verdict.deep_ratio

    lines: list[str] = [f"Ship-readiness: {_headline(verdict)}"]

    lines.append(f"  - Verdict-blocking findings: {verdict.blocking_finding_count}")
    if scope is None:
        lines.append(
            f"  - Deeply examined: {verdict.deep_count} of {verdict.total_count} files "
            f"({verdict.deep_ratio}) — whole repository, test files included"
        )
    else:
        lines.append(
            f"  - Deeply examined: {scope.assessed_deep_count} of "
            f"{scope.assessed_total_count} assessed files ({scope.assessed_deep_ratio}) "
            f"— scope '{scope.scope_id}', {scope.excluded_count} held out "
            f"({scope.excluded_reason})"
        )
    if not verdict.critical_subsystems_all_deep:
        lines.append(
            f"  - Critical files not examined deeply: "
            f"{len(verdict.critical_subsystems_not_deep)}"
        )

    if enabled_passes:
        lines.append(f"  - {render_depth_meaning(enabled_passes)}")

    next_steps: list[str] = []
    if assessed_ratio < RELEASE_READY_DEEP_THRESHOLD and scope is None:
        next_steps.append(
            "test files are counted in this denominator and are graded shallow by "
            "construction — `--coverage-scope application` assesses application files "
            "only (disclosed in the verdict; the coverage floor still applies)"
        )
    if not verdict.critical_subsystems_all_deep:
        next_steps.append(
            "see the final-verdict report for the named critical files and their actual "
            "depth; `--exclude-critical <path>` removes one that is not genuinely critical"
        )
    for step in next_steps:
        lines.append(f"  Next: {step}")

    return tuple(lines)
