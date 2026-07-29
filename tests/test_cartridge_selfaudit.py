"""Story 6.5 — the defect-cartridge self-audit harness (FR20 measurement substrate).

Verification area ArgusAgent-CARTRIDGE (``TC-ArgusAgent-CARTRIDGE-001-NN`` — this is the FIRST
file in that area; the index starts at 01). Drivers: ArgusAgent-FR-20 (ArgusAgent validates its
own detectors against defect cartridges with golden expected-findings keys, asserted
in CI), ArgusAgent-FR-13 (every emitted finding carries >=1 verifiable locator — a
locator-less finding is rejected, not emitted), ArgusAgent-NFR-D1/D2 (the cartridge audits
are deterministic + zero-LLM-token — the V1 pipeline calls NO LLM), ArgusAgent-NFR-P1 (each
cartridge audited twice -> byte-identical verdict envelope ``content_hash``),
ArgusAgent-NFR-S1 (no source/secret byte from any cartridge in any read surface — flows
through the 4.4 randomized-canary suite), ArgusAgent-AR9 (committed / durable CI gate under
the existing ArgusAgent pytest invocation — no new CI job), ArgusAgent-AR10 / NFR-R1 (the
no-crash cartridge row: an honest-degradation input degrades to a typed verdict,
never an uncaught crash — AI-E4-2 mechanized as a cartridge), ArgusAgent-NFR-M1/M2
(<=1200-line files; frozen Epic-1..6 contracts unchanged — this harness COMPOSES
them, edits none).

What this harness IS (partial-reuse note, AI-E5-7)
--------------------------------------------------
It REUSES, by import, the LOCKED substrate: ``stage_cartridge`` (the 1.7 fresh-
single-commit cartridge-pinning helper), ``run_audit_detailed`` (the deterministic
zero-token V1 pipeline), and ``ApaaStoreReader`` (the tamper-guard reader). It ADDS a
parametrized cartridge REGISTRY (``cartridges/_registry.py``) carrying per-cartridge
golden expected-findings keys + a mechanized ``PRECISION_GATE_STATUS`` marker. It
GENERALIZES the ``test_pipeline_signature_demo.py`` stage->audit->assert pattern over
the whole corpus — it adds NO parallel pipeline runner and NO new detector (s3.3).

THE OI1 LOCK (the central honesty constraint — read the registry docstring)
---------------------------------------------------------------------------
N is LOCKED at 5; populated phased 3->5; precision measured over FINDINGS not repos;
the >=80%-precision gate is PROVISIONAL below N=5. This harness computes NO precision
NUMBER (that is Story 6.6) — it asserts the true-positive / true-negative PROPERTIES
+ the committed provisional-gate marker. Do NOT overclaim a precision number from too
few cartridges (honest coverage is ArgusAgent's whole thesis).

The complete-the-declared-set matrix (AI-E5-1 / AI-E4-2 / AR10), each covered below:
  (1) golden-key true positive per planted-defect cartridge (vacuous / secret / orphan)
  (2) clean-control true negative — ANY blocking 🔴 is an instant CI fail
  (3) hidden holdout — caught with NO detector change (overfitting defense)
  (4) false-negative / citation-gaming trap — a naive/gamed detector fails
  (5) determinism + secret-containment + non-ASCII over the corpus
  (6) >=1 no-crash cartridge row (AI-E4-2: degrades to a typed verdict, never a crash)
Every assertion NAMES the cartridge id (the AI-E5-1 no-crash leg — a clear NAMED
failure, never an opaque traceback).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))

from _cartridge import stage_cartridge  # noqa: E402
from _registry import (  # noqa: E402
    CARTRIDGE_REGISTRY,
    PRECISION_GATE_STATUS,
    VALIDATION_SET_FLOOR_N,
    CartridgeSpec,
    populated_planted_defect_count,
)

from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit_detailed  # noqa: E402
from argus.store.reader import ApaaStoreReader  # noqa: E402
from argus.verdict.verdict_gate import Verdict  # noqa: E402

# ── Source/secret bytes planted in the cartridges that MUST NOT leak into any read
# surface the harness inspects (NFR-S1 producer guarantee). These mirror the 4.4
# randomized-canary suite's fixed cartridge canaries; the harness re-asserts them on
# the secret-bearing rows it audits so containment is co-located with the cartridge
# self-audit (the 4.4 suite remains the CI-blocking randomized property gate).
_PLANTED_SECRET_BYTES: tuple[str, ...] = (
    "PLANTEDxAbCdEfGhIjKlMnOpQrStUvWxYz012345",  # hardcoded_secret / evidence_sentinel AWS
    "пароль_секрет_значение_PLANTED_1234567",  # hardcoded_secret non-ASCII token
    "EVIDENCE_SENTINEL_zXqW7vKpLmNrTaBcDeF1234567890ABCDEF",  # evidence_sentinel source sentinel
    "marker-only-distinctive-source-byte",  # evidence_sentinel / hardcoded source-byte
)

_IDS = [spec.cartridge_id for spec in CARTRIDGE_REGISTRY]


def _request(repo: Path, commit: str = "HEAD") -> AuditRequest:
    return AuditRequest(
        repo_path=str(repo), commit=commit, budget=100, materiality_bar="default"
    )


def _audit(spec: CartridgeSpec, dest: Path):
    """Stage + audit a cartridge; a staging/audit failure becomes a NAMED assertion.

    AI-E5-1 no-crash leg: a missing cartridge id / git failure / pipeline raise is
    re-raised as an ``AssertionError`` citing the cartridge id, never a bare
    traceback that hides WHICH cartridge failed.
    """
    try:
        repo, _sha = stage_cartridge(spec.cartridge_id, dest)
    except Exception as exc:  # noqa: BLE001 — convert to a NAMED failure
        raise AssertionError(
            f"cartridge {spec.cartridge_id!r}: staging failed ({type(exc).__name__}: {exc})"
        ) from exc
    try:
        result = run_audit_detailed(_request(repo))
    except Exception as exc:  # noqa: BLE001 — convert to a NAMED failure
        raise AssertionError(
            f"cartridge {spec.cartridge_id!r}: audit raised "
            f"{type(exc).__name__}: {exc} (expected a typed verdict, never a crash)"
        ) from exc
    return repo, result


def _emitted_keys(result) -> set[tuple[str, bool, bool]]:
    """The SET of (rule_id, verdict_eligible, advisory) tuples the audit emitted."""
    return {
        (f.rule_id, f.depth_supported is not None, f.advisory)
        for f in result.verdict.ordered_findings
    }


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — the parametrized registry is the mechanically-iterated source of truth
# ─────────────────────────────────────────────────────────────────────────────


def test_registry_shape_designed_for_n5() -> None:
    """TC-ArgusAgent-CARTRIDGE-001-01 — AC1: the registry is a frozen, well-formed, N=5-shaped set."""
    assert CARTRIDGE_REGISTRY, "the cartridge registry must be non-empty"
    # The declared set covers every member kind (AC8 (1)-(6)).
    kinds = {spec.kind for spec in CARTRIDGE_REGISTRY}
    assert {"planted_defect", "clean_control", "holdout", "trap", "no_crash"} <= kinds
    # Ids are unique (a NEW cartridge is a NEW row, never a silent overwrite).
    assert len(_IDS) == len(set(_IDS))
    # The registry is shaped for the locked N=5 floor.
    assert VALIDATION_SET_FLOOR_N == 5
    # Golden keys are SETS of (rule_id, bool, bool) — never counts, never source bytes.
    for spec in CARTRIDGE_REGISTRY:
        for gf in spec.required_findings:
            assert isinstance(gf.rule_id, str) and gf.rule_id
            assert isinstance(gf.verdict_eligible, bool)
            assert isinstance(gf.advisory, bool)


# ─────────────────────────────────────────────────────────────────────────────
# AC2 / AC4 / AC5 — golden-key true positives (planted_defect / holdout / trap),
# each emitted finding carries a verifiable locator (FR13), verdict/exit/order match
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "spec",
    [s for s in CARTRIDGE_REGISTRY if s.kind in ("planted_defect", "holdout", "trap")],
    ids=lambda s: s.cartridge_id,
)
def test_golden_key_true_positive(spec: CartridgeSpec, tmp_path: Path) -> None:
    """TC-ArgusAgent-CARTRIDGE-001-02 — AC2/AC4/AC5/FR13: each planted defect hits its golden key.

    Covers planted_defect (AC2 — vacuous/secret/orphan), holdout (AC4 — caught with NO
    detector change, the overfitting defense), and trap (AC5 — a citation-gaming
    surface whose only finding is the advisory redacted-secret, NOT a blocking false
    accusation). Each REQUIRED golden finding is present, carries >=1 verifiable
    locator (a locator-less finding would have been rejected, not emitted — FR13), and
    the value-free contract holds.
    """
    _repo, result = _audit(spec, tmp_path / "repo")
    emitted = _emitted_keys(result)

    for gf in spec.required_findings:
        key = (gf.rule_id, gf.verdict_eligible, gf.advisory)
        assert key in emitted, (
            f"cartridge {spec.cartridge_id!r}: missing golden finding {key} "
            f"(emitted: {sorted(emitted)})"
        )
        matching = [
            f
            for f in result.verdict.ordered_findings
            if f.rule_id == gf.rule_id
            and (f.depth_supported is not None) == gf.verdict_eligible
            and f.advisory == gf.advisory
        ]
        for finding in matching:
            assert len(finding.locators) >= 1, (
                f"cartridge {spec.cartridge_id!r}: {gf.rule_id} finding has no locator (FR13)"
            )
            for loc in finding.locators:
                assert loc.start_line >= 1
                assert loc.file_path  # a verifiable path, not empty

    # Verdict + exit match the locked golden expectation (NAMED on failure).
    assert result.verdict.verdict.value == spec.expected_verdict, (
        f"cartridge {spec.cartridge_id!r}: verdict "
        f"{result.verdict.verdict.value} != {spec.expected_verdict}"
    )
    assert result.verdict.exit_code == spec.expected_exit, (
        f"cartridge {spec.cartridge_id!r}: exit {result.verdict.exit_code} != {spec.expected_exit}"
    )

    # FR33 ordering: when a blocking finding is expected it sorts strictly first.
    if spec.first_finding_rule_id is not None:
        first = result.verdict.ordered_findings[0]
        assert first.rule_id == spec.first_finding_rule_id, (
            f"cartridge {spec.cartridge_id!r}: first finding {first.rule_id} "
            f"!= {spec.first_finding_rule_id} (FR33 ordering)"
        )
        assert first.depth_supported is not None  # verdict-eligible (the moat)


# ─────────────────────────────────────────────────────────────────────────────
# AC3 / AC5 — the false-accusation floor: ANY blocking 🔴 is an instant CI fail
# (clean_control true-negative + the citation-gaming trap rejected)
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "spec",
    [s for s in CARTRIDGE_REGISTRY if s.max_blocking == 0],
    ids=lambda s: s.cartridge_id,
)
def test_false_accusation_floor_zero_blocking(spec: CartridgeSpec, tmp_path: Path) -> None:
    """TC-ArgusAgent-CARTRIDGE-001-03 — AC3/AC5: clean controls + traps emit ZERO blocking findings.

    The moat the whole tool's credibility rests on. A cartridge declared
    ``max_blocking == 0`` (clean_control, the citation-gaming trap, the secret/orphan
    advisory cartridges, the no-crash row) must audit to ZERO blocking findings — ANY
    blocking 🔴 is an instant CI fail. A clean-control row with a blocking finding
    FAILS here with a NAMED assertion citing the offending rule_id + locator (never
    source bytes — NFR-S1).
    """
    _repo, result = _audit(spec, tmp_path / "repo")
    blocking = [f for f in result.verdict.ordered_findings if f.depth_supported is not None]
    offenders = [(f.rule_id, f.locators[0].file_path, f.locators[0].start_line) for f in blocking]
    assert result.verdict.blocking_finding_count == 0, (
        f"cartridge {spec.cartridge_id!r}: false-accusation floor breached — "
        f"{result.verdict.blocking_finding_count} blocking finding(s): {offenders}"
    )
    assert not blocking, (
        f"cartridge {spec.cartridge_id!r}: a verdict-eligible finding leaked: {offenders}"
    )


def test_clean_control_is_release_ready(tmp_path: Path) -> None:
    """TC-ArgusAgent-CARTRIDGE-001-04 — AC3: the clean control audits RELEASE_READY / exit 0."""
    spec = next(s for s in CARTRIDGE_REGISTRY if s.kind == "clean_control")
    _repo, result = _audit(spec, tmp_path / "repo")
    assert result.verdict.verdict is Verdict.RELEASE_READY, (
        f"cartridge {spec.cartridge_id!r}: not RELEASE_READY ({result.verdict.verdict.value})"
    )
    assert result.verdict.exit_code == 0


def test_holdout_is_marked_and_caught(tmp_path: Path) -> None:
    """TC-ArgusAgent-CARTRIDGE-001-05 — AC4: the holdout is a NEW kind=holdout cartridge, caught + blocking.

    The overfitting defense: the holdout (a differently-named, differently-structured
    vacuous defect added in THIS story, never used to tune any 6.1-6.4 detector) is
    caught by the SAME ``vacuous_test_ast`` rule with NO detector change. An overfit
    detector that only memorized ``vacuous_basic`` would FAIL this test.
    """
    holdouts = [s for s in CARTRIDGE_REGISTRY if s.kind == "holdout"]
    assert holdouts, "the registry must declare >=1 hidden-holdout cartridge (AC4)"
    spec = holdouts[0]
    assert spec.cartridge_id == "holdout_vacuous"
    _repo, result = _audit(spec, tmp_path / "repo")
    assert any(
        f.rule_id == "vacuous_test_ast" and f.depth_supported is not None
        for f in result.verdict.ordered_findings
    ), f"cartridge {spec.cartridge_id!r}: the holdout defect was NOT caught (overfit?)"
    assert result.verdict.verdict is Verdict.NOT_READY_FOR_RELEASE
    assert result.verdict.exit_code == 2


def test_trap_is_marked_and_does_not_false_block(tmp_path: Path) -> None:
    """TC-ArgusAgent-CARTRIDGE-001-06 — AC5: the citation-gaming trap is kind=trap and does NOT false-block.

    The gaming defense: ``evidence_sentinel`` plants a distinctive SOURCE sentinel + a
    secret. A naive detector that citation-games (emits a BLOCKING finding citing a
    real locator while describing nothing real) would breach the max_blocking==0 floor
    and FAIL. The real detectors emit only an advisory redacted-secret finding.
    """
    traps = [s for s in CARTRIDGE_REGISTRY if s.kind == "trap"]
    assert traps, "the registry must declare >=1 citation-gaming trap cartridge (AC5)"
    spec = traps[0]
    _repo, result = _audit(spec, tmp_path / "repo")
    assert result.verdict.blocking_finding_count == 0, (
        f"cartridge {spec.cartridge_id!r}: the trap produced a blocking false accusation"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC6 — determinism + zero-token + secret-containment + non-ASCII over the corpus
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("spec", CARTRIDGE_REGISTRY, ids=lambda s: s.cartridge_id)
def test_byte_identical_determinism(spec: CartridgeSpec, tmp_path: Path) -> None:
    """TC-ArgusAgent-CARTRIDGE-001-07 — AC6/NFR-P1: each cartridge audited twice -> identical verdict envelope.

    The ``_cartridge.py`` HEAD-pin determinism precedent, generalized over the corpus:
    two independent stagings of the SAME cartridge yield a byte-identical (content-
    addressed name AND on-disk bytes AND ``content_hash``) verdict envelope.
    """
    repo_a, result_a = _audit(spec, tmp_path / "a")
    repo_b, result_b = _audit(spec, tmp_path / "b")
    loc_a = result_a.locators[0]
    loc_b = result_b.locators[0]
    assert loc_a == loc_b, f"cartridge {spec.cartridge_id!r}: verdict locator drift"
    reader_a = ApaaStoreReader(repo_a)
    reader_b = ApaaStoreReader(repo_b)
    assert reader_a.read_bytes(loc_a) == reader_b.read_bytes(loc_b), (
        f"cartridge {spec.cartridge_id!r}: verdict bytes drift (non-deterministic)"
    )
    env_a = reader_a.read_envelope(loc_a)
    env_b = reader_b.read_envelope(loc_b)
    assert env_a.content_hash == env_b.content_hash


@pytest.mark.parametrize(
    "spec",
    [s for s in CARTRIDGE_REGISTRY if s.non_ascii],
    ids=lambda s: s.cartridge_id,
)
def test_non_ascii_cartridge_audits_and_matches_golden_key(spec: CartridgeSpec, tmp_path: Path) -> None:
    """TC-ArgusAgent-CARTRIDGE-001-08 — AC6/AI-E1-1: a non-ASCII cartridge audits + matches its golden key under UTF-8.

    The non-ASCII module/test/path round-trips intact (UTF-8, not mojibake) and the
    golden key still matches — exercised under ``PYTHONIOENCODING=utf-8`` (the single
    serializer is ``ensure_ascii=False``).
    """
    _repo, result = _audit(spec, tmp_path / "repo")
    emitted = _emitted_keys(result)
    for gf in spec.required_findings:
        assert (gf.rule_id, gf.verdict_eligible, gf.advisory) in emitted, (
            f"cartridge {spec.cartridge_id!r}: non-ASCII golden key not matched"
        )
    assert result.verdict.verdict.value == spec.expected_verdict


@pytest.mark.parametrize(
    "spec",
    [s for s in CARTRIDGE_REGISTRY if s.cartridge_id in ("hardcoded_secret", "evidence_sentinel")],
    ids=lambda s: s.cartridge_id,
)
def test_secret_bytes_absent_from_read_surface(spec: CartridgeSpec, tmp_path: Path) -> None:
    """TC-ArgusAgent-CARTRIDGE-001-09 — AC6/NFR-S1: planted secret/source bytes ABSENT from findings/verdict/ledger.

    The harness audits the secret-bearing cartridges and asserts the planted secrets +
    the evidence source sentinel are ABSENT from the persisted ``.argus/`` byte blob
    AND every finding repr AND the verdict repr (the redaction guarantee, producer
    side). The 4.4 randomized-canary suite remains the CI-blocking property gate; this
    co-locates a fixed-canary containment check with the cartridge self-audit.
    """
    repo, result = _audit(spec, tmp_path / "repo")
    blob = b""
    for path in sorted((repo / ".argus").rglob("*")):
        if path.is_file():
            blob += path.read_bytes()
    blob += repr(result.verdict).encode("utf-8")
    for finding in result.verdict.ordered_findings:
        blob += repr(finding).encode("utf-8")
    for secret in _PLANTED_SECRET_BYTES:
        assert secret.encode("utf-8") not in blob, (
            f"cartridge {spec.cartridge_id!r}: SECRET/SOURCE LEAK — {secret!r} "
            f"appeared in the harness read surface (NFR-S1)"
        )


def test_secret_finding_is_value_free_and_redacted(tmp_path: Path) -> None:
    """TC-ArgusAgent-CARTRIDGE-001-10 — AC6/NFR-S1: the secret finding cites a locator but is structurally value-free."""
    spec = next(s for s in CARTRIDGE_REGISTRY if s.cartridge_id == "hardcoded_secret")
    _repo, result = _audit(spec, tmp_path / "repo")
    secret_findings = [f for f in result.verdict.ordered_findings if f.rule_id == "hardcoded_secret"]
    assert secret_findings, "the planted secret WAS detected (redaction != non-detection)"
    for finding in secret_findings:
        assert "value" not in type(finding).model_fields
        for loc in finding.locators:
            for loc_field in type(loc).model_fields:
                assert "value" not in loc_field and "source" not in loc_field


# ─────────────────────────────────────────────────────────────────────────────
# AC8 (6) — the no-crash cartridge row (AI-E4-2 mechanized / AR10)
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "spec",
    [s for s in CARTRIDGE_REGISTRY if s.kind == "no_crash"],
    ids=lambda s: s.cartridge_id,
)
def test_no_crash_cartridge_degrades_to_typed_verdict(spec: CartridgeSpec, tmp_path: Path) -> None:
    """TC-ArgusAgent-CARTRIDGE-001-11 — AC8(6)/AR10/NFR-R1: a no-crash input degrades to a typed verdict, never a crash.

    AI-E4-2 mechanized as a cartridge: ``tool_breadth`` (a breadth-tool surface with
    non-ASCII module paths and NO test files) audits to a typed ``Verdict`` with a
    valid exit code — NEVER an uncaught crash. ``_audit`` already converts any raise
    into a NAMED assertion; this asserts the honest-verdict outcome explicitly.
    """
    _repo, result = _audit(spec, tmp_path / "repo")
    assert isinstance(result.verdict.verdict, Verdict), (
        f"cartridge {spec.cartridge_id!r}: did not produce a typed Verdict"
    )
    assert result.verdict.exit_code in (0, 2, 3), (
        f"cartridge {spec.cartridge_id!r}: unexpected exit code {result.verdict.exit_code}"
    )
    assert result.verdict.verdict.value == spec.expected_verdict


def test_registry_count_matches_no_hand_copied_bodies() -> None:
    """TC-ArgusAgent-CARTRIDGE-001-12 — AC1/AI-E5-2: the declared set is iterated mechanically.

    Guards that the parametrized harness covers EVERY registry row (no row silently
    dropped, no hand-copied per-cartridge body that diverges from the registry).
    """
    covered_kinds = {spec.kind for spec in CARTRIDGE_REGISTRY}
    assert covered_kinds == {"planted_defect", "clean_control", "holdout", "trap", "no_crash"}
    # The planted-defect + holdout cartridges are the labeled true-positive set.
    assert populated_planted_defect_count() >= 3, (
        "OI1: the corpus front-loads >=3 labeled planted-defect cartridges in this phase"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC7 — the OI1 honesty keystone: the precision gate is mechanically PROVISIONAL
# ─────────────────────────────────────────────────────────────────────────────


def test_precision_gate_status_is_provisional_below_n5() -> None:
    """TC-ArgusAgent-CARTRIDGE-001-13 — AC7/OI1: the committed marker reports the gate PROVISIONAL below N=5.

    The mechanized form of "do not overclaim a precision number from too few
    cartridges." In Story 6.5 the marker MUST say "provisional" UNCONDITIONALLY — the
    harness computes NO >=80% number (that is Story 6.6). The count is reported for
    transparency but is NEVER used to silently flip the gate to cleared. Story 6.6
    flips this marker to non-provisional only after running the validation protocol at
    N>=5 with sufficient findings.
    """
    n = populated_planted_defect_count()
    assert PRECISION_GATE_STATUS.startswith("provisional"), (
        f"the precision gate must be PROVISIONAL in Story 6.5: {PRECISION_GATE_STATUS!r}"
    )
    assert "precision measured over findings" in PRECISION_GATE_STATUS
    assert "Story 6.6" in PRECISION_GATE_STATUS
    assert "NO " in PRECISION_GATE_STATUS  # NO precision number computed here
    assert f"N={n}" in PRECISION_GATE_STATUS
    assert f"N={VALIDATION_SET_FLOOR_N}" in PRECISION_GATE_STATUS


def test_harness_computes_no_precision_number() -> None:
    """TC-ArgusAgent-CARTRIDGE-001-14 — AC7 scope fence: 6.5 asserts NO >=80% precision figure.

    The marker is a STATUS string, not a number — the >=80% figure is Story 6.6 (the
    scope fence). ``PRECISION_GATE_STATUS`` must be a plain ``str`` carrying no numeric
    precision value, and it must report the gate as not-yet-computed here.
    """
    # PRECISION_GATE_STATUS is a str status marker, not a float / numeric ratio.
    assert isinstance(PRECISION_GATE_STATUS, str)
    assert "%" not in PRECISION_GATE_STATUS  # no percentage figure asserted
    assert "provisional" in PRECISION_GATE_STATUS
    assert "NO precision number computed here" in PRECISION_GATE_STATUS
    # The marker is the only precision surface the substrate exposes — the actual
    # number is Story 6.6 (the scope fence). No precision-ratio float is bound here.
    import _registry as _reg

    assert not hasattr(_reg, "PRECISION_VALUE")
    assert not hasattr(_reg, "MEASURED_PRECISION")


def test_this_harness_is_under_1200_lines() -> None:
    """TC-ArgusAgent-CARTRIDGE-001-15 — AC9/NFR-M1: this harness file is <=1200 lines."""
    lines = Path(__file__).read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 1200
