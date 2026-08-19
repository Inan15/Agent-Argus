"""Story 10.2 / AC1-AC2 — a delivered capability cannot still be specified as deferred.

Verification area ArgusAgent-DOCS (``TC-ArgusAgent-DOCS-001-24``..``-27``, CONTINUING the index
locked by Story 8.4; ``-01``..``-19`` belong to ``tests/test_release_note.py`` and
``tests/test_release_surface_honesty.py``, ``-20``..``-23`` to ``tests/test_evidence_citation.py``
and ``tests/test_status_document_registry.py`` — *(amended 2026-08-17 by Story 13.4: that range now
has TWO hosts, split along a cohesion boundary — the derivation stays in the first, and ``-21``/
``-22`` plus the governed population moved to the second. No id was renumbered.)*).

**The defect under repair (``DF-AUD-APAA-D``).** Multi-language AST grounding entered the product
through ``sprint-change-proposal-2026-07-28.md:18`` with no story and no specification amendment.
The capability shipped; every specification kept calling it V2. That is the *undersell* direction of
the same class Story 10.5 files in the oversell direction, and it double-counts delivered work on
the V2 roadmap.

**Why this file exists rather than a corrected list.** The site enumeration has now been wrong
THREE times — 4 sites, then 7, then 10, and measurement on 2026-08-10 found **12 to amend plus 2 to
exempt**. A hand-counted list closes today's instance; only a closure guard closes the class. This
is Story 10.2's load-bearing AC (DN-4), not the amendment itself.

**Why it is a NEW file and not an extension of ``test_evidence_citation.py``.** That guard governs
*status* claims in *status* documents (change proposals and retrospectives) under Story 10.1's
citation rule. This one governs *scope* claims in *specification* documents under a different rule
with a different vocabulary. The registry-plus-glob-closure SHAPE is copied deliberately (story §D /
10.1's precedent); the corpus, the pattern and the exemptions are this story's.

**The corpus is deliberately narrow: ``E-PRD/*.md`` and ``architecture.md``.** Story files, change
proposals and the deferred-work ledger DISCUSS the V2/V1 question — this very story file is full of
the phrase *"multi-language ... V2"* — and a guard that fires on the project's own meta-discussion
cries wolf and gets deleted by the third person to hit it (10.1's D2 lesson, learned the same way).
A specification says what the product IS; a proposal says what changed. Only the first is bound.

**Four known ways a guard like this lies, and what stops each.**

1. *It names the files that existed when it was written* (AI-E8-6). Stopped by ``-26``: the corpus is
   resolved by **glob**, and any matching file that is not registered fails.
2. *It freezes a line list, so a claim rewritten at a new line escapes.* Stopped by ``-24``: the
   claim is a PATTERN over sentence-scoped units, never a line number. Line numbers in this project
   drift under the amendment cascade; every site here is located by content.
3. *Its exemption swallows what it looks for* (the ``-17b`` escape, found by review, not by the
   author). Stopped by ``-25``, a positive control in **both** directions, and by ``-26``, which
   requires every exemption to be reasoned AND to be exercised — an exemption that matches nothing
   is dead weight that silently widens over time.
4. *It is only ever run after the fix* (AI-E3-1: Story 3.4's keystone test was green over its own
   keystone bug). Every assertion here was demonstrated RED against the unamended specifications
   before the amendments landed; the run is recorded in the story's Dev Agent Record.

**No network, no LLM, no subprocess, no ``.argus/`` write** — pure ``pathlib`` + ``re`` over
committed markdown, so it runs identically on all three CI legs. Every file is opened
``encoding="utf-8"`` explicitly: the artifact tree carries ``~~``, ``⚠️``, ``🚩`` and Cyrillic, and an
inherited host locale is the exact defect class that turned run ``31322881580`` red.
"""

from __future__ import annotations

import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACT_DIR = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"

_GUARD_FILE = "tests/test_spec_claim_scope.py"

# The SPECIFICATION corpus, as measured on 2026-08-10. These are the documents that state what the
# product IS; `-26` resolves the patterns below against the tree and fails on anything found there
# that nobody registered.
_SPEC_DOCUMENTS: tuple[str, ...] = (
    "E-PRD/prd.md",
    "E-PRD/addendum.md",
    "E-PRD/.memlog.md",
    "architecture.md",
)

