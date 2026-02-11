"""Module for character selection and display in Discord bot."""
import sys
from datetime import datetime, timezone
import asyncio
import discord
from discord import Interaction
from .db import (
    get_all_open_user_games,
    get_available_characters,
    get_all_owned_characters,
    get_user_from_dc_id,
    get_mapped_ugc_association,
    get_object_by_id,
    update_db_objs,
    get_game_id_from_character_id,
)
from .db_classes import CHARACTER
from .discord_utils import interface_select_game, send_character_embed
from .configuration import Configuration, ProcessInput


class CharacterSelectView(discord.ui.View):
    """
    View class to select a character for a game.
    """

    def __init__(self, config, process_data: ProcessInput):
        super().__init__()
        self.add_item(CharacterSelect(config, process_data))


class CharacterSelect(discord.ui.Select):
    """
    Select class to select a character for a game.
    """

    def __init__(self, config, process_data: ProcessInput):
        self.config = config
        self.process_data = process_data
        options = [
            discord.SelectOption(
                label=f"{char.id}: {char.name}",
                value=f"{char.id}",
                description=(
                    f"{char.background[:97]}..."
                    if len(char.background) > 100
                    else char.background
                ),
            )
            for char in process_data.user_context.available_chars
        ]

        super().__init__(
            placeholder="Select a character...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        selected_option = [
            option for option in self.options if option.value == self.values[0]
        ]
        self.config.logger.debug(f"Selected character id: {self.values[0]}")
        self.process_data.user_context.selected_char = int(self.values[0])
        label = selected_option[0].label
        self.disabled = True
        await interaction.response.edit_message(
            content=f"You have chosen the character {label}",
            view=self.view,
        )
        self.view.stop()


async def select_character(interaction: Interaction, config: Configuration) -> None:
    """
    This function allows the user to select a character for a specific game.

    Args:
        interaction (Interaction): Interaction object
        config (Configuration): App configuration
    """
    try:
        process_data = ProcessInput()
        process_data.user_context.user_dc_id = str(interaction.user.id)
        await get_all_open_user_games(config, process_data)
        if not await process_data.game_context.input_valid_game():
            await interaction.response.send_message(
                "An error occurred while retrieving your games. Your not registered "
                "for any game. Please contact the admin.",
                ephemeral=True,
            )
            config.logger.debug(
                f"User: {interaction.user.id} wants to select a character, "
                + "but has not been asked to do so in any game."
            )
            return
        select_success = await interface_select_game(interaction, config, process_data)
        if not select_success:
            return
        process_data.user_context.available_chars = await get_available_characters(
            config
        )
        if not await process_data.user_context.input_valid_char():
            await interaction.followup.send(
                "An error occurred while retrieving character. There are no selectable characters. "
                "Please contact the admin.",
                ephemeral=True,
            )
            return
        character_view = CharacterSelectView(config, process_data)
        await interaction.followup.send(
            "Please select now the character for the game.",
            view=character_view,
            ephemeral=True,
        )
        await character_view.wait()
        user = await get_user_from_dc_id(config, process_data.user_context.user_dc_id)
        association = await get_mapped_ugc_association(
            config, process_data.game_context.selected_game_id, user.id
        )
        selected_character = await get_object_by_id(
            config, CHARACTER, process_data.user_context.selected_char
        )
        selected_character.user_id = association.user_id
        selected_character.start_date = datetime.now(timezone.utc)
        association.character_id = process_data.user_context.selected_char
        await update_db_objs(config, [association, selected_character])

    except discord.Forbidden:
        config.logger.opt(exception=sys.exc_info()).error(
            "Cannot send message, permission denied."
        )
    except discord.HTTPException:
        config.logger.opt(exception=sys.exc_info()).error("Failed to send message.")
    except (TypeError, ValueError):
        config.logger.opt(exception=sys.exc_info()).error("General error occurred.")
    except asyncio.TimeoutError:
        config.logger.opt(exception=sys.exc_info()).error("Timeout error occurred.")
    except KeyError:
        config.logger.opt(exception=sys.exc_info()).error(
            "Missing key in game data or for DB object."
        )


async def show_character(interaction: Interaction, config: Configuration) -> None:
    """
    This function allows the user to show a character's details.

    Args:
        interaction (Interaction): Discord interaction object
        config (Configuration): App configuration
    """
    try:
        char_context = ProcessInput()
        char_context.user_context.available_chars = await get_available_characters(
            config
        )
        if not await char_context.user_context.input_valid_char():
            await interaction.response.send_message(
                "An error occurred while retrieving character. There are no selectable characters. "
                "Please contact a admin or mod and follow the creation guideline in "
                "the documentation.",
                ephemeral=True,
            )
            return
        character_view = CharacterSelectView(config, char_context)
        await interaction.response.send_message(
            "Please select now the character to inspect.",
            view=character_view,
            ephemeral=True,
        )
        await character_view.wait()
        selected_character = await get_object_by_id(
            config, CHARACTER, char_context.user_context.selected_char
        )
        await send_character_embed(interaction, config, selected_character)
    except Exception as err:
        print(err)


async def show_own_character(interaction: Interaction, config: Configuration) -> None:
    """
    This function allows the user to show a character's details.

    Args:
        interaction (Interaction): Discord interaction object
        config (Configuration): App configuration
    """
    char_context = ProcessInput()
    user = await get_user_from_dc_id(config, str(interaction.user.id))
    char_context.user_context.available_chars = await get_all_owned_characters(
        config, user
    )
    if not await char_context.user_context.input_valid_char():
        await interaction.response.send_message(
            "An error occurred while retrieving character. There are no selectable characters. "
            "Please contact the admin.",
            ephemeral=True,
        )
        return
    character_view = CharacterSelectView(config, char_context)
    await interaction.response.send_message(
        "Please select now the character to inspect.",
        view=character_view,
        ephemeral=True,
    )
    await character_view.wait()
    selected_character = await get_object_by_id(
        config, CHARACTER, char_context.user_context.selected_char
    )
    game_id = await get_game_id_from_character_id(config, selected_character.id)
    await send_character_embed(interaction, config, selected_character, True, game_id)
