"""Story 18.1 / DF-AUD-DETECT-A — the sentinel table matches VALUES, not substrings of them.

Verification area ArgusAgent-SECRET (``TC-ArgusAgent-SECRET-001-23``..``-27``, CONTINUING the index
whose prior maximum is ``-22``; nothing is renumbered).

**The defect under repair, measured on 2026-08-24 at HEAD ``7a3cc7c``.**
``secret_suppression.py``'s ``is_public_sentinel`` tested ``sentinel in snippet_clean`` over a table
five of whose eight members are shorter than twenty characters (``localhost`` 9, ``127.0.0.1`` 9,
``example.com`` / ``.org`` / ``.net`` 11). The only production caller — ``secret_scan.py``'s
``run()`` — passes ``snippet=match.value``, the EXTRACTED VALUE. So any credential whose value
happened to carry one of those nine-to-eleven-character runs answered ``(True, 'known_sentinel')``
at step 2 and was dropped in silence. Executed on this host, on the NON-TEST path
``argus/prod/settings.py``, each line alone, through the shipped ``SecretScanDetector().run()``::

    DATABASE_URL  = "postgres://admin:Tr0ub4dor3@localhost:5432/prod"   -> 0 findings
    SMTP_PASSWORD = "aBcD1234EfGh5678@example.com"                      -> 0 findings
    DATABASE_URL  = "postgres://admin:Tr0ub4dor3@dbhost:5432/prod"      -> 1 finding   [CONTROL]

The CONTROL is the same value with the sentinel substring removed, and it **is** reported. That is
what makes the first two a security false negative rather than a policy: a real password is lost
because its host is named ``localhost``.

``is_live_production_key`` carried the IDENTICAL short-circuit in its own body, so the Live-Key
Safeguard — the layer Story 10.3 promoted above both operator flags precisely to be the backstop —
**disabled itself on the same string** step 2 had already matched. Enumerated here: of the seven
values that genuinely match a ``LIVE_KEY_PATTERNS`` member AND carry a short sentinel, **7 of 7**
had the safeguard disabled and **7 of 7** were suppressed. That measurement falsifies
``DF-10-3-B``'s claim that *"no live production key can be suppressed by any of these paths except
an explicit inline annotation"* — none of the seven involves a flag or an annotation.

**The repair is LENGTH-GATED, not uniform equality** (``DN-18-1-1``). Sentinels shorter than
``MIN_CONTAINMENT_SENTINEL_LENGTH`` match by exact equality of ``snippet.strip()``; the three
published full-length credentials (39-40 chars) keep containment, because a value that long cannot
be an accidental substring of anything. Uniform equality was executed and rejected: it breaks the
shipped ``test_secret_suppression.py::test_public_sentinel_suppression``, which passes a whole
assignment LINE, and repairing that would have meant editing a shipped test to accommodate a
change. ``-27`` puts both call shapes on the record instead of leaving the ambiguity inherited.

**RED evidence (AI-E14-1).** Every case here was run against the UNFIXED engine before the repair
existed, and again afterwards by restoring the shipped module body. ``-23``, ``-24``, ``-26`` and
``-27`` go RED; ``-25`` stays GREEN **by design** — it is the no-suppression-lost case, and it must
hold before AND after. The raw failure text is in the story's Dev Agent Record. Per the guard-fire
rule this author-driven RED is **vacuity evidence** — proof the cases can fail — not "these guards
caught a defect".

**Every case runs on the NON-TEST path** ``argus/prod/settings.py`` (§2.3): a case built on a
``tests/**`` path would be suppressed by step 5's ``DEFAULT_TEST_PATH_PATTERNS`` for an entirely
different reason and would assert nothing. That path is never opened — ``run()`` is pure and uses
``file_path`` only for glob matching and locators — and it does not exist on disk.

**Key material here is synthetic and built in this module**, never planted in a committed fixture
file (NFR-S1 / NFR-S2), and every assertion is on a count, a rule id or a ``(bool, reason)`` tuple —
never on a value. Every case asserts its population is non-empty BEFORE asserting anything about it
(AI-E11-1).

Counts are asserted as ``>= 1`` per line, never as an exact total (``DN-18-1-5``): the
``example.com`` line legitimately yields TWO findings because ``run()`` de-duplicates on
``(start_line, end_line, pattern_id)`` and two patterns hit that span. The exact post-repair triple
is 1 / 2 / 1 and is RECORDED in the story; asserting it would redden this module the moment Story
18.3 narrows those very regexes, which is the right reason for a wrong RED.
"""

