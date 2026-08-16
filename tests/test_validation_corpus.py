"""Story 13.1 — the VALIDATION SET: what it is, and that its figures are MEASURED.

Verification areas ``TC-ArgusAgent-PRECISION-001-21``..``-29`` (the manifest — continuing the
6.6 precision area, since the validation set IS the precision gate's substrate) and
``TC-ArgusAgent-DOGFOOD-001-53``..``-55`` (AC5 — the published figure is DERIVED). **No new
area is opened**; both populations already exist and the story's §Testing forbids opening one
for convenience.

**What this file guards, in one sentence.** Story 13.1 decided that the **PRD governs** the
≥80%-precision gate — the validation set is *N ≈ 5–10 real repositories*, not the planted-defect
cartridges — so the corpus needs one named place that says who is in it (AC3a), a schema that
cannot quietly grow a usage field (AC4), a floor that is derived rather than transcribed (DN-3),
and a published gate figure that is a measurement rather than a literal (AC5 / ``DF-8-5-C``).

**Why the manifest and the cartridge registry are separate tables (DN-2).** They measure
different quantities. The cartridges measure **recall** against defects the team planted and
whose answers the team wrote; the repository corpus measures **precision** on code nobody
planted. Fusing them into one table would let a clean-control cartridge enter the precision
denominator, which is the "measure your own homework" failure Epic 13 exists to remove. So
``-24`` asserts no cartridge id is a manifest member, in both directions.

**Non-vacuity is mandatory** (the ``-39`` / ``-118`` / ``-05`` precedent). A manifest guard that
iterates an empty tuple passes forever — and the manifest legitimately holds **zero eligible
members** today, which is exactly the state in which a careless guard is silent. So ``-21``
refuses an empty manifest, every closure below asserts the row count it actually examined, and
``-27`` generates its adversarial variants **from the real members** rather than hand-writing
them (``AI-E10-5``: the list is never the contract).

**Network-free by construction** (DN-5). Nothing here fetches a repository. ``-28`` proves that
structurally with an ``ast`` closure over the manifest module rather than by assertion, because
"the suite must not reach the network" is the kind of rule that decays into a comment.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import FrozenInstanceError, fields, replace
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent / "corpus"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))

from _manifest import (  # noqa: E402
    AST_INELIGIBLE_LANGUAGES,
    MANIFEST_FIELDS,
    NEVER_ELIGIBLE_FIELDS,
    PROVENANCE_VALUES,
    SOURCING_RULE,
    VALIDATION_CORPUS,
    CorpusMemberSpec,
    UnregisteredCorpusMember,
    eligible_member_count,
    eligible_members,
    meets_validation_floor,
    member,
    validation_floor_n,
    validation_set_status,
)
from _registry import CARTRIDGE_REGISTRY, VALIDATION_SET_FLOOR_N  # noqa: E402

from argus.dogfood.proof_run import derive_gate_status  # noqa: E402
from argus.precision.replay_harness import (  # noqa: E402
    measure_validation_corpus,
    precision_gate_status_for,
)

_MANIFEST_SOURCE = _REPO_ROOT / "tests" / "corpus" / "_manifest.py"
_PROOF_ARTIFACT = (
    _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent" / "minions-dogfood-proof.md"
)
_PROOF_RUN_SOURCE = _REPO_ROOT / "argus" / "dogfood" / "proof_run.py"


# ─────────────────────────────────────────────────────────────────────────────────────
# AC3a — the manifest is the one named place a corpus member exists
# ─────────────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PRECISION_001_21_the_manifest_is_populated_and_every_row_is_complete() -> None:
    """TC-ArgusAgent-PRECISION-001-21 — AC3a: membership is declared, with the fields that decide it.

    Driver: ``VALIDATION_CORPUS`` itself. Every member carries repository URL, pinned commit
    sha, licence, primary language, provenance and ``eligible_for_n`` — the AC3a minimum. A
    member that is not in this tuple is not in N, so the tuple being non-empty is the
    precondition for every other assertion in this file meaning anything.
    """
    assert VALIDATION_CORPUS, (
        "the validation-set manifest is EMPTY. Every closure in this file would iterate zero "
        "rows and pass vacuously — which is precisely the state the corpus is in today "
        "(zero ELIGIBLE members), so the manifest must still record the members it excludes "
        "and why. An empty manifest is not the same fact as an empty eligible set."
    )

    examined = 0
    for spec in VALIDATION_CORPUS:
        assert spec.member_id.strip(), "a manifest member carries no id"
        assert spec.repository_url.strip(), f"{spec.member_id}: no repository URL"
        assert spec.commit_sha.strip(), f"{spec.member_id}: no pinned commit sha"
        assert spec.licence.strip(), f"{spec.member_id}: no licence recorded"
        assert spec.primary_language.strip(), f"{spec.member_id}: no primary language"
        assert spec.provenance in PROVENANCE_VALUES, (
            f"{spec.member_id}: provenance {spec.provenance!r} is not one of {PROVENANCE_VALUES}"
        )
        assert isinstance(spec.eligible_for_n, bool)
        examined += 1

    assert examined == len(VALIDATION_CORPUS) >= 2, (
        f"only {examined} manifest rows examined; the three recorded exclusions of AC3a require "
        "at least the Argus self-audit and the superseded Minions run to be present as members"
    )

    ids = [spec.member_id for spec in VALIDATION_CORPUS]
    assert len(ids) == len(set(ids)), f"duplicate member ids in the manifest: {sorted(ids)}"


def test_TC_ArgusAgent_PRECISION_001_22_the_schema_is_CLOSED_and_usage_can_never_be_a_field() -> None:
    """TC-ArgusAgent-PRECISION-001-22 — AC4: "usage is not evidence", enforced in the schema.

    Driver: ``dataclasses.fields(CorpusMemberSpec)`` against the declared ``MANIFEST_FIELDS``,
    in BOTH directions. The PRD's guard is that *"adoption cannot advance the precision gate,
    only adjudicated findings can"* — a rule that is easy to restate and easy to erode one
    convenient field at a time. Adding ``stars`` to the row would not break a single existing
    test; it breaks this one, because the schema is an enumerated space rather than whatever
    the dataclass happens to hold.

    The adversarial half is GENERATED from ``NEVER_ELIGIBLE_FIELDS`` rather than hand-written,
    so a new usage-shaped field name is covered by adding it to the registry the rule owns.
    """
    actual = {f.name for f in fields(CorpusMemberSpec)}
    assert actual == set(MANIFEST_FIELDS), (
        "the manifest schema drifted from its declared closure. "
        f"dataclass-only={sorted(actual - set(MANIFEST_FIELDS))} "
        f"declared-only={sorted(set(MANIFEST_FIELDS) - actual)}. A field added to the row "
        "without being added to MANIFEST_FIELDS is a silent extension of the corpus contract."
    )

    assert NEVER_ELIGIBLE_FIELDS, "the never-eligible field registry is empty — see AC4"
    forbidden = actual & set(NEVER_ELIGIBLE_FIELDS)
    assert not forbidden, (
        f"the manifest row carries usage-shaped field(s) {sorted(forbidden)}. PRD:159 — "
        "'usage is not evidence: adoption cannot advance the precision gate, only adjudicated "
        "findings can'. A member is SOURCED from anywhere, including public users; it counts "
        "toward N only once its findings are adjudicated by a named human (Story 13.2)."
    )

    # The rule is written down where a reader will find it, not only enforced here.
    assert len(SOURCING_RULE.split()) >= 25, (
        "SOURCING_RULE carries no substantive text. AC4 requires the sourcing rule to be "
        "RECORDED, not merely obeyed (the _EXCLUDED_BY_DESIGN precedent)."
    )
    assert "adjudicat" in SOURCING_RULE.lower(), (
        "the sourcing rule must state that adjudication, not sourcing, is what admits a member"
    )


def test_TC_ArgusAgent_PRECISION_001_23_an_unregistered_member_RAISES() -> None:
    """TC-ArgusAgent-PRECISION-001-23 — AC4: the DF-10-4-E exhaustive-dispatch shape.

    Driver: ``member()`` over the real ids and over ids that are not in the manifest. An
    unregistered member must RAISE and name itself — never return ``None``, never fall back to
    a default row. This is the same shape 12.5's ``_downgrade_sentence`` and 12.8/AC4 take, and
    it is the reason a corpus member cannot be conjured at a call site: the manifest is the one
    named place, so "not in the manifest" has to be an error rather than an absence.
    """
    resolved = 0
    for spec in VALIDATION_CORPUS:
        assert member(spec.member_id) is spec
        resolved += 1
    assert resolved == len(VALIDATION_CORPUS) >= 2, "the resolution closure ran over too few rows"

    for absent in ("", "not-a-member", "argus", "minions", "vacuous_basic"):
        with pytest.raises(UnregisteredCorpusMember) as excinfo:
            member(absent)
        assert absent in str(excinfo.value) or not absent, (
            "the raise must name the id that was not registered, so the failure is actionable"
        )


def test_TC_ArgusAgent_PRECISION_001_24_the_three_exclusions_live_IN_the_manifest_with_reasons() -> None:
    """TC-ArgusAgent-PRECISION-001-24 — AC3a: the exclusions are data, not prose elsewhere.

    Driver: the manifest rows. AC3a names three exclusions and requires each to be recorded in
    the manifest itself: the **Argus self-audit** (self-authored), the **superseded Minions
    run** (not re-derivable in this repository), and the **cartridges** — which are excluded by
    being a different corpus entirely rather than by being a row flagged ``False``.

    The cartridge half is asserted in BOTH directions, because "they are not members" is a
    claim about two tables at once: no manifest id may be a cartridge id, and no cartridge id
    may be a manifest id. A single-direction check would still pass if someone added
    ``clean_control`` to the manifest under a different member id.
    """
    by_id = {spec.member_id: spec for spec in VALIDATION_CORPUS}

    self_audit = [s for s in VALIDATION_CORPUS if s.provenance == "self"]
    assert self_audit, (
        "the Argus self-audit is not recorded in the manifest. Story 8.5 re-derived the dogfood "
        "as a self-audit of `argus/`; leaving it unrecorded is how it quietly became 'the "
        "corpus' in the first place"
    )
    superseded = [s for s in VALIDATION_CORPUS if s.provenance == "superseded"]
    assert superseded, (
        "the superseded Minions run is not recorded. deferred-work.md:832-836 states it 'can "
        "never be re-derived in this repository' — an exclusion that is only in the ledger is "
        "not in the one named place"
    )

    for spec in (*self_audit, *superseded):
        assert spec.eligible_for_n is False, (
            f"{spec.member_id}: provenance {spec.provenance!r} can never be eligible for N"
        )
        assert spec.ineligible_reason and len(spec.ineligible_reason.split()) >= 8, (
            f"{spec.member_id}: excluded with no substantive reason. An exclusion without a "
            "reason is an oversight wearing a decision's clothes (_PRESERVED_RECORD precedent)"
        )

    cartridge_ids = {spec.cartridge_id for spec in CARTRIDGE_REGISTRY}
    assert cartridge_ids, "the cartridge registry is empty — this direction would be vacuous"
    overlap = cartridge_ids & set(by_id)
    assert not overlap, (
        f"cartridge id(s) {sorted(overlap)} appear as validation-set members. DN-2: the "
        "cartridges measure RECALL against planted defects the team authored; the validation "
        "set measures PRECISION on unplanted code. One table for both would let a clean-control "
        "cartridge enter the precision denominator."
    )
    for spec in VALIDATION_CORPUS:
        assert spec.member_id not in cartridge_ids


def test_TC_ArgusAgent_PRECISION_001_25_the_floor_is_DERIVED_and_there_is_only_ONE_of_it() -> None:
    """TC-ArgusAgent-PRECISION-001-25 — AC3a/DN-3: one floor constant, two populations.

    Driver: ``validation_floor_n()`` against the 6.5 ``VALIDATION_SET_FLOOR_N``, plus a static
    read of the manifest source. Two floors is how two corpora happened in the first place, so
    the manifest resolves the existing constant rather than restating ``5``. ``AI-E9-7``: never
    publish a prose copy of a pinned constant.

    The count is DERIVED too — ``eligible_member_count()`` folds the rows; nobody transcribes
    it. Today it is **0**, and the floor is NOT met; that is the honest state this story hands
    to 13.2, and asserting it here means a fabricated member cannot slip in unnoticed.
    """
    assert validation_floor_n() == VALIDATION_SET_FLOOR_N == 5, (
        "the manifest's floor and the cartridge registry's floor disagree, or the locked OI1 "
        "floor moved. N is LOCKED at 5 (protocol §7); a corpus that is hard to build is a fact "
        "to record, never a reason to move a number"
    )

    # Read as CODE, not as text: the module legitimately NAMES the 6.5 constant in its prose
    # when it explains DN-3, and a substring check would fail on the explanation rather than on
    # the defect. What DN-3 forbids is a second BINDING.
    manifest_tree = ast.parse(_MANIFEST_SOURCE.read_text(encoding="utf-8"))
    bound: list[str] = []
    for node in manifest_tree.body:
        if isinstance(node, ast.Assign):
            bound.extend(t.id for t in node.targets if isinstance(t, ast.Name))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            bound.append(node.target.id)
    forked = [name for name in bound if name.endswith("FLOOR_N")]
    assert not forked, (
        f"the manifest binds its own floor constant(s) {forked}. DN-3: one floor, two "
        "populations — resolve the 6.5 constant through validation_floor_n(), never fork it. "
        "Two floors is how two corpora happened in the first place."
    )

    derived = eligible_member_count()
    assert derived == len(eligible_members()) == len(
        [s for s in VALIDATION_CORPUS if s.eligible_for_n]
    ), "eligible_member_count() disagrees with a direct fold over the manifest"
    assert derived == 0, (
        f"the manifest reports {derived} ELIGIBLE members. If AC3b has genuinely been ratified "
        "and populated, update this assertion DELIBERATELY in the story that did it — do not "
        "loosen it. A member appearing here without an operator ratification is a fabricated "
        "corpus in the story that defines the corpus."
    )
    assert meets_validation_floor() is False, (
        "the validation floor reports MET at zero eligible members — the gate's whole premise"
    )

    status = validation_set_status()
    assert str(derived) in status and str(VALIDATION_SET_FLOOR_N) in status, (
        "the derived status string must carry both the measured count and the floor"
    )
    assert "cleared" not in status.split("NOT")[0].lower(), (
        "the validation-set status must never lead with a cleared claim"
    )


def test_TC_ArgusAgent_PRECISION_001_26_eligibility_refuses_every_shape_that_would_fake_N() -> None:
    """TC-ArgusAgent-PRECISION-001-26 — AC3a/AC4/DN-6: the row validates itself, at construction.

    Driver: ``CorpusMemberSpec.__post_init__``. Four ways a corpus could be quietly faked, each
    refused where the row is BUILT rather than where it is read — a validator that only runs in
    a test is a validator the next call site can skip:

    (a) an INELIGIBLE member with no reason (the exclusion-without-a-reason class);
    (b) an ELIGIBLE member whose provenance is not ``independent`` — the self-audit and the
        superseded run cannot be promoted by editing one boolean;
    (c) an ELIGIBLE member with no pinned 40-hex commit sha (DN-4: pinned and fetched, never
        vendored — an unpinned member is not reproducible and cannot be adjudicated);
    (d) an ELIGIBLE member whose ``primary_language`` cannot support ``audited_deep``
        (``DF-10-2-A`` / DN-6: C, C++, Ruby and Rust ground cleanly and extract ZERO
        definitions, so no file in them can reach the depth the gate is about).
    """
    good = dict(
        member_id="example-independent",
        repository_url="https://example.invalid/org/repo",
        commit_sha="0" * 40,
        licence="MIT",
        primary_language="python",
        provenance="independent",
        eligible_for_n=True,
        ineligible_reason=None,
    )
    CorpusMemberSpec(**good)  # the control: this shape is legal

    with pytest.raises(ValueError, match="reason"):
        CorpusMemberSpec(**{**good, "eligible_for_n": False, "ineligible_reason": None})

    for provenance in ("self", "superseded"):
        with pytest.raises(ValueError, match="independent"):
            CorpusMemberSpec(**{**good, "provenance": provenance})

    with pytest.raises(ValueError, match="unregistered provenance"):
        CorpusMemberSpec(**{**good, "provenance": "vendored"})

    for sha in ("", "abc123", "z" * 40, "0" * 39):
        with pytest.raises(ValueError, match="sha"):
            CorpusMemberSpec(**{**good, "commit_sha": sha})

    assert AST_INELIGIBLE_LANGUAGES, "the DN-6 ineligible-language set is empty"
    for language in sorted(AST_INELIGIBLE_LANGUAGES):
        with pytest.raises(ValueError, match="audited_deep"):
            CorpusMemberSpec(**{**good, "primary_language": language})

    with pytest.raises(ValueError, match="unregistered language"):
        CorpusMemberSpec(**{**good, "primary_language": "cobol"})

    # The row is frozen: a member cannot be promoted after the manifest is built.
    spec = CorpusMemberSpec(**good)
    with pytest.raises(FrozenInstanceError):
        spec.eligible_for_n = False  # type: ignore[misc]


def test_TC_ArgusAgent_PRECISION_001_27_adversarial_variants_are_GENERATED_from_the_real_members() -> None:
    """TC-ArgusAgent-PRECISION-001-27 — AI-E11-1 clause (iii): the variants come from the registry.

    Driver: every real member of ``VALIDATION_CORPUS``, mutated with ``dataclasses.replace``.
    ``-26`` proves the validator bites on a synthetic row; this proves it bites on **the rows
    that actually exist**, which is the difference between a guard that closes over a
    hand-written sample and one that closes over the population (``AI-E10-5``).

    For each ineligible member the story's own RED recipe is generated twice: strip its reason,
    and promote it to eligible. Both must raise. The count is asserted, so a manifest that
    stopped being enumerated cannot make this pass by iterating zero times.
    """
    generated = 0
    for spec in VALIDATION_CORPUS:
        if spec.eligible_for_n:
            # A real eligible member: demoting it without a reason must raise.
            with pytest.raises(ValueError, match="reason"):
                replace(spec, eligible_for_n=False, ineligible_reason=None)
            generated += 1
            continue

        with pytest.raises(ValueError, match="reason"):
            replace(spec, ineligible_reason=None)
        generated += 1

        with pytest.raises(ValueError, match="independent"):
            replace(spec, eligible_for_n=True, ineligible_reason=None)
        generated += 1

    assert generated >= 2 * len(VALIDATION_CORPUS) >= 4, (
        f"only {generated} adversarial variants were generated from {len(VALIDATION_CORPUS)} "
        "real members — the closure ran over almost nothing and proves almost nothing"
    )


def test_TC_ArgusAgent_PRECISION_001_28_the_manifest_reaches_no_network_and_vendors_no_source() -> None:
    """TC-ArgusAgent-PRECISION-001-28 — DN-5/DN-4/NFR-S1: proven structurally, not promised.

    Driver: an ``ast`` closure over the manifest module, plus a walk of its directory. DN-5
    says the guards over the corpus are network-free and assert the manifest and the
    derivation — never a live fetch — and DN-4 says a member is pinned and fetched, **never
    vendored**. Both are the kind of rule that decays into a comment, so:

    (a) the module imports nothing that can open a socket or spawn a fetch;
    (b) ``tests/corpus/`` contains no third-party source file — metadata and locators only
        (NFR-S1: no third-party source byte is committed).
    """
    tree = ast.parse(_MANIFEST_SOURCE.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])

    assert imported, "the ast walk found no imports at all — the closure is broken, not clean"
    networked = imported & {
        "socket", "http", "urllib", "urllib2", "requests", "httpx", "ftplib",
        "telnetlib", "smtplib", "asyncio", "subprocess", "aiohttp",
    }
    assert not networked, (
        f"the validation-set manifest imports {sorted(networked)}. DN-5: the guards assert the "
        "MANIFEST and the DERIVATION; staging a corpus is an operator act behind the AC3b "
        "escalation, never something a test run performs. A suite that fetches is a suite that "
        "fails differently on a machine with no network."
    )

    corpus_dir = _MANIFEST_SOURCE.parent
    stray = sorted(
        p.name
        for p in corpus_dir.rglob("*")
        if p.is_file() and p.suffix not in (".py", ".md") and "__pycache__" not in p.parts
    )
    assert not stray, (
        f"third-party-looking file(s) in tests/corpus/: {stray}. DN-4 pins and fetches; it "
        "never vendors. No third-party source byte is committed (NFR-S1)."
    )


def test_TC_ArgusAgent_PRECISION_001_29_the_manifest_is_repository_only_like_the_cartridges() -> None:
    """TC-ArgusAgent-PRECISION-001-29 — DF-9-2-A: the manifest must not ship in the wheel.

    Driver: the packaging surface. ``tests/cartridges/`` is repository-only and absent from the
    built distribution, which is why ``replay_harness`` resolves the registry through a lazy
    edge rather than a module-level import. The manifest lives under ``tests/`` for the same
    reason and inherits the same treatment — so this asserts the two facts that make the lazy
    edge necessary AND sufficient: the manifest is under ``tests/``, and no shipped ``argus/**``
    module imports it at module level.

    A module-level import from ``argus/`` would ship a wheel that cannot import, and
    ``tests/test_built_distribution.py`` ``-20`` is the guard that would catch it — after the
    fact. This catches it at the seam.
    """
    assert _MANIFEST_SOURCE.is_relative_to(_REPO_ROOT / "tests"), (
        "the manifest moved out of tests/; it would then ship in the wheel (DF-9-2-A)"
    )

    argus_modules = sorted(
        p for p in (_REPO_ROOT / "argus").rglob("*.py") if "__pycache__" not in p.parts
    )
    assert len(argus_modules) >= 50, (
        f"only {len(argus_modules)} argus modules walked — the population is broken, not clean"
    )
    for path in argus_modules:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:  # MODULE level only — the lazy edge is inside a function
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or ""]
            else:
                continue
            assert not any(n.startswith("_manifest") or n.startswith("_registry") for n in names), (
                f"{path.relative_to(_REPO_ROOT).as_posix()} imports the repository-only corpus "
                "substrate at MODULE level. It must be resolved lazily through "
                "`replay_harness.registry_module()` / `corpus_manifest_module()`, or the built "
                "wheel cannot import (DF-9-2-A)."
            )


# ─────────────────────────────────────────────────────────────────────────────────────
# AC5 / DF-8-5-C — the published figure is DERIVED from the corpora, not written by hand
# ─────────────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_DOGFOOD_001_53_the_corpus_measurement_is_a_measurement() -> None:
    """TC-ArgusAgent-DOGFOOD-001-53 — AC5/DF-8-5-C: the numbers come from the corpora.

    Driver: ``measure_validation_corpus()`` against an INDEPENDENT fold over both tables,
    computed here from the raw rows rather than by calling the same helper twice. The defect
    ``DF-8-5-C`` records is that ``proof_run.py`` passed ``precision=Fraction(0, 1), n=0`` as
    **literals** — arguments that were never a measurement of anything — so what has to be
    proven is not that the numbers are *right* but that they are *derived*.

    Both quantities are asserted because the artifact reports both and they are different
    corpora (AC1): the gate's ``N`` is the **repository** corpus (0 eligible members today),
    and the cartridge rows are the **recall** substrate (7 populated rows across 5 distinct
    rule classes, measured live). Reporting the cartridge count as the gate's ``N`` would read
    as "floor met" for a gate the cartridges do not gate at all.
    """
    measured = measure_validation_corpus()

    expected_n = len([s for s in VALIDATION_CORPUS if s.eligible_for_n])
    expected_rows = len(
        [s for s in CARTRIDGE_REGISTRY if s.kind in ("planted_defect", "holdout")]
    )
    expected_classes = len(
        {
            gf.rule_id
            for s in CARTRIDGE_REGISTRY
            if s.kind in ("planted_defect", "holdout")
            for gf in s.required_findings
        }
    )

    assert measured.validation_set_n == expected_n == 0
    assert measured.recall_cartridge_rows == expected_rows == 7, (
        "the recall substrate is no longer 7 populated rows. If a cartridge was added or "
        "removed, re-measure and update this DELIBERATELY — DF-8-5-C exists because a figure "
        "about this corpus was published without anyone measuring it"
    )
    assert measured.recall_rule_classes == expected_classes == 5
    assert measured.floor_n == VALIDATION_SET_FLOOR_N
    assert measured.validation_set_available and measured.recall_substrate_available
    assert measured.unavailable_reasons == ()


def test_TC_ArgusAgent_DOGFOOD_001_54_the_rendered_figure_EQUALS_the_derived_figure() -> None:
    """TC-ArgusAgent-DOGFOOD-001-54 — AC5: the committed artifact carries the derivation, verbatim.

    Driver: ``derive_gate_status()`` — the single composition ``build_dogfood_proof`` uses —
    compared against the committed ``minions-dogfood-proof.md``. This is the assertion that
    fails when someone reverts to a literal and regenerates: the artifact would then carry
    ``precision=0/1 … N=0 labeled cartridges``, and the derivation would not.

    It is deliberately an EQUALITY against the live derivation rather than a substring match on
    an expected number. A guard that asserted ``"N=0"`` was absent would go green the moment the
    literal changed to any other wrong number; a guard that asserts the rendered line IS the
    derived line cannot be satisfied by a second hand-written figure.
    """
    derived = derive_gate_status()
    artifact = _PROOF_ARTIFACT.read_text(encoding="utf-8")

    assert derived in artifact, (
        "the committed proof artifact does not carry the DERIVED gate status.\n"
        f"derived: {derived}\n"
        "The artifact is regenerated by its own renderer, never hand-edited: run\n"
        "  python scripts/regenerate_dogfood_artifacts.py\n"
        "after committing the `argus/` delta (the DF-8-5-B / DF-10-4-D bootstrap)."
    )

    # The superseded literals must not survive anywhere in the artifact.
    assert "precision=0/1" not in artifact, (
        "the artifact still renders `precision=0/1` — the DF-8-5-C literal. This run computes "
        "NO precision number, and saying 'zero' is not the same statement as 'not computed'"
    )
    assert "N=0 labeled cartridges populated" not in artifact, (
        "the artifact still renders `N=0 labeled cartridges populated` — the DF-8-5-C literal, "
        "which understated a corpus of 7 populated rows across 5 rule classes"
    )

    # The gate is still PROVISIONAL. Deriving the figure must never move the gate.
    assert "provisional" in derived and "NOT a cleared gate" in derived, (
        "OI1: the derivation is a correctness fix to a reported number, never a step toward "
        "clearing the gate"
    )


def test_TC_ArgusAgent_DOGFOOD_001_55_the_literals_are_gone_and_cannot_come_back_silently() -> None:
    """TC-ArgusAgent-DOGFOOD-001-55 — AC5 RED-first: the seam refuses the shape it was built from.

    Two halves, because "derived" has to be true of both the source and the contract:

    (a) ``proof_run.py`` no longer passes a literal ``Fraction(0, 1)`` or ``n=0`` into the gate
        status — read out of the source with ``ast``, so a reformatting cannot hide it;
    (b) ``precision_gate_status_for`` REFUSES to render a not-computed precision as anything
        other than provisional. The old signature would happily have rendered
        ``precision=0/1 … cleared`` if a caller had passed ``provisional=False``; a run that
        computed no precision number must be structurally incapable of reporting a cleared gate.
    """
    tree = ast.parse(_PROOF_RUN_SOURCE.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
            continue
        if node.func.id != "precision_gate_status_for":
            continue
        for keyword in node.keywords:
            if keyword.arg == "n":
                assert not isinstance(keyword.value, ast.Constant), (
                    "proof_run.py passes a LITERAL n into precision_gate_status_for — this is "
                    "DF-8-5-C exactly as it was filed. Derive it from the corpus."
                )
            if keyword.arg == "precision":
                assert not (
                    isinstance(keyword.value, ast.Call)
                    and isinstance(keyword.value.func, ast.Name)
                    and keyword.value.func.id == "Fraction"
                ), (
                    "proof_run.py passes a LITERAL Fraction into precision_gate_status_for. "
                    "This run computes no precision number; say so, do not invent a zero."
                )

    # (b) — the contract itself refuses the over-claim.
    with pytest.raises(ValueError, match="computed NO precision number"):
        precision_gate_status_for(
            precision=None,
            n=0,
            provisional=False,
            protocol_path="_bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md",
            floor_n=VALIDATION_SET_FLOOR_N,
        )

    rendered = precision_gate_status_for(
        precision=None,
        n=0,
        provisional=True,
        protocol_path="_bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md",
        floor_n=VALIDATION_SET_FLOOR_N,
    )
    assert "NOT COMPUTED BY THIS RUN" in rendered, (
        "a not-computed precision must SAY so on the surface a reader sees, rather than "
        "rendering a ratio that looks like a measurement"
    )
