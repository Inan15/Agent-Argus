"""Story 12.9 / AC3 — the GitHub Release note is GENERATED, and every claim in it is derived.

Verification area ``ArgusAgent-DOCS`` (``TC-ArgusAgent-DOCS-001-67``..``-70``, CONTINUING the
index that ended at ``-66``).

**The measurement this file exists for.** ``.github/workflows/release.yml:174-190`` built the
release-note body as a **string literal inside a ``run:`` script**, and that literal
hand-transcribed three pinned facts: the AR3 exit-code contract, the install command, and a
*paraphrase* of the FR34 disclosure. Story 12.8 changed what exit ``2`` can mean — a usage
error now returns the reserved ``1`` — corrected ``action.yml``'s map comment and
``docs/first-run.md``'s exit table, **and this literal did not move, because nothing could
see it.** ``release.yml`` is in ``_RELEASE_SURFACES``, so ``TC-ArgusAgent-DOCS-001-17`` scans
it for *over-claims*; no guard checked whether what it said was **true**.

So the body is now rendered by ``scripts/release_notes.py`` and this file asserts each claim
against the live source **in both directions**, with a ``> 0`` floor on claims checked — the
shape ``-63``/``-64`` already use for ``docs/first-run.md``, reused rather than re-invented.

**Why a separate module, recorded rather than assumed (AC3 / AC6.4).** AC3 asks that the
disclosure reaching the release channel be registered *where FR34 is enforced*, which is
``tests/test_instrument_disclosure.py``. That file is at **1179** of NFR-M1's 1200 lines —
21 lines of headroom — and, more importantly, its ``_DISCLOSURE_SURFACES`` registry is a
tuple of :class:`_Surface` records keyed by **committed file path** with a ``form`` field.
The release-note body is a **rendered string with no path**. Forcing it into that dataclass
would change the meaning of a shipped registry for one member, and relieving the line ceiling
to do it would mean splitting a 1179-line guard as a side effect of a release story. So the
note body is registered HERE and held to the SAME two-sided property ``-50`` states —
*presence AND no over-claim* — importing the same constants from
``argus.verdict.negative_assurance`` and the same over-claim detector from
``tests/test_release_surface_honesty.py``. One vocabulary, one authority, a second
population. That is the cohesion split 12.7/12.8 established as the NFR-M1 remedy, applied
before the ceiling was hit rather than after.

**These tests may import ``argus``; the generator may not** (Story 12.9 / DN-4). That
asymmetry is the whole design: ``scripts/release_notes.py`` runs on a bare runner before
anything is installed, so it reads the single-source modules as text and parses them with
``ast``; this file imports the live constants and asserts the two agree. A drift in either
direction is RED.

No network, no LLM, no ``.argus/`` write, no new dependency. Every file is opened
``encoding="utf-8"`` explicitly.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import release_notes as rn  # noqa: E402
import release_preflight as rp  # noqa: E402

from argus.verdict.negative_assurance import (  # noqa: E402
    INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED,
    INSTRUMENT_DISCLOSURE_VALIDATED,
    INSTRUMENT_STATUS,
    InstrumentStatus,
)
from argus.verdict.verdict_gate import Verdict, exit_code_for_verdict  # noqa: E402
from tests.test_release_surface_honesty import _affirmative_over_claims  # noqa: E402

_WORKFLOW = _REPO_ROOT / ".github" / "workflows" / "release.yml"
_GENERATOR = "scripts/release_notes.py"

# The tag the note is rendered for in these tests. It must equal the declared version, since
# the generator refuses to render a note whose tag and pyproject version disagree (E5,
# reused rather than restated) — which is itself part of the contract asserted below.
_TAG = f"v{rp.read_pyproject_version(_REPO_ROOT)}"

# A sha that no observed run covers, used where the test needs the NOT ESTABLISHED branch
# without depending on what HEAD happens to be.
_UNCOVERED_SHA = "f" * 40

# The single-source files the generator reads. Copied into a temporary tree by `-68` so a
# real mutation can be made at the REAL seam without ever rewriting the source tree.
_SINGLE_SOURCES: tuple[str, ...] = (
    "pyproject.toml",
    "argus/verdict/verdict_gate.py",
    "argus/verdict/negative_assurance.py",
    "argus/cli.py",
)

_DISCLOSURE_BY_STATUS = {
    InstrumentStatus.NOT_INDEPENDENTLY_VALIDATED: (
        INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED
    ),
    InstrumentStatus.VALIDATED: INSTRUMENT_DISCLOSURE_VALIDATED,
}


def _body(root: Path = _REPO_ROOT, sha: str = _UNCOVERED_SHA) -> str:
    return rn.render_release_note(_TAG, repo_root=root, released_sha=sha)


def _mirror_sources(destination: Path) -> Path:
    """Copy the generator's single-source files into *destination*, paths preserved."""
    for relative in _SINGLE_SOURCES:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(_REPO_ROOT / relative, target)
    return destination


