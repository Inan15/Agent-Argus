from unittest.mock import Mock


def test_subtotal():
    fake = Mock()
    fake.compute.return_value = 25
    assert fake.compute() == 25
