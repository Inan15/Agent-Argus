"""Reproducible dogfood PROOF-RUN generator (Story 7.2 — the CAPSTONE).

Subject honesty (Story 8.5 / AC2, restated by Story 9.2 / D10): this generator's default
enumeration scope is :data:`_DEFAULT_SCOPE_PREFIX` = ``"argus"``, so what it runs is a
SELF-audit of THIS package. Story 7.2 originally ran it over the Minions platform
repository; that source is not in this repository and the run cannot be re-executed here.
The preserved record of the independent run is
``minions-dogfood-proof-story-7-2-superseded.md``, and the ``minions-dogfood-`` filename
prefix on the artifacts is a retained HISTORICAL identifier, not a claim about the
subject. Everywhere below, the audited tree is the one the SCOPE names — never a
repository this module does not read.

Verification area ArgusAgent-DOGFOOD (``TC-ArgusAgent-DOGFOOD-001-NN`` — CONTINUING from the 7.1
index; 7.1 locked ``...-01..17``, so 7.2 starts at ``...-18``). Drivers: ArgusAgent-FR-30
(headless invocation contract — the dogfood RUNS the frozen ``run_audit_detailed``
over the scoped tree), ArgusAgent-FR-21 / OI3 (the empirically-sized ``$X`` = 843
credit ceiling from 7.1 — the run completes within it AND halts + downgrades if
breached), ArgusAgent-FR-29 / NFR-A1 / NFR-D3 (the SIGNED evidence bundle — content-hashed,
prev-hash-chained, schema-versioned envelope; the point-in-time stamp is the envelope
``created_at``, EXCLUDED from the hash — REUSED from 4.3/1.1, no fork), ArgusAgent-FR-17 /
NFR-A3 (the negative-assurance verdict + scope statement + disclaimer the bundle
exports — REUSED from 4.1), ArgusAgent-FR-20 / FR13 (the defect-cartridge precision
substrate + the ``finding_match_key`` adjudication identity — the REAL dogfood findings
laid out ADJUDICATION-READY for the later human TP/FP judgment), ArgusAgent-NFR-D1 / P1 (the
dogfood run is 100% reproducible on the same repo content — byte-identical verdict +
bundle bytes; no clock/float/set-order in the hashed payload), ArgusAgent-NFR-S1 / S3 (NO
audited source byte / secret value in the proof artifact / bundle / any persisted
``.argus/`` artifact — the no-source-retention moat over the REAL repo), ArgusAgent-AR4 (int
credits / ``Fraction`` ratios — NEVER float in any persisted figure), ArgusAgent-AR7 (REUSE
by import — no fork of the pipeline / bundle / serializer / lint / precision harness /
7.1 plan), ArgusAgent-AR8 (pure/impure separation — Story 9.2 made it STRUCTURAL: the
frozen result types live in ``proof_types.py`` and the renderers in ``proof_render.py``,
neither of which may import this impure shell), ArgusAgent-AR10
(typed failure — :class:`DogfoodProofError`, never a bare traceback), ArgusAgent-NFR-M1/M2
(≤1200-line files; the frozen Epic-1..6 + 7.1 contracts + the 4.3/6.5 SHAPES are
unchanged — this module COMPOSES them, edits none).

What this module IS (partial-reuse note, AI-E5-7 — narrate PRECISELY)
--------------------------------------------------------------------
It REUSES, BY IMPORT: the frozen ``pipeline.run_audit_detailed`` (the Tier-A,
zero-LLM-token audit shell), the 7.1 ``dogfood.partition_plan.build_full_repo_plan``
(the 4-unit partition map + the empirical ``$X`` = 843 sizing — CONSUMED, not
re-authored), the 4.3 ``evidence.bundle.build_evidence_bundle`` /
``persist_evidence_bundle`` / ``bundle_to_canonical_bytes`` (the SIGNED bundle export
+ the single 1.1 serializer + the 1.1 prev-hash-chained envelope), the 4.2
``store.integrity.lint_referential_integrity`` (the referential-integrity report the
bundle includes), the 1.3 ``ApaaStoreWriter`` / ``ApaaStoreReader``, and the 6.6
``precision.replay_harness.finding_match_key`` (the adjudication identity shape). It
ADDS: the dogfood snapshot-materialize + run orchestration (``run_dogfood``), the
adjudication-ready finding aggregation (``adjudication_rows``), and the within-ceiling +
3.2-halt cost accounting (``cost_summary`` — REUSING the 3.1 ``account_spend``). Since
Story 9.2 it RE-EXPORTS, rather than defines, the five frozen result dataclasses
(``proof_types.py``) and the ``.md`` proof-artifact renderer
(``render_proof_markdown``, ``proof_render.py``) — the public import surface is
unchanged. It adds NO forked pipeline, NO second bundle model / serializer / hasher,
NO LLM dispatch, NO new ``cli.py`` flag / HTTP route / CI job.

Why a materialized snapshot repo (the LOCKED dogfood-run mechanism, DN-DOGFOOD-REUSE)
------------------------------------------------------------------------------------
``run_audit_detailed`` calls ``load_repo_at_commit`` which REFUSES a drifted working
tree (HEAD must BE the pin AND ``git status --porcelain`` must be empty — Story 1.4).
A live working tree generally cannot satisfy this: it carries untracked and modified
paths. Rather than fork/relax the frozen loader (out of scope), this
generator MIRRORS the 6.5 ``_cartridge.stage_cartridge`` pattern the whole precision
substrate already uses: it enumerates the git-TRACKED source files under the configured
:data:`_DEFAULT_SCOPE_PREFIX` (holding out the configured exclusion prefixes — via the
SAME 7.1 ``enumerate_minions_source_files`` scope logic, so the dogfood audits the SAME
tree the 7.1 plan sized),
COPIES them into a fresh temp directory, ``git init``s + commits ONCE, and audits that
clean on-pin snapshot. The audited BYTES are the REAL tracked source of the scoped tree at the current
tracked commit (recorded as ``commit_descriptor`` provenance) — this is a real dogfood
over real committed code, NOT a cartridge. The snapshot commit SHA varies per run
(author/commit timestamps), but the SHA is NOT part of the hashed verdict/bundle
payload (NFR-D3 excludes volatile fields), so the run is byte-reproducible for the same
tracked content (NFR-D1/P1 — verified by a committed test).

The honest ``grade: demo-heuristic-only`` flag (DN-GRADE — the red-team guard)
-----------------------------------------------------------------------------
``run_audit_detailed`` wires NO ``LLMDispatchPort`` — it is Tier-A / zero-LLM-token
(NFR-D2; the ``audit/deep_audit.py`` deep-audit seam is a SEPARATE injected port NOT
wired into the live pipeline). So the dogfood run is heuristic-only. This module carries
the honest ``grade: demo-heuristic-only`` flag + the externalization-guard language on
the PROOF ARTIFACT and on the pure :class:`DogfoodProofRun` wrapper — it does NOT mutate
the frozen 4.1 ``NegativeAssuranceVerdict`` / 4.3 ``EvidenceBundle`` SHAPE (DN-GRADE:
the additive frozen-model field was NOT needed — the wrapper + artifact carry the grade,
and every finding already carries ``depth_supported=None`` = advisory / verdict-
ineligible, which IS the structural heuristic-only signal). A Tier-A demo run is NEVER
presented as externalization / assurance evidence.

The OI1 provisional-gate keystone (DN-PROVISIONAL — do NOT soften)
------------------------------------------------------------------
The ≥80%-precision gate STAYS PROVISIONAL. This generator produces the REAL dogfood
findings + lays them ADJUDICATION-READY (per-finding ``rule_id`` + locators +
advisory-vs-blocking verdict-eligibility, mapped to the 6.6 ``finding_match_key`` shape)
so the later human Eng-Lead + QA-Lead TP/FP adjudication can clear the gate on REAL data.
It does NOT run the adjudication, NEVER flips ``protocol_cleared``, NEVER flips the 6.5
``precision_gate_status()`` marker, and presents NO ≥80% number as authoritative /
cleared. The still-open human step is a follow-up defer (six CC-3 fields).

Pure/impure separation (AR8) — STRUCTURAL since Story 9.2, not narrated
-----------------------------------------------------------------------
Before Story 9.2 the pure derivations, the pure value types and the pure renderer all
lived in this impure module, and the separation existed only as this paragraph. The
``DF-8-5-D`` extraction made it a property of the import graph, which is one directed
edge deep and cannot be violated without a cycle Python refuses to load::

    proof_run  (IMPURE)  ->  proof_render  (PURE)  ->  proof_types  (PURE)

- ``argus/dogfood/proof_types.py`` — the five frozen result dataclasses. No I/O.
- ``argus/dogfood/proof_render.py`` — :func:`render_proof_markdown` and its helpers,
  plus the externalization-guard sentence they render. No I/O.
- THIS module — the impure shell: :func:`enumerate_tracked_sources` +
  :func:`materialize_snapshot` (``git`` + file copy), :func:`run_dogfood` (the audit +
  integrity lint + bundle export + persist), :func:`build_dogfood_proof` (the full
  orchestration) — plus two derivations that are pure but belong to the run rather than
  to the artifact: :func:`adjudication_rows` and :func:`cost_summary`.

Every name from both siblings is re-exported here and :data:`__all__` is UNCHANGED, so
no call site moved.
"""

