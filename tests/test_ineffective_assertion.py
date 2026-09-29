"""wq-1084 — family A: a test with no effective assertion on the code under test BLOCKS.

Verification area ArgusAgent-DETECT (``-170``..``-184``, and ``-187``..``-190`` added by
wq-1127 for the runner-may-skip exit and the validating-callee narrowing). Drivers:
``argus/detectors/ineffective_assertion.py`` (four facts, their exits, and the wq-1083
measurement that forced fact 4's callee-purity bar), ``evaluation/seeded-defect-harness/``
(``a1``/``a2``/``a4``/``a5``/``a6`` are planted verbatim in ``-170``), cross-cutting #6 (every
exit has its own silent case).

The SYNTHETIC cases are deliberately NOT harness shapes: other modules, other names, other
spellings of each fact, each paired with a near neighbour that must stay silent. They are what
shows the rules fire on the shape and not on the harness's text.

Every case stands up the REAL Story-1.4 index via ``build_ast_index`` and runs the real
detector; the end-to-end cases (``-183``/``-184``) run ``run_audit_detailed``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("tree_sitter")
pytest.importorskip("tree_sitter_python")

from argus.detectors.ineffective_assertion import (  # noqa: E402
    RULE_ASSERTION_ABSENT,
    RULE_ASSERTION_AFTER_RETURN,
    RULE_ASSERTION_ON_MOCK_ONLY,
    RULE_ASSERTION_SWALLOWED,
    IneffectiveAssertionDetector,
)
from argus.detectors.tautological_assertion import RULE_TAUTOLOGICAL_ASSERTION  # noqa: E402
from argus.detectors.vacuous_test import RULE_AST  # noqa: E402
from argus.index.ast_index import build_ast_index  # noqa: E402
from argus.ledger.coverage_ledger import CoverageDepth  # noqa: E402
from argus.models import AuditRequest  # noqa: E402
from argus.pipeline import run_audit_detailed  # noqa: E402
from argus.verdict.verdict_gate import is_verdict_blocking  # noqa: E402

_TEST = "tests/test_subject.py"
_SUT = """def subtotal(items):
    total = 0
    for price, qty in items:
        total = total + price * qty
    return total
"""


def _write(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _flagged(tmp_path: Path, test_source: str, modules: dict[str, str] | None = None) -> dict[str, str]:
    """Test name → rule id for every test the detector blocks (asserting each one blocks)."""
    files = {_TEST: test_source, **(modules or {})}
    _write(tmp_path, files)
    python_files = tuple(sorted(rel for rel in files if rel.endswith(".py")))
    entry = {e.file_path: e for e in build_ast_index(tmp_path, python_files).entries}[_TEST]
    result = IneffectiveAssertionDetector().run(
        file_path=_TEST, source=test_source, ast_entry=entry, module_sources=modules or {}
    )
    out = {}
    for finding in result.findings:
        assert finding.depth_supported is CoverageDepth.AUDITED_SHALLOW
        assert is_verdict_blocking(finding)
        name = finding.locators[0].ast_span.split(":", 1)[1].split("@", 1)[0]  # type: ignore[union-attr]
        out[name] = finding.rule_id
    return out


# ── the harness shapes, verbatim ────────────────────────────────────────────────────────────

_HARNESS = {
    "a1": ("from src.cart import subtotal\n\n\ndef test_subtotal():\n    subtotal([(10, 2), (5, 1)])\n", RULE_ASSERTION_ABSENT),
    "a2": (
        "from unittest.mock import Mock\n\n\ndef test_subtotal():\n    fake = Mock()\n"
        "    fake.compute.return_value = 25\n    assert fake.compute() == 25\n",
        RULE_ASSERTION_ON_MOCK_ONLY,
    ),
    "a4": (
        "from src.cart import subtotal\n\n\ndef test_subtotal():\n    try:\n        subtotal([(10, 2), (5, 1)])\n"
        "    except Exception:\n        pass\n",
        RULE_ASSERTION_SWALLOWED,
    ),
    "a5": (
        "from src.cart import subtotal\n\n\ndef test_subtotal():\n    result = subtotal([(10, 2), (5, 1)])\n"
        "    if result is not None:\n        return\n    assert result == 25\n",
        RULE_ASSERTION_AFTER_RETURN,
    ),
    "a6": ("def test_subtotal():\n    pass\n", RULE_ASSERTION_ABSENT),
}


@pytest.mark.parametrize("case", sorted(_HARNESS))
def test_harness_shapes_block(tmp_path: Path, case: str) -> None:
    """TC-ArgusAgent-DETECT-001-170 — the five harness shapes of family A, verbatim, each block."""
    source, rule = _HARNESS[case]
    assert _flagged(tmp_path, source, {"src/cart.py": _SUT}) == {"test_subtotal": rule}


# ── 1. swallowed ────────────────────────────────────────────────────────────────────────────


def test_synthetic_swallowed_assertion_blocks(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-171 — an ``assert`` INSIDE the ``try``: ``AssertionError`` is swallowed too."""
    source = (
        "from inventory.stock import reserve\n\n\n"
        "def test_reserve_reduces_stock():\n"
        "    try:\n"
        '        left = reserve("sku-1", 3)\n'
        "        assert left == 7\n"
        "    except (KeyError, BaseException):\n"
        "        print('reserve failed')\n"
    )
    assert _flagged(tmp_path, source) == {"test_reserve_reduces_stock": RULE_ASSERTION_SWALLOWED}


