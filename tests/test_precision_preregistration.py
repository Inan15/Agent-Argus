"""Story 17.1 — the PRE-REGISTRATION guards: a criterion nobody can quietly move.

Verification area ``TC-ArgusAgent-PRECISION-001-135``..``-141``. **No new area is opened**: the
pre-registration governs the precision gate's substrate, so its guards continue the existing
``PRECISION-001`` area, exactly as ``tests/test_candidate_selection.py`` continued it for the
selection harness. Ids are the next **actually free** ones — the area ran to ``-134`` across
``tests/test_release_preflight.py``, ``tests/test_silent_class.py`` and
``tests/test_silent_class_record.py`` when this module was created. No existing id was renumbered;
an id here is a citation.

**Why these guards exist, in one sentence.** Story 17.1's whole claim is that the criterion was
fixed **before the number existed** — and an intention to decide-before-looking is not evidence of
having done so. Git history is the evidence; an asserted intention is not. So the floors are
proved RESOLVED rather than re-typed (``-135``), the exposure ceiling is RE-DERIVED from its
pinned blob rather than trusted as a literal (``-136``), the ceiling is proved NOT REDUNDANT with
the ratio by being watched failing on its own (``-137``), a thin or narrow population is proved
``UNEVALUABLE`` rather than ``MET`` (``-138``), the ordering is checked against the real object
database (``-139``), the criterion is proved DIRECTIONALLY immutable against its own pinned blob
(``-140``), and the module is proved structurally incapable of looking, fetching or writing
(``-141``).

**⛔ FIVE OF THESE SEVEN ASSERT A NEGATIVE, AND NON-VACUITY IS THE POINT.** This project's
signature defect is a guard that asserts an absence over a population it never read: Epic 14
shipped **35** guards of which **4** were not real, one reducing to ``f(x) == f(x)`` on a pure
function. So, per the GUARD-ADEQUACY CLAUSE, each guard below pins its **precondition before its
assertion** and drives its predicate to **BOTH** outcomes by an **EXECUTED** mutation:

* an empty ``SUCCESSOR_OUTPUT_PATHS`` would make ``-139`` forbid nothing → asserted non-empty
  first;
* ``git log <sha> -- <pathspec>`` returns empty both for a clean history **and for a misspelled
  path** → a **control path known to carry commits** is asserted non-empty first (``-75``'s
  answer, reused rather than re-invented);
* a pinned blob that fails to parse would make ``-136`` vacuous → the row count and the
  disposition vocabulary are asserted non-empty first;
* an ``ast`` walk that matches nothing passes → ``-135`` and ``-141`` assert the walk found the
  module's **real** symbols before asserting what it did **not** find.

**Adversarial variants are GENERATED from the module, the record or the path set** — never
hand-written — so they cannot go stale against the thing they are supposed to shadow.

⛔ **A guard here is never loosened to go green** (``DF-8-5-B``). If ``-136`` reddens because the
count moved, the answer is to report the measurement, not to adjust the literal.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "corpus"))

from _manifest import (  # noqa: E402
    MANIFEST_FIELDS,
    eligible_member_count,
    validation_floor_n,
)
from argus.precision.adjudication import change_log_head_version  # noqa: E402
from argus.precision.gate_conditions import CONDITION_VERDICTS  # noqa: E402
from argus.precision.gate_decision import GATE_OUTCOMES  # noqa: E402
from argus.precision.replay_harness import PRECISION_GATE_THRESHOLD  # noqa: E402

from precision_preregistration import (  # noqa: E402
    CRITERION_OUTCOMES,
    EXPOSURE_SOURCE_PATH,
    EXPOSURE_SOURCE_SHA,
    MAX_FALSE_ACCUSATION_EXPOSURE,
    POPULATION_ID,
    PROTOCOL_CHANGE_LOG_PATH,
    PROTOCOL_VERSION,
    SUCCESSOR_OUTPUT_PATHS,
    evaluate,
    precision_floor,
    refuse_protocol_drift,
    resolution_floors,
)

#: The module under guard. Repository-relative so the same string can be handed to ``git show``.
_CRITERION_REL_PATH = "scripts/precision_preregistration.py"
_CRITERION_SOURCE = _REPO_ROOT / _CRITERION_REL_PATH

#: Where ``PRECISION_GATE_THRESHOLD`` lives, so ``-140`` can read the ratio floor **at the pin**
#: out of the same blob store rather than assuming today's value was always the value.
_THRESHOLD_REL_PATH = "argus/precision/replay_harness.py"
_THRESHOLD_SYMBOL = "PRECISION_GATE_THRESHOLD"

#: A path KNOWN to carry commits. Without it a misspelled pathspec returns empty and reads exactly
#: like a clean ordering — the single most likely way ``-139`` could pass vacuously (``-75``).
_CONTROL_PATH_WITH_COMMITS = "tests/corpus/_manifest.py"

#: AC3.2 — the five vocabulary/population sizes this story must leave untouched, measured BEFORE
#: any of it was written. ``-141`` re-measures them by IMPORT and compares. They are typed here,
#: in the guard, precisely because the guard's job is to notice if the imported values move.
_CONSTANTS_BEFORE = {
    "eligible_member_count()": 5,
    "len(MANIFEST_FIELDS)": 9,
    "len(GATE_OUTCOMES)": 3,
    "len(CONDITION_VERDICTS)": 4,
    "validation_floor_n()": 5,
}

#: AC3.3 — the module names the criterion may NEVER import. ``argus.detectors`` is the
#: *looking* ban (it must be unable to read the instrument's verdict); the rest are the
#: *fetching* and *shelling* bans (protocol §6 R2: fetching third-party source is not an
#: autonomous act, and a pure criterion spawns nothing).
_FORBIDDEN_IMPORTS: tuple[str, ...] = (
    "argus.detectors",
    "urllib",
    "requests",
    "http.client",
    "socket",
    "ftplib",
    "subprocess",
)

#: AC3.3 — the write surfaces a criterion may never reach. A pre-registration that can write is a
#: pre-registration that can re-register itself.
_FORBIDDEN_WRITE_ATTRIBUTES: tuple[str, ...] = (
    "write_text",
    "write_bytes",
    "writelines",
)


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    """A pure READ of this repository's history. Never mutates: no checkout, no commit.

    ``-C <root>`` rather than a shell ``cd``, and an argument list rather than ``shell=True``:
    the local gate runs on Windows while CI runs an ubuntu matrix, and a shell string is where
    that split turns into a platform-only bug (``AI-E13-1``).
    """
    return subprocess.run(
        ["git", "-C", str(_REPO_ROOT), *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


def _criterion_source() -> str:
    return _CRITERION_SOURCE.read_text(encoding="utf-8")


def _dotted_imports(source: str) -> set[str]:
    """Every module name *source* imports, as FULL dotted paths. PURE — no I/O (AR8).

    Full dotted paths, not top-level packages: the ban distinguishes ``argus.precision``
    (required — the floors are resolved through it) from ``argus.detectors`` (forbidden), and a
    walk that collapsed both to ``argus`` could not tell them apart. It would pass while seeing
    nothing, which is the vacuity shape.
    """
    imported: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    return imported


def _forbidden_imports_seen(source: str) -> tuple[str, ...]:
    """AC3.3's import predicate, isolated so it can be driven to BOTH outcomes. PURE."""
    seen = _dotted_imports(source)
    return tuple(
        sorted(
            banned
            for banned in _FORBIDDEN_IMPORTS
            for name in seen
            if name == banned or name.startswith(banned + ".")
        )
    )


