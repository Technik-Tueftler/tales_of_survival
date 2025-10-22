from openai import OpenAI
from .configuration import Configuration


async def request_openai(config: Configuration, messages: list):
    client = OpenAI(
        base_url=config.env.base_url,
        api_key=config.env.api_key,
    )

    response = client.chat.completions.create(
        model=config.env.model, reasoning_effort="high", messages=messages
    )
    return response.choices[0].message.content
