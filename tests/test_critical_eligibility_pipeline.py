"""The eligibility SEAM end-to-end + the F1 false-green counterweight (Story 8.2).

Verification area ArgusAgent-PIPELINE (``TC-ArgusAgent-PIPELINE-002-NN``). Drivers:
ArgusAgent-FR-4 as amended (DR-5 eligibility filter, DR-6 operator exemption), AR7/§3.3
(``is_test_file`` and ``is_deep_claim_grounded`` are REUSED by import — no second
predicate), AR8 (the fact is derived in the impure shell and travels as DATA), boundary
B3 (a vacuously satisfied gate must be VISIBLE), inversion **F1** (the loosening is
measured, not hidden) and FR16 **row-2 precedence** (a real finding outranks the gates).

Why the counterweight is the most important test in this file
-------------------------------------------------------------
Every other guard in this delta points at *"don't over-block"*. DR-5 and the
``--coverage-scope application`` default each make ``RELEASE_READY`` EASIER to reach, and
the PRD names a false ``RELEASE_READY`` as the fatal error. The existing clean-control
cartridges only guard the false-**red** direction. So the loosening is asserted in both
directions here: leg (a) proves the gate still withholds where it should, and leg (b)
proves — against the REAL pre-filter behaviour, recomputed from the same candidates — the
exact transition the filter buys, so the residual exposure is measured rather than
assumed.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))

from _cartridge import stage_cartridge  # noqa: E402

from argus.index.ast_index import build_ast_index  # noqa: E402
from argus.ledger.coverage_ledger import CoverageDepth, CoverageLedger  # noqa: E402
from argus.ledger.critical_subsystems import (  # noqa: E402
    CriticalIneligibility,
    critical_subsystems_not_deep,
    identify_critical_subsystems,
)
from argus.ledger.depth_semantics import Criticality  # noqa: E402
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import _detect_per_file, run_audit_detailed  # noqa: E402
from argus.pipeline_persist import (  # noqa: E402
    CRITICAL_SUBSYSTEMS_PRODUCER,
    NEGATIVE_ASSURANCE_PRODUCER,
)
from argus.reports.generator import render_final_verdict_report  # noqa: E402
from argus.reports.plain_english import render_ship_readiness  # noqa: E402
from argus.store.reader import ApaaStoreReader  # noqa: E402
from argus.verdict.verdict_gate import DecisionRow, Verdict  # noqa: E402

# ─────────────────────────────────────────────────────────────────────────────
# Fixture repositories — staged in a tmp dir, never added to CARTRIDGE_REGISTRY
# (that registry is the ground truth of the 6.6 precision replay harness).
# ─────────────────────────────────────────────────────────────────────────────

#: A genuinely security-relevant module that is ``audited_shallow`` BY CONSTRUCTION:
#: the epic's own example — a clean-parsed ZERO-definition ``__init__.py`` that
#: re-exports a security boundary. Heuristic-CRITICAL by content, never deep-gradable.
_SECURITY_REEXPORT_INIT = (
    '"""Application package — re-exports the authorization boundary."""\n'
    "\n"
    "from app.auth import authorize_request  # noqa: F401\n"
)

_AUTH_MODULE = (
    '"""Authorization boundary."""\n'
    "\n"
    "\n"
    "def authorize_request(user_token: str, permission: str) -> bool:\n"
    '    """Return True when the token grants the permission."""\n'
    "    return bool(user_token) and bool(permission)\n"
)

#: Leg (b) — every OTHER gate met: 3 deep + 1 shallow = 3/4 ≥ 3/5, zero blocking findings.
_ALL_GATES_MET = {
    "app/__init__.py": _SECURITY_REEXPORT_INIT,
    "app/auth.py": _AUTH_MODULE,
    "app/service.py": (
        "from app.auth import authorize_request\n"
        "\n"
        "\n"
        "def handle(user_token: str) -> str:\n"
        '    if authorize_request(user_token, "read"):\n'
        '        return "ok"\n'
        '    return "denied"\n'
    ),
    "app/util.py": "def normalize(value: str) -> str:\n    return value.strip().lower()\n",
}

#: Leg (a) — identical except that ANOTHER gate is genuinely unmet: 1 deep + 3 shallow
#: = 1/4, which is below the 3/5 deep-coverage gate and above the 1/5 floor, so the
#: withholding is a GATE decision (row 4) rather than the floor (row 1).
_ANOTHER_GATE_UNMET = {
    "app/__init__.py": _SECURITY_REEXPORT_INIT,
    "app/auth.py": _AUTH_MODULE,
    "app/models/__init__.py": '"""Model package."""\n',
    "app/config/__init__.py": '"""Config package."""\n',
}

#: AC8 — every heuristic critical hit is INELIGIBLE, so the filter EMPTIES the critical
#: set while the run still reaches ``RELEASE_READY``: the sharpest possible test that no
#: surface converts a vacuously satisfied gate into a positive assurance claim.
_VACUOUSLY_SATISFIED = {
    "app/__init__.py": _SECURITY_REEXPORT_INIT,
    "app/util.py": "def normalize(value: str) -> str:\n    return value.strip().lower()\n",
    "app/formatting.py": (
        "def titleize(value: str) -> str:\n"
        "    return value.title()\n"
        "\n"
        "\n"
        "def indent(value: str, width: int) -> str:\n"
        '    return " " * width + value\n'
    ),
}


def _stage(files: dict[str, str], dest: Path) -> Path:
    """Materialize *files* into *dest* as a fresh single-commit git repo.

    The same shape ``_cartridge.stage_cartridge`` uses (``load_repo_at_commit`` wants a
    clean tree whose HEAD is the resolved pin), kept local because these fixtures are
    deliberately NOT cartridges: ``CARTRIDGE_REGISTRY`` is the ground truth of the 6.6
    precision replay harness and its size is read by a gate.
    """
    dest.mkdir(parents=True, exist_ok=True)
    for rel, text in files.items():
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    (dest / ".gitignore").write_text(".argus/\n", encoding="utf-8")
    for args in (
        ["init"],
        ["config", "core.autocrlf", "false"],
        ["config", "user.email", "eligibility@argus.test"],
        ["config", "user.name", "ArgusAgent Eligibility Fixture"],
        ["add", "-A"],
        ["commit", "-m", "eligibility fixture"],
    ):
        subprocess.run(["git", "-C", str(dest), *args], check=True, capture_output=True)
    return dest


def _request(repo: Path, **overrides: object) -> AuditRequest:
    return AuditRequest(
        repo_path=str(repo),
        commit="HEAD",
        budget=100,
        materiality_bar="default",
        **overrides,  # type: ignore[arg-type]
    )


def _payload(reader: ApaaStoreReader, locators: tuple[str, ...], producer: str) -> dict[str, object]:
    """The single persisted payload written by *producer*, read back from ``state/``."""
    matches = [
        json.loads(reader.read_bytes(loc).decode("utf-8"))
        for loc in locators
    ]
    payloads = [env["payload"] for env in matches if env["producer"] == producer]
    assert len(payloads) == 1, f"expected exactly one {producer} artifact, got {len(payloads)}"
    return payloads[0]


# ─────────────────────────────────────────────────────────────────────────────
# AC7 — the seam: the fact is derived in the shell, from the REUSED predicates,
#       and the eligibility stage cannot disagree with the GRADING stage
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "unreadable_path",
    ["app/broken_auth.py", "app/auth_test.py"],
    ids=["production-name", "ambiguous-test-suffix"],
)
def test_TC_ArgusAgent_PIPELINE_002_01_shell_derives_the_token_for_each_grading_class(
    tmp_path: Path, unreadable_path: str
) -> None:
    """AC1/AC2/AC3/AC7 — the token the shell derives matches the depth it actually grades.

    All four rows of the grading table in ONE run, so the two stages are compared against
    each other rather than against a restatement of the rule:

    * a test file             → ``audited_shallow``, ``TEST_FILE``
    * clean parse, 0 defs     → ``audited_shallow``, ``ZERO_DEFINITION_MODULE``
    * parse-failed            → ``skipped``, **ELIGIBLE** (shallow by CIRCUMSTANCE — D3)
    * clean parse, ≥1 def     → ``audited_deep``, ELIGIBLE

    The parse-failed row is parametrized over **both filename shapes** because D3 is a
    claim about the file's READABILITY, not about its name: an unreadable security module
    called ``app/auth_test.py`` must land on exactly the same side as one called
    ``app/broken_auth.py``. The unparametrized version of this test covered only the
    unambiguous name and so missed a live false green (review iteration 1).
    """
    repo = _stage(
        {
            "tests/test_auth.py": (
                "from app.auth import authorize_request\n"
                "\n"
                "\n"
                "def test_authorize_request_requires_a_token():\n"
                '    assert authorize_request("", "read") is False\n'
            ),
            "app/__init__.py": _SECURITY_REEXPORT_INIT,
            unreadable_path: "def authorize_request(token:\n",
            "app/auth.py": _AUTH_MODULE,
        },
        tmp_path / "repo",
    )
    sources = ("app/__init__.py", "app/auth.py", unreadable_path, "tests/test_auth.py")
    index = build_ast_index(repo, sources, partition_id="root")

    entries, _findings, candidates = _detect_per_file(repo, index.entries, _request(repo))
    by_path = {c.file_path: c for c in candidates}
    depth_by_path = {e.file_path: e.depth for e in CoverageLedger.build(entries).entries}

    # Every one of these is heuristic-CRITICAL by content — that is the whole problem.
    assert all(
        by_path[p].criticality is Criticality.CRITICAL
        for p in ("tests/test_auth.py", "app/__init__.py", unreadable_path, "app/auth.py")
    )

    assert by_path["tests/test_auth.py"].ineligibility is CriticalIneligibility.TEST_FILE
    assert depth_by_path["tests/test_auth.py"] is CoverageDepth.AUDITED_SHALLOW

    assert (
        by_path["app/__init__.py"].ineligibility
        is CriticalIneligibility.ZERO_DEFINITION_MODULE
    )
    assert depth_by_path["app/__init__.py"] is CoverageDepth.AUDITED_SHALLOW

    # D3 — skipped by CIRCUMSTANCE stays in the critical set. It is NOT audited_shallow.
    assert by_path[unreadable_path].ineligibility is None, (
        "an unreadable file is shallow by CIRCUMSTANCE; the filename must not decide it"
    )
    assert depth_by_path[unreadable_path] is CoverageDepth.SKIPPED

    assert by_path["app/auth.py"].ineligibility is None
    assert depth_by_path["app/auth.py"] is CoverageDepth.AUDITED_DEEP

    # …and the fold keeps exactly the two files a run could still satisfy the gate with.
    critical = identify_critical_subsystems(candidates)
    assert critical.paths == tuple(sorted(("app/auth.py", unreadable_path)))
    assert critical.heuristic_excluded_ineligible == {
        "tests/test_auth.py": CriticalIneligibility.TEST_FILE,
        "app/__init__.py": CriticalIneligibility.ZERO_DEFINITION_MODULE,
    }


def test_TC_ArgusAgent_PIPELINE_002_02_ambiguous_test_suffix_is_classified_once_by_content(
    tmp_path: Path,
) -> None:
    """AC7 — one ``is_test_file`` evaluation drives BOTH stages, so they cannot disagree.

    A production module named ``*_test.py`` whose subject is testing must not be mistaken
    for a test suite. The load-bearing assertion is the AGREEMENT: the file is graded
    ``audited_deep``, so calling it a test file for eligibility purposes would silently
    remove a deep-gradable security module from the gate.
    """
    repo = _stage(
        {
            "app/auth_test.py": (
                '"""Production helpers for exercising the authorization boundary."""\n'
                "\n"
                "\n"
                "def build_permission_token(user: str) -> str:\n"
                '    return f"{user}:token"\n'
            )
        },
        tmp_path / "repo",
    )
    index = build_ast_index(repo, ("app/auth_test.py",), partition_id="root")
    entries, _findings, candidates = _detect_per_file(repo, index.entries, _request(repo))

    candidate = candidates[0]
    depth = CoverageLedger.build(entries).entries[0].depth
    assert candidate.criticality is Criticality.CRITICAL
    assert depth is CoverageDepth.AUDITED_DEEP
    assert candidate.ineligibility is None, (
        "the grading stage treated this as production; the eligibility stage must agree"
    )
    assert identify_critical_subsystems(candidates).paths == ("app/auth_test.py",)


def test_TC_ArgusAgent_PIPELINE_002_09_an_unreadable_ambiguous_name_keeps_its_place(
    tmp_path: Path,
) -> None:
    """AC3 / D3 — a tier-3 test label is a GUESS when the content cannot be read.

    ``-002-02``'s clean-parse twin is staged beside a syntax-error file of the same shape
    and a genuine test file that also fails to parse. All three answers must hold at once:

    * the READABLE ``app/auth_test.py`` — content says production → ELIGIBLE (``-002-02``)
    * the UNREADABLE ``svc/token_test.py`` — ``is_test_file`` says "test" only because
      :func:`_exhibits_test_definitions` answers ``True`` for anything it cannot read, and
      that direction is conservative for GRADING but LOOSENING for eligibility → ELIGIBLE,
      and never disclosed under the false reason ``test_file``
    * the UNREADABLE ``tests/test_broken.py`` — tier 1 classified it by LOCATION, which is
      a property of what the file IS and holds however the parse went → ``TEST_FILE``

    That third row is why the fix is not "hoist the clean-parse guard above the test
    branch": doing so would make grammar-less GENUINE test files eligible again and
    rebuild the permanently unsatisfiable gate DR-5 exists to delete. The classification
    is distrusted only for the AMBIGUOUS tier, via the predicate exported from the module
    that owns the tiers (AR7/§3.3 — the suffix table is not re-declared in the shell).
    """
    repo = _stage(
        {
            "app/auth_test.py": (
                '"""Production helpers for exercising the authorization boundary."""\n'
                "\n"
                "\n"
                "def build_permission_token(user: str) -> str:\n"
                '    return f"{user}:token"\n'
            ),
            "svc/token_test.py": "def issue_permission_token(secret:\n",
            "tests/test_broken.py": "def test_check_permission(token:\n",
        },
        tmp_path / "repo",
    )
    sources = ("app/auth_test.py", "svc/token_test.py", "tests/test_broken.py")
    index = build_ast_index(repo, sources, partition_id="root")
    entries, _findings, candidates = _detect_per_file(repo, index.entries, _request(repo))

    by_path = {c.file_path: c for c in candidates}
    depth_by_path = {e.file_path: e.depth for e in CoverageLedger.build(entries).entries}
    assert all(by_path[p].criticality is Criticality.CRITICAL for p in sources)

    assert by_path["app/auth_test.py"].ineligibility is None
    assert depth_by_path["app/auth_test.py"] is CoverageDepth.AUDITED_DEEP

    assert by_path["svc/token_test.py"].ineligibility is None, (
        "the 'test' label was a guess forced by the unreadable content; the file is a "
        "security-token-bearing module the tool could not read — it stays in the gate"
    )
    assert depth_by_path["svc/token_test.py"] is CoverageDepth.SKIPPED

    assert by_path["tests/test_broken.py"].ineligibility is CriticalIneligibility.TEST_FILE, (
        "a test file identified by LOCATION is audited_shallow BY CONSTRUCTION whatever "
        "the parse did; keeping it would rebuild the unsatisfiable gate DR-5 deletes"
    )

    critical = identify_critical_subsystems(candidates)
    assert critical.paths == ("app/auth_test.py", "svc/token_test.py")
    assert critical.heuristic_excluded_ineligible == {
        "tests/test_broken.py": CriticalIneligibility.TEST_FILE
    }


# ─────────────────────────────────────────────────────────────────────────────
# AC10 / inversion F1 — the false-green counterweight, BOTH legs
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PIPELINE_002_03_leg_a_gate_still_withholds_where_it_should(
    tmp_path: Path,
) -> None:
    """AC10(a) — the filter does NOT make an under-assessed repository releasable.

    Same security-re-exporting ``__init__.py``, removed from the critical set exactly as
    in leg (b) — but another gate is genuinely unmet (1/4 deep, below 3/5), so
    ``RELEASE_READY`` is still withheld. The withholding is row 4 (a GATE, above the
    floor), not row 1, so this proves the coverage gate rather than the floor.
    """
    repo = _stage(_ANOTHER_GATE_UNMET, tmp_path / "repo")
    result = run_audit_detailed(_request(repo))

    assert result.verdict.verdict is not Verdict.RELEASE_READY
    assert result.verdict.verdict is Verdict.INSUFFICIENT_COVERAGE
    assert result.verdict.exit_code == 3
    assert result.verdict.decision_row is DecisionRow.GATE_UNMET_NO_FINDINGS
    assert result.verdict.is_below_floor is False
    # The critical clause IS vacuously satisfied here — which is precisely why the
    # OTHER gate has to be the thing still withholding release.
    assert result.verdict.critical_subsystems_all_deep is True


def test_TC_ArgusAgent_PIPELINE_002_04_leg_b_the_loosening_is_measured_not_hidden(
    tmp_path: Path,
) -> None:
    """AC10(b) — the exact transition the filter buys, proven against the REAL pre-filter fold.

    The counterfactual is not narrated: the same candidates are re-folded with the
    eligibility fact stripped (which IS the pre-8.2 contract, since the field defaults to
    ELIGIBLE) and shown to leave ``app/__init__.py`` in the critical set at
    ``audited_shallow`` — so ``critical_subsystems_all_deep`` was ``False`` and
    ``RELEASE_READY`` was unreachable. With the filter, the identical repository reaches
    it.

    **Accepted residual exposure (recorded, not waved away):** a genuinely
    security-relevant module that is shallow BY CONSTRUCTION no longer withholds release
    on its own. That is the deliberate trade — a gate no run can satisfy is not a gate —
    and the operator's remedy is pinned in ``-002-05``.
    """
    repo = _stage(_ALL_GATES_MET, tmp_path / "repo")
    sources = tuple(sorted(_ALL_GATES_MET))
    index = build_ast_index(repo, sources, partition_id="root")
    entries, _findings, candidates = _detect_per_file(repo, index.entries, _request(repo))
    ledger = CoverageLedger.build(entries)

    # The pre-filter contract: strip the fact (its default IS "eligible") and re-fold.
    pre_filter = identify_critical_subsystems(
        [c.model_copy(update={"ineligibility": None}) for c in candidates]
    )
    assert "app/__init__.py" in pre_filter.paths
    assert critical_subsystems_not_deep(pre_filter.paths, ledger) == ("app/__init__.py",)

    # The post-filter contract: the same file is removed AND disclosed.
    post_filter = identify_critical_subsystems(candidates)
    assert "app/__init__.py" not in post_filter.paths
    assert post_filter.heuristic_excluded_ineligible == {
        "app/__init__.py": CriticalIneligibility.ZERO_DEFINITION_MODULE
    }
    assert critical_subsystems_not_deep(post_filter.paths, ledger) == ()

    # …and end-to-end the repository now reaches the verdict it previously could not.
    result = run_audit_detailed(_request(repo))
    assert result.verdict.verdict is Verdict.RELEASE_READY
    assert result.verdict.exit_code == 0
    assert result.verdict.decision_row is DecisionRow.GATES_MET


def test_TC_ArgusAgent_PIPELINE_002_05_operator_designation_restores_the_block(
    tmp_path: Path,
) -> None:
    """AC10 / DR-6 — the lever that makes the residual exposure acceptable.

    An operator who judges the shallow-by-construction module genuinely critical says so,
    and the block comes back. Designation is EXEMPT from the eligibility filter, so this
    is the whole remedy — no new flag was needed (D6).
    """
    repo = _stage(_ALL_GATES_MET, tmp_path / "repo")
    result = run_audit_detailed(
        _request(repo, critical_paths=("app/__init__.py",))
    )

    assert result.verdict.verdict is not Verdict.RELEASE_READY
    assert result.verdict.decision_row is DecisionRow.GATE_UNMET_NO_FINDINGS
    assert result.verdict.critical_subsystems_all_deep is False
    assert "app/__init__.py" in result.verdict.critical_subsystems_not_deep


# ─────────────────────────────────────────────────────────────────────────────
# AC8 / boundary B3 — the disclosure lands on disk and NO surface over-claims
# ─────────────────────────────────────────────────────────────────────────────

#: Phrases that would convert a VACUOUSLY satisfied gate into a positive assurance
#: claim. Matched case-insensitively against every surface reachable from this story.
_FALSE_POSITIVE_CLAIMS = (
    "all critical",
    "every critical",
    "all criticals",
    "criticals examined",
    "critical subsystems examined deeply",
    "critical subsystems were examined",
)


def _assert_makes_no_positive_critical_claim(text: str, surface: str) -> None:
    lowered = text.lower()
    for phrase in _FALSE_POSITIVE_CLAIMS:
        assert phrase not in lowered, (
            f"{surface} asserts {phrase!r} for a gate that is only VACUOUSLY satisfied"
        )


def test_TC_ArgusAgent_PIPELINE_002_06_emptied_critical_set_is_disclosed_on_disk(
    tmp_path: Path,
) -> None:
    """AC8 / B3 — an emptied critical set is distinguishable from "there were none".

    Without the disclosure map the two serialize identically, which is exactly how a
    vacuously satisfied gate becomes invisible to the operator reading the artifacts.
    """
    repo = _stage(_VACUOUSLY_SATISFIED, tmp_path / "repo")
    result = run_audit_detailed(_request(repo))
    reader = ApaaStoreReader(repo)

    payload = _payload(reader, result.locators, CRITICAL_SUBSYSTEMS_PRODUCER)
    assert payload["paths"] == []
    assert payload["heuristic_excluded_ineligible"] == {
        "app/__init__.py": "zero_definition_module"
    }
    assert payload["schema_version"] == "2"
    # The gate really is satisfied only vacuously.
    assert result.verdict.critical_subsystems_all_deep is True
    assert result.verdict.verdict is Verdict.RELEASE_READY


def test_TC_ArgusAgent_PIPELINE_002_07_no_surface_claims_all_criticals_examined_deeply(
    tmp_path: Path,
) -> None:
    """AC8 — the proof of the NEGATIVE, over every surface this story can reach.

    The persisted ``assurance_statement``, the ``scope_statement`` critical narration and
    both rendered report surfaces are inspected. None may assert that critical subsystems
    were examined deeply when the gate is satisfied only because the set is empty.

    Adding the POSITIVE prose that names the vacuity for a human is Story 8.3 / DR-11;
    this story's obligation is the machine-readable disclosure above plus this proof that
    no false claim exists in the meantime.
    """
    repo = _stage(_VACUOUSLY_SATISFIED, tmp_path / "repo")
    result = run_audit_detailed(_request(repo))
    reader = ApaaStoreReader(repo)

    assurance = _payload(reader, result.locators, NEGATIVE_ASSURANCE_PRODUCER)
    scope = assurance["scope_statement"]
    assert isinstance(scope, dict)
    # Nothing is listed as examined deeply, because nothing was.
    assert scope["critical_examined_deep"] == []
    assert scope["critical_not_examined_deep"] == []
    assert scope["critical_designated_but_unmatched"] == []
    _assert_makes_no_positive_critical_claim(
        str(assurance["assurance_statement"]), "the persisted assurance_statement"
    )

    # The report surfaces are rendered from the SAME ledger the run folded — rebuilt
    # through the shipped functions rather than restated, so what is inspected here is
    # what an operator would actually read.
    index = build_ast_index(repo, tuple(sorted(_VACUOUSLY_SATISFIED)), partition_id="root")
    entries, findings, _candidates = _detect_per_file(repo, index.entries, _request(repo))
    ledger = CoverageLedger.build(entries)

    report = render_final_verdict_report(
        _request(repo), result.verdict, ledger, len(findings)
    )
    _assert_makes_no_positive_critical_claim(report, "the final-verdict report")
    _assert_makes_no_positive_critical_claim(
        "\n".join(render_ship_readiness(result.verdict)), "the ship-readiness summary"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC14 — the ONE cartridge the filter touches keeps its verdict (row-2 precedence)
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_PIPELINE_002_08_holdout_vacuous_keeps_its_block_by_row_2_precedence(
    tmp_path: Path,
) -> None:
    """AC14 — the flip is UNDERSTOOD, not merely survived.

    ``holdout_vacuous`` is the single cartridge whose critical set the filter empties (its
    lone critical path is a test file), so ``critical_subsystems_all_deep`` moves
    ``False`` → ``True``. Its verdict must NOT move: it carries a real AST-corroborated
    blocking finding, and under the Story-8.1 four-row table row 2 (findings) is evaluated
    BEFORE row 3 (gates). This asserts the mechanism — gate satisfied, block retained —
    rather than just the surviving exit code.
    """
    repo, _sha = stage_cartridge("holdout_vacuous", tmp_path / "repo")
    result = run_audit_detailed(_request(repo))
    reader = ApaaStoreReader(repo)

    payload = _payload(reader, result.locators, CRITICAL_SUBSYSTEMS_PRODUCER)
    assert payload["paths"] == [], "the filter empties this cartridge's critical set"
    assert payload["heuristic_excluded_ineligible"] == {
        "tests/test_inventory.py": "test_file"
    }
    # The gate clause is now satisfied…
    assert result.verdict.critical_subsystems_all_deep is True
    # …and the verdict is unchanged anyway, because a real finding outranks the gates.
    assert result.verdict.verdict is Verdict.NOT_READY_FOR_RELEASE
    assert result.verdict.exit_code == 2
    assert result.verdict.decision_row is DecisionRow.BLOCKING_FINDINGS
    assert any(
        f.rule_id == "vacuous_test_ast" for f in result.verdict.ordered_findings
    ), "the golden vacuous_test_ast finding must be unchanged"
