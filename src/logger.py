import sys
from typing import Type
from loguru import logger
from config import settings

Logger = Type[logger.__class__]

def setup_logger() -> Logger:
    logger_format = "[{time:YYYY-MM-DD HH:mm:ss}][{level}]: {message}"

    if 0 in logger._core.handlers:
        logger.remove(0)

    logger.add(
        sink=sys.stderr,
        level=settings.LOGGING_LEVEL,
        format=logger_format
    )

    logger.add(
        sink=settings.LOGGING_FILE,
        level=settings.LOGGING_LEVEL,
        format=logger_format
    )
    return logger
