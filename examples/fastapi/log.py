import logging

LOG_LEVEL = logging.DEBUG
formatter = logging.Formatter(
    '%(asctime)s | %(name)s | %(levelname)s | '
    '%(pathname)s:%(funcName)s:%(lineno)d - %(message)s'
)

cache_logger = logging.getLogger('cachetoolz')
cache_logger.setLevel(LOG_LEVEL)

logger = logging.getLogger('examples.fastapi')
logger.setLevel(LOG_LEVEL)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(LOG_LEVEL)
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
