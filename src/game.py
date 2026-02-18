"""
Module to handle game creation and management
"""

import sys
from datetime import datetime, timezone
import asyncio
import discord
from discord import Interaction
from .discord_utils import (
    send_channel_message,
    update_embed_message,
    interface_select_game,
    delete_channel_messages,
    update_embed_message_color,
    send_game_embed,
    create_dc_message_link,
    send_game_info_embed,
)
from .discord_permissions import check_permissions_storyteller
from .configuration import Configuration, ProcessInput, IdError
from .llm_handler import request_openai, OpenAiContext
from .db_classes import StoryType, GameStatus
from .db_classes import (
    GAME,
    TALE,
    UserGameCharacterAssociation,
    STORY,
    MESSAGE,
)
from .db import (
    process_player,
    update_db_objs,
    get_all_running_games,
    get_all_running_user_games,
    get_tale_from_game_id,
    get_games_w_status,
    count_regist_char_from_game,
    get_character_from_game_id,
    get_stories_messages_for_ai,
    channel_id_exist,
    check_only_init_stories,
    delete_init_stories,
)
from .db_genre import get_genre_double_cond, get_all_active_genre
from .db_game import GameInfo, get_all_game_related_infos
from .game_views import (
    GenreSelectView,
    UserSelectView,
    KeepTellingButtonView,
    NewGameStatusSelectView,
    GameFinishView,
)
from .game_start import (
    collect_start_input,
    get_first_phase_prompt,
    get_second_phase_prompt,
)
from .game_telling import telling_event, telling_fiction


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
        message = await send_game_embed(
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
        process_data.user_context.user_dc_id = str(interaction.user.id)
        if await check_permissions_storyteller(config, interaction):
            await get_all_running_games(config, process_data)
        else:
            await get_all_running_user_games(config, process_data)
        select_success = await interface_select_game(interaction, config, process_data)
        if not select_success:
            return
        process_data.story_context.tale = await get_tale_from_game_id(
            config, process_data.game_context.selected_game_id
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
            await telling_fiction(config, process_data, interaction)
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


async def start_game_schedule(
    interaction: Interaction, config: Configuration, game_data: ProcessInput
) -> bool:
    """
    This function the schedule to start a new game. It collects all necessary
    inputs from the user, gets the tale and character data from the database,
    creates the prompts for the LLM model, sends the requests and stores
    the responses in the database.

    Args:
        interaction (Interaction): Interaction object
        config (Configuration): App configuration
        game_data (ProcessInput): Game data object

    Returns:
        bool: Success status of the game start process
    """
    try:
        await collect_start_input(interaction, config, game_data)

        tale = await get_tale_from_game_id(
            config, game_data.game_context.selected_game.id
        )
        game_character = await get_character_from_game_id(
            config, game_data.game_context.selected_game.id
        )
        game_data.story_context.tale = tale
        game_data.story_context.character = game_character

        messages = await get_first_phase_prompt(config, game_data)

        response_world: OpenAiContext = await request_openai(config, messages)
        if not await response_world.error_free():
            await interaction.followup.send(
                f"The following error occurred during the AI request: {response_world.error}",
                ephemeral=True,
            )
            return False
        msg_ids_world = await send_channel_message(
            config,
            game_data.game_context.selected_game.channel_id,
            response_world.response,
        )

        if not msg_ids_world:
            raise IdError(
                f"The id {game_data.game_context.selected_game.channel_id} "
                + "is not available on the DC server. No stories are being created."
            )

        stories = [
            STORY(request=story["content"], story_type=StoryType.INIT, tale_id=tale.id)
            for story in messages
        ]
        stories.append(
            STORY(
                response=response_world.response,
                story_type=StoryType.INIT,
                tale_id=tale.id,
                messages=[MESSAGE(message_id=msg_id) for msg_id in msg_ids_world],
            )
        )
        await update_db_objs(config=config, objs=stories)

        messages = await get_stories_messages_for_ai(config, tale.id)
        stories = []

        messages_second_phase = await get_second_phase_prompt(config, game_data)

        for msg in messages_second_phase:
            stories.append(
                STORY(
                    request=msg["content"], story_type=StoryType.INIT, tale_id=tale.id
                )
            )

        messages.extend(messages_second_phase)
        response_start = await request_openai(config, messages)
        if not await response_start.error_free():
            await interaction.followup.send(
                f"The following error occurred during the AI request: {response_start.error}",
                ephemeral=True,
            )
            return False
        msg_ids_start = await send_channel_message(
            config,
            game_data.game_context.selected_game.channel_id,
            response_start.response,
        )
        if not msg_ids_start:
            raise IdError(
                f"The id {game_data.game_context.selected_game.channel_id} "
                + "is not available on the DC server. No stories are being created."
            )

        stories.append(
            STORY(
                response=response_start.response,
                story_type=StoryType.INIT,
                tale_id=tale.id,
                messages=[MESSAGE(message_id=msg_id) for msg_id in msg_ids_start],
            )
        )
        await update_db_objs(config=config, objs=stories)
        return True
    except IdError as err:
        config.logger.error(f"ID-Error: {err}")
        return False


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
        select_success = await interface_select_game(interaction, config, process_data)
        if not select_success:
            return
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
            status = await start_game_schedule(interaction, config, process_data)
            if not status:
                return
            await update_embed_message(config, process_data.game_context.selected_game)
        process_data.game_context.selected_game.status = (
            process_data.game_context.new_game_status
        )
        await update_db_objs(config, [process_data.game_context.selected_game])

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
    This function resets a game and generates a new start story.
    Only possible if stories in the game with the status INIT.

    Args:
        interaction (Interaction): Discrod interaction
        config (Configuration): App configuration
    """
    process_data = ProcessInput()
    process_data.game_context.available_games = await get_games_w_status(
        config, [GameStatus.PAUSED, GameStatus.RUNNING]
    )
    select_success = await interface_select_game(interaction, config, process_data)
    if not select_success:
        return
    process_data.story_context.tale = await get_tale_from_game_id(
        config, process_data.game_context.selected_game.id
    )
    if not await check_only_init_stories(config, process_data.story_context.tale.id):
        await interaction.followup.send(
            "The story has already been passed on and cannot be reset.",
            ephemeral=True,
        )
        return
    dc_message_ids = await delete_init_stories(
        config,
        process_data.story_context.tale.id,
        process_data.game_context.selected_game.id,
    )
    await delete_channel_messages(
        config, process_data.game_context.selected_game, dc_message_ids
    )
    await update_embed_message_color(
        config, process_data.game_context.selected_game, discord.Color.yellow()
    )


async def finish_game(interaction: Interaction, config: Configuration) -> None:
    """
    This function finishes a game and generates a PDF with the story so far.
    The game status will be set to finished. It is not possible to keep
    telling a story after finishing the game.
    Args:
        interaction (Interaction): Discord interaction object
        config (Configuration): App configuration
    """
    process_data = ProcessInput()
    process_data.game_context.available_games = await get_games_w_status(
        config,
        [
            GameStatus.STOPPED,
        ],
    )
    select_success = await interface_select_game(interaction, config, process_data)
    if not select_success:
        return
    game_finish_view = GameFinishView(config, process_data)
    await interaction.followup.send(
        "Are you sure you want to finish the game with ID: "
        + f"{process_data.game_context.selected_game_id}? "
        + "It will not be possible to restart it!",
        view=game_finish_view,
        ephemeral=True,
    )
    await game_finish_view.wait()


async def info_game(interaction: Interaction, config: Configuration) -> None:
    """
    This function prints information about a game like state, players, etc.

    Args:
        interaction (Interaction): Discrod interaction
        config (Configuration): App configuration
    """
    process_data = ProcessInput()
    process_data.game_context.available_games = await get_games_w_status(
        config,
        [
            GameStatus.CREATED,
            GameStatus.PAUSED,
            GameStatus.RUNNING,
            GameStatus.STOPPED,
            GameStatus.FINISHED,
            GameStatus.FAILURE,
        ],
    )
    select_success = await interface_select_game(interaction, config, process_data)
    if not select_success:
        return
    game_info = GameInfo()
    game_info.game = process_data.game_context.selected_game
    await get_all_game_related_infos(config, game_info)
    await send_game_info_embed(interaction, config, game_info)
