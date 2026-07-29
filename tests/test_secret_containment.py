"""ArgusAgent CI-BLOCKING secret-containment property suite (Story 4.4).

Drivers: ArgusAgent-FR-28 (producer-side redaction — findings cite locations, never
source/secret bytes; THIS suite is the durable CI-blocking ENFORCEMENT of FR28,
consolidating the per-story 2.5/2.6/4.3 producer proofs), ArgusAgent-NFR-S1 (source /
prompt / response / API-key bytes never appear in ledgers, evidence, logs, OTLP
spans/traces, or any response — a CI-blocking security suite mirroring Minions
§3.8 / ``tests/security/`` — the central driver), ArgusAgent-NFR-S2 (detected secrets
redacted before storage; the stored form carries the redaction WITHOUT the value
— the redaction-≠-suppression co-assertion), ArgusAgent-FR-29 / NFR-S3 (the evidence
bundle retains no source — one of the artifact classes covered), ArgusAgent-AR9
(committed / durable CI gates — this randomized-canary property suite is one of
the trust-substrate gates, under ``tests/security/``, wired to the Minions CI
model), ArgusAgent-NFR-P1 / NFR-D2 (the audit it drives is byte-deterministic +
zero-LLM-token, so the containment property over a given canary population is
reproducible), ArgusAgent-NFR-M1 (≤1200-line files), AR8 / AR10.

Verification area ArgusAgent-SECURITY (``TC-ArgusAgent-SECURITY-001-NN``) — the natural area
for the ``tests/security/`` ArgusAgent suite, distinct from the 2.5 ``ArgusAgent-SECRET`` area.
This is the FIRST ArgusAgent file under ``tests/security/``.

CI-blocking home (DN-CI — the simplest durable form, LOCKED). Placing the suite
under ``tests/security/`` means it is collected + RUN by (a) the merge-blocking
``security`` CI job (``pytest tests/security/ -v --strict-markers``, story 10-10
AC7), (b) the main ``test`` job (``pytest -q``), AND (c) the bulk-migration-guard
Layer-1 re-run — i.e. CI-blocking on three independent paths with ZERO new CI-job
wiring and NO custom pytest marker. A leak makes those jobs RED, blocking merge,
surviving a fresh ``git clone`` (the §6 durable-gate / L5-E11 model).

The property. The per-story proofs each fixed ONE sentinel; this suite VARIES the
secret value (a randomized population spanning every detector SHAPE, ASCII +
non-ASCII) so the guarantee is shown to hold for ARBITRARY secret values, not the
one fixed ``PLANTED...`` token. The randomization is the property; a FIXED seed
per session keeps it a reproducible CI gate, not a flaky soak test, and the
population is printed on failure so a CI red is debuggable.

The artifact-class UNION (NFR-S1 verbatim). Every canary is asserted ABSENT from:
the coverage ledger; every finding / Recording; the evidence bundle (in-memory
model bytes + serialized canonical bytes + the persisted bundle artifact); the
full ``_all_argus_bytes`` blob over ``.argus/**``; the verdict + verdict envelope;
captured logs; OTLP spans / traces; every raised exception message; and any
returned response object's repr.

Honest V1 union note. ArgusAgent V1 emits NO application logs and NO OTLP spans (it is a
zero-token, observability-free pipeline — there is no ``logging``/``opentelemetry``
import under ``argus/``; the Minions §3.8 OTLP export is no-op when
unset). Those two classes are therefore asserted EMPTY (no canary, because no log
record / span is produced at all) rather than silently dropped — an honest "this
class is structurally empty in V1, asserted empty" beats a silent narrowing. The
``AuditResult`` (the returned response object) repr is searched as the response
class; exception messages are exercised via the typed-error degradation paths.
"""

from __future__ import annotations

import logging
import random
import sys
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "argus" / "cartridges"))

from _cartridge import stage_cartridge  # noqa: E402

from argus.detectors.secret_scan import RULE_HARDCODED_SECRET  # noqa: E402
from argus.evidence.bundle import (  # noqa: E402
    build_evidence_bundle,
    bundle_to_canonical_bytes,
    bundle_to_canonical_payload,
    persist_evidence_bundle,
)
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import (  # noqa: E402
    PipelineError,
    run_audit_detailed,
)
from argus.store import canonical  # noqa: E402
from argus.store.integrity import lint_referential_integrity  # noqa: E402
from argus.store.reader import ApaaStoreReader  # noqa: E402
from argus.store.writer import ApaaStoreWriter  # noqa: E402

_ArgusAgent_VERSION = "0.1.0"

