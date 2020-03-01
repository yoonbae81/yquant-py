import logging

import backtester

config = {
    'cash': 10_000_000,
    'ticks': 'ticks/',
    'output': 'output.txt',
}


def strategy(tick):
    logging.debug('Calculating...')


if __name__ == '__main__':
    backtester.run(config, strategy)
