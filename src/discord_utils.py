"""
This module contains utility functions for interacting with Discord.
"""

import sys
from urllib.parse import urljoin
import asyncio
import discord
from discord import TextChannel, Embed, Interaction
from .configuration import Configuration, ProcessInput
from .constants import (
    DC_MAX_CHAR_MESSAGE,
    DC_EMBED_DESCRIPTION,
    DEFAULT_CHARACTER_THUMBNAIL,
    DEFAULT_THUMBNAIL_URL,
    DEFAULT_TALE_THUMBNAIL,
)
from .db import get_active_user_from_game, get_object_by_id
from .db_classes import GAME, USER, CHARACTER, GENRE
from .game_views import GameSelectView


async def split_text(text: str, max_len: int = DC_MAX_CHAR_MESSAGE) -> list[str]:
    """
    Function split a long text into smaller parts based on a maximum length.

    Args:
        text (str): Text to split
        max_len (int, optional): Character threshold . Defaults to DC_MAX_CHAR_MESSAGE.

    Returns:
        list[str]: Plitted text parts
    """
    text_parts = []
    while len(text) > max_len:
        split_at = text.rfind(" ", 0, max_len)
        if split_at == -1:
            split_at = max_len
        text_parts.append(text[:split_at])
        text = text[split_at:].lstrip()
    if text:
        text_parts.append(text)
    return text_parts


async def send_channel_message(
    config: Configuration, channel_id: int, message: str
) -> list[int]:
    """
    This function send a message to a specific Discord channel.

    Args:
        config (Configuration): App configuration
        channel_id (int): Channel ID to send the message to
        message (str): Message to send
    """
    try:
        channel = config.dc_bot.get_channel(channel_id)
        if channel is None:
            channel = await config.dc_bot.fetch_channel(channel_id)

        msg_ids = []
        for text_part in message.splitlines():
            if text_part.strip() == "":
                continue
            msg_parts = await split_text(text_part, DC_MAX_CHAR_MESSAGE)
            for msg_part in msg_parts:
                msg = await channel.send(msg_part)
                msg_ids.append(msg.id)
        config.logger.debug(f"Sended messages: {msg_ids}")
        return msg_ids

    except discord.errors.NotFound:
        config.logger.error(f"Channel ID {channel_id} not found.")
        return []
    except discord.errors.Forbidden:
        config.logger.error(f"No permission to write to channel {channel_id}.")
        return []
    except discord.errors.HTTPException:
        config.logger.opt(exception=sys.exc_info()).error(
            "HTTP-Error during send message"
        )
        return []
    except KeyError:
        config.logger.error("The message is missing the content key.")
        return []


async def delete_channel_messages(
    config: Configuration, game: GAME, dc_message_ids: list[int]
) -> None:
    """
    Function to delete messages in a Discord channel based on message IDs.

    Args:
        config (Configuration): App configuration
        game (GAME): Game object with all required information
        dc_message_ids (list[int]): List of Discord message IDs to delete
    """
    try:
        channel: TextChannel = config.dc_bot.get_channel(game.channel_id)
        if channel is None:
            channel = await config.dc_bot.fetch_channel(game.channel_id)
        delete_messages = []
        for dc_msg in dc_message_ids:
            msg = await channel.fetch_message(dc_msg)
            delete_messages.append(msg)
        await channel.delete_messages(delete_messages)
        config.logger.debug(f"Deleted DC message ID: {len(delete_messages)}")
    except discord.errors.NotFound:
        config.logger.error(f"Channel ID {game.channel_id} not found.")
    except discord.errors.Forbidden:
        config.logger.error(f"No permission to write to channel {game.channel_id}.")
    except discord.errors.HTTPException:
        config.logger.opt(exception=sys.exc_info()).error(
            "HTTP-Error during delete messages"
        )
    except KeyError:
        config.logger.error("The message is missing the content key.")
    except TypeError:
        config.logger.opt(exception=sys.exc_info()).error(
            "Type-Error during delete messages"
        )


async def create_dc_message_link(
    config: Configuration, message: discord.Message, interaction: Interaction
) -> str:
    """
    Function to create a link to a specific Discord message.

    Args:
        config (Configuration): App configuration
        message (discord.Message): General message object to collect ids
        interaction (Interaction): Last interaction to collect guild id

    Returns:
        str: Message link in the format
    """
    message_link = (
        f"https://discord.com/channels/{interaction.guild.id}"
        f"/{message.channel.id}/{message.id}"
    )
    config.logger.debug(f"Create message link: {message_link}")
    return message_link


