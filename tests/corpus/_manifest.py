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
Status               Delivered, CI-asserted (FR20)                **Built here; POPULATED to N=5
                                                                  by the AC3b ratification,
                                                                  awaiting 13.2's adjudication**
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
    "BENCH_COMMIT_SHA",
    "BENCH_MEMBER_IDS",
    "PRE_SEAL_MEMBER_IDS",
    "unratified_bench_candidates",
    "SEALED_PARTITION_TABLE",
    "bench_candidates",
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
    # Added 2026-08-16 with the AC3b ratification, DELIBERATELY and not silently (`-22`
    # checks this tuple against the dataclass in both directions, so the extension could not
    # have been made quietly). It carries what Story 13.2's adjudicator must know about a
    # member BEFORE judging its findings — e.g. that Argus's detectors were developed against
    # that very repository. It is emphatically NOT an eligibility escape hatch: it does not
    # affect any count, and an ELIGIBLE member still may not carry an ``ineligible_reason``.
    "adjudication_caveat",
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

# ─────────────────────────────────────────────────────────────────────────────────────────────
# THE SEAL (Story 16.2, 2026-08-20) — a partition of the bench frozen BEFORE anything is run.
#
# H-2: the cartridge corpus has an author-blind holdout; the repository corpus that actually
# gates has none. If every bench member is adjudicated and the detector is then tuned, no
# untouched population remains to show the tool was not shaped to fit its own exam.
#
# THE RULE LIVES IN ONE PLACE AND IT IS NOT HERE. `argus.precision.gate_seal.partition_of` is
# the pure function; its derivation and its three rejected alternatives are recorded WITH it
# (AC1.2). What lives here is the manifest's half: WHICH members already had output when the
# seal was taken, and the FROZEN MATERIALIZATION of the partition the rule produced.
# ─────────────────────────────────────────────────────────────────────────────────────────────

#: AC1.4 — the members over which Argus output ALREADY EXISTED when the seal was taken, so the
#: bisection was never applied to them. It is DERIVED, not chosen: it is exactly the union of
#: the `members[]` arrays of the two committed adjudication sets (2026-08-16 and 2026-08-18),
#: and `TC-ArgusAgent-PRECISION-001-88` re-derives it from those artifacts and asserts equality
#: in BOTH directions with a non-vacuity floor, so a broken extractor goes RED rather than
#: silently green.
#:
#: ⛔ This set is the reason the seal rule has TWO conjuncts rather than one. Two of these five
#: carry ODD pins — the bisection ALONE would have declared two already-audited members
#: "sealed", one of which supplied 7 of the committed record's 31 judged findings. A holdout
#: that has already been peeked at is not a holdout, and this project would have shipped one.
PRE_SEAL_MEMBER_IDS: frozenset[str] = frozenset(
    {
        "ai-body-runtime",
        "agent-markovich",
        "minions",
        "xagents-webapp",
        "agent-smith",
    }
)

#: AC1.3 — the FROZEN PARTITION of every bench candidate, materialized at the seal commit.
#:
#: ⛔ IT IS A FROZEN MATERIALIZATION OF A RULE, NEVER A HAND-LIST, and the distinction is the
#: whole point: `TC-ArgusAgent-PRECISION-001-89` RE-DERIVES every row from
#: `gate_seal.partition_of` and asserts equality in BOTH directions — no table row the rule
#: contradicts, and no rule output the table omits. A guard that only read the table would be a
#: guard over a hand-list.
#:
#: WHY IT EXISTS AT ALL, given the rule can always be re-run. It exists so the partition
#: SURVIVES the protocol §6 R2 ratification act. After R2 a ratified candidate carries
#: `eligible_for_n=True` and is indistinguishable from a pre-seal member by its fields alone;
#: this table and `PRE_SEAL_MEMBER_IDS` are what keep the two apart, and both were frozen in
#: git before any Argus output over any candidate existed.
SEALED_PARTITION_TABLE: tuple[tuple[str, str], ...] = (
    ("aws-aws-sam-cli", "sealed"),
    ("celery-celery", "sealed"),
    ("certbot-certbot", "sealed"),
    ("conda-conda", "sealed"),
    ("getsentry-sentry-python", "sealed"),
    ("googleapis-google-auth-library-python", "sealed"),
    ("mitmproxy-mitmproxy", "open"),
    ("pypa-pip", "open"),
    ("python-poetry-poetry", "open"),
    ("redis-redis-py", "open"),
    ("scrapy-scrapy", "open"),
    ("spotify-luigi", "open"),
    ("streamlink-streamlink", "open"),
    ("tox-dev-tox", "open"),
)