from __future__ import annotations

import shutil
import subprocess
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from argus import __version__ as _ARGUS_VERSION
from argus.cost.budget_governor import (
    BudgetConfig,
    account_spend,
    baseline_ratio,
    budget_config_from_budget,
)
from argus.dogfood.partition_plan import (
    FullRepoPlan,
    build_full_repo_plan,
    effective_exclusions,
)

# ── The DF-8-5-D re-export shim (Story 9.2 / AC8) ────────────────────────────
# The five frozen result dataclasses and the pure markdown renderer were MOVED, verbatim,
# to the two sibling modules below so this module carries one responsibility (the impure
# orchestration) instead of five. They are re-imported here and left in :data:`__all__`
# UNCHANGED, so every existing ``from argus.dogfood.proof_run import <name>`` keeps
# working with no change at any call site. The edge runs one way only —
# ``proof_run -> proof_render -> proof_types`` — so the pure modules never import the
# impure shell and no cycle exists. ``TC-ArgusAgent-DOGFOOD-001-37`` enumerates
# ``__all__`` and fails if any name stops resolving OR if a name is dropped from the
# surface, so shrinking ``__all__`` cannot silently satisfy the guard.
from argus.dogfood.proof_render import (  # noqa: F401 — re-export, see __all__
    DOGFOOD_EXTERNALIZATION_GUARD,
    render_proof_markdown,
)
from argus.dogfood.proof_types import (  # noqa: F401 — re-export, see __all__
    AdjudicationRow,
    CostSummary,
    CriticalClauseDisclosure,
    DogfoodProofRun,
    ScopeDisclosure,
)
from argus.evidence.bundle import (
    EvidenceBundle,
    build_evidence_bundle,
    bundle_to_canonical_bytes,
    persist_evidence_bundle,
)
from argus.intake.repo_loader import _SOURCE_SUFFIXES
from argus.ledger.critical_subsystems import CriticalSubsystemSet
from argus.models import AuditRequest
from argus.pipeline import AuditResult, run_audit_detailed
from argus.pipeline_persist import CRITICAL_SUBSYSTEMS_PRODUCER
from argus.precision.replay_harness import (
    MatchKey,
    finding_match_key,
    measure_validation_corpus,
    precision_gate_status_for,
)
from argus.store.integrity import IntegrityReport, lint_referential_integrity
from argus.store.reader import ApaaStoreReader
from argus.store.writer import ApaaStoreWriter