async def update_embed_message_color(
    config: Configuration, game: GAME, discord_color: discord.colour.Colour
) -> None:
    """
    This function updates the color of a game embed message.

    Args:
        config (Configuration): App configuration
        game (GAME): Game object to udpate the embed message
        discord_color (discord.colour.Colour): New color for the embed message
    """
    try:
        users: list[USER] = await get_active_user_from_game(config, game.id)
        config.logger.debug(
            f"All active user in game <id>: {game.id}. <user>: {[user.name for user in users]}"
        )
        channel: TextChannel = config.dc_bot.get_channel(game.channel_id)
        if channel is None:
            channel = await config.dc_bot.fetch_channel(game.channel_id)
        embed_message = await channel.fetch_message(game.message_id)
        embed: Embed = embed_message.embeds[0]
        embed.color = discord_color
        await embed_message.edit(embed=embed)

    except discord.errors.NotFound:
        config.logger.error(f"Channel ID {game.channel_id} not found.")
    except discord.errors.Forbidden:
        config.logger.error(f"No permission to write to channel {game.channel_id}.")
    except discord.errors.HTTPException:
        config.logger.opt(exception=sys.exc_info()).error(
            "HTTP-Error during update embed message"
        )
    except KeyError:
        config.logger.error("The message is missing the content key.")
    except TypeError:
        config.logger.opt(exception=sys.exc_info()).error(
            "Type-Error during update embed message"
        )


async def update_embed_message(config: Configuration, game: GAME) -> None:
    """
    This function updates a game embed with the start information and current players.

    Args:
        config (Configuration): App configuration
        game (GAME): Game object to udpate the embed message
    """
    config.logger.trace("Start with update game embed.")
    try:
        users: list[USER] = await get_active_user_from_game(config, game.id)
        config.logger.debug(
            f"All active user in game <id>: {game.id}. <user>: {[user.name for user in users]}"
        )
        channel: TextChannel = config.dc_bot.get_channel(game.channel_id)
        if channel is None:
            channel = await config.dc_bot.fetch_channel(game.channel_id)
        embed_message = await channel.fetch_message(game.message_id)
        embed: Embed = embed_message.embeds[0]
        fields = list(embed.fields)
        config.logger.trace("DC channel and embed loaded.")
        embed.title = game.name
        embed.description = (
            game.description if game.description else DC_EMBED_DESCRIPTION
        )
        embed.color = discord.Color.green()
        config.logger.trace("General Embed fields updated.")
        for i, field in enumerate(fields):
            if field.name in ("The Players:", "The Player:"):
                field_name = "The Players:" if len(users) > 1 else "The Player:"
                player = ", ".join([f"<@{user.dc_id}>" for user in users])
                embed.set_field_at(
                    i, name=field_name, value=player, inline=field.inline
                )
                config.logger.trace("Embed field <Player> upddated.")
                break
        await embed_message.edit(embed=embed)

    except discord.errors.NotFound:
        config.logger.error(f"Channel ID {game.channel_id} not found.")
    except discord.errors.Forbidden:
        config.logger.error(f"No permission to write to channel {game.channel_id}.")
    except discord.errors.HTTPException:
        config.logger.opt(exception=sys.exc_info()).error(
            "HTTP-Error during update embed message"
        )
    except KeyError:
        config.logger.error("The message is missing the content key.")
    except TypeError:
        config.logger.opt(exception=sys.exc_info()).error(
            "Type-Error during update embed message"
        )


async def interface_select_game(
    interaction: Interaction, config: Configuration, process_data: ProcessInput
) -> bool:
    """
    This function is a general interface to select a game for the player.
    The required input is a list of games which is saved in process data.

    Args:
        interaction (Interaction): Discord interaction
        config (Configuration): App configuration
        process_data (ProcessInput): Process data with required list of games

    Returns:
        bool: Selection was successful and a game was selected and saved in the process data.
    """
    try:
        if not await process_data.game_context.input_valid_game():
            await interaction.response.send_message(
                "No game is available for this command, please contact a Mod.",
                ephemeral=True,
            )
            return False

        select_view = GameSelectView(config, process_data)
        await interaction.response.send_message(
            "Which game would you like to select?",
            view=select_view,
            ephemeral=True,
        )
        await select_view.wait()
        process_data.game_context.selected_game = await get_object_by_id(
            config, GAME, process_data.game_context.selected_game_id
        )
        return True
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


