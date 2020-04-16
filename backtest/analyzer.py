import json
import queue
import logging
import logging.config

from collections import defaultdict
from logging.handlers import QueueHandler
from multiprocessing import Event
from os import path

from .data import Tick, RESET, Stock, Order

logger = logging.getLogger('analyzer')


def run(config, strategy, cash, quantity_dict, tick_queue, order_queue, log_queue, done: Event):
    _init_logger(log_queue)

    stock_dict = defaultdict(Stock)

    count = 0
    while not done.is_set():
        try:
            t = tick_queue.get(block=True, timeout=1)
            count += 1
        except queue.Empty:
            continue

        if t == RESET:
            [s.erase_timeseries() for s in stock_dict.values()]
            continue

        stock = stock_dict[t.symbol]
        stock += t

        holding = quantity_dict.get(t.symbol, 0)
        if holding > 0 and t.price < stock.stoploss:
            quantity = strategy.calc_quantity_to_sell(holding, stock)
        else:
            quantity = strategy.calc_quantity_to_buy(config['initial_cash'], cash.value, holding, stock)

        if abs(quantity) > 0:
            order = Order(t.symbol, t.price, quantity, t.timestamp)
            order_queue.put(order)

        if quantity > 0 or holding > 0:
            stock.stoploss = strategy.calc_stoploss(stock)

    logger.info(f'Analyzed {count} ticks')


def _init_logger(log_queue):
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, 'logging.json')) as f:
        logging.config.dictConfig(json.load(f))
