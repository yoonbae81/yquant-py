import logging
import logging.handlers

FORMAT = '%(asctime)s %(processName)-9s %(levelname)-8s %(message)s'

# Aliases
critical = logging.getLogger().critical
error = logging.getLogger().error
warning = logging.getLogger().warning
info = logging.getLogger().info
debug = logging.getLogger().debug


def config(queue):
    handler = logging.handlers.QueueHandler(queue)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)


def run(config, queue):
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    formatter = logging.Formatter(FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    # file_handler = logging.handlers.RotatingFileHandler('Backtester.log', 'a', 1000, 5)
    # file_handler.setFormatter(formatter)
    # root.addHandler(file_handler)

    while record := queue.get():
        logging.getLogger().handle(record)
