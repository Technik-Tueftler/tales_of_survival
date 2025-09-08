"""All functions and features for logging the app"""

import sys
import environ
from loguru import logger


@environ.config(prefix="WATCHER")
class WatcherConfiguration:
    """
    Configuration model for the watcher component.
    """

    log_file_path: str = environ.var("files/app.log")
    log_level: str = environ.var(logger.level("INFO").name)


def init_logging(config) -> None:
    """
    Initializes logging configuration for the application..

    Args:
        conf_watcher (watcher.WatcherConfiguration): A configuration object containing logging
            settings.

    Returns:
        None

    Note:
        - This function modifies the global `logger` object from Loguru.
        - Log files are rotated when they reach 100 MB in size.
        - Console output is colorized for better readability.

    """
    logger.remove()
    logger.add(
        config.env.watcher.log_file_path, rotation="100 MB", level=config.env.watcher.log_level
    )
    logger.add(sys.stdout, colorize=True, level=config.env.watcher.log_level)
    config.logger = logger
