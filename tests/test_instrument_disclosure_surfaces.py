"""Story 11.1 / AC3.1 + AC3.2 + AC4.1 — the FR34 disclosure on the RUNNING surfaces.

Verification areas ``ArgusAgent-CLI`` (``TC-ArgusAgent-CLI-001-50``, ``-51``) and
``ArgusAgent-REPORT`` (``TC-ArgusAgent-REPORT-002-30``..``-32``). **Test ids are
byte-identical to the ones this module was split out of** — renumbering an id silently
invalidates the citations that resolve against it in ``architecture.md``,
``deferred-work.md`` and the sibling test modules.

**Why this module exists — the cohesion boundary.** ``tests/test_instrument_disclosure.py``
is a STATIC guard suite: it reads the disclosure CONSTANTS, the ``InstrumentStatus``
vocabulary, the ``argus/**`` source text through ``ast``, and the architecture registration.
Nothing in it runs an audit. The guards here are BEHAVIOURAL: they invoke the CLI, generate
the four report artifacts into a ``tmp_path`` and assert the disclosure is on what came out.
Two substrates, two costs, one module — and by Story 13.5 that module stood at **1198 of
NFR-M1's 1200 lines**, i.e. two lines of headroom in front of the FR34 surface every
disclosure story has to touch.

Split by COHESION and not by arithmetic (the Story 13.4 precedent): the boundary is the
section banner Story 11.1 itself drew, no function is split across it, no test id moved, and
the import edge runs **one way only** — this module imports the shared analyzers and floors
FROM ``tests/test_instrument_disclosure.py`` and that module imports nothing from here. A
circular import between two test modules fails at collection, which is why the direction is
stated rather than assumed. No ``_EXEMPT_BY_DESIGN`` entry was added: ``MAINT-001-04``
audits that registry and it may only shrink.

``protocol_cleared_call_sites`` deliberately STAYS in the static module: it is the mechanism
``TC-ArgusAgent-DOCS-001-46`` rests on and ``tests/test_gate_decision.py`` imports it from
there by name.
"""

from __future__ import annotations

from pathlib import Path


from argus.ledger.coverage_ledger import CoverageDepth, CoverageLedger, grade_entry
from argus.models import AuditRequest
from argus.reports.generator import generate_reports
from argus.verdict.negative_assurance import (
    INSTRUMENT_STATUS,
    render_instrument_disclosure,
)
from argus.verdict.verdict_gate import evaluate_verdict

# The analyzers and the non-vacuity floors are IMPORTED from the module this one was split
# out of — never re-authored. A second copy of `unrouted_write_text_calls` would be a second
# thing to keep true, and `-32`'s positive control proves THIS one bites.
from tests.test_instrument_disclosure import (  # noqa: E402
    _DISCLOSURE_HELPER,
    _DISCLOSURE_RENDERER,
    _GENERATOR,
    _MIN_REPORT_ARTIFACTS,
    _MIN_WRITE_TEXT_CALLS,
    _VERDICT_RENDER_CALLS,
    _WRITE_POINT,
    functions_calling,
    mcp_surface_tokens,
    protocol_cleared_call_sites,
    unrouted_write_text_calls,
    write_text_call_count,
)

# The over-claim detector is IMPORTED, never re-authored (Story 9.2's `-17b` documents an
# escape a naive substring scan let through: a negation trailing BEHIND the banned phrase).
from tests.test_release_surface_honesty import _affirmative_over_claims  # noqa: E402

_REPO_ROOT = Path(__file__).resolve().parents[1]

# ─────────────────────────────────────────────────────────────────────────────────────
# AC3.1 — the CLI surface
# ─────────────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_CLI_001_50_the_cli_discloses_on_stderr_and_stdout_is_unchanged(
    tmp_path: Path, capsys
) -> None:
    """TC-ArgusAgent-CLI-001-50 — Story 11.1 / AC3.1: disclosed to the operator, off the wire.

    stdout is the FR18/AR3 wire contract a CI step parses POSITIONALLY, so the disclosure
    goes to stderr — the register the project has already chosen twice for this reason (the
    ship-readiness block; ``_emit_suppression_disclosure``, Story 10.3/AC4.3). Emission is
    UNCONDITIONAL, including on a clean ``RELEASE_READY`` run: a disclosure that only
    appears when something is wrong is one an operator learns nothing from.

    The ``Ship-readiness:`` headline must remain the FIRST line on stderr
    (``tests/test_cli.py::-31`` pins it), so the disclosure follows the human register.
    """
    import sys as _sys

    _sys.path.insert(0, str(Path(__file__).resolve().parent / "cartridges"))
    from _cartridge import stage_cartridge

    from argus import cli

    repo, _sha = stage_cartridge("orphan_basic", tmp_path / "repo")
    code = cli.main(
        ["audit", str(repo), "--commit", "HEAD", "--budget", "100", "--coverage-scope", "repository"]
    )
    captured = capsys.readouterr()

    assert code == 3
    stdout_lines = captured.out.splitlines()
    assert len(stdout_lines) == 1, "stdout is the wire contract: exactly one line"
    assert stdout_lines[0].startswith("verdict=")

    short = render_instrument_disclosure(INSTRUMENT_STATUS, short=True)
    assert short not in captured.out, (
        "the disclosure leaked onto stdout — that surface is parsed positionally (FR18/AR3)"
    )
    assert captured.err.startswith("Ship-readiness:"), (
        "the human headline must stay the first line on stderr (tests/test_cli.py::-31)"
    )
    assert short in " ".join(captured.err.split()), (
        "an invocation that printed a verdict= line printed no instrument-status disclosure"
    )


