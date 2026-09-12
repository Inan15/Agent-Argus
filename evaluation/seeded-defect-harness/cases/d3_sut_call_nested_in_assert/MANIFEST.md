# d3_sut_call_nested_in_assert

class: reaches-proves-nothing
expected: defect

The SUT call is nested inside the assert expression itself (as an operand), which the AST subset counts as CONSUMED rather than discarded, though the `or True` still makes the assertion unfalsifiable. Edge probe.