def _write_surfaces_seen(source: str) -> tuple[str, ...]:
    """AC3.3's write predicate, isolated so it can be driven to BOTH outcomes. PURE.

    Catches three shapes: ``open(..., "w"/"a"/"x")`` in either positional or ``mode=`` form,
    ``json.dump(...)``, and any ``.write_text`` / ``.write_bytes`` / ``.writelines`` attribute
    call. Three shapes because a ban held at one end is a ban somebody walks around.
    """
    offenders: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id == "open":
            modes = [a for a in node.args[1:2]] + [
                kw.value for kw in node.keywords if kw.arg == "mode"
            ]
            for mode in modes:
                if isinstance(mode, ast.Constant) and isinstance(mode.value, str):
                    if set(mode.value) & set("wax+"):
                        offenders.add(f'open(..., {mode.value!r})')
        elif isinstance(func, ast.Attribute):
            if func.attr in _FORBIDDEN_WRITE_ATTRIBUTES:
                offenders.add(f".{func.attr}(...)")
            elif func.attr in {"dump", "dumps"} and isinstance(func.value, ast.Name):
                if func.value.id == "json" and func.attr == "dump":
                    offenders.add("json.dump(...)")
    return tuple(sorted(offenders))


def _resolved_values() -> dict[str, int | float]:
    """The values the criterion RESOLVES today — the population ``-135``'s mutants are generated
    from. Derived by calling the same code the module calls, never typed here.
    """
    floors = resolution_floors()
    ratio = precision_floor()
    return {
        "ratio (as float)": float(ratio),
        "verdict-eligible population floor": floors.verdict_eligible_population,
        "contributing-member floor": floors.contributing_members,
        "sealed-contributing-member floor": floors.sealed_contributing_members,
    }


def _retyped_floor_literals(source: str) -> tuple[str, ...]:
    """Every numeric literal or ``Fraction(...)`` construction in *source* that RE-TYPES a floor.

    PURE. The population of banned values is GENERATED by resolving the floors, so this predicate
    tracks the code it guards instead of shadowing a snapshot of it.
    """
    banned = _resolved_values()
    offenders: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            if isinstance(node.value, bool):
                continue
            for label, value in banned.items():
                if node.value == value:
                    offenders.add(f"line {node.lineno}: literal {node.value!r} == {label}")
        elif isinstance(node, ast.Call):
            name = node.func
            constructed = (isinstance(name, ast.Name) and name.id == "Fraction") or (
                isinstance(name, ast.Attribute) and name.attr == "Fraction"
            )
            if constructed:
                offenders.add(f"line {node.lineno}: Fraction(...) constructed in the criterion")
    return tuple(sorted(offenders))


def _pinned_blob(sha: str, rel_path: str) -> subprocess.CompletedProcess[str]:
    """``git show <sha>:<path>`` — a read of the OBJECT DATABASE, never of the working tree."""
    return _git("show", f"{sha}:{rel_path}")


# ═════════════════════════════════════════════════════════════════════════════════════════
# AC1.2 / AC1.3 — the floors are RESOLVED, and the protocol version is CHECKED
# ═════════════════════════════════════════════════════════════════════════════════════════