__all__ = [
    "DOGFOOD_PROOF_SCHEMA_VERSION",
    "DOGFOOD_BUDGET_CEILING",
    "DOGFOOD_GRADE",
    "DOGFOOD_ArgusAgent_VERSION",
    "DogfoodProofError",
    "AdjudicationRow",
    "CostSummary",
    "ScopeDisclosure",
    "CriticalClauseDisclosure",
    "DogfoodProofRun",
    "enumerate_tracked_sources",
    "materialize_snapshot",
    "run_dogfood",
    "adjudication_rows",
    "cost_summary",
    "derive_gate_status",
    "build_dogfood_proof",
    "render_proof_markdown",
]

#: The human-adjudication protocol this generator points at, declared once so the path the
#: artifact publishes and the path the guard checks cannot drift apart (AI-E9-7).
PRECISION_PROTOCOL_PATH = (
    "_bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md"
)

DOGFOOD_PROOF_SCHEMA_VERSION = "1"

# The 7.1 empirically-sized ceiling ``$X`` (``minions-dogfood-budget-plan.md``). The
# dogfood runs under ``budget = DOGFOOD_BUDGET_CEILING``. An int-credit value (AR4).
DOGFOOD_BUDGET_CEILING = 843

# The honest red-team grade flag (DN-GRADE / AC-DEMO-GRADE). The dogfood cuts LLM
# AST-grounding (Tier-A only), so it is a demo-heuristic-only result — NEVER presented
# as externalization / assurance evidence.
DOGFOOD_GRADE = "demo-heuristic-only"

# The ArgusAgent package version the bundle records — SOURCED from the single
# ArgusAgent-owned constant, NEVER a literal (9.2 / DF-8-5-A): it reaches the SIGNED,
# content-hashed PAYLOAD while the envelope wrapping it defaults to ``argus.__version__``.
DOGFOOD_ArgusAgent_VERSION = _ARGUS_VERSION

_GIT_TIMEOUT_SECONDS = 120

# The DEFAULT enumeration scope of the dogfood run. Named constants (not inline
# literals) so the SUBJECT the rendered artifact names is the SAME value the enumerator
# actually used — the artifact can never claim a tree the run did not read (Story 8.5 /
# AC2). Both impure call sites (:func:`run_dogfood`, :func:`build_dogfood_proof`) take
# these defaults.
_DEFAULT_SCOPE_PREFIX = "argus"
_DEFAULT_EXCLUDE_PREFIXES = ("argus/tests/",)


