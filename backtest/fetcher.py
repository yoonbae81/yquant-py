import logging
from time import sleep
from multiprocessing.connection import Connection
from os import listdir
from os.path import exists, isfile, isdir, join, basename
from threading import Thread
from pathlib import Path
from typing import List, Dict

from .data import Tick, RESET, Msg

logger = logging.getLogger('fetcher')


class Fetcher(Thread):
    def __init__(self, ticks: Path) -> None:
        super().__init__(name=self.__class__.__name__)

        self._ticks: Path = ticks
        self.output: Connection

        logger.debug(self._name + ' initialized')

    def run(self) -> None:
        sleep(0.2)

        for file in self._get_files():
            logger.info(f'Loading {file.name}')

            for i, line in enumerate(file.open('rt').readlines(), 1):
                try:
                    msg = self._parse(line)

                except ValueError:
                    logger.warning(f'{file.name} line {i} [{line.strip()}]')
                    continue

                self.output.send(msg)

            self.output.send(Msg('EOF'))  # End of file

        sleep(0.2)
        self.output.send(Msg('EOD'))  # End of data

    def _get_files(self) -> List[Path]:
        if self._ticks.is_file():
            return [self._ticks]

        if self._ticks.is_dir():
            result = [p for p in self._ticks.iterdir()
                      if p.is_file()
                      and p.name.endswith('.txt')]
            return sorted(result)

        logger.error(f'Not found: {self._ticks.name}')
        return []

    @staticmethod
    def _parse(line: str) -> Msg:
        symbol, price, quantity, timestamp = line.split()

        return Msg('TICK',
                   symbol=symbol,
                   price=float(price),
                   quantity=float(quantity),
                   timestamp=int(timestamp))
