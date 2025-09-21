"""
This file contains all functions and definitions required for document handling.
"""

import aiofiles
import yaml
from discord import Interaction

from .configuration import Configuration
from .db import create_genre_from_input, create_character_from_input


async def load_yaml(filename):
    async with aiofiles.open(filename, mode="r", encoding="utf-8") as file:
        content = await file.read()
        data = yaml.safe_load(content)
        return data


async def import_data(interaction: Interaction, config: Configuration):
    try:
        data = await load_yaml("files/genre.yml")
        await create_genre_from_input(config, data)
        data = await load_yaml("files/character.yml")
        await create_character_from_input(config, data)
    except Exception as err:
        print(err, type(err))
