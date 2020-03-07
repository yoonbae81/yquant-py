from collections import defaultdict
from multiprocessing import cpu_count, Manager, Process, Queue, Value
from threading import Thread

import backtester.fetcher
import backtester.analyzer
import backtester.broker
import backtester.logger

NUM_ANALYZER = max(1, cpu_count() - 1)


def run(config, strategy):
    manager = Manager()
    cash = manager.Value(float, config['cash'])
    holding_dict = manager.dict()

    tick_queues = [Queue() for _ in range(NUM_ANALYZER)]
    order_queue = Queue()
    log_queue = Queue()

    processes = [
        Process(target=fetcher.run, name='Fetcher',
                args=(config, tick_queues, log_queue)),
        Process(target=broker.run, name='Broker',
                args=(config, cash, holding_dict, order_queue, log_queue)),
    ]

    threads = [
        Thread(target=logger.run, args=(config, log_queue)),
    ]

    for i, tick_queue in enumerate(tick_queues, 1):
        p = Process(target=analyzer.run, name=f'Analyzer{i}',
                    args=(config, strategy, cash, holding_dict,
                          tick_queue, order_queue, log_queue))
        processes.append(p)

    [t.start() for t in threads]
    [p.start() for p in processes]
    [p.join() for p in processes]
    [t.join() for t in threads]