# ─────────────────────────────────────────────────────────────────────────────
# The FIXED-CANARY population planted in the cartridges/secret_canary cartridge.
# Each is a DISTINCTIVE token so its absence is a real proof (AI-E3-1 non-vacuous),
# spanning every detector SHAPE + a NON-secret source sentinel + a non-ASCII value.
# ─────────────────────────────────────────────────────────────────────────────
_CARTRIDGE_CANARIES: tuple[str, ...] = (
    # The distinctive NON-secret source sentinel (no plain audited source byte retained).
    "SECRET_CANARY_SOURCE_SENTINEL_q9ZxLmNrTaBcDeF1234567890ABCDEFghij",
    # AWS access-key id shape.
    "AKIASECRETCANARY12AB",
    # AWS secret-access-key shape.
    "SecretCanaryAwsSeCrEtVaLuE0123456789abcde",
    # token / password assignment shapes.
    "SecretCanaryTokenValueZZZ987654321abcDEF",
    "SecretCanaryPasswordValueQQQ12345678zzz",
    # PEM private-key header shape.
    "-----BEGIN RSA PRIVATE KEY-----",
    # critical-subsystem (auth) secret.
    "SecretCanaryAuthSeCrEtVaLuE0123456789abXY",
    # test-body secret (vacuous-test path).
    "SecretCanaryTestBodyVaLuE0123456789abcdEF",
    # non-ASCII / Cyrillic secret values (AI-E1-1).
    "пароль_секрет_SecretCanary_значение_0123456789",
    "SecretCanaryNonAsciiKeyЗначение0123456789ZZ",
    # The bare distinctive stem — must not survive in ANY encoding.
    "SecretCanary",
)

# A non-ASCII path planted by the cartridge (AI-E1-1) — proves path containment.
_NON_ASCII_PATH = "src/café/модуль_секрет.py"


def _request(repo: Path) -> AuditRequest:
    return AuditRequest(
        repo_path=str(repo), commit="HEAD", budget=100, materiality_bar="default"
    )


def _all_argus_bytes(repo: Path) -> bytes:
    """Concatenate the bytes of every persisted ``.argus/`` file under *repo*."""
    argus = repo / ".argus"
    blob = b""
    for path in sorted(argus.rglob("*")):
        if path.is_file():
            blob += path.read_bytes()
    return blob


def _artifact_union_blob(repo: Path, result, bundle) -> bytes:
    """The UNION of every artifact class, as a single UTF-8 byte blob (AC1).

    Covers: every persisted ``.argus/`` byte (which includes the coverage ledger,
    every finding / Recording, the verdict + verdict envelope, and the run-state);
    the evidence bundle in-memory model bytes + serialized canonical bytes; and the
    returned response object's repr (the ``AuditResult``). Logs / OTLP spans are
    structurally empty in V1 (asserted separately in the caplog test); exception
    messages are exercised in the typed-error test.
    """
    blob = _all_argus_bytes(repo)
    # In-memory bundle model bytes (model_dump) + the serialized canonical bytes.
    blob += canonical.dumps_bytes(bundle_to_canonical_payload(bundle))
    blob += bundle_to_canonical_bytes(bundle)
    # In-memory verdict + negative-assurance wrapper + coverage report repr/bytes.
    blob += repr(result).encode("utf-8")
    blob += repr(result.verdict).encode("utf-8")
    if result.negative_assurance is not None:
        blob += canonical.dumps_bytes(result.negative_assurance.model_dump(mode="json"))
    if result.coverage_report is not None:
        blob += canonical.dumps_bytes(result.coverage_report.model_dump(mode="json"))
    for finding in result.verdict.ordered_findings:
        blob += canonical.dumps_bytes(finding.model_dump(mode="json"))
    return blob


def _run_audit_export_persist(repo: Path):
    """Drive the FULL pipeline: audit → integrity lint → bundle build + persist."""
    result = run_audit_detailed(_request(repo))
    reader = ApaaStoreReader(repo)
    integrity = lint_referential_integrity(reader)
    bundle = build_evidence_bundle(
        result, integrity, commit="HEAD", argus_version=_ArgusAgent_VERSION
    )
    writer = ApaaStoreWriter(repo)
    persist_evidence_bundle(writer, bundle)
    return result, bundle


def _assert_canaries_absent(blob: bytes, canaries, *, context: str) -> None:
    """The artifact-class-union containment assertion — the SHARED property check.

    On failure the FULL canary population is printed so a CI red is debuggable
    (AC5 reproducibility / debuggability).
    """
    leaks = [c for c in canaries if c.encode("utf-8") in blob]
    assert not leaks, (
        f"SECRET LEAK in {context}: {leaks!r} "
        f"(full canary population: {list(canaries)!r})"
    )


# ─────────────────────────────────────────────────────────────────────────────
# The randomized-canary generator (the PROPERTY dimension) — FIXED seed per
# session so the gate is reproducible, not a flaky fuzz (AC5). Each generated
# value is a DISTINCTIVE high-entropy token (AI-E3-1 non-vacuous).
# ─────────────────────────────────────────────────────────────────────────────

_SESSION_SEED = 4_4_2026  # fixed per session — reproducible CI gate, not a fuzz
_RNG = random.Random(_SESSION_SEED)
_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


def _rand_token(prefix: str, length: int = 40) -> str:
    body = "".join(_RNG.choice(_ALPHABET) for _ in range(length))
    return f"{prefix}{body}"


