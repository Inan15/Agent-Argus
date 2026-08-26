"""The OPT-IN LLM-backed deep-audit pass — the one seam through which source can leave.

Story 12.2 / FR36 (*an LLM-backed deep-audit pass, OFF by default, that never produces a
false deep claim*), NFR-S6 (*no source code, prompt or repository content leaves the
machine on the default path*), NFR-R1 (*honest degradation*), NFR-D2 (*zero-token
testable*), AR7 (*the LLM is reached ONLY via the injected ``LLMDispatchPort``*), AR10
(*a failure becomes a typed error → a recorded finding, never an uncaught raise*),
AR4 (*credits are an exact-numeric string, never a float*), FR21/FR22 (*spend flows
through the EXISTING ceiling*), NFR-M1 (≤1200-line files).

Verification area ArgusAgent-AUDIT (``TC-ArgusAgent-AUDIT-001-NN``).

Why this module exists, and why it lives HERE
---------------------------------------------
``argus/audit/`` is where the determinism quarantine already reasons: the whole
vocabulary of the quarantine — pure seam, allowed importer, forbidden surface — is
written in terms of ``argus.audit.*``. A new module here is INSIDE the fence rather than
a new place the fence has to learn about, and the fence is now DERIVED from the package's
real contents (``tests/test_no_web_imports.py``), so this module was covered by it before
it had a single line of behaviour. The alternatives were measured and rejected: putting
provider-adjacent orchestration in ``pipeline.py`` grows the module that has already
breached NFR-M1 once, and a fourth ``argus/pipeline*.py`` sibling trips ``DF-12-1-E``
(three siblings, no layering guard).

THE DEFERRED IMPORT, AND THE PROPERTY THAT LOOKS CONTRADICTORY AND IS NOT
------------------------------------------------------------------------
``argus/pipeline.py`` imports this module INSIDE the function that runs the pass, never
at module scope. That satisfies two requirements that read as opposites:

* ``argus.audit.deep_audit`` must be in the STATIC import closure from ``argus.cli`` —
  that is what makes FR36's ``wired`` disposition PROVEN rather than asserted
  (``TC-ArgusAgent-DOCS-001-34``). ``build_import_graph`` walks with ``ast.walk``, which
  descends into function bodies, so a function-local import is statically visible.
* ``argus.audit.deep_audit`` must be ABSENT from ``sys.modules`` after a DEFAULT run
  (NFR-S6 / ``TC-ArgusAgent-PIPELINE-001-10``). A function-local import in a branch that
  never executes never runs, so it is runtime-inert.

**The danger, stated so nobody walks into it:** the moment the import is deferred, the
zero-token quarantine goes green *for a reason that has nothing to do with safety* — it
is green because the code never ran. A one-directional import-absence gate over a
deferred path is a guard that passes by NOT EXECUTING. That is why the quarantine now
carries a POSITIVE CONTROL (``TC-ArgusAgent-PIPELINE-001-11``): with the opt-in ENABLED
the dispatch surface IS present, and with it absent the surface is NOT. Neither direction
is evidence without the other.

THE FABRICATED-RECORDING HAZARD (AC5.2) — WHY THIS MODULE REFUSES TO CONSTRUCT
------------------------------------------------------------------------------
``OpenLLMAdapter._dispatch_httpx`` contains a branch, taken when no endpoint is
configured, that RETURNS A SYNTHETIC ``LLMRecording`` (``input_tokens=10``,
``output_tokens=5``, ``finish_reason="stop"``) which is INDISTINGUISHABLE AT THE PORT
BOUNDARY from a real dispatch. Wiring that into the verdict path would manufacture deep
claims out of an unconfigured environment — precisely the false deep claim FR36 forbids
by name. This module therefore validates the provider configuration BEFORE dispatch and,
finding none, degrades immediately without ever constructing an adapter (§A.5 option 1).

The residual is REAL and is DISCLOSED, not hidden: the adapter still fabricates for any
OTHER caller. Filed as ``DF-12-2-B`` in ``deferred-work.md`` with an owner and a target.

HOW FAR THE SHIPPED ADAPTER ACTUALLY CARRIES THIS PASS (DF-12-2-D) — READ THIS BEFORE
TRUSTING THE WORD "WIRED"
--------------------------------------------------------------------------------------
``LLMRecording.structured_output`` is the field ``_dispatch_one`` requires before a claim
is even offered to :func:`_claim_is_ast_grounded`, and **neither**
``OpenLLMAdapter._dispatch_litellm`` **nor** ``._dispatch_httpx`` ever populates it: both
capture the response's usage, model id and finish reason and DISCARD the completion
content. Measured over a mocked transport at review iteration 1
(``TC-ArgusAgent-AUDIT-001-73``): a fully successful dispatch to a healthy provider comes
back with ``structured_output == ()``, so it degrades as ``empty-response`` before
grounding is ever consulted. **Through the shipped adapter, ``delivered_count`` is
therefore always 0; the delivered branch is reachable only through an injected port.**

Three things follow, and all three are load-bearing:

* **The gap is one field wide, and it is the ADAPTER'S, not this module's.**
  ``TC-ArgusAgent-AUDIT-001-74`` is the positive control: the same real adapter, the same
  mocked transport, the same real pipeline, with the discarded completion carried onto
  ``structured_output`` and NOTHING else changed — and the pass delivers. Everything wired
  downstream of the port works on real provider-shaped input.
* **The wiring is NOT vacuous, and this is the discrimination that shows it.** The egress
  path genuinely fires: the pipeline constructs the real adapter and the request really
  reaches the transport (asserted in ``-73``). What is unreachable is only the FAVOURABLE
  outcome. The failure polarity is the opposite of a false claim — the pass under-claims,
  never over-claims — so FR36's *"never produces a false deep claim"* is made
  unconditional by this gap rather than weakened by it.
* **Closing it is NOT a one-line change and must not be attempted as one.** There is no
  claim grammar and no response contract: ``OpenLLMAdapter._build_messages`` never asks
  the model for structured output. ``structured_output``'s own contract in ``ports.py`` is
  *claim/locator-shaped strings, NEVER raw prompt/response bytes* (NFR-S1, producer-side
  redaction), so tipping the completion text into it is a documented contract violation,
  not a fix — and ``tests/test_open_llm_adapter.py`` asserts ``structured_output == ()``
  for exactly that reason. Doing it honestly means a declared claim grammar, a prompt
  contract, a redacting parser, and a ``DEEP_PROMPT_TEMPLATE_VERSION`` bump (an AR5
  cache-key closure input). That is *full claim-grammar grounding*, and it is
  UNSCHEDULED — ⛔ NOT Story 6.2's, which is ``done`` (2026-06-29) and shipped a
  deterministic structural grounding fact instead. ``deep_audit.py`` and
  :func:`_claim_is_ast_grounded` name the same unscheduled work.

Filed as ``DF-12-2-D``, owner XAgent007 (Engineering Lead). It has NO target story:
the destination is a scope change, and pointing it at a `done` story is the defect
Story 17.5 corrected on 2026-08-26.

NFR-S1
------
Nothing this module records can carry prompt/response bytes, an endpoint or a key: the
degradation reasons are a CLOSED set of structured identifier tokens, and the outcome
model has no field that could hold source bytes.
"""

