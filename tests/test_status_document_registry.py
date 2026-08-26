"""WHICH planning records are governed by the evidence-citation rule, and is that set closed?

Verification area ArgusAgent-DOCS. This module holds ``TC-ArgusAgent-DOCS-001-21`` and
``TC-ArgusAgent-DOCS-001-22``, **relocated verbatim** from ``tests/test_evidence_citation.py``
by Story 13.4 (2026-08-17). **It opens NO new test ids and no new verification area.** Every id
here already existed, at the same number, in the module named below; a relocation that renumbered
anything would silently invalidate the citations at ``architecture.md:648``/``:964``, at
``deferred-work.md:1384``/``:2236``/``:2523`` (one of which is a full pytest node id) and in five
test modules.

**Where the other half went, and why.** ``tests/test_evidence_citation.py`` keeps the DERIVATION —
*what* a status claim is, *what* an executed-gate citation is, and whether the records and the
consumer surfaces carry them (``-20``, ``-21b``, ``-23``, ``-24``, ``-25``, ``-25b``). This module
owns the POPULATION — *which* records are governed, and whether that set is closed against the
tree. Two questions, two modules, one import edge.

**Why the boundary is here (DN-1), chosen by measurement and not by line count.**
``_STATUS_DOCUMENTS`` has exactly three readers — ``_registered_paths``, ``-21`` and ``-22`` — and
none of them is ``-20``, ``-21b``, ``-23``, ``-24``, ``-25`` or ``-25b`` (verified by reference
scan). So the registry, its glob closure and its exclusion table lift out as a closed unit with a
single import edge. The rejected alternative was splitting off the Story 12.9 release-surface half
(``-24``/``-25``/``-25b``): it moves more lines, it would read as choosing whichever boundary helps
the arithmetic most — the thing ``test_module_size_ceiling.py::_REMEDY`` forbids — and it would
leave the registry in the module that was full. It stays on record as the *next* boundary, which is
a different decision for a different day.

**Why ``-21b`` did NOT move with ``-21`` (DN-2).** ``-21b`` is the positive control for
``_status_assertions`` and ``_executed_gate_citations``: it drives them over synthetic and quoted
strings and **never reads** ``_STATUS_DOCUMENTS``. Its subject is the derivation, so it belongs
beside the derivation. Moving it because its id says ``21`` would separate a control from the code
it controls and put the derivation's two controls (``-21b`` and ``-25b``) in different modules for
no stated reason — a line-count decision wearing an id's clothes. So: **``-21``'s control lives in
``tests/test_evidence_citation.py``**, next to what it controls.

**The one import edge (DN-3) is new → old, once, and never back.** This module imports four
derivation symbols from ``tests/test_evidence_citation.py``; that module must never import from
this one, because a circular import between two test modules fails at collection. It therefore
declares this module's path as a literal beside its own ``_GUARD_FILE``, with a comment saying why.
Importing rather than copying is AR7: a rule with two implementations is a fork, and this project
has recorded that defect four times.

**Why the registry is PYTHON and not a data file (DN-4).** ``AI-E13-2`` offered *"or move the
registry to a data file"* and it is rejected: every entry in ``_STATUS_DOCUMENTS`` carries a prose
comment recording why and when it was registered and what was verified before registering it. A
JSON or YAML sidecar either loses those or turns them into uncommentable data, and it would let the
governed population be edited without touching a guard.

**No network, no LLM, no subprocess, no ``.argus/`` write** — pure functions over committed bytes,
so this runs identically on all three CI legs. Every file is opened ``encoding="utf-8"``
explicitly: the artifact tree carries non-ASCII and an inherited host locale is the exact defect
class that turned run ``31322881580`` red.
"""

from __future__ import annotations

from pathlib import Path

# Derived paths, not policy — re-derived here from `__file__` exactly as every other test module
# in this tree does (`test_module_size_ceiling.py`, `test_governance_record_integrity.py`), rather
# than imported, so this module's own location is what locates the tree.
_REPO_ROOT = Path(__file__).resolve().parents[1]
_ARTIFACT_DIR = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"

# The DERIVATION, imported from the module that owns it and never copied (DN-3 / AR7). These four
# symbols are the entire dependency: what counts as a status assertion, what counts as an executed
# gate citation, how text is split into sentences, and the marker that records an unestablished
# status. Their positive control (`-21b`) stays with them, in that module (DN-2).
from tests.test_evidence_citation import (  # noqa: E402
    _NOT_ESTABLISHED_MARKER,
    _executed_gate_citations,
    _split_sentences,
    _status_assertions,
)

