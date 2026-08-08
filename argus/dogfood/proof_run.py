"""Reproducible Minions dogfood PROOF-RUN generator (Story 7.2 — the CAPSTONE).

Verification area ArgusAgent-DOGFOOD (``TC-ArgusAgent-DOGFOOD-001-NN`` — CONTINUING from the 7.1
index; 7.1 locked ``...-01..17``, so 7.2 starts at ``...-18``). Drivers: ArgusAgent-FR-30
(headless invocation contract — the dogfood RUNS the frozen ``run_audit_detailed``
over the real Minions repo), ArgusAgent-FR-21 / OI3 (the empirically-sized ``$X`` = 843
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
Minions source byte / secret value in the proof artifact / bundle / any persisted
``.argus/`` artifact — the no-source-retention moat over the REAL repo), ArgusAgent-AR4 (int
credits / ``Fraction`` ratios — NEVER float in any persisted figure), ArgusAgent-AR7 (REUSE
by import — no fork of the pipeline / bundle / serializer / lint / precision harness /
7.1 plan), ArgusAgent-AR8 (pure/impure separation — the derivation + render are pure over the
run result; the snapshot-materialize + audit + persist are the impure shell), ArgusAgent-AR10
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
adjudication-ready finding aggregation (``adjudication_rows``), the within-ceiling +
3.2-halt cost accounting (``cost_summary`` — REUSING the 3.1 ``account_spend``), and
the ``.md`` proof-artifact renderer (``render_proof_markdown``). It adds NO forked
pipeline, NO second bundle model / serializer / hasher, NO LLM dispatch, NO new
``cli.py`` flag / HTTP route / CI job.

Why a materialized snapshot repo (the LOCKED dogfood-run mechanism, DN-DOGFOOD-REUSE)
------------------------------------------------------------------------------------
``run_audit_detailed`` calls ``load_repo_at_commit`` which REFUSES a drifted working
tree (HEAD must BE the pin AND ``git status --porcelain`` must be empty — Story 1.4).
The LIVE Minions tree cannot satisfy this: the ArgusAgent sub-tree is git-UNTRACKED and the
working tree is dirty. Rather than fork/relax the frozen loader (out of scope), this
generator MIRRORS the 6.5 ``_cartridge.stage_cartridge`` pattern the whole precision
substrate already uses: it enumerates the git-TRACKED ``minions_core/`` source files
(EXCLUDING ``minions_core/argus/`` — the SAME 7.1 ``enumerate_minions_source_files``
scope so the dogfood audits the SAME Minions PLATFORM tree the 7.1 plan sized),
COPIES them into a fresh temp directory, ``git init``s + commits ONCE, and audits that
clean on-pin snapshot. The audited BYTES are the REAL Minions source at the current
tracked commit (recorded as ``commit_descriptor`` provenance) — this is a real dogfood
over real Minions code, NOT a cartridge. The snapshot commit SHA varies per run
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

Pure/impure separation (AR8)
----------------------------
PURE: :func:`adjudication_rows` (over the run result's findings), :func:`cost_summary`
(over the enumerated file counts, REUSING ``account_spend``), :func:`render_proof_markdown`
(over the pure :class:`DogfoodProofRun`). IMPURE shell: :func:`enumerate_tracked_sources`
+ :func:`materialize_snapshot` (``git`` + file copy), :func:`run_dogfood` (the audit +
integrity lint + bundle export + persist), :func:`build_dogfood_proof` (the full
orchestration).
"""

from __future__ import annotations

import shutil
import subprocess
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

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
    "build_dogfood_proof",
    "render_proof_markdown",
]

DOGFOOD_PROOF_SCHEMA_VERSION = "1"

# The 7.1 empirically-sized ceiling ``$X`` (``minions-dogfood-budget-plan.md``). The
# dogfood runs under ``budget = DOGFOOD_BUDGET_CEILING``. An int-credit value (AR4).
DOGFOOD_BUDGET_CEILING = 843

# The honest red-team grade flag (DN-GRADE / AC-DEMO-GRADE). The dogfood cuts LLM
# AST-grounding (Tier-A only), so it is a demo-heuristic-only result — NEVER presented
# as externalization / assurance evidence.
DOGFOOD_GRADE = "demo-heuristic-only"

# The ArgusAgent package version the bundle records (mirrors ``pyproject.toml`` ``version``).
DOGFOOD_ArgusAgent_VERSION = "1.43.0"