from __future__ import annotations

import os
from fractions import Fraction

from argus.audit.deep_audit import DeepAuditSeam
from argus.audit.grounding import is_deep_claim_grounded
from argus.audit.ports import (
    CheckpointDriftError,
    LLMDispatchError,
    LLMDispatchInput,
    LLMDispatchPort,
    LLMRecording,
)
from argus.cost.budget_governor import budget_config_from_budget
from argus.cost.exhaustion import CostUnit, project_halt_point
from argus.detectors.base import FindingDraft, build_recording
from argus.index.ast_index import AstIndexEntry
from argus.ledger.coverage_ledger import CoverageDepth, CoverageLedgerEntry, grade_entry
from argus.ledger.recording import Recording
from argus.verdict.verdict_gate import DeepPassOutcome

__all__ = [
    "DEEP_PROMPT_TEMPLATE_VERSION",
    "DEEP_UNIT_COST",
    "PROVIDER_ENDPOINT_VARIABLES",
    "RULE_DEGRADED_DEEP_READ",
    "DeepPassResult",
    "render_egress_disclosure",
    "resolve_provider_endpoint",
    "run_deep_pass",
]

# The declared prompt-template version this pass dispatches under (AR5 — it is folded
# into the cache-key closure alongside the captured checkpoint). A VERSION, not a prompt:
# no template text lives on the dispatch input (NFR-S1).
DEEP_PROMPT_TEMPLATE_VERSION = "argus-deep-v1"

