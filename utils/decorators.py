import functools
import logging
from datetime import datetime


def step(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        start = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        logger.info(f"[{start}] → {func.__name__}")

        try:
            result = func(*args, **kwargs)
            end = datetime.now().strftime("%H:%M:%S.%f")[:-3]

            logger.info(f"[{end}] ✓ {func.__name__} passed")
            return result

        except Exception as e:
            end = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            logger.info(f"[{end}] ✗ {func.__name__} failed: {e}")
            raise

    return wrapper
