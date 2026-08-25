"""Story 17.2 / AC5 — the successor-predicate specification is CHECKED, not asserted.

``TC-ArgusAgent-PRECISION-001-142``..``-144``. Story 17.2 lands a **document** and a
**ledger disposition** and no executable predicate — Story 17.3 builds ``S1``. A document
is not falsifiable on its own, so the three guards below turn its checkable claims into
observables that can go RED:

    -142  every figure the specification attributes to a committed artifact RE-DERIVES
          from that artifact. Extraction is ANCHORED to an explicit marker pair, and the
          anchoring itself is driven adversarially with a decoy.
    -143  the mock-binding decision (§7.3) rests on a MEASURED fact: an ``ast`` walk over
          every module of the ``argus`` package classifies each reference to
          ``mock_referencing_assertions`` and finds EXACTLY ONE decision site.
    -144  the specification QUOTES ``SILENT_CLASS_DEFINITION`` character for character,
          and no commit in Story 17.2's arc touches the ``argus`` package.

**GUARD-ADEQUACY CLAUSE (`architecture.md`, Story 13.2 / AC8.4), discharged per guard.**
Two of the three assert a NEGATIVE, which is the shape that goes green by finding nothing.
Each therefore states (i) its observable, (ii) a demonstration that the defect MOVES that
observable — driven RED at the REAL SEAM by an executed mutation of the real artifact or
the real module, recorded in the story file with the restore sha256 — and (iii) at least
one adversarial variant GENERATED from the record it closes over, with its count asserted.

⚠️ **17.1's one review finding was an UNANCHORED WHOLE-DOCUMENT REGEX** in this same area
id: a same-shaped table row planted above the heading resolved the wrong row and the check
returned silently. ``-142`` extracts figures from a markdown document, which is the same
defect class one story later, so its extractor is anchored to
``<!-- CITED-FIGURES:BEGIN -->``/``<!-- CITED-FIGURES:END -->`` and a decoy row carrying a
wrong value is planted OUTSIDE the anchors on every run. The decoy must be invisible to the
anchored extractor **and** visible to an unanchored one — the second half is what proves the
input actually carries the defect, rather than proving the extractor found nothing.

⛔ **A fourth guard cross-checking the ``DF-INV-VACUOUS-B`` disposition was CONSIDERED and
DECLINED** (`DN-17-2-9`): ``TC-ArgusAgent-DOCS-001-78`` already cross-checks every story
file's closure claims against ``deferred-work.md`` in both directions, with its own
non-vacuity floor and its own generated adversarial variants. An id-scoped copy would be an
``AR7`` fork of a working guard.

**PURE except for read-only ``git`` verbs** (``AR8``). No network, no LLM, no write, no
``.argus/`` output. Every file is opened ``encoding="utf-8"`` explicitly: the artifact tree
carries non-ASCII, and an inherited host locale is the exact defect class that turns the
ubuntu CI legs red against a green Windows local gate (``AI-E13-1``).
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACT_DIR = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_SPECIFICATION = _ARTIFACT_DIR / "successor-vacuity-predicate-specification.md"
_SILENT_CLASS_RECORD = _ARTIFACT_DIR / "validation-corpus" / "silent-class-record.json"
_STORY_FILE = (
    _ARTIFACT_DIR / "stories" / "17-2-a-different-predicate-argued-as-one.md"
)
_ARGUS_PACKAGE = _REPO_ROOT / "argus"

#: The anchors. The extractor reads BETWEEN these and nowhere else — 17.1's review finding,
#: one story later, in the same area id.
_FIGURES_BEGIN = "<!-- CITED-FIGURES:BEGIN -->"
_FIGURES_END = "<!-- CITED-FIGURES:END -->"
_QUOTATION_BEGIN = "<!-- SILENT-CLASS-DEFINITION-QUOTATION:BEGIN -->"
_QUOTATION_END = "<!-- SILENT-CLASS-DEFINITION-QUOTATION:END -->"

#: A row of the anchored figure table: ``| `key` | **value** | authority |``.
_FIGURE_ROW = re.compile(r"^\|\s*`([A-Za-z0-9_.\-]+)`\s*\|\s*\*\*(\d+)\*\*\s*\|")

#: The floor the extraction must clear before any comparison is allowed to observe
#: anything. Measured when this guard landed: the specification cites 19 figures.
_MIN_FIGURES = 15

#: The number of modules the ``argus`` package must parse to before an ABSENCE claim over
#: it means anything. Measured at 95 when this guard landed; the floor is set below that so
#: a legitimate cohesion split does not redden the guard, and far above zero so a broken
#: walk does.
_MIN_ARGUS_MODULES = 60

#: The name whose decision sites §7.3 counts.
_MREF = "mock_referencing_assertions"

#: The ONE decision site the specification claims, as a repository-relative posix path.
_KNOWN_DECISION_SITE = "argus/detectors/vacuous_test.py"

#: This story's commits, identified by the ``(17-2)`` scope every commit in its arc carries
#: (``chore(17-2)``/``docs(17-2)``/``fix(17-2)``). ⛔ If the arc's message convention ever
#: changes, THIS SELECTOR IS UPDATED — never deleted, and never widened to "all commits
#: since the baseline", which would go RED the moment Story 17.3 legitimately writes inside
#: the ``argus`` package.
_STORY_SCOPE = "(17-2)"

#: ``argus`` is a package DIRECTORY pathspec. Forward slash, repository-relative: the same
#: string must work on the Windows local gate and on the ubuntu CI matrix.
_ARGUS_PATHSPEC = "argus"


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    """A pure READ of this repository's history. Never mutates: no checkout, no commit.

    ``-C <root>`` rather than a shell ``cd``, and an argument list rather than
    ``shell=True`` — the local gate runs on Windows while CI runs an ubuntu matrix, and a
    shell string is where that split turns into a platform-only bug (``AI-E13-1``). The
    idiom is ``tests/test_candidate_selection.py``'s and
    ``tests/test_precision_preregistration.py``'s, reused rather than re-invented.
    """
    return subprocess.run(
        ["git", "-C", str(_REPO_ROOT), *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


# ═════════════════════════════════════════════════════════════════════════════════════════
# The analyzers. PURE and EXPORTED, so each predicate can be driven over synthetic input by
# a positive control — a rule enforced only through the live artifact is a rule nobody has
# watched fire (12.2's precedent, `-78`'s form).
# ═════════════════════════════════════════════════════════════════════════════════════════


def anchored_figures(document: str) -> dict[str, int]:
    """Every figure the specification CITES, read from the ANCHORED table only. Pure.

    ⛔ The anchoring is the point. An unanchored scan of a markdown document resolves any
    same-shaped row anywhere in it — including one written as an example, a rejected
    variant or a decoy — which is precisely how Story 17.1's ``protocol_change_log_head``
    read the wrong row and returned silently. Text outside the marker pair is NOT read.

    Returns an empty mapping when the markers are absent or inverted, so a document that
    loses its anchors fails the non-vacuity floor rather than passing on an empty set.
    """
    start = document.find(_FIGURES_BEGIN)
    end = document.find(_FIGURES_END)
    if start < 0 or end < 0 or end <= start:
        return {}
    region = document[start + len(_FIGURES_BEGIN) : end]
    figures: dict[str, int] = {}
    for line in region.splitlines():
        match = _FIGURE_ROW.match(line.strip())
        if match is not None:
            figures[match.group(1)] = int(match.group(2))
    return figures


def unanchored_figures(document: str) -> dict[str, int]:
    """The BROKEN extractor, kept deliberately: the whole-document scan ``-142`` refuses.

    It exists for one reason — to prove that a planted decoy IS visible to an unanchored
    reading of the same bytes. Without that half, "the anchored extractor did not see the
    decoy" is indistinguishable from "the extractor sees nothing at all" (``AI-E11-1``).
    ⛔ It is never used to make a claim about the specification.
    """
    figures: dict[str, int] = {}
    for line in document.splitlines():
        match = _FIGURE_ROW.match(line.strip())
        if match is not None:
            figures[match.group(1)] = int(match.group(2))
    return figures


def quoted_silent_class_definition(document: str) -> str | None:
    """The specification's ``SILENT_CLASS_DEFINITION`` quotation, or ``None``. Pure.

    Anchored the same way and for the same reason. The fenced block between the markers is
    unwrapped; the trailing newline the fence requires is stripped, and nothing else is.
    """
    start = document.find(_QUOTATION_BEGIN)
    end = document.find(_QUOTATION_END)
    if start < 0 or end < 0 or end <= start:
        return None
    region = document[start + len(_QUOTATION_BEGIN) : end]
    lines = region.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if len(lines) < 3 or not lines[0].startswith("```") or lines[-1].strip() != "```":
        return None
    return "\n".join(lines[1:-1])


def definition_figures(definition: str) -> dict[str, int]:
    """The figures ``SILENT_CLASS_DEFINITION`` states IN ITS OWN WORDS. Pure.

    Each pattern is ANCHORED to the surrounding sentence rather than to a bare number, so a
    figure moving elsewhere in the constant cannot be silently re-resolved here. A pattern
    that stops matching yields a missing key, and ``-142``'s authority-completeness
    assertion turns that into RED rather than into a smaller comparison.
    """
    figures: dict[str, int] = {}
    walked = re.search(
        r"over the ([\d,]+) recorded vacuous_test_heuristic findings:\s*(\d+) members",
        definition,
    )
    if walked is not None:
        figures["definition.population_walked"] = int(walked.group(1).replace(",", ""))
        figures["definition.class_size"] = int(walked.group(2))
    v1 = re.search(r"V1 \(drop the provably-dead mock-referencing clause\) reaches (\d+)", definition)
    if v1 is not None:
        figures["definition.v1_reach"] = int(v1.group(1))
    v3 = re.search(r"V3 \(V1 AND silent\) also reaches (\d+)", definition)
    if v3 is not None:
        figures["definition.v3_reach"] = int(v3.group(1))
    outside = re.search(r"(\d+) of the (\d+) lie outside V1 entirely", definition)
    if outside is not None:
        figures["definition.outside_v1"] = int(outside.group(1))
        figures["definition.outside_v1_denominator"] = int(outside.group(2))
    return figures


def record_figures(record: dict[str, object]) -> dict[str, int]:
    """The figures ``silent-class-record.json`` states, keyed as the specification keys them.

    Pure over an already-parsed record: the guard reads the file, this function does not.
    Missing fields yield missing keys, which ``-142`` turns into RED.
    """
    figures: dict[str, int] = {}
    for field in ("class_size", "population_walked", "population_skipped"):
        value = record.get(field)
        if isinstance(value, int):
            figures[f"record.{field}"] = value
    for field in ("class_by_corpus_member", "files_by_corpus_member", "counts"):
        table = record.get(field)
        if isinstance(table, dict):
            for member, value in table.items():
                if isinstance(value, int):
                    figures[f"record.{field}.{member}"] = value
    exhaustiveness = record.get("exhaustiveness")
    if isinstance(exhaustiveness, dict):
        for field in ("adjudicated_count", "residual_count"):
            value = exhaustiveness.get(field)
            if isinstance(value, int):
                figures[f"record.exhaustiveness.{field}"] = value
    return figures


def mref_reference_sites(source: str, module: str) -> tuple[tuple[str, int, str], ...]:
    """Classify EVERY ``mock_referencing_assertions`` reference in *source*. Pure.

    ⛔ **AST NODES, NOT SUBSTRINGS.** A substring counter is a guard over the SHAPE of the
    input and not over its EFFECT (the GUARD-ADEQUACY CLAUSE's input-side twin): it cannot
    tell a comparison that DECIDES something from a field annotation, a keyword argument
    carried for a reader, or the word inside a docstring. The claim §7.3 rests on is about
    DECISIONS, so the classification is about decisions:

    ``decision``      the reference is inside an :class:`ast.Compare` — it is compared, and
                      the comparison's value is what fact (b) branches on.
    ``field``         an :class:`ast.AnnAssign` target: a dataclass field DECLARATION.
    ``keyword``       an :class:`ast.keyword` argument name: a value CARRIED to a
                      constructor, deciding nothing.
    ``read``          any other load of the name or attribute.

    ⛔ **No ``isinstance``/``issubclass`` decision against a Protocol** anywhere in this
    module (Story 18.4 / AC5.4): ``@runtime_checkable`` is deliberately absent from
    ``Detector`` and such a check is a ``TypeError``, not a weak yes. The ``isinstance``
    calls here are against ``ast`` node classes, which is the standard-library AST idiom
    ``tests/test_silent_class.py`` already uses.
    """
    tree = ast.parse(source, filename=module)
    in_compare: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for descendant in ast.walk(node):
                in_compare.add(id(descendant))

    sites: list[tuple[str, int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == _MREF:
                sites.append((module, node.lineno, "field"))
                continue
        if isinstance(node, ast.keyword) and node.arg == _MREF:
            sites.append((module, node.lineno, "keyword"))
            continue
        named = (
            isinstance(node, ast.Attribute) and node.attr == _MREF
        ) or (isinstance(node, ast.Name) and node.id == _MREF)
        if not named:
            continue
        kind = "decision" if id(node) in in_compare else "read"
        sites.append((module, node.lineno, kind))
    return tuple(sorted(set(sites)))


# ═════════════════════════════════════════════════════════════════════════════════════════
# AC5.1 — the specification's figures RE-DERIVE from the committed artifacts
# ═════════════════════════════════════════════════════════════════════════════════════════


def test_TC_ArgusAgent_PRECISION_001_142_specification_figures_rederive() -> None:
    """TC-ArgusAgent-PRECISION-001-142 — AC1/AC5.1: a cited figure is re-derived, not typed.

    **(i) Observable.** Every numeric figure the specification attributes to a committed
    artifact, extracted by :func:`anchored_figures` from the marker-delimited table, set
    against the two authorities that own those numbers: the committed
    ``silent-class-record.json`` and the imported
    ``argus.precision.silent_class.SILENT_CLASS_DEFINITION``. The comparison closes in
    BOTH directions — every cited figure must match its authority, and every authority
    figure the specification claims to cite must be present — so neither a wrong value nor
    a quietly dropped row passes.

    **(ii) RED at the real seam, by an EXECUTED mutation.** ``record.class_size`` was
    changed from ``36`` to ``37`` in the real committed specification and this guard went
    RED naming the key, the cited value and the authority value; the document was restored
    byte-exact and verified by sha256. The mutation and the restore hash are recorded in
    the story file's Dev Agent Record.

    **(iii) Adversarial variants, GENERATED from the live record, with counts.**
    Two families, both derived from what the document actually cites rather than
    hand-written:

    1. **A DECOY ROW per cited key**, planted OUTSIDE the anchors in a copy of the real
       document with a value the authorities do not carry. The anchored extractor must be
       BLIND to every one of them — and the unanchored extractor must SEE every one of
       them, which is what proves the planted input genuinely carries the defect rather
       than proving the extractor found nothing. ⚠️ This is Story 17.1's one review
       finding, generated against this document on every run.
    2. **A PERTURBATION per cited key**: each figure is moved by one and the comparison
       must reject it. A comparison that accepts a perturbed figure is not comparing.
    """
    from argus.precision.silent_class import SILENT_CLASS_DEFINITION

    # ── Non-vacuity FIRST: the artifacts must parse non-empty. ─────────────────────────
    assert _SPECIFICATION.is_file(), (
        f"the specification {_SPECIFICATION.name} does not exist; every assertion below "
        "would observe nothing"
    )
    document = _SPECIFICATION.read_text(encoding="utf-8")
    assert len(document) > 5000, (
        f"the specification is {len(document)} characters — far too short to be the "
        "document Story 17.2 commits, so this guard is reading the wrong file or a stub"
    )
    assert _SILENT_CLASS_RECORD.is_file(), (
        f"{_SILENT_CLASS_RECORD.name} is missing; the record half of the authority does "
        "not exist and the comparison below would be one-sided without saying so"
    )
    record = json.loads(_SILENT_CLASS_RECORD.read_text(encoding="utf-8"))
    assert isinstance(record, dict) and record, "silent-class-record.json parsed empty"

    authority = {**record_figures(record), **definition_figures(SILENT_CLASS_DEFINITION)}
    assert len(authority) >= _MIN_FIGURES, (
        f"non-vacuity: only {len(authority)} authority figure(s) were derived from the "
        f"record and the constant, against a floor of {_MIN_FIGURES}. Either an extractor "
        "stopped matching or an artifact moved — and a comparison against a collapsed "
        "authority set passes without observing anything (AI-E11-1). Fix the derivation, "
        "never the floor."
    )
    for expected_key in (
        "definition.population_walked",
        "definition.class_size",
        "definition.v1_reach",
        "definition.v3_reach",
        "definition.outside_v1",
        "definition.outside_v1_denominator",
    ):
        assert expected_key in authority, (
            f"{expected_key!r} could not be resolved out of SILENT_CLASS_DEFINITION. Its "
            "anchored pattern no longer matches the constant, so this guard has stopped "
            "reading half its authority. The constant is the source of truth; re-anchor "
            "the pattern to it, do not delete the key."
        )

    cited = anchored_figures(document)
    assert len(cited) >= _MIN_FIGURES, (
        f"non-vacuity: the ANCHORED extractor found {len(cited)} figure(s) between "
        f"{_FIGURES_BEGIN} and {_FIGURES_END}, against a floor of {_MIN_FIGURES}. An "
        "extractor that matches nothing compares an empty set and passes forever."
    )

    # ── THE CLAIM, both directions. ────────────────────────────────────────────────────
    unknown = sorted(key for key in cited if key not in authority)
    assert not unknown, (
        "the specification cites figure key(s) no committed authority carries: "
        f"{unknown}. A figure whose authority cannot be named is a hand-written number, "
        "which is the DF-8-5-C class this guard exists to prevent."
    )
    wrong = sorted(
        f"{key}: document says {cited[key]}, {'record' if key.startswith('record.') else 'SILENT_CLASS_DEFINITION'} says {authority[key]}"
        for key in cited
        if cited[key] != authority[key]
    )
    assert not wrong, (
        "the specification's cited figure(s) no longer re-derive from the committed "
        "artifacts:\n  " + "\n  ".join(wrong) + "\n⛔ Fix the DOCUMENT against the "
        "artifact. Never edit the artifact to match the document, and never delete the "
        "row (DF-8-5-B)."
    )
    missing = sorted(key for key in authority if key.startswith("definition.") and key not in cited)
    assert not missing, (
        f"SILENT_CLASS_DEFINITION states figure(s) the specification stopped citing: "
        f"{missing}. AC1.10 requires the constant's own figures to be carried, and a row "
        "silently dropped from the table is how a comparison shrinks to nothing."
    )

    # ── (iii-1) DECOY per cited key, generated from the live document. ─────────────────
    decoys_planted = 0
    for key, value in sorted(cited.items()):
        decoy_row = f"| `{key}` | **{value + 1000}** | a decoy planted OUTSIDE the anchors |"
        planted = document + "\n\n" + decoy_row + "\n"
        assert anchored_figures(planted).get(key) == value, (
            f"THE ANCHORING FAILED: a decoy row for {key!r} planted outside "
            f"{_FIGURES_BEGIN}/{_FIGURES_END} was resolved by the anchored extractor. "
            "This is Story 17.1's review finding — an unanchored read of a markdown "
            "document resolving the wrong row — recurring one story later."
        )
        assert unanchored_figures(planted).get(key) == value + 1000, (
            f"the decoy for {key!r} is INVISIBLE to the unanchored extractor too, so the "
            "planted input does not carry the defect and the assertion above proved "
            "nothing about anchoring (AI-E11-1)."
        )
        decoys_planted += 1
    assert decoys_planted == len(cited) >= _MIN_FIGURES, (
        f"non-vacuity: {decoys_planted} decoy(s) generated from {len(cited)} live cited "
        "figure(s)"
    )

    # ── (iii-2) PERTURBATION per cited key. ────────────────────────────────────────────
    perturbations = 0
    for key, value in sorted(cited.items()):
        assert value + 1 != authority[key], (
            f"perturbing {key!r} by one produced a value the authority ACCEPTS "
            f"({value + 1}); the comparison cannot distinguish this figure from a wrong "
            "one and is not comparing anything."
        )
        perturbations += 1
    assert perturbations == len(cited), (
        f"non-vacuity: {perturbations} perturbation(s) over {len(cited)} cited figure(s)"
    )

    # ── Positive control over synthetic input: the predicates are watched FIRING. ──────
    assert anchored_figures(
        f"{_FIGURES_BEGIN}\n| `a.b` | **7** | x |\n{_FIGURES_END}\n| `a.b` | **9** | x |"
    ) == {"a.b": 7}
    assert anchored_figures("| `a.b` | **7** | x |") == {}
    assert definition_figures("nothing here") == {}


# ═════════════════════════════════════════════════════════════════════════════════════════
# AC5.2 — the mock-binding decision rests on a MEASURED fact
# ═════════════════════════════════════════════════════════════════════════════════════════


def test_TC_ArgusAgent_PRECISION_001_143_mref_has_exactly_one_decision_site() -> None:
    """TC-ArgusAgent-PRECISION-001-143 — AC3.1/AC5.2: one comparison, one branch, one predicate.

    **(i) Observable.** Every reference to ``mock_referencing_assertions`` in every module
    of the ``argus`` package, collected by an ``ast`` walk and CLASSIFIED by
    :func:`mref_reference_sites` into a DECISION (the reference sits inside a comparison)
    versus a field declaration, a keyword carry or a plain read. The specification's §7.3
    claim — and with it the ``DF-INV-VACUOUS-B`` disposition — is that there is **exactly
    one decision site**, and that it is in ``argus/detectors/vacuous_test.py``.

    ⛔ **Classification, never substring counting.** A ``source.count("mref")`` is a guard
    over the SHAPE of the input rather than its EFFECT: it cannot tell a comparison that
    branches from a docstring that mentions the name. The claim is about branches.

    **(ii) RED at the real seam, by an EXECUTED mutation.** A second real comparison —
    ``evidence.mock_referencing_assertions >= 2`` — was planted in
    ``argus/precision/silent_class.py``, a module that today carries only carries and no
    decision, and this guard went RED naming two decision sites; the module was restored
    byte-exact and verified by sha256. Recorded in the story file's Dev Agent Record.

    **(iii) Adversarial variants, GENERATED from the live modules, with a count.** For
    every module that references the name at all, its real source is re-parsed with a
    second comparison appended inside a synthetic function, and the classifier must report
    one MORE decision site than the unmutated source did. The variants are generated from
    the live tree, so the count moves with the tree rather than with a fixture.

    ⛔ **AC7.3:** a second decision site found in the live tree does not mean this guard is
    wrong. It falsifies the specification's §7.3 basis outright, and the response is to
    escalate in the story record — never to relax this assertion.
    """
    assert _ARGUS_PACKAGE.is_dir(), f"{_ARGUS_PACKAGE} is not a directory"
    modules = sorted(_ARGUS_PACKAGE.rglob("*.py"))

    # ── Non-vacuity FIRST: the walk must actually parse a package. ─────────────────────
    assert len(modules) >= _MIN_ARGUS_MODULES, (
        f"non-vacuity: only {len(modules)} module(s) found under {_ARGUS_PACKAGE}, "
        f"against a floor of {_MIN_ARGUS_MODULES}. An absence asserted over a population "
        "the walk failed to enumerate is not evidence (AI-E11-1)."
    )

    sites: list[tuple[str, int, str]] = []
    sources: dict[str, str] = {}
    for path in modules:
        relative = path.relative_to(_REPO_ROOT).as_posix()
        source = path.read_text(encoding="utf-8")
        found = mref_reference_sites(source, relative)
        if found:
            sources[relative] = source
        sites.extend(found)

    # ── Non-vacuity SECOND, and it is the one that matters: the KNOWN site is FOUND. ───
    decisions = sorted(site for site in sites if site[2] == "decision")
    assert any(module == _KNOWN_DECISION_SITE for module, _line, _kind in decisions), (
        f"the KNOWN decision site in {_KNOWN_DECISION_SITE} was NOT found. Before this "
        "guard may assert that no OTHER decision site exists, it must prove it can see "
        "the one that does — otherwise 'no other decision site' is a broken walk "
        f"reporting silence. Classified references found: {sites}"
    )
    assert len(sites) >= 4, (
        f"non-vacuity: only {len(sites)} reference(s) to {_MREF} were classified across "
        "the package; the field declaration, its population and the decision are all "
        "expected, so a smaller count means the walk stopped resolving references."
    )

    # ── THE CLAIM. ─────────────────────────────────────────────────────────────────────
    assert len(decisions) == 1, (
        f"{_MREF} has {len(decisions)} decision site(s) in the argus package, not one: "
        f"{decisions}. ⛔ AC7.3 — this FALSIFIES the specification's §7.3 basis and the "
        "DF-INV-VACUOUS-B disposition that rests on it. ESCALATE in the story record with "
        "the new site's evidence. Do NOT relax this assertion and do NOT edit the "
        "specification to fit (DF-8-5-B)."
    )
    assert decisions[0][0] == _KNOWN_DECISION_SITE, (
        f"the single decision site moved to {decisions[0][0]!r}; the specification names "
        f"{_KNOWN_DECISION_SITE!r}. Update the specification against the tree, with "
        "evidence."
    )

    # ── (iii) Adversarial variants GENERATED from the live modules, with a count. ──────
    generated = 0
    for relative, source in sorted(sources.items()):
        before = len([s for s in mref_reference_sites(source, relative) if s[2] == "decision"])
        mutated = source + (
            "\n\n\ndef _adversarial_variant_generated_by_TC_143(evidence: object) -> bool:\n"
            f"    return evidence.{_MREF} >= 2\n"
        )
        after = len([s for s in mref_reference_sites(mutated, relative) if s[2] == "decision"])
        assert after == before + 1, (
            f"the classifier did not react to a second REAL comparison planted in "
            f"{relative}: {before} decision(s) before, {after} after. It is therefore not "
            "detecting decision sites and every assertion above is silent."
        )
        generated += 1
    assert generated == len(sources) >= 3, (
        f"non-vacuity: {generated} adversarial variant(s) generated from {len(sources)} "
        f"live module(s) that reference {_MREF}"
    )

    # ── Positive control over synthetic input: each classification watched firing. ─────
    control = mref_reference_sites(
        "import dataclasses\n"
        "@dataclasses.dataclass\n"
        "class C:\n"
        f"    {_MREF}: int = 0\n"
        f"def carry(e):\n    return C({_MREF}=e.{_MREF})\n"
        f"def decide(e):\n    return e.{_MREF} >= 1\n",
        "control.py",
    )
    kinds = sorted(kind for _module, _line, kind in control)
    assert kinds.count("decision") == 1, f"control decision count moved: {control}"
    assert "field" in kinds and "keyword" in kinds, f"control classification moved: {control}"


# ═════════════════════════════════════════════════════════════════════════════════════════
# AC5.3 — the quotation is verbatim, and this story's arc wrote no argus byte
# ═════════════════════════════════════════════════════════════════════════════════════════


def test_TC_ArgusAgent_PRECISION_001_144_quotation_is_verbatim_and_argus_is_untouched() -> None:
    """TC-ArgusAgent-PRECISION-001-144 — AC1.10/AC2.1/AC5.3: cited, not copied; and unmoved.

    **(i) Observable, two halves.**

    1. The specification's anchored ``SILENT_CLASS_DEFINITION`` quotation, compared
       **character for character** to the imported constant. ``AI-E9-7``: a prose copy of a
       pinned constant is a second source of truth that drifts silently, and this project
       has already paid for one (``DF-8-5-C``). This guard is what makes re-typing it
       impossible rather than discouraged.
    2. Every commit in **Story 17.2's arc** that touches the ``argus`` package. The claim
       is that there are **none** — the ``consumed == 0`` arithmetic and everything around
       it are untouched by this story, proved against the object database rather than
       promised in prose (AC2.1, AC6.2).

    ⛔ **Why the second half is scoped to this story's arc and not to "everything since the
    baseline".** Story 17.3 is chartered to write inside the ``argus`` package. A guard
    asserting that nothing after the baseline touches it would be a self-inflicted RED the
    moment the next story lands legitimately, and the correct response to that RED would be
    to delete the guard — which is how a real claim gets thrown away with a badly scoped
    one. The claim Story 17.2 actually makes is about ITS OWN commits, and that claim stays
    checkable forever.

    **(ii) RED at the real seam, by an EXECUTED mutation.** One character of the quotation
    was altered in the real committed specification and this guard went RED reporting the
    offset and both characters; the document was restored byte-exact and verified by
    sha256. Recorded in the story file's Dev Agent Record.

    **(iii) Adversarial variants, GENERATED from the live constant, with a count.** Every
    character class present in the constant is perturbed in turn — one variant per sampled
    offset, generated from the constant's real length — and the comparison must reject each
    one. Plus the control the ``-75``/``-139`` idiom demands for the git half.

    **Non-vacuity FIRST, both halves.** The constant and the quotation are each asserted
    non-empty and above a length floor before they are compared, or an empty-vs-empty match
    passes silently. And the git half asserts that the ``argus`` pathspec is CAPABLE of
    finding commits, because a misspelled or moved pathspec returns empty and is
    **indistinguishable from a clean tree** (``-75``/``-139``'s answer, reused verbatim
    rather than re-invented).
    """
    from argus.precision.silent_class import SILENT_CLASS_DEFINITION

    # ─────────────────────────── HALF ONE: the quotation ──────────────────────────────
    assert _SPECIFICATION.is_file(), f"{_SPECIFICATION.name} does not exist"
    document = _SPECIFICATION.read_text(encoding="utf-8")

    assert len(SILENT_CLASS_DEFINITION) > 400, (
        f"SILENT_CLASS_DEFINITION is {len(SILENT_CLASS_DEFINITION)} characters. It is the "
        "V2 predicate written in the words a promotion proposal would have to defend and "
        "it is far longer than that — an empty or truncated constant makes the comparison "
        "below vacuous, so this is asserted BEFORE it (AI-E11-1)."
    )
    quotation = quoted_silent_class_definition(document)
    assert quotation is not None, (
        f"the specification carries no fenced quotation between {_QUOTATION_BEGIN} and "
        f"{_QUOTATION_END}. AC1.10 requires SILENT_CLASS_DEFINITION to be QUOTED verbatim "
        "and attributed, never paraphrased."
    )
    assert len(quotation) > 400, (
        f"the extracted quotation is {len(quotation)} characters; the extractor is "
        "resolving the wrong region and an empty-vs-empty comparison would pass silently."
    )
    if quotation != SILENT_CLASS_DEFINITION:
        offset = next(
            (
                index
                for index, (left, right) in enumerate(zip(quotation, SILENT_CLASS_DEFINITION))
                if left != right
            ),
            min(len(quotation), len(SILENT_CLASS_DEFINITION)),
        )
        raise AssertionError(
            "the specification's SILENT_CLASS_DEFINITION quotation is NOT character-for-"
            f"character identical to the imported constant. First difference at offset "
            f"{offset}: document has {quotation[offset:offset + 30]!r}, constant has "
            f"{SILENT_CLASS_DEFINITION[offset:offset + 30]!r}. Lengths "
            f"{len(quotation)} vs {len(SILENT_CLASS_DEFINITION)}. ⛔ Regenerate the "
            "quotation FROM THE IMPORTED CONSTANT — never re-type it by eye, and never "
            "edit the constant to match the document (AI-E9-7 / DF-8-5-C)."
        )

    # (iii) Perturbations generated from the live constant, with a count.
    perturbed = 0
    step = max(1, len(SILENT_CLASS_DEFINITION) // 40)
    for index in range(0, len(SILENT_CLASS_DEFINITION), step):
        original = SILENT_CLASS_DEFINITION[index]
        replacement = "Z" if original != "Z" else "Q"
        variant = (
            SILENT_CLASS_DEFINITION[:index]
            + replacement
            + SILENT_CLASS_DEFINITION[index + 1 :]
        )
        assert variant != quotation, (
            f"a one-character perturbation at offset {index} still compares EQUAL to the "
            "quotation; the comparison is not character-for-character."
        )
        perturbed += 1
    assert perturbed >= 30, (
        f"non-vacuity: only {perturbed} perturbation(s) generated from a "
        f"{len(SILENT_CLASS_DEFINITION)}-character constant"
    )

    # ─────────────────────── HALF TWO: this story's arc, in git ────────────────────────
    baseline = re.search(
        r"^baseline_commit:\s*([0-9a-fA-F]{7,40})\s*$",
        _STORY_FILE.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    assert baseline is not None, (
        f"{_STORY_FILE.name} carries no `baseline_commit` in its YAML frontmatter, so "
        "there is no range to scope this story's arc against."
    )
    base = baseline.group(1)

    resolved = _git("cat-file", "-t", base)
    assert resolved.returncode == 0 and resolved.stdout.strip() == "commit", (
        f"the story's baseline_commit {base!r} does not resolve to a commit in this "
        f"repository (git said {resolved.stdout.strip()!r} / {resolved.stderr.strip()!r})."
    )
    ancestry = _git("merge-base", "--is-ancestor", base, "HEAD")
    assert ancestry.returncode == 0, (
        f"the story's baseline_commit {base} is not an ancestor of HEAD, so the range "
        f"{base}..HEAD does not describe this story's arc."
    )

    # Precondition: prove the pathspec can FIND something. A misspelled or moved pathspec
    # returns empty and is indistinguishable from a clean tree (-75 / -139).
    control = _git("log", "--format=%H", "HEAD", "--", _ARGUS_PATHSPEC)
    assert control.returncode == 0, f"control `git log` failed: {control.stderr.strip()!r}"
    control_commits = [line for line in control.stdout.splitlines() if line.strip()]
    assert control_commits, (
        f"`git log HEAD -- {_ARGUS_PATHSPEC}` returned NOTHING. That path is the shipped "
        "package and it is known to carry hundreds of commits, so this invocation cannot "
        "find anything — and an invocation that finds nothing reports a clean arc for a "
        "dirty one. Fix the invocation, never the assertion."
    )

    # Precondition: prove the story-scope selector can FIND this story's own commits.
    arc = _git("log", "--format=%H%x1f%s", f"{base}..HEAD")
    assert arc.returncode == 0, f"`git log {base}..HEAD` failed: {arc.stderr.strip()!r}"
    arc_rows = [row for row in arc.stdout.splitlines() if row.strip()]
    story_commits = {
        row.split("\x1f", 1)[0]
        for row in arc_rows
        if _STORY_SCOPE in row.split("\x1f", 1)[1]
    }
    assert story_commits, (
        f"no commit in {base}..HEAD carries the {_STORY_SCOPE!r} scope, so the claim below "
        "is an absence over an empty set. Story 17.2's arc opens with a "
        f"`chore{_STORY_SCOPE}` commit; if the message convention changed, UPDATE "
        "_STORY_SCOPE — do not widen this to every commit since the baseline, which would "
        "go RED the moment Story 17.3 legitimately writes inside the argus package."
    )

    # THE CLAIM: no commit of this story's arc touches the argus package.
    touching = _git("log", "--format=%H", f"{base}..HEAD", "--", _ARGUS_PATHSPEC)
    assert touching.returncode == 0, f"`git log` failed: {touching.stderr.strip()!r}"
    argus_commits = {line for line in touching.stdout.splitlines() if line.strip()}
    offenders = sorted(story_commits & argus_commits)
    assert not offenders, (
        f"{len(offenders)} commit(s) in Story 17.2's arc touch the {_ARGUS_PATHSPEC} "
        f"package: {offenders}. ⛔ Story 17.2 is a SPECIFICATION and writes no shipped "
        "byte: AC2.1 (`consumed == 0` is not edited), AC6.2 (no code_identity movement, no "
        "dogfood regeneration, no Evidence-partition trailer) and AC7.6 (an argus edit is "
        "an ESCALATION, not a scope adjustment) all rest on this being empty."
    )

    # Positive control: the intersection predicate is watched FINDING something.
    assert story_commits & story_commits == story_commits
    fabricated = {"0" * 40}
    assert not (story_commits & fabricated), "control: the intersection is not discriminating"
    assert (story_commits | fabricated) & story_commits == story_commits