# The deterministic int work-unit cost of ONE deep read (AR4 — never a float). It is a
# per-unit PROXY in the existing FR22 unit vocabulary, NOT a new ceiling, threshold or
# numeric default: the ceiling remains `--budget` and the admission decision remains the
# reused `project_halt_point` / `_coerce_breach` `>=`-is-a-breach comparison.
DEEP_UNIT_COST = 1

# The environment variables that configure a provider ENDPOINT. Read to answer one
# question only — *is a provider configured?* — and NEVER to decide whether the pass runs:
# that is `--deep-audit`'s job alone (AC2.3). With the flag absent this module is never
# imported, so no value here can cause a byte to leave the machine.
PROVIDER_ENDPOINT_VARIABLES: tuple[str, ...] = (
    "OPENAI_BASE_URL",
    "OLLAMA_HOST",
    "OLLAMA_URL",
)

# The rule-id prefix every degradation finding carries. The suffix is the typed reason.
# NAMED `..._DEEP_READ` rather than `..._DEEP_PASS` on purpose: bandit's B105 keys on the
# substring `PASS` in an assigned name and flags it as a hardcoded password. The wire VALUE
# is unchanged; only the Python identifier moved, so no rule id, report or persisted byte is
# affected. This module adds the only egress path in the product, and a reviewer reading its
# security scan should not have to triage a false positive to get there.
RULE_DEGRADED_DEEP_READ = "deep_pass_degraded"

# The CLOSED set of typed degradation reasons (NFR-S1 — structured identifiers only).
REASON_PROVIDER_UNCONFIGURED = "provider-unconfigured"
REASON_DISPATCH_FAILED = "dispatch-failed"
REASON_CHECKPOINT_DRIFT = "checkpoint-drift"
REASON_EMPTY_RESPONSE = "empty-response"
REASON_CLAIM_UNGROUNDED = "claim-ungrounded"
REASON_BUDGET_EXHAUSTED = "budget-exhausted"


class DeepPassResult:
    """The deep pass's effect on the fold: re-graded entries, findings, and the outcome.

    A plain container (the ``AuditResult`` precedent in ``pipeline.py``) rather than a
    frozen model: it carries live model objects onward within one process and is never
    serialized, so it needs no schema, no version and no canonical payload.
    """

    __slots__ = ("entries", "findings", "outcome")

    def __init__(
        self,
        *,
        entries: tuple[CoverageLedgerEntry, ...],
        findings: tuple[Recording, ...],
        outcome: DeepPassOutcome,
    ) -> None:
        self.entries = entries
        self.findings = findings
        self.outcome = outcome


