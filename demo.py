import logging

import backtester

config = {
    'cash': 100_000,
    'ticks': 'ticks/',
    'output': 'output.txt',
    'threshold': 5,
}


def strategy(ticks):
    logging.debug('Calculating...')
    return config['threshold']


if __name__ == '__main__':
    backtester.run(config, strategy)