class DogfoodProofError(ValueError):
    """A TYPED dogfood-proof-generation failure (AR10).

    A ``ValueError`` subclass localized to this module (mirroring ``DogfoodPlanError``
    / ``PipelineError`` / ``EvidenceBundleError``). Raised on a git-enumeration /
    snapshot-materialize failure or a malformed run configuration — never a bare
    ``CalledProcessError`` / ``OSError`` out of the impure shell. The message names the
    relative condition only — never an absolute host path / source byte (NFR-S1).
    """


# ──────────────────────────────────────────────────────────────────────────────
# IMPURE shell — enumerate + materialize a clean snapshot of the real scoped tree
# ──────────────────────────────────────────────────────────────────────────────


def _run_git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    """Run ``git -C <repo> <args>`` (typed failure; AR10)."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            timeout=_GIT_TIMEOUT_SECONDS,
        )
    except FileNotFoundError as exc:
        raise DogfoodProofError("git executable not found on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise DogfoodProofError(f"git {' '.join(args)} timed out") from exc
    if check and proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="replace").strip()
        raise DogfoodProofError(
            f"git {' '.join(args)} failed (exit {proc.returncode}): {stderr or 'no stderr'}"
        )
    return proc


def enumerate_tracked_sources(
    repo_root: str | Path,
    *,
    scope_prefix: str = _DEFAULT_SCOPE_PREFIX,
    exclude_prefixes: tuple[str, ...] = _DEFAULT_EXCLUDE_PREFIXES,
) -> tuple[str, ...]:
    """Enumerate the git-TRACKED source files under the scope (the SAME 7.1 scope logic).

    REUSES the 1.4 ``_SOURCE_SUFFIXES`` filter over ``git ls-files -z`` (committed
    content, NUL-separated + unquoted so a non-ASCII path round-trips), scoped to
    *scope_prefix* and excluding *exclude_prefixes* (the untracked/self-audited ArgusAgent
    sub-tree). Deterministic: SORTED. A git failure raises :class:`DogfoodProofError`.
    """
    root = Path(repo_root)
    proc = _run_git(root, "ls-files", "-z", scope_prefix)
    records = proc.stdout.decode("utf-8", errors="replace").split("\0")
    return tuple(
        sorted(
            rec
            for rec in records
            if rec
            and Path(rec).suffix in _SOURCE_SUFFIXES
            and not any(rec.startswith(p) for p in exclude_prefixes)
        )
    )


def materialize_snapshot(
    repo_root: str | Path, source_files: tuple[str, ...], dest: Path
) -> tuple[Path, str]:
    """Copy *source_files* into *dest* as a fresh committed git snapshot (the impure shell).

    Mirrors the 6.5 ``stage_cartridge`` LOCKED pattern: copy the REAL tracked source
    bytes into a fresh temp tree, ``git init`` + commit ONCE with a deterministic
    identity, and return ``(snapshot_repo, commit_sha)``. The snapshot is a CLEAN on-pin
    tree the frozen ``load_repo_at_commit`` accepts (so ``run_audit_detailed`` runs
    unmodified). The audited bytes are the real tracked source at the current tracked
    commit. A copy / git failure raises :class:`DogfoodProofError` (AR10).
    """
    root = Path(repo_root)
    dest.mkdir(parents=True, exist_ok=True)
    for rel in source_files:
        src = root / rel
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copyfile(src, target)
        except OSError as exc:
            raise DogfoodProofError(
                f"could not copy source file {rel!r} into the snapshot ({type(exc).__name__})"
            ) from exc
    _run_git(dest, "init")
    _run_git(dest, "config", "core.autocrlf", "false")
    _run_git(dest, "config", "user.email", "dogfood@argus.test")
    _run_git(dest, "config", "user.name", "ArgusAgent Dogfood")
    _run_git(dest, "add", "-A")
    _run_git(dest, "commit", "-m", "minions dogfood snapshot")

    sha = _run_git(dest, "rev-parse", "HEAD").stdout.decode("utf-8", errors="replace").strip()
    return dest, sha or "unresolved-HEAD"


# ──────────────────────────────────────────────────────────────────────────────
# PURE derivation — adjudication rows + the within-ceiling cost accounting (AR8)
# ──────────────────────────────────────────────────────────────────────────────

# The per-class representative-locator cap (the human inspects a sample, not thousands).
_SAMPLE_LOCATOR_CAP = 5


def adjudication_rows(result: AuditResult) -> tuple[AdjudicationRow, ...]:
    """Lay the REAL dogfood findings out ADJUDICATION-READY (PURE; AC-ADJUDICATION-READY).

    Aggregates the emitted findings BY the 6.6 ``finding_match_key`` identity
    ``(rule_id, verdict_eligible, advisory)`` — the SAME shape the 6.6 precision harness
    + the 6.5 self-audit agree on (DN-MATCH-KEY-REUSE — no divergent key). Each row is
    one finding CLASS with its ``rule_id``, verdict-eligibility (``depth_supported is not
    None`` = blocking / verdict-eligible; ``None`` = advisory), the emitted ``count``, and
    up to :data:`_SAMPLE_LOCATOR_CAP` representative repo-relative POSIX locators (sorted,
    deterministic) so a human Eng-Lead + QA-Lead can inspect the class on the real repo
    and tag it TP/FP per ``precision-validation-protocol.md`` §4/§5. Two DISTINCT classes
    NEVER collapse to one row (the AI-E6-1 no-collision keystone — the row identity IS the
    match key). PURE — reads only rule-id provenance + booleans + locators (NFR-S1); no
    I/O / clock / float. Rows are sorted by ``(rule_id, verdict_eligible, advisory)`` for
    byte-stability. The ``adjudication`` field stays EMPTY (7.2 does NOT run the human
    judgment — OI1).
    """
    findings = result.verdict.ordered_findings
    by_key: dict[MatchKey, list[str]] = {}
    counts: Counter[MatchKey] = Counter()
    for finding in findings:
        key = finding_match_key(finding)
        counts[key] += 1
        bucket = by_key.setdefault(key, [])
        # Collect sorted representative locators up to the cap (deterministic sample).
        for loc in finding.locators:
            bucket.append(f"{loc.file_path}:{loc.start_line}")
    rows: list[AdjudicationRow] = []
    for key in sorted(by_key):
        rule_id, verdict_eligible, advisory = key
        samples = tuple(sorted(set(by_key[key]))[:_SAMPLE_LOCATOR_CAP])
        rows.append(
            AdjudicationRow(
                rule_id=rule_id,
                verdict_eligible=verdict_eligible,
                advisory=advisory,
                count=counts[key],
                sample_locators=samples,
            )
        )
    return tuple(rows)


def cost_summary(
    source_files: tuple[str, ...],
    total_loc: int,
    *,
    live_sized_ceiling: int | None = None,
) -> CostSummary:
    """Compute the within-ceiling + 3.2-halt cost accounting (PURE; AC-EXECUTE / AR4).

    Folds the V1 deterministic zero-token contributions (``files_indexed`` +
    ``python_files`` + ``detector_passes`` — the SAME recipe ``pipeline._build_cost_ledger``
    uses, REUSED via the 3.1 ``account_spend``, no fork) into the whole-repo ``int``-credit
    total, then DEMONSTRATES the 3.2 semantics via the SAME accountant: the run FITS under
    ``$X`` = 843 (``ceiling_reached is False``) while a ceiling one credit below the total
    demonstrably BREACHES (the >=-is-a-breach REUSE — the halt->skip->downgrade->report
    path). All ``int`` credits / a ``Fraction`` baseline ratio (NFR-C1) — never float.

    *live_sized_ceiling* is the 7.1 ``build_full_repo_plan`` sizing measured on the LIVE
    tree by the SAME derivation the budget artifact publishes. When supplied, the fit is
    re-folded through the SAME 3.1 accountant under that ceiling too, so the proof can
    state the CEILING HONESTY PAIR (Story 8.5 / AC1 / D7): the frozen historical ``$X``
    the run was executed under AND the live sizing, with a fit verdict for each. No
    second accountant, no re-derived comparison (AR7).
    """
    python_files = sum(1 for f in source_files if f.endswith((".py", ".pyi", ".pyx")))
    contributions = {
        "files_indexed": len(source_files),
        "python_files": python_files,
        "detector_passes": python_files * 3,
    }
    fitted = account_spend(
        contributions,
        config=budget_config_from_budget(DOGFOOD_BUDGET_CEILING),
        build_cost_proxy=total_loc,
    )
    total_credits = fitted.total_credits
    breach = account_spend(
        {"total": total_credits},
        config=BudgetConfig(ceiling_credits=max(total_credits - 1, 0)),
        build_cost_proxy=total_loc,
    )
    fits_live = False
    if live_sized_ceiling is not None:
        fits_live = not account_spend(
            {"total": total_credits},
            config=BudgetConfig(ceiling_credits=live_sized_ceiling),
            build_cost_proxy=total_loc,
        ).ceiling_reached
    return CostSummary(
        total_credits=total_credits,
        ceiling=DOGFOOD_BUDGET_CEILING,
        build_cost_proxy=total_loc,
        baseline_ratio=baseline_ratio(total_credits, total_loc),
        fits_within_ceiling=not fitted.ceiling_reached,
        breaches_below_total=breach.ceiling_reached,
        live_sized_ceiling=live_sized_ceiling,
        fits_within_live_sized_ceiling=fits_live,
    )


# ──────────────────────────────────────────────────────────────────────────────
# IMPURE orchestration — snapshot → audit → integrity lint → SIGNED bundle → proof
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class _DogfoodExecution:
    """The impure run's raw outputs (the seam :func:`run_dogfood` returns)."""

    result: AuditResult
    integrity: IntegrityReport
    bundle: EvidenceBundle
    bundle_locator: str
    bundle_bytes: bytes
    # The run's own persisted critical-subsystem set, or None when no such envelope was
    # written. Defaulted so no existing construction site breaks (NFR-M2).
    critical_subsystems: CriticalSubsystemSet | None = None
    # The MEASURED reason the set is None (empty when it was retrieved).
    critical_subsystems_note: str = ""