def resolve_provider_endpoint() -> str | None:
    """Return the configured provider endpoint, or ``None`` when none is configured.

    THE GUARD IN FRONT OF THE FABRICATING BRANCH (AC5.2). ``OpenLLMAdapter`` defaults its
    API key to the literal ``"mock-key"`` and, when ``_api_base`` is falsy, RETURNS A
    SYNTHETIC RECORDING rather than failing — so "no endpoint" is exactly the condition
    under which the adapter manufactures depth. Answering the question HERE, before an
    adapter is constructed, is what keeps that branch unreachable from the verdict.

    Reads the environment for CONFIGURATION only. The environment is never an opt-in
    (AC2.3): with ``--deep-audit`` absent, this function is not called, this module is not
    imported, and no adapter exists to absorb anything.
    """
    for name in PROVIDER_ENDPOINT_VARIABLES:
        value = os.getenv(name)
        if value:
            return value
    return None


def render_egress_disclosure(
    *, target_count: int, endpoint: str | None, injected: bool = False
) -> str:
    """State WHAT will be transmitted and WHO receives it — BEFORE the first byte (AC2.5).

    Ordering is the requirement, not presence: this string is emitted before the pass
    dispatches anything, and the gate that proves it observes the disclosure stream at the
    moment ``dispatch`` is ENTERED. A check that the final stdout contains a provider name
    cannot tell "before" from "after" and would not be evidence.

    THREE recipients, because there are three, and naming the wrong one would be its own
    small dishonesty: an INJECTED port (the caller supplied the dispatcher, so Argus
    cannot say where the bytes go and says exactly that), a configured PROVIDER ENDPOINT,
    or NOTHING AT ALL. The last one still discloses: "nothing will be sent" is precisely
    what an operator who just asked for a deep read needs to hear.

    NFR-S1: the disclosure names the SCHEME AND HOST of the endpoint, never the full URL
    (which can carry a token in a query string or userinfo), never a key, never source.
    """
    what = (
        "repo-relative file paths, a tier hint and a prompt-template version, "
        "never file contents or secrets"
    )
    if injected:
        return (
            f"Deep audit: ENABLED. About to transmit AUDIT METADATA for {target_count} "
            f"file(s) — {what} — to an INJECTED dispatch port supplied by the caller. "
            "Where that port sends the data is the caller's to know, not Argus's."
        )
    if endpoint is None:
        return (
            "Deep audit: ENABLED, but NO provider endpoint is configured "
            f"({' / '.join(PROVIDER_ENDPOINT_VARIABLES)} are all unset), so NOTHING will "
            "be transmitted and no deep read will be performed. The pass will degrade and "
            "say so; it will not fabricate a deep claim."
        )
    return (
        f"Deep audit: ENABLED. About to transmit AUDIT METADATA for {target_count} file(s) "
        f"— {what} — to the provider at {_redact_endpoint(endpoint)}. "
        "This is the only path in Argus that sends anything off this machine."
    )


def _redact_endpoint(endpoint: str) -> str:
    """Reduce an endpoint to ``scheme://host[:port]`` (NFR-S1 — no path, no userinfo).

    A full endpoint URL can carry a bearer token in userinfo or a query string, so the
    disclosure names only the part an operator needs in order to know WHO is receiving
    the data. Total-safe: a malformed value degrades to a fixed marker, never a raise.
    """
    try:
        scheme, _, rest = endpoint.partition("://")
        if not rest:
            scheme, rest = "", endpoint
        authority = rest.split("/")[0]
        # Drop any `user:pass@` userinfo — never disclose a credential.
        authority = authority.rsplit("@", 1)[-1]
        return f"{scheme}://{authority}" if scheme else authority
    except (AttributeError, ValueError):  # pragma: no cover - defensive (AR10)
        return "<unparseable-endpoint>"


def _deep_targets(entries: tuple[CoverageLedgerEntry, ...]) -> tuple[str, ...]:
    """The files a deep read is owed for: exactly those claiming ``audited_deep``.

    Derived from the ledger the deterministic passes just produced, so the deep pass can
    never target a file the run does not claim depth for, and can never MISS one it does.
    A hand-maintained target list would drift from the grade it is supposed to justify.
    Sorted (AR11) so the dispatch order — and therefore the halt point — is deterministic.
    """
    return tuple(
        sorted(
            entry.file_path
            for entry in entries
            if entry.depth is CoverageDepth.AUDITED_DEEP
        )
    )


