"""Shared corpora and controls for the Story 12.3 stage-memoization guards.

NOT a test module — a fixture module, following the ``tests/cartridges/_cartridge.py``
precedent. It exists because the Story 12.3 guards outgrew the NFR-M1 1200-line ceiling and
were split along a COHESION boundary into two siblings that must not drift apart:

* ``tests/test_stage_memo_wiring.py`` — *is the cache load-bearing?* The two mandatory
  anti-vacuity controls, the key the production path derives (AC2), and HIT == COLD (AC3).
* ``tests/test_stage_memo_contract.py`` — *can the cache lie?* The correctness surface (AC4),
  the invalidation contract over the wired path (AC5), the deep-pass fence (AC6), and the
  no-new-surface guards (AC1).

The corpora, the request builder and above all the CONTROL-1 spy live here so both files
observe the SAME seam. Two copies of a spy is two definitions of what "the stage ran" means,
and the whole story turns on that one measurement.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from argus.detectors.base import FindingDraft, build_recording
from argus.ledger.coverage_ledger import CoverageDepth
from argus.models import AuditRequest

# ─────────────────────────────────────────────────────────────────────────────
# Synthetic corpora — two verdict classes (AC3.3 / DN-8)
# ─────────────────────────────────────────────────────────────────────────────
#
# DN-8: a cold/warm proof pinned only to RELEASE_READY could be green because there is
# nothing to serve — an empty finding set round-trips through a broken store perfectly.
# So every byte-identity leg runs over BOTH a clean repo and one that carries a real
# blocking finding.

_APP_SOURCE = '''"""A small application module."""


def add(a: int, b: int) -> int:
    return a + b


def subtract(a: int, b: int) -> int:
    return a - b
'''

_TEST_SOURCE = """from app.service import add


def test_add():
    assert add(1, 2) == 3
"""

# THE PLANTED VACUOUS TEST — the shape of the `vacuous_basic` cartridge, reused rather than
# invented: it calls the SUT but asserts a Mock's own configured return value, so it is flagged
# by the AST vacuous path (`vacuous_test_ast`) as a VERDICT-ELIGIBLE finding. That eligibility
# is the point — an advisory-only finding never moves a verdict, so it could not give this file
# its second verdict class.
_VACUOUS_TEST_SOURCE = '''"""A test that passes while asserting nothing about the SUT."""

from unittest.mock import Mock

from app.service import add


def test_add_is_vacuous():
    add(1, 2)
    fake = Mock()
    fake.calculate.return_value = 6
    pretended = fake.calculate()
    assert pretended == 6
'''

# A hardcoded credential. Carried by the blocked corpus so the CONTAINMENT sweep (`-90`) has a
# real secret to hunt for in the persisted cache bytes. It is a SYNTHETIC literal matching no
# real provider's key beyond its shape.
_LEAKY_SOURCE = '''"""A module that hardcodes a credential."""

AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"


def connect(endpoint: str) -> str:
    return f"{endpoint}:{AWS_SECRET_ACCESS_KEY}"
'''


def _clean_repo(root: Path, *, modules: int = 2) -> Path:
    """A minimal auditable repository with no blocking finding (the RELEASE_READY class)."""
    (root / "app").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)
    for i in range(modules):
        name = "service.py" if i == 0 else f"service{i}.py"
        (root / "app" / name).write_text(_APP_SOURCE, encoding="utf-8")
    (root / "tests" / "test_service.py").write_text(_TEST_SOURCE, encoding="utf-8")
    return root


def _blocked_repo(root: Path) -> Path:
    """A repository that audits NOT_READY_FOR_RELEASE (the second verdict class, DN-8).

    Four clean modules keep the deep ratio above the 60% row-3 gate — below it the only
    reachable verdict is ``INSUFFICIENT_COVERAGE``, which would make this corpus a *different*
    kind of non-green rather than the blocking-findings kind the tamper leg needs. The planted
    vacuous test supplies the verdict-eligible finding; the credentials module supplies the
    secret bytes `-90` sweeps for.
    """
    (root / "app").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)
    for i in range(4):
        name = "service.py" if i == 0 else f"service{i}.py"
        (root / "app" / name).write_text(_APP_SOURCE, encoding="utf-8")
    (root / "tests" / "test_service.py").write_text(_VACUOUS_TEST_SOURCE, encoding="utf-8")
    (root / "app" / "creds.py").write_text(_LEAKY_SOURCE, encoding="utf-8")
    return root


def _request(repo: Path, **overrides: object) -> AuditRequest:
    """Build the frozen request through the real model (never a hand-built stub)."""
    fields: dict[str, object] = {
        "repo_path": str(repo),
        "commit": "HEAD",
        "budget": 0,
        "materiality_bar": "",
        "coverage_scope": "application",
    }
    fields.update(overrides)
    return AuditRequest(**fields)  # type: ignore[arg-type]


def _cache_slots(repo: Path) -> tuple[Path, ...]:
    """Every persisted cache slot, read off the FILESYSTEM (§0.5 trap 4: `.argus/` is gitignored)."""
    cache_dir = repo / ".argus" / "cache"
    if not cache_dir.is_dir():
        return ()
    return tuple(sorted(p for p in cache_dir.iterdir() if p.is_file()))


class _StageSpy:
    """CONTROL 1 — a counting spy over the REAL ``_detect_per_file`` seam.

    Wraps rather than replaces: the stage still really runs on a miss, so a cold run is a
    genuine audit and not a fixture. ``calls`` is the whole assertion surface — a warm run
    that executed the stage even once did not take a hit, however identical its bytes.
    """

    def __init__(self, real: Any) -> None:
        self._real = real
        self.calls = 0

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.calls += 1
        return self._real(*args, **kwargs)


def _spy_on_detect_stage(monkeypatch: pytest.MonkeyPatch) -> _StageSpy:
    """Install the CONTROL-1 spy on the seam the pipeline actually calls."""
    import argus.pipeline as pipeline_module

    spy = _StageSpy(pipeline_module._detect_per_file)
    monkeypatch.setattr(pipeline_module, "_detect_per_file", spy)
    return spy


def _poison_finding(file_path: str) -> Any:
    """A VALID, verdict-blocking recording that the real run would never produce here.

    Minted through the real 1.2 builder, so it is schema-valid in every respect —
    the poison is its PRESENCE, not its shape. ``depth_supported is not None`` is the
    verdict gate's own eligibility predicate (`verdict_gate.py`), so this finding is
    verdict-BLOCKING and its arrival must move the verdict off RELEASE_READY.
    """
    return build_recording(
        FindingDraft(
            file_path=file_path,
            start_line=1,
            end_line=1,
            rule_id="poison_positive_control",
            advisory=False,
        ),
        depth_supported=CoverageDepth.AUDITED_DEEP,
        claim_present=True,
    )
