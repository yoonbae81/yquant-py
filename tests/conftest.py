import pytest

import backtest.utils.korea_symbols as s


@pytest.fixture(scope="session")
def symbols():
    yield s.run()
