import argparse
import json
import logging
from importlib import import_module
from multiprocessing import cpu_count
from pathlib import Path

from .analyzer import Analyzer
from .broker import Broker
from .fetcher import Fetcher
from .ledger import Ledger
from .router import Router

logger = logging.getLogger(Path(__file__).stem)


def validate(**config):
    required = {'exchanges', 'strategy', 'ticks_dir', 'ledger_dir', 'cash'}

    if missing := required - set(config):
        print('Missing key(s) in configuration: ' + ', '.join(missing))
        return False

    dirs = {key: config[key] for key in config if key.endswith('_dir')}
    for k, v in dirs.items():
        if not Path(v).exists():
            print(f'Not found dir: {v}')
            return False

    return True


def run(cash: float,
        ticks_dir: str,
        ledger_dir: str,
        symbols_file: str,
        strategy: str,
        exchanges: list,
        ):
    logger.info('Started')

    fetcher = Fetcher(Path(ticks_dir))

    logger.debug('Loading strategy module...')
    strategy_module = import_module(strategy)

    analyzers = [Analyzer(strategy_module.calc_strength,
                          strategy_module.calc_stoploss)
                 for _ in range((cpu_count() or 2) - 1)]

    logger.debug('Loading symbols file...')
    with Path(symbols_file).open('rt', encoding='utf-8') as f:
        symbols = json.load(f)

    broker = Broker(cash,
                    symbols,
                    exchanges,
                    strategy_module.calc_quantity)

    ledger = Ledger(Path(ledger_dir))

    nodes: list = [ledger, broker, *analyzers, fetcher]

    router = Router()
    router.connect(nodes)

    nodes.insert(0, router)
    [node.start() for node in nodes]
    [node.join() for node in reversed(nodes)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='config.json')
    args = parser.parse_args()

    with Path(args.config).open('rt', encoding='utf8') as f:
        config = json.load(f)

    if validate(**config):
        run(**config)
