"""Guard-fire telemetry — records WHICH guard went RED, and at which sha.

Registered in `architecture.md` §Enforcement under *Guard-fire ledger enforcement*
(added 2026-08-23). This file is the mechanism that makes the ledger half of that
rule real; the RETIREMENT half is deliberately not in force and nothing here
proposes, scores or deletes a guard.

**The problem it exists to fix, measured.** The tree carries 1,251 distinct guard
ids and **967 of them (77%) are named nowhere outside their own test file** — no
commit, no story, no retrospective. Zero test files or scripts have ever been
deleted in 189 commits. On that evidence *"this guard has never caught anything"*
is indistinguishable from *"nobody wrote it down"*, so no sunset rule can act.
This hook removes the second reading by writing the observation down
automatically, because the alternative — asking a human to remember — is the
mechanism `AI-E14-1`..`AI-E14-9` measured as not-addressed six retrospectives
running.

**It records an OBSERVATION, never a verdict.** A row here means "guard X was
observed RED at sha Y". It is NOT the `guard-fires.md` ledger's definition of
*caught a real defect*, which additionally requires the sha of a fix that changes
a non-test file. Resolving an observation into a fire is a human act over this
data; this file does not attempt it, and deliberately ships no promotion pipeline
— an audit of process apparatus should not answer itself with more apparatus.

**Where it writes, and why there.** `.argus/guard-fires.jsonl` — already gitignored.
A hook that dirtied the working tree would break `release_preflight`'s E1
dirty-worktree refusal and `tests/test_dogfood_artifact_currency.py`, i.e. the
telemetry would start failing the build it is meant to inform. Append-only JSONL:
one self-describing row per observation, never rewritten (§3.4).

**It can never fail the suite.** Every path is wrapped: a broken hook that raised
during collection or reporting would take down 1,703 passing tests to record a
statistic. On any error it silently records nothing. Telemetry is not allowed to
be load-bearing.

Set `ARGUS_GUARD_FIRES=0` to disable.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
_LEDGER = _REPO_ROOT / ".argus" / "guard-fires.jsonl"

# Test functions carry the guard id in their NAME with underscores
# (`test_TC_ArgusAgent_PRECISION_001_134_a_map_override...`); the canonical id
# everything else cites is hyphenated. Translate rather than store both.
_GUARD_IN_NAME = re.compile(r"TC_ArgusAgent_([A-Z0-9]+)_(\d+)_(\d+[a-z]?)")

_SHA: str | None = None
_ENABLED = os.environ.get("ARGUS_GUARD_FIRES", "1") != "0"


def _head_sha() -> str:
    """Resolve HEAD once per session. `unknown` when git cannot answer."""
    global _SHA
    if _SHA is None:
        try:
            out = subprocess.run(
                ["git", "-C", str(_REPO_ROOT), "rev-parse", "HEAD"],
                capture_output=True,
                timeout=10,
            )
            _SHA = out.stdout.decode("utf-8", "replace").strip() or "unknown"
        except Exception:
            _SHA = "unknown"
    return _SHA


def _guard_id(nodeid: str) -> str | None:
    """Return the canonical hyphenated guard id a nodeid names, or None.

    A test with no `TC_ArgusAgent_*` in its name is not a registered guard — 1,012
    of this suite's tests are ordinary tests — and is not recorded. Silence here
    is correct: the ledger is about the guard population, not about every failure.
    """
    m = _GUARD_IN_NAME.search(nodeid)
    if m is None:
        return None
    return f"TC-ArgusAgent-{m.group(1)}-{m.group(2)}-{m.group(3)}"


def _append(row: dict[str, Any]) -> None:
    """Append one JSONL row. Any failure is swallowed — see the module docstring."""
    try:
        _LEDGER.parent.mkdir(parents=True, exist_ok=True)
        with _LEDGER.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    except Exception:
        return


def pytest_runtest_logreport(report: Any) -> None:
    """Record a guard observed RED during its call phase.

    Only ``when == "call"`` is recorded: a setup/teardown error is an environment
    fault, not a guard finding anything, and recording it would fill the ledger
    with noise that makes the real signal harder to see rather than easier.
    """
    if not _ENABLED:
        return
    try:
        if getattr(report, "when", None) != "call" or not getattr(report, "failed", False):
            return
        guard = _guard_id(getattr(report, "nodeid", "") or "")
        if guard is None:
            return
        _append(
            {
                "guard_id": guard,
                "nodeid": report.nodeid,
                "observed_red_at_sha": _head_sha(),
                "observed_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "record_kind": "observation",
            }
        )
    except Exception:
        return