# `E-PRD/*.md` deliberately, not `**/*.md`: the artifact directory also holds stories, change
# proposals, retrospectives and the ledger, which are governed elsewhere (see the module docstring).
# `pathlib.Path.glob` does NOT skip dotfiles, so `.memlog.md` is inside the closure and must be
# registered — that is the point of resolving the set instead of typing it.
_SPEC_PATTERNS: tuple[str, ...] = (
    "E-PRD/*.md",
    "architecture.md",
)

# ─────────────────────────────────────────────────────────────────────────────
# The claim shape — measured against the real corpus before it was written (10.1's D2)
# ─────────────────────────────────────────────────────────────────────────────

# A term that names the capability. Bare "multi-language" is not enough on its own: the phrase also
# appears about test-file conventions and stack detection, which are not AST grounding.
_MULTILANG_TERMS: tuple[str, ...] = (
    "multi-language",
    "multi language",
    "multilanguage",
)

# A term that says the sentence is about DEEP AST GROUNDING rather than, say, packaging metadata.
# `deep` and `tree-sitter` are here because the first RED run proved they are load-bearing:
# architecture.md:317 reads *"V1 deep = Python only, `claim_emitted` proxy elsewhere"* and contains
# no other grounding word at all. Without them the guard missed one of the twelve sites it was
# written for — the same under-count, in the same document, for the fourth time.
_GROUNDING_TERMS: tuple[str, ...] = (
    "ast",
    "grounding",
    "grounded",
    "grounds",
    "grammar",
    "deep",
    "tree-sitter",
)

# Deferral vocabulary. Matched with word boundaries: `\bv2\b` must not fire on "V1.5", and
# "deferred" must not fire on "deferred-work.md" as a bare path (it does not; the hyphen breaks it).
_DEFERRAL_MARKERS: tuple[str, ...] = (
    r"\bv2\b",
    r"\bpost-v1\b",
    r"future enhancement",
    r"\bdeferred\b",
    r"growth features",
    r"\broadmap\b",
)
_DEFERRAL_RE = re.compile("|".join(_DEFERRAL_MARKERS))

# The OTHER half of the unamended shape, and the half every prior enumeration under-counted: a
# sentence does not need the word "V2" to scope deep grounding to Python. "AST = Python in V1" and
# "V1 deep = Python only" are scope claims with no V2 marker in them at all, which is exactly how
# architecture.md:89 and :800 survived three hand-counts.
_PYTHON_ONLY_TERMS: tuple[str, ...] = (
    "python only",
    "python-only",
    "python in v1",
    "python v1",
    "python ast in v1",
    "= python",
)

# The AMENDED shape. A sentence that records the capability as delivered is the fix, not the defect,
# and must not fire — this is the `-25` reverse control. Note the pleasing constraint: the guard's
# only escape hatch is the literal wording AC1 requires the amendment to carry, so an amendment that
# quiets the guard is an amendment that satisfies the AC.
_DELIVERY_MARKERS: tuple[str, ...] = (
    "delivered in v1",
    "shipped in v1",
    "grounded in v1",
    "no longer deferred",
    "delivered by `sprint-change-proposal-2026-07-28.md`",
    "delivered by sprint-change-proposal-2026-07-28.md",
)

# EXEMPTIONS ARE DATA WITH REASONS (AC1.4 / AC2.5 / DN-2), never silence. Silent omission is the
# `_PRESERVED_RECORD` anti-pattern 10.1's DN-5 already ruled on. Each key is an anchor substring of
# the offending unit, lower-cased; `-26` asserts each one is both REASONED and EXERCISED, so a
# stale exemption for a sentence that no longer exists cannot sit here quietly widening the guard.
#
# ⚠️ EMPTY SINCE 2026-08-15 (Story 12.5 / NFR-P3), and the emptiness is a RESULT, not an omission.
# Story 10.2 opened this table with exactly two entries, both quoting architecture.md's *"the
# default public install grounds **Python only**"* — TRUE statements about the default install
# rather than V1/V2 scope claims, exempted BY NAME and fenced to Story 12.5, which owned the
# packaging decision. 12.5 took that decision: the nine grammars are promoted to
# `[project.dependencies]`, both sentences are STRUCK in architecture.md (§3.4 — struck, never
# deleted), and `_strip_struck` therefore no longer presents them to the scanner. Keeping the
# exemptions would have failed `-26`'s own EXERCISED half, which is the guard working as designed:
# an exemption that matches nothing is a silent licence that grows. `-26` asserts the shape of
# every entry that IS here; it deliberately does NOT require the table to be non-empty, because
# "no document currently needs an exemption" is the healthiest state this table can be in and a
# non-emptiness assertion would pressure a future story to invent one.
_EXEMPT_BY_DESIGN: dict[str, str] = {}


