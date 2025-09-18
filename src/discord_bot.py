"""
This module contains the discord bot implementation with definitions for the bot and its commands.
The bot is implemented using the discord.py library and provides a simple command to test the bot.
"""

import discord
from discord.ext import commands
from .configuration import Configuration
from .game import create_game, keep_telling


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
        intents.reactions = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)

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
        try:
            self.config.logger.info(f"{self.bot.user} ist online")
            synced = await self.bot.tree.sync()
            self.config.logger.info(f"Slash Commands synchronisiert: {len(synced)}")
            await self.bot.change_presence(
                status=discord.Status.online,
                activity=discord.Activity(
                    type=discord.ActivityType.listening, name="storyteller"
                ),
            )
        except Exception as err:
            print(err)

    def register_commands(self):
        """
        Function to register the commands for the bot. This function is called in the
        constructor to register the commands.
        """

        async def wrapped_create_game(interaction: discord.Interaction):
            await create_game(interaction, self.config)

        async def wrapped_keep_telling(interaction: discord.Interaction):
            await keep_telling(interaction, self.config)

        self.bot.tree.command(
            name="create_game",
            description=("Create a new game and set the parameters."),
        )(wrapped_create_game)

        self.bot.tree.command(
            name="keep_telling",
            description=("Continue the story of a game."),
        )(wrapped_keep_telling)
