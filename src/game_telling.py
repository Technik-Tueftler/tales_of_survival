"""
Module for handling the telling of story command.
"""

from discord import Interaction
from .discord_utils import send_channel_message
from .configuration import Configuration, ProcessInput, DelimitedTemplate
from .db import get_stories_messages_for_ai, update_db_objs
from .db_classes import STORY, StoryType, MESSAGE
from .llm_handler import request_openai
from .constants import (
    PROMPT_MAX_WORDS_EVENT,
    PROMPT_MAX_WORDS_FICTION,
    EVENT_REQUEST_PROMPT,
    FICTION_REQUEST_PROMPT,
)


async def telling_event(
    config: Configuration, process_data: ProcessInput, interaction: Interaction
):
    """
    This function handles the telling of story based on an event.

    Args:
        config (Configuration): App configuration
        process_data (ProcessInput): Process game data
    """
    config.logger.debug(
        "Generating event phase prompt for tale id: "
        + f"{process_data.story_context.tale.id}"
    )
    commit_stories = []
    messages = await get_stories_messages_for_ai(
        config, process_data.story_context.tale.id
    )
    event_requ_prompt = DelimitedTemplate(EVENT_REQUEST_PROMPT).substitute(
        EventText=process_data.story_context.event.text, MaxWords=PROMPT_MAX_WORDS_EVENT
    )
    config.logger.trace(f"Event request prompt: {event_requ_prompt}")
    messages.append({"role": "user", "content": event_requ_prompt})
    commit_stories.append(
        STORY(
            request=event_requ_prompt,
            story_type=StoryType.EVENT,
            tale_id=process_data.story_context.tale.id,
        )
    )
    response_event = await request_openai(config, messages)
    if not await response_event.error_free():
        await interaction.followup.send(
            f"The following error occurred during the AI request: {response_event.error}",
            ephemeral=True,
        )
        return False
    config.logger.trace(f"Event response: {response_event.response}")

    msg_ids_event = await send_channel_message(
        config,
        process_data.game_context.selected_game.channel_id,
        response_event.response,
    )

    event_message = (
        f"An event has been triggered:\nEvent: {process_data.story_context.event.text}"
    )
    await interaction.followup.send(event_message, ephemeral=True)

    commit_stories.append(
        STORY(
            response=response_event.response,
            story_type=StoryType.EVENT,
            tale_id=process_data.story_context.tale.id,
            messages=[MESSAGE(message_id=msg_id) for msg_id in msg_ids_event],
        )
    )
    await update_db_objs(config, commit_stories)


async def telling_fiction(
    config: Configuration, process_data: ProcessInput, interaction: Interaction
):
    """
    This function handles the telling of story based on an fiction input.

    Args:
        config (Configuration): App configuration
        process_data (ProcessInput): Process game data
    """
    config.logger.debug(
        "Generating fiction phase prompt for tale id: "
        + f"{process_data.story_context.tale.id}"
    )
    commit_stories = []
    messages = await get_stories_messages_for_ai(
        config, process_data.story_context.tale.id
    )
    fiction_prompt = await process_data.story_context.get_fiction_prompt()
    config.logger.trace(f"Fiction word: {fiction_prompt}")
    fiction_requ_prompt = DelimitedTemplate(FICTION_REQUEST_PROMPT).substitute(
        FictionText=fiction_prompt, MaxWords=PROMPT_MAX_WORDS_FICTION
    )
    config.logger.trace(f"Fiction request prompt: {fiction_requ_prompt}")
    messages.append({"role": "user", "content": fiction_requ_prompt})
    commit_stories.append(
        STORY(
            request=fiction_requ_prompt,
            story_type=StoryType.FICTION,
            tale_id=process_data.story_context.tale.id,
        )
    )
    response_fiction = await request_openai(config, messages)
    if not await response_fiction.error_free():
        await interaction.followup.send(
            f"The following error occurred during the AI request: {response_fiction.error}",
            ephemeral=True,
        )
        return False
    config.logger.trace(f"Fiction response: {response_fiction.response}")

    msg_ids_fiction = await send_channel_message(
        config,
        process_data.game_context.selected_game.channel_id,
        response_fiction.response,
    )

    commit_stories.append(
        STORY(
            response=response_fiction.response,
            story_type=StoryType.FICTION,
            tale_id=process_data.story_context.tale.id,
            messages=[MESSAGE(message_id=msg_id) for msg_id in msg_ids_fiction],
        )
    )
    await update_db_objs(config, commit_stories)
