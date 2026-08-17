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
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import release_notes as rn  # noqa: E402

# The consumer-facing surfaces, IMPORTED from the registry that owns them rather than
# re-listed here (Story 12.9 / AC2). This is the decision the AC demanded be recorded:
# `-24`/`-25` are NEW ASSERTIONS IN THIS FILE that reuse this file's derivation
# (`_status_assertions` / `_executed_gate_citations`) over an IMPORTED population — rather
# than widening `_STATUS_DOCUMENTS`, which is the planning-record population with its own
# glob closure, or copying the regexes into the surface-honesty file.
#
# Why this shape and not the other two:
#   * widening `_STATUS_DOCUMENTS` would put `README.md` and `.github/workflows/release.yml`
#     under `-22`'s glob closure, which resolves `sprint-change-proposal-*.md` /
#     `epic-*-retro-*.md` under the ARTIFACT directory — a population they are not in, so
#     `-22` would have to grow a second closure with a second meaning inside one constant;
#   * copying the regexes into `tests/test_release_surface_honesty.py` would give this rule
#     two implementations, which is the fork AR7 forbids and the class this project has
#     recorded four times.
# The two files keep their SEPARATE marker vocabularies for the reason recorded at :7-15 —
# they are policy, and two guards sharing one mutable policy table is tighter coupling than
# fifteen duplicated lines of policy is duplication. Only the POPULATION is shared, and it
# is shared by import, from the one place that owns it.
from tests.test_release_surface_honesty import _RELEASE_SURFACES  # noqa: E402
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
    # Registered on 2026-08-15 (AI-E12-1), the same one-line edit for the same reason: `-22`'s
    # glob closure sees `epic-*-retro-*.md` the moment the file lands, which is the closure
    # working as designed — the Epic-12 retrospective predicted this red about itself (§6 SD-3)
    # and was written to go green on registration alone. Verified by execution before
    # registering, exactly as the entry above records: `_status_assertions()` returns 0 for it
    # (no phrase in `_STATUS_CLAIMS` occurs in the document at all, denied or otherwise), so
    # `-21`'s per-document loop short-circuits, and `_executed_gate_citations()` returns 0, so
    # it mints no excuse for anything. Its release-status statements are all NOT ESTABLISHED
    # and name the superseded run with the `_CITATION_DENIAL_MARKERS`. No retrospective was
    # edited and no citation minted.
    "epic-12-retro-2026-08-15.md",
    "epic-13-retro-INTERIM-2026-08-17.md",  # Registered 2026-08-17 by the Epic-13 INTERIM retrospective, discharging AI-E12-1's SECOND half ("make the registration part of the retrospective step's own DoD") for the first time. Same one-line edit, same reason, same verification-before-registration as the two entries above: `-22` was observed RED against this document and GREEN after, and `_status_assertions()` returns 0 for it (no phrase in `_STATUS_CLAIMS` occurs in it at all), so `-21`'s per-document loop short-circuits and the registration is inert. It DOES carry 2 well-formed run+sha citations, which mint an excuse for nothing because there is no claim to excuse. No retrospective was edited. ⚠️ THIS LINE PUTS THIS FILE AT EXACTLY 1200/1200 (NFR-M1; `MAINT-001-03` pins 1201 as the failure). The NEXT status document cannot be registered until this module is split — filed as AI-E13-2, and it blocks the FINAL Epic-13 retrospective.
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
    # Added 2026-08-15 by Story 12.9 / AC2, closing a MEASURED hole rather than describing a
    # decision: README.md, CHANGELOG.md, .github/workflows/release.yml and the GitHub Release
    # notes were never excluded from this rule with a reason — they were simply OUTSIDE it,
    # because `_STATUS_DOCUMENTS` above is change-proposals and retrospectives only. The
    # release note is the single most read status-asserting document this project will ever
    # publish and nothing checked it. They are no longer outside: `-24` scans every registered
    # release surface with this file's own derivation, and `-25` pins the derived statement.
    "README.md / CHANGELOG.md / release.yml / the release-note body": (
        "NOT excluded — moved INSIDE the rule by Story 12.9. They are governed by -24 and -25 "
        "over the `_RELEASE_SURFACES` registry imported above rather than by `_STATUS_DOCUMENTS`, "
        "because they are consumer surfaces rather than planning records and they are enumerated "
        "and closed by `TC-ArgusAgent-DOCS-001-18` in the file that owns them. This entry exists "
        "so a reader of this table finds where the rule reaches them instead of concluding they "
        "escaped it."
    ),
}

