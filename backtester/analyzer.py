import time
from collections import defaultdict

from . import logger
from .data import Dataset, Order


def run(config, strategy, cash, quantity_dict, tick_queue, order_queue, log_queue):
    logger.config(log_queue)
    dataset_dict = defaultdict(Dataset)
    stoploss_dict = defaultdict(float)

    count = 0
    while t := tick_queue.get():
        holding = quantity_dict.get(t.symbol, 0)
        stoploss = stoploss_dict[t.symbol]
        dataset = dataset_dict[t.symbol]
        dataset += t

        if holding > 0 and t.price < stoploss:
            quantity = strategy.calc_quantity_to_sell(holding, dataset)
        else:
            quantity = strategy.calc_quantity_to_buy(config['initial_cash'], cash.value, holding, dataset)

        if abs(quantity) > 0:
            order = Order(t.symbol, t.price, quantity, t.timestamp)
            order_queue.put(order)

        if quantity > 0 or holding > 0:
            stoploss_dict[t.symbol] = strategy.calc_stoploss(stoploss, dataset)

        count += 1

    logger.info(f'Analyzed {count} ticks')

    time.sleep(0.1)
    order_queue.put(None)
