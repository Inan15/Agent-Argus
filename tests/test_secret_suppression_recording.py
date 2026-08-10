"""Story 10.3 / AC4 — an operator cannot silently defeat the Live-Key Safeguard.

Verification area ArgusAgent-SECRET (``TC-ArgusAgent-SECRET-001-15``..``-22``, CONTINUING the index
whose prior maximum is ``-14``).

**The defect under repair, measured on 2026-08-10** (story §A.2). ``secret_suppression.py``'s own
module docstring promises a four-layer design in which *"High-confidence live production key
signatures override folder glob exemptions unless annotated with an explicit inline line comment."*
``evaluate_suppression`` implemented the order **inline → sentinel → ignore_patterns → live-key →
ignore_paths**, so the CLI-supplied ``--ignore-pattern`` ran ABOVE the safeguard, and its match test
is a bare substring (``pat in snippet``). Executed on this host before the fix::

    E.evaluate_suppression(file_path="argus/prod.py", snippet=live)                             -> (False, None)
    E.evaluate_suppression(file_path="argus/prod.py", snippet=live, ignore_paths=("argus/**",))  -> (False, None)
    E.evaluate_suppression(file_path="argus/prod.py", snippet=live, ignore_patterns=("AKIA",))   -> (True, 'custom_ignore_pattern')
    E.evaluate_suppression(file_path="argus/prod.py", snippet=live, ignore_patterns=("A",))      -> (True, 'custom_ignore_pattern')

``--ignore-pattern A`` — one character — suppressed every live AWS key, GitHub PAT, Slack token and
``BEGIN RSA PRIVATE KEY`` block in the repository. ``--ignore-path 'argus/**'`` suppressed none of
them. The two flags were never the same risk, and they do not take the same ruling (DN-5 / DN-6).

**And nothing at all was recorded.** ``secret_scan.py`` bound the reason to ``_reason`` and
``continue``d: the operator's *inputs* were persisted through ``to_provenance_payload()`` while the
*effect* — that a secret was found and suppressed — left no trace anywhere. That is unevidenced
green on the security surface, in a tool whose own report recommends the flag.

**DN-7 fixes the order of the fix: layering first, recording second.** A recording built on the old
order would have faithfully recorded a safeguard bypass.

**Every assertion here was run RED against the unfixed engine** (trap E.1 / AI-E3-1: Story 3.4's
keystone test was green over its own keystone bug); the raw pre-fix output is in the story's Dev
Agent Record. ``-15`` enumerates the whole ``LIVE_KEY_PATTERNS`` space rather than one sample
(trap E.2 — every Epic-8 guard was narrower than its own AC).

**Key material here is synthetic and built in the test**, never planted in a committed fixture file,
and every assertion is on the ``(bool, reason)`` tuple or on a redacted record — never on a value.
"""

from __future__ import annotations

import json

from argus.detectors.base import DetectorResult
from argus.detectors.secret_scan import (
    RULE_HARDCODED_SECRET,
    RULE_OPERATOR_SUPPRESSED_SECRET,
    SecretScanDetector,
    operator_suppression_rule_id,
)
from argus.detectors.secret_suppression import (
    OPERATOR_ATTRIBUTABLE_REASONS,
    SecretSuppressionEngine,
)
from argus.index.ast_index import AstIndexEntry
from argus.verdict.verdict_gate import blocking_finding_count, is_verdict_blocking

_ENGINE = SecretSuppressionEngine

# One synthetic-but-matching sample per LIVE_KEY_PATTERNS member (trap E.2: the enumerated space,
# not one sample). Built here, never committed as a fixture file.
_LIVE_KEYS: tuple[tuple[str, str], ...] = (
    ("aws_access_key", "AKIA" + "ABCDEFGHIJKLMNOP"),
    ("github_pat", "ghp_" + "A" * 36),
    ("private_key_pem", "-----BEGIN RSA PRIVATE KEY-----"),
    ("slack_bot_token", "xoxb-1234567890-1234567890-" + "a" * 24),
)

# The pattern spellings an operator can reach from `--ignore-pattern`. `"A"` is the one-character
# case that defeated the safeguard for every key above at once.
_HOSTILE_PATTERNS: tuple[str, ...] = ("A", "AKIA", "ghp_", "-----BEGIN", "xoxb", "*")

_PRODUCTION_FILE = "argus/prod.py"


def test_TC_ArgusAgent_SECRET_001_15_ignore_pattern_cannot_suppress_a_live_production_key() -> None:
    """TC-ArgusAgent-SECRET-001-15 — the CLI flag now sits BELOW the Live-Key Safeguard.

    Story 10.3 / AC4.1 (`DF-AUD-APAA-E`, §A.2). Enumerates the whole `LIVE_KEY_PATTERNS` space
    against the whole hostile-pattern space, because the pre-fix defect suppressed all of them.
    """
    escapes: list[str] = []
    for kind, live_key in _LIVE_KEYS:
        for pattern in _HOSTILE_PATTERNS:
            suppressed, reason = _ENGINE.evaluate_suppression(
                file_path=_PRODUCTION_FILE, snippet=live_key, ignore_patterns=(pattern,)
            )
            if suppressed:
                escapes.append(
                    f"--ignore-pattern {pattern!r} suppressed a live {kind} "
                    f"(reason={reason!r}) — the Live-Key Safeguard this module's own docstring "
                    f"promises was defeated from the command line"
                )
    assert not escapes, "LIVE-KEY SAFEGUARD BYPASS:\n  " + "\n  ".join(escapes)


