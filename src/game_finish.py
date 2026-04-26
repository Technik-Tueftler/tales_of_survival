"""
Module to handle game finish actions and commands, including processing
and generating the final story.
"""

from discord import Interaction
from .discord_utils import (
    interface_select_game,
    send_channel_message,
)
from .configuration import Configuration, ProcessInput, DelimitedTemplate, IdError
from .db_classes import GAME, GameStatus, STORY, StoryType, MESSAGE
from .db import (
    get_games_w_status,
    get_object_by_id,
    get_stories_messages_for_ai,
    update_db_objs,
    get_tale_from_game_id,
)
from .game_views import GameFinishView, StoryFinishView, FinalPromptView
from .llm_handler import request_openai, OpenAiContext
from .file_utils import create_story_pdf
from .constants import (
    FINAL_REQUEST_PROMPT,
    FINAL_REQUEST_PROMPT_USER,
    PROMPT_MAX_WORDS_END,
    CHAPTER_SECTION_PROMPT,
)


async def telling_story_end(
    config: Configuration, process_data: ProcessInput, interaction: Interaction
):
    """
    This function handles the end of the story with the final prompt and
    generates the final story output.

    Args:
        config (Configuration): App configuration
        process_data (ProcessInput): Process game data
        interaction (Interaction): Discord interaction object
    """
    try:
        config.logger.debug(
            "Generating final story part for tale id: "
            + f"{process_data.story_context.tale.id}"
        )
        commit_stories = []
        messages = await get_stories_messages_for_ai(
            config, process_data.story_context.tale.id
        )
        if process_data.game_context.finish.ai_prompt_requested:
            final_story_prompt = DelimitedTemplate(FINAL_REQUEST_PROMPT).substitute(
                MaxWords=PROMPT_MAX_WORDS_END
            )
        else:
            final_story_prompt = DelimitedTemplate(
                FINAL_REQUEST_PROMPT_USER
            ).substitute(
                FinalText=process_data.game_context.finish.finish_prompt,
                MaxWords=PROMPT_MAX_WORDS_END,
            )

        messages.append({"role": "user", "content": final_story_prompt})
        commit_stories.append(
            STORY(
                request=final_story_prompt,
                story_type=StoryType.FINAL,
                tale_id=process_data.story_context.tale.id,
            )
        )
        config.logger.trace(
            f"Final story request send response for tale id: {process_data.story_context.tale.id}"
        )
        response_final_story = await request_openai(config, messages)
        if not await response_final_story.error_free():
            await interaction.followup.send(
                f"The following error occurred during the AI request: {response_final_story.error}",
                ephemeral=True,
            )
            return
        config.logger.trace(f"Final response: {response_final_story.response}")

        msg_ids_fiction = await send_channel_message(
            config,
            process_data.game_context.selected_game.channel_id,
            response_final_story.response,
        )
        if not msg_ids_fiction:
            raise IdError(
                f"The id {process_data.game_context.selected_game.channel_id} "
                + "is not available on the DC server. No stories are being created."
            )

        commit_stories.append(
            STORY(
                response=response_final_story.response,
                story_type=StoryType.FINAL,
                tale_id=process_data.story_context.tale.id,
                messages=[MESSAGE(message_id=msg_id) for msg_id in msg_ids_fiction],
            )
        )
        await update_db_objs(config, commit_stories)
    except IdError as err:
        config.logger.error(f"ID-Error: {err}")


async def chapter_creation(
    interaction: Interaction, config: Configuration, final_story: str
) -> OpenAiContext:
    """
    This funktion creates chapter for the story if the user requested it in the story finish view.

    Args:
        interaction (Interaction): Discord interaction object
        config (Configuration): App configuration
        story (str): The story text for which to create chapters
    """
    messages = [
        {"role": "user", "content": CHAPTER_SECTION_PROMPT},
        {"role": "user", "content": final_story},
    ]
    print(final_story)
    final_story_with_capter: OpenAiContext = await request_openai(config, messages)
    if not await final_story_with_capter.error_free():
        await interaction.followup.send(
            f"The following error occurred during the AI request: {final_story_with_capter.error}",
            ephemeral=True,
        )
        return final_story_with_capter
    config.logger.trace("Final story with chapter are generated.")
    return final_story_with_capter


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

    if not process_data.game_context.finish.finish_confirmed:
        return
    story_output_view = StoryFinishView(config, process_data)
    await interaction.followup.send(
        (
            "Select the parameters for the last part of the "
            "story and the formatting of the output file."
        ),
        view=story_output_view,
        ephemeral=True,
    )
    await story_output_view.wait()
    if not process_data.game_context.finish.ai_prompt_requested:
        final_prompt_view = FinalPromptView(config, process_data)
        await interaction.followup.send(
            content=(
                "Writing Guidelines:\n"
                "1. Choose an open ending or wrap up the story.\n"
                "2. Think about all the characters.\n"
                "3. Describe the circumstances in which the story ends.\n"
                "4. Should it have a happy or sad ending?\n"
            ),
            view=final_prompt_view,
            ephemeral=True,
        )
        await final_prompt_view.wait()
    process_data.game_context.selected_game = await get_object_by_id(
        config, GAME, process_data.game_context.selected_game_id
    )
    process_data.story_context.tale = await get_tale_from_game_id(
        config, process_data.game_context.selected_game_id
    )
    # await telling_story_end(config, process_data, interaction) #TODO: einschalten
    story_messages = await get_stories_messages_for_ai(
        config, process_data.story_context.tale.id
    )
    filtered_story_messages = list(
        filter(lambda message: message["role"] == "assistant", story_messages)
    )
    config.logger.trace(
        f"List of messages filtered with role assistant: {len(filtered_story_messages)}"
    )
    final_story = "\n".join(
        message["content"] for message in filtered_story_messages
    )
    final_formated_story: OpenAiContext = (
        await chapter_creation(interaction, config, final_story)
        if process_data.game_context.finish.chapter_requested
        else None
    )
    if final_formated_story is not None and not await final_formated_story.error_free():
        return

    await create_story_pdf(
        config,
        interaction,
        process_data.game_context.selected_game.name,
        final_formated_story.response or final_story,
    )
    #TODO: PDF posten?
    #TODO: Game beenden und Status auf finish setzen.
