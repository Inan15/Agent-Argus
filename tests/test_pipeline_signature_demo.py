"""Story 1.7 — the signature demo + pipeline wiring + determinism + degradation.

Verification area ArgusAgent-PIPELINE (TC-ArgusAgent-PIPELINE-001-NN). Covers:
  - AC4: the signature demo on cartridge #1 (BLOCKED / exit 2 / vacuous finding first)
  - AC5: sequential byte-identical determinism (two runs → identical verdict bytes)
  - AC6: honest degradation (bad repo → exit 1, drifted tree → typed RepoIntakeError)
  - AC2: pipeline-wiring over the cartridge (six stages run; ledger + verdict assembled)
  - the false-accusation floor (clean control → RELEASE_READY, never a false 🔴)

The pipeline/CLI are the impure shell under test, so a real (staged) git repo +
temp ``.argus/`` trees are used — but the verdict/ledger/serializer stay zero-token
(NFR-D2: the Epic-1 slice calls NO LLM).
"""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))

from _cartridge import stage_cartridge  # noqa: E402

from argus.intake.repo_loader import RepoIntakeError  # noqa: E402
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import (  # noqa: E402
    PipelineError,
    ResumeStateError,
    resume_audit_detailed,
    run_audit,
    run_audit_detailed,
)
from argus.store.reader import ApaaStoreReader  # noqa: E402
from argus.store.writer import ApaaStoreWriter  # noqa: E402
from argus.verdict.verdict_gate import Verdict  # noqa: E402


def _request(repo: Path, commit: str = "HEAD") -> AuditRequest:
    return AuditRequest(
        repo_path=str(repo), commit=commit, budget=100, materiality_bar="default"
    )


