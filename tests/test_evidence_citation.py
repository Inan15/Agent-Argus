"""Story 10.1 / AC2-AC4 — a release status cites an executed gate, or it is NOT ESTABLISHED.

Verification area ArgusAgent-DOCS (``TC-ArgusAgent-DOCS-001-20``..``-23``, CONTINUING the index
locked by Story 8.4; ``-01``..``-19`` are taken by ``tests/test_release_note.py`` and
``tests/test_release_surface_honesty.py``).

**Why this is a NEW file and not an extension of ``test_release_surface_honesty.py``.**
That file is bound by its own docstring to Story 9.2/AC12 and its registry is release
*surfaces* — the things a stranger reads. This one governs status-asserting *planning records*,
a different set under a different rule, with a different marker vocabulary (this guard needs
``nothing`` as a denial marker; adding it there would silently retune a shipped guard). The
position rule below is therefore RE-STATED rather than imported: two independent guards sharing
one mutable policy table is tighter coupling than fifteen duplicated lines of policy is
duplication, and a change to one must not be able to weaken the other. The *shape* is copied
deliberately (§D of the story) — registry + glob closure + sentence scan + positive control.

**The defect under repair (``DF-AUD-APAA-C``).** ``sprint-change-proposal-2026-07-28.md`` created
``.github/workflows/audit-ci.yml`` in section 2 and then, four sections later, declared
*"Upgraded from NEEDS TARGETED REWORK to READY FOR RELEASE!"* on the evidence of a **local**
``pytest`` run. The gate it had just created had never passed: run ``30774175196`` is ``failure``.
A status was asserted over an unexecuted gate — the precise thing Argus exists to catch in other
repositories, committed about itself.

**What a citation is (story DN-3).** An Actions run URL or run id **plus the sha that run covers**,
in the same sentence. A run id is sha-scoped: a bare id looks like evidence while covering an
unknown tree, so a bare id is NOT a citation here. That is not pedantry — run ``31341363300``
covers ``00c8d1b`` and cannot evidence any commit made after it, including the commit that adds
this file.

**Three known ways a guard like this lies, and what stops each.**

1. *It names the files that existed when it was written* (AI-E8-6: all five Epic-8 stories shipped
   a guard narrower than its own AC). Stopped by ``-22``: the registry is resolved by **glob**, and
   any matching file that is not registered fails. A new proposal cannot escape by being new.
2. *Its exemption swallows what it looks for* (the ``-17b`` trailing-negation escape, found by code
   review and not by the author). Stopped by ``-21b``, a positive control in **both** directions
   that plants the verbatim historical defect line and asserts each real honest sentence now on
   disk is not flagged.
3. *It is only ever run after the fix* (AI-E3-1: Story 3.4's keystone test was green over its own
   keystone bug). Every assertion here was demonstrated RED against the uncorrected documents
   before the corrections landed; the run is recorded in the story's Dev Agent Record.

**No network, no LLM, no subprocess, no ``.argus/`` write** — pure functions over committed bytes,
so this runs identically on all three CI legs. Every file is opened ``encoding="utf-8"``
explicitly: the artifact tree carries non-ASCII and an inherited host locale is the exact defect
class that turned run ``31322881580`` red.
"""

from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACT_DIR = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_ARCHITECTURE = _ARTIFACT_DIR / "architecture.md"
_DEFERRED_WORK = _ARTIFACT_DIR / "deferred-work.md"
_CORRECTED_PROPOSAL = _ARTIFACT_DIR / "sprint-change-proposal-2026-07-28.md"

_GUARD_FILE = "tests/test_evidence_citation.py"

