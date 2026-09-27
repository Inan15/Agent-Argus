"""Remediation patch generator, dry-run verification, and patch application engine (PURE).

Drivers: Story 20.2 (Defect Remediation Engine), NFR-S1 (workspace path containment),
AR8 (pure functions), AR10 (typed failure / graceful degradation).
"""

from __future__ import annotations

import ast
import difflib
import re
from datetime import datetime, timezone

from collections.abc import Callable, Sequence
from pathlib import Path

from argus.ledger.recording import Recording
from argus.remediation.models import RemediationPatch, RemediationResult
from argus.shared.workspace_containment import WorkspaceArtifactWriter

__all__ = [
    "RemediationEngine",
    "apply_patch",
    "apply_unified_diff",
    "verify_patch_dry_run",
]

_VACUOUS_ASSERT_RE = re.compile(
    r"\bassert\s+(True|1\s*==\s*1|0\s*==\s*0|False\s*==\s*False|None\s+is\s+None)\b"
)
_UNITTEST_TRUE_RE = re.compile(r"\bself\.assertTrue\(\s*True\s*")
_UNITTEST_EQ_RE = re.compile(r"\bself\.assertEqual\(\s*1\s*,\s*1\s*")
_PASS_RE = re.compile(r"^\s*pass\s*$")
_ASSIGNMENT_RE = re.compile(r"^\s*([a-zA-Z_][a-zA-Z0-9_.]*)\s*=(?!=)")


def _extract_comment(line: str) -> tuple[str, str]:
    """Extract code and trailing inline comment from line, respecting quotes."""
    in_quote = False
    quote_char = ""
    for idx, char in enumerate(line):
        if char in ('"', "'"):
            if not in_quote:
                in_quote = True
                quote_char = char
            elif char == quote_char:
                in_quote = False
        elif char == "#" and not in_quote:
            code_text = line[:idx].rstrip()
            spaces = line[:idx][len(code_text):]
            if not spaces:
                spaces = " "
            return code_text, f"{spaces}{line[idx:]}"
    return line, ""


def _find_prior_assigned_var(source_lines: Sequence[str], current_idx: int) -> str | None:
    """Find the assigned variable name from the nearest line prior to current_idx."""
    for k in range(current_idx - 1, -1, -1):
        m = _ASSIGNMENT_RE.match(source_lines[k])
        if m:
            var_name = m.group(1)
            if var_name not in ("def", "class", "return", "if", "for", "while", "with", "raise"):
                return var_name
    return None


def apply_unified_diff(source_content: str, diff_text: str) -> str | None:
    """In-memory application of a unified diff patch to source content.

    Returns the modified source code string on clean application, or None if
    the patch cannot be applied cleanly.
    """
    source_lines = source_content.splitlines()
    diff_lines = diff_text.splitlines()

    hunk_re = re.compile(r"^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@")

    i = 0
    hunks = []
    while i < len(diff_lines):
        line = diff_lines[i]
        match = hunk_re.match(line)
        if match:
            old_start = int(match.group(1))
            old_count = int(match.group(2)) if match.group(2) is not None else 1
            new_start = int(match.group(3))
            new_count = int(match.group(4)) if match.group(4) is not None else 1
            i += 1
            hunk_ops = []
            while (
                i < len(diff_lines)
                and not diff_lines[i].startswith("@@")
                and not diff_lines[i].startswith("---")
                and not diff_lines[i].startswith("+++")
            ):
                dl = diff_lines[i]
                if dl.startswith(" ") or dl.startswith("-") or dl.startswith("+"):
                    hunk_ops.append((dl[0], dl[1:]))
                elif dl == "":
                    hunk_ops.append((" ", ""))
                i += 1
            hunks.append((old_start, old_count, new_start, new_count, hunk_ops))
        else:
            i += 1

    if not hunks:
        return None

    result_lines: list[str] = []
    curr_idx = 0  # 0-based line index

    for old_start, _old_count, _new_start, _new_count, ops in hunks:
        hunk_start_idx = old_start - 1
        if hunk_start_idx < curr_idx or hunk_start_idx > len(source_lines):
            return None

        result_lines.extend(source_lines[curr_idx:hunk_start_idx])
        curr_idx = hunk_start_idx

        for op, text in ops:
            if op == " ":
                if curr_idx >= len(source_lines) or source_lines[curr_idx] != text:
                    return None
                result_lines.append(source_lines[curr_idx])
                curr_idx += 1
            elif op == "-":
                if curr_idx >= len(source_lines) or source_lines[curr_idx] != text:
                    return None
                curr_idx += 1
            elif op == "+":
                result_lines.append(text)

    result_lines.extend(source_lines[curr_idx:])
    ending = "\n" if source_content.endswith("\n") else ""
    return "\n".join(result_lines) + ending


