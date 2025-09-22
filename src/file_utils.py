"""
This file contains all functions and definitions required for document handling.
"""

from pathlib import Path

import aiofiles
import yaml
from discord import HTTPException, Interaction

from .configuration import Configuration
from .db import (ImportResult, create_character_from_input,
                 create_genre_from_input)


async def load_yaml(config: Configuration, result: ImportResult) -> dict:
    try:
        if not Path(result.file_path).is_file():
            config.logger.debug(f"During import, file {result.file_path} don't exist")
            return
        async with aiofiles.open(result.file_path, mode="r", encoding="utf-8") as file:
            content = await file.read()
            result.data = yaml.safe_load(content)
    except PermissionError:
        config.logger.error(f"No permission to read the file {result.file_path}")
    except FileNotFoundError:
        config.logger.error(f"File disappeared before opening: {result.file_path}")
    except IsADirectoryError:
        config.logger.error(f"Expected a file but found a directory: {result.file_path}")
    except IOError as err:
        config.logger.error(f"I/O error reading file {result.file_path}: {err}")
    except UnicodeDecodeError:
        config.logger.error(f"File {result.file_path} is not valid UTF-8 encoded")
    except yaml.YAMLError as err:
        config.logger.error(f"YAML parsing error in file {result.file_path}: {err}")


async def import_data(interaction: Interaction, config: Configuration):
    try:
        result_genre = ImportResult(data=None, file_path="files/genre.yml")
        result_character = ImportResult(data=None, file_path="files/character.yml")
        await load_yaml(config, result_genre)
        if result_genre.data:
            await create_genre_from_input(config, result_genre)
        await load_yaml(config, result_character)
        if result_character.data:
            await create_character_from_input(config, result_character)
        await interaction.response.send_message(
            f"The import from genre was {'successful' if result_genre.success else 'unsuccessful'}"
            f" and {result_genre.import_number} records were imported. The import from character"
            f" was {'successful' if result_character.success else 'unsuccessful'}"
            f" and {result_character.import_number} records were imported."
        )
    except FileNotFoundError as err:
        config.logger.error(f"File not found: {err}")
        await interaction.response.send_message("A required file was not found.")
    except yaml.YAMLError as err:
        config.logger.error(f"Error parsing the YAML file: {err}")
        await interaction.response.send_message("Error parsing the YAML file")
    except PermissionError as err:
        config.logger.error(f"No access rights: {err}")
        await interaction.response.send_message("Access rights to a file are missing.")
    except HTTPException as err:
        config.logger.error(f"Error in Discord communication: {err}")
