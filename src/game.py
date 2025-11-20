"""
Module to handle game creation and management
"""

import sys
from datetime import datetime, timezone
import asyncio
import discord
from discord import Interaction
from .discord_utils import send_channel_message, update_embed_message
from .configuration import Configuration, ProcessInput
from .llm_handler import request_openai
from .db_classes import StoryType, GameStatus
from .db_classes import (
    GAME,
    GENRE,
    TALE,
    USER,
    UserGameCharacterAssociation,
    CHARACTER,
    STORY,
)
from .db import (
    get_all_active_genre,
    get_genre_double_cond,
    process_player,
    update_db_objs,
    get_available_characters,
    get_object_by_id,
    get_all_running_games,
    get_all_user_games,
    get_tale_from_game_id,
    get_games_w_status,
    get_user_from_dc_id,
    get_mapped_ugc_association,
    count_regist_char_from_game,
    get_character_from_game_id,
    get_stories_messages_for_ai,
    channel_id_exist,
)
from .game_views import (
    CharacterSelectView,
    GameSelectView,
    GenreSelectView,
    UserSelectView,
    KeepTellingButtonView,
    NewGameStatusSelectView,
)
from .game_start import (
    collect_start_input,
    get_first_phase_prompt,
    get_second_phase_prompt,
)
from .game_telling import telling_event, telling_fiction
from .constants import DC_EMBED_DESCRIPTION


async def collect_all_game_contexts(
    interaction: Interaction, config: Configuration, process_data: ProcessInput
):
    """
    Function to collect all necessary game contexts from user interactions.

    Args:
        interaction (Interaction): Interaction object from Discord
        config (Configuration): App configuration
        process_data (ProcessInput): Input collection object
    """
    try:
        user_view = UserSelectView(config, process_data)
        await interaction.response.send_message(
            "Please select all players for the new story.",
            view=user_view,
            ephemeral=True,
        )
        await user_view.wait()
        config.logger.trace("Player selected.")
        genres = await get_all_active_genre(config)
        if not genres:
            await interaction.followup.send(
                "No genres are available. No game can be created. Please contact a mod or admin.",
                ephemeral=True,
            )
            return
        config.logger.debug(f"All active genre: {[genre.id for genre in genres]}")
        genre_view = GenreSelectView(config, process_data, genres)
        await interaction.followup.send(
            "Please select the genre for the new story.",
            view=genre_view,
            ephemeral=True,
        )
        await genre_view.wait()

    except discord.Forbidden:
        config.logger.error("Cannot send message, permission denied.")
    except discord.HTTPException:
        config.logger.opt(exception=sys.exc_info()).error("Failed to send message.")
    except (TypeError, ValueError):
        config.logger.opt(exception=sys.exc_info()).error("General error occurred.")
    except asyncio.TimeoutError:
        config.logger.opt(exception=sys.exc_info()).error("Timeout error occurred.")


