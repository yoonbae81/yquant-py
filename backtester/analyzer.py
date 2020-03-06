import time
from collections import defaultdict

from backtester import logger
from backtester.data import History, Order


def run(config, strategy, cash, quantity_dict, tick_queue, order_queue, log_queue):
    logger.config(log_queue)
    history_dict = defaultdict(History)
    stoploss_dict = defaultdict(float)

    count = 0
    while tick := tick_queue.get():
        stoploss = stoploss_dict[tick.symbol]
        quantity = 0.0 if tick.symbol is not quantity_dict else quantity_dict[tick.symbol]
        history = history_dict[tick.symbol]
        history += tick
        quantity_new, stoploss_new = strategy(cash.value, quantity, stoploss, history)

        if quantity_new:
            order = Order(tick.symbol, tick.price, quantity_new, tick.timestamp)
            order_queue.put(order)

        if stoploss_new:
            stoploss_dict[tick.symbol] = stoploss_new

        count += 1

    logger.info(f'Analyzed {count} ticks')

    time.sleep(0.1)
    order_queue.put(None)
