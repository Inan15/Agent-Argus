"""One run's two human surfaces must not describe it differently (Story 8.3 / DR-11).

Verification area ArgusAgent-REPORT (TC-ArgusAgent-REPORT-002-NN, continuing at -20).

``argus audit`` renders a verdict for a human TWICE — as the stderr ship-readiness
block (``plain_english.render_ship_readiness``) and as the persisted ``final-verdict.md``
(``generator.render_final_verdict_report``, which quotes the first surface as its own
headline). Nothing forced the two to agree with each other or with the verdict token
printed between them, and DF-8-1-A is what that costs: a document whose second line
says ``INSUFFICIENT_COVERAGE (Exit Code 3)`` and whose eighth line says ``Repository is
NOT ready for release``.

This module is the anti-regression net for that class of defect:

- ``-002-20`` the DF-8-1-A closer — a row-4 document asserts no block (RED-first).
- ``-002-21`` all four FR16 rows, through BOTH surfaces, checked against the verdict
  and exit code printed in the same document. This is the single test that would have
  caught DF-8-1-A.
- ``-002-22`` the generator surface is deterministic and leaks no host path / secret
  (measured gap: ``plain_english`` had such a pin, ``render_final_verdict_report`` had
  none).
- ``-002-23`` the report's application/test split uses the SAME content-disambiguated
  classification the pipeline's scope narrowing uses (AC8).

Every verdict here is a REAL ``evaluate_verdict`` fold: a surface can only be shown to
describe what the tool produces if the input is what the tool produces.
"""

from __future__ import annotations

from pathlib import Path

from argus.index.ast_index import build_ast_index
from argus.ledger.coverage_ledger import (
    CoverageDepth,
    CoverageLedger,
    CoverageLedgerEntry,
)
from argus.models import AuditRequest
from argus.reports.generator import render_final_verdict_report
from argus.reports.plain_english import render_ship_readiness
from argus.verdict.verdict_gate import AuditVerdict, DecisionRow, evaluate_verdict

_DEEP = CoverageDepth.AUDITED_DEEP
_SHALLOW = CoverageDepth.AUDITED_SHALLOW

#: The sentence that asserts the repository itself is defective. Legitimate for FR16
#: row 2 (a finding was actually made) and a falsehood for every other row. Matched
#: case-insensitively; the verdict TOKEN ``NOT_READY_FOR_RELEASE`` carries underscores
#: and is deliberately not matched by it.
_BLOCK_ASSERTION = "not ready for release"

#: Every ``Next:`` line that sends the operator INTO the persisted report, mapped to the
#: section that must therefore EXIST in the same run's document. A pointer at a section
#: the document does not contain is the cross-surface contradiction DR-11 exists to
#: delete — one surface promising a work list the other surface silently dropped.
#: Registration is mandatory: an unregistered pointer fails the test, so a future
#: ``Next:`` line cannot reference the report without proving the reference resolves.
_REPORT_POINTERS: dict[str, str] = {
    "see the final-verdict report for the named critical files": (
        "### Critical subsystems below `audited_deep`"
    ),
}


def _entry(path: str, depth: CoverageDepth) -> CoverageLedgerEntry:
    return CoverageLedgerEntry(file_path=path, depth=depth, claim_present=(depth is _DEEP))


def _ledger(total: int, deep: int) -> CoverageLedger:
    return CoverageLedger.build(
        tuple(
            _entry(f"src/m{i}.py", _DEEP if i < deep else _SHALLOW) for i in range(total)
        )
    )


def _request(repo_path: str = "/repo") -> AuditRequest:
    return AuditRequest(
        repo_path=repo_path, commit="HEAD", budget=100, materiality_bar="default"
    )


def _fold(
    ledger: CoverageLedger,
    n_findings: int = 0,
    *,
    criticals_all_deep: bool = True,
    criticals_not_deep: tuple[str, ...] = (),
) -> AuditVerdict:
    """A REAL fold — reusing the shared finding builder (§3.3 / AR7 no-fork)."""
    from tests.test_verdict_gate import _ast_finding

    return evaluate_verdict(
        ledger,
        tuple(_ast_finding(file_path=f"t{i}.py", start=i + 1) for i in range(n_findings)),
        critical_subsystems_all_deep=criticals_all_deep,
        critical_subsystems_not_deep=criticals_not_deep,
    )


def _asserts_a_block(document: str) -> bool:
    return _BLOCK_ASSERTION in document.lower()


