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

The disclosure is DERIVED from what the run actually DID, not hardcoded and — since
Story 12.2 — not from what it was ASKED to do either: the text changes with the deep
pass's OUTCOME and cannot go stale or over-claim.

~~The disclosure is DERIVED from ``enabled_passes``, not hardcoded: when a deep
LLM-backed pass is built and enabled, the text changes with it and cannot go stale.~~
(§3.4 struck, not deleted — corrected 2026-08-13 by Story 12.2. Deriving it from
``enabled_passes`` derived it from the REQUEST while the sentence stated the OUTCOME.
Because ``--passes`` accepts unvalidated tokens, ``--passes coverage,deep`` made the
tool report a dispatched, AST-validated deep read on a tree whose deep seam had zero
production callers — FR36's *"never produces a false deep claim"*, violated by the
shipped tool. See :func:`render_depth_meaning` for the three states that replace it.)

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

from collections import Counter
from typing import Iterable

from argus.verdict.verdict_gate import (
    RELEASE_READY_DEEP_THRESHOLD,
    AuditVerdict,
    DeepPassOutcome,
    Verdict,
)

from argus.shared.source_languages import format_ingestion_boundary, AUDITABLE_SUFFIXES

# The reason-token vocabulary is the PURE contract shared with the PRODUCER
# (``argus/index/ast_index.py``) and with the report register
# (``argus/reports/generator.py``). This module owns the HUMAN wording and nothing else:
# which class, which language and which package are read off that one table, so the two
# registers of a single run cannot disagree about the facts while each keeps its own voice
# (Story 10.4 / DN-3 — the arrow stays pure-module → pure-module, AR8).
from argus.shared.grammar_status import (
    CORE_PACKAGE,
    INSPECT_CORE_VERSION_COMMAND,
    SUPPORTED_CORE_RANGE,
    GrammarFailure,
    classify_reason,
    grammar_package_for,
)

__all__ = [
    "ARGUS_ISSUE_TRACKER",
    "INTERNAL_DEFECT_MARKER",
    "TERMINAL_OUTCOMES",
    "TYPED_FAILURE_CLASSES",
    "LLM_DEEP_PASSES",
    "deep_pass_enabled",
    "with_deep_pass",
    "ShipReadinessError",
    "render_depth_meaning",
    "render_grammar_downgrade_summary",
    "render_inert_reports_disclosure",
    "render_ship_readiness",
    "render_audit_failed_next_action",
    "render_unmatched_designation_disclosure",
    "render_usage_error_next_action",
]

# The four terminal outcome tokens (FR37 / AC1)
TERMINAL_OUTCOMES: tuple[str, ...] = (
    "RELEASE_READY",
    "NOT_READY_FOR_RELEASE",
    "INSUFFICIENT_COVERAGE",
    "AUDIT_FAILED",
)



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

# Pass names that dispatch an LLM-backed deep read. Story 12.2 WIRED this: the token is
# put into ``enabled_passes`` by the ``--deep-audit`` opt-in and the pipeline runs the
# pass, so an enabled deep pass can now supply comprehension-grade evidence — and
# ``render_depth_meaning`` reports whether it actually DID.
#
# ~~EMPTY-in-effect today: the Epic-6 LLMDispatchPort + adapters exist, but no pass wires
# them into the pipeline, so no enabled pass can currently supply comprehension-grade
# evidence. Adding the pass here is what flips render_depth_meaning to its stronger
# wording — the disclosure tracks what actually ran instead of drifting out of date.~~
# (§3.4 struck, not deleted — corrected 2026-08-13 by Story 12.2. The last sentence was
# the defect in one line: membership of THIS tuple flipped the wording, and membership
# was reachable from an unvalidated CSV token, so the disclosure tracked what was ASKED
# FOR and not what ran.)
LLM_DEEP_PASSES: tuple[str, ...] = ("deep",)