from __future__ import annotations

from argus.detectors.secret_scan import RULE_HARDCODED_SECRET, SecretScanDetector
from argus.detectors.secret_suppression import (
    CONTAINMENT_PUBLIC_SENTINELS,
    EQUALITY_PUBLIC_SENTINELS,
    KNOWN_PUBLIC_SENTINELS,
    LIVE_KEY_PATTERNS,
    MIN_CONTAINMENT_SENTINEL_LENGTH,
    SecretSuppressionEngine,
)
from argus.index.ast_index import AstIndexEntry
from argus.verdict.verdict_gate import blocking_finding_count

_ENGINE = SecretSuppressionEngine

# A plausible NON-TEST path (§2.3). DEFAULT_TEST_PATH_PATTERNS does not match it, `run()` never
# opens it, and it deliberately does not exist on disk.
_NON_TEST_PATH = "argus/prod/settings.py"

# DF-AUD-DETECT-A's reproduction, verbatim, including the CONTROL. Synthetic passwords, built here.
_AUDIT_LINES: tuple[tuple[str, str], ...] = (
    (
        "localhost",
        'DATABASE_URL  = "postgres://admin:Tr0ub4dor3@localhost:5432/prod"\n',
    ),
    (
        "example.com",
        'SMTP_PASSWORD = "aBcD1234EfGh5678@example.com"\n',
    ),
    (
        "CONTROL",
        'DATABASE_URL  = "postgres://admin:Tr0ub4dor3@dbhost:5432/prod"\n',
    ),
)


def _entry(file_path: str) -> AstIndexEntry:
    """The tests/test_secret_scan.py::_entry precedent — no tree-sitter, a pure 1.4 entry."""
    return AstIndexEntry(file_path=file_path, ast_eligible=True, definitions=(), edges=())


def _hardcoded_secret_findings(source: str, *, file_path: str = _NON_TEST_PATH):
    """Every ``hardcoded_secret`` finding the shipped detector reports for *source*."""
    result = SecretScanDetector().run(
        file_path=file_path, source=source, ast_entry=_entry(file_path)
    )
    return [f for f in result.findings if f.rule_id == RULE_HARDCODED_SECRET]


def _live_key_short_sentinel_cells() -> tuple[tuple[str, str, str], ...]:
    """The enumerated space: every (live-key family, short sentinel) pair that is CONSTRUCTIBLE.

    Trap E.2 — enumerate the space, not one sample. A cell exists only where the family's own
    regex can actually accept the sentinel's characters, and every cell is verified against
    ``LIVE_KEY_PATTERNS`` before it is returned, so this can never quietly become a list of
    values that are not live keys at all:

    * ``AKIA[0-9A-Z]{16}`` is upper-case-and-digits and can carry NONE of the five.
    * ``ghp_[A-Za-z0-9_]{36}`` can carry ``localhost`` but not a dotted sentinel.
    * ``xox[baprs]-...-[a-zA-Z0-9]{24,32}`` likewise.
    * the PEM header is a ``search``, so ANY sentinel anywhere in the snippet reaches it.
    """
    cells: list[tuple[str, str, str]] = []
    for sentinel in EQUALITY_PUBLIC_SENTINELS:
        if sentinel.isalnum() and len(sentinel) <= 36:
            cells.append(("github_pat", sentinel, "ghp_" + (sentinel + "0" * 36)[:36]))
    for sentinel in EQUALITY_PUBLIC_SENTINELS:
        cells.append(
            (
                "private_key_pem",
                sentinel,
                "-----BEGIN RSA PRIVATE KEY-----" + sentinel,
            )
        )
    for sentinel in EQUALITY_PUBLIC_SENTINELS:
        if sentinel.isalnum():
            cells.append(
                (
                    "slack_bot_token",
                    sentinel,
                    "xoxb-1234567890-1234567890-" + (sentinel + "a" * 24)[:24],
                )
            )
    verified = tuple(
        cell
        for cell in cells
        if any(pattern.search(cell[2]) for pattern in LIVE_KEY_PATTERNS)
    )
    assert len(verified) == len(cells), (
        "a constructed cell does not match any LIVE_KEY_PATTERNS member — the enumeration is "
        "building values that are not live keys, so it would assert nothing"
    )
    return verified