def test_TC_ArgusAgent_DOCS_001_67_every_claim_in_the_note_is_derived() -> None:
    """TC-ArgusAgent-DOCS-001-67 — Story 12.9 / AC3: the note agrees with the live constants.

    OBSERVABLE: the rendered body, claim by claim, against the module that owns each fact —
    the version, the AR3 exit-code map (including the reserved code), the FR34 disclosure in
    its canonical single-sourced form, the install command, and AC2's derived release status.

    Both directions, and a ``> 0`` floor on claims checked, because a body that said nothing
    would satisfy every "must equal" assertion ever written.
    """
    body = _body()
    checked = 0

    # 1. the version, from pyproject.toml — and the tag it was rendered for.
    version = rp.read_pyproject_version(_REPO_ROOT)
    assert f"argus-agent` {_TAG}" in body, f"the note does not name the release: {body[:200]!r}"
    assert version in _TAG
    checked += 1

    # 2. the AR3 exit-code map, every member, from the gate itself.
    for member in Verdict:
        expected = f"{exit_code_for_verdict(member)}={member.value}"
        assert expected in body, (
            f"the note does not publish the live AR3 mapping {expected!r}. The exit code is "
            "the one fact a CI consumer acts on without reading anything else."
        )
        checked += 1
    assert "1=no verdict produced" in body, (
        "the note omits AR3's reserved code. Exit 1 is NOT a verdict, and a consumer who "
        "reads it as one has been handed a fabricated assessment (Story 12.8 / AC8)."
    )
    checked += 1

    # Direction two: the note may publish NO exit code the contract does not define.
    published = {int(code) for code in re.findall(r"\b(\d)=", body)}
    defined = {exit_code_for_verdict(member) for member in Verdict} | {1}
    assert published == defined, (
        f"the note's exit-code set is {sorted(published)} and the live wire contract is "
        f"{sorted(defined)}. A fifth code in a published note teaches a consumer to branch "
        "on something the tool cannot emit."
    )
    checked += 1

    # 3. the FR34 disclosure, canonical form, selected by the DECLARED status.
    assert _DISCLOSURE_BY_STATUS[INSTRUMENT_STATUS] in body, (
        "the note does not carry the FR34 instrument disclosure in its canonical "
        "single-sourced form. The old literal carried a PARAPHRASE, which is a second thing "
        "to keep true (AI-E9-7)."
    )
    checked += 1

    # 4. the install command, built from the tag under release.
    assert rn.install_command(_TAG) in body
    assert _TAG in rn.install_command(_TAG), "the install command does not embed the tag"
    checked += 1

    # 5. AC2's derived release status — the SAME function every other surface renders.
    status = rn.derive_release_status(rn.RECORDED_GATE_OBSERVATION, _UNCOVERED_SHA)
    assert status.statement in body, (
        "the note does not render the derived release status. A release note that states a "
        "status it typed itself is DF-AUD-APAA-C in the most-read document this project "
        "will ever publish."
    )
    assert not status.established and rn.NOT_ESTABLISHED in body
    checked += 1

    # 6. the visibility measurement, one source, rendered not retyped.
    assert rn.REPOSITORY_VISIBILITY_MEASUREMENT in body
    checked += 1

    assert checked >= 8, f"only {checked} claims were checked; the floor is not met"

    # And the body itself is honest by the same rule every other release surface is held to.
    assert not _affirmative_over_claims(body), (
        f"the generated release note ASSERTS an over-claim: {_affirmative_over_claims(body)}"
    )


