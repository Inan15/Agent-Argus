"""Story 9.2 / AC12 + D12 — the release surfaces are an enumerated space, and they are honest.

Verification area ArgusAgent-DOCS (``TC-ArgusAgent-DOCS-001-16``..``-18``, CONTINUING the
index locked by Story 8.4; ``-01``..``-13`` were taken, ``-14``/``-15`` are Story 9.2's
version-surface enumeration in ``tests/test_release_note.py``).

Two things are pinned here, in one file because they fail for the same reason — a guard
that names the files that existed when it was written.

**1. The release note's section list (D12, closing ledger item ``DF-8-4-B``).**
``DF-8-4-B``'s ``target_story`` is *"the first story after 8.5 that edits
``tests/test_release_note.py`` (or Epic-9 ``9-2``, whichever fires first)"*. BOTH clauses
fire here, because AC6 had to update ``TC-ArgusAgent-DOCS-001-01``'s ``## Unreleased``
pin. Its suggested close was a section-presence assertion over each ``###`` heading PLUS a
bytes-example equality check. **The heading half is closed by ``-16``. The bytes-example
half is left OPEN and recorded as such in ``deferred-work.md``**: the note already carries
byte-equality assertions over the surfaces that matter — the FR16 decision table, the
ship-readiness headlines, the ``final-verdict.md`` callouts and the persisted assurance
sentences are each compared byte-for-byte by ``-03``..``-06`` — so a second generic bytes
check would add duplication rather than coverage. Naming which half closed is the
disposition; closing one half silently would not be.

**2. No release surface presents the self-audit as assurance (AC12, SD-2).**
The repo separation silently changed the CLASS of Argus's flagship evidence. Story 8.5
measured it: the preserved independent Minions run found 2906 findings over 135 files and
returned ``NOT_READY_FOR_RELEASE`` (exit 2); the re-derived Argus SELF-audit finds ~101
over 69 files and returns ``RELEASE_READY`` (exit 0). A self-audit is materially weaker
evidence than an independent-repository run and is NEVER independent corroboration, and
the >=80%-precision externalization gate is defined over the Minions population, which can
never be re-derived in this repository.

A release is where a project describes itself to strangers, so it is the moment that
distinction is most likely to be lost. ``-17`` asserts no registered surface over-claims;
``-18`` asserts the registry is CLOSED — a new consumer-facing surface added to the
release without being registered fails, which is the ``_REPORT_POINTERS``
fail-on-unregistered shape Story 8.3 established for exactly this (AI-E8-6). All five
Epic-8 stories shipped a guard narrower than its own AC by omitting this half.
"""

from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_CHANGELOG = _REPO_ROOT / "CHANGELOG.md"
_ARTIFACT_DIR = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"

# Every `###` section the note carries, in order, as of 0.1.0. The registry is the
# enumerated space: removing a section fails, and ADDING one without registering it fails
# too — so a future edit can neither quietly drop the exit-code contract nor bolt on an
# unreviewed claim section.
_NOTE_SECTIONS: tuple[str, ...] = (
    "### Resolving `argus-agent`",
    "### Version: one value, one source",
    "### Behaviour: the composite action distinguishes a crash from an assessment",
    "### Packaging: what the distribution contains",
    "### No assurance claim is made by this release",
    "### The FR16/FR4 verdict-contract amendment",
    "### Behaviour: exit codes",
    "### Artifacts: schema versions",
    "### Defaults: `--coverage-scope`",
    "### Output: changed strings",
    "### Unchanged on purpose",
    "### API (library consumers)",
    "### Do I need to change anything?",
)

# The consumer-facing surfaces this release publishes or regenerates.
_RELEASE_SURFACES: tuple[str, ...] = (
    "README.md",
    "CHANGELOG.md",
    "action.yml",
    ".github/workflows/release.yml",
    "_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md",
    "_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md",
    "_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md",
)

# Globs that resolve to every file that COULD be such a surface. Anything they find which
# is not registered above fails -18.
_RELEASE_SURFACE_PATTERNS: tuple[str, ...] = (
    "README.md",
    "CHANGELOG.md",
    "action.yml",
    ".github/workflows/release.yml",
    "_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-*.md",
)

