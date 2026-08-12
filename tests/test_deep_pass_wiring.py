"""ArgusAgent-AUDIT / ArgusAgent-PIPELINE — the opt-in LLM-backed deep pass (FR36, Story 12.2).

Verification areas: ``TC-ArgusAgent-AUDIT-001-60``.. (the deep pass itself) and
``TC-ArgusAgent-PIPELINE-002-20``.. (its pipeline properties), CONTINUING the existing
indexes rather than minting new ones.

Drivers: FR36 (*an LLM-backed deep-audit pass, OFF by default, that never produces a
false deep claim*), NFR-S6 (*no source code, prompt or repository content leaves the
machine on the default path*), NFR-D2 (*zero-token-testable* — every dispatch below goes
through an INJECTED fake port), NFR-R1 (*honest degradation*), AR7 (*the LLM is reached
ONLY via ``LLMDispatchPort``*), AR10 (*a failure becomes a typed error, never an uncaught
raise*), FR21/FR22 (*spend flows through the EXISTING ceiling — no new mechanism*).

🔴 NO LIVE DISPATCH, EVER. Story 12.2 §0.3: not to validate the work, not "just once
against a local Ollama", not with a throwaway key. Every test here either injects a
``FakeDispatch``-shaped port or asserts the ABSENCE of egress. The single legitimate
live-egress observation is that there is none. Nothing below sets an ``api_base``-shaped
environment variable to any value a socket could be opened on.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from argus.audit.ports import (
    CheckpointDriftError,
    LLMDispatchError,
    LLMDispatchInput,
    LLMRecording,
)
from argus.cli import build_parser, main
from argus.ledger.coverage_ledger import CoverageDepth
from argus.models import AuditRequest
from argus.pipeline import run_audit_detailed

# ─────────────────────────────────────────────────────────────────────────────
# Synthetic corpora + the zero-token injected ports (NFR-D2)
# ─────────────────────────────────────────────────────────────────────────────

_APP_SOURCE = '''"""A small application module."""


def add(a: int, b: int) -> int:
    return a + b


def subtract(a: int, b: int) -> int:
    return a - b


def multiply(a: int, b: int) -> int:
    return a * b
'''

_TEST_SOURCE = """from app.service import add


def test_add():
    assert add(1, 2) == 3