# Every status-asserting planning record under the artifact directory, as of Story 10.1.
# The registry is the enumerated space; `-22` resolves the globs below against the tree and
# fails on anything found here that nobody registered.
_STATUS_DOCUMENTS: tuple[str, ...] = (
    "sprint-change-proposal-2026-07-28.md",
    "sprint-change-proposal-2026-08-03.md",
    "sprint-change-proposal-2026-08-09.md",
    "sprint-change-proposal-2026-08-10.md",
    "sprint-change-proposal-2026-08-10b.md",
    "epic-1-retro-2026-06-21.md",
    "epic-2-retro-2026-06-24.md",
    "epic-3-retro-2026-06-27.md",
    "epic-4-retro-2026-06-28.md",
    "epic-5-retro-2026-06-29.md",
    "epic-6-retro-2026-07-02.md",
    "epic-7-retro-2026-07-04.md",
    "epic-8-retro-2026-08-08.md",
    "epic-9-retro-2026-08-09.md",
    # Registered by Story 12.1 (2026-08-12), closing DF-11-1-A. `-22` had been carved out by node
    # id by five consecutive stories because these two retrospectives existed on disk but were
    # unregistered. Registration is INERT against every other assertion in this file:
    # `_status_assertions()` returns 0 status assertions for each (verified by execution), so the
    # per-document loop in `-21` short-circuits. No retrospective was edited and no citation minted.
    "epic-10-retro-2026-08-11.md",
    "epic-11-retro-2026-08-12.md",
    # Registered on 2026-08-15 (AI-E12-1), the same one-line edit for the same reason: `-22`'s
    # glob closure sees `epic-*-retro-*.md` the moment the file lands, which is the closure
    # working as designed — the Epic-12 retrospective predicted this red about itself (§6 SD-3)
    # and was written to go green on registration alone. Verified by execution before
    # registering, exactly as the entry above records: `_status_assertions()` returns 0 for it
    # (no phrase in `_STATUS_CLAIMS` occurs in the document at all, denied or otherwise), so
    # `-21`'s per-document loop short-circuits, and `_executed_gate_citations()` returns 0, so
    # it mints no excuse for anything. Its release-status statements are all NOT ESTABLISHED
    # and name the superseded run with the `_CITATION_DENIAL_MARKERS`. No retrospective was
    # edited and no citation minted.
    "epic-12-retro-2026-08-15.md",
    "epic-13-retro-INTERIM-2026-08-17.md",  # Registered 2026-08-17 by the Epic-13 INTERIM retrospective, discharging AI-E12-1's SECOND half ("make the registration part of the retrospective step's own DoD") for the first time. Same one-line edit, same reason, same verification-before-registration as the two entries above: `-22` was observed RED against this document and GREEN after, and `_status_assertions()` returns 0 for it (no phrase in `_STATUS_CLAIMS` occurs in it at all), so `-21`'s per-document loop short-circuits and the registration is inert. It DOES carry 2 well-formed run+sha citations, which mint an excuse for nothing because there is no claim to excuse. No retrospective was edited. ~~⚠️ THIS LINE PUTS THIS FILE AT EXACTLY 1200/1200 (NFR-M1; `MAINT-001-03` pins 1201 as the failure). The NEXT status document cannot be registered until this module is split — filed as AI-E13-2, and it blocks the FINAL Epic-13 retrospective.~~ SUPERSEDED 2026-08-17 by Story 13.4 (§3.4 — strike, never erase): that sentence was true of `tests/test_evidence_citation.py`, and it is no longer true of this registry, which now lives in `tests/test_status_document_registry.py` with headroom for many further registrations. The remedy taken was the sanctioned COHESION SPLIT — not a shave and not an `_EXEMPT_BY_DESIGN` entry, both of which `AI-E13-2` and `_REMEDY` forbid by name. AI-E13-2 is discharged.
    # Registered 2026-08-17 by Story 13.4, and it is the reason this module exists rather than a
    # beneficiary of it: this document is the APPROVED sprint change proposal that Epic 14 and
    # Story 13.5 rest on, and writing it to the artifact directory took `-22` RED on the live tree
    # — the deadlock of §0.1, happening for real rather than as a probe. It could not be registered
    # in the old host at 1200/1200 without breaching NFR-M1, which is precisely what this split
    # repaired. Verified before registering, in the same form as every entry above: the document
    # states its own release-status claims and each carries either an executed-gate citation or the
    # NOT ESTABLISHED marker, so `-21` passes over it rather than short-circuiting past it.
    "sprint-change-proposal-2026-08-17.md",
    # Registered 2026-08-17 by the correct-course run that wrote it — the registration is part of
    # writing the document, not a later cleanup, which is AI-E12-1's second half applied to a change
    # proposal for the first time. `-22` was observed RED against this document before this line and
    # GREEN after, on the live tree. Verified before registering, in the same form as every entry
    # above: `_status_assertions()` returns 0 for it — no phrase in `_STATUS_CLAIMS` occurs in it at
    # all, denied or otherwise — so `-21`'s per-document loop short-circuits and this registration is
    # inert rather than load-bearing. It is a DRAFT proposal (Epic 14 / Story 14.3, the cross-language
    # assertion vocabulary) and asserts no release status of any kind; the one status-shaped sentence
    # it does carry, §2.3's corpus-impact claim, is labelled UNMEASURED in the document itself rather
    # than cited, because it is a derivation and citing it would mint exactly the excuse `-21` exists
    # to refuse.
    "sprint-change-proposal-2026-08-17b.md",
    # Registered 2026-08-18 by the Epic-14 retrospective that wrote it — `AI-E12-1`'s SECOND half
    # ("make the registration part of the retrospective step's own DoD") on its second consecutive
    # application, after the Epic-13 INTERIM entry above established it. Same one-line edit, same
    # reason, same verification-before-registration: `-22`'s glob closure sees `epic-*-retro-*.md`
    # the moment the file lands, and it was observed RED against this document before this line and
    # GREEN after, on the live tree. `_status_assertions()` returns 0 for it — no phrase in
    # `_STATUS_CLAIMS` occurs in it at all, denied or otherwise — so `-21`'s per-document loop
    # short-circuits and this registration is inert rather than load-bearing. The document asserts
    # no release status of any kind: it records that the precision gate is UNCHANGED by Epic 14,
    # that CI evidence is NOT ESTABLISHED for every commit in that epic, and that the FR34
    # disclosure stands. No retrospective was edited and no citation minted.
    # ⚠️ It must be committed TOGETHER with this line — `-22` closes in BOTH directions, so the
    # document without this entry and this entry without the document red `master` equally.
    "epic-14-retro-2026-08-18.md",
    # Registered 2026-08-19 by the FINAL Epic-13 retrospective that wrote it — `AI-E12-1`'s SECOND
    # half on its third consecutive application, and the first one this module was built for: the
    # INTERIM entry above carries the struck sentence saying the NEXT status document could not be
    # registered until `tests/test_evidence_citation.py` was split. Story 13.4 performed that split
    # and THIS is that next document. Same one-line edit, same verification-before-registration:
    # `-22` was observed RED against it before this line (`unregistered:
    # ['epic-13-retro-2026-08-19.md']`) and GREEN after, on the live tree. `_status_assertions()`
    # returns 0 for it — no phrase in `_STATUS_CLAIMS` occurs in it at all, denied or otherwise —
    # so `-21`'s per-document loop short-circuits and this registration is inert rather than
    # load-bearing. `_executed_gate_citations()` returns 0, so it mints an excuse for nothing. The
    # document asserts no release status of any kind: it records the gate outcome as BLOCKED with
    # the precision condition UNEVALUABLE, that the FR34 disclosure stands unchanged, and that CI
    # evidence is NOT ESTABLISHED for every commit in Epic 14, Story 13.4 and Story 13.5. It
    # SUPERSEDES the INTERIM document by name and does not edit it (§3.4 — records are superseded,
    # never erased), so both remain registered and both are found by the globs.
    # ⚠️ It must be committed TOGETHER with this line — `-22` closes in BOTH directions, so the
    # document without this entry and this entry without the document red `master` equally.
    "epic-13-retro-2026-08-19.md",
    # Registered 2026-08-19 by the correct-course run that wrote it — the registration is part of
    # writing the document, not a later cleanup (`AI-E12-1`'s second half, applied to a change
    # proposal for the second time after `sprint-change-proposal-2026-08-17b.md` established it
    # here). `-22` was observed RED against this document before this line (`unregistered:
    # ['sprint-change-proposal-2026-08-19.md']`) and GREEN after, on the live tree, and the full
    # suite was re-run green afterwards. Verified before registering, in the same form as every
    # entry above: `_status_assertions()` returns 0 for it — no phrase in `_STATUS_CLAIMS` occurs
    # in it at all, denied or otherwise — so `-21`'s per-document loop short-circuits and this
    # registration is inert rather than load-bearing. `_executed_gate_citations()` returns 0, so it
    # mints an excuse for nothing. The document asserts no release status of any kind: it is the
    # APPROVED proposal that adds Story 15.2 to Epic 15 (the line-numbering contract between
    # `argus/detectors/vacuous_test.py` and the Story 1.4 index), and the one status-shaped
    # question it raises — whether the defect can reach verdict-eligibility — is recorded as NOT
    # established in either direction and pushed into that story's AC1 rather than answered here.
    # ⚠️ It must be committed TOGETHER with this line — `-22` closes in BOTH directions, so the
    # document without this entry and this entry without the document red `master` equally.
    "sprint-change-proposal-2026-08-19.md",
    # Registered 2026-08-19 by the Epic-15 retrospective that wrote it — `AI-E12-1`'s SECOND half
    # ("make the registration part of the retrospective step's own DoD") on its FOURTH consecutive
    # application, after the Epic-13 INTERIM, Epic-14 and FINAL Epic-13 entries above established
    # it. Same one-line edit, same reason, same verification-before-registration: `-22` was observed
    # RED against this document before this line (`unregistered:
    # ['epic-15-retro-2026-08-19.md']`) and GREEN after, on the live tree.
    # `_status_assertions()` returns 0 for it — no phrase in `_STATUS_CLAIMS` occurs in it at all,
    # denied or otherwise — so `-21`'s per-document loop short-circuits and this registration is
    # inert rather than load-bearing. `_executed_gate_citations()` returns 0, so it mints an excuse
    # for nothing. The document asserts no release status of any kind: it records that the precision
    # gate is UNCHANGED and still `UNEVALUABLE`, that the FR34 disclosure stands, that protocol §6
    # R2 ratification has NOT been taken (all 14 candidate rows remain `eligible_for_n=False` and
    # `eligible_member_count()` is 5), that `DF-13-5-A`'s ONE pre-registered round is UNSPENT, and
    # that publication is NOT ESTABLISHED — `git tag -l` empty, no release. It dispositions NO
    # ledger entry and edits no planning document.
    # ⚠️ It must be committed TOGETHER with this line — `-22` closes in BOTH directions, so the
    # document without this entry and this entry without the document red `master` equally.
    "epic-15-retro-2026-08-19.md",
    # Registered 2026-08-20 by the change proposal that carries it — `AI-E12-1`'s second half
    # ("make the registration part of the authoring step's own DoD") on its FIFTH consecutive
    # application. Same one-line edit, same verification-before-registration: `-22` was observed
    # RED against this document before this line (`unregistered:
    # ['sprint-change-proposal-2026-08-20.md']`) and GREEN after, on the live tree.
    # `_status_assertions()` returns 0 for it and `_executed_gate_citations()` returns 0, so
    # `-21`'s per-document loop short-circuits and this registration is inert rather than
    # load-bearing — it mints an excuse for nothing.
    # WHAT THE DOCUMENT ASSERTS, so the registration is judged against its contents: the gate is
    # UNCHANGED and still `BLOCKED` with an empty precision denominator; `protocol_cleared` is
    # `False` and has never been `True`; the >=80% threshold, `VALIDATION_SET_FLOOR_N`, FR34 and
    # the five ratified members are untouched; all 14 candidate rows stay `eligible_for_n=False`;
    # `DF-13-5-A`'s ONE round is UNSPENT. It PROPOSES a §5 amendment in the STRENGTHENING
    # direction and applies none of it — the document is `AWAITING OPERATOR APPROVAL`, which is a
    # status about the proposal and not a release status about the tool.
    # ⚠️ It must be committed TOGETHER with this line — `-22` closes in BOTH directions, so the
    # document without this entry and this entry without the document red `master` equally.
    "sprint-change-proposal-2026-08-20.md",
    # Registered 2026-08-20 by the operator decision that received it (XAgent007) — `AI-E12-1`'s
    # second half ("make the registration part of the authoring step's own DoD") on its SIXTH
    # consecutive application, and the FIRST one applied to a document that is NOT approved.
    # REGISTRATION IS NOT APPROVAL, and this entry is the place that says so. The operator ruled
    # "register it, do NOT approve it": this line places the document under `-21`'s citation rule
    # and inside `-22`'s closure, and does nothing else. The document's own §7.4 asked for exactly
    # this and no more. Its status line still reads `AWAITING OPERATOR APPROVAL`; no Epic 17 or
    # Epic 18 container was written to `epics.md`; no key was added to sprint-status.yaml's
    # `development_status` map; not one byte of the document's substance was edited. A registered
    # proposal is a GOVERNED proposal, not an accepted one — the registry answers "is this record
    # covered by the citation rule", never "was this record approved", and reading a registration
    # as an approval would be the exact category error `-21` exists to refuse.
    # Same one-line edit and same verification-before-registration as every entry above: `-22` was
    # observed RED against this document before this line (`status-asserting document(s) exist but
    # are not registered: ['sprint-change-proposal-2026-08-20-amendment-A.md']`) and GREEN after,
    # on the live tree, with the full suite re-run green afterwards. Verified by execution:
    # `_split_sentences()` returns 225 sentences, so `-21` is genuinely reading the document rather
    # than passing over an unparseable one; `_status_assertions()` returns 0 — no phrase in
    # `_STATUS_CLAIMS` occurs in it at all, denied or otherwise — so `-21`'s per-document loop
    # short-circuits and this registration is inert rather than load-bearing; and
    # `_executed_gate_citations()` returns 0, so it mints an excuse for nothing. The `RELEASE_READY`
    # in its appendix is a verdict the tool RETURNED about an audited third-party repository, which
    # is a measurement about someone else's tree and not a release status about ArgusAgent.
    # WHAT THE DOCUMENT ASSERTS, so the registration is judged against its contents: it PROPOSES
    # two epic containers (17, 18) and an FR38 pre-condition gate, and applies none of it. The
    # parent proposal, Epic 16 and the in-flight Story 16.1 are untouched and uncontested by it;
    # the >=80% threshold, `VALIDATION_SET_FLOOR_N`, `MANIFEST_FIELDS`, FR34, `protocol_cleared`
    # and the five ratified members are untouched; no FR is added, amended or dispositioned; no
    # ledger entry is dispositioned; `DF-13-5-A`'s ONE round is UNSPENT, no bench round was spent,
    # no candidate ratified and no row moved off `UNADJUDICATED`.
    # ⚠️ It must be committed TOGETHER with this line — `-22` closes in BOTH directions, so the
    # document without this entry and this entry without the document red `master` equally.
    "sprint-change-proposal-2026-08-20-amendment-A.md",
    # Registered 2026-08-22 by the research + measurement session that wrote it — the registration is
    # part of writing the document, not a later cleanup (`AI-E12-1`'s second half, applied to a change
    # proposal again). `-22` was observed RED against this document before this line
    # (`unregistered: ['sprint-change-proposal-2026-08-22.md']`) and GREEN after, on the live tree.
    # Verified before registering, in the same form as every entry above: `_status_assertions()`
    # returns 0 for it — no phrase in `_STATUS_CLAIMS` occurs in it at all, denied or otherwise — so
    # `-21`'s per-document loop short-circuits and this registration is inert rather than
    # load-bearing. `_executed_gate_citations()` returns 0, so it mints an excuse for nothing. The
    # document asserts no release status of any kind: it is a proposal adding Stories 16.6 and 16.7
    # to Epic 16 (the assertion-vocabulary defect, then adjudication of the silent-test class).
    # It was registered here while UNAPPROVED and was ✅ APPROVED by XAgent007 later the same day
    # (2026-08-22), with §4's edits applied on approval — the two acts kept separate on the §4.3
    # precedent. Re-verified after approval: `_status_assertions()` still returns 0 and
    # `_executed_gate_citations()` still returns 0, so this registration remains inert. It proposes
    # NO bench expansion, NO ratification,
    # NO gate or protocol amendment and NO promotion of any finding, and it WITHDRAWS its own
    # predecessor's falsified 250-candidate estimate in place rather than restating it quietly.
    # ⚠️ It must be committed TOGETHER with this line — `-22` closes in BOTH directions, so the
    # document without this entry and this entry without the document red `master` equally.
    "sprint-change-proposal-2026-08-22.md",
    # Registered 2026-08-23 for the Epic-16 retrospective — `AI-E12-1`'s second half ("make the
    # registration part of the retrospective step's own DoD") on its FIFTH consecutive
    # retrospective, after the Epic-13 INTERIM, Epic-14, FINAL Epic-13 and Epic-15 entries above.
    # It is also the FIRST registration NOT written by the session that wrote the document, and
    # that break is recorded here rather than smoothed over: the retrospective worker was chartered
    # READ-ONLY over `tests/` on a working tree shared with another active session, so it could not
    # add this line, and instead filed the omission against itself as `AI-E16-15` — item 0 of its
    # own critical path — stating that the tree was RED from the moment the document was written.
    # This entry is that action item discharged by a separate chartered session: registration, and
    # nothing else. The document's content, its action items and every `development_status` value
    # were left untouched by the session that added this line.
    # Same one-line edit and same verification-before-registration as every entry above: `-22` was
    # observed RED against this document before this line (`status-asserting document(s) exist but
    # are not registered: ['epic-16-retro-2026-08-23.md']`) and GREEN after, on the live tree, with
    # the full suite re-run green afterwards. Verified by execution: `_split_sentences()` returns
    # 498 sentences, so `-21` is genuinely reading the document rather than passing over an
    # unparseable one; `_status_assertions()` returns 0 — no phrase in `_STATUS_CLAIMS` occurs in it
    # at all, denied or otherwise — so `-21`'s per-document loop short-circuits and this
    # registration is inert rather than load-bearing; and `_executed_gate_citations()` returns 0, so
    # it mints an excuse for nothing. ⛔ No `_EXCLUDED_BY_DESIGN` entry was added and not one
    # assertion in `-22` was weakened, reworded or exempted — `AI-E16-15` names that as the escape
    # route to refuse, and `-22`'s written-reason rule exists to close it.
    # WHAT THE DOCUMENT ASSERTS, so the registration is judged against its contents: the gate is
    # UNCHANGED and still `BLOCKED`, with 7 recorded conditions and an empty precision denominator;
    # the precision figure STILL DOES NOT EXIST; `eligible_member_count()` is 5 and all 14
    # candidates remain `eligible_for_n=False`; nothing was ratified and the protocol was not
    # re-versioned; `DF-13-5-A`'s ONE pre-registered round is OPEN and UNSPENT, with its re-review
    # trigger recorded as FIRED and the spend-or-decline branch explicitly NOT taken here; FR34's
    # DISCLOSED tier stands unchanged as the honest fallback; and deployment/release is recorded as
    # NOT ESTABLISHED for anything outward-facing. It dispositions NO ledger entry — §10 RE-DERIVES
    # the ledger against `deferred-work.md` on disk and edits it not at all — and it amends no FR,
    # no threshold, no epic container and no planning document.
    # ⚠️ It must be committed TOGETHER with this line — `-22` closes in BOTH directions, so the
    # document without this entry and this entry without the document red `master` equally.
    "epic-16-retro-2026-08-23.md",
    # Registered 2026-08-24 by the `bmad-correct-course` session that wrote it — the registration is
    # part of writing the document, not a later cleanup (`AI-E12-1`'s second half). This is the
    # SECOND consecutive registration written by the authoring session after `AI-E16-15` broke the
    # streak for a stated reason, and unlike that one this session was NOT read-only over `tests/`,
    # so the line lands in the same commit as the document.
    # Same verification-before-registration as every entry above, by execution: `_split_sentences()`
    # returns 133 sentences, so `-21` is genuinely reading the document rather than passing over an
    # unparseable one; `_status_assertions()` returns 0 — no phrase in `_STATUS_CLAIMS` occurs in it
    # at all, denied or otherwise — so `-21`'s per-document loop short-circuits and this
    # registration is inert rather than load-bearing; and `_executed_gate_citations()` returns 0, so
    # it mints an excuse for nothing. `-22` was observed RED against this document before this line
    # (`status-asserting document(s) exist but are not registered:
    # ['sprint-change-proposal-2026-08-24.md']`) and GREEN after, on the live tree, with the full
    # suite re-run green afterwards. ⛔ No `_EXCLUDED_BY_DESIGN` entry was added and not one
    # assertion in `-22` was weakened, reworded or exempted.
    # WHAT THE DOCUMENT ASSERTS, so the registration is judged against its contents: it CREATES two
    # epic containers (17 and 18) and thirteen `backlog` keys, and it changes NO release status of
    # any kind. The >=80% precision gate is UNCHANGED, still `BLOCKED` and still NOT CLEARED; the
    # precision figure STILL DOES NOT EXIST; `eligible_member_count()` is 5 and all 14 candidates
    # remain `eligible_for_n=False`; nothing is ratified, no third-party source is fetched and the
    # protocol is not re-versioned; `DF-13-5-A`'s ONE round is OPEN and UNSPENT, DECLINED a second
    # time on 2026-08-24 with a substantive replacement trigger, and this proposal explicitly does
    # NOT spend it; FR34's DISCLOSED tier stands unchanged as the honest fallback. It amends no FR,
    # no threshold and no delivered epic — Epics 1–16 are NOT reopened and Story 6.2's closed record
    # is left standing rather than edited.
    # ⚠️ It dispositions NO ledger entry, and says so with a named owner: the `deferred-work.md`
    # re-homing is DEFERRED to a follow-up commit owned by Story 17.5, because at authoring time
    # that file held a concurrent session's uncommitted `DF-AUD-DETECT-A..F` and staging it by path
    # would have swept unfinished work into this commit.
    # ⚠️ It must be committed TOGETHER with this line — `-22` closes in BOTH directions, so the
    # document without this entry and this entry without the document red `master` equally.
    "sprint-change-proposal-2026-08-24.md",
    # Registered 2026-08-25 for the Epic-18 retrospective — `AI-E12-1`'s second half ("make the
    # registration part of the retrospective step's own DoD") on its SIXTH consecutive retrospective,
    # after the Epic-13 INTERIM, Epic-14, FINAL Epic-13, Epic-15 and Epic-16 entries above. It is
    # written by the session that wrote the document, which is the form `AI-E16-15` asked to return
    # to: that session was chartered READ-ONLY over `tests/` and correctly refused, filing the
    # omission against itself; this one carries no such charter, so the line lands with the document
    # instead of as a follow-up act by a separately chartered session.
    # Same one-line edit and same verification-before-registration as every entry above, by
    # execution: `_split_sentences()` returns 354 sentences, so `-21` is genuinely reading the
    # document rather than passing over an unparseable one; `_status_assertions()` returns 0 — no
    # phrase in `_STATUS_CLAIMS` occurs in it at all, denied or otherwise — so `-21`'s per-document
    # loop short-circuits and this registration is inert rather than load-bearing; and
    # `_executed_gate_citations()` returns 0, so it mints an excuse for nothing. `-22` was observed
    # RED against this document before this line (`status-asserting document(s) exist but are not
    # registered: ['epic-18-retro-2026-08-25.md']`) and GREEN after, on the live tree, with the full
    # suite re-run green afterwards. ⛔ No `_EXCLUDED_BY_DESIGN` entry was added and not one
    # assertion in `-22` was weakened, reworded or exempted.
    # WHAT THE DOCUMENT ASSERTS, so the registration is judged against its contents: Epic 18's four
    # stories are `done` and it closes `DF-AUD-DETECT-A`, `-B`, `-E` and `-F`; `-C` and `-D` stay
    # OPEN and it dispositions NEITHER — §10 RE-DERIVES the ledger against `deferred-work.md` on disk
    # and edits it not at all. It changes NO release status of any kind: cross-platform verification,
    # deployment and release are all recorded as NOT ESTABLISHED, the >=80% precision gate is
    # UNCHANGED and not cleared, the precision figure STILL DOES NOT EXIST, nothing is ratified and
    # the protocol is not re-versioned. `DF-13-5-A` stays OPEN and UNSPENT — declined a second time
    # on 2026-08-24, its trigger now conditioned on shipped promotions rising above zero — and this
    # document explicitly does NOT spend it. It amends no FR, no threshold, no epic container and no
    # planning document: its Epic-17 finding (the narrowed `Detector` Protocol and the four
    # conformance pins that landed after Epic 17's plan was written) is filed as a RECOMMENDATION to
    # the orchestrator and the operator, and `epics.md` is not touched.
    # ⚠️ The only `development_status` value its session wrote is `epic-18-retrospective` -> `done`;
    # the `epic-18` roll-up is the orchestrator's and was left `in-progress`.
    # ⚠️ It must be committed TOGETHER with this line — `-22` closes in BOTH directions, so the
    # document without this entry and this entry without the document red `master` equally.
    "epic-18-retro-2026-08-25.md",
    # Registered 2026-08-26 for the Epic-17 retrospective — `AI-E12-1`'s second half ("make the
    # registration part of the retrospective step's own DoD") on its SEVENTH consecutive
    # retrospective, after the Epic-13 INTERIM, Epic-14, FINAL Epic-13, Epic-15, Epic-16 and Epic-18
    # entries above. Written by the session that wrote the document, which is the form `AI-E16-15`
    # asked to return to; this session carries no read-only-over-`tests/` charter, so the line lands
    # with the document instead of as a follow-up act by a separately chartered session.
    # Same one-line edit and same verification-before-registration as every entry above, by
    # execution: `_split_sentences()` returns 401 sentences, so `-21` is genuinely reading the
    # document rather than passing over an unparseable one; `_status_assertions()` returns 0 — no
    # phrase in `_STATUS_CLAIMS` occurs in it at all, denied or otherwise — so `-21`'s per-document
    # loop short-circuits and this registration is inert rather than load-bearing; and
    # `_executed_gate_citations()` returns 0, so it mints an excuse for nothing. `-22` was observed
    # RED against this document before this line (`status-asserting document(s) exist but are not
    # registered: ['epic-17-retro-2026-08-26.md']`) and GREEN after, on the live tree. ⛔ No
    # `_EXCLUDED_BY_DESIGN` entry was added and not one assertion in `-22` was weakened, reworded
    # or exempted.
    # WHAT THE DOCUMENT ASSERTS, so the registration is judged against its contents: Epic 17's five
    # stories are `done`, and the pre-registered precision criterion was called ONCE and returned
    # ⛔ `UNEVALUABLE` — sealed contributing members 0 against a resolved floor of 3,
    # `measured_precision` null, 1,032 walked / 0 skipped, 85 `S1`-eligible across 3 contributing
    # members. The population and breadth floors CLEARED; only the sealed arm failed. ⛔ NO successor
    # predicate was promoted: `S1` is ADVISORY, `argus/detectors/vacuous_test.py:796` is
    # byte-unchanged and no finding's `verdict_eligible` moved. It changes NO release status of any
    # kind: cross-platform verification, deployment and release are all recorded as NOT ESTABLISHED,
    # the precision gate is UNCHANGED and not cleared, the externalization gate stays `BLOCKED`,
    # `protocol_cleared` stays `False`, nothing is ratified, nothing was fetched and the protocol is
    # not re-versioned. `DF-13-5-A` stays OPEN and UNSPENT — its 2026-08-24 trigger was evaluated by
    # Story 17.4's measurement and condition 1 did NOT fire (0 shipped promotions of 1,032). It
    # dispositions NO ledger entry and `deferred-work.md` is absent from its write set: the two
    # Epic-17 dispositions (`DF-INV-VACUOUS-B`, `DF-AUD-DETECT-D`) were made by Stories 17.2 and
    # 17.3, and §10 RE-DERIVES the ledger against the file on disk without editing it. It amends no
    # FR, no threshold, no epic container and no planning document: its findings — chiefly that
    # sealing ratified members AND filling `AI-E16-7` are BOTH blocking prerequisites for any
    # evaluable successor measurement — are filed as RECOMMENDATIONS to the orchestrator and the
    # operator, and `epics.md`/`architecture.md`/the PRD are not touched.
    # ⚠️ The only `development_status` value its session wrote is `epic-17-retrospective` -> `done`;
    # the `epic-17` roll-up is the orchestrator's and was left `in-progress`. The thirteen Epic-17
    # action items `AI-E17-1`..`AI-E17-13` WERE appended to `action_items:` in the house form, after
    # the operator widened that session's write scope. ⛔ An earlier revision of THIS comment, of the
    # document's section 12 and of `sprint-status.yaml`'s `last_updated` recorded them as WITHHELD;
    # all three are reconciled and that claim no longer stands anywhere. The append is PURE and was
    # verified after the write: 116 lines at end of file, `git diff` +118/-2 (the two being the
    # `last_updated` and `epic-17-retrospective` lines), NOT ONE existing `action`/`owner`/
    # `destination`/`priority`/`status` field edited, every comment and the STATUS DEFINITIONS block
    # intact, YAML re-parsed clean at 112 `action_items` entries and 122 `development_status` keys,
    # and the CRLF invariant re-verified at 1,380 lines / 1,380 CR / 1,380 CRLF / 0 lone CR / 0 lone
    # LF. ⚠️ Section 5.1's Epic-18 follow-through verdicts are still recorded in the document ONLY
    # — no existing status field was edited, on `AI-E12-3`'s rule that a worker does not dispose of
    # governance.
    # ⚠️ It must be committed TOGETHER with this line — `-22` closes in BOTH directions, so the
    # document without this entry and this entry without the document red `master` equally.
    "epic-17-retro-2026-08-26.md",
    # Registered 2026-08-26 by the `bmad-correct-course` session that wrote it — the registration is
    # part of writing the document, not a later cleanup (`AI-E12-1`'s second half). This is the
    # THIRD `bmad-correct-course` registration written by its authoring session, after the
    # 2026-08-22 and 2026-08-24 entries above, and this session carries no read-only-over-`tests/`
    # charter, so the line lands in the same commit as the document.
    # Same verification-before-registration as every entry above, by execution: `_split_sentences()`
    # returns 151 sentences, so `-21` is genuinely reading the document rather than passing over an
    # unparseable one; `_status_assertions()` returns 0 — no phrase in `_STATUS_CLAIMS` occurs in it
    # at all, denied or otherwise — so `-21`'s per-document loop short-circuits and this
    # registration is inert rather than load-bearing; and `_executed_gate_citations()` returns 0, so
    # it mints an excuse for nothing. `-22` was observed RED against this document before this line
    # (`status-asserting document(s) exist but are not registered:
    # ['sprint-change-proposal-2026-08-26.md']`) and GREEN after, on the live tree. ⛔ No
    # `_EXCLUDED_BY_DESIGN` entry was added and not one assertion in `-22` was weakened, reworded or
    # exempted.
    # WHAT THE DOCUMENT ASSERTS, so the registration is judged against its contents: it CREATES one
    # epic container (19) and six story keys, of which TWO are filed `operator-act` rather than
    # `backlog` because a §6 R2 ratification and a §4 adjudication are not autonomous acts. It
    # changes NO release status of any kind: the >=80% externalization gate is UNCHANGED, still
    # `BLOCKED` and still NOT CLEARED; `protocol_cleared` stays `False`; the precision figure STILL
    # DOES NOT EXIST; `eligible_member_count()` is 5, all 14 bench candidates remain
    # `eligible_for_n=False` and the sealed-vs-ratified intersection it measures is EMPTY; nothing
    # is ratified, no third-party source is fetched and the protocol is not re-versioned. It amends
    # no FR and no threshold, and it reopens no delivered epic — Epics 1–18 stand.
    # ⚠️ `DF-13-5-A` stays OPEN and UNSPENT, and the document REFUSES to decide by implication
    # whether ratifying already-manifested sealed members would spend it: §3.4 puts that to the
    # operator as a dated ruling owed BEFORE Story 19.2, rather than answering it here.
    # ⚠️ It dispositions NO ledger entry. `deferred-work.md` is absent from its write set; the 46
    # stale `target_story` pointers it measures are carried to Story 19.6, not re-homed here, and
    # `_POINTS_AT_DONE_AT_LANDING` is byte-unchanged by it.
    # ⚠️ Its §3.2 finding is a PROTOCOL-FORM finding and is recorded as a recommendation, not taken:
    # filling §2's External adjudicator is a holder-cell change (a dated block, no change-log row),
    # whereas pre-recording a stuck-pair rule would be a §4 METHOD change requiring V1.4 and would
    # re-stamp `protocol_version` across the 31 committed judgements of 2026-08-17.
    # ⚠️ It must be committed TOGETHER with this line — `-22` closes in BOTH directions, so the
    # document without this entry and this entry without the document red `master` equally.
    "sprint-change-proposal-2026-08-26.md",
)