class _Unit:
    """One scan unit: a sentence, plus the nearest enclosing heading for MARKER context only.

    The heading is consulted for deferral markers and never for claim terms, because a section
    called *"Growth Features (V2)"* supplies the V2 that its list items omit — which is precisely
    how ``prd.md:214`` carried a delivered capability on the V2 roadmap while no sentence on that
    line contained the string ``V2``.
    """

    __slots__ = ("document", "heading", "text")

    def __init__(self, document: str, heading: str, text: str) -> None:
        self.document = document
        self.heading = heading
        self.text = text

    def __repr__(self) -> str:  # pragma: no cover - diagnostic only
        return f"<{self.document} :: {self.text[:120]!r}>"


# A strikethrough span, bounded so it cannot cross a blank line — an unterminated `~~` must not pair
# with a closing `~~` further down and silently retract everything between them. Copied from
# `test_evidence_citation.py` on purpose: struck text is RETRACTED, and striking (never deleting) is
# the §3.4 form every amendment in this story uses.
_STRUCK_RE = re.compile(r"~~(?:[^\n]|\n(?!\s*\n))+?~~")

# A line that OPENS a new unit: heading, list item, table row, blockquote. Anything else continues
# the unit it follows. This differs from `test_evidence_citation.py::_split_sentences`, which
# collapses whole paragraphs: these documents are dense markdown tables and bullet lists, and
# collapsing a ten-row table into one unit lets a grounding term in one row co-occur with a
# Python-only term in another and manufacture a hit that no sentence actually makes.
_UNIT_OPENER_RE = re.compile(r"^\s*(#{1,6}\s|[-*+]\s|\d+\.\s|\||>)")
_HEADING_RE = re.compile(r"^\s*#{1,6}\s+(.*)$")


def _strip_struck(text: str) -> str:
    """Remove ``~~struck~~`` spans: struck wording is RETRACTED, and retracting is the §3.4 form.

    Without this, the mandated fix (strike the V2 wording, write the delivered wording beside it)
    would look identical to the defect, and the guard would forbid the only correction the project's
    evidence-immutability rule permits.
    """
    return _STRUCK_RE.sub(" ", text)


def _scan_units(document: str, text: str) -> list[_Unit]:
    """Split *text* into heading-scoped, sentence-ish scan units."""
    units: list[_Unit] = []
    heading = ""
    buffer: list[str] = []

    def flush() -> None:
        if not buffer:
            return
        flat = " ".join(" ".join(buffer).split())
        buffer.clear()
        if not flat:
            return
        for part in flat.split(". "):
            stripped = part.strip()
            if stripped:
                units.append(_Unit(document, heading, stripped.lower()))

    for line in _strip_struck(text).splitlines():
        if not line.strip():
            flush()
            continue
        match = _HEADING_RE.match(line)
        if match:
            flush()
            heading = match.group(1).strip().lower()
            continue
        if _UNIT_OPENER_RE.match(line):
            flush()
        buffer.append(line)
    flush()
    return units


def _is_amended(unit: _Unit) -> bool:
    return any(marker in unit.text for marker in _DELIVERY_MARKERS)


def _exemption_for(unit: _Unit) -> str | None:
    for anchor in _EXEMPT_BY_DESIGN:
        if anchor in unit.text:
            return anchor
    return None


def _raw_claims(units: list[_Unit]) -> list[tuple[str, _Unit]]:
    """Every (rule, unit) matching the unamended claim shape, BEFORE exemptions are applied.

    Two rules, because the defect has two grammatical forms and the second one is the one three
    hand-counts missed:

    ``deferral``
        the capability named together with a deferral marker — "multi-language AST (V2)",
        "Deferred (post-V1): multi-language AST", a bullet under *Growth Features (V2)*;
    ``python-only-scope``
        deep grounding scoped to Python with no V2 marker anywhere — "AST = Python in V1",
        "V1 deep = Python only", "(Python AST in V1)".
    """
    hits: list[tuple[str, _Unit]] = []
    for unit in units:
        if _is_amended(unit):
            continue
        grounded = any(term in unit.text for term in _GROUNDING_TERMS)
        if not grounded:
            continue
        if any(term in unit.text for term in _MULTILANG_TERMS) and _DEFERRAL_RE.search(
            f"{unit.heading} {unit.text}"
        ):
            hits.append(("deferral", unit))
            continue
        if any(term in unit.text for term in _PYTHON_ONLY_TERMS):
            hits.append(("python-only-scope", unit))
    return hits


