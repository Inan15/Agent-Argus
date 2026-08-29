"""Story 8.1 / AC11 — the FR16 amendment's ONLY intentional content-hash change.

Verification area ArgusAgent-VERDICT (``TC-ArgusAgent-VERDICT-003-NN``). Drivers:
ArgusAgent-DR-4 (the ``VERDICT_SCHEMA_VERSION`` "1" → "2" bump), ArgusAgent-DR-9 (byte-level
determinism across the delta), ArgusAgent-NFR-D1/P1 (byte-identical on-disk state),
ArgusAgent-NFR-D3 (content hash over the canonical payload only), ArgusAgent-NFR-M2
(additive-only schema evolution — the bump is the sanctioned lever for an INTENTIONAL
hash change).

Why a fixture of pre-amendment bytes
------------------------------------
"Only the verdict envelope changed" is a claim about a DIFFERENCE between two trees, and
a difference cannot be observed from inside one of them. ``fixtures/
verdict_schema_v1_row2_artifacts.json`` therefore holds the actual persisted ``.argus/``
bytes of a full pipeline run over the ``vacuous_basic`` cartridge, captured from the tree
at commit ``9109e16`` (pre-amendment) and verified reproducible across two runs before the
delta landed. This test re-runs the SAME audit post-amendment and diffs.

``vacuous_basic`` lands on FR16 **row 2** (one AST-corroborated vacuous finding), so the
verdict VALUE and the exit code are unchanged by the amendment — which is exactly what
makes it the right subject: every byte that moves is attributable to the schema bump and
the added ``decision_row`` key, and nothing else.

Story 8.2 EXTENDS (never relaxes) this proof
--------------------------------------------
DR-5 gives ``CriticalSubsystemSet`` an always-serialized disclosure field and moves its
localized stamp "1" → "2", so a SECOND envelope necessarily changes bytes. Rather than
widening ``-003-01`` to "ignore", the critical-subsystem envelope is named, held to the
SAME revert-proof shape ``-003-02`` uses for the verdict (``-003-04``), and every OTHER
artifact stays byte-identical with the artifact COUNT unchanged. ``vacuous_basic``'s
critical set is empty both before and after the filter (measured), so its added key is
empty and the stamp is the only substantive delta — which is precisely why a diff here
is readable rather than a wall of noise.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))

from _cartridge import stage_cartridge  # noqa: E402

from argus.ledger.critical_subsystems import (  # noqa: E402
    CRITICAL_SUBSYSTEMS_SCHEMA_VERSION,
)
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit_detailed  # noqa: E402
from argus.pipeline_persist import CRITICAL_SUBSYSTEMS_PRODUCER  # noqa: E402
from argus.store import canonical  # noqa: E402
from argus.store.reader import ApaaStoreReader  # noqa: E402
from argus.verdict.verdict_gate import (  # noqa: E402
    VERDICT_SCHEMA_VERSION,
    DecisionRow,
    Verdict,
)

_FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "verdict_schema_v1_row2_artifacts.json"
)


def _pre_amendment() -> dict[str, object]:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


def _sole_locator(artifacts: dict[str, str], producer: str) -> str:
    """The single locator in *artifacts* whose envelope carries *producer*.

    Content-addressing means a changed payload changes the locator, so the two trees
    cannot be compared key-by-key for an artifact that legitimately moved. The producer
    token is the stable identity; requiring EXACTLY one match keeps this from silently
    degrading into "pick the first thing that looks right".
    """
    matches = [
        loc for loc, text in artifacts.items() if json.loads(text)["producer"] == producer
    ]
    assert len(matches) == 1, f"expected exactly one {producer} artifact, got {matches}"
    return matches[0]


def _run(tmp_path: Path) -> tuple[ApaaStoreReader, object]:
    repo, _sha = stage_cartridge("vacuous_basic", tmp_path / "repo")
    result = run_audit_detailed(
        AuditRequest(
            repo_path=str(repo), commit="HEAD", budget=100, materiality_bar="default"
        )
    )
    return ApaaStoreReader(repo), result


def test_TC_ArgusAgent_VERDICT_003_01_only_the_verdict_envelope_changed(
    tmp_path: Path,
) -> None:
    """AC11 — every persisted artifact except the two SCHEMA-BUMPED envelopes is BYTE-IDENTICAL.

    Both bumped envelopes are content-addressed, so each bump necessarily moves its own
    locator; those are the intentional hash changes. Nothing else may move: not the
    ledger, not the findings, not the halt report, not the assignments.

    Story 8.2 names the critical-subsystem envelope as the SECOND permitted mover rather
    than widening this assertion — the exemption is one enumerated artifact whose whole
    delta is re-proved key-by-key in ``-003-04``, not a blanket "ignore".
    """
    baseline = _pre_amendment()
    old_artifacts: dict[str, str] = baseline["artifacts"]  # type: ignore[assignment]
    old_verdict_locator: str = baseline["verdict_locator"]  # type: ignore[assignment]

    reader, result = _run(tmp_path)
    new_verdict_locator = result.locators[0]
    new_artifacts = {
        loc: reader.read_bytes(loc).decode("utf-8") for loc in result.locators
    }

    # The verdict value itself did NOT change — this is a row-2 run.
    assert result.verdict.verdict is Verdict.NOT_READY_FOR_RELEASE
    assert result.verdict.exit_code == 2
    assert result.verdict.decision_row is DecisionRow.BLOCKING_FINDINGS

    # Same artifact COUNT — the delta adds no state and removes none.
    assert len(new_artifacts) == len(old_artifacts)

    old_critical_locator = _sole_locator(old_artifacts, CRITICAL_SUBSYSTEMS_PRODUCER)
    new_critical_locator = _sole_locator(new_artifacts, CRITICAL_SUBSYSTEMS_PRODUCER)
    bumped_old = {old_verdict_locator, old_critical_locator}
    bumped_new = {new_verdict_locator, new_critical_locator}

    old_rest = {k: v for k, v in old_artifacts.items() if k not in bumped_old}
    new_rest = {k: v for k, v in new_artifacts.items() if k not in bumped_new}

    # The property is CONTENT-HASH stability, and the artifact key IS the content hash — so
    # assert that first and directly. This is what the byte comparison below was reaching for.
    assert set(new_rest) == set(old_rest), (
        "an artifact other than the two schema-bumped envelopes changed its content-addressed "
        "name; the bumps must be the ONLY intentional content-hash changes"
    )

    # 🔧 **CORRECTED 2026-08-29.** The comparison below was over raw envelope BYTES, which
    # includes `argus_version` — an envelope field carrying the package's release number. When
    # the tree moved 0.1.0 -> 1.0.0 to match the published `v1.0.0` tag, every stored artifact
    # differed from every rebuilt one and this failed, while reporting *"an artifact changed
    # bytes"* about a change that moved no content hash and no filename. NFR-D3 is explicit
    # that `content_hash` covers the PAYLOAD only, so a version-bearing envelope field cannot
    # move it — and the keys asserted equal above prove it did not. The version is normalised
    # out so this stays a test about the schema delta; `TC-ArgusAgent-DOCS-001-14` holds the
    # version's own agreement, and the evidence bundle — the one artifact that carries the
    # version INSIDE the hashed payload (DF-8-5-A) — is not in this corpus.
    def _without_version(artifacts: dict[str, str]) -> dict[str, str]:
        return {
            key: re.sub(r'"argus_version":"[^"]*"', '"argus_version":"<pinned>"', text)
            for key, text in artifacts.items()
        }

    assert _without_version(new_rest) == _without_version(old_rest), (
        "an artifact other than the two schema-bumped envelopes changed bytes, in a field "
        "other than `argus_version`; the bumps must be the ONLY intentional content changes"
    )
    # Both bumped envelopes DID move (that is the point of the bumps).
    assert new_verdict_locator != old_verdict_locator
    assert new_critical_locator != old_critical_locator


def test_TC_ArgusAgent_VERDICT_003_02_verdict_envelope_delta_is_exactly_two_keys(
    tmp_path: Path,
) -> None:
    """AC11 — the verdict payload differs ONLY by ``schema_version`` + ``decision_row``.

    Reverses the two amendment-introduced changes and requires the remainder to be
    byte-identical to the pre-amendment envelope payload. A reordered key, a changed
    ratio encoding or a dropped field would all surface here.
    """
    baseline = _pre_amendment()
    old_envelope = json.loads(
        baseline["artifacts"][baseline["verdict_locator"]]  # type: ignore[index]
    )
    old_payload = old_envelope["payload"]

    reader, result = _run(tmp_path)
    new_envelope = json.loads(reader.read_bytes(result.locators[0]).decode("utf-8"))
    new_payload = new_envelope["payload"]

    assert old_payload["schema_version"] == "1"
    assert new_payload["schema_version"] == VERDICT_SCHEMA_VERSION == "2"
    assert "decision_row" not in old_payload
    assert new_payload["decision_row"] == DecisionRow.BLOCKING_FINDINGS.value

    reverted = dict(new_payload)
    del reverted["decision_row"]
    reverted["schema_version"] = "1"
    assert canonical.dumps(reverted) == canonical.dumps(old_payload)

    # …and the envelope AROUND the payload is otherwise untouched. Three fields follow
    # the payload BY CONSTRUCTION and are not independent changes: the content_hash
    # (NFR-D3, hash over the payload) and the envelope's own schema_version, which
    # ``pipeline_persist`` sets to ``verdict.schema_version`` verbatim — ONE bump with one
    # source, not two.
    assert new_envelope["schema_version"] == new_payload["schema_version"]
    assert old_envelope["schema_version"] == old_payload["schema_version"]
    # `argus_version` joined this list on 2026-08-29, and the reason is a test-design fix
    # rather than an accommodation. This assertion's subject is the SCHEMA delta between a
    # stored v1 envelope and a freshly-built one; `argus_version` is an envelope field
    # carrying the package's release number, so it necessarily differs whenever the fixture
    # was recorded under a different release — it moved 0.1.0 -> 1.0.0 with the v1.0.0
    # version correction and broke three tests that are not about versions at all. Pinning it
    # here guaranteed a failure at every future bump while adding nothing: it is not part of
    # the schema change under test, and NFR-D3 keeps it out of `content_hash` (which covers
    # the payload only), so excluding it cannot hide a hash or filename movement. The
    # agreement between `pyproject.toml` and `argus.__version__` is held where it belongs, by
    # `TC-ArgusAgent-DOCS-001-14`.
    _derived = ("payload", "content_hash", "schema_version", "argus_version")
    assert {k: v for k, v in new_envelope.items() if k not in _derived} == {
        k: v for k, v in old_envelope.items() if k not in _derived
    }


def test_TC_ArgusAgent_VERDICT_003_04_critical_envelope_delta_is_exactly_two_changes(
    tmp_path: Path,
) -> None:
    """AC12 (Story 8.2) — the critical-subsystem payload differs ONLY by the stamp + the added key.

    The same shape as ``-003-02``, applied to the second bumped envelope: reverse the two
    DR-5-introduced changes and require the remainder to be byte-identical to the
    pre-amendment payload. A reordered key, a dropped ``origins`` entry, or a critical
    set the eligibility filter quietly re-shaped would all surface here.

    ``vacuous_basic`` has no heuristic critical hits at all (measured), so the filter
    removes nothing and the added key is EMPTY — the stamp is the only substantive
    delta, and ``paths`` must be provably unmoved.
    """
    baseline = _pre_amendment()
    old_artifacts: dict[str, str] = baseline["artifacts"]  # type: ignore[assignment]
    old_envelope = json.loads(old_artifacts[_sole_locator(old_artifacts, CRITICAL_SUBSYSTEMS_PRODUCER)])
    old_payload = old_envelope["payload"]

    reader, result = _run(tmp_path)
    new_artifacts = {
        loc: reader.read_bytes(loc).decode("utf-8") for loc in result.locators
    }
    new_envelope = json.loads(new_artifacts[_sole_locator(new_artifacts, CRITICAL_SUBSYSTEMS_PRODUCER)])
    new_payload = new_envelope["payload"]

    assert old_payload["schema_version"] == "1"
    assert new_payload["schema_version"] == CRITICAL_SUBSYSTEMS_SCHEMA_VERSION == "2"
    assert "heuristic_excluded_ineligible" not in old_payload
    assert new_payload["heuristic_excluded_ineligible"] == {}
    # The critical set itself did NOT move — the filter had nothing to remove here.
    assert new_payload["paths"] == old_payload["paths"]

    reverted = dict(new_payload)
    del reverted["heuristic_excluded_ineligible"]
    reverted["schema_version"] = "1"
    assert canonical.dumps(reverted) == canonical.dumps(old_payload)

    # …and the envelope AROUND the payload is otherwise untouched (the -003-02 rule):
    # the content_hash and the envelope schema_version follow the payload BY
    # CONSTRUCTION and are not independent changes.
    assert new_envelope["schema_version"] == new_payload["schema_version"]
    assert old_envelope["schema_version"] == old_payload["schema_version"]
    # `argus_version` joined this list on 2026-08-29, and the reason is a test-design fix
    # rather than an accommodation. This assertion's subject is the SCHEMA delta between a
    # stored v1 envelope and a freshly-built one; `argus_version` is an envelope field
    # carrying the package's release number, so it necessarily differs whenever the fixture
    # was recorded under a different release — it moved 0.1.0 -> 1.0.0 with the v1.0.0
    # version correction and broke three tests that are not about versions at all. Pinning it
    # here guaranteed a failure at every future bump while adding nothing: it is not part of
    # the schema change under test, and NFR-D3 keeps it out of `content_hash` (which covers
    # the payload only), so excluding it cannot hide a hash or filename movement. The
    # agreement between `pyproject.toml` and `argus.__version__` is held where it belongs, by
    # `TC-ArgusAgent-DOCS-001-14`.
    _derived = ("payload", "content_hash", "schema_version", "argus_version")
    assert {k: v for k, v in new_envelope.items() if k not in _derived} == {
        k: v for k, v in old_envelope.items() if k not in _derived
    }


def test_TC_ArgusAgent_VERDICT_003_03_two_runs_are_byte_identical(tmp_path: Path) -> None:
    """AC11 / DR-9 — determinism is unaffected: two runs produce identical bytes."""
    reader_a, res_a = _run(tmp_path / "a")
    reader_b, res_b = _run(tmp_path / "b")

    arts_a = {loc: reader_a.read_bytes(loc) for loc in res_a.locators}
    arts_b = {loc: reader_b.read_bytes(loc) for loc in res_b.locators}
    assert arts_a == arts_b
