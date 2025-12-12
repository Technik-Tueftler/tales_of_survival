"""
This module contains the function to handle requests to the OpenAI API.
"""

import sys
from openai import (
    OpenAI,
    OpenAIError,
    APIConnectionError,
    RateLimitError,
    AuthenticationError,
    InternalServerError,
)
from .configuration import Configuration


class OpenAiContext:
    """
    This class represents the return context for OpenAI API requests.
    """
    def __init__(self, response: str, error: str = ""):
        self.response = response
        self.error = error
    async def error_free(self) -> bool:
        """
        This function checks if there was no error in the OpenAI response.
        """
        return self.error == ""


async def request_openai(config: Configuration, messages: list) -> OpenAiContext:
    """
    This function handles the request to the OpenAI API.

    Args:
        config (Configuration): App configuration
        messages (list): List of messages for the OpenAI API

    Returns:
        OpenAiContext: The OpenAI response context
    """
    try:
        client = OpenAI(
            base_url=config.env.base_url,
            api_key=config.env.api_key,
        )

        response = client.chat.completions.create(
            model=config.env.model, reasoning_effort="high", messages=messages
        )
        return OpenAiContext(response=response.choices[0].message.content)
    except AuthenticationError:
        config.logger.error("API key invalid or expired")
        return OpenAiContext(response="", error="API key invalid or expired")
    except RateLimitError:
        config.logger.error("Rate limit reached, retry later")
        return OpenAiContext(response="", error="Rate limit reached, retry later")
    except APIConnectionError:
        config.logger.error("Failed to connect to API")
        return OpenAiContext(response="", error="Failed to connect to API")
    except InternalServerError:
        config.logger.opt(exception=sys.exc_info()).error("OpenAI server error.")
        return OpenAiContext(response="", error="OpenAI server error")
    except OpenAIError:
        config.logger.opt(exception=sys.exc_info()).error("OpenAI error.")
        return OpenAiContext(response="", error="OpenAI error")
