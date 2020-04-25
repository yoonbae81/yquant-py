import logging
from collections import defaultdict
from multiprocessing.connection import Connection, Pipe, wait
from threading import Thread
from typing import List, Dict, DefaultDict, TypeVar, Callable

from .analyzer import Analyzer
from .broker import Broker
from .data import Msg
from .fetcher import Fetcher

Node = TypeVar('Node', Fetcher, Analyzer, Broker)

logger = logging.getLogger('router')


class Router(Thread):
    def __init__(self) -> None:
        self._name = self.__class__.__name__

        super().__init__(name=self._name)

        self._loop = True

        # Fetcher
        self._from_fetcher: Connection

        # Broker
        self._from_broker: Connection
        self._to_broker: Connection

        # Analyzer
        self._from_analyzers: List[Connection] = []
        self._to_analyzers: List[Connection] = []
        self._analyzer_counter: Dict[Connection, int] = {}
        self._analyzer_assigned: Dict[str, Connection] = {}

        self._handlers: Dict[str, Callable[[Msg], None]] = {
            'TICK': self._handler_tick,
            'SIGNAL': self._handler_signal,
            'QUANTITY': self._handler_quantity,
            'EOF': self._handler_eof,
            'EOD': self._handler_eod,
        }

        self._msg_counter: DefaultDict[str, int] = defaultdict(int)

        logger.debug(self._name + ' initialized')

    def connect(self, node: Node) -> bool:
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

        else:
            raise TypeError(node)

        logger.debug(f'{node.name} connected')

        return True

    def run(self):
        while self._loop:
            for conn in wait([*self._from_analyzers,
                              self._from_broker,
                              self._from_fetcher],
                             timeout=1):

                msg = conn.recv()
                self._msg_counter[msg.type] += 1
                # print(f'{self.name} received: {msg}')

                try:
                    self._handlers[msg.type](msg)
                except KeyError:
                    logger.warn('Unknown message ', msg)

        logger.info(self._msg_counter)

    def _get_analyzer(self, symbol: str) -> Connection:
        try:
            to_analyzer = self._analyzer_assigned[symbol]

        except KeyError:
            to_analyzer = min(self._analyzer_counter,
                              key=self._analyzer_counter.get)
            self._analyzer_assigned[symbol] = to_analyzer
            self._analyzer_counter[to_analyzer] += 1

        return to_analyzer

    def _handler_tick(self, msg: Msg) -> None:
        to_analyzer = self._get_analyzer(msg.symbol)
        to_analyzer.send(msg)

    def _handler_signal(self, msg: Msg) -> None:
        self._to_broker.send(msg)

    def _handler_quantity(self, msg: Msg) -> None:
        to_analyzer = self._get_analyzer(msg.symbol)
        to_analyzer.send(msg)

    def _handler_eof(self, msg: Msg) -> None:
        for to_analyzer in self._to_analyzers:
            to_analyzer.send(Msg('RESET'))

    def _handler_eod(self, msg: Msg) -> None:
        for node in [*self._to_analyzers, self._to_broker]:
            node.send(Msg('QUIT'))

        self._loop = False