def _read_critical_subsystem_set(
    reader: ApaaStoreReader,
) -> tuple[CriticalSubsystemSet | None, str]:
    """Read the run's persisted :class:`CriticalSubsystemSet` back out (IMPURE; AR8/AR7).

    REUSES the ``ApaaStoreReader`` :func:`run_dogfood` already builds for the 4.2 lint
    and the ``CRITICAL_SUBSYSTEMS_PRODUCER`` token ``pipeline_persist`` publishes — no
    second store reader, no re-derived critical set (AR7), so the proof discloses the
    SAME set the gate keyed on. Enumeration is ``sorted`` (AR4).

    Returns ``(set, "")`` on success and ``(None, measured_reason)`` otherwise. This is an
    OPTIONAL disclosure on an artifact whose §3 REPORTS store integrity, so an unreadable
    UNRELATED envelope DEGRADES to "not retrieved, because …" rather than aborting: a
    store the 4.2 lint would report as ``integrity_consistent: False`` must still be able
    to produce the artifact that reports it (8.5 review, iteration 1). Only an envelope
    that ACTUALLY claims the producer fails hard (AR10): a malformed payload under it, or
    MORE THAN ONE such envelope — filenames are content-addressed, so ``sorted`` is
    lexicographic, not recency, and disclosing whichever hash sorts first would name a set
    the gate may never have keyed on. Message locators are ``.argus/``-relative (NFR-S1).
    """
    state_dir = reader.paths.argus_root / "state"
    if not state_dir.is_dir():
        return None, "the snapshot store holds no `state/` directory"
    matches: list[tuple[str, object]] = []
    unreadable: list[str] = []
    for child in sorted(state_dir.glob("*.json")):
        locator = f"state/{child.name}"
        try:
            envelope = reader.read_envelope(locator)
        except Exception as exc:  # noqa: BLE001 — degraded, never fatal (see docstring)
            unreadable.append(f"`{locator}` ({type(exc).__name__})")
            continue
        if envelope.producer == CRITICAL_SUBSYSTEMS_PRODUCER:
            matches.append((locator, envelope.payload))
    if len(matches) > 1:
        raise DogfoodProofError(
            f"{len(matches)} persisted envelopes claim producer "
            f"{CRITICAL_SUBSYSTEMS_PRODUCER!r} ({', '.join(m for m, _ in matches)}) — the "
            "set the gate keyed on is ambiguous and is NOT guessed by filename order"
        )
    if not matches:
        seen = f" ({len(unreadable)} unreadable: {', '.join(unreadable)})" if unreadable else ""
        return None, (
            "no persisted envelope in `state/` claimed producer "
            f"`{CRITICAL_SUBSYSTEMS_PRODUCER}`{seen}"
        )
    try:
        return CriticalSubsystemSet.model_validate(matches[0][1]), ""
    except Exception as exc:  # noqa: BLE001 — typed failure, never a bare raise
        raise DogfoodProofError(
            f"the envelope at {matches[0][0]!r} claims producer "
            f"{CRITICAL_SUBSYSTEMS_PRODUCER!r} but its payload is not a "
            f"CriticalSubsystemSet ({type(exc).__name__})"
        ) from exc


