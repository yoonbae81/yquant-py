import logging

import backtester
from backtester.analyzer import Ticks

config = {
    'cash': 10_000_000,
    'ticks': 'ticks/',
    'output': 'output.txt',
}


def strategy(ticks: Ticks):
    logging.debug('Calculating...')
    return True

if __name__ == '__main__':
    backtester.run(config, strategy)