# Every status-asserting planning record under the artifact directory, as of Story 10.1.
# The registry is the enumerated space; `-22` resolves the globs below against the tree and
# fails on anything found here that nobody registered.
_STATUS_DOCUMENTS: tuple[str, ...] = (
    "sprint-change-proposal-2026-07-28.md",
    "sprint-change-proposal-2026-08-03.md",
    "sprint-change-proposal-2026-08-09.md",
    "sprint-change-proposal-2026-08-10.md",
    "sprint-change-proposal-2026-08-10b.md",
    "epic-1-retro-2026-06-21.md",
    "epic-2-retro-2026-06-24.md",
    "epic-3-retro-2026-06-27.md",
    "epic-4-retro-2026-06-28.md",
    "epic-5-retro-2026-06-29.md",
    "epic-6-retro-2026-07-02.md",
    "epic-7-retro-2026-07-04.md",
    "epic-8-retro-2026-08-08.md",
    "epic-9-retro-2026-08-09.md",
    # Registered by Story 12.1 (2026-08-12), closing DF-11-1-A. `-22` had been carved out by node
    # id by five consecutive stories because these two retrospectives existed on disk but were
    # unregistered. Registration is INERT against every other assertion in this file:
    # `_status_assertions()` returns 0 status assertions for each (verified by execution), so the
    # per-document loop in `-21` short-circuits. No retrospective was edited and no citation minted.
    "epic-10-retro-2026-08-11.md",
    "epic-11-retro-2026-08-12.md",
)

# Exactly the set the epic's AC names — "any future change proposal or retrospective".
_STATUS_DOCUMENT_PATTERNS: tuple[str, ...] = (
    "sprint-change-proposal-*.md",
    "epic-*-retro-*.md",
)

# Exclusions are BY NAME WITH A REASON, never by silence (the `_PRESERVED_RECORD` precedent in
# tests/test_release_surface_honesty.py:89-96). `-22` asserts every entry carries a reason, so an
# exclusion cannot be added as a bare path by someone trying to make this guard quiet.
_EXCLUDED_BY_DESIGN: dict[str, str] = {
    "stories/": (
        "Story files record TEST-RUN evidence for one unit of work, not a release status for "
        "the project; a story's status lives in sprint-status.yaml, which is the tracker. "
        "Excluded deliberately (story 10.1, DN-5) rather than omitted silently. They do not "
        "match the patterns above either, and this entry states WHY that is correct."
    ),
    "prd.md / architecture.md / epics.md / deferred-work.md": (
        "Specification and ledger documents, not status records. They describe what the system "
        "must do and what is deferred; where they mention a release status they are quoting or "
        "governing one. architecture.md is instead asserted POSITIVELY by -23, which requires "
        "the rule prose to be present, so the (a)-half of AC2 cannot be silently deleted."
    ),
}

# Affirmative assertions that the PROJECT is ready to be released. Deliberately narrow and
# measured against the real corpus rather than guessed: a wide list ("release status",
# "shippable", "release readiness") fires on meta-discussion and rule statements, and a guard
# that cries wolf on its own governance prose gets deleted by the third person to hit it.
_STATUS_CLAIMS: tuple[str, ...] = (
    "ready for release",
    "release ready",
    "release-ready",
    "ready to release",
    "ready for production",
    "production ready",
    "production-ready",
    "cleared for release",
    "approved for release",
    "safe to release",
    "safe to ship",
    "ready to ship",
)

# POSITION MATTERS. A negation denies only a claim it PRECEDES — English binds negation
# leftward, and accepting a trailing one is how "externally validated with no exceptions" walked
# through the first version of `-17b`'s filter. `nothing` is here because the corpus needs it:
# epic-8-retro-2026-08-08.md says "nothing in the story record ... cites the new `release_ready`
# as evidence that argus is release-ready", which is a denial with no bare "no "/"not " in it.
_DENIAL_MARKERS: tuple[str, ...] = (
    " not ",
    "not ",
    " no ",
    "no ",
    "never",
    "cannot",
    "must not",
    "should not",
    "nothing",
    "n't",
    "refuse",
    "withdrawn",
    "struck",
)

# Restrictions that legitimately FOLLOW a claim and narrow it rather than negating it.
_QUALIFIER_MARKERS: tuple[str, ...] = (
    "not established",
    "would be",
    "only when",
    "only once",
    "only after",
    "stays provisional",
    "remains provisional",
)

_NOT_ESTABLISHED_MARKER = "not established"

# A GitHub Actions run, either as a URL or as a bare id introduced by the word "run".
_RUN_URL_RE = re.compile(r"github\.com/[\w.-]+/[\w.-]+/actions/runs/(\d{6,})")
_RUN_ID_RE = re.compile(r"\bruns?\s*(?:id\s*)?[`\[(]*(\d{9,})")

