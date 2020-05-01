from pathlib import Path

from backtest.ledger import Ledger as Sut


def test_init():
    sut = Sut(Path('../demo/ledger_dir'))

    assert sut
