import logging
import os


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def setup_logging():
    root_logger = logging.getLogger()

    if not root_logger.handlers:
        logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
    else:
        root_logger.setLevel(LOG_LEVEL)


def get_logger(name: str):
    setup_logging()
    return logging.getLogger(name)