# A git sha: 7-40 hex characters with AT LEAST ONE a-f letter. The letter requirement is what
# stops an all-digit run id (e.g. 31341363300, which is 11 valid hex characters) from being read
# as the sha that is supposed to scope it — which would make every bare run id self-certifying
# and hand the guard back the exact loophole it exists to close.
_SHA_RE = re.compile(r"\b(?=[0-9a-f]{7,40}\b)[0-9a-f]*[a-f][0-9a-f]*\b")

# A strikethrough span, bounded so it cannot cross a blank line. An unterminated `~~` must not be
# able to pair with a closing `~~` further down the file and silently retract everything between
# the two -- that would be a one-character way to hide a claim from this guard.
_STRUCK_RE = re.compile(r"~~(?:[^\n]|\n(?!\s*\n))+?~~")


def _strip_struck(text: str) -> str:
    """Remove `~~struck~~` spans: struck text is RETRACTED, and retracting is the §3.4 form.

    This is why `-20` separately pins that the struck claim is still physically present in
    `sprint-change-proposal-2026-07-28.md`. Without that pin, "strike the claim" and "delete the
    claim" would look identical to this scanner, and deletion is the thing §3.4 forbids.
    """
    return _STRUCK_RE.sub(" ", text)


def _is_attribution(line: str) -> bool:
    """Does *line* introduce a verbatim quotation of another document?

    The house shape is ``` `sprint-change-proposal-2026-07-28.md:63` records: ``` followed by a
    blockquote. A correction document necessarily QUOTES the claim it is correcting, so a scanner
    that cannot tell "X said we were ready" from "we are ready" flags every correction ever
    written -- including the one this story delivers. Both conditions are required (names a `.md`
    source AND ends with a colon), which is narrow enough that the only way to abuse it is to
    attribute your own claim to a named file that does not contain it: a different, checkable lie.
    """
    stripped = line.rstrip()
    return stripped.endswith(":") and ".md" in stripped


def _strip_attributed_quotations(text: str) -> str:
    """Drop blockquote lines that an immediately preceding line attributes to a named document."""
    kept: list[str] = []
    attributing = False
    for line in text.splitlines():
        bare = line.lstrip()
        if bare.startswith(">"):
            kept.append("" if attributing else line)
            continue
        if bare:
            attributing = _is_attribution(bare)
        kept.append(line)
    return "\n".join(kept)


def _split_sentences(text: str) -> list[str]:
    """Sentence-ish units over MARKDOWN, which hard-wraps mid-sentence.

    Paragraph line breaks are cosmetic and are collapsed BEFORE splitting, because a hard wrap can
    otherwise strip a claim of the negation that denies it. Splitting on ``. `` errs toward LARGER
    units, which makes the denial filter easier to satisfy and this guard weaker -- which is
    exactly why ``-21b`` exists. Same shape as ``test_release_surface_honesty.py::_split_sentences``.
    """
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
    """Is the claim at *claim_at* denied or narrowed by the rest of *sentence*?

    A negation counts only when it PRECEDES the claim; a qualifier may appear anywhere, because it
    restricts the claim rather than negating it. Restated from -17b's position rule on purpose --
    see the module docstring for why it is not imported.
    """
    if any(marker in sentence for marker in _QUALIFIER_MARKERS):
        return True
    return any(0 <= sentence.find(marker) < claim_at for marker in _DENIAL_MARKERS)


def _status_assertions(text: str) -> list[tuple[str, str]]:
    """Every (claim phrase, sentence) the document ASSERTS in its own voice.

    Struck spans and attributed quotations are removed first; denials and qualifiers are filtered
    per sentence. What survives is a live, first-person release-status claim.
    """
    scannable = _strip_attributed_quotations(_strip_struck(text)).lower()
    hits: list[tuple[str, str]] = []
    for sentence in _split_sentences(scannable):
        for claim in _STATUS_CLAIMS:
            claim_at = sentence.find(claim)
            if claim_at >= 0 and not _is_denied(sentence, claim_at):
                hits.append((claim, sentence))
    return hits