def unamended_scope_claims(document: str, text: str) -> list[tuple[str, _Unit]]:
    """Every live, unexempted, unamended scope claim in *text* (the guard's operative function)."""
    return [
        (rule, unit)
        for rule, unit in _raw_claims(_scan_units(document, text))
        if _exemption_for(unit) is None
    ]


def _registered_paths() -> list[Path]:
    return [_ARTIFACT_DIR / name for name in _SPEC_DOCUMENTS]


def test_TC_ArgusAgent_DOCS_001_24_no_specification_defers_a_delivered_capability() -> None:
    """TC-ArgusAgent-DOCS-001-24 — Story 10.2/AC1+AC2: the rule, enforced over the whole corpus.

    Multi-language AST grounding is DELIVERED. No specification document may still record it as V2 /
    post-V1 / deferred / a future enhancement, and none may scope deep AST grounding to Python in V1
    — except the two default-install sentences exempted by name above, which are true.

    Non-vacuity is asserted directly: a registry of unreadable or empty files would satisfy every
    assertion below without reading a word.
    """
    assert _SPEC_DOCUMENTS, "the specification registry is empty — the guard scans nothing"

    scanned = 0
    surviving: list[str] = []
    for path in _registered_paths():
        rel = path.relative_to(_REPO_ROOT).as_posix()
        assert path.is_file(), f"registered specification document is missing: {rel}"

        text = path.read_text(encoding="utf-8")
        units = _scan_units(rel, text)
        assert units, f"{rel} parsed to ZERO scan units — the splitter is broken and this is vacuous"
        scanned += 1

        for rule, unit in unamended_scope_claims(rel, text):
            surviving.append(f"  [{rule}] {rel}: {unit.text[:220]}")

    assert scanned == len(_SPEC_DOCUMENTS), (
        f"only {scanned} of {len(_SPEC_DOCUMENTS)} registered specification documents were scanned"
    )
    assert not surviving, (
        "specification site(s) still record multi-language AST grounding as deferred, or still "
        "scope deep AST grounding to Python in V1, while the capability has shipped since "
        "`sprint-change-proposal-2026-07-28.md` (DF-AUD-APAA-D):\n"
        + "\n".join(surviving)
        + "\n  fix: amend each site in the §3.4 form — STRIKE the replaced wording (~~…~~), never "
        "delete it, and write the replacement so it records the capability as DELIVERED IN V1, "
        "dated and attributed. If a site is a TRUE statement about the default install rather "
        f"than a scope claim, add it to _EXEMPT_BY_DESIGN in {_GUARD_FILE} WITH ITS REASON."
    )