# The preserved, frozen Story-7.2 independent run matches the dogfood glob but is NOT a
# surface this release publishes — it is the record being SUPERSEDED, it is the only
# surviving copy of the independent Minions evidence, and Story 9.2 / AC15 fences it.
# Exempted by name so the exemption is a decision rather than an oversight.
_PRESERVED_RECORD = (
    "_bmad-output/design-artifacts/ArgusAgent/"
    "minions-dogfood-proof-story-7-2-superseded.md"
)

# Phrases that would present the self-audit as assurance, claim external validation, or
# claim a cleared precision gate.
_OVER_CLAIMS: tuple[str, ...] = (
    "externally validated",
    "independently validated",
    "independent validation",
    "independent corroboration",
    "externalization-grade",
    "gate is cleared",
    "gate cleared",
    "precision gate cleared",
    "protocol_cleared=true",
    "validated deep audit",
    "third-party validated",
    "independently verified",
)

# A blunt substring scan cannot tell an over-claim from its own denial, and these surfaces
# are FULL of denials — that is the point of them. `minions-dogfood-proof.md` says "The
# gate is cleared ONLY by the human TP/FP adjudication"; CHANGELOG.md says "No statement
# ... should be read as a claim that Argus has been externally validated". Both are the
# honest form and both contain a banned phrase.
#
# So the scan is SENTENCE-scoped and a sentence carrying any of these markers is a denial
# or a condition, not an assertion. This generalises the `-30` precedent in
# tests/test_dogfood_proof.py, which splits the gate-status string on an "EARLY" marker to
# isolate the affirmative region. `-17b` below is the positive control: it proves the
# filter still catches a genuine affirmative over-claim, so the exemption cannot silently
# swallow the thing it exists to find.
#
# POSITION MATTERS, and the first version of this filter ignored it. A bare `"no "` or
# `"not "` ANYWHERE in the sentence exempted it, so "Argus has been externally validated
# with no exceptions" — an affirmative over-claim with a negation trailing behind it —
# passed. English negation binds LEFTWARD to the claim it denies, so a negation is only a
# denial of this claim if it appears BEFORE the banned phrase. Two classes, therefore:
#
#   _DENIAL_MARKERS    — negations. Must appear BEFORE the banned phrase in the sentence.
#   _QUALIFIER_MARKERS — restrictions that legitimately follow the phrase and narrow it,
#                        e.g. "The gate is cleared ONLY by the human TP/FP adjudication",
#                        which is the honest form and says the gate is NOT cleared today.
#
# Both classes are still sentence-scoped, and `-17b` now carries the trailing-negation
# sentence as a second positive control so this exact escape cannot reopen.
_DENIAL_MARKERS: tuple[str, ...] = (
    " not ",
    "not ",
    " no ",
    "no ",
    "never",
    "cannot",
    "must not",
    "should not",
    "n't",
)

_QUALIFIER_MARKERS: tuple[str, ...] = (
    "only by",
    "only cleared",
    "would be",
    "stays provisional",
    "remains provisional",
    "is provisional",
)


def _split_sentences(text: str) -> list[str]:
    """Sentence-ish units over MARKDOWN, which hard-wraps mid-sentence.

    Paragraphs are separated by blank lines; inside a paragraph the line breaks are
    cosmetic, so they are collapsed BEFORE splitting. Splitting on raw line breaks was the
    first thing tried and it failed on a real case: ``CHANGELOG.md``'s "No statement ...
    should be read as a claim that Argus has been / externally validated." wraps so that
    the banned phrase lands on a line of its own, stripped of the "No" that denies it.

    Sentences are then split on ``. `` only. Where this errs it errs toward LARGER units,
    which makes the denial filter easier to satisfy and the guard weaker — which is
    exactly why ``-17b`` exists as a positive control.
    """
    import re

    units: list[str] = []
    for paragraph in re.split(r"\n\s*\n", text):
        flat = " ".join(paragraph.split())
        if not flat:
            continue
        for part in flat.split(". "):
            stripped = part.strip()
            if stripped:
                units.append(stripped)
    return units