def run_dogfood(
    repo_root: str | Path,
    snapshot_dir: Path,
    *,
    argus_version: str = DOGFOOD_ArgusAgent_VERSION,
    commit_label: str = "minions-dogfood",
) -> _DogfoodExecution:
    """Materialize a snapshot, RUN the frozen audit, and export + persist the SIGNED bundle.

    The impure orchestration (AR8): enumerate the tracked scoped sources → materialize a
    clean on-pin snapshot → ``run_audit_detailed`` under ``budget = $X`` = 843 (REUSED —
    no fork) → ``lint_referential_integrity`` over the persisted ``.argus/`` tree →
    ``build_evidence_bundle`` + ``persist_evidence_bundle`` (the 4.3 seam + the 1.1
    prev-hash-chained envelope) → the canonical bundle bytes. Returns a
    :class:`_DogfoodExecution`. A pipeline / bundle / lint failure surfaces as the typed
    ``PipelineError`` / ``EvidenceBundleError`` / ``StoreIntegrityError`` (AR10 — never a
    bare traceback); a git/copy failure raises :class:`DogfoodProofError`.
    """
    root = Path(repo_root)
    source_files = enumerate_tracked_sources(root)
    if not source_files:
        # RS-4b (Story 9.2): this is an OPERATOR-VISIBLE message, not a comment. It used
        # to name the host product's package directory — a tree this enumeration has not
        # read since the repo separation — so an operator debugging an empty snapshot was
        # sent to look for a directory that does not exist here. It now names the scope
        # the enumerator ACTUALLY used, read from the same constants the call above passes.
        raise DogfoodProofError(
            f"no tracked source files enumerated under scope {_DEFAULT_SCOPE_PREFIX!r} "
            f"(excluding {_DEFAULT_EXCLUDE_PREFIXES!r}) for the dogfood snapshot"
        )
    snapshot_repo, _sha = materialize_snapshot(root, source_files, snapshot_dir)

    request = AuditRequest(
        repo_path=str(snapshot_repo),
        commit="HEAD",
        budget=DOGFOOD_BUDGET_CEILING,
        materiality_bar="default",
    )
    result = run_audit_detailed(request)

    # ONE reader over the snapshot store, REUSED for both the 4.2 lint and the
    # critical-subsystem read-back (AR7 — no second store reader).
    reader = ApaaStoreReader(snapshot_repo)
    integrity = lint_referential_integrity(reader)
    critical_subsystems, critical_note = _read_critical_subsystem_set(reader)
    bundle = build_evidence_bundle(
        result, integrity, commit=commit_label, argus_version=argus_version
    )
    bundle_locator = persist_evidence_bundle(ApaaStoreWriter(snapshot_repo), bundle)
    bundle_bytes = bundle_to_canonical_bytes(bundle)
    return _DogfoodExecution(
        result=result,
        integrity=integrity,
        bundle=bundle,
        bundle_locator=bundle_locator,
        bundle_bytes=bundle_bytes,
        critical_subsystems=critical_subsystems,
        critical_subsystems_note=critical_note,
    )