def test_TC_ArgusAgent_PRECISION_001_135_the_floors_are_resolved_never_retyped() -> None:
    """TC-ArgusAgent-PRECISION-001-135 — AC1.2/AC1.3: the criterion resolves, it does not copy.

    **Observable.** The set of numeric literals and ``Fraction(...)`` constructions in
    ``scripts/precision_preregistration.py`` that equal a value the module is supposed to RESOLVE
    — the ratio floor, the verdict-eligible population floor, the contributing-member floor and
    the sealed-contributing-member floor.

    **Why it matters.** ``DN-3``: one floor, never forked. A re-typed floor agrees on the day it
    is typed and silently forks the moment protocol §5's own machinery moves — on the criterion
    that judges whether an instrument may start accusing people. ``AI-E9-7`` is the same rule for
    constants.

    **Non-vacuity, asserted BEFORE the absence:**

    1. the walk found imports **at all** — a broken parse forbids nothing;
    2. the walk can **SEE** the four resolving imports as full dotted paths, which proves the
       absence below is a measured absence rather than an artifact of a walk that reads nothing;
    3. the banned-value population is non-empty and was **resolved by calling the code**, so this
       guard cannot pass by comparing against nothing.

    **Adversarial, EXECUTED and GENERATED:** one mutant per resolved value, produced by appending
    that value to the real source as a literal. Each must be caught.

    **AC1.2 rides here too:** the protocol version is not asserted, it is CHECKED — the guard
    reads ``precision-validation-protocol.md``'s change-log head off disk (the impure edge the
    pure module refuses to take) and hands it to ``refuse_protocol_drift``.

    **⛔ AND THE ONE DERIVATION IS PROVED, STRUCTURALLY AND BEHAVIOURALLY (iteration-1 review).**
    Iteration 1 answered *"what is the protocol's head version"* twice: once canonically in
    ``argus.precision.adjudication.change_log_head_version`` (anchored to the ``## Change log``
    heading) and once locally, with an unanchored pattern searched over the whole document. The
    two forked immediately — a same-shaped ``| <date> | Vx.y | ... |`` row planted ABOVE the real
    table made the local reading resolve the wrong row and ``refuse_protocol_drift`` **silently
    pass** on real protocol drift. Fixed by deletion, and pinned here two ways so it cannot
    return: (i) STRUCTURALLY, ``argus.precision.adjudication`` is a REQUIRED visible import
    below, so the criterion must reach the canonical derivation; (ii) BEHAVIOURALLY, the exact
    adversarial document is GENERATED from the real protocol — the decoy row is the protocol's
    own head row, re-dated and re-planted above the ``## Change log`` heading, with the real head
    moved past ``PROTOCOL_VERSION`` — and the guard asserts, in order, that an unanchored reading
    of it really does resolve the decoy (so the input genuinely carries the defect), that the
    anchored reading resolves the moved head, and that ``refuse_protocol_drift`` RAISES. Watched
    firing, not only passing.
    """
    source = _criterion_source()
    imported = _dotted_imports(source)

    assert imported, (
        "the ast walk over the criterion found NO imports at all — the parse is broken, not the "
        "module clean. A ban that reads nothing forbids nothing."
    )
    for required in (
        "argus.precision.replay_harness",
        "argus.precision.gate_yield",
        "argus.precision.gate_breadth",
        "argus.precision.gate_seal",
        # ⛔ The iteration-1 review finding, pinned structurally: the change-log head is ONE
        # derivation and it lives here. If this import disappears the criterion has grown a
        # second parser for a fact `argus.precision.adjudication` already derives (AR7, DN-3,
        # the DF-8-5-C class) — which is exactly how the unanchored silent-pass got shipped.
        "argus.precision.adjudication",
    ):
        assert required in imported, (
            f"the criterion does not import {required!r} (saw {sorted(imported)}). That import is "
            "REQUIRED to be visible: it is what proves the floor is RESOLVED rather than typed, "
            "and it is what proves this walk resolves dotted `argus.*` paths at all."
        )

    banned = _resolved_values()
    assert banned and all(value > 0 for value in banned.values()), (
        f"the banned-value population resolved to {banned!r}. It is generated by CALLING the "
        "floor derivations; an empty or zero population would make the assertion below an "
        "absence over nothing."
    )

    offenders = _retyped_floor_literals(source)
    assert not offenders, (
        f"{_CRITERION_REL_PATH} re-types a resolved floor: {list(offenders)}. Resolve it by "
        f"calling the derivation ({sorted(banned)}), never by typing the integer it currently "
        "evaluates to. A literal agrees on the day it is written and forks silently afterwards "
        "— DN-3 and AI-E9-7, on the criterion that gates an accusation."
    )

    # ── RED, EXECUTED and GENERATED. One mutant per resolved value. ──
    for label, value in banned.items():
        mutant = source + f"\n_MUTANT_{abs(hash(label)) % 97} = {value!r}\n"
        assert _retyped_floor_literals(mutant), (
            f"the re-typing predicate did NOT catch an injected literal {value!r} ({label}). It "
            "is therefore incapable of catching a real one, and its silence above means nothing."
        )
    fraction_mutant = source + "\n_MUTANT_FRACTION = Fraction(4, 5)\n"
    assert _retyped_floor_literals(fraction_mutant), (
        "the predicate missed an injected `Fraction(...)` construction, so the ratio floor could "
        "be re-built from a numerator and a denominator without anything noticing."
    )

    # ── AC1.2: the version is CHECKED against the change-log head, not asserted. ──
    protocol_file = _REPO_ROOT / PROTOCOL_CHANGE_LOG_PATH
    assert protocol_file.is_file(), (
        f"the protocol at {PROTOCOL_CHANGE_LOG_PATH} is not on disk, so the version check below "
        "would be performed against nothing."
    )
    protocol_text = protocol_file.read_text(encoding="utf-8")
    head = refuse_protocol_drift(protocol_text)
    assert head == PROTOCOL_VERSION, (
        f"change-log head {head!r} != pre-registered {PROTOCOL_VERSION!r} — and "
        "refuse_protocol_drift did not raise, which means the refusal is inert."
    )
    # ── RED, EXECUTED: the refusal must actually fire on a moved head. ──
    moved = protocol_text.replace(f"| {PROTOCOL_VERSION} |", "| V99.9 |", 1)
    assert moved != protocol_text, (
        "the generated drift mutant is byte-identical to the real protocol, so the refusal below "
        "would be driven by the SAME input as the pass above and would prove nothing."
    )
    assert change_log_head_version(moved) == "V99.9", (
        "the canonical, anchored derivation does not read the generated drift mutant's head as "
        "V99.9, so the refusal below would be driven by an input that does not carry the defect."
    )
    with pytest.raises(Exception) as drift:
        refuse_protocol_drift(moved)
    assert PROTOCOL_VERSION in str(drift.value)
    with pytest.raises(Exception):
        refuse_protocol_drift("a protocol document with no change-log table at all")

    # ── ⛔ THE ITERATION-1 REVIEW FINDING, WATCHED FIRING. An EARLIER SAME-SHAPED ROW MUST NOT
    #    BE ABLE TO PRODUCE A SILENT PASS. The document is GENERATED from the real protocol, not
    #    hand-written: the decoy is the protocol's own head row re-dated and re-planted above the
    #    `## Change log` heading, and the real head is moved past PROTOCOL_VERSION. Under the
    #    deleted unanchored parser this document passed silently; under the anchored derivation
    #    it must REFUSE.
    heading = "## Change log"
    assert protocol_text.count(heading) == 1, (
        f"the real protocol carries {protocol_text.count(heading)} {heading!r} headings, so the "
        "adversarial document generated below would not be the shape the finding describes."
    )
    heading_at = protocol_text.index(heading)
    decoy_row = f"| 2019-01-01 | {PROTOCOL_VERSION} | a row of the same shape | nobody |"
    planted = (
        protocol_text[:heading_at]
        + "## An earlier table that is not the change log"
        + "\n\n| Date | Version | Description | Author |\n|---|---|---|---|\n"
        + decoy_row
        + "\n\n"
        + moved[heading_at:]
    )

    # Non-vacuity 1 — the decoy really does precede the real table.
    assert planted.index(decoy_row) < planted.index(heading), (
        "the planted row does not sit above the change-log heading, so this document does not "
        "reproduce the finding and the refusal below would prove nothing."
    )
    # Non-vacuity 2 — an UNANCHORED reading of it really does resolve the decoy. This is the
    # deleted implementation, rebuilt here ONLY to prove the input carries the defect.
    unanchored = re.search(
        r"^\|\s*\d{4}-\d{2}-\d{2}\s*\|\s*(V[\w.]*)\s*\|", planted, re.MULTILINE
    )
    assert unanchored is not None and unanchored.group(1) == PROTOCOL_VERSION, (
        "a whole-document scan of the planted document does NOT resolve the decoy row, so this "
        "input does not reproduce the iteration-1 defect and the assertion below is not watching "
        "the seam it claims to watch."
    )
    # Non-vacuity 3 — the anchored derivation reads the REAL, moved head.
    assert change_log_head_version(planted) == "V99.9", (
        "the anchored derivation did not resolve the moved head past the decoy, so the two "
        "readings do not disagree on this document and it cannot discriminate."
    )
    # THE CLAIM: a decoy row cannot buy a silent pass.
    with pytest.raises(Exception) as planted_drift:
        refuse_protocol_drift(planted)
    assert "V99.9" in str(planted_drift.value), (
        "refuse_protocol_drift raised, but not about the REAL head V99.9 — it must refuse "
        "because the head moved, not for some incidental reason."
    )
    # And the converse: a decoy must not manufacture a FALSE refusal either.
    benign = planted.replace(decoy_row, decoy_row.replace(PROTOCOL_VERSION, "V0.1"), 1).replace(
        "| V99.9 |", f"| {PROTOCOL_VERSION} |", 1
    )
    assert refuse_protocol_drift(benign) == PROTOCOL_VERSION, (
        "an unchanged head with a decoy row above it must resolve to PROTOCOL_VERSION; a "
        "derivation that trips over the decoy in this direction is the same defect wearing the "
        "other hat."
    )


# ═════════════════════════════════════════════════════════════════════════════════════════
# AC2.2 / AC2.3 — the exposure ceiling RE-DERIVES from the pinned blob
# ═════════════════════════════════════════════════════════════════════════════════════════


