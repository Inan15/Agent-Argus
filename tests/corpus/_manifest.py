"""The VALIDATION-SET MANIFEST — the one named place a corpus member exists (Story 13.1 / AC3a).

Verification area ``TC-ArgusAgent-PRECISION-001-21``..``-30`` (``tests/test_validation_corpus.py``).
Drivers: the PRD's **≥80% finding-precision** externalization gate over *"N ≈ 5–10 **real**
XAgents repos"* (`prd.md:196`) judged *"genuinely real by an **independent senior engineer**"*
(`prd.md:191`); **FR13** (every finding carries ≥1 verifiable locator — the shape 13.2
adjudicates); **NFR-S1** (no source byte in any artifact — metadata and locators only);
**AR4** (no float in any recorded figure); **NFR-M1** (≤1200-line modules).

Why this module exists (DN-1 — the decision Story 13.1 was created to take)
--------------------------------------------------------------------------
The project carried **two corpora and never reconciled them**. `precision-validation-protocol.md`
§5 fixed the gate at *"N ≥ 5 distinct labeled **planted-defect cartridges**"*; the PRD fixed it at
*"N ≈ 5–10 **real** repositories"*. They are not two opinions about one quantity — they are two
different quantities:

===================  ==========================================  ==============================
\\                    Cartridge corpus (``tests/cartridges/``)     Repository corpus (THIS module)
===================  ==========================================  ==============================
Measures             **Recall** — did we find what we hid?        **Precision** — is a blocking
                                                                  finding on unplanted code real?
Denominator          Golden keys the team authored                Findings the tool emitted on
                                                                  code nobody planted
Gates externalizing  **No**                                       **Yes** — the ≥80% gate
Status               Delivered, CI-asserted (FR20)                **Built here; empty of eligible
                                                                  members until 13.2 adjudicates**
===================  ==========================================  ==============================

**Story 13.1 decided the PRD governs** (2026-08-16). The alternative — letting the protocol
govern and amending the PRD down to cartridges — would make the externalization gate clearable
by a corpus the team authored, planted and wrote the answers to. That is the "measure your own
homework" failure Epic 13 exists to remove. The cartridges are **not demoted**: they are
re-labelled as the **recall** instrument they always were (FR20), and they keep doing exactly
what they do today.

What a member IS, and what it is NOT (DN-4)
--------------------------------------------
A member is **metadata + a pin**: a repository URL, a commit sha, a licence, a language and a
provenance. It is **never vendored source**. No third-party source byte is committed to this
repository and none reaches any artifact (NFR-S1) — exactly as `minions-dogfood-proof.md`
already does for `argus/`, carrying locators and counts and no bytes. Staging a member is an
**operator act** performed at its pinned sha, behind the AC3b ratification; nothing in this
module or its guards fetches anything (DN-5).

"Usage is not evidence" is a SCHEMA property here, not a promise (AC4)
----------------------------------------------------------------------
The PRD's guard reads *"**usage is not evidence** — adoption cannot advance the precision gate,
only adjudicated findings can"* (`prd.md:159`). A member may be **sourced** from anywhere,
including from public users — that is recorded in :data:`SOURCING_RULE`. But a member counts
toward **N** only once its findings are adjudicated by the named human in Story 13.2. So install
counts, run counts, stars and downloads are not merely unused: :data:`MANIFEST_FIELDS` is a
**closed** schema and :data:`NEVER_ELIGIBLE_FIELDS` is the enumerated ban, both asserted by
``-22``. Adding ``stars`` to the row would break no other test in this repository; it breaks that
one, which is the point.

One floor, two populations (DN-3)
----------------------------------
:func:`validation_floor_n` **resolves** the 6.5 ``VALIDATION_SET_FLOOR_N = 5`` rather than
restating it. Two floor constants is how two corpora happened in the first place, and
``AI-E9-7`` forbids publishing a prose copy of a pinned constant. ``N`` is **LOCKED at 5**
(protocol §7 / OI1): a corpus that turns out to be hard to build is a fact to record, never a
reason to move a number.

The registry is resolved through the ONE declared lazy edge
------------------------------------------------------------
``tests/`` is **repository-only and absent from the built distribution** (``DF-9-2-A``), so this
module reaches the cartridge floor through
``argus.precision.replay_harness.registry_module()`` — the single declared impure edge — and
never through a module-level import or a second path of its own.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "CorpusMemberSpec",
    "UnregisteredCorpusMember",
    "VALIDATION_CORPUS",
    "PROVENANCE_VALUES",
    "MANIFEST_FIELDS",
    "NEVER_ELIGIBLE_FIELDS",
    "AST_INELIGIBLE_LANGUAGES",
    "AST_INELIGIBILITY_REASONS",
    "SOURCING_RULE",
    "member",
    "eligible_members",
    "eligible_member_count",
    "validation_floor_n",
    "meets_validation_floor",
    "validation_set_status",
]


#: The provenance vocabulary. ``independent`` is the ONLY value that can support eligibility —
#: the other two exist so the corpus records what it excluded and why, rather than being silent
#: about it (the failure mode that let a self-audit become "the corpus" in the first place).
PROVENANCE_VALUES: tuple[str, ...] = ("independent", "self", "superseded")

#: The CLOSED schema (AC4). The dataclass below must carry exactly these fields; ``-22`` checks
#: it in both directions, so a field cannot be added to the row without being admitted here.
MANIFEST_FIELDS: tuple[str, ...] = (
    "member_id",
    "repository_url",
    "commit_sha",
    "licence",
    "primary_language",
    "provenance",
    "eligible_for_n",
    "ineligible_reason",
)

#: Fields that may NEVER exist on a member, enumerated so the ban is testable rather than
#: remembered (AC4 / `prd.md:159`). Adoption is not evidence; only adjudicated findings are.
NEVER_ELIGIBLE_FIELDS: frozenset[str] = frozenset(
    {
        "stars", "forks", "watchers", "downloads", "installs", "install_count",
        "users", "user_count", "adoption", "usage", "run_count", "runs",
        "popularity", "traffic", "clones", "dependents",
    }
)

#: How a member may be SOURCED — recorded because AC4 requires the rule written down, not only
#: obeyed. Sourcing is unrestricted; ADMISSION is what is restricted.
SOURCING_RULE = (
    "A candidate repository may be sourced from anywhere — including from public users of the "
    "tool, from a maintainer's own reading, or from a public index — and the sourcing channel "
    "is not recorded as evidence because it is not evidence. A member contributes to N ONLY "
    "once every blocking finding Argus emitted on it has been adjudicated TP or FP by the "
    "named human adjudicator under precision-validation-protocol.md §2/§4 (Story 13.2). "
    "Adoption, popularity and run counts can never advance the gate: they are not fields of "
    "this schema, and NEVER_ELIGIBLE_FIELDS makes adding one a failure rather than a silent "
    "extension."
)

#: DN-6 / ``DF-10-2-A``, decided here as a CORPUS-ELIGIBILITY rule rather than as a detector
#: story. These languages parse cleanly (``ast_eligible=True``, ``parse_failed=False``) but
#: cannot yield the ``audited_deep`` grounding the ≥80% gate is about, so a member whose primary
#: language is one of them cannot silently count toward N.
#:
#: MEASURED 2026-08-16 by execution against the shipped extractor (``argus/index/ast_index.py``)
#: at the grammar versions this tree pins — NOT taken from the ledger, which states the weaker
#: and partly INACCURATE claim that all four extract zero definitions. Rust does not: it extracts
#: structs and misses only functions. The reasons below are the measured mechanism in each case,
#: and ``-30`` re-measures them so this table cannot rot into folklore.
AST_INELIGIBILITY_REASONS: dict[str, str] = {
    "c": (
        "MEASURED 0 definitions (tree-sitter-c 0.24.2). The node type `function_definition` IS "
        "in the extractor's vocabulary, but a C `function_definition` carries its name under a "
        "`declarator` field rather than a `name` field, and `_node_name` reads `name` only — so "
        "every definition is matched and then dropped for having no name."
    ),
    "cpp": (
        "MEASURED 0 definitions (tree-sitter-cpp 0.23.4). Same `declarator`-not-`name` mechanism "
        "as C for functions; classes are `class_specifier`, which is not in the vocabulary at all."
    ),
    "ruby": (
        "MEASURED 0 definitions (tree-sitter-ruby 0.23.1). A vocabulary gap: Ruby's nodes are "
        "`method` and `class`, while the extractor knows `method_definition`/`method_declaration` "
        "and `class_definition`/`class_declaration`. Nothing matches."
    ),
    "rust": (
        "MEASURED 1 of 2 definitions (tree-sitter-rust 0.24.2) — the ledger's 'zero definitions' "
        "is INACCURATE for Rust and is corrected here. `struct_item` is in the vocabulary and "
        "extracts; FUNCTIONS do not, because the vocabulary entry is `fn_item`, which is not a "
        "node type tree-sitter-rust emits — the real one is `function_item`, so the entry matches "
        "nothing. Rust is nonetheless ineligible: a corpus member whose FUNCTIONS can never be "
        "grounded cannot support the audited_deep claims the precision gate is about, and "
        "admitting it on the strength of struct extraction alone would be exactly the "
        "over-claim OI1 forbids."
    ),
}

#: The derived ban set — never restated, so the set and its reasons cannot disagree.
AST_INELIGIBLE_LANGUAGES: frozenset[str] = frozenset(AST_INELIGIBILITY_REASONS)

#: A 40-character lowercase hex sha. DN-4 pins by commit; an unpinned member is not reproducible
#: and therefore cannot be adjudicated (protocol §4's determinism precondition).
_SHA_LENGTH = 40
_SHA_ALPHABET = frozenset("0123456789abcdef")


class UnregisteredCorpusMember(LookupError):
    """Raised when a member id is not in the manifest (the ``DF-10-4-E`` dispatch shape).

    The manifest is the one named place: *"a member that is not in it is not in N"*. So a
    lookup miss is an ERROR that names itself and the registered set, never ``None`` and never
    a default row — the same exhaustive-dispatch discipline 12.5's ``_downgrade_sentence`` and
    12.8/AC4 take, for the same reason.
    """


def _known_languages() -> frozenset[str]:
    """The shipped language vocabulary, IMPORTED from the module that owns it (AI-E9-7).

    ``argus/shared/source_languages.py`` exists precisely because this mapping used to live in
    three places with three different contents. A manifest that hand-listed its own language
    tokens would be the fourth.
    """
    from argus.shared.source_languages import LANGUAGE_BY_SUFFIX

    return frozenset(LANGUAGE_BY_SUFFIX.values())


@dataclass(frozen=True)
class CorpusMemberSpec:
    """One validation-set member — metadata and a pin, never source bytes (DN-4 / NFR-S1).

    - ``member_id`` — the stable local name; it is NOT a cartridge id (DN-2: different corpus).
    - ``repository_url`` / ``commit_sha`` — where it is and exactly which tree, so a run over it
      is reproducible and therefore adjudicable (protocol §4).
    - ``licence`` — recorded so the operator's ratification is an informed one (AC3b).
    - ``primary_language`` — from the shipped vocabulary; gates DN-6 eligibility.
    - ``provenance`` — ``independent`` | ``self`` | ``superseded``.
    - ``eligible_for_n`` — whether this member may count toward the locked floor.
    - ``ineligible_reason`` — REQUIRED whenever ``eligible_for_n`` is ``False``. An exclusion
      without a reason is an oversight wearing a decision's clothes.

    The row **validates itself at construction**, not at read time, so a call site cannot build
    an invalid member and hope nobody folds it.
    """

    member_id: str
    repository_url: str
    commit_sha: str
    licence: str
    primary_language: str
    provenance: str
    eligible_for_n: bool
    ineligible_reason: str | None = None

    def __post_init__(self) -> None:
        if self.provenance not in PROVENANCE_VALUES:
            raise ValueError(
                f"{self.member_id!r}: unregistered provenance {self.provenance!r}; the "
                f"vocabulary is {PROVENANCE_VALUES}. An unregistered value RAISES rather than "
                "being tolerated (DF-10-4-E)."
            )
        if self.primary_language not in _known_languages():
            raise ValueError(
                f"{self.member_id!r}: unregistered language {self.primary_language!r}. The "
                "vocabulary is argus/shared/source_languages.py::LANGUAGE_BY_SUFFIX — a "
                "language Argus cannot even enumerate cannot be a corpus member."
            )

        if not self.eligible_for_n:
            if not (self.ineligible_reason or "").strip():
                raise ValueError(
                    f"{self.member_id!r}: eligible_for_n is False with no ineligible_reason. "
                    "Record WHY it is excluded — an exclusion without a reason is an oversight "
                    "wearing a decision's clothes."
                )
            return

        # From here on the member CLAIMS to count toward the locked floor. Every condition
        # below is a way a corpus could be quietly faked by editing one field.
        if self.provenance != "independent":
            raise ValueError(
                f"{self.member_id!r}: provenance {self.provenance!r} can never be eligible for "
                "N — only 'independent' can. Story 8.5 turned the dogfood into a self-audit and "
                "the record calls the result 'a materially weaker evidence class … not "
                "independent corroboration of anything'; a member cannot be promoted out of "
                "that by flipping a boolean."
            )
        sha = self.commit_sha
        if len(sha) != _SHA_LENGTH or not set(sha) <= _SHA_ALPHABET:
            raise ValueError(
                f"{self.member_id!r}: commit_sha {sha!r} is not a full {_SHA_LENGTH}-character "
                "lowercase hex sha. DN-4 pins by commit and fetches; an unpinned member is not "
                "byte-reproducible, and protocol §4 makes reproducibility the precondition for "
                "any adjudication being valid."
            )
        if self.primary_language in AST_INELIGIBLE_LANGUAGES:
            raise ValueError(
                f"{self.member_id!r}: primary_language {self.primary_language!r} cannot support "
                f"audited_deep grounding, so it cannot count toward N. "
                f"{AST_INELIGIBILITY_REASONS[self.primary_language]} (DN-6 / DF-10-2-A)"
            )
        if (self.ineligible_reason or "").strip():
            raise ValueError(
                f"{self.member_id!r}: an ELIGIBLE member carries an ineligible_reason "
                f"({self.ineligible_reason!r}). One of the two is wrong, and guessing which "
                "is how a corpus acquires a member nobody decided to admit."
            )


# ─────────────────────────────────────────────────────────────────────────────────────────────
# THE MANIFEST. A member that is not here is not in N.
#
# It holds ZERO eligible members today, and that is the honest state Story 13.1 hands to 13.2 —
# not an omission. AC3b (populating it to N ≥ 5 from independent repositories) is gated on one
# explicit operator ratification, because choosing which repositories are legitimate members and
# fetching third-party source are operator acts, not autonomous ones. Fabricating plausible
# repository names to make a count look met would be the worst available outcome in the story
# that defines the corpus.
#
# The two rows below are the RECORDED EXCLUSIONS AC3a requires to live in the manifest itself
# rather than in prose elsewhere. The third exclusion — the cartridges — is not a row at all:
# they are a different corpus measuring a different quantity (DN-2), and `-24` asserts in both
# directions that no cartridge id appears here.
# ─────────────────────────────────────────────────────────────────────────────────────────────
VALIDATION_CORPUS: tuple[CorpusMemberSpec, ...] = (
    CorpusMemberSpec(
        member_id="argus-self-audit",
        repository_url="https://github.com/XAgentsLabs007/ArgusAgent",
        commit_sha="bc55e361d46b1a33672d0214c7d8e1a97190d0dc",
        licence="proprietary — this repository",
        primary_language="python",
        provenance="self",
        eligible_for_n=False,
        ineligible_reason=(
            "SELF-AUTHORED. Story 8.5 re-derived the dogfood as an audit of `argus/` by "
            "`argus/`, and deferred-work.md records the measured collapse it caused: "
            "cross_partition 332 -> 2, hardcoded_secret 2289 -> 22, orphan_code 285 -> 77, "
            "2906 -> 101 findings, and the verdict itself moving from NOT_READY_FOR_RELEASE "
            "(exit 2) to RELEASE_READY (exit 0). The ledger calls it 'a materially weaker "
            "evidence class … not independent corroboration of anything'. A tool cannot clear "
            "an externalization gate by auditing itself, so this can never be eligible."
        ),
    ),
    CorpusMemberSpec(
        member_id="minions-story-7-2-superseded",
        repository_url="https://github.com/XAgentsLabs007/Minions",
        commit_sha="0000000000000000000000000000000000000000",
        licence="proprietary — XAgents internal",
        primary_language="python",
        provenance="superseded",
        eligible_for_n=False,
        ineligible_reason=(
            "NOT RE-DERIVABLE IN THIS REPOSITORY. The Story 7.2 run over the Minions platform "
            "repository is the only independent evidence this project ever produced (2906 "
            "findings), and it survives only as the preserved artifact "
            "minions-dogfood-proof-story-7-2-superseded.md; deferred-work.md:832-836 records "
            "that it 'can never be re-derived in this repository' because the Minions source is "
            "not here and the 2026-08-03 separation removed it. Preserved-but-unrepeatable "
            "evidence cannot be adjudicated under protocol §4, whose determinism precondition "
            "requires a byte-reproducible run. The pin is recorded as all-zero deliberately: "
            "there is no sha this repository can resolve, and inventing one would be a "
            "fabricated citation. This is why AC3 is a BUILD and not a re-run."
        ),
    ),
)


def member(member_id: str) -> CorpusMemberSpec:
    """Resolve a member by id, or RAISE naming the id and the registered set (``DF-10-4-E``)."""
    for spec in VALIDATION_CORPUS:
        if spec.member_id == member_id:
            return spec
    raise UnregisteredCorpusMember(
        f"{member_id!r} is not a validation-set member. The manifest is the one named place a "
        f"member exists, so this is an error rather than an absence. Registered: "
        f"{sorted(spec.member_id for spec in VALIDATION_CORPUS)}"
    )


def eligible_members() -> tuple[CorpusMemberSpec, ...]:
    """The members that may count toward the locked floor — a fold, never a transcription."""
    return tuple(spec for spec in VALIDATION_CORPUS if spec.eligible_for_n)


def eligible_member_count() -> int:
    """**N** — the derived validation-set count the ≥80% gate is measured over (AC3a)."""
    return len(eligible_members())


def _registry() -> Any:
    """The 6.5 registry, through the ONE declared lazy edge (``DF-9-2-A``) — never a second path."""
    from argus.precision.replay_harness import registry_module

    return registry_module()


def validation_floor_n() -> int:
    """The locked floor, RESOLVED from the 6.5 constant (DN-3 — one floor, two populations)."""
    return int(_registry().VALIDATION_SET_FLOOR_N)


def meets_validation_floor() -> bool:
    """Whether the corpus has genuinely reached the locked floor. Today: ``False``."""
    return eligible_member_count() >= validation_floor_n()


def validation_set_status() -> str:
    """The derived one-line status of the REPOSITORY corpus (never a hand-written figure).

    Mirrors the 6.5 ``precision_gate_status()`` convention — a mechanically-derived marker
    rather than a prose promise that rots — for the corpus the PRD governs. It states the
    measured count, the locked floor and, when the floor is unmet, the reason it is unmet: the
    corpus has no eligible members until Story 13.2 adjudicates one.
    """
    n = eligible_member_count()
    floor_n = validation_floor_n()
    if n >= floor_n:
        return (
            f"floor MET (validation set N={n} independent repositories >= floor N={floor_n}); "
            "reaching the floor is necessary and NOT sufficient — the gate also requires the "
            "adjudication run of precision-validation-protocol.md §5 to be recorded cleared"
        )
    return (
        f"floor NOT MET (validation set N={n} independent repositories, floor N={floor_n}); "
        "the repository corpus is the population the >=80% precision gate is measured over "
        "(PRD Validation Approach), and it is populated by an operator ratification act "
        "(Story 13.1 / AC3b) and adjudicated by a named human (Story 13.2)"
    )