def derive_gate_status() -> str:
    """The precision-gate status line this proof publishes — DERIVED, never hand-written.

    **Story 13.1 / AC5 — the fix for ``DF-8-5-C``.** This call site previously read::

        gate_status = precision_gate_status_for(
            precision=Fraction(0, 1),
            n=0,
            provisional=True,
            ...
        )

    Both arguments were **literals**. Neither was a measurement of anything, and the resulting
    sentence — *"precision=0/1 over FINDINGS not repos; N=0 labeled cartridges populated, floor
    N=5"* — was rendered verbatim into ``minions-dogfood-proof.md``, a proof artifact **about
    the very gate those numbers describe**. A hand-written number in a proof artifact is the
    defect class Epic 8 exists to delete, and it survived five epics inside the generator that
    exists to prevent it.

    **The correction, and its direction.** ``n=0`` UNDERSTATED the cartridge corpus, which
    holds 7 populated rows across 5 distinct rule classes — so it never made a gate look
    cleared, and nothing published was an over-claim. That is why this is filed 🟢 and closed
    as a correctness fix rather than as a false-assurance incident.

    **What it is NOT corrected to, and why (Story 13.1 / DN-7).** The obvious fix — pass
    ``n=populated_planted_defect_count()`` = 7 — would publish *"N=7 … floor N=5"*, which reads
    as **floor met** for a gate the cartridges do not gate at all. Story 13.1 / DN-1 decided the
    **PRD governs**: the ≥80% externalization gate is measured over a corpus of *real
    repositories*, while the cartridges measure **recall** (FR20). So ``n`` is the ELIGIBLE
    member count of the REPOSITORY corpus — measured, and currently **0** — and the cartridge
    substrate is reported alongside it with its role named. The published number is the same
    ``0`` it always was; the difference is that it is now a measurement of a named population
    instead of a literal, and it says which population it counts.

    ``precision`` is ``None`` — *not computed by this run* — because that is the truth: this
    generator audits a repository and never invokes the replay harness. Saying "zero" was a
    stronger and false claim. The harness refuses to render a ``None`` precision as anything
    but provisional, so this call cannot become a cleared gate by editing one keyword.

    Pure apart from the two declared lazy substrate edges (``DF-9-2-A``); reads no clock, makes
    no LLM call, and never passes a true ``protocol_cleared`` — the flag is not passed at all.

    (That sentence is deliberately worded around the literal ``TC-ArgusAgent-DOGFOOD-001-30``
    greps this package for. The guard is a substring scan by design, so prose that quotes the
    forbidden assignment would trip it; the right response to that is to reword the prose, not
    to teach the guard about docstrings.)
    """
    measurement = measure_validation_corpus()
    return precision_gate_status_for(
        precision=None,
        n=measurement.validation_set_n,
        provisional=True,
        protocol_path=PRECISION_PROTOCOL_PATH,
        floor_n=measurement.floor_n,
        corpus_note=measurement.corpus_note(),
        population_label="independent repositories in the validation set",
    )