async def send_game_information(
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
        embed.set_footer(text=f"Game-ID: {game.id}")

        message = await interaction.followup.send(embed=embed)
        return message
    except discord.Forbidden:
        config.logger.error("Cannot send message, permission denied.")
    except discord.HTTPException:
        config.logger.opt(exception=sys.exc_info()).error("Failed to send message.")
    except (TypeError, ValueError):
        config.logger.opt(exception=sys.exc_info()).error("General error occurred.")


async def inform_players(
    config: Configuration, users: list[discord.member.Member], message_link: str
):
    """
    Send a DM to each player to inform them about the new game.

    Args:
        config (Configuration): App configuration
        users (list[discord.member.Member]): All player of the game
        message_link (str): Link to the game information message
    """
    try:
        message = (
            "Hello #USERNAME, you have been invited to participate in "
            f"**Tales of Survival**. Check: {message_link}"
        )
        for user in users:
            temp_message = message.replace("#USERNAME", user.name)
            await user.send(temp_message)
    except discord.Forbidden:
        config.logger.error(f"Cannot send message to {user.name}, permission denied.")
    except discord.HTTPException:
        config.logger.opt(exception=sys.exc_info()).error(
            f"Failed to send message to {user.name}."
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


async def create_game(interaction: Interaction, config: Configuration):
    """
    Create a new game based on user inputs from Discord interactions.

    Args:
        interaction (Interaction): Intgeraction object from Discord
        config (Configuration): App configuration
    """
    try:
        if await channel_id_exist(config, interaction.channel_id):
            await interaction.response.send_message(
                (
                    "In this channel is a Tale ongoing and no new Tale can created. "
                    "Please select another channel."
                ),
                ephemeral=True,
            )
            return
        process_data = ProcessInput()
        await collect_all_game_contexts(interaction, config, process_data)
        if process_data.game_context.start.selected_genre == 0:
            config.logger.trace(
                "No genre can been selected. Game creation will be canceled."
            )
            return
        genre = await get_genre_double_cond(
            config, process_data.game_context.start.selected_genre
        )
        processed_user_list = await process_player(
            config, process_data.game_context.start.selected_user
        )
        tale = TALE(genre=genre)
        game = GAME(
            name=process_data.game_context.start.game_name,
            description=process_data.game_context.start.game_description,
            start_date=datetime.now(timezone.utc),
            tale=tale,
        )
        await update_db_objs(config, [game])
        associations = [
            UserGameCharacterAssociation(game_id=game.id, user_id=user.id)
            for user in processed_user_list
        ]
        await update_db_objs(config, associations)
        message = await send_game_information(
            interaction, config, game, genre, processed_user_list
        )
        game.message_id = message.id
        game.channel_id = message.channel.id
        config.logger.debug(
            f"Update game informations: message id {game.message_id}, channel id {game.channel_id}"
        )
        await update_db_objs(config, [game])
        message_link = await create_dc_message_link(config, message, interaction)
        await inform_players(
            config, process_data.game_context.start.selected_user, message_link
        )

    except discord.Forbidden:
        config.logger.error("Cannot send message, permission denied.")
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


async def keep_telling_schedule(interaction: Interaction, config: Configuration):
    """
    This function is the schedule to keep telling a story. It collects all necessary
    inputs from the user and write the next part of the story.

    Args:
        interaction (Interaction): Interaction object
        config (Configuration): App configuration
    """
    try:
        process_data = ProcessInput()
        await get_all_running_games(config, process_data)
        if not await process_data.game_context.input_valid_game():
            return
        game_view = GameSelectView(config, process_data)
        await interaction.response.send_message(
            "Please select the game for keep telling",
            view=game_view,
            ephemeral=True,
        )
        await game_view.wait()

        process_data.story_context.tale = await get_tale_from_game_id(
            config, process_data.game_context.selected_game_id
        )
        process_data.game_context.selected_game = await get_object_by_id(
            config, GAME, process_data.game_context.selected_game_id
        )
        telling_view = KeepTellingButtonView(config, process_data)

        await interaction.followup.send(view=telling_view, ephemeral=True)
        await telling_view.wait()
        config.logger.debug("Finish keep telling input interaction.")
        if (
            process_data.story_context.story_type is StoryType.EVENT
            and process_data.story_context.events_available()
        ):
            await process_data.story_context.get_random_event_weighted()
            await telling_event(config, process_data, interaction)

        elif process_data.story_context.story_type is StoryType.FICTION:
            await telling_fiction(config, process_data)
        else:
            config.logger.error(
                f"Story type: {process_data.story_context.story_type} is not defined."
            )
            return

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
        await get_all_user_games(config, process_data)
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
        game_view = GameSelectView(config, process_data)
        await interaction.response.send_message(
            "Please select the game for set character",
            view=game_view,
            ephemeral=True,
        )
        await game_view.wait()
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
    except Exception as err:
        print(err)


async def start_game_schedule(
    interaction: Interaction, config: Configuration, game_data: ProcessInput
):
    """
    This function the schedule to start a new game. It collects all necessary
    inputs from the user, gets the tale and character data from the database,
    creates the prompts for the LLM model, sends the requests and stores
    the responses in the database.

    Args:
        interaction (Interaction): Interaction object
        config (Configuration): App configuration
        game_data (ProcessInput): Game data object
    """
    await collect_start_input(interaction, config, game_data)

    tale = await get_tale_from_game_id(config, game_data.game_context.selected_game.id)
    game_character = await get_character_from_game_id(
        config, game_data.game_context.selected_game.id
    )
    game_data.story_context.tale = tale
    game_data.story_context.character = game_character

    messages = await get_first_phase_prompt(config, game_data)

    response_world = await request_openai(config, messages)
    await send_channel_message(
        config, game_data.game_context.selected_game.channel_id, response_world
    )
    stories = [
        STORY(request=story["content"], story_type=StoryType.INIT, tale_id=tale.id)
        for story in messages
    ]
    stories.append(
        STORY(response=response_world, story_type=StoryType.INIT, tale_id=tale.id)
    )
    await update_db_objs(config=config, objs=stories)

    messages = await get_stories_messages_for_ai(config, tale.id)
    stories = []

    messages_second_phase = await get_second_phase_prompt(config, game_data)

    for msg in messages_second_phase:
        stories.append(
            STORY(request=msg["content"], story_type=StoryType.INIT, tale_id=tale.id)
        )

    messages.extend(messages_second_phase)
    response_start = await request_openai(config, messages)

    await send_channel_message(
        config, game_data.game_context.selected_game.channel_id, response_start
    )

    stories.append(
        STORY(response=response_start, story_type=StoryType.INIT, tale_id=tale.id)
    )
    await update_db_objs(config=config, objs=stories)


async def setup_game(interaction: Interaction, config: Configuration) -> None:
    """
    Function game status with a select menu to choose the game status. The game status can be
    switched based on the current status of the game.

    Args:
        config (Configuration): App configuration
        interaction (Interaction): Interaction object
    """
    try:
        process_data = ProcessInput()
        process_data.game_context.available_games = await get_games_w_status(
            config,
            [
                GameStatus.CREATED,
                GameStatus.RUNNING,
                GameStatus.PAUSED,
            ],
        )
        if not await process_data.game_context.input_valid_game():
            await interaction.response.send_message(
                "No game is available, please contact a Mod.",
                ephemeral=True,
            )
            return
        select_view = GameSelectView(config, process_data)
        await interaction.response.send_message(
            "Which game would you like to change the status of?",
            view=select_view,
            ephemeral=True,
        )
        await select_view.wait()
        process_data.game_context.selected_game = await get_object_by_id(
            config, GAME, process_data.game_context.selected_game_id
        )
        game_select_view = NewGameStatusSelectView(config, process_data)
        await interaction.followup.send(
            "Select now the new status for game with id: "
            + f"{process_data.game_context.selected_game_id}",
            view=game_select_view,
            ephemeral=True,
        )
        await game_select_view.wait()
        if await process_data.game_context.request_game_start():
            counted_participants = await count_regist_char_from_game(
                config, process_data.game_context.selected_game.id
            )
            if counted_participants == 0:
                await interaction.followup.send(
                    "You have selected that the game with the ID: "
                    + f"{process_data.game_context.selected_game_id}. "
                    + "However, no character has been registered for the game by a user yet.",
                    ephemeral=True,
                )
                return
            await interaction.followup.send(
                "You have selected that the game with the ID: "
                + f"{process_data.game_context.selected_game_id} "
                + "will be started.",
                ephemeral=True,
            )
            await start_game_schedule(interaction, config, process_data)
        process_data.game_context.selected_game.status = (
            process_data.game_context.new_game_status
        )
        await update_db_objs(config, [process_data.game_context.selected_game])
        await update_embed_message(config, process_data.game_context.selected_game)

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


async def reset_game(interaction: Interaction, config: Configuration) -> None:
    """
    _summary_

    Args:
        interaction (Interaction): _description_
        config (Configuration): _description_
    """