async def send_character_embed(
    interaction: Interaction,
    config: Configuration,
    character: CHARACTER,
) -> None:
    """
    Function to send an embed message with character information.

    Args:
        interaction (Interaction): Discord interaction object
        config (Configuration): App configuration
        character (CHARACTER): Character object with all information
    """
    try:
        config.logger.trace(
            f"Thumbnail URL: {urljoin(DEFAULT_THUMBNAIL_URL, DEFAULT_CHARACTER_THUMBNAIL)}"
        )
        embed = discord.Embed(
            title=character.name,
            description=character.background,
            color=discord.Color.dark_blue(),
        )
        embed.add_field(name="Description", value=character.description, inline=False)
        embed.add_field(name="Pos-Trait", value=character.pos_trait, inline=True)
        embed.add_field(name="Neg-Trait", value=character.neg_trait, inline=True)
        embed.set_thumbnail(
            url=urljoin(DEFAULT_THUMBNAIL_URL, DEFAULT_CHARACTER_THUMBNAIL)
        )

        message = await interaction.followup.send(embed=embed, ephemeral=True)
        return message
    except discord.Forbidden:
        config.logger.error("Cannot send message, permission denied.")
    except discord.HTTPException:
        config.logger.opt(exception=sys.exc_info()).error("Failed to send message.")
    except (TypeError, ValueError):
        config.logger.opt(exception=sys.exc_info()).error("General error occurred.")


async def send_game_embed(
    interaction: Interaction,
    config: Configuration,
    game: GAME,
    genre: GENRE,
    users: list[USER],
) -> discord.Message:
    """
    Functions create and send a Discord message with game information to a channel.

    Args:
        interaction (Interaction): Interaction object from Discord
        config (Configuration): App configuration
        game (GAME): Game object
        genre (GENRE): Genre object from game
        users (list[USER]): All player of the game

    Returns:
        discord.Message: Discord message object
    """
    try:
        game_description = (
            game.description if game.description else DC_EMBED_DESCRIPTION
        )
        embed = discord.Embed(
            title=game.name,
            description=game_description,
            color=discord.Color.yellow(),
        )
        embed.add_field(name="Genre", value=genre.name, inline=False)
        embed.add_field(name="Language", value=genre.language, inline=True)
        embed.add_field(name="Style", value=genre.storytelling_style, inline=True)
        embed.add_field(name="Atmosphere", value=genre.atmosphere, inline=True)
        embed.add_field(
            name="The Players:",
            value=", ".join([f"<@{user.dc_id}>" for user in users]),
            inline=False,
        )

        embed.set_thumbnail(url=urljoin(DEFAULT_THUMBNAIL_URL, DEFAULT_TALE_THUMBNAIL))
        embed.set_footer(text=f"Game-ID: {game.id}, Genre-ID: {genre.id}")

        message = await interaction.followup.send(embed=embed)
        return message
    except discord.Forbidden:
        config.logger.error("Cannot send message, permission denied.")
    except discord.HTTPException:
        config.logger.opt(exception=sys.exc_info()).error("Failed to send message.")
    except (TypeError, ValueError):
        config.logger.opt(exception=sys.exc_info()).error("General error occurred.")


async def send_public_event_ephemeral(
    config: Configuration, interaction: Interaction, process_data: ProcessInput
):
    event_message = (
        "An event has been triggered:\nEvent: "
        + f"{process_data.story_context.event.text}"
    )
    await interaction.followup.send(event_message, ephemeral=True)


async def send_public_event_embed(
    config: Configuration, interaction: Interaction, process_data: ProcessInput, message_id: int
):
    try:
        if config.env.dc.public_event_channel_id == 0:
            await send_public_event_ephemeral(config, interaction, process_data)
            config.logger.debug(
                "Public event channel does not configured. Event message "
                + "is send ephemeral in tale channel."
            )
            return

        channel = config.dc_bot.get_channel(config.env.dc.public_event_channel_id)
        if channel is None:
            channel = await config.dc_bot.fetch_channel(
                config.env.dc.public_event_channel_id
            )
        if channel is None:
            await send_public_event_ephemeral(config, interaction, process_data)
            config.logger.warning(
                "Public event channel does not exist. Event message "
                + "is send ephemeral in tale channel."
            )
            return

        message_link = (
            f"https://discord.com/channels/{interaction.guild.id}"
            f"/{process_data.game_context.selected_game.channel_id}/{message_id}"
        )
        config.logger.debug(f"Create message link: {message_link}")
        embed = discord.Embed(
            title="Public Event",
            description=process_data.story_context.event.text,
            color=discord.Color.purple(),
        )
        embed.add_field(name="Game", value=message_link, inline=False)
        embed.add_field(
            name="Chance", value=process_data.story_context.event.chance, inline=True
        )
        # TODO: Neues Thumbnail dafür erstellen
        embed.set_thumbnail(url=urljoin(DEFAULT_THUMBNAIL_URL, DEFAULT_TALE_THUMBNAIL))

        await channel.send(embed=embed)

    except discord.Forbidden:
        config.logger.error("Cannot send message, permission denied.")
    except discord.HTTPException:
        config.logger.opt(exception=sys.exc_info()).error("Failed to send message.")
    except (TypeError, ValueError):
        config.logger.opt(exception=sys.exc_info()).error("General error occurred.")
    except Exception:
        config.logger.opt(exception=sys.exc_info()).error("Unknown error occurred.")