def test_TC_ArgusAgent_PRECISION_001_136_the_exposure_ceiling_rederives_from_its_pin() -> None:
    """TC-ArgusAgent-PRECISION-001-136 — AC2.2/AC2.3: the ceiling is derived, not chosen.

    **Observable.** The number of ``FP`` dispositions in the adjudication record read from the
    OBJECT DATABASE at ``EXPOSURE_SOURCE_SHA`` — compared to ``MAX_FALSE_ACCUSATION_EXPOSURE``.

    **Why it matters.** The ceiling is the one genuinely new quantity Story 17.1 lands, and a new
    quantity that cannot be reproduced is a preference wearing a derivation. It is frozen as a
    LITERAL on purpose (the record GROWS — Story 17.4 appends to it — and a ceiling that moves
    once the number is in view is the exact defect this story exists to prevent), which is
    precisely why the literal needs a guard that re-derives it.

    **Non-vacuity, each asserted BEFORE the count:**

    1. the sha RESOLVES to a commit in this repository;
    2. it is an ANCESTOR of ``HEAD`` — a sha on an abandoned line proves nothing about this one;
    3. ``git show`` succeeded and the blob PARSES as JSON;
    4. ``rows`` is non-empty — counting a label in an empty list returns 0 and would agree with a
       ceiling of 0 forever;
    5. the disposition VOCABULARY observed in the blob is non-empty and actually contains the
       label being counted.

    **Adversarial, EXECUTED and GENERATED from the record:** the counted label is perturbed —
    every ``FP`` row relabelled — and the count must MOVE. A counter that returns the same number
    for a relabelled record is not counting.

    ⛔ If this goes RED because the count moved, report the measurement. Do NOT adjust the
    literal (``DF-8-5-B``, and AC7 of the story).
    """
    assert len(EXPOSURE_SOURCE_SHA) == 40 and EXPOSURE_SOURCE_SHA.islower(), (
        "the exposure-source sha must be recorded as a full 40-character lowercase hex sha — a "
        "short sha is ambiguous, and this is the criterion's central citation."
    )
    kind = _git("cat-file", "-t", EXPOSURE_SOURCE_SHA)
    assert kind.returncode == 0 and kind.stdout.strip() == "commit", (
        f"the exposure-source sha {EXPOSURE_SOURCE_SHA} does not resolve to a commit in this "
        f"repository (git said {kind.stdout.strip()!r} / {kind.stderr.strip()!r})."
    )
    ancestry = _git("merge-base", "--is-ancestor", EXPOSURE_SOURCE_SHA, "HEAD")
    assert ancestry.returncode == 0, (
        f"{EXPOSURE_SOURCE_SHA} is NOT an ancestor of HEAD. The derivation would then rest on a "
        "commit that is not in this branch's history."
    )

    blob = _pinned_blob(EXPOSURE_SOURCE_SHA, EXPOSURE_SOURCE_PATH)
    assert blob.returncode == 0, (
        f"`git show {EXPOSURE_SOURCE_SHA}:{EXPOSURE_SOURCE_PATH}` failed: "
        f"{blob.stderr.strip()!r}. The ceiling's provenance is unreadable."
    )
    record = json.loads(blob.stdout)
    rows = record.get("rows")
    assert isinstance(rows, list) and rows, (
        "the pinned adjudication record carries no `rows` list, so counting a disposition in it "
        "returns 0 and would agree with any ceiling forever."
    )
    vocabulary = sorted({row.get("disposition") for row in rows} - {None})
    assert vocabulary, (
        "no `disposition` field was found on any pinned row — the field was renamed or the "
        "reader is wrong, and either way the count below measures nothing."
    )
    assert "FP" in vocabulary, (
        f"the pinned record's disposition vocabulary is {vocabulary} and does not contain 'FP'. "
        "The label the ceiling is derived from is absent, so the count is an absence over "
        "nothing rather than a measurement."
    )

    false_accusations = sum(1 for row in rows if row.get("disposition") == "FP")
    assert false_accusations == MAX_FALSE_ACCUSATION_EXPOSURE, (
        f"MAX_FALSE_ACCUSATION_EXPOSURE is {MAX_FALSE_ACCUSATION_EXPOSURE} but the pinned record "
        f"at {EXPOSURE_SOURCE_SHA} carries {false_accusations} FP row(s) of {len(rows)} "
        f"(vocabulary {vocabulary}). The ceiling no longer re-derives from the blob it cites. "
        "⛔ REPORT THE MEASUREMENT AND STOP — do NOT edit the literal to agree: a ceiling "
        "adjusted to whatever the record says today was never pre-registered against anything."
    )

    # ── RED, EXECUTED and GENERATED from the record: relabel and the count must MOVE. ──
    relabelled = [
        {**row, "disposition": "RELABELLED"} if row.get("disposition") == "FP" else row
        for row in rows
    ]
    perturbed = sum(1 for row in relabelled if row.get("disposition") == "FP")
    assert perturbed != false_accusations, (
        "relabelling every FP row left the count unchanged, so the counter is not reading the "
        "disposition field at all and its agreement with the ceiling above is a coincidence."
    )
    assert perturbed == 0


# ═════════════════════════════════════════════════════════════════════════════════════════
# AC2.4 — the ceiling is NOT redundant with the ratio, and it is watched FAILING
# ═════════════════════════════════════════════════════════════════════════════════════════


def test_TC_ArgusAgent_PRECISION_001_137_the_ceiling_is_not_redundant_with_the_ratio() -> None:
    """TC-ArgusAgent-PRECISION-001-137 — AC2.4: two conditions, and each can fail alone.

    **Observable.** ``evaluate()``'s outcome over four synthetic populations that hold the
    resolution floors fixed and vary only the ratio arm and the exposure arm:

    ======================  ======================  ==========
    ratio                   exposure                outcome
    ======================  ======================  ==========
    at or above the floor   at or below the ceiling ``MET``
    at or above the floor   ABOVE the ceiling       ``NOT_MET``
    below the floor         at or below the ceiling ``NOT_MET``
    below the floor         ABOVE the ceiling       ``NOT_MET``
    ======================  ======================  ==========

    **Why it matters.** This is AC2's whole point. A ceiling that only ever fires when the ratio
    has already failed is not a second condition — it is decoration on the first, and eighty
    percent of a thousand findings would still be two hundred wrong accusations. The
    ratio-pass / exposure-fail row is the one that proves the ceiling is load-bearing, and it is
    watched **failing**, not only passing.

    **Non-vacuity:** the four populations are GENERATED from the resolved floors and the resolved
    ceiling rather than typed, so they cannot drift away from the thresholds they straddle; and
    the ratio arm of the passing row is asserted to actually clear the floor before the outcome is
    read, so a ``MET`` cannot be produced by an accidentally-failing input.
    """
    floors = resolution_floors()
    ratio = precision_floor()
    ceiling = MAX_FALSE_ACCUSATION_EXPOSURE

    # Generated, not typed: FP counts straddling the ceiling, TP counts chosen so the ratio
    # lands on the required side of the floor for each corner.
    fp_ok, fp_over = ceiling, ceiling + 1

    def tp_for(fp: int, *, clearing: bool) -> int:
        """Smallest TP making tp/(tp+fp) clear (or miss) the floor. Exact Fraction, no float."""
        tp = 0
        while Fraction(tp, tp + fp) < ratio:
            tp += 1
        return tp if clearing else 0

    corners = {
        ("ratio PASS", "exposure PASS"): (tp_for(fp_ok, clearing=True), fp_ok, "MET"),
        ("ratio PASS", "exposure FAIL"): (tp_for(fp_over, clearing=True), fp_over, "NOT_MET"),
        ("ratio FAIL", "exposure PASS"): (tp_for(fp_ok, clearing=False), fp_ok, "NOT_MET"),
        ("ratio FAIL", "exposure FAIL"): (tp_for(fp_over, clearing=False), fp_over, "NOT_MET"),
    }

    seen: dict[tuple[str, str], str] = {}
    for corner, (tp, fp, expected) in corners.items():
        population = tp + fp
        assessment = evaluate(
            verdict_eligible_count=population,
            contributing_member_count=floors.contributing_members,
            sealed_contributing_member_count=floors.sealed_contributing_members,
            true_positive_count=tp,
            false_accusation_count=fp,
        )
        # Non-vacuity: the corner really is the corner it claims to be.
        measured = Fraction(tp, population)
        assert (measured >= ratio) is (corner[0] == "ratio PASS"), (
            f"corner {corner} was generated with precision {measured}, which is on the WRONG "
            f"side of the floor {ratio}. The table below would then be asserting something other "
            "than what it says."
        )
        assert (fp > ceiling) is (corner[1] == "exposure FAIL"), (
            f"corner {corner} was generated with {fp} false accusation(s) against a ceiling of "
            f"{ceiling}, which is on the wrong side of it."
        )
        assert assessment.outcome in CRITERION_OUTCOMES
        seen[corner] = assessment.outcome
        assert assessment.outcome == expected, (
            f"{corner}: evaluate() returned {assessment.outcome!r}, expected {expected!r} over "
            f"{tp} TP / {fp} FP. Reason given: {assessment.reason}"
        )
        assert assessment.false_accusation_count == fp
        assert assessment.measured_precision == measured

    # ── THE CLAIM, stated as a claim: the two arms are INDEPENDENT. ──
    assert seen[("ratio PASS", "exposure PASS")] != seen[("ratio PASS", "exposure FAIL")], (
        "holding the ratio at a PASSING value and pushing false accusations past the ceiling did "
        "NOT change the outcome. The exposure ceiling is therefore redundant with the ratio and "
        "AC2's absolute cap does not exist — a ratio alone cannot see two hundred wrong "
        "accusations behind a good percentage."
    )
    assert seen[("ratio PASS", "exposure PASS")] != seen[("ratio FAIL", "exposure PASS")], (
        "holding false accusations at a PASSING value and dropping the ratio below the floor did "
        "NOT change the outcome, so the ratio arm is inert."
    )


