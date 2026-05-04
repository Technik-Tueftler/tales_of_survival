"""
This module contains all functions to validate the environment variables and login information
"""
from pathlib import Path

from .configuration import Configuration


def check_all_directories(config: Configuration) -> bool:
    path = Path("files")
    if not path.exists():
        config.logger.error(f"Directory {path} does not exist.")
        return False
    return True


def scheduler_general_checks(config: Configuration) -> bool:
    valid = [
        check_all_directories(config),
    ]
    return all(valid)