def deep_pass_enabled(enabled_passes: tuple[str, ...] | list[str]) -> bool:
    """Whether this run REQUESTED an LLM-backed deep read (PURE).

    THE single membership predicate. `argus/cli.py`, `argus/pipeline.py` and
    :func:`render_depth_meaning` all ask this question, and before Story 12.2 each would
    have spelled the token itself — three literals that could drift apart on the one flag
    that governs egress. One vocabulary, asked one way (AR7 / §3.3 — reuse, never fork).

    Note this answers *requested*, never *delivered*. The whole of §0.5's defect was
    treating the two as the same question; :func:`render_depth_meaning` needs BOTH and
    takes the outcome separately.
    """
    return any(name in LLM_DEEP_PASSES for name in enabled_passes)


def with_deep_pass(enabled_passes: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    """Return *enabled_passes* with the deep pass selected — the ``--deep-audit`` entrance.

    The flag is a new ENTRANCE to the existing pass, not a new mechanism: it composes the
    same token every other surface already understands, so the vocabulary stays single.
    Idempotent, and it never removes anything — subtraction is ``--skip-pass``'s job, and
    keeping the two operations separate is what preserves the LOCKED one-directional
    composition rule (a skip can never re-add; an add must never override a skip).
    """
    if deep_pass_enabled(enabled_passes):
        return tuple(enabled_passes)
    return tuple(enabled_passes) + LLM_DEEP_PASSES[:1]


def render_depth_meaning(
    enabled_passes: tuple[str, ...] | list[str],
    *,
    deep_pass: DeepPassOutcome | None = None,
) -> str:
    """State what ``audited_deep`` attests IN THIS RUN (PURE, one sentence-pair).

    THREE honest states, not two (Story 12.2 / §A.4). The function stays PURE and the
    sentences are unchanged where they were already true; what changed is the PREDICATE
    the strong sentence is derived from.

    1. **Not requested** — no deep pass in *enabled_passes*. The grade attests structure
       + deterministic detectors, and says so plainly. UNCHANGED, and it is the branch
       every default run takes.
    2. **Requested and DELIVERED** — ``deep_pass.delivered``. The strengthened sentence,
       UNCHANGED, and now true by construction: ``delivered_count`` counts only targets
       for which a recording came back AND its claim was AST-grounded, which is exactly
       what the sentence says happened.
    3. **Requested and NOT delivered** — the state FR36 and NFR-R1 care about most, and
       the one that did not exist before. It is NOT the same as state 1: saying "no
       LLM-backed deep pass was enabled" to an operator who explicitly enabled one is a
       different falsehood, not a safe fallback.

    THE DEFECT THIS CLOSES (measured on ``2bea92f``, before this story changed a line):
    the predicate was ``any(name in LLM_DEEP_PASSES for name in enabled_passes)`` — i.e.
    *was depth REQUESTED* — while the sentence it selected answered *was depth
    DELIVERED*. Because ``--passes`` is an unvalidated CSV (``_ALL_PASSES`` is the
    DEFAULT set, not a whitelist), ``argus audit <repo> --passes coverage,deep`` printed
    *"a deep read was dispatched … validated against the repository AST"* on a tree where
    ``DeepAuditSeam`` had ZERO production callers. That is FR36's *"it never produces a
    false deep claim"* being violated by the shipped tool. The remedy is NOT to delete
    the sentence — the sentence is correct — but to derive it from work performed, in the
    same spirit as *the artifact is the fact* (``TC-ArgusAgent-DOCS-001-54``).

    Returned MARKUP-FREE (plain prose plus backticks, which render as-is in a
    terminal) so the same string is correct in the CLI and inside a Markdown callout.
    A caller wanting emphasis adds it; this function never embeds formatting that
    would leak asterisks onto a terminal.
    """
    if deep_pass_enabled(enabled_passes):
        if deep_pass is not None and deep_pass.delivered:
            return (
                "What `audited_deep` means in this run: a deep read was dispatched for the "
                "file and its claim was validated against the repository AST. (Note: deep pass "
                "results are recomputed per run and not served from the offline stage memo store.)"
            )
        return (
            "What `audited_deep` means in this run: a deep pass was requested but no deep "
            "read was completed, so no file is graded on comprehension. Every "
            "`audited_deep` grade here rests on structure and the deterministic detectors "
            "alone, and the files the deep pass could not read are recorded "
            "`audited_shallow` rather than counted as deeply examined. (Note: deep pass "
            "results are recomputed per run and not served from the offline stage memo store.)"
        )
    return (
        "What `audited_deep` means in this run: the file parsed cleanly, contains at "
        "least one real function or class, and every enabled deterministic detector ran "
        "over it. No language model read any source — no LLM-backed deep pass was "
        "enabled. This is a structural and deterministic assurance grade, not a "
        "comprehension grade."
    )


def _downgrade_sentence(failure: GrammarFailure, counts: Counter[str]) -> str:
    """One human-register sentence for ONE failure class (PURE, markup-free).

    Never a blended sentence, for :func:`~argus.reports.generator._render_grammar_remedy`'s
    reason: a polyglot repository can hit several of these at once and a merged
    ``pip install`` line is wrong for at least one of them by construction — cause 1's
    package is absent, cause 3's is present and broken, cause 2's is present and fine.

    This is the HUMAN register of facts the report register also states. The wording is this
    module's (markup-free, so the same string is correct on a terminal and inside a Markdown
    callout); the FACTS — which class, which language, which package — come from
    ``argus.shared.grammar_status`` in both places, which is what stops the two surfaces of
    one run from naming different packages.

    Raises:
        ValueError: *failure* has no registered sentence. An unregistered cause is LOUD here
            rather than falling through to another cause's remedy — ``DF-10-4-E``'s lesson,
            applied to this surface the day it was written rather than after it bites.
    """
    languages = sorted(counts)
    files = sum(counts.values())
    where = ", ".join(f"{counts[lang]} {lang}" for lang in languages)
    packages = " ".join(grammar_package_for(lang) for lang in languages)

    if failure is GrammarFailure.PACKAGE_MISSING:
        return (
            f"Downgraded to `audited_shallow` — grammar package not installed ({where}): run "
            f"`pip install {packages}` and re-run to restore deep grounding. All supported "
            f"languages ship in the default install, so a grammar missing here is a packaging "
            f"or environment defect rather than a limit of this code (NFR-P3)."
        )
    if failure is GrammarFailure.ENTRY_POINT_MISSING:
        return (
            f"Downgraded to `audited_shallow` — Argus does not recognise this grammar "
            f"package's entry point ({where}): `{packages}` IS installed, so there is nothing "
            f"for you to install. This is an Argus defect; please report it with the "
            f"installed version of `{packages}`."
        )
    if failure is GrammarFailure.LOAD_FAILED:
        return (
            f"Downgraded to `audited_shallow` — the installed grammar could not be loaded on "
            f"this runtime ({where}): reinstall or rebuild `{packages}` and check that its "
            f"version pairs with the installed `{CORE_PACKAGE}` (an ABI mismatch or a corrupt "
            f"build looks like this)."
        )
    if failure is GrammarFailure.CORE_RUNTIME_MISSING:
        return (
            f"Downgraded to `audited_shallow` — the `{CORE_PACKAGE}` core runtime is not "
            f"importable ({files} file(s)): run `pip install {CORE_PACKAGE}` and re-run. "
            f"Every language is affected, so installing individual grammar packages will not "
            f"help."
        )
    if failure is GrammarFailure.RUNTIME_UNVALIDATED:
        # Deliberately names no observed version, exception message or host path
        # (NFR-S1 / 10.4 DN-5): the operator is given the supported range and the command to
        # read their own environment. A richer diagnostic is Story 12.8's.
        return (
            f"Downgraded to `audited_shallow` — the installed parsing toolchain did not pass "
            f"Argus's self-check ({files} file(s)): install a supported `{CORE_PACKAGE}` "
            f"(`{SUPPORTED_CORE_RANGE}`) and re-run; check what you have with "
            f"`{INSPECT_CORE_VERSION_COMMAND}`. Every language is affected, so installing "
            f"individual grammar packages will not help."
        )
    raise ValueError(
        f"no operator remedy is registered for GrammarFailure.{failure.name}. Every registered "
        "cause must render ITS OWN sentence: falling through to another cause's would tell the "
        "operator to run a command that cannot help them (argus/shared/grammar_status.py)."
    )


def render_grammar_downgrade_summary(
    reasons: Iterable[str | None],
) -> tuple[str, ...]:
    """State, per failure class, WHICH grammar package is missing (PURE, secret-safe).

    Story 12.5 / NFR-P3, second clause: *where a language grammar is uninstalled or
    downgraded, its absence and the reason are stated in the tool's own output at the point
    the file is downgraded* — not only in the README, and not only as a coverage number that
    reads as a judgement about the code.

    *reasons* is the recorded ``parse_failure_reason`` of each affected file, in any order.
    Classification goes through ``classify_reason``, never through prefix arithmetic at this
    call site: ``grammar_entrypoint_missing_go`` does not start with ``grammar_missing_`` (a
    prefix reader goes SILENT) and a naive widening to ``grammar_`` would slice it into the
    "language" ``entrypoint_missing_go`` and name the package
    ``tree-sitter-entrypoint_missing_go`` (a prefix reader MISDIRECTS). Anything that is not
    a grammar-LOAD failure — ``syntax_error``, ``read_error``, ``None`` — yields nothing:
    a grammar remedy for a typo would be the same class of wrong answer.

    Ordering is deterministic (AR4): classes in ``GrammarFailure`` declaration order,
    languages sorted inside each class.
    """
    by_class: dict[GrammarFailure, Counter[str]] = {}
    for reason in reasons:
        diagnosis = classify_reason(reason)
        if diagnosis is None:
            continue
        by_class.setdefault(diagnosis.failure, Counter())[diagnosis.language or ""] += 1
    return tuple(
        _downgrade_sentence(failure, by_class[failure])
        for failure in GrammarFailure
        if failure in by_class
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


def render_audit_failed_next_action(
    error_message: str | None = None, *, cause: BaseException | None = None
) -> str:
    """Render the next action for the AUDIT_FAILED non-verdict outcome (FR37).

    Story 12.4 shipped this function for the FR37 terminal-outcome enumeration and it
    acquired **zero production callers** — measured on ``2f84a0b``: its own ``__all__`` and
    one test, while both CLI failure arms printed a cause and stopped. Story 12.8 wires it,
    and it is EXTENDED rather than replaced: a parallel next-action renderer beside the
    shipped one is a defect, not a delivery (AR7 / architecture §3.3).

    Two modes, and the split is the whole design:

    * *cause* omitted — the AUDIT_FAILED **fallback**, byte-identical to what 12.4 shipped.
      This is the terminal-outcome sense: an outcome token with no exception object behind it.
    * *cause* supplied — the **per-cause** remedy, selected by TYPED CLASS from
      :data:`TYPED_FAILURE_CLASSES`. A ``RepoIntakeError`` for a missing path must not be
      answered with *"report an unhandled exception"*; that is a remedy which cannot work.

    Dispatch walks ``type(cause).__mro__`` and takes the FIRST registered class, so a
    subclass always beats its base and no arm can shadow a more specific one by ordering.

    ⚠️ **Dispatch is by class NAME, deliberately.** This module is PURE (AR8) and is
    imported BY ``argus/pipeline.py``, so importing the pipeline's or the intake layer's
    exception classes here would invert that arrow and create an import cycle. The names
    are enumerated in :data:`TYPED_FAILURE_CLASSES` and
    ``tests/test_outcome_next_action_contract.py`` closes over the real classes to prove the
    enumeration still matches the tree — an unenumerated typed failure turns that guard RED,
    which is the ``TERMINAL_OUTCOMES`` device applied at this seam.

    Raises:
        ValueError: *cause* is an exception no registered class matches. Registered
            ``ValueError`` is what makes the dispatch TOTAL over everything the CLI's
            ``except ValueError`` arms can catch, so this raise is reachable only from a
            caller handing over something else — and it is LOUD rather than falling through
            to a neighbour's remedy (``DF-10-4-E``'s lesson, the shape ``_downgrade_sentence``
            above already uses).
    """
    if cause is None:
        detail = f": {error_message}" if error_message else ""
        return (
            f"audit process encountered execution failure{detail} — inspect logs/stderr, "
            f"verify environment setup, or report unhandled exception if persistent"
        )
    for klass in type(cause).__mro__:
        remedy = _NEXT_ACTION_BY_CLASS.get(klass.__name__)
        if remedy is not None:
            return remedy
    raise ValueError(
        f"no operator next action is registered for {type(cause).__name__} (mro: "
        f"{[k.__name__ for k in type(cause).__mro__]}). Every typed failure that can reach "
        "a user surface must name ITS OWN next action: falling through to another class's "
        "would tell the operator to do something that cannot help them. Register it in "
        "TYPED_FAILURE_CLASSES (argus/reports/plain_english.py)."
    )


def render_usage_error_next_action() -> str:
    """The next action for an invocation the PARSER rejected (Story 12.8 / AC8, PURE).

    argparse has already printed the cause (its usage message) on stderr. What it does not
    say — and what a consumer of the exit code cannot otherwise know — is that **no audit
    ran and no verdict exists**. Before this, an argparse usage error exited ``2``, which
    ``action.yml`` publishes as ``verdict=NOT_READY_FOR_RELEASE assessed=true``: a typo
    fabricated an assessment for a run that never happened. The remedy is the tool's own
    output, never a wiki (FR37) — ``--help`` is where the accepted surface is stated, and
    since Story 12.8 it states every argument's live default too.
    """
    return (
        "the command line was rejected by the parser (see the usage message above), so NO "
        "audit ran and NO verdict was produced — exit 1 is the reserved 'no verdict' code, "
        "never a verdict. Correct the invocation and re-run; `argus audit --help` and "
        "`argus install-commands --help` list every accepted argument with its default."
    )


def render_inert_reports_disclosure(reports: tuple[str, ...] | list[str]) -> str:
    """Disclose that ``--reports`` selected types nothing will render (Story 12.8 / AC3, PURE).

    DN-3: this is DISCLOSED, not refused. The combination is legal — a caller that sets
    ``--reports`` unconditionally and ``--report-dir`` conditionally is doing nothing wrong —
    it is simply INERT, and measured on ``2f84a0b`` it produced no file and no word about it.
    Refusing it would break that caller; staying silent costs the operator the run.

    The register is ``_emit_suppression_disclosure``'s (Story 10.3 / AC4.3) and so is the
    reason: a disclosure an operator can act on is one that names what did NOT happen.
    """
    return (
        f"--reports selected {list(reports)} but --report-dir is not set, so NO report file "
        f"was written. Add --report-dir <dir> to render them, or drop --reports; the verdict "
        f"and the ship-readiness block above are unaffected."
    )


def render_unmatched_designation_disclosure(flag: str, paths: tuple[str, ...] | list[str]) -> str:
    """Disclose designated paths that are not in the audited tree (Story 12.8 / AC3, PURE).

    DN-3: ``--critical-subsystem`` / ``--exclude-critical`` take PATHS, an OPEN vocabulary,
    so an unmatched value is disclosed rather than refused — refusing would break the
    legitimate case of designating a subtree that is absent from this partition.

    It is worth disclosing because the measured effect is not cosmetic: on ``2f84a0b``,
    ``--critical-subsystem does/not/exist`` moved the verdict from ``RELEASE_READY`` (exit 0)
    to ``INSUFFICIENT_COVERAGE`` (exit 3) and printed *"Critical files not examined deeply: 1"*
    for a path that does not exist, with nothing anywhere naming the typo.

    Repository-RELATIVE spellings only — they are the operator's own argv values and are
    echoed as given, never resolved against the host filesystem (NFR-S1).
    """
    return (
        f"{flag} named {list(paths)}, which no file or directory in the audited repository "
        f"matches. The designation still applies — a path absent from this partition is "
        f"legal — but it can only be counted as NOT examined deeply, so check the spelling "
        f"if you meant a path that is present."
    )


#: The stable, distinguishable marker an INTERNAL DEFECT carries on stderr (``DF-8-4-D``).
#: Grep-able on purpose: it is what lets an operator, a CI log scraper and a maintainer tell
#: *"Argus is broken"* apart from *"your repository did not meet a gate"*.
#:
#: Named ``…_MARKER`` rather than the house ``…_TOKEN`` suffix, deliberately: ``bandit``'s
#: ``B105`` (hardcoded-password) fires on any constant whose NAME contains ``token``, and the
#: project gate for this story is a stashed-``argus/`` control run proving NO NEW finding. A
#: rename costs nothing here, while the alternative — this repository's FIRST ``# nosec`` — adds
#: a suppression mechanism that is easy to reach for the second time. Recorded rather than done
#: quietly, because it is a deliberate departure from the naming the tree uses elsewhere
#: (``CORE_RUNTIME_TOKEN``, ``RUNTIME_UNVALIDATED_TOKEN``), whose own B105 hits predate this.
INTERNAL_DEFECT_MARKER = "INTERNAL DEFECT"

#: Where a defect is reported. One constant; never re-typed into a message.
ARGUS_ISSUE_TRACKER = "https://github.com/Inan15/Agent-Argus/issues"

_INTERNAL_DEFECT_NEXT_ACTION = (
    f"{INTERNAL_DEFECT_MARKER} — this is a bug in Argus, not a problem with your repository, "
    f"and re-running will not change it. No verdict was produced. Please report it at "
    f"{ARGUS_ISSUE_TRACKER}, quoting the typed line above: it names the failing stage and "
    f"the exception CLASS only, so it carries no path, no source and no secret."
)

_INTAKE_NEXT_ACTION = (
    "the repository could not be read at the state you asked for, so nothing was assessed "
    "and no `.argus/` state was written. Correct the path or the `--commit` pin named above "
    "and re-run; `--strict` is what requires a git repository and a clean tree, so dropping "
    "it audits whatever is on disk and records which state that was."
)

#: The TYPED failure vocabulary that can reach a user surface, enumerated the way
#: ``TERMINAL_OUTCOMES`` enumerates verdicts (Story 12.8 / AC4). Every member has its OWN
#: next action below; a typed class added to ``argus/**`` and not added here turns
#: ``TC-ArgusAgent-REPORT-003-08`` RED rather than silently inheriting a neighbour's remedy.
TYPED_FAILURE_CLASSES: tuple[str, ...] = (
    "SourceStateError",
    "RepoIntakeError",
    "ResumeStateError",
    "UnexpectedStageError",
    "PipelineError",
    "WorkspaceContainmentError",
    "CanonicalSerializationError",
    "ShipReadinessError",
    "UnknownHostError",
    "ContainmentError",
    "CommandInstallError",
    "ValueError",
)

_NEXT_ACTION_BY_CLASS: dict[str, str] = {
    # Intake: the operator's own input is wrong and the operator can fix it.
    "SourceStateError": _INTAKE_NEXT_ACTION,
    "RepoIntakeError": _INTAKE_NEXT_ACTION,
    "ResumeStateError": (
        "the prior `.argus/` state cannot be resumed from, and Argus will never resume from "
        "state it cannot verify. Run a fresh audit; if the state is corrupt or was written by "
        "an older version, remove or move the `.argus/` directory first."
    ),
    # An EXPECTED degradation: a stage refused, and the stage plus the typed reason are on
    # the line above. Distinct from the arm below it, which is the whole of `DF-8-4-D`.
    "PipelineError": (
        "a pipeline stage did not complete, so NO verdict was produced (exit 1 is the "
        "reserved 'no verdict' code). The failing stage and the typed reason are named above "
        "— re-run once, and if it repeats report it with that line."
    ),
    "WorkspaceContainmentError": (
        "a write was refused because it would have left the `.argus/` workspace, and Argus "
        "writes nowhere else. Run the audit from the repository root you intend to audit; "
        "nothing outside the workspace was written."
    ),
    "CanonicalSerializationError": (
        "the run produced a payload that could not be canonically serialised, so nothing was "
        f"persisted and no verdict was produced. Re-run once; if it repeats, report it at "
        f"{ARGUS_ISSUE_TRACKER} with the typed line above."
    ),
    # ── `argus install-commands` (Story 12.7 / FR35) ─────────────────────────────
    # Its typed failures are OPERATOR errors, not defects, and they are enumerated for
    # exactly that reason: without their own arms they would inherit the base-`ValueError`
    # remedy below and an unregistered `--host` would be reported as a bug in Argus.
    "UnknownHostError": (
        "name a host this build registers, or omit --host to place the commands in every "
        "registered host whose configuration directory is detected. Nothing was written."
    ),
    "ContainmentError": (
        "the step refused a write that would have left the destination root, and Argus "
        "writes nowhere else. Check --dest (and whether the host's configuration directory "
        "is a symlink); nothing was written."
    ),
    "CommandInstallError": (
        "the command assets could not be placed as asked. The typed reason is above; "
        "correct it and re-run, or use --dry-run to see the whole plan without writing."
    ),
    # ── The three INTERNAL-DEFECT arms (`DF-8-4-D`) ───────────────────────────────
    # An unexpected exception inside a stage, a verdict the FR16 gate cannot produce, and any
    # OTHER `ValueError` reaching the CLI (Pydantic's `ValidationError` is the entry's own
    # stated example) are all one thing from the operator's side: Argus is broken. They are
    # NOT a fallthrough to a neighbour's remedy — this IS their remedy, and it is the only
    # honest one, because no change to the repository or the invocation can clear them.
    "UnexpectedStageError": _INTERNAL_DEFECT_NEXT_ACTION,
    "ShipReadinessError": _INTERNAL_DEFECT_NEXT_ACTION,
    "ValueError": _INTERNAL_DEFECT_NEXT_ACTION,
}


def render_ship_readiness(
    verdict: AuditVerdict,
    *,
    enabled_passes: tuple[str, ...] | list[str] = (),
    non_auditable_suffixes: tuple[str, ...] | set[str] | list[str] | None = None,
    degraded_conditions: tuple[object, ...] | list[object] = (),
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

    # Ingestion boundary 3-population disclosure (AC2 / FR37)
    held_out_count = scope.excluded_count if scope is not None else 0
    assessed_count = scope.assessed_total_count if scope is not None else verdict.total_count
    lines.append(
        f"  - {format_ingestion_boundary(non_auditable_suffixes, held_out_count=held_out_count, assessed_count=assessed_count)}"
    )

    if degraded_conditions:  # DF-10-4-B
        lines.append(
            f"  - Recorded degradation conditions: {len(degraded_conditions)} condition(s) recorded during analysis — check detailed findings for per-file remediation"
        )

    crit_set = getattr(verdict, "critical_subsystems", None)
    if crit_set is not None and getattr(crit_set, "heuristic_excluded_ineligible", None):
        ineligible_count = len(crit_set.heuristic_excluded_ineligible)
        if ineligible_count > 0:  # DF-8-3-A
            lines.append(
                f"  - Vacuous critical subsystem exclusions (DF-8-3-A): {ineligible_count} critical path(s) heuristically excluded as ungradable by construction"
            )

    if enabled_passes:
        # The OUTCOME, not the request (Story 12.2 / §A.4). It travels on the verdict —
        # the only channel that reaches both this caller and the report renderer — and
        # is `None` on every run that did not opt in.
        lines.append(
            f"  - {render_depth_meaning(enabled_passes, deep_pass=verdict.deep_pass)}"
        )

    next_steps: list[str] = []
    if verdict.verdict is Verdict.RELEASE_READY:
        next_steps.append(
            "repository satisfies all release gates — maintain coverage floor and monitor for blocking findings on future commits"
        )
    else:
        if verdict.verdict is Verdict.NOT_READY_FOR_RELEASE:
            next_steps.append(
                f"resolve the {verdict.blocking_finding_count} verdict-blocking finding(s) in named files before re-auditing"
            )
        elif verdict.verdict is Verdict.INSUFFICIENT_COVERAGE:
            if verdict.is_below_floor:
                next_steps.append(
                    f"deep coverage ratio {assessed_ratio} is below the 20% floor — add deep-auditable source definitions or tests for shallow modules"
                )
            elif assessed_ratio < RELEASE_READY_DEEP_THRESHOLD and scope is not None:
                next_steps.append(
                    f"assessed deep coverage ratio {assessed_ratio} is below the 80% threshold ({RELEASE_READY_DEEP_THRESHOLD}) — add deep-auditable tests or definitions for application modules"
                )

        if assessed_ratio < RELEASE_READY_DEEP_THRESHOLD and scope is None and not verdict.is_below_floor:
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