# ═════════════════════════════════════════════════════════════════════════════════════════
# AC2.1 — a thin or narrow population is UNEVALUABLE, never MET
# ═════════════════════════════════════════════════════════════════════════════════════════


def test_TC_ArgusAgent_PRECISION_001_138_a_thin_population_is_unevaluable_never_met() -> None:
    """TC-ArgusAgent-PRECISION-001-138 — AC2.1: the downward half of the exposure question.

    **Observable.** ``evaluate()``'s outcome over three populations that each breach exactly ONE
    resolution floor while carrying a ratio that would otherwise **pass**:

    * **breadth 2** — the MEASURED shape of both known candidate successors. ``V1`` draws from
      ``minions`` + ``agent-smith``; ``V2`` draws from ``agent-smith`` + ``minions``. Two
      contributing members against a floor of three, today, before either was ever graded. This
      row is the single most valuable thing this story pre-registers, and it is pre-registered
      **as a consequence** rather than discovered as a concession.
    * **yield one short of the floor** — the tiny denominator AC2 exists to refuse.
    * **sealed-contributing zero** — the measured state of the corpus: ``sealed ∩ ratified`` is
      EMPTY.

    **Why it matters.** A ratio alone is satisfiable by a tiny denominator, and ``UNEVALUABLE`` is
    a recorded failure to evaluate — never a pass, never a fail, and never an invitation to argue
    the floor down.

    **Non-vacuity:** each case is generated one below its RESOLVED floor (not typed), the ratio is
    asserted to clear the floor first so the ``UNEVALUABLE`` cannot be an accidental ``NOT_MET``
    in disguise, and a CONTROL population at exactly the floors is driven to ``MET`` — proving the
    fold is capable of returning something other than ``UNEVALUABLE`` over these inputs.
    """
    floors = resolution_floors()
    ratio = precision_floor()
    unevaluable = "UNEVALUABLE"
    assert unevaluable in CONDITION_VERDICTS, (
        "UNEVALUABLE is not in the imported protocol §5 verdict vocabulary, so this guard is "
        "comparing against a name this project no longer uses."
    )
    assert unevaluable in CRITERION_OUTCOMES

    tp, fp = MAX_FALSE_ACCUSATION_EXPOSURE * 9, MAX_FALSE_ACCUSATION_EXPOSURE
    population = tp + fp
    assert Fraction(tp, population) >= ratio, (
        f"the ratio used for every case below is {Fraction(tp, population)}, which does NOT "
        f"clear the floor {ratio}. Each UNEVALUABLE would then be explicable as a failed ratio "
        "and this guard would prove nothing about the resolution floors."
    )
    assert fp <= MAX_FALSE_ACCUSATION_EXPOSURE

    at_floor = {
        "verdict_eligible_count": max(population, floors.verdict_eligible_population),
        "contributing_member_count": floors.contributing_members,
        "sealed_contributing_member_count": floors.sealed_contributing_members,
        "true_positive_count": tp,
        "false_accusation_count": fp,
    }
    control = evaluate(**at_floor)
    assert control.outcome == "MET", (
        f"the CONTROL population, sitting exactly at every resolved floor with a passing ratio "
        f"and a passing exposure, returned {control.outcome!r} rather than MET ({control.reason})."
        " The fold is incapable of returning MET over these inputs, so the UNEVALUABLE results "
        "below are not evidence of the floors doing anything."
    )

    thin_cases = {
        "breadth 2 — the measured shape of BOTH candidate successors": {
            **at_floor,
            "contributing_member_count": 2,
            "sealed_contributing_member_count": 2,
        },
        "yield one below the resolved population floor": {
            **at_floor,
            "verdict_eligible_count": floors.verdict_eligible_population - 1,
            "true_positive_count": floors.verdict_eligible_population - 1,
            "false_accusation_count": 0,
        },
        "sealed-contributing 0 — sealed ∩ ratified is EMPTY": {
            **at_floor,
            "sealed_contributing_member_count": 0,
        },
    }
    for label, population_kwargs in thin_cases.items():
        assessment = evaluate(**population_kwargs)
        assert assessment.outcome == unevaluable, (
            f"{label}: evaluate() returned {assessment.outcome!r}, expected {unevaluable!r}. "
            f"Reason given: {assessment.reason}. A population that fails a resolution floor has "
            "no ratio worth reporting; grading it anyway is how a two-member score becomes a "
            "score."
        )
        assert assessment.outcome != "MET"
        assert assessment.reason, "an UNEVALUABLE with no recorded reason is unauditable"

    # ── RED, EXECUTED: the breadth case must be UNEVALUABLE *because of breadth*, and must
    #    flip back to MET when only that count is restored. Otherwise the case proves nothing. ──
    restored = evaluate(**{**thin_cases["breadth 2 — the measured shape of BOTH candidate successors"],
                           "contributing_member_count": floors.contributing_members,
                           "sealed_contributing_member_count": floors.sealed_contributing_members})
    assert restored.outcome == "MET", (
        "restoring ONLY the contributing-member count did not flip the outcome back to MET "
        f"(got {restored.outcome!r}: {restored.reason}), so the UNEVALUABLE above was caused by "
        "something other than the breadth floor and this case is mislabelled."
    )