def _claim_is_ast_grounded(
    recording: LLMRecording, entry: AstIndexEntry | None
) -> bool:
    """Whether the returned claim VALIDATES against the repository AST (FR7).

    The strengthened disclosure says *"a deep read was dispatched for the file and its
    claim was validated against the repository AST"*. This is the predicate that makes
    that sentence true, so it asserts both halves:

    * the file exhibits the V1 grounding fact — ``is_deep_claim_grounded`` (≥1 real
      ``Definition``), REUSED by import from the pure FR7 validator, never re-derived; and
    * the model actually made a claim that RESOLVES against that file's own AST — the
      claim text must name the target path or one of the definitions the 1.4 index
      already extracted for it.

    A recording with no structured output has made no claim, and a claim naming a symbol
    that is not in the file is not validated. Both degrade; neither is treated as depth.
    Full claim-grammar grounding is UNSCHEDULED (``DF-12-2-D``, owner XAgent007) and
    was NOT delivered by Story 6.2; this is the V1 fact, and it is a real
    check rather than a rubber stamp.
    """
    if entry is None or not is_deep_claim_grounded(entry):
        return False
    if not recording.structured_output:
        return False
    known = {definition.name for definition in entry.definitions}
    known.add(entry.file_path)
    return any(
        any(token and token in claim for token in known)
        for claim in recording.structured_output
    )


def _degradation_finding(*, file_path: str, reason: str) -> Recording | None:
    """Mint the ADVISORY finding naming a file the deep pass could not read (FR13).

    ``advisory=True`` with ``depth_supported=None`` — so it is NOT verdict-blocking. That
    is deliberate and it is the honest choice: a provider that was unreachable is a fact
    about THE AUDIT, not a defect in the audited code, and routing it through FR16 row 2
    would print *"BLOCKED — 1 verdict-blocking finding(s) must be resolved"* about
    somebody else's clean repository. The run's honesty is carried instead by the COVERAGE
    DOWNGRADE (the file loses the ``audited_deep`` grade it did not earn), which moves the
    ratio the FR16 table already reads — so a failed deep pass cannot yield
    ``RELEASE_READY``, and it does so without a single row, threshold or mapping moving.

    Returns ``None`` if a verifiable locator cannot be built (FR13 locator-or-reject:
    rejected, never emitted as a locator-less finding).
    """
    try:
        return build_recording(
            FindingDraft(
                file_path=file_path,
                start_line=1,
                end_line=1,
                rule_id=f"{RULE_DEGRADED_DEEP_READ}:{reason}",
                advisory=True,
            ),
            depth_supported=None,
            claim_present=False,
        )
    except ValueError:
        return None


def _downgrade(entry: CoverageLedgerEntry) -> CoverageLedgerEntry:
    """Re-grade a file the deep pass could not read (AC5.4 — downgrade, never delete).

    REUSES the existing FR6/FR7 honesty keystone verbatim: ``grade_entry`` with
    ``claim_present=False`` records a proposed ``AUDITED_DEEP`` as ``AUDITED_SHALLOW``
    (*silence → shallow*). No new grading rule, no new depth state, no new threshold —
    the deep read's silence is handled by the same mechanism the FR7 validator's silence
    already is.

    The file STAYS IN THE DENOMINATOR at the depth it actually earned. Dropping it would
    inflate the ratio by hiding what was never examined, which is the failure mode FR37's
    *"names what was never examined"* principle exists to prevent.
    """
    return grade_entry(
        file_path=entry.file_path,
        proposed_depth=CoverageDepth.AUDITED_DEEP,
        claim_present=False,
        recording_ids=entry.recording_ids,
        partition_id=entry.partition_id,
    )