def test_TC_ArgusAgent_DOCS_001_25_the_claim_detector_actually_bites() -> None:
    """TC-ArgusAgent-DOCS-001-25 — Story 10.2/AC2.3: positive control, in BOTH directions.

    A guard whose filters swallow the thing it looks for passes over any text, and `-17b` proved
    this project ships that bug when nobody plants a control. Every string below is a pure-function
    check over a planted literal — never over the real files, which `-24` already reads.
    """
    # --- direction 1: the verbatim historical defects MUST fire ---
    for planted, why in (
        (
            "- **Deferred (post-V1):** multi-language AST, seam auditor, mutation-grade vacuous.",
            "architecture.md:267 verbatim — the deferral list",
        ),
        (
            "- **Future enhancement:** multi-language AST (V2), seam auditor (V2).",
            "architecture.md:800 verbatim — the future-enhancement list",
        ),
        (
            "- **Stack:** Python 3.11+ (Minions baseline); AST = Python in V1 "
            "(`claim_emitted` proxy elsewhere).",
            "architecture.md:89 verbatim — a Python-only scope claim with NO V2 marker, the shape "
            "three hand-counts missed",
        ),
        (
            "- **Stack detection** via `cloc`/`radon` + tree-sitter; V1 deep = Python only.",
            "architecture.md:317 verbatim — the same shape again",
        ),
        (
            "- **FR7:** APAA can validate a deep claim against source structure (Python AST in V1) "
            "and downgrade an unverifiable claim.",
            "prd.md:469 verbatim — FR7, the BINDING capability contract",
        ),
        (
            "- **NFR-P2:** The audit is **stack-agnostic by construction** (deep AST-grounding = "
            "Python in V1; `claim_emitted` proxy elsewhere).",
            "prd.md:571 verbatim — NFR-P2",
        ),
        (
            "  durableMoat: 'AST-grounded depth [Python V1, multi-language V2] + Prosecutor'",
            "prd.md:23 verbatim — the moat statement",
        ),
    ):
        assert unamended_scope_claims("planted.md", planted), (
            f"the detector MISSED a verbatim site this story exists to close ({why}): {planted!r}. "
            "A guard that cannot catch the sentences it was written for catches nothing."
        )

    # A claim can inherit its deferral marker from the SECTION it sits in — prd.md:214's Growth
    # Features list names no V2 on the line itself.
    assert unamended_scope_claims(
        "planted.md",
        "### Growth Features (V2)\n"
        "Bidirectional traceability · **multi-language** AST grounding · mutation-grade vacuous.\n",
    ), (
        "a delivered capability listed under a section heading marked (V2) escaped, because the "
        "line itself contains no deferral marker. The V2 roadmap must not be able to re-scope "
        "delivered work by putting the marker in the heading (AC1.2)."
    )

    # A NEWLY WRITTEN claim at a NEW line must be caught: the pattern is not a line list (AC2.2).
    assert unamended_scope_claims(
        "planted.md",
        "- **Somebody's new bullet, written next year:** multi-language AST grounding is deferred "
        "to V2 along with the seam auditor.\n",
    ), "a newly written V2 deferral at a new line escaped — the guard has frozen into a line list"

    # A dangling `~~` must not retract the rest of the document.
    assert unamended_scope_claims(
        "planted.md",
        "~~an old struck note\n\n- **Deferred (post-V1):** multi-language AST.\n\nmore text~~",
    ), (
        "an unterminated strikethrough span swallowed a live claim in a later block — a "
        "one-character way to hide a scope claim from this guard"
    )

    # --- direction 2: correctly amended text must NOT fire ---
    for honest, why in (
        (
            "- **FR7:** APAA can validate a deep claim against source structure — "
            "~~(Python AST in V1)~~ **AST grounding is delivered in V1 for every language "
            "enumerated in `argus/shared/source_languages.py`** — and downgrade an unverifiable "
            "claim.",
            "the mandated amendment shape: strike the old wording, state delivery",
        ),
        (
            "- **Deferred (post-V1):** ~~multi-language AST,~~ seam auditor, mutation-grade "
            "vacuous. *(Amended 2026-08-10, Story 10.2: multi-language AST grounding was "
            "delivered in V1 and is struck from this list.)*",
            "the deferral list with the delivered item struck and the strike explained",
        ),
        (
            "Multi-language AST grounding is **delivered in V1** and is therefore no longer a V2 "
            "growth feature.",
            "a sentence that names V2 only to say the capability left it",
        ),
        (
            "- **Stack:** Python 3.11+ (Minions baseline); AST grounding is delivered in V1 for "
            "the languages in `argus/shared/source_languages.py`.",
            "the amended stack line",
        ),
    ):
        assert not unamended_scope_claims("planted.md", honest), (
            f"the detector flagged CORRECTLY AMENDED text as an unamended claim ({why}): "
            f"{honest!r}. A guard that forbids the fix makes the fix impossible."
        )

    # A struck claim alone is retracted, not asserted.
    assert not unamended_scope_claims(
        "planted.md", "- ~~**Deferred (post-V1):** multi-language AST, seam auditor.~~"
    ), (
        "a STRUCK claim was still counted; striking is how this project retracts (§3.4 evidence "
        "immutability), and a guard that ignores it makes the correct fix impossible"
    )

    # Packaging prose about the OPTIONAL EXTRA is a different subject and must not be swept in by
    # the exemption machinery being absent — it is caught, then exempted, by `-26`.
    assert not unamended_scope_claims(
        "planted.md",
        "- The `[languages]` extra ships nine grammars; installing it is one command.",
    ), "the detector fired on packaging prose that makes no scope claim at all"