# ═════════════════════════════════════════════════════════════════════════════════════════
# AC3.2 / AC3.3 — the criterion cannot look, cannot fetch, cannot write; and nothing moved
# ═════════════════════════════════════════════════════════════════════════════════════════


def test_TC_ArgusAgent_PRECISION_001_141_the_criterion_cannot_look_fetch_or_write() -> None:
    """TC-ArgusAgent-PRECISION-001-141 — AC3.2/AC3.3: 'it ratifies nothing' as a PROPERTY.

    **Observable, part one.** The forbidden module names and write surfaces reachable from
    ``scripts/precision_preregistration.py``'s AST: ``argus.detectors.*`` (the *looking* ban),
    ``urllib`` / ``requests`` / ``http.client`` / ``socket`` / ``ftplib`` (the *fetching* ban,
    protocol §6 R2), ``subprocess`` (a pure criterion spawns nothing), and any write mode —
    ``open(..., 'w'/'a')``, ``Path.write_*``, ``json.dump``.

    **Observable, part two.** The five constants this story must leave untouched, re-measured BY
    IMPORT: ``eligible_member_count()``, ``len(MANIFEST_FIELDS)``, ``len(GATE_OUTCOMES)``,
    ``len(CONDITION_VERDICTS)`` and ``validation_floor_n()``.

    **Why it matters.** *"This story ratifies nothing, fetches nothing and spends nothing"* is a
    promise until something makes it unexpressible. A criterion that could import the detector
    could be tuned to the verdict; a criterion that could fetch could stage a corpus member; a
    criterion that could write could re-register itself. And a criterion that quietly changed
    ``CONDITION_VERDICTS`` would have amended protocol §5 while claiming not to.

    **Non-vacuity, asserted BEFORE the absence:** the walk is proved able to SEE dotted
    ``argus.*`` paths (the module's four resolving imports), and able to SEE a write surface
    (``Path.read_text`` is deliberately NOT banned, so the attribute-call machinery is exercised
    against a real call it must let through).

    **Adversarial, EXECUTED and GENERATED:** one mutant per forbidden import name and one per
    write shape, each injected into the REAL source text; every one must be caught.
    """
    source = _criterion_source()
    imported = _dotted_imports(source)

    assert any(name.startswith("argus.precision") for name in imported), (
        f"the walk did not see any `argus.precision` import among {sorted(imported)}. That import "
        "is REQUIRED to be visible here: it proves the walk resolves dotted `argus.*` paths, so "
        "the absence of `argus.detectors` below is a MEASURED absence rather than an artifact of "
        "a walk that reads nothing."
    )

    seen_forbidden = _forbidden_imports_seen(source)
    assert not seen_forbidden, (
        f"{_CRITERION_REL_PATH} imports {list(seen_forbidden)}. The criterion may reference the "
        "defect's DEFINITION and may never reference the tool's VERDICT, reach the network, or "
        "spawn a process. Protocol §6 R2: fetching third-party source is not an autonomous act."
    )

    write_surfaces = _write_surfaces_seen(source)
    assert not write_surfaces, (
        f"{_CRITERION_REL_PATH} can WRITE: {list(write_surfaces)}. A pre-registration that can "
        "write is a pre-registration that can re-register itself, which is the one thing a "
        "pre-registration must not be able to do."
    )

    # ── RED, EXECUTED and GENERATED: one mutant per banned name, both import forms. ──
    for banned in _FORBIDDEN_IMPORTS:
        for injected in (f"import {banned}\n", f"from {banned} import thing\n"):
            assert banned in _forbidden_imports_seen(injected + source), (
                f"the import ban missed an injected {injected.strip()!r}. Half the ways to breach "
                "it are unguarded, and the silence above means nothing."
            )
    assert _forbidden_imports_seen("import argus.detectors.vacuous_test\n" + source), (
        "the ban missed a SUBMODULE import of argus.detectors, so the looking ban is walkable."
    )
    assert not _forbidden_imports_seen("import argus.precision.gate_yield\n" + source), (
        "the ban flagged `argus.precision`, which is REQUIRED. A predicate that rejects the "
        "permitted import is not discriminating between reach and verdict — it is rejecting "
        "everything, and its verdict above is meaningless."
    )

    write_mutants = (
        'open("x", "w")\n',
        "open('x', mode='a')\n",
        'Path("x").write_text("y")\n',
        'Path("x").write_bytes(b"y")\n',
        "json.dump({}, handle)\n",
    )
    for mutant in write_mutants:
        assert _write_surfaces_seen(mutant + source), (
            f"the write ban missed an injected {mutant.strip()!r}."
        )
    assert not _write_surfaces_seen('Path("x").read_text(encoding="utf-8")\n' + source), (
        "the write ban flagged a READ. A predicate that rejects every attribute call is not "
        "discriminating writes from reads and its verdict above measures nothing."
    )

    # ── AC3.2: nothing this story must not touch has moved. Measured BY IMPORT. ──
    after = {
        "eligible_member_count()": eligible_member_count(),
        "len(MANIFEST_FIELDS)": len(MANIFEST_FIELDS),
        "len(GATE_OUTCOMES)": len(GATE_OUTCOMES),
        "len(CONDITION_VERDICTS)": len(CONDITION_VERDICTS),
        "validation_floor_n()": validation_floor_n(),
    }
    assert after == _CONSTANTS_BEFORE, (
        f"a constant Story 17.1 must not touch has MOVED: before {_CONSTANTS_BEFORE}, after "
        f"{after}. Ratifying a member, adding a manifest field, inventing a terminal state or "
        "moving the locked N floor are each an operator act this story is forbidden — and each "
        "would silently re-shape the criterion pre-registered against them."
    )
    assert PRECISION_GATE_THRESHOLD == precision_floor(), (
        "precision_floor() no longer returns protocol §5's locked threshold object, so the "
        "criterion's ratio floor has forked from the gate's own."
    )
    assert POPULATION_ID and SUCCESSOR_OUTPUT_PATHS, (
        "the population and the successor-output path set must both be declared and non-empty; "
        "an empty one makes every absence asserted about them an absence over nothing."
    )


# ═════════════════════════════════════════════════════════════════════════════════════════
# AC4.3 — the ordering, proved from the object database rather than promised in prose
# ═════════════════════════════════════════════════════════════════════════════════════════


