#!/usr/bin/env python3
"""Generate ~24 seeded-defect Python mini-repos for the Argus detection-rate harness (wq-188).

Each case is a standalone repo under cases/<name>/ with src/ and tests/, a single
planted defect (or none, for the clean controls), and a green pytest suite. This
script only WRITES files -- it does not run pytest or argus. See run_harness.py.
"""
from __future__ import annotations

import pathlib

HERE = pathlib.Path(__file__).resolve().parent
CASES_DIR = HERE / "cases"

# Shared SUT, byte-identical to Argus's own shipped demo (examples/demo.py) so the
# positive-control case is the demo verbatim, not a lookalike.
DEMO_SUT = '''\
def subtotal(items):
    total = 0
    for price, qty in items:
        total = total + price * qty
    return total


def apply_discount(total, rate):
    return total - (total * rate)
'''

# Every case EXCEPT the verbatim positive control uses this minimal SUT instead of
# DEMO_SUT. DEMO_SUT's own `apply_discount` is only called by the demo's own honest
# fix, never by the vacuous test -- so reusing DEMO_SUT verbatim in every case would
# make `apply_discount` an orphan in every single one, a confound unrelated to the
# defect each case is meant to isolate (and it would break the clean-control floor
# of zero findings, since the clean controls never call it either). One function,
# one seeded defect, no incidental second finding.
MINIMAL_SUT = '''\
def subtotal(items):
    total = 0
    for price, qty in items:
        total = total + price * qty
    return total
'''

# name -> dict(class=, expected=, src=, test=, notes=)
CASES: dict[str, dict] = {}


def add(name, klass, expected, src, test, notes=""):
    CASES[name] = dict(klass=klass, expected=expected, src=src, test=test, notes=notes)


# ── Class A: tests that assert nothing ───────────────────────────────────────

add(
    "a1_no_assert_at_all", "assert-nothing", "defect",
    MINIMAL_SUT,
    '''\
from src.cart import subtotal


def test_subtotal():
    subtotal([(10, 2), (5, 1)])
''',
    "Calls the SUT, discards the result, asserts nothing at all.",
)

add(
    "a2_assert_only_on_mock", "assert-nothing", "defect",
    MINIMAL_SUT,
    '''\
from unittest.mock import Mock


def test_subtotal():
    fake = Mock()
    fake.compute.return_value = 25
    assert fake.compute() == 25
''',
    "Never touches the real SUT at all -- constructs and asserts on a mock only.",
)

add(
    "a3_assert_on_literal", "assert-nothing", "defect",
    MINIMAL_SUT,
    '''\
from src.cart import subtotal


def test_subtotal():
    subtotal([(10, 2), (5, 1)])
    assert "ok"
''',
    "Calls the SUT, then asserts a hardcoded literal unrelated to the result.",
)

add(
    "a4_call_in_try_except_swallowed", "assert-nothing", "defect",
    MINIMAL_SUT,
    '''\
from src.cart import subtotal


def test_subtotal():
    try:
        subtotal([(10, 2), (5, 1)])
    except Exception:
        pass
''',
    "SUT call wrapped in a swallowing try/except; even a crash would not fail this test.",
)

add(
    "a5_assertion_after_early_return", "assert-nothing", "defect",
    MINIMAL_SUT,
    '''\
from src.cart import subtotal


def test_subtotal():
    result = subtotal([(10, 2), (5, 1)])
    if result is not None:
        return
    assert result == 25
''',
    "The assert is dead code -- an early return in the only branch ever taken skips it.",
)

add(
    "a6_test_body_is_pass", "assert-nothing", "defect",
    MINIMAL_SUT,
    '''\
def test_subtotal():
    pass
''',
    "Body is a bare `pass` -- does not even call the SUT.",
)

# ── Class B: assertions that cannot fail ─────────────────────────────────────

add(
    "b1_assert_true", "cannot-fail", "defect",
    MINIMAL_SUT,
    '''\
from src.cart import subtotal


def test_subtotal():
    subtotal([(10, 2), (5, 1)])
    assert True
''',
    "Reaches the SUT, then asserts the literal True.",
)

add(
    "b2_assert_1_eq_1", "cannot-fail", "defect",
    MINIMAL_SUT,
    '''\
from src.cart import subtotal


def test_subtotal():
    subtotal([(10, 2), (5, 1)])
    assert 1 == 1
''',
    "Reaches the SUT, then asserts a tautology unrelated to the result.",
)

add(
    "b3_assert_x_eq_x", "cannot-fail", "defect",
    MINIMAL_SUT,
    '''\
from src.cart import subtotal


def test_subtotal():
    x = subtotal([(10, 2), (5, 1)])
    assert x == x
''',
    "Binds the SUT's own result to x, then asserts x == x -- can never fail.",
)