# Exactly the set the epic's AC names — "any future change proposal or retrospective".
_STATUS_DOCUMENT_PATTERNS: tuple[str, ...] = (
    "sprint-change-proposal-*.md",
    "epic-*-retro-*.md",
)

# Exclusions are BY NAME WITH A REASON, never by silence (the `_PRESERVED_RECORD` precedent in
# tests/test_release_surface_honesty.py:89-96). `-22` asserts every entry carries a reason, so an
# exclusion cannot be added as a bare path by someone trying to make this guard quiet.
_EXCLUDED_BY_DESIGN: dict[str, str] = {
    "stories/": (
        "Story files record TEST-RUN evidence for one unit of work, not a release status for "
        "the project; a story's status lives in sprint-status.yaml, which is the tracker. "
        "Excluded deliberately (story 10.1, DN-5) rather than omitted silently. They do not "
        "match the patterns above either, and this entry states WHY that is correct."
    ),
    "prd.md / architecture.md / epics.md / deferred-work.md": (
        "Specification and ledger documents, not status records. They describe what the system "
        "must do and what is deferred; where they mention a release status they are quoting or "
        "governing one. architecture.md is instead asserted POSITIVELY by -23, which requires "
        "the rule prose to be present, so the (a)-half of AC2 cannot be silently deleted."
    ),
    # Added 2026-08-15 by Story 12.9 / AC2, closing a MEASURED hole rather than describing a
    # decision: README.md, CHANGELOG.md, .github/workflows/release.yml and the GitHub Release
    # notes were never excluded from this rule with a reason — they were simply OUTSIDE it,
    # because `_STATUS_DOCUMENTS` above is change-proposals and retrospectives only. The
    # release note is the single most read status-asserting document this project will ever
    # publish and nothing checked it. They are no longer outside: `-24` scans every registered
    # release surface with this file's own derivation, and `-25` pins the derived statement.
    "README.md / CHANGELOG.md / release.yml / the release-note body": (
        "NOT excluded — moved INSIDE the rule by Story 12.9. They are governed by -24 and -25 "
        "over the `_RELEASE_SURFACES` registry imported above rather than by `_STATUS_DOCUMENTS`, "
        "because they are consumer surfaces rather than planning records and they are enumerated "
        "and closed by `TC-ArgusAgent-DOCS-001-18` in the file that owns them. This entry exists "
        "so a reader of this table finds where the rule reaches them instead of concluding they "
        "escaped it."
    ),
}


