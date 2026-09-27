"""Unit and dry-run verification tests for defect remediation engine (`argus.remediation`).

Drivers: Story 20.2 (Defect Remediation Engine).
"""

from __future__ import annotations

import tempfile
from pathlib import Path
import pytest
from pydantic import ValidationError

from argus.ledger.recording import Locator, Recording
from argus.remediation import (
    RemediationEngine,
    RemediationPatch,
    RemediationResult,
    apply_patch,
    verify_patch_dry_run,
)


def _make_recording(
    recording_id: str = "rec_001",
    file_path: str = "tests/test_sample.py",
    start_line: int = 1,
    end_line: int = 4,
) -> Recording:
    locator = Locator(file_path=file_path, start_line=start_line, end_line=end_line)
    return Recording(
        recording_id=recording_id,
        rule_id="vacuous_test_ast",
        advisory=True,
        locators=(locator,),
    )


class TestRemediationModels:
    """Test pure data contracts immutability, extra forbid, and POSIX path containment validation."""

    def test_remediation_patch_immutability(self) -> None:
        patch = RemediationPatch(
            finding_id="f_001",
            target_file="tests/test_foo.py",
            diff_content="--- a/tests/test_foo.py\n+++ b/tests/test_foo.py\n",
            affected_lines=(3,),
            patch_id="patch:f_001",
            created_at="2026-08-29T00:00:00Z",
        )
        with pytest.raises(ValidationError):
            patch.target_file = "tests/test_bar.py"  # type: ignore[misc]

    def test_remediation_patch_extra_forbid(self) -> None:
        with pytest.raises(ValidationError):
            RemediationPatch(
                finding_id="f_001",
                target_file="tests/test_foo.py",
                diff_content="...",
                affected_lines=(1,),
                patch_id="p1",
                created_at="2026-08-29T00:00:00Z",
                extra_field="invalid",  # type: ignore[call-arg]
            )

    def test_remediation_patch_posix_contained_path_validation(self) -> None:
        # Valid POSIX relative path
        patch = RemediationPatch(
            finding_id="f_001",
            target_file="tests/sub/test_foo.py",
            diff_content="...",
            affected_lines=(1,),
            patch_id="p1",
            created_at="2026-08-29T00:00:00Z",
        )
        assert patch.target_file == "tests/sub/test_foo.py"

        # Absolute path rejected
        with pytest.raises(ValidationError, match="relative path"):
            RemediationPatch(
                finding_id="f_001",
                target_file="/abs/path/test_foo.py",
                diff_content="...",
                affected_lines=(1,),
                patch_id="p1",
                created_at="2026-08-29T00:00:00Z",
            )

        # Backslash path rejected
        with pytest.raises(ValidationError, match="forward slashes"):
            RemediationPatch(
                finding_id="f_001",
                target_file="tests\\test_foo.py",
                diff_content="...",
                affected_lines=(1,),
                patch_id="p1",
                created_at="2026-08-29T00:00:00Z",
            )

        # Path traversal rejected
        with pytest.raises(ValidationError, match="traversal"):
            RemediationPatch(
                finding_id="f_001",
                target_file="../outside/test_foo.py",
                diff_content="...",
                affected_lines=(1,),
                patch_id="p1",
                created_at="2026-08-29T00:00:00Z",
            )

    def test_remediation_result_model(self) -> None:
        result = RemediationResult(
            patches=(),
            success=True,
            dry_run_verified=True,
            applied_count=0,
            errors=(),
        )
        assert result.success is True
        assert result.applied_count == 0
        with pytest.raises(ValidationError):
            result.success = False  # type: ignore[misc]


