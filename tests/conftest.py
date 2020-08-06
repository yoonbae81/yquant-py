import pytest

import backtest.symbols.krx as symbols_krx


@pytest.fixture(scope="session")
def symbols():
    yield symbols_krx.run()
