from multiprocessing import Manager, Process, Queue
from threading import Thread

import backtester.analyzer
import backtester.broker
import backtester.fetcher
import backtester.logger


def run(config, strategy):
    manager = Manager()
    cash = manager.Value(float, config['initial_cash'])
    quantity_dict = manager.dict()

    tick_queues = [Queue() for _ in range(config['num_analyzer'])]
    order_queue = Queue()
    log_queue = Queue()

    processes = [
        Process(target=fetcher.run, name='Fetcher',
                args=(config, tick_queues, log_queue)),
        Process(target=broker.run, name='Broker',
                args=(config, cash, quantity_dict, order_queue, log_queue)),
    ]

    threads = [
        Thread(target=logger.run, args=(config, log_queue)),
    ]

    for i, tick_queue in enumerate(tick_queues, 1):
        p = Process(target=analyzer.run, name=f'Analyzer{i}',
                    args=(config, strategy, cash, quantity_dict,
                          tick_queue, order_queue, log_queue))
        processes.append(p)

    [t.start() for t in threads]
    [p.start() for p in processes]
    [p.join() for p in processes]
    [t.join() for t in threads]
