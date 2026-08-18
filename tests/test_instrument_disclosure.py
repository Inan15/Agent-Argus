"""Story 11.1 / FR34 — the tool discloses its own validation status, and the disclosure expires.

Verification areas ArgusAgent-DOCS (``TC-ArgusAgent-DOCS-001-42``..``-53``, CONTINUING the
index whose high-water was ``-41``, Story 10.5), ArgusAgent-CLI (``-50``..``-51``, after
``-49``) and ArgusAgent-REPORT-002 (``-30``..``-32``, after ``-29``).

**What this file defends.** Argus states a release-readiness verdict without stating that
its own finding precision has never been independently measured. FR34's binding half is
*mechanical enforcement, not editorial discipline*: "the surface set is enumerated in a
committed test that fails on an unenumerated member". So the load-bearing assertions here
are the two CLOSURES, not the surface list:

* **Code side** (``-31``) — an ``ast`` walk of ``generate_reports``' OWN BODY. Every
  ``write_text`` call in it must receive a value produced by the disclosure helper, so a
  **fifth** report added without it turns this RED. (The ``_get_parser_for_lang`` idiom
  from ``tests/test_grammar_diagnosis.py``.)
* **Non-code side** (``-47``/``-49`` + ``tests/test_release_surface_honesty.py::-18``) — a
  registry resolved by glob. A consumer-facing surface that is not registered fails, and
  the MCP pin fires the day Story 12.6 adds an entry point.

**Why a closure and not a list.** Five hand-counted enumerations in this project were
re-measured on 2026-08-10/11 and all five were wrong; this story's own context made a
sixth (it recorded TWO test-side ``protocol_cleared=True`` occurrences — there are FOUR,
across three files; see ``_PROTOCOL_CLEARED_TEST_EXEMPTIONS``). The list is a convenience.
The closure is the contract.

**Run grade is NOT instrument status.** ``architecture.md`` §"Run grade vs instrument
status" makes merging them a stated error: it would mislabel a ``--deep`` run
heuristic-only and — far worse — make the disclosure appear to lift when a user enables a
flag. ``DOGFOOD_EXTERNALIZATION_GUARD`` is a *run-grade* sentence and is deliberately NOT
reused here (``-45``); what this story widens is the two-sided (presence AND
over-claim-absence) GUARD MECHANISM, by IMPORTING ``_affirmative_over_claims`` from
``tests/test_release_surface_honesty.py`` rather than re-authoring a substring scan that
would reopen the trailing-negation escape ``-17b`` closed.

**The expiry.** ``-46`` is the mechanised half of FR34's clause 5. The declared status must
be *not independently validated* if and only if no production call site passes
``protocol_cleared=True`` to the precision harness. When Story 13.3 passes it ``True``,
this file goes RED until the disclosure is REPLACED by the cleared statement — **that red
is the guard working**, not a defect.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

import pytest

from argus.dogfood.proof_render import DOGFOOD_EXTERNALIZATION_GUARD
from argus.verdict.negative_assurance import (
    DISCLAIMER,
    INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED,
    INSTRUMENT_DISCLOSURE_SHORT_NOT_INDEPENDENTLY_VALIDATED,
    INSTRUMENT_DISCLOSURE_SHORT_VALIDATED,
    INSTRUMENT_DISCLOSURE_VALIDATED,
    INSTRUMENT_STATUS,
    InstrumentStatus,
    NegativeAssuranceError,
    render_instrument_disclosure,
)

# The over-claim detector is IMPORTED, never re-authored (Story 9.2's `-17b` documents an
# escape a naive substring scan let through: a negation trailing BEHIND the banned phrase).
from tests.test_release_surface_honesty import (  # noqa: E402
    _RELEASE_SURFACES,
    _affirmative_over_claims,
)

# The static `argus/**` import graph is IMPORTED from Story 10.5's closure, which builds it
# from source text with `ast` and NEVER executes `import argus` — a runtime walk would be
# defeated by lazy imports and would perturb the coverage figure.
from tests.test_v1_commitment_closure import (  # noqa: E402
    _ENTRY_POINTS,
    build_import_graph,
    reachable_from,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
_PACKAGE_ROOT = _REPO_ROOT / "argus"
_ARTIFACT_DIR = _REPO_ROOT / "_bmad-output" / "design-artifacts" / "ArgusAgent"
_ARCHITECTURE = _ARTIFACT_DIR / "architecture.md"

_GENERATOR = _PACKAGE_ROOT / "reports" / "generator.py"
_CLI_SOURCE = _PACKAGE_ROOT / "cli.py"

# The single write point for every report artifact, and the helper every one of its writes
# must flow through. Named here so a RENAME of either turns `-31` red rather than green.
_WRITE_POINT = "generate_reports"
_DISCLOSURE_HELPER = "_with_instrument_disclosure"

# Non-vacuity floors (E.3 — 10.3's `-39`, 10.4's `-118`, 10.5's `-39` were all guards that
# could pass by finding nothing). Measured 2026-08-11: four `write_text` calls, four report
# artifacts, 72 `argus/**` modules.
#
# ⚠️ `_MIN_WRITE_TEXT_CALLS` CORRECTED 2026-08-15 by Story 12.8 / AC3+AC9, and RE-DERIVED
# rather than lowered. `generate_reports` used to hold four copy-pasted `if`-blocks, one
# `write_text` each, so "at least 4 write_text calls" was a legitimate proxy for "the four
# reports are still written here". Story 12.8 had to introduce ONE constant naming the
# report types — there was none, which is exactly why nothing in the tool could validate a
# `--reports` token, and why this repository's own workflow shipped `vacuous-tests` — and a
# constant BESIDE four hand-written branches is a parallel list that drifts (a fifth token
# in the constant with no branch renders nothing and says nothing). So the branches became
# one loop over `RENDERED_REPORT_TYPES` and the literal count is now 1.
#
# The proxy is therefore replaced by the thing it was a proxy FOR: the population is
# `RENDERED_REPORT_TYPES` and the floor is asserted against ITS length, which cannot be
# satisfied by deleting reports. The guard is STRONGER after the change, not weaker — a
# fifth report type is now routed through `_with_instrument_disclosure` BY CONSTRUCTION
# rather than by a fifth author remembering to — and `-32`'s positive control below still
# proves `unrouted_write_text_calls` bites on an unrouted write. The write-point floor
# stays >= 1 so a write point that stops writing at all is still RED.
_MIN_WRITE_TEXT_CALLS = 1
_MIN_REPORT_ARTIFACTS = 4
_MIN_PACKAGE_MODULES = 55
_MIN_REACHABLE_MODULES = 35


# ─────────────────────────────────────────────────────────────────────────────────────
# The non-code surface registry (AC3.3/AC3.4/AC3.5, AC5.1)
# ─────────────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class _Surface:
    """A consumer-facing listing/note surface that must carry the disclosure.

    ``form`` is ``"full"`` or ``"short"``. A ``"short"`` surface is a ONE-LINE summary
    field where a multi-sentence paragraph does not fit; the shortened text is itself a
    constant and ``-48`` asserts it is a SUBSTRING of the full one, never an independently
    authored sentence (AI-E9-7: never publish a prose copy of a pinned figure).
    """

    path: str
    form: str
    reason: str


_DISCLOSURE_SURFACES: tuple[_Surface, ...] = (
    _Surface(
        "README.md",
        "full",
        "`readme = \"README.md\"` in pyproject.toml — this file IS the PyPI page body, "
        "the long description a stranger reads before installing.",
    ),
    _Surface(
        "CHANGELOG.md",
        "full",
        "the release note; a release is where a project describes itself to strangers.",
    ),
    _Surface(
        "pyproject.toml",
        "short",
        "`[project].description` is the ONE-LINE PyPI summary shown beside the package "
        "name in an index listing; a four-sentence paragraph cannot go there.",
    ),
    _Surface(
        "action.yml",
        "short",
        "the top-level `description:` is the GitHub Marketplace listing summary, one "
        "line, rendered under the action's name.",
    ),
)

# The `### ` section this story adds to `CHANGELOG.md`. Registered here as well as in
# `tests/test_release_surface_honesty.py::_NOTE_SECTIONS`, which pins section ORDER.
_NOTE_SECTION = (
    "### Disclosed — Argus now states its own validation status on every verdict surface"
)

# MCP surfaces registered as carrying the disclosure.
#
# ~~EMPTY TODAY, deliberately: measured 2026-08-11, `mcp|model.context.protocol` has ZERO
# hits across `argus/`, `pyproject.toml` and `action.yml`. FR35 / Story 12.6 builds that
# surface; 11.1 must NOT build it.~~ (§3.4 struck, not deleted.) POPULATED 2026-08-15 by
# Story 12.6, which built it. `-49` was RED on the first commit of `argus/mcp/__init__.py`,
# exactly as designed — that red was the guard working.
#
# Each entry is a file the MCP scan resolves. They discharge FR34 in two different ways and
# the assertion below derives which, rather than taking a per-file declaration:
#
#   * `pyproject.toml` — a LISTING surface, already registered in `_DISCLOSURE_SURFACES`
#     above as the `short` form. It became an MCP hit because `[project.scripts]` now names
#     `argus-mcp`; it carries the disclosure TEXT, and `-47`/`-51` already assert that.
#   * `argus/__init__.py`, `argus/mcp/__init__.py` — package docstrings that name the new
#     alias and the adapter. Neither renders a verdict, so neither owes a disclosure; the
#     derived rule below says so mechanically instead of taking that on trust.
#   * `argus/mcp/protocol.py` — renders BOTH the `tools/list` description and every
#     verdict-bearing tool result, and routes both through the disclosure helper.
#   * `argus/mcp/server.py` — the stdin→stdout shell. It renders no verdict text itself;
#     it calls `protocol`.
_MCP_DISCLOSURE_SURFACES: tuple[str, ...] = (
    "argus/__init__.py",
    "argus/mcp/__init__.py",
    "argus/mcp/protocol.py",
    "argus/mcp/server.py",
    "pyproject.toml",
)

# The verdict-render vocabulary the routing closure is derived from: the two helpers by
# which any surface in this repository describes a verdict in words. A function that calls
# either is describing a verdict and therefore owes the FR34 disclosure; a function that
# calls neither owes nothing. Deriving the obligation this way is what makes `-49` a
# CLOSURE rather than a list — a SECOND verdict-rendering function added to an MCP surface
# without the disclosure turns it red with no edit here, which is `-31`'s device
# (`unrouted_write_text_calls`) applied to this seam.
_VERDICT_RENDER_CALLS: tuple[str, ...] = ("summary_line", "render_ship_readiness")
_DISCLOSURE_RENDERER = "render_instrument_disclosure"

# Non-vacuity floor for `-49`'s registered-surface loop (E.3). At least one function across
# the registered surfaces must actually render a verdict AND route it through the helper; a
# rename or a module move that emptied both sets would otherwise leave the loop green while
# proving nothing at all — which is the state the loop was in before 2026-08-15, when it
# carried `# pragma: no cover - empty until 12.6` and had never executed.
_MIN_MCP_DISCLOSURE_ROUTES = 1

_MCP_PATTERN = re.compile(r"mcp|model.context.protocol", re.IGNORECASE)

# Run-scoped tokens the instrument-status text must NEVER contain (AC1.4). Instrument
# status varies per TOOL VERSION and is removed by Epic 13 clearing the gate; run grade
# varies per RUN and is removed by engaging the deep pass. A reader who can conclude that
# enabling a flag lifts the disclosure has been told something false.
_RUN_SCOPED_TOKENS: tuple[str, ...] = (
    "demo-heuristic-only",
    "heuristic-only",
    "tier-a",
    "--deep",
    "deep pass",
    "deep audit",
    "grade:",
    "this run",
)

# The `NegativeAssuranceVerdict` forbidden stems (AC1.5) — cheap insurance so the constant
# stays safe if a later story ever does persist it inside the hashed payload.
_FORBIDDEN_STEMS: tuple[str, ...] = (
    "certif",
    "is correct",
    "proven",
    "guarantee",
    "defect-free",
    "bug-free",
    "passed",
)

# Anchor text (never a line number — `test_v1_commitment_closure.py::-31`'s standing rule)
# that the current-state disclosure must carry so a reader learns what would END it.
# AMENDED 2026-08-17: anchored on the CONDITION, not the internal reference "Epic 13",
# which ships to end users in a published build. NOT weakened -- a removal condition must
# still be named and "nothing else removes it" must still be present.
_REMOVAL_CONDITION_ANCHORS: tuple[str, ...] = (
    ">=80% precision gate",
    "removed only when",
    "nothing else removes it",
)

# Test files that legitimately pass `protocol_cleared=True`, exempted BY NAME with their
# reason (AC2.2). MEASURED 2026-08-11 with `protocol_cleared_call_sites`, and this is a
# DIVERGENCE from the story context, recorded rather than quietly adopted: the story named
# TWO occurrences in ONE file (`test_dogfood_plan.py:406,410`), but `:406` passes False and
# the real CALL SITES are THREE across TWO files — `test_dogfood_plan.py` once and
# `test_precision_replay.py` twice. A sixth hand-counted enumeration in this project was
# wrong, which is precisely why the contract is the closure below and not this list.
_PROTOCOL_CLEARED_TEST_EXEMPTIONS: dict[str, str] = {
    "tests/test_dogfood_plan.py": (
        "TC-ArgusAgent-DOGFOOD-001-12 proves the flip PATH is reachable (N>=5 + high "
        "precision + protocol_cleared=True) so the provisional gate cannot be dismissed "
        "as unreachable-by-construction."
    ),
    "tests/test_precision_replay.py": (
        "TC-ArgusAgent-PRECISION-001-08/-09 prove the N>=5 floor binds even when "
        "protocol_cleared=True is claimed, and that the flip needs all three conditions."
    ),
    "tests/test_adjudication_record.py": (
        "Story 13.2 / AC6, AC7. TC-ArgusAgent-PRECISION-001-49/-52 pass protocol_cleared=True "
        "to prove the gate is REFUSED anyway — once over a NON-REPRODUCIBLE corpus carrying a "
        "full sweep of TP judgements (§4's determinism precondition binds before the "
        "arithmetic), and once over the live committed record, where 31 UNADJUDICATED rows "
        "must yield Unevaluable rather than a number. Neither clears anything."
    ),
    "tests/test_gate_flip_path.py": (
        "Story 13.2 / AC1. TC-ArgusAgent-PRECISION-001-32/-35 REPRODUCE the two defects "
        "measured on bc55e36 — an injected 2-member registry reporting N=7, and a corpus "
        "emitting nothing reporting precision=1/1 / provisional=False / 'cleared' — and "
        "both reproductions require protocol_cleared=True, because that flag was the ONLY "
        "thing standing between this repository and a false cleared claim. The guards "
        "assert the gate is REFUSED; none of them clears it."
    ),
}


# ─────────────────────────────────────────────────────────────────────────────────────
# Pure analyzers — every one of them is exercised on synthetic input by a positive control
# ─────────────────────────────────────────────────────────────────────────────────────


def unrouted_write_text_calls(
    source: str, function: str, helper: str
) -> tuple[tuple[int, str], ...]:
    """Every ``write_text`` call inside *function* whose value did NOT come from *helper*.

    The closure device for AC4.1. Parsing the write point's OWN BODY closes the CLASS —
    a fifth report added without the helper is caught — where a list of four report names
    closes only today's instances. Raises ``SyntaxError`` (from ``ast.parse``) or returns
    a sentinel via :func:`write_text_call_count` being zero if the function is renamed or
    moved, which ``-31``'s non-vacuity floor turns into a RED rather than a silent green.
    """
    tree = ast.parse(source)
    unrouted: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != function:
            continue
        for call in ast.walk(node):
            if not isinstance(call, ast.Call):
                continue
            if not (
                isinstance(call.func, ast.Attribute) and call.func.attr == "write_text"
            ):
                continue
            value = call.args[0] if call.args else None
            routed = (
                isinstance(value, ast.Call)
                and isinstance(value.func, ast.Name)
                and value.func.id == helper
            )
            if not routed:
                unrouted.append((call.lineno, ast.dump(call.func)))
    return tuple(unrouted)


def write_text_call_count(source: str, function: str) -> int:
    """How many ``write_text`` calls live inside *function* — the non-vacuity counter.

    A guard that walks source goes green by finding nothing. A rename of the write point,
    a move of the module, or an ``ast`` shape change must make this ZERO and therefore
    turn ``-31`` RED (E.3 — 10.4's ``-118`` precedent).
    """
    tree = ast.parse(source)
    found = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function:
            for call in ast.walk(node):
                if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute):
                    if call.func.attr == "write_text":
                        found += 1
    return found


def protocol_cleared_call_sites(source: str) -> tuple[int, ...]:
    """Line numbers of every CALL that actually passes ``protocol_cleared=True``.

    The closure device for AC2.2, and it is deliberately an ``ast`` walk rather than a
    substring scan. A substring scan reports every module that MENTIONS the literal —
    ``replay_harness.py``'s own docstring and this repository's honesty comments both do,
    and both are the opposite of a call site. Measuring the mention rather than the call
    would have declared the gate cleared by four modules that never clear anything.
    """
    sites: list[int] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if keyword.arg != "protocol_cleared":
                continue
            value = keyword.value
            if isinstance(value, ast.Constant) and value.value is True:
                sites.append(node.lineno)
    return tuple(sites)


def mcp_surface_tokens(candidates: dict[str, str]) -> tuple[str, ...]:
    """Every candidate (label → text) that mentions MCP, in either its label or its body.

    The closure for AC4.3. It does not know what an MCP surface looks like; it knows that
    one cannot be introduced without the token appearing somewhere in the package, the
    distribution metadata or the action listing.
    """
    hits = []
    for label in sorted(candidates):
        if _MCP_PATTERN.search(label) or _MCP_PATTERN.search(candidates[label]):
            hits.append(label)
    return tuple(hits)


def functions_calling(source: str, names: tuple[str, ...]) -> frozenset[str]:
    """Every function in *source* that CALLS one of *names* (PURE, ``ast``).

    The analyzer behind `-49`'s corrected registered-surface closure, and it is the same
    device `-31` uses on ``generate_reports``: parse the module and ask which functions
    ROUTE through a named helper, rather than asking whether a string appears anywhere in
    the file.

    A nested function is attributed to itself, which is what makes the closure honest: a
    verdict renderer hidden inside another function still owes the disclosure.
    """
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for call in ast.walk(node):
            if not isinstance(call, ast.Call):
                continue
            func = call.func
            called = (
                func.id
                if isinstance(func, ast.Name)
                else func.attr
                if isinstance(func, ast.Attribute)
                else ""
            )
            if called in names:
                found.add(node.name)
    return frozenset(found)


def _package_sources() -> dict[str, str]:
    """Every tracked ``argus/**`` module, as {repo-relative posix path: source}."""
    return {
        path.relative_to(_REPO_ROOT).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(_PACKAGE_ROOT.rglob("*.py"))
    }


def _expected_text(surface: _Surface, status: InstrumentStatus) -> str:
    return render_instrument_disclosure(status, short=surface.form == "short")


# ─────────────────────────────────────────────────────────────────────────────────────
# AC1 — ONE vocabulary, ONE module, a closed set with an exhaustive renderer
# ─────────────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_DOCS_001_42_instrument_status_is_a_closed_two_member_vocabulary() -> None:
    """TC-ArgusAgent-DOCS-001-42 — Story 11.1 / AC1.1-AC1.2: closed set, exhaustive renderer.

    Prevents the failure where a third instrument state is added and silently renders as
    "not validated" — the COMFORTABLE wrong answer. The renderer is exhaustive over the
    enum and RAISES a typed error on an unregistered member (the ``exit_code_for_verdict``
    house pattern, AR10), never falls through to a default.
    """
    assert [member.name for member in InstrumentStatus] == [
        "NOT_INDEPENDENTLY_VALIDATED",
        "VALIDATED",
    ], "the instrument-status vocabulary is CLOSED at exactly two members (FR34.1/FR34.4)"

    # Every registered member renders, in both forms, without falling through.
    for member in InstrumentStatus:
        for short in (False, True):
            rendered = render_instrument_disclosure(member, short=short)
            assert rendered and rendered.strip() == rendered

    # Positive control: an unregistered member RAISES rather than rendering a default.
    with pytest.raises(NegativeAssuranceError) as excinfo:
        render_instrument_disclosure("not-a-member")  # type: ignore[arg-type]
    assert "instrument status" in str(excinfo.value).lower()

    # The declared status is one of the closed members, and it is today's honest one.
    assert INSTRUMENT_STATUS is InstrumentStatus.NOT_INDEPENDENTLY_VALIDATED


def test_TC_ArgusAgent_DOCS_001_43_the_disclosure_says_what_FR34_requires() -> None:
    """TC-ArgusAgent-DOCS-001-43 — Story 11.1 / AC1.3-AC1.5: content, scope and honesty.

    FR34's Content clause has three parts and each is asserted separately, because a
    disclosure that states the status without the corpus, or the corpus without what would
    remove it, is the half-disclosure this story exists to prevent.
    """
    current = render_instrument_disclosure(INSTRUMENT_STATUS)
    lowered = current.lower()

    # (a) the validation state, (b) the corpus it rests on, (c) what would remove it.
    assert "has not been independently validated" in lowered
    assert "dogfood corpus" in lowered and "self-audit" in lowered
    for anchor in _REMOVAL_CONDITION_ANCHORS:
        assert anchor.lower() in lowered, (
            f"the disclosure must name its own removal condition: {anchor!r} (FR34.4)"
        )

    # AC1.4 — instrument-scoped, NEVER run-scoped. A reader must not be able to conclude
    # that enabling a flag lifts it.
    for token in _RUN_SCOPED_TOKENS:
        for text in (
            INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED,
            INSTRUMENT_DISCLOSURE_VALIDATED,
        ):
            assert token not in text.lower(), (
                f"instrument status must not mention the run-scoped token {token!r}: run "
                "grade is removed by engaging the deep pass, instrument status ONLY by "
                "Epic 13 clearing the gate (architecture.md, run-grade vs instrument-status)"
            )

    # AC1.5 — no forbidden stem, in EITHER member's text.
    for text in (
        INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED,
        INSTRUMENT_DISCLOSURE_VALIDATED,
        INSTRUMENT_DISCLOSURE_SHORT_NOT_INDEPENDENTLY_VALIDATED,
        INSTRUMENT_DISCLOSURE_SHORT_VALIDATED,
    ):
        for stem in _FORBIDDEN_STEMS:
            assert stem not in text.lower(), f"over-claim stem {stem!r} in {text!r}"


def test_TC_ArgusAgent_DOCS_001_44_the_disclosure_is_pure_and_is_not_the_run_grade() -> None:
    """TC-ArgusAgent-DOCS-001-44 — Story 11.1 / AC1.6 + DN-4: PURE, and NOT the dogfood sentence.

    Two failures in one place because they are the same mistake seen from two sides.
    **Purity (AR8):** a disclosure that read a clock or a host path would make the four
    report artifacts non-byte-stable (NFR-P1) and could leak a path (NFR-S1).
    **DN-4:** ``DOGFOOD_EXTERNALIZATION_GUARD`` describes how THIS RUN was configured;
    reusing it on the CLI would state a per-run fact as a per-tool fact, and would make the
    disclosure appear to lift when a user enables a flag.
    """
    texts = (
        INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED,
        INSTRUMENT_DISCLOSURE_VALIDATED,
    )
    for text in texts:
        # PURE by construction: a fixed constant with NO interpolation.
        assert "{" not in text and "}" not in text and "%s" not in text
        assert text != DISCLAIMER, "FR34 is a SIBLING of FR17's disclaimer, not a copy"
        assert text not in DOGFOOD_EXTERNALIZATION_GUARD
        assert DOGFOOD_EXTERNALIZATION_GUARD not in text

    # The pure half imports nothing impure. Asserted over the module's own import list so
    # a later story cannot reach for `datetime`/`uuid`/`random`/`httpx` to enrich it.
    module_source = (_PACKAGE_ROOT / "verdict" / "negative_assurance.py").read_text(
        encoding="utf-8"
    )
    imported: set[str] = set()
    for node in ast.walk(ast.parse(module_source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    forbidden = imported & {
        "datetime",
        "time",
        "uuid",
        "random",
        "os",
        "subprocess",
        "httpx",
        "requests",
        "socket",
    }
    assert not forbidden, f"the PURE disclosure module reached for {sorted(forbidden)}"


# ─────────────────────────────────────────────────────────────────────────────────────
# AC2 — the disclosure does not fork the state the tool already computes
# ─────────────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_DOCS_001_45_the_precision_harness_is_not_on_the_user_path() -> None:
    """TC-ArgusAgent-DOCS-001-45 — Story 11.1 / AC2.1: the harness stays off every install's critical path.

    ``argus/precision/replay_harness.py`` performs a module-level ``sys.path.insert`` of
    ``<repo>/tests/cartridges`` and then ``from _registry import ...``. That is exactly the
    wheel defect Story 11.5 exists to fix (5 of 71 wheel modules fail to import). Reaching
    the disclosure's status BY IMPORTING the harness would move a latent packaging defect
    onto every user's start-up path and turn it into a crash-on-start.

    The walk is STATIC and never executes ``import argus`` (Story 10.5's DN-6): a runtime
    walk is defeated by lazy imports and would perturb the coverage figure.
    """
    graph = build_import_graph(_PACKAGE_ROOT)
    assert len(graph) >= _MIN_PACKAGE_MODULES, (
        "the static import graph collapsed — a package move or an ast.parse failure must "
        "turn this RED, not silently green"
    )

    harness = "argus.precision.replay_harness"
    # The entry-point half of this list is DERIVED from `[project.scripts]` (Story 12.6),
    # not written down: the hazard is "a user-facing start-up path reaches the harness", and
    # on 2026-08-15 this distribution gained a SECOND console entry point. A hand-written
    # list would have gone on checking `argus.cli` and left the new start-up path — the one
    # an agent host launches — entirely outside the guard.
    entry_points = (
        *_ENTRY_POINTS,
        "argus.reports.generator",
        "argus.verdict.negative_assurance",
    )
    assert len(entry_points) >= 4, "the entry-point derivation collapsed"
    for entry in entry_points:
        reachable = reachable_from(graph, entry)
        assert harness not in reachable, (
            f"{harness} became reachable from {entry}. Its module-level sys.path insert + "
            "`from _registry import ...` is Story 11.5's wheel defect; putting it on a "
            "user-facing path converts a packaging defect into a crash-on-start (DN-3)."
        )

    # Non-vacuity, both directions: the walk really does resolve edges.
    cli_reachable = reachable_from(graph, "argus.cli")
    assert len(cli_reachable) >= _MIN_REACHABLE_MODULES
    assert "argus.pipeline" in cli_reachable, "the reachability walk found no edges at all"


def test_TC_ArgusAgent_DOCS_001_46_the_declared_status_agrees_with_the_harness() -> None:
    """TC-ArgusAgent-DOCS-001-46 — Story 11.1 / AC2.2-AC2.3: THE EXPIRY, mechanised.

    AR7/§3.3 forbid a second mechanism where one exists. The instrument's gate state is
    computed today by ``compute_precision(..., protocol_cleared=...)``; the disclosure
    declares it WITHOUT importing that module (``-45``), so this guard is what stops the
    two from silently disagreeing.

    **When Story 13.3 passes ``protocol_cleared=True`` from a production call site, this
    test goes RED. THAT RED IS THE GUARD WORKING.** The fix is not to widen the exemptions:
    it is to REPLACE the disclosure with ``InstrumentStatus.VALIDATED``'s cleared statement
    (FR34.4 — the surface never becomes silent).
    """
    production_sites = sorted(
        rel
        for rel, source in _package_sources().items()
        if protocol_cleared_call_sites(source)
    )
    assert not production_sites, (
        f"a production call site now passes protocol_cleared=True: {production_sites}. "
        "THIS RED IS THE GUARD WORKING (Story 13.3). The instrument's precision gate has "
        "cleared, so REPLACE the disclosure with InstrumentStatus.VALIDATED's text on every "
        "registered surface — never delete it (FR34.4)."
    )
    assert INSTRUMENT_STATUS is InstrumentStatus.NOT_INDEPENDENTLY_VALIDATED

    # The test-side occurrences are exempted BY NAME WITH THEIR REASON, in both directions:
    # an unregistered new one fails, and a registered one that disappeared fails too.
    measured = {
        path.relative_to(_REPO_ROOT).as_posix()
        for path in sorted((_REPO_ROOT / "tests").rglob("*.py"))
        if path.name != Path(__file__).name
        and protocol_cleared_call_sites(path.read_text(encoding="utf-8"))
    }
    registered = set(_PROTOCOL_CLEARED_TEST_EXEMPTIONS)
    assert measured == registered, (
        "the protocol_cleared=True exemption set drifted.\n"
        f"  unregistered: {sorted(measured - registered)}\n"
        f"  stale:        {sorted(registered - measured)}\n"
        "Each exemption must be named WITH its reason — an unnamed one is an oversight."
    )
    assert measured, "the exemption scan found nothing — it is not scanning the tests"
    assert all(_PROTOCOL_CLEARED_TEST_EXEMPTIONS.values()), "every exemption carries a reason"


# ─────────────────────────────────────────────────────────────────────────────────────
# AC3/AC4 — every surface that emits a verdict emits the disclosure, and the set is CLOSED
# ─────────────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_DOCS_001_47_every_registered_listing_surface_carries_the_disclosure() -> None:
    """TC-ArgusAgent-DOCS-001-47 — Story 11.1 / AC3.3-AC3.5, AC5.1: present, and never retyped.

    The copies on ``README.md`` / ``CHANGELOG.md`` / ``pyproject.toml`` / ``action.yml`` are
    COMPARED AGAINST THE CONSTANT rather than transcribed (AI-E9-7: a prose copy of an
    enumerable fact drifts — this project has hit that class five times). This is also
    ``-19``'s shape: ``-17`` proves nothing bad was ADDED; this proves the honest language
    is still THERE, so AC3 cannot be satisfied by deleting the sentence.
    """
    assert _DISCLOSURE_SURFACES, "the surface registry is empty"
    for surface in _DISCLOSURE_SURFACES:
        path = _REPO_ROOT / surface.path
        assert path.is_file(), f"registered disclosure surface is missing: {surface.path}"
        expected = _expected_text(surface, INSTRUMENT_STATUS)
        text = path.read_text(encoding="utf-8")
        flat = " ".join(text.split())
        assert " ".join(expected.split()) in flat, (
            f"{surface.path} does not carry the instrument-status disclosure "
            f"({surface.form} form). It is registered because: {surface.reason}\n"
            f"  expected: {expected!r}"
        )
        assert surface.reason, "every registered surface states WHY it is one"

    # The release note's new section is registered where `-16` pins ORDER, not just
    # membership — an unregistered `### ` heading fails there, in the right position.
    changelog = (_REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert _NOTE_SECTION in changelog, "CHANGELOG.md lost the registered disclosure section"

    # Closure hand-off: every listing surface here is also covered by the release-surface
    # over-claim guard, so widening one registry cannot silently narrow the other.
    for surface in _DISCLOSURE_SURFACES:
        assert surface.path in _RELEASE_SURFACES, (
            f"{surface.path} carries the disclosure but is not in _RELEASE_SURFACES, so "
            "tests/test_release_surface_honesty.py::-17 does not scan it for over-claims"
        )


def test_TC_ArgusAgent_DOCS_001_48_the_short_form_is_a_substring_of_the_full_one() -> None:
    """TC-ArgusAgent-DOCS-001-48 — Story 11.1 / AC3.5: the shortening is a RELATION, not a rewrite.

    Two surfaces are one-line summary fields that cannot hold a four-sentence paragraph.
    The shortened text is therefore itself a constant, and its relation to the full text is
    ASSERTED — never an independently authored second sentence, which is the drift site
    AI-E9-7 names.
    """
    for member in InstrumentStatus:
        full = render_instrument_disclosure(member)
        short = render_instrument_disclosure(member, short=True)
        assert short in full, (
            f"the short form for {member.name} is not a substring of the full text — it "
            "is an independent sentence that can drift away from the constant"
        )
        assert len(short) < len(full)
        assert short.strip()


def test_TC_ArgusAgent_DOCS_001_49_no_mcp_surface_escapes_the_disclosure() -> None:
    """TC-ArgusAgent-DOCS-001-49 — Story 11.1 / AC4.3: the closure fires the day 12.6 lands.

    The MCP surface DOES NOT EXIST (measured 2026-08-11: zero hits for
    ``mcp|model.context.protocol`` across ``argus/``, ``pyproject.toml`` and ``action.yml``)
    and **this story must not create one** — FR35 is Story 12.6's, and an unspecified flag
    or entry point would also fail ``tests/test_invocation_contract.py``.

    So the AC is satisfied by the CLOSURE, not by the surface: when 12.6 adds an MCP entry
    point, module or extra, this goes RED until that surface is registered in
    ``_MCP_DISCLOSURE_SURFACES`` *and* carries the disclosure.

    ⚠️ **CORRECTED 2026-08-15 by Story 12.6, and recorded rather than fixed quietly.** The
    registered-surface loop below had NEVER EXECUTED — it carried
    ``# pragma: no cover - empty until 12.6`` over an empty registry — and as written it
    asserted that the literal short disclosure text was a SUBSTRING OF THE REGISTERED
    MODULE'S SOURCE. Satisfying that would have required pasting a transcribed copy of the
    constant into ``argus/mcp/**``: the exact AI-E9-7 drift the FR34 regime exists to
    prevent, demanded by the guard that exists to prevent it, and the same *"guard whose
    observable is wrong"* class Epic 11 produced five times (retro §3.1). It was written in
    good faith for a surface nobody could see yet, and it was wrong about the one thing
    that mattered: FR34 asks a code surface to ROUTE its verdict through the helper, not to
    contain the sentence.

    The corrected assertion is therefore three things, all derived:

    1. **No transcription.** No registered Python module may contain the constant's text at
       all. The old assertion demanded the opposite.
    2. **Routing, by ``ast``.** Every function on a registered surface that renders a
       verdict — derived as *"calls something in ``_VERDICT_RENDER_CALLS``"*, not declared
       per file — must also call ``render_instrument_disclosure``. This is `-31`'s
       ``unrouted_write_text_calls`` device at this seam, so a SECOND verdict-rendering
       function added later without the disclosure turns this red with no edit here.
    3. **A listing surface discharges by carrying the text**, which is what a
       ``pyproject.toml`` description can do and a Python module must not.

    Plus a non-vacuity floor, because a loop that walks source goes green by finding
    nothing — which is precisely how it spent its first four days.
    """
    candidates = dict(_package_sources())
    for extra in ("pyproject.toml", "action.yml"):
        candidates[extra] = (_REPO_ROOT / extra).read_text(encoding="utf-8")
    assert len(candidates) >= _MIN_PACKAGE_MODULES, (
        "the MCP scan resolved almost nothing — a package move must turn this RED"
    )

    hits = mcp_surface_tokens(candidates)
    unregistered = sorted(set(hits) - set(_MCP_DISCLOSURE_SURFACES))
    assert not unregistered, (
        f"an MCP surface appeared and is not a registered disclosure surface: {unregistered}. "
        "This is Story 12.6 (FR35), whose sprint-status entry already commits it to "
        "'Carries the FR34 disclosure'. Register the surface in _MCP_DISCLOSURE_SURFACES "
        "and make it emit render_instrument_disclosure(INSTRUMENT_STATUS) — THIS RED IS THE "
        "GUARD WORKING."
    )
    assert _MCP_DISCLOSURE_SURFACES, (
        "the MCP registry was emptied while MCP surfaces exist on the tree; the loop below "
        "would then prove nothing"
    )
    listing_surfaces = {surface.path for surface in _DISCLOSURE_SURFACES}
    full = render_instrument_disclosure(INSTRUMENT_STATUS)
    short = render_instrument_disclosure(INSTRUMENT_STATUS, short=True)
    routed_total = 0

    for registered in _MCP_DISCLOSURE_SURFACES:
        assert registered in candidates, (
            f"{registered} is registered as an MCP disclosure surface but the scan no "
            "longer resolves it — a registry entry the population cannot see proves nothing"
        )
        source = candidates[registered]

        if registered in listing_surfaces:
            # A one-line listing field: it CARRIES the text, compared against the constant
            # (`-47`/`-51` hold this too; asserted here so the hand-off cannot be silently
            # broken from either side).
            assert short in source, (
                f"{registered} is a registered listing surface and no longer carries the "
                "disclosure"
            )
            continue

        assert registered.endswith(".py"), (
            f"{registered} is neither a Python module nor a registered listing surface, so "
            "this closure has no way to say how it discharges FR34. Register it in "
            "_DISCLOSURE_SURFACES too, or make it a module."
        )
        for text in (full, short):
            assert text not in source, (
                f"{registered} TRANSCRIBES the instrument-status constant. AI-E9-7: never "
                "publish a prose copy of a pinned constant — it goes stale the day Epic 13 "
                "clears the precision gate, and the surface then publishes a disclosure "
                "the tool has retired. Call render_instrument_disclosure(INSTRUMENT_STATUS)."
            )
        renders_verdict = functions_calling(source, _VERDICT_RENDER_CALLS)
        routes_disclosure = functions_calling(source, (_DISCLOSURE_RENDERER,))
        unrouted = sorted(renders_verdict - routes_disclosure)
        assert not unrouted, (
            f"{registered}: {unrouted} render a verdict and do NOT route it through "
            f"{_DISCLOSURE_RENDERER}. FR34: no verdict surface ships without the "
            "disclosure. Add the call; do not paste the text."
        )
        routed_total += len(renders_verdict & routes_disclosure)

    assert routed_total >= _MIN_MCP_DISCLOSURE_ROUTES, (
        f"no registered MCP surface renders a verdict at all ({routed_total} routed "
        f"function(s), floor {_MIN_MCP_DISCLOSURE_ROUTES}). Either the renderers were "
        "renamed out of _VERDICT_RENDER_CALLS or the surface stopped emitting verdicts — "
        "and this loop is back to proving nothing, which is the state it was corrected out "
        "of on 2026-08-15."
    )


def test_TC_ArgusAgent_DOCS_001_50_the_disclosure_is_two_sided_presence_and_no_over_claim() -> None:
    """TC-ArgusAgent-DOCS-001-50 — Story 11.1 / AC4.4: the widened two-sided guard bites both ways.

    ``architecture.md`` asks for the two-sided ``DOGFOOD_EXTERNALIZATION_GUARD`` (presence
    AND over-claim-phrase absence) to be WIDENED to the user-facing surface set — never a
    second mechanism. So the detector is IMPORTED from
    ``tests/test_release_surface_honesty.py``; re-authoring a blunt substring scan would
    reopen the trailing-negation escape ``-17b`` closed.

    The half ``-17`` cannot see is the Python constant itself: the disclosure is prose that
    CONTAINS a banned phrase ("independently validated") and is honest only because it is
    denied. If a later edit drops the denial, this fires.
    """
    for text in (
        INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED,
        INSTRUMENT_DISCLOSURE_VALIDATED,
        INSTRUMENT_DISCLOSURE_SHORT_NOT_INDEPENDENTLY_VALIDATED,
        INSTRUMENT_DISCLOSURE_SHORT_VALIDATED,
    ):
        assert not _affirmative_over_claims(text), (
            f"the instrument-status text ASSERTS an over-claim: {text!r}"
        )

    # Positive control, both directions, over SYNTHETIC input only (E.4) — never by
    # editing a real surface during a test.
    assert _affirmative_over_claims(
        "Argus's own finding precision has been independently validated."
    ), "the imported detector stopped biting; the two-sided guard is now one-sided"
    assert not _affirmative_over_claims(
        INSTRUMENT_DISCLOSURE_NOT_INDEPENDENTLY_VALIDATED
    )


def test_TC_ArgusAgent_DOCS_001_51_flipping_the_token_turns_the_surfaces_red() -> None:
    """TC-ArgusAgent-DOCS-001-51 — Story 11.1 / AC5.1-AC5.2: the guard cannot go vacuous.

    A presence guard keyed on a hardcoded string is trivially satisfiable: change the
    string and the assertion evaporates. This is the epic AC's "cannot pass vacuously once
    the token changes" clause — the surfaces are checked against **the rendered text for
    the CURRENT status**, so rendering the *validated* member must make every one of them
    RED. That is what makes FR34.4 mechanical: the disclosure is REPLACED, never deleted.
    """
    flipped = InstrumentStatus.VALIDATED
    assert flipped is not INSTRUMENT_STATUS

    for surface in _DISCLOSURE_SURFACES:
        text = " ".join((_REPO_ROOT / surface.path).read_text(encoding="utf-8").split())
        expected_now = " ".join(_expected_text(surface, INSTRUMENT_STATUS).split())
        expected_flipped = " ".join(_expected_text(surface, flipped).split())
        assert expected_now in text
        assert expected_flipped not in text, (
            f"{surface.path} already satisfies the VALIDATED text, so the presence guard "
            "would pass whichever status is declared — it is keyed on nothing"
        )


def test_TC_ArgusAgent_DOCS_001_52_the_enforcement_rule_is_registered_in_the_architecture() -> None:
    """TC-ArgusAgent-DOCS-001-52 — Story 11.1 / AC5.4: a rule that lives only in a test is not a rule.

    The ``-23``/``-29``/``-41`` pattern: §Enforcement must carry the FR34 rule text and name
    this module and its ids, so the enforcement cannot be deleted from the architecture
    while the test quietly survives (or vice versa).
    """
    architecture = _ARCHITECTURE.read_text(encoding="utf-8")
    assert "### Enforcement" in architecture
    for anchor in (
        "Instrument-status enforcement",
        "tests/test_instrument_disclosure.py",
        "TC-ArgusAgent-DOCS-001-42",
        "no verdict surface ships without disclosure",
    ):
        assert anchor in architecture, (
            f"architecture.md §Enforcement is missing the FR34 registration anchor {anchor!r}"
        )