# The externalization-guard sentence the proof artifact + wrapper carry (AC-DEMO-GRADE).
# A committed test asserts this language is present + that no "externalization-grade /
# validated deep audit" over-claim phrase is injected.
DOGFOOD_EXTERNALIZATION_GUARD = (
    "This dogfood run is a demo-heuristic-only (Tier-A) result: the frozen pipeline "
    "run_audit_detailed calls NO LLM (zero-token) and the AST-grounding deep-audit "
    "seam is NOT wired in, so every finding is advisory / verdict-ineligible "
    "(depth_supported is None). It is NOT presented as externalization or assurance "
    "evidence, and it does NOT clear the >=80%-precision gate — that requires the human "
    "TP/FP adjudication over these REAL findings (a documented human step, still open)."
)

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


@dataclass(frozen=True)
class AdjudicationRow:
    """One adjudication-ready finding CLASS — the 6.6 match-key shape (NFR-S1).

    The REAL dogfood emits thousands of findings; a human TP/FP adjudication tags each
    finding CLASS (the 6.6 ``finding_match_key`` identity ``(rule_id, verdict_eligible,
    advisory)``), not each of thousands of locator instances. This row is one such class:
    the ``rule_id`` provenance, whether the class is verdict-eligible (blocking) vs
    advisory, the emitted ``count``, and up to :data:`_SAMPLE_LOCATOR_CAP` representative
    repo-relative POSIX ``sample_locators`` so a human can inspect the class on the real
    repo. Carries NO source byte / secret value — only the rule-id token, two booleans,
    an int count, and repo-relative locators (NFR-S1). ``adjudication`` is the empty
    string placeholder the human fills with ``TP`` / ``FP`` (7.2 leaves it UN-tagged —
    the adjudication is the human step, OUT of scope here).
    """

    rule_id: str
    verdict_eligible: bool
    advisory: bool
    count: int
    sample_locators: tuple[str, ...]
    adjudication: str = ""

    @property
    def match_key(self) -> MatchKey:
        """The 6.6 ``finding_match_key`` identity ``(rule_id, verdict_eligible, advisory)``."""
        return (self.rule_id, self.verdict_eligible, self.advisory)


@dataclass(frozen=True)
class CostSummary:
    """The within-ceiling + 3.2-halt cost accounting for the dogfood run (AR4).

    REUSES the 3.1 ``account_spend`` over the V1 deterministic contribution recipe (the
    SAME recipe ``pipeline._build_cost_ledger`` folds — no fork). ``total_credits`` is the
    whole-repo V1 zero-token total; ``ceiling`` is ``$X`` = 843; ``fits_within_ceiling``
    asserts the run does NOT breach ``$X`` (``ceiling_reached is False``);
    ``breaches_below_total`` DEMONSTRATES the 3.2 halt (a ceiling one credit below the
    total breaches). All ``int`` credits / a ``Fraction`` baseline ratio — never float.
    """

    total_credits: int
    ceiling: int
    build_cost_proxy: int
    baseline_ratio: Fraction | str
    fits_within_ceiling: bool
    breaches_below_total: bool
    # The CEILING HONESTY PAIR (Story 8.5 / AC1 / D7). ``ceiling`` above is the FROZEN
    # historical execution parameter the run was actually executed under; the 7.1
    # generator re-sizes ``$X`` from the LIVE tree on every derivation and has drifted
    # away from it. Recording only one of the two lets the proof artifact and the budget
    # artifact — both published by the same change — disagree about what "the 7.1
    # empirical ceiling" is. Both are recorded, with a fit verdict for EACH. Defaults so
    # every existing construction site keeps working (NFR-M2 additive-only).
    # ``None`` means NO live sizing was supplied — never ``0``, which is a legitimate
    # sizing for an empty tree; collapsing the two would publish "not supplied" about a
    # derivation that WAS supplied a zero ceiling (the same ambiguity
    # :class:`CriticalClauseDisclosure.set_retrieved` exists to refuse).
    live_sized_ceiling: int | None = None
    fits_within_live_sized_ceiling: bool = False


@dataclass(frozen=True)
class ScopeDisclosure:
    """The verdict's DISCLOSED assessment-scope narrowing, flattened for render (PURE).

    A value copy of the frozen ``verdict.CoverageScope`` fields the proof artifact must
    print (Story 8.5 / AC1 — the ASSESSED population the row was computed from, not only
    the whole-ledger numbers), kept a plain dataclass so :class:`DogfoodProofRun` stays a
    pure value holder. ``assessed_deep_ratio`` is an exact ``Fraction`` (AR4). ``None``
    on the run means ``coverage_scope is None``, i.e. **no narrowing occurred** — which
    the renderer states EXPLICITLY rather than by omission.
    """

    scope_id: str
    excluded_reason: str
    assessed_deep_count: int
    assessed_total_count: int
    assessed_deep_ratio: Fraction
    excluded_count: int


