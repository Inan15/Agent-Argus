"""Verification for content-derived test-file classification (CR-5, 2026-08-03).

Verification area ArgusAgent-DETECT (TC-ArgusAgent-DETECT-002-NN).

The defect this pins
--------------------
``*_test.py`` is a real pytest convention (``python_files = test_*.py *_test.py``), so
it cannot simply be removed from the suffix list. But it ALSO matches production
modules whose subject happens to be testing — ``argus/detectors/vacuous_test.py``, the
vacuous-test DETECTOR itself, was classified as a test file, skipped by the deep
grading path, and landed in the ledger as ``tool_scanned_only``.

Neither answer is correct from the filename alone. The fix applies the doctrine
``assess_criticality`` already states — classify by CONTENT, not filename — using the
pre-built AST entry when a caller has one.
"""

from __future__ import annotations

from argus.detectors.vacuous_test import is_test_file
from argus.index.ast_index import AstIndexEntry, Definition


def _entry(
    file_path: str,
    *definitions: Definition,
    ast_eligible: bool = True,
    parse_failed: bool = False,
) -> AstIndexEntry:
    return AstIndexEntry(
        file_path=file_path,
        ast_eligible=ast_eligible,
        parse_failed=parse_failed,
        definitions=tuple(definitions),
        edges=(),
    )


_PRODUCTION_DEFS = (
    Definition(name="is_test_file", kind="function", start_line=1, end_line=9),
    Definition(name="VacuousTestDetector", kind="class", start_line=11, end_line=40),
)
_TEST_DEFS = (
    Definition(name="test_widget_rejects_empty", kind="function", start_line=1, end_line=5),
)


def test_the_regression_file_itself_is_classified_as_production() -> None:
    """THE case: argus/detectors/vacuous_test.py is a detector, not a test suite."""
    entry = _entry("argus/detectors/vacuous_test.py", *_PRODUCTION_DEFS)

    assert is_test_file("argus/detectors/vacuous_test.py", ast_entry=entry) is False


def test_a_genuine_pytest_style_module_outside_tests_stays_a_test_file() -> None:
    """The moat must survive the fix: `foo_test.py` with test functions is still a test."""
    entry = _entry("pkg/widget_test.py", *_TEST_DEFS)

    assert is_test_file("pkg/widget_test.py", ast_entry=entry) is True


def test_path_only_behaviour_is_unchanged_for_callers_without_an_ast_entry() -> None:
    """Backward compatibility: the optional kwarg cannot alter an existing call site."""
    assert is_test_file("thing_test.py") is True
    assert is_test_file("tests/test_x.py") is True
    assert is_test_file("pkg/tests/foo.py") is True
    assert is_test_file("test_thing.py") is True
    assert is_test_file("argus/detectors/vacuous.py") is False


def test_location_beats_content_so_a_helper_under_tests_is_never_deep_graded() -> None:
    """A file under tests/ is a test file even with zero test-shaped definitions.

    Test helpers/fixtures define no ``test_*`` function. Letting content override
    LOCATION would promote them into the deep-graded population and inflate coverage.
    """
    entry = _entry("tests/cartridges/_registry.py", *_PRODUCTION_DEFS)

    assert is_test_file("tests/cartridges/_registry.py", ast_entry=entry) is True


def test_unreadable_content_stays_a_test_file_the_conservative_direction() -> None:
    """AR10: when content cannot be read, do NOT promote to production.

    The two misclassifications are asymmetric — treating a test as production both
    inflates the deep count and skips the vacuous detector, a false green. So an
    unreadable entry keeps the filename verdict.
    """
    parse_failed = _entry("pkg/widget_test.py", parse_failed=True)
    ineligible = _entry("pkg/widget_test.py", ast_eligible=False)

    assert is_test_file("pkg/widget_test.py", ast_entry=parse_failed) is True
    assert is_test_file("pkg/widget_test.py", ast_entry=ineligible) is True
    assert is_test_file("pkg/widget_test.py", ast_entry=object()) is True  # type: ignore[arg-type]


def test_unittest_style_test_classes_are_recognized_as_test_content() -> None:
    """`class TestFoo(TestCase)` holds the test_* methods — the class is the signal."""
    entry = _entry(
        "pkg/widget_test.py",
        Definition(name="TestWidget", kind="class", start_line=1, end_line=20),
    )

    assert is_test_file("pkg/widget_test.py", ast_entry=entry) is True


def test_non_python_conventions_are_unambiguous_and_ignore_content() -> None:
    """Go/JS/Rust test suffixes are reserved by convention — no content check needed."""
    entry = _entry("pkg/handler_test.go", *_PRODUCTION_DEFS)

    assert is_test_file("pkg/handler_test.go", ast_entry=entry) is True
    assert is_test_file("web/button.test.tsx") is True
    assert is_test_file("crate/parser_test.rs") is True