#: HALT-3 (Story 16.4) — the Story 15.1 BENCH: the 14 members admitted as candidates, frozen at
#: :data:`BENCH_COMMIT_SHA`. **Historical and CLOSED**, exactly like :data:`PRE_SEAL_MEMBER_IDS`
#: — and for the reason :data:`SEALED_PARTITION_TABLE`'s own docstring already states:
#: *"After R2 a ratified candidate carries ``eligible_for_n=True`` and is indistinguishable from
#: a pre-seal member by its fields alone."*
#:
#: ⛔ **WHY THIS SET EXISTS AT ALL.** Story 16.2 froze the PARTITION so it would survive the
#: protocol §6 R2 ratification act, but bench MEMBERSHIP was still derived from the two fields
#: R2 edits (``eligible_for_n`` and ``ineligible_reason``), so ratifying a member silently
#: removed it FROM THE BENCH IT WAS CHOSEN INTO. Story 16.4 MEASURED the consequence: ratifying
#: three members dropped the bench 14 -> 11, breaching ``DF-13-5-A``'s pre-registered 12-20 band
#: and breaking :data:`SEALED_PARTITION_TABLE`'s both-directions equality with the bench.
#: Membership in a set frozen in the past cannot depend on state edited in the future. This
#: constant COMPLETES 16.2's own design intent rather than introducing a new one.
#:
#: ⛔ It is DERIVED, not chosen. ``TC-ArgusAgent-PRECISION-001-103`` re-derives it from
#: ``tests/corpus/_manifest.py`` **as read out of git at** :data:`BENCH_COMMIT_SHA`, applying the
#: ORIGINAL live predicate — correct at that commit precisely because nothing had been ratified
#: yet — and asserts equality in BOTH directions behind a non-vacuity floor that is
#: ``DF-13-5-A``'s own 12-20 band.
BENCH_MEMBER_IDS: frozenset[str] = frozenset(
    {
        "aws-aws-sam-cli",
        "celery-celery",
        "certbot-certbot",
        "conda-conda",
        "getsentry-sentry-python",
        "googleapis-google-auth-library-python",
        "mitmproxy-mitmproxy",
        "pypa-pip",
        "python-poetry-poetry",
        "redis-redis-py",
        "scrapy-scrapy",
        "spotify-luigi",
        "streamlink-streamlink",
        "tox-dev-tox",
    }
)

#: The commit in which Story 15.1's bench LANDED — the 14 rows entered this manifest here.
#: ⛔ NOT ``CRITERIA_COMMIT_SHA``: the criteria were frozen three commits earlier, when this
#: manifest still held only 7 rows. The ordering criteria -> bench -> seal is asserted from the
#: object database by ``TC-ArgusAgent-PRECISION-001-103``, never from this comment.
BENCH_COMMIT_SHA = "c028da5b06a553f9c79c37877874e37a0bdecc61"

