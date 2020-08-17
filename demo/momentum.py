import logging
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

import backtest.launcher
from backtest.data import Timeseries
from backtest.exchanges.korea_exchange import KoreaExchange

logger = logging.getLogger(Path(__file__).stem)


def calc_strength(ts: Timeseries, stoploss: Optional[float] = None) -> int:
    """ use ta-lib that downloadable from https://www.lfd.uci.edu/~gohlke/pythonlibs/
    """
    logger.debug('Calculated strength')
    return 2


def calc_stoploss(ts: Timeseries, orig: Optional[float] = None) -> float:
    logger.debug('Calculated stoploss')
    return 1


def calc_quantity(price: float, strength: int, initial_cash: float, cash: float) -> float:
    logger.debug('Calculated quantity')
    return 100


if __name__ == '__main__':
    symbols_json = 'symbols.json'
    with Path(symbols_json).open('rt', encoding='utf-8') as f:
        symbols = json.load(f)

    exchange = KoreaExchange(symbols)
    strategy = SimpleNamespace(
        calc_strength=calc_strength,
        calc_stoploss=calc_stoploss,
        calc_quantity=calc_quantity
    )

    backtest.launcher.run(
        exchange,
        strategy,
        1_000_000,
        'ticks/',
        'ledger/'
    )