def test_TC_ArgusAgent_CLI_001_51_a_verdict_line_and_the_disclosure_appear_together(
    tmp_path: Path, capsys, monkeypatch
) -> None:
    """TC-ArgusAgent-CLI-001-51 — Story 11.1 / AC3.1: the invariant, asserted in BOTH directions.

    *An invocation that prints a ``verdict=`` line prints the disclosure; an invocation that
    prints no verdict prints neither.* The invariant is keyed on THE VERDICT LINE, not on
    the exit code, and the two ``exit 1`` paths below are why that distinction is load-bearing:

    * a TYPED pipeline failure produces no verdict at all — nothing reached the consumer,
      so disclosing the instrument's status would imply an assessment happened;
    * a ``ShipReadinessError`` is a CONTRACT VIOLATION *after* a ``verdict=`` line already
      reached stdout. The suppression disclosure is correctly withheld there (it is a claim
      about what THIS RUN found, beside a verdict the tool has just refused to vouch for),
      but FR34 is a statement about the TOOL, so withholding it would leave a verdict on
      stdout with no instrument-status line anywhere — the exact gap FR34 forbids.
    """
    from argus.reports.plain_english import ShipReadinessError

    from argus import cli

    short = render_instrument_disclosure(INSTRUMENT_STATUS, short=True)

    def _typed_failure(_request):
        raise ValueError("synthetic intake failure")

    # Patched at `run_audit_detailed` since 2026-08-15 (Story 12.8 / AC7 / DN-4): `cli.main`
    # calls that entry now, because the grammar-downgrade diagnosis rides on `AuditResult`.
    # `run_audit` is a thin wrapper returning `run_audit_detailed(...).verdict`, so the seam
    # and this guard's observable — no instrument line beside a run with no verdict — are
    # unchanged. Updated deliberately; the alternative was to leave a stand-in nothing calls.
    monkeypatch.setattr(cli, "run_audit_detailed", _typed_failure)
    code = cli.main(["audit", str(tmp_path), "--commit", "HEAD"])
    captured = capsys.readouterr()

    assert code == 1
    assert "verdict=" not in captured.out
    assert short not in captured.err and short not in captured.out, (
        "an invocation that produced NO verdict disclosed the instrument's status anyway; "
        "exit 1 with no verdict line means nothing was assessed (AR10)"
    )

    _request, synthetic_verdict, _ledger = _sample_report_inputs()

    def _unrenderable(_verdict, **_kwargs):
        raise ShipReadinessError("synthetic contract violation")

    from argus.pipeline import AuditResult

    monkeypatch.setattr(  # Story 12.8 / DN-4 — see the note above
        cli,
        "run_audit_detailed",
        lambda _request: AuditResult(verdict=synthetic_verdict, locators=()),
    )
    monkeypatch.setattr(cli, "render_ship_readiness", _unrenderable)
    code = cli.main(["audit", str(tmp_path), "--commit", "HEAD"])
    captured = capsys.readouterr()

    assert code == 1
    assert "verdict=" in captured.out, "the summary line reached stdout before the refusal"
    assert short in " ".join(captured.err.split()), (
        "a verdict= line reached stdout with NO instrument-status disclosure anywhere — "
        "FR34 permits no verdict surface without it"
    )


# ─────────────────────────────────────────────────────────────────────────────────────
# AC3.2 / AC4.1 — the report surface, closed by an `ast` walk of the write point
# ─────────────────────────────────────────────────────────────────────────────────────


def _sample_report_inputs() -> tuple[AuditRequest, object, CoverageLedger]:
    request = AuditRequest(
        repo_path=".",
        commit="HEAD",
        budget=0,
        materiality_bar="",
        enabled_reports=("all",),
    )
    entries = [
        grade_entry(
            file_path=f"file_{i}.py",
            proposed_depth=CoverageDepth.AUDITED_DEEP,
            claim_present=True,
        )
        for i in range(5)
    ]
    ledger = CoverageLedger.build(entries)
    return request, evaluate_verdict(ledger, ()), ledger