def _sum_credits(values: tuple[str, ...]) -> str:
    """Sum exact-numeric credit STRINGS into one exact-numeric string (AR4 — no float).

    ``Fraction`` arithmetic end to end: a float anywhere on this path is a defect, and the
    canonical serializer raises on a float leaf. A malformed value is treated as zero
    rather than raising — a provider's cost metadata must never be able to fail an audit
    that otherwise completed (AR10).
    """
    total = Fraction(0)
    for value in values:
        try:
            total += Fraction(value)
        except (TypeError, ValueError, ZeroDivisionError):
            continue
    return str(total)


def run_deep_pass(
    *,
    entries: tuple[CoverageLedgerEntry, ...],
    index_entries: tuple[AstIndexEntry, ...],
    budget: int,
    spent_credits: int = 0,
    port: LLMDispatchPort | None = None,
    disclose: object = None,
) -> DeepPassResult:
    """Run the opt-in deep pass over the files this run claims ``audited_deep`` for.

    Called ONLY when the operator passed ``--deep-audit`` (FR36 — off by default,
    always). Returns the re-graded ledger entries, the degradation findings, and the
    :class:`DeepPassOutcome` the disclosure and the verdict carry.

    *port* is the INJECTED :class:`~argus.audit.ports.LLMDispatchPort` (AR7). Tests pass a
    ``FakeDispatch`` and consume zero LLM tokens (NFR-D2). When it is ``None`` a live
    adapter is constructed — but ONLY if a provider endpoint is actually configured; with
    none, the pass degrades without constructing anything (AC5.2).

    *disclose* is an optional one-argument callable receiving the egress disclosure
    BEFORE the first dispatch (AC2.5). The pipeline passes the CLI's stderr writer.

    *budget* / *spent_credits* fund the pass from the EXISTING FR21/FR22 ceiling: the
    remaining headroom is ``budget - spent_credits`` and the admission decision is the
    reused :func:`project_halt_point`. No new ceiling, no new threshold, no new module.

    AR10: no failure escapes. Every typed dispatch error, every malformed response and
    every ungrounded claim becomes a recorded finding + a coverage downgrade.
    """
    index_by_path = {entry.file_path: entry for entry in index_entries}
    targets = _deep_targets(entries)

    # ── Spend: the EXISTING ceiling, projected over the deep pass's own units. The
    # headroom is what the deterministic passes left; `budget == 0` stays first-class
    # "no ceiling" (OI3) and admits everything, exactly as it does everywhere else.
    headroom = 0 if budget == 0 else max(0, budget - spent_credits)
    projection = project_halt_point(
        tuple(CostUnit(path=path, cost=DEEP_UNIT_COST) for path in targets),
        config=budget_config_from_budget(headroom),
    )
    assessed = tuple(path for path in targets if path in set(projection.assessed_paths))
    exhausted = tuple(path for path in targets if path in set(projection.skipped_paths))

    endpoint = resolve_provider_endpoint()
    if callable(disclose):
        disclose(
            render_egress_disclosure(
                target_count=len(assessed),
                endpoint=endpoint,
                injected=port is not None,
            )
        )

    degraded: dict[str, str] = {path: REASON_BUDGET_EXHAUSTED for path in exhausted}
    delivered: list[str] = []
    credits: list[str] = []

    dispatcher = _resolve_dispatcher(port=port, endpoint=endpoint)
    if dispatcher is None:
        for path in assessed:
            degraded[path] = REASON_PROVIDER_UNCONFIGURED
    else:
        for path in assessed:
            reason, recording = _dispatch_one(dispatcher, path=path)
            if recording is not None:
                credits.append(recording.credits_used)
            if reason is not None:
                degraded[path] = reason
            elif recording is None or not _claim_is_ast_grounded(
                recording, index_by_path.get(path)
            ):
                # A successful dispatch whose claim does not resolve against the file's
                # own AST is NOT depth. This is the branch a plausible-sounding model
                # lands in, and it is the difference between the strengthened sentence
                # being true and being a guess.
                degraded[path] = REASON_CLAIM_UNGROUNDED
            else:
                delivered.append(path)

    findings = tuple(
        finding
        for finding in (
            _degradation_finding(file_path=path, reason=degraded[path])
            for path in sorted(degraded)
        )
        if finding is not None
    )
    regraded = tuple(
        _downgrade(entry) if entry.file_path in degraded else entry for entry in entries
    )
    outcome = DeepPassOutcome(
        requested_count=len(targets),
        delivered_count=len(delivered),
        degraded_count=len(degraded),
        reasons=tuple(sorted(set(degraded.values()))),
        halted_on_exhaustion=projection.halted_on_exhaustion,
        credits_used=_sum_credits(tuple(credits)),
    )
    return DeepPassResult(entries=regraded, findings=findings, outcome=outcome)