def _assert_every_pointer_resolves(
    block: tuple[str, ...], document: str, label: str
) -> None:
    """Every ``Next:`` line that references the report must land on something.

    ``render_ship_readiness`` and ``render_final_verdict_report`` render ONE run. A
    ``Next:`` line telling the operator to "see the final-verdict report for the named
    critical files" while that report contains no such section is exactly the
    cross-surface disagreement boundary B4 forbids — and it is invisible to a check
    that only compares block assertions, which is how it survived the first review.
    """
    for line in block:
        step = line.strip()
        if not step.startswith("Next:"):
            continue
        if "final-verdict report" not in step:
            continue  # self-contained advice (re-run with a flag), not a pointer
        targets = [
            section for pointer, section in _REPORT_POINTERS.items() if pointer in step
        ]
        assert targets, f"{label}: unregistered pointer into the report — {step!r}"
        for section in targets:
            assert section in document, (
                f"{label}: `Next:` points at a section this run's document does not "
                f"contain — {step!r} -> {section!r}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# -002-20 — DF-8-1-A: the persisted report stops contradicting its own verdict
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_REPORT_002_20_row_4_document_asserts_no_block() -> None:
    """TC-ArgusAgent-REPORT-002-20 — AC5: closes DF-8-1-A, for both of its causes.

    Measured verbatim before the fix, six lines under
    ``- **Final Verdict**: **`INSUFFICIENT_COVERAGE`** (Exit Code `3`)``::

        > [!CAUTION]
        > Repository is NOT ready for release — deep coverage `2/5` is below the `3/5`
        > release threshold.

    and, for the critical-clause cause at 5/5 deep::

        > [!CAUTION]
        > Repository is NOT ready for release — at least one critical subsystem is not
        > audited deep (FR16).

    Both are a blocking assertion on a NON-blocking verdict with zero findings. What
    replaces them must be true of row 4: nothing blocking was found, the gate(s) that
    actually were unmet are named, and it says plainly that this describes the AUDIT.
    """
    coverage_ledger = _ledger(5, 2)
    coverage_verdict = _fold(coverage_ledger)
    critical_ledger = _ledger(5, 5)
    critical_verdict = _fold(
        critical_ledger, criticals_all_deep=False, criticals_not_deep=("src/ghost.py",)
    )

    documents = {}
    for cause, (ledger, verdict) in {
        "coverage": (coverage_ledger, coverage_verdict),
        "critical": (critical_ledger, critical_verdict),
    }.items():
        assert verdict.decision_row is DecisionRow.GATE_UNMET_NO_FINDINGS, cause
        assert verdict.blocking_finding_count == 0, cause
        text = render_final_verdict_report(_request(), verdict, ledger, 0)
        documents[cause] = text

        assert "**`INSUFFICIENT_COVERAGE`** (Exit Code `3`)" in text, cause
        assert not _asserts_a_block(text), f"{cause}: document still asserts a block"
        # …and what it says instead is true of row 4.
        assert "NOT VOUCHED" in text, cause
        assert "nothing blocking" in text, cause
        assert "This is a statement about the audit, not about the code." in text, cause

    # The gate that was ACTUALLY unmet is the one named — never the other one.
    assert (
        "deep coverage `2/5` is below the `3/5` release threshold" in documents["coverage"]
    )
    assert "critical subsystem is not audited deep" not in documents["coverage"]
    assert (
        "at least one critical subsystem is not audited deep (FR16)"
        in documents["critical"]
    )
    assert "release threshold" not in documents["critical"]


# ─────────────────────────────────────────────────────────────────────────────
# -002-21 — the four-row cross-surface net
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_REPORT_002_21_all_four_rows_agree_across_both_surfaces() -> None:
    """TC-ArgusAgent-REPORT-002-21 — AC11: the test that would have caught DF-8-1-A.

    One REAL fold per FR16 row, rendered through BOTH surfaces. For each, the prose
    must be consistent with the verdict token and exit code printed in the same
    document: no ``INSUFFICIENT_COVERAGE`` document may assert the repository is not
    ready for release, and no ``RELEASE_READY`` document may explain a block.

    EXTENDED after review finding R1, which this test's first version did not catch:
    consistency is not only about what each surface ASSERTS, it is also about what one
    surface PROMISES the other contains. Every row that CAN carry an unmet
    critical-subsystem clause now carries one, and every ``Next:`` pointer emitted by
    ``render_ship_readiness`` must resolve inside the very document the same run
    produced. Row 3 is excluded from the critical fixture by the gate itself —
    ``RELEASE_READY`` requires ``critical_subsystems_all_deep``.
    """
    rows: dict[DecisionRow, tuple[CoverageLedger, AuditVerdict]] = {}
    below_floor = _ledger(10, 1)
    rows[DecisionRow.BELOW_FLOOR] = (
        below_floor,
        _fold(below_floor, criticals_all_deep=False, criticals_not_deep=("src/m9.py",)),
    )
    blocking = _ledger(5, 3)
    rows[DecisionRow.BLOCKING_FINDINGS] = (
        blocking,
        _fold(blocking, 1, criticals_all_deep=False, criticals_not_deep=("src/m4.py",)),
    )
    gates_met = _ledger(5, 3)
    rows[DecisionRow.GATES_MET] = (gates_met, _fold(gates_met))
    gate_unmet = _ledger(5, 2)
    rows[DecisionRow.GATE_UNMET_NO_FINDINGS] = (
        gate_unmet,
        _fold(gate_unmet, criticals_all_deep=False, criticals_not_deep=("src/m4.py",)),
    )

    headlines: set[str] = set()
    for row, (ledger, verdict) in rows.items():
        assert verdict.decision_row is row, "the fold did not fire the row it is filed under"
        block = render_ship_readiness(verdict)
        headline = block[0]
        document = render_final_verdict_report(_request(), verdict, ledger, 0)
        headlines.add(headline)

        # R1: one run, two surfaces — neither may point at what the other omits.
        _assert_every_pointer_resolves(block, document, row.value)

        # The surfaces are ONE register: the report quotes the ship-readiness line.
        assert f"> {headline}" in document
        assert f"**`{verdict.verdict.value}`** (Exit Code `{verdict.exit_code}`)" in document
        assert f"**Blocking Findings**: **{verdict.blocking_finding_count}**" in document

        if verdict.verdict.value == "NOT_READY_FOR_RELEASE":
            # The ONLY row allowed to assert a block — and only with a finding behind it.
            assert _asserts_a_block(document)
            assert verdict.blocking_finding_count >= 1
        else:
            assert not _asserts_a_block(
                document
            ), f"{row.value} asserts a block on a non-blocking verdict"

        if not verdict.critical_subsystems_all_deep:
            # The work list is rendered on EVERY row that has one — otherwise the
            # ``- Critical files not examined deeply: N`` counter on the other surface
            # names a quantity with nothing behind it.
            assert "### Critical subsystems below `audited_deep`" in document, row.value
            # …but only row 4 may present it as the CAUSE. On rows 1 and 2 the cause is
            # in the callout above, and a causal lead here would be a second false
            # causal claim of exactly the kind AC6 removed from the reason list.
            assert ("These withheld `RELEASE_READY` (FR16)." in document) is (
                row is DecisionRow.GATE_UNMET_NO_FINDINGS
            ), row.value

        if verdict.verdict.value == "RELEASE_READY":
            assert "Critical subsystems below" not in document
            assert "test-file dilution" not in document
            assert "satisfies all deterministic release readiness criteria" in document
        if verdict.verdict.value == "INSUFFICIENT_COVERAGE":
            assert verdict.blocking_finding_count == 0
            assert "verdict-blocking finding(s) must be resolved" not in document

    assert len(headlines) == 4, "each FR16 row must read differently to a human"


# ─────────────────────────────────────────────────────────────────────────────
# -002-22 — determinism + secret safety on the generator surface (measured gap)
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_REPORT_002_22_report_is_deterministic_and_leaks_nothing() -> None:
    """TC-ArgusAgent-REPORT-002-22 — AC10: PURE + NFR-S1 on ``final-verdict.md``.

    ``plain_english`` has had this pin since it shipped; the generator surface — the
    one that gets COMMITTED into a repository as evidence — had none. Same inputs must
    give byte-identical output (no clock, no ``uuid``, no set/dict iteration order, no
    ``float``), and no absolute host path, source byte or secret may appear.
    """
    secret = "AKIAIOSFODNN7EXAMPLE"
    ledger = CoverageLedger.build(
        (
            _entry("src/a.py", _DEEP),
            _entry("src/b.py", _DEEP),
            _entry("src/naïve.py", _SHALLOW),
            _entry("tests/test_a.py", _SHALLOW),
        )
    )
    verdict = _fold(
        ledger,
        criticals_all_deep=False,
        criticals_not_deep=("src/naïve.py", "src/z.py"),
    )
    request = _request(repo_path="/home/ci/work/repo")

    first = render_final_verdict_report(request, verdict, ledger, 3)
    second = render_final_verdict_report(request, verdict, ledger, 3)

    assert first == second
    assert secret not in first
    assert "/home/ci/work/repo" not in first
    assert ":\\" not in first
    assert "0." not in first, "ratios must render as exact Fractions, never floats"
    for line in first.splitlines():
        assert not line.startswith("/"), line


# ─────────────────────────────────────────────────────────────────────────────
# -002-23 — the report and the verdict classify the same file the same way (AC8)
# ─────────────────────────────────────────────────────────────────────────────


_PRODUCTION_MODULE_WITH_A_TEST_NAME = (
    '"""The vacuous-TEST detector — a production module, not a test suite."""\n'
    "\n"
    "\n"
    "def assess_vacuity(symbol: str) -> bool:\n"
    '    """Return whether *symbol* names a vacuous test."""\n'
    '    return symbol.startswith("noop")\n'
)

_REAL_TEST_MODULE = (
    "from src.widget import build\n"
    "\n"
    "\n"
    "def test_build_returns_a_widget():\n"
    "    assert build() is not None\n"
)

_APPLICATION_MODULE = (
    "def build():\n"
    '    """Build the widget."""\n'
    '    return {"kind": "widget"}\n'
)


def test_TC_ArgusAgent_REPORT_002_23_report_split_matches_the_pipeline_classification(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-REPORT-002-23 — AC8: one run, one test-file predicate.

    ``_render_test_dilution_hint`` split application from test files by NAME ONLY while
    ``pipeline._assessment_scope_paths`` uses ``is_test_file(path, ast_entry=…)`` — whose
    docstring says a disagreement inside one run "is precisely the kind of inconsistency
    this tool exists to surface in other people's repositories". MEASURED on Argus's own
    repository at the time of writing: 147 indexed files, exactly ONE disagreement —
    ``argus/detectors/vacuous_test.py``, a production module whose name ends ``_test.py``.

    Reproduced here BY CONSTRUCTION rather than by reading this repo's file list, so the
    pin cannot rot: a production module named ``*_test.py`` must land on the APPLICATION
    side of the report's denominator exactly as it lands inside the verdict's assessed
    population, and the ``ast_index is None`` callers must keep their old behaviour.
    """
    from argus.detectors.vacuous_test import is_test_file

    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "tests").mkdir()
    sources = {
        "src/vacuous_test.py": _PRODUCTION_MODULE_WITH_A_TEST_NAME,
        "src/widget.py": _APPLICATION_MODULE,
        "tests/test_widget.py": _REAL_TEST_MODULE,
    }
    for rel, text in sources.items():
        (repo / rel).write_text(text, encoding="utf-8")
    index = build_ast_index(repo, tuple(sorted(sources)), partition_id="root")
    entry_by_path = {e.file_path: e for e in index.entries}

    # The disagreement itself: name-only says "test", the content says "production".
    assert is_test_file("src/vacuous_test.py") is True
    assert (
        is_test_file("src/vacuous_test.py", ast_entry=entry_by_path["src/vacuous_test.py"])
        is False
    )

    # A ledger diluted enough for the hint to fire: both application files are deep,
    # the (many) test files are shallow by construction.
    entries = [
        _entry("src/vacuous_test.py", _DEEP),
        _entry("src/widget.py", _DEEP),
    ]
    entries += [_entry(f"tests/test_{i}.py", _SHALLOW) for i in range(8)]
    ledger = CoverageLedger.build(tuple(entries))
    verdict = _fold(ledger)
    assert verdict.decision_row is DecisionRow.GATE_UNMET_NO_FINDINGS

    with_index = render_final_verdict_report(
        _request(), verdict, ledger, 0, ast_index=index
    )
    without_index = render_final_verdict_report(_request(), verdict, ledger, 0)

    # WITH the AST index the production module counts as application — 2 of 2 deep,
    # the same population `_assessment_scope_paths` would assess.
    assert "2/2 (`1`) of APPLICATION files" in with_index
    assert "8 test file(s)" in with_index
    # WITHOUT one (the pre-existing unit-test callers) behaviour is UNCHANGED: the
    # ambiguous name still answers "test", so the denominator is 1 and 9 are held out.
    assert "1/1 (`1`) of APPLICATION files" in without_index
    assert "9 test file(s)" in without_index
