from multiprocessing import Process, Queue, cpu_count

import backtester.fetcher
import backtester.analyzer
import backtester.broker
import backtester.logger


def run(config, strategy):
    num_analyzer = max(1, cpu_count() - 1)

    tick_queues = [Queue() for _ in range(num_analyzer)]
    order_queue = Queue()
    log_queue = Queue()

    processes = [Process(target=fetcher.run, name='Fetcher',
                         args=(config, tick_queues, log_queue)),
                 Process(target=broker.run, name='Broker',
                         args=(config, order_queue, log_queue)),
                 Process(target=logger.run, args=(config, log_queue))]

    for i, tick_queue in enumerate(tick_queues):
        p = Process(target=analyzer.run, name=f'Analyzer{i}',
                    args=(config, strategy, tick_queue, order_queue, log_queue))
        processes.append(p)

    [p.start() for p in processes]
    [p.join() for p in processes]