def _is_denied(sentence: str, claim_at: int) -> bool:
    """Is the banned phrase at *claim_at* denied or narrowed by the rest of *sentence*?

    A negation counts only when it PRECEDES the phrase — that is where English puts the
    negation of a claim, and accepting one that trails behind is how "externally validated
    with no exceptions" escaped. A qualifier may appear anywhere, because it restricts the
    phrase rather than negating it, and restriction reads naturally after the claim.
    """
    if any(marker in sentence for marker in _QUALIFIER_MARKERS):
        return True
    return any(
        0 <= sentence.find(marker) < claim_at for marker in _DENIAL_MARKERS
    )


def _affirmative_over_claims(text: str) -> list[tuple[str, str]]:
    """Every (phrase, sentence) pair where a banned phrase is asserted, not denied."""
    hits: list[tuple[str, str]] = []
    for sentence in _split_sentences(text.lower()):
        for claim in _OVER_CLAIMS:
            claim_at = sentence.find(claim)
            if claim_at >= 0 and not _is_denied(sentence, claim_at):
                hits.append((claim, sentence))
    return hits


def test_TC_ArgusAgent_DOCS_001_16_note_sections_are_an_enumerated_space() -> None:
    """TC-ArgusAgent-DOCS-001-16 — Story 9.2/D12 (closes DF-8-4-B, heading half).

    The note IS the consumer contract — ``argus/__init__.py`` defers to it explicitly so
    there is no second copy to cross-check against. A section silently deleted from it
    deletes part of that contract with nothing going red, which is what DF-8-4-B was filed
    about. Order is pinned too: the note is ordered by what breaks a pipeline soonest, and
    a reordering changes what a skimming reader hits first.
    """
    note = _CHANGELOG.read_text(encoding="utf-8")
    present = [line.rstrip() for line in note.splitlines() if line.startswith("### ")]

    missing = [section for section in _NOTE_SECTIONS if section not in present]
    assert not missing, f"the release note lost registered section(s): {missing}"

    unregistered = [section for section in present if section not in _NOTE_SECTIONS]
    assert not unregistered, (
        "the release note grew section(s) not registered in _NOTE_SECTIONS: "
        f"{unregistered}. Register them deliberately — an unenumerated section is a "
        "consumer claim nobody reviewed."
    )
    assert present == list(_NOTE_SECTIONS), (
        "the note's sections are all registered but their ORDER changed.\n"
        f"  registry: {list(_NOTE_SECTIONS)}\n  measured: {present}"
    )


def test_TC_ArgusAgent_DOCS_001_17_no_release_surface_over_claims() -> None:
    """TC-ArgusAgent-DOCS-001-17 — Story 9.2/AC12 (SD-2): every registered surface is honest.

    Each registered surface must exist, and none may contain a phrase asserting external
    validation or a cleared precision gate.
    """
    for rel in _RELEASE_SURFACES:
        path = _REPO_ROOT / rel
        assert path.is_file(), f"registered release surface is missing: {rel}"
        hits = _affirmative_over_claims(path.read_text(encoding="utf-8"))
        assert not hits, (
            f"{rel} ASSERTS an over-claim (phrase, sentence): {hits}. The dogfood run is "
            "a SELF-audit; it is never independent corroboration, and the >=80%-precision "
            "gate stays PROVISIONAL (SD-2)."
        )