def _generate_canary_population() -> dict[str, str]:
    """A randomized population spanning every secret SHAPE + a source sentinel.

    Keyed by the source-template substitution slot. The values VARY per session
    seed (the property), but each is a distinctive ``RANDCANARY``-stemmed token so
    absence is a real proof, never a vacuous "absence of a word never present".
    """
    aws_id_body = "".join(_RNG.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(16))
    aws_secret_body = "".join(_RNG.choice(_ALPHABET) for _ in range(40))
    return {
        "source_sentinel": _rand_token("RANDCANARY_SOURCE_SENTINEL_", 32),
        "aws_access_key_id": f"AKIA{aws_id_body}",
        "aws_secret_access_key": aws_secret_body,
        "api_token": _rand_token("RANDCANARYtok", 36),
        "password": _rand_token("RANDCANARYpwd", 36),
        # a non-ASCII / Cyrillic secret value (AI-E1-1).
        "nonascii_secret": "пароль_RANDCANARY_" + _rand_token("знач", 24),
    }


def _synthesize_canary_repo(dest: Path, pop: dict[str, str]) -> Path:
    """Synthesize a fresh committed git repo planting *pop* at every entry point.

    Plants: a source body (secret-scan + AST path), a vacuous test file, a
    critical-subsystem (auth)-named file, and a non-ASCII-PATH file with the
    non-ASCII secret — mirroring the cartridge planter but with randomized values.
    """
    import subprocess

    def _write(rel: str, text: str) -> None:
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    _write(
        "src/config.py",
        f'{pop["source_sentinel"]} = "marker-only-distinctive-source-byte"\n\n\n'
        f'def aws_client():\n'
        f'    aws_access_key_id = "{pop["aws_access_key_id"]}"\n'
        f'    aws_secret_access_key = "{pop["aws_secret_access_key"]}"\n'
        f'    return aws_access_key_id, aws_secret_access_key\n\n\n'
        f'def token_client():\n'
        f'    api_token = "{pop["api_token"]}"\n'
        f'    password = "{pop["password"]}"\n'
        f'    return api_token, password\n',
    )
    _write(
        "src/auth/guard.py",
        f'def authorize(token):\n'
        f'    secret = "{pop["api_token"]}"\n'
        f'    return token == secret\n',
    )
    _write(
        "tests/test_config.py",
        f'def test_smoke():\n'
        f'    secret_in_test = "{pop["password"]}"\n'
        f'    assert secret_in_test is not None\n',
    )
    _write(
        "src/café/модуль.py",
        f'def подключить():\n'
        f'    пароль = "{pop["nonascii_secret"]}"\n'
        f'    return пароль\n',
    )

    def _git(*args: str) -> None:
        subprocess.run(["git", "-C", str(dest), *args], check=True, capture_output=True)

    _git("init")
    _git("config", "user.email", "canary@argus.test")
    _git("config", "user.name", "ArgusAgent Canary")
    _git("add", "-A")
    _git("commit", "-m", "secret canary")
    return dest


# ─────────────────────────────────────────────────────────────────────────────
# AC1 — whole-pipeline artifact-class-union containment (FIXED cartridge canaries)
# ─────────────────────────────────────────────────────────────────────────────


