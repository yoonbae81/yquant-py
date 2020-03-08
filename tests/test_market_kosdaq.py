import pytest

import backtester.market.kosdaq as sut


@pytest.mark.parametrize('input, expected', [
    (999, 1),
    (1000, 5),
    (4999, 5),
    (5000, 10),
    (10000, 50),
    (50000, 100),
    (100000, 100),
    (499999, 100),
    (500000, 100),
])
def test_get_unit_price(input, expected):
    actual = sut._get_unit_price(input)
    assert actual == expected
