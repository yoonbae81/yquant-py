import json
import logging.config
from pathlib import Path

with Path(__file__).parent.joinpath('logging.json').open() as f:
    logging.config.dictConfig(json.load(f))
