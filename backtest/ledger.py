import json
import logging
from dataclasses import asdict
from datetime import datetime
from multiprocessing.connection import Connection
from pathlib import Path
from threading import Thread
from typing import Dict, Callable, TextIO

from .data import Msg

logger = logging.getLogger(Path(__file__).stem)


class Ledger(Thread):

    def __init__(self, dir: Path) -> None:
        super().__init__(name=self.__class__.__name__)

        self.input: Connection

        self._loop: bool = True
        self._file: TextIO = self._open_file(dir)

        self._handlers: Dict[str, Callable[[Msg], None]] = {
            'CASH': self._handler_cash,
            'ORDER': self._handler_order,
            'QUIT': self._handler_quit,
        }

        logger.debug('Initialized')

    @staticmethod
    def _open_file(dir: Path) -> TextIO:
        dir.mkdir(parents=True, exist_ok=True)
        filename = f'{datetime.now():%Y%m%d%H%M%S}.jsonl'

        return dir.joinpath(filename).open('wt')

    def run(self) -> None:
        logger.debug('Started')

        while self._loop:
            msg = self.input.recv()
            logger.debug(f'Received: {msg}')
            self._handlers[msg.type](msg)

    def _handler_cash(self, msg: Msg) -> None:
        json.dump({'cash': msg.cash}, self._file)
        self._file.write('\n')

    def _handler_order(self, msg: Msg) -> None:
        json.dump(asdict(msg), self._file)
        self._file.write('\n')

    def _handler_quit(self, _: Msg) -> None:
        self._loop = False

    def __del__(self) -> None:
        self._file.close()
        logger.info(f'Result saved in {self._file.name}')
