from collections import defaultdict
from multiprocessing import Value

from backtester import logger

from backtester.data import Order
from backtester.market import kosdaq, kospi


def buy(order: Order, cash: Value, quantity_dict: dict):
    tax = kosdaq.calc_tax(order)
    commission = kosdaq.calc_commission(order)

    if order.symbol not in quantity_dict:
        quantity_dict[order.symbol] = 0

    quantity_dict[order.symbol] += order.quantity
    cash.value -= order.price * order.quantity + tax + commission
    assert cash.value >= 0


def sell(order: Order, cash: Value, quantity_dict: dict):
    pass


def run(config, cash, quantity_dict, order_queue, log_queue):
    logger.config(log_queue)

    count = 0
    while order := order_queue.get():
        logger.info(order)

        fn = buy if order.quantity >= 0 else sell
        fn(order, cash, quantity_dict)

        count += 1

    logger.info(f'Processed {count} orders')
    logger.info(f'Remaining cash: {cash.value}')
    logger.info(quantity_dict)
