"""
This module contains the function to handle requests to the OpenAI API.
"""

import traceback
from openai import (
    OpenAI,
    OpenAIError,
    APIConnectionError,
    RateLimitError,
    AuthenticationError,
    InternalServerError,
)
from .configuration import Configuration


async def request_openai(config: Configuration, messages: list) -> None:
    """
    This function is the entry point to communicate with the configured
    LLM model via OpenAI API.

    Args:
        config (Configuration): App configuration
        messages (list): List of prompt messages
    """
    try:
        client = OpenAI(
            base_url=config.env.base_url,
            api_key=config.env.api_key,
        )

        response = client.chat.completions.create(
            model=config.env.model, reasoning_effort="high", messages=messages
        )
        return response.choices[0].message.content
    except AuthenticationError:
        config.logger.error("API key invalid or expired")
    except RateLimitError:
        config.logger.error("Rate limit reached, retry later")
    except APIConnectionError:
        config.logger.error("Failed to connect to API")
    except InternalServerError as err:
        config.logger.error(f"OpenAI server error: {traceback.print_exception(err)}")
    except OpenAIError as err:
        config.logger.error(f"OpenAI error: {traceback.print_exception(err)}")
