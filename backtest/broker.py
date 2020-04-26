import logging
from collections import defaultdict
from importlib import import_module
from math import copysign
from multiprocessing.connection import Connection
from pathlib import Path
from threading import Thread
from typing import Callable, Dict, DefaultDict

from .data import Msg, Positions

logger = logging.getLogger(Path(__file__).name)


class Broker(Thread):

    def __init__(self, market: str, strategy: str, initial_cash: float) -> None:
        super().__init__(name=self.__class__.__name__)

        self.input: Connection
        self.output: Connection

        self._loop: bool = True
        self._market_name = market
        self._strategy_name = strategy
        self._cash: float = initial_cash
        self._initial_cash: float = initial_cash
        self._positions: Positions = Positions()

        self._handlers: Dict[str, Callable[[Msg], None]] = {
            'SIGNAL': self._handler_signal,
            'QUIT': self._handler_quit,
        }

        logger.debug(self.name + ' initialized')

    def run(self):
        logger.debug(self.name + ' started')

        logger.debug(f'Loading market: {self._market_name}')
        self._market = import_module('market.' + self._market_name)

        logger.debug(f'Loading strategy: {self._strategy_name}')
        self._strategy = import_module('strategy.' + self._strategy_name)

        self.output.send(Msg('CASH', cash=self._initial_cash))

        while self._loop:
            msg = self.input.recv()
            logger.debug(f'{self.name} received: {msg}')
            self._handlers[msg.type](msg)

    def _handler_signal(self, msg: Msg) -> None:
        quantity = self._strategy.calc_quantity(
            msg.strength,
            self._cash,
            self._positions)

        market = self._market.get_market(msg.symbol)

        price = self._market.simulate_price(
            market,
            msg.price,
            quantity)

        commission = self._market.calc_commission(
            market,
            price,
            quantity)

        tax = self._market.calc_tax(
            market,
            price,
            quantity)

        self._cash -= self._calc_total_cost(price, quantity, commission, tax)
        self._positions[msg.symbol].quantity += quantity

        self.output.send(
            Msg("ORDER",
                symbol=msg.symbol,
                price=price,
                quantity=quantity,
                strength=msg.strength,
                commission=commission,
                tax=tax,
                slippage=msg.price - price,
                cash=self._cash,
                timestamp=msg.timestamp))

        self.output.send(
            Msg('QUANTITY',
                symbol=msg.symbol,
                quantity=self._positions[msg.symbol].quantity))

    def _handler_quit(self, _: Msg) -> None:
        self._loop = False

    @staticmethod
    def _calc_total_cost(price: float, quantity: float, commission: float, tax: float) -> float:
        return copysign(1, quantity) \
               * (abs(quantity)
                  * price
                  + commission
                  + tax)
