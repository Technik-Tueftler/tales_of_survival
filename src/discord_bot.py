"""
This module contains the discord bot implementation with definitions for the bot and its commands.
The bot is implemented using the discord.py library and provides a simple command to test the bot.
"""

import discord
from discord.ext import commands
from .configuration import Configuration
from .game import (
    create_game,
    keep_telling_schedule,
    select_character,
    setup_game,
    reset_game,
)
from .file_utils import import_data


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

    def register_commands(self):
        """
        Function to register the commands for the bot. This function is called in the
        constructor to register the commands.
        """

        async def wrapped_create_game(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute command for game creation."
            )
            await create_game(interaction, self.config)

        async def wrapped_keep_telling(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute command to continue telling a story."
            )
            await keep_telling_schedule(interaction, self.config)

        async def wrapped_import_data(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute command import game data."
            )
            await import_data(interaction, self.config)

        async def wrapped_select_char(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute command for character selection."
            )
            await select_character(interaction, self.config)

        async def wrapped_setup_game(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute command for setup game."
            )
            await setup_game(interaction, self.config)

        async def wrapped_reset_game(interaction: discord.Interaction):
            self.config.logger.trace(
                f"User: {interaction.user.id} execute command for reset game."
            )
            await reset_game(interaction, self.config)

        self.bot.tree.command(
            name="create_game", description="Create a new game and set the parameters."
        )(wrapped_create_game)

        self.bot.tree.command(
            name="keep_telling",
            description="Continue the story of a game.",
        )(wrapped_keep_telling)

        self.bot.tree.command(
            name="import_data",
            description="Import game data from a YAML file.",
        )(wrapped_import_data)

        self.bot.tree.command(
            name="select_character",
            description="Select a character for a game.",
        )(wrapped_select_char)

        self.bot.tree.command(
            name="setup_game",
            description="Switch game state to specific status like running, paused, finished, etc.",
        )(wrapped_setup_game)

        self.bot.tree.command(
            name="reset_game",
            description="Restart a Tale and create new start prompt.",
        )(wrapped_reset_game)