# ── AC3 — the audit's reproduction, committed ───────────────────────────────


def test_TC_ArgusAgent_SECRET_001_23_audit_reproduction_lines_are_reported() -> None:
    """TC-ArgusAgent-SECRET-001-23 — DF-AUD-DETECT-A's three lines each report, control included."""
    assert _AUDIT_LINES, "the reproduction population is empty — this case would assert nothing"

    for label, source in _AUDIT_LINES:
        findings = _hardcoded_secret_findings(source)
        assert len(findings) >= 1, (
            f"the {label} line reports no hardcoded_secret: a credential is being dropped "
            f"because its value carries a public-sentinel SUBSTRING (DF-AUD-DETECT-A)"
        )
        for finding in findings:
            assert finding.locators, "a hardcoded_secret finding carries no locator"
            assert finding.locators[0].start_line == 1

    # AC4.2 / §2.7 — the recovered findings are advisory by construction and can never block a
    # release on their own. Proven against the gate, not asserted in prose.
    for _label, source in _AUDIT_LINES:
        findings = _hardcoded_secret_findings(source)
        assert blocking_finding_count(findings) == 0, (
            "a recovered hardcoded_secret finding is VERDICT-ELIGIBLE — this story moves "
            "under-reporting to correct, it does not move a verdict"
        )


def test_TC_ArgusAgent_SECRET_001_24_sentinel_tables_hold_their_length_invariant() -> None:
    """TC-ArgusAgent-SECRET-001-24 — a short sentinel cannot be added to the containment table."""
    assert CONTAINMENT_PUBLIC_SENTINELS, "the containment table is empty"
    assert EQUALITY_PUBLIC_SENTINELS, "the equality table is empty"

    for sentinel in CONTAINMENT_PUBLIC_SENTINELS:
        assert len(sentinel) >= MIN_CONTAINMENT_SENTINEL_LENGTH, (
            "a sentinel shorter than MIN_CONTAINMENT_SENTINEL_LENGTH is matched by CONTAINMENT: "
            "that is exactly DF-AUD-DETECT-A, reopened by a table edit"
        )
    for sentinel in EQUALITY_PUBLIC_SENTINELS:
        assert len(sentinel) < MIN_CONTAINMENT_SENTINEL_LENGTH, (
            "a full-length published credential is matched by EQUALITY only, so it would stop "
            "being recognised inside a larger line"
        )

    assert not set(CONTAINMENT_PUBLIC_SENTINELS) & set(EQUALITY_PUBLIC_SENTINELS), (
        "the two tables overlap — one value would be matched by two semantics (AR7)"
    )
    assert (
        tuple(CONTAINMENT_PUBLIC_SENTINELS) + tuple(EQUALITY_PUBLIC_SENTINELS)
        == KNOWN_PUBLIC_SENTINELS
    ), (
        "KNOWN_PUBLIC_SENTINELS is no longer the order-preserving union of the two tables: the "
        "public module-level contract has drifted (NFR-M2, additive-only)"
    )
    assert len(KNOWN_PUBLIC_SENTINELS) == 8, (
        "the sentinel table was widened or narrowed — that is AC8, an escalation, not a fix"
    )


