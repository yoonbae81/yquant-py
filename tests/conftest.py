import pytest

import backtest.utils.symbols_krx as symbols_krx


@pytest.fixture(scope="session")
def symbols():
    yield symbols_krx.run()
