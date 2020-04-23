import json
import queue

from multiprocessing import Event
from pathlib import Path

import logging
from .data import Tick, RESET, Stock, Signal

logger = logging.getLogger('analyzer')


def run(symbols, strategy, quantity_dict, tick_queue, signal_queue, done: Event):

    stock_dict = {}
    count = 0
    while not done.is_set():
        try:
            tick = tick_queue.get(block=True, timeout=1)
        except queue.Empty:
            continue

        if tick == RESET:
            [s.erase_timeseries() for s in stock_dict.values()]
            continue

        try:
            stock = stock_dict[tick.symbol]
        except KeyError:
            stock = Stock(tick.symbol, symbols.get(tick.symbol, 'KOSPI'))
            stock_dict[tick.symbol] = stock

        stock += tick
        count += 1

        holding = quantity_dict.get(tick.symbol, 0)
        if holding > 0:
            stock.stoploss = strategy.calc_stoploss(stock)

        strength = strategy.calc_strength(stock)
        signal = Signal(stock.symbol,
                        stock.market,
                        tick.price,
                        strength,
                        tick.timestamp)
        signal_queue.put(signal)

    logger.info(f'Analyzed {count} ticks')
