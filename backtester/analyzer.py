import time
from collections import namedtuple

from backtester import logger

Order = namedtuple('Order', 'symbol price strength timestamp')


def _calc_strength():
    pass


def _calc_quantity():
    pass


def _calc_stoploss():
    pass


def run(config, strategy, tick_queue, order_queue, log_queue):
    logger.config(log_queue)
    count = 0

    while tick := tick_queue.get():
        order = Order(tick.symbol,
                      tick.price,
                      strategy(tick),
                      tick.timestamp)

        order_queue.put(order)
        count += 1

    # logger.info(f'Analyzed {count} ticks')

    time.sleep(0.1)
    order_queue.put(None)