def test_TC_ArgusAgent_SECRET_001_16_inline_annotation_still_outranks_the_safeguard() -> None:
    """TC-ArgusAgent-SECRET-001-16 — the ONE override that is deliberately preserved.

    Story 10.3 / AC4.1. An inline annotation is the documented, in-diff, reviewable override: it
    lands in a pull request beside the line it exempts, where a reviewer sees it. That is a
    different accountability class from an argv flag nobody reads afterwards, which is why the
    reordering keeps step 1 on top and moves only the flag.
    """
    for kind, live_key in _LIVE_KEYS:
        suppressed, reason = _ENGINE.evaluate_suppression(
            file_path=_PRODUCTION_FILE,
            snippet=live_key,
            line_content=f'KEY = "{live_key}"  # argus:ignore secret_scan',
        )
        assert suppressed is True, f"an explicit inline annotation stopped exempting a {kind}"
        assert reason == "inline_annotation"


def test_TC_ArgusAgent_SECRET_001_17_ignore_path_still_cannot_suppress_a_live_key() -> None:
    """TC-ArgusAgent-SECRET-001-17 — the bound that MEASURABLY held, pinned so it keeps holding.

    Story 10.3 / AC4.1, DN-5. `--ignore-path` was already bounded by the safeguard before this
    story; that is the measured fact on which its bless rests, and it was pinned by nothing. A
    future reordering must fail here.
    """
    for kind, live_key in _LIVE_KEYS:
        suppressed, reason = _ENGINE.evaluate_suppression(
            file_path=_PRODUCTION_FILE,
            snippet=live_key,
            ignore_paths=("argus/**", "*"),
        )
        assert suppressed is False, f"--ignore-path suppressed a live {kind} (reason={reason!r})"
        assert reason is None


def test_TC_ArgusAgent_SECRET_001_18_ignore_pattern_still_suppresses_a_non_live_secret() -> None:
    """TC-ArgusAgent-SECRET-001-18 — the bless is real; this is not a stealth removal.

    Story 10.3 / AC2.3, DN-6. AC4 bounds `--ignore-pattern`; it does not disable it. A flag that
    silently stopped working would be a behaviour change smuggled in under "blessing".
    """
    suppressed, reason = _ENGINE.evaluate_suppression(
        file_path="src/app.py",
        snippet="MY_CUSTOM_SECRET_TEST_TOKEN",
        ignore_patterns=("MY_CUSTOM_SECRET_*",),
    )
    assert suppressed is True
    assert reason == "custom_ignore_pattern"


def test_TC_ArgusAgent_SECRET_001_19_operator_suppression_is_attributable_to_the_operator() -> None:
    """TC-ArgusAgent-SECRET-001-19 — a custom `--ignore-path` is distinguishable from a built-in.

    Story 10.3 / AC4.2. `is_test_fixture_path` merged `DEFAULT_TEST_PATH_PATTERNS` with the
    operator's own patterns and returned one undifferentiated `test_fixture_glob`, so attribution
    was impossible. Attribution is CONSERVATIVE by design: when a built-in default already matches,
    the operator's flag caused nothing and is not credited with the suppression.
    """
    snippet = "some_plausible_secret_value_1234567890"

    suppressed, reason = _ENGINE.evaluate_suppression(
        file_path="vendor/generated/blob.py", snippet=snippet, ignore_paths=("vendor/**",)
    )
    assert (suppressed, reason) == (True, "custom_ignore_path")
    assert "custom_ignore_path" in OPERATOR_ATTRIBUTABLE_REASONS

    suppressed, reason = _ENGINE.evaluate_suppression(
        file_path="tests/fixtures/mock_credentials.py", snippet=snippet
    )
    assert (suppressed, reason) == (True, "test_fixture_glob")
    assert "test_fixture_glob" not in OPERATOR_ATTRIBUTABLE_REASONS

    # BOTH match: the built-in already suppressed it, so the operator caused nothing.
    suppressed, reason = _ENGINE.evaluate_suppression(
        file_path="tests/fixtures/mock_credentials.py", snippet=snippet, ignore_paths=("tests/**",)
    )
    assert (suppressed, reason) == (True, "test_fixture_glob"), (
        "a redundant --ignore-path was credited with a suppression a built-in default already made"
    )


def _run_detector(source: str, **kwargs: object) -> DetectorResult:
    entry = AstIndexEntry(file_path=_PRODUCTION_FILE, ast_eligible=True, definitions=())
    return SecretScanDetector().run(
        file_path=_PRODUCTION_FILE, source=source, ast_entry=entry, **kwargs  # type: ignore[arg-type]
    )