def test_TC_ArgusAgent_DOCS_001_26_the_specification_set_is_closed_and_exemptions_are_reasoned() -> None:
    """TC-ArgusAgent-DOCS-001-26 — Story 10.2/AC2.1+2.4+2.5: no new spec file can escape the rule.

    The failure shape is always the same and this project shipped it five times in one epic
    (AI-E8-6): the guard names the files that existed when it was written, and the next file added
    is outside it. The globs are resolved against the tree and anything unregistered fails.

    Exemptions are asserted twice over: each must carry a substantive written reason (an exemption
    without one is an oversight wearing a decision's clothes), and each must be EXERCISED — it must
    actually suppress a unit the pattern really flags on disk. An exemption that matches nothing is
    a silent licence that grows.
    """
    found: set[str] = set()
    for pattern in _SPEC_PATTERNS:
        for path in _ARTIFACT_DIR.glob(pattern):
            if path.is_file():
                found.add(path.relative_to(_ARTIFACT_DIR).as_posix())

    assert found, (
        f"the specification patterns {_SPEC_PATTERNS} resolved to NOTHING under {_ARTIFACT_DIR} — "
        "the globs are broken and every other assertion in this file is vacuous"
    )

    unregistered = sorted(found - set(_SPEC_DOCUMENTS))
    assert not unregistered, (
        f"specification document(s) exist but are not registered: {unregistered}. Add them to "
        f"_SPEC_DOCUMENTS in {_GUARD_FILE} so the scope rule covers them — a new PRD companion is "
        "exactly the kind of document that restates a V1/V2 boundary."
    )

    missing = sorted(set(_SPEC_DOCUMENTS) - found)
    assert not missing, (
        f"registered document(s) are no longer found by the globs: {missing}. Either they were "
        "moved/deleted (§3.4: records are superseded, never erased) or the patterns drifted."
    )

    # Exemptions carry reasons. An EMPTY table is legitimate and is not asserted against
    # (Story 12.5 emptied it by striking the two sentences it excused — see the table's own
    # comment): requiring non-emptiness would make "nothing needs an exemption" a failure, and
    # would pressure a future story to invent an entry to satisfy the guard. What is asserted is
    # the shape of every entry that IS present, in both directions, which is where the risk is.
    for anchor, reason in _EXEMPT_BY_DESIGN.items():
        assert len(reason.split()) >= 20, (
            f"exemption {anchor!r} has no substantive reason recorded. An exemption without a "
            "reason is an oversight wearing a decision's clothes (_PRESERVED_RECORD precedent, "
            "10.1 DN-5)."
        )

    # …and every exemption is EXERCISED against the real corpus (AC2.4 non-vacuity).
    exercised: dict[str, int] = {anchor: 0 for anchor in _EXEMPT_BY_DESIGN}
    for path in _registered_paths():
        rel = path.relative_to(_REPO_ROOT).as_posix()
        for _rule, unit in _raw_claims(_scan_units(rel, path.read_text(encoding="utf-8"))):
            anchor = _exemption_for(unit)
            if anchor is not None:
                exercised[anchor] += 1

    unexercised = sorted(a for a, n in exercised.items() if n == 0)
    assert not unexercised, (
        f"exemption(s) matched NOTHING the pattern actually flags: {unexercised}. Either the "
        "sentence they excuse has been edited (re-derive the anchor and re-check that the reason "
        "still holds — it belongs to Story 12.5 / NFR-P3), or the exemption was never needed and "
        "is silently widening the guard. Both are defects (AC2.4)."
    )


