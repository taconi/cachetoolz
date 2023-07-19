"""Logging implemetation."""

import logging


def get_logger(name='cachetoolz') -> logging.Logger:
    """Get a logger.

    Parameters
    ----------
    name
        logger name

    """
    logger = logging.getLogger(name)

    log_level = logger.level
    if log_level == logging.NOTSET:
        log_level = logging.WARN
        logger.setLevel(log_level)

    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | '
        '%(pathname)s:%(funcName)s:%(lineno)d - %(message)s'
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)

    return logger