def test_TC_ArgusAgent_DOCS_001_68_the_note_goes_red_when_a_source_fact_moves() -> None:
    """TC-ArgusAgent-DOCS-001-68 — Story 12.9 / AC3: the derivation BITES, at the real seam.

    OBSERVABLE: the rendered body, when a single-source constant is changed.

    AI-E11-1 clause (ii): a guard that has never been seen to move is not evidence. The
    generator reads its facts from files BY PATH, so the seam is the file — and the defect is
    injected into a temporary MIRROR of those files rather than into the source tree, because
    a committed test must never rewrite the tree to prove a point (``-23``'s established
    form).

    Three mutations, one per derived fact class: an exit code, the declared instrument
    status, and the disclosure constant's name. The third is the adversarial variant
    GENERATED from the registry the derivation closes over (clause (iii)) — a renamed single
    source must RAISE, never render an empty claim.
    """
    import pytest

    mirror = _mirror_sources(Path(__import__("tempfile").mkdtemp(prefix="argus-src-")))
    assert _body(mirror) == _body(), (
        "an untouched mirror of the single sources rendered a DIFFERENT note than the tree; "
        "the derivation is reading something other than these files and this control proves "
        "nothing"
    )

    # (a) an exit code moves.
    gate = mirror / "argus/verdict/verdict_gate.py"
    original = gate.read_text(encoding="utf-8")
    gate.write_text(
        original.replace("Verdict.NOT_READY_FOR_RELEASE: 2", "Verdict.NOT_READY_FOR_RELEASE: 7"),
        encoding="utf-8",
    )
    moved = _body(mirror)
    assert "7=NOT_READY_FOR_RELEASE" in moved and "2=NOT_READY_FOR_RELEASE" not in moved, (
        "the exit-code map changed in the single source and the rendered note did not "
        "follow — which is exactly the failure the old `run:` literal had"
    )
    gate.write_text(original, encoding="utf-8")
    assert "2=NOT_READY_FOR_RELEASE" in _body(mirror)

    # (b) the declared instrument status flips: the note must carry the OTHER disclosure.
    disclosure = mirror / "argus/verdict/negative_assurance.py"
    original_disclosure = disclosure.read_text(encoding="utf-8")
    disclosure.write_text(
        original_disclosure.replace(
            "INSTRUMENT_STATUS: InstrumentStatus = InstrumentStatus.NOT_INDEPENDENTLY_VALIDATED",
            "INSTRUMENT_STATUS: InstrumentStatus = InstrumentStatus.VALIDATED",
        ),
        encoding="utf-8",
    )
    flipped = _body(mirror)
    assert INSTRUMENT_DISCLOSURE_VALIDATED in flipped, (
        "flipping the DECLARED instrument status did not change the disclosure in the note. "
        "The day Epic 13's adjudication clears the gate, the release note would publish a "
        "stale disclosure."
    )
    assert INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED not in flipped

    # (c) ADVERSARIAL VARIANT, generated from the derivation's own source registry: rename a
    # single source and the generator must RAISE rather than render a note with a hole in it.
    disclosure.write_text(
        original_disclosure.replace(
            "INSTRUMENT_STATUS: InstrumentStatus =", "INSTRUMENT_STATUS_RENAMED: InstrumentStatus ="
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="no longer declares"):
        _body(mirror)
    disclosure.write_text(original_disclosure, encoding="utf-8")

    # (d) and the tag/version agreement is E5's handler, reused — not a second comparison.
    with pytest.raises(ValueError, match="E5"):
        rn.render_release_note(
            "v9.9.9", repo_root=_REPO_ROOT, released_sha=_UNCOVERED_SHA
        )


def test_TC_ArgusAgent_DOCS_001_69_the_workflow_invokes_the_generator_and_types_no_fact() -> None:
    """TC-ArgusAgent-DOCS-001-69 — Story 12.9 / AC3: the `run:` body states nothing itself.

    OBSERVABLE: the committed ``release.yml`` text — whether it calls the generator, whether
    it still carries any of the three facts it used to transcribe, and whether Story 11.3's
    injection invariance survived the edit.

    A generator nothing invokes is documentation, not a delivery — the same property
    ``TC-ArgusAgent-RELEASE-001-09`` asserts for the preflight, applied to this step.
    """
    workflow = _WORKFLOW.read_text(encoding="utf-8")

    assert _GENERATOR in workflow, (
        f"{_WORKFLOW.name} does not invoke {_GENERATOR}; the generator would be a module "
        "nobody runs and the note would still be whatever the `run:` body says"
    )
    assert "--notes-file" in workflow, "the release step does not consume the generated body"
    assert "--notes " not in workflow and '--notes "' not in workflow, (
        "the release step still passes an inline `--notes` literal. That literal is the "
        "transcription Story 12.9 / AC3 removed."
    )

    # The three transcribed facts are GONE from the workflow text. Each is asserted by the
    # phrase the old literal actually used, so a reworded copy is caught too.
    for gone, what in (
        ("0=RELEASE_READY", "the exit-code map"),
        ("typed audit failure", "the old, now-wrong gloss on exit 1"),
        ("externalization gate is PROVISIONAL", "the FR34 disclosure paraphrase"),
        ("git+https://github.com/Inan15/Agent-Argus.git@", "the install command"),
    ):
        assert gone not in workflow, (
            f"{_WORKFLOW.name} still transcribes {what} ({gone!r}). It has one source and "
            "the generator reads it; a copy here cannot track it, which is the measured "
            "defect this AC closes."
        )

    # Story 11.3's injection invariance, re-asserted because this story edited the file:
    # every untrusted value is bound through `env:` and referenced as a quoted shell
    # variable, never interpolated into a `run:` body.
    run_bodies = re.findall(r"^\s*run: \|?\n((?:\s{10,}.*\n)+)", workflow, re.MULTILINE)
    assert run_bodies, "no `run:` body parsed out of the workflow; this check is vacuous"
    for body in run_bodies:
        assert "${{" not in body, (
            "a `run:` body interpolates a `${{ }}` expression. The runner expands that INTO "
            "THE SHELL SOURCE TEXT before bash parses it, on a job holding `contents: "
            "write` — GitHub's documented script-injection anti-pattern (Story 11.3)."
        )
    assert 'python scripts/release_notes.py --tag "$TAG"' in workflow, (
        "the generator is not invoked with the tag bound through `env:` and QUOTED"
    )
    assert "permissions:\n  contents: write\n" in workflow, (
        "release.yml's permission block changed. Adding a permission is a security change, "
        "not a convenience (Story 9.2)."
    )


def test_TC_ArgusAgent_DOCS_001_70_the_generator_never_imports_argus() -> None:
    """TC-ArgusAgent-DOCS-001-70 — Story 12.9 / DN-4: the bare-runner contract holds.

    OBSERVABLE: the generator's own import graph, and whether it runs in an interpreter that
    cannot see ``argus`` at all.

    ``scripts/release_preflight.py`` is stdlib-only because it *"must run on a bare GitHub
    runner before the package (or anything else) is installed"*. The note generator runs in
    the same step-order and inherits the same contract. This is asserted structurally rather
    than by reading the docstring: an ``import argus`` anywhere in the module fails here.
    """
    source = (_REPO_ROOT / _GENERATOR).read_text(encoding="utf-8")
    offenders = re.findall(r"^\s*(?:import|from)\s+(argus[\w.]*)", source, re.MULTILINE)
    assert not offenders, (
        f"{_GENERATOR} imports {offenders} — it must run on a bare runner BEFORE the package "
        "is installed, so importing the thing being released would make the release note "
        "depend on a successful install of it (DN-4)."
    )

    # The alternative route DN-4 permits was NOT taken, and the workflow shows it: the note
    # is generated BEFORE any install step, from the checkout alone.
    # Compared over the INVOCATIONS rather than over the file text: both names also appear in
    # comments, and an ordering assertion that a comment can satisfy is a guard on the wrong
    # observable (12.8 recorded two of those in its own new work).
    workflow = _WORKFLOW.read_text(encoding="utf-8")
    generate_at = workflow.index('python scripts/release_notes.py --tag "$TAG"')
    publish_at = workflow.index('gh release create "$TAG"')
    assert generate_at < publish_at, (
        "the note is generated after the release is created, which is not a note"
    )
    assert "pip install dist/" not in workflow, (
        "the workflow installs the built wheel before rendering the note — that is DN-4's "
        "REJECTED alternative, and it makes the note depend on the install succeeding"
    )


# ─────────────────────────────────────────────────────────────────────────────────────
# Story 12.9 / AC4 — the visibility measurement: ONE dated sentence, on every surface
# that publishes it
# ─────────────────────────────────────────────────────────────────────────────────────

# The surfaces that tell a consumer what it costs them to resolve the documented install
# command. All three used to say some version of *"visibility was NOT measured"*; all three
# now render the one measured sentence, and this is what stops them drifting apart again.
_VISIBILITY_SURFACES: tuple[str, ...] = (
    "README.md",
    "CHANGELOG.md",
    "docs/first-run.md",
)

# The sentences that were measured FALSE-BY-OMISSION and struck. Each must survive on its
# surface, struck rather than deleted (§3.4 evidence immutability): deleting the admission
# that nobody looked would destroy the record that nobody looked.
_STRUCK_VISIBILITY_ADMISSIONS: tuple[tuple[str, str], ...] = (
    ("README.md", "This repository's visibility was not\nmeasured when this line was written"),
    ("CHANGELOG.md", "Visibility was NOT measured when this line was written"),
)


def test_TC_ArgusAgent_DOCS_001_71_the_visibility_measurement_is_dated_and_single_sourced() -> None:
    """TC-ArgusAgent-DOCS-001-71 — Story 12.9 / AC4: measured, dated, and stated in one place.

    OBSERVABLE: whether every surface that tells a consumer what the install costs them
    carries the ONE measurement sentence, verbatim, and whether the superseded *"was NOT
    measured"* admissions survive struck rather than deleted.

    A repository's visibility can change under a document that asserts it, so the sentence is
    written as a **dated measurement with its command** rather than as a standing claim — and
    it is stated once, in ``scripts/release_notes.py``, and rendered onto the surfaces. Three
    hand-written copies of one fact is how ``README.md`` and ``CHANGELOG.md`` came to spend
    two epics both admitting they had never looked.
    """
    statement = rn.REPOSITORY_VISIBILITY_MEASUREMENT
    flat = " ".join(statement.split())

    # The sentence says what AC4 requires it to say: what was measured, on what date, by what
    # command, and what it costs a consumer.
    for required, why in (
        ("2026-08-15", "the date the measurement was taken"),
        ("gh repo view", "the command that took it"),
        ("PRIVATE", "the measured result"),
        ("cannot resolve for anybody", "what it costs a consumer"),
        ("tag or no tag", "that the tag is not the blocker"),
        ("dated measurement, not a standing claim", "that it must be re-checked"),
    ):
        assert required in statement, (
            f"the visibility measurement does not state {required!r} — {why}. An undated "
            "visibility claim is a standing assertion about something that can change under "
            "the document making it."
        )

    checked = 0
    for rel in _VISIBILITY_SURFACES:
        text = " ".join((_REPO_ROOT / rel).read_text(encoding="utf-8").split())
        assert flat in text, (
            f"{rel} does not carry the measured visibility sentence verbatim. Render it from "
            f"`release_notes.REPOSITORY_VISIBILITY_MEASUREMENT`; do not retype it.\n\n{statement}"
        )
        checked += 1
    assert checked == len(_VISIBILITY_SURFACES) >= 3

    # And the release note — the surface a stranger meets on the Release page — carries it too.
    assert statement in _body()
    assert flat in " ".join(_body().split())

    # §3.4: the superseded admissions are struck, not erased.
    for rel, admission in _STRUCK_VISIBILITY_ADMISSIONS:
        text = (_REPO_ROOT / rel).read_text(encoding="utf-8")
        flat_text = " ".join(text.split())
        flat_admission = " ".join(admission.split())
        assert flat_admission in flat_text, (
            f"{rel} DELETED the admission that visibility had never been measured. Striking "
            "it is the correction; deleting it destroys the record that the gap existed "
            "(§3.4 evidence immutability)."
        )
        struck = re.findall(r"~~(?:[^~]|~(?!~))+~~", text, re.DOTALL)
        assert any(flat_admission in " ".join(span.split()) for span in struck), (
            f"{rel} still ASSERTS {admission!r} — it is false and reads as current. Strike it."
        )
