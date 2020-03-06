from backtester import logger


def calc_transaction_cost():
    pass


def get_unit_price(market, current_price):
    pass


def run(config, cash, holding_dict, order_queue, log_queue):
    logger.config(log_queue)

    count = 0
    while order := order_queue.get():
        logger.info(order)
        cash.value -= order.price
        count += 1

    logger.info(f'Processed {count} orders')
    logger.info(f'Remaining cash: {cash.value}')
