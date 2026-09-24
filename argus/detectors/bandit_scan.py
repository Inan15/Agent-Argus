"""Bandit SAST findings-only detector (impure shell / pure core) — Stage 1, wq-620.

Drivers: `company/argus-finding-shape-ruling-2026-09-22.md` Part 1 Stage 1 (Zero's
2026-09-22 ruling, measured by Amphion under wq-615): wire ``bandit`` on the SAME
pattern the live :class:`~argus.detectors.secret_scan.SecretScanDetector` already
uses — ``pipeline_stages.py`` folds ONLY this detector's ``findings``, never its
``entries`` (there are none). **Not through the breadth channel at all.**

Three invariants the ruling makes non-negotiable (do not add to this module without
re-reading them first):

- **Zero schema change.** ``FindingDraft`` keeps its eight fields; ``Recording``
  keeps its ten. Bandit's severity / confidence / CWE / issue text are NOT carried
  (that is Stage 2, the deferred ``evidence`` field, a separate ruling).
- **Zero classifier change.** This module does not import from, call, or in any way
  reach ``argus.detectors.tool_runner`` — ``classify_outcomes`` never sees a bandit
  row. The breadth channel stays ``radon`` ONLY (``tool_runner.py:48``).
- **Coverage ledger byte-identical.** :class:`BanditScanDetector` NEVER returns a
  non-empty ``entries`` tuple — mirroring the secret-scan precedent exactly. A repo
  bandit finds nothing in (or that this detector never reaches) produces exactly the
  ledger it produced before this module existed.

Scope decision (LOCKED for Stage 1, per the ruling's own instruction to decide and
say what was chosen): **non-test source, severity >= MEDIUM** — the same scope the
CI gate at ``.github/workflows/audit-ci.yml`` already blocks on
(``bandit -r argus -f txt --severity-level medium``). Unscoped, bandit emits 7,031
findings on this repo's own ``argus/`` + ``tests/`` tree, 6,829 of them ``B101
assert_used`` under ``tests/`` — the ruling calls that the largest measured cost in
the whole question (§5.1). The caller (``argus/pipeline_stages.py``) is responsible
for excluding test files from the target list BEFORE calling :meth:`run` — using
Argus's own content-aware ``is_test_file`` classification, not a path glob — and
``--severity-level medium`` on the bandit invocation itself does the severity half.

The pure / impure split (AR8, mirroring ``tool_runner.py``)
-------------------------------------------------------------
- an IMPURE shell (:func:`bandit_invoker`) that shells out to ``python -m bandit``
  over the target files (AC7 safe-bounded-subprocess rules: ``shell=False``, an
  explicit arg list, a hard ``timeout=``, explicit UTF-8 decode with
  ``errors="replace"``). ``bandit``'s public ``BanditManager`` API reads from disk
  (wq-447), so there is no in-process, no-subprocess path available the way
  ``radon``'s library API offers one.
- a PURE core (:meth:`BanditScanDetector.run`'s finding construction) that maps the
  captured, already-redacted :class:`BanditIssue` rows to ``FindingDraft`` /
  ``Recording``. No raw bandit stdout/stderr, source line (``code``), issue text, CWE
  link, or host path EVER reaches a stored field (NFR-S1) — only the four fields
  that survive the journey described in the ruling's §3 table: ``filename`` ->
  ``file_path``, ``line_range[0]``/``line_range[-1]`` -> ``start_line``/``end_line``,
  ``test_id`` -> ``rule_id`` (prefixed ``bandit_``).

Findings are ``advisory=True``, ``depth_supported=None`` — the same V1
advisory-by-contract discipline ``tool_runner.py`` and ``secret_scan.py`` both use
(cross-cutting #6): a heuristic SAST hit can never move the verdict to blocking on
its own.

Best-effort, not a new hard dependency
---------------------------------------
``bandit`` is NOT added to ``[project.dependencies]`` by this module. If it is not
importable (``importlib.util.find_spec("bandit") is None``), :func:`bandit_invoker`
degrades to :attr:`BanditOutcome.UNAVAILABLE` and the detector emits no findings —
the AR1 "SAST is the OPTIONAL / best-effort family" framing already in
``tool_runner.py:51``, extended here rather than contradicted.
"""

from __future__ import annotations

import enum
import importlib.util
import json
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from argus.detectors.base import DetectorResult, FindingDraft, build_recording

__all__ = [
    "BANDIT_TOOL_ID",
    "BANDIT_MIN_SEVERITY",
    "BanditScanError",
    "BanditOutcome",
    "BanditIssue",
    "BanditInvocationResult",
    "BanditInvoker",
    "bandit_invoker",
    "BanditScanDetector",
]

# Not versioned via a schema-version field: this module mints no new frozen model
# that is ever persisted (`BanditIssue` / `BanditInvocationResult` are transient,
# in-process carriers — only `FindingDraft` -> `Recording` is ever built, and both
# are UNCHANGED, Stage-1's own zero-schema-change invariant).
BANDIT_TOOL_ID = "bandit"

