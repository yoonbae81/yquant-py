from threading import Thread
from multiprocessing import Manager, Process, Queue, Event, cpu_count
from pathlib import Path

from . import analyzer
from . import broker
from . import fetcher


def run(market, strategy, tick_dir, ledger_dir, initial_cash=1_000_000, num_workers=cpu_count()):
    if not Path(tick_dir).exists():
        raise FileNotFoundError(tick_dir)

    manager = Manager()
    quantity_dict = manager.dict()

    tick_queues = [Queue() for _ in range(num_workers - 1)]
    signal_queue = Queue()
    done = Event()

    threads = [
        Thread(target=fetcher.run,
               name='Fetcher',
               args=(tick_dir,
                     tick_queues,
                     done)),

        Thread(target=broker.run,
               name='Broker',
               args=(market['rules'],
                     strategy,
                     initial_cash,
                     quantity_dict,
                     signal_queue,
                     ledger_dir,
                     done)),
    ]

    processes = []
    for i, tick_queue in enumerate(tick_queues, 1):
        p = Process(target=analyzer.run,
                    name=f'Analyzer{i}',
                    args=(market['symbols'],
                          strategy,
                          quantity_dict,
                          tick_queue,
                          signal_queue,
                          done))
        processes.append(p)

    [t.start() for t in threads]
    [p.start() for p in processes]
    [p.join() for p in processes]
    [t.join() for t in threads]

