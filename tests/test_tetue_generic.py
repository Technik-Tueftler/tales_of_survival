"""
This file contains unit tests for verifying the functionality of
generic utilities and functions within package tetue_generic.
"""
import io
import pytest
import requests
from loguru import logger
import src

@pytest.mark.asyncio
async def test_generic_http_request_success(monkeypatch):
    """
    Tests the successful execution of the `generic_http_request` function.

    This test ensures that when a HTTP GET request executes successfully,
    the function returns a valid response object with the expected status code.

    The `requests.get` method is monkeypatched to return a dummy response
    with a status code of 200, simulating a successful request.

    Args:
        monkeypatch: Pytest fixture used to temporarily replace methods.

    Asserts:
        - The response is not None.
        - The response has a status code of 200.
    """
    class DummyResponse:
        """
        Response class to simulate a successful HTTP response.
        """
        status_code = 200

    def mock_get(url, headers, timeout): # pylint: disable=unused-argument
        return DummyResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    response = await src.generic_http_request("http://test.com", {"User-Agent": "pytest"}, 5)
    assert response is not None
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_generic_http_request_http_error(monkeypatch):
    """
    Tests the behavior of `generic_http_request` when an HTTP error occurs.

    This test ensures that when `requests.get` raises an HTTPError,
    the function logs the error correctly and returns None.

    The `requests.get` method is monkeypatched to raise an HTTPError
    to simulate a failed HTTP request.

    Args:
        monkeypatch: Pytest fixture used to temporarily replace methods.

    Asserts:
        - The function returns None.
        - The error message is logged by Loguru.
    """
    log_stream = io.StringIO()
    handler_id = logger.add(log_stream, format="{message}")

    def mock_get(url, headers, timeout): # pylint: disable=unused-argument
        raise requests.exceptions.HTTPError("Bad response")

    monkeypatch.setattr("requests.get", mock_get)

    response = await src.generic_http_request("http://test.com", {}, 5)
    assert response is None

    logger.remove(handler_id)
    log_contents = log_stream.getvalue()
    assert "HTTP error occurred" in log_contents


@pytest.mark.asyncio
async def test_generic_http_request_timeout(monkeypatch):
    """
    Tests the behavior of `generic_http_request` when an connection timeout error.

    This test ensures that when `requests.get` raises an ConnectTimeout,
    the function logs the error correctly and returns None.

    The `requests.get` method is monkeypatched to raise an ConnectTimeout
    to simulate a failed connection timeout error.

    Args:
        monkeypatch: Pytest fixture used to temporarily replace methods.

    Asserts:
        - The function returns None.
        - The error message is logged by Loguru.
    """
    log_stream = io.StringIO()
    handler_id = logger.add(log_stream, format="{message}")

    def mock_get(url, headers, timeout): # pylint: disable=unused-argument
        raise requests.exceptions.ConnectTimeout("Timeout!")

    monkeypatch.setattr("requests.get", mock_get)

    response = await src.generic_http_request("http://test.com", {}, 5)
    assert response is None

    logger.remove(handler_id)
    log_contents = log_stream.getvalue()
    assert "Connection timeout error occurred" in log_contents


@pytest.mark.asyncio
async def test_generic_http_request_connection_error(monkeypatch):
    """
    Tests the behavior of `generic_http_request` when an network issue.

    This test ensures that when `requests.get` raises an ConnectionError,
    the function logs the error correctly and returns None.

    The `requests.get` method is monkeypatched to raise an ConnectionError
    to simulate a failed connection network issue.

    Args:
        monkeypatch: Pytest fixture used to temporarily replace methods.

    Asserts:
        - The function returns None.
        - The error message is logged by Loguru.
    """
    log_stream = io.StringIO()
    handler_id = logger.add(log_stream, format="{message}")

    def mock_get(url, headers, timeout):
        raise requests.exceptions.ConnectionError("Network issue")

    monkeypatch.setattr("requests.get", mock_get)

    response = await src.generic_http_request("http://test.com", {}, 5)
    assert response is None

    logger.remove(handler_id)
    log_contents = log_stream.getvalue()
    assert "Connection error occurred" in log_contents
