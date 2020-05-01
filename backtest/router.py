import logging
from collections import defaultdict
from multiprocessing.connection import Connection, Pipe, wait
from pathlib import Path
from threading import Thread
from time import time
from typing import List, Dict, DefaultDict, TypeVar, Callable, Any

from .analyzer import Analyzer
from .broker import Broker
from .data import Msg
from .fetcher import Fetcher
from .ledger import Ledger

Node = TypeVar('Node', Fetcher, Analyzer, Broker)

logger = logging.getLogger(Path(__file__).stem)


class Router(Thread):
    def __init__(self) -> None:
        super().__init__(name=self.__class__.__name__)

        self._loop = True

        # Fetcher
        self._from_fetcher: Connection

        # Analyzer
        self._from_analyzers: List[Connection] = []
        self._to_analyzers: List[Connection] = []
        self._analyzer_counter: Dict[Connection, int] = {}
        self._analyzer_assigned: Dict[str, Connection] = {}

        # Broker
        self._from_broker: Connection
        self._to_broker: Connection

        # Ledger
        self._to_ledger: Connection

        # Timer
        self._start_time: float = 0

        self._handlers: Dict[str, Callable[[Msg], None]] = {
            'TICK': self._handler_tick,
            'SIGNAL': self._handler_signal,
            'CASH': self._handler_cash,
            'ORDER': self._handler_order,
            'QUANTITY': self._handler_quantity,
            'EOF': self._handler_eof,
            'EOD': self._handler_eod,
        }

        self._msg_counter: DefaultDict[str, int] = defaultdict(int)

        logger.debug('Initialized')

    def run(self):
        logger.debug('Started')

        self._start_time = time()
        while self._loop:
            for conn in wait([*self._from_analyzers,
                              self._from_broker,
                              self._from_fetcher],
                             timeout=1):

                msg = conn.recv()
                self._msg_counter[msg.type] += 1

                try:
                    self._handlers[msg.type](msg)
                except KeyError:
                    logger.warning('Unknown message ', msg)

    def connect(self, nodes: List[Any]) -> None:
        [self._connect(node) for node in nodes]

    def _connect(self, node: Node) -> bool:
        if isinstance(node, Analyzer):
            from_analyzer, node.output = Pipe(duplex=False)
            self._from_analyzers.append(from_analyzer)

            node.input, to_analyzer = Pipe(duplex=False)
            self._to_analyzers.append(to_analyzer)
            self._analyzer_counter[to_analyzer] = 0

        elif isinstance(node, Fetcher):
            # Fetcher does not need to listen from Router
            self._from_fetcher, node.output = Pipe(duplex=False)

        elif isinstance(node, Broker):
            self._from_broker, node.output = Pipe(duplex=False)
            node.input, self._to_broker = Pipe(duplex=False)

        elif isinstance(node, Ledger):
            node.input, self._to_ledger = Pipe(duplex=False)

        elif isinstance(node, Router):
            pass

        else:
            raise TypeError(type(node))

        logger.debug(f'Connected to {node.name}')

        return True

    def _handler_tick(self, msg: Msg) -> None:
        to_analyzer = self._get_analyzer(msg.symbol)
        to_analyzer.send(msg)

    def _get_analyzer(self, symbol: str) -> Connection:
        try:
            to_analyzer = self._analyzer_assigned[symbol]

        except KeyError:
            to_analyzer = min(self._analyzer_counter,
                              key=self._analyzer_counter.get)
            self._analyzer_assigned[symbol] = to_analyzer
            self._analyzer_counter[to_analyzer] += 1

        return to_analyzer

    def _handler_signal(self, msg: Msg) -> None:
        self._to_broker.send(msg)

    def _handler_cash(self, msg: Msg) -> None:
        self._to_ledger.send(msg)

    def _handler_order(self, msg: Msg) -> None:
        self._to_ledger.send(msg)

    def _handler_quantity(self, msg: Msg) -> None:
        to_analyzer = self._get_analyzer(msg.symbol)
        to_analyzer.send(msg)

    def _handler_eof(self, _: Msg) -> None:
        for to_analyzer in self._to_analyzers:
            to_analyzer.send(Msg('RESET'))

    def _handler_eod(self, _: Msg) -> None:
        self._loop = False
        for node in [*self._to_analyzers, self._to_broker, self._to_ledger]:
            node.send(Msg('QUIT'))

    def __del__(self) -> None:

        tick_cnt = self._msg_counter.get('TICK', 0)
        delay_sec = self._msg_counter.get('EOD', 0) * 1
        elapsed_time = time() - self._start_time

        logger.info(f'Handled: {dict(self._msg_counter)}')
        logger.info(f'Elapsed: {elapsed_time:.2f} sec '
                    f'({(elapsed_time - delay_sec) / tick_cnt * 1000:.2f} ms/msg)')

        assert self._msg_counter['TICK'] \
               == self._msg_counter['SIGNAL'] \
               == self._msg_counter['ORDER']