def test_TC_ArgusAgent_PRECISION_001_139_the_criterion_precedes_every_successor_output() -> None:
    """TC-ArgusAgent-PRECISION-001-139 — AC4.2/AC4.3: the ordering claim, checked MECHANICALLY.

    **Observable.** The commits reachable from ``PREREGISTRATION_COMMIT_SHA`` that touch any
    declared ``SUCCESSOR_OUTPUT_PATHS`` entry. The claim is that there are **none**.

    **Why it matters.** Story 17.1's entire value is the ORDER: the criterion was fixed while the
    verdict-eligible population was still zero. An intention to decide-before-looking is not
    evidence of having done so — git history is the evidence, and an asserted intention is not.

    **Three non-vacuity preconditions, each asserted BEFORE the absence it protects** (``-75``'s
    answer, reused verbatim rather than re-invented):

    1. the declared successor-output path set is **non-empty** — an empty pathspec makes
       ``git log`` report everything or nothing depending on invocation, and either way the
       assertion below would be meaningless;
    2. ``git log`` over a **control path known to carry commits** returns **non-empty** — this is
       the one that matters, because a misspelled or moved pathspec returns empty and is
       **indistinguishable from a clean ordering**;
    3. the ancestry predicate is driven to **BOTH** outcomes — asserted ``True`` for
       criterion-to-``HEAD`` and ``False`` for ``HEAD``-to-criterion — so it is watched
       **failing**, not only passing. Both use real resolvable shas in this repository; neither
       fabricates one.

    ⛔ **The ancestry guard over commits LATER than the pre-registration is Story 17.4's, not this
    story's.** 17.4 imports ``PREREGISTRATION_COMMIT_SHA`` and ``SUCCESSOR_OUTPUT_PATHS`` from the
    criterion module and re-types neither (``DN-16-4-2`` / ``AI-E9-7``).
    """
    from precision_preregistration import PREREGISTRATION_COMMIT_SHA

    # ── Precondition 0: the sha RESOLVES. Every assertion below is vacuous without it. ──
    assert PREREGISTRATION_COMMIT_SHA is not None, (
        "PREREGISTRATION_COMMIT_SHA is still None. A commit cannot contain its own sha, so it is "
        "written by the commit AFTER the one that froze the criterion — but it must be written."
    )
    assert len(PREREGISTRATION_COMMIT_SHA) == 40 and PREREGISTRATION_COMMIT_SHA.islower(), (
        "the pre-registration sha must be recorded as a full 40-character lowercase hex sha — a "
        "short sha is ambiguous, and this is the story's central citation."
    )
    kind = _git("cat-file", "-t", PREREGISTRATION_COMMIT_SHA)
    assert kind.returncode == 0 and kind.stdout.strip() == "commit", (
        f"the recorded pre-registration sha {PREREGISTRATION_COMMIT_SHA} does not resolve to a "
        f"commit in this repository (git said {kind.stdout.strip()!r} / "
        f"{kind.stderr.strip()!r}). The ordering claim is a claim about git history and cannot "
        "be established against a sha that is not in it."
    )

    # ── Precondition 1: the declared output-path set is non-empty. ──
    assert SUCCESSOR_OUTPUT_PATHS, (
        "SUCCESSOR_OUTPUT_PATHS is empty, so the absence asserted below is an absence over "
        "nothing. Declare where a successor predicate's output would land, or this guard forbids "
        "nothing."
    )
    assert all(
        path and not path.startswith("/") and "\\" not in path
        for path in SUCCESSOR_OUTPUT_PATHS
    ), (
        "every SUCCESSOR_OUTPUT_PATHS entry must be repository-relative and forward-slash so the "
        "same string works as a git pathspec on both the Windows local gate and the ubuntu CI "
        f"matrix; got {list(SUCCESSOR_OUTPUT_PATHS)}."
    )

    # ── Precondition 2: prove the invocation can FIND something. ──
    control = _git(
        "log", "--format=%H", PREREGISTRATION_COMMIT_SHA, "--", _CONTROL_PATH_WITH_COMMITS
    )
    assert control.returncode == 0, f"control `git log` failed: {control.stderr.strip()!r}"
    control_commits = [line for line in control.stdout.splitlines() if line.strip()]
    assert control_commits, (
        f"`git log {PREREGISTRATION_COMMIT_SHA} -- {_CONTROL_PATH_WITH_COMMITS}` returned "
        "NOTHING. That path is known to carry commits, so this invocation is not capable of "
        "finding anything — and an invocation that finds nothing reports a clean ordering for a "
        "dirty one. The guard below would be vacuous; fix the invocation, never the assertion."
    )

    # ── THE CLAIM: no commit reachable from the criterion touches successor output. ──
    touching = _git(
        "log", "--format=%H", PREREGISTRATION_COMMIT_SHA, "--", *SUCCESSOR_OUTPUT_PATHS
    )
    assert touching.returncode == 0, f"`git log` failed: {touching.stderr.strip()!r}"
    offenders = [line for line in touching.stdout.splitlines() if line.strip()]
    assert not offenders, (
        f"{len(offenders)} commit(s) reachable from the pre-registration sha touch a declared "
        f"successor-output path {list(SUCCESSOR_OUTPUT_PATHS)}: {offenders[:5]}. The criterion "
        "would then have been fixed with a successor's output already in hand, which is exactly "
        "the failure Story 17.1 exists to prevent — a standard chosen once the result is in view."
    )

    # ── Precondition 3: the ancestry predicate, driven to BOTH outcomes. ──
    forward = _git("merge-base", "--is-ancestor", PREREGISTRATION_COMMIT_SHA, "HEAD")
    assert forward.returncode == 0, (
        f"the pre-registration commit {PREREGISTRATION_COMMIT_SHA} is NOT an ancestor of HEAD. It "
        "is on a detached or abandoned line of history, so it does not establish that the "
        "criterion preceded anything on the branch that shipped."
    )
    backward = _git("merge-base", "--is-ancestor", "HEAD", PREREGISTRATION_COMMIT_SHA)
    assert backward.returncode != 0, (
        "HEAD reports as an ancestor of the pre-registration commit, which cannot be true while "
        "the pre-registration commit is also an ancestor of HEAD unless they are the same "
        "commit. The ancestry predicate is therefore returning the same answer to both questions "
        "and is not discriminating anything — the forward assertion above proves nothing."
    )


# ═════════════════════════════════════════════════════════════════════════════════════════
# AC4.5 — the criterion is DIRECTIONALLY immutable: it may be strengthened, never loosened
# ═════════════════════════════════════════════════════════════════════════════════════════


def _module_level_literal(source: str, name: str) -> object:
    """The value module-level *name* is assigned, read from *source*'s AST. PURE.

    ``ast.literal_eval`` rather than ``exec``: the pinned blob is read to be COMPARED, and
    executing a historical revision of a module to find out what it said is a different and much
    larger act than parsing it.
    """
    for node in ast.walk(ast.parse(source)):
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        for target in targets:
            if isinstance(target, ast.Name) and target.id == name and node.value is not None:
                try:
                    return ast.literal_eval(node.value)
                except ValueError:
                    return None
    raise AssertionError(
        f"no module-level assignment to {name!r} was found in the pinned source. The frozen "
        "field set cannot be read, so the immutability check below would compare nothing."
    )


def _threshold_from(source: str) -> Fraction:
    """``PRECISION_GATE_THRESHOLD`` as an exact Fraction, read out of *source*'s AST. PURE.

    Read from the pinned ``replay_harness`` blob rather than assumed: the criterion RESOLVES its
    ratio floor, so *the ratio at the pin* is whatever protocol section 5's threshold was at the
    pin. A guard that compared today's value with today's value would be ``f(x) == f(x)``.
    """
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == _THRESHOLD_SYMBOL:
                call = node.value
                assert isinstance(call, ast.Call), (
                    f"{_THRESHOLD_SYMBOL} is not built by a call in the pinned blob; the ratio "
                    "floor at the pin cannot be read exactly and AR4 forbids approximating it."
                )
                args = [ast.literal_eval(arg) for arg in call.args]
                return Fraction(*args)
    raise AssertionError(
        f"{_THRESHOLD_SYMBOL} was not found in the pinned {_THRESHOLD_REL_PATH}, so the ratio "
        "floor at the pin cannot be established."
    )


