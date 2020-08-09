import argparse
import json
import logging
import sys
from importlib import import_module
from multiprocessing import cpu_count
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
    'ticks_dir': 'ticks',
    'ledger_dir': 'ledger',
    'symbols_json': 'symbols.json',
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


def run(config: dict, strategy: ModuleType):
    logger.info('Started')

    fetcher = Fetcher(Path(config['ticks_dir']))

    analyzers = [Analyzer(strategy.calc_strength,
                          strategy.calc_stoploss)
                 for _ in range((cpu_count() or 2) - 1)]

    logger.debug('Loading exchange module...')
    exchange: Exchange = load_exchange(config['exchange'], config['symbols_json'])

    broker = Broker(config['cash'],
                    exchange,
                    strategy.calc_quantity)

    ledger = Ledger(Path(config['ledger_dir']))

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

    return exchange_module.KoreaExchange(symbols)


def main(argv: list[str]):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='config.json')
    args = parser.parse_args(argv)

    with Path(args.config).open('rt', encoding='utf8') as f:
        config: dict = json.load(f)

    config = DEFAULTS | config

    sys.path.insert(0, '.')
    logger.debug('Loading strategy module...')
    strategy = import_module(config['strategy'])

    # if validate(**config):
    run(config, strategy)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