add(
    "b4_assert_isinstance_literal", "cannot-fail", "defect",
    MINIMAL_SUT,
    '''\
from src.cart import subtotal


def test_subtotal():
    subtotal([(10, 2), (5, 1)])
    assert isinstance(5, int)
''',
    "Reaches the SUT, then asserts a type fact about a just-constructed literal.",
)

add(
    "b5_assert_on_test_defined_constant", "cannot-fail", "defect",
    MINIMAL_SUT,
    '''\
from src.cart import subtotal


def test_subtotal():
    subtotal([(10, 2), (5, 1)])
    expected = 25
    assert expected == 25
''',
    "Asserts a constant the test itself just defined, never compared to the SUT result.",
)

# ── Class C: functions nothing calls ─────────────────────────────────────────

add(
    "c1_orphan_module_level_function", "orphan", "defect",
    MINIMAL_SUT + '''

def orphan_module_level(x):
    """Nothing in this repository calls this name."""
    return x * 3
''',
    '''\
from src.cart import subtotal


def test_subtotal():
    result = subtotal([(10, 2), (5, 1)])
    assert result == 25
''',
    "A module-level function with no caller anywhere in the repo; test suite is honest.",
)

add(
    "c2_orphan_method_uninstantiated_class", "orphan", "defect",
    MINIMAL_SUT + '''

class PricingHelper:
    """Nothing in this repository ever instantiates PricingHelper."""

    def orphan_method(self, x):
        return x * 4
''',
    '''\
from src.cart import subtotal


def test_subtotal():
    result = subtotal([(10, 2), (5, 1)])
    assert result == 25
''',
    "A method on a class nobody instantiates; test suite is honest.",
)

add(
    "c3_orphan_behind_dead_import", "orphan", "defect",
    MINIMAL_SUT + '''

def orphan_behind_import(x):
    """Imported by tests/test_cart.py but never actually called."""
    return x * 5
''',
    '''\
from src.cart import subtotal, orphan_behind_import  # imported, never called


def test_subtotal():
    result = subtotal([(10, 2), (5, 1)])
    assert result == 25
''',
    "Imported (a name-reference exists) but never called -- probes whether import "
    "alone counts as a reference under the name-match reachability rule.",
)

# ── Class D: reaches the code, proves nothing -- the demo's own shape + edges ─

add(
    "d1_demo_verbatim_POSITIVE_CONTROL", "reaches-proves-nothing", "defect",
    DEMO_SUT,
    '''\
from unittest.mock import Mock

from src.cart import subtotal


def test_subtotal():
    subtotal([(10, 2), (5, 1)])
    fake = Mock()
    fake.compute.return_value = 25
    pretended = fake.compute()
    assert pretended == 25
''',
    "POSITIVE CONTROL: Argus's own shipped demo defect, verbatim (examples/demo.py). "
    "If this does not fire, the harness itself is broken.",
)

add(
    "d2_result_consumed_then_mock_assert", "reaches-proves-nothing", "defect",
    MINIMAL_SUT,
    '''\
from unittest.mock import Mock

from src.cart import subtotal


def test_subtotal():
    result = subtotal([(10, 2), (5, 1)])
    fake = Mock()
    fake.compute.return_value = 25
    pretended = fake.compute()
    assert pretended == 25
''',
    "Near-neighbour of the demo: the SUT result IS bound to a name (result) -- "
    "'consumed', not discarded -- but the assertion still only checks the mock. "
    "Same defect a human would see; probes the 'no consumed SUT call' AST clause.",
)

add(
    "d3_sut_call_nested_in_assert", "reaches-proves-nothing", "defect",
    MINIMAL_SUT,
    '''\
from unittest.mock import Mock

from src.cart import subtotal


def test_subtotal():
    fake = Mock()
    fake.compute.return_value = 25
    assert fake.compute() == subtotal([(10, 2), (5, 1)]) or True
''',
    "The SUT call is nested inside the assert expression itself (as an operand), "
    "which the AST subset counts as CONSUMED rather than discarded, though the "
    "`or True` still makes the assertion unfalsifiable. Edge probe.",
)

add(
    "d4_mock_via_patch_decorator", "reaches-proves-nothing", "defect",
    MINIMAL_SUT,
    '''\
from unittest.mock import patch

from src.cart import subtotal


@patch("time.time")
def test_subtotal(mock_time):
    subtotal([(10, 2), (5, 1)])
    mock_time.return_value = 25
    pretended = mock_time()
    assert pretended == 25
''',
    "Same shape as the demo, but the mock is bound via @patch(...) as an argument "
    "rather than Mock() inline (patching an unrelated stdlib target so the SUT itself "
    "stays untouched). Probes whether patch-decorator binding is recognised as "
    "mock-bound the same way Mock() is.",
)

