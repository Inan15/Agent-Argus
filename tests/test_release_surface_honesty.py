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
    # `## Unreleased` — added 2026-08-15 by Story 12.5 (NFR-P3). A PURE INSERTION: no existing
    # section moved relative to any other, and nothing was demoted.
    # Placed FIRST, and the placement is the DECISION this registry's comment above demands
    # rather than a default. Promotion above 11.1's instrument disclosure — which has held first
    # place since it was registered, on the ground that it bounds how a consumer should weigh
    # every other claim in this note — was NOT taken lightly, and it survives the registry's own
    # stated principle, *what a consumer of THIS release hits first*, applied literally: this is
    # the only entry in the note that changes what `pip install` puts on their disk, and it is
    # therefore the only one they encounter before Argus has run at all. It is also the only
    # entry that silently changed the ANSWER for a whole class of user — a non-Python repository
    # was graded by a tool that could not read it — and 11.1's disclosure is what tells them how
    # much to trust the answer, which is a question that arises after there is one. Everything
    # below it can move a verdict, an exit code or a claim; this one moves what the product IS.
    "### Fixed — the default install now grounds every language the tool claims to support",
    # `## Unreleased` — added 2026-08-13 by Story 12.4 (FR37 / DF-11-4-D / AI-E11-6).
    "### Specified — every terminal outcome names its next action and the ingestion boundary",
    # `## Unreleased` — added 2026-08-11 by Story 11.1 (FR34). Registered FIRST because it is
    # the claim a consumer of THIS release must read before weighing any other: the tool now
    # states its own validation status on every verdict surface. Order is pinned by `-16`, so
    # a later story cannot demote it by adding a section above it without deciding to.
    "### Disclosed — Argus now states its own validation status on every verdict surface",
    # `## Unreleased` — added 2026-08-12 by Story 11.4. Registered SECOND, and the placement is
    # the DECISION this registry's comment above demands rather than a default. 11.1's
    # instrument disclosure stays first for the reason it was placed there — it bounds how a
    # consumer should weigh every other claim in this note, including this one — so it was NOT
    # demoted. This section is placed above 11.2's and 11.3's on the registry's own stated
    # principle, *what breaks a pipeline soonest*: it is the only entry that can change an EXIT
    # CODE on an unchanged repository, from `0` to `3`, for a consumer who changed nothing but
    # their environment. 11.2's classification fix moves a verdict conservatively and 11.3's
    # binds only the marketplace channel; this one binds every channel and every language,
    # because the toolchain it validates is the substrate under all of them. It is also the
    # entry a reader most needs BEFORE the others: if their toolchain does not validate, the
    # coverage numbers every other section discusses are withheld rather than wrong. No
    # existing section moved relative to any other — this is a pure insertion.
    "### Fixed — an unvalidated parsing toolchain can no longer produce a false green",
    # `## Unreleased` — added 2026-08-11 by Story 11.2 (DF-8-2-B). Registered THIRD, and that
    # placement is a DECISION this registry's own comment above demands rather than a default:
    # 11.1's instrument disclosure bounds how a consumer should weigh every other claim in this
    # note, including this one, so demoting it beneath a behavioural fix would be the wrong
    # signal for an assurance tool. This section is nonetheless a consumer-visible BEHAVIOUR
    # change — it can move a polyglot repository's verdict, conservatively — which is why it
    # precedes the 10.2/10.3 sections and states its direction rather than hedging it.
    "### Fixed — a production file is no longer mistaken for a test because its name ends in the right letters",
    # `## Unreleased` — added 2026-08-12 by Story 11.3 (DF-9-2-D). Registered FOURTH (was third
    # until Story 11.4 inserted above it on 2026-08-12; its own reasoning below is unchanged and
    # still holds — it was not reordered relative to any other section). The placement is the
    # DECISION this registry's comment above demands rather than a default.
    # Urgency alone would promote it: it is the only *security* entry in the note. It is placed
    # below 11.1's and 11.2's anyway because the stated principle is *what a consumer of THIS
    # release hits first*, and the dominant install path for this release is the index/VCS channel:
    # a CLI or library consumer is entirely UNAFFECTED by the composite-action fix, whereas 11.1's
    # instrument disclosure bounds how they should weigh every claim in this note and 11.2's
    # classification change can move ANY consumer's verdict. The action fix binds only the
    # marketplace channel, which `epics.md` Story 11.3 AC3 hard-gates on this story and ships later
    # (Story 12.9). Reordering an already-reviewed entry would also add avoidable churn to a
    # security change, so no existing section moved.
    "### Security — the composite action no longer pastes your workflow's inputs into its shell script",
    # `## Unreleased` — added 2026-08-12 by Story 11.5 (DF-9-2-A / DF-9-2-B). Registered FIFTH,
    # and the placement is the DECISION this registry's comment above demands rather than a
    # default. THIS IS THE FIFTH CONSECUTIVE STORY TO EDIT THIS REGISTRY (11.1, 11.2, 11.3,
    # 11.4, now 11.5), filed as `DF-11-4-D` and stated here rather than left to be counted:
    # the Epic-11 checkpoint review should look at this file's history and decide whether the
    # registry's cost is buying what it was meant to buy. It is a pure INSERTION — no existing
    # section moved relative to any other, and nothing was demoted.
    # Placed below the four above it on the registry's own stated principle, *what breaks a
    # pipeline soonest*, applied honestly against this entry rather than flatteringly:
    # 11.1 bounds how a consumer weighs every other claim here (including this one); 11.4 can
    # change an EXIT CODE on an unchanged repository; 11.2 can move any consumer's verdict;
    # 11.3 is a security fix on an executable surface. This entry changes NO verdict, NO exit
    # code, NO threshold, NO default and no `stdout` byte — it can only turn an import that
    # failed into one that succeeds, and correct sentences that were untrue. Promotion above
    # 11.3 was considered on the ground that this one binds the dominant index/VCS channel
    # while 11.3 binds only the marketplace channel, and DECLINED: a security fix on an
    # executable surface outranks a packaging fix on a non-consumer module surface.
    "### Fixed — five shipped modules could not be imported from the distribution at all",
    # `## Unreleased` — added 2026-08-13 by Story 12.2 (FR36). A PURE INSERTION: no existing
    # section moved relative to any other, and nothing was demoted.
    # ⚠️ `DF-11-4-D` / `AI-E11-6` are LIVE about this registry and are targeted at Story 12.4.
    # Adding a section is NOT the same as re-opening the impact-rank question, so this entry
    # does exactly what the ledger asks of a story that must touch the file anyway: it is added
    # in registry order with its placement reasoned, and the RANKING of every existing section
    # is left entirely alone. The registry's cost/benefit question stays open for 12.4.
    # Placed SIXTH — below every Epic-11 section — on the registry's own stated principle,
    # *what breaks a pipeline soonest*, applied against this entry honestly rather than
    # flatteringly. It is tempting to promote it: it introduces the ONLY code path in the
    # product that can transmit anything off the machine, and for an assurance tool that is the
    # kind of claim a reader wants early. DECLINED, because the principle is about what a
    # consumer HITS, and this path is unreachable without an explicit new flag: it changes no
    # default, no exit code, no verdict and no byte on any invocation that existed before this
    # release. Each of the five above it can move a consumer who changed nothing — 11.1 bounds
    # how every other claim here should be weighed, 11.4 can change an exit code on an unchanged
    # repository, 11.2 can move any polyglot verdict, 11.3 is a security fix on an executable
    # surface, and 11.5 turns a failing import into a working one.
    # It is placed ABOVE the 10.3 group deliberately: both specify the invocation surface, and a
    # consumer reading the CLI-contract sections should meet the egress opt-in before the six
    # already-shipped flags, because it is the only one of the seven that sends anything.
    "### Specified: `--deep-audit` — the opt-in deep pass, and the false deep claim it replaces",
    # `## Unreleased` — added 2026-08-10 by Story 10.2 (DF-AUD-APAA-D). Registered deliberately,
    # which is what this enumeration is for: each one is a consumer-visible claim someone signed
    # off. "Documented" records the `[languages]` extra, which shipped with zero README/CHANGELOG
    # coverage; "Fixed" records TypeScript/PHP being reported as missing grammars they already had;
    # "Changed" records the per-grammar cache-key provenance (internal — no store is wired, so no
    # cached result exists to invalidate).
    # `## Unreleased` — added 2026-08-10 by Story 10.3 (DF-AUD-APAA-E). "Specified" records the six
    # CLI flags that shipped in 0.1.0 accepted and specified in no binding document; "Fixed" records
    # the one behavioural change under that bless — `--ignore-pattern` was evaluated ABOVE the
    # Live-Key Safeguard its own module docstring promised, so `--ignore-pattern "A"` suppressed
    # every live credential in the audited repository with nothing recorded; "Known divergence"
    # states, rather than changes, the `--coverage-scope` CLI/library default split (DN-8). These
    # precede 10.2's sections because they are what a consumer of THIS release hits first.
    "### Specified — six CLI flags that shipped in `0.1.0` accepted and specified nowhere",
    "### Fixed — `--ignore-pattern` could defeat the live-key safeguard it was documented to sit under",
    "### Known divergence — `--coverage-scope`'s default differs between the CLI and the library",
    "### Documented — the `[languages]` extra, which shipped undocumented",
    "### Fixed — TypeScript and PHP were reported as missing grammars they already had",
    "### Changed — the memoization cache key now names the grammar that actually parsed",
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
    # Registered 2026-08-11 by Story 11.1 (FR34). `[project].description` is the ONE-LINE
    # PyPI summary a stranger reads beside the package name — before the README, before
    # anything. It now carries the instrument-status disclosure, so it has to be inside the
    # over-claim guard: a surface this release publishes on and `-17` does not scan is a
    # surface where an over-claim can land unseen.
    "pyproject.toml",
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
    "pyproject.toml",
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