def verify_patch_dry_run(source_content: str, patch: RemediationPatch) -> bool:
    """Dry-run applies patch in memory and validates AST syntax without modifying disk (AC3)."""
    try:
        new_content = apply_unified_diff(source_content, patch.diff_content)
        if new_content is None:
            return False
        ast.parse(new_content)
        return True
    except Exception:
        return False


def apply_patch(
    target_file_path: str,
    patch: RemediationPatch,
    workspace_root: str = ".",
) -> bool:
    """Safely writes patch to target file ensuring path containment (NFR-S1) (AC3)."""
    try:
        root = Path(workspace_root).resolve()
        target_path = (root / target_file_path).resolve()

        if not WorkspaceArtifactWriter._is_contained(target_path, root):
            return False

        if not target_path.exists() or not target_path.is_file():
            return False

        source_content = target_path.read_text(encoding="utf-8")
        if not verify_patch_dry_run(source_content, patch):
            return False

        new_content = apply_unified_diff(source_content, patch.diff_content)
        if new_content is None:
            return False

        target_path.write_text(new_content, encoding="utf-8")
        return True
    except Exception:
        return False


class RemediationEngine:
    """Engine for generating and applying defect remediation patches (AC2)."""

    def __init__(self, workspace_root: str = ".") -> None:
        self.workspace_root = workspace_root

    def generate_patch(
        self, recording: Recording, source_code: str
    ) -> RemediationPatch | None:
        """Generate a RemediationPatch for the given finding recording and source code (AC2)."""
        if not recording.locators:
            return None

        locator = recording.locators[0]
        target_file = locator.file_path.replace("\\", "/")
        start_line = locator.start_line
        end_line = locator.end_line

        source_lines = source_code.splitlines()
        if start_line < 1 or start_line > len(source_lines):
            return None

        start_idx = max(0, start_line - 1)
        end_idx = min(len(source_lines), end_line)

        new_lines = list(source_lines)
        affected_lines: set[int] = set()

        transformed = False
        for i in range(start_idx, end_idx):
            line = source_lines[i]
            code_part, comment_part = _extract_comment(line)
            indent = code_part[: len(code_part) - len(code_part.lstrip())]

            if _VACUOUS_ASSERT_RE.search(code_part):
                assigned_var = _find_prior_assigned_var(source_lines, i)
                msg_match = re.search(
                    r"\bassert\s+(?:True|1\s*==\s*1|0\s*==\s*0|False\s*==\s*False|None\s+is\s+None)\s*,\s*(.+)$",
                    code_part,
                )
                msg_str = f", {msg_match.group(1).strip()}" if msg_match else ""

                if assigned_var is None:
                    # DECLINE rather than fabricate. Until 2026-08-29 this branch emitted
                    # `assert len(locals()) > 0`, which Story 20.2's review round 1 accepted as
                    # "inspects local state". MEASURED at checkpoint: `len(locals()) > 0` is False
                    # in a scope holding no locals, so the proposal turned a PASSING vacuous test
                    # into a FAILING one - and `verify_patch_dry_run` cannot see it, because the
                    # syntax is valid. There is no honest assertion to make about a span with no
                    # assertable state; AR10 says degrade visibly, so no patch is proposed.
                    continue
                new_expr = f"assert {assigned_var} is not None{msg_str}"

                new_lines[i] = f"{indent}{new_expr}{comment_part}"
                affected_lines.add(i + 1)
                transformed = True
            elif _UNITTEST_TRUE_RE.search(code_part):
                assigned_var = _find_prior_assigned_var(source_lines, i)
                msg_match = re.search(
                    r"\bself\.assertTrue\(\s*True\s*,\s*(.+)\)", code_part
                )
                msg_str = f", {msg_match.group(1).strip()}" if msg_match else ""

                if assigned_var is None:
                    continue  # no assertable state - decline, see the vacuous-assert branch
                new_expr = f"self.assertTrue({assigned_var} is not None{msg_str})"

                new_lines[i] = f"{indent}{new_expr}{comment_part}"
                affected_lines.add(i + 1)
                transformed = True
            elif _UNITTEST_EQ_RE.search(code_part):
                assigned_var = _find_prior_assigned_var(source_lines, i)
                msg_match = re.search(
                    r"\bself\.assertEqual\(\s*1\s*,\s*1\s*,\s*(.+)\)", code_part
                )
                msg_str = f", {msg_match.group(1).strip()}" if msg_match else ""

                if assigned_var is None:
                    continue  # no assertable state - decline, see the vacuous-assert branch
                new_expr = f"self.assertIsNotNone({assigned_var}{msg_str})"

                new_lines[i] = f"{indent}{new_expr}{comment_part}"
                affected_lines.add(i + 1)
                transformed = True
            elif _PASS_RE.match(code_part):
                assigned_var = _find_prior_assigned_var(source_lines, i)
                if assigned_var is None:
                    continue  # no assertable state - decline, see the vacuous-assert branch
                new_expr = f"assert {assigned_var} is not None"

                new_lines[i] = f"{indent}{new_expr}{comment_part}"
                affected_lines.add(i + 1)
                transformed = True

        if not transformed:
            # Check if span has no assertion keyword at all
            span_text = "\n".join(source_lines[start_idx:end_idx])
            if not re.search(r"\bassert\b", span_text):
                target_idx = max(start_idx, end_idx - 1)
                code_part, comment_part = _extract_comment(source_lines[target_idx])
                indent = code_part[: len(code_part) - len(code_part.lstrip())]
                assigned_var = _find_prior_assigned_var(source_lines, target_idx + 1)

                if assigned_var is None:
                    # Same decline as above: a span with no assertion AND no assignment offers
                    # nothing to assert on. `transformed` stays False, so generate_patch returns
                    # None and process_recordings records it as a miss rather than a proposal.
                    return None
                addition = f"\n{indent}assert {assigned_var} is not None{comment_part}"

                new_lines[target_idx] = source_lines[target_idx] + addition
                affected_lines.add(target_idx + 1)
                transformed = True

        if not transformed or new_lines == source_lines:
            return None

        ending = "\n" if source_code.endswith("\n") else ""
        new_source_code = "\n".join(new_lines) + ending

        orig_diff_lines = source_code.splitlines(keepends=True)
        new_diff_lines = new_source_code.splitlines(keepends=True)

        diff_lines = list(
            difflib.unified_diff(
                orig_diff_lines,
                new_diff_lines,
                fromfile=f"a/{target_file}",
                tofile=f"b/{target_file}",
            )
        )
        diff_content = "".join(diff_lines)
        if not diff_content:
            return None

        patch_id = f"patch:{recording.recording_id}"
        created_at = datetime.now(timezone.utc).isoformat()

        try:
            patch = RemediationPatch(
                finding_id=recording.recording_id,
                target_file=target_file,
                diff_content=diff_content,
                affected_lines=tuple(sorted(affected_lines)),
                patch_id=patch_id,
                created_at=created_at,
            )
        except ValueError:
            return None

        if not verify_patch_dry_run(source_code, patch):
            return None

        return patch

    def process_recordings(
        self,
        recordings: Sequence[Recording],
        source_loader: Callable[[str], str],
        dry_run: bool = True,
    ) -> RemediationResult:
        """Process a sequence of finding recordings to remediate defects (AC2, AC3)."""
        patches: list[RemediationPatch] = []
        errors: list[str] = []
        applied_count = 0
        dry_run_verified_all = True

        for rec in recordings:
            try:
                if not rec.locators:
                    errors.append(f"Recording {rec.recording_id} has no locators")
                    continue
                target_file = rec.locators[0].file_path
                source_code = source_loader(target_file)
                patch = self.generate_patch(rec, source_code)
                if patch is None:
                    errors.append(
                        f"Could not generate patch for recording {rec.recording_id}"
                    )
                    continue

                patches.append(patch)
                verified = verify_patch_dry_run(source_code, patch)
                if not verified:
                    dry_run_verified_all = False
                    errors.append(
                        f"Dry-run verification failed for patch {patch.patch_id}"
                    )

                if not dry_run and verified:
                    success = apply_patch(
                        target_file, patch, workspace_root=self.workspace_root
                    )
                    if success:
                        applied_count += 1
                    else:
                        errors.append(
                            f"Failed to apply patch {patch.patch_id} to {target_file}"
                        )
            except Exception as exc:
                errors.append(f"Error processing recording {rec.recording_id}: {exc}")

        overall_success = len(errors) == 0
        dry_run_verified = dry_run_verified_all and (
            len(patches) > 0 or len(recordings) == 0
        )

        return RemediationResult(
            patches=tuple(patches),
            success=overall_success,
            dry_run_verified=dry_run_verified,
            applied_count=applied_count,
            errors=tuple(errors),
        )