def _executed_gate_citations(text: str) -> list[tuple[str, str]]:
    """Every (run id, sentence) where a run is cited TOGETHER WITH a sha, in one sentence.

    A run id alone is not a citation (DN-3): run ids are sha-scoped, so a bare id looks like
    evidence and covers an unknown tree.
    """
    found: list[tuple[str, str]] = []
    for sentence in _split_sentences(text.lower()):
        run_ids = _RUN_URL_RE.findall(sentence) + _RUN_ID_RE.findall(sentence)
        if run_ids and _SHA_RE.search(sentence):
            found.extend((run_id, sentence) for run_id in run_ids)
    return found


def _flatten(text: str) -> str:
    """Collapse all whitespace, so a required phrase can be matched across a markdown hard wrap.

    These documents wrap at ~95 columns mid-sentence, so a literal substring check for anything
    longer than a few words fails on where the author happened to break the line — which would
    make this guard assert the line-wrapping rather than the content.
    """
    return " ".join(text.split())


def _registered_paths() -> list[Path]:
    return [_ARTIFACT_DIR / name for name in _STATUS_DOCUMENTS]


def _section(text: str, heading: str, stop_prefixes: tuple[str, ...]) -> str:
    """The slice of *text* from *heading* up to the next heading at or above its level."""
    start = text.find(heading)
    assert start >= 0, f"architecture.md no longer contains the heading {heading!r}"
    rest = text[start + len(heading):]
    end = len(rest)
    for line_start in (m.start() for m in re.finditer(r"^", rest, re.MULTILINE)):
        if any(rest.startswith(prefix, line_start) for prefix in stop_prefixes):
            end = min(end, line_start)
            break
    return rest[:end]


def test_TC_ArgusAgent_DOCS_001_20_the_record_is_corrected_by_striking_and_appending() -> None:
    """TC-ArgusAgent-DOCS-001-20 — Story 10.1/AC1+AC4: corrections strike and append, never rewrite.

    Two records, one rule (§3.4 evidence immutability). The 2026-07-28 proposal's release-status
    claim must survive STRUCK -- present, readable, and marked withdrawn -- beside a dated
    correction that names the failed gate, the superseding run, and the sha each one covers. The
    ledger entry `DF-AUD-APAA-C` must be closed by an append-only note with its original text,
    including the sentence that turned out to be wrong, left byte-for-byte intact.

    Deleting the bad claim instead of striking it would pass a naive honesty scan and destroy the
    evidence that the defect happened, which is the whole point of recording it.
    """
    proposal = _flatten(_CORRECTED_PROPOSAL.read_text(encoding="utf-8"))

    original_claim = (
        "**Release Status**: Upgraded from `NEEDS TARGETED REWORK` to **READY FOR RELEASE**!"
    )
    assert f"~~{original_claim}~~" in proposal, (
        f"{_CORRECTED_PROPOSAL.name}: the 2026-07-28 release-status claim must be present and "
        f"STRUCK, exactly as ~~{original_claim}~~. Deleting or rewording it destroys the record "
        "of the defect (§3.4 evidence immutability)."
    )

    # The untouched context around the claim is still there: nothing was quietly dropped while
    # editing. `:35` created the gate and `:55` reported the local run -- the two halves whose
    # coexistence IS the finding.
    for preserved in (
        "**916 PASSED, 1 SKIPPED, 0 FAILED**",
        "coverage enforcement (`--cov-fail-under=80`)",
        "## 1. Issue Summary",
        "## 4. Implementation Handoff & Scope Classification",
    ):
        assert preserved in proposal, (
            f"{_CORRECTED_PROPOSAL.name} lost original content it was not permitted to edit: "
            f"{preserved!r}. Only the status line may change, and only by being struck."
        )

    assert "LOCAL" in proposal, (
        f"{_CORRECTED_PROPOSAL.name}: the pytest figure at :55 must be labelled as a LOCAL run. "
        "An unlabelled local run reads as gate evidence, which is how this defect happened."
    )

    for required, why in (
        ("30774175196", "the failed run that proves the gate had never passed"),
        ("31341363300", "the superseding run"),
        ("00c8d1b", "the sha run 31341363300 covers"),
        ("2026-08-10", "the correction date"),
        ("NOT ESTABLISHED", "the corrected status"),
    ):
        assert required in proposal, (
            f"{_CORRECTED_PROPOSAL.name}: the correction block must state {required!r} — {why}."
        )

    # AC1.3 -- the citation must say what the run does NOT cover, or it is a half-truth again.
    assert "sha-scoped" in proposal.lower(), (
        f"{_CORRECTED_PROPOSAL.name}: the correction must state that a run id is SHA-SCOPED and "
        "name the tree run 31341363300 does and does not cover (story §A.5). A run id presented "
        "without that scope is the next version of the defect being corrected."
    )

    ledger = _flatten(_DEFERRED_WORK.read_text(encoding="utf-8"))

    original_ledger_sentence = (
        "Both were repaired 2026-08-09 and a clean-venv reproduction of every step passes on "
        "3.12; the repair is NOT the deferred item."
    )
    assert original_ledger_sentence in ledger, (
        "deferred-work.md: DF-AUD-APAA-C's original text — INCLUDING the 'passes on 3.12' "
        "sentence that the executed gate contradicted — must remain byte-for-byte intact. "
        "Correcting it in place would be the third instance of the class it files (DN-8)."
    )
    assert "append-only closure note" in ledger and "31322881580" in ledger, (
        "deferred-work.md: DF-AUD-APAA-C must be closed by an append-only note that records run "
        "31322881580 contradicting the entry's own repair claim (AC4.2)."
    )


