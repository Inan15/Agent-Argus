# a4_call_in_try_except_swallowed

class: assert-nothing
expected: defect

SUT call wrapped in a swallowing try/except; even a crash would not fail this test.