def test_TC_ArgusAgent_SECRET_001_25_no_public_sentinel_suppression_is_lost() -> None:
    """TC-ArgusAgent-SECRET-001-25 — all eight members alone still suppress; long ones still embed."""
    assert KNOWN_PUBLIC_SENTINELS, "the sentinel table is empty"

    for sentinel in KNOWN_PUBLIC_SENTINELS:
        assert _ENGINE.evaluate_suppression(
            file_path=_NON_TEST_PATH, snippet=sentinel
        ) == (True, "known_sentinel"), (
            f"a published non-secret sentinel is no longer suppressed when passed alone — the "
            f"repair lost a suppression instead of narrowing one (AC1.4)"
        )

    assert CONTAINMENT_PUBLIC_SENTINELS, "the containment table is empty"
    for sentinel in CONTAINMENT_PUBLIC_SENTINELS:
        line = f'MOCK_KEY = "{sentinel}"'
        assert _ENGINE.evaluate_suppression(file_path=_NON_TEST_PATH, snippet=line) == (
            True,
            "known_sentinel",
        ), (
            "a published full-length credential embedded in a larger snippet is answered below "
            "step 2, so removing the Live-Key Safeguard's short-circuit would start reporting a "
            "documented non-secret (AC2.4)"
        )


def test_TC_ArgusAgent_SECRET_001_26_live_key_safeguard_no_longer_disables_itself() -> None:
    """TC-ArgusAgent-SECRET-001-26 — the enumerated live-key x short-sentinel space, all reported."""
    cells = _live_key_short_sentinel_cells()
    assert cells, "the live-key x short-sentinel enumeration is empty — nothing would be asserted"

    for family, sentinel, value in cells:
        assert _ENGINE.is_live_production_key(value) is True, (
            f"the Live-Key Safeguard DISABLES ITSELF for a {family} value carrying "
            f"'{sentinel}': the backstop does not merely get bypassed, it declines to fire"
        )
        assert _ENGINE.evaluate_suppression(
            file_path=_NON_TEST_PATH, snippet=value
        ) == (False, None), (
            f"a live {family} credential carrying '{sentinel}' is SUPPRESSED — DF-10-3-B's "
            f"safety claim, falsified, with no flag and no inline annotation in sight"
        )

    # End to end, through the shipped run(), on a non-test path: the safeguard's own families.
    for _family, _sentinel, value in cells:
        source = f'API_TOKEN = "{value}"\n'
        assert len(_hardcoded_secret_findings(source)) >= 1, (
            "a live production key is dropped end-to-end by the sentinel short-circuit"
        )


def test_TC_ArgusAgent_SECRET_001_27_both_call_shapes_of_is_public_sentinel_are_pinned() -> None:
    """TC-ArgusAgent-SECRET-001-27 — the VALUE-shaped call and the LINE-shaped call, on the record."""
    assert EQUALITY_PUBLIC_SENTINELS, "the equality table is empty"
    assert CONTAINMENT_PUBLIC_SENTINELS, "the containment table is empty"

    # (a) The VALUE shape — what secret_scan.py's run() actually passes. A short sentinel is the
    #     whole value: suppressed. A short sentinel merely INSIDE a larger value: reported.
    for sentinel in EQUALITY_PUBLIC_SENTINELS:
        assert _ENGINE.is_public_sentinel(sentinel) is True, (
            "the value IS the published sentinel and is no longer recognised (AC1.4)"
        )
        assert _ENGINE.is_public_sentinel(f"postgres://admin:Tr0ub4dor3@{sentinel}:5432/prod") is False, (
            "a short sentinel still matches as a SUBSTRING of a larger value — DF-AUD-DETECT-A"
        )
        assert _ENGINE.is_public_sentinel(f"  {sentinel}  ") is True, (
            "surrounding whitespace defeats the equality match; the shipped body strips first "
            "and that behaviour is unchanged"
        )

    # (b) The LINE shape — what tests/test_secret_suppression.py::test_public_sentinel_suppression
    #     passes, and what the production caller never passes. A full-length published credential
    #     inside a whole assignment line stays suppressed: 39-40 characters cannot be accidental.
    for sentinel in CONTAINMENT_PUBLIC_SENTINELS:
        assert _ENGINE.is_public_sentinel(f'MOCK_KEY = "{sentinel}"') is True, (
            "the line-shaped call lost the containment semantics the shipped suite asserts — "
            "uniform equality is DN-18-1-1's REJECTED alternative"
        )
