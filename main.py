"""
Main function for starting application
"""

import src


def main() -> None:
    """
    Scheduling function for regular call.
    """
    config = src.environ.to_config(src.Configuration)
    src.init_logging(config.watcher)
    src.logger.info(f"Start application in version: {src.__version__}")


if __name__ == "__main__":
    main()