class TestRemediationEnginePatchGenerator:
    """Test patch generation for vacuous assertions, empty test bodies, and missing assertions."""

    def test_remediate_vacuous_assert_true_with_sut_variable(self) -> None:
        source = (
            "def test_foo():\n"
            "    result = calculate_data()\n"
            "    assert True\n"
        )
        rec = _make_recording(start_line=1, end_line=3)
        engine = RemediationEngine()
        patch = engine.generate_patch(rec, source)

        assert patch is not None
        assert patch.target_file == "tests/test_sample.py"
        assert "assert result is not None" in patch.diff_content
        assert patch.affected_lines == (3,)

    def test_remediate_vacuous_assert_1_equals_1(self) -> None:
        source = (
            "def test_foo():\n"
            "    val = compute()\n"
            "    assert 1 == 1\n"
        )
        rec = _make_recording(start_line=1, end_line=3)
        engine = RemediationEngine()
        patch = engine.generate_patch(rec, source)

        assert patch is not None
        assert "assert val is not None" in patch.diff_content

    def test_remediate_empty_pass_body(self) -> None:
        """A `pass` body IS remediated - when the span offers something to assert on."""
        source = (
            "def test_empty():\n"
            "    val = compute()\n"
            "    pass\n"
        )
        rec = _make_recording(start_line=1, end_line=3)
        engine = RemediationEngine()
        patch = engine.generate_patch(rec, source)

        assert patch is not None
        assert "assert val is not None" in patch.diff_content

    def test_declines_when_the_span_has_no_assertable_state(self) -> None:
        """AC2 - amended 2026-08-29. A proposal that breaks the test is worse than none.

        This case previously produced `assert len(locals()) > 0`. MEASURED: that predicate is
        False in a scope holding no locals, so the "remediation" converted a PASSING vacuous
        test into a FAILING one, and `verify_patch_dry_run` passed it because the syntax is
        valid. AC2 requires a CONCRETE, NON-VACUOUS assertion; where none exists the engine
        now declines. Two shapes, both of which used to fabricate one.
        """
        engine = RemediationEngine()

        empty_body = (
            "def test_empty():\n"
            "    pass\n"
        )
        assert engine.generate_patch(_make_recording(start_line=1, end_line=2), empty_body) is None

        # `assert True` stands BEFORE `val` exists, so val cannot be asserted on at line 2 and
        # there is nothing else in scope. Declining is the only honest answer.
        assert_before_assignment = (
            "def test_order():\n"
            "    assert True\n"
            "    val = compute()\n"
        )
        assert engine.generate_patch(
            _make_recording(start_line=1, end_line=3), assert_before_assignment
        ) is None

    def test_remediate_missing_assertion(self) -> None:
        source = (
            "def test_no_assert():\n"
            "    output = do_work()\n"
        )
        rec = _make_recording(start_line=1, end_line=2)
        engine = RemediationEngine()
        patch = engine.generate_patch(rec, source)

        assert patch is not None
        assert "assert output is not None" in patch.diff_content

    def test_remediate_vacuous_assert_after_assignment(self) -> None:
        """The ordering guard from review round 1: only a PRIOR assignment may be referenced."""
        source = (
            "def test_order():\n"
            "    val = compute()\n"
            "    assert True\n"
            "    later = compute()\n"
        )
        rec = _make_recording(start_line=1, end_line=4)
        engine = RemediationEngine()
        patch = engine.generate_patch(rec, source)

        assert patch is not None
        assert "assert val is not None" in patch.diff_content
        # `later` is declared AFTER the vacuous assert and must never be referenced by it.
        assert "assert later is not None" not in patch.diff_content

    def test_remediate_preserve_custom_message_and_comment(self) -> None:
        source = (
            "def test_msg():\n"
            "    val = compute()\n"
            '    assert True, "custom error message"  # check result\n'
        )
        rec = _make_recording(start_line=1, end_line=3)
        engine = RemediationEngine()
        patch = engine.generate_patch(rec, source)

        assert patch is not None
        assert 'assert val is not None, "custom error message"  # check result' in patch.diff_content

    def test_remediate_unittest_assertions(self) -> None:
        source = (
            "def test_ut(self):\n"
            "    res = compute()\n"
            '    self.assertTrue(True, "failed")  # comment\n'
            "    self.assertEqual(1, 1)\n"
        )
        rec = _make_recording(start_line=1, end_line=4)
        engine = RemediationEngine()
        patch = engine.generate_patch(rec, source)

        assert patch is not None
        assert 'self.assertTrue(res is not None, "failed")  # comment' in patch.diff_content
        assert "self.assertIsNotNone(res)" in patch.diff_content


