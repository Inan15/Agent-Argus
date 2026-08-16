"""Story 13.1 / AC2 — the validation-set decision is RECORDED, at every site that states it.

Verification area ``TC-ArgusAgent-DOCS-001-73``..``-76``. Continues the DOCS area; **no new area
is opened** (the story's §Testing forbids opening one for convenience).

**Why this file is a new module rather than four more assertions in
``tests/test_evidence_citation.py``**, which is where the ``-23`` precedent lives: that file
measured **1199 lines** against NFR-M1's 1200-line ceiling when this story began — one line of
headroom. The sanctioned remedy for a full guard file in this repository is a **cohesion split**
(the Story 12.8 precedent, ``tests/test_module_size_ceiling.py::_REMEDY``), never shaving lines
to make room, and never an exemption. Splitting ``test_evidence_citation.py`` is a refactor of a
load-bearing guard file and belongs to a story that says so. So the Story 13.1 rule is homed in
its own cohesive module — *"is the validation-set decision recorded where it is stated?"* — and
that choice is recorded here rather than left for the next reader to reconstruct.

**What the rule is.** Story 13.1 closed the architecture's last OPEN input **by decision**: the
≥80%-precision externalization gate is measured over a corpus of **real repositories**, never
over the planted-defect cartridges. The architecture states that input at **three** sites, and
the reason this guard counts occurrences rather than checking one is history: the 2026-08-10b
proposal amended one site and left another reading ``CLOSED``, so for three epics the plan
recorded the same item as *closed* in one place and *"still open"* in another. **Closing one
site again would have reproduced that defect exactly.** A guard that asserted the resolution
"is present" would pass on one site out of three, which is why every assertion below is a
**count**.

**A rule that lives only in a test is not a rule, and a rule that lives only in prose is not
enforced** (``architecture.md:921-922``). ``-73``/``-74`` hold the prose side; the corpus's
behaviour is held by ``tests/test_validation_corpus.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "corpus"))

from _manifest import eligible_member_count  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACT_DIR = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_ARCHITECTURE = _ARTIFACT_DIR / "architecture.md"
_PRD = _ARTIFACT_DIR / "E-PRD" / "prd.md"
_PROTOCOL = _ARTIFACT_DIR / "precision-validation-protocol.md"

_GUARD_FILE = "tests/test_validation_set_decision.py"

#: The three sites in ``architecture.md`` that state the validation-set input. This is the
#: population; ``-73`` asserts the resolution reaches ALL of it.
_RESOLUTION_SITES = 3

#: The marker that opens the resolution paragraph at each site, and the clauses the decision is
#: made of. Every one is asserted to appear at least once PER SITE, so a site cannot carry a
#: shortened version that omits the reason or the "does not clear the gate" limit.
_RESOLUTION_MARKER = "RESOLVED BY DECISION 2026-08-16 (Story 13.1 / DN-1) — the PRD governs."

_RESOLUTION_CLAUSES: tuple[tuple[str, str], ...] = (
    (
        "VALIDATION-SET RESOLUTION",
        "the cross-site label, so a reader at any one site knows the other two exist",
    ),
    (
        "`N ≈ 5–10` real repositories",
        "WHICH definition won",
    ),
    (
        "conflicting **`N ≥ 5` labeled planted-defect cartridges** floor is **struck**",
        "which definition lost, and that it was struck rather than silently dropped",
    ),
    (
        "the cartridges measure **recall**",
        "the REASON — two different quantities, not two opinions about one",
    ),
    (
        "A gate clearable by the team's own plants is not an externalization gate.",
        "the reason stated as the principle it rests on",
    ),
    (
        "re-labelled, not demoted",
        "that FR20's delivered cartridge substrate is untouched by this decision",
    ),
    (
        "tests/corpus/_manifest.py::VALIDATION_CORPUS",
        "where membership is now decided — a decision with no named place is a preference",
    ),
    (
        "closes the input by DECISION;\n  it does not clear the gate",
        "the LIMIT of the decision — 13.1 makes the adjudication possible, it does not run it",
    ),
    (
        "`N = 0` eligible members",
        "the measured state AT RESOLUTION, kept struck-not-erased so a later reader can tell "
        "the corpus moved rather than finding a number that was quietly overwritten",
    ),
    (
        "the operator ratified five members under AC3b",
        "the state AFTER ratification. Recording only the resolution-time zero is what made "
        "this document stale within the same story (code-review R1)",
    ),
    (
        "tests/test_validation_set_decision.py",
        "the guard, so the enforcement is discoverable from the rule (AI-E9-7)",
    ),
)


def _flatten(text: str) -> str:
    """Collapse all whitespace so a required phrase matches across a markdown hard wrap.

    Deliberately NOT imported from ``tests/test_evidence_citation.py``: that module's copy is
    private, that file has no room to grow a public export (see this module's docstring), and
    this is a generic whitespace normalizer rather than a rule. AR7 forbids a rule having two
    implementations — the RULE here is :data:`_RESOLUTION_CLAUSES`, and it exists exactly once.
    """
    return " ".join(text.split())


def test_TC_ArgusAgent_DOCS_001_73_the_resolution_is_recorded_at_ALL_THREE_sites() -> None:
    """TC-ArgusAgent-DOCS-001-73 — AC2: closed at every site, in the same words.

    Driver: occurrence COUNTS over ``architecture.md``. The input is stated at §Architectural
    Decisions, §Still OPEN and §Gap Analysis. Before this story those sites disagreed — one said
    *"CLOSED 2026-08-10b — assigned, not answered"*, one said *"Still open"* — which is how an
    architecture decision drifts for three epics while every gate stays green.

    Counting is the whole design. A presence check would go green with the resolution at one
    site and the contradiction intact at the other two, which is precisely the failure this
    story exists to close.
    """
    flat = _flatten(_ARCHITECTURE.read_text(encoding="utf-8"))

    marker_count = flat.count(_flatten(_RESOLUTION_MARKER))
    assert marker_count == _RESOLUTION_SITES, (
        f"the validation-set resolution appears at {marker_count} site(s); it must appear at "
        f"exactly {_RESOLUTION_SITES} — §Architectural Decisions, §Still OPEN and §Gap "
        "Analysis. Recording it at fewer leaves the architecture contradicting itself, which "
        "is the defect Story 13.1 was created to fix (the 2026-08-10b proposal amended one of "
        "two sites and the plan disagreed with itself for three epics). Recording it at more "
        "means a fourth site appeared and this population is stale — re-measure and update "
        "_RESOLUTION_SITES deliberately."
    )

    assert _RESOLUTION_CLAUSES, "the clause registry is empty — every assertion here is vacuous"
    for clause, why in _RESOLUTION_CLAUSES:
        found = flat.count(_flatten(clause))
        assert found >= _RESOLUTION_SITES, (
            f"the resolution clause {clause!r} appears {found} time(s), fewer than the "
            f"{_RESOLUTION_SITES} sites — so at least one site carries a SHORTENED resolution "
            f"that omits it. That clause records {why}."
        )


def test_TC_ArgusAgent_DOCS_001_74_the_rule_is_registered_in_the_architecture_enforcement() -> None:
    """TC-ArgusAgent-DOCS-001-74 — AC2: the ``-23`` / ``-59`` registration pattern.

    Driver: ``architecture.md`` §Enforcement. *"A rule that lives only in a test is not a rule
    and a rule that lives only in prose is not enforced"* — so §Enforcement must carry the rule's
    text, name its enforcing modules and name its test ids, and an enforcement cannot be deleted
    from the architecture while the tests quietly survive, or the reverse.
    """
    text = _ARCHITECTURE.read_text(encoding="utf-8")
    assert "### Enforcement" in text, (
        "architecture.md has no §Enforcement section — every registration assertion in this "
        "repository is vacuous"
    )
    enforcement = _flatten(text.split("### Enforcement", 1)[1])

    for anchor, why in (
        ("Validation-set enforcement", "the registration's own heading"),
        (
            "measured over a corpus of real repositories, never over the planted-defect cartridges",
            "the RULE text itself, not merely a pointer to it",
        ),
        (_GUARD_FILE, "the guard that holds the prose side"),
        ("tests/test_validation_corpus.py", "the guard that holds the behaviour side"),
        ("TC-ArgusAgent-DOCS-001-73", "the id, so an orphaned guard is discoverable"),
        ("TC-ArgusAgent-PRECISION-001-21", "the manifest ids"),
        ("TC-ArgusAgent-DOGFOOD-001-54", "the derived-figure id (DF-8-5-C)"),
        (
            "an unregistered member raises rather than resolving",
            "what the closed manifest actually fails on (the -23 precedent: name the failure)",
        ),
        (
            "at all three sites",
            "the multi-site requirement, which is the part that was breached before",
        ),
    ):
        assert _flatten(anchor) in enforcement, (
            f"architecture.md §Enforcement is missing the Story 13.1 anchor {anchor!r} — {why}"
        )


def test_TC_ArgusAgent_DOCS_001_75_both_documents_record_which_governs_and_which_was_amended() -> None:
    """TC-ArgusAgent-DOCS-001-75 — AC1: the decision carries a date and a reason in BOTH documents.

    Driver: ``prd.md`` and ``precision-validation-protocol.md``. AC1 requires *exactly one*
    definition to govern and the decision to be recorded in both — the winner marked as
    governing, the loser **amended rather than deleted** (§3.4 evidence immutability: strike,
    never erase). A decision recorded only in the document that won is indistinguishable from
    the document that lost having simply been forgotten again.
    """
    prd = _flatten(_PRD.read_text(encoding="utf-8"))
    protocol_raw = _PROTOCOL.read_text(encoding="utf-8")
    protocol = _flatten(protocol_raw)

    for required, why in (
        ("2026-08-16", "the decision carries a DATE"),
        ("Story 13.1 / DN-1", "the decision names its origin"),
        ("This row GOVERNS", "the PRD records that it is the governing definition"),
        (
            "tests/corpus/_manifest.py",
            "the PRD points at where membership is now decided",
        ),
    ):
        assert _flatten(required) in prd, (
            f"prd.md does not record {required!r} — {why}. AC1 requires the decision in BOTH "
            "documents, dated and reasoned."
        )

    # THE MEASURED STATE IS DERIVED, NEVER TRANSCRIBED (code-review R1).
    #
    # This assertion used to be a literal: `("N = 0 eligible members", "the measured state, not
    # an aspiration")`. It was true when written and false eight commits later, because AC3b
    # ratified five members and only the DERIVED surfaces followed. The guard did not merely
    # fail to notice — it REQUIRED the stale string to remain, so correcting the PRD would have
    # turned the suite red. A guard that pins a measurement as a literal is the exact defect
    # `DF-8-5-C` names, and it had been reproduced inside the story that closed it.
    #
    # It now reads the live count and requires the document to agree with it. Ratify a sixth
    # member and this goes red until the PRD is updated — which is the whole point.
    live_n = eligible_member_count()
    assert f"N = {live_n} eligible members" in prd or f"N = {live_n}" in prd, (
        f"prd.md does not state the LIVE eligible-member count ({live_n}). The manifest is the "
        "one named place a member exists, so the PRD's figure must be re-derived from it "
        "whenever membership moves — never left at whatever was true when the sentence was "
        "written. This is the DF-8-5-C rule applied to prose."
    )

    for required, why in (
        ("AMENDMENT 2026-08-16 (Story 13.1)", "the amendment is dated and attributed"),
        ("the PRD governs", "the protocol records that it LOST, in its own text"),
        (
            "STRUCK 2026-08-16 (Story 13.1 / DN-1) — this named the wrong corpus.",
            "§5's corpus-floor row is struck in place",
        ),
        (
            "measure your own homework",
            "the REASON the protocol lost, recorded where the loser can read it",
        ),
        ("V1.1", "the change-log entry exists"),
        (
            "§2 roles, §3 budget and §7 invariants",
            "what was NOT amended — §7 says in its own heading that it is not softened",
        ),
    ):
        assert _flatten(required) in protocol, (
            f"precision-validation-protocol.md does not record {required!r} — {why}"
        )

    # STRIKE, NEVER ERASE: the superseded cartridge floor must survive, struck and readable.
    assert "~~**N ≥ 5** distinct labeled planted-defect" in protocol_raw, (
        "the superseded cartridge-floor text was DELETED rather than struck. §3.4 evidence "
        "immutability: the record of what was wrong is what stops it being reintroduced, and a "
        "deletion passes a naive honesty scan while destroying the lesson (the -20 precedent)."
    )

    # The honesty invariants are NOT softened by the amendment (protocol §7 says so itself).
    for invariant in (
        "N is LOCKED at 5",
        "Precision is measured over FINDINGS, not repos",
        "No over-claim.",
    ):
        assert _flatten(invariant) in protocol, (
            f"protocol §7 invariant {invariant!r} is missing. The corpus moved; the honesty "
            "invariants did not, and §7 is headed 'do NOT soften'."
        )


def test_TC_ArgusAgent_DOCS_001_76_the_protocol_can_locate_its_own_substrate() -> None:
    """TC-ArgusAgent-DOCS-001-76 — AC6.1: a protocol that cannot find its instruments cannot govern.

    Driver: the paths named in ``precision-validation-protocol.md`` §1, checked against the
    filesystem. All three were **dead** — ``minions_core/apaa/precision/replay_harness.py``,
    ``tests/apaa/cartridges/_registry.py``, ``tests/apaa/test_precision_replay.py`` — moved by
    the 2026-08-03 APAA→Argus separation and never updated, so the document governing the
    precision gate pointed at nothing for every instrument it governs.

    Both directions, because a path correction can fail either way: the live paths must be
    NAMED and must EXIST, and no dead path may be asserted as a live **pointer** again.

    **What counts as a pointer, and what counts as a record.** The defect was a §1 substrate
    bullet — ``- **Ground-truth source (golden keys):** `tests/apaa/cartridges/_registry.py`…``
    — a line whose job is to tell a reader where to look. Two contexts legitimately QUOTE the
    dead paths and must not be broken by this guard: the ``>`` correction blockquote, and the
    append-only change-log row. Both are the record of what was wrong, and deleting either would
    pass a naive honesty scan while destroying the lesson (§3.4; the ``-59`` precedent for the
    ``tests/apaa/`` claim in the architecture). So the permitted contexts are **enumerated with
    reasons** rather than left as a blanket allowance.
    """
    # Record contexts, not pointer contexts. An entry here is a decision with a reason.
    permitted_prefixes: dict[str, str] = {
        ">": (
            "the correction blockquote — the dated record of what the path used to say, which "
            "is what stops the dead path being restored by someone who never knew it was wrong"
        ),
        "|": (
            "an append-only change-log table row — §3.4 evidence immutability requires the "
            "amendment to state what it corrected, which means naming the corrected paths"
        ),
    }
    raw = _PROTOCOL.read_text(encoding="utf-8")
    flat = _flatten(raw)

    for live in (
        "tests/cartridges/_registry.py",
        "argus/precision/replay_harness.py",
        "tests/test_precision_replay.py",
        "tests/corpus/_manifest.py",
    ):
        assert live in flat, f"protocol §1 no longer names its substrate {live!r}"
        assert (_REPO_ROOT / live).is_file(), (
            f"protocol §1 names {live!r}, which does not exist on this tree. This is the exact "
            "defect AC6.1 corrected — re-measure before editing the document."
        )

    dead_paths = (
        "minions_core/apaa/precision/replay_harness.py",
        "tests/apaa/cartridges/_registry.py",
        "tests/apaa/test_precision_replay.py",
    )
    for dead in dead_paths:
        assert not (_REPO_ROOT / dead).exists(), (
            f"{dead!r} now EXISTS, so this guard is protecting a premise that changed. "
            "Re-measure and amend the protocol deliberately rather than deleting this check."
        )
        occurrences = [line for line in raw.splitlines() if dead in line]
        asserted_live = [
            line
            for line in occurrences
            if not any(line.lstrip().startswith(p) for p in permitted_prefixes)
        ]
        assert not asserted_live, (
            f"precision-validation-protocol.md names the DEAD path {dead!r} as a live POINTER: "
            f"{asserted_live}. A protocol that cannot locate its own substrate cannot govern an "
            "adjudication. Quoting it is permitted only in a record context — "
            + "; ".join(f"a line starting {p!r} ({why})" for p, why in permitted_prefixes.items())
            + "."
        )

    # A substrate BULLET is the pointer surface the defect lived on. Nothing dead may be there,
    # and the enumeration must be non-empty or this whole assertion is vacuous.
    substrate_bullets = [
        line for line in raw.splitlines() if line.lstrip().startswith("- **") and "`" in line
    ]
    assert len(substrate_bullets) >= 4, (
        f"only {len(substrate_bullets)} substrate bullet(s) found in the protocol — the §1 "
        "enumeration is not being read, so the check below proves nothing"
    )
    for bullet in substrate_bullets:
        for dead in dead_paths:
            assert dead not in bullet, (
                f"a §1 substrate bullet points at the dead path {dead!r}: {bullet!r}"
            )

    assert any(dead in raw for dead in dead_paths), (
        "the corrected dead paths are no longer QUOTED anywhere. The correction is the record "
        "of what was wrong and why; deleting the quotation deletes the lesson, and the next "
        "reader has no way to know the protocol spent thirteen days pointing at nothing."
    )