def test_TC_ArgusAgent_DOCS_001_27_the_amendment_is_written_attributed_and_sourced() -> None:
    """TC-ArgusAgent-DOCS-001-27 — Story 10.2/AC1.1+1.2+1.3: the positive half of the rule.

    `-24` asserts the old claim is GONE. That is satisfiable by deletion, and deletion is what §3.4
    forbids: the record of what the specification used to say is the evidence that the drift
    happened. So this asserts the amendment is PRESENT, in the mandated shape — struck original,
    dated attribution, and (for the two load-bearing requirements) a pointer at the code that is the
    source of truth for the language set rather than a hand-typed list, which is trap E.5:
    AI-E9-7/R1 saw a prose copy of a pinned figure drift at five separate sites.
    """
    prd = (_ARTIFACT_DIR / "E-PRD" / "prd.md").read_text(encoding="utf-8")
    arch = (_ARTIFACT_DIR / "architecture.md").read_text(encoding="utf-8")

    # FR7 is the BINDING capability contract (prd.md: "a capability not listed here will not exist
    # in V1 unless explicitly added"). It carries the heaviest requirement of the twelve.
    fr7 = next((line for line in prd.splitlines() if line.startswith("- **FR7:**")), "")
    assert fr7, "prd.md no longer contains an `- **FR7:**` line — the binding contract moved"
    for required, why in (
        ("~~", "the replaced wording must be STRUCK, not deleted (§3.4 evidence immutability)"),
        ("delivered in V1", "FR7 must record multi-language AST grounding as delivered"),
        (
            "argus/shared/source_languages.py",
            "FR7 must point at the SOURCE OF TRUTH for the grounded language set, not a "
            "hand-typed list (trap E.5 / AI-E9-7)",
        ),
        ("2026-08-10", "the amendment is dated"),
    ):
        assert required in fr7, (
            f"prd.md FR7 amendment is missing {required!r} — {why}.\n  FR7 now reads: {fr7[:400]!r}"
        )

    nfr_p2 = next((line for line in prd.splitlines() if line.startswith("- **NFR-P2:**")), "")
    assert nfr_p2, "prd.md no longer contains an `- **NFR-P2:**` line"
    for required in ("~~", "delivered in V1", "argus/shared/source_languages.py", "2026-08-10"):
        assert required in nfr_p2, (
            f"prd.md NFR-P2 amendment is missing {required!r}; NFR-P2 is the other load-bearing "
            f"site (AC1.3).\n  NFR-P2 now reads: {nfr_p2[:400]!r}"
        )

    # AC1.2 — the V2 roadmap and the deferral lists no longer CARRY it, and each says why.
    for text, name, anchor in (
        (prd, "prd.md", "Growth Features (V2)"),
        (arch, "architecture.md", "**Deferred (post-V1):**"),
        (arch, "architecture.md", "**Future enhancement:**"),
    ):
        assert anchor in text, f"{name} no longer contains {anchor!r} — locate the site by content"

    assert "sprint-change-proposal-2026-07-28.md" in prd, (
        "prd.md amendments must be ATTRIBUTED to `sprint-change-proposal-2026-07-28.md`, the "
        "change that shipped the capability with no story and no amendment (AC1.1)"
    )
    assert "sprint-change-proposal-2026-07-28.md" in arch, (
        "architecture.md amendments must carry the same attribution (AC1.1)"
    )

    # ── Story 12.5 / NFR-P3, 2026-08-15 ────────────────────────────────────────────────────
    # Until this date the two sentences below were EXEMPT here by name (see `_EXEMPT_BY_DESIGN`):
    # they were TRUE statements about the default install, not V1/V2 scope claims, and the
    # packaging decision that would make them false belonged to Story 12.5. That decision has now
    # been taken, so the same two sentences are asserted in their AMENDED form — present but
    # STRUCK, with the resolution recorded beside them. This is the amendment protocol the whole
    # file enforces, applied to the one pair of sentences it previously had to exempt from it.
    assert "packaging decision resolved by story 12.5 (nfr-p3)" in arch.lower(), (
        "architecture.md no longer records that the NFR-P3 packaging decision was RESOLVED by "
        "Story 12.5. The decision is the load-bearing fact — `pyproject.toml` alone cannot say "
        "WHY the nine grammars are core dependencies, or that the alternative was rejected."
    )
    for struck in (
        "~~⚠️ **Open packaging decision, owned by Story 12.5 (NFR-P3).**",
        "~~⚠️ **open packaging decision owned by Story 12.5** (§L446-447):",
    ):
        assert struck in arch, (
            f"architecture.md does not carry {struck!r} in STRUCK form. Both sentences were true "
            "of every release before 12.5, and §3.4 says a superseded record is struck and never "
            "deleted — deleting them erases the evidence that the default install ever grounded "
            "Python only, which is the fact that makes this change auditable."
        )
    assert "Python only" in arch, (
        "the superseded default-install wording has vanished from architecture.md entirely. "
        "Non-vacuity for the two assertions above: they must be checking live text."
    )