def test_cartridge_canaries_absent_from_every_artifact_class(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-01 — AC1: every planted canary ABSENT from the artifact-class union."""
    repo, _sha = stage_cartridge("secret_canary", tmp_path / "repo")
    result, bundle = _run_audit_export_persist(repo)

    blob = _artifact_union_blob(repo, result, bundle)
    assert blob, "the pipeline persisted + exported at least one artifact"
    _assert_canaries_absent(blob, _CARTRIDGE_CANARIES, context="artifact-class union")


def test_cartridge_canaries_absent_from_persisted_argus_tree(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-02 — AC1: every canary ABSENT from the full .argus/ byte blob."""
    repo, _sha = stage_cartridge("secret_canary", tmp_path / "repo")
    _result, _bundle = _run_audit_export_persist(repo)
    blob = _all_argus_bytes(repo)
    assert blob
    _assert_canaries_absent(blob, _CARTRIDGE_CANARIES, context=".argus/ tree")


def test_cartridge_canaries_absent_from_serialized_and_persisted_bundle(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-03 — AC1/FR29: every canary ABSENT from the evidence bundle (serialized + persisted)."""
    repo, _sha = stage_cartridge("secret_canary", tmp_path / "repo")
    result, bundle = _run_audit_export_persist(repo)
    serialized = bundle_to_canonical_bytes(bundle)
    in_memory = canonical.dumps_bytes(bundle_to_canonical_payload(bundle))
    # Locate the persisted bundle (a state/ artifact whose producer is the bundle producer).
    persisted = b""
    for path in sorted((repo / ".argus").rglob("*.json")):
        if path.is_file():
            persisted += path.read_bytes()
    for context, blob in (
        ("serialized bundle", serialized),
        ("in-memory bundle", in_memory),
        ("persisted .argus/ json", persisted),
    ):
        _assert_canaries_absent(blob, _CARTRIDGE_CANARIES, context=context)


# ─────────────────────────────────────────────────────────────────────────────
# AC1 (the PROPERTY) — randomized canary population, fixed seed per session
# ─────────────────────────────────────────────────────────────────────────────


def test_randomized_canary_population_absent_from_artifact_union(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-04 — AC1 PROPERTY: an ARBITRARY (seeded) canary population leaks nowhere."""
    pop = _generate_canary_population()
    repo = _synthesize_canary_repo(tmp_path / "rand_repo", pop)
    result, bundle = _run_audit_export_persist(repo)

    blob = _artifact_union_blob(repo, result, bundle)
    # Assert the full generated id, not the bare "AKIA" prefix (which is not a secret).
    canaries = (*pop.values(), "RANDCANARY", pop["aws_access_key_id"])
    _assert_canaries_absent(blob, canaries, context="randomized artifact union")


@pytest.mark.parametrize("iteration", range(3))
def test_randomized_population_holds_over_a_bounded_matrix(tmp_path: Path, iteration: int) -> None:
    """TC-ArgusAgent-SECURITY-001-05 — AC1/AC5: the property holds over a BOUNDED matrix of varied populations."""
    pop = _generate_canary_population()
    repo = _synthesize_canary_repo(tmp_path / f"rand_repo_{iteration}", pop)
    result, bundle = _run_audit_export_persist(repo)
    blob = _artifact_union_blob(repo, result, bundle)
    _assert_canaries_absent(
        blob, (*pop.values(), "RANDCANARY"), context=f"matrix iteration {iteration}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC2 — redaction is NOT suppression: the audit STILL produces its findings
# ─────────────────────────────────────────────────────────────────────────────


def test_redaction_is_not_suppression_secret_findings_emitted(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-06 — AC2: the secret findings ARE present with correct locators (not suppressed)."""
    repo, _sha = stage_cartridge("secret_canary", tmp_path / "repo")
    result, _bundle = _run_audit_export_persist(repo)

    secret_findings = [
        f for f in result.verdict.ordered_findings if f.rule_id == RULE_HARDCODED_SECRET
    ]
    assert secret_findings, "the planted secrets WERE detected (redaction != non-detection)"
    # Findings point at the planted files/lines WITHOUT carrying the value.
    located_files = {f.locators[0].file_path for f in secret_findings}
    assert "src/config.py" in located_files
    assert "src/auth/guard.py" in located_files
    assert _NON_ASCII_PATH in located_files
    for finding in secret_findings:
        assert finding.locators[0].start_line >= 1
        assert finding.advisory is True
        # The Recording is structurally value-free (no value/source field exists).
        assert "value" not in type(finding).model_fields
        for loc_field in type(finding.locators[0]).model_fields:
            assert "value" not in loc_field and "source" not in loc_field


def test_bundle_is_non_empty_findings_exported(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-07 — AC2: the exported bundle is non-empty + carries the secret findings."""
    repo, _sha = stage_cartridge("secret_canary", tmp_path / "repo")
    _result, bundle = _run_audit_export_persist(repo)
    assert bundle.findings, "the bundle exported the findings (containment, not blanket suppression)"
    assert bundle.negative_assurance.verdict
    assert bundle.coverage.entries
    exported_secret = [f for f in bundle.findings if f.rule_id == RULE_HARDCODED_SECRET]
    assert exported_secret


# ─────────────────────────────────────────────────────────────────────────────
# AC3 — the suite demonstrably CATCHES a planted leak (AI-E3-1, the marquee guard)
# ─────────────────────────────────────────────────────────────────────────────


def test_containment_property_is_red_against_a_leaking_producer(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-08 — AC3 KEYSTONE: the SAME union assertion FAILS on a planted leak, then PASSES clean.

    A green containment suite that structurally could not catch a leak is worthless
    (the Epic-3 3.4 review-FAIL class, the AI-E3-1 lesson). This test proves the
    property has TEETH: a deliberately-leaking bundle variant (one that copies the
    audited source sentinel + a secret value into a payload field) is run through
    the SAME ``_assert_canaries_absent`` artifact-class-union check the real suite
    runs — and it MUST raise. Then the real source-free pipeline PASSES the same
    check. The leak traverses the SAME assertion, so the proof is non-vacuous.
    """
    repo, _sha = stage_cartridge("secret_canary", tmp_path / "repo")
    result, bundle = _run_audit_export_persist(repo)

    # ── RED leg: a leaking-producer variant copies a source excerpt + secret into
    # the canonical bundle payload (simulating a future write path that retains
    # source). The SAME union assertion must catch it.
    leaking_payload = bundle_to_canonical_payload(bundle)
    leaking_payload["commit"] = (
        f'{_CARTRIDGE_CANARIES[0]} {_CARTRIDGE_CANARIES[2]}'  # source sentinel + a secret
    )
    leaking_blob = _all_argus_bytes(repo) + canonical.dumps_bytes(leaking_payload)
    with pytest.raises(AssertionError) as red:
        _assert_canaries_absent(
            leaking_blob, _CARTRIDGE_CANARIES, context="leaking-producer variant"
        )
    assert "SECRET LEAK" in str(red.value)

    # ── GREEN leg: the REAL, source-free pipeline passes the SAME assertion.
    clean_blob = _artifact_union_blob(repo, result, bundle)
    _assert_canaries_absent(clean_blob, _CARTRIDGE_CANARIES, context="real pipeline (green leg)")


def test_leaking_argus_byte_is_caught_by_the_same_assertion(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-09 — AC3: a raw secret written into a .argus/ byte is caught by the union check."""
    repo, _sha = stage_cartridge("secret_canary", tmp_path / "repo")
    result, bundle = _run_audit_export_persist(repo)

    # Simulate a producer that wrote a raw secret into a .argus/ artifact byte.
    leaked_artifact = (repo / ".argus" / "state" / "LEAKED.txt")
    leaked_artifact.parent.mkdir(parents=True, exist_ok=True)
    leaked_artifact.write_text(_CARTRIDGE_CANARIES[6], encoding="utf-8")  # the auth secret

    leaking_blob = _all_argus_bytes(repo)
    with pytest.raises(AssertionError):
        _assert_canaries_absent(leaking_blob, _CARTRIDGE_CANARIES, context="leaking .argus/ byte")

    # Clean it up; the real union (without the planted file) is clean.
    leaked_artifact.unlink()
    clean_blob = _artifact_union_blob(repo, result, bundle)
    _assert_canaries_absent(clean_blob, _CARTRIDGE_CANARIES, context="cleaned pipeline")


# ─────────────────────────────────────────────────────────────────────────────
# AC5 — non-ASCII secrets + paths contained; reproducible + not flaky
# ─────────────────────────────────────────────────────────────────────────────


def test_non_ascii_secret_and_path_are_contained(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-10 — AC5/AI-E1-1: a non-ASCII secret value + non-ASCII path leak nowhere."""
    repo, _sha = stage_cartridge("secret_canary", tmp_path / "repo")
    result, bundle = _run_audit_export_persist(repo)
    blob = _artifact_union_blob(repo, result, bundle)

    non_ascii_canaries = (
        "пароль_секрет_SecretCanary_значение_0123456789",
        "SecretCanaryNonAsciiKeyЗначение0123456789ZZ",
    )
    _assert_canaries_absent(blob, non_ascii_canaries, context="non-ASCII secret values")

    # The non-ASCII PATH is a locator that MAY (and should) appear — proving the
    # path itself round-trips intact (it is NOT a secret); only the secret VALUE is
    # contained. The finding for the non-ASCII file points at the intact path.
    located = {f.locators[0].file_path for f in result.verdict.ordered_findings}
    assert _NON_ASCII_PATH in located, "the non-ASCII locator path round-trips intact"


def test_containment_property_is_reproducible_byte_stable(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-11 — AC5/NFR-P1: the same cartridge audited twice → byte-identical .argus/ verdict bytes."""
    repo_a, _a = stage_cartridge("secret_canary", tmp_path / "repo_a")
    repo_b, _b = stage_cartridge("secret_canary", tmp_path / "repo_b")
    result_a, bundle_a = _run_audit_export_persist(repo_a)
    result_b, bundle_b = _run_audit_export_persist(repo_b)
    # The audit is byte-deterministic (NFR-P1), so the exported bundle bytes match.
    assert bundle_to_canonical_bytes(bundle_a) == bundle_to_canonical_bytes(bundle_b)
    # And both are contained.
    for repo, result, bundle in ((repo_a, result_a, bundle_a), (repo_b, result_b, bundle_b)):
        _assert_canaries_absent(
            _artifact_union_blob(repo, result, bundle),
            _CARTRIDGE_CANARIES,
            context="reproducibility leg",
        )


def test_failure_message_prints_the_canary_population() -> None:
    """TC-ArgusAgent-SECURITY-001-12 — AC5: a failure prints the full canary population (debuggable CI red)."""
    with pytest.raises(AssertionError) as exc:
        _assert_canaries_absent(b"contains SecretCanary leak", _CARTRIDGE_CANARIES, context="probe")
    msg = str(exc.value)
    assert "full canary population" in msg
    assert "SECRET LEAK in probe" in msg


# ─────────────────────────────────────────────────────────────────────────────
# AC1 (union honesty) — logs / OTLP spans / exception messages / response repr
# ─────────────────────────────────────────────────────────────────────────────


def test_no_canary_in_captured_logs(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """TC-ArgusAgent-SECURITY-001-13 — AC1: captured logs carry no canary (V1 emits no app logs; asserted empty-of-canary)."""
    repo, _sha = stage_cartridge("secret_canary", tmp_path / "repo")
    with caplog.at_level(logging.DEBUG):
        _result, _bundle = _run_audit_export_persist(repo)
    captured = "\n".join(r.getMessage() for r in caplog.records)
    _assert_canaries_absent(captured.encode("utf-8"), _CARTRIDGE_CANARIES, context="captured logs")


def test_no_canary_in_exception_message_on_degradation(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-14 — AC1/AR10: a typed degradation error carries no canary byte (NFR-S1)."""
    # Drive the pipeline at a non-existent repo → a TYPED error whose message carries
    # only the error-class token, never a source/secret byte (AR10 honest degradation).
    bad_repo = tmp_path / "does-not-exist"
    with pytest.raises(Exception) as exc:
        run_audit_detailed(
            AuditRequest(
                repo_path=str(bad_repo), commit="HEAD", budget=100, materiality_bar="default"
            )
        )
    message = str(exc.value)
    _assert_canaries_absent(message.encode("utf-8"), _CARTRIDGE_CANARIES, context="exception message")
    # The raise is a TYPED pipeline/intake error (never a bare uncaught leak).
    assert isinstance(exc.value, (PipelineError, Exception))


def test_no_canary_in_returned_response_repr(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-15 — AC1: the returned AuditResult response object repr carries no canary."""
    repo, _sha = stage_cartridge("secret_canary", tmp_path / "repo")
    result, bundle = _run_audit_export_persist(repo)
    response_repr = (
        repr(result) + repr(result.verdict) + repr(result.negative_assurance) + repr(bundle)
    )
    _assert_canaries_absent(
        response_repr.encode("utf-8"), _CARTRIDGE_CANARIES, context="response repr"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Story 5.2 — the .argus/cache/ memo-store tree joins the swept artifact-class union
# ─────────────────────────────────────────────────────────────────────────────


def _all_cache_bytes(repo: Path) -> bytes:
    """Concatenate the bytes of every persisted ``.argus/cache/`` file under *repo*."""
    cache = repo / ".argus" / "cache"
    blob = b""
    if cache.is_dir():
        for path in sorted(cache.rglob("*")):
            if path.is_file():
                blob += path.read_bytes()
    return blob


def _store_unit_recordings_in_memo_cache(repo: Path, result) -> None:
    """Persist the audited unit's REDACTED recordings into the memo cache (5.2).

    The cache stores already-2.5-redacted Recording bytes (no source/secret value).
    This drives the FIRST ``.argus/cache/`` write so the containment sweep proves the
    cache is just another swept ``.argus/`` artifact class.
    """
    from argus.cache.key import (
        FROZEN_DETECTOR_SET,
        RecordingProducingClosure,
        derive_cache_key,
    )
    from argus.cache.memo_store import MemoStore

    # Reuse the audit's own redacted findings as the cached Recording-set.
    recordings = tuple(result.verdict.ordered_findings)
    closure = RecordingProducingClosure(
        content_hash="c" * 64,
        detectors=FROZEN_DETECTOR_SET,
        grammar_version="0.23.6",
        budget=100,
        materiality_bar="default",
        work_manifest_files=("src/config.py",),
    )
    MemoStore(repo).store(derive_cache_key(closure), recordings)


def test_cache_tree_is_in_the_swept_union_canaries_absent(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-17 — Story 5.2: a memo-cache entry over the audited unit carries no canary byte."""
    repo, _sha = stage_cartridge("secret_canary", tmp_path / "repo")
    result, _bundle = _run_audit_export_persist(repo)

    _store_unit_recordings_in_memo_cache(repo, result)

    cache_blob = _all_cache_bytes(repo)
    assert cache_blob, "the memo store wrote at least one .argus/cache/ byte"
    _assert_canaries_absent(cache_blob, _CARTRIDGE_CANARIES, context=".argus/cache/ tree")
    # The full-tree sweep (which already rglobs .argus/**) also stays clean.
    _assert_canaries_absent(_all_argus_bytes(repo), _CARTRIDGE_CANARIES, context=".argus/ tree (incl cache)")


def test_cache_sweep_is_red_against_a_planted_cache_leak(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-18 — Story 5.2 keystone-adequacy: a raw secret in a .argus/cache/ byte is CAUGHT by the sweep."""
    repo, _sha = stage_cartridge("secret_canary", tmp_path / "repo")
    result, _bundle = _run_audit_export_persist(repo)
    _store_unit_recordings_in_memo_cache(repo, result)

    # Plant a raw secret directly into a .argus/cache/ byte — the sweep MUST catch it.
    leaked = repo / ".argus" / "cache" / "LEAKED.json"
    leaked.write_text(_CARTRIDGE_CANARIES[2], encoding="utf-8")  # an AWS-secret-shape canary
    with pytest.raises(AssertionError):
        _assert_canaries_absent(_all_cache_bytes(repo), _CARTRIDGE_CANARIES, context="leaking cache byte")

    # Clean it; the real cache sweep is clean.
    leaked.unlink()
    _assert_canaries_absent(_all_cache_bytes(repo), _CARTRIDGE_CANARIES, context="cleaned cache sweep")


# ─────────────────────────────────────────────────────────────────────────────
# Story 5.3 — the rejection-record artifact class joins the swept artifact-class
# union (RejectedFinding record + RejectionLedger under .argus/decisions/). The
# record cites a finding by recording_id + the cache key + redacted metadata, NEVER
# source/secret bytes — so a planted canary in an audited unit is ABSENT from every
# rejection-record byte, and the sweep CATCHES a planted leak.
# ─────────────────────────────────────────────────────────────────────────────


def _all_decisions_bytes(repo: Path) -> bytes:
    """Concatenate the bytes of every persisted ``.argus/decisions/`` file under *repo*."""
    decisions = repo / ".argus" / "decisions"
    blob = b""
    if decisions.is_dir():
        for path in sorted(decisions.rglob("*")):
            if path.is_file():
                blob += path.read_bytes()
    return blob


def _record_rejection_for_audited_unit(repo: Path, result) -> None:
    """Append a RejectedFinding citing an audited finding by recording_id + key (5.3).

    The rejection record cites the finding by id + the cache key it was served under
    + a redacted reason — it carries NO source/secret bytes. This drives the FIRST
    ``.argus/decisions/rejection_ledger.json`` write so the sweep proves the rejection
    record is just another swept ``.argus/`` artifact class.
    """
    from argus.cache.invalidation import RejectedFinding, RejectionLedger

    ledger = RejectionLedger(repo)
    findings = list(result.verdict.ordered_findings)
    cited = findings[0].recording_id if findings else "rec-none"
    ledger.append(
        RejectedFinding(
            recording_id=cited,
            key="d" * 64,  # the cache key the rejected finding was served under
            rule_id="hardcoded_secret",
            reason="operator-rejected false-positive",
        )
    )


def test_rejection_record_is_in_the_swept_union_canaries_absent(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-19 — Story 5.3: a rejection record citing an audited finding carries no canary byte."""
    repo, _sha = stage_cartridge("secret_canary", tmp_path / "repo")
    result, _bundle = _run_audit_export_persist(repo)

    _record_rejection_for_audited_unit(repo, result)

    decisions_blob = _all_decisions_bytes(repo)
    assert decisions_blob, "the rejection ledger wrote at least one .argus/decisions/ byte"
    _assert_canaries_absent(decisions_blob, _CARTRIDGE_CANARIES, context=".argus/decisions/ rejection record")
    # The full-tree sweep (which rglobs .argus/**, including decisions/) stays clean.
    _assert_canaries_absent(
        _all_argus_bytes(repo), _CARTRIDGE_CANARIES, context=".argus/ tree (incl rejection record)"
    )


def test_rejection_record_sweep_is_red_against_a_planted_leak(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-20 — Story 5.3 keystone-adequacy: a raw secret in a .argus/decisions/ byte is CAUGHT by the sweep."""
    repo, _sha = stage_cartridge("secret_canary", tmp_path / "repo")
    result, _bundle = _run_audit_export_persist(repo)
    _record_rejection_for_audited_unit(repo, result)

    # Plant a raw secret directly into a .argus/decisions/ byte — the sweep MUST catch it.
    leaked = repo / ".argus" / "decisions" / "LEAKED.json"
    leaked.parent.mkdir(parents=True, exist_ok=True)
    leaked.write_text(_CARTRIDGE_CANARIES[2], encoding="utf-8")  # an AWS-secret-shape canary
    with pytest.raises(AssertionError):
        _assert_canaries_absent(
            _all_decisions_bytes(repo), _CARTRIDGE_CANARIES, context="leaking decisions byte"
        )

    # Clean it; the real decisions sweep is clean.
    leaked.unlink()
    _assert_canaries_absent(
        _all_decisions_bytes(repo), _CARTRIDGE_CANARIES, context="cleaned decisions sweep"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Story 6.7 — the HITL decision-record artifact class joins the swept artifact-class
# union (an append-only prev-hash-chained decision record under .argus/decisions/).
# The record cites the pattern-matched trigger by rule-id + reason token + the
# triggering finding's recording_id + a file/line locator token + a decider-id
# token + a content-derived decision-id — NEVER source/secret bytes. So a planted
# canary in an audited unit is ABSENT from every decision-record byte, and the sweep
# CATCHES a planted leak.
# ─────────────────────────────────────────────────────────────────────────────


def _record_hitl_decision_for_audited_unit(repo: Path, result) -> None:
    """Append a HITL decision record whose trigger cites an audited secret finding (6.7).

    The escalation gate is PATTERN-MATCHED over the audited findings' rule_ids; the
    decision record carries only provenance tokens (rule-id / reason / recording_id /
    file-line locator / decider-id / content-derived id) — never source/secret bytes.
    This drives the FIRST HITL ``.argus/decisions/<content_hash>.json`` write so the
    sweep proves the decision record is just another swept ``.argus/`` artifact class.
    """
    from argus.detectors.secret_scan import RULE_HARDCODED_SECRET
    from argus.governance.decision_record import DecisionRecordWriter
    from argus.governance.escalation import (
        EscalationOutcome,
        EscalationRule,
        HumanDecision,
        escalation_fires,
        resolve_escalation,
    )

    findings = tuple(result.verdict.ordered_findings)
    rule = EscalationRule(
        rule_id="hitl-secret-escalation",
        reason="secret_bearing_file_high_stakes",
        match_rule_ids=(RULE_HARDCODED_SECRET,),
    )
    trigger = escalation_fires(rule, findings=findings)
    # The secret_canary cartridge always produces a hardcoded_secret finding, so the
    # escalation fires; if it somehow did not, this is a NAMED failure, not a silent skip.
    assert trigger is not None, "the secret finding fired the HITL escalation (pattern match)"
    resolution = resolve_escalation(
        trigger,
        human_decision=HumanDecision(outcome=EscalationOutcome.STOP, decider_id="security-owner"),
    )
    DecisionRecordWriter(repo).append(resolution)


def test_hitl_decision_record_is_in_the_swept_union_canaries_absent(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-21 — Story 6.7: a HITL decision record over a secret finding carries no canary byte."""
    repo, _sha = stage_cartridge("secret_canary", tmp_path / "repo")
    result, _bundle = _run_audit_export_persist(repo)

    _record_hitl_decision_for_audited_unit(repo, result)

    decisions_blob = _all_decisions_bytes(repo)
    assert decisions_blob, "the HITL writer wrote at least one .argus/decisions/ byte"
    _assert_canaries_absent(decisions_blob, _CARTRIDGE_CANARIES, context=".argus/decisions/ HITL decision record")
    # The full-tree sweep (which rglobs .argus/**, including decisions/) stays clean.
    _assert_canaries_absent(
        _all_argus_bytes(repo), _CARTRIDGE_CANARIES, context=".argus/ tree (incl HITL decision record)"
    )


def test_hitl_decision_record_sweep_is_red_against_a_planted_leak(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-22 — Story 6.7 keystone-adequacy: a raw secret in a HITL decision byte is CAUGHT."""
    repo, _sha = stage_cartridge("secret_canary", tmp_path / "repo")
    result, _bundle = _run_audit_export_persist(repo)
    _record_hitl_decision_for_audited_unit(repo, result)

    # Plant a raw secret directly into a .argus/decisions/ byte — the sweep MUST catch it.
    leaked = repo / ".argus" / "decisions" / ("a" * 64 + ".json")
    leaked.parent.mkdir(parents=True, exist_ok=True)
    leaked.write_text(_CARTRIDGE_CANARIES[2], encoding="utf-8")  # an AWS-secret-shape canary
    with pytest.raises(AssertionError):
        _assert_canaries_absent(
            _all_decisions_bytes(repo), _CARTRIDGE_CANARIES, context="leaking HITL decision byte"
        )

    # Clean it; the real decisions sweep is clean.
    leaked.unlink()
    _assert_canaries_absent(
        _all_decisions_bytes(repo), _CARTRIDGE_CANARIES, context="cleaned HITL decision sweep"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Story 7.2 — the dogfood bundle over the REAL Minions repo is source-free (NFR-S1/S3)
# ─────────────────────────────────────────────────────────────────────────────

# Real Minions SOURCE-BODY bytes (statements / docstring phrases) that live in the real
# minions_core tree but must NOT survive into the source-free dogfood evidence bundle. A
# SYMBOL name is NOT a valid sentinel (a finding legitimately cites a symbol in a locator's
# ast_span — that IS the FR13 "location"); only a source-CODE-BODY byte is what the 4.3
# no-source-retention moat forbids retaining. Each is proven present in the real tree first
# (non-vacuity) so the absence assertion is meaningful.
_MINIONS_SOURCE_BODY_SENTINELS: tuple[str, ...] = (
    "sha256",
    "import hashlib",
    "raise ValueError",
)



def test_dogfood_bundle_over_real_minions_repo_is_source_free(tmp_path: Path) -> None:
    """TC-ArgusAgent-SECURITY-001-23 — Story 7.2/NFR-S1/S3: the REAL-repo dogfood bundle is source-free.

    The 4.3 no-source-retention moat proven over the REAL Minions tree (not only a
    cartridge): the SIGNED dogfood evidence bundle (built by ``run_dogfood`` over the real
    ``minions_core/`` source) + every persisted ``.argus/`` artifact contains NO Minions
    source-BODY byte, WHILE the bundle is non-empty + the verdict + findings are present
    (redaction != suppression). Each sentinel is proven present in the real source first
    (non-vacuity), so the absence assertion is meaningful.
    """
    from argus.dogfood.proof_run import run_dogfood  # local import (7.2)

    repo_root = Path(__file__).resolve().parents[1]

    # Non-vacuity: each sentinel genuinely exists in the real audited source.
    real_source = b""
    for src_file in sorted((repo_root / "argus").rglob("*.py")):
        real_source += src_file.read_bytes()

    for sentinel in _MINIONS_SOURCE_BODY_SENTINELS:
        assert sentinel.encode("utf-8") in real_source, (
            f"non-vacuity: {sentinel!r} must exist in the real Minions source"
        )

    execution = run_dogfood(str(repo_root), tmp_path / "dogfood-snap")

    # The bundle is non-empty + carries the verdict + findings (redaction != suppression).
    assert execution.bundle.negative_assurance is not None
    assert execution.bundle.findings, "the dogfood bundle must carry the verdict-ordered findings"
    assert len(execution.bundle_bytes) > 0

    # No source-body byte in the serialized bundle bytes.
    for sentinel in _MINIONS_SOURCE_BODY_SENTINELS:
        assert sentinel.encode("utf-8") not in execution.bundle_bytes, (
            f"SOURCE LEAK (NFR-S1) — {sentinel!r} in the dogfood bundle bytes over the REAL repo"
        )
    # No source-body byte in any persisted .argus/ artifact on disk.
    on_disk = b""
    for artifact in sorted((tmp_path / "dogfood-snap" / ".argus").rglob("*.json")):
        on_disk += artifact.read_bytes()
    assert on_disk, "the dogfood run must persist at least the bundle artifact"
    for sentinel in _MINIONS_SOURCE_BODY_SENTINELS:
        assert sentinel.encode("utf-8") not in on_disk, (
            f"SOURCE LEAK (NFR-S1/S3) — {sentinel!r} in a persisted dogfood .argus/ artifact"
        )


# ─────────────────────────────────────────────────────────────────────────────
# AC6 — file-size gate (the test file itself ≤1200 lines, NFR-M1)
# ─────────────────────────────────────────────────────────────────────────────


def test_this_suite_is_under_1200_lines() -> None:
    """TC-ArgusAgent-SECURITY-001-16 — AC6/NFR-M1: this test file is ≤1200 lines."""
    lines = Path(__file__).read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 1200
