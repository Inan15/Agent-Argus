"""Story 8.4 — the release note (``CHANGELOG.md``) and the package front door cannot rot.

Verification area ArgusAgent-DOCS (``TC-ArgusAgent-DOCS-001-NN`` — a NEW area; no ``DOCS``
tests existed before this story). Drivers: DR-8 (publish the consumer-visible delta),
RS-4a (the package front door), and the Epic-8 outcome statement — *no published Argus
artifact contradicting the shipped contract*.

A hand-written release note is correct exactly once. It is, by construction, the NEXT
published artifact able to contradict the shipped contract — which is the defect class
this epic exists to delete, so the note does not get to be the exception. These tests
IMPORT the shipped constants and RENDER the shipped strings through real
``evaluate_verdict`` folds, then assert the note still says what the code does.

Nothing here needs a network, an LLM, a ``.argus/`` write or a new dependency (NFR-D2):
the note is a file on disk and the contract is a pure fold. Rot-check precedent:
``tests/test_dogfood_proof.py``'s committed-artifact check.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from argus.cost.exhaustion import HaltReport, build_floor_report
from argus.detectors.base import FindingDraft, build_recording
from argus.ledger.coverage_ledger import CoverageDepth, CoverageLedger, grade_entry
from argus.ledger.critical_subsystems import (
    CRITICAL_SUBSYSTEMS_SCHEMA_VERSION,
    CriticalSubsystemSet,
)
from argus.ledger.recording import Recording
from argus.models import AuditRequest
from argus.reports.generator import render_final_verdict_report
from argus.reports.plain_english import render_depth_meaning, render_ship_readiness
from argus.verdict.negative_assurance import build_negative_assurance_verdict
from argus.verdict.verdict_gate import (
    INSUFFICIENT_COVERAGE_FLOOR,
    RELEASE_READY_DEEP_THRESHOLD,
    VERDICT_SCHEMA_VERSION,
    AuditVerdict,
    DecisionRow,
    Verdict,
    evaluate_verdict,
    exit_code_for_verdict,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
_CHANGELOG = _REPO_ROOT / "CHANGELOG.md"
_FRONT_DOOR = _REPO_ROOT / "argus" / "__init__.py"


def _note() -> str:
    assert _CHANGELOG.is_file(), (
        f"the release note is missing: {_CHANGELOG.relative_to(_REPO_ROOT).as_posix()}"
    )
    return _CHANGELOG.read_text(encoding="utf-8")


#: A Markdown cell separator: a ``|`` that is NOT escaped. The note legitimately carries
#: escaped pipes inside cells (``` `DecisionRow \| None` ``` in the API table), and a
#: naive ``split("|")`` shifts every later cell one position left — which would silently
#: make a positional assertion read the WRONG COLUMN rather than fail.
_CELL_SEPARATOR = re.compile(r"(?<!\\)\|")


def _cells(row: str) -> list[str]:
    """The cells of one Markdown table row, so a claim is read from its own column."""
    return [cell.strip() for cell in _CELL_SEPARATOR.split(row.strip().strip("|"))]


def _cell(row: str, index: int, *, expected: int) -> str:
    """Cell ``index`` of a row asserted to have exactly ``expected`` columns.

    Positional reads must fail loudly on a reshaped table, never quietly return a
    neighbouring cell: a wrong-column read can satisfy an assertion off the *Before*
    column and report a rot as clean.
    """
    cells = _cells(row)
    assert len(cells) == expected, (
        f"expected a {expected}-column table row, got {len(cells)}: {row}"
    )
    return cells[index]


def _flat(text: str) -> str:
    """Whitespace-collapsed text: the note wraps its prose, the renderer does not."""
    return " ".join(text.split())


# ── real folds, one per FR16 row (never a hand-built verdict) ──────────────────


def _ledger(deep: int, total: int) -> CoverageLedger:
    depths = [CoverageDepth.AUDITED_DEEP] * deep
    depths += [CoverageDepth.AUDITED_SHALLOW] * (total - deep)
    return CoverageLedger.build(
        [
            grade_entry(
                file_path=f"f{i}.py",
                proposed_depth=depth,
                claim_present=depth is CoverageDepth.AUDITED_DEEP,
            )
            for i, depth in enumerate(depths)
        ]
    )


def _blocking_finding() -> Recording:
    draft = FindingDraft(
        file_path="f0.py", start_line=1, end_line=1, rule_id="vacuous_test_ast", advisory=True
    )
    return build_recording(draft, depth_supported=CoverageDepth.AUDITED_SHALLOW)


# (deep, total, blocking findings) — one shape per FR16 row. The ratios are the ones
# the note quotes (`3/10` against the `3/5` threshold), so the rendered surfaces below
# are comparable to the note's published text without a substitution.
_ROW_SHAPES = (
    (1, 10, 0),  # below the floor
    (9, 10, 1),  # a blocking finding
    (9, 10, 0),  # gates met
    (3, 10, 0),  # a gate unmet, nothing found
)


def _live_cases() -> dict[DecisionRow, tuple[AuditVerdict, CoverageLedger]]:
    """One REAL ``evaluate_verdict`` result per FR16 row — the fold decides, not the test.

    The ledger is carried alongside its verdict because ``render_final_verdict_report``
    needs both, and re-deriving it would let the two drift.
    """
    cases: dict[DecisionRow, tuple[AuditVerdict, CoverageLedger]] = {}
    for deep, total, n_findings in _ROW_SHAPES:
        ledger = _ledger(deep, total)
        verdict = evaluate_verdict(ledger, [_blocking_finding()] * n_findings)
        if verdict.decision_row is not None:
            cases[verdict.decision_row] = (verdict, ledger)
    assert set(cases) == set(DecisionRow), (
        "the four folds must cover every DecisionRow member; got "
        f"{sorted(r.value for r in cases)}"
    )
    return cases


def _live_rows() -> dict[DecisionRow, AuditVerdict]:
    return {row: verdict for row, (verdict, _) in _live_cases().items()}


def _live_callout_cases() -> dict[str, tuple[AuditVerdict, CoverageLedger]]:
    """One REAL fold per *rendered callout*, which is NOT one per FR16 row.

    Row 4's callout names the gates that were actually unmet, ``"; "``-joined, so it has
    three distinct renderings and each must be published and compared on its own. Rows
    1-3 have one each. Every verdict here is a real ``evaluate_verdict`` result — the
    fold decides which row it is, and the assertion below re-checks that it really is 4.
    """
    cases: dict[str, tuple[AuditVerdict, CoverageLedger]] = {
        row.value.removeprefix("row_")[0]: pair for row, pair in _live_cases().items()
    }
    not_deep = ("svc/auth.py",)
    row4 = {
        # (key, deep, total, critical_subsystems_all_deep)
        "4 (coverage)": (3, 10, True),
        "4 (critical)": (10, 10, False),
        "4 (both)": (3, 10, False),
    }
    del cases["4"]  # replaced by its three cause-specific variants
    for key, (deep, total, all_deep) in row4.items():
        ledger = _ledger(deep, total)
        verdict = evaluate_verdict(
            ledger,
            [],
            critical_subsystems_all_deep=all_deep,
            critical_subsystems_not_deep=() if all_deep else not_deep,
        )
        assert verdict.decision_row is DecisionRow.GATE_UNMET_NO_FINDINGS, (
            f"{key} must fold to row 4, got {verdict.decision_row}"
        )
        cases[key] = (verdict, ledger)
    return cases


def _request() -> AuditRequest:
    return AuditRequest(
        repo_path="repo", commit="HEAD", budget=100, materiality_bar="default"
    )


def _callouts(document: str) -> list[tuple[str, str]]:
    """Every GitHub alert callout in a rendered report, as ``(LEVEL, message)``."""
    blocks: list[tuple[str, str]] = []
    lines = document.splitlines()
    for i, line in enumerate(lines):
        match = re.fullmatch(r">\s*\[!([A-Z]+)]", line.strip())
        if match is None:
            continue
        body: list[str] = []
        for follower in lines[i + 1 :]:
            if not follower.startswith(">"):
                break
            body.append(follower[1:].strip())
        blocks.append((match.group(1), _flat(" ".join(body))))
    return blocks


def _verdict_callout(verdict: AuditVerdict, ledger: CoverageLedger) -> tuple[str, str]:
    """The FR16 verdict callout of a LIVE ``final-verdict.md`` render.

    Located structurally, not by matching the text under test: it is the callout that
    immediately follows the depth-meaning ``NOTE`` the generator always emits above it.
    Matching on the message would make the assertion a copy of its own subject.
    """
    request = _request()
    document = render_final_verdict_report(request, verdict, ledger, 0)
    blocks = _callouts(document)
    meaning = _flat(render_depth_meaning(request.enabled_passes))
    anchors = [i for i, (_, message) in enumerate(blocks) if message == meaning]
    assert len(anchors) == 1, (
        f"expected exactly one depth-meaning NOTE to anchor on, got {len(anchors)}"
    )
    assert anchors[0] + 1 < len(blocks), "no verdict callout follows the depth-meaning NOTE"
    return blocks[anchors[0] + 1]


#: The note publishes each row's CURRENT ship-readiness headline on one line, e.g.
#: ``- Headline row 4 after: `NOT VOUCHED — …` ``. Same current/history discipline as the
#: callouts below: a ``before`` line is laid out differently and deliberately misses.
_PUBLISHED_HEADLINE = re.compile(
    r"^- Headline row (?P<row>\d) (?:after|unchanged): `(?P<headline>.+?)`\s*$"
)


def _published_headlines() -> dict[str, str]:
    """``{row number: headline}`` as the note publishes them today."""
    found: dict[str, str] = {}
    for line in _note().splitlines():
        match = _PUBLISHED_HEADLINE.match(line)
        if match is not None:
            assert match["row"] not in found, f"headline row {match['row']} published twice"
            found[match["row"]] = match["headline"]
    return found


#: The note publishes each row's CURRENT callout on one line, level first, e.g.
#: ``- Row 4 (coverage) after: `> [!WARNING]` — Release readiness is NOT VOUCHED — …``.
#: "after" and "unchanged" are the two ways a callout can be current; a "before" line
#: deliberately does not match, so history cannot satisfy a liveness assertion.
#:
#: The optional ``(variant)`` exists because ROW 4 RENDERS THREE DIFFERENT CALLOUTS — it
#: names the gates actually unmet, ``"; "``-joined, so coverage-only, critical-only and
#: both-unmet are three distinct strings. Keying on the bare row number published one of
#: them and made the other two unpublishable (a second ``- Row 4`` line tripped the
#: duplicate guard), so two thirds of row 4 could rot with nothing failing.
_PUBLISHED_CALLOUT = re.compile(
    r"^- Row (?P<row>\d)(?: \((?P<variant>[a-z]+)\))? (?:after|unchanged): "
    r"`> \[!(?P<level>[A-Z]+)]` — (?P<message>.+?)\s*$"
)


def _published_callouts() -> dict[str, tuple[str, str]]:
    """``{case key: (LEVEL, message)}`` as the note publishes them today."""
    found: dict[str, tuple[str, str]] = {}
    for line in _note().splitlines():
        match = _PUBLISHED_CALLOUT.match(line)
        if match is not None:
            key = match["row"] if not match["variant"] else f"{match['row']} ({match['variant']})"
            assert key not in found, f"row {key} published twice"
            found[key] = (match["level"], match["message"])
    return found


#: The persisted assurance sentences, published the same way: one current row per line,
#: e.g. ``- Assurance row 2 unchanged: Blocking findings were detected …(…).``
_PUBLISHED_ASSURANCE = re.compile(
    r"^- Assurance row (?P<row>\d) (?:after|unchanged): (?P<sentence>.+?)\s*$"
)


def _published_assurance() -> dict[str, str]:
    """``{row number: contract half of the sentence}`` as the note publishes them today."""
    found: dict[str, str] = {}
    for line in _note().splitlines():
        match = _PUBLISHED_ASSURANCE.match(line)
        if match is not None:
            assert match["row"] not in found, f"assurance row {match['row']} published twice"
            found[match["row"]] = _contract_half(match["sentence"])
    return found


def _assurance_sentence(verdict: AuditVerdict, ledger: CoverageLedger) -> str:
    """The LIVE persisted ``assurance_statement``, via the real production fold."""
    halt = HaltReport(
        halted_on_exhaustion=False,
        total_credits=0,
        ceiling_credits=None,
        assessed_count=verdict.total_count,
        assessed_files=(),
        skipped_on_exhaustion_count=0,
        skipped_on_exhaustion_files=(),
    )
    return build_negative_assurance_verdict(
        verdict,
        build_floor_report(verdict, halt),
        CriticalSubsystemSet(),
        ledger,
        materiality_bar="default",
    ).assurance_statement


def _contract_half(sentence: str) -> str:
    """The sentence without its trailing run-data scope clause.

    ``(examined N deeply, sampled M, …)`` is run data; the note quotes it as ``(…)``.
    Everything before it is contract text and is compared verbatim.
    """
    return sentence.split(" (")[0]


#: A history LABEL: the token ``before:``. Anchored on the colon on purpose — the earlier
#: guard tested for the bare word "before" anywhere in a two-line window, and the note
#: says "before" in ordinary prose seven times, including in the header of the
#: *unchanged* list (``**Byte-identical to before — these did not change:**``). Stale
#: wording inserted directly under that header was therefore accepted as history while
#: asserting itself as current — the exact thing this test exists to forbid. A label ends
#: in ``before:``; prose does not.
_BEFORE_LABEL = re.compile(r"\bbefore:", re.IGNORECASE)


def _is_labelled_before(lines: list[str], index: int, fragment: str) -> bool:
    """Is the stale ``fragment`` on line ``index`` introduced by a ``before:`` label?

    Two accepted layouts, and nothing else: the label introduces the quote earlier on the
    SAME line, or it is the whole of the PRECEDING line (which is how a long before/after
    pair is laid out readably).
    """
    line = lines[index]
    if _BEFORE_LABEL.search(line[: line.find(fragment)]):
        return True
    return index > 0 and lines[index - 1].rstrip().lower().endswith("before:")


def _headline(verdict: AuditVerdict) -> str:
    """The live headline with the finding COUNT normalised to ``N``.

    The count is run data, not contract text; the note quotes the shape. Everything
    else in the sentence is compared byte-for-byte.
    """
    line = render_ship_readiness(verdict)[0].removeprefix("Ship-readiness: ")
    return line.replace(
        f" {verdict.blocking_finding_count} verdict-blocking", " N verdict-blocking"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC9 — the note cannot drift from the code
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_DOCS_001_01_note_exists_and_heads_the_released_version() -> None:
    """TC-ArgusAgent-DOCS-001-01 — AC7/AC9, UPDATED by Story 9.2 / AC6: the note heads a VERSION.

    Story 8.4 wrote this as ``assert "## Unreleased" in note`` because there was no
    release path at all: no tag, no workflow, nothing an index could resolve. Story 9.2
    ships the release path, so the note stops being permanently unreleased — and this
    assertion is updated THROUGH that change rather than deleted around it, because its
    job is unchanged: the note must never lose its heading.

    What it now pins is stronger than what it replaced. The heading must be a real
    version, and that version must be the one the package actually ships — so a note that
    announces a version the code does not carry fails here. ``## Unreleased`` must ALSO
    still exist, as the place the next change lands; a note with only a released heading
    invites the next contributor to edit the released section in place.
    """
    note = _note()
    import argus

    version_headings = [
        line.strip()
        for line in note.splitlines()
        if re.match(r"^##\s+\[?v?\d+\.\d+\.\d+", line.strip())
    ]
    assert version_headings, (
        "the note must head a released version section (Story 9.2 / AC6); it carries none"
    )
    assert any(argus.__version__ in heading for heading in version_headings), (
        f"the note heads {version_headings} but the package ships "
        f"{argus.__version__!r} — a note may not announce a version the code does not carry"
    )
    assert "## Unreleased" in note, (
        "the note must keep an `## Unreleased` heading for the next change; without one, "
        "the next edit lands inside a released section"
    )


def test_TC_ArgusAgent_DOCS_001_02_note_carries_both_live_schema_versions() -> None:
    """TC-ArgusAgent-DOCS-001-02 — AC2/AC9: BOTH schema constants, at their LIVE values.

    Bumping either constant without amending the note fails here. The row is located by
    the constant NAME, so the assertion cannot be satisfied by the value appearing
    somewhere else in the document.

    The live value is asserted against the **After** cell specifically (the way ``-03``
    locates its cells). Scanning the whole row would also see the *Before* cell, so a
    published DOWNGRADE — the constant reverted to its pre-amendment value while the note
    still shows the bump — would satisfy the assertion off the wrong column.
    """
    note = _note()
    for name, live in (
        ("VERDICT_SCHEMA_VERSION", VERDICT_SCHEMA_VERSION),
        ("CRITICAL_SUBSYSTEMS_SCHEMA_VERSION", CRITICAL_SUBSYSTEMS_SCHEMA_VERSION),
    ):
        rows = [line for line in note.splitlines() if name in line and line.startswith("|")]
        assert rows, f"the note names no table row for {name}"
        # `| Constant | Before | After | Module |` — the After cell is index 2 of 4.
        after_cells = [_cell(row, 2, expected=4) for row in rows]
        assert f'`"{live}"`' in after_cells, (
            f"{name} is live at {live!r}, but no note row publishes it in the After "
            f"column: rows={rows}, after cells={after_cells}"
        )


def test_TC_ArgusAgent_DOCS_001_03_note_reproduces_the_live_decision_table() -> None:
    """TC-ArgusAgent-DOCS-001-03 — AC1/AC5/AC9: the four-row table matches the real fold.

    For each FR16 row this compares the note's published (verdict, exit code) pair
    against the pair a REAL ``evaluate_verdict`` fold produced for that same row, and
    against the live ``exit_code_for_verdict`` map. Reordering the table, moving a run
    class between exit codes, or renaming a ``DecisionRow`` member all fail here.
    """
    note = _note()
    by_row = _live_rows()

    published: dict[str, str] = {}
    for line in note.splitlines():
        if not line.startswith("|"):
            continue
        cells = _cells(line)
        for row in DecisionRow:
            if cells and cells[-1] == f"`{row.value}`":
                published[row.value] = line

    assert set(published) == {row.value for row in DecisionRow}, (
        "the note's decision table must carry EVERY DecisionRow member exactly once; "
        f"missing {sorted({r.value for r in DecisionRow} - set(published))}"
    )

    for row, verdict in by_row.items():
        line = published[row.value]
        assert f"`{verdict.verdict.value}`" in line, (
            f"the real fold produced {verdict.verdict.value} for {row.value}, "
            f"but the note's row says: {line}"
        )
        live_exit = exit_code_for_verdict(verdict.verdict)
        assert live_exit == verdict.exit_code  # the fold and the map agree
        assert f"`{live_exit}`" in line, (
            f"{row.value} exits {live_exit}, but the note's row says: {line}"
        )


def test_TC_ArgusAgent_DOCS_001_04_note_carries_the_live_exit_code_map() -> None:
    """TC-ArgusAgent-DOCS-001-04 — AC1/AC9: every verdict's live exit code is published.

    Restricted to the FR16 decision table (the rows whose last cell is a ``DecisionRow``
    value), and each half read from its OWN column. Scanning whole lines anywhere in the
    note would accept a (verdict, code) pair assembled from two different columns of the
    historical exit-code table — that table carries `NOT_READY_FOR_RELEASE` / `2` in its
    *Before* cell and `INSUFFICIENT_COVERAGE` / `3` in its *After* cell on one line, so a
    line-wide match can be satisfied by a pairing the tool never produces.
    """
    note = _note()
    # `| # | Condition | Verdict | Exit | decision_row |` — verdict at 2, exit at 3, of 5.
    decision_rows = [
        line
        for line in note.splitlines()
        if line.startswith("|") and _cells(line)[-1] in {f"`{r.value}`" for r in DecisionRow}
    ]
    assert decision_rows, "the note carries no FR16 decision table"

    published = {
        (_cell(line, 2, expected=5), _cell(line, 3, expected=5)) for line in decision_rows
    }
    for verdict in Verdict:
        code = exit_code_for_verdict(verdict)
        assert (f"`{verdict.value}`", f"`{code}`") in published, (
            f"{verdict.value} exits {code}, but the FR16 table publishes no row pairing "
            f"them in their own columns; published pairs = {sorted(published)}"
        )


def test_TC_ArgusAgent_DOCS_001_17_note_publishes_the_live_floor_and_threshold() -> None:
    """TC-ArgusAgent-DOCS-001-17 — AC1/AC9: the two gate CONSTANTS, by name not by luck.

    The note states the `1/5` floor six times, including inside the binding FR16 decision
    table, and the `3/5` release threshold alongside it. Neither was asserted anywhere:
    re-binding ``INSUFFICIENT_COVERAGE_FLOOR`` from `1/5` to `1/4` left this whole module
    green while the note went on publishing `< 1/5`. The rendered strings only catch a
    move large enough to push one of the sample folds into a different row, so the floor
    was covered by accident, never by name — and a floor is exactly the kind of number a
    consumer copies into its own gate.

    Imported and compared as the exact ``Fraction`` the tool prints, so a change to either
    constant fails here whether or not it happens to move a fold.
    """
    note = _note()
    for label, live in (
        ("INSUFFICIENT_COVERAGE_FLOOR", INSUFFICIENT_COVERAGE_FLOOR),
        ("RELEASE_READY_DEEP_THRESHOLD", RELEASE_READY_DEEP_THRESHOLD),
    ):
        assert f"`{live}`" in note, (
            f"{label} is live at {live}, but the note never publishes `{live}` — so the "
            "gate a consumer would copy out of this note is not the gate the tool applies"
        )
    # The FR16 table is where the floor is BINDING, not merely mentioned.
    floor_rows = [
        line
        for line in note.splitlines()
        if line.startswith("|") and f"`{INSUFFICIENT_COVERAGE_FLOOR}`" in line
    ]
    assert floor_rows, (
        f"the FR16 decision table must state the live floor `{INSUFFICIENT_COVERAGE_FLOOR}`"
    )


def test_TC_ArgusAgent_DOCS_001_05_note_quotes_the_four_live_headlines() -> None:
    """TC-ArgusAgent-DOCS-001-05 — AC4/AC9: the four LIVE ship-readiness headlines.

    Rendered through the real ``render_ship_readiness`` over the real folds — so a
    reword of any headline that is not carried into the note fails here.

    Compared PER ROW BY EQUALITY, like the callouts and the assurance sentences, and for
    the same reason. A whole-document ``headline in note`` substring search is satisfied
    by the note's own quoted *before* line: reverting ``_headline``'s row-4 wording to the
    pre-amendment text left that check green, because the note publishes exactly that text
    two sections down, correctly labelled as history. The flagship string of the whole
    amendment was therefore unpinned by the module written to pin it. Matching the row's
    CURRENT marker (``after`` / ``unchanged``, never ``before``) is what closes it.
    """
    published = _published_headlines()
    assert set(published) == {"1", "2", "3", "4"}, (
        f"the note must publish a current headline for all four rows; got {sorted(published)}"
    )
    for row, verdict in _live_rows().items():
        number = row.value.removeprefix("row_")[0]
        assert _headline(verdict) == published[number], (
            f"{row.value}'s live ship-readiness headline is not what the note publishes"
            f"\n  live:      {_headline(verdict)}"
            f"\n  published: {published[number]}"
        )


def test_TC_ArgusAgent_DOCS_001_06_note_states_the_stale_wording_only_as_history() -> None:
    """TC-ArgusAgent-DOCS-001-06 — AC4/AC9: replaced strings appear ONLY as "before".

    AC4 requires the note to QUOTE what was replaced; AC9 requires it not to STATE the
    replaced wording as current. Both hold iff every occurrence of a pre-amendment
    string sits on a line explicitly labelled as a "before". A stale note that simply
    describes the old behaviour has no such label and fails.
    """
    note = _note()
    stale_fragments = (
        "but a coverage gate was not met",  # the pre-amendment row-4 headline
        "Repository is NOT ready for release — deep coverage",  # the pre-amendment row-4 callout
    )
    lines = note.splitlines()
    for fragment in stale_fragments:
        hits = [i for i, line in enumerate(lines) if fragment in line]
        assert hits, f"the note must QUOTE what it says was replaced: {fragment!r}"
        for i in hits:
            assert _is_labelled_before(lines, i, fragment), (
                f"the pre-amendment wording {fragment!r} appears outside a "
                f"'before:' label, i.e. as though it were current:\n  {lines[i]}"
            )
    # …and the live replacement really is published (the other half of the same claim).
    assert "a coverage or critical-subsystem gate was not met" in note


def test_TC_ArgusAgent_DOCS_001_15_note_quotes_the_live_final_verdict_callouts() -> None:
    """TC-ArgusAgent-DOCS-001-15 — AC4/AC9: the callouts AND their alert LEVEL.

    ``final-verdict.md``'s FR16 callout is the surface an integrator greps, and the
    row-4 level change (``CAUTION`` → ``WARNING``) is the sharpest grep-facing claim
    in the note — a tool matching ``[!CAUTION]`` to detect a failing audit stops
    matching that row. Nothing pinned either the text or the level, so
    ``render_final_verdict_report`` could be reworded and the note would rot silently.

    Each row is rendered through the REAL generator over a REAL fold and compared, as a
    ``(level, message)`` pair, against the row the note publishes as CURRENT. Equality
    per row is what gives this teeth: merely finding the text somewhere in the note
    passes even when two rows collapse onto one callout (which is how the pre-amendment
    generator rendered rows 1 and 4), and merely finding the level passes off the
    quoted *before*.
    """
    published = _published_callouts()
    live = _live_callout_cases()
    assert set(published) == set(live), (
        "the note must publish a current callout for every rendering the generator "
        f"produces; published={sorted(published)} live={sorted(live)}"
    )
    for key, (verdict, ledger) in live.items():
        assert _verdict_callout(verdict, ledger) == published[key], (
            f"row {key}'s live final-verdict.md callout is not what the note publishes"
            f"\n  live:      {_verdict_callout(verdict, ledger)}"
            f"\n  published: {published[key]}"
        )


def test_TC_ArgusAgent_DOCS_001_16_note_publishes_the_live_assurance_sentences() -> None:
    """TC-ArgusAgent-DOCS-001-16 — AC4/AC9: the PERSISTED negative-assurance strings.

    ``assurance_statement`` is machine-read out of ``.argus/state/*.json`` and no
    schema signal announces a reword of it, so the note is the only warning a consumer
    gets. Rows 1 and 4 are folded through the real ``build_negative_assurance_verdict``
    and both must be published.

    Compared per row, like the callouts and for the same reason: rows 3 and 4 share a
    prefix and rows 1 and 4 were a single sentence before the amendment, so "the text is
    somewhere in the note" is not a claim about the row that renders it.

    The row-4 *before* is pinned too, and it is code-anchored rather than historical:
    pre-amendment the sentence was chosen from the verdict token alone and a row-4 run
    wore ``NOT_READY_FOR_RELEASE``, so what such a run persisted is exactly the sentence
    row 2 still renders today. Asserting that identity is what catches the note quoting
    some other row's sentence as the row-4 history.
    """
    note = _note()
    published = _published_assurance()
    assert set(published) == {"1", "2", "3", "4"}, (
        f"the note must publish a current sentence for all four rows; got {sorted(published)}"
    )
    for row, (verdict, ledger) in _live_cases().items():
        number = row.value.removeprefix("row_")[0]
        live = _contract_half(_assurance_sentence(verdict, ledger))
        assert live == published[number], (
            f"{row.value}'s live assurance sentence is not what the note publishes"
            f"\n  live:      {live}"
            f"\n  published: {published[number]}"
        )

    # The row-4 "before" must be the sentence a pre-amendment row-4 run really wrote.
    _, _, section = note.partition("**Persisted negative-assurance statement**")
    section = section.partition("**Byte-identical to before")[0]
    assert section, "the note has no persisted-negative-assurance section"
    lines = section.splitlines()
    before_hits = [
        _flat(" ".join(lines[i : i + 2]))
        for i, line in enumerate(lines)
        if "row 4" in line.lower() and "before" in line.lower()
    ]
    assert before_hits, "the note does not state a row-4 'before' assurance sentence"
    assert any(published["2"] in hit for hit in before_hits), (
        "a pre-amendment row-4 run persisted row 2's sentence (its verdict token was "
        f"NOT_READY_FOR_RELEASE), i.e.\n  {published['2']}\n"
        "but the note's row-4 'before' reads:\n"
        + "\n".join(f"  {hit}" for hit in before_hits)
    )


def test_TC_ArgusAgent_DOCS_001_07_note_makes_no_published_index_claim() -> None:
    """TC-ArgusAgent-DOCS-001-07 — AC7/AC9 (the D2 honesty pin), NARROWED by Story 9.2 / AC6.

    Story 8.4 pinned three things at once: no index install instruction, no version
    heading, and an explicit "not tagged and not published" sentence. Story 9.2 ships a
    release workflow and a version heading, so the middle clause moved to ``-01`` — but
    the honesty clause it existed for did NOT weaken, it got MORE specific.

    Two claims remain forbidden and one is now required, and the distinction between them
    is the whole point: *a committed workflow is a committed workflow; a published release
    is a URL.* The note may say the first. It may not imply the second.
    """
    note = _note()
    assert not re.search(r"pip\s+install\s+argus-agent(?![-\w])", note), (
        "the note must not instruct an install from an index — `argus-agent` is on no "
        "package index, so that command cannot work for any reader"
    )
    lowered = note.lower()
    for claim in (
        "published to pypi",
        "available on pypi",
        "released to pypi",
        "now on pypi",
    ):
        assert claim not in lowered, f"the note claims an index publication: {claim!r}"
    assert "not published to any package index" in lowered, (
        "the note must still state out loud that no distribution is published to an "
        "index (D2) — shipping a release workflow does not publish one"
    )
    # And it must say plainly that the workflow itself has not run, so a reader cannot
    # infer a release from the existence of the automation (Story 9.2 / AC2, D13).
    assert "never executed" in lowered, (
        "the note must state that the release workflow is committed but has not run; "
        "no release may be implied without a URL or an Actions run id as evidence"
    )


def test_TC_ArgusAgent_DOCS_001_08_note_publishes_no_absolute_host_path() -> None:
    """TC-ArgusAgent-DOCS-001-08 — AC9 (NFR-S1): no absolute host path in the note.

    Renamed to what it actually asserts. It was called
    ``note_needs_no_network_llm_or_argus_write`` and its docstring claimed "nothing in
    this module dispatches, writes, or reaches a network" — while asserting only the
    absolute-path property below. The claim is true (the folds are pure), but an
    unsupported claim inside the module whose entire thesis is that unsupported claims
    are the defect is not one to leave standing. NFR-D2 inertness is now asserted by
    ``-18``; this test owns the NFR-S1 half.
    """
    note = _note()
    # A Windows drive path at a token boundary — deliberately anchored so a URL scheme
    # (`https://…`) is not mistaken for one.
    drive_path = re.search(r"(?:^|[\s(\[`'\"])[A-Za-z]:[\\/]", note, flags=re.MULTILINE)
    assert drive_path is None, f"absolute host path in the note: {drive_path!r}"
    assert "/home/" not in note and "/Users/" not in note


def test_TC_ArgusAgent_DOCS_001_18_rot_check_reaches_no_network_and_writes_nothing() -> None:
    """TC-ArgusAgent-DOCS-001-18 — AC9 (NFR-D2): the claim `-08` used to make, asserted.

    Every fold in this module must run with no socket and no ``.argus/`` write. Proven
    rather than stated: sockets and the store writer are replaced with detonators, and
    the module's most expensive path — the live callout renders, which fold real
    verdicts through the real generator — is run underneath them.
    """
    import socket

    import argus.store.writer as writer_module

    class _NoSockets(socket.socket):
        def __init__(self, *args: object, **kwargs: object) -> None:
            raise AssertionError("the rot check must not open a socket (NFR-D2)")

    def _no_writes(*args: object, **kwargs: object) -> None:
        raise AssertionError("the rot check must not write .argus/ state (NFR-D2)")

    real_socket = socket.socket
    real_create = socket.create_connection
    real_envelope = writer_module.ApaaStoreWriter.write_envelope
    real_payload = writer_module.ApaaStoreWriter.write_payload
    socket.socket = _NoSockets  # type: ignore[misc, assignment]
    socket.create_connection = _no_writes  # type: ignore[assignment]
    writer_module.ApaaStoreWriter.write_envelope = _no_writes  # type: ignore[method-assign, assignment]
    writer_module.ApaaStoreWriter.write_payload = _no_writes  # type: ignore[method-assign, assignment]
    try:
        for key, (verdict, ledger) in _live_callout_cases().items():
            assert _verdict_callout(verdict, ledger), key
            assert _assurance_sentence(verdict, ledger)
        assert _published_headlines() and _published_callouts() and _published_assurance()
    finally:
        socket.socket = real_socket  # type: ignore[misc]
        socket.create_connection = real_create  # type: ignore[assignment]
        writer_module.ApaaStoreWriter.write_envelope = real_envelope  # type: ignore[method-assign]
        writer_module.ApaaStoreWriter.write_payload = real_payload  # type: ignore[method-assign]


def test_TC_ArgusAgent_DOCS_001_14_note_lists_only_names_that_really_import() -> None:
    """TC-ArgusAgent-DOCS-001-14 — AC6/AC9: every published API name is IMPORTED here.

    The note's API section is only worth reading if no name in it was listed on trust.
    Each name below is resolved from the shipped tree — a rename or a removal fails
    here — and then required to appear in the note.
    """
    from argus.detectors.vacuous_test import is_test_classification_content_dependent
    from argus.ledger.critical_subsystems import CriticalCandidate, CriticalSubsystemSet
    from argus.reports.plain_english import ShipReadinessError
    from argus.verdict.prosecutor import ProsecutionResult

    resolved: dict[str, object] = {
        "DecisionRow": DecisionRow,
        "ShipReadinessError": ShipReadinessError,
        "CriticalIneligibility": __import__(
            "argus.ledger.critical_subsystems", fromlist=["CriticalIneligibility"]
        ).CriticalIneligibility,
        "is_test_classification_content_dependent": is_test_classification_content_dependent,
    }
    fields: dict[str, tuple[type, str]] = {
        "AuditVerdict.decision_row": (AuditVerdict, "decision_row"),
        "CriticalCandidate.ineligibility": (CriticalCandidate, "ineligibility"),
        "CriticalSubsystemSet.heuristic_excluded_ineligible": (
            CriticalSubsystemSet,
            "heuristic_excluded_ineligible",
        ),
        "ProsecutionResult.verdict_changed": (ProsecutionResult, "verdict_changed"),
    }

    note = _note()
    for name, obj in resolved.items():
        assert obj is not None
        assert f"`{name}`" in note, f"{name} imports but the note does not list it"
    for name, (model, field) in fields.items():
        assert field in model.model_fields, f"{name} is not a field on {model.__name__}"
        assert f"`{name}`" in note, f"{name} exists but the note does not list it"
    # The one derived property, and the behavioural flag the note must carry for it.
    assert isinstance(AuditVerdict.__dict__.get("is_below_floor"), property)
    assert "`AuditVerdict.is_below_floor`" in note
    assert ShipReadinessError.__mro__[1] is ValueError
    assert "behavioural change" in note, (
        "the note must flag ShipReadinessError as a behavioural change, not an addition"
    )


# ─────────────────────────────────────────────────────────────────────────────
# AC8 (RS-4a) — the package front door states only what is true
# ─────────────────────────────────────────────────────────────────────────────


def test_TC_ArgusAgent_DOCS_001_09_front_door_carries_no_stale_claim() -> None:
    """TC-ArgusAgent-DOCS-001-09 — AC8/RS-4a: the removals are pinned.

    ``argus/__init__.py`` is the first thing a reader of the package meets. It claimed
    the package lives under ``minions_core/``, that it is a reserved shell with no
    business logic, and that it ships as the ``minions[argus]`` extra. None is true.
    """
    text = _FRONT_DOOR.read_text(encoding="utf-8")
    for stale in ("minions_core", "RESERVED PACKAGE SHELL", "minions[argus]"):
        assert text.count(stale) == 0, (
            f"argus/__init__.py still contains {stale!r} ({text.count(stale)}x)"
        )


def test_TC_ArgusAgent_DOCS_001_10_front_door_version_surface_is_unchanged() -> None:
    """TC-ArgusAgent-DOCS-001-10 — AC8/AC12: ``__version__`` is load-bearing, not prose.

    ``__version__`` is the DEFAULT ``argus_version`` field on every envelope
    (``store/envelope.py``), so changing it changes the BYTES of every persisted
    ``.argus/`` artifact.

    Precision correction (Story 9.2): it is NOT "folded into every content hash".
    ``compute_content_hash`` hashes the **payload only** (NFR-D3) and ``argus_version``
    is an **envelope** field, so for every artifact except the evidence bundle a version
    change moves the file's bytes but NOT its content hash or its content-addressed
    filename. The evidence bundle is the sole exception, because
    ``bundle_to_canonical_payload`` also carries the version INSIDE the hashed payload —
    which is exactly why DF-8-5-A's literal was able to move a published signature.

    ``0.1.0`` is asserted here as a DELIBERATE pin: Story 9.2 ships ``0.1.0`` un-bumped
    (D1), so this assertion was left untouched by the release rather than edited to
    accommodate one.
    """
    import argus

    assert argus.__version__ == "0.1.0"
    assert argus.__status__ == "experimental"
    assert argus.__all__ == ["__version__", "__status__"]


def test_TC_ArgusAgent_DOCS_001_11_front_door_cites_only_paths_that_exist() -> None:
    """TC-ArgusAgent-DOCS-001-11 — AC8: every authoritative source it names is on disk.

    The docstring previously pointed at a decisions/ path that does not exist in this
    repository and at architecture/epics/stories marked "TO BE CREATED". A front door
    that cites a dead path is a front door that lies about where the truth is.
    """
    docstring = _FRONT_DOOR.read_text(encoding="utf-8").split('"""')[1]
    cited = re.findall(r"(?:^|\s)((?:_bmad-output|CHANGELOG\.md)[^\s`,)]*)", docstring)
    assert cited, "the front door must cite its authoritative sources"
    missing = [p for p in cited if not (_REPO_ROOT / p.rstrip("/")).exists()]
    assert not missing, f"argus/__init__.py cites paths that do not exist: {missing}"


@pytest.mark.parametrize(
    "fact",
    ["argus-agent", "argus/", "repo-audit", "Agent-Argus"],
)
def test_TC_ArgusAgent_DOCS_001_12_front_door_states_the_true_distribution(fact: str) -> None:
    """TC-ArgusAgent-DOCS-001-12 — AC8: what REPLACES the stale claims is verifiable.

    The distribution name, the package directory, the repository, and the one console
    script whose name is unambiguous. Four DISTINCT facts: the list read
    ``["argus-agent", "argus/", "argus-agent", "repo-audit"]`` — ``argus-agent`` twice,
    for three real cases out of four.

    The bare ``argus`` console script is deliberately NOT checked here: as a substring of
    ``argus-agent``, ``argus/`` and the package's own name it is satisfied by almost any
    text, so asserting it here would be assurance theatre. ``-13`` covers it properly, by
    reading the script names out of ``pyproject.toml`` and requiring each one.
    """
    text = _FRONT_DOOR.read_text(encoding="utf-8")
    assert fact in text, f"the front door does not state {fact!r}"


def test_TC_ArgusAgent_DOCS_001_13_front_door_facts_match_pyproject() -> None:
    """TC-ArgusAgent-DOCS-001-13 — AC8: the front door's package facts are not asserted alone.

    Cross-checked against ``pyproject.toml`` so the two cannot diverge: the
    distribution name and every console script the front door names.
    """
    pyproject = (_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    text = _FRONT_DOOR.read_text(encoding="utf-8")

    assert 'name = "argus-agent"' in pyproject
    scripts = re.findall(r"^(\S+)\s*=\s*\"argus\.cli:main\"", pyproject, flags=re.MULTILINE)
    assert sorted(scripts) == ["argus", "argus-agent", "repo-audit"], scripts
    for script in scripts:
        assert script in text, f"the front door does not name the console script {script!r}"


# ─────────────────────────────────────────────────────────────────────────────
# Story 9.2 / AC1 — the version-bearing surfaces are ONE enumerated space
#
# Before 9.2 this repository stated its own version three times and the three did not
# agree: ``pyproject.toml`` ``0.1.0``, ``argus.__version__`` ``0.1.0``, and
# ``argus.dogfood.proof_run.DOGFOOD_ArgusAgent_VERSION`` ``1.43.0`` — and the third one
# reached the SIGNED, content-hashed evidence payload, so one persisted envelope asserted
# two versions of the same package on its two levels (DF-8-5-A).
#
# ``-14`` pins AGREEMENT across the enumerated surfaces. ``-15`` pins COMPLETENESS of the
# enumeration: an AST sweep over the whole ``argus/**`` tree fails on ANY semver-shaped
# string literal outside the single registered source, so a *fourth* version literal
# introduced by a future module goes RED instead of quietly disagreeing (AI-E8-6 — an AC
# that quantifies universally needs a test that enumerates and rejects the unenumerated).
# ─────────────────────────────────────────────────────────────────────────────

# The ONE place in the package permitted to hold a version literal: (posix path, binding).
_VERSION_LITERAL_SITE = ("argus/__init__.py", "__version__")

# A whole string that is exactly a semver release token. Deliberately anchored and
# 3-part: ``schema_version`` constants ("1") and ratio/marker strings do not match, so the
# sweep flags package-version literals and not every numeric string in the tree.
_SEMVER_LITERAL = re.compile(r"^\d+\.\d+\.\d+$")


def _pyproject_version() -> str:
    pyproject = (_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r"^version\s*=\s*\"([^\"]+)\"", pyproject, flags=re.MULTILINE)
    assert match, "pyproject.toml states no `version = ` for the argus-agent distribution"
    return match.group(1)


def test_TC_ArgusAgent_DOCS_001_14_every_version_surface_states_one_value() -> None:
    """TC-ArgusAgent-DOCS-001-14 — Story 9.2 / AC1: the enumerated version surfaces AGREE.

    Each surface is read from where it actually lives (the packaging metadata, the
    package front door, the dogfood generator) rather than compared against a literal
    repeated in this test — a fourth copy of the value in the guard would be the defect
    the guard exists to catch.
    """
    import argus
    from argus.dogfood.proof_run import DOGFOOD_ArgusAgent_VERSION

    surfaces = {
        "pyproject.toml [project] version": _pyproject_version(),
        "argus.__version__": argus.__version__,
        "argus.dogfood.proof_run.DOGFOOD_ArgusAgent_VERSION": DOGFOOD_ArgusAgent_VERSION,
    }
    distinct = set(surfaces.values())
    assert len(distinct) == 1, (
        f"the package states more than one version: {surfaces}"
    )


def test_TC_ArgusAgent_DOCS_001_15_no_unregistered_version_literal_in_argus() -> None:
    """TC-ArgusAgent-DOCS-001-15 — Story 9.2 / AC1: the enumeration is COMPLETE.

    Walks the AST of every ``argus/**/*.py`` module and collects every string constant
    that is exactly a semver release token, wherever it appears — an assignment, a
    default argument, a keyword argument at a call site. Exactly ONE is permitted, at
    :data:`_VERSION_LITERAL_SITE`. Any other is a second source of truth for the package
    version and fails here, which is what makes ``-14``'s three-surface enumeration a
    closed space rather than a sample of an open one.
    """
    import ast

    package_root = _REPO_ROOT / "argus"
    found: list[tuple[str, int, str]] = []
    modules = 0
    for path in sorted(package_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        modules += 1
        tree = ast.parse(path.read_text(encoding="utf-8"))
        rel = path.relative_to(_REPO_ROOT).as_posix()
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and _SEMVER_LITERAL.match(node.value)
            ):
                found.append((rel, node.lineno, node.value))

    # Non-vacuity: the sweep really walked the package, and really found the one site.
    assert modules >= 60, f"the version sweep only walked {modules} modules"
    assert len(found) == 1, (
        "exactly one semver version literal may exist in argus/**; found: " f"{found}"
    )
    rel, _lineno, value = found[0]
    assert rel == _VERSION_LITERAL_SITE[0], (
        f"the version literal moved to {rel}; the single source is {_VERSION_LITERAL_SITE[0]}"
    )

    import argus

    assert value == argus.__version__
    assert f"{_VERSION_LITERAL_SITE[1]} = " in (_REPO_ROOT / rel).read_text(encoding="utf-8")