# The scope decision (locked for Stage 1) — matches the CI gate exactly.
BANDIT_MIN_SEVERITY = "medium"

_TIMEOUT_SECONDS = 120


class BanditScanError(ValueError):
    """Raised on a MALFORMED ARGUMENT to the detector (AR10 typed failure).

    A tool failure (bandit missing / crashing / timing out) is NEVER raised here —
    it degrades to :attr:`BanditOutcome.UNAVAILABLE` / ``CRASHED`` / ``TIMED_OUT`` and
    the detector emits no findings for that run. Only a programmer-supplied bad
    argument raises.
    """


class BanditOutcome(str, enum.Enum):
    """Closed whole-invocation outcome (mirrors the ``tool_runner.py`` ``ToolOutcome``
    naming, but is a SEPARATE, locally-scoped enum — this module never imports from
    ``tool_runner.py``, by design; see the module docstring's second invariant).

    - ``OK`` — bandit ran (exit 0 = clean, exit 1 = issues found — BOTH are a
      successful run; bandit's per-file parse failures land in its own ``errors``
      array and never fail the whole invocation).
    - ``UNAVAILABLE`` — the ``bandit`` package is not importable.
    - ``CRASHED`` — bandit exited with an unexpected code, or its stdout was not
      parseable JSON.
    - ``TIMED_OUT`` — the subprocess exceeded the bounded timeout.
    """

    OK = "ok"
    UNAVAILABLE = "unavailable"
    CRASHED = "crashed"
    TIMED_OUT = "timed_out"


class BanditIssue(BaseModel):
    """One redaction-safe bandit result (NFR-S1) — frozen, ``extra="forbid"``.

    Carries ONLY the four fields the ruling's §3 table found survive into a
    ``FindingDraft``: nothing else bandit reports (``code``, ``issue_text``,
    ``issue_cwe``, ``issue_severity``, ``issue_confidence``, ``more_info``,
    ``test_name``, ``col_offset``) is captured here at all — the absence of the
    field is the structural guarantee (the 2.5 ``SecretFindingEvidence`` /
    ``VacuousTestScore`` precedent), not a redaction step performed on a wider model.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_path: str = Field(..., description="Repo-relative POSIX path bandit flagged.")
    start_line: int = Field(..., ge=1, description="1-based inclusive start line.")
    end_line: int = Field(..., ge=1, description="1-based inclusive end line.")
    test_id: str = Field(..., description="Bandit's own rule id (e.g. 'B301').")


class BanditInvocationResult(BaseModel):
    """The frozen, redaction-safe capture the impure shell hands the pure core.

    NO raw stdout / stderr field exists on this model AT ALL (the structural NFR-S1
    guarantee) — only the closed :class:`BanditOutcome` and the already-filtered,
    already-redacted :class:`BanditIssue` rows.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    outcome: BanditOutcome = Field(..., description="Closed whole-invocation outcome.")
    issues: tuple[BanditIssue, ...] = Field(
        default=(), description="Redaction-safe issues at or above BANDIT_MIN_SEVERITY."
    )


# The injected impure-shell seam (AR8's testability seam, mirroring `ToolInvoker`):
# (repo_root, target file paths) -> a captured, redaction-safe result.
BanditInvoker = Callable[[Path, Sequence[str]], BanditInvocationResult]