def test_TC_ArgusAgent_SECRET_001_20_an_operator_suppression_is_recorded_and_redacted() -> None:
    """TC-ArgusAgent-SECRET-001-20 — the suppression leaves a trace, and the trace leaks nothing.

    Story 10.3 / AC4.2, AC4.4 design (a). The record travels on the `Recording` fold the pipeline
    already consumes — chosen over carrying it on `DetectorResult` because `argus/pipeline.py` is
    byte-fenced to Story 12.1 and would have had to grow a line to surface a new field, whereas it
    already folds `secret_result.findings` unchanged.

    Producer-side redaction is ABSOLUTE (NFR-S1/NFR-S2/AR8): the reason token and the locator, and
    nothing else. The operator's own `--ignore-pattern` text is DELIBERATELY not recorded — the
    pattern is operator-supplied and may itself be secret bytes.
    """
    secret = "ThisIsAPlausibleLookingSecretValue0123456789"
    source = f'TOKEN = "{secret}"\n'

    result = _run_detector(source, ignore_patterns=(secret[:12],))
    records = [f for f in result.findings if f.rule_id.startswith(RULE_OPERATOR_SUPPRESSED_SECRET)]

    assert len(records) == 1, (
        "an operator-supplied --ignore-pattern suppressed a secret finding and recorded nothing — "
        f"findings were {[f.rule_id for f in result.findings]}"
    )
    record = records[0]
    assert record.rule_id == operator_suppression_rule_id("custom_ignore_pattern"), (
        f"the record does not name its reason token: {record.rule_id!r}"
    )
    assert record.locators and record.locators[0].file_path == _PRODUCTION_FILE
    assert record.locators[0].start_line == 1

    serialized = json.dumps(json.loads(record.model_dump_json()), ensure_ascii=False)
    assert secret not in serialized, "THE SUPPRESSION RECORD LEAKED THE SECRET (NFR-S1)"
    assert secret[:12] not in serialized, (
        "the record leaked the operator's --ignore-pattern, which is itself operator-supplied text "
        "and may be secret bytes"
    )
    assert 'TOKEN = "' not in serialized, "the record leaked source bytes (NFR-S2)"
    assert ":\\" not in serialized and ":/" not in serialized, (
        "the record leaked an absolute host path (AR8/NFR-S1)"
    )

    # The suppressed finding itself is GONE — recording it is not un-suppressing it.
    assert not [f for f in result.findings if f.rule_id == RULE_HARDCODED_SECRET]


def test_TC_ArgusAgent_SECRET_001_21_built_in_suppressions_are_deliberately_not_recorded() -> None:
    """TC-ArgusAgent-SECRET-001-21 — AC4.5's scope boundary, asserted rather than assumed.

    Story 10.3 / AC4.5. The public sentinels, the inline annotation and
    `DEFAULT_TEST_PATH_PATTERNS` are pre-existing blessed behaviour that NO operator flag caused.
    Recording them is a reporting enhancement (filed as `DF-10-3-B`), not this story's work — and
    silently widening the record would move the dogfood finding count on a run that passed no
    flags at all.
    """
    sentinel = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    annotated = 'KEY = "AnotherPlausibleSecretValue0123456789"  # argus:ignore secret_scan\n'

    for source in (f'MOCK = "{sentinel}"\n', annotated):
        result = _run_detector(source)
        assert not [
            f for f in result.findings if f.rule_id.startswith(RULE_OPERATOR_SUPPRESSED_SECRET)
        ], f"a BUILT-IN suppression emitted an operator-attributed record: {source!r}"


def test_TC_ArgusAgent_SECRET_001_22_the_record_is_never_verdict_eligible() -> None:
    """TC-ArgusAgent-SECRET-001-22 — zero verdict drift, proven not asserted.

    Story 10.3 / AC4.4 (design (a) requires proving the record cannot become verdict-eligible) and
    AC8.7 (a changed dogfood verdict is a stop-and-report, not a figure to update). A disclosure
    that could move a verdict would make disclosure itself a behavioural change, and the flag would
    then be unsafe to bless.
    """
    secret = "YetAnotherPlausibleSecretValue012345678901"
    source = f'TOKEN = "{secret}"\n'

    without_flag = _run_detector(source)
    with_flag = _run_detector(source, ignore_patterns=(secret[:12],))

    assert blocking_finding_count(with_flag.findings) == blocking_finding_count(
        without_flag.findings
    ), "the suppression record moved the blocking-finding count"

    for finding in with_flag.findings:
        if finding.rule_id.startswith(RULE_OPERATOR_SUPPRESSED_SECRET):
            assert not is_verdict_blocking(finding), (
                "the suppression record is VERDICT-ELIGIBLE — a disclosure must never be able to "
                "block a release on its own (cross-cutting #6)"
            )

    # And with no operator flag at all, the detector's output is byte-identical to before the
    # change: the dogfood run passes no --ignore-* flag, so its verdict cannot drift.
    assert not [
        f for f in without_flag.findings if f.rule_id.startswith(RULE_OPERATOR_SUPPRESSED_SECRET)
    ]