class TestDryRunVerificationAndContainment:
    """Test dry-run verification and workspace path containment protection."""

    def test_verify_patch_dry_run_success(self) -> None:
        source = (
            "def test_foo():\n"
            "    res = compute()\n"
            "    assert True\n"
        )
        rec = _make_recording(start_line=1, end_line=3)
        engine = RemediationEngine()
        patch = engine.generate_patch(rec, source)
        assert patch is not None

        verified = verify_patch_dry_run(source, patch)
        assert verified is True

    def test_verify_patch_dry_run_syntax_failure(self) -> None:
        source = "def test_foo():\n    pass\n"
        bad_patch = RemediationPatch(
            finding_id="f_bad",
            target_file="tests/test_sample.py",
            diff_content=(
                "--- a/tests/test_sample.py\n"
                "+++ b/tests/test_sample.py\n"
                "@@ -1,2 +1,2 @@\n"
                " def test_foo():\n"
                "-    pass\n"
                "+    def invalid_syntax(((\n"
            ),
            affected_lines=(2,),
            patch_id="p_bad",
            created_at="2026-08-29T00:00:00Z",
        )
        assert verify_patch_dry_run(source, bad_patch) is False

    def test_apply_patch_success_and_containment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            ws_root = Path(tmp_dir).resolve()
            test_dir = ws_root / "tests"
            test_dir.mkdir(parents=True, exist_ok=True)
            target_file = test_dir / "test_sample.py"
            source = "def test_foo():\n    result = 42\n    assert True\n"
            target_file.write_text(source, encoding="utf-8")

            rec = _make_recording(start_line=1, end_line=3)
            engine = RemediationEngine(workspace_root=str(ws_root))
            patch = engine.generate_patch(rec, source)
            assert patch is not None

            # Apply patch cleanly
            success = apply_patch("tests/test_sample.py", patch, workspace_root=str(ws_root))
            assert success is True
            new_text = target_file.read_text(encoding="utf-8")
            assert "assert result is not None" in new_text

            # Escape containment fails safely
            escape_success = apply_patch("../outside.py", patch, workspace_root=str(ws_root))
            assert escape_success is False


class TestBatchProcessing:
    """Test process_recordings batch execution in dry-run and apply modes."""

    def test_process_recordings_dry_run(self) -> None:
        source_map = {
            "tests/test_sample.py": "def test_a():\n    result = 10\n    assert True\n"
        }
        rec = _make_recording()
        engine = RemediationEngine()
        res = engine.process_recordings([rec], source_loader=lambda path: source_map[path], dry_run=True)

        assert res.success is True
        assert res.dry_run_verified is True
        assert len(res.patches) == 1
        assert res.applied_count == 0

    def test_process_recordings_apply_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            ws_root = Path(tmp_dir).resolve()
            test_dir = ws_root / "tests"
            test_dir.mkdir(parents=True, exist_ok=True)
            target_file = test_dir / "test_sample.py"
            source = "def test_a():\n    result = 10\n    assert True\n"
            target_file.write_text(source, encoding="utf-8")

            rec = _make_recording()
            engine = RemediationEngine(workspace_root=str(ws_root))
            res = engine.process_recordings(
                [rec],
                source_loader=lambda path: (ws_root / path).read_text(encoding="utf-8"),
                dry_run=False,
            )

            assert res.success is True
            assert res.applied_count == 1
            assert "assert result is not None" in target_file.read_text(encoding="utf-8")
