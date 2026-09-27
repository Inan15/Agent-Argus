# d2_result_consumed_then_mock_assert

class: reaches-proves-nothing
expected: defect

Near-neighbour of the demo: the SUT result IS bound to a name (result) -- 'consumed', not discarded -- but the assertion still only checks the mock. Same defect a human would see; probes the 'no consumed SUT call' AST clause.
