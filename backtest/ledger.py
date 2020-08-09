import json
import logging
from dataclasses import asdict
from datetime import datetime
from multiprocessing.connection import Connection
from pathlib import Path
from threading import Thread
from typing import Callable, TextIO

from .data import Msg

logger = logging.getLogger(Path(__file__).stem)


class Ledger(Thread):

    def __init__(self, dir: Path) -> None:
        super().__init__(name=self.__class__.__name__)

        self.input: Connection

        self._loop: bool = True
        self._file: TextIO = self._create_file(dir)

        self._handlers: dict[str, Callable[[Msg], None]] = {
            'FILL': self._handler_fill,
            'CASH': self._handler_cash,
            'QUIT': self._handler_quit,
        }

    def __del__(self):
        if self._file and not self._file.close():
            self._file.close()

    def run(self) -> None:
        while self._loop:
            msg = self.input.recv()
            logger.debug(f'Received: {msg}')
            self._handlers[msg.type](msg)

    def _handler_cash(self, msg: Msg) -> None:
        if msg.cash < 0:
            raise ArithmeticError('Cash should be greater than zero')

        output = json.dumps({'cash': msg.cash})
        print(output, file=self._file)

    def _handler_fill(self, msg: Msg) -> None:
        output = json.dumps(asdict(msg))
        print(output, file=self._file)

    def _handler_quit(self, _: Msg) -> None:
        self._loop = False

    @staticmethod
    def _create_file(dir: Path) -> TextIO:
        dir.mkdir(parents=True, exist_ok=True)
        filename = f'{datetime.now():%Y%m%d%H%M%S}.jsonl'
        logger.debug(f'Preparing file: {filename}')

        return dir.joinpath(filename).open('w')
