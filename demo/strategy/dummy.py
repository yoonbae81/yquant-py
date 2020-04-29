from typing import Optional

from backtest.data import Timeseries, Positions


# could use ta-lib that downloadable from https://www.lfd.uci.edu/~gohlke/pythonlibs/
def calc_strength(ts: Timeseries) -> int:
    return 2


def calc_stoploss(ts: Timeseries, original: Optional[float] = None) -> float:
    return 1


def calc_quantity(price: float, strength: int, cash: float, positions: Positions) -> float:
    return 100