def test_TC_ArgusAgent_DOCS_001_21_every_status_claim_cites_an_executed_gate() -> None:
    """TC-ArgusAgent-DOCS-001-21 — Story 10.1/AC2b: the rule, enforced over the registered set.

    For every registered status document: a live release-status claim is allowed only if the
    document cites an executed gate (a run id together with the sha it covers) or the claim's own
    sentence records the status as NOT ESTABLISHED.

    Non-vacuity is asserted directly. A registry of unreadable or empty files would satisfy every
    assertion below without reading a word, so each document must exist, be non-empty and parse to
    real sentences before the scan is allowed to mean anything.
    """
    assert _STATUS_DOCUMENTS, "the status-document registry is empty — the guard scans nothing"

    for path in _registered_paths():
        rel = path.relative_to(_REPO_ROOT).as_posix()
        assert path.is_file(), f"registered status document is missing: {rel}"

        text = path.read_text(encoding="utf-8")
        sentences = _split_sentences(text)
        assert len(sentences) > 10, (
            f"{rel} parsed to {len(sentences)} sentences — the document is empty or the sentence "
            "splitter is broken, and either way this guard is not reading it."
        )

        assertions = _status_assertions(text)
        if not assertions:
            continue

        citations = _executed_gate_citations(text)
        for claim, sentence in assertions:
            if _NOT_ESTABLISHED_MARKER in sentence:
                continue
            assert citations, (
                f"{rel} ASSERTS a release status without citing an executed gate.\n"
                f"  claim   : {claim!r}\n"
                f"  sentence: {sentence[:300]!r}\n"
                "  fix     : cite the audit-ci.yml run that covers this tree, as "
                "'run <id> (<sha>, N/N legs)', or record the status as NOT ESTABLISHED. "
                "A local pytest/mypy/bandit run is necessary but NOT sufficient "
                "(architecture.md §H, DF-AUD-APAA-C)."
            )