def test_signature_demo_vacuous_cartridge_blocks(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-01 — cartridge #1: BLOCKED 🔴, exit 2, vacuous finding first."""
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")
    verdict = run_audit(_request(repo))

    assert verdict.verdict is Verdict.NOT_READY_FOR_RELEASE
    assert verdict.exit_code == 2
    assert verdict.blocking_finding_count >= 1

    first = verdict.ordered_findings[0]
    assert first.rule_id == "vacuous_test_ast"
    assert first.depth_supported is not None  # verdict-eligible (the moat)
    # The blocking finding sorts strictly first (FR33).
    assert any(f.rule_id == "vacuous_test_ast" for f in verdict.ordered_findings)


def test_signature_demo_calculator_stays_deep_under_fr7(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-40 — story 6.2 (AC4): the signature-demo SUT stays audited_deep under FR7.

    The migration honesty check: ``src/calculator.py`` has real ``compute_total`` /
    ``apply_discount`` definitions → it is AST-GROUNDED under FR7 → it STAYS
    ``audited_deep``, so the deep-% (1/2 ≥ 20%) and the BLOCKED 🔴 / exit 2 verdict
    are PRESERVED (the signature moat reproduces — DF-1-7-B closure did NOT weaken
    the demo). Proven empirically, not assumed.
    """
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")
    result = run_audit_detailed(_request(repo))

    from argus.ledger.coverage_ledger import CoverageDepth as _CD

    counts = result.verdict.counts_by_depth
    assert counts[_CD.AUDITED_DEEP] == 1  # calculator.py is grounded, stays deep
    assert result.verdict.verdict is Verdict.NOT_READY_FOR_RELEASE
    assert result.verdict.exit_code == 2
    assert result.verdict.deep_ratio == Fraction(1, 2)


def test_clean_control_is_not_a_false_block(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-02 — false-accusation floor: clean control → RELEASE_READY."""
    repo, _sha = stage_cartridge("clean_control", tmp_path / "repo")
    verdict = run_audit(_request(repo))

    assert verdict.verdict is Verdict.RELEASE_READY
    assert verdict.exit_code == 0
    assert verdict.blocking_finding_count == 0


def test_pipeline_persists_verdict_and_findings(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-03 — AC2: the run writes a verdict + finding into .argus/."""
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")
    result = run_audit_detailed(_request(repo))

    # verdict (state/), >=1 finding (findings/), run-state (state/).
    assert any(loc.startswith("state/") for loc in result.locators)
    assert any(loc.startswith("findings/") for loc in result.locators)

    reader = ApaaStoreReader(repo)
    verdict_locator = result.locators[0]
    envelope = reader.read_envelope(verdict_locator)  # re-verifies content_hash (tamper guard)
    assert envelope.payload["verdict"] == "NOT_READY_FOR_RELEASE"


def test_pipeline_persists_partition_work_manifests(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-13 — Story 2.4: the run persists per-unit work-manifests.

    The scope-fenced 2.4 persistence touch writes ≥1 ``assignments/<partition_id>
    .json`` work-manifest + a partition-plan snapshot carrying the V1
    ``seam_analysis="v2-deferred"`` marker — without changing the verdict.
    """
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")
    result = run_audit_detailed(_request(repo))

    assignment_locs = [loc for loc in result.locators if loc.startswith("assignments/")]
    assert assignment_locs, "expected at least one persisted work-manifest"

    reader = ApaaStoreReader(repo)
    manifest_env = reader.read_envelope(assignment_locs[0])  # re-verifies content_hash
    payload = manifest_env.payload
    assert payload["work_manifest"]["files"]  # the closed read allow-set
    assert isinstance(payload["file_count"], int)
    # The persisted manifest carries no absolute host path.
    for f in payload["work_manifest"]["files"]:
        assert not f.startswith("/") and ":\\" not in f

    # The verdict is unchanged by the partition persistence (scope fence).
    assert result.verdict.verdict.value == "NOT_READY_FOR_RELEASE"


def test_partition_manifests_byte_identical_across_runs(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-14 — Story 2.4: per-unit manifests are byte-stable (NFR-P1)."""
    repo_a, _ = stage_cartridge("vacuous_basic", tmp_path / "a")
    repo_b, _ = stage_cartridge("vacuous_basic", tmp_path / "b")
    result_a = run_audit_detailed(_request(repo_a))
    result_b = run_audit_detailed(_request(repo_b))

    locs_a = sorted(loc for loc in result_a.locators if loc.startswith("assignments/"))
    locs_b = sorted(loc for loc in result_b.locators if loc.startswith("assignments/"))
    assert locs_a == locs_b  # identical content-addressed names across hosts

    reader_a = ApaaStoreReader(repo_a)
    reader_b = ApaaStoreReader(repo_b)
    for loc in locs_a:
        assert reader_a.read_bytes(loc) == reader_b.read_bytes(loc)


def test_sequential_byte_identical_determinism(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-04 — AC5: same cartridge twice → identical verdict bytes."""
    repo_a, _ = stage_cartridge("vacuous_basic", tmp_path / "a")
    repo_b, _ = stage_cartridge("vacuous_basic", tmp_path / "b")

    result_a = run_audit_detailed(_request(repo_a))
    result_b = run_audit_detailed(_request(repo_b))

    reader_a = ApaaStoreReader(repo_a)
    reader_b = ApaaStoreReader(repo_b)

    # The verdict envelope is content-addressed: identical content → identical name.
    verdict_loc_a = result_a.locators[0]
    verdict_loc_b = result_b.locators[0]
    assert verdict_loc_a == verdict_loc_b

    # Byte-identical persisted verdict bytes (NFR-P1) + identical content_hash.
    bytes_a = reader_a.read_bytes(verdict_loc_a)
    bytes_b = reader_b.read_bytes(verdict_loc_b)
    assert bytes_a == bytes_b

    env_a = reader_a.read_envelope(verdict_loc_a)
    env_b = reader_b.read_envelope(verdict_loc_b)
    assert env_a.content_hash == env_b.content_hash


def test_bad_repo_path_raises_typed_error(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-05 — AC6: a non-existent repo path → typed RepoIntakeError."""
    request = _request(tmp_path / "does_not_exist")
    with pytest.raises(RepoIntakeError):
        run_audit(request)


def test_drifted_tree_is_audited_by_default_and_refused_under_strict(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-06 — drift is a WORKTREE audit by default, refused under --strict.

    Supersedes the original "drift always raises" contract. A developer mid-edit is
    the common case, and refusing them an audit helps nobody; the release gate that
    genuinely needs commit-pinned evidence opts in with ``strict=True``. The relaxation
    is safe because the resolved state is RECORDED — a worktree audit is labelled as
    not third-party reproducible rather than presented as a pinned commit.
    """
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")
    # Introduce drift: an untracked file makes ``git status --porcelain`` non-empty.
    (repo / "drift.py").write_text("x = 1\n", encoding="utf-8")

    # Default: it runs.
    verdict = run_audit(_request(repo))
    assert verdict.exit_code in (0, 2, 3)

    # Release-gate mode: it still refuses, with a typed error.
    with pytest.raises(RepoIntakeError):
        run_audit(_request(repo).model_copy(update={"strict": True}))


def test_unresolvable_commit_raises_typed_error(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-07 — AC6: an unresolvable pin → typed RepoIntakeError."""
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")
    with pytest.raises(RepoIntakeError):
        run_audit(_request(repo, commit="deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"))


def test_injected_store_writer_is_used(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-08 — AC2: an injected ApaaStoreWriter receives the artifacts."""
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")
    out = tmp_path / "out"
    out.mkdir()
    writer = ApaaStoreWriter(out)
    result = run_audit_detailed(_request(repo), store_writer=writer)

    # Artifacts landed under the injected writer's .argus/, not the repo's.
    assert (out / ".argus" / "state").exists()
    assert result.locators


def test_pipeline_error_is_a_value_error() -> None:
    """TC-ArgusAgent-PIPELINE-001-09 — PipelineError is a ValueError (CLI maps it to exit 1)."""
    assert issubclass(PipelineError, ValueError)


# ─────────────────────────────────────────────────────────────────────────────
# Story 6.2 — FR7 AST-grounding: the verdict migration is observable (DF-1-7-B)
# ─────────────────────────────────────────────────────────────────────────────


def _stage_zero_def_only_repo(dest: Path) -> Path:
    """Stage a repo whose ONLY non-test Python file is a clean-parse ZERO-definition module.

    Under the INTERIM over-grading (claim_present=True always) this constants-only
    module was graded ``audited_deep`` (deep-% = 1/1 = 100% ≥ 20% floor → a real
    verdict). Under FR7 it is UNGROUNDED → ``audited_shallow`` (deep-% = 0% < 20%
    floor → INSUFFICIENT_COVERAGE / exit 3) — the verdict migration the DF-1-7-B
    closure produces, observable end-to-end.
    """
    import subprocess

    dest.mkdir(parents=True, exist_ok=True)
    src = dest / "src"
    src.mkdir(parents=True, exist_ok=True)
    # A clean-parsing module with ZERO function/class definitions (constants +
    # re-export + __all__ only) — nothing for a deep read to substantively examine.
    (src / "constants.py").write_text(
        '"""A constants-only module — no function/class definitions (ungrounded under FR7)."""\n'
        "\n"
        "MAX_RETRIES = 3\n"
        "DEFAULT_TIMEOUT = 30\n"
        '__all__ = ["MAX_RETRIES", "DEFAULT_TIMEOUT"]\n',
        encoding="utf-8",
    )
    subprocess.run(["git", "-C", str(dest), "init"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(dest), "config", "core.autocrlf", "false"], check=True, capture_output=True)
    (dest / ".gitignore").write_text(".argus/\n", encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(dest), "config", "user.email", "fr7@argus.test"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(dest), "config", "user.name", "ArgusAgent FR7"],
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "-C", str(dest), "add", "-A"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(dest), "commit", "-m", "zero-def constants module"],
        check=True,
        capture_output=True,
    )
    return dest



def test_e2e_zero_def_module_no_longer_clears_floor_under_fr7(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-41 — story 6.2 (AC2/AC4): a zero-def module downgrades, lowering deep-%.

    The verdict-migration proof. A repo whose only non-test Python file is a
    clean-parse ZERO-definition constants module:
      - INTERIM (claim_present=True always): graded ``audited_deep`` → deep-% 100%.
      - FR7: ``is_deep_claim_grounded`` is False → ``audited_shallow`` → deep-% 0% <
        20% floor → INSUFFICIENT_COVERAGE / exit 3. The over-grading is removed, and
        the deep-% the gate reads now reflects GROUNDED depth.
    """
    from argus.audit.grounding import is_deep_claim_grounded
    from argus.index.ast_index import build_ast_index
    from argus.intake.repo_loader import load_repo_at_commit
    from argus.ledger.coverage_ledger import CoverageDepth as _CD

    repo = _stage_zero_def_only_repo(tmp_path / "repo")

    # PRECONDITION: the constants module parses cleanly with ZERO definitions, so the
    # FR7 validator finds it ungrounded (the interim shape would have graded it deep).
    intake = load_repo_at_commit(str(repo), "HEAD")
    index = build_ast_index(repo, intake.source_files, partition_id="root")
    constants_entry = next(e for e in index.entries if e.file_path == "src/constants.py")
    assert constants_entry.ast_eligible is True
    assert constants_entry.parse_failed is False
    assert len(constants_entry.definitions) == 0
    assert is_deep_claim_grounded(constants_entry) is False  # the downgrade trigger

    result = run_audit_detailed(_request(repo))
    counts = result.verdict.counts_by_depth
    # FR7: the zero-def module is audited_shallow, NOT audited_deep → deep-% 0%.
    assert counts[_CD.AUDITED_DEEP] == 0
    assert counts[_CD.AUDITED_SHALLOW] >= 1
    assert result.verdict.verdict is Verdict.INSUFFICIENT_COVERAGE
    assert result.verdict.exit_code == 3


# ─────────────────────────────────────────────────────────────────────────────
# Story 2.3 — the wired FR16 critical-subsystem clause, end-to-end through the pipeline
# ─────────────────────────────────────────────────────────────────────────────


def _request_with_designation(
    repo: Path,
    *,
    critical: tuple[str, ...] = (),
    excluded: tuple[str, ...] = (),
) -> AuditRequest:
    return AuditRequest(
        repo_path=str(repo),
        commit="HEAD",
        budget=100,
        materiality_bar="default",
        critical_paths=critical,
        excluded_critical_paths=excluded,
    )


def test_e2e_operator_designated_critical_shallow_withholds_release_ready(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-10 — story 2.3: forcing a shallow file critical → NOT_READY/exit 2.

    The clean control is RELEASE_READY by default. The shallow test file
    ``tests/test_math.py`` is graded ``audited_shallow``; forcing it critical means a
    critical subsystem is below deep → the wired evaluate_verdict withholds
    RELEASE_READY (the FR16 clause), end-to-end through the pipeline.
    """
    repo, _sha = stage_cartridge("clean_control", tmp_path / "repo")
    verdict = run_audit(
        _request_with_designation(repo, critical=("tests/test_math.py",))
    )
    assert verdict.verdict is Verdict.NOT_READY_FOR_RELEASE
    assert verdict.exit_code == 2
    assert verdict.critical_subsystems_all_deep is False


def test_e2e_excluding_the_critical_restores_release_ready(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-11 — story 2.3: excluding that same path → RELEASE_READY (operator precedence)."""
    repo, _sha = stage_cartridge("clean_control", tmp_path / "repo")
    verdict = run_audit(
        _request_with_designation(
            repo,
            critical=("tests/test_math.py",),
            excluded=("tests/test_math.py",),
        )
    )
    assert verdict.verdict is Verdict.RELEASE_READY
    assert verdict.exit_code == 0


def test_e2e_no_designation_is_byte_identical_to_pre_2_3(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-12 — story 2.3: no-critical / no-designation run → byte-identical RELEASE_READY."""
    repo_a, _ = stage_cartridge("clean_control", tmp_path / "a")
    repo_b, _ = stage_cartridge("clean_control", tmp_path / "b")

    # A no-designation request and a plain default request resolve to the same verdict.
    default = run_audit_detailed(_request(repo_a))
    no_desig = run_audit_detailed(_request_with_designation(repo_b))

    reader_a = ApaaStoreReader(repo_a)
    reader_b = ApaaStoreReader(repo_b)
    # The content-addressed verdict envelope is byte-identical (the empty-set path is a no-op).
    assert default.locators[0] == no_desig.locators[0]
    assert reader_a.read_bytes(default.locators[0]) == reader_b.read_bytes(no_desig.locators[0])
    assert default.verdict.verdict is Verdict.RELEASE_READY


# ─────────────────────────────────────────────────────────────────────────────
# Story 3.1 — the scope-fenced cost-ledger snapshot persistence, end-to-end
# ─────────────────────────────────────────────────────────────────────────────


def test_e2e_cost_snapshot_persisted_with_ceiling(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-15 — story 3.1: a budget-configured run persists a cost snapshot.

    The cost-ledger snapshot lands content-addressed in ``state/`` carrying the
    int total + the configured ceiling + ceiling_reached + the per-axis breakdown +
    the NFR-C1 baseline Fraction. The verdict is unchanged by the additive
    persistence (scope fence — no halt, no verdict-math change).
    """
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")
    result = run_audit_detailed(_request(repo))  # budget=100 → ceiling configured

    reader = ApaaStoreReader(repo)
    cost_payloads = []
    for loc in result.locators:
        if not loc.startswith("state/"):
            continue
        payload = reader.read_envelope(loc).payload  # re-verifies content_hash
        if "ceiling_reached" in payload and "baseline_ratio" in payload:
            cost_payloads.append(payload)
    assert len(cost_payloads) == 1, "expected exactly one persisted cost snapshot"
    cost = cost_payloads[0]
    assert cost["ceiling_credits"] == 100
    assert isinstance(cost["total_credits"], int)
    assert cost["ceiling_reached"] in (True, False)
    assert "/" in cost["baseline_ratio"]  # the canonical Fraction "num/den" form
    assert isinstance(cost["breakdown"], dict)
    # The verdict is unchanged by the cost persistence (scope fence).
    assert result.verdict.verdict is Verdict.NOT_READY_FOR_RELEASE


def test_e2e_no_ceiling_run_byte_identical_verdict_ledger_findings(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-16 — story 3.1: a no-ceiling run is byte-identical on verdict/ledger/findings.

    The OI3 no-ceiling path (``budget == 0``) persists the additive cost snapshot,
    but the verdict + findings artifacts (which do NOT depend on the budget) stay
    byte-identical across a no-ceiling and a ceiling-configured run — proven by
    comparing the two runs' verdict + findings bytes. (The run-state legitimately
    records the differing ``budget`` for provenance, as it has since Story 1.7, so
    it is excluded from this byte-identity comparison.) ceiling_reached is False.
    """
    repo_a, _ = stage_cartridge("vacuous_basic", tmp_path / "a")
    repo_b, _ = stage_cartridge("vacuous_basic", tmp_path / "b")
    no_ceiling = AuditRequest(
        repo_path=str(repo_a), commit="HEAD", budget=0, materiality_bar="default"
    )
    with_ceiling = AuditRequest(
        repo_path=str(repo_b), commit="HEAD", budget=100, materiality_bar="default"
    )
    res_a = run_audit_detailed(no_ceiling)
    res_b = run_audit_detailed(with_ceiling)

    reader_a = ApaaStoreReader(repo_a)
    reader_b = ApaaStoreReader(repo_b)

    def _verdict_and_findings(reader, result):
        # The verdict envelope is always locators[0] (the _persist order, since 1.7);
        # findings are the findings/ locators. Both are budget-independent.
        out = {"__verdict__": reader.read_bytes(result.locators[0])}
        for loc in result.locators:
            if loc.startswith("findings/"):
                out[loc] = reader.read_bytes(loc)
        return out

    vf_a = _verdict_and_findings(reader_a, res_a)
    vf_b = _verdict_and_findings(reader_b, res_b)
    assert len(vf_a) >= 2, "expected a persisted verdict + >=1 finding"
    # The verdict + findings (content-addressed names AND bytes) match — the budget
    # config does NOT change them (the regression-safe scope fence).
    assert vf_a == vf_b

    # The no-ceiling cost snapshot exists and reports no ceiling / not reached.
    cost = [
        payload
        for loc in res_a.locators
        if loc.startswith("state/")
        for payload in (reader_a.read_envelope(loc).payload,)
        if "ceiling_reached" in payload
    ]
    assert len(cost) == 1
    assert cost[0]["ceiling_credits"] is None
    assert cost[0]["ceiling_reached"] is False


# ─────────────────────────────────────────────────────────────────────────────
# Story 3.2 — halt → skip → downgrade → report on budget exhaustion, end-to-end
# ─────────────────────────────────────────────────────────────────────────────


def _halt_report_payload(reader: ApaaStoreReader, result) -> dict:
    """Find the single persisted halt-report snapshot among the state/ locators."""
    payloads = []
    for loc in result.locators:
        if not loc.startswith("state/"):
            continue
        payload = reader.read_envelope(loc).payload  # re-verifies content_hash
        if "halted_on_exhaustion" in payload:
            payloads.append(payload)
    assert len(payloads) == 1, "expected exactly one persisted halt report"
    return payloads[0]


def _request_budget(repo: Path, budget: int) -> AuditRequest:
    return AuditRequest(
        repo_path=str(repo), commit="HEAD", budget=budget, materiality_bar="default"
    )


def test_e2e_budget_exhausted_run_halts_skips_and_downgrades(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-17 — story 3.2: a tiny budget halts, skips the remainder, degrades.

    The vacuous_basic cartridge has 2 Python files (5 credits each = 10 total). A
    budget of 6 admits the first file (5 < 6) then halts at the second (5+5=10 >= 6)
    → the remainder is graded SKIPPED (NEVER fabricated audited_*), the partial
    ledger re-folds through the UNCHANGED gate (degraded), and a halt report is
    persisted flagging halted_on_exhaustion=True with the skipped set.
    """
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")
    result = run_audit_detailed(_request_budget(repo, 6))

    reader = ApaaStoreReader(repo)
    report = _halt_report_payload(reader, result)
    assert report["halted_on_exhaustion"] is True
    assert report["skipped_on_exhaustion_count"] >= 1
    assert report["assessed_count"] >= 0
    # No skipped file appears in the assessed set (disjoint).
    assert not (
        set(report["assessed_files"]) & set(report["skipped_on_exhaustion_files"])
    )

    # The persisted ledger snapshot proves the un-audited remainder is SKIPPED,
    # never fabricated as an audited grade (the honest-degradation keystone).
    ledger_payloads = []
    for loc in result.locators:
        if not loc.startswith("state/"):
            continue
        payload = reader.read_envelope(loc).payload
        if "ledger" in payload and isinstance(payload.get("ledger"), dict):
            ledger_payloads.append(payload["ledger"])
    assert ledger_payloads, "expected a persisted run-state with a ledger"
    ledger = ledger_payloads[0]
    depths = {e["file_path"]: e["depth"] for e in ledger["entries"]}
    for skipped in report["skipped_on_exhaustion_files"]:
        assert depths[skipped] == "skipped"
        assert depths[skipped] not in ("audited_deep", "audited_shallow")


def test_e2e_full_budget_skip_when_ceiling_below_first_unit(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-18 — story 3.2: a ceiling below the first unit skips everything → INSUFFICIENT_COVERAGE.

    A budget of 1 (below the 5-credit per-Python-file cost) breaches at the very
    first unit → every file is SKIPPED → deep-% 0 → the UNCHANGED gate returns
    INSUFFICIENT_COVERAGE / exit 3 (the floor decision is the gate's existing
    threshold; the floor SEMANTICS rendering is Story 3.3).
    """
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")
    result = run_audit_detailed(_request_budget(repo, 1))

    reader = ApaaStoreReader(repo)
    report = _halt_report_payload(reader, result)
    assert report["halted_on_exhaustion"] is True
    assert report["assessed_count"] == 0
    assert result.verdict.verdict is Verdict.INSUFFICIENT_COVERAGE
    assert result.verdict.exit_code == 3


def test_e2e_no_halt_run_byte_identical_to_pre_3_2(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-19 — story 3.2: a no-halt run is byte-identical on verdict/ledger/findings (AC6).

    A run whose budget never reaches the ceiling (budget=100 over 10 credits) does
    NOT halt: no file is skipped-on-exhaustion, the halt report flags
    halted_on_exhaustion=False, and the verdict + findings artifacts are
    byte-identical to a no-ceiling (budget=0) run — the halt mechanism + the halt
    report are purely additive when no halt fires (the regression-safe keystone).
    """
    repo_a, _ = stage_cartridge("vacuous_basic", tmp_path / "a")
    repo_b, _ = stage_cartridge("vacuous_basic", tmp_path / "b")
    res_a = run_audit_detailed(_request_budget(repo_a, 0))  # no ceiling
    res_b = run_audit_detailed(_request_budget(repo_b, 100))  # ceiling never reached

    reader_a = ApaaStoreReader(repo_a)
    reader_b = ApaaStoreReader(repo_b)

    def _verdict_and_findings(reader, result):
        out = {"__verdict__": reader.read_bytes(result.locators[0])}
        for loc in result.locators:
            if loc.startswith("findings/"):
                out[loc] = reader.read_bytes(loc)
        return out

    vf_a = _verdict_and_findings(reader_a, res_a)
    vf_b = _verdict_and_findings(reader_b, res_b)
    assert len(vf_a) >= 2
    # The verdict + findings (content-addressed names AND bytes) match — the halt
    # mechanism does NOT change them when no halt fires (AC6).
    assert vf_a == vf_b

    # Both halt reports flag no halt + an empty skipped set.
    report_a = _halt_report_payload(reader_a, res_a)
    report_b = _halt_report_payload(reader_b, res_b)
    assert report_a["halted_on_exhaustion"] is False
    assert report_b["halted_on_exhaustion"] is False
    assert report_a["skipped_on_exhaustion_files"] == []
    assert report_b["skipped_on_exhaustion_files"] == []


# ─────────────────────────────────────────────────────────────────────────────
# Story 3.3 — INSUFFICIENT_COVERAGE floor SEMANTICS under exhaustion, end-to-end
# ─────────────────────────────────────────────────────────────────────────────


def test_e2e_below_floor_under_exhaustion_is_insufficient_coverage_exit_3(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-20 — story 3.3: a budget that skips everything → INSUFFICIENT_COVERAGE/exit 3.

    The vacuous_basic cartridge has 2 Python files (5 credits each). A budget of 1
    breaches at the very first unit → every file is SKIPPED → deep-% 0 < 20% floor →
    the UNCHANGED gate returns INSUFFICIENT_COVERAGE / exit 3 (NEVER a fabricated
    RELEASE_READY/exit 0, NEVER a misleading BLOCKED/exit 2). The exhaustion-aware
    floor report is present, below_floor=True, driven_by_exhaustion=True, and names
    the assessed deep-%.
    """
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")
    result = run_audit_detailed(_request_budget(repo, 1))

    assert result.verdict.verdict is Verdict.INSUFFICIENT_COVERAGE
    assert result.verdict.exit_code == 3
    # NEVER the lethal fabricated-ready nor the misleading block.
    assert result.verdict.verdict is not Verdict.RELEASE_READY
    assert result.verdict.verdict is not Verdict.NOT_READY_FOR_RELEASE

    floor = result.floor_report
    assert floor is not None
    assert floor.below_floor is True
    assert floor.driven_by_exhaustion is True
    assert floor.verdict == "INSUFFICIENT_COVERAGE"
    assert "no repo-wide verdict rendered (floor: 20%)" in floor.message
    assert "% deep" in floor.message


def test_e2e_above_floor_under_exhaustion_does_not_over_fire(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-21 — story 3.3: a halt that left >=20% deep gets a real release verdict.

    A budget of 6 admits the first Python file (5 < 6) then halts at the second
    (5+5=10 >= 6). 1 deep assessed / 2 total = 50% deep — at/above the 20% floor →
    the gate's NORMAL decision (NOT_READY_FOR_RELEASE, the vacuous finding still
    blocks), NOT INSUFFICIENT_COVERAGE. The floor does not over-fire on the mere
    fact of exhaustion; the floor report reflects below_floor=False.
    """
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")
    result = run_audit_detailed(_request_budget(repo, 6))

    reader = ApaaStoreReader(repo)
    report = _halt_report_payload(reader, result)
    assert report["halted_on_exhaustion"] is True
    assert report["assessed_count"] == 1  # one file admitted

    # The halt left >=20% deep → a real release verdict, NOT the floor.
    assert result.verdict.verdict is not Verdict.INSUFFICIENT_COVERAGE
    assert result.verdict.deep_ratio == Fraction(1, 2)
    floor = result.floor_report
    assert floor is not None
    assert floor.below_floor is False
    assert floor.driven_by_exhaustion is True
    assert "verdict rendered:" in floor.message


def test_e2e_non_floor_run_byte_identical_and_floor_report_neutral(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-22 — story 3.3: a non-floor run is byte-identical to 3-2; floor report neutral (AC6).

    A no-halt run (budget never reaches the ceiling) keeps the verdict / ledger /
    findings / halt-report artifacts byte-identical to a no-ceiling run (the floor
    report is exposed PURELY on the result, NOT persisted, so it changes NO bytes).
    The floor report is the neutral below_floor=False surface.
    """
    repo_a, _ = stage_cartridge("vacuous_basic", tmp_path / "a")
    repo_b, _ = stage_cartridge("vacuous_basic", tmp_path / "b")
    res_a = run_audit_detailed(_request_budget(repo_a, 0))  # no ceiling
    res_b = run_audit_detailed(_request_budget(repo_b, 100))  # ceiling never reached

    reader_a = ApaaStoreReader(repo_a)
    reader_b = ApaaStoreReader(repo_b)

    def _artifacts(reader, result):
        out = {"__verdict__": reader.read_bytes(result.locators[0])}
        for loc in result.locators:
            if loc.startswith("findings/"):
                out[loc] = reader.read_bytes(loc)
        return out

    arts_a = _artifacts(reader_a, res_a)
    arts_b = _artifacts(reader_b, res_b)
    assert arts_a == arts_b

    # Both halt reports flag no halt + an empty skipped set (the ceiling_credits
    # provenance legitimately differs by budget, as it has since 3-1/3-2).
    report_a = _halt_report_payload(reader_a, res_a)
    report_b = _halt_report_payload(reader_b, res_b)
    assert report_a["halted_on_exhaustion"] is False
    assert report_b["halted_on_exhaustion"] is False
    assert report_a["skipped_on_exhaustion_files"] == []
    assert report_b["skipped_on_exhaustion_files"] == []
    # No persisted floor-report artifact was written (the no-new-write option): the
    # 3.3 floor report adds NO new state/ artifact, so the locator count is unchanged
    # from 3-2 (the floor report is exposed PURELY on the result).
    assert len(res_a.locators) == len(res_b.locators)
    for loc in res_a.locators:
        if loc.startswith("state/"):
            payload = reader_a.read_envelope(loc).payload
            assert "below_floor" not in payload, "no floor-report artifact must be persisted"

    # The floor report is the neutral below_floor=False surface (purely additive).
    for res in (res_a, res_b):
        assert res.floor_report is not None
        assert res.floor_report.below_floor is False
        assert res.floor_report.driven_by_exhaustion is False


# ─────────────────────────────────────────────────────────────────────────────
# Story 3.4 — resumability from on-disk .argus/ state, end-to-end
# ─────────────────────────────────────────────────────────────────────────────
#
# The resume re-loads the repo at the pin to audit the remainder, so the .argus/
# store lives OUTSIDE the audited working tree (an injected writer/reader rooted in
# a separate dir) — otherwise the prior run's in-tree .argus/ would trip the loader's
# clean-tree drift check on the resume re-load. This is the V1 resume seam (the same
# injected-store pattern TC-...-08 uses). The carried-forward work is reused from the
# on-disk LEDGER (NOT a memo cache — that is Epic 5).


def _store(tmp_path: Path, name: str) -> tuple[ApaaStoreWriter, ApaaStoreReader]:
    root = tmp_path / name
    root.mkdir()
    return ApaaStoreWriter(root), ApaaStoreReader(root)


def _run_state_ledger_bytes(reader: ApaaStoreReader, result) -> bytes:
    """The bytes of the persisted run-state envelope carrying the coverage ledger."""
    for loc in result.locators:
        if not loc.startswith("state/"):
            continue
        payload = reader.read_envelope(loc).payload
        if isinstance(payload.get("ledger"), dict):
            return reader.read_bytes(loc)
    raise AssertionError("no persisted run-state with a ledger found")


def _halt_report_bytes(reader: ApaaStoreReader, result) -> bytes:
    """The on-disk bytes of the single persisted halt-report snapshot."""
    for loc in result.locators:
        if not loc.startswith("state/"):
            continue
        payload = reader.read_envelope(loc).payload  # re-verifies content_hash
        if "halted_on_exhaustion" in payload:
            return reader.read_bytes(loc)
    raise AssertionError("no persisted halt report found")


# The PLANTED VACUOUS TEST content (copied from the vacuous_basic cartridge's
# tests/test_calculator.py) — graded ``audited_shallow`` by the 1.5 vacuous detector.
_VACUOUS_TEST_SRC = '''\
"""A vacuous test that sorts into the assessed prefix (keystone regression fixture)."""

from unittest.mock import Mock

from src.calculator import compute_total


def test_compute_total_is_vacuous():
    compute_total([1, 2, 3])
    fake = Mock()
    fake.calculate.return_value = 6
    pretended = fake.calculate()
    assert pretended == 6
'''


def _stage_with_assessed_prefix_non_deep_file(dest: Path) -> Path:
    """Stage ``vacuous_basic`` + an ``aaa_test.py`` that sorts FIRST (into the assessed prefix).

    ``aaa_test.py`` (a test file → ``audited_shallow``) sorts before ``src/calculator.py``
    (deep). With ``halt(6)`` it is admitted (5 < 6) and the run halts at the deep file —
    so a NON-``audited_deep`` file lands in the ASSESSED prefix. This is the fixture the
    code-review demanded: it goes RED on the old ``audited_deep``-only carry-forward
    (``aaa_test.py`` would be silently dropped from the resumed ledger), and green on the
    carry-forward-every-assessed-path fix.
    """
    import subprocess

    repo, _sha = stage_cartridge("vacuous_basic", dest)
    (repo / "aaa_test.py").write_text(_VACUOUS_TEST_SRC, encoding="utf-8")
    (repo / ".gitignore").write_text(".argus/\n", encoding="utf-8")
    # Re-commit so load_repo_at_commit sees a clean working tree at HEAD (story 1.4).
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "add assessed-prefix non-deep file"],
        check=True,
        capture_output=True,
    )
    return repo



def test_e2e_resume_identity_with_assessed_prefix_non_deep_file(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-30 — story 3.4 (AC2 KEYSTONE / NFR-R2): no loss of assessed-non-deep coverage.

    The RED-then-green regression for the iteration-1 review High finding. A NON-deep
    file (``aaa_test.py`` → ``audited_shallow``) sorts into the ASSESSED prefix of the
    prior ``halt(6)``. The OLD ``audited_deep``-only carry-forward silently DROPPED it
    (resumed ledger 3 entries / ``deep_ratio 2/3`` vs uninterrupted 4 entries /
    ``deep_ratio 1/2``). The fix carries forward EVERY assessed path, so ``halt(6) →
    resume(100)`` is BYTE-IDENTICAL to a single uninterrupted ``run(100)`` — including
    the persisted HALT-REPORT bytes (which the prior keystone never compared).
    """
    repo_hr = _stage_with_assessed_prefix_non_deep_file(tmp_path / "hr")
    w_hr, r_hr = _store(tmp_path, "store_hr")
    halt = run_audit_detailed(_request_budget(repo_hr, 6), store_writer=w_hr)  # halt + persist
    halt_report = _halt_report_payload(r_hr, halt)
    # PRECONDITION: a non-deep file IS in the assessed prefix (the fixture is valid).
    assert "aaa_test.py" in halt_report["assessed_files"]
    assert "src/calculator.py" in halt_report["skipped_on_exhaustion_files"]

    resumed = resume_audit_detailed(
        _request_budget(repo_hr, 100), store_reader=r_hr, store_writer=w_hr
    )

    repo_u = _stage_with_assessed_prefix_non_deep_file(tmp_path / "u")
    w_u, r_u = _store(tmp_path, "store_u")
    uninterrupted = run_audit_detailed(_request_budget(repo_u, 100), store_writer=w_u)

    # Identical verdict surface (deep_ratio / counts denominator must NOT drift).
    assert resumed.verdict.verdict is uninterrupted.verdict.verdict
    assert resumed.verdict.exit_code == uninterrupted.verdict.exit_code
    assert resumed.verdict.deep_ratio == uninterrupted.verdict.deep_ratio
    assert resumed.verdict.counts_by_depth == uninterrupted.verdict.counts_by_depth

    # The dropped-coverage proof: the resumed ledger must carry the shallow assessed file.
    resumed_ledger = None
    for loc in resumed.locators:
        if not loc.startswith("state/"):
            continue
        payload = r_hr.read_envelope(loc).payload
        if isinstance(payload.get("ledger"), dict):
            resumed_ledger = payload["ledger"]
    assert resumed_ledger is not None
    depths = {e["file_path"]: e["depth"] for e in resumed_ledger["entries"]}
    assert depths.get("aaa_test.py") == "audited_shallow"  # carried forward, NOT dropped

    # Byte-identical persisted verdict (content-addressed name AND bytes).
    assert resumed.locators[0] == uninterrupted.locators[0]
    assert r_hr.read_bytes(resumed.locators[0]) == r_u.read_bytes(uninterrupted.locators[0])
    # Byte-identical persisted coverage ledger.
    assert _run_state_ledger_bytes(r_hr, resumed) == _run_state_ledger_bytes(r_u, uninterrupted)
    # Byte-identical persisted HALT-REPORT (Decision #3 — _resumed_halt_report parity).
    assert _halt_report_bytes(r_hr, resumed) == _halt_report_bytes(r_u, uninterrupted)


def test_e2e_resume_reuses_prior_coverage_and_audits_only_remainder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TC-ArgusAgent-PIPELINE-001-23 — story 3.4 (AC1): resume reuses prior audited_deep; detector runs ONLY on the remainder.

    halt(6) admits one Python file (5<6) + skips the other (5+5>=6). The resume(100)
    carries the prior audited_deep file forward VERBATIM and runs ``_detect_per_file``
    ONLY over the skipped remainder (proven by spying on the detect call's entries) —
    never re-auditing the carried-forward file (NFR-R2 affordability win).
    """
    repo, _ = stage_cartridge("vacuous_basic", tmp_path / "repo")
    writer, reader = _store(tmp_path, "store")
    halt = run_audit_detailed(_request_budget(repo, 6), store_writer=writer)
    halt_report = _halt_report_payload(reader, halt)
    carried = list(halt_report["assessed_files"])
    remainder = list(halt_report["skipped_on_exhaustion_files"])
    assert carried and remainder  # a genuine partial halt

    # Spy on _detect_per_file to capture the entries it is invoked over.
    import argus.pipeline as pipeline_mod

    detected_paths: list[str] = []
    real_detect = pipeline_mod._detect_per_file

    def _spy(repo_root, index_entries):
        detected_paths.extend(e.file_path for e in index_entries)
        return real_detect(repo_root, index_entries)

    monkeypatch.setattr(pipeline_mod, "_detect_per_file", _spy)
    resumed = resume_audit_detailed(
        _request_budget(repo, 100), store_reader=reader, store_writer=writer
    )

    # The detector was invoked ONLY for the remainder — never the carried-forward set.
    assert sorted(detected_paths) == sorted(remainder)
    for path in carried:
        assert path not in detected_paths

    # The carried-forward audited_deep entry is present in the resumed ledger.
    resumed_ledger = None
    for loc in resumed.locators:
        if not loc.startswith("state/"):
            continue
        payload = reader.read_envelope(loc).payload
        if isinstance(payload.get("ledger"), dict):
            resumed_ledger = payload["ledger"]
    assert resumed_ledger is not None
    depths = {e["file_path"]: e["depth"] for e in resumed_ledger["entries"]}
    for path in carried:
        assert depths[path] == "audited_deep"


def test_e2e_resume_reaches_identical_verdict_and_ledger_as_uninterrupted_run(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-PIPELINE-001-24 — story 3.4 (AC2 KEYSTONE): halt→resume is BYTE-IDENTICAL to run(B2).

    The repo audited as ``halt(6)`` THEN ``resume(100)`` produces a final verdict +
    coverage-ledger BYTE-IDENTICAL (content-addressed NAMES and on-disk BYTES) to a
    single uninterrupted ``run(100)`` — resume does NOT change the answer (FR31/NFR-R2).
    """
    repo_hr, _ = stage_cartridge("vacuous_basic", tmp_path / "hr")
    w_hr, r_hr = _store(tmp_path, "store_hr")
    run_audit_detailed(_request_budget(repo_hr, 6), store_writer=w_hr)  # halt + persist
    resumed = resume_audit_detailed(
        _request_budget(repo_hr, 100), store_reader=r_hr, store_writer=w_hr
    )

    repo_u, _ = stage_cartridge("vacuous_basic", tmp_path / "u")
    w_u, r_u = _store(tmp_path, "store_u")
    uninterrupted = run_audit_detailed(_request_budget(repo_u, 100), store_writer=w_u)

    # Identical verdict object surface.
    assert resumed.verdict.verdict is uninterrupted.verdict.verdict
    assert resumed.verdict.exit_code == uninterrupted.verdict.exit_code
    assert resumed.verdict.deep_ratio == uninterrupted.verdict.deep_ratio
    assert resumed.verdict.counts_by_depth == uninterrupted.verdict.counts_by_depth

    # Byte-identical persisted verdict (content-addressed name AND bytes).
    assert resumed.locators[0] == uninterrupted.locators[0]
    assert r_hr.read_bytes(resumed.locators[0]) == r_u.read_bytes(uninterrupted.locators[0])

    # Byte-identical persisted coverage ledger (the run-state envelope).
    assert _run_state_ledger_bytes(r_hr, resumed) == _run_state_ledger_bytes(r_u, uninterrupted)

    # Byte-identical persisted HALT-REPORT (Decision #3 — the resumed halt report is
    # re-projected over the full current index, so its assessed_files/assessed_count/
    # total_credits match the uninterrupted run for ALL assessed depths).
    assert _halt_report_bytes(r_hr, resumed) == _halt_report_bytes(r_u, uninterrupted)

    # Byte-identical findings set.
    def _findings(reader, result):
        return {
            loc: reader.read_bytes(loc)
            for loc in result.locators
            if loc.startswith("findings/")
        }

    assert _findings(r_hr, resumed) == _findings(r_u, uninterrupted)


def test_e2e_tamper_on_resume_raises_never_silent_wrong_resume(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-25 — story 3.4 (AC3 / AI-E1-1): a mutated state byte → ResumeStateError/exit 1.

    A persisted ``state/`` payload mutated WITHOUT recomputing its envelope
    content_hash makes the resume RAISE a typed ``ResumeStateError`` (via the 1-3
    ``StoreIntegrityError`` tamper guard, REUSED) → exit 1 — it NEVER silently resumes
    from the corrupted state, NEVER fabricates a verdict, NEVER falls back to a fresh
    run. The message names only the relative locator (no abs-path/source/secret byte).
    """
    import json

    repo, _ = stage_cartridge("vacuous_basic", tmp_path / "repo")
    writer, reader = _store(tmp_path, "store")
    halt = run_audit_detailed(_request_budget(repo, 6), store_writer=writer)

    # Mutate the run-state payload byte without recomputing the content_hash.
    state_dir = reader.paths.resolve("state")
    mutated = False
    for f in sorted(state_dir.glob("*.json")):
        raw = json.loads(f.read_text(encoding="utf-8"))
        payload = raw.get("payload")
        if isinstance(payload, dict) and isinstance(payload.get("ledger"), dict):
            payload["exit_code"] = 999  # tamper (stale content_hash)
            f.write_text(json.dumps(raw), encoding="utf-8")
            mutated = True
            break
    assert mutated, "expected a run-state payload to mutate"

    with pytest.raises(ResumeStateError) as exc:
        resume_audit_detailed(
            _request_budget(repo, 100), store_reader=reader, store_writer=writer
        )
    # ResumeStateError is a PipelineError (a ValueError) → the CLI maps it to exit 1.
    assert isinstance(exc.value, PipelineError)
    msg = str(exc.value)
    assert "/home/" not in msg and "C:\\" not in msg
    assert str(repo) not in msg  # no absolute host path leak


def test_e2e_unknown_field_state_raises_typed_resume_error(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-26 — story 3.4 (AC3): an unknown-field state payload → typed ResumeStateError.

    An unknown field in the persisted halt-report payload (extra='forbid') makes the
    resume RAISE a typed ``ResumeStateError`` (via pydantic ValidationError), never a
    fabricated resume. (The content_hash is recomputed here so the integrity check
    PASSES and the validation layer is the one that rejects — proving the unknown-field
    path is covered independently of the tamper path.)
    """
    import json

    from argus.store import canonical
    from argus.store.envelope import compute_content_hash

    repo, _ = stage_cartridge("vacuous_basic", tmp_path / "repo")
    writer, reader = _store(tmp_path, "store")
    run_audit_detailed(_request_budget(repo, 6), store_writer=writer)

    state_dir = reader.paths.resolve("state")
    mutated = False
    for f in sorted(state_dir.glob("*.json")):
        raw = json.loads(f.read_text(encoding="utf-8"))
        payload = raw.get("payload")
        if isinstance(payload, dict) and "halted_on_exhaustion" in payload:
            payload["bogus_unknown_field"] = "x"
            raw["payload"] = payload
            raw["content_hash"] = compute_content_hash(payload)  # keep integrity valid
            f.write_bytes(canonical.dumps_bytes(raw))
            mutated = True
            break
    assert mutated, "expected a halt-report payload to mutate"

    with pytest.raises(ResumeStateError):
        resume_audit_detailed(
            _request_budget(repo, 100), store_reader=reader, store_writer=writer
        )


def test_e2e_no_prior_state_raises_typed_resume_error(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-27 — story 3.4 (AC1): resuming with NO prior state → typed ResumeStateError.

    A resume invocation against an empty ``.argus/`` store RAISES a typed
    ``ResumeStateError`` (the locked no-silent-empty-resume choice) — never a silent
    empty/fabricated resume, never a silent fresh run.
    """
    repo, _ = stage_cartridge("vacuous_basic", tmp_path / "repo")
    writer, reader = _store(tmp_path, "store")
    with pytest.raises(ResumeStateError):
        resume_audit_detailed(
            _request_budget(repo, 100), store_reader=reader, store_writer=writer
        )


def test_e2e_chained_partial_then_complete_resume_reaches_identity(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-28 — story 3.4 (AC4): halt → resume(partial) → resume(complete) == run(B2).

    A first resume whose RAISED budget still cannot cover the whole remainder halts
    AGAIN honestly (the still-skipped remainder stays SKIPPED, halted_on_exhaustion=True
    with the shrunken skipped set). A follow-on resume that finally covers the rest
    reaches the SAME final verdict + ledger a single uninterrupted run would (AC2
    transitively) — proven by comparing the final bytes to a single run(100).

    The clean_control cartridge has 3 Python files (5 credits each = 15 total). A
    budget of 6 admits 1; resume(11) admits 1 more (still short → halts again);
    resume(100) covers the rest.
    """
    repo, _ = stage_cartridge("clean_control", tmp_path / "repo")
    writer, reader = _store(tmp_path, "store")

    run_audit_detailed(_request_budget(repo, 6), store_writer=writer)  # admits 1
    # First resume: B2=11 → prior 5 + one more 5 = 10 < 11; + next 5 = 15 >= 11 → halts again.
    partial = resume_audit_detailed(
        _request_budget(repo, 11), store_reader=reader, store_writer=writer
    )
    partial_report = _halt_report_payload(reader, partial)
    assert partial_report["halted_on_exhaustion"] is True
    assert partial_report["skipped_on_exhaustion_count"] >= 1

    # Second resume: B2=100 covers the rest.
    final = resume_audit_detailed(
        _request_budget(repo, 100), store_reader=reader, store_writer=writer
    )

    # Compare to a single uninterrupted run(100).
    repo_u, _ = stage_cartridge("clean_control", tmp_path / "u")
    w_u, r_u = _store(tmp_path, "store_u")
    uninterrupted = run_audit_detailed(_request_budget(repo_u, 100), store_writer=w_u)

    assert final.locators[0] == uninterrupted.locators[0]
    assert reader.read_bytes(final.locators[0]) == r_u.read_bytes(uninterrupted.locators[0])
    assert _run_state_ledger_bytes(reader, final) == _run_state_ledger_bytes(r_u, uninterrupted)
    assert final.verdict.verdict is uninterrupted.verdict.verdict


def test_e2e_no_resume_run_is_byte_identical_to_3_3(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-29 — story 3.4 (AC6): a normal (non-resume) run is byte-identical to pre-3.4.

    The resume entrypoint is purely additive: a plain ``run_audit_detailed`` (no
    resume) produces verdict/ledger/findings/halt-report artifacts byte-identical
    across two runs (the regression-safe keystone — resume changed NO existing path,
    added NO field to AuditRequest, changed NO verdict math).
    """
    repo_a, _ = stage_cartridge("vacuous_basic", tmp_path / "a")
    repo_b, _ = stage_cartridge("vacuous_basic", tmp_path / "b")
    w_a, r_a = _store(tmp_path, "store_a")
    w_b, r_b = _store(tmp_path, "store_b")
    res_a = run_audit_detailed(_request_budget(repo_a, 100), store_writer=w_a)
    res_b = run_audit_detailed(_request_budget(repo_b, 100), store_writer=w_b)

    # Same locator count + byte-identical verdict / findings / halt-report / ledger.
    assert len(res_a.locators) == len(res_b.locators)
    assert res_a.locators[0] == res_b.locators[0]
    assert r_a.read_bytes(res_a.locators[0]) == r_b.read_bytes(res_b.locators[0])
    assert _run_state_ledger_bytes(r_a, res_a) == _run_state_ledger_bytes(r_b, res_b)
    assert _halt_report_payload(r_a, res_a) == _halt_report_payload(r_b, res_b)


# ─────────────────────────────────────────────────────────────────────────────
# Story 4.1 — negative-assurance verdict WRAPPER + critical-set persistence, e2e
# ─────────────────────────────────────────────────────────────────────────────
#
# The wrapper is built in the SHARED _assemble_and_persist fold both the fresh and
# resume paths run, so a resumed run's wrapper is byte-identical to an uninterrupted
# run's (the 3.4 keystone applied to the new surface). The wrapper + the computed
# CriticalSubsystemSet are PURELY ADDITIVE new state/ artifacts.

_NEGATIVE_ASSURANCE_PRODUCER = "argus.verdict.negative_assurance"
_CRITICAL_SUBSYSTEMS_PRODUCER = "argus.pipeline.critical_subsystems"

_NA_FORBIDDEN_PHRASES = (
    "certif",
    "is correct",
    "proven",
    "guarantee",
    "defect-free",
    "bug-free",
    "passed",
)


def _na_payload(reader: ApaaStoreReader, result) -> dict:
    """Find the single persisted negative-assurance wrapper among the state/ locators."""
    payloads = []
    for loc in result.locators:
        if not loc.startswith("state/"):
            continue
        envelope = reader.read_envelope(loc)  # re-verifies content_hash
        if envelope.producer == _NEGATIVE_ASSURANCE_PRODUCER:
            payloads.append(envelope.payload)
    assert len(payloads) == 1, "expected exactly one persisted negative-assurance wrapper"
    return payloads[0]


def _na_locator(result) -> str:
    for loc in result.locators:
        if loc.startswith("state/"):
            return loc
    raise AssertionError("no state/ locator")


def _critical_payload(reader: ApaaStoreReader, result) -> dict:
    payloads = []
    for loc in result.locators:
        if not loc.startswith("state/"):
            continue
        envelope = reader.read_envelope(loc)
        if envelope.producer == _CRITICAL_SUBSYSTEMS_PRODUCER:
            payloads.append(envelope.payload)
    assert len(payloads) == 1, "expected exactly one persisted critical-subsystem set"
    return payloads[0]


@pytest.mark.parametrize(
    "cartridge, budget, expected_verdict",
    [
        ("clean_control", 100, "RELEASE_READY"),
        ("vacuous_basic", 100, "NOT_READY_FOR_RELEASE"),
        ("vacuous_basic", 1, "INSUFFICIENT_COVERAGE"),
    ],
)
def test_e2e_negative_assurance_present_no_over_claim_all_three_verdicts(
    tmp_path: Path, cartridge: str, budget: int, expected_verdict: str
) -> None:
    """TC-ArgusAgent-PIPELINE-001-31 — story 4.1 (AC1/AC2): wrapper present + no over-claim, all three verdicts."""
    repo, _ = stage_cartridge(cartridge, tmp_path / "repo")
    result = run_audit_detailed(_request_budget(repo, budget))
    assert result.verdict.verdict.value == expected_verdict
    assert result.negative_assurance is not None
    assert result.negative_assurance.verdict == expected_verdict

    reader = ApaaStoreReader(repo)
    na = _na_payload(reader, result)
    assert na["verdict"] == expected_verdict
    assert na["materiality_bar"] == "default"
    assert "scope_statement" in na and "disclaimer" in na
    assert "assurance_statement" in na

    # No over-claim anywhere in the serialized wrapper (the AC2 forbidden-phrase scan).
    from argus.store import canonical as _canon

    text = _canon.dumps(na).lower()
    for phrase in _NA_FORBIDDEN_PHRASES:
        assert phrase not in text, f"{expected_verdict} wrapper over-claims: {phrase!r}"


def test_e2e_critical_subsystem_set_is_persisted(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-32 — story 4.1 (AC4 / DF-2-3-B): the computed CriticalSubsystemSet persists.

    Forcing a shallow test file critical produces a non-empty computed set; it is
    persisted to state/ with its paths + per-path origins + designated_but_unmatched,
    so the scope statement's critical narration is auditable from disk.
    """
    repo, _ = stage_cartridge("clean_control", tmp_path / "repo")
    result = run_audit_detailed(
        _request_with_designation(repo, critical=("tests/test_math.py",))
    )
    reader = ApaaStoreReader(repo)
    crit = _critical_payload(reader, result)
    assert "tests/test_math.py" in crit["paths"]
    assert crit["origins"]["tests/test_math.py"] == "operator_designated"
    # The wrapper's scope statement names the critical-not-deep file.
    na = _na_payload(reader, result)
    assert "tests/test_math.py" in na["scope_statement"]["critical_not_examined_deep"]


def test_e2e_designated_but_unmatched_persisted_and_narrated(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-33 — story 4.1 (AC4): a designated-but-unmatched critical path is persisted + narrated."""
    repo, _ = stage_cartridge("clean_control", tmp_path / "repo")
    result = run_audit_detailed(
        _request_with_designation(repo, critical=("nonexistent/ghost.py",))
    )
    reader = ApaaStoreReader(repo)
    crit = _critical_payload(reader, result)
    assert "nonexistent/ghost.py" in crit["designated_but_unmatched"]
    na = _na_payload(reader, result)
    scope = na["scope_statement"]
    assert "nonexistent/ghost.py" in scope["critical_designated_but_unmatched"]
    assert "nonexistent/ghost.py" in scope["critical_not_examined_deep"]


def test_e2e_existing_verdict_findings_bytes_unchanged_by_4_1(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-34 — story 4.1 (AC6): the wrapper + critical set are PURELY additive.

    The verdict + findings + ledger + halt-report artifacts are byte-identical across
    two runs; the new artifacts add to the locator count but never alter existing bytes.
    """
    repo_a, _ = stage_cartridge("vacuous_basic", tmp_path / "a")
    repo_b, _ = stage_cartridge("vacuous_basic", tmp_path / "b")
    res_a = run_audit_detailed(_request_budget(repo_a, 100))
    res_b = run_audit_detailed(_request_budget(repo_b, 100))
    reader_a = ApaaStoreReader(repo_a)
    reader_b = ApaaStoreReader(repo_b)

    # The verdict envelope (locators[0]) bytes are byte-identical.
    assert res_a.locators[0] == res_b.locators[0]
    assert reader_a.read_bytes(res_a.locators[0]) == reader_b.read_bytes(res_b.locators[0])
    # The findings bytes are byte-identical.
    fnd_a = {loc: reader_a.read_bytes(loc) for loc in res_a.locators if loc.startswith("findings/")}
    fnd_b = {loc: reader_b.read_bytes(loc) for loc in res_b.locators if loc.startswith("findings/")}
    assert fnd_a == fnd_b
    # The new wrapper + critical-set artifacts are present in both runs (additive).
    assert _na_payload(reader_a, res_a) == _na_payload(reader_b, res_b)
    assert _critical_payload(reader_a, res_a) == _critical_payload(reader_b, res_b)


def test_e2e_fresh_vs_resumed_wrapper_byte_identical(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-35 — story 4.1 (AC6 KEYSTONE): the wrapper is byte-identical fresh-vs-resumed.

    The fixture has a NON-deep file (aaa_test.py → audited_shallow) in the ASSESSED
    prefix of halt(6) (the exact 3.4 mask). The wrapper is built in the SHARED
    _assemble_and_persist fold both paths run, so halt(6)→resume(100) produces a
    BYTE-IDENTICAL negative-assurance wrapper to a single uninterrupted run(100).
    Demonstrated RED if the wrapper depended on input order: were the scope counts
    derived from an order-dependent source, the resumed (carry-forward-merged) and
    uninterrupted ledgers would diverge — but both fold the SAME re-sorted ledger.
    """
    repo_hr = _stage_with_assessed_prefix_non_deep_file(tmp_path / "hr")
    w_hr, r_hr = _store(tmp_path, "store_hr")
    halt = run_audit_detailed(_request_budget(repo_hr, 6), store_writer=w_hr)
    halt_report = _halt_report_payload(r_hr, halt)
    # PRECONDITION (the 3.4 mask): a non-deep file IS in the assessed prefix.
    assert "aaa_test.py" in halt_report["assessed_files"]

    resumed = resume_audit_detailed(
        _request_budget(repo_hr, 100), store_reader=r_hr, store_writer=w_hr
    )

    repo_u = _stage_with_assessed_prefix_non_deep_file(tmp_path / "u")
    w_u, r_u = _store(tmp_path, "store_u")
    uninterrupted = run_audit_detailed(_request_budget(repo_u, 100), store_writer=w_u)

    # The in-memory wrapper is equal.
    assert resumed.negative_assurance == uninterrupted.negative_assurance
    # The persisted wrapper bytes are byte-identical (content-addressed name + bytes).
    na_loc_resumed = _na_wrapper_locator(r_hr, resumed)
    na_loc_uninterrupted = _na_wrapper_locator(r_u, uninterrupted)
    assert na_loc_resumed == na_loc_uninterrupted
    assert r_hr.read_bytes(na_loc_resumed) == r_u.read_bytes(na_loc_uninterrupted)


def _na_wrapper_locator(reader: ApaaStoreReader, result) -> str:
    for loc in result.locators:
        if not loc.startswith("state/"):
            continue
        if reader.read_envelope(loc).producer == _NEGATIVE_ASSURANCE_PRODUCER:
            return loc
    raise AssertionError("no negative-assurance wrapper locator")


def test_e2e_wrapper_scope_statement_reflects_real_coverage(tmp_path: Path) -> None:
    """TC-ArgusAgent-PIPELINE-001-36 — story 4.1 (AC1/AC3): the scope triad reflects the real ledger counts."""
    repo, _ = stage_cartridge("vacuous_basic", tmp_path / "repo")
    result = run_audit_detailed(_request_budget(repo, 100))
    reader = ApaaStoreReader(repo)
    na = _na_payload(reader, result)
    scope = na["scope_statement"]
    counts = result.verdict.counts_by_depth
    from argus.ledger.coverage_ledger import CoverageDepth as _CD

    assert scope["examined_deep"] == counts[_CD.AUDITED_DEEP]
    assert scope["sampled_shallow"] == counts[_CD.AUDITED_SHALLOW]
    assert scope["not_covered_skipped"] == counts[_CD.SKIPPED]
    assert scope["total_count"] == result.verdict.total_count
