"""Story 15.1 — the SELECTION harness, and the ORDERING claim that gives it its meaning.

Verification area ``TC-ArgusAgent-PRECISION-001-74``..``-79``. **No new area is opened**: the
validation set is the precision gate's substrate, so its selection guards continue the existing
``PRECISION-001`` area. Ids are the next **actually free** ones — the area ran to ``-73`` across
five modules when this module was created, and ``-21..-31`` is only this area's range *inside*
``tests/test_validation_corpus.py``. No existing id was renumbered; an id here is a citation.

**Why these guards exist, in one sentence.** Story 15.1's whole claim is that the bench was
chosen **before anyone looked at what Argus says about it** — and an intention to pick-before-
looking is not evidence of having done so. Git history is the evidence; an asserted intention is
not. So the ban on looking is enforced by an ``ast`` walk (``-74``), the ordering is checked
against real git history (``-75``), the shapes a candidate row can silently take are checked by
a pure fold (``-76``), the criteria are pinned as code rather than prose (``-77``), candidacy is
held distinct from membership (``-78``), and every candidate's recorded justification is proved
substantive and free of any detector output (``-79``).

**The two halves of the ban, and why both ends are needed.** ``-74`` closes the *measurement*
end: the harness cannot import the detector, so no verdict could have reached a figure. ``-79``
closes the *record* end: no verdict may be written into a candidate's rationale by hand either.
A ban held at only one end is a ban somebody walks around.

**Why this module is separate from ``tests/test_validation_corpus.py``.** These guards are about
``scripts/candidate_selection.py``, not about the manifest — the repository already pairs
``scripts/pinned_corpus_snapshot.py`` with ``tests/test_pinned_corpus_snapshot.py`` and this
follows that precedent. It is also the NFR-M1 answer: folding ~300 lines into the 859-line manifest
guard module would make it the tightest test module in the repository and push the next change
into a split. **Cohesion split over a shave**, and no ``_EXEMPT_BY_DESIGN`` entry.

**⛔ NON-VACUITY IS THE POINT, NOT A FORMALITY.** Every guard below asserts a **NEGATIVE** — no
detector import, no output commit before the criteria, no malformed candidate row. This project's
signature defect is a guard that asserts an absence over a population it never actually read:
Epic 14 shipped **35** guards and **4** were not real, one of them (``-107``) reducing to
``f(x) == f(x)`` on a pure function. An absence is only evidence if the population was proved
non-empty **first**, so each guard here pins its precondition **before** its assertion, and each
predicate is driven to **BOTH** outcomes by an **executed mutation** rather than by a claim that
one was observed.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "corpus"))

from _manifest import (  # noqa: E402
    AST_INELIGIBLE_LANGUAGES,
    VALIDATION_CORPUS,
    CorpusMemberSpec,
    eligible_member_count,
    unratified_bench_candidates,
)

from candidate_selection import (  # noqa: E402
    COOCCURRENCE_FILE_FLOOR,
    CRITERIA,
    IN_SCOPE_LANGUAGES,
    TEST_FILE_FLOOR,
    candidate_row_defects,
    cooccurs,
)

_HARNESS_SOURCE = _REPO_ROOT / "scripts" / "candidate_selection.py"

#: AC1.1 — the commit that froze the selection criteria and the candidate sweep. Recorded as a
#: full 40-hex sha because a short sha is ambiguous and this is the story's central citation.
CRITERIA_COMMIT_SHA = "16d7100d73261c759d6176351f2caeff3d1fe172"

#: AC1.2 — the declared CANDIDATE-OUTPUT paths: where Argus output over a *candidate* would land
#: if anyone had run the detector over one. The ordering claim is that no commit reachable from
#: the criteria commit touches any of them.
#:
#: These are deliberately candidate-scoped rather than "anything under validation-corpus/". The
#: existing `validation-corpus/` artifacts are output over the five RATIFIED members and predate
#: this story by weeks; folding them in would make the guard assert something false and invite
#: somebody to "fix" it by loosening the assertion.
CANDIDATE_OUTPUT_PATHS: tuple[str, ...] = (
    "_bmad-output/design-artifacts/ArgusAgent/validation-corpus/candidates",
    "_bmad-output/audit-reports/candidates",
)

#: A path KNOWN to carry commits. Without it, a misspelled pathspec returns empty and reads
#: exactly like a clean ordering — the single most likely way ``-75`` could pass vacuously.
_CONTROL_PATH_WITH_COMMITS = "tests/corpus/_manifest.py"


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    """A pure READ of this repository's history. Never mutates: no checkout, no commit."""
    return subprocess.run(
        ["git", "-C", str(_REPO_ROOT), *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


def _dotted_imports(source: str) -> set[str]:
    """Every module name *source* imports, as FULL dotted paths. PURE — no I/O (AR8).

    Full dotted paths, not top-level packages: the AC2.2 ban distinguishes ``argus.index``
    (permitted) from ``argus.detectors`` (banned), and a walk that collapsed both to ``argus``
    could not tell them apart — it would pass while seeing nothing, which is the vacuity shape.
    """
    imported: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    return imported


def _imports_the_detector(source: str) -> bool:
    """AC2.2's predicate, isolated so it can be driven to BOTH outcomes. PURE."""
    return any(
        name == "argus.detectors" or name.startswith("argus.detectors.")
        for name in _dotted_imports(source)
    )


# ─────────────────────────────────────────────────────────────────────────────────────
# AC2.2 — the import ban: "we did not look" as a PROPERTY, not a promise
# ─────────────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_74_the_selection_harness_can_never_read_the_detector() -> None:
    """TC-ArgusAgent-PRECISION-001-74 — AC2.2: the strongest guard in Story 15.1.

    The selection harness may import ``argus.index.*`` and must NEVER import
    ``argus.detectors.*``. The index measures whether a test is **visible** — the instrument's
    *reach*. The detector measures whether it is **guilty** — the instrument's *output*. Choosing
    repositories the detector already flagged is criterion-shopping wearing public repositories
    as a disguise, and it is the same fallacy the Story 13.1 amendment rejected by name when it
    refused *"an externalization gate clearable by a corpus the team authored, planted, and wrote
    the answers for."*

    Modelled on ``-28``, which does this for network imports, and carrying ``-28``'s own
    non-vacuity floor plus a **stronger second one**:

    (i)   the walk found imports **at all** — otherwise the closure is broken, not clean;
    (ii)  the walk can **SEE** ``argus.index`` — which proves dotted-name extraction actually
          resolves ``argus.*`` paths, so the *absence* of ``argus.detectors`` is a measured
          absence rather than an artifact of a walk that reads nothing;
    (iii) the predicate is driven to its OTHER outcome by an **executed mutation** — a detector
          import is injected into the real source text and the same analyzer must catch it.

    (ii) is the one that matters. Without it, collapsing dotted names to their top-level package
    would make this guard pass forever while checking nothing.
    """
    source = _HARNESS_SOURCE.read_text(encoding="utf-8")
    imported = _dotted_imports(source)

    assert imported, (
        "the ast walk over the selection harness found NO imports at all — the closure is "
        "broken, not clean. A ban that reads nothing forbids nothing."
    )
    assert any(name.startswith("argus.index") for name in sorted(imported)), (
        f"the walk did not see any `argus.index` import among {sorted(imported)}. That import "
        "is REQUIRED to be visible here: it is what proves this walk resolves dotted `argus.*` "
        "paths at all. Without it, the `argus.detectors` assertion below would pass while "
        "seeing nothing — an absence measured over an empty population."
    )

    assert not _imports_the_detector(source), (
        f"scripts/candidate_selection.py imports argus.detectors (saw {sorted(imported)}). "
        "AC2.2: selection may measure the instrument's REACH (argus.index — is this test "
        "visible?) and may never read its OUTPUT (argus.detectors — is this test guilty?). A "
        "criterion may reference the defect's DEFINITION; it may never reference the tool's "
        "VERDICT. This is what converts 'we did not look' from a promise into a property."
    )

    # ── RED, EXECUTED. Not "observed once by hand" — driven here, every run. ──
    mutated = "from argus.detectors.vacuous_test import _is_test_function\n" + source
    assert _imports_the_detector(mutated), (
        "the ban predicate did NOT catch an injected `argus.detectors` import. It is therefore "
        "incapable of catching a real one, and its silence above means nothing."
    )
    mutated_plain = "import argus.detectors\n" + source
    assert _imports_the_detector(mutated_plain), (
        "the ban predicate missed a bare `import argus.detectors`; it only catches the "
        "`from ... import` form, so half the ways to breach it are unguarded."
    )


# ─────────────────────────────────────────────────────────────────────────────────────
# AC1 — the criteria were frozen BEFORE any output, and git history is the evidence
# ─────────────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_75_the_criteria_commit_precedes_every_candidate_output() -> None:
    """TC-ArgusAgent-PRECISION-001-75 — AC1.2/AC1.3: the ordering claim, checked MECHANICALLY.

    Story 15.1's central evidentiary claim is a claim about **git history**: the criteria and the
    candidate sweep landed in a commit containing no Argus output over any candidate. An asserted
    intention is not evidence of it, so this reads the real object database.

    **Three non-vacuity preconditions, each asserted BEFORE the absence it protects** (AC1.3):

    1. the declared candidate-output path set is **non-empty** — an empty pathspec makes
       ``git log`` report everything or nothing depending on invocation, and either way the
       assertion would be meaningless;
    2. ``git log`` over a **control path known to carry commits** returns **non-empty** — this is
       the one that matters, because a misspelled or moved pathspec returns empty and is
       **indistinguishable from a clean ordering**;
    3. the ancestry predicate is driven to **BOTH** outcomes — asserted ``True`` for
       criteria→HEAD and ``False`` for HEAD→criteria — so it is watched **failing**, not only
       passing. Both use real resolvable shas in this repository; neither fabricates one.
    """
    # ── Precondition 0: the sha RESOLVES. Every assertion below is vacuous without it. ──
    kind = _git("cat-file", "-t", CRITERIA_COMMIT_SHA)
    assert kind.returncode == 0 and kind.stdout.strip() == "commit", (
        f"the recorded criteria sha {CRITERIA_COMMIT_SHA} does not resolve to a commit in this "
        f"repository (git said {kind.stdout.strip()!r} / {kind.stderr.strip()!r}). Story 15.1's "
        "ordering claim is a claim about git history, and it cannot be established against a "
        "sha that is not in it."
    )
    assert len(CRITERIA_COMMIT_SHA) == 40 and CRITERIA_COMMIT_SHA.islower(), (
        "the criteria sha must be recorded as a full 40-character lowercase hex sha — a short "
        "sha is ambiguous, and this is the story's central citation."
    )

    # ── Precondition 1: the declared output-path set is non-empty. ──
    assert CANDIDATE_OUTPUT_PATHS, (
        "CANDIDATE_OUTPUT_PATHS is empty, so the absence asserted below is an absence over "
        "nothing. Declare where candidate output would land, or this guard forbids nothing."
    )

    # ── Precondition 2: prove the invocation can FIND something. ──
    control = _git("log", "--format=%H", CRITERIA_COMMIT_SHA, "--", _CONTROL_PATH_WITH_COMMITS)
    assert control.returncode == 0, f"control `git log` failed: {control.stderr.strip()!r}"
    control_commits = [line for line in control.stdout.splitlines() if line.strip()]
    assert control_commits, (
        f"`git log {CRITERIA_COMMIT_SHA} -- {_CONTROL_PATH_WITH_COMMITS}` returned NOTHING. That "
        "path is known to carry commits, so this invocation is not capable of finding anything "
        "— and an invocation that finds nothing reports a clean ordering for a dirty one. The "
        "guard below would be vacuous; fix the invocation, never the assertion."
    )

    # ── THE CLAIM: no commit reachable from the criteria sha touches candidate output. ──
    touching = _git(
        "log", "--format=%H", CRITERIA_COMMIT_SHA, "--", *CANDIDATE_OUTPUT_PATHS
    )
    assert touching.returncode == 0, f"`git log` failed: {touching.stderr.strip()!r}"
    offenders = [line for line in touching.stdout.splitlines() if line.strip()]
    assert not offenders, (
        f"{len(offenders)} commit(s) reachable from the criteria sha touch a declared "
        f"candidate-output path {list(CANDIDATE_OUTPUT_PATHS)}: {offenders[:5]}. The criteria "
        "would then have been written with Argus's verdicts already in hand, which is exactly "
        "the failure Story 15.1 exists to prevent — selecting on the tool's OUTPUT rather than "
        "on the defect's DEFINITION."
    )

    # ── Precondition 3: the ancestry predicate, driven to BOTH outcomes. ──
    forward = _git("merge-base", "--is-ancestor", CRITERIA_COMMIT_SHA, "HEAD")
    assert forward.returncode == 0, (
        f"the criteria commit {CRITERIA_COMMIT_SHA} is NOT an ancestor of HEAD. It is on a "
        "detached or abandoned line of history, so it does not establish that the criteria "
        "preceded anything on the branch that shipped."
    )
    backward = _git("merge-base", "--is-ancestor", "HEAD", CRITERIA_COMMIT_SHA)
    assert backward.returncode != 0, (
        "HEAD reports as an ancestor of the criteria commit, which cannot be true while the "
        "criteria commit is also an ancestor of HEAD unless they are the same commit. The "
        "ancestry predicate is therefore returning the same answer to both questions and is "
        "not discriminating anything — the forward assertion above proves nothing."
    )


# ─────────────────────────────────────────────────────────────────────────────────────
# AC4.3 / AC4.4 — the three checks __post_init__ does NOT perform on a candidate row
# ─────────────────────────────────────────────────────────────────────────────────────


def _candidate_rows() -> tuple[CorpusMemberSpec, ...]:
    """Rows admitted as CANDIDATES awaiting the protocol section 6 R2 ratification act.

    ⛔ DELEGATES; it does not re-implement. This function used to carry a VERBATIM COPY of
    ``_manifest.bench_candidates()``'s predicate, so when Story 16.4 corrected that predicate
    the copy here kept the defect — AR7's reuse-never-fork rule, and exactly the shape
    ``AI-E9-7`` warns about for constants.

    It maps to ``unratified_bench_candidates()`` rather than to ``bench_candidates()``, which
    keeps this module's behaviour BIT-IDENTICAL today: nothing is ratified, so the two
    populations coincide. Which of the guards below should measure the frozen BENCH instead of
    the pending subset is a semantic decision belonging to the story that carries the operator's
    ratification authority, and it is deliberately NOT taken here (Story 16.4 / HALT-3).
    """
    return unratified_bench_candidates()


def test_TC_ArgusAgent_PRECISION_001_76_a_candidate_row_cannot_carry_a_bad_pin_or_language() -> None:
    """TC-ArgusAgent-PRECISION-001-76 — AC4.3/AC4.4: what *"the guard is structural"* does NOT cover.

    ⛔ **THE MEASURED PREMISE — AMENDED 2026-08-20 (Story 16.2), STRUCK NOT ERASED.**
    ~~``CorpusMemberSpec.__post_init__`` returns early immediately after the ineligible-reason
    check, so on a row with ``eligible_for_n=False`` the sha, provenance and AST-eligibility
    validations never run.~~ That was true from 2026-08-19 to 2026-08-20 and this guard
    asserted it as a FACT precisely so a change to it could not pass unnoticed. **Story 16.2
    HOISTED the pin check above the early return**, because protocol §5's seal condition
    bisects on ``int(commit_sha, 16)`` and a candidate's pin therefore became an input to a
    gate condition. The premise now reads: the sha is validated for EVERY row; ``provenance``
    and AST-eligibility are still checked only on the eligible branch. *"The guard is
    structural"* is TRUE of the promotion path — flipping ``eligible_for_n`` to ``True`` while
    the reason is still present RAISES, so promotion takes two deliberate edits, both visible
    in a diff — TRUE of criterion 1 since 2026-08-20, and still FALSE of criteria 5 and 7 on a
    candidate row. If ``__post_init__`` ever stops validating, this guard says so rather than
    quietly becoming redundant.

    The three missing checks are added as a **pure fold over the rows**, never as a new
    ``__post_init__`` branch — a new branch would change behaviour for the five RATIFIED rows,
    which is outside this story and would move ``N``.

    ⛔ **RE-AUTHORED 2026-08-19 — the TRIPWIRE FIRED, exactly as it was built to.** This guard
    originally ended with ``assert len(candidates) == 0``. That was not a mistake and it is not
    being "fixed": at the time it was written the candidate population was genuinely empty — the
    first Story 15.1 pass swept the whole locally-resolvable universe, found eleven repositories
    and zero clearing ``COOCCURRENCE_FILE_FLOOR``, and halted on the protocol §6 R2 operator act
    rather than fabricate a bench. AC4.4 requires the population be proved **non-empty before**
    any per-row absence is read off it, and that assertion could not be made truthfully then.
    Folding over an empty tuple and passing forever is this project's signature defect — 4 of
    Epic 14's 35 guards failed exactly that way — so the emptiness was asserted **exactly**, with
    instructions to replace it the moment a real population existed.

    **The operator authorised the fetch on 2026-08-19** (recorded as a dated strike on AC5), the
    frozen criteria were applied unchanged to twenty fetched repositories, fourteen passed, and
    this assertion went RED on the first run afterwards. It is therefore **replaced, not
    deleted and not relaxed to ``>= 0``**: the AC4.4 population arm is now completed as intended
    — the population is asserted non-empty, its size is asserted against AC6.1's band, and the
    fold is asserted to have actually visited every row, so "no defects" can never again mean
    "nothing was inspected".
    """
    # ⛔ ── THE TRIPWIRE FIRED AGAIN, 2026-08-20 (Story 16.2 / AC2.3). ──────────────────────
    # This block used to assert, as a PREMISE, that a candidate row with commit_sha="deadbeef"
    # or "zzzz" CONSTRUCTS SILENTLY — and the docstring above says why in its own words:
    # *"if __post_init__ ever stops returning early, this guard says so rather than quietly
    # becoming redundant."* Story 16.2 hoisted the pin check ABOVE the `not eligible_for_n`
    # early return, and this guard went RED on the first run afterwards. That is the tripwire
    # working, so the premise is RE-AUTHORED to the new truth rather than the hoist being
    # reverted or this assertion deleted.
    #
    # WHY THE PIN MOVED AND THE LANGUAGE DID NOT, which is the whole content of the change.
    # The pin stopped being inert metadata awaiting an operator act: protocol §5's SEAL
    # condition bisects on int(commit_sha, 16), so a candidate's pin is now an INPUT TO A
    # GATE CONDITION and a sha-ordered rule over unvalidated shas is not mechanically
    # reproducible. `primary_language` is unchanged: criterion 5 is still checked by the
    # pure fold below and NOT by __post_init__, because adding that branch would change
    # behaviour for the five RATIFIED rows and move N — which is outside both stories.
    #
    # STRICTLY STRONGER, never a relaxation (DF-8-5-B): the premise moves from "constructs"
    # to "RAISES", the bad pins are asserted refused on an INELIGIBLE row (where nothing
    # checked them before), and the legal shape is asserted to still construct so this is
    # not a guard that simply refuses everything. `tests/test_gate_seal.py::-92` drives the
    # same hoist from the seal side, over a generated family of malformed pins.
    for bad_sha in ("deadbeef", "zzzz", "", "A" * 40, "0" * 39):
        with pytest.raises(ValueError, match="sha"):
            CorpusMemberSpec(
                member_id="premise-probe",
                repository_url="https://example.invalid/x.git",
                commit_sha=bad_sha,
                licence="MIT",
                primary_language="python",
                provenance="independent",
                eligible_for_n=False,
                ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
            )
    # ...and the control: a WELL-PINNED candidate row still constructs, so the refusal above
    # is about the pin and not about the row.
    CorpusMemberSpec(
        member_id="premise-probe",
        repository_url="https://example.invalid/x.git",
        commit_sha="a" * 40,
        licence="MIT",
        primary_language="python",
        provenance="independent",
        eligible_for_n=False,
        ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
    )
    # The LANGUAGE premise is UNCHANGED and still holds: criterion 5 is not structural on a
    # candidate row, and this row constructs silently today exactly as it always did.
    CorpusMemberSpec(
        member_id="premise-probe",
        repository_url="https://example.invalid/x.git",
        commit_sha="a" * 40,
        licence="MIT",
        primary_language="ruby",
        provenance="independent",
        eligible_for_n=False,
        ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
    )

    # ── AC4.2, the half that IS structural, asserted in the promotion direction. ──
    with pytest.raises(ValueError, match="ineligible_reason"):
        CorpusMemberSpec(
            member_id="premise-probe",
            repository_url="https://example.invalid/x.git",
            commit_sha="a" * 40,
            licence="MIT",
            primary_language="python",
            provenance="independent",
            eligible_for_n=True,
            ineligible_reason="candidate - awaiting operator ratification (protocol section 6 R2)",
        )

    # ── The checker must be proved able to REPORT before it is trusted to report none. ──
    clean = dict(
        member_id="probe",
        commit_sha="a" * 40,
        primary_language="python",
        licence="MIT License",
        ast_ineligible_languages=AST_INELIGIBLE_LANGUAGES,
    )
    assert candidate_row_defects(**clean) == (), (
        "the checker reports a defect on a well-formed candidate row, so every 'no defects' "
        "result it returns below is worthless."
    )
    mutations = {
        "short sha": {**clean, "commit_sha": "deadbeef"},
        "non-hex sha": {**clean, "commit_sha": "z" * 40},
        "AST-ineligible language": {**clean, "primary_language": "ruby"},
        "out-of-scope language": {**clean, "primary_language": "go"},
        "missing licence": {**clean, "licence": "   "},
    }
    for label, row in mutations.items():
        assert candidate_row_defects(**row), (
            f"the checker did NOT report a defect for {label!r}. It is therefore incapable of "
            "catching that shape, and its silence over the real population means nothing. This "
            "is DF-15-2-A arm (a): a guard is trusted only after it has been observed RED by an "
            "EXECUTED mutation, because 4 of Epic 14's 35 guards did not hold what they claimed."
        )

    # ── ⛔ AC4.4's POPULATION ARM, asserted BEFORE any absence is read off the rows. ──
    #
    # This is the replacement for the tripwire described in the docstring. The order matters and
    # is not cosmetic: the population is proved non-empty FIRST, and only then is each row's
    # "no defects" result treated as evidence. Reversed, a manifest that lost every candidate
    # row would report a clean sweep of nothing.
    candidates = _candidate_rows()
    assert candidates, (
        "there are ZERO candidate rows, so the per-row check below would fold over an empty "
        "tuple and pass while inspecting nothing — this project's signature defect, and the "
        "reason 4 of Epic 14's 35 guards were not real. If the bench was genuinely withdrawn, "
        "this guard must be re-authored to say so with the reason recorded, exactly as the "
        "tripwire it replaced was. It must never be relaxed to `>= 0`."
    )
    assert 12 <= len(candidates) <= 20, (
        f"the candidate population is {len(candidates)}, outside AC6.1's declared 12-20 band "
        f"(`DF-13-5-A`'s own number, pre-registered 2026-08-17 before any repository was "
        f"chosen). A band asserted here is a band that cannot drift into 'keep expanding until "
        f"it passes' — the failure mode the pre-registered ONE-round rule exists to prevent."
    )

    # ── The real population, per row — and the fold is COUNTED, so silence means inspection. ──
    inspected = 0
    for spec in candidates:
        defects = candidate_row_defects(
            member_id=spec.member_id,
            commit_sha=spec.commit_sha,
            primary_language=spec.primary_language,
            licence=spec.licence,
            ast_ineligible_languages=AST_INELIGIBLE_LANGUAGES,
        )
        assert not defects, f"candidate row {spec.member_id!r} is malformed: {list(defects)}"
        inspected += 1
    assert inspected == len(candidates), (
        f"the fold inspected {inspected} of {len(candidates)} candidate rows. A clean result "
        "over a partially-walked population is not a clean population."
    )

    # ── AC4.5 — N is unchanged. Candidates can never move it; that is the whole design. ──
    assert eligible_member_count() == 5, (
        f"N moved to {eligible_member_count()}. Story 15.1 is SELECTION ONLY: it does not "
        "ratify, and a candidate cannot count toward the floor. Ratification is an operator "
        "act (protocol section 6 R2)."
    )


def test_TC_ArgusAgent_PRECISION_001_77_the_criteria_are_declared_in_code_not_in_prose() -> None:
    """TC-ArgusAgent-PRECISION-001-77 — AC2.1: the criteria are CODE, never prose.

    ``AI-E9-7``: a predicate retyped into prose drifts from the one that runs. Section 1.1's
    1-versus-6 sensitivity is exactly why — the same corpus reads 1 or 6 depending on which
    assertion pattern is chosen, so an unnamed predicate is how a figure becomes folklore.

    Also pins ``DN-15-1-1``'s conjunction against the **refuted** definition: "constructs a mock"
    measured 0 TP / 26 FP, so a criterion satisfied by a mock binding ALONE would select exactly
    the population that already failed.
    """
    assert len(CRITERIA) == 7, f"the criteria set is {len(CRITERIA)} rows; AC2.1 declares seven"
    assert TEST_FILE_FLOOR == 50 and COOCCURRENCE_FILE_FLOOR == 10, (
        "DN-15-1-2 is a PAIR of numbers and the second is the real floor; both are pinned here "
        "so a silent retune is a test failure rather than a diff nobody reads."
    )
    assert IN_SCOPE_LANGUAGES == frozenset({"python", "typescript"}), (
        "AC3.1: Go, Java, PHP and the four AST-ineligible languages stay out. DF-14-3-A/-B are "
        "COUPLED and neither is reopened here."
    )

    binding_only = "m = MagicMock()\nresult = thing(m)\nassert result == 3\n"
    assertion_only = "obj.assert_called_once()\n"
    both = "m = MagicMock()\nthing(m)\nm.assert_called_once()\n"

    assert not cooccurs(binding_only), (
        "a file that merely BINDS a mock satisfies the criterion. That is the REFUTED "
        "definition — it measured 0 true positives and 26 false positives over the ratified "
        "corpus, and 21 of minions' 286 test files match it while only 1 carries the "
        "co-occurrence."
    )
    assert not cooccurs(assertion_only), (
        "a mock assertion with no mock binding satisfies the criterion; the conjunction is not "
        "being applied."
    )
    assert cooccurs(both), (
        "a file carrying BOTH a mock binding and a mock assertion does NOT satisfy the "
        "criterion, so the predicate cannot select the defect class at all and every zero it "
        "reports is meaningless."
    )


# ─────────────────────────────────────────────────────────────────────────────────────
# AC4.1 / AC6.1 — the candidate CONTRACT: what admission to this manifest does and does
# not mean. Ids continue from the true next-free id in the PRECISION-001 area (`-77`).
# ─────────────────────────────────────────────────────────────────────────────────────

#: AC4.1 — the EXACT reason every candidate row carries, character for character. A single
#: shared string rather than fourteen paraphrases: a per-row wording would let one row drift
#: into sounding ratified, and `_candidate_rows()` keys off this text to find the population at
#: all. It is declared here and asserted, never retyped into prose (`AI-E9-7`).
_RATIFICATION_PENDING_REASON = (
    "candidate - awaiting operator ratification (protocol section 6 R2)"
)


def test_TC_ArgusAgent_PRECISION_001_78_a_candidate_is_pending_a_decision_nobody_has_taken() -> None:
    """TC-ArgusAgent-PRECISION-001-78 — AC4.1/AC4.5/AC6.1: candidacy is a state, not a promotion.

    ⛔ **WHAT THIS GUARD IS FOR.** Fourteen third-party repositories entered the manifest on
    2026-08-19. Every one of them is *pending an operator decision that has not been taken* —
    protocol §6 R2, verbatim: *"choosing which repositories are legitimate members, and fetching
    third-party source, are not autonomous acts."* The single most damaging thing that could
    happen to this corpus is for that pending state to quietly read as ratified: a row that
    drifted into ``N`` would put the >=80% precision gate over a bench **no named human ever
    admitted**, which is the failure the whole protocol exists to prevent.

    So the properties that keep candidacy visibly distinct from membership are asserted here
    rather than trusted to a comment:

    (a) the population exists and sits inside AC6.1's declared 12-20 band;
    (b) every candidate is ``eligible_for_n=False`` and carries the EXACT pending reason;
    (c) every candidate's pin, id and URL is **distinct** — a duplicated pin would inflate the
        apparent bench while measuring the same bytes twice;
    (d) ``N`` is **still 5**, and the eligible set is the ratified five, disjoint from these.

    **Non-vacuity (``DF-15-2-A`` arm (a)).** The population is proved non-empty before any of
    the above is read off it, the fold is counted, and the exact-reason predicate is driven to
    **both** outcomes by an executed mutation — a near-miss wording must be rejected, or "every
    row matches" would be a statement about a predicate that matches anything.
    """
    candidates = _candidate_rows()
    assert candidates, (
        "there are ZERO candidate rows. Every assertion below would fold over an empty tuple "
        "and pass while checking nothing."
    )
    assert 12 <= len(candidates) <= 20, (
        f"{len(candidates)} candidates, outside AC6.1's 12-20 band. The band is `DF-13-5-A`'s "
        "own pre-registered number and is asserted so the bench cannot grow round after round."
    )

    # ── (b) The pending state, exact. ──
    checked = 0
    for spec in candidates:
        assert spec.eligible_for_n is False, (
            f"{spec.member_id!r} is marked ELIGIBLE while still described as a candidate. It "
            "would count toward N without any operator having admitted it — the protocol "
            "section 6 R2 act performed by nobody."
        )
        assert spec.ineligible_reason == _RATIFICATION_PENDING_REASON, (
            f"{spec.member_id!r} carries {spec.ineligible_reason!r}, not the exact pending "
            f"reason {_RATIFICATION_PENDING_REASON!r}. One row wording its own status is how a "
            "candidate starts reading as a member."
        )
        assert spec.provenance == "independent", (
            f"{spec.member_id!r}: provenance {spec.provenance!r}. Read AC2.3 — `independent` "
            "means 'not the tool auditing itself' and does NOT encode 'third-party'; the "
            "third-party property lives in the caveat prose because the closed vocabulary "
            "cannot express it."
        )
        checked += 1
    assert checked == len(candidates), (
        f"only {checked} of {len(candidates)} candidate rows were checked"
    )

    # ── ⛔ The predicate, driven to BOTH outcomes by an EXECUTED near-miss. ──
    near_miss = "candidate - awaiting operator ratification (protocol section 6 R3)"
    assert near_miss != _RATIFICATION_PENDING_REASON, "the mutation is not a mutation"
    assert near_miss.replace("R3", "R2") == _RATIFICATION_PENDING_REASON, (
        "the near-miss differs from the real reason by more than the one token it is meant to, "
        "so it does not test the equality it claims to test"
    )
    probe = replace(candidates[0], ineligible_reason=near_miss)
    assert probe.ineligible_reason != _RATIFICATION_PENDING_REASON, (
        "a row whose reason cites the WRONG protocol rule compares equal to the right one. The "
        "equality above is therefore satisfied by anything and asserts nothing."
    )

    # ── (c) Distinctness. A duplicated pin measures the same bytes twice under two names. ──
    for label, values in (
        ("member_id", [s.member_id for s in candidates]),
        ("commit_sha", [s.commit_sha for s in candidates]),
        ("repository_url", [s.repository_url for s in candidates]),
    ):
        duplicates = sorted({v for v in values if values.count(v) > 1})
        assert not duplicates, (
            f"duplicate candidate {label}(s): {duplicates}. The bench would look larger than "
            "the number of distinct trees it actually measures."
        )

    # ── (d) AC4.5 — N is UNCHANGED, and the eligible set is the ratified five, unmoved. ──
    eligible = {s.member_id for s in VALIDATION_CORPUS if s.eligible_for_n}
    assert eligible_member_count() == 5, (
        f"N moved to {eligible_member_count()}. Story 15.1 is SELECTION ONLY. Fourteen "
        "candidates landing must leave N at exactly 5, or a bench nobody ratified is already "
        "inside the gate's denominator."
    )
    assert not (eligible & {s.member_id for s in candidates}), (
        "a candidate id appears in the ELIGIBLE set. The two populations must stay disjoint "
        "until an operator moves a row between them, deliberately, in a visible diff."
    )
    assert len(eligible) == 5, f"the eligible set is {sorted(eligible)}, not the ratified five"


def test_TC_ArgusAgent_PRECISION_001_79_every_candidate_records_why_it_was_considered() -> None:
    """TC-ArgusAgent-PRECISION-001-79 — AC6.2/AC2.4: the justification is DATA, and it is measured.

    ⛔ **THE RULE THIS GUARD MAKES MECHANICAL** (§1.3, and the whole reason Story 15.1 exists):

        A criterion may reference the defect's DEFINITION.
        A criterion may never reference the tool's VERDICT.

    Selecting repositories likely to contain the defect is ordinary benchmark design — a bench
    for a null-pointer analyser is chosen from code that dereferences pointers. Selecting
    repositories **the detector already reported on** is criterion-shopping wearing public
    repositories as a disguise, and it is the same fallacy the Story 13.1 amendment rejected by
    name when it refused *"an externalization gate clearable by a corpus the team authored,
    planted, and wrote the answers for."*

    ``-74`` already makes the ban structural at the *harness* level: the selection module cannot
    import ``argus.detectors.*``, so no verdict could have reached the measurement. This guard
    closes the other end — the **recorded justification** — so that a future editor cannot write
    a detector result into a candidate's rationale by hand. It also enforces AC6.2's substance
    floor, the same one ``-24`` already applies to the two recorded exclusions: *an exclusion
    without a reason is an oversight wearing a decision's clothes*, and an ADMISSION without one
    is the same defect facing the other way.

    **Non-vacuity.** The population is proved non-empty first; the fold is counted; and both
    predicates — the substance floor and the verdict ban — are driven to **both** outcomes by
    executed probes, so neither can be a check that accepts everything.
    """
    candidates = _candidate_rows()
    assert candidates, "ZERO candidate rows — every assertion below would fold over nothing"

    #: Detector-OUTPUT vocabulary. A rationale containing any of these was written by someone
    #: who had read a verdict. Deliberately narrow and literal: broad words like "verdict" and
    #: "detector" appear in the caveats' own DISCLAIMERS, and a ban that fired on a row saying
    #: "this was not selected on the tool's verdict" would be a guard punishing honesty.
    verdict_vocabulary = (
        "vacuous_test",
        "true positive",
        "false positive",
        "flagged",
        "verdict-eligible",
        "blocking finding",
        "advisory finding",
    )

    def cites_a_verdict(text: str) -> bool:
        lowered = text.lower()
        return any(term in lowered for term in verdict_vocabulary)

    def is_substantive(text: str) -> bool:
        """AC6.2: a rationale that states WHY, and carries MEASURED figures rather than an
        impression. The digit requirement is the load-bearing half — "it uses a lot of mocks"
        is an impression; "215 of 497 test files carry the co-occurrence" is a measurement.
        """
        return (
            len(text.split()) >= 40
            and "CONSIDERED BECAUSE" in text
            and "THIRD-PARTY" in text
            and sum(character.isdigit() for character in text) >= 8
        )

    # ── ⛔ BOTH predicates driven to BOTH outcomes, by EXECUTED probes, BEFORE the population
    #    is read. A checker that has not been seen rejecting something is not a checker. ──
    clean_probe = (
        "THIRD-PARTY and arms-length. CONSIDERED BECAUSE its tests drive a network boundary "
        "that a unit suite must substitute, which is where an assertion against a mock-derived "
        "value lives. MEASURED at the pin with the detector NOT imported: 120 test files, 44 "
        "binding a mock primitive, 31 asserting on one, 27 carrying both, 1500 days of history."
    )
    assert is_substantive(clean_probe) and not cites_a_verdict(clean_probe), (
        "the checkers reject a well-formed rationale, so every row they accept below is "
        "accepted for the wrong reason"
    )
    assert not is_substantive("third-party, looks about right"), (
        "a five-word impression with no figures passes the substance floor; the floor is not a "
        "floor and AC6.2's 'with its measured figures' is unenforced"
    )
    assert not is_substantive(clean_probe.replace("CONSIDERED BECAUSE", "chosen since")), (
        "the substance floor does not require the rationale to state WHY the repository was "
        "considered at all, which is exactly what AC6.2 asks for"
    )
    assert cites_a_verdict(clean_probe + " Argus flagged 12 of these."), (
        "a rationale that reports what the detector said passes the verdict ban. The ban "
        "catches nothing, and selection-on-output could be recorded here undetected."
    )

    # ── The real population. ──
    examined = 0
    for spec in candidates:
        caveat = spec.adjudication_caveat or ""
        assert caveat.strip(), (
            f"{spec.member_id!r} was admitted as a candidate with NO recorded rationale. AC6.2 "
            "requires why-it-was-chosen with its measured figures; an admission without one is "
            "an oversight wearing a decision's clothes, the DN-4 rule facing forwards."
        )
        assert is_substantive(caveat), (
            f"{spec.member_id!r}: the rationale is not substantive — it must state THIRD-PARTY "
            "status, say CONSIDERED BECAUSE, run to at least 40 words and carry the measured "
            f"figures as digits. Got {len(caveat.split())} words: {caveat[:120]!r}"
        )
        assert not cites_a_verdict(caveat), (
            f"{spec.member_id!r}: the rationale cites the DETECTOR'S OUTPUT. A criterion may "
            "reference the defect's definition; it may never reference the tool's verdict. "
            "Selecting on output is criterion-shopping, and it would void the ordering claim "
            "that `-75` establishes over git history."
        )
        examined += 1

    assert examined == len(candidates) >= 12, (
        f"examined {examined} of {len(candidates)} candidate rationales; the closure did not "
        "run over the population"
    )
