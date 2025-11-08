"""
Module for handling the game start process, including collecting
user input and generating initial prompts.
"""

from discord import Interaction
from .configuration import Configuration, ProcessInput, StartCondition
from .game_views import StartTaleButtonView
from .constants import PROMPT_MAX_WORDS_DESCRIPTION, PROMPT_MAX_WORDS_START


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
    system_requ_prompt = (
        f"Du bist ein Geschichtenerzähler für ein/e {game_data.story_context.tale.genre.name}. "
        + f"Die Antworten nur in {game_data.story_context.tale.genre.language}."
    )
    system_requ_prompt += (
        f" Der Erzählstil sollte: {game_data.story_context.tale.genre.storytelling_style} sein."
        if game_data.story_context.tale.genre.storytelling_style is not None
        else ""
    )
    system_requ_prompt += (
        f" Die Atmosphäre der Geschichte ist: {game_data.story_context.tale.genre.atmosphere}."
        if game_data.story_context.tale.genre.atmosphere is not None
        else ""
    )
    user_requ_prompt = (
        "Beschreibe mir die Welt in der die Menschen jetzt "
        + f"leben müssen mit (maximal {PROMPT_MAX_WORDS_DESCRIPTION} Wörter)"
    )
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

    match game_data.story_context.start.condition:
        case StartCondition.S_ZOMBIE_X:
            char_requ_prompt = (
                "Es sind die folgenden Charaktere (Anzahl: "
                + f"{len(game_data.story_context.character)}) in der Geschichte:"
            )
            messages.append({"role": "user", "content": char_requ_prompt})
            for character in game_data.story_context.character:
                messages.append({"role": "user", "content": character.summary})
            if game_data.story_context.start.prompt == "":
                start_requ_prompt = (
                    f"Erzähl mir den Start der Geschichte (maximal {PROMPT_MAX_WORDS_START} "
                    + "Wörter) bei der sich die Charaktere in einer Stadt namens "
                    + f"{game_data.story_context.start.city} treffen und beschließen eine "
                    + "Gemeinschaft zu bilden."
                )
            else:
                start_requ_prompt = game_data.story_context.start.prompt
            messages.append({"role": "user", "content": start_requ_prompt})

        case StartCondition.S_ZOMBIE_1:
            char_requ_prompt = "Um den folgende Charaktere geht es in der Geschichte:"
            messages.append({"role": "user", "content": char_requ_prompt})
            messages.append(
                {
                    "role": "user",
                    "content": game_data.story_context.character[0].summary,
                }
            )
            if game_data.story_context.start.prompt == "":
                start_requ_prompt = (
                    f"Erzähl mir den Start der Geschichte (maximal {PROMPT_MAX_WORDS_START} "
                    + "Wörter) bei der sich der Charakter in einer Stadt namens "
                    + f"{game_data.story_context.start.city} aufhält und dort versucht "
                    + "zu überleben."
                )
            else:
                start_requ_prompt = game_data.story_context.start.prompt
            messages.append({"role": "user", "content": start_requ_prompt})

        case StartCondition.OWN_X:
            char_requ_prompt = (
                "Es sind die folgenden Charaktere (Anzahl: "
                + f"{len(game_data.story_context.character)}) in der Geschichte:"
            )
            messages.append({"role": "user", "content": char_requ_prompt})
            for character in game_data.story_context.character:
                messages.append({"role": "user", "content": character.summary})
            start_requ_prompt = game_data.story_context.start.prompt
            messages.append({"role": "user", "content": start_requ_prompt})

        case StartCondition.OWN_1:
            char_requ_prompt = "Um den folgende Charaktere geht es in der Geschichte:"
            messages.append({"role": "user", "content": char_requ_prompt})
            messages.append(
                {
                    "role": "user",
                    "content": game_data.story_context.character[0].summary,
                }
            )
            start_requ_prompt = game_data.story_context.start.prompt
            messages.append({"role": "user", "content": start_requ_prompt})

        case _:
            config.logger.error(
                f"Start condition {game_data.story_context.start.condition} not defined."
            )
    return messages
