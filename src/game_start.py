"""
Module for handling the game start process, including collecting
user input and generating initial prompts.
"""

from discord import Interaction
from .configuration import (
    Configuration,
    ProcessInput,
    StartCondition,
    DelimitedTemplate,
)
from .game_views import StartTaleButtonView
from .constants import (
    PROMPT_MAX_WORDS_DESCRIPTION,
    PROMPT_MAX_WORDS_START,
    NEW_TALE_FIRST_PHASE_PROMPT_PART_1,
    NEW_TALE_FIRST_PHASE_PROMPT_PART_2,
    NEW_TALE_FIRST_PHASE_PROMPT_PART_3,
    NEW_TALE_FIRST_PHASE_PROMPT_PART_4,
    NEW_TALE_SECOND_PHASE_PROMPT_MULTI_PART_1,
    NEW_TALE_SECOND_PHASE_PROMPT_MULTI_PART_2,
    NEW_TALE_SECOND_PHASE_PROMPT_SINGLE_PART_1,
    NEW_TALE_SECOND_PHASE_PROMPT_SINGLE_PART_2
)


async def collect_start_input(
    interaction: Interaction, config: Configuration, game_data: ProcessInput
):
    """
    This function is the entry point for the view to collect game start input

    Args:
        interaction (Interaction): Interaction object
        config (Configuration): App configuration
        game_data (ProcessInput): Game data object
    """
    telling_view = StartTaleButtonView(config, game_data)
    await interaction.followup.send(view=telling_view, ephemeral=True)
    await telling_view.wait()


async def get_first_phase_prompt(
    config: Configuration, game_data: ProcessInput
) -> list[dict]:
    """
    This function generates the prompt messages for the first phase
    of the game start process based on the selected start condition.

    Args:
        config (Configuration): App configuration
        game_data (ProcessInput): Game data object

    Returns:
        list[dict]: List of prompt messages
    """
    config.logger.debug(
        "Generating first phase prompt for game start for tale id: "
        + f"{game_data.story_context.tale.id}"
    )
    system_requ_prompt = DelimitedTemplate(
        NEW_TALE_FIRST_PHASE_PROMPT_PART_1
    ).substitute(
        GenreName=game_data.story_context.tale.genre.name,
        GenreLanguage=game_data.story_context.tale.genre.language,
    )

    system_requ_prompt += (
        DelimitedTemplate(NEW_TALE_FIRST_PHASE_PROMPT_PART_2).substitute(
            GenreStorytellingStyle=game_data.story_context.tale.genre.storytelling_style
        )
        if game_data.story_context.tale.genre.storytelling_style is not None
        else ""
    )

    system_requ_prompt += (
        DelimitedTemplate(NEW_TALE_FIRST_PHASE_PROMPT_PART_3).substitute(
            GenreAtmosphere=game_data.story_context.tale.genre.atmosphere
        )
        if game_data.story_context.tale.genre.atmosphere is not None
        else ""
    )
    config.logger.trace(f"System prompt part 1: {system_requ_prompt}")
    user_requ_prompt = DelimitedTemplate(NEW_TALE_FIRST_PHASE_PROMPT_PART_4).substitute(
        MaxWords=PROMPT_MAX_WORDS_DESCRIPTION
    )
    config.logger.trace(f"User prompt part 1: {user_requ_prompt}")
    messages = [
        {"role": "user", "content": system_requ_prompt},
        {"role": "user", "content": user_requ_prompt},
    ]
    return messages