def _normalize_bandit_filename(raw: str) -> str:
    """Undo bandit's ``./`` / ``.\\`` relative-path prefix (measured empirically, wq-620).

    Bandit echoes back whatever relative path it was given, but prefixes it with the
    OS's ``os.curdir + os.sep`` (``./`` on POSIX, ``.\\`` on Windows) and does NOT
    otherwise normalize internal separators. Given a POSIX-style input (the house
    convention — ``AstIndexEntry.file_path`` is always repo-relative POSIX), this
    reverses that prefix and normalizes any stray backslash, reproducing the exact
    input path.
    """
    normalized = raw.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def bandit_invoker(repo_root: Path, file_paths: Sequence[str]) -> BanditInvocationResult:
    """Default IMPURE invoker — shells out to ``python -m bandit`` over *file_paths*.

    AC7 safe-bounded-subprocess rules: ``shell=False`` (an explicit arg list, never a
    shell string), a hard ``timeout=``, explicit UTF-8 decode with
    ``errors="replace"``. Never raises out on a tool failure (AR10) — every failure
    mode maps to a closed :class:`BanditOutcome`; raw stdout/stderr is read ONLY to
    parse JSON or detect failure and is NEVER stored on the returned model (NFR-S1).

    An empty *file_paths* is a no-op: bandit is not even spawned, so a repo with
    nothing in scope pays zero cost and calls no subprocess at all.
    """
    if not file_paths:
        return BanditInvocationResult(outcome=BanditOutcome.OK)

    if importlib.util.find_spec("bandit") is None:
        return BanditInvocationResult(outcome=BanditOutcome.UNAVAILABLE)

    command = [
        sys.executable,
        "-m",
        "bandit",
        "-f",
        "json",
        "-q",
        "--severity-level",
        BANDIT_MIN_SEVERITY,
        *file_paths,
    ]
    try:
        completed = subprocess.run(
            command,
            cwd=repo_root,
            shell=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return BanditInvocationResult(outcome=BanditOutcome.TIMED_OUT)
    except OSError:
        return BanditInvocationResult(outcome=BanditOutcome.CRASHED)

    # Bandit's own contract: exit 0 = clean, exit 1 = issues found — BOTH are a
    # successful run. Any other code (a usage error, an internal crash) is not.
    if completed.returncode not in (0, 1):
        return BanditInvocationResult(outcome=BanditOutcome.CRASHED)

    try:
        payload = json.loads(completed.stdout)
        raw_results = payload["results"]
    except (json.JSONDecodeError, KeyError, TypeError):
        return BanditInvocationResult(outcome=BanditOutcome.CRASHED)

    issues: list[BanditIssue] = []
    for result in raw_results:
        try:
            line_range = result["line_range"]
            issues.append(
                BanditIssue(
                    file_path=_normalize_bandit_filename(str(result["filename"])),
                    start_line=int(line_range[0]),
                    end_line=int(line_range[-1]),
                    test_id=str(result["test_id"]),
                )
            )
        except (KeyError, IndexError, TypeError, ValueError):
            # A malformed single result is dropped, not a whole-invocation crash
            # (AR10) — bandit's JSON shape is not ours to guarantee row-by-row.
            continue

    return BanditInvocationResult(outcome=BanditOutcome.OK, issues=tuple(issues))


class BanditScanDetector:
    """Findings-only SAST detector — NEVER mints a coverage entry (Stage 1, wq-620).

    Satisfies the ``detectors.base.Detector`` protocol structurally. The impure
    invocation is the injected :class:`BanditInvoker` (default :func:`bandit_invoker`);
    finding construction is PURE (no clock, no ``uuid4``/``random``, no LLM).
    """

    rule_id = "bandit_finding"

    def __init__(self, *, invoker: BanditInvoker | None = None) -> None:
        self._invoker: BanditInvoker = invoker if invoker is not None else bandit_invoker

    def run(
        self,
        *,
        repo_root: Path,
        targets: Sequence[str],
    ) -> DetectorResult:
        """Run bandit over *targets* (already scope-filtered by the caller) and emit
        findings ONLY — ``entries`` is always ``()`` (the coverage-ledger invariant).

        *targets* must already exclude test files (the caller's job — the content-
        aware ``is_test_file`` classification, not this module). Raises
        :class:`BanditScanError` (AR10) ONLY on a malformed argument; a tool failure
        degrades to an empty result, never a crash.
        """
        if not isinstance(repo_root, Path):
            raise BanditScanError("repo_root must be a Path")
        if not isinstance(targets, Sequence) or isinstance(targets, (str, bytes)):
            raise BanditScanError("targets must be a sequence of str file paths")
        for target in targets:
            if not isinstance(target, str) or not target:
                raise BanditScanError("each target must be a non-empty str file path")

        if not targets:
            return DetectorResult()

        try:
            invocation = self._invoker(repo_root, tuple(targets))
        except Exception:  # noqa: BLE001 — a raising invoker degrades, never leaks (AR10)
            invocation = BanditInvocationResult(outcome=BanditOutcome.CRASHED)
        if not isinstance(invocation, BanditInvocationResult):
            invocation = BanditInvocationResult(outcome=BanditOutcome.CRASHED)

        if invocation.outcome is not BanditOutcome.OK or not invocation.issues:
            return DetectorResult()

        findings = []
        seen: set[tuple[str, int, int, str]] = set()
        for issue in sorted(
            invocation.issues,
            key=lambda i: (i.file_path, i.start_line, i.end_line, i.test_id),
        ):
            identity = (issue.file_path, issue.start_line, issue.end_line, issue.test_id)
            if identity in seen:
                continue
            seen.add(identity)
            draft = FindingDraft(
                file_path=issue.file_path,
                start_line=issue.start_line,
                end_line=issue.end_line,
                rule_id=f"{BANDIT_TOOL_ID}_{issue.test_id}",
                advisory=True,
            )
            findings.append(
                build_recording(draft, depth_supported=None, claim_present=False)
            )

        return DetectorResult(findings=tuple(findings))


if TYPE_CHECKING:  # pragma: no cover - static conformance pin; TYPE_CHECKING is False at runtime
    # Story 18.4 / AC2 - the STATIC conformance pin. `mypy argus` is a blocking CI gate
    # and this line is what it checks: drop `rule_id`, retype it non-`str`, drop `run` or
    # regress its return type and THIS goes red. It lives inside `argus/` on purpose -
    # there is no [tool.mypy] section in this repository and CI runs `mypy argus` only, so
    # the same pin written under `tests/` would be enforced by nothing.
    from argus.detectors.base import Detector

    _DETECTOR_CONFORMANCE_PIN: Detector = BanditScanDetector()
