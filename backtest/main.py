import argparse
import json
import logging
import sys
from importlib import import_module
from multiprocessing import cpu_count, Value
from pathlib import Path
from types import ModuleType

from .analyzer import Analyzer
from .broker import Broker
from .fetcher import Fetcher
from .ledger import Ledger
from .router import Router
from .exchanges import Exchange

logger = logging.getLogger(Path(__file__).stem)

DEFAULTS = {
    'cash': 1_000_000,
    'ticks': './ticks',
    'ledger': './ledger',
    'symbolsn': './symbols.json',
    'strategy': 'strategy',
    'exchange': 'backtest.exchanges.korea_exchange'
}


def validate(**config):
    required = {'exchanges', 'strategy', 'ticks_dir', 'ledger_dir', 'cash', 'rates'}

    if missing := required - set(config):
        print('Missing key(s) in configuration: ' + ', '.join(missing))
        return False

    dirs = {key: config[key] for key in config if key.endswith('_dir')}
    for k, v in dirs.items():
        if not Path(v).exists():
            print(f'Not found dir: {v}')
            return False

    return True


def run(config: dict):
    config = DEFAULTS | config
    logger.info('Starting')
    logger.debug(f'config: {config}')

    sys.path.insert(0, '.')
    logger.debug('Loading strategy module...')
    strategy = import_module(config['strategy'])

    logger.debug('Loading exchange module...')
    exchange: Exchange = load_exchange(config['exchange'], config['symbolsn'])

    cash = Value('d', config['cash'])

    fetcher = Fetcher(Path(config['ticks']))

    analyzers = [Analyzer(cash,
                          strategy.calc_strength,
                          strategy.calc_stoploss,
                          strategy.calc_quantity)
                 for _ in range((cpu_count() or 2) - 1)]

    broker = Broker(cash,
                    exchange)

    ledger = Ledger(Path(config['ledger']))

    nodes: list = [ledger, broker, *analyzers, fetcher]

    router = Router()
    [router.connect(node) for node in nodes]

    nodes.insert(0, router)
    [node.start() for node in nodes]
    [node.join() for node in reversed(nodes)]


def load_exchange(exchange_path: str, symbols_path: str) -> Exchange:
    with Path(symbols_path).open('rt', encoding='utf-8') as f:
        symbols = json.load(f)

    exchange_module = import_module(exchange_path)

    # TODO Generalize ctor's name
    return exchange_module.KoreaExchange(symbols)


def main(argv: list[str]):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='config.json')
    args = parser.parse_args(argv)

    with Path(args.config).open('rt', encoding='utf8') as f:
        config: dict = json.load(f)

    # if validate(**config):
    run(config)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
