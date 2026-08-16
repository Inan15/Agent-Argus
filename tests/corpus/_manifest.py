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