# Two reasons that apply to a whole class of surface, named once because the class is the
# reason: repeating them per path would invite them to drift into three different reasons for
# one decision.
_COMMAND_ASSET_REASON = (
    "a packaged assistant command asset. It is an instruction sheet an agent reads before "
    "invoking the tool, it makes no claim about the project's release status, and it is "
    "written into a consumer's own configuration directory rather than published as a "
    "record. Its disclosure obligation is held by TC-ArgusAgent-ASSETS-001-06."
)
_DOGFOOD_REASON = (
    "a regenerated dogfood EVIDENCE artifact, not a status record: it reports what one "
    "self-audit run measured, and `TC-ArgusAgent-DOCS-001-19` separately asserts it keeps "
    "the honesty language that bounds how that evidence may be read."
)

# Registered release surfaces that are SCANNED for unevidenced status claims but are not
# required to CARRY the derived status statement, each with the reason. A surface that
# neither carries the statement nor appears here fails `-25`, so "it just does not say
# anything about the release" can never be an unrecorded default.
_STATUS_STATEMENT_NOT_REQUIRED: dict[str, str] = {
    "action.yml": (
        "the composite action's own contract surface: it describes inputs, outputs and the "
        "exit-code map for one CI step, and it is consumed by a workflow rather than read as "
        "a project status. Its FR34 disclosure obligation is separately held by "
        "TC-ArgusAgent-DOCS-001-47 over `_DISCLOSURE_SURFACES`."
    ),
    "pyproject.toml": (
        "package metadata. `[project].description` is a ONE-LINE index summary where a "
        "multi-sentence status paragraph cannot go; the same constraint that made the FR34 "
        "disclosure carry a `short` form there applies to this statement, and a truncated "
        "status sentence would be exactly the half-truth this rule exists to stop."
    ),
    ".github/workflows/release.yml": (
        "the workflow no longer types any release fact: Story 12.9 / AC3 moved the release "
        "note body out of its `run:` literal into `scripts/release_notes.py`, which renders "
        "the derived statement into the note at release time. Carrying a second copy in a "
        "YAML comment would re-create the transcription this story removed."
    ),
    "docs/first-run.md": (
        "an orientation page for a first-time reader — install, first audit, reading the "
        "ledger, what each verdict means. It states the tag caveat where a reader meets it "
        "and points at README.md for the full one; a project-wide CI-evidence paragraph on "
        "it would be answering a question a first-time reader has not yet asked."
    ),
    "scripts/release_notes.py": (
        "it is the GENERATOR: it defines the derivation and the recorded observation the "
        "statement is computed from, and renders that value onto every other surface. "
        "Requiring it to also carry a rendered copy of its own output would be precisely the "
        "transcription this module exists to remove, and the copy could then disagree with "
        "the function beside it."
    ),
    "docs/README.md": (
        "a BMad tooling stub, not a consumer document. It is registered as a release surface "
        "only so that a SECOND page dropped into `docs/` is red rather than invisible "
        "(Story 12.8 / DN-1), and it asserts nothing about a release."
    ),
    "argus/assets/commands/argus-audit.md": _COMMAND_ASSET_REASON,
    "argus/assets/commands/argus-audit-report.md": _COMMAND_ASSET_REASON,
    "argus/assets/commands/argus-audit-security.md": _COMMAND_ASSET_REASON,
    "_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-proof.md": _DOGFOOD_REASON,
    "_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-partition-plan.md": _DOGFOOD_REASON,
    "_bmad-output/design-artifacts/ArgusAgent/minions-dogfood-budget-plan.md": _DOGFOOD_REASON,
}