def _resolve_dispatcher(
    *, port: LLMDispatchPort | None, endpoint: str | None
) -> DeepAuditSeam | None:
    """Wrap the injected port in the PURE :class:`DeepAuditSeam`, or refuse (AC5.2).

    The seam is the Epic-6 consumer side of the determinism quarantine and it is what
    this story wires: it holds the port TYPE and never a concrete adapter. An injected
    port is used as given. With no port and NO configured endpoint the answer is ``None``
    — REFUSE TO CONSTRUCT — because constructing ``OpenLLMAdapter`` in that state yields
    an object whose ``dispatch`` fabricates a recording that is indistinguishable from a
    real one at the port boundary.

    The adapter import is function-local: it pulls ``httpx``, and nothing may drag an
    HTTP client onto the default path (NFR-S6).
    """
    if port is not None:
        return DeepAuditSeam(port=port)
    if endpoint is None:
        return None
    from argus.audit.open_llm_adapter import OpenLLMAdapter

    return DeepAuditSeam(port=OpenLLMAdapter(provider_id="open-llm", use_litellm=False))


def _dispatch_one(
    dispatcher: DeepAuditSeam, *, path: str
) -> tuple[str | None, LLMRecording | None]:
    """Dispatch ONE deep read, mapping every failure to a typed reason (AR10 / AC5.1).

    Returns ``(reason, recording)``: a ``reason`` of ``None`` means the dispatch itself
    succeeded. NOTHING propagates out of here — the port contract already says an
    implementation must never raise an uncaught exception out of ``dispatch``, and this
    is the belt to that braces: a third-party adapter that breaks the contract degrades
    the pass instead of crashing an audit that had already completed its work.

    The reason vocabulary is CLOSED and derives from the typed error surface in
    ``argus/audit/ports.py``: ``CheckpointDriftError`` is named specifically because it
    means something an operator can act on (the model changed mid-run), and every other
    ``LLMDispatchError`` — transport, HTTP status, provider-chain exhaustion — maps to
    ``dispatch-failed``. A future ``LLMDispatchError`` subclass is therefore HANDLED by
    construction rather than silently unhandled, which is what AC5.1 asks for.
    """
    try:
        recording = dispatcher.run(
            LLMDispatchInput(
                target_path=path,
                prompt_template_version=DEEP_PROMPT_TEMPLATE_VERSION,
            )
        )
    except CheckpointDriftError:
        return REASON_CHECKPOINT_DRIFT, None
    except LLMDispatchError:
        return REASON_DISPATCH_FAILED, None
    except Exception:  # noqa: BLE001 — AR10: a contract-breaking port degrades, never crashes
        return REASON_DISPATCH_FAILED, None
    if not isinstance(recording, LLMRecording) or not recording.structured_output:
        return REASON_EMPTY_RESPONSE, recording if isinstance(recording, LLMRecording) else None
    return None, recording