async def get_second_phase_prompt(
    config: Configuration, game_data: ProcessInput
) -> list[dict]:
    """
    This function generates the prompt messages for the second phase
    of the game start process based on the selected start condition.

    Args:
        config (Configuration): App configuration
        game_data (ProcessInput): Game data object

    Returns:
        list[dict]: List of prompt messages
    """
    config.logger.debug(
        "Generating second phase prompt for game start for tale id: "
        + f"{game_data.story_context.tale.id}"
    )
    messages = []
    start_condition = game_data.story_context.start.condition
    if (
        start_condition is StartCondition.S_ZOMBIE
        and len(game_data.story_context.character) > 1
    ):
        config.logger.debug(
            "Generating S_ZOMBIE start condition prompt for multiple characters "
            + f"Count: {len(game_data.story_context.character)}"
        )
        char_requ_prompt = DelimitedTemplate(
            NEW_TALE_SECOND_PHASE_PROMPT_MULTI_PART_1
        ).substitute(NumberCharacters=len(game_data.story_context.character))
        config.logger.trace(f"Charakter prompt part 2: {char_requ_prompt}")

        messages.append({"role": "user", "content": char_requ_prompt})

        for character in game_data.story_context.character:
            config.logger.trace(f"Charakter-ID for part 2: {character.id}")
            messages.append({"role": "user", "content": character.summary})

        if game_data.story_context.start.prompt == "":
            start_requ_prompt = DelimitedTemplate(
                NEW_TALE_SECOND_PHASE_PROMPT_MULTI_PART_2
            ).substitute(
                MaxWords=PROMPT_MAX_WORDS_START, City=game_data.story_context.start.city
            )
        else:
            start_requ_prompt = game_data.story_context.start.prompt
        config.logger.trace(f"Start prompt part 2: {start_requ_prompt}")
        messages.append({"role": "user", "content": start_requ_prompt})

    elif (
        start_condition is StartCondition.S_ZOMBIE
        and len(game_data.story_context.character) == 1
    ):
        config.logger.debug(
            "Generating S_ZOMBIE start condition prompt for one characters "
            + f"Count: {len(game_data.story_context.character)}"
        )
        char_requ_prompt = DelimitedTemplate(
            NEW_TALE_SECOND_PHASE_PROMPT_SINGLE_PART_1
        ).substitute(CharacterSummary=game_data.story_context.character[0].summary)
        config.logger.trace(f"Charakter prompt part 2: {char_requ_prompt}")
        messages.append({"role": "user", "content": char_requ_prompt})

        if game_data.story_context.start.prompt == "":
            start_requ_prompt = DelimitedTemplate(
                NEW_TALE_SECOND_PHASE_PROMPT_SINGLE_PART_2
            ).substitute(MaxWords=PROMPT_MAX_WORDS_START, City=game_data.story_context.start.city)
        else:
            start_requ_prompt = game_data.story_context.start.prompt
        config.logger.trace(f"Start prompt part 2: {start_requ_prompt}")
        messages.append({"role": "user", "content": start_requ_prompt})

    elif start_condition is StartCondition.OWN:
        if len(game_data.story_context.character) > 1:
            char_requ_prompt = DelimitedTemplate(
                NEW_TALE_SECOND_PHASE_PROMPT_MULTI_PART_1
            ).substitute(NumberCharacters=len(game_data.story_context.character))
            config.logger.trace(f"Charakter prompt part 2: {char_requ_prompt}")
            messages.append({"role": "user", "content": char_requ_prompt})
            for character in game_data.story_context.character:
                config.logger.trace(f"Charakter-ID for part 2: {character.id}")
                messages.append({"role": "user", "content": character.summary})
        else:
            char_requ_prompt = DelimitedTemplate(
                NEW_TALE_SECOND_PHASE_PROMPT_SINGLE_PART_1
            ).substitute(CharacterSummary=game_data.story_context.character[0].summary)
            config.logger.trace(f"Charakter prompt part 2: {char_requ_prompt}")
            messages.append({"role": "user", "content": char_requ_prompt})

        start_requ_prompt = game_data.story_context.start.prompt
        config.logger.trace(f"Start prompt part 2: {start_requ_prompt}")
        messages.append({"role": "user", "content": start_requ_prompt})
    else:
        config.logger.critical(
            f"Start condition {game_data.story_context.start.condition} not defined."
        )
    return messages