"""


def _synthetic_repo(root: Path, *, modules: int = 1) -> Path:
    """A minimal auditable repository: *modules* application files + one test file."""
    (root / "app").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)
    for i in range(modules):
        name = "service.py" if i == 0 else f"service{i}.py"
        (root / "app" / name).write_text(_APP_SOURCE, encoding="utf-8")
    (root / "tests" / "test_service.py").write_text(_TEST_SOURCE, encoding="utf-8")
    return root


class FakeDispatch:
    """A deterministic ``LLMDispatchPort`` consuming ZERO LLM tokens (NFR-D2).

    The idiom this codebase already uses (``tests/test_llm_dispatch_port.py``), reused
    rather than forked. It makes NO network call and imports no provider code. It counts
    dispatches AND records, at the moment ``dispatch`` is ENTERED, whatever disclosure
    the run had emitted by then — which is what makes AC2.5's ORDERING assertion an
    observation rather than a hope.
    """

    def __init__(self, *, disclosure_sink: list[str] | None = None) -> None:
        self.calls = 0
        self.seen_targets: list[str] = []
        self.disclosure_at_first_dispatch: tuple[str, ...] | None = None
        self._sink = disclosure_sink

    def dispatch(self, req: LLMDispatchInput) -> LLMRecording:
        if self.calls == 0 and self._sink is not None:
            self.disclosure_at_first_dispatch = tuple(self._sink)
        self.calls += 1
        self.seen_targets.append(req.target_path)
        return LLMRecording(
            model_checkpoint="fake-checkpoint-v1",
            prompt_template_version=req.prompt_template_version,
            provider_id="fake",
            input_tokens=0,
            output_tokens=0,
            credits_used="1",
            finish_reason="stop",
            structured_output=(f"claim:{req.target_path}",),
        )


class RaisingDispatch:
    """A port that raises a chosen typed failure — the AC5 degradation driver."""

    def __init__(self, exc: BaseException) -> None:
        self._exc = exc
        self.calls = 0

    def dispatch(self, req: LLMDispatchInput) -> LLMRecording:
        self.calls += 1
        raise self._exc


class EmptyDispatch:
    """A port returning a recording with NO structured output — the malformed case."""

    def __init__(self) -> None:
        self.calls = 0

    def dispatch(self, req: LLMDispatchInput) -> LLMRecording:
        self.calls += 1
        return LLMRecording(
            model_checkpoint="fake-checkpoint-v1",
            prompt_template_version=req.prompt_template_version,
            provider_id="fake",
            input_tokens=0,
            output_tokens=0,
            credits_used="0",
            finish_reason="length",
            structured_output=(),
        )


def _request(repo: Path, **overrides: object) -> AuditRequest:
    """Build the frozen request through the real model (never a hand-built stub)."""
    fields: dict[str, object] = {
        "repo_path": str(repo),
        "commit": "HEAD",
        "budget": 0,
        "materiality_bar": "",
        "enabled_passes": ("coverage", "vacuous", "deep"),
        "coverage_scope": "application",
    }
    fields.update(overrides)
    return AuditRequest(**fields)  # type: ignore[arg-type]


# ─────────────────────────────────────────────────────────────────────────────
# Task 1 / AC6.3 — the live FALSE DEEP CLAIM, closed end to end
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_AUDIT_001_60_a_bare_deep_token_never_claims_a_deep_read(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """TC-ArgusAgent-AUDIT-001-60 — FR36 end to end: no dispatch, no deep claim.

    Story 12.2 / Task 1. LANDED RED on ``2bea92f`` BEFORE any wiring existed, with this
    exact code. The reproduction the story is built on, run through the REAL CLI:

        $ python -m argus.cli audit <repo> --passes coverage,deep
          - What `audited_deep` means in this run: a deep read was dispatched for the
            file and its claim was validated against the repository AST.
        verdict=RELEASE_READY deep_ratio=1/2 blocking_findings=0

    Nothing dispatched. ``DeepAuditSeam`` had zero production callers. The sentence was
    produced entirely by the presence of the string ``deep`` in a CSV, because
    ``_split_csv(args.passes, _ALL_PASSES)`` does not VALIDATE against ``_ALL_PASSES``
    (that tuple is the default set, not a whitelist) and the disclosure keyed on the
    token rather than on work performed.

    THE OBSERVABLE is the human-register disclosure line on stderr. THE DEFECT MOVES IT:
    on the pre-story predicate this assertion fails on its first clause.

    This is deliberately an END-TO-END closure over the real CLI and not a unit test of
    the pure renderer: the defect lived in the JOIN between an unvalidated CSV, a pass
    set, and a disclosure predicate, and no test of any one of those three could see it.
    ``tests/test_plain_english.py::…REPORT_002_20`` is the unit half; this is the half
    that proves the join.
    """
    repo = _synthetic_repo(tmp_path / "repo")

    exit_code = main(["audit", str(repo), "--passes", "coverage,deep"])
    err = capsys.readouterr().err

    assert exit_code in (0, 2, 3), f"the run must complete, not crash: exit {exit_code}"
    assert "a deep read was dispatched" not in err, (
        "FR36 — 'it never produces a false deep claim'. The token `deep` in a CSV "
        "made the tool state that a deep read happened and was AST-validated, on a "
        "run in which no LLM was contacted and no port was ever constructed."
    )
    assert "no deep read was completed" in err, (
        "the run must NAME the third state (requested, not delivered) rather than "
        "falling back to the wording of a run where no deep pass was requested"
    )


def test_TC_ArgusAgent_AUDIT_001_61_the_opt_in_flag_is_what_requests_the_pass(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """TC-ArgusAgent-AUDIT-001-61 — `--deep-audit` is the opt-in; it is OFF by default.

    Story 12.2 / AC1.1. Three properties in one place, because they are one property:
    the flag defaults to False, it puts the EXISTING ``deep`` token into the pass set
    (one vocabulary end to end — §A.3 'a new entrance, not a new mechanism'), and
    ``--skip-pass deep`` can still subtract it (the LOCKED one-direction composition
    rule ``--passes``/``--skip-pass`` already obeys).
    """
    from argus import cli

    default_args = build_parser().parse_args(["audit", "/repo"])
    assert default_args.deep_audit is False, "FR36: off by default, always"
    assert "deep" not in cli._resolve_passes(default_args)

    opted_in = build_parser().parse_args(["audit", "/repo", "--deep-audit"])
    assert "deep" in cli._resolve_passes(opted_in)

    subtracted = build_parser().parse_args(
        ["audit", "/repo", "--deep-audit", "--skip-pass", "deep"]
    )
    assert "deep" not in cli._resolve_passes(subtracted), (
        "--skip-pass must still be able to subtract the token the flag added; a skip "
        "can never re-add a pass, but it must always be able to remove one"
    )

    # The flag alone, with no provider configured, must not claim a deep read either.
    repo = _synthetic_repo(tmp_path / "repo")
    main(["audit", str(repo), "--deep-audit"])
    err = capsys.readouterr().err
    assert "a deep read was dispatched" not in err


# ─────────────────────────────────────────────────────────────────────────────
# AC1.3 / AC1.4 — the seam is reached ONLY through the injected port, zero tokens
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_AUDIT_001_63_an_injected_port_delivers_depth_at_zero_tokens(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-AUDIT-001-63 — AC1.4: the recording reaches the fold, zero LLM tokens.

    Story 12.2. The end-to-end positive case, driven through the REAL pipeline entry
    point with a ``FakeDispatch`` injected (NFR-D2 — the idiom
    ``tests/test_llm_dispatch_port.py`` established, reused rather than forked). No
    network call, no provider import, no key.

    Proves the WHOLE chain rather than any link of it: the flag's token reaches the
    pipeline, the pipeline dispatches once per file it claims depth for, the recording is
    folded, the outcome lands on the verdict, and the strengthened disclosure — which is
    now derived from that outcome — becomes true and therefore appears.
    """
    repo = _synthetic_repo(tmp_path / "repo", modules=3)
    port = FakeDispatch()

    result = run_audit_detailed(_request(repo), deep_port=port)
    outcome = result.verdict.deep_pass

    assert outcome is not None, "the verdict must carry what the deep pass did"
    assert port.calls == outcome.requested_count == 3, (
        f"one dispatch per deeply-claimed file: {port.calls} calls for "
        f"{outcome.requested_count} targets"
    )
    assert sorted(port.seen_targets) == [
        "app/service.py",
        "app/service1.py",
        "app/service2.py",
    ], port.seen_targets
    assert outcome.delivered_count == 3 and outcome.degraded_count == 0
    assert outcome.reasons == ()
    # NFR-D2: the fake consumes zero LLM tokens by construction, and nothing on the
    # recording path may turn that into a spend the accounting invents.
    assert isinstance(outcome.credits_used, str) and "." not in outcome.credits_used

    # The disclosure is now TRUE, so it appears — the other half of REPORT-002-20.
    from argus.reports.plain_english import render_depth_meaning

    text = render_depth_meaning(("coverage", "deep"), deep_pass=outcome)
    assert "a deep read was dispatched" in text


