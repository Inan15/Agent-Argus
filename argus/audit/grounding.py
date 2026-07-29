"""PURE FR7 deep-claim AST-grounding validator — the stack-agnostic claim→validated? interface.

Drivers: ArgusAgent-FR-7 (validate a deep claim against source STRUCTURE — Python AST
in V1 — and downgrade an unverifiable claim to ``audited_shallow``), ArgusAgent-FR-6
(the EXISTING claim-required ``audited_deep`` / silence→shallow keystone, composed
not forked), ArgusAgent-NFR-P2 (the stack-agnostic ``claim → validated?`` interface;
Python is implementation #1; a non-Python / AST-ineligible / parse-failed file
routes to the ``claim_emitted`` proxy; V2 multi-language is purely additive behind
the SAME interface), ArgusAgent-AR10 / NFR-R1 (a malformed / empty / None / parse-failed
entry → a typed boolean answer, NEVER an uncaught raise — NAMED handling, no bare
``except``), ArgusAgent-AR8 (PURE — no I/O, no clock, no LLM, no provider import, no
float), ArgusAgent-NFR-D1/D2 (deterministic, zero-LLM-token — the V1 grounding fact is a
structural count over the pre-built 1.4 AST entry), ArgusAgent-AR7 / §3.3 (REUSE the 1.4
``definitions`` BY IMPORT — no re-parse, no second tree-sitter / ``ast`` / ``radon``
call), ArgusAgent-NFR-S1 (the answer is a count over already-redacted AST metadata — no
source / secret byte), ArgusAgent-NFR-M1 (≤1200-line files).

Verification area ArgusAgent-AUDIT (TC-ArgusAgent-AUDIT-001-46..).

Why this module exists (closes DF-1-7-B — the interim Python deep over-grading)
-------------------------------------------------------------------------------
Story 1.7 (and the pipeline since Epic 1) graded EVERY cleanly-parsed non-test
Python file ``audited_deep`` purely on claim-PRESENCE (``grade_entry(
proposed_depth=AUDITED_DEEP, claim_present=True)`` — the FR6 proxy). That
over-graded a file as deep merely because it parsed, not because its claim was
verified — the long-carried 🟡 DF-1-7-B. This module is the FR7 GROUNDING gate
the pipeline now consults: it computes a pure ``claim_grounded: bool`` over a
non-test file's pre-built 1.4 ``AstIndexEntry`` so the pipeline can grade
``audited_deep`` ONLY when grounded (passing ``claim_present=(claim_emitted AND
claim_grounded)`` into the UNCHANGED ``grade_entry`` — DN-GROUNDED, the ledger
stays byte-identical).

The V1 grounding rule (DN-GROUND-RULE) — and its HONEST limitation
------------------------------------------------------------------
A non-test Python file's deep claim is GROUNDED iff its AST entry exhibits **≥1
real ``Definition``** (a ``function`` / ``class`` the audit could ground a deep
claim against). A clean-parsed module with ZERO definitions (a pure-constants /
re-export / ``__all__``-only / docstring-only / dunder-glue module) has nothing
for a deep read to substantively examine → its deep claim is UNGROUNDED →
``audited_shallow``.

This is the *credible, conservative* bar the FR7-split first-principles demands
(architecture §141-151, CC #6 advisory-by-contract): it does NOT over-downgrade
(a real module with real defs stays deep — not cry-wolf) and it does NOT attempt
to prove a SPECIFIC claim's truth. **What it grounds is the STRUCTURE the claim is
*about*, not the truth of a specific claim** — that richer grounding rides the 6.1
LLM port + the 6.4 Prosecutor (DN-V1-DETERMINISTIC). This is the SAME honesty
register the 1.5 vacuous-path subset uses ("what it can and cannot prove").

The stack-agnostic interface (NFR-P2 — Python = impl #1)
--------------------------------------------------------
``is_deep_claim_grounded`` is the ``claim → validated?`` interface. The
``ast_eligible`` flag (1.4) is the impl-selection seam: a cleanly-parsed Python
file (``ast_eligible=True``, ``parse_failed=False``) routes to the REAL Python
AST-grounding impl (#1, the ≥1-definition fact); a non-Python file / an
AST-ineligible / parse-failed Python file routes to the ``claim_emitted`` PROXY
(``False`` here — no grounding attempted, presence governs at the call site). A
future language impl is a second branch behind the SAME interface — no
re-architecture, no new flag.
"""

from __future__ import annotations

from argus.index.ast_index import AstIndexEntry

__all__ = ["is_deep_claim_grounded"]


def is_deep_claim_grounded(entry: AstIndexEntry | None) -> bool:
    """Decide whether a non-test file's deep claim is AST-grounded (FR7, PURE).

    Returns ``True`` iff *entry* is a cleanly-parsed Python file (``ast_eligible``
    and not ``parse_failed``) that exhibits the V1 grounding fact — **≥1 real
    ``Definition``** (DN-GROUND-RULE). Everything else returns ``False``: a
    clean-parse-but-zero-definitions module (the DF-1-7-B downgrade), a
    parse-failed / AST-ineligible Python file, a non-Python file (the
    ``claim_emitted`` proxy — presence governs at the call site, not grounding),
    or a malformed / ``None`` / wrong-shaped entry (AR10 — a degraded input is a
    typed ``False``, never an uncaught raise; NAMED handling, no bare ``except``).

    PURE: no I/O, no clock, no LLM, no provider import, no float. It consumes the
    PRE-BUILT ``entry.definitions`` (the 1.4 substrate the 1.5 subset reads for
    test files) — it does NOT re-parse, add a second tree-sitter call, or import
    ``ast`` / ``radon`` (AR7 / §3.3).
    """
    if not isinstance(entry, AstIndexEntry):
        return False
    if entry.parse_failed or not entry.ast_eligible:
        return False
    return len(entry.definitions) >= 1