def _registered_paths() -> list[Path]:
    return [_ARTIFACT_DIR / name for name in _STATUS_DOCUMENTS]


def test_TC_ArgusAgent_DOCS_001_21_every_status_claim_cites_an_executed_gate() -> None:
    """TC-ArgusAgent-DOCS-001-21 — Story 10.1/AC2b: the rule, enforced over the registered set.

    For every registered status document: a live release-status claim is allowed only if the
    document cites an executed gate (a run id together with the sha it covers) or the claim's own
    sentence records the status as NOT ESTABLISHED.

    Non-vacuity is asserted directly. A registry of unreadable or empty files would satisfy every
    assertion below without reading a word, so each document must exist, be non-empty and parse to
    real sentences before the scan is allowed to mean anything.
    """
    assert _STATUS_DOCUMENTS, "the status-document registry is empty — the guard scans nothing"

    for path in _registered_paths():
        rel = path.relative_to(_REPO_ROOT).as_posix()
        assert path.is_file(), f"registered status document is missing: {rel}"

        text = path.read_text(encoding="utf-8")
        sentences = _split_sentences(text)
        assert len(sentences) > 10, (
            f"{rel} parsed to {len(sentences)} sentences — the document is empty or the sentence "
            "splitter is broken, and either way this guard is not reading it."
        )

        assertions = _status_assertions(text)
        if not assertions:
            continue

        citations = _executed_gate_citations(text)
        for claim, sentence in assertions:
            if _NOT_ESTABLISHED_MARKER in sentence:
                continue
            assert citations, (
                f"{rel} ASSERTS a release status without citing an executed gate.\n"
                f"  claim   : {claim!r}\n"
                f"  sentence: {sentence[:300]!r}\n"
                "  fix     : cite the audit-ci.yml run that covers this tree, as "
                "'run <id> (<sha>, N/N legs)', or record the status as NOT ESTABLISHED. "
                "A local pytest/mypy/bandit run is necessary but NOT sufficient "
                "(architecture.md §H, DF-AUD-APAA-C)."
            )


