import json
import logging.config
from pathlib import Path

from . import launcher

with Path(__file__).parent.joinpath('logging.json').open() as f:
    logging.config.dictConfig(json.load(f))


run = launcher.run