@dataclass(frozen=True)
class CriticalClauseDisclosure:
    """The FR4/FR16 critical-subsystem clause state the gate keyed on (PURE; boundary B3).

    Epic 8 LOOSENS the critical gate twice (the DR-5 eligibility filter, the
    ``application`` scope default) and nothing guards the PRD-fatal
    false-``RELEASE_READY`` direction (inversion F1). A green verdict whose clause held
    because the critical set was **EMPTY** is a vacuously satisfied gate, and that must
    be VISIBLE, never implied.

    ``all_deep`` / ``not_deep`` come from the verdict and are always present.
    ``set_retrieved`` records whether the run's persisted :class:`CriticalSubsystemSet`
    was actually read back; when ``False`` the remaining counters are meaningless and the
    renderer says so — reporting ``set_size = 0`` for "not retrieved" would fabricate the
    very vacuous-gate claim this disclosure exists to make falsifiable.
    ``retrieval_note`` carries the MEASURED reason it could not be read, so an unread set
    is not merely unread but explained.
    """

    all_deep: bool
    not_deep: tuple[str, ...] = ()
    set_retrieved: bool = False
    set_size: int = 0
    excluded_ineligible_count: int = 0
    designated_but_unmatched: tuple[str, ...] = ()
    retrieval_note: str = ""

    @property
    def vacuously_satisfied(self) -> bool:
        """Whether the clause was satisfied by an EMPTY critical set (a vacuous gate)."""
        return self.set_retrieved and self.all_deep and self.set_size == 0


@dataclass(frozen=True)
class DogfoodProofRun:
    """The whole 7.2 dogfood-proof result (PURE value holder — the render input).

    Aggregates: the audited ``commit_descriptor`` provenance, the 7.1 partition/budget
    plan (CONSUMED), the run verdict token + exit code + deep-ratio + blocking count, the
    cost summary (within-ceiling + halt), the adjudication-ready finding rows, the SIGNED
    bundle's locator + content hash, the integrity-report consistency, the honest
    ``grade`` flag, and the PROVISIONAL gate status string. PURE / value-free — only
    provenance / counts / rule-ids / locators / a ``Fraction`` cross a byte boundary
    (NFR-S1). ``protocol_cleared`` is NOT a field here and is NEVER flipped (OI1).
    """

    commit_descriptor: str
    source_file_count: int
    total_loc: int
    unit_count: int
    verdict: str
    exit_code: int
    deep_ratio: Fraction
    blocking_finding_count: int
    total_finding_count: int
    cost: CostSummary
    adjudication: tuple[AdjudicationRow, ...]
    bundle_locator: str
    bundle_content_hash: str
    bundle_byte_length: int
    integrity_consistent: bool
    grade: str
    gate_status: str
    # ── DR-3 row + input disclosure (Story 8.5 / AC1) — all defaulted (NFR-M2) ──
    # The LITERAL DecisionRow value the gate disclosed, never a re-derivation from the
    # verdict token: rows 1 and 4 both render INSUFFICIENT_COVERAGE / exit 3, so a
    # consumer that infers the row from the token states a falsehood for one of them.
    # Empty string ONLY for a pre-amendment payload that never disclosed a row.
    decision_row: str = ""
    deep_count: int = 0
    total_count: int = 0
    scope: ScopeDisclosure | None = None
    critical: CriticalClauseDisclosure | None = None
    # The enumeration SUBJECT this run actually audited (Story 8.5 / AC2) — recorded
    # from the module-level enumeration defaults BOTH impure call sites pass, so the
    # artifact cannot name a tree the run did not read.
    scope_prefix: str = ""
    exclude_prefixes: tuple[str, ...] = ()
    # What the enumerator MEASURABLY held out: the subset of ``exclude_prefixes`` that
    # matched >=1 tracked file (:func:`effective_exclusions`). Rendering the CONFIGURED set
    # asserts a held-out sub-tree a stale/renamed prefix may never have matched.
    effective_exclude_prefixes: tuple[str, ...] = ()


