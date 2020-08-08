"""
Evaluates trading results
"""
import logging
from pathlib import Path

logger = logging.getLogger(Path(__file__).stem)


def evaluate(tick_files, ledger_file, benchmark_symbol, factors=[]):
    return {
        'profit': 99,
        'utils': {
            'A': 79,
            'B': 19
        },
        'sonos': 0 - 1,
        'sharp_ratio': -1.4
    }
