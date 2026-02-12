"""
This module contains the discord bot implementation with definitions for the bot and its commands.
The bot is implemented using the discord.py library and provides a simple command to test the bot.
"""

import discord
from discord import app_commands
from discord.ext import commands
from .configuration import Configuration
from .discord_permissions import check_permissions_historian
from .game import (
    create_game,
    keep_telling_schedule,
    setup_game,
    reset_game,
    finish_game,
    info_game,
)
from .character import select_character, show_character, show_own_character
from .file_utils import import_data
from .genre import deactivate_genre, activate_genre, update_genre_with_content


class DiscordBot:
    """
    DiscordBot class to create a discord bot with the given configuration. This is
    necessary because of a own implementation with user configuration and
    pydantic validation.
    """

    def __init__(self, config: Configuration):
        self.config = config
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        # intents.reactions = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self.config.dc_bot = self.bot

        @self.bot.event
        async def on_ready():
            await self.on_ready()

        self.register_commands()

    async def start(self):
        """
        Function to start the bot with the given token from the configuration.
        This function is called in the main function to start the bot.
        """
        await self.bot.start(self.config.env.dc.bot_token)

    async def on_ready(self):
        """
        Event function to print a message when the bot is online.
        """
        self.config.logger.info(f"{self.bot.user} ist online")
        synced = await self.bot.tree.sync()
        self.config.logger.info(f"Slash Commands synchronisiert: {len(synced)}")
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=discord.ActivityType.listening, name="storyteller"
            ),
        )

    def register_commands(self):  # pylint: disable=too-many-locals, too-many-statements
        """
        Function to register the commands for the bot. This function is called in the
        constructor to register the commands.
        """

        character_group = app_commands.Group(
            name="character", description="Character administration"
        )

        content_group = app_commands.Group(
            name="content", description="Content administration"
        )
        genre_group = app_commands.Group(
            name="genre", description="Genre administration"
        )
        game_group = app_commands.Group(name="game", description="Game administration")

        @self.bot.tree.command(
            name="keep_telling",
            description="Continue the story of a game.",
        )
        async def wrapped_keep_telling(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute command to continue telling a story."
            )
            await keep_telling_schedule(interaction, self.config)

        @content_group.command(
            name="import-data",
            description="Import game data from a YAML file.",
        )
        async def wrapped_import_data(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute command import game data."
            )
            if not await check_permissions_historian(self.config, interaction):
                return
            await import_data(interaction, self.config)

        @content_group.command(
            name="update-genre",
            description="Update events and inspirational words for genres from external source.",
        )
        async def wrapped_update_genre(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute command to update genre content."
            )
            if not await check_permissions_historian(self.config, interaction):
                return
            await update_genre_with_content(interaction, self.config)

        @game_group.command(
            name="create", description="Create a new game and set the parameters."
        )
        async def wrapped_create_game(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute command for game creation."
            )
            if not await check_permissions_historian(self.config, interaction):
                return
            await create_game(interaction, self.config)

        @game_group.command(
            name="setup",
            description="Switch game state to specific status like running, paused, etc.",
        )
        async def wrapped_setup_game(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute command for setup game."
            )
            if not await check_permissions_historian(self.config, interaction):
                return
            await setup_game(interaction, self.config)

        @game_group.command(
            name="reset", description="Restart a Tale and create new start prompt."
        )
        async def wrapped_reset_game(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute command for reset game."
            )
            if not await check_permissions_historian(self.config, interaction):
                return
            await reset_game(interaction, self.config)

        @game_group.command(
            name="finish", description="Finish a Tale and print the story as PDF."
        )
        async def wrapped_finish_game(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute command for finish game."
            )
            if not await check_permissions_historian(self.config, interaction):
                return
            await finish_game()

        @game_group.command(
            name="info",
            description="Print information about a selected game like state, players, etc.",
        )
        async def wrapped_info_game(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute command for info game."
            )
            await info_game()

        @genre_group.command(name="deactivate", description="Deactivate genre")
        async def wrapped_genre_deactivate(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute sub-command for genre deactivation."
            )
            if not await check_permissions_historian(self.config, interaction):
                return
            await deactivate_genre(interaction, self.config)

        @genre_group.command(name="activate", description="Activate genre")
        async def wrapped_genre_activate(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute sub-command for genre activation."
            )
            if not await check_permissions_historian(self.config, interaction):
                return
            await activate_genre(interaction, self.config)

        @character_group.command(
            name="select", description="Join a game by selecting a character."
        )
        async def wrapped_character_select(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute sub-command for character selection."
            )
            await select_character(interaction, self.config)

        @character_group.command(
            name="show",
            description="Show available character and select one with background and traits.",
        )
        async def wrapped_character_show(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute sub-command to show character."
            )
            await show_character(interaction, self.config)

        @character_group.command(
            name="own",
            description="Show all characters selected by the player in games",
        )
        async def wrapped_character_own(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute sub-command to show own character."
            )
            await show_own_character(interaction, self.config)

        self.bot.tree.add_command(content_group)
        self.bot.tree.add_command(game_group)
        self.bot.tree.add_command(genre_group)
        self.bot.tree.add_command(character_group)