# The surfaces that DO state the project's release status, and therefore must render the
# derived statement verbatim. Two, and they are the two a stranger actually reads: README.md
# is the PyPI page body (`readme = "README.md"`), CHANGELOG.md is the release note.
_STATUS_STATEMENT_REQUIRED: tuple[str, ...] = ("README.md", "CHANGELOG.md")

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

# Markers that DISQUALIFY a sentence from being read as a citation, even though it carries a
# run id and a sha in the same breath.
#
# ⚠️ FOUND BY MEASUREMENT 2026-08-15 (Story 12.9 / AC2), and it is a real defect rather than
# noise: the honest `NOT ESTABLISHED` statement this story derives NAMES the superseded run
# WITH the sha it covers — it has to, because a run id quoted without its sha is the
# half-truth `architecture.md:614-616` uses that exact run id to illustrate. So the most
# scrupulous sentence this project can write parsed as a well-formed citation, and any
# surface carrying it would have had every OTHER unevidenced status claim on it excused by a
# citation that was never offered.
#
# This makes the reader STRICTER, never looser — the correct direction, because a citation
# here EXCUSES a claim, so recognising fewer of them can only tighten the rule. Adding one of
# these markers to your own sentence therefore costs you the excuse rather than buying one;
# there is no loophole in this direction. `-25b` is the positive control both ways.
_CITATION_DENIAL_MARKERS: tuple[str, ...] = (
    "not established",
    "superseded",
    "does not cover",
    "no executed gate",
    "half-truth",
)

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

    Struck spans go first (added 2026-08-16). §3.4 retracts by striking rather than by
    deleting, so a WITHDRAWN citation necessarily stays on the page, and reading it as live
    evidence would let it go on excusing claims — the opposite of what striking it meant.
    ⚠️ Direction check, because this reader EXCUSES claims: recognising fewer citations can
    only make the composed rule STRICTER, which is the argument already recorded for
    `_CITATION_DENIAL_MARKERS` above. `-21b` is the control, both ways.
    """
    found: list[tuple[str, str]] = []
    for sentence in _split_sentences(_strip_struck(text).lower()):
        if any(marker in sentence for marker in _CITATION_DENIAL_MARKERS):
            continue
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

    # A run NAMED AS SUPERSEDED is not a citation, even though it carries its sha — which it
    # must, because a run id without one is the half-truth this rule exists to stop. Added
    # 2026-08-15 by Story 12.9 / AC2 after the composed rule was measured excusing claims on
    # the strength of the honest NOT ESTABLISHED sentence itself.
    for disqualified in (
        "run 31341363300 covers sha 00c8d1b and is named here as superseded rather than "
        "cited",
        "ci evidence: not established — run 31341363300 (00c8d1b) does not cover this tree",
    ):
        assert not _executed_gate_citations(disqualified), (
            "a sentence that names a run as superseded / not established was read as a "
            f"CITATION, which would excuse every other claim on that surface: {disqualified!r}"
        )
    # A STRUCK citation is a RETRACTED one and must not go on excusing claims (added
    # 2026-08-16 with the strengthening it controls). Both directions over the SAME sentence.
    struck_citation = "Run 31341363300 concluded success at sha 00c8d1b with 3/3 legs green."
    assert not _executed_gate_citations(f"~~{struck_citation}~~"), (
        "a STRUCK citation was still read as live evidence. Striking is how this project "
        "retracts (§3.4), and a retracted citation that still excuses status claims makes "
        "the correct fix impossible."
    )
    # ...and the ordinary citation still is one, so neither disqualifier swallowed the rule.
    assert _executed_gate_citations(struck_citation)


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


# ─────────────────────────────────────────────────────────────────────────────────────
# Story 12.9 / AC2 — the rule reaches the surfaces a STRANGER reads, and the status is DERIVED
#
# MEASURED on `de05dec`: `_STATUS_DOCUMENTS` above covers `sprint-change-proposal-*.md` and
# `epic-*-retro-*.md` only. `README.md`, `CHANGELOG.md`, `.github/workflows/release.yml` and
# the GitHub Release notes were not excluded with a reason — they were simply OUTSIDE this
# guard. The release note is the single most read status-asserting document this project will
# ever publish, and nothing checked it.
#
# Two assertions close that, and they are deliberately different jobs. `-24` applies the
# EXISTING rule (cite, or record NOT ESTABLISHED) to the imported release-surface population.
# `-25` closes the second half of the AC — the citation is DERIVED, never transcribed: one
# named function computes the statement, and every surface that states a release status
# renders THAT value rather than a sentence somebody typed.
# ─────────────────────────────────────────────────────────────────────────────────────

# The sha the derivation is asked about. It is HEAD, read from git, not a literal: pinning a
# sha here would make the guard describe a tree that has moved on, which is the staleness
# this whole rule exists to prevent.
def _head_sha() -> str:
    done = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
    )
    return done.stdout.strip() if done.returncode == 0 else ""


def test_TC_ArgusAgent_DOCS_001_24_every_release_surface_cites_or_records_not_established() -> None:
    """TC-ArgusAgent-DOCS-001-24 — Story 12.9 / AC2: the rule reaches the consumer surfaces.

    OBSERVABLE: live, first-person release-status claims on the registered release surfaces,
    and whether the surface carrying one also cites an executed gate (a run id together with
    the sha it covers) or records the status as NOT ESTABLISHED in that claim's own sentence.

    Same rule as `-21`, same derivation, different population — imported from the registry
    that owns it, not re-listed. Non-vacuity is asserted directly and twice, because this
    guard passes by finding nothing: the population must be non-empty AND the scan must have
    classified real sentences. A registry of unreadable files would otherwise satisfy every
    assertion below without reading a word.
    """
    assert _RELEASE_SURFACES, "the release-surface registry is empty — the guard scans nothing"

    scanned = 0
    classified = 0
    for rel in _RELEASE_SURFACES:
        path = _REPO_ROOT / rel
        assert path.is_file(), f"registered release surface is missing: {rel}"
        text = path.read_text(encoding="utf-8")
        scanned += 1
        classified += len(_split_sentences(text))

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
                "  fix     : CORRECT the sentence — cite the audit-ci.yml run that covers "
                "this tree as 'run <id> (<sha>, N/N legs)', or record the status as NOT "
                "ESTABLISHED — or add an `_EXCLUDED_BY_DESIGN` entry with a stated reason. "
                "Do NOT trim `_STATUS_CLAIMS`, widen `_DENIAL_MARKERS` or narrow the "
                "population: that vocabulary was measured against the real corpus, and "
                "loosening it to silence a hit is how this guard stops guarding (-21b)."
            )

    assert scanned > 0, "no release surface was scanned"
    assert classified > 0, (
        f"the {scanned} registered release surfaces parsed to {classified} sentences — the "
        "splitter is broken and every assertion above is vacuous"
    )


def test_TC_ArgusAgent_DOCS_001_25_the_release_status_is_derived_not_transcribed() -> None:
    """TC-ArgusAgent-DOCS-001-25 — Story 12.9 / AC2: ONE derivation, rendered everywhere.

    OBSERVABLE: the statement `release_notes.derive_release_status` produces for a given
    (observation, sha) pair, and whether the surfaces that state a release status carry
    exactly the statement it produces for the commit actually in hand.

    This is the story's title, mechanised. A surface that hand-types a run id, a sha or a
    status is the transcription class AI-E9-7 forbids and is what made `DF-AUD-APAA-C`
    possible, so the surfaces render the derived value and this asserts they do — over BOTH
    branches, each driven by an observation that really happened:

    * asked about the sha the RECORDED run covers (31908861401 / `cea9268`) the status is
      ESTABLISHED, and the citation must carry the run id, that sha, the leg count and the
      SCOPE of what the run did not evaluate;
    * fed the SUPERSEDED observation (31341363300 / `00c8d1b`) the same function must return
      NOT ESTABLISHED, name that run as superseded WITH its sha, and name the human step. A
      derivation that can only ever cite is as much a constant wearing a function's clothes
      as one that can only ever abstain.

    **RE-POINTED 2026-08-16, and the reason is the whole point of this assertion.** Between
    `03f3a39` and this commit `-25` asserted `status.established` for HEAD — that the
    recorded run cover whatever commit is checked out. That is STRUCTURALLY UNSATISFIABLE on
    a moving branch: recording an observation and re-rendering the surfaces is ITSELF a
    commit, so HEAD moves past the covered sha the instant the render lands, and the failure
    message's own remedy re-created the failure. A guard which cannot fail is a defect here;
    one which cannot pass is that defect mirrored. So the property asserted is the one the
    guard was always FOR: the status is DERIVED and CORRECT FOR WHICHEVER BRANCH THE OBSERVED
    FACTS IMPLY. Staleness is *reported* rather than *required* — the derivation is asked
    about HEAD, graded against an independently computed expectation, and the surfaces must
    carry that answer. *"The cited run covers cea9268 and HEAD has moved on"* is TRUE, so the
    surfaces may say it and this guard stays green.
    """
    head = _head_sha()
    assert re.fullmatch(r"[0-9a-f]{40}", head), (
        f"could not read HEAD ({head!r}); this guard cannot ask whether the recorded gate "
        "run covers the commit being released, and must not pass while it cannot look"
    )

    # The sha the recorded run ACTUALLY covers — read off the observation, never typed, so
    # this half re-points itself the day the observation is re-taken.
    covered = rn.RECORDED_GATE_OBSERVATION.run_sha

    # ── BRANCH ONE: asked about the commit the recorded run covers ──
    status = rn.derive_release_status(rn.RECORDED_GATE_OBSERVATION, covered)
    assert status.established, (
        "the recorded observation does not establish a status even for the sha its own run "
        f"covers ({covered}): either it stopped reporting `success`, or "
        "`derive_release_status` can no longer reach its citation branch at all."
    )
    assert rn.NOT_ESTABLISHED not in status.statement
    # A citation carries the run id AND the sha that run covers, in the same breath — a bare
    # id is the half-truth `architecture.md:614-616` uses run 31341363300 to illustrate.
    assert rn.RECORDED_GATE_OBSERVATION.run_id in status.statement
    assert rn.RECORDED_GATE_OBSERVATION.run_sha in status.statement
    assert f"{rn.RECORDED_GATE_OBSERVATION.legs} legs green" in status.statement, (
        "the citation does not state the leg count, which is what says how much of the "
        "matrix actually ran"
    )
    # ...and this file's own citation reader must accept it, so the generator and the guard
    # cannot disagree about what a citation is.
    assert _executed_gate_citations(status.statement), (
        "the derivation emitted a 'citation' that `_executed_gate_citations` does not "
        "recognise as one"
    )

    # The answer FOLLOWS THE SHA IT IS ASKED ABOUT — one observation, two questions, two
    # answers. Without this, the branch above could be reached by a function that ignores its
    # second argument, which is the transcription defect with a signature bolted on.
    assert not rn.derive_release_status(
        rn.RECORDED_GATE_OBSERVATION, "f" * 40
    ).established, (
        "the recorded observation established a status for a sha its run does not cover; a "
        "run id is sha-scoped (architecture.md §H, DN-3)"
    )

    # ── the SCOPE half: a green run is evidence for what it EXECUTED ──
    #
    # Added 2026-08-16 with the citation it qualifies. Story 10.1 wrote the rule against the
    # only half-truth reachable then (a run id without its tree). The moment a run covers the
    # released commit a second one opens: the run's green is read as covering guards the run
    # itself declined to evaluate — and on this repository that is not hypothetical, because
    # `audit-ci.yml` has no `uv`, so all four installed-artifact guards SKIP on every leg
    # while the run reports success. A citation that lets a reader infer that proof ran is
    # the same defect one level along.
    assert rn.RECORDED_GATE_OBSERVATION.unexercised, (
        "the recorded observation claims the cited run evaluated everything it carries. If "
        "that became true, it was a CI change (`uv` on the runner) — record it by "
        "re-observing the run, and leave this assertion pointing at the observation"
    )
    for unexercised in rn.RECORDED_GATE_OBSERVATION.unexercised:
        assert unexercised in status.statement, (
            "the citation omits something the observed run recorded as NOT EVALUATED:\n\n"
            f"{unexercised}\n\nA green run cited without its scope claims coverage the run "
            "refused to give, which is the half-truth this rule exists to stop."
        )
    assert "SCOPE" in status.statement and "NOT EVALUATED" in status.statement

    # The scope is DERIVED from the observation, not appended to every citation as boilerplate
    # — proven in both directions over the same function, since a caveat that is always there
    # is decoration and a caveat that is never there is the defect.
    silent = rn.derive_release_status(
        replace(rn.RECORDED_GATE_OBSERVATION, unexercised=(), outcomes=""), covered
    )
    assert silent.established and "SCOPE" not in silent.statement, (
        "a run that evaluated everything it carries still published a scope caveat; a "
        "caveat nobody can ever remove is one every reader learns to skip"
    )
    invented = rn.derive_release_status(
        replace(rn.RECORDED_GATE_OBSERVATION, unexercised=("a guard nobody ran",)), covered
    )
    assert "a guard nobody ran" in invented.statement, (
        "the scope did not follow the observation, so it is a literal in the derivation "
        "rather than a rendering of what was observed"
    )

    # ── the STALENESS signal: reported and checked, never demanded away ──
    # The derivation is asked about the commit in hand and graded against an expectation
    # computed HERE — a restatement of the sha-scoping rule rather than a call into
    # `release_notes._covers`, because a grader borrowing the graded function's own helper
    # grades nothing. Prefix-tolerant both ways; shas are published abbreviated.
    head_is_covered = head.startswith(covered[:7]) and (
        head.startswith(covered) or covered.startswith(head)
    )
    expected = head_is_covered and rn.RECORDED_GATE_OBSERVATION.conclusion == "success"
    published = rn.derive_release_status(rn.RECORDED_GATE_OBSERVATION, head)
    assert published.established is expected, (
        f"the derivation answered `established={published.established}` for HEAD ({head}) "
        f"while the recorded run covers {covered} and concluded "
        f"{rn.RECORDED_GATE_OBSERVATION.conclusion!r}, so the honest answer is {expected}: "
        "the status did not follow the facts it is derived from"
    )
    # Whichever branch that is, the statement must NAME the observed run and the sha it
    # covers: that IS the staleness signal, and it is what lets a reader see whether the
    # cited tree is the one in front of them. Dropping the run id when it goes stale would
    # hide exactly the fact worth reporting.
    assert rn.RECORDED_GATE_OBSERVATION.run_id in published.statement
    assert covered in published.statement
    # ...and the citation reader must AGREE with the machine answer, both ways.
    assert bool(_executed_gate_citations(published.statement)) is published.established, (
        "the derivation and this file's citation reader disagree about whether the published "
        f"statement is a citation:\n\n{published.statement}"
    )

    # Every surface that states a release status renders THAT value — the answer for the
    # commit in hand — byte for byte.
    for rel in _STATUS_STATEMENT_REQUIRED:
        assert rel in _RELEASE_SURFACES, (
            f"{rel} is required to carry the derived status but is not a registered release "
            "surface; the two registries have drifted"
        )
        text = _flatten((_REPO_ROOT / rel).read_text(encoding="utf-8"))
        assert _flatten(published.statement) in text, (
            f"{rel} does not carry the derived release-status statement. Render it — do not "
            "retype or paraphrase it. If the observation was just re-taken, re-render every "
            f"surface in {list(_STATUS_STATEMENT_REQUIRED)} through "
            f"`release_notes.derive_release_status`. Expected:\n\n{published.statement}"
        )

    # Every registered surface either carries the statement or has a recorded reason not to.
    unaccounted = sorted(
        rel
        for rel in _RELEASE_SURFACES
        if rel not in _STATUS_STATEMENT_REQUIRED
        and rel not in _STATUS_STATEMENT_NOT_REQUIRED
    )
    assert not unaccounted, (
        f"release surface(s) neither carry the derived status statement nor record why they "
        f"do not: {unaccounted}. Silence about a release status on a consumer surface is a "
        "decision; make it one."
    )
    for surface, reason in _STATUS_STATEMENT_NOT_REQUIRED.items():
        assert surface in _RELEASE_SURFACES, (
            f"{surface!r} is exempted from carrying the status statement but is not a "
            "registered release surface — the exemption describes a file the rule never "
            "reached, which proves nothing"
        )
        assert len(reason.split()) >= 12, (
            f"exemption {surface!r} has no substantive reason recorded (the -22 rule)"
        )

    # ── the other direction: a run that does NOT cover the released commit ──
    #
    # Driven by the REAL superseded observation (run 31341363300 / 00c8d1b), retained rather
    # than deleted (§3.4), so this branch is exercised by an observation that actually
    # happened instead of by a synthetic one nobody ever published.
    assert rn.SUPERSEDED_GATE_OBSERVATIONS, (
        "the superseded observations were deleted. They are the record that this citation "
        "was earned rather than assumed, and they are what drives the NOT ESTABLISHED "
        "branch on real data (§3.4 evidence immutability)"
    )
    superseded = rn.derive_release_status(rn.SUPERSEDED_GATE_OBSERVATIONS[0], covered)
    assert not superseded.established, (
        "a run that does NOT cover the commit being released established the status — the "
        "whole rule is that a run id is sha-scoped (architecture.md §H, DN-3)"
    )
    assert rn.NOT_ESTABLISHED in superseded.statement
    assert rn.SUPERSEDED_GATE_OBSERVATIONS[0].run_id in superseded.statement
    assert rn.SUPERSEDED_GATE_OBSERVATIONS[0].run_sha in superseded.statement
    assert "SUPERSEDED" in superseded.statement, (
        "the statement quotes a run id without saying what it is; naming it as superseded is "
        "what stops the sentence from reading as a citation"
    )
    assert "push `master`" in superseded.statement, (
        "the statement does not name the exact human step that would establish a citation"
    )
    # ...and the citation reader must REFUSE to read it as a citation, which is the
    # strengthening made on 2026-08-15: a scrupulous NOT ESTABLISHED sentence necessarily
    # names a run WITH its sha, and reading that as a citation would excuse every other
    # claim on the surface carrying it.
    assert not _executed_gate_citations(superseded.statement), (
        "the honest NOT ESTABLISHED sentence was read as a CITATION; the disqualifier that "
        "stops that must survive every change to the derivation"
    )

    # A run that COVERS the sha but did NOT succeed is not a citation either — asked about
    # `covered`, so the failure is the only thing separating it from the branch above.
    failed = rn.derive_release_status(
        replace(rn.RECORDED_GATE_OBSERVATION, conclusion="failure", legs="2/3"),
        covered,
    )
    assert not failed.established and rn.NOT_ESTABLISHED in failed.statement, (
        "a FAILED run covering the released commit was accepted as evidence of readiness — "
        "that is DF-AUD-APAA-C with the sha filled in"
    )
    assert not _executed_gate_citations(failed.statement)


def test_TC_ArgusAgent_DOCS_001_25b_the_release_surface_scan_actually_bites() -> None:
    """TC-ArgusAgent-DOCS-001-25b — Story 12.9 / AC2: positive control, on a REAL surface.

    MEASURED on `de05dec`: every registered release surface produces ZERO live status claims
    today, so `-24` passes by finding nothing — and a guard that passes by finding nothing
    proves nothing until it has been shown to find something. The strongest available control
    is the real corpus with the real defect planted in it: `README.md`'s own bytes, plus the
    verbatim historical sentence from `sprint-change-proposal-2026-07-28.md:63`.

    `-21b` is the same control over the planning-record population; this is deliberately not
    a copy of it — it runs the detector over a surface that is really on disk, which is the
    only way to show that the scan reaches these files at all.

    **RE-POINTED 2026-08-16, twice; the second reason is the load-bearing one.** The original
    control asserted `README.md` cites NO executed gate, so a planted claim could not be
    excused by a citation that did not exist. `03f3a39` replaced that with `assert
    _executed_gate_citations(readme)` — README MUST carry one — the same structurally
    unsatisfiable demand `-25` carried, failing for the same reason: README carries whatever
    the derivation says about the commit in hand, and on a moving branch that is the
    stale-run statement, which is deliberately not readable as a citation. The property kept
    holds on BOTH branches and needs neither: **every citation README carries comes from the
    one derivation, and none from anywhere else.** Strip the derived statement and not one
    run id may remain. A broken scan would satisfy that trivially, so it carries its OWN
    control — a synthetic citation spliced into the stripped text must be found — and the
    planted status defect then runs over those stripped bytes, which is the original
    control's premise restored by construction, not by assumption.
    """
    readme = (_REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert not _status_assertions(readme), (
        "README.md now asserts a release status; resolve it as a finding (cite, or record "
        "NOT ESTABLISHED), never by loosening the detector"
    )

    derived = rn.derive_release_status(rn.RECORDED_GATE_OBSERVATION, _head_sha()).statement
    assert _flatten(derived) in _flatten(readme), (
        "README.md no longer renders the derived release-status statement, so the 'every "
        "citation comes from the derivation' property below is being asserted about a "
        "surface the derivation does not reach (`-25` states this too, and states it first)"
    )
    stripped = _flatten(readme).replace(_flatten(derived), " ")
    assert not _executed_gate_citations(stripped), (
        "README.md mints a citation that is NOT the derived statement. Every excuse this "
        "surface offers a status claim must come from the one derivation; a second run id "
        "typed onto the page is the transcription class AI-E9-7 forbids, and it would "
        "excuse claims on the strength of evidence nobody re-derived:\n"
        f"{_executed_gate_citations(stripped)}"
    )
    # ...and that scan is NOT passing by being blind: a hand-typed citation of exactly the
    # forbidden shape, spliced into the same stripped bytes, must be found.
    assert _executed_gate_citations(
        stripped + " Run 31341363300 concluded success at sha 00c8d1b with 3/3 legs green."
    ), (
        "a hand-typed 'run id + sha' citation spliced into README's own bytes was NOT "
        "detected, so the assertion above passes by finding nothing and proves nothing"
    )

    planted_body = (
        "\n\n## Release status\n\n"
        "- **Release Status**: Upgraded from `NEEDS TARGETED REWORK` to **READY FOR "
        "RELEASE**!\n"
    )
    caught = _status_assertions(readme + planted_body)
    assert caught, (
        "an uncited affirmative release-status claim planted on a REAL release surface was "
        "not caught. The detector does not reach these files, and `-24` is vacuous."
    )
    assert {claim for claim, _ in caught} == {"ready for release"}

    # The original control, over the same real bytes with the earned citation removed: with
    # nothing to excuse it, the planted claim stands uncited and `-24` would fail on it.
    assert _status_assertions(stripped + planted_body)
    assert not _executed_gate_citations(stripped + planted_body), (
        "the planted claim would have been excused by a citation this surface did not earn"
    )

    # And the honest sentences this project publishes must NOT be flagged — asserted against
    # the real derived statements, never a paraphrase. BOTH branches, from real observations
    # over real shas: each observation is asked about the sha its OWN run covers (citation)
    # and about the sha the OTHER run covers (stale), so neither branch is reached only by a
    # synthetic input and neither depends on where HEAD happens to stand.
    head = _head_sha()
    observations = (rn.RECORDED_GATE_OBSERVATION, *rn.SUPERSEDED_GATE_OBSERVATIONS)
    shas = tuple(observation.run_sha for observation in observations) + (head,)
    branches: set[bool] = set()
    for observation in observations:
        for sha in shas:
            status = rn.derive_release_status(observation, sha)
            branches.add(status.established)
            assert not _status_assertions(status.statement), (
                "a derived release-status statement was flagged as an unevidenced status "
                f"claim:\n\n{status.statement}"
            )
    assert branches == {True, False}, (
        f"every derived statement swept above landed on the same branch ({branches}), so "
        "only half the rule was exercised by real observations"
    )