def test_synthetic_handler_that_fails_stays_silent(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-172 — a handler that fails, a narrow ``except``, an ``else`` assert,
    and best-effort cleanup beside a real assertion are each silent."""
    source = (
        "import pytest\n"
        "from inventory.stock import reserve, release\n\n\n"
        "def test_handler_fails():\n"
        "    try:\n"
        '        reserve("sku-1", 3)\n'
        "    except Exception as exc:\n"
        "        pytest.fail(str(exc))\n\n\n"
        "def test_narrow_except():\n"
        "    try:\n"
        '        reserve("sku-1", 3)\n'
        "    except KeyError:\n"
        "        pass\n\n\n"
        "def test_assert_in_else():\n"
        "    try:\n"
        '        left = reserve("sku-1", 3)\n'
        "    except Exception:\n"
        "        left = None\n"
        "    else:\n"
        "        assert left == 7\n\n\n"
        "def test_cleanup_is_best_effort():\n"
        '    left = reserve("sku-1", 3)\n'
        "    try:\n"
        '        release("sku-1", 3)\n'
        "    except Exception:\n"
        "        pass\n"
        "    assert left == 7\n"
    )
    assert _flagged(tmp_path, source) == {}


# ── 2. after return ─────────────────────────────────────────────────────────────────────────


def test_synthetic_assertion_after_return_blocks(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-173 — an unconditional ``return``, and a guard on the value under test."""
    source = (
        "from ledger.io import load_rows, parse_header\n\n\n"
        "def test_header_version():\n"
        '    header = parse_header(b"V2")\n'
        "    return\n"
        "    assert header == 2\n\n\n"
        "def test_first_row():\n"
        '    rows = load_rows("fixtures/a.csv")\n'
        "    if not rows:\n"
        "        return None\n"
        '    assert rows[0] == ("a", 1)\n'
    )
    assert _flagged(tmp_path, source) == {
        "test_header_version": RULE_ASSERTION_AFTER_RETURN,
        "test_first_row": RULE_ASSERTION_AFTER_RETURN,
    }


def test_synthetic_environment_guard_stays_silent(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-174 — a guard on the platform or a stdlib lookup is a skip, not a dodge;
    a guard after an assertion and a ``return`` with a value are not this fact either."""
    source = (
        "import shutil\n"
        "import sys\n"
        "from ledger.io import load_rows\n\n\n"
        "def test_platform_guard():\n"
        '    if sys.platform == "win32":\n'
        "        return\n"
        '    assert load_rows("a.csv") == []\n\n\n'
        "def test_tool_guard():\n"
        '    git = shutil.which("git")\n'
        "    if git is None:\n"
        "        return\n"
        '    assert load_rows(git) == []\n\n\n'
        "def test_asserts_before_guard():\n"
        '    rows = load_rows("a.csv")\n'
        "    assert rows is not None\n"
        "    if not rows:\n"
        "        return\n"
        '    assert rows[0] == ("a", 1)\n'
    )
    assert _flagged(tmp_path, source) == {}


# ── 3. mock only ────────────────────────────────────────────────────────────────────────────


def test_synthetic_mock_only_assertion_blocks(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-175 — every value asserted is read off a mock the test built and kept."""
    source = (
        "from unittest import mock\n"
        "from notify.email import notify\n\n\n"
        "def test_sends_email():\n"
        '    notify("ops@example.invalid")\n'
        "    mailer = mock.MagicMock()\n"
        "    mailer.send.return_value = True\n"
        '    sent = mailer.send("ops@example.invalid")\n'
        "    assert sent is True\n"
        "    assert mailer.send.call_count == 1\n"
    )
    assert _flagged(tmp_path, source) == {"test_sends_email": RULE_ASSERTION_ON_MOCK_ONLY}


def test_synthetic_mock_that_escapes_stays_silent(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-176 — a mock handed to the code under test (argument, attribute,
    ``patch.object``) is interaction testing; a mock-fed REAL result (control ``e2``) is a real assert."""
    source = (
        "from unittest.mock import MagicMock, Mock, patch\n"
        "from notify.email import Notifier, notify, price_with_tax\n\n\n"
        "def test_argument():\n"
        "    mailer = MagicMock()\n"
        '    notify(mailer, "ops@example.invalid")\n'
        "    assert mailer.send.called\n\n\n"
        "def test_attribute():\n"
        "    mailer = MagicMock()\n"
        "    n = Notifier()\n"
        "    n.mailer = mailer\n"
        '    n.run("ops@example.invalid")\n'
        "    assert mailer.send.called\n\n\n"
        "def test_patch_object():\n"
        "    mailer = MagicMock()\n"
        '    with patch.object(Notifier, "mailer", mailer):\n'
        '        Notifier().run("ops@example.invalid")\n'
        "    assert mailer.send.called\n\n\n"
        "def test_mock_fed_real_result():\n"
        "    rates = Mock()\n"
        "    rates.get_rate.return_value = 0.1\n"
        "    result = price_with_tax([(10, 2), (5, 1)], rates)\n"
        "    assert round(result, 2) == 27.5\n"
    )
    assert _flagged(tmp_path, source) == {}


# ── 4. absent ───────────────────────────────────────────────────────────────────────────────

_SLUG = 'def slugify(title):\n    return "-".join(_words(title))\n\n\ndef _words(title):\n    return title.lower().split()\n'
_ENFORCE = (
    "def enforce(limit):\n    if limit < 0:\n        raise ValueError(limit)\n    return limit\n\n\n"
    "def audit(event):\n    event.store()\n    return event\n"
)


def test_synthetic_discarded_pure_call_blocks(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-177 — the callee's own source has no failure signal but its value,
    and the test throws that value away; a placeholder ``...`` body cannot fail at all."""
    source = (
        "from text.slug import slugify as make_slug\n\n\n"
        "class TestSlug:\n"
        "    def test_slugify(self):\n"
        '        """Slugs are lowercase."""\n'
        '        make_slug("Hello World")\n\n\n'
        "def test_placeholder():\n"
        '    """TODO."""\n'
        "    ...\n"
    )
    assert _flagged(tmp_path, source, {"text/slug.py": _SLUG}) == {
        "test_slugify": RULE_ASSERTION_ABSENT,
        "test_placeholder": RULE_ASSERTION_ABSENT,
    }


def test_synthetic_should_not_raise_stays_silent(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-178 — wq-1083's nine false blocks: a callee that raises, a method,
    an import smoke test, a callee not handed in, a fixture argument, a skip marker."""
    source = (
        "import pytest\n"
        "from policy.limits import enforce, audit\n"
        "from text.slug import slugify\n"
        "from vendor.lib import compress\n\n\n"
        "def test_enforce_accepts_valid():\n"
        "    enforce(5)\n\n\n"
        "def test_audit_stores():\n"
        "    audit(None)\n\n\n"
        "def test_import_smoke():\n"
        "    from policy import limits  # noqa: F401\n\n\n"
        "def test_callee_not_visible():\n"
        '    compress(b"abc")\n\n\n'
        "def test_with_fixture(tmp_path):\n"
        '    slugify("Hello")\n\n\n'
        '@pytest.mark.skip(reason="not yet")\n'
        "def test_skipped_placeholder():\n"
        "    pass\n\n\n"
        "def test_non_literal_argument():\n"
        "    title = object()\n"
        "    slugify(title)\n"
    )
    modules = {"policy/limits.py": _ENFORCE, "text/slug.py": _SLUG}
    assert _flagged(tmp_path, source, modules) == {}


def test_same_file_helper_and_fixture_data_stay_silent(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-179 — a same-file helper may assert; a module no runner collects is data."""
    source = (
        "from unittest.mock import Mock\n\n\n"
        "def _ensure(m):\n"
        "    assert m.x == 1\n\n\n"
        "def run_checks(m):\n"
        "    assert m.x == 1\n\n\n"
        "def test_delegates():\n"
        "    fake = Mock()\n"
        "    fake.x = 1\n"
        "    run_checks(fake)\n"
    )
    assert _flagged(tmp_path, source) == {}
    data = tmp_path / "data"
    data.mkdir()
    _write(data, {"tests/fixtures/load/dispatch_check.py": "def test_dispatch_under_load():\n    pass\n"})
    rel = "tests/fixtures/load/dispatch_check.py"
    entry = build_ast_index(data, (rel,)).entries[0]
    result = IneffectiveAssertionDetector().run(
        file_path=rel, source="def test_dispatch_under_load():\n    pass\n", ast_entry=entry
    )
    assert result.findings == ()


def test_one_finding_per_test_in_rule_order(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-180 — a test matching two facts carries ONE finding, the first in order."""
    source = (
        "from unittest.mock import Mock\n\n\n"
        "def test_both():\n"
        "    fake = Mock()\n"
        "    try:\n"
        "        assert fake.run() == 1\n"
        "    except Exception:\n"
        "        pass\n"
    )
    assert _flagged(tmp_path, source) == {"test_both": RULE_ASSERTION_SWALLOWED}


def test_without_module_sources_absent_b_is_silent(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-181 — no callee source, no purity fact: ``a1`` stays silent."""
    source = _HARNESS["a1"][0]
    assert _flagged(tmp_path, source, None) == {}


def test_relative_import_resolves(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-182 — ``from .slug import slugify`` resolves beside the test file."""
    source = 'from .slug import slugify\n\n\ndef test_slugify():\n    slugify("A B")\n'
    assert _flagged(tmp_path, source, {"tests/slug.py": _SLUG}) == {"test_slugify": RULE_ASSERTION_ABSENT}


# ── a test the runner may skip (wq-1127) ────────────────────────────────────────────────────

_SKIPPED_BODIES = (
    "        pass\n",
    '        slugify("Hello World")\n',
    '        try:\n            slugify("A")\n        except Exception:\n            pass\n',
)


@pytest.mark.parametrize("body", _SKIPPED_BODIES, ids=["absent-a", "absent-b", "swallowed"])
@pytest.mark.parametrize(
    "wrap",
    [
        "import pytest\n\n\n@pytest.mark.skip(reason='later')\nclass TestLater:\n    def test_later(self):\n{body}",
        "import unittest\n\n\n@unittest.skipIf(True, 'later')\nclass TestLater(unittest.TestCase):\n"
        "    def test_later(self):\n{body}",
        "import pytest\n\n\nclass TestLater:\n    pytestmark = pytest.mark.skip(reason='later')\n\n"
        "    def test_later(self):\n{body}",
        "import pytest\n\npytestmark = pytest.mark.skip(reason='later')\n\n\nclass TestLater:\n"
        "    def test_later(self):\n{body}",
        "import sys\n\nimport pytest\n\nif sys.platform == 'win32':\n"
        "    pytest.skip('posix only', allow_module_level=True)\n\n\nclass TestLater:\n    def test_later(self):\n{body}",
        "import pytest\n\nnumpy = pytest.importorskip('numpy')\n\n\nclass TestLater:\n    def test_later(self):\n{body}",
        "import pytest\n\n\nclass TestLater:\n    @pytest.mark.xfail(reason='known bug')\n    def test_later(self):\n{body}",
    ],
    ids=["class-skip", "class-unittest-skipif", "class-pytestmark", "module-pytestmark", "module-skip",
         "module-importorskip", "own-xfail"],
)
def test_runner_may_skip_stays_silent(tmp_path: Path, wrap: str, body: str) -> None:
    """TC-ArgusAgent-DETECT-001-187 — wq-1091 probes p2/p3 and their neighbours: a skip reaching
    the test from its class, a ``pytestmark``, a module-level skip or its own xfail marker keeps
    every family-A fact silent; a test the runner does not run is not a test that passes."""
    source = "from text.slug import slugify\n" + wrap.format(body=body)
    assert _flagged(tmp_path, source, {"text/slug.py": _SLUG}) == {}


def test_undecorated_class_still_blocks(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-188 — the class read is an exit only when something can skip:
    a plain ``TestCase`` method whose body is ``pass`` under a "Skipped:" comment (Minions'
    ``tests/test_remaining_engines.py:566`` shape) is not skipped; it runs and passes."""
    source = (
        "import unittest\n\n\nclass TestLater(unittest.TestCase):\n"
        "    def test_later(self):\n        # Skipped: not implemented\n        pass\n"
    )
    assert _flagged(tmp_path, source) == {"test_later": RULE_ASSERTION_ABSENT}


def test_should_not_raise_on_a_validating_callee_stays_silent(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-189 — a callee that runs its input through a builtin which rejects
    a well-typed value (``int``, ``float``, ``max``) validates it: feeding it a valid literal and
    discarding the value is a "should not raise" test. Import-smoke through ``importlib`` stays
    silent too; the ``slugify`` neighbour (``lower``/``split``/``join`` only) still blocks."""
    ports = (
        "def parse_port(text):\n    return int(text.strip())\n\n\n"
        "def parse_ratio(text):\n    return float(text)\n\n\n"
        "def widest(values):\n    return max(len(v) for v in values)\n"
    )
    source = (
        "from importlib import import_module\n"
        "from net.ports import parse_port, parse_ratio, widest\n"
        "from text.slug import slugify\n\n\n"
        "def test_parse_port_accepts_valid():\n"
        '    parse_port(" 8080 ")\n\n\n'
        "def test_parse_ratio_accepts_valid():\n"
        '    parse_ratio("0.5")\n\n\n'
        "def test_widest_accepts_non_empty():\n"
        '    widest(["a", "bb"])\n\n\n'
        "def test_module_imports():\n"
        '    import_module("net.ports")\n\n\n'
        "def test_slugify():\n"
        '    slugify("Hello World")\n'
    )
    modules = {"net/ports.py": ports, "text/slug.py": _SLUG}
    assert _flagged(tmp_path, source, modules) == {"test_slugify": RULE_ASSERTION_ABSENT}


# ── end to end ──────────────────────────────────────────────────────────────────────────────


def _blocking(repo: Path) -> list[tuple[str, str, int]]:
    request = AuditRequest(repo_path=str(repo), commit="HEAD", budget=0, materiality_bar="")
    verdict = run_audit_detailed(request).verdict
    return [
        (f.rule_id, f.locators[0].file_path, f.locators[0].start_line)
        for f in verdict.ordered_findings
        if is_verdict_blocking(f)
    ]


def test_pipeline_blocks_both_families_and_spares_clean_control(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-183 — through ``run_audit_detailed``: family A (with the callee
    resolved from the repository) and family B block; the ``e1`` control does not."""
    seeded = tmp_path / "seeded"
    _write(seeded, {
        "src/__init__.py": "",
        "src/cart.py": _SUT,
        "tests/__init__.py": "",
        "tests/test_cart.py": (
            "from src.cart import subtotal\n\n\n"
            "def test_discarded():\n    subtotal([(10, 2)])\n\n\n"
            "def test_true():\n    subtotal([(10, 2)])\n    assert True\n"
        ),
    })
    assert sorted(_blocking(seeded)) == [
        (RULE_ASSERTION_ABSENT, "tests/test_cart.py", 4),
        (RULE_TAUTOLOGICAL_ASSERTION, "tests/test_cart.py", 8),
    ]
    control = tmp_path / "control"
    _write(control, {
        "src/__init__.py": "",
        "src/cart.py": _SUT,
        "tests/__init__.py": "",
        "tests/test_cart.py": (
            "from src.cart import subtotal\n\n\n"
            "def test_subtotal():\n    result = subtotal([(10, 2), (5, 1)])\n    assert result == 25\n"
        ),
    })
    assert _blocking(control) == []


def test_pipeline_keeps_the_demo_span_to_one_finding(tmp_path: Path) -> None:
    """TC-ArgusAgent-DETECT-001-184 — the demo shape (``d1``) is ALSO mock-only; the span already
    carries ``vacuous_test_ast``, so family A does not re-accuse it and the headline is unchanged."""
    repo = tmp_path / "demo"
    _write(repo, {
        "src/__init__.py": "",
        "src/cart.py": _SUT,
        "tests/__init__.py": "",
        "tests/test_cart.py": (
            "from unittest.mock import Mock\n\nfrom src.cart import subtotal\n\n\n"
            "def test_subtotal():\n    subtotal([(10, 2), (5, 1)])\n    fake = Mock()\n"
            "    fake.compute.return_value = 25\n    pretended = fake.compute()\n    assert pretended == 25\n"
        ),
    })
    assert _blocking(repo) == [(RULE_AST, "tests/test_cart.py", 6)]


@pytest.mark.parametrize(
    "tests",
    [
        {"tests/test_cart.py": "import pytest\n\n\n@pytest.mark.skip(reason='refunds')\nclass TestRefunds:\n"
         "    def test_refund_pending(self):\n        pass\n"},
        {"tests/test_refunds.py": "import pytest\n\npytestmark = pytest.mark.skip(reason='refunds')\n\n\n"
         "def test_refund_pending():\n    pass\n"},
    ],
    ids=["p2-class-level-skip", "p3-module-pytestmark"],
)
def test_pipeline_does_not_block_wq1091_p2_p3(tmp_path: Path, tests: dict[str, str]) -> None:
    """TC-ArgusAgent-DETECT-001-190 — wq-1091 probes p2 and p3 through ``run_audit_detailed``:
    after wq-1120 they blocked ONLY through ``assertion_absent``; now nothing blocks."""
    repo = tmp_path / "probe"
    _write(repo, {
        "src/__init__.py": "",
        "src/cart.py": _SUT,
        "tests/__init__.py": "",
        "tests/test_subtotal.py": (
            "from src.cart import subtotal\n\n\ndef test_subtotal():\n    assert subtotal([(10, 2), (5, 1)]) == 25\n"
        ),
        **tests,
    })
    assert _blocking(repo) == []
