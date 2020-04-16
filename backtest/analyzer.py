import json
import logging.config
import queue

from multiprocessing import Event
from pathlib import Path

from .data import Tick, RESET, Stock, Order

with Path(__file__).parent.joinpath('logging.json').open() as f:
    logging.config.dictConfig(json.load(f))

logger = logging.getLogger('analyzer')


def run(symbols, strategy, cash, quantity_dict, tick_queue, order_queue, done: Event):
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
        if holding > 0 and tick.price < stock.stoploss:
            quantity = strategy.calc_quantity_to_sell(holding, stock)
        else:
            quantity = strategy.calc_quantity_to_buy(cash.value, holding, stock)

        if abs(quantity) > 0:
            order = Order(stock.symbol, stock.market, tick.price, quantity, tick.timestamp)
            order_queue.put(order)

        if quantity > 0 or holding > 0:
            stock.stoploss = strategy.calc_stoploss(stock)

    logger.info(f'Analyzed {count} ticks')
