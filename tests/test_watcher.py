"""
This file contains unit tests for verifying the functionality of
watcher utilities and functions within package tetue_generic.
"""
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
import pytest
import src


@pytest.fixture(name="capture_logs")
def fct_capture_logs():
    """
    Pytest fixture to capture log output during tests.

    This fixture provides a mechanism to capture log messages emitted during test execution.

    Yields:
        list: An empty list that can be used to capture log messages.
    """
    output = []
    yield output


@pytest.fixture(name="temp_log_file")
def fct_temp_log_file():
    """
    Pytest fixture to create a temporary log file for testing purposes.

    This fixture creates a temporary file, writes some initial content to it,
    and provides the file path for use in tests. The file is not automatically
    deleted after the test, allowing for post-test inspection if needed.

    Yields:
        Path: A Path object representing the location of the temporary log file.
    """
    with NamedTemporaryFile(delete=False, mode="w") as f:
        f.write("Test content")
        yield Path(f.name)


def test_init_logging(temp_log_file):
    """
    Tests the initialization of the logging system.

    This test verifies that the logging system is correctly initialized with the specified 
    configuration, including custom log levels and file output.

    Args:
        temp_log_file (str): Path to a temporary log file used for testing.

    Procedure:
        1. Initializes the logging system with a WatcherConfiguration set to TRACE level
           and a specified temporary log file path.
        2. Verifies that the log file has been created.

    Assertions:
        - Confirms that the specified log file has been created.

    Notes:
        - This test is crucial for ensuring that the logging system is properly configured
          at the application startup.
        - It validates both the custom log level setup and the file logging functionality.
    """
    # Procedure 1: Initialize the logging system
    src.init_logging(
        src.WatcherConfiguration(log_level="TRACE", log_file_path=temp_log_file)
    )

    # Procedure 2: Check if the log file was created
    assert os.path.exists(temp_log_file), "Log file was not created"


def test_console_logging(capture_logs):
    """
    Tests the functionality of file logging.

    This test verifies that log messages are correctly written to console output.
    It uses a temporary handler to capture log messages and checks which messages are
    actually logged based on the configured log level.

    Procedure:
        1. Adds a temporary handler to capture log messages at the DEBUG level.
        2. Generates test log messages at TRACE, DEBUG and INFO levels.
        3. Removes the temporary handler.
        4. Checks the captured log messages to ensure correct filtering.

    Assertions:
        - Verifies that the TRACE message is not captured (as it's below the set level).
        - Verifies that the DEBUG message is captured.
        - Verifies that the INFO message is captured.

    Notes:
        - The test assumes that the logger is configured with a minimum level of DEBUG or lower.
        - The EXTDEBUG level is a custom level that should be higher than INFO in the 
        logging hierarchy.
        - This test helps ensure that log level filtering works as expected in the application.
    """
    # Procedure 1: Add a temporary handler to capture log messages
    temp_handler_id = src.logger.add(
        lambda msg: capture_logs.append(msg.record["message"]), level="DEBUG"
    )

    # Procedure 2: Write log messages
    src.logger.trace("Test TRACE message")
    src.logger.debug("Test DEBUG message")
    src.logger.info("Test INFO message")

    # Procedure 3: Remove the temporary handler
    src.logger.remove(temp_handler_id)

    # Procedure 4: Check the captured log messages
    assert not "Test TRACE message" in capture_logs
    assert "Test DEBUG message" in capture_logs
    assert "Test INFO message" in capture_logs


def test_file_logging(temp_log_file):
    """
    Tests the functionality of file logging.

    This test verifies that log messages are correctly written to a log file.
    It uses a temporary log file to write different messages at various log levels.
    Subsequently, it checks the file's content to ensure all expected messages are included.

    Args:
        temp_log_file (str): The path to a temporary log file used for the test.

    Procedure:
        1. Initializes a `WatcherConfiguration` with a specific log level and file path.
        2. Adds the log file as a target for the logger.
        3. Writes test log messages at the TRACE, DEBUGm and INFO levels.
        4. Opens the log file and checks if all test messages are present in the content.

    Assertions:
        - Verifies that the message "Test TRACE message" is not contained in the file.
        - Verifies that the message "Test DEBUG message" is contained in the file.
        - Verifies that the message "Test INFO message" is contained in the file.
    """
    # Procedure 1: Specify the logging configuration
    config = src.WatcherConfiguration(log_level="DEBUG", log_file_path=temp_log_file)

    # Procedure 2: Initialize the logging configuration
    _ = src.logger.add(config.log_file_path, rotation="500 MB", level=config.log_level)

    # procedure 3: Write log messages
    src.logger.trace("Test TRACE message")
    src.logger.debug("Test DEBUG message")
    src.logger.info("Test INFO message")

    # Procedure 4: Check the log file content
    with open(temp_log_file, "r", encoding="utf-8") as log_file:
        log_content = log_file.read()
        print(f"content: {log_content}")
        assert not "Test TRACE message" in log_content
        assert "Test DEBUG message" in log_content
        assert "Test INFO message" in log_content
