# a5_assertion_after_early_return

class: assert-nothing
expected: defect

The assert is dead code -- an early return in the only branch ever taken skips it.
