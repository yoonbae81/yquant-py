import logging
from copy import copy
from enum import IntEnum
from math import copysign
from pathlib import Path

import numpy as np

from backtest.data import Msg

logger = logging.getLogger(Path(__file__).stem)


class Trade(IntEnum):
    """
    Used for [math.copysign](https://docs.python.org/3/library/math.html#math.copysign)
    """
    BUY = 1
    SELL = -1


TAX_RATES = {
    Trade.BUY: 0,
    Trade.SELL: 0.0025
}

COMMISSION_RATES = {
    Trade.BUY: 0.00015,
    Trade.SELL: 0.00015
}

PRICE_UNITS = {
    'KOSPI': [
        {'price': 1000, 'unit': 1},
        {'price': 5000, 'unit': 5},
        {'price': 10000, 'unit': 10},
        {'price': 50000, 'unit': 50},
        {'price': 100000, 'unit': 100},
        {'price': 500000, 'unit': 500},
        {'price': 999999999, 'unit': 1000}
    ],
    'KOSDAQ': [
        {'price': 1000, 'unit': 1},
        {'price': 5000, 'unit': 5},
        {'price': 10000, 'unit': 10},
        {'price': 50000, 'unit': 50},
        {'price': 999999999, 'unit': 100}
    ]
}


class KoreaExchange:
    """
    Simulates stock trading in KOSPI and KOSDAQ exchanges
    """

    def __init__(self,
                 symbols: dict,
                 slippage_mean: float = 0.5,
                 slippage_stdev: float = 0.7):

        self.symbols = symbols
        self.slippage_mean = slippage_mean
        self.slippage_stdev = slippage_stdev

    def execute_order(self, order: Msg) -> Msg:
        market: str = self._get_market(order.symbol)
        trade: Trade = Trade.BUY if order.quantity >= 0 else Trade.Sell
        slippage: float = self._simulate_slippage(market, trade, order.price)

        fill: Msg = copy(order)
        fill.type = 'FILL'
        fill.price += slippage
        fill.tax = self._calc_tax(trade, fill.price, fill.quantity)
        fill.commission = self._calc_commission(trade, fill.price, fill.quantity)
        fill.slippage = slippage

        return fill

    def _get_market(self, symbol: str, default: str = 'KOSDAQ') -> str:
        try:
            return self.symbols[symbol]['market']
        except KeyError:
            logger.warning(f'Unknown symbol: {symbol}')

        return default

    @staticmethod
    def _get_price_unit(market: str, price: float) -> float:
        items = PRICE_UNITS[market]
        for item in items:
            if price < item['price']:
                return item['unit']

        return items[-1]['unit']

    def _simulate_slippage(self, market, trade: Trade, price: float) -> float:
        mean = copysign(self.slippage_mean, trade)  # 0.5 on buy, -0.5 on sell
        stdev = self.slippage_stdev
        offset = int(np.random.normal(mean, stdev))

        return offset * self._get_price_unit(market, price)

    @staticmethod
    def _calc_tax(trade: Trade, price: float, quantity: float) -> float:
        rate = TAX_RATES[trade]
        result = round(price * abs(quantity) * rate)

        return result

    @staticmethod
    def _calc_commission(trade: Trade, price: float, quantity: float) -> float:
        rate = COMMISSION_RATES[trade]
        result = round(price * abs(quantity) * rate)

        return result