def build_dogfood_proof(
    repo_root: str | Path,
    snapshot_dir: Path,
    *,
    argus_version: str = DOGFOOD_ArgusAgent_VERSION,
) -> DogfoodProofRun:
    """Run the dogfood + assemble the PURE :class:`DogfoodProofRun` (the full orchestration).

    Composes: the 7.1 ``build_full_repo_plan`` (the 4-unit map + the ``$X`` sizing —
    CONSUMED for provenance, over the LIVE tracked tree so the plan the proof cites is the
    committed 7.1 plan), the impure :func:`run_dogfood` (audit + SIGNED bundle), the pure
    :func:`cost_summary` (within-ceiling + 3.2 halt), the pure :func:`adjudication_rows`
    (the adjudication-ready finding classes), and the PROVISIONAL gate status (via the 6.6
    ``precision_gate_status_for`` — ``provisional=True``, NEVER flipped). Carries the
    honest ``grade: demo-heuristic-only`` flag. Deterministic for the same tracked content
    (NFR-D1/P1). Raises the typed :class:`DogfoodProofError` / ``PipelineError`` /
    ``EvidenceBundleError`` (AR10).
    """
    root = Path(repo_root)
    plan: FullRepoPlan = build_full_repo_plan(str(root))
    execution = run_dogfood(root, snapshot_dir, argus_version=argus_version)

    result = execution.result
    verdict = result.verdict
    source_files = enumerate_tracked_sources(root)
    cost = cost_summary(
        source_files, plan.total_loc, live_sized_ceiling=plan.budget.sized_ceiling
    )
    rows = adjudication_rows(result)

    # DR-3 row + input disclosure (Story 8.5 / AC1): read STRAIGHT off the verdict the
    # gate produced. Nothing here re-derives a row from the verdict token and nothing
    # here is hand-written — a hardcoded historical figure in a generator is the exact
    # fork/staleness shape AR7 exists to prevent.
    scope_disclosure: ScopeDisclosure | None = None
    if verdict.coverage_scope is not None:
        cs = verdict.coverage_scope
        scope_disclosure = ScopeDisclosure(
            scope_id=cs.scope_id,
            excluded_reason=cs.excluded_reason,
            assessed_deep_count=cs.assessed_deep_count,
            assessed_total_count=cs.assessed_total_count,
            assessed_deep_ratio=cs.assessed_deep_ratio,
            excluded_count=cs.excluded_count,
        )
    critical_set = execution.critical_subsystems
    critical_disclosure = CriticalClauseDisclosure(
        all_deep=verdict.critical_subsystems_all_deep,
        not_deep=tuple(verdict.critical_subsystems_not_deep),
        set_retrieved=critical_set is not None,
        set_size=0 if critical_set is None else len(critical_set.paths),
        excluded_ineligible_count=(
            0 if critical_set is None else len(critical_set.heuristic_excluded_ineligible)
        ),
        designated_but_unmatched=(
            () if critical_set is None else tuple(critical_set.designated_but_unmatched)
        ),
        retrieval_note=execution.critical_subsystems_note,
    )

    # OI1: the gate STAYS PROVISIONAL. The precision NUMBER is NOT computed / presented as
    # authoritative here — the proof reports the gate status string with provisional=True
    # (protocol_cleared is NEVER passed True). The status string carries the harness's
    # provisional framing + the pointer to the human-adjudication protocol.
    gate_status = derive_gate_status()

    return DogfoodProofRun(
        commit_descriptor=plan.commit_descriptor,
        source_file_count=len(source_files),
        total_loc=plan.total_loc,
        unit_count=len(plan.partition_plan.partitions),
        verdict=verdict.verdict.value,
        exit_code=verdict.exit_code,
        deep_ratio=verdict.deep_ratio,
        blocking_finding_count=verdict.blocking_finding_count,
        total_finding_count=len(verdict.ordered_findings),
        cost=cost,
        adjudication=rows,
        bundle_locator=execution.bundle_locator,
        bundle_content_hash=Path(execution.bundle_locator).stem,
        bundle_byte_length=len(execution.bundle_bytes),
        integrity_consistent=execution.integrity.consistent,
        grade=DOGFOOD_GRADE,
        gate_status=gate_status,
        decision_row="" if verdict.decision_row is None else verdict.decision_row.value,
        deep_count=verdict.deep_count,
        total_count=verdict.total_count,
        scope=scope_disclosure,
        critical=critical_disclosure,
        scope_prefix=_DEFAULT_SCOPE_PREFIX,
        exclude_prefixes=_DEFAULT_EXCLUDE_PREFIXES,
        effective_exclude_prefixes=effective_exclusions(
            enumerate_tracked_sources(root, exclude_prefixes=()), _DEFAULT_EXCLUDE_PREFIXES
        ),
    )


