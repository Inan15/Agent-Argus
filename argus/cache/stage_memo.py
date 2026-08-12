"""IMPURE composition — memoize the DETERMINISTIC detect/grade stage (FR27 / NFR-D1, Story 12.3).

Drivers: ArgusAgent-FR-27 (*reproduce the same verdict for the same repo + Argus version* — this
module is the production call site that finally makes the 5.1 key and the 5.2 store DO that),
ArgusAgent-NFR-D1 (*local content-addressed memoization* — **the mechanism**, not an assumption
that anything repeats itself), ArgusAgent-NFR-D2 (a HIT spends ZERO LLM tokens; this module
imports no provider surface), ArgusAgent-NFR-P1 (a served answer is byte-identical to a computed
one), ArgusAgent-AR5 (the key is derived by the ONE key function — consumed, never re-derived
and never composed ad hoc), ArgusAgent-AR7 (compose the existing key / store / index / request —
no fork of any of them), ArgusAgent-AR8 (this is the IMPURE shell; the pure cores it calls stay
pure), ArgusAgent-AR10 (a cache is ADVISORY — every typed cache failure degrades to a recompute,
never to a crash and never to a wrong answer), ArgusAgent-NFR-M1 (≤1200-line files).

What this module is
-------------------
Exactly one thing: *a production call site that derives a key and consults the store, around the
stage whose recomputation is the expensive part of a run.* The store (5.2), the key (5.1,
corrected by 10.2) and the invalidation contract (5.3) were all already built and test-proven —
what did not exist, from Epic 5 until this story, was anywhere in the product that USED them.
``argus.cache.memo_store`` was not even in the static import closure from ``argus.cli``.

WHERE THE HOOK SITS, AND WHY NOT ANYWHERE ELSE (DN-1)
-----------------------------------------------------
It wraps the per-file detect/grade stage plus the single cross-file orphan pass — the step that
produces ``(entries, findings, candidates)`` — and NOTHING else:

* **Not per-file.** The 5.1 closure is a UNIT fingerprint: ``content_hash`` is the unit's and
  ``work_manifest_files`` is a set. Keying per file is a key-SHAPE change, which means a
  ``CACHE_KEY_SCHEMA_VERSION`` bump, which is the exact migration cost the 10.2-before-12.3
  ordering exists to avoid.
* **Not around the deep pass.** See the fence note below. It runs downstream, and it is excluded.
* **Not around the verdict fold.** The verdict is a PURE function of the recordings. Memoizing it
  would cache the one thing whose recomputation is free and the one thing that must never be
  served from a stale input.

🔴 SCOPE DISCLOSURE — WHAT THIS DOES **NOT** DELIVER (§D.3(3), DF-12-3-A)
-------------------------------------------------------------------------
**PRD §501 (under FR36) is NOT delivered by this module, and a reader must not infer otherwise.**
That bullet says *"Determinism is preserved by the FR27/NFR-D1 memoization path — a re-run
returns the recorded result"* about the ``--deep-audit`` pass. It is not true yet:

* Memoization here covers the DETERMINISTIC stage only. The deep pass runs downstream, inside
  ``pipeline._assemble_and_persist``, and is never served from this store.
* **With ``--deep-audit`` on, a re-run DISPATCHES AGAIN.** The deep component of the verdict is
  reproducible only to the extent the provider repeats itself — which NFR-D1 itself calls
  infeasible. This story's guarantee holds for the DETERMINISTIC component of a verdict and NOT
  for the deep component.

Why it is scoped this way rather than quietly widened: (a) memoizing deep output today would
cache the ``empty-response`` degradations of ``DF-12-2-D``, and *"memoization caches errors →
reproducibility ≠ correctness"* is ``memo_store.py``'s own named failure mode; (b) doing it
honestly needs the CAPTURED checkpoint and a real prompt-template version folded into the key —
``deep_audit.build_closure_from_recording`` plus a claim grammar — which ``DF-12-2-D`` already
assigns to an owner; (c) the fence in ``memo_store._fence_llm_derived`` makes the collision
hazard impossible rather than leaving it for whoever wires deep memoization later. Filed as
``DF-12-3-A``. **Story 12.4 must not write next-action text implying a deep verdict is
reproducible.**
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from argus.cache.key import (
    CacheKeyError,
    DetectorDescriptor,
    FROZEN_DETECTOR_SET,
    RecordingProducingClosure,
    derive_cache_key,
)
from argus.cache.memo_store import MemoStore, RecordedStageResult
from argus.index.ast_index import AstIndex, AstIndexEntry, resolved_tool_version
from argus.intake.source_state import SourceState
from argus.models import AuditRequest
from argus.store.paths import WorkspaceContainmentError

__all__ = [
    "PINNED_TOOL_DISTRIBUTIONS",
    "StageMemoOutcome",
    "stage_detector_set",
    "build_stage_closure",
    "memoize_detect_stage",
]

# The pinned distributions whose versions determine a recording's output and therefore belong
# in the closure. Probed through the EXISTING impure resolver (AR7/AR8), never re-implemented;
# an uninstalled distribution resolves to "unknown", which is stable on a given host and so
# still keys honestly (AR10).
#
# * ``radon`` — what the breadth detector (``detectors/tool_runner.py``) runs on. Its findings
#   ARE in the memoized payload, so a radon upgrade that moves a complexity metric must move
#   the key, or the store would serve metrics computed by a different tool.
# * ``argus-agent`` — ARGUS ITSELF, and it is not decoration. FR27 promises the same verdict
#   for *"the same repository AND ARGUS VERSION"*, which means an Argus upgrade is entitled to
#   a different answer — and a cache that does not know the tool changed would serve the OLD
#   answer across that upgrade, which is the "memoization caches errors" failure arriving
#   through the front door. The declared ``DetectorDescriptor.code_identity`` tokens cover a
#   detector whose logic changes, but they are hand-bumped and they cover only detectors: a
#   change to the grader, the orphan pass, the index's extraction vocabulary or the ledger is
#   invisible to them. Folding the distribution version makes every Argus upgrade a natural
#   MISS, which is the conservative direction (a needless recompute is correct; a stale serve
#   is not).
PINNED_TOOL_DISTRIBUTIONS: tuple[str, ...] = ("argus-agent", "radon")


@dataclass(frozen=True)
class StageMemoOutcome:
    """What the memo hook did, so a caller (and a test) can tell a HIT from a recompute.

    ``served_from_store`` is the honest name: it says the payload CAME FROM the store, not
    merely that a key was derived. ``key`` is ``None`` when the key could not be derived at
    all, which is the one state in which the run proceeds with no memoization whatsoever.
    """

    result: RecordedStageResult
    key: str | None
    served_from_store: bool


def stage_detector_set(request: AuditRequest) -> tuple[DetectorDescriptor, ...]:
    """The LIVE detector descriptor set for this run — the FROZEN set with runtime config bound.

    THIS IS THE LOAD-BEARING PART OF THE CLOSURE, and it is easy to get wrong in a way that
    is silently unsafe. The memoized stage does not depend only on the repository's content:
    it also depends on WHICH passes the operator enabled and WHICH paths/patterns they told
    the secret scanner to ignore. ``_detect_per_file`` reads exactly ``request.enabled_passes``,
    ``request.ignore_paths`` and ``request.ignore_patterns``; ``_orphan_findings`` reads
    ``request.enabled_passes``. If any of those were left out of the key, two runs with
    different ``--passes`` or ``--ignore-path`` would COLLIDE ON ONE SLOT and the second would
    be served the first's answer — a cache serving a result computed under a configuration
    the caller did not ask for.

    They are folded through ``DetectorDescriptor.config``, which is precisely what that field
    is for (*"the determinism-relevant settings"* — editing one MOVES the set hash and so MOVES
    the key: the AR6 invalidation lever Story 5.3 rides). That means NO new closure field, so
    ``CACHE_KEY_SCHEMA_VERSION`` stays ``"3"`` (DN-4) and the frozen set is REUSED rather than
    re-enumerated (§C.4 — never a second enumeration).

    The whole stage configuration is bound to EVERY descriptor rather than attributed
    detector-by-detector. That is deliberate: attribution would require this module to hold a
    private opinion about which setting governs which detector, and an attribution that drifts
    from the real gating is an UNDER-key — the unsafe direction. Binding all of it to all of
    them is redundant in the hash and costs nothing, and redundancy here can only ever cause an
    extra MISS (a recompute, which is correct) and never a wrong serve.
    """
    stage_config: dict[str, object] = {
        "enabled_passes": sorted(request.enabled_passes),
        "ignore_paths": sorted(request.ignore_paths),
        "ignore_patterns": sorted(request.ignore_patterns),
    }
    return tuple(
        descriptor.model_copy(update={"config": dict(stage_config)})
        for descriptor in FROZEN_DETECTOR_SET
    )


def build_stage_closure(
    *,
    request: AuditRequest,
    index: AstIndex,
    assessed_entries: tuple[AstIndexEntry, ...],
    source_state: SourceState,
) -> RecordingProducingClosure:
    """Build the recording-producing closure for the memoized stage (AC2.1).

    Every input is taken from LIVE structure, never from a hand-maintained list:

    * ``content_hash`` — ``source_state.identity``. It is content-faithful in all three
      source-state kinds by construction: a ``commit`` identity is only issued for a CLEAN
      git tree, and both the ``worktree`` and ``directory`` identities embed
      ``_digest_of``, a sha256 over the audited files' actual bytes. So ANY source byte that
      changes moves this input — which is what makes a changed file a natural MISS rather
      than a stale hit. It also REUSES the intake digest instead of adding a second hasher.
    * ``grammar_versions`` — the LIVE ``AstIndex.grammar_versions``: the grammars that
      ACTUALLY PARSED in this build (10.2 / DN-6). Not a hand-listed language set, and not
      every grammar INSTALLED on the host, which would key on the machine instead of the
      audit and is the exact inverse of the defect 10.2 closed.
    * ``work_manifest_files`` — the ASSESSED entries' paths, so a budget ceiling that changes
      what the run actually audits changes the slot it reads.
    * ``detectors`` — :func:`stage_detector_set` (see its note; this is where the operator's
      pass/ignore configuration enters the key).
    * ``model_checkpoint`` / ``prompt_template_version`` — left at their V1 defaults, which is
      what the ``memo_store`` fence keys on. Substituting a real captured checkpoint here is
      Story 6.1's job, and doing it would stand the fence down deliberately rather than by
      accident.
    """
    return RecordingProducingClosure(
        content_hash=source_state.identity,
        detectors=stage_detector_set(request),
        grammar_version=index.grammar_version,
        grammar_versions=index.grammar_versions,
        tool_versions={
            distribution: resolved_tool_version(distribution)
            for distribution in PINNED_TOOL_DISTRIBUTIONS
        },
        budget=request.budget,
        materiality_bar=request.materiality_bar or "none",
        work_manifest_files=tuple(entry.file_path for entry in assessed_entries),
        critical_paths=tuple(request.critical_paths),
        excluded_critical_paths=tuple(request.excluded_critical_paths),
    )


def memoize_detect_stage(
    *,
    repo_root: Path,
    request: AuditRequest,
    index: AstIndex,
    assessed_entries: tuple[AstIndexEntry, ...],
    source_state: SourceState,
    compute: Callable[[], RecordedStageResult],
) -> StageMemoOutcome:
    """Serve the detect/grade stage from the memo store, or compute it and record it.

    The whole contract in one sentence: **the answer is the same either way.** A HIT returns
    the payload the previous run recorded; a MISS calls *compute* and stores what it produced.
    ``memo_store``'s own invariant — *"the verdict is correct WHETHER OR NOT the cache exists /
    is warm / is wiped"* — is what this function must not break, and it is why every failure
    below falls back to computing rather than raising.

    AR10 — WHAT DEGRADES AND WHAT DOES NOT. A cache is ADVISORY. A malformed closure
    (:class:`CacheKeyError`), a containment refusal, or an unwritable ``.argus/`` tree all
    degrade to *"run the stage, skip the cache"*: the audit completes and its answer is
    byte-identical to a cold run, because it IS a cold run. The degradation costs time, never
    correctness. The named typed set only — no bare ``except``, no ``except Exception`` — so a
    programming bug still surfaces, and ``DeepMemoizationFenceError`` is deliberately NOT in
    the set: it means a caller tried to memoize LLM-derived output, which is a defect at the
    call site and must be loud.
    """
    try:
        closure = build_stage_closure(
            request=request,
            index=index,
            assessed_entries=assessed_entries,
            source_state=source_state,
        )
        key = derive_cache_key(closure)
    except (CacheKeyError, ValueError):
        # A closure this run cannot fingerprint is a run that is not memoized. It is NOT a
        # run that fails: nothing about the audit's correctness depends on the cache.
        return StageMemoOutcome(result=compute(), key=None, served_from_store=False)

    store = MemoStore(repo_root)
    served = store.lookup_stage(key)
    if served is not None:
        return StageMemoOutcome(result=served, key=key, served_from_store=True)

    result = compute()
    try:
        # The checkpoint slots are taken from THE CLOSURE THE KEY WAS DERIVED FROM, never
        # re-stated as literals here. That is what makes the fence honest: it is asked
        # whether THIS payload is safe under THIS key, and the two cannot drift apart.
        store.store_stage(
            key,
            result,
            model_checkpoint=closure.model_checkpoint,
            prompt_template_version=closure.prompt_template_version,
        )
    except (WorkspaceContainmentError, OSError):
        # An unwritable or escaping cache slot must not fail an audit that has already
        # done its work. The next run simply misses again.
        pass
    return StageMemoOutcome(result=result, key=key, served_from_store=False)
