"""Story 18.2 / DF-AUD-DETECT-B — the redaction call kept the evidence it computed.

Verification area ArgusAgent-SECRET (``TC-ArgusAgent-SECRET-001-28``..``-30``, CONTINUING the index
whose prior maximum is ``-27``; nothing is renumbered).

**The defect under repair, measured on 2026-08-24 at HEAD ``c288d40``.**
``secret_scan.py``'s ``run()`` carried, under the banner ``# -- PRODUCER-SIDE REDACTION (the
keystone) --``, the expression statement ``self._evidence_for(match)``. ``_evidence_for`` is a pure
``@staticmethod`` returning a frozen :class:`SecretFindingEvidence`, and **its return value was
bound to nothing**. Proven by AST at that HEAD: it was the module's ONLY expression statement
discarding an ``_evidence_for`` return, and the other call site — inside ``scan_evidence`` — binds
its result and is genuine::

    DISCARDED-VALUE CALL STATEMENTS to _evidence_for: [(506, 'self._evidence_for(match)')]
    ALL _evidence_for CALL SITES:                     [(376, ...), (506, ...)]

Per match that statement computed ``masked``, ``value_length``, ``kind``, ``pattern_id`` and an
exact ``Fraction`` Shannon ``entropy_bits`` — and discarded all five in the same statement that
computed them.

**It was unobservable, measured over the whole tree rather than argued.** ``SecretScanDetector()
.run()`` was driven over every file in ``git ls-files -- '*.py'`` (251 files) twice — once with the
shipped ``_evidence_for``, once with it nulled — comparing the FULL ``DetectorResult`` (``entries``
+ ``findings`` + ``degraded``, canonical JSON) per file:

===========================  =========================  =============  ====================
population 251               ``hardcoded_secret``       files with >=1  ``DetectorResult``
                             findings                                   differing
===========================  =========================  =============  ====================
shipped ``_evidence_for``    88                         37             --
``_evidence_for`` nulled     88                         37             **0**
===========================  =========================  =============  ====================

``_evidence_for`` was invoked 88 times over that sweep, exactly once per emitted finding: a
suppressed match ``continue``s ABOVE the call, so suppressed matches never reached it.

**The cost was noise and no performance claim rests on this module.** 1.467 s shipped vs 1.477 s
nulled on the re-measurement — the nulled side was *slower*, which is how far inside the noise the
difference sits. ``DF-AUD-DETECT-C`` (detector cost) is **not** dispositioned by it.

**The repair is DELETE-AND-CORRECT, not schema widening** (``DN-18-2-1``). ``DF-AUD-DETECT-B``
offers two repairs and names the widening arm as the one matching Story 2.5; Story 2.5's own record
at ``:613`` states the opposite — *"SecretFindingEvidence is NOT folded into DetectorResult and is
NOT persisted"* — so the widening arm would reverse a ``done`` story's locked decision. FR11, this
detector's FR, requires no evidence to be carried at all; the entry's FR10 citation is the
*vacuous-test* FR. The carrier is NOT deleted: :class:`SecretFindingEvidence`,
``SECRET_EVIDENCE_SCHEMA_VERSION``, ``_evidence_for`` and ``scan_evidence()`` all survive unchanged.

**What these three guards cover that the shipped suite does not.**
``TC-ArgusAgent-SECRET-001-08`` already asserts :class:`SecretFindingEvidence` has no value field,
``TC-ArgusAgent-EVIDENCE-001-04`` already asserts the field-name discipline over ``Recording`` and
``Locator``, and ``tests/test_secret_containment.py`` already gates the end-to-end containment
PROPERTY under a randomized population. None of them asserts that the redaction **claim in the
code** is true — that nothing in ``run()`` depends on the discarded computation, that the discarded
call cannot come back, and that ``FindingDraft`` / ``DetectorResult`` (the two models
``-04`` does not reach) have nowhere to put a value.

**RED evidence (AI-E14-1).** Every case here was run against the SHIPPED module body before the
repair existed, by monkeypatching a pre-change copy of the module held OUTSIDE the repository.
``-28`` goes RED: ``:506`` sits outside the ``try/except`` that wraps only ``self._scan(source)``,
so an ``_evidence_for`` raised through the shipped body **propagates out of** ``run()``. ``-29``
goes RED on the AST assertion. ``-30`` stays GREEN **by design** and must hold before AND after —
it pins FR28's structural guarantee, which was true before this story and stays true after it; it
is here so that a future widening of these models cannot land silently. The raw failure text is in
the story's Dev Agent Record. Per the guard-fire rule this author-driven RED is **vacuity
evidence** — proof the cases can fail — not "these guards caught a defect".

**Every case runs on the NON-TEST path** ``argus/prod/settings.py`` (§2.3): a case built on a
``tests/**`` path would be suppressed by step 5's ``DEFAULT_TEST_PATH_PATTERNS`` for an entirely
unrelated reason and would assert nothing at all. That path is never opened — ``run()`` is pure and
uses ``file_path`` only for glob matching and locators — and it does not exist on disk.

**Key material here is synthetic and built in this module**, never planted in a committed fixture
file (NFR-S1 / NFR-S2), and every assertion is on a count, a rule id, a field name or an absence —
never on a secret value. Every case asserts its population is non-empty BEFORE asserting anything
about it (AI-E11-1).

Counts are asserted as ``>= 1`` and by before/after EQUALITY, never as an exact total: ``run()``
de-duplicates on ``(start_line, end_line, pattern_id)``, so one source line legitimately yields more
than one finding — the ``API_TOKEN = "AKIA..."`` line yields three. Asserting the exact triple would
redden this module the moment Story 18.3 narrows those very regexes, which is the right reason for a
wrong RED.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from argus.detectors.base import DetectorResult, FindingDraft
from argus.detectors.secret_scan import RULE_HARDCODED_SECRET, SecretScanDetector
from argus.index.ast_index import AstIndexEntry
from argus.store import canonical
from argus.verdict.verdict_gate import blocking_finding_count, is_verdict_blocking

#: The non-test path every case runs on. Never opened; ``run()`` is pure (AR8) and uses
#: ``file_path`` only for glob matching and locators. It does not exist on disk and must not
#: be created (§2.7).
_NON_TEST_PATH = "argus/prod/settings.py"

#: The module under guard, resolved from THIS file rather than from a hard-coded absolute
#: path, so the AST guard travels with the repository (AI-E13-1: CI runs an ubuntu matrix).
_SECRET_SCAN_PATH = (
    Path(__file__).resolve().parent.parent / "argus" / "detectors" / "secret_scan.py"
)

#: Synthetic key material, built here and never read from a fixture file (NFR-S1 / NFR-S2).
#: The AWS-shaped literal is the published documentation example, not a live credential.
_SYNTHETIC_SECRET = "AKIAIOSFODNN7EXAMPLE"
_SYNTHETIC_SOURCE = f'API_TOKEN = "{_SYNTHETIC_SECRET}"\n'

#: The field names :class:`SecretFindingEvidence` carries. NONE of them may appear in the
#: canonical serialization of an emitted ``DetectorResult`` (AC3.4/(i)).
_EVIDENCE_FIELD_NAMES = ("masked", "value_length", "entropy_bits", "kind", "pattern_id")

#: The forbidden field-name tokens, extending ``TC-ArgusAgent-EVIDENCE-001-04``'s discipline
#: to the two models it does not cover (AC3.4/(ii)).
_FORBIDDEN_FIELD_TOKENS = (
    "source",
    "secret",
    "value",
    "body",
    "excerpt",
    "content",
    "raw",
)


def _entry(file_path: str = _NON_TEST_PATH) -> AstIndexEntry:
    """The 1.4 entry, constructed directly — no tree-sitter (the ``test_secret_scan`` precedent)."""
    return AstIndexEntry(
        file_path=file_path, ast_eligible=True, definitions=(), edges=()
    )


def _run(source: str = _SYNTHETIC_SOURCE, *, file_path: str = _NON_TEST_PATH):
    return SecretScanDetector().run(
        file_path=file_path, source=source, ast_entry=_entry(file_path)
    )


def _hardcoded(result) -> list:
    return [f for f in result.findings if f.rule_id == RULE_HARDCODED_SECRET]


# -- -28 - the BEHAVIOURAL guard --------------------------------------------------


def test_TC_ArgusAgent_SECRET_001_28_run_does_not_depend_on_the_discarded_evidence_computation() -> None:
    """TC-ArgusAgent-SECRET-001-28 — ``run()``'s output does not depend on ``_evidence_for``.

    **Observable:** with ``SecretScanDetector._evidence_for`` monkeypatched to RAISE, ``run()``
    on the non-test path still emits byte-identical findings. The redaction guarantee is
    STRUCTURAL — no emitted model has a field that could hold the value — so the evidence
    computation is not on ``run()``'s path at all and its absence must be unobservable.

    **RED against the shipped body:** the discarded ``self._evidence_for(match)`` statement sat
    OUTSIDE the ``try/except`` that wraps only ``self._scan(source)``, so the raise propagated
    and ``run()`` never returned. Author-driven RED = vacuity evidence (AI-E14-1).

    ``monkeypatch`` is scoped by pytest and undone at teardown, so no other case sees the
    patched body.
    """
    # AI-E11-1 - the population is asserted non-empty with the REAL body first. A guard that
    # compared two empty results would pass forever without observing anything.
    real = _run()
    real_findings = _hardcoded(real)
    assert real_findings, (
        "non-vacuity: the real body must emit at least one hardcoded_secret finding on "
        f"{_NON_TEST_PATH!r}, otherwise the comparison below observes nothing"
    )
    real_blob = canonical.dumps(real.model_dump(mode="json"))

    def _raising(match):  # noqa: ANN001, ANN202 - a stand-in for a @staticmethod
        raise AssertionError(
            "_evidence_for must not be on run()'s path (TC-ArgusAgent-SECRET-001-28)"
        )

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(SecretScanDetector, "_evidence_for", staticmethod(_raising))
        patched = _run()

    assert canonical.dumps(patched.model_dump(mode="json")) == real_blob, (
        "run() emitted a DIFFERENT DetectorResult when _evidence_for was unavailable, so "
        "the producer-side evidence computation IS on run()'s path"
    )
    assert len(_hardcoded(patched)) == len(real_findings)

    # The carrier itself is untouched by this story and still USES _evidence_for, which is
    # what stops the guard from passing by the function having become dead everywhere.
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(SecretScanDetector, "_evidence_for", staticmethod(_raising))
        with pytest.raises(AssertionError):
            SecretScanDetector().scan_evidence(
                file_path=_NON_TEST_PATH, source=_SYNTHETIC_SOURCE
            )


# -- -29 - the NON-RECURRENCE guard -----------------------------------------------


def test_TC_ArgusAgent_SECRET_001_29_no_evidence_for_call_discards_its_return_value() -> None:
    """TC-ArgusAgent-SECRET-001-29 — no ``_evidence_for`` call site throws its return away.

    **Observable:** over ``argus/detectors/secret_scan.py``'s own AST, whether any
    ``_evidence_for`` call is an ``ast.Expr(value=ast.Call(...))`` — the exact shape of a call
    whose value is discarded. At HEAD ``c288d40`` there was exactly one, at ``:506``.

    **Scoped to ``_evidence_for`` deliberately.** A blanket *"no bare call statements"* rule
    would fire on ``matches.append(...)``, ``seen.add(...)`` and ``findings.append(...)`` in
    this same file, which are legitimate discarded-value statements (§2.7).

    The module must still contain AT LEAST ONE ``_evidence_for`` call site, so the guard
    cannot pass by the function having vanished — deleting the carrier is AC7, an escalation,
    and this assertion is what makes that escalation visible instead of silent.
    """
    source = _SECRET_SCAN_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    def _callee_name(call: ast.Call) -> str | None:
        func = call.func
        if isinstance(func, ast.Attribute):
            return func.attr
        if isinstance(func, ast.Name):
            return func.id
        return None

    call_sites = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and _callee_name(node) == "_evidence_for"
    ]
    # AI-E11-1 - assert the population is non-empty BEFORE asserting anything about it.
    assert call_sites, (
        "non-vacuity: secret_scan.py contains NO _evidence_for call site at all, so the "
        "discarded-value assertion below would pass without observing anything. The "
        "in-memory carrier scan_evidence() must keep calling it (AC1.4)"
    )

    discarded = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Call)
        and _callee_name(node.value) == "_evidence_for"
    ]
    assert not discarded, (
        "secret_scan.py calls _evidence_for and DISCARDS the return value at line(s) "
        f"{discarded!r}. That computes the masked indicator, the length, the kind, the "
        "pattern id and an exact-Fraction entropy and throws all five away in the statement "
        "that computes them, while reading as the load-bearing redaction step "
        "(DF-AUD-DETECT-B). Redaction here is STRUCTURAL - the emitted models have no field "
        "that could hold the value - so this call cannot be what provides it"
    )

    # The definition itself survives with its shape intact (AC1.4).
    definitions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_evidence_for"
    ]
    assert len(definitions) == 1, (
        f"expected exactly one _evidence_for definition, found {len(definitions)}"
    )
    assert "staticmethod" in [
        ast.unparse(decorator) for decorator in definitions[0].decorator_list
    ], "_evidence_for must remain a pure @staticmethod (AC1.4)"


# -- -30 - the FR28 STRUCTURAL guard ----------------------------------------------


def test_TC_ArgusAgent_SECRET_001_30_the_emitted_result_has_nowhere_to_put_a_value() -> None:
    """TC-ArgusAgent-SECRET-001-30 — FR28's redaction is structural, over the whole result.

    **Observable:** (i) the canonical serialization of the WHOLE ``DetectorResult`` carries
    neither the secret value nor any :class:`SecretFindingEvidence` field NAME; (ii) no field
    name of ``FindingDraft`` or ``DetectorResult`` matches the forbidden token set — extending
    ``TC-ArgusAgent-EVIDENCE-001-04``'s discipline to the two models it does not cover.

    **GREEN before AND after this story, by design.** The guarantee it pins was already true;
    what was missing was anything asserting it over these two models. It is the guard that
    reddens if a future story widens ``DetectorResult`` to carry evidence without taking
    ``DN-18-2-1``'s escalation path (AC7).

    No assertion here is on a secret value: the value is asserted ABSENT, and everything else
    asserted is a count or a field name (AC3.6).
    """
    result = _run()
    findings = _hardcoded(result)
    # AI-E11-1 - the absence assertions below are worthless over an empty result.
    assert findings, (
        "non-vacuity: the synthetic secret must produce at least one hardcoded_secret "
        "finding, otherwise every absence assertion below passes trivially"
    )

    # (i) the WHOLE result, not just the first finding.
    blob = canonical.dumps(result.model_dump(mode="json"))
    assert _SYNTHETIC_SECRET not in blob, (
        "the secret value appears in the emitted DetectorResult (FR28 / NFR-S1 / NFR-S2)"
    )
    assert "****" not in blob, (
        "the masked indicator reached an emitted field. It is computed by scan_evidence()'s "
        "in-memory carrier and must never enter a finding - only the LOCATION survives"
    )
    for name in _EVIDENCE_FIELD_NAMES:
        assert f'"{name}"' not in blob, (
            f"evidence field name {name!r} appears in the emitted DetectorResult; "
            "SecretFindingEvidence is an in-memory carrier and is NOT folded into "
            "DetectorResult (Story 2.5 :613, locked)"
        )

    # (ii) the two models TC-ArgusAgent-EVIDENCE-001-04 does not cover.
    for model in (FindingDraft, DetectorResult):
        field_names = set(model.model_fields)
        assert field_names, f"non-vacuity: {model.__name__} reported zero fields"
        offenders = sorted(
            name
            for name in field_names
            for token in _FORBIDDEN_FIELD_TOKENS
            if token in name.lower()
        )
        assert not offenders, (
            f"{model.__name__} carries field(s) {offenders!r} whose name matches the "
            "forbidden token set. Redaction here is the ABSENCE of a value slot; a field "
            "that could hold one is the thing FR28 forbids"
        )
        assert model.model_config.get("frozen") is True, (
            f"{model.__name__} must stay frozen (NFR-M2)"
        )
        assert model.model_config.get("extra") == "forbid", (
            f"{model.__name__} must stay extra='forbid' - that is what makes the absence of "
            "a value field a GUARANTEE rather than a convention"
        )

    # A hardcoded_secret finding is advisory and non-blocking by construction, so nothing
    # here can move a verdict (the -22 precedent).
    assert blocking_finding_count(result.findings) == 0
    for finding in findings:
        assert finding.advisory is True
        assert finding.depth_supported is None
        assert not is_verdict_blocking(finding)
