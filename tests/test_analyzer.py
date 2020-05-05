from unittest.mock import patch

from backtest.analyzer import Analyzer as Sut
from backtest.data import Msg


def test_init():
    sut = Sut('dummy')
    assert sut
