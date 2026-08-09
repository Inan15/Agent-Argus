"""PURE value contract of the dogfood PROOF-RUN — the five frozen result dataclasses.

Extracted VERBATIM from ``argus/dogfood/proof_run.py`` by Story 9.2 (ledger item
``DF-8-5-D``), whose ``target_story`` is *"the first story that edits
``argus/dogfood/proof_run.py`` for any reason"*. The move is a PURE RELOCATION: not one
character of a dataclass body, field default, docstring or property was changed, and
``proof_run.py`` re-exports every name, so every existing
``from argus.dogfood.proof_run import ...`` call site keeps working unchanged
(``TC-ArgusAgent-DOGFOOD-001-37`` enumerates ``proof_run.__all__`` and proves it).

AR8 — this module is PURE and STRUCTURALLY so, not merely narrated as such: it holds
value types only. It performs no I/O, reads no clock, spawns no subprocess, imports no
impure ArgusAgent module, and imports nothing from ``proof_run`` (which is the impure
shell) — so the pure/impure line the 7.2 docstring described in prose is now a module
boundary the import graph enforces.

NFR-S1 — nothing here can carry a source byte or a secret value: every field is a
provenance token, an ``int`` count, a ``bool``, a repo-relative locator, or an exact
``Fraction`` (AR4 — never a ``float``).

Why a separate module rather than a bigger one: ``proof_run.py`` carried five
responsibilities against the NFR-M1 1200-line ceiling. Note for the record (Story 9.2 /
§G): the ceiling did NOT force this extraction — the DF-8-5-A version fix is +3 lines net
and left the module at 1199/1200. The LEDGER forced it, and the fact that Story 9.2 is
the last story in the plan, so a deferral here is a deferral to nobody.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from argus.precision.replay_harness import MatchKey

__all__ = [
    "AdjudicationRow",
    "CostSummary",
    "ScopeDisclosure",
    "CriticalClauseDisclosure",
    "DogfoodProofRun",
]


@dataclass(frozen=True)
class AdjudicationRow:
    """One adjudication-ready finding CLASS — the 6.6 match-key shape (NFR-S1).

    The REAL dogfood emits thousands of findings; a human TP/FP adjudication tags each
    finding CLASS (the 6.6 ``finding_match_key`` identity ``(rule_id, verdict_eligible,
    advisory)``), not each of thousands of locator instances. This row is one such class:
    the ``rule_id`` provenance, whether the class is verdict-eligible (blocking) vs
    advisory, the emitted ``count``, and up to :data:`_SAMPLE_LOCATOR_CAP` representative
    repo-relative POSIX ``sample_locators`` so a human can inspect the class on the real
    repo. Carries NO source byte / secret value — only the rule-id token, two booleans,
    an int count, and repo-relative locators (NFR-S1). ``adjudication`` is the empty
    string placeholder the human fills with ``TP`` / ``FP`` (7.2 leaves it UN-tagged —
    the adjudication is the human step, OUT of scope here).
    """

    rule_id: str
    verdict_eligible: bool
    advisory: bool
    count: int
    sample_locators: tuple[str, ...]
    adjudication: str = ""

    @property
    def match_key(self) -> MatchKey:
        """The 6.6 ``finding_match_key`` identity ``(rule_id, verdict_eligible, advisory)``."""
        return (self.rule_id, self.verdict_eligible, self.advisory)


@dataclass(frozen=True)
class CostSummary:
    """The within-ceiling + 3.2-halt cost accounting for the dogfood run (AR4).

    REUSES the 3.1 ``account_spend`` over the V1 deterministic contribution recipe (the
    SAME recipe ``pipeline._build_cost_ledger`` folds — no fork). ``total_credits`` is the
    whole-repo V1 zero-token total; ``ceiling`` is ``$X`` = 843; ``fits_within_ceiling``
    asserts the run does NOT breach ``$X`` (``ceiling_reached is False``);
    ``breaches_below_total`` DEMONSTRATES the 3.2 halt (a ceiling one credit below the
    total breaches). All ``int`` credits / a ``Fraction`` baseline ratio — never float.
    """

    total_credits: int
    ceiling: int
    build_cost_proxy: int
    baseline_ratio: Fraction | str
    fits_within_ceiling: bool
    breaches_below_total: bool
    # The CEILING HONESTY PAIR (Story 8.5 / AC1 / D7). ``ceiling`` above is the FROZEN
    # historical execution parameter the run was actually executed under; the 7.1
    # generator re-sizes ``$X`` from the LIVE tree on every derivation and has drifted
    # away from it. Recording only one of the two lets the proof artifact and the budget
    # artifact — both published by the same change — disagree about what "the 7.1
    # empirical ceiling" is. Both are recorded, with a fit verdict for EACH. Defaults so
    # every existing construction site keeps working (NFR-M2 additive-only).
    # ``None`` means NO live sizing was supplied — never ``0``, which is a legitimate
    # sizing for an empty tree; collapsing the two would publish "not supplied" about a
    # derivation that WAS supplied a zero ceiling (the same ambiguity
    # :class:`CriticalClauseDisclosure.set_retrieved` exists to refuse).
    live_sized_ceiling: int | None = None
    fits_within_live_sized_ceiling: bool = False


@dataclass(frozen=True)
class ScopeDisclosure:
    """The verdict's DISCLOSED assessment-scope narrowing, flattened for render (PURE).

    A value copy of the frozen ``verdict.CoverageScope`` fields the proof artifact must
    print (Story 8.5 / AC1 — the ASSESSED population the row was computed from, not only
    the whole-ledger numbers), kept a plain dataclass so :class:`DogfoodProofRun` stays a
    pure value holder. ``assessed_deep_ratio`` is an exact ``Fraction`` (AR4). ``None``
    on the run means ``coverage_scope is None``, i.e. **no narrowing occurred** — which
    the renderer states EXPLICITLY rather than by omission.
    """

    scope_id: str
    excluded_reason: str
    assessed_deep_count: int
    assessed_total_count: int
    assessed_deep_ratio: Fraction
    excluded_count: int


@dataclass(frozen=True)
class CriticalClauseDisclosure:
    """The FR4/FR16 critical-subsystem clause state the gate keyed on (PURE; boundary B3).

    Epic 8 LOOSENS the critical gate twice (the DR-5 eligibility filter, the
    ``application`` scope default) and nothing guards the PRD-fatal
    false-``RELEASE_READY`` direction (inversion F1). A green verdict whose clause held
    because the critical set was **EMPTY** is a vacuously satisfied gate, and that must
    be VISIBLE, never implied.

    ``all_deep`` / ``not_deep`` come from the verdict and are always present.
    ``set_retrieved`` records whether the run's persisted :class:`CriticalSubsystemSet`
    was actually read back; when ``False`` the remaining counters are meaningless and the
    renderer says so — reporting ``set_size = 0`` for "not retrieved" would fabricate the
    very vacuous-gate claim this disclosure exists to make falsifiable.
    ``retrieval_note`` carries the MEASURED reason it could not be read, so an unread set
    is not merely unread but explained.
    """

    all_deep: bool
    not_deep: tuple[str, ...] = ()
    set_retrieved: bool = False
    set_size: int = 0
    excluded_ineligible_count: int = 0
    designated_but_unmatched: tuple[str, ...] = ()
    retrieval_note: str = ""

    @property
    def vacuously_satisfied(self) -> bool:
        """Whether the clause was satisfied by an EMPTY critical set (a vacuous gate)."""
        return self.set_retrieved and self.all_deep and self.set_size == 0


@dataclass(frozen=True)
class DogfoodProofRun:
    """The whole 7.2 dogfood-proof result (PURE value holder — the render input).

    Aggregates: the audited ``commit_descriptor`` provenance, the 7.1 partition/budget
    plan (CONSUMED), the run verdict token + exit code + deep-ratio + blocking count, the
    cost summary (within-ceiling + halt), the adjudication-ready finding rows, the SIGNED
    bundle's locator + content hash, the integrity-report consistency, the honest
    ``grade`` flag, and the PROVISIONAL gate status string. PURE / value-free — only
    provenance / counts / rule-ids / locators / a ``Fraction`` cross a byte boundary
    (NFR-S1). ``protocol_cleared`` is NOT a field here and is NEVER flipped (OI1).
    """

    commit_descriptor: str
    source_file_count: int
    total_loc: int
    unit_count: int
    verdict: str
    exit_code: int
    deep_ratio: Fraction
    blocking_finding_count: int
    total_finding_count: int
    cost: CostSummary
    adjudication: tuple[AdjudicationRow, ...]
    bundle_locator: str
    bundle_content_hash: str
    bundle_byte_length: int
    integrity_consistent: bool
    grade: str
    gate_status: str
    # ── DR-3 row + input disclosure (Story 8.5 / AC1) — all defaulted (NFR-M2) ──
    # The LITERAL DecisionRow value the gate disclosed, never a re-derivation from the
    # verdict token: rows 1 and 4 both render INSUFFICIENT_COVERAGE / exit 3, so a
    # consumer that infers the row from the token states a falsehood for one of them.
    # Empty string ONLY for a pre-amendment payload that never disclosed a row.
    decision_row: str = ""
    deep_count: int = 0
    total_count: int = 0
    scope: ScopeDisclosure | None = None
    critical: CriticalClauseDisclosure | None = None
    # The enumeration SUBJECT this run actually audited (Story 8.5 / AC2) — recorded
    # from the module-level enumeration defaults BOTH impure call sites pass, so the
    # artifact cannot name a tree the run did not read.
    scope_prefix: str = ""
    exclude_prefixes: tuple[str, ...] = ()
    # What the enumerator MEASURABLY held out: the subset of ``exclude_prefixes`` that
    # matched >=1 tracked file (:func:`effective_exclusions`). Rendering the CONFIGURED set
    # asserts a held-out sub-tree a stale/renamed prefix may never have matched.
    effective_exclude_prefixes: tuple[str, ...] = ()
