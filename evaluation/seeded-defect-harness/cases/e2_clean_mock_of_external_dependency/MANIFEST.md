# e2_clean_mock_of_external_dependency

class: clean-control
expected: clean

Legitimate mocking: an external collaborator is mocked, but the assertion checks the REAL return value of the function under test, computed from that mocked input. Must not be flagged.