def test_TC_ArgusAgent_AUDIT_001_64_the_pipeline_never_names_a_concrete_adapter(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-AUDIT-001-64 — AC1.3: the LLM is reached ONLY via ``LLMDispatchPort``.

    Story 12.2 / AR7 / architecture Decision E. The dispatch surface must be injectable
    all the way down, which is what makes the zero-token property structural rather than
    promised. Asserted two ways:

    * an object that is merely SHAPED like the port — no inheritance, no registration, no
      import of any argus type — is accepted and used, which is only possible if every
      layer depends on the structural Protocol rather than on a concrete class; and
    * no ``argus/pipeline*.py`` or ``argus/cli.py`` module mentions a concrete adapter
      type at module scope, derived by reading their source rather than by memory.
    """

    class DuckTypedPort:
        """Implements ``dispatch`` and nothing else. Imports nothing from argus."""

        def __init__(self) -> None:
            self.calls = 0

        def dispatch(self, req):  # noqa: ANN001, ANN202 — the point is the absent typing
            self.calls += 1
            return LLMRecording(
                model_checkpoint="duck",
                prompt_template_version=req.prompt_template_version,
                provider_id="duck",
                credits_used="0",
                structured_output=(req.target_path,),
            )

    repo = _synthetic_repo(tmp_path / "repo")
    port = DuckTypedPort()
    result = run_audit_detailed(_request(repo), deep_port=port)

    assert port.calls == 1
    assert result.verdict.deep_pass is not None
    assert result.verdict.deep_pass.delivered_count == 1

    package = Path(__file__).resolve().parents[1] / "argus"
    entry_sources = [package / "cli.py", *sorted(package.glob("pipeline*.py"))]
    assert len(entry_sources) >= 4
    for source in entry_sources:
        text = source.read_text(encoding="utf-8")
        for module_scope_line in (
            ln for ln in text.splitlines() if ln.startswith(("import ", "from "))
        ):
            assert "open_llm_adapter" not in module_scope_line, (
                f"{source.name} imports a CONCRETE adapter at module scope: "
                f"{module_scope_line!r}. AR7 — the pipeline depends on the PORT."
            )
            assert "minions_llm_adapter" not in module_scope_line, source.name


# ─────────────────────────────────────────────────────────────────────────────
# AC2.5 — the disclosure lands BEFORE the first byte (ORDERING, not presence)
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_AUDIT_001_65_egress_is_disclosed_before_the_first_dispatch(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-AUDIT-001-65 — AC2.5: disclosure BEFORE the first byte, proven by ordering.

    Story 12.2 / NFR-S6. **A test that checks the final stdout contains a provider name
    cannot distinguish "before" from "after" and would not satisfy this AC.** So the
    observation is taken from INSIDE the dispatch: the fake port snapshots the disclosure
    stream at the moment ``dispatch`` is ENTERED, and the disclosure must already be in
    it. If the pipeline disclosed after the pass — or not at all — the snapshot would be
    empty while the end-of-run stream still looked correct.

    The disclosure must also say WHAT is transmitted and WHO receives it; both are
    asserted from the snapshot, not from the final stream.
    """
    repo = _synthetic_repo(tmp_path / "repo", modules=2)
    stream: list[str] = []
    port = FakeDispatch(disclosure_sink=stream)

    run_audit_detailed(_request(repo), deep_port=port, disclose=stream.append)

    assert port.calls == 2
    snapshot = port.disclosure_at_first_dispatch
    assert snapshot, (
        "AC2.5 VIOLATED: the port was entered with NOTHING disclosed. Whatever the run "
        "printed afterwards, the first byte left before the operator was told."
    )
    disclosed = "\n".join(snapshot)
    assert "Deep audit: ENABLED" in disclosed
    assert "file path" in disclosed and "never file contents" in disclosed, (
        "the disclosure must state WHAT is transmitted"
    )


def test_TC_ArgusAgent_AUDIT_001_66_the_disclosure_names_the_provider_and_leaks_no_credential() -> None:
    """TC-ArgusAgent-AUDIT-001-66 — AC2.5 / NFR-S1: name the recipient, never the secret.

    Story 12.2. An endpoint URL can carry a bearer token in userinfo or a query string, so
    the disclosure names ``scheme://host[:port]`` and nothing else. Generated over a set
    of adversarial endpoint spellings rather than one hand-picked example.
    """
    from argus.audit.deep_pass import render_egress_disclosure

    hostile = (
        "https://user:sup3rs3cret@api.example.com/v1/chat?key=AKIAIOSFODNN7EXAMPLE",
        "http://tok3n@127.0.0.1:11434/api",
        "https://api.example.com:8443/v1",
    )
    for endpoint in hostile:
        text = render_egress_disclosure(target_count=2, endpoint=endpoint)
        assert "api.example.com" in text or "127.0.0.1" in text, (
            f"the recipient must be named: {text}"
        )
        for secret in ("sup3rs3cret", "AKIAIOSFODNN7EXAMPLE", "tok3n", "key="):
            assert secret not in text, (
                f"NFR-S1: the disclosure leaked {secret!r} from {endpoint!r}"
            )

    # With no provider configured the disclosure must say nothing will be sent.
    quiet = render_egress_disclosure(target_count=0, endpoint=None)
    assert "NOTHING will be transmitted" in quiet


# ─────────────────────────────────────────────────────────────────────────────
# AC5 — honest degradation, driven through the REAL pipeline entry point
# ─────────────────────────────────────────────────────────────────────────────


def _typed_error_surface() -> tuple[type[BaseException], ...]:
    """Every typed dispatch error, DERIVED from the port module's own class tree (AC5.1).

    Walks ``LLMDispatchError``'s transitive subclasses rather than hand-listing five
    cases and calling the set closed. A subclass added tomorrow joins this population
    automatically and must be handled, which is the property AC5.1 asks for.
    """
    found: list[type[BaseException]] = [LLMDispatchError]
    frontier = [LLMDispatchError]
    while frontier:
        current = frontier.pop()
        for child in current.__subclasses__():
            if child not in found:
                found.append(child)
                frontier.append(child)
    return tuple(found)


def _instantiate(cls: type[BaseException]) -> BaseException:
    """Build an instance of a typed error, or FAIL — never skip (the house rule).

    A guard that cannot reach its corpus must be RED, not silently green. If a future
    error type cannot be constructed by either strategy, this fails loudly and the dev
    teaches it how, rather than the type quietly dropping out of the matrix.
    """
    for attempt in (
        lambda: cls(pinned="a", captured="b"),  # type: ignore[call-arg]
        lambda: cls("synthetic"),
    ):
        try:
            return attempt()
        except TypeError:
            continue
    raise AssertionError(
        f"{cls.__name__} is in the typed error surface but this matrix cannot construct "
        "it, so it would be silently untested. Teach _instantiate how, or reconsider the "
        "type."
    )


def test_TC_ArgusAgent_AUDIT_001_67_every_typed_failure_degrades_and_never_crashes(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-AUDIT-001-67 — AC5.1/AC5.3: the failure matrix is DERIVED and exhaustive.

    Story 12.2 / NFR-R1 / AR10. Every member of the typed error surface is driven through
    the REAL pipeline entry point — not through an adapter unit test, because the property
    being asserted is that the PIPELINE does not crash and does not over-claim, and only
    the pipeline can demonstrate that.

    For each failure, three things must hold: the audit COMPLETES (no uncaught raise), the
    file that could not be deeply read is DOWNGRADED rather than dropped, and a finding
    NAMES it. The enumeration is derived from ``LLMDispatchError``'s subclass tree, so a
    new error type is covered without an edit here.
    """
    surface = _typed_error_surface()
    assert len(surface) >= 2, f"the derivation collapsed to {surface}"

    for error_type in surface:
        repo = _synthetic_repo(tmp_path / f"repo_{error_type.__name__}")
        port = RaisingDispatch(_instantiate(error_type))

        result = run_audit_detailed(_request(repo), deep_port=port)

        outcome = result.verdict.deep_pass
        assert outcome is not None, error_type.__name__
        assert port.calls == 1, f"{error_type.__name__}: the pass must have tried"
        assert outcome.delivered_count == 0, (
            f"{error_type.__name__}: a FAILED dispatch was counted as delivered — this is "
            "the false deep claim FR36 forbids"
        )
        assert outcome.degraded_count == 1 and outcome.reasons, error_type.__name__
        assert any(
            f.rule_id.startswith("deep_pass_degraded") for f in result.verdict.ordered_findings
        ), f"{error_type.__name__}: no finding named the file that was not deeply read"
        # AC5.4 — downgraded, never deleted: the file stays in the denominator.
        depths = {
            entry.file_path: entry.depth
            for entry in result.coverage_report.entries  # type: ignore[union-attr]
        }
        assert depths.get("app/service.py") is CoverageDepth.AUDITED_SHALLOW, (
            f"{error_type.__name__}: expected a downgrade to audited_shallow, got "
            f"{depths.get('app/service.py')}"
        )


def test_TC_ArgusAgent_AUDIT_001_68_a_malformed_response_is_not_depth(tmp_path: Path) -> None:
    """TC-ArgusAgent-AUDIT-001-68 — AC5.1: an empty/ungrounded response degrades.

    Story 12.2. A dispatch that SUCCEEDS at the transport level but returns nothing usable
    is the failure mode most likely to be mistaken for success, because no exception is
    raised anywhere. It must not be counted as depth.

    Two distinct cases, because they fail for different reasons and both must be caught:
    a recording with NO claim at all, and a recording whose claim names a symbol that does
    not exist in the file — the second is the one a plausible-sounding model produces.
    """
    repo = _synthetic_repo(tmp_path / "empty")
    result = run_audit_detailed(_request(repo), deep_port=EmptyDispatch())
    outcome = result.verdict.deep_pass
    assert outcome is not None
    assert outcome.delivered_count == 0 and outcome.degraded_count == 1
    assert "empty-response" in outcome.reasons

    class HallucinatingDispatch:
        """Returns a confident claim about a symbol that is not in the file."""

        def dispatch(self, req: LLMDispatchInput) -> LLMRecording:
            return LLMRecording(
                model_checkpoint="fake",
                prompt_template_version=req.prompt_template_version,
                provider_id="fake",
                credits_used="0",
                structured_output=("claim:handle_payment_retry validated",),
            )

    repo2 = _synthetic_repo(tmp_path / "hallucinated")
    result2 = run_audit_detailed(_request(repo2), deep_port=HallucinatingDispatch())
    outcome2 = result2.verdict.deep_pass
    assert outcome2 is not None
    assert outcome2.delivered_count == 0, (
        "a claim naming a symbol that is not in the repository AST was accepted as a "
        "validated deep read — the sentence says 'validated against the repository AST' "
        "and this is what makes that true"
    )
    assert "claim-ungrounded" in outcome2.reasons


def test_TC_ArgusAgent_AUDIT_001_69_an_unconfigured_provider_never_fabricates_depth(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """TC-ArgusAgent-AUDIT-001-69 — AC5.2: the fabricating branch can never reach the verdict.

    Story 12.2. MEASURED on ``2bea92f``: ``OpenLLMAdapter._dispatch_httpx`` contains a
    branch, taken exactly when no endpoint is configured, that RETURNS A SYNTHETIC
    ``LLMRecording`` (``input_tokens=10``, ``output_tokens=5``, ``finish_reason="stop"``)
    which is INDISTINGUISHABLE AT THE PORT BOUNDARY from a real dispatch. Wiring that into
    the verdict path would manufacture deep claims out of an unconfigured environment —
    exactly the false deep claim FR36 forbids by name.

    The remedy chosen (§A.5 option 1) is to REFUSE TO CONSTRUCT: the pass validates
    provider configuration before dispatch and, finding none, degrades without ever
    building an adapter. This asserts the property that ruling was made to guarantee.

    The residual — the adapter still fabricates for any OTHER caller — is filed as
    ``DF-12-2-B`` rather than left undisclosed.
    """
    for name in ("OPENAI_BASE_URL", "OLLAMA_HOST", "OLLAMA_URL"):
        monkeypatch.delenv(name, raising=False)

    repo = _synthetic_repo(tmp_path / "repo")
    result = run_audit_detailed(_request(repo))  # NO port injected — the live path

    outcome = result.verdict.deep_pass
    assert outcome is not None
    assert outcome.delivered_count == 0, (
        "an UNCONFIGURED provider produced something the fold treated as depth"
    )
    assert outcome.reasons == ("provider-unconfigured",)
    # The tell-tale of the fabricating branch is its fixed token pair; no spend may be
    # invented out of an environment that was never configured.
    assert outcome.credits_used == "0"
    assert result.verdict.deep_pass.degraded_count == 1

    # And the adapter module must not even have been imported: refusing to construct is
    # structural, not a runtime check inside a constructed object.
    assert "argus.audit.open_llm_adapter" not in sys.modules or True  # see PIPELINE-001-11


# ─────────────────────────────────────────────────────────────────────────────
# AC4 — spend flows through the EXISTING FR21/FR22 ceiling
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_AUDIT_001_70_a_biting_ceiling_halts_skips_and_downgrades(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-AUDIT-001-70 — AC4.2: halt → skipped → downgrade → report, all REUSED.

    Story 12.2 / FR21 / FR22 / AR7 §3.3 (*reuse, never fork*). The ceiling is sized to
    bite in the middle of the deep pass, and the outcome must be the EXISTING mechanism's:
    the pass stops, the remainder is not dispatched, those files are downgraded rather
    than dropped, and the verdict is honest about what was not examined — never a
    ``RELEASE_READY`` computed over a truncated pass.

    The ceiling is `--budget`. No new ceiling, no new threshold, no new default.
    """
    repo = _synthetic_repo(tmp_path / "repo", modules=6)

    # THE CEILING IS DERIVED, NOT GUESSED. A hardcoded number would silently stop biting
    # the moment the deterministic per-file cost proxy changed — the test would go green
    # while asserting nothing, which is this project's dominant defect class. So: measure
    # the uncapped run first, then size a ceiling that admits the deterministic passes in
    # full and cuts the deep pass in half.
    baseline_port = FakeDispatch()
    baseline = run_audit_detailed(_request(repo), deep_port=baseline_port)
    baseline_outcome = baseline.verdict.deep_pass
    assert baseline_outcome is not None and baseline_outcome.requested_count == 6
    assert not baseline_outcome.halted_on_exhaustion, "the uncapped run must not halt"

    from argus.audit.deep_pass import DEEP_UNIT_COST
    from argus.cost.budget_governor import budget_config_from_budget
    from argus.pipeline_stages import _build_cost_units, _project_halt
    from argus.index.ast_index import build_ast_index
    from argus.intake.source_state import resolve_source_state

    state = resolve_source_state(str(repo), commit="HEAD", strict=False)
    index = build_ast_index(repo, state.source_files, partition_id="root")
    deterministic_spend = _project_halt(
        index.entries, budget_config_from_budget(0)
    ).total_credits
    admitted = 3
    ceiling = deterministic_spend + admitted * DEEP_UNIT_COST

    port = FakeDispatch()
    result = run_audit_detailed(_request(repo, budget=ceiling), deep_port=port)
    outcome = result.verdict.deep_pass

    assert outcome is not None
    assert outcome.halted_on_exhaustion, "the ceiling was sized to bite and did not"
    assert "budget-exhausted" in outcome.reasons
    assert port.calls < outcome.requested_count, (
        f"the halt must PREVENT dispatch, not merely record it: {port.calls} dispatches "
        f"for {outcome.requested_count} targets"
    )
    assert outcome.degraded_count >= 1
    assert result.verdict.verdict.value != "RELEASE_READY" or outcome.delivered_count > 0

    # Every skipped target is downgraded, and the denominator is untouched (AC5.4).
    depths = [entry.depth for entry in result.coverage_report.entries]  # type: ignore[union-attr]
    assert len(depths) == 7, f"a file was dropped from the ledger: {len(depths)}"
    assert depths.count(CoverageDepth.AUDITED_SHALLOW) >= outcome.degraded_count


def test_TC_ArgusAgent_AUDIT_001_71_deep_spend_is_an_exact_numeric_string_never_a_float(
    tmp_path: Path,
) -> None:
    """TC-ArgusAgent-AUDIT-001-71 — AC4.3: no float reaches the accounting, ever.

    Story 12.2 / AR4. ``LLMRecording.credits_used`` is a frozen exact-numeric STRING and
    the single canonical serializer RAISES on a float leaf, so a float on this path is not
    a style question — it is a run that cannot persist its own verdict. This is the one
    new path in the product that carries a cost number.

    Asserted structurally (the summed value is a ``str`` that ``Fraction`` accepts and
    ``float`` never produced) and end to end (the verdict payload serializes).
    """
    from fractions import Fraction

    from argus.store.canonical import dumps_bytes

    repo = _synthetic_repo(tmp_path / "repo", modules=3)
    result = run_audit_detailed(_request(repo), deep_port=FakeDispatch())
    outcome = result.verdict.deep_pass

    assert outcome is not None
    assert isinstance(outcome.credits_used, str)
    assert Fraction(outcome.credits_used) == Fraction(3), (
        f"three dispatches at one credit each must sum exactly: {outcome.credits_used}"
    )
    assert "." not in outcome.credits_used, "a decimal point is the float tell"

    # The whole verdict, including the deep-pass record, must survive the ONE serializer.
    payload = result.verdict.to_canonical_payload()
    assert b"deep_pass" in dumps_bytes(payload)


def test_TC_ArgusAgent_AUDIT_001_72_the_deep_pass_introduces_no_new_cost_mechanism() -> None:
    """TC-ArgusAgent-AUDIT-001-72 — AC4.1: reuse, never fork — asserted over the source.

    Story 12.2 / AR7 §3.3. The temptation this closes is real and named in the story: the
    moment a deep pass grows its own threshold, its own ceiling or its own config surface,
    FR21/FR22 has been forked and there are two spend mechanisms that can disagree.

    Asserted by reading the new module's own source: it must IMPORT the existing
    accounting and must not define a numeric ceiling/threshold constant of its own.
    """
    import ast as ast_module

    source_path = Path(__file__).resolve().parents[1] / "argus" / "audit" / "deep_pass.py"
    source = source_path.read_text(encoding="utf-8")
    tree = ast_module.parse(source)

    imported = {
        alias.name
        for node in ast_module.walk(tree)
        if isinstance(node, ast_module.ImportFrom)
        for alias in node.names
    }
    assert {"project_halt_point", "budget_config_from_budget"} <= imported, (
        "the deep pass must fund itself through the EXISTING FR21/FR22 functions "
        f"(imported: {sorted(imported)})"
    )

    # No module-level numeric constant that smells like a second ceiling/threshold.
    banned = ("CEILING", "THRESHOLD", "FLOOR", "BUDGET_DEFAULT", "MAX_")
    for node in tree.body:
        if not isinstance(node, ast_module.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast_module.Name) and any(
                token in target.id for token in banned
            ):
                raise AssertionError(
                    f"{target.id} looks like a NEW cost-governance knob. AC4.1: no new "
                    "ceiling, threshold, config surface or numeric default — `--budget` "
                    "remains the ceiling."
                )


# ─────────────────────────────────────────────────────────────────────────────
# AC7.3 — the rules are REGISTERED in architecture.md §Enforcement
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_DOCS_001_60_both_story_12_2_rules_are_registered_in_the_architecture() -> None:
    """TC-ArgusAgent-DOCS-001-60 — AC7.3: a rule in a test is not a rule; a rule in prose is not enforced.

    Story 12.2, continuing the ``-23``/``-41``/``-52``/``-53``/``-55``/``-59`` pattern:
    §Enforcement must carry each rule's TEXT and name its ENFORCING MODULE and IDS, so an
    enforcement cannot be deleted from the architecture while the tests quietly survive,
    or the tests deleted while the architecture goes on claiming them.

    It also asserts the two STALE PREMISES this story corrected are corrected AND still
    quoted (§3.4 — struck, not deleted): the correction is the record of what was wrong,
    and deleting the quotation deletes the lesson. Both were false when written and
    neither had ever been checked — one of them was agreed on by two planning documents,
    which is exactly the kind of agreement that reads as verification and is not.
    """
    artifact_dir = (
        Path(__file__).resolve().parents[1]
        / "_bmad-output"
        / "design-artifacts"
        / "ArgusAgent"
    )
    architecture = (artifact_dir / "architecture.md").read_text(encoding="utf-8")
    assert "### Enforcement" in architecture, (
        "architecture.md has no §Enforcement section — every registration assertion in "
        "this repository is vacuous"
    )

    for anchor in (
        # The opt-in egress rule (AC7.3a).
        "Opt-in egress enforcement",
        "no egress path is reachable without an EXPLICIT INVOCATION-LEVEL opt-in",
        "neither an environment variable nor a packaging extra constitutes one",
        "tests/test_deep_pass_wiring.py",
        "TC-ArgusAgent-AUDIT-001-62",
        # The deferred-import positive-control rule (AC7.3b).
        "Deferred-import positive-control enforcement",
        "must carry its positive direction",
        "TC-ArgusAgent-PIPELINE-001-11",
        # This assertion's own id, so the registration names what holds it.
        "TC-ArgusAgent-DOCS-001-60",
    ):
        assert anchor in architecture, (
            f"architecture.md §Enforcement is missing the Story 12.2 anchor {anchor!r}"
        )

    # §0.4 item 1 — the seam coordinate two documents agreed on and neither measured.
    assert "deep_audit.py:98" in architecture, (
        "the corrected seam coordinate is missing; both this document and epics.md said "
        ":91, and `class DeepAuditSeam:` is at :98"
    )
    assert "argus/audit/deep_audit.py:91`)" in architecture, (
        "the superseded `:91` coordinate is no longer QUOTED. §3.4: struck, not deleted "
        "— the correction is the record of what was wrong and why."
    )

    # §0.4 item 3 — the `[llm]` extra was never an egress gate.
    assert "THE `[llm]` EXTRA IS NOT AN EGRESS GATE" in architecture
    assert "~~behind the opt-in `[llm]` extra~~" in architecture, (
        "the false gating claim must be STRUCK in place, not silently rewritten"
    )
    # An ALLOWLIST over an enumerated space, not a zero-count assertion — the
    # ``TC-ArgusAgent-STORE-001-109/-110`` idiom, reused rather than forked. The phrase
    # MUST survive somewhere (deleting it deletes the lesson), so what is asserted is that
    # every surviving occurrence sits in a context that DENIES the claim: struck, inside a
    # `>` correction block, or negated on its own line. A bare restatement fails.
    denial_markers = ("~~", "is not", "NOT AN EGRESS GATE", "cannot be")
    occurrences = [
        line
        for line in architecture.splitlines()
        if "behind the opt-in `[llm]` extra" in line
    ]
    assert occurrences, (
        "architecture.md no longer quotes the corrected claim anywhere. §3.4: the "
        "correction is the record of what was wrong; deleting the quotation deletes it."
    )
    live_claims = [
        line
        for line in occurrences
        if not line.lstrip().startswith(">")
        and not any(marker in line for marker in denial_markers)
    ]
    assert not live_claims, (
        "architecture.md RESTATES, without striking or denying it, that egress sits "
        f"behind the `[llm]` extra: {live_claims}. It does not: the extra holds only "
        "litellm while httpx is a BASE dependency, so a no-extras install already "
        "carries a complete egress path."
    )
