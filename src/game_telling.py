"""
Module for handling the telling of story command.
"""

import traceback
from .discord_utils import send_channel_message
from .configuration import Configuration, ProcessInput
from .db import get_stories_messages_for_ai, update_db_objs
from .db_classes import STORY, StoryType
from .llm_handler import request_openai
from .constants import MAX_WORDS_EVENT_PROMPT, MAX_WORDS_FICTION_PROMPT


async def telling_event(config: Configuration, process_data: ProcessInput):
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
    event_requ_prompt = (
        "Erzähl mir einen neuen Teil der Geschichte basierend auf dem folgenden Ereignis: "
        + f"{process_data.story_context.event.text} mit maximal {MAX_WORDS_EVENT_PROMPT} Wörtern."
        + "Achte darauf, dass das Ereignis so angepasst wird, dass es für ein Spieler ist, "
        + "wenn nur ein Charakter in der Geschichte ist."
    )

    messages.append({"role": "user", "content": event_requ_prompt})
    commit_stories.append(
        STORY(
            request=event_requ_prompt,
            story_type=StoryType.EVENT,
            tale_id=process_data.story_context.tale.id,
        )
    )
    response_event = await request_openai(config, messages)

    await send_channel_message(
        config,
        process_data.game_context.selected_game.channel_id,
        response_event,
    )

    commit_stories.append(
        STORY(
            response=response_event,
            story_type=StoryType.EVENT,
            tale_id=process_data.story_context.tale.id,
        )
    )
    await update_db_objs(config, commit_stories)


async def telling_fiction(config: Configuration, process_data: ProcessInput):
    """
    This function handles the telling of story based on an fiction input.

    Args:
        config (Configuration): App configuration
        process_data (ProcessInput): Process game data
    """
    try:
        config.logger.debug(
            "Generating fiction phase prompt for tale id: "
            + f"{process_data.story_context.tale.id}"
        )
        commit_stories = []
        messages = await get_stories_messages_for_ai(
            config, process_data.story_context.tale.id
        )
        fiction_requ_prompt = (
            "Schreibe die Geschichte weiter basierend auf dem folgenden Input: "
            + f"{process_data.story_context.fiction_prompt} mit maximal "
            + f"{MAX_WORDS_FICTION_PROMPT} Wörtern."
        )

        messages.append({"role": "user", "content": fiction_requ_prompt})
        commit_stories.append(
            STORY(
                request=fiction_requ_prompt,
                story_type=StoryType.FICTION,
                tale_id=process_data.story_context.tale.id,
            )
        )
        response_fiction = await request_openai(config, messages)

        await send_channel_message(
            config,
            process_data.game_context.selected_game.channel_id,
            response_fiction,
        )

        commit_stories.append(
            STORY(
                response=response_fiction,
                story_type=StoryType.FICTION,
                tale_id=process_data.story_context.tale.id,
            )
        )
        await update_db_objs(config, commit_stories)
    except Exception as err:
        traceback.print_exception(err)