def test_TC_ArgusAgent_DOCS_001_17b_the_over_claim_detector_actually_bites() -> None:
    """TC-ArgusAgent-DOCS-001-17b — Story 9.2/AC12: the denial filter is not a loophole.

    A guard whose exemption swallows the thing it looks for passes on any text. This is
    the positive control: an affirmative over-claim is caught, and each of the real
    denials the surfaces actually contain is correctly NOT caught.
    """
    caught = _affirmative_over_claims(
        "Argus has been externally validated by a third party and the precision "
        "gate is cleared."
    )
    assert caught, "the detector missed a plain affirmative over-claim"
    assert {claim for claim, _ in caught} >= {"externally validated"}

    # SECOND positive control — the trailing-negation escape, found by code review.
    # The first version of the filter exempted any sentence containing a bare "no " or
    # "not " ANYWHERE, so this sentence — an affirmative over-claim with a negation
    # trailing harmlessly behind it — walked straight through. A negation only denies a
    # claim it precedes.
    for trailing_negation in (
        "Argus has been externally validated with no exceptions.",
        "The precision gate is cleared and there is no caveat.",
        "Argus is independently verified; we are not exaggerating.",
    ):
        assert _affirmative_over_claims(trailing_negation), (
            "the denial filter exempted an affirmative over-claim because a negation "
            f"appeared AFTER the banned phrase: {trailing_negation!r}"
        )

    # The real denials on the shipped surfaces, verbatim, must NOT be flagged.
    for honest in (
        "No statement in this release should be read as a claim that Argus has been "
        "externally validated.",
        "The gate is cleared ONLY by the human TP/FP adjudication over the REAL dogfood "
        "findings above.",
        "it is NEVER independent corroboration of the tool's detection ability.",
        "The >=80%-precision externalization gate stays PROVISIONAL and is not cleared.",
    ):
        assert not _affirmative_over_claims(honest), (
            f"the detector flagged an honest denial as an over-claim: {honest!r}"
        )


def test_TC_ArgusAgent_DOCS_001_18_release_surface_set_is_closed() -> None:
    """TC-ArgusAgent-DOCS-001-18 — Story 9.2/AC12: a NEW surface cannot escape the guard.

    The failure shape this prevents is always the same: a guard names the files that
    existed when it was written, and the next file added is outside it. Resolving the
    patterns against the tree and failing on anything unregistered means a fourth dogfood
    artifact, or a second release workflow, goes RED until someone decides it is honest.
    """
    found: set[str] = set()
    for pattern in _RELEASE_SURFACE_PATTERNS:
        for path in _REPO_ROOT.glob(pattern):
            if path.is_file():
                found.add(path.relative_to(_REPO_ROOT).as_posix())
    assert found, "the release-surface patterns resolved to nothing — the globs are broken"
    assert _PRESERVED_RECORD in found or not (_REPO_ROOT / _PRESERVED_RECORD).exists(), (
        "the preserved Story-7.2 record should have been matched by the dogfood glob; if "
        "it no longer exists, RS-3 'supersede, don't erase' has been violated"
    )
    found.discard(_PRESERVED_RECORD)
    unregistered = sorted(found - set(_RELEASE_SURFACES))
    assert not unregistered, (
        f"consumer-facing release surface(s) exist but are not registered: {unregistered}. "
        "Register them in _RELEASE_SURFACES so the over-claim guard covers them."
    )
    # Non-vacuity: the registry is not a superset of nothing.
    assert set(_RELEASE_SURFACES) - {_PRESERVED_RECORD} <= found | {
        rel for rel in _RELEASE_SURFACES if (_REPO_ROOT / rel).is_file()
    }


def test_TC_ArgusAgent_DOCS_001_19_provisional_gate_language_survives_regeneration() -> None:
    """TC-ArgusAgent-DOCS-001-19 — Story 9.2/AC12: the honesty language is present, not merely un-negated.

    ``-17`` proves no over-claim was ADDED. That is only half of AC12: a surface could
    satisfy it by saying nothing at all, and silence about a self-audit reads as a normal
    audit. The regenerated proof artifact must still SAY the things that make it
    falsifiable — the honest grade, the self-audit clause, and the provisional gate.
    """
    proof = _ARTIFACT_DIR / "minions-dogfood-proof.md"
    assert proof.is_file()
    text = proof.read_text(encoding="utf-8")
    for required in (
        "grade: demo-heuristic-only",
        "SELF-audit",
        "MATERIALLY WEAKER",
        "STAYS PROVISIONAL",
        "NEVER independent corroboration",
    ):
        assert required in text, (
            f"the regenerated proof artifact lost its honesty language: {required!r}"
        )
    # And the two plan artifacts carry the same subject-honesty clause.
    for name in (
        "minions-dogfood-partition-plan.md",
        "minions-dogfood-budget-plan.md",
    ):
        plan_text = (_ARTIFACT_DIR / name).read_text(encoding="utf-8")
        assert "SELF-scoped plan" in plan_text, f"{name} lost its subject-honesty clause"
