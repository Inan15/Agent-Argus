"""Story 12.1 / AC2 — NFR-M1's ≤1200-line ceiling, swept over the WHOLE tracked tree.

Verification area ArgusAgent-MAINT (``TC-ArgusAgent-MAINT-001-01``..``-05``). A NEW area,
opened here because this is the first guard in the repository whose subject is the
repository's own maintainability standard rather than any product behaviour.

**Why this file exists.** ``architecture.md`` states NFR-M1 — *"Modules: ``snake_case.py``,
≤1200 lines"* — in four places (``:57``, ``:263``, ``:698``, ``:857``), and the repository
enforced it **per-module and ad hoc**: eight test files each assert *"this test file and its
module under test are ≤1200 lines"* (``tests/test_cache_invalidation.py``,
``test_cartridge_selfaudit.py``, ``test_dogfood_module_split.py``, ``test_dogfood_plan.py``,
``test_dogfood_proof.py``, ``test_evidence_bundle.py``, ``test_hitl_escalation.py``,
``test_memo_store.py``). **No assertion anywhere covered ``argus/pipeline.py``**, which is why
it drifted from 1199 (``DF-8-2-A``, which warned *"the next edit of any size breaches
NFR-M1"*) to **1331** across four epics with every gate green. That is this project's dominant
defect class — a rule that is stated, locally asserted, and structurally unable to see the one
place it is broken — so the remedy is a **population**, never another per-module line.

**The population is the contract, never a list.** It is ``git ls-files -- '*.py'``, re-derived
on every run. ``git ls-files`` reports the **INDEX**, not ``HEAD``: a new module is swept the
moment it is ``git add``-ed, before any commit. That is deliberate and is the desirable
direction for *this* guard — you want to know that a module breaches the ceiling while you are
still writing it, not after you push — and it is stated here so the next reader is not
surprised (``DF-10-4-D`` correctly warns that the same property surprises people in
``argus/dogfood/``). A filesystem walk was rejected: it picks up ``.venv/``, ``__pycache__``
and untracked scratch, none of which this standard governs.

**Exemptions are named, dated, reasoned and FILED — and the registry SHRINKS.** Three test
files breach the ceiling today (measured 2026-08-12: 1326 / 1308 / 1203). Splitting three of
this repository's most load-bearing guard files inside a story whose defining criterion is
*behaviour untouched* is a different story with a different risk profile, so they are deferred
**visibly**: each is a named entry with a reason, a date, an owner and a ``deferred-work.md``
id, following the ``_PRESERVED_RECORD`` / ``_EXCLUDED_BY_DESIGN`` precedent
(``tests/test_release_surface_honesty.py:178``, ``tests/test_evidence_citation.py:91``).
Narrowing the population to ``argus/**`` until the sweep went green — the obvious alternative —
is the exact move this repository files as a defect. ``-04`` makes the registry a **shrinking**
allow-list: an entry naming a file that no longer exists, or that is no longer over the cap,
**fails**, so a fixed file cannot leave dead weight behind and the registry cannot become a
parking lot.

**Non-vacuity is mandatory** (five precedents in this repository: ``-39``, ``-118``, ``-51``,
``-99``, ``-122``). A sweep goes green by finding nothing, so ``-01`` refuses an empty or
one-sided enumeration and ``-05`` proves the predicate actually bites by **generating** an
over-cap adversarial variant of **every file in the real population** — a closure over the
tree, with its count asserted, never a hand-listed sample.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACT_DIR = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_DEFERRED_WORK = _ARTIFACT_DIR / "deferred-work.md"

#: NFR-M1's ceiling, stated by ``architecture.md`` at :57, :263, :698 and :857.
_CEILING = 1200

#: The remedy, named in every failure message so it is discoverable from the red output
#: (``DF-8-5-B``'s close condition, applied to this guard's own class).
_REMEDY = (
    "Split the file along a COHESION boundary into a sibling module and re-export, following "
    "the `argus/pipeline_persist.py` (Story 6.3, DN-PIPELINE-SPLIT) and `argus/pipeline_stages.py` "
    "(Story 12.1) precedent — a module docstring naming why the module exists, no function split "
    "across the boundary, `__all__` and every import path unchanged. Do NOT shave lines, and do "
    "NOT narrow this guard's population. If the split genuinely belongs to another story, add a "
    "NAMED exemption to _EXEMPT_BY_DESIGN below carrying a reason, a date, an owner and a "
    "deferred-work.md id — never silence."
)


@dataclass(frozen=True)
class _Exemption:
    """A named, dated, filed exemption. Silence is never an exemption."""

    reason: str
    dated: str
    owner: str
    deferred_work_id: str
    target_story: str


# EXEMPTIONS ARE DATA WITH REASONS (AC2), never a narrowed population. Every entry is checked
# by `-04` for a reason, an ISO date, an owner, a filed ledger id AND for still being LIVE —
# an exemption for a file that is gone or no longer over the cap fails, so this list can only
# shrink. `argus/pipeline.py` is deliberately absent: Story 12.1 fixed it rather than exempting
# it, and `-04` asserts it can never be added here.
_EXEMPT_BY_DESIGN: dict[str, _Exemption] = {
    "tests/test_pipeline_signature_demo.py": _Exemption(
        reason=(
            "1326 lines at 2026-08-12. This file demonstrates the FR32 pipeline signature end to "
            "end over real git fixtures; splitting it is a substantial refactor of a load-bearing "
            "guard file, and Story 12.1's defining criterion is that behaviour is PROVEN "
            "untouched. Deferred visibly rather than fixed under load — the Epic-11 retrospective "
            "measured that this project's defects come from guards written under load."
        ),
        dated="2026-08-12",
        owner="Engineering",
        deferred_work_id="DF-12-1-A",
        target_story="12-2-deep-audit-is-wired-opt-in-and-honest",
    ),
    "tests/test_v1_commitment_closure.py": _Exemption(
        reason=(
            "1308 lines at 2026-08-12. The Story 10.5 delivery-closure guard: two static closures "
            "over prd.md and the argus/** import graph. Same reason as above — a restructuring "
            "story must not refactor the guard that would notice if it broke something. "
            "RE-MEASURED 2026-08-15: 1685 lines, and the growth is recorded rather than left to be "
            "discovered. Every story since has had to amend a disposition REASON in the reverse "
            "registry — that is the file's design, since a disposition without a reason is a label "
            "— and 12.6 added the largest single one (FR35's, which had to state both what was "
            "delivered and the 12.7 half that was not, or the entry would over-claim the FR). The "
            "exemption still holds for its original reason and the split is still owed; the honest "
            "note is that this file grows with every epic and the eventual split is the registries "
            "moving to their own module, not the closures being rewritten."
        ),
        dated="2026-08-12",
        owner="Engineering",
        deferred_work_id="DF-12-1-B",
        target_story="12-3-a-re-run-returns-the-recorded-result",
    ),
    "tests/test_grammar_diagnosis.py": _Exemption(
        reason=(
            "1203 lines at 2026-08-12 — three lines over. The Story 10.4 grammar-diagnosis guard, "
            "including the `ast` closure over the loader's control flow. Same reason as above. "
            "RE-RECORDED 2026-08-15 by Story 12.8, because the entry had become ORPHANED and an "
            "exemption nobody owns is a hole rather than a decision: its target story "
            "`12-5-default-install-grounds-languages-it-claims` is `done` and did not perform the "
            "split, so the clause that was meant to retire this entry can never fire. Story 12.8 "
            "needed a CLI-level grammar-downgrade guard and DECLINED to add it here — it is homed "
            "in `tests/test_cli.py` beside the other operator-diagnosis guards, which is also "
            "where it cohesively belongs — so this file is UNCHANGED at 1203 lines and the "
            "exemption did not grow. It is still owed: the split is a mechanical one (the four "
            "simulated failure modes and their seam installer are a self-contained half), and it "
            "belongs to a story that says so rather than to whichever story next needs a line."
        ),
        dated="2026-08-15",
        owner="Engineering",
        deferred_work_id="DF-12-1-C",
        target_story="NONE — unscheduled; the split is owed and belongs to a story that says so",
    ),
}

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _tracked_python_files() -> tuple[str, ...]:
    """The population: every tracked ``.py`` path, from git, NUL-separated and unquoted.

    ``-z`` is used so a non-ASCII path round-trips regardless of ``core.quotepath`` (the
    Story 1.4 precedent already relied on by ``argus/dogfood/partition_plan.py``).
    """
    done = subprocess.run(
        ["git", "-C", str(_REPO_ROOT), "ls-files", "-z", "--", "*.py"],
        capture_output=True,
        timeout=60,
    )
    assert done.returncode == 0, (
        "`git ls-files -z -- '*.py'` failed "
        f"(exit {done.returncode}): {done.stderr.decode('utf-8', 'replace').strip()!r} — "
        "the population could not be enumerated, so this guard would otherwise pass VACUOUSLY"
    )
    return tuple(sorted(p for p in done.stdout.decode("utf-8", "replace").split("\0") if p))


def _physical_line_count(text: str) -> int:
    """Physical lines, matching the per-module NFR-M1 assertions already in this repository.

    ``len(text.splitlines())`` is what ``tests/test_dogfood_plan.py:485`` and its seven siblings
    use. It equals ``wc -l`` for a file ending in a newline and is ``wc -l + 1`` for one that
    does not — i.e. it never UNDER-counts, so it cannot let a breach through.
    """
    return len(text.splitlines())


def _breaches_ceiling(text: str) -> bool:
    """THE predicate. Every assertion below drives this one function — no second derivation."""
    return _physical_line_count(text) > _CEILING


def _measure_population() -> dict[str, int]:
    """Line count for every enumerated path that exists on disk."""
    measured: dict[str, int] = {}
    for rel in _tracked_python_files():
        path = _REPO_ROOT / rel
        if not path.is_file():
            continue
        measured[rel] = _physical_line_count(path.read_text(encoding="utf-8"))
    return measured


def test_TC_ArgusAgent_MAINT_001_01_the_swept_population_is_real_and_two_sided() -> None:
    """TC-ArgusAgent-MAINT-001-01 — AC2 non-vacuity: a broken glob turns this RED, not green.

    Driver: ``git ls-files -z -- '*.py'``. A sweep that enumerates nothing passes trivially,
    which is the failure mode this whole story exists to close — so the enumeration itself is
    asserted: non-empty, covering BOTH trees the standard governs, every member ending in
    ``.py``, and every member present on disk (a path in the index that is not on disk would
    be silently skipped by the measurement below).
    """
    population = _tracked_python_files()
    assert population, (
        "`git ls-files -- '*.py'` enumerated NOTHING — the population is empty and every "
        "assertion in this file would be vacuous"
    )
    assert len(population) >= 100, (
        f"the tracked Python population collapsed to {len(population)} files; it was 169 when "
        "this guard was written (2026-08-12). A glob or a `cwd` regression is far more likely "
        "than the repository losing two thirds of its modules"
    )
    assert all(p.endswith(".py") for p in population), (
        "the pathspec leaked a non-Python path into the population"
    )

    argus_files = [p for p in population if p.startswith("argus/")]
    test_files = [p for p in population if p.startswith("tests/")]
    assert len(argus_files) >= 50, (
        f"only {len(argus_files)} `argus/**` files swept (72 at 2026-08-12) — the population is "
        "one-sided and NFR-M1 would go unenforced over the product"
    )
    assert len(test_files) >= 50, (
        f"only {len(test_files)} `tests/**` files swept — the population is one-sided. Test files "
        "are unambiguously in scope: this repository's own per-module NFR-M1 assertions say "
        "'this test file is <= 1200 lines' file by file"
    )

    missing = sorted(p for p in population if not (_REPO_ROOT / p).is_file())
    assert not missing, (
        f"tracked path(s) enumerated but absent from the working tree: {missing}. They would be "
        "skipped by the sweep, so the population would silently narrow"
    )


def test_TC_ArgusAgent_MAINT_001_02_every_tracked_python_file_is_under_the_nfr_m1_ceiling() -> None:
    """TC-ArgusAgent-MAINT-001-02 — AC2/NFR-M1: THE sweep. No tracked ``.py`` over 1200 lines.

    Driver: ``_breaches_ceiling`` over ``_measure_population()``. This is the assertion that
    did not exist while ``argus/pipeline.py`` drifted 131 lines past the cap with every gate
    green. Exempt files are named in ``_EXEMPT_BY_DESIGN`` and audited by ``-04``.
    """
    measured = _measure_population()
    assert measured, "nothing was measured — see -01"

    breaching = {
        rel: n
        for rel, n in sorted(measured.items())
        if n > _CEILING and rel not in _EXEMPT_BY_DESIGN
    }
    assert not breaching, (
        "NFR-M1 breach — file(s) over the "
        f"{_CEILING}-line ceiling: "
        + ", ".join(f"{rel} ({n} lines, {n - _CEILING} over)" for rel, n in breaching.items())
        + ". "
        + _REMEDY
    )


def test_TC_ArgusAgent_MAINT_001_03_the_ceiling_boundary_is_pinned_in_both_directions() -> None:
    """TC-ArgusAgent-MAINT-001-03 — AC2: exactly 1200 passes, 1201 fails, through the predicate.

    Driver: synthesized content of an exact length, run through ``_breaches_ceiling`` itself —
    the same function the sweep uses, so an off-by-one introduced there is caught here rather
    than in six months by a file that squeaked through at 1201.
    """
    def synth(n: int) -> str:
        return "".join(f"# line {i}\n" for i in range(n))

    for n in (0, 1, 1199, _CEILING):
        text = synth(n)
        assert _physical_line_count(text) == n
        assert not _breaches_ceiling(text), f"{n} lines must NOT breach a ceiling of {_CEILING}"

    for n in (_CEILING + 1, _CEILING + 2, _CEILING + 131):
        text = synth(n)
        assert _physical_line_count(text) == n
        assert _breaches_ceiling(text), f"{n} lines MUST breach a ceiling of {_CEILING}"

    # A file whose final line carries no newline still counts as a line (never under-counts).
    no_trailing_newline = synth(_CEILING) + "# line 1200"
    assert _physical_line_count(no_trailing_newline) == _CEILING + 1
    assert _breaches_ceiling(no_trailing_newline)


def test_TC_ArgusAgent_MAINT_001_04_the_exemption_registry_is_reasoned_filed_and_shrinking() -> None:
    """TC-ArgusAgent-MAINT-001-04 — AC2: an exemption is a dated decision with an owner, and it expires.

    Driver: the registry itself, cross-checked against the measured population and against
    ``deferred-work.md``. Three properties, each of which has failed in this repository before:
    (a) an exemption without a written reason is an oversight wearing a decision's clothes
    (the ``_PRESERVED_RECORD`` anti-pattern); (b) an exemption that outlives the breach it
    excused is dead weight that quietly widens the guard; (c) an exemption that was never filed
    has no owner and no date by which anyone will look at it again.
    """
    measured = _measure_population()
    ledger = _DEFERRED_WORK.read_text(encoding="utf-8")

    assert "argus/pipeline.py" not in _EXEMPT_BY_DESIGN, (
        "argus/pipeline.py must NEVER be exempted — Story 12.1 exists because it breached this "
        "ceiling, and exempting it would close the story by deleting its subject"
    )

    for rel, exemption in sorted(_EXEMPT_BY_DESIGN.items()):
        assert rel in measured, (
            f"exemption for {rel!r} names a file that is no longer tracked or no longer exists. "
            "Delete the exemption — a registry entry the population cannot see proves nothing"
        )
        assert measured[rel] > _CEILING, (
            f"exemption for {rel!r} is DEAD: the file is now {measured[rel]} lines, at or under "
            f"the {_CEILING}-line ceiling. Remove it from _EXEMPT_BY_DESIGN — this registry "
            "shrinks, it is not a parking lot"
        )
        assert len(exemption.reason) >= 80, (
            f"exemption for {rel!r} carries no substantive reason ({len(exemption.reason)} chars)"
        )
        assert _ISO_DATE.match(exemption.dated), (
            f"exemption for {rel!r} carries no ISO date: {exemption.dated!r}"
        )
        assert exemption.owner.strip(), f"exemption for {rel!r} names no owner"
        assert exemption.target_story.strip(), f"exemption for {rel!r} names no target story"
        assert exemption.deferred_work_id in ledger, (
            f"exemption for {rel!r} cites {exemption.deferred_work_id!r}, which is not filed in "
            f"{_DEFERRED_WORK.name}. An exemption that is not filed has no owner and no date by "
            "which anyone looks at it again (AI-E11-10's alternative DoD)"
        )
        assert exemption.target_story in ledger, (
            f"exemption for {rel!r} names target story {exemption.target_story!r}, which does not "
            f"appear in {_DEFERRED_WORK.name} — the ledger entry must carry the same target"
        )


def test_TC_ArgusAgent_MAINT_001_05_the_predicate_bites_on_every_file_in_the_real_population() -> None:
    """TC-ArgusAgent-MAINT-001-05 — AC2 non-vacuity: adversarial variants GENERATED from the tree.

    Driver: every member of the live population, each mutated two ways. A guard that goes green
    by finding nothing must be shown to be capable of finding something, and the adversarial
    set is **generated from the structure the guard closes over** rather than hand-listed —
    ``AI-E10-5``, *the list is never the contract*. For each real file: pad its real content
    past the ceiling and require the predicate to flag it; trim a copy to exactly the ceiling
    and require it not to be flagged. The count is asserted, so a population that quietly
    stopped being enumerated cannot make this pass by iterating zero times.
    """
    population = _tracked_python_files()
    flagged = 0
    cleared = 0

    for rel in population:
        path = _REPO_ROOT / rel
        if not path.is_file():
            continue
        real = path.read_text(encoding="utf-8")
        lines = real.splitlines()

        over = "\n".join(lines + ["# adversarial pad"] * (_CEILING + 1 - len(lines))) if len(
            lines
        ) <= _CEILING else real
        assert _breaches_ceiling(over), (
            f"the predicate did NOT flag an over-ceiling variant of {rel!r} "
            f"({_physical_line_count(over)} lines) — it is structurally incapable of seeing the "
            "defect it claims to guard"
        )
        flagged += 1

        at_cap = "\n".join((lines + ["# pad"] * _CEILING)[:_CEILING])
        assert not _breaches_ceiling(at_cap), (
            f"the predicate flagged a variant of {rel!r} at exactly {_CEILING} lines — the "
            "ceiling is inclusive and a correct file must not be accused"
        )
        cleared += 1

    assert flagged >= 150, (
        f"only {flagged} adversarial over-ceiling variants were generated (169 files tracked at "
        "2026-08-12) — the closure ran over almost nothing and proves almost nothing"
    )
    assert cleared == flagged, "every generated pair must exercise both directions"


def test_TC_ArgusAgent_DOCS_001_59_both_story_12_1_rules_are_registered_in_the_architecture() -> None:
    """TC-ArgusAgent-DOCS-001-59 — AC2/AC3: the enforcements are registered, and the FALSE claim is gone.

    The ``-23`` / ``-41`` / ``-52`` / ``-53`` / ``-55`` pattern: §Enforcement must carry each rule's
    text and name its enforcing module and ids, so an enforcement cannot be deleted from the
    architecture while the tests quietly survive, or vice versa.

    **Plus a half those siblings did not need.** `architecture.md` §Enforcement claimed NFR-M1 was
    *"enforced by … file-size CI — committed under `tests/apaa/`"*. Measured 2026-08-12:
    `tests/apaa/` does not exist and no workflow contains a file-size step — the architecture
    asserted a guard that had **never been built**, and `argus/pipeline.py` drifted 131 lines past
    the cap under that false assurance. **An architecture that claims an enforcement it does not
    have is the same defect class this story closes**, so the false sentence must not survive the
    story that makes the claim true — and this assertion is what stops it being restored.
    """
    architecture = (_ARTIFACT_DIR / "architecture.md").read_text(encoding="utf-8")
    assert "### Enforcement" in architecture, (
        "architecture.md has no §Enforcement section — every registration assertion in this "
        "repository is vacuous"
    )

    for anchor in (
        # The NFR-M1 sweep (AC2).
        "Module-size enforcement",
        "tests/test_module_size_ceiling.py",
        "TC-ArgusAgent-MAINT-001-01",
        "holds over EVERY tracked `.py` file",
        "never a narrowed population and never silence",
        # The artifact-currency guard (AC3).
        "Dogfood-artifact currency enforcement",
        "tests/test_dogfood_artifact_currency.py",
        "TC-ArgusAgent-DOGFOOD-001-49",
        "may not describe a tree that no longer exists",
        "scripts/regenerate_dogfood_artifacts.py",
        # This assertion's own id, so the registration names what holds it.
        "TC-ArgusAgent-DOCS-001-59",
    ):
        assert anchor in architecture, (
            f"architecture.md §Enforcement is missing the Story 12.1 registration anchor {anchor!r}"
        )

    false_claim = "committed under `tests/apaa/`"
    occurrences = [
        line for line in architecture.splitlines() if false_claim in line
    ]
    assert occurrences, (
        "architecture.md no longer QUOTES the corrected false claim anywhere. The correction is "
        "the record of what was wrong and why; deleting the quotation deletes the lesson, and the "
        "next reader has no way to know the enforcement was once asserted and never built."
    )
    asserted_live = [line for line in occurrences if not line.lstrip().startswith(">")]
    assert not asserted_live, (
        "architecture.md ASSERTS, outside the correction blockquote, that NFR-M1 is enforced by "
        f"file-size CI {false_claim}: {asserted_live}. That directory does not exist, no workflow "
        "contains a file-size step, and `argus/pipeline.py` drifted 131 lines past the cap under "
        "exactly that false assurance. The enforcement is `tests/test_module_size_ceiling.py`. "
        "A quotation inside the `>` correction block is the only permitted occurrence."
    )
    assert not (_REPO_ROOT / "tests" / "apaa").exists(), (
        "`tests/apaa/` now exists, so the assertion above is guarding a premise that has changed. "
        "Re-measure and amend the architecture deliberately rather than deleting this check."
    )