def test_TC_ArgusAgent_DOCS_001_21b_the_claim_detector_actually_bites() -> None:
    """TC-ArgusAgent-DOCS-001-21b — Story 10.1/AC3.1: positive control, in both directions.

    A guard whose exemptions swallow the thing it looks for passes over any text, and `-17b`
    proved this project ships that bug when nobody plants a control. The strongest available
    control is the real defect: the verbatim line from `sprint-change-proposal-2026-07-28.md:63`
    must be caught, and every exemption below must be shown to fail closed.
    """
    historical_defect = (
        "- **Release Status**: Upgraded from `NEEDS TARGETED REWORK` to **READY FOR RELEASE**!"
    )
    caught = _status_assertions(historical_defect)
    assert caught, (
        "the detector missed the VERBATIM historical defect this story exists to close: "
        f"{historical_defect!r}. If this guard cannot catch the sentence it was written for, it "
        "catches nothing."
    )
    assert {claim for claim, _ in caught} == {"ready for release"}

    # Trailing negation: the `-17b` escape. A negation only denies a claim it PRECEDES.
    for trailing_negation in (
        "ArgusAgent is ready for release with no caveats.",
        "The repository is production-ready; we are not overstating it.",
        "0.1.0 is cleared for release and nothing blocks it.",
    ):
        assert _status_assertions(trailing_negation), (
            "the denial filter exempted a live status claim because a negation appeared AFTER "
            f"the claim: {trailing_negation!r}"
        )

    # A dangling `~~` must not retract the rest of the file.
    assert _status_assertions(
        "~~an old struck note\n\nArgusAgent is ready for release.\n\nmore text~~"
    ), (
        "an unterminated strikethrough span swallowed a live claim in a later paragraph — a "
        "one-character way to hide a status claim from this guard"
    )

    # An unattributed blockquote is the document's own voice and must still be caught.
    assert _status_assertions("Our position:\n\n> ArgusAgent is ready for release.\n"), (
        "a blockquote with no attribution to a named source document escaped the scan; the "
        "quotation exemption must require an attribution line"
    )

    # --- the other direction: honest text now on disk must NOT be flagged ---

    # The corrected form of the very same line.
    assert not _status_assertions(f"~~{historical_defect}~~"), (
        "a STRUCK claim was still counted as an assertion; striking is how this project retracts "
        "(§3.4), and a guard that ignores it makes the correct fix impossible"
    )

    # Verbatim from sprint-change-proposal-2026-08-09.md:31-33 — a quotation of the defect,
    # attributed to the file it came from. A correction document must be able to quote what it
    # corrects.
    assert not _status_assertions(
        "`sprint-change-proposal-2026-07-28.md:63` records:\n\n"
        "> **Release Status**: Upgraded from `NEEDS TARGETED REWORK` to **READY FOR RELEASE**!\n"
    ), (
        "an ATTRIBUTED verbatim quotation of another document's claim was flagged as this "
        "document's own assertion; every correction record quotes the claim it corrects"
    )

    # Verbatim from epic-8-retro-2026-08-08.md — a denial that contains no bare "no "/"not ".
    assert not _status_assertions(
        "Nothing in the story record, the artifacts or the ledger cites the new `release_ready` "
        "as evidence that Argus is release-ready."
    ), "the detector flagged an honest denial as a status claim"

    for honest in (
        "Release status as of 2026-08-10: NOT ESTABLISHED — no tag exists and nothing is "
        "published.",
        "ArgusAgent is not ready for release: the precision gate is not cleared.",
        "The repository will be ready for release only when an executed gate says so.",
    ):
        assert not _status_assertions(honest), (
            f"the detector flagged an honest sentence as an unevidenced claim: {honest!r}"
        )

    # --- and the citation reader must be just as hard to fool ---
    assert _executed_gate_citations(
        "Run 31341363300 concluded success at sha 00c8d1b with 3/3 legs green."
    ), "the citation reader missed a well-formed 'run id + sha' citation"
    assert _executed_gate_citations(
        "See https://github.com/Inan15/Agent-Argus/actions/runs/31341363300 (sha 00c8d1b)."
    ), "the citation reader missed a well-formed Actions run URL citation"
    assert not _executed_gate_citations("CI is green, see run 31341363300."), (
        "a BARE run id was accepted as a citation. Run ids are sha-scoped: without the sha this "
        "is a claim about an unknown tree, which is the defect one level up (DN-3). The all-digit "
        "run id must not be readable as its own sha."
    )
    assert not _executed_gate_citations(
        "916 PASSED, 1 SKIPPED, 0 FAILED locally on commit 00c8d1b."
    ), "a LOCAL run with a sha but no executed gate was accepted as a citation"