add(
    "d5_mock_assert_called_with_style", "reaches-proves-nothing", "defect",
    MINIMAL_SUT,
    '''\
from unittest.mock import Mock

from src.cart import subtotal


def test_subtotal():
    subtotal([(10, 2), (5, 1)])
    fake = Mock()
    fake.compute(25)
    fake.compute.assert_called_once_with(25)
''',
    "SUT result discarded, exactly like the demo, but the assertion is a mock-method "
    "call-assertion (assert_called_once_with) rather than an equality check on the "
    "mock's return value. Probes the assertion-vocabulary edge.",
)

add(
    "d6_extra_real_call_also_discarded", "reaches-proves-nothing", "defect",
    # Own SUT (not MINIMAL_SUT): apply_discount must exist here, and this case's own
    # test DOES call it (discarding the result, same as subtotal) -- so it is
    # referenced, not an orphan. No confound with the vacuous-test defect this case
    # is meant to isolate.
    MINIMAL_SUT + '''

def apply_discount(total, rate):
    return total - (total * rate)
''',
    '''\
from unittest.mock import Mock

from src.cart import subtotal, apply_discount


def test_subtotal():
    subtotal([(10, 2), (5, 1)])
    apply_discount(25, 0.1)
    fake = Mock()
    fake.compute.return_value = 25
    pretended = fake.compute()
    assert pretended == 25
''',
    "Demo's exact defect plus a second, unrelated real SUT call, also discarded. "
    "Probes robustness to slightly busier bodies than the minimal demo shape.",
)

# ── Class E: clean controls -- must raise ZERO findings ──────────────────────

add(
    "e1_clean_real_assertion", "clean-control", "clean",
    MINIMAL_SUT,
    '''\
from src.cart import subtotal


def test_subtotal():
    result = subtotal([(10, 2), (5, 1)])
    assert result == 25
''',
    "A correct test asserting the SUT's real, computed result.",
)

add(
    "e2_clean_mock_of_external_dependency", "clean-control", "clean",
    MINIMAL_SUT + '''

def price_with_tax(items, tax_rate_source):
    """tax_rate_source is an injected dependency, e.g. a rates service."""
    rate = tax_rate_source.get_rate()
    return subtotal(items) * (1 + rate)
''',
    '''\
from unittest.mock import Mock

from src.cart import price_with_tax


def test_price_with_tax_applies_the_injected_rate():
    fake_rate_source = Mock()
    fake_rate_source.get_rate.return_value = 0.1
    result = price_with_tax([(10, 2), (5, 1)], fake_rate_source)
    assert round(result, 2) == 27.5
''',
    "Legitimate mocking: an external collaborator is mocked, but the assertion "
    "checks the REAL return value of the function under test, computed from that "
    "mocked input. Must not be flagged.",
)

add(
    "e3_clean_multi_assert_suite", "clean-control", "clean",
    MINIMAL_SUT + '''

def apply_discount(total, rate):
    return total - (total * rate)
''',
    '''\
from src.cart import subtotal, apply_discount


def test_subtotal_sums_price_times_quantity():
    assert subtotal([(10, 2), (5, 1)]) == 25


def test_subtotal_empty_cart_is_zero():
    assert subtotal([]) == 0


def test_apply_discount_reduces_total_by_rate():
    assert apply_discount(100, 0.2) == 80
''',
    "A genuinely well-asserted suite covering several real behaviours.",
)

add(
    "e4_clean_no_orphans", "clean-control", "clean",
    MINIMAL_SUT + '''

def price_summary(items):
    """Used by tests below -- not an orphan."""
    return f"total: {subtotal(items)}"
''',
    '''\
from src.cart import subtotal, price_summary


def test_subtotal():
    assert subtotal([(10, 2), (5, 1)]) == 25


def test_price_summary_formats_the_total():
    assert price_summary([(10, 2), (5, 1)]) == "total: 25"
''',
    "Every function defined is genuinely called by the test suite; orphan detector "
    "must stay silent.",
)


def write_case(name: str, case: dict) -> None:
    root = CASES_DIR / name
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / "src" / "__init__.py").write_text("", encoding="utf-8")
    (root / "src" / "cart.py").write_text(case["src"], encoding="utf-8")
    (root / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (root / "tests" / "test_cart.py").write_text(case["test"], encoding="utf-8")
    (root / "MANIFEST.md").write_text(
        f"# {name}\n\nclass: {case['klass']}\nexpected: {case['expected']}\n\n"
        f"{case['notes']}\n",
        encoding="utf-8",
    )


def main() -> None:
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    for name, case in CASES.items():
        write_case(name, case)
    print(f"wrote {len(CASES)} cases under {CASES_DIR}")


if __name__ == "__main__":
    main()
