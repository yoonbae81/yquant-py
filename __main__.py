from collections import namedtuple

import analyzer
import broker
from fetcher import Tick, fetch

import fetcher


# @todo load config

# @todo verify input dir from config
# @todo initialize asset (cash) from config


# @todo load ticks using fetcher

# @todo prepare queue between fetcher and analyzers
# @todo prepare queue between analzyers and broker

# @todo initialize analyzers and pop messages from que

# @todo analyzers calculate and send signal to broker

# @todo