#: The `ineligible_reason` marker Story 15.1 gave every bench candidate. Named once so
#: `bench_candidates()` folds on a constant rather than on a substring repeated at call sites.
_CANDIDATE_REASON_MARKER = "candidate"


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
    - ``adjudication_caveat`` — OPTIONAL, and read by a human rather than by a fold: what
      Story 13.2's adjudicator must know about this member before judging its findings. It
      changes no count and grants no eligibility.

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
    adjudication_caveat: str | None = None

    @property
    def partition(self) -> str:
        """AC2.1 — this member's SEAL PARTITION, DERIVED from its own pin. Never stored.

        ``sealed`` | ``open`` | ``pre-seal``, through the one rule in
        ``argus.precision.gate_seal.partition_of``. Read it off the row; never recompute it
        at a call site and never cache it into a field.

        ⛔ **A DERIVED PROPERTY, AND `MANIFEST_FIELDS` STAYS CLOSED AT 9 (DN-16-2-3).**
        ``TC-ArgusAgent-PRECISION-001-22`` compares ``dataclasses.fields(CorpusMemberSpec)``
        against ``MANIFEST_FIELDS`` in both directions, and a ``@property`` is not a
        dataclass field — so this satisfies *"structurally readable off the row"* without
        touching a constant this epic's authorisation lists as untouched.

        **It is also the STRONGER answer, not merely the permitted one.** A stored field can
        be edited to move a member across the seal in one character. A DERIVED partition
        cannot change at all without changing the PIN — which changes which bytes are
        audited, is visible in the diff, and is refused by ``__post_init__`` above unless it
        is a real 40-hex sha. AC2's requirement is that the partition be UNFORGEABLE, and
        derivation is what makes it so.

        The import is function-local for the reason ``_known_languages`` and ``_registry``
        are: ``tests/`` is repository-only and absent from the built distribution
        (``DF-9-2-A``), so this module reaches ``argus`` through declared lazy edges and
        never through a module-level import.
        """
        from argus.precision.gate_seal import partition_of

        return partition_of(
            self.commit_sha, has_prior_output=self.member_id in PRE_SEAL_MEMBER_IDS
        )

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

        # ⛔ HOISTED 2026-08-20 (Story 16.2 / AC2.3) — an INTENDED BEHAVIOUR CHANGE, recorded
        # as one. This check used to live inside the `eligible_for_n=True` branch BELOW, after
        # the early `return`, so a row with `eligible_for_n=False` was never pin-validated at
        # all: `commit_sha="NOT-A-SHA"` and `commit_sha=""` both CONSTRUCTED SILENTLY, on
        # exactly the fourteen candidate rows Story 16.2's seal rule keys on. That was
        # tolerable while a candidate's pin was inert metadata awaiting an operator act. It
        # stopped being tolerable the moment the pin became the INPUT TO A GATE CONDITION:
        # `gate_seal.partition_of` bisects on `int(commit_sha, 16)`, and a SHA-ORDERED RULE
        # OVER UNVALIDATED SHAS IS NOT MECHANICALLY REPRODUCIBLE — the property the whole
        # seal rests on.
        #
        # MEASURED SAFE BEFORE HOISTING, not assumed: all 21 committed rows already satisfy
        # this check, including the deliberate all-zero pin on `minions-story-7-2-superseded`
        # (which is a valid 40-hex sha and is meant to be). So the hoist closes the gap and
        # breaks no existing row. `TC-ArgusAgent-PRECISION-001-76` recorded the OLD behaviour
        # as a deliberate tripwire — *"if __post_init__ ever stops returning early, this
        # guard says so rather than quietly becoming redundant"* — and it fired here exactly
        # as built to; it is re-authored, never relaxed.
        sha = self.commit_sha
        if len(sha) != _SHA_LENGTH or not set(sha) <= _SHA_ALPHABET:
            raise ValueError(
                f"{self.member_id!r}: commit_sha {sha!r} is not a full {_SHA_LENGTH}-character "
                "lowercase hex sha. DN-4 pins by commit and fetches; an unpinned member is not "
                "byte-reproducible, and protocol §4 makes reproducibility the precondition for "
                "any adjudication being valid. Since 2026-08-20 the pin is ALSO the input to "
                "protocol §5's seal condition (Story 16.2): a member's partition is derived "
                "from int(commit_sha, 16), so an unvalidated pin makes the partition "
                "irreproducible. Record the full 40-character lowercase hex sha of the commit "
                "you intend to audit; do NOT shorten it and do NOT leave it blank."
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
        # (the pin is validated ABOVE, for EVERY row — Story 16.2 / AC2.3)
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
# It holds FIVE eligible members. It held ZERO until the AC3b ratification of 2026-08-16, and
# that zero was the honest state up to that point — AC3b (populating it to N ≥ 5 from independent
# repositories) is gated on one explicit operator ratification, because choosing which
# repositories are legitimate members and fetching third-party source are operator acts, not
# autonomous ones. Fabricating plausible repository names to make a count look met would have
# been the worst available outcome in the story that defines the corpus, so the manifest stayed
# empty and said so until a named human ratified it.
#
# REACHING THE FLOOR IS NOT CLEARING THE GATE. N ≥ 5 is one of four §5 conditions; the
# adjudication run, the ≥80% figure and the zero-clean-repo-blocking-FP condition are all still
# outstanding, and `protocol_cleared` has never been `True`.
#
# The two rows below are the RECORDED EXCLUSIONS AC3a requires to live in the manifest itself
# rather than in prose elsewhere. The third exclusion — the cartridges — is not a row at all:
# they are a different corpus measuring a different quantity (DN-2), and `-24` asserts in both
# directions that no cartridge id appears here.
# ─────────────────────────────────────────────────────────────────────────────────────────────
VALIDATION_CORPUS: tuple[CorpusMemberSpec, ...] = (
    # ── RATIFIED 2026-08-16 by the Engineering Lead (XAgent007), Story 13.1 / AC3b ──────────
    # Five members, named by the operator. Each was MEASURED before admission, not accepted on
    # description: git HEAD resolved, tracked-file language mix folded through
    # `argus.shared.source_languages.LANGUAGE_BY_SUFFIX`, and licence checked by looking for a
    # tracked LICENSE/COPYING file (none of the five has one — see the licence strings).
    #
    # ON "INDEPENDENT", STATED PLAINLY BECAUSE IT IS THE CORPUS'S MAIN LIMITATION.
    # The PRD specifies "N ~ 5-10 real XAgents repos, starting with Minions", so same-org
    # repositories ARE the governing corpus and these five satisfy it as written. `independent`
    # here means what it has always meant in this project's record — NOT the tool auditing
    # itself, the distinction that made the 8.5 self-audit worthless as gate evidence. It does
    # NOT mean third-party. All five are XAgents projects, and four of the five are themselves
    # agent-authored (they carry `_bmad/`, `.claude/`, `.agents/`). That is on-thesis rather
    # than accidental — the PRD's primary user is "the Engineering Lead running APAA on an
    # XAgents repo", and AI-authored code is the defect population Argus exists to find — but a
    # reader must not mistake this corpus for an arms-length external one. Recorded here so
    # 13.2's adjudication and 13.3's published figure inherit the caveat rather than the
    # impression.
    CorpusMemberSpec(
        member_id="ai-body-runtime",
        repository_url="file:///D:/ProjectX/XAgents/XAgents/ai_body_runtime",
        commit_sha="4480ffdeb4c56e232d230ebb67572117b72dd754",
        licence="proprietary — XAgents internal (no LICENSE file tracked; operator-recorded)",
        primary_language="python",
        provenance="independent",
        eligible_for_n=True,
        adjudication_caveat=(
            "PIN IS A FRESH INITIAL COMMIT, NOT REAL HISTORY. This tree was NOT under version "
            "control when it was ratified (no .git directory), so it could not be pinned and "
            "was therefore not adjudicable: DN-4 pins by commit, and protocol §4 makes "
            "byte-reproducibility the precondition for any adjudication being valid. On the "
            "operator's explicit instruction (2026-08-16) `git init` + a single initial commit "
            "were performed, producing this sha. The CONTENT is the operator's real working "
            "tree; the COMMIT is minutes old and has no history behind it. The pin is therefore "
            "sound for reproducibility — the point of pinning — but carries no provenance, and "
            "nothing here should be read as evidence about how the code was developed. "
            "`repository_url` is a local file:// locator because the tree has no remote."
        ),
    ),
    CorpusMemberSpec(
        member_id="agent-markovich",
        repository_url="https://github.com/Inan15/Agent-Markovich.git",
        commit_sha="a561668636d8dac922b72d548ad92fdcc814a2ac",
        licence="proprietary — XAgents internal (no LICENSE file tracked; operator-recorded)",
        primary_language="python",
        provenance="independent",
        eligible_for_n=True,
        adjudication_caveat=(
            "The cleanest member of the five: 98 tracked files, 65 of them Python and NOTHING "
            "else — no second language to dilute the grounding, and the working tree was CLEAN "
            "at ratification (0 uncommitted entries), so the audited pin is exactly what the "
            "operator was looking at."
        ),
    ),
    CorpusMemberSpec(
        member_id="minions",
        repository_url="https://github.com/varinderpratap/minions.git",
        commit_sha="ec63b7293b7036bf910a0d1b5e61aba7dc551526",
        licence="proprietary — XAgents internal (no LICENSE file tracked; operator-recorded)",
        primary_language="python",
        provenance="independent",
        eligible_for_n=True,
        adjudication_caveat=(
            "⚠️ OVERFITTING RISK — THE STRONGEST CAVEAT IN THIS MANIFEST, AND THE ADJUDICATOR "
            "MUST WEIGH IT. Argus was DEVELOPED AGAINST THIS REPOSITORY. It began life inside "
            "it as `minions_core/apaa/` and was separated out on 2026-08-03; Story 7.2's "
            "capstone dogfood ran over it (2906 findings); the PRD names it as the validation "
            "set's starting point. So its detectors have been read against, tuned around and "
            "demonstrated on this code in a way that is true of no other member. This is "
            "exactly the bias the cartridge corpus handles with author-blind HOLDOUT rows, and "
            "the repository corpus has no equivalent mechanism. Treat a high precision score on "
            "this member as the LEAST transferable evidence in the corpus, and prefer the other "
            "four when judging whether the >=80% gate genuinely generalises. "
            "SEPARATELY, A LEDGER CORRECTION: deferred-work.md:832-836 records that the Story "
            "7.2 run 'can never be re-derived in this repository'. Re-measured 2026-08-16 — "
            "that statement is TRUE OF THE ARGUS REPOSITORY and MISLEADING AS A GENERAL CLAIM. "
            "The Minions source is present on this machine and resolves at the pin above, so a "
            "NEW run over it is derivable; what can never be re-derived is the SPECIFIC 7.2 "
            "artifact at its own sha. The distinct `minions-story-7-2-superseded` row below is "
            "that artifact and stays ineligible; this row is a NEW pin, audited fresh."
        ),
    ),
    CorpusMemberSpec(
        member_id="xagents-webapp",
        repository_url="https://github.com/varinderpratap/XAgents-WebApp.git",
        commit_sha="33a86525a4981c2725133c3f297ce003c1ef8a2b",
        licence="proprietary — XAgents internal (no LICENSE file tracked; operator-recorded)",
        primary_language="typescript",
        provenance="independent",
        eligible_for_n=True,
        adjudication_caveat=(
            "THE MOST VALUABLE MEMBER FOR THE GATE, AND THE ONE MOST LIKELY TO EXPOSE A "
            "LIMITATION. Measured: 862 source files, 810 TypeScript, 36 Python, 16 JavaScript "
            "— the only member where Python is a rounding error. Story 10.2 delivered "
            "multi-language grounding for every language in `source_languages.py`, and "
            "TypeScript extracts definitions (measured), so this member is eligible under DN-6. "
            "But almost every detector in this tool was written and validated against Python, "
            "so findings here are the corpus's real test of whether the >=80% precision claim "
            "survives outside the language it was built for. One uncommitted entry existed at "
            "ratification; the audit runs the PIN, not the working tree."
        ),
    ),
    CorpusMemberSpec(
        member_id="agent-smith",
        repository_url="https://github.com/Inan15/agent-smith.git",
        commit_sha="9ab774d7bf5d61da552c61094b2d478f72dfbb6d",
        licence="proprietary — XAgents internal (no LICENSE file tracked; operator-recorded)",
        primary_language="typescript",
        provenance="independent",
        eligible_for_n=True,
        adjudication_caveat=(
            "THE POLYGLOT MEMBER, and the one whose coverage figure needs reading carefully. "
            "Measured: 435 source files — 226 TypeScript, 168 Python, 34 Rust, 7 JavaScript. "
            "`primary_language` is recorded as the measured plurality (TypeScript), which is "
            "what DN-6 rules on. The 34 RUST files are the point of interest: Rust grounds "
            "cleanly but its FUNCTIONS never extract (DF-10-2-A / DN-6 — the extractor's "
            "vocabulary entry `fn_item` is not a node type tree-sitter-rust emits), so those "
            "files can reach the index and still never support an `audited_deep` claim. Expect "
            "the coverage ledger to reflect that, and do NOT read a low deep-% here as a defect "
            "in the repository — it is a known limitation of the tool, filed and owned. "
            "16 uncommitted entries existed at ratification; the audit runs the PIN."
        ),
    ),
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

    # ── CANDIDATES, selected 2026-08-19 under Story 15.1 — NOT RATIFIED, NOT IN N ────────────
    #
    # ⛔ THESE FOURTEEN ROWS COUNT TOWARD NOTHING. Each carries `eligible_for_n=False` and the
    # same ratification-pending reason, so `eligible_members()` is unchanged and N is still 5.
    # Protocol §6 R2, verbatim: *"choosing which repositories are legitimate members, and
    # fetching third-party source, are not autonomous acts."* Story 15.1 prepares that decision
    # and does not take it. `MANIFEST_FIELDS` stays CLOSED at nine — no field was added for
    # candidacy, because candidacy is expressible in the fields that already exist, and adding
    # one would be a schema change smuggled in as a convenience.
    #
    # ⛔ PROMOTION TAKES TWO DELIBERATE EDITS, BOTH VISIBLE IN A DIFF. Flipping `eligible_for_n`
    # to `True` while the `ineligible_reason` is still present RAISES ("an ELIGIBLE member
    # carries an ineligible_reason"). That is the R2 act, and it is deliberately not a
    # one-character change. `-78` asserts the single-edit flip still raises for every row here.
    #
    # HOW THEY WERE CHOSEN, AND WHY THE ORDER MATTERS MORE THAN THE LIST. The seven criteria
    # were frozen as executable code in `scripts/candidate_selection.py` at commit
    # `16d7100d73261c759d6176351f2caeff3d1fe172`, which PRECEDES every fetch — `-75` asserts
    # that ordering against real git history rather than asserting an intention. The criteria
    # were then applied UNCHANGED: twenty repositories were fetched, fourteen passed, six were
    # rejected, and not one constant was retuned after seeing what it rejected. Retuning a
    # frozen criterion once you can see which candidates it excludes is the exact failure the
    # freeze exists to prevent, so the rejections are recorded rather than legislated away.
    #
    # THE LINE EVERY ROW HERE RESPECTS: a criterion may reference the defect's DEFINITION; a
    # criterion may never reference the tool's VERDICT. Each `adjudication_caveat` records WHY
    # the repository was considered at all, and every rationale is a statement about the
    # boundary its tests must cross — never a statement about anything Argus reported. The
    # detector was NEVER imported, and `-74` enforces that structurally by an `ast` walk rather
    # than by this comment.
    #
    # ON `provenance="independent"` — READ AC2.3 BEFORE ASSUMING WHAT IT MEANS. The vocabulary
    # is CLOSED at three values and `independent` means, as it always has here, "not the tool
    # auditing itself". It does NOT encode "third-party". These fourteen genuinely ARE
    # arms-length third-party repositories — the first in this corpus that are — and that
    # property is carried in each `adjudication_caveat`'s prose and enforced by selection,
    # because it is stricter than the field can express. A reader who takes `independent` to
    # mean arms-length would misread the five RATIFIED rows above, which are same-org.
    #
    # EVERY FIGURE BELOW WAS READ FROM THE GIT OBJECT DATABASE AT THE PIN, never from a working
    # tree (Story 13.5 exists because working-tree reads silently measured the wrong bytes), and
    # every pin was resolved INDIVIDUALLY by `cat-file -t` returning `commit` with the clone's
    # `origin` verified — three decoy trees on the selection machine carry the right origin URL
    # and the wrong bytes, so matching the remote is not matching the tree. The harness was
    # proved non-vacuous by reproducing an independent earlier measurement EXACTLY (`minions` at
    # its ratified pin: 286 test files / 21 binding / 3 asserting / 1 co-occurrence / 6 loose) —
    # a measurement over an empty or unreachable tree reports 0 and looks identical to a real 0.
    #
    # NO SOURCE BYTE IS VENDORED (NFR-S1 / DN-4): a candidate is metadata and a pin, exactly as
    # the five ratified members are, and `-28` still walks `tests/corpus/` for stray files.
    CorpusMemberSpec(
        member_id="aws-aws-sam-cli",
        repository_url="https://github.com/aws/aws-sam-cli",
        commit_sha="5b6ebdba5866be7a9430d2127630e96329a87649",
        licence="Apache-2.0 — 'Apache License' (LICENSE, tracked at the pin)",
        primary_language="python",
        provenance="independent",
        eligible_for_n=False,
        ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
        adjudication_caveat=(
            "THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has "
            "contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE "
            "its tests drive the AWS SDK across a service boundary that is substituted throughout — a "
            "rationale that references the defect's definition, never the tool's verdict. MEASURED at the "
            "pin, read from the git object database with the detector NOT imported: 497 test files, 296 "
            "binding a mock primitive, 217 asserting on a mock-derived value, 215 carrying BOTH (the "
            "DN-15-1-1 co-occurrence, floor 10; loose variant 218), rate 215/497 exact, 3294 days of history "
            "first-commit-to-pin. Criterion 6 is NOT machine-decidable: admitting this row is the operator's "
            "act at R2."
        ),
    ),
    CorpusMemberSpec(
        member_id="celery-celery",
        repository_url="https://github.com/celery/celery",
        commit_sha="2c42237d375718a84f01f3a7b4eb12a85e061e37",
        licence="BSD-3-Clause — 'Copyright (c) 2017-2026 Asif Saif Uddin, core team & contributors. All rights reserved.' (LICENSE, tracked at the pin)",
        primary_language="python",
        provenance="independent",
        eligible_for_n=False,
        ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
        adjudication_caveat=(
            "THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has "
            "contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE "
            "its tests drive broker and transport boundaries that cannot be exercised for real in a unit "
            "suite — a rationale that references the defect's definition, never the tool's verdict. MEASURED "
            "at the pin, read from the git object database with the detector NOT imported: 147 test files, 81 "
            "binding a mock primitive, 71 asserting on a mock-derived value, 71 carrying BOTH (the DN-15-1-1 "
            "co-occurrence, floor 10; loose variant 73), rate 71/147 exact, 6325 days of history "
            "first-commit-to-pin. Criterion 6 is NOT machine-decidable: admitting this row is the operator's "
            "act at R2."
        ),
    ),
    CorpusMemberSpec(
        member_id="certbot-certbot",
        repository_url="https://github.com/certbot/certbot",
        commit_sha="abf9d1b2e143c51fe1a2209a3b8be33e6a24267f",
        licence="Apache-2.0 — 'Certbot ACME Client' (LICENSE.txt, tracked at the pin)",
        primary_language="python",
        provenance="independent",
        eligible_for_n=False,
        ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
        adjudication_caveat=(
            "THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has "
            "contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE "
            "its tests drive an ACME client against a CA and against system configuration, neither reachable "
            "in a unit suite — a rationale that references the defect's definition, never the tool's verdict. "
            "MEASURED at the pin, read from the git object database with the detector NOT imported: 97 test "
            "files, 73 binding a mock primitive, 54 asserting on a mock-derived value, 53 carrying BOTH (the "
            "DN-15-1-1 co-occurrence, floor 10; loose variant 53), rate 53/97 exact, 5206 days of history "
            "first-commit-to-pin. Criterion 6 is NOT machine-decidable: admitting this row is the operator's "
            "act at R2."
        ),
    ),
    CorpusMemberSpec(
        member_id="conda-conda",
        repository_url="https://github.com/conda/conda",
        commit_sha="ad60271d84099ea3bac642038560ecf0e2ad0a41",
        licence="BSD-3-Clause — 'BSD 3-Clause License' (LICENSE, tracked at the pin)",
        primary_language="python",
        provenance="independent",
        eligible_for_n=False,
        ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
        adjudication_caveat=(
            "THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has "
            "contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE "
            "its tests drive a package solver against network and filesystem boundaries that are "
            "conventionally faked — a rationale that references the defect's definition, never the tool's "
            "verdict. MEASURED at the pin, read from the git object database with the detector NOT imported: "
            "170 test files, 55 binding a mock primitive, 29 asserting on a mock-derived value, 22 carrying "
            "BOTH (the DN-15-1-1 co-occurrence, floor 10; loose variant 23), rate 11/85 exact, 5055 days of "
            "history first-commit-to-pin. Criterion 6 is NOT machine-decidable: admitting this row is the "
            "operator's act at R2."
        ),
    ),
    CorpusMemberSpec(
        member_id="getsentry-sentry-python",
        repository_url="https://github.com/getsentry/sentry-python",
        commit_sha="064542dd2cbdbe0b11f1cda7f47d7d2920b0c38b",
        licence="MIT — 'MIT License' (LICENSE, tracked at the pin)",
        primary_language="python",
        provenance="independent",
        eligible_for_n=False,
        ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
        adjudication_caveat=(
            "THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has "
            "contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE "
            "it is an SDK whose tests must substitute the HTTP transport that ships events — a rationale that "
            "references the defect's definition, never the tool's verdict. MEASURED at the pin, read from the "
            "git object database with the detector NOT imported: 155 test files, 69 binding a mock primitive, "
            "25 asserting on a mock-derived value, 25 carrying BOTH (the DN-15-1-1 co-occurrence, floor 10; "
            "loose variant 28), rate 5/31 exact, 2977 days of history first-commit-to-pin. Criterion 6 is NOT "
            "machine-decidable: admitting this row is the operator's act at R2."
        ),
    ),
    CorpusMemberSpec(
        member_id="googleapis-google-auth-library-python",
        repository_url="https://github.com/googleapis/google-auth-library-python",
        commit_sha="2ea24b03436765fa3cf279ce148482ff6332136b",
        licence="Apache-2.0 — 'Apache License' (LICENSE, tracked at the pin)",
        primary_language="python",
        provenance="independent",
        eligible_for_n=False,
        ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
        adjudication_caveat=(
            "THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has "
            "contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE "
            "its tests must substitute the token endpoint and the HTTP request callable — a rationale that "
            "references the defect's definition, never the tool's verdict. MEASURED at the pin, read from the "
            "git object database with the detector NOT imported: 84 test files, 52 binding a mock primitive, "
            "45 asserting on a mock-derived value, 45 carrying BOTH (the DN-15-1-1 co-occurrence, floor 10; "
            "loose variant 46), rate 15/28 exact, 3440 days of history first-commit-to-pin. Criterion 6 is "
            "NOT machine-decidable: admitting this row is the operator's act at R2."
        ),
    ),
    CorpusMemberSpec(
        member_id="mitmproxy-mitmproxy",
        repository_url="https://github.com/mitmproxy/mitmproxy",
        commit_sha="bae1a7e179da7f9e516ba1b9fe0743f4fd758894",
        licence="MIT — 'Copyright (c) 2013, Aldo Cortesi. All rights reserved.' (LICENSE, tracked at the pin)",
        primary_language="python",
        provenance="independent",
        eligible_for_n=False,
        ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
        adjudication_caveat=(
            "THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has "
            "contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE "
            "its tests drive proxy, TLS and connection layers that a unit suite must substitute — a rationale "
            "that references the defect's definition, never the tool's verdict. MEASURED at the pin, read "
            "from the git object database with the detector NOT imported: 193 test files, 30 binding a mock "
            "primitive, 20 asserting on a mock-derived value, 18 carrying BOTH (the DN-15-1-1 co-occurrence, "
            "floor 10; loose variant 19), rate 18/193 exact, 6022 days of history first-commit-to-pin. "
            "Criterion 6 is NOT machine-decidable: admitting this row is the operator's act at R2."
        ),
    ),
    CorpusMemberSpec(
        member_id="pypa-pip",
        repository_url="https://github.com/pypa/pip",
        commit_sha="0268b0aa084332f5d3cc044810b5958d0c2d1894",
        licence="MIT — 'Copyright (c) 2008-present The pip developers (see AUTHORS.txt file)' (LICENSE.txt, tracked at the pin)",
        primary_language="python",
        provenance="independent",
        eligible_for_n=False,
        ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
        adjudication_caveat=(
            "THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has "
            "contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE "
            "its tests drive package resolution, network and subprocess boundaries that are conventionally "
            "replaced with test doubles — a rationale that references the defect's definition, never the "
            "tool's verdict. MEASURED at the pin, read from the git object database with the detector NOT "
            "imported: 141 test files, 34 binding a mock primitive, 15 asserting on a mock-derived value, 12 "
            "carrying BOTH (the DN-15-1-1 co-occurrence, floor 10; loose variant 16), rate 4/47 exact, 6515 "
            "days of history first-commit-to-pin. Criterion 6 is NOT machine-decidable: admitting this row is "
            "the operator's act at R2."
        ),
    ),
    CorpusMemberSpec(
        member_id="python-poetry-poetry",
        repository_url="https://github.com/python-poetry/poetry",
        commit_sha="92b74dcfe348d0e01e14d40d6c1fa47a4ee04a54",
        licence="MIT — 'Copyright (c) 2018-present Sébastien Eustace' (LICENSE, tracked at the pin)",
        primary_language="python",
        provenance="independent",
        eligible_for_n=False,
        ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
        adjudication_caveat=(
            "THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has "
            "contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE "
            "its tests drive a dependency resolver against PyPI and filesystem boundaries that are "
            "conventionally faked — a rationale that references the defect's definition, never the tool's "
            "verdict. MEASURED at the pin, read from the git object database with the detector NOT imported: "
            "128 test files, 54 binding a mock primitive, 39 asserting on a mock-derived value, 35 carrying "
            "BOTH (the DN-15-1-1 co-occurrence, floor 10; loose variant 35), rate 35/128 exact, 3084 days of "
            "history first-commit-to-pin. Criterion 6 is NOT machine-decidable: admitting this row is the "
            "operator's act at R2."
        ),
    ),
    CorpusMemberSpec(
        member_id="redis-redis-py",
        repository_url="https://github.com/redis/redis-py",
        commit_sha="3972275826c4c2a40c05c999e55d682ffbd33a48",
        licence="MIT — 'MIT License' (LICENSE, tracked at the pin)",
        primary_language="python",
        provenance="independent",
        eligible_for_n=False,
        ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
        adjudication_caveat=(
            "THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has "
            "contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE "
            "it is a client library whose tests must substitute the socket and connection layer — a rationale "
            "that references the defect's definition, never the tool's verdict. MEASURED at the pin, read "
            "from the git object database with the detector NOT imported: 116 test files, 56 binding a mock "
            "primitive, 48 asserting on a mock-derived value, 42 carrying BOTH (the DN-15-1-1 co-occurrence, "
            "floor 10; loose variant 44), rate 21/58 exact, 6127 days of history first-commit-to-pin. "
            "Criterion 6 is NOT machine-decidable: admitting this row is the operator's act at R2."
        ),
    ),
    CorpusMemberSpec(
        member_id="scrapy-scrapy",
        repository_url="https://github.com/scrapy/scrapy",
        commit_sha="df64fe32f61482c2f2f79c6a30960362a0228456",
        licence="BSD-3-Clause — 'Copyright (c) Scrapy developers.' (LICENSE, tracked at the pin)",
        primary_language="python",
        provenance="independent",
        eligible_for_n=False,
        ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
        adjudication_caveat=(
            "THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has "
            "contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE "
            "its tests drive an HTTP downloader and scheduler across boundaries a unit suite must substitute "
            "— a rationale that references the defect's definition, never the tool's verdict. MEASURED at the "
            "pin, read from the git object database with the detector NOT imported: 151 test files, 34 "
            "binding a mock primitive, 12 asserting on a mock-derived value, 12 carrying BOTH (the DN-15-1-1 "
            "co-occurrence, floor 10; loose variant 16), rate 12/151 exact, 6315 days of history "
            "first-commit-to-pin. Criterion 6 is NOT machine-decidable: admitting this row is the operator's "
            "act at R2."
        ),
    ),
    CorpusMemberSpec(
        member_id="spotify-luigi",
        repository_url="https://github.com/spotify/luigi",
        commit_sha="715f65c4a56a908ef0a1df4df6fc33b8420e2e6c",
        licence="Apache-2.0 — 'Apache License' (LICENSE, tracked at the pin)",
        primary_language="python",
        provenance="independent",
        eligible_for_n=False,
        ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
        adjudication_caveat=(
            "THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has "
            "contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE "
            "its tests drive a workflow scheduler against remote targets that are conventionally faked — a "
            "rationale that references the defect's definition, never the tool's verdict. MEASURED at the "
            "pin, read from the git object database with the detector NOT imported: 123 test files, 46 "
            "binding a mock primitive, 33 asserting on a mock-derived value, 32 carrying BOTH (the DN-15-1-1 "
            "co-occurrence, floor 10; loose variant 33), rate 32/123 exact, 5356 days of history "
            "first-commit-to-pin. Criterion 6 is NOT machine-decidable: admitting this row is the operator's "
            "act at R2."
        ),
    ),
    CorpusMemberSpec(
        member_id="streamlink-streamlink",
        repository_url="https://github.com/streamlink/streamlink",
        commit_sha="a9d6db50f4ee4f302a2c73f5e26490395730c396",
        licence="BSD-2-Clause — 'Copyright (c) 2011-2016, Christopher Rosell' (LICENSE, tracked at the pin)",
        primary_language="python",
        provenance="independent",
        eligible_for_n=False,
        ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
        adjudication_caveat=(
            "THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has "
            "contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE "
            "its per-plugin tests substitute the HTTP session that fetches every stream — a rationale that "
            "references the defect's definition, never the tool's verdict. MEASURED at the pin, read from the "
            "git object database with the detector NOT imported: 218 test files, 54 binding a mock primitive, "
            "23 asserting on a mock-derived value, 22 carrying BOTH (the DN-15-1-1 co-occurrence, floor 10; "
            "loose variant 41), rate 11/109 exact, 5483 days of history first-commit-to-pin. Criterion 6 is "
            "NOT machine-decidable: admitting this row is the operator's act at R2."
        ),
    ),
    CorpusMemberSpec(
        member_id="tox-dev-tox",
        repository_url="https://github.com/tox-dev/tox",
        commit_sha="c3927c6437add6d0dd527e14008fe7b174aa3150",
        licence="MIT — 'Permission is hereby granted, free of charge, to any person obtaining a' (LICENSE, tracked at the pin)",
        primary_language="python",
        provenance="independent",
        eligible_for_n=False,
        ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
        adjudication_caveat=(
            "THIRD-PARTY and arms-length: Argus was never developed against it, no Argus author has "
            "contributed to it, and it was not selected on anything Argus said about it. CONSIDERED BECAUSE "
            "its tests drive environment creation and subprocess execution, both conventionally substituted — "
            "a rationale that references the defect's definition, never the tool's verdict. MEASURED at the "
            "pin, read from the git object database with the detector NOT imported: 96 test files, 24 binding "
            "a mock primitive, 14 asserting on a mock-derived value, 10 carrying BOTH (the DN-15-1-1 "
            "co-occurrence, floor 10; loose variant 13), rate 5/48 exact, 2333 days of history "
            "first-commit-to-pin. Criterion 6 is NOT machine-decidable: admitting this row is the operator's "
            "act at R2."
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


def bench_candidates() -> tuple[CorpusMemberSpec, ...]:
    """The Story 15.1 BENCH: rows admitted as candidates awaiting the protocol §6 R2 act.

    A fold over the manifest, never a transcription — the same shape
    :func:`eligible_members` takes. It is the population :data:`SEALED_PARTITION_TABLE` is
    frozen over, so the table's key set and this fold are asserted equal in both directions
    rather than each being maintained by hand.

    ⛔ **It keys on :data:`BENCH_MEMBER_IDS`, never on eligibility.** It used to fold on
    ``not eligible_for_n and "candidate" in ineligible_reason`` — the exact two fields the
    protocol §6 R2 ratification act edits — so a ratified member LEFT the bench it was chosen
    into. Being admitted to the bench is a historical fact about a frozen set; being ratified is
    a later and separate act, and one may not silently undo the other. For the LIVE pending
    state, which ratification legitimately empties, see :func:`unratified_bench_candidates`.
    """
    return tuple(spec for spec in VALIDATION_CORPUS if spec.member_id in BENCH_MEMBER_IDS)


def unratified_bench_candidates() -> tuple[CorpusMemberSpec, ...]:
    """The bench members STILL AWAITING the protocol §6 R2 ratification act.

    ⛔ **This is a different population from :func:`bench_candidates` and the difference is the
    whole of HALT-3.** The bench is HISTORICAL and closed — what was admitted at
    :data:`BENCH_COMMIT_SHA`. *Pending* is a LIVE state that ratification legitimately empties.
    Before 16.4 one predicate served both, so ratifying a member silently shrank the bench; a
    guard asking *"is this row still pending?"* and a guard asking *"is the bench intact?"* got
    the same answer to two different questions.

    Guards asserting a row's **pending state** read this. Guards asserting anything about **the
    bench as chosen** — its size band, its pins, its recorded rationales — read
    :func:`bench_candidates`, which ratification does not move.
    """
    return tuple(
        spec
        for spec in bench_candidates()
        if not spec.eligible_for_n
        and _CANDIDATE_REASON_MARKER in (spec.ineligible_reason or "").lower()
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
