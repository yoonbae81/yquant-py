from abc import ABC
import time
from collections import namedtuple, defaultdict

import numpy as np
import talib

from backtester import logger

Order = namedtuple('Order', 'symbol price strength timestamp')


class Ticks(object):
    def __init__(self, size=100, keep=30):
        self.keep = keep
        self.watermark = -1
        self.timestamp = -1
        self.prices = np.zeros(size, dtype=float)
        self.quantities = np.zeros(size, dtype=float)

    def __iadd__(self, tick):
        self._add(tick)
        return self

    def _add(self, tick):
        if self.timestamp == tick.timestamp:
            i = self.watermark
            self.prices[i] = tick.price
            self.quantities[i] += tick.quantity
            return

        done = False
        while not done:
            try:
                i = self.watermark + 1
                self.prices[i] = tick.price
                self.quantities[i] = tick.quantity
                self.timestamp = tick.timestamp
                self.watermark = i
                done = True

            except IndexError:  # array is full
                self._erase_old(self.prices, self.keep)
                self._erase_old(self.quantities, self.keep)
                self.watermark = self.keep - 1

    @staticmethod
    def _erase_old(arr, keep):
        """ Erases old values and keep the recent ones when the array is full

        Args:
            arr:
                an array which is full

        Returns:
            lowered watermark
        """

        # copy the recent values into the beginning of array
        for i in range(keep):
            arr[i] = arr[arr.size - keep + i]

        # delete the remaining parts of array
        for i in range(keep, arr.size):
            arr[i] = 0


class StrategyBase(ABC):
    def _calc_strength(self):
        pass

    def _calc_quantity(self):
        pass

    def _calc_stoploss(self):
        pass


def run(config, strategy, tick_queue, order_queue, log_queue):
    logger.config(log_queue)

    data = defaultdict(Ticks)

    count = 0
    while tick := tick_queue.get():
        ticks = data[tick.symbol]
        ticks += tick

        if strategy(ticks):
            order = Order(tick.symbol,
                          tick.price,
                          strategy(tick),
                          tick.timestamp)
            order_queue.put(order)

        count += 1

    logger.info(f'Analyzed {count} ticks')

    time.sleep(0.1)
    order_queue.put_nowait(None)
