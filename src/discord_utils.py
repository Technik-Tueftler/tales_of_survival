"""
This module contains utility functions for interacting with Discord.
"""
import discord
from .configuration import Configuration

async def send_channel_message(config: Configuration, channel_id: int, message: str):
    """
    This function send a message to a specific Discord channel.

    Args:
        config (Configuration): App configuration
        channel_id (int): Channel ID to send the message to
        message (str): Message to send
    """
    try:
        channel = config.dc_bot.get_channel(channel_id)
        if channel is not None:
            await channel.send(message)
        else:
            channel = await config.dc_bot.fetch_channel(channel_id)
            await channel.send(message)
    except discord.errors.NotFound:
        config.logger.error(f"Channel ID {channel_id} not found.")
    except discord.errors.Forbidden:
        config.logger.error(f"No permission to write to channel {channel_id}.")
    except discord.errors.HTTPException as e:
        config.logger.error(f"HTTP-Error during send: {e}")