# ──────────────────────────────────────────────────────────────────────────────
# IMPURE shell — enumerate + materialize a clean snapshot of the real Minions tree
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
    """Enumerate the git-TRACKED Minions source files (the SAME 7.1 scope; the impure read).

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

    Mirrors the 6.5 ``stage_cartridge`` LOCKED pattern: copy the REAL Minions source
    bytes into a fresh temp tree, ``git init`` + commit ONCE with a deterministic
    identity, and return ``(snapshot_repo, commit_sha)``. The snapshot is a CLEAN on-pin
    tree the frozen ``load_repo_at_commit`` accepts (so ``run_audit_detailed`` runs
    unmodified). The audited bytes are the real Minions source at the current tracked
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

    The impure orchestration (AR8): enumerate the tracked Minions sources → materialize a
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
        raise DogfoodProofError(
            "no tracked minions_core/ source files enumerated for the dogfood snapshot"
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
    gate_status = precision_gate_status_for(
        precision=Fraction(0, 1),
        n=0,
        provisional=True,
        protocol_path="_bmad-output/design-artifacts/ArgusAgent/precision-validation-protocol.md",
    )

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


# ──────────────────────────────────────────────────────────────────────────────
# PURE markdown renderer (AR8) — provenance + counts + locators only (NFR-S1)
# ──────────────────────────────────────────────────────────────────────────────


# The provenance banner this renderer stamps. ONE definition so the artifact can never
# name a generator module that does not exist (Story 8.5 / AC2 — pinned by a committed
# test that resolves every path the artifact cites).
_GENERATOR_MODULE = "argus/dogfood/proof_run.py"

# The preserved, non-regenerable independent run this artifact path used to hold (AC5).
_SUPERSEDED_ARTIFACT = "minions-dogfood-proof-story-7-2-superseded.md"

_SELF_AUDIT_HONESTY = (
    "**This is a SELF-audit — Argus auditing Argus (Story 8.5 / AC2).** The subject is "
    "this repository's own package, not an independent codebase. A self-audit is "
    "MATERIALLY WEAKER evidence than the independent-repository run it supersedes: the "
    "tool and the tree share authorship, so the run cannot demonstrate that the tool "
    "finds defects it was not written alongside. It is reportable as a reproducibility "
    "and no-source-retention demonstration; it is NEVER independent corroboration of "
    "the tool's detection ability. The independent Story-7.2 run over the Minions "
    f"platform repository is preserved verbatim at `{_SUPERSEDED_ARTIFACT}` and cannot "
    "be re-executed here, because that source is not in this repository. The filename "
    "`minions-dogfood-proof.md` is a retained HISTORICAL identifier (an evidence path "
    "that moves is an evidence path that gets lost); the subject is what this section "
    "names, not what the filename suggests."
)


def _audited_tree_clause(proof: DogfoodProofRun) -> str:
    """Name the tree the run ACTUALLY enumerated (PURE; Story 8.5 / AC2).

    Rendered from the scope the impure orchestration recorded onto the run — never a
    hardcoded subject — so the artifact cannot name a tree the audit did not read. An
    unrecorded scope degrades to an explicit marker rather than a guessed subject. Only
    the MEASURED exclusions are named: a configured prefix that held nothing out is not
    rendered as a held-out sub-tree (Story 8.5 review, iteration 1).
    """
    if not proof.scope_prefix:
        return "the audited tree (scope not recorded by this run)"
    excluded = ", ".join(f"`{p}`" for p in proof.effective_exclude_prefixes)
    tail = f", excluding {excluded}" if excluded else ""
    return f"the git-tracked `{proof.scope_prefix}` package tree{tail}"


def _row_token(proof: DogfoodProofRun) -> str:
    """Render the LITERAL disclosed ``DecisionRow`` value, never a re-derivation (PURE)."""
    if not proof.decision_row:
        return (
            "`not disclosed` (a pre-amendment verdict payload carried no row; the row is "
            "NOT inferred from the verdict token here, because rows 1 and 4 render the "
            "same token)"
        )
    return f"`{proof.decision_row}`"


def _render_assessed_population(proof: DogfoodProofRun) -> list[str]:
    """Render the population the gate keyed on (PURE; Story 8.5 / AC1).

    States the whole-ledger numbers AND, when a narrowing was disclosed, the assessed
    sub-population with its scope id, held-out count and reason. An absent narrowing is
    stated EXPLICITLY — it must never be readable as a silent one.
    """
    if proof.scope is None:
        return [
            "**No narrowing occurred.** The verdict carries no `coverage_scope`, so the "
            "gate keyed on the WHOLE coverage ledger: "
            f"**{proof.deep_count} `audited_deep` of {proof.total_count} entries** "
            f"(`{proof.deep_ratio.numerator}/{proof.deep_ratio.denominator}`, exact "
            "`Fraction`). No entry was held out of the assessment and no scope "
            "identifier was applied.",
        ]
    s = proof.scope
    return [
        "**A narrowing WAS applied and is disclosed on the verdict.** The gate keyed on "
        "the assessed sub-population below, not on the whole ledger:",
        "",
        f"- Scope identifier: `{s.scope_id}`",
        f"- Assessed deep / assessed total: **{s.assessed_deep_count} / "
        f"{s.assessed_total_count}** "
        f"(`{s.assessed_deep_ratio.numerator}/{s.assessed_deep_ratio.denominator}`, "
        "exact `Fraction`)",
        f"- Held out of the assessment: **{s.excluded_count}** entries, reason "
        f"`{s.excluded_reason}`",
        f"- Whole-ledger deep / total (for comparison): **{proof.deep_count} / "
        f"{proof.total_count}** "
        f"(`{proof.deep_ratio.numerator}/{proof.deep_ratio.denominator}`)",
        "",
        "The `INSUFFICIENT_COVERAGE` floor is re-applied WITHIN the narrowed population, "
        "so a narrowing changes WHAT is claimed and never lowers the bar for claiming it.",
    ]


def _render_critical_clause(proof: DogfoodProofRun) -> list[str]:
    """Render the critical-subsystem clause state (PURE; Story 8.5 / AC1, boundary B3).

    Distinguishes a clause satisfied over a NON-EMPTY, fully-deep critical set from one
    satisfied over an EMPTY set — the second is VACUOUS and is named as such.
    """
    c = proof.critical
    if c is None:
        return [
            "**Not captured by this run.** This artifact makes NO claim about the "
            "critical-subsystem clause state.",
        ]
    if not c.set_retrieved:
        why = f" MEASURED reason: {c.retrieval_note}." if c.retrieval_note else ""
        return [
            "**The run's persisted critical-subsystem set could NOT be read back** from "
            "the snapshot's `.argus/state/` tree, so its SIZE is unknown here. This "
            "artifact therefore does NOT state whether the clause was satisfied over a "
            "real set or vacuously over an empty one — an unread set is reported as "
            f"unread, never as empty.{why}",
            "",
            f"- Clause satisfied (`critical_subsystems_all_deep`): **{c.all_deep}**",
            f"- Critical paths NOT `audited_deep`: **{len(c.not_deep)}**",
        ]
    if not c.all_deep:
        headline = (
            "**NOT satisfied.** At least one critical path is not `audited_deep`; the "
            "paths below are the evidence behind the clause result."
        )
    elif c.set_size == 0:
        headline = (
            "**VACUOUSLY satisfied — the critical set is EMPTY.** The clause held "
            "because there was nothing in it to hold over, NOT because critical code "
            "was audited deep. Read this run's verdict accordingly."
        )
    else:
        headline = (
            "**Satisfied over a NON-EMPTY set.** Every path in the critical set is "
            "`audited_deep`; the gate is not vacuous."
        )
    out = [
        headline,
        "",
        f"- Clause satisfied (`critical_subsystems_all_deep`): **{c.all_deep}**",
        f"- Critical-set size (`CriticalSubsystemSet.paths`): **{c.set_size}**",
        "- Paths the DR-5 eligibility filter removed from the HEURISTIC term as "
        f"ineligible: **{c.excluded_ineligible_count}**",
        f"- `designated_but_unmatched` operator paths: **{len(c.designated_but_unmatched)}**",
    ]
    for path in c.designated_but_unmatched:
        out.append(f"  - `{path}`")
    out.append(f"- Critical paths NOT `audited_deep`: **{len(c.not_deep)}**")
    for path in c.not_deep:
        out.append(f"  - `{path}`")
    return out


def _render_ceiling_pair(proof: DogfoodProofRun) -> list[str]:
    """Render the CEILING HONESTY PAIR (PURE; Story 8.5 / AC1, D7).

    ``$X`` = :data:`DOGFOOD_BUDGET_CEILING` is a FROZEN historical execution parameter;
    the 7.1 generator re-sizes its ceiling from the live tree every derivation and has
    drifted away from it. Stating only one lets this artifact and the budget artifact —
    published together — disagree about "the 7.1 empirical ceiling". Both are stated,
    with a fit verdict for EACH.
    """
    cost = proof.cost
    out = [
        "**The ceiling honesty pair (Story 8.5 / AC1).** Two different numbers are in "
        "play and this artifact states both rather than letting them be confused:",
        "",
        f"- **Frozen historical execution parameter** `$X` = `DOGFOOD_BUDGET_CEILING` = "
        f"**{cost.ceiling}** credits — the ceiling this run was actually EXECUTED under. "
        "It is a pinned constant recording a past sizing, NOT a live measurement.",
    ]
    if cost.live_sized_ceiling is not None:
        out.append(
            "- **Live 7.1 sizing** — the `sized_ceiling` derived from the CURRENT tree by "
            "the same `build_full_repo_plan` call this generator already makes (REUSED — "
            f"no second accountant): **{cost.live_sized_ceiling}** credits. This is the "
            "number `minions-dogfood-budget-plan.md` publishes."
        )
        out.append(
            f"- Fits under the frozen `$X` = {cost.ceiling}: **{cost.fits_within_ceiling}** "
            f"· Fits under the live 7.1 sizing = {cost.live_sized_ceiling}: "
            f"**{cost.fits_within_live_sized_ceiling}**"
        )
    else:
        out.append(
            "- **Live 7.1 sizing:** not supplied to this derivation, so no live figure is "
            "stated here. Read `minions-dogfood-budget-plan.md` for the current sizing."
        )
    return out


def render_proof_markdown(proof: DogfoodProofRun) -> str:
    """Render the committed dogfood PROOF ARTIFACT (``minions-dogfood-proof.md``; PURE).

    Records: the run provenance + verdict, the within-ceiling + 3.2-halt confirmation, the
    SIGNED bundle locator + content hash (the "signature") + the no-source-retention +
    reproducibility claims, the honest ``grade: demo-heuristic-only`` flag + the
    externalization guard, the adjudication-ready finding classes (per-class ``rule_id`` +
    verdict-eligibility + count + sample locators + an empty TP/FP column for the human),
    and the OI1 provisional-gate report. Value-free — only provenance / counts / rule-ids /
    repo-relative locators (NFR-S1). Deterministic + byte-stable for the same proof.
    """
    b = proof.cost.baseline_ratio
    baseline_str = (
        f"{b.numerator}/{b.denominator}" if isinstance(b, Fraction) else str(b)
    )
    scope = _audited_tree_clause(proof)
    lines: list[str] = []
    lines.append(
        "# Argus Dogfood — Proof Artifact (Story 7.2 generator, RE-DERIVED by Story 8.5 "
        "as a SELF-audit)"
    )
    lines.append("")
    lines.append(
        f"> AUTO-GENERATED by `{_GENERATOR_MODULE}` "
        "(`render_proof_markdown`). Reproducible + byte-stable for the same tracked "
        "content of the tree named in §1 — do NOT hand-edit. "
        "Drivers: ArgusAgent-FR-29 / ArgusAgent-FR-17 / "
        "ArgusAgent-FR-30 / ArgusAgent-FR-21 / ArgusAgent-NFR-D1 / ArgusAgent-NFR-S1 / ArgusAgent-AR4 / ArgusAgent-AR7."
    )
    lines.append("")

    # ── Run provenance + verdict ────────────────────────────────────────────
    lines.append(
        f"## 1. Dogfood execution (AC-EXECUTE) — the frozen audit over {scope}"
    )
    lines.append("")
    lines.append(
        "**Derivation method: RE-RUN** (Story 8.5 / AC4). Every figure in this artifact "
        "was produced by EXECUTING the shipped pipeline on the tree named below, pinned "
        "by the commit descriptor and the `$X` ceiling recorded in §1 and §2. Nothing "
        "here is analytic, nothing is hand-written into the file, and no historical "
        "figure is hardcoded into the generator."
    )
    lines.append("")
    lines.append(
        "The frozen `pipeline.run_audit_detailed` (REUSED — no fork) was run over "
        f"{scope} of THIS repository. That tree was materialized into a CLEAN on-pin "
        "snapshot (the 6.5 `stage_cartridge` pattern) so the frozen "
        "`load_repo_at_commit` clean-tree precondition holds. The audited BYTES are this "
        "repository's own package source at the commit descriptor below."
    )
    lines.append("")
    lines.append(_SELF_AUDIT_HONESTY)
    lines.append("")
    lines.append(f"- Commit descriptor (HEAD at generation): `{proof.commit_descriptor}`")
    lines.append(f"- Source files audited: **{proof.source_file_count}**")
    lines.append(f"- Total physical LOC (build-cost proxy): **{proof.total_loc}**")
    lines.append(f"- Partition units (7.1 plan, CONSUMED): **{proof.unit_count}**")
    lines.append(
        f"- **Verdict: `{proof.verdict}` (exit `{proof.exit_code}`)**"
    )
    lines.append(f"- **Decision row (FR16 / DR-3), as DISCLOSED by the gate: {_row_token(proof)}**")
    lines.append(
        f"- Coverage-ledger deep-%: **`{proof.deep_ratio.numerator}/{proof.deep_ratio.denominator}`** "
        "(exact `Fraction`, never a float — AR4)"
    )
    lines.append(
        f"- Coverage-ledger deep count / total entries: **{proof.deep_count} / "
        f"{proof.total_count}**"
    )
    lines.append(f"- Blocking (verdict-eligible) findings: **{proof.blocking_finding_count}**")
    lines.append(f"- Total findings emitted: **{proof.total_finding_count}**")
    lines.append("")

    # ── The inputs the row was computed from (DR-3) ─────────────────────────
    lines.append("### 1a. The assessed population the row was computed from (DR-3)")
    lines.append("")
    lines.extend(_render_assessed_population(proof))
    lines.append("")
    lines.append(
        "### 1b. The critical-subsystem clause (FR4 / DR-5 / boundary B3)"
    )
    lines.append("")
    lines.extend(_render_critical_clause(proof))
    lines.append("")

    # ── Within-ceiling + 3.2 halt ───────────────────────────────────────────
    lines.append("## 2. Within the `$X` = 843 ceiling (AC-EXECUTE / FR21 / OI3) + the 3.2 halt")
    lines.append("")
    lines.append(
        f"The run's V1 deterministic zero-token cost total is **{proof.cost.total_credits} "
        "credits** (folded via the 3.1 `account_spend` — no fork)."
    )
    lines.append("")
    lines.extend(_render_ceiling_pair(proof))
    lines.append("")
    lines.append(
        f"- Under `BudgetConfig(ceiling_credits={proof.cost.ceiling})` the run FITS "
        f"(`ceiling_reached is False`): **{proof.cost.fits_within_ceiling}**"
    )
    lines.append(
        f"- Under a ceiling ONE credit below the total the run BREACHES "
        f"(the >=-is-a-breach REUSE — the 3.2 halt->skip->downgrade->report path fires): "
        f"**{proof.cost.breaches_below_total}**"
    )
    lines.append(
        f"- NFR-C1 baseline ratio (audit-cost / build-cost proxy): `{baseline_str}` "
        "(`Fraction`/marker — never a float)"
    )
    lines.append("")

    # ── SIGNED bundle ───────────────────────────────────────────────────────
    lines.append("## 3. The SIGNED, source-free evidence bundle (AC-BUNDLE / FR29 / NFR-A1 / NFR-S1)")
    lines.append("")
    lines.append(
        "Exported via the done 4.3 `build_evidence_bundle` + persisted via "
        "`persist_evidence_bundle` (REUSED — no forked bundle model / serializer), "
        "serialized THROUGH the single 1.1 `canonical.dumps_bytes` and stamped by the 1.1 "
        "content-addressed, **prev-hash-chained** envelope (the ArgusAgent \"signature\"; the "
        "point-in-time stamp is the envelope `created_at`, EXCLUDED from the hash — "
        "NFR-A1/D3)."
    )
    lines.append("")
    lines.append(f"- Persisted bundle locator: `{proof.bundle_locator}`")
    lines.append(f"- Bundle content hash (the signature): `{proof.bundle_content_hash}`")
    lines.append(f"- Canonical bundle byte length: **{proof.bundle_byte_length}**")
    lines.append(f"- Referential-integrity report consistent (4.2 lint): **{proof.integrity_consistent}**")
    lines.append(
        "- **No-source-retention MOAT (NFR-S1 / NFR-S3):** the bundle retains NO source "
        "byte and NO secret value — the moat is STRUCTURAL (no bundle field holds "
        "a source/secret value; only locations + redacted indicators). Proven over the "
        "REAL audited tree by `tests/test_secret_containment.py` "
        "(`TC-ArgusAgent-SECURITY-001-23`) and `tests/test_dogfood_proof.py` "
        "(`TC-ArgusAgent-DOGFOOD-001-22`)."
    )
    lines.append(
        "- **100% reproducibility (AC-REPRODUCIBLE / NFR-D1 / P1):** two dogfood runs on "
        "the same tracked content yield a BYTE-IDENTICAL verdict + bundle canonical bytes "
        "(the builder sorts/order-fixes every collection; no clock/float/set-order in the "
        "hashed payload). Demonstrated (RED against injected non-determinism, then green) "
        "in `tests/test_dogfood_proof.py` (`TC-ArgusAgent-DOGFOOD-001-24`)."
    )
    lines.append("")

    # ── Signature demo ──────────────────────────────────────────────────────
    lines.append("## 4. The `GitHub green · Sonar green · ArgusAgent 🔴` signature demo (AC-SIGNATURE)")
    lines.append("")
    lines.append(
        "ArgusAgent audits a vacuous test (the `vacuous_basic` cartridge — a test that runs "
        "green in CI while asserting nothing) and emits a **BLOCKING** `vacuous_test_ast` "
        "finding → verdict `NOT_READY_FOR_RELEASE` / exit `2` (the 🔴), reproducing the "
        "`GitHub green · Sonar green · ArgusAgent 🔴 tests appear vacuous` line as a real, "
        "repeatable committed artifact (the 1.7 `TC-ArgusAgent-PIPELINE-001-01` precedent). "
        "Asserted in `tests/test_dogfood_proof.py` "
        "(`test_signature_demo_vacuous_test_blocks`)."
    )
    lines.append("")

    # ── Demo-grade flag ─────────────────────────────────────────────────────
    lines.append("## 5. `grade: demo-heuristic-only` — the red-team honesty flag (AC-DEMO-GRADE)")
    lines.append("")
    lines.append(f"- **`grade: {proof.grade}`**")
    lines.append("")
    lines.append(f"> {DOGFOOD_EXTERNALIZATION_GUARD}")
    lines.append("")

    # ── Adjudication-ready findings ─────────────────────────────────────────
    lines.append("## 6. Adjudication-ready REAL findings (AC-ADJUDICATION-READY / OI1 / DF-6-6-A)")
    lines.append("")
    lines.append(
        "The REAL dogfood findings are laid out below by the 6.6 `finding_match_key` "
        "identity `(rule_id, verdict_eligible, advisory)` — one row per finding CLASS "
        "(two DISTINCT classes never collapse to one row — AI-E6-1). A human Eng-Lead + "
        "QA-Lead can tag each class TP/FP per `precision-validation-protocol.md` §4/§5 by "
        "inspecting the sample locators on the real repo. **The human TP/FP adjudication "
        "is NOT performed here (OI1 — it is the human step); the `TP/FP` column is left "
        "empty for the human.**"
    )
    lines.append("")
    lines.append("| rule_id | verdict-eligible (blocking) | advisory | count | sample locators | TP/FP (human) |")
    lines.append("|---|---|---|---|---|---|")
    for row in proof.adjudication:
        samples = "; ".join(f"`{s}`" for s in row.sample_locators) or "—"
        lines.append(
            f"| `{row.rule_id}` | {row.verdict_eligible} | {row.advisory} | {row.count} "
            f"| {samples} | {row.adjudication or '&nbsp;'} |"
        )
    lines.append("")

    # ── Provisional gate ────────────────────────────────────────────────────
    lines.append("## 7. The ≥80%-precision gate STAYS PROVISIONAL (AC-PROVISIONAL / OI1 keystone)")
    lines.append("")
    lines.append(
        "The synthetic corpus (7.1: 5 distinct classes) bootstrapped a PROVISIONAL "
        "≥80%-precision gate. **The gate is cleared ONLY by the human TP/FP adjudication "
        "over the REAL dogfood findings above** — a HUMAN step (Eng-Lead + QA-Lead), OUT "
        "of scope for this autonomous story. This proof presents NO ≥80% number as "
        "authoritative / cleared, does NOT flip `protocol_cleared`, and does NOT flip the "
        "6.5 `precision_gate_status()` marker."
    )
    lines.append("")
    lines.append(f"- Gate status: `{proof.gate_status}`")
    lines.append(
        "- The still-open human-adjudication step is filed as a defer (six CC-3 fields, "
        "`target_story: epic-7-minions-dogfood-precision`) in `deferred-work.md`."
    )
    lines.append("")
    return "\n".join(lines)
