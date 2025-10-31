"""
This module contains the function to handle requests to the OpenAI API.
"""
from openai import OpenAI
from .configuration import Configuration


async def request_openai(config: Configuration, messages: list) -> None:
    """
    This function is the entry point to communicate with the configured
    LLM model via OpenAI API.

    Args:
        config (Configuration): App configuration
        messages (list): List of prompt messages´
    """
    client = OpenAI(
        base_url=config.env.base_url,
        api_key=config.env.api_key,
    )

    response = client.chat.completions.create(
        model=config.env.model, reasoning_effort="high", messages=messages
    )
    return response.choices[0].message.content
