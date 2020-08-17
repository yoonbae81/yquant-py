import argparse
import logging
import json
import sys
from pathlib import Path
from typing import Optional

import backtest.launcher
from backtest.data import Msg, Timeseries, Position
from backtest.strategies import Strategy
from backtest.exchanges import Exchange
from backtest.exchanges.korea_exchange import KoreaExchange

logger = logging.getLogger(Path(__file__).stem)


class MomentumStrategy():
    def __init__(self):
        pass

    def handle(self, msg: Msg, cash: float, timeseries: Timeseries, position: Position) -> Msg:
        if position.quantity > 0:
            position.stoploss = self.calc_stoploss(
                timeseries, position.stoploss)

        strength = self.calc_strength(
            timeseries,
            position.stoploss)

        quantity = self.calc_quantity(
            msg.price,
            msg.strength,
            cash)

        order = Msg('ORDER',
                    symbol=msg.symbol,
                    price=msg.price,
                    quantity=quantity,
                    strength=strength,
                    timestamp=msg.timestamp)

        return order

    def calc_strength(self, ts: Timeseries, stoploss: Optional[float] = None) -> int:
        logger.debug('Calculated strength')
        return 2

    def calc_stoploss(self, ts: Timeseries, orig: Optional[float] = None) -> float:
        logger.debug('Calculated stoploss')
        return 1

    def calc_quantity(self, price: float, strength: int, cash: float) -> float:
        # TODO Required initial cash
        logger.debug('Calculated quantity')
        return 100


def main(args):
    with Path(args.symbols_json).open('rt', encoding='utf-8') as f:
        symbols = json.load(f)

    exchange: Exchange = KoreaExchange(symbols)
    strategy: Strategy = MomentumStrategy()

    backtest.launcher.run(
        exchange,
        strategy,
        1_000_000,
        'ticks/',
        'ledger/'
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--symbols_json', default='symbols.json')
    args = parser.parse_args(sys.argv[1:])

    sys.exit(main(args))