def test_TC_ArgusAgent_DOCS_001_22_the_status_document_set_is_closed() -> None:
    """TC-ArgusAgent-DOCS-001-22 — Story 10.1/AC3.2+3.3: a new proposal cannot escape by being new.

    The failure shape is always the same and this project has shipped it five times in one epic
    (AI-E8-6): the guard names the files that existed when it was written, and the next file added
    is outside it. The globs are resolved against the tree and anything unregistered fails.

    A pattern that matches nothing passes every assertion inside it, so non-vacuity is asserted
    twice: the globs must resolve to a non-empty set, and every registered name must be found by
    them (a registry entry the globs cannot see is dead weight that proves nothing).
    """
    found: set[str] = set()
    for pattern in _STATUS_DOCUMENT_PATTERNS:
        for path in _ARTIFACT_DIR.glob(pattern):
            if path.is_file():
                found.add(path.name)

    assert found, (
        f"the status-document patterns {_STATUS_DOCUMENT_PATTERNS} resolved to NOTHING under "
        f"{_ARTIFACT_DIR} — the globs are broken and every other assertion in this file is vacuous"
    )

    unregistered = sorted(found - set(_STATUS_DOCUMENTS))
    assert not unregistered, (
        f"status-asserting document(s) exist but are not registered: {unregistered}. Add them to "
        "_STATUS_DOCUMENTS so the citation rule covers them — a change proposal or retrospective "
        "is exactly the kind of document that states a release status."
    )

    missing = sorted(set(_STATUS_DOCUMENTS) - found)
    assert not missing, (
        f"registered document(s) are no longer found by the globs: {missing}. Either they were "
        "deleted (§3.4: records are superseded, never erased) or the patterns drifted."
    )

    # Exclusions are decisions, not silence: each one carries a written reason.
    assert _EXCLUDED_BY_DESIGN, "the exclusion table is empty — record exclusions, do not omit"
    for excluded, reason in _EXCLUDED_BY_DESIGN.items():
        assert len(reason.split()) >= 12, (
            f"exclusion {excluded!r} has no substantive reason recorded. An exclusion without a "
            "reason is an oversight wearing a decision's clothes (_PRESERVED_RECORD precedent)."
        )

    # The story-file exclusion is real: story files must not be reachable by the patterns.
    stories = _ARTIFACT_DIR / "stories"
    if stories.is_dir():
        assert not (found & {p.name for p in stories.glob("*.md")}), (
            "a story file was matched by the status-document patterns; stories are excluded by "
            f"design — {_EXCLUDED_BY_DESIGN['stories/']}"
        )
