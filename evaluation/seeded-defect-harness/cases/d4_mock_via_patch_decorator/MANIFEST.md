# d4_mock_via_patch_decorator

class: reaches-proves-nothing
expected: defect

Same shape as the demo, but the mock is bound via @patch(...) as an argument rather than Mock() inline (patching an unrelated stdlib target so the SUT itself stays untouched). Probes whether patch-decorator binding is recognised as mock-bound the same way Mock() is.