def test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed() -> None:
    """TC-ArgusAgent-DOCS-001-22 — Story 10.1/AC3.2+3.3: a new proposal cannot escape by being new.

    The failure shape is always the same and this project has shipped it five times in one epic
    (AI-E8-6): the guard names the files that existed when it was written, and the next file added
    is outside it. The globs are resolved against the tree and anything unregistered fails.

    A pattern that matches nothing passes every assertion inside it, so non-vacuity is asserted
    twice: the globs must resolve to a non-empty set, and every registered name must be found by
    them (a registry entry the globs cannot see is dead weight that proves nothing).
    """
    found: set[str] = set()
    for pattern in _STATUS_DOCUMENT_PATTERNS:
        for path in _ARTIFACT_DIR.glob(pattern):
            if path.is_file():
                found.add(path.name)

    assert found, (
        f"the status-document patterns {_STATUS_DOCUMENT_PATTERNS} resolved to NOTHING under "
        f"{_ARTIFACT_DIR} — the globs are broken and every other assertion in this file is vacuous"
    )

    unregistered = sorted(found - set(_STATUS_DOCUMENTS))
    assert not unregistered, (
        f"status-asserting document(s) exist but are not registered: {unregistered}. Add them to "
        "_STATUS_DOCUMENTS so the citation rule covers them — a change proposal or retrospective "
        "is exactly the kind of document that states a release status."
    )

    missing = sorted(set(_STATUS_DOCUMENTS) - found)
    assert not missing, (
        f"registered document(s) are no longer found by the globs: {missing}. Either they were "
        "deleted (§3.4: records are superseded, never erased) or the patterns drifted."
    )

    # Exclusions are decisions, not silence: each one carries a written reason.
    assert _EXCLUDED_BY_DESIGN, "the exclusion table is empty — record exclusions, do not omit"
    for excluded, reason in _EXCLUDED_BY_DESIGN.items():
        assert len(reason.split()) >= 12, (
            f"exclusion {excluded!r} has no substantive reason recorded. An exclusion without a "
            "reason is an oversight wearing a decision's clothes (_PRESERVED_RECORD precedent)."
        )

    # The story-file exclusion is real: story files must not be reachable by the patterns.
    stories = _ARTIFACT_DIR / "stories"
    if stories.is_dir():
        assert not (found & {p.name for p in stories.glob("*.md")}), (
            "a story file was matched by the status-document patterns; stories are excluded by "
            f"design — {_EXCLUDED_BY_DESIGN['stories/']}"
        )


def test_TC_ArgusAgent_DOCS_001_23_the_rule_exists_in_prose_and_names_its_guard() -> None:
    """TC-ArgusAgent-DOCS-001-23 — Story 10.1/AC2a: a rule that lives only in a test is not a rule.

    The other half of AC2. `-21` enforces the rule; this asserts the rule is WRITTEN, in
    architecture.md §H where AI-E9-7 says it belongs, and that §Enforcement names the guard file —
    so half (a) cannot be silently deleted and the enforcement cannot become an orphan nobody can
    find. AI-E9-8 is the reason this lives in architecture.md and not in a new governance
    document: a register with no reader is how the last one evaporated.
    """
    text = _ARCHITECTURE.read_text(encoding="utf-8")

    # Flattened, so these assert the RULE and not where the author happened to wrap the line.
    section_h = _flatten(_section(text, "### H. Self-Audit & CI", ("### ", "## ")))
    for required, why in (
        ("cites an executed gate", "the rule's operative clause"),
        ("run URL or run id", "the accepted citation forms"),
        ("the sha that run covers", "DN-3 — a run id without a sha is not a citation"),
        ("NOT ESTABLISHED", "the honest-degradation alternative to a verdict"),
        ("`AUDIT_FAILED`-is-not-a-verdict", "the same principle applied to the tool's own output"),
        ("action.yml:33-48", "where that principle is published"),
        ("necessary, not sufficient", "a local run does not discharge the rule"),
        (_GUARD_FILE, "the guard that enforces it"),
    ):
        assert required in section_h, (
            f"architecture.md §H is missing part of the Story 10.1 evidence-citation rule: "
            f"{required!r} — {why}. A rule that exists only in tests/test_evidence_citation.py "
            "is not a rule (AC2)."
        )

    enforcement = _flatten(_section(text, "### Enforcement", ("## ",)))
    assert _GUARD_FILE in enforcement, (
        f"architecture.md §Enforcement must name {_GUARD_FILE} alongside the existing gates, so "
        "the guard is discoverable from the place guards are listed (AC2a)."
    )
    assert "NOT ESTABLISHED" in enforcement, (
        "architecture.md §Enforcement must state what the guard actually fails on — a status "
        "claim carrying neither a citation nor a NOT ESTABLISHED marker."
    )