def test_TC_ArgusAgent_PRECISION_001_140_the_criterion_may_only_be_strengthened() -> None:
    """TC-ArgusAgent-PRECISION-001-140 — AC4.5: strengthening only, enforced DIRECTIONALLY.

    **Observable.** The frozen field set read from the PINNED BLOB at
    ``PREREGISTRATION_COMMIT_SHA`` — ``POPULATION_ID``, ``PROTOCOL_VERSION``, the ratio floor and
    ``MAX_FALSE_ACCUSATION_EXPOSURE`` — compared against today's live values.

    **The direction is the whole point** (``DN-17-1-6``). Equality alone would make the criterion
    unamendable, and protocol section 5 is amended by dated addition precisely because an
    amendment can only make clearing HARDER. So:

    * ``ceiling <= ceiling_at_pin`` — the exposure cap may be **lowered**, never raised;
    * ``ratio >= ratio_at_pin`` — the precision floor may be **raised**, never lowered;
    * ``POPULATION_ID`` and ``PROTOCOL_VERSION`` **equal** — moving either is not a strengthening,
      it is measuring something else and calling it the same criterion.

    ⛔ ``PREREGISTRATION_COMMIT_SHA`` itself is **excluded** from the frozen field set: the commit
    that records it legitimately writes it, and including it would make the guard red by
    construction (section 2.2 of the story record).

    **Non-vacuity, asserted BEFORE the comparison:** the sha resolves and is an ancestor of HEAD;
    both pinned blobs are fetched and PARSE; each frozen field is actually FOUND in the pinned
    source (a missing name raises rather than defaulting to today's value); and the ratio at the
    pin is read from the pinned ``replay_harness`` blob rather than from the live import, so the
    comparison is not ``f(x) == f(x)``.

    **Adversarial, EXECUTED:** the directional predicate is driven to both outcomes on generated
    values — a loosened ceiling and a lowered ratio must both be rejected, and a strengthened
    ceiling and a raised ratio must both be accepted.
    """
    from precision_preregistration import PREREGISTRATION_COMMIT_SHA

    assert PREREGISTRATION_COMMIT_SHA is not None
    ancestry = _git("merge-base", "--is-ancestor", PREREGISTRATION_COMMIT_SHA, "HEAD")
    assert ancestry.returncode == 0, (
        f"{PREREGISTRATION_COMMIT_SHA} is not an ancestor of HEAD; the pin does not describe "
        "this branch's history."
    )

    pinned = _pinned_blob(PREREGISTRATION_COMMIT_SHA, _CRITERION_REL_PATH)
    assert pinned.returncode == 0, (
        f"`git show {PREREGISTRATION_COMMIT_SHA}:{_CRITERION_REL_PATH}` failed: "
        f"{pinned.stderr.strip()!r}. The frozen criterion is unreadable, so nothing below is a "
        "comparison."
    )
    pinned_source = pinned.stdout
    assert pinned_source.strip(), "the pinned criterion blob is empty"
    ast.parse(pinned_source)  # a blob that does not parse makes every read below meaningless

    pinned_threshold_blob = _pinned_blob(PREREGISTRATION_COMMIT_SHA, _THRESHOLD_REL_PATH)
    assert pinned_threshold_blob.returncode == 0, (
        f"`git show {PREREGISTRATION_COMMIT_SHA}:{_THRESHOLD_REL_PATH}` failed: "
        f"{pinned_threshold_blob.stderr.strip()!r}."
    )

    population_at_pin = _module_level_literal(pinned_source, "POPULATION_ID")
    protocol_at_pin = _module_level_literal(pinned_source, "PROTOCOL_VERSION")
    ceiling_at_pin = _module_level_literal(pinned_source, "MAX_FALSE_ACCUSATION_EXPOSURE")
    ratio_at_pin = _threshold_from(pinned_threshold_blob.stdout)

    assert isinstance(population_at_pin, str) and population_at_pin, (
        "POPULATION_ID at the pin is empty or not a string; the equality below would hold "
        "trivially."
    )
    assert isinstance(ceiling_at_pin, int) and ceiling_at_pin > 0, (
        f"the exposure ceiling at the pin read as {ceiling_at_pin!r}; a non-positive or "
        "unreadable ceiling makes the directional comparison meaningless."
    )
    assert isinstance(ratio_at_pin, Fraction) and 0 < ratio_at_pin <= 1

    # ── THE CLAIM: equal where it must be equal, directional where it may move. ──
    assert POPULATION_ID == population_at_pin, (
        "POPULATION_ID has MOVED since the criterion was frozen. Measuring a different "
        "population is not a strengthening of the criterion — it is a different criterion "
        "wearing the same name and the same date."
    )
    assert PROTOCOL_VERSION == protocol_at_pin, (
        f"PROTOCOL_VERSION has moved from {protocol_at_pin!r} to {PROTOCOL_VERSION!r} since the "
        "pin. A pre-registration folded across an amendment is a re-interpretation of judgements "
        "nobody re-made."
    )
    assert MAX_FALSE_ACCUSATION_EXPOSURE <= ceiling_at_pin, (
        f"the exposure ceiling has been RAISED from {ceiling_at_pin} to "
        f"{MAX_FALSE_ACCUSATION_EXPOSURE}. STRENGTHENING ONLY: the ceiling may be lowered and "
        "never raised once the criterion is pinned. Raising it after the fact permits more false "
        "accusations than were pre-registered, which is the defect this story exists to prevent."
    )
    assert precision_floor() >= ratio_at_pin, (
        f"the ratio floor has been LOWERED from {ratio_at_pin} to {precision_floor()}. "
        "STRENGTHENING ONLY: it may be raised and never lowered."
    )

    # ── RED, EXECUTED: the direction predicate driven to BOTH outcomes on generated values. ──
    def strengthening(ceiling: int, ratio: Fraction) -> bool:
        return ceiling <= ceiling_at_pin and ratio >= ratio_at_pin

    assert strengthening(ceiling_at_pin, ratio_at_pin), "an unchanged criterion must be accepted"
    assert strengthening(ceiling_at_pin - 1, ratio_at_pin), "a LOWERED ceiling must be accepted"
    assert strengthening(ceiling_at_pin, ratio_at_pin + Fraction(1, 100)), (
        "a RAISED ratio floor must be accepted — protocol section 5's own amendments are "
        "permitted precisely because they can only make clearing harder."
    )
    assert not strengthening(ceiling_at_pin + 1, ratio_at_pin), (
        "a RAISED ceiling was accepted, so the directional predicate is not directional and the "
        "assertions above are equality checks that happen to pass."
    )
    assert not strengthening(ceiling_at_pin, ratio_at_pin - Fraction(1, 100)), (
        "a LOWERED ratio floor was accepted, so the ratio arm of the asymmetry is inert."
    )