def test_TC_ArgusAgent_REPORT_002_30_every_generated_report_carries_the_disclosure(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-REPORT-002-30 — Story 11.1 / AC3.2: all four artifacts, behaviourally.

    ``coverage-ledger.md`` is rendered by ``argus/ledger/coverage_report.py``, not by the
    generator. The disclosure is injected AT THE WRITE, so it reaches that artifact with no
    ``argus/ledger/**`` edit and no ``ledger → reports`` import inversion (§C.2 / DN-1b).
    """
    request, verdict, ledger = _sample_report_inputs()
    generated = generate_reports(request, verdict, ledger, [], tmp_path / "reports")

    assert len(generated) >= _MIN_REPORT_ARTIFACTS, (
        f"only {len(generated)} report artifacts were written — the behavioural check has "
        "gone vacuous (E.3)"
    )
    expected = render_instrument_disclosure(INSTRUMENT_STATUS)
    for key, path in sorted(generated.items()):
        body = path.read_text(encoding="utf-8")
        assert expected in body, f"{key} was written without the instrument-status disclosure"
        assert not _affirmative_over_claims(body), f"{key} asserts an over-claim"


def test_TC_ArgusAgent_REPORT_002_31_every_write_in_the_write_point_is_routed(
    ) -> None:
    """TC-ArgusAgent-REPORT-002-31 — Story 11.1 / AC4.1, AC4.5: THE LOAD-BEARING CLOSURE.

    ``-30`` proves today's four artifacts carry the disclosure. That closes the instances,
    not the class: a **fifth** report added to ``generate_reports`` would ship undisclosed
    and ``-30`` would stay green. So this parses the write point's OWN BODY with the stdlib
    ``ast`` module and requires every ``write_text`` call in it to receive a value produced
    by the disclosure helper — the ``_get_parser_for_lang`` idiom from
    ``tests/test_grammar_diagnosis.py::-115``.

    Non-vacuity is mandatory (E.3): a rename of ``generate_reports``, a move of the module,
    or an ``ast.parse`` failure must turn this RED, not silently green.

    ⚠️ **The floor was RE-DERIVED 2026-08-15 by Story 12.8** — see ``_MIN_WRITE_TEXT_CALLS``
    for the full reason. Counting ``write_text`` calls was a proxy for *"the four reports are
    still written here"* and held only while the four were four copy-pasted branches. They
    are now ONE loop over ``RENDERED_REPORT_TYPES``, so the population is asserted directly,
    against the constant. That is a correction, not a loosening: this guard's own remedy
    sentence — *"route it, do not enumerate it"* — is what the loop implements.
    """
    from argus.reports.generator import RENDERED_REPORT_TYPES

    source = _GENERATOR.read_text(encoding="utf-8")

    found = write_text_call_count(source, _WRITE_POINT)
    assert found >= _MIN_WRITE_TEXT_CALLS, (
        f"found {found} write_text calls inside {_WRITE_POINT}() — expected at least "
        f"{_MIN_WRITE_TEXT_CALLS}. Either the write point was renamed/moved (fix this "
        "guard's _WRITE_POINT) or the reports are no longer written there. A source-walking "
        "guard that finds nothing passes vacuously."
    )
    assert len(RENDERED_REPORT_TYPES) >= _MIN_REPORT_ARTIFACTS, (
        f"the report-type population shrank to {list(RENDERED_REPORT_TYPES)}. The write "
        "point is a loop over that constant now, so the count of write_text CALLS can no "
        "longer notice a report disappearing — this assertion is what does. Removing a "
        "consumer-facing report type is a published-surface change; take it deliberately."
    )
    assert f"in {'RENDERED_REPORT_TYPES'}:" in source, (
        "the write point no longer iterates RENDERED_REPORT_TYPES, so a report type could "
        "again be written by a hand-authored branch that bypasses the disclosure helper."
    )
    assert f"def {_DISCLOSURE_HELPER}(" in source, (
        f"the disclosure helper {_DISCLOSURE_HELPER}() is gone from the write point's module"
    )

    unrouted = unrouted_write_text_calls(source, _WRITE_POINT, _DISCLOSURE_HELPER)
    assert not unrouted, (
        f"{len(unrouted)} write_text call(s) in {_WRITE_POINT}() do not flow through "
        f"{_DISCLOSURE_HELPER}(): {unrouted}. Every report artifact is a verdict surface "
        "and FR34 permits none without the disclosure — route it, do not enumerate it."
    )


def test_TC_ArgusAgent_REPORT_002_32_the_write_point_closure_fires_on_a_fifth_report() -> None:
    """TC-ArgusAgent-REPORT-002-32 — Story 11.1 / AC4.6: the closure's positive control.

    A guard that never fails on a bad input proves nothing (AI-E3-1: Story 3.4 shipped a
    keystone test that was green over its own keystone bug). Both directions, over
    SYNTHETIC source only — never by editing the live generator during a test.
    """
    routed = (
        "def generate_reports():\n"
        "    dest.write_text(_with_instrument_disclosure(a), encoding='utf-8')\n"
        "    other.write_text(_with_instrument_disclosure(b), encoding='utf-8')\n"
    )
    assert not unrouted_write_text_calls(routed, _WRITE_POINT, _DISCLOSURE_HELPER)
    assert write_text_call_count(routed, _WRITE_POINT) == 2

    # A FIFTH report, added the obvious way, with the helper forgotten.
    smuggled = routed + "    fifth.write_text(c, encoding='utf-8')\n"
    caught = unrouted_write_text_calls(smuggled, _WRITE_POINT, _DISCLOSURE_HELPER)
    assert len(caught) == 1, "the closure did not catch an unrouted fifth report"

    # A helper of a DIFFERENT name is not the helper — the routing is not "any call".
    wrong_helper = (
        "def generate_reports():\n"
        "    dest.write_text(_with_something_else(a), encoding='utf-8')\n"
    )
    assert unrouted_write_text_calls(wrong_helper, _WRITE_POINT, _DISCLOSURE_HELPER)

    # A renamed write point makes the counter zero — which is what the non-vacuity floor
    # in `-31` converts into a RED.
    assert write_text_call_count(routed, "some_other_name") == 0

    # The harness-agreement analyzer, both directions. A MENTION is not a call site — the
    # substring form of this scan reported `replay_harness.py`'s own docstring and this
    # repository's honesty comments as production flips of the gate.
    assert protocol_cleared_call_sites("compute_precision(x, protocol_cleared=True)") == (1,)
    assert protocol_cleared_call_sites("compute_precision(x, protocol_cleared=False)") == ()
    assert protocol_cleared_call_sites("# never passes protocol_cleared=True\n") == ()
    assert protocol_cleared_call_sites('"""mentions protocol_cleared=True."""\n') == ()

    # And the MCP closure's own positive control, over a synthetic candidate set.
    assert mcp_surface_tokens({"argus/mcp_server.py": "serve()"}) == ("argus/mcp_server.py",)
    assert mcp_surface_tokens({"argus/cli.py": "# Model Context Protocol server"}) == (
        "argus/cli.py",
    )
    assert mcp_surface_tokens({"argus/cli.py": "def main(): ..."}) == ()

    # The ROUTING analyzer `-49` was corrected onto (Story 12.6), both directions, over
    # SYNTHETIC source only. The correction replaced an assertion that would have DEMANDED
    # a transcribed copy of the constant, so its control has to show that routing — and
    # only routing — satisfies it.
    honest = (
        "def render_result(v):\n"
        "    lines = [summary_line(v)]\n"
        "    lines.extend(render_ship_readiness(v))\n"
        "    lines.append(render_instrument_disclosure(INSTRUMENT_STATUS))\n"
        "    return lines\n"
    )
    assert functions_calling(honest, _VERDICT_RENDER_CALLS) == {"render_result"}
    assert functions_calling(honest, (_DISCLOSURE_RENDERER,)) == {"render_result"}
    assert not (
        functions_calling(honest, _VERDICT_RENDER_CALLS)
        - functions_calling(honest, (_DISCLOSURE_RENDERER,))
    )

    # A SECOND verdict renderer added later without the disclosure — the drift the closure
    # exists to catch, and the reason it is derived rather than declared per file.
    smuggled_surface = honest + (
        "\n\ndef render_short_result(v):\n    return summary_line(v)\n"
    )
    assert functions_calling(smuggled_surface, _VERDICT_RENDER_CALLS) - functions_calling(
        smuggled_surface, (_DISCLOSURE_RENDERER,)
    ) == {"render_short_result"}, "the routing closure stopped catching an unrouted verdict"

    # A module that renders no verdict owes nothing, and the closure says so rather than
    # demanding a disclosure from a package marker.
    assert functions_calling("VERSION = '1'\n", _VERDICT_RENDER_CALLS) == frozenset()

    # A method call spelled through an attribute is still a call — a renderer reached as
    # `protocol.summary_line(...)` must not slip past.
    assert functions_calling(
        "def f(v):\n    return mod.summary_line(v)\n", _VERDICT_RENDER_CALLS
    ) == {"f"}
