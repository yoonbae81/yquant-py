import logging
from multiprocessing.connection import Connection
from pathlib import Path
from threading import Thread
from time import sleep
from typing import List

from .data import Msg

logger = logging.getLogger(Path(__file__).stem)


class Fetcher(Thread):

    def __init__(self, ticks: Path) -> None:
        super().__init__(name=self.__class__.__name__)

        self._ticks: Path = ticks
        self.output: Connection

        logger.debug('Initialized')

    def run(self) -> None:
        logger.debug('Started')

        for file in self._get_files():
            logger.info(f'Loading {file.name}')

            for i, line in enumerate(file.open('rt').readlines(), 1):
                try:
                    msg = self._parse(line)

                except ValueError:
                    logger.warning(f'{file.name} line {i} [{line.strip()}]')

                self.output.send(msg)

            sleep(1)
            self.output.send(Msg('EOF'))  # End of file

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
