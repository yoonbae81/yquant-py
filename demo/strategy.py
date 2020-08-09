import logging
from collections import defaultdict
from pathlib import Path
from typing import Optional, DefaultDict

from backtest.data import Timeseries, Position

logger = logging.getLogger(Path(__file__).stem)


# use ta-lib that downloadable from https://www.lfd.uci.edu/~gohlke/pythonlibs/
def calc_strength(ts: Timeseries, stoploss: Optional[float] = None) -> int:
    logger.debug('Calculated strength')
    return 2


def calc_stoploss(ts: Timeseries, orig: Optional[float] = None) -> float:
    logger.debug('Calculated stoploss')
    return 1


def calc_quantity(price: float, strength: int, initial_cash: float, cash: float) -> float:
    logger.debug('Calculated quantity')
    return 100
